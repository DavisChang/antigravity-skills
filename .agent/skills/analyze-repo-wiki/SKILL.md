---
name: analyze-repo-wiki
description: Analyze any Git repository and generate structured wiki documentation that helps AI agents quickly understand the codebase. Produces a .wiki/ folder with architecture overview, component docs, data flow, and Mermaid diagrams. Use when the user asks to analyze a codebase, generate documentation, create a wiki, understand a repository's architecture, document a project for AI consumption, or onboard onto an unfamiliar repo. Triggers on "analyze repo", "generate wiki", "document codebase", "repo analysis", "create documentation", "explain this project", "help AI understand this repo".
---

# Analyze Repo & Generate Wiki

Generate structured wiki documentation for any Git repository so that AI agents (and humans) can rapidly understand the codebase. Follows the **scan → classify → structure → generate → output** methodology.

All output is written to `.wiki/` at the project root.

## Workflow

### Phase 1: Scan & Classify

Use Cursor tools to build a project map:

1. **File tree**: Use `Glob` with `**/*` to enumerate all files. Filter out noise:
   - **Exclude dirs**: `.git`, `node_modules`, `.venv`, `venv`, `env`, `__pycache__`, `dist`, `build`, `out`, `bin`, `target`, `coverage`, `.next`, `.output`, `bower_components`
   - **Exclude files**: lock files (`*.lock`, `package-lock.json`), binaries (`*.exe`, `*.dll`, `*.so`, `*.pyc`), minified (`*.min.js`, `*.min.css`), maps (`*.map`), archives (`*.zip`, `*.tar`, `*.gz`)
2. **README**: Use `Read` to get README.md (or README.rst, README.txt)
3. **Tech stack detection**: Use `Glob` to check for marker files:
   - `package.json` → Node.js/JS/TS; read to get framework (next, react, vue, express, etc.)
   - `pyproject.toml` / `requirements.txt` / `setup.py` → Python; read to get framework (fastapi, django, flask, etc.)
   - `go.mod` → Go
   - `Cargo.toml` → Rust
   - `pom.xml` / `build.gradle` → Java
   - `Dockerfile` / `docker-compose.yml` → Containerized
   - `.env.example` / `.env.sample` → Environment-configured
4. **Entry points**: Identify main entry files by searching for patterns:
   - Use `Grep` for `if __name__`, `app.listen`, `createApp`, `main()`, `func main`
   - Check common paths: `src/index.*`, `src/main.*`, `app.*`, `api/main.*`, `cmd/`
5. **Key directories**: Identify purpose of top-level directories by reading 1-2 files in each

### Phase 2: Determine Wiki Structure

Based on Phase 1 findings, plan 6-10 wiki pages. Select from these categories (skip if not applicable):

| Category | When to include | What to cover |
|----------|----------------|---------------|
| **Project Overview** | Always | Purpose, tech stack, architecture summary, getting started |
| **System Architecture** | Projects with 3+ modules | Component diagram, communication patterns, data flow |
| **API Reference** | Has REST/GraphQL/gRPC endpoints | Endpoints, request/response schemas, auth |
| **Data Layer** | Has database/ORM/state management | Schema, models, migrations, data flow |
| **Frontend Architecture** | Has UI code | Components, routing, state management, styling |
| **Backend Architecture** | Has server code | Request lifecycle, middleware, services, error handling |
| **AI/ML Pipeline** | Has ML/AI components | Models, training, inference, prompts, RAG |
| **Configuration & Environment** | Has config files/env vars | All config options, env vars, feature flags |
| **Deployment & Infrastructure** | Has Docker/CI/CD/IaC | Build, deploy, environments, monitoring |
| **Testing Strategy** | Has test files | Test structure, how to run, coverage |
| **Extension & Plugin System** | Has plugin/hook architecture | How to extend, APIs, examples |

For each page, list 5-10 `relevant_files` — the actual file paths the agent must read to write that page.

### Phase 3: Generate Pages

For each wiki page, use `Read` and `Grep` to examine relevant files, then write a markdown file following this structure:

```markdown
# {Page Title}

> Based on: `file1.py`, `file2.ts`, `file3.go`, ...

## Overview
1-2 paragraphs: purpose, scope, how it fits in the project.

## {Logical Section}
Detailed explanation with:
- Mermaid diagrams (architecture, sequence, class, ER)
- Tables (APIs, config options, data models)
- Code excerpts (short, key snippets with file:line citations)

## Key Files
| File | Purpose |
|------|---------|
| `src/api/main.py` | FastAPI entry point |
| ... | ... |
```

#### Mermaid Diagram Rules
- Use `graph TD` (top-down), not `graph LR`
- Max 3-4 words per node label
- Sequence diagrams: declare all `participant` first, use `->>` for calls, `-->>` for returns
- Use `loop`, `alt/else`, `opt`, `par/and` for control flow

#### Citation Format
After significant claims, cite: `(source: filename.ext:L10-L25)`

### Phase 4: Generate Output

Write all files to `.wiki/` directory:

```
.wiki/
├── README.md              # Wiki index with table of contents
├── 01-project-overview.md
├── 02-system-architecture.md
├── 03-api-reference.md
├── 04-data-layer.md
├── ...
└── assets/                # (optional) diagrams, images
```

The `.wiki/README.md` must contain:
1. **Project name and one-line description**
2. **Tech stack summary** (languages, frameworks, databases, infra)
3. **Architecture diagram** (Mermaid `graph TD`)
4. **Table of contents** linking all wiki pages
5. **Quick reference**: entry points, how to run, key env vars

## Important Guidelines

- **Read before writing**: Always use `Read` on relevant files before generating content. Never fabricate.
- **Cite sources**: Every claim should reference the actual file and approximate line range.
- **Prioritize accuracy**: If information is unclear from the source, say so. Don't guess.
- **Use parallel exploration**: Launch `Task` subagents with `subagent_type="explore"` to analyze different areas of the codebase concurrently.
- **Handle large repos**: For repos with 100+ files, use `Grep` and `SemanticSearch` to find relevant code instead of reading everything.
- **Adapt to project type**: Not every project has frontend/backend/AI. Only generate pages that are relevant.

## Reference Files

- [references/page-templates.md](references/page-templates.md) — Detailed templates for each wiki page type
- [references/wiki-structure-schema.md](references/wiki-structure-schema.md) — XML schema for programmatic wiki structure definition
- [references/file-filters.md](references/file-filters.md) — Complete file inclusion/exclusion rules
