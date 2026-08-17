# MEMORY.md — long-term memory (lean INDEX, not a log)

> Auto-loads every turn. Soft ceiling: ~8 KB (adjust to your Brain's load-bearing floor per the "ceilings as measurements" discipline). Rotating log lives in `memory/latest-activity.md`.

## User & stack

*One paragraph on the operator + primary stack. Points at USER.md for detail.*

## Product topology / project scope

*One paragraph on what the Brain is being used for. Points at topical files or PROJECT_NOTES/ for detail.*

## Topical memory files

*Read on demand. Trigger words on the right.*

| File | Triggers |
|---|---|
| `memory/lessons.md` | lessons, history, resolved threads |
| `memory/latest-activity.md` | recent turns, latest activity |
| `memory/<add-topics-as-needed>.md` | *your triggers* |

## Standing rules

*The rules the agent must obey on every turn. Full text inline — never demoted behind pointers, even under ceiling pressure. See the "Don't demote auto-injected rules" discipline in the pattern doc.*

1. *e.g. Never commit to `main`/`master` directly; all writes go through a branch + operator sign-off.*
2. *e.g. Never overwrite content hashes; append to a mutation ledger.*
3. *e.g. Never leak private context into public-facing artefacts.*
4. *…*

## Open threads

*A short table of active workstreams. State + trigger for each. Detail lives in daily notes or topical files.*

## Latest Activity

See `memory/latest-activity.md`. This section MUST remain a lean pointer — no bullet-shaped rows here (they'd indicate the timeline has regressed back into the index; see the pattern doc's §7 pointer-sanity discipline).
