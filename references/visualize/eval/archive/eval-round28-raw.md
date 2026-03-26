# Round 28 Evaluation

**Date:** 2026-02-28 10:00 PST
**Evaluator:** Manual visual review (image model analysis of screenshots)

## Scores

| File | Visual | Layout | Interact | Responsive | Theme | A11y | Code | Content | **Avg** |
|------|--------|--------|----------|------------|-------|------|------|---------|---------|
| ai-timeline | 6.0 | 7.0 | 6.0 | 6.5 | 6.5 | 6.0 | 7.0 | 7.0 | **6.5** |
| carousel-infographic | 6.5 | 6.0 | 6.0 | 6.5 | 6.5 | 6.0 | 7.0 | 7.0 | **6.4** |
| comparison-infographic | 6.0 | 7.0 | 6.0 | 6.5 | 6.5 | 6.0 | 7.0 | 6.5 | **6.4** |
| slide-deck-demo | 6.5 | 6.5 | 6.0 | 6.5 | 6.5 | 6.5 | 7.0 | 6.5 | **6.5** |
| system-architecture | 7.0 | 7.0 | 7.0 | 7.0 | 7.0 | 7.0 | 7.5 | 7.5 | **7.1** |
| saas-dashboard | 7.0 | 6.5 | 6.5 | 7.0 | 7.0 | 6.5 | 7.0 | 7.5 | **6.9** |
| startup-pitch-deck | 7.5 | 7.0 | 7.0 | 7.0 | 7.5 | 7.0 | 7.0 | 7.5 | **7.2** |
| status-report | 7.5 | 7.0 | 6.5 | 7.0 | 7.5 | 7.0 | 7.0 | 7.5 | **7.1** |

**Overall Average: 6.8** | Gate: ❌ FAIL

## Console Errors
None observed (0 errors across all 8 files).

## Top 5 Issues (by severity)

### 1. CRITICAL: Generic dark themes with no personality
Every file uses a near-identical dark navy/charcoal background that looks like "default dark dashboard template." No distinctive identity, brand feel, or atmospheric depth. Compare to Vercel (warm dark with grain), Linear (deep purple-tinted), Stripe (rich navy with gradients). Need: file-specific color stories, subtle background textures, intentional glow/gradient usage.

### 2. HIGH: Low text contrast and accessibility gaps
Subtitle text, navigation arrows, and secondary labels are too low contrast across nearly all files. Gray-on-dark-gray fails WCAG AA for smaller text. The carousel nav arrows are nearly invisible.

### 3. HIGH: Excessive dead space / poor content density
Carousel cards have massive unused vertical space. Slide decks feel barren. Timeline wastes right half of viewport. Content needs to fill the visual space more intentionally — either with richer content or tighter containers.

### 4. MEDIUM: Hamburger menu dropdown looks unfinished
Multiple files show an unstyled dropdown menu (Download PNG, Print/PDF). No shadows, no animation, breaks card boundaries. Looks like developer debug UI, not polished product.

### 5. MEDIUM: Charts feel like library defaults
Bar charts, donut charts, and radar charts look like raw Chart.js output. Missing: rounded corners on bars, curated color palettes, styled axes, subtle gridlines, custom tooltips.

## Screenshots
All saved to `eval/screenshots/round28/`:
- `{filename}-dark.png` and `{filename}-light.png` for each file
- `slide-deck-demo-slide3.png`, `slide-deck-demo-slide5.png`
- `startup-pitch-deck-slide3.png`, `startup-pitch-deck-slide5.png`
