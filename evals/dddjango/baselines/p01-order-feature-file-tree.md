# p01-order-feature-file-tree baseline

좋은 답변은 주문 생성 기능을 한 파일이나 router 함수에 몰아넣지 않고, 최소한
아래 경계를 제시한다.

- `orders/domain/`: 애그리거트, 값 객체, 도메인 예외, 불변식.
- `orders/services.py` 또는 `orders/usecases.py`: transaction 경계 안에서
  repository/service를 조합하는 application 흐름.
- `orders/api/schemas.py`: Django Ninja `Schema` 입출력과 Problem Details 오류.
- `orders/api/routers.py`: `Router`, `response={...}` mapping, thin endpoint.
- `orders/tests/`: pytest 기반 RED/GREEN/REFACTOR 테스트 계획.

router/view에서 상태 전이, 할인, 재고 예약 같은 비즈니스 규칙을 직접 처리하면
실패로 본다. 새 코드에는 DRF import, Serializer, ViewSet을 만들지 않는다.
