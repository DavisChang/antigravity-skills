# Figma Readiness Audit — Scoring Rules & Checklist

## How Scoring Works

Each Tier 1 dimension gets one rating:

| Rating | Meaning | Action |
|--------|---------|--------|
| 🔴 Blocker | Cannot produce correct code; designer must fix | Block handoff |
| 🟡 Ambiguity | Engineers must guess; clarification recommended | Proceed with assumptions documented |
| 🟢 Clear | Information complete; can generate directly | No action needed |
| ⬜ N/A | Does not apply to this DS layer | Skip |

---

## Tier 0 — DS Layer Positioning

Before scoring Tier 1, determine the DS layer. This affects which dimensions
are required vs optional.

### Decision Tree

1. Is this a **global visual rule** (color, spacing, type scale, radius)?
   → Layer 1: Tokens/Foundations
2. Is this a **single structural primitive** with no business semantics?
   → Layer 2: Primitives
3. Is this a **single interactive unit** (Button, Input, Modal)?
   - Reusable across products, no business logic? → Layer 3: Core Component
   - Product-specific? → Layer 6: Product Module
4. Does it solve a **complete user task or flow**?
   - Reusable across products? → Layer 4: Pattern
   - Product-specific? → Layer 6: Product Module
5. Is it a **page skeleton or information layout**?
   → Layer 5: Template
6. Still exploring, not yet stable?
   → Layer 7: Experiment/Local

### Dimension Applicability by Layer

| Dimension | L1 Token | L2 Prim | L3 Comp | L4 Pattern | L5 Template | L6 Product | L7 Experiment |
|-----------|----------|---------|---------|------------|-------------|------------|---------------|
| D1 Naming | Required | Required | Required | Required | Required | Required | ⬜ Skip |
| D2 Tokens | Required | Required | Required | Required | Required | 🟡 Relaxed | ⬜ Skip |
| D3 States | ⬜ Skip | ⬜ Skip | Required | Required | 🟡 Relaxed | 🟡 Relaxed | ⬜ Skip |
| D4 Non-Visual | ⬜ Skip | ⬜ Skip | 🟡 Relaxed | Required | Required | Required | ⬜ Skip |
| D5 Typography | Required | ⬜ Skip | Required | Required | Required | 🟡 Relaxed | ⬜ Skip |
| D6 Assets | ⬜ Skip | ⬜ Skip | Required | Required | Required | Required | ⬜ Skip |
| D7 Handoff | ⬜ Skip | ⬜ Skip | Required | Required | Required | Required | ⬜ Skip |
| D8 Code Connect | ⬜ Skip | ⬜ Skip | Bonus | Bonus | ⬜ Skip | ⬜ Skip | ⬜ Skip |
| D9 Token Syntax | Bonus | ⬜ Skip | Bonus | ⬜ Skip | ⬜ Skip | ⬜ Skip | ⬜ Skip |
| D10 A11y | Required | ⬜ Skip | Required | Required | Required | 🟡 Relaxed | ⬜ Skip |

---

## Tier 1 — Detailed Scoring Rules

### D1 Semantic Naming

**MCP Evidence**: `use_figma` non-semantic name scan + `get_metadata` layer tree

| Rating | Condition |
|--------|-----------|
| 🔴 Blocker | > 50% of frames/components named `Frame N`, `Group N`, `Rectangle N` |
| 🟡 Ambiguity | 20–50% non-semantic names, or names are appearance-based (`blue-btn`) |
| 🟢 Clear | < 20% non-semantic; follows taxonomy (`ui/button`, `section/hero`) |

**Designer fix guidance**:
1. Select layer → double-click name → rename to purpose (e.g. `Card/Header`)
2. Adopt naming convention: `{category}/{name}` — e.g. `ui/button`, `layout/sidebar`
3. Bulk rename: use Figma plugin "Rename It" with pattern rules
4. Test: have a colleague read 10 names without seeing the design — can they guess purpose for ≥ 8?

---

### D2 Token / Variable Coverage

**MCP Evidence**: `use_figma` color/spacing Variable coverage; `get_variable_defs` cross-check

| Rating | Condition |
|--------|-----------|
| 🔴 Blocker | Variable coverage < 30% for colors (mostly raw hex everywhere) |
| 🟡 Ambiguity | 30–80% coverage; Variables defined but many nodes not bound |
| 🟢 Clear | ≥ 80% coverage; alias chains ≤ 2 levels deep |

**Designer fix guidance**:
1. Open Variables panel → verify collections exist (color, spacing, etc.)
2. Select unbound node → Fill → click hex swatch → switch to Variables mode → bind
3. Bulk bind: use plugin "Variable Swapper" or "Tokens Studio"
4. Alias depth check: click a variable → trace aliases → ensure ≤ 2 hops to final value

---

### D3 States Completeness

**MCP Evidence**: `use_figma` component set variant listing

Required states (check all that apply to the component type):

| State | When Required |
|-------|---------------|
| default | Always |
| hover | Any interactive element |
| focus | Any keyboard-interactive element |
| active / pressed | Buttons, links, toggles |
| disabled | Any element that can be disabled |
| selected | Tabs, toggles, list items, checkboxes |
| loading | Anything that fetches data |
| error | Form inputs, submission states |
| empty | Lists, tables, search results |

| Rating | Condition |
|--------|-----------|
| 🔴 Blocker | Only default state exists for interactive components |
| 🟡 Ambiguity | Has some states but missing ≥ 2 relevant ones (e.g. no focus, no empty) |
| 🟢 Clear | All relevant states designed as Variants |

**Designer fix guidance**:
1. Select component set → add new Variant for each missing state
2. Use Figma property: add a "State" property with values (default, hover, focus, ...)
3. For empty/loading/error: create at least 1 representative variant
4. Test: list all interactive elements and check each against the state table above

---

### D4 Non-Visual Patterns

**MCP Evidence**: `get_design_context` annotations; `get_metadata` frame structure; Figma Make context

| Rating | Condition |
|--------|-----------|
| 🔴 Blocker | Key interactive sections have zero annotations for data source or logic |
| 🟡 Ambiguity | Some annotations, but content source (CMS / API / static) not labeled |
| 🟢 Clear | Auto Layout structure matches intent; content sources labeled; interaction rules annotated |

**Designer fix guidance**:
1. For layout: ensure every container uses Auto Layout (not absolute positioning)
2. For content: add annotation per section — "Source: CMS", "Source: API /products", "Static"
3. For interactions: annotate conditional logic — "Shows Plan A price if user.plan === 'A'"
4. Use Figma comments or a dedicated annotation component from your DS

---

### D5 Typography

**MCP Evidence**: `use_figma` Text Style coverage; `get_design_context` font names

| Rating | Condition |
|--------|-----------|
| 🔴 Blocker | < 30% of text nodes use Named Text Styles; fonts not on Google Fonts or not licensed |
| 🟡 Ambiguity | 30–80% Text Style coverage; fonts available but inconsistent usage |
| 🟢 Clear | ≥ 80% coverage; all fonts available on target platforms |

**Designer fix guidance**:
1. Select text → right panel → Style dropdown → choose existing Text Style
2. If no style matches → create one following convention: `Heading/H1`, `Body/Regular`
3. Check font availability: Google Fonts for Web; system fonts for mobile

---

### D6 Assets

**MCP Evidence**: `get_design_context` asset URLs; `get_metadata` exportable flags

| Rating | Condition |
|--------|-----------|
| 🔴 Blocker | Key icons/images have no asset URL and no export settings |
| 🟡 Ambiguity | Some assets present but format unclear (raster where SVG expected) |
| 🟢 Clear | All icons SVG-exportable; images have asset URLs; brand assets annotated |

**Designer fix guidance**:
1. Select icon → right panel → Export → add SVG format
2. For images: ensure they appear in `get_design_context` asset list
3. For brand assets: add annotation with source (e.g. "Brand kit / logo-primary.svg")

---

### D7 Handoff Readiness

**MCP Evidence**: `get_metadata` structure analysis

| Rating | Condition |
|--------|-----------|
| 🔴 Blocker | No clear separation between exploration and delivery; entire canvas is "the design" |
| 🟡 Ambiguity | Some sections clearly done but not marked; exploration frames mixed in |
| 🟢 Clear | Ready sections marked; exploration separated; Dev Mode focus view clean |

**Designer fix guidance**:
1. Move exploration/WIP to a separate page named "Exploration" or "WIP"
2. Mark delivery frames with a status — e.g. rename `[Ready] Login Page`
3. In Dev Mode: set focus view to only include delivery section
4. Run 10-min naming audit before handoff: check 10 layers, ≥ 9 self-explanatory

---

### D8 Code Connect (Bonus)

**MCP Evidence**: `get_code_connect_suggestions`

| Rating | Condition |
|--------|-----------|
| 🟢 Clear | Core components have Code Connect snippets; mapping suggestions available |
| ⬜ N/A | Not set up yet (recommend as improvement, not a blocker) |

**Designer fix guidance**:
1. Work with engineering to identify top 10 reused components
2. Set up Code Connect for those 10 first
3. Use `get_code_connect_suggestions` to find additional mapping candidates

---

### D9 Token Platform Syntax (Bonus)

**MCP Evidence**: `get_variable_defs` token names; manual cross-check with codebase

| Rating | Condition |
|--------|-----------|
| 🟢 Clear | Core tokens have CSS variable / Flutter const / WinUI resource syntax documented |
| ⬜ N/A | Not yet set up |

**Designer fix guidance**:
1. For top 15 color tokens: ensure CSS variable name is in token description
2. Use Tokens Studio or similar tool to auto-generate platform syntax
3. Verify light/dark mode aliases resolve correctly on each platform

---

### D10 Accessibility Foundations

**MCP Evidence**: `get_design_context` color values (compute contrast); state analysis from D3

| Rating | Condition |
|--------|-----------|
| 🔴 Blocker | Primary text-on-background fails WCAG AA 4.5:1 |
| 🟡 Ambiguity | Most contrasts pass but some secondary combinations untested; no focus state |
| 🟢 Clear | All key pairs meet AA; focus state designed; touch targets ≥ 44px |

**Designer fix guidance**:
1. Use Figma plugin "Stark" or "A11y - Color Contrast Checker" on key text/bg pairs
2. Add a `:focus` variant to every interactive component (visible ring/outline)
3. Verify touch targets: interactive elements ≥ 44×44px

---

## Tier 2 — Platform Level Upgrade/Downgrade Rules

### Level Definitions (Designer Language)

| Level | What it means |
|-------|---------------|
| **A** | "Your design is so clear I barely need to guess. I can generate working UI directly." |
| **B** | "I can build the skeleton — layout, components, spacing — but I'll need to fill in details myself." |
| **C** | "I can produce a spec document — sizes, colors, states — but engineers write the UI code by hand." |

### Web (Target: Level A)

| Condition | Effect |
|-----------|--------|
| All D1–D3 🟢, D4–D7 🟢 or 🟡 | Level A |
| Any of D1/D2/D3 has 🔴 | → Level B |
| ≥ 3 dimensions with 🔴 | → Level C |

### Flutter (Target: Level B)

| Condition | Effect |
|-----------|--------|
| D1 🟢, D4 frame structure clear | Level B |
| D1 🟡, D2 🟡, structure partly absolute | Still Level B (with notes) |
| D1 🔴 (all non-semantic) + all absolute positioning | → Level C |

### Windows (Target: Level C)

| Condition | Effect |
|-----------|--------|
| D1 at least 🟡, D3 at least 🟡, D2 any | Level C |
| D1 🔴 + D2 🔴 (zero variables, zero naming) | → Cannot produce valid spec |

---

## Self-Check Checklist (18 items)

Designers can use this before requesting an audit:

### Design System Foundations
- [ ] Key components use the design system (not ad-hoc assembly)
- [ ] Variable names describe purpose, not just appearance
- [ ] At least main states defined: default / hover / disabled / selected / loading
- [ ] Important content sections have source labels (CMS / API / static / brand asset)
- [ ] Important images/brand assets have source annotations

### Annotations & Handoff
- [ ] Complex interactions have annotations explaining switch conditions
- [ ] Key layer names are understandable by an unfamiliar engineer
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
- [ ] AI common errors are written back to team documentation
- [ ] Post-handoff: tracking follow-up question count and correction volume
