# DB 트랜잭션/멱등성 설계

주문 생성과 재고 예약은 하나의 트랜잭션 경계 안에서 처리하되, 외부 결제나 메시지
발행은 커밋 이후로 분리합니다. Django에서는 `transaction.atomic()`으로 재고
예약 경계를 잡습니다.

동시성 제어는 재고 행을 `select_for_update()`로 잠그는 비관적 잠금을 기본으로
두고, 충돌 빈도가 낮은 경우에는 `version` 컬럼을 둔 optimistic locking을 대안으로
검토합니다.

중복 요청은 `Idempotency-Key`를 저장소에 기록하고 payload hash와 응답 요약을
함께 보관합니다. DB에는 `UniqueConstraint`를 추가해서 같은 멱등 키가 중복 저장되지
않게 하고, `IntegrityError`가 발생하면 기존 처리 결과를 조회합니다.

검증은 동시 요청 테스트, 중복 요청 테스트, 롤백 테스트로 나눕니다. 실제 테스트는
실행하지 않았습니다. 실행할 명령은 `pytest`입니다.
