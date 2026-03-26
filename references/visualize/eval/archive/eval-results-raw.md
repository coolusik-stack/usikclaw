# Eval Results — Raw Scores
**Date:** 2026-02-26 | **Evaluator:** Lex | **Loop:** 1/3

## 1. startup-pitch-deck.html
| # | Dimension | Score | Notes |
|---|-----------|-------|-------|
| D1 | First Impression | 4/10 | Hero slide is BLANK — title text invisible (white on near-white gradient?). Catastrophic first impression. |
| D2 | Typography | 6/10 | Slide 2 looks decent — "THE PROBLEM" eyebrow + big stat. But hero is broken. |
| D3 | Color | 6/10 | Orange accent works. Dark bg fine. But no light theme exists. |
| D4 | Layout | 7/10 | Card layout on content slides is clean. Dot pagination nice. |
| D5 | Content | 7/10 | Good pitch structure (problem → solution → market). Content itself is solid. |
| D6 | Interactivity | 5/10 | Menu EXISTS (hamburger visible) but audit shows menuExists=false (class mismatch?). No light theme. No print styles. |
| D7 | Technical | 4/10 | No light theme, no print styles, no @keyframes, no reduced-motion. Menu class mismatch. |
| D8 | Shareability | 4/10 | Can't share a deck with a blank first slide. |
| | **OVERALL** | **5.4/10** | **❌ FAIL** |

### Systemic Issues
- Hero slide text invisible — likely CSS color issue on gradient background
- Menu class doesn't match `.viz-menu` convention from SKILL.md
- No light theme at all
- No print styles
- No entrance animations

---

## 2. saas-dashboard.html
| # | Dimension | Score | Notes |
|---|-----------|-------|-------|
| D1 | First Impression | 8/10 | Immediately looks like a real SaaS dashboard. KPI row + charts = instant clarity. |
| D2 | Typography | 7/10 | KPI numbers are bold and clear. Labels adequate. Could use Inter font. |
| D3 | Color | 7/10 | Good use of accent colors on KPIs. Chart colors distinct. Donut chart colors (red/orange/purple) feel random. |
| D4 | Layout | 8/10 | 6-column KPI grid + 2x2 chart grid works well. Good density. |
| D5 | Content | 8/10 | All metrics realistic and labeled. MRR/ARR/churn/LTV/CAC — correct SaaS metrics. |
| D6 | Interactivity | 6/10 | Menu visible. Charts are Chart.js (hover tooltips). But need to verify theme toggle, download, print. |
| D7 | Technical | 6/10 | Need to audit — likely missing light theme, print styles. |
| D8 | Shareability | 7/10 | Decent. Would look good in a screenshot. Not jaw-dropping but professional. |
| | **OVERALL** | **7.2/10** | **🔧 NEEDS WORK** |

### Systemic Issues
- No Inter font (uses system fonts only)
- Donut chart color palette not harmonious
- Likely missing light theme + print CSS

---

## 3. ai-timeline.html
| # | Dimension | Score | Notes |
|---|-----------|-------|-------|
| D1 | First Impression | 6/10 | Title is nice (gradient text). But timeline cards are TINY — barely readable. Massive empty space. |
| D2 | Typography | 5/10 | Card text is way too small. Title good. Date labels tiny. |
| D3 | Color | 7/10 | Blue-purple gradient title looks good. Card backgrounds have subtle distinction. |
| D4 | Layout | 4/10 | Cards are too small, too much whitespace between them. The alternating layout works in concept but cards need to be 2-3x larger. |
| D5 | Content | 7/10 | Good milestone selection. Descriptions are accurate. But hard to read at this size. |
| D6 | Interactivity | 5/10 | Menu visible. Scroll-triggered animations (not visible in screenshot — cards may animate in). |
| D7 | Technical | 5/10 | Likely missing light theme, print. Viewport is very tall (mobile-ratio render). |
| D8 | Shareability | 4/10 | Too much empty space. Cards too tiny. Wouldn't screenshot this. |
| | **OVERALL** | **5.4/10** | **❌ FAIL** |

### Systemic Issues
- Timeline cards way too small — need minimum card width guidance in SKILL.md
- Too much spacing between timeline events
- Viewport rendering issue (looks stretched vertically)

---

## 4. comparison-infographic.html
| # | Dimension | Score | Notes |
|---|-----------|-------|-------|
| D1 | First Impression | 7/10 | Gradient title looks nice. Stat cards are visible and colorful. Professional feel. |
| D2 | Typography | 7/10 | Big numbers (77%, 64%, $11K, 40min) are bold and clear. Section headers readable. |
| D3 | Color | 7/10 | Green (remote) vs purple (office) color coding works. Stat cards have good contrast. |
| D4 | Layout | 6/10 | Stat cards look good. But "Pros & Cons" and "Satisfaction" sections appear empty — likely Chart.js not rendering or content missing below fold. |
| D5 | Content | 6/10 | Top section is great. But middle sections appear empty — "Pros & Cons" heading with nothing under it. |
| D6 | Interactivity | 6/10 | Menu visible. Scroll behavior unknown from screenshot. |
| D7 | Technical | 6/10 | Charts may not be rendering (empty sections). Need to verify. |
| D8 | Shareability | 6/10 | Top portion is shareable. Overall feels incomplete. |
| | **OVERALL** | **6.4/10** | **🔧 NEEDS WORK** |

### Systemic Issues
- Chart.js charts not rendering (empty sections visible)
- Infographic sections need content validation

---

## 5. system-architecture.html
| # | Dimension | Score | Notes |
|---|-----------|-------|-------|
| D1 | First Impression | 8/10 | Wow — the Mermaid diagram with color-coded layers is impressive. Looks like real documentation. |
| D2 | Typography | 7/10 | Title gradient text is nice. Diagram labels readable. Annotation cards well-structured. |
| D3 | Color | 8/10 | Color-coded layers (blue=clients, orange=gateway, green=services, pink=data, red=external) is excellent. Legend matches. |
| D4 | Layout | 8/10 | Diagram centered, legend below, annotation cards in a 4-column grid. Clean hierarchy. |
| D5 | Content | 8/10 | Accurate architecture. Good service descriptions. Deployment card mentions Docker/K8s/Helm. |
| D6 | Interactivity | 6/10 | Menu visible. Not much to interact with beyond theme/download. |
| D7 | Technical | 7/10 | Mermaid rendered correctly. Need to verify light theme, print. |
| D8 | Shareability | 8/10 | Would definitely screenshot this. Looks professional. |
| | **OVERALL** | **7.6/10** | **⚠️ GOOD** |

### Systemic Issues
- Best of the 5 — Mermaid + annotation cards pattern works well
- Could improve with light theme support

---

## Summary

| Example | Overall | Gate |
|---------|---------|------|
| Pitch Deck | 5.4 | ❌ FAIL |
| SaaS Dashboard | 7.2 | 🔧 NEEDS WORK |
| AI Timeline | 5.4 | ❌ FAIL |
| Comparison Infographic | 6.4 | 🔧 NEEDS WORK |
| System Architecture | 7.6 | ⚠️ GOOD |

**Average: 6.4/10 — 🔧 NEEDS WORK**

**None pass SHIP (≥9.0). None even pass GOOD (≥8.0) except architecture (barely).**

## Top Systemic Issues (SKILL.md fixes needed)

1. **[CRITICAL] Invisible/broken hero text** — pitch deck hero is blank. Need explicit color rules for text on gradient backgrounds.
2. **[CRITICAL] Missing light theme** — most examples have no `.theme-light` CSS at all. SKILL.md says required but skill doesn't enforce.
3. **[CRITICAL] Missing print styles** — `@media print` absent in most. SKILL.md says required but not enforced.
4. **[HIGH] Timeline cards too small** — need minimum sizing guidance.
5. **[HIGH] Chart.js not rendering in some cases** — comparison infographic has empty chart sections.
6. **[HIGH] Menu class inconsistency** — some use different class names than `.viz-menu`.
7. **[MEDIUM] No Inter font** — examples use system fonts only despite SKILL.md now requiring Inter.
8. **[MEDIUM] No entrance animations** — most lack @keyframes entirely.
9. **[MEDIUM] No reduced-motion support** — accessibility gap.
10. **[LOW] Donut chart color palettes** — need curated chart colors in SKILL.md.
