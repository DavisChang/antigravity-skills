# Security and Sandbox Design

AI-generated code is **untrusted by default**. Every candidate's code runs in an isolated sandbox with strict limits.

---

## Sandbox Principles

### Mandatory Controls

| Control | Rule |
|---------|------|
| Network egress | OFF by default — no outbound connections |
| CPU limit | Configurable per task (default: 2 cores) |
| Memory limit | Configurable per task (default: 512MB) |
| Time limit | Configurable per task (default: 5 minutes) |
| Filesystem | Temporary, destroyed after validation |
| Base image | Read-only, minimal |
| Secrets | NEVER injected — use test-only fakes |
| Artifacts | Scanned before extraction from sandbox |

### Sandbox Technology

| Level | Technology | Use Case |
|-------|-----------|----------|
| MVP | Docker containers | Quick to set up, reasonable isolation |
| Production | gVisor (runsc) | Kernel-level syscall filtering |
| High security | Firecracker microVMs | Hardware-level isolation, multi-tenant safe |

---

## Secret Design

### During Candidate Execution

- Candidates receive **test-only fake credentials**
- No real API keys, tokens, or database credentials
- Test fixtures provide mock responses for external services

### During Deployment (Post-Judge)

- Real secrets injected only by a **secret broker** at deployment time
- The judge never sees real secrets
- Secret broker is a separate service with its own access controls

### Secret Broker Flow

```
Candidate code → uses fake keys → validated in sandbox
                                        ↓
Final approved code → secret broker injects real keys → deployed
```

---

## Policy Engine

Use deterministic rules for hard limits. These are NOT suggestions — they are enforced programmatically.

### Default Policies

| Policy | Rule |
|--------|------|
| No shell escape | Candidate code cannot invoke shell commands |
| No network access | No outbound HTTP, DNS, or socket connections |
| No persistent storage | Cannot write to host filesystem |
| No privilege escalation | Cannot change user, mount, or access /proc |
| License compliance | Reject packages with forbidden licenses (GPL in proprietary projects, etc.) |
| No eval/exec of dynamic strings | Flag dynamic code execution patterns |

### Policy Implementation Options

| Tool | Description |
|------|-------------|
| OPA (Open Policy Agent) | Rego-based policy evaluation |
| Custom Python rules | Simple if/then checks for MVP |
| Seccomp profiles | Kernel-level syscall filtering |
| AppArmor / SELinux | MAC-based confinement |

### Policy Violation Output

```json
{
  "violations": [
    {
      "policy": "no_shell_escape",
      "file": "src/utils/deploy.ts",
      "line": 42,
      "snippet": "exec('rm -rf /tmp/cache')",
      "severity": "critical"
    }
  ]
}
```

---

## Threat Model

### Threats from AI-Generated Code

| Threat | Mitigation |
|--------|-----------|
| Data exfiltration | Network egress disabled |
| Destructive commands | Read-only base, temp filesystem, no shell |
| Resource exhaustion | CPU/memory/time limits |
| Dependency poisoning | Dependency scan + pinned versions |
| Secret theft | No real secrets in sandbox |
| Persistence | Ephemeral containers, destroyed after use |

### Threats to the Judge Pipeline

| Threat | Mitigation |
|--------|-----------|
| Prompt injection via candidate output | Judge sees structured schema, not raw text |
| Model hallucination in scoring | Evidence requirement for every score |
| Biased model selection | Multiple judge protocol for high-risk tasks |
| Audit tampering | Append-only audit log, immutable once written |

---

## Security Checklist for Deployment

- [ ] Sandbox network egress is disabled
- [ ] Resource limits are enforced (CPU, memory, time)
- [ ] No real secrets in sandbox environment
- [ ] Artifacts are scanned before extraction
- [ ] Audit log is append-only
- [ ] Policy engine rules are active
- [ ] Dependency scanning is enabled
- [ ] Secret broker is separate from the judge pipeline
- [ ] Human review gate is available for high-risk tasks
