수정 대상: reference

# implementation-test P1 reference 반영도 점검

## 점검 대상

- Skill: `dddjango/skills/implementation-test/SKILL.md`
- Skill reference: `dddjango/skills/implementation-test/references/*.md`
- Source reference: `workspace/reference/implementation-test/reference/final.md`
- 기준 절차: `workspace/plan/master_plan.md`의 `P1`, `C-REF`
- 제약 기준: `workspace/plan/constraint_rules.md`

## 목적

`implementation-test`는 Python/Django 테스트 구현과 리뷰에서 pytest, fixture, test double, factory, property test, API contract, concurrency, coverage, mutation, flaky test 기준을 실제 테스트 작성 규칙으로 연결하는 skill이다.

## 기준 reference

`workspace/reference/implementation-test/reference/final.md`는 pytest 기본 구조, fixture, parametrization, assertion, marker, plugin, test double, factory_boy/Faker, Hypothesis, time mocking, HTTP mocking, testcontainers, coverage.py, tox/nox, FIRST, AAA, anti-pattern, mutation testing, BDD, debugging을 포함한다.

`workspace/reference/implementation-test/reference/review.md`는 다음 상충을 이미 정리했다.

- test double은 Dummy, Stub, Spy, Mock, Fake 5분류를 기준으로 삼는다.
- 시간 모킹은 다수 모듈의 `datetime` 직접 patch보다 `freezegun` 또는 `time-machine` 같은 전용 도구를 우선한다.
- Mock은 외부 의존성과 관찰해야 하는 collaboration에 주로 쓰고 핵심 비즈니스 로직은 실제 객체로 테스트한다.
- 동일한 Act에 대한 관련 assert는 허용하되 여러 Act-Assert 블록은 분리한다.
- 구현 세부사항에 결합한 화이트박스 테스트는 설계와 테스트 기법 양쪽에서 개선 대상으로 본다.

## reference 상태

개선 필요.

일반 Python 테스트 작성 기준은 충분하지만, `implementation-test` skill의 현재 trigger와 runtime rule은 Django/Ninja 테스트까지 명시적으로 포함한다. 반면 source reference는 Django ORM, `pytest-django`, Django Ninja `TestClient`, API contract test, idempotency/concurrency test를 전용 절로 다루지 않고 일부 흩어진 언급에 머문다.

이 gap은 현재 P1에서 skill이나 eval을 바로 수정할 이유가 아니라, source reference가 먼저 Django 테스트 기준을 명확히 보강해야 하는 문제다.

## skill 반영도

현재 `SKILL.md`와 bundled reference는 source reference의 일반 테스트 기준을 대체로 잘 반영한다.

- `SKILL.md` description은 pytest, fixture, parametrization, assertion, test double, factory_boy/Faker, Hypothesis, time/HTTP mocking, testcontainers, coverage, mutation, BDD, flaky test, Django Ninja `TestClient`, idempotency/concurrency test를 trigger로 포함한다.
- `Reference Loading`은 `pytest-fixtures.md`, `test-doubles.md`, `factories-property-tests.md`, `coverage-mutation.md`를 작업별로 나누어 progressive disclosure를 지킨다.
- Runtime Rules는 작은 테스트 우선, integration/API contract test 선택, output/state verification 우선, 과도한 mock 회피, 독립적이고 반복 가능한 테스트, property test, coverage/mutation 해석, 실제 실행한 검증만 보고하는 규칙을 포함한다.
- bundled reference는 source reference의 핵심 기준을 짧게 압축하고 있으며, `SKILL.md` 본문에 상세 내용을 중복으로 넣지 않는다.

Django 전용 기준은 skill이 과하게 만든 규칙이라기보다 source reference가 아직 충분히 받쳐주지 못하는 항목으로 본다.

## 책임 경계

handoff 조건은 적절하다.

- Red-Green-Refactor, failing-test-first, TDD 코칭은 `implementation-tdd`로 넘긴다.
- domain invariant가 불명확하면 `architecture-ddd`로 넘긴다.
- DB schema, transaction, locking, rollout 가정이 불명확하면 `architecture-db`로 넘긴다.
- REST resource, status code, Problem Details, pagination, idempotency, OpenAPI 계약이 불명확하면 `architecture-api`로 넘긴다.
- Django ORM, migration, service, selector, Django Ninja 구현은 생산 코드 owner skill과 협업하고, 이 skill은 `tests/**`, `conftest.py`, factory, double을 맡는다.
- composite/risky work 또는 subagent 요청은 `workflow-dddjango-subagents`로 넘긴다.

현재 P1에서 책임 경계 수정 후보는 없다.

## eval 점검 필요 여부

현재 P1 결론에서는 eval bucket을 확정하지 않는다.

source reference의 Django 테스트 기준을 보강한 뒤 P4에서 개별 skill 평가가 Django API/ORM/concurrency 테스트 기준을 검증하는지 확인해야 한다. 그 전에는 eval 개선 후보를 `case`, `answer`, `evaluator` 중 하나로 확정하기 이르다.

## 후속 분석 문서 위치

`workspace/plan/reference_lv_up_plan/implementation-test/analysis/20260521-183817-implementation-test-p1-reference.md`

## 다음 단계

reference 개선 계획.

다음 단계에서는 `workspace/plan/reference_lv_up_plan/implementation-test/plan/` 아래에 같은 timestamp 또는 이 분석 문서를 명시적으로 연결한 계획 문서를 작성하고, Django 테스트 기준 보강 범위를 정한다.

후속 계획에서 다룰 최소 후보는 다음과 같다.

- `pytest-django` 기본 설정, `django_db` 사용 기준, transaction DB test 선택 기준
- Django ORM/service/selector 테스트에서 unit, integration, DB constraint test 선택 기준
- Django Ninja `TestClient`와 API contract test 기준
- Problem Details, auth/permission, pagination/filtering response assertion 기준
- idempotency, uniqueness, transaction/locking, concurrency test 기준
- database cleanup, factory scope, time/random/network isolation 기준

## 리뷰 방식

리뷰 방식: real-subagent

## 리뷰 결과

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

독립 subagent의 최초 리뷰는 `reference gap`을 Major 1로 보고했다. 통합 판단에서는 이 항목을 P1 종료를 막는 열린 Major가 아니라, 수정 대상 후보 `reference`와 다음 단계 `reference 개선 계획`으로 확정해 이 분석 문서에 기록했다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰 실행됨.

- 역할: `skill-creator` 관점 독립 리뷰
- 파일 수정 여부: 없음
- 주요 결론: 목적 명확성, trigger description, progressive disclosure, validation integrity는 수용 가능하다. Django/pytest-django/Django Ninja 테스트 기준은 source reference 보강이 필요하다.

## skill-creator 리뷰

실행됨.

검토 기준은 `/Users/hyun/.codex/skills/.system/skill-creator/SKILL.md`의 skill 목적 명확성, trigger description, progressive disclosure, reference 중복/누락, validation integrity를 사용했다.

- 목적 명확성: 충분
- trigger description: 충분
- progressive disclosure: 충분
- reference 중복: 문제 없음
- reference 누락: Django 테스트 기준의 source reference depth 부족
- validation integrity: 실제 실행하지 않은 테스트, 검증, subagent 작업을 수행했다고 쓰지 말라는 runtime rule이 있어 충분

## 통합 리뷰 결과

Blocker 없음.

Major 없음. 독립 리뷰의 Major 1은 reference 개선 후보로 분류되어 후속 분석 문서에 기록됐다.

열린 Minor 없음. P1 밖에서 처리할 내용은 `다음 단계`의 reference 개선 계획 후보로 내렸다.

수정 대상 후보는 `reference`다. `skill`, `runtime-sync`, `eval`은 현재 P1에서 직접 수정 대상으로 확정하지 않는다.

## 종료 조건 충족 여부

충족.

- 기준 reference 상태: `개선 필요`
- 수정 대상 후보: `reference`
- Blocker: 0
- Major: 0
- 열린 Minor: 0
- Subagent 리뷰: 실행됨
- skill-creator 리뷰: 실행됨
- 다음 단계: `reference 개선 계획`
- 후속 분석 문서: 작성됨
- 개선 계획 문서: P1에서 작성하지 않음
- 미실행 검증, 리뷰, subagent 작업을 수행한 것처럼 기록하지 않음

## 검증/미검증

검증:

- source reference와 skill/runtime reference를 파일 기준으로 대조했다.
- workspace source skill과 runtime cache skill의 `implementation-test` 파일 diff가 없음을 확인했다.
- real subagent 결과를 `wait_agent`로 수집했다.

미검증:

- P1 범위가 아니므로 skill, reference, eval 파일은 수정하지 않았다.
- P1 범위가 아니므로 eval runner와 pytest suite는 실행하지 않았다.
