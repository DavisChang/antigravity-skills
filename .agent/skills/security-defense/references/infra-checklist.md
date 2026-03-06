# Infrastructure Security Checklist

## 1. 對外服務盤點

### 不該公開的服務

| 服務 | 預設 Port | 風險 |
|------|-----------|------|
| SSH | 22 | 暴力破解、未授權存取 |
| Redis | 6379 | 未認證存取、資料外洩 |
| MongoDB | 27017 | 未認證存取、資料外洩 |
| PostgreSQL | 5432 | 暴力破解、SQL 注入 |
| MySQL | 3306 | 暴力破解、SQL 注入 |
| Elasticsearch | 9200 | 未認證讀寫、資料外洩 |
| Kibana | 5601 | 管理介面暴露 |
| Prometheus | 9090 | 內部指標外洩 |
| Grafana | 3000 | 管理介面暴露 |
| Docker API | 2375/2376 | 完全主機控制 |
| K8s Dashboard | 8443/6443 | 叢集控制 |
| Jenkins | 8080 | CI/CD 控制 |
| GitLab Runner | | 程式碼存取 |
| RabbitMQ Management | 15672 | 訊息佇列控制 |
| Kafka | 9092 | 訊息流存取 |
| Memcached | 11211 | 快取資料外洩 |

### 掃描指令

```bash
# 全 port 掃描
nmap -sV -sC -T4 -p- $TARGET_IP -oN nmap_full.txt

# 快速掃常見危險 port
nmap -sV -p 22,3306,5432,6379,9200,27017,2375,8443,9090,15672 $TARGET_IP

# 服務版本偵測
nmap -sV --version-intensity 5 -p $PORT $TARGET_IP
```

## 2. 主機安全

- [ ] 無預設帳號密碼
- [ ] 無共用帳號
- [ ] SSH 停用密碼登入（使用金鑰）
- [ ] SSH 停用 root 直接登入
- [ ] 無不必要的服務在運行
- [ ] OS 和套件定期更新
- [ ] 核心已無已知高風險 CVE
- [ ] 權限最小化（服務不以 root 運行）
- [ ] 檔案權限正確（/etc/shadow, private keys 等）
- [ ] 時間同步（NTP）

### 掃描指令

```bash
# 系統安全審計
lynis audit system

# 檢查 SUID 程式
find / -perm -4000 -type f 2>/dev/null

# 檢查監聽的服務
ss -tlnp
netstat -tlnp
```

## 3. 防火牆與網路

- [ ] 防火牆規則已啟用
- [ ] 預設策略為拒絕 (deny all)
- [ ] 僅開放必要 port
- [ ] 管理介面僅限內網
- [ ] 管理網段與應用網段分離
- [ ] 出站流量有限制
- [ ] 網路分段合理

### 檢查指令

```bash
# 查看防火牆規則
iptables -L -n
ufw status verbose
firewall-cmd --list-all
```

## 4. 服務配置

- [ ] debug mode 已關閉
- [ ] directory listing 已關閉
- [ ] 預設頁面已移除（Apache/Nginx 預設頁、Tomcat 管理頁）
- [ ] Server header 不洩漏版本號
- [ ] health check / metrics 端點不暴露敏感資訊
- [ ] 錯誤頁面不過度詳細
- [ ] 管理後台有 IP 白名單或 VPN 限制
- [ ] 不必要的 HTTP method 已停用（TRACE, OPTIONS 等）

### 檢查指令

```bash
# 檢查 server header
curl -sI https://target.com | grep -i server

# 檢查 HTTP methods
curl -sI -X OPTIONS https://target.com | grep -i allow

# 檢查 directory listing
curl -s https://target.com/assets/
curl -s https://target.com/static/
```

## 5. 敏感資料與密鑰管理

- [ ] .env 檔案不可從外部下載
- [ ] 備份檔不可從外部下載（.sql, .bak, .tar.gz, .zip）
- [ ] Log 檔不可從外部下載
- [ ] 設定檔不可從外部存取
- [ ] 管理憑證不在主機可讀路徑
- [ ] Secrets 使用環境變數或專用管理工具（Vault, AWS SSM）
- [ ] Secrets 定期輪替
- [ ] Git repo 不含 secrets（gitleaks 掃描）
- [ ] Docker image layers 不含 secrets
- [ ] CI/CD logs 不包含 secrets

### 常見敏感檔案路徑

```bash
# 嘗試存取常見敏感路徑
curl -s https://target.com/.env
curl -s https://target.com/.git/config
curl -s https://target.com/backup.sql
curl -s https://target.com/dump.sql
curl -s https://target.com/config.yml
curl -s https://target.com/wp-config.php
curl -s https://target.com/.DS_Store
curl -s https://target.com/server-status
curl -s https://target.com/debug
curl -s https://target.com/actuator
curl -s https://target.com/metrics
```

## 6. 容器安全（如適用）

- [ ] 使用最小基礎映像（alpine/distroless）
- [ ] 不以 root 運行容器
- [ ] 無 --privileged flag
- [ ] 已設 resource limits
- [ ] read-only root filesystem
- [ ] secrets 不在 image layers
- [ ] image 有漏洞掃描
- [ ] network policy 限制容器間流量

## 7. S3 / Object Storage（如適用）

- [ ] Bucket 非公開
- [ ] ACL 設定正確
- [ ] 無公開 list objects 權限
- [ ] 靜態網站託管不暴露敏感檔案
- [ ] Server-side encryption 已啟用
