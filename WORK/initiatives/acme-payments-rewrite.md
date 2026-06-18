---
type: initiative
status: active
owner: you
stakeholders: [jane-doe]
priority: P1
tags: [work, acme, payments, migration]
related-prd: none
started: 2026-01-15
last-updated: 2026-01-15
---

# ACME Payments Rewrite

## What we're building / solving
Migrate ACME Corp's 2022-vintage payments system to a new v2 model without a big-bang rewrite. Every feature currently takes ~3 weeks because the data model is wrong. Target: v2 running alongside v1, new transactions routed through v2, old customers grandfathered per-tier, demonstrable milestone by mid-June 2026.

## Current state
Kickoff completed 2026-01-15. Scope doc in draft, due Friday 2026-01-17. Day-to-day contact is Marcus (senior eng, last name _(to confirm via Jane's intro)_).

## Stakeholders
- **Owner**: you (lead architect & embedded consultant, 3 days/week for 2 months then dial down)
- **Sponsor**: [[people/jane-doe|Jane Doe]] — Head of Engineering, owns scope/cadence/cutover decisions
- **CFO sign-off**: _(name to confirm)_ — signs off on per-tier customer cutover plan
- **Engineering day-to-day**: Marcus _(full name to confirm)_

## References
- PRD: _none yet_ — to be drafted in the scope doc (due 2026-01-17)
- Decisions: _(none yet on this initiative)_
- Meetings: [[raw/meetings/2026-01-15-acme-kickoff|ACME kickoff 2026-01-15]]
- Knowledge: _(dual-write migration patterns — to be researched)_

## Scope

### In scope
- New v2 data model, designed for 10× the feature velocity
- Dual-write architecture, v1 + v2 running in parallel
- Per-tier customer cutover plan (tier selection owned by Jane + CFO)
- Engineering-velocity visibility to the ACME board by end of Q2 2026

### Out of scope
- Customer cutover decisions (Jane's call, not mine)
- v1 decommissioning timeline (post end of my engagement)
- Non-payments systems (settlement, reporting, tax — all downstream consumers, not mine to touch)

## Next steps
- [ ] Draft scope doc — owner: you — target: 2026-01-17 (Friday)
- [ ] Set up weekly sync Thursdays 10am ACME-local — owner: you — target: this week
- [ ] Wait for Jane to intro Marcus on the scope thread — owner: Jane — target: this week
- [ ] Research dual-write migration patterns (candidate `/ingest` targets) — owner: you — target: before next Thursday sync

## Blockers
_(none yet)_

## Timeline
- 2026-01-15: kickoff with Jane, scope agreed at high level, engagement shape locked in
