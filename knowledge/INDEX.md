---
type: meta
description: Sub-index for domain knowledge. Points to each domain's knowledge / hypotheses / rules.
status: evergreen
---

# Knowledge — sub-index

> Domain knowledge lives here, split by domain. Each domain folder has three files:
> - `knowledge.md` — observed facts and patterns (descriptive)
> - `hypotheses.md` — patterns to confirm (3 confirmations → promote to rule)
> - `rules.md` — confirmed patterns (apply by default)

## Domains

- [[knowledge/workflow/knowledge|workflow]] — patterns about how you manage your own work (meetings, prioritization, stakeholder management)

<!-- Add domains as they accumulate enough content to be worth splitting. Suggested domains:
- `ai-workflows` — patterns of working with AI (prompting, agentic workflows, MCP usage)
- `{your-industry}` — your industry's business vocabulary and rules
- `{core-technology}` — tools and platforms your work revolves around
-->

## Promotion pipeline

```
observation (knowledge.md)
    ↓ (recurring enough to predict)
hypothesis (hypotheses.md)  ← count: 0/3
    ↓ (confirmed 3 times)
rule (rules.md)  ← apply by default
    ↑
    demoted if contradicted ──┘
```

When a hypothesis hits **3/3** confirmations, `/lint` flags it for promotion. The user (or the AI) moves it to `rules.md` with a short "Confirmed on YYYY-MM-DD" note.

When a rule is contradicted by new evidence, demote it back to hypothesis (reset count to 0/3) and log the demotion in `knowledge.md` with context.
