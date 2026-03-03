# AI Agent Evaluation Playbook

Practical strategies for evaluating AI agents at each layer. Use as a reference when implementing evaluations.

---

## Evaluation Philosophy

Traditional software: test code paths → deterministic pass/fail.
Agent systems: test **reasoning quality** and **context handling** → probabilistic, distribution-based.

**Key principles:**
1. Evaluate *decisions*, not *exact outputs* — "did it pick the right tool?" not "did it produce this exact string?"
2. Define *must-happen* and *must-not-happen* conditions instead of golden answers
3. Measure *efficiency* alongside *correctness* — a correct answer that costs 10x is a regression
4. Use production traces as your test case generator — you don't know what to test until you see real failures

---

## Layer 1: Run-Level Evaluation (Decision Unit Tests)

### When to Use
- You want CI-speed feedback (seconds, not minutes)
- Failures cluster at specific decision points (tool selection, query generation)
- You're iterating on a specific prompt or tool definition

### How to Build

**Step 1: Identify critical run types**
```
List your agent's LLM calls and classify them:
- Planner: decomposes user request into subtasks
- Tool selector: decides which tool to call
- Query generator: creates search/retrieval queries
- Summarizer: produces final response
- Critic: validates other agent output
```

**Step 2: For each critical run, build 10+ test cases**
```python
tool_selection_tests = [
    {
        "input_messages": [{"role": "user", "content": "What's the weather in Tokyo?"}],
        "available_tools": ["get_weather", "search_web", "send_email"],
        "expected_tool": "get_weather",
        "tags": ["simple", "single_tool"],
    },
    {
        "input_messages": [{"role": "user", "content": "Compare weather in NYC and London"}],
        "available_tools": ["get_weather", "search_web", "send_email"],
        "expected_tool": "get_weather",
        "expected_calls": 2,  # should call twice
        "tags": ["multi_call", "comparison"],
    },
    {
        "input_messages": [{"role": "user", "content": "Tell me a fun fact"}],
        "available_tools": ["get_weather", "search_web", "send_email"],
        "expected_tool": None,  # should NOT use any tool
        "tags": ["no_tool", "edge_case"],
    },
]
```

**Step 3: Define pass/fail criteria**
- Tool name matches expected → pass
- Format matches schema → pass
- Required facts present → pass
- Avoid "exact string match" criteria — too brittle

**Step 4: Run as part of CI**
```bash
# Every time prompt or tool definition changes
python -m pytest tests/eval/test_tool_selection.py -v
# Target: >= 90% pass rate
```

### Common Pitfalls
- Over-specifying expected output → prompt tweak breaks everything
- Not including edge cases (no-tool, ambiguous, multi-tool)
- Using only LLM-as-judge without calibration → scores drift

---

## Layer 2: Trace-Level Evaluation (End-to-End Tasks)

### When to Use
- Run-level tests pass but end-to-end still fails
- Agent modifies external state (files, databases, APIs)
- You need to verify the entire task flow, not just individual steps

### How to Build

**Step 1: Define task with minimum acceptance criteria**
```python
trace_test = {
    "name": "book_flight_under_budget",
    "input": "Find me a flight from NYC to London, under $500, next week",
    "must_happen": [
        "search_flights tool called with origin=NYC, destination=London",
        "price filter applied with max=500",
        "at least 1 result returned to user",
    ],
    "must_not_happen": [
        "loop detected (same tool+args >= 3 times)",
        "tool error occurred",
        "trace exceeded 60 seconds",
        "agent hallucinated a booking confirmation",
    ],
    "max_steps": 8,
    "max_cost_usd": 0.05,
}
```

**Step 2: Implement trace evaluator**
```python
def evaluate_trace(trace, test_spec):
    results = {"must_happen": {}, "must_not_happen": {}, "limits": {}}
    
    # Check must-happen
    for condition in test_spec["must_happen"]:
        results["must_happen"][condition] = check_condition(trace, condition)
    
    # Check must-not-happen
    for condition in test_spec["must_not_happen"]:
        results["must_not_happen"][condition] = not check_condition(trace, condition)
    
    # Check limits
    results["limits"]["steps"] = len(trace.runs) <= test_spec["max_steps"]
    results["limits"]["cost"] = trace.total_cost <= test_spec["max_cost_usd"]
    
    passed = all(
        all(v.values()) for v in results.values()
    )
    return {"passed": passed, "details": results}
```

**Step 3: Start small**
- 5 traces for core tasks
- Expand by 2-3 per week based on production failures

### Common Pitfalls
- Criteria too subjective → unreliable pass/fail
- Not checking must-not-happen → misses loops and errors
- Only testing happy path → no edge case coverage

---

## Layer 3: Thread-Level Evaluation (Multi-Turn Consistency)

### When to Use
- Product is chat / multi-turn interaction
- Users report "it forgot what I said"
- Human-in-the-loop approval flows

### How to Build

**Step 1: Define memory points that must persist**
```python
thread_test = {
    "name": "dietary_preference_retention",
    "turns": [
        {
            "user": "I'm allergic to peanuts and I'm vegetarian",
            "check": "agent acknowledges both constraints",
        },
        {
            "user": "Suggest me a restaurant",
            "check": "suggestions are vegetarian AND peanut-free",
        },
        {
            "user": "Actually, let's do Thai food",
            "check": "still applies vegetarian + peanut-free filter to Thai restaurants",
        },
        {
            "user": "What were my dietary restrictions again?",
            "check": "correctly states: vegetarian, peanut allergy",
        },
    ],
    "memory_points": ["vegetarian", "peanut allergy"],
    "must_not": ["suggest non-vegetarian", "suggest peanut-containing dish"],
}
```

**Step 2: Evaluate with LLM-as-judge (calibrated)**
```python
def evaluate_thread_turn(agent_response, check_criteria, memory_points):
    judge_prompt = f"""
    Agent response: {agent_response}
    Check: {check_criteria}
    Memory points that must be respected: {memory_points}
    
    Does the response satisfy the check? Answer: PASS or FAIL with brief reason.
    """
    judgment = llm_judge(judge_prompt)
    return judgment
```

### Common Pitfalls
- Fixed test messages break when agent response format changes
- Thread tests are slow and expensive — keep the set small (3-5)
- LLM-as-judge needs calibration against human labels

---

## Online Evaluation (Production, No Ground Truth)

### Minimum Viable Online Evaluators

**1. Loop Detector**
```python
def detect_loop(trace):
    """Same tool + same args >= 3 consecutive times"""
    calls = trace.tool_calls
    for i in range(len(calls) - 2):
        if (calls[i].name == calls[i+1].name == calls[i+2].name
            and calls[i].args == calls[i+1].args == calls[i+2].args):
            return True
    return False
```

**2. Tool Error Rate**
```python
def tool_error_rate(traces, window="1h"):
    total_calls = sum(len(t.tool_calls) for t in traces)
    error_calls = sum(1 for t in traces for c in t.tool_calls if c.error)
    return error_calls / max(total_calls, 1)
# Alert if > 5%
```

**3. Timeout Rate**
```python
def timeout_rate(traces, max_seconds=120):
    timed_out = sum(1 for t in traces if t.duration_seconds > max_seconds)
    return timed_out / max(len(traces), 1)
# Alert if > 2%
```

**4. Quality Signals (no ground truth needed)**
- Does agent cite sources when making claims?
- Does agent acknowledge uncertainty when unsure?
- Does agent ask clarification for ambiguous requests?
- Format compliance rate (JSON valid, required fields present)

### Alert Thresholds (starting points, tune weekly)

| Metric | Warning | Critical |
|--------|---------|----------|
| Loop rate | > 1% | > 5% |
| Tool error rate | > 3% | > 10% |
| Timeout rate | > 2% | > 5% |
| Format violation rate | > 5% | > 15% |
| Re-ask rate (thread) | > 20% | > 40% |

---

## Production → Offline Pipeline

### Conversion Process

```
1. Trigger: User report OR alert threshold exceeded
2. Find: trace_id from report / alert
3. Locate: Failing step in trace replay
4. Extract: State snapshot at that step
   - messages (conversation so far)
   - tools available
   - retrieval context
   - external state (file contents, DB state) if applicable
5. Anonymize: Mask PII, replace real names/emails/IDs
6. Package: Create test case
   {
     "input": extracted_state,
     "expected": "correct behavior description",
     "must_not": "the failure that happened",
     "source_trace_id": "abc123",
     "date_added": "2026-02-05"
   }
7. Verify: Fails before fix, passes after fix
8. Add to CI regression suite
```

### Weekly Review Template

```markdown
## Week of YYYY-MM-DD — Failure Mode Review

### Top 3 Failure Modes
1. **[Category]**: [Description] — [Count] occurrences
   - Root cause: [analysis]
   - Fix: [prompt change / tool change / guardrail]
   - Test case added: [yes/no, link]

2. ...

3. ...

### Metrics vs Last Week
| Metric | Last Week | This Week | Trend |
|--------|-----------|-----------|-------|
| Success rate | X% | Y% | ↑↓ |
| Avg steps | N | M | ↑↓ |
| Avg cost | $X | $Y | ↑↓ |
| Loop rate | X% | Y% | ↑↓ |
| Tool error rate | X% | Y% | ↑↓ |

### Regression Suite Status
- Total cases: N
- Pass rate: X%
- New cases added this week: M
```

---

## Experiment Backlog (Prioritized)

Use this as a starting point when planning iteration work:

| # | Experiment | Impact | Effort | Success Criteria |
|---|-----------|--------|--------|-----------------|
| 1 | Add approval gate + max_steps/tool guardrails for high-risk actions | High | Medium | Cost down, zero new high-risk misactions |
| 2 | Loop detector (same tool+args >= 3x) + online alert | High | Low | Catches >= 1 known loop, false positive < 20% |
| 3 | Benchmark core task: run 20x, measure success rate + step distribution | High | Low | Identify top 2 failure types, reproducible |
| 4 | Tool selection unit test suite (30 cases) | High | Medium | >= 90% correct, failures categorized |
| 5 | Convert 1 production bug trace → offline test case in CI | High | Medium | Fail before fix, pass after, CI-runnable |
| 6 | Minimal thread replay: show trace_id per turn in thread view | Medium | Medium | Can locate "first divergence point" |
| 7 | Weekly online evaluator report (tool error rate + timeout rate) | Medium | Low | Find >= 2 improvable failure modes in 1 week |
| 8 | Define 3 end-to-end acceptance conditions, build 5 trace evals | Medium | Medium | Each test auto-judges pass/fail, stable reruns |
