# ⚡ Visualize

**Turn any idea into a beautiful HTML visualization — with one prompt.**

A [Claude Code](https://code.claude.com) plugin that creates stunning, self-contained HTML visualizations from natural language. Slide decks, dashboards, infographics, flowcharts, timelines, and more — all as single HTML files you can open anywhere.

> HTML is not a "website." It's a visualization tool. Code is cheap. Everyone should feel empowered to visualize anything.

## What It Does

Describe what you want to visualize → get a production-quality HTML file.

```
You: "Create a pitch deck for my AI startup"
→ pitch-deck.html (interactive slides, dark/light themes, keyboard nav, export to PNG/PDF)

You: "Visualize this CSV data as a dashboard"
→ sales-dashboard.html (KPI cards, Chart.js graphs, responsive grid)

You: "Make an infographic about remote work trends"
→ remote-work-infographic.html (big stats, scroll animations, print-ready)
```

### Supported Visualization Types

| Type | Description |
|------|-------------|
| 🎯 **Slide Deck** | Presentations with keyboard nav, transitions, speaker notes |
| 📊 **Dashboard** | KPI cards, charts, metrics — Chart.js powered |
| 📈 **Infographic** | Scrollable visual storytelling with animations |
| 🔀 **Flowchart** | Process diagrams, decision trees, architecture diagrams |
| 📅 **Timeline** | Chronological events, roadmaps, milestones |
| ⚖️ **Comparison** | Side-by-side features, pros/cons matrices |
| 📉 **Data Viz** | Bar, line, pie, radar charts from raw data |
| 📄 **One-Pager** | Landing pages, summaries, briefs |
| 🧠 **Mind Map** | Concept relationships, brainstorming visuals |
| 📋 **Kanban** | Status boards, categorized item tracking |

## Why This Over Gamma / Canva / PowerPoint?

| | Gamma/Canva | PowerPoint | **Visualize** |
|---|---|---|---|
| **Cost** | $10-40/mo | $100+ license | **Free** |
| **Output** | Proprietary | .pptx | **Standard HTML** |
| **Customization** | Template-limited | Manual | **Infinite** |
| **Interactivity** | Limited | None | **Full HTML/CSS/JS** |
| **AI-native** | Bolted-on | Copilot add-on | **Core workflow** |
| **Offline** | No | Yes | **Yes** |
| **Version control** | No | Barely | **Yes (it's text)** |
| **File size** | N/A | 10MB+ | **~20KB** |

## Features

Every visualization includes:

- 🌙 **Dark / Light / Auto themes** — toggle via hamburger menu, persisted to localStorage
- 📥 **Download as PNG** — 2x retina quality via html-to-image
- 🖨️ **Print / Save PDF** — optimized `@media print` styles
- 📱 **Responsive** — works on desktop, tablet, and mobile
- ⌨️ **Keyboard navigation** — arrow keys for slide decks
- 🎨 **Beautiful defaults** — professional typography, HSL color system, 8px spacing grid
- 📦 **Single file** — everything inline, zero dependencies beyond optional CDN libraries
- ♿ **Accessible** — semantic HTML, WCAG AA contrast

### CDN Libraries (optional, used when beneficial)

- [Chart.js](https://www.chartjs.org/) — beautiful charts with zero config
- [D3.js](https://d3js.org/) — complex custom data visualizations
- [Mermaid](https://mermaid.js.org/) — diagrams from text definitions
- [Three.js](https://threejs.org/) — 3D visualizations
- [Leaflet](https://leafletjs.com/) — interactive maps
- [Reveal.js](https://revealjs.com/) — full-featured slide engine

## Installation

### Claude Code Plugin (recommended)

```bash
# Step 1: Add the marketplace (one-time)
claude plugin marketplace add careerhackeralex/visualize

# Step 2: Install the plugin
claude plugin install visualize@careerhackeralex
```

To update later:
```bash
claude plugin update visualize@careerhackeralex
```

### Manual Installation

```bash
# Clone the repo
git clone https://github.com/careerhackeralex/visualize.git

# Claude Code auto-discovers plugins with .claude-plugin/plugin.json
# Just open Claude Code in the cloned directory, or add it as a plugin dir:
claude plugin install --plugin-dir /path/to/visualize
```

## Usage

Once installed, just ask Claude Code to visualize anything:

```
"Create a presentation about our Q4 results"
"Visualize this data as a dashboard: [paste CSV/JSON]"
"Make an infographic summarizing this article: [paste URL]"
"Show me a flowchart of our deployment process"
"Create a timeline of AI milestones"
```

The skill triggers automatically on visualization-related requests.

## Examples

See the [`examples/`](examples/) directory for sample outputs.

## Project Structure

```
visualize/
├── .claude-plugin/
│   └── plugin.json             # Plugin manifest
├── skills/
│   └── visualize/
│       ├── SKILL.md            # Core skill instructions
│       └── references/         # Design system, skeleton, patterns
├── examples/                   # 15 sample HTML outputs
├── eval/                       # Quality assurance & eval loop
├── research/                   # Design research notes
├── CLAUDE.md                   # Claude Code context file
├── README.md                   # This file
└── LICENSE                     # MIT
```

## How It Works

1. You describe what you want to visualize
2. Claude Code reads the skill instructions (design system, patterns, best practices)
3. It generates a single `.html` file with inline CSS/JS
4. Open in any browser — done

The skill encodes professional design knowledge (typography scales, color theory, spacing rhythm, animation best practices) so every output looks polished without manual design work.

## Contributing

We use a systematic evaluation loop to improve quality:

1. **Generate** — run test cases from `eval/stress-tests.md`
2. **Evaluate** — score outputs using the 8-dimension rubric
3. **Fix the skill** — update `SKILL.md` or references (not individual outputs)
4. **Re-evaluate** — verify the fix works across test cases
5. **Ship** when overall score ≥ 9.0 with no dimension below 8

See [`eval/LOOP.md`](eval/LOOP.md) for the full methodology.

### Quality Bar

We aim to produce visualizations that people would:
- Screenshot and share on social media
- Use in a real meeting without embarrassment
- Prefer over Gamma/Canva output
- Ask "how did you make this?"

The bar is not "good for AI-generated." The bar is **"good, period."**

## License

MIT — use it however you want.

## Credits

Built by [Career Hacker Alex](https://youtube.com/@CareerHackerAlex) (커리어해커 알렉스)

기술로 선한영향력을 만들고 싶습니다 — Create positive impact through technology.
