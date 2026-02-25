# Medium Tech Digest Skill

An automated agent skill for fetching, summarizing, and delivering the latest technical insights from Medium.

## Overview

The `medium-tech-digest` skill enables the Antigravity agent to act as a personalized tech curator. It scans Medium for high-quality technical articles published within the last 7 days, generates bilingual summaries, and can deliver the final report via email.

## Key Features

- **Curated Technical Categories**:
  - **Core AI & Technical Breakthroughs**: LLMs, Transformers, RAG, GenAI.
  - **Frontend/Backend + AI Integration**: Vercel SDK, LangChain, React AI.
  - **New Libraries & Tools**: Latest releases and programming tools.
  - **Cross-Domain AI Applications**: AI in Art, Biology, Finance, Science, etc.
  - **Architecture & Innovations**: Deep dives into systems and technical design.
- **Deep Research**: Uses full-text extraction (not just snippets) for accurate summarization.
- **Bilingual Reports**: Automatically generates summaries in both Traditional Chinese (繁體中文) and English.
- **Automated Archiving**: Saves reports in a structured `medium_digest_output/` directory with timestamped subfolders.
- **Email Delivery**: Supports optional delivery via SMTP with a customizable email script.

## Directory Structure

```
medium-tech-digest/
├── SKILL.md          # Core instructions and logic
├── README.md         # This documentation
└── scripts/
    └── send_email_template.py  # Reference for email delivery
```

## How to Use

Simply ask the Antigravity agent to run the tech digest.

**Example Prompts**:
- "Run the Medium tech digest for this week."
- "Give me a summary of recent AI news from Medium."
- "幫我收集最近一週 Medium 上的技術文章並寄信給我。"

## Workflow Details

1. **Search**: The agent performs targeted searches on Medium with clap-count and freshness filters.
2. **Filter**: Articles are selected based on relevance, quality, and publication date.
3. **Summarize**: The agent reads the full content of selected articles and creates structured summaries (Core Concept, Key Takeaway, Application).
4. **Output**: A Markdown report is generated as `digest.md` in the archive folder.
5. **Notify/Email**: The agent informs the user of the new digest and, if requested, sends it via email.

## Output Location

Reports are saved to:
`medium_digest_output/medium_digest_<YYYY-MM-DD>/digest.md`
