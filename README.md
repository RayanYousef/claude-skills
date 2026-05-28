# claude-skills

Personal **Claude Code** and **Cursor** agents, skills, rules, and context-monitor hooks — reusable across projects.

Source: [github.com/RayanYousef/claude-skills](https://github.com/RayanYousef/claude-skills)

## Install

```bash
# From your project root — clones and installs into ./.claude/ and ./.cursor/
git clone https://github.com/RayanYousef/claude-skills /tmp/claude-skills
bash /tmp/claude-skills/install.sh

# Global (all projects on this machine)
bash /tmp/claude-skills/install.sh --global

# Only one stack
bash /tmp/claude-skills/install.sh --claude-only
bash /tmp/claude-skills/install.sh --cursor-only
```

After installing, restart Claude Code / Cursor and wire hooks (below).

## Structure

```
agents/                 → Claude Code subagents     →  .claude/agents/
skills/                 → Claude slash commands     →  .claude/skills/<name>/SKILL.md
hooks/                  → Claude context monitor    →  .claude/hooks/

cursor/agents/          → Cursor subagents          →  .cursor/agents/
cursor/rules/           → Cursor project rules      →  .cursor/rules/
cursor/hooks/           → Cursor context monitor    →  .cursor/hooks/
cursor/hooks.json.example
```

## Claude Code agents

| Name | Description |
|------|-------------|
| review-pr-asset-analyzer | Analyzes asset changes in Unity PRs |
| review-pr-commit-analyzer | Analyzes commit quality and hygiene in PRs |
| review-pr-prefab-impact | Analyzes prefab impact in Unity PRs |
| review-pr-script-analyzer | Analyzes C# script changes in Unity PRs |

## Cursor agents & rules

Orchestration stack (from llm-game-flow):

| Agent | Role |
|-------|------|
| orchestrator (rule) | Plans, grills, delegates — never writes product code |
| code-implementer | Implements one authorized task per slice |
| code-verify | Read-only reviewer; PASS / BLOCK verdict |
| code-advisor | Strategic advisor when implementer is stuck |
| web-research | Live-web facts; no guessing |

Rules in `cursor/rules/`: `orchestrator.mdc`, `vcontainer-di.mdc`, `event-system.mdc`, `command-dispatcher.mdc`, `project-folder-structure.mdc`.

## Skills (Claude Code)

| Command | Description |
|---------|-------------|
| `/agent-creator` | Create Claude Code subagent .md files |
| `/sync-claude` | Sync agents/skills across `~/.claude*` profiles |
| `/update-claude-skills` | Add a new skill or agent to this repo |
| `/review-pr` | Review pull requests |
| `/docx`, `/pdf`, `/pptx`, `/xlsx` | Office document workflows |
| `/pdf-ocr-to-docx` | Scanned PDF → Word via OCR |
| `/sprint-planning` | Sprint planning assistant |
| `/task-creator` | Create and structure tasks |

## Context monitor hooks

Shared idea: warn near **100k** tokens, block or strongly alert near **150k**, show usage on the status line. Override with env vars `CC_CONTEXT_WARN` / `CC_CONTEXT_BLOCK` (Claude) or `CURSOR_CONTEXT_WARN` / `CURSOR_CONTEXT_BLOCK` (Cursor).

### Claude Code (`hooks/`)

| File | Purpose |
|------|---------|
| `context-monitor-hook.py` | `UserPromptSubmit` — injects context notes / block message |
| `context-monitor-lib.py` | Shared token math from transcript JSONL |
| `context-statusline.py` | Status line: ctx count + model + cwd |

Wire in `~/.claude/settings.json` (use your absolute path on Windows):

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"C:/Users/<you>/.claude/hooks/context-monitor-hook.py\""
          }
        ]
      }
    ]
  },
  "statusLine": {
    "type": "command",
    "command": "python \"C:/Users/<you>/.claude/hooks/context-statusline.py\""
  }
}
```

### Cursor (`cursor/hooks/`)

| File | Purpose |
|------|---------|
| `context_monitor_lib.py` | Shared lib (IDE meter, transcript, CLI payload) |
| `context-session-start.py` | `sessionStart` — threshold reminder |
| `context-before-submit.py` | `beforeSubmitPrompt` — warn / block send |
| `context-post-tool.py` | `postToolUse` — agent nudge when elevated |
| `context-pre-compact.py` | `preCompact` — snapshot before `/summarize` |
| `context-statusline.py` | CLI status line (also used from `cli-config.json`) |
| `test_context_monitor.py` | Local test harness |

Copy `cursor/hooks.json.example` → `~/.cursor/hooks.json` and replace `{{CURSOR_HOOKS}}` with your hooks directory (e.g. `C:/Users/<you>/.cursor/hooks`).

CLI status line in `~/.cursor/cli-config.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python \"C:/Users/<you>/.cursor/hooks/context-statusline.py\"",
    "updateIntervalMs": 500
  }
}
```

Run tests (after install):

```bash
python ~/.cursor/hooks/test_context_monitor.py
```

## About

Claude Code agents, skills, and Cursor orchestration assets for reuse across Unity / game-dev projects.
