# Security & Secrets: Best Practices

## Principle of Least Privilege

Every workflow should declare **only the permissions it actually needs**. GitHub Actions tokens are over-permissioned by default in older workflows.

### Set restrictive defaults, then grant per-job

```yaml
# Workflow level default: deny everything
permissions: {} # or: read-all

jobs:
  test:
    permissions:
      contents: read # checkout only
    runs-on: ubuntu-latest
    steps: ...

  comment-pr:
    permissions:
      pull-requests: write # post PR comment
      contents: read
    runs-on: ubuntu-latest
    steps: ...

  deploy:
    permissions:
      id-token: write # OIDC — request cloud credentials
      contents: read
    runs-on: ubuntu-latest
    steps: ...
```

### Common permission scopes

| Permission               | When needed                             |
| ------------------------ | --------------------------------------- |
| `contents: read`         | `actions/checkout`                      |
| `contents: write`        | Pushing commits, creating releases      |
| `pull-requests: write`   | Posting PR comments, labels             |
| `checks: write`          | Publishing test result annotations      |
| `actions: write`         | Deleting cache entries, re-running jobs |
| `id-token: write`        | OIDC — getting short-lived cloud tokens |
| `packages: write`        | Publishing to GitHub Packages / GHCR    |
| `security-events: write` | SARIF upload to code scanning           |

---

## Secrets vs Variables

|                    | `secrets.*`                         | `vars.*`                                    |
| ------------------ | ----------------------------------- | ------------------------------------------- |
| Content            | Sensitive (tokens, passwords, keys) | Non-sensitive (URLs, feature flags, config) |
| Visibility in logs | Masked automatically                | Visible in logs                             |
| Accessible via API | No                                  | Yes                                         |
| Example            | `secrets.DEPLOY_TOKEN`              | `vars.BASE_URL`                             |

```yaml
steps:
  - name: Deploy
    run: deploy.sh
    env:
      API_TOKEN: ${{ secrets.DEPLOY_TOKEN }} # Sensitive
      BASE_URL: ${{ vars.APP_BASE_URL }} # Non-sensitive
      ENVIRONMENT: ${{ vars.DEPLOY_ENVIRONMENT }} # Non-sensitive
```

> **Never put secrets in `vars.`** — they will appear in logs and the API.

---

## OIDC: Preferred Over Long-Lived Credentials

OIDC (OpenID Connect) lets your workflow request **short-lived, scoped cloud credentials** without storing static secrets. Supported by AWS, GCP, Azure, Vault, and others.

### Why OIDC is better

| Long-Lived Secret                      | OIDC Token                         |
| -------------------------------------- | ---------------------------------- |
| Never expires (until manually rotated) | Expires in minutes                 |
| Stolen secret = full access forever    | Stolen token = expires immediately |
| Requires rotation procedures           | No rotation needed                 |
| Stored in GitHub Secrets               | Not stored anywhere                |

### AWS OIDC example

```yaml
jobs:
  deploy:
    permissions:
      id-token: write # Required for OIDC
      contents: read
    steps:
      - name: Configure AWS credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: ap-east-1

      - name: Deploy
        run: aws s3 sync dist/ s3://my-bucket/
```

### GCP OIDC example

```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/PROJECT_ID/locations/global/workloadIdentityPools/POOL/providers/PROVIDER'
    service_account: 'sa@project.iam.gserviceaccount.com'
```

---

## Action Version Pinning

### The risk of unpinned actions

Tags like `@v4` or `@main` are **mutable** — the repository owner (or an attacker who compromises it) can change what they point to. This is a supply-chain attack vector.

### Best practice: pin to a full commit SHA

```yaml
# ❌ Vulnerable — tag can move
- uses: actions/checkout@v4

# ✅ Safe — SHA is immutable
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
```

### Practical approach: use Dependabot to manage pins

Add to `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    groups:
      actions:
        patterns: ['*']
```

Dependabot will automatically open PRs to update pinned SHAs when new versions are released.

### Risk tiers

| Action source                 | Risk level | Recommendation                               |
| ----------------------------- | ---------- | -------------------------------------------- |
| `actions/*` (GitHub official) | Low        | Pin to SHA; trust is high                    |
| Verified publishers           | Medium     | Pin to SHA; audit before use                 |
| Third-party / unknown         | High       | Pin to SHA; audit source code before use     |
| Your own org's actions        | Low        | Tag pinning acceptable within controlled org |

---

## Protecting Secrets from Forked PRs

### The fork PR problem

By default, `pull_request` workflows from forks do **not** have access to secrets. But `pull_request_target` does — and it runs in the context of the base branch, making it dangerous if combined with arbitrary code checkout.

```yaml
# ❌ DANGEROUS — runs attacker code with secret access
on: pull_request_target
steps:
  - uses: actions/checkout@v4 # Checks out attacker's code
    with:
      ref: ${{ github.event.pull_request.head.sha }}
  - run: npm ci && npm test # Attacker's code runs with secrets
```

```yaml
# ✅ Safe pattern for PR comments/labels from forks
# Workflow A: run tests (no secrets needed)
on: pull_request
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm test

# Workflow B: post comment (triggered by workflow completion, not PR)
on:
  workflow_run:
    workflows: ['CI']
    types: [completed]
jobs:
  comment:
    permissions:
      pull-requests: write
    runs-on: ubuntu-latest
    steps:
      - name: Post result comment
        uses: actions/github-script@v7
        with:
          script: |
            // safe — no untrusted code executed here
```

---

## Secret Scanning and Prevention

### Prevent accidental secret commits

Add a pre-commit hook or CI check:

```yaml
- name: Scan for secrets
  uses: trufflesecurity/trufflehog@main # Pin to SHA in production
  with:
    path: ./
    base: ${{ github.event.repository.default_branch }}
    head: HEAD
```

### GitHub native secret scanning

Enable in repository settings: **Security → Secret scanning → Enable**. GitHub automatically scans for known token patterns (AWS keys, GitHub PATs, etc.).

---

## Environment Protection Rules

For production deploys, use **GitHub Environments** to require manual approval:

```yaml
jobs:
  deploy-production:
    environment:
      name: production # References a protected Environment in repo settings
      url: https://myapp.com
    permissions:
      id-token: write
      contents: read
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: ./deploy.sh
```

In repository settings → Environments → production:

- Add required reviewers
- Set deployment branch filter to `main` only
- Add environment-specific secrets (separate from repo secrets)

---

## Security Checklist

- [ ] `permissions:` block at workflow or job level (never rely on defaults)
- [ ] Third-party actions pinned to full commit SHA
- [ ] `.github/dependabot.yml` configured to update action SHAs
- [ ] Secrets stored in `secrets.*`, non-sensitive config in `vars.*`
- [ ] OIDC used for cloud provider authentication
- [ ] No `pull_request_target` + `checkout` combination
- [ ] Production deploys use GitHub Environment with required reviewers
- [ ] Secret scanning enabled on the repository
- [ ] Self-hosted runners used only in private repositories (or with ephemeral runner setup)
