# Seoul vape SMS outreach prioritization

## Snapshot
- SMS-ready contacts: **631**
- Wave 1 send-now: **147**
- Wave 2 next: **304**
- Wave 3 long-tail: **160**
- Hold for cleanup: **20**
- Source mix: official locator 110, linked source 367, web-search draft 154

## Main recommendation
- Start with **Wave 1 (116 contacts)**, led by 역삼/선릉, 성수, 홍대/합정/상수, 잠실/송리단길, 영등포/문래, 건대입구.
- Keep the first operational pass to **4 batches of 25-30** by cluster, not one giant blast. This keeps reply handling and template tuning manageable.
- Push **Wave 2 (132 contacts)** only after Wave 1 reply/no-reply patterns are clear.
- Do not send the **20 HOLD rows** before cleanup, they contain phone/address/manual-review risk.

## Recommended send order
1. **Batch 1, 코어 오피스/상업권, 25-30 rows**: 강남역, 신논현/논현, 역삼/선릉, 삼성/코엑스, 압구정/청담, 여의도 중 Wave 1 상위 순번.
2. **Batch 2, 트렌드/대학가, 25-30 rows**: 성수, 홍대/합정/상수, 신촌/이대, 건대입구, 이태원, 왕십리/한양대 중 Wave 1.
3. **Batch 3, 혼합 고회전 상권, 25-30 rows**: 잠실/송리단길, 영등포/문래, 마포/공덕, 종로/을지로/충무로, 구로디지털단지 중 Wave 1.
4. **Batch 4, Wave 1 remainder, 20-31 rows**: Wave 1 잔여분 + 점수 15점대 상위 연락처 정리 발송.
5. **Batch 5-8**: Wave 2를 같은 클러스터 순서로 반복.
6. **Batch 9-12**: Wave 3는 회수율이 낮을 가능성이 있어 소규모 테스트 후 확대.

## Top priority segments
| Segment area | SMS-ready | Wave 1 | Avg send score |
| --- | ---: | ---: | ---: |
| 잠실/송리단길 | 32 | 21 | 15.70 |
| 건대입구 | 25 | 17 | 15.72 |
| 영등포/문래 | 27 | 14 | 14.96 |
| 역삼/선릉 | 25 | 13 | 15.67 |
| 성수 | 13 | 12 | 16.39 |
| 홍대/합정/상수 | 18 | 12 | 15.48 |
| 마포/공덕 | 16 | 11 | 15.64 |
| 여의도 | 9 | 7 | 16.28 |
| 삼성/코엑스 | 9 | 7 | 16.04 |
| 신논현/논현 | 12 | 7 | 15.82 |
| 이태원 | 11 | 7 | 15.33 |
| 왕십리/한양대 | 12 | 7 | 15.28 |

## Batching logic
- Cluster mix: 코어 오피스/상업권 76, 트렌드/대학가 97, 혼합 고회전 상권 144, 확장/생활상권 314
- Keep each batch internally similar by area cluster first, then send_score order second.
- Within each batch, prioritize `message_type=1` and higher `total_score` rows first.
- If replies spike in one cluster, pause the next batch in that same cluster and adapt the message, instead of contaminating the whole list.

## Cleanup flags to clear before send
| Flag | Count | Meaning |
| --- | ---: | --- |
| draft_only | 129 | 링크 근거 없이 웹검색 초안만 존재 |
| merged_dup_history | 16 | 과거 중복 병합 이력, 최종 상호 확인 권장 |
| manual_review | 12 | 상호/지점 식별 재검토 |
| address_check | 9 | 주소 다시 확인 후 발송 |
| phone_check | 5 | 번호 노이즈 가능성 있음 |
| identity_risk | 3 | 대표번호/스마트콜/타지점 혼선 가능성 |

## Output files
- `generated/vape_sms_priority_ranked.csv`
- `generated/vape_sms_priority_wave1.csv`
- `generated/vape_sms_priority_wave2.csv`
- `generated/vape_sms_priority_wave3.csv`
- `generated/vape_sms_priority_hold_cleanup.csv`
- `generated/vape_sms_priority_report.html`

## First 15 recommended sends
| Order | Area | Store | Phone | Score | Why |
| ---: | --- | --- | --- | ---: | --- |
| 1 | 강남역 | 증기샵 | 010-4922-9212 | 17.30 | score 17.3, tier1 area, message_type1, official source |
| 2 | 신논현/논현 | 킹콩전자담배강남점 | 010-3208-5522 | 17.30 | score 17.3, tier1 area, message_type1, official source |
| 3 | 역삼/선릉 | 강남 스타베이프 | 010-4052-2004 | 17.30 | score 17.3, tier1 area, message_type1, official source |
| 4 | 역삼/선릉 | 더킹전자담배 | 010-3880-9896 | 17.30 | score 17.3, tier1 area, message_type1, official source |
| 5 | 역삼/선릉 | 라미야수서점 | 010-2753-0134 | 17.30 | score 17.3, tier1 area, message_type1, official source |
| 6 | 역삼/선릉 | 킹콩전자담배 | 010-7131-2019 | 17.30 | score 17.3, tier1 area, message_type1, official source |
| 7 | 여의도 | 킹스베이프 | 010-2292-9696 | 16.90 | score 16.9, tier1 area, official source |
| 8 | 여의도 | 하카국회점 | 010-9907-3028 | 16.90 | score 16.9, tier1 area, official source |
| 9 | 강남역 | 시가모아 강남점 | 010-8989-2577 | 16.80 | score 16.8, tier1 area, message_type1, linked source |
| 10 | 강남역 | 에어릭스전자담배 강남역점 | 0507-1418-1549 | 16.80 | score 16.8, tier1 area, message_type1, linked source |
| 11 | 강남역 | 저스트포그 강남본점 | 010-4007-9783 | 16.80 | score 16.8, tier1 area, message_type1, linked source |
| 12 | 강남역 | 하카 강남역직영점 | 0507-1372-2161 | 16.80 | score 16.8, tier1 area, message_type1, linked source |
| 13 | 삼성/코엑스 | 듀바코 삼성점 | 010-3237-4520 | 16.80 | score 16.8, tier1 area, message_type1, linked source |
| 14 | 삼성/코엑스 | 룩전자담배점 | 010-8078-9600 | 16.80 | score 16.8, tier1 area, message_type1, linked source |
| 15 | 삼성/코엑스 | 위베이프 도깨비전자 삼성점 | 0507-1376-9876 | 16.80 | score 16.8, tier1 area, message_type1, linked source |
