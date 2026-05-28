---
name: update-agent-skills
description: Add a new skill, agent, rule, or hook to the agent-skills-and-rules GitHub repo. TRIGGER when the user asks to add, publish, or sync a skill, agent, rule, or hook to the agent-skills-and-rules repo.
argument-hint: "[path to skill folder, agent .md, rule .mdc, or hook .py]"
---

Add a new item to the **agent-skills-and-rules** repo (local clone, e.g. `C:/Users/Ray/claude-skills` or `~/agent-skills-and-rules`).

Repo: https://github.com/RayanYousef/agent-skills-and-rules

## Steps

### 1. Identify what's being added
- If `$ARGUMENTS` is provided, use that path
- Otherwise ask the user: "What's the path to the file or folder you want to add?"

### 2. Determine type and destination

| Type | Source | Destination |
|------|--------|-------------|
| Claude agent | single `.md` | `agents/<name>.md` |
| Claude skill | folder with `SKILL.md` | `skills/<folder-name>/` |
| Cursor agent | single `.md` | `cursor/agents/<name>.md` |
| Cursor rule | `.mdc` | `cursor/rules/<name>.mdc` |
| Claude hook | `.py` | `hooks/<name>.py` |
| Cursor hook | `.py` | `cursor/hooks/<name>.py` |

### 3. Copy the file(s)

Use Bash to copy into the repo clone.

### 4. Update README.md

Add a row to the appropriate table in the repo `README.md`. Use the frontmatter description from the source file.

### 5. Commit and push

```bash
cd "<repo-clone>"
git add -A
git commit -m "Add <name> <type>"
git push
```

### 6. Confirm

Tell the user the item was added and link to: `https://github.com/RayanYousef/agent-skills-and-rules`

## Notes

- Never add Praxilabs-specific logic (YouTrack, internal experiment formats, internal system names)
- If unsure whether something is private, ask the user before adding
