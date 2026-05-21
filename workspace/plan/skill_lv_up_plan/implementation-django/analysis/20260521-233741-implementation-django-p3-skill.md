수정 대상: skill

# implementation-django P3 분석

## 점검 범위

- 대상 skill: `dddjango/skills/implementation-django/`
- source reference: `workspace/reference/implementation-django/reference/final.md`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django/`
- 비교 skill: `architecture-ddd`, `architecture-db`, `architecture-api`, `architecture-implementation-patterns`, `implementation-django-ninja`, `implementation-django-web`, `implementation-test`, `source-reference-audit`, `workflow-dddjango-subagents`

## 현재 상태

- `SKILL.md`는 41줄로 500줄 미만이다.
- bundled reference 5개는 `SKILL.md`의 `Reference Loading`에서 모두 1단계 직접 링크로 발견된다.
- runtime cache와 source skill은 점검 시작 시 `diff -qr` 기준 동일했다.
- source reference는 Django 5.x/LTS, 모델/ORM, migration, transaction, performance, security, DRF 유지보수, service layer 판단을 폭넓게 제공한다.

## 발견 사항

### Major 1: 구현 아키텍처 패턴 handoff가 명시적으로 부족함

- 증거: `implementation-django/SKILL.md`는 repository/UoW를 기본 도입하지 말라는 runtime rule은 담고 있으나, repository/UoW/ports/outbox/ACL 같은 구현 아키텍처 결정 자체가 미정일 때 `architecture-implementation-patterns`로 넘기는 routing 기준을 직접 적지 않는다.
- 충돌 위험: `architecture-implementation-patterns`는 pattern-level decision을 소유하고, `implementation-django`는 concrete Django model/service/selector/migration code를 소유한다. handoff가 약하면 두 skill이 repository/UoW 또는 service layer 선택을 서로 다른 기준으로 판단할 수 있다.
- 조치: `SKILL.md` frontmatter와 `Routing`에 `architecture-implementation-patterns` handoff를 추가한다.

### Major 2: risky write block이 미정 결정을 다시 수집할 수 있음

- 증거: `implementation-django/SKILL.md`의 `Risky Write Consistency Block` 문장이 transaction owner, lock/idempotency, DB constraint, `Idempotency-Key`, side-effect timing, isolation/retry, test plan을 모두 포함하라고만 말해, 미정 항목을 architecture/API/DB/pattern/test skill로 넘기는 기준이 약했다.
- 충돌 위험: risky write에서 `architecture-implementation-patterns`, `architecture-db`, `architecture-api`, `implementation-test`가 맡는 결정을 implementation skill이 재결정할 수 있다.
- 조치: block은 concrete Django implementation을 위한 already-decided inputs 요약으로 한정하고, 미정 항목은 owning skill로 handoff한다고 명시한다.

### Major 3: forms/views reference wording이 web skill 책임과 겹쳐 보일 수 있음

- 증거: `implementation-django/SKILL.md`와 `references/models-orm.md`가 forms/views를 넓게 언급한다. 반면 `implementation-django-web`은 TemplateView, Generic CBV/FBV, web forms, templates/static, HTMX, CSRF-aware frontend behavior를 명확히 소유한다.
- 충돌 위험: server-rendered web 화면 구현을 `implementation-django`가 직접 다룬다고 오해할 수 있다.
- 조치: `models-orm.md`와 `SKILL.md`의 reference loading 설명을 ORM/service 구현에 인접한 model/form/view/signal boundary 판단으로 좁힌다. web page composition, templates/static, HTMX, web forms 구현은 `implementation-django-web`로 넘긴다는 문구를 직접 둔다.

### Major 4: existing DRF maintenance trigger가 metadata에 부족함

- 증거: `SKILL.md` 본문은 `coding-style-drf-maintenance.md`와 existing DRF maintenance runtime rule을 직접 제공하지만, frontmatter와 `agents/openai.yaml`은 greenfield DRF-style request를 `implementation-django-ninja`로 넘기는 기준만 강하게 드러냈다.
- 충돌 위험: frontmatter가 primary trigger surface이므로 “existing DRF serializer/viewset review/maintenance” 요청에서 이 skill과 직접 연결된 bundled reference가 발견되지 않을 수 있다.
- 조치: `SKILL.md` description과 `agents/openai.yaml`에 existing/legacy DRF maintenance/review trigger를 추가하되, greenfield DRF는 계속 `implementation-django-ninja`로 넘기도록 유지한다.

## Reference 후속 필요 여부

- source reference는 넓은 Django framework reference 역할을 하므로 source 자체의 기준 부족은 확인되지 않았다.
- 이번 문제는 runtime skill의 handoff와 bundled reference wording 문제이므로 `reference_lv_up_plan/implementation-django` 후속 분석은 새로 만들지 않는다.

## 리뷰 방식

리뷰 방식: real-subagent
- skill-creator 리뷰: real-subagent가 Major 1, Minor 1을 보고했다. Major는 existing DRF maintenance/review trigger 부족으로, 본 수정에 반영했다. Minor는 `validate_skill_docs.py`에 `implementation-django` 전용 semantic routing check가 없다는 검증 도구 보강 후보이다. 이번 P3의 직접 수정 범위가 `implementation-django/**`이고, semantic drift는 subagent/manual review와 required validators로 확인하므로 target skill 기준 열린 Minor로 유지하지 않는다.
- 독립 책임 경계 리뷰: real-subagent가 Major 1, Minor 2를 보고했다. Major는 `Risky Write Consistency Block`의 미정 결정 재소유 위험으로, 본 수정에 반영했다. Minor 2개는 각각 `workflow-dddjango-subagents` role-map wording과 `implementation-django-ninja`의 transaction ownership wording에 관한 인접 skill 개선 후보이며, 이번 P3의 허용 수정 범위인 `implementation-django/**` 밖이다. `implementation-django`에는 이미 pattern handoff와 risky-write 미정 항목 handoff를 추가했으므로 target skill 기준 열린 Minor로 유지하지 않는다.

## 리뷰 결과

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
- 초기 메인 평가: Blocker 0, Major 4, 열린 Minor 0
- 독립 책임 경계 리뷰 통합 후 target skill 기준: Blocker 0, Major 0, 열린 Minor 0
- skill-creator 리뷰 통합 후 target skill 기준: Blocker 0, Major 0, 열린 Minor 0
