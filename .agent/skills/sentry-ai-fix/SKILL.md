---
name: sentry-ai-fix
description: 'Sentry → AI Fix Expert for Frontend, Backend & App. Use when: reading live errors from Sentry, analyzing stack traces, locating source files, applying minimal-scope fixes, creating fix branches and opening PRs. Supports: React/Vue/Angular frontend, Node/Python/Go/Java backend, React Native/iOS/Android/Flutter mobile apps. Requires Sentry MCP connected (.vscode/mcp.json). USE FOR: fixing Sentry issues, analyzing root causes of production errors, auto-generating fix PRs across all platforms. DO NOT USE FOR: new feature development, refactoring, performance optimization.'
argument-hint: 'Enter the Sentry Issue ID to fix, or let the skill auto-fetch the highest-event unresolved issue (e.g. "fix Sentry issue 1234567890" or "fix the most critical Sentry error")'
---

# Sentry → AI Fix Expert (Frontend · Backend · App)

## What This Skill Does

- Reads issue details and stack traces directly via **Sentry MCP**
- **Auto-detects platform** (Frontend / Backend / App) from Sentry tags and stack trace characteristics
- Locates the corresponding source files using **platform-specific path rules**
- Analyzes root cause with **platform-aware error pattern matching**
- Creates a fix branch, commits, and opens a PR (following the PR template)
- Surfaces **new issues introduced in the last 30 days** to validate that fixes resolve recently-regressed behavior
- All changes require human review before merging

---

## Supported Platforms

| Platform | Languages & Frameworks |
|----------|----------------------|
| **Frontend** | React, Vue, Angular, TypeScript/JavaScript, Electron |
| **Backend** | Node.js, Python (Django/Flask/FastAPI), Go, Java (Spring Boot), Ruby (Rails) |
| **App (Mobile)** | React Native, iOS (Swift/Objective-C), Android (Kotlin/Java), Flutter (Dart) |

---

## Decision Tree: Start Here

```
Receive task
├─ Specific Sentry Issue ID provided?
│   ├─ Yes → [Fetch single issue via MCP](./references/mcp-tools.md#get_issue)
│   └─ No  → [Search for highest-impact unresolved issue](./references/mcp-tools.md#find_issues)
│            OR [Find new issues from last 30 days](./references/mcp-tools.md#find_new_issues)
│
├─ After fetching the issue
│   ├─ Get latest event (with full stack trace) → [mcp-tools.md#get_sentry_issue_events](./references/mcp-tools.md#get_sentry_issue_events)
│   └─ 🆕 Detect Platform → see "Platform Detection" below
│
├─ Platform Detection (from tags + stack trace)
│   ├─ Frontend → browser/os tags (Chrome, Firefox, Windows, macOS…)
│   │            stack frames: .tsx, .jsx, .vue, .ts, .js (browser context)
│   ├─ Backend  → runtime tag (node, python, go, java); no browser frame
│   │            stack frames: .py, .go, .java, .rb, .ts/.js (server context)
│   └─ App      → os.name tag (iOS, Android); device tags present
│                stack frames: .swift, .kt, .java (Android), .dart,
│                              or React Native (.tsx/.jsx with RN bridge frames)
│
├─ After locating source (using platform-specific path rules)
│   ├─ Read relevant file contents
│   ├─ Analyze root cause → [fix-workflow.md#analyze-root-cause](./references/fix-workflow.md#step-4-analyze-root-cause)
│   └─ Apply minimal-scope fix → [fix-workflow.md#apply-fix](./references/fix-workflow.md#step-5-apply-minimal-scope-fix)
│
└─ After fix is applied
    ├─ Create branch: sentry-fix/<issue_id>
    ├─ Commit: [sentry-fix] <summary>
    ├─ Open PR → [fix-workflow.md#open-pr](./references/fix-workflow.md#step-7-open-pull-request)
    └─ Verify fix: confirm issue no longer appears in new 30-day list
```

---

## Reference Documents

| Topic | Description |
|-------|-------------|
| [mcp-tools.md](./references/mcp-tools.md) | Sentry MCP tool catalog, parameters, and response formats |
| [fix-workflow.md](./references/fix-workflow.md) | Full fix workflow: locate → analyze → fix → verify → PR |
| [README.md](./README.md) | English overview and quick-start guide |
| [README_TW.md](./README_TW.md) | Traditional Chinese overview |

---

## Execution Steps

When a Sentry fix task is received, follow these steps:

### Step 1: Fetch Sentry Data

Load and use Sentry MCP tools (all tool names prefixed with `mcp_sentry_`).

1. If an issue ID is specified, call `mcp_sentry_get_issue_details` directly
2. If not specified, call `mcp_sentry_search_issues` with `firstSeen:-30d` to surface new regressions, or search by event volume for the most impactful issue
3. Call `mcp_sentry_get_sentry_issue_events` to get the latest event with full stack trace

See detailed tool usage → [mcp-tools.md](./references/mcp-tools.md)

### Step 1.5: Detect Platform

Determine the platform from the event data **before** locating source code:

| Signal | Frontend | Backend | App (Mobile) |
|--------|----------|---------|---------------|
| `tags.browser` | ✅ Present (Chrome, Firefox…) | ❌ Absent | ❌ Absent or WebView |
| `tags.runtime` | — | ✅ `node`, `python`, `go`, `java` | — |
| `tags.os.name` | `Windows`, `macOS`, `Linux` | `Linux` (server) | `iOS`, `Android` |
| `tags.device` | ❌ | ❌ | ✅ Present (iPhone, Pixel…) |
| Stack frame extensions | `.tsx`, `.jsx`, `.vue` | `.py`, `.go`, `.java`, `.rb` | `.swift`, `.kt`, `.dart` |
| SDK name (`contexts.sdk`) | `sentry.javascript.browser` | `sentry.python`, `sentry.go` | `sentry.cocoa`, `sentry.java.android`, `sentry.dart.flutter` |

Use the detected platform to select the correct path normalization rules and error pattern table in subsequent steps.

### Step 2: Locate Source Code

Extract source path frames from the stack trace and read the corresponding file contents. **Path rules vary by platform.**

See detailed steps → [fix-workflow.md](./references/fix-workflow.md)

### Step 3: Analyze and Fix

Analyze root cause using the **platform-specific error pattern table** and apply a minimal text-replacement fix. **Do not** refactor, add features, or modify unrelated code.

### Step 4: Verify the Fix

After applying the fix, re-query Sentry for issues matching `firstSeen:-30d is:unresolved` to confirm the issue is resolved or its event count has dropped. Document the before/after in the PR body.

### Step 5: Open PR

Create branch `sentry-fix/<issue_id>`, commit, and open a PR following the PR template.

---

## Core Principles

| Principle | Description |
|-----------|-------------|
| **Minimal scope** | Only change the code causing this specific error |
| **Human review** | PR must be reviewed by a human engineer before merging |
| **Idempotency** | If `sentry-fix/<issue_id>` branch already exists, skip to avoid duplicates |
| **Skip when uncertain** | If root cause is unclear or risk is high, document the risk in the PR instead of forcing a fix |
| **Verify with data** | Use `firstSeen:-30d` query to confirm new issues are resolved after the fix |
| **Platform-aware** | Always detect and respect the platform context — do not apply frontend patterns to backend code or vice versa |
