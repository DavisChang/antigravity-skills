# analyze-repo-wiki — Cursor Agent Skill

> English | **[繁體中文](README-TW.md)**

Transform any Git repository into structured wiki documentation, enabling AI agents to rapidly understand the entire codebase.

## What is this?

A **Cursor Agent Skill** that teaches the Cursor Agent how to:

1. Scan any project's file structure and detect the tech stack
2. Automatically determine which wiki pages are needed
3. Read source files page by page and generate technical docs with Mermaid diagrams
4. Output to a `.wiki/` folder as a knowledge base for both AI and humans

## Why do you need it?

| Pain Point | Solution |
|-----------|----------|
| Slow onboarding to new projects | Agent auto-generates architecture overviews, component docs, API references |
| AI doesn't understand your codebase | `.wiki/` provides structured context, making follow-up AI conversations more accurate |
| Docs are outdated or missing | Generated directly from source code, guaranteed to be in sync |
| Hard to grasp large repos | Automatically classifies and generates system architecture diagrams |

## Installation

Copy the `analyze-repo-wiki/` folder to your Cursor skills directory:

```bash
# Personal (available across all projects)
cp -r analyze-repo-wiki ~/.cursor/skills/

# Project-level (this project only)
cp -r analyze-repo-wiki .cursor/skills/
```

## Usage

### How to trigger

In Cursor Chat, tell the Agent in natural language:

```
Analyze this codebase and generate documentation
```

```
Create a wiki for this project so AI can understand it quickly
```

```
Generate a comprehensive wiki for this repo
```

```
Help me document this project
```

These keywords will trigger the Skill:
- `analyze repo` / `repo analysis`
- `generate wiki` / `create wiki`
- `document codebase` / `create documentation`
- `explain this project`

### Agent execution flow

Once triggered, the Agent automatically runs:

```
Phase 1: Scan & Classify
  ├─ Enumerate file tree (filter out node_modules, .git, etc.)
  ├─ Read README.md
  ├─ Detect tech stack (package.json, pyproject.toml, go.mod...)
  └─ Identify entry points and key directories

Phase 2: Determine Wiki Structure
  ├─ Decide which pages are needed based on project type
  ├─ List relevant source files for each page
  └─ Mark importance (high/medium/low)

Phase 3: Generate Pages
  ├─ Read source files page by page
  ├─ Generate Markdown with Mermaid diagrams, tables, code references
  └─ Every claim is cited with source file and line numbers

Phase 4: Output
  └─ Write to .wiki/ folder
```

### Output structure

```
.wiki/
├── README.md                      ← Wiki index (TOC + architecture diagram)
├── 01-project-overview.md         ← Project overview
├── 02-system-architecture.md      ← System architecture
├── 03-api-reference.md            ← API reference
├── 04-data-layer.md               ← Data layer
├── 05-frontend-architecture.md    ← Frontend architecture
├── 06-backend-architecture.md     ← Backend architecture
├── 07-deployment.md               ← Deployment
└── ...                            ← Dynamically adjusted per project type
```

### Use with other AI tools

The generated `.wiki/` can be used for:

- **Follow-up Cursor conversations**: Agent reads `.wiki/README.md` for instant project context
- **Team onboarding**: Structured project documentation for new members
- **Code review assistance**: Understand system architecture before reviewing code
- **Complement Cursor Rules**: `.wiki/` provides knowledge; Rules provide behavioral guidelines

## Customization

### Page count

Specify in the conversation:

```
Generate a concise wiki (4-6 pages)
Generate a comprehensive wiki with 10+ pages
```

### Focus areas

```
Focus on the API and data layer
Focus on the AI/ML pipeline and prompt templates
Only analyze the backend
```

### Include/exclude directories

```
Ignore tests/ and docs/ directories during analysis
Only analyze src/api/ and src/services/
```

## Skill structure

```
analyze-repo-wiki/
├── SKILL.md                           # Main skill file (read by Agent)
├── README.md                          # English usage guide (this file)
├── README-TW.md                       # 繁體中文 usage guide
└── references/
    ├── page-templates.md              # Detailed templates for each wiki page type
    ├── wiki-structure-schema.md       # Wiki structure definition (JSON schema)
    └── file-filters.md               # File inclusion/exclusion rules
```

| File | Purpose | When loaded |
|------|---------|-------------|
| `SKILL.md` | Core workflow and instructions | On skill trigger |
| `page-templates.md` | Templates for each page type | When generating page content |
| `wiki-structure-schema.md` | Structure definition format | When planning wiki structure |
| `file-filters.md` | Filtering rules | When scanning files |

## Methodology

1. **Scan** — Recursively read all repo files, filter out noise
2. **Classify** — Categorize by file type (code/doc) and purpose (impl/test)
3. **Plan structure** — Analyze file tree + README, decide wiki sections
4. **Generate content** — Read relevant source files per page, produce Markdown with diagrams and citations
5. **Output** — Write to a structured wiki folder
