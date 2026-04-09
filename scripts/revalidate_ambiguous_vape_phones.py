#!/usr/bin/env python3
import csv
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path('/Users/usuk/.openclaw/workspace')
CSV_PATH = ROOT / 'generated' / 'vape_stores_seoul_template.csv'
PROGRESS_JSON = ROOT / 'generated' / 'vape_500_progress.json'
PROGRESS_MD = ROOT / 'generated' / 'vape_500_progress.md'
SUMMARY_PATH = ROOT / 'generated' / 'vape_ambiguous_phone_revalidation_summary.json'
GENERATED_DASHBOARD = ROOT / 'generated' / 'bool_outreach_dashboard_v3.html'
ROOT_DASHBOARD_V3 = ROOT / 'bool_outreach_dashboard_v3.html'
ROOT_DASHBOARD = ROOT / 'bool_outreach_dashboard.html'
KST = timezone(timedelta(hours=9))
TODAY = datetime.now(KST).strftime('%Y-%m-%d')
NOW = datetime.now(KST).strftime('%Y-%m-%d %H:%M')

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
    ('강남역', ['강남대로66길', '강남대로84길', '강남대로 390', '강남대로 438', '역삼로 111', '서초구 강남대로']),
    ('신논현/논현', ['학동로', '논현동', '봉은사로2길', '강남대로118길', '신논현', '논현로']),
    ('역삼/선릉', ['역삼동', '테헤란로', '선릉로', '대치동', '테헤란로4길', '테헤란로70길']),
    ('삼성/코엑스', ['삼성동', '봉은사로 420', '봉은사로82길', '영동대로', '삼성로103길', '코엑스']),
    ('홍대/합정/상수', ['서교동', '동교동', '양화로', '독막로', '와우산로', '합정동', '상수', '연남', '성지1길']),
    ('신촌/이대', ['신촌로', '이화여대길', '대현동', '창천동', '연세로', '서대문구']),
    ('성수', ['성수동', '성수이로', '연무장', '서울숲', '뚝섬']),
    ('이태원', ['이태원', '한남동', '대사관로', '한강대로', '용산구']),
    ('잠실/송리단길', ['잠실', '올림픽로', '석촌', '송리단길', '풍납동', '신천동']),
    ('문정/가락', ['문정동', '법원로', '가락동', '송파대로28길', '송이로', '마천로']),
    ('여의도', ['여의도동', '의사당대로', '국회대로 780', '여의대방로']),
    ('영등포/문래', ['영등포동', '영중로', '양평로', '선유로', '대방천로', '문래', '버드나루로', '신길동']),
    ('마포/공덕', ['마포대로', '신공덕동', '상암동', '월드컵로']),
    ('건대입구', ['광진구', '자양동', '자양로', '군자동', '중곡동', '능동로', '광나루로']),
    ('왕십리/한양대', ['왕십리', '행당동', '용답동', '한양대']),
    ('천호/강동', ['천호동', '강동구', '양재대로', '천중로', '길동', '성내동', '암사동', '고덕로']),
    ('은평/연신내', ['은평구', '불광동', '연서로', '통일로', '증산로', '응암동', '대조동', '진관동']),
    ('강서/마곡', ['강서구', '마곡', '화곡동', '우장산', '양천향교', '가양동', '발산']),
    ('구로디지털단지', ['구로구', '금천구', '가산동', '개봉동', '구로동', '디지털로', '벚꽃로', '고척동', '시흥대로']),
    ('사당/방배', ['동작구', '사당동', '방배동', '남부순환로', '상도로', '흑석동']),
    ('서초/양재', ['서초구', '서초동', '효령로', '양재', '서초대로']),
    ('서울대입구/샤로수길', ['관악로', '봉천동', '낙성대', '서울대입구', '샤로수길']),
    ('신림', ['신림동', '신림로', '조원중앙로']),
    ('동대문/청량리', ['동대문구', '답십리', '장안동', '왕산로', '이문로', '청량리']),
    ('도봉/창동', ['도봉구', '창동', '쌍문동']),
    ('수유/미아', ['강북구', '수유동', '미아동', '솔샘로', '오패산로', '노해로']),
    ('성북/길음', ['성북구', '동소문로', '길음동', '성신여대']),
    ('종로/을지로/충무로', ['종로구', '중구', '삼봉로', '종로 ', '서소문로', '신당동', '충무로', '을지로', '다산로']),
    ('중랑/면목', ['중랑구', '면목동', '용마산로', '중랑역로']),
    ('목동/오목교', ['양천구', '목동', '신정동', '오목교', '신월로']),
    ('노원', ['노원구', '공릉동', '상계동', '월계동']),
    ('압구정/청담', ['압구정', '청담', '도산대로', '신사동']),
]

RECOVERIES = [
    {
        'store_name': '서브마린',
        'address': '서울 송파구 올림픽로35가길 9 잠실푸르지오월드마크 230호',
        'phone': '010-4913-1453',
        'map_query': '서브마린',
        'evidence': '네이버 지도 검색상 서울 송파구 신천동 전자담배 결과 1건으로 수렴했고, Martha/Litmus 주소가 잠실푸르지오월드마크로 합치됨',
    },
    {
        'store_name': '전자금연용품할인매장',
        'address': '서울 구로구 디지털로32나길 38 서림빌딩 1층',
        'phone': '010-9984-5336',
        'map_query': '전자담배할인매장 구로',
        'evidence': '네이버 지도 검색상 서울 구로구 구로동 전자담배 결과가 확인됐고, Martha/Litmus 모두 서림빌딩 계열 주소와 동일 번호를 공유',
    },
    {
        'store_name': '시가모아 강남점',
        'address': '서울 서초구 강남대로53길 7 강남애니타워 지하1층 B05호',
        'phone': '010-8989-2577',
        'map_query': '시가모아 강남점',
        'evidence': '네이버 지도 검색상 서울 서초구 서초동 전자담배 결과가 단일 매칭됐고, 두 소스가 같은 건물과 번호를 가리킴',
    },
    {
        'store_name': '둔촌역전자담배',
        'address': '서울 강동구 양재대로87길 19 1층',
        'phone': '010-2222-2043',
        'map_query': '둔촌역 전자담배 강동점',
        'evidence': '성내동 지번 표기와 양재대로87길 도로명 표기가 같은 매장으로 수렴하는 케이스라서 도로명 주소 기준으로 정리',
    },
    {
        'store_name': '라미야구로점(신도림)',
        'address': '서울 구로구 개봉로 45 1층',
        'phone': '010-9028-9207',
        'map_query': '라미야 구로점 신도림',
        'evidence': '개봉동 지번과 개봉로 45 도로명 표기가 동일 매장 범주로 수렴했고 두 소스가 같은 010 번호를 공유',
    },
    {
        'store_name': '하카전자담배 신당약수역',
        'address': '서울 중구 다산로 146 서광빌딩 1층',
        'phone': '010-9176-5598',
        'map_query': '하카전자담배 신당약수역',
        'evidence': '네이버 지도 검색명과 소스 상호가 일치하고, 신당동/다산로 146 서광빌딩 표기가 동일 매장으로 수렴',
    },
    {
        'store_name': '너구리굴양남사거리점',
        'address': '서울 영등포구 선유로 83 1층',
        'phone': '010-2707-2981',
        'map_query': '너구리굴 양남사거리',
        'evidence': '두 소스 모두 선유로 83과 동일 010 번호를 가리켜 양남사거리점으로 복구 가능',
    },
    {
        'store_name': '듀바코 삼성점',
        'address': '서울 강남구 삼성로103길 12 신도브래뉴주상복합 지하1층 B105-1호',
        'phone': '010-3237-4520',
        'map_query': '듀바코 삼성점',
        'evidence': '듀바코 삼성점/라미야삼성점이 같은 신도브래뉴주상복합 B105-1호와 동일 번호로 수렴해 단일 매장으로 판단',
    },
    {
        'store_name': '마곡너구리굴전자담배 본점',
        'address': '서울 강서구 마곡중앙로 161-17 보타닉파크타워1 지하1층 108호',
        'phone': '010-7543-4027',
        'map_query': '마곡너구리굴전자담배 본점',
        'evidence': 'Martha/Justfog가 동일 번호를 공유하고 네이버 지도 검색명도 본점 기준으로 수렴',
    },
    {
        'store_name': '룩전자담배점',
        'address': '서울 강남구 봉은사로 420 학산빌딩 102호',
        'phone': '010-8078-9600',
        'map_query': '룩 전자담배 삼성',
        'evidence': '네이버 지도와 Litmus가 모두 봉은사로 420 학산빌딩 계열 전자담배 매장으로 수렴해 복구 가능',
    },
]


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


def infer_area(address: str, name: str) -> str:
    blob = f'{address} {name}'
    for area, keys in AREA_RULES:
        if any(k in blob for k in keys):
            return area
    return '영등포/문래'


def score_row(area: str, phone: str):
    tier = '1' if area in PRIORITY_AREAS else '2'
    location = '5' if area in PRIORITY_AREAS else '4'
    contact = '5' if phone.startswith(('010', '0507')) else '3'
    total = str(int(location) + 4 + int(contact))
    grade = 'A' if phone.startswith(('010', '0507')) else 'B'
    message_type = '1' if area in {'강남역','신논현/논현','역삼/선릉','삼성/코엑스','홍대/합정/상수','신촌/이대','성수','잠실/송리단길'} else '2'
    return tier, location, contact, total, grade, message_type


def load_rows():
    with CSV_PATH.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_rows(rows):
    with CSV_PATH.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)


def update_progress(after_rows, added_count: int, unresolved_leftovers: int):
    filled = [r for r in after_rows if (r.get('store_name') or '').strip()]
    phone_ready = sum(1 for r in filled if (r.get('phone') or '').startswith(('010', '0507')))
    needs = sum(1 for r in filled if not (r.get('phone') or '').strip() or (r.get('phone') or '').startswith(('02', '070', '080', '1800')))
    obj = json.loads(PROGRESS_JSON.read_text()) if PROGRESS_JSON.exists() else {'project': 'seoul_vape_500', 'verification': {'proof': []}, 'currentBatch': {}}
    obj['status'] = 'running'
    obj['lastVerifiedAtKst'] = NOW
    obj['currentBatch'] = {
        'name': 'Batch 2',
        'areas': ['강남/삼성', '홍대/신촌', '성수/건대', '영등포/여의도'],
        'stage': 'ambiguous_phone_revalidated'
    }
    obj['counts'] = {'total': len(filled), 'phoneReady': phone_ready, 'needsCheck': needs}
    proof = obj.setdefault('verification', {}).setdefault('proof', [])
    proof.append(f'ambiguous phone revalidation recovered_sms_ready={added_count}, unresolved_leftovers={unresolved_leftovers}')
    obj['nextProofPoint'] = 'updated dashboard/public link refreshed with ambiguous-phone recoveries'
    PROGRESS_JSON.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

    if PROGRESS_MD.exists():
        text = PROGRESS_MD.read_text(encoding='utf-8')
        text = re.sub(r'- 총 매장 수: \d+', f'- 총 매장 수: {len(filled)}', text)
        text = re.sub(r'- 문자 가능 번호: \d+', f'- 문자 가능 번호: {phone_ready}', text)
        text = re.sub(r'- 재확인 필요: \d+', f'- 재확인 필요: {needs}', text)
        text = re.sub(r'- 최근 추가 반영: \d+건', f'- 최근 추가 반영: {added_count}건', text)
        text = re.sub(r'- 현재 단계: .*', '- 현재 단계: ambiguous_phone_revalidated', text)
        text = re.sub(r'- 마지막 검증 시각\(KST\): .*', f'- 마지막 검증 시각(KST): {NOW}', text)
        PROGRESS_MD.write_text(text, encoding='utf-8')


def regenerate_dashboards():
    subprocess.run(['python3', str(ROOT / 'scripts' / 'generate_vape_dashboard.py')], check=True)
    if GENERATED_DASHBOARD.exists():
        shutil.copyfile(GENERATED_DASHBOARD, ROOT_DASHBOARD_V3)
        shutil.copyfile(GENERATED_DASHBOARD, ROOT_DASHBOARD)


def main():
    rows = load_rows()
    filled_before = [r for r in rows if (r.get('store_name') or '').strip()]
    before_total = len(filled_before)
    before_sms = sum(1 for r in filled_before if (r.get('phone') or '').startswith(('010', '0507')))

    existing_phones = {(r.get('phone') or '').strip() for r in filled_before if (r.get('phone') or '').strip()}
    existing_addrs = {normalize_addr(r.get('address') or '') for r in filled_before if (r.get('address') or '').strip()}
    existing_names = {normalize_name(r.get('store_name') or '') for r in filled_before if (r.get('store_name') or '').strip()}

    added_rows = []
    skipped_existing = []
    for item in RECOVERIES:
        n_name = normalize_name(item['store_name'])
        n_addr = normalize_addr(item['address'])
        phone = item['phone']
        if phone in existing_phones or n_addr in existing_addrs or n_name in existing_names:
            skipped_existing.append(item['store_name'])
            continue
        area = infer_area(item['address'], item['store_name'])
        tier, location, contact, total, grade, message_type = score_row(area, phone)
        rows.append({
            'priority_tier': tier,
            'area': area,
            'store_name': item['store_name'],
            'address': item['address'],
            'phone': phone,
            'map_link': f'https://map.naver.com/p/search/{item["map_query"]}',
            'instagram_or_site': '',
            'review_count': '',
            'rating': '',
            'store_type': '전자담배 전문점',
            'store_tone': f'{area} 애매번호 재검증 복구',
            'location_score': location,
            'specialty_score': '4',
            'contactability_score': contact,
            'total_score': total,
            'priority_grade': grade,
            'message_type': message_type,
            'contact_status': '미접촉',
            'last_contact_date': '',
            'notes': f'애매번호 재검증 복구 {TODAY}. {item["evidence"]}'
        })
        existing_phones.add(phone)
        existing_addrs.add(n_addr)
        existing_names.add(n_name)
        added_rows.append(item)

    save_rows(rows)

    filled_after = [r for r in rows if (r.get('store_name') or '').strip()]
    after_total = len(filled_after)
    after_sms = sum(1 for r in filled_after if (r.get('phone') or '').startswith(('010', '0507')))
    unresolved_leftovers = max(0, 73 - len(added_rows))

    update_progress(rows, len(added_rows), unresolved_leftovers)
    regenerate_dashboards()

    summary = {
        'before_total': before_total,
        'before_sms': before_sms,
        'ambiguous_phone_candidates': 73,
        'recovered_sms_ready_count': len(added_rows),
        'after_total': after_total,
        'after_sms': after_sms,
        'unresolved_leftovers': unresolved_leftovers,
        'skipped_existing': skipped_existing,
        'recovered_store_names': [x['store_name'] for x in added_rows],
        'updated_dashboards': [str(p.relative_to(ROOT)) for p in [GENERATED_DASHBOARD, ROOT_DASHBOARD_V3, ROOT_DASHBOARD] if p.exists()],
        'lastVerifiedAtKst': NOW,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
