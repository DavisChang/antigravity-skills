---
name: medium-tech-digest
description: Use when the user wants a digest of top Medium tech articles (AI, Frontend/Backend, Cross-domain) from the past 7 days emailed to them.
---

# Medium Tech Digest

## Overview
This skill guides the agent to fetch, summarize, and email a weekly digest of top Medium articles. It covers AI technology, practical dev integration, technical breakthroughs, new libraries, and cross-domain AI applications.

## When to Use
- User asks for "recent top Medium articles".
- User wants a "tech digest" or "summary of AI news".
- User specifically mentions collecting articles and emailing them.

**When NOT to use:**
- User asks for general web search (use `search_web` directly).
- User wants deep technical debugging of a specific library.

## Workflow

### 1. Search Strategy
Use `search_web` with the following queries (adjust dates to "past 7 days"):
*   `site:medium.com "Artificial Intelligence" OR "LLM" OR "Transformer" min_claps:500 when:7d`
*   `site:medium.com "Frontend" OR "Backend" AND "AI" when:7d`
*   `site:medium.com "technical breakthrough" OR "architecture" when:7d`
*   `site:medium.com "new library" OR "release" programming when:7d`
*   `site:medium.com "AI" AND ("Art" OR "Biology" OR "Finance" OR "Music" OR "Science") when:7d` (Cross-domain)

### 2. Filtering Criteria
Select 3 articles per category based on:
- **Relevance**: Matches the specific category (e.g., truly "cross-domain").
- **Quality**: High clap count (if visible), trusted publications (e.g., Towards Data Science), or clear technical depth.
- **Freshness**: Must be published within the last 7 days.

### 3. Summarization
For each of the selected articles (3 per category):
1.  **Read Content**: Use `read_url_content` (or `read_browser_page` if behind a check) to fetch the **full text** of the article. Do not rely on search snippets.
2.  **Generate Summary**: Create a concise summary covering:
    - **Core Concept**: What is the main idea/tech?
    - **Key Takeway**: Why is it important? (Breakthrough, efficiency, new capability)
    - **Application**: How can it be used?

### 4. Delivery & Archiving
1.  **Generate Report**: Compile the summaries into a a Markdown report.
    -   **Requirement**: Provide the content in **Traditional Chinese (繁體中文)** first, followed by the **English** version.
2.  **Create Archive Folder**: 
    -   Ensure main output folder exists: `medium_digest_output/`
    -   Create timestamped subfolder: `medium_digest_output/medium_digest_<YYYY-MM-DD>` (use current date).
3.  **Save Report**: Save the bilingual report as `medium_digest_output/medium_digest_<YYYY-MM-DD>/digest.md`.
4.  **Email (Optional)**:
    -   Use the `scripts/send_email_template.py` as a reference to generate a customized script.
    -   Read the content from the saved `digest.md` file.
    -   **Ask the user** for their email credentials/settings if not already provided.
    -   Run the email script to send the digest.

## Quick Reference
| Category | Keywords |
|:---|:---|
| Core AI | LLM, Transformer, RAG, GenAI |
| Dev + AI | Vercel SDK, LangChain, React AI |
| Cross-Domain | AI in Bio, AI Art, FinTech AI |

## Common Mistakes
- **Mistake**: Fetching generic news articles instead of technical Medium posts.
    - **Fix**: Enforce `site:medium.com` and look for "Towards Data Science" or similar tags.
- **Mistake**: Hallucinating links.
    - **Fix**: ONLY use URLs returned by the search tool.
