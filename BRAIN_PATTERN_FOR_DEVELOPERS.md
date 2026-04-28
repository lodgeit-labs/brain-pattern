# The Brain Pattern

**An optional architecture for AI-assisted software development.**

*Vendor-neutral. Tooling-agnostic. Battle-tested in production at LodgeiT Labs.*

---

## TL;DR

If you're using a coding agent (Copilot, Cursor, Claude Code, Gemini, OpenClaw, anything else) and you've ever had it:

- Forget your team's conventions five minutes after you told it
- Hallucinate an API that doesn't exist
- Drift from your build/test/deployment process
- Suggest a refactor that contradicts an architectural decision you made two years ago
- Leak proprietary context into a public artefact (a comment, a commit message, a PR description)

…then you have a **memory and discipline problem**, not an LLM problem. The Brain Pattern solves it with a simple, durable structure: a git-backed knowledge repo, written in plain Markdown, that your agent reads on every session and writes to as it works.

This document describes the pattern. It is not a product. You can adopt it in 90 minutes with no infrastructure, no cloud, no licence, and no vendor lock-in.

---

## The problem, stated plainly

Modern coding agents are powerful within a single session and amnesiac between sessions. They re-derive your team's context every time you open a new chat, and they re-derive it imperfectly. The worse your codebase's documentation, the worse this gets. For greenfield projects this is annoying. For **legacy systems** — large .NET solutions with 15 years of accreted decisions, undocumented integrations, brittle tests, and engineers who have moved on — it is debilitating.

The standard mitigations don't fix it:

- **Confluence / SharePoint / wikis:** Your agent doesn't read them, doesn't trust them, and they go stale because nobody enjoys updating them.
- **ADRs (Architectural Decision Records):** Better, but usually one-shot historical records, not durable agent context. They live in a `docs/` folder that the agent ignores.
- **Per-IDE context files** (`.cursorrules`, `CLAUDE.md`, `.github/copilot-instructions.md`): Tool-specific. Lock you into one vendor. Don't survive when you switch agents. Usually a single file with no internal structure.
- **Telling the agent more in your prompt:** Burns context window, doesn't persist, doesn't compound.

The Brain Pattern is the fix. It is what you'd build if you stopped trying to fit your team's institutional knowledge into a chat window.

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
   ┌──────────────┐                            │
   │    BRAIN     │  ── persistent memory,    │
   │  (git repo,  │     identity, conventions, │
   │   markdown)  │     integrity rules       │
   └──────┬───────┘                            │
          │                                    │
          │ ─── filtered egress only ──────►   │
          │                                    │
          ▼                                    │
   ┌──────────────┐                            │
   │     KIT      │ ── public artefacts:      │
   │ (open source │    your codebase, docs,    │
   │  / public)   │    deployable services    │
   └──────────────┘                            │
```

Three zones. Information flows downhill — from private (Brain) to public (Kit). It never flows back up. This single rule is the foundation of the security model.

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
│   ├── lessons.md     ← things learnt the hard way
│   ├── runbooks/      ← stepwise operational procedures
│   └── …
├── PROJECT_NOTES/     ← canonical knowledge nodes
│   ├── 100_overview.md
│   ├── 200_decisions/
│   └── 300_runbooks/
├── scripts/           ← integrity tooling (see below)
├── Makefile           ← `make validate`, `make publish-check`, etc.
└── .github/workflows/ ← server-side CI for integrity
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
| `memory/runbooks/` | Step-by-step operational procedures the agent must follow exactly. |
| `PROJECT_NOTES/` | Your canonical knowledge graph — architecture, decisions, conventions, gotchas. |
| `scripts/` | The integrity tooling. The hidden value of the pattern. |

---

## The five layers of the pattern

The pattern decomposes into five layers, each adoptable independently. You can take Layer 1 in an afternoon and add the rest as you grow.

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

### Layer 4 — Integrity tooling

This is the moat, and it is what most teams skip and regret.

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

**Cost:** ~1 day to build the tooling, then negligible. The scripts are typically <500 lines of Python total. **Benefit:** the Brain remains trustworthy as it grows, even with multiple human and agent authors mutating it concurrently.

### Layer 5 — Egress filter (the Privacy Gradient)

Brains are private. But teams ship public artefacts — open-source code, documentation, blog posts, conference talks, customer-facing docs. The route from Brain to public artefact must be **gated**, not trusted.

The filter is a script that runs before any Brain → public publication and checks for:

- **Layer A (hard-fail):** known-proprietary fields. E.g. internal cost data, client identifiers, billing codes, contractual fields. If detected, refuse.
- **Layer B (soft-fail):** structural patterns suggestive of leakage. E.g. references to private repository paths, cloud bucket names, internal hostnames. If detected, warn loudly and require an explicit override flag.
- **Layer C (hard-fail):** a reserved namespace (e.g. `x-internal-*`) that anything internal must use. If any field in that namespace appears in a publication candidate, refuse.

The filter runs on egress only — never as a pre-commit hook on the Brain itself, because that would block authoring of legitimately private content. You commit privately and freely; the gate fires only when you try to publish.

This is the same architectural pattern as a unidirectional firewall: data can flow downhill (private → public), but only after passing a deterministic check; nothing can flow uphill.

**Cost:** ~1 day to build. **Benefit:** you can run a public open-source presence and a private knowledge base from the same workflow without ever lying awake worrying about leaks.

---

## What you don't have to build

The following are *generic* — they have nothing to do with any specific domain or vendor — and can be lifted directly from any existing Brain implementation:

- The schema validator pattern
- The content-hash auditor
- The mutation ledger format
- The pre-commit hook
- The CI workflow
- The publication filter (with team-specific denylist)
- The Makefile that wires them together

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

---

## What it costs

| Resource | Cost |
|---|---|
| Disk space | Negligible. A mature Brain with hundreds of nodes is typically a few MB. |
| Cloud spend | $0 for the experiment tier. Optional later (CI runners, hosted runtime). |
| Per-developer fee | None. The pattern has no licence. |
| Discipline | The real cost. Brains decay if nobody maintains them. |
| Setup time | 90 minutes for Layer 1; a day for Layers 4+5 if you want them. |

---

## What it gives back

Six concrete benefits, each with a one-line example:

1. **Continuity across sessions.** *"Pick up where we left off on the migration; the daily log is in `memory/2026-04-25.md`."*
2. **Decision archaeology.** *"Why did we choose SQL Server in 2018? See `200_decisions/2018_db_choice.md`."*
3. **Runbook fidelity.** *"Run the staging deploy. Use the runbook exactly; don't improvise."*
4. **Convention enforcement.** *"All commits must follow the prefix convention in standing rules. Reject anything that doesn't."*
5. **Onboarding acceleration.** *"New senior engineer joining; point them at the Brain README and they'll understand the system in a day, not a month."*
6. **Audit trail.** *"Every change to architectural metadata is recorded in the mutation ledger with author and timestamp; you can reconstruct any state in history."*

---

## What it costs you if you skip it

Honest version: not adopting the Brain Pattern is fine if your team is small, your turnover is low, and your agent use is light. The cost is not catastrophic; it is *cumulative*. Specifically:

- Your agent re-derives team context every session and gets it slightly wrong each time.
- Architectural decisions live in people's heads and walk out the door when they leave.
- Onboarding takes weeks of pair-programming because nothing else is canonical.
- Agent-suggested refactors occasionally contradict decisions made years ago, and you only catch it in code review (or, worse, in production).
- Your agents leak proprietary context into public artefacts because nothing is gating egress.

Whether that's worth a 90-minute investment is your call.

---

## Common objections

**"We already have Confluence."**
Confluence is for humans browsing manually. A Brain is for agents reading programmatically every session. They are not substitutes. You can mirror Confluence content into a Brain (and many teams do), but the Brain is the source the agent actually reads.

**"We already have ADRs."**
Good. ADRs are a strong start on Layer 3. Move them into the Brain, add frontmatter, run them through the schema validator, and you've upgraded them from one-shot historical records to durable agent context.

**"We already have `.cursorrules` / `CLAUDE.md` / `.github/copilot-instructions.md`."**
These are vendor-specific Layer-1 files: persona + scope, in a single fixed-format file. They're a prefix of the Brain pattern. Switch vendor and you start over. The Brain pattern is what you build when you don't want to start over.

**"This sounds like over-engineering for legacy maintenance."**
For greenfield work it might be. For legacy systems — where institutional knowledge is the asset, not the code — it's the opposite. The pattern formalises what your senior engineers already do informally; it just makes the agent able to participate.

**"We can't store private knowledge in a public format."**
The Brain is a *private* repo. Layer 5 (the egress filter) exists precisely to control what, if anything, ever becomes public. The pattern is designed for private-by-default knowledge with deliberate, gated publication.

**"What if we want to change agents later?"**
You change agents. The Brain is markdown in git; it has no vendor coupling. Every coding agent can read markdown.

---

## Reference implementation

LodgeiT Labs runs this pattern in production for the development of its open-source accounting and tax compliance systems. The public-facing pieces of that implementation are:

- **The Kit** — `github.com/lodgeit-labs/clawdog` — the open-source classification engine produced from the Brain.
- **This document** — `github.com/lodgeit-labs/brain-pattern` — the pattern as practised, vendor-neutral, for adoption by other teams.

The Brain itself is private (it contains LodgeiT-specific operational knowledge), but the *pattern* is open. Patterns travel; implementations don't.

LodgeiT's domain is highly deterministic — accounting algebra, statutory tax law, regulatory taxonomies — so the pattern is tuned for *zero-hallucination* in those domains. For legacy software development, the same machinery applies with different domain-specific guardrails (e.g. "build commands must match the runbook exactly", rather than "tax rates must match the statutory table"). The shape is identical.

---

## Where to go next

If you experiment and the pattern fits, the next steps are:

1. **Add Layer 4 (integrity tooling).** Without it, the Brain corrupts under multi-author load. Take a look at the reference implementation; lift the scripts.
2. **Define your standing rules.** What must your agent never do? Write those down.
3. **Decide on a Brain topology.** One Brain per developer? One per team? One per product line? Brains can `git submodule` other Brains.
4. **Decide on egress discipline.** When does Brain content ever become public? Define that path; gate it.
5. **Iterate.** Brains get better with use. Yours will look different from anybody else's after six months. That's correct behaviour.

If you'd like to discuss the pattern with the team that built it, the LodgeiT Labs maintainers are reachable via the GitHub issues on this repository.

---

## Licence

This document is published under Apache 2.0. The pattern itself is unencumbered — it is just a design.

---

*Authored by ClawDog (LodgeiT Labs' resident agent) on behalf of the LodgeiT engineering practice. ∮*
