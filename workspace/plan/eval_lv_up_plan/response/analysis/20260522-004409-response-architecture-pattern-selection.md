수정 대상: case
원인 분류: case

# architecture-implementation-patterns P4 response case 분석

## 문제

`response` bucket의 `eval_goal.md`는 `Architecture Pattern Selection` 대표 시나리오와 implementation pattern choice를 최소 coverage로 요구하지만, 현재 public/answer case에는 `architecture-implementation-patterns` 단독 목적을 직접 검증하는 positive case가 없다.

현재 관련 case는 다음처럼 보조적이다.

- `case-response-order-create`: 주문 생성 API의 DDD/DB/API/Django Ninja/Test 복합 설계를 검증한다. repository/UoW 과적용 금지는 포함하지만, 개별 implementation pattern 선택 기준을 단독으로 검증하지 않는다.
- `case-response-simple-rename`: 단순 rename에서 repository/UoW/DDD/workflow 과적용을 막는 negative case다.

따라서 layered/clean/hexagonal, ports/adapters, dependency direction, repository/UoW, CQRS, event sourcing, saga, outbox, ACL, service layer를 reference 기준으로 선택하거나 제외하는 positive 검증이 부족하다.

## 영향

- P4 기준 1, 2, 4, 5를 충분히 만족하지 못한다.
- answer oracle이 `workspace/reference/architecture-implementation-patterns/reference/final.md`와 runtime bundled references를 직접 기준으로 삼는 case가 없다.
- 단순 negative restraint는 있으나 사용 조건과 제외 조건을 한 응답에서 함께 판정하는 case가 부족하다.

## 수정 방향

- `response` bucket에 `case-response-architecture-pattern-selection` public case와 matching answer oracle을 추가한다.
- public case는 evaluator-only answer, private 기준, 이전 run finding을 노출하지 않고 사용자-facing architecture pattern 판단 요청으로 작성한다.
- answer oracle은 source reference보다 과도한 구현 산출물을 요구하지 않고, pattern-level 판단과 owning-skill handoff만 요구한다.

## 리뷰

리뷰 방식: not-run
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

수정 후 real-subagent 리뷰에서 trigger, 목적, reference, progressive disclosure, validation integrity를 다시 확인한다.
