---
name: daily-log
description: Create or update the daily log for the current session in `daily/YYYY-MM-DD.md`. Trigger -- user invokes `/daily-log` explicitly, or indirectly via `/end-session`. Use when the user wants to log what was done today (decisions made, meetings, outputs, next steps) before closing, or to checkpoint mid-day.
---

# /daily-log — Generate the session's daily log

## Purpose

Produce or update `daily/YYYY-MM-DD.md` (today's date) by synthesizing what happened in the current session. This is the **primary way** the user keeps persistent memory of daily work (the "2D" model — I draft, the user confirms/corrects).

## Strict workflow

### Step 1 — Determine the date and path
- Today's date in `YYYY-MM-DD` format (use `date +%Y-%m-%d` if needed)
- Path: `daily/YYYY-MM-DD.md`

### Step 2 — Check existence
- If the file **already exists**: read it. Likely a mid-day checkpoint. I must **integrate** what happened after, not overwrite.
- If it **doesn't exist**: create from scratch.

### Step 3 — Synthesize the current session
Mentally re-read the current conversation. Extract and organize:

1. **What I did** (concrete actions, files touched at macro level)
2. **Decisions taken** (wikilink to `decisions/...` if I created formal ones)
3. **Meetings / relevant interactions** (wikilink to `raw/meetings/...` if I ingested any)
4. **Learnings** (insights that emerged during the session)
5. **Next steps** (todos spilling to the next day)
6. **Free notes** (optional, for uncategorizable items)

### Step 4 — Show the draft to the user
**Don't write the file silently.** First show the user the draft and ask for confirmation or corrections:

> "Here's the draft of today's daily log. Confirm, or do you want to add/correct anything?"

Wait for the response. Iterate if needed.

### Step 5 — Write the file
Strict frontmatter:

```yaml
---
type: daily
date: YYYY-MM-DD
context: {macro-area-slug or 'mixed'}
session-tag: {short session identifier, optional}
---
```

Body in the 6 standard sections above.

### Step 6 — Update INDEX.md
Add an entry under `## Daily logs` in `INDEX.md` (root):

```markdown
- [[daily/YYYY-MM-DD|YYYY-MM-DD]] — {context} — {1-line tagline of the day}
```

**Keep reverse-chronological** (newest on top). When the section grows past ~30 entries, promote to a dedicated sub-INDEX `daily/INDEX.md`.

### Step 7 — Update `hot.md` (hot cache)
`/hot.md` is the ~500-word cache read by the `SessionStart` hook. It must be **overwritten completely** (not appended) — it's a cache, not a journal.

Overwrite `hot.md` with frontmatter:

```yaml
---
type: meta
description: Hot cache — recent-context digest (~500 words)
updated: YYYY-MM-DD
---
```

Body in 4–5 sections:
- **Last Updated**: 1 line with date + session tagline
- **Key Recent Facts**: 3–5 strategic bullets from today and the last 2–3 days (wikilinks to decisions/ and key meetings)
- **Recent Changes**: created / updated / new sub-index from today
- **Active Threads**: next steps, rollovers, open blockers, operational flags (e.g. declared stress)
- **Open Patterns / Hypotheses**: patterns to monitor or promote to knowledge rules

Format reference: the file itself (first iteration is hand-written). If unsure about tone, read the current one to calibrate.

### Step 8 — Append to log.md
Append an entry to `log.md` (root):

```markdown
## [YYYY-MM-DD HH:MM] daily-log | YYYY-MM-DD
- {1 line: what was logged}
- files touched: `daily/YYYY-MM-DD.md`, `INDEX.md`, `hot.md`, `log.md`
```

### Step 9 — Confirm to the user
Final summary: file created/updated + INDEX updated + hot.md updated + log appended. Nothing more.

## Edge cases

- **Empty session** (user invokes `/daily-log` right after opening, without having worked): ask if they want to create a placeholder anyway or skip.
- **Date change during session** (e.g. work past midnight): use the date of the **majority** of the session, and ask if unclear.
- **Session spanning contexts** (multiple macro areas): use `context: mixed` and create distinct subsections under "What I did".

## What NOT to do

- Do not overwrite an existing daily without reading and integrating first.
- Do not invent decisions or meetings that didn't actually happen in the session.
- Do not skip user confirmation before writing.
- Do not create files in other folders (this skill's responsibility is limited to daily/, INDEX, hot.md, log).
