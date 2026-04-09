#!/usr/bin/env python3
import csv
import html
import json
import re
import urllib.parse
import urllib.request
import time
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path('/Users/usuk/.openclaw/workspace')
CSV_PATH = ROOT / 'generated' / 'vape_stores_seoul_template.csv'
PROGRESS_JSON = ROOT / 'generated' / 'vape_500_progress.json'
PROGRESS_MD = ROOT / 'generated' / 'vape_500_progress.md'
SUMMARY_PATH = ROOT / 'generated' / 'vape_hotspot_wave2_summary.json'
LOG_PATH = ROOT / 'generated' / 'logs' / 'vape_hotspot_wave2.log'
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
KST = timezone(timedelta(hours=9))
TODAY = datetime.now(KST).strftime('%Y-%m-%d')

FIELDNAMES = [
    'priority_tier','area','store_name','address','phone','map_link','instagram_or_site',
    'review_count','rating','store_type','store_tone','location_score','specialty_score',
    'contactability_score','total_score','priority_grade','message_type','contact_status',
    'last_contact_date','notes'
]

PRIORITY_AREAS = {
    '강남역', '신논현/논현', '역삼/선릉', '삼성/코엑스', '홍대/합정/상수', '신촌/이대',
    '성수', '잠실/송리단길', '영등포/문래', '여의도', '마포/공덕', '이태원', '건대입구', '왕십리/한양대'
}

AREA_RULES = [
    ('강남역', ['강남역', '강남대로66길', '강남대로84길', '강남대로 390', '강남대로 438', '강남대로65길', '서초동', '서초구 강남대로']),
    ('신논현/논현', ['신논현', '논현', '학동로', '봉은사로2길', '강남대로118길', '논현로']),
    ('역삼/선릉', ['역삼동', '테헤란로', '선릉로', '대치동', '테헤란로4길', '테헤란로70길']),
    ('삼성/코엑스', ['삼성역', '코엑스', '삼성동', '봉은사로 420', '봉은사로82길', '영동대로', '삼성로103길', '테헤란로87길']),
    ('홍대/합정/상수', ['홍대', '합정', '상수', '서교동', '동교동', '양화로', '독막로', '와우산로', '연남', '성지1길', '잔다리로', '어울마당로']),
    ('신촌/이대', ['신촌', '이대', '이화여대길', '대현동', '창천동', '연세로', '서대문구 거북골로']),
    ('성수', ['성수역', '성수동', '성수이로', '연무장', '서울숲', '뚝섬', '왕십리로10길']),
    ('이태원', ['이태원', '한남동', '대사관로', '보광로', '이태원로', '용산구 한강대로']),
    ('잠실/송리단길', ['잠실', '송리단길', '석촌', '올림픽로', '풍납동', '백제고분로7길', '삼전로']),
    ('문정/가락', ['문정', '가락', '법원로', '송파대로28길', '송이로', '마천로', '장지', '충민로']),
    ('여의도', ['여의도', '의사당대로', '국제금융로6길', '여의대방로', '여의나루로']),
    ('영등포/문래', ['영등포', '문래', '당산', '영중로', '양평로', '선유로', '대방천로', '버드나루로', '경인로', '문래로']),
    ('마포/공덕', ['공덕', '마포대로', '대흥동', '상암동', '새창로', '월드컵로 190', '성암로 215']),
    ('건대입구', ['건대', '광진구', '자양동', '자양로', '군자동', '중곡동', '능동로', '광나루로56길', '아차산로', '동일로 150']),
    ('왕십리/한양대', ['왕십리', '행당동', '용답동', '한양대', '무학봉25길', '왕십리로21길', '왕십리광장로']),
    ('압구정/청담', ['압구정', '청담', '도산대로', '신사동']),
]

QUERY_PLAN = [
    '강남역 전자담배',
    '삼성역 전자담배',
    '홍대 전자담배',
    '합정 전자담배',
    '성수 전자담배',
    '서울숲 전자담배',
    '잠실 전자담배',
    '문정 전자담배',
    '영등포역 전자담배',
    '문래 전자담배',
    '여의도 전자담배',
    '건대입구 전자담배',
    '왕십리 전자담배',
    '이태원 전자담배',
    '공덕 전자담배',
]

STORE_KEYWORDS = ['전자담배', '베이프', 'vape', '하카', '킹콩', '시가', '전담', '퍼프', '쥬스', '베이퍼', '위베이프', '오지구', '베이프큐', '베이프월드']
NAME_EXCLUDE_PATTERNS = ['릴 ', '릴미니멀리움', '아이코스', 'iqos', 'kt&g', '편의점', 'cu ', 'gs25', '세븐일레븐']


def log(message: str):
    ts = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {message}'
    print(line, flush=True)
    with LOG_PATH.open('a', encoding='utf-8') as fh:
        fh.write(line + '\n')


def fetch_search(query: str) -> str:
    url = 'https://search.naver.com/search.naver?where=nexearch&ie=utf8&query=' + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://search.naver.com/',
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'ignore')


def normalize_name(value: str) -> str:
    value = (value or '').lower()
    value = value.replace('서울특별시', '서울')
    value = re.sub(r'\([^)]*\)', '', value)
    value = re.sub(r'(전자담배|베이프|vape|vap|멀티샵|멀티샾|점|본점|매장|전담|톡톡|쿠폰)', '', value)
    value = re.sub(r'[^0-9a-z가-힣]+', '', value)
    return value.strip()


def normalize_addr(value: str) -> str:
    value = (value or '').replace('서울특별시', '서울').replace('서울시', '서울')
    return re.sub(r'[^0-9a-z가-힣]+', '', value.lower())


def normalize_phone(value: str) -> str:
    value = (value or '').strip().replace('.', '-').replace(' ', '')
    m = re.search(r'(010-\d{4}-\d{4}|0507-\d{3,4}-\d{4}|02-\d{3,4}-\d{4}|070-\d{3,4}-\d{4}|080-\d{3,4}-\d{4}|18\d{2}-\d{4})', value)
    return m.group(1) if m else value


def clean_label(label: str) -> str:
    label = html.unescape(re.sub(r'<[^>]+>', '', label or ''))
    label = re.sub(r'\s+', ' ', label).strip()
    label = re.sub(r'\b(네이버페이|톡톡|쿠폰)\b', ' ', label)
    return re.sub(r'\s+', ' ', label).strip()


def looks_store_like(name: str, address: str = '') -> bool:
    blob = f'{name} {address}'.lower()
    return any(k.lower() in blob for k in STORE_KEYWORDS)


def infer_area(address: str, name: str) -> str:
    blob = f'{address} {name}'
    for area, keys in AREA_RULES:
        if any(k in blob for k in keys):
            return area
    if '서울 ' in address:
        district_defaults = [
            ('강남구', '역삼/선릉'), ('서초구', '강남역'), ('마포구', '홍대/합정/상수'), ('영등포구', '영등포/문래'),
            ('송파구', '잠실/송리단길'), ('용산구', '이태원'), ('광진구', '건대입구'), ('성동구', '성수'),
        ]
        for key, area in district_defaults:
            if key in address:
                return area
    return '영등포/문래'


def score_row(area: str, phone: str):
    tier = '1' if area in PRIORITY_AREAS else '2'
    location = '5' if area in PRIORITY_AREAS else '4'
    contact = '5' if phone.startswith(('010', '0507')) else '3'
    total = str(int(location) + 4 + int(contact))
    grade = 'A' if phone.startswith(('010', '0507')) else 'B'
    message_type = '1' if area in {'강남역','신논현/논현','역삼/선릉','삼성/코엑스','홍대/합정/상수','신촌/이대','성수','잠실/송리단길','영등포/문래','여의도','건대입구','왕십리/한양대','마포/공덕','이태원'} else '2'
    return tier, location, contact, total, grade, message_type


def load_rows():
    return list(csv.DictReader(CSV_PATH.open(encoding='utf-8')))


def save_rows(rows):
    with CSV_PATH.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def parse_search_items(query: str, html_doc: str):
    items = []
    blocks = re.findall(r'(<li class="VLTHu JJ4Cd" data-laim-exp-id="loc_plc".*?</li>)', html_doc, re.S)
    for block in blocks:
        pid_m = re.search(r'data-loc_plc-doc-id="(\d+)"', block)
        name_m = re.search(r'<span class="YwYLL">(.*?)</span>', block)
        phone_m = re.search(r'<div class="KUVY7 l8afP">(010-\d{4}-\d{4}|0507-\d{3,4}-\d{4}|02-\d{3,4}-\d{4}|070-\d{3,4}-\d{4})<a ', block)
        loc_m = re.search(r'<span class="suKMR">(.*?)</span>', block)
        title_m = re.search(r'data-title="([^"]+)"', block)
        if not (pid_m and name_m and phone_m and title_m):
            continue
        name = clean_label(name_m.group(1))
        if not name:
            continue
        lowered = name.lower()
        if any(token in lowered for token in NAME_EXCLUDE_PATTERNS):
            continue
        title_lines = [x.strip() for x in html.unescape(title_m.group(1)).split('\n') if x.strip()]
        addr_candidate = ' '.join(title_lines[1:] if len(title_lines) > 1 else title_lines)
        addr_candidate = re.sub(r'\s+', ' ', addr_candidate).strip()
        loc_text = clean_label(loc_m.group(1)) if loc_m else ''
        loc_parts = loc_text.split()
        prefix = ' '.join(loc_parts[:2]) if len(loc_parts) >= 2 else loc_text
        if addr_candidate and not addr_candidate.startswith('서울') and prefix.startswith('서울'):
            address = f'{prefix} {addr_candidate}'.strip()
        else:
            address = addr_candidate
        address = address.replace('서울특별시', '서울').replace('서울시', '서울').strip()
        items.append({
            'query': query,
            'place_id': pid_m.group(1),
            'store_name': name,
            'phone': normalize_phone(phone_m.group(1)),
            'address': address,
            'district_hint': loc_text,
            'map_link': f'https://pcmap.place.naver.com/place/{pid_m.group(1)}/home',
        })
    return items


def update_progress(rows, added_rows, query_counts, scanned_candidates):
    filled = [r for r in rows if (r.get('store_name') or '').strip()]
    phone_ready = sum(1 for r in filled if (r.get('phone') or '').startswith(('010', '0507')))
    needs = sum(1 for r in filled if not (r.get('phone') or '').strip() or (r.get('phone') or '').startswith(('02', '070', '080', '1800')))
    now = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
    obj = json.loads(PROGRESS_JSON.read_text()) if PROGRESS_JSON.exists() else {'project': 'seoul_vape_500', 'verification': {'proof': []}, 'currentBatch': {}}
    obj['status'] = 'running'
    obj['lastVerifiedAtKst'] = now
    obj['currentBatch'] = {
        'name': 'Batch 2',
        'areas': ['강남/삼성', '홍대/신촌', '성수/건대', '영등포/여의도'],
        'stage': 'hotspot_wave2_verified',
    }
    obj['counts'] = {'total': len(filled), 'phoneReady': phone_ready, 'needsCheck': needs}
    proof = obj.setdefault('verification', {}).setdefault('proof', [])
    proof.append(f'hotspot wave2 added={len(added_rows)}, scanned={scanned_candidates}, by_query={dict(query_counts)}')
    obj['nextProofPoint'] = 'dashboard refreshed with second-wave hotspot verified additions'
    PROGRESS_JSON.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    if PROGRESS_MD.exists():
        text = PROGRESS_MD.read_text(encoding='utf-8')
        text = re.sub(r'- 총 매장 수: \d+', f'- 총 매장 수: {len(filled)}', text)
        text = re.sub(r'- 문자 가능 번호: \d+', f'- 문자 가능 번호: {phone_ready}', text)
        text = re.sub(r'- 재확인 필요: \d+', f'- 재확인 필요: {needs}', text)
        text = re.sub(r'- 최근 추가 반영: \d+건', f'- 최근 추가 반영: {len(added_rows)}건', text)
        text = re.sub(r'- 현재 단계: .*', '- 현재 단계: hotspot_wave2_verified', text)
        text = re.sub(r'- 마지막 검증 시각\(KST\): .*', f'- 마지막 검증 시각(KST): {now}', text)
        PROGRESS_MD.write_text(text, encoding='utf-8')


def main():
    rows = load_rows()
    before_total = len([r for r in rows if (r.get('store_name') or '').strip()])
    before_sms = sum(1 for r in rows if (r.get('store_name') or '').strip() and (r.get('phone') or '').startswith(('010', '0507')))

    existing_names = {normalize_name(r.get('store_name') or '') for r in rows if (r.get('store_name') or '').strip()}
    existing_addrs = {normalize_addr(r.get('address') or '') for r in rows if (r.get('address') or '').strip()}
    existing_phones = {(r.get('phone') or '').strip() for r in rows if (r.get('phone') or '').strip()}

    scanned_candidates = 0
    query_counts = Counter()
    added_rows = []
    search_failures = []
    seen_place_ids = set()

    for query in QUERY_PLAN:
        try:
            time.sleep(1.2)
            html_doc = fetch_search(query)
            items = parse_search_items(query, html_doc)
        except Exception as exc:
            search_failures.append({'query': query, 'error': str(exc)})
            log(f'query failed: {query} :: {exc}')
            continue

        log(f'query {query}: parsed {len(items)} candidates')
        for item in items:
            scanned_candidates += 1
            name = item['store_name']
            address = item['address']
            phone = item['phone']
            if not address.startswith('서울 '):
                continue
            if not phone.startswith(('010-', '0507-')):
                continue
            if item['place_id'] in seen_place_ids:
                continue
            n_name = normalize_name(name)
            n_addr = normalize_addr(address)
            if phone in existing_phones or n_addr in existing_addrs or (n_name and n_name in existing_names):
                continue
            if not looks_store_like(name, address):
                continue
            area = infer_area(address, name)
            tier, location, contact, total, grade, message_type = score_row(area, phone)
            row = {
                'priority_tier': tier,
                'area': area,
                'store_name': name,
                'address': address,
                'phone': phone,
                'map_link': item['map_link'],
                'instagram_or_site': '',
                'review_count': '',
                'rating': '',
                'store_type': '전자담배 전문점',
                'store_tone': f'{area} 네이버 검색 핫스팟 2차 검증',
                'location_score': location,
                'specialty_score': '4',
                'contactability_score': contact,
                'total_score': total,
                'priority_grade': grade,
                'message_type': message_type,
                'contact_status': '미접촉',
                'last_contact_date': '',
                'notes': f'네이버 검색 핫스팟 2차 확장 {TODAY} · query={query}',
            }
            rows.append(row)
            added_rows.append(row)
            query_counts[query] += 1
            seen_place_ids.add(item['place_id'])
            existing_phones.add(phone)
            existing_addrs.add(n_addr)
            existing_names.add(n_name)
            log(f'added {query} :: {name} :: {phone}')

    save_rows(rows)

    summary = {
        'before_total': before_total,
        'after_total': len([r for r in rows if (r.get('store_name') or '').strip()]),
        'before_sms': before_sms,
        'after_sms': sum(1 for r in rows if (r.get('store_name') or '').strip() and (r.get('phone') or '').startswith(('010', '0507'))),
        'added_total': len(added_rows),
        'scanned_candidates': scanned_candidates,
        'query_counts': dict(query_counts),
        'search_failures': search_failures,
        'added_rows': [
            {'store_name': r['store_name'], 'phone': r['phone'], 'area': r['area'], 'address': r['address'], 'map_link': r['map_link']}
            for r in added_rows
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    update_progress(rows, added_rows, query_counts, scanned_candidates)
    log(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
