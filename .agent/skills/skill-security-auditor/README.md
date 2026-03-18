# Skill Security Auditor

A static security review skill for AI agent skills — any format, any ecosystem. Detects prompt injection, malware delivery, secret exfiltration, supply-chain abuse, and authority escalation before a skill is installed or executed.

## Why This Exists

AI skill marketplaces are the latest supply-chain attack surface. The same patterns seen in npm, PyPI, VS Code extensions, and browser add-ons — typosquatting, social engineering, trojanized functionality, and credential theft — now target AI agent ecosystems. A compromised agent skill can access everything the agent is connected to: email, messaging, calendar, documents, financial data, and secrets.

This skill provides a first layer of static analysis and threat detection for any agent skill, regardless of format.

## What It Detects

| Risk Class | Description |
|:---|:---|
| Prompt Injection | Untrusted input treated as commands; email/web content driving execution |
| Malware Delivery | `curl\|bash`, obfuscated scripts, encoded payloads, persistence mechanisms |
| Multi-Stage Payload | Base64 decode chains, paste-site loaders, staged downloads, unresolvable final payloads |
| Trojanized Logic | Malicious calls hidden inside working features; reverse shells in functional code paths |
| Reverse Shell / C2 | Outbound shell to raw IP:port, socket redirection, `nc -e`, hidden `os.system(curl)` |
| Secret Theft | Access to `.ssh`, `.env`, cookies, wallets, keychains, agent configs; upload to remote sinks |
| Archive Evasion | Password-protected ZIP/RAR/7z containing executables; password in instructions |
| Prerequisite Trap | "Install this tool first" leading to non-official binary downloads or malware |
| Over-Privilege | Unnecessary env vars, broad filesystem/network access, unscoped MCP tools |
| Authority Escalation | Sandbox bypass, permission elevation, safety guardrail override |
| Supply Chain | Typosquatted names, unverified downloads, shortened URLs, missing checksums |
| High-Value Targeting | Crypto/wallet/trading, YouTube, Google Workspace, social media, finance, PDF tools |

## Supported Skill Formats

| Format | Typical Location | Key File(s) |
|:---|:---|:---|
| AgentSkills / Antigravity | `.agent/skills/<name>/` | `SKILL.md`, scripts, configs |
| Cursor Skills | `.cursor/skills/<name>/` | `SKILL.md` |
| Cursor Rules | `.cursor/rules/` | `*.mdc`, `RULE.md` |
| Codex Skills | `.codex/skills/<name>/` | `SKILL.md` |
| Gemini Skills | `.gemini/skills/<name>/` | `SKILL.md` |
| Google AGENTS.md | repo root or subdirectories | `AGENTS.md` |
| MCP Server Configs | `.cursor/mcp.json`, etc. | JSON config files |
| Custom / Ad-hoc | any path | any instructional file |

## How to Invoke

Ask your AI agent to audit a skill:

```
Audit this skill for security issues.
Check if this skill is safe to install.
Review .agent/skills/some-skill/ for security risks.
檢查這個 skill 安不安全
```

## Review Procedure

The auditor follows a 9-step process for every skill:

| Step | Action |
|------|--------|
| 1 | Identify skill format and locate all associated files |
| 2 | Inventory all files, executables, URLs, and downloads |
| 3 | Review frontmatter/metadata for misleading descriptions or hidden capabilities |
| 4 | Review instructions for trust-boundary violations, prompt injection, secret exposure |
| 5 | Review code/scripts for trojanized logic, multi-stage payloads, reverse shells, obfuscation |
| 6 | Review privilege requirements against documented purpose |
| 7 | Review supply-chain dependencies, prerequisites, archives, and typosquatting |
| 8 | Analyze full payload delivery chain (entry → stages → final payload → platform branches) |
| 9 | Assign verdict: `PASS`, `WARN`, `FAIL`, or `NEEDS_MANUAL_REVIEW` |

## Verdict Levels

| Verdict | Meaning |
|---------|---------|
| `PASS` | No significant security concerns found |
| `WARN` | Suspicious or over-privileged, but no confirmed malicious behavior |
| `FAIL` | Confirmed destructive, exfiltrating, or malware-like behavior |
| `NEEDS_MANUAL_REVIEW` | Insufficient evidence to determine; human review required |

## Hard Fail Conditions

The auditor immediately returns `FAIL` for confirmed instances of:

- Browser cookie / crypto wallet / SSH key theft
- Secret exfiltration to remote destinations
- Hidden remote execution payloads or reverse shells
- Multi-stage payload chains where the final payload cannot be statically verified
- Password-protected archives containing executables
- Prerequisite installation from non-official sources
- Functional code with hidden shell execution calls to remote URLs
- Agent config exfiltration (`.env`, credentials sent externally)

## File Structure

```
.agent/skills/skill-security-auditor/
├── SKILL.md        # Skill definition (loaded by AI agent)
├── README.md       # This file — English overview
└── README_TW.md    # Traditional Chinese overview
```

## Design Principles

1. **Untrusted by default** — every third-party skill is treated as untrusted until proven otherwise
2. **Static analysis only** — never execute untrusted scripts, commands, or payloads during review
3. **False positives over missed threats** — prefer flagging a safe skill over missing a malicious one
4. **Full chain tracing** — follow every download, decode, and stage to determine the final payload
5. **Appearance is not trust** — professional READMEs and working features do not reduce risk
6. **Blast radius awareness** — evaluate impact in context of all services the agent is connected to
