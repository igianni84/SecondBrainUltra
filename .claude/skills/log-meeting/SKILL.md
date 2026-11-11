---
name: log-meeting
description: Process a Google Meet (or other call) transcript saved in `raw/meetings/` and extract decisions, action items, people, updating the wiki. Trigger -- user invokes `/log-meeting <path>` after dropping a transcript in `raw/meetings/`. Specialized for calls vs. generic `/ingest`. Uses a parallel fan-out (one sub-agent per isolated output file) to cut wall-clock time and keep the main context clean.
---

# /log-meeting — Process a meeting transcript (fan-out pattern)

## Purpose

From a transcript in `raw/meetings/` this skill extracts decisions, action items and people, and updates the daily, the pages and the indexes. The transcript stays as it is: `raw/` is read-only.

Four phases: MAIN reads and extracts; parallel sub-agents write the isolated files (daily, people, decisions, initiatives); MAIN writes the shared files (indexes, `hot.md`, `log.md`), which two concurrent writers would clobber; MAIN recaps.

## Input

`/log-meeting <path>` where `<path>` is a file inside `raw/meetings/`, saved as the recording tool exported it: same file name, no frontmatter. Date, title and attendees come from the transcript's header.

---

## PHASE 1 — Read & extract (MAIN)

### 1.1 Read the raw
In full, once.

### 1.2 Extract
- **Initiative(s)** touched — verify each against `WORK/initiatives/INDEX.md` (or the relevant macro area's `initiatives/INDEX.md`).
- **Participants** — check each for a page with `ls people/`. Before writing any name heard in the transcript, grep its stem (e.g. `marc` for Marcus) in `people/`, `aliases` included, and in the macro area's `CLAUDE.md`. A name found only in transcripts is a speech-to-text mangling: the mangled form goes into the `aliases` of the right card. A name that stays ambiguous is flagged inline with `_(to confirm)_` and asked to the user.
- **Explicit decisions** (with a verbatim quote where possible).
- **Action items**: owner, what, deadline only if it was stated.
- **NEW people** (names not in `people/`).
- **Emerging patterns** — candidates for `knowledge/{domain}/`.
- **Callout candidates** — `contradiction` / `gap` / `key-insight` inline.

Only what was said goes in: no inferred action items, no estimated deadlines.

### 1.3 Decide which files to write

```
ISOLATED FILES (one sub-agent each):
- daily/YYYY-MM-DD.md                     (create or merge)
- people/{slug}.md                        (merge if it exists, create if new)
- decisions/YYYY-MM-DD-{slug}.md          (create) × N
- WORK/initiatives/{slug}.md              (merge)  × K

SHARED FILES (MAIN, at the end, sequential):
- decisions/INDEX.md, people/INDEX.md, WORK/initiatives/INDEX.md — the ones touched
- INDEX.md (root)
- hot.md
- log.md
```

A decision's slug has at most 6 words (`decisions/README.md`): the topic, not the sentence. The full sentence is the file's `#` title.

With a single isolated file — a short call, one decision, no new people — MAIN writes it directly, without sub-agents. If a new workstream emerges, propose `/new-initiative` and wait for a yes.

### 1.4 Controversial / strategic decisions → confirm BEFORE the fan-out
An ambiguous, contentious or strategically heavy decision is confirmed with the user first: afterwards the file would already be written.

---

## PHASE 2 — Fan-out (MAIN)

Launch all sub-agents in **a single message** with N parallel `Agent` tool calls, `subagent_type: general-purpose`. Each owns exactly one target file. A sub-agent sees neither this `SKILL.md` nor any `CLAUDE.md`: its briefing carries the schema, the conventions and the expected wikilinks. Pass it only the transcript lines it needs, as verbatim quotes.

### ⛔ Scope-prohibition block (a required section of EVERY briefing)

Paste it verbatim into every briefing, right before the "Return format" section. An unconstrained sub-agent expands its scope to the shared files, and parallel writes to `INDEX.md`, `hot.md` or `log.md` overwrite each other: it is the most repeatedly observed failure of this skill.

> **SCOPE CONSTRAINTS (non-negotiable)**: Do NOT create or modify ANY file other than the single `Target path` named above. In particular, NEVER touch `INDEX.md`, `decisions/INDEX.md`, `people/INDEX.md`, `WORK/initiatives/INDEX.md` (or any macro-area `initiatives/INDEX.md`), `hot.md`, or `log.md`, and NEVER touch any other person / decision / initiative file. If you discover cross-references that other files should carry, **do NOT apply them** — return them as plain text under the "Cross-references" section of your return, and MAIN will apply them in PHASE 3.

### The 7 sections of a briefing, in order
1. **Goal** — what this sub-agent must produce (its one file).
2. **Raw extract** — only the transcript lines that matter for this file.
3. **Target path** — the repo-relative path + whether it already exists or must be created.
4. **Schema** — the complete frontmatter to use/preserve + the expected section structure.
5. **Wiki conventions** — wikilinks, callouts, English, kebab-case.
6. **Scope constraints** — the ⛔ block above.
7. **Return format** — always with "Cross-references to apply: [list]", which MAIN applies in PHASE 3.

> Paths in briefings are repo-relative (e.g. `decisions/...`, `people/...`). If a sub-agent needs an absolute base, give it `${CLAUDE_PROJECT_DIR}` — never a machine-specific path.

### Briefing template — Decision sub-agent (NEW file)

```
Goal: create decisions/YYYY-MM-DD-{slug}.md for the decision "{decision title}" that emerged in the meeting "{meeting title}".

Target path: decisions/YYYY-MM-DD-{slug}.md (NEW — does not exist).

Relevant raw extract (from the transcript raw/meetings/{file}):
---
{paste ONLY the transcript lines where this decision is discussed, including verbatim participant quotes — ~30-100 lines max}
---

Expected frontmatter:
---
type: decision
date: YYYY-MM-DD
status: active
tags: [tag1, tag2, ...]      # 5-10 relevant tags
context: {macro-area-slug or 'meta'}
supersedes: []
superseded-by: []
---

Section structure (follow decisions/README.md exactly):
# {Decision title — what you decided, 1 line}
## Decision            — what you decided, 1-2 crisp sentences
## Context             — why it arose, the problem/trigger
## Alternatives considered  — Alternative A / B / C, each with "Why rejected"
## Reasoning           — why this option won (the binding constraint / trade-off that mattered)
## Trade-offs accepted — what you gave up; be honest
## References          — meeting wikilink + related decisions + initiative + people

Conventions:
- Obsidian wikilinks: [[path/without-extension|optional label]]. Examples:
  - [[raw/meetings/{meeting-file}|{meeting title}]]
  - [[decisions/YYYY-MM-DD-other-decision]]
  - [[WORK/initiatives/{slug}]]
  - [[people/{person-slug}|Name]]
- Language: English.
- Verbatim quotes in italics: *"..."* (Jane 44:53).
- Add a `> [!key-insight]` callout if the decision carries a promotion-worthy takeaway.

MANDATORY wikilinks to include:
- the source meeting: [[raw/meetings/{meeting-file}|{meeting title}]]
- the relevant initiative: [[WORK/initiatives/{slug}]]
- the key stakeholders: [[people/{person-slug}]]
{any other wikilinks known from the context}

[PASTE THE ⛔ SCOPE-CONSTRAINTS BLOCK HERE, VERBATIM]

Return format (hand back exactly this):
- 1-line summary: "decision created: {slug} — {one sentence}"
- Wikilinks created in the file: [list]
- Cross-references to apply: [decisions / initiatives / people that should be reciprocally updated — as TEXT, do not apply them]
- File path written: decisions/YYYY-MM-DD-{slug}.md
```

### Briefing template — Person sub-agent (MERGE an existing page)

```
Goal: update people/{slug}.md by adding the {date} interaction for the meeting "{meeting title}".

Target path: people/{slug}.md (EXISTING — MERGE, do NOT overwrite).

MANDATORY first step: read the existing file IN FULL before changing anything. You must preserve the frontmatter, the section structure, and every prior interaction. MERGE, never replace.

Relevant raw extract:
---
{paste ONLY the transcript lines where {person} speaks or is mentioned substantively — ~20-50 lines}
---

Updates to make:
1. Frontmatter:
   - `last-interaction:` → set to {date}
   - `tags:` → add 1-3 tags relevant to this meeting (e.g. {tag1, tag2}). KEEP all existing tags.

2. Section `## Interactions log`:
   - Add ONE new entry AT THE TOP (newest first), format:
     - YYYY-MM-DD: [[raw/meetings/{meeting-file}|{meeting title}]] — {1-3 sentence synthesis of {person}'s contribution + decisions crystallized, with wikilinks + verbatim quotes if relevant}
   - Do NOT touch the prior entries.

3. If an operational change emerges (new role, new focus, new responsibility), also update `## Role & context` and/or `## Preferences / style` (append, do not overwrite).

Conventions:
- Wikilinks: [[raw/meetings/{file}|{label}]], [[decisions/{slug}]], [[WORK/initiatives/{slug}]]
- Verbatim quotes: *"..."* (Name HH:MM)
- Language: English.
- If a decision this person pushed/owned was crystallized, link it explicitly.
- If a leadership/communication pattern worth tracking emerges, note it briefly in the interaction entry.
- If a name is uncertain, flag it inline with `_(to confirm)_` — do NOT crystallize an ambiguous name.

[PASTE THE ⛔ SCOPE-CONSTRAINTS BLOCK HERE, VERBATIM]

Return format:
- 1 line: "person updated: {slug} — {date} entry added"
- Wikilinks added: [list]
- Cross-references to apply: [list — as TEXT]
- File path: people/{slug}.md
```

### Briefing template — Person sub-agent (NEW page)

```
Goal: create people/{firstname-lastname}.md for {Full Name}, a new person mentioned in the meeting "{meeting title}".

Target path: people/{firstname-lastname}.md (NEW). kebab-case, no spaces, no accents.

Relevant raw extract:
---
{transcript lines where the person speaks or is introduced + any context from the transcript header}
---

Frontmatter:
---
type: person
name: {Full Name}
role: {role if known, otherwise "to confirm"}
organization: {org slug or name}
last-interaction: YYYY-MM-DD
tags: [{initial tags, max 3}]
status: active
aliases: [{nicknames/handles if any}]
---

Section structure (follow people/README.md):
# {Full Name}
## Role & context     — who they are, their org, why they're relevant
## Background         — what we know (may be brief for a new page)
## Preferences / style — communication style if observed, else "to confirm from future meetings"
## Interactions log
  - {today's meeting entry}
## Flags / caveats    — sensitivities / conflicts / confidentiality, if any
## Links              — LinkedIn / writing / internal wikilinks, if known

Conventions: same as the Person MERGE briefing (wikilinks, English, verbatim quotes, `_(to confirm)_` for uncertain names).

[PASTE THE ⛔ SCOPE-CONSTRAINTS BLOCK HERE, VERBATIM]

Return format:
- 1 line: "person created: {slug} — {role} @ {org}"
- File path: people/{slug}.md
- Wikilinks added: [list]
- FLAG for MAIN: "person NEW — add to people/INDEX.md under section {appropriate section}"
```

### Briefing template — Daily sub-agent

```
Goal: {create | update} daily/YYYY-MM-DD.md, adding the meeting "{meeting title}" under "## Meetings / relevant interactions".

Target path: daily/YYYY-MM-DD.md ({NEW | EXISTING — MERGE}).

First step (if it exists): read the file IN FULL. Preserve everything. Add under "## Meetings / relevant interactions". If decisions were crystallized, also add them under "## Decisions taken".

Frontmatter (if NEW):
---
type: daily
date: YYYY-MM-DD
context: {macro-area-slug or 'mixed'}
session-tag: {short session identifier, optional}
---

Meeting extract:
---
{the structured summary from PHASE 1: topics, decisions, action items with owners, and the quotes to carry over}
---

What to add under "## Meetings / relevant interactions":
- [[raw/meetings/{meeting-file}|{meeting title}]] — {3-5 sentence high-density synthesis}. Main topics: {Topic 1: 1-2 sentences + quote if relevant}; {Topic 2: ...}. Action items (N total): {Owner 1 (count): list}; {Owner 2 (count): list}. The {N decisions} + action items touch: [[WORK/initiatives/{slug1}]], [[WORK/initiatives/{slug2}]].

Decisions to add under "## Decisions taken" (if the daily is NEW or the section is missing):
- [[decisions/YYYY-MM-DD-{slug}|{decision title}]] — {one-sentence recap}

Patterns to add under "## Learnings" (if NEW or the section is missing):
- **{Pattern title}** ({X}/3 observation, candidate `knowledge/{domain}`). {2-3 sentences}.

Conventions: Obsidian wikilinks, English, verbatim quotes *"..."* with (Name HH:MM).

[PASTE THE ⛔ SCOPE-CONSTRAINTS BLOCK HERE, VERBATIM]

Return format:
- 1 line: "daily updated: YYYY-MM-DD — meeting section + N decisions + K patterns"
- Wikilinks added: [list]
- File path: daily/YYYY-MM-DD.md
```

### Briefing template — Initiative sub-agent (MERGE)

```
Goal: update WORK/initiatives/{slug}.md to reflect the action items, decisions, and changes from the meeting "{meeting title}".

Target path: WORK/initiatives/{slug}.md (EXISTING — MERGE).

MANDATORY first step: read the file IN FULL before changing anything. Preserve everything; update surgically. MERGE, never overwrite.

Relevant raw extract (filtered to this initiative {slug}):
---
{paste the transcript lines that touch this specific initiative — typically 30-100 lines}
---

Updates to make:
1. Frontmatter:
   - `last-updated:` → {date}
   - `tags:` → add relevant tags (KEEP existing).
   - `status:` → change ONLY if the meeting explicitly changed it (active → paused/done). Otherwise leave it.

2. Section `## Timeline`: add an entry at the appropriate position with:
   - YYYY-MM-DD: {what happened — decisions crystallized, action items, patterns}. Decisions: [[decisions/YYYY-MM-DD-{slug}]]. Meeting: [[raw/meetings/{meeting-file}|{meeting title}]].

3. Section `## Current state`: update to reflect where the initiative stands after this meeting.

4. Section `## Next steps`: add the new action items; mark completed ones done (`[x]`).

5. Section `## Blockers`: if new blockers/risks emerged, add them.

Conventions: wikilinks, English, verbatim quotes *"..."*.

[PASTE THE ⛔ SCOPE-CONSTRAINTS BLOCK HERE, VERBATIM]

Return format:
- 1 line: "initiative updated: {slug} — {one sentence}"
- Wikilinks added: [list]
- Cross-references to apply: [list — as TEXT]
- File path: WORK/initiatives/{slug}.md
```

---

## PHASE 3 — Shared files (MAIN, sequential)

Starts when **every** sub-agent has returned success. If one failed, retry only that one: the others' files are already written. Wikilinks go only to files that exist (`ls` when unsure).

### 3.1 Sub-index updates
Apply the cross-references the sub-agents returned as text, then update each touched sub-index:

- **`decisions/INDEX.md`**, for each new decision: a row at the top of the right topic section's table, with a short title as the label. If a decision supersedes an older one, flip the old row to `superseded`.
- **`people/INDEX.md`**: a new person gets a row in the relevant section; for a person already listed, update the `Last interaction` date.
- **`WORK/initiatives/INDEX.md`**, for each initiative touched: update the row, plus any status change. The last cell is a pointer — the status and, at most, the latest source with one sentence, 30 words in all. It is replaced, never appended to: the history is in the page the sub-agent just wrote.
- **`knowledge/INDEX.md`**: only if you promoted a pattern.

### 3.2 Root INDEX
`INDEX.md` (root):
- "Recent raw meetings": the new entry on top, with a 1-line gloss + links to the extracted decisions.
- "Decisions": only if a new decision belongs among the 5 shown there. One comes in, one goes out.
- "Daily logs", if the daily is new.

Done when `bash .claude/hooks/check-index-caps.sh` prints nothing: it measures the caps of every index touched, and what it reports gets fixed before PHASE 3 closes.

### 3.3 hot.md
Overwrite `hot.md` following `CLAUDE.md` §4bis: the meeting's facts go in place of the oldest ones, and emerging patterns are written to `knowledge/{domain}/hypotheses.md`, with only the link here. In the frontmatter only `updated:` changes, and it holds only the date.

Done when `wc -w hot.md` gives at most 700. If everything is needed, go over and tell the user how many words and why.

### 3.4 log.md
Exactly one line under the current month header `## YYYY-MM` (create it if missing), with the time from `date +%H:%M`:

```
- YYYY-MM-DD HH:MM · log-meeting · raw/meetings/{file} → {outcome ≤15 words}
```

The line counts what the meeting produced; quotes and positions live in the daily and in the decisions. Example:
```
- 2026-01-15 16:46 · log-meeting · raw/meetings/2026-01-15-acme-kickoff → 1 dec, +marcus-chen, jane-doe updated, acme-payments-rewrite
```

---

## PHASE 4 — Recap to the user

- **Decisions created** (wikilink + 1 sentence each)
- **Initiatives updated** (what changed)
- **People**: created / updated, with the names and roles to confirm
- **Emerging patterns** (knowledge candidates): list + promotion status (1/3, 2/3, 3/3 ready)
- **Inline callouts applied**: contradiction / gap / key-insight, if any
- A big strategic decision that deserves more rigor: propose a `/log-decision` pass.
