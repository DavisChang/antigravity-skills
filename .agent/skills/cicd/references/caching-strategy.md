# Caching Strategy: Best Practices

## Core Principle

> **Cache only when the time saved exceeds the time spent managing the cache.**

Cache adds complexity: it can become stale, corrupt builds, and — on self-hosted runners — actually make things _slower_. Always justify each cache entry.

---

## How `actions/setup-node` `cache:` Works

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 22
    cache: yarn # or 'npm' or 'pnpm'
```

This option does two things per run:

| Phase                   | Action                                                                                               |
| ----------------------- | ---------------------------------------------------------------------------------------------------- |
| **Restore** (job start) | Downloads the package manager's global cache from GitHub's remote cache servers to the local machine |
| **Save** (job end)      | Compresses and uploads the local cache back to GitHub's servers                                      |

Cache key is derived from the lockfile hash (`yarn.lock`, `package-lock.json`). A different hash means cache miss → full download from registry.

---

## GitHub-Hosted vs Self-Hosted: The Critical Difference

### ✅ GitHub-Hosted Runners — Use `cache:`

```
Each run starts on a fresh, clean VM
→ No local package cache exists
→ Without cache: every package downloads from npm registry (~2–10 min)
→ With cache: restore from GitHub servers, much faster (~30 sec)
→ Net positive: saves 2–10 minutes per run
```

### ❌ Self-Hosted Runners — Do NOT Use `cache:`

```
Same machine reused across runs
→ ~/.cache/yarn/ already exists and is warm from previous runs
→ Without cache: yarn install completes in seconds (local hit)
→ With cache: setup-node additionally:
   1. Computes lockfile hash
   2. Queries GitHub cache API
   3. Downloads the remote cache archive (hundreds of MB)
   4. Extracts it over the already-warm local cache
   5. After the job: re-compresses and re-uploads it
→ Net negative: adds 5–20 minutes for zero benefit
```

**Rule: On self-hosted runners, omit `cache:` entirely.**

```yaml
# ✅ Correct for self-hosted
- uses: actions/setup-node@v4
  with:
    node-version: 22
    # No cache: option

# ❌ Wrong for self-hosted — adds 5–20 min overhead
- uses: actions/setup-node@v4
  with:
    node-version: 22
    cache: yarn
```

---

## What Persists on Self-Hosted Runners (No Config Needed)

| Path                      | Contents                    | Behavior                         |
| ------------------------- | --------------------------- | -------------------------------- |
| `~/.cache/yarn/`          | Yarn global package cache   | Warm after first run; stays warm |
| `~/.npm/`                 | npm global cache            | Same as above                    |
| `~/.cache/ms-playwright/` | Playwright browser binaries | Installed once, reused forever   |
| `node_modules/`           | Installed packages          | Persists unless `clean: true`    |

---

## Manual `actions/cache` for GitHub-Hosted Runners

When you need more control than `setup-node cache:` provides:

### Yarn

```yaml
- name: Get yarn cache directory
  id: yarn-cache-dir
  run: echo "dir=$(yarn cache dir)" >> $GITHUB_OUTPUT

- uses: actions/cache@v4
  id: yarn-cache
  with:
    path: ${{ steps.yarn-cache-dir.outputs.dir }}
    key: ${{ runner.os }}-yarn-${{ hashFiles('**/yarn.lock') }}
    restore-keys: |
      ${{ runner.os }}-yarn-

- run: yarn install --frozen-lockfile
```

### npm

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-npm-

- run: npm ci
```

### Playwright Browsers (GitHub-hosted only)

```yaml
- name: Cache Playwright browsers
  uses: actions/cache@v4
  id: playwright-cache
  with:
    path: ~/.cache/ms-playwright
    key: playwright-${{ runner.os }}-${{ hashFiles('**/yarn.lock') }}
    restore-keys: |
      playwright-${{ runner.os }}-

- name: Install Playwright browsers
  run: yarn playwright install --with-deps
  # playwright install self-checks hashes; already-cached browsers are skipped
  # On self-hosted: this completes instantly. On GitHub-hosted: uses cache above.
```

---

## Cache Key Design

A well-designed cache key balances **hit rate** (reuse) vs **correctness** (not reusing stale data).

```yaml
# Best: exact match on lockfile content
key: ${{ runner.os }}-yarn-${{ hashFiles('**/yarn.lock') }}

# Fallback: broader prefix, accepts partial matches (restore-keys)
restore-keys: |
  ${{ runner.os }}-yarn-
  ${{ runner.os }}-
```

**Include in the key:**

- `runner.os` — caches built on macOS ≠ Linux
- `hashFiles('**/yarn.lock')` — invalidates when dependencies change
- A version prefix (e.g., `v2-`) when you want to intentionally bust the cache

**Do not include:**

- Branch name (reduces hit rate without improving correctness)
- Commit SHA (guarantees 100% cache miss — use `restore-keys` instead)

---

## Cache Invalidation

| Cause                       | Effect                                         |
| --------------------------- | ---------------------------------------------- |
| `yarn.lock` changes         | Key hash changes → cache miss → full reinstall |
| Different OS                | `runner.os` differs → separate cache entry     |
| First run                   | No cache exists yet → cold start               |
| Cache unused for 7 days     | GitHub auto-expires (GitHub-hosted)            |
| Cache storage exceeds 10 GB | GitHub evicts oldest entries                   |
| Manual bust                 | Change key prefix (e.g., `v1-` → `v2-`)        |

---

## Python Caching

### pip

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: pip # Caches ~/.cache/pip

- run: pip install -r requirements.txt
```

### Poetry (with virtualenv)

```yaml
- uses: actions/cache@v4
  with:
    path: .venv
    key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}

- run: poetry install --no-interaction
```

---

## Go Caching

```yaml
- uses: actions/setup-go@v5
  with:
    go-version: '1.22'
    cache: true # Caches ~/go/pkg/mod and ~/.cache/go-build
```

> `setup-go` with `cache: true` handles both module cache and build cache automatically.

---

## Java / Kotlin Caching

### Gradle

```yaml
- uses: actions/setup-java@v4
  with:
    distribution: temurin
    java-version: '21'
    cache: gradle # Caches ~/.gradle/caches and ~/.gradle/wrapper
```

### Maven

```yaml
- uses: actions/setup-java@v4
  with:
    distribution: temurin
    java-version: '21'
    cache: maven # Caches ~/.m2/repository
```

---

## .NET Caching

```yaml
- uses: actions/setup-dotnet@v4
  with:
    dotnet-version: '8.0.x'

- uses: actions/cache@v4
  with:
    path: ~/.nuget/packages
    key: ${{ runner.os }}-nuget-${{ hashFiles('**/*.csproj', '**/Directory.Packages.props') }}
    restore-keys: |
      ${{ runner.os }}-nuget-

- run: dotnet restore
```

> `setup-dotnet` does not have a built-in `cache:` option like other setup actions. Use manual `actions/cache` targeting `~/.nuget/packages`.

---

## Mobile Caching

### CocoaPods (iOS)

```yaml
- uses: actions/cache@v4
  with:
    path: ios/Pods
    key: pods-${{ runner.os }}-${{ hashFiles('ios/Podfile.lock') }}
```

### Gradle (Android)

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
    key: gradle-${{ runner.os }}-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
```

### Flutter pub

```yaml
- uses: subosito/flutter-action@v2
  with:
    flutter-version: '3.24'
    cache: true # Caches Flutter SDK and pub dependencies
```

---

## Docker Layer Caching

```yaml
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

> See [backend-pipelines.md](./backend-pipelines.md) for full Docker build workflows.

---

## Decision Matrix

| Scenario                      | Recommendation                                                     |
| ----------------------------- | ------------------------------------------------------------------ |
| GitHub-hosted, Yarn/npm       | `cache: yarn` or `cache: npm` in setup-node                       |
| GitHub-hosted, Playwright     | Manual `actions/cache` on `~/.cache/ms-playwright`                 |
| GitHub-hosted, Python pip     | `cache: pip` in setup-python                                       |
| GitHub-hosted, Poetry         | Manual `actions/cache` on `.venv`                                  |
| GitHub-hosted, Go             | `cache: true` in setup-go                                          |
| GitHub-hosted, Gradle         | `cache: gradle` in setup-java                                      |
| GitHub-hosted, Maven          | `cache: maven` in setup-java                                       |
| GitHub-hosted, CocoaPods      | Manual `actions/cache` on `ios/Pods`                               |
| GitHub-hosted, Flutter        | `cache: true` in flutter-action                                    |
| GitHub-hosted, Docker layers  | `cache-from: type=gha` in build-push-action                       |
| GitHub-hosted, .NET (NuGet)   | Manual `actions/cache` on `~/.nuget/packages`                      |
| Self-hosted, any              | **No cache configuration needed** — local disk is already warm     |
| Self-hosted + `clean: true`   | Dependencies wiped → consider manual cache                         |
| Monorepo with many workspaces | Manual `actions/cache` with `hashFiles('**/lockfile')` across all  |
