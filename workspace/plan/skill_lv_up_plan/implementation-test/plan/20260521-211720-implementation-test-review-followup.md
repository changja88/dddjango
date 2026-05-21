# implementation-test P1 Review Follow-up Plan

## 수정 이유

Real subagent 리뷰에서 `implementation-test` skill의 progressive disclosure가 mutation testing, BDD, pytest/coverage configuration, pytest-mock, HTTP socket-level mocking, Django Ninja `TestClient` mechanics를 source reference보다 약하게 반영한다고 판정했다. P1 종료 조건은 Blocker 0, Major 0, 열린 Minor 0이므로 보완 후 재검증이 필요하다.

## 수정 범위

- `dddjango/skills/implementation-test/references/pytest-fixtures.md`
- `dddjango/skills/implementation-test/references/test-doubles.md`
- `dddjango/skills/implementation-test/references/factories-property-tests.md`
- `dddjango/skills/implementation-test/references/coverage-mutation.md`
- `dddjango/skills/implementation-test/references/django-api-concurrency.md`
- `dddjango/skills/implementation-test/agents/openai.yaml`
- `workspace/plan/reference_lv_up_plan/implementation-test/**`
- `workspace/plan/skill_lv_up_plan/implementation-test/**`
- runtime cache `implementation-test` sync after source edits

## 수정하지 말아야 할 범위

- `workspace/develop/eval/**`는 수정하지 않는다.
- 다른 skill의 source/runtime drift는 이번 P1 범위에서 임의로 수정하지 않는다.
- Source reference는 현재 충분하므로 새 source gap이 발견되지 않는 한 수정하지 않는다.
- Bundled references는 source reference 전체 복제가 아니라 runtime에 필요한 operational guidance만 보강한다.

## 작업 체크리스트

- [x] pytest config/conftest/strict marker guidance 보강
- [x] pytest-mock, HTTPretty, TestClient wording 보강
- [x] pytest-bdd mechanics 보강
- [x] coverage config, tox/nox, mutmut workflow 보강
- [x] Django Ninja TestClient concrete example 보강
- [x] `agents/openai.yaml` scope 보정
- [x] runtime cache 동기화
- [x] stale analysis/plan review result와 checklist 갱신
- [x] required validators 재실행
- [x] 최종 재평가에서 Blocker 0, Major 0, 열린 Minor 0 확인

## 검증 명령

- `diff -ru dddjango/skills/implementation-test /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Subagent review findings 중 Blocker, Major, 열린 Minor가 모두 해소됐다.
- Source skill과 runtime cache가 일치한다.
- P1 analysis/plan records가 실행한 review와 검증 상태를 정직하게 반영한다.
- Required validators가 통과한다.
