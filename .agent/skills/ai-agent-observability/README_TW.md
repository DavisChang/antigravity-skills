# AI Agent 可觀測性與評估 — Cursor Agent Skill

> 讓你和 AI 一起開發**可觀測、可評估、可持續迭代改善**的 AI Agent 系統。

[English version: README.md](README.md)

---

## 為什麼需要這個 Skill

AI Agent 跟傳統軟體有根本性差異：

| 傳統軟體 | AI Agent |
|----------|----------|
| 決定性：同樣輸入 → 同樣輸出 | **非決定性**：同樣輸入 → 每次可能不同 |
| 受限輸入（表單、API） | **不受限輸入**（自然語言，什麼都可能） |
| 用 stack trace 除錯 | **用執行 trace 除錯**（程式碼無法預測行為） |
| 測程式路徑 | **測推理品質與上下文處理** |
| Code review 找 bug | **上線後才會被用戶輸入揭露 bug** |

量產 Agent 最關鍵的兩件事：**可觀測性（Observability）** 與 **評估（Evaluation）**，而且它們綁在一起。

---

## 這個 Skill 涵蓋什麼

### 1. 核心思維模型

```
程式碼定義 prompt + 工具 → Agent 產生行為分佈
Trace 捕捉實際發生的事 → Eval 衡量推理品質
線上失敗 → 轉成離線測試案例 → 形成迭代閉環
```

**關鍵觀念**：你在管理「行為分佈」，不是管理確定性的程式路徑。

### 2. 觀測三原語

| 原語 | 範圍 | 回答什麼問題 |
|------|------|-------------|
| **Run**（單次 LLM 呼叫） | 一個決策點 | 「這次決策合理嗎？」 |
| **Trace**（一次任務執行） | 多個 Run 串成的軌跡 | 「這個任務完成了嗎？有效率嗎？」 |
| **Thread**（多輪對話） | 多個 Trace 跨輪串接 | 「Agent 跨輪次是否一致？有沒有忘記？」 |

### 3. 每次 LLM 呼叫必須記錄什麼

- **輸入上下文**：system prompt、messages、tool definitions、retrieval context
- **輸出**：模型回覆、tool calls（名稱、參數、回傳值、錯誤）
- **元資料**：tokens、latency、cost、decision_context
- **除錯快照**：`prompt_preview`（前 500 字）、`response_preview`（前 500 字）

### 4. 三層評估策略

| 層級 | 速度 | 真實度 | 適用場景 |
|------|------|--------|---------|
| **Run 層**（決策單元測試） | 快（CI 可跑） | 低 | 保護關鍵決策點（工具選擇、查詢生成） |
| **Trace 層**（端到端測試） | 中 | 中 | 驗證完整任務，含 must-happen / must-not-happen 條件 |
| **Thread 層**（多輪一致性） | 慢 | 高 | 測記憶保留、跨輪一致性 |

### 5. 線上評估：沒有標準答案也能做

線上通常拿不到 ground truth。改用：
- **效率指標**：latency、token 用量、tool 呼叫次數、成本
- **失敗訊號**：loop 偵測、tool 錯誤率、超時率、格式違規率
- **用戶行為**：重問率、放棄率、轉接率

跟 baseline 比，偏離就是異常。

### 6. 迭代閉環

```
線上失敗 → 找 trace → 定位失敗步驟 → 擷取狀態
  → 匿名化 → 建立離線測試案例 → 修復 → 驗證 → 加入 CI
  → 每週重複
```

這就是從「demo 可以跑」到「production 可以用」的路。

---

## 檔案結構

```
ai-agent-observability/
├── SKILL.md          # 主要 Agent 指令（Cursor 讀取的核心文件）
├── checklist.md      # 完整自我評估清單（40+ 項目）
├── playbook.md       # 詳細評估策略與程式碼範例
├── README.md         # 英文版說明
└── README_TW.md      # 本檔案（中文版說明）
```

### Cursor 如何使用這個 Skill

當你在開發 AI Agent 相關程式碼，詢問 Cursor：
- 加入 observability / tracing
- 設計評估策略
- 除錯非決定性行為
- 準備 Agent 上線（從 demo 到可靠）
- 加入護欄或安全機制

Cursor 會自動讀取 `SKILL.md`，依照其中的模式、清單和策略來協助你。

---

## 快速上手：先做 5 件事

1. **定義 3 個禁止行為**，加上執行機制（審核閘門、硬阻擋）
2. **設護欄**：`max_steps=15`、`max_tool_calls=30`、`timeout=120s`
3. **記錄每次 LLM 呼叫**，含完整上下文（prompt、messages、tools、response、tokens、latency）
4. **上 2 個線上 evaluator**：loop 偵測 + tool 錯誤率
5. **跑基準測試**：核心任務跑 20 次，量測成功率與成本分佈

---

## 觀測系統自我評估（簡版）

完整版見 [checklist.md](checklist.md)

### P0 必做
- [ ] 3+ 個禁止行為各有防線
- [ ] max_steps / max_tool_calls / timeout 已設定
- [ ] 每次 LLM 呼叫都有完整 Run 記錄
- [ ] Tool 呼叫有記錄（參數、回傳、錯誤、延遲）
- [ ] Trace 可回放、有 trace_id
- [ ] Thread_id 串起多輪對話

### P1 應做
- [ ] 錯誤有結構化記錄（step, error_code, severity）
- [ ] 至少 1 組 run-level eval（auto pass/fail）
- [ ] 至少 1 組 trace-level eval（端到端，含 must-not-happen）
- [ ] 至少 2 個線上 evaluator 在跑

### P2 持續改善
- [ ] Production trace → 離線測例 的轉換流程
- [ ] 每週 Top 3 failure modes 回顧
- [ ] 非決定性基準：核心任務跑 N 次有成功率分佈

---

## 十大金句

1. 量產 Agent 最關鍵的兩件事：可觀測性與評估，而且它們綁在一起。
2. Agent 系統不是「看 code 就知道會怎樣」，真相在 trace。
3. 你不會在用戶上線前真正知道 Agent 會做什麼。
4. Agent 的輸入是自然語言，天生不受限；再加上非決定性，風險倍增。
5. 除錯要鑽進每一次 LLM 呼叫的上下文，而不是找 stack trace。
6. Run、Trace、Thread 是理解與治理 Agent 行為的三個層級。
7. 評估 Agent 是在測推理與上下文，不是在測程式分支。
8. 端到端測試更真實，但指標更難定義；單步測試快但易過期。
9. Production traces 會變成你的評估資料集來源。
10. 線上沒有 ground truth 也能做評估：用軌跡與效率指標抓異常。

---

## 一頁式 Playbook（可直接照做）

詳細版見 [playbook.md](playbook.md)

### 流程

```
1. 定義風險護欄
   → 哪些動作必須審核/二次確認
   → max_steps / max_tool_calls / timeout

2. 上 trace
   → 以 Run 為單位記錄完整上下文與輸出
   → 串成 Trace → 以 Thread 串多輪

3. 先做 2 種 eval
   → 離線：20-50 條關鍵單步回歸（工具選擇/查詢生成/總結）
   → 線上：loop 偵測 + tool 錯誤率（不需 ground truth）

4. 把線上失敗變測例
   → 用戶回報或指標異常 → 找 trace → 擷取狀態
   → 匿名化 → 加入離線回歸集

5. 每週節奏
   → 回顧 Top 3 failure modes
   → 修 prompt / tool 介面
   → 重新跑離線基準
   → 更新門檻
```

### 你怎麼知道變好了？

| 指標 | 說明 |
|------|------|
| 成功率 | 核心任務的通過率 |
| 平均步數 | 越少越好（效率） |
| loop_rate | 迴圈發生率（<1% 為佳） |
| tool_error_rate | 工具錯誤率（<3% 為佳） |
| 平均延遲 | 回應時間 |
| 平均成本 | 每次任務的 token/美元成本 |
| 重問率 | 用戶需要重複問同一件事的比率（thread 層） |
| 記憶命中率 | Agent 正確記住跨輪上下文的比率 |

---

## 下一步實驗清單

| # | 實驗 | 效益 | 成本 | 成功判準 |
|---|------|------|------|---------|
| 1 | 高風險動作加二次確認 + 護欄 | 高 | 中 | 成本下降，零新增誤動作 |
| 2 | Loop 偵測 (同 tool+同參數 ≥3 次) + 告警 | 高 | 低 | 抓到 ≥1 已知迴圈，誤報 <20% |
| 3 | 核心任務跑 20 次，產出成功率/步數分佈 | 高 | 低 | 找到前 2 大失敗類型可復現 |
| 4 | 工具選擇單步回歸集 30 條 | 高 | 中 | ≥90% 選對工具 |
| 5 | 把 1 個線上 bug trace 轉成離線測例納入 CI | 高 | 中 | 修前 fail、修後 pass |
| 6 | Thread 回放最小版 | 中 | 中 | 能定位到「第一個偏離點」 |
| 7 | 線上 evaluator 週報 (tool error + timeout) | 中 | 低 | 一週找出 ≥2 可改善 failure mode |
| 8 | 端到端最小驗收條件 3 條 + 5 條 trace eval | 中 | 中 | 每條自動判 pass/fail |

---

## 適用範圍

- **框架**：LangGraph、LangChain、CrewAI、AutoGen、自建 Agent
- **工具**：Langfuse、LangSmith、Phoenix、或自建 trace 實作
- **語言**：Python 為主，概念適用於任何語言
