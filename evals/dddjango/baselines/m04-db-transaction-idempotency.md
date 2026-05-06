# M04 Baseline: DB transaction and idempotency

필수 기대 기준:

- 주문 생성과 재고 예약의 트랜잭션 경계를 명확히 나눈다.
- 동시성 제어는 `select_for_update` 또는 optimistic locking/version 전략 중 하나를 설명한다.
- 중복 요청은 `Idempotency-Key` 또는 도메인 고유 키 저장소로 처리한다.
- DB `UniqueConstraint`와 `IntegrityError`/재시도 처리를 포함한다.
- 롤백, 재시도, 검증 방법을 구체적으로 제시한다.
- “락은 필요 없다”, “중복 요청은 무시해도 된다”처럼 위험한 단순화를 하지 않는다.
