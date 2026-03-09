# Backend Pipelines: Best Practices

## Language-Specific Setup

### Node.js (Express / Fastify / NestJS)

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm # or 'yarn' or 'pnpm'

      - run: npm ci

      - name: Lint
        run: npx eslint .

      - name: Type check
        run: npx tsc --noEmit

      - name: Run unit tests
        run: npm test -- --coverage

      - name: Run integration tests
        run: npm run test:integration
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379

      - name: Upload coverage
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: node-backend-coverage
          path: coverage/
```

#### NestJS-specific

```yaml
- run: npm ci
- run: npm run lint
- run: npm run test       # unit tests
- run: npm run test:e2e   # e2e tests with supertest
- run: npm run build      # verify production build
```

#### With service containers (database + Redis)

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: test
          POSTGRES_PASSWORD: test
        ports: ['5432:5432']
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
      redis:
        image: redis:7
        ports: ['6379:6379']
        options: --health-cmd "redis-cli ping" --health-interval 10s --health-timeout 5s --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm test
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379
```

---

### Python

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip # or 'poetry' or 'pipenv'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          # Or with poetry:
          # pip install poetry
          # poetry install --no-interaction

      - name: Lint
        run: |
          pip install ruff
          ruff check .

      - name: Type check
        run: |
          pip install mypy
          mypy src/

      - name: Run tests
        run: pytest --cov=src --cov-report=xml --junitxml=test-results.xml

      - name: Upload coverage
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.python-version }}
          path: coverage.xml
```

#### Poetry-specific setup

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'

- name: Install Poetry
  uses: snok/install-poetry@v1 # Pin to SHA in production
  with:
    virtualenvs-create: true
    virtualenvs-in-project: true

- name: Load cached venv
  uses: actions/cache@v4
  with:
    path: .venv
    key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}

- run: poetry install --no-interaction
```

---

### Go

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
          cache: true # Caches ~/go/pkg/mod and ~/.cache/go-build

      - name: Lint
        uses: golangci/golangci-lint-action@v6 # Pin to SHA in production
        with:
          version: latest

      - name: Run tests
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

---

### Java / Kotlin (Gradle)

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'
          cache: gradle

      - name: Grant execute permission for gradlew
        run: chmod +x gradlew

      - name: Build
        run: ./gradlew build

      - name: Run tests
        run: ./gradlew test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: build/reports/tests/
```

#### Maven variant

```yaml
- uses: actions/setup-java@v4
  with:
    distribution: temurin
    java-version: '21'
    cache: maven

- run: mvn -B verify
```

---

### .NET (C# / F#)

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'
          # Multiple versions:
          # dotnet-version: |
          #   6.0.x
          #   8.0.x

      - name: Restore dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore --configuration Release

      - name: Run tests
        run: dotnet test --no-build --configuration Release --verbosity normal --collect:"XPlat Code Coverage" --results-directory ./TestResults

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: TestResults/

      - name: Upload coverage
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: dotnet-coverage
          path: TestResults/**/coverage.cobertura.xml
```

#### NuGet package publish

```yaml
- name: Pack
  run: dotnet pack --configuration Release --no-build --output ./nupkgs

- name: Push to NuGet
  if: github.ref == 'refs/heads/main'
  run: dotnet nuget push ./nupkgs/*.nupkg --api-key ${{ secrets.NUGET_API_KEY }} --source https://api.nuget.org/v3/index.json
```

#### .NET Dockerfile (multi-stage)

```dockerfile
# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY *.sln .
COPY src/**/*.csproj ./src/
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /app/publish --no-restore

# Stage 2: Runtime (minimal)
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
ENTRYPOINT ["dotnet", "MyApp.dll"]
```

## Docker Build & Push

### Build and push to GitHub Container Registry (GHCR)

```yaml
jobs:
  docker:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Docker layer caching strategy

```yaml
# Option 1: GitHub Actions cache (recommended)
cache-from: type=gha
cache-to: type=gha,mode=max

# Option 2: Registry-based cache (for cross-workflow reuse)
cache-from: type=registry,ref=ghcr.io/${{ github.repository }}:buildcache
cache-to: type=registry,ref=ghcr.io/${{ github.repository }}:buildcache,mode=max
```

> **`mode=max`**: Caches all layers, not just the final image layers. Larger cache but much higher hit rate for multi-stage builds.

### Multi-stage Dockerfile best practices for CI

```dockerfile
# Stage 1: Dependencies (cached aggressively)
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

# Stage 2: Build
FROM deps AS builder
COPY . .
RUN yarn build

# Stage 3: Production image (minimal)
FROM node:22-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/server.js"]
```

> **Key principle**: Copy dependency files first so the install layer is cached until `package.json` or `yarn.lock` changes.

---

## Database Migration Validation in CI

Run migrations against a test database to catch migration errors before they reach production:

```yaml
jobs:
  migration-check:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4

      - name: Run migrations
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
        run: |
          # Prisma
          npx prisma migrate deploy
          # Or Django
          # python manage.py migrate
          # Or Go (golang-migrate)
          # migrate -path ./migrations -database "$DATABASE_URL" up

      - name: Verify schema
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
        run: |
          # Prisma: check for drift
          npx prisma migrate diff --from-migrations ./prisma/migrations --to-schema-datamodel ./prisma/schema.prisma --exit-code
```

### Service container patterns

```yaml
services:
  # PostgreSQL
  postgres:
    image: postgres:16
    env:
      POSTGRES_DB: test
      POSTGRES_PASSWORD: test
    ports: ['5432:5432']
    options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5

  # MySQL
  mysql:
    image: mysql:8
    env:
      MYSQL_ROOT_PASSWORD: test
      MYSQL_DATABASE: test
    ports: ['3306:3306']
    options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=5

  # Redis
  redis:
    image: redis:7
    ports: ['6379:6379']
    options: --health-cmd "redis-cli ping" --health-interval 10s --health-timeout 5s --health-retries 5
```

---

## API Testing in CI

### Newman (Postman collections)

```yaml
- name: Run API tests
  run: |
    npx newman run collection.json \
      --environment env.json \
      --reporters cli,junit \
      --reporter-junit-export api-test-results.xml
```

### Hurl (HTTP file-based testing)

```yaml
- name: Install Hurl
  run: |
    curl -LO https://github.com/Orange-OpenSource/hurl/releases/latest/download/hurl_amd64.deb
    sudo dpkg -i hurl_amd64.deb

- name: Run API tests
  run: hurl --test tests/**/*.hurl --report-junit api-results.xml
```

---

## Backend-Specific Key Rules

| Rule | Reason |
| --- | --- |
| Use `services:` for database dependencies | Isolated, reproducible test environment |
| Run migrations before tests | Validates schema matches code expectations |
| Use `npm ci` (not `npm install`) for Node.js backend | Ensures reproducible installs from lockfile |
| Run integration tests with service containers | Tests real database/Redis interactions |
| Use `-race` flag for Go tests | Detects data races that only appear under concurrency |
| Use `dotnet restore` before `dotnet build --no-restore` | Separates cacheable restore step from build |
| Use `--collect:"XPlat Code Coverage"` for .NET | Cross-platform coverage collection |
| Pin Docker base images to digest | Prevents unexpected base image changes |
| Use multi-stage Docker builds | Smaller production images, better layer caching |
| Use `docker/build-push-action` with `cache-from: type=gha` | Leverages GitHub Actions cache for Docker layers |
| Set `PYTHONDONTWRITEBYTECODE=1` in Python CI | Prevents `.pyc` pollution on self-hosted runners |
