# Deployment Strategies: Best Practices

## Deployment Target Overview

| Target | Tool | Trigger | Typical Timeout |
| --- | --- | --- | --- |
| Docker → GHCR/ECR/GCR | `docker/build-push-action` | push to main | 10–15 min |
| Cloud Run / ECS / K8s | `gcloud` / `aws` CLI | push to main | 5–10 min |
| Static site → Vercel | Vercel GitHub integration | automatic | 2–5 min |
| Static site → Netlify | Netlify GitHub integration | automatic | 2–5 min |
| Static site → S3/CloudFront | `aws s3 sync` | push to main | 5 min |
| iOS → TestFlight | Fastlane / `xcrun altool` | push to main / tag | 30–45 min |
| Android → Google Play | Fastlane / `r0adkll/upload-google-play` | push to main / tag | 20–30 min |

---

## Container Deployments

### Docker → Cloud Run (GCP)

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4

      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ vars.WIF_PROVIDER }}
          service_account: ${{ vars.WIF_SERVICE_ACCOUNT }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker for GCR
        run: gcloud auth configure-docker ${{ vars.GCR_REGION }}-docker.pkg.dev

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ vars.GCR_REGION }}-docker.pkg.dev/${{ vars.GCP_PROJECT }}/${{ vars.REPO_NAME }}/app:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy ${{ vars.SERVICE_NAME }} \
            --image ${{ vars.GCR_REGION }}-docker.pkg.dev/${{ vars.GCP_PROJECT }}/${{ vars.REPO_NAME }}/app:${{ github.sha }} \
            --region ${{ vars.GCR_REGION }} \
            --allow-unauthenticated
```

### Docker → ECS (AWS)

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}

      - name: Login to ECR
        id: ecr-login
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.ecr-login.outputs.registry }}/${{ vars.ECR_REPO }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster ${{ vars.ECS_CLUSTER }} \
            --service ${{ vars.ECS_SERVICE }} \
            --force-new-deployment
```

---

## Static Site / Frontend Deployments

### Vercel (automatic)

Vercel's GitHub integration auto-deploys on push. No workflow needed for most cases. For custom control:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - run: npm ci

      - name: Deploy to Vercel
        run: npx vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_ORG_ID: ${{ vars.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ vars.VERCEL_PROJECT_ID }}
```

### S3 + CloudFront

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - run: npm ci && npm run build

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}

      - name: Sync to S3
        run: aws s3 sync dist/ s3://${{ vars.S3_BUCKET }} --delete

      - name: Invalidate CloudFront cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ vars.CLOUDFRONT_DIST_ID }} \
            --paths "/*"
```

---

## App Store Deployments

### iOS → TestFlight

```yaml
jobs:
  deploy-testflight:
    runs-on: macos-latest
    timeout-minutes: 45
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v')
    steps:
      - uses: actions/checkout@v4

      # ... (setup, build, and archive steps from mobile-app-pipelines.md)

      - name: Upload to TestFlight via Fastlane
        run: bundle exec fastlane upload_testflight
        env:
          APP_STORE_CONNECT_API_KEY_ID: ${{ secrets.ASC_KEY_ID }}
          APP_STORE_CONNECT_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}
          APP_STORE_CONNECT_API_KEY: ${{ secrets.ASC_PRIVATE_KEY }}

      # Or via xcrun:
      # - name: Upload to TestFlight
      #   run: xcrun altool --upload-app -f MyApp.ipa -t ios --apiKey $ASC_KEY_ID --apiIssuer $ASC_ISSUER_ID
```

### Android → Google Play

```yaml
jobs:
  deploy-play-store:
    runs-on: ubuntu-latest
    timeout-minutes: 25
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v')
    steps:
      - uses: actions/checkout@v4

      # ... (setup and build steps from mobile-app-pipelines.md)

      - name: Upload to Google Play (internal track)
        uses: r0adkll/upload-google-play@v1 # Pin to SHA in production
        with:
          serviceAccountJsonPlainText: ${{ secrets.GOOGLE_PLAY_SERVICE_ACCOUNT_JSON }}
          packageName: com.example.myapp
          releaseFiles: android/app/build/outputs/bundle/release/*.aab
          track: internal
          status: completed
```

### Expo (EAS Submit)

```yaml
- name: Submit to App Store
  run: eas submit --platform ios --latest --non-interactive

- name: Submit to Google Play
  run: eas submit --platform android --latest --non-interactive
```

---

## Multi-Environment Deployment

### Staging → Production promotion pattern

```yaml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, production]
        default: staging

concurrency:
  group: deploy-${{ github.event.inputs.environment || 'staging' }}
  cancel-in-progress: false # Never cancel deploys

permissions:
  contents: read
  id-token: write

jobs:
  deploy-staging:
    environment:
      name: staging
      url: https://staging.example.com
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      # ... build and deploy to staging

  deploy-production:
    needs: deploy-staging
    if: github.event.inputs.environment == 'production'
    environment:
      name: production
      url: https://example.com
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      # ... deploy to production (same image as staging)
```

> **Key principle**: Production should deploy the _same artifact_ that was validated in staging — never rebuild.

---

## Release Tagging & Versioning

### Tag-triggered release

```yaml
on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write # For creating GitHub Release
    steps:
      - uses: actions/checkout@v4

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2 # Pin to SHA in production
        with:
          generate_release_notes: true
          files: |
            dist/*.tar.gz
            dist/*.zip
```

### Semantic versioning with Changesets

```yaml
- name: Create Release PR
  uses: changesets/action@v1 # Pin to SHA in production
  with:
    publish: npx changeset publish
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

---

## Deployment Key Rules

| Rule | Reason |
| --- | --- |
| Use `concurrency` with `cancel-in-progress: false` for deploys | Never interrupt a deploy mid-way |
| Use GitHub Environments with required reviewers for production | Prevents accidental production deploys |
| Deploy the same artifact to production that passed staging | Rebuilding may introduce non-reproducibility |
| Use OIDC for cloud credentials | No long-lived secrets to rotate |
| Always invalidate CDN cache after static deploy | Users may see stale content otherwise |
| Use `--non-interactive` flags for all CLI deploys | Prevents CI hangs waiting for user input |
| Tag-based deploys for mobile releases | App Store/Play Store releases need explicit versioning |
| Store signing keys as base64-encoded secrets | Binary files cannot be stored directly in GitHub secrets |
