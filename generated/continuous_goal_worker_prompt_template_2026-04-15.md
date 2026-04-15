# Continuous Goal Worker Prompt Template (2026-04-15)

Use this block for long-running collection workers.

## Required fields
- Goal: <e.g. 서울 전자담배점 send-ready 1300>
- Global baseline: <number>
- Target: <number>
- Dedupe file: <path>
- Acceptance: Seoul only, 010/0507 only, strict exact-phone unique
- Checkpoint cadence: every <N> queries/candidates
- Underperform rule: if net-new <= 2, mark exhausted or recommend lane switch

## End-of-run mandatory handoff
At the end, always include:

- `next_best_lane`: one short lane name
- `spawn_ready_task_brief`: a ready-to-spawn task brief the supervisor can paste almost directly
- `continue_if_goal_open`: true or false
- `global_count_confidence`: high / medium / low
- `known_overlap_risk`: short note

## End-of-run example
- next_best_lane: blog_cafe_masked_phone_recovery
- spawn_ready_task_brief: Search Naver blog/cafe place-review posts for low-coverage districts, recover masked phone candidates, confirm via place/mobile map, additions only when 010/0507 exact phone is directly supported.
- continue_if_goal_open: true
- global_count_confidence: medium
- known_overlap_risk: 2 phones may overlap with prior naver_variant lane
