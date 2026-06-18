---
name: log-meeting
description: Process a Google Meet (or other call) transcript saved in `raw/meetings/` and extract decisions, action items, people, updating the wiki. Trigger -- user invokes `/log-meeting <path>` after dropping a transcript in `raw/meetings/`. Specialized for calls vs. generic `/ingest`. Uses a parallel fan-out (one sub-agent per isolated output file) to cut wall-clock time and keep the main context clean.
---

# /log-meeting — Process a meeting transcript (fan-out pattern)

## Purpose

Meeting transcripts are a rich source: they contain decisions made, per-person action items, and context for initiatives. This skill turns them into wiki artifacts **without burning the main context** writing files one by one. The isolated output files (a daily summary, a person page, a decision entry, an initiative update) are written by **parallel sub-agents**; the shared catalog files (sub-indexes, root `INDEX.md`, `hot.md`, `log.md`) are written by MAIN at the end.

## Input

`/log-meeting <path>` where `<path>` is a file inside `raw/meetings/`. The file is already in `YYYY-MM-DD-{topic}.md` format with raw frontmatter (`attendees`, `context`, `date`).

## Architecture (fan-out)

Four cleanly separated phases:

```
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 1 — MAIN: read + extract structured data                   │
│   - reads the raw transcript exactly once                        │
│   - extracts: participants, initiative(s), decisions, action     │
│     items, people mentioned, emerging patterns, callout candidates│
│   - decides which ISOLATED files will be written                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 2 — FAN-OUT: N parallel sub-agents (one per isolated file)  │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│   │ daily/   │ │ people/X │ │decisions/│ │initiative│  (parallel)│
│   └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
│   Each sub-agent: self-contained briefing → writes ONE file →    │
│   returns a 1-line summary + the wikilinks/cross-refs it found   │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 3 — MAIN: aggregate + write shared files (sequential)      │
│   1. touched sub-indexes (people/INDEX, decisions/INDEX, …)      │
│   2. root INDEX.md                                               │
│   3. hot.md (full overwrite, ~500 words)                         │
│   4. log.md (one-line append)                                    │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 4 — MAIN: recap to the user                                │
└──────────────────────────────────────────────────────────────────┘
```

**Why split this way**: isolated files (`daily/`, `people/X`, `decisions/Y`, `WORK/initiatives/Z`) are independent → safe to write in parallel. Catalog files (`INDEX.md`, the sub-indexes, `hot.md`, `log.md`) are *shared* → if two sub-agents wrote them concurrently they would clobber each other (a real, repeatedly-observed race condition), so MAIN writes them sequentially at the end.

---

## PHASE 1 — Read & extract (MAIN)

### 1.1 Read the raw
Open `raw/meetings/<path>` in full. If it's very long (>5000 words), that's fine — the read happens once. (Optionally delegate the first pass to an Explore sub-agent, then refine.)

### 1.2 Identify structure
From the raw's frontmatter (`attendees`, `context`, `date`) and content, extract:
- **Initiative(s)** touched — verify each against `WORK/initiatives/INDEX.md` (or the relevant macro-area's `initiatives/INDEX.md`). Do not invent slugs.
- **Participants** — verify whether each already has a page with `ls people/`.
- **Explicit decisions** (with a verbatim quote where possible).
- **Action items** (owner + description + deadline if stated).
- **NEW people** (names not in `people/`).
- **Emerging patterns** — candidates for `knowledge/{domain}/`.
- **Callout candidates** — `contradiction` / `gap` / `key-insight` inline.

### 1.3 Decide which files to write
Compile an internal plan like this:

```
ISOLATED FILES (parallelizable — one sub-agent each):
- daily/YYYY-MM-DD.md                          (create or merge)
- people/jane-doe.md                           (merge — already exists)
- people/{new-slug}.md                         (create)          [if any]
- decisions/YYYY-MM-DD-{topic-slug}.md         (create) × N
- WORK/initiatives/{slug}.md                   (merge)  × K

SHARED FILES (MAIN, at the end, sequential):
- decisions/INDEX.md          (if N > 0)
- people/INDEX.md             (if a new person was created)
- WORK/initiatives/INDEX.md   (if K > 0)
- INDEX.md (root)
- hot.md
- log.md
```

### 1.4 Controversial / strategic decisions → confirm BEFORE the fan-out
If a decision is ambiguous, contentious, or strategically heavy, **ask the user first** — before launching the sub-agents. You do not want a sub-agent to write a decision file that then has to be rewritten. Confirm the framing, then fan out. (For a big strategic decision, also consider suggesting a dedicated `/log-decision` pass for more rigor — see PHASE 4.)

---

## PHASE 2 — Fan-out (MAIN)

### Golden rule
**Launch all sub-agents in a SINGLE message** (one message containing N parallel `Agent` tool calls). Never sequentially.

### Sub-agent type
Always use `subagent_type: general-purpose` (it has Read/Write/Edit/Bash). Each sub-agent owns **exactly one** target file.

### ⛔ Scope-prohibition block (MANDATORY — it is a required section of EVERY briefing)

Every sub-agent is `general-purpose`: if it is not explicitly constrained, it will **expand its own scope** and edit shared/index files → race condition and corrupted catalogs. This is not hypothetical — it is the single most repeatedly-observed failure mode of this skill (see `lessons.md`): parallel sub-agents racing on `INDEX.md` / `hot.md` / `log.md` and overwriting each other's work. Knowing this rule "at the skill level" is **not enough**, because the sub-agent never sees this `SKILL.md` or any `CLAUDE.md`. Therefore you must **paste the block below VERBATIM into every briefing**, right before the "Return format" section:

> **SCOPE CONSTRAINTS (non-negotiable)**: Do NOT create or modify ANY file other than the single `Target path` named above. In particular, NEVER touch `INDEX.md`, `decisions/INDEX.md`, `people/INDEX.md`, `WORK/initiatives/INDEX.md` (or any macro-area `initiatives/INDEX.md`), `hot.md`, or `log.md`, and NEVER touch any other person / decision / initiative file. If you discover cross-references that other files should carry, **do NOT apply them** — return them as plain text under the "Cross-references" section of your return, and MAIN will apply them in PHASE 3.

### Briefing template — every briefing has these 7 sections, in order
1. **Goal** — what this sub-agent must produce (its one file).
2. **Raw extract** — ONLY the transcript lines that matter for this file (verbatim quotes, no paraphrase). The sub-agent must NOT read the whole transcript.
3. **Target path** — the repo-relative path + whether it already exists or must be created.
4. **Schema** — the complete frontmatter to use/preserve + the expected section structure.
5. **Wiki conventions** — wikilinks, callouts, English, kebab-case.
6. **Scope constraints** — the ⛔ block above, VERBATIM. NOT optional (it is the root cause of the near-misses in `lessons.md`).
7. **Return format** — what to hand back to MAIN (always include "Cross-references to apply: [list]", which MAIN applies in PHASE 3).

> Paths in briefings are repo-relative (e.g. `decisions/...`, `people/...`). If a sub-agent needs an absolute base, give it `${CLAUDE_PROJECT_DIR}` — never a machine-specific path.

### Briefing template — Decision sub-agent (NEW file)

```
Goal: create decisions/YYYY-MM-DD-{topic-slug}.md for the decision "{decision title}" that emerged in the meeting "{meeting title}".

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
{transcript lines where the person speaks or is introduced + any context from the raw frontmatter}
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

Relevant raw extract:
---
{the whole transcript if <2000 lines, otherwise an executive summary + the relevant sections}
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

## PHASE 3 — Aggregate & finalize (MAIN, sequential)

After ALL sub-agents complete, collect their returns and proceed.

### 3.0 Verify the fan-out before touching shared files
Before writing anything shared (especially `log.md`), confirm **every** sub-agent returned success. If one failed, **retry only the failed sub-agent** (re-send its briefing — do NOT relaunch the others, their files are already written). Only continue once all returns are green.

### 3.1 Sub-index updates
Apply the cross-references the sub-agents returned as text, then update each touched sub-index, in order:

- **`decisions/INDEX.md`** (if N new decisions): add a row in the appropriate topic section's table (the sections reflect the user's own topic clusters — see the file). If a decision supersedes an older one, flip the old row to `superseded`.
- **`people/INDEX.md`** (if a new person was created): add to the relevant section.
- **`WORK/initiatives/INDEX.md`** (if an initiative was touched): update `last-updated` in the table + any status change.
- **`knowledge/INDEX.md`** (rare from a meeting): only if you promoted a pattern.

### 3.2 Root INDEX
Update `INDEX.md` (root):
- "Recent raw meetings" section: add an entry with a 1-2 line synthesis + links to the extracted decisions.
- "Decisions" section (top recent only): if a new decision deserves top-level visibility, include it and push one less important down.
- Daily section, if you created a new daily.

### 3.3 hot.md (full overwrite, ~500 words)
A meeting is almost ALWAYS a trigger to update `hot.md`. Overwrite it completely (it's a cache, not a journal), keeping its frontmatter:

```yaml
---
type: meta
description: Hot cache — recent-context digest (~500 words)
updated: YYYY-MM-DD
---
```

Body, 4-5 sections:
1. **Last Updated** — 1 line: date + tagline.
2. **Key Recent Facts** — 3-5 strategic bullets with wikilinks.
3. **Recent Changes** — created / updated.
4. **Active Threads** — action-item rollover + next steps.
5. **Open Patterns / Hypotheses** — patterns that emerged + prior rollovers.

### 3.4 log.md (one-line append)
`log.md` holds **only the current month**. Append **exactly ONE line** under the current month header `## YYYY-MM` (create the header if it's missing). No per-entry header, no multi-line block, no "files touched:" line — the key files/outcome are summarized compactly inside the single line.

```
- YYYY-MM-DD HH:MM · log-meeting · raw/meetings/{file} → {outcome ≤15 words}
```

Example:
```
- 2026-01-15 16:46 · log-meeting · raw/meetings/2026-01-15-acme-kickoff → 1 dec, +marcus-chen, jane-doe updated, acme-payments-rewrite
```

---

## PHASE 4 — Recap to the user

Short summary in chat:
- **Decisions created** (wikilink + 1 sentence each)
- **Initiatives updated** (what changed)
- **People**: created / updated
- **hot.md updated**: yes
- **Emerging patterns** (knowledge candidates): list + promotion status (1/3, 2/3, 3/3 ready)
- **Inline callouts applied**: contradiction / gap / key-insight, if any
- **Suggestion**: "want me to open a `/log-decision` proposal for X?" if a big strategic decision deserves more rigor.

---

## Fan-out: cost / benefit

- **Token cost**: the fan-out raises total tokens by ~20-30% (extra round-trips + briefing setup) but cuts the main context by ~70-80% and wall-clock time by ~3-4×.
- **When NOT to fan out**: a trivial meeting (<15 min, exactly 1 decision, 0 new people) touches a single file — the fan-out is pure overhead. Handle it sequentially in MAIN.
- **Self-contained briefings**: sub-agents do NOT see this `SKILL.md` or any `CLAUDE.md`. MAIN's briefing MUST carry the schema, conventions, expected wikilinks, and the ⛔ scope-constraints block.
- **Post-fan-out verification**: see 3.0 — confirm all returns are green before writing `log.md`; retry only failed sub-agents.

---

## What NOT to do

- **NEVER** modify the raw transcript.
- **NEVER** launch sub-agents sequentially — always a single message with parallel calls.
- **NEVER** let a sub-agent write a shared file (`log.md`, `INDEX.md`, any sub-index, `hot.md`): race condition. This is why the ⛔ scope-constraints block is pasted verbatim into every briefing.
- **NEVER** pass the whole transcript to a sub-agent when an extract suffices — it wastes the context saving.
- Do not invent action items — only those actually said.
- Do not assign arbitrary deadlines if none were mentioned.
- For controversial / ambiguous decisions: confirm with the user BEFORE the fan-out, not after a sub-agent has already written a decision file.
- Do not auto-create initiatives: if a new one emerges, suggest `/new-initiative` but don't run it without confirmation.
- Do not invent cross-references: only wikilink files that EXIST (verify with `ls` if unsure).
- Do not crystallize an ambiguous name — flag inline with `_(to confirm)_` and ask the user.
