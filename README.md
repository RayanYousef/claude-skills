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
| `/grill-me` | Knowledge testing / interview prep |
| `/sync-claude` | Sync missing agents and skills between ~/.claude/ and ./.claude/ |
| `/update-claude-skills` | Add a new skill or agent to this repo |
| `/review-pr` | Review pull requests |
| `/docx` | Work with Word documents |
| `/pdf` | Work with PDF files |
| `/pdf-ocr-to-docx` | Convert scanned PDFs to Word via OCR |
| `/pptx` | Work with PowerPoint files |
| `/sprint-planning` | Sprint planning assistant |
| `/task-creator` | Create and structure tasks |
| `/xlsx` | Work with Excel files |
