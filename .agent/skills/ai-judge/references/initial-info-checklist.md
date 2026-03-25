# Initial Information Checklist

**This checklist is MANDATORY.** Before generating any candidates or starting the judge pipeline, collect all required fields from the user. If any required field is missing, ask the user explicitly.

---

## Required Fields

### 1. Problem Statement

| Field | Description | Example |
|-------|-------------|---------|
| **What to solve** | One clear sentence describing the problem | "Design and implement a login system with Google OAuth and RBAC" |
| **Why it matters** | Business context or motivation | "Current system has no auth; users share a single account" |

**If missing:** Ask — "Can you describe in one sentence what problem this should solve, and why it matters?"

### 2. Task Type

| Type | When to Use | Candidate Count |
|------|-------------|-----------------|
| `architecture` | System design, component layout, data flow, options comparison | 3 |
| `code` | Working implementation with tests | 3 |
| `architecture_and_code` | Both design and implementation (alias: `mixed`) | 3 |
| `sql` | Database schema, migrations, queries | 3 |
| `documentation` | Technical docs, runbooks, ADRs | 2 |
| `advice` | Recommendations, trade-off analysis | 2 |
| `security_compliance` | Security review, compliance check | 4 |

**Note on `mixed`:** Treat `mixed` as an alias for `architecture_and_code`. Applies both architecture and code validation checks.

**If missing:** Ask — "Is this primarily architecture, code, SQL, documentation, advice, or a security/compliance task?"

### 3. Constraints

Collect all applicable constraints:

| Category | Examples |
|----------|---------|
| **Language / runtime** | TypeScript, Python 3.12, Go 1.22 |
| **Framework** | FastAPI, Next.js, Spring Boot |
| **Database** | PostgreSQL 16, MongoDB, Redis |
| **Infrastructure** | AWS, GCP, Kubernetes, Docker |
| **Compliance** | SOC2, GDPR, HIPAA, PCI-DSS |
| **Performance** | p95 < 200ms, support 10K concurrent users |
| **Budget** | Use only open-source, avoid expensive managed services |
| **Existing codebase** | Must integrate with existing monorepo at `src/` |
| **Team conventions** | Naming standards, folder structure, review process |

**If missing:** Ask — "Are there any language, framework, database, infrastructure, compliance, or performance constraints I should know about?"

### 4. Deliverables

What artifacts should the final output include?

| Deliverable | Description |
|-------------|-------------|
| `architecture` | Component diagram, data flow, trade-off table |
| `api_spec` | Endpoint definitions with request/response schemas |
| `db_schema` | Table definitions, relationships, indexes |
| `code` | Working source files |
| `tests` | Unit tests, integration tests, test plan |
| `deployment_notes` | How to deploy, rollback, monitor |
| `migration_plan` | Database migration strategy |
| `security_review` | Threat model, risk list, mitigations |
| `cost_estimate` | Infrastructure cost projection |
| `adr` | Architecture Decision Record |

**If missing:** Ask — "What should the final output include? (e.g., code, tests, architecture diagram, API spec, deployment notes)"

### 5. Acceptance Criteria

Hard requirements that every candidate MUST meet. These become **hard gates** in validation.

| Example Criteria |
|-----------------|
| Must compile without errors |
| Must pass all unit tests |
| Must handle token rotation |
| Must include audit logging |
| Must not use deprecated APIs |
| Must support horizontal scaling |
| Response time under 200ms at p95 |

**If missing:** Ask — "What are the hard requirements that any solution MUST meet to be acceptable?"

### 6. Risk Level

Determines how many candidates and judges to use.

| Level | Criteria | Candidates | Judges | Refine? |
|-------|----------|------------|--------|---------|
| `low` | Advice, docs, low-impact changes | 2 | 1 | No |
| `medium` | Standard architecture or code tasks | 3 | 1 | Yes |
| `high` | Security-sensitive, compliance, production systems | 4 | 2 | Yes + human gate |

**If unclear:** Default to `medium`. Escalate to `high` if the task involves authentication, payments, PII, or compliance.

### 7. Domain Context (Optional but Recommended)

| Field | Description |
|-------|-------------|
| **Existing codebase** | Point to relevant files or directories |
| **Existing patterns** | "We use repository pattern", "All services are in `src/services/`" |
| **Team size** | Affects maintainability expectations |
| **Timeline** | Affects pragmatism vs. thoroughness trade-off |
| **Prior attempts** | What was tried before and why it failed |

---

## Quick Collection Template

Present this to the user when starting:

```
To set up the AI Judge pipeline, I need the following information:

1. **Problem**: What exactly needs to be solved? Why?
2. **Type**: Architecture / Code / SQL / Docs / Advice / Security?
3. **Constraints**: Language, framework, database, compliance, performance?
4. **Deliverables**: What artifacts do you need? (code, tests, API spec, etc.)
5. **Acceptance criteria**: What hard requirements must every solution meet?
6. **Risk level**: Low / Medium / High?
7. **Context** (optional): Existing codebase, patterns, prior attempts?
```

---

## Minimum Viable Input

At absolute minimum, the following must be known before proceeding:

- [ ] Problem statement (what + why)
- [ ] Task type
- [ ] At least one constraint
- [ ] At least one deliverable
- [ ] At least one acceptance criterion

If fewer than these five items are provided, **do not proceed** — ask the user.

---

## What Happens After Collection

Follow the order in `SKILL.md` **Phase 0 — Basic Information Confirmation**:

1. **Summarize** — output the **Basic Info Confirmation** table (see `SKILL.md`; same columns: problem, task type, constraints, deliverables, acceptance criteria, risk, context).
2. **User confirmation (gate)** — do **not** run normalization, rubric, candidates, or judge until the user confirms the summary is correct or explicitly approves stated assumptions. If anything is still missing, ask first.
3. **Normalize (Phase 1)** — convert into a structured `TaskSpec` JSON only after step 2.
4. **Plan** — generate the rubric and hard gates.
5. **Proceed** — begin candidate generation.

Optional: after step 3, show the `TaskSpec` JSON for a quick sanity check if the task is complex or ambiguous.

This prevents wasted computation and unfair comparison from a misunderstood task.
