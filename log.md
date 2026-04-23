# Operation Log

> Append-only chronological log of every operation on this wiki.
> Each slash command (`/daily-log`, `/ingest`, `/log-meeting`, `/log-decision`, `/lint`, `/end-session`, `/weekly-review`, `/new-initiative`) adds an entry here.
>
> Format:
> ```
> ## [YYYY-MM-DD HH:MM] {op} | {target}
> - bullet describing what changed
> - files touched: `a.md`, `b.md`
> ```

<!-- Newest entries on top. Oldest at the bottom gets rotated to log-archive-YYYY.md when this file exceeds ~5000 lines. -->

## [YYYY-MM-DD HH:MM] bootstrap | template baseline
- Initialized SecondBrainUltra from template.
- Files touched: scaffold — see `git log` for the full initial commit.
