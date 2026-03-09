# Sentry AI 修復 Skill

一個 VS Code Copilot Skill，將 **Sentry 線上錯誤**到**原始碼修復**的流程串成閉環——支援 **Frontend、Backend、App（Mobile）** 三大平台：

1. 透過 MCP 查詢 Sentry，找出新增的問題或高影響力 issue
2. **自動偵測平台**（Frontend / Backend / App），從 Sentry tags 與 stack trace 特徵判斷
3. 以**平台對應的路徑規則**解析 stack trace，讀取相關原始碼檔案
4. AI 以**平台專屬錯誤模式表**分析根本原因，套用最小範圍修復
5. 以近 30 天新問題過濾器**重新查詢 Sentry** 驗證修復效果
6. 依照專案 PR template 開 Pull Request

---

## 支援平台

| 平台 | 語言 & 框架 |
|------|------------|
| **Frontend** | React、Vue、Angular、TypeScript/JavaScript、Electron |
| **Backend** | Node.js、Python（Django/Flask/FastAPI）、Go、Java（Spring Boot）、Ruby（Rails） |
| **App（Mobile）** | React Native、iOS（Swift/Objective-C）、Android（Kotlin/Java）、Flutter（Dart） |

---

## 快速開始

在 Copilot Chat（Agent 模式）中描述任務，即可觸發此 Skill，例如：

```
# Frontend
修復目前最嚴重的 Sentry 錯誤
修復 Sentry issue PROJECT-NAME-B4

# Backend
修復 Python 後端 Sentry 錯誤導致的 500
列出近 30 天的 Node.js production 新問題

# App（Mobile）
修復 Sentry 回報的 iOS crash
修復 Sentry issue MOBILE-APP-C12 的 Android NullPointerException
列出近 30 天的 React Native 新問題
```

Skill 定義自 `.github/skills/sentry-ai-fix/SKILL.md` 自動載入。

---

## 前置條件

| 需求 | 說明 |
|------|------|
| **Sentry MCP** | 已設定於 `.vscode/mcp.json` → `https://mcp.sentry.dev/mcp` |
| **OAuth 授權** | 首次使用時在 VS Code 完成瀏覽器授權 |
| **Sentry 專案** | 一個或多個 Sentry 組織內的專案（前端、後端、行動端） |
| **gh CLI** | 從終端機開 PR 時需要 |

---

## 平台偵測機制

Skill 會自動從 Sentry event 資料判斷平台：

| 訊號 | Frontend | Backend | App（Mobile） |
|------|----------|---------|---------------|
| `tags.browser` | ✅ 有 | ❌ 無 | ❌ 無 |
| `tags.runtime` | — | ✅ `node`、`CPython`、`go` | — |
| `tags.os.name` | 桌面 OS | `Linux`（伺服器） | `iOS`、`Android` |
| `tags.device` | ❌ | ❌ | ✅ 有 |
| SDK 名稱 | `sentry.javascript.browser` | `sentry.python`、`sentry.go` | `sentry.cocoa`、`sentry.java.android` |

---

## 近 30 天新問題過濾（找新增問題）

建議以**近 30 天首次出現的問題**作為起點，聚焦在真正的問題退化（regression），而非長期已知的遺留問題。

使用的 MCP 呼叫：

```
mcp_sentry_search_issues(
  naturalLanguageQuery = "unresolved issues in production environment first seen in the last 30 days, sorted by event count descending",
  projectSlugOrId     = "PROJECT-NAME",
  regionUrl           = "https://us.sentry.io",
  limit               = 10
)
```

對應的 Sentry 查詢語法：`is:unresolved firstSeen:-30d environment:production`

---

## 驗證修復效果

PR 合入並部署後，重新執行同一個近 30 天查詢。若修復成功，該 issue 應不再出現於清單中（或事件數持續下降）。此結果需填入 PR 說明的**驗證區塊**中。

> **App 備註**：行動端修復需發佈新版至 App Store / Google Play。請以 `app.version` tag 過濾，確認新版本中 issue 已修復。

---

## 檔案結構

```
.agent/skills/sentry-ai-fix/
├── SKILL.md                      # Skill 定義（由 Copilot 載入）
├── README.md                     # 英文說明
├── README_TW.md                  # 本檔案——繁體中文說明
└── references/
    ├── mcp-tools.md              # Sentry MCP 工具目錄與參數說明
    └── fix-workflow.md           # 逐步修復流程（8 個步驟）
```

---

## 流程概覽

| 步驟 | 動作 |
|------|------|
| 1 | 以 `mcp_sentry_search_issues`（30 天新問題）或 `mcp_sentry_get_issue_details` 取得 issue |
| 1.5 | **偵測平台**：從 tags（`browser`、`runtime`、`os.name`、`device`）與 SDK context 判斷 |
| 2 | 以 `mcp_sentry_get_sentry_issue_events` 取得完整 stack trace |
| 3 | 篩選 `in_app: true` 的 frame，以**平台專屬規則**正規化路徑 |
| 4 | 以 `read_file` 讀取原始碼（錯誤行前後各 50 行） |
| 5 | 以**平台專屬錯誤模式表**分析根本原因 → 套用最小範圍修復 |
| 6 | 風險評估：若涉及 3 個以上檔案、API 契約、共用元件或平台特定風險，改在 PR 說明 |
| 7 | 在 `sentry-fix/<issue_id>` 分支 commit，依照 template 開 PR |
| 8 | 重新執行近 30 天查詢，確認 issue 已解決 |

---

## 核心原則

- **最小範圍** — 只修改直接造成此錯誤的程式碼
- **人工審查** — 每個 PR 都必須由工程師審查後才能合入
- **以資料驗證** — 部署後一定要重新查詢 Sentry 確認修復效果
- **不確定時不改** — 無法確定根本原因或風險過高時，在 PR 說明風險即可
- **平台感知** — 偵測並尊重平台 context；使用正確的路徑規則與錯誤模式

---

## 相關檔案

| 檔案 | 用途 |
|------|------|
| `.vscode/mcp.json` | Sentry MCP 伺服器設定 |
| `.github/scripts/sentry_ai_fix.py` | GitHub Actions 版本（REST API，非互動式） |
| `.github/workflows/sentry-ai-fix.yaml` | 每日定時執行的 workflow |
| `.github/pull_request_template.md` | Skill 遵循的 PR template |
| `docs/sentry-report-2026-03-09.md` | Production 問題分析報告範例 |
