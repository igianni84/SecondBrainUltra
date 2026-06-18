# Workflow Orchestration — SecondBrainUltra meta-layer

> This file defines **how** the LLM works inside SecondBrainUltra.
> The **what** (identity, structure, inviolable rules) is in `../CLAUDE.md` (root).

---

## 1. Plan Mode Default

- Enter **plan mode** for any non-trivial task (3+ steps or decisions that touch the wiki structure).
- If something goes sideways, **STOP and re-plan** — don't push through.
- Use plan mode for verification phases too, not just for building.
- For changes to the root `CLAUDE.md`, the wiki schema, or new macro folders: **always** plan mode.

---

## 2. Subagent Strategy

- Use subagents to keep the main context clean.
- Offload exploration, research, and parallel analysis to subagents.
- For hard problems, throw more compute via subagents.
- One task per subagent (focus).
- **Typical example**: to explore a new macro area, launch an Explore subagent instead of reading files one by one in the main context.

---

## 3. Self-Improvement Loop (lessons.md)

- After EVERY correction from the user: update `../lessons.md` with the pattern.
- Write rules for yourself that prevent the same mistake.
- At session start, read `lessons.md` to avoid repeating already-corrected mistakes.
- For accumulated domain knowledge (descriptive, not corrective), see `## Knowledge System`.

---

## 4. Verification Before Done

- Never invent names (files, people, initiatives, terminology) — always verify existence before using them.
- Never mark a task `completed` without proof it works.
  - Structural tasks: `git status` clean + structure visible via `ls`/`tree`.
  - Wiki writing: file exists, valid frontmatter, INDEX.md updated, log.md updated.
- Check question: "Would a senior peer approve this?"

---

## 5. Demand Elegance (Balanced)

- For non-trivial wiki changes: pause and ask "is there a more elegant way?"
- If a solution feels hacky: "knowing everything I know now, implement the elegant version."
- Skip this for trivial fixes — no over-engineering.
- Challenge your own work before presenting it.

---

## 6. Issue Resolution (the bug-fixing analogue)

When the user reports a block (hard decision, conflict between sources, knowledge gap):
- Don't jump to the solution. Frame the problem first.
- Search the relevant sources (PRDs, transcripts, decisions/, knowledge/).
- If data is missing, **ask** or suggest a targeted `/ingest`.
- Aim for verifiable evidence (links to transcripts, PRDs, decision entries) — not LLM opinions without support.

---

## Task Management

1. **Plan First**: for non-trivial work, write a plan (in chat or in `plans/`) with verifiable items.
2. **Verify Plan**: ask for confirmation before starting implementation.
3. **Track Progress**: use TaskCreate/TaskUpdate. Mark completed as soon as a task is really done.
4. **Explain Changes**: high-level summary at each step.
5. **Document Results**: update `log.md` with what was done.
6. **Capture Lessons**: update `lessons.md` after every correction.

---

## Core Principles

- **Simplicity First**: every change as simple as possible. Touch the minimum necessary.
- **No Laziness**: chase root causes. No temporary fixes. Senior standards.
- **Minimal Impact**: touch only what's needed.
- **Follow Project Guidelines**: respect the conventions in `../CLAUDE.md` (root).

---

## Team Memory (committed)

Memory shared with the user, lives in **`.claude/memory/`** (committed in the repo).

### When to add
- Recurring conventions that should survive the session
- References to external systems (e.g. Notion databases, Slack channels, Drive paths, ticket trackers)
- State of projects that can't be inferred from files
- Communication preferences

### How to add
1. New file `.claude/memory/{slug}.md` with frontmatter:
   ```yaml
   ---
   name: Short title
   description: One-line hook
   type: user | feedback | project | reference
   ---
   ```
2. Add a row to `.claude/memory/MEMORY.md` (the index).
3. Commit.

### Types
- **user** — facts about the user (role, expertise, preferences)
- **feedback** — "do this / don't do that" conventions (from confirmed successes too, not only corrections)
- **project** — current state of ongoing work, completed items, next up
- **reference** — pointers to where info lives (paths, external systems, line numbers)

---

## Persistence Taxonomy

Four persistence mechanisms, each with a distinct purpose:

| Mechanism | Path | Scope | Lifetime | Purpose |
|---|---|---|---|---|
| **Auto Memory** | `~/.claude/projects/.../memory/` | Personal, per-machine | Cross-session | The LLM's personal "mental model" of the user. Not shared. System-managed. |
| **Team Memory** | `.claude/memory/` (here) | Shared, committed | Cross-session | Workflow conventions, external references, project state. Visible to anyone reading the repo. |
| **Lessons** | `lessons.md` (root) | Shared, committed | Cross-session | Mistakes and corrections. Quick-reference to avoid repeating. |
| **Knowledge System** | `knowledge/{domain}/` | Shared, committed | Long-term, evolving | Domain insights with a promotion lifecycle (knowledge → hypotheses → rules). |

### When to use what

- User corrects me → `lessons.md`
- I discover a domain pattern → `knowledge/{domain}/`
- Workflow convention or external reference → `.claude/memory/`
- Personal preference of the user → Auto Memory (system-managed)

### Boundaries

- **Lesson** = mistake pattern: "don't do X, do Y." Prescriptive and immediate.
- **Knowledge entry** = observation: "X behaves like Y in this context." Descriptive, evolving.
- **Memory** = stable convention/reference; doesn't correct a mistake or describe a pattern.

---

## Knowledge System

### Before starting a task
- When relevant, re-read rules and hypotheses of the domain in `../knowledge/{domain}/`.
- Apply rules by default (confirmed patterns).
- Check if a hypothesis can be tested with today's work.

### At the end of a task
- Extract insights from what was done.
- Save them in the appropriate domain folder.

### Folder structure
Each domain: `knowledge/{domain}/`

```
knowledge/
  INDEX.md                # routing
  {domain}/
    knowledge.md          # observed facts and patterns
    hypotheses.md         # to confirm
    rules.md              # confirmed — apply by default
```

### Promotion & demotion
- Hypothesis confirmed **3 times** → promote to rule
- Rule contradicted → demote to hypothesis
- Track the count inside hypotheses:
  ```
  ### Hypothesis: X
  - Confirmations: 2/3
    - 2026-01-22: observed during meeting A
    - 2026-01-25: confirmed in call with client B
  ```

### Suggested domains
- `workflow` — patterns of your own work (interview techniques, prioritization, stakeholder management)
- `ai-workflows` — patterns of working with AI (prompting, agentic workflows, MCP usage)
- `{industry}` — business vocabulary and rules of your industry
- `{technology}` — tools and platforms your work revolves around

---

## Decision Journal

### When to log
When you choose between alternatives that impact beyond today's task — a tool, an architecture, a positioning, **or a decision NOT to do something** — log it.

### File format
File: `decisions/YYYY-MM-DD-{topic}.md`

Frontmatter:
```yaml
---
type: decision
date: YYYY-MM-DD
status: active | superseded
tags: [topic1]
---
```

Body:
```markdown
## Decision: {what you decided}
## Context: {why it came up}
## Alternatives considered: {what else was on the table}
## Reasoning: {why this one won}
## Trade-offs accepted: {what you gave up}
## References: {wikilinks to related meetings, PRDs, knowledge}
```

### Before making a similar decision
- Search `decisions/` for prior choices on the same topic.
- Follow them unless new info invalidates the reasoning.
- If you supersede a prior decision, create a new entry referencing the old one (set `status: superseded` on the old one).

---

## Conventions specific to this meta-layer

### Obsidian wikilinks
Always `[[path/without-extension|optional label]]` for internal links.
- Example: `[[knowledge/workflow/interview-techniques|Interview techniques]]`
- Files inside folders: `[[WORK/initiatives/acme-payments|ACME Payments initiative]]`

### YAML frontmatter
Mandatory on every wiki page. Minimum schema per type:
- `daily`: type, date
- `weekly`: type, date (Monday of the week), week-number
- `decision`: type, date, status, tags
- `meeting` (in `raw/meetings/` and the summary in `daily/`): type, date, attendees, source
- `person`: type, name, role, organization, last-interaction
- `initiative`: type, status (active|paused|done), owner, stakeholders, related-prd
- `client`: type, status (active|dormant|prospect), since, tags
- `knowledge`/`hypothesis`/`rule`: type, domain, confirmations (for hypothesis)

### Naming
- Dates `YYYY-MM-DD`
- Weeks `YYYY-Www` (ISO week)
- Slugs `kebab-case`, short
- People: `firstname-lastname.md` (no spaces)

### Append to log.md
`log.md` is a **lean audit trail, not a journal**. Every operation (`/daily-log`, `/ingest`, `/log-meeting`, `/log-decision`, `/lint`, `/new-initiative`, `/weekly-review`, `/end-session`) appends **exactly one line**, under the current month's header `## YYYY-MM` (create it if missing):
```
- YYYY-MM-DD HH:MM · {op} · {target} → {outcome ≤15 words}
```
The *content* of the work lives in `daily/`, `decisions/`, `people/`, `knowledge/`, etc. — `log.md` keeps only the mechanical trace (when · what · on what · outcome).

### Compaction (general rule — files distill, they don't accumulate)
Same principle as `hot.md` ("it's a cache, not a journal"). Applies to files that would otherwise grow unbounded:
- **`log.md`** keeps only the **current month**. On month rollover, `/end-session` moves concluded-month entries to `log/YYYY-MM.md` (one file per month).
- **`INDEX.md`** is a **catalog that links, not one that contains**. Chronological sections (daily, raw meetings, articles) keep only the most recent ~10–14 entries with a link + a 1-line gloss; the full history is browsed from the folder. **Never paste the full content of child files** into the index.

### Updating INDEX.md + sub-index
Every operation that creates/moves a wiki page **must** update:
1. The relevant **sub-index** (if it exists): `decisions/INDEX.md`, `people/INDEX.md`, `knowledge/INDEX.md`, `{macro-area}/initiatives/INDEX.md`.
2. `../INDEX.md` root — primary catalog that links to sub-indexes. If a root section is "Cross-area decisions" or similar, include only the top-5 most recent/relevant and link to the sub-index for the full catalog.

Pattern: **sub-index first, INDEX root after**. The root INDEX does not duplicate sub-index content.

### Runtime hooks (`.claude/settings.json`)

Three hooks automate persistent memory — executed by the runtime, not by the LLM:

- **`SessionStart`** (matcher `startup|resume`) → silent prompt: read `hot.md` if it exists. Gives the model recent context without a manual recap.
- **`PostCompact`** → after context compaction, re-read `hot.md` (hook-injected context doesn't survive compaction).
- **`Stop`** → if the wiki was modified in-session but `hot.md` isn't among the touched files, emit `HOT_CACHE_REMINDER` to the model. If `/end-session` or `/daily-log` were already executed, this is a false positive (they've already updated `hot.md`) — ignore it.

The hooks don't interfere with non-wiki sessions: the check on `hot.md` / `.git` silently fails outside the meta-layer.
