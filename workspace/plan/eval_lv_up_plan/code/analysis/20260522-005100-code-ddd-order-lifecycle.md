수정 대상: evaluator
원인 분류: evaluator

# architecture-ddd P4 code 평가 분석

## 문제

`case-code-ddd-order-placement`는 `Order.place`와 `Order.confirm` 같은 aggregate behavior 존재와 service의 직접 `status` 대입만 검사한다. 그러나 architecture-ddd runtime rule과 source reference는 aggregate-owned lifecycle state가 invariant를 보호할 때 외부에서 mutable public field로 바뀌면 안 된다고 본다.

현재 hidden check는 `order.status = ...` 같은 외부 직접 변경 가능성을 잡지 못한다. 따라서 service가 aggregate behavior를 호출하더라도 반환된 aggregate의 lifecycle 상태가 외부에서 직접 변경 가능하면 reference 기준보다 약하게 통과할 수 있다.

## 영향

- `Order` aggregate가 status invariant를 behavior method로만 보호한다는 P4 기준을 충분히 검증하지 못한다.
- reservation direct case는 lifecycle state 외부 변경 가능성을 검사하지만 order direct case는 동일한 위험을 놓친다.
- answer oracle과 evaluator가 architecture-ddd 개별 skill 목적을 같은 깊이로 검증하지 못한다.

## 수정 방향

- public case에 lifecycle 상태 직접 변경 방지 요구를 명시한다.
- answer oracle의 required behavior, `ddd_observations`, scoring checks, test evidence에 외부 직접 상태 변경 방지를 추가한다.
- `eval_code_behavior_checks.py`에서 `Order` lifecycle 상태가 외부에서 직접 `CONFIRMED`로 바뀌면 실패하게 한다.
- service 직접 mutation 검사는 AST 기반으로 `status`, `_status`, `setattr(..., "status")`, `setattr(..., "_status")`를 함께 잡는다.

## 리뷰 방식

리뷰 방식: real-subagent

skill-creator 관점 리뷰에서 Major로 지적된 항목을 근거로 수정한다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
