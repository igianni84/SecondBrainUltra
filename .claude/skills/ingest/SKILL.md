---
name: ingest
description: Process a file in `raw/` (article, note, screenshot, transcript) and extract its value into the wiki -- summary, cross-reference, INDEX, log. Trigger -- user invokes `/ingest <path>` after dropping a file in `raw/articles/`, `raw/notes/`, or `raw/assets/`. For Meet transcripts use `/log-meeting` instead. Uses a fan-out pattern (parallel sub-agents on isolated files) to cut wall-clock time and keep the main context clean.
---

# /ingest — Process a raw asset into the wiki (fan-out pattern)

## Purpose

`/ingest` reads a file in `raw/articles/`, `raw/notes/` or `raw/assets/`, brings its useful content into the wiki (`knowledge/`, and `decisions/` or `people/` when relevant) and updates the indexes. The file in `raw/` stays as it is: that layer is read-only. For `raw/meetings/` use `/log-meeting`.

Four phases: MAIN reads and proposes; sub-agents write the isolated files in parallel; MAIN writes the shared files; MAIN recaps.

```
ISOLATED files (one sub-agent each):
- knowledge/{domain}/knowledge.md   (merge — append a titled entry)   — almost always
- knowledge/{domain}/hypotheses.md  (merge — if there's an insight to confirm)
- decisions/YYYY-MM-DD-{slug}.md    (create — if the user decides something; slug of at most 6 words)
- people/{slug}.md                  (create — if a new relevant person appears)

SHARED files (MAIN only, at the end, sequential):
- knowledge/INDEX.md, decisions/INDEX.md, people/INDEX.md — the ones touched
- INDEX.md (root)
- hot.md               (if confirmed by the user)
- log.md
```

Isolated files have one writer each, so they are safe in parallel. The shared files have a single writer, MAIN: two sub-agents editing the same index would clobber each other.

---

## PHASE 1 — Read & propose (MAIN)

### 1.1 Read the raw
Open the file and read it in full. PDFs and images are read with the Read tool, a long PDF in page ranges. Ask the user only if the file can't be opened.

### 1.2 Propose the plan
Summarize the 3–5 key takeaways and, below them, the plan you propose:
- the knowledge domains touched
- whether there is a decision to extract, or it's purely informational
- new people, i.e. names with no page in `people/`
- whether `hot.md` changes: yes when the ingest touches *Active Threads* or *Key Recent Facts*

The user confirms or corrects in one round; then the fan-out starts.

### 1.3 Count the isolated files
Map the takeaways onto the taxonomy above. The count drives PHASE 2:
- **0** — the user says it's purely informational: skip PHASES 2–3 and append only the `log.md` line (`… → ingest skipped — informational`).
- **1** — MAIN writes it directly, then PHASE 3.
- **2+** — fan out, one sub-agent per file.

> **Status lifecycle**: every NEW knowledge/weekly/daily/plan page starts with `status: seed` in frontmatter. The lint flags it if it stays `seed` for more than 30 days. Values: `seed | developing | mature | evergreen`. Types with a domain-specific status keep theirs (decision: active/superseded; initiative: active/paused/done; client: active/dormant/prospect; person: active/dormant/archived).

---

## PHASE 2 — Fan-out (MAIN)

Launch all sub-agents in **one single message** with N parallel `Agent` tool calls, `subagent_type: general-purpose`. A sub-agent sees neither this `SKILL.md` nor any `CLAUDE.md`: its briefing carries the frontmatter schema, the wiki conventions, the return format and the scope block. Pass it the relevant extract of the raw, not the whole file.

### Scope-prohibition block (paste into EVERY briefing)

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

### Briefing template — Hypothesis sub-agent

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
- Confirmations: 1/3
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
tags: [{topic1}, {topic2}]
context: {macro-area-slug or 'meta'}
supersedes: []
superseded-by: []
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

Pre-step (if EXISTING): read the file first. Preserve everything. Append to "Interactions log".

Frontmatter schema (only if NEW):
---
type: person
name: {Full Name}
role: {role}
organization: {org}
last-interaction: YYYY-MM-DD
status: active
---

Card to add (if NEW) / line to append to "## Interactions log":
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

## PHASE 3 — Shared files (MAIN, sequential)

Starts when **every** sub-agent has returned success. If one failed, retry only that one. Wikilinks go only to files that exist (`ls` when unsure).

### 3.1 Sub-index updates
- **`knowledge/INDEX.md`**: the link to the `knowledge.md`, if the file is new.
- **`decisions/INDEX.md`**: the row of the decision, if one was created.
- **`people/INDEX.md`**: the row of the new person.

### 3.2 Root INDEX
`INDEX.md`:
- "Recently ingested": the new entry on top with a 1-line gloss. The section keeps the latest 14: the oldest leaves whole.
- "Decisions": only if the decision belongs among the 5 shown there.

Done when `bash .claude/hooks/check-index-caps.sh` prints nothing: it measures the caps, and what it reports gets fixed before the step closes.

### 3.3 hot.md
Only if confirmed in PHASE 1: the new fact enters in place of an older one, following `CLAUDE.md` §4bis. Done when `wc -w hot.md` gives at most 700; if everything is needed, go over and tell the user how many words and why.

### 3.4 log.md
One line under the current month's header `## YYYY-MM` (create it if missing), with the time from `date +%H:%M`:

```
- YYYY-MM-DD HH:MM · ingest · raw/{type}/{file} → {N knowledge + K hypotheses (+1 decision/person if any); domains touched — ≤15 words}
```

---

## PHASE 4 — Recap to the user

- **File read** and **files updated**
- **Knowledge entries and hypotheses**, with the confirmation count (1/3, 2/3, 3/3 ready)
- **Decisions** and **people** created, with wikilinks
- **hot.md**: updated or not, and why
- **Suggested follow-up ingestions**, if the content points to any

Initiatives are updated by `/log-meeting` or on an explicit request, not by an ingest.
