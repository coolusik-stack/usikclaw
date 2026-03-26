# Eval-First Rebuild: Implementation Summary

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a fully automated 3-layer evaluation pipeline and self-improvement loop for the Visualize plugin.

**Architecture:** Playwright-based DOM audit pipeline + Claude vision API scoring, orchestrated by a standalone Node.js tool. The improvement loop is a prompt (not a persistent agent) that any caller can follow.

**Tech Stack:** Node.js (ES modules), Playwright, @anthropic-ai/sdk, Claude Sonnet (vision eval)

---

## What Was Built

### Task 1: Pipeline Infrastructure (COMPLETE)

**Files created:**
- `eval/pipeline/package.json` — dependencies: playwright, @anthropic-ai/sdk
- `eval/pipeline/node_modules/` — installed (gitignored)

### Task 2: DOM Check Modules — Layer 2 (COMPLETE)

7 modular check files, each exports `runChecks(page)`:

| File | Category | Checks | Weight |
|------|----------|--------|--------|
| `checks/theme.js` | Theme & Styling | 6 checks | ~20 pts |
| `checks/menu.js` | Menu System | 8 checks | ~14 pts |
| `checks/typography.js` | Typography | 6 checks | ~15 pts |
| `checks/layout.js` | Layout | 6 checks | ~15 pts |
| `checks/accessibility.js` | Accessibility | 6 checks | ~15 pts |
| `checks/charts.js` | Charts (conditional) | 5 checks | ~10 pts |
| `checks/technical.js` | Technical | 8 checks | ~15 pts |

**Total: 45 automated checks, normalized to 0-100 score.**

### Task 3: Format Detection — Layer 1 (COMPLETE)

**File:** `eval/pipeline/format-detect.js`

Detects 10 format types from DOM signals:
- slide-deck, carousel, poster-9x16, poster-1x1, dashboard
- infographic, timeline, comparison, cheatsheet, flowchart
- Falls back to "generic" below 30% confidence

### Task 4: Pipeline Orchestrator (COMPLETE)

**File:** `eval/pipeline/run.js`

Usage:
```bash
# Single file
node run.js --file path/to/file.html

# Directory (all .html files)
node run.js --dir path/to/examples/

# With round number + vision eval
node run.js --dir path/to/dir/ --round 40 --vision
```

Features:
- Opens files in headless Chromium
- Captures console errors
- Runs format detection
- Runs all 45 DOM checks
- Takes screenshots (dark/light 1440px, dark mobile 375px)
- Extra slide screenshots for slide decks
- Calculates Layer 2 score
- Optionally runs Layer 3 vision eval
- Outputs JSON results to `eval/rounds/round-{N}/scores.json`
- Prints summary with quality gate

### Task 5: Vision Evaluation Helper — Layer 3 (COMPLETE)

**File:** `eval/pipeline/vision-eval.js`

Helper module that provides:
- `prepareVisionEval()` — generates the calibrated prompt + screenshot paths for the agent
- `calculateScore()` — computes weighted overall from agent-provided dimension scores
- `EVALUATION_PROMPT` — exported prompt text for use in documentation

Layer 3 is performed by the AI agent (Claude Code, OpenClaw, etc.) using its built-in vision capabilities. The pipeline captures screenshots; the agent evaluates them.

7 dimensions scored:
- D1. First Impression (15%)
- D2. Typography (15%)
- D3. Color (10%)
- D4. Layout (15%)
- D5. Content (15%)
- D6. Information Architecture (20%)
- D7. Format Execution (10%)

### Task 6: Self-Improvement Loop Prompt (COMPLETE)

**File:** `eval/pipeline/LOOP-PROMPT.md`

Complete instructions for any agent to run one improvement round:
0. Setup (clone, read state)
1. Generate (persona-driven random prompts)
2. Evaluate (3-layer pipeline)
3. Analyze (root cause in SKILL.md)
4. Fix (skill + references)
5. Re-test (worst output)
6. Finalize (commit, push)
7. Report

### Task 7: Eval Directory Restructure (COMPLETE)

- Archived 42 old eval files to `eval/archive/`
- Archived 32 screenshot directories to `eval/archive/screenshots/`
- Deleted 3 one-time scripts (fix-theme.py, apply-r36-fixes.py, fix-round38.js)
- Created `eval/rounds/` structure with round-39 baseline
- Wrote `eval/EVAL.md` (3-layer scoring specification)
- Rewrote `eval/LOOP.md` (v4 — Pipeline-First)

### Task 8: Contradiction Fixes (COMPLETE)

- **Card hover:** Removed `translateY(-4px) scale(1.02)` from `animations.md`, kept shadow-only
- **Emoji audit:** `ai-timeline.html` uses emojis only in menu (skeleton pattern, acceptable)
- **CHANGELOG:** Updated to cover v0.1.0, v0.2.0, v0.3.0 in Keep a Changelog format

### Task 9: .gitignore Updates (COMPLETE)

Added exclusions for:
- `eval/pipeline/node_modules/`
- `eval/pipeline/package-lock.json`
- `eval/rounds/*/generated/` (large generated files)
- `eval/rounds/*/screenshots/` (large binary files)

---

## Baseline Results

First pipeline run on all 15 examples (Layer 2 only):

| File | Format | L2 Score |
|------|--------|----------|
| cheatsheet-git.html | cheatsheet | 100/100 |
| slide-deck-demo.html | slide-deck | 100/100 |
| startup-pitch-deck.html | slide-deck | 100/100 |
| event-poster.html | dashboard* | 98/100 |
| process-guide.html | infographic | 98/100 |
| quote-card.html | dashboard* | 98/100 |
| cheatsheet-claude-code.html | cheatsheet | 96/100 |
| status-report.html | timeline | 96/100 |
| comparison-infographic.html | infographic | 95/100 |
| ai-timeline.html | timeline | 94/100 |
| carousel-korean.html | poster-9x16 | 94/100 |
| system-architecture.html | infographic | 94/100 |
| carousel-infographic.html | poster-9x16 | 93/100 |
| saas-dashboard.html | dashboard | 89/100 |
| carousel-threads.html | flowchart* | 82/100 |

**Average: 9.51/10 | Gate: SHIP** (Layer 2 only)

\* Format detection needs refinement for: event-poster, quote-card, carousel-threads

---

## Remaining Work

### P0: Must Do

1. **First loop round** — Pass `eval/pipeline/LOOP-PROMPT.md` to a Claude Code or OpenClaw agent to run one full improvement cycle. The agent runs Layer 2 via the pipeline, evaluates Layer 3 visually, analyzes failures, and fixes SKILL.md.

2. **Capture calibration anchors** — Take screenshots of Stripe/Linear for the 9-anchor and best current example for the 7-anchor. Save to `eval/pipeline/calibration/`.

### P1: Should Do

3. **Improve format detection** — event-poster, quote-card, and carousel-threads are misclassified. Add format-specific DOM signatures for these types.

4. **Format appropriateness judgment** — Layer 1 currently only detects format. The agent running the loop should also judge: "Given prompt X, is format Y appropriate?"

5. **Add interactivity check module** — The design doc lists interactivity as a separate category. Currently it's in technical.js but could be its own module with format-specific interaction requirements.

### P2: Nice to Have

6. **Reference restructuring** — Once eval data shows which rules are most violated, consolidate reference files around actual problem areas.

7. **Eval report visualization** — Generate an HTML dashboard from scores.json (using the visualize skill itself — dogfooding).
