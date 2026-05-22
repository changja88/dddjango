수정 대상: case
원인 분류: coverage gap

# implementation-django code positive coverage 분석

## 문제

`code` bucket의 implementation-django 관련 case는 현재 migration 지원 case와 작은 rename restraint case 중심이다. `workspace/develop/eval/code/eval_goal.md`는 실제 코드 변경에서 Django model, QuerySet/Manager, service/selector, transaction, performance/security 기준을 검증해야 한다.

`response` bucket의 `case-response-django-orm-service`가 같은 판단을 답변으로 검증하지만, code-backed 산출물에서 QuerySet/Manager, selector/service, `transaction.atomic()`, `transaction.on_commit()`, query-count 검증, cache invalidation owner를 확인하는 positive case가 없다.

## 수정 방향

- `django_shop_service` fixture를 사용하는 code case를 추가한다.
- public prompt는 주문 목록/확정 use case 구현을 요구하고 REST/API 계약 설계로 확장하지 않는다.
- answer oracle은 `implementation-django` source/runtime references에 직접 trace한다.
- `code-capture.json`에 새 case의 subject repo를 추가한다.
- `validate_eval_bucket_pack.py`가 code bucket의 implementation-django positive coverage tag를 확인하도록 한다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: 독립 리뷰에서 code-side implementation-django coverage가 Major gap으로 확인됐다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0
