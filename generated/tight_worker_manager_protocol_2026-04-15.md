# Tight Worker Manager Protocol (2026-04-15)

## Purpose
장기 목표 작업에서 worker를 직접 믿지 않고, manager가 상태를 짧은 주기로 관리한다.

## Role split
- Main session: user communication first
- Manager: worker 상태 감시, 다음 lane 결정, handoff 정리
- Worker: 실제 수집/검증만 수행

## Manager duties
1. 항상 현재 baseline / gap / active worker 수를 알고 있어야 한다
2. worker 종료 전 handoff block 유무를 검사한다
3. handoff block이 없으면 harness failure로 기록한다
4. goal open + active worker 0 이면 즉시 failure로 판정한다
5. same turn에 next worker spawn-ready brief를 main session에 넘긴다
6. counts conflict 시 export 금지, 먼저 reconcile 한다
7. goal-state 숫자가 대화상 최신 총계와 다르면 먼저 sync 한다
8. 보고는 항상 짧게, spawn-ready 상태로 남긴다

## Manager state machine
- `running`: active worker >= 1, goal open
- `awaiting_handoff`: worker finishing, next brief expected
- `relaunch_required`: goal open + active worker 0
- `reconciling`: counts conflict / overlap risk / stale totals
- `goal_reached`: target met
- `exhausted`: all realistic lanes documented as exhausted

Manager는 상태를 보고서에 명시적으로 남긴다.

## Mandatory manager report format
- manager_state
- current_total
- target
- gap
- active_workers
- latest_lane_result
- next_best_lane
- spawn_ready_task_brief
- confidence
- overlap_risk
- action_now
## Escalation rules
- active worker 0: immediate report + relaunch
- 20m silence: watchdog report
- 2 consecutive underperform lanes: source-family switch
- stale goal_state: sync before trust
- every major lane switch should leave a fresh manager block artifact for the next wake

## Operating preference
- default active workers: 1
- only allow 2 when lanes are clearly orthogonal
- manager summaries must be short enough to send fast in chat

## Manager report template
```text
[manager]
state: <running|awaiting_handoff|relaunch_required|reconciling|goal_reached|exhausted>
current_total: <n>
target: <n>
gap: <n>
active_workers: <n>
latest_lane_result: <short>
next_best_lane: <short>
spawn_ready_task_brief: <1-3 lines>
confidence: <high|medium|low>
overlap_risk: <short>
action_now: <report|relaunch|reconcile|stop>
```

## Spawn decision rubric
- if lane was strong and still orthogonal, continue source family
- if lane underperformed twice, switch source family
- if overlap risk is high, reconcile before spawning
- if handoff is missing, patch template before next spawn
- if a worker is already running and healthy, manager action should be `continue`, not unnecessary respawn
