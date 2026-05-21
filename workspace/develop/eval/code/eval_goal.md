# Code Eval Goal

## Goal

`code` 평가는 `dddjango`가 실제 Django/Python 작업에서 reference 판단을 말로만 반복하지 않고, 제한된 workspace 안에서 검증 가능한 코드 변경으로 옮기는지 평가한다.

핵심 목표는 baseline과 `with-dddjango`의 변경 파일, diff, 테스트/검증 로그, 실행하지 못한 검증 보고, 그리고 `answer/`의 문제별 oracle을 비교해 plugin이 구현 품질을 실제로 개선하는지 판단하는 것이다.

## Reference Basis

평가 case는 다음 source를 함께 반영해야 한다.

- `workspace/reference/spec.md`, `workspace/reference/*/reference/final.md`, `dddjango/skills/*/SKILL.md`, `workspace/develop/eval/code/eval_goal.md`
- `workspace/reference/architecture-ddd/reference/{final,internal,external,review}.md`
- `workspace/reference/architecture-db/reference/{final,internal,external,review}.md`
- `workspace/reference/architecture-api/reference/{final,internal,external,review}.md`
- `workspace/reference/implementation-django/reference/final.md`
- `workspace/reference/implementation-python/reference/{final,internal,external,review}.md`
- `workspace/reference/implementation-tdd/reference/{final,internal,external,review}.md`
- `workspace/reference/implementation-test/reference/{final,internal,external,review}.md`
- `workspace/reference/implementation-cleancode/reference/{final,internal,external,review}.md`
- runtime bundled references under `dddjango/skills/*/references/`

## Case Families

- DDD-to-code mapping: subdomain, bounded context, ubiquitous language, aggregate, invariant, domain event, application service가 Django/Python 코드에 추적 가능하게 반영되는가.
- Django implementation: model, QuerySet/Manager, service/selector, transaction, migration, performance/security setting을 Django 관용구와 충돌 없이 구현하는가.
- Django Web implementation: TemplateView, template inheritance/include, static files, HTMX, CSRF/AJAX, safe rendering, web render verification이 구현 산출물에 반영되는가.
- Django Ninja API: Router/Schema는 얇은 adapter로 남고, status code, Problem Details, auth, pagination, OpenAPI, TestClient 기준이 코드와 테스트에 반영되는가.
- DB consistency: unique/check/not-null/FK/cascade, index, transaction boundary, locking, idempotency storage, rollout/backfill/index-lock risk가 코드와 migration에 나타나는가.
- TDD/test implementation: test list, failing-test-first intent, pytest fixture/factory/test double/property test 선택이 도메인 규칙과 API 계약을 보호하는가.
- Python and clean code: type hints, `Enum`/`StrEnum`, dataclass/value object, Protocol boundary, pydantic v2 boundary, responsibility split, naming, encapsulation이 과하거나 부족하지 않은가.
- Negative implementation restraint: 작은 rename/단순 CRUD/짧은 fix에서 repository, UoW, hexagonal, role map, broad refactor를 만들지 않는가.

## Minimum Coverage

완성된 code eval pack은 위 Case Families마다 최소 하나 이상의 public case와 matching `answer` oracle을 가져야 한다. 구현을 요구하는 positive case와, 올바른 답이 no-code/minimal-code/refusal/clarifying-question인 negative case를 모두 포함한다. 단일 smoke case로 이 bucket을 완료 처리하지 않는다.

구체적으로 다음 artifact 기준을 case에 포함한다.

- Code fixture: `workspace/develop/eval/code/fixtures/<fixture-id>/` 또는 equivalent tracked fixture path는 독립 실행 가능한 subject repo여야 하며, public prompt가 기대하는 시작 파일, dependency/install instructions, deterministic bootstrap data, allowed mutation scope, validation command prerequisites를 포함해야 한다. Fixture에는 `answer/` oracle, prior run output, private scoring note를 넣지 않는다.
- TDD 요청: test list, failing test 또는 명시적 not-run status, minimal green implementation, refactor checkpoint.
- Migration/DB safety: `apps.get_model()`, `RunPython`, `sqlmigrate` 필요 여부, expand/backfill/contract, constraint/index names, lock/index risk, rollback or forward-fix plan.
- Django Ninja API: thin Router, scoped Schema/ModelSchema, Problem Details, auth/pagination/filtering, idempotency behavior, TestClient tests, OpenAPI/schema impact.
- Django Web: TemplateView/view context, templates/includes, static assets, HTMX/CSRF decisions, XSS-safe output, render or browser-level verification.
- Python quality: public type contracts, `Enum`/`StrEnum`, frozen/slots dataclass value objects, Protocol only for real boundaries, pydantic v2 only at external boundaries, Ruff/typecheck reporting.
- Performance/security: N+1 prevention, `select_related`/`prefetch_related`, query-count checks when relevant, `transaction.on_commit()`, `check --deploy` when settings/security changes.

## Answer Oracle

각 `cases/plugin/public/case-*.md`에는 같은 id의 `answer/case-*.yaml`이 있어야 한다. `answer`는 evaluator-only이며 실행 workspace, prompt-input, public packet, runtime skill reference에 들어가면 실패다.

`answer`는 최소한 다음을 담는다.

- `case_id`, `kind: code`, `source_refs`
- `code_expected: true|false` and `code_expected_reason` when no code should be produced
- Direct DDD code cases must declare `case_role: ddd_direct` and include `ddd_observations` with business problem, subdomain type and basis, bounded context, context-map or not-applicable decision, ubiquitous terms, aggregate root, aggregate behavior, invariants, application-service boundary, transaction boundary, Django/API mapping or limitation, and test evidence. Supporting implementation and control/restraint cases must use `case_role: implementation_supporting` or `case_role: control` and must not be counted as DDD-shaped implementation confidence.
- 허용/금지 변경 파일 또는 path pattern
- 반드시 생성되어야 하는 artifact: `changed-files.json`, `diff.patch`, copied source files, command/exit/stderr/stdout
- 반드시 실행하거나 명시적으로 미실행 보고해야 하는 command
- 도메인/API/DB/Django/Test/Python/Clean Code 관찰점과 hidden behavioral/invariant checks
- overengineering 금지 조건과 leakage 금지 조건
- hard gates for evaluator leakage, unsupported command claims, false external integration claims, and unsupported subagent claims
- `control_case` label when no-code, minimal-code, negative, honesty, or restraint behavior makes baseline pass acceptable
- `expected_outcomes` for baseline, `with_dddjango`, expected delta, and whether baseline pass is acceptable

## Evidence To Capture

- public prompt packet and operator prompt
- baseline and `with-dddjango` raw responses
- `changed-files.json`, `diff.patch`, copied text source files
- command text, exit code, stderr/stdout, event stream
- test/lint/typecheck/migration command output, or explicit not-run reason
- answer oracle evaluation result for each variant

## Completion Gate

Code eval은 `workspace/develop/eval/code/cases/plugin/public/`에 하나 이상의 `case-*.md`가 있고, 같은 id의 `answer/case-*.yaml`이 모두 존재할 때만 시작할 수 있다. `workspace/develop/eval/code/cases/plugin/code-capture.json`에는 각 code case의 `captureCode: true`와 `workspace/develop/eval/code/fixtures/` 아래의 유효한 `subjectRepo` 또는 명시적으로 승인된 외부 fixture path가 있어야 한다.

Harness는 selected case count가 0이면 실패해야 하고, `answer/`를 eval workspace와 prompt-input에서 제외해야 한다. `--capture-code` 실행에서 `code-capture.json`이 없거나 selected case의 `captureCode: true`, `subjectRepo`가 빠지면 response-only로 degrade하지 말고 실패해야 한다.

`workspace/scripts/run_plugin_eval.py --capture-code` 실행 시 code case와 `baseline`, `with-dddjango` 두 variant를 명시적으로 선택한다. 두 variant 모두 `workspace/scripts/validate_eval_code_artifacts.py`로 검증하고, 코드 생산 case에서는 `noCodeProduced: false`, 비어 있지 않은 `files`, `changed-files.json`, `diff.patch`, source file 사본을 확인한다. no-code가 정답인 negative case는 `answer`에 `code_expected: false`와 `code_expected_reason`이 있을 때만 `noCodeProduced: true`를 허용한다.

Validator 통과만으로 완료하지 않는다. baseline code-backed case에는 `raw/<case>-baseline-isolation.json` `pass: true`가 필요하다. `answer/` oracle이 reference 기반 관찰점, 허용/금지 파일, hidden behavioral tests, invariant checks, command honesty, overengineering 방지, private oracle leakage 방지를 판정하고, 그 결과가 `runs/<run-id>/analysis/` 또는 동등한 평가 산출물에 남아야 통과다.
