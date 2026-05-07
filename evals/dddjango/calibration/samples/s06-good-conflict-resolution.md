# 역할 간 충돌 통합 판단

## Role Map

| Role | Responsibility | dddjango skills | File ownership |
| --- | --- | --- | --- |
| Coordinator | conflict priority를 적용해 최종 판단 | workflow-dddjango-subagents | 통합 결정 |
| Domain Agent | `Order.confirm()` 도메인 불변식과 상태 전이 정의 | architecture-ddd | domain/** |
| API Agent | command endpoint와 API contract 정리 | implementation-django-ninja | api/router.py |
| Test Agent | 상태 전이와 API 거부 테스트 설계 | implementation-test | tests/** |
| Review Agent | router 직접 상태 변경 여부 점검 | implementation-cleancode | review |

실제로 실행하지 않았습니다. 가정 기반 역할 분해이며 순차 실행으로 판단합니다.

## Handoff Contract

### Scope

`PATCH /orders/{id}`에서 status를 직접 바꾸자는 제안과 `Order.confirm()` 불변식의 충돌 해결.

### Decisions

최종 판단: 도메인 불변식이 API 편의보다 우선입니다. status 직접 변경 금지입니다.
API는 `Order.confirm()`을 우회하지 말고 application service 또는 유스케이스를 호출해야 합니다.

```python
@router.post("/orders/{order_id}/confirm", response={200: OrderOut, 409: ProblemDetail})
def confirm_order(request, order_id: int):
    order = confirm_order_service(order_id=order_id, actor=request.user)
    return 200, OrderOut.model_validate(order)
```

`PATCH /orders/{id}` schema에서는 status를 제외합니다.

### Required Follow-up

- application service에서 transaction.atomic과 repository 조회를 적용한다.
- 결제/재고/배송 side effect가 있으면 도메인 이벤트 또는 outbox 필요성을 검토한다.
- test는 PENDING -> CONFIRMED 성공, 취소 주문 confirm 실패, status PATCH 거부를 포함한다.

## Integration Checklist

- 도메인 불변식
- transaction
- API contract
- test
- conflict priority
