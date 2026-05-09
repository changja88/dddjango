# Source Coverage Crosswalk: implementation-django-web

## Status

- Skill: `implementation-django-web`
- Runtime target: `dddjango/skills/implementation-django-web/`
- Source status: provisional until dedicated Django Web source reference exists
- Source policy decision: `allow-provisional-with-fallback`
- Fallback source: `workspace/reference/implementation-django/reference/final.md` URL/template/view/form/security/auth/middleware sections plus `workspace/docs` product decisions for static files, CSS/JS, HTMX, and CSRF-aware AJAX
- Runtime reference split: follows `workspace/docs/plugin-structure.md` without deviation
- Runtime references: `templates.md`, `static-assets.md`, `templateview-htmx.md`, `csrf-ajax.md`

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
- `workspace/reference/implementation-django/reference/final.md` URL/template/view/form/security/auth/middleware sections

## Authoring Instructions Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill_goal_instructions.md` `## 범위` | included | runtime path, this crosswalk | Plugin-bundled target and crosswalk location followed. |
| `## 실행 규칙` | included | this workflow | One skill at a time; rubrics not used during draft. |
| `## 구현 순서` | included | plan order | This follows `implementation-django-ninja` and precedes `implementation-python`. |
| `## Skill별 작성 루프` | included | this crosswalk, review notes | Source scope, crosswalk, draft, review, rubric sequencing tracked. |
| `## SKILL.md 작성 규칙` | included | `SKILL.md` | Frontmatter has only name/description; body is short and procedural. |
| `## Runtime Reference 작성 규칙` | included | `references/*.md` | Four one-level references summarize source rather than copying it. |
| `## Agents Metadata 작성 규칙` | included | `agents/openai.yaml` | Metadata reflects provisional fallback scope. |
| `## 한국어 사용자 기준` | included | `SKILL.md` description/routing | Korean trigger and boundary terms such as 템플릿, 정적 파일, 화면, 폼, 렌더링, REST API, ORM, 마이그레이션, 복합/위험 작업 included. |
| `## Provisional Skill 처리` | included | `SKILL.md`, this crosswalk | `allow-provisional-with-fallback` and fallback source are explicit. |
| `## Cross-Skill Routing 기준` | included | `SKILL.md` Routing | API, ORM, DDD, and workflow boundaries are routed. |
| `## Review 기준` | included | Review Notes | Review types and finding closure tracked. |
| `## Completed 조건` | included | Review Notes, validation report | Completion requires zero remaining blocking/major/minor findings. |
| `## 검증` | included | final validation report | Only executed validation is reported. |
| `## 완료 보고` | included | final response | Required report fields will be included. |
| `## Goal Objective Template` | omitted | n/a | Goal prompt authoring content is not runtime skill behavior. |

## Product Docs Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `spec.md` `## 관련 문서` | included | this crosswalk | Linked docs are the source set used for this skill. |
| `## 1. 목표` | merged | `SKILL.md` Routing | Django Ninja API standard, simple-vs-complex judgment, and workflow delegation reflected. |
| `## 2. 설계 원칙` | merged | `SKILL.md`, references | Adapter boundary, simple Django structure, and evidence-based validation reflected. |
| `## 3. 스킬 종류` | included | `SKILL.md` Routing | `implementation-django-web` ownership and adjacent skill boundaries included. |
| `## 4. 산출물 기준` | included | `SKILL.md`, references | Implementation boundary and honest verification requirements included. |
| `plugin-structure.md` `## 1. 개발 위치` | included | runtime path | Runtime files live under repo-root plugin artifact because plugin runtime requires it. |
| `## 2. 목표 구조` | included | `dddjango/skills/implementation-django-web/` | Folder shape matches planned plugin-bundled skill structure. |
| `## 2.1 Runtime 동기화 기준` | included | this workflow | Workspace docs/reference treated as canonical; no cache edits. |
| `## 3. Skill 파일 기준` | included | `SKILL.md` | Trigger, routing, references, and runtime rules only. |
| `## 4. Reference 파일 기준` | included | `references/*.md` | One-level references directly linked from `SKILL.md`. |
| `## 5. Claude Code와 Codex 공통성` | included | `SKILL.md`, references | Shared skill name, responsibility, and verification rules preserved. |
| `## 6. 작성 순서` | included | this workflow | Docs/reference read before rubric review. |
| `## 7. Runtime Reference Split Plan` | included | four reference files | Exact split for `implementation-django-web` used. |
| `## 8. 금지 사항` | included | file tree | No README/changelog/install guide; no false validation claim. |
| `skill-authoring.md` `## 1. 작성 원칙` | included | `SKILL.md` frontmatter/body | Description focuses on trigger/routing; details moved to references. |
| `## 2. Frontmatter 입력 표` | included | `SKILL.md` description | Provisional Django Web trigger, Korean signals, and API boundary included. |
| `## 3. Cross-Skill Precedence` | included | `SKILL.md` Routing | Workflow/DDD/API/implementation precedence reflected without overapplying to tiny changes. |
| `## 4. Agents Metadata Inputs` | included | `agents/openai.yaml` | Display name, short description, and default prompt align with skill. |
| `reference-index.md` `## Architecture` | delegated-to-other-skill | `architecture-*` skills | Architecture source mapping is outside web implementation. |
| `## Implementation` | included | `SKILL.md`, references | Django Web fallback and implementation ownership included. |
| `## Reference 사용 원칙` | included | references | Runtime references summarize source and avoid copying `final.md`. |
| `## Reference Gap` | included | `SKILL.md`, this crosswalk | Django Web source gap and provisional fallback stated. |
| `## DRF Guardrail` | delegated-to-other-skill | `implementation-django-ninja` | API/DRF work routes away from this skill. |
| `## Reference에서 도출한 제품 결정` | included | `SKILL.md`, references | Product decisions for Django Web ownership and Django source fallback reflected. |

## Skill Contract And Hierarchy Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill-contracts.md` `## architecture-ddd` | delegated-to-other-skill | `SKILL.md` Routing | Domain rules and bounded context route to DDD. |
| `## architecture-implementation-patterns` | delegated-to-other-skill | `workflow-dddjango-subagents` | Implementation architecture patterns are not web-specific. |
| `## architecture-db` | delegated-to-other-skill | `implementation-django`, `architecture-db` | DB schema/transaction concerns route away. |
| `## architecture-api` | delegated-to-other-skill | `implementation-django-ninja`, `architecture-api` | REST contract/API work routes away. |
| `## implementation-django` | delegated-to-other-skill | `SKILL.md` Routing | ORM/service/migration work routes to Django core skill. |
| `## implementation-django-ninja` | delegated-to-other-skill | `SKILL.md` Routing | Router/Schema/API error/OpenAPI work routes to Ninja skill. |
| `## implementation-django-web` | included | `SKILL.md`, references | Template/static/frontend, TemplateView, includes, HTMX, CSRF ownership covered. |
| `## implementation-python` | delegated-to-other-skill | `implementation-python` | Python typing and language contracts are outside this skill. |
| `## implementation-tdd` | delegated-to-other-skill | `implementation-tdd` | TDD method belongs to TDD skill. |
| `## implementation-test` | delegated-to-other-skill | `implementation-test` | Test mechanics belong to test skill; web verification criteria remain here. |
| `## implementation-cleancode` | merged | `SKILL.md`, references | Thin views and presentation-only templates cover web quality boundaries. |
| `## workflow-dddjango-subagents` | delegated-to-other-skill | `SKILL.md` Routing | Composite/subagent work routes to workflow. |
| `## 공통 필수 출력` | delegated-to-other-skill | `workflow-dddjango-subagents`, `implementation-django` | Risky write consistency is not web-specific unless workflow combines responsibilities. |
| `skill-hierarchy.md` `## Skill Hierarchy` | included | `SKILL.md` Routing | Bottom implementation skill with upward delegation for domain/workflow complexity. |

## Workflow And DDD Standard Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `workflow.md` `## 1. 기본 흐름` | merged | `SKILL.md` Routing | Domain ambiguity routes before web implementation. |
| `## 2. 작업 유형별 흐름` | included | `SKILL.md` Routing | Simple web work direct; composite/risky work routes to workflow. |
| `## 3. 역할 분해` | delegated-to-other-skill | `workflow-dddjango-subagents` | Role map belongs to workflow skill; web skill only routes there. |
| `## 4. Sequential Fallback` | delegated-to-other-skill | `workflow-dddjango-subagents` | Sequential role order belongs to workflow skill. |
| `## 5. Handoff Contract` | delegated-to-other-skill | `workflow-dddjango-subagents` | Handoff fields are not this skill’s runtime responsibility. |
| `## 6. 통합 우선순위` | merged | `SKILL.md`, references | Domain/template boundary and security verification reflected. |
| `## 7. Integration Checklist` | merged | `SKILL.md`, references | No domain logic in view/template and verification honesty included. |
| `## 8. Reference Loading` | included | `SKILL.md` Reference Loading | Runtime references are directly linked; no workspace-only runtime dependency. |
| `## 9. 검증 방식` | included | `SKILL.md`, `csrf-ajax.md` | Only executed verification may be claimed. |
| `ddd-implementation-standard.md` `## 1. 판단 순서` | merged | `SKILL.md` Routing | Domain decisions route before web implementation when unclear. |
| `## 2. 하위 도메인별 구현 강도` | merged | `SKILL.md` Routing | Tiny template changes stay direct. |
| `## 3. 바운디드 컨텍스트와 언어` | delegated-to-other-skill | `architecture-ddd` | Strategic modeling responsibility. |
| `## 4. 애그리거트와 불변식` | merged | `templates.md`, `templateview-htmx.md` | Domain rules stay out of templates/views. |
| `## 5. Domain Events` | delegated-to-other-skill | `architecture-ddd`, `implementation-django` | Event timing is not web-specific. |
| `## 6. Application Service와 Domain Service` | merged | `templateview-htmx.md` | Views call service/usecase and do not own domain behavior. |
| `## 7. Django ORM 매핑` | delegated-to-other-skill | `implementation-django` | ORM mapping belongs to Django core skill. |
| `## 8. Repository와 Transaction` | delegated-to-other-skill | `implementation-django`, `architecture-db` | Transaction/repository design is outside this skill. |
| `## 9. API 매핑` | delegated-to-other-skill | `implementation-django-ninja` | API adapter work belongs to Ninja skill. |
| `## 10. Python 매핑` | delegated-to-other-skill | `implementation-python` | Typing/details belong elsewhere. |
| `## 11. 테스트 매핑` | merged | `csrf-ajax.md` | Web render/form/HTMX verification criteria included; test mechanics delegated. |

## Validation Plan Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `validation-plan.md` `## 1. 검증 원칙` | included | `SKILL.md`, references | Validation must be real evidence, not memorized source. |
| `## 2. 대표 시나리오` | included | `SKILL.md`, references | Django Web scenario and relevant routing negatives reflected. |
| `### Django Web` | included | `SKILL.md`, references | TemplateView, template/static structure, CSRF/HTMX, and no template domain rules included. |
| `## 3. 평가 항목` | merged | `SKILL.md`, references | Skill activation, output quality, routing, and validation honesty reflected. |
| `## 4. Skill Folder 검증` | included | validation commands | Generated skill folder will be checked with validator. |

## Fallback Source Heading Coverage

| Heading | Status | Runtime location | Reason |
|---|---|---|---|
| `implementation-django/final.md` `## 목차` | omitted | n/a | Navigational table of contents, not runtime behavior. |
| `## 1. Django 설계 철학` | merged | `templates.md`, `templateview-htmx.md` | Relevant URL/template/view philosophy included below. |
| `### 1.4 URL 설계 철학` | included | `templateview-htmx.md` | Loose coupling from Python names and no file-extension URLs included. |
| `### 1.5 템플릿 시스템 철학` | included | `templates.md` | Logic/presentation split and safe templates included. |
| `### 1.6 뷰 철학` | included | `templateview-htmx.md` | Simple views, request parameter, GET/POST clarity included. |
| `## 2. Django 코딩 스타일` | merged | `templates.md`, `templateview-htmx.md` | Relevant template and view style included below. |
| `### 2.6 템플릿 코딩 스타일` | included | `templates.md` | Extends/load spacing/endblock guidance included. |
| `### 2.7 뷰 코딩 스타일` | included | `templateview-htmx.md` | FBV first parameter `request` included. |
| `## 3. 프로젝트 구조와 앱 설계` | delegated-to-other-skill | `implementation-django` | General Django project/app/settings structure belongs to core Django skill. |
| `## 4. 모델 설계 패턴` / `### 4.1 Fat Model, Thin View` | included | `SKILL.md`, `templateview-htmx.md` | Thin views and no template domain rules included. |
| `## 5. QuerySet과 Manager 패턴` | delegated-to-other-skill | `implementation-django` | QuerySet/Manager implementation belongs to Django core skill. |
| `## 6. 뷰 패턴: CBV vs FBV` | included | `templateview-htmx.md` | TemplateView/Generic CBV/FBV choice included. |
| `### 6.1 선택 기준` | included | `templateview-htmx.md` | View choice criteria included. |
| `### 6.2 CBV 올바른 사용` | merged | `templateview-htmx.md` | Generic CBV use included without copying examples. |
| `### 6.3 Mixin 활용 패턴` | included | `templateview-htmx.md` | Mixin MRO, single concern, and chain caution included. |
| `### 6.4 FBV 올바른 사용` | included | `templateview-htmx.md` | FBV for custom flow and request parameter included. |
| `## 7. 폼과 유효성 검증` | included | `templateview-htmx.md` | Form boundary and validation included. |
| `### 7.1 폼 유효성 검증 순서` | included | `templateview-htmx.md` | Field cleaning, field-specific clean method, and form-wide clean order included. |
| `### 7.2 ModelForm 활용` | included | `templateview-htmx.md`, `SKILL.md` | Explicit `ModelForm.Meta.fields` and no `__all__` or `exclude` included. |
| `### 7.3 커스텀 Validator 재사용` | included | `templateview-htmx.md` | Reusable validator guidance included. |
| `## 8. Django REST Framework 패턴` | delegated-to-other-skill | `implementation-django-ninja` | DRF/API work is not web skill responsibility. |
| `## 9. 시그널 사용 가이드라인` | delegated-to-other-skill | `implementation-django` | Signals/event timing belong to core Django/DDD skills. |
| `## 10. 마이그레이션 베스트 프랙티스` | delegated-to-other-skill | `implementation-django`, `architecture-db` | Migration rollout belongs elsewhere. |
| `## 11. 성능 최적화` | merged | `templateview-htmx.md` | Web-facing N+1 avoidance included; deeper DB performance delegated. |
| `## 12. 캐싱 전략` | delegated-to-other-skill | `implementation-django` | General caching strategy belongs to core Django skill. |
| `## 13. 보안` | included | `csrf-ajax.md`, `templateview-htmx.md` | CSRF, XSS, SQL injection safety, auth/permission, secure settings, deploy checks included. |
| `### 13.1 Django 내장 보안 기능` | included | `csrf-ajax.md` | CSRF/XSS/clickjacking protections and SQL injection cautions included. |
| `### 13.2 보안 설정 체크리스트` | included | `csrf-ajax.md` | HTTPS, secure cookies, HSTS, frame/content settings included. |
| `### 13.3 Raw SQL 안전하게 사용` | included | `csrf-ajax.md` | Raw SQL string interpolation is forbidden; deeper query design routes to `implementation-django`. |
| `### 13.4 인증과 인가` | included | `templateview-htmx.md` | FBV decorators, CBV mixins, and no template-owned permission policy included. |
| `## 14. 테스트 패턴` | delegated-to-other-skill | `implementation-test` | Test mechanics belong to test skill; web verification criteria stay here. |
| `## 15. 미들웨어` | included | `csrf-ajax.md` | Middleware ordering and safety included. |
| `## 16. Django와 서비스 레이어 아키텍처` | delegated-to-other-skill | `implementation-django`, `architecture-implementation-patterns` | Service layer architecture belongs outside web rendering skill. |
| `## 17. Django 5.x 새 기능` | delegated-to-other-skill | `implementation-django` | General version feature guidance belongs to core Django skill. |
| `## 참고 자료` | omitted | n/a | Bibliography is source provenance, not runtime behavior. |
| `workspace docs static/HTMX/CSRF product references` | included | `static-assets.md`, `templateview-htmx.md`, `csrf-ajax.md` | Product-level static files, CSS/JS, HTMX, CSRF for AJAX covered despite source gap. |

## Review Notes

- 2026-05-10 source self-review: found source-backed gaps in test-mechanics delegation, API/DB boundary wording, Korean trigger coverage, and stale review claims from an earlier draft. Runtime wording and metadata were updated; this note now only records evidence from the current evaluation loop.
- 2026-05-10 independent source review by subagents found source-backed gaps in auth/permission coverage, ModelForm `exclude`, raw SQL safety, provisional static-source precision, agent metadata, and progressive reference loading. Runtime files and this crosswalk were updated.
- Independent source re-review reported blocking 0, major 0, minor 0.
- Rubric review ran after source self-review. No additional source-backed runtime issue remained; blocking 0, major 0, minor 0.
- Runtime checks: `codex debug prompt-input` smoke checks were run for positive, boundary/combined, and API negative prompts. The output exposes dddjango plugin metadata globally, so it is useful as a runtime cache/metadata exposure check but not as sole evidence of routing quality.
- Runtime behavior checks: read-only `codex exec` positive prompt used `implementation-django-web` and produced a TemplateView/template/static/HTMX/CSRF plan; boundary prompt used web, Django, and test references and separated service/HTMX/render-test responsibilities; negative REST API prompt rejected template-owned order creation logic and answered as API contract/service separation rather than web/template work.
- Validation so far: `validate_skill_docs.py --phase all`, `git diff --check`, leakage grep, cache sync, and source/cache diff passed. Actual Django render tests, browser screenshots, `collectstatic`, and pytest were not run because this was runtime skill evaluation, not an app implementation.
