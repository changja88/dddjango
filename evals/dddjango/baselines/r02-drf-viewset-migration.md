# R02 Baseline: DRF ViewSet을 Django Ninja로 전환

필수 기대 기준:

- 기존 DRF 코드는 분석 대상으로만 언급하고 새 코드에는 생성하지 않는다.
- Django Ninja `Router`, `Schema`, `response={...}` 구조로 전환한다.
- URL, schema, auth, pagination, error response 호환성을 점검한다.
- 단계별 마이그레이션과 회귀 테스트 계획을 제시한다.
- `from rest_framework`, `ModelSerializer`, `ViewSet` 코드를 생성하지 않는다.
