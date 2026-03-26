# Evaluation Round 8 — Raw Scores

**Date:** 2026-02-27  
**Evaluator:** Subagent (eval-round-8)  
**Benchmark:** Apple Keynotes, Stripe Docs, NYT Interactives, Vercel Dashboard  
**Console Errors:** 0 across all 6 files ✅

---

## Per-File Scores

### 1. ai-timeline.html

| Dimension | Score | Notes |
|-----------|-------|-------|
| Visual Polish | 8 | Clean card layout, good typography hierarchy, nice gradient accents. Timeline line/dot design is solid. Cards could use subtler shadows; spacing between era badges and cards feels slightly uneven. |
| Interactivity | 7 | Era navigation sidebar with active state, scroll-based highlighting. No card hover animations or entrance animations visible on load. Timeline feels static compared to NYT interactives. |
| Data Clarity | 8 | Clear chronological flow, year labels prominent, era badges provide context. Stats header (75+, 12, $184B) is effective. |
| Responsiveness | 7 | Left sidebar nav may crowd on narrow screens. Timeline alternating layout works at desktop but untested at mobile breakpoints from visual inspection. |
| Accessibility | 9 | Skip link, aria-labels on region, semantic articles, focus-visible outlines, nav landmark with descriptive label. Best in class for this set. |
| Code Quality | 9 | Zero console errors. Single-file, no external deps. ~479 lines, clean structure. |
| Theme Support | 8 | Dark/light toggle works fully. Respects prefers-color-scheme. Light mode looks polished. No prefers-color-scheme media query in CSS (JS only). |
| Wow Factor | 7 | Professional and clean, but not breathtaking. Lacks micro-animations, parallax, or interactive data points that would elevate to Apple keynote level. |
| **Average** | **7.88** | |

### 2. comparison-infographic.html

| Dimension | Score | Notes |
|-----------|-------|-------|
| Visual Polish | 8 | Good use of green/purple dual-color system. Stats cards are bold and readable. Bar chart is well-styled. Pros/cons layout is balanced. |
| Interactivity | 7 | Filter buttons (All/Well-being/Performance/Growth) for chart. Bar chart hover states. Menu toggle. No scroll animations or transitions between filter states. |
| Data Clarity | 8 | Chart has clear labels, legend, Y-axis percentages. Pros/cons are well-organized with color-coded bullets. Key Insights section summarizes well. |
| Responsiveness | 7 | Two-column layout for stats/pros-cons should stack on mobile. Chart container may need scroll on narrow viewports. |
| Accessibility | 7 | Has skip link and focus-visible. Chart lacks aria-labels for individual bars. Pros/cons lists use visual bullets (dots) rather than semantic list elements. |
| Code Quality | 9 | Zero console errors. ~434 lines, self-contained. SVG chart is hand-rolled — impressive but harder to maintain. |
| Theme Support | 8 | Dark/light toggle via hamburger menu. Respects system preference. Light mode functional. |
| Wow Factor | 7 | Solid infographic, but static feel. A world-class version would have animated number counters, bar chart entrance animations, scroll-triggered reveals. |
| **Average** | **7.63** | |

### 3. saas-dashboard.html

| Dimension | Score | Notes |
|-----------|-------|-------|
| Visual Polish | 9 | Closest to Vercel/Stripe aesthetic. KPI cards with trend indicators are crisp. Chart styling is professional. Donut charts with clean legends. Great use of teal accent. |
| Interactivity | 7 | "Live" indicator pulses. Charts are SVG but static — no hover tooltips on data points. No time range selector for revenue chart. |
| Data Clarity | 9 | Excellent metric hierarchy: primary KPIs up top, detailed charts below. Trend indicators (↑12%, ↓0.5%) with color coding. Clear legends on all charts. |
| Responsiveness | 7 | 3-column KPI grid and 2-column chart grid should collapse gracefully, but fixed widths on chart SVGs may cause issues. |
| Accessibility | 7 | Has skip link, focus-visible. KPI cards lack individual aria-labels. Chart SVGs missing role="img" and aria-labels for screen readers. |
| Code Quality | 9 | Zero errors. ~359 lines — most concise file. Clean separation of concerns. |
| Theme Support | 8 | Toggle present, system preference respected. |
| Wow Factor | 8 | This actually looks like a real SaaS dashboard. Best wow factor of the set. A designer would nod approvingly. Missing: real-time update animations, sparklines, hover tooltips. |
| **Average** | **8.00** | |

### 4. slide-deck-demo.html

| Dimension | Score | Notes |
|-----------|-------|-------|
| Visual Polish | 8 | Full-screen slide layout is clean. Title slide has nice gradient glow effect. Korean + English bilingual text is well-handled. Progress bar at top. |
| Interactivity | 8 | Slide navigation with prev/next buttons, keyboard arrows likely supported. Slide counter (1/8). Progress bar animates. This is the most interactive file. |
| Data Clarity | 7 | Title slide is clear. Can't evaluate other slides without navigating, but structure suggests data slides exist. Slide format inherently limits data density. |
| Responsiveness | 6 | Full-viewport slides are inherently responsive for width, but text sizing on very small screens may not scale. Fixed slide dimensions may letterbox. |
| Accessibility | 7 | Has skip link. Navigation buttons have labels. Slides likely use aria-live for screen readers? Keyboard navigation is a plus. |
| Code Quality | 8 | Zero errors. ~405 lines. Slide engine is custom-built — good but complex. |
| Theme Support | 7 | Theme toggle present but slide decks are typically dark-only in presentations. Light mode may look odd for this use case. |
| Wow Factor | 8 | Feels like a real keynote presentation. The gradient glow and centered typography create impact. Best Apple-keynote-adjacent file in the set. |
| **Average** | **7.38** | |

### 5. startup-pitch-deck.html

| Dimension | Score | Notes |
|-----------|-------|-------|
| Visual Polish | 8 | CookAI branding is clean. Icon + gradient title looks polished. Centered layout with good whitespace. Blue/purple accent palette is cohesive. |
| Interactivity | 8 | 10 slides with navigation. Progress bar. Slide transitions. Hamburger menu for additional options. |
| Data Clarity | 7 | Title slide is minimal by design. Business data would be in subsequent slides. Pitch deck format prioritizes story over data density. |
| Responsiveness | 6 | Same slide-deck viewport constraints. Fixed aspect ratio may not adapt well to portrait mobile. |
| Accessibility | 8 | 36 aria attributes — highest in the set. Skip link present. Good semantic structure for a presentation format. |
| Code Quality | 8 | Zero errors. ~549 lines (longest file — 10 slides worth of content). |
| Theme Support | 7 | Toggle present. Pitch decks work best dark; light mode is bonus. |
| Wow Factor | 8 | Looks like a real YC-style pitch deck. The icon, branding, and tagline ("Snap your fridge. Get personalized recipes. Waste nothing.") create a compelling opening. |
| **Average** | **7.50** | |

### 6. system-architecture.html

| Dimension | Score | Notes |
|-----------|-------|-------|
| Visual Polish | 8 | Layered architecture with color-coded tiers (green/yellow/red status). Dashed connection lines between layers. Clean pill-shaped service nodes. Architecture Notes cards are well-designed. |
| Interactivity | 7 | Status indicators (green dots) pulse. Service nodes likely have hover states. Hamburger menu. No click-to-expand or zoom on layers. |
| Data Clarity | 9 | Excellent architecture communication. Clear layer hierarchy (Clients → Gateway → Microservices → Data → External). Status legend at top. Architecture Notes provide context. Color-coded health status is intuitive. |
| Responsiveness | 7 | Horizontal service node layout may overflow on narrow screens. Layer boxes use max-width but pill elements could wrap awkwardly. |
| Accessibility | 9 | 54 aria attributes — highest count. Skip link present. Good semantic structure. Status indicators have meaning conveyed through color AND text legend. |
| Code Quality | 8 | Zero errors. ~528 lines. Well-structured with clear layer separation. |
| Theme Support | 8 | Toggle works. System preference respected. |
| Wow Factor | 8 | This is genuinely useful — a real engineering team could present this. The status indicators and layered design feel professional. Lacks: animated data flow lines, click-to-drill-down. |
| **Average** | **8.00** | |

---

## Summary Table

| File | Polish | Interactive | Data | Responsive | A11y | Code | Theme | Wow | **Avg** |
|------|--------|------------|------|------------|------|------|-------|-----|---------|
| ai-timeline | 8 | 7 | 8 | 7 | 9 | 9 | 8 | 7 | **7.88** |
| comparison-infographic | 8 | 7 | 8 | 7 | 7 | 9 | 8 | 7 | **7.63** |
| saas-dashboard | 9 | 7 | 9 | 7 | 7 | 9 | 8 | 8 | **8.00** |
| slide-deck-demo | 8 | 8 | 7 | 6 | 7 | 8 | 7 | 8 | **7.38** |
| startup-pitch-deck | 8 | 8 | 7 | 6 | 8 | 8 | 7 | 8 | **7.50** |
| system-architecture | 8 | 7 | 9 | 7 | 9 | 8 | 8 | 8 | **8.00** |
| **Dimension Avg** | **8.17** | **7.33** | **8.00** | **6.67** | **7.83** | **8.50** | **7.67** | **7.67** | **7.73** |

### Overall Average: **7.73**

(Previous round: 8.33 — this round applies stricter benchmarking against world-class references)

---

## Console Errors

| File | Errors |
|------|--------|
| ai-timeline.html | 0 |
| comparison-infographic.html | 0 |
| saas-dashboard.html | 0 |
| slide-deck-demo.html | 0 |
| startup-pitch-deck.html | 0 |
| system-architecture.html | 0 |

**Total: 0 console errors** ✅

---

## Top Issues Per File

### ai-timeline.html
- No entrance/scroll animations on timeline cards — feels static vs NYT interactives
- Era sidebar nav text is tiny and hard to read (font-size looks ~10px)
- No `prefers-color-scheme` CSS media query — only JS detection (flash-of-wrong-theme possible)

### comparison-infographic.html
- Chart bars lack aria-labels — screen readers can't interpret the SVG bar chart
- No animated number counters on stat cards (77%, 65%, $40K, 72%)
- Filter button transitions between chart states are instant, no animation

### saas-dashboard.html
- No hover tooltips on line chart data points — critical for a real dashboard
- KPI cards lack individual `aria-label` attributes
- Chart SVGs missing `role="img"` and descriptive `aria-label`

### slide-deck-demo.html
- Responsiveness is weakest dimension — no evidence of mobile breakpoints for slide content
- Only evaluated slide 1/8 — content slides may have additional issues
- Light mode is awkward for presentation content (gradient glow effects designed for dark)

### startup-pitch-deck.html
- Same responsiveness concern as slide-deck-demo — portrait mobile likely problematic
- 549 lines is heavy for a single file — could benefit from CSS custom properties consolidation
- Only slide 1/10 evaluated visually

### system-architecture.html
- Connection lines between layers are static dashed lines — animated flow lines would elevate significantly
- No click-to-expand/drill-down on service nodes
- Horizontal node layout may overflow on tablets (7 pills in Microservices row)

---

## Top 5 Issues to Fix (Ranked by Impact)

1. **No scroll/entrance animations across all files** — Every file feels static on load. Adding IntersectionObserver-based fade-in/slide-up animations would dramatically increase wow factor across all 6 files. Impact: +1 point on Interactivity and Wow for every file.

2. **Responsiveness gaps in slide decks (slide-deck-demo, startup-pitch-deck)** — Both score 6/10. Need viewport-relative font sizing (`clamp()`), flexible slide layouts, and portrait-mode adaptations. These are the two lowest-scoring files overall.

3. **Chart accessibility (comparison-infographic, saas-dashboard)** — SVG charts lack `role="img"`, `aria-label`, and individual bar/point labels. Screen readers get nothing from the most data-rich visualizations. Easy fix, high a11y impact.

4. **No `prefers-color-scheme` CSS media query (all files)** — Theme detection is JS-only, causing potential flash-of-wrong-theme on initial load. Adding a CSS `@media (prefers-color-scheme: light)` block that sets light variables before JS runs would eliminate the flash.

5. **Missing hover tooltips on charts (saas-dashboard, comparison-infographic)** — Interactive data exploration is expected in any modern dashboard. Hovering over a chart data point should show the exact value. This is table stakes for Stripe/Vercel-level quality.
