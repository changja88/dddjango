# B02: Cross-Skill Boundary Test -- DRF Request to Django Skill

## Test Info

| Item | Value |
|------|-------|
| Skill | `implementation-django` |
| Prompt | "DRF ViewSet으로 주문 목록 API를 만들고 싶어. permission_classes 설정이랑 pagination 어떻게 해?" |
| Boundary Rule | DRF(Django REST Framework)는 사용하지 않는다. API 구현에는 Django Ninja를 사용한다. |

## Skill Response

이 프로젝트에서는 **DRF(Django REST Framework)를 사용하지 않습니다.** API 엔드포인트는 **Django Ninja**로 구현합니다.

요청하신 `ViewSet`, `permission_classes`, DRF의 `PageNumberPagination`은 모두 DRF 고유의 패턴입니다. 이 프로젝트의 컨벤션에 따라 Django Ninja 패턴으로 안내드립니다.

### DRF vs Django Ninja 대응 관계

| DRF 개념 | Django Ninja 대응 |
|----------|-------------------|
| `ViewSet` | `Router` + 개별 엔드포인트 함수 |
| `Serializer` | `Schema` (Pydantic 기반) |
| `permission_classes` | Django Ninja 인증 클래스 (`HttpBearer`, 커스텀 `AuthBase`) |
| `PageNumberPagination` | `paginate_queryset` 데코레이터 + `PageNumberPagination` |

### 주문 목록 API -- Django Ninja 방향 안내

DRF의 `ViewSet` + `permission_classes` + `pagination` 조합 대신, Django Ninja에서는 다음과 같은 구조를 사용합니다:

```python
# apps/orders/api.py
from ninja import Router, Schema
from ninja.pagination import paginate, PageNumberPagination
from ninja.security import HttpBearer

router = Router(tags=["orders"])


class AuthToken(HttpBearer):
    def authenticate(self, request, token: str):
        # 토큰 검증 로직
        ...


class OrderOut(Schema):
    id: int
    status: str
    total_amount: str
    created_at: datetime


@router.get(
    "/",
    response=list[OrderOut],
    auth=AuthToken(),
)
@paginate(PageNumberPagination)
def list_orders(request):
    return Order.objects.select_related("user").order_by("-created_at")
```

Django Ninja의 Schema, Router, 인증, 페이지네이션, 필터링, 에러 처리에 대한 상세한 패턴과 코드 예제는 **implementation-django-ninja** 스킬에서 다룹니다. 해당 스킬을 호출하여 완전한 구현 가이드를 받으세요.

---
> **관련 스킬 참조:**
> - [Django Ninja API 구현 (Schema, Router, 인증, 페이지네이션)] -> **implementation-django-ninja** 스킬
> - [REST API 설계 원칙 (엔드포인트, 상태 코드, 버저닝)] -> **architecture-api** 스킬
> - [주문 모델 설계 (Fat Model, TextChoices, QuerySet)] -> **implementation-django** 스킬

## Boundary Enforcement Analysis

| Criterion | Result |
|-----------|--------|
| DRF 코드 직접 생성 거부 | PASS -- ViewSet/Serializer/permission_classes 코드를 생성하지 않음 |
| Django Ninja 전환 권고 | PASS -- DRF 대신 Django Ninja 사용을 명확히 안내 |
| 상세 구현을 django-ninja 스킬로 위임 | PASS -- implementation-django-ninja 스킬 참조를 안내 |
| 응답 구조 준수 (주요 내용 + 관련 스킬 참조) | PASS -- 스킬 정의 템플릿 준수 |
| DRF-to-Ninja 대응 관계 제공 | PASS -- 사용자가 기존 DRF 지식을 매핑할 수 있도록 테이블 제공 |

## Verdict

**PASS** -- 스킬이 DRF 경계를 정확히 집행했다. DRF 코드를 생성하지 않고, Django Ninja로의 전환을 권고하며, 상세 API 구현은 implementation-django-ninja 스킬로 위임했다. 스킬 문서에 명시된 "DRF 코드(Serializer, ViewSet, APIView, permission_classes)를 발견하면 Django Ninja 패턴으로 전환을 권고한다" 규칙을 충실히 따랐다.
