---
name: figma-readiness-audit
description: >-
  Analyze Figma designs via MCP to assess code-generation readiness across
  platforms (Web / Flutter / Windows). Outputs a designer-friendly report with
  quantified evidence, Figma fix steps, and per-platform Level A/B/C ratings.
  Primary audience is designers—helps them understand how their Figma decisions
  affect code composition and cross-platform consistency. Use when the user
  provides a Figma URL and asks about design quality, readiness, ambiguity,
  handoff completeness, design-engineering alignment, DS audit, or mentions
  "設計稿完整嗎", "夠不夠清楚", "有沒有模糊空間", "readiness", "Figma audit",
  "設計一致性", "Ready for Dev".
---

# Figma Readiness Audit

## Goal

> Turn "engineers can't read your design" into
> "here's exactly what to fix in Figma, step by step."

Three deliverables per finding:

1. **Make it visible** — quantified data from MCP
2. **Explain why** — in designer language, not code jargon
3. **Show how to fix** — Figma UI steps, not code commands

---

## Phase 1 — MCP Data Collection

**Budget: 2 mandatory calls + up to 2 optional calls.**
`get_design_context` already includes a screenshot — never call `get_screenshot`
separately. If any call returns a rate-limit error, jump immediately to
[Manual Audit Mode](#manual-audit-mode-rate-limit-fallback).

### Call 1 (mandatory): Design Context

```
get_design_context(fileKey, nodeId, clientLanguages="typescript,css", clientFrameworks="react")
```

Returns: screenshot + generated code + colors + fonts + spacing + asset URLs + annotations.
This single call covers visual reference, spec values, and D4/D5/D6 evidence.

If the response says the node is too large and returns only metadata →
also call `get_metadata(fileKey, nodeId)` to get the subtree, then pick
the key child nodeIds and call `get_design_context` on those instead.

### Call 2 (mandatory): Consolidated Audit Script

Run ONE `use_figma` call with this all-in-one script. It covers D1, D2, D3,
D4, and D5 in a single execution, costing only 1 MCP call instead of 5:

```javascript
// ── Scope: find the target node, audit descendants ──────────────────────
const TARGET_ID = '__NODE_ID__'; // replace with actual nodeId (colon format)
const root = figma.getNodeById(TARGET_ID) || figma.currentPage;

const all = 'findAll' in root ? root.findAll(() => true) : [];

// D1: Non-semantic names
const badNameRx = /^(Frame|Group|Rectangle|Ellipse|Vector|Line|Polygon|Star|Component)\s*\d*$/i;
const badNames = all.filter(n => badNameRx.test(n.name))
  .slice(0, 20).map(n => ({ id: n.id, name: n.name, type: n.type }));

// D2: Color Variable coverage
const fills = [];
all.filter(n => n.fills?.length).forEach(n => {
  n.fills.forEach(f => {
    if (f.type === 'SOLID')
      fills.push({ id: n.id, name: n.name, bound: !!f.boundVariables?.color });
  });
});
const colorTotal = fills.length;
const colorBound = fills.filter(f => f.bound).length;
const unboundSample = fills.filter(f => !f.bound).slice(0, 15)
  .map(f => ({ id: f.id, name: f.name }));

// D3: Variant sets + state coverage
const sets = ('findAllWithCriteria' in root)
  ? root.findAllWithCriteria({ types: ['COMPONENT_SET'] })
  : figma.currentPage.findAllWithCriteria({ types: ['COMPONENT_SET'] });
const variantSummary = sets.slice(0, 15).map(s => ({
  name: s.name, id: s.id, count: s.children.length,
  variants: s.children.slice(0, 10).map(c => c.name)
}));

// D4: Auto Layout coverage
const frames = all.filter(n => n.type === 'FRAME');
const alFrames = frames.filter(f => f.layoutMode !== 'NONE');
const absoluteSample = frames.filter(f => f.layoutMode === 'NONE')
  .slice(0, 15).map(f => ({ id: f.id, name: f.name }));

// D5: Text Style coverage
const texts = all.filter(n => n.type === 'TEXT');
const styledTexts = texts.filter(t => t.textStyleId && t.textStyleId !== '');

return {
  nodeInfo: { id: root.id, name: root.name, type: root.type,
    childCount: all.length },
  d1_naming: { badCount: badNames.length, total: all.length,
    badPct: all.length ? `${Math.round(badNames.length/all.length*100)}%` : 'n/a',
    sample: badNames },
  d2_colorVars: { total: colorTotal, bound: colorBound,
    coverage: colorTotal ? `${Math.round(colorBound/colorTotal*100)}%` : 'n/a',
    unboundSample },
  d3_variants: { setCount: sets.length, summary: variantSummary },
  d4_autoLayout: { frameTotal: frames.length, alCount: alFrames.length,
    coverage: frames.length ? `${Math.round(alFrames.length/frames.length*100)}%` : 'n/a',
    absoluteSample },
  d5_textStyles: { total: texts.length, styled: styledTexts.length,
    coverage: texts.length ? `${Math.round(styledTexts.length/texts.length*100)}%` : 'n/a' }
};
```

Replace `__NODE_ID__` with the actual nodeId in `1234:5678` format before running.

### Call 3 (optional): Variable Definitions

Only call if D2 color coverage is low and you need to cross-check which
Variables are defined vs what's actually used:

```
get_variable_defs(fileKey, nodeId)  → defined Variables (for D2/D9 cross-check)
```

### Call 4 (optional): Code Connect Suggestions

Only for DS Layer 3 (Components) audits:

```
get_code_connect_suggestions(fileKey, nodeId)  → D8 evidence
```

### Figma Make Context (optional)

If URL is `figma.com/make/...`, `get_design_context` already returns richer
interaction descriptions. Use these to supplement D4 (non-visual patterns).

---

## Manual Audit Mode (Rate-Limit Fallback)

When any MCP call returns a rate-limit error, switch to this mode.
Ask the designer to open the node in Figma and self-check:

| # | Open in Figma | Check | Pass if |
|---|---|---|---|
| D1 | Layers panel | Layer names | No `Frame N`, `Group N`, `Rectangle N` |
| D2 | Right panel → Fill | Color swatch | Variable icon visible (not bare hex) |
| D3 | Component set | Variants list | Includes hover / focus / disabled |
| D4 | Right panel → Layout | Frame mode | "Horizontal" or "Vertical" (not None) |
| D5 | Right panel → Text | Style field | Shows a named style (not blank) |
| D6 | Right panel → Export | Export settings | Has at least 1 format (SVG/PNG) |
| D7 | Dev Mode | Visible frames | Only delivery content, no WIP |

Produce a partial report based on whatever MCP data was collected before
the limit was reached, clearly marking which dimensions have MCP evidence
vs which are marked ⚠️ MCP unavailable (manual check recommended).

---

## Phase 2 — Three-Tier Analysis

### Tier 0: DS Layer Positioning

Before scoring, determine where this design sits in the DS hierarchy.
This decides which Tier 1 dimensions apply.

| DS Layer | Examples | Audit Focus |
|---|---|---|
| 1 Tokens/Foundations | Color, spacing, type scale | Variable naming, semantic vs raw |
| 2 Primitives | Box, Stack, Text | Simple structure, no biz logic |
| 3 Components | Button, Input, Modal | Variants, States, Code Connect |
| 4 Patterns | Filter panel, Form layout | Task completeness, cross-product reuse |
| 5 Templates | Dashboard, List-detail | Page skeleton, content zones labeled |
| 6 Product Modules | Domain-specific modules | Spec completeness (relaxed DS bar) |
| 7 Experiment/Local | Exploration drafts | Suggest Figma Make first, defer formal audit |

**How to determine**: Inspect `get_metadata` structure + `get_design_context`
content. If Layer 7, output a notice:
> "This looks like an exploration draft. Consider using Figma Make to validate
> interactions first, then re-run this audit on the converged design."

### Tier 1: Design System Quality (10 dimensions)

Score each: 🔴 Blocker / 🟡 Ambiguity / 🟢 Clear / ⬜ N/A (per DS layer)

**D1 Semantic Naming**
- Layer names purpose-oriented (`Button/Primary`) vs appearance-oriented (`Frame1`)?
- Component taxonomy follows convention (`ui/button`, `section/hero`)?
- Evidence: `use_figma` non-semantic name count + percentage

**D2 Token/Variable Coverage**
- Colors/spacing/fonts use Variables / Named Text Styles (not raw hex/px)?
- Alias chains traceable (not endless indirection)?
- Evidence: `use_figma` Variable coverage %; `get_variable_defs` cross-check

**D3 States Completeness**
- Covers: default / hover / focus / active / disabled / selected / loading / error / empty
- "No hover yet" = engineers guess
- Evidence: `use_figma` variant listing per component set

**D4 Non-Visual Patterns**
- Auto Layout direction + gap reflected in frame structure?
- Content source annotations (CMS / API / static / brand asset)?
- Complex interaction rules documented (conditions, plan variants, permissions)?
- Evidence: `get_design_context` annotations; Figma Make interaction descriptions

**D5 Typography**
- Named Text Styles used (not raw font-size + weight)?
- Fonts available (Google Fonts / system / licensed)?
- Evidence: `use_figma` Text Style coverage %

**D6 Assets**
- Icons/images marked exportable? Format (SVG vs raster)?
- Brand assets have source annotation?
- Evidence: `get_design_context` asset URLs present or absent

**D7 Handoff Readiness**
- Sections marked Ready for Dev?
- Dev Mode focus view shows minimal necessary context?
- Exploration vs delivery frames separated?

**D8 Code Connect (bonus)**
- Core components have Code Connect snippets to codebase?
- `get_code_connect_suggestions` returns actionable mappings?

**D9 Token Platform Syntax (bonus)**
- Core tokens have platform code syntax (CSS var / Flutter const / WinUI resource)?
- Light/dark mode aliases traceable to final values?

**D10 Accessibility Foundations**
- Color contrast meets WCAG AA (text 4.5:1, large 3:1)?
- Focus state designed (not just hover)?

### Tier 2: Platform Readiness (Level A / B / C)

**Web — target Level A (full generation)**

| Check | Source |
|---|---|
| Auto Layout → Flexbox (no absolute) | D4 + use_figma |
| Variable coverage ≥ 80% | D2 |
| Variants + States complete | D3 |
| Responsive breakpoints specified | D4 |
| Fonts web-available | D5 |

Downgrade: D1/D2/D3 Blocker → B; ≥ 3 Blockers → C

**Flutter — target Level B (skeleton generation)**

| Check | Source |
|---|---|
| Frame structure → Row / Column / Stack | D4 + use_figma |
| Component boundaries clear | D1 |
| Constraint / Expanded behavior annotated | D4 |
| Spacing → EdgeInsets | D2 |

Downgrade: all names non-semantic + all absolute → C

**Windows — target Level C (spec generation)**

| Check | Source |
|---|---|
| Component anatomy (leading / content / trailing) | D1 |
| States clearly defined | D3 |
| Token names → Resource Dictionary | D2 |
| Size / spacing specs complete | D4 |

Downgrade: all names `Frame1/Group1` + no Variables → cannot generate valid spec

---

## Phase 3 — Report Generation

Use the template below. Every finding MUST include at least 2 MCP evidence
sources. See [CHECKLIST.md](CHECKLIST.md) for detailed scoring rules.

### Finding Card Format

```
### 🔴 D2-001 [Short title in designer language]

**What does this mean?**
[1–3 sentences, designer language, no code jargon.
Explain how this Figma decision causes problems for engineers / across platforms.]

**Evidence (from MCP)**
- use_figma: [quantified stat, e.g. "47/63 fills (75%) are raw hex"]
- get_variable_defs: [cross-check detail]
- Affected nodes: [node names + IDs, clickable in Figma]

**Screenshot**
[get_screenshot image of the affected area]

**How to fix in Figma**
1. [Click where]
2. [Select what]
3. [Confirm / bulk tool suggestion]

**Figma Make note** (if applicable)
[Interaction context that helps ensure the fix matches design intent]
```

### Full Report Template

```markdown
# Figma Design Consistency Report

> Target: [node name]
> DS Layer: [Token / Component / Pattern / Template / Product Module / Experiment]
> Platforms: Web / Flutter / Windows

---

## At a Glance

[1–2 sentence designer-language summary]
[If Experiment/Local: note to converge via Figma Make before formal handoff]

### Platform Readiness
| Platform | Level | Key Bottleneck |
|----------|-------|----------------|
| Web      | A/B/C | ...            |
| Flutter  | A/B/C | ...            |
| Windows  | A/B/C | ...            |

### Design System Maturity (Tier 1)
| Dimension          | Status      | Issue |
|--------------------|-------------|-------|
| D1 Naming          | 🔴/🟡/🟢/⬜ | ...   |
| D2 Tokens          | 🔴/🟡/🟢/⬜ | ...   |
| D3 States          | 🔴/🟡/🟢/⬜ | ...   |
| D4 Non-Visual      | 🔴/🟡/🟢/⬜ | ...   |
| D5 Typography      | 🔴/🟡/🟢/⬜ | ...   |
| D6 Assets          | 🔴/🟡/🟢/⬜ | ...   |
| D7 Handoff Ready   | 🔴/🟡/🟢/⬜ | ...   |
| D8 Code Connect    | 🟢/⬜       | ...   |
| D9 Token Syntax    | 🟢/⬜       | ...   |
| D10 Accessibility  | 🔴/🟡/🟢/⬜ | ...   |

---

## Designer Action Items

### 🔴 Must Fix (affects all platforms)
[Finding cards with evidence + Figma steps]

### 🟡 Should Improve (works now, problems later)
[Finding cards]

### 🟢 Well Done (keep doing this)
[Positive feedback on good practices found]

---

## Engineer Notes
[Reasonable assumptions while waiting for designer fixes;
things engineers should NOT start on yet]

---

## Next Steps
- Designer: prioritize 🔴 list; estimated fix effort
- Engineer: which platforms can start now / which must wait
```

---

## Additional Resources

- Detailed scoring rules and Level upgrade/downgrade conditions:
  [CHECKLIST.md](CHECKLIST.md)
- This skill is a pre-step to [figma-to-react](../figma-to-react/SKILL.md)
  and [figma-assets-only](../figma-assets-only/SKILL.md)
