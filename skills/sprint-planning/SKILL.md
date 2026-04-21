---
name: sprint-planning
description: >
  Guide interactive sprint planning and produce a formatted sprint document.
  TRIGGER when: user says "plan sprint", "sprint planning", "new sprint",
  "plan my sprint", "start sprint", "next sprint", "create sprint plan",
  or asks to plan/create a sprint. Also triggers on "/sprint-planning".
---

# Sprint Planning

Interactive skill that guides the user through multi-phase sprint planning
and produces a formatted sprint Markdown document. Uses plan mode throughout
to collaborate before generating the final output.

## Behavior

- Enter plan mode at the start. Stay in plan mode through Phases 0-4.
  Only exit plan mode in Phase 5 to write the final file.
- Work through each phase sequentially. Do not skip phases.
- At each phase, present your understanding and ask for confirmation
  before moving on. Never generate the full document without user approval.
- Keep questions focused — present defaults based on context and ask
  the user to confirm or adjust.

---

## Phase 0 — Load Context & Ask Goals

Before anything else, silently read these files to understand current state:

1. **Latest OKR file:** Find the most recent quarter folder under
   `E:\_WorkDocuments\PlanningProject\Praxilabs\Planning\Quarters\`
   and read the highest-versioned OKRs file (prefer `.md`, fall back to `.xlsx`).
   Extract: objectives, key results, team roster, capacity allocations.

2. **Most recent sprint file:** Read the most recent sprint file (by date,
   regardless of quarter) from
   `E:\_WorkDocuments\PlanningProject\Praxilabs\Planning\Sprints\`.
   Extract: team members, task statuses, any incomplete work (carryover candidates).

After reading context, ask the user:

**"What are the goals for this sprint?"**

Provide the OKR objectives as reference so the user can anchor their goals,
but let them define the actual sprint goals in their own words.
Wait for the user's response before proceeding.

---

## Phase 1 — Sprint Identity

Present what you inferred from context and ask the user to confirm or correct:

1. **Quarter & Sprint number** — Infer from the last sprint file
   (e.g., if last was Q1 S3, next is Q2 S1).
2. **Sprint start date** — The closest upcoming Sunday to today's date.
   If today is Sunday, use today.
3. **Sprint duration** — Always 2 weeks = 10 working days (Sun-Thu work week).
4. **Hours/day** — Show last sprint's values. Ask if changed.
   Clarify both man power and ideal if they differ.

Present as a summary table:

```
| Field          | Value                          |
|----------------|--------------------------------|
| Quarter        | QX YYYY                        |
| Sprint         | Sprint N                       |
| Start Date     | [Closest Sunday], YYYY         |
| End Date       | [Thursday 2 weeks later], YYYY |
| Duration       | 10 working days (Sun-Thu)      |
| Hours/Day      | Xh (man power) / Yh (ideal)   |
```

Ask: **"Does this look correct? Adjust anything before we continue."**

---

## Phase 2 — Team & Carryover

1. **Team members** — List the members from the previous sprint.
   Ask: **"Same team this sprint? Anyone joining or leaving?"**

2. **Carryover** — If the previous sprint had incomplete tasks
   (any status other than done/completed), list them grouped by member.
   Ask: **"Which of these carry over to this sprint?"**

Wait for confirmation before proceeding.

---

## Phase 3 — Sprint Goals Table

Take the goals the user provided in Phase 0 and structure them:

1. Present each goal in a weighted table (1-5 scale).
2. Suggest weights based on how each goal maps to OKR priorities.
3. Briefly note which OKR objective each goal relates to.

```
| # | Goal                                        | Weight | OKR Link      |
|---|---------------------------------------------|--------|---------------|
| 1 | [User's goal]                               | 5      | Obj 1 — ...   |
| 2 | [User's goal]                               | 4      | Obj 2 — ...   |
| ... |
```

Ask: **"Adjust weights or goals? Confirm when ready."**

---

## Phase 4 — Per-Member Task Breakdown

For each team member (one at a time, in order):

1. State the member name and their capacity for this sprint:
   `Capacity: [duration] days x [ideal hours/day] = [total]h`

2. Suggest a **Goal** summary line based on sprint goals and
   their OKR assignments.

3. Propose tasks with hour estimates based on:
   - Their OKR allocation from the OKR file.
   - Any confirmed carryover tasks.
   - Sprint goals relevant to them.

4. Present as:

```
### [Member Name]

**Capacity:** X days x Yh = Zh
**Suggested Goal:** [Summary of what they're working on]

| # | Task                        | Estimate       |
|---|-----------------------------|----------------|
| 1 | [Task description]          | X days (Xh)    |
| 2 | [Task description]          | X days (Xh)    |

**Total: X days (Xh) / Capacity: Y days (Yh)**
```

5. After presenting each member, ask:
   **"Adjust [Name]'s tasks? Confirm, then I'll move to the next member."**

**Estimation rules:**
- Always show both days and hours: `X days (Xh)`.
- Calculate hours as: days x hours/day (use the "ideal" hours value).
- For buffer/stretch tasks, use: `Remaining (~Xh)`.
- Total per member must not exceed capacity. If it does, warn:
  **"[Name] is overallocated by Xh. Reduce or redistribute?"**

---

## Phase 5 — Generate Sprint Document

Only after ALL phases are confirmed, exit plan mode and generate
the final sprint document.

**Output file:**
- Path: `E:\_WorkDocuments\PlanningProject\Praxilabs\Planning\Sprints\YYYY_-_QX_-_SN.md`
- Use the confirmed quarter, year, and sprint number for the filename.

**Document template:**

```markdown
# Sprint Planning — YYYY QX Sprint N

> **Date:** [Confirmed start date]
> **Sprint Duration:** [N] working days
> **Hours/Day:** [X]h (man power) / [Y]h (ideal)

---

## Sprint Goals

| # | Goal | Weight | OKR Link | Achievement |
|---|------|--------|----------|-------------|
| 1 | [Goal] | [W] | [Obj X — KR X.X] | |

---

## Team Sprint Plan

---

### [Member Name]

**Goal:** [Summary]

| # | Task | Estimate | OKR | Logged | Status |
|---|------|----------|-----|--------|--------|
| 1 | [Task] | X days (Xh) | [Obj X — KR X.X] | | Not Started |

| Metric | Value |
|--------|-------|
| Total Estimated | X days (Xh) |
| Total Logged | |
| Buffer Remaining | |

---

[Repeat for each member]

---

## Notes

- *Add any decisions, blockers, or changes mid-sprint here.*
```

**After writing the file**, confirm:
- The file path where it was saved.
- A quick summary: sprint identity, number of goals, team members included.

---

## Phase 6 — Fill Sprint Planning Excel Form

After generating the markdown file, fill the SprintPlanningForm.xlsx located at:
`E:\_WorkDocuments\PlanningProject\Praxilabs\Planning\Quarters\[QUARTER_FOLDER]\Sprints\SprintPlanningForm.xlsx`

Use the xlsx skill to populate the "Sprint Plan" sheet:

1. **Team setup** (Column F onward): Enter each team member's name in the Team column.
   Set ideal hours/day (Column G) and number of days (Column H) for each member.

2. **Tasks** (Columns A-D): For each task from the per-member breakdown:
   - Column A: Task name (Backlog Item)
   - Column B: Assignee name
   - Column C: Estimate in hours
   - Column D: Status (default "Not Started")

3. **Misc activities** (Column M-N): Fill standard meeting estimates:
   - Daily Stand-up, Sprint Planning Meeting, Sprint Review Meeting,
     Retrospective, and any other recurring activities.

4. After filling, confirm the xlsx was updated successfully.

**Note:** If the xlsx file does not exist for the current quarter, skip this phase
and inform the user.

---

## Rules

1. **Never skip phases.** Even if the user provides all info upfront,
   walk through each phase to validate.
2. **Stay in plan mode** through Phases 0-4. Only exit for Phase 5.
3. **Hours/Day display:** If man power equals ideal, show as
   `Xh (man power & ideal)`. If different, show as
   `Xh (man power) / Yh (ideal)`.
4. **Do not hardcode team members.** Always read from the previous sprint
   and OKR files.
5. **Flag overallocation.** If a member's total estimate exceeds capacity,
   warn explicitly and suggest adjustment.
6. **Respect the exact file format.** Match the table structure and
   section ordering from existing sprint files exactly.
7. **One member at a time** in Phase 4. Do not present all members at once.
8. **Work week is Sunday to Thursday.** 5 working days per week.
   Sprint is always 2 weeks = 10 working days.
9. **Start date is always the closest upcoming Sunday** to the planning date.
