# Cost Control

AI model calls are the primary cost driver. The system uses dynamic routing and tiered strategies to control spend.

---

## Core Strategy

1. Use **cheaper models** for initial candidate generation when possible
2. Only run **expensive judge models** on candidates that pass hard gates
3. Scale candidate and judge count based on **task risk level**
4. Track cost per task and alert on anomalies

---

## Dynamic Routing by Task Type

| Task Type | Candidates | Judges | Refine? | Estimated Cost |
|-----------|:----------:|:------:|:-------:|:--------------:|
| Advice / documentation | 2 | 1 | No | $ |
| Architecture design | 3 | 1 | Yes | $$ |
| Code implementation | 3 | 1 | Yes | $$ |
| Architecture + code | 3 | 1 | Yes | $$$ |
| Security / compliance | 4 | 2 | Yes + human gate | $$$$ |

---

## Model Tiering

### Tier 1: Generation (Candidates)

Use capable but cost-efficient models:
- Claude Sonnet / Haiku for structured outputs
- GPT-4o-mini for fast iteration
- Open-source models (Llama, Mistral) for cost-sensitive tasks

### Tier 2: Judgment

Use the most capable models available:
- Claude Opus / Sonnet for nuanced evaluation
- GPT-4o for complex comparisons
- Only called on gate-passed candidates (typically 2–3 out of 3–4)

### Tier 3: Refinement

Use the same tier as generation — refinement is targeted patching, not full reasoning.

---

## Cost Optimization Tactics

| Tactic | Savings | Risk |
|--------|---------|------|
| Gate elimination before judge | 20–40% | None — gated candidates are objectively bad |
| 2 candidates for low-risk tasks | 30% | Less diversity |
| Skip refine for advice tasks | 10–15% | Minor quality loss on non-code tasks |
| Cache repeated rubrics | 5% | Stale rubric if task types evolve |
| Batch candidates to same model | 5–10% | Less diversity (mitigated by role variation) |
| Use structured output mode | 5% | Reduces extraction costs |

---

## Cost Tracking

### Per-Task Cost Breakdown

```json
{
  "task_id": "...",
  "cost_breakdown": {
    "normalization": 0.01,
    "rubric_generation": 0.01,
    "candidate_A": 0.08,
    "candidate_B": 0.08,
    "candidate_C": 0.06,
    "validation": 0.00,
    "judge": 0.12,
    "refinement": 0.05,
    "revalidation": 0.00,
    "total_usd": 0.41
  }
}
```

### Budget Controls

| Control | Description |
|---------|-------------|
| Per-task budget cap | Abort if estimated cost exceeds threshold |
| Daily budget cap | Pause pipeline when daily spend exceeds limit |
| Per-user rate limit | Max tasks per user per hour/day |
| Model fallback | If primary model is unavailable, fall back to cheaper alternative |

---

## When to Invest More

Spend more tokens/money when:
- Task is security or compliance related
- Task affects production systems
- Previous attempt resulted in no-winner
- User explicitly requests higher rigor
- The task has financial or legal implications
