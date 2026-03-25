# Phase 5 — Judgment

## Candidate Scores (rubric weighted estimation)

| Criterion | Weight | cand_A | cand_B | cand_C |
|-----------|--------|--------|--------|--------|
| correctness | 0.28 | 8.5 | 8.0 | 8.2 |
| completeness | 0.22 | 8.2 | 7.8 | 7.5 |
| security | 0.18 | 7.8 | 9.0 | 7.5 |
| feasibility | 0.17 | 9.0 | 7.5 | 6.5 |
| maintainability | 0.10 | 8.0 | 7.0 | 6.0 |
| clarity | 0.05 | 8.5 | 8.0 | 7.5 |
| **weighted_total** | | **8.38** | **7.96** | **7.38** |

## Decision

```
winner_candidate_id: cand_A
decision: revise_then_accept
confidence: 0.79
```

## Candidate Reviews

### Candidate A — strengths
- AWS native, EventBridge + SQS have high maturity, zero extra operational components
- SQS and DynamoDB correctly separate "trigger intent" from "business state"
- EKS + KEDA combination is complete for this scenario
- rerun semantics are clear: new run_id does not affect old records

### Candidate A — weaknesses
- Lacks "node-level auditing" (only run dimension, no step dimension)
- The worker_version field after rerun is not strictly defined
- Idempotency mechanism is not explicitly explained

### Candidate A — must_fix
1. Define Job state machine (`pending` → `running` → `succeeded` / `failed` / `dead`) and explain the alignment strategy between SQS messages and DynamoDB state
2. Clarify idempotency key design (prevent duplicate processing)
3. S3 path and lifecycle policy (how long to keep inputs, presigned URLs for outputs)
4. EKS: HPA and KEDA config, resource limits, SQS visibility and heartbeat during Pod disruption
5. Observability: Structured logs with `job_id` / `run_id`, Trace from API → queue → worker

### Candidate B — strengths
- Step-level auditing and visualization are the strongest
- SFN built-in retry semantics are clear, no need to manage state manually

### Candidate B — weaknesses
- Long-running conversions require heartbeats, otherwise SFN times out, increasing complexity
- Cost increases with the number of transitions
- EKS Activity Worker integration is more complex

### Candidate C — strengths
- replay / reset semantics are closest to "fix code and rerun from a specific step"
- workflow is fully versioned

### Candidate C — weaknesses
- Highest operational complexity (Temporal cluster multiple services + persistence)
- Steep learning curve
- If persistence is unstable, the entire system is affected

## Merge Plan

| From | Items to borrow | Apply to |
|------|-----------------|----------|
| cand_B | Node-level retry semantics → Explicitly draw "state transition diagram" and CloudWatch dashboard/alerts in A's design | cand_A |
| cand_C | Versioned rerun semantics → DDB mandatory fields: `workflow_version` / `container_image_digest` / `rerun_of_run_id` | cand_A |
