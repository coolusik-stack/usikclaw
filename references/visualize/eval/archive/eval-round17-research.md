# Round 17 — RESEARCH ROUND

## Research Findings

### New CSS Features (2024-2025)
1. **`interpolate-size: allow-keywords`** (Chrome 129+) — Animate to `height: auto` smoothly. One-liner on `:root`.
2. **`::details-content`** (Chrome 131+) — Style the expandable part of `<details>` elements. Enables animated accordions.
3. **CSS Anchor Positioning** (Chrome 125+) — Position elements relative to anchors without JS. Good for tooltips.
4. **`field-sizing: content`** — Auto-size inputs/textareas to content. Useful for forms.
5. **`@page` margin boxes** (Chrome 131+) — Custom headers/footers for print. Better PDF export.
6. **Styleable `<details>`** (Chrome 131+) — Use `display: flex/grid` on details elements.

### Core Issue Identified
**Slide deck theme support is the #1 quality blocker.** Both slide decks scored 6/10 on themes because:
- Gradient backgrounds are hardcoded and look identical in dark/light
- Content slide backgrounds use hardcoded dark colors instead of CSS vars
- Data cards don't adapt to light theme

### SKILL.md Updates Made
- Added "Theme-Aware Slide Gradients" section with CSS patterns for dark/light gradient pairs
- Added `interpolate-size: allow-keywords` to advanced techniques
- Clarified that content slides must use `var(--bg)` not hardcoded colors

### Rebuild Plan
1. Fix both slide decks with theme-aware gradients (priority 1)
2. Add SVG chart accessibility (role="img", aria-label, title elements)
3. Add staggered scroll-reveal animations
4. Add interpolate-size to all files
5. Improve chart hover micro-interactions
