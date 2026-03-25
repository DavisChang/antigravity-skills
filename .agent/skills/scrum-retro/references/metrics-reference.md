# Retro Improvement Metrics Reference

Each action should have 1–2 measurable indicators. Pick from the theme below.
Unless otherwise noted, measure per sprint.

---

## A. Spec clarity / refinement

| Metric | How to measure |
|---|---|
| Clarifications added mid-sprint due to unclear requirements | Weekly count of Slack threads or ticket comments tagged “clarification” |
| Stories missing AC or spec discovered after sprint start | Count at planning or during sprint (PM or QA flags) |
| Share of spillover stories caused by spec gaps | Of spillover stories, how many tagged “spec gap” |
| Items discovered before demo that do not match expectations | PM logs on demo day |
| Share of stories that met DoR before planning | Count at each planning |

---

## B. Delivery planning / estimation

| Metric | How to measure |
|---|---|
| Stories entering sprint without executable-level breakdown | Engineering lead flags at planning |
| Items that get task breakdown only mid-sprint | Compare Jira task creation time to sprint start |
| Spillover rate | Spillover stories ÷ committed stories |
| Stories or person-days disrupted by unplanned work | Unplanned work log per sprint |
| Estimation accuracy | Story points completed ÷ committed points |

---

## C. Dependency management

| Metric | How to measure |
|---|---|
| Tickets blocked by dependencies | Jira “Blocked” count per sprint |
| Average days blocked | Unblocked date − blocked date per ticket |
| Share of dependencies identified before planning | Fill rate of dependency field at planning |
| Slips caused by external dependencies | Count from retro notes |
| Dependencies discovered after sprint midpoint | Share of tickets where “blocked since” is after mid-sprint |

---

## D. Quality process / QA

| Metric | How to measure |
|---|---|
| Major issues found only in staging | QA counts P1+ staging bugs per sprint |
| Stories not testable the day before demo | QA checklist the day before demo |
| Rework from missing test cases or test info | Tickets QA tags “missing test info” |
| QA participation in refinement | QA sessions attended ÷ refinement sessions |
| DoD pass rate | Share of stories that pass DoD checklist before Done |

---

## E. Collaboration / alignment

| Metric | How to measure |
|---|---|
| PM prep completeness before refinement | At planning, share of stories with AC, wireframe, and scope |
| Acceptance walkthrough before demo | Share of stories with PM + eng walkthrough before demo |
| Rework from cross-role misalignment | EM or SM counts per sprint |
| Days with “waiting for alignment” in standup | Per sprint |

---

## Metric selection guide

Prefer metrics that are:
- **Already visible** in Jira, Slack, or standup — avoid heavy new process
- **Tied to the problem**, not vague proxies
- **Easy to count** — avoid subjective scoring

Aim for **one leading** (process did we run?) and **one lagging** (did outcomes improve?) indicator.

Example for a refinement action:
- Leading: share of stories that met DoR before planning  
- Lagging: spillover stories caused by unclear requirements  
