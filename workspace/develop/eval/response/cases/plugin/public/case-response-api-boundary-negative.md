실시간 배송 추적 기능을 설계하려고 해.

요구:
- 모바일 앱은 배송 위치를 실시간으로 받아야 해서 WebSocket 또는 GraphQL subscription을 고려하고 있다.
- 외부 파트너는 API Gateway 뒤에서 GraphQL query로 배송 상태를 조회하고 싶어 한다.
- 일부 내부 시스템은 gRPC나 SOAP 연동 가능성도 묻고 있다.
- 팀 내부에서는 REST endpoint도 같이 만들어야 하는지 논쟁 중이다.
- HATEOAS 링크 구조나 API Gateway 라우팅 정책까지 자세히 설계해 달라는 요구도 나왔다.

dddjango 관점에서 이 요청을 어떤 skill 범위로 다룰지 판단해줘. REST 계약으로 다룰 수 있는 경계가 있다면 짧게 정리하되, REST 범위 밖인 부분을 억지로 endpoint 설계로 바꾸지 말아줘. 실제 코드 작성은 하지 마.
