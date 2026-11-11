---
name: daily-log
description: Create or update the daily log for the current session in `daily/YYYY-MM-DD.md`. Trigger -- user invokes `/daily-log` explicitly, or indirectly via `/end-session`. Use when the user wants to log what was done today (decisions made, meetings, outputs, next steps) before closing, or to checkpoint mid-day.
---

# /daily-log — Generate the session's daily log

## Purpose

Produce or update `daily/YYYY-MM-DD.md` (today's date) by synthesizing what happened in the current session. This is the **primary way** the user keeps persistent memory of daily work (the "2D" model — I draft, the user confirms/corrects). The skill touches four files: the daily, `INDEX.md`, `hot.md`, `log.md`.

## Strict workflow

### Step 1 — Determine the date and path
- Today's date in `YYYY-MM-DD` format (`date +%Y-%m-%d`). If the session ran past midnight, use the date of the **majority** of the work, and ask if unclear.
- Path: `daily/YYYY-MM-DD.md`

### Step 2 — Check existence
- If the file **already exists**: read it. It's a mid-day checkpoint or another session's work. **Integrate** what happened after; the rest stays as it is.
- If it **doesn't exist**: create from scratch.

### Step 3 — Synthesize the current session
From the current conversation, six sections:

1. **What I did** (concrete actions, files touched at macro level; one subsection per macro area if the session spanned several)
2. **Decisions taken** (wikilink to `decisions/...` if formal ones were created)
3. **Meetings / relevant interactions** (wikilink to `raw/meetings/...`)
4. **Learnings** (insights that emerged during the session)
5. **Next steps** (todos spilling to the next day)
6. **Free notes** (optional)

Only what actually happened in the session goes in.

### Step 4 — Show the draft to the user
Show the draft and wait for confirmation or corrections; iterate if needed. If the session is empty (the user invoked `/daily-log` right after opening), ask whether to create a placeholder or skip.

### Step 5 — Write the file

```yaml
---
type: daily
date: YYYY-MM-DD
context: {macro-area-slug or 'mixed'}
session-tag: {short session identifier, optional}
---
```

Body: the six sections of Step 3.

### Step 6 — Update INDEX.md
Under `## Daily logs` in `INDEX.md` (root), newest on top:

```markdown
- [[daily/YYYY-MM-DD|YYYY-MM-DD]] — {context} — {1-line tagline of the day}
```

If the day is already listed, update its line. The section keeps the latest 14 entries with a 1-line gloss: the entry that falls off leaves whole. Older dailies are browsed from the `daily/` folder, and their weekly links them.

Done when `bash .claude/hooks/check-index-caps.sh` prints nothing: it measures the caps, and what it reports gets fixed before the step closes.

### Step 7 — Update `hot.md` (hot cache)
Overwrite `hot.md` completely, following `CLAUDE.md` §4bis: five sections with their caps, and what comes in takes the place of what the next session no longer needs. In the frontmatter only `updated:` changes, and it holds only the date. A pattern that lives only in `hot.md` is written to `knowledge/{domain}/hypotheses.md` before it leaves.

Done when `wc -w hot.md` gives at most 700. If everything is needed, go over and tell the user how many words and why.

### Step 8 — Append to log.md
One line in `log.md` (root), under the current month's header `## YYYY-MM` (create it if missing), with the time from `date +%H:%M`:

```
- YYYY-MM-DD HH:MM · daily-log · {target} → {outcome ≤15 words}
```

Called by `/end-session`, skip this step: the session gets one line, the `session-end` one.

### Step 9 — Confirm to the user
Daily, INDEX, `hot.md`, log: one line each.
