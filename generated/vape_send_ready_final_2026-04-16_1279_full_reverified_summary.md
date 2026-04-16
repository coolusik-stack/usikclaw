# 서울 전자담배 DB 1279 전수 재검증 보고서

**생성일**: 2026-04-16  
**입력 파일**: `vape_send_ready_final_2026-04-16_1279_trusted.csv`  
**출력 파일**: `vape_send_ready_final_2026-04-16_1279_full_reverified.csv`  
**최종 배포본**: `vape_send_ready_final_2026-04-16_1126_fully_verified.csv`

---

## 1. 전수 재검증 요약 표

| 항목 | 수치 |
|------|------|
| 총 입력 | **1,279** |
| VERIFIED_KEEP | **1,126** |
| DROP | **65** |
| NEEDS_REVIEW | **88** |
| **즉시 배포 가능 (fully verified)** | **1,126** |

---

## 2. DROP 사유 분류 (총 65건)

| 사유 | 건수 |
|------|------|
| IQOS/HNB 공식판매점 (편의점·마트 코너) | 25 |
| 동일 매장 0507 secondary (010 번호 중복 등재) | 15 |
| 비전문/비전자담배 업종 (법률, 시니어클럽, 릴버거, 복권, 스포츠베팅, 맥주창고, 핸드폰샵) | 15 |
| HNB 전용 브랜드 (플룸, GLO) | 4 |
| 일반마트 (IGA마트, 아이지에이마트) | 3 |
| 기타 (주소불명, 수리점 등) | 3 |
| **합계** | **65** |

### 대표 DROP 예시

| no | 상호명 | 사유 |
|----|--------|------|
| 134 | 아이코스공식매장 오렌지마트점 | IQOS 공식판매점 (마트 코너) |
| 654 | 수연법률사무소 | 법률사무소 (비전문) |
| 664 | 목동전자담배 (0507번호) | 동일 매장 0507 secondary |
| 696 | 릴버거 | HNB 관련 버거집 (비전문) |
| 711 | 노원시니어클럽 | 시니어클럽 (비전문) |
| 715 | IGA마트가일점 | 일반마트 |
| 728 | 플룸 폴 스튜디오 | HNB 플룸 전용 (비전담) |
| 753 | 스포츠베팅샵 | 스포츠베팅 (비전문) |
| 889 | 더플룸 | HNB 플룸 전용 |
| 980 | 더윌 변호사법률상담사무소 | 법률사무소 (비전문) |
| 1082 | 고래맥주창고 오류점 | 맥주창고 (주류업, 비전문) |
| 1049 | Bacchus Repair Shop | 수리점 (비전문) |

---

## 3. NEEDS_REVIEW 사유 분류 (총 88건)

| 사유 | 건수 |
|------|------|
| 상호명 모호 + URL/노트 없음 (오티코티, 에이플러스 등) | 27 |
| Naver 블로그 출처 + URL 없음 (전담 상호 명확) | 22 |
| 약한 출처 (daum_sweep, instagram, coord_grid 등) | 21 |
| 신뢰 출처이나 URL/노트 없음 (칠렉스, 더바코 등) | 4 |
| 고릴라파이프 (파이프+전담 복합매장, 비중 불명확) | 4 |
| 기타 | 10 |

### 대표 NEEDS_REVIEW 예시

| no | 상호명 | 사유 |
|----|--------|------|
| 36 | 압구정 전자담배 (매장문의) | Naver 블로그 출처, URL 없음 |
| 62, 429, 532 | 서초 vape샵2/3/4 | Naver 블로그, URL 없음 |
| 294, 406, 583, 801 | 고릴라파이프 각 지점 | 파이프담배 전문, 전담 비중 불명확 |
| 515 | 조쿤컴퍼니 | 상호 모호 (vape 여부 불명확) |
| 700–703 | 서울 pod system 판매점 | 약한 출처, URL 없음 |
| 1049 | Bacchus Repair Shop | 영문 상호, 수리점 추정 |

---

## 4. VERIFIED_KEEP 근거 분류

| 근거 유형 | 건수 (추정) |
|-----------|-------------|
| Naver Place pcmap URL 직접 확인 | ~383 |
| 공식 로케이터 URL (litmus, martha, endpuff 등) | ~120 |
| 공식 로케이터 출처 파일 | ~80 |
| 804 메인 baseline + 전담 상호명 | ~350 |
| KakaoMap 스윕 + 전담 상호명 | ~35 |
| 기타 신뢰 출처 + URL/노트 | ~158 |

---

## 5. 핵심 판단 3줄

1. **1279 trusted 목록에서 65건(5.1%)이 확정 DROP** — 주요 이유: 아이코스 공식판매점(25), 0507 secondary(15), 비전문업종(15)
2. **1,126건은 pcmap/공식 로케이터/804 baseline 등 1차 근거 기반으로 즉시 배포 가능** — 전수조사 기준 최종 신뢰본
3. **88건(6.9%)은 Naver 블로그 출처이거나 상호명이 모호** — 별도 스프린트로 Naver Place 직접 조회 후 최대 1,214건까지 확장 가능

---

## 6. 즉시 배포 가능 최종 카운트

> **1,126건** — `vape_send_ready_final_2026-04-16_1126_fully_verified.csv`

---

## 7. Handoff Fields

| 필드 | 내용 |
|------|------|
| **next_best_lane** | needs_review_direct_verification |
| **spawn_ready_task_brief** | NEEDS_REVIEW 88건 Naver Place API/web_fetch 직접 조회 후 재판정. naver_blog 22건 + 약한출처 21건 우선. |
| **continue_if_goal_open** | true |
| **global_count_confidence** | HIGH (1126 VERIFIED_KEEP), LOW-MEDIUM (88 NEEDS_REVIEW) |
| **known_overlap_risk** | LOW — 0507 secondary 15건 이미 제거, 1126 기준 중복 최소화 |
| **manager_state_recommendation** | 1126 = 안전한 최종본 즉시 사용. 1279 trusted 비권장(65건 DROP 포함). NEEDS_REVIEW 88건 별도 태스크 권장. |
| **action_now** | (1) 1126 fully_verified 파일 배포. (2) NEEDS_REVIEW 88건 별도 스프린트 스폰. (3) DROP 65건 영구 제외 목록 기록. |

---

## 8. 산출 파일 목록

| 파일 | 설명 |
|------|------|
| `vape_send_ready_final_2026-04-16_1279_full_reverified.csv` | 1279건 전수 재검증 결과 (verdict + reason + evidence_url) |
| `vape_send_ready_final_2026-04-16_1126_fully_verified.csv` | VERIFIED_KEEP 1126건만 추출한 최종 배포본 |
| `vape_send_ready_final_2026-04-16_1279_full_reverified_summary.json` | 상세 분류 통계 JSON |
| `vape_send_ready_final_2026-04-16_1279_full_reverified_summary.md` | 이 보고서 |
