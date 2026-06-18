# Operation Log

> Lean audit trail of every operation on this wiki — **one line per operation**, not a journal.
> Each slash command (`/daily-log`, `/ingest`, `/log-meeting`, `/log-decision`, `/lint`, `/new-initiative`, `/weekly-review`, `/end-session`) appends one line under the current month's `## YYYY-MM` header.
>
> Format (separator is the middle dot ·):
> ```
> - YYYY-MM-DD HH:MM · {op} · {target} → {outcome ≤15 words}
> ```
>
> Compaction: this file keeps only the **current month**. On month rollover, `/end-session` moves concluded months to `log/YYYY-MM.md` (one file per month). The *content* of the work lives in `daily/`, `decisions/`, `knowledge/`, etc. — `log.md` keeps only the mechanical trace (when · what · on what · outcome).

## 2026-01

- 2026-01-15 09:00 · bootstrap · template baseline → initialized SecondBrainUltra from template
