# Continuous Goal Harness for Vape 1300 (2026-04-15)

## Purpose
1300 목표가 열린 동안 워커가 끊기지 않게 유지하는 감독용 하네스 메모.

## Main-session priority
1. 사용자 직접 메시지 즉답
2. 짧은 현재 상태 보고
3. 그 다음 워커 relaunch / lane switch

## Hard rules
- open goal + active worker 0 = failure
- worker completion event = relay trigger
- same turn action: result report -> active check -> relaunch if needed
- pre-handoff is preferred over post-completion recovery
- every worker must end with a spawn-ready recommendation block
- default active worker count: 1
- only raise to 2 when throughput gain is clear

## Worker prompt minimum fields
- baseline
- target
- exact dedupe file
- accepted phone rules (010/0507)
- Seoul-only rule
- checkpoint cadence
- exhausted criteria
- expected net-new target
- next_best_lane
- spawn_ready_task_brief
- continue_if_goal_open

## Lane order for 1300
1. m.map.naver.com/search2 driven low-coverage sweep
2. Naver variant family v4
3. embedded TownConnect recovery v2
4. blog/cafe masked-phone recovery
5. new directory discovery

## Fast-response operating discipline
- If user asks status, answer first in 1-3 lines
- Never delay a direct user reply to finish worker summaries
- If multiple worker events arrive, summarize only the latest net effect unless a conflict exists
- If there is no major change, still send a short heartbeat-style update every ~20 minutes during active goal runs

## Failure recovery
- If worker fails or vanishes, relaunch within the same turn
- If two consecutive lanes underperform, switch source family instead of retrying blindly
- If counts conflict, freeze export and reconcile before reporting a final file
- If a worker finishes without handoff fields, treat that as harness-quality failure and patch the next worker prompt
- If no worker event arrives for too long, do not assume progress. Run a silence check and report the gap.

## Silence watchdog
- If an open goal has no active worker, report failure immediately and relaunch.
- If an open goal has no worker event for ~20 minutes, send a short status check update even without a completion event.
- If goal-state numbers lag behind confirmed conversation totals, sync the state file before trusting it.
- Treat `active worker 0 + stale goal_state + no user update` as a supervisor failure, not a normal pause.
