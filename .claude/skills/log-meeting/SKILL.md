---
name: log-meeting
description: Process a Google Meet (or other call) transcript saved in `raw/meetings/` and extract decisions, action items, people, updating the wiki. Trigger -- user invokes `/log-meeting <path>` after dropping a transcript in `raw/meetings/`. Specialized for calls vs. generic `/ingest`.
---

# /log-meeting — Process a meeting transcript

## Purpose

Meeting transcripts are a rich source: they contain decisions made, per-person action items, context for initiatives. This skill turns them into wiki artifacts.

## Input

`/log-meeting <path>` where `<path>` is a file inside `raw/meetings/`. The file is already in `YYYY-MM-DD-{topic}.md` format with raw frontmatter.

## Workflow

### Step 1 — Read the transcript
Open the file completely. If very long (>5000 words), consider delegating to a subagent (Explore) for initial extraction, then refine.

### Step 2 — Identify the context
From the raw's frontmatter (`context: {macro-area} | mixed | ...`) and content, identify:
- Which **initiative** the meeting belongs to (if any)
- Who the participants are (`attendees:` list from frontmatter)
- Any new external stakeholders

### Step 3 — Extract by category

**A. Decisions**
For each explicit or implicit decision in the meeting:
- Create `decisions/YYYY-MM-DD-{topic-slug}.md` (date of the meeting)
- Frontmatter `type: decision`, link to the raw meeting
- Body following the standard template in `decisions/README.md`

**B. Action items**
For each action item:
- Identify owner (person) and deadline (if mentioned)
- Add to the relevant initiative card in `{macro-area}/initiatives/{slug}.md` under `## Next steps`
- If it's the user's action and not tied to an initiative, also put it in the `daily/YYYY-MM-DD.md` for that date

**C. New people**
If names not in `people/` come up:
- Ask the user whether they're worth tracking (criteria in `people/README.md`)
- If yes: create `people/{firstname-lastname}.md` with a basic card + reference to the meeting + frontmatter `status: seed`

**D. Insights / knowledge**
If domain patterns emerge in the meeting (rules, anti-patterns, learnings):
- Consider an entry in `knowledge/{domain}/` with frontmatter `status: seed` if it's a new page.
- Don't automate — ask for confirmation.

> **Suggested callouts**: if you find contradictions between what was said in the meeting and existing pages, use `> [!contradiction]` inline in the conflicting page. If the meeting raises an unresolved question, `> [!gap]`. If it confirms a strong takeaway, `> [!key-insight]`. The 4 callouts (contradiction, gap, stale, key-insight) have custom CSS in `.obsidian/snippets/wiki-callouts.css`.

### Step 4 — Summary in the daily
Add to `daily/YYYY-MM-DD.md` (date of the meeting) in the `## Meetings / relevant interactions` section:

```markdown
- [[raw/meetings/YYYY-MM-DD-{topic}|{topic}]] — {1–2 line synthesis} — decisions: [[decisions/...]]
```

If the daily doesn't exist yet for that date, create it (same logic as `/daily-log`).

### Step 5 — Update INDEX + sub-index
Pattern: **sub-index first, INDEX root after**.

- `decisions/INDEX.md` — if new decisions were created
- `people/INDEX.md` — if new person cards were created
- `{macro-area}/initiatives/INDEX.md` — if status/owner of an initiative was updated
- `knowledge/INDEX.md` — if a domain was touched (typically rare from meetings)
- `INDEX.md` (root) "Recent raw meetings" section: add an entry with 1–2 line synthesis + links to the extracted decisions
- `INDEX.md` (root) "Decisions" section (top recent only): if a new decision deserves visibility in the top-5, include it and push one less important down

### Step 6 — Update `hot.md`
A meeting is almost always a trigger to update `hot.md` (decisions, action items, emerging patterns change "Key Recent Facts" and "Active Threads"). Complete overwrite, ~500 words.

### Step 7 — Append to log.md
```markdown
## [YYYY-MM-DD HH:MM] log-meeting | raw/meetings/{file}
- extracted N decisions, M action items, K new people
- initiatives updated: {list}
- files touched: {list + INDEX touched + hot.md}
```

### Step 8 — Summary to user
Show:
- Decisions created (with links)
- Initiatives updated (what changed)
- New people tracked
- hot.md updated: yes/no
- Inline callouts applied: `[!contradiction]` / `[!gap]` / `[!key-insight]` if relevant
- Suggestions: "want me to open a `/log-decision` proposal for X?" if a big strategic decision emerges that deserves more rigor.

## What NOT to do

- **NEVER** modify the raw transcript.
- Do not invent action items — only those that were actually said.
- Do not assign arbitrary deadlines if not mentioned.
- For controversial or ambiguous decisions: ask the user for confirmation before writing to `decisions/`.
- Do not auto-create new initiatives: if a new one emerges, suggest `/new-initiative` but don't execute without confirmation.
