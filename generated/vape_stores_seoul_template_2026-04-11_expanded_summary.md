# Seoul vape template expansion summary (2026-04-11)

- Baseline: `generated/vape_stores_seoul_template.csv`
- Output: `generated/vape_stores_seoul_template_2026-04-11_expanded.csv`

## Counts
- Baseline total rows: **740**
- Baseline filled store rows: **706**
- Baseline SMS-ready rows (010/0507): **701**
- Final total rows: **740**
- Final filled store rows: **707**
- Final SMS-ready rows (010/0507): **704**
- Final non-SMS rows kept: **3**
- Final blank-phone filled rows: **0**

## Conservative additions
1. `예스` | 서울역/용산 | 010-6297-5622 | 마샤 베이프 공식 로케이터
2. `강남핫딜` | 역삼/선릉 | 010-2648-2864 | 마샤 베이프 공식 로케이터
3. `아메리퀴드여의도` | 여의도 | 010-4557-4742 | 마샤 베이프 공식 로케이터

## Upgrade retained
- `방이베이프전자담배` 02-417-6979 후보는 동일 주소 공식 로케이터 `라미야 방이점` 010-9624-3989로 업그레이드

## Non-SMS revalidation kept as-is
- 강남역전자담배멀티샵 | 070-7943-9445 | 010/0507 미확인
- 시가브로 | 1800-7495 | 010/0507 미확인
- 강남전자담배마샤 신논현역점 | 02-508-1179 | 직통 02만 재확인

## Notes
- 신규/교체는 모두 기존 템플릿과 exact phone/address 중복이 없는 값만 사용
- 보수적으로, 상호 또는 번호가 애매한 후보는 제외
- 기존 파일 내부의 광범위한 near-duplicate 전체 정리는 이번 작업 범위에서 미완료이며, exact/obsolete 수준만 정리
