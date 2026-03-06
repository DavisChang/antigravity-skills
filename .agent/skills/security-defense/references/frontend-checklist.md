# Frontend Security Checklist

## 1. 資訊洩漏

- [ ] JS bundle 無 API key / token / 密鑰
- [ ] JS bundle 無內部環境網址
- [ ] JS bundle 無 S3 bucket 名稱
- [ ] JS bundle 無 feature flag 敏感值
- [ ] JS bundle 無管理端路徑
- [ ] Source map 不對外暴露（production 不部署 .map 檔）
- [ ] HTML 註解無內部資訊
- [ ] console.log 不輸出敏感 debug 資訊
- [ ] robots.txt / sitemap 不洩漏內部路徑

### 掃描指令

```bash
# 檢查 source map
curl -s https://target.com/main.js.map | head -c 100

# 搜索 JS 中的敏感字串
curl -s https://target.com/main.js | rg -i '(api[_-]?key|secret|token|password|aws|s3://|internal|admin|debug)'
```

## 2. XSS / DOM XSS

- [ ] 所有用戶輸入已正確編碼後渲染
- [ ] 無使用 `innerHTML` / `dangerouslySetInnerHTML` 處理用戶輸入
- [ ] 無使用 `eval()` / `Function()` / `document.write()` 處理用戶輸入
- [ ] URL 參數不直接注入 DOM
- [ ] 第三方嵌入內容已沙箱化

### 測試方式

```
# 基本 XSS payload
<script>alert(1)</script>
"><img src=x onerror=alert(1)>
javascript:alert(1)
{{7*7}}  (SSTI 測試)

# DOM XSS 測試
https://target.com/page?q=<img/src=x onerror=alert(1)>
https://target.com/page#<img/src=x onerror=alert(1)>
```

## 3. CSRF

- [ ] 所有狀態變更操作（POST/PUT/DELETE）有 CSRF token
- [ ] CSRF token 不可預測且綁定 session
- [ ] SameSite cookie 屬性設為 Strict 或 Lax
- [ ] 跨來源請求有驗證 Origin / Referer

## 4. Clickjacking

- [ ] X-Frame-Options 設為 DENY 或 SAMEORIGIN
- [ ] CSP 包含 frame-ancestors 'none' 或 'self'
- [ ] 敏感操作頁面不允許被 iframe 嵌入

## 5. 開放重新導向

- [ ] 重新導向目標 URL 有白名單驗證
- [ ] 不允許導向外部網域
- [ ] 登入後 redirect 參數有驗證

## 6. CORS 配置

- [ ] Access-Control-Allow-Origin 不是 `*`
- [ ] 不反射 Origin header 為 Allow-Origin
- [ ] 不允許不信任的來源帶 credentials
- [ ] preflight 快取時間合理

### 測試方式

```bash
# CORS 配置檢查
curl -sI -H "Origin: https://evil.com" https://api.target.com/endpoint | grep -i access-control
```

## 7. 安全標頭

- [ ] `Content-Security-Policy` — 限制 script/style/img 來源
- [ ] `X-Frame-Options: DENY` 或 `SAMEORIGIN`
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `Strict-Transport-Security` — 包含 max-age 與 includeSubDomains
- [ ] `Referrer-Policy: strict-origin-when-cross-origin` 或更嚴格
- [ ] `Permissions-Policy` — 停用不需要的瀏覽器 API

### 掃描指令

```bash
curl -sI https://target.com | grep -iE '(content-security-policy|x-frame-options|x-content-type-options|strict-transport-security|referrer-policy|permissions-policy)'
```

## 8. Cookie 安全

- [ ] 敏感 cookie 設 `HttpOnly`（JS 不可讀取）
- [ ] 敏感 cookie 設 `Secure`（僅 HTTPS）
- [ ] 敏感 cookie 設 `SameSite=Strict` 或 `Lax`
- [ ] token 不存在 `localStorage`
- [ ] session ID 不可預測且足夠長

## 9. 檔案上傳

- [ ] 檔案類型有白名單驗證（不只看副檔名）
- [ ] 檔案大小有限制
- [ ] 上傳的檔案不直接在同域名下提供
- [ ] 上傳檔案有重新命名處理
- [ ] 圖片有重新處理（防止嵌入惡意 payload）
