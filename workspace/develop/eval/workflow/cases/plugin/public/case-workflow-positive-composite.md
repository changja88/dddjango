주문 생성, 재고 예약, 결제 승인, 중복 요청 방지가 모두 얽힌 Django 작업을 진행하려고 해.

DDD 모델링, DB 제약/트랜잭션, Django Ninja API, Django 구현, 테스트가 모두 필요해. subagent를 쓸 수 있으면 역할별로 나누고, 쓸 수 없으면 같은 순서로 순차 진행 계획을 세워줘.

aggregate invariant, transaction owner, locking/isolation, uniqueness/idempotency storage, `Idempotency-Key` replay/conflict, 결제 승인과 알림의 side effect timing, retry/isolation, concurrency/integration test 기준도 역할별 handoff와 integration owner 판단에 포함해줘.
