# Case Study: PPTX Worker Queue on AWS EKS

Complete execution record of the ai-judge pipeline (Phase 0–7).
This folder is an end-to-end example showing what one full ai-judge run looks like.

## Files

| File | Contents |
|------|----------|
| `phase0-basic-info.md` | Phase 0: Basic Info Confirmation (includes user Q&A) |
| `phase1-taskspec.json` | Phase 1: Normalized Task Specification (TaskSpec) |
| `phase2-rubric.json` | Phase 2: Scoring Rules (Rubric) |
| `phase3-candidates.md` | Phase 3: Three Candidate Solutions |
| `phase4-validation.md` | Phase 4: Validation Gate (Requirement Coverage Check) |
| `phase5-judgment.md` | Phase 5: Judge's Conclusion, merge plan, must-fix items |
| `phase6-refined-architecture.md` | Phase 6–7: Refined Final Architecture |
| `diagrams.md` | Technical Flowcharts (Mermaid) |
| `dynamodb-design.md` | DynamoDB Table Design Recommendations |

## Quick Summary

- **Task:** Process PPTX format conversion using scheduled + background workers on AWS EKS; capable of retrying upon failure and keeping a complete history.
- **Winner:** Candidate A (Enhanced EventBridge + SQS + DynamoDB + EKS/KEDA)
- **Decision:** `revise_then_accept` (Base on A, absorbing B's auditing semantics and C's versioned retry semantics)
