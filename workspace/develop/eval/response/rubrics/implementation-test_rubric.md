# implementation-test Rubric

## Skill Scope

`implementation-test`는 Python/Django 테스트 코드를 작성하고 품질을 평가하는 스킬이다. 평가 대상은 pytest tests, fixtures, parametrization, marks, test doubles, fakes/mocks/stubs/spies, factories, time/HTTP mocking, Django integration tests, Django Ninja `TestClient`, property-based tests, coverage, mutation testing, flaky test fixes, and test quality review.

책임 경계:

- Red-Green-Refactor 방법론과 테스트 우선 진행 방식은 `implementation-tdd`가 담당한다.
- 도메인 규칙 자체의 설계는 `architecture-ddd`가 담당하지만 테스트는 그 규칙과 invariant를 검증한다.
- Django/API/DB implementation ownership은 해당 implementation/architecture skill에 있다.
- Mock을 모든 협력에 기본 적용하지 않는다.
- 실행하지 않은 테스트나 coverage/mutation 결과를 완료했다고 말하지 않는다.

## Source Status

ready

Canonical sources:

- `workspace/docs/spec.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/validation-plan.md`
- `workspace/docs/reference-index.md`
- `workspace/reference/implementation-test/reference/final.md`

## Trigger Examples

- "pytest로 주문 도메인 invariant 테스트를 작성해줘."
- "Django Ninja API contract test를 `TestClient`로 추가해줘."
- "fixture, factory_boy, freezegun/time-machine을 사용해 테스트 데이터를 정리해줘."
- "외부 결제 API를 fake/mock 중 무엇으로 테스트할지 판단해줘."
- "flaky test 원인을 찾고 안정화해줘."
- "coverage 또는 mutation testing 기준을 제안해줘."
- "경계값 테스트랑 fixture를 보기 좋게 정리해줘."
- "중복 요청이 한 번만 처리되는지 Django DB까지 붙여서 검증해줘."

## Anti-Trigger Examples

- "쿠폰 정책을 TDD로 구현해줘." -> `implementation-tdd` first, then this skill for pytest mechanics
- "주문 aggregate와 invariant를 설계해줘." -> `architecture-ddd`
- "Django migration을 구현해줘." -> `implementation-django`
- "REST contract를 설계해줘." -> `architecture-api`
- "Ninja Router를 구현해줘." -> `implementation-django-ninja`
- "단순 설명만 해줘." -> direct answer; no test suite design
- "테스트 파일 import 순서만 고쳐줘." -> direct small edit; no full strategy

## Skill-Specific Hard Gates

- **Verification honesty**: claims pytest, coverage, mutation, browser, or integration test execution without command output.
- **Implementation-coupled tests**: tests assert private calls/internal structure where public behavior or contract would be more stable.
- **Mock misuse**: mocks domain objects or stable in-process collaborators by default, making tests brittle without isolation benefit.
- **Missing contract coverage**: API tests omit status code, response schema, Problem Details, auth, pagination/filtering when scenario requires them.
- **Missing consistency tests**: risky write/concurrency/idempotency scenario lacks integration, replay, uniqueness, or concurrency test criteria.
- **Flaky fix without cause**: flaky test is skipped/xfail-silenced without identifying timing, ordering, isolation, external dependency, or data leak cause.
- **Workflow over-application**: small test addition triggers full DDD/subagent workflow.

## Analytic Criteria

Use `common_rubric.md` scoring anchors. Core dimensions for this skill:

- **Test And Verification**: 5 when tests protect domain rules/API contracts/risky behavior and command execution status is clear.
- **Maintainability**: 5 when fixtures/factories/doubles are named by role, scoped appropriately, and avoid brittle implementation coupling.
- **Implementation Pragmatism**: 5 when test level (unit/integration/E2E/property/mutation) matches risk and cost.
- **Data And API Consistency**: applicable for DB/API/risky write tests; 5 requires constraint, transaction, idempotency, status/error, and OpenAPI-relevant behavior coverage as needed.
- **Workflow Fit**: 5 when TDD/composite workflow is used only when the scenario demands it.

Score 1 if tests are merely snapshot-like implementation checks, or if the report claims execution without evidence.

## Reference-Derived Additions

Required reference coverage:

- Test pyramid and SMURF trade-offs: speed, maintainability, utilization, reliability, fidelity.
- pytest fixtures should have suitable scope and teardown, not global state leaks.
- Test doubles must be named by role: dummy, stub, spy, mock, fake.
- Prefer state/result verification for domain behavior; use behavior verification for external interactions or collaboration contracts.
- Factories should build meaningful domain data without hiding important scenario facts.
- Time/HTTP/external side effects need deterministic fakes/mocks.
- Property-based, coverage, and mutation testing are optional risk-based additions, not universal requirements.

## Required Public Fixtures

Positive prompt:

```text
주문 생성 API의 pytest 테스트를 추가해줘. 중복 요청, Problem Details 오류, 인증 실패, 성공 응답을 Django Ninja TestClient로 검증하고 필요한 fixture/factory도 만들어줘.
```

Negative prompt:

```text
테스트 파일 하나의 import 정렬만 고쳐줘. 전체 TDD 계획이나 subagent 리뷰는 필요 없어.
```

Additional prompt 1:

```text
주문 생성 테스트에 성공, 인증 실패, 재고 부족 Problem Details, 중복 요청 replay 케이스를 pytest로 추가해줘.
```

Additional prompt 2:

```text
Django Ninja TestClient로 POST /orders API contract test를 만들고 fixture/factory_boy 데이터도 정리해줘.
```

Additional prompt 3:

```text
외부 결제 API 테스트가 자꾸 흔들려. fake를 둘지 mock을 둘지, flaky 원인을 어떻게 잡을지 봐줘.
```

Additional public fixtures may include code under test, existing tests, failure output, fixtures, factories, HTTP/time dependencies, or database setup. Public fixtures must not expose expected routing, pass criteria, hidden failure cases, or private scoring notes.

## Private Grader Key Notes

Expected routing:

- Positive prompt: `implementation-test`; add `implementation-django-ninja` only if Router behavior itself must change.
- Negative prompt: direct small edit; no full test strategy.
- Additional prompts 1-3: `implementation-test`; add `implementation-django-ninja` only when endpoint implementation changes are required.

Expected answer evidence:

- Tests cover behavior/contract rather than private implementation.
- Fixture/factory scope and data meaning are clear.
- API tests cover success, auth failure, validation/error Problem Details, duplicate/idempotency behavior when required.
- External dependencies use appropriate fake/mock/stub and do not overmock domain logic.
- Execution output or explicit not-run status is present.

Failure criteria:

- Test suite claims pass without output.
- Mocks replace the domain behavior under test.
- Risky write prompt lacks idempotency/concurrency/constraint test criteria.
- Flaky test is hidden with skip/xfail without cause analysis.
- Public eval packet leaks private expected coverage or scoring notes.
- Korean fixture/flaky wording is answered with broad TDD methodology instead of concrete pytest/test-double decisions.

Applicable hard gates: `Verification honesty`, `Scenario-required consistency decision missing` for risky writes, `Risky Write Consistency Block missing` only when product-docs output requires it, `Workflow over-application`, plus skill-specific test-quality gates above.

## Reference Loading Expectations

- Load `workspace/reference/implementation-test/reference/final.md` for pytest, fixtures, doubles, factories, property tests, coverage, mutation, and flaky test criteria.
- Load `workspace/reference/implementation-tdd/reference/final.md` only when the prompt asks for TDD cycle or test-first ordering.
- Load Django/API/DB references only for framework or contract-specific test requirements.
- Load DDD reference only when the invariant under test is unclear.

## Raw Artifact Checklist

- Test files, fixture/factory files, `conftest.py`, or proposed diffs.
- pytest/coverage/mutation command output when claimed.
- API request/response assertions, status code/error schema assertions, and auth/idempotency cases when applicable.
- Test double decision notes for external dependencies.
- Flaky test reproduction evidence and cause if relevant.
- Explicit "Not run" list and reasons.

## Scenario Tags

Primary tags: `test`, `simple`, `api`, `django-ninja`, `db`, `concurrency`, `risky-write`, `negative-simple`.

Usually N/A unless combined with other work: `tdd`, `ddd`, `migration`, `django-web`, `composite-workflow`, `runtime`, `skill-folder`.

## Do Not Penalize

- Not adding property-based, mutation, or coverage threshold work when risk is low.
- Using real domain objects instead of mocks for pure domain behavior.
- Using integration tests for ORM/constraint/transaction behavior where unit tests would be misleading.
- Marking tests as not run when dependencies or environment are unavailable.
- Routing TDD process design back to `implementation-tdd` instead of duplicating it here.
