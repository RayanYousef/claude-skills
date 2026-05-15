# claude-skills

Personal Claude Code agents and skills.

## Install

```bash
# From your project root — clones the repo and installs into ./.claude/
git clone https://github.com/RayanYousef/claude-skills /tmp/claude-skills
bash /tmp/claude-skills/install.sh

# Or install globally into ~/.claude/ (works across all projects)
bash /tmp/claude-skills/install.sh --global
```

After installing, restart Claude Code to pick up new agents.

## Structure

```
agents/          ← subagent .md files  →  .claude/agents/<name>.md
skills/          ← slash commands      →  .claude/skills/<name>/SKILL.md
  <skill-name>/
    SKILL.md
hooks/           ← hook scripts        →  .claude/hooks/<name>.py
```

## Agents

| Name | Description |
|------|-------------|
| review-pr-asset-analyzer | Analyzes asset changes in Unity PRs |
| review-pr-commit-analyzer | Analyzes commit quality and hygiene in PRs |
| review-pr-prefab-impact | Analyzes prefab impact in Unity PRs |
| review-pr-script-analyzer | Analyzes C# script changes in Unity PRs |

## Skills

| Command | Description |
|---------|-------------|
| `/agent-creator` | Create Claude Code subagent .md files with tools, models, and prompts |
| `/grill-me` | Knowledge testing / interview prep |
| `/sync-claude` | Sync agents and skills across all ~/.claude* profile directories |
| `/update-claude-skills` | Add a new skill or agent to this repo |
| `/review-pr` | Review pull requests |
| `/docx` | Work with Word documents |
| `/pdf` | Work with PDF files |
| `/pdf-ocr-to-docx` | Convert scanned PDFs to Word via OCR |
| `/pptx` | Work with PowerPoint files |
| `/sprint-planning` | Sprint planning assistant |
| `/task-creator` | Create and structure tasks |
| `/xlsx` | Work with Excel files |

## Hooks

Hook scripts are copied to `~/.claude/hooks/` but **not auto-wired** — add the entries below to your `settings.json` to activate them.

| File | Purpose |
|------|---------|
| `context-monitor-hook.py` | UserPromptSubmit hook — warns when context usage gets high |
| `context-monitor-lib.py` | Shared library for the context-monitor hook + statusline |
| `context-statusline.py` | Status line renderer showing context usage |
| `sync-profiles.py` | SessionStart hook — syncs agents/skills/projects/MCP across `~/.claude*` profiles |
| `test_context_monitor.py` | Tests for the context monitor |

Required `settings.json` entries (paths assume global install):

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [{ "type": "command",
                    "command": "python \"~/.claude/hooks/sync-profiles.py\"",
                    "shell": "bash",
                    "statusMessage": "Syncing Claude profiles...",
                    "async": true }] }
    ],
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command",
                    "command": "python \"~/.claude/hooks/context-monitor-hook.py\"" }] }
    ]
  },
  "statusLine": {
    "type": "command",
    "command": "python \"~/.claude/hooks/context-statusline.py\""
  }
}
```

On Windows, replace `~/.claude/...` with the absolute path (e.g. `C:/Users/<you>/.claude/hooks/...`).
