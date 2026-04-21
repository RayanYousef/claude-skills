---
name: sync-claude
description: Sync Claude config between ~/.claude/ (global) and ./.claude/ (project). Finds missing agents, skills, and settings in either direction and lets you choose what to sync. TRIGGER when the user asks to sync Claude config, sync skills/agents, or check what's missing between global and project Claude settings.
argument-hint: "[--to-project | --to-global | --both (default: --both)]"
---

Compare `~/.claude/` (global) with `./.claude/` (current project) and sync missing items between them.

## Steps

### 1. Discover what exists

Use Bash to list both sides:

```bash
echo "=== Global agents ===" && ls ~/.claude/agents/ 2>/dev/null || echo "(none)"
echo "=== Project agents ===" && ls .claude/agents/ 2>/dev/null || echo "(none)"
echo "=== Global skills ===" && ls ~/.claude/skills/ 2>/dev/null || echo "(none)"
echo "=== Project skills ===" && ls .claude/skills/ 2>/dev/null || echo "(none)"
```

### 2. Diff and report

Compare the two sides and present a clear summary to the user:

```
Missing from project (.claude/):     Missing from global (~/.claude/):
  agents:                              agents:
    - review-pr-asset-analyzer           - (none)
  skills:                              skills:
    - grill-me                           - sprint-planning
    - sync-claude
```

### 3. Ask the user what to sync

Unless `$ARGUMENTS` specifies a direction, ask:
> "What would you like to sync?"
> 1. Copy missing items → project `.claude/`
> 2. Copy missing items → global `~/.claude/`
> 3. Both directions
> 4. Pick specific items

### 4. Perform the sync

Copy only the missing items (never overwrite existing ones):

```bash
# Agent (missing from project):
cp ~/.claude/agents/<name>.md .claude/agents/

# Agent (missing from global):
cp .claude/agents/<name>.md ~/.claude/agents/

# Skill (missing from project):
cp -r ~/.claude/skills/<name> .claude/skills/

# Skill (missing from global):
cp -r .claude/skills/<name> ~/.claude/skills/
```

### 5. Confirm

List what was copied and remind the user to restart Claude Code to pick up new agents.

## Notes
- Never overwrite files that already exist on the destination side — only fill gaps
- If both sides have a file with the same name but different content, flag it and ask the user which version to keep
- Scope is limited to `agents/` and `skills/` — do not touch `settings.json`, `memory/`, or other config files unless the user explicitly asks
