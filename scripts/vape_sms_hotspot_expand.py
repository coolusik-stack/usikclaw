#!/usr/bin/env python3
import csv
import html
import json
import re
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path('/Users/usuk/.openclaw/workspace')
CSV_PATH = ROOT / 'generated' / 'vape_stores_seoul_template.csv'
PROGRESS_JSON = ROOT / 'generated' / 'vape_500_progress.json'
PROGRESS_MD = ROOT / 'generated' / 'vape_500_progress.md'
QUEUE_JSON = ROOT / 'generated' / 'vape_500_queue.json'
LOG_PATH = ROOT / 'generated' / 'logs' / 'vape_sms_hotspot_expand.log'
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
KST = timezone(timedelta(hours=9))
TODAY = datetime.now(KST).strftime('%Y-%m-%d')

FIELDNAMES = [
    'priority_tier','area','store_name','address','phone','map_link','instagram_or_site',
    'review_count','rating','store_type','store_tone','location_score','specialty_score',
    'contactability_score','total_score','priority_grade','message_type','contact_status',
    'last_contact_date','notes'
]

SOURCE_URLS = {
    'martha': 'https://m.martha-vape.com/bs21/layout/map_store2.html',
    'litmus': 'http://litmuskorea.co.kr/sitefront/Litmuskorea/stores/',
    'justfog': 'https://m.justfog.co.kr/stockist.html',
}

PRIORITY_AREAS = {
    '강남역', '신논현/논현', '역삼/선릉', '삼성/코엑스', '홍대/합정/상수', '신촌/이대',
    '성수', '잠실/송리단길', '영등포/문래', '여의도', '마포/공덕', '이태원', '건대입구', '왕십리/한양대'
}

STORE_KEYWORDS = [
    '전자담배', '베이프', 'vape', 'vap', '하카', '마샤', '라미야', '너구리굴', '시가',
    '스모크', '킹콩', '듀바코', '마크', '에어베이프', '베이핑', '액상', '아울렛', '멀티샵',
    '증기샵', '원더베이프', '킹스베이프', '고릴라', '베이퍼', '스누스'
]

AREA_RULES = [
    ('강남역', ['강남대로66길', '강남대로84길', '강남대로 390', '강남대로 438', '역삼로 111', '서초동 1327', '서초구 강남대로']),
    ('신논현/논현', ['학동로', '논현동', '봉은사로2길', '강남대로118길', '신논현', '논현로']),
    ('역삼/선릉', ['역삼동', '테헤란로', '선릉로', '대치동', '테헤란로4길', '테헤란로70길']),
    ('삼성/코엑스', ['삼성동', '봉은사로 420', '봉은사로82길', '영동대로', '삼성로103길', '코엑스']),
    ('홍대/합정/상수', ['서교동', '동교동', '양화로', '독막로', '와우산로', '합정동', '상수', '연남', '성지1길']),
    ('신촌/이대', ['신촌로', '이화여대길', '대현동', '창천동', '연세로', '서대문구 거북골로']),
    ('성수', ['성수동', '성수이로', '연무장', '서울숲', '뚝섬', '성암로 215']),
    ('이태원', ['이태원', '한남동', '대사관로', '한강대로 95', '한강대로 257', '용산구 한강대로']),
    ('잠실/송리단길', ['잠실', '올림픽로', '석촌', '송리단길', '풍납동']),
    ('문정/가락', ['문정동', '법원로', '가락동', '송파대로28길', '송이로', '마천로']),
    ('여의도', ['여의도동', '의사당대로', '국회대로 780', '여의대방로']),
    ('영등포/문래', ['영등포동', '영중로', '양평로', '선유로', '대방천로', '문래', '버드나루로']),
    ('마포/공덕', ['마포대로', '신공덕동', '상암동', '월드컵로 190', '성암로 215']),
    ('건대입구', ['광진구', '자양동', '자양로', '군자동', '중곡동', '능동로', '광나루로56길']),
    ('왕십리/한양대', ['왕십리', '행당동', '용답동', '한양대']),
    ('천호/강동', ['천호동', '강동구', '양재대로', '천중로', '길동', '성내동', '암사동', '고덕로']),
    ('은평/연신내', ['은평구', '불광동', '연서로', '통일로', '증산로', '응암동', '대조동', '진관동']),
    ('강서/마곡', ['강서구', '마곡', '화곡동', '우장산', '양천향교', '가양동', '발산']),
    ('구로디지털단지', ['구로구', '금천구', '가산동', '개봉동', '디지털로', '벚꽃로', '고척동', '시흥대로']),
    ('사당/방배', ['동작구', '사당동', '방배동', '남부순환로 2029', '만양로', '상도로']),
    ('서초/양재', ['서초구', '서초동', '효령로', '양재', '서초대로']),
    ('서울대입구/샤로수길', ['관악로', '봉천동', '낙성대', '서울대입구', '샤로수길', '인헌', '남부순환로 1924']),
    ('신림', ['신림동', '신림로', '조원중앙로']),
    ('동대문/청량리', ['동대문구', '답십리', '장안동', '왕산로', '이문로', '청량리']),
    ('도봉/창동', ['도봉구', '창동', '쌍문동']),
    ('수유/미아', ['강북구', '수유동', '미아동', '솔샘로', '오패산로', '노해로', '도봉로 146']),
    ('성북/길음', ['성북구', '동소문로', '길음동', '성신여대']),
    ('종로/을지로/충무로', ['종로구', '중구', '삼봉로', '종로 ', '서소문로', '신당동', '충무로', '을지로', '다산로']),
    ('중랑/면목', ['중랑구', '면목동', '용마산로', '중랑역로']),
    ('목동/오목교', ['양천구', '목동', '신정동', '오목교', '신월로']),
    ('노원', ['노원구', '공릉동', '상계동', '월계동']),
    ('압구정/청담', ['압구정', '청담', '도산대로', '신사동']),
]


def log(msg: str):
    ts = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    with LOG_PATH.open('a', encoding='utf-8') as f:
        f.write(line + '\n')


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'ignore')


def clean_text(s: str) -> str:
    s = re.sub(r'<!--.*?-->', ' ', s, flags=re.S)
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    return ' '.join(s.split()).strip()


def normalize_name(s: str) -> str:
    s = (s or '').lower()
    s = s.replace('서울특별시', '서울')
    s = re.sub(r'\([^)]*\)', '', s)
    s = re.sub(r'(전자담배|베이프|vape|vap|멀티샵|멀티샾|점|본점|매장|전담)', '', s)
    s = re.sub(r'[^0-9a-z가-힣]+', '', s)
    return s.strip()


def normalize_addr(s: str) -> str:
    s = (s or '').replace('서울특별시', '서울').replace('서울시', '서울')
    return re.sub(r'[^0-9a-z가-힣]+', '', s.lower())


def normalize_phone(s: str) -> str:
    s = (s or '').strip().replace('.', '-').replace(' ', '')
    m = re.search(r'(010-\d{4}-\d{4}|0507-\d{3,4}-\d{4}|02-\d{3,4}-\d{4}|070-\d{3,4}-\d{4})', s)
    return m.group(1) if m else s


def looks_store_like(name: str, addr: str) -> bool:
    blob = f'{name} {addr}'.lower()
    return any(k.lower() in blob for k in STORE_KEYWORDS)


def infer_area(address: str, name: str) -> str:
    blob = f'{address} {name}'
    for area, keys in AREA_RULES:
        if any(k in blob for k in keys):
            return area
    if '서울 ' in address:
        if '강남구' in address:
            return '역삼/선릉'
        if '서초구' in address:
            return '서초/양재'
        if '마포구' in address:
            return '홍대/합정/상수'
        if '영등포구' in address:
            return '영등포/문래'
        if '송파구' in address:
            return '잠실/송리단길'
        if '용산구' in address:
            return '이태원'
        if '광진구' in address:
            return '건대입구'
        if '성동구' in address:
            return '성수'
        if '강서구' in address:
            return '강서/마곡'
        if '관악구' in address:
            return '서울대입구/샤로수길'
        if '중구' in address or '종로구' in address:
            return '종로/을지로/충무로'
        if '동대문구' in address:
            return '동대문/청량리'
        if '중랑구' in address:
            return '중랑/면목'
        if '강동구' in address:
            return '천호/강동'
        if '은평구' in address:
            return '은평/연신내'
        if '도봉구' in address:
            return '도봉/창동'
        if '강북구' in address:
            return '수유/미아'
        if '성북구' in address:
            return '성북/길음'
        if '양천구' in address:
            return '목동/오목교'
        if '노원구' in address:
            return '노원'
        if '동작구' in address:
            return '사당/방배'
        if '금천구' in address or '구로구' in address:
            return '구로디지털단지'
        if '서대문구' in address:
            return '신촌/이대'
    return '영등포/문래'


def score_row(area: str, phone: str):
    tier = '1' if area in PRIORITY_AREAS else '2'
    location = '5' if area in PRIORITY_AREAS else '4'
    contact = '5' if phone.startswith(('010', '0507')) else '3'
    total = str(int(location) + 4 + int(contact))
    grade = 'A' if phone.startswith(('010', '0507')) else 'B'
    message_type = '1' if area in {'강남역','신논현/논현','역삼/선릉','삼성/코엑스','홍대/합정/상수','신촌/이대','성수','잠실/송리단길'} else '2'
    return tier, location, contact, total, grade, message_type


def parse_martha(txt: str):
    pat = re.compile(r'<h3>\[(?P<bracket>[^\]]+)\]\s*(?P<name>[^<]+)</h3><div>(?P<addr>[^<]+)</div><div class="bs_tel">(?P<phone>[^<]+)</div>', re.S)
    out = []
    for m in pat.finditer(txt):
        name = clean_text(m.group('name'))
        addr = clean_text(m.group('addr'))
        phone = normalize_phone(clean_text(m.group('phone')))
        out.append({'source': 'martha', 'store_name': name, 'address': addr, 'phone': phone, 'map_link': SOURCE_URLS['martha']})
    return out


def parse_litmus(txt: str):
    out = []
    for tr in re.findall(r'<tr>(.*?)</tr>', txt, re.S):
        tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)
        if len(tds) < 2:
            continue
        name = clean_text(tds[0])
        detail = clean_text(tds[1])
        m = re.search(r'\((010-\d{4}-\d{4}|0507-\d{3,4}-\d{4}|02-\d{3,4}-\d{4}|070-\d{3,4}-\d{4})\)\s*(.+)$', detail)
        if not m:
            continue
        phone = normalize_phone(m.group(1))
        addr = m.group(2).strip()
        out.append({'source': 'litmus', 'store_name': name, 'address': addr, 'phone': phone, 'map_link': SOURCE_URLS['litmus']})
    return out


def parse_justfog(txt: str):
    pat = re.compile(r'<div class="txt_name">.*?>\s*([^<]+?)\s*</div>\s*<div class="txt_addr">([^<]+)</div>\s*<div class="txt_tel">Tel\.\s*([^<]+)</div>', re.S)
    out = []
    for name, addr, phone in pat.findall(txt):
        out.append({
            'source': 'justfog',
            'store_name': clean_text(name),
            'address': clean_text(addr),
            'phone': normalize_phone(phone),
            'map_link': SOURCE_URLS['justfog'],
        })
    return out


def load_rows():
    with CSV_PATH.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_rows(rows):
    with CSV_PATH.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)


def update_progress(rows, added_count: int, source_counts: dict, unresolved_fixed: int):
    filled = [r for r in rows if (r.get('store_name') or '').strip()]
    phone_ready = sum(1 for r in filled if (r.get('phone') or '').strip().startswith(('010','0507')))
    needs = sum(1 for r in filled if not (r.get('phone') or '').strip() or (r.get('phone') or '').strip().startswith(('02','070','080','1800')))
    now = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
    obj = json.loads(PROGRESS_JSON.read_text()) if PROGRESS_JSON.exists() else {'project': 'seoul_vape_500', 'verification': {'proof': []}, 'currentBatch': {}}
    obj['status'] = 'running'
    obj['lastVerifiedAtKst'] = now
    obj['currentBatch'] = {
        'name': 'Batch 2',
        'areas': ['강남/삼성', '홍대/신촌', '성수/건대', '영등포/여의도'],
        'stage': 'source_locator_sms_expansion'
    }
    obj['counts'] = {'total': len(filled), 'phoneReady': phone_ready, 'needsCheck': needs}
    proof = obj.setdefault('verification', {}).setdefault('proof', [])
    proof.append(f'source locator expansion added={added_count}, unresolved_fixed={unresolved_fixed}, by_source={source_counts}')
    obj['nextProofPoint'] = 'dashboard + public link refreshed with updated SMS-ready pool'
    PROGRESS_JSON.write_text(json.dumps(obj, ensure_ascii=False, indent=2))
    if PROGRESS_MD.exists():
        text = PROGRESS_MD.read_text(encoding='utf-8')
        text = re.sub(r'- 총 매장 수: \d+', f'- 총 매장 수: {len(filled)}', text)
        text = re.sub(r'- 문자 가능 번호: \d+', f'- 문자 가능 번호: {phone_ready}', text)
        text = re.sub(r'- 재확인 필요: \d+', f'- 재확인 필요: {needs}', text)
        text = re.sub(r'- 최근 추가 반영: \d+건', f'- 최근 추가 반영: {added_count}건', text)
        text = re.sub(r'- 현재 단계: .*', '- 현재 단계: source_locator_sms_expansion', text)
        text = re.sub(r'- 마지막 검증 시각\(KST\): .*', f'- 마지막 검증 시각(KST): {now}', text)
        PROGRESS_MD.write_text(text, encoding='utf-8')


def main():
    rows = load_rows()
    before_total = len([r for r in rows if (r.get('store_name') or '').strip()])
    before_sms = sum(1 for r in rows if (r.get('store_name') or '').strip() and (r.get('phone') or '').startswith(('010','0507')))

    existing_phones = {(r.get('phone') or '').strip() for r in rows if (r.get('phone') or '').strip()}
    existing_addrs = {normalize_addr(r.get('address') or '') for r in rows if (r.get('address') or '').strip()}
    existing_names = {normalize_name(r.get('store_name') or '') for r in rows if (r.get('store_name') or '').strip()}

    raw = []
    raw.extend(parse_martha(fetch(SOURCE_URLS['martha'])))
    raw.extend(parse_litmus(fetch(SOURCE_URLS['litmus'])))
    raw.extend(parse_justfog(fetch(SOURCE_URLS['justfog'])))

    candidates = []
    for item in raw:
        phone = normalize_phone(item['phone'])
        addr = (item['address'] or '').replace('서울특별시', '서울').replace('서울시', '서울').strip()
        name = (item['store_name'] or '').strip()
        if not addr.startswith('서울 '):
            continue
        if not phone.startswith(('010-', '0507-')):
            continue
        if '*' in phone:
            continue
        if not looks_store_like(name, addr):
            continue
        candidates.append({
            'source': item['source'],
            'store_name': name,
            'address': addr,
            'phone': phone,
            'map_link': item['map_link'],
        })

    by_phone = defaultdict(list)
    for item in candidates:
        by_phone[item['phone']].append(item)

    filtered = []
    ambiguous_phones = set()
    for phone, items in by_phone.items():
        addr_keys = {normalize_addr(x['address']) for x in items}
        if len(addr_keys) > 1:
            ambiguous_phones.add(phone)
            continue
        def rank(x):
            name = x['store_name']
            score = 0
            if '전자담배' in name: score += 3
            if '베이프' in name or 'VAPE' in name.upper(): score += 2
            if x['source'] == 'martha': score += 1
            return (-score, len(name))
        filtered.append(sorted(items, key=rank)[0])

    added = []
    source_counts = defaultdict(int)
    for item in filtered:
        n_name = normalize_name(item['store_name'])
        n_addr = normalize_addr(item['address'])
        phone = item['phone']
        if phone in existing_phones or n_addr in existing_addrs or (n_name and n_name in existing_names):
            continue
        area = infer_area(item['address'], item['store_name'])
        tier, location, contact, total, grade, message_type = score_row(area, phone)
        row = {
            'priority_tier': tier,
            'area': area,
            'store_name': item['store_name'],
            'address': item['address'],
            'phone': phone,
            'map_link': item['map_link'],
            'instagram_or_site': '',
            'review_count': '',
            'rating': '',
            'store_type': '전자담배 전문점',
            'store_tone': f'{area} 공식 스토어 로케이터 검증',
            'location_score': location,
            'specialty_score': '4',
            'contactability_score': contact,
            'total_score': total,
            'priority_grade': grade,
            'message_type': message_type,
            'contact_status': '미접촉',
            'last_contact_date': '',
            'notes': f'공식 스토어 로케이터({item["source"]}) 기반 SMS 우선 확장 배치 {TODAY}'
        }
        rows.append(row)
        added.append(row)
        source_counts[item['source']] += 1
        existing_phones.add(phone)
        existing_addrs.add(n_addr)
        existing_names.add(n_name)

    save_rows(rows)

    unresolved_fixed = 0
    if QUEUE_JSON.exists():
        queue = json.loads(QUEUE_JSON.read_text())
        added_phones = {r['phone'] for r in added}
        added_addr_keys = {normalize_addr(r['address']) for r in added}
        for item in queue:
            phone = normalize_phone(item.get('hint_phone', ''))
            addr_key = normalize_addr(item.get('hint_address', ''))
            if item.get('status') in {'no_place_id', 'non_seoul', 'error', 'low_contact'} and (phone in added_phones or addr_key in added_addr_keys):
                item['status'] = 'added_from_source'
                unresolved_fixed += 1
        QUEUE_JSON.write_text(json.dumps(queue, ensure_ascii=False, indent=2))

    update_progress(rows, len(added), dict(source_counts), unresolved_fixed)

    after_total = len([r for r in rows if (r.get('store_name') or '').strip()])
    after_sms = sum(1 for r in rows if (r.get('store_name') or '').strip() and (r.get('phone') or '').startswith(('010','0507')))
    summary = {
        'before_total': before_total,
        'after_total': after_total,
        'before_sms': before_sms,
        'after_sms': after_sms,
        'added_total': len(added),
        'source_counts': dict(source_counts),
        'ambiguous_phone_skips': len(ambiguous_phones),
        'unresolved_fixed': unresolved_fixed,
    }
    out = ROOT / 'generated' / 'vape_sms_hotspot_expand_summary.json'
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    log(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
