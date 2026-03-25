# Validation Layer

The validation layer is **more important than the judge**. It provides objective, programmatic, deterministic checks that no amount of persuasive writing can bypass.

---

## Two-Stage Decision: Gates → Scores

### Stage 1: Hard Gates (Pass/Fail)

Any candidate that fails a hard gate is **immediately eliminated** — the judge never sees it.

```json
{
  "gates": [
    {"name": "build_ok",                "rule": "== true"},
    {"name": "test_pass_rate",          "rule": ">= 0.95"},
    {"name": "critical_security_issues","rule": "== 0"},
    {"name": "required_coverage",       "rule": ">= 0.90"}
  ]
}
```

### Stage 2: Weighted Score (Ranking)

Only candidates that pass all gates are scored and ranked.

```
final_score =
  0.45 × judge_score +
  0.20 × test_score +
  0.15 × security_score +
  0.10 × performance_score +
  0.10 × coverage_score
```

---

## Validation Checks by Task Type

> **Task-type routing:** Use the correct section for the task type. For `architecture_and_code`, apply both the Architecture AND Code checks.

### Architecture Tasks

| Check | Method | Gate? |
|-------|--------|:-----:|
| Candidate schema compliance | JSON schema validator | Yes |
| Required deliverables coverage | Checklist match vs `task_spec.deliverables` | Yes (≥ 90%) |
| Acceptance criteria addressed | Each AC must appear in at least one of: architecture, risks, api_spec, deployment_notes | Yes |
| `missing_fields` is empty or justified | Candidate must explain any absent deliverable | No (scored) |
| Contradiction detection | Logical consistency within the candidate output | No (scored) |
| Risk coverage | At least one risk entry per high-severity acceptance criterion | No (scored) |
| Forbidden content / policy check | Regex + policy rules | Yes |

**Note:** Architecture tasks do not run build/test/lint. Hard gates are requirement-coverage checks only.

### Code Tasks

| Check | Tool | Gate? |
|-------|------|:-----:|
| Compile / build | Language compiler | Yes |
| Unit tests | Test runner | Yes (≥ 95% pass rate) |
| Integration tests | Test runner | No (scored) |
| Lint | ESLint, Ruff, etc. | No (scored) |
| Type check | tsc, mypy, etc. | No (scored) |
| Dependency scan | npm audit, pip-audit | No (scored) |
| SAST | Semgrep, Bandit, etc. | Yes (0 critical) |
| Benchmark | Custom runner | No (scored) |

### Document / Advice Tasks

| Check | Method | Gate? |
|-------|--------|:-----:|
| JSON schema validation | jsonschema | Yes |
| Requirement coverage | Checklist match | Yes (≥ 90%) |
| Contradiction detection | Rule-based + LLM | No (scored) |
| Forbidden content check | Regex + policy rules | Yes |
| External constraint check | Custom rules | Depends |

### SQL Tasks

| Check | Method | Gate? |
|-------|--------|:-----:|
| Syntax validation | SQL parser | Yes |
| Schema consistency | Cross-reference DDL | Yes |
| Migration safety | Linter (squawk, etc.) | No (scored) |
| Index coverage | Query plan analysis | No (scored) |
| Data integrity | FK / constraint check | Yes |

---

## Gate Logic Implementation

Gate thresholds differ by task type. The `rubric.hard_gates` field is the authoritative source; the defaults below apply when no custom gates are specified.

```python
class ValidatorService:
    def passes_gate(self, result: dict, rubric: dict, task_type: str) -> bool:
        # For code / architecture_and_code tasks
        if task_type in ("code", "architecture_and_code", "sql"):
            if not result.get("build_ok", False):
                return False
            if result.get("test_pass_rate", 0) < 0.95:
                return False
            if result.get("critical_security_issues", 1) > 0:
                return False
            if result.get("required_coverage", 0) < 0.90:
                return False

        # For architecture / documentation / advice tasks
        if task_type in ("architecture", "documentation", "advice"):
            if result.get("required_coverage", 0) < 0.90:
                return False
            if result.get("schema_valid") is False:
                return False
            if result.get("policy_violations"):
                critical = [v for v in result["policy_violations"]
                            if v.get("severity") == "critical"]
                if critical:
                    return False

        # Apply any custom gates from the rubric (overrides defaults)
        for gate_expr in rubric.get("hard_gates", []):
            if not self._eval_gate(gate_expr, result):
                return False

        return True

    def _eval_gate(self, gate_expr: str, result: dict) -> bool:
        """Evaluate a gate expression like 'test_pass_rate >= 0.95'.
        In production, use a safe expression evaluator or OPA."""
        # Minimal safe evaluator — extend as needed
        import re
        m = re.match(r"(\w+)\s*(==|!=|>=|<=|>|<)\s*(.+)", gate_expr.strip())
        if not m:
            return True  # unknown expression → pass (log warning)
        field, op, value_str = m.groups()
        actual = result.get(field)
        if actual is None:
            return False  # field missing → gate fails
        try:
            expected = float(value_str) if "." in value_str else int(value_str)
            ops = {"==": lambda a, b: a == b, "!=": lambda a, b: a != b,
                   ">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b,
                   ">": lambda a, b: a > b, "<": lambda a, b: a < b}
            return ops[op](actual, expected)
        except (ValueError, KeyError):
            return True  # cannot evaluate → pass conservatively (log warning)
```

---

## Two-Level Scoring — How Rubric Weights and Aggregate Score Relate

The system uses **two independent scoring layers** that serve different purposes:

| Layer | Where | What it produces | Used by |
|-------|-------|-----------------|---------|
| **Layer 1: Rubric criterion weights** | Phase 2 (Rubric) + Phase 5 (Judge) | `weighted_total` = Σ(criterion_score × weight) per candidate — this is the **judge_score** | Judge, comparison table |
| **Layer 2: Aggregate score** | After Phase 5 | Final combined score = `judge_score` + validation metrics | Ranking; tie-breaking |

**Flow:**
```
Phase 2: rubric weights defined (correctness 0.30, security 0.20, ...)
   ↓
Phase 5: judge scores each criterion (0–10) → computes weighted_total (= judge_score)
   ↓
aggregate_score(judge_score, validation) → final_score used for ranking
```

The rubric weights shape the judge's opinion. The aggregate formula then grounds that opinion in objective validation data (tests, security scan, benchmark).

## Score Aggregation

```python
def aggregate_score(judge_score: float, validation: dict) -> float:
    test_score = validation["test_pass_rate"] * 100

    security_score = 100 if validation["critical_security_issues"] == 0 else 0
    security_score -= min(validation["high_security_issues"] * 10, 40)

    perf_latency = validation.get("benchmark", {}).get("p95_latency_ms", 1000)
    performance_score = max(0, 100 - perf_latency / 5)

    coverage_score = validation["required_coverage"] * 100

    return round(
        0.45 * judge_score +
        0.20 * test_score +
        0.15 * security_score +
        0.10 * performance_score +
        0.10 * coverage_score,
        2
    )
```

---

## Validation Output Format

Each candidate produces one validation result:

```json
{
  "candidate_id": "cand_B",
  "build_ok": true,
  "test_pass_rate": 0.97,
  "lint_errors": 0,
  "type_errors": 0,
  "critical_security_issues": 0,
  "high_security_issues": 1,
  "required_coverage": 0.94,
  "benchmark": {
    "p95_latency_ms": 82,
    "memory_mb": 143
  },
  "policy_violations": [],
  "gate_passed": true,
  "gate_failures": []
}
```

When a gate fails:

```json
{
  "candidate_id": "cand_C",
  "build_ok": false,
  "test_pass_rate": 0.0,
  "gate_passed": false,
  "gate_failures": [
    "build_ok: expected true, got false",
    "test_pass_rate: expected >= 0.95, got 0.0 (cannot test without build)"
  ]
}
```

---

## Sandbox Requirements

All candidate code runs in a sandbox. See [security-and-sandbox.md](security-and-sandbox.md) for details.

Key rules:
- Network egress off by default
- CPU / memory / time limits enforced
- Read-only base image
- Temporary filesystem
- No real secrets injected
- Artifacts scanned before extraction
