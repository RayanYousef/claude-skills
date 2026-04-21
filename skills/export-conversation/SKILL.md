---
name: export-conversation
description: Export the current conversation to a markdown file. TRIGGER when the user asks to export, save, or download the conversation, chat, or session.
argument-hint: "[output path (optional)]"
---

Export the entire current conversation to a markdown file.

## Steps

1. **Determine output path**
   - If the user provided a path via `$ARGUMENTS`, use it
   - Otherwise default to `./conversation-export-<YYYY-MM-DD>.md` in the current working directory

2. **Write the file** using the Write tool. Structure it as:

```markdown
# Conversation Export
**Date:** <today's date>
**Project:** <current working directory>

---

**User:** <message content>

---

**Assistant:** <message content>

---
... (continue for every turn)
```

   - Preserve code blocks with their language tags
   - Preserve tool calls as collapsible summaries if relevant (e.g. `> Tool: Read — path/to/file.ts`)
   - Skip internal system messages

3. **Confirm** by telling the user the full path of the saved file.

## Notes
- Reconstruct the conversation from what is visible in your context window
- If the conversation is very long and was compacted, note that at the top: `> Note: Earlier messages were compacted and may not appear in full.`
- Do not truncate — export everything visible
