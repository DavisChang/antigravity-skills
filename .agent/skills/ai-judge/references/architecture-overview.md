# Architecture Overview

## Core Pipeline

```
[Client / UI]
    ↓
[API Gateway]
    ↓
[Task Normalizer]         ← converts natural language → structured task spec
    ↓
[Planner + Rubric Engine] ← defines scoring rules, does NOT solve the problem
    ↓
[Candidate Orchestrator]  ← runs multiple AI candidates in parallel
    ├─ Model A: correctness-first
    ├─ Model B: security-first
    ├─ Model C: cost-first
    ├─ Model D: speed-first
    ↓
[Validation Layer]        ← programmatic, deterministic checks
    ├─ schema validator
    ├─ test runner
    ├─ linter / type checker
    ├─ security scanner
    ├─ benchmark runner
    ├─ policy engine
    ↓
[AI Judge Engine]         ← rubric-based scoring with evidence
    ├─ structured scoring
    ├─ evidence extraction
    ├─ merge / reject / revise decision
    ↓
[Refiner]                 ← patches winner based on must-fix list
    ↓
[Re-validation]           ← runs validation again on refined output
    ↓
[Final Arbiter]           ← produces the deliverable package
    ↓
[Audit Log + Storage + Telemetry]
```

---

## Role Responsibilities

### Task Normalizer

Converts user natural language into a structured task spec.

**Input:** raw text, attached files, constraints, domain type
**Output:**

```json
{
  "task_id": "task_001",
  "task_type": "architecture_and_code",
  "problem_statement": "Design and implement a login and authorization system",
  "constraints": [
    "Backend TypeScript",
    "PostgreSQL database",
    "Google OAuth support",
    "RBAC required"
  ],
  "deliverables": [
    "architecture", "api_spec", "db_schema",
    "code", "tests", "deployment_notes"
  ],
  "acceptance_criteria": [
    "must compile",
    "must pass tests",
    "must address token rotation",
    "must include audit logging"
  ]
}
```

### Planner / Rubric Engine

Defines scoring rules. Does NOT solve the problem.

**Output:**

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

### Candidate Generators

Diversity sources — not limited to different models:

| Strategy | Description |
|----------|-------------|
| Different models | GPT-4o vs Claude vs Gemini vs open-source |
| Different roles | Conservative vs security-first vs cost-first vs speed-first |
| Different temperatures | Low-temp precise vs high-temp creative |
| Different prompt strategies | Chain-of-thought vs few-shot vs structured |
| Mixed closed + open source | Proprietary quality vs open-source transparency |

### Validation Layer

More important than the judge. Provides objective, programmatic checks.

See → [validation-layer.md](validation-layer.md)

### AI Judge

Evaluates only validated candidates. Produces scores, evidence, and a decision.

See → [judge-design.md](judge-design.md)

### Refiner

Takes the winner and patches it based on `must_fix`. Does not freelance.

See → [refiner-design.md](refiner-design.md)

---

## State Machine

```
created
  → normalized
  → planned
  → generating_candidates
  → validating
  → judging
  → refining
  → revalidating
  → finalized
```

Each state transition is logged as an audit event.

---

## Workflow Engine Fit

### Why Temporal

Temporal's workflow/execution model is well-suited for this pipeline:

- **Long tasks recoverable** — if the process crashes, it resumes from the last completed activity
- **Per-activity retry** — a failed validation can be retried without re-generating all candidates
- **Human approval insertion** — Temporal signals allow inserting a human gate at any step
- **Full event history** — every activity completion is recorded for audit

### Temporal Workflow Structure

```
TaskWorkflow
  ├─ NormalizeTaskActivity
  ├─ PlanTaskActivity
  ├─ GenerateCandidatesActivity   (fan-out: parallel)
  ├─ ValidateCandidatesActivity   (fan-out: parallel)
  ├─ JudgeCandidatesActivity
  ├─ RefineWinnerActivity         (conditional)
  ├─ RevalidateWinnerActivity     (conditional)
  └─ FinalizeActivity
```

### MVP Alternative

For MVP, a simple Python async pipeline with Redis queue can replace Temporal. Upgrade when you need:
- Cross-process recovery
- Human approval gates
- Multi-day workflows
- Production-grade retry semantics

---

## Technology Recommendations

### Control Plane

| Module | Recommendation | Rationale |
|--------|---------------|-----------|
| API | FastAPI | Fast to build, async-native, auto-docs |
| Workflow | Temporal | Durable execution, retry, human gates |
| Queue | Redis / RabbitMQ | MVP-friendly, upgrade to Temporal later |
| Database | PostgreSQL | JSONB for structured outputs, mature |
| Object Storage | S3-compatible | Artifact files, audit snapshots |
| Observability | OpenTelemetry | Traces + metrics + logs unified |
| Sandbox | Docker + gVisor / Firecracker | Untrusted code execution |
| Policy | OPA or custom rules | Deterministic hard gates |
| Search / Logs | OpenSearch / Elasticsearch | Log aggregation, audit search |

### MVP vs Production

| Aspect | MVP | Production |
|--------|-----|------------|
| Orchestration | Python async + queue | Temporal |
| Sandbox | Docker | Firecracker / hardened sandbox |
| Judge | 1 judge | 2 judges + disagreement handling |
| Observability | Basic logs | Full trace + metrics + audit |
| Routing | Static config | Task-aware dynamic model routing |
| Security | Network off in sandbox | Network off + secret broker + policy engine |
