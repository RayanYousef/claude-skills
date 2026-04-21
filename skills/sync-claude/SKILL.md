---
name: sync-claude
description: Sync agents and skills across all ~/.claude* profile directories (~/.claude, ~/.claude-praxi, ~/.claude-dr, etc.). Finds what's missing in each profile and fills the gaps from the others. TRIGGER when the user asks to sync Claude profiles, sync skills or agents across profiles, or check what's missing between Claude configs.
---

Sync agents and skills across all `~/.claude*` profile directories by finding what each profile is missing and copying it from the others.

## Steps

### 1. Discover all Claude profile directories

```bash
ls -d ~/.claude*/ 2>/dev/null
```

This finds all directories matching `~/.claude*/` (e.g. `~/.claude/`, `~/.claude-praxi/`, `~/.claude-dr/`).

### 2. Build the union inventory

For each profile directory found, list its agents and skills:

```bash
for dir in ~/.claude*/; do
  echo "=== $dir ==="
  echo "-- agents --"
  ls "$dir/agents/" 2>/dev/null || echo "(none)"
  echo "-- skills --"
  ls "$dir/skills/" 2>/dev/null || echo "(none)"
done
```

### 3. Diff and report

Compute the full union of all agents and all skills across every profile. Then show a table of what each profile is missing:

```
                        ~/.claude   ~/.claude-praxi   ~/.claude-dr
agents:
  review-pr-analyzer       ✓              ✗               ✓
  grill-me                 ✓              ✓               ✗
skills:
  sync-claude              ✓              ✗               ✗
  sprint-planning          ✗              ✓               ✓
```

### 4. Sync missing items

For each missing item, copy it from any profile that has it:

```bash
# Agent missing from a profile:
cp <source-profile>/agents/<name>.md <target-profile>/agents/

# Skill missing from a profile:
cp -r <source-profile>/skills/<name> <target-profile>/skills/
```

Rules:
- **Never overwrite** — only copy to profiles where the item is absent
- If the same agent/skill name exists in multiple profiles but with **different content**, flag it to the user and ask which version should be the source of truth before syncing
- Process all profiles in one pass

### 5. Confirm

After syncing, re-run the inventory and show the updated state, confirming every profile now has the full set.

Remind the user: **restart any Claude Code sessions using the updated profiles** to pick up the new agents.

## Notes
- Profile directories are discovered dynamically — no hardcoded list needed
- Scope: `agents/` and `skills/` only. Do not touch `settings.json`, `memory/`, `CLAUDE.md`, or other config files
- This skill itself should be installed in all profiles so it's always available regardless of which profile is active
