---
name: ai-judge
description: 'Multi-AI Judge System. ALWAYS completes basic-info confirmation (problem, type, constraints, deliverables, acceptance criteria, risk) and gets explicit user approval before normalizing, generating candidates, or judging. Then orchestrates multiple AI candidates, validates with programmatic gates, AI judge with rubric, refine. Task types: architecture, code, architecture_and_code (mixed), sql, documentation, advice, security_compliance. Triggers on "AI judge", "multi-AI", "AI 裁判", "多模型比較", "AI panel", "compare approaches", "best-of-N", "candidate tournament".'
argument-hint: 'Describe the task to judge (e.g., "design a login system with OAuth", "compare three approaches to rate limiting", "generate and judge SQL migration strategies")'
user-invocable: true
---

# Multi-AI Judge System

Orchestrate multiple AI candidates → validate with programmatic gates → score with an AI judge → refine and deliver.

**Hard rule:** 先完成 **基本資料確認**（含使用者回覆或確認），再進行正規化、候選產生、驗證與裁判。不允許在缺資訊或未確認的情況下直接開始跑管線。

## When to Use

- User wants **multiple AI perspectives** on a task, compared fairly
- User needs **high-confidence answers** with supporting evidence
- User wants **code, architecture, or docs** reviewed by competing approaches
- User asks for an **AI panel, jury, or tournament** to pick the best solution
- User says "AI 裁判", "多模型比較", "AI panel", "compare approaches", "best-of-N"

## When NOT to Use

- Simple single-step questions (just answer directly)
- Tasks where the user already knows the approach and just wants implementation
- Pure chat / brainstorming without a deliverable
- Direct execution of AI-generated code to production (this system produces artifacts for human review)

---

## MANDATORY: Phase 0 — Basic Information Confirmation (基本資料確認)

**Nothing in Phases 1–7 may run until this phase is complete.**

Complete the following in order. Details and question templates → [references/initial-info-checklist.md](references/initial-info-checklist.md).

### Step 0 — What to collect (minimum)

| # | Field | Required? |
|---|--------|-------------|
| 1 | Problem statement | **Yes** — what to solve + why it matters |
| 2 | Task type | **Yes** — architecture / code / SQL / docs / advice / security_compliance / mixed |
| 3 | Constraints | **At least one** — stack, infra, compliance, or performance |
| 4 | Deliverables | **At least one** — e.g. code, tests, api_spec, architecture |
| 5 | Acceptance criteria | **At least one** — verifiable hard requirement |
| 6 | Risk level | If unclear → default `medium`; escalate for auth/PII/payments |
| 7 | Domain context | Optional but recommended — repo paths, conventions, prior attempts |

If the user already gave everything in one message, **still** output the summary in Step 1 and ask for confirmation in Step 2.

### Step 1 — Summarize and surface gaps

1. Read [initial-info-checklist.md](references/initial-info-checklist.md).
2. Produce a **Basic Info Confirmation** block (see template below).
3. List any **missing or ambiguous** items as explicit questions.

### Step 2 — User confirmation (gate)

Before Phase 1:

- If anything is missing → **stop and ask**; do not normalize or generate candidates.
- If everything is present → **ask the user to confirm** the summary is correct (e.g. 「以上是否正確？有需要修正或補充的項目嗎？」).
- **Proceed only after** the user confirms (or explicitly says to proceed with stated assumptions) or supplies the missing answers.

**Forbidden:** Starting normalization, rubric generation, candidate generation, or judging without completing Step 2.

### Basic Info Confirmation — output template

Use this block whenever you finish Step 0–1 (and again after the user fills gaps):

```text
## Basic Info Confirmation

| Item | Content |
|------|---------|
| Problem (what + why) | … |
| Task type | … |
| Constraints | … |
| Deliverables | … |
| Acceptance criteria | … |
| Risk level | low / medium / high |
| Domain context | … or N/A |

- Open questions: … (none if complete)
- Status: ☐ pending user confirmation  ☐ confirmed — proceed to Phase 1
```

---

## Decision Tree: Start Here

```
User provides a task
│
├─ Phase 0 basic info complete AND user confirmed?
│   └─ No → STOP: collect / summarize / ask until Basic Info Confirmation is "confirmed"
│   └─ Yes → continue below
│
├─ Task type clear?
│   ├─ architecture            → 3 candidates, 1 judge, refine (no build/test sandbox)
│   ├─ code                    → 3 candidates, 1 judge, refine (full sandbox validation)
│   ├─ architecture_and_code   → 3 candidates, 1 judge, refine (both validation types)
│   │   (alias: mixed)
│   ├─ sql                     → 3 candidates, 1 judge, refine (SQL syntax + schema validation)
│   ├─ documentation / advice  → 2 candidates, 1 judge, NO refine (schema + coverage check only)
│   └─ security_compliance     → 4 candidates, 2 judges, refine + human gate
│
├─ Need architecture reference?
│   └─ [architecture-overview.md]
│
├─ Need candidate output format?
│   └─ [candidate-schema.md]
│
├─ Need validation rules?
│   └─ [validation-layer.md]
│
├─ Need judge scoring rules?
│   └─ [judge-design.md]
│
├─ Need prompt templates?
│   └─ [prompt-templates.md]
│
├─ Need data model?
│   └─ [data-model.md]
│
├─ Need API design?
│   └─ [api-design.md]
│
├─ Building the system?
│   └─ [project-skeleton.md]
│
├─ Need security / sandbox rules?
│   └─ [security-and-sandbox.md]
│
├─ Need observability setup?
│   └─ [observability.md]
│
├─ Need cost control strategy?
│   └─ [cost-control.md]
│
└─ Handling failures?
    └─ [failure-handling.md]
```

---

## Reference Documents

| Topic | Description |
|-------|-------------|
| [initial-info-checklist.md](references/initial-info-checklist.md) | **Read first** — mandatory information to collect before starting |
| [architecture-overview.md](references/architecture-overview.md) | Core pipeline, roles, state machine, data flow |
| [candidate-schema.md](references/candidate-schema.md) | Candidate output schema, role definitions, generation strategies |
| [validation-layer.md](references/validation-layer.md) | Hard gates, score aggregation, validation output format |
| [judge-design.md](references/judge-design.md) | Judge rules, constraints, output format, prompt |
| [refiner-design.md](references/refiner-design.md) | Refiner workflow, merge plan, re-validation |
| [prompt-templates.md](references/prompt-templates.md) | All prompt templates: candidate, judge, refiner, extractor |
| [data-model.md](references/data-model.md) | PostgreSQL schema: tasks, candidates, validations, judgments, outputs, audit |
| [api-design.md](references/api-design.md) | REST API endpoints, request/response formats |
| [security-and-sandbox.md](references/security-and-sandbox.md) | Sandbox rules, secret design, policy engine |
| [observability.md](references/observability.md) | Metrics, traces, audit logging with OpenTelemetry |
| [cost-control.md](references/cost-control.md) | Dynamic routing, candidate/judge count by task type |
| [failure-handling.md](references/failure-handling.md) | No-winner, judge disagreement, fallback strategies |
| [project-skeleton.md](references/project-skeleton.md) | FastAPI project structure and Python code skeletons |

### Examples (completed runs)

| Example | Summary |
|---------|---------|
| [examples/pptx-worker-queue/](examples/pptx-worker-queue/README.md) | Phase 0–7 完整案例：AWS EKS 上 PPTX 轉檔 worker queue 架構選型（EventBridge + SQS + DynamoDB + KEDA） |

---

## Execution Workflow

### Phase 0 — Basic Information Confirmation (MANDATORY)

→ Defined in full at the top of this document (**MANDATORY: Phase 0**). Execute once per task; do not repeat.

**Gate:** `Status: confirmed — proceed to Phase 1` must be set before continuing.

### Phase 1 — Normalize Task

**Prerequisite:** Phase 0 completed with user confirmation.

Convert the user's natural-language request into a structured task spec:

```json
{
  "task_id": "task_001",
  "task_type": "architecture_and_code",
  "problem_statement": "...",
  "constraints": ["..."],
  "deliverables": ["architecture", "api_spec", "code", "tests"],
  "acceptance_criteria": ["must compile", "must pass tests", "..."]
}
```

### Phase 2 — Define Rubric

Generate scoring criteria based on the task type. Do not solve the problem — only define how solutions will be judged.

```json
{
  "rubric_version": "v1",
  "criteria": [
    {"name": "correctness",      "weight": 0.30},
    {"name": "completeness",     "weight": 0.20},
    {"name": "security",         "weight": 0.20},
    {"name": "feasibility",      "weight": 0.15},
    {"name": "maintainability",  "weight": 0.10},
    {"name": "clarity",          "weight": 0.05}
  ],
  "hard_gates": [
    "test_pass_rate >= 0.95",
    "critical_security_issues == 0",
    "required_fields_coverage >= 0.90"
  ]
}
```

### Phase 3 — Generate Candidates

Run multiple AI candidates **in parallel** with different roles:

| Role | Focus | Strategy |
|------|-------|----------|
| Candidate A | Correctness-first | Conservative, stable, well-tested |
| Candidate B | Security-first | Threat modeling, defensive coding |
| Candidate C | Cost-first | Minimal infrastructure, pragmatic |
| Candidate D | Speed-first | Fast delivery, lean architecture |

All candidates MUST output in the structured schema defined in [candidate-schema.md](references/candidate-schema.md).

Diversity comes from: different roles, different temperatures, different prompt strategies, or different models.

### Phase 4 — Validate

Apply **programmatic validation** before the judge sees anything:

**For code tasks:**
- compile / build
- unit tests + integration tests
- lint + type check
- dependency scan + SAST
- benchmark

**For document / advice tasks:**
- JSON schema validation
- requirement coverage check
- contradiction detection
- forbidden content / policy check

Any candidate that fails a **hard gate** is eliminated. See [validation-layer.md](references/validation-layer.md).

### Phase 5 — Judge

The AI judge evaluates only candidates that passed validation:

- Score each criterion with evidence
- Apply rubric weights
- Factor in validation results
- Decide: `accept` / `revise_then_accept` / `no-winner`
- Produce a `must_fix` list and optional `merge_plan`

**Judge constraints:**
- Cannot add new requirements
- Cannot reward length or confidence
- Cannot ignore failed tests
- Must cite evidence for every score
- Must output `no-winner` if all candidates fail

See [judge-design.md](references/judge-design.md).

### Phase 6 — Refine (if needed)

If the judge decides `revise_then_accept`:

1. Take the winner as the base
2. Apply all items from the `must_fix` list
3. Borrow specified items from other candidates per `merge_plan`
4. Do NOT change anything that already passes tests
5. Re-validate the refined output

See [refiner-design.md](references/refiner-design.md).

### Phase 7 — Final Output

Deliver the complete package:

```json
{
  "final_answer": {
    "summary": "...",
    "architecture": {},
    "api_spec": [],
    "db_schema": [],
    "implementation_artifacts": [],
    "tests": [],
    "risks": []
  },
  "decision_report": {
    "winner_candidate_id": "cand_A",
    "why_selected": ["..."],
    "comparison_table": [...]
  },
  "validation_report": {},
  "audit_refs": {}
}
```

---

## State Machine

```
created → basic_info_confirmed → normalized → planned → generating_candidates → validating
→ judging → [refining → revalidating]* → finalized

* refining / revalidating are conditional:
  - advice / documentation: skip (judge decides accept directly)
  - architecture / code / sql / architecture_and_code: run if decision = "revise_then_accept"
  - security_compliance: always run + human gate before finalized
```

`basic_info_confirmed` means the Basic Info Confirmation block is complete and the user has confirmed (or explicitly approved assumptions). Each transition is logged. If any step fails, the system can retry, fall back, or halt with a clear reason.

---

## Core Principles

| Principle | Description |
|-----------|-------------|
| **Judge ≠ truth source** | The judge only arbitrates; programmatic validation does the heavy lifting |
| **Unified schema** | All candidates use the same output format — no free-text comparisons |
| **Hard gates first** | Failed tests cannot be rescued by good prose |
| **No-winner is valid** | If all candidates fail, the system refuses to produce a fake winner |
| **Audit everything** | Every prompt, response, score, and decision is logged for traceability |
| **Artifacts, not chat** | The output is structured data + files, not a conversation summary |

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong |
|-------------|----------------|
| Single judge as subjective selector | No programmatic validation = no objectivity |
| Chatbot wrapper | Judge system must produce structured artifacts, not chat |
| "Looks reasonable" text comparison | Without schema + gates, comparison is meaningless |
| Direct execution of AI code | All AI output is untrusted; sandbox and human review required |
| Skipping no-winner branch | Forces the system to pick a bad answer when all fail |
| No audit log | Makes it impossible to debug why a judgment went wrong |
| Skipping Phase 0 confirmation | Produces wrong rubric, wasted candidates, and unfair comparison |
