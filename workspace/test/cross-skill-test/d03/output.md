# D03: Django API 코드의 설계 원칙 리뷰 (architecture-api 스킬)

**Skill:** architecture-api (리뷰 mode)
**Code under review:**
```python
from rest_framework import serializers, viewsets, permissions
class OrderSerializer(serializers.ModelSerializer):
    class Meta: model=Order; fields='__all__'
class OrderViewSet(viewsets.ModelViewSet):
    queryset=Order.objects.all()
    serializer_class=OrderSerializer
    permission_classes=[permissions.IsAuthenticated]
```

## [주요 내용]

### API 설계 원칙 리뷰 결과

[원칙: 리소스 노출 범위] -- `fields='__all__'`은 API가 내부 데이터 구조를 그대로 노출한다. API 응답은 클라이언트가 필요로 하는 필드만 명시적으로 선택해야 한다. 내부 DB 스키마 변경이 API 호환성을 깨뜨리는 원인이 된다.

[원칙: 페이지네이션 누락] -- `ModelViewSet`의 기본 `list` 액션에 페이지네이션이 설정되지 않았다. 컬렉션 리소스는 반드시 페이지네이션을 적용해야 한다. 1M+ 레코드에서 Cursor 페이지네이션이 Offset보다 17배 빠르다.

[원칙: 버저닝 전략 없음] -- API 버전 관리가 없다. URL 경로(/v1/), 헤더, 또는 쿼리 파라미터 기반 버저닝 전략이 필요하다. 추가적 변경은 비호환이 아니지만, 필드 제거/타입 변경은 새 버전을 요구한다.

[원칙: 에러 형식 미정의] -- 에러 응답 형식이 정의되지 않았다. 모든 API 에러는 RFC 9457 Problem Details 형식(type/title/status/detail/instance)을 일관되게 사용해야 한다.

[원칙: 멱등성 처리 없음] -- POST로 주문을 생성하는 경우 Idempotency-Key 헤더를 지원하여 네트워크 재시도 시 중복 생성을 방지해야 한다.

[원칙: 상태 코드 일관성] -- ViewSet의 기본 응답 코드가 명시적이지 않다. POST=201(Created+Location), DELETE=204(No Content)를 정확히 매핑해야 한다.

### 권장 API 설계

```
GET    /api/v1/orders         → 200, 페이지네이션 필수
POST   /api/v1/orders         → 201 + Location 헤더
GET    /api/v1/orders/{id}    → 200
PATCH  /api/v1/orders/{id}    → 200
DELETE /api/v1/orders/{id}    → 204
```

---
> **관련 스킬 참조:**
> - [Django Ninja로 구현] → **implementation-django-ninja** 스킬
> - [Django 모델, QuerySet 최적화] → **implementation-django** 스킬
> - [도메인 모델 설계] → **architecture-ddd** 스킬
