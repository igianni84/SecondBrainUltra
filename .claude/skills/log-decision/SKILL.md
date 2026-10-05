---
name: log-decision
description: Create a new entry in `decisions/` formalizing a strategic decision. Trigger -- user invokes `/log-decision` to register a decision made explicitly or emerged from a conversation (even outside a meeting). The AI interviews to fill context, alternatives, reasoning, trade-offs.
---

# /log-decision — Register a formal decision

## Purpose

Cross-area decisions live in `decisions/`. This skill formalizes them with the standard pattern (context → alternatives → reasoning → trade-offs → references).

Different from `/log-meeting` (passively extracts decisions from a transcript) — here the user actively decides to register a decision.

## Workflow

### Step 1 — Identify the decision
Ask the user:
1. **What did you decide?** (1–2 sentences)
2. **Which topic/area?** (for slug and tags)

From these, build the filename: `decisions/YYYY-MM-DD-{topic-slug}.md`

### Step 2 — Check prior decisions
Before writing, **search `decisions/`** for existing entries on the same topic. If found:
- Show the user: "There's already `[[decisions/YYYY-MM-DD-old-topic]]`. Do you want to (a) create a new one that supersedes it, (b) edit the existing one, (c) cancel, or (d) create a new one that supersedes only part of it?"
- If new-supersede: the new one has `supersedes: [old-id]`, the old one becomes `status: superseded` with `superseded-by: [new-id]`.
- If it supersedes only part: the new one has `supersedes-partially: [old-id]`; the old one stays `status: active` and gets `superseded-partially-by: [new-id]`. Ids are the slug, without `decisions/`.

### Step 3 — Interview to fill the template
Ask the questions from the decision template:

1. **Context**: why did this decision arise? What problem/trigger?
2. **Alternatives considered**: what else was on the table? (at least 2–3)
3. **Reasoning**: why did this option win?
4. **Trade-offs accepted**: what did you give up? (be honest)
5. **References**: which meetings/PRDs/knowledge entries are related?

One question at a time. Wait for the answer. Do not fill in on your own.

### Step 4 — Show draft for confirmation
Compose the file with frontmatter + body. Show the user. Ask for confirmation or corrections.

### Step 5 — Write `decisions/YYYY-MM-DD-{topic-slug}.md`

Frontmatter:
```yaml
---
type: decision
date: YYYY-MM-DD
status: active
tags: [topic1, topic2]
context: {macro-area-slug or 'meta'}
supersedes: []  # ids of any decisions this supersedes
superseded-by: []  # empty at creation time
---
```

Body (from template in `decisions/README.md`):

```markdown
## Decision
{what you decided, 1–2 sentences}

## Context
{why this decision arose, what trigger/problem}

## Alternatives considered
- **Alt A**: {description}, why rejected
- **Alt B**: {description}, why rejected

## Reasoning
{why this option won}

## Trade-offs accepted
{what you gave up}

## References
- Meeting: [[raw/meetings/...]]
- PRD: [[...]]
- Knowledge: [[knowledge/.../...]]
```

### Step 6 — If superseding: update the old one
Open the prior decision's file, change frontmatter:
- `status: superseded`
- `superseded-by: [new-id]`

If it supersedes only part: `status` stays `active`; add `superseded-partially-by: [new-id]` and, at the top of the "Decision" section, a `> [!stale]` callout saying which part is superseded, with the link to the new one.

### Step 7 — Update sub-index + INDEX root
Pattern: **sub-index first, INDEX root after**.

**A. `decisions/INDEX.md`** (mandatory) — add a row in the appropriate section's table. The sections in `decisions/INDEX.md` are organized by the user's chosen topic clusters (see `decisions/INDEX.md` itself for current section names). If no section fits, create one or use a catch-all. Format:
```markdown
| YYYY-MM-DD | [[decisions/YYYY-MM-DD-{slug}\|{title}]] | active | {key tag} |
```
If a decision supersedes an earlier one, update the old row's status to **superseded**. If it supersedes only part, the old row's status becomes `active *(point N superseded → [[decisions/{new-slug}\|YYYY-MM-DD]])*`.

**B. `INDEX.md` (root)** "Decisions" section — only if the decision deserves to be in the top-5 recent ones shown at root level. If yes, include it and remove one less recent/relevant. Always keep the top link to `[[decisions/INDEX|decisions/INDEX]]`.

### Step 8 — Update `hot.md`
If the decision is strategic or architectural, update `hot.md` (complete overwrite). If purely tactical, you can skip.

⛔ **The cache replaces, it doesn't accumulate**: the decision enters *Key Recent Facts* in place of an old fact, not on top. `updated:` is only the date. Before closing: `wc -w hot.md` → **≤ 700 words**, or tell the user how many and why (caps: `CLAUDE.md` §4bis).

### Step 9 — Append to log.md
Append **a single line** to `log.md` (root), under the current month's header `## YYYY-MM` (create it if the current month's header is missing):
```
- YYYY-MM-DD HH:MM · log-decision · {slug} → {what was decided, in brief; +superseded {slug} if applicable}
```

### Step 10 — Connections
Suggest to the user:
- Do you want to link this decision from an initiative card?
- Do you want to update a rule/hypothesis in knowledge?
- Do you want to include this decision in today's `daily/`?

## What NOT to do

- Do not write without interviewing: decision journal quality comes from rigor in context/alternatives/trade-offs.
- Do not invent alternatives if the user says "there really weren't alternatives" — record that this was the only viable path and why.
- Do not auto-supersede without explicit confirmation.
- Do not duplicate existing `decisions/` — use the supersede system.
