# DynamoDB Table Design — PPTX Worker Queue

## Design Principles

- **DynamoDB is the single source of truth for business state**; SQS is merely the execution trigger
- Use `ConditionExpression` for state transitions (optimistic locking) to prevent concurrent worker conflicts
- rerun = new `run_id` row, old runs are not deleted (complete audit history)

---

## Table 1: `jobs` (Business Entity)

**Purpose:** One "job" (one user upload + one conversion request) corresponds to one row.

| Attribute | Type | Role | Description |
|-----------|------|------|-------------|
| `job_id` | String | **PK** | UUID / ULID |
| `user_id` | String | — | Associated user |
| `idempotency_key` | String | — | hash(user_id + input_s3_key + output_format); prevents duplicate creation |
| `status` | String | — | pending / running / succeeded / failed / dead |
| `input_s3_key` | String | — | `inputs/{user_id}/{job_id}/original.pptx` |
| `output_format` | String | — | pdf / png / pptx etc. |
| `latest_run_id` | String | — | The latest run_id, convenient for list display |
| `schedule_id` | String | — | If originating from EventBridge (optional) |
| `created_at` | String | — | ISO 8601 |
| `updated_at` | String | — | ISO 8601 |
| `ttl` | Number | — | Epoch; optional, used for DynamoDB TTL auto-cleanup |

**GSI (Select based on query needs):**

| GSI Name | PK | SK | Applicable Query |
|----------|----|----|------------------|
| `gsi-user-created` | `user_id` | `created_at` | User listing recent N jobs |
| `gsi-status-updated` | `status` | `updated_at` | Ops querying "all failed jobs" |

---

## Table 2: `job_runs` (One row per execution)

**Purpose:** Records every execution attempt, including retries and reruns.

| Attribute | Type | Role | Description |
|-----------|------|------|-------------|
| `job_id` | String | **PK** | Corresponds to jobs table |
| `run_id` | String | **SK** | ULID (chronological, convenient for sorting) |
| `status` | String | — | pending / running / succeeded / failed |
| `attempt` | Number | — | The Nth attempt under the same job_id (including retries) |
| `worker_version` | String | — | container image digest (sha256:...) |
| `workflow_version` | String | — | Application version or git sha |
| `rerun_of_run_id` | String | — | If this is a rerun, points to the previous failed run_id |
| `error_code` | String | — | Error category (CONVERT_TIMEOUT / OOM / etc.) |
| `error_message` | String | — | Error summary |
| `output_s3_key` | String | — | `outputs/{user_id}/{job_id}/{run_id}/result.{format}` |
| `started_at` | String | — | ISO 8601 |
| `finished_at` | String | — | ISO 8601 |
| `sqs_message_id` | String | — | For tracking (optional) |

**Query Pattern:**

```
Query PK=job_id, ScanIndexForward=false
→ Latest run is first (sorted by run_id ULID)
```

---

## Table 3: `artifacts` (Optional)

If there are many output artifacts, or if there's a need to independently query which S3 object corresponds to which run:

| Attribute | Type | Role |
|-----------|------|------|
| `job_id` | String | **PK** |
| `artifact_id` | String | **SK** (`{run_id}#{kind}`) |
| `run_id` | String | — |
| `kind` | String | — | input / output / thumbnail |
| `s3_bucket` | String | — |
| `s3_key` | String | — |
| `size_bytes` | Number | — |
| `checksum_sha256` | String | — |
| `created_at` | String | — |

If there are few artifacts (usually just one output), simply embedding `job_runs.output_s3_key` is sufficient, no separate table needed.

---

## State Transition Write Example (ConditionExpression)

```python
# Worker shifting from pending → running (prevents two workers mapping the same task concurrently)
table.update_item(
    Key={"job_id": job_id, "run_id": run_id},
    UpdateExpression="SET #s = :running, started_at = :now",
    ConditionExpression="attribute_not_exists(#s) OR #s = :pending",
    ExpressionAttributeNames={"#s": "status"},
    ExpressionAttributeValues={
        ":running": "running",
        ":pending": "pending",
        ":now": datetime.utcnow().isoformat()
    }
)
```

---

## Capacity Mode Recommendations

- **On-Demand (PAY_PER_REQUEST)**: Suitable for this scenario (conversion workload is uneven, no need to provision capacity)
- If workload is large and stable: Switch to Provisioned + Auto Scaling

---

## Common Anti-patterns

| Anti-pattern | Consequence | Correct Approach |
|--------------|-------------|------------------|
| SQS message as primary business state | Message lost = State lost | DDB is authoritative, SQS is just a trigger |
| Combining `jobs` and `job_runs` in one row | Cannot query history; concurrent update conflicts | Separate into two tables; jobs only stores summary |
| Not recording `worker_version` | Cannot verify which run used the new version after fix | Mandatorily record image digest |
| No `idempotency_key` | May create duplicate jobs during retries | hash(user + input + format) for deduplication |
