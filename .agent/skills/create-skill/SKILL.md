---
name: create-skill
description: Use when you need to extend agent capabilities by creating a new skill. Handles scaffolding, TDD workflow, and CSO (Claude Search Optimization).
---

# Create Skill

Use this skill to create high-quality, reusable agent skills following the "Writing Skills" TDD methodology and Claude Search Optimization (CSO) standards.

## Skill Creation Workflow (TDD for Skills)

Follow this cycle to ensure the skill is robust and useful:

1.  **RED (Definition & Baseline)**
    - Gather requirements: name (kebab-case), scope (global/workspace), and specific problem/symptom.
    - **Draft the Frontmatter First**: Define the `description` carefully.
        - *Rule*: Description must state **WHEN** to use it (triggers), NOT **WHAT** it does (workflow).
        - *Example*: "Use when tests are flaky or failing intermittently" (Good) vs "Reviews code and fixes tests" (Bad).
    - **Identify a Test Case**: Determine a scenario where the agent currently fails or struggles. This is your "Failing Test".

2.  **GREEN (Scaffolding & Drafting)**
    - Determine Target Directory:
        - **Global**: `~/.gemini/antigravity/skills/<skill-name>/`
        - **Workspace**: `<workspace-root>/.agent/skills/<skill-name>/`
        - **Repo**: If in a skills repo, use root `skills/<skill-name>/`.
    - Create Directory: `mkdir -p <path>`
    - Create `SKILL.md` using the **Standard Template** (see below).

3.  **REFACTOR (Refine & Optimize)**
    - Review against the **CSO Checklist**.
    - Verify that the description keywords cover synonyms and error messages.
    - Ensure the "When to Use" section is comprehensive.

## SKILL.md Template

Use this exact structure for the new skill:

```markdown
---
name: <skill-name-kebab-case>
description: Use when [specific triggering conditions, symptoms, or context].
---

# <Skill Name Title>

## Overview
<Core principle in 1-2 sentences. What is this skill providing?>

## When to Use
- [Trigger A]
- [Trigger B]
- [Symptom C]

**When NOT to use:**
- [Counter-example]

## Core Pattern / Instructions
<Step-by-step guidance, mental models, or process>

## Quick Reference
| Operation | Command/Pattern |
|:---|:---|
| Action | `code` |

## Common Mistakes
- **Mistake**: ...
  - **Fix**: ...
```

## CSO (Claude Search Optimization) Rules

1.  **Name**: Active voice, verb-first if possible (e.g., `creating-skills`, `testing-react`).
2.  **Description**:
    - **MUST** start with "Use when...".
    - **MUST NOT** summarize the workflow (prevent agent shortcutting).
    - **MUST** include specific triggers and symptoms.
3.  **Keywords**: Include error messages, library names, and synonyms in the text.

## Final Checklist

Before finishing the task, verify the new skill:
- [ ] **Name**: Kebab-case, no special chars.
- [ ] **Frontmatter**: `description` is under 1024 chars and describes *triggers*.
- [ ] **Structure**: Has "When to Use" and "Quick Reference".
- [ ] **Completeness**: Instructions allow an agent to solve the "Failing Test" scenario.
- [ ] **Registration**: Remind the user the skill is active.
