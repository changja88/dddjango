# Source Coverage Crosswalk: implementation-django

## Status

- Skill: `implementation-django`
- Runtime target: `dddjango/skills/implementation-django/`
- Source status: ready
- Source policy decision: not provisional; dedicated source exists at `workspace/reference/implementation-django/reference/final.md`
- Runtime reference split: follows `workspace/docs/plugin-structure.md` without deviation
- Runtime references: `models-orm.md`, `services-selectors.md`, `migrations.md`, `transactions-performance-security.md`
- Rubric status: not opened during draft; reserved for post-source-review verification

## Sources Used

- `workspace/develop/skill_goal_instructions.md`
- `workspace/docs/plugin-structure.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/skill-hierarchy.md`
- `workspace/docs/skill-authoring.md`
- `workspace/docs/reference-index.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/workflow.md`
- `workspace/docs/validation-plan.md`
- `workspace/reference/implementation-django/reference/final.md`

## Authoring And Product Docs

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill_goal_instructions.md` `## 범위` | included | `SKILL.md`, this crosswalk | Runtime target and review artifact locations followed. |
| `## 실행 규칙` | included | this crosswalk, review notes | One-skill sequencing, no rubric before draft, and honest verification followed. |
| `## 구현 순서` | included | completion sequence | Implemented next skill after skeleton: `implementation-django`. |
| `## Skill별 작성 루프` / `### Source Coverage Crosswalk` | included | this crosswalk | Loop and crosswalk format followed. |
| `## SKILL.md 작성 규칙` | included | `SKILL.md` | Frontmatter has only `name` and `description`; body is concise and reference-linked. |
| `## Runtime Reference 작성 규칙` | included | `references/*.md` | Source was summarized and split, not copied. |
| `## Agents Metadata 작성 규칙` | included | `agents/openai.yaml` | Metadata generated from final skill responsibility. |
| `## 한국어 사용자 기준` | included | `SKILL.md` description/routing | Korean and mixed triggers include 상태 컬럼, backfill, ORM 최적화, service layer. |
| `## Provisional Skill 처리` | omitted | this crosswalk | Not applicable; this skill has dedicated source. |
| `## Cross-Skill Routing 기준` | included | `SKILL.md` Routing | Delegates DDD, DB, API, web, and workflow cases. |
| `## Review 기준` | included | review notes | Source and rubric review categories used. |
| `## Completed 조건` | included | review notes, validation | Completion criteria checked for this skill. |
| `## 검증` | included | final report | Validation commands selected and reported honestly. |
| `## 완료 보고` | included | final report | Required report fields tracked. |
| `## Goal Objective Template` | omitted | n/a | Goal prompt template for future runs; not runtime skill guidance, but accounted for by this crosswalk. |
| `plugin-structure.md` `## 1. 개발 위치` | included | runtime path | Runtime files are under repo-root `dddjango/` because plugin runtime requires it. |
| `## 2. 목표 구조` / `## 2.1 Runtime 동기화 기준` | included | `dddjango/skills/implementation-django/` | Plugin-bundled structure followed; no cache edits. |
| `## 3. Skill 파일 기준` | included | `SKILL.md` | Only trigger, routing, references, and runtime rules. |
| `## 4. Reference 파일 기준` | included | `references/*.md` | One-level references directly linked. |
| `## 5. Claude Code와 Codex 공통성` | included | `SKILL.md`, references | Shared skill name, responsibility, reference names, and standards preserved. |
| `## 6. 작성 순서` | included | this workflow | Docs/reference read before draft. |
| `## 7. Runtime Reference Split Plan` | included | four reference files | Used exact split for `implementation-django`. |
| `## 8. 금지 사항` | included | file tree | No README/changelog/install guide; no false validation claim. |
| `skill-contracts.md` `## architecture-ddd` | delegated-to-other-skill | `SKILL.md` Routing | Unclear domain rules and bounded context route to DDD. |
| `## architecture-implementation-patterns` | delegated-to-other-skill | `SKILL.md` Routing | Implementation architecture decisions are not forced by this skill. |
| `## architecture-db` | delegated-to-other-skill | `SKILL.md` Routing | Undecided schema, constraints, locking, and rollout route to DB architecture. |
| `## architecture-api` | delegated-to-other-skill | `SKILL.md` Routing | REST API contract design routes to API architecture. |
| `## implementation-django` | included | `SKILL.md`, all references | Core responsibility mapped to models, ORM, services, migrations, transactions. |
| `## implementation-django-ninja` | delegated-to-other-skill | `SKILL.md` Routing | Router/Schema/API endpoint work routes to Ninja implementation. |
| `## implementation-django-web` | delegated-to-other-skill | `SKILL.md` Routing | Template/static/page work routes to web implementation. |
| `## implementation-python` | delegated-to-other-skill | `SKILL.md` Routing | Python type/language details route to Python implementation. |
| `## implementation-tdd` | delegated-to-other-skill | runtime rules | TDD methodology is separate; this skill reports needed acceptance tests. |
| `## implementation-test` | delegated-to-other-skill | runtime rules | Fixture/mock/factory mechanics belong to test implementation. |
| `## implementation-cleancode` | delegated-to-other-skill | runtime rules | Broad code quality review belongs to clean-code skill. |
| `## workflow-dddjango-subagents` | delegated-to-other-skill | `SKILL.md` Routing | Subagent/role decomposition requests route to workflow. |
| `skill-contracts.md` `## 공통 필수 출력` / `### Risky Write Consistency Block` | included | `transactions-performance-security.md` | Risky write consistency block is runtime rule. |
| `reference-index.md` `## Architecture` | delegated-to-other-skill | `SKILL.md` Routing | Architecture source belongs to architecture skills. |
| `## Implementation` | included | all references | Django source and related boundaries used. |
| `## Reference 사용 원칙` | included | this crosswalk | Used `final.md`; did not copy source. |
| `## Reference Gap` | omitted | this crosswalk | Not a gap for `implementation-django`. |
| `## DRF Guardrail` | included | `SKILL.md` Runtime Rules | New API standard must not be DRF. |
| `## Reference에서 도출한 제품 결정` | included | `SKILL.md`, references | Django philosophy, service boundary, test honesty reflected. |
| `skill-authoring.md` `## 1. 작성 원칙` | included | `SKILL.md` frontmatter | Description is trigger/routing centered. |
| `## 2. Frontmatter 입력 표` | included | `SKILL.md` description | Draft, positive signals, negative routing merged. |
| `## 3. Cross-Skill Precedence` | included | `SKILL.md` Routing | Simple tasks stay on implementation skill; uncertain contracts route upward. |
| `## 4. Agents Metadata Inputs` | included | `agents/openai.yaml` | Display name, short description, default prompt aligned. |
| `skill-hierarchy.md` all headings | included | `SKILL.md` Routing | Bottom-skill behavior and upward delegation reflected. |
| `workflow.md` `## 1. 기본 흐름` | merged | `SKILL.md` Routing | Only the relevant implementation entry point is reflected. |
| `## 2. 작업 유형별 흐름` | included | `SKILL.md` Routing | Simple vs DDD/composite/risky boundary included. |
| `## 3. 역할 분해` | delegated-to-other-skill | `workflow-dddjango-subagents` | Workflow role map belongs to workflow skill. |
| `## 4. Sequential Fallback` | delegated-to-other-skill | `workflow-dddjango-subagents` | Not a runtime responsibility of this skill. |
| `## 5. Handoff Contract` | delegated-to-other-skill | `workflow-dddjango-subagents` | Not a runtime responsibility of this skill. |
| `## 6. 통합 우선순위` | merged | `SKILL.md`, transaction rules | Invariant/data/transaction/security priority reflected for risky writes. |
| `## 7. Integration Checklist` | merged | `transactions-performance-security.md` | Relevant implementation, data, transaction, verification checks included. |
| `## 8. Reference Loading` | included | `SKILL.md` Reference Loading | Runtime references are directly linked. |
| `## 9. 검증 방식` | included | `SKILL.md` Runtime Rules | Honest verification rule included. |
| `ddd-implementation-standard.md` `## 1. 판단 순서` | merged | `SKILL.md` Routing | Routes unclear domain work to architecture first. |
| `## 2. 하위 도메인별 구현 강도` | merged | `SKILL.md`, `services-selectors.md` | Simple CRUD stays simple; complex domain may add boundaries. |
| `## 3. 바운디드 컨텍스트와 언어` | delegated-to-other-skill | `architecture-ddd` | Strategic modeling responsibility. |
| `## 4. 애그리거트와 불변식` | merged | `services-selectors.md`, transaction rules | Implementation keeps invariants in model/service/DB boundary. |
| `## 5. Domain Events` | merged | `transactions-performance-security.md` | Outbox/on_commit/cross-aggregate consistency included. |
| `## 6. Application Service와 Domain Service` | included | `services-selectors.md` | Service/domain service ownership included. |
| `## 7. Django ORM 매핑` | included | `services-selectors.md` | ORM-as-domain vs separation trade-off included. |
| `## 8. Repository와 Transaction` | included | `services-selectors.md`, `transactions-performance-security.md` | Repository trade-off and transaction consistency included. |
| `## 9. API 매핑` | delegated-to-other-skill | `implementation-django-ninja` | API adapter implementation belongs to Ninja skill. |
| `## 10. Python 매핑` | delegated-to-other-skill | `implementation-python` | Python typing conventions owned by Python skill. |
| `## 11. 테스트 매핑` | merged | `transactions-performance-security.md` | Django acceptance criteria included; test mechanics delegated to test skills. |
| `validation-plan.md` `## 1. 검증 원칙` | included | review notes | Actual artifacts and honest verification used. |
| `## 2. 대표 시나리오` | merged | `SKILL.md`, references | Relevant Django scenarios reflected; API/web/false-subagent scenarios delegated. |
| `### 운영 마이그레이션` | included | `migrations.md` | Migration rollout risk reflected. |
| `### 트랜잭션과 동시성` | included | `transactions-performance-security.md` | Transaction/locking consistency reflected. |
| `### Negative Case: 단순 필드 rename` | included | `SKILL.md` | Simple work must not force workflow/DDD. |
| `### Negative Case: false subagent claim` | included | `SKILL.md` Runtime Rules | Verification honesty and no false subagent claim carried from goal instructions. |
| `## 3. 평가 항목` | included | review notes | Product checks used for source self-review. |
| `## 4. Skill Folder 검증` | included | validation | Folder structure and commands followed where possible. |

## Django Source Reference Heading Coverage

| Heading | Status | Runtime location | Reason |
|---|---|---|---|
| `## 목차` | omitted | n/a | Source navigation only. |
| `## 1. Django 설계 철학` | merged | `models-orm.md`, `SKILL.md` | Django conventions and separation boundaries reflected. |
| `### 1.1 전체 철학` | merged | `SKILL.md`, `models-orm.md` | Loose coupling, less code, DRY, explicitness reflected. |
| `### 1.2 모델 철학` | included | `models-orm.md` | Model ownership and methods included. |
| `### 1.3 데이터베이스 API 철학` | included | `models-orm.md` | ORM, QuerySet, raw SQL fallback included. |
| `### 1.4 URL 설계 철학` | delegated-to-other-skill | `implementation-django-web`, `implementation-django-ninja` | URL/API/page routing is not this skill’s main responsibility. |
| `### 1.5 템플릿 시스템 철학` | delegated-to-other-skill | `implementation-django-web` | Template/static responsibility belongs to web skill. |
| `### 1.6 뷰 철학` | merged | `models-orm.md` | Thin view boundary included; web specifics delegated. |
| `## 2. Django 코딩 스타일` | merged | `models-orm.md` | Runtime references keep model/style essentials. |
| `### 2.1 포매팅 기본 규칙` | delegated-to-other-skill | `implementation-python`, project formatter | General formatting is Python/project tooling. |
| `### 2.2 임포트 순서` | delegated-to-other-skill | `implementation-python` | Python style detail. |
| `### 2.3 문자열 포매팅` | delegated-to-other-skill | `implementation-python` | Python/i18n style detail. |
| `### 2.4 모델 코딩 스타일` | included | `models-orm.md` | Model organization included. |
| `### 2.5 선택지(Choices) 정의` | included | `models-orm.md` | `TextChoices`/finite state guidance included. |
| `### 2.6 템플릿 코딩 스타일` | delegated-to-other-skill | `implementation-django-web` | Template-specific. |
| `### 2.7 뷰 코딩 스타일` | merged | `models-orm.md` | Thin view and simple FBV/CBV choice included. |
| `## 3. 프로젝트 구조와 앱 설계` | included | `models-orm.md` | App/settings structure included. |
| `### 3.1 프로젝트 레이아웃` | merged | `models-orm.md` | Summarized conventional layout. |
| `### 3.2 앱 분리 기준` | included | `models-orm.md` | Cohesive app boundary included. |
| `### 3.3 설정(Settings) 분리` | included | `models-orm.md`, `transactions-performance-security.md` | Settings/env/security included. |
| `### 3.4 settings 접근 시 주의사항` | included | `models-orm.md` | Lazy settings access included. |
| `## 4. 모델 설계 패턴` | included | `models-orm.md` | Model design included. |
| `### 4.1 Fat Model, Thin View 원칙` | included | `models-orm.md`, `services-selectors.md` | Model/service vs view boundary included. |
| `### 4.2 모델 상속 패턴` | included | `models-orm.md` | Abstract, multi-table, proxy guidance included. |
| `### 4.3 필드 선택 가이드` | included | `models-orm.md` | Choices, JSON, Decimal guidance included. |
| `### 4.4 모델 유효성 검증` | included | `models-orm.md` | `clean()` and DB constraints included. |
| `## 5. QuerySet과 Manager 패턴` | included | `models-orm.md` | QuerySet/manager guidance included. |
| `### 5.1 Custom Manager와 QuerySet` | included | `models-orm.md` | Chainable predicates included. |
| `### 5.2 QuerySet 최적화 필수 패턴` | included | `models-orm.md`, `transactions-performance-security.md` | select/prefetch and N+1 included. |
| `### 5.3 only(), defer(), values()` | included | `models-orm.md`, `transactions-performance-security.md` | Projection/lazy loading cautions included. |
| `### 5.4 annotate()와 aggregate()` | included | `models-orm.md` | Order sensitivity and alias included. |
| `### 5.5 bulk 연산` | included | `models-orm.md`, `migrations.md` | Bulk operations and migration use included. |
| `## 6. 뷰 패턴: CBV vs FBV` | merged | `models-orm.md` | Only boundary and simple choice included. |
| `### 6.1 선택 기준` | merged | `models-orm.md` | Simple FBV vs CBV guidance included. |
| `### 6.2 CBV 올바른 사용` | delegated-to-other-skill | `implementation-django-web` | View implementation detail. |
| `### 6.3 Mixin 활용 패턴` | delegated-to-other-skill | `implementation-django-web` | Web view detail. |
| `### 6.4 FBV 올바른 사용` | merged | `models-orm.md` | Simple view rule included. |
| `## 7. 폼과 유효성 검증` | merged | `models-orm.md` | Form/domain validation boundary included. |
| `### 7.1 폼 유효성 검증 순서` | omitted | n/a | Detailed form lifecycle belongs to web/form implementation, not core runtime split. |
| `### 7.2 ModelForm 활용` | delegated-to-other-skill | `implementation-django-web` | Web form detail. |
| `### 7.3 커스텀 Validator 재사용` | merged | `models-orm.md` | Validation ownership included. |
| `## 8. Django REST Framework 패턴` | delegated-to-other-skill | `implementation-django-ninja` | DRF is legacy/migration/comparison only. |
| `### 8.1 Serializer 설계` | delegated-to-other-skill | `implementation-django-ninja` | Not new API standard. |
| `### 8.2 ViewSet과 Router` | delegated-to-other-skill | `implementation-django-ninja` | Not new API standard. |
| `### 8.3 Permission 패턴` | delegated-to-other-skill | `implementation-django-ninja` | API permission detail. |
| `### 8.4 Pagination 설정` | delegated-to-other-skill | `implementation-django-ninja` | API pagination detail. |
| `### 8.5 API 버전 관리` | delegated-to-other-skill | `architecture-api`, `implementation-django-ninja` | API contract responsibility. |
| `## 9. 시그널 사용 가이드라인` | included | `models-orm.md` | Signal use/avoid boundaries included. |
| `### 9.1 시그널을 사용해야 하는 경우` | included | `models-orm.md` | Appropriate signal cases included. |
| `### 9.2 시그널을 피해야 하는 경우` | included | `models-orm.md` | Hidden control flow warning included. |
| `## 10. 마이그레이션 베스트 프랙티스` | included | `migrations.md` | Migration rules included. |
| `### 10.1 기본 원칙` | included | `migrations.md` | Version control, small migrations, sqlmigrate included. |
| `### 10.2 데이터 마이그레이션` | included | `migrations.md` | `apps.get_model()` and reverse handling included. |
| `### 10.3 무중단 마이그레이션` | included | `migrations.md` | Expand/backfill/contract included. |
| `## 11. 성능 최적화` | included | `transactions-performance-security.md` | Query performance included. |
| `### 11.1 N+1 문제 탐지와 해결` | included | `transactions-performance-security.md` | N+1 and query-count tests included. |
| `### 11.2 데이터베이스 인덱스 전략` | included | `migrations.md`, `transactions-performance-security.md` | Index rollout and EXPLAIN included. |
| `### 11.3 save(update_fields=...)` | included | `transactions-performance-security.md`, `migrations.md` | Narrow updates included. |
| `### 11.4 exists()와 count()` | included | `transactions-performance-security.md` | Existence/count guidance included. |
| `## 12. 캐싱 전략` | included | `transactions-performance-security.md` | Caching levels and invalidation included. |
| `### 12.1 캐싱 수준` | included | `transactions-performance-security.md` | Cache level choice included. |
| `### 12.2 캐시 무효화 패턴` | included | `transactions-performance-security.md` | Version/invalidation ownership included. |
| `## 13. 보안` | included | `transactions-performance-security.md` | Django security rules included. |
| `### 13.1 Django 내장 보안 기능` | included | `transactions-performance-security.md` | CSRF/XSS/SQLi/clickjacking included. |
| `### 13.2 보안 설정 체크리스트` | included | `transactions-performance-security.md` | Deploy settings checks included. |
| `### 13.3 Raw SQL 안전하게 사용` | included | `transactions-performance-security.md` | Parameterized SQL included. |
| `### 13.4 인증과 인가` | merged | `transactions-performance-security.md` | Adapter-boundary permission guidance included. |
| `## 14. 테스트 패턴` | merged | `transactions-performance-security.md` | Django test acceptance included; detailed pytest/factory delegated. |
| `### 14.1 TestCase 선택 기준` | included | `transactions-performance-security.md` | TestCase/TransactionTestCase included. |
| `### 14.2 Factory Boy 활용` | delegated-to-other-skill | `implementation-test` | Factory mechanics owned by test skill. |
| `### 14.3 pytest-django 활용` | merged | `transactions-performance-security.md` | `pytest.mark.django_db` included; fixture mechanics delegated. |
| `### 14.4 테스트에서의 Django 공식 규칙` | delegated-to-other-skill | `implementation-test` | Test style details owned by test skill. |
| `## 15. 미들웨어` | included | `transactions-performance-security.md` | Middleware rules included. |
| `### 15.1 미들웨어 실행 순서` | included | `transactions-performance-security.md` | Ordering constraints included. |
| `### 15.2 커스텀 미들웨어 작성` | included | `transactions-performance-security.md` | Lightweight/single concern included. |
| `## 16. Django와 서비스 레이어 아키텍처` | included | `services-selectors.md` | Service layer and DDD trade-off included. |
| `### 16.1 서비스 레이어가 필요한 시점` | included | `services-selectors.md` | Service introduction criteria included. |
| `### 16.2 HackSoft 서비스/셀렉터 패턴` | included | `services-selectors.md` | Service/selector shapes included. |
| `### 16.3 DDD와 Django의 트레이드오프` | included | `services-selectors.md` | ORM vs repository trade-off included. |
| `## 17. Django 5.x 새 기능` | omitted | n/a | Version feature list is temporal/reference detail; runtime skill targets Django 5.x without copying release notes. |
| `### 17.1 Django 5.0 주요 기능` | merged | `models-orm.md` | `db_default` and `GeneratedField` implementation notes included. |
| `### 17.2 Django 5.1 주요 기능` | omitted | n/a | Login middleware detail is auth/web routing detail, not central to this skill. |
| `### 17.3 Django 5.2 주요 기능 (LTS)` | merged | `SKILL.md` description, `models-orm.md` | LTS trigger and composite-PK constraints included. |
| `## 참고 자료` and child headings | omitted | n/a | Bibliography not runtime guidance. |

## Review Notes

- Source self-review: fixed 3 minor findings before external review: Django 5.x trigger, selector metadata, and validation-plan crosswalk coverage; later evaluation pass fixed workflow routing, test-implementation boundary, and `Goal Objective Template` crosswalk coverage; remaining blocking/major/minor findings 0 by local review.
- Skill-creator review: 0 findings after checking frontmatter-only metadata, concise body, direct one-level reference links, no TODO placeholders, no banned auxiliary docs, and no runtime rubric leakage.
- Independent review subagent `Zeno` executed: fixed 3 major and 3 minor findings from the first pass; second-pass wording follow-up was addressed in subsequent local cleanup; current remaining blocking/major/minor findings 0 by local review.
- Independent evaluation review subagent `Confucius` executed: fixed 3 source-backed findings and 1 metadata finding; current remaining blocking/major/minor findings 0 by local review.
- Rubric review: fixed 1 source-backed runtime issue from `Risky Write Consistency Block` naming/completeness; eval-only rubric material was not copied into runtime docs. Blocking 0, major 0, minor 0 after fix.
