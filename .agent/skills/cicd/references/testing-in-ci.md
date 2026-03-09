# Testing in CI: Best Practices

## Unit Tests and Coverage

### Vitest

```yaml
- name: Run unit tests with coverage
  run: yarn test:coverage
# vitest.config.ts should include:
# coverage: { reporter: ['lcov', 'text', 'html'] }
# The lcov reporter generates coverage/lcov.info for SonarQube
```

### Jest

```yaml
- name: Run tests with coverage
  run: npx jest --coverage --coverageReporters=lcov,text
# Generates coverage/lcov.info
```

### Publishing test results as GitHub Check annotations

Use a JUnit XML reporter and upload results:

```yaml
- name: Run tests
  run: yarn test --reporter=junit --outputFile=test-results/junit.xml

- name: Publish Test Results
  uses: EnricoMi/publish-unit-test-result-action@v2 # Pin to SHA in production
  if: always()
  with:
    files: test-results/junit.xml
    check_name: Unit Test Results
```

### GITHUB_STEP_SUMMARY

Write a human-readable summary visible in the workflow run:

```yaml
- name: Test Summary
  if: always()
  run: |
    echo "## Test Results" >> $GITHUB_STEP_SUMMARY
    echo "- Total: $TOTAL" >> $GITHUB_STEP_SUMMARY
    echo "- Passed: $PASSED" >> $GITHUB_STEP_SUMMARY
    echo "- Failed: $FAILED" >> $GITHUB_STEP_SUMMARY
```

---

## SonarQube / SonarCloud Integration

```yaml
- name: SonarQube Scan
  uses: SonarSource/sonarqube-scan-action@v5 # Pin to SHA in production
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}
```

`sonar-project.properties` must point to the lcov file:

```properties
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.testExecutionReportPaths=test-results/junit.xml
```

> Run tests **before** the SonarQube step so coverage data exists when it scans.

---

## Playwright E2E in CI

### Worker count

E2E tests should be parallelized, but excessive parallelism destabilizes browser tests. Use 2 workers as a conservative CI default:

```yaml
- name: Run E2E tests
  run: yarn playwright test --workers=2
  # Or configure in playwright.config.ts:
  # workers: process.env.CI ? 2 : undefined
```

### Handling test failures

Use `continue-on-error: true` with a separate failure step. This ensures artifacts are always uploaded even when tests fail, which is critical for debugging:

```yaml
- name: Run E2E tests
  id: playwright
  continue-on-error: true
  run: yarn playwright test

- name: Upload Playwright artifacts
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: playwright-report-${{ github.run_id }}
    path: |
      playwright-report/
      tests/results/
      test-results.xml
    retention-days: 30

- name: Fail job if tests failed
  if: steps.playwright.outcome == 'failure'
  run: exit 1
```

> **Why this pattern?** If tests fail and you use `run: exit 1` directly, the step fails and all subsequent steps (like artifact upload) are skipped — leaving you with nothing to debug. `continue-on-error: true` + deferred `exit 1` ensures artifacts are always available.

### Full Playwright E2E workflow example

```yaml
name: Playwright E2E

on:
  pull_request:
    branches: ['main']
    types: [opened, synchronize, reopened, ready_for_review, labeled]
    paths-ignore: ['**.md', 'docs/**']
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:

concurrency:
  group: e2e-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  e2e:
    if: |
      github.event_name == 'schedule' ||
      github.event_name == 'workflow_dispatch' ||
      (github.event_name == 'pull_request' && contains(github.event.pull_request.labels.*.name, 'e2e'))
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps chromium

      - name: Run Playwright tests
        id: playwright
        continue-on-error: true
        run: npx playwright test --workers=2
        env:
          BASE_URL: ${{ vars.E2E_BASE_URL }}
          LOGIN_EMAIL: ${{ secrets.E2E_LOGIN_EMAIL }}
          LOGIN_PASSWORD: ${{ secrets.E2E_LOGIN_PASSWORD }}

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report-${{ github.run_id }}
          path: playwright-report/
          retention-days: 30

      - name: Fail if tests failed
        if: steps.playwright.outcome == 'failure'
        run: exit 1
```

---

## Node.js Backend Testing

```yaml
- name: Run unit tests
  run: npm test -- --coverage

- name: Run integration tests
  run: npm run test:integration
  env:
    DATABASE_URL: postgresql://test:test@localhost:5432/test
```

### Supertest (API integration tests)

```ts
// Example: tests/api.test.ts
import request from 'supertest';
import { app } from '../src/app';

describe('GET /api/health', () => {
  it('returns 200', async () => {
    await request(app).get('/api/health').expect(200);
  });
});
```

```yaml
# In CI — run as regular npm test
- run: npm run test:integration
```

---

## Python Testing (pytest)

```yaml
- name: Run tests with coverage
  run: pytest --cov=src --cov-report=xml --cov-report=html --junitxml=test-results.xml

- name: Upload coverage
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: python-coverage
    path: |
      coverage.xml
      htmlcov/
```

### Tox (multi-environment testing)

```yaml
- name: Run tox
  run: |
    pip install tox
    tox -e py311,py312,lint
```

---

## Go Testing

```yaml
- name: Run tests with race detection
  run: go test -race -coverprofile=coverage.out -covermode=atomic ./...

- name: Generate coverage report
  run: go tool cover -html=coverage.out -o coverage.html

- name: Upload coverage
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: go-coverage
    path: coverage.html
```

> Always use `-race` in CI — data races are a common source of production bugs that only manifest under concurrency.

---

## Java / Kotlin Testing

### Gradle + JUnit5

```yaml
- name: Run tests
  run: ./gradlew test

- name: Upload test report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-report
    path: build/reports/tests/
```

### Maven

```yaml
- run: mvn -B test
```

---

## .NET Testing (xUnit / NUnit)

```yaml
- name: Run tests with coverage
  run: dotnet test --configuration Release --verbosity normal --collect:"XPlat Code Coverage" --results-directory ./TestResults

- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: dotnet-test-results
    path: TestResults/
```

### Generate human-readable coverage report

```yaml
- name: Install ReportGenerator
  run: dotnet tool install -g dotnet-reportgenerator-globaltool

- name: Generate coverage report
  run: reportgenerator -reports:TestResults/**/coverage.cobertura.xml -targetdir:CoverageReport -reporttypes:Html

- uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: CoverageReport/
```

---

## Mobile Testing

### React Native (Detox E2E)

```yaml
- name: Install Detox CLI
  run: npm install -g detox-cli

- name: Build for Detox
  run: detox build --configuration ios.sim.release

- name: Run Detox tests
  run: detox test --configuration ios.sim.release --cleanup
```

### Flutter test

```yaml
- name: Run Flutter tests
  run: flutter test --coverage

- name: Upload coverage
  uses: actions/upload-artifact@v4
  with:
    name: flutter-coverage
    path: coverage/lcov.info
```

### XCTest (iOS native)

```yaml
- name: Run tests
  run: |
    xcodebuild test \
      -workspace MyApp.xcworkspace \
      -scheme MyApp \
      -destination 'platform=iOS Simulator,name=iPhone 16' \
      -resultBundlePath TestResults.xcresult
```

---

## Artifact Best Practices

### Naming artifacts with run ID

Always include `${{ github.run_id }}` or `${{ github.run_attempt }}` in artifact names to avoid collisions in matrix builds or re-runs:

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: test-results-${{ matrix.node }}-${{ github.run_id }}
    path: test-results/
```

### Retention policy

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: playwright-report
    path: playwright-report/
    retention-days: 30 # Keep for 30 days; 90 is default
    if-no-files-found: warn # warn | error | ignore
```

### What to upload

| Artifact                             | When to upload                                  | Retention |
| ------------------------------------ | ----------------------------------------------- | --------- |
| Playwright HTML report               | `if: always()`                                  | 30 days   |
| Playwright traces/screenshots/videos | `if: always()`                                  | 14 days   |
| Coverage report (HTML/lcov/xml)      | `if: success()` or `if: always()`               | 14 days   |
| Build output / APK / IPA             | On deploy workflows                             | 7 days    |
| JUnit XML / test-results             | `if: always()`                                  | 7 days    |
| Go coverage HTML                     | `if: always()`                                  | 14 days   |
| XCResult bundle                      | `if: always()`                                  | 14 days   |

---

## Test Parallelism Strategy

| Test type           | CI workers              | Notes                                                         |
| ------------------- | ----------------------- | ------------------------------------------------------------- |
| Unit tests (Vitest) | All available (default) | CPU-bound, no side effects                                    |
| Unit tests (pytest) | `-n auto` (pytest-xdist) | Auto-detects CPU count; install `pytest-xdist`               |
| Unit tests (Go)     | `-parallel` (default)   | Go runs tests in parallel per package by default              |
| Unit tests (JUnit)  | Gradle `maxParallelForks` | Configure in `build.gradle`                                 |
| Unit tests (.NET)   | `--parallel` (default)    | xUnit runs test classes in parallel by default              |
| Integration tests   | 4–8                     | Depends on shared resource contention                         |
| Playwright E2E      | 2                       | Browser tests are I/O-heavy; too many workers cause flakiness |
| Detox E2E           | 1–2                     | Simulator-based; serialized is more reliable                  |
| Flutter tests       | All available (default) | Dart test runner handles parallelism                          |
| API tests           | 4–8                     | Depends on target service capacity                            |

---

## Flaky Test Management

Common causes of flaky E2E tests in CI:

| Cause                      | Fix                                                                         |
| -------------------------- | --------------------------------------------------------------------------- |
| Insufficient timeouts      | Increase `timeout` in playwright.config.ts; CI machines can be slower       |
| Race conditions in app     | Use `waitFor` / `expect(locator).toBeVisible()` instead of `waitForTimeout` |
| Shared state between tests | Ensure tests are independent; use `storageState` per test where needed      |
| Test order dependency      | Randomize test order; use `--shard` for isolation                           |
| External service flakiness | Add retries in playwright.config.ts: `retries: process.env.CI ? 2 : 0`      |

```ts
// playwright.config.ts
export default defineConfig({
	retries: process.env.CI ? 2 : 0, // Retry flaky tests in CI
	timeout: 60_000, // Per-test timeout
	expect: { timeout: 10_000 }, // Assertion timeout
	workers: process.env.CI ? 2 : undefined
});
```
