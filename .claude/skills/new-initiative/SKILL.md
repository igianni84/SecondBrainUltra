---
name: new-initiative
description: Scaffold a new initiative in `{macro-area}/initiatives/{slug}.md`. Trigger -- user invokes `/new-initiative` when starting a new PM workstream (e.g. new PRD being drafted, new workstream emerging from a meeting). The AI interviews to fill frontmatter and base sections.
---

# /new-initiative — Scaffold a new initiative

## Purpose

Start a new initiative card in a macro area's `initiatives/` folder. Initiatives track long-running workstreams (weeks/months) — see `{macro-area}/initiatives/README.md` for criteria.

## Workflow

### Step 1 — Identify the macro area and initiative
Ask the user:
1. **Which macro area does this belong to?** (e.g. `WORK`, `CLIENTS`, `VENTURES`) — show existing ones.
2. **Initiative name** (human-readable, short)
3. **Slug** suggested (kebab-case) — propose a default based on the name, user confirms or tweaks
4. **Is there an existing PRD, or is this from scratch?** (path to the PRD if yes)

Verify that `{macro-area}/initiatives/{slug}.md` doesn't already exist. If it does, flag and ask whether to edit instead of create.

### Step 2 — Fill frontmatter via interview
Questions:
1. **Initial status**: `active`, `paused`, `done`? (default: `active`)
2. **Owner**: who's responsible? (default: the user)
3. **Stakeholders**: who's involved? (slugs of people, separated by dev/business/legal/other)
4. **Priority**: P0/P1/P2 (default `P1`, confirm)
5. **Tags**: what specific tags beyond the macro-area tag? (e.g. `payments`, `backend`, `allocation`)

### Step 3 — Fill body sections (at least the first)

**What we're building / solving** (mandatory):
Ask the user for 1–2 sentences on the desired outcome and why it's worth doing.

**Current state** (optional):
If they already know the state, summarize. Otherwise leave as `*(to populate)*`.

**Stakeholders** (optional but recommended):
Partially in frontmatter — expand here with specific roles.

**References**:
- PRD: if one was mentioned, wikilink to the correct path
- Decisions, meetings, knowledge: leave placeholders if empty

**Next steps / Blockers / Timeline**:
Empty initially, unless the user wants to populate now.

### Step 4 — Show draft for confirmation
Show the complete file to the user. Iterate if needed.

### Step 5 — Write `{macro-area}/initiatives/{slug}.md`
Use the template in `{macro-area}/initiatives/_template.md` as a base, filled with the captured values.

Add at the start of the "Timeline" section:
```markdown
- YYYY-MM-DD: initial scaffold via /new-initiative
```

### Step 6 — Update `{macro-area}/initiatives/INDEX.md`
Add a row in the "Active" table:
```markdown
| [[{macro-area}/initiatives/{slug}\|{slug}]] | {owner} | {priority} | YYYY-MM-DD | active |
```

### Step 7 — Update `hot.md`
A new initiative almost always shifts "Active Threads" in the hot cache. Update `hot.md` (complete overwrite, ~500 words). If the initiative is marginal (e.g. exploration, low priority), you can skip.

### Step 8 — Append to log.md
Append ONE single line under the current month's header in `log.md` (`## YYYY-MM`, create it if the current month's header is missing):
```
- YYYY-MM-DD HH:MM · new-initiative · {target} → created initiative card "{name}"
```

### Step 9 — Final suggestions
- "Do you want to update `{macro-area}/CLAUDE.md` (if present) with a reference to the new initiative?"
- "Do you want to create a `decisions/` entry for the strategic decision to launch this initiative?"

## What NOT to do

- Do not duplicate existing initiatives — check `{macro-area}/initiatives/INDEX.md` first.
- Do not assign priority/owner without asking — operational data only the user knows.
- Do not create a card with invented body: an honest empty skeleton beats plausible fiction.
- For initiatives that don't fit any existing macro area: either create a new macro area (with the user's confirmation) or use `plans/` for lightweight tracking.
