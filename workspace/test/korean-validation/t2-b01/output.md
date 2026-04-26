# Review: OrderListView

## 대상 코드

```python
from django.http import JsonResponse
from django.views import View

class OrderListView(View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).values('id', 'status', 'total')
        return JsonResponse({'orders': list(orders)})
```

## 잘된 점

- `values('id', 'status', 'total')`를 사용하여 필요한 필드만 조회하고 있다. 불필요한 컬럼 로딩을 피하는 좋은 습관이다.
- `list()`로 QuerySet을 변환하여 `JsonResponse`에 직렬화 가능한 형태로 전달하고 있다.
- CBV 기반의 `View`를 사용하여 HTTP 메서드별 분리가 되어 있다.

## 발견 사항

### 1. 인증 보호 누락

```
[보안 -- 인증] -- 인증되지 않은 사용자가 이 뷰에 접근하면 request.user가
AnonymousUser가 되어 예상치 못한 결과를 반환하거나 에러가 발생할 수 있다.
LoginRequiredMixin을 추가하여 인증된 사용자만 접근할 수 있도록 해야 한다.
```

```python
# 권장
from django.contrib.auth.mixins import LoginRequiredMixin

class OrderListView(LoginRequiredMixin, View):
    ...
```

### 2. API 엔드포인트에 Django Ninja 사용 권장

```
[API 레이어] -- JsonResponse로 직접 JSON API를 구현하고 있다. Django에서
API 엔드포인트를 구현할 때는 Django Ninja를 사용하는 것이 권장된다.
Django Ninja는 Schema 기반 직렬화, 자동 문서화(OpenAPI), 타입 힌트 기반
검증, 인증/페이지네이션 등을 제공하여 수동 JsonResponse 구성보다 안전하고
유지보수하기 쉽다.
```

### 3. 쿼리 로직을 뷰에서 분리 필요 -- Fat Model / 커스텀 QuerySet

```
[QuerySet 패턴 / Fat Model, Thin View] -- 뷰 내부에 bare queryset
(Order.objects.filter(...).values(...))이 직접 작성되어 있다.
이 필터링 로직을 커스텀 QuerySet 메서드나 셀렉터로 추출하면
재사용성이 높아지고 테스트가 용이해진다.
```

```python
# 권장: 커스텀 QuerySet 메서드로 추출
class OrderQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)

class Order(models.Model):
    objects = OrderQuerySet.as_manager()
```

또는 읽기 전용 쿼리 로직이 복잡해질 경우 셀렉터 패턴을 적용한다:

```python
# selectors.py
def order_list(*, user):
    return Order.objects.filter(user=user).values("id", "status", "total")
```

### 4. 페이지네이션 부재

```
[성능] -- 필터 결과를 list()로 전부 메모리에 올리고 있다. 주문 수가
많아지면 응답 시간과 메모리 사용량이 급격히 증가한다. 페이지네이션을
적용하여 한 번에 반환하는 데이터 양을 제한해야 한다.
```

## Review 체크리스트 확인 결과

- [x] 프로젝트 구조: 해당 없음 (단일 뷰 코드)
- [x] 모델 필드 순서: 해당 없음 (모델 정의 없음)
- [x] 불리언 플래그 남발: 해당 없음
- [x] select_related/prefetch_related 누락: `values()`를 사용하므로 FK JOIN 불필요. 현재 조회 필드(`id`, `status`, `total`)는 모두 `Order` 테이블의 직접 필드이므로 문제 없음
- [x] N+1 쿼리: `values()`로 단일 쿼리 실행. 현재 N+1 문제 없음
- [x] update_fields 없는 save(): 해당 없음 (읽기 전용 뷰)
- [x] 같은 앱 시그널: 해당 없음
- [x] ModelForm fields = "__all__": 해당 없음
- [ ] **DRF Serializer/ViewSet 사용 아님, 그러나 JsonResponse 직접 사용** -- Django Ninja로 전환 권장
- [x] 다중 테이블 상속: 해당 없음
- [x] 문자열 보간 raw SQL: 해당 없음 (ORM 사용)
- [x] CSRF 보호: GET 요청이므로 CSRF 해당 없음
- [x] 4개 이상 Mixin: 해당 없음
- [ ] **Fat 뷰**: bare queryset이 뷰에 직접 작성됨 -- 커스텀 QuerySet 또는 셀렉터로 추출 권장
- [x] assertNumQueries: 해당 없음 (테스트 코드 아님)
- [x] Django 5.x 기능 미사용: 이 뷰 패턴에서는 해당 없음

## 교차 참조 안내

- API 엔드포인트 구현(Django Ninja Schema, Router, 인증, 페이지네이션)에 대한 자세한 안내는 **implementation-django-ninja** 스킬을 참조하세요.
- Python 타입 힌트와 관용구에 대한 자세한 안내는 **implementation-python** 스킬을 참조하세요.
- REST API 설계 원칙(엔드포인트 네이밍, 상태 코드, 페이지네이션 전략)에 대한 자세한 안내는 **architecture-api** 스킬을 참조하세요.
