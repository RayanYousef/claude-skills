---
name: update-claude-skills
description: Add a new skill or agent to the claude-skills GitHub repo. TRIGGER when the user asks to add, publish, or sync a skill or agent to the claude-skills repo.
argument-hint: "[path to skill folder or agent .md file]"
---

Add a new skill or agent to the claude-skills repo at `H:/Users/Rayan/claude-skills/`.

## Steps

### 1. Identify what's being added
- If `$ARGUMENTS` is provided, use that path
- Otherwise ask the user: "What's the path to the skill folder or agent file you want to add?"

### 2. Determine type
- **Agent**: a single `.md` file — goes to `H:/Users/Rayan/claude-skills/agents/<filename>.md`
- **Skill**: a folder containing `SKILL.md` — goes to `H:/Users/Rayan/claude-skills/skills/<folder-name>/`

### 3. Copy the file(s)
Use Bash to copy:
```bash
# For an agent:
cp "<source>.md" "H:/Users/Rayan/claude-skills/agents/"

# For a skill:
cp -r "<source-folder>" "H:/Users/Rayan/claude-skills/skills/"
```

### 4. Update README.md
Open `H:/Users/Rayan/claude-skills/README.md` and add a row to the appropriate table:
- Agents table: `| name | one-line description |`
- Skills table: `| \`/name\` | one-line description |`

Get the description from the frontmatter of the agent or SKILL.md file.

### 5. Commit and push
```bash
cd "H:/Users/Rayan/claude-skills"
git add -A
git commit -m "Add <name> <agent|skill>"
git push
```

### 6. Confirm
Tell the user the item was added and link to: `https://github.com/RayanYousef/claude-skills`

## Notes
- Never add skills or agents that contain Praxilabs-specific logic (YouTrack references, internal experiment storyboard formats, internal system names)
- If unsure whether something is private, ask the user before adding
