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

### Step 3 — Append "session-end" to log.md
Add a final entry to `log.md`:

```markdown
## [YYYY-MM-DD HH:MM] session-end | {1-line summary}
- files touched in the session: {macro list}
- next session: {if the user has indicated anything}
```

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

### Step 5 — Push
```bash
git push
```

If it's the branch's first push:
```bash
git push -u origin main
```

If push fails (divergence, authentication, network):
- Honest report to the user
- NEVER use `--force` (even if git suggests it)
- Suggest `git pull --rebase` if it's just divergence

### Step 6 — Final summary
Show the user:
- Daily log: `daily/YYYY-MM-DD.md`
- INDEX and log updated
- Commit `<sha>` on `main`
- Push to `origin/main` successful (or push status)
- Any open todos for the next session

One closing line, e.g. *"Session closed. See you next time."*

## What NOT to do

- Do not skip `/daily-log` — it's the heart of persistent memory.
- Do not commit with `--no-verify` or `--amend` (never, unless explicitly requested).
- Do not `--force` push.
- Do not proceed without explicit user confirmation if `git status` shows suspicious files.
- Do not leave the session without pushing (unless the user explicitly says not to).

## Edge cases

- **Nothing to commit**: after daily-log the commit might be unnecessary. In that case just daily + push (if daily produced changes).
- **Work in intermediate state** (unfinished refactor): the user might not want to commit. Ask first.
- **No connection for push**: `daily/` and `log.md` stay committed locally; push happens next session. Warn the user.
