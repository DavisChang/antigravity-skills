# analyze-repo-wiki — Cursor Agent Skill

> **[English](README.md)** | 繁體中文

將任意 Git Repository 轉化為結構化的 Wiki 文件，讓 AI Agent 能夠快速理解整個 codebase。

## 這是什麼？

這是一個 **Cursor Agent Skill**，教導 Cursor Agent 如何：

1. 掃描任意專案的檔案結構與技術棧
2. 自動判斷需要哪些 Wiki 頁面
3. 逐頁讀取原始碼並生成帶有 Mermaid 圖表的技術文件
4. 輸出到 `.wiki/` 資料夾，作為 AI 和人類都能快速參考的知識庫

## 為什麼需要它？

| 痛點 | 解決方式 |
|------|---------|
| 新專案 onboarding 耗時 | Agent 自動生成架構總覽、元件說明、API 文件 |
| AI 不了解你的 codebase | `.wiki/` 提供結構化上下文，讓後續 AI 對話更精準 |
| 文件過時或不存在 | 直接從原始碼生成，保證與程式碼同步 |
| 大型 repo 難以掌握全貌 | 自動分類並生成系統架構圖 |

## 安裝

將整個 `analyze-repo-wiki/` 資料夾複製到你的 Cursor skills 目錄：

```bash
# 個人級（所有專案可用）
cp -r analyze-repo-wiki ~/.cursor/skills/

# 專案級（僅此專案）
cp -r analyze-repo-wiki .cursor/skills/
```

## 使用方式

### 觸發方式

在 Cursor Chat 中，用自然語言告訴 Agent：

```
幫我分析這個 repo 並生成 wiki 文件
```

```
Analyze this codebase and generate documentation
```

```
Create a wiki for this project so AI can understand it quickly
```

```
幫我產生這個專案的技術文件
```

以下關鍵字都會觸發此 Skill：
- `analyze repo` / `分析 repo`
- `generate wiki` / `生成 wiki`
- `document codebase` / `文件化`
- `repo analysis` / `專案分析`
- `explain this project` / `解釋這個專案`

### Agent 執行流程

觸發後，Agent 會自動執行：

```
Phase 1: Scan & Classify
  ├─ 列舉檔案樹（過濾 node_modules、.git 等噪音）
  ├─ 讀取 README.md
  ├─ 偵測技術棧（package.json, pyproject.toml, go.mod...）
  └─ 找出 entry points 和關鍵目錄

Phase 2: Determine Wiki Structure
  ├─ 根據專案類型決定需要哪些頁面
  ├─ 為每個頁面列出相關的原始碼檔案
  └─ 標記重要性（high/medium/low）

Phase 3: Generate Pages
  ├─ 逐頁讀取原始碼
  ├─ 生成 Markdown，含 Mermaid 圖表、表格、程式碼引用
  └─ 所有內容都附上原始碼出處

Phase 4: Output
  └─ 寫入 .wiki/ 資料夾
```

### 輸出結構

```
.wiki/
├── README.md                      ← Wiki 首頁（目錄 + 架構圖）
├── 01-project-overview.md         ← 專案總覽
├── 02-system-architecture.md      ← 系統架構
├── 03-api-reference.md            ← API 文件
├── 04-data-layer.md               ← 資料層
├── 05-frontend-architecture.md    ← 前端架構
├── 06-backend-architecture.md     ← 後端架構
├── 07-deployment.md               ← 部署方式
└── ...                            ← 依專案類型動態調整
```

### 配合其他 AI 工具使用

生成的 `.wiki/` 可以：

- **Cursor 後續對話**：Agent 可直接讀取 `.wiki/README.md` 快速了解專案
- **新成員 Onboarding**：提供結構化的專案入門文件
- **Code Review 輔助**：了解系統架構後，更有效地 review 程式碼
- **作為 Cursor Rules 的補充**：`.wiki/` 提供知識，Rules 提供行為規範

## 自訂選項

### 頁面數量

在對話中指定：

```
幫我生成一個精簡版的 wiki（4-6 頁）
Generate a comprehensive wiki with 10+ pages
```

### 指定重點

```
重點分析 API 和資料層
Focus on the AI/ML pipeline and prompt templates
只分析 backend 部分
```

### 排除/包含特定目錄

```
分析時忽略 tests/ 和 docs/ 目錄
只分析 src/api/ 和 src/services/ 的程式碼
```

## Skill 結構

```
analyze-repo-wiki/
├── SKILL.md                           # 主技能文件（Agent 讀取此檔）
├── README.md                          # 英文使用說明
├── README-TW.md                       # 繁體中文使用說明（本文件）
└── references/
    ├── page-templates.md              # 各類 Wiki 頁面的詳細模板
    ├── wiki-structure-schema.md       # Wiki 結構定義（JSON schema）
    └── file-filters.md               # 檔案過濾規則（包含/排除清單）
```

| 檔案 | 用途 | 何時載入 |
|------|------|---------|
| `SKILL.md` | 核心工作流程和指令 | Skill 觸發時 |
| `page-templates.md` | 各頁面類型的模板 | 生成頁面內容時 |
| `wiki-structure-schema.md` | 結構定義格式 | 規劃 wiki 結構時 |
| `file-filters.md` | 過濾規則 | 掃描檔案時 |

## 方法論

1. **掃描** — 遞迴讀取 repo 所有檔案，過濾噪音
2. **分類** — 依檔案類型（code/doc）和用途（impl/test）分類
3. **結構規劃** — 分析 file tree + README，決定 wiki 章節
4. **內容生成** — 逐頁讀取相關原始碼，生成帶圖表和引用的 Markdown
5. **輸出** — 寫入結構化的 wiki 資料夾
