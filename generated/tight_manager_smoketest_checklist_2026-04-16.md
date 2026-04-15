# Tight Manager Smoketest Checklist (2026-04-16)

## 목적
manager 하네스가 문서가 아니라 실제 운영 상태를 제대로 반영하는지 빠르게 점검한다.

## 체크 항목
1. activeGoal / currentAccepted / targetAccepted / gap 이 최신 대화 기준과 일치하는가
2. active worker 수가 실제와 상태 파일에 논리적으로 맞는가
3. active worker 0이면 state가 `relaunch_required` 또는 same-turn relaunch로 이어졌는가
4. 최근 worker handoff에 다음 필드가 있었는가
   - next_best_lane
   - spawn_ready_task_brief
   - continue_if_goal_open
   - global_count_confidence
   - known_overlap_risk
   - manager_state_recommendation
   - action_now
5. next lane이 source-family exhaustion 판단과 맞는가
6. 사용자 메시지 응답 리듬이 워커 결과 처리보다 우선되고 있는가

## 합격 기준
- 최신 수치 sync 완료
- active worker 상태 일치
- handoff fields 누락 없음
- next action이 immediately spawn-ready 상태
- 보고 문장이 3~8줄 내외로 짧게 유지됨
