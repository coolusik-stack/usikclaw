# Open Goal Enforcement (2026-04-15)

## Root cause confirmed
1. Workers are mostly one-shot runs.
2. Channel cannot hold a true thread-bound persistent supervisor session.
3. Completion-event relay existed, but idle gaps outside immediate relay handling were not treated as hard failures.
4. Result: goal remained open while active workers dropped to 0.

## Hard enforcement rules
- If goal is open and active workers == 0, that is FAILURE, not idle.
- On any worker completion event, do two things in the same turn:
  1. report result
  2. relaunch next worker(s) if goal is still open and active workers == 0
- Keep 1-2 workers active only.
- Prefer smaller batches over long runs.
- If a lane is exhausted, mark exhausted and switch immediately.

## Relay chain
worker done -> report -> check active workers -> if 0 and goal open -> relaunch immediately

## Stop condition
Only stop when one of these is true:
- target reached
- user explicitly pauses/stops
- all candidate lanes truly exhausted and documented

## Current application
- Applies to vape 900/1000 collection immediately.
- Same rule should be reused for any long-running goal work.
