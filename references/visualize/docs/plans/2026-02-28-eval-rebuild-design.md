# Eval-First Rebuild: Self-Improving Visualize Skill

**Date:** 2026-02-28
**Status:** Approved
**Author:** Alex + Claude

## Problem

The visualize skill (v0.3.0) has run 39 eval rounds but scores remain volatile (8.33 → 5.67 between rounds) because:

1. **Evaluator inconsistency** — AI self-evaluation drifts as criteria interpretation shifts between sessions
2. **No deterministic baseline** — there's no reliable, repeatable measurement of output quality
3. **Fixed test prompts** — evaluating against predetermined types (1 deck, 1 dashboard, etc.) only tests the happy path, not real-world usage
4. **Score doesn't reflect what matters** — rules compliance ≠ visual appeal + good information architecture

Current state: Round 39, average 8.10 (ACCEPTABLE). Target: SHIP (9.0).

## Solution

Build a fully automated self-improvement loop that:

1. Simulates real users with random personas and prompts
2. Evaluates outputs with a 3-layer system (deterministic + vision model)
3. Traces failures back to skill instructions
4. Fixes the skill (not individual outputs)
5. Validates fixes by re-generating and re-scoring

Built specifically for visualize first. Generalize to other skills later.

## Design

### The Self-Improvement Loop (12 Steps)

```
Step 0  — Setup (install plugin, read state)
Step 1  — Generate (persona-driven random prompts)
Step 2  — Evaluate (3-layer scoring)
Step 3  — Analyze (root cause in SKILL.md)
Step 4  — Fix (skill + references)
Step 5  — Re-test (re-generate worst outputs)
Step 6  — Finalize (commit, push)
Step 7  — Report
```

### Step 0: Setup

- Install plugin from git (real user path):
  ```bash
  claude plugin marketplace add careerhackeralex/visualize
  claude plugin install visualize@careerhackeralex
  ```
- Clone repo to temp dir
- Read `eval/loop-state.json` — if gate is SHIP (≥9.0), stop
- If plateau detected (<0.3 improvement over 3 rounds AND loopsSinceResearch ≥ 5), switch to research mode

### Step 1: Generate — Persona-Driven Random Prompts

Instead of fixed test prompts per visualization type, the agent creates a **random persona** and generates **3 realistic prompts** that persona would actually ask.

**How it works:**

1. The agent invents a persona with context:
   - Role (e.g., "VP of Sales at a B2B SaaS company")
   - Situation (e.g., "preparing quarterly board update")
   - Skill level (e.g., "non-technical, wants something impressive fast")

2. From that persona, generate 3 prompts they'd realistically type:
   - e.g., "Create a slide deck showing our Q4 revenue growth, churn reduction, and 2026 targets"
   - e.g., "Make an infographic comparing our pricing tiers for the sales team"
   - e.g., "Visualize our customer journey funnel — 10k visitors → 2k signups → 500 trials → 120 paid"

3. Each round gets a **different persona**, ensuring diversity over time. No two rounds test the same scenario.

**Constraints on persona generation:**
- Must vary across industries, roles, and technical levels
- Must include at least 1 prompt that requires data visualization (charts)
- Must not repeat a persona archetype from the last 3 rounds (check loop-state.json history)
- Prompts should be natural language — not "make a dashboard", but the way a real person would describe what they need

**Why this is better than fixed prompts:**
- Tests format selection (did the skill pick the right format for an ambiguous request?)
- Tests content generation (does it create realistic data, not lorem ipsum?)
- Tests edge cases organically (Korean content, dense data, vague requests emerge naturally)
- Catches failure modes that curated test suites miss

Each output is generated via:
```bash
claude -p --dangerously-skip-permissions --model sonnet \
  "{persona prompt}"
```

Save outputs to `eval/rounds/round-{N}/generated/`.

### Step 2: Evaluate — 3-Layer Scoring

#### Layer 1: Format Appropriateness (Pass/Fail Gate)

Since prompts are random, the eval can't pre-know the expected format. Instead:

- **Detect what was generated** — Playwright inspects the DOM to classify: slide deck (100vw×100vh slides with nav), carousel (1080×1080 cards), poster (fixed dimensions, overflow:hidden), dashboard (grid + charts), infographic (long-scroll sections), etc.
- **Judge format fit** — Given the original prompt, does the chosen format make sense? A "quarterly board update" should be a slide deck or dashboard, not a quote card. This check uses a lightweight LLM call with the prompt + detected format.
- **Validate format execution** — Once format is identified, check format-specific rules:

| Format | Checks |
|--------|--------|
| Slide Deck | 16:9 viewport, slides fill screen, keyboard nav, slide counter, progress bar, theme-aware gradients |
| Carousel | 1080×1080 per card, swipe+arrow+keyboard nav, card counter, download individual cards |
| Poster (9:16) | 1080×1920, overflow:hidden, no scroll, space-between layout |
| Square (1:1) | 1080×1080, overflow:hidden, single-screen |
| Dashboard | Scrollable, CSS grid, KPI cards, ≥1 chart, filter/interaction |
| Infographic | Long-scroll, multiple sections, data-reveal, big stats |
| Timeline | Chronological markers, alternating or vertical layout, scroll-triggered |

If format is wrong for the prompt → score is 0, skip remaining layers.

#### Layer 2: Structural Quality (0-100, deterministic)

Playwright DOM audit — 30+ automated checks:

**Theme & Styling:**
- `html.theme-dark` and `html.theme-light` classes exist
- CSS custom properties defined (--bg, --surface, --text, --accent, --border)
- Theme toggle in menu cycles correctly (dark → light → auto)
- Both themes render without broken colors (no white-on-white, dark-on-dark)
- Inter font loaded from Google Fonts CDN

**Menu:**
- `.viz-menu` exists with toggle button
- Theme button present and functional
- Download PNG button present (html-to-image CDN loaded)
- Print/PDF button present

**Typography:**
- h1 > h2 > h3 > body font sizes (clear hierarchy)
- Minimum body font size ≥ 14px
- Minimum heading font size ≥ 20px
- Letter-spacing on headings (negative tracking)
- Font-weight hierarchy (700/600/400)

**Layout:**
- No horizontal overflow at 1440px, 768px, 375px widths
- Uses CSS grid or flexbox (not just block flow)
- Minimum section spacing ≥ 48px
- Card padding ≥ 24px

**Accessibility:**
- Semantic HTML (`<main>`, `<section>`, `<header>`)
- `@media print` styles present
- `@media (prefers-reduced-motion)` present
- Charts wrapped in `role="img"` with `aria-label`
- Skip-to-content link or landmark roles

**Technical:**
- Zero console errors on load
- Zero console warnings on load
- All top-level JS uses `var` (not `let`/`const`)
- File size < 200KB
- No external image URLs (unless user-provided)

**Interactivity:**
- At least 1 type-specific interaction beyond menu (filter, search, accordion, swipe, etc.)
- Entrance animations present (.animate classes or data-reveal)
- Hover states on interactive elements

**Charts (if present):**
- Chart.defaults.animation = false
- Tooltips enabled (not disabled)
- Container has explicit dimensions (≥300px height)
- maintainAspectRatio: false
- Theme-aware colors (reads CSS vars)

Each check: pass = full points, fail = 0. Weighted by importance. Total normalized to 0-100.

#### Layer 3: Visual & Information Architecture Quality (1-10, vision model)

Playwright captures screenshots:
- Dark theme at 1440px width
- Light theme at 1440px width
- Dark theme at 375px width (mobile)
- For slide decks: slides 1, 3, and last slide

Screenshots are sent to Claude vision model with a **calibrated evaluation prompt**:

```
You are evaluating an HTML visualization. Score each dimension 1-10.

CALIBRATION (use these as anchors — do not deviate):
- 10 = Apple keynote / Stripe dashboard level
- 9 = Linear, Vercel, Raycast level
- 8 = Polished SaaS product
- 7 = Good Bootstrap template
- 6 = Amateur but functional
- 5 = Multiple visible problems

DIMENSIONS:
D1. First Impression (15%) — Would you screenshot this? Does it feel premium?
D2. Typography (15%) — Clear hierarchy? Professional sizing/spacing?
D3. Color (10%) — Harmonious palette? Both themes look intentional?
D4. Layout (15%) — Good rhythm? Generous whitespace? Responsive?
D5. Content (15%) — Clear message? Real data? No filler?
D6. Information Architecture (20%) — Is content structured for the audience?
     Can you grasp the key message in 5 seconds? Logical flow?

Score each dimension with a number and one-sentence justification.
Overall = weighted average.
```

**Calibration anchors** — include 2-3 reference screenshots in the prompt:
- A known 7-score output (from eval history)
- A known 9-score output (from eval history or hand-crafted)
- These anchors are FIXED across all rounds, preventing evaluator drift

**Why 6 dimensions instead of 8:**
- Merged Interactivity and Technical into Layer 2 (they're deterministic — either the menu works or it doesn't)
- Added Information Architecture as its own dimension (was implicit before)
- Shareability is captured by First Impression (would you screenshot it?)

### Step 3: Analyze

For every issue found across all 3 layers:

1. **Trace to root cause** — Which instruction in SKILL.md or references is missing, unclear, contradictory, or buried?
2. **Categorize:**
   - Missing instruction (skill doesn't mention this at all)
   - Unclear instruction (mentioned but ambiguous)
   - Contradictory instruction (two references disagree)
   - Buried instruction (exists but too deep in reference files to be followed)
3. **Prioritize** by: frequency (affects multiple outputs) × severity (large score impact)
4. **Write analysis** to `eval/rounds/round-{N}/analysis.md`

### Step 4: Fix

1. Uninstall plugin:
   ```bash
   claude plugin uninstall visualize@careerhackeralex
   ```
2. Working in the cloned repo:
   - Fix SKILL.md first — add missing instructions, clarify vague ones, remove contradictions
   - SKILL.md must stay under 5,000 words
   - Fix references — skeleton.md priority, then design-system.md, then others
   - Consolidate/deduplicate where analysis shows overlap causes confusion
3. Commit fixes:
   ```bash
   git commit -m "eval: round {N} fixes — [summary of changes]"
   git push
   ```

### Step 5: Re-test

1. Re-install from git:
   ```bash
   claude plugin marketplace update careerhackeralex
   claude plugin install visualize@careerhackeralex
   ```
2. Re-generate the worst-scoring output from Step 1 (the one with lowest overall score)
3. Re-evaluate with the same 3-layer pipeline
4. Compare before/after scores
5. If regression detected on other dimensions → revert fix, try different approach

### Step 6: Finalize

- Copy improved examples to `examples/` (if they're better than existing)
- Update `eval/loop-state.json`:
  ```json
  {
    "currentRound": N,
    "loopsSinceResearch": N,
    "lastAverage": X.XX,
    "gate": "ACCEPTABLE|SHIP|etc",
    "lastPersona": "description of persona used",
    "history": [...]
  }
  ```
- Commit and push:
  ```bash
  git commit -m "eval: round {N} complete — avg {score}, gate {gate}"
  git push
  ```

### Step 7: Report

Output a summary:
- Round number
- Persona used + 3 prompts
- Per-file scores (Layer 2 structural + Layer 3 vision, overall)
- Delta from last round
- Top SKILL.md changes made
- Before/after comparison on re-tested output
- Commit hash
- Gate status (ACCEPTABLE / SHIP / VIRAL)

### Quality Gates

| Gate | Overall Avg | Min Score | Action |
|------|-------------|-----------|--------|
| VIRAL | ≥ 9.5 | all ≥ 9 | Stop. Screenshot-worthy. |
| SHIP | ≥ 9.0 | all ≥ 8 | Stop. Production-ready. |
| ACCEPTABLE | ≥ 8.0 | all ≥ 7 | Continue iterating. |
| NEEDS WORK | ≥ 7.0 | any < 7 | Continue, prioritize weak areas. |
| FAIL | < 7.0 | any < 5 | Major rework needed. |

### Research Mode

Triggered when: `loopsSinceResearch >= 5` AND score plateau (< 0.3 improvement over 3 rounds).

Activities:
- Web search for current design trends
- Study reference sites (Stripe, Linear, Vercel, Apple)
- Analyze what the best-scoring outputs have in common
- Document findings in `eval/rounds/round-{N}/research.md`
- Update SKILL.md + references with new techniques
- Reset `loopsSinceResearch` counter

## Repo Cleanup (Parallel Track)

### CHANGELOG

Update to cover v0.2.0 and v0.3.0. Reconstruct from eval round history and git log.

### Eval Directory Restructure

**New structure:**
```
eval/
├── loop-state.json              # round state + history
├── stress-tests.md              # legacy test prompts (reference only)
├── LOOP.md                      # rewritten for new pipeline
├── EVAL.md                      # 3-layer scoring spec
├── pipeline/                    # automated eval code
│   ├── package.json
│   ├── run.js                   # orchestrator
│   ├── checks/                  # DOM audit checks (modular)
│   │   ├── theme.js
│   │   ├── menu.js
│   │   ├── typography.js
│   │   ├── layout.js
│   │   ├── accessibility.js
│   │   ├── charts.js
│   │   └── technical.js
│   ├── format-detect.js         # auto-detect visualization format
│   ├── vision-eval.js           # vision model scoring
│   └── calibration/             # anchor screenshots (fixed)
│       ├── anchor-7.png
│       ├── anchor-9.png
│       └── anchors.md           # description of why each is that score
├── rounds/                      # per-round results
│   └── round-{N}/
│       ├── persona.md           # persona + prompts
│       ├── generated/           # HTML outputs
│       ├── screenshots/         # dark/light/mobile PNGs
│       ├── scores.json          # all 3 layers
│       ├── analysis.md          # root cause analysis
│       └── report.md            # summary
└── archive/                     # rounds 1-38
```

**Deleted:** `fix-theme.py`, `apply-r36-fixes.py`, `fix-round38.js` (one-time scripts).

**Archived:** Rounds 1-38 markdown files and screenshots → `eval/archive/`.

### Contradiction Fixes

1. **Card hover:** Resolve to shadow-only (matches visual restraint philosophy). Remove transform example from animations.md.
2. **Emoji vs SVG:** Fix ai-timeline.html to use inline SVGs. Enforce "never emojis" rule.

### Reference Restructuring

Deferred until eval pipeline produces data on which rules are most violated. Then consolidate around actual problem areas.

## Implementation Priority

| # | Component | Priority | Depends On |
|---|-----------|----------|------------|
| 1 | Eval pipeline (Playwright + DOM checks) | P0 | Nothing |
| 2 | Vision model eval (calibration + scoring) | P0 | #1 |
| 3 | Self-improvement loop agent (12-step orchestrator) | P0 | #1, #2 |
| 4 | Repo cleanup (archive, restructure, changelog) | P1 | Nothing |
| 5 | Contradiction fixes (card hover, emoji) | P1 | Nothing |
| 6 | Reference restructuring | P2 | #3 (needs eval data) |

## Success Criteria

- [ ] Eval scores are consistent between rounds (variance < 0.5 on same input)
- [ ] The loop runs autonomously end-to-end without human intervention
- [ ] Format detection correctly identifies visualization type from DOM
- [ ] Vision model scoring stays within ±0.5 of calibration anchors
- [ ] Quality gate reaches SHIP (9.0) with the new scoring system
- [ ] Repo is clean enough for a new contributor to understand in 10 minutes

## Resolved Questions

1. **Where does the loop live?**
   **Eval pipeline as code in the repo (`eval/pipeline/`), loop as a skill/prompt.**
   The pipeline (Playwright checks, vision scoring) is reusable tooling that lives in the repo. The 12-step loop is a set of instructions (skill/prompt) that any caller can follow — a cron job, a manual `claude -p` invocation, or a Claude Code agent. The caller decides how to invoke it. Not a persistent agent.

2. **Vision model cost?**
   **Acceptable.** ~4-6 vision API calls per round (a few dollars). Worth it for consistent aesthetic evaluation.

3. **Calibration anchor selection?**
   **Both internal + external references.**
   - 9-anchor: Screenshot of a real site (Stripe dashboard or Linear landing page) — grounds scoring in real-world quality
   - 7-anchor: Best current example output from the visualize skill — shows what "good for this tool" looks like
   - These anchors are FIXED and never change between rounds

4. **Research mode depth?**
   **Focused: 3-5 sites only.** Check Stripe, Linear, Vercel, Apple, and 1 trending design site. Extract specific techniques that can be encoded into SKILL.md. 30 minutes max. No rabbit holes.
