# Seven Dimensions: Complete Questions, Decisions & Deliverables

The agent references this file on demand during discussions. Each dimension lists:
- **Ask (Questions)**: Questions to surface blind spots
- **Decide (Decisions)**: Corresponding architectural decision points
- **Deliver (Deliverables)**: Concrete artifacts to produce after discussion

---

## ① Requirements & Success Definition

> If you haven't defined what success looks like, the architecture is just guessing.

### 1-1 Business Goals & Success Metrics (North Star)

**Ask**
- What pain point does this system solve? What happens if we don't build it?
- How do we quantify success? (conversion rate, retention, cost-per-unit, latency, availability)
- Are there conflicting metrics? (e.g., lower latency vs. lower cost)

**Decide**
- Architecture priority: time-to-market first vs. scalability/availability first
- When metrics conflict, which one wins?

**Deliver**
- KPI / SLI list + target values + measurement timeline
- Priority ranking document

### 1-2 Scope & Non-goals

**Ask**
- What are we explicitly NOT building in this version? Can we write it down?
- Are there parts designed preemptively "because we might need it later"? Do we really?
- Which capabilities can be deferred? (multi-region, strong consistency, real-time analytics...)

**Decide**
- What goes into MVP, V1, V2
- Whether to accept tech debt in exchange for speed

**Deliver**
- PRD In/Out list
- Milestone breakdown + scope per version

### 1-3 User Journeys & Critical Paths

**Ask**
- What are the 3 most common user flows?
- Which flow is most revenue-critical / most sensitive (biggest impact if it breaks)?
- Are there cross-system flows? Who's upstream, who's downstream?
- **Does this system proactively push notifications or alerts to users?**
  If yes, notification fatigue is a product design problem that must be solved at the architecture level — it cannot be retrofitted later:

  ```
  NOTIFICATION FATIGUE SPECTRUM
  ═══════════════════════════════════════════════════════════════

  Too few alerts              Balanced                Too many alerts
       │                         │                         │
       ▼                         ▼                         ▼
  Users miss the event     Users act on alerts       Users ignore or
  they cared about         that are relevant         unsubscribe; worst
  "Why didn't it alert     and timely                case: uninstall app
   me?"
  ═══════════════════════════════════════════════════════════════

  Design questions:
  • What conditions make a notification genuinely valuable to the user?
  • What's the maximum number of notifications a user should receive per day/week?
  • Should users be able to configure their own frequency/sensitivity?
  • What happens if the same triggering condition occurs repeatedly in a short window?
    (e.g., price crosses threshold, recovers, crosses again — 3 alerts or 1?)
  • How do we measure whether our notifications are creating value vs. annoyance?
    (engagement rate, unsubscribe rate, re-subscribe rate)
  ```

  The answers shape deduplication windows, cooldown logic, user preference models, and the notification rate-limiting architecture.

**Decide**
- Which paths require ultra-low latency / ultra-high availability
- Which paths can tolerate eventual consistency / degradation
- Notification rate limits and deduplication strategy (if system sends alerts)

**Deliver**
- Sequence diagrams (annotating sync/async boundaries)
- Critical path SLOs
- Notification value + fatigue design spec (if applicable)

### 1-4 Functional Requirements Inventory

**Ask**
- What are the core operations? CRUD? Batch? Search? Aggregation?
- What level of access control? RBAC? ABAC?
- Do we need audit trails? Which operations must be logged?
- Must features be real-time, or is eventually consistent acceptable?

**Decide**
- API style (REST / GraphQL / gRPC / hybrid)
- Sync vs. async split points

**Deliver**
- API list (with method, path, expected latency)
- Event list (with topic, schema, consumers)

---

## ② Traffic, Performance & Capacity

> This is the most commonly underestimated dimension. "We'll figure it out after launch" — famous last words.

### 2-1 Traffic Model

**Ask**
- Average QPS? Peak QPS? How long do peaks last?
- Are there event-driven bursts? (marketing campaigns, push notifications, back-to-school...)
- Traffic distribution: uniform or hotspots? Geographic spread? Timezone effects?
- Read/write ratio? (Does the typical 80/20 assumption apply?)
- **Does the system have fan-out patterns — where a single input event triggers a large number of downstream operations?**

  Fan-out is one of the most common causes of unexpected scale failures.
  A single event that looks like "1 write" at the input layer can become thousands of operations downstream:

  ```
  FAN-OUT PATTERN DETECTOR
  ═══════════════════════════════════════════════════════════════

  Examples of hidden fan-out:
  ──────────────────────────────────────────────────────────────
  System                Input               Fan-out
  ──────────────────────────────────────────────────────────────
  Price tracker         1 price change      → N users subscribed to that product
  Social media          1 celebrity post    → M followers' feeds to update
  Notification system   1 campaign trigger  → K users to notify
  E-commerce            1 flash sale start  → J users watching that item
  Chat app              1 message in group  → P members to deliver to
  ──────────────────────────────────────────────────────────────

  Key questions:
  • What's the maximum fan-out ratio? (1 event → how many downstream ops, worst case?)
  • Is this fan-out synchronous or asynchronous?
    Synchronous fan-out on the hot path will serialize and collapse under load.
    Asynchronous fan-out through a queue is the standard pattern.
  • Can the fan-out be batched? (send 1000 notifications per batch, not 1 at a time)
  • What's the SLA on fan-out completion? (all 200,000 users notified within 15 minutes?)
  ═══════════════════════════════════════════════════════════════
  ```

**Decide**
- Whether CDN / cache layer / queue is needed
- Auto-scaling strategy (CPU-based? queue-depth-based?)
- Hotspot protection (rate limit per key? distributed hash?)
- Fan-out strategy: synchronous vs. asynchronous; batch size; completion SLA (if applicable)

**Deliver**
- Capacity estimation sheet (including calculations and assumptions)
- Load test targets
- Fan-out topology diagram with worst-case multiplier (if applicable)

### 2-2 Latency Budget

**Ask**
- What are the user-perceivable p50 / p95 / p99 targets?
- How many hops in the full request chain? Which segment consumes the most latency?
- How much do external dependencies consume (third-party APIs, DNS, TLS handshake)?
- Serialization/deserialization cost? Payload size?

**Decide**
- Millisecond allocation per dependency (latency budget breakdown)
- Which work can be moved to async to shorten the synchronous path
- Whether precomputation is needed (precompute / materialized views)

**Deliver**
- Latency budget allocation table
- Request chain diagram (annotated with expected latency per segment)

### 2-3 Read/Write Ratio & Access Patterns

**Ask**
- Primarily read-heavy? Or write-intensive?
- Are there hot keys? (e.g., a single user/product queried extremely often)
- Do queries require sorting? Filtering? Full-text search? Aggregation?
- Do we need cross-table JOINs, or can we denormalize?

**Decide**
- Database type (KV / Relational / Document / OLAP / Time-series)
- Indexing strategy (which columns? composite indexes?)
- Whether read/write separation is needed

**Deliver**
- Data model (ERD or schema)
- Primary query list (with expected indexes)

### 2-4 Growth Curve & Limits

**Ask**
- Growth projections for 6 / 12 / 24 months?
- Which dimension grows fastest? (user count, request volume, data volume, tenant count)
- How far can the current design stretch? Where's the first bottleneck?

**Decide**
- Whether partitioning / sharding is needed
- Whether multi-tenant isolation is required
- When to move from single-node to distributed

**Deliver**
- Scaling roadmap (what to do and when, with trigger conditions)
- Bottleneck analysis + countermeasures

---

## ③ Data & Consistency

> Many incidents trace back here. "Eventually consistent" is easy to say, hard to get right.

### Pre-check: Identify the System Type First

Before diving into consistency questions, ask: **"Is this system primarily stateful or stateless computation?"**

This determines which questions are relevant.

```
SYSTEM TYPE DETECTOR
════════════════════════════════════════════════════════════

  "Does the system store and mutate shared state?"
           │
    ┌──────┴──────┐
   YES            NO
    │              │
    ▼              ▼
 Stateful      Stateless / Idempotent
 (orders,      (generators, converters,
  accounts,     hash services, renderers)
  inventory)
    │              │
    ▼              ▼
 Full ③         Skip most of ③
 discussion     Focus on:
 applies        • Cache strategy
                • Library version pinning
                  (same input must always
                   produce same output)
                • Idempotency (natural)
                • Bulk/async patterns

════════════════════════════════════════════════════════════
```

**For stateless / idempotent systems**, the key consistency question is different:

> "Does upgrading a dependency (library, algorithm, model) change the output for the same input?"
> If yes — how do you handle cache invalidation, versioned keys, and backward compatibility?

### 3-1 Consistency Requirements

**Ask**
- How soon after an update must everyone see the latest value?
- Is it acceptable to briefly see stale data? (e.g., user preferences vs. account balance)
- Cross-region / cross-service read consistency requirements?

**Decide**
- Strong consistency vs. eventual consistency (decide per data domain)
- Cache invalidation strategy (TTL / write-through / write-behind / cache-aside)
- Whether version numbers / compare-and-swap (CAS) are needed

**Deliver**
- Consistency spec table (e.g., "account balance: 99% visible within 1 second")
- Cache strategy document

### 3-2 Transactions & Atomicity

**Ask**
- Which business rules must NEVER be violated? (balance can't go negative, inventory can't oversell, no double-charging...)
- How many tables / services do these invariants span?
- Are there cross-service transaction requirements?
- **Does this system handle real or virtual money / credits / points transfers?**
  If yes, choose a money recording model before writing any code:

  ```
  MONEY RECORDING MODEL CHOICE
  ═══════════════════════════════════════════════════════════
  
  Option A — Mutable balance field
  ─────────────────────────────────────────────────────────
  UPDATE accounts SET balance = balance - 100 WHERE id = 1
  
  ✅ Simple to implement
  ❌ Hard to audit ("why is this user's balance $42?")
  ❌ Balance can silently drift from actual transactions
  ❌ No replay capability
  Suitable for: toy projects, internal points with no audit needs
  
  Option B — Immutable ledger (double-entry accounting)
  ─────────────────────────────────────────────────────────
  INSERT INTO ledger (from_acct, to_acct, amount, ref, type)
  VALUES ('user:1', 'escrow:order:99', 100, 'order_placed', ...)
  
  ✅ Every balance is a derived sum — always recomputable
  ✅ Full audit trail for free
  ✅ Every debit has a matching credit (total always balances to zero)
  ✅ Industry standard for financial systems
  ❌ More complex queries (balance = SUM of entries)
  ❌ Ledger table grows with every transaction
  Suitable for: any system where money integrity and auditability matter
  ═══════════════════════════════════════════════════════════
  ```

  Rule of thumb: if a regulator, auditor, or user could ever ask "prove my balance is correct" — use the ledger model.

**Decide**
- Single-database transactions (simple, reliable) vs. distributed transactions (avoid if possible)
- Saga pattern / Outbox pattern / 2PC (know when to use which)
- Compensation logic design
- Mutable balance vs. immutable ledger (double-entry) — decide before schema design

**Deliver**
- Invariant list (with protection mechanism for each)
- Transaction boundary diagram (which operations share a transaction)
- Money recording model decision + ledger schema (if applicable)

### 3-3 Idempotency & Retry Semantics

**Ask**
- Will clients resend requests? (network jitter, timeout-then-retry)
- Does the backend retry calls to downstream services?
- Will event consumers receive duplicate events?

**Decide**
- Idempotency key design (in header? body? who generates it?)
- Deduplication table / deduplication window
- at-least-once vs. at-most-once vs. exactly-once (and the real-world cost of each)

**Deliver**
- Retry strategy table for each API / event
- Idempotency specification document

### 3-4 Outbound Delivery Reliability & Delivery Contract

**Ask**
- **Does this system have an obligation to push data or events to external consumers (rather than serving inbound requests)?**

  This is the inverse of the typical inbound reliability problem. In a push-delivery system, *your* system owns the delivery SLA, even though the consumer's endpoint is outside your control:

  ```
  INBOUND vs. OUTBOUND RELIABILITY RESPONSIBILITY
  ═══════════════════════════════════════════════════════════════

  Inbound API (typical):
    Consumer → requests data → your system responds
    Failure mode: your system is down → consumer retries
    Your responsibility: your own uptime, latency, correctness

  Outbound Delivery (Webhook / Push Notification / ETL sink):
    Your system → pushes data to → consumer endpoint
    Failure mode: consumer endpoint unavailable → YOU must retry
    Your responsibility: guaranteed delivery even when the
                        consumer is flaky or intermittently down
  ═══════════════════════════════════════════════════════════════
  ```

  Core questions for outbound delivery systems:
  - What delivery semantic do you guarantee? (at-least-once / at-most-once / exactly-once)
  - Consumers may receive the same event twice — is deduplication their responsibility or yours?
  - What is your retry schedule when the consumer endpoint is unavailable?
  - After exhausting all retries (Dead Letter Queue), who owns the undelivered event — platform or consumer?
  - Can consumers request manual replay of a specific event range after recovery?
  - Does your retry logic create a "thundering herd" on a recovering endpoint
    (all backed-up retries firing simultaneously)?
  - How do you prevent one slow consumer endpoint from consuming all delivery worker capacity?
    (→ noisy neighbor problem; see 4-4 for the multi-tenant dimension)

- **What is the "retry storm" amplification factor under worst-case consumer outage?**
  ```
  Retry Storm Amplification Example
  ═══════════════════════════════════════════════════════════════
  Normal:   1,000 events/hr → 1,000 first-attempt deliveries
  Outage:   consumer down for 2 hours → 2,000 events queued
  Recovery: all 2,000 events retry simultaneously
            + 6 retry levels each → up to 12,000 attempts/hr spike
  Mitigation:
    • Exponential backoff with jitter (spread retry timing)
    • Per-consumer max retry rate (e.g., 1,000 retries/hr cap)
    • Circuit breaker: pause retries when endpoint is clearly down,
      resume with gradual ramp-up on recovery
  ═══════════════════════════════════════════════════════════════
  ```

**Decide**
- Delivery semantic (at-least-once is the practical standard; exactly-once requires consumer-side idempotency coordination)
- Retry schedule (exponential backoff + jitter is preferred over fixed interval)
- Dead letter queue ownership and consumer visibility (self-service retry UI?)
- Per-consumer circuit breaker + rate limit (isolates one slow consumer from the whole platform)
- Event immutability + replay window (how far back can consumers request replay?)

**Deliver**
- Delivery contract document (delivery semantic, retry schedule, DLQ policy, replay window)
- Consumer endpoint circuit breaker specification
- Retry storm analysis (max amplification factor under worst-case consumer outage)

### 3-5 Data Lifecycle

**Ask**
- How long must data be retained? Any regulatory requirements?
- Can data be hard-deleted, or must it be soft-deleted?
- How far back do queries need to reach?
- What's the access frequency difference between hot and cold data?

**Decide**
- Hot/warm/cold tiering strategy (e.g., 30 days hot, 1 year warm, then archive)
- TTL settings / partitioned tables (time-based partitioning)
- Archive format and query method

**Deliver**
- Data retention policy
- Storage cost estimate (including savings from tiering)

### 3-6 Data Quality & Traceability

**Ask**
- Do statistics / reports need to be auditable? (What if numbers don't add up?)
- Can all derived data be recomputed from raw events?
- Will event schemas evolve? How are versions handled?

**Decide**
- Raw event retention vs. rollup-only storage
- Whether replay capability is required
- Schema registry / versioning strategy (forward/backward compatibility)

**Deliver**
- Event schema definition + version evolution rules
- Recomputation process document (how to rebuild from raw)

---

## ④ Reliability, Failure Modes & Resilience

> Must-discuss for production. If you only think about this during incidents, it's too late.

### 4-1 SLO / SLI & Error Budget

**Ask**
- Availability target: 99.9% (~43 min downtime/month) or 99.99% (~4 min)?
- Do different features have different availability requirements? (core transactions vs. reports)
- What's the policy when error budget is exhausted? (freeze deployments?)

**Decide**
- Multi-AZ / multi-region deployment
- Degradation strategy (which features to shed first?)
- Engineering investment ratio (reliability vs. new features)

**Deliver**
- SLO document (with SLI definitions + measurement method)
- Alert thresholds (warning / critical / page)

### 4-2 Failure Mode Analysis (FMEA)

**Ask**
- If the DB goes down, what happens? What does the user see?
- If cache goes down — fail-open (hit DB) or fail-closed (return error)?
- If the queue fills up — are messages lost?
- If an external API becomes slow (not down, just 10x slower) — what's the impact?

**Decide**
- Fail-open / fail-closed policy for each dependency
- Graceful degradation order (which feature sheds first, which last)
- Whether fallback paths are needed

**Deliver**
- Failure drill checklist (expected behavior per scenario)
- Degradation matrix (features × failure scenarios)

### 4-3 Dependency Governance

**Ask**
- What's the timeout for each downstream service?
- How many retries? Retry interval? (Could this become a retry storm that crushes downstream?)
- Is there a circuit breaker? What path is taken when it opens?
- **Are there dependencies that, when unavailable, leave the system in an unresolvable intermediate state?**

  Most dependency failures are recoverable: the request fails, the user retries, life goes on.
  But some dependencies are *sources of external truth* — their unavailability doesn't just fail a request,
  it suspends the system in a state that can't be resolved by retrying:

  ```
  REGULAR DEPENDENCY FAILURE vs. TRUTH-SOURCE FAILURE
  ═══════════════════════════════════════════════════════════════

  Regular dependency (e.g., recommendations API):
    Unavailable → "We'll show default content" → User continues
    Recovery: immediate, automatic
  
  External truth source (e.g., market settlement oracle,
    shipping carrier "delivered" event, election result feed):
    Unavailable → System is stuck in limbo
                  (funds locked, order undeliverable, bet unsettled)
    Recovery: requires the external event to actually occur,
              OR a human override policy
  
  ═══════════════════════════════════════════════════════════════

  Examples of truth-source dependencies:
  • Prediction market / betting: "did team A win?" oracle
  • E-commerce: "was the package delivered?" carrier webhook
  • Insurance: "did the insured event occur?" claims adjuster
  • Escrow services: "did both parties confirm?" confirmation API
  • IoT / physical systems: "did the sensor trigger?" hardware event
  ```

  For each truth-source dependency, define:
  1. **Limbo timeout**: how long to wait before escalating?
  2. **Escalation path**: auto-refund? human review queue? customer notification?
  3. **Manual override**: who can force-resolve, and with what audit trail?

- **Does the system depend on an external data source that actively resists automated access?**

  This is distinct from a regular dependency or a truth-source dependency.
  The data source is not merely unavailable — it is *adversarially unavailable*:
  it detects and blocks automated access through technical and legal mechanisms.

  ```
  HOSTILE DATA SOURCE RISK PROFILE
  ═══════════════════════════════════════════════════════════════

  Characteristics of a hostile external data source:
  • Deploys anti-bot measures (CAPTCHAs, JS challenges, fingerprinting)
  • Rate-limits or IP-bans automated clients
  • Periodically changes HTML/API structure without notice (breaking parsers)
  • Prohibits automated access in Terms of Service
  • May take legal action (C&D letters, CFAA claims, civil suits)

  Common examples:
  ──────────────────────────────────────────────────────────────
  Service                   Hostile to scraping?
  ──────────────────────────────────────────────────────────────
  Amazon, eBay product data  Yes — ToS prohibition + active anti-bot
  LinkedIn profiles          Yes — aggressive legal enforcement
  Social media public feeds  Varies — many have restricted API access
  Real estate listings       Yes — many prohibit scraping
  Job postings               Varies
  Government / court data    Usually no — public record
  ──────────────────────────────────────────────────────────────

  Key questions:
  • Is there an official API or data partnership that provides the same data legally?
  • If scraping is the only option, what is the legal risk in the target jurisdiction?
  • What is the operational cost of maintaining scraper stealth
    (proxy pools, browser automation, CAPTCHA solving services)?
  • What happens to the service if the target site changes its structure?
    (silent failure? partial failure? full outage?)
  • Is there a monitoring strategy for parser health separate from service health?
  ═══════════════════════════════════════════════════════════════
  ```

**Decide**
- End-to-end timeout budget (not every layer can set 30 seconds)
- Circuit breaker strategy (how to probe recovery in half-open state)
- Bulkhead pattern (isolate thread pools / connection pools per dependency)
- Limbo timeout + escalation policy for any truth-source dependencies
- Official API vs. scraping decision + legal sign-off (for hostile data sources)

**Deliver**
- Dependency contract table (service, SLA, timeout, retry, breaker settings)
- Unified resilience configuration document
- Limbo state runbook (for each truth-source dependency, if applicable)
- Hostile data source risk assessment + access strategy (if applicable)

### 4-4 Backpressure, Overload Protection & Multi-tenant Isolation

**Ask**
- What happens when traffic exceeds capacity?
- Drop? Queue? Return 429/503?
- Do different clients / APIs have different priorities?

- **Does this system serve multiple tenants (customers/users) sharing the same underlying infrastructure?**

  If yes, the biggest reliability threat is often not a global failure — it's one tenant's behavior degrading the experience of all others (the "noisy neighbor" problem):

  ```
  MULTI-TENANT ISOLATION FAILURE MODES
  ═══════════════════════════════════════════════════════════════

  Failure Mode          Description                    Symptom for Other Tenants
  ──────────────────────────────────────────────────────────────────────────────
  Queue monopolization  Tenant A sends 1M events/hr    Tenant B's events delayed
                        and fills the shared queue     hours (or never delivered)

  Worker starvation     Tenant A's slow endpoints      All workers occupied retrying
                        absorb all delivery workers    Tenant A; Tenant B starves

  DB contention         Tenant A runs heavy batch      Query latency spikes for
                        queries on shared DB           all tenants

  Retry storms          Tenant A's endpoint goes       Retry amplification from
                        down and triggers mass         Tenant A floods the queue,
                        retries                        crowding out Tenant B

  ═══════════════════════════════════════════════════════════════

  Isolation mechanisms (choose based on risk level):
  ──────────────────────────────────────────────────
  Level 1 (Soft):   Per-tenant rate limits + per-tenant queue depth limits
  Level 2 (Medium): Per-tenant worker pool allocation (concurrent delivery slots)
  Level 3 (Hard):   Per-tenant circuit breakers (stop retrying a dead endpoint
                    without starving healthy tenants)
  Level 4 (Full):   Dedicated infrastructure per tenant (for enterprise/premium tier)
  ```

  Key design questions:
  - What is the maximum per-tenant queue depth? What happens when it's breached?
  - What is the per-tenant concurrency limit (max simultaneous delivery attempts)?
  - When a tenant's endpoint becomes slow, does it degrade the worker pool for all tenants?
  - Is there a per-tenant circuit breaker separate from the global circuit breaker?
  - Can tenants see their own isolation metrics? (queue depth, retry count, circuit state)
  - How do you detect and alert on noisy neighbor incidents before other tenants notice?

**Decide**
- Queue length limits + overflow strategy
- Fail-fast vs. queuing
- Tiered rate limiting (VIP clients / internal services / public API)
- Per-tenant isolation level (soft rate limit / per-tenant concurrency / dedicated infra)
- Per-tenant circuit breaker strategy (pause retries for one tenant without affecting others)

**Deliver**
- Overload strategy document
- Rate limiting rules (including retry-after header specification)
- Multi-tenant isolation architecture (with per-tenant limit table)
- Noisy neighbor detection runbook

### 4-5 Disaster Recovery (DR)

**Ask**
- Maximum acceptable data loss (RPO)? Minutes? Seconds? Zero?
- Service recovery time objective (RTO)?
- Has a DR drill been conducted? How often?

**Decide**
- Backup frequency + backup validation
- Cross-region replication strategy
- Drill frequency + drill scope

**Deliver**
- DR Runbook (step-by-step operations manual)
- Drill records + discovered issues

---

## ⑤ Security, Privacy & Compliance

> Frequently deferred until it explodes. Should be considered at design time.

### 5-1 Threat Model

**Ask**
- What are the attack surfaces? (public API, admin console, webhooks, OAuth redirects...)
- User authentication method? (OAuth, JWT, API key, session...)
- Authorization model? Who can do what? (RBAC / ABAC / resource-based)
- Is service-to-service communication authenticated? (mTLS, service tokens?)

**Decide**
- AuthN / AuthZ architecture
- Implementation of least-privilege principle
- Degree of zero-trust architecture

**Deliver**
- Threat list + countermeasures table (STRIDE framework works well)
- Authentication / authorization architecture diagram

### 5-2 Abuse Prevention

**Ask**
- Is brute force possible? (login, OTP, password reset)
- Scraping / volume abuse risk?
- Spam content / phishing / malicious redirects?
- Can users attack each other? (XSS, CSRF)
- **Can this service be weaponized to attack or harm third parties?**
  This is a distinct threat class often missed — the attacker isn't targeting *your* system, they're using your system as a tool:

  | Service Type | Weaponization Risk |
  |-------------|-------------------|
  | URL shorteners | Spreading malware / phishing behind a trusted domain |
  | QR code generators | Printing phishing QR codes for physical attacks |
  | Email / SMS senders | Spam, phishing campaigns |
  | Image / file converters | Hosting or distributing illegal content |
  | Webhook / callback services | Triggering requests against internal services (SSRF) |
  | PDF / screenshot renderers | SSRF via embedded URLs in content |

  Ask: "If a bad actor got free API access, what's the worst they could do *to someone else* using this service?"

- **Does this system involve trading, auctions, markets, or competitive resource allocation?**
  If yes, standard rate-limiting and brute-force defenses are not sufficient.
  Financial fraud patterns require *behavioral analytics*, not rule engines — because each individual action is legitimate; only the pattern is fraudulent:

  ```
  FINANCIAL FRAUD PATTERNS
  ═══════════════════════════════════════════════════════════════

  Pattern            Description                    Detection Signal
  ─────────────────────────────────────────────────────────────────
  Wash Trading       User trades with themselves    Graph: same user on
                     or colluding accounts to        both sides of a trade;
                     inflate volume artificially     buy/sell pairs from
                                                     linked accounts
  
  Front-running      Observing pending orders        Time delta: order
                     and inserting trades ahead      submission vs. execution
                     to profit from price impact     anomaly analysis
  
  Price Manipulation Large volume of small trades   Statistical: price
                     to move price to a favorable    deviation from expected
                     position before a large trade   fair value
  
  Sybil / Multi-acct Creating many accounts to      Device fingerprint,
                     extract bonuses or bypass       IP clustering, behavioral
                     per-account limits              similarity scoring
  
  Oracle Collusion   Bribing or manipulating the    Multi-oracle consensus;
  (prediction mkt)   entity that resolves outcomes   outcome dispute mechanism
  ─────────────────────────────────────────────────────────────────
  ```

  These require: transaction graph analysis, statistical anomaly detection, and human review queues — not just IP-based rate limiting.

**Decide**
- WAF rules
- Rate limit strategy (per IP / per user / per API key)
- Allow/deny lists / risk control rule engine
- Blocking + appeals process
- Content moderation or URL safety checks if the service processes user-supplied URLs or content
- Whether API keys are mandatory (anonymous access dramatically increases weaponization risk)
- For financial/trading systems: behavioral fraud detection strategy (graph analysis, statistical baselines, review queues)

**Deliver**
- Risk control strategy document
- Blocking rules + appeals SOP
- Weaponization threat assessment (if applicable)
- Financial fraud detection design (for trading/market/auction systems)

### 5-3 Secrets Management

**Ask**
- Where are API keys, DB passwords, encryption keys stored?
- Key rotation frequency? Automatic or manual?
- Who can read secrets? Is access audited?
- How are dev/test environment secrets managed?

**Decide**
- Secrets management solution (KMS / Secrets Manager / Vault)
- Rotation strategy (automatic rotation)
- Environment isolation

**Deliver**
- Key rotation policy
- Secrets access audit method

### 5-4 Privacy Minimization (Privacy by Design)

**Ask**
- Do we really need to store IP / User-Agent / geolocation?
- Can PII be hashed / truncated / anonymized?
- How long is the retention period? Regulatory requirements? (GDPR / local privacy laws)
- Can we fulfill data deletion requests?

**Decide**
- Data minimization principle implementation
- Anonymization / pseudonymization strategy
- Data retention period

**Deliver**
- PII inventory (which fields, where stored, how long retained)
- Data processing records (DPA / ROPA)
- Data deletion process

### 5-5 Compliance & Audit

**Ask**
- **Is this business model legally permitted in the target market?**

  This is the question technical teams most often skip — and the one with the highest architectural impact.
  Some systems require specific licenses or are outright prohibited in certain jurisdictions,
  and the answer completely reshapes the architecture *before* any other compliance question matters:

  ```
  BUSINESS LEGALITY PRE-CHECK BY DOMAIN
  ═══════════════════════════════════════════════════════════════

  Domain                   Key Regulatory Risk           Example Constraint
  ─────────────────────────────────────────────────────────────────────────
  Prediction markets /     Gambling laws; financial       License required or
  betting platforms        instrument regulations         banned outright in many
                                                          jurisdictions
  
  Fintech / payments       Payment services directive;    PSP license, AML/KYC
                           money transmission laws        program mandatory
  
  Healthcare data          HIPAA (US), GDPR health        Data residency, breach
                           category (EU)                  notification obligations
  
  AI / ML products         EU AI Act; sector-specific     High-risk AI requires
                           bias regulations               conformity assessment
  
  Crypto / digital assets  Securities law; AML;           May be unregistered
                           exchange licensing             securities offering
  
  Telemedicine             Medical device regulation;     May require FDA/CE
                           practice of medicine laws      clearance
  
  Encryption software      Export control (EAR/ITAR)     Prohibited in some
                           in some countries              countries or customer types
  ─────────────────────────────────────────────────────────────────────────
  ```

  Ask: "Have we confirmed with legal counsel that this product can operate in [target market]?"
  If the answer is no or uncertain — **this must be resolved before architecture decisions are made.**
  The required compliance level directly determines: KYC flows, data residency, audit depth, and reporting infrastructure.

- Which operations need audit trails? (who changed what, when?)
- Must audit logs be immutable? (WORM storage)
- Are there regulatory requirements? (SOC 2 / ISO 27001 / PCI DSS / HIPAA)

**Decide**
- Audit log architecture (synchronous write vs. asynchronous)
- Storage method (append-only / signed / external SIEM)
- Query tooling

**Deliver**
- Audit event schema
- Compliance mapping table

---

## ⑥ Architecture Shape & Operability

> It's not enough to build it — you have to keep it running.

### 6-1 Boundary Design (Service Decomposition / Modularization)

**Ask**
- Is it currently a monolith? Or already decomposed?
- If splitting, are boundaries drawn by domain (DDD bounded context) or by traffic / team?
- Is the RPC overhead from decomposition acceptable?
- Could "splitting too fine" cause distributed complexity to explode?

**Decide**
- Monolith-first or microservice-first
- Explicit bounded context definitions
- Inter-service communication method (sync REST/gRPC vs. async event)

**Deliver**
- Bounded context diagram
- Service dependency graph

### 6-2 Sync vs. Async Boundaries

**Ask**
- Which work can be deferred? (email, notifications, reports, recommendations...)
- Which must respond to the user in real-time?
- Retry / compensation strategy when async processing fails?

**Decide**
- Queue / stream technology choice (Kafka / SQS / RabbitMQ...)
- Outbox pattern (ensuring atomicity of DB write + event publish)
- How long is "eventually" in eventual consistency

**Deliver**
- Event-driven architecture diagram
- Event inventory (topic, schema, producer, consumer)
- Replay / retry strategy

### 6-3 Observability

**Ask**
- Can we pinpoint issues within 5 minutes of an incident?
- Is there distributed tracing? What's the sampling rate?
- Do logs contain PII? Should they be masked?
- Current monitoring coverage? Any blind spots?
- **Does the system include a crawler, scraper, or scheduled data-collection component?**
  If yes, standard web service observability is not sufficient.
  Crawlers have a distinct set of failure modes that require dedicated monitoring — many of which are *silent failures* (the system appears healthy while producing wrong data):

  ```
  CRAWLER-SPECIFIC OBSERVABILITY CHECKLIST
  ═══════════════════════════════════════════════════════════════

  Metric                    Why it matters
  ──────────────────────────────────────────────────────────────
  Parse success rate        Did we extract a valid price/value, or return null/garbage?
                            A site redesign causes this to drop without any HTTP errors.
                            Alert threshold: < 98% success rate over 15-min window.

  Data plausibility check   Is the extracted value within a reasonable range?
                            e.g., a product that was $500 yesterday shouldn't be $0.01 today.
                            Catches unit errors, currency mismatches, parsing bugs.

  Proxy pool health         Per-proxy success rate, ban rate, average latency.
                            A degraded proxy pool looks like slow crawls, not errors.

  Crawl queue depth         Are scheduled jobs completing within their time window?
                            A growing queue means crawlers are falling behind schedule.

  False alert rate          % of sent alerts where the price hadn't actually changed.
                            Catches parser bugs that produce noisy data downstream.

  Per-source freshness      For each data source: when was the last successful fetch?
                            Detects source-specific blocking without full outage.
  ──────────────────────────────────────────────────────────────

  Note: silent parser failures are more dangerous than outright crashes.
  A crashed crawler is immediately visible; a parser returning stale or wrong
  values can go undetected for days while users receive incorrect alerts.
  ═══════════════════════════════════════════════════════════════
  ```

- **Does the system include a persistent background delivery or processing worker (webhook delivery, notification dispatch, async job runners)?**
  If yes, inbound-request observability (latency, error rate, throughput) does not cover the worker tier.
  Background workers fail silently in different ways — the inbound metrics look fine while the work is piling up:

  ```
  SCHEDULED / ASYNC WORKER OBSERVABILITY CHECKLIST
  ═══════════════════════════════════════════════════════════════

  Metric                        Why it matters
  ──────────────────────────────────────────────────────────────
  Queue depth (per tenant)      Are jobs being processed faster than they're produced?
                                A growing queue = workers falling behind.
                                Per-tenant visibility catches noisy neighbor before it
                                becomes a global incident.

  Worker utilization            % of workers actively processing vs. idle.
                                < 30% idle capacity = risk of starvation under spike.
                                100% utilization = queue will start growing.

  Job age (oldest pending job)  How old is the oldest unprocessed item in the queue?
                                Latency p99 misses chronically-stuck jobs.
                                Alert if any item is older than X minutes.

  Delivery success rate         % of jobs completing successfully on first attempt.
                                Drop indicates endpoint health issue or payload bug.

  Retry depth distribution      What % of deliveries required 1 / 2 / 3+ attempts?
                                Increasing retry depth signals tenant endpoint degradation
                                before it saturates the worker pool.

  DLQ growth rate               How many jobs are being written to the Dead Letter Queue?
                                A sudden spike = systematic failure (bad payload, auth bug,
                                or a tenant endpoint returning 5xx for all events).

  Circuit breaker state         Per-tenant: CLOSED / HALF-OPEN / OPEN?
                                An open circuit means that tenant is receiving no deliveries.
                                Needs alert + consumer notification.

  End-to-end delivery latency   Time from event creation to successful consumer acknowledgment.
                                The SLA most consumers care about.
  ──────────────────────────────────────────────────────────────

  Note: the most common dangerous state is "queue growing slowly for hours" — all
  individual metrics look green (low error rate, workers busy) while delivery latency
  silently degrades. Queue age + depth are the leading indicators; error rate is lagging.
  ═══════════════════════════════════════════════════════════════
  ```

**Decide**
- Metrics / logging / tracing tool selection
- Sampling strategy (full capture vs. sampling vs. tail-based sampling)
- PII masking rules
- Parser health monitoring strategy and alert thresholds (for crawler systems)
- Queue depth + job age alerting thresholds + per-tenant circuit breaker visibility (for async worker systems)

**Deliver**
- Dashboard design (core metrics)
- Alert rules (with escalation path)
- Investigation SOP (step-by-step guide during incidents)
- Crawler health dashboard + plausibility validation rules (if applicable)
- Async worker health dashboard: queue depth, worker utilization, DLQ growth, delivery latency p50/p99/p999 (if applicable)

### 6-4 Deployment & Change Risk

**Ask**
- How do we deploy safely? (canary / blue-green / rolling)
- How fast is rollback? Is there automatic rollback?
- Feature flag management approach?
- How to do zero-downtime DB migrations?

**Decide**
- CI/CD pipeline design
- Canary strategy (traffic percentage, judgment criteria)
- Feature flag tool selection
- Migration forward/backward compatibility strategy

**Deliver**
- Release process document
- Rollback strategy + drill records
- Migration plan template

### 6-5 Testing Strategy

**Ask**
- Have load tests been run? What bottleneck was hit?
- Has chaos engineering been done? What faults were injected?
- How is synthetic traffic generated?
- Is there traffic replay capability?

**Decide**
- Load test tool and environment (production shadow? dedicated environment?)
- Fault injection scope and frequency
- Test data management

**Deliver**
- Load test report (bottlenecks + fix list)
- Chaos engineering drill plan

### 6-6 Data Migration, Compatibility & In-flight Async Task Migration

**Ask**
- How do we make zero-downtime schema changes?
- Will old clients still work? Forward/backward compatible?
- How to do large-scale backfills? Will it impact production?

- **Does this system have long-running or queued async tasks that will be in-progress during a deployment?**

  Stateless HTTP services can be restarted with near-zero ceremony — but stateful async systems (delivery workers, job queues, retry schedulers) have *work in progress* that may be in the middle of execution during a deployment:

  ```
  IN-FLIGHT ASYNC TASK MIGRATION PROBLEM
  ═══════════════════════════════════════════════════════════════

  Without a migration plan:

  Deploy v2 workers while v1 workers are processing
  ┌─────────────────────────────────────────────────────┐
  │  Queue contains:                                     │
  │  • 5,000 items in v1 format                         │
  │  • 500 items in v2 format (just enqueued)           │
  │                                                     │
  │  v2 worker starts — encounters v1 format item:      │
  │  → parse error → goes to DLQ → delivery lost         │
  │                                                     │
  │  v1 worker receives v2 format item:                 │
  │  → parse error → goes to DLQ → delivery lost         │
  └─────────────────────────────────────────────────────┘

  Risks:
  • Format incompatibility: v2 worker can't process v1 queue items
  • State incompatibility: v2 uses a new retry state machine that
    doesn't recognize v1 in-progress state records
  • Double processing: graceful shutdown of v1 workers while v2
    workers pick up the same items (no proper handoff)
  ═══════════════════════════════════════════════════════════════

  Strategies (choose based on risk tolerance):

  Strategy 1 — Drain before deploy (simplest, requires downtime window):
    Stop enqueuing → wait for queue to drain → deploy → resume
    Risk: downtime window. Acceptable for low-frequency batch systems.

  Strategy 2 — Versioned queue items (zero-downtime, recommended):
    Every queue item includes a schema_version field.
    Each worker version handles the versions it knows, requeues unknown versions.
    New version workers only enqueue new-format items.
    Gradual rollout: v2 workers drain v2 items; v1 workers drain remaining v1 items.

  Strategy 3 — Shadow processing + cutover:
    v2 workers run in shadow mode (consume but don't deliver) until verified,
    then v1 is retired.
    Risk: v1 and v2 fight over the same queue items.

  Strategy 4 — Separate queues for v1 and v2:
    New deployments write to a new queue; old workers drain the old queue.
    Cleanest isolation; operational complexity of managing queue lifecycle.
  ```

  Questions to ask:
  - What format do your current queue items use? Is the format versioned?
  - What happens if a new-version worker encounters an old-format item?
  - What happens if an old-version worker is still running and encounters a new-format item?
  - How long does it take to fully drain the queue under normal load?
  - Is there a graceful worker shutdown sequence (finish current job before dying)?
  - For retry schedulers: does the retry state machine schema change between versions?
    If yes, how does v2 handle a retry record created by v1?

**Decide**
- Dual-write / dual-read transition strategy
- API versioning strategy
- Feature flag for switching old/new paths
- Queue item schema versioning strategy (versioned payloads vs. separate queues vs. drain-first)
- Worker graceful shutdown strategy (ensure no job is abandoned mid-flight during deployment)

**Deliver**
- Migration plan (with validation steps and rollback procedures)
- Compatibility matrix
- In-flight task migration strategy (for async worker systems)
- Queue item schema version evolution rules

---

## ⑦ Cost & Organizational Reality

> The best architecture is useless if the team can't sustain it.

### 7-1 Cost Model

**Cost pattern hints by system type** — use this to focus the conversation before asking:

```
COST DRIVER BY SYSTEM TYPE
══════════════════════════════════════════════════════════

  System Type                  Typical Biggest Cost
  ─────────────────────────────────────────────────
  Media processing             Egress + storage
  (image/video/QR/PDF render)

  ML inference                 Compute (GPU/TPU)

  CRUD / transactional         DB ops + storage

  Search / analytics           Data warehouse query cost

  Message queue / event bus    Storage retention

  Stateless computation        Egress > compute
  (converters, generators)     (cache hit rate is the key lever)

  Real-time streaming          Network + compute

  Batch / ETL pipelines        Compute burst + storage

══════════════════════════════════════════════════════════
```

**Ask**
- Where's the biggest cost — compute, storage, egress, or data warehouse?
- What's the approximate cost per request / per customer?
- Are there runaway cost risks? (unbounded queries, large payloads, N+1 queries)

**Decide**
- Cache hit rate target (reduce DB/API calls)
- Data rollup / sampling (reduce storage)
- CDN / compression (reduce egress)
- Cost guardrails (budget alarms, hard limits)

**Deliver**
- Cost breakdown table (by component)
- Budget guardrails + alerts

### 7-2 Vendor / Technology Lock-in Risk

**Ask**
- If we need to switch cloud / DB / queue, how expensive is it?
- Are we using proprietary features? (AWS-specific APIs, GCP-only services...)
- Can data be exported? In a universal format?

**Decide**
- Whether an abstraction layer is needed (e.g., repository pattern, cloud-agnostic SDK)
- Which lock-in is "acceptable" (saves time) vs. must be avoided
- Data export / portability plan

**Deliver**
- Lock-in risk list + exit strategy (exit plan)

### 7-3 Team Capability & On-call Reality

**Ask**
- Who maintains this system? Dedicated team or shared?
- Who's on-call at 3 AM? How is the on-call rotation structured?
- Can a new hire understand the system within 1 week?
- Is the team familiar with these technologies, or is learning required?

**Decide**
- Choose mature technology vs. chase best-of-breed (team learning curve)
- Reduce component count (one fewer service = one fewer failure point)
- Runbook completeness requirements

**Deliver**
- On-call handbook
- Ownership matrix
- Technology stack decision rationale

### 7-4 Decision Records (ADR — Architecture Decision Records)

**Ask**
- Why did we choose A over B? Is the reasoning documented?
- Are the original assumptions still valid?
- Under what conditions should this decision be revisited?

**Decide**
- ADR format and storage location
- Review process

**Deliver**
- ADR documents (with: context, options, decision, rationale, risks, revisit conditions)

### 7-5 Lifecycle & Decommissioning

**Ask**
- What happens when a feature is sunset? How is data handled?
- How are downstream dependents notified / migrated?
- How is data deletion verified after decommissioning?

**Decide**
- Version sunset strategy (sunset notice, deprecation period)
- Data cleanup process
- Dependent service notification SOP

**Deliver**
- Decommissioning plan template
- Data deletion verification checklist

---

## Usage Tips

- You don't need to cover every item in every discussion
- Go deeper selectively based on system scale and complexity
- Mark inapplicable items as `N/A` with explanation
- Ask at least one question per dimension to confirm the user "has thought about it"
- When blind spots are found, use counterfactual questions ("What if X happens...")
