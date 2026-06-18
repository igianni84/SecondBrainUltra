---
type: meta
description: Template and conventions for the decision journal
status: evergreen
---

# decisions/ — Decision journal

Every cross-area decision of consequence lives here. Driven by `/log-decision` (explicit) or `/log-meeting` (extracted from a transcript).

## When to log

Log when you choose between alternatives that impact **beyond today's task**. Examples:
- Picking a tool (wiki, CRM, task tracker, …)
- Architectural choice (dual-write vs cutover, monolith vs extraction, …)
- Strategic positioning (premium vs volume, direct vs partner, …)
- A decision to NOT do something (saying no to a feature, a client, a project)

Do NOT log for:
- Implementation details already specified by a higher-level decision
- Personal preferences (those go in Auto Memory)
- Today's tactical moves (those go in the daily log)

## File naming

`decisions/YYYY-MM-DD-{topic-slug}.md`
- Date = when the decision was made (not when written up)
- Slug = kebab-case, short, describes *the decision*, not the problem

Examples:
- `2026-01-15-pick-obsidian-over-notion.md` ✓
- `2026-01-15-wiki-tooling-thoughts.md` ✗ (describes the topic, not the decision)

## Template

```yaml
---
type: decision
date: YYYY-MM-DD
status: active
tags: [topic1, topic2]
context: {macro-area-slug or 'meta'}
supersedes: []
superseded-by: []
---

# {Decision title — what you decided, 1 line}

## Decision
{what you decided, 1–2 sentences, crisp}

## Context
{why this decision arose, what problem or trigger. Link meetings, PRDs.}

## Alternatives considered
- **Alternative A**: {description}. **Why rejected**: {reason}
- **Alternative B**: {description}. **Why rejected**: {reason}
- **Alternative C**: {description}. **Why rejected**: {reason}

## Reasoning
{why this option won. Be specific: what trade-off mattered most, what constraint was binding, what future state you're optimizing for.}

## Trade-offs accepted
{what you gave up — be honest. Every decision has a cost; name it.}

## References
- Meeting: [[raw/meetings/YYYY-MM-DD-topic|Meeting title]]
- PRD: [[...]]
- Knowledge: [[knowledge/.../...]]
- People involved: [[people/person-slug|Name]]
```

## Supersede semantics

When a new decision replaces an older one:
1. The new decision has `supersedes: [2026-01-15-old-slug]` in frontmatter.
2. The old decision's frontmatter is updated: `status: superseded` + `superseded-by: [2026-03-10-new-slug]`.
3. `decisions/INDEX.md` reflects the status change on the old row.
4. Consider adding a `> [!key-insight]` callout in the new decision summarizing why the old one didn't hold.

Supersede is preferred over in-place edits — the old reasoning is often historically valuable.
