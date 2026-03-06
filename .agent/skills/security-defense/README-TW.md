# 資安防禦技能（Security Defense Skill）

> **版本**：2.0.0 | **Language**: [English](README.md)

一套 AI Agent 技能，用於執行端點安全檢測、滲透測試、防禦分析，以及 EU CRA 產品合規評估。專為 Cursor IDE 設計——當使用者要求安全檢測或 CRA 合規時，AI Agent 會自動啟用此技能。

## 功能概述

兩大核心能力，各有結構化的可重複流程：

### 1. 端點安全檢測

針對上線服務做系統性測試——後端 API、前端網頁、IP/Port 服務、基礎設施。

| 檢測領域 | 重點項目 |
|----------|---------|
| **前端** | XSS、CSRF、CORS、CSP、token 儲存、source map 洩漏 |
| **後端 / API** | SQLi、SSRF、IDOR、輸入驗證、rate limiting、錯誤訊息洩漏 |
| **身份驗證** | BOLA/BFLA、JWT 安全、session 管理、MFA、帳號枚舉 |
| **基礎設施** | 暴露的服務、預設帳密、防火牆規則、密鑰管理 |
| **業務邏輯** | 重放攻擊、步驟跳過、權限提升、webhook 偽造 |
| **銀行業** | 8 條攻擊主線：帳號接管、邊界利用、DDoS、API 濫用、勒索、供應鏈、支付、資料外洩 |

### 2. EU CRA 產品合規

依據歐盟網路韌性法案（EU 2024/2847），對出口歐盟的產品做分類與符合性評估路徑規劃。

| 產品線 | CRA 類別 | 評估路徑 |
|--------|----------|---------|
| **防火牆 / IDS / IPS** | Important Class II | Module B+C 或 H（需 notified body） |
| **路由器 / 交換機 / 數據機** | Important Class I | 有 harmonised standard 可走 Module A；否則 B+C/H |
| **IoT（智慧家庭 / 穿戴）** | 逐 SKU 判定 | 依核心功能是否落入 Annex III/IV 決定 |

## 運作方式

### 端點測試流程

```
Phase 0        Phase 1         Phase 2-5        Phase 6          Phase 7
範圍確認  ──▶  偵察與      ──▶  前端 / API / ──▶  業務邏輯    ──▶  風險報告
(先問清楚)     暴露面分析       認證 / 基礎      與監控驗證       與改善方案
                                設施測試
```

### CRA 合規流程

```
步驟 1          步驟 2            步驟 3           步驟 4
分類每個   ──▶  選擇評估     ──▶  建立證據     ──▶  在期限前
SKU             路徑              文件包           完成合規
                                                  (2026/2027)
```

## 目錄結構

```
security-defense/
├── SKILL.md                                    # AI Agent 核心指令
├── README.md                                   # 英文說明
├── README-TW.md                                # 本檔案（繁體中文）
└── references/
    ├── scope-template.md                       # 資產盤點與範圍定義模板
    ├── frontend-checklist.md                   # 前端安全檢查清單
    ├── backend-api-checklist.md                # 後端/API 安全檢查清單
    ├── auth-checklist.md                       # 身份驗證與授權檢查清單
    ├── infra-checklist.md                      # 主機/IP/Port/服務安全檢查清單
    ├── banking-defense-matrix.md               # 銀行業攻擊—防禦矩陣
    ├── report-template.md                      # 漏洞報告模板
    ├── cra-product-compliance.md               # CRA 產品線分級治理指南
    ├── cra-classification-guide.md             # SKU 分類工作坊（5 題判定法）
    └── cra-timeline-obligations.md             # CRA 時程與義務完整對照
```

## 快速開始

### 觸發 — 端點安全檢測

在 Cursor 中向 AI Agent 提出要求即可：

```
「幫我檢測這個 API 的安全性」
「掃描一下這些 IP/Port 有什麼問題」
「對我的服務做滲透測試」
「幫我做暴露面分析」
"Help me do a penetration test on my service"
```

**重要：** Agent 會先詢問範圍問題（目標、帳號、技術棧、測試邊界），資訊不足時會主動提問，不會直接開始掃描。

### 觸發 — CRA 合規

```
「我的產品需要做 CRA 合規嗎？」
「幫我做 CRA 產品分類」
「CE 認證需要準備什麼？」
「幫我評估產品的漏洞通報義務」
"Help me classify my products under CRA"
```

### 測試強度等級

| 等級 | 範圍 | 風險 |
|------|------|------|
| **L1** | 被動偵察、設定檢查、低風險驗證 | 極低 |
| **L2** | 標準滲透測試：認證/授權/輸入驗證 | 低 |
| **L3** | 高風險驗證：SSRF、反序列化、RCE、提權 | 中 |

## CRA 關鍵日期

| 日期 | 事件 | 狀態 |
|------|------|------|
| 2024-12-11 | CRA 生效 | 已完成 |
| **2026-06-11** | Notified body 規定開始適用 | 即將到來 |
| **2026-09-11** | **漏洞與安全事件通報義務強制** | 即將到來 |
| **2027-12-11** | **CRA 全面強制 + CE Mark 要求** | 即將到來 |

## 風險分級

### 端點測試 — 發現記錄格式

| 編號 | 類型 | 位置 | 影響 | 可利用性 | 風險 |
|------|------|------|------|----------|------|
| V-01 | IDOR | /api/users/{id} | 可讀他人資料 | 高 | 高 |
| V-02 | CORS | api.example.com | token 誤用 | 中 | 中 |

### 最常出事的 Top 10

1. IDOR / 權限控管錯誤
2. 管理端或 debug 端點外露
3. 檔案上傳繞過
4. 密碼重設 / 驗證碼流程缺陷
5. Webhook / callback 缺驗簽
6. CORS / token 儲存方式錯誤
7. Redis / DB / metrics 直接外露
8. 前端 bundle / repo 洩漏 secrets
9. 錯誤訊息過度詳細
10. 業務邏輯可被重放或跳步

## 工具生態系

| 類別 | 工具 |
|------|------|
| 子網域列舉 | `subfinder`, `amass`, `httpx` |
| Port 掃描 | `nmap`, `masscan`, `rustscan` |
| Web 掃描 | `nuclei`, `nikto`, `OWASP ZAP` |
| API 測試 | `Burp Suite`, `Postman`, `ffuf` |
| 密鑰掃描 | `gitleaks`, `trufflehog` |
| TLS 測試 | `testssl.sh`, `sslyze` |
| 靜態分析 | `semgrep`, `bandit`, `gosec` |
| 動態掃描 | `OWASP ZAP`, `Burp Suite` |
| 基礎設施 | `trivy`, `grype`, `lynis` |
| SBOM 產生 | `syft`, `trivy`, `cdxgen` |
| SBOM 漏洞比對 | `grype`, `trivy` |
| 韌體分析 | `binwalk`, `firmwalker` |

## 參考標準

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/API-Security/)
- [EU CRA 官方法規文本 (EU 2024/2847)](https://eur-lex.europa.eu/eli/reg/2024/2847/oj)
- [NIST Cybersecurity Framework 2.0](https://www.nist.gov/cyberframework)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)

## 版本歷史

| 版本 | 日期 | 重點 |
|------|------|------|
| v2.0.0 | 2026-03-06 | 新增 EU CRA 產品合規模組（3 個 reference 檔案）|
| v1.0.0 | 2026-03-06 | 首次發布：端點檢測 + 銀行業防禦矩陣 |

## 與 security-audit 技能的差異

| 面向 | security-audit | security-defense |
|------|---------------|-----------------|
| **聚焦** | **原始碼**審核 | **上線服務**測試 + **產品合規** |
| **輸入** | 程式碼庫 / Repository | 網域、IP、Port、API、產品 SKU |
| **方法** | 靜態分析（SAST）、程式碼審查 | 動態測試（DAST）、滲透測試、掃描 |
| **產出** | 程式碼層級的弱點報告 | 服務層級 + CRA 合規報告 |
| **平台** | 前端、後端、Electron、容器、AI | 前端、後端、API、基礎設施、銀行業、CRA |
| **觸發語** | 「幫我做程式碼資安檢查」 | 「幫我測試 API / 檢查產品 CRA 合規」 |

**最佳實踐：** 兩個技能搭配使用——`security-audit` 做程式碼審查，`security-defense` 做上線測試和 CRA 合規。

## 授權

專案內部工具，隨程式碼庫一同分發。
