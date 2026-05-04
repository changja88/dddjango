맥락이 불명확합니다. 우선 “Django Ninja 기반 REST API를 새로 정리한다”는 가정으로 잡겠습니다. 대상 도메인이 상품/주문/회원 중 무엇인지 알려주면 엔드포인트까지 구체화하겠습니다.

**주요 내용**

현재 작업공간은 읽기 전용이고, `/private/tmp/dddjango-codex-eval`에서 프로젝트 파일과 `config.toml`을 확인하지 못했습니다. 그래서 실제 수정 대신 적용할 구조를 제안합니다.

**Django라면**

```text
config/
  api.py          # NinjaAPI 생성, 앱 router 합성
  urls.py         # path("api/", api.urls)

<bounded_context>/
  api.py          # Router, HTTP endpoint
  schemas.py      # 요청/응답 Schema
  services.py     # 유스케이스/트랜잭션 로직
  selectors.py    # 조회 전용 QuerySet 조합
  models.py
  tests/
    test_api.py
```

핵심 원칙은 이렇게 가져가면 됩니다.

- URL은 리소스 명사 중심: `/api/v1/products`, `/api/v1/orders/{order_id}/items`
- 동사는 URL에 넣지 않음: `/create-order` 대신 `POST /orders`
- 앱별 `Router()`를 만들고 `config/api.py`에서 `api.add_router("/products", products_router)`로 합성
- API 함수는 얇게 유지: 인증, 입력 Schema, 응답 Schema, 상태 코드만 담당
- 비즈니스 규칙은 `services.py`, 조회 조합은 `selectors.py`로 분리
- 요청/응답은 Django Ninja `Schema`/`ModelSchema` 사용, DRF Serializer/ViewSet은 사용하지 않음
- 목록 API는 처음부터 페이지네이션 포함
- 에러는 RFC 9457 Problem Details 형태로 통일
- 버전은 `/api/v1/...`부터 시작하고, 필드 제거/이름 변경 같은 호환성 깨는 변경은 `/v2`로 분리

예시 라우팅 기준:

```text
GET    /api/v1/products
POST   /api/v1/products
GET    /api/v1/products/{product_id}
PATCH  /api/v1/products/{product_id}
DELETE /api/v1/products/{product_id}
```

검증은 실제 파일 수정 후 `python manage.py check`와 `pytest` 또는 `python manage.py test`로 확인하는 흐름이 맞습니다. 이번 세션에서는 읽기 전용이라 실행 결과를 만들지는 못했습니다.

---
> **관련 스킬 참조:**
> - REST API 설계 → **architecture-api** 스킬
> - Django Ninja 구현 → **implementation-django-ninja** 스킬