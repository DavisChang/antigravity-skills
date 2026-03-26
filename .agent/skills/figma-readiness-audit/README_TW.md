# Figma 設計一致性審查

**在 Handoff 之前，而不是之後，幫助設計師理解自己的 Figma 決策如何影響程式碼。**

---

## 這個工具解決什麼問題

設計師交出 Figma 檔案，三個平台團隊（Web、Flutter、Windows）各自開始建置。每個團隊都在獨立猜測：

- 「`#2D6BE4` 是 primary color 還是隨便選的？」
- 「沒有 hover 狀態——要自己編一個嗎？」
- 「這個圖層叫 `Frame 47`——它是什麼？」

結果：三個平台交出三種不同的詮釋。設計師不知道這件事會發生。

## 這個 SKILL 做什麼

它透過 Figma MCP 工具對設計稿進行結構化分析，產出一份**設計師看得懂的報告**：

1. **用數據呈現問題** — 「你有 75% 的顏色是 raw hex，不是 Variables」
2. **用設計師語言解釋** — 不用程式術語，說明這個 Figma 決策對程式碼的影響
3. **提供 Figma 操作步驟** — 點哪裡、選什麼、怎麼修
4. **為每個平台評級** — Web 可達 Level A，Flutter Level B，Windows Level C
5. **為每個元素分類** — 用 DS 決策樹告訴你每個元件應該放在哪一層

---

## 誰應該使用

| 角色 | 使用時機 |
|------|----------|
| **設計師** | Handoff 前：「我的設計稿夠清楚嗎？」 |
| **工程師** | 實作前：「可以開始了嗎？還是要等設計師修正？」 |
| **PM** | Sprint 規劃：「設計和工程在這個功能上對齊了嗎？」 |

---

## 工作流程

```
Figma URL
    |
    v
+---------------------------+
| 階段 1：MCP 資料收集       |  get_screenshot、get_metadata、
|  （四個步驟）              |  get_design_context、get_variable_defs、
|                           |  use_figma（程式化查詢）、
|                           |  Figma Make context（選用）
+---------------------------+
    |
    v
+---------------------------+
| 階段 2：三層分析            |
|                           |
|  Tier 0：DS 層級 +         |
|    決策樹元素分解           |
|  Tier 1：設計系統品質       |
|   （11 個維度）             |
|  Tier 2：平台可程式化       |
|   （Level A / B / C）      |
+---------------------------+
    |
    v
+---------------------------+
| 階段 3：產出報告            |
|  - DS 組成分析表            |
|  - 設計師行動清單           |
|  - 每個問題的數據佐證       |
|  - Figma 修法步驟          |
|  - 工程師備忘               |
+---------------------------+
```

---

## 平台等級說明（設計師語言）

| 等級 | 代表什麼 |
|------|----------|
| **Level A** | 「你的設計稿非常清楚，我幾乎不需要猜，可以直接生出能用的 UI。」 |
| **Level B** | 「我可以生出骨架——版面、元件、間距——但細節要自己補。」 |
| **Level C** | 「我可以產出規格文件——尺寸、顏色、狀態——但工程師要手寫 UI 程式碼。」 |

各平台的典型目標：

- **Web** → Level A（完整生成）
- **Flutter** → Level B（骨架生成）
- **Windows** → Level C（規格生成）

---

## 設計系統層級定位 + 決策樹

審查會先判斷你的設計稿在設計系統架構中屬於哪一層（第 1–7 層），然後**對每個子元素**跑決策樹。不同層的審查重點不同，決策樹結果會產出「DS 組成分析表」。

| 層級 | 內容 | 審查重點 |
|------|------|----------|
| 1 Tokens | 色彩、間距、字級規則 | Variable 命名、語意 vs. 原始值 |
| 2 Primitives | Box、Stack、Text | 結構單純性 |
| 3 Components | Button、Input、Modal | Variants、States、Code Connect |
| 4 Patterns | 篩選面板、表單配置 | 任務完整度 |
| 5 Templates | Dashboard、List-detail | 頁面骨架、內容區標示 |
| 6 Product Modules | 業務專屬模組 | 規格完整度（降低 DS 門檻）|
| 7 Experiment | 探索稿 | 先用 Figma Make 驗證，再審查 |

### 決策樹（逐元素判斷）

對設計中每個可識別的 UI 元素，按順序問：

1. **是全域視覺規則嗎？** → Foundations / Tokens
2. **是單一互動元件嗎？**
   - 可跨產品重用、不依賴業務邏輯 → Core Component
   - 產品專屬 → Product Component
3. **是在解一個完整任務或流程嗎？**
   - 可跨產品複用 → Pattern
   - 只服務單一產品 → Product Module
4. **是頁面骨架嗎？** → Template
5. **還在探索中嗎？** → Experiment / Local

補充判斷：是否有產品專屬語意？是否已在 2+ 情境驗證？能否抽象命名？工程是否願意維護？

報告會產出一張元素對照表，列出每個元件是什麼、DS 裡有沒有、建議動作（使用現有 / 擴充 / 新建 / 留在產品層）。

### 為什麼重要

當設計用原始矩形 + 文字拼出一個「按鈕」，工程師就得自己發明元件邊界、猜 hover/disabled 行為、手寫每個 variant 的樣式。乘以三個平台，結果就是三端不一致。決策樹幫助設計師在 handoff **之前**就想清楚元件組成。

---

## 報告範例（問題卡片）

```markdown
### 🔴 D2-001 顏色沒有綁定 Variables

**這代表什麼？**
你的設計裡有些顏色是直接填 `#2D6BE4`，而不是選 Variables 面板裡的
`color/primary`。對工程師來說，每個平台的工程師都必須各自「猜」這個顏色
對應哪個設計 Token——Web 可能猜對，Flutter 可能猜錯，Windows 又不同。
結果：三個平台用的顏色可能對不起來，而你不知道。

**數據佐證（MCP 擷取）**
- use_figma 統計：63 個顏色填充中，47 個（75%）是 raw hex，16 個（25%）有綁 Variable
- get_variable_defs：Variables 面板中 `color/primary = #2D6BE4` 已定義，
  但有 12 個節點直接用了 `#2D6BE4` 而未綁定
- 影響元件：Button/Primary (2:45)、Card/Header (3:12)、Tag/Active (4:89)

**在 Figma 怎麼修**
1. 左側圖層面板選取 `Button/Primary`
2. 右側 Fill → 點色塊 → 右上角切換成「Variables」模式
3. 選擇 `color/primary` → 確認
4. 對所有影響節點重複，或使用 Figma 外掛「Variable Swapper」批次替換
```

---

## Figma Make 支援

如果 URL 是 Figma Make 檔案（`figma.com/make/...`），審查會額外擷取互動描述——元件用途、section 語意、使用者操作流程。這些資訊用來：

- 補充 **D4（非視覺模式）** 的互動意圖說明
- 引導設計師從探索稿收斂為正式交付稿
- 確保修正不偏離原始的互動設計

對於**第 7 層（Experiment）**設計稿，審查會建議先用 Figma Make 驗證互動，再執行正式審查。

---

## 與其他 SKILL 的關係

```
figma-readiness-audit（本 SKILL）
    |
    |-- 前置步驟：
    |     figma-to-react（Web Level A 實作）
    |     figma-assets-only（圖片資源下載規則）
    |
    |-- 提供資訊給：
          Flutter 骨架生成（Level B）
          Windows 規格生成（Level C）
```

---

## 觸發時機

**設計師主動使用（最重要的場景）**
- 「幫我看看這個設計稿，工程師說不夠清楚」
- 「我的設計稿哪裡需要補充？」
- 「設計稿 review」、「設計一致性檢查」
- 「我這樣設計工程師看得懂嗎？」

**Handoff 前確認**
- 「Ready for Dev 了嗎？」、「可以開始實作了嗎？」
- 「還缺什麼資訊？」、「設計稿完整嗎？」

**跨平台對齊**
- 「這個設計稿 Flutter 可以用嗎？」
- 「Web / Windows / Flutter 三端規格一致嗎？」
- 「Token 對齊」、「design-engineering alignment」

**DS 品質提升**
- 「這個元件放在 Design System 的哪一層比較對？」
- 「我的 Token 命名合理嗎？」
- 「設計師成熟度提升」、「DS 審查」
- 「這個應該是 DS 元件還是產品元件？」
- 「這個設計有用 DS 元件組成嗎？」

---

## 自查清單（23 項）

設計師在請求審查前可以先自我檢查：

### 設計系統基礎
- [ ] 關鍵元件都有使用設計系統（不是臨時拼裝）
- [ ] Variable 命名以用途為主，不只描述外觀
- [ ] 至少定義主要 State：default / hover / disabled / selected / loading
- [ ] 重要內容區塊有標示來源（CMS / API / static / brand asset）
- [ ] 重要圖片或品牌素材有來源標示

### 元件組成（D11）
- [ ] 每個 button / badge / select / input 都是 DS component instance（◆ 圖示）
- [ ] 沒有「視覺重複」— 同類型控制項都使用同一個 DS 元件
- [ ] 尚未進 DS 的元素已用決策樹分類
- [ ] 互動狀態（hover、disabled、focus）定義在元件 Variant 上，不是在每個頁面各做一次
- [ ] DS 缺口有記錄計畫：升級到 Core / 擴充現有 / 留在 Product layer

### 註解與交付
- [ ] 複雜互動有註解說明切換條件
- [ ] 關鍵圖層名稱可讓陌生工程師理解
- [ ] 要交付的 section 已標記 Ready for Dev
- [ ] 工程視角只看到最小必要上下文

### 程式碼連結
- [ ] 核心元件已對應到 codebase 檔案或 Code Connect snippet
- [ ] 核心 Token 已補齊平台 code syntax
- [ ] Light / dark mode 的 Token alias 已驗證

### AI / Agent 準備度
- [ ] Agent 指令已寫明優先使用既有元件
- [ ] Agent 指令已寫明禁用做法
- [ ] AI 工作流有固定的取材順序
- [ ] 第一版 AI 產出後會做型別與 props 校正

### 流程
- [ ] AI 常見錯誤有回寫到團隊文件
- [ ] Handoff 後有追蹤追問次數與修正量

---

## 常見問題

**Q：我的設計完全沒有 Variables，還能跑嗎？**
A：可以。審查會把它標為 Blocker，並告訴你從哪些最重要的顏色開始加 Variables。

**Q：我只做 Web，需要分析 Flutter / Windows 嗎？**
A：不需要。告訴 agent 你只針對哪些平台，它會跳過其他的。

**Q：Code Connect 一定要做嗎？**
A：不一定。D8 和 D9 是加分項。沒有它們不會被標為 Blocker。

**Q：探索稿 / Experiment 要怎麼分析？**
A：審查會偵測第 7 層設計稿，建議你先用 Figma Make 驗證互動，收斂後再跑正式審查。

**Q：這份報告是給設計師看還是給工程師看？**
A：主要給設計師。報告最後的「工程師備忘」區塊是給工程師看的，其他所有內容都用設計師語言撰寫。

**Q：DS 組成分析表是什麼？**
A：報告新增的一個區塊，列出設計中每個可識別的 UI 元素，透過決策樹判斷它該放在 DS 的哪一層，檢查 DS 裡是否已有對應元件，並給出建議動作（使用現有元件 / 擴充 / 新建 / 留在產品層）。這幫助設計師在 handoff 前就想好元件組成，避免工程師重新發明輪子。

**Q：D11 元件組成是什麼？**
A：新增的一個審查維度，檢查設計是否由 DS 元件組成，而非用原始圖形拼裝。使用 DS component instance 的設計能直接對應到工程的 DS 元件，工程師不需要猜測。

---

## 檔案說明

| 檔案 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | 主流程（< 500 行）|
| [CHECKLIST.md](CHECKLIST.md) | 詳細評分規則、Level 升降條件、23 項自查清單 |
| [README.md](README.md) | 英文版說明 |
| [README_TW.md](README_TW.md) | 本檔案（繁體中文）|
