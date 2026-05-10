# Source Coverage Crosswalk: implementation-test

## Status

- Skill: `implementation-test`
- Runtime target: `dddjango/skills/implementation-test/`
- Source status: ready
- Runtime reference split: follows `workspace/docs/plugin-structure.md` without deviation
- Runtime references: `pytest-fixtures.md`, `test-doubles.md`, `factories-property-tests.md`, `coverage-mutation.md`
- Rubric status: not opened during draft; reserved for post-source-review verification

## Sources Used

- `workspace/develop/skill_goal_instructions.md`
- `workspace/docs/spec.md`
- `workspace/docs/plugin-structure.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/skill-hierarchy.md`
- `workspace/docs/skill-authoring.md`
- `workspace/docs/reference-index.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/workflow.md`
- `workspace/docs/validation-plan.md`
- `workspace/reference/implementation-test/reference/final.md`

## Authoring And Product Docs

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill_goal_instructions.md` `## 범위` | included | runtime path, this crosswalk | Plugin-bundled target and crosswalk location followed. |
| `## 실행 규칙` | included | this workflow | One skill at a time; rubrics not used during draft. |
| `## 구현 순서` | included | plan order | This follows `implementation-tdd`. |
| `## Skill별 작성 루프` | included | this crosswalk, review notes | Source scope, draft, review, and rubric sequencing tracked. |
| `### Source Coverage Crosswalk` | included | this file | Source headings and runtime treatment tracked. |
| `## SKILL.md 작성 규칙` | included | `SKILL.md` | Frontmatter has only name/description; body is concise and procedural. |
| `## Runtime Reference 작성 규칙` | included | `references/*.md` | Four one-level references summarize source rather than copying it. |
| `## Agents Metadata 작성 규칙` | included | `agents/openai.yaml` | Metadata aligns with source and runtime skill. |
| `## 한국어 사용자 기준` | included | `SKILL.md` description | Korean triggers for 테스트 코드 작성/리뷰, pytest 픽스처, 모킹/mock, 테스트 더블, 팩토리, 커버리지, 뮤테이션 테스트, 속성 기반 테스트, 중복 요청/동시성 테스트, flaky/불안정 테스트 included. |
| `## Provisional Skill 처리` | omitted | n/a | This skill has dedicated source reference and is not provisional. |
| `## Cross-Skill Routing 기준` | included | `SKILL.md` Routing | Adjacent TDD, DDD, implementation, and workflow boundaries included. |
| `## Review 기준` | included | Review Notes | Review types and findings tracked. |
| `## Completed 조건` | included | Review Notes, final validation record | Completion requires zero remaining blocking/major/minor findings; final evidence is recorded for this skill. |
| `## 검증` | included | final validation record | Only executed validation is reported; completion validation was performed. |
| `## 완료 보고` | included | completion report | Required report fields are captured in the completion report and commit history. |
| `## Goal Objective Template` | omitted | n/a | Goal prompt authoring content is not runtime behavior. |
| `spec.md` `## 관련 문서` | included | Sources Used | Linked product docs are covered. |
| `## 1. 목표` | merged | `SKILL.md`, references | Tests protect domain/API rules and executable verification. |
| `## 2. 설계 원칙` | included | `SKILL.md`, references | Domain/API tests, behavior focus, and validation honesty reflected. |
| `## 3. 스킬 종류` | included | `SKILL.md` Routing | Test responsibility and adjacent skill boundaries included. |
| `### Core DDD` | delegated-to-other-skill | `architecture-ddd`, `architecture-implementation-patterns` | Domain modeling and implementation architecture choices route away before test assertions are locked. |
| `### Implementation Mapping` | merged | `SKILL.md` Routing, `coverage-mutation.md` | Django/Ninja/Web/Python production implementation routes away; this skill owns tests for those mapped behaviors when assigned. |
| `### Supporting Architecture` | merged | `SKILL.md` Routing, `coverage-mutation.md` | DB/API architecture routes away while DB/API contract tests, idempotency, and concurrency criteria are supported after decisions are clear. |
| `### Quality` | included | `SKILL.md`, references | `implementation-test` responsibility, TDD boundary, and clean-code adjacency are reflected. |
| `### Workflow` | delegated-to-other-skill | `SKILL.md` Routing, `workflow-dddjango-subagents` | Composite/risky role decomposition routes to workflow. |
| `## 4. 산출물 기준` | included | `SKILL.md`, references | Test artifacts, factories, doubles, and honest verification included. |
| `plugin-structure.md` `## 1. 개발 위치` | included | runtime path | Runtime files live under plugin artifact because plugin runtime requires it. |
| `## 2. 목표 구조` / `## 2.1 Runtime 동기화 기준` | included | `dddjango/skills/implementation-test/` | Plugin-bundled structure used; no cache edits. |
| `## 3. Skill 파일 기준` | included | `SKILL.md` | Trigger, routing, references, and runtime rules only. |
| `## 4. Reference 파일 기준` | included | `references/*.md` | One-level references directly linked. |
| `## 5. Claude Code와 Codex 공통성` | included | `SKILL.md`, references | Shared skill name and responsibility preserved. |
| `## 6. 작성 순서` | included | this workflow | Docs/reference read before rubric review. |
| `## 7. Runtime Reference Split Plan` | included | four reference files | Exact split for `implementation-test` used. |
| `## 8. 금지 사항` | included | file tree, `SKILL.md` | No auxiliary docs; no false validation claim. |
| `skill-authoring.md` `## 1. 작성 원칙` | included | `SKILL.md` | Trigger/routing and boundaries are in description/body. |
| `## 2. Frontmatter 입력 표` | included | `SKILL.md` description | pytest, fixture, mock, factory, coverage, testcontainers signals included. |
| `## 3. Cross-Skill Precedence` | included | `SKILL.md` Routing | Workflow/DDD/TDD precedence applied only when relevant. |
| `## 4. Agents Metadata Inputs` | included | `agents/openai.yaml` | Display name, short description, and default prompt align. |
| `reference-index.md` `## Architecture` | delegated-to-other-skill | `architecture-*` skills | Architecture source mapping outside test implementation. |
| `## Implementation` | included | references | Implementation-test source reference used for runtime split. |
| `## Reference 사용 원칙` | included | references | Runtime references summarize source and avoid copying `final.md`. |
| `## Reference Gap` | omitted | n/a | This skill has dedicated source reference. |
| `## DRF Guardrail` | delegated-to-other-skill | `implementation-django-ninja` | API framework choice outside test implementation. |
| `## Reference에서 도출한 제품 결정` | included | `SKILL.md`, references | TDD/pytest split, behavior-first verification, and false-claim prevention reflected. |

## Contracts, Workflow, And DDD Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill-contracts.md` `## architecture-ddd` | delegated-to-other-skill | `SKILL.md` Routing | Unclear invariants route to DDD before assertions. |
| `## architecture-implementation-patterns` | delegated-to-other-skill | `architecture-implementation-patterns` | Architecture pattern selection is outside test implementation. |
| `## architecture-db` / `## architecture-api` | delegated-to-other-skill | `SKILL.md` Routing | Unresolved DB/API contract design routes away before tests encode assumptions. |
| `## implementation-django` / `## implementation-django-ninja` / `## implementation-django-web` | delegated-to-other-skill | `SKILL.md` Routing | Production implementation routes away; tests are owned here. |
| `## implementation-python` / `## implementation-cleancode` | delegated-to-other-skill | `implementation-python`, `implementation-cleancode` | Python/refactor details route away unless writing tests for them. |
| `## implementation-tdd` | delegated-to-other-skill | `SKILL.md` Routing | Red-Green-Refactor flow routes to TDD skill; pytest mechanics remain here. |
| `## implementation-test` | included | `SKILL.md`, references | Pytest, fixtures, doubles, factories, property tests, coverage, mutation, and file ownership covered. |
| `## workflow-dddjango-subagents` | delegated-to-other-skill | `SKILL.md` Routing | Composite, risky, subagent, and role-decomposed Django work routes to workflow. |
| `## 공통 필수 출력` | merged | `workflow-dddjango-subagents`, `SKILL.md`, `coverage-mutation.md` | The named block belongs to workflow/composite outputs; this skill must still cover test criteria for risky write consistency. |
| `### Risky Write Consistency Block` | merged | `SKILL.md`, `coverage-mutation.md` | Transaction owner, locking, idempotency, API behavior, side-effect timing, isolation/retry, and integration/concurrency test criteria are supported after responsible architecture roles make the decisions. |
| `skill-hierarchy.md` `## Skill Hierarchy` | included | `SKILL.md` Routing | Test skill is an implementation support skill and can combine with TDD/Django/API skills. |
| `workflow.md` `## 1. 기본 흐름` | merged | `SKILL.md` Routing | Domain ambiguity routes before tests; tests verify resulting decisions. |
| `## 2. 작업 유형별 흐름` | included | `SKILL.md` Routing | Simple pytest work direct; composite/risky work routes to workflow. |
| `## 3. 역할 분해` | included | `SKILL.md`, references | Test Agent ownership of `tests/**`, fixtures, doubles, API/integration tests reflected. |
| `## 4. Sequential Fallback` / `## 5. Handoff Contract` | delegated-to-other-skill | `workflow-dddjango-subagents` | Workflow orchestration belongs elsewhere. |
| `## 6. 통합 우선순위` | merged | `SKILL.md`, references | Tests protect domain/data/API decisions and verification honesty. |
| `## 7. Integration Checklist` | merged | references | Domain/API/migration risk tests reflected. |
| `## 8. Reference Loading` | included | `SKILL.md` Reference Loading | Runtime references directly linked. |
| `## 9. 검증 방식` | included | `SKILL.md` Runtime Rules | Only executed tests may be claimed. |
| `ddd-implementation-standard.md` `## 1. 판단 순서` | merged | `SKILL.md` Routing | Domain decisions precede test assertions when unclear. |
| `## 2. 하위 도메인별 구현 강도` | included | `coverage-mutation.md` | Test level remains proportional to domain complexity. |
| `## 3. 바운디드 컨텍스트와 언어` / `## 4. 애그리거트와 불변식` | delegated-to-other-skill | `architecture-ddd` | DDD modeling routes away; clarified invariants become tests. |
| `## 5. Domain Events` / `## 6. Application Service와 Domain Service` | delegated-to-other-skill | `architecture-ddd`, implementation skills | Event/service ownership is not test implementation. |
| `## 7. Django ORM 매핑` / `## 8. Repository와 Transaction` / `## 9. API 매핑` | merged | `coverage-mutation.md`, `SKILL.md` | ORM/transaction/API contracts are tested here; implementation belongs elsewhere. |
| `## 10. Python 매핑` | delegated-to-other-skill | `implementation-python` | Python typing routes away. |
| `## 11. 테스트 매핑` | included | `SKILL.md`, references | Domain unit, fake repository, ORM/transaction integration, Ninja TestClient, and mock boundaries included. |
| `validation-plan.md` `## 1. 검증 원칙` | included | `SKILL.md` | Real executed validation only. |
| `## 2. 대표 시나리오` / `### 쿠폰 정책 TDD` | delegated-to-other-skill | `implementation-tdd`, this skill | TDD sequence routes to TDD; pytest files/cases are supported here. |
| `## 3. 평가 항목` | merged | `SKILL.md`, references | Behavior-focused tests, API contracts, and verification honesty reflected. |
| `## 4. Skill Folder 검증` | included | validation commands | Generated skill folder was checked with the final validator. |

## Validation Scenario Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `validation-plan.md` `### 주문 생성 API` | included | `SKILL.md`, `coverage-mutation.md`, `test-doubles.md` | Domain state, API contract, idempotency, risky write, concurrency, and integration/API tests are test-skill responsibilities after domain/API/DB contracts are clear. |
| `### 쿠폰 정책 TDD` | delegated-to-other-skill | `implementation-tdd`, this skill | TDD owns sequencing; this skill owns concrete pytest cases and boundary assertions. |
| `### DRF to Django Ninja 전환` | included | `SKILL.md`, `coverage-mutation.md` | Django Ninja `TestClient`, API contract tests, compatibility checks, and no greenfield DRF standard are supported; conversion implementation routes to Ninja skill. |
| `### Fat Model 리뷰`, `### View Logic 리뷰` | delegated-to-other-skill | `implementation-cleancode`, `architecture-ddd`, this skill | Review/refactor decisions route away; this skill supports behavior-preservation or adapter/usecase tests when assigned. |
| `### 운영 마이그레이션`, `### 트랜잭션과 동시성` | included | `SKILL.md`, `coverage-mutation.md` | Migration, transaction, isolation, idempotency, and concurrency assertions are covered after architecture/DB decisions are clear. |
| `### Django Web` | delegated-to-other-skill | `implementation-django-web`, this skill | Web/template implementation routes to web skill; render/browser or CSRF behavior tests are supported when assigned. |
| `### Python Typing` | delegated-to-other-skill | `implementation-python` | Typecheck/runtime typing choices route to Python skill; this skill can test behavior around them only when needed. |
| `### Architecture Pattern Selection` | delegated-to-other-skill | `architecture-implementation-patterns` | Pattern choice routes away; tests verify selected behavior, seams, or contracts afterward. |
| `### Negative Case: 단순 필드 rename`, `### Negative Case: 짧은 설명` | included | `SKILL.md` Routing | Small assertion, fixture, import ordering, typo, pytest command, or short explanation stays direct without DDD/workflow ceremony. |
| `### Negative Case: false subagent claim` | included | `SKILL.md` Runtime Rules | Runtime forbids claiming tests, coverage, mutation checks, or subagent reviews that were not actually run. |

## Test Reference Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `implementation-test/final.md` `## 목차` | omitted | n/a | Navigation only. |
| `## 1. 테스트 전략과 피라미드` | included | `coverage-mutation.md` | Test level strategy and cost trade-offs included. |
| `### 1.1 Martin Fowler의 테스트 피라미드` | included | `coverage-mutation.md` | Unit/integration/e2e proportions and regression guidance reflected. |
| `### 1.2 Google의 SMURF 프레임워크` | included | `coverage-mutation.md` | Speed, maintainability, utilization, reliability, fidelity trade-offs included. |
| `### 1.3 Google의 테스트 크기 분류` | included | `coverage-mutation.md` | Small/medium/large resource-use framing included. |
| `## 2. 테스트 더블 분류 체계` | included | `test-doubles.md` | Dummy, stub, spy, mock, fake selection included. |
| `## 3. pytest 기본 구조와 Fixture` | included | `pytest-fixtures.md` | Test functions/classes, fixtures, assertions, parametrization, and commands included. |
| `### 3.1 pytest 기본 구조` | included | `pytest-fixtures.md` | Plain functions and small `Test*` classes covered. |
| `### 3.2 Fixture` | included | `pytest-fixtures.md` | Fixture setup/teardown and scope guidance covered. |
| `### 3.3 xUnit 패턴과 pytest 매핑` | merged | `pytest-fixtures.md` | pytest fixture equivalents summarized; xUnit details omitted as historical mapping. |
| `### 3.4 단언(Assertion)` | included | `pytest-fixtures.md` | assert, raises, approx, automated pass/fail covered. |
| `### 3.5 예외 테스트` | included | `pytest-fixtures.md` | `pytest.raises` with match covered. |
| `### 3.6 파라미터화 테스트` | included | `pytest-fixtures.md` | `pytest.mark.parametrize` included. |
| `### 3.7 conftest.py를 활용한 공유 픽스처` | included | `pytest-fixtures.md` | Shared/nested `conftest.py` guidance included. |
| `### 3.8 monkeypatch를 활용한 환경 격리` | included | `pytest-fixtures.md`, `test-doubles.md` | Environment isolation and time-tool caveat included. |
| `### 3.9 tmp_path를 활용한 파일 테스트` | included | `pytest-fixtures.md` | Filesystem isolation included. |
| `### 3.10 전체 테스트 실행` | included | `pytest-fixtures.md` | Common pytest commands included. |
| `## 4. pytest 심화 설정` | included | `pytest-fixtures.md` | Strict markers/config, test discovery, and `conftest.py` hierarchy covered. |
| `### 4.1 pyproject.toml 종합 설정` | merged | `pytest-fixtures.md` | Configuration concerns summarized without copying full TOML. |
| `### 4.2 conftest.py 계층 구조` | included | `pytest-fixtures.md` | Localized fixture hierarchy covered. |
| `## 5. pytest 마커 시스템` | included | `pytest-fixtures.md` | Built-in/custom markers and selection covered. |
| `### 5.1 내장 마커: skip, skipif, xfail` | included | `pytest-fixtures.md` | skip/skipif/xfail use and strictness covered. |
| `### 5.2 커스텀 마커와 마커 활용 패턴` | included | `pytest-fixtures.md` | Custom marker registration and execution covered. |
| `### 5.3 마커에서 fixture로 데이터 전달` | included | `pytest-fixtures.md` | Marker arguments via `request.node.get_closest_marker` covered as rare advanced pattern. |
| `## 6. pytest 플러그인 생태계` | included | `pytest-fixtures.md`, `coverage-mutation.md` | xdist, async, coverage, random, timeout reflected. |
| `### 6.1 pytest-xdist` | included | `pytest-fixtures.md` | Parallel test caveat included. |
| `### 6.2 pytest-asyncio` | included | `pytest-fixtures.md` | asyncio modes and async test support included. |
| `### 6.3 pytest-cov` | included | `pytest-fixtures.md`, `coverage-mutation.md` | `pytest --cov`, reports, fail-under, branch coverage, and caveats covered. |
| `### 6.4 pytest-randomly` | included | `pytest-fixtures.md`, `coverage-mutation.md` | Order dependence and seed reporting included. |
| `### 6.5 pytest-timeout` | included | `pytest-fixtures.md` | Hanging test guidance included. |
| `## 7. Mock과 테스트 더블 실전` | included | `test-doubles.md` | Verification priority and concrete mock rules included. |
| `### 7.1 검증 방식 우선순위` | included | `test-doubles.md`, `SKILL.md` | Output/state/communication priority included. |
| `### 7.2 Mock 기본 사용법` | included | `test-doubles.md` | spec/autospec, return values, exceptions, ANY, calls covered. |
| `### 7.3 의존 관계 캡슐화로 모킹을 쉽게 만들기` | included | `test-doubles.md` | Adapter seam/dependency injection guidance included. |
| `### 7.4 PropertyMock` | included | `test-doubles.md` | PropertyMock sparing-use guidance included. |
| `### 7.5 AsyncMock` | included | `test-doubles.md` | AsyncMock and awaited assertions included. |
| `### 7.6 seal()` | included | `test-doubles.md` | Sealed mock guidance included. |
| `### 7.7 side_effect 고급 활용` | included | `test-doubles.md` | Errors, retries, and input-dependent behavior included. |
| `## 8. Property-Based Testing (Hypothesis)` | included | `factories-property-tests.md` | Hypothesis purpose and strategy use included. |
| `### 8.1 기본 사용법` | included | `factories-property-tests.md` | Invariant/property use included. |
| `### 8.2 전략 조합` | included | `factories-property-tests.md` | Strategy constraints and composition included. |
| `### 8.3 @example` | included | `factories-property-tests.md` | Business-critical boundary examples included. |
| `### 8.4 settings로 실행 제어` | included | `factories-property-tests.md` | Reasoned settings tuning included. |
| `### 8.5 Stateful Testing` | included | `factories-property-tests.md` | Sequence tests and reference model guidance included. |
| `## 9. 테스트 데이터 팩토리` | included | `factories-property-tests.md` | factory_boy and Faker selection included. |
| `### 9.1 기본 개념` | included | `factories-property-tests.md` | Factory use case included. |
| `### 9.2 기본 팩토리 정의` | included | `factories-property-tests.md` | Sequence, Faker, LazyAttribute, LazyFunction covered. |
| `### 9.3 관계 처리` | included | `factories-property-tests.md` | SubFactory and RelatedFactory covered. |
| `### 9.4 Trait` | included | `factories-property-tests.md` | Meaningful state traits covered. |
| `### 9.5 배치 생성과 재현성` | included | `factories-property-tests.md` | Batch and reseeding covered. |
| `### 9.6 SQLAlchemy / Django ORM 통합` | included | `factories-property-tests.md` | DjangoModelFactory, `django_get_or_create`, and SQLAlchemyModelFactory coverage included; Django remains the primary runtime target. |
| `## 10. 시간 모킹` | included | `test-doubles.md` | freezegun/time-machine choice included. |
| `### 10.1 freezegun` | included | `test-doubles.md` | Selective/PyPy-friendly time mocking included. |
| `### 10.2 time-machine` | included | `test-doubles.md` | CPython performance choice included. |
| `### 10.3 비교 및 선택 기준` | included | `test-doubles.md` | Selection criteria included. |
| `## 11. HTTP 모킹` | included | `test-doubles.md` | responses, aioresponses, socket-level fallback included. |
| `### 11.1 responses` | included | `test-doubles.md` | requests-based mocking included. |
| `### 11.2 aioresponses` | included | `test-doubles.md` | aiohttp async mocking included. |
| `### 11.3 HTTPretty` | included | `test-doubles.md` | Broad socket-level interceptor included only as fallback. |
| `## 12. Docker 기반 통합 테스트` | included | `coverage-mutation.md` | testcontainers strategy included. |
| `### 12.1 PostgreSQL 통합 테스트` | included | `coverage-mutation.md` | PostgreSQL fidelity and isolation covered. |
| `### 12.2 Redis 통합 테스트` | included | `coverage-mutation.md` | Redis integration cleanup covered generally. |
| `### 12.3 여러 서비스 동시 사용` | included | `coverage-mutation.md` | Multi-service large test guidance included. |
| `## 13. 커버리지 설정` | included | `coverage-mutation.md` | coverage.py configuration and commands covered. |
| `### 13.1 pyproject.toml 종합 설정` | merged | `coverage-mutation.md` | Coverage settings summarized without copying full TOML. |
| `### 13.2 활용 명령어` | included | `coverage-mutation.md` | coverage commands included. |
| `## 14. 멀티환경 테스트` | included | `coverage-mutation.md` | tox/nox selection included. |
| `### 14.1 tox` | included | `coverage-mutation.md` | Straightforward matrix use included. |
| `### 14.2 nox` | included | `coverage-mutation.md` | Python-coded session use included. |
| `### 14.3 tox vs nox 비교` | included | `coverage-mutation.md` | Selection criteria included. |
| `## 15. 테스트 코드 품질 원칙` | included | `coverage-mutation.md` | FIRST, AAA, and public-contract tests covered. |
| `### 15.1 FIRST 원칙` | included | `coverage-mutation.md` | Fast, independent, repeatable, self-validating, timely covered. |
| `### 15.2 AAA 패턴` | included | `coverage-mutation.md` | Arrange-Act-Assert and one Act guidance included. |
| `### 15.3 화이트박스 테스트를 피하라` | included | `coverage-mutation.md`, `SKILL.md` | Public behavior over private implementation included. |
| `## 16. 테스트 안티패턴` | included | `coverage-mutation.md` | Code-level and strategy-level smells summarized. |
| `### 16.1 코드 수준 안티패턴` | included | `coverage-mutation.md` | Weak assertions, excessive setup, unrelated asserts, shared state, over-mocking included. |
| `### 16.2 전략 수준 안티패턴` | included | `coverage-mutation.md` | Wrong test type, flaky tests, manual execution, coverage obsession included. |
| `## 17. Mutation Testing` | included | `coverage-mutation.md` | Mutation concept, use, and interpretation included. |
| `### 17.1 개념` | included | `coverage-mutation.md` | Tests-for-tests idea included. |
| `### 17.2 뮤테이션 종류` | included | `coverage-mutation.md` | Boundary/operator mutation risks summarized. |
| `### 17.3 mutmut 사용법` | merged | `coverage-mutation.md` | Tool use represented without long command list. |
| `### 17.4 결과 해석` | included | `coverage-mutation.md` | Survived mutant analysis included. |
| `### 17.5 뮤테이션 점수 목표` | included | `coverage-mutation.md` | Score as signal, not blind target, included. |
| `## 18. BDD pytest-bdd 구현` | included | `factories-property-tests.md` | Given-When-Then and pytest-bdd use guidance included. |
| `### 18.1 Given-When-Then` | included | `factories-property-tests.md` | Step responsibility included. |
| `### 18.2 pytest-bdd로 구현` | merged | `factories-property-tests.md` | Implementation pattern summarized; exact example omitted for brevity. |
| `## 19. 테스트 디버깅 기법` | included | `coverage-mutation.md` | pytest debugging commands included. |
| `### 19.1 pytest에서 디버거 진입` | included | `coverage-mutation.md` | `--pdb`, `--lf --pdb`, `-x --pdb`, `-k` covered. |
| `## 20. 참고 문헌` | omitted | n/a | Bibliography is source provenance, not runtime behavior. |
| `## 부록: 도구 설치 한눈에 보기` | omitted | n/a | Installation list is not runtime behavior; tools are referenced where needed. |

## Review Notes

- 2026-05-10 source self-review in the current evaluation loop found source-backed gaps in Korean trigger coverage, risky/composite workflow routing, broad workflow responsibility wording, validation scenario heading coverage, and stale review/rubric completion claims from an earlier draft. Runtime files and this crosswalk were updated.
- Independent source re-review by Carver found the crosswalk missing runtime-relevant `spec.md` child headings and `Risky Write Consistency Block` coverage; fixes were applied and re-review returned blocking 0, major 0, minor 0.
- Rubric review found one source-backed small-task boundary improvement for test-file import ordering; runtime routing was updated without copying evaluation-only private material. Independent rubric review by Carver returned blocking 0, major 0, minor 0 and no leakage risk.
- Runtime checks completed with positive, boundary/combined, and negative prompts through `codex debug prompt-input`; isolated read-only `codex exec` smoke ran in `/private/tmp/test-smoke` for Django Ninja API contract tests, risky DDD/API/test workflow, and import-order negative behavior. Validator, leakage check, cache sync, and source/cache diff completed for this skill.
