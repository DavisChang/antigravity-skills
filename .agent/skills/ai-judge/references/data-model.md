# Data Model

PostgreSQL schema for the AI Judge system. All structured outputs are stored as JSONB for flexibility.

---

## Tables

### tasks

```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  task_type TEXT NOT NULL,
  raw_input TEXT NOT NULL,
  normalized_spec JSONB NOT NULL,
  rubric JSONB,
  status TEXT NOT NULL DEFAULT 'created',
  risk_level TEXT NOT NULL DEFAULT 'medium',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
```

**Status values:** `created`, `normalized`, `planned`, `generating_candidates`, `validating`, `judging`, `refining`, `revalidating`, `finalized`, `failed`

### candidates

```sql
CREATE TABLE candidates (
  id UUID PRIMARY KEY,
  task_id UUID NOT NULL REFERENCES tasks(id),
  provider TEXT NOT NULL,
  model_name TEXT NOT NULL,
  role_name TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  response_json JSONB NOT NULL,
  raw_text TEXT,
  latency_ms INT,
  token_input INT,
  token_output INT,
  estimated_cost_usd NUMERIC(10,4),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_candidates_task_id ON candidates(task_id);
```

### validations

```sql
CREATE TABLE validations (
  id UUID PRIMARY KEY,
  candidate_id UUID NOT NULL REFERENCES candidates(id),
  build_ok BOOLEAN,
  test_pass_rate NUMERIC(5,4),
  lint_errors INT,
  type_errors INT,
  critical_security_issues INT,
  high_security_issues INT,
  required_coverage NUMERIC(5,4),
  benchmark_json JSONB,
  policy_violations JSONB,
  coverage_json JSONB,
  gate_passed BOOLEAN NOT NULL,
  gate_failures JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_validations_candidate_id ON validations(candidate_id);
```

### judgments

```sql
CREATE TABLE judgments (
  id UUID PRIMARY KEY,
  task_id UUID NOT NULL REFERENCES tasks(id),
  judge_provider TEXT NOT NULL,
  judge_model TEXT NOT NULL,
  rubric_version TEXT NOT NULL,
  judgment_json JSONB NOT NULL,
  winner_candidate_id UUID REFERENCES candidates(id),
  decision TEXT NOT NULL,
  confidence NUMERIC(4,3),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_judgments_task_id ON judgments(task_id);
```

**Decision values:** `accept`, `revise_then_accept`, `no-winner`

### refinements

```sql
CREATE TABLE refinements (
  id UUID PRIMARY KEY,
  task_id UUID NOT NULL REFERENCES tasks(id),
  base_candidate_id UUID NOT NULL REFERENCES candidates(id),
  refined_json JSONB NOT NULL,
  refinement_log JSONB NOT NULL,
  revalidation_id UUID REFERENCES validations(id),
  revalidation_passed BOOLEAN,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_refinements_task_id ON refinements(task_id);
```

### final_outputs

```sql
CREATE TABLE final_outputs (
  id UUID PRIMARY KEY,
  task_id UUID NOT NULL REFERENCES tasks(id),
  final_answer_json JSONB NOT NULL,
  final_text TEXT NOT NULL,
  decision_report JSONB NOT NULL,
  validation_report JSONB NOT NULL,
  artifact_manifest JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_final_outputs_task_id ON final_outputs(task_id);
```

### audit_events

```sql
CREATE TABLE audit_events (
  id UUID PRIMARY KEY,
  task_id UUID NOT NULL REFERENCES tasks(id),
  event_type TEXT NOT NULL,
  actor TEXT NOT NULL DEFAULT 'system',
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_events_task_id ON audit_events(task_id);
CREATE INDEX idx_audit_events_event_type ON audit_events(event_type);
CREATE INDEX idx_audit_events_created_at ON audit_events(created_at);
```

**Event types:** `task_created`, `task_normalized`, `rubric_generated`, `candidate_generated`, `validation_completed`, `gate_failed`, `judgment_completed`, `refinement_completed`, `revalidation_completed`, `finalized`, `error`, `human_review_requested`

---

## Entity Relationships

```
tasks 1──N candidates
candidates 1──1 validations
tasks 1──N judgments
tasks 1──N refinements
tasks 1──1 final_outputs
tasks 1──N audit_events
```

---

## Final Output JSON Structure

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
    "why_selected": [
      "passed all hard gates",
      "best security posture",
      "highest weighted score after validation"
    ],
    "comparison_table": [
      {
        "candidate_id": "cand_A",
        "gate_passed": true,
        "weighted_total": 8.28,
        "final_score": 85.3
      },
      {
        "candidate_id": "cand_B",
        "gate_passed": true,
        "weighted_total": 7.95,
        "final_score": 81.7
      }
    ]
  },
  "validation_report": {
    "candidates_generated": 3,
    "candidates_passed_gates": 2,
    "candidates_eliminated": ["cand_C: build_ok failed"],
    "winner_validation": {}
  },
  "audit_refs": {
    "task_id": "...",
    "trace_id": "...",
    "total_cost_usd": 0.42,
    "total_latency_ms": 45000
  }
}
```
