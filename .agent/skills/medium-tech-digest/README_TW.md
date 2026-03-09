# Medium 技術文摘

一個 Agent 技能，用於自動抓取、摘要並發送每週 Medium 最優質的技術文章。

---

## 概觀

`medium-tech-digest` 將 Antigravity Agent 轉化為你的個人技術策展人。它會掃描 Medium 上過去 7 天發布的高品質技術文章，自動生成繁體中文與英文雙語摘要，將報告存檔於本機，並支援透過電子郵件發送。

---

## 功能特色

| 功能 | 說明 |
|:---|:---|
| **5 大策展分類** | 核心 AI 與 LLM・開發 + AI 整合・新函式庫與工具・系統架構・跨領域 AI |
| **全文摘要** | 讀取文章完整內容（而非搜尋摘錄），確保摘要準確且有深度 |
| **雙語報告** | 每份摘要同時包含繁體中文版與英文版 |
| **自動存檔** | 報告儲存至 `medium_digest_output/medium_digest_<YYYY-MM-DD>/digest.md` |
| **郵件發送** | 支援透過可自訂的 Python 腳本以 SMTP 方式寄出報告 |

---

## 目錄結構

```
medium-tech-digest/
├── SKILL.md                     # Agent 核心指令與工作流程邏輯
├── README.md                    # 英文說明文件
├── README_TW.md                 # 本文件（繁體中文）
└── scripts/
    └── send_email_template.py   # 郵件發送參考腳本
```

---

## 使用方式

直接向 Antigravity Agent 發出指令：

```
Run the Medium tech digest for this week.
Give me a summary of recent AI news from Medium.
Collect top Medium articles and email them to me.
幫我收集最近一週 Medium 上的技術文章並寄信給我。
幫我整理本週 Medium 的 AI 技術文章。
```

---

## 工作流程

```
搜尋 Medium（5 大分類）
    ↓
篩選：每分類選出最佳 3 篇（依新鮮度 + 品質 + 深度）
    ↓
摘要：核心概念・核心洞見・實際應用
    ↓
彙整：雙語 Markdown 報告（繁體中文 → 英文）
    ↓
存檔：medium_digest_output/medium_digest_<YYYY-MM-DD>/digest.md
    ↓
【選用】透過 send_email_template.py 發送郵件
```

---

## 文章分類

| 分類 | 主要關鍵字 |
|:---|:---|
| 核心 AI 與 LLM | LLM、GPT、Claude、Gemini、Transformer、RAG、GenAI、Fine-tuning |
| 開發 + AI 整合 | LangChain、LlamaIndex、Vercel AI SDK、MCP、AI Agent、React AI |
| 新函式庫與工具 | 開源新發布、npm/PyPI 套件、SDK、CLI 工具 |
| 架構與系統 | 系統設計、微服務、擴展性、可觀測性、基礎設施 |
| 跨領域 AI | AI × 生物醫學、AI × 金融、AI × 藝術、AI × 音樂、AI × 醫療、AI × 科學 |

---

## 輸出格式

每篇文章的摘要遵循以下結構：

```markdown
### [文章標題](URL)
> *作者 · 出版物 · 日期*

**核心概念**：一句話說明主要想法或技術。

**核心洞見**：為何重要——突破性進展、效率提升或全新能力。

**實際應用**：開發者或團隊今天就能如何運用。
```

報告儲存路徑：

```
medium_digest_output/
└── medium_digest_2026-03-09/
    └── digest.md
```

---

## 郵件發送設定

使用郵件功能前，請先設定以下環境變數：

```bash
export EMAIL_USER="you@gmail.com"
export EMAIL_PASS="your-app-password"    # Gmail 應用程式密碼，非帳號密碼
export EMAIL_RECIPIENT="recipient@example.com"
```

接著告訴 Agent：

```
把摘要寄給我。
Send the digest to my email.
```

Agent 會參考 `scripts/send_email_template.py` 產生並執行自訂的發送腳本。

> **注意**：使用 Gmail 時，必須使用[應用程式密碼](https://support.google.com/accounts/answer/185833)，而非一般帳號密碼。

---

## 客製化

你可以直接修改 `SKILL.md` 來調整以下設定：

- **搜尋時間範圍**：將 `when:7d` 改為 `when:30d` 以取得每月摘要。
- **每分類文章數**：預設為 3 篇，可依需求增減。
- **優先出版物**：新增信任的 Medium 出版物，以確保文章品質。
- **語言偏好**：調換語言順序，或新增其他語言版本。
