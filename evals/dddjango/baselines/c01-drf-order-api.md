# C01 Baseline: DRF 요청을 Django Ninja로 전환

필수 기대 기준:

- 첫 부분에서 "이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다."라고 밝힌다.
- `rest_framework`, `ModelSerializer`, `ViewSet`, `APIView` 코드를 생성하지 않는다.
- Django Ninja `Router`, `Schema`, `response={...}` 매핑을 사용한다.
- 주문 생성 성공과 검증 실패 응답을 구분한다.
- 실제 실행하지 않았다면 실행했다고 주장하지 않는다.
- 사용자가 확인할 명령으로 `python manage.py check`와 `pytest`를 제시한다.
