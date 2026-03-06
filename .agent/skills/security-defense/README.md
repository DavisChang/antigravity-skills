# Security Defense Skill

> **Version**: 2.0.0 | **Language**: [繁體中文](README-TW.md)

An AI agent skill for performing endpoint security testing, penetration testing, defense analysis, and EU CRA product compliance assessment. Designed for Cursor IDE — the AI agent automatically activates this skill when security testing or CRA compliance is requested.

## What It Does

Two core capabilities with structured, repeatable workflows:

### 1. Endpoint Security Testing

Systematic testing for live services — backend APIs, frontend web apps, IP/port services, and infrastructure.

| Test Area | Key Focus |
|-----------|-----------|
| **Frontend** | XSS, CSRF, CORS, CSP, token storage, source map leaks |
| **Backend / API** | SQLi, SSRF, IDOR, input validation, rate limiting, error leakage |
| **Auth** | BOLA/BFLA, JWT security, session management, MFA, account enumeration |
| **Infrastructure** | Exposed services, default credentials, firewall rules, secrets management |
| **Business Logic** | Replay attacks, step-skipping, privilege escalation, webhook forgery |
| **Banking Sector** | 8 threat lines: ATO, edge exploitation, DDoS, API abuse, ransomware, supply chain, Swift/payment, data exfiltration |

### 2. EU CRA Product Compliance

Product-line classification and conformity assessment for products exported to the EU market under the Cyber Resilience Act (EU 2024/2847).

| Product Line | CRA Class | Assessment Path |
|-------------|-----------|-----------------|
| **Firewall / IDS / IPS** | Important Class II | Module B+C or H (notified body required) |
| **Router / Switch / Modem** | Important Class I | Module A if harmonised standard exists; else B+C/H |
| **IoT (smart home / wearable)** | Per-SKU determination | Depends on core functionality vs Annex III/IV |

## How It Works

### Endpoint Testing Workflow

```
Phase 0        Phase 1         Phase 2-5        Phase 6          Phase 7
Scope     ──▶  Recon &    ──▶  Frontend /  ──▶  Business    ──▶  Risk Report
Discovery      Exposure        API / Auth /     Logic &          & Remediation
(Ask First)                    Infra Testing    Monitoring
```

### CRA Compliance Workflow

```
Step 1          Step 2            Step 3           Step 4
Classify   ──▶  Select       ──▶  Build       ──▶  Comply by
each SKU        Assessment        Evidence          Deadline
                Path              Package           (2026/2027)
```

## Directory Structure

```
security-defense/
├── SKILL.md                                    # Core instructions for the AI agent
├── README.md                                   # This file (English)
├── README-TW.md                                # 繁體中文版說明
└── references/
    ├── scope-template.md                       # Asset inventory & scope definition
    ├── frontend-checklist.md                   # Frontend security checklist
    ├── backend-api-checklist.md                # Backend/API security checklist
    ├── auth-checklist.md                       # Authentication & authorization checklist
    ├── infra-checklist.md                      # Host/IP/Port/service security checklist
    ├── banking-defense-matrix.md               # Banking sector attack-defense matrix
    ├── report-template.md                      # Vulnerability report template
    ├── cra-product-compliance.md               # CRA product-line classification & governance
    ├── cra-classification-guide.md             # SKU classification workshop (5 questions)
    └── cra-timeline-obligations.md             # CRA timeline, deadlines & action items
```

## Quick Start

### Trigger — Endpoint Security Testing

Ask the AI agent in Cursor:

```
"Help me do a penetration test on my service"
"幫我檢測這個 API 的安全性"
"Check if my endpoints have vulnerabilities"
"掃描一下這些 IP/Port 有什麼問題"
```

**Important:** The agent will ask scope questions first (targets, accounts, tech stack, test boundaries) before starting any scan. If you haven't provided enough info, it will ask.

### Trigger — CRA Compliance

```
"Help me classify my products under CRA"
"我的產品需要做 CRA 合規嗎？"
"What do I need for CE marking under CRA?"
"幫我做 CRA 產品分類"
```

### Test Intensity Levels

| Level | Scope | Risk |
|-------|-------|------|
| **L1** | Passive recon, config checks, low-risk validation | Minimal |
| **L2** | Standard pentest: auth, authz, input validation | Low |
| **L3** | High-risk: SSRF, deserialization, RCE, privilege escalation | Medium |

## CRA Key Dates

| Date | What Happens | Status |
|------|-------------|--------|
| 2024-12-11 | CRA enters into force | Done |
| **2026-06-11** | Notified body provisions apply | Upcoming |
| **2026-09-11** | **Vulnerability & incident reporting mandatory** | Upcoming |
| **2027-12-11** | **Full CRA enforcement + CE Mark required** | Upcoming |

## Risk Classification

### Endpoint Testing — Finding Format

| ID | Type | Location | Impact | Exploitability | Risk |
|----|------|----------|--------|----------------|------|
| V-01 | IDOR | /api/users/{id} | Read others' data | High | HIGH |
| V-02 | CORS | api.example.com | Token misuse | Medium | MEDIUM |

### Top 10 Most Common Findings

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

## Tools Ecosystem

| Category | Tools |
|----------|-------|
| Subdomain enum | `subfinder`, `amass`, `httpx` |
| Port scanning | `nmap`, `masscan`, `rustscan` |
| Web scanning | `nuclei`, `nikto`, `OWASP ZAP` |
| API testing | `Burp Suite`, `Postman`, `ffuf` |
| Secret scanning | `gitleaks`, `trufflehog` |
| TLS testing | `testssl.sh`, `sslyze` |
| SAST | `semgrep`, `bandit`, `gosec` |
| DAST | `OWASP ZAP`, `Burp Suite` |
| Infra scanning | `trivy`, `grype`, `lynis` |
| SBOM generation | `syft`, `trivy`, `cdxgen` |
| SBOM vuln matching | `grype`, `trivy` |
| Firmware analysis | `binwalk`, `firmwalker` |

## References & Standards

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/API-Security/)
- [EU CRA Official Text (EU 2024/2847)](https://eur-lex.europa.eu/eli/reg/2024/2847/oj)
- [NIST Cybersecurity Framework 2.0](https://www.nist.gov/cyberframework)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)

## Version History

| Version | Date | Highlights |
|---------|------|-----------|
| v2.0.0 | 2026-03-06 | Added EU CRA product compliance module (3 reference files) |
| v1.0.0 | 2026-03-06 | Initial release: endpoint testing + banking defense matrix |

## Comparison with security-audit Skill

| Aspect | security-audit | security-defense |
|--------|---------------|-----------------|
| **Focus** | **Source code** auditing | **Live service** testing + **product compliance** |
| **Input** | Codebase / repository | Domains, IPs, ports, APIs, product SKUs |
| **Method** | Static analysis (SAST), code review | Dynamic testing (DAST), penetration testing, scanning |
| **Output** | Code-level vulnerability report | Service-level + CRA compliance report |
| **Platforms** | Frontend, Backend, Electron, Container, AI | Frontend, Backend, API, Infra, Banking, CRA |
| **When to use** | "Review this codebase for security issues" | "Test my live API / Check my product for CRA" |

**Best practice:** Use both skills together — `security-audit` for code review, `security-defense` for live testing and CRA compliance.

## License

Internal project tool. Distributed with the repository.
