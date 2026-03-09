# cicd Skill

A GitHub Actions CI/CD expert skill for frontend, backend, and mobile app projects. Provides industry best-practice guidance and hands-on implementation for designing, optimizing, and debugging GitHub Actions workflows across all project types.

## What It Covers

- **Frontend** — Node.js (npm/yarn/pnpm), Vite/webpack builds, Playwright E2E, Vitest/Jest
- **Backend** — Python (pip/poetry), Go, Java/Kotlin (Gradle/Maven), Docker build & push, DB migrations
- **Mobile** — React Native (Expo/EAS, bare), Flutter, iOS (Xcode/Fastlane), Android (Gradle)
- **Deployment** — Docker registries (GHCR/ECR/GCR), Cloud Run/ECS, Vercel/Netlify, S3/CDN, TestFlight/App Store, Google Play
- **Self-hosted vs GitHub-hosted runners** — environment persistence, macOS runners for iOS, Docker builds, timeout
- **Caching strategy** — per-language caching (Node, Python, Go, Java, Mobile, Docker layers)
- **Workflow triggers** — `on:` events, `paths` / `paths-ignore` filters, `concurrency`, `schedule`, conditional `if`
- **Testing in CI** — unit tests, E2E, coverage, artifact uploading, GITHUB_STEP_SUMMARY
- **Security & secrets** — least-privilege `permissions:`, `secrets` vs `vars`, OIDC authentication, action pinning
- **Monorepo** — path-based triggers, matrix builds, Turborepo/Nx, reusable workflows

## File Structure

```
.agent/skills/cicd/
├── SKILL.md                              # Entry point — decision tree and quick reference
├── README.md                             # This file (English)
├── README_TW.md                          # Chinese version
└── references/
    ├── self-hosted-runners.md            # Runner types, macOS, Docker, environment persistence
    ├── caching-strategy.md               # Cache mechanics for all languages and Docker
    ├── workflow-triggers.md              # Trigger events, filters, concurrency
    ├── testing-in-ci.md                  # Test pipelines, coverage, E2E for all platforms
    ├── security-and-secrets.md           # Permissions, secrets, OIDC, action pinning
    ├── backend-pipelines.md              # Python, Go, Java/Kotlin, Docker, DB migrations
    ├── mobile-app-pipelines.md           # React Native, Flutter, iOS, Android, code signing
    ├── deployment-strategies.md          # Container, static site, App Store/Play Store deploy
    └── monorepo-strategies.md            # Path-based triggers, matrix, Turborepo/Nx
```

## How to Invoke

Type `/cicd` in the chat, or describe your workflow task naturally:

> "Why does Setup Node take 20 minutes on my self-hosted runner?"
> "Add a Playwright E2E workflow that only runs with an `e2e` label on PRs to main."
> "Set up Docker build and push to GHCR with layer caching."
> "Configure EAS Build for React Native with TestFlight upload."
> "What's the safest way to use AWS credentials in GitHub Actions?"

## Design Principles

This skill is built around **industry best practices**, not project-specific opinions:

1. **Security first** — least-privilege permissions, OIDC over long-lived secrets, pinned action SHAs
2. **Fail fast** — `timeout-minutes` on every job, `cancel-in-progress` concurrency
3. **Reproducible** — locked dependencies (`--frozen-lockfile`, `npm ci`, `pip install -r`), pinned action versions
4. **Efficient** — cache only where it helps, `paths-ignore` to skip irrelevant runs
5. **Observable** — GITHUB_STEP_SUMMARY for test results, artifact retention for debugging

## Quick Reference

| Problem | Reference |
| --- | --- |
| Setup Node / yarn install is slow | [caching-strategy.md](./references/caching-strategy.md) |
| pip / Go / Gradle install is slow | [caching-strategy.md](./references/caching-strategy.md) |
| Docker build is slow | [backend-pipelines.md](./references/backend-pipelines.md) |
| Workflow triggers on unrelated commits | [workflow-triggers.md](./references/workflow-triggers.md) |
| E2E tests flaky or slow in CI | [testing-in-ci.md](./references/testing-in-ci.md) |
| How to store credentials safely | [security-and-secrets.md](./references/security-and-secrets.md) |
| Self-hosted runner behaves unexpectedly | [self-hosted-runners.md](./references/self-hosted-runners.md) |
| Setting up backend CI (Python/Go/Java) | [backend-pipelines.md](./references/backend-pipelines.md) |
| Setting up mobile app CI/CD | [mobile-app-pipelines.md](./references/mobile-app-pipelines.md) |
| Deploying to cloud / App Store / CDN | [deployment-strategies.md](./references/deployment-strategies.md) |
| Monorepo CI optimization | [monorepo-strategies.md](./references/monorepo-strategies.md) |
