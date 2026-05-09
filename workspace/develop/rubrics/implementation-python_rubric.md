# implementation-python Rubric

## Skill Scope

`implementation-python`은 Python 언어 기능과 타입 계약으로 도메인/구현 의도를 명시하는 스킬이다. 평가 대상은 type hints, `T | None`, built-in generics, dataclass, `Enum`/`StrEnum`, `Protocol`, `TypedDict`, `Literal`, exceptions, async boundaries, pydantic v2 boundary, Ruff/typecheck-friendly Python code다.

책임 경계:

- 범용 clean code review, 이름/함수/중복/캡슐화 판단은 `implementation-cleancode`가 우선하거나 함께 적용된다.
- Django model, QuerySet, migration, transaction 구현은 `implementation-django`가 담당한다.
- REST/Django Ninja 구현은 `implementation-django-ninja`가 담당한다.
- 도메인 경계, aggregate, invariant 발견은 `architecture-ddd`가 담당한다.
- pydantic v2는 외부 DTO/config/runtime validation에 쓰며 도메인 모델의 기본값으로 강제하지 않는다.

## Source Status

ready

Canonical sources:

- `workspace/docs/spec.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/reference-index.md`
- `workspace/reference/implementation-python/reference/final.md`

## Trigger Examples

- "주문 상태 전이를 `Enum`/`StrEnum`과 타입 힌트로 명시적으로 리팩터링해줘."
- "금액 값 객체를 frozen dataclass로 표현할지 판단해줘."
- "외부 결제 SDK adapter에 `Protocol`을 도입해야 하는지 봐줘."
- "pydantic v2 모델과 도메인 dataclass의 경계를 정리해줘."
- "Python 3.12 타입 문법과 Ruff 기준에 맞게 함수 시그니처를 고쳐줘."

## Anti-Trigger Examples

- "Order 모델 migration을 작성해줘." -> `implementation-django`
- "주문 aggregate와 invariant를 설계해줘." -> `architecture-ddd`
- "REST status code와 Problem Details 계약을 설계해줘." -> `architecture-api`
- "Django Ninja Router와 Schema를 구현해줘." -> `implementation-django-ninja`
- "이 레거시 서비스 코드의 책임 분리를 리뷰해줘." -> `implementation-cleancode`, plus this skill only for Python typing details
- "pytest fixture를 만들어줘." -> `implementation-test`

## Skill-Specific Hard Gates

- **Type contract opacity**: public function or method changes omit input/output type contracts where scenario asks for explicit typing.
- **Invalid state preserved**: refactor keeps illegal combinations that a simple union, enum, value object, or dataclass boundary should remove.
- **Pydantic domain overreach**: pydantic v2 is forced as the default domain model without external validation/DTO justification.
- **Protocol overuse**: `Protocol` or interface-like abstractions are introduced for stable concrete collaborators without replacement/testing need.
- **Async boundary confusion**: async refactor mixes sync Django ORM or external side effects without identifying runtime constraints.
- **Verification honesty**: claims Ruff, mypy, pyright, pytest, or runtime execution without evidence.
- **Workflow over-application**: small typing cleanup triggers full DDD/subagent workflow.

## Analytic Criteria

Use `common_rubric.md` scoring anchors. Core dimensions for this skill:

- **Implementation Pragmatism**: 5 when Python features are chosen for clarity and current constraints, not novelty.
- **Maintainability**: 5 when types, dataclasses, enums, exceptions, and protocols reduce invalid states and make caller expectations explicit.
- **Domain Reasoning**: applicable when Python constructs represent domain concepts; 5 requires matching value object/state/invariant choices to domain meaning.
- **Test And Verification**: 5 when typecheck/lint/test execution is evidenced or honestly listed as not run.
- **Workflow Fit**: 5 when simple Python refactors stay direct and broader domain/Django/API work is routed outward.

Score 1 if the output adds fashionable typing syntax without reducing ambiguity, or replaces clear domain objects with pydantic models by default.

## Reference-Derived Additions

Required reference coverage:

- Public contracts should use explicit parameter and return annotations.
- Use `T | None` and built-in generics for Python 3.10+ unless project compatibility says otherwise.
- Use `Enum`/`StrEnum`, `Literal`, or union types to constrain finite states.
- Use frozen/slots dataclasses for value objects when identity is not the point and immutability protects meaning.
- Use `Protocol` only for meaningful interchangeable boundaries such as external adapters, fakes, or plugins.
- Use pydantic v2 for DTO/config/runtime validation boundaries, not as a blanket domain model.
- Preserve runtime compatibility and existing project typing style.

## Required Public Fixtures

Positive prompt:

```text
주문 상태 전이 코드를 Python 타입과 dataclass/Enum을 사용해 더 명시적으로 리팩터링해줘. pydantic 모델과 도메인 객체 경계도 확인해줘.
```

Negative prompt:

```text
작은 helper 함수 하나에 타입 힌트만 추가해줘. DDD 설계나 subagent 계획은 필요 없어.
```

Additional public fixtures may include Python modules, typecheck output, Ruff output, pydantic DTOs, dataclass/domain code, or runtime errors. Public fixtures must not include expected routing, scoring keys, hidden failures, or private grader notes.

## Private Grader Key Notes

Expected routing:

- Positive prompt: `implementation-python`; add `architecture-ddd` only if state transitions/invariants are not defined.
- Negative prompt: direct `implementation-python`; no workflow, no domain model expansion.

Expected answer evidence:

- Type choices reduce invalid state or make None/collection/item types explicit.
- pydantic boundary is DTO/config/validation-facing, not the default domain model.
- Protocol use has a real interchangeable boundary or is rejected with reason.
- Verification commands are run or marked not run.

Failure criteria:

- Adds annotations that lie about possible `None`/error states.
- Introduces pydantic as domain default without justification.
- Adds Protocol, generic base classes, or complex type aliases that do not serve the current code.
- Public eval material leaks expected routing or hidden failure criteria.
- Claims typecheck/lint/test execution without evidence.

Applicable hard gates: `Verification honesty`, `Workflow over-application`, and skill-specific type/pydantic/protocol gates above.

## Reference Loading Expectations

- Load `workspace/reference/implementation-python/reference/final.md` for typing, dataclass, enum, protocol, async, pydantic, and modern Python guidance.
- Load `workspace/reference/implementation-cleancode/reference/final.md` only for responsibility/naming/refactoring judgment beyond Python typing.
- Load Django/API/DB references only when the Python refactor touches those concrete boundaries.
- Load DDD reference only when domain concept ownership or invariant meaning is unclear.

## Raw Artifact Checklist

- Changed Python module or proposed diff.
- Public function/method type signatures and any compatibility assumptions.
- Typecheck/Ruff/pytest output when claimed.
- Before/after examples showing invalid states removed or made explicit.
- Notes on pydantic/Protocol/dataclass boundary decisions.
- Explicit "Not run" list for omitted commands.

## Scenario Tags

Primary tags: `python`, `simple`, `review`, `test`, `negative-simple`.

Usually N/A unless combined with other work: `db`, `api`, `django-ninja`, `django-web`, `migration`, `composite-workflow`, `runtime`, `skill-folder`.

## Do Not Penalize

- Not using the newest Python syntax when project compatibility targets an older supported version.
- Keeping a simple class or function when dataclass/Protocol would add ceremony without reducing risk.
- Using pydantic at external input/output boundaries.
- Not running typecheck when the environment lacks the configured checker, if the report says it was not run.
- Routing broader Django/API/DDD changes to the correct skill instead of solving them inside this rubric.
