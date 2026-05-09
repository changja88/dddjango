# Source Coverage Crosswalk: implementation-cleancode

## Status

- Skill: `implementation-cleancode`
- Runtime target: `dddjango/skills/implementation-cleancode/`
- Source status: ready
- Runtime reference split: follows `workspace/docs/plugin-structure.md` without deviation
- Runtime references: `responsibility.md`, `naming-functions.md`, `encapsulation-abstraction.md`, `legacy-review.md`
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
- `workspace/reference/implementation-cleancode/reference/final.md`

## Authoring And Product Docs

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill_goal_instructions.md` `## 범위` | included | runtime path, this crosswalk | Plugin-bundled target and crosswalk location followed. |
| `## 실행 규칙` | included | this workflow | One skill at a time; rubrics not used during draft. |
| `## 구현 순서` | included | plan order | This follows `implementation-python`. |
| `## Skill별 작성 루프` | included | this crosswalk, review notes | Source scope, draft, review, rubric sequencing tracked. |
| `## SKILL.md 작성 규칙` | included | `SKILL.md` | Frontmatter has only name/description; body is short and procedural. |
| `## Runtime Reference 작성 규칙` | included | `references/*.md` | Four one-level references summarize source rather than copying it. |
| `## Agents Metadata 작성 규칙` | included | `agents/openai.yaml` | Metadata aligns with source and runtime skill. |
| `## 한국어 사용자 기준` | included | `SKILL.md` description | Korean triggers for review/refactor/responsibility included. |
| `## Provisional Skill 처리` | omitted | n/a | This skill has dedicated source reference and is not provisional. |
| `## Cross-Skill Routing 기준` | included | `SKILL.md` Routing | Adjacent DDD, implementation, test, and workflow boundaries included. |
| `## Review 기준` | included | Review Notes | Review types and findings tracked. |
| `## Completed 조건` | included | Review Notes, validation report | Completion requires zero remaining blocking/major/minor findings. |
| `## 검증` | included | final validation report | Only executed validation is reported. |
| `## 완료 보고` | included | final response | Required report fields will be included. |
| `## Goal Objective Template` | omitted | n/a | Goal prompt authoring content is not runtime behavior. |
| `spec.md` `## 관련 문서` | included | Sources Used | Linked product docs are covered. |
| `## 1. 목표` | merged | `SKILL.md` Routing | DDD-first, simple-vs-complex, and workflow delegation reflected. |
| `## 2. 설계 원칙` | merged | `SKILL.md`, references | Domain-first, adapter boundary, and test evidence reflected. |
| `## 3. 스킬 종류` | included | `SKILL.md`, references | Clean-code responsibility and adjacent skill boundaries included. |
| `## 4. 산출물 기준` | included | `SKILL.md`, references | Review findings, quality risks, behavior preservation, and verification included. |
| `plugin-structure.md` `## 1. 개발 위치` | included | runtime path | Runtime files live under plugin artifact because plugin runtime requires it. |
| `## 2. 목표 구조` / `## 2.1 Runtime 동기화 기준` | included | `dddjango/skills/implementation-cleancode/` | Plugin-bundled structure used; no cache edits. |
| `## 3. Skill 파일 기준` | included | `SKILL.md` | Trigger, routing, references, and runtime rules only. |
| `## 4. Reference 파일 기준` | included | `references/*.md` | One-level references directly linked. |
| `## 5. Claude Code와 Codex 공통성` | included | `SKILL.md`, references | Shared skill name, responsibility, and verification rules preserved. |
| `## 6. 작성 순서` | included | this workflow | Docs/reference read before rubric review. |
| `## 7. Runtime Reference Split Plan` | included | four reference files | Exact split for `implementation-cleancode` used. |
| `## 8. 금지 사항` | included | file tree | No README/changelog/install guide; no false validation claim. |
| `skill-authoring.md` `## 1. 작성 원칙` | included | `SKILL.md` | Trigger/routing and boundaries are in description/body. |
| `## 2. Frontmatter 입력 표` | included | `SKILL.md` description | Clean code/review/refactoring signals included. |
| `## 3. Cross-Skill Precedence` | included | `SKILL.md` Routing | Domain/workflow precede clean-code judgment only when relevant. |
| `## 4. Agents Metadata Inputs` | included | `agents/openai.yaml` | Display name, short description, and default prompt align. |
| `reference-index.md` `## Architecture` | delegated-to-other-skill | `architecture-*` skills | Architecture source mapping outside clean-code implementation. |
| `## Implementation` | included | references | Clean-code source reference used for runtime split. |
| `## Reference 사용 원칙` | included | references | Runtime references summarize source and avoid copying `final.md`. |
| `## Reference Gap` | omitted | n/a | This skill has dedicated source reference. |
| `## DRF Guardrail` | delegated-to-other-skill | `implementation-django-ninja` | API/DRF routing outside clean-code skill. |
| `## Reference에서 도출한 제품 결정` | included | `SKILL.md`, references | Implementation boundaries and verification principles reflected. |

## Contracts, Workflow, And DDD Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill-contracts.md` `## architecture-ddd` | delegated-to-other-skill | `SKILL.md` Routing | Domain modeling routes to DDD. |
| `## architecture-implementation-patterns` | delegated-to-other-skill | `architecture-implementation-patterns` | Architecture patterns are outside clean-code review unless already selected. |
| `## architecture-db` | delegated-to-other-skill | `architecture-db` | DB schema/transaction design routes away. |
| `## architecture-api` | delegated-to-other-skill | `architecture-api` | REST contract design routes away. |
| `## implementation-django` | delegated-to-other-skill | `SKILL.md` Routing | ORM/migration/settings route to Django skill. |
| `## implementation-django-ninja` | delegated-to-other-skill | `SKILL.md` Routing | Router/Schema/API work routes to Ninja skill. |
| `## implementation-django-web` | delegated-to-other-skill | `implementation-django-web` | Template/static work routes away. |
| `## implementation-python` | delegated-to-other-skill | `SKILL.md` Routing | Python typing details route to Python skill. |
| `## implementation-tdd` / `## implementation-test` | delegated-to-other-skill | `implementation-tdd`, `implementation-test` | TDD/test mechanics route away. |
| `## implementation-cleancode` | included | `SKILL.md`, references | Responsibility, naming, encapsulation, abstraction, errors, duplication, legacy review, and review/edit boundary covered. |
| `## workflow-dddjango-subagents` | delegated-to-other-skill | `SKILL.md` Routing | Composite/subagent work routes to workflow. |
| `## 공통 필수 출력` | delegated-to-other-skill | `workflow-dddjango-subagents`, implementation skills | Risky write consistency is not clean-code specific. |
| `skill-hierarchy.md` `## Skill Hierarchy` | included | `SKILL.md` Routing | Quality skill can combine with lower implementation skills but avoids over-application. |
| `workflow.md` `## 1. 기본 흐름` | merged | `SKILL.md` Routing | Domain ambiguity routes before quality judgment. |
| `## 2. 작업 유형별 흐름` | included | `SKILL.md` Routing | Simple clean-code work direct; composite work routes to workflow. |
| `## 3. 역할 분해` | delegated-to-other-skill | `workflow-dddjango-subagents` | Review Agent role belongs to workflow skill. |
| `## 4. Sequential Fallback` / `## 5. Handoff Contract` | delegated-to-other-skill | `workflow-dddjango-subagents` | Workflow orchestration belongs elsewhere. |
| `## 6. 통합 우선순위` | merged | `SKILL.md`, references | Domain invariants outrank style preferences. |
| `## 7. Integration Checklist` | merged | `SKILL.md`, references | Implementation mapping, tests, and review findings reflected. |
| `## 8. Reference Loading` | included | `SKILL.md` Reference Loading | Runtime references directly linked. |
| `## 9. 검증 방식` | included | `SKILL.md` Runtime Rules | Only executed verification may be claimed. |
| `ddd-implementation-standard.md` `## 1. 판단 순서` | merged | `SKILL.md` Routing | Domain decisions precede clean-code judgment when unclear. |
| `## 2. 하위 도메인별 구현 강도` | merged | `SKILL.md` | Simple work stays simple; complex domain may need DDD. |
| `## 3. 바운디드 컨텍스트와 언어` | delegated-to-other-skill | `architecture-ddd` | Strategic modeling responsibility. |
| `## 4. 애그리거트와 불변식` | merged | `responsibility.md`, `encapsulation-abstraction.md` | Domain rules should remain readable and protected. |
| `## 5. Domain Events` | delegated-to-other-skill | `architecture-ddd`, `implementation-django` | Event timing is not clean-code specific. |
| `## 6. Application Service와 Domain Service` | merged | `responsibility.md`, `encapsulation-abstraction.md` | Service responsibility and boundary readability reflected. |
| `## 7. Django ORM 매핑` / `## 8. Repository와 Transaction` | delegated-to-other-skill | `implementation-django`, `architecture-db` | ORM/transaction design routes away. |
| `## 9. API 매핑` | delegated-to-other-skill | `implementation-django-ninja` | API adapter work routes away. |
| `## 10. Python 매핑` | delegated-to-other-skill | `implementation-python` | Python-specific types route away. |
| `## 11. 테스트 매핑` | delegated-to-other-skill | `implementation-test` | Test design routes away; behavior preservation noted. |
| `validation-plan.md` `## 1. 검증 원칙` | included | `SKILL.md` | Real executed validation only. |
| `## 2. 대표 시나리오` | included | `SKILL.md`, references | Fat Model and View Logic review scenarios covered by responsibility/adapter boundary rules. |
| `## 3. 평가 항목` | merged | `SKILL.md`, references | Implementation pragmatism, maintainability, workflow fit, and verification reflected. |
| `## 4. Skill Folder 검증` | included | validation commands | Generated skill folder will be checked. |

## Clean Code Reference Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `implementation-cleancode/final.md` `## 목차` | omitted | n/a | Navigational table of contents, not runtime behavior. |
| `## 1. 클린 코드란 무엇인가` | included | `responsibility.md` | Communication, simplicity, flexibility, and complexity management included. |
| `## 2. 이름 짓기` | included | `naming-functions.md` | Intent, consistency, boolean/collection/count/index naming covered. |
| `## 3. 함수와 메서드 설계` | included | `naming-functions.md` | One abstraction level, argument count, flag args, command/query split, side effects covered. |
| `## 4. 주석과 문서화` | included | `responsibility.md`, `naming-functions.md` | Why-comments and public-interface docstrings covered. |
| `## 5. 코드 형식과 구조` | merged | `naming-functions.md` | Follow project formatter/lint rather than local style invention. |
| `## 6. 추상화와 캡슐화` | included | `encapsulation-abstraction.md` | Information hiding, state encapsulation, interface/implementation separation covered. |
| `## 7. 깊은 모듈 설계` | included | `encapsulation-abstraction.md` | Deep modules, shallow wrappers, pass-through red flags covered. |
| `## 8. 객체 설계 원칙` | included | `encapsulation-abstraction.md` | Tell-Don't-Ask, data/logic locality, behavior-first design, composition covered. |
| `## 9. SOLID 원칙` | included | `encapsulation-abstraction.md` | SRP/OCP/LSP/ISP/DIP included as judgment, not ceremony. |
| `## 10. 디자인 패턴` | merged | `encapsulation-abstraction.md`, `legacy-review.md` | Patterns only when they reduce real complexity; pattern selection otherwise delegated. |
| `## 11. 상태 관리` | included | `encapsulation-abstraction.md` | Value objects, state access, and lifetime concerns reflected. |
| `## 12. 오류 처리` | included | `encapsulation-abstraction.md` | Error-state removal, exceptions, guard clauses, contracts covered. |
| `## 13. 중복 제거와 DRY` | included | `encapsulation-abstraction.md`, `SKILL.md` | DRY as knowledge duplication, not mechanical line matching. |
| `## 14. 협력과 의존성 관리` | included | `responsibility.md`, `encapsulation-abstraction.md` | Roles, cohesion/coupling, composition, reversibility covered. |
| `## 15. 리팩토링` | included | `legacy-review.md` | Smells and major refactoring techniques covered. |
| `## 16. 레거시 코드 다루기` | included | `legacy-review.md` | Characterization tests, seams, sprout/wrap methods, residual risk covered. |
| `## 17. 설계 철학과 프로세스` | merged | `SKILL.md`, `legacy-review.md` | Small steps, behavior preservation, YAGNI, pattern non-absolutism reflected. |
| `## 18. Python 관용구와 스타일` | delegated-to-other-skill | `implementation-python` | Source points Python specifics to Python reference. |
| `## 핵심 요약 체크리스트` | merged | all references | Checklist principles distributed across runtime split. |

## Review Notes

- Source self-review: local review found 1 minor review/edit boundary gap; fixed; remaining blocking/major/minor findings 0.
- Skill-creator/writing-skills review: no extraneous files, direct reference links, concise `SKILL.md`, and frontmatter length under 1024; remaining blocking/major/minor findings 0 by local review.
- Independent subagent review: reported blocking/major/minor findings 0.
- Rubric review: source-backed runtime issues 0; eval-only calibration issues 0; rubric defects 0; accepted trade-offs 0; remaining blocking/major/minor findings 0.
