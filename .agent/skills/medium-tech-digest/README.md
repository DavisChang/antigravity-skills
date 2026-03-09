# Medium Tech Digest

An agent skill for fetching, summarizing, and delivering a weekly digest of the best technical articles from Medium.

---

## Overview

`medium-tech-digest` turns the Antigravity agent into a personalized tech curator. It scans Medium for high-quality technical articles published within the last 7 days, generates bilingual summaries in Traditional Chinese and English, archives the report locally, and can optionally deliver it via email.

---

## Features

| Feature | Description |
|:---|:---|
| **5 Curated Categories** | Core AI & LLMs · Dev+AI Integration · New Libraries & Tools · Architecture & Systems · Cross-Domain AI |
| **Full-text Summarization** | Reads complete article content — not just search snippets — for accurate, structured summaries |
| **Bilingual Reports** | Every digest includes both Traditional Chinese (繁體中文) and English versions |
| **Automated Archiving** | Reports saved to `medium_digest_output/medium_digest_<YYYY-MM-DD>/digest.md` |
| **Email Delivery** | Optional SMTP delivery via a customizable Python script |

---

## Directory Structure

```
medium-tech-digest/
├── SKILL.md                     # Core agent instructions and workflow logic
├── README.md                    # This file (English)
├── README_TW.md                 # Documentation in Traditional Chinese
└── scripts/
    └── send_email_template.py   # Reference script for email delivery
```

---

## Usage

Ask the Antigravity agent using any of these prompts:

```
Run the Medium tech digest for this week.
Give me a summary of recent AI news from Medium.
Collect top Medium articles and email them to me.
幫我收集最近一週 Medium 上的技術文章並寄信給我。
```

---

## Workflow Summary

```
Search Medium (5 categories)
    ↓
Filter: top 3 articles per category (recency + quality + depth)
    ↓
Summarize: Core Concept · Key Takeaway · Practical Application
    ↓
Compile: bilingual Markdown report (繁體中文 → English)
    ↓
Archive: medium_digest_output/medium_digest_<YYYY-MM-DD>/digest.md
    ↓
[Optional] Email delivery via send_email_template.py
```

---

## Article Categories

| Category | Key Topics |
|:---|:---|
| Core AI & LLMs | LLM, GPT, Claude, Gemini, Transformer, RAG, GenAI, Fine-tuning |
| Dev + AI Integration | LangChain, LlamaIndex, Vercel AI SDK, MCP, AI Agent, React AI |
| New Libraries & Tools | Open source releases, npm/PyPI packages, SDKs, CLI tools |
| Architecture & Systems | System design, microservices, scalability, observability, infra |
| Cross-Domain AI | AI in Biology, Finance, Art, Music, Healthcare, Science |

---

## Output Format

Each article summary follows this structure:

```markdown
### [Article Title](URL)
> *Author · Publication · Date*

**Core Concept**: One sentence on the main idea or technology.

**Key Takeaway**: Why it matters — breakthrough, efficiency gain, or new capability.

**Practical Application**: How a developer or team can apply this today.
```

Reports are saved to:

```
medium_digest_output/
└── medium_digest_2026-03-09/
    └── digest.md
```

---

## Email Delivery Setup

To use email delivery, set the following environment variables before running the agent:

```bash
export EMAIL_USER="you@gmail.com"
export EMAIL_PASS="your-app-password"    # Gmail App Password, not your account password
export EMAIL_RECIPIENT="recipient@example.com"
```

Then ask the agent:

```
Send the digest to my email.
```

The agent will reference `scripts/send_email_template.py` to generate and run a customized send script.

> **Note**: For Gmail, you must use an [App Password](https://support.google.com/accounts/answer/185833), not your regular account password.

---

## Customization

You can modify `SKILL.md` to adjust:

- **Search window**: Change `when:7d` to `when:30d` for monthly digests.
- **Articles per category**: Default is 3; increase or decrease as needed.
- **Preferred publications**: Add trusted Medium publications to prioritize quality sources.
- **Language preference**: Swap language order or add additional languages.
