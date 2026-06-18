---
name: ingest
description: Process a file in `raw/` (article, note, screenshot, transcript) and extract its value into the wiki -- summary, cross-reference, INDEX, log. Trigger -- user invokes `/ingest <path>` after dropping a file in `raw/articles/`, `raw/notes/`, or `raw/assets/`. For Meet transcripts use `/log-meeting` instead. Uses a fan-out pattern (parallel sub-agents on isolated files) to cut wall-clock time and keep the main context clean.
---

# /ingest — Process a raw asset into the wiki (fan-out pattern)

## Purpose

The `raw/` layer is immutable. `/ingest` reads a file in `raw/`, extracts useful content, integrates it into the wiki (`knowledge/`, `decisions/`, `people/` as relevant), and updates the indexes — **without burning the main context** by writing every file inline.

When the ingest produces 2+ isolated wiki files, MAIN fans out one sub-agent per file, in parallel. Each sub-agent owns exactly one file; MAIN owns the shared catalog files. This is the same architecture as `/log-meeting`, slimmed down because `/ingest` typically touches fewer files.

## Input

`/ingest <path>` where `<path>` is a file inside `raw/articles/`, `raw/notes/`, or `raw/assets/`.

For `raw/meetings/`, use `/log-meeting` instead (it has dedicated logic).

## Architecture (4 phases)

```
PHASE 1 — MAIN: read the raw + discuss + decide which wiki files result
PHASE 2 — FAN-OUT: N parallel sub-agents, each on ONE isolated file
PHASE 3 — MAIN: write SHARED files sequentially (sub-index → root INDEX → hot.md → log.md)
PHASE 4 — MAIN: recap to the user
```

### Isolated vs. shared files (the taxonomy that makes fan-out safe)

```
ISOLATED files (parallelizable — one sub-agent each):
- knowledge/{domain}/knowledge.md   (merge — append a titled entry)   — almost always
- knowledge/{domain}/hypotheses.md  (merge — if there's an insight to confirm)   [optional]
- decisions/YYYY-MM-DD-{slug}.md    (create)   [optional, if the user decides something]
- people/{slug}.md                  (create)   [optional, if a new relevant person appears]

SHARED files (MAIN only, at the end, sequential):
- knowledge/INDEX.md   (if a domain was touched)
- decisions/INDEX.md   (if a decision was created)
- people/INDEX.md      (if a new person was created)
- INDEX.md (root)
- hot.md               (if confirmed by the user)
- log.md
```

**Why the split**: the shared catalog files (`INDEX.md`, the sub-indexes, `hot.md`, `log.md`) are written **only by MAIN** to avoid race conditions — two parallel sub-agents editing the same INDEX would clobber each other's writes. Isolated files have a single writer each, so they are safe to parallelize. Sub-agents therefore never touch shared files; they return their cross-references as **text** for MAIN to apply in PHASE 3.

---

## PHASE 1 — Read & discuss (MAIN)

### 1.1 Read the raw
Open the file and read it in full. If it's an unreadable binary asset (PDF, image, binary `.eml`), ask the user for a manual extraction or a description.

### 1.2 Discuss with the user
Summarize the 3–5 key takeaways. Then ask:
- "Which knowledge domains does this touch?" (suggest based on content)
- "Is there a decision to extract? Or is it purely informational?"
- "New people to track?" (names not already in `people/`)
- "Update `hot.md`?" (if the insight is strategic) — default yes for articles/notes that change Active Threads or Key Recent Facts; no for purely tactical ingests.

Wait for guidance before launching the fan-out.

### 1.3 Decide which files result
Map the takeaways onto the **isolated vs. shared** taxonomy above. Count the isolated files — that count drives the fan-out decision in PHASE 2.

> **Status lifecycle**: every NEW knowledge/people/weekly/daily/plan page starts with `status: seed` in frontmatter. The lint flags it if it stays `seed` for more than 30 days. Values: `seed | developing | mature | evergreen`. Do not apply this to types with a domain-specific status (decision: active/superseded; initiative: active/paused/done; client: active/dormant/prospect).

### 1.4 Degenerate case (no wiki page)
If the raw is purely informational and yields **no** wiki page (the user says "it's just informational, don't write anything"), close **without fan-out** and append only the single `log.md` line — e.g. `… · ingest · raw/articles/{file} → ingest skipped — informational`. Skip PHASES 2–3.

---

## PHASE 2 — Fan-out (MAIN)

### Fan-out threshold
Fan-out pays off **only at 2+ isolated files**. For 0–1 isolated files, fall back to **sequential MAIN-only** writing — spawning a single sub-agent is pure overhead. So:
- **0 isolated files** → degenerate case (see 1.4), log line only.
- **1 isolated file** → MAIN writes it directly, then proceeds to PHASE 3.
- **2+ isolated files** → fan out, one sub-agent per isolated file.

### Golden rule
**One single message** with N parallel `Agent` tool calls. Never sequential.

### Sub-agent type
`subagent_type: general-purpose` (has Read/Write/Edit access).

### Self-contained briefings
Sub-agents do **not** see this `SKILL.md` or any `CLAUDE.md`. Each briefing must be self-contained: it carries the frontmatter schema, the wiki conventions, the return format, and the scope-prohibition block below. Pass only the relevant raw extract, not the whole raw file, unless the whole file is needed.

### Scope-prohibition block (paste into EVERY briefing, verbatim-style)

```
SCOPE — READ CAREFULLY:
- Touch ONLY your single target file: {target path}. Create or edit that file and nothing else.
- Do NOT touch any shared/catalog file: not INDEX.md, not any */INDEX.md sub-index,
  not hot.md, not log.md, not any other wiki page.
- If you discover a cross-reference (a wikilink to another page, an INDEX entry that should
  exist, a hot.md fact), do NOT apply it. Return it as TEXT in your final message so MAIN
  applies it in PHASE 3.
Reason: several sub-agents run in parallel. The shared files have a single writer (MAIN); if
sub-agents wrote them too, parallel writes would corrupt those files. You can't see the
orchestration SKILL.md, so this rule lives here in your briefing.
```

### Briefing template — Knowledge-entry sub-agent

```
Goal: add a titled entry to knowledge/{domain}/knowledge.md synthesizing the insight
"{insight title}" extracted from the raw {raw path}.

Target path: knowledge/{domain}/knowledge.md   ({NEW if the file doesn't exist | EXISTING — merge/append}).

Pre-step (if EXISTING): read the file first. Preserve everything. Add a new `##` section at the end.

Relevant raw extract:
---
{paste the raw lines containing the insight + minimal surrounding context — typically 20–100 lines}
---

Frontmatter schema (only if NEW file):
---
type: knowledge
domain: {domain}   # e.g. workflow, ai-workflows, {industry}, {technology}
status: seed
---

Entry to add:
## {Insight title} — from [[raw/{type}/{file}|{article or note title}]]
{2–5 lines of substantive synthesis}
- **Observed pattern**: {1–2 descriptive sentences}
- **Implications**: {1–2 sentences on how to apply it}
- **Cross-links**: {wikilinks to related knowledge/decisions/initiatives, only if they EXIST}

Wiki conventions:
- Obsidian wikilinks: `[[path/without-extension|label]]`
- Language: English
- Use literal quotes if the source states something relevant verbatim
- Add a `> [!key-insight]` callout if the insight is promotion-worthy toward rules.md

{SCOPE-PROHIBITION block here}

Return format:
- 1 line: "knowledge entry added: {domain} — {insight title}"
- Wikilinks you added (as text)
- Flag if the file is NEW (so MAIN adds it to knowledge/INDEX.md)
- The target path
```

### Briefing template — Hypothesis sub-agent (if applicable)

```
Goal: add a hypothesis to knowledge/{domain}/hypotheses.md for "{hypothesis title}" — to be
confirmed 3 times before promotion to a rule.

Target path: knowledge/{domain}/hypotheses.md   ({NEW | merge}).

Pre-step (if EXISTING): read the file first. Preserve everything. Append the new hypothesis.

Relevant raw extract:
---
{relevant lines}
---

Frontmatter schema (only if NEW):
---
type: hypothesis
domain: {domain}
status: seed
---

Entry to add:
### Hypothesis: {title}
{2–3 descriptive lines}
- **Confirmations: 1/3**
  - YYYY-MM-DD: observed in [[raw/{type}/{file}|{source title}]]
- **Anti-pattern**: {if relevant, what would contradict the hypothesis}

Wiki conventions: same as the knowledge sub-agent.

{SCOPE-PROHIBITION block here}

Return format: same as the knowledge sub-agent (one summary line, wikilinks as text, NEW flag, path).
```

### Briefing template — Decision sub-agent

```
Goal: create the decision entry decisions/YYYY-MM-DD-{slug}.md (use the raw's/ingest date)
formalizing the decision "{what was decided}".

Target path: decisions/YYYY-MM-DD-{slug}.md   (NEW — create).

Frontmatter schema:
---
type: decision
date: YYYY-MM-DD
status: active
tags: [{topic}]
---

Body (all sections required):
## Decision: {what was decided}
## Context: this decision emerged from reading/ingesting [[raw/articles/{file}|{title}]] (YYYY-MM-DD). {1–2 sentences on why the ingest triggered a decision}.
## Alternatives considered: {what else was on the table}
## Reasoning: {why this one won}
## Trade-offs accepted: {what was given up}
## Cross-impact: {which initiatives/areas this affects — as text, only if they EXIST}
## References: {wikilinks to related raw, knowledge, initiatives, only if they EXIST}

Wiki conventions:
- Obsidian wikilinks: `[[path/without-extension|label]]`
- Language: English

{SCOPE-PROHIBITION block here}

Return format:
- 1 line: "decision created: {slug}"
- The wikilink MAIN should add to decisions/INDEX.md and the root INDEX (as text)
- The target path
```

### Briefing template — Person sub-agent

```
Goal: create (or merge into) the person card people/{slug}.md for "{Full Name}".

Target path: people/{firstname-lastname}.md   ({NEW — create | EXISTING — merge}).

Pre-step (if EXISTING): read the file first. Preserve everything. Append to "Recent interactions".

Frontmatter schema (only if NEW):
---
type: person
name: {Full Name}
role: {role}
organization: {org}
last-interaction: YYYY-MM-DD
status: seed
---

Card to add (if NEW) / line to append to "## Recent interactions":
- YYYY-MM-DD — [[raw/articles/{file}|{title}]] (ingest, no direct interaction). {what the source says about the person}.

Wiki conventions:
- Obsidian wikilinks: `[[path/without-extension|label]]`
- Language: English

{SCOPE-PROHIBITION block here}

Return format:
- 1 line: "person card {created|updated}: {slug}"
- Flag if NEW (so MAIN adds it to people/INDEX.md)
- The target path
```

---

## PHASE 3 — Aggregate & finalize (MAIN, sequential)

Sub-agents only wrote their isolated files and returned cross-references as text. MAIN now writes the shared files, **in this order**.

### 3.0 Verify the fan-out
Confirm **every** sub-agent returned success before writing anything shared. If one failed, **retry only that one** (re-issue its briefing). Don't write `log.md` until all isolated files exist.

### 3.1 Sub-index updates
- **`knowledge/INDEX.md`**: if a domain was touched (add a link to the `knowledge.md` if NEW; refresh the last-touched date if you applied the pattern).
- **`decisions/INDEX.md`**: if a decision was created.
- **`people/INDEX.md`**: if a new person was created.

### 3.2 Root INDEX
`INDEX.md` — update:
- The "Recently ingested" section (articles or notes; keep only the most recent ~10–14).
- The "Cross-area decisions" section (top-5 only) if a decision deserves visibility there.

### 3.3 hot.md (optional)
If the ingest produced strategic insights or changes Active Threads / Key Recent Facts, overwrite the 5 sections of `hot.md` (~500 words). If it's purely tactical, skip it — just the log line.

Default: update `hot.md` if the user confirmed in PHASE 1.

### 3.4 log.md (append — ONE line)
`log.md` is a **lean audit trail: one line per operation**, grouped under monthly headers `## YYYY-MM`.

Append a **single line** under the current month's header (`## YYYY-MM` — create it if it doesn't exist yet). No per-entry `## [...]` header, no multi-line "files touched:" list, no multi-bullet block: summarize the key files/outcome compactly inside the one line.

```
- YYYY-MM-DD HH:MM · ingest · raw/{type}/{file} → {N knowledge + K hypotheses (+1 decision/person if any); domains touched}
```

---

## PHASE 4 — Recap to the user

Short summary in chat:
- **File read**: path
- **Files updated**: list
- **Knowledge entries created/updated**: with promotion count (1/3, 2/3, 3/3 ready)
- **Decisions**: if created, with wikilink
- **People**: if created
- **hot.md updated**: yes/no + reason
- **Suggested follow-up ingestions** (if any emerge from the content)

---

## What NOT to do

- **NEVER** modify the file in `raw/` (it's immutable by design).
- **NEVER** launch sub-agents sequentially — always one single parallel multi-call.
- **NEVER** let sub-agents write shared files (`log.md`, `INDEX.md`, the sub-indexes, `hot.md`): race condition.
- **NEVER** pass the whole raw to a sub-agent if a relevant extract is enough.
- Do not create knowledge entries if the user says "it's purely informational".
- Do not invent cross-references: only wikilink to files that EXIST (check with `ls` if unsure).
- Do not auto-update initiatives — that's the domain of `/log-meeting` or an explicit action.

---

## Operational notes on fan-out

- **When NOT to fan out**: an ingest that touches a single isolated file (e.g. just an append to `knowledge/ai-workflows/knowledge.md`) → fan-out is overhead. Fall back to the sequential MAIN-only pattern.
- **Threshold**: fan-out pays off at 2+ isolated files. 1 file → sequential MAIN. 2+ files → parallel fan-out.
- **Self-contained briefings**: sub-agents do NOT see this `SKILL.md` or any `CLAUDE.md`. The briefing MUST include the frontmatter schema, the conventions, the expected wikilinks, and the scope-prohibition block.
- **Post-fan-out verification**: confirm all sub-agents returned success before writing `log.md`. If one failed, retry only that one.
