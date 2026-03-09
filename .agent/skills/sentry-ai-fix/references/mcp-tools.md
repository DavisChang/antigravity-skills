# Sentry MCP Tool Reference

> Sentry MCP server is configured in `.vscode/mcp.json` (URL: `https://mcp.sentry.dev/mcp`).
> Complete OAuth authorization in VS Code before first use.
> All tool names are prefixed with `mcp_sentry_`.

---

## Tool Overview

| Tool Name | Purpose |
|-----------|---------|
| `mcp_sentry_search_issues` | Search Sentry issues with natural language or query filters |
| `mcp_sentry_get_issue_details` | Get full details for a single issue |
| `mcp_sentry_get_sentry_issue_events` | Get events for an issue (with full stack trace) |
| `mcp_sentry_find_organizations` | List accessible Sentry organizations |
| `mcp_sentry_find_projects` | List projects within an organization |
| `mcp_sentry_get_event_attachment` | Get attachments from a specific event |
| `mcp_sentry_get_trace_details` | Get full trace details for a transaction |

---

## search_issues

Search for issues matching specific conditions. This is the **primary tool** for discovering new regressions or high-impact problems.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `naturalLanguageQuery` | string | ✅ | Describe what you want to find in plain language |
| `projectSlugOrId` | string | — | Limit to a specific project (omit = all projects) |
| `regionUrl` | string | — | Sentry region URL, e.g. `https://us.sentry.io` |
| `limit` | number | — | Max results (default `25`, recommended `5`–`10`) |

### Common Query Patterns

```
# Find new issues first seen in the last 30 days (production)
naturalLanguageQuery: "unresolved issues in production first seen in the last 30 days, sorted by event count"
projectSlugOrId: "PROJECT-NAME"
regionUrl: "https://us.sentry.io"
limit: 10

# Find highest-impact unresolved issues
naturalLanguageQuery: "unresolved issues sorted by most events descending"
projectSlugOrId: "PROJECT-NAME"
limit: 5

# Find all issues active within 90 days
naturalLanguageQuery: "production environment, all unresolved issues last seen within 90 days, sorted by event count descending"
limit: 25
```

### Platform-Aware Query Patterns

Use these patterns to target issues from specific platforms:

#### Frontend-specific

```
naturalLanguageQuery: "unresolved issues in production first seen in the last 30 days with browser tag, sorted by event count"
projectSlugOrId: "FRONTEND-PROJECT"
```

#### Backend-specific

```
# Node.js backend
naturalLanguageQuery: "unresolved issues in production first seen in the last 30 days with runtime:node, sorted by event count"
projectSlugOrId: "BACKEND-PROJECT"

# Python backend
naturalLanguageQuery: "unresolved issues in production first seen in the last 30 days with runtime:CPython, sorted by event count"
projectSlugOrId: "BACKEND-PROJECT"

# Go backend
naturalLanguageQuery: "unresolved issues in production first seen in the last 30 days, sorted by event count"
projectSlugOrId: "GO-SERVICE-PROJECT"
```

#### App (Mobile)-specific

```
# iOS
naturalLanguageQuery: "unresolved issues first seen in the last 30 days with os.name:iOS, sorted by event count"
projectSlugOrId: "MOBILE-APP-PROJECT"

# Android
naturalLanguageQuery: "unresolved issues first seen in the last 30 days with os.name:Android, sorted by event count"
projectSlugOrId: "MOBILE-APP-PROJECT"

# React Native (shared project for both platforms)
naturalLanguageQuery: "unresolved issues in production first seen in the last 30 days, sorted by event count"
projectSlugOrId: "REACT-NATIVE-PROJECT"
```

### Finding New Issues (30-day filter) {#find_new_issues}

This is the **recommended starting point** to identify regressions introduced recently:

```
naturalLanguageQuery: "unresolved issues in production environment first seen in the last 30 days, sorted by event count descending"
projectSlugOrId: "PROJECT-NAME"
regionUrl: "https://us.sentry.io"
limit: 10
```

The MCP server translates this to `is:unresolved firstSeen:-30d environment:production` internally.

### Response Key Fields

```json
[
  {
    "id": "1234567890",
    "shortId": "PROJECT_NAME",
    "title": "TypeError: Cannot read properties of undefined",
    "culprit": "src/components/pages/Lesson/LessonPage.tsx in handleClick",
    "count": "142",
    "userCount": 42,
    "status": "unresolved",
    "firstSeen": "2026-02-10T08:00:00Z",
    "lastSeen": "2026-03-09T14:30:00Z",
    "project": { "slug": "PROJECT-NAME" }
  }
]
```

---

## get_issue_details

Fetch complete details for a single issue, including metadata and tags. {#get_issue}

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `issueUrl` | string | ✅ | Full Sentry issue URL, e.g. `https://org-name.sentry.io/issues/PROJECT_NAME` |

### Response Key Fields

Same as `search_issues`, plus:

```json
{
  "metadata": {
    "type": "TypeError",
    "value": "Cannot read properties of undefined (reading 'id')",
    "filename": "src/components/pages/Lesson/LessonPage.tsx"
  },
  "tags": [
    { "key": "browser", "value": "Chrome 120" },
    { "key": "os", "value": "Windows 10" },
    { "key": "runtime", "value": "node" },
    { "key": "device", "value": "iPhone 15 Pro" }
  ]
}
```

### Platform Detection from Tags

Use these tag keys to determine the platform:

| Tag Key | Frontend | Backend | App (Mobile) |
|---------|----------|---------|---------------|
| `browser` | ✅ `Chrome 120`, `Firefox 121` | ❌ absent | ❌ absent or `WebView` |
| `runtime` | — | ✅ `node`, `CPython`, `go1.22` | — |
| `os` / `os.name` | `Windows 10`, `macOS` | `Linux` | `iOS 17.2`, `Android 14` |
| `device` | ❌ absent | ❌ absent | ✅ `iPhone 15 Pro`, `Pixel 8` |
| `app.version` | ❌ absent | ❌ absent | ✅ `1.2.3` |

---

## get_sentry_issue_events

Fetch the event list for an issue. Each event includes a full stack trace and context.
**Use this tool** to get stack frames that map to source files.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `organization_slug` | string | ✅ | Sentry organization slug |
| `issue_id` | string | ✅ | Issue ID (numeric) |
| `full` | boolean | — | `true` returns full stack trace (recommended) |
| `limit` | number | — | Number of events to return; `1` is sufficient for root-cause analysis |

### Response Key Fields (Stack Trace Parsing)

#### Frontend / Node.js example

```json
{
  "id": "event_abc123",
  "dateCreated": "2026-03-09T14:30:00Z",
  "contexts": {
    "browser": { "name": "Chrome", "version": "120.0.0" },
    "os": { "name": "Windows", "version": "10" },
    "runtime": null
  },
  "exception": {
    "values": [
      {
        "type": "TypeError",
        "value": "Cannot read properties of undefined (reading 'id')",
        "stacktrace": {
          "frames": [
            {
              "filename": "src/components/pages/Lesson/LessonPage.tsx",
              "absPath": "/usr/src/app/src/components/pages/Lesson/LessonPage.tsx",
              "lineno": 42,
              "colno": 18,
              "function": "handleClick",
              "context_line": "  const lessonId = lesson.id;",
              "pre_context": [
                "  const handleClick = (lesson) => {",
                "    if (!lesson) return;"
              ],
              "post_context": [
                "    navigate(`/lesson/${lessonId}`);",
                "  };"
              ],
              "in_app": true
            }
          ]
        }
      }
    ]
  },
  "breadcrumbs": { "values": [] },
  "user": { "id": "user_123", "email": "user@example.com" },
  "request": { "url": "https://app.example.com/lesson", "method": "GET" }
}
```

#### Python backend example

```json
{
  "contexts": {
    "runtime": { "name": "CPython", "version": "3.11.4" },
    "os": { "name": "Linux" }
  },
  "exception": {
    "values": [
      {
        "type": "AttributeError",
        "value": "'NoneType' object has no attribute 'email'",
        "stacktrace": {
          "frames": [
            {
              "filename": "app/services/user_service.py",
              "absPath": "/usr/src/app/app/services/user_service.py",
              "lineno": 28,
              "function": "get_user_email",
              "context_line": "    return user.profile.email",
              "in_app": true
            }
          ]
        }
      }
    ]
  }
}
```

#### iOS (Swift) example

```json
{
  "contexts": {
    "os": { "name": "iOS", "version": "17.2" },
    "device": { "name": "iPhone 15 Pro", "model": "iPhone16,1" },
    "app": { "app_version": "1.2.3", "app_build": "42" }
  },
  "exception": {
    "values": [
      {
        "type": "Fatal error",
        "value": "Unexpectedly found nil while unwrapping an Optional value",
        "stacktrace": {
          "frames": [
            {
              "filename": "HomeViewController.swift",
              "function": "HomeViewController.viewDidLoad()",
              "package": "com.example.MyApp",
              "lineno": 35,
              "in_app": true,
              "symbolAddr": "0x100a4b2c0"
            }
          ]
        }
      }
    ]
  }
}
```

#### Android (Kotlin) example

```json
{
  "contexts": {
    "os": { "name": "Android", "version": "14" },
    "device": { "name": "Pixel 8", "model": "shiba" },
    "app": { "app_version": "2.0.1", "app_build": "100" }
  },
  "exception": {
    "values": [
      {
        "type": "java.lang.NullPointerException",
        "value": "Attempt to invoke virtual method on a null object reference",
        "stacktrace": {
          "frames": [
            {
              "filename": "HomeActivity.kt",
              "module": "com.example.app.ui.HomeActivity",
              "function": "onCreate",
              "lineno": 42,
              "in_app": true
            }
          ]
        }
      }
    ]
  }
}
```

### Stack Frame Parsing Guide

| Field | Meaning |
|-------|---------|
| `in_app: true` | **Application code** — prioritize these frames |
| `filename` | Relative path, maps to repo source file |
| `lineno` / `colno` | Exact error location |
| `context_line` | The line where the error occurred |
| `pre_context` / `post_context` | ~5 lines before/after for context |
| `module` | (Backend/Android) Fully qualified class/module name |
| `package` | (iOS/Android) App bundle or package identifier |
| `symbolAddr` | (iOS) Symbolicated address — ignore for source-level analysis |

### Platform-Specific Frame Filters

| Platform | `in_app` filter | Additional filters |
|----------|----------------|-------------------|
| Frontend | `in_app: true` + `filename` contains `src/` | Skip `node_modules/`, `webpack-internal://` |
| Backend (Node) | `in_app: true` | Skip `node_modules/`, `internal/` (Node core) |
| Backend (Python) | `in_app: true` | Skip `site-packages/`, `lib/python` |
| Backend (Go) | `in_app: true` | Skip `runtime/`, `net/http/`, GOROOT paths |
| Backend (Java) | `in_app: true` | Skip `java.`, `javax.`, `org.springframework.` core |
| App (iOS) | `in_app: true` | Skip `UIKit`, `Foundation`, `CoreFoundation` frames |
| App (Android) | `in_app: true` | Skip `android.`, `androidx.`, `java.lang.` frames |
| App (Flutter) | `in_app: true` | Skip `dart:`, `package:flutter/` frames |
| App (React Native) | `in_app: true` | Skip `node_modules/react-native/`, `com.facebook.react` frames |

---

## Verification Query (Post-Fix)

After applying a fix and merging the PR, re-run the 30-day new issues query to confirm the issue no longer appears:

```
naturalLanguageQuery: "unresolved issues in production first seen in the last 30 days, sorted by event count"
projectSlugOrId: "PROJECT-NAME"
regionUrl: "https://us.sentry.io"
limit: 10
```

If the fixed issue still appears, check whether the event count is decreasing over time (expected after a fix is deployed).

> **App note**: For mobile apps, filter by `app.version` tag to confirm the fix in the new version. Older app versions will continue producing events until users update.

---

## Authentication Notes

Sentry MCP uses **OAuth 2.0**. In VS Code, the browser opens automatically for authorization on first use; the token is managed by the MCP server afterward.

For **GitHub Actions** (non-interactive), use the REST API with `SENTRY_AUTH_TOKEN` secret instead. See `.github/scripts/sentry_ai_fix.py`.
