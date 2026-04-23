---
type: decision
date: 2026-01-15
status: active
tags: [tooling, pkm, wiki]
context: meta
supersedes: []
superseded-by: []
---

# Pick Obsidian over Notion for the personal wiki

## Decision
Use Obsidian as the primary wiki front-end for SecondBrainUltra, with git-backed markdown files on disk. Do not use Notion even though I already have a Notion workspace.

## Context
I needed a wiki system to give Claude Code persistent memory across sessions. The two obvious candidates were Notion (already in my workflow for client docs) and Obsidian (local-first, markdown-native). The trigger: I was about to start the [[WORK/initiatives/acme-payments-rewrite|ACME engagement]] and wanted memory in place before the volume of context ramps up.

## Alternatives considered

- **Notion**: already have a workspace, integrated with my existing docs, great sharing. **Why rejected**: proprietary format, no local files, can't `git diff`, hard for Claude Code to read/write reliably without a custom MCP adapter, and sharing the wiki = sharing my internal thinking.

- **Plain markdown + VS Code**: lowest friction, fully local. **Why rejected**: no graph view, no wikilink autocompletion, no Dataview queries. Would work short-term but degrades as the graph grows.

- **Logseq**: similar to Obsidian, more outline-oriented, open-source. **Why rejected**: weaker plugin ecosystem, and I prefer page-based to outline-based for long-form decisions/meetings.

## Reasoning

Three constraints decided it:
1. **Files on disk** — Claude Code reads and writes plain files natively, no integration layer needed.
2. **Git-versionable** — every wiki change is a commit; history is auditable.
3. **Graph view + wikilinks** — makes the emergent connections between decisions, people, initiatives visible, which is exactly what a second brain is *for*.

Obsidian wins all three. The friction of migrating my Notion client docs is not a blocker — those aren't part of the second-brain graph, they live in Notion as client-facing artifacts.

## Trade-offs accepted
- **Mobile writing**: Obsidian mobile works but syncing on disk across devices requires iCloud/Dropbox/Syncthing — more finicky than Notion's native multi-device.
- **Sharing with collaborators**: if I ever want to share a page, it's "send them a commit" or "publish via Obsidian Publish (paid)". Notion's "share link" is zero-friction.
- **Rich embeds**: Notion embeds Figma/Loom/etc inline; Obsidian is more text-centric. For a second brain that's fine — my rich artifacts live elsewhere anyway.

## References
- Starting this wiki: the template [[README|SecondBrainUltra README]]
- Pattern inheritance: [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)
- Meeting that kicked off the engagement: [[raw/meetings/2026-01-15-acme-kickoff|ACME kickoff]]
