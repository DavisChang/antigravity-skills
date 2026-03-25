# Phase 0 — Basic Info Confirmation

## Collected from User

| Item | Content |
|------|---------|
| Problem (what + why) | Provide a background worker service for **PPTX to other formats conversion** on AWS EKS; conversions may fail, so it needs to keep a history and be able to rerun after modifying the code, providing a complete deployment solution. |
| Task type | `architecture` (including deployment and operations) |
| Constraints | AWS EKS, schedule-driven, PPTX conversion (long-running, prone to failure), auditable status, re-executable (including rerun after code modification), complete deployment required |
| Deliverables | Architecture, queue and schedule design, state/history model, retry semantics, deployment key points, risks, technical flowcharts |
| Acceptance criteria | (1) Task status is persisted and queryable; (2) Failures can be retried, with DLQ; (3) Both scheduled and manual triggers are supported; (4) Supports "rerunning the same task or new version after code modification"; (5) Can be deployed on EKS |
| Risk level | `medium` |
| Domain context | N/A (no existing repo or existing service) |

- Open questions: none
- **Status: ✅ confirmed — proceed to Phase 1**

## Q&A Record

**User's Original Request (First Round):**
> Use the AI Judge system to compare three worker queue solutions.

**Agent Asked for Additional Information, User Replied:**
> Execution environment aws k8s, nature of work: scheduled. Likely to be helping users convert pptx to other formats, errors might occur in the middle, requires modifying the code and rerunning, so a history needs to be kept, capable of being re-executed. Complete deployment required.

↳ The above reply covers all minimum required fields → Phase 0 confirmation completed.
