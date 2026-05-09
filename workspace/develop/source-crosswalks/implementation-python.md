# Source Coverage Crosswalk: implementation-python

## Status

- Skill: `implementation-python`
- Runtime target: `dddjango/skills/implementation-python/`
- Source status: ready
- Runtime reference split: follows `workspace/docs/plugin-structure.md` without deviation
- Runtime references: `typing.md`, `dataclasses-enums.md`, `protocols-boundaries.md`, `pydantic-v2.md`
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
- `workspace/reference/implementation-python/reference/final.md`

## Authoring And Product Docs

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill_goal_instructions.md` `## 범위` | included | runtime path, this crosswalk | Plugin-bundled target and crosswalk location followed. |
| `## 실행 규칙` | included | this workflow | One skill at a time; rubrics not used during draft. |
| `## 구현 순서` | included | plan order | This follows `implementation-django-web`. |
| `## Skill별 작성 루프` | included | this crosswalk, review notes | Source scope, draft, review, rubric sequencing tracked. |
| `## SKILL.md 작성 규칙` | included | `SKILL.md` | Frontmatter has only name/description; body is short and procedural. |
| `## Runtime Reference 작성 규칙` | included | `references/*.md` | One-level references summarize source rather than copying it. |
| `## Agents Metadata 작성 규칙` | included | `agents/openai.yaml` | Metadata aligns with source and runtime skill. |
| `## 한국어 사용자 기준` | included | `SKILL.md` description | Korean trigger terms for typing/dataclass/Enum refactoring included. |
| `## Provisional Skill 처리` | omitted | n/a | This skill has dedicated source reference and is not provisional. |
| `## Cross-Skill Routing 기준` | included | `SKILL.md` Routing | Adjacent implementation, DDD, test, clean-code, and workflow boundaries included. |
| `## Review 기준` | included | Review Notes | Review types and findings tracked. |
| `## Completed 조건` | included | Review Notes, validation report | Completion requires zero remaining blocking/major/minor findings. |
| `## 검증` | included | final validation report | Only executed validation is reported. |
| `## 완료 보고` | included | final response | Required report fields will be included. |
| `## Goal Objective Template` | omitted | n/a | Goal prompt authoring content is not runtime skill behavior. |
| `spec.md` `## 관련 문서` | included | Sources Used | Linked product docs are covered. |
| `## 1. 목표` | merged | `SKILL.md` Routing | Python/Django ecosystem, simple-vs-complex judgment, and workflow delegation reflected. |
| `## 2. 설계 원칙` | merged | `SKILL.md`, references | Domain-first boundary and Python/Django adapter boundary reflected. |
| `## 3. 스킬 종류` | included | `SKILL.md`, references | `implementation-python` responsibility and adjacent skill boundaries included. |
| `## 4. 산출물 기준` | included | `SKILL.md`, references | Explicit contracts and honest verification included. |
| `plugin-structure.md` `## 1. 개발 위치` | included | runtime path | Runtime files live under plugin artifact because plugin runtime requires it. |
| `## 2. 목표 구조` / `## 2.1 Runtime 동기화 기준` | included | `dddjango/skills/implementation-python/` | Plugin-bundled structure used; no cache edits. |
| `## 3. Skill 파일 기준` | included | `SKILL.md` | Trigger, routing, references, and runtime rules only. |
| `## 4. Reference 파일 기준` | included | `references/*.md` | One-level references directly linked. |
| `## 5. Claude Code와 Codex 공통성` | included | `SKILL.md`, references | Shared skill name, responsibility, and verification rules preserved. |
| `## 6. 작성 순서` | included | this workflow | Docs/reference read before rubric review. |
| `## 7. Runtime Reference Split Plan` | included | four reference files | Exact split for `implementation-python` used. |
| `## 8. 금지 사항` | included | file tree | No README/changelog/install guide; no false validation claim. |
| `skill-authoring.md` `## 1. 작성 원칙` | included | `SKILL.md` | Trigger/routing and boundaries are in description/body. |
| `## 2. Frontmatter 입력 표` | included | `SKILL.md` description | Python typing/dataclass/Protocol/pydantic/Ruff signals included. |
| `## 3. Cross-Skill Precedence` | included | `SKILL.md` Routing | Domain/workflow precede Python implementation only when relevant. |
| `## 4. Agents Metadata Inputs` | included | `agents/openai.yaml` | Display name, short description, and default prompt align. |
| `reference-index.md` `## Architecture` | delegated-to-other-skill | `architecture-*` skills | Architecture source mapping outside Python implementation. |
| `## Implementation` | included | references | Python source reference used for runtime split. |
| `## Reference 사용 원칙` | included | references | Runtime references summarize source and avoid copying `final.md`. |
| `## Reference Gap` | delegated-to-other-skill | `architecture-implementation-patterns`, provisional skills | Python itself has dedicated source; implementation-patterns may use it as fallback. |
| `## DRF Guardrail` | delegated-to-other-skill | `implementation-django-ninja` | API/DRF routing outside Python skill. |
| `## Reference에서 도출한 제품 결정` | included | `SKILL.md`, references | Python contracts, test/source boundaries, and Django/Ninja separation reflected. |

## Contracts, Workflow, And DDD Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill-contracts.md` `## architecture-ddd` | delegated-to-other-skill | `SKILL.md` Routing | Domain modeling routes to DDD. |
| `## architecture-implementation-patterns` | delegated-to-other-skill | `architecture-implementation-patterns` | Architecture patterns are outside Python syntax choices. |
| `## architecture-db` | delegated-to-other-skill | `architecture-db` | DB schema and transaction design route away. |
| `## architecture-api` | delegated-to-other-skill | `architecture-api` | REST contract design routes away. |
| `## implementation-django` | delegated-to-other-skill | `SKILL.md` Routing | ORM/migration/settings route to Django core skill. |
| `## implementation-django-ninja` | delegated-to-other-skill | `SKILL.md` Routing | Router/Schema/API tests route to Ninja skill. |
| `## implementation-django-web` | delegated-to-other-skill | `implementation-django-web` | Template/static work routes away. |
| `## implementation-python` | included | `SKILL.md`, references | Typing, dataclass, Enum, Protocol, pydantic, exceptions, Ruff/typecheck covered. |
| `## implementation-tdd` | delegated-to-other-skill | `implementation-tdd` | TDD method routes away. |
| `## implementation-test` | delegated-to-other-skill | `implementation-test` | Pytest fixture/mock/factory mechanics route away. |
| `## implementation-cleancode` | merged | `SKILL.md` Routing | General refactoring combines with Python-specific choices when needed. |
| `## workflow-dddjango-subagents` | delegated-to-other-skill | `SKILL.md` Routing | Composite/subagent work routes to workflow. |
| `## 공통 필수 출력` | delegated-to-other-skill | `workflow-dddjango-subagents`, implementation skills | Risky write consistency is not Python-specific. |
| `skill-hierarchy.md` `## Skill Hierarchy` | included | `SKILL.md` Routing | Bottom implementation skill with upward delegation for domain/workflow complexity. |
| `workflow.md` `## 1. 기본 흐름` | merged | `SKILL.md` Routing | Domain ambiguity routes before Python constructs. |
| `## 2. 작업 유형별 흐름` | included | `SKILL.md` Routing | Simple Python work direct; composite work routes to workflow. |
| `## 3. 역할 분해` | delegated-to-other-skill | `workflow-dddjango-subagents` | Role map belongs to workflow skill. |
| `## 4. Sequential Fallback` / `## 5. Handoff Contract` | delegated-to-other-skill | `workflow-dddjango-subagents` | Workflow orchestration belongs elsewhere. |
| `## 6. 통합 우선순위` | merged | `SKILL.md`, references | Python idioms are below domain/data/security and above style-only details. |
| `## 7. Integration Checklist` | merged | references | Implementation mapping and verification honesty included. |
| `## 8. Reference Loading` | included | `SKILL.md` Reference Loading | Runtime references directly linked. |
| `## 9. 검증 방식` | included | `SKILL.md` Runtime Rules | Only executed Ruff/typecheck/tests may be claimed. |
| `ddd-implementation-standard.md` `## 1. 판단 순서` | merged | `SKILL.md` Routing | Domain decisions precede Python constructs when unclear. |
| `## 2. 하위 도메인별 구현 강도` | merged | `SKILL.md` Routing | Simple Python changes stay simple. |
| `## 3. 바운디드 컨텍스트와 언어` | delegated-to-other-skill | `architecture-ddd` | Strategic modeling responsibility. |
| `## 4. 애그리거트와 불변식` | merged | `dataclasses-enums.md`, `pydantic-v2.md` | Value objects and validation/domain invariant boundary reflected. |
| `## 5. Domain Events` | delegated-to-other-skill | `architecture-ddd`, `implementation-django` | Event timing is not Python typing responsibility. |
| `## 6. Application Service와 Domain Service` | merged | `protocols-boundaries.md` | Boundaries and explicit contracts help service responsibilities. |
| `## 7. Django ORM 매핑` | delegated-to-other-skill | `implementation-django` | ORM mapping routes away. |
| `## 8. Repository와 Transaction` | delegated-to-other-skill | `architecture-implementation-patterns`, `implementation-django` | Python protocols may express ports but architecture choice is delegated. |
| `## 9. API 매핑` | delegated-to-other-skill | `implementation-django-ninja` | API adapter implementation routes away. |
| `## 10. Python 매핑` | included | `SKILL.md`, all references | Public types, `X | None`, generics, Enum, dataclass, Protocol, pydantic v2 included. |
| `## 11. 테스트 매핑` | delegated-to-other-skill | `implementation-test` | Test implementation routes away; verification honesty remains here. |
| `validation-plan.md` `## 1. 검증 원칙` | included | `SKILL.md` | Real executed validation only. |
| `## 2. 대표 시나리오` / `### Python Typing` | included | `SKILL.md`, references | Enum/StrEnum, dataclass, pydantic-not-domain-default covered. |
| `## 3. 평가 항목` | merged | `SKILL.md`, references | Implementation pragmatism, routing, and verification reflected. |
| `## 4. Skill Folder 검증` | included | validation commands | Generated skill folder will be checked. |

## Python Reference Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `implementation-python/final.md` `## 1. 타입 힌트와 타입 시스템` | included | `typing.md`, `SKILL.md` | 1.1-1.14 covered as type contracts, `X | None`, generics, TypedDict, advanced typing, version gates. |
| `## 2. 구조적 패턴 매칭` | merged | `dataclasses-enums.md` | State-machine and dataclass pattern matching guidance included. |
| `## 3. 컬렉션 선택과 데이터 구조` | merged | `typing.md` | Collection type contracts included; detailed data-structure performance remains task-specific. |
| `## 4. 함수 설계: Python 특화 기법` | merged | `typing.md`, `protocols-boundaries.md` | Mutable default, keyword-only, `None` return, and callable contract concerns reflected. |
| `## 5. 데코레이터` | merged | `typing.md` | `ParamSpec` and `Concatenate` signature preservation included. |
| `## 6. 디스크립터` | omitted | n/a | Descriptor framework details are advanced implementation mechanics, not core runtime skill trigger/reference split. |
| `## 7. @property와 애트리뷰트 접근` | merged | `protocols-boundaries.md` | Property contracts in Protocols and ordinary attribute preference reflected. |
| `## 8. 클래스 설계: Python 특화 패턴` | merged | `dataclasses-enums.md`, `protocols-boundaries.md` | Factory/classmethod, repr/str, protected attributes, mixins/container protocols folded into class/boundary guidance. |
| `## 9. Protocol 심화` | included | `protocols-boundaries.md`, `SKILL.md` | Protocol use, composition, generics, runtime_checkable caveat included. |
| `## 10. Enum, dataclass, NamedTuple` | included | `dataclasses-enums.md`, `SKILL.md` | Enum/StrEnum, dataclass options, NamedTuple, value-object guidance included. |
| `## 11. 연산자 오버로딩과 Python 데이터 모델 심화` | omitted | n/a | Specialized data-model implementation; not first-class in product contract. |
| `## 12. pydantic v2` | included | `pydantic-v2.md`, `SKILL.md` | v2 APIs, validators, strict mode, and domain boundary included. |
| `## 13. 이터레이터, 제너레이터, 컴프리헨션` | omitted | n/a | General Python fluency; not part of runtime split except when project task requires local judgment. |
| `## 14. 컨텍스트 매니저와 with문` | merged | `protocols-boundaries.md` | Resource cleanup/context manager guidance included. |
| `## 15. 예외 처리` | included | `protocols-boundaries.md` | Module exception root, explicit exceptions, `try` block roles included. |
| `## 16. 동시성과 병렬성` | merged | `protocols-boundaries.md` | TaskGroup/thread/GIL version-specific guidance included. |
| `## 17. 성능 프로파일링과 최적화` | delegated-to-other-skill | `implementation-cleancode`, project-specific profiling | Performance tuning needs task-specific evidence; not central runtime split. |
| `## 18. f-문자열 개선과 PEG 파서` | omitted | n/a | Syntax detail not central to dddjango Python contract. |
| `## 19. 파이썬다운 관용 표현` | delegated-to-other-skill | `implementation-cleancode` | General idioms/readability handled by clean-code plus local style. |
| `## 20. 디자인 패턴 (Python 고유 구현)` | delegated-to-other-skill | `architecture-implementation-patterns` | Pattern selection belongs to architecture patterns skill. |
| `## 21. Repository / Unit of Work` | delegated-to-other-skill | `architecture-implementation-patterns` | Source itself states future architecture-pattern source separation. |
| `## 22. Ruff -- 통합 린터/포매터` | included | `typing.md`, `SKILL.md` | Ruff target/version and rule compatibility included. |
| `## 23. mypy/pyright 최신 기능` | included | `typing.md`, `SKILL.md` | Strict typing and type narrowing guidance included. |
| `## 24. 테스트` | delegated-to-other-skill | `implementation-test` | Test implementation belongs to test skill. |
| `## 25. 디버깅 기법` | omitted | n/a | Debugging tools are not product contract for this skill. |
| `## 26. 독스트링과 문서화` | delegated-to-other-skill | `implementation-cleancode` | Documentation style belongs to clean-code/review. |
| `## 27. 정밀 연산` | merged | `dataclasses-enums.md` | Precision-sensitive value-object choice can use value objects; detailed Decimal/Fraction is task-specific. |
| `## 28. Python 3.14 주요 변경사항` | merged | `typing.md`, `protocols-boundaries.md` | Version gates for 3.13+/3.14 features included. |
| `## 부록 A: Python 3.10-3.14 핵심 변경사항 요약` | merged | all references | Version-gated modern Python guidance reflected. |
| `## 부록 B: 타입 시스템 진화 요약` | merged | `typing.md` | Modern typing evolution reflected. |
| `## 부록 C: 주요 매직 메서드 요약` | omitted | n/a | Detailed magic method reference is outside runtime skill scope. |
| `## 출처` | omitted | n/a | Bibliography is source provenance, not runtime behavior. |

## Review Notes

- Source self-review: local review found 1 minor wording cleanup and no remaining blocking/major/minor findings.
- Skill-creator/writing-skills review: no extraneous files, direct reference links, concise `SKILL.md`, and frontmatter length under 1024; remaining blocking/major/minor findings 0 by local review.
- Independent subagent review: first pass found 0 blocking, 0 major, and 3 minor; fixes applied; re-review reported blocking/major/minor findings 0.
- Rubric review: 1 source-backed runtime issue found (async boundary constraints); fixed. Eval-only calibration issues 0; rubric defects 0; accepted trade-offs 0; remaining blocking/major/minor findings 0.
