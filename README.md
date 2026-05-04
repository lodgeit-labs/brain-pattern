# brain-pattern

**An optional architecture for AI-assisted software development — now with deterministic closure.**

A vendor-neutral pattern for giving coding agents persistent memory, identity, integrity discipline, **and a self-auditing Prolog engine that blocks PRs which drift from the recorded state.** Built from nothing more than markdown, git, and ~1,000 lines of Python + SWI-Prolog tooling.

Practised in production at [LodgeiT Labs](https://lodgeit.org). Open-sourced because the pattern is more useful than any one implementation of it.

---

## Why a developer managing GitHub repos should care

If you ship code through GitHub with help from any coding agent — Copilot, Cursor, Claude Code, Gemini, OpenClaw — you have probably noticed:

- Your agent **forgets your team's conventions** five minutes after you told it.
- It **hallucinates an API**, a build flag, a deploy step, a lint rule that doesn't exist.
- It **drifts from your build / test / deploy process** every other PR.
- It **suggests a refactor that contradicts a decision** you wrote down two years ago and have since forgotten.
- It **leaks proprietary context** — internal hostnames, client identifiers, billing codes — into a comment, a commit message, or a PR description that ends up on a public repo.

These are not LLM problems. They are **memory and discipline problems**. The fix is not a bigger model; it is a small, durable structure your agent reads at the start of every session, writes to as it works, and is *audited against* before any PR can land.

The Brain Pattern gives you that structure in three escalating tiers:

| Tier | What you get | Effort |
|---|---|---|
| **Layer 1 (persona + memory)** | Your agent stops being a stranger every session. | 90 minutes. |
| **Proofing 0 (graph integrity)** | Every claim in your Brain is cryptographically anchored. Hand-edits to canonical metadata fail CI. | One day. |
| **Proofing 1 (deterministic closure)** | Your Brain audits **itself**. A Prolog engine reads the markdown, projects it into facts, and runs rules. Drift is detected automatically and blocks merge. | One day. |

The proofing tiers are what move you from *"I have notes my agent reads"* to *"my repo cannot land a PR that contradicts what it claims about itself."* That is the property GitHub-managing devs care about, because it makes review tractable: you stop arguing about whether the docs match the code; the gate has already proved it.

---

## What this is

A **pattern**, not a product:

- No infrastructure. No cloud. No licence. No vendor lock-in.
- ~1,000 LOC of Python + SWI-Prolog tooling, all Apache-2.0, lift-and-fork friendly.
- Works with **any** coding agent that can read a file.
- Tier 1 (persona + memory) adoptable in 90 minutes.
- Both proofing tiers demonstrated end-to-end in [the reference implementation](#reference-implementation).

## What this isn't

- **Not a product.** Nothing to install, nothing to buy, nothing to subscribe to.
- **Not a framework.** No code to import; no package to depend on.
- **Not vendor-specific.** Switch agents tomorrow; your Brain comes with you.
- **Not all-or-nothing.** Take Layer 1 today, add the proofing tiers when you outgrow the pain.

## Read the document

→ **[`BRAIN_PATTERN_FOR_DEVELOPERS.md`](./BRAIN_PATTERN_FOR_DEVELOPERS.md)** — full pattern, ~20 minute read.

The document covers:

1. The problem, stated plainly
2. The pattern in one diagram (Agent → Brain → Kit, three zones, downhill flow, **bilateral audit**)
3. What lives in a Brain
4. The six layers — persona, standing rules, knowledge graph, **graph-integrity tooling (Proofing 0)**, egress filter, **deterministic closure (Proofing 1)**
5. A 90-minute experiment you can run today
6. **Proofing 0 worked example** — content-hashes + mutation ledgers in practice
7. **Proofing 1 worked example** — the Prolog audit engine, with two real "structural sight" loops from the reference Brain
8. **The human-side disciplines that complement the audit** — ceiling-as-measurement, the Memory Tracer review pattern, two-PR additive-then-subtractive sequencing, cut-over diff review
9. Honest cost / benefit
10. Common objections, answered

## Why developers managing GitHub repos buy in

The two proofing tiers translate into concrete, mergeable PR-level guarantees you can put on your CI status page:

- **Proofing 0 (graph integrity).** No PR lands if any node's `content_hash` was changed without an entry in the mutation ledger. **Hallucinated metadata cannot survive the gate.**
- **Proofing 1 (deterministic closure).** A SWI-Prolog audit reads your Brain on every PR, projects it into facts (~150 facts in the reference Brain today), and evaluates a small ruleset (currently 7 rules, "W1–W7"). The gate is **tri-state**: exit 0 = COHERENT, exit 1 = INCOHERENT (rule violation), exit 2+ = the audit could not run (infrastructure broken). All three states are surfaced separately in CI; you cannot mistake "audit silently broke" for "audit passed."

In the reference Brain, Proofing 1 has already caught:

- Three carryover files claiming `Status: Active` while the index claimed they were resolved (PR #89/#90).
- 21 lesson citations in the index pointing at registry entries that didn't exist (PR #91/#92).
- A protocol-version pointer that drifted across two sections after a schema upgrade (several iterations).
- An attempted PR that would have removed a banked lesson — the gate refused to let it land.
- During a curation pass that demoted index detail into topical files, the same gate caught the cut-over **before** commit: every demoted row from the index was confirmed present in the topical file with the same id and the same closure state, refusing to let an index/detail mismatch ship.

These are exactly the kinds of drift that **silently rot a wiki**. Here, they fail loudly, on a known PR, with a Prolog finding citing the offending file and line. **The audit reproduces what humans see when they look carefully — then it does it on every CI run, forever.**

## Reference implementation

LodgeiT Labs runs this pattern in production. The public Kit produced from the Brain lives at:

- **[`lodgeit-labs/clawdog`](https://github.com/lodgeit-labs/clawdog)** — the open-source classification engine.

The Brain itself is private (it contains LodgeiT-specific operational knowledge), but the *pattern* is open. If you want to see the Proofing 1 tooling in flight, the [`BRAIN_PATTERN_FOR_DEVELOPERS.md`](./BRAIN_PATTERN_FOR_DEVELOPERS.md) document includes annotated extracts from the live extractor, audit engine, and CI workflow.

## Audience

This document is written for **senior software engineers and developers managing GitHub repositories** evaluating whether to adopt structured memory and self-auditing for their AI coding workflows. It is deliberately not aimed at managers; it assumes you're the person who will actually try the experiment, run the Makefile, and read the Prolog.

If you're an engineering leader looking for a one-pager to circulate, the TL;DR section of the main document is your starting point.

## How this repo practises the pattern

A documentation repo is not a Brain — there is no knowledge graph here, no `content_hash` frontmatter, no W-rules to fire. So Proofing 0 and Proofing 1 don't apply. But the *publication-integrity* surface still does, and this repo gates it: every PR runs `link-check` (lychee verifies every URL resolves) and `markdown-lint` (markdownlint verifies the structure is well-formed). Both block merge on failure.

The principle generalises: **the cheapest discipline that catches a real failure class is the one to ship.** A teaching artefact about strict-mode integrity that itself accepted broken links would be incoherent.

## Discussion

Issues are open. If you adopt the pattern, modify it, find a flaw in it, or want to share what your team did differently, please [open an issue](https://github.com/lodgeit-labs/brain-pattern/issues). The pattern improves through being practised in different contexts.

## Licence

[Apache 2.0](./LICENSE). The pattern itself is unencumbered — it is a design, not code.

---

*From [LodgeiT Labs](https://lodgeit.org). Maintained by ClawDog ∮*
