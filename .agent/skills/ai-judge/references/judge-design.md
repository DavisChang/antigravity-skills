# Judge Design

The AI judge is a **technical arbiter**, not a solution author. It evaluates candidates against a rubric using validation evidence. It does not create, modify, or supplement solutions.

---

## What the Judge CAN Do

- Score each rubric criterion with numerical values
- Cite specific evidence from candidates and validation results
- Deduct points based on validation failures
- Decide: `accept` / `revise_then_accept` / `no-winner`
- Produce a `must_fix` list for the refiner — **each item must be specific and actionable** (e.g. "Add rate limiting to POST /auth/token" not "improve security")
- Suggest a `merge_plan` — must name exactly which items to borrow and from which candidate ID

## What the Judge CANNOT Do

- Add requirements not in the task spec
- Award points for length, confidence, or writing style
- Ignore failed tests or security issues
- Say "I feel B is better" without evidence
- Override hard gate failures
- Modify candidate outputs

---

## Judge Output Format

```json
{
  "rubric_version": "v1",
  "candidate_reviews": [
    {
      "candidate_id": "cand_A",
      "scores": {
        "correctness": 8.4,
        "completeness": 7.8,
        "security": 9.1,
        "feasibility": 8.0,
        "maintainability": 7.9,
        "clarity": 7.5
      },
      "weighted_total": 8.28,
      "strengths": [
        "OAuth flow is complete",
        "Includes refresh token rotation"
      ],
      "weaknesses": [
        "Missing migration strategy",
        "Insufficient deployment rollback documentation"
      ],
      "must_fix": [
        "Add database migration plan",
        "Add audit event schema"
      ],
      "evidence": [
        "api_spec defines callback and revoke endpoints",
        "risks section addresses token theft with mitigation"
      ]
    }
  ],
  "winner_candidate_id": "cand_A",
  "decision": "revise_then_accept",
  "confidence": 0.81,
  "merge_plan": [
    {
      "base": "cand_A",
      "borrow_from": "cand_C",
      "items": ["cost estimate", "deployment topology"]
    }
  ]
}
```

---

## Decision Types

| Decision | Meaning | Next Step |
|----------|---------|-----------|
| `accept` | Winner is ready as-is | → Final output |
| `revise_then_accept` | Winner needs specific fixes | → Refiner → Re-validate → Final output |
| `no-winner` | All candidates failed | → Report failure + reasons |

---

## Scoring Rules

1. Each criterion is scored 0–10
2. Weighted total = Σ(score × weight)
3. Validation results adjust the weighted total:
   - Failed tests: mandatory deduction
   - Security issues: severity-based deduction
   - Lint/type errors: minor deduction
4. The final combined score uses the aggregation formula from [validation-layer.md](validation-layer.md)

---

## Evidence Requirements

Every score must be backed by at least one piece of evidence:

| Score Range | Evidence Required |
|-------------|-------------------|
| 9–10 | Specific section/code that excels, with explanation |
| 7–8 | What the candidate does well, and what's missing |
| 5–6 | What's adequate and what's notably absent |
| 0–4 | Specific failure points with validation data |

---

## Dual Judge Protocol (High-Risk Tasks)

For `security_compliance` tasks or when risk level is `high`:

1. Run two independent judges with different models
2. Compare their `winner_candidate_id` and scores
3. If they agree → proceed with the consensus winner
4. If they disagree:
   - Score difference < 1.0 point → average the scores, use the higher-confidence judge's winner
   - Score difference ≥ 1.0 point → trigger tie-breaker judge OR escalate to human review

---

## Judge Disagreement Output

```json
{
  "judge_1": {
    "winner": "cand_A",
    "confidence": 0.82,
    "weighted_total": 8.28
  },
  "judge_2": {
    "winner": "cand_B",
    "confidence": 0.76,
    "weighted_total": 7.95
  },
  "disagreement": true,
  "score_delta": 0.33,
  "resolution": "tie_breaker_judge | human_review | average_scores"
}
```

---

## Judge Prompt

See full prompt template → [prompt-templates.md](prompt-templates.md#judge-prompt)

Key rules embedded in the prompt:
- Only use: task spec, rubric, candidates, validation results
- No new requirements beyond the task spec
- No scoring based on length, tone, or confidence
- Critical test failures and security issues must be heavily penalized
- Every score must have specific evidence
- If all candidates fail, output `no-winner`
- Output must conform to the judgment schema
