# WORK — Macro-area context

> This is an **example macro area** shipped with the SecondBrainUltra template. It demonstrates the pattern for documenting a context-specific workspace (employer, client portfolio, personal venture).
>
> Rename or duplicate this folder to match your reality. You can have 0–N macro areas.

---

## What this macro area is for

Replace this section with a 1–2 sentence description of what this macro area represents for you:

- If you're a full-time employee, this might be your employer (`ACME/`, `Stripe/`, `Shopify/`).
- If you're a consultant, this might be `CLIENTS/` with one file per client.
- If you run side-projects, this might be `VENTURES/` with one file per project.

**In this template**: WORK/ represents a consulting engagement portfolio. The one example initiative — [[WORK/initiatives/acme-payments-rewrite|ACME Payments Rewrite]] — models what a single client workstream looks like.

---

## Orientation

| Path | What it is |
|---|---|
| [[WORK/CLAUDE.md\|CLAUDE.md]] (this file) | Macro-area context the AI reads first when working in WORK/ |
| [[WORK/initiatives/INDEX\|initiatives/INDEX.md]] | Catalog of all workstreams in this macro area |
| `WORK/initiatives/{slug}.md` | One file per active workstream |
| `WORK/docs/` | (optional) PRDs, specs, reference docs specific to this macro area |
| `WORK/brand/` | (optional) client-facing assets |

---

## Conventions specific to this macro area

_(Customize this section with anything the AI should know when you work here. Examples:)_

- **Primary stakeholder**: {stakeholder name or link to person page}
- **Communication channels**: {preferred channels — Slack, email, specific chat}
- **Documentation source of truth**: {where PRDs, specs, or contracts live — path or URL}
- **Naming conventions**: {any that differ from the root wiki}
- **Restricted content**: {anything confidential, under NDA, or not to be committed to a public repo}

---

## Active initiatives

See [[WORK/initiatives/INDEX|initiatives/INDEX.md]] for the full catalog.

Current highlights:
- [[WORK/initiatives/acme-payments-rewrite|ACME Payments Rewrite]] — active, owner: you, priority: P1

---

## How this relates to the rest of the wiki

- **Daily logs**: when you work in this macro area, tag the daily with `context: work`.
- **Decisions**: strategic decisions for this macro area live in root `decisions/` with `context: work` in frontmatter (not in a `WORK/decisions/` — the decision journal stays unified so cross-area patterns surface).
- **People**: contacts relevant to this area live in root `people/` (again, unified directory — wikilink freely).
- **Knowledge**: domain knowledge specific to this area lives in `knowledge/{domain}/` at the root. If you accumulate enough WORK-specific lore, consider a `knowledge/work-{subdomain}/` folder.

The goal is a **single unified graph**. Macro areas organize *workstreams*, but the underlying knowledge graph stays flat.
