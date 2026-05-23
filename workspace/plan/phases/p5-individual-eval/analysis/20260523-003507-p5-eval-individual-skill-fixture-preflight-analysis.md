수정 대상: `workspace/develop/eval/fixtures/individual-skills/`, `workspace/scripts/p5_individual_eval.py`, `workspace/scripts/test_p5_individual_eval.py`, `workspace/plan/phases/p5-individual-eval/`

# P5 Individual Skill Fixture Preflight Analysis

## Scope

This work item prepares the P5 individual skill eval matrix and a deterministic
fixture-scored runner. It does not claim P5 completion because the run is not
model-backed installed-runtime evidence.

Current precondition check:

| source | observed status |
|---|---|
| `workspace/plan/status/phase_status.md` | `p4-5-runtime-parity` is `complete` |
| `workspace/plan/phases/p4-5-runtime-parity/index.md` | parity precheck evidence row exists |
| `workspace/plan/phases/p4-5-runtime-parity/evidence/` | parity precheck evidence exists |

## Decision

To make concrete progress without redefining the completion gate, this work
item creates a fixture-scored preflight bucket that proves the intended
individual eval matrix, scoring cleanliness, report/raw consistency, and
current-file metadata digest checks.

The fixture preflight is not installed-runtime evidence and is not integration
eval evidence.

## Trigger-Family Matrix

Each high-risk trigger family from P1.5 has one positive and one negative
surface. Each case scores only these answer dimensions:

- `reference-criterion-coverage`
- `required-observations`
- `forbidden-overclaim`

| trigger family | positive case | negative case | negative expected loaded skill |
|---|---|---|---|
| REST API contract | `p5-architecture-api-positive` | `p5-architecture-api-negative` | `dddjango:implementation-django-ninja` |
| Relational DB integrity and rollout | `p5-architecture-db-positive` | `p5-architecture-db-negative` | `dddjango:architecture-ddd` |
| Domain modeling and invariants | `p5-architecture-ddd-positive` | `p5-architecture-ddd-negative` | `dddjango:architecture-db` |
| Implementation architecture patterns | `p5-architecture-implementation-patterns-positive` | `p5-architecture-implementation-patterns-negative` | `dddjango:architecture-ddd` |
| Maintainability review and refactor | `p5-implementation-cleancode-positive` | `p5-implementation-cleancode-negative` | `dddjango:architecture-implementation-patterns` |
| Django ORM/service/migration implementation | `p5-implementation-django-positive` | `p5-implementation-django-negative` | `dddjango:architecture-api` |
| Django Ninja API implementation | `p5-implementation-django-ninja-positive` | `p5-implementation-django-ninja-negative` | `dddjango:architecture-api` |
| Django server-rendered web | `p5-implementation-django-web-positive` | `p5-implementation-django-web-negative` | `dddjango:implementation-django-ninja` |
| Python language and typing implementation | `p5-implementation-python-positive` | `p5-implementation-python-negative` | `dddjango:implementation-django` |
| TDD workflow | `p5-implementation-tdd-positive` | `p5-implementation-tdd-negative` | `dddjango:implementation-test` |
| pytest and Django test mechanics | `p5-implementation-test-positive` | `p5-implementation-test-negative` | `dddjango:implementation-tdd` |
| Source/reference governance | `p5-source-reference-audit-positive` | `p5-source-reference-audit-negative` | `dddjango:architecture-api` |
| Coordinated dddjango workflow | `p5-workflow-dddjango-subagents-positive` | `p5-workflow-dddjango-subagents-negative` | `dddjango:source-reference-audit` |

## Gap Classification

| item | classification |
|---|---|
| P4.5 runtime parity | complete after later P4.5 parity precheck |
| model-backed individual runs | not run; completion blocked |
| fixture-scored individual matrix | implemented as preflight |
| affected bucket clean/scored | verified for fixture bucket only |
| integration proof | out of scope; individual eval must not be reused for P6 |
