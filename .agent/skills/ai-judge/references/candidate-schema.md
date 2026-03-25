# Candidate Schema

All candidates MUST output in this structured format. Free-text responses are not accepted — the judge needs a uniform schema to compare fairly.

---

## Full Candidate Output Schema

```json
{
  "candidate_id": "cand_A",
  "role": "security-first",
  "summary": "string — one paragraph overview of the approach",

  "assumptions": [
    "string — each assumption the candidate made"
  ],

  "architecture": {
    "components": ["api", "auth_service", "db", "redis"],
    "data_flow": ["browser -> api -> auth_service -> db"],
    "tradeoffs": [
      {
        "decision": "JWT + refresh token",
        "pros": ["stateless access token"],
        "cons": ["refresh token revocation complexity"]
      }
    ]
  },

  "api_spec": [
    {
      "method": "POST",
      "path": "/auth/google/callback",
      "request": {},
      "response": {"access_token": "string"}
    }
  ],

  "db_schema": [
    {
      "table": "users",
      "columns": [
        {"name": "id", "type": "uuid", "constraints": "PRIMARY KEY"},
        {"name": "email", "type": "text", "constraints": "UNIQUE NOT NULL"}
      ],
      "indexes": ["idx_users_email"]
    }
  ],

  "implementation": {
    "artifacts": [
      {
        "filename": "src/auth/service.ts",
        "language": "typescript",
        "content": "..."
      }
    ]
  },

  "tests": [
    {
      "name": "oauth callback success",
      "type": "integration",
      "description": "Verifies Google OAuth callback returns valid tokens"
    }
  ],

  "risks": [
    {
      "risk": "refresh token theft",
      "severity": "high",
      "mitigation": "rotation + revocation list"
    }
  ],

  "missing_fields": [
    "string — any deliverable the candidate could not provide, with reason"
  ]
}
```

---

## Field Requirements by Task Type

| Field | architecture | code | sql | documentation | advice |
|-------|:-----------:|:----:|:---:|:------------:|:------:|
| summary | Required | Required | Required | Required | Required |
| assumptions | Required | Required | Required | Required | Required |
| architecture | Required | Optional | Optional | Optional | Optional |
| api_spec | If applicable | If applicable | — | — | — |
| db_schema | If applicable | If applicable | Required | — | — |
| implementation | — | Required | Required | — | — |
| tests | — | Required | Optional | — | — |
| risks | Required | Required | Required | Required | Required |
| missing_fields | Always | Always | Always | Always | Always |

---

## Candidate Roles

### Role A: Correctness-First (Conservative)

- Prioritizes well-tested, proven patterns
- Avoids cutting-edge or untested approaches
- Thorough error handling and edge cases
- May over-engineer for safety

### Role B: Security-First

- Starts from threat model
- Defensive coding throughout
- Explicit trust boundaries
- May sacrifice simplicity for security

### Role C: Cost-First (Pragmatic)

- Minimal infrastructure
- Uses managed services strategically
- Avoids over-engineering
- Clear cost projections
- May defer some hardening for later

### Role D: Speed-First (Lean)

- Fastest path to working solution
- Lean architecture with clear upgrade paths
- Favors convention over configuration
- May accept more technical debt

---

## Generation Strategies

### Strategy 1: Same Model, Different Roles

Use the same model (e.g., Claude) with different system prompts for each role. Good for MVP — cheapest and fastest.

### Strategy 2: Different Models, Same Role

Use multiple models (GPT-4o, Claude, Gemini) with identical prompts. Good for comparing model capabilities on the same task.

### Strategy 3: Mixed Models and Roles

Assign specific models to roles they excel at. Best diversity but highest cost.

### Strategy 4: Temperature Variation

Same model, same prompt, different temperatures (0.2 for precise, 0.8 for creative). Useful for exploring solution space.

---

## Schema Enforcement

If a candidate produces free-text instead of structured output, add an **extraction layer**:

1. Run the candidate's raw output through a schema extractor
2. The extractor maps content to the candidate schema
3. Any field the extractor cannot fill is marked in `missing_fields`
4. The extractor MUST NOT fabricate content — only map existing content

See prompt template → [prompt-templates.md](prompt-templates.md#extraction-prompt)
