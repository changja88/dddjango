재고 차감, 예약 확정, 결제 승인, 알림 발송이 같은 주문 흐름에서 동시에 들어오는 상황을 설계해줘.

DDD, DB, API, Django 구현, Test 역할을 나누고 각 역할이 무엇을 결정해서 누구에게 넘기는지 정리해줘. 마지막에 integration owner가 어떤 위험을 닫는지도 적어줘.

aggregate invariant, transaction owner, locking/isolation, uniqueness/idempotency storage, `Idempotency-Key` replay/conflict behavior, 외부 결제/알림 side effect timing, retry/isolation, concurrency/integration test 기준이 빠지지 않게 해줘.
