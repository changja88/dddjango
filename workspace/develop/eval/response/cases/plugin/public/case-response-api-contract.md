고객용 주문 API 계약을 REST 관점에서 설계해줘.

상황:
- 고객은 자기 주문 목록을 조회하고, 주문을 생성하고, 주문 상세를 확인한다.
- 주문 목록은 주문 상태, 생성일 범위, 정렬, 필요한 필드만 선택하는 조회가 필요하다.
- 목록 데이터는 계속 늘어나고 주문 상태도 자주 바뀐다.
- API 클라이언트는 JSON을 기본으로 쓰지만, 목록 조회는 CSV 다운로드도 협상할 수 있어야 한다.
- 주문 생성은 네트워크 재시도 때문에 같은 요청이 두 번 들어와도 중복 주문이 생기면 안 된다.
- 인증된 고객은 자기 주문만 볼 수 있고, 운영자는 고객 주문을 조회할 수 있다.
- 하위 호환성을 지키면서 새 응답 필드를 추가하고, 향후 큰 변경은 버전 전략이 필요하다.
- 과도한 호출은 제한하고 클라이언트가 재시도 시점을 알 수 있어야 한다.

Django 코드나 DB schema는 작성하지 말고, endpoint별 `resource/URL`, HTTP method/status, request/response/header, Problem Details, auth/authz, content negotiation, pagination, versioning/deprecation, rate limit, `Idempotency-Key`, OpenAPI 영향을 정리해줘.
