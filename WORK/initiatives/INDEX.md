---
type: meta
description: Sub-index for WORK initiatives. Active / paused / done workstreams.
status: evergreen
---

# WORK — Initiatives

> One row per initiative. Update status/owner/priority as they evolve.
> New initiatives are created via `/new-initiative`.

## Active

| Initiative | Owner | Priority | Started | Status |
|---|---|---|---|---|
| [[WORK/initiatives/acme-payments-rewrite\|acme-payments-rewrite]] | you | P1 | 2026-01-15 | active |

## Paused

_(empty)_

## Done

_(empty)_

---

## Conventions

- **Priority**: P0 (critical, drop everything) / P1 (main focus this month) / P2 (on the plate, not rush)
- **Status**: `active` (being worked) / `paused` (intentionally stopped, may resume) / `done` (completed, keep for history)
- **Archive**: after ~6 months of `done`, consider moving the file to `WORK/archive/` and removing the row from this INDEX — keeps the graph clean.

---

## Template

New initiatives use [[WORK/initiatives/_template|_template.md]] as the starting skeleton. `/new-initiative` copies from the template and fills frontmatter via interview.
