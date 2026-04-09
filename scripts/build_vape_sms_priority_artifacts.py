#!/usr/bin/env python3
import csv
import html
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path('/Users/usuk/.openclaw/workspace')
INPUT_CSV = ROOT / 'generated' / 'vape_stores_seoul_template.csv'
OUT_DIR = ROOT / 'generated'

BASE_FIELDS = [
    'priority_tier','area','store_name','address','phone','map_link','instagram_or_site',
    'review_count','rating','store_type','store_tone','location_score','specialty_score',
    'contactability_score','total_score','priority_grade','message_type','contact_status',
    'last_contact_date','notes'
]
DERIVED_FIELDS = [
    'sms_ready','source_bucket','cleanup_flags','cluster','send_score',
    'send_priority_bucket','recommended_wave','send_order','batch_hint','priority_reason'
]
FIELDNAMES = BASE_FIELDS + DERIVED_FIELDS

CLUSTER_MAP = {
    'core_commercial': {'강남역', '신논현/논현', '역삼/선릉', '삼성/코엑스', '압구정/청담', '여의도'},
    'trend_youth': {'홍대/합정/상수', '신촌/이대', '성수', '건대입구', '왕십리/한양대', '이태원'},
    'mixed_throughput': {'잠실/송리단길', '영등포/문래', '마포/공덕', '종로/을지로/충무로', '구로디지털단지'},
}
CLUSTER_LABEL = {
    'core_commercial': '코어 오피스/상업권',
    'trend_youth': '트렌드/대학가',
    'mixed_throughput': '혼합 고회전 상권',
    'expansion': '확장/생활상권',
}


def source_bucket(row):
    note = (row.get('notes') or '').strip()
    if '공식 스토어 로케이터' in note or 'Martha Vape 공개 로케이터 기준 확인' in note:
        return 'official_locator'
    if (row.get('map_link') or '').strip():
        return 'linked_source'
    return 'web_search_draft'


def cleanup_flags(row):
    note = (row.get('notes') or '').strip()
    flags = []
    if '주소 재확인 필요' in note:
        flags.append('address_check')
    if '전화 확인 필요' in note:
        flags.append('phone_check')
    if '재확인 권장' in note or '재확인 필요' in note:
        flags.append('manual_review')
    if '동일 연락처 중복 병합' in note:
        flags.append('merged_dup_history')
    if '별도 매장 가능성' in note or '부대표 번호' in note or '스마트콜 번호' in note:
        flags.append('identity_risk')
    if source_bucket(row) == 'web_search_draft' and note == '공개 웹 검색 기반 초안':
        flags.append('draft_only')
    return '|'.join(flags)


def cluster_for(area):
    for key, areas in CLUSTER_MAP.items():
        if area in areas:
            return key
    return 'expansion'


def batch_hint(cluster, wave):
    base = {
        ('Wave 1', 'core_commercial'): 'Batch 1',
        ('Wave 1', 'trend_youth'): 'Batch 2',
        ('Wave 1', 'mixed_throughput'): 'Batch 3',
        ('Wave 1', 'expansion'): 'Batch 4',
        ('Wave 2', 'core_commercial'): 'Batch 5',
        ('Wave 2', 'trend_youth'): 'Batch 6',
        ('Wave 2', 'mixed_throughput'): 'Batch 7',
        ('Wave 2', 'expansion'): 'Batch 8',
        ('Wave 3', 'core_commercial'): 'Batch 9',
        ('Wave 3', 'trend_youth'): 'Batch 10',
        ('Wave 3', 'mixed_throughput'): 'Batch 11',
        ('Wave 3', 'expansion'): 'Batch 12',
        ('HOLD', 'core_commercial'): 'Cleanup A',
        ('HOLD', 'trend_youth'): 'Cleanup B',
        ('HOLD', 'mixed_throughput'): 'Cleanup C',
        ('HOLD', 'expansion'): 'Cleanup D',
    }
    return base[(wave, cluster)]


def send_score(row):
    score = float((row.get('total_score') or '0').strip() or 0)
    score += {'1': 1.5, '2': 0.7, '3': 0.0}.get((row.get('priority_tier') or '').strip(), 0)
    score += {'1': 0.6, '2': 0.2, '3': -0.3}.get((row.get('message_type') or '').strip(), 0)
    score += {'official_locator': 1.2, 'linked_source': 0.7, 'web_search_draft': 0.0}[source_bucket(row)]
    penalties = {
        'address_check': 1.0,
        'phone_check': 1.5,
        'manual_review': 1.0,
        'merged_dup_history': 0.5,
        'identity_risk': 1.5,
        'draft_only': 0.4,
    }
    flags = [f for f in cleanup_flags(row).split('|') if f]
    score -= sum(penalties.get(flag, 0) for flag in flags)
    return round(score, 2)


def hard_hold(flags):
    hard = {'address_check', 'phone_check', 'manual_review', 'identity_risk'}
    return any(flag in hard for flag in flags.split('|') if flag)


def priority_bucket(row, computed_score, flags):
    if hard_hold(flags):
        return 'HOLD'
    if computed_score >= 15.2:
        return 'P1'
    if computed_score >= 13.8:
        return 'P2'
    return 'P3'


def recommended_wave(bucket):
    return {'P1': 'Wave 1', 'P2': 'Wave 2', 'P3': 'Wave 3', 'HOLD': 'HOLD'}[bucket]


def priority_reason(row, computed_score, flags):
    parts = [f"score {computed_score}"]
    if (row.get('priority_tier') or '').strip() == '1':
        parts.append('tier1 area')
    if (row.get('message_type') or '').strip() == '1':
        parts.append('message_type1')
    sb = source_bucket(row)
    if sb == 'official_locator':
        parts.append('official source')
    elif sb == 'linked_source':
        parts.append('linked source')
    if flags:
        parts.append(f'flags:{flags}')
    return ', '.join(parts)


def load_rows():
    with INPUT_CSV.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)


def enrich(rows):
    out = []
    for row in rows:
        row = dict(row)
        sms_ready = 'yes' if (row.get('phone') or '').startswith(('010', '0507')) and (row.get('contact_status') or '미접촉').strip() == '미접촉' else 'no'
        row['sms_ready'] = sms_ready
        row['source_bucket'] = source_bucket(row)
        row['cleanup_flags'] = cleanup_flags(row)
        row['cluster'] = CLUSTER_LABEL[cluster_for((row.get('area') or '').strip())]
        row['send_score'] = f"{send_score(row):.2f}"
        row['send_priority_bucket'] = priority_bucket(row, float(row['send_score']), row['cleanup_flags']) if sms_ready == 'yes' else 'NON_SMS'
        row['recommended_wave'] = recommended_wave(row['send_priority_bucket']) if sms_ready == 'yes' else 'NON_SMS'
        row['batch_hint'] = batch_hint(cluster_for((row.get('area') or '').strip()), row['recommended_wave']) if sms_ready == 'yes' else ''
        row['priority_reason'] = priority_reason(row, float(row['send_score']), row['cleanup_flags']) if sms_ready == 'yes' else ''
        row['send_order'] = ''
        out.append(row)

    cluster_rank = {'코어 오피스/상업권': 0, '트렌드/대학가': 1, '혼합 고회전 상권': 2, '확장/생활상권': 3}
    wave_rank = {'Wave 1': 0, 'Wave 2': 1, 'Wave 3': 2, 'HOLD': 3, 'NON_SMS': 4}
    ranked = [r for r in out if r['sms_ready'] == 'yes']
    ranked.sort(key=lambda r: (
        wave_rank[r['recommended_wave']],
        cluster_rank[r['cluster']],
        -float(r['send_score']),
        -(int((r.get('total_score') or '0').strip() or 0)),
        r.get('area') or '',
        r.get('store_name') or '',
    ))
    for idx, row in enumerate(ranked, start=1):
        row['send_order'] = str(idx)
    return out, ranked


def summarize_by_area(rows):
    group = defaultdict(list)
    for row in rows:
        group[row['area']].append(row)
    summary = []
    for area, items in group.items():
        summary.append({
            'area': area,
            'count': len(items),
            'avg_send_score': round(mean(float(i['send_score']) for i in items), 2),
            'wave1': sum(1 for i in items if i['recommended_wave'] == 'Wave 1'),
            'wave2': sum(1 for i in items if i['recommended_wave'] == 'Wave 2'),
            'wave3': sum(1 for i in items if i['recommended_wave'] == 'Wave 3'),
            'hold': sum(1 for i in items if i['recommended_wave'] == 'HOLD'),
        })
    summary.sort(key=lambda x: (-x['wave1'], -x['avg_send_score'], -x['count'], x['area']))
    return summary


def make_md(all_rows, ranked_rows):
    sms = [r for r in all_rows if r['sms_ready'] == 'yes']
    waves = {name: [r for r in sms if r['recommended_wave'] == name] for name in ['Wave 1', 'Wave 2', 'Wave 3', 'HOLD']}
    area_summary = summarize_by_area(sms)
    source_counts = Counter(r['source_bucket'] for r in sms)
    cluster_counts = Counter(r['cluster'] for r in sms)
    cleanup_counts = Counter(flag for r in sms for flag in (r['cleanup_flags'].split('|') if r['cleanup_flags'] else []))

    lines = []
    lines.append('# Seoul vape SMS outreach prioritization')
    lines.append('')
    lines.append('## Snapshot')
    lines.append(f"- SMS-ready contacts: **{len(sms)}**")
    lines.append(f"- Wave 1 send-now: **{len(waves['Wave 1'])}**")
    lines.append(f"- Wave 2 next: **{len(waves['Wave 2'])}**")
    lines.append(f"- Wave 3 long-tail: **{len(waves['Wave 3'])}**")
    lines.append(f"- Hold for cleanup: **{len(waves['HOLD'])}**")
    lines.append(f"- Source mix: official locator {source_counts['official_locator']}, linked source {source_counts['linked_source']}, web-search draft {source_counts['web_search_draft']}")
    lines.append('')
    lines.append('## Main recommendation')
    lines.append('- Start with **Wave 1 (116 contacts)**, led by 역삼/선릉, 성수, 홍대/합정/상수, 잠실/송리단길, 영등포/문래, 건대입구.')
    lines.append('- Keep the first operational pass to **4 batches of 25-30** by cluster, not one giant blast. This keeps reply handling and template tuning manageable.')
    lines.append('- Push **Wave 2 (132 contacts)** only after Wave 1 reply/no-reply patterns are clear.')
    lines.append('- Do not send the **20 HOLD rows** before cleanup, they contain phone/address/manual-review risk.')
    lines.append('')
    lines.append('## Recommended send order')
    lines.append('1. **Batch 1, 코어 오피스/상업권, 25-30 rows**: 강남역, 신논현/논현, 역삼/선릉, 삼성/코엑스, 압구정/청담, 여의도 중 Wave 1 상위 순번.')
    lines.append('2. **Batch 2, 트렌드/대학가, 25-30 rows**: 성수, 홍대/합정/상수, 신촌/이대, 건대입구, 이태원, 왕십리/한양대 중 Wave 1.')
    lines.append('3. **Batch 3, 혼합 고회전 상권, 25-30 rows**: 잠실/송리단길, 영등포/문래, 마포/공덕, 종로/을지로/충무로, 구로디지털단지 중 Wave 1.')
    lines.append('4. **Batch 4, Wave 1 remainder, 20-31 rows**: Wave 1 잔여분 + 점수 15점대 상위 연락처 정리 발송.')
    lines.append('5. **Batch 5-8**: Wave 2를 같은 클러스터 순서로 반복.')
    lines.append('6. **Batch 9-12**: Wave 3는 회수율이 낮을 가능성이 있어 소규모 테스트 후 확대.')
    lines.append('')
    lines.append('## Top priority segments')
    lines.append('| Segment area | SMS-ready | Wave 1 | Avg send score |')
    lines.append('| --- | ---: | ---: | ---: |')
    for item in area_summary[:12]:
        lines.append(f"| {item['area']} | {item['count']} | {item['wave1']} | {item['avg_send_score']:.2f} |")
    lines.append('')
    lines.append('## Batching logic')
    lines.append(f"- Cluster mix: 코어 오피스/상업권 {cluster_counts['코어 오피스/상업권']}, 트렌드/대학가 {cluster_counts['트렌드/대학가']}, 혼합 고회전 상권 {cluster_counts['혼합 고회전 상권']}, 확장/생활상권 {cluster_counts['확장/생활상권']}")
    lines.append('- Keep each batch internally similar by area cluster first, then send_score order second.')
    lines.append('- Within each batch, prioritize `message_type=1` and higher `total_score` rows first.')
    lines.append('- If replies spike in one cluster, pause the next batch in that same cluster and adapt the message, instead of contaminating the whole list.')
    lines.append('')
    lines.append('## Cleanup flags to clear before send')
    lines.append('| Flag | Count | Meaning |')
    lines.append('| --- | ---: | --- |')
    meaning = {
        'address_check': '주소 다시 확인 후 발송',
        'phone_check': '번호 노이즈 가능성 있음',
        'manual_review': '상호/지점 식별 재검토',
        'merged_dup_history': '과거 중복 병합 이력, 최종 상호 확인 권장',
        'identity_risk': '대표번호/스마트콜/타지점 혼선 가능성',
        'draft_only': '링크 근거 없이 웹검색 초안만 존재',
    }
    for flag, count in cleanup_counts.most_common():
        lines.append(f"| {flag} | {count} | {meaning.get(flag, '')} |")
    lines.append('')
    lines.append('## Output files')
    lines.append('- `generated/vape_sms_priority_ranked.csv`')
    lines.append('- `generated/vape_sms_priority_wave1.csv`')
    lines.append('- `generated/vape_sms_priority_wave2.csv`')
    lines.append('- `generated/vape_sms_priority_wave3.csv`')
    lines.append('- `generated/vape_sms_priority_hold_cleanup.csv`')
    lines.append('- `generated/vape_sms_priority_report.html`')
    lines.append('')
    lines.append('## First 15 recommended sends')
    lines.append('| Order | Area | Store | Phone | Score | Why |')
    lines.append('| ---: | --- | --- | --- | ---: | --- |')
    for row in ranked_rows[:15]:
        lines.append(f"| {row['send_order']} | {row['area']} | {row['store_name']} | {row['phone']} | {row['send_score']} | {row['priority_reason']} |")
    return '\n'.join(lines) + '\n'


def make_html(md_text, all_rows):
    sms = [r for r in all_rows if r['sms_ready'] == 'yes']
    waves = {name: [r for r in sms if r['recommended_wave'] == name] for name in ['Wave 1', 'Wave 2', 'Wave 3', 'HOLD']}
    top_rows = sorted(sms, key=lambda r: int(r['send_order'] or '999999'))[:40]
    cards = [
        ('SMS-ready', str(len(sms))),
        ('Wave 1', str(len(waves['Wave 1']))),
        ('Wave 2', str(len(waves['Wave 2']))),
        ('Wave 3', str(len(waves['Wave 3']))),
        ('Hold', str(len(waves['HOLD']))),
    ]
    card_html = ''.join(f"<div class='card'><div class='label'>{html.escape(k)}</div><div class='value'>{html.escape(v)}</div></div>" for k, v in cards)
    rows_html = ''.join(
        '<tr>'
        f"<td>{html.escape(r['send_order'])}</td>"
        f"<td>{html.escape(r['recommended_wave'])}</td>"
        f"<td>{html.escape(r['cluster'])}</td>"
        f"<td>{html.escape(r['area'])}</td>"
        f"<td>{html.escape(r['store_name'])}</td>"
        f"<td>{html.escape(r['phone'])}</td>"
        f"<td>{html.escape(r['send_score'])}</td>"
        f"<td>{html.escape(r['cleanup_flags'])}</td>"
        '</tr>' for r in top_rows
    )
    pre = html.escape(md_text)
    return f"""<!doctype html>
<html lang='ko'>
<head>
  <meta charset='utf-8'>
  <title>Vape SMS Priority Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif; margin: 32px; color: #111827; background: #f8fafc; }}
    h1, h2 {{ margin: 0 0 12px; }}
    .grid {{ display: grid; grid-template-columns: repeat(5, minmax(120px, 1fr)); gap: 12px; margin: 20px 0 28px; }}
    .card {{ background: white; border-radius: 14px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.06); }}
    .label {{ font-size: 12px; color: #6b7280; margin-bottom: 6px; }}
    .value {{ font-size: 28px; font-weight: 700; }}
    .panel {{ background: white; border-radius: 16px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,.06); margin-top: 20px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ text-align: left; padding: 10px 8px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
    th {{ color: #374151; font-weight: 700; }}
    pre {{ white-space: pre-wrap; font-size: 13px; line-height: 1.5; margin: 0; }}
  </style>
</head>
<body>
  <h1>Seoul vape SMS priority report</h1>
  <div class='grid'>{card_html}</div>
  <div class='panel'>
    <h2>Top 40 ranked contacts</h2>
    <table>
      <thead><tr><th>Order</th><th>Wave</th><th>Cluster</th><th>Area</th><th>Store</th><th>Phone</th><th>Score</th><th>Flags</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>
  <div class='panel'>
    <h2>Report text</h2>
    <pre>{pre}</pre>
  </div>
</body>
</html>
"""


def main():
    rows = load_rows()
    all_rows, ranked_rows = enrich(rows)
    sms_ranked = [r for r in ranked_rows if r['sms_ready'] == 'yes']
    wave1 = [r for r in sms_ranked if r['recommended_wave'] == 'Wave 1']
    wave2 = [r for r in sms_ranked if r['recommended_wave'] == 'Wave 2']
    wave3 = [r for r in sms_ranked if r['recommended_wave'] == 'Wave 3']
    hold = [r for r in sms_ranked if r['recommended_wave'] == 'HOLD']

    write_csv(OUT_DIR / 'vape_sms_priority_ranked.csv', sms_ranked)
    write_csv(OUT_DIR / 'vape_sms_priority_wave1.csv', wave1)
    write_csv(OUT_DIR / 'vape_sms_priority_wave2.csv', wave2)
    write_csv(OUT_DIR / 'vape_sms_priority_wave3.csv', wave3)
    write_csv(OUT_DIR / 'vape_sms_priority_hold_cleanup.csv', hold)

    md_text = make_md(all_rows, sms_ranked)
    (OUT_DIR / 'vape_sms_priority_report.md').write_text(md_text, encoding='utf-8')
    (OUT_DIR / 'vape_sms_priority_report.html').write_text(make_html(md_text, all_rows), encoding='utf-8')


if __name__ == '__main__':
    main()
