# Changelog

All notable changes to the Visualize plugin are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## v0.3.0 — Eval Maturity

### Added
- 39 eval rounds completed (R1–R39, 8.1 avg score at R39)
- Carousel card types: Instagram/LinkedIn-format multi-slide carousels
- New visualization types: event poster, quote card, process guide, status report
- 8 comprehensive reference files in `skills/visualize/references/` (design-system, skeleton, types, libraries, menu, css-techniques, animations, eval)
- `skeleton.md` mandatory HTML template for all outputs
- Type-specific interactivity requirements (Popover API, exclusive accordions, anchor positioning)
- Single-screen poster rules for mobile-fit layouts
- CJK font support via Noto Sans (Korean carousel example)
- Visual restraint guidelines (no floating orbs, gradient text, scale transforms, glow effects)

### Changed
- Class-based theming (`html.theme-dark` / `html.theme-light`); removed `@media prefers-color-scheme`
- `var` for all top-level JS declarations to prevent TDZ errors
- Improved Chart.js integration: `Chart.defaults.animation = false`, destroy-and-recreate on theme toggle
- Theme-aware slide gradients using `color-mix()`
- Refactored to Claude Code plugin structure with `plugin.json` and marketplace support
- Card hover uses shadow-only effect (no `translateY` / `scale` transforms)

### Fixed
- Chart.js canvas reuse crash (resetCanvas pattern)
- Theme cascade bug with darker dark mode
- Broken light theme on ai-timeline
- Sparse slide content, broken SVG paths, truncated donut legends

## v0.2.0 — Eval Loop Infrastructure

### Added
- Eval loop methodology with vision-model scoring (LOOP.md)
- 15 example HTML files across all visualization types
- Design system reference (`design-system.md`)
- Standardized menu system across all examples
- CSS-first animation strategy (replaced Motion.js dependency)
- Scroll-reveal, hover effects, entrance animations
- Screenshot capture in eval loop for visual validation
- Mobile breakpoints and responsive layouts for all examples

### Changed
- Rebuilt all examples from CSS-first skeleton (no Motion.js)
- Mandatory HTML skeleton with sizing and text visibility rules

### Fixed
- TDZ errors from `let`/`const` at top level (switched to `var`)
- Motion.js `animate().finished` promise chain failures
- Pitch deck slide nav using unreliable `Motion.finished`

## v0.1.0 — Initial Release

### Added
- Core skill (`SKILL.md`) with design system, output rules, and process guidelines
- 10 visualization types: slide deck, infographic, dashboard, flowchart, timeline, comparison, data viz, one-pager, mind map, kanban
- Hamburger menu component (dark/light/auto themes, PNG download, PDF print)
- CDN library reference (Chart.js, D3.js, Three.js, Mermaid, Reveal.js, Leaflet)
- 3 starter templates (slide deck, dashboard, infographic)
- Evaluation skill with 5-dimension quality rubric
- 40 stress test cases across 7 categories
- Iterative improvement loop methodology (LOOP.md)
