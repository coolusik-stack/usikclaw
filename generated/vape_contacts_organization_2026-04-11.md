# Vape contacts organization snapshot (2026-04-11)

## What changed
- Merged the 701-row priority file with the 2026-04-10 audit results into one master list.
- Added action buckets so the list is operational instead of just descriptive.

## Master counts
- Total contacts: **701**
- Send now: **275**
- Review first: **145**
- Audit first: **261**
- Hold cleanup: **20**

## Wave split inside each action bucket
- Send now: Wave 1 111, Wave 2 101, Wave 3 63
- Review first: Wave 1 5, Wave 2 32, Wave 3 108
- Audit first: Wave 1 36, Wave 2 203, Wave 3 22
- Hold cleanup: HOLD 20

## Best immediate list
- Recommended first operating list: **`vape_contacts_send_now_2026-04-11.csv`**
- Safest first slice inside that file: **Wave 1 confirmed rows = 111**
- Then expand to Wave 2 confirmed rows = **101** if reply pattern looks normal.

## Top areas in send-now bucket
- 건대입구: 18
- 영등포/문래: 18
- 천호/강동: 18
- 강서/마곡: 15
- 역삼/선릉: 14
- 잠실/송리단길: 14
- 구로디지털단지: 13
- 마포/공덕: 11
- 홍대/합정/상수: 10
- 성수: 10

## Top areas that still need review/audit
### Review first
- 종로/을지로/충무로: 13
- 구로디지털단지: 11
- 역삼/선릉: 9
- 잠실/송리단길: 9
- 홍대/합정/상수: 8
- 영등포/문래: 8
- 중랑/면목: 8
- 신림: 7
- 천호/강동: 6
- 사당/방배: 6
### Audit first
- 종로/을지로/충무로: 21
- 강서/마곡: 19
- 천호/강동: 18
- 노원: 16
- 은평/연신내: 14
- 동대문/청량리: 13
- 서초/양재: 12
- 노량진/보라매: 12
- 성북/길음: 12
- 구로디지털단지: 11

## Main risk flags in review-first bucket
- draft_provenance_only: 137
- missing_map_link: 137
- cleanup:draft_only: 129
- cleanup:merged_dup_history: 13
- area_address_mismatch: 7

## Output files
- `vape_contacts_master_2026-04-11.csv`
- `vape_contacts_send_now_2026-04-11.csv`
- `vape_contacts_review_first_2026-04-11.csv`
- `vape_contacts_audit_first_2026-04-11.csv`
- `vape_contacts_hold_cleanup_2026-04-11.csv`
