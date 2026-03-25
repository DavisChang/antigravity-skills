---
name: scrum-retro
description: Facilitates Scrum retrospectives by turning raw retro notes into structured Improvement Log entries with themes, actionable experiments, owners, and metrics. Use when the user provides retro data, sticky notes, sprint observations, or asks to organize or summarize a retro. Triggers on "retro", "retrospective", "sprint retro", "improvement log", "retro 整理", "retro 紀錄".
user-invocable: true
---

# Scrum Retro Agent

Turns raw retrospective input into structured, trackable improvement outputs.

## Input

The user may provide:
- Raw sticky notes or observations (unstructured text)
- Grouped items (e.g. Keep / Try / Improve / Drop)
- Previous sprint Improvement Log entries (for review)
- Both: last sprint review plus new observations

**If anything is missing**, ask:
1. Is this a new retro only, a review of last sprint’s actions only, or both?
2. Sprint number or date?
3. Which roles are involved (PM, engineering, QA, EM, Scrum Master)?

---

## Workflow

### Step 1 — Triage the input

- **New retro notes only** → Step 2  
- **Last sprint action review only** → Step 5  
- **Both** → Step 5, then Step 2  

### Step 2 — Categorize into themes

Map every observation to one of these five themes (or add a new theme only if clearly distinct):

| Theme | Typical signals |
|---|---|
| **Spec clarity** | Missing spec or AC, unclear wireframes, domain gaps, demo vs expectation mismatch |
| **Delivery planning** | Weak task breakdown, estimation drift, overloaded sprint, unplanned work inserted mid-sprint |
| **Dependency management** | Cross-team blocking, PR dependencies, late discovery of waits on others |
| **Quality process** | QA engaged too late, stage-only defects, missing tests or unclear DoD |
| **Collaboration rhythm** | PM / eng / QA misalignment, refinement not prepared, demo not verified early |

Merge duplicates. Show which raw items land in each theme.

### Step 3 — Select 1–2 improvement experiments

Prioritize in this order:
1. Recurred in 2+ consecutive retros  
2. Highest impact on delivery stability  
3. Controllable by the team within one sprint  
4. Observable outcome within one sprint  

State which themes were chosen and briefly why others were deferred.

### Step 4 — Write Improvement Log entries

For each selected action, output one block:

```
**Date / Sprint**: [Sprint number or date]
**Theme**: [one of the five themes]
**Problem Statement**: [one sentence — what is wrong and what it hurts]
**Hypothesis**: [if we do X, then Y improves]
**Action / Experiment**: [concrete, executable step — not a slogan]
**Owner**: [single accountable role or person]
**Supporters**: [other roles]
**Metric**: [1–2 measurable indicators and how often to review]
**Review**: [next retro / after 2 sprints / date]
**Status**: Planned
```

**Action quality check** — rewrite vague items:

| Vague (reject) | Concrete (use) |
|---|---|
| Improve refinement | Every story must pass AC review 24h before planning; otherwise it cannot enter the sprint |
| Involve QA earlier | QA joins the last 15 minutes of refinement to check testability and edge cases only |
| Plan better | Each story gets a dependency field in refinement: external / internal / waiting owner |
| Communicate more | PM + eng do a 15-minute acceptance walkthrough the day before demo |

### Step 5 — Review last sprint’s actions (if provided)

For each prior action:

```
**Action**: [original action]
**Did it happen?**: Yes / Partially / No
**Result**: [what actually happened]
**Metric change**: [before → after, or "not measured"]
**Decision**: Keep as-is / Adjust (describe) / Standardize into working agreement / Drop
```

---

## Output format

Deliver a single document:

```
# Retro Output — Sprint [X] — [Date]

## Last Sprint Action Review
[Step 5 output, or "N/A — first retro"]

## Theme Summary
[Observations grouped by theme, with counts]

## Selected Improvements (this sprint)
[1–2 Improvement Log entries from Step 4]

## Deferred Themes
[Not chosen this sprint, one-line reason each]

## Capacity Note
Reserve 5–10% of sprint capacity for process improvement.  
Add selected actions as real backlog items (e.g. Jira) with owner and due date.
```

---

## Retro agenda (facilitator)

1. **Review last sprint’s actions** (10–15 min) — outcomes, metrics, Keep / Adjust / Drop  
2. Gather new observations  
3. Cluster into themes  
4. Vote — pick 1–2 themes  
5. Define action, owner, and metric for next sprint  

---

## Reference files

- Improvement Log table and examples → [references/improvement-log-template.md](references/improvement-log-template.md)  
- Metrics by theme → [references/metrics-reference.md](references/metrics-reference.md)  
