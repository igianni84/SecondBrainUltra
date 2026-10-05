---
type: meta
description: Immutable inbox for external material. The LLM reads but never modifies files here.
status: evergreen
---

# raw/ — Immutable inbox

Everything that enters SecondBrainUltra from outside lands here. The LLM may read these files, but **never modifies them**. Processed output lives in `knowledge/`, `decisions/`, `people/`, `daily/`, etc.

## Subfolders

- **`meetings/`** — call/meeting transcripts, saved as the recording tool exported them: same file name, no frontmatter. Processed by `/log-meeting <path>`.
- **`articles/`** — web-clipped articles (Obsidian Web Clipper or manual save). Processed by `/ingest <path>`.
- **`notes/`** — raw notes, voice-memo transcripts, screenshots-as-text. Processed by `/ingest <path>`.
- **`assets/`** — PDFs, images, attachments. PDFs are excluded from git (see `.gitignore`).

## Frontmatter conventions

Articles and notes should have minimal frontmatter so downstream skills can route correctly. Meeting transcripts have none.

### For meetings
No frontmatter: the transcript stays as the recording tool exported it, so there's nothing to fill in by hand. `/log-meeting` reads date, title and attendees from the transcript's header.

### For articles
```yaml
---
type: raw-article
date: YYYY-MM-DD
url: https://...
author: Author Name
source: medium | substack | blog | ...
---
```

### For notes
```yaml
---
type: raw-note
date: YYYY-MM-DD
source: voice-memo | screenshot | hand-notes
---
```

## Why immutable?

1. **Auditability**: you can always trace a wiki claim back to the original source verbatim.
2. **Idempotence**: re-running `/ingest` on the same file produces the same result.
3. **Trust**: the LLM never silently "improves" your raw input.
