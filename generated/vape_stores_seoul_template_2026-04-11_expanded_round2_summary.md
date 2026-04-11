# Seoul vape outreach send-ready summary (2026-04-11)

- Baseline: `generated/vape_stores_seoul_template_2026-04-11_expanded.csv`
- Expanded round2: `generated/vape_stores_seoul_template_2026-04-11_expanded_round2.csv`
- Send-ready: `generated/vape_send_ready_final_2026-04-11.csv`
- Excluded non-SMS: `generated/vape_send_excluded_non_sms_2026-04-11.csv`
- New target-area additions only: `generated/vape_new_additions_target_areas_2026-04-11.csv`

## Counts
- Baseline filled store rows: **707**
- Baseline SMS-ready rows (010/0507): **704**
- Final filled store rows: **708**
- Final SMS-ready rows (010/0507): **705**
- Final send-ready unique rows: **705**
- Final non-SMS rows kept separate: **3**

## Excluded 3 non-SMS rows
- 강남역전자담배멀티샵 | 070-7943-9445 | 서울 강남구 역삼로 111 대세빌딩 1층
- 시가브로 | 1800-7495 | 서울 강남구 테헤란로 147 성지하이츠Ⅱ 제지하층 13호
- 강남전자담배마샤 신논현역점 | 02-508-1179 | 서울 강남구 봉은사로 106

## 4 target-area conservative expansion
- 이태원 | 더바코 이태원점 | 0507-1422-0951 | 서울 용산구 이태원로 165-1 뉴월드프라자 1층 | source: https://thebacco.co.kr/itaewon_lounge

## Target area stats
- 홍대/합정/상수: before 18 SMS-ready -> after 18 (+0)
- 성수: before 13 SMS-ready -> after 13 (+0)
- 왕십리/한양대: before 12 SMS-ready -> after 12 (+0)
- 이태원: before 12 SMS-ready -> after 13 (+1)

## Notes
- send-ready CSV는 010/0507만 포함, 빈 상호/빈 행 제거, 전화번호 기준 dedupe 적용
- exact same (store_name, address, phone) 중복도 제거 대상으로 처리
- 추가 확보는 공개 페이지에서 번호와 서울 주소가 함께 확인된 경우만 반영
