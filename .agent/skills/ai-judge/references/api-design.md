# API Design

REST API for the AI Judge system. All endpoints are under `/v1/`.

---

## Endpoints

### Create Task

**POST** `/v1/tasks`

Create a new task and start the judge pipeline.

Request:
```json
{
  "input": "Design and implement a login system with Google OAuth",
  "task_type": "architecture_and_code",
  "constraints": {
    "language": "typescript",
    "database": "postgresql",
    "framework": "fastapi"
  },
  "deliverables": ["architecture", "api_spec", "code", "tests"],
  "acceptance_criteria": [
    "must compile",
    "must pass tests",
    "must support token rotation"
  ],
  "risk_level": "medium"
}
```

Response `201`:
```json
{
  "task_id": "8f5d...",
  "status": "queued",
  "created_at": "2026-03-25T12:00:00Z"
}
```

### Get Task Status

**GET** `/v1/tasks/{task_id}`

```json
{
  "task_id": "8f5d...",
  "status": "judging",
  "stage": "validation",
  "progress": {
    "candidates_generated": 3,
    "candidates_validated": 2,
    "candidates_pending": 1
  },
  "created_at": "2026-03-25T12:00:00Z",
  "updated_at": "2026-03-25T12:02:30Z"
}
```

### Get Normalized Spec

**GET** `/v1/tasks/{task_id}/spec`

Returns the normalized task specification for user confirmation.

### Get Candidates

**GET** `/v1/tasks/{task_id}/candidates`

```json
{
  "task_id": "8f5d...",
  "candidates": [
    {
      "candidate_id": "cand_A",
      "role": "correctness-first",
      "provider": "anthropic",
      "model": "claude-sonnet-4-20250514",
      "summary": "...",
      "latency_ms": 12000,
      "estimated_cost_usd": 0.08
    }
  ]
}
```

### Get Candidate Detail

**GET** `/v1/tasks/{task_id}/candidates/{candidate_id}`

Returns the full candidate output with all schema fields.

### Get Validations

**GET** `/v1/tasks/{task_id}/validations`

```json
{
  "task_id": "8f5d...",
  "validations": [
    {
      "candidate_id": "cand_A",
      "gate_passed": true,
      "build_ok": true,
      "test_pass_rate": 0.98,
      "critical_security_issues": 0
    }
  ]
}
```

### Get Judgment

**GET** `/v1/tasks/{task_id}/judgment`

Returns the full judge output including scores, evidence, decision, and merge plan.

### Get Final Output

**GET** `/v1/tasks/{task_id}/final`

Returns the complete final deliverable package including:
- Final answer with all artifacts
- Decision report with comparison table
- Validation report
- Audit references

### Get Audit Trail

**GET** `/v1/tasks/{task_id}/audit`

Returns all audit events for a task, ordered chronologically.

### Download Artifacts

**GET** `/v1/tasks/{task_id}/artifacts/{filename}`

Downloads a specific artifact file from the final output.

---

## Webhook Notifications

Optional webhook for async status updates:

**POST** (configured webhook URL)

```json
{
  "task_id": "8f5d...",
  "event": "status_changed",
  "status": "finalized",
  "timestamp": "2026-03-25T12:05:00Z"
}
```

---

## Error Responses

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task 8f5d... does not exist",
    "task_id": "8f5d..."
  }
}
```

| HTTP Status | Error Code | Description |
|-------------|-----------|-------------|
| 400 | INVALID_INPUT | Missing or malformed request fields |
| 404 | TASK_NOT_FOUND | Task ID does not exist |
| 409 | TASK_ALREADY_RUNNING | Duplicate task submission |
| 422 | NORMALIZATION_FAILED | Could not normalize the input |
| 500 | INTERNAL_ERROR | Unexpected server error |
| 503 | SERVICE_UNAVAILABLE | Dependent service (LLM, sandbox) unavailable |
