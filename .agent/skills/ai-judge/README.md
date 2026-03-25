# ai-judge Skill

A multi-AI judge system that orchestrates multiple AI candidates to produce structured solutions, validates them with programmatic gates, scores them with an AI judge using a rubric, and delivers refined artifacts with full audit trails.

## What This Is NOT

- A single AI picking its favorite answer
- A chatbot wrapper that summarizes multiple responses
- A "looks reasonable" text comparison
- A system that directly executes AI-generated code

## What This IS

Multiple AI candidates produce **structured outputs** (code, architecture, SQL, docs) → **programmatic validation** filters out failures (build, test, lint, security scan) → an **AI judge** scores survivors against a rubric with evidence → a **refiner** patches the winner → the system delivers a **complete package** with artifacts, decision report, and audit trail.

## Key Design Decisions

1. **Mandatory information collection** — the system collects problem statement, constraints, deliverables, and acceptance criteria before generating any candidates
2. **Hard gates before judge** — candidates that fail build, tests, or security checks are eliminated before the judge sees them
3. **No-winner is valid** — if all candidates fail, the system reports failure instead of picking a bad answer
4. **Evidence-based scoring** — every judge score must cite specific evidence from the candidate output
5. **Structured schema** — all candidates use the same output format for fair comparison
6. **Audit everything** — every prompt, response, validation result, and decision is logged

## File Structure

```
.agent/skills/ai-judge/
├── SKILL.md                                    # Entry point — workflow and execution steps
├── README.md                                   # This file (English)
├── README_TW.md                                # Traditional Chinese overview
└── references/
    ├── initial-info-checklist.md               # MANDATORY upfront information collection
    ├── architecture-overview.md                # Core pipeline, roles, state machine
    ├── candidate-schema.md                     # Candidate output schema and role definitions
    ├── validation-layer.md                     # Hard gates, score aggregation, validation output
    ├── judge-design.md                         # Judge rules, constraints, output format
    ├── refiner-design.md                       # Refiner workflow, merge plan, re-validation
    ├── prompt-templates.md                     # All prompt templates (candidate, judge, refiner)
    ├── data-model.md                           # PostgreSQL schema (6 tables)
    ├── api-design.md                           # REST API endpoints and formats
    ├── security-and-sandbox.md                 # Sandbox rules, secret design, policy engine
    ├── observability.md                        # Metrics, traces, audit logging (OpenTelemetry)
    ├── cost-control.md                         # Dynamic routing, budget controls
    ├── failure-handling.md                     # No-winner, disagreement, fallback strategies
    └── project-skeleton.md                     # FastAPI project structure and Python code
```

## How to Invoke

Mention the skill or describe the task:

> "Use the AI judge system to compare three approaches for rate limiting."
> "Run the multi-AI pipeline on this login system design."
> "I want multiple AI candidates to propose database schemas — judge the best one."
> "AI 裁判：比較多個 AI 對這個架構問題的解法。"

## Pipeline Overview

```
Collect Info → Normalize Task → Generate Rubric → Generate Candidates (parallel)
→ Validate (gates) → Judge (rubric + evidence) → Refine (if needed)
→ Re-validate → Final Output (artifacts + report + audit)
```

## Candidate Roles

| Role | Focus |
|------|-------|
| Correctness-first | Proven patterns, thorough testing, conservative |
| Security-first | Threat modeling, defensive coding, trust boundaries |
| Cost-first | Minimal infrastructure, pragmatic trade-offs |
| Speed-first | Fastest delivery, lean architecture, clear upgrade path |

## Validation Gates

Candidates are eliminated before the judge if they fail:
- Build / compile
- Test pass rate < 95%
- Critical security issues > 0
- Required field coverage < 90%

## Design Principles

1. **Validation > Judge** — programmatic checks are more important than AI opinions.
2. **Schema uniformity** — all candidates use the same format; no free-text beauty contests.
3. **Evidence required** — every score needs a citation, not just a gut feeling.
4. **Fail safely** — no-winner, fallbacks, and human escalation are first-class features.
5. **Full traceability** — every step is logged and reproducible.
