# workflow-dddjango-subagents P1 reference 개선 계획

## 수정 이유

`workflow-dddjango-subagents`의 dedicated source reference가 없어 runtime skill과 bundled reference가 어떤 source decision을 반영하는지 검증할 수 없다. P1 종료 조건을 만족하려면 reference가 먼저 충분해야 하며, reference 문제가 있는데 skill만 수정해서 덮을 수 없다.

## 수정 범위

- 생성: `workspace/reference/workflow-dddjango-subagents/reference/final.md`
- 작성: workflow 적용 기준, canonical roles, delegation authorization, sequential fallback, handoff, ownership, integration checklist, risky write consistency, runtime sync, review/validation 기준
- 반영하지 않음: eval case, answer oracle, evaluator, run artifact

## 수정하지 말아야 할 범위

- `workspace/develop/eval/**` 직접 수정
- runtime skill wording 변경
- 다른 skill의 source reference 변경
- 기존 사용자 변경 되돌리기

## 작업 체크리스트

- [x] reference gap을 analysis 문서로 기록한다.
- [x] 같은 timestamp 파일명으로 reference 계획을 작성한다.
- [x] `workspace/reference/workflow-dddjango-subagents/reference/final.md`를 작성한다.
- [x] 작성한 source decision이 P1 판단 축을 모두 포함하는지 재평가한다.
- [x] reference가 충분해진 뒤 skill 반영도와 runtime sync를 별도 분석한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- dedicated source reference가 존재한다.
- source reference가 composite/risky 판단, role decomposition, subagent authorization, critical path vs sidecar, handoff, ownership, integration, sequential fallback, runtime sync를 판단할 수 있다.
- eval 문제가 발견되면 P1에서 직접 수정하지 않고 `workspace/plan/eval_lv_up_plan/<bucket>/analysis/` 후속 대상으로 분류한다는 기준이 들어 있다.
- 이후 skill 반영도 분석의 source basis로 사용할 수 있다.

## 완료 확인

Reference 작성과 재평가가 완료됐다. 이후 skill 반영 분석과 runtime-sync 분석을 별도 문서로 수행했다.
