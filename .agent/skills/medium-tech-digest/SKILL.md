---
name: medium-tech-digest
description: Use when the user wants a digest of top Medium tech articles (AI, Frontend/Backend, New Libraries, Cross-domain, Architecture) from the past 7 days, with optional email delivery.
---

# Medium Tech Digest

## Overview
This skill guides the agent to fetch, summarize, and optionally email a weekly digest of top Medium articles. It covers AI technology, practical dev integration, technical breakthroughs, new libraries, and cross-domain AI applications.

## When to Use
- User asks for "recent top Medium articles" or "tech digest".
- User wants a "summary of AI/tech news from Medium".
- User mentions collecting articles and sending them by email.
- User says "幫我整理 Medium 技術文章" or similar.

**When NOT to use:**
- User asks for general web search (use `search_web` directly).
- User wants deep technical debugging of a specific library.
- User wants news from sources other than Medium.

---

## Workflow

### Step 1 — Search Strategy

Use `search_web` with the following queries. Replace `7d` with the appropriate recency window (default: 7 days).

| Category | Query |
|:---|:---|
| Core AI & LLMs | `site:medium.com ("LLM" OR "Large Language Model" OR "RAG" OR "Transformer" OR "GenAI") when:7d` |
| Dev + AI Integration | `site:medium.com ("LangChain" OR "Vercel AI SDK" OR "React AI" OR "AI agent" OR "MCP") when:7d` |
| New Libraries & Tools | `site:medium.com ("new release" OR "open source" OR "just released") programming when:7d` |
| Architecture & Systems | `site:medium.com ("system design" OR "architecture" OR "technical deep dive" OR "engineering") when:7d` |
| Cross-Domain AI | `site:medium.com "AI" AND ("Biology" OR "Finance" OR "Art" OR "Music" OR "Science" OR "Healthcare") when:7d` |

**Search tips:**
- Prefer results from trusted publications: *Towards Data Science*, *Better Programming*, *Level Up Coding*, *The Startup*.
- If a query returns fewer than 3 usable results, broaden the date window to `30d`.
- Never fabricate URLs — only use links returned by the search tool.

---

### Step 2 — Filtering Criteria

Select **3 articles per category** (15 total) based on:

1. **Relevance**: Clearly matches the category topic.
2. **Quality signals**: High clap count (if visible), reputable publication, clear author credentials.
3. **Freshness**: Published within the last 7 days (verify date in article metadata or URL).
4. **Depth**: Prefers articles with code examples, benchmarks, diagrams, or novel insights over listicles.

> If a category yields fewer than 3 qualifying articles, reduce to 1–2 and note it in the report.

---

### Step 3 — Summarization

For each selected article:

1. **Fetch full content**: Use `read_url_content` to retrieve the full article text.
   - If blocked by a paywall or bot-check, use `read_browser_page` as fallback.
   - Do **not** rely on search snippets for summarization.

2. **Generate a structured summary** using this format:

```
### [Article Title](URL)
> *Author · Publication · Date*

**Core Concept**: One sentence describing the main idea or technology.

**Key Takeaway**: Why it matters — breakthrough, efficiency gain, new capability, or paradigm shift.

**Practical Application**: How a developer or team can apply this today.
```

---

### Step 4 — Compile Report

Assemble all summaries into a single Markdown report using this structure:

```markdown
# 📰 Medium Tech Digest — YYYY-MM-DD

## 🤖 Core AI & LLMs
[3 summaries]

## 🛠️ Dev + AI Integration
[3 summaries]

## 📦 New Libraries & Tools
[3 summaries]

## 🏗️ Architecture & Systems
[3 summaries]

## 🌐 Cross-Domain AI
[3 summaries]

---
*Report generated on YYYY-MM-DD. Articles sourced from Medium.*
```

**Language requirement**: Write the **Traditional Chinese (繁體中文)** version first, then append the **English** version in the same file, separated by a horizontal rule (`---`).

---

### Step 5 — Archive Report

1. Ensure the base output folder exists: `medium_digest_output/`
2. Create a timestamped subfolder: `medium_digest_output/medium_digest_<YYYY-MM-DD>/`
3. Save the report as: `medium_digest_output/medium_digest_<YYYY-MM-DD>/digest.md`

---

### Step 6 — Email Delivery (Optional)

Only proceed if the user explicitly requests email delivery.

1. Reference `scripts/send_email_template.py` to generate a customized send script.
2. Read content from the saved `digest.md`.
3. **Ask the user** for missing credentials if not already set via environment variables:
   - `EMAIL_USER` — sender email address
   - `EMAIL_PASS` — app password (not account password)
   - `EMAIL_RECIPIENT` — recipient address
4. Run the generated script to send the digest.
5. Confirm delivery success or surface the error to the user.

---

## Quick Reference

| Category | Key Terms |
|:---|:---|
| Core AI & LLMs | LLM, GPT, Claude, Gemini, Transformer, RAG, GenAI, Fine-tuning |
| Dev + AI | LangChain, LlamaIndex, Vercel AI SDK, MCP, AI Agent, React AI |
| Libraries & Tools | open source, release, npm, PyPI, CLI tool, SDK |
| Architecture | system design, microservices, scalability, observability, infra |
| Cross-Domain | AI + Bio, AI + Finance, AI + Art, AI + Healthcare |

---

## Common Mistakes

| Mistake | Fix |
|:---|:---|
| Fetching generic news instead of technical Medium posts | Enforce `site:medium.com` and prefer known publications |
| Hallucinating article links | **Only** use URLs returned by the search tool |
| Summarizing from snippets without reading full content | Always call `read_url_content` or `read_browser_page` |
| Missing the bilingual requirement | Generate 繁體中文 section first, English section second |
| Typo "Key Takeway" | Correct spelling is "Key Takeaway" |
