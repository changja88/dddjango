# M01 Baseline: Django Ninja error standard

필수 기대 기준:

- `Problem Details`와 `application/problem+json`을 표준으로 사용한다.
- 성공 목록 응답에는 `items`와 `meta` envelope를 사용한다.
- `ProblemDetail(Schema)`, error code enum, exception handler, status-code별 `response={...}` 매핑을 포함한다.
- `{"error": ...}`를 표준으로 제시하지 않는다.
- DRF 코드를 생성하지 않는다.
