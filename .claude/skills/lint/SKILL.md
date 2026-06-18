---
name: lint
description: Health-check of the SecondBrainUltra wiki. Searches for contradictions between pages, orphans without incoming links, concepts cited but without a dedicated page, stale claims, missing frontmatter. Trigger -- user invokes `/lint` (typically weekly). Produces a `lint-report.md` with specific fix suggestions.
---

# /lint — Wiki health-check

## Purpose

Periodically (ideally once a week, after `/weekly-review`), verify wiki health: find inconsistencies, gaps, and suggest maintenance actions.

Pattern from Karpathy/Leo — the idea is that the wiki self-maintains because the AI does the bookkeeping.

## What to check

### 1. Orphans
Markdown files in the wiki that **no other file** links to via wikilink. Possible candidates:
- Archive/remove
- Or connect to other pages if still relevant

Excluded from orphan logic: `INDEX.md`, `README.md`, `_template*.md`, `MEMORY.md`.

### 2. Broken wikilinks
Wikilinks `[[...]]` pointing to **non-existent** files. They're typos or renamed files.

### 3. Missing/malformed frontmatter
Wiki pages without frontmatter or with unrecognized `type:`.

### 4. Reverse-orphan concepts
Recurring terms (>3 occurrences in the wiki) that do NOT have a dedicated page. They might deserve one.
- Examples: names of people appearing in `daily/` without a card in `people/`
- Initiatives mentioned but without a card in `{macro-area}/initiatives/`

### 5. Hypotheses ready for promotion
Entries in `knowledge/{domain}/hypotheses.md` with `Confirmations: 3/3` not yet promoted to `rules.md`.

### 6. Daily without weekly
Weeks of daily logs without a corresponding `weekly/YYYY-Www.md`.

### 7. Stale initiatives
Cards in `{macro-area}/initiatives/` with `last-updated` > 30 days but `status: active`. Likely missed update or status needs reviewing.

### 8. Unreferenced decisions
Entries in `decisions/` not linked from any other file. Might not be "live" — consider archiving.

### 9. Obsolete knowledge claims
Entries in `knowledge/{domain}/knowledge.md` or `rules.md` that might be contradicted by newer entries (requires careful domain reading — use a subagent if large).

### 10. Stagnant `status: seed` pages
Pages in `knowledge/`, `weekly/`, `plans/` with frontmatter `status: seed` and `updated` (or `created` if `updated` missing) older than **30 days**. These are seed pages that never got developed — candidates for promotion to `developing`/`mature` or for archiving.

**Suggested fix**:
- If the page is still relevant: promote it (enrich content, update `status: developing`).
- If obsolete or never took off: propose archiving.
- If it's just a light reference and that's fine: promote to `evergreen` (doesn't need updates).

### 11. Unresolved callouts
Pages with open `> [!contradiction]` or `> [!gap]` callouts — flags left open by the AI or user that never got closed. `> [!stale]` is different: it's a hint for future verification, not a blocker.

**Suggested fix**:
- `[!contradiction]`: re-read the two conflicting pages, decide which prevails, update and remove the callout. If the contradiction was real but resolved by a more recent decision, link the decision.
- `[!gap]`: if the gap is still open, consider a targeted `/ingest`, a `/log-meeting` for a dedicated call, or turn it into an action item in the daily.

## Output

File: `lint-report.md` (root, overwritten on each run).

Frontmatter:
```yaml
---
type: lint-report
generated: YYYY-MM-DD HH:MM
issues-found: N
---
```

Body organized by category, with concrete fixes:

```markdown
# Lint report — YYYY-MM-DD HH:MM

## Summary
N total issues.
- Orphans: X
- Broken wikilinks: X
- ...

## Orphans
- `daily/2026-01-15.md` — not referenced by any INDEX. **Fix**: add to `INDEX.md` Daily logs.

## Broken wikilinks
- `decisions/2026-01-12-pricing.md` links to `[[knowledge/consulting/pricing-rules]]` but the file doesn't exist. **Fix**: either create the file or correct the link.

## ...
```

## Workflow

### Step 1 — Explore the wiki
Use a subagent (Explore) to scan every `.md` in the wiki (excluding `raw/` which isn't linted), extracting wikilinks and frontmatter. For large repos, delegation is faster.

### Step 2 — Run the 11 checks
Category by category. Aggregate the issues.

### Step 3 — Suggest fixes
Every issue must have a concrete action. Not "check X" — but "rename X to Y" or "add link in Z".

### Step 4 — Write `lint-report.md`
Overwrite (it's a transient report, not historical).

### Step 5 — Append to log.md
Append ONE single line under the current month's header in `log.md` (`## YYYY-MM`, create it if missing):
```
- YYYY-MM-DD HH:MM · lint · wiki health-check → {N issues found; see lint-report.md}
```

### Step 6 — Propose actions to the user
Show a report summary and ask whether to apply some auto-fixes (the trivial ones) or let the user handle them manually.

## What NOT to do

- Do not auto-apply fixes without asking.
- Do not remove orphan files — those are the user's choices.
- Do not invent contradictions: if uncertain, report as "to verify", not as an issue.
