# Round 38 Evaluation (Pre-Fix)

*Date: 2026-02-28*
*Benchmark: Linear.app, Vercel.com, Stripe.com*

## Scoring (1-10): VP=Visual Polish, TY=Typography, CS=Color System, LS=Layout/Spacing, IN=Interactivity, AC=Accessibility, CQ=Code Quality, OI=Overall Impression

### 1. slide-deck-demo.html (Slide Deck)
| VP | TY | CS | LS | IN | AC | CQ | OI | Avg |
|----|----|----|----|----|----|----|----|----|
| 7 | 6 | 7 | 7 | 8 | 7 | 7 | 7 | 7.0 |
- Decorative SVG wireframe overlay on title slide looks complex but professional
- font-weight: 800 on titles is too heavy (should be 700)
- Missing font-feature-settings
- Light mode feels washed out — slide backgrounds don't adapt enough
- Good keyboard/touch nav, progress bar

### 2. saas-dashboard.html (Dashboard)
| VP | TY | CS | LS | IN | AC | CQ | OI | Avg |
|----|----|----|----|----|----|----|----|----|
| 7 | 6 | 7 | 7 | 7 | 7 | 7 | 7 | 6.9 |
- Clean dashboard layout with proper KPI cards + charts
- font-weight: 800 on stat numbers too heavy
- Chart.js charts render properly in both themes
- Good data density (activity feed + feature table)
- Missing font-feature-settings

### 3. ai-timeline.html (Timeline)
| VP | TY | CS | LS | IN | AC | CQ | OI | Avg |
|----|----|----|----|----|----|----|----|----|
| 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7.0 |
- Solid vertical timeline with era sections
- Colored left borders on cards (anti-pattern per SKILL.md)
- Teal accent works well throughout
- Filter tabs for eras are good interactivity
- font-weight: 800 on heading

### 4. carousel-infographic.html (Carousel)
| VP | TY | CS | LS | IN | AC | CQ | OI | Avg |
|----|----|----|----|----|----|----|----|----|
| 7 | 6 | 7 | 7 | 8 | 6 | 6 | 7 | 6.8 |
- Nice gradient backgrounds on cards
- Large purple badge/spinner graphic is distinctive but busy
- font-weight: 800, missing font-feature-settings
- Good carousel navigation with dots + arrows + keyboard
- Icon grid on first slide adds visual interest

### 5. quote-card.html (Card)
| VP | TY | CS | LS | IN | AC | CQ | OI | Avg |
|----|----|----|----|----|----|----|----|----|
| 7 | 6 | 7 | 7 | 7 | 7 | 7 | 7 | 6.9 |
- Masonry-style grid with varied card sizes works well
- Colored left borders on quote cards — acceptable for this type
- Category filter buttons are good
- font-weight: 800 on title, missing font-feature-settings
- Quote marks as decorative elements work

### 6. comparison-infographic.html (Infographic)
| VP | TY | CS | LS | IN | AC | CQ | OI | Avg |
|----|----|----|----|----|----|----|----|----|
| 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7.0 |
- Best structured of all — clear sections, good data hierarchy
- Chart.js bar, horizontal bar, and doughnut charts all render well
- Purple/blue accent palette is sophisticated
- font-weight: 800 on hero stats
- Advantages/Challenges layout is clear

## Summary
| File | Pre-Fix Avg |
|------|------------|
| slide-deck-demo | 7.0 |
| saas-dashboard | 6.9 |
| ai-timeline | 7.0 |
| carousel-infographic | 6.8 |
| quote-card | 6.9 |
| comparison-infographic | 7.0 |
| **Overall Average** | **6.93** |

### Common Issues Across Files
1. **font-weight: 800** used everywhere — should be 700 max per SKILL.md
2. **Missing font-feature-settings: 'cv11', 'ss01'** in most files
3. **Colored left borders on cards** in timeline and some other files (anti-pattern)
4. Missing body letter-spacing: -0.011em in several files
5. Some files load 800/900 weight Inter unnecessarily
