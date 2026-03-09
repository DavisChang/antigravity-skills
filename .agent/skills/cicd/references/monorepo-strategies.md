# Monorepo Strategies: Best Practices

## When This Applies

Monorepo = multiple applications or packages in one repository. Common layouts:

```
repo/
├── apps/
│   ├── web/          # Frontend (Next.js, Vite)
│   ├── api/          # Backend (Node.js, Python, Go)
│   └── mobile/       # React Native / Flutter
├── packages/
│   ├── ui/           # Shared UI components
│   ├── utils/        # Shared utilities
│   └── config/       # Shared config (ESLint, TS, etc.)
├── package.json      # Root workspace
└── turbo.json        # Turborepo config (optional)
```

---

## Path-Based Triggers

Only run CI for the app/package that actually changed:

```yaml
# .github/workflows/ci-web.yaml
name: CI — Web
on:
  push:
    branches: [main]
    paths:
      - 'apps/web/**'
      - 'packages/ui/**'     # Shared dependency
      - 'packages/utils/**'  # Shared dependency
      - 'package.json'
      - 'yarn.lock'
  pull_request:
    branches: [main]
    paths:
      - 'apps/web/**'
      - 'packages/ui/**'
      - 'packages/utils/**'
```

```yaml
# .github/workflows/ci-api.yaml
name: CI — API
on:
  push:
    branches: [main]
    paths:
      - 'apps/api/**'
      - 'packages/utils/**'
      - 'package.json'
      - 'yarn.lock'
```

```yaml
# .github/workflows/ci-mobile.yaml
name: CI — Mobile
on:
  push:
    branches: [main]
    paths:
      - 'apps/mobile/**'
      - 'packages/ui/**'
      - 'packages/utils/**'
      - 'package.json'
      - 'yarn.lock'
```

> **Remember to include shared packages** in `paths:`. If `packages/ui/` changes, both `ci-web` and `ci-mobile` should trigger.

---

## Matrix Builds

Build and test multiple packages in a single workflow:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      web: ${{ steps.filter.outputs.web }}
      api: ${{ steps.filter.outputs.api }}
      mobile: ${{ steps.filter.outputs.mobile }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3 # Pin to SHA in production
        id: filter
        with:
          filters: |
            web:
              - 'apps/web/**'
              - 'packages/ui/**'
            api:
              - 'apps/api/**'
              - 'packages/utils/**'
            mobile:
              - 'apps/mobile/**'
              - 'packages/ui/**'

  test-web:
    needs: detect-changes
    if: needs.detect-changes.outputs.web == 'true'
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run test --workspace=apps/web

  test-api:
    needs: detect-changes
    if: needs.detect-changes.outputs.api == 'true'
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run test --workspace=apps/api

  test-mobile:
    needs: detect-changes
    if: needs.detect-changes.outputs.mobile == 'true'
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run test --workspace=apps/mobile
```

---

## Workspace Caching

### npm / yarn / pnpm workspaces

The `cache:` option in `setup-node` automatically handles workspace lockfiles:

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 22
    cache: npm # Automatically finds root package-lock.json
```

For more control:

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
      apps/*/node_modules
      packages/*/node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

### Turborepo cache

```yaml
- uses: actions/cache@v4
  with:
    path: .turbo
    key: turbo-${{ runner.os }}-${{ github.sha }}
    restore-keys: |
      turbo-${{ runner.os }}-
```

### Mixed-language monorepo caching

For monorepos with multiple languages (e.g., Node.js frontend + Python backend):

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 22
    cache: npm

- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: pip
    cache-dependency-path: apps/api/requirements.txt

# Each setup action manages its own cache independently
```

---

## Turborepo / Nx Integration

### Turborepo

```yaml
steps:
  - uses: actions/checkout@v4

  - uses: actions/setup-node@v4
    with:
      node-version: 22
      cache: npm

  - run: npm ci

  - name: Build affected packages
    run: npx turbo run build --filter='...[origin/main]'
    # Only builds packages that changed since main

  - name: Test affected packages
    run: npx turbo run test --filter='...[origin/main]'
```

### Nx

```yaml
steps:
  - uses: actions/checkout@v4
    with:
      fetch-depth: 0 # Nx needs full history for affected detection

  - uses: actions/setup-node@v4
    with:
      node-version: 22
      cache: npm

  - run: npm ci

  - name: Run affected tests
    run: npx nx affected --target=test --base=origin/main

  - name: Build affected apps
    run: npx nx affected --target=build --base=origin/main
```

> **`fetch-depth: 0`**: Both Nx and Turborepo need Git history to determine what changed. Default shallow clone (`depth: 1`) breaks affect detection.

---

## Reusable Workflows for Monorepos

Extract common CI logic into reusable workflows:

```yaml
# .github/workflows/reusable-node-test.yaml
name: Reusable Node Test

on:
  workflow_call:
    inputs:
      workspace:
        type: string
        required: true
        description: 'Workspace to test, e.g. apps/web'
      node-version:
        type: string
        default: '22'

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: npm
      - run: npm ci
      - run: npm run test --workspace=${{ inputs.workspace }}
      - run: npm run lint --workspace=${{ inputs.workspace }}
```

```yaml
# .github/workflows/ci-web.yaml
name: CI — Web
on:
  push:
    branches: [main]
    paths: ['apps/web/**', 'packages/ui/**']
jobs:
  test:
    uses: ./.github/workflows/reusable-node-test.yaml
    with:
      workspace: apps/web
```

```yaml
# .github/workflows/ci-api.yaml
name: CI — API
on:
  push:
    branches: [main]
    paths: ['apps/api/**', 'packages/utils/**']
jobs:
  test:
    uses: ./.github/workflows/reusable-node-test.yaml
    with:
      workspace: apps/api
```

---

## Monorepo Key Rules

| Rule | Reason |
| --- | --- |
| Use `paths:` triggers for per-app workflows | Only run CI for what changed; saves runner time |
| Include shared packages in `paths:` triggers | Changes to shared code must trigger dependent app CIs |
| Use `dorny/paths-filter` for complex change detection | More flexible than `on.push.paths` for matrix/conditional jobs |
| Use `fetch-depth: 0` with Nx/Turborepo | Full Git history required for affected/changed detection |
| Cache at workspace root level | Workspace lockfile covers all packages |
| Prefer reusable workflows over copy-paste | Consistent CI across apps; single point of maintenance |
| Use Turborepo/Nx `--filter` for affected-only builds | Dramatically reduces CI time on large monorepos |
| Separate deploy workflows per app | Different apps have different deploy targets and cadences |
