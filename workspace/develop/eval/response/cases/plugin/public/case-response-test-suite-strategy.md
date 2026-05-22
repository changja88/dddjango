Django Ninja 주문 API와 쿠폰 정책 테스트를 정리하려고 해. 파일 수정은 하지 말고, 테스트 설계와 검증 계획만 답해줘.

상황:
- 주문 생성 API의 REST 계약과 멱등성 정책은 이미 정해져 있다.
- 같은 `Idempotency-Key`와 같은 payload는 같은 결과를 재사용하고, 같은 key와 다른 payload는 conflict로 응답해야 한다.
- 쿠폰은 최소 주문 금액, 만료일, 이미 사용한 쿠폰 규칙이 있다.
- 외부 결제 확인은 HTTP client adapter 뒤에 있고, 만료 판단은 현재 시각에 의존한다.
- PostgreSQL lock이나 unique constraint처럼 SQLite로는 충분히 검증하기 어려운 부분이 있다.

요청:
- pytest 기준으로 테스트 레벨과 파일 배치, fixture/conftest 사용 기준을 정리해줘.
- 어떤 항목을 parametrization, assertion, test double, factory/Faker, property-based test로 검증할지 구분해줘.
- 시간과 HTTP 의존성, testcontainers 필요 여부, coverage/mutation 활용 방식, BDD가 적합한지, flaky concurrency test를 피하는 기준을 포함해줘.
- Django Ninja `TestClient`로 확인할 API 계약 테스트와 idempotency/concurrency 테스트 기준을 포함해줘.
- 실제로 실행하지 않은 명령이나 subagent 리뷰를 실행했다고 쓰지는 마.
