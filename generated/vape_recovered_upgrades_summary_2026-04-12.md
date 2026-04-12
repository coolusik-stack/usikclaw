# Vape recovery summary - 2026-04-12

## Scope
- Priority recheck of 5 unresolved non-SMS/blank Seoul vape rows
- Naver search HTML / place-context-first verification
- Conservative rule: only mark `send_ready=yes` when `010` or `0507` is tied to the same place context, not just regex hits

## Result
- Strict confirmed recoveries: **1**
- Same-address candidate needing manual place confirmation: **1**
- Still unresolved: **3**
- Strict blank/non-SMS -> send-ready conversions from this pass: **1**

## Confirmed recovery
1. `방이베이프전자담배`
   - old: `02-417-6979`
   - new: `0507-1411-6979`
   - matched place: `방이 베이프 전자담배 송파잠실점`
   - matched address in Naver structured snippet: `서울특별시 송파구 오금로11길 33 신동아타워 1층 110호`
   - evidence: Naver search HTML structured place block contained `virtualPhone=0507-1411-6979`
   - URL: <https://search.naver.com/search.naver?where=nexearch&query=%EB%B0%A9%EC%9D%B4%EB%B2%A0%EC%9D%B4%ED%94%84%EC%A0%84%EC%9E%90%EB%8B%B4%EB%B0%B0%20%EC%86%A1%ED%8C%8C%EA%B5%AC%20%EC%98%A4%EA%B8%88%EB%A1%9C11%EA%B8%B8%2033%200507>

## Candidate, not yet promoted
1. `스위든바 논현동점`
   - old: blank
   - same-address candidate already in master: `야옹이 전자담배 논현점 / 010-6259-5397`
   - address overlap: `서울 강남구 언주로 604 지1층 111호`
   - reason not promoted: same address is strong, but I did not get a direct Naver place/card confirmation tying `스위든바 논현동점` itself to that number in this pass

## Still unresolved
1. `강남역전자담배멀티샵` / `서울 강남구 역삼로 111 대세빌딩 1층` / `070-7943-9445`
   - Naver and helper-source hits mostly collapsed into other stores like `킹콩전자담배멀티샵 강남역점` at different addresses
2. `시가브로` / `서울 강남구 테헤란로 147 성지하이츠Ⅱ 제지하층 13호` / `1800-7495`
   - only representative-number style evidence found, no verified `010`/`0507`
3. `강남전자담배마샤 신논현역점` / `서울 강남구 봉은사로 106` / `02-508-1179`
   - raw `010` regex hits were false positives from unrelated blog/table fragments
   - public search context still points back to the `02-508-1179` store number only

## Output files
- CSV: `/Users/usuk/.openclaw/workspace/generated/vape_recovered_upgrades_2026-04-12.csv`
- JSON: `/Users/usuk/.openclaw/workspace/generated/vape_recovered_upgrades_summary_2026-04-12.json`
