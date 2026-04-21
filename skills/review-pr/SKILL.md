---
name: review-pr
description: >
  Review a PR and generate a summary. Spawns parallel sub-agents
  to analyze commits, shared prefab impact, script changes, and asset changes.
  Aggregates results and updates the PR description. Invoke with /review-pr <PR_NUMBER>.
---

You are the lead orchestrator for PR review analysis on a large Unity virtual labs project (Praxilabs). Your job is to coordinate 4 parallel sub-agents, aggregate their findings, and produce a clear PR review summary.

## Input

The user will provide a PR number as an argument (e.g., `/review-pr 670`). Parse it from the arguments.

## Step 1: Validate the PR

```bash
gh pr view <PR_NUMBER> --json number,title,baseRefName,headRefName,state
```

Extract the base ref and head ref. Verify the PR is open. If not, inform the user and stop.

## Step 2: Get the diff scope

```bash
# Ensure we have latest refs
git fetch origin <baseRefName> <headRefName>

# Get the merge base
MERGE_BASE=$(git merge-base origin/<baseRefName> origin/<headRefName>)

# Count changed files and commits
git diff --name-only $MERGE_BASE..origin/<headRefName> | wc -l
git log --oneline $MERGE_BASE..origin/<headRefName> | wc -l
```

Store the `MERGE_BASE` and `origin/<headRefName>` — these are the two refs all sub-agents will use.

## Step 3: Spawn 4 sub-agents IN PARALLEL

Launch ALL 4 agents in a single message using the Agent tool. Each agent must receive the base and head refs.

### Agent 1: Commit Analyzer
```
subagent_type: review-pr-commit-analyzer (or use the agent file)
prompt: "Analyze commits between <MERGE_BASE> and origin/<headRefName> in the repo at H:\Unity\_Work\Praxilabs\virtual-labs. Base ref: <MERGE_BASE>, Head ref: origin/<headRefName>. Follow your instructions to categorize all commits and extract ticket numbers."
```

### Agent 2: Shared Prefab Impact Analyzer
```
subagent_type: review-pr-prefab-impact (or use the agent file)
prompt: "Analyze shared prefab impact between <MERGE_BASE> and origin/<headRefName> in the repo at H:\Unity\_Work\Praxilabs\virtual-labs. Base ref: <MERGE_BASE>, Head ref: origin/<headRefName>. Follow your instructions to find changed shared prefabs and map them to affected experiments via GUID cross-referencing."
```

### Agent 3: Script Change Analyzer
```
subagent_type: review-pr-script-analyzer (or use the agent file)
prompt: "Analyze C# script changes between <MERGE_BASE> and origin/<headRefName> in the repo at H:\Unity\_Work\Praxilabs\virtual-labs. Base ref: <MERGE_BASE>, Head ref: origin/<headRefName>. Follow your instructions to classify all script changes by risk level."
```

### Agent 4: Asset/Config Change Analyzer
```
subagent_type: review-pr-asset-analyzer (or use the agent file)
prompt: "Analyze asset and config changes between <MERGE_BASE> and origin/<headRefName> in the repo at H:\Unity\_Work\Praxilabs\virtual-labs. Base ref: <MERGE_BASE>, Head ref: origin/<headRefName>. Follow your instructions to categorize all non-script file changes."
```

**IMPORTANT**: Launch all 4 agents in a SINGLE message with 4 Agent tool calls so they run in parallel.

## Step 4: Aggregate results

Once all 4 agents return, combine their reports into the final QA summary using the template below.

### Synthesis rules:
- **Brief Summary**: Write 2-4 sentences covering the most important changes. Mention new experiments, major bug fixes, and high-risk system changes.
- **Bug Fixes**: Take bug fix commits from the commit analyzer and **group them by system/area** (e.g., "Burette System", "Hints UI", "Blood Grouping", "Liquid System"). For each group, write a short summary of what was fixed (not individual commits). Include ticket numbers inline. Individual commit details remain available in the collapsible Detailed Reports section.
- **New Features**: Combine commit analyzer (feature commits) + asset analyzer (new experiments).
- **Systems Changed**: Take from script analyzer's HIGH and MEDIUM risk sections.
- **Experiments Potentially Affected**: Take from prefab impact analyzer. For each affected experiment, include WHAT shared prefab changed so QA knows what to look for.
- **Risk Areas**: Synthesize from all reports. Prioritize: deleted shared assets > HIGH risk script changes > shared prefab changes affecting 3+ experiments > medium risk changes.
- **QA Testing Guide**: Build from all reports. Must Test = HIGH risk items. Should Test = MEDIUM risk + new experiments. Spot Check = LOW risk visual/material changes.

## Step 5: Update the PR

### 5a: Read the existing PR body

```bash
gh pr view <PR_NUMBER> --json body -q .body
```

Store this as `EXISTING_BODY`.

### 5b: Ask the user how to handle the existing body

If `EXISTING_BODY` is non-empty (more than whitespace), use AskUserQuestion to ask:

**Question:** "The PR already has a description. How should I combine it with the review?"

Options:
1. **Keep original + append review (Recommended)** — Preserve the original PR description above a separator, then add the auto-generated review below it.
2. **Re-summarize into one** — Read the original description and merge its context into the Brief Summary section of the review, producing a single unified body.
3. **Replace entirely** — Overwrite the existing body with only the auto-generated review.

If `EXISTING_BODY` is empty, skip this question and write the review directly.

### 5c: Write the final body

Based on the user's choice:

- **Option 1 (Keep + append):** Build the final body as:
  ```
  <EXISTING_BODY>

  ---

  <assembled QA summary markdown>
  ```

- **Option 2 (Re-summarize):** Incorporate key points from `EXISTING_BODY` into the Brief Summary section of the review template. The original body is not preserved verbatim but its context is reflected in the summary.

- **Option 3 (Replace):** Use only the assembled QA summary markdown.

Write the final body to a temp file and update the PR:
```bash
gh pr edit <PR_NUMBER> --body-file <temp_file_path>
```

## PR Summary Template

Use this exact structure for the PR body:

```markdown
# Review Summary

> Auto-generated by `/review-pr` on <today's date>
> PR #<NUMBER>: <headRefName> -> <baseRefName> | <N> commits | <N> files changed

## Brief Summary
<2-4 sentences synthesized from all agent reports>

## Ticket References
<comma-separated list from commit analyzer, or "None found">

---

## Bug Fixes
<Group bug fix commits by system/area. For each group, write a brief summary of what was fixed with ticket numbers inline. Example:>

### Burette System (3 fixes)
Fixed titration endpoint misconception, flickering not triggering correctly, and hand animation not stopping on pause. (NL-XXXX)

### Hints UI (2 fixes)
Fixed mobile hints display issue and progress bar out-of-bounds on first step. (NL-1481)

### [Experiment Name] (N fixes)
<summary of fixes for that experiment>

## New Features / Functionality
<from commit analyzer + asset analyzer — new experiments, new features>

## UI Changes
<from commit analyzer — UI-related commits>

---

## Systems Changed
| System | Risk | What Changed |
|--------|------|-------------|
| <path> | HIGH/MEDIUM | <description> |

## Experiments Potentially Affected

### By Shared Prefab Changes
| Shared Prefab | What Changed | Experiments Affected |
|--------------|-------------|---------------------|
| <prefab name> | <brief change description> | <experiment1>, <experiment2>, ... |

### By Shared Script Changes
| Script | What Changed | Potential Impact |
|--------|-------------|-----------------|
| <script path> | <description> | <impact> |

---

## Risk Areas

### HIGH
- <item>

### MEDIUM
- <item>

### LOW
- <item>

---

## QA Testing Guide

### Must Test (High Priority)
- [ ] <experiment or system to test> — reason: <why>
- [ ] ...

### Should Test (Medium Priority)
- [ ] <experiment or system to test> — reason: <why>
- [ ] ...

### Spot Check (Low Priority)
- [ ] <item> — reason: <why>
- [ ] ...

---

## Detailed Reports

<details>
<summary>Commit Analysis (click to expand)</summary>

<paste full commit analyzer report here>

</details>

<details>
<summary>Shared Prefab Impact Analysis (click to expand)</summary>

<paste full prefab impact report here>

</details>

<details>
<summary>Script Change Analysis (click to expand)</summary>

<paste full script analyzer report here>

</details>

<details>
<summary>Asset & Config Analysis (click to expand)</summary>

<paste full asset analyzer report here>

</details>

---
*Generated by review-pr skill | Agents: commit-analyzer, prefab-impact, script-analyzer, asset-analyzer*
```

## Important Notes

- All sub-agents are READ-ONLY. Only you (the lead) write to the PR via `gh pr edit`.
- If a sub-agent fails or times out, include a note in the summary: "Note: [agent name] did not complete — manual review recommended for [area]."
- If there are no changes in a category (e.g., no shared prefabs changed), still include the section with "None" or "No changes detected."
- The detailed reports go inside `<details>` tags so the summary stays scannable.
- After updating the PR, tell the user: "PR #<NUMBER> updated with QA summary. [link to PR]"
