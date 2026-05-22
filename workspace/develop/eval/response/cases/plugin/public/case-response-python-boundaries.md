Python 3.11 서비스 모듈을 손보기 전에 구현 기준을 정리해줘. 파일 수정은 하지 말고, 어떤 타입/검증/동시성 선택을 할지 판단 순서와 예시 수준으로 답해줘.

상황:
- 외부 결제 provider JSON payload를 받아 내부 주문 처리 코드로 넘긴다.
- provider payload는 `payment_id`, `order_id`, `amount`, `currency`, `status` 정도의 가벼운 shape만 필요하고, 내부 도메인 객체로 바로 쓰지는 않는다.
- `find_payment()`는 결제가 없을 수 있지만, 결제 실패는 정상 결과가 아니라 오류로 다루고 싶다.
- raw payload나 조회 결과를 다룰 때 `is_valid_provider_payload()` 같은 custom predicate를 둘지, `isinstance`/`None` check만으로 충분한지도 판단해줘.
- 주문 상태는 문자열로 직렬화되지만 상태 전이 규칙이 붙는다.
- 금액은 값 객체로 다루고, 통화가 다르면 더하지 못해야 한다.
- storage, clock, HTTP client는 테스트에서 갈아끼울 수 있지만, 모든 class마다 protocol을 만들고 싶지는 않다.
- provider 세션은 열고 닫는 cleanup이 필요하다.
- pydantic v2를 쓸 수 있지만 domain model 전체를 pydantic으로 바꾸고 싶지는 않다.
- 여러 provider 호출은 async로 병렬 처리할 수도 있지만 Django ORM과 외부 SDK가 async-safe인지 아직 확실하지 않다.
- Ruff, mypy, pyright 기준과 Python target을 확인해야 한다.

DDD, DB, REST API 설계로 확장하지 말고 Python 구현 선택에 집중해줘.
