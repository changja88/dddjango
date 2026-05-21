수정 대상: skill
원인 분류: subagent-review-gap
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# implementation-test P1 Review Follow-up Analysis

## 평가 입력

- skill-creator 관점 subagent 리뷰: `019e4a74-4505-7a12-8612-87f9305f93e1`
- 독립 P1 audit subagent 리뷰: `019e4a74-463b-7413-a68f-6c1080354756`
- 현재 검증 명령: `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 채택한 finding

| 등급 | 항목 | 판단 |
|---|---|---|
| Major | mutation testing bundled reference가 source의 mutmut commands/result interpretation을 충분히 반영하지 않음 | 채택 |
| Major | pytest-bdd bundled reference가 source의 feature/scenario/step fixture mechanics를 충분히 반영하지 않음 | 채택 |
| Major | pytest/coverage/tox/nox config mechanics가 bundled reference에 부족함 | 채택 |
| Minor | `agents/openai.yaml` short description이 skill scope를 좁게 보임 | 채택 |
| Minor | `pytest-mock`/`mocker` guidance 누락 | 채택 |
| Minor | HTTPretty source option이 generic socket-level interceptor로만 표현됨 | 채택 |
| Minor | Django Ninja TestClient bundled reference가 concrete import/client construction 예제를 제공하지 않음 | 채택 |
| Minor | `test-doubles.md`의 “Django Ninja skill” wording이 이 skill의 test ownership과 충돌 가능 | 채택 |
| Major | P1 closure records가 stale/open 상태 | 채택 |
| Major | global validation command failure | 현재 로컬 재실행에서는 통과하므로 stale finding으로 분류. 최종 검증에서 재확인 필요 |

## 수정 필요성

Source reference는 충분하지만 runtime bundled references가 일부 named trigger topic을 너무 압축한다. `implementation-test` skill은 concrete test implementation skill이므로, mutation, BDD, pytest configuration, coverage/multi-environment, pytest-mock, HTTP socket-level mocking, Django Ninja TestClient mechanics를 최소 operational guidance 수준으로 보강해야 한다.

## 수정 방향

- `pytest-fixtures.md`: pyproject pytest 설정, conftest hook, strict marker/warning/xfail guidance 보강
- `test-doubles.md`: pytest-mock/mocker와 HTTPretty, Django Ninja TestClient wording 수정
- `factories-property-tests.md`: pytest-bdd feature/scenario/step fixture mechanics 보강
- `coverage-mutation.md`: coverage config, tox/nox, mutmut commands/result interpretation 보강
- `django-api-concurrency.md`: TestClient import/client construction 예제 추가
- `agents/openai.yaml`: short description을 더 넓은 scope로 수정
- 이전 analysis/plan 문서의 review/result/checklist 상태를 현재 루프 결과와 검증 상태에 맞게 갱신

## 재평가 결과

Follow-up 수정 후 bundled references는 mutation workflow, pytest-bdd mechanics, pytest/coverage/tox/nox config, pytest-mock, HTTPretty, Django Ninja `TestClient` concrete shape를 반영한다. Runtime cache는 source skill과 일치하며, required validators가 모두 통과했다. Subagent findings 중 남은 Blocker, Major, 열린 Minor는 없다.

## skill-creator 리뷰

Real subagent 리뷰를 실행했다. Main 판단은 subagent의 selective omission 지적을 채택한다. 다만 skill은 source reference 전체를 복제할 필요는 없으므로 source의 긴 예제 전체가 아니라 작업에 필요한 operational checklist와 짧은 examples만 bundled references에 반영한다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰/순차 fallback: real-subagent. 두 subagent 모두 Blocker 0을 보고했다. 열린 Major/Minor는 이 follow-up loop에서 수정 대상으로 둔다.
