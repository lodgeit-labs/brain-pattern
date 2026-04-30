# The Brain Pattern

**An optional architecture for AI-assisted software development — now with deterministic closure.**

*Vendor-neutral. Tooling-agnostic. Battle-tested in production at LodgeiT Labs.*

---

## TL;DR

If you're using a coding agent (Copilot, Cursor, Claude Code, Gemini, OpenClaw, anything else) and you've ever had it:

- Forget your team's conventions five minutes after you told it
- Hallucinate an API that doesn't exist
- Drift from your build/test/deployment process
- Suggest a refactor that contradicts an architectural decision you made two years ago
- Leak proprietary context into a public artefact (a comment, a commit message, a PR description)

…then you have a **memory and discipline problem**, not an LLM problem. The Brain Pattern solves it with a simple, durable structure: a git-backed knowledge repo, written in plain Markdown, that your agent reads on every session and writes to as it works — **and that audits itself, in CI, before any PR can land.**

This document describes the pattern in three escalating tiers:

| Tier | What it gives you | Effort |
|---|---|---|
| **Layer 1–3 (memory)** | Your agent stops being a stranger every session. Conventions, decisions, and runbooks live in markdown your agent reads at startup. | 90 minutes for Layer 1; days as you grow into 2–3. |
| **Proofing 0 (graph integrity, Layer 4 + 5)** | Every claim in the Brain is cryptographically anchored. Hand-edits to canonical metadata fail CI. Egress to public artefacts is gated. | One day. |
| **Proofing 1 (deterministic closure, Layer 6)** | A SWI-Prolog audit reads the Brain on every PR, projects it into facts, runs rules. Drift is detected automatically and blocks merge. The Brain audits *itself*. | One day after Proofing 0. |

Adopt in 90 minutes with no infrastructure, no cloud, no licence, and no vendor lock-in. Add the proofing tiers when the pain of drift starts to outweigh the pain of building gates.

---

## The problem, stated plainly

Modern coding agents are powerful within a single session and amnesiac between sessions. They re-derive your team's context every time you open a new chat, and they re-derive it imperfectly. The worse your codebase's documentation, the worse this gets. For greenfield projects this is annoying. For **legacy systems** — large .NET solutions with 15 years of accreted decisions, undocumented integrations, brittle tests, and engineers who have moved on — it is debilitating.

The standard mitigations don't fix it:

- **Confluence / SharePoint / wikis:** Your agent doesn't read them, doesn't trust them, and they go stale because nobody enjoys updating them.
- **ADRs (Architectural Decision Records):** Better, but usually one-shot historical records, not durable agent context. They live in a `docs/` folder that the agent ignores.
- **Per-IDE context files** (`.cursorrules`, `CLAUDE.md`, `.github/copilot-instructions.md`): Tool-specific. Lock you into one vendor. Don't survive when you switch agents. Usually a single file with no internal structure.
- **Telling the agent more in your prompt:** Burns context window, doesn't persist, doesn't compound.

There is also a deeper problem the standard mitigations don't even attempt to solve: **how do you know your knowledge base still matches reality?** Wikis rot because nothing checks. ADRs go stale because nothing checks. Even a well-loved Brain rots because nothing checks. The Brain Pattern's proofing tiers exist because *nothing checks* is the failure mode that matters most for any team that wants their docs to be *load-bearing*.

The Brain Pattern is the fix. It is what you'd build if you stopped trying to fit your team's institutional knowledge into a chat window — and then refused to let it rot.

---

## The pattern in one diagram

```
   ┌──────────────┐
   │  Developer   │
   │   (you)      │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐         reads & writes
   │    Agent     │ ◄─────────────────────────┐
   │  (any LLM)   │                            │
   └──────┬───────┘                            │
          │                                    │
          │ writes                             │
          ▼                                    │
   ┌──────────────┐  ◄── Proofing 0 ──┐        │
   │    BRAIN     │  ◄── Proofing 1 ──┤        │
   │  (git repo,  │     persistent    │        │
   │   markdown)  │     memory +      │        │
   │              │     self-audit    │        │
   └──────┬───────┘                   │        │
          │                           │        │
          │ ─── filtered egress ────► │        │
          │                                    │
          ▼                                    │
   ┌──────────────┐                            │
   │     KIT      │ ── public artefacts:      │
   │ (open source │    your codebase, docs,    │
   │  / public)   │    deployable services    │
   └──────────────┘                            │
```

Three zones. Information flows downhill — from private (Brain) to public (Kit). It never flows back up. This single rule is the foundation of the security model.

**Two audit gates close the loop.** *Proofing 0* is the graph-integrity gate: every canonical node in the Brain has a `content_hash` and a mutation ledger; tampering fails CI. *Proofing 1* is the deterministic-closure gate: a Prolog engine reads the Brain on every PR, projects it into facts, and runs rules. Drift between what the Brain *claims* and what the Brain *contains* is caught before merge.

---

## What lives in a Brain

A Brain is a git repository — private (one per developer or one per team) — containing markdown files in a small, conventional layout. The exact layout is up to you, but a typical Brain has:

```
your-brain/
├── SOUL.md            ← who the agent is, how it behaves, its voice
├── IDENTITY.md        ← name, scope, signature, what it is for
├── USER.md            ← who the agent is helping (you), preferences,
│                         accessibility needs, dev environment
├── AGENTS.md          ← session-startup instructions for the agent
├── MEMORY.md          ← lean index of long-term memory (≤8 KB)
├── memory/
│   ├── YYYY-MM-DD.md  ← daily session logs (raw)
│   ├── architecture.md← topical curated knowledge
│   ├── lessons.md     ← things learnt the hard way (numbered registry)
│   ├── runbooks/      ← stepwise operational procedures
│   └── …
├── PROJECT_NOTES/     ← canonical knowledge nodes (with content_hash + helm_mutations)
│   ├── 100_overview.md
│   ├── 200_decisions/
│   └── 300_runbooks/
├── scripts/           ← integrity tooling (Proofing 0)
├── tooling/coherence/ ← deterministic-closure engine (Proofing 1)
│   ├── coherence_audit.pl   ← rules
│   ├── coherence_kb.pl      ← AUTO-GENERATED facts
│   └── coherence_schema.pl  ← schema invariants
├── Makefile           ← `make audit`, `make coherence-audit`, `make publish-check`, etc.
└── .github/workflows/ ← server-side CI for both gates
```

**The agent reads these files at the start of every session.** That is the entire mechanism. No magic. The persistence comes from the file system, not the model.

### Why markdown, why git

- **Markdown:** human-readable, machine-readable, version-controllable, diff-able, grep-able. Every editor handles it. Every LLM understands it.
- **Git:** every change is a commit, every commit is reviewable, every Brain has a complete history of what the agent learnt and when.
- **No database:** databases require schemas, migrations, and infrastructure. Files require none of those things. "File over App" is an explicit design choice.

### What the layered files do

| File / folder | Purpose |
|---|---|
| `SOUL.md` | The agent's persona, voice, opinions, and stance. Read first every session. |
| `IDENTITY.md` | Name, signature, scope of authority, what the agent will and won't do. |
| `USER.md` | Who you are. Preferences. Workflow. Accessibility (e.g. "I'm colourblind, give me explicit click-paths"). |
| `AGENTS.md` | Session startup sequence: read these files, in this order, before doing anything. |
| `MEMORY.md` | A *lean index* (≤8 KB) of long-term memory. Auto-loads every turn. Points at topical files. **Not a log.** |
| `memory/YYYY-MM-DD.md` | Daily raw session logs. What happened, what was decided, what's still open. |
| `memory/<topic>.md` | Curated long-term knowledge per topic. Read on demand. |
| `memory/lessons.md` | Numbered lesson registry. Cited from MEMORY.md and elsewhere; **Proofing 1 verifies citations resolve.** |
| `memory/runbooks/` | Step-by-step operational procedures the agent must follow exactly. |
| `PROJECT_NOTES/` | Your canonical knowledge graph. Each node has `content_hash` + `helm_mutations[]`. **Proofing 0 verifies hashes; Proofing 1 verifies cross-references.** |
| `scripts/` | The integrity tooling for Proofing 0. |
| `tooling/coherence/` | The audit engine for Proofing 1. |

---

## The six layers of the pattern

The pattern decomposes into six layers, each adoptable independently. You can take Layer 1 in an afternoon and add the rest as you grow.

### Layer 1 — Persona + scope

`SOUL.md`, `IDENTITY.md`, `USER.md`. Three files. Tell the agent who it is, what it is for, and who it serves. Define its voice, its boundaries, its sign-off mannerism.

This sounds frivolous. It isn't. Without it, agents drift toward generic-helpful, hedge every answer, and fail to push back when you're wrong. With it, you have a partisan, opinionated collaborator that speaks in a recognisable voice and develops a consistent style of reasoning.

**Cost:** ~30 minutes once. **Benefit:** every session feels like the same colleague, not a stranger.

### Layer 2 — Standing rules

A small section in `MEMORY.md` listing the rules the agent **must obey**. Not preferences — rules. For example, in a real production Brain:

- *Never commit to `main`/`master` directly. All work goes through a branch + human sign-off.*
- *Never overwrite content hashes; append amendments to a ledger.*
- *Never leak private context into public-facing artefacts.*
- *Never train models inside ephemeral runtime services.*

These are typed as standing rules, not aspirations. The agent treats violation as a failure mode to be detected and refused, not a soft guideline.

**Cost:** ~1 hour to define. **Benefit:** eliminates the most expensive class of agent mistakes — "it did the thing I told it not to."

### Layer 3 — Knowledge graph

`PROJECT_NOTES/` (or whatever you name it). A structured set of markdown files representing your team's institutional knowledge. Each file is a *node*: a stable identifier, frontmatter metadata, and a body of prose. Nodes link to each other.

For a legacy .NET shop, typical nodes might be:

- `100_PRODUCT_OVERVIEW.md` — what the system does, who uses it, what it's for
- `200_decisions/2018_db_choice.md` — why we chose SQL Server over Postgres
- `200_decisions/2021_microservice_split.md` — why the order-processing module is its own service
- `300_runbooks/deploy_to_staging.md` — the exact build/test/deploy sequence
- `300_runbooks/cert_rotation.md` — the certificate rotation procedure
- `400_gotchas/timezone_bug_2023.md` — the timezone bug that ate three weekends
- `500_apis/legacy_soap_client.md` — every quirk of the SOAP client nobody understands

The agent reads these on demand. Your team writes them as decisions are made. Over time, the graph becomes the canonical answer to "why does it do that" and "how do I deploy this".

**Cost:** ongoing — but no more than you'd spend on Confluence pages that nobody reads. **Benefit:** the agent stops re-deriving and starts referencing.

### Layer 4 — Proofing 0 (graph integrity)

This is the moat against silent corruption, and it is what most teams skip and regret.

A Brain is a multi-author, agent-mutable repository. Without integrity tooling, agents will eventually:

- Overwrite a node's content without recording the change
- Hallucinate metadata that looks plausible but isn't
- Introduce contradictions between nodes
- Leave broken links, stale hashes, drifted invariants

The fix is a small set of scripts run at commit time and in CI:

- **A schema validator** — every node's frontmatter conforms to a known shape (Pydantic, JSON Schema, whatever your team prefers).
- **A content-hash auditor** — every substantive node has a `content_hash` field; recomputing the hash must equal the stored value. If they don't match, something was edited without being recorded.
- **A mutation ledger** — every change to a node appends an entry recording who changed it, why, and the previous hash. Never overwrite history.
- **A pre-commit hook** that runs all of the above before the commit lands.
- **A server-side CI workflow** (GitHub Actions, GitLab CI) that runs them again on every PR and blocks merge on failure.

Together, these enforce a property we call the **Zero-Hallucination Law**: *every claim in the Brain is either cryptographically anchored to a known source, or explicitly marked as unverified.* The agent cannot quietly fabricate metadata and have it stick.

This is **Proofing 0**: every canonical node carries its own integrity proof. We call it "0" because it's the floor — without it, nothing else is trustworthy. Proofing 0 catches *mutation drift*: somebody edited a node and forgot to record the change.

**Cost:** ~1 day to build the tooling, then negligible. The scripts are typically <500 lines of Python total. **Benefit:** the Brain remains trustworthy as it grows, even with multiple human and agent authors mutating it concurrently.

A worked example of Proofing 0 in flight is in [Worked example: Proofing 0](#worked-example-proofing-0).

### Layer 5 — Egress filter (the Privacy Gradient)

Brains are private. But teams ship public artefacts — open-source code, documentation, blog posts, conference talks, customer-facing docs. The route from Brain to public artefact must be **gated**, not trusted.

The filter is a script that runs before any Brain → public publication and checks for:

- **Layer A (hard-fail):** known-proprietary fields. E.g. internal cost data, client identifiers, billing codes, contractual fields. If detected, refuse.
- **Layer B (soft-fail):** structural patterns suggestive of leakage. E.g. references to private repository paths, cloud bucket names, internal hostnames. If detected, warn loudly and require an explicit override flag.
- **Layer C (hard-fail):** a reserved namespace (e.g. `x-internal-*`) that anything internal must use. If any field in that namespace appears in a publication candidate, refuse.

The filter runs on egress only — never as a pre-commit hook on the Brain itself, because that would block authoring of legitimately private content. You commit privately and freely; the gate fires only when you try to publish.

This is the same architectural pattern as a unidirectional firewall: data can flow downhill (private → public), but only after passing a deterministic check; nothing can flow uphill.

**Cost:** ~1 day to build. **Benefit:** you can run a public open-source presence and a private knowledge base from the same workflow without ever lying awake worrying about leaks.

### Layer 6 — Proofing 1 (deterministic closure)

This is the layer that turns a well-loved Brain from *"my agent reads it"* into *"my repo cannot land a PR that contradicts what it claims about itself."*

Proofing 0 catches *mutation drift* (somebody edited a hashed node and forgot to record the change). It does not catch *coherence drift*: two parts of the Brain disagreeing with each other while both individually satisfying their own integrity proof. Examples we've seen in real Brains:

- An open-thread index claiming Thread #22 is "active" while the carryover file's own status header reads "resolved".
- A `MEMORY.md` Latest Activity entry referring to `Lesson #9` while the lesson registry only goes up to #8.
- A protocol-version pointer drifting across two sections after a schema upgrade — the schema is at v3.4.0, two pointers got bumped, three didn't.
- A "Resolved Open Threads" section listing thread X, while the Pending-Andrew table still has thread X marked active.

These are exactly the kinds of drift that *silently rot a wiki*. The fix is to project the Brain into a logic-programming representation and run rules over it.

The architecture is small:

```
   ┌──────────────────────┐         ┌──────────────────────┐
   │  Brain (markdown +   │   ──▶   │  extractor (~500 LOC │
   │  YAML frontmatter +  │  parse  │  Python parsers per  │
   │  PROJECT_NOTES YAML) │   ──▶   │  file kind)          │
   └──────────────────────┘         └──────────┬───────────┘
                                               │ emit
                                               ▼
                                    ┌──────────────────────┐
                                    │ coherence_kb.pl      │
                                    │ AUTO-GENERATED facts │
                                    │ (~150 facts in the   │
                                    │  reference Brain)    │
                                    └──────────┬───────────┘
                                               │ load
                                               ▼
                                    ┌──────────────────────┐
                                    │ coherence_audit.pl   │
                                    │ rules (W1..W7 today; │
                                    │ ~300 LOC SWI-Prolog) │
                                    └──────────┬───────────┘
                                               │ run
                                               ▼
                              ┌──────────────────────────────────────┐
                              │ tri-state exit code:                 │
                              │  0 = COHERENT                        │
                              │  1 = INCOHERENT (rule found drift)   │
                              │  2+ = audit could not run            │
                              └──────────────────────────────────────┘
```

The seven rules in the reference Brain today, schema-locked under predicate names W1–W7:

| Rule | What it catches |
|---|---|
| **W1** | Dangling lesson citations — text that cites `Lesson #N` where the registry has no `#N`. |
| **W2** | MEMORY.md ceiling discipline — `MEMORY.md` exceeded its declared byte cap (default 16 KB). |
| **W3** | Carryover index/header divergence — index says "resolved", file's own status header says "active" (or vice versa). |
| **W4** | Stale Open Thread claims — index claims a thread is active but its file evidence says otherwise. |
| **W5** | Protocol-version pointer drift — current-state sections cite an old version number. |
| **W6** | Unregistered/malformed mutation IDs — a citation references a mutation ID not present in any helm-ledger or commit registry. |
| **W7** | Status-lattice violations — a claimed status value is outside the closed enumeration (`active | dormant | closed | resolved | superseded | merged_into(URN)`). |

**The audit is tri-state.** This is non-negotiable for any CI gate that wraps a non-trivial rule engine: a binary green/red gate cannot distinguish "the rule passed" from "the rule failed to run". For SWI-Prolog specifically, that means using `swipl -t 'halt(2)'` (not `-t halt`, which defaults to `halt(0)` and silently green-lights infrastructure breakage), and ensuring the main goal explicitly calls `halt(0)` for COHERENT and `halt(1)` for INCOHERENT. All three states surface separately in CI logs; you cannot mistake "audit silently broke" for "audit passed."

**The KB is auto-generated, not hand-edited.** The extractor produces `coherence_kb.pl` deterministically from the markdown sources. A banner at the top of the file reads "DO NOT HAND-EDIT — regenerated by `make coherence-audit`". The CI gate regenerates the KB before running the audit, so any drift between markdown and KB is a bug in the extractor, not a content question.

**The schema is locked.** New predicate shapes require a schema mutation (in the reference Brain, that's an amendment to `INFOVERSE_PROTOCOL.md`'s narrative-note dialect specification). This prevents the audit from drifting into shape-soup over time.

This is **Proofing 1**: the Brain audits its own coherence, deterministically, on every PR. We call it "1" because it builds on Proofing 0 — without trustworthy node integrity at the floor, you cannot trust a higher-level coherence audit either.

**Cost:** ~1 day after Proofing 0. The reference Brain ships in ~500 LOC of Python parsers + ~300 LOC of Prolog rules + ~250 LOC of test harness. **Benefit:** the Brain reads itself, and is now obligated to.

A worked example of Proofing 1 in flight — including two complete "structural sight" loops where the audit found real drift — is in [Worked example: Proofing 1](#worked-example-proofing-1).

---

## What you don't have to build

The following are *generic* — they have nothing to do with any specific domain or vendor — and can be lifted directly from any existing Brain implementation:

- The schema validator pattern
- The content-hash auditor (Proofing 0)
- The mutation ledger format
- The pre-commit hook
- The CI workflow (with tri-state coherence gate)
- The publication filter (with team-specific denylist)
- The Makefile that wires `make audit` (Proofing 0) and `make coherence-audit` (Proofing 1)
- The Prolog rule engine, schema-locked predicates, and parser scaffolding

LodgeiT Labs has open-sourced its own implementation as the reference example for this pattern (see "Reference implementation" below). You're free to fork, copy, ignore, or rewrite from scratch.

---

## A 90-minute experiment

If you want to see whether this pattern fits your workflow, try this sequence:

**Minutes 0–15: stand up an empty Brain.**
1. Create a new private git repo. Call it `<your-name>-brain` or `<team-name>-brain`.
2. Add five files at the root: `SOUL.md`, `IDENTITY.md`, `USER.md`, `AGENTS.md`, `MEMORY.md`.
3. In each file, write 5–10 lines about what it represents. Be specific. Be opinionated.
4. Commit. Push.

**Minutes 15–45: write three real architectural decisions.**
1. Make a `PROJECT_NOTES/` folder.
2. Pick three real architectural decisions from your current legacy system — choices that took weeks to make and that nobody outside your team understands.
3. Write each one as a separate markdown file: the decision, the alternatives considered, the constraints that ruled them out, the consequences. 100–300 words each.
4. Commit. Push.

**Minutes 45–75: point your agent at the Brain.**
1. Open your coding agent (Copilot Workspace, Cursor, Claude Code, OpenClaw, whatever you use).
2. Tell it: *"At the start of every session, read SOUL.md, IDENTITY.md, USER.md, and AGENTS.md from this repo. Then proceed."*
3. (For some agents, this means adding the repo to its workspace context; for others, putting the instructions in a `.cursorrules` / `CLAUDE.md` / equivalent file. The mechanism varies; the principle doesn't.)

**Minutes 75–90: ask it three questions you've previously had to re-explain every session.**
1. *"Why did we choose X over Y for the order pipeline?"*
2. *"What's our deployment sequence for staging?"*
3. *"Walk me through the gotchas in the SOAP client."*

If the agent now answers from the Brain — citing the nodes you wrote — you've validated the pattern. If it doesn't, you've learnt something about your agent's context handling, which is also valuable.

Layers 4–6 (the proofing tiers) are deliberately out of scope for the 90-minute experiment. Adopt them once you've felt the difference Layer 1 makes and decided you want to commit harder.

---

## Worked example: Proofing 0

The reference Brain anchors every canonical PROJECT_NOTES node with two YAML frontmatter fields:

```yaml
content_hash: "sha256:38263ba4..."   # SHA-256 of the canonical body region
helm_mutations:
  - id: "mut-2026-04-15-001"
    timestamp: "2026-04-15T03:42:11Z"
    actor: "ClawDog"
    authority: "user:andrew"
    justification: "Initial node creation."
    previous_hash: null
  - id: "mut-2026-04-22-001"
    timestamp: "2026-04-22T11:14:09Z"
    actor: "ClawDog"
    authority: "user:andrew"
    justification: "Updated rate table for FY2026."
    previous_hash: "sha256:e9b14a..."
```

A `make audit` target runs three checks:

1. **Schema validation.** Every node's frontmatter parses against a Pydantic model. Required fields present, types correct, enums respected.
2. **Content-hash recomputation.** For every node, recompute SHA-256 over the canonical body region (delimited by a `<!-- HASH BEGIN -->` / `<!-- HASH END -->` pair, or the whole post-frontmatter body, depending on convention). Assert it equals the stored `content_hash`. If not, the gate fails with the offending file path and the diff.
3. **Mutation-ledger continuity.** For each node, walk `helm_mutations[]`. The last entry's `previous_hash` (or `null`) must match the recomputed prior hash. Any gap means a mutation was made without being recorded.

Same logic runs as a pre-commit hook (so you find out *before* you push) and again in CI (so a bypassed pre-commit hook can't sneak past).

**What this catches in practice:**

- An agent edits a `PROJECT_NOTES/` node and forgets to bump the `content_hash` → pre-commit fails, the agent retries with the recomputed hash + a new `helm_mutations[]` entry.
- A reviewer accepts a PR that *looks* like only the body changed, but actually flipped a metadata field silently → CI fails before merge.
- Six months later you want to know "when did this rate change?" — `git log` over the file plus the embedded ledger gives you the answer cryptographically, not narratively.

The Zero-Hallucination Law lives or dies at this layer. Without it, the rest of the Brain is built on sand.

---

## Worked example: Proofing 1

The reference Brain's deterministic-closure tier is wired through three commands:

```
$ make coherence-audit
[1/2] Regenerating coherence_kb.pl from markdown sources...
      MEMORY.md: bytes=14904, pointers=9, open_threads=23
      INFOVERSE_PROTOCOL.md: version=v3.4.0
      GLOBAL_NOTES: mutations=136
      memory/: files visited=62, lessons emitted=25, citations=47
      git log: commits scanned=50, mc-mutations found=3
      wrote 18223 bytes (sha256:38263ba4...)

[2/2] Running Tier 1 narrative-layer audit...
[w1] OK    Dangling lesson citations
[w2] OK    MEMORY.md ceiling discipline           (14904 / 16384 bytes, 91%)
[w3] OK    Carryover index/header divergence
[w4] OK    Stale Open Thread claims
[w5] OK    Protocol version pointer drift
[w6] OK    Unregistered/malformed mutations
[w7] OK    Status lattice violations

Passed: 7  |  Failed: 0
Verdict: COHERENT.
```

That's the green path. The interesting paths are when it goes red.

### Loop 1 — W3 fires on three real carryover divergences (PRs #89/#90)

The audit was wired up, then immediately fired:

```
[w3] FAIL  Carryover index/header divergence (3 finding(s))
        urn:lodgeit:carryover:2026-04-28-l402-restart-carryover
            index=resolved, file=active
        urn:lodgeit:carryover:2026-04-29-coherence-tier1-carryover
            index=resolved, file=active
        urn:lodgeit:carryover:2026-04-29-tier1-execution-kickoff-carryover
            index=resolved, file=active
```

These were real drifts. The MEMORY.md index had been curated to mark each carryover as resolved, but the carryover files' own `**Status:**` headers had never been updated to match. A human eye had skimmed past the divergence three times. The Prolog audit found all three on its first run.

PR #90 reconciled the headers. The next `make coherence-audit` ran clean.

### Loop 2 — W1 fires on 21 dangling lesson citations (PRs #91/#92)

The `MEMORY.md` standing-rules section and several daily logs cited `Lesson #N` for several values of `N`. The lesson-registry parser was added; the audit immediately flagged 21 dangling citations:

```
[w1] FAIL  Dangling lesson citations (21 finding(s))
        cites_lesson(MEMORY.md, line=66, lesson_number=11) but no such lesson in registry
        cites_lesson(MEMORY.md, line=109, lesson_number=14) but no such lesson in registry
        ... (19 more)
```

Each citation referred to a lesson that had been *banked in prose* (e.g. `**Lesson #11 — Sign-off verification discipline.** ...`) inside daily logs but had never been promoted to the `memory/lessons.md` registry. The Prolog audit had effectively reproduced the manual audit a human did the day before, which had concluded the same 21 lessons were missing.

PR #92 promoted 14 of the 21 to the registry, with verbatim sourcing (every promoted lesson had explicit "banked as Lesson #N" provenance in its original site). The rest were narrative-only and didn't warrant elevation. The next `make coherence-audit` ran clean.

### Loop 3 — the gate refuses to let a bad PR land

After Proofing 1 was switched to blocking (PR #93), the next attempted PR included a routine MEMORY.md curation that incidentally removed a lesson registry entry. The PR opened. CI ran. CI failed with W1 dangling citations. The PR could not merge. The author (the agent itself, in this case) noticed the contradiction in the same breath as acknowledging it, restored the entry, and re-pushed.

**The structural sight reproduces what humans see when they look carefully — then it does it on every CI run, forever.** That is the property GitHub-managing developers buy when they adopt Proofing 1.

---

## What it costs

| Resource | Cost |
|---|---|
| Disk space | Negligible. A mature Brain with hundreds of nodes is typically a few MB. |
| Cloud spend | $0 for the experiment tier. Optional later (CI runners, hosted runtime). |
| Per-developer fee | None. The pattern has no licence. |
| Discipline | The real cost. Brains decay if nobody maintains them. The proofing tiers reduce — but do not eliminate — the discipline cost. |
| Setup time | 90 minutes for Layer 1; one day for Proofing 0; one day for Proofing 1. |

---

## What it gives back

Eight concrete benefits, each with a one-line example:

1. **Continuity across sessions.** *"Pick up where we left off on the migration; the daily log is in `memory/2026-04-25.md`."*
2. **Decision archaeology.** *"Why did we choose SQL Server in 2018? See `200_decisions/2018_db_choice.md`."*
3. **Runbook fidelity.** *"Run the staging deploy. Use the runbook exactly; don't improvise."*
4. **Convention enforcement.** *"All commits must follow the prefix convention in standing rules. Reject anything that doesn't."*
5. **Onboarding acceleration.** *"New senior engineer joining; point them at the Brain README and they'll understand the system in a day, not a month."*
6. **Audit trail.** *"Every change to architectural metadata is recorded in the mutation ledger with author and timestamp; you can reconstruct any state in history."* (Proofing 0)
7. **Coherence guarantee.** *"The Brain cannot land a PR that contradicts what it claims about itself; the audit blocks merge."* (Proofing 1)
8. **Tri-state CI.** *"Green = the audit ran and was happy. Red = the audit ran and found drift. Yellow = the audit could not run; the gate is broken. We can never silently mistake (3) for (1)."*

Benefits 6–8 are the ones GitHub-managing developers care about: they translate into PR-level guarantees you can put on your status page.

---

## What it costs you if you skip it

Honest version: not adopting the Brain Pattern is fine if your team is small, your turnover is low, and your agent use is light. The cost is not catastrophic; it is *cumulative*. Specifically:

- Your agent re-derives team context every session and gets it slightly wrong each time.
- Architectural decisions live in people's heads and walk out the door when they leave.
- Onboarding takes weeks of pair-programming because nothing else is canonical.
- Agent-suggested refactors occasionally contradict decisions made years ago, and you only catch it in code review (or, worse, in production).
- Your agents leak proprietary context into public artefacts because nothing is gating egress.
- Your knowledge base rots silently — the index claims one thing, the files say another, and nobody notices for months.

Whether that's worth a 90-minute investment for Layer 1 (and two more days for Proofing 0 + 1) is your call.

---

## Common objections

**"We already have Confluence."**
Confluence is for humans browsing manually. A Brain is for agents reading programmatically every session. They are not substitutes. You can mirror Confluence content into a Brain (and many teams do), but the Brain is the source the agent actually reads — and the source the audit gate runs against.

**"We already have ADRs."**
Good. ADRs are a strong start on Layer 3. Move them into the Brain, add frontmatter, run them through the schema validator, and you've upgraded them from one-shot historical records to durable agent context. Add Proofing 0 and they're cryptographically anchored. Add Proofing 1 and the audit will catch when an ADR's "decision" diverges from its "consequences" section.

**"We already have `.cursorrules` / `CLAUDE.md` / `.github/copilot-instructions.md`."**
These are vendor-specific Layer-1 files: persona + scope, in a single fixed-format file. They're a prefix of the Brain pattern. Switch vendor and you start over. The Brain pattern is what you build when you don't want to start over.

**"This sounds like over-engineering for legacy maintenance."**
For greenfield work it might be — though even then, Layer 1 pays for itself in 90 minutes. For legacy systems — where institutional knowledge is the asset, not the code — it's the opposite. The pattern formalises what your senior engineers already do informally; it just makes the agent able to participate. Proofing 1 is overkill for a five-person greenfield team. It pays for itself the first time it catches a knowledge-base drift in a thirty-person team running a multi-year migration.

**"We can't store private knowledge in a public format."**
The Brain is a *private* repo. Layer 5 (the egress filter) exists precisely to control what, if anything, ever becomes public. The pattern is designed for private-by-default knowledge with deliberate, gated publication.

**"What if we want to change agents later?"**
You change agents. The Brain is markdown in git; it has no vendor coupling. Every coding agent can read markdown.

**"Why Prolog for Proofing 1? We're a Python shop."**
Three reasons. (1) The audit rules read like the property assertions they are: `dangling_lesson_citation(File, Line, N) :- cites_lesson(File, Line, N), \+ lesson(N, _, _, _).` That's directly readable as "a citation is dangling iff it cites a lesson that doesn't exist". (2) SWI-Prolog is small, fast, scriptable from Make, and ubiquitous on Linux. (3) The cost of writing the same audit in Python ends up being larger and uglier — you reinvent unification, query planning, and the "rule found nothing" vs "rule failed to evaluate" distinction. Take the Prolog. The KB and rules together are <800 LOC in the reference Brain.

**"How does Proofing 1 handle false positives?"**
The audit is shape-driven, not literal-string-driven. When false positives surface (and they will), the fix is usually a tightening of the parser's classifier — e.g. "treat headings under `## Resolved Open Threads` as historical-scope, not current-scope" — or a tightening of the rule clause-shape. We've shipped two such tightenings in the reference Brain (`section_classifier.py` and `clause_shape_classifier.py`) and the harness has parity tests that fail loudly if either falls behind the schema.

**"What if the audit takes too long to run?"**
In the reference Brain — with ~150 facts, ~300 LOC of rules, and no indexing optimisation — the full audit runs in <500 ms. SWI-Prolog will scale a long way before this becomes a real concern.

---

## Reference implementation

LodgeiT Labs runs this pattern in production for the development of its open-source accounting and tax compliance systems. The public-facing pieces of that implementation are:

- **The Kit** — `github.com/lodgeit-labs/clawdog` — the open-source classification engine produced from the Brain.
- **This document** — `github.com/lodgeit-labs/brain-pattern` — the pattern as practised, vendor-neutral, for adoption by other teams.

The Brain itself is private (it contains LodgeiT-specific operational knowledge), but the *pattern* is open. Patterns travel; implementations don't.

LodgeiT's domain is highly deterministic — accounting algebra, statutory tax law, regulatory taxonomies — so the pattern is tuned for *zero-hallucination* in those domains. For legacy software development, the same machinery applies with different domain-specific guardrails (e.g. "build commands must match the runbook exactly" for the W-rule set, rather than "tax rates must match the statutory table"). The shape is identical.

---

## Where to go next

If you experiment and the pattern fits, the next steps are:

1. **Add Proofing 0 (Layer 4).** Without it, the Brain corrupts under multi-author load. Take a look at the reference implementation; lift the scripts.
2. **Define your standing rules.** What must your agent never do? Write those down.
3. **Decide on a Brain topology.** One Brain per developer? One per team? One per product line? Brains can `git submodule` other Brains.
4. **Decide on egress discipline.** When does Brain content ever become public? Define that path; gate it.
5. **Add Proofing 1 (Layer 6) when you outgrow eyeball audits.** Start with one or two rules — a ceiling check, a dangling-citation check — wired into a non-blocking CI step. Watch them fire on real drift. Flip to blocking only when the rule set is stable.
6. **Iterate.** Brains get better with use. Yours will look different from anybody else's after six months. That's correct behaviour.

If you'd like to discuss the pattern with the team that built it, the LodgeiT Labs maintainers are reachable via the GitHub issues on this repository.

---

## Licence

This document is published under Apache 2.0. The pattern itself is unencumbered — it is just a design.

---

*Authored by ClawDog (LodgeiT Labs' resident agent) on behalf of the LodgeiT engineering practice. ∮*
