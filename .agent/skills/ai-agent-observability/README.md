# AI Agent Observability & Evaluation Skill

> A Cursor Agent Skill for building **observable, evaluable, and iteratively improvable** AI Agent systems.

[中文版 README_TW.md](README_TW.md)

---

## Why This Skill Exists

AI Agents are fundamentally different from traditional software:

| Traditional Software | AI Agents |
|---------------------|-----------|
| Deterministic: same input → same output | **Non-deterministic**: same input → different outputs each time |
| Constrained inputs (forms, APIs) | **Unconstrained inputs** (natural language, anything goes) |
| Debug with stack traces | **Debug with execution traces** (code doesn't predict behavior) |
| Test code paths | **Test reasoning quality & context handling** |
| Bugs found in code review | **Bugs found in production** (by user inputs you didn't anticipate) |

The two most critical capabilities for production agents: **Observability** and **Evaluation** — and they feed each other.

---

## What This Skill Covers

### 1. Core Mental Model
- Agents produce **behavior distributions**, not deterministic outputs
- **Traces are the source of truth** — not code, not logs, but the actual sequence of LLM calls, tool invocations, and decisions
- You manage distributions: measure success rates, failure modes, cost variance

### 2. The Three Observation Primitives

| Primitive | Scope | What It Answers |
|-----------|-------|-----------------|
| **Run** | Single LLM call | "Did this specific decision make sense?" |
| **Trace** | One task (multiple Runs) | "Did the agent complete this task correctly and efficiently?" |
| **Thread** | Multi-turn conversation (multiple Traces) | "Does the agent maintain consistency across turns?" |

### 3. What to Record

For every LLM call (Run):
- Input context: system prompt, messages, tool definitions, retrieval context
- Output: model response, tool calls (name, args, return value, error)
- Metadata: tokens, latency, cost, decision context
- Debug aids: `prompt_preview` (first 500 chars), `response_preview` (first 500 chars)

### 4. Three-Layer Evaluation Strategy

| Layer | Speed | Realism | Use Case |
|-------|-------|---------|----------|
| **Run-level** (unit tests) | Fast (CI) | Low | Protect critical decision points (tool selection, query generation) |
| **Trace-level** (end-to-end) | Medium | Medium | Verify complete task execution with must-happen/must-not-happen conditions |
| **Thread-level** (multi-turn) | Slow | High | Test memory retention, consistency across conversation turns |

### 5. Online Evaluation Without Ground Truth

In production, you rarely have "correct answers." Instead, monitor:
- **Efficiency signals**: latency, token usage, tool call count, cost
- **Failure signals**: loop detection, tool error rate, timeout rate, format violations
- **User behavior signals**: re-ask rate, abandon rate, escalation rate

Compare against baselines. Alert on deviation.

### 6. The Feedback Loop

```
Production failure → Find trace → Locate failing step → Extract state
  → Anonymize → Create offline test case → Fix → Verify → Add to CI
  → Repeat weekly
```

This is how you go from "it works in demo" to "it works in production."

---

## Skill File Structure

```
ai-agent-observability/
├── SKILL.md          # Main agent instructions (read by Cursor)
├── checklist.md      # Full self-assessment checklist (40+ items)
├── playbook.md       # Detailed evaluation strategies & code examples
├── README.md         # This file (English overview)
└── README_TW.md      # 中文版說明
```

### How Cursor Uses This Skill

When you're working on AI agent code and ask Cursor to:
- Add observability / tracing
- Design evaluation strategies
- Debug non-deterministic behavior
- Prepare an agent for production
- Add guardrails or safety mechanisms

Cursor will automatically read `SKILL.md` and follow the patterns, checklists, and strategies defined within.

---

## Quick Start: 5 Things to Do First

1. **Define 3 forbidden actions** and add enforcement (approval gates, hard blocks)
2. **Set guardrails**: `max_steps=15`, `max_tool_calls=30`, `timeout=120s`
3. **Record every LLM call** with full context (prompt, messages, tools, response, tokens, latency)
4. **Add 2 online evaluators**: loop detection + tool error rate
5. **Benchmark one core task**: run it 20 times, measure success rate and cost distribution

---

## Top 10 Principles

1. The two most critical things for production agents: observability and evaluation — they're coupled.
2. Agent systems aren't "read the code and know what happens" — the truth is in the trace.
3. You won't truly know what your agent will do until users interact with it in production.
4. Agent inputs are natural language (unconstrained) + non-deterministic = amplified risk.
5. Debugging means diving into the context of each LLM call, not finding a stack trace.
6. Run, Trace, Thread — three levels for understanding and governing agent behavior.
7. Evaluating agents means testing reasoning and context, not testing code branches.
8. End-to-end tests are more realistic but harder to define metrics; unit tests are fast but expire quickly.
9. Production traces become your evaluation dataset source.
10. No ground truth in production? You can still evaluate: use trace structure and efficiency metrics to catch anomalies.

---

## References

- Based on: "Observability and Evals for AI Agents" framework
- Applicable to: LangGraph, LangChain, CrewAI, AutoGen, custom agent frameworks
- Works with: Langfuse, LangSmith, Phoenix, or custom trace implementations
