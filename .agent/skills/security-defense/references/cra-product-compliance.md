# EU CRA 產品線分級治理 — 產品資安合規指南

> 核心原則：先分類、再選路徑、按時程排優先級
> CRA 生效：2024-12-10 | 通報義務：2026-09-11 | 全面適用：2027-12-11

---

## 產品線優先級矩陣

| 產品線 | 典型 SKU | 建議暫定分類 | 符合性評估路徑 | 優先級 |
|--------|----------|-------------|---------------|--------|
| **資安產品** | Firewall, IDS, IPS | Important **Class II** | Module B+C 或 Module H | **最高** |
| **網通設備** | Router, Switch, Modem | Important **Class I** | 有 harmonised standard 時 Module A；否則 B+C / H | **高** |
| **IoT 產品** | 智慧家庭, 穿戴裝置 | **逐 SKU 判定**（可能 default / Class I） | 依分類決定 | **中高** |

---

## 一、資安產品線 (Firewall / IDS / IPS) — P1 最高優先

### 為什麼最優先

- CRA 架構下屬 **Important products – Class II** 核心範例
- Class II **必須走 notified body 參與的符合性評估**（Module B+C 或 Module H），不能只靠自我宣告
- 第三方評估資源未來很可能吃緊，越晚準備越容易排隊
- 客戶採購詢問最容易先問合規

### 符合性評估路徑

```
Important Class II
  └─→ Module B (EU-type examination) + Module C (conformity to type)
  └─→ 或 Module H (full quality assurance)
  └─→ 必須有 notified body 參與
```

### 你現在最該先做的事

1. **SKU 清單與分類確認** — 列出所有出口 EU 的資安產品 SKU
2. **啟動 notified body 路徑** — 提前聯繫、評估時程與費用
3. **技術文件骨架** — 安全設計、開發流程、測試策略、風險評估
4. **測試證據體系** — 建立可重複的測試計畫與證據保存機制
5. **PSIRT 與通報流程** — 2026-09-11 前必須可運作
6. **SBOM / 第三方元件治理** — 機器可讀格式、CVE 追蹤

### 主要卡點

- 證據鏈不完整導致評估延遲
- 漏洞處理成熟度不足
- notified body 資源不足

---

## 二、網通設備 (Router / Switch / Modem) — P2 高優先

### 分類定位

- 路由器、連網 modem、switch 一般屬 **Important products – Class I**
- Class I 若有適用的 harmonised standard / common specifications，可走 **Module A**（自我評估）
- 若沒有適用標準，則同樣要走 Module B+C 或 H

### 符合性評估路徑

```
Important Class I
  ├─→ 有 harmonised standard / common specs / EU cyber certification
  │     └─→ Module A (self-assessment) 即可
  └─→ 沒有
        └─→ Module B+C 或 Module H（需 notified body）
```

### Support Period 關鍵警告

**CRA FAQ 明確指出：**
- Support period **至少 5 年**
- 若產品合理預期使用期更長，**support period 就要更長**
- FAQ **直接點名** routers, modems, switches 屬於常見需要更長 support period 的類型

### 這對你的影響

| 問題 | 衝擊 |
|------|------|
| LTS branch 怎麼維護 | 每個主要版本可能要維護 7-10 年 |
| 晶片/BSP 供應商支援多久 | 供應商 EOL 可能早於你的 support period |
| OTA 與修補節奏 | 需要可靠的遠端更新機制 |
| EOS/EOL 與客戶合約 | 必須在產品上明確標示 support end date |
| 第三方元件（Linux kernel, Wi-Fi stack 等） | 需長期追蹤上游安全更新 |

### 你現在最該先做的事

1. **完成 SKU 分類** — 確認每個產品的 Class I 定位
2. **制定 support period 政策** — 至少 5 年，網通通常需要更長
3. **LTS / OTA 路線** — 韌體分支策略、安全更新分發機制
4. **BSP / 晶片供應商盤點** — 確認供應商支援期限是否匹配
5. **SBOM 與漏洞追蹤** — 含 Linux 套件、Wi-Fi/BT stack、SDK

### 主要卡點

- Support period 撐不住
- 晶片/BSP 供應商不配合
- OTA / 韌體維護流程不成熟
- EOS/EOL 聲明與客戶期待不一致

---

## 三、IoT 產品 (智慧家庭 / 穿戴裝置) — P3 中高優先

### 最關鍵的警告：不能整條線直接預設 Class I

CRA 的邏輯是看 **core functionality**，不是只看「它是不是 IoT」：

- 是否屬於 Important Class I / II，要看是否落入 **Annex III / IV** 類別
- 很多 IoT 產品在 CRA 範圍內，但**不一定是 Class I**
- 智慧家庭、穿戴要**逐 SKU 判定**，不能整條產品線直接套同一類

### Remote Data Processing 邊界

**CRA 範圍包含產品必須依賴的 remote data processing solutions：**

```
IoT 產品邊界
  ├─→ 裝置本體（韌體、硬體）
  ├─→ 手機 App（iOS / Android）
  ├─→ 雲端服務（帳號系統、API、資料庫）
  ├─→ OTA 更新平台
  └─→ 第三方服務（語音助手、地圖、支付）
  
  ↑ 如果這些是核心功能不可或缺的一部分，
    就全部落入 CRA 邊界
```

### 你現在最該先做的事

1. **裝置 / App / Cloud / OTA 邊界圖** — 畫出每個 SKU 的完整系統邊界
2. **Remote data processing 判定** — 哪些雲端/App 是核心功能必須的
3. **SKU 分級** — 逐一判定 default / Class I / Class II
4. **第三方元件盤點** — mobile app 套件、cloud SDK、裝置韌體元件
5. **SBOM** — 裝置 + App + Cloud 各自的 SBOM

### 主要卡點

- SKU 多，證據零散
- App / Cloud / 裝置韌體版本不同步
- 零組件多，SBOM 與漏洞追蹤難度高
- Remote data processing 邊界不清楚

---

## 四、跨產品線共通義務

### 4.1 PSIRT / 漏洞通報（2026-09-11 起強制）

**此義務也適用到在 2027-12-11 之前就已放到 EU 市場上的產品。**

| 時限 | 動作 | 內容 |
|------|------|------|
| **24 小時** | Early Warning | 通報被積極利用漏洞，指明產品上市位置 |
| **72 小時** | Vulnerability Notice | 產品資訊、漏洞性質、緩解措施、敏感程度 |
| **14 天** | Final Report | 漏洞描述、嚴重性、影響、惡意行為者資訊、修復措施 |

**通報對象：** CSIRT / ENISA（透過單一報告平臺）

### 4.2 SBOM（軟體物料清單）

- 機器可讀格式（CycloneDX / SPDX）
- 至少涵蓋頂級依賴關係
- 需包含第三方元件 / 開源元件
- 需持續更新與 CVE 追蹤

### 4.3 Technical Documentation

**使用者資訊 (User Facing)：**
- 安全安裝與操作手冊
- 製造商聯繫方式
- 支援結束日期 (End of Support Date)
- 安全更新的自動設定指引

**技術文件 (Regulator Facing)：**
- 網路安全風險評估 (Cybersecurity Risk Assessment)
- 軟體物料清單 (SBOM)
- 測試報告與安全開發生命週期證明
- 符合性聲明 (EU Declaration of Conformity, DoC)

### 4.4 產品網路安全要求

- (a) 上市時不存在已知的可利用漏洞
- (b) 採用默認安全配置 (Secure by Default)
- (c) 安全更新機制（默認自動更新 + 退出機制）
- (d) 存取控制與身份驗證
- (e) 資料加密（靜態 + 傳輸中）

### 4.5 漏洞處理 8 項要求

1. 識別並記錄漏洞和元件（SBOM）
2. 立即解決和修復漏洞，安全更新與功能更新分離
3. 定期安全測試與審查
4. 公開披露已修復漏洞資訊
5. 制定協調漏洞披露政策
6. 促進第三方元件漏洞資訊共用
7. 安全分發更新機制
8. 及時免費分發安全更新

---

## 五、違規罰款

| 違規類型 | 罰款上限 |
|----------|----------|
| 未遵守基本安全要求、製造商義務或報告義務 | **1500 萬歐元** 或全球營業額 **2.5%** |
| 不遵守其他義務 | 1000 萬歐元 或全球營業額 2% |
| 提供誤導性或不正確的資訊 | 500 萬歐元 或全球營業額 1% |

---

## 六、90 天行動計畫

### 第 1 個月：分類與盤點

- [ ] 完成所有出口 EU 產品的 **SKU classification workshop**
- [ ] 每個 SKU 建立：類別、版本、核心功能、必需 cloud/app、預期 support period
- [ ] 先挑出所有 Firewall / IDS / IPS 做 **Class II 清單**
- [ ] IoT 產品做 remote data processing 邊界判定

### 第 2 個月：流程與文件

- [ ] 建立 **PSIRT / VEX / SBOM / 通報流程**
- [ ] 定義 **support period 與 EOL/EOS** 溝通格式
- [ ] 建立 CRA **technical documentation 樣板**
- [ ] 網通設備 LTS / OTA 策略定案

### 第 3 個月：驗證與啟動

- [ ] Class II 產品先跑一次 **mock assessment**
- [ ] Router / Switch 建 **LTS 與 OTA 策略**
- [ ] IoT 產品把 App / Cloud / OTA / backend 一起納入邊界
- [ ] 啟動 **notified body 溝通**

---

## 七、SKU 分類決策樹

```
產品是否含有數位元素且投放 EU 市場？
  │
  ├─ 否 → 不適用 CRA
  │
  └─ 是 → 是否屬於豁免產品？（醫療/車輛/民航/船用/純 SaaS）
       │
       ├─ 是 → 不適用 CRA
       │
       └─ 否 → 核心功能是否落入 Annex IV？（Critical products）
            │
            ├─ 是 → Critical Category → 最嚴格評估
            │
            └─ 否 → 核心功能是否落入 Annex III Class II？
                 │
                 ├─ 是 → Important Class II → Module B+C 或 H
                 │
                 └─ 否 → 核心功能是否落入 Annex III Class I？
                      │
                      ├─ 是 → Important Class I
                      │    ├─ 有 harmonised standard → Module A
                      │    └─ 無 → Module B+C 或 H
                      │
                      └─ 否 → Default category → Module A
```

For SKU classification workshop template, see [cra-classification-guide.md](cra-classification-guide.md)
For complete CRA timeline, see [cra-timeline-obligations.md](cra-timeline-obligations.md)
