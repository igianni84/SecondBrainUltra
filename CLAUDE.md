# SecondBrainUltra — Your Second Brain

> This folder is your personal operating system: a meta-layer that gives a persistent, long-lived memory to Claude Code (and to you) across every session.
> Drop work in (meeting transcripts, articles, notes) and the slash commands (`/daily-log`, `/ingest`, `/log-meeting`, …) do the bookkeeping so the wiki stays useful instead of rotting.

---

## 1. Owner identity

- **Name**: `{{YOUR NAME}}`
- **Email**: `{{YOUR EMAIL}}`
- **Working language**: `{{e.g. English}}`
- **Main role(s)**: `{{e.g. Product Manager at ACME, independent consultant}}`
- **Strategic goals**: `{{1-3 goals you want this system to serve}}`

> Replace the `{{...}}` placeholders above with your real identity. The AI reads them at session start via `CLAUDE.md` and tailors its behavior accordingly.

See also `.claude/memory/MEMORY.md` (team memory, committed) and `~/.claude/projects/.../memory/` (auto memory, per-machine).

---

## 2. Macro areas

This system assumes 0–N macro folders at the root, each representing a distinct **context** of your working life (employer, side venture, client portfolio, personal). The template ships one example — `WORK/` — that you should rename or duplicate to match your reality.

Suggested starting points:
- `WORK/` — main employer / primary role
- `CLIENTS/` — consulting or client portfolio
- `VENTURES/` — personal side-projects
- `LIFE/` — optional, if you want personal life in the same graph

Each macro area is **standalone**: it can have its own `CLAUDE.md`, its own `initiatives/` subfolder, its own conventions. If the area is software with its own git history, add it to the parent `.gitignore`.

---

## 3. The three meta-layers (wiki pattern)

Adapted from Andrej Karpathy's "LLM Wiki" and AgriciDaniel's claude-obsidian.

### Layer 1 — `raw/` (immutable)
Everything entering from outside. **The LLM reads but never modifies.**
- `raw/meetings/` — meeting transcripts, saved as the recording tool exported them: same file name, no frontmatter. Date and attendees come from the transcript's header.
- `raw/articles/` — web-clipped articles (via Obsidian Web Clipper or manual)
- `raw/notes/` — raw notes, voice-memo transcripts, chat screenshots
- `raw/assets/` — PDFs/images/attachments (PDFs excluded from git via `.gitignore`)

### Layer 2 — Wiki (LLM-processed output)
- `hot.md` (root) — **hot cache** ~500 words, recent-context digest. Auto-loaded at session start via the `SessionStart` hook. Overwritten (not appended) by `/end-session`, `/daily-log`, `/log-meeting`, `/log-decision`. See `§4bis`.
- `INDEX.md` (root) — primary catalog, links to per-domain sub-indexes.
- `daily/YYYY-MM-DD.md` — daily digest (created by `/daily-log` or `/end-session`)
- `weekly/YYYY-Www.md` — weekly review (created by `/weekly-review`)
- `decisions/YYYY-MM-DD-{topic}.md` + `decisions/INDEX.md` — cross-area decisions with context, alternatives, trade-offs
- `plans/{name}.md` — macro roadmaps
- `knowledge/{domain}/` + `knowledge/INDEX.md` — domain knowledge with a promotion lifecycle (knowledge → hypotheses → rules)
- `people/{slug}.md` + `people/INDEX.md` — lightweight directory of relevant people (created on evidence, not proactively)
- `{macro-area}/initiatives/{slug}.md` + `{macro-area}/initiatives/INDEX.md` — one file per long-running workstream

### Layer 3 — Schema (this file + `.claude/`)
- `CLAUDE.md` (this file) — top-level instructions, owner identity, inviolable rules
- `.claude/CLAUDE.md` — detailed workflow orchestration (plan mode, persistence, decision journal)
- `.claude/skills/` — custom slash commands (`/daily-log`, `/end-session`, `/ingest`, `/lint`, …)
- `.claude/hooks/` — `lint-scan.py` (the scanner of `/lint`) and `check-index-caps.sh` (a `Stop` hook)
- `.claude/memory/` — team memory (committed, shared across contributors)

---

## 4. Obsidian-friendly conventions

This vault is also an Obsidian vault (`.obsidian/` is pre-configured). To get graph view and plugins (Dataview, etc.) working:

- **Wikilinks**: use `[[Page Name]]` for internal links, NOT `[text](path.md)`. Works in both Obsidian and for the LLM.
- **YAML frontmatter** on every wiki page:
  ```yaml
  ---
  type: decision | knowledge | hypothesis | rule | person | initiative | daily | weekly | plan | client | meta | lessons | log | log-archive | lint-report
  date: YYYY-MM-DD
  status: <see status lifecycle below>
  tags: [topic1, topic2]
  aliases: [alternative name]
  ---
  ```
- **Naming**: `kebab-case`, dates `YYYY-MM-DD`, slugs short and meaningful.
- **PNG/JPG are included** in the repo (Obsidian assets); PDF/XLSX/PPTX/DOCX **are not** (see `.gitignore`).
- **Outside this enum**: `.claude/memory/` has its own schema (`user | feedback | project | reference`, see `.claude/CLAUDE.md` → Team Memory). Schema-layer files (`CLAUDE.md`, `README.md`, `MEMORY.md`, `SKILL.md`) need no frontmatter. Files in `raw/` aren't wiki pages: they follow `raw/README.md`, and meeting transcripts have no frontmatter at all.

### Status lifecycle (`status` field)

The `status` field has two value families depending on page `type`:

**A. Domain-specific status** (for types with their own semantic lifecycle):
- `decision` → `active | superseded`
- `initiative` → `active | paused | done`
- `client` → `active | dormant | prospect`
- `person` → `active | dormant | archived`

**B. Universal lifecycle status** (for knowledge, hypothesis, rule, weekly, daily, plan, meta):
- `seed` — exists, barely populated, just created
- `developing` — has real content, not yet complete
- `mature` — comprehensive, well-linked
- `evergreen` — stable, unlikely to need updates

A new page almost always starts as `seed`. `/lint` flags it if it stays `seed` for more than 30 days — candidate for promotion or archiving.

### Custom Obsidian callouts

4 semantic callouts have custom CSS in `.obsidian/snippets/wiki-callouts.css` (enabled by default in `.obsidian/appearance.json`):

- `> [!contradiction]` — two pages disagree on a fact. Link both; the LLM or you resolve it on the next pass.
- `> [!gap]` — open question or concept cited but not documented. Candidate for a targeted `/ingest`.
- `> [!stale]` — claim may be obsolete; verify on the next relevant pass.
- `> [!key-insight]` — takeaway relevant beyond the local context; candidate for promotion to `knowledge/` or to a `rule`.

`/lint` flags open `[!contradiction]` and `[!gap]` callouts.

### ⛔ When NOT to use `[!gap]`

`[!gap]` is a **flag**: it says *"something is missing here and someone has to close it"*. If it also marks what's already tracked, it stops telling things apart.

Three cases that aren't gaps:

| Not a gap | Why | Write instead |
|---|---|---|
| **A blocker inside a "Blockers and risks" section** | The section *is* already its home. The flag adds nothing | A bold bullet |
| **A pointer to another home** (*"⛔ Home: X — only the pointer here"*) | The gap is open **there**, with its own marker | A bullet with the wikilink |
| **A question inside a dated entry** (an initiative's timeline, `daily/`, `decisions/`) | It's the snapshot of *that* day, not a question for today | *"Open question as of YYYY-MM-DD, kept as a record"* |

⇒ The test: **if someone closed this gap, would this file change?** If the answer is "no, another file would change", a pointer goes here. If it's "no, it was true only that day", it's a record. `[!gap]` stays for the **open question that has no home yet** — the only case where the lint should wake someone up.

---

## 4bis. Hot cache (`hot.md`)

The file `hot.md` at the root is a ~500-word cache of the most recent context. **It's a cache, not a journal** — overwritten completely, never appended.

### ⛔ Eviction rule (the only one that matters)

**The cache doesn't accumulate: it replaces.** When a new fact comes in, what the next session no longer needs goes out — you don't add on top and leave the previous session below. The mark of a journal isn't length: it's yesterday's session kept under today's, or a closed fact that stays (the journal is `daily/` + `log.md`). Under the cap the cache can grow: write what's needed.

Evicted content **isn't lost**: it already lives in `daily/`, `decisions/`, `knowledge/` and the initiatives. Before evicting, check that it has a home — if a pattern exists **only** in `hot.md`, its home is `knowledge/{domain}/hypotheses.md`, not this cache.

### Caps

| | Cap |
|---|---|
| **Whole file** | **≤ 700 words** (target ~500). Over the cap, what's no longer needed goes first; if everything is needed, go over and tell the user how many words and why |
| `updated:` (frontmatter) | **only `YYYY-MM-DD`**. ⛔ **Never a chain** of sessions separated by `//` — it's how that one field grows to hundreds of words |
| **Last Updated** | 1–2 lines: date + tagline |
| **Key Recent Facts** | **max 5 bullets**, ≤60 words each |
| **Recent Changes** | **max 3 bullets** — only the last 1–2 sessions |
| **Active Threads** | **max 4 bullets** |
| **Open Patterns** | **pointers only** to `knowledge/`, ≤60 words in all. Pattern tracking (`n/3` counts, dated confirmations) lives in `knowledge/`, **never here** |

`lint-scan.py` measures every cap except the Last Updated lines; `wc -w hot.md` gives the total on the spot.

**Format** (5 sections, in this order):
1. **Last Updated** — date + session tagline
2. **Key Recent Facts** — strategic bullets (wikilinks to decisions/ and key meetings)
3. **Recent Changes** — created / updated / new sub-index
4. **Active Threads** — next steps, rollovers, blockers, operational flags
5. **Open Patterns / Hypotheses** — pointers to the active rules and hypotheses in `knowledge/`

**Auto-loaded** at every session start, after `/clear` and after compaction, via the `SessionStart` hook in `.claude/settings.json`. Eliminates the need for a manual recap.

**Updated by**: `/end-session`, `/daily-log`, `/log-meeting`, `/log-decision`, optionally `/ingest` and `/new-initiative` (only if the operation changes Key Recent Facts or Active Threads).

Pattern inherited from [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) (their `wiki/hot.md`).

---

## 5. Operations (slash commands)

| Command | What it does |
|---|---|
| `/daily-log` | Creates/updates `daily/YYYY-MM-DD.md` (lighter checkpoint; also runs inside `/end-session`) |
| `/end-session` | `/daily-log` + update `log.md` + commit + push |
| `/ingest <path>` | Processes a file in `raw/` → updates wiki + INDEX + log |
| `/lint` | Health-check of the wiki (contradictions, orphans, gaps) |
| `/log-meeting <path>` | Extracts decisions / action items / people from a meeting transcript |
| `/log-decision` | Adds a new entry to `decisions/` |
| `/new-initiative` | Scaffolds a new initiative in a macro area |
| `/weekly-review` | Rolls up daily logs of the week into `weekly/YYYY-Www.md` |

Every operation appends **one line** to `log.md` (a lean audit trail, not a journal), in the format `- YYYY-MM-DD HH:MM · {op} · {target} → {outcome}`, under the current month's header `## YYYY-MM`. `log.md` keeps only the current month; `/end-session` archives concluded months to `log/YYYY-MM.md` (one file per month). Details and the compaction rule: `.claude/CLAUDE.md` → "Append to log.md".

---

## 6. Typical workflows

**Article read**:
1. Clip or save the `.md` into `raw/articles/`
2. `/ingest raw/articles/{name}.md`
3. The LLM reads, writes a summary in `knowledge/{domain}/`, updates INDEX, logs.

**Meeting finished**:
1. Export the transcript, save it into `raw/meetings/` with the name the tool gave it, no frontmatter added
2. `/log-meeting raw/meetings/{file}`
3. The LLM extracts decisions → `decisions/`, action items → `{macro-area}/initiatives/{workstream}.md`, people → `people/`.

**End of each work session** (run it whenever you close Claude Code — typically several times a day, not just once):
1. `/end-session`
2. The LLM summarizes the session, proposes a daily log, you confirm; it then updates `log.md`, commits + pushes.

**Weekly review (Friday or Monday)**:
1. `/weekly-review`
2. The LLM reads the week's daily logs, produces a summary in `weekly/`, flags trends and next steps.

---

## 7. LLM agent guidelines (me)

- **Working language** as declared in §1.
- **Plan mode** for non-trivial tasks (3+ steps or architectural decisions).
- **Subagent strategy** for exploration/parallelism (keep the main context clean).
- **Mandatory wikilinks** for internal wiki navigation.
- **Mandatory YAML frontmatter** on every wiki page (enables future Dataview queries).
- **For macro-area work**, read the relevant `{macro-area}/CLAUDE.md` first if it exists.
- **Never assume**: get confirmation before structural actions. Assumptions propagate downstream.

---

## 8. Key files to check first

| File | When to read it |
|---|---|
| `.claude/memory/MEMORY.md` | At the start of every session |
| `INDEX.md` | To orient yourself in the wiki |
| `log.md` (last entries) | To know what happened recently |
| `.claude/CLAUDE.md` | For workflow details |
| `{macro-area}/CLAUDE.md` | When you work on a macro area |

Method corrections, loaded every session together with this file: @lessons.md

---

*Last rewrite: template baseline — replace this line when you fork and start populating.*
