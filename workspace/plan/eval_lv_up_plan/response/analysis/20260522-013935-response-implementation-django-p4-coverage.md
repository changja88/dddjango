수정 대상: case
원인 분류: coverage gap

# implementation-django P4 평가 분석

## 범위

- 대상 skill: `dddjango/skills/implementation-django/`
- source reference: `workspace/reference/implementation-django/reference/final.md`
- 관련 bucket: `response`, `code`

## 확인한 기준

`implementation-django`는 이미 범위가 정해진 Django 구현 작업에서 다음 기준을 검증해야 한다.

- Django model, ORM, QuerySet, Manager
- service/selector와 application service 책임
- migration, `RunPython`, historical model, expand/backfill/contract
- transaction boundary, `transaction.atomic()`, `on_commit()`
- settings, caching, security, performance
- 기존 DRF maintenance/review는 adapter 경계로 다루고, 신규 API 표준으로 DRF를 권장하지 않음
- 단순 CRUD나 작은 rename에는 DDD/workflow/repository/UoW를 과적용하지 않음

## Inventory

| bucket | case id | public | answer | evaluator 관련성 | 수정 여부 | targeted eval 필요 | run id / status |
|---|---|---|---|---|---|---|---|
| response | `case-response-django-orm-service` | ORM/service/transaction/performance/cache 계획을 묻는다. | implementation-django source/runtime basis 직접 연결 | positive response coverage | case/answer 추가 | 필요 | `20260522-014626-response-try01-targeted-implementation-django-p4` / pass |
| response | `case-response-django-drf-maintenance` | 기존 DRF 유지보수를 adapter cleanup으로 묻는다. | existing DRF maintenance와 DRF greenfield 금지 직접 연결 | positive response coverage | case/answer 추가 | 필요 | `20260522-014819-response-try01-targeted-implementation-django-p4` / pass |
| response | `case-response-operational-migration` | 운영 migration 계획을 묻는다. | migration source/runtime basis 보강 | migration/rollout 일부 검증 | answer 보강 | 필요 | `20260522-030622-response-try01-targeted-implementation-django-p4` / pass |
| response | `case-response-simple-rename` | 작은 Django field rename에서 짧은 답을 요구한다. | implementation-django restraint와 migration basis 보강 | negative restraint 검증 | answer 보강 | 필요 | `20260522-030817-response-try01-targeted-implementation-django-p4` / pass |
| response | `case-response-drf-ninja` | DRF에서 Ninja 전환 계획을 묻는다. | DRF guardrail은 검증하지만 기존 DRF 유지보수 자체는 아니다. | implementation-django 목적에는 보조 | 수정 없음 | 불필요 | not run |
| code | `case-code-django-orm-service` | fixture에서 QuerySet/Manager, selector/service, transaction/on_commit 구현을 요구한다. | implementation-django source/runtime basis 직접 연결 | positive code-backed coverage | case/answer 추가 | 필요 | `20260522-024704-code-try01-targeted-implementation-django-p4` / pass; earlier `20260522-022502...` and `20260522-023515...` failed positive delta gate |
| code | `case-code-status-migration` | fixture에서 status migration 초안 작성을 요구한다. | migration source/runtime basis 보강, baseline pass reason 명시 | code-backed migration/honesty 검증 | answer 보강 | 필요 | `20260522-031819-code-try01-targeted-implementation-django-p4` / pass; earlier `20260522-015326...` failed expected delta gate and `20260522-025640...` exposed non-negative validator gap |
| code | `case-code-small-rename` | 작은 rename 코드 변경을 요구한다. | implementation-django restraint와 migration basis 보강 | negative code restraint 검증 | case/answer 보강 | 필요 | `20260522-034201-code-try01-targeted-implementation-django-p4` / pass; earlier `20260522-030221...` exposed non-negative validator gap and `20260522-032625...` exposed extra command-claim risk |

## Gap

P4 기준 1, 2, 4, 5에 Major gap이 있다. 기존 case는 migration과 restraint 일부를 다루지만, 개별 `implementation-django` skill의 positive coverage인 model/ORM/QuerySet/Manager, service/selector, transaction, caching, settings/security, query performance, existing DRF maintenance를 직접 검증하지 않는다.

Public case에 answer oracle, private 기준, 이전 run finding 누설은 확인되지 않았다. 그러나 evaluator가 `implementation-django` 전용 coverage tag와 answer basis를 강제하지 않아 같은 gap이 다시 생길 수 있다.

## 수정 방향

- `response` bucket에 positive case 2개를 추가한다.
  - `case-response-django-orm-service`: model/ORM/QuerySet/Manager, service/selector, transaction, performance, caching, settings/security 경계를 검증한다.
  - `case-response-django-drf-maintenance`: 기존 DRF maintenance에서 serializer/viewset을 adapter로 다루고 신규 DRF 권장을 금지하는지 검증한다.
- 기존 migration/restraint answer에 implementation-django runtime source basis와 coverage tag를 보강한다.
- `validate_eval_bucket_pack.py`가 implementation-django P4 coverage와 answer source basis를 구조적으로 확인하도록 한다.
- `code` bucket에 `case-code-django-orm-service`를 추가해 code-backed positive coverage gap을 닫는다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real subagent 2개를 실행했다. 첫 리뷰는 skill-creator 관점에서 trigger/purpose alignment, reference traceability, progressive disclosure, validation integrity를 검토했고, 둘째 리뷰는 독립 P4 관점에서 inventory completeness, public leakage, answer over/under-claim, evaluator alignment, P5 boundary를 검토했다.

skill-creator 리뷰: 최초 Blocker 0, Major 4, Minor 2. 조치: status migration control 분류, evidence_required 보강, broad source basis 제거, review/inventory 기록 보강, evaluator coverage 보강.

독립 리뷰: 최초 Blocker 0, Major 4, Minor 1. 조치: code-backed positive case 추가, status migration outcome semantics 정리, workflow role-map basis 제거, review evidence 기록 보강, completion inventory 보강.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
