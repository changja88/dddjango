Fixture repo에서 주문 생성 API의 멱등성과 충돌 처리를 개선해줘.

요구사항:
- 주문 생성 결정은 service/usecase 책임으로 두고, Ninja Router는 얇은 adapter로 남겨줘.
- 같은 `Idempotency-Key`와 같은 payload는 새 주문을 만들지 않고 같은 응답 snapshot을 replay해야 해.
- 같은 `Idempotency-Key`와 다른 payload는 Problem Details conflict로 구분해야 해.
- 중복 방지는 DB unique constraint와 service transaction boundary에서 보장해야 해.
- 관련 서비스/API 테스트를 추가해.

가능하면 `python3 manage.py check`와 `python3 manage.py test`를 실행하고 결과를 보고해줘.
