# C05 Baseline: 인벤토리 예약과 동시성 설계

필수 기대 기준:

- 재고 예약을 명시적 도메인 개념으로 모델링한다.
- 주문 생성과 재고 차감의 트랜잭션 경계를 설명한다.
- 동시 주문에는 `select_for_update`, optimistic locking, unique constraint 중 적절한 전략을 제시한다.
- 중복 요청에는 idempotency key 또는 unique constraint를 사용한다.
- 롤백과 실패 결과를 명확히 다룬다.
- pytest로 동시성, 중복 요청, 롤백 케이스를 검증한다.
