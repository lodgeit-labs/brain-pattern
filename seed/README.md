# Day-1 seed kit

The template files here are the concrete artifacts named in the *"Day-1 seed kit"* section of `BRAIN_PATTERN_FOR_DEVELOPERS.md`. Read that section first; this directory is the operational companion, not a standalone tutorial.

## What lands where when you follow the six-step bootstrap

```
<your-brain>/
├── SOUL.md               ← seed/SOUL.md
├── IDENTITY.md           ← seed/IDENTITY.md
├── USER.md               ← seed/USER.md
├── AGENTS.md             ← seed/AGENTS.md
├── MEMORY.md             ← seed/MEMORY.md
├── .gitignore            ← seed/.gitignore
├── memory/
│   ├── lessons.md        ← seed/memory/lessons.md
│   ├── latest-activity.md ← seed/memory/latest-activity.md
│   └── YYYY-MM-DD.md     ← seed/memory/DAILY-NOTE-TEMPLATE.md (rename to today's date)
└── scripts/
    └── secret_scanner.py ← seed/scripts/secret_scanner.py
```

## What this is NOT

- **Not a fork target.** You do not fork `brain-pattern` to get a Brain. You copy these seed files into a fresh private repo you own, filled with your own content, on your own credentials.
- **Not a schema.** Every file here is prose or minimally-scaffolded structure. Change field names, invent new sections, delete anything that doesn't fit your work. The pattern is the layout and the invariants, not the exact wording.
- **Not authority.** Nothing in this seed set overrides your own operator decisions. If a template says one thing and you want another, your Brain wins.

## Version

Seed set v1, aligned to `BRAIN_PATTERN_FOR_DEVELOPERS.md` at the commit where this file was introduced. Future revisions supersede-don't-erase (see the "Candidate-lesson lifecycle" section and the "Engraving versioning" note in Layer 1).
