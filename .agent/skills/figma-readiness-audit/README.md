# Figma Readiness Audit

**Help designers understand how their Figma decisions affect code — before handoff, not after.**

---

## The Problem

A designer hands off a Figma file. Three platform teams (Web, Flutter, Windows) start building. Each team independently guesses:

- "Is `#2D6BE4` the primary color or just something they picked?"
- "There's no hover state — should I make one up?"
- "This layer is called `Frame 47` — what is it?"

Result: three platforms ship three different interpretations of the same design. The designer didn't know this would happen.

## What This Skill Does

It runs a structured analysis of any Figma design using Figma MCP tools, then outputs a **designer-friendly report** that:

1. **Shows problems with data** — "75% of your colors are raw hex, not Variables"
2. **Explains why it matters** — in designer language, not code jargon
3. **Gives Figma fix steps** — click here, select this, done
4. **Rates each platform** — Web can reach Level A, Flutter B, Windows C

---

## Who Should Use This

| Role | When to Use |
|------|-------------|
| **Designer** | Before handoff: "Is my design clear enough for engineers?" |
| **Engineer** | Before implementation: "Can I start, or do I need to wait for fixes?" |
| **PM** | Sprint planning: "How aligned are design and engineering on this feature?" |

---

## How It Works

```
Figma URL
    |
    v
+---------------------------+
| Phase 1: MCP Data Collect |  get_screenshot, get_metadata,
|   (4 stages)              |  get_design_context, get_variable_defs,
|                           |  use_figma (programmatic queries),
|                           |  Figma Make context (optional)
+---------------------------+
    |
    v
+---------------------------+
| Phase 2: Three-Tier       |
|   Analysis                |
|                           |
|  Tier 0: DS Layer (Token? |
|    Component? Pattern?)   |
|  Tier 1: Design System    |
|    Quality (10 dims)      |
|  Tier 2: Platform Level   |
|    (A / B / C)            |
+---------------------------+
    |
    v
+---------------------------+
| Phase 3: Report           |
|  - Designer action items  |
|  - Evidence per finding   |
|  - Figma fix steps        |
|  - Engineer notes         |
+---------------------------+
```

---

## Platform Levels Explained

| Level | What it means (designer language) |
|-------|-----------------------------------|
| **A** | "Your design is so clear I barely need to guess. I can generate working UI directly." |
| **B** | "I can build the skeleton — layout, components, spacing — but I'll fill in details myself." |
| **C** | "I can produce a spec — sizes, colors, states — but engineers write the code by hand." |

Typical targets:

- **Web** → Level A (full generation)
- **Flutter** → Level B (skeleton generation)
- **Windows** → Level C (spec generation)

---

## DS Layer Positioning

The audit first determines where your design sits in the Design System hierarchy (layers 1–7). This changes which checks apply:

| Layer | What | Audit Focus |
|-------|------|-------------|
| 1 Tokens | Color, spacing, type scale | Variable naming, semantic vs raw |
| 2 Primitives | Box, Stack, Text | Simple structure |
| 3 Components | Button, Input, Modal | Variants, States, Code Connect |
| 4 Patterns | Filter panel, Form layout | Task completeness |
| 5 Templates | Dashboard, List-detail | Page skeleton, content zones |
| 6 Product Modules | Domain-specific | Spec completeness (relaxed bar) |
| 7 Experiment | Exploration drafts | Use Figma Make first, then audit |

---

## Report Example (Finding Card)

```markdown
### 🔴 D2-001 Colors not bound to Variables

**What does this mean?**
Some colors in your design are filled with raw hex `#2D6BE4` instead of
selecting `color/primary` from the Variables panel. Each platform's engineers
must independently guess which design token this hex maps to. Web might guess
right, Flutter might guess wrong, Windows picks something else.
Result: three platforms show three different colors, and you won't know.

**Evidence (from MCP)**
- use_figma: 47 of 63 fills (75%) are raw hex; only 16 (25%) bound to Variables
- get_variable_defs: `color/primary = #2D6BE4` is defined but 12 nodes
  use the raw hex instead of binding
- Affected: Button/Primary (2:45), Card/Header (3:12), Tag/Active (4:89)

**How to fix in Figma**
1. Select `Button/Primary` in the layers panel
2. Right panel → Fill → click the hex swatch → switch to "Variables" mode
3. Select `color/primary` → confirm
4. Repeat for all affected nodes, or use plugin "Variable Swapper" for bulk replace
```

---

## Figma Make Support

If the URL is a Figma Make file (`figma.com/make/...`), the audit extracts
additional interaction descriptions — component purposes, section semantics,
user flow annotations. This helps:

- Supplement **D4 (Non-Visual Patterns)** with interaction intent
- Guide designers when converging exploration into formal handoff
- Ensure fixes align with the original interaction design

For **Layer 7 (Experiment)** designs, the audit will recommend using Figma Make
to validate interactions before running a formal readiness check.

---

## Relationship to Other Skills

```
figma-readiness-audit (this skill)
    |
    |-- Pre-step to:
    |     figma-to-react (Web Level A implementation)
    |     figma-assets-only (asset download rules)
    |
    |-- Informs:
          Flutter skeleton generation (Level B)
          Windows spec generation (Level C)
```

---

## Trigger Phrases

**Designer-initiated** (primary use case):
- "Is my design clear enough for engineers?"
- "What do I need to fix before handoff?"
- "Design review", "design consistency check"

**Handoff check**:
- "Ready for Dev?", "Can we start implementing?"
- "What's missing?", "Is the design complete?"

**Cross-platform alignment**:
- "Can Flutter use this design?"
- "Are Web / Windows / Flutter specs consistent?"
- "Token alignment", "design-engineering alignment"

**DS quality**:
- "Which DS layer does this belong to?"
- "Are my token names reasonable?"

---

## Self-Check Checklist (18 items)

Before requesting an audit, designers can self-check:

### Design System Foundations
- [ ] Key components use the design system (not ad-hoc assembly)
- [ ] Variable names describe purpose, not just appearance
- [ ] At least main states defined: default / hover / disabled / selected / loading
- [ ] Important content sections have source labels (CMS / API / static / brand asset)
- [ ] Important images/brand assets have source annotations

### Annotations & Handoff
- [ ] Complex interactions have annotations explaining conditions
- [ ] Key layer names understandable by an unfamiliar engineer
- [ ] Delivery sections marked as Ready for Dev
- [ ] Dev Mode focus view shows only minimum necessary context

### Code Connection
- [ ] Core components mapped to codebase files or Code Connect snippets
- [ ] Core tokens have platform code syntax documented
- [ ] Light / dark mode token aliases verified

### AI / Agent Readiness
- [ ] Agent instructions specify "use existing components first"
- [ ] Agent instructions list prohibited patterns
- [ ] AI workflow has a fixed data-fetching order
- [ ] First AI output goes through type/props correction

### Process
- [ ] AI common errors written back to team documentation
- [ ] Post-handoff: tracking follow-up question count and correction volume

---

## FAQ

**Q: My design doesn't use Variables at all. Can I still run this?**
A: Yes. The audit will flag it as a Blocker and show you exactly how to add
Variables, starting with the highest-impact colors.

**Q: I only target Web. Do I need Flutter/Windows analysis?**
A: No. Tell the agent which platforms you care about. It will skip the rest.

**Q: Is Code Connect required?**
A: No. D8 and D9 are bonus dimensions. They improve the score but their
absence is not a Blocker.

**Q: What about Experiment/exploration designs?**
A: The audit detects Layer 7 designs and recommends using Figma Make to
validate interactions first, then re-running on the converged design.

**Q: Is this report for designers or engineers?**
A: Primarily designers. The "Engineer Notes" section at the bottom is for
engineers. Everything else is written in designer language.

---

## Files

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Main workflow (< 500 lines) |
| [CHECKLIST.md](CHECKLIST.md) | Detailed scoring rules, Level conditions, 18-item self-check |
| [README.md](README.md) | This file (English) |
| [README_TW.md](README_TW.md) | Traditional Chinese version |
