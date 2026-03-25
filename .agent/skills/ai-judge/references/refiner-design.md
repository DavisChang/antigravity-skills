# Refiner Design

The refiner takes the winner candidate and applies targeted fixes. It does NOT regenerate from scratch or add creative embellishments.

---

## Refiner Rules

1. Use the **winner candidate** as the sole base
2. Apply **every item** in the `must_fix` list
3. Borrow **only** from candidates specified in the `merge_plan`
4. Do NOT change anything that already passes tests
5. Do NOT add features or requirements not in the task spec
6. Output must still conform to the candidate schema
7. The refined output goes through **re-validation** before finalization

---

## Refiner Input

```json
{
  "winner": { "...candidate schema..." },
  "must_fix": [
    "Add database migration plan",
    "Add audit event schema"
  ],
  "merge_plan": [
    {
      "borrow_from": "cand_C",
      "items": ["cost estimate", "deployment topology"]
    }
  ],
  "task_spec": { "..." },
  "rubric": { "..." },
  "other_candidates": {
    "cand_C": { "...candidate schema..." }
  }
}
```

## Refiner Output

The same candidate schema, with fixes applied:

```json
{
  "candidate_id": "cand_A_refined",
  "role": "refined",
  "summary": "...",
  "...all candidate fields...",
  "refinement_log": [
    {
      "fix": "Add database migration plan",
      "action": "Added migration section with up/down scripts",
      "source": "original"
    },
    {
      "fix": "Add cost estimate",
      "action": "Borrowed cost estimate from cand_C",
      "source": "cand_C"
    }
  ]
}
```

---

## Re-Validation

After refinement, the output goes through the full validation pipeline again:

1. All hard gates must still pass
2. Previously passing tests must still pass
3. New content from `must_fix` is validated
4. If re-validation fails, fall back to the original winner and flag the issue

---

## Refinement Failure Handling

| Scenario | Action |
|----------|--------|
| Refined output fails a gate | Fall back to original winner, mark must-fix items as unresolved |
| Refined output breaks existing tests | Revert to original winner, log the regression |
| Must-fix item cannot be addressed | Mark as `unresolved` in the final report |
| Merge-plan item conflicts with winner | Keep the winner's version, log the conflict |

---

## Refiner Prompt

See full prompt template → [prompt-templates.md](prompt-templates.md#refiner-prompt)

Key instructions:
- The winner is the only base — do not restructure or rewrite
- Must-fix items are mandatory, not suggestions
- Borrowed items must not conflict with the winner's approach
- Preserve all external behavior that already works
- Output must conform to the candidate schema
