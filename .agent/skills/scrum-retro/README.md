# scrum-retro Skill

An agent skill that turns raw Scrum retrospective notes into a **structured Improvement Log**: themes, concrete experiments, owners, metrics, and a repeatable retro agenda.

## What It Covers

- **Theme clustering** — maps observations to five default themes (spec clarity, delivery planning, dependency management, quality process, collaboration rhythm) or a custom theme when needed  
- **1–2 experiments per sprint** — prioritization rules so the team does not try to fix everything at once  
- **Action quality** — rewrites vague items (“communicate more”) into trackable experiments with clear scope  
- **Improvement Log** — table schema and example rows for Notion, Confluence, Sheets, or Jira  
- **Metrics by theme** — leading and lagging indicators you can actually count  
- **Last-sprint review** — Keep / Adjust / Standardize / Drop for prior actions  

## File Structure

```
.agent/skills/scrum-retro/
├── SKILL.md                              # Entry point — workflow and output format
├── README.md                             # This file (English)
├── README_TW.md                          # Traditional Chinese overview
└── references/
    ├── improvement-log-template.md       # Log table schema and examples
    └── metrics-reference.md              # Metrics catalog by theme
```

## How to Invoke

Mention the skill or describe the task in natural language:

> “Here are our retro sticky notes — cluster themes and pick two actions with metrics.”  
> “Review last sprint’s two improvement items and then process this sprint’s observations.”  
> “Output an Improvement Log row for our dependency theme.”

## Design Principles

1. **Patterns over sticky notes** — improve recurring themes, not every card.  
2. **Experiments, not slogans** — every action must be executable and measurable.  
3. **Review first** — next retro opens with last sprint’s actions so retros do not become complaint-only sessions.  
4. **Capacity** — treat improvement as real work (e.g. 5–10% capacity, backlog tickets, owners).
