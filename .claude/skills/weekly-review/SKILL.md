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
- Articles ingested (search log.md for "· ingest ·" entries in range)

**Highlights** (what really happened):
Aggregate by macro area (e.g. WORK, CLIENTS, VENTURES, LIFE). For each, 2–4 synthetic bullets.

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
generated: routine | backfill   # ONLY in non-interactive mode; omit when written with the user
---
```

Body: the sections extracted in Step 4 (Key numbers, Highlights, Observed trends, Week's decisions, Next week). Use the example `weekly/2026-W03.md` as a format reference.

At the bottom, always `## References` with `- Dailies of the week: [[daily/YYYY-MM-DD]] · …`, one link per daily. `INDEX.md` keeps only the latest 14 dailies: past those, the weekly is what links a daily, and without it the lint reports the daily as an orphan.

### Step 7 — Update INDEX and log

`INDEX.md` "Weekly reviews" section:
```markdown
- [[weekly/YYYY-Www|YYYY-Www]] — {date-start} – {date-end} — {1-line tagline}
```

`log.md` — append ONE single line under the current month's header (`## YYYY-MM`, create it if missing):
```
- YYYY-MM-DD HH:MM · weekly-review · YYYY-Www → consolidated N dailies
```

### Step 8 — Suggestions
- "Want me to also update the active `plans/` in light of this week?"
- "Want me to run `/lint` now? It's a good moment for a health-check."

## Non-interactive execution (scheduled cloud routine / backfill)

When the skill is invoked **headlessly** — by a scheduled weekly cloud routine (runs every Monday morning with nobody present to confirm) or to **backfill** past weeks — adapt the workflow:

- **Skip** Step 2 (the overwrite prompt), the priorities question in Step 4, and Step 5 (draft confirmation). Generate directly.
- **Idempotency guard**: if `weekly/YYYY-Www.md` **already exists → do nothing** and exit. Never overwrite a weekly the user may have hand-refined.
- **"Next week"**: derive the todos from the week's daily spillover. Lacking the user's input, mark the file in the **frontmatter** with `generated: routine` (or `backfill`) — ⛔ never with a `[!gap]` callout. Where a file comes from is a stable fact, so it goes in the frontmatter; a callout is an open question someone has to answer, and the lint would count one in every generated weekly.
- All "What NOT to do" rules still apply: do not invent numbers, highlights, or trends. If the week has few tracked days, write "no significant trends this week".
- **Only for the scheduled cloud routine** (not for backfill, which the main thread handles): after writing the file and updating `INDEX.md` + `log.md`, run `git add` + commit + push to the default branch. Use a model-agnostic commit message and sign it:
  ```
  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

## What NOT to do

- Do not invent numbers: if dailies are missing, declare the gap instead of "estimating".
- Do not write highlights that aren't in the dailies: the review distills, it doesn't add.
- Do not write unobservable trends: if the week is too short or too heterogeneous, say "no significant trends this week".
- Do not overwrite an existing weekly without asking (interactive mode) or silently (non-interactive mode exits instead).
