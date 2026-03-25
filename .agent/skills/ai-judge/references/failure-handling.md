# Failure Handling

The system must handle failures gracefully at every stage. The default behavior is: fail safely, explain clearly, never produce a fake result.

---

## No-Winner

When all candidates fail hard gates or the judge determines no candidate is adequate:

```json
{
  "decision": "no-winner",
  "reasons": [
    "All candidates failed required coverage gate (< 0.90)",
    "2 candidates had critical security issues",
    "1 candidate failed build"
  ],
  "candidate_summary": [
    {"candidate_id": "cand_A", "gate_failures": ["required_coverage: 0.82"]},
    {"candidate_id": "cand_B", "gate_failures": ["critical_security_issues: 2"]},
    {"candidate_id": "cand_C", "gate_failures": ["build_ok: false"]}
  ],
  "next_action": "request_regeneration_with_tighter_constraints",
  "suggestions": [
    "Relax the coverage threshold if 0.90 is too strict for this task",
    "Add more explicit constraints to guide candidates",
    "Try different model/role combinations"
  ]
}
```

**Rules:**
- Never force-pick a winner when all fail
- Always explain WHY each candidate failed
- Suggest actionable next steps
- Log the no-winner event for pattern analysis

---

## Judge Disagreement (Dual Judge)

When two judges disagree on the winner:

| Condition | Resolution |
|-----------|-----------|
| Score difference < 1.0 | Average scores, use higher-confidence judge's winner |
| Score difference ≥ 1.0, both > 0.6 confidence | Trigger tie-breaker judge (third judge) |
| Score difference ≥ 1.0, either < 0.6 confidence | Escalate to human review |
| Different decisions (accept vs revise) | Use the more conservative decision |

```json
{
  "judge_1": {
    "winner": "cand_A",
    "confidence": 0.82,
    "decision": "accept"
  },
  "judge_2": {
    "winner": "cand_B",
    "confidence": 0.76,
    "decision": "revise_then_accept"
  },
  "resolution": "tie_breaker_judge",
  "reason": "Score delta 1.2, both above 0.6 confidence"
}
```

---

## Stage-Level Failures

### Model Timeout / Failure

| Scenario | Action |
|----------|--------|
| Candidate model times out | Retry once with extended timeout; if still fails, use fallback model |
| Candidate model returns error | Retry once; if fails, skip this candidate (proceed with fewer candidates) |
| All candidate models fail | Abort task, report infrastructure failure |
| Judge model times out | Retry with extended timeout; fall back to alternate judge model |
| Judge model returns invalid output | Retry once; if invalid again, escalate to human review |

### Sandbox Failure

| Scenario | Action |
|----------|--------|
| Sandbox container fails to start | Retry on different worker; if fails, report infrastructure issue |
| Sandbox times out | Kill container, mark validation as timeout, candidate gets gate_failed |
| Sandbox OOM | Kill container, mark validation as OOM, candidate gets gate_failed |
| All sandboxes unavailable | Queue task for retry, alert operations |

### Refinement Failure

| Scenario | Action |
|----------|--------|
| Refined output fails gate | Fall back to original winner, mark must-fix items as unresolved |
| Refined output breaks existing tests | Revert to original winner, log the regression |
| Refiner model fails | Use original winner as final output, note in report |

---

## Retry Policy

| Stage | Max Retries | Backoff | Timeout |
|-------|:-----------:|---------|---------|
| Normalization | 2 | 1s, 3s | 30s |
| Rubric generation | 2 | 1s, 3s | 30s |
| Candidate generation | 1 | 5s | 120s |
| Validation | 2 | 2s, 5s | 300s |
| Judge | 2 | 3s, 10s | 60s |
| Refinement | 1 | 5s | 120s |
| Re-validation | 2 | 2s, 5s | 300s |

---

## Fallback Model Map

When the primary model is unavailable:

| Primary | Fallback 1 | Fallback 2 |
|---------|-----------|-----------|
| Claude Opus | Claude Sonnet | GPT-4o |
| GPT-4o | Claude Sonnet | GPT-4o-mini |
| Claude Sonnet | GPT-4o-mini | Gemini Pro |
| Open-source (Llama) | Mistral | GPT-4o-mini |

---

## Human Escalation Triggers

Automatically request human review when:

| Trigger | Reason |
|---------|--------|
| No-winner on second attempt | Repeated failures suggest task needs human guidance |
| Judge disagreement unresolvable | Three-judge tie or all low confidence |
| Security/compliance task | Always requires human gate before finalization |
| Confidence < 0.5 | Judge is not sure enough to decide |
| Policy violation in winner | Even the best candidate has compliance issues |
| Cost exceeds budget | Unusual resource consumption |
