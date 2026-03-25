# Retro Improvement Log — Template

Maintain one log per team (Notion, Confluence, Google Sheet, or a Jira Epic).
Each row is one improvement experiment.

## Table schema

| Field | Description | Example |
|---|---|---|
| Date / Sprint | Retro that produced this entry | Sprint 10 / 2025-03-01 |
| Theme | Spec clarity / Delivery planning / Dependency management / Quality process / Collaboration rhythm | Spec clarity |
| Problem Statement | One sentence: what is broken and what it impacts | We still add spec and AC after sprint start, which breaks estimates and delivery |
| Hypothesis | If we do X, Y will improve | If stories pass DoR before planning, rework from unclear requirements will drop |
| Action / Experiment | Concrete executable step | All stories must complete AC review 24h before planning or they cannot enter the sprint |
| Owner | Single accountable role | PM |
| Supporters | Collaborators | Engineering lead, QA |
| Metric | 1–2 measurable indicators | Clarification threads per sprint; spillover stories tagged “spec gap” |
| Review date | When to check results | Next retro |
| Status | Planned / Doing / Done / Dropped | Doing |
| Result | Actual outcome after review | Clarifications dropped from 8 to 3 |
| Decision | Keep / Adjust / Standardize / Drop | Standardize → add to Working Agreement |

---

## Example entries

### Entry 1 — Refinement quality

| Field | Value |
|---|---|
| Date / Sprint | Sprint 10 |
| Theme | Spec clarity |
| Problem Statement | We still add spec and AC after sprint start, which hurts estimates and delivery |
| Hypothesis | If stories pass DoR before planning, rework from unclear requirements will drop |
| Action / Experiment | From next sprint: every story must include AC, out of scope, dependencies, and acceptance method before planning |
| Owner | PM |
| Supporters | Engineering lead, QA |
| Metric | Clarifications per sprint; spillover stories caused by unclear requirements |
| Review date | Sprint 11 retro |
| Status | Doing |

### Entry 2 — Dependency visibility

| Field | Value |
|---|---|
| Date / Sprint | Sprint 10 |
| Theme | Dependency management |
| Problem Statement | Cross-team and PR dependencies often surface in the second half of the sprint |
| Hypothesis | If we mark dependencies in refinement, blocked time will decrease |
| Action / Experiment | Add Jira fields: dependency type (external / internal), waiting owner, blocked since |
| Owner | EM / Scrum Master |
| Supporters | Engineering, PM |
| Metric | Average days blocked; share of dependencies identified before planning |
| Review date | Sprint 12 retro (two sprints) |
| Status | Planned |

---

## Sprint-level operating rhythm

### After each retro
- [ ] Facilitator groups cards into 4–6 themes
- [ ] Team votes → select 1–2 improvement actions
- [ ] Add rows to this log
- [ ] Create tickets for selected actions

### Before sprint planning
- [ ] Confirm improvement actions are in the sprint backlog
- [ ] Assign owner
- [ ] Set review date and metric baseline

### Weekly (10 min)
- [ ] Short check: done / blocked / needs adjustment?

### Next retro opening (10–15 min)
- [ ] Review each “Doing” entry
- [ ] Record result and decide: Keep / Adjust / Standardize / Drop

---

## Every 4–6 sprints: trend review

- Which themes repeat most?
- Which actions moved the metrics?
- What can become a Working Agreement?
- What is the team repeatedly deferring?
