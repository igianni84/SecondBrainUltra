---
name: ingest
description: Process a file in `raw/` (article, note, screenshot, transcript) and extract its value into the wiki -- summary, cross-reference, INDEX, log. Trigger -- user invokes `/ingest <path>` after dropping a file in `raw/articles/`, `raw/notes/`, or `raw/assets/`. For Meet transcripts use `/log-meeting` instead.
---

# /ingest — Process a raw asset into the wiki

## Purpose

The `raw/` layer is immutable. `/ingest` reads a file in `raw/`, extracts useful content, integrates it into the wiki (`knowledge/`, `decisions/`, `people/` as relevant), and updates indexes.

## Input

`/ingest <path>` where `<path>` is a file inside `raw/articles/`, `raw/notes/`, or `raw/assets/`.

For `raw/meetings/`, use `/log-meeting` instead (it has dedicated logic).

## Workflow

### Step 1 — Read the raw
Open the file fully. If it's an unreadable binary asset (PDF, image), ask the user for a manual extraction or description.

### Step 2 — Discuss with the user
Summarize the 3–5 key takeaways. Ask:
- "Which knowledge domains does this touch?" (suggest based on content)
- "Is there a decision to extract? Or is it purely informational?"
- "New people to track?" (names not already in `people/`)

Wait for guidance before writing.

### Step 3 — Update wiki targets

For each target confirmed by the user:

**A. Summary in `knowledge/{domain}/`**
- If `knowledge.md` doesn't exist for the domain, create it with frontmatter (include `status: seed` for a new page).
- Add a titled entry, citing the raw via wikilink:
  ```markdown
  ## {Insight title} — from [[raw/articles/{file}|{article title}]]
  {2–5 lines of synthesis}
  - Implications: ...
  ```

**B. Possible `hypotheses.md` entry** (if the insight looks like a rule to confirm) — frontmatter with `status: seed`

**C. Possible `decisions/` entry** (if the user decides something based on this)

**D. Possible new `people/{slug}.md`** (see `people/README.md` for criteria) — frontmatter with `status: seed`

> **Status lifecycle**: every NEW knowledge/people/weekly/daily/plan page starts with `status: seed` in frontmatter. The lint will flag it if it stays `seed` for more than 30 days. Values: `seed | developing | mature | evergreen`. Do not apply to types with domain-specific status (decision: active/superseded; initiative: active/paused/done; client: active/dormant/prospect).

### Step 4 — Update INDEX + sub-index
Add entries in the following indexes, **in order**:
- `INDEX.md` (root) — "Recently ingested" section
- `knowledge/INDEX.md` if you touched a domain
- `people/INDEX.md` if you created a new person
- `decisions/INDEX.md` if you created a new decision (appropriate section by topic cluster — the user decides what sections fit their domains)

Pattern: **specific sub-index first, INDEX root after**. The root INDEX links to sub-indexes, it doesn't duplicate their content.

### Step 5 — Update `hot.md`
If the ingest produced strategic insights or information that changes "Key Recent Facts" or "Active Threads", update `hot.md` (complete overwrite, ~500 words). If the ingest is purely tactical (e.g. informational article without operational impact), you can skip this step.

### Step 6 — Append to log.md
```markdown
## [YYYY-MM-DD HH:MM] ingest | raw/{type}/{file}
- {1 bullet: what was extracted and where it landed}
- files touched: `raw/{type}/{file}`, `knowledge/.../...`, `INDEX.md`, `hot.md` (if updated)
```

### Step 7 — Summary
Show the user: file read, files updated (including hot.md if updated), suggested follow-up ingestions (if any emerge).

## What NOT to do

- **NEVER** modify the file in `raw/` (it's immutable by design).
- Do not create knowledge entries if the user says "it's purely informational".
- Do not invent cross-references: only wikilink to files that EXIST.
- Do not auto-update initiatives — that's the domain of `/log-meeting` or an explicit action.
