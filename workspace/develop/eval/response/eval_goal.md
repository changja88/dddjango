# Response Eval Goal

## Goal

`response` 평가는 파일 수정을 요구하지 않는 prompt에서 baseline과 `with-dddjango` 응답의 판단 품질, skill routing, reference 적용, 과적용 방지, 검증 정직성, leakage 방지를 비교한다.

핵심 목표는 `dddjango`가 reference를 암기한 듯 나열하는지보다, 사용자의 요청 범위에 맞는 판단 순서와 책임 경계를 실제 응답에 적용하는지 확인하는 것이다.

## Reference Basis

평가 case는 다음 source를 함께 반영해야 한다.

- `workspace/reference/spec.md`, `workspace/reference/*/reference/final.md`, `dddjango/skills/*/SKILL.md`, `workspace/develop/eval/*/eval_goal.md`
- `workspace/reference/source-reference-audit/reference/final.md`의 source boundary, reference gap, DRF guardrail
- `workspace/reference/*/reference/{final,internal,external,review}.md`
- runtime `dddjango/skills/*/SKILL.md` and directly linked `references/*.md`
- `skill-creator` 원칙 중 trigger description, progressive disclosure, validation integrity

## Case Families

- Strategic DDD: subdomain, bounded context, context map, ubiquitous language가 tactical pattern보다 먼저 판단되는가.
- Implementation pattern choice: repository/UoW, hexagonal, CQRS, outbox, saga, ACL, transaction script, Django-native structure를 필요와 비용으로 선택하는가.
- DB/API architecture: constraint, index, transaction/isolation/locking, idempotency storage, REST resource, status code, Problem Details, pagination, versioning, OpenAPI를 요청 범위에 맞게 다루는가.
- Django/Ninja/Web/Python implementation advice: Django model/service/selector/migration, Django Ninja Router/Schema/TestClient, template/static/HTMX/CSRF, Python typing/dataclass/Enum/Protocol/pydantic boundary를 올바르게 라우팅하는가.
- TDD/Test/Clean Code: test list, Red-Green-Refactor, pytest fixture/double/factory/property test, responsibility/naming/encapsulation/refactoring findings를 상황에 맞게 제안하는가.
- Validation-plan representative scenarios: 주문 생성 API, 쿠폰 정책 TDD, DRF-to-Ninja 전환, Fat Model 리뷰, View Logic 리뷰, 운영 마이그레이션, 트랜잭션/동시성, Django Web, Python Typing, Architecture Pattern Selection.
- Negative cases: 단순 필드 rename, 짧은 설명, false subagent claim, user opt-out에서 workflow나 subagent claims를 과하게 출력하지 않는가.

## Minimum Coverage

완성된 response eval pack은 Validation Plan의 대표 시나리오와 negative case를 각각 최소 하나 이상의 public case로 덮어야 한다. specialist-positive, mixed-boundary, ambiguity, prompt-injection, eval-leakage, simple-negative, false-claim family를 모두 포함한다. 단일 response smoke case나 hard-coded score만으로 완료 처리하지 않는다.

세부 reference dimensions는 다음을 빠뜨리면 안 된다.

- DDD: subdomain classification, bounded context, context map, ubiquitous language, aggregate boundary, invariant, value object/entity, domain event, dispatch timing, outbox/eventual consistency.
- Risky DB/API: idempotency replay/conflict, uniqueness storage, locking/isolation, side-effect timing, Problem Details output checklist, OpenAPI impact.
- Implementation patterns: lightest sufficient pattern, patterns not chosen, ports/adapters, repository/UoW, CQRS, saga, outbox, ACL only when triggered.
- Python/TDD/Test/Clean Code: typing/dataclass/Enum/Protocol/pydantic boundaries, Red-Green-Refactor/test-list honesty, fixture/double/factory/property/coverage choices, severity-first review findings.

## Answer Oracle

각 response case는 `answer/case-*.yaml`에 evaluator-only oracle을 둔다. `answer`는 공개 문제에 들어가지 않고, response runner의 workspace copy, prompt-input, runtime references에도 들어가면 실패다.

`answer`는 최소한 다음을 담는다.

- `case_id`, `kind: response`, source reference list
- required answer dimensions and forbidden overreach
- required skill routing or explicit direct-answer path
- expected omissions when scope is intentionally small
- verification honesty requirements
- leakage and false-claim checks
- hard gates that force fail/block on evaluator leakage, unsupported command claims, or unsupported subagent claims
- `control_case` label when baseline pass is acceptable for restraint, negative, honesty, or safety controls
- `expected_outcomes` for baseline, `with_dddjango`, expected delta, and whether baseline pass is acceptable
- scoring or pass/fail observations for baseline and `with-dddjango`
- `allow_adversarial_public_terms: true` plus allowed bait terms when a public prompt intentionally mentions hidden/evaluator terms without leaking the actual oracle

## Evidence To Capture

- public prompt packet
- baseline output and `with-dddjango` output
- baseline isolation artifact
- `with-dddjango` prompt-input artifact
- command, exit code, event stream, stderr
- answer oracle evaluation notes
- machine-readable answer-oracle evaluation artifact, e.g. `raw/<case>-answer-oracle-evaluation.json`, with `caseId` and `answerOracleEvaluated: true`

## Non-Goals

- 실제 code diff가 필요한 평가는 `code` 폴더에서 다룬다.
- plugin packaging 구조 검증은 `plugin` 폴더에서 다룬다.
- runtime cache exposure 자체는 `runtime` 폴더에서 다룬다.
- evaluator-only `answer/` 내용을 public prompt나 skill runtime에 심어 점수를 만들지 않는다.

## Completion Gate

Response eval은 `workspace/develop/eval/response/cases/plugin/public/`에 하나 이상의 `case-*.md`가 있고, 같은 id의 `answer/case-*.yaml`이 존재하며, 선택된 case 수가 0이 아닐 때만 완료 후보가 된다.

`workspace/scripts/run_plugin_eval.py`가 생성한 run artifact와 `workspace/scripts/validate_eval_protocol.py`의 protocol isolation 검증을 함께 확인한다. Harness와 validator는 selected case count가 0이면 실패해야 하고, `answer/`는 eval workspace와 prompt-input에서 제외되어야 한다. zero-case validation pass는 유효하지 않다.

Protocol 검증은 응답 품질을 점수화하지 않는다. 완료 판정에는 모든 claimed case의 public prompt, baseline/with outputs, command, event stream, stderr, exit status, baseline isolation artifact가 `workspace/develop/eval/response/runs/<run-id>/` 아래에 있어야 한다. 필요한 fixture는 `workspace/develop/eval/response/fixtures/` 아래에서 추적되어야 한다. Report renderer나 readability validator가 hard-coded judgment만으로 passing-looking report를 만들면 완료로 보지 않는다.

`answer/` oracle을 기준으로 baseline과 `with-dddjango` output을 scored/manual analysis한 결과가 필요하다. 그 분석은 reference 적용, skill routing, 과적용 방지, validation honesty, leakage 방지를 모두 판정해야 하며, renderer가 소비할 수 있는 machine-readable answer-oracle evaluation artifact를 case별로 남겨야 한다. Response report가 runtime/source/workflow/code/plugin sibling bucket까지 완료했다고 암시하면 실패다.
