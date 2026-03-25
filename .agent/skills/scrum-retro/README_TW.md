# scrum-retro Skill（中文說明）

將 Scrum Retro 的**原始筆記／便利貼**整理成**結構化 Improvement Log**：主題歸類、可執行實驗、負責人、衡量指標，以及固定議程流程。

## 涵蓋範圍

- **主題歸類** — 將觀察對應到五個預設主題（需求／規格清晰度、交付規劃、依賴管理、品質流程、協作節奏），必要時可新增主題  
- **每次 1–2 個實驗** — 依優先順則篩選，避免一次想解太多問題  
- **行動品質** — 把空泛口號改寫成可追蹤、可驗證的實驗敘述  
- **Improvement Log** — 表格欄位與範例列，可放 Notion、Confluence、試算表或 Jira  
- **依主題的指標** — 領先／落後指標建議，方便實際統計  
- **上個 Sprint 檢視** — 對既有行動做 Keep / Adjust / Standardize / Drop  

## 檔案結構

```
.agent/skills/scrum-retro/
├── SKILL.md                              # 入口 — 工作流程與輸出格式
├── README.md                             # 英文說明
├── README_TW.md                          # 本文件（繁體中文）
└── references/
    ├── improvement-log-template.md       # Log 表格欄位與範例
    └── metrics-reference.md              # 各主題指標參考
```

## 如何使用

在對話中提及 retro／整理 retro，或直接描述需求：

> 「這次 retro 的便利貼如下，請歸類主題並選兩個 action，附上 metric。」  
> 「先 review 上個 sprint 兩個改善項，再處理這次新的觀察。」  
> 「幫 dependency 主題產出一筆 Improvement Log 列。」

## 設計原則

1. **改善模式，不是每張便利貼** — 聚焦重複出現的主題。  
2. **實驗，不是口號** — 每個行動都要可執行、可衡量。  
3. **先追上次** — 下次 Retro 開場先檢視上次 action，避免只剩抱怨。  
4. **算正式工** — 改善要佔容量（例如 5–10%）、進 backlog、有 owner。
