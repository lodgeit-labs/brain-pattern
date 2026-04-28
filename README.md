# brain-pattern

**An optional architecture for AI-assisted software development.**

A vendor-neutral pattern for giving coding agents persistent memory, identity, and integrity discipline — using nothing more than markdown, git, and ~500 lines of Python tooling.

Practised in production at [LodgeiT Labs](https://lodgeit-labs.org). Open-sourced because the pattern is more useful than any one implementation of it.

---

## What this is

If your AI coding agent ever:

- Forgets your team's conventions five minutes after you told it
- Hallucinates an API that doesn't exist
- Drifts from your build / test / deploy process
- Suggests something that contradicts a decision you made two years ago
- Leaks proprietary context into a public artefact

…you have a memory and discipline problem, not an LLM problem. **The Brain Pattern is the fix.** It is a small, durable structure — markdown files in a git repo — that your agent reads at the start of every session and writes to as it works.

No infrastructure, no cloud, no licence, no vendor lock-in. **You can adopt Layer 1 in 90 minutes.**

## What this isn't

- **Not a product.** Nothing to install. Nothing to buy.
- **Not a framework.** No code to import.
- **Not vendor-specific.** Works with Copilot, Cursor, Claude Code, Gemini, OpenClaw, or anything else that can read a file.
- **Not prescriptive.** Take the layers you want, ignore the rest.

## Read the document

→ **[`BRAIN_PATTERN_FOR_DEVELOPERS.md`](./BRAIN_PATTERN_FOR_DEVELOPERS.md)** — full pattern, ~15 minute read.

The document covers:

1. The problem, stated plainly
2. The pattern in one diagram (Agent → Brain → Kit, three zones, downhill flow)
3. What lives in a Brain
4. The five layers — persona, standing rules, knowledge graph, integrity tooling, egress filter
5. A 90-minute experiment you can run today
6. Honest cost / benefit
7. Common objections, answered

## Reference implementation

LodgeiT Labs runs this pattern as part of building open-source accounting and tax compliance systems. The public Kit produced from that Brain lives at:

- **[`lodgeit-labs/clawdog`](https://github.com/lodgeit-labs/clawdog)** — the open-source classification engine.

The Brain itself is private (it contains LodgeiT-specific operational knowledge). The *pattern*, as documented here, is open.

## Audience

This document is written for **senior software engineers** evaluating whether to adopt structured memory for their AI coding workflows. It is deliberately not aimed at managers or executives — it assumes you're the person who will actually try the experiment.

If you're an engineering leader looking for a one-pager to circulate, the TL;DR section of the main document is your starting point.

## Discussion

Issues are open. If you adopt the pattern, modify it, find a flaw in it, or want to share what your team did differently, please [open an issue](https://github.com/lodgeit-labs/brain-pattern/issues). The pattern improves through being practised in different contexts.

## Licence

[Apache 2.0](./LICENSE). The pattern itself is unencumbered — it is a design, not code.

---

*From [LodgeiT Labs](https://lodgeit-labs.org). Maintained by ClawDog ∮*
