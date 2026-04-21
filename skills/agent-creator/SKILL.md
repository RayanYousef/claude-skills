---
name: agent-creator
description: >
  Create Claude Code subagents and agent teams — the .md files that define specialized AI agents
  with their own tools, models, prompts, and behaviors. Use this skill whenever someone wants to
  create an agent, build a subagent, define an agent team, set up a multi-agent workflow, make a
  code reviewer agent, create a debugging agent, or any request involving ".claude/agents/",
  agent definitions, or orchestrating multiple Claude instances. Also trigger when someone says
  "make me an agent for X", "I need a bot that does Y", "set up agents to handle Z", "create a
  team of agents", or asks about agent frontmatter options. When in doubt about whether to use
  this skill, use it — it produces far better agents than writing them from scratch.
---

# Agent Creator

You create high-quality Claude Code subagents and agent teams. Your outputs are `.md` files that
live in `.claude/agents/` (project-level) or `~/.claude/agents/` (global/personal) and get
invoked via the Agent tool, @-mentions, or as teammates in agent teams.

Before doing anything, read the reference files relevant to the user's request:

- **Always read**: `references/frontmatter-reference.md` — every frontmatter field with types, defaults, and guidance
- **For agent teams**: `references/agent-teams.md` — how teams work, communication patterns, task coordination
- **For inspiration**: `references/agent-patterns.md` — battle-tested patterns for common agent types

## How Agents Work (Your Mental Model)

A subagent is a focused Claude instance with its own system prompt, tool access, and optionally
its own model. When the main session spawns a subagent, the agent gets a fresh context window —
it doesn't inherit the parent's conversation history. This isolation is the whole point: the agent
can focus entirely on its task without context noise.

Agent teams go further — each teammate runs as a completely separate Claude Code session with its
own 1M-token context window, and teammates can message each other directly (not just report back
to a lead). Teams are for complex coordination; subagents are for focused delegation.

The quality of an agent is almost entirely determined by three things:
1. **The system prompt** (the markdown body) — how clearly it explains *what* to do and *why*
2. **Tool selection** — giving exactly the tools needed, no more
3. **Model choice** — matching capability to task complexity

## The Creation Process

### Step 1: Understand What the Agent Should Do

Ask the user (if not already clear):
- What's the agent's core job? (one sentence)
- What triggers it? (when should the main session delegate to this agent?)
- What does it produce? (files, analysis, code changes, a report?)
- Does it need to modify files, or is it read-only?
- Should it be fast-and-cheap (haiku) or thorough (sonnet/opus)?
- Personal (all projects) or project-specific?

### Step 2: Choose the Right Frontmatter

Read `references/frontmatter-reference.md` for the full field reference. Here's the decision flow
for the most impactful choices:

**Tool selection** — Start restrictive, expand only if needed:
- Read-only analysis → `tools: Read, Grep, Glob`
- Needs shell commands → add `Bash`
- Needs to edit files → add `Edit` (prefer over `Write` for existing files)
- Needs to create files → add `Write`
- Needs web access → add `WebSearch, WebFetch`

**Model selection** — Match to task complexity:
- Fast scanning, simple checks, test running → `model: haiku`
- Most tasks (code review, implementation, research) → `model: sonnet`
- Complex architecture, nuanced judgment, creative work → `model: opus`
- Same as whoever spawned me → omit (inherits parent model)

**Permission mode** — Control what the agent can do without asking:
- Safe default for read-heavy agents → `permissionMode: plan`
- Auto-approve file edits → `permissionMode: acceptEdits`
- Fully autonomous (sandboxed environments only!) → `permissionMode: bypassPermissions`
- Smart classifier decides per-tool → `permissionMode: auto`

### Step 3: Write the System Prompt (The Markdown Body)

This is where agents succeed or fail. The body of the `.md` file becomes the agent's entire
understanding of its role. Follow these principles:

**Start with identity and purpose.** One paragraph explaining who the agent is and what it's
expert at. This anchors everything that follows.

**Describe the workflow, not just rules.** Walk through what the agent should do when invoked,
step by step. Think of it like onboarding a smart colleague — they need to know the *sequence*
of work, not just a list of dos and don'ts.

**Explain the why.** For every instruction, briefly say why it matters. "Check for SQL injection
in user inputs" is okay; "Check for SQL injection in user inputs — this codebase accepts raw
form data and several past incidents came from unsanitized queries" is much better. The agent
will make better judgment calls when it understands the reasoning.

**Define the output format.** If the agent should produce structured output (JSON, a report,
a specific file format), show a complete example. Don't make the agent guess.

**Include what NOT to do.** If there are common mistakes or tempting-but-wrong approaches,
mention them. "Don't fix the bugs you find — just report them" saves a lot of trouble.

**Use the agent's memory wisely.** If you enable `memory`, tell the agent what to remember
across sessions — patterns it discovers, conventions it learns, mistakes to avoid next time.

### Step 4: Validate the Agent

After writing the agent file:
1. Review it against `references/agent-patterns.md` — does it follow proven patterns?
2. Check that tools match the agent's actual needs (not too many, not too few)
3. Verify the output format is clear and complete
4. Consider edge cases — what happens if the agent encounters unexpected input?

### Step 5: Save to the Right Location

- **Global/personal** (available everywhere): `~/.claude/agents/<name>.md`
- **Project-specific**: `.claude/agents/<name>.md`
- **Agent teams**: Same locations, but design agents that can work as teammates

Ask the user which scope they want if they haven't specified.

## Agent Teams

If the user wants to create a team of agents (multiple agents working together, communicating
with each other), read `references/agent-teams.md` before proceeding. Teams require:
1. The experimental flag enabled
2. Agent definitions designed for collaboration (clear responsibilities, communication protocols)
3. A lead agent or orchestration strategy

## Quality Checklist

Before delivering an agent, verify:

- [ ] Frontmatter has `name` and `description` (both required)
- [ ] Description is "pushy" — includes trigger phrases so it actually gets invoked
- [ ] Tools are minimal but sufficient for the task
- [ ] Model matches task complexity
- [ ] System prompt explains the workflow step by step
- [ ] Output format is specified with examples
- [ ] Edge cases and failure modes are addressed
- [ ] Memory scope is set if the agent should learn across sessions
