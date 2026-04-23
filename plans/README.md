---
type: meta
description: Conventions for macro plans and multi-month roadmaps
status: evergreen
---

# plans/ — Macro plans

Multi-month roadmaps that don't fit inside a single initiative. Examples:
- "Grow consulting revenue from X to Y over 12 months"
- "Move career from IC to staff-eng"
- "Transition the product from B2B SaaS to PLG"
- "Learn {skill} to proficiency"

A plan is strategic (the _why_ and _what_), not tactical (the _how_). Tactical work lives in:
- `{macro-area}/initiatives/` for operational workstreams
- `daily/` for the day-to-day
- `weekly/` for the retrospective

## When to create a plan

- You want to track progress toward a multi-month goal.
- The goal spans more than one macro area (e.g. affects your day-job and your side venture).
- You want a single place where milestones live.

Do NOT create a plan for:
- Short-horizon tactical work (use an initiative)
- Goals you're not willing to revisit — dead plans bloat the graph.

## Frontmatter

```yaml
---
type: plan
status: seed | developing | mature | evergreen
horizon: {e.g. "12 months", "Q1 2026", "2026"}
started: YYYY-MM-DD
last-updated: YYYY-MM-DD
tags: [topic]
---
```

## Body template

```markdown
# {Plan title}

## North star
{The single outcome you're optimizing for, 1–2 sentences.}

## Why now
{Why this plan matters at this moment — the pressure or opportunity that opens the window.}

## Milestones
- [ ] {Milestone 1} — target YYYY-MM-DD
- [ ] {Milestone 2} — target YYYY-MM-DD
- [ ] {Milestone 3} — target YYYY-MM-DD

## Current state
{Where you are now on the journey. Update on each `/weekly-review`.}

## Blockers & risks
{Things that could derail. Update when they appear or resolve.}

## Related
- Initiatives: [[...]]
- Decisions: [[...]]
- Knowledge domains: [[...]]

## History
- YYYY-MM-DD: {milestone reached / plan revised / blocker resolved}
```

## Review cadence

- Update `last-updated` on every edit.
- Review during `/weekly-review` if the plan was touched by any of the week's decisions or initiatives.
- Run `/lint` to catch plans that haven't been updated in >60 days — decide whether to archive, revise, or close.
