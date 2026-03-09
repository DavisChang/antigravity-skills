# Self-Hosted Runners: Best Practices

## Runner Types Overview

|                     | GitHub-Hosted                | Self-Hosted                          |
| ------------------- | ---------------------------- | ------------------------------------ |
| Environment         | Fresh VM every run           | **Persistent — same machine reused** |
| Post-run cleanup    | Automatic, fully clean       | **No automatic cleanup**             |
| Local cache         | None (rebuilt each run)      | **Persists across runs**             |
| `node_modules`      | Always reinstalled           | May still exist from last run        |
| GitHub remote cache | Useful — saves download time | Usually counterproductive            |
| Disk management     | Handled by GitHub            | **You are responsible**              |
| Security boundary   | Isolated VM per job          | Shared OS; code runs on your infra   |

---

## Configuring `runs-on`

### GitHub-Hosted (standard)

```yaml
runs-on: ubuntu-latest # or macos-latest, windows-latest
```

### Self-Hosted (by group)

```yaml
runs-on:
  group: my-runner-group
```

### Self-Hosted (group + label filter)

```yaml
runs-on:
  group: my-runner-group
  labels:
    - self-hosted
    - macOS
    - X64
```

> Use `labels` only when you have heterogeneous machines in a group and need to target specific ones. If all machines in the group are equivalent, `group:` alone is cleaner.

---

## The Most Important Difference: Environment Persistence

### What persists between runs on self-hosted:

- `~/.cache/yarn/` or `~/.npm/` — package manager cache (already warm)
- `~/.cache/ms-playwright/` — Playwright browser binaries
- `node_modules/` — unless explicitly cleaned
- Any files written to the workspace that weren't committed

### Why this matters

**Benefit:** Package installs are near-instant because the local disk cache is already populated from previous runs.

**Risk:** Leftover artifacts from previous runs can silently corrupt the current run.

```
Common failure modes:
- Stale test-results.xml → wrong pass/fail counts in summary
- Conflicting node_modules → mysterious import or version errors
- Residual .env files → picking up wrong environment variables
- Old build artifacts → shipping stale code
```

### Recommended mitigation

Option A — clean checkout (simplest, but removes `node_modules`):

```yaml
- uses: actions/checkout@v4
  with:
    clean: true # runs: git clean -ffdx
```

Option B — targeted cleanup (faster; preserves node_modules):

```yaml
- uses: actions/checkout@v4

- name: Clean previous test artifacts
  run: |
    rm -f test-results.xml
    rm -rf playwright-report test-results
```

> `clean: true` deletes everything in `.gitignore`, including `node_modules`. Use Option B if you want to preserve the local package cache.

---

## macOS Runners for iOS/macOS Builds

### When macOS runners are required

- **iOS builds** (Xcode, SwiftUI, CocoaPods) — mandatory
- **macOS native apps** — mandatory
- **React Native iOS** — mandatory
- **Flutter iOS** — mandatory

### GitHub-hosted macOS runners

```yaml
runs-on: macos-latest # or macos-14 for Apple Silicon (M1)
```

> **Cost**: macOS runners are ~10× more expensive than Linux per minute. Optimize build times aggressively.

### Self-hosted Mac mini considerations

- **Apple Silicon (M1/M2)**: Use `labels: [self-hosted, macOS, ARM64]` to target
- **Xcode versions**: Multiple Xcode versions can coexist; use `xcode-select` to switch
- **CocoaPods cache**: `~/Library/Caches/CocoaPods` persists — similar to yarn cache on self-hosted
- **Keychain**: Clean up signing keychains after each build to prevent keychain bloat

```yaml
# Target Apple Silicon self-hosted runner
runs-on:
  group: mac-runners
  labels: [self-hosted, macOS, ARM64]
```

---

## Docker Builds on Self-Hosted Runners

### Docker-in-Docker considerations

- **Docker socket**: Self-hosted runners need Docker daemon access
- **BuildKit**: Enable for better caching and parallel builds
- **Disk space**: Docker images accumulate — schedule periodic cleanup

```yaml
# Ensure BuildKit is enabled
env:
  DOCKER_BUILDKIT: 1

# Periodic cleanup (add to a scheduled workflow)
- name: Docker cleanup
  run: |
    docker system prune -af --volumes
    docker builder prune -af
```

### Security

> Running Docker on self-hosted runners means containers share the host kernel. For sensitive workloads, use ephemeral runners or rootless Docker.

---

## `timeout-minutes`: Always Required

On GitHub-hosted runners, billing stops when the job ends. On self-hosted runners, a hung job occupies the machine indefinitely without a timeout.

```yaml
jobs:
  test:
    runs-on:
      group: my-runners
    timeout-minutes: 15 # Set to ~2× the expected normal duration
```

| Workflow type         | Suggested timeout |
| --------------------- | ----------------- |
| Lint / type-check     | 5 min             |
| Unit tests + coverage | 10–15 min         |
| Build (Vite/webpack)  | 10 min            |
| Python tests (pytest) | 10–15 min         |
| Go build + test       | 10 min            |
| Gradle build + test   | 15–20 min         |
| Docker build + push   | 15 min            |
| Playwright E2E        | 30 min            |
| iOS build (Xcode)     | 45 min            |
| Android build (Gradle)| 30 min            |
| Flutter build (both)  | 30 min            |
| Full pipeline         | 60 min            |

---

## Security Considerations for Self-Hosted Runners

> Self-hosted runners run **your code** on **your machine**. This has significant security implications, especially for public repositories.

### Never use self-hosted runners on public repositories

A malicious PR can execute arbitrary code on your runner. Only use self-hosted runners for **private repositories**, or with strict controls.

### Additional hardening

```yaml
# Restrict workflows that CAN use self-hosted runners
# In the repository or organization settings:
# Settings → Actions → Runners → "Protected"
```

- Enable **"Require approval for first-time contributors"** (or all external contributors)
- Use separate runner groups for different trust levels (e.g., one group for PRs, one for deploys)
- Consider ephemeral runners (JIT runners) for sensitive workflows — they self-deregister after each job

### Ephemeral runner pattern (recommended for production)

Instead of long-running persistent runners, provision a fresh runner per job using tools like:

- [actions/runner](https://github.com/actions/runner) with `--ephemeral` flag
- [Philips-Labs/terraform-aws-github-runner](https://github.com/philips-labs/terraform-aws-github-runner)
- Kubernetes-based runners (GitHub Actions Runner Controller)

---

## Disk Space Management

Self-hosted runner disk is not automatically cleaned. Monitor and maintain periodically:

```bash
# Common large directories
~/.cache/ms-playwright/    # Old Playwright browser versions
~/.cache/yarn/             # Old yarn packages
~/.cache/pip/              # Old Python packages
~/go/pkg/mod/              # Go module cache
~/.gradle/                 # Gradle caches
~/Library/Caches/CocoaPods/  # CocoaPods cache (macOS)
/path/to/_work/            # GitHub Actions workspace (includes artifacts)

# Check Playwright installed versions
ls ~/.cache/ms-playwright/

# Docker cleanup
docker system prune -af --volumes
```

---

## Common Problems and Solutions

| Symptom                                  | Likely Cause                      | Fix                                                                                     |
| ---------------------------------------- | --------------------------------- | --------------------------------------------------------------------------------------- |
| `yarn install` takes 10–20 min           | `cache: yarn` uploading to GitHub | Remove `cache: yarn` — see [caching-strategy.md](./caching-strategy.md)                 |
| Tests pass/fail unpredictably            | Stale artifacts from previous run | Add `clean: true` or delete artifacts before tests                                      |
| Playwright browser reinstalls every time | Expected; it self-checks hashes   | Normal behavior — each run verifies, then skips if up-to-date                           |
| `node: command not found`                | PATH not set in runner shell      | Verify `setup-node` runs before node usage; check runner `~/.zshrc` / launch agent PATH |
| Job never finishes                       | Hung process, no timeout          | Always set `timeout-minutes`                                                            |
| iOS build fails on Linux runner          | Xcode requires macOS              | Use `runs-on: macos-latest` or self-hosted Mac                                          |
| Docker build out of disk space           | Images accumulate on self-hosted  | Schedule `docker system prune -af` cleanup                                              |
| Gradle build very slow on first run      | No cached dependencies            | Use `cache: gradle` in `setup-java` on GitHub-hosted                                    |
| CocoaPods version mismatch               | Runner has different Ruby/gem     | Pin CocoaPods version in Gemfile; use `bundle exec pod install`                         |
