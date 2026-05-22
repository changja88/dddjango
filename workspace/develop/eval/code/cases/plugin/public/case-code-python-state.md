결제 금액과 주문 상태 표현을 Python 타입으로 더 명확하게 리팩터링해줘.

요구사항:
- `Money`는 값 객체처럼 동작해야 하고, 다른 통화끼리 더하는 규칙을 테스트해.
- 주문 상태는 명시적 타입을 유지하되 과한 pydantic 모델을 도메인 기본값으로 만들지 마.
- fixture의 Python 버전을 존중하면서 필요한 경우 frozen dataclass나 Enum을 사용해.
- 변경 범위는 `apps/payments/**`, `apps/orders/models.py`, `apps/orders/services.py`, `tests/**` 안에서만 다뤄줘.
- 관련 테스트를 추가하고, 실제 실행한 검증만 결과로 보고해줘. 실행하지 않은 lint/typecheck/compile/format 검증은 실행했다고 말하지 마.
- 검증 명령 이름도 정확히 적어줘. 예를 들어 `python3 -m unittest`로 실행했다면 pytest라고 쓰지 마.
- 실행 산출물로 남기지 않은 특정 테스트 선택자, `discover` 명령, 환경변수 접두사, 구현 전 실패 확인은 최종 검증 결과에 쓰지 마. 전체 unittest를 실행했다면 `python3 -m unittest`만 적어줘.
