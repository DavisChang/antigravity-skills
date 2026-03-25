# Phase 3 — Candidates

## Candidate A — Correctness-First: EventBridge Scheduler + SQS + DynamoDB + EKS Worker

**Role:** correctness-first

**Summary:**  
Uses AWS managed scheduler (EventBridge Scheduler) and standard queue (SQS) as the core;  
**True task status** is stored in DynamoDB (`jobs` + `job_runs`), SQS is only responsible for "whether to trigger an execution attempt", avoiding the "queue as database" anti-pattern.

**Architecture:**

- EventBridge Scheduler / Rules → SQS Standard (Optional FIFO if strict ordering is needed)
- EKS Deployment/StatefulSet Workers (scaled via KEDA ScaledObject)
- S3: Input (raw PPTX), Output (conversion result)
- DynamoDB: `jobs` (business entity), `job_runs` (each execution attempt row), optional `artifacts`

**Scheduling:**  
One `schedule expression` per user or per batch; manual rerun = API writes a new `job_runs` record + sends to SQS, without creating duplicate schedules.

**Rerun semantics:**  
Records version, `attempt`, `worker_version` (image digest) by `job_id` dimension;  
rerun = new `run_id`, keeping the old run for auditing;  
DLQ handles poison messages; simply update the image and initiate a new run after fixing the code.

**Risks:**
- FIFO throughput and SQS visibility timeout need tuning
- Poor DynamoDB design may cause hot partitions

---

## Candidate B — Security-First: Step Functions + EKS Activity + S3

**Role:** security-first (security / audit prioritization)

**Summary:**  
Builds the "conversion steps" as an **AWS Step Functions state machine**, with built-in history, retries, and visual tracking;  
PPTX conversion runs on EKS workers using the **Activity Worker pattern**.

**Architecture:**

- API → StartExecution (SFN Standard Workflow)
- State machine includes `input_s3_key`, `format`, `retry_count`
- EKS Worker polls SFN Activity Task (GetActivityTask / SendTaskSuccess / SendTaskFailure)
- CloudWatch Logs: Full events for each execution
- S3: Input / Output

**Scheduling:**  
EventBridge → `StartExecution`;  
Rerun = new execution or Redrive (from the failed node).

**Rerun semantics:**  
Execution history serves as audit log;  
Publish new deployment after fixing code, new executions use the new version of the state machine definition;  
Old executions are kept as read-only.

**Risks:**
- Long conversion requires heartbeat (SendTaskHeartbeat), otherwise Step Functions times out
- Cost increases with the number of state transitions
- EKS Activity Worker integration is less straightforward, requiring maintenance of the polling loop

---

## Candidate C — Cost-First: Temporal (or Argo Workflows) on EKS + PostgreSQL + S3

**Role:** cost-first / control-first (maximum control)

**Summary:**  
Self-hosted **Temporal** or **Argo Workflows** within EKS;  
Workflow code is versioned, **replay / reset** semantics closely match "fix code and rerun";  
Argo uses CRD (WorkflowTemplate) to express DAGs and retries.

**Architecture:**

- Temporal Cluster (or Argo Server) on EKS (requires persistence: PostgreSQL / MySQL)
- Workflow defines conversion steps (Multiple Activities / Multiple Tasks)
- Activity Worker calls conversion logic
- Execution history stored in Temporal persistence / Argo DB
- Artifact input/output on S3

**Scheduling:**  
Temporal Schedule (cron expression) or external cron triggering `StartWorkflow`;  
Rerun = `ResetWorkflow` to a specific event point, or start a new Run.

**Rerun semantics:**  
Temporal replay can precisely control which step to rerun from;  
Old history is kept intact.

**Risks:**
- Highest operational complexity (Temporal cluster includes frontend/history/matching/worker service)
- Steep learning curve
- If Temporal persistence is unstable, the entire system is affected
