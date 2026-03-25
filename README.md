# Antigravity Skills

A collection of custom skills for the Antigravity AI agent, designed to extend agent capabilities for specialized tasks.

## Overview

This repository contains reusable skills that enable the Antigravity agent to perform complex, domain-specific tasks. Each skill is a self-contained package with instructions, helper scripts, and resources.

## Available Skills

### 1. create-skill
**Location**: `.agent/skills/create-skill/`

A meta-skill for creating new Antigravity skills following best practices.

**Use when**: You need to extend agent capabilities by creating a new skill.

**Features**:
- TDD (Test-Driven Development) workflow for skill creation
- Claude Search Optimization (CSO) guidelines
- Comprehensive skill scaffolding template
- Quality checklist for skill validation

**Quick Start**:
```
Ask the agent: "Create a new skill for [your task]"
```

### 2. medium-tech-digest
**Location**: `.agent/skills/medium-tech-digest/`

Automated weekly digest of top tech articles from Medium.

**Use when**: You want a curated summary of recent AI and tech articles.

**Features**:
- Searches Medium for articles in 5 categories
- Reads full article content for accurate summarization
- Generates bilingual reports (Traditional Chinese + English)
- Optional email delivery via SMTP

**Quick Start**:
```
Ask the agent: "Run the Medium tech digest"
```

**Output**: `medium_digest_output/medium_digest_<YYYY-MM-DD>/digest.md`

### 3. analyze-repo-wiki
**Location**: `.agent/skills/analyze-repo-wiki/`

Generate structured wiki documentation for any Git repository.

**Use when**: You need to analyze a codebase, generate documentation, or onboard onto an unfamiliar repo.

**Features**:
- Automated tech stack detection and entry point identification
- Generates 6-10 specialized wiki pages (Architecture, API, Data Layer, etc.)
- Produces Mermaid diagrams for visualization
- Built-in citation system referencing source files

**Quick Start**:
```
Ask the agent: "Analyze this repo and generate a wiki"
```

### 4. ai-agent-observability
**Location**: `.agent/skills/ai-agent-observability/`

Operational guide for building observable, evaluable, and iteratively improvable AI agent systems.

**Use when**: You're developing AI agents, adding observability to LLM pipelines, designing agent evaluation, or debugging non-deterministic behavior.

**Features**:
- Three-primitive trace design (Run / Trace / Thread)
- Guardrail templates with `max_steps`, `max_tool_calls`, timeout enforcement
- Three-layer evaluation strategy (unit, end-to-end, multi-turn)
- Production → offline feedback loop for continuous improvement
- Online evaluators (loop detector, tool error rate, refusal rate)

**Quick Start**:
```
Ask the agent: "Help me add observability to my AI agent"
```

### 5. arch-design-review
**Location**: `.agent/skills/arch-design-review/`

Facilitates structured system architecture design discussions using Socratic dialogue across seven dimensions.

**Use when**: You want to review a system design, discuss architecture tradeoffs, prepare for a design review meeting, or evaluate a new system proposal.

**Features**:
- Seven-dimension framework: Requirements, Traffic, Data, Reliability, Security, Architecture, Cost
- Socratic facilitation — guides the team to surface blind spots rather than dictating answers
- Structured output template with assumptions, SLOs, risk register, ADRs, and rollout plan
- Techniques for fault injection, counterfactual thinking, and cost probing

**Quick Start**:
```
Ask the agent: "Let's do an architecture design review for [your system]"
```

### 6. security-audit
**Location**: `.agent/skills/security-audit/`

Comprehensive multi-platform security audits with actionable reports.

**Use when**: You need a code security review, vulnerability scan, or penetration test preparation.

**Features**:
- Multi-platform support: SPA, Backend API, Desktop (Electron), AI/LLM, Containers
- Threat modeling using STRIDE framework
- Systematic scanning for hardcoded secrets and dangerous APIs
- Self-updating intelligence from 9+ security advisory sources

**Quick Start**:
```
Ask the agent: "Perform a security audit on this project"
```

### 7. security-defense
**Location**: `.agent/skills/security-defense/`

Perform endpoint security testing, penetration testing, defense analysis, and EU CRA product compliance assessment.

**Use when**: You need penetration testing, endpoint security check, service security scan, attack surface analysis, or CRA compliance.

**Features**:
- Endpoint/Service Security Testing (API, web, IP/port, infrastructure)
- Multi-phase structured testing (recon, frontend, backend, auth, infra)
- EU CRA Product Compliance workflow (classification, conformity assessment)
- Top 10 common findings and Banking sector attack-defense matrix

**Quick Start**:
```
Ask the agent: "Perform an endpoint security test on this project"
```

### 8. skill-security-auditor
**Location**: `.agent/skills/skill-security-auditor/`

Statically review any AI agent skill for security risks before installation or execution.

**Use when**: You need to audit a third-party AI agent skill, MCP config, Cursor rule, or AGENTS.md for safety and security.

**Features**:
- Detects prompt injection, malicious payloads, and supply-chain risks
- Identifies secret/host data exfiltration and over-privileged configurations
- Supports multiple formats: Antigravity/Cursor/Codex/Gemini skills, MCP config, AGENTS.md
- Provides actionable findings, severity ratings, and a clear safety verdict

**Quick Start**:
```text
Ask the agent: "Audit this skill for security risks"
```

### 9. ai-judge
**Location**: `.agent/skills/ai-judge/`

Multi-AI Judge System that orchestrates multiple models to compare approaches, generate candidates, validate with programmatic gates, and judge with rubrics.

**Use when**: You need to compare system designs, architectures, or get a best-of-N evaluated answer for complex tasks.

**Features**:
- Orchestrates multiple AI candidates to solve the same problem
- Employs validation gates and AI judging with rubrics
- Merges best features from various candidates into a refined architecture
- Systematic phasing (basic info → taskspec → rubric → candidates → validation → judgment → refined)

**Quick Start**:
```text
Ask the agent: "AI judge these architectural approaches for a worker queue"
```

### 10. figma-readiness-audit
**Location**: `.agent/skills/figma-readiness-audit/`

Analyze Figma designs via MCP to assess code-generation readiness across platforms.

**Use when**: You provide a Figma URL and want to know design quality, readiness, or handoff completeness for web/mobile engineering.

**Features**:
- Designer-friendly report quantifying evidence of readiness
- Actionable Figma fix steps for the design team
- Per-platform Level A/B/C ratings for Web, Flutter, and Windows
- Evaluates design-engineering alignment and ambiguity

**Quick Start**:
```text
Ask the agent: "Audit this Figma URL for dev readiness"
```

### 11. scrum-retro
**Location**: `.agent/skills/scrum-retro/`

Facilitates Scrum retrospectives by organizing raw data into structured Improvement Logs.

**Use when**: You have raw retro notes, observations, or sticky notes and need to organize or summarize a sprint retrospective.

**Features**:
- Turns chaotic notes into actionable Improvement Log entries
- Identifies themes, owners, metrics, and actionable experiments
- Provides structured tracking for sprint improvements

**Quick Start**:
```text
Ask the agent: "Summarize these sprint retro notes into an improvement log"
```

## Repository Structure

```
antigravity-skills/
├── .agent/
│   └── skills/
│       ├── ai-agent-observability/
│       │   ├── SKILL.md
│       │   ├── checklist.md
│       │   ├── playbook.md
│       │   ├── README.md
│       │   └── README_TW.md
│       ├── analyze-repo-wiki/
│       │   ├── SKILL.md
│       │   ├── README.md
│       │   └── references/
│       ├── arch-design-review/
│       │   ├── SKILL.md
│       │   └── dimensions.md
│       ├── create-skill/
│       │   └── SKILL.md
│       ├── medium-tech-digest/
│       │   ├── SKILL.md
│       │   └── scripts/
│       ├── security-audit/
│       │   ├── SKILL.md
│       │   ├── scripts/
│       │   └── references/
│       ├── security-defense/
│       │   ├── SKILL.md
│       │   └── references/
│       ├── skill-security-auditor/
│       │   ├── SKILL.md
│       │   ├── README.md
│       │   └── README_TW.md
│       ├── ai-judge/
│       │   ├── SKILL.md
│       │   ├── README.md
│       │   └── examples/
│       ├── figma-readiness-audit/
│       │   ├── SKILL.md
│       │   └── README.md
│       └── scrum-retro/
│           ├── SKILL.md
│           └── references/
├── search_medium.py
└── medium_digest_output/
    └── ...
```

## How Skills Work

1. **Discovery**: The Antigravity agent scans `.agent/skills/` and loads available skills
2. **Activation**: When a task matches a skill's description, the agent reads the full `SKILL.md`
3. **Execution**: The agent follows the skill's instructions to complete the task

## Creating New Skills

Use the `create-skill` skill to generate new skills:

1. Ask the agent to create a skill for your specific use case
2. The agent will guide you through:
   - Naming the skill
   - Defining triggers (when to use it)
   - Writing instructions
   - Adding helper scripts (optional)

## Skill Anatomy

Each skill requires a `SKILL.md` file with:

```yaml
---
name: skill-name
description: Use when [specific triggering conditions]
---

# Skill Name

## Overview
[What this skill does]

## When to Use
- [Trigger A]
- [Trigger B]

## Workflow
[Step-by-step instructions]

## Quick Reference
[Tables, commands, or key information]
```

## Best Practices

1. **Clear Triggers**: Skill descriptions should focus on *when* to use them, not *what* they do
2. **Keyword Rich**: Include error messages, symptoms, and tool names for better discoverability
3. **Self-Contained**: Skills should include all necessary context and instructions
4. **Tested**: Verify skills work with real scenarios before committing

## Contributing

To add a new skill to this repository:

1. Create a new folder in `.agent/skills/`
2. Add a `SKILL.md` file following the template
3. (Optional) Add helper scripts in a `scripts/` subdirectory
4. Test the skill with the Antigravity agent
5. Commit and push to the repository

## Resources

- [Antigravity Documentation](https://github.com/obra/superpowers) (inspiration and reference)
- [Writing Skills Guide](https://github.com/obra/superpowers/tree/main/skills/writing-skills)

## License

MIT License - feel free to use and modify these skills for your own projects.
