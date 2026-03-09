# Sentry Issue Fix Workflow

A step-by-step guide: Sentry MCP → detect platform → analyze → fix → verify → PR.

---

## Full Workflow Diagram

```
1. Fetch Issue Data (Sentry MCP: search new 30-day issues OR get specific issue)
       │
       ▼
1.5 Detect Platform (Frontend / Backend / App) from tags + stack frames
       │
       ▼
2. Parse Stack Trace → extract source file paths (platform-specific rules)
       │
       ▼
3. Read Source Code (read_file tool)
       │
       ▼
4. Analyze Root Cause (use platform-specific error pattern table)
       │
       ├─ Cause clear   → 5. Apply minimal-scope fix
       └─ Cause unclear → 6. Create PR documenting risk, no code change
       │
5. Apply Fix
       │
       ▼
6. Create Git branch + commit
       │
       ▼
7. Open Pull Request
       │
       ▼
8. Verify Fix: re-run 30-day new-issues query to confirm resolution
```

---

## Step 1: Fetch Issue Data

### Scenario A: Issue ID is known

```
mcp_sentry_get_issue_details(
  issueUrl = "https://org-name.sentry.io/issues/<SHORT_ID>"
)

mcp_sentry_get_sentry_issue_events(
  organization_slug = "org-name",
  issue_id = "<numeric_id>",
  full = true,
  limit = 1
)
```

### Scenario B: Find new regressions automatically (recommended starting point)

**Use the 30-day new-issues query** to discover issues that were introduced recently and have not yet been fixed:

```
mcp_sentry_search_issues(
  naturalLanguageQuery = "unresolved issues in production environment first seen in the last 30 days, sorted by event count descending",
  projectSlugOrId = "PROJECT-NAME",
  regionUrl = "https://us.sentry.io",
  limit = 10
)
```

This surfaces genuine **new issues** rather than long-standing known issues. Pick the one with the highest event count or user impact.

### Scenario C: Find highest-impact unresolved issues

```
mcp_sentry_search_issues(
  naturalLanguageQuery = "unresolved issues sorted by most events descending",
  projectSlugOrId = "PROJECT-NAME",
  regionUrl = "https://us.sentry.io",
  limit = 5
)
```

After getting the list in either scenario, call `mcp_sentry_get_sentry_issue_events` for the chosen issue.

---

## Step 1.5: Detect Platform

Before locating source code, determine the platform from the Sentry event data:

### Detection Rules

| Signal | Frontend | Backend | App (Mobile) |
|--------|----------|---------|---------------|
| `tags.browser` | ✅ Present | ❌ Absent | ❌ Absent or `WebView` |
| `tags.runtime` | — | ✅ `node` / `CPython` / `go` / `java` | — |
| `tags.os.name` | Desktop OS | `Linux` (server) | `iOS` / `Android` |
| `tags.device` | ❌ | ❌ | ✅ Present |
| `contexts.sdk.name` | `sentry.javascript.browser`, `sentry.javascript.vue` | `sentry.python`, `sentry.go`, `sentry.java`, `sentry.ruby` | `sentry.cocoa`, `sentry.java.android`, `sentry.dart.flutter`, `sentry.javascript.react-native` |
| Stack frame `.filename` | `.tsx`, `.jsx`, `.vue`, `.ts`, `.js` | `.py`, `.go`, `.java`, `.rb`, `.ts`/`.js` | `.swift`, `.m`, `.kt`, `.java`, `.dart`, `.tsx`/`.jsx` (RN) |

### Decision Logic

```
IF tags.browser exists AND contexts.sdk.name contains "browser"
  → Platform = Frontend

ELSE IF contexts.sdk.name contains "cocoa" OR "android" OR "flutter" OR "react-native"
  OR tags.os.name IN ("iOS", "Android") AND tags.device exists
  → Platform = App

ELSE IF tags.runtime IN ("node", "CPython", "go", "java", "ruby")
  OR contexts.sdk.name contains "python" OR "go" OR "java" OR "ruby"
  → Platform = Backend

ELSE
  → Platform = Unknown → treat as Frontend (default fallback)
```

---

## Step 2: Locate Source Code {#step-2-locate-source-code}

### Extract source paths from the stack trace

From the event's `exception.values[].stacktrace.frames`, filter for `in_app: true` frames.

### Path normalization — by platform

#### Frontend

| Sentry `filename` format | Normalized path |
|--------------------------|-----------------|
| `src/components/Foo.tsx` | `src/components/Foo.tsx` ✅ use as-is |
| `/usr/src/app/src/components/Foo.tsx` | strip everything before `src/` |
| `webpack:///src/components/Foo.tsx` | strip everything before `src/` |
| `./src/components/Foo.tsx` | remove `./` prefix |

#### Backend

| Sentry `filename` format | Normalized path |
|--------------------------|-----------------|
| **Node.js** `src/services/UserService.ts` | `src/services/UserService.ts` ✅ use as-is |
| **Node.js** `/usr/src/app/dist/services/UserService.js` | map `dist/` → `src/`, change `.js` → `.ts` if TS project |
| **Python** `app/services/user_service.py` | `app/services/user_service.py` ✅ use as-is |
| **Python** `/usr/local/lib/python3.11/site-packages/…` | ❌ skip — third-party package |
| **Go** `github.com/org/repo/internal/handler.go` | strip module prefix → `internal/handler.go` |
| **Java** `com.example.app.service.UserService` | convert to `src/main/java/com/example/app/service/UserService.java` |
| **Ruby** `app/controllers/users_controller.rb` | `app/controllers/users_controller.rb` ✅ use as-is |

#### App (Mobile)

| Sentry `filename` format | Normalized path |
|--------------------------|-----------------|
| **React Native** `src/screens/HomeScreen.tsx` | `src/screens/HomeScreen.tsx` ✅ use as-is |
| **React Native** `node_modules/react-native/…` | ❌ skip — framework internal |
| **iOS (Swift)** `MyApp/ViewControllers/HomeVC.swift` | `ios/MyApp/ViewControllers/HomeVC.swift` or search by filename |
| **iOS** symbolicated `HomeVC.swift:42` (no full path) | search repo for `HomeVC.swift` |
| **Android (Kotlin)** `com.example.app.ui.HomeActivity` | convert to `android/app/src/main/kotlin/com/example/app/ui/HomeActivity.kt` |
| **Flutter (Dart)** `package:myapp/screens/home.dart` | strip `package:myapp/` → `lib/screens/home.dart` |

### Source path directories to search (by platform)

| Platform | Primary directories |
|----------|-------------------|
| Frontend | `src/`, `components/`, `pages/`, `views/` |
| Backend | `src/`, `app/`, `lib/`, `server/`, `api/`, `internal/`, `cmd/` |
| App | `src/`, `ios/`, `android/`, `lib/` (Flutter), `screens/`, `components/` |

The frame's `context_line`, `pre_context`, and `post_context` provide ~10 lines of surrounding code — use these to pinpoint the exact area to read.

---

## Step 3: Read Source Code

Use the `read_file` tool:

- Read **50 lines before and after** the error line for sufficient context
- Read at most **5 files** to stay within context limits
- For React/RN components, also read the relevant TypeScript interface / props definition
- For Python, also read the relevant class or function imports
- For Go, also read the struct definition and interface the function implements
- For Swift/Kotlin, also read the protocol/interface the class conforms to

```
read_file(
  filePath = "/abs/path/to/repo/<platform-specific-path>",
  startLine = 1,       // or max(1, lineno - 50)
  endLine   = 100      // or lineno + 50
)
```

---

## Step 4: Analyze Root Cause {#step-4-analyze-root-cause}

### Frontend error patterns

| Error type | Common root cause | Typical fix |
|------------|-------------------|-------------|
| `TypeError: Cannot read properties of undefined` | Missing null check on object | Add optional chaining `?.` or guard clause |
| `TypeError: X is not a function` | Wrong function reference or async timing | Verify types, add guard |
| `TypeError: Object.hasOwn is not a function` | Browser compatibility — `Object.hasOwn` requires Chrome 93+ | Replace with `Object.prototype.hasOwnProperty.call(obj, key)` |
| `ReferenceError: X is not defined` | Uninitialized variable or missing import | Add import or initialize variable |
| `Unhandled Promise Rejection` | Missing try/catch in async function | Add error handling |
| Redux/RTK Query errors | Incorrect selector return-value assumption | Add default value or null check |
| Electron IPC errors (`No handler registered`) | Handler not registered before invocation | Ensure IPC handler is registered in main process |

### Backend error patterns

| Error type | Common root cause | Typical fix |
|------------|-------------------|-------------|
| **Node.js** `TypeError: Cannot read properties of undefined` | Missing null check on API response or DB result | Add null guard or optional chaining |
| **Node.js** `UnhandledPromiseRejection` | Missing `.catch()` or try/catch in async handler | Wrap in try/catch, add error middleware |
| **Python** `AttributeError: 'NoneType' has no attribute 'X'` | Variable is `None` when expected to have value | Add `if obj is not None` check or provide default |
| **Python** `KeyError: 'X'` | Missing key in dictionary | Use `.get('X', default)` instead of `['X']` |
| **Python** `IntegrityError` / `OperationalError` | DB constraint violation or connection issue | Add validation before insert, or connection retry |
| **Go** `runtime error: invalid memory address / nil pointer dereference` | Nil pointer not checked | Add `if ptr != nil` guard before dereference |
| **Go** `panic: runtime error: index out of range` | Array/slice bounds not checked | Add length check before access |
| **Java** `NullPointerException` | Null reference not checked | Add null check or use `Optional<>` |
| **Java** `SQLException` / `DataAccessException` | DB query failure, connection pool exhaustion | Add connection pool config, retry logic |
| **Ruby** `NoMethodError: undefined method 'X' for nil:NilClass` | Nil object method call | Add `&.` safe navigation or nil check |

### App (Mobile) error patterns

| Error type | Common root cause | Typical fix |
|------------|-------------------|-------------|
| **React Native** `TypeError` in bridge call | Native module not linked or method signature mismatch | Verify native module linking, check method params |
| **React Native** `Invariant Violation` | Component rendering before data loaded | Add loading state guard, check component lifecycle |
| **React Native** Red screen / JS bundle load failure | Metro bundler issue or corrupted cache | Clear cache; if code issue, fix import path |
| **iOS (Swift)** `Fatal error: Unexpectedly found nil while unwrapping` | Force unwrap `!` on nil Optional | Replace `!` with `guard let` / `if let` / `??` |
| **iOS (Swift)** `EXC_BAD_ACCESS` | Accessing deallocated memory | Check retain cycles, use `[weak self]` in closures |
| **iOS** `NSInvalidArgumentException` | Invalid argument to ObjC API | Validate argument before calling API |
| **Android (Kotlin)** `NullPointerException` / `KotlinNullPointerException` | Null safety bypass with `!!` or Java interop | Replace `!!` with `?.` / `?:` / `let { }` |
| **Android** `IllegalStateException: Fragment not attached` | Fragment lifecycle mismatch | Add `isAdded` / `isAttached` check |
| **Android** `OutOfMemoryError` | Image/bitmap not recycled, memory leak | Use image loading library (Glide/Coil), recycle bitmaps |
| **Flutter (Dart)** `Null check operator used on a null value` | `!` operator on null | Replace with `?.` or add null check |
| **Flutter (Dart)** `RangeError (index)` | List index out of bounds | Add bounds check before access |

### Risk assessment

If **any** of the following apply, **do not generate a code fix** — instead document the risk in the PR:

- Fix requires changes to more than **3 different files**
- Root cause involves a **database schema** or **API contract** change
- Stack trace points to **third-party package internals** (not application code)
- Fix requires changing a **shared component** with unclear impact scope
- **(App)** Fix requires native module changes that need a new app store release
- **(Backend)** Fix requires infrastructure/config changes (env vars, secrets, DB migration)

---

## Step 5: Apply Minimal-Scope Fix {#step-5-apply-minimal-scope-fix}

### Principles

1. Change only the smallest code snippet that causes this specific error
2. No refactoring, renaming, or formatting changes
3. Fixed code must satisfy existing type systems (TypeScript, mypy, Go compiler, etc.)
4. For null checks, prefer language-idiomatic patterns (see examples below)

### Fix examples by platform

#### Frontend (TypeScript/JavaScript)

```
replace_string_in_file(
  filePath  = "src/components/pages/Lesson/LessonPage.tsx",
  oldString = "  const lessonId = lesson.id;",
  newString = "  const lessonId = lesson?.id;"
)
```

#### Backend — Node.js

```
replace_string_in_file(
  filePath  = "src/services/UserService.ts",
  oldString = "  const email = user.profile.email;",
  newString = "  const email = user?.profile?.email ?? '';"
)
```

#### Backend — Python

```
replace_string_in_file(
  filePath  = "app/services/user_service.py",
  oldString = "    email = user['profile']['email']",
  newString = "    email = user.get('profile', {}).get('email', '')"
)
```

#### Backend — Go

```
replace_string_in_file(
  filePath  = "internal/handler/user.go",
  oldString = "	name := user.Profile.Name",
  newString = "	var name string\n\tif user != nil && user.Profile != nil {\n\t\tname = user.Profile.Name\n\t}"
)
```

#### App — Swift (iOS)

```
replace_string_in_file(
  filePath  = "ios/MyApp/ViewControllers/HomeVC.swift",
  oldString = "        let name = user!.name",
  newString = "        guard let name = user?.name else { return }"
)
```

#### App — Kotlin (Android)

```
replace_string_in_file(
  filePath  = "android/app/src/main/kotlin/com/example/app/ui/HomeActivity.kt",
  oldString = "        val name = user!!.name",
  newString = "        val name = user?.name ?: return"
)
```

#### App — Flutter (Dart)

```
replace_string_in_file(
  filePath  = "lib/screens/home.dart",
  oldString = "    final name = user!.name;",
  newString = "    final name = user?.name ?? '';"
)
```

**Important:** `oldString` must include at least 3 unchanged lines before and after the target for unambiguous matching.

---

## Step 6: Create Git Branch and Commit

### Branch naming

```
sentry-fix/<issue_id>
```

Example: `sentry-fix/1234567890`

### Create the branch (check for existence first)

```bash
git ls-remote --heads origin sentry-fix/<issue_id>
# If it already exists → skip to avoid duplicates

git checkout -b sentry-fix/<issue_id>
```

### Commit message format

```
[sentry-fix] <one-line summary>

Sentry issue: <issue_id>
Platform: <Frontend|Backend|App>
Error: <exception type>: <exception value>
Impact: <count> events, <userCount> users affected
Auto-generated by Sentry AI Fix Skill.
```

---

## Step 7: Open Pull Request

### PR title format

```
[Sentry-Fix] <First 60 chars of Sentry issue title>
```

### PR body (following `.github/pull_request_template.md`)

```markdown
## Reason / Purpose

Jira: N/A — Automated Sentry fix

> ⚠️ **This PR was auto-generated by the Sentry AI Fix Skill. Human review required before merging.**

**Sentry Issue**: [<shortId>](<sentry_issue_url>)
**Title**: <issue_title>
**Platform**: <Frontend|Backend|App> — <language/framework>
**Events**: <count> | **Users affected**: <userCount>
**First seen**: <firstSeen> | **Last seen**: <lastSeen>

---

## Changes

### Root Cause
<AI-analyzed root cause>

### Fix Description
<Technical explanation including before/after diff>

### Verification
<!-- Fill in after deploying -->
- 30-day new issues query re-run: [ ] issue no longer appears / [ ] event count decreasing
- Query used: `unresolved issues in production first seen in the last 30 days`

---

## Checklist

- [ ] Modified shared components?
- [ ] Committed code outside this PR's scope?
- [ ] Unit tests
- [ ] Flow diagram
- [ ] i18n
- [ ] Environment variables added to Parameter Store?
- [ ] (App) Does this fix require a new app store release?
- [ ] (Backend) Does this fix require a database migration?

---
*Auto-generated by [Sentry AI Fix Skill](/.github/skills/sentry-ai-fix/SKILL.md)*
```

### Create PR using gh CLI

```bash
gh pr create \
  --title "[Sentry-Fix] <title>" \
  --body "<pr body>" \
  --head "sentry-fix/<issue_id>" \
  --label "sentry-fix" \
  --label "ai-generated"
```

> If labels do not exist, remove the `--label` flags and retry.

---

## Step 8: Verify the Fix {#step-8-verify-fix}

After the PR is merged and deployed, re-run the **30-day new-issues query** to confirm the issue is resolved:

```
mcp_sentry_search_issues(
  naturalLanguageQuery = "unresolved issues in production first seen in the last 30 days, sorted by event count",
  projectSlugOrId = "PROJECT-NAME",
  regionUrl = "https://us.sentry.io",
  limit = 10
)
```

**Expected result**: The fixed issue no longer appears in this list, or its event count has stopped growing.

If the issue still appears with growing event counts, it means the root cause was not fully addressed — open a follow-up issue with the new data.

> **App-specific note**: Mobile app fixes require a new release to be published to App Store / Google Play. Event counts may continue for older app versions. Filter by `app.version` tag to verify the fix only in the new version.

---

## Summary Report to User

After completing the workflow, report:

1. **Which issue was fixed** (ID, title, affected user count)
2. **Platform detected** (Frontend / Backend / App + specific language/framework)
3. **Root cause** identified
4. **Which file and line** was modified
5. **PR link**
6. **Verification result** from the 30-day query (before vs. after)
7. **Any manual review items** (if risk was identified)
