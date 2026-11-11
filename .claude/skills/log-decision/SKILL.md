---
name: log-decision
description: Create a new entry in `decisions/` formalizing a strategic decision. Trigger -- user invokes `/log-decision` to register a decision made explicitly or emerged from a conversation (even outside a meeting). The AI drafts the entry from the session and asks the user only for what is missing.
---

# /log-decision — Register a formal decision

## Purpose

Cross-area decisions live in `decisions/`. This skill formalizes one with the standard pattern (context → alternatives → reasoning → trade-offs → references). `/log-meeting` extracts decisions from a transcript; here the user registers one from a conversation.

## Workflow

### Step 1 — Draft from the session
Write the whole draft yourself, from what the session already holds and the template in Step 4. Where the session doesn't say something, leave `{from the user}`: that field is theirs to fill. If there were no real alternatives, write that it was the only viable path and why.

The file is `decisions/YYYY-MM-DD-{slug}.md`, with a slug of at most 6 words (`decisions/README.md`): the topic, not the sentence. The full sentence is the `#` title.

### Step 2 — Check prior decisions
Search `decisions/` for active entries on the same point (the folder, the index and its archive). If there is one, the new decision supersedes it in full or in part: pick which of the two to propose.

### Step 3 — One round with the user
Show the draft and, below it, the questions left: the `{from the user}` fields and the supersession, if any. All together, numbered, each with your proposal. The file is written after their confirmation; a supersession needs an explicit yes.

### Step 4 — Write `decisions/YYYY-MM-DD-{slug}.md`

Frontmatter:
```yaml
---
type: decision
date: YYYY-MM-DD
status: active
tags: [topic1, topic2]
context: {macro-area-slug or 'meta'}
supersedes: []  # ids of any decisions this supersedes
superseded-by: []  # empty at creation time
---
```

Body (from the template in `decisions/README.md`):

```markdown
## Decision
{what you decided, 1–2 sentences}

## Context
{why this decision arose, what trigger/problem}

## Alternatives considered
- **Alt A**: {description}, why rejected
- **Alt B**: {description}, why rejected

## Reasoning
{why this option won}

## Trade-offs accepted
{what you gave up}

## References
- Meeting: [[raw/meetings/...]]
- PRD: [[...]]
- Knowledge: [[knowledge/.../...]]
```

### Step 5 — If superseding: update the old one
- **In full**: the old file gets `status: superseded` and `superseded-by: [new-id]`; the new one has `supersedes: [old-id]`.
- **In part**: the new one has `supersedes-partially: [old-id]`; the old one stays `active`, gets `superseded-partially-by: [new-id]` and, at the top of its "Decision" section, a `> [!stale]` callout saying which part is superseded, with the link to the new one.

Ids are the dated slug, without `decisions/`.

### Step 6 — Update sub-index + INDEX root
Pattern: **sub-index first, INDEX root after**.

**A. `decisions/INDEX.md`** (mandatory) — a row at the top of the right section's table. The sections are the user's own topic clusters (see the file); if none fits, create one or use a catch-all.
```markdown
| YYYY-MM-DD | [[decisions/YYYY-MM-DD-{slug}\|{short title}]] | active | {key tag} |
```
The label is a title of at most 8 words: the summary lives in the file. If the decision supersedes an earlier one, the old row's status becomes **superseded**; if only in part, `active *(point N superseded → [[decisions/{new-slug}\|YYYY-MM-DD]])*`.

**B. `INDEX.md` (root)** "Decisions" section — only if the decision belongs among the 5 shown there. One comes in, one goes out. Keep the top link to `[[decisions/INDEX|decisions/INDEX]]`.

Done when `bash .claude/hooks/check-index-caps.sh` prints nothing: it measures the caps of both indexes, and what it reports gets fixed before the step closes.

### Step 7 — Update `hot.md`
Only for a strategic or architectural decision: it enters *Key Recent Facts* in place of an older fact, following `CLAUDE.md` §4bis. Done when `wc -w hot.md` gives at most 700; if everything is needed, go over and tell the user how many words and why.

### Step 8 — Append to log.md
One line in `log.md` (root), under the current month's header `## YYYY-MM` (create it if missing), with the time from `date +%H:%M`:
```
- YYYY-MM-DD HH:MM · log-decision · {slug} → {what was decided, ≤15 words; +superseded {slug} if applicable}
```

### Step 9 — Connections
Propose in one line the links still missing: from an initiative card, or to a rule or hypothesis in `knowledge/`.
