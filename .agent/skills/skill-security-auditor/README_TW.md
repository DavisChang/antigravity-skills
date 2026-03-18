# Skill 安全審核工具

針對 AI Agent Skill 的靜態安全審查工具——支援任何格式、任何生態系。在安裝或執行前，偵測 Prompt Injection、惡意程式投放、機密外洩、供應鏈攻擊與權限提升。

## 為什麼需要這個工具

AI 技能市集已成為新一代的供應鏈攻擊面。過去在 npm、PyPI、VS Code 外掛和瀏覽器擴充套件上看到的攻擊模式——名稱搶註（typosquatting）、社交工程、木馬化功能、憑證竊取——現在都瞄準了 AI Agent 生態系。一旦 Agent 安裝的 Skill 遭植入惡意程式，攻擊者可以存取 Agent 連接的所有服務：Email、訊息、行事曆、文件、金融資料和各種 Secrets。

本 Skill 提供第一層靜態分析與威脅偵測，適用於任何格式的 Agent Skill。

## 偵測項目

| 風險類別 | 說明 |
|:---|:---|
| Prompt Injection | 不受信任的輸入被當作指令執行；Email/網頁內容驅動自動化操作 |
| 惡意程式投放 | `curl\|bash`、混淆腳本、編碼 payload、持久化機制 |
| 多階段 Payload | Base64 解碼鏈、Paste 站台載入器、分階段下載、無法確認的最終 Payload |
| 木馬化邏輯 | 惡意呼叫藏在正常運作的功能中；Reverse Shell 埋在業務邏輯裡 |
| Reverse Shell / C2 | 對外連線至裸 IP:port、Socket 重導向、`nc -e`、隱藏的 `os.system(curl)` |
| 機密竊取 | 存取 `.ssh`、`.env`、Cookie、錢包、Keychain、Agent 設定檔並上傳至遠端 |
| 壓縮檔規避 | 帶密碼的 ZIP/RAR/7z 內含執行檔；密碼寫在說明中 |
| 前置工具陷阱 | 「先安裝這個工具」導向非官方來源的二進位檔下載或惡意程式 |
| 過度授權 | 不必要的環境變數、過寬的檔案系統/網路存取、未限制範圍的 MCP 工具 |
| 權限提升 | 沙箱繞過、權限拉高、安全護欄覆寫 |
| 供應鏈攻擊 | 名稱搶註、未驗證的下載、縮短網址、缺少校驗值 |
| 高價值目標鎖定 | 加密貨幣/錢包/交易、YouTube、Google Workspace、社群媒體、金融、PDF 工具 |

## 支援的 Skill 格式

| 格式 | 典型位置 | 主要檔案 |
|:---|:---|:---|
| AgentSkills / Antigravity | `.agent/skills/<name>/` | `SKILL.md`、腳本、設定檔 |
| Cursor Skills | `.cursor/skills/<name>/` | `SKILL.md` |
| Cursor Rules | `.cursor/rules/` | `*.mdc`、`RULE.md` |
| Codex Skills | `.codex/skills/<name>/` | `SKILL.md` |
| Gemini Skills | `.gemini/skills/<name>/` | `SKILL.md` |
| Google AGENTS.md | Repo 根目錄或子目錄 | `AGENTS.md` |
| MCP Server 設定 | `.cursor/mcp.json` 等 | JSON 設定檔 |
| 自定義 / 其他 | 任意路徑 | 任何指令檔 |

## 如何使用

請 AI Agent 審查 Skill：

```
審核這個 skill 的安全性
檢查這個 skill 安不安全
掃描 .agent/skills/some-skill/ 有沒有安全風險
Audit this skill for security issues.
```

## 審核流程

審核工具對每個 Skill 執行 9 步驟完整流程：

| 步驟 | 動作 |
|------|------|
| 1 | 辨識 Skill 格式，定位所有關聯檔案 |
| 2 | 盤點所有檔案、可執行內容、URL 與下載項目 |
| 3 | 審查 Frontmatter / Metadata 是否有誤導性描述或隱藏功能 |
| 4 | 審查指令內容是否有信任邊界違規、Prompt Injection、機密暴露 |
| 5 | 審查程式碼與腳本，偵測木馬化邏輯、多階段 Payload、Reverse Shell、混淆 |
| 6 | 審查權限需求是否超出文件描述的目的 |
| 7 | 審查供應鏈相依性、前置工具、壓縮檔、名稱搶註 |
| 8 | 分析完整的 Payload 投放鏈（入口 → 各階段 → 最終 Payload → 平台分支） |
| 9 | 給出判定結果：`PASS`、`WARN`、`FAIL` 或 `NEEDS_MANUAL_REVIEW` |

## 判定等級

| 判定 | 意義 |
|------|------|
| `PASS` | 未發現顯著安全疑慮 |
| `WARN` | 可疑或過度授權，但未確認惡意行為 |
| `FAIL` | 確認存在破壞性、資料外洩或類似惡意軟體的行為 |
| `NEEDS_MANUAL_REVIEW` | 證據不足以判定，需人工審查 |

## 立即判定失敗的條件

審核工具在確認以下情況時立即回傳 `FAIL`：

- 瀏覽器 Cookie / 加密貨幣錢包 / SSH 金鑰竊取
- 機密資料外洩至遠端目的地
- 隱藏的遠端執行 Payload 或 Reverse Shell
- 多階段 Payload 鏈中最終 Payload 無法被靜態驗證
- 帶密碼的壓縮檔內含執行檔
- 前置工具安裝導向非官方來源
- 功能性程式碼中隱藏對遠端 URL 的 Shell 執行呼叫
- Agent 設定檔外洩（`.env`、憑證被傳送至外部）

## 檔案結構

```
.agent/skills/skill-security-auditor/
├── SKILL.md        # Skill 定義（由 AI Agent 載入）
├── README.md       # 英文說明
└── README_TW.md    # 本檔案——繁體中文說明
```

## 設計原則

1. **預設不信任** — 所有第三方 Skill 在證明安全之前一律視為不受信任
2. **僅靜態分析** — 審查過程中絕不執行不受信任的腳本、指令或 Payload
3. **寧可誤報，不可漏報** — 寧願標記安全的 Skill，也不漏掉惡意的
4. **完整鏈追蹤** — 追蹤每一次下載、解碼和階段轉換，確認最終 Payload
5. **外觀不代表信任** — 專業的 README 和正常運作的功能不會降低風險評估
6. **爆炸半徑意識** — 在 Agent 所連接的所有服務上下文中評估影響範圍
