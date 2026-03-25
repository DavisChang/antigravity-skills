# Observability

The AI Judge system is a multi-stage pipeline where any step can fail silently or produce unexpected results. Full observability is essential — without it, debugging a bad judgment or cost spike is nearly impossible.

---

## OpenTelemetry Integration

Use OpenTelemetry for unified traces, metrics, and logs.

### Trace Structure

Each task produces one root trace with child spans for each pipeline stage:

```
task (root span)
├── normalize
├── plan (rubric generation)
├── candidate.A (generation)
├── candidate.B (generation)
├── candidate.C (generation)
├── validation.A
├── validation.B
├── validation.C
├── judge
├── refine (conditional)
├── revalidate (conditional)
└── finalize
```

Each span includes:
- Duration
- Status (ok / error)
- Relevant attributes (model name, candidate ID, scores, etc.)

---

## Required Metrics

### Pipeline Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `tasks_total` | Counter | Total tasks created, by status |
| `task_duration_seconds` | Histogram | End-to-end task duration |
| `task_stage_duration_seconds` | Histogram | Duration per pipeline stage |
| `tasks_in_progress` | Gauge | Currently running tasks |

### Candidate Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `candidate_generation_latency_ms` | Histogram | Per-candidate generation time |
| `candidate_token_input` | Histogram | Input tokens per candidate |
| `candidate_token_output` | Histogram | Output tokens per candidate |
| `candidate_cost_usd` | Histogram | Estimated cost per candidate |

### Validation Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `validation_failure_rate` | Gauge | Percentage of candidates failing gates |
| `validation_duration_ms` | Histogram | Per-candidate validation time |
| `sandbox_failure_rate` | Gauge | Sandbox infrastructure failures |
| `gate_failure_by_type` | Counter | Gate failures by gate name |

### Judge Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `judge_disagreement_rate` | Gauge | Rate of dual-judge disagreements |
| `no_winner_rate` | Gauge | Rate of no-winner outcomes |
| `judge_confidence` | Histogram | Judge confidence distribution |
| `judge_score_distribution` | Histogram | Score distribution across candidates |

### Cost Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `average_cost_per_task` | Gauge | Mean USD per completed task |
| `total_cost_usd` | Counter | Cumulative cost |
| `cost_by_model` | Counter | Cost broken down by model |
| `cost_by_task_type` | Counter | Cost broken down by task type |

---

## Required Audit Events

Every significant action is logged as an audit event. The audit log is **append-only** — events cannot be modified or deleted.

### Events to Capture

| Event | Payload Includes |
|-------|-----------------|
| `task_created` | Raw input, user ID |
| `task_normalized` | Normalized spec |
| `rubric_generated` | Full rubric JSON |
| `candidate_generated` | Candidate ID, model, role, prompt version, response hash |
| `validation_completed` | Candidate ID, all validation metrics, gate pass/fail |
| `gate_failed` | Candidate ID, which gates failed, values |
| `judgment_completed` | Full judgment JSON, winner, decision |
| `refinement_completed` | Refinement log, changes made |
| `revalidation_completed` | Re-validation results |
| `finalized` | Final output hash, cost summary |
| `error` | Error type, stage, stack trace |
| `human_review_requested` | Reason, task stage, assigned reviewer |

### What to Store

For full reproducibility, store:

- Original user input
- Normalized spec
- Rubric
- Every prompt version sent to every model
- Every candidate output (full JSON)
- Every validation report
- Judgment output
- Refinement log
- Final merge plan
- Final output

---

## Alerting Rules

| Condition | Alert Level |
|-----------|-------------|
| `no_winner_rate > 0.3` over 1 hour | Warning |
| `sandbox_failure_rate > 0.1` over 15 min | Critical |
| `task_duration_seconds > 300` | Warning |
| `average_cost_per_task > $2.00` | Warning |
| `judge_disagreement_rate > 0.4` over 1 hour | Warning |
| `validation_failure_rate > 0.8` over 1 hour | Critical |
