# C02 Baseline: Django Ninja 주문 생성 API 설계

필수 기대 기준:

- Django Ninja `Router`, `Schema`, status-code `response={...}` 매핑을 사용한다.
- router는 얇게 유지하고 주문 생성 규칙은 유스케이스/도메인 서비스로 분리한다.
- 주문 애그리거트, 값 객체, 도메인 예외, 결과 타입을 명시한다.
- DB 제약, 트랜잭션 경계, idempotency key 또는 중복 요청 방지 전략을 설명한다.
- DRF 패턴을 생성하지 않는다.
- 파일 단위 산출물과 검증 명령을 제시한다.
