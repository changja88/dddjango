# Code Review: Django REST Framework PostViewSet

## 1. Model 미임포트

`Post` 모델이 임포트되지 않았다. 코드 실행 시 `NameError`가 발생한다.

```python
from .models import Post  # 추가 필요
```

## 2. Pagination 설정 부재

`PageNumberPagination`을 직접 사용하고 있지만, `page_size`가 설정되어 있지 않다. DRF 기본 `PageNumberPagination`은 `page_size`가 `None`이므로, `settings.py`의 `DEFAULT_PAGINATION_CLASS`에서 전역 설정하지 않았다면 페이지네이션이 동작하지 않거나 예외가 발생한다.

```python
class PostPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostViewSet(viewsets.ModelViewSet):
    pagination_class = PostPagination
```

## 3. 권한 정책 미흡

`IsAuthenticated`만 사용하면 인증된 사용자 누구나 다른 사용자의 글을 수정/삭제할 수 있다. 객체 수준 권한 제어가 필요하다.

```python
from rest_framework.permissions import BasePermission

class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
```

## 4. Serializer의 `fields = '__all__'` 사용

`__all__`은 모델 필드 전체를 노출한다. 의도치 않은 필드(예: `author`, `created_at` 등 쓰기 불가 필드)가 API 입력으로 허용될 수 있고, 모델 변경 시 민감한 필드가 자동 노출되는 위험이 있다.

```python
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at']
        read_only_fields = ['author', 'created_at']
```

## 5. queryset 필터링 부재

`Post.objects.all()`은 모든 게시글을 반환한다. 요구사항에 따라 삭제된 글 제외, 본인 글만 조회 등의 필터링이 필요할 수 있다. `get_queryset()`을 오버라이드하면 동적 필터링이 가능하다.

```python
def get_queryset(self):
    return Post.objects.filter(is_deleted=False).select_related('author')
```

`select_related`를 통해 author 조회 시 N+1 쿼리 문제도 방지할 수 있다.

## 6. Throttling 미설정

인증된 사용자에 대한 요청 제한이 없다. 악의적 대량 요청에 노출될 수 있으므로, ViewSet 또는 전역 설정에서 throttle을 적용하는 것이 좋다.

## 요약

| 항목 | 심각도 | 유형 |
|------|--------|------|
| Model 미임포트 | 높음 | 버그 |
| Pagination page_size 미설정 | 중간 | 버그 |
| 객체 수준 권한 부재 | 높음 | 보안 |
| `fields = '__all__'` | 중간 | 보안 |
| queryset 필터링/최적화 부재 | 낮음 | 성능 |
| Throttling 미설정 | 낮음 | 보안 |
