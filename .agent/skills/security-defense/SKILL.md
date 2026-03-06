---
name: security-defense
description: Perform endpoint security testing, penetration testing, defense analysis, and EU CRA product compliance assessment. Covers backend APIs, frontend web apps, IP/port services, infrastructure, and CRA product-line classification (Class I/II/Critical). Asks structured questions when information is insufficient. Use when the user asks for penetration testing, endpoint security check, service security scan, attack surface analysis, CRA compliance, product classification, or mentions "滲透測試", "安全檢測", "資安防禦", "endpoint 檢查", "暴露面分析", "CRA 合規", "產品分類", "CE 認證", "漏洞通報".
---

# Security Defense — Endpoint Testing, Defense Analysis & CRA Compliance

## Overview

Two core capabilities:
1. **Endpoint Security Testing** — systematic testing for live services (API, web, IP/port, infra)
2. **EU CRA Product Compliance** — product-line classification, conformity assessment path, timeline obligations

Workflow: **ask scope → inventory → scan → test → report → remediate** (for testing)
Workflow: **classify SKU → select assessment path → build evidence → comply by deadline** (for CRA)

## Phase 0 — Scope Discovery (Ask First)

**Always gather target information before scanning. If insufficient, ask structured questions.**

### Required Information

| Category | What to ask |
|----------|-------------|
| Targets | Domains, subdomains, API URLs, public IPs |
| Accounts | Test accounts (user/admin/multi-tenant roles) |
| Tech stack | Frontend framework, backend language, DB, cache |
| Auth | JWT / Session / OAuth / API Key / MFA |
| Features | File upload, webhook, admin panel, export/download |
| Environment | Staging or production |
| Boundaries | Allowed test intensity (L1/L2/L3) |

### Test Intensity Levels

| Level | Scope | Risk |
|-------|-------|------|
| L1 | Passive recon, config checks, low-risk validation | Minimal |
| L2 | Standard pentest: auth, authz, input validation | Low |
| L3 | High-risk: SSRF, deserialization, RCE, privilege escalation | Medium |

**If the user hasn't specified targets or boundaries, use AskQuestion or ask conversationally before proceeding.**

### Scope Output Template

For asset inventory template, see [references/scope-template.md](references/scope-template.md)

---

## Phase 1 — Reconnaissance & Exposure

### Automated Scanning

```bash
# Subdomain enumeration
subfinder -d $DOMAIN -o subdomains.txt
httpx -l subdomains.txt -sc -title -tech-detect -o alive.txt

# Port scanning
nmap -sV -sC -T4 -p- $TARGET_IP -oN nmap_full.txt

# Web vulnerability scan
nuclei -u https://$TARGET -t cves/ -t exposures/ -t misconfigurations/

# TLS check
testssl.sh https://$TARGET

# Security headers
curl -sI https://$TARGET | grep -iE '(content-security|x-frame|x-content|strict-transport|referrer-policy|permissions-policy)'
```

### Exposure Checklist

- [ ] Forgotten systems (dev/staging/test/old/backup subdomains)
- [ ] Admin panels publicly accessible
- [ ] Swagger / API docs / GraphQL playground exposed
- [ ] Unnecessary ports open
- [ ] Redis / ES / MongoDB / Kafka / RabbitMQ exposed
- [ ] Docker daemon / K8s API / metrics exposed
- [ ] TLS misconfiguration or weak ciphers
- [ ] HSTS not set

---

## Phase 2 — Frontend Testing

For complete frontend checklist, see [references/frontend-checklist.md](references/frontend-checklist.md)

**Priority checks:**
1. JS bundle / source map leaking secrets, API URLs, internal paths
2. XSS / DOM XSS / CSRF / Clickjacking / Open redirect
3. Security headers (CSP, X-Frame-Options, HSTS)
4. Token storage (localStorage vs HttpOnly cookie)
5. CORS configuration

---

## Phase 3 — Backend / API Testing

For complete backend/API checklist, see [references/backend-api-checklist.md](references/backend-api-checklist.md)

**Priority checks:**
1. Endpoint inventory (path, method, auth requirement, role, risk)
2. Input validation: SQLi, NoSQLi, CMDi, SSTI, path traversal, SSRF, XXE, deserialization
3. Response leakage: stack traces, internal paths, version info
4. Rate limiting on sensitive endpoints

---

## Phase 4 — Authentication & Authorization Testing

For complete auth checklist, see [references/auth-checklist.md](references/auth-checklist.md)

**Must-test scenarios:**
1. User A reads User B's data (IDOR/BOLA)
2. User A modifies User B's data
3. Normal user hits admin endpoint (BFLA)
4. Disabled account token still works
5. Sensitive operations without step-up verification

---

## Phase 5 — Infrastructure Testing

For complete infrastructure checklist, see [references/infra-checklist.md](references/infra-checklist.md)

**Priority checks:**
1. Exposed services (SSH, Redis, MongoDB, PostgreSQL, ES, Docker API, K8s)
2. Default credentials
3. Debug mode / directory listing / default pages
4. Firewall rules too permissive
5. Secrets in .env / backup files / logs

---

## Phase 6 — Business Logic & Monitoring

**Test each core flow asking: can it be bypassed, replayed, skipped, forged, or abused in batch?**

Core flows to test: registration → login → create → update → escalate → delete/export/share → webhook/callback → admin ops

**Monitoring verification:**
- [ ] Failed logins trigger alerts
- [ ] High-frequency requests trigger alerts
- [ ] Sensitive operations have audit logs
- [ ] 5xx spikes are observable

---

## Phase 7 — Risk Classification & Report

### Finding Record Format

| ID | Type | Location | Impact | Exploitability | Risk |
|----|------|----------|--------|----------------|------|
| V-01 | IDOR | /api/users/{id} | Read others' data | High | HIGH |
| V-02 | CORS miscfg | api.example.com | Token misuse | Medium | MEDIUM |

### Risk Assessment (4 dimensions)
1. Can it be exploited without authentication?
2. Can it be reliably reproduced?
3. Can it access sensitive data or gain control?
4. Can it be escalated laterally?

For report structure, see [references/report-template.md](references/report-template.md)

---

## Top 10 Most Common Findings

1. IDOR / broken access control
2. Admin or debug endpoints exposed
3. File upload bypass
4. Password reset / verification code flaws
5. Webhook / callback missing signature verification
6. CORS / token storage misconfiguration
7. Redis / DB / metrics directly exposed
8. Secrets leaked in frontend bundle / repo
9. Verbose error messages
10. Business logic replay or step-skipping

---

## Banking & Financial Sector

For banking-specific attack-defense matrix covering 8 threat lines (ATO, edge exploitation, DDoS, API abuse, ransomware, supply chain, Swift/payment, data exfiltration), see [references/banking-defense-matrix.md](references/banking-defense-matrix.md)

---

## EU CRA Product Compliance

### When to Use

Use the CRA compliance workflow when:
- The target is a **product** (not just a service) sold/exported to the EU market
- Product types: networking equipment, IoT devices, security appliances, software with digital elements
- User mentions CRA, CE marking, product classification, Annex III/IV, notified body, conformity assessment

### Product Line Priority

| Product Line | Likely Class | Assessment Path | Priority |
|-------------|-------------|-----------------|----------|
| **Firewall / IDS / IPS** | Important Class II | Module B+C or H (notified body required) | **Highest** |
| **Router / Switch / Modem** | Important Class I | Module A if harmonised standard exists; else B+C/H | **High** |
| **IoT (smart home / wearable)** | Per-SKU (default / Class I) | Depends on classification | **Medium-High** |

### CRA Key Dates

| Date | Obligation |
|------|-----------|
| **2026-06-11** | Notified body provisions apply |
| **2026-09-11** | **Vulnerability & incident reporting mandatory** (also for products already on market) |
| **2027-12-11** | **Full CRA enforcement + CE Mark required** |

### CRA Scope Decision (Quick Check)

Ask these 5 questions for each SKU:
1. What is its **core functionality**?
2. Does it fall under **Annex III (Class I/II) or Annex IV (Critical)**?
3. Does it depend on **App / Cloud / backend** for core functions? (→ remote data processing in CRA scope)
4. What **support period** is appropriate? (min 5 years; network devices often longer)
5. What are the current **security capability gaps**?

### Critical Warnings

- **Class II must use notified body** — self-assessment is NOT sufficient
- **Class I without harmonised standard** — also needs notified body
- **IoT ≠ automatically Class I** — must check core functionality against Annex III/IV
- **Cloud/App may be in CRA scope** — if essential for core product functionality
- **Reporting obligation is retroactive** — applies to products already on EU market before 2027

For complete CRA product compliance guide, see [references/cra-product-compliance.md](references/cra-product-compliance.md)
For SKU classification workshop, see [references/cra-classification-guide.md](references/cra-classification-guide.md)
For CRA timeline and obligations, see [references/cra-timeline-obligations.md](references/cra-timeline-obligations.md)

---

## Tool Recommendations

| Category | Tools |
|----------|-------|
| Subdomain enum | subfinder, amass, httpx |
| Port scanning | nmap, masscan, rustscan |
| Web scanning | nuclei, nikto, OWASP ZAP |
| API testing | Burp Suite, Postman, ffuf |
| Secret scanning | gitleaks, trufflehog |
| TLS testing | testssl.sh, sslyze |
| SAST | semgrep, bandit, gosec |
| DAST | OWASP ZAP, Burp Suite |
| Infra scanning | trivy, grype, lynis |
| SBOM generation | syft, trivy, cdxgen |
| SBOM vuln matching | grype, trivy |
| Firmware analysis | binwalk, firmwalker |

---

## Reference Files

| File | Contents | When to read |
|------|----------|-------------|
| [references/scope-template.md](references/scope-template.md) | Asset inventory & scope definition template | Phase 0 |
| [references/frontend-checklist.md](references/frontend-checklist.md) | Complete frontend security checklist | Phase 2 |
| [references/backend-api-checklist.md](references/backend-api-checklist.md) | Complete backend/API security checklist | Phase 3 |
| [references/auth-checklist.md](references/auth-checklist.md) | Authentication & authorization checklist | Phase 4 |
| [references/infra-checklist.md](references/infra-checklist.md) | Host/IP/Port/service security checklist | Phase 5 |
| [references/banking-defense-matrix.md](references/banking-defense-matrix.md) | Banking sector attack-defense matrix | Financial sector engagements |
| [references/report-template.md](references/report-template.md) | Vulnerability report structure | Phase 7 |
| [references/cra-product-compliance.md](references/cra-product-compliance.md) | CRA product-line classification & governance | CRA compliance engagements |
| [references/cra-classification-guide.md](references/cra-classification-guide.md) | SKU classification workshop (5 questions) | CRA product classification |
| [references/cra-timeline-obligations.md](references/cra-timeline-obligations.md) | CRA timeline, deadlines & action items | CRA compliance planning |

---

## Continuous Improvement

After each engagement:
1. Record new attack patterns discovered
2. Update checklists with new findings
3. Add industry-specific matrices as needed
4. Update CRA reference files when new standards/FAQ are published
5. Bump version in this file

**Current version: 2.0.0 (2026-03-06) — Added CRA product compliance module**
