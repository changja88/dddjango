# Django Ninja 코드 리뷰

전반적으로 Django Ninja의 관례를 잘 따르고 있으며, CRUD가 깔끔하게 정리되어 있다. 아래는 개선이 필요한 부분들이다.

---

## 1. 보안 및 인증

### 1-1. `AuthBearer.authenticate` 반환값 오류

```python
user = Token.objects.filter(key=token).select_related('user').first()
if user:
    return user.user
```

변수명이 `user`이지만 실제로는 `Token` 인스턴스다. 가독성을 위해 변수명을 수정해야 한다.

```python
def authenticate(self, request, token):
    token_obj = Token.objects.filter(key=token).select_related('user').first()
    if token_obj:
        return token_obj.user
    return None
```

### 1-2. 소유권 검증 누락 (update/delete)

`get_object_or_404(Article, id=article_id, author=request.auth)`로 소유권을 검증하고 있는데, 이 경우 **본인 소유가 아닌 글에 접근하면 404가 반환**된다. 보안 관점에서 이것이 의도적인 선택일 수 있지만, API 소비자 입장에서는 "존재하지 않음"과 "권한 없음"의 구분이 불가하다. 필요에 따라 403 응답을 분리하는 것이 좋다.

```python
from ninja.errors import HttpError

@router.patch('/{article_id}', response=ArticleOut)
def update_article(request, article_id: int, payload: ArticlePatch):
    article = get_object_or_404(Article, id=article_id)
    if article.author != request.auth:
        raise HttpError(403, "You do not have permission to edit this article.")
    ...
```

---

## 2. 버그 및 잠재적 문제

### 2-1. `payload.dict()` 이중 호출 (update_article)

```python
for attr, value in payload.dict(exclude_unset=True).items():
    setattr(article, attr, value)
article.save(update_fields=list(payload.dict(exclude_unset=True).keys()) + ['updated_at'])
```

`payload.dict(exclude_unset=True)`를 두 번 호출하고 있다. 변수로 추출해야 한다.

```python
updates = payload.dict(exclude_unset=True)
for attr, value in updates.items():
    setattr(article, attr, value)
article.save(update_fields=list(updates.keys()) + ['updated_at'])
```

### 2-2. `payload.dict()` deprecated 경고

Pydantic v2 기준으로 `.dict()`는 deprecated이며 `.model_dump()`를 사용해야 한다. Django Ninja가 내부적으로 Pydantic v2를 사용하는 경우 경고가 발생할 수 있다.

```python
# Pydantic v2 호환
updates = payload.model_dump(exclude_unset=True)
article = Article.objects.create(author=request.auth, **payload.model_dump())
```

### 2-3. PATCH에서 빈 payload 처리

모든 필드가 `None`이고 아무것도 전송하지 않으면 `updates`가 빈 dict가 된다. 이 경우 `save(update_fields=['updated_at'])`만 실행되어 불필요한 DB 쿼리가 발생한다.

```python
updates = payload.model_dump(exclude_unset=True)
if not updates:
    return article
```

---

## 3. 성능

### 3-1. `list_articles`에서 불필요한 `select_related`

```python
@router.get('/', response=list[ArticleOut])
def list_articles(request):
    return Article.objects.select_related('author').all()
```

`ArticleOut`에 `author_id`만 포함되어 있고 author 객체의 필드는 사용하지 않는다. `select_related('author')`는 JOIN을 발생시키므로, author 객체의 필드를 직렬화하지 않는 한 제거하는 것이 좋다.

```python
def list_articles(request):
    return Article.objects.all()
```

반대로, author 정보를 함께 내려주고 싶다면 `ArticleOut`에 author 관련 필드를 추가해야 한다.

### 3-2. `get_article`에서 `select_related` 누락

단건 조회에서도 author 정보가 필요한 경우가 있을 수 있는데, `list_articles`와 달리 `select_related`가 없어 일관성이 떨어진다. 응답 스키마에 맞춰 통일해야 한다.

---

## 4. API 설계

### 4-1. 에러 응답 스키마 미정의

성공 응답만 정의되어 있고, 에러 응답(400, 403, 404, 422)에 대한 스키마가 없다. API 문서(OpenAPI/Swagger) 완성도를 높이려면 에러 응답도 명시하는 것이 좋다.

```python
class ErrorOut(Schema):
    detail: str

@router.patch('/{article_id}', response={200: ArticleOut, 403: ErrorOut, 404: ErrorOut})
def update_article(request, article_id: int, payload: ArticlePatch):
    ...
```

### 4-2. `list_articles`에 필터/정렬 없음

현재 전체 게시글을 페이지네이션만으로 반환한다. 실무에서는 최소한 정렬 기준(`ordering`)이 있어야 페이지네이션이 안정적으로 동작한다. 정렬 없이 페이지네이션하면 중복/누락이 발생할 수 있다.

```python
@router.get('/', response=list[ArticleOut])
@paginate(PageNumberPagination, page_size=20)
def list_articles(request):
    return Article.objects.order_by('-created_at')
```

---

## 5. 코드 구조

### 5-1. 모델 import 누락

`Article`, `Token` 모델의 import 문이 없다. 실제 코드에는 있겠지만, 리뷰 대상 코드에서는 빠져 있어 확인이 필요하다.

### 5-2. Router를 API에 등록하는 코드 누락

`router = Router(...)`만 있고, `api.add_router('/articles', router)` 같은 등록 코드가 보이지 않는다. 별도 파일에서 처리하고 있다면 문제없지만 확인이 필요하다.

---

## 요약

| 구분 | 항목 | 심각도 |
|------|------|--------|
| 버그 | 변수명 혼동 (`user` vs `token_obj`) | 낮음 |
| 버그 | `payload.dict()` 이중 호출 | 중간 |
| 호환성 | `.dict()` -> `.model_dump()` (Pydantic v2) | 중간 |
| 성능 | 불필요한 `select_related` / 누락 불일치 | 낮음 |
| 안정성 | 정렬 없는 페이지네이션 | 높음 |
| 설계 | 404 vs 403 구분 불가 | 중간 |
| 설계 | 에러 응답 스키마 미정의 | 낮음 |
| 방어 | 빈 PATCH payload 미처리 | 낮음 |

코드의 기본 구조는 잘 잡혀 있다. 위 항목들을 반영하면 프로덕션 수준의 완성도를 갖출 수 있다.
