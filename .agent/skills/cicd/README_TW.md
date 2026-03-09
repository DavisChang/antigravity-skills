# cicd Skill（中文說明）

GitHub Actions CI/CD 專家 Skill，適用於 **前端、後端及行動應用** 專案，提供業界最佳實踐建議，並直接完成設定。

## 涵蓋範圍

- **前端** — Node.js (npm/yarn/pnpm)、Vite/webpack 建置、Playwright E2E、Vitest/Jest
- **後端** — Python (pip/poetry)、Go、Java/Kotlin (Gradle/Maven)、Docker 建置與推送、資料庫 Migration
- **行動應用** — React Native (Expo/EAS、bare)、Flutter、iOS (Xcode/Fastlane)、Android (Gradle)
- **部署** — Docker Registry (GHCR/ECR/GCR)、Cloud Run/ECS、Vercel/Netlify、S3/CDN、TestFlight/App Store、Google Play
- **Self-hosted vs GitHub-hosted runner** — 環境持久性、macOS runner（iOS 建置）、Docker 建置、timeout 設定
- **Cache 策略** — 各語言快取（Node、Python、Go、Java、Mobile、Docker layers）
- **Workflow 觸發條件** — `on:` 事件、`paths` / `paths-ignore` 過濾、`concurrency`、`schedule`、條件式 `if`
- **CI 測試流程** — 單元測試、E2E、覆蓋率、Artifact 上傳、GITHUB_STEP_SUMMARY 報告
- **安全性與 Secrets** — 最小權限 `permissions:`、`secrets` vs `vars`、OIDC 認證、Action 版本釘選
- **Monorepo** — 路徑觸發、矩陣建置、Turborepo/Nx、可重用 Workflow

## 檔案結構

```
.agent/skills/cicd/
├── SKILL.md                              # 入口 — 決策樹與快速參考
├── README.md                             # 英文說明
├── README_TW.md                          # 本文件（中文）
└── references/
    ├── self-hosted-runners.md            # Runner 類型、macOS、Docker、環境持久性
    ├── caching-strategy.md               # 各語言與 Docker 的快取機制
    ├── workflow-triggers.md              # 觸發事件、過濾條件、並發控制
    ├── testing-in-ci.md                  # 各平台測試流程、覆蓋率、E2E
    ├── security-and-secrets.md           # 權限、Secrets、OIDC、Action 釘選
    ├── backend-pipelines.md              # Python、Go、Java/Kotlin、Docker、DB Migration
    ├── mobile-app-pipelines.md           # React Native、Flutter、iOS、Android、簽章
    ├── deployment-strategies.md          # Container、靜態網站、App Store/Play Store 部署
    └── monorepo-strategies.md            # 路徑觸發、矩陣建置、Turborepo/Nx
```

## 如何使用

在 Chat 輸入 `/cicd`，或直接用自然語言描述你的需求：

> 「為什麼 Self-hosted runner 上 Setup Node 要跑 20 分鐘？」
> 「新增一個 Playwright E2E workflow，只有在 PR 加上 `e2e` label 時才執行。」
> 「設定 Docker build and push 到 GHCR，加上 layer caching。」
> 「幫我建立 React Native EAS Build + TestFlight 上架的 CI/CD。」
> 「在 GitHub Actions 裡用 AWS 認證最安全的方式是什麼？」

## 設計原則

此 Skill 以**業界最佳實踐**為基礎，而非針對特定專案的配置：

1. **安全優先** — 最小權限、OIDC 取代長期 Secrets、Action SHA 釘選
2. **快速失敗** — 每個 Job 設 `timeout-minutes`、`cancel-in-progress` 並發控制
3. **可重現性** — 鎖定相依套件（`--frozen-lockfile`、`npm ci`、`pip install -r`）、釘選 Action 版本
4. **效能效率** — 只在有效的情境下使用 cache、`paths-ignore` 跳過不相關的觸發
5. **可觀測性** — 用 GITHUB_STEP_SUMMARY 展示測試結果、保存 Artifacts 供偵錯

## 快速索引

| 問題 | 對應文件 |
| --- | --- |
| Setup Node / yarn install 很慢 | [caching-strategy.md](./references/caching-strategy.md) |
| pip / Go / Gradle 安裝很慢 | [caching-strategy.md](./references/caching-strategy.md) |
| Docker 建置很慢 | [backend-pipelines.md](./references/backend-pipelines.md) |
| Workflow 被不相關的 commit 觸發 | [workflow-triggers.md](./references/workflow-triggers.md) |
| E2E 測試在 CI 不穩定或很慢 | [testing-in-ci.md](./references/testing-in-ci.md) |
| 如何安全儲存與使用認證 | [security-and-secrets.md](./references/security-and-secrets.md) |
| Self-hosted runner 行為異常 | [self-hosted-runners.md](./references/self-hosted-runners.md) |
| 建立後端 CI（Python/Go/Java） | [backend-pipelines.md](./references/backend-pipelines.md) |
| 建立行動應用 CI/CD | [mobile-app-pipelines.md](./references/mobile-app-pipelines.md) |
| 部署到雲端 / App Store / CDN | [deployment-strategies.md](./references/deployment-strategies.md) |
| Monorepo CI 優化 | [monorepo-strategies.md](./references/monorepo-strategies.md) |
