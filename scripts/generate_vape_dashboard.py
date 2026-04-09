#!/usr/bin/env python3
import csv
import html
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path('/Users/usuk/.openclaw/workspace')
CSV_PATH = ROOT / 'generated' / 'vape_stores_seoul_template.csv'
QUEUE_PATH = ROOT / 'generated' / 'vape_500_queue.json'
PROGRESS_PATH = ROOT / 'generated' / 'vape_500_progress.json'
OUT_PATH = ROOT / 'generated' / 'bool_outreach_dashboard_v3.html'


def esc(value: str) -> str:
    return html.escape(value or '')


rows = list(csv.DictReader(CSV_PATH.open(encoding='utf-8')))
rows = [r for r in rows if (r.get('store_name') or '').strip()]
queue = json.loads(QUEUE_PATH.read_text()) if QUEUE_PATH.exists() else []
progress = json.loads(PROGRESS_PATH.read_text()) if PROGRESS_PATH.exists() else {}
counts = progress.get('counts', {})
updated = progress.get('lastVerifiedAtKst') or datetime.now().strftime('%Y-%m-%d %H:%M')

phone_ready = counts.get('phoneReady') or sum(1 for r in rows if (r.get('phone') or '').startswith(('010', '0507')))
needs_check = counts.get('needsCheck') or sum(1 for r in rows if not (r.get('phone') or '').strip() or (r.get('phone') or '').startswith(('02', '070', '080', '1800')))
total = counts.get('total') or len(rows)
a_grade = sum(1 for r in rows if (r.get('priority_grade') or '').upper() == 'A')
area_counts = Counter((r.get('area') or '기타').strip() for r in rows)
priority_counts = Counter((r.get('priority_grade') or 'N/A').strip() for r in rows)
status_counts = Counter((r.get('status') or '').strip() for r in queue)
unresolved = [q for q in queue if q.get('status') in {'no_place_id', 'non_seoul', 'error', 'low_contact', 'duplicate'}]

area_cards = ''.join(
    f"<div class='pill'><span>{esc(area)}</span><strong>{count}</strong></div>"
    for area, count in area_counts.most_common()
)

unresolved_rows = ''.join(
    "<tr>"
    f"<td>{esc(item.get('query', ''))}</td>"
    f"<td>{esc(item.get('area', ''))}</td>"
    f"<td>{esc(item.get('status', ''))}</td>"
    f"<td>{esc(item.get('hint_phone', ''))}</td>"
    f"<td>{esc(item.get('hint_address', ''))}</td>"
    "</tr>"
    for item in unresolved[:40]
)

store_rows = []
for idx, row in enumerate(sorted(rows, key=lambda r: (r.get('area', ''), r.get('store_name', ''))), start=1):
    map_link = row.get('map_link') or ''
    store_name = esc(row.get('store_name', ''))
    if map_link.startswith('http'):
        store_name = f"<a href='{esc(map_link)}' target='_blank' rel='noopener'>{store_name}</a>"
    store_rows.append(
        "<tr>"
        f"<td>{idx}</td>"
        f"<td>{esc(row.get('area', ''))}</td>"
        f"<td class='store'>{store_name}</td>"
        f"<td>{esc(row.get('phone', ''))}</td>"
        f"<td>{esc(row.get('address', ''))}</td>"
        f"<td>{esc(row.get('priority_grade', ''))}</td>"
        f"<td>{esc(row.get('message_type', ''))}</td>"
        f"<td>{esc(row.get('notes', ''))}</td>"
        "</tr>"
    )
store_rows_html = ''.join(store_rows)

html_doc = f"""<!doctype html>
<html lang='ko'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>BOOL Korea · Seoul Vape Outreach Dashboard v3</title>
  <style>
    :root {{
      --bg: #0b1020;
      --panel: rgba(16, 24, 48, 0.82);
      --panel-2: rgba(17, 25, 40, 0.95);
      --line: rgba(148, 163, 184, 0.18);
      --text: #e5eefc;
      --muted: #9fb0cd;
      --accent: #7dd3fc;
      --accent-2: #a78bfa;
      --good: #6ee7b7;
      --warn: #fbbf24;
      --bad: #fca5a5;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: radial-gradient(circle at top, #13203d 0%, var(--bg) 45%, #050814 100%); color: var(--text); }}
    .wrap {{ width: min(1320px, calc(100vw - 32px)); margin: 0 auto; padding: 32px 0 64px; }}
    .hero, .card {{ background: var(--panel); backdrop-filter: blur(14px); border: 1px solid var(--line); border-radius: 24px; box-shadow: 0 24px 70px rgba(0, 0, 0, 0.28); }}
    .hero {{ padding: 32px; margin-bottom: 20px; }}
    .kicker {{ color: var(--accent); font-size: 13px; letter-spacing: 0.12em; text-transform: uppercase; }}
    h1 {{ margin: 10px 0 8px; font-size: clamp(32px, 5vw, 52px); line-height: 1.02; }}
    .sub {{ color: var(--muted); max-width: 900px; line-height: 1.6; }}
    .note {{ margin-top: 14px; color: #dbeafe; font-size: 14px; }}
    .stats {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin: 22px 0 16px; }}
    .stat {{ background: var(--panel-2); border: 1px solid var(--line); border-radius: 18px; padding: 18px; }}
    .num {{ font-size: clamp(30px, 4vw, 40px); font-weight: 800; }}
    .lab {{ margin-top: 6px; color: var(--muted); font-size: 14px; }}
    .grid {{ display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; margin-bottom: 20px; }}
    .card {{ padding: 22px; }}
    h2 {{ margin: 0 0 14px; font-size: 20px; }}
    .pill-wrap {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .pill {{ display: inline-flex; align-items: center; gap: 10px; padding: 10px 14px; border: 1px solid var(--line); border-radius: 999px; background: rgba(15, 23, 42, 0.8); color: #dbeafe; }}
    .pill strong {{ color: white; }}
    .meta-list {{ margin: 0; padding-left: 18px; color: var(--muted); line-height: 1.7; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 11px 10px; border-bottom: 1px solid var(--line); font-size: 13px; vertical-align: top; text-align: left; }}
    th {{ color: #cbd5e1; position: sticky; top: 0; background: rgba(9, 14, 28, 0.98); backdrop-filter: blur(8px); }}
    td {{ color: #e2e8f0; }}
    td.store a {{ color: #93c5fd; text-decoration: none; }}
    td.store a:hover {{ text-decoration: underline; }}
    .table-card {{ padding: 0; overflow: hidden; }}
    .table-head {{ padding: 22px 22px 0; }}
    .table-wrap {{ max-height: 70vh; overflow: auto; padding: 0 22px 22px; }}
    .mini-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .mini {{ background: rgba(15, 23, 42, 0.8); border: 1px solid var(--line); border-radius: 16px; padding: 14px; }}
    .mini .t {{ color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    .mini .v {{ font-size: 22px; font-weight: 700; }}
    .section-gap {{ margin-top: 20px; }}
    .foot {{ color: var(--muted); margin-top: 16px; font-size: 12px; }}
    @media (max-width: 980px) {{ .stats, .grid, .mini-grid {{ grid-template-columns: 1fr; }} .wrap {{ width: min(100vw - 20px, 1320px); }} }}
  </style>
</head>
<body>
  <div class='wrap'>
    <section class='hero'>
      <div class='kicker'>BOOL Korea · Cold Outreach</div>
      <h1>서울 전자담배점 아웃리치 대시보드</h1>
      <p class='sub'>서울 전자담배점 500 프로젝트의 최신 검증 상태입니다. 공개 웹 정보와 네이버 지도 검증 기준으로 누적했으며, 실제 발송 우선순위는 010 / 0507 번호 중심으로 운영합니다.</p>
      <div class='note'>업데이트: {esc(updated)} KST · 현재 큐는 소진 완료 상태</div>
      <div class='stats'>
        <div class='stat'><div class='num'>{total}</div><div class='lab'>총 매장 수</div></div>
        <div class='stat'><div class='num'>{phone_ready}</div><div class='lab'>문자 가능한 번호</div></div>
        <div class='stat'><div class='num'>{needs_check}</div><div class='lab'>재확인 필요 번호</div></div>
        <div class='stat'><div class='num'>{a_grade}</div><div class='lab'>A등급 후보</div></div>
      </div>
      <div class='pill-wrap'>{area_cards}</div>
    </section>

    <section class='grid'>
      <div class='card'>
        <h2>현재 상태 요약</h2>
        <div class='mini-grid'>
          <div class='mini'><div class='t'>Queue known</div><div class='v'>{status_counts.get('known', 0)}</div></div>
          <div class='mini'><div class='t'>No place ID</div><div class='v'>{status_counts.get('no_place_id', 0)}</div></div>
          <div class='mini'><div class='t'>Non-Seoul / 제외</div><div class='v'>{status_counts.get('non_seoul', 0)}</div></div>
        </div>
        <ul class='meta-list section-gap'>
          <li>현재 남은 <strong>queued</strong> 후보는 {status_counts.get('queued', 0)}건입니다.</li>
          <li>이번 마감 기준 CSV는 {total}개 매장, 그중 {phone_ready}개가 010/0507 번호입니다.</li>
          <li>동일 연락처 중복은 병합 정리했고, 다음 확장 포인트는 신규 소스 확보, no_place_id 재탐색, 저신뢰 번호 재검증입니다.</li>
        </ul>
      </div>
      <div class='card'>
        <h2>우선 후속 액션</h2>
        <ul class='meta-list'>
          <li>신규 소스 페이지 추가 크롤링 또는 브랜드 취급점 확장</li>
          <li>no_place_id 후보 재검색, 상호 변형명으로 재시도</li>
          <li>02 / 070 / 080 번호의 대체 010 / 0507 탐색</li>
          <li>실제 발송은 A등급, 핫상권, 최근 검증 매장부터 시작</li>
        </ul>
        <p class='foot'>등급 분포: {', '.join(f'{k}:{v}' for k, v in sorted(priority_counts.items()))}</p>
      </div>
    </section>

    <section class='card table-card'>
      <div class='table-head'><h2>검증 보류 / 제외 후보</h2><div class='foot'>최대 40개 표시</div></div>
      <div class='table-wrap'>
        <table>
          <thead><tr><th>후보명</th><th>권역</th><th>상태</th><th>힌트 번호</th><th>힌트 주소</th></tr></thead>
          <tbody>{unresolved_rows}</tbody>
        </table>
      </div>
    </section>

    <section class='card table-card section-gap'>
      <div class='table-head'><h2>마스터 리스트</h2><div class='foot'>총 {total}개 매장</div></div>
      <div class='table-wrap'>
        <table>
          <thead><tr><th>#</th><th>권역</th><th>매장명</th><th>전화</th><th>주소</th><th>등급</th><th>문안</th><th>메모</th></tr></thead>
          <tbody>{store_rows_html}</tbody>
        </table>
      </div>
    </section>
  </div>
</body>
</html>
"""

OUT_PATH.write_text(html_doc, encoding='utf-8')
print(str(OUT_PATH))
