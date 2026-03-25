# Project Skeleton

FastAPI project structure and Python code skeletons for the AI Judge system.

---

## Directory Structure

```
app/
├── main.py                        # FastAPI app entry point
├── api/
│   └── routes/
│       ├── tasks.py               # POST /v1/tasks, GET /v1/tasks/{id}
│       ├── candidates.py          # GET /v1/tasks/{id}/candidates
│       ├── judgments.py           # GET /v1/tasks/{id}/judgment
│       └── finals.py             # GET /v1/tasks/{id}/final
├── core/
│   ├── config.py                  # Settings, env vars
│   ├── logging.py                 # Structured logging setup
│   └── security.py                # Auth middleware, API keys
├── domain/
│   ├── models.py                  # SQLAlchemy / ORM models
│   ├── schemas.py                 # Pydantic schemas
│   └── enums.py                   # Status, TaskType, Decision enums
├── services/
│   ├── normalizer.py              # Task normalization
│   ├── planner.py                 # Rubric generation
│   ├── candidate_orchestrator.py  # Parallel candidate generation
│   ├── validator.py               # Validation + gate checking
│   ├── judge.py                   # AI judge evaluation
│   ├── refiner.py                 # Winner refinement
│   └── finalizer.py               # Final output assembly
├── infra/
│   ├── db.py                      # Database connection
│   ├── storage.py                 # Object storage (S3)
│   ├── queue.py                   # Task queue (Redis)
│   ├── telemetry.py               # OpenTelemetry setup
│   ├── sandbox.py                 # Docker sandbox management
│   └── llm/
│       ├── base.py                # Abstract LLM adapter
│       ├── openai_adapter.py      # OpenAI API adapter
│       ├── anthropic_adapter.py   # Anthropic API adapter
│       └── local_adapter.py       # Local model adapter
├── workflows/
│   ├── temporal_workflows.py      # Temporal workflow definitions
│   └── activities.py              # Temporal activity implementations
├── tests/
│   ├── test_normalizer.py
│   ├── test_validator.py
│   ├── test_judge.py
│   └── test_pipeline.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Domain Schemas (Pydantic)

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class TaskType(str, Enum):
    architecture = "architecture"
    code = "code"
    architecture_and_code = "architecture_and_code"
    sql = "sql"
    documentation = "documentation"
    advice = "advice"
    security_compliance = "security_compliance"

class Decision(str, Enum):
    accept = "accept"
    revise_then_accept = "revise_then_accept"
    no_winner = "no-winner"

class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskSpec(BaseModel):
    task_id: str
    task_type: TaskType
    problem_statement: str
    constraints: List[str] = []
    deliverables: List[str] = []
    acceptance_criteria: List[str] = []
    risk_level: RiskLevel = RiskLevel.medium

class CandidateArtifact(BaseModel):
    filename: str
    language: str
    content: str

class CandidateOutput(BaseModel):
    candidate_id: str
    role: str
    summary: str
    assumptions: List[str] = []
    architecture: Dict[str, Any] = {}
    api_spec: List[Dict[str, Any]] = []
    db_schema: List[Dict[str, Any]] = []
    implementation: Dict[str, Any] = {}
    tests: List[Dict[str, Any]] = []
    risks: List[Dict[str, Any]] = []
    missing_fields: List[str] = []

class ValidationResult(BaseModel):
    candidate_id: str
    build_ok: bool = True
    test_pass_rate: float = 0.0
    lint_errors: int = 0
    type_errors: int = 0
    critical_security_issues: int = 0
    high_security_issues: int = 0
    required_coverage: float = 0.0
    benchmark: Dict[str, Any] = {}
    policy_violations: List[Dict[str, Any]] = []
    gate_passed: bool = False
    gate_failures: List[str] = []

class RubricCriterion(BaseModel):
    name: str
    weight: float

class Rubric(BaseModel):
    rubric_version: str = "v1"
    criteria: List[RubricCriterion]
    hard_gates: List[str]

class CandidateReview(BaseModel):
    candidate_id: str
    scores: Dict[str, float]
    weighted_total: float
    strengths: List[str]
    weaknesses: List[str]
    must_fix: List[str]
    evidence: List[str]

class MergePlanItem(BaseModel):
    base: str
    borrow_from: str
    items: List[str]

class Judgment(BaseModel):
    rubric_version: str
    candidate_reviews: List[CandidateReview]
    winner_candidate_id: Optional[str] = None
    decision: Decision
    confidence: float
    merge_plan: List[MergePlanItem] = []
```

---

## Pipeline Orchestrator

```python
class MultiAIPipeline:
    def __init__(
        self,
        normalizer,
        planner,
        candidate_orchestrator,
        validator,
        judge,
        refiner,
        finalizer,
    ):
        self.normalizer = normalizer
        self.planner = planner
        self.candidate_orchestrator = candidate_orchestrator
        self.validator = validator
        self.judge = judge
        self.refiner = refiner
        self.finalizer = finalizer

    async def run(self, raw_input: str) -> dict:
        task_spec = await self.normalizer.normalize(raw_input)
        rubric = await self.planner.plan(task_spec)

        candidates = await self.candidate_orchestrator.generate(
            task_spec, rubric
        )
        validations = await self.validator.validate_all(
            task_spec, candidates
        )

        gated = [
            c for c in candidates
            if self.validator.passes_gate(
                validations[c["candidate_id"]], rubric
            )
        ]

        if not gated:
            return {
                "decision": "no-winner",
                "reason": "No candidate passed hard gates",
                "task_spec": task_spec,
            }

        judgment = await self.judge.evaluate(
            task_spec, rubric, gated, validations
        )

        if judgment["decision"] == "revise_then_accept":
            revised = await self.refiner.revise(
                task_spec=task_spec,
                rubric=rubric,
                judgment=judgment,
                candidates={
                    c["candidate_id"]: c for c in candidates
                },
            )
            rev_validation = await self.validator.validate_one(
                task_spec, revised
            )
            return await self.finalizer.finalize(
                task_spec, revised, rev_validation, judgment
            )

        winner = next(
            c for c in candidates
            if c["candidate_id"] == judgment["winner_candidate_id"]
        )
        return await self.finalizer.finalize(
            task_spec,
            winner,
            validations[winner["candidate_id"]],
            judgment,
        )
```

---

## Gate Checker

```python
class ValidatorService:
    def passes_gate(self, result: dict, rubric: dict) -> bool:
        if not result.get("build_ok", False):
            return False
        if result.get("test_pass_rate", 0) < 0.95:
            return False
        if result.get("critical_security_issues", 1) > 0:
            return False
        if result.get("required_coverage", 0) < 0.90:
            return False
        return True
```

---

## Score Aggregation

```python
def aggregate_score(judge_score: float, validation: dict) -> float:
    test_score = validation["test_pass_rate"] * 100

    security_score = 100 if validation["critical_security_issues"] == 0 else 0
    security_score -= min(validation["high_security_issues"] * 10, 40)

    perf_latency = validation.get("benchmark", {}).get(
        "p95_latency_ms", 1000
    )
    performance_score = max(0, 100 - perf_latency / 5)

    coverage_score = validation["required_coverage"] * 100

    return round(
        0.45 * judge_score
        + 0.20 * test_score
        + 0.15 * security_score
        + 0.10 * performance_score
        + 0.10 * coverage_score,
        2,
    )
```

---

## Development Roadmap

### Week 1: Core Pipeline

- FastAPI API skeleton
- PostgreSQL schema migration
- Candidate schema enforcement
- 2 candidates + 1 judge
- Mock validation (no sandbox)

### Week 2: Real Validation

- Docker sandbox integration
- Build / test / lint runners
- Policy gate enforcement
- Result persistence

### Week 3: Refinement Loop

- Must-fix workflow
- Merge-plan execution
- Re-validation
- Final output packaging

### Week 4: Observability and Audit

- OpenTelemetry integration
- Audit event logging
- Cost reporting dashboard
- Replay dataset for testing

### Post-Launch

- Dual judge for high-risk tasks
- Replay test suite
- Secret broker integration
- Human review portal
- Firecracker sandbox upgrade
