---
name: end-session
description: Cleanly close a working session. Trigger -- user invokes `/end-session` when they are done and about to close Claude Code. Runs in order -- daily-log + update log.md + git add/commit/push. This is the standard way to ensure every session produces persistent memory and ends up on GitHub.
---

# /end-session — Clean session shutdown

## Purpose

Wrapper that ensures every working session **does not get lost**:
1. Knowledge that emerged is captured in `daily/YYYY-MM-DD.md` (via `/daily-log`)
2. The chronological log is updated
3. All changes are committed and pushed to GitHub

"2D" model: user invokes me before closing, I produce the session summary, user confirms, I commit.

## Strict workflow

### Step 1 — Run `/daily-log`
Invoke/execute the `/daily-log` workflow (see `.claude/skills/daily-log/SKILL.md`):
- Determine date
- Synthesize session
- Show draft to user
- Wait for confirmation
- Write `daily/YYYY-MM-DD.md`
- Update `INDEX.md` (Daily logs section)
- Update `hot.md` (hot cache ~500 words)
- Append to `log.md`

**Do not proceed to next steps until the user has confirmed the daily log.**

> **Note on `Stop` hook**: the hook in `.claude/settings.json` emits a `HOT_CACHE_REMINDER` if the wiki was touched but `hot.md` is not among the changed files in the commit. If the reminder fires after `/daily-log` has already run, it's a false positive (daily-log already updates `hot.md`) — ignore it.

### Step 2 — Check repo status
```bash
git status --short
```

Show the user what will be committed. If unexpected files appear (not session-related), ask for explicit confirmation before proceeding — they might be works-in-progress that shouldn't be committed.

### Step 3 — Append "session-end" to log.md (lean audit, 1 line)
`log.md` is a **lean audit, not a journal**: one line per operation, under the current month's header `## YYYY-MM`. It holds only the **current month** — it distills, it does not accumulate.

Do this in order:

1. **Month-rollover check (before appending).** Inspect the monthly headers (`## YYYY-MM`) already present in `log.md`. If any entries sit under a **concluded** month's header (any month earlier than the current one — e.g. today is July but a `## 2026-06` section is still there):
   - **Move** each concluded month's entire section into `log/YYYY-MM.md` — one file per month. Create the file if it doesn't exist, or append to the end of it if it already exists.
   - Leave **only** the current month's `## YYYY-MM` section in `log.md`. Create that header if it isn't there yet.
   This is the mechanism that keeps `log.md` bounded.
2. **Append the new entry.** Add exactly **one line** under the current month's header, using the canonical format (separator = middle dot `·`):

```
- YYYY-MM-DD HH:MM · session-end · {session in 3-4 words} → {macro files touched; next priority if known}
```

The *content* of the work lives in `daily/`, `decisions/`, `people/`, `knowledge/`, etc. — `log.md` keeps only the mechanical trace (when · what · on what · outcome, ≤15 words).

### Step 4 — Stage + commit
```bash
git add .
```

Re-check with `git status --short` what is staged. If sensitive files slip through `.gitignore` (keys, tokens, unfinished work files), **STOP** and flag — do not commit.

Commit message — use HEREDOC with format:

```
session: YYYY-MM-DD — {short tagline}

{2–4 bullets of what was done, for history}

Co-Authored-By: Claude <noreply@anthropic.com>
```

If you are on the default branch and the work warrants a branch, branch off first; otherwise commit on the current branch. Commit only as part of this `/end-session` flow (or when the user explicitly asks).

### Step 5 — Push
```bash
git push
```

If it's the branch's first push:
```bash
git push -u origin <branch>
```

If push fails (divergence, authentication, network):
- Honest report to the user
- NEVER use `--force` (even if git suggests it)
- Suggest `git pull --rebase` if it's just divergence

### Step 6 — Final summary
Show the user:
- Daily log: `daily/YYYY-MM-DD.md`
- INDEX and log updated
- Commit `<sha>` on the current branch
- Push successful (or push status)
- Any open todos for the next session

One closing line, e.g. *"Session closed. See you next time."*

## What NOT to do

- Do not skip `/daily-log` — it's the heart of persistent memory.
- Do not commit with `--no-verify` or `--amend` an already-pushed commit (never, unless explicitly requested).
- Do not `--force` push.
- Do not proceed without explicit user confirmation if `git status` shows suspicious files.
- Do not leave the session without pushing (unless the user explicitly says not to).

## Edge cases

- **Nothing to commit**: after daily-log the commit might be unnecessary. In that case just daily + push (if daily produced changes).
- **Work in intermediate state** (unfinished refactor): the user might not want to commit. Ask first.
- **No connection for push**: `daily/` and `log.md` stay committed locally; push happens next session. Warn the user.
