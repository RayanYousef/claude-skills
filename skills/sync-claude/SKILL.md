---
name: sync-claude
description: Sync agents, skills, and project history across all ~/.claude* profile directories (~/.claude, ~/.claude-praxi, ~/.claude-dr, etc.). Finds what's missing in each profile and fills the gaps from the others. TRIGGER when the user asks to sync Claude profiles, sync skills/agents/projects across profiles, or check what's missing between Claude configs.
---

Sync `agents/`, `skills/`, and `projects/` across all `~/.claude*` profile directories by finding what each profile is missing and copying it from the others.

## Steps

### 1. Discover all Claude profile directories

```bash
ls -d ~/.claude*/ 2>/dev/null
```

This finds all directories matching `~/.claude*/` (e.g. `~/.claude/`, `~/.claude-praxi/`, `~/.claude-dr/`).

### 2. Build the union inventory

For each profile, list agents, skills, and projects:

```bash
for dir in ~/.claude*/; do
  echo "=== $dir ==="
  echo "-- agents --"
  ls "$dir/agents/" 2>/dev/null || echo "(none)"
  echo "-- skills --"
  ls "$dir/skills/" 2>/dev/null || echo "(none)"
  echo "-- projects --"
  ls "$dir/projects/" 2>/dev/null || echo "(none)"
done
```

### 3. Diff and report

Compute the full union across every profile for each category. Show a table of what each profile is missing:

```
                           ~/.claude   ~/.claude-praxi   ~/.claude-dr
agents:
  review-pr-analyzer          ✓              ✗               ✓
  grill-me                    ✓              ✓               ✗
skills:
  sync-claude                 ✓              ✗               ✗
  sprint-planning             ✗              ✓               ✓
projects:
  H--Unity--Work-Praxilabs    ✓              ✗               ✓
  E---WorkDocuments-Planning  ✗              ✓               ✓
```

### 4. Sync missing items

Copy only what's absent — never overwrite existing items:

```bash
# Agent missing from a profile:
cp <source>/agents/<name>.md <target>/agents/

# Skill missing from a profile:
cp -r <source>/skills/<name> <target>/skills/

# Project missing from a profile:
cp -r <source>/projects/<slug> <target>/projects/
```

Rules:
- **Never overwrite** — only copy to profiles where the item is absent
- If the same name exists in multiple profiles but with **different content**, flag it and ask the user which version is the source of truth before syncing
- For `projects/`: directory names are path slugs (e.g. `H--Unity--Work-Praxilabs-experiment-engine`) so they are unique and safe to copy without collision risk
- Process all profiles in one pass

### 5. Confirm

After syncing, re-run the inventory and show the updated state confirming every profile now has the full set.

Remind the user: **restart any Claude Code sessions using the updated profiles** to pick up new agents.

## Notes
- Profile directories are discovered dynamically — no hardcoded list needed
- Scope: `agents/`, `skills/`, `projects/` only. Do not touch `settings.json`, `memory/`, `CLAUDE.md`, `sessions/`, or `history.jsonl` unless explicitly asked
- This skill itself should be installed in all profiles so it's always available regardless of which profile is active
