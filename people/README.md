---
type: meta
description: Conventions for the people directory
status: evergreen
---

# people/ — Lightweight directory

Not a full CRM — a lightweight index of people you interact with. Enough to help the LLM give context-aware answers ("who's Jane again?"), not enough to be a commercial tool.

## When to create a page

Create a page when **all** of these hold:
1. The person has been mentioned in the wiki **2+ times** (meetings, decisions, daily).
2. You expect to interact with them again.
3. Context about their role/expertise/preferences would save you re-asking.

Do NOT create a page for:
- One-off mentions (e.g. a name dropped in a transcript you'll never act on)
- People already extensively documented elsewhere (LinkedIn, your CRM — link, don't duplicate)
- Purely private-life contacts (unless you've decided to track personal network here)

## Frontmatter

```yaml
---
type: person
name: Firstname Lastname
role: {their role at the org}
organization: {org slug or name}
last-interaction: YYYY-MM-DD
tags: [domain-tag, relationship-tag]
status: active | dormant | archived
aliases: [nicknames, handles]
---
```

## File naming

`people/firstname-lastname.md` — kebab-case, no spaces, no accents.

## Body template

```markdown
# {Full name}

## Role & context
{Their role, organization, and why they're relevant to you.}

## Background
{What you know about them — trajectory, expertise, style. Capture from conversations and public sources.}

## Preferences / style
{Communication style, what they value, what they avoid. Especially useful for recurring stakeholders.}

## Interactions log
- YYYY-MM-DD: [[raw/meetings/...|topic]] — 1-line takeaway
- YYYY-MM-DD: [[decisions/...|decision-name]] — involvement

## Flags / caveats
{Anything to watch: sensitivities, conflicts of interest, confidentiality.}

## Links
- LinkedIn: ...
- Their blog / writing: ...
- Internal: [[knowledge/...|related-knowledge]]
```

## Do

- Update `last-interaction` on every meaningful touch.
- When you learn a preference, log it under "Preferences / style".
- Flag sensitivities clearly — the LLM will read this before drafting anything involving them.

## Don't

- Speculate about people's personal lives.
- Record negative judgments ("hard to work with") — stick to observable behaviors ("prefers async written updates to live calls").
- Let the page become a diary — keep it scannable in 30 seconds.
