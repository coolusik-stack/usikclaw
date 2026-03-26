# Research Round 31 — February 28, 2026

## Problem Analysis

After 30 rounds, scores plateau at ~7.85 (calibrated). Key patterns:
- **Interactivity** is consistently the lowest dimension (8.0 even in inflated scores → ~7.0 calibrated)
- **Accessibility** second lowest
- **Evaluator inflation** — R30 evaluator gave 10/10 for code quality to files it never opened
- Weakest files: status-report (8.4 inflated → ~7.4), quote-card (8.5 → ~7.5), event-poster (8.5 → ~7.5)

## Root Causes (Why We're Stuck)

1. **All files feel the same** — identical skeleton, identical animations, identical hover effects. No file has a "wow" moment unique to its type.
2. **Interactivity is shallow** — theme toggle + menu is the only interaction on most files. No filtering, no sorting, no progressive disclosure.
3. **Static content types** (quote-card, event-poster, status-report) have NO meaningful interaction beyond theme toggle.
4. **border-radius: 16px** on status-report violates SKILL.md (should be 8px) — small but indicates skeleton drift.

## New CSS/HTML Techniques Discovered

### 1. Exclusive `<details>` Accordion (Chrome 120+)
```html
<details name="faq"><summary>Question 1</summary><p>Answer</p></details>
<details name="faq"><summary>Question 2</summary><p>Answer</p></details>
```
No JS needed. Perfect for: process guides, cheatsheets, FAQs. Adds interactivity for free.

### 2. `::details-content` Pseudo-element (Chrome 131+)
Style the expandable part of `<details>`:
```css
::details-content { transition: height 0.3s, opacity 0.3s; }
```
Animate accordion open/close with pure CSS.

### 3. CSS Anchor Positioning (Chrome 125+)
```css
.anchor { anchor-name: --tooltip; }
.tooltip { position: fixed; position-anchor: --tooltip; position-area: block-start; }
```
Perfect for: architecture diagrams (node tooltips), dashboards (chart annotations), timelines (event details). No JS positioning needed.

### 4. `field-sizing: content` (Chrome 123+)
Auto-size textareas/inputs to fit content. Useful for interactive filter inputs.

### 5. `interpolate-size: allow-keywords` (Chrome 129+)
Already in SKILL.md but NOT in skeleton. Should be added to `:root`.

### 6. `@page` Margin Boxes (Chrome 131+)
Custom print headers/footers:
```css
@page { @bottom-center { content: "Page " counter(page) " of " counter(pages); } }
```

### 7. Popover API (Chrome 114+)
```html
<button popovertarget="info">Info</button>
<div id="info" popover>Details here</div>
```
Zero-JS tooltips/modals. Perfect for adding info panels to dashboards and architecture diagrams.

## Specific Improvements to Make

### SKILL.md Changes

1. **Add `interpolate-size: allow-keywords` to skeleton `:root`** — enables smooth height:auto transitions everywhere
2. **Add Popover API section** — zero-JS info panels for dashboards/architecture
3. **Add Exclusive Accordion guidance** — use `<details name="...">` for collapsible sections in cheatsheets, process guides
4. **Add Anchor Positioning for tooltips** — replace JS-positioned tooltips in architecture diagrams
5. **Add type-specific interactivity requirements:**
   - Status reports: collapsible detail sections, progress bar animations on scroll
   - Quote cards: card flip animation, swipeable quotes, share button
   - Event posters: countdown timer, RSVP button interaction
   - Cheatsheets: search/filter, copy-to-clipboard, collapsible groups
   - Dashboards: filter toolbar, chart type switcher, date range selector
   - Architecture: clickable nodes with popover details
6. **Fix skeleton border-radius** — ensure 8px consistency (some files drifted to 16px)
7. **Add `@page` margin boxes to print section** — page numbers in print output
8. **Strengthen evaluator instructions** — mandate opening EVERY file, not "assessing"

### File-Specific Rebuilds Needed

| File | Key Change |
|------|-----------|
| status-report | Add collapsible risk details, animated progress bars, print page numbers |
| quote-card | Add card cycling animation (auto-rotate quotes), share/copy button |
| event-poster | Add animated countdown timer, RSVP interaction |
| process-guide | Convert steps to exclusive accordion |
| cheatsheet-claude-code | Add search/filter, copy-to-clipboard buttons |
| cheatsheet-git | Add search/filter, copy-to-clipboard buttons |
| system-architecture | Add popover details on node click |
| saas-dashboard | Add filter toolbar, metric drill-down |

## Summary

The plateau isn't about visual quality anymore — it's about **interactivity depth**. Every file needs at least ONE meaningful interaction beyond theme toggle. The new CSS/HTML features (popover, exclusive accordion, anchor positioning) let us add interactivity without increasing JS complexity — which aligns perfectly with the "simplify code" principle.
