수정 대상: reference
원인 분류: source gap
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# implementation-test P1 Reference Analysis

## 평가 범위

- Source reference: `workspace/reference/implementation-test/reference/final.md`
- 보조 source: `workspace/reference/implementation-test/reference/internal.md`, `review.md`, `external.md`
- 평가 기준: pytest, fixtures, parametrization, assertions, test doubles, factory_boy/Faker, Hypothesis, time/HTTP mocking, testcontainers, coverage, mutation testing, BDD, flaky tests, Django Ninja TestClient, idempotency/concurrency tests

## 초기 판정

Reference는 일반 Python/pytest 테스트 작성 기준은 충분하지만 Django API 계약 테스트와 위험한 write 동작의 재시도/동시성 검증 기준이 부족하다.

| 기준 | 판정 | 근거 |
|---|---|---|
| pytest, fixtures, parametrization, assertions | 충분 | `final.md` 3-6장에 pytest 구조, fixture, conftest, marker, plugin, assertion 예제가 있음 |
| test doubles, fake/mock/stub/spy/dummy | 충분 | `final.md` 2장과 7장에 5분류, 검증 방식 우선순위, Mock/AsyncMock/seal이 있음 |
| factory_boy/Faker, Hypothesis | 충분 | `final.md` 8-9장에 property/stateful testing, factory_boy/Faker/Django factory가 있음 |
| time/HTTP mocking | 충분 | `final.md` 10-11장에 freezegun/time-machine, responses/aioresponses/HTTPretty가 있음 |
| testcontainers | 충분 | `final.md` 12장에 PostgreSQL/Redis/복수 서비스 container fixture가 있음 |
| coverage, mutation testing, BDD | 충분 | `final.md` 13장, 17장, 18장에 coverage.py, mutmut, pytest-bdd가 있음 |
| flaky tests | 충분 | `final.md` 1장, 6장, 16장에 reliability, pytest-randomly/timeout, flaky 방치 금지가 있음 |
| Django Ninja TestClient | 부족 | `final.md`와 보조 source에 Django Ninja `TestClient` 계약 테스트 기준이 없음 |
| idempotency/concurrency tests | 부족 | `final.md`에 transaction/testcontainers 일반 예시는 있으나 재시도, 중복 요청, row lock, `TransactionTestCase`/`transaction=True` 선택 기준이 없음 |

## Source gap

초기 finding: P1 기준에 명시된 Django Ninja `TestClient`, idempotency/concurrency tests를 판단하기 위한 source reference가 부족했다. 이 상태에서 skill만 보강하면 reference 문제를 skill로 덮는 것이었다.

## 외부 기준 확인

- Django Ninja 공식 testing guide는 Django test client와 별개로 router/API를 직접 테스트하는 `ninja.testing.TestClient`를 제공하며, URL resolver/middleware 계층 없이 API를 빠르게 테스트할 수 있음을 설명한다.
- pytest-django 공식 문서는 DB 접근이 기본 차단되며 `pytest.mark.django_db` 또는 `db` fixture가 필요하고, transaction 동작 검증에는 `transaction=True` 또는 `transactional_db`가 필요하다고 설명한다.
- Django 공식 testing tools 문서는 `select_for_update()`처럼 transaction 내부 실행 여부를 검증해야 하는 경우 `TransactionTestCase`가 필요하다고 설명한다.

## 보완 방향

- `final.md`에 Django Ninja `TestClient` 계약 테스트 섹션을 추가한다.
- `final.md`에 idempotency/concurrency 테스트 섹션을 추가한다.
- 참고 문헌과 설치 도구 목록에 Django Ninja/pytest-django 관련 항목을 보강한다.
- eval case나 evaluator 문제는 발견하지 못했으므로 P1에서 `eval_lv_up_plan` 후속 대상으로 분류하지 않는다.

## 재평가 결과

`final.md`에 Django Ninja `TestClient`, pytest-django DB/transaction 선택, idempotency replay, DB uniqueness, transaction/row-lock, concurrency race test guidance를 추가한 뒤 real subagent 독립 P1 audit이 source reference sufficiency를 확인했다. 남은 reference Blocker, Major, 열린 Minor는 없다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰/순차 fallback: real-subagent. 독립 P1 audit subagent가 current `final.md`의 Django Ninja `TestClient`, pytest-django DB/transaction, idempotency/concurrency, supporting citation coverage를 확인했다.
