---
type: raw-meeting
date: 2026-01-15
attendees: [jane-doe, you]
source: google-meet
context: work
tags: [kickoff, acme, payments]
---

# ACME Kickoff — 2026-01-15 · 60 min · Google Meet

> EXAMPLE FILE. This is a fictional meeting transcript used to demonstrate the `/log-meeting` workflow of SecondBrainUltra. Replace with real transcripts as you start using your wiki.

---

**Jane Doe** (Head of Engineering, ACME Corp): Thanks for joining. Quick context: we're a 200-person B2B SaaS, payments was built in 2022 by the founding team and hasn't been touched since. It works but every feature takes 3 weeks because the model is wrong.

**You**: Before we scope, what's the deadline pressure?

**Jane**: No hard deadline but the board wants visibility on engineering velocity by end of Q2. So practically, we need something demonstrable by mid-June.

**You**: That's 5 months. What's "demonstrable" mean here — a rewrite, or a migration path?

**Jane**: Migration. We can't afford a big-bang rewrite. I'd like the v2 model running alongside v1, new transactions routed through v2, old ones grandfathered.

**You**: Okay, dual-write with a cutover per customer tier. Who owns the decision on the customer cutover plan?

**Jane**: That's me, with our CFO sign-off. You don't need to worry about it, but flag risks if you see them.

**You**: Understood. For the engagement — what shape works for you? Fractional advisory (1 day/week), embedded (3 days/week), or audit-then-handoff?

**Jane**: Embedded. 3 days a week for the first two months, then we can dial down.

**You**: Works. Let me draft a scope doc by Friday. One thing — I noticed in your blog post on remote-first principles you mentioned investing heavily in internal tooling. Anything about payments tooling that's relevant?

**Jane**: Not directly. We built a nice decision log tool but it's not payments-specific. Happy to share it.

**You**: Perfect. I'll send a calendar invite for a weekly sync Thursdays 10am your time.

**Jane**: Let me introduce you to Marcus — he's the senior engineer who'll be your day-to-day. I'll CC him on the scope doc thread.

**You**: One last thing. How do you want me to communicate? Slack, email, docs?

**Jane**: Slack for fast stuff (#proj-payments-v2), docs for decisions. Avoid email.

**You**: Noted. Talk Thursday.

---

## Action items (raw)

- **You**: draft scope doc by Friday 2026-01-17
- **You**: set up weekly sync Thursdays 10am ACME-local
- **Jane**: introduce Marcus on the scope thread
- **Jane**: share the internal decision-log tool URL
