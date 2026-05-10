# Source Coverage Crosswalk: implementation-tdd

## Status

- Skill: `implementation-tdd`
- Runtime target: `dddjango/skills/implementation-tdd/`
- Source status: ready
- Runtime reference split: follows `workspace/docs/plugin-structure.md` without deviation
- Runtime references: `red-green-refactor.md`, `inside-out-outside-in.md`, `test-list.md`, `ai-assisted-tdd.md`
- Rubric status: not opened during draft; reserved for post-source-review verification

## Sources Used

- `workspace/docs/spec.md`
- `workspace/docs/plugin-structure.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/skill-hierarchy.md`
- `workspace/docs/skill-authoring.md`
- `workspace/docs/reference-index.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/workflow.md`
- `workspace/docs/validation-plan.md`
- `workspace/reference/implementation-tdd/reference/final.md`

## Authoring And Product Docs

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `plugin-structure.md` `## 1. 개발 위치` | included | runtime path | Runtime files live under plugin artifact because plugin runtime requires it. |
| `## 2. 목표 구조` / `## 2.1 Runtime 동기화 기준` | included | `dddjango/skills/implementation-tdd/` | Plugin-bundled structure used; no cache edits. |
| `## 3. Skill 파일 기준` | included | `SKILL.md` | Trigger, routing, references, and runtime rules only. |
| `## 4. Reference 파일 기준` | included | `references/*.md` | One-level references directly linked. |
| `## 5. Claude Code와 Codex 공통성` | included | `SKILL.md`, references | Shared skill name, responsibility, and verification rules preserved. |
| `## 6. 작성 순서` | included | this workflow | Docs/reference read before rubric review. |
| `## 7. Runtime Reference Split Plan` | included | four reference files | Exact split for `implementation-tdd` used. |
| `## 8. 금지 사항` | included | file tree | No README/changelog/install guide; no false validation claim. |
| `skill-authoring.md` `## 1. 작성 원칙` | included | `SKILL.md` | Trigger/routing and boundaries are in description/body. |
| `## 2. Frontmatter 입력 표` | included | `SKILL.md` description | TDD, failing test, Red-Green-Refactor signals included. |
| `## 3. Cross-Skill Precedence` | included | `SKILL.md` Routing | Domain/workflow precede TDD only when relevant. |
| `## 4. Agents Metadata Inputs` | included | `agents/openai.yaml` | Display name, short description, and default prompt align. |
| `reference-index.md` `## Architecture` | delegated-to-other-skill | `architecture-*` skills | Architecture source mapping outside TDD method. |
| `## Implementation` | included | references | TDD source reference used for runtime split. |
| `## Reference 사용 원칙` | included | references | Runtime references summarize source and avoid copying `final.md`. |
| `## Reference Gap` | omitted | n/a | This skill has dedicated source reference. |
| `## DRF Guardrail` | delegated-to-other-skill | `implementation-django-ninja` | API/DRF routing outside TDD skill. |
| `## Reference에서 도출한 제품 결정` | included | `SKILL.md`, references | TDD+pytest split and verification principles reflected. |

## Contracts, Workflow, And DDD Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill-contracts.md` `## architecture-ddd` | delegated-to-other-skill | `SKILL.md` Routing | Unclear domain rules route to DDD before tests. |
| `## architecture-implementation-patterns` | delegated-to-other-skill | `architecture-implementation-patterns` | Architecture pattern selection is outside TDD method. |
| `## architecture-db` / `## architecture-api` | delegated-to-other-skill | `SKILL.md` Routing, `architecture-db`, `architecture-api` | DB/API contract, transaction, locking, rollout, and consistency decisions route away before test expectations are locked. |
| `## implementation-django` / `## implementation-django-ninja` / `## implementation-django-web` | delegated-to-other-skill | `SKILL.md` Routing | Framework implementation follows once tests clarify target behavior. |
| `## implementation-python` / `## implementation-cleancode` | delegated-to-other-skill | `implementation-python`, `implementation-cleancode` | Python/refactor details route away unless part of Refactor step. |
| `## implementation-tdd` | included | `SKILL.md`, references | Test list, failing tests, small implementation, refactor checkpoints, and Test Agent file ownership covered. |
| `## implementation-test` | delegated-to-other-skill | `implementation-test` | Fixture/mock/factory/tool details route away. |
| `## workflow-dddjango-subagents` | delegated-to-other-skill | `SKILL.md` Routing | Composite, risky, subagent, and role-decomposed Django work routes to workflow. |
| `## 공통 필수 출력` | delegated-to-other-skill | `workflow-dddjango-subagents`, implementation skills | Risky write consistency is not TDD-specific, though tests should cover it. |
| `skill-hierarchy.md` `## Skill Hierarchy` | included | `SKILL.md` Routing | TDD is a bottom method skill and can combine with implementation/test skills. |
| `workflow.md` `## 1. 기본 흐름` | merged | `SKILL.md` Routing | Domain ambiguity routes before tests; test strategy follows domain/API decisions. |
| `## 2. 작업 유형별 흐름` | included | `SKILL.md` Routing | Simple TDD work direct; composite/risky work routes to workflow. |
| `## 3. 역할 분해` | delegated-to-other-skill | `workflow-dddjango-subagents` | Test Agent role belongs to workflow skill. |
| `## 4. Sequential Fallback` / `## 5. Handoff Contract` | delegated-to-other-skill | `workflow-dddjango-subagents` | Workflow orchestration belongs elsewhere. |
| `## 6. 통합 우선순위` | merged | `SKILL.md`, references | Tests protect domain/data/API decisions and verification honesty. |
| `## 7. Integration Checklist` | merged | `SKILL.md`, references | Tests and verification criteria reflected. |
| `## 8. Reference Loading` | included | `SKILL.md` Reference Loading | Runtime references directly linked. |
| `## 9. 검증 방식` | included | `SKILL.md` Runtime Rules | Only executed tests may be claimed red/green. |
| `ddd-implementation-standard.md` `## 1. 판단 순서` | merged | `SKILL.md` Routing | Domain decisions precede test design when unclear. |
| `## 2. 하위 도메인별 구현 강도` | included | `SKILL.md`, `test-list.md` | Core domain emphasizes test-first; simple work stays proportional. |
| `## 3. 바운디드 컨텍스트와 언어` / `## 4. 애그리거트와 불변식` | delegated-to-other-skill | `architecture-ddd` | DDD modeling routes away; TDD captures clarified rules as tests. |
| `## 5. Domain Events` / `## 6. Application Service와 Domain Service` | delegated-to-other-skill | `architecture-ddd`, implementation skills | Event/service ownership is not TDD method. |
| `## 7. Django ORM 매핑` / `## 8. Repository와 Transaction` / `## 9. API 매핑` | delegated-to-other-skill | implementation/architecture skills | Framework/DB/API implementation routes away. |
| `## 10. Python 매핑` | delegated-to-other-skill | `implementation-python` | Python typing routes away. |
| `## 11. 테스트 매핑` | included | `SKILL.md`, references | Domain, application, ORM, and API test mapping drives test list; mechanics delegated. |
| `validation-plan.md` `## 1. 검증 원칙` | included | `SKILL.md` | Real executed validation only. |
| `## 2. 대표 시나리오` / `### 쿠폰 정책 TDD` | included | `SKILL.md`, references | Test list, failing tests, boundary cases, Red/Green/Refactor included. |
| `## 3. 평가 항목` | merged | `SKILL.md`, references | Domain/API tests and verification reflected. |
| `## 4. Skill Folder 검증` | included | validation commands | Generated skill folder was checked with the final validator. |

## Validation Scenario Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `validation-plan.md` `### 주문 생성 API` | delegated-to-other-skill | `workflow-dddjango-subagents`, `architecture-ddd`, `architecture-api`, `architecture-db`, `implementation-django-ninja`, `implementation-test` | Composite API/domain/DB/test work routes through workflow and adjacent skills; TDD can own test-list/Red-Green-Refactor portions after contracts are clear. |
| `### 쿠폰 정책 TDD` | included | `SKILL.md`, `test-list.md`, `red-green-refactor.md`, `inside-out-outside-in.md` | Coupon policy TDD is this skill's primary validation scenario: test list, failing tests, boundary cases, and Red/Green/Refactor must be explicit. |
| `### DRF to Django Ninja 전환` | delegated-to-other-skill | `implementation-django-ninja`, `implementation-test` | Migration/API implementation and API test mechanics are not TDD-method primary work. |
| `### Fat Model 리뷰`, `### View Logic 리뷰` | delegated-to-other-skill | `implementation-cleancode`, `architecture-ddd` | Review/refactor responsibility belongs to clean-code/DDD; TDD may supply characterization tests only when asked. |
| `### 운영 마이그레이션`, `### 트랜잭션과 동시성` | delegated-to-other-skill | `architecture-db`, `implementation-django`, `implementation-test` | Migration, transaction, locking, and concurrency mechanics must be decided outside TDD before writing stable expectations. |
| `### Django Web` | delegated-to-other-skill | `implementation-django-web`, `implementation-test` | Template/static/web implementation and browser/render test mechanics route away. |
| `### Python Typing` | delegated-to-other-skill | `implementation-python` | Python typing implementation is not TDD-method work. |
| `### Architecture Pattern Selection` | delegated-to-other-skill | `architecture-implementation-patterns` | Pattern choice routes away; tests can validate chosen behavior afterward. |
| `### Negative Case: 단순 필드 rename`, `### Negative Case: 짧은 설명` | included | `SKILL.md` Routing | Tiny explanation or simple change should not trigger full workflow or forced TDD ceremony. |
| `### Negative Case: false subagent claim` | included | `SKILL.md`, `ai-assisted-tdd.md` | Runtime forbids claiming tests or subagent review that were not actually executed. |

## TDD Reference Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `implementation-tdd/final.md` `## 1. TDD 핵심 철학` | included | `red-green-refactor.md`, `ai-assisted-tdd.md` | Tests as feedback/courage and working clean code reflected. |
| `### 1.1 TDD의 목표` / `### 1.2 TDD를 해야 하는 이유` | included | `red-green-refactor.md`, `ai-assisted-tdd.md` | Working clean code, feedback interval, and limits reflected. |
| `## 2. TDD 사이클` | included | `red-green-refactor.md`, `SKILL.md` | Red, Green, Refactor cycle and execution honesty included. |
| `### 2.1 기본 사이클` / `### 2.2 pytest로 보는 TDD 사이클` | included | `red-green-refactor.md`, `SKILL.md` | Red/Green/Refactor sequence and not-run reporting included; pytest mechanics delegated. |
| `## 3. TDD 학파 비교` | included | `inside-out-outside-in.md` | Classic/London, state/behavior, Inside-Out/Outside-In selection included. |
| `### 3.1 두 학파의 기원과 핵심 차이` | included | `inside-out-outside-in.md` | Classic vs London selection summarized. |
| `### 3.2 상태 검증 vs 행위 검증` | included | `inside-out-outside-in.md` | Output/state vs behavior verification priority included. |
| `### 3.3 Inside-Out vs Outside-In TDD` | included | `inside-out-outside-in.md` | Approach selection included. |
| `### 3.4 실전 권고: 상황별 선택` | included | `inside-out-outside-in.md` | Pure domain vs external collaboration choice included. |
| `## 4. 좋은 단위 테스트의 4대 특성` | included | `test-list.md`, `inside-out-outside-in.md` | Regression protection, refactoring resistance, fast feedback, maintainability included. |
| `### 4.1 네 가지 기둥` / `### 4.2 회귀 방지의 위상` | included | `test-list.md` | Quality balance and regression tests for bugs included. |
| `### 4.3 리팩토링 내성` / `### 4.4 CAP 정리와의 유사성` | included | `inside-out-outside-in.md`, `test-list.md` | Refactoring resistance and trade-off included. |
| `### 4.5 세 가지 테스트 스타일` / `### 4.6 테스트 품질 3대 속성` | included | `inside-out-outside-in.md`, `test-list.md` | Output/state/communication priority and trust/readability included. |
| `## 5. 빨간 막대 패턴` | included | `test-list.md` | Test list, next test, starting test, explanation test included. |
| `### 5.1 테스트 목록` | included | `test-list.md`, `SKILL.md` | Test list before implementation included. |
| `### 5.2 한 단계 테스트` / `### 5.3 시작 테스트` / `### 5.4 설명 테스트` | included | `test-list.md` | Next teachable test, simple start, and tests as explanation included. |
| `## 6. 초록 막대 패턴` | included | `red-green-refactor.md` | Fake it, triangulation, obvious implementation included. |
| `### 6.1 가짜로 구현하기` / `### 6.2 삼각측량` / `### 6.3 명백한 구현` | included | `red-green-refactor.md` | Green strategies included. |
| `## 7. 테스팅 패턴` | included | `test-list.md`, `inside-out-outside-in.md` | AAA, test data, names, isolation, mock role guidance included. |
| `### 7.1 테스트 격리` | included | `test-list.md` | Independent tests, execution-order independence, and shared-state removal included. |
| `### 7.2 AAA 패턴` | included | `test-list.md` | Arrange-Act-Assert and Assert First reflected. |
| `### 7.3 테스트 데이터` / `### 7.4 명백한 데이터` | included | `test-list.md` | Meaningful data and visible expected relationship included. |
| `### 7.5 테스트 명명 규칙` | included | `test-list.md` | Unit/condition/expected behavior naming included. |
| `### 7.6 Mock 객체의 올바른 사용` | included | `inside-out-outside-in.md` | Mock external roles, not domain internals. |
| `### 7.7 크래시 테스트 더미` / `### 7.8 셀프 션트` / `### 7.9 로그 문자열` | delegated-to-other-skill | `implementation-test` | Detailed double/test pattern mechanics belong to test skill. |
| `### 7.10 깨진 테스트 / 깨끗한 체크인` | merged | `red-green-refactor.md`, `ai-assisted-tdd.md` | Honest red/green status and team-safe reporting reflected. |
| `## 8. 테스트 더블 분류 체계` | delegated-to-other-skill | `implementation-test` | Source delegates double taxonomy to test skill. |
| `## 9. Outside-In TDD와 이중 루프` | included | `inside-out-outside-in.md` | Double loop, walking skeleton, mock roles, Tell-Don't-Ask included. |
| `### 9.1 이중 루프 TDD` | included | `inside-out-outside-in.md` | Outer acceptance loop and inner unit loop included. |
| `### 9.2 Walking Skeleton` | included | `inside-out-outside-in.md` | End-to-end thin slice guidance included. |
| `### 9.3 Mock Roles, Not Objects` | included | `inside-out-outside-in.md` | Mock roles, not implementation objects, included. |
| `### 9.4 Tell, Don't Ask 원칙` | merged | `inside-out-outside-in.md` | External collaboration and domain behavior boundary reflected. |
| `## 10. 디자인 패턴과 TDD` | merged | `inside-out-outside-in.md`, `red-green-refactor.md` | Value object/factory/null-object pattern use covered at approach level; detailed implementation delegated. |
| `### 10.1 값 객체` / `### 10.2 널 객체` / `### 10.3 팩토리 메서드` | delegated-to-other-skill | `implementation-python`, `implementation-cleancode`, `architecture-ddd` | Design pattern implementation belongs to implementation/architecture skills; tests can drive use. |
| `## 11. 리팩토링 패턴` | included | `red-green-refactor.md` | Refactor while green, small behavior-preserving steps included. |
| `### 11.1`-`### 11.8 리팩토링 패턴` | merged | `red-green-refactor.md`, `implementation-cleancode` | TDD keeps refactoring green; detailed refactor technique belongs to clean-code. |
| `## 12. 테스트 냄새 카탈로그` | included | `test-list.md` | Test smell prevention included. |
| `### 12.1 행위 냄새` / `### 12.2 코드 냄새` | included | `test-list.md` | Erratic, fragile, obscure, conditional, and eager test smells included. |
| `## 13. 레거시 코드 다루기` | delegated-to-other-skill | `implementation-cleancode` | Source points legacy code to clean-code reference. |
| `## 14. Property-Based Testing` | delegated-to-other-skill | `implementation-test` | Source delegates property-based testing. |
| `## 15. Mutation Testing` | delegated-to-other-skill | `implementation-test` | Source delegates mutation testing. |
| `## 16. BDD`, `### 16.1 TDD와 BDD의 관계` | delegated-to-other-skill | `implementation-test` | pytest-bdd implementation details are delegated; BDD relation can inform examples but is not central TDD-method runtime behavior. |
| `## 17. TDD와 AI 코딩의 관계` | included | `ai-assisted-tdd.md` | Plan/Red/Green/Refactor/Validate and AI false-claim prevention included. |
| `### 17.1 TDD as Prompt Engineering` / `### 17.2 AI 보조 TDD 워크플로우` | included | `ai-assisted-tdd.md` | Tests as executable prompts and AI-assisted loop included. |
| `### 17.3 TDD가 AI 코딩에서 더 중요한 이유` | included | `ai-assisted-tdd.md` | AI hallucination and intent risks reflected. |
| `### 17.4 Test-Driven AI Development 5단계` | included | `ai-assisted-tdd.md` | Plan, Red, Green, Refactor, Validate included. |
| `## 18. Python 테스트 생태계 심화` | delegated-to-other-skill | `implementation-test` | Source delegates Python test tooling. |
| `## 참고 문헌` | omitted | n/a | Bibliography is source provenance, not runtime behavior. |

## Review Notes

- 2026-05-10 source self-review in the current evaluation loop found source-backed gaps in Korean trigger coverage, API/DB architecture routing, workflow over-routing via broad responsibility wording, validation scenario heading coverage, test isolation guidance, mock-role/TDD boundary wording, and stale review/rubric completion claims from an earlier draft. Runtime files and this crosswalk were updated.
- 2026-05-10 independent source re-review by Kierkegaard returned blocking 0, major 0, minor 0 after fixes.
- 2026-05-10 rubric review ran after source review. No new source-backed runtime issues were found. Final rubric finding counts: blocking 0, major 0, minor 0.
- 2026-05-10 runtime checks completed: `codex debug prompt-input` positive/boundary/negative metadata exposure, isolated read-only `codex exec` positive coupon-policy TDD planning, composite order API workflow/TDD boundary, and README typo negative behavior. Validator, leakage grep, cache sync, and source/cache diff passed; durable results were recorded in completion notes and commit history.
