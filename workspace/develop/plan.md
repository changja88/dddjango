# dddjango Plugin Development Plan

이 문서는 `dddjango` 플러그인을 실제 스킬 묶음으로 개발하기 위한 실행 계획과 진행 체크리스트이다.

기준 문서는 `workspace/docs`이고, source reference corpus는 `workspace/reference`이다. 개발 산출물은 기본적으로 workspace 안에 둔다. 플러그인 런타임이 요구하는 경우에만 repo root의 `dddjango/` 또는 설치된 plugin cache를 다룬다.

## 진행 현황

- 현재 단계: 종합 플러그인 평가 completion gate 통과
- 최근 완료: baseline isolation, public/operator artifact instruction 분리, 17개 public case baseline/with-dddjango 전체 재실행, post-review `case-017` finding rerun 해결, 평가 요약의 `plan.md` 통합
- 다음 작업: 필수 완료 게이트 없음. 차기 평가 고도화는 별도 backlog로 관리한다.

- [x] 기준 문서 정리: `workspace/docs`
- [x] 공통 평가 기준 작성: `workspace/develop/rubrics/common_rubric.md`
- [x] 개별 스킬 평가표 빈 파일 생성: `workspace/develop/rubrics/*_rubric.md`
- [x] 개별 스킬 평가표 작성
- [x] 개별 스킬 구현
- [x] 개별 스킬 평가 및 개선
- [x] 스킬 연계 평가표 작성
- [x] 스킬 연계용 스킬 구현
- [x] 스킬 연계 평가 및 개선
- [x] 종합 평가표 작성
- [x] 종합 플러그인 평가 및 개선
- [x] 최종 검증 및 커밋

## 0. Runtime Evaluation Preflight

목적:

- 평가 대상이 기존 설치 cache가 아니라 repo의 최신 `dddjango/` plugin bundle임을 고정한다.
- Codex local marketplace가 repo root에서 `./dddjango` plugin root를 발견하게 만든다.
- 성능 평가 전에 구조 검증, cache sync, smoke trigger 확인을 끝낸다.

체크리스트:

- [x] 평가 대상 canonical source를 `/Users/hyun/Desktop/dddjango/dddjango`로 고정한다.
- [x] repo root에 `.agents/plugins/marketplace.json`을 추가하고 `source.path`를 `./plugins/dddjango`로 지정한다.
- [x] `plugins/dddjango -> ../dddjango` symlink로 Codex local marketplace 표준 배치와 canonical source를 연결한다.
- [x] `dddjango/.codex-plugin/plugin.json` 버전을 기존 cache `0.1.9`보다 높은 `0.1.10`으로 맞춘다.
- [x] local marketplace 재등록 후 stale cache를 제거하고 repo source를 `dddjango/0.1.10` cache에 동기화한다.
- [x] 갱신된 cache가 `dddjango/0.1.10`이고 repo source와 동기화되었는지 확인한다.
- [x] `description` YAML plain scalar의 `: ` 문제를 block scalar로 수정해 12개 skill이 모두 로드되게 한다.
- [x] 새 Codex prompt input에서 12개 dddjango skill metadata가 로드되는지 확인한다.
- [x] smoke prompt 3개에서 dddjango 12개 skill metadata가 노출되는지 확인한다.
- [x] 개별 평가 prompt로 실제 trigger/routing 품질을 확인한다.

통과 기준:

- [x] `python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`가 통과한다.
- [x] `git diff --check -- dddjango .agents plugins workspace/docs/plugin-structure.md workspace/develop/plan.md workspace/scripts/validate_skill_docs.py`가 통과한다.
- [x] private rubric/scoring/expected/routing 누출 검색 결과가 없다.
- [x] Codex runtime cache와 repo source가 평가 대상 버전 기준으로 일치한다.

## 1. 개별 스킬 평가표 작성

목적:

- 각 스킬을 구현하기 전에 독립 평가 기준을 먼저 고정한다.
- trigger, routing, reference 반영, 금지 행동을 스킬별로 검증 가능하게 만든다.
- `common_rubric.md`를 공통 기준으로 사용하고, 스킬별 문서에는 해당 스킬 고유 책임만 추가한다.

체크리스트:

- [x] 공통 평가 기준을 작성한다: `common_rubric.md`
- [x] 스킬별 평가표 파일을 생성한다.
- [x] `implementation-django_rubric.md`를 작성한다.
- [x] `implementation-django-ninja_rubric.md`를 작성한다.
- [x] `implementation-django-web_rubric.md`를 작성한다.
- [x] `implementation-python_rubric.md`를 작성한다.
- [x] `implementation-cleancode_rubric.md`를 작성한다.
- [x] `implementation-tdd_rubric.md`를 작성한다.
- [x] `implementation-test_rubric.md`를 작성한다.
- [x] `architecture-ddd_rubric.md`를 작성한다.
- [x] `architecture-implementation-patterns_rubric.md`를 작성한다.
- [x] `architecture-db_rubric.md`를 작성한다.
- [x] `architecture-api_rubric.md`를 작성한다.
- [x] 각 평가표에 positive prompt, negative prompt, expected routing을 포함한다.
- [x] 각 평가표에 required reference coverage와 failure criteria를 포함한다.
- [x] provisional 스킬의 평가표에 fallback source와 한계를 명시한다.
- [x] 평가표 전체를 동일 agent의 네 관점 self-review로 리뷰하고 수정한다. 실제 subagent review는 이 단계에서 실행하지 않았다.
- [x] 공통 Language Policy를 `common_rubric.md`와 `rubric_goal_instructions.md`에 반영한다.
- [x] 각 평가표의 public prompt를 한국어 자연어, 한국어/영어 혼합, 구어적/모호한 사용자 요청, 단순 negative case까지 보강한다.
- [x] 각 평가표의 private grader key에 추가 public prompt family의 expected routing과 failure criteria를 반영한다.
- [x] 한국어 사용자 coverage, routing correctness, public/private integrity, product alignment, anti-overapplication 관점으로 파일별 self-review를 수행하고 남은 finding 0개로 정리한다. 실제 subagent review는 실행하지 않았다.

통과 기준:

- [x] 각 평가표가 해당 스킬 단독 책임을 검증한다.
- [x] 다른 스킬을 호출해야 하는 상황과 호출하지 않아야 하는 상황을 구분한다.
- [x] 단순 작업에 DDD나 subagent workflow를 과하게 적용하지 않는 negative case가 포함된다.
- [x] 모든 평가표가 `common_rubric.md`, `workspace/docs`, `workspace/reference`와 충돌하지 않는다.
- [x] 한국어/한영 혼합/구어체 prompt에서도 skill routing과 hard gate를 평가할 수 있다.
- [x] public eval material에는 expected routing, scenario classification, scoring key, hidden failure criteria가 노출되지 않는다.

한국어 coverage self-review:

- [x] `architecture-api_rubric.md`: 한국어 API 계약, Idempotency-Key, pagination/filtering prompt 보강; findings 0.
- [x] `architecture-db_rubric.md`: 기존 데이터 채우기, 필수값 전환, rolling deploy, 중복 저장 방지 prompt 보강; findings 0.
- [x] `architecture-ddd_rubric.md`: bounded context 언어 차이, coupon invariant, DDD 적용 범위 판단 prompt 보강; findings 0.
- [x] `architecture-implementation-patterns_rubric.md`: port/adapter, ACL, outbox, CQRS 적용/비적용 판단 prompt 보강; findings 0.
- [x] `implementation-django_rubric.md`: Django migration sequence, backfill, NOT NULL, transaction/on_commit prompt 보강; findings 0.
- [x] `implementation-django-ninja_rubric.md`: Django Ninja 구현, DRF-to-Ninja migration, fat Router 방지 prompt 보강; findings 0.
- [x] `implementation-django-web_rubric.md`: template/static, HTMX/CSRF, template business logic 방지 prompt 보강; findings 0.
- [x] `implementation-python_rubric.md`: Enum/StrEnum, pydantic boundary, Protocol 적용 판단 prompt 보강; findings 0.
- [x] `implementation-cleancode_rubric.md`: view/model/service 책임 분리, 중복/추상화 판단, 긴 함수 리뷰 prompt 보강; findings 0.
- [x] `implementation-tdd_rubric.md`: 실패 테스트 우선, boundary test, Red-Green-Refactor 순서 prompt 보강; findings 0.
- [x] `implementation-test_rubric.md`: API contract test, fixture/factory, fake/mock/flaky 판단 prompt 보강; findings 0.
- [x] `workflow-dddjango-subagents_rubric.md`: composite/risky, sequential fallback, false subagent claim, simple negative prompt 보강; findings 0.

## 2. 개별 스킬 구현

목적:

- 각 스킬을 독립적으로 사용할 수 있는 최소 runtime 단위로 구현한다.
- `SKILL.md`는 짧게 유지하고 세부 판단 기준은 `references/`로 분리한다.
- `implementation-*` 스킬을 바닥 스킬로 먼저 구현한 뒤 상위 판단 스킬을 구현한다.

공통 산출물:

- [x] `dddjango/.codex-plugin/plugin.json`
- [x] `dddjango/skills/<skill>/SKILL.md` (12개 runtime skill 완료)
- [x] `dddjango/skills/<skill>/agents/openai.yaml` (12개 runtime skill 완료)
- [x] `dddjango/skills/<skill>/references/*.md` (12개 runtime skill 완료)

구현 체크리스트:

- [x] 플러그인 파일 구조를 `workspace/docs/plugin-structure.md` 기준으로 만든다.
- [x] `implementation-django`를 구현한다.
- [x] `implementation-django-ninja`를 구현한다.
- [x] `implementation-django-web`을 구현한다.
- [x] `implementation-python`을 구현한다.
- [x] `implementation-cleancode`를 구현한다.
- [x] `implementation-tdd`를 구현한다.
- [x] `implementation-test`를 구현한다.
- [x] `architecture-ddd`를 구현한다.
- [x] `architecture-implementation-patterns`를 구현한다.
- [x] `architecture-db`를 구현한다.
- [x] `architecture-api`를 구현한다.
- [x] `workflow-dddjango-subagents`를 구현한다.
- [x] provisional 스킬은 완성본처럼 표시하지 않고 한계를 명시한다.
- [x] 모든 스킬의 `agents/openai.yaml`을 작성한다.

작성 기준:

- [x] frontmatter에는 `name`과 `description`만 둔다.
- [x] `description`에는 trigger와 routing 기준을 충분히 포함한다.
- [x] 본문에는 핵심 절차, reference 읽기 기준, 경계와 금지 사항만 둔다.
- [x] 긴 설명, 비교, 예시는 `references/`로 분리한다.
- [x] skill 내부에 README, installation guide, changelog를 만들지 않는다.
- [x] `SKILL.md`에서 모든 runtime reference가 직접 링크된다.
- [x] `agents/openai.yaml`이 `SKILL.md`와 의미적으로 일치한다.
- [x] `implementation-*` 스킬이 상위 workflow 없이도 단순 작업을 처리할 수 있다.

## 3. 개별 스킬 평가 및 개선

목적:

- 개별 스킬이 평가표 기준을 통과할 때까지 구현을 반복 개선한다.

반복 체크리스트:

- [x] 구조 검증을 실행한다.
- [x] 개별 평가 prompt를 실행한다.
- [x] 실패 원인을 `trigger`, `routing`, `instruction`, `reference`, `eval` 문제로 분류한다.
- [x] `description`, 본문, reference, 평가표 중 수정 대상을 정한다.
- [x] 수정 후 같은 평가를 다시 실행한다.
- [x] 실패가 발생하면 원인과 수정 위치를 기록한다.
- [x] 모든 개별 스킬의 통과 상태를 기록한다.

검증 명령:

```bash
python3 workspace/scripts/validate_skill_docs.py --phase generated --skills-dir dddjango/skills
```

통과 기준:

- [x] 개별 평가표의 필수 항목을 충족한다.
- [x] negative prompt에서 과한 skill routing이 발생하지 않는다.
- [x] 실행하지 않은 테스트나 검증을 완료했다고 말하지 않는다.
- [x] 모든 개별 스킬이 독립 실행 기준을 통과한다.

### Evaluation Progress

| Skill | Status | Source review | Runtime trigger checks | Rubric review | Notes |
|---|---|---|---|---|---|
| `implementation-django` | completed | blocking 0, major 0, minor 0 after fixing workflow routing, test boundary, crosswalk heading, and metadata wording | positive, boundary/combined, and negative prompts executed with `codex debug prompt-input`; read-only `codex exec` samples were also run for positive and boundary behavior before the final wording patch, and negative behavior after the final patch | blocking 0, major 0, minor 0; source-backed runtime issues reflected only | Cache synced to `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`; source/cache diff clean. Actual code/migration tests were not run because these were skill evaluation prompts, not a Django app implementation. |
| `implementation-django-ninja` | completed | blocking 0, major 0, minor 0 after fixing test boundary wording, `architecture-db` idempotency/locking routing, Korean trigger coverage, content negotiation delegation, and crosswalk heading coverage | positive, DRF migration/boundary, Korean auth/pagination/filtering, idempotency storage/locking, short-explanation negative, and greenfield DRF anti-trigger prompts executed with `codex debug prompt-input`; read-only `codex exec` samples were run for short explanation and greenfield DRF behavior | blocking 0, major 0, minor 0; source-backed runtime issues reflected only | Provisional status and fallback source remain explicit. Cache synced to `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`; source/cache diff clean. TestClient/OpenAPI/pytest were not run because these were skill evaluation prompts, not an app implementation. |
| `implementation-django-web` | completed | blocking 0, major 0, minor 0 after fixing test-mechanics delegation, API/DB routing, Korean trigger coverage, auth/permission coverage, ModelForm `exclude`, raw SQL safety, provisional static-source precision, metadata, and progressive reference loading | positive, boundary/combined, and API negative prompts executed with `codex debug prompt-input`; read-only `codex exec` samples were run for TemplateView/static/HTMX positive behavior, HTMX/CSRF/service/test boundary behavior, and REST API negative behavior | blocking 0, major 0, minor 0; source-backed runtime issues reflected only | Provisional status and fallback/product-source split remain explicit. Cache synced to `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`; source/cache diff clean. Render tests, browser screenshots, `collectstatic`, and pytest were not run because these were skill evaluation prompts, not an app implementation. |
| `implementation-python` | completed | blocking 0, major 0, minor 0 after fixing API/DB routing, function contract coverage, decorator signature preservation, class API shape, TypeVarTuple/type defaults, collection choice, Python 3.14 gates, Korean trigger coverage, Django Ninja boundary wording, and deprecation guidance | positive, pydantic-boundary, and simple negative prompts executed with `codex debug prompt-input`; read-only `codex exec` samples were run for state-transition typing, pydantic/domain boundary, and small helper type-hint behavior | blocking 0, major 0, minor 0; source-backed runtime issues reflected only | Cache synced to `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`; source/cache diff clean. Ruff, mypy, pyright, pytest, and runtime app checks were not run because these were skill evaluation prompts, not an app implementation. |
| `implementation-cleancode` | completed | blocking 0, major 0, minor 0 after fixing Korean trigger coverage, API/DB and pattern routing, Django Fat Model/View responsibility boundaries, detailed source/crosswalk heading coverage, state/error details, review/edit boundary, design-it-twice guidance, and false validation claim handling; independent source re-review by Socrates returned 0 findings | positive, boundary/view-logic, and simple negative prompts executed with `codex debug prompt-input`; isolated read-only `codex exec` samples were run in `/private/tmp/cleancode-smoke` for Fat Model, View Logic, and simple naming behavior | blocking 0, major 0, minor 0; source-backed runtime issues reflected only | Cache synced to `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`; source/cache diff clean. Pytest, Django checks, and app tests were not run because these were skill evaluation prompts, not a Django app implementation. |
| `implementation-tdd` | completed | blocking 0, major 0, minor 0 after fixing Korean trigger coverage, API/DB routing, risky/composite workflow routing, Source Coverage Crosswalk heading tracking, validation scenario heading coverage, test isolation guidance, mock-role/TDD boundary wording, and stale review claims; independent source re-review by Kierkegaard returned 0 findings | positive, composite boundary, and simple negative prompts executed with `codex debug prompt-input`; isolated read-only `codex exec` samples were run in `/private/tmp/tdd-smoke` for coupon-policy TDD planning, risky order API workflow/TDD boundary, and README typo negative behavior | blocking 0, major 0, minor 0; source-backed runtime issues reflected only | Cache synced to `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`; source/cache diff clean. Pytest and app tests were not run because these were skill evaluation prompts/read-only smoke checks, not a code implementation. |
| `implementation-test` | completed | blocking 0, major 0, minor 0 after fixing Korean trigger coverage, risky/composite workflow routing, broad workflow responsibility wording, validation scenario heading coverage, `spec.md` child-heading coverage, Risky Write Consistency Block coverage, stale review claims, and import-order negative boundary; independent source re-review and rubric review by Carver returned 0 findings | positive, boundary/combined, and import-order negative prompts executed with `codex debug prompt-input`; isolated read-only `codex exec` samples were run in `/private/tmp/test-smoke` for Django Ninja API contract tests, risky DDD/API/test workflow, and import-order negative behavior | blocking 0, major 0, minor 0; source-backed runtime issues reflected only and rubric-private material not copied | Cache synced to `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`; source/cache diff clean. Pytest, coverage, mutation testing, and app tests were not run because these were skill evaluation prompts/read-only smoke checks, not a code implementation. |
| `architecture-ddd` | completed | blocking 0, major 0, minor 0 after fixing Korean trigger coverage, risky/composite workflow routing, `spec.md` child-heading coverage, validation scenario heading coverage, Risky Write DDD handoff, metadata specificity, combined-work implementation boundary, and stale completion claims | positive, composite/risky boundary, and simple naming negative prompts executed with `codex debug prompt-input`; isolated read-only `codex exec` samples were run in `/private/tmp/ddd-smoke` for order DDD design, workflow handoff, and category-code naming behavior | blocking 0, major 0, minor 0; source-backed runtime issues reflected only and evaluation-only material not copied | Cache synced to `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`; source/cache diff clean. Pytest, Django checks, and app tests were not run because these were skill evaluation prompts/read-only smoke checks, not a code implementation. |
| `architecture-implementation-patterns` | completed | blocking 0, major 0, minor 0 after fixing Korean trigger coverage, direct pattern-selection vs workflow routing, layered dependency wording, `spec.md` child-heading coverage, validation scenario coverage, Risky Write Consistency Block output shape, metadata specificity, and stale review claims; independent source re-review returned 0 findings | positive, coordinated workflow boundary, and simple `verbose_name` negative prompts executed with `codex debug prompt-input`; isolated read-only `codex exec` samples were run in `/private/tmp/pattern-smoke` for payment pattern selection, workflow handoff, and negative direct-edit behavior, with positive re-run after block-heading wording fix | blocking 0, major 0, minor 0; source-backed runtime issues reflected only and evaluation-only material not copied | Provisional fallback status remains explicit. Cache synced to `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`; source/cache diff clean. Pytest, Django checks, and app tests were not run because these were skill evaluation prompts/read-only smoke checks, not a code implementation. |
| `architecture-db` | completed | blocking 0, major 0, minor 0 after fixing direct DB design vs workflow routing, Korean trigger coverage for idempotency/rollout/query-plan language, `spec.md` child-heading coverage, validation scenario coverage, ddd-implementation-standard heading coverage, stale review claims, and metadata specificity; independent source review returned 0 findings | positive DB concurrency, coordinated workflow boundary, and simple negative prompts executed with `codex debug prompt-input`; isolated read-only `codex exec` samples were run in `/private/tmp/db-smoke` for stock/reservation DB design, workflow handoff, and simple `verbose_name` negative behavior | blocking 0, major 0, minor 0; source-backed runtime issues reflected only and evaluation-only material not copied | Cache synced to `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`; source/cache diff clean. Pytest, Django checks, and app tests were not run because these were skill evaluation prompts/read-only smoke checks, not a code implementation. |
| `architecture-api` | completed | blocking 0, major 0, minor 0 after fixing direct API contract vs workflow routing, Korean trigger coverage for auth/header/compatibility language, `spec.md` child-heading coverage, validation scenario coverage, ddd-implementation-standard heading coverage, metadata specificity, API contract acceptance-criteria output, and stale review claims; independent source re-review returned 0 findings | positive API contract, coordinated workflow boundary, and simple Django negative prompts executed with `codex debug prompt-input`; isolated read-only `codex exec` samples were run in `/private/tmp/api-smoke` for order API contract, workflow handoff, and simple memo-field negative behavior | blocking 0, major 0, minor 0; source-backed runtime issues reflected only and evaluation-only material not copied | Cache synced to `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`; source/cache diff clean. Pytest, Django checks, OpenAPI generation, TestClient, and app tests were not run because these were skill evaluation prompts/read-only smoke checks, not a code implementation. |
| `workflow-dddjango-subagents` | completed | blocking 0, major 0, minor 0 after fixing stale review/rubric claims, source crosswalk heading precision, Korean trigger coverage for role-map/handoff/integration/check terms, `spec.md` child-heading coverage, validation scenario coverage, metadata wording, review-focused findings-first output order, canonical role responsibility coverage, handoff field pinning, and visible Risky Write Consistency Block output; independent source re-review returned 0 findings | positive composite/risky workflow, review-focused boundary, false-subagent claim, and simple Django negative prompts executed with `codex debug prompt-input`; isolated read-only `codex exec` samples were run in `/private/tmp/workflow-smoke` for composite order workflow, review findings-first workflow, false-claim correction, and simple memo-field negative behavior, with positive re-run after Risky Write block wording fix | blocking 0, major 0, minor 0; source-backed runtime issues reflected only and evaluation-only material not copied | Cache synced to `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`; source/cache diff clean. Pytest, Django checks, migrations, OpenAPI generation, and app tests were not run because these were skill evaluation prompts/read-only smoke checks, not a code implementation. |

Final runtime skill evaluation verification on 2026-05-10: `python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills` passed with 0 warnings; `git diff --check` was clean; runtime and current crosswalk leakage grep found no private grader/scoring/expected material; `/private/tmp/workflow-smoke/*.txt` leakage grep found no private evaluator material; source/cache `diff -qr dddjango /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10` was clean; final `codex debug prompt-input` smoke artifact at `/private/tmp/dddjango-final-runtime-debug.json` exposed all 12 dddjango skill metadata entries from cache version `0.1.10`.

## 4. 스킬 연계 평가표 작성

목적:

- 상위 스킬이 여러 하위 스킬을 조합하는 동작을 평가한다.
- DDD 구현 흐름이 실제 개발 작업에서 유지되는지 확인한다.

체크리스트:

- [x] `workflow-dddjango-subagents_rubric.md`를 작성한다.
- [x] 역할별 handoff 기대 산출물을 정의한다.
- [x] sequential fallback 기준을 정의한다.
- [x] integration checklist 기준을 정의한다.
- [x] 단순 작업에서 workflow를 생략하는 negative routing을 포함한다.
- [x] DDD 설계에서 Django 구현까지 이어지는 평가 prompt를 작성한다.
- [x] Django Ninja API 설계와 구현 연계 평가 prompt를 작성한다.
- [x] DB schema, transaction, migration 연계 평가 prompt를 작성한다.
- [x] TDD와 pytest 구현 연계 평가 prompt를 작성한다.

통과 기준:

- [x] 복합 작업에서는 `Role Map`, `Sequential Fallback`, `Handoff Contract`, `Integration Checklist`가 유지된다.
- [x] 역할별 책임과 관련 skill 구성이 `workspace/docs/workflow.md`와 일치한다.
- [x] Django template/static/web 책임이 있으면 `implementation-django-web`이 누락되지 않는다.
- [x] 연계 평가가 개별 스킬 평가와 중복되지 않고 조합 실패를 잡는다.

## 5. 스킬 연계용 스킬 구현

목적:

- 여러 하위 스킬을 조합하는 workflow skill을 구현한다.
- subagent 사용 가능 여부와 무관하게 같은 기준으로 작업을 진행할 수 있게 한다.

대상 스킬:

- `workflow-dddjango-subagents`

체크리스트:

- [x] `workflow-dddjango-subagents/SKILL.md`를 작성한다.
- [x] `workflow-dddjango-subagents/references/delegation-rules.md`를 작성한다.
- [x] `workflow-dddjango-subagents/references/role-map.md`를 작성한다.
- [x] `workflow-dddjango-subagents/references/handoff-contract.md`를 작성한다.
- [x] `workflow-dddjango-subagents/references/integration-checklist.md`를 작성한다.
- [x] `workflow-dddjango-subagents/agents/openai.yaml`을 작성한다.
- [x] subagent를 실제로 사용하지 않았다면 사용했다고 주장하지 않는 규칙을 포함한다.
- [x] subagent를 사용할 수 없을 때 sequential fallback을 제공한다.
- [x] 역할 분해가 DDD, DB, API, Django, Test, Review 책임을 축소하지 않게 한다.
- [x] cache를 수정한 경우 workspace canonical source와 대응 관계를 보고하도록 한다.

## 6. 스킬 연계 평가 및 개선

목적:

- 개별 스킬은 통과하지만 조합에서 실패하는 문제를 찾아 개선한다.

반복 체크리스트:

- [x] 연계 평가 prompt를 실행한다.
- [x] role map과 handoff 산출물을 확인한다.
- [x] 하위 스킬 reference가 필요한 시점에만 읽히는지 확인한다.
- [x] 과한 구조 적용이나 역할 누락을 수정한다.
- [x] 수정 후 같은 평가를 다시 실행한다.
- [x] 연계 실패 원인과 수정 위치를 기록한다.

검증 기준:

- `workspace/docs/validation-plan.md`
- `workspace/docs/workflow.md`

통과 기준:

- [x] 복합 작업에서 DDD 판단이 구현보다 먼저 나온다.
- [x] Django Ninja가 API 구현 표준으로 유지된다.
- [x] DB transaction, constraint, migration 책임이 구현 책임과 구분된다.
- [x] 테스트가 도메인 규칙과 API 계약을 보호한다.
- [x] 단순 prompt에서는 workflow를 출력하지 않는다.

## 7. 종합 평가표 작성

목적:

- 플러그인 전체가 하나의 제품처럼 동작하는지 평가한다.

체크리스트:

- [x] 종합 평가표를 작성한다: `workspace/develop/rubrics/plugin_rubric.md`
- [x] install/discovery 검증 항목을 포함한다.
- [x] Claude Code와 Codex 공통성 검증 항목을 포함한다.
- [x] runtime cache 동기화 검증 항목을 포함한다.
- [x] 전체 eval prompt 묶음을 작성한다: `workspace/develop/evals/cases/plugin/public`, `workspace/develop/evals/cases/plugin/private`

평가 항목:

- [x] 플러그인 구조
- [x] 스킬 발견과 trigger
- [x] 스킬 위계
- [x] reference 반영
- [x] DDD 구현 일관성
- [x] Django Ninja 표준
- [x] 과적용 방지
- [x] 검증 정직성
- [x] runtime cache와 workspace source 동기화

통과 기준:

- [x] 모든 스킬이 발견 가능한 구조로 생성된다.
- [x] `agents/openai.yaml`이 모든 스킬에 존재하고 `SKILL.md`와 일치한다.
- [x] `workspace/docs`와 runtime skill 구조가 충돌하지 않는다.
- [x] cache-only 변경이 완료 상태로 남지 않는다.

## 8. 종합 플러그인 평가 및 개선

목적:

- 실제 사용 가능한 플러그인 상태까지 검증하고 반복 개선한다.

평가 요약:

- 17개 public case에서 baseline/with-dddjango를 isolated workspace로 실행했다.
- baseline isolation 오염과 artifact instruction 충돌은 eval protocol 문제로 분류하고 runner/public packet을 수정했다.
- `case-017`의 `plugins/dddjango` real-directory 관찰은 실제 source layout 문제가 아니라 eval workspace copy가 symlink를 dereference한 문제였다.
- eval/code-capture workspace copy를 `symlinks=True`로 수정했고, targeted `case-017` with-dddjango rerun에서 해당 finding이 재발하지 않았다.
- 최종 response-level plugin integration judgment는 `85/85`, public case 통과는 `17/17`이다.
- 최종 open blocking/major/minor finding은 0이다.
- run별 raw/report/analysis/finding 메모는 완료 요약을 이 계획에 흡수한 뒤 저장소에서 정리한다.

반복 체크리스트:

- [x] 전체 구조 검증을 실행한다.
- [x] 개별 평가표를 실행한다.
- [x] 연계 평가표를 실행한다.
- [x] 종합 평가표를 실행한다.
- [x] 실패를 skill trigger, instruction, reference, workflow, eval 문제로 분류한다.
- [x] 수정 후 전체 검증을 다시 실행한다.
- [x] 평가 실패가 남아 있으면 실패 항목과 다음 수정 계획을 명시한다.

완료 게이트:

```bash
python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
```

완료 기준:

- [x] docs phase가 통과한다.
- [x] generated/all phase가 실제 `dddjango/skills`를 대상으로 통과한다.
- [x] runtime smoke만으로 완료 처리하지 않는다.
- [x] open blocking/major/minor finding이 0이거나, 남은 finding이 accepted exception 또는 rerun evidence로 닫힌다.
- [x] 최종 상태를 커밋한다.

차기 평가 고도화 backlog:

- [ ] scored code-backed case를 추가해 실제 코드 변경 품질을 점수화한다.
- [ ] progressive-disclosure 체크를 추가해 필요한 reference만 읽히는지 검증한다.
- [ ] trigger-mutation 체크를 추가해 유사/변형 프롬프트에서도 스킬 routing이 안정적인지 검증한다.
- [ ] runtime skill behavior가 바뀌면 동일한 isolated baseline protocol로 full public pack을 재실행한다.

## 개발 원칙

- [ ] 평가표를 먼저 만들고 스킬을 구현한다.
- [ ] 스킬은 간결하게 만들고 reference는 필요할 때만 읽히게 한다.
- [ ] 구현은 바닥 스킬에서 시작해 상위 workflow로 올라간다.
- [ ] 검증은 prompt, 산출물, diff, 로그, 리뷰 findings 같은 raw artifact를 기준으로 한다.
- [ ] subagent 검증은 가능한 경우 forward-test로 사용하되, 정답이나 의도한 수정 방향을 노출하지 않는다.
- [ ] 실제로 실행하지 않은 검증, 테스트, subagent 리뷰를 완료했다고 말하지 않는다.
