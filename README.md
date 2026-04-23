# SecondBrainUltra

> A personal second-brain operating system built on **Obsidian** + **Claude Code**.
> Drop your work in (meeting transcripts, articles, notes, decisions) and let Claude do the bookkeeping — so the wiki stays useful instead of rotting.

SecondBrainUltra is a **template**, not a live system. You clone it, fill in your identity, and start feeding it. The schema (folders, slash commands, hooks, Obsidian snippets) is designed so that the AI assistant has persistent memory across sessions and the graph stays navigable.

---

## Why another PKM template?

Most "second brain" templates are just folder structures. This one ships the *behavior* too:

- **8 slash commands** (`/daily-log`, `/end-session`, `/ingest`, `/lint`, `/log-meeting`, `/log-decision`, `/new-initiative`, `/weekly-review`) that do the bookkeeping for you.
- **3 session hooks** that auto-load a "hot cache" at session start, restore it after compaction, and warn you before you lose context.
- **Obsidian callouts** (`[!contradiction]`, `[!gap]`, `[!stale]`, `[!key-insight]`) with custom CSS for semantic flagging.
- **Status lifecycle** (`seed` → `developing` → `mature` → `evergreen`) tracked in frontmatter so stale pages get flagged automatically.
- **Promotion pipeline** for domain knowledge: observation → hypothesis → rule (confirmed 3×).
- **Decision journal** with supersede semantics baked in.

The pattern is adapted from [Andrej Karpathy's LLM Wiki](https://karpathy.ai) and [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian), refined over months of daily use by a working Product Manager.

---

## What's inside

```
SecondBrainUltra/
├── CLAUDE.md                    # Root: identity, 3-layer wiki pattern, conventions
├── INDEX.md                     # Primary catalog
├── hot.md                       # Hot cache (~500 words, auto-loaded at session start)
├── log.md                       # Append-only op log
├── lessons.md                   # Mistake → correction pairs
├── .claude/
│   ├── CLAUDE.md                # Workflow orchestration (plan mode, memory, knowledge)
│   ├── settings.json            # 3 hooks: SessionStart / PostCompact / Stop
│   ├── memory/                  # Team memory (committed)
│   └── skills/                  # 8 slash commands
├── .obsidian/                   # Vault config + custom callouts snippet
├── raw/                         # Immutable inbox (meetings, articles, notes, assets)
├── daily/                       # Daily digests
├── weekly/                      # Weekly reviews
├── decisions/                   # Decision journal (with INDEX)
├── knowledge/                   # Domain knowledge (with promotion pipeline)
├── people/                      # Lightweight CRM (with INDEX)
├── plans/                       # Macro roadmaps
└── WORK/                        # Example macro area (rename/duplicate to match you)
    └── initiatives/             # Long-running workstreams
```

Everything is documented inline in `CLAUDE.md` (root) and `.claude/CLAUDE.md` (workflow). Read those two files first — they're the manual.

---

## Quick start

### 1. Clone and initialize

```bash
git clone https://github.com/{YOUR_HANDLE}/SecondBrainUltra.git my-brain
cd my-brain
rm -rf .git && git init           # start fresh history
```

### 2. Personalize your identity

Open `CLAUDE.md` and fill in section `§1. Owner identity` (name, email, working language, strategic goals). These are placeholder values — the AI reads them at session start.

### 3. Open in Obsidian

Point Obsidian at the folder. The vault is pre-configured (`.obsidian/` is committed):
- Graph view works out of the box
- Custom callouts snippet auto-enabled
- Folder color-coding active

### 4. Open in Claude Code

```bash
claude
```

Claude reads `CLAUDE.md`, loads `hot.md` via the `SessionStart` hook, and knows your 8 slash commands. Try `/daily-log` at the end of your first day.

### 5. (Optional) Rename the example macro area

The template ships with `WORK/` as an example. Rename it (`CLIENTS/`, `VENTURES/`, `{YourEmployer}/`, …) or duplicate it to match your real life. You can have 0–N macro areas.

---

## The daily loop

A typical day inside SecondBrainUltra:

1. **Morning**: session starts, Claude auto-reads `hot.md` — you don't need to recap.
2. **During the day**: you dump raw stuff into `raw/meetings/`, `raw/articles/`, `raw/notes/`. You make decisions and invoke `/log-decision`. You finish meetings and invoke `/log-meeting <path>`.
3. **Before a break**: `/daily-log` to checkpoint.
4. **End of day**: `/end-session` wraps everything, commits, pushes.
5. **End of week**: `/weekly-review` distills the week, flags trends.
6. **Every so often**: `/lint` runs a health check (orphans, broken wikilinks, stale seeds, open `[!contradiction]` / `[!gap]` callouts).

Over time, observations in `knowledge/{domain}/knowledge.md` become hypotheses, hypotheses confirmed 3× become rules. The AI applies rules automatically on relevant future tasks.

---

## Dependencies

- **[Obsidian](https://obsidian.md/)** (free) — for the graph view and Dataview queries
- **[Claude Code](https://docs.claude.com/claude-code)** — for the slash commands, hooks, and subagents
- **git** — for versioning your second brain

That's it. No cloud services, no databases, no SaaS. Your second brain lives as markdown files on your disk and in your git remote.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Credits

- [Andrej Karpathy](https://karpathy.ai) — core idea of an LLM-maintained personal wiki
- [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) — `hot.md` hot cache, status lifecycle, custom callouts
- [Anthropic](https://anthropic.com) — for Claude Code, skills, and the hook system

---

## Contributing

This is a personal template, but improvements are welcome. Open an issue or PR if you:

- find a bug in a skill workflow
- have a pattern to add (new slash command, new callout semantic)
- want to improve documentation

Keep PRs focused and don't over-engineer — the whole point of this template is restraint.
