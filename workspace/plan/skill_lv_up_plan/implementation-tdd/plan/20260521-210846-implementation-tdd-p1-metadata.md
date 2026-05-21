# implementation-tdd P1 skill metadata 수정 계획

## 수정 이유

`agents/openai.yaml`이 `implementation-tdd`의 핵심 범위를 test lists, failing tests, Red-Green-Refactor 중심으로만 표현한다. P1 기준상 skill은 approach selection, boundary cases, state vs behavior verification, AI-assisted TDD honesty까지 포함하므로 metadata가 이 범위를 더 정확히 반영해야 한다.

## 수정 범위

- `dddjango/skills/implementation-tdd/agents/openai.yaml`
  - `short_description`을 25-64자 범위에서 더 포괄적으로 수정한다.
  - `default_prompt`에 `$implementation-tdd`를 유지하고, test list, Red-Green-Refactor, approach/edge/verification choice를 포함한다.

## 수정하지 말아야 할 범위

- `SKILL.md`와 `references/*.md`는 이미 P1 기준을 반영하므로 이번 계획에서 수정하지 않는다.
- source reference는 별도 reference 계획에서 보강했다.
- eval case, answer, evaluator는 이번 P1에서 수정하지 않는다.

## 작업 체크리스트

- [ ] `agents/openai.yaml` metadata를 갱신한다.
- [ ] source skill과 runtime cache diff를 확인한다.
- [ ] runtime cache가 달라졌으면 `runtime-sync` 분석/계획 후 동기화한다.
- [ ] subagent 리뷰 결과를 통합해 Blocker, Major, 열린 Minor가 남으면 루프를 반복한다.
- [ ] validators를 실행한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- metadata가 source skill 목적과 충돌하지 않고 중요한 TDD decision axes를 드러낸다.
- runtime cache 동기화 여부가 확인된다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
