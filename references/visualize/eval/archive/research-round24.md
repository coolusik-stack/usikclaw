# R24 Research Findings

## 1. Apple Typography Patterns
- **Letter-spacing:** -0.03em on hero headings, -0.015em on subheadings, normal on body
- **Weight hierarchy:** 700 (bold) for h1 not 800 — Apple uses SF Pro Display which is optically balanced at 700
- **Font size scale:** Much larger than typical — hero titles 56-80px, section titles 40-48px, body 17-21px
- **Line-height:** 1.05-1.08 for large headings (extremely tight), 1.4-1.5 for body
- **Color:** Near-white (#f5f5f7) on dark, not pure white. Secondary text at ~60% opacity
- **Key insight:** Apple NEVER uses gradient text on headings. Clean solid colors only.

## 2. Stripe Dashboard Patterns
- **Cards:** No gradient borders ever. 1px border with rgba(0,0,0,0.05) in light / rgba(255,255,255,0.06) in dark
- **Shadows:** Extremely subtle — `0 1px 3px rgba(0,0,0,0.08)` base, `0 4px 12px rgba(0,0,0,0.05)` on hover
- **Border radius:** 8px consistently (not 12px, not 16px)
- **Card hover:** Just shadow elevation, NO translateY or scale transform
- **Background:** Pure #0a2540 (navy) for dark, #f6f9fc for light — NOT pure black
- **Typography:** 600 weight for card titles, 400 for body, 500 for labels
- **Spacing:** 32px card padding, 24px gap between cards

## 3. Vercel/Geist Dark Theme
- **Background:** #000000 (pure black) with #111111 surfaces — much simpler than gradient-heavy approaches
- **Border:** rgba(255,255,255,0.08) — extremely subtle
- **Text:** #ededed (not pure white), secondary #888888
- **Accent:** Single blue (#0070f3) used very sparingly
- **No decorative elements:** Zero orbs, zero glows, zero gradient borders
- **Cards:** background #111, 1px border, no shadow in dark mode

## 4. Premium Card Design (No Gradients)
- **The rule:** Premium = restraint. One border, one shadow level, one radius
- **Shadow layers:** `0 0 0 1px rgba(0,0,0,0.03), 0 2px 4px rgba(0,0,0,0.05)` — barely visible
- **Hover:** Shadow deepens slightly, no transform. `0 0 0 1px rgba(0,0,0,0.03), 0 4px 8px rgba(0,0,0,0.08)`
- **Anti-patterns to remove:** gradient top-borders, color-coded left borders, scale(1.02) transforms, glow effects

## 5. Chart.js Readability
- **Minimum font size:** 14px for axis labels, 16px for chart titles
- **Padding:** `layout: { padding: { top: 20, right: 20, bottom: 20, left: 20 } }`
- **Axis ticks:** `font: { size: 13, weight: 500 }`, maxRotation: 0 for horizontal labels
- **Grid:** Very faint — `color: 'rgba(0,0,0,0.04)'` in light, `'rgba(255,255,255,0.04)'` in dark
- **Tooltip:** `padding: 12`, `cornerRadius: 8`, `titleFont: { size: 14 }`, `bodyFont: { size: 13 }`
- **Point radius:** 0 by default, 6 on hover for clean lines

## 6. Infographic vs Dashboard
- **Infographic:** Single narrative flow (top to bottom), large hero numbers, editorial typography, section dividers, icons as visual anchors, designed to be read sequentially
- **Dashboard:** Grid layout, equal-weight cards, interactive filters, real-time data focus
- **Key difference:** Infographics tell a STORY. Dashboards present DATA.
- **Comparison-as-infographic:** Should have a clear winner/narrative, use visual metaphors (scales, arrows), flowing sections, not a grid of equal cards
