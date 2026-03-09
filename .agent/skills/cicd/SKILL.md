---
name: cicd
description: 'GitHub Actions CI/CD expert for frontend, backend, and mobile app projects. Use when: creating or modifying GitHub Actions workflows, configuring self-hosted runners, setting up caching strategy, managing secrets and permissions, optimizing workflow triggers, implementing concurrency controls, integrating test coverage and reporting, setting up deploy pipelines (Docker, cloud, CDN, App Store, Play Store), debugging slow or failing workflows, configuring monorepo CI, or applying CI/CD industry best practices. Covers: Node.js, Python, Go, Java/Kotlin, .NET (C#/F#), React Native, Flutter, iOS (Xcode/Fastlane), Android (Gradle), Docker builds, and deployment strategies.'
argument-hint: 'Describe your CI/CD task (e.g., "add a workflow for...", "why is setup-node slow on self-hosted?", "add concurrency control", "set up iOS build with TestFlight", "configure Docker build and push")'
---

# GitHub Actions CI/CD Expert

## What This Skill Does

- Design and create new GitHub Actions workflows from scratch
- Audit and optimize existing workflows for speed, reliability, and cost
- Diagnose CI problems (slowness, flakiness, unnecessary triggers)
- Apply industry best practices and explain the reasoning behind them
- Implement changes directly — not just suggestions
- **Supports**: Frontend (Node.js), Backend (Node.js, Python, Go, Java/Kotlin, .NET, Docker), Mobile (React Native, Flutter, iOS, Android)

---

## Decision Tree: Start Here

```
Frontend build/test slow?
├─ Setup Node takes minutes   → caching-strategy.md
├─ yarn/npm install is slow   → caching-strategy.md
└─ Browser install is slow    → testing-in-ci.md

Backend build/test slow?
├─ Node.js backend slow        → backend-pipelines.md
├─ pip/poetry install slow     → caching-strategy.md
├─ Go build/test slow          → caching-strategy.md
├─ Gradle/Maven build slow     → caching-strategy.md
├─ .NET restore/build slow     → caching-strategy.md
├─ Docker build slow           → backend-pipelines.md
└─ DB migration issues in CI   → backend-pipelines.md

Mobile app build?
├─ React Native (Expo/EAS)    → mobile-app-pipelines.md
├─ React Native (bare)        → mobile-app-pipelines.md
├─ Flutter build              → mobile-app-pipelines.md
├─ iOS build (Xcode)          → mobile-app-pipelines.md
├─ Android build (Gradle)     → mobile-app-pipelines.md
└─ Code signing issues        → mobile-app-pipelines.md

Deployment?
├─ Docker → Cloud (ECS/CR/K8s) → deployment-strategies.md
├─ Static site → CDN/Vercel    → deployment-strategies.md
├─ iOS → TestFlight/App Store  → deployment-strategies.md
├─ Android → Google Play       → deployment-strategies.md
└─ Multi-environment promote   → deployment-strategies.md

Monorepo?
├─ Only build changed apps     → monorepo-strategies.md
├─ Turborepo / Nx integration  → monorepo-strategies.md
└─ Shared reusable workflows   → monorepo-strategies.md

Workflow triggers unnecessarily?
└─ workflow-triggers.md

Secrets or permissions question?
└─ security-and-secrets.md

Self-hosted runner issue?
└─ self-hosted-runners.md

Tests are flaky or failing in CI?
└─ testing-in-ci.md
```

---

## Reference Documents

| Topic | Description |
| --- | --- |
| [self-hosted-runners.md](./references/self-hosted-runners.md) | Runner types, macOS for iOS, Docker builds, environment persistence, timeout |
| [caching-strategy.md](./references/caching-strategy.md) | Node.js, Python, Go, Java, Mobile, Docker caching strategies |
| [workflow-triggers.md](./references/workflow-triggers.md) | `on:` events, `paths` filters, `concurrency`, `schedule`, conditional `if` |
| [testing-in-ci.md](./references/testing-in-ci.md) | Unit/E2E testing: Vitest, Jest, Playwright, pytest, Go, JUnit, Detox, Flutter |
| [security-and-secrets.md](./references/security-and-secrets.md) | Least-privilege permissions, secrets vs vars, OIDC, action pinning |
| [backend-pipelines.md](./references/backend-pipelines.md) | Node.js backend, Python, Go, Java/Kotlin, .NET, Docker build & push, DB migrations, API testing |
| [mobile-app-pipelines.md](./references/mobile-app-pipelines.md) | React Native, Flutter, iOS (Xcode/Fastlane), Android, code signing |
| [deployment-strategies.md](./references/deployment-strategies.md) | Container, static site, App Store/Play Store, multi-env, rollback |
| [monorepo-strategies.md](./references/monorepo-strategies.md) | Path-based triggers, matrix builds, Turborepo/Nx, reusable workflows |

---

## Execution Process

When given a CI/CD task:

1. **Identify the project type** — frontend, backend, mobile, or monorepo
2. **Load relevant references** — use the decision tree above
3. **Read existing workflow files** — understand the current state before proposing changes
4. **Explain the recommendation** — what, why, and trade-offs
5. **Implement directly** — write the final configuration into the file

---

## Workflow Skeletons

### Frontend (Node.js)

```yaml
name: CI — Frontend

on:
  push:
    branches: ['main', 'stage/**']
    paths-ignore: ['**.md', 'docs/**']
  pull_request:
    branches: ['main', 'stage/**']
    types: [opened, synchronize, reopened, ready_for_review]
    paths-ignore: ['**.md', 'docs/**']
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          # Add `cache: 'npm'` or `cache: 'yarn'` ONLY on GitHub-hosted runners
          # On self-hosted runners, omit it — local disk cache is already persistent

      - run: npm ci # or: yarn install --frozen-lockfile
      - run: npm run lint
      - run: npm test
      - run: npm run build
```

### Backend (Python)

```yaml
name: CI — Backend

on:
  push:
    branches: ['main']
    paths: ['src/**', 'tests/**', 'requirements*.txt', 'pyproject.toml']
  pull_request:
    branches: ['main']
    paths: ['src/**', 'tests/**', 'requirements*.txt', 'pyproject.toml']
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip

      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: pytest --cov=src --junitxml=test-results.xml
```

### Backend (Docker)

```yaml
name: Build & Push Docker

on:
  push:
    branches: ['main']
  workflow_dispatch:

permissions:
  contents: read
  packages: write

jobs:
  docker:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Mobile App (React Native / EAS)

```yaml
name: Build — Mobile

on:
  push:
    branches: ['main']
    paths: ['src/**', 'app.json', 'package.json', 'eas.json']
  workflow_dispatch:

permissions:
  contents: read

jobs:
  eas-build:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - run: npm ci

      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}

      - run: eas build --platform all --profile preview --non-interactive
```

### Mobile App (Flutter)

```yaml
name: CI — Flutter

on:
  push:
    branches: ['main']
    paths-ignore: ['**.md', 'docs/**']
  pull_request:
    branches: ['main']
  workflow_dispatch:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.24'
          channel: stable
          cache: true

      - run: flutter pub get
      - run: flutter analyze
      - run: flutter test --coverage
```

---

## Key Rules at a Glance

| Rule | Reason |
| --- | --- |
| Always set `timeout-minutes` | Prevents hung jobs from consuming runner time indefinitely |
| Use `concurrency` with `cancel-in-progress: true` | Avoids stacking up duplicate runs on fast-push branches |
| Pin actions to a full SHA for third-party actions | Prevents supply-chain attacks via tag mutation |
| Use `permissions:` block at job level | Follows least-privilege principle |
| Use `vars.*` for non-sensitive config, `secrets.*` for credentials | Clear separation of sensitivity |
| Use `paths-ignore` or `paths` to scope triggers | Reduces unnecessary runner usage |
| Use lockfile-based installs (`npm ci`, `--frozen-lockfile`, `pip install -r`) | Ensures reproducible installs |
| Prefer OIDC over long-lived cloud credentials | Eliminates secret rotation burden |
| Do NOT add `cache:` on self-hosted runners | Local disk cache makes it counterproductive |
| Use `cache-from: type=gha` for Docker builds | Leverages GitHub Actions cache for Docker layers |
| Use macOS runners for iOS builds | Xcode is macOS-only; budget for ~10× Linux cost |
| Clean up signing materials in `if: always()` | Prevents keychain/cert leaks on shared runners |
| Use `--non-interactive` for all CLI deploys | Prevents CI hangs waiting for user input |
| Deploy same artifact staging → production | Rebuilding may introduce non-reproducibility |
