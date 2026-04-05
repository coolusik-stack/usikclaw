# HEARTBEAT.md

## 매 heartbeat 실행 순서

### 1. 모니터링 스크립트 실행
```
python3 scripts/heartbeat_monitor.py
```
결과를 확인해서:
- `alerts`에 `urgent: true` 항목 있으면 → 텔레그램으로 즉시 알림
- `alerts`에 항목 있지만 urgent 아니면 → 오늘 일정 간단히 메모만
- 환율 USD/KRW 1,400 이하 또는 1,550 이상이면 → 알림

### 2. 비즈니스 모니터링 (하루 1회, 마지막 체크 후 8시간 경과 시)
`memory/heartbeat-state.json`의 `boolMonitor` 기준으로 8시간 지났으면:
- **BOOL 니코틴 파우치** 관련 국내 뉴스 검색
- **더바코 Thebacco** 관련 소식 검색
- 새 소식 있을 때만 보고 (없으면 스킵)

### 3. 뉴스 브리핑 보조 (아침 08:30~09:00 사이 heartbeat에서만)
- AI/테크 주요 뉴스 1~2개 검색
- 경제 지표 변동 있으면 포함
- 9시 브리핑 직전에 합산해서 전달

---

## 알림 기준 요약

| 조건 | 행동 |
|--|--|
| 2시간 내 중요 일정 | 즉시 알림 |
| USD/KRW 1,400 미만 또는 1,550 초과 | 알림 |
| BOOL/Thebacco 유의미한 뉴스 | 알림 |
| 아무것도 없으면 | HEARTBEAT_OK |
