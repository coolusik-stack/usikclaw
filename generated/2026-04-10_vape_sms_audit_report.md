# Seoul vape SMS-ready contact audit (2026-04-10_vape_sms_audit)

- Dataset: `vape_sms_priority_ranked.csv`
- SMS-ready rows confirmed: **424**
- Confirmed high confidence: **259**
- Review needed: **165**
- Excluded: **0**
- Strongest caveat: **Without actual outbound SMS or live call verification, 100% live reachability cannot be proven.**

## Core findings
- `sms_ready=yes` rows in ranked file: **424 / 424**
- Duplicate phones: **0 groups / 0 rows**
- Duplicate store+address rows: **0 groups / 0 rows**
- Phone type mix: **010=355**, **0507=69**, **other=0**
- Source provenance: official_locator=105, linked_source=165, web_search_draft=154
- Area/address mismatches flagged: **7**

## Review drivers
- draft_provenance_only: 154
- missing_map_link: 154
- cleanup:draft_only: 129
- cleanup:merged_dup_history: 16
- cleanup:manual_review: 12
- cleanup:address_check: 9
- area_address_mismatch: 7
- cleanup:phone_check: 5
- cleanup:identity_risk: 3

## Area/address mismatch rows
- row 37: 요가파이어 | 성수 | 서울 마포구 성암로 215 1층 전자담배
- row 177: 벨베이프 이대 | 종로/을지로/충무로 | 서울 서대문구 이화여대길 29 1층
- row 235: 일원전자담배 | 천호/강동 | 서울 강남구 양재대로31길 5, 1층 (일원동)
- row 267: 카리 전자담배 무악동 | 신촌/이대 | 서울 종로구 통일로 230 (무악동) 경희궁롯데캐슬 상가 111호
- row 285: 보라매전자담배 | 영등포/문래 | 서울 동작구 신길동 보라매 인근
- row 295: 에어베이프 연희동 | 종로/을지로/충무로 | 서울 서대문구 연희로 114 1층
- row 296: 전자담배 충정로 | 종로/을지로/충무로 | 서울 서대문구 충정로 73 1층

## Review sample (first 20 rows)
- row 37: 요가파이어 | 010-2208-1078 | area_address_mismatch
- row 74: 베이프랩 성수점 | 010-7739-2839 | cleanup:merged_dup_history
- row 77: 몬스터즈베이프 홍대 | 010-9725-5262 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 78: 스타브론즈 홍대 | 010-6528-7501 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 79: 홍대전자담배 | 010-5160-0986 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 120: 삼성역전자담배 | 010-2816-5801 | cleanup:merged_dup_history
- row 121: 삼성전자담배 삼성동점 | 010-3239-0208 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 122: 도깨비전자담배 강남구청점 | 010-5149-8765 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 123: 야옹이 전자담배 논현점 | 010-6259-5397 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 124: 지포앤퍼프 논현 | 010-9166-5953 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 125: 강남전자담배프라자 대치점 | 010-6229-6662 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 126: 강남핫딜전자담배 | 010-6237-4242 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 127: 베리베리 역삼 | 010-8931-0753 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 128: 비원베이프 | 010-8222-8333 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 129: 역삼전자담배 | 010-6659-9800 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 130: 홀릭전자담배 선릉점 | 010-3337-9457 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 131: 카우베이프 논현 | 010-2581-3799 | cleanup:merged_dup_history|draft_provenance_only|missing_map_link
- row 140: vaping lounge | 010-4806-6928 | cleanup:draft_only|draft_provenance_only|missing_map_link
- row 141: 엔드퍼프/마샤 베이프 여의도 | 010-3544-3028 | cleanup:merged_dup_history
- row 151: 마포전자담배 망원점 | 010-9024-2960 | cleanup:draft_only|draft_provenance_only|missing_map_link

## Output files
- `2026-04-10_vape_sms_audit_all_rows.csv`
- `2026-04-10_vape_sms_audit_confirmed_high_confidence.csv`
- `2026-04-10_vape_sms_audit_review_needed.csv`
- `2026-04-10_vape_sms_audit_excluded_if_any.csv`
- `2026-04-10_vape_sms_audit_summary.json`
- `2026-04-10_vape_sms_audit_report.md`
