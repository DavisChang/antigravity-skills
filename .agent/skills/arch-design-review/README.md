# Architecture Design Review — Agent Skill

A Cursor Agent Skill that facilitates structured system architecture design discussions. Instead of producing a one-shot design document, it guides you through **seven critical dimensions** via Socratic dialogue, surfacing blind spots and recording tradeoffs.

## Why This Skill?

Architecture reviews often miss critical aspects because:

- Teams focus on the "happy path" and skip failure modes
- Traffic/capacity estimates get hand-waved as "we'll scale later"
- Security and compliance are bolted on after launch
- Cost and team capability are rarely discussed until it's too late
- Decisions are made verbally and never recorded

This skill ensures every dimension gets at least a surface-level check, and critical ones get deep dives.

## The Seven Dimensions

| # | Dimension | What It Covers |
|---|-----------|---------------|
| ① | **Requirements & Success Definition** | Business goals, scope/non-goals, user journeys, feature inventory |
| ② | **Traffic, Performance & Capacity** | Traffic models, latency budgets, read/write patterns, growth curves |
| ③ | **Data & Consistency** | Consistency requirements, transactions, idempotency, data lifecycle, data quality |
| ④ | **Reliability & Resilience** | SLOs, failure modes (FMEA), dependency governance, backpressure, disaster recovery |
| ⑤ | **Security, Privacy & Compliance** | Threat models, abuse prevention, secrets management, privacy, audit |
| ⑥ | **Architecture Shape & Operability** | Service boundaries, sync/async, observability, deployment, testing, migrations |
| ⑦ | **Cost & Organizational Reality** | Cost models, vendor lock-in, team capability, ADRs, decommissioning |

## How It Works

1. **You describe what you're designing** — a new system, a major refactor, or a design for review
2. **The agent walks through each dimension** — asking probing questions, surfacing risks, and recording decisions
3. **You get a structured output** — goals & SLOs, traffic assumptions, architecture sketch, top 10 risks, tradeoff records (ADRs), and a phased rollout plan

### Discussion Approach

The agent acts as a **thinking partner**, not a lecturer:

- Uses **counterfactual questions** to test assumptions ("What breaks at 100x traffic?")
- **Digs deeper** when answers are vague (a sign of blind spots)
- **Moves on** when answers are solid and well-reasoned
- **Marks items as N/A** when a dimension doesn't apply

## Output Format

After discussion, the agent produces a structured summary:

```
(1) Goals & SLOs          — 3 success metrics with targets
(2) Traffic Assumptions   — average / peak / burst / 6-month projection
(3) Architecture Sketch   — control plane / data plane / event plane
(4) Top 10 Risks          — with dimension, severity, and mitigation
(5) Tradeoffs / ADRs      — 3+ key decisions with reasoning and revisit conditions
(6) Rollout Plan          — MVP → V1 → V2 with risk coverage per phase
```

## File Structure

```
arch-design-review/
├── SKILL.md          # Agent instructions (discussion flow, output template, guardrails)
├── dimensions.md     # Full reference — questions, decisions, deliverables per dimension
├── README.md         # This file (English)
└── README_TW.md      # Traditional Chinese version
```

## Usage

Trigger the skill by mentioning keywords like:
- "system design", "architecture design", "design review", "arch review"

Or directly ask the agent to review a system architecture.

### Example Prompts

```
"I'm designing a real-time notification system — let's do an architecture review."

"We're refactoring our payment service. Can you walk me through what we should consider?"

"Review this architecture: [paste your design doc or describe the system]"
```

## Customization

- **Add domain-specific checklists**: Extend `dimensions.md` with items specific to your industry (fintech, healthcare, gaming, etc.)
- **Adjust depth**: The agent adapts — quick reviews touch each dimension once, deep reviews explore every sub-item
- **Change output format**: Modify the output template in `SKILL.md` to match your team's design doc standard

## License

MIT
