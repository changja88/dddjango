# M03 Baseline: Django Ninja list API filter and pagination

필수 기대 기준:

- Django Ninja `Router`, `Schema`, `response={...}` 구조를 사용한다.
- 검색/상태/기간 필터는 `FilterSchema` 또는 명시적 입력 schema로 분리한다.
- 정렬 필드는 allow-list로 제한하고 임의 컬럼 정렬을 허용하지 않는다.
- 목록 응답은 `items`와 `meta` envelope로 반환한다.
- 인증/권한 경계를 언급하고, `TestClient` 또는 pytest 기반 테스트를 포함한다.
- DRF, ViewSet, APIView 코드를 생성하지 않는다.
