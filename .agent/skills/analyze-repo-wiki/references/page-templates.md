# Wiki Page Templates

Detailed templates for each wiki page type. Read the section matching the page you're generating.

## Table of Contents
- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [API Reference](#api-reference)
- [Data Layer](#data-layer)
- [Frontend Architecture](#frontend-architecture)
- [Backend Architecture](#backend-architecture)
- [AI/ML Pipeline](#aiml-pipeline)
- [Configuration & Environment](#configuration--environment)
- [Deployment & Infrastructure](#deployment--infrastructure)
- [Testing Strategy](#testing-strategy)

---

## Project Overview

**Always generate this page first.** It's the entry point for anyone (human or AI) understanding the project.

### What to investigate
- README.md
- package.json / pyproject.toml / go.mod / Cargo.toml (for project name, description, deps)
- Dockerfile / docker-compose.yml (for runtime overview)
- .env.example (for key configuration)
- Top-level directory structure

### Template

```markdown
# {Project Name}

> Based on: `README.md`, `package.json`, ...

## What is {Project Name}?
1-2 paragraphs: what the project does, who it's for, key value proposition.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 / TypeScript 5.x / ... |
| Framework | FastAPI / Next.js / ... |
| Database | PostgreSQL / MongoDB / ... |
| Infrastructure | Docker / Kubernetes / ... |
| AI/ML | OpenAI / PyTorch / ... |

## Architecture Overview

{Mermaid graph TD showing major components and their relationships}

## Project Structure

{Top-level directory listing with purpose of each}

## Getting Started

{How to install, configure, and run — derived from README or Makefile/scripts}

## Key Entry Points

| Entry | File | Purpose |
|-------|------|---------|
| API Server | `api/main.py` | Starts FastAPI on port 8001 |
| Frontend | `src/app/page.tsx` | Next.js home page |
| ... | ... | ... |
```

---

## System Architecture

### What to investigate
- Entry point files (how the app boots)
- Module/package boundaries (top-level dirs, __init__.py, index.ts)
- Import graphs (use Grep to trace imports between modules)
- Communication patterns (HTTP calls, WebSocket, message queues, function calls)
- Middleware chains

### Template

```markdown
# System Architecture

> Based on: {list 5-10 key architectural files}

## High-Level Architecture

{Mermaid graph TD: boxes for each major subsystem, arrows for communication}

## Component Breakdown

### {Component A}
Purpose, responsibilities, key files.

### {Component B}
Purpose, responsibilities, key files.

## Communication Patterns

{Mermaid sequenceDiagram: typical request flow through the system}

## Key Design Decisions
Bullet list of notable architectural choices found in the code.
```

---

## API Reference

### What to investigate
- Route definitions: search for `@app.get`, `@app.post`, `router.`, `app.use`, `HandleFunc`
- Request/response models: Pydantic models, TypeScript interfaces, Go structs
- Middleware: auth, CORS, rate limiting, logging
- WebSocket handlers if present

### Template

```markdown
# API Reference

> Based on: {route files, model files, middleware files}

## Endpoints Overview

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | /api/users | List users | Yes |
| POST | /api/users | Create user | Yes |
| ... | ... | ... | ... |

## {Endpoint Group}

### {METHOD} {path}
- **Purpose**: ...
- **Request body**: {table of fields, types, required}
- **Response**: {table or example JSON}
- **Error codes**: {table}

## Authentication & Authorization
How auth works, what middleware enforces it.

## WebSocket Endpoints (if applicable)
Connection flow, message format, events.
```

---

## Data Layer

### What to investigate
- ORM models / database schemas (models.py, schema.prisma, migrations/)
- Database config (connection strings, pool settings)
- Data access patterns (repositories, DAOs, query builders)
- State management (Redux, Zustand, Context, Vuex)

### Template

```markdown
# Data Layer

> Based on: {model files, migration files, repository files}

## Data Model

{Mermaid erDiagram showing entities and relationships}

## Key Entities

### {Entity Name}
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | ... |
| ... | ... | ... | ... |

## Data Access Patterns
How code reads/writes data (repository pattern, active record, raw queries).

## State Management (frontend, if applicable)
Stores, contexts, data flow between components.
```

---

## Frontend Architecture

### What to investigate
- Page/route structure (app/, pages/, routes/)
- Component hierarchy (components/, shared/)
- State management (stores, contexts, hooks)
- Styling approach (Tailwind, CSS modules, styled-components)
- Build config (next.config, vite.config, webpack.config)

### Template

```markdown
# Frontend Architecture

> Based on: {layout files, key page files, component files}

## Routing Structure

| Route | Page File | Purpose |
|-------|-----------|---------|
| `/` | `src/app/page.tsx` | Home |
| `/dashboard` | `src/app/dashboard/page.tsx` | Dashboard |

## Component Architecture

{Mermaid graph TD: component hierarchy}

## State Management
How data flows: contexts, stores, props, server state.

## Key Components
For each major component: purpose, props, key behavior.

## Styling Approach
Framework used, theming, responsive strategy.
```

---

## Backend Architecture

### What to investigate
- Server setup and middleware chain
- Service/business logic layer
- Error handling patterns
- Background jobs / async processing
- Logging and observability

### Template

```markdown
# Backend Architecture

> Based on: {server files, service files, middleware files}

## Request Lifecycle

{Mermaid sequenceDiagram: request → middleware → handler → service → DB → response}

## Service Layer

| Service | File | Responsibility |
|---------|------|---------------|
| UserService | `services/user.py` | User CRUD, auth |
| ... | ... | ... |

## Middleware Stack
Ordered list of middleware with purpose.

## Error Handling
How errors propagate, error response format, logging.
```

---

## AI/ML Pipeline

### What to investigate
- LLM client code (OpenAI, Anthropic, Google calls)
- Prompt templates
- RAG pipeline (embedding, retrieval, generation)
- Model config (temperature, tokens, providers)
- Training/fine-tuning scripts if present

### Template

```markdown
# AI/ML Pipeline

> Based on: {LLM client files, prompt files, config files}

## Pipeline Overview

{Mermaid graph TD: input → embed → retrieve → generate → output}

## LLM Providers
Table of supported providers, models, config.

## Prompt Templates
Key prompts used, their purpose, template variables.

## RAG Pipeline (if applicable)
Chunking strategy, embedding model, retrieval method, context injection.
```

---

## Configuration & Environment

### What to investigate
- .env.example / .env.sample
- Config files (JSON, YAML, TOML)
- Config loading code
- Feature flags
- Secrets management

### Template

```markdown
# Configuration & Environment

> Based on: {.env.example, config files, config loading code}

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `PORT` | No | `3000` | Server port |

## Configuration Files

### {config-file.json}
Purpose, key fields, how it's loaded.

## Feature Flags (if applicable)
How to toggle features on/off.
```

---

## Deployment & Infrastructure

### What to investigate
- Dockerfile / docker-compose.yml
- CI/CD configs (.github/workflows, .gitlab-ci.yml, Jenkinsfile)
- Infrastructure as code (Terraform, Pulumi, CDK)
- Build scripts (Makefile, scripts/)
- Kubernetes manifests

### Template

```markdown
# Deployment & Infrastructure

> Based on: {Dockerfile, docker-compose.yml, CI config files}

## Build Process
How the project is built (npm build, docker build, etc).

## Deployment Architecture

{Mermaid graph TD: build → registry → deploy → runtime}

## Docker Setup
Services, volumes, ports, health checks.

## CI/CD Pipeline
Steps, triggers, environments.

## Environment Configuration
How different environments (dev, staging, prod) are configured.
```

---

## Testing Strategy

### What to investigate
- Test directories (tests/, __tests__/, spec/, test/)
- Test config (jest.config, pytest.ini, vitest.config)
- Test fixtures / factories
- CI test steps

### Template

```markdown
# Testing Strategy

> Based on: {test config, sample test files, CI config}

## Test Structure

| Type | Directory | Framework | Count |
|------|-----------|-----------|-------|
| Unit | `tests/unit/` | pytest | ~50 |
| Integration | `tests/integration/` | pytest | ~20 |
| E2E | `tests/e2e/` | Playwright | ~10 |

## Running Tests
Commands to run tests locally.

## Test Patterns
Key patterns used (fixtures, mocks, factories).
```
