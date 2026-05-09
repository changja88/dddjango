# implementation-tdd Rubric

## Skill Scope

`implementation-tdd`는 테스트 우선 개발 흐름을 설계하고 실행하는 스킬이다. 평가 대상은 test list, first failing test, Red-Green-Refactor evidence, Inside-Out vs Outside-In choice, state vs behavior verification choice, small implementation steps, and refactoring checkpoints.

책임 경계:

- pytest fixture, mock/fake/factory, property-based testing, coverage/mutation 세부 구현은 `implementation-test`가 담당한다.
- 도메인 모델링 자체는 `architecture-ddd`가 담당하지만 TDD는 도메인 규칙을 테스트 목록과 실패 테스트로 명세화한다.
- Django/Ninja/API concrete implementation은 해당 implementation skill이 담당한다.
- 테스트 없이 구현 완료를 주장하지 않는다.
- 단순 수정에 TDD ceremony를 강제하지 않는다.

## Source Status

ready

Canonical sources:

- `workspace/docs/spec.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/validation-plan.md`
- `workspace/docs/reference-index.md`
- `workspace/reference/implementation-tdd/reference/final.md`

## Trigger Examples

- "쿠폰 할인 정책을 TDD로 구현해줘. 최소 주문 금액, 중복 사용 금지, 만료일을 포함해줘."
- "이 유스케이스를 Red-Green-Refactor로 작게 나눠 진행해줘."
- "Inside-Out과 Outside-In 중 어떤 TDD 흐름이 맞는지 판단해줘."
- "실패 테스트를 먼저 쓰고 최소 구현, 리팩터링 체크포인트를 잡아줘."
- "AI가 구현부터 하지 않게 TDD 사이클로 진행해줘."

## Anti-Trigger Examples

- "pytest fixture와 factory를 정리해줘." -> `implementation-test`
- "기존 테스트가 왜 flaky한지 고쳐줘." -> `implementation-test`, plus debugging workflow if failure analysis is needed
- "Django migration 파일을 구현해줘." -> `implementation-django`
- "주문 bounded context와 aggregate를 설계해줘." -> `architecture-ddd`
- "작은 오타 하나만 고쳐줘." -> direct small edit; no TDD ceremony
- "테스트 실행 결과만 해석해줘." -> direct analysis or `implementation-test` if test design changes

## Skill-Specific Hard Gates

- **TDD order violation**: TDD-requested work implements first without a test list or failing test step.
- **False red/green claim**: claims a failing or passing test was observed without execution evidence.
- **No refactor checkpoint**: TDD cycle stops at green with no review of duplication, naming, or design pressure.
- **Over-mocking domain rules**: domain behavior is verified only through mocks where state/result verification is feasible and stronger.
- **Missing edge cases**: policy/rule scenario omits boundary cases that define the behavior, such as expiration, duplicate use, minimum amount, invalid state.
- **Verification honesty**: claims pytest or test execution without command output.
- **Workflow over-application**: trivial changes receive full TDD/workflow ceremony despite no meaningful behavior risk.

## Analytic Criteria

Use `common_rubric.md` scoring anchors. Core dimensions for this skill:

- **Test And Verification**: 5 when test list, red test, green implementation, refactor checkpoint, and execution/not-run status are separated.
- **Domain Reasoning**: 5 when tests specify domain rules and invariants rather than implementation details.
- **Implementation Pragmatism**: 5 when cycle size and Inside-Out/Outside-In choice fit the task and current codebase.
- **Maintainability**: 5 when refactor steps respond to duplication, naming, and design pressure revealed by tests.
- **Workflow Fit**: 5 when TDD is used for behavior-bearing work and skipped or minimized for trivial edits.

Score 1 if implementation is produced first and tests are added afterward while calling the process TDD.

## Reference-Derived Additions

Required reference coverage:

- Red means a small test is added and observed or explicitly expected to fail.
- Green means the smallest implementation that satisfies the current test.
- Refactor means improving design while keeping tests green.
- Inside-Out is preferred for pure domain logic and state/result verification.
- Outside-In is useful for external interfaces and collaboration contracts.
- Mocks are for external systems or behavior verification where meaningful; they are not the default for domain object collaboration.
- TDD alone is not sufficient proof for security/concurrency; risky cases still need integration/concurrency verification criteria.

## Required Public Fixtures

Positive prompt:

```text
쿠폰 할인 정책을 TDD로 구현해줘. 최소 주문 금액, 중복 사용 금지, 만료일을 포함하고 Red-Green-Refactor 단계를 보여줘.
```

Negative prompt:

```text
README의 오타 하나만 고쳐줘. 테스트 계획이나 DDD 설명은 필요 없어.
```

Additional public fixtures may include current tests, source files, failing output, domain rules, or API contract snippets. Public fixtures must not expose expected routing, hidden pass criteria, scoring keys, or private grader notes.

## Private Grader Key Notes

Expected routing:

- Positive prompt: `implementation-tdd`; add `implementation-test` for pytest fixture/mock details and implementation skills for production code.
- Negative prompt: direct small edit; no TDD workflow.

Expected answer evidence:

- Test list precedes implementation.
- At least one failing test is written or clearly marked not executed with expected failure.
- Green step is minimal and tied to the test.
- Refactor checkpoint names design pressure and confirms tests remain green or not run.
- Boundary cases cover policy facts in the prompt.

Failure criteria:

- "TDD" answer begins with production implementation and retrofits tests.
- Test execution state is fabricated.
- Mock-heavy tests verify implementation calls instead of coupon policy outcomes.
- Refactor phase is absent.
- Public eval packet leaks expected answer or private scoring notes.

Applicable hard gates: `Verification honesty`, `Workflow over-application`, and skill-specific TDD order/false red-green gates above.

## Reference Loading Expectations

- Load `workspace/reference/implementation-tdd/reference/final.md` for TDD cycle, schools, verification style, and AI-assisted TDD criteria.
- Load `workspace/reference/implementation-test/reference/final.md` only when fixture/mock/factory/tooling details are in scope.
- Load DDD/API/Django references only when the behavior under test belongs to those domains.
- Do not load full workflow references for simple TDD exercises unless multiple roles or risky writes are involved.

## Raw Artifact Checklist

- Test list and scenario boundaries.
- Red test code and failure output, or clear not-run expected failure.
- Green implementation diff or minimal code plan.
- Refactor diff/checkpoint and tests-after-refactor output when claimed.
- Not-run commands and reasons.
- Any handoff to `implementation-test` or implementation skill for concrete code ownership.

## Scenario Tags

Primary tags: `tdd`, `test`, `simple`, `ddd`, `negative-simple`.

Usually N/A unless combined with other work: `db`, `api`, `django-ninja`, `migration`, `risky-write`, `composite-workflow`, `runtime`, `skill-folder`.

## Do Not Penalize

- Using a lightweight test list instead of full code when the user asks for planning only.
- Not using mocks for pure domain rules.
- Stopping before implementation when the requested step is only Red.
- Marking tests as not run when execution is unavailable.
- Skipping TDD ceremony for typo-only or documentation-only edits.
