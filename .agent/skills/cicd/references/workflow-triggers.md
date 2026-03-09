# Workflow Triggers: Best Practices

## The `on:` Block

Controls when a workflow runs. Being precise here prevents wasted runner time and annoying noise.

```yaml
on:
  push:
    branches: ['main', 'stage/**']
    paths-ignore: ['**.md', 'docs/**']
  pull_request:
    branches: ['main']
    types: [opened, synchronize, reopened, ready_for_review]
    paths-ignore: ['**.md', 'docs/**']
  schedule:
    - cron: '0 2 * * *' # Daily at 02:00 UTC
  workflow_dispatch: # Allow manual runs
```

---

## Event Reference

### `push`

Triggers on commits pushed to a branch.

```yaml
on:
  push:
    branches:
      - main
      - 'release/**'
      - 'stage/**'
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.github/CODEOWNERS'
```

### `pull_request`

Triggers on PR activity. The default activity types are `opened`, `synchronize`, `reopened`.

```yaml
on:
  pull_request:
    branches: ['main', 'stage/**']
    types:
      - opened
      - synchronize
      - reopened
      - ready_for_review # Re-trigger when converted from draft
    paths-ignore: ['**.md', 'docs/**']
```

> **`pull_request` vs `pull_request_target`**: Never use `pull_request_target` for CI that checks out and runs untrusted code — it runs in the context of the _base_ branch and has access to secrets, making it a vector for secret exfiltration from forked PRs.

### `schedule`

Cron-based periodic execution. Always specify in UTC.

```yaml
on:
  schedule:
    - cron: '0 2 * * 1-5' # 02:00 UTC Mon–Fri
    # = 10:00 Taiwan Time (UTC+8)
```

> Scheduled workflows run on the **default branch** only. They may be delayed by up to 15 minutes under high load.

### `workflow_dispatch`

Enables manual triggering from the GitHub UI or API.

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options: [staging, production]
        default: staging
      force:
        description: 'Force run even if nothing changed'
        required: false
        type: boolean
        default: false
```

### `workflow_call`

Makes the workflow reusable — callable from other workflows.

```yaml
on:
  workflow_call:
    inputs:
      node-version:
        type: string
        required: false
        default: '22'
    secrets:
      deploy-token:
        required: true
```

---

## `paths` vs `paths-ignore`

Use `paths` when you want CI to run **only** for specific file changes:

```yaml
# CI runs only when source files change
on:
  push:
    paths:
      - 'src/**'
      - 'public/**'
      - 'package.json'
      - 'yarn.lock'
      - 'Dockerfile'
```

Use `paths-ignore` when you want CI to run **except** for certain files:

```yaml
# CI skips doc-only commits
on:
  push:
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.github/CODEOWNERS'
```

> **`paths` and `paths-ignore` are mutually exclusive** per event — you cannot use both in the same trigger.

---

## Concurrency Control

Without concurrency control, rapid pushes create a queue of runs — most of which are already outdated.

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**How to choose `group`:**

```yaml
# Per-branch: cancels older runs on the same branch
group: ${{ github.workflow }}-${{ github.ref }}

# Per-PR: cancels older runs for the same PR
group: ${{ github.workflow }}-pr-${{ github.event.pull_request.number }}

# Global: only one run of this workflow at a time (useful for deploys)
group: deploy-production
cancel-in-progress: false   # For deploys: queue, don't cancel
```

> For **deploy workflows**, use `cancel-in-progress: false` to ensure deploys complete rather than being interrupted. For **CI checks**, use `true` to discard outdated runs immediately.

---

## Conditional `if` Expressions

### Job-level conditions

```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

  e2e:
    if: |
      github.event_name == 'schedule' ||
      github.event_name == 'workflow_dispatch' ||
      (github.event_name == 'pull_request' && contains(github.event.pull_request.labels.*.name, 'e2e'))
```

### Step-level conditions

```yaml
steps:
  - name: Deploy to production
    if: github.ref == 'refs/heads/main'

  - name: Notify on failure
    if: failure() # runs only if a previous step failed

  - name: Always upload artifacts
    if: always() # runs regardless of previous step outcomes

  - name: Upload on success or failure (but not cancelled)
    if: success() || failure()
```

### Checking PR labels

```yaml
if: contains(github.event.pull_request.labels.*.name, 'e2e')
```

---

## Skipping CI

### Commit-level skip (no workflow change needed)

Add `[skip ci]` or `[ci skip]` to the commit message — GitHub Actions automatically skips all workflows for that push.

```bash
git commit -m "chore: update changelog [skip ci]"
```

### Workflow-level skip via `paths-ignore`

```yaml
on:
  push:
    paths-ignore:
      - '**.md'
```

---

## Reusable Workflows Pattern

Extract common pipeline logic into reusable workflows to avoid duplication:

```yaml
# .github/workflows/reusable-test.yaml
on:
  workflow_call:
    inputs:
      node-version:
        type: string
        default: '22'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: npm
      - run: npm ci && npm test
```

```yaml
# .github/workflows/ci.yaml
jobs:
  run-tests:
    uses: ./.github/workflows/reusable-test.yaml
    with:
      node-version: '22'
    secrets: inherit
```

---

## Common Mistakes

| Mistake                                     | Problem                               | Fix                                                                                         |
| ------------------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------------- |
| No `paths-ignore` on PR trigger             | Runs CI on every doc edit             | Add `paths-ignore: ['**.md', 'docs/**']`                                                    |
| No `concurrency`                            | Old runs pile up and waste runners    | Add `concurrency` with `cancel-in-progress: true`                                           |
| Using `pull_request_target` with `checkout` | Secret exfiltration risk from forks   | Use `pull_request` for CI; use `pull_request_target` only for read-only labeling/commenting |
| No `workflow_dispatch`                      | Can't manually trigger, hard to debug | Add `workflow_dispatch:` to every workflow                                                  |
| `schedule` on non-default branch            | Won't run                             | Schedules always execute on the default branch                                              |
