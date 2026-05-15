#!/usr/bin/env python3
"""
Full profile sync across ~/.claude*/ profile directories.

Syncs every top-level item in each profile root EXCEPT a denylist of things
that are per-session, transient, or sensitive (sessions, caches, logs, auth
state, lock files). Also merges user-scope MCP servers from .claude.json.

Behavior:
- Never overwrites. A profile that already has an item keeps its version.
- If the same item exists in multiple profiles with different content, logs a
  CONFLICT and skips it — manual resolution required.
- Creates .claude.json.bak-sync-<ts> before editing MCP config.
- Always exits 0 so a sync hiccup never blocks Claude Code session start.
"""
import json, shutil, datetime, os, glob, sys, filecmp

# Items that MUST NOT be synced. Reasons in comments so future-me remembers.
DENY = {
    # Per-conversation transcripts — merging corrupts session history.
    "sessions", "history.jsonl",
    # Per-profile runtime/cache/log state — bloat and irrelevance.
    "cache", "debug", "statsig", "telemetry",
    "shell-snapshots", "file-history", "paste-cache",
    "session-env", "todos", "tasks", "plans",
    "backups", "downloads", "ide",
    "image-cache", "stats-cache.json",
    ".last-cleanup", ".update.lock",
    # Per-profile auth/lock state — leaking these between profiles is bad.
    "mcp-needs-auth-cache.json",
    ".claude.json.lock",
    ".credentials.json",
    # Backups of the user's own config — keep local.
    ".claude.json.backup",
    # .claude.json is handled specially by sync_mcp_servers (merge, not copy).
    ".claude.json",
    # Local-only overrides should stay local by convention.
    "settings.local.json",
}

# Profile dirs that match the glob but aren't real profiles.
PROFILE_BLACKLIST = {".claude.json.lock"}

# Items where same-name divergence is legitimate and conflict-checking just
# produces noise. projects/ holds session transcripts under each project dir.
SKIP_CONFLICT_CHECK = {"projects"}


def log(msg):
    print(f"[sync] {msg}", file=sys.stderr)


def discover_profiles():
    profiles = sorted(glob.glob(os.path.expanduser("~/.claude*/")))
    out = []
    for p in profiles:
        p = p.rstrip("/\\")
        if not os.path.isdir(p):
            continue
        if os.path.basename(p) in PROFILE_BLACKLIST:
            continue
        # Real profiles always have at least one of these.
        if not any(os.path.exists(os.path.join(p, m)) for m in
                   ("settings.json", "CLAUDE.md", "agents", "skills", "projects")):
            continue
        out.append(p)
    return out


def items_equal(a, b):
    if os.path.isfile(a) and os.path.isfile(b):
        return filecmp.cmp(a, b, shallow=False)
    if os.path.isdir(a) and os.path.isdir(b):
        cmp = filecmp.dircmp(a, b)
        if cmp.left_only or cmp.right_only or cmp.diff_files:
            return False
        # Recurse into common subdirs to catch deep diffs.
        for sub in cmp.common_dirs:
            if not items_equal(os.path.join(a, sub), os.path.join(b, sub)):
                return False
        return True
    return False  # type mismatch (file vs dir) = conflict


def sync_item(profiles, name):
    """Generic sync for a single top-level item across all profiles."""
    sources = []  # [(profile_root, full_path)]
    for p in profiles:
        full = os.path.join(p, name)
        if os.path.exists(full):
            sources.append((p, full))

    if not sources:
        return

    canonical = sources[0][1]
    check_conflicts = name not in SKIP_CONFLICT_CHECK

    if check_conflicts:
        for _, other in sources[1:]:
            if not items_equal(canonical, other):
                log(f"CONFLICT: {name} differs between profiles — skipping")
                return

    have = {p for p, _ in sources}
    for p in profiles:
        if p in have:
            continue
        target = os.path.join(p, name)
        try:
            if os.path.isfile(canonical):
                shutil.copy2(canonical, target)
            else:
                shutil.copytree(canonical, target)
            log(f"{os.path.basename(p)}: added {name}")
        except Exception as e:
            log(f"FAILED to copy {name} to {os.path.basename(p)}: {e}")


def discover_synced_items(profiles):
    """Union of every top-level entry across all profiles, minus DENY."""
    names = set()
    for p in profiles:
        try:
            for n in os.listdir(p):
                if n in DENY:
                    continue
                if n.startswith(".claude.json.bak"):
                    continue  # any .claude.json backup (sync's or user's)
                names.add(n)
        except OSError:
            continue
    return sorted(names)


def _account_email(raw_cfg):
    """Identify the Claude account a profile is logged into. None = unknown.

    MCP servers often carry implicit auth state (cookies, OAuth scopes, env
    vars) tied to the account that set them up. Propagating an MCP definition
    from account A into account B may not work and could surprise the user
    next time they log in. So we group profiles by account and only merge
    within a group.
    """
    oauth = raw_cfg.get("oauthAccount") if isinstance(raw_cfg, dict) else None
    if isinstance(oauth, dict):
        return oauth.get("emailAddress")
    return None


def _write_mcp_update(raw, profile_path, missing, source_defns, stamp):
    """Add the missing mcpServers entries to one profile. Account-safe by
    construction: we only mutate raw[profile_path]['mcpServers'][name] —
    oauthAccount, userID, and all other top-level keys are preserved."""
    target_mcp = raw[profile_path].setdefault("mcpServers", {})
    for n in missing:
        target_mcp[n] = source_defns[n]
    shutil.copy(os.path.join(profile_path, ".claude.json"),
                os.path.join(profile_path, f".claude.json.bak-sync-{stamp}"))
    with open(os.path.join(profile_path, ".claude.json"), "w", encoding="utf-8") as f:
        json.dump(raw[profile_path], f, indent=2)
    log(f"{os.path.basename(profile_path)}: added mcpServers {missing}")


def sync_mcp_servers(profiles):
    per_profile, raw, account = {}, {}, {}
    for p in profiles:
        cfg = os.path.join(p, ".claude.json")
        if not os.path.isfile(cfg):
            continue
        try:
            with open(cfg, "r", encoding="utf-8") as f:
                raw[p] = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            log(f"skip MCP for {os.path.basename(p)}: {e}")
            continue
        per_profile[p] = raw[p].get("mcpServers") or {}
        account[p] = _account_email(raw[p])

    # Group profiles by account email. None / missing accounts each form their
    # own singleton group — better to skip than to risk a wrong merge.
    groups = {}
    for p, email in account.items():
        if not email:
            log(f"skip MCP merge for {os.path.basename(p)}: no oauthAccount email — keeping isolated")
            continue
        groups.setdefault(email, []).append(p)

    def looks_secret(v):
        return isinstance(v, str) and len(v) > 20 and not (v.startswith("${") and v.endswith("}"))

    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

    for email, group in groups.items():
        if len(group) < 2:
            continue
        # Build canonical map within this account group only.
        canon = {}
        conflict = False
        for p in group:
            for name, defn in per_profile[p].items():
                key = json.dumps(defn, sort_keys=True)
                if name in canon and canon[name][0] != key:
                    log(f"CONFLICT: mcpServers/{name} differs within account {email} — skipping that server")
                    canon[name] = None  # mark conflicted
                else:
                    canon.setdefault(name, (key, p))
        canon = {n: v for n, v in canon.items() if v is not None}
        if not canon:
            continue

        # Refuse to propagate any server with hardcoded secrets in env.
        unsafe = False
        for name, (_, src) in canon.items():
            for k, v in (per_profile[src][name].get("env") or {}).items():
                if looks_secret(v):
                    log(f"WARN: mcpServers/{name}.env.{k} (from {os.path.basename(src)}) looks hardcoded — fix to ${{VAR}} before it propagates. Skipping all MCP merge for account {email}.")
                    unsafe = True
                    break
            if unsafe:
                break
        if unsafe:
            continue

        # Fill gaps within the group.
        for p in group:
            source_defns = {n: per_profile[canon[n][1]][n] for n in canon}
            missing = [n for n in canon if n not in (per_profile[p] or {})]
            if missing:
                _write_mcp_update(raw, p, missing, source_defns, stamp)


def main():
    try:
        profiles = discover_profiles()
        if len(profiles) < 2:
            return
        for name in discover_synced_items(profiles):
            sync_item(profiles, name)
        sync_mcp_servers(profiles)
    except Exception as e:
        log(f"sync failed: {e}")
    sys.exit(0)


if __name__ == "__main__":
    main()
