# DRF Code Review: ProductSerializer & ProductViewSet

## 1. `fields = '__all__'` 사용 지양

```python
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
```

**문제:** `__all__`은 모델에 추가되는 모든 필드를 자동으로 API에 노출한다. 민감한 필드(예: 내부 플래그, 가격 원가 등)가 의도치 않게 노출될 수 있다.

**권장:** 필드를 명시적으로 나열한다.

```python
fields = ['id', 'name', 'price', 'description', 'created_at']
```

---

## 2. `create` 메서드의 이중 저장(Double Save) 문제

```python
def create(self, request, *args, **kwargs):
    serializer = ProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    product = serializer.save()        # 첫 번째 DB write
    product.created_by = request.user
    product.save()                     # 두 번째 DB write
    return Response(ProductSerializer(product).data, status=201)
```

**문제:** `serializer.save()`로 한 번 저장한 뒤, `created_by`를 설정하고 다시 `save()`를 호출한다. 불필요한 DB 쿼리가 발생하며, 첫 번째 저장 시점에 `created_by`가 NULL이므로 NOT NULL 제약이 있으면 에러가 발생한다.

**권장:** `save()`에 키워드 인자를 전달한다.

```python
product = serializer.save(created_by=request.user)
```

---

## 3. `create` 메서드에서 `self.get_serializer()` 미사용

```python
serializer = ProductSerializer(data=request.data)
```

**문제:** ViewSet에 이미 `serializer_class = ProductSerializer`가 설정되어 있다. 직접 클래스를 참조하면 `get_serializer_class()` 오버라이드가 무시되고, ViewSet이 제공하는 컨텍스트(`request`, `format`, `view`)가 serializer에 전달되지 않는다.

**권장:** `self.get_serializer()`를 사용한다.

```python
serializer = self.get_serializer(data=request.data)
```

---

## 4. `create`에서 `perform_create` 패턴 미활용

**문제:** DRF의 `ModelViewSet`은 `create` -> `perform_create` 흐름을 제공한다. `create` 전체를 오버라이드하면 DRF가 기본 제공하는 헤더 설정(`Location` 헤더), `get_success_headers()` 호출 등이 누락된다.

**권장:** `perform_create`만 오버라이드한다.

```python
def perform_create(self, serializer):
    serializer.save(created_by=self.request.user)
```

이렇게 하면 `create` 메서드의 나머지 로직(유효성 검사, 응답 생성, 헤더 설정)은 DRF 기본 구현이 처리한다.

---

## 5. `list` 메서드의 불필요한 오버라이드

```python
def list(self, request, *args, **kwargs):
    queryset = Product.objects.all()
    serializer = ProductSerializer(queryset, many=True)
    return Response(serializer.data)
```

**문제:**
- 이 구현은 `ModelViewSet`의 기본 `list` 동작과 동일하므로 오버라이드할 이유가 없다.
- `self.get_queryset()` 대신 `Product.objects.all()`을 직접 호출하여, ViewSet의 `queryset` 속성이나 `get_queryset()` 오버라이드가 무시된다.
- `self.filter_queryset()`을 거치지 않으므로 DjangoFilterBackend 등 필터가 적용되지 않는다.
- **페이지네이션이 누락**되어 레코드가 많아지면 응답이 느려지고 메모리 문제가 발생한다.

**권장:** `list` 오버라이드를 삭제한다. 기본 구현이 필터링, 페이지네이션을 모두 처리한다.

---

## 6. 응답 상태 코드 하드코딩

```python
return Response(ProductSerializer(product).data, status=201)
```

**문제:** 매직 넘버 사용은 가독성을 떨어뜨린다.

**권장:** DRF에서 제공하는 상수를 사용한다.

```python
from rest_framework import status
return Response(serializer.data, status=status.HTTP_201_CREATED)
```

---

## 7. 권한(Permission) 및 인증(Authentication) 미설정

**문제:** `ModelViewSet`은 기본적으로 CRUD 전체를 노출한다. `permission_classes`가 없으면 프로젝트 기본 설정에 의존하게 되며, 의도치 않게 비인증 사용자에게 수정/삭제 권한이 열릴 수 있다. 특히 `create`에서 `request.user`를 사용하고 있으므로 인증이 반드시 필요하다.

**권장:** 명시적으로 권한을 설정한다.

```python
from rest_framework.permissions import IsAuthenticated

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
```

---

## 개선된 전체 코드

```python
from rest_framework import serializers, viewsets, status
from rest_framework.permissions import IsAuthenticated


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
```
