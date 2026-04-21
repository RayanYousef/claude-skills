# Agent Teams Reference

Agent teams let you orchestrate multiple Claude Code instances working together on a shared
project. Unlike subagents (which run inside a single session), each teammate is a fully
independent session with its own 1M-token context window.

## When to Use Teams vs. Subagents

| Situation | Use Subagents | Use Agent Teams |
|-----------|:------------:|:---------------:|
| Focused task delegation ("review this file") | ✓ | |
| Tasks that need direct peer communication | | ✓ |
| Budget-conscious work | ✓ | |
| Complex multi-role coordination | | ✓ |
| Tasks that might exceed context limits | | ✓ |
| Simple parallel execution | ✓ | |
| Teammates need to share findings directly | | ✓ |

**Rule of thumb**: If agents only need to report results back to you, use subagents.
If agents need to talk to *each other*, use teams.

## Prerequisites

Agent teams are experimental. Enable them via:

**Settings file** (`~/.claude/settings.json` or `.claude/settings.json`):
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**Or environment variable:**
```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

## Architecture

```
Team Lead (main session)
    ├── Teammate A (own session, own 1M context)
    ├── Teammate B (own session, own 1M context)
    └── Teammate C (own session, own 1M context)
    
Communication:
    Lead ↔ Teammate (direct messages)
    Teammate ↔ Teammate (direct messages via SendMessage)
    Lead → All (broadcast)
    Shared task list (all can see/claim tasks)
```

## Communication Methods

### Direct Messages (SendMessage)
Teammates message each other by name:
```
"Send a message to the architect: I found a circular dependency in the auth module"
```
- Synchronous — the sender waits for acknowledgment
- Use for coordination, sharing findings, asking questions

### Broadcast
Lead sends to all teammates at once:
```
"Broadcast to all: pause your current work, we're changing the API contract"
```
- Use sparingly — costs scale with team size
- Good for: priority changes, new information that affects everyone

### Shared Task List
- All teammates can see task status
- Tasks can have dependencies (task B blocks on task A)
- Teammates self-claim available tasks
- When a blocking task completes, dependent tasks auto-unblock

## Designing Team Agents

When creating agents intended for teams, add these considerations to their system prompt:

### 1. Communication protocol
Tell the agent when and how to communicate:
```markdown
## Team communication

- When you complete a task, send your findings to the team lead
- If you discover something that affects another teammate's work,
  message them directly — don't wait
- When blocked, message the teammate you're waiting on
- Keep messages concise — your teammates have their own context to manage
```

### 2. Clear role boundaries
Each teammate should know what's theirs and what isn't:
```markdown
## Your scope

You handle: authentication, authorization, session management
You do NOT handle: database schema, API endpoints, frontend code

If you find issues outside your scope, message the relevant teammate
rather than fixing them yourself.
```

### 3. Shared conventions
If teammates produce artifacts, define common formats:
```markdown
## Reporting format

When reporting findings, use this structure so the team lead
can aggregate easily:

- **Module**: which part of the codebase
- **Finding**: what you found
- **Severity**: critical / warning / info
- **Recommendation**: what should be done
```

## Spawning Teams

Teams are spawned through natural language — no code needed:

```
Create a team to review this PR. I need:
- A security reviewer checking for vulnerabilities
- A performance reviewer checking for bottlenecks  
- A test coverage reviewer checking for missing tests

Have them each review independently and send me their findings.
```

You can reference predefined agent definitions:
```
Spawn a teammate using the security-reviewer agent to audit the auth module.
```

## Display Modes

### In-Process (default)
All teammates in the main terminal. Cycle with `Shift+Down`.

### Split Panes
Each teammate gets its own tmux/iTerm2 pane.

Set globally:
```json
{
  "teammateMode": "split-panes"
}
```

Or per session:
```bash
claude --teammate-mode split-panes
```

## Example: Full Team Configuration

Here's a set of three agents designed to work as a review team:

### Lead: Review Coordinator
```yaml
---
name: review-lead
description: Coordinates code review across multiple specialists
tools: Read, Grep, Glob, Bash, Agent
model: sonnet
---
```

### Teammate: Security Specialist
```yaml
---
name: security-specialist  
description: Security-focused reviewer for team deployments
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: plan
color: red
---
```

### Teammate: Performance Analyst
```yaml
---
name: perf-analyst
description: Performance analysis specialist for team deployments
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: plan
color: yellow
---
```

## Tips

- **Start small**: 2-3 teammates max. Coordination overhead grows fast.
- **Clear roles**: Overlapping responsibilities cause confusion and duplicate work.
- **Lead reviews**: Have the lead synthesize findings rather than dumping raw results.
- **Timeboxing**: Set maxTurns on teammates to prevent runaway sessions.
- **Cost awareness**: Each teammate is a full session. A 3-agent team costs roughly 3x a single session.
