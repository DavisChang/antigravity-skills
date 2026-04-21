# AI Workflow

這是一套用來提升 AI 協作效率的工作系統。核心目的不是把 AI 當成一次性問答工具，而是把 AI 帶進你的決策流程、知識整理流程與任務執行流程。

## 最快開始

如果只想先用起來，照這 3 步：

1. 打開 `PERSONAL_AI_OPERATING_MANUAL.md`，先填你的工作背景、主要輸出物、輸出格式偏好
2. 每次開新任務時，把 `AI_COLLABORATION_BRIEF.md` 貼給 AI，讓 AI 先理解你的協作方式
3. 遇到複雜問題時，用 `DECISION_CANVAS.md` 把問題拆成資料、邏輯、行動

## 建議使用順序

1. 先建立你的個人設定：`PERSONAL_AI_OPERATING_MANUAL.md`
2. 再定義 AI 的協作方式：`AI_COLLABORATION_BRIEF.md`
3. 遇到決策問題時使用：`DECISION_CANVAS.md`
4. 要重複執行某類任務時，建立一份 onboarding brief
5. 執行任務時從 `PROMPT_PLAYBOOK.md` 選 prompt
6. 完成後用 `CHECKLISTS.md` 檢查品質
7. 把下一步測試放進 `EXPERIMENT_BACKLOG.md`
8. 把真實案例沉澱到 `case_library/`

## 每個檔案的用途

| 檔案 | 用途 | 何時使用 |
| --- | --- | --- |
| `PERSONAL_AI_OPERATING_MANUAL.md` | 定義你和 AI 長期協作的方式 | 第一次建立系統時、每週回顧時 |
| `AI_COLLABORATION_BRIEF.md` | 讓 AI 快速理解你的角色、偏好與品質標準 | 每次開新任務或新對話時 |
| `DECISION_CANVAS.md` | 把複雜問題拆成資料、邏輯、行動 | 做決策、比較方案、設計流程時 |
| `PROMPT_PLAYBOOK.md` | 收錄可重複使用的高品質 prompt | 執行常見任務時 |
| `CHECKLISTS.md` | 檢查 AI 專案、AI 輸出、決策品質 | 任務完成前 |
| `EXPERIMENT_BACKLOG.md` | 把想法轉成下週可測的小實驗 | 規劃行動與驗證假設時 |
| `onboarding_briefs/` | 讓 AI 熟悉特定任務類型 | 任務會反覆出現時 |
| `templates/` | 可複製的文件模板 | 要產出 decision memo、experiment、role redesign 時 |
| `case_library/` | 保存真實案例與修正紀錄 | 任務完成後沉澱經驗時 |

## Personal AI Operating Manual

`PERSONAL_AI_OPERATING_MANUAL.md` 是這套系統的核心文件。它用來回答：

- 你是誰
- 你主要做什麼
- 你希望 AI 扮演什麼角色
- 你常見的任務類型是什麼
- 你偏好的輸出格式是什麼
- 你認為好的 AI 輸出應該長什麼樣

建議先填這三段：

1. 我的工作背景
2. 我的主要輸出物
3. 我的輸出格式偏好

填完後，可以在新對話開頭貼上這段：

```text
請先參考我的 Personal AI Operating Manual 與 AI Collaboration Brief。接下來請依照其中的協作原則、輸出偏好與品質標準協助我。
```

## 何時用哪個模板

- 要整理逐字稿：使用 `onboarding_briefs/transcript_knowledge_extraction.md`
- 要做重要決策：使用 `DECISION_CANVAS.md` 與 `templates/decision_memo_template.md`
- 要設計產品或流程：使用 `onboarding_briefs/product_workflow_design.md`
- 要把想法變成可測實驗：使用 `templates/experiment_template.md`
- 要重新設計角色與分工：使用 `templates/role_redesign_template.md`
- 要檢查輸出品質：使用 `CHECKLISTS.md`

## 資料夾結構

```text
AI_Workflow/
├── README.md
├── AI_COLLABORATION_BRIEF.md
├── DECISION_CANVAS.md
├── PROMPT_PLAYBOOK.md
├── CHECKLISTS.md
├── EXPERIMENT_BACKLOG.md
├── PERSONAL_AI_OPERATING_MANUAL.md
├── onboarding_briefs/
│   ├── transcript_knowledge_extraction.md
│   ├── decision_analysis.md
│   └── product_workflow_design.md
├── templates/
│   ├── ai_onboarding_brief_template.md
│   ├── decision_memo_template.md
│   ├── experiment_template.md
│   └── role_redesign_template.md
└── case_library/
    └── case_template.md
```

## 核心原則

- 先補上下文，再要求高品質輸出
- 先增強人的能力，再考慮自動化
- 先把決策拆成資料、邏輯、行動
- 先讓 AI 做整理、分流、建議，再授權執行
- 所有重要輸出都要有依據、風險、反例與下一步

## 每週維護節奏

每週花 15 分鐘更新這套系統：

1. 把本週好用的 prompt 補進 `PROMPT_PLAYBOOK.md`
2. 把失敗或需要大量修正的案例放進 `case_library/`
3. 把重複出現的任務整理成新的 onboarding brief
4. 把下週要測的 AI 協作方式放進 `EXPERIMENT_BACKLOG.md`
5. 更新 `PERSONAL_AI_OPERATING_MANUAL.md` 中的偏好與品質標準
