---
name: weekly-review
description: Consolidate the current week's (or a specified week's) daily logs into `weekly/YYYY-Www.md`. Trigger -- user invokes `/weekly-review` typically Friday evening or Monday morning. Produces a summary with highlights, trends, decisions, upcoming priorities.
---

# /weekly-review — Weekly summary from dailies

## Purpose

Turn 5–7 daily logs into a weekly view: numbers, highlights, observable trends, decisions made, upcoming priorities. Helps the user see the forest beyond the trees and plan the next week.

## Input

`/weekly-review` (default: current week)
`/weekly-review YYYY-Www` (explicit, e.g. `/weekly-review 2026-W17`)

## Workflow

### Step 1 — Determine the week
- Default: current ISO week (Monday–Sunday). Compute from today's date.
- Explicit: parse `YYYY-Www` from the command.
- Compute `date-start` (Monday) and `date-end` (Sunday) of the week.

### Step 2 — Check existence
Path: `weekly/YYYY-Www.md`.
- If it exists: ask whether to overwrite (regenerate) or add/integrate.

### Step 3 — Collect the week's dailies
Glob `daily/YYYY-MM-DD.md` for each date in range [date-start, date-end].
- If dailies are missing for workdays, flag it to the user (they might want to create them first)
- Read all existing ones

### Step 4 — Extract by category

**Key numbers**:
- Working days tracked (X/5 weekdays)
- Decisions made (count entries in `decisions/` with dates in range)
- Meetings logged (count files in `raw/meetings/` with dates in range)
- Articles ingested (search log.md for "ingest |" entries in range)

**Highlights** (what really happened):
Aggregate by macro area. For each, 2–4 synthetic bullets.

**Observed trends**:
Patterns emerging from the dailies — e.g. "recurring blockers on X", "stakeholder Y becoming key", "initiative Z accelerating". Only if truly observable — do not invent.

**Week's decisions**:
List of wikilinks to `decisions/` created in range.

**Next week**:
Spillover of open todos from dailies + explicit user indications if provided. Ask: "What are the 2–3 priorities for next week?"

### Step 5 — Show draft for confirmation
Show the proposed file. The user can add insights only they can bring (e.g. thoughts from outside the session, feelings, unlogged calls).

### Step 6 — Write `weekly/YYYY-Www.md`

Frontmatter:
```yaml
---
type: weekly
week: YYYY-Www
date-start: YYYY-MM-DD
date-end: YYYY-MM-DD
days-tracked: N
status: seed | developing | mature | evergreen
---
```

Body from the template in `weekly/README.md`.

### Step 7 — Update INDEX and log

`INDEX.md` "Weekly reviews" section:
```markdown
- [[weekly/YYYY-Www|YYYY-Www]] — {date-start} – {date-end} — {1-line tagline}
```

`log.md`:
```markdown
## [YYYY-MM-DD HH:MM] weekly-review | YYYY-Www
- consolidated N daily logs
- files touched: `weekly/YYYY-Www.md`, `INDEX.md`
```

### Step 8 — Suggestions
- "Want me to also update the active `plans/` in light of this week?"
- "Want me to run `/lint` now? It's a good moment for a health-check."

## What NOT to do

- Do not invent numbers: if dailies are missing, declare the gap instead of "estimating".
- Do not write highlights that aren't in the dailies: the review distills, it doesn't add.
- Do not write unobservable trends: if the week is too short or too heterogeneous, say "no significant trends this week".
- Do not overwrite an existing weekly without asking.
