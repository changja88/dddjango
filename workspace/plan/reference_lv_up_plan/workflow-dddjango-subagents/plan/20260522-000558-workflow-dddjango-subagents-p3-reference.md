# workflow-dddjango-subagents P3 reference 수정 계획

## 수정 이유

P3 post-fix review에서 `workspace/reference/workflow-dddjango-subagents/reference/final.md`의 eval 문제 분류 문구가 `constraint_rules.md`의 분석 첫 줄 형식과 다르게 읽힐 수 있다는 지적이 남았다. Runtime skill은 이미 prefixed form을 사용하지만, source reference가 같은 기준을 명확히 표현해야 source/runtime 판단 근거가 충돌하지 않는다.

## 수정 범위

- `workspace/reference/workflow-dddjango-subagents/reference/final.md`
  - eval 문제 분류 section의 first-line 예시를 모두 `수정 대상: ...` prefixed form으로 정리한다.

## 수정하지 말아야 할 범위

- Runtime skill의 routing, role-map, handoff, integration 규칙은 이 reference 수정에서 바꾸지 않는다.
- Eval case, answer oracle, evaluator, report, generated eval run artifacts는 수정하지 않는다.
- 다른 source reference는 수정하지 않는다.

## 체크리스트

- [x] `final.md`의 eval follow-up taxonomy가 `constraint_rules.md` 허용 형식과 일치한다.
- [x] Runtime skill과 bundled reference의 prefixed form과 충돌하지 않는다.
- [x] Plan constraint validator가 통과한다.
- [x] P3 review에서 source taxonomy Major가 닫힌다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`

## 완료 조건

- Source reference, runtime skill, bundled reference가 eval follow-up first-line 형식을 같은 방식으로 설명한다.
- Reference 수정 관련 Blocker 0, Major 0, 열린 Minor 0이다.
