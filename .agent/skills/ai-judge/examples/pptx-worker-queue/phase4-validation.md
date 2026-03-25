# Phase 4 — Validation (Requirement Coverage Gate)

This is an architecture task; hard gates use "requirement coverage" instead of programmatic build/test.

| Gate | cand_A | cand_B | cand_C |
|------|:------:|:------:|:------:|
| Persistent state and history | ✅ DDB jobs + job_runs | ✅ SFN execution history + S3 | ✅ Temporal / Argo history |
| Scheduling | ✅ EventBridge Scheduler | ✅ EventBridge → StartExecution | ✅ Temporal Schedule / Cron |
| Failure retry / poison message | ✅ SQS replay + DLQ + exponential backoff | ✅ SFN built-in retry policy | ✅ Workflow retry policy |
| Rerun after code fix | ✅ New image + new run_id (version field) | ✅ New version state machine + new execution | ✅ Workflow version + reset/replay |
| Complete EKS deployment | ✅ Worker + KEDA + IRSA | ⚠️ EKS mainly connects via Activity, network and IAM design need separate explanation | ✅ Fully on EKS (highest operational burden) |

**Gate Results:**
- cand_A: ✅ Passed all
- cand_B: ✅ Passed (EKS integration needs supplementary explanation, not a hard failure)
- cand_C: ✅ Passed (Operational complexity is a must-fix item)

All three enter the judgment phase.

## Limitation Note

If the constraint is "**all logic must strictly reside within EKS, without relying on AWS managed orchestration services**":

- cand_B: Step Functions is a managed service and would be down-weighted
- cand_A: SQS + EventBridge are still managed, but more lightweight than SFN, usually acceptable
- cand_C: Best fits "purely self-hosted within EKS" but has the highest operational cost
