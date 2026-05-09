# implementation-cleancode Rubric

## Skill Scope

`implementation-cleancode`는 책임 분리, 이름, 함수, 캡슐화, 추상화, 오류 처리, 중복, SOLID, 리팩터링, 레거시 코드 리뷰를 평가하거나 수행하는 스킬이다. 평가 대상은 evidence-backed review findings, behavior-preserving refactor plans/diffs, naming/function extraction decisions, abstraction boundaries, duplication judgment, and maintainability risks.

책임 경계:

- 도메인 모델링, bounded context, aggregate, invariant 발견은 `architecture-ddd`가 담당한다.
- Django model/query/migration implementation은 `implementation-django`가 담당한다.
- Python typing/dataclass/Protocol detail은 `implementation-python`이 담당한다.
- 테스트 구현 세부는 `implementation-test`가 담당한다.
- 코드 리뷰 요청에서는 findings가 먼저 나오고, 심각도와 근거가 명시되어야 한다.

## Source Status

ready

Canonical sources:

- `workspace/docs/spec.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/reference-index.md`
- `workspace/reference/implementation-cleancode/reference/final.md`

## Trigger Examples

- "Order 모델이 너무 커졌는지 리뷰하고 어떤 로직을 남길지 판단해줘."
- "이 service 함수를 읽기 쉽게 리팩터링해줘."
- "책임 분리와 추상화가 과한지 dddjango 기준으로 리뷰해줘."
- "중복을 제거해야 할지, 아직 유지해야 할지 판단해줘."
- "legacy 코드에 characterization test를 두고 안전하게 개선할 계획을 세워줘."
- "view에 비즈니스 규칙이 섞인 것 같은데 dddjango 기준으로 리뷰해줘."
- "비슷한 함수가 세 군데 있는데 공통화해야 할지 아직 두는 게 나은지 봐줘."

## Anti-Trigger Examples

- "주문 aggregate와 bounded context를 설계해줘." -> `architecture-ddd`
- "Django migration 파일을 구현해줘." -> `implementation-django`
- "타입 힌트와 dataclass만 정리해줘." -> `implementation-python`
- "pytest fixture와 mock을 작성해줘." -> `implementation-test`
- "REST endpoint 계약을 설계해줘." -> `architecture-api`
- "단순 오타 수정만 해줘." -> direct small edit; no broad review ceremony
- "변수명 하나만 고쳐줘." -> direct small edit; no full review/workflow ceremony

## Skill-Specific Hard Gates

- **Evidence-free review**: review findings lack file/line, code behavior, or concrete artifact evidence.
- **Severity order missing**: explicit code review output does not lead with findings ordered by severity.
- **Behavior preservation missing**: refactor changes behavior without tests, characterization, or explicit risk callout.
- **Premature abstraction**: introduces interfaces, base classes, plugin layers, or generic config without repeated change axis or real duplication of knowledge.
- **Wrong responsibility split**: splits by file size/method count alone instead of change reason, invariant, or domain knowledge.
- **Domain leakage ignored**: identifies style issues but misses business rules scattered across adapters when review prompt asks dddjango 기준.
- **Verification honesty**: claims tests/lint/review/subagent execution without evidence.
- **Workflow over-application**: simple code cleanup triggers full DDD/subagent workflow.

## Analytic Criteria

Use `common_rubric.md` scoring anchors. Core dimensions for this skill:

- **Maintainability**: 5 when findings explain responsibility, naming, abstraction, duplication, error handling, and coupling in terms of change cost and evidence.
- **Implementation Pragmatism**: 5 when refactors are small, behavior-preserving, and aligned with existing project patterns.
- **Domain Reasoning**: applicable when quality issues affect business rules; 5 requires protecting invariants and routing deeper modeling to `architecture-ddd`.
- **Test And Verification**: 5 when risky refactors have characterization tests or executed/not-run verification status.
- **Workflow Fit**: 5 when review/refactor scope is proportional and simple changes are handled directly.

Score 1 if the output is style preference without evidence, or "extract service/repository" is recommended solely because a file is large.

## Reference-Derived Additions

Required reference coverage:

- Responsibility is divided by reason to change, not by line count.
- Names reveal intent, role, and domain language without encoding incidental implementation strategy.
- Functions should be cohesive and explicit about inputs, outputs, dependencies, and side effects.
- Encapsulation means keeping representation and invariants behind stable behavior, not adding trivial getters/setters.
- Deep modules and small interfaces are preferred over shallow abstractions with many knobs.
- Duplication of business knowledge is riskier than similar-looking code; premature generic abstraction is also a risk.
- Refactoring should be behavior-preserving and supported by tests or characterization in legacy code.

## Required Public Fixtures

Positive prompt:

```text
Order 모델이 너무 커졌는지 dddjango 기준으로 리뷰해줘. 어떤 로직을 model method에 남기고 어떤 흐름을 service/usecase로 뺄지 판단해줘.
```

Negative prompt:

```text
이 작은 함수 이름 하나만 더 명확하게 바꿔줘. 전체 DDD 설계나 subagent 계획은 필요 없어.
```

Additional prompt 1:

```text
주문 취소 로직이 view, model, service에 조금씩 흩어져 있어. dddjango 기준으로 책임 분리와 리팩터링 방향을 리뷰해줘.
```

Additional prompt 2:

```text
비슷한 validation 코드가 세 군데 있는데 바로 추상화해야 할지, 중복을 조금 더 두는 게 나은지 판단해줘.
```

Additional prompt 3:

```text
이 함수가 너무 길어 보여. 그런데 동작은 바꾸면 안 돼. 어떤 부분만 안전하게 쪼갤 수 있는지 리뷰해줘.
```

Additional public fixtures may include code snippets, diffs, failing tests, coverage output, or dependency graphs. Public fixtures must not expose expected findings, scoring notes, hidden failure criteria, or private grader key.

## Private Grader Key Notes

Expected routing:

- Positive prompt: `implementation-cleancode`; add `architecture-ddd` if aggregate/invariant ownership is unresolved.
- Negative prompt: direct small refactor; no workflow role map.
- Additional prompts 1-3: `implementation-cleancode`; add `architecture-ddd` only when business invariant ownership is not derivable from the code.

Expected answer evidence:

- Review findings come first, ordered by severity, with file/line or concrete code evidence.
- Fat model judgment distinguishes model-owned invariants from usecase/application flow.
- Refactor proposals preserve behavior and identify tests or characterization gaps.
- Avoids extracting abstractions unless there is repeated business knowledge or stable change axis.

Failure criteria:

- Findings are generic style opinions without evidence.
- Large file is treated as automatic reason to split.
- Business rule duplication or adapter leakage is missed in a dddjango review fixture.
- Behavior-changing refactor is presented as safe without verification.
- Public eval packet leaks expected findings or private scoring key.
- Korean "길다/흩어져 있다/중복" prompts are answered with generic style advice instead of evidence-backed findings.

Applicable hard gates: `Verification honesty`, `Business logic in adapter` when review involves adapters, `Workflow over-application`, plus skill-specific review/refactor gates above.

## Reference Loading Expectations

- Load `workspace/reference/implementation-cleancode/reference/final.md` for responsibility, naming, abstraction, duplication, error handling, and legacy refactoring criteria.
- Load `workspace/reference/architecture-ddd/reference/final.md` only when responsibility decisions depend on domain invariant or aggregate boundaries.
- Load Django/Python/Test references only for framework, type, or test-specific implementation details in the fixture.
- Do not load unrelated architecture pattern references just to justify a simple cleanup.

## Raw Artifact Checklist

- Reviewed file paths and line references, diff hunks, or concrete code snippets.
- Findings with severity and evidence for review cases.
- Refactor plan/diff and behavior preservation strategy.
- Test/lint/typecheck output when claimed.
- Characterization test plan for legacy behavior that cannot be safely inferred.
- Explicit "Not run" list for omitted verification.

## Scenario Tags

Primary tags: `review`, `simple`, `view-adapter`, `python`, `test`, `negative-simple`.

Usually N/A unless combined with other work: `db`, `api`, `django-ninja`, `django-web`, `migration`, `composite-workflow`, `runtime`, `skill-folder`.

## Do Not Penalize

- Leaving cohesive code together even if the file is long.
- Keeping limited duplication when shared meaning or change direction is not yet clear.
- Avoiding interfaces or base classes for stable concrete dependencies.
- Not adding full DDD modeling for a small naming or readability refactor.
- Reporting no findings when the review evidence genuinely shows no issue, while still noting residual test gaps.
