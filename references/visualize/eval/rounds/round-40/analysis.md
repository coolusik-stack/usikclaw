# Round 40 Analysis

## Persona
VP of Clinical Operations at a mid-size biotech (Series C). Preparing board deck showing drug pipeline status, enrollment, timelines, budget.

## Scores Summary
| File | L2 | L3 | Overall |
|------|----|----|---------|
| pipeline-dashboard.html | 9.7 | 7.2 | 7.9 |
| clinical-timeline.html | 9.1 | 5.7 | 6.7 |
| executive-summary.html | 9.2 | 5.5 | 6.7 |

Average: **7.1**

## Issues Found

### Issue 1: Chart.js onThemeChange race condition
- **Category:** Missing
- **Frequency:** 2/3 outputs (all with charts)
- **Severity:** High
- **Root cause:** SKILL.md skeleton calls `applyTheme()` on page load which triggers `onThemeChange()` before charts exist. The eval pipeline's theme toggle also triggers a rebuild on an already-used canvas.
- **Proposed fix:** Add a `chartsBuilt` guard flag pattern to skeleton. Document that `onThemeChange` must check if charts have been initialized before calling buildCharts.

### Issue 2: data-reveal makes content invisible in initial screenshots/above-fold
- **Category:** Unclear
- **Frequency:** 3/3 outputs
- **Severity:** High
- **Root cause:** The `reveal` class sets `opacity: 0` immediately, making below-fold content invisible even for screenshot tools. The SKILL.md says "content visible by default" but the skeleton's JS adds `.reveal` class which hides content. Pages that rely heavily on scroll-reveal look empty in non-scrolling contexts.
- **Proposed fix:** Clarify that scroll-reveal should be used sparingly (max 2-3 sections), and critical content sections should use `.animate` (page-load) instead. Add guidance: "Above-fold content must NEVER use data-reveal."

### Issue 3: Stat value color inconsistency
- **Category:** Missing
- **Frequency:** 2/3 outputs (executive-summary, pipeline-dashboard)
- **Severity:** Medium
- **Root cause:** No guidance in SKILL.md about when to use colored stat values vs plain text. Random color application (some green, some purple, some plain) creates confusion about meaning.
- **Proposed fix:** Add rule: "Colored stat values must have semantic meaning (green=positive, red=negative, accent=primary metric). If no semantic meaning, use var(--text)."

### Issue 4: SVG world maps look crude
- **Category:** Missing
- **Frequency:** 1/3 outputs
- **Severity:** Medium
- **Root cause:** No guidance on map visualizations. Hand-drawn SVG continents look amateurish. No recommendation for Leaflet or proper map approaches.
- **Proposed fix:** Add to SKILL.md: "For geographic data, use Leaflet.js (CDN: https://unpkg.com/leaflet) with a tile provider, or use a pre-built SVG world map. Never hand-draw continent shapes."

### Issue 5: Missing skip-to-content link
- **Category:** Buried
- **Frequency:** 3/3 outputs
- **Severity:** Low
- **Root cause:** SKILL.md mentions accessibility requirements including skip-to-content, but the skeleton template doesn't include one.
- **Proposed fix:** Add `<a href="#main-content" class="skip-link">Skip to content</a>` to the skeleton template.
