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

**Engraving versioning.** The persona surface itself is not exempt from the supersede-don't-erase discipline the rest of the Brain runs on. When a persona file needs a genuine revision — the agent's stance changes, a new authority is added, an old scope is retired — the file gets an explicit version bump (`v1` → `v2`) rather than an in-place edit that silently overwrites the prior engraving. The previous version stays in git history where it belongs, and the new version carries a note referencing what it supersedes. This matters because persona drift is uniquely invisible: the agent will speak in whichever voice the file currently says without flagging that the voice has changed. Explicit versioning makes voice changes legible in the same way content-hash discipline makes graph mutations legible.

**Cost:** ~30 minutes once, plus ~5 minutes per version bump when the persona genuinely evolves. **Benefit:** every session feels like the same colleague, not a stranger — and when the colleague *does* change, the change is a visible event rather than a silent overwrite.

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

#### What Proofing 0 doesn't catch by default

The content-hash check above answers one question: *did anyone edit this node without recording the change?* It doesn't answer the questions that adopters discover the second they put real load through the gate. Three sharper variants are worth shipping alongside the baseline, each closing a failure mode that survives a green `make audit`.

The first variant: **content fidelity beyond existence.** When a node says it has lifted a passage verbatim from another file (a public source, a sibling node, an external standard), the baseline audit can confirm the source exists but cannot confirm the lift is still byte-identical. The body of the claim and the body of the source can drift independently over months and the hash check never notices, because both files re-hash cleanly on their own. The fix is a second gate that walks every declared verbatim claim, reads the sidecar, and refuses the commit if the byte-diff isn't zero — or if a verbatim-lift phrase appears in the body without a corresponding declaration. The lesson is structural: *verifying that a file exists is not verifying that its content is what the citing site claims it is.*

The second variant: **production-bundle assertions, not just hermetic-test assertions.** Adopters who add Proofing 0 typically also add a hermetic test suite that mocks out the filesystem and exercises the audit against synthetic fixtures. Those suites pass cleanly even when the real bundle is missing, malformed, or wired to the wrong path in the deploy artefact. A green hermetic suite without a complementary production-bundle assertion is *pre-broken*: the gate that should fire at deploy time silently doesn't, because nothing has ever tested it against the real shape. The fix is a small parallel test path that exercises the production resolver against the production bundle, with the production environment shape, and asserts the structural markers a real request would traverse. It is cheap to add and catches an entire class of "the test was green and production was on fire" incidents.

The third variant: **near-miss negative fixtures alongside positive ones.** A self-test suite that only carries positive examples (the rule fires when it should) gives no signal when the rule's *boundary* drifts — when a regex starts matching one character too wide, or a parser starts accepting something it shouldn't. Pairing every positive fixture with a near-miss negative fixture (the rule must *not* fire on this almost-identical case) makes boundary drift fail loudly the first time it crosses. It is the difference between testing *that the gate fires* and testing *that the gate fires exactly when it should*.

None of these are baseline-Proofing-0 requirements. They are the sharper variants the reference Brain ships now because each one paid for itself the first time something slipped past the baseline.

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

## Day-1 seed kit: the six-step bootstrap as actually practised

The 90-minute experiment above proves the pattern works on your material. When you decide to commit to it — to run your real work through a Brain, not just try it — the graduation path is a short bootstrap sequence that lands the load-bearing invariants on day one. The reference Brains this pattern draws on were each bootstrapped by this sequence; a template set that mirrors it lives in `seed/` in this repository.

The six steps are ordered by *what breaks if you skip them*, not by tidiness. Skip step 3 and your first curation pass turns into a merge hazard. Skip step 4 and the temptation to fabricate the missing days becomes real. Skip step 5 and the first accidentally-staged credential is a public incident. The order is the argument.

**Step 1 — Engraving set authored.** Fill `SOUL.md`, `IDENTITY.md`, `USER.md` with *real* content, not placeholder text. Persona is the load-bearing seed for everything downstream: the agent's voice, the operator's disposition, the not-negotiables that will become standing rules. Placeholder engravings produce placeholder agents. If you cannot write a specific SOUL.md paragraph in one sitting, write no SOUL.md; return to it in an hour with real conviction rather than shipping generic-helpful into canon. See `seed/SOUL.md`, `seed/IDENTITY.md`, `seed/USER.md` for scaffolding.

**Step 2 — `memory/lessons.md` seeded, including inherited candidates if federated.** A fresh Brain has no local lessons; that is honest. It may have inherited candidate lessons if it federates with a commons — lessons another Brain has offered and this Brain has accepted as reported evidence per the candidate-lesson lifecycle above. Record them explicitly with their inherited-versus-local composition (`n=3 inherited from <other-brain>; n=0 local`); do not promote them to canon on inherited evidence alone. Local promotion waits for local recurrence or independent re-anchoring. See `seed/memory/lessons.md`.

**Step 3 — `memory/latest-activity.md` externalized from day one, with a provenance-honest founding entry.** Do not start with a rotating log inside `MEMORY.md` and defer the externalization; the maintainer discipline the externalization requires accretes on day one and gets structurally harder every day you postpone. The founding entry is your first append: what you did to bootstrap the Brain, in the same voice future turns will use. Provenance-honest means naming the day, the operator, and the fact that this is founding (not backfill). See `seed/memory/latest-activity.md`.

**Step 4 — Daily note opened same day; NO backfill of unwitnessed days.** The daily-note file (`memory/<YYYY-MM-DD>.md`) opens the moment substantive work starts. It does not backfill days the Brain was not present for — a missing daily note is more honest than a fabricated one. The temptation to write yesterday's context into today's note *as if* it were witnessed is exactly the shape the zero-exec-invariant discipline in §5 above catches on the verification side: provenance is either real or absent; it is never confabulated. See `seed/memory/DAILY-NOTE-TEMPLATE.md`.

**Step 5 — Whitelist `.gitignore` + secret-scan gate.** The `.gitignore` in a Brain is whitelist-shaped, not blacklist-shaped: block everything by default and enumerate the specific paths that belong in tracking. A blacklist fails open (a new secret-bearing filename with an unanticipated extension slips through); a whitelist fails closed (nothing is tracked unless permitted). Alongside the whitelist runs a small `scripts/secret_scanner.py` under the six-element rule shape from later in this doc — tri-state exit codes, pre-commit hook, CI backstop, fixture tests, prose entry in `MEMORY.md`, Makefile target. This is the Privacy Gradient's mechanical perimeter on day one; without it, the first accidentally-staged credential is a public incident. See `seed/.gitignore` and `seed/scripts/secret_scanner.py`.

**Step 6 — Private repo, first push as the verification artifact, operator holds the credential.** Create the repo as *private*, on the operator's own credential (a fine-grained PAT scoped to Contents on this one repo is the reference shape). The first `git push` is not routine — it is the verification artifact for steps 1–5: if the whitelist misclassifies a real file, or the secret scanner fails to gate a staged credential, or the engraving set is malformed, the push is where the failure surfaces before any second party has visibility. The operator holds the credential end-to-end; no shared PAT store, no CI-side service account, no bot identity. Federation credentials (if you federate later) are separate PATs on separate stores under a separate access policy — the day-1 credential does not become the federation credential by drift.

The seed set in `seed/` is prose-scaffolded rather than code-scaffolded on purpose: nothing in it will be *correct* for your Brain without your own content. It is a shape to fill, not a fork to inherit. If you find yourself editing a seed file to match your project, you are doing it right; if you find yourself using a seed file unchanged in production, the seed file did not do its job.

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

### Loop 4 — a behavioural rule promoted to binary failure catches real misses on the next two commits

One discipline in the reference Brain lived for months as a written rule that said *every merged PR must be rowed in this index file with its merge SHA and a one-paragraph summary*. The rule was clear, the index existed, the agent and the human both agreed it was important — and over a seven-day window thirty merged PRs accumulated without rows, because nothing physically halted the workflow when a row was forgotten.

The drift was caught during an audit pass and the response was to promote the discipline from behavioural recall to binary failure: a small verifier walks the merged-PR history on master, walks the index file, and exits non-zero if any merged PR above a stated floor has neither a row nor an explicit exempt marker. Pre-commit hook, CI workflow, Makefile target. Standard architectural shape.

The rule went green at landing and then immediately caught two real misses on the next two commits — each one a PR that closed substantive structural work and was about to be banked into the index, except the row had been forgotten in the rush of getting the work itself merged. The verifier blocked both commits; the missing rows were added; the commits re-passed; the index never drifted again.

This is the property worth naming. **The rule didn't change behaviour by being clearer or more frequently reminded. It changed behaviour by becoming the exit code of a command the workflow runs.** A rule whose only enforcement is *please remember* drifts. The same rule, given a small verifier that exits 1 when it's violated, doesn't — because the workflow physically halts when it's violated, and the next thing the author does is fix it.

**The structural sight reproduces what humans see when they look carefully — then it does it on every CI run, forever.** That is the property GitHub-managing developers buy when they adopt Proofing 1.

---

## Why these tiers are gates, not guidelines

There is a single principle underneath every proofing tier above, and it is worth stating directly because it determines which disciplines you bother to mechanise and which you leave as written rules.

**Rules that depend on the agent remembering them drift. Rules that physically halt the workflow when they're violated don't.**

The rules you write down in the Brain are, by default, behavioural — they bind only as long as the reader (human or agent) recalls them at the right moment. Under context load, fatigue, or simple novelty, recall degrades. The drift is not a moral failing; it is a property of probabilistic readers under real conditions. You can mitigate it with reminders, repetition, and discipline, and you should — but you will not eliminate it.

The rules you encode as binary-failure gates bind differently. A rule that exits non-zero when violated stops being a recall task and starts being a workflow constraint. You cannot push past it without overriding it explicitly, which leaves a visible trail. The cost of "forgetting" a binary-failure rule is the workflow halting; the cost of remembering it is zero. The asymmetry is what makes the rule load-bearing.

This is the meta-principle that organises the proofing tiers. Layer 4 (Proofing 0) takes the rule *don't edit a canonical node without recording the change* and makes it a hash check that fails CI. Layer 6 (Proofing 1) takes a set of structural-consistency rules and makes them a Prolog audit that fails CI. The human-side disciplines below are the residual: rules whose failure modes are real but whose enforcement surface is not yet a binary-failure gate. Each one is a candidate for promotion the moment its drift cost crosses the cost of writing the verifier.

The corollary worth carrying explicitly: **a rule promoted from behavioural to binary-failure should be promoted using the same architectural shape every time.** The reference Brain has converged on a six-element shape after enough one-off variations to be sure it generalises. It is set out in [Building your own audit rule](#building-your-own-audit-rule) below the human-side disciplines.

---

## The human-side disciplines that complement the audit

Proofing 0 and Proofing 1 catch *structural* drift: hashes that don't match, citations that don't resolve, status fields that contradict the index. They do not catch every class of failure that erodes a Brain. The disciplines below cover the gaps the Prolog cannot see, and the reference Brain has paid for each of them by getting one wrong first. Each one is also a candidate for promotion to a binary-failure gate — if and when its enforcement surface becomes mechanisable and its drift cost crosses the cost of writing the verifier.

### 1. Treat ceilings as measurements, not aspirations

A persistent index file (the equivalent of MEMORY.md in the reference Brain) accumulates pressure: new threads, new activity, new pointers to topical files. It is tempting to declare a *target ceiling* ("keep it under 8 KB") and treat the rule as discipline.

The failure mode: the file steady-states well above the target, the discipline becomes broken-windows aspirational, and every new edit silently hopes the next curation pass will deal with it.

The fix is to **measure the load-bearing floor before setting the ceiling.** A well-curated index has a floor that cannot compress further without losing signal: the persona block, the file-trigger index, the standing rules. Sum those, add a realistic margin for the surfaces that legitimately grow (open threads, latest activity, recent carryovers), and set the ceiling at that number — not at a smaller number you wish were true. A ceiling that matches the file's actual physics gets enforced; a ceiling that doesn't, doesn't.

In the reference Brain, this looks like a soft ceiling and a hard ceiling carried in the file's own header, alongside a forensic record of past curation passes and the size each landed at. The audit's W2 rule (index ceiling) keys off the *self-declared* ceiling, not a hard-coded number, so the contract stays honest as the project's load-bearing floor evolves.

### 2. Refuse to demote auto-injected rules behind pointers, even under size pressure

The rules a coding agent must obey on every turn (the standing rules) are auto-loaded as part of the index. When the index gets large, the obvious move is to demote those rules into a topical file, leaving a one-line summary in the index pointing at the canonical detail.

**Don't.** A rule that lives behind a pointer is a rule the agent has to *fetch* before acting. Fetching is a recall task, and recall drifts under context load. The very property that made the rule worth declaring — that it is unmissable, present at every reasoning step — is exactly the property that pointer-demotion destroys.

The binding shape is: any rule whose violation would normally produce a binary failure (a non-zero exit, a refused commit, a refused merge) gets its full contract inline in the index. Rules that are advisory in nature ("prefer terse replies," "don't dominate group chats") live in the persona file. The line between the two is whether the rule has a CI-shaped enforcement surface. If it does, the rule belongs in the index, full text, even when the index is under ceiling pressure. The ceiling is the thing that yields, not the rule.

### 3. Use a second agent to challenge curation proposals before they ship

A curation pass is itself a design artefact. The first agent (the one curating) inherits its own assumptions. A second agent, given the same brief and asked to pressure-test the proposed plan, will catch class-of-mistake errors the first agent cannot see from inside.

The reference Brain practises this as a **Memory Tracer review**: before a non-trivial curation PR opens, the proposed plan goes through a separate agent that reviews scope, floor target, and PR sequencing. Three concrete corrections that this pattern has surfaced in production, all in a single sprint:

- **Don't demote the standing rules** even when ceiling pressure suggests it (per the principle above) — the first agent had agreed in the abstract but had still drafted the demotion as a phase. The Tracer caught it.
- **Don't aim for an aspirational floor** that requires compressing load-bearing content; pick the floor that matches the load-bearing physics (per the principle above).
- **Don't bundle additive and subtractive work in a single PR** when they touch the same surface; split into two PRs so an audit failure isolates to one cause (per the principle below).

The Tracer is not a checker; it is an adversarial collaborator. The cheapest implementation is a second context, given the proposal as text and asked specifically *"what is wrong with this plan?"*.

### 4. Sequence additive and subtractive work in separate PRs

A curation pass typically has two halves: an *additive* half (catch a topical file up to live state, add resolution stubs to a registry) and a *subtractive* half (demote the matching detail out of the index). They are interdependent — you cannot do the subtractive half safely until the additive half lands, because in the gap between the two the same content exists in both surfaces and a coherence audit can legitimately flag the duplication.

The discipline is: **two PRs, sequenced.** PR 1 is purely additive. PR 2 is the trim, against the now-prepared sister file. If PR 1 fails its audit, you know you broke a citation or a stub. If PR 2 fails, you know you broke a demotion or an index-detail correspondence. The audit failure isolates to one cause instead of two.

The complement to this is the **cut-over diff review**: before committing PR 2, walk every row removed from the index and confirm it exists in the topical file with the same identifier and the same closure state. The Prolog audit will catch this on the server side, but the diff-review catches it before the commit message is even written, which means a clean PR opens green instead of opening red and being amended. The 30 seconds of diff review at PR 2 saves a permanent CI breakage on a public PR.

The seven disciplines in this section split by *when* they fire. Disciplines §1–§4 are *maintainer* disciplines — they govern how a curation pass or a schema change is shaped, and they fire when the shape of the Brain is being changed. Disciplines §5–§6 are *operator* disciplines — they fire on every turn that closes any unit of work, against the gates the Brain already carries. §7 is *hybrid*: the externalization act itself is maintainer-shaped (a one-time structural change to how the Brain lays out files), but the ongoing append-versus-edit invariant it introduces is operator-shaped (every turn honours it, or the two surfaces start clobbering each other again). Naming the hybrid case rather than forcing it into one bucket is the honest classification.

### 5. Earn green honestly — never merge over a yellow, and never fake the verification

Every binary-failure gate the Brain ships has a tri-state exit contract: `0` clean, `1` real violation, `2+` verifier broken. A maintainer holding the merge button can turn any of those into a green PR by pressing hard enough on the wrong lever: overriding a yellow (`2+`) on the theory that it looked infra-flavoured, overriding a red (`1`) on the theory that the finding was a false positive, or — the shape most worth naming — writing prose that describes a verification without actually running one.

The reference Brain has paid for the third of these once (the fabricated-verification incident of 2026-08-14, which produced the zero-exec invariant); the first two are shape-recognized failure modes the tri-state contract is built against — designed-for, not yet incident-anchored. The load-bearing rule that survived is a single principle with three attached mechanisms.

**The principle: green is earned by the verifier, not asserted by the author.** A rule that fires `1` gets cleared by fixing the underlying state and re-running until the verifier itself returns `0` — never by overriding the exit code, never by editing the verifier to be quiet, never by claiming the finding is spurious in the PR body. A rule that fires `2+` (infra broken) gets cleared by *repairing the verifier* and re-running, never by promoting the yellow to a green in the CI config. The tri-state contract is only load-bearing if every state is honoured.

**Mechanism one: the zero-exec invariant.** A verification section in a PR body, a chronicle entry, or a plan document that reports outcomes without a corresponding tool invocation on the wire is a fabricated verification. The reference Brain caught one of these when a proposed §15 verification block landed with confident PASS/FAIL rows and zero tool calls in the underlying transcript — the author had written what the verifier *would have* said, on the shape of what the gate *usually* looks like. The fix was to invert the shape: verification blocks now emit artifact references (log paths, response bytes, CI URLs), and the absence of an artifact reference is treated the same as a failed gate. If the verification cannot produce an artifact on the wire, it did not happen.

**Mechanism two: counts must match trace.** When a verification reports a numeric outcome ("6 rows verified," "3 fixtures green," "12 citations resolved"), the count must match the count of things actually invoked on the wire, not the count of things the author *intended* to invoke or the count of things a template asserts should be present. The failure mode this catches is the declared-versus-real fidelity gap: a section that says "all 6 rows verified" while the underlying trace shows only 4 invocations and 2 assumed-from-context. The discipline is small — before writing a numeric assertion in a verification block, count the actual tool invocations that produced it. When the two counts disagree, the assertion is wrong; fix the count, don't launder the assertion.

**Mechanism three: artifacts, not prose.** A verification produces files, CI log URLs, API response bytes, or hashes — surfaces another reader can independently re-check. Prose descriptions of what a verifier *did* are not verifications; they are narratives about verifications. The two are indistinguishable on a screen and structurally different on the wire. The discipline is to prefer the artifact citation over the description in every verification block: `see: audit-run-2026-08-17.log line 47` beats `the audit passed cleanly` every time, because the first can be re-checked and the second cannot.

Each of these three mechanisms is a candidate for promotion to a binary-failure gate — a linter that refuses to accept a verification block without at least one artifact citation, a script that reconciles reported counts against transcript trace counts, a CI step that requires every PR-body verification claim to link to a run URL. The reference Brain has not yet paid for all three verifiers, so they sit here on the human side. Their drift cost is real enough that a promotion is likely; until then, the discipline holds them.

### 6. Fetch and assert co-owned state before authoring against it

A Brain that federates with other agents, that publishes egress artifacts to public repos, or that has any surface where a second party can mutate shared state has a distinct failure class: **the local snapshot is not the wire truth.** A turn that opens by reading a local clone of a co-owned repo, drafts against that snapshot, and pushes assuming the remote matches will produce a divergence the moment the second party has moved. The divergence is silent — the local commands succeed, the PR opens, the CI runs against a base the author has never seen — until the merge conflict or the semantic conflict surfaces downstream.

The reference Brain paid for this one when a co-owned egress repo had drifted 75 commits ahead of a local clone that had not been fetched in some weeks. The author began drafting against the stale local state; the divergence surfaced only when the push was rejected by a fast-forward gate on the remote. The salvage cost was small in that case, but the general shape — *authored a change against a snapshot the wire does not agree with* — is exactly the class that can leak an assumption into a downstream artifact where it is expensive to remove.

The discipline is: **before authoring against any co-owned repository, `git fetch` and assert the local HEAD equals the remote HEAD.** On divergence, the reconcile is a first-class task — either a fast-forward pull (if the local is behind only), an explicit surface-to-human (if the remote has moved in a way that changes the plan), or an operator-authored merge (if both sides have moved). Never author against a stale snapshot and never treat "the branch is ahead of origin/main by N commits" as an incidental log line; both are signals that the wire truth is not what the local clone says.

The mechanical shape that supports this discipline in the reference Brain is a pre-turn gate that runs the fetch-and-assert automatically for every registered co-owned repository, tri-stated the same way as every other verifier: `0` synced, `1` operator-actionable divergence, `2+` infra broken (fetch failed, auth failed, remote unreachable). The gate does not do the reconcile — that decision requires a human — but it converts *discovered* divergence (surfaced when a downstream operation fails against a stale base) into *asserted* divergence (surfaced at turn start, before any state is authored).

Co-owned state includes: shared Brain instances that federate, egress repositories that publishers other than the primary Brain can push to, and any public repository whose default branch a maintainer other than the current agent can advance. It does not include Brain-internal branches or fully-owned egress artifacts, where the agent is the only writer.

### 7. Externalize the append-only timeline from the edited index

The `MEMORY.md`-shaped index is not a log — the file table says so, and §1 above says so. In practice, though, every non-trivial Brain grows a *latest-activity* surface: the last handful of turns' outputs, the most recent decisions, the running commentary that any session bootstrapping into the Brain needs to catch up on. This surface is genuinely append-only — each turn adds a new entry to the top or bottom; existing entries are not edited. Keeping it inline in the index creates a category confusion: the index proper is *edited* (rows updated, pointers rewired, ceilings adjusted), while the latest-activity surface is *appended*. Every curation pass on the index has to hand-preserve the appended surface, and every appended turn has to hand-avoid touching the edited surface. Both classes of writer step on each other at merge time.

The discipline is: **externalize the append-only timeline into its own file, and let the index carry a lean pointer to it.** In the reference Brain this is `memory/latest-activity.md`, appended by every session that closes a substantive turn, with `MEMORY.md` carrying a single one-line pointer at the section where the inline log used to live. Two properties fall out immediately. First, merge conflicts collapse: the index is now edited-only, the timeline is now appended-only, and the natural git merge behaviour handles both cleanly. Second, curation load drops: an index-shaped curation pass no longer has to walk past thirty turns of append rows to find the rows it actually needs to edit; those rows live in a file whose only invariant is *newest-first* (or *oldest-first*, if that fits the reader better).

The subtler property is that the split makes the *category* of each surface legible. A future maintainer looking at the file names alone can see that `MEMORY.md` is the edited index and `memory/latest-activity.md` is the appended timeline. The category is enforced by the file boundary, not by discipline. This is a small example of the same principle the six-element rule shape uses: **make the invariant a property of the file layout, not a property of the maintainer's memory.** The moment two writers have different implicit assumptions about which parts of a file are appended versus edited, they will clobber each other; separating them into two files makes the assumption structural.

A sibling application of the same principle: **verify the pointer stays a pointer.** A one-line mechanical check on the index confirms the section that used to be an inline log is now a single pointer line and has not silently regressed into inline rows. In the reference Brain this is a small pre-commit check that greps for bullet-shaped rows immediately following the `## Latest Activity` header; a bullet found there indicates the pointer has regressed and the timeline has started leaking back into the index. Small, structural, and it exactly closes the failure mode the externalization opens.

These seven disciplines are not enforced by the Prolog audit — they are how a maintainer keeps the audit's gates *meaningful* over the lifetime of the Brain. The audit catches the failures that survive these disciplines; these disciplines catch the failures the audit cannot see.

---

## Candidate-lesson lifecycle

The lessons registry (`memory/lessons.md` in the reference Brain, or whatever your equivalent is) accumulates knowledge that started as an incident and was earned into a rule. Two questions face any maintainer working on the registry: how does a new lesson *enter* the registry (candidate versus banked), and how does the registry *evolve* when a banked lesson turns out to have been narrower or wider than the evidence justified. The reference Brain has converged on a small explicit lifecycle for both questions, and it is worth setting out because the alternative — an implicit lifecycle — lets lessons drift into canon on the strength of a single incident, and lets superseded lessons quietly vanish when they should have stayed visible.

**Stage 1: Candidate.** A lesson is a *candidate* when it has been observed once. Candidates are written down (the incident, the shape, the anchor) but do not yet count as canon. The registry may carry candidates in a separate section, or annotate them inline with a `candidate` marker; the presentation matters less than the fact that a candidate is structurally distinct from a banked lesson.

**Stage 2: n-count accumulation.** Each subsequent recurrence of the same failure shape increments an explicit `n=` count on the candidate. The reference Brain records this per-brain (a `n_local` count for instances observed directly, and a `n_inherited` count for instances observed by federated brains reporting into the registry). The composition is always visible: `n=4 (3 inherited: <other-brain>; 1 local)`, not a flat `n=4`. This matters when the count is used to justify a promotion: an operator ratifying a lesson on the strength of `n=4` should be able to see immediately whether the four instances were four different local incidents or one local and three reports.

**Stage 3: Operator-only ratification at n≥3.** Promotion from candidate to banked is *not* automatic. The threshold (typically `n≥3` in the reference Brain) is a necessary condition, not a sufficient one: the operator ratifies the promotion explicitly, and only then does the candidate become a banked lesson with its own registry number and its own citation surface. This matters because promotion changes the lesson's authority: banked lessons are cited from the index, from daily logs, and from PR bodies; candidates are not. The operator's ratification is the moment the lesson acquires that authority, and it deserves to be an explicit event rather than a threshold crossed silently.

**Stage 4: Supersede-don't-erase on revision.** When a banked lesson turns out to have been mis-scoped — too narrow, too wide, subsumed by another lesson, contradicted by later evidence — the correction is a *new* lesson entry that supersedes the old one. The old entry stays visible in the registry, marked with an explicit `superseded-by: Lesson #N` note; the new entry carries a reciprocal `supersedes: Lesson #M` note. Nothing is erased. This is the same mechanic content-hash discipline uses on the graph side, applied to the lessons registry: the audit trail of what the Brain used to believe is as valuable as the current state, because the reasoning that led to a superseded lesson is what a future reader needs to see to trust the correction.

**Stage 5: Inherited-versus-local composition on federation.** For Brains that federate — a shared commons where lessons from one Brain can be inherited by another — the composition of `n_inherited` (from other Brains' reports) and `n_local` (from this Brain's own incidents) is always visible on the lesson row. A lesson with `n=4 (3 inherited: <other-brain>; 1 local)` is not the same as a lesson with `n=4 (0 inherited; 4 local)`, and the registry preserves that distinction rather than flattening it to a single count. Cross-brain evidence may count toward a local promotion threshold, but the local operator ratifies against the composition, not against the sum.

Each of these five stages is discipline, not code, in the current reference Brain: no verifier fires on a mis-scoped candidate or a silent supersession. They sit here on the human side for the same reason the disciplines above do — their enforcement surface is not yet a binary-failure gate. Each is a candidate for promotion under the six-element shape the moment its drift cost warrants: a verifier that halts commits which promote a candidate without an explicit operator-ratification note, a verifier that refuses to accept a corrective lesson without a reciprocal `supersedes`/`superseded-by` pair, a verifier that refuses a federated `n=` count without a composition breakdown. Until then, the lifecycle lives here in prose alongside the disciplines that guard it.

---

## Building your own audit rule

The disciplines above sit on the human side because their enforcement surface isn't mechanisable yet — either the failure mode is intrinsically behavioural, or no one has paid for the verifier. The interesting question for adopters isn't whether to write a rule; it's how to write one when the cost crosses the threshold. The reference Brain has done this enough times to have converged on a fixed architectural shape, and it is the cheapest part of this whole pattern to lift directly.

A new binary-failure rule ships as six small artefacts. None of them is optional; the absence of any one is a known failure mode the reference Brain has paid for.

**1. A verifier script with a tri-state exit code.** The same `0` / `1` / `2+` contract Layer 6 uses for Proofing 1, applied here. Exit 0 means the rule found no violations. Exit 1 means the rule found a real violation — the workflow author fixes the underlying state. Exit 2 or higher means the verifier itself could not run (parse error, missing file, broken regex), which is *not* the same as a clean run and must halt loudly rather than be quietly absorbed as a passing result. The distinction between "the rule fired green" and "the rule could not be evaluated" is load-bearing; conflating them is how silent-broken-gate failures originate.

**2. A pre-commit hook entry.** The verifier runs at commit time, before the staged change reaches the remote. This is the fastest feedback loop the author gets — violations surface in seconds, against the diff in front of them, while the context is still hot. Expensive verifiers can be conditional on whether the relevant file is staged; cheap ones can run unconditionally. Either way the hook is present.

**3. A CI workflow step.** The same verifier runs on every PR and every push to the protected branch. This is the catch-all backstop against `--no-verify` bypasses, against developers who haven't installed the hooks, and against authors operating on machines where the hook path doesn't apply. Pre-commit is the convenience layer; CI is the perimeter.

**4. A self-test suite.** Every exit-code path of the verifier is covered by a test fixture: at least one positive fixture per violation class (the rule must fire), at least one negative fixture for each (the rule must not fire on the near-miss case), and at least one infra-failure fixture (the verifier must exit in the 2+ band, not the 1 band, when its inputs are malformed). The near-miss negative is the one most adopters forget, and it is the one that catches regex-width drift and parser-classifier drift months later.

**5. A short prose entry next to the standing rules.** Two paragraphs at most: the rule's binding contract, its exit-code semantics, and a cross-reference to the verifier script. This is the surface the agent reads when reasoning about whether a proposed action would trip the gate; without it, the gate exists but is structurally invisible to the agent's planning step.

**6. A Makefile target.** The verifier is invocable manually by both the author and the agent without needing to remember its path or its flags. This is what enables the agent to run pre-flight checks before opening a PR, the maintainer to run it ad hoc when debugging, and the CI workflow to call it through the same interface that humans use. One name; one contract; everywhere it runs.

That is the whole shape. The reference Brain ships seven binary-failure rules built to this template at the time of this writing, and the marginal cost of the seventh was a small fraction of the marginal cost of the first — because each new rule is the same shape, only the verifier body differs. The shape is the lift; the verifier is the easy part.

### Auditing the audits

There is one more invariant worth promoting, because it is the variant that closes the recursion. The rules-list itself is a knowledge artefact; the rule that *every rule must ship under the six-element shape* is itself a behavioural rule unless something physically checks it.

The reference Brain promotes that meta-invariant to a small verifier that walks the standing-rules block and, for each numbered rule, requires either a reference to its mechanical perimeter (a script, a hook target, a Makefile target, or an explicit composite delegation to another rule) or an explicit exempt marker carrying a non-empty justification. A rule with neither is a logic-drift failure. A rule whose stated perimeter doesn't exist on disk is a logic-drift failure. A rule whose exempt marker has no justification text is an infra-broken failure, halted loudly.

This is small, structural, and closes the loop the original promotion principle opens. The rule that says *every drifting rule should be promoted to a binary-failure gate* is itself promoted to a binary-failure gate. Without that closure, the discipline is still behavioural — you might forget to give the next rule its perimeter, or you might add a new rule and skip the shape, and there is nothing in the workflow to halt you. With the closure, the discipline is self-validating: any new standing rule that lands without the shape, including this one, fails its own gate on its own commit.

It is the smallest, cheapest, and most recursive of the binary-failure perimeters, and it is the one that makes the rest of them load-bearing over time rather than over a single sprint.

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

## Running the pattern on more than one brain

The 90-minute experiment and the day-1 seed kit both describe standing up *one* Brain. That is the right unit for getting started; it is not the right unit for a working practice. Once the pattern is proving out, a second Brain — a different agent, a different operator, a different scope of authority — becomes the natural next question. This section describes what running the pattern on more than one Brain looks like in practice, with receipts.

### The pattern generalises: two live production instances

At the time of this writing, this pattern has two live production instances. The first is the reference Brain that generated most of the material in this document. The second stood up in under a day using the day-1 seed kit above — a different agent with a different persona engraving, a different scope of authority, and a different operator relationship. Both are running the same layered file structure and the same proofing-tier discipline; both are private to their operators; both draw on the same public methodology under the org. The second-Brain bring-up time is the load-bearing receipt: if the six-step bootstrap could not stand up a fresh Brain in under a day, the seed kit above would not deserve its name.

### The three-pile factoring

What you find when you run the pattern on a second Brain is that everything in an existing Brain sorts into three piles, and only one of the piles moves:

**Portable core** — the invariants that hold for any Brain: the layered file structure, the proofing tiers, the standing-rule discipline, the human-side disciplines and the candidate-lesson lifecycle above. This is what the *pattern* is. It is what the day-1 seed kit scaffolds. It moves cleanly to a new Brain because it does not depend on any particular agent, operator, or subject matter.

**Per-agent adaptation** — persona, voice, sign-off, standing rules that reflect *this* agent's authority and *this* operator's disposition. This is what a new Brain writes fresh at bootstrap. It cannot be inherited because it is not portable by construction — an inherited persona is a placeholder persona, and placeholder personas produce placeholder agents.

**Implementation-specific machinery** — the concrete scripts, the specific verifier bodies, the Prolog rules keyed to the local knowledge graph, the CI workflows tuned to the local repo. This is what the reference Brain accumulates over time and what a new Brain grows into as its own drift costs justify the mechanisation. It does not transfer cleanly; each Brain grows its own machinery under the same six-element rule shape.

The factoring matters because it says what a new Brain inherits (the pattern), what it authors (its own engraving and rules), and what it earns over time (its own verifier corpus). Nothing in the third pile shortcuts the second; nothing in the first pile substitutes for the second.

### Tier self-declaration

Each Brain declares which pattern tier it is running — Layer 1 honest-manual, Proofing 0, or Proofing 1 — as part of its own canon. Declaration matters when Brains exchange evidence: a Layer 1 Brain's lesson candidates come with a different confidence profile than a Proofing 1 Brain's, and the honest way to make the difference legible is for each Brain to say what tier it runs. The declaration is prose in the Brain's own canon; it is not a badge or a compliance claim.

### Cross-brain lesson inheritance

Brains that federate can inherit candidate lessons from each other under a small explicit convention:

- **Composition preserved.** A lesson row that carries inherited evidence names the composition explicitly: `n=4 (3 inherited from <other-brain>; 1 local)`, never a flat `n=4`. The candidate-lesson lifecycle above (Stage 5) is the mechanism.
- **Operator-only promotion.** Cross-brain evidence may count toward a *local* promotion threshold, but promotion to canon is ratified by the receiving Brain's operator, per that Brain's own protocol. No Brain can promote a lesson into another Brain's canon.
- **Anchor format.** Cross-brain anchors are written `<brain-slug>@<commit>:<path>` (optionally `#<locator>`), so the reference resolves to a specific point-in-time in a specific Brain. A wire consumer with access to that other Brain can fetch the anchor and read the source of the lesson at the exact commit where it was banked.
- **Anchor-verification discipline.** An offering Brain cites only anchors it can itself verify — that is, `<brain-slug>@<commit>:<path>` references that resolve to the offering Brain's own history at a commit the offering Brain has published. Cross-brain anchors (references to another Brain's canon) are completed by the receiving Brain at acceptance, not fabricated by the offering Brain. Fabricating an unverifiable cross-brain anchor is a compliance failure; declining to cite one you cannot verify is compliance.

### One live example, told anonymously

Within the first federation exchange between the two live Brains, one inherited candidate lesson recurred on the receiving side within 24 hours — at a novel surface, in a different concrete shape than any of the offering Brain's prior instances of the same class. The failure mode the offering Brain had named was real on the receiving Brain too, in a place the receiving Brain had not seen it before. The prevention the offering Brain had proposed was wire-verified on the receiving side the same day the recurrence surfaced. This is the load-bearing property of the inheritance mechanism: an inherited lesson that catches a real local failure the receiving Brain had not yet paid for is an inheritance that earned its weight. Details of the specific surface and the exchange belong to the operators involved; the *shape* of the event — inherit, recur, catch, prevent, wire-verify same day — is what the mechanism is for.

### On the fuller federation architecture

The convention above (composition, promotion, anchor format, anchor-verification discipline) describes lesson inheritance between Brains. It does not yet describe a full federation architecture — the contract-commons layer, citation-without-replication, append-only ledgers, and the operator-ratified amendment discipline that lets multiple Brains share a durable interchange surface without any Brain overriding another. That architecture is in live trial between the two production Brains and has completed its first full exchange, including its first operator-ratified contract amendment. It will be documented as its own chapter when its receipts are written up.

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
3. **Decide on a Brain topology.** One Brain per developer? One per team? One per product line? A useful anonymized default: private Brains under each operator's own account, this public pattern under the org. See the *Running the pattern on more than one brain* section below for how multi-Brain topology works in practice.
4. **Decide on egress discipline.** When does Brain content ever become public? Define that path; gate it.
5. **Add Proofing 1 (Layer 6) when you outgrow eyeball audits.** Start with one or two rules — a ceiling check, a dangling-citation check — wired into a non-blocking CI step. Watch them fire on real drift. Flip to blocking only when the rule set is stable.
6. **Iterate.** Brains get better with use. Yours will look different from anybody else's after six months. That's correct behaviour.

If you'd like to discuss the pattern with the team that built it, the LodgeiT Labs maintainers are reachable via the GitHub issues on this repository.

---

## Licence

This document is published under Apache 2.0. The pattern itself is unencumbered — it is just a design.

---

*Authored by ClawDog (LodgeiT Labs' resident agent) on behalf of the LodgeiT engineering practice. ∮*
