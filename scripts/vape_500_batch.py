#!/usr/bin/env python3
import csv
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path('/Users/usuk/.openclaw/workspace')
CSV_PATH = ROOT / 'generated' / 'vape_stores_seoul_template.csv'
PROGRESS_JSON = ROOT / 'generated' / 'vape_500_progress.json'
PROGRESS_MD = ROOT / 'generated' / 'vape_500_progress.md'
QUEUE_JSON = ROOT / 'generated' / 'vape_500_queue.json'
LOG_DIR = ROOT / 'generated' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / 'vape_500_batch.log'
KST = timezone(timedelta(hours=9))

FIELDNAMES = [
    'priority_tier','area','store_name','address','phone','map_link','instagram_or_site',
    'review_count','rating','store_type','store_tone','location_score','specialty_score',
    'contactability_score','total_score','priority_grade','message_type','contact_status',
    'last_contact_date','notes'
]

SOURCE_URLS = {
    'martha': 'https://m.martha-vape.com/bs21/layout/map_store2.html',
    'endpuff': 'https://end-puff.com/bs21/layout/map_all2.html',
    'justfog': 'https://m.justfog.co.kr/stockist.html',
}

AREA_RULES = [
    ('홍대/합정/상수', ['마포구 와우산', '마포구 양화로', '마포구 잔다리로', '마포구 독막로', '마포구 동교로', '마포구 포은로', '마포구 성지1길', '서교동', '동교동', '합정동', '상수', '망원동', '연남']),
    ('신촌/이대', ['서대문구 신촌로', '서대문구 대현', '창천동', '이대', '아현동', '대흥동', '광흥창']),
    ('성수', ['성동구 성수', '연무장', '성수이로', '서울숲', '뚝섬']),
    ('이태원', ['용산구 보광로', '용산구 이태원', '한강대로', '갈월동', '한남']),
    ('왕십리/한양대', ['왕십리', '행당동', '한양대']),
    ('노원', ['노원구', '상계동', '공릉동', '월계동', '석계로']),
    ('목동/오목교', ['양천구 목동', '오목교', '신정동', '신목로', '목동중앙']),
    ('사당/방배', ['사당', '방배']),
    ('건대입구', ['광진구', '자양동', '화양동', '건대']),
    ('여의도', ['여의도', '의사당대로']),
    ('영등포/문래', ['문래', '영등포']),
    ('마포/공덕', ['공덕', '마포대로']),
    ('강남역', ['강남구 강남대로', '역삼로', '서초구 강남대로']),
    ('신논현/논현', ['학동로', '봉은사로', '논현동']),
]


def log(msg: str):
    ts = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    with LOG_PATH.open('a', encoding='utf-8') as f:
        f.write(line + '\n')


def run(cmd: str, timeout: int = 120) -> str:
    return subprocess.check_output(cmd, shell=True, text=True, timeout=timeout).strip()


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'ignore')


def infer_area(address: str, name: str) -> str | None:
    blob = f'{address} {name}'
    for area, keys in AREA_RULES:
        if any(k in blob for k in keys):
            return area
    return None


def normalize(s: str) -> str:
    return re.sub(r'\s+', '', (s or '').strip())


def load_csv_rows():
    with CSV_PATH.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    return rows


def write_csv_rows(rows):
    with CSV_PATH.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)


def bootstrap_candidates():
    candidates = []
    # Martha / EndPuff patterns
    for source in ['martha', 'endpuff']:
        try:
            txt = fetch(SOURCE_URLS[source])
            pat = re.compile(r'<h3>\[(?P<bracket>[^\]]+)\]\s*(?P<name>[^<]+)</h3><div>(?P<addr>[^<]+)</div><div class="bs_tel">(?P<phone>[^<]+)</div>', re.S)
            for m in pat.finditer(txt):
                name = re.sub(r'\s+', ' ', m.group('name')).strip()
                address = re.sub(r'\s+', ' ', m.group('addr')).strip()
                phone = re.sub(r'\s+', '', m.group('phone')).strip()
                if '서울' not in address:
                    continue
                area = infer_area(address, name)
                if not area:
                    continue
                candidates.append({
                    'query': name,
                    'source': source,
                    'area': area,
                    'hint_name': name,
                    'hint_address': address,
                    'hint_phone': phone,
                    'status': 'queued'
                })
        except Exception as e:
            log(f'bootstrap error {source}: {e}')
    # Justfog pattern
    try:
        txt = fetch(SOURCE_URLS['justfog'])
        pat = re.compile(r'<div class="txt_name">.*?>\s*([^<]+?)\s*</div>\s*<div class="txt_addr">([^<]+)</div>\s*<div class="txt_tel">Tel\.\s*([^<]+)</div>', re.S)
        for m in pat.finditer(txt):
            name = re.sub(r'\s+', ' ', m.group(1)).strip()
            address = re.sub(r'\s+', ' ', m.group(2)).strip()
            phone = re.sub(r'\s+', '', m.group(3)).strip()
            if '서울' not in address:
                continue
            area = infer_area(address, name)
            if not area:
                continue
            candidates.append({
                'query': name,
                'source': 'justfog',
                'area': area,
                'hint_name': name,
                'hint_address': address,
                'hint_phone': phone,
                'status': 'queued'
            })
    except Exception as e:
        log(f'bootstrap error justfog: {e}')

    dedup = {}
    for c in candidates:
        key = (normalize(c['hint_name']), normalize(c['hint_address']))
        dedup[key] = c
    return list(dedup.values())


def load_queue(existing_rows):
    if QUEUE_JSON.exists():
        return json.loads(QUEUE_JSON.read_text())
    queue = bootstrap_candidates()
    existing_names = {normalize(r.get('store_name', '')) for r in existing_rows if (r.get('store_name') or '').strip()}
    existing_addrs = {normalize(r.get('address', '')) for r in existing_rows if (r.get('address') or '').strip()}
    existing_phones = {(r.get('phone') or '').strip() for r in existing_rows if (r.get('phone') or '').strip()}
    for c in queue:
        if normalize(c['hint_name']) in existing_names or normalize(c['hint_address']) in existing_addrs or c['hint_phone'] in existing_phones:
            c['status'] = 'known'
    QUEUE_JSON.write_text(json.dumps(queue, ensure_ascii=False, indent=2))
    return queue


def save_queue(queue):
    QUEUE_JSON.write_text(json.dumps(queue, ensure_ascii=False, indent=2))


def naver_place_id(query: str) -> str | None:
    enc = urllib.parse.quote(query)
    run(f"openclaw browser --browser-profile openclaw open 'https://map.naver.com/p/search/{enc}' >/dev/null", timeout=120)
    time.sleep(2)
    reqs = run("openclaw browser --browser-profile openclaw requests | grep 'pcmap.place.naver.com/place/' | tail -n 6", timeout=60)
    ids = re.findall(r'pcmap\.place\.naver\.com/place/(\d+)/home.*searchText=([^\s]+)', reqs)
    for pid, search in reversed(ids):
        if urllib.parse.unquote(search) == query:
            return pid
    m = re.findall(r'pcmap\.place\.naver\.com/place/(\d+)/home', reqs)
    return m[-1] if m else None


def naver_place_text(pid: str, query: str) -> str:
    enc = urllib.parse.quote(query)
    url = f'https://pcmap.place.naver.com/place/{pid}/home?from=map&fromPanelNum=1&additionalHeight=76&locale=ko&svcName=map_pcv5&searchText={enc}'
    run(f"openclaw browser --browser-profile openclaw open '{url}' >/dev/null", timeout=120)
    time.sleep(2)
    return run("openclaw browser --browser-profile openclaw evaluate --fn '() => document.body.innerText'", timeout=120)


def parse_place_text(text: str):
    address = ''
    phone = ''
    name = ''
    lines = [x.strip() for x in text.replace('"','').split('\n') if x.strip()]
    if lines:
        name = lines[0]
    for i, line in enumerate(lines):
        if line == '주소' and i + 1 < len(lines):
            address = lines[i + 1]
        if line == '전화번호' and i + 1 < len(lines):
            phone = lines[i + 1].replace('복사', '').strip()
    phone_match = re.search(r'(010-\d{4}-\d{4}|0507-\d{3,4}-\d{4}|02-\d{3,4}-\d{4}|070-\d{3,4}-\d{4}|080-\d{3,4}-\d{4}|18\d{2}-\d{4})', text)
    if phone_match:
        phone = phone_match.group(1)
    return name, address, phone


def score_row(area: str, phone: str):
    tier = '1' if area in ['홍대/합정/상수', '성수', '강남역', '신논현/논현'] else '2'
    location = '5' if area in ['홍대/합정/상수', '성수'] else '4'
    contact = '5' if phone.startswith(('010', '0507')) else '3'
    total = str(int(location) + 4 + int(contact))
    grade = 'A' if phone.startswith(('010', '0507')) else 'B'
    mtype = '1' if area in ['홍대/합정/상수', '신촌/이대', '성수'] else '2'
    return tier, location, contact, total, grade, mtype


def update_progress(rows, stage: str, note: str):
    filled = [r for r in rows if (r.get('store_name') or '').strip()]
    phone_ready = sum(1 for r in filled if (r.get('phone') or '').strip().startswith(('010','0507')))
    needs = sum(1 for r in filled if not (r.get('phone') or '').strip() or (r.get('phone') or '').strip().startswith(('02','070','080','1800')))
    now = datetime.now(KST).strftime('%Y-%m-%d %H:%M')
    if PROGRESS_JSON.exists():
        obj = json.loads(PROGRESS_JSON.read_text())
    else:
        obj = {'project': 'seoul_vape_500', 'verification': {'proof': []}, 'currentBatch': {}}
    obj['status'] = 'running'
    obj['lastVerifiedAtKst'] = now
    obj['currentBatch'] = {
        'name': 'Batch 1',
        'areas': ['홍대/합정/상수', '신촌/이대', '성수'],
        'stage': stage,
    }
    obj['counts'] = {'total': len(filled), 'phoneReady': phone_ready, 'needsCheck': needs}
    obj.setdefault('verification', {}).setdefault('proof', []).append(note)
    obj['nextProofPoint'] = 'next verified additions reflected in CSV and reported to user'
    PROGRESS_JSON.write_text(json.dumps(obj, ensure_ascii=False, indent=2))
    if PROGRESS_MD.exists():
        text = PROGRESS_MD.read_text()
        text = re.sub(r'- 총 매장 수: \d+', f'- 총 매장 수: {len(filled)}', text)
        text = re.sub(r'- 문자 가능 번호: \d+', f'- 문자 가능 번호: {phone_ready}', text)
        text = re.sub(r'- 마지막 검증 시각\(KST\): .*', f'- 마지막 검증 시각(KST): {now}', text)
        text = re.sub(r'- 현재 단계: .*', f'- 현재 단계: {stage}', text)
        PROGRESS_MD.write_text(text)


def ensure_browser():
    try:
        run("openclaw browser --browser-profile openclaw start >/dev/null", timeout=120)
    except Exception as e:
        log(f'browser start error: {e}')


def main():
    ensure_browser()
    rows = load_csv_rows()
    queue = load_queue(rows)
    existing_names = {normalize(r.get('store_name', '')) for r in rows if (r.get('store_name') or '').strip()}
    existing_addrs = {normalize(r.get('address', '')) for r in rows if (r.get('address') or '').strip()}
    existing_phones = {(r.get('phone') or '').strip() for r in rows if (r.get('phone') or '').strip()}

    pending = [c for c in queue if c.get('status') == 'queued']
    if not pending:
        update_progress(rows, 'idle', 'queue exhausted or awaiting more candidates')
        log('No queued candidates left')
        return

    processed = 0
    added = 0
    for cand in pending[:3]:
        processed += 1
        query = cand['query']
        try:
            pid = naver_place_id(query)
            if not pid:
                cand['status'] = 'no_place_id'
                continue
            text = naver_place_text(pid, query)
            name, address, phone = parse_place_text(text)
            if '서울' not in address:
                cand['status'] = 'non_seoul'
                cand['verified_name'] = name
                continue
            area = infer_area(address, name or query) or cand['area']
            if normalize(name) in existing_names or normalize(address) in existing_addrs or (phone and phone in existing_phones):
                cand['status'] = 'duplicate'
                cand['verified_name'] = name
                cand['verified_address'] = address
                cand['verified_phone'] = phone
                continue
            if not phone.startswith(('010', '0507')):
                cand['status'] = 'low_contact'
                cand['verified_name'] = name
                cand['verified_address'] = address
                cand['verified_phone'] = phone
                continue
            tier, location, contact, total, grade, mtype = score_row(area, phone)
            row = {
                'priority_tier': tier,
                'area': area,
                'store_name': name or query,
                'address': address,
                'phone': phone,
                'map_link': f'https://pcmap.place.naver.com/place/{pid}/home',
                'instagram_or_site': '',
                'review_count': '',
                'rating': '',
                'store_type': '전자담배 전문점',
                'store_tone': f'{area} 네이버 지도 검증',
                'location_score': location,
                'specialty_score': '4',
                'contactability_score': contact,
                'total_score': total,
                'priority_grade': grade,
                'message_type': mtype,
                'contact_status': '미접촉',
                'last_contact_date': '',
                'notes': '자동 배치 러너: 네이버 지도 검증 완료'
            }
            rows.append(row)
            existing_names.add(normalize(row['store_name']))
            existing_addrs.add(normalize(row['address']))
            existing_phones.add(row['phone'])
            cand['status'] = 'added'
            cand['verified_name'] = row['store_name']
            cand['verified_address'] = row['address']
            cand['verified_phone'] = row['phone']
            cand['place_id'] = pid
            added += 1
            log(f"Added: {row['store_name']} / {row['phone']}")
        except Exception as e:
            cand['status'] = 'error'
            cand['error'] = str(e)
            log(f'Error on {query}: {e}')
    write_csv_rows(rows)
    save_queue(queue)
    update_progress(rows, 'csv_updated' if added else 'browser_verification', f'batch processed={processed}, added={added}')
    log(f'Batch complete: processed={processed}, added={added}')

if __name__ == '__main__':
    main()
