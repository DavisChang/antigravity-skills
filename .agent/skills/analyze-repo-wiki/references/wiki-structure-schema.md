# Wiki Structure Schema

Defines the structured format for planning a wiki before generating pages. Use this schema when you want to plan the wiki structure as a data artifact before writing pages.

## Structure Definition (JSON)

```json
{
  "title": "Project Name Wiki",
  "description": "Brief description of the repository",
  "sections": [
    {
      "id": "section-overview",
      "title": "Overview",
      "pages": ["page-1"]
    },
    {
      "id": "section-architecture",
      "title": "Architecture",
      "pages": ["page-2", "page-3"],
      "subsections": ["section-frontend"]
    }
  ],
  "pages": [
    {
      "id": "page-1",
      "title": "Project Overview",
      "description": "What the project does, tech stack, getting started",
      "importance": "high",
      "relevant_files": [
        "README.md",
        "package.json",
        "docker-compose.yml"
      ],
      "related_pages": ["page-2"],
      "output_file": "01-project-overview.md"
    }
  ]
}
```

## Field Reference

### Wiki Root

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Overall wiki title (usually "{Project} Wiki") |
| `description` | Yes | One-line project description |
| `sections` | No | Group pages into logical sections (for 8+ pages) |
| `pages` | Yes | All wiki pages |

### Section

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier (e.g., `section-overview`) |
| `title` | Yes | Display name |
| `pages` | Yes | Array of page IDs in this section |
| `subsections` | No | Array of child section IDs |

### Page

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier (e.g., `page-1`) |
| `title` | Yes | Page display name |
| `description` | Yes | What this page covers (1-2 sentences) |
| `importance` | Yes | `high`, `medium`, or `low` |
| `relevant_files` | Yes | 5-10 actual repo file paths to read for this page |
| `related_pages` | No | IDs of related pages for cross-linking |
| `output_file` | Yes | Output filename (e.g., `02-architecture.md`) |

## Importance Levels

- **high**: Core architecture, main features, critical systems — generate first
- **medium**: Supporting systems, secondary features, configuration
- **low**: Utilities, helpers, minor components — generate last or skip if constrained

## Page Count Guidelines

| Project Size | Recommended Pages | Structure |
|-------------|-------------------|-----------|
| Small (< 20 files) | 3-4 pages | Flat (no sections) |
| Medium (20-100 files) | 5-7 pages | Flat or light sections |
| Large (100-500 files) | 8-12 pages | Sectioned |
| Very large (500+ files) | 10-15 pages | Sectioned with subsections |

## Output Directory Layout

```
.wiki/
├── README.md                       # Index with TOC + architecture diagram
├── 01-project-overview.md          # Always first
├── 02-system-architecture.md       # High-level architecture
├── 03-{topic}.md                   # Additional pages...
├── 04-{topic}.md
├── ...
└── NN-configuration.md             # Config/env usually last
```

## Naming Conventions

- Files: `{NN}-{kebab-case-title}.md` with zero-padded number prefix
- Page IDs: `page-{N}` or descriptive like `page-architecture`
- Section IDs: `section-{name}`
