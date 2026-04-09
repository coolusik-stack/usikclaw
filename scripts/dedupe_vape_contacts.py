#!/usr/bin/env python3
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path('/Users/usuk/.openclaw/workspace')
CSV_PATH = ROOT / 'generated' / 'vape_stores_seoul_template.csv'
FIELDNAMES = [
    'priority_tier','area','store_name','address','phone','map_link','instagram_or_site',
    'review_count','rating','store_type','store_tone','location_score','specialty_score',
    'contactability_score','total_score','priority_grade','message_type','contact_status',
    'last_contact_date','notes'
]
PRIORITY_AREAS = {
    '강남역','신논현/논현','역삼/선릉','삼성/코엑스','홍대/합정/상수','신촌/이대','성수',
    '잠실/송리단길','영등포/문래','여의도','마포/공덕','이태원','건대입구','왕십리/한양대'
}


def score(row):
    addr = row.get('address') or ''
    name = row.get('store_name') or ''
    notes = row.get('notes') or ''
    area = row.get('area') or ''
    s = 0.0
    s += len(addr)
    s += len(name) * 0.3
    s += 5 if area in PRIORITY_AREAS else 0
    s += 6 if '공식 스토어 로케이터' in notes else 0
    s += 2 if row.get('map_link') else 0
    s += 2 if '기존 02 대신' in notes else 0
    if '주변' in addr or addr.endswith('동') or addr.endswith('역') or addr == '':
        s -= 12
    if '전자담배' in name:
        s += 2
    if '베이프' in name:
        s += 1
    return s


def main():
    rows = list(csv.DictReader(CSV_PATH.open(encoding='utf-8')))
    filled = [r for r in rows if (r.get('store_name') or '').strip()]
    by_phone = defaultdict(list)
    for row in filled:
        phone = (row.get('phone') or '').strip()
        if phone:
            by_phone[phone].append(row)

    keep = []
    dropped = []
    for row in rows:
        phone = (row.get('phone') or '').strip()
        if not phone or len(by_phone[phone]) == 1:
            keep.append(row)

    for phone, items in by_phone.items():
        if len(items) == 1:
            continue
        ranked = sorted(items, key=score, reverse=True)
        winner = ranked[0].copy()
        aliases = [f"{item['store_name']} | {item['address']}" for item in ranked[1:]]
        note = (winner.get('notes') or '').strip()
        merge_note = '동일 연락처 중복 병합: ' + ' / '.join(aliases)
        winner['notes'] = (note + ('; ' if note else '') + merge_note)[:1000]
        keep.append(winner)
        dropped.extend(ranked[1:])

    with CSV_PATH.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(keep)

    print(f'dropped={len(dropped)}')
    for row in dropped:
        print(f"{row['phone']}\t{row['store_name']}\t{row['address']}")


if __name__ == '__main__':
    main()
