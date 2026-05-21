수정 대상: reference

# implementation-django P1 reference 반영도 점검

## 점검 목적

`dddjango:implementation-django`는 이미 범위가 정해진 Django 구현 작업에서 모델, ORM/QuerySet/Manager, 서비스/셀렉터, 마이그레이션, 트랜잭션, settings, caching, security, performance, Django 구현 수용 기준을 runtime에서 실행 가능한 규칙으로 안내해야 한다.

## 기준 reference

- 기준 reference: `workspace/reference/implementation-django/reference/final.md`
- runtime skill: `dddjango/skills/implementation-django/SKILL.md`
- bundled reference: `dddjango/skills/implementation-django/references/*.md`
- 관련 handoff skill: `implementation-django-ninja`, `architecture-db`, `architecture-api`, `implementation-django-web`, `implementation-test`, `implementation-python`, `workflow-dddjango-subagents`

## 핵심 근거

- `SKILL.md`는 Django 5.x/LTS 구현, ORM, 서비스/셀렉터, migration, transaction, settings, caching, security, performance, Django integration test acceptance를 trigger로 선언한다.
- bundled reference는 `models-orm.md`, `services-selectors.md`, `migrations.md`, `transactions-performance-security.md`로 나뉘어 progressive disclosure 구조를 유지한다.
- source reference는 Django/DRF를 한 문서에서 다루며 `Django REST Framework 패턴`을 Serializer, ViewSet, Router, Permission, Pagination, Versioning의 정상 구현 지침처럼 제시한다.
- runtime skill과 `implementation-django-ninja`는 greenfield DRF 구현 요청을 Django Ninja로 전환하고, DRF 자료는 legacy review, migration, compatibility, comparison에만 쓰도록 한다.
- source reference는 transaction/idempotency/risky-write 기준을 runtime 수준만큼 직접 다루지 않는다. `select_for_update()`는 주로 `TransactionTestCase` 선택 기준에서만 확인된다.

## 통합 판단

reference 상태: 개선 필요

수정 대상 후보: reference

기준 reference는 Django 모델, ORM, QuerySet/Manager, 프로젝트 구조, settings, migration, performance, caching, security, test, service/selector의 일반 기준을 제공하므로 P1 점검 자체를 막지는 않는다. 다만 다음 두 축은 runtime skill의 판단 근거를 왜곡할 수 있어 reference 개선이 먼저 필요하다.

1. DRF와 Django Ninja의 책임 결정이 source reference와 runtime skill 사이에서 정렬되어 있지 않다.
   - source reference는 DRF Serializer/ViewSet/Router를 first-class 구현 guidance처럼 다룬다.
   - runtime skill은 API endpoint 구현을 `implementation-django-ninja`로 넘기고, 새 API에서 DRF `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`를 표준으로 권하지 말라고 한다.
   - 이 차이는 단순 압축 문제가 아니라 product/runtime decision의 source 근거 누락이다.

2. risky write, idempotency, locking, isolation/retry, `Idempotency-Key` handoff의 provenance가 `implementation-django` source reference 안에서는 약하다.
   - runtime skill은 `Risky Write Consistency Block`을 요구한다.
   - `architecture-db`도 risky transaction, locking, isolation, idempotency storage를 owns 한다.
   - source reference가 Django 구현 skill과 DB/API architecture skill 사이의 책임 경계를 충분히 결정하지 않아 handoff 판단이 runtime 쪽에 먼저 생겨 있다.

## skill 반영도

skill 반영도: 부분 충분, reference decision 필요

- 충분한 부분: 모델 메서드와 서비스/셀렉터 선택, QuerySet/Manager, migration historical model, expand/backfill/contract, N+1 대응, caching/security/middleware/test acceptance는 bundled reference에 압축되어 있다.
- 부족한 부분: DRF guardrail과 Django Ninja 전환 기준, risky-write consistency block의 source provenance, form/model-form 책임 경계, Django-specific coding style의 포함/제외 결정은 source reference에서 먼저 확정해야 한다.
- `agents/openai.yaml`은 settings, caching, security, performance를 short description/default prompt에 드러내지 않는다. 그러나 primary issue가 source decision gap이므로 P1에서는 skill 수정 후보가 아니라 reference 정렬 후 P2에서 재검토할 보조 관찰로 둔다.

## 책임 경계

책임 경계: reference decision 전제 하에 대체로 적절하나 DRF/API와 risky write 축은 재정렬 필요

- API contract 설계는 `architecture-api`, Django Ninja endpoint 구현은 `implementation-django-ninja`, ORM/service/migration 구현은 `implementation-django`로 넘기는 현재 runtime 방향은 dddjango runtime decision과 맞다.
- DB schema, constraint, transaction isolation, locking, rollout risk가 undecided이면 `architecture-db`를 먼저 쓰는 handoff도 적절하다.
- 다만 source reference가 DRF를 정상 구현 guidance처럼 유지하는 동안 `implementation-django`가 DRF guardrail을 단정하면 source/runtime 충돌로 남는다.
- risky write block은 `implementation-django`가 concrete Django implementation acceptance를 기록하는 역할인지, `architecture-db`/`architecture-api`가 결정한 항목을 구현 단계에서 확인하는 역할인지 reference에서 분리해야 한다.

## eval 점검 필요 여부

eval 점검 필요 여부: 있음, reference 개선 후 source/runtime crosswalk와 DRF guardrail coverage를 P4에서 재검토

- `workspace/develop/eval/source/eval_goal.md`는 사람이 읽을 수 있는 crosswalk가 source provenance, conflict/gap decision, provisional handling, DRF guardrail, validation coverage, eval bucket traceability를 덮어야 한다고 한다.
- 현재 `validate_skill_docs.py`와 `validate_eval_bucket_pack.py`는 구조 검증과 contamination 검증 중심이며, 위 semantic conflict를 통과 상태로 둘 수 있다.
- 단, P1의 다음 수정 대상은 eval이 아니라 reference다. eval case/answer/evaluator 조정은 reference decision 이후 별도 P4 또는 failure loop에서 판단한다.

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

Subagent 리뷰/순차 fallback: real-subagent `019e49d7-7123-7243-889f-c31246b4233e`가 read-only 독립 리뷰를 수행했다. 원 리뷰는 Blocker 0, Major 3, Minor 3, Note 2를 보고했다. 통합 판단에서는 Major/Minor를 열린 이슈로 남기지 않고 `reference` 개선 후보와 P2/P4 보조 재검토 항목으로 분류했다.

skill-creator 리뷰: real-subagent가 목적 명확성, trigger description, progressive disclosure, reference 중복/누락, validation integrity를 함께 점검했다. 메인 점검에서도 `/Users/hyun/.codex/skills/.system/skill-creator/SKILL.md`를 읽고 SKILL.md가 짧고 one-level bundled reference를 직접 링크하는 구조를 확인했다.

통합 리뷰 결과:

- Blocker: 0
- Major: 0
- 열린 Minor: 0
- Note: core Django 구현 기준은 대부분 runtime reference에 압축되어 있으나, DRF guardrail과 risky-write provenance는 reference 개선 계획으로 넘긴다.

## 후속 분석 문서 위치

후속 분석 문서 위치: `workspace/plan/reference_lv_up_plan/implementation-django/analysis/20260521-182556-implementation-django-p1-reference.md`

## 다음 단계

다음 단계: reference 개선 계획

- `workspace/plan/reference_lv_up_plan/implementation-django/plan/` 아래에 같은 기준의 계획 문서를 별도 작성한다.
- 계획에서는 DRF material을 legacy/fallback/compatibility로 재분류할지, Django Ninja product decision을 implementation-django reference에 반영할지 결정한다.
- 계획에서는 transaction/idempotency/risky-write 기준의 source 위치와 `architecture-db`, `architecture-api`, `implementation-django` handoff 문장을 확정한다.
- reference 개선 전에는 `dddjango/skills/implementation-django/SKILL.md`, bundled reference, eval case/answer를 바로 수정하지 않는다.

## 종료 조건 충족 여부

종료 조건 충족 여부: 충족

- 기준 reference 상태: `개선 필요`로 확정했다.
- 수정 대상 후보: `reference`로 확정했다.
- Blocker와 Major: 통합 후 0개다.
- 열린 Minor: 0개다. P1 밖 항목은 Note와 다음 단계로 내렸다.
- subagent 리뷰: 실행했고 결과를 수집했다.
- skill-creator 관점 리뷰: real-subagent와 메인 순차 확인으로 수행했다.
- 다음 단계: `reference 개선 계획`으로 확정했다.
- 후속 분석 문서: 지정된 `reference_lv_up_plan/implementation-django/analysis/` 아래에 작성했다.
- 개선 계획 문서: P1에서는 작성하지 않았다.
- 실제로 실행하지 않은 검증, 리뷰, subagent 작업을 실행한 것처럼 기록하지 않았다.

## 검증/미검증

검증/미검증:

- 실행: `uv run pytest workspace/scripts/test_validate_plan_constraints.py` 통과.
- 실행: `uv run python workspace/scripts/validate_plan_constraints.py` 통과.
- 실행: `uv run python workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills` 통과.
- 미실행: eval bucket run. P1은 reference 개선 후보 확정 단계이며 eval 수정 또는 eval run 단계가 아니다.
- 미실행: runtime cache sync. P1에서 runtime cache를 수정하지 않았다.
