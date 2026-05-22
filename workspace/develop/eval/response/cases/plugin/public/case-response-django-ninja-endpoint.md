Django Ninja로 주문 목록과 주문 생성 endpoint를 설계해야 해.

이미 REST 리소스와 상태 코드는 정해져 있고, 주문 생성 usecase와 주문 조회 selector도 있다고 가정해줘. 실제 코드는 작성하지 말고 Router/Schema adapter 설계, 인증/인가 연결, filtering/sorting/pagination, Problem Details 오류 매핑, OpenAPI 영향, TestClient 검증 계획을 정리해줘.

`ModelSchema`를 써도 되는지, DRF Serializer/ViewSet에서 옮겨올 때 어떤 호환성 차이를 확인해야 하는지도 함께 판단해줘.
