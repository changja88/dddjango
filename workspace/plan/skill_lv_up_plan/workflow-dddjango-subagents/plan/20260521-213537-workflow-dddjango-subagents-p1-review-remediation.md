# workflow-dddjango-subagents P1 review remediation 계획

## 수정 이유

독립 리뷰에서 runtime skill 반영도와 evidence trail에 남은 Major/Minor가 확인됐다. P1 종료 조건인 Blocker 0, Major 0, 열린 Minor 0을 만족하려면 runtime guidance와 분석 문서 상태를 갱신해야 한다.

## 수정 범위

- `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- `dddjango/skills/workflow-dddjango-subagents/references/integration-checklist.md`
- runtime cache의 같은 파일
- 기존 P1 analysis/plan 문서의 stale review result와 checklist 상태

## 수정하지 말아야 할 범위

- eval pack 직접 수정
- source reference decision 변경
- 다른 skill bundle
- subagent 리뷰 결과를 실행하지 않은 것처럼 다시 쓰거나 과장하기

## 작업 체크리스트

- [x] runtime guidance에 eval follow-up 위치와 허용 `수정 대상:` label을 추가한다.
- [x] validation honesty에 eval과 Serena 실행 claim 정직성을 추가한다.
- [x] runtime-sync guidance에 analysis/plan 위치와 same timestamp pair requirement를 추가한다.
- [x] source skill 수정 후 runtime cache를 sync한다.
- [x] stale analysis/plan 문서를 최종 evidence에 맞게 갱신한다.
- [x] validators와 source/cache diff를 재실행한다.
- [x] final review result를 Blocker 0, Major 0, 열린 Minor 0으로 재평가한다.

## 검증 명령

- `diff -rq dddjango/skills/workflow-dddjango-subagents /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- 독립 리뷰의 Major와 열린 Minor가 모두 닫힌다.
- Runtime skill과 bundled references가 source decision의 eval follow-up, validation honesty, runtime-sync 절차를 충분히 반영한다.
- Source/cache parity가 실제 diff evidence로 확인된다.
- Analysis 문서들이 더 이상 stale open findings를 최종 상태처럼 남기지 않는다.

## 완료 확인

Review remediation을 반영했고 runtime cache를 sync했다. Required validators와 source/cache diff evidence로 완료 조건을 확인했다.
