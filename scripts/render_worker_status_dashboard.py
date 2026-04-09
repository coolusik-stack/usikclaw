#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def trim_note(value: str, limit: int = 220) -> str:
    value = " ".join(str(value).split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def read_lines(path: Path, limit: int = 8) -> list[str]:
    if not path.exists():
        return []
    lines = [trim_note(line.rstrip("\n")) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return lines[-limit:]


def file_mtime_kst(path: Path) -> str:
    dt = datetime.fromtimestamp(path.stat().st_mtime)
    return dt.strftime("%Y-%m-%d %H:%M")


def stage_badge(stage: str) -> tuple[str, str]:
    s = (stage or "unknown").lower()
    if s in {"running", "active", "processing"}:
        return ("running", "Running")
    if s in {"idle", "waiting", "queued"}:
        return ("idle", "Idle")
    if s in {"done", "completed", "complete"}:
        return ("done", "Done")
    if s in {"warning", "stalled", "attention"}:
        return ("warning", "Attention")
    return ("unknown", stage or "Unknown")


def build_payload() -> dict[str, Any]:
    progress_path = GENERATED / "vape_500_progress.json"
    progress_md_path = GENERATED / "vape_500_progress.md"
    batch_log_path = GENERATED / "logs" / "vape_500_batch.log"
    cron_log_path = GENERATED / "logs" / "vape_500_cron.log"
    hotspot_log_path = GENERATED / "logs" / "vape_hotspot_wave2.log"
    source_log_path = GENERATED / "logs" / "vape_sms_hotspot_expand.log"
    hotspot_summary_path = GENERATED / "vape_hotspot_wave2_summary.json"
    source_summary_path = GENERATED / "vape_sms_hotspot_expand_summary.json"
    ambiguous_summary_path = GENERATED / "vape_ambiguous_phone_revalidation_summary.json"

    progress = read_json(progress_path)
    hotspot_summary = read_json(hotspot_summary_path)
    source_summary = read_json(source_summary_path)
    ambiguous_summary = read_json(ambiguous_summary_path)

    proof = progress.get("verification", {}).get("proof", [])
    recent_proof = proof[-6:]
    counts = progress.get("counts", {})
    current_batch = progress.get("currentBatch", {})

    workers = [
        {
            "name": "Verification loop",
            "task": "Seoul vape 500 coordinator",
            "status": progress.get("status", "unknown"),
            "stage": current_batch.get("stage", "unknown"),
            "lastUpdate": progress.get("lastVerifiedAtKst", file_mtime_kst(progress_path)),
            "summary": f"{counts.get('phoneReady', 0)} SMS-ready contacts out of {counts.get('total', 0)} verified stores.",
            "metrics": [
                {"label": "Verified stores", "value": counts.get("total", 0)},
                {"label": "SMS-ready", "value": counts.get("phoneReady", 0)},
                {"label": "Needs check", "value": counts.get("needsCheck", 0)},
            ],
            "notes": [trim_note(item) for item in recent_proof],
            "sources": [str(progress_path.relative_to(ROOT)), str(progress_md_path.relative_to(ROOT))],
        },
        {
            "name": "Queue watcher",
            "task": "Batch and cron monitor",
            "status": "running",
            "stage": "waiting for new queued candidates",
            "lastUpdate": file_mtime_kst(batch_log_path),
            "summary": "The recurring worker is still writing heartbeat-style queue checks.",
            "metrics": [
                {"label": "Recent batch checks", "value": len(read_lines(batch_log_path, 20))},
                {"label": "Recent cron checks", "value": len(read_lines(cron_log_path, 20))},
            ],
            "notes": read_lines(batch_log_path, 6),
            "sources": [str(batch_log_path.relative_to(ROOT)), str(cron_log_path.relative_to(ROOT))],
        },
        {
            "name": "Hotspot expansion",
            "task": "Naver search wave 2",
            "status": "completed",
            "stage": "results merged into master CSV",
            "lastUpdate": file_mtime_kst(hotspot_log_path),
            "summary": f"Added {hotspot_summary.get('added_total', 0)} rows and lifted SMS-ready count from {hotspot_summary.get('before_sms', 0)} to {hotspot_summary.get('after_sms', 0)}.",
            "metrics": [
                {"label": "Rows added", "value": hotspot_summary.get("added_total", 0)},
                {"label": "Queries scanned", "value": sum(hotspot_summary.get("query_counts", {}).values())},
                {"label": "After SMS-ready", "value": hotspot_summary.get("after_sms", 0)},
            ],
            "notes": read_lines(hotspot_log_path, 7),
            "sources": [str(hotspot_log_path.relative_to(ROOT)), str(hotspot_summary_path.relative_to(ROOT))],
        },
        {
            "name": "Source locator expansion",
            "task": "Brand/store locator sweep",
            "status": "completed",
            "stage": "deduped and consolidated",
            "lastUpdate": file_mtime_kst(source_log_path),
            "summary": f"Gross +{source_summary.get('gross_added_total', 0)} candidates from locator sources, net +{source_summary.get('net_added_total', 0)} after dedupe.",
            "metrics": [
                {"label": "Net added", "value": source_summary.get("net_added_total", 0)},
                {"label": "Deduped away", "value": source_summary.get("dedupe_removed", 0)},
                {"label": "Ambiguous skipped", "value": source_summary.get("ambiguous_phone_skips", 0)},
            ],
            "notes": [
                trim_note(f"martha: {source_summary.get('source_counts', {}).get('martha', 0)}"),
                trim_note(f"litmus: {source_summary.get('source_counts', {}).get('litmus', 0)}"),
                trim_note(f"justfog: {source_summary.get('source_counts', {}).get('justfog', 0)}"),
                trim_note(f"unresolved fixed: {source_summary.get('unresolved_fixed', 0)}"),
            ],
            "sources": [str(source_log_path.relative_to(ROOT)), str(source_summary_path.relative_to(ROOT))],
        },
        {
            "name": "Ambiguous phone recovery",
            "task": "Strict revalidation pass",
            "status": "completed",
            "stage": "low-confidence leftovers held back",
            "lastUpdate": ambiguous_summary.get("lastVerifiedAtKst", file_mtime_kst(ambiguous_summary_path)),
            "summary": f"Recovered {ambiguous_summary.get('recovered_sms_ready_count', 0)} SMS-ready stores from {ambiguous_summary.get('ambiguous_phone_candidates', 0)} ambiguous candidates.",
            "metrics": [
                {"label": "Recovered", "value": ambiguous_summary.get("recovered_sms_ready_count", 0)},
                {"label": "Left unresolved", "value": ambiguous_summary.get("unresolved_leftovers", 0)},
                {"label": "After SMS-ready", "value": ambiguous_summary.get("after_sms", 0)},
            ],
            "notes": [trim_note(item) for item in ambiguous_summary.get("recovered_store_names", [])[:7]],
            "sources": [str(ambiguous_summary_path.relative_to(ROOT))],
        },
    ]

    summary = {
        "project": progress.get("project", "worker-status"),
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "headline": "Worker status dashboard",
        "overview": {
            "workers": len(workers),
            "running": sum(1 for w in workers if w["status"] == "running"),
            "completed": sum(1 for w in workers if w["status"] == "completed"),
            "smsReady": counts.get("phoneReady", 0),
            "verifiedStores": counts.get("total", 0),
            "needsCheck": counts.get("needsCheck", 0),
        },
        "guidance": [
            "A moving last update time or fresh log lines means a worker is still alive.",
            "Running means the loop is active now. Completed means its output has already been folded into the dataset.",
            "If queue watcher keeps advancing but verification loop stays idle, the system is waiting on new candidates rather than being broken.",
        ],
        "workers": workers,
    }
    return summary


def render_html(payload: dict[str, Any]) -> str:
    overview = payload["overview"]
    worker_cards = []
    table_rows = []

    for worker in payload["workers"]:
        badge_class, badge_text = stage_badge(worker["status"])
        notes = "".join(f"<li>{html.escape(str(note))}</li>" for note in worker.get("notes", [])) or "<li>No recent notes</li>"
        metrics = "".join(
            f"<div class='metric'><span>{html.escape(str(m['label']))}</span><strong>{html.escape(str(m['value']))}</strong></div>"
            for m in worker.get("metrics", [])
        )
        sources = "".join(f"<code>{html.escape(src)}</code>" for src in worker.get("sources", []))
        worker_cards.append(
            f"""
            <article class='card worker-card'>
              <div class='card-top'>
                <div>
                  <p class='eyebrow'>{html.escape(worker['task'])}</p>
                  <h3>{html.escape(worker['name'])}</h3>
                </div>
                <span class='badge {badge_class}'>{badge_text}</span>
              </div>
              <div class='meta-grid'>
                <div><span>Stage</span><strong>{html.escape(worker['stage'])}</strong></div>
                <div><span>Last update</span><strong>{html.escape(worker['lastUpdate'])}</strong></div>
              </div>
              <p class='summary'>{html.escape(worker['summary'])}</p>
              <div class='metric-grid'>{metrics}</div>
              <div class='log-box'>
                <div class='log-title'>Recent notes / log snippets</div>
                <ul>{notes}</ul>
              </div>
              <div class='sources'>{sources}</div>
            </article>
            """
        )
        table_rows.append(
            f"<tr><td>{html.escape(worker['name'])}</td><td>{html.escape(worker['status'])}</td><td>{html.escape(worker['stage'])}</td><td>{html.escape(worker['lastUpdate'])}</td><td>{html.escape(worker['summary'])}</td></tr>"
        )

    guidance = "".join(f"<li>{html.escape(item)}</li>" for item in payload.get("guidance", []))

    return f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{html.escape(payload['headline'])}</title>
  <meta http-equiv='refresh' content='120'>
  <style>
    :root {{
      --bg: #07111f;
      --bg-2: #0f1d33;
      --panel: rgba(11, 23, 41, 0.82);
      --panel-strong: rgba(8, 18, 33, 0.95);
      --line: rgba(148, 163, 184, 0.18);
      --text: #edf3ff;
      --muted: #9caecc;
      --cyan: #79e3ff;
      --mint: #7ef0c1;
      --amber: #ffd166;
      --rose: #ff8aa1;
      --violet: #baa7ff;
      --shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
      --radius: 24px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(121, 227, 255, 0.16), transparent 28%),
        radial-gradient(circle at top right, rgba(186, 167, 255, 0.2), transparent 34%),
        linear-gradient(180deg, #0d1830 0%, #08111d 45%, #050b14 100%);
      min-height: 100vh;
    }}
    body::before {{
      content: '';
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
      background-size: 28px 28px;
      mask-image: linear-gradient(180deg, rgba(0,0,0,0.55), transparent 88%);
    }}
    .wrap {{ width: min(1320px, calc(100vw - 32px)); margin: 0 auto; padding: 28px 0 72px; position: relative; z-index: 1; }}
    .hero, .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius); backdrop-filter: blur(18px); box-shadow: var(--shadow); }}
    .hero {{ padding: 28px; overflow: hidden; position: relative; }}
    .hero::after {{ content: ''; position: absolute; inset: auto -10% -35% 40%; height: 320px; background: radial-gradient(circle, rgba(121,227,255,0.28), transparent 62%); filter: blur(20px); }}
    .eyebrow {{ margin: 0 0 10px; color: var(--cyan); text-transform: uppercase; letter-spacing: 0.16em; font-size: 12px; }}
    h1 {{ margin: 0; font-size: clamp(34px, 5vw, 68px); line-height: 0.95; max-width: 9ch; }}
    .hero-grid {{ display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 18px; align-items: end; }}
    .lead {{ color: var(--muted); font-size: 16px; line-height: 1.7; max-width: 72ch; margin: 16px 0 0; }}
    .timestamp {{ margin-top: 16px; color: #d8e6ff; font-size: 13px; }}
    .stats {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .stat {{ background: var(--panel-strong); border: 1px solid var(--line); border-radius: 18px; padding: 18px; min-height: 120px; display: flex; flex-direction: column; justify-content: space-between; }}
    .stat span {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; }}
    .stat strong {{ font-size: clamp(28px, 4vw, 42px); line-height: 1; }}
    .stat em {{ font-style: normal; color: #d7e6ff; font-size: 14px; }}
    .section {{ margin-top: 18px; }}
    .section-title {{ display: flex; justify-content: space-between; align-items: end; gap: 12px; margin: 0 0 12px; }}
    .section-title h2 {{ margin: 0; font-size: 22px; }}
    .section-title p {{ margin: 0; color: var(--muted); font-size: 14px; }}
    .cards {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    .worker-card {{ padding: 20px; }}
    .card-top {{ display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }}
    h3 {{ margin: 0; font-size: 26px; line-height: 1.08; }}
    .badge {{ padding: 10px 14px; border-radius: 999px; font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid transparent; white-space: nowrap; }}
    .badge.running {{ background: rgba(126, 240, 193, 0.14); color: var(--mint); border-color: rgba(126, 240, 193, 0.26); }}
    .badge.idle {{ background: rgba(255, 209, 102, 0.12); color: var(--amber); border-color: rgba(255, 209, 102, 0.24); }}
    .badge.done {{ background: rgba(121, 227, 255, 0.12); color: var(--cyan); border-color: rgba(121, 227, 255, 0.24); }}
    .badge.warning, .badge.unknown {{ background: rgba(255, 138, 161, 0.12); color: var(--rose); border-color: rgba(255, 138, 161, 0.24); }}
    .meta-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin: 16px 0 0; }}
    .meta-grid div, .metric {{ background: rgba(255,255,255,0.03); border: 1px solid var(--line); border-radius: 16px; padding: 12px 14px; }}
    .meta-grid span, .metric span {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.08em; }}
    .meta-grid strong, .metric strong {{ font-size: 15px; line-height: 1.4; }}
    .summary {{ color: #e7efff; line-height: 1.7; margin: 16px 0; }}
    .metric-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .log-box {{ margin-top: 14px; background: #06101e; border: 1px solid rgba(121, 227, 255, 0.12); border-radius: 18px; padding: 14px; }}
    .log-title {{ color: var(--cyan); font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 10px; }}
    .log-box ul {{ margin: 0; padding-left: 18px; color: #dbe7ff; line-height: 1.6; font-size: 14px; }}
    .sources {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
    .sources code {{ background: rgba(186, 167, 255, 0.12); color: #e7deff; border: 1px solid rgba(186, 167, 255, 0.22); border-radius: 999px; padding: 6px 10px; font-size: 12px; }}
    .lower-grid {{ display: grid; grid-template-columns: 0.9fr 1.1fr; gap: 16px; }}
    .guide-card, .table-card {{ padding: 20px; }}
    .guide-card ol {{ margin: 12px 0 0; padding-left: 18px; color: #dce7fb; line-height: 1.75; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 12px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; font-size: 14px; }}
    th {{ color: #cfddf7; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }}
    td {{ color: #e9f1ff; }}
    .footer {{ margin-top: 16px; color: var(--muted); font-size: 12px; }}
    @media (max-width: 1024px) {{ .hero-grid, .cards, .lower-grid {{ grid-template-columns: 1fr; }} }}
    @media (max-width: 720px) {{ .stats, .metric-grid, .meta-grid {{ grid-template-columns: 1fr; }} .wrap {{ width: min(100vw - 18px, 1320px); }} h1 {{ max-width: none; }} }}
  </style>
</head>
<body>
  <main class='wrap'>
    <section class='hero'>
      <div class='hero-grid'>
        <div>
          <p class='eyebrow'>Live workspace telemetry</p>
          <h1>Worker status dashboard</h1>
          <p class='lead'>A practical readout for seeing whether background worker-style tasks are actually doing work in this workspace. It pulls from the existing progress files and logs, then presents the most recent evidence in one page.</p>
          <div class='timestamp'>Generated: {html.escape(payload['generatedAt'])} KST-ish local time, auto refresh every 120s.</div>
        </div>
        <div class='stats'>
          <div class='stat'><span>Workers tracked</span><strong>{overview['workers']}</strong><em>{overview['running']} running, {overview['completed']} completed</em></div>
          <div class='stat'><span>Verified stores</span><strong>{overview['verifiedStores']}</strong><em>{overview['smsReady']} are SMS-ready</em></div>
          <div class='stat'><span>Needs check</span><strong>{overview['needsCheck']}</strong><em>held back for manual or stricter validation</em></div>
        </div>
      </div>
    </section>

    <section class='section'>
      <div class='section-title'>
        <h2>Worker cards</h2>
        <p>Each card shows task name, state, stage, last update, and the freshest proof we have.</p>
      </div>
      <div class='cards'>
        {''.join(worker_cards)}
      </div>
    </section>

    <section class='section lower-grid'>
      <article class='card guide-card'>
        <div class='section-title'>
          <h2>How to read this</h2>
          <p>Quick operator guidance</p>
        </div>
        <ol>{guidance}</ol>
        <p class='footer'>Tip: open this file directly or publish it as a static page. The companion JSON artifact can feed another frontend later without changing the source logs.</p>
      </article>
      <article class='card table-card'>
        <div class='section-title'>
          <h2>Compact matrix</h2>
          <p>Good for fast scanning and screenshots</p>
        </div>
        <table>
          <thead><tr><th>Worker</th><th>Status</th><th>Stage</th><th>Last update</th><th>Summary</th></tr></thead>
          <tbody>{''.join(table_rows)}</tbody>
        </table>
      </article>
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    payload = build_payload()
    json_text = json.dumps(payload, ensure_ascii=False, indent=2)
    html_text = render_html(payload)

    output_json = GENERATED / "worker_status_dashboard.json"
    output_html_generated = GENERATED / "worker_status_dashboard.html"
    output_html_root = ROOT / "worker_status_dashboard.html"

    output_json.write_text(json_text + "\n", encoding="utf-8")
    output_html_generated.write_text(html_text, encoding="utf-8")
    output_html_root.write_text(html_text, encoding="utf-8")


if __name__ == "__main__":
    main()
