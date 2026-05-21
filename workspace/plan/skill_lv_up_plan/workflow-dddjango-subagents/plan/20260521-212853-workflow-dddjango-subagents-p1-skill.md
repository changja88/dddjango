# workflow-dddjango-subagents P1 skill 개선 계획

## 수정 이유

새 dedicated source reference가 정한 판단 축을 runtime skill bundle에 더 명확히 반영해야 한다. 특히 critical path와 sidecar delegation, source/runtime boundary, eval 문제 후속 분류, 한글 기본 문서 원칙이 부족하다.

## 수정 범위

- `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- `dddjango/skills/workflow-dddjango-subagents/references/delegation-rules.md`
- `dddjango/skills/workflow-dddjango-subagents/references/role-map.md`
- `dddjango/skills/workflow-dddjango-subagents/references/handoff-contract.md`
- `dddjango/skills/workflow-dddjango-subagents/references/integration-checklist.md`
- `dddjango/skills/workflow-dddjango-subagents/agents/openai.yaml`

## 수정하지 말아야 할 범위

- `workspace/develop/eval/**`
- 다른 skill bundle
- runtime cache 직접 수정. Source bundle patch 후 별도 `runtime-sync` 분석/계획을 작성하고 sync한다.
- validator가 요구하는 exact phrase와 workflow role table 축소 금지

## 작업 체크리스트

- [x] `SKILL.md`를 한글 중심으로 정리하고 source reference의 routing, delegation, output honesty를 반영한다.
- [x] `delegation-rules.md`에 critical path, sidecar, advisory, shared write 기준을 반영한다.
- [x] `role-map.md`의 canonical role table이 source와 validator 요구를 모두 만족하는지 확인한다.
- [x] `handoff-contract.md`에 approval-before-execution과 ownership field 기준을 보강한다.
- [x] `integration-checklist.md`에 source/runtime boundary, eval follow-up, runtime cache sync reporting을 보강한다.
- [x] `agents/openai.yaml`이 skill 목적과 negative routing을 반영하도록 갱신한다.
- [x] patch 후 skill 반영도를 재평가하고 analysis 문서의 review 결과를 닫는다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- skill bundle이 dedicated source reference의 주요 decision을 반영한다.
- bundled references가 source reference를 runtime-facing path로 노출하지 않고 skill-local guidance로만 작동한다.
- role map의 role names, responsibility scope, related skills가 축소되지 않는다.
- `agents/openai.yaml`이 source skill 목적과 충돌하지 않는다.
- skill 재평가 결과가 Blocker 0, Major 0, 열린 Minor 0이다.

## 완료 확인

Source skill과 bundled references를 수정했고 runtime cache sync 및 validator 통과로 재평가를 완료했다.
