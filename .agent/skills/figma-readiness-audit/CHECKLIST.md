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

## Tier 0 — DS Layer Positioning + Component Decomposition

Before scoring Tier 1, determine the DS layer of the overall design **and**
classify every identifiable sub-element. This affects which dimensions are
required vs optional, and produces the "DS Composition Analysis" section.

### Decision Tree (run on overall design AND on each sub-element)

Ask these questions **in order**:

1. **Is it a global visual rule or foundational design value?**
   (color palette, spacing scale, type ramp, radius set, shadow definition, motion curve)
   → **Yes → Layer 1: Foundations / Tokens**
   → No → next question

2. **Is it a single interactive unit?**
   (Button, Input, Checkbox, Tabs, Modal, Tooltip, Select, Badge, Avatar)
   → **Yes →** Ask: *Can it be reused across multiple products, without
     depending on specific business logic?*
     - Yes → **Layer 3: Core Component** — check if it already exists in the DS
     - No → **Layer 6: Product / Domain Component**
   → No → next question

3. **Does it solve a complete user task or multi-step flow?**
   (filter + results list, batch operation, form wizard, upload flow, approval process)
   → **Yes →** Ask: *Can this flow be reused across products?*
     - Yes → **Layer 4: Pattern**
     - No → **Layer 6: Product Module / Local Pattern**
   → No → next question

4. **Is it a page skeleton or information layout?**
   (dashboard shell, list-detail layout, settings page, create/edit page)
   → **Yes → Layer 5: Template**
   → No → next question

5. **Is it still exploratory or unstable?**
   → **Yes → Layer 7: Experiment / Local**
   → **No → Re-decompose**: the element likely combines multiple layers.
     Break it down further and re-run the tree on each piece.

### Supplementary Judgment Questions

When the decision tree alone is not conclusive, ask these:

| Letter | Question | If Yes | If No |
|--------|----------|--------|-------|
| A | Does it carry product-specific business semantics? | Product / Domain layer | Candidate for Core DS |
| B | Has it been validated in 2+ distinct contexts? | Ready for DS promotion | Keep in local / experiment |
| C | Can it be named in abstract, product-agnostic language? | Suitable for DS | Likely a product module |
| D | Is engineering willing to maintain it as a shared dependency? | Can enter DS | Stay local for now |

### Core DS Entry Criteria

An element should enter the core design system only when **most** of these hold:

- **High reuse** — needed by 2+ products or 3+ distinct screens
- **Low business coupling** — no domain-specific logic baked in
- **Stable structure** — API / props / variants unlikely to churn
- **Abstract naming** — name makes sense outside any single product
- **Central maintenance** — a DS team or designated owner exists

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
| D11 Composition | ⬜ Skip | ⬜ Skip | Required | Required | Required | Required | ⬜ Skip |

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

### D11 Component Composition

**MCP Evidence**: `get_design_context` component instances + Code Connect mappings;
`use_figma` component instance count vs total element count

Checks whether the design is **composed from DS components** rather than built
ad-hoc from raw shapes and text. This is the highest-leverage dimension for
implementation quality: a design that uses DS components translates directly
to DS code, while a design built from raw elements forces engineers to
re-discover and hand-style every control.

**What to check:**

1. **DS component reuse** — Are standard controls (Button, Badge, Select, Input, Chip)
   instances of a DS component, or are they assembled from rectangles + text?
2. **DS gap identification** — For elements that look like standard controls but are NOT
   DS instances: should a new DS component be created? Run the decision tree.
3. **Behavior encapsulation** — Are interaction states (hover, disabled, focus) defined
   at the component level (as Variants), or implicitly expected per-page?
4. **Consistent usage** — Are all buttons of the same semantic type using the same DS
   component, or are there visual duplicates built differently?

| Rating | Condition |
|--------|-----------|
| 🔴 Blocker | > 50% of identifiable UI controls are raw shapes, not component instances; engineers must invent component boundaries |
| 🟡 Ambiguity | Some controls use DS components, but common elements (e.g. buttons, badges) are ad-hoc in places; inconsistent usage of same control |
| 🟢 Clear | ≥ 80% of standard controls are DS component instances; gaps identified with decision-tree classification and creation plan |

**Designer fix guidance**:
1. For every button, badge, select, input, chip, and card in the design: check if
   it is an instance of a DS component (indicated by the diamond icon ◆ in Figma)
2. If it is a raw shape + text assembly, swap it for the DS component instance
3. If no DS component exists yet, run the decision tree:
   - Single interactive unit + reusable across products → propose as Core Component
   - Product-specific → keep as Product Component, but still make it a local component
4. Ensure all interactive states are defined as Variants on the component, not as
   separate ad-hoc frames
5. Run the supplementary judgment questions (A–D) for any element on the boundary

**Report output**: Populate the "DS Composition Analysis" table with one row per
identifiable UI element, including the decision tree result and recommended action.

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

## Self-Check Checklist (23 items)

Designers can use this before requesting an audit:

### Design System Foundations
- [ ] Key components use the design system (not ad-hoc assembly)
- [ ] Variable names describe purpose, not just appearance
- [ ] At least main states defined: default / hover / disabled / selected / loading
- [ ] Important content sections have source labels (CMS / API / static / brand asset)
- [ ] Important images/brand assets have source annotations

### Component Composition (D11)
- [ ] Every button / badge / select / input in the design is a DS component instance (◆ icon)
- [ ] No "visual duplicates" — same control type always uses the same DS component
- [ ] Elements not yet in the DS have been classified via the decision tree
- [ ] Interactive states (hover, disabled, focus) are Variants on the component, not ad-hoc per-page
- [ ] DS gaps have a documented plan: promote to Core / extend existing / keep in Product layer

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
