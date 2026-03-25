# Phase 6–7 — Refined Architecture (Enhanced Version A)

## Refined Architecture Summary

| Layer | Selection | Description |
|-------|-----------|-------------|
| **Scheduling** | EventBridge Scheduler | cron expression triggers "create job record + send SQS"; manual rerun only goes through API, no duplicate scheduling |
| **Queue** | SQS Standard | Lightweight; evaluate FIFO + MessageGroupId only if strict ordering is required |
| **Worker** | EKS Deployment + KEDA | KEDA ScaledObject scales based on `ApproximateNumberOfMessages` |
| **State** | DynamoDB: `jobs` + `job_runs` + optional `artifacts` | See dynamodb-design.md |
| **Failure** | Exponential backoff retry → DLQ → manual or rerun after code fix | rerun = new run_id; old run is saved for auditing |
| **Deployment** | EKS + IRSA + Secrets Manager | IRSA binds ServiceAccount to access SQS / S3 / DDB; Helm / Kustomize per environment |

## Must-Fix Implementation (Absorbed from Judgment)

### 1. Job State Machine

```
pending → running → succeeded
                  ↘ failed (retriable)
                  ↘ dead (exceeded retry limit, enters DLQ)
```

- **SQS Message**: Only represents "a single execution intent", not the authoritative source of business state
- **DynamoDB**: The single source of truth for business state (using `ConditionExpression` for state transitions to avoid concurrent worker conflicts)

### 2. Idempotency Key

```
idempotency_key = hash(user_id + input_s3_key + output_format)
```

- Before creating a job, check DDB for any unfinished job with the same key
- SQS message also carries `job_id`, worker checks DDB state before processing

### 3. S3 Path Design

```
Input: s3://bucket/inputs/{user_id}/{job_id}/original.pptx
Output: s3://bucket/outputs/{user_id}/{job_id}/{run_id}/result.{format}
```

- Keep input for N days (based on requirement; S3 Lifecycle management)
- Use Pre-signed URL for users to retrieve output
- run_id path supports comparing multiple reruns

### 4. DDB Mandatory Fields (Borrowed from Candidate C's versioned semantics)

Added to `job_runs`:
- `worker_version`: `container_image_digest` (which image was used for each run)
- `workflow_version`: Application version or git sha
- `rerun_of_run_id`: If this is a rerun, points to the previous failed run_id

### 5. EKS Worker Key Settings

- **KEDA ScaledObject**: `sqsQueueName`, `queueLength` threshold, `minReplicaCount: 0` (allow scaling to 0), `maxReplicaCount`
- **Resource limits**: Must set `requests/limits` (PPTX conversion can be CPU/Memory intensive)
- **SQS Visibility Timeout**: Must be > expected max conversion time; worker periodically heartbeats to extend visibility
- **Pod Disruption Budget**: Prevent task interruption during scale-down
- **Graceful shutdown**: Worker completes current task or resets visibility upon receiving SIGTERM

### 6. Observability (Borrowed from Candidate B's auditing semantics)

- **Structured logs**: Each log includes `job_id`, `run_id`, `attempt`, `worker_version`
- **CloudWatch Metrics / Alerting**:
  - SQS `ApproximateNumberOfMessagesNotVisible` (inflight count)
  - SQS `ApproximateAgeOfOldestMessage` (age of oldest pending message → alert if exceeds threshold)
  - DLQ message count alert
- **Distributed Trace**: API → SQS → Worker → S3, with `X-Trace-Id` (OpenTelemetry)

## Deployment Architecture Key Points

```
AWS Account
├── EventBridge Scheduler
│   └── Rule → Target: Job API Lambda or Fargate Task (create job + enqueue)
├── SQS Standard Queue + DLQ
├── DynamoDB (On-Demand): jobs, job_runs
├── S3: inputs / outputs (separate buckets or prefixes)
└── EKS Cluster
    ├── Namespace: pptx-worker
    │   ├── Deployment: worker (IRSA ServiceAccount)
    │   ├── ScaledObject (KEDA)
    │   └── NetworkPolicy (optional)
    ├── KEDA Controller (Namespace: keda)
    └── IRSA → IAM Role
        ├── SQS: ReceiveMessage, DeleteMessage, ChangeMessageVisibility
        ├── S3: GetObject (inputs), PutObject (outputs)
        ├── DynamoDB: GetItem, PutItem, UpdateItem (jobs, job_runs)
        └── Secrets Manager: GetSecretValue (app secrets)
```

## Risk Register

| Risk | Severity | Mitigation |
|------|----------|------------|
| Inconsistency between queue and DDB state | high | DDB is authoritative; use ConditionExpression as optimistic lock before consuming |
| Long-running conversion timeout (SQS visibility) | high | Chunking, progress checkpoints; worker heartbeat periodically extends visibility |
| Duplicate processing | medium | idempotency key; configure output S3 object versioning |
| Cold start latency after KEDA scales to 0 | medium | Set `minReplicaCount: 1` if sensitive to latency; evaluate KEDA cool-down parameters |
| Task loss during Pod disruption | medium | Graceful shutdown + PDB; idempotent task design |
| DLQ untouched for a long time | medium | DLQ alert + periodic manual review; provide rerun API |
