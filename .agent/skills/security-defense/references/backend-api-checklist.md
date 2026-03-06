# Backend / API Security Checklist

## 1. Endpoint 盤點

每個 API 都應記錄：

| Method | Path | Auth Required | Role | Input Params | Output Data | Rate Limit | Risk |
|--------|------|---------------|------|--------------|-------------|------------|------|
| | | | | | | | |

### 盤點方式

```bash
# 從 OpenAPI / Swagger 自動提取
curl -s https://api.target.com/docs/openapi.json | jq '.paths | keys'

# 從前端 JS 提取 API 路徑
curl -s https://target.com/main.js | rg -o '"/api/[^"]*"' | sort -u

# 暴力探測常見路徑
ffuf -u https://api.target.com/FUZZ -w /path/to/api-wordlist.txt -mc 200,301,302,403
```

## 2. 輸入驗證

### 2.1 SQL / NoSQL Injection

- [ ] 所有資料庫查詢使用參數化查詢
- [ ] 無字串拼接 SQL
- [ ] NoSQL operator injection 已防護 ($gt, $ne, $regex)

```
# 測試 payload
' OR '1'='1
' UNION SELECT NULL,NULL--
{"$gt": ""}
{"$ne": null}
```

### 2.2 Command Injection

- [ ] 無直接將用戶輸入傳給 shell
- [ ] 使用安全的 API 替代 system()/exec()
- [ ] 參數有白名單驗證

```
# 測試 payload
; id
| cat /etc/passwd
$(whoami)
`id`
```

### 2.3 Server-Side Template Injection (SSTI)

- [ ] 無將用戶輸入直接作為模板渲染

```
# 測試 payload
{{7*7}}
${7*7}
<%= 7*7 %>
#{7*7}
```

### 2.4 Path Traversal

- [ ] 檔案路徑參數有驗證
- [ ] 不允許 ../ 遍歷
- [ ] 使用基礎路徑限制

```
# 測試 payload
../../../etc/passwd
..%2F..%2F..%2Fetc%2Fpasswd
....//....//....//etc/passwd
```

### 2.5 SSRF

- [ ] 外部 URL 參數有白名單
- [ ] 封鎖內網位址（127.0.0.1, 169.254.169.254, 10.x, 172.16-31.x, 192.168.x）
- [ ] 封鎖 file://, gopher://, dict:// 等協議

```
# 測試 payload
http://127.0.0.1
http://169.254.169.254/latest/meta-data/
http://[::1]
http://0x7f000001
```

### 2.6 XML / XXE

- [ ] XML parser 已停用外部實體
- [ ] 已停用 DTD 處理

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root>&xxe;</root>
```

### 2.7 反序列化

- [ ] 不反序列化不受信任的輸入
- [ ] 使用安全的序列化格式（JSON 優先）
- [ ] Python pickle / Java ObjectInputStream / PHP unserialize 已限制

### 2.8 檔案上傳

- [ ] 伺服器端檔案類型驗證（magic bytes, not just extension）
- [ ] 檔案大小限制
- [ ] 上傳目錄不可執行
- [ ] 隨機化檔名
- [ ] 病毒/惡意軟體掃描

## 3. 回應安全

- [ ] 錯誤回應不包含堆疊追蹤
- [ ] 錯誤回應不包含 SQL / ORM 錯誤細節
- [ ] 錯誤回應不包含內部路徑或主機名
- [ ] 錯誤回應不包含版本號
- [ ] API 回應不包含不必要欄位（最小揭露原則）
- [ ] 統一錯誤格式（不依錯誤類型洩漏內部狀態）

### 測試方式

```bash
# 觸發錯誤回應
curl -s https://api.target.com/api/users/999999999
curl -s -X POST https://api.target.com/api/login -d '{"invalid": true}'
curl -s https://api.target.com/api/users/' -H "Content-Type: application/json"
```

## 4. Rate Limiting

- [ ] 登入端點有 rate limit
- [ ] OTP / 驗證碼端點有 rate limit
- [ ] 查詢端點有 per-user / per-IP 限制
- [ ] 檔案上傳有頻率限制
- [ ] 匯出/下載有頻率限制
- [ ] rate limit 回應使用 429 狀態碼
- [ ] rate limit 回應包含 Retry-After header

## 5. 日誌與可觀測性

- [ ] 所有認證事件有日誌（成功/失敗）
- [ ] 所有授權失敗有日誌
- [ ] 所有敏感操作有 audit trail
- [ ] 日誌不包含密碼、token、密鑰等敏感值
- [ ] 日誌可被集中收集與查詢
