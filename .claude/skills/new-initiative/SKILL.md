---
name: new-initiative
description: Scaffold a new initiative in `{macro-area}/initiatives/{slug}.md`. Trigger -- user invokes `/new-initiative` when starting a new PM workstream (e.g. new PRD being drafted, new workstream emerging from a meeting). The AI drafts the card from the session and asks the user only for what is missing.
---

# /new-initiative — Scaffold a new initiative

## Purpose

Start a new initiative card in a macro area's `initiatives/` folder. Initiatives track long-running workstreams (weeks/months) — see `{macro-area}/initiatives/README.md` for criteria. A workstream that fits no macro area gets a new one (with the user's confirmation) or a lightweight entry in `plans/`.

## Workflow

### Step 1 — Draft from the session
Fill `{macro-area}/initiatives/_template.md` with what the session and the vault already say:
- macro area (`ls` the root for the existing ones), name, and a kebab-case slug
- the related PRD, if there is one
- stakeholders, as slugs from `people/`
- tags beyond the macro-area tag
- "What we're building / solving": 1–2 sentences on the desired outcome and why it's worth doing

Where there is no source, leave `{from the user}` in the frontmatter and `*(to populate)*` in the sections: a card starts as an honest skeleton.

If `{macro-area}/initiatives/{slug}.md` already exists, stop and propose updating it.

### Step 2 — One round with the user
Show the draft and, below it, the questions left, numbered, each with your proposal. Owner and priority are always theirs to confirm: propose the user as owner, `P1`, `active`.

### Step 3 — Write `{macro-area}/initiatives/{slug}.md`
From the template. At the start of the "Timeline" section:
```markdown
- YYYY-MM-DD: card created via /new-initiative
```

### Step 4 — Update `{macro-area}/initiatives/INDEX.md`
A row in the "Active" table:
```markdown
| [[{macro-area}/initiatives/{slug}\|{slug}]] | {owner} | {priority} | YYYY-MM-DD | active |
```

The last cell is a pointer: the status and, at most, the latest source with one sentence, 30 words in all. State and timeline live in the card. Done when `bash .claude/hooks/check-index-caps.sh` prints nothing.

### Step 5 — Update `hot.md`
If the initiative changes the *Active Threads*, it enters in place of an older thread, following `CLAUDE.md` §4bis. Done when `wc -w hot.md` gives at most 700; if everything is needed, go over and tell the user how many words and why. A low-priority exploration leaves `hot.md` alone.

### Step 6 — Append to log.md
One line in `log.md`, under the current month's header `## YYYY-MM` (create it if missing), with the time from `date +%H:%M`:
```
- YYYY-MM-DD HH:MM · new-initiative · {slug} → created initiative card "{name}"
```

### Step 7 — Connections
Propose in one line: a reference in `{macro-area}/CLAUDE.md` (if present) and, if launching the workstream was a choice between alternatives, a `/log-decision`.
