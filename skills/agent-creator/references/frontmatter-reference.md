# Agent Frontmatter Reference

Complete reference for all YAML frontmatter fields in agent `.md` definition files.

## Table of Contents

1. [Required Fields](#required-fields)
2. [Tool Access](#tool-access)
3. [Model & Performance](#model--performance)
4. [Permissions](#permissions)
5. [Memory](#memory)
6. [Skills & MCP](#skills--mcp)
7. [Display & UX](#display--ux)
8. [Execution](#execution)

---

## Required Fields

### `name`
- **Type**: string (lowercase, hyphens only)
- **Required**: Yes
- **Example**: `name: security-reviewer`
- **Notes**: This is how the agent is referenced in @-mentions (`@agent-security-reviewer`) and in the Agent tool. Keep it short and descriptive.

### `description`
- **Type**: string
- **Required**: Yes
- **Example**: `description: Security specialist reviewing code for vulnerabilities. Use proactively when reviewing authentication, authorization, or input handling logic.`
- **Notes**: This is the primary triggering mechanism. Claude reads this to decide whether to delegate to the agent. Make it specific and include phrases like "use proactively when..." to encourage delegation. Be generous with trigger conditions — undertriggering is more common than overtriggering.

---

## Tool Access

### `tools`
- **Type**: comma-separated string
- **Required**: No (omit to inherit all parent tools)
- **Example**: `tools: Read, Grep, Glob, Bash`
- **Available tools**: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, Agent, TodoWrite, AskUserQuestion, NotebookEdit
- **Notes**: This is an allowlist — the agent can ONLY use these tools. Start restrictive and expand. Read-only agents should use `Read, Grep, Glob`. If the agent needs to modify files, add `Edit` (for existing files) or `Write` (for new files). Note: subagents cannot spawn other subagents, so `Agent` is only useful for the main session or team leads.

### `disallowedTools`
- **Type**: comma-separated string
- **Required**: No
- **Example**: `disallowedTools: Write, Edit, Bash`
- **Notes**: Denylist — these tools are removed from whatever the agent would otherwise have. Applied before `tools`. Use this when you want "everything except X" rather than listing every allowed tool.

---

## Model & Performance

### `model`
- **Type**: string enum
- **Required**: No (inherits parent model if omitted)
- **Options**:
  - `haiku` — Fast, cheap. Good for: scanning, simple checks, test running, repetitive tasks
  - `sonnet` — Balanced. Good for: most tasks including code review, implementation, research
  - `opus` — Most capable. Good for: complex architecture, nuanced judgment, creative work, hard debugging
  - Omit to inherit the parent session's model
- **Example**: `model: sonnet`
- **Notes**: Model choice dramatically affects both quality and cost. Use haiku for volume work, opus for tasks where getting it wrong is expensive. Sonnet is the safe default.

### `effort`
- **Type**: string enum
- **Required**: No
- **Options**: `low`, `medium`, `high`, `max`
- **Example**: `effort: high`
- **Notes**: Controls reasoning depth. Higher effort = more thinking tokens = better results on complex tasks but slower and more expensive. Default varies by model. Use `low` for simple scanning tasks, `high` or `max` for architecture decisions or complex debugging.

### `maxTurns`
- **Type**: integer
- **Required**: No
- **Example**: `maxTurns: 15`
- **Notes**: Safety limit — stops the agent after N tool-use rounds. Prevents runaway sessions. Set based on expected task complexity: 5–10 for simple tasks, 15–25 for moderate, 30+ for complex multi-step work.

---

## Permissions

### `permissionMode`
- **Type**: string enum
- **Required**: No (defaults to `default`)
- **Options**:
  - `default` — No auto-approvals; unmatched tools trigger permission prompt
  - `acceptEdits` — Auto-approve file operations (Read, Write, Edit, Glob, Grep)
  - `plan` — Read-only mode; modification tools are blocked while the agent plans
  - `dontAsk` — Anything not pre-approved via `tools` is silently denied
  - `bypassPermissions` — All tools auto-approved (use only in sandboxed environments!)
  - `auto` — An AI classifier decides per-tool whether to approve
- **Example**: `permissionMode: auto`
- **Notes**: For read-only agents (reviewers, analyzers), `plan` or `dontAsk` with read-only tools is safest. For agents that need to modify code, `acceptEdits` or `auto` reduces friction. `bypassPermissions` should only be used in isolated/sandboxed environments.

---

## Memory

### `memory`
- **Type**: string enum
- **Required**: No (no persistent memory if omitted)
- **Options**:
  - `user` — `~/.claude/agent-memory/<agent-name>/` — personal, all projects
  - `project` — `.claude/agent-memory/<agent-name>/` — project-specific, shared with team
  - `local` — `.claude/agent-memory-local/<agent-name>/` — project-specific, not shared (gitignored)
- **Example**: `memory: project`
- **Notes**: When enabled, the agent maintains a MEMORY.md file in the memory directory. Tell the agent in its system prompt what to remember — patterns discovered, conventions learned, mistakes to avoid. The agent reads MEMORY.md at session start and updates it as it learns. `project` memory is great for shared codebases; `user` memory for personal agents that learn your preferences across projects.

---

## Skills & MCP

### `skills`
- **Type**: list of strings
- **Required**: No
- **Example**:
  ```yaml
  skills:
    - api-conventions
    - error-handling-patterns
  ```
- **Notes**: Skills listed here have their full content injected into the agent's context at startup. The agent doesn't "invoke" the skill — it already has the knowledge. Use this when the agent should always follow certain conventions or patterns. Keep the list short — each skill adds to context size.

### `mcpServers`
- **Type**: list of server references or inline definitions
- **Required**: No
- **Example**:
  ```yaml
  mcpServers:
    - github
    - playwright:
        type: stdio
        command: npx
        args: ["-y", "@playwright/mcp@latest"]
  ```
- **Notes**: Reference existing MCP servers by name (must be configured in the project's `.mcp.json`) or define inline. The agent gets access to all tools from these servers. Tool naming follows: `mcp__<server>__<tool>`.

---

## Display & UX

### `color`
- **Type**: string enum
- **Required**: No
- **Options**: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`
- **Example**: `color: red`
- **Notes**: Display color in the terminal when the agent is running. Helps visually distinguish agents. Convention: red for security, blue for architecture, green for testing, yellow for debugging, purple for research.

---

## Execution

### `isolation`
- **Type**: string enum
- **Required**: No
- **Options**: `worktree`
- **Example**: `isolation: worktree`
- **Notes**: When set to `worktree`, the agent runs in a temporary git worktree — an isolated copy of the repository. If the agent makes changes, the worktree and branch are preserved. If no changes, it's cleaned up automatically. Use this for experimental or risky changes where you don't want to touch the main working tree.

### `background`
- **Type**: boolean
- **Required**: No (defaults to false)
- **Example**: `background: true`
- **Notes**: When true, the agent always runs as a background task, equivalent to pressing Ctrl+B. All permissions must be pre-approved since the user can't interact. Useful for long-running tasks like test suites or monitoring. The main session continues working while the background agent runs.

---

## Complete Example

```yaml
---
name: security-reviewer
description: >
  Security specialist auditing code for vulnerabilities.
  Use proactively when reviewing authentication, authorization,
  or input handling logic. Also invoke for dependency audits
  or security-focused PR reviews.
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: plan
memory: project
color: red
maxTurns: 20
effort: high
---
```

## Scope Priority

When multiple agents share the same name, this priority applies (highest first):
1. Managed settings (org-wide, set by admins)
2. CLI `--agents` flag (session-only)
3. `.claude/agents/` (project-level)
4. `~/.claude/agents/` (user/global level)
5. Plugin agents (lowest priority)
