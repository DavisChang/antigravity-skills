# AI Agent Observability & Evaluation — Full Checklist

Use this as a self-assessment and implementation tracker. Items are grouped by priority.

---

## P0: Safety & Guardrails

- [ ] I can list 3+ "absolutely forbidden" actions, each with an enforcement mechanism (approval gate / hard block / confirmation prompt)
- [ ] `max_steps` limit is enforced — agent cannot run indefinitely
- [ ] `max_tool_calls` limit is enforced — prevents cost explosion from looping
- [ ] Timeout strategy exists — agent is killed after N seconds
- [ ] High-risk tool calls require human approval or secondary confirmation
- [ ] Input routing exists: known patterns → rules/forms; unknown → LLM
- [ ] Rollback mechanism: can revert agent's external state changes

## P0: Trace Capture

- [ ] Every LLM call is recorded as a **Run** with:
  - [ ] Full input context (system prompt, messages, tool definitions, retrieval context)
  - [ ] Model parameters (model name, temperature, max_tokens)
  - [ ] Full output (model response, tool calls with args and return values)
  - [ ] Metadata: `run_id`, `step_id`, timestamp, token counts, latency, cost
- [ ] Every tool call has its own record: name, arguments, return value, error (if any), latency
- [ ] Runs are typed: planner / tool-selector / summarizer / critic / other
- [ ] Context length and truncation status recorded per Run
- [ ] `prompt_preview` (first 500 chars) captured for debugging
- [ ] `response_preview` (first 500 chars) captured for debugging
- [ ] `decision_context` recorded (key factors that influenced the LLM call)

## P0: Trace & Thread Linkage

- [ ] Each task execution has a unique `trace_id`
- [ ] Runs within a trace are ordered and linkable (parent → child)
- [ ] Trace can be replayed in time-order (UI or JSON timeline)
- [ ] Multi-turn conversations have a `thread_id` linking all traces
- [ ] Thread view shows: human message → AI message → backing trace for each turn
- [ ] All bug reports / incident tickets include `trace_id` or `thread_id`

## P1: Error & Anomaly Tracking

- [ ] Errors are structured: `{ step, error_code, message, severity, recoverable, details }`
- [ ] Unhandled exceptions are caught and written to trace (not silently dropped)
- [ ] Node/step failures don't silently break the pipeline — they appear in trace output
- [ ] Loop detection rule defined: same tool + same args >= 3 consecutive = loop
- [ ] Tool error rate tracked per-tool
- [ ] Alert thresholds set for key anomalies:
  - [ ] Loop rate > X%
  - [ ] Tool error rate > Y%
  - [ ] Timeout rate > Z%
  - [ ] Format violation rate spike

## P1: Evaluation — Run Level (Unit Tests)

- [ ] Critical run types identified (tool selection, query generation, summarization)
- [ ] At least 10 test cases per critical run type
- [ ] Each test case has clear pass/fail criteria (not subjective)
- [ ] Criteria focus on decisions (correct tool, correct format, required facts) not exact wording
- [ ] Test suite runs in CI on every prompt/tool change
- [ ] Target: >= 90% pass rate for tool selection
- [ ] Failure cases are categorized: hallucination / wrong tool / missing info / context loss / loop

## P1: Evaluation — Trace Level (End-to-End)

- [ ] At least 5 end-to-end test cases for core tasks
- [ ] Each case defines:
  - [ ] Input (user request)
  - [ ] Must-happen conditions (specific tools called, specific facts present)
  - [ ] Must-not-happen conditions (no loops, no tool errors, no timeouts)
  - [ ] Max steps and max cost bounds
- [ ] Tests are auto-judgeable (pass/fail without human review)
- [ ] Failure categorization: which step failed, why

## P2: Evaluation — Thread Level (Multi-Turn)

- [ ] At least 3 multi-turn test scenarios
- [ ] Each scenario defines 3+ memory points that must persist across turns
- [ ] Checks for self-contradiction across turns
- [ ] Checks for context retention (preferences, constraints, earlier corrections)
- [ ] Re-ask rate tracked (user repeating themselves = context loss signal)

## P2: Production → Offline Feedback Loop

- [ ] Process exists: user report → find trace → locate failing step → extract state
- [ ] State extraction produces replayable test case (messages + tools + context snapshot)
- [ ] PII masking / anonymization applied before storing test cases
- [ ] Fixed test cases are added to CI regression suite
- [ ] Verification: test fails before fix, passes after fix
- [ ] Weekly review rhythm: Top 3 failure modes → triage → fix → regress

## P2: Structured Logging

- [ ] Logs are structured (JSON / structlog), not plain `print()`
- [ ] Log entries include: `job_id`, `trace_id`, `node/step`, `level`, `event`
- [ ] Logs are queryable (by job_id, by node, by error level)
- [ ] Sensitive data is masked in logs

## P3: Metrics & Dashboards

- [ ] Efficiency metrics collected: latency, token usage, cost per trace
- [ ] User behavior signals: abandon rate, re-ask rate, satisfaction
- [ ] Dashboard: Trace replay view (debug)
- [ ] Dashboard: Thread health view (product)
- [ ] Baseline metrics established for comparison
- [ ] Trend tracking: cost per task, success rate, loop rate over time

## P3: Non-Determinism Management

- [ ] Core tasks benchmarked: same input run N>=20 times
- [ ] Success rate and variance documented
- [ ] Average steps and cost distribution known
- [ ] Failure modes categorized from benchmark runs
- [ ] Prompt/tool changes are regression-tested against benchmark

---

## Scoring Guide

| Score | Level | Description |
|-------|-------|-------------|
| 0-5 checked | **Dangerous** | Agent is a demo, not production-ready |
| 6-15 checked | **Basics** | Core safety and tracing in place |
| 16-25 checked | **Solid** | Evaluation loop forming, most gaps covered |
| 26-35 checked | **Production** | Observable, evaluable, iteratively improving |
| 36+ checked | **Mature** | Full feedback loop, non-determinism managed |
