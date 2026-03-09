# Sentry AI Fix Skill

A VS Code Copilot skill that closes the loop between **Sentry production errors** and **source code fixes** — supporting **Frontend, Backend, and App (Mobile)** platforms:

1. Query Sentry via MCP for new / high-impact issues
2. Auto-detect platform (Frontend / Backend / App) from Sentry tags and stack trace
3. Parse the stack trace and read the relevant source files using platform-specific path rules
4. Apply a minimal-scope fix using AI analysis with platform-aware error patterns
5. Verify the fix by re-querying Sentry's 30-day new-issue filter
6. Open a PR following the project's PR template

---

## Supported Platforms

| Platform | Languages & Frameworks |
|----------|----------------------|
| **Frontend** | React, Vue, Angular, TypeScript/JavaScript, Electron |
| **Backend** | Node.js, Python (Django/Flask/FastAPI), Go, Java (Spring Boot), Ruby (Rails) |
| **App (Mobile)** | React Native, iOS (Swift/Objective-C), Android (Kotlin/Java), Flutter (Dart) |

---

## Quick Start

Ask Copilot Chat (Agent mode) to invoke this skill, for example:

```
# Frontend
Fix the most critical Sentry error right now.
Fix Sentry issue PROJECT-NAME-B4.

# Backend
Fix the Python backend Sentry error causing 500s.
Show me all new Node.js production issues from the last 30 days.

# App (Mobile)
Fix the iOS crash reported in Sentry.
Fix the Android NullPointerException from Sentry issue MOBILE-APP-C12.
Show me all new React Native issues from the last 30 days.
```

The skill auto-loads from `.github/skills/sentry-ai-fix/SKILL.md`.

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **Sentry MCP** | Configured in `.vscode/mcp.json` → `https://mcp.sentry.dev/mcp` |
| **OAuth** | Complete browser authorization on first VS Code use |
| **Sentry project(s)** | One or more projects in your Sentry organization (frontend, backend, mobile) |
| **gh CLI** | Required for opening PRs from the terminal |

---

## How Platform Detection Works

The skill automatically determines the platform from the Sentry event data:

| Signal | Frontend | Backend | App (Mobile) |
|--------|----------|---------|---------------|
| `tags.browser` | ✅ Present | ❌ Absent | ❌ Absent |
| `tags.runtime` | — | ✅ `node`, `CPython`, `go` | — |
| `tags.os.name` | Desktop OS | `Linux` (server) | `iOS`, `Android` |
| `tags.device` | ❌ | ❌ | ✅ Present |
| SDK name | `sentry.javascript.browser` | `sentry.python`, `sentry.go` | `sentry.cocoa`, `sentry.java.android` |

---

## Finding New Issues (30-day filter)

The recommended entry point is querying for issues that **first appeared in the last 30 days** in the production environment. This focuses effort on genuine regressions rather than long-standing known issues.

The MCP call used:

```
mcp_sentry_search_issues(
  naturalLanguageQuery = "unresolved issues in production environment first seen in the last 30 days, sorted by event count descending",
  projectSlugOrId     = "PROJECT-NAME",
  regionUrl           = "https://us.sentry.io",
  limit               = 10
)
```

This maps to the Sentry query: `is:unresolved firstSeen:-30d environment:production`

---

## Verifying a Fix

After merging and deploying, re-run the same 30-day query. The fixed issue should no longer appear (or its event count should be decreasing). This result is documented in the PR body under the **Verification** section.

> **App note**: Mobile app fixes require a new app store release. Filter by `app.version` tag to verify the fix in the new version.

---

## File Structure

```
.agent/skills/sentry-ai-fix/
├── SKILL.md                      # Skill definition (loaded by Copilot)
├── README.md                     # This file — English overview
├── README_TW.md                  # Traditional Chinese overview
└── references/
    ├── mcp-tools.md              # Sentry MCP tool catalog & parameters
    └── fix-workflow.md           # Step-by-step fix workflow (8 steps)
```

---

## Workflow Summary

| Step | Action |
|------|--------|
| 1 | Fetch issue via `mcp_sentry_search_issues` (30-day new) or `mcp_sentry_get_issue_details` |
| 1.5 | **Detect platform** from tags (`browser`, `runtime`, `os.name`, `device`) and SDK context |
| 2 | Get full stack trace via `mcp_sentry_get_sentry_issue_events` |
| 3 | Extract `in_app: true` frames → normalize paths using **platform-specific rules** |
| 4 | Read source files with `read_file` (±50 lines around error) |
| 5 | Analyze root cause using **platform-specific error pattern table** → apply minimal fix |
| 6 | Risk check: skip code fix if >3 files, API contract, shared component, or platform-specific risk |
| 7 | Commit on branch `sentry-fix/<issue_id>`, open PR with template |
| 8 | Re-run 30-day query to verify the issue is resolved |

---

## Core Principles

- **Minimal scope** — only change the code directly causing the error
- **Human review** — every PR must be reviewed before merging
- **Verify with data** — always re-check Sentry after the fix is deployed
- **Skip when uncertain** — document risk in the PR rather than forcing a fix
- **Platform-aware** — detect and respect the platform context; use correct path rules and patterns

---

## Related Files

| File | Purpose |
|------|---------|
| `.vscode/mcp.json` | Sentry MCP server configuration |
| `.github/scripts/sentry_ai_fix.py` | GitHub Actions version (REST API, non-interactive) |
| `.github/workflows/sentry-ai-fix.yaml` | Daily scheduled workflow |
| `.github/pull_request_template.md` | PR template the skill follows |
| `docs/sentry-report-2026-03-09.md` | Sample production issue analysis report |
