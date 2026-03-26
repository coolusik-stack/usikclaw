# Evaluation Round 6 — Raw Results

**Date:** 2026-02-27  
**Evaluator:** Strict benchmark (Apple keynotes, Stripe, NYT, Vercel)

---

## 1. ai-timeline.html

**Screenshot observations:** Clean vertical timeline with alternating left/right cards. Hero stats at top with animated counters. Era labels on center line. Left sticky nav for decades. Light theme showing (despite default dark in code — localStorage override). **Major bug: 8 items hidden by scroll-reveal never appear in full-page view.** Bottom 60% of page is empty white space with only era labels visible.

**Console errors:** None

**Theme toggle:** Works correctly. Light/dark swap clean.

**Interactivity:** Scroll reveal animations, era nav, hover card lift. Counter animation works. But scroll reveal is too aggressive — items below fold stay invisible until manually scrolled into view, which breaks the full-page experience and PNG export.

| Dimension | Score | Notes |
|-----------|-------|-------|
| Visual Design | 7 | Clean but generic. Cards are plain white boxes. No visual hierarchy beyond alternating sides. Missing: gradient accents, illustration, iconography. Looks like a CSS tutorial, not NYT. |
| Data Clarity | 7 | Timeline events are readable but sparse. Hero stats are good. Missing context — no visual weight to distinguish major vs minor events. |
| Interactivity | 6 | Scroll reveal is broken for full-page view. Card hover is subtle. Era nav works but unstyled. No click-to-expand, no rich hover tooltips. |
| Responsiveness | 7 | Viewport meta present. Likely works on mobile but not tested. Single-column would stack okay. |
| Code Quality | 7 | Well-structured, shared boilerplate. But scroll reveal bug is a code quality issue. IntersectionObserver threshold 0.05 with rootMargin should work but doesn't for off-screen items in full capture. |
| Theme Support | 8 | Both themes work. Colors are appropriate. Dot border color updates on theme change. Good. |
| Accessibility | 5 | No aria-labels on timeline items. No role attributes. Era nav links lack aria-current. No skip navigation. Color-only era differentiation. |
| Polish | 5 | Half the page is blank due to scroll-reveal bug. This is a showstopper for presentation/export. |

**Average: 6.5**

**Top issues:**
1. Scroll-reveal hides content that never gets triggered — half the timeline invisible
2. No accessibility attributes whatsoever
3. Visually generic — needs more design personality

---

## 2. comparison-infographic.html

**Screenshot observations:** Two-column comparison layout. Hero stats in grid. Pros/cons section with check/x marks. Bar chart at bottom (Chart.js). Clean light theme. Good information hierarchy.

**Console errors:** `Failed to create chart: can't acquire context from the given item` — this error persists from a previous page load (stale console). The bar chart IS rendering, so this may be a race condition or from another chart attempt.

**Theme toggle:** Present via menu.

**Interactivity:** Card hover effects, animated counters, chart hover tooltips.

| Dimension | Score | Notes |
|-----------|-------|-------|
| Visual Design | 7 | Clean and readable but feels like a Bootstrap template. No brand personality. The stat cards are too uniform — all same size regardless of importance. Bar chart colors are okay but not refined. |
| Data Clarity | 8 | Good! Stats are prominent, pros/cons clearly organized, chart is readable. The comparison format inherently works well. |
| Interactivity | 6 | Basic hover effects. Chart.js provides tooltips. No filtering, no animated transitions between data views. Static feeling. |
| Responsiveness | 7 | Grid layout should collapse. Not tested on mobile. |
| Code Quality | 7 | Chart.js console error is concerning even if chart renders. Clean structure otherwise. |
| Theme Support | 7 | Works but chart colors may not adapt perfectly to theme changes. |
| Accessibility | 5 | Chart has no aria description. Pros/cons use color (green/red) without alternative indicators beyond ✓/✗ text. No landmark roles. |
| Polish | 7 | Chart error in console. Some empty space at bottom. Generally solid but not polished. |

**Average: 6.75**

---

## 3. saas-dashboard.html

**Screenshot observations:** Best-looking of the set. 6 KPI cards in 3x2 grid with trend indicators. 4 charts below (line, donut, bar, donut). Clean layout, good data density. "Live" indicator in header. Light theme.

**Console errors:** Stale chart error from previous navigation.

**Interactivity:** Chart.js hover/tooltips. Card hover effects.

| Dimension | Score | Notes |
|-----------|-------|-------|
| Visual Design | 8 | Closest to a real SaaS dashboard. Good card design, appropriate whitespace, KPI hierarchy works. Still missing: sidebar nav, time-range selector, user avatar — things that make it feel "real." |
| Data Clarity | 8 | KPIs are immediately scannable. Charts are well-labeled. Trend indicators (↑12%) are helpful. Donut legends clear. |
| Interactivity | 6 | Chart.js defaults. No time range filtering, no drill-down, no animated data transitions. A real dashboard (Stripe, Linear) would have much more. |
| Responsiveness | 7 | Grid-based, should collapse. |
| Code Quality | 7 | Clean. Chart.js integration standard. |
| Theme Support | 7 | Theme toggle present. Charts may need color updates on theme switch. |
| Accessibility | 5 | No aria-labels on KPI cards. Charts lack descriptions. No keyboard navigation for chart data. |
| Polish | 7 | Feels complete for what it is. "Live" indicator is a nice touch. But it's a static mock, not interactive. |

**Average: 6.9**

---

## 4. slide-deck-demo.html

**Screenshot observations:** Full-screen slide deck with dark gradient background. Korean + English text. "From 180+ Rejections to Staff Engineer at Meta" — personal career story. Slide navigation (1/8). Progress bar at top. Slide 2 shows "By the Numbers" with 4 stat cards with colored top borders.

**Console errors:** Stale chart error.

**Interactivity:** Arrow key navigation works. Slide transitions. Progress bar updates.

| Dimension | Score | Notes |
|-----------|-------|-------|
| Visual Design | 8 | The dark gradient background is genuinely nice. Typography is strong — large, bold, impactful. Colored accent text works well. Slide 2 stat cards have good design with gradient top borders. Best visual design of the set. |
| Data Clarity | 7 | Stats are clear. Content is narrative-driven which works for slides. |
| Interactivity | 8 | Keyboard nav, click nav, progress bar, slide counter all work. Smooth transitions. This feels like a real presentation tool. |
| Responsiveness | 7 | Full-viewport slides should scale. |
| Code Quality | 7 | 828 lines is the longest file — could be more modular. |
| Theme Support | 6 | Dark-only design. The dark gradient is integral to the aesthetic — light mode would need different approach. Theme toggle may exist but dark is clearly the intended mode. |
| Accessibility | 5 | No aria-live for slide changes. No role="tablist" for slides. No aria-label on navigation buttons. |
| Polish | 8 | Feels complete and professional. The progress bar, smooth transitions, and keyboard support create a polished experience. |

**Average: 7.0**

---

## 5. startup-pitch-deck.html

**Screenshot observations:** Light theme slide deck for "CookAI" — AI kitchen companion. Clean, minimal design with emoji icon. Slide 2 shows "The Problem" with 3 stat cards. Progress bar at top. 10 slides total. Purple accent color.

**Console errors:** Stale.

**Interactivity:** Arrow key navigation, progress bar, slide counter.

| Dimension | Score | Notes |
|-----------|-------|-------|
| Visual Design | 7 | Clean but plain. The light gradient background is subtle. Purple accent is fine. Stat cards on slide 2 are generic white boxes. Compared to real pitch decks (Sequoia template), this lacks visual storytelling — no illustrations, no product screenshots, no team photos. |
| Data Clarity | 7 | Stats are readable. Problem framing is clear. |
| Interactivity | 7 | Same slide nav as slide-deck-demo. Works well. |
| Responsiveness | 7 | Viewport-based slides. |
| Code Quality | 7 | Standard structure. |
| Theme Support | 6 | Light-focused design. Menu has toggle but light is clearly intended. |
| Accessibility | 5 | Same issues as slide-deck-demo. No aria attributes for slides. |
| Polish | 7 | Functional but doesn't wow. A real pitch deck needs more visual variety across slides. |

**Average: 6.6**

---

## 6. system-architecture.html

**Screenshot observations:** Microservices architecture diagram. Layered boxes (Clients → API Gateway → Microservices → Data Layer → External APIs). Each layer has component pills with emojis and status dots (green/yellow/red). Animated dashed connectors between layers. Architecture notes section at bottom.

**Console errors:** Stale.

**Interactivity:** Component hover effects. Status dots presumably clickable or hoverable.

| Dimension | Score | Notes |
|-----------|-------|-------|
| Visual Design | 7 | The layered architecture is clear. Animated connectors between layers are a nice touch. Status dot colors work. But the overall look is flat — compare to Miro or Lucidchart's polished diagrams. Emojis as icons feel amateur. |
| Data Clarity | 8 | Architecture layers are immediately clear. Component relationships obvious. Status indicators useful. This is the most informative visualization of the set. |
| Interactivity | 7 | Animated connectors, hover effects on components. Missing: click to expand service details, tooltip with service info, drag to rearrange. |
| Responsiveness | 6 | Architecture diagrams are inherently hard on mobile. The horizontal pill layout would likely break. |
| Code Quality | 7 | Clean structure. CSS animations for connectors are well done. |
| Theme Support | 7 | Theme toggle works. Light theme shown. |
| Accessibility | 5 | Status dots use color-only (green/yellow/red) with no text labels. No aria-labels on components. Architecture relationships not communicated to screen readers. |
| Polish | 7 | Animated connectors are nice. "Architecture Notes" section adds context. But emojis as icons lower the professional feel. |

**Average: 6.75**

---

## Overall Summary

| File | Avg Score | Lowest | Verdict |
|------|-----------|--------|---------|
| ai-timeline.html | 6.5 | 5 (A11y, Polish) | NEEDS WORK |
| comparison-infographic.html | 6.75 | 5 (A11y) | NEEDS WORK |
| saas-dashboard.html | 6.9 | 5 (A11y) | NEEDS WORK |
| slide-deck-demo.html | 7.0 | 5 (A11y) | NEEDS WORK |
| startup-pitch-deck.html | 6.6 | 5 (A11y) | NEEDS WORK |
| system-architecture.html | 6.75 | 5 (A11y) | NEEDS WORK |

**Overall Average: 6.75**

## 🚦 Gate: NEEDS WORK

All files have at least one dimension scoring 5 (accessibility), and overall averages are below 7.0 for most. No file reaches ACCEPTABLE (≥8.0 all≥7).

---

## Top 10 Issues (Ranked by Impact)

1. **Accessibility is uniformly terrible (all files score 5)** — Zero aria-labels, no landmark roles, no skip navigation, color-only indicators, no keyboard focus management, no screen reader support. This is the single biggest gap across the board.

2. **AI Timeline scroll-reveal hides half the content** — IntersectionObserver-based reveal means items below the initial viewport are invisible in full-page screenshots and PNG exports. Showstopper for the timeline's primary use case.

3. **No meaningful interactivity beyond basics** — Compared to NYT interactives or Stripe's docs, these are static. No filtering, no drill-down, no data exploration, no animated state transitions. Just hover effects and scroll animations.

4. **Chart.js console error** — `Failed to create chart: can't acquire context` appears. Even if charts render, this indicates a timing/initialization bug that could surface in different browsers.

5. **Generic visual design lacking brand personality** — Everything uses the same Inter font + card + border-radius formula. No custom illustrations, no unique color stories, no typographic hierarchy that surprises. Looks like AI-generated templates (which they are).

6. **Emojis used as icons throughout** — System architecture, slide decks all use emoji for icons. This screams "prototype." Real products use SVG icon sets (Lucide, Heroicons) for consistency and scalability.

7. **No responsive testing or mobile breakpoints** — viewport meta tags exist but no evidence of @media queries for mobile layouts. Architecture diagram and dashboards would likely break on phones.

8. **Theme support is surface-level** — Toggle works but Chart.js charts don't update colors on theme switch. Dark/light modes need more nuance than just swapping CSS variables.

9. **Slide decks lack content variety** — Both slide decks show mostly stat cards and text. Real presentations have diverse layouts: full-bleed images, split screens, quote slides, comparison tables, embedded videos.

10. **No loading states, error handling, or offline support** — External dependencies (Google Fonts, Chart.js CDN, html-to-image) with no fallbacks. If CDN is down, pages break silently.

---

## What Would Make These SHIP-worthy (≥9.0)

- **Accessibility audit:** Add aria-labels, roles, keyboard navigation, focus indicators, screen reader descriptions for all charts/diagrams
- **Custom SVG icons** instead of emojis
- **Richer interactivity:** Click-to-filter, animated transitions, tooltips with real data
- **Mobile breakpoints** with tested responsive layouts  
- **Fix scroll-reveal** to not hide content (use opacity animation that starts visible, or trigger all on page load)
- **Chart theme sync** — rebuild charts on theme toggle
- **Visual personality** — unique illustrations, gradients, micro-animations that feel intentional
- **Error handling** — fallback fonts, chart error recovery, graceful CDN failure
