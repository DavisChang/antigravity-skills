# Authentication & Authorization Security Checklist

## 1. 認證 (Authentication)

### 1.1 密碼安全

- [ ] 密碼最小長度 >= 8（建議 12+）
- [ ] 密碼複雜度要求合理
- [ ] 密碼使用安全雜湊（bcrypt / argon2 / scrypt）
- [ ] 不使用 MD5 / SHA1 做密碼雜湊
- [ ] 密碼不以明文存儲
- [ ] 密碼不在 API 回應中返回

### 1.2 登入保護

- [ ] 登入失敗有次數限制（帳號鎖定或漸進延遲）
- [ ] 失敗訊息不區分「帳號不存在」或「密碼錯誤」（防帳號枚舉）
- [ ] 登入端點有 rate limiting
- [ ] 登入使用 HTTPS
- [ ] 登入有 CAPTCHA 或類似防自動化機制
- [ ] 不同 IP 大量失敗有告警

### 1.3 MFA

- [ ] 高風險操作要求 MFA
- [ ] MFA 使用 TOTP / FIDO2 / WebAuthn（非 SMS 優先）
- [ ] MFA 備份碼安全存儲
- [ ] MFA 設定變更需重新驗證
- [ ] MFA fatigue 防護（push notification 有次數限制）

### 1.4 密碼重設

- [ ] Reset token 足夠隨機且不可猜測
- [ ] Reset token 有過期時間（建議 15-30 分鐘）
- [ ] Reset token 使用一次即失效
- [ ] 重設密碼後所有舊 session/token 失效
- [ ] 重設流程不洩漏帳號是否存在
- [ ] 重設連結使用 HTTPS

### 1.5 Session / Token 管理

- [ ] Session ID 足夠隨機且不可猜測
- [ ] Session 有過期時間
- [ ] 登出後 session 立即失效（server-side invalidation）
- [ ] 密碼變更後所有其他 session 失效
- [ ] 權限變更後舊 token 立即失效
- [ ] Refresh token 有輪替機制
- [ ] Token 不在 URL 中傳遞

### 1.6 JWT 安全

- [ ] JWT 使用強演算法（RS256 / ES256，非 HS256 配弱密鑰）
- [ ] JWT 驗證簽名（不接受 alg: none）
- [ ] JWT 有合理過期時間
- [ ] JWT payload 不含敏感資訊
- [ ] JWT 不可被修改後仍通過驗證
- [ ] 關鍵 claims（iss, aud, exp）都有驗證

### 測試方式

```bash
# 帳號枚舉測試
curl -s -X POST https://target.com/api/login -d '{"email":"exist@test.com","password":"wrong"}' -H "Content-Type: application/json"
curl -s -X POST https://target.com/api/login -d '{"email":"nonexist@test.com","password":"wrong"}' -H "Content-Type: application/json"
# 比較回應差異

# JWT 測試
# 解碼 JWT
echo "eyJ..." | cut -d'.' -f2 | base64 -d 2>/dev/null

# 修改 payload 後重簽（alg:none 測試）
# 修改 user role 後重放
```

---

## 2. 授權 (Authorization)

### 2.1 物件層授權 (BOLA/IDOR)

- [ ] 每個 API 端點都驗證請求者是否有權存取該物件
- [ ] 不僅檢查「已登入」，也檢查「有權限存取此筆資料」
- [ ] 物件 ID 使用 UUID（而非可預測的遞增 ID）
- [ ] 批量操作端點也有逐筆授權檢查

### 必測情境

```
1. user A 的 token → GET /api/users/{userB_id}       → 應返回 403
2. user A 的 token → PUT /api/users/{userB_id}       → 應返回 403
3. user A 的 token → DELETE /api/orders/{userB_order} → 應返回 403
4. user A 的 token → GET /api/users/{userB_id}/files  → 應返回 403
```

### 2.2 功能層授權 (BFLA)

- [ ] 管理功能的端點有角色驗證
- [ ] 一般使用者無法呼叫 admin endpoint
- [ ] 權限不僅在前端隱藏，後端也有檢查
- [ ] API 路徑 / HTTP method 都有權限檢查

### 必測情境

```
1. 一般使用者 → GET /api/admin/users          → 應返回 403
2. 一般使用者 → POST /api/admin/settings      → 應返回 403
3. 一般使用者 → DELETE /api/admin/users/{id}   → 應返回 403
4. 改 HTTP method (GET → PUT → DELETE)         → 確認都有檢查
```

### 2.3 屬性層授權

- [ ] 用戶不能修改自己不應修改的欄位（如 role, isAdmin）
- [ ] API 回應不返回不應看到的欄位
- [ ] 批量更新不允許修改受限欄位

### 必測情境

```
1. PUT /api/users/me -d '{"role": "admin"}'          → role 不應被改
2. PUT /api/users/me -d '{"isVerified": true}'       → 不應被改
3. GET /api/users/me → 回應不含 passwordHash 等欄位
```

### 2.4 多租戶隔離

- [ ] 租戶 A 無法存取租戶 B 的資料
- [ ] 查詢自動限定在當前租戶範圍
- [ ] 租戶間的資料在 API 層完全隔離
- [ ] 切換租戶需要重新驗證

### 2.5 特殊操作

- [ ] 被停權帳號的 token 立即失效
- [ ] 刪除操作有確認機制
- [ ] 匯出/下載有額外權限檢查
- [ ] 批量操作有上限限制
- [ ] 敏感操作需 step-up 驗證（重新輸入密碼或 MFA）
