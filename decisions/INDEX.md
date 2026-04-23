---
type: meta
description: Sub-index for the decision journal. Full catalog of all decisions, grouped by topic cluster.
status: evergreen
---

# Decisions — sub-index

> All cross-area decisions live in `decisions/`. This sub-index is the source of truth.
> The root `INDEX.md` shows only the top-5 most recent decisions and links here for the full catalog.

## How to read this

- **Sections** are topic clusters you've defined over time (examples below). Add/rename sections as your system grows.
- **Status**: `active` means in force; `superseded` means replaced by a later decision.
- ⭐ marks a strategic decision (cross-area impact). ⭐⭐ marks a strategic-corporate/architectural pivot.

---

## Tooling & meta

| Date | Decision | Status | Tag |
|---|---|---|---|
| 2026-01-15 | [[decisions/2026-01-15-pick-obsidian-over-notion\|Pick Obsidian over Notion]] | active | tooling |

## Strategy

_(empty — populate as you take cross-area strategic decisions)_

## {macro-area} decisions

_(empty — add a section per macro area as decisions accumulate there)_

---

## How to add a decision here

Triggered by `/log-decision` — the skill writes the new row automatically. If you write a decision manually, mirror the format: one row per decision, newest at the top of its section.

When a decision supersedes another, update the old row's status to `superseded` and link the new one in the "superseded-by" frontmatter of the old file.
