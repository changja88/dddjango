# Django Ninja Code Review: Articles API

전반적으로 잘 구성된 코드다. Router 분리, `select_related` 사용, `ModelSchema`의 명시적 필드 선택, `@paginate` 적용, `HttpBearer` 인증, 204 빈 응답 패턴 등 Django Ninja의 핵심 관행을 대부분 따르고 있다. 아래는 더 개선할 수 있는 부분이다.

---

## Review Findings

### 1. PATCH 엔드포인트에서 `PatchDict` 미사용

```
[Schema and Validation] -- PATCH 작업에 별도 Schema를 정의하고 payload.dict(exclude_unset=True)를 수동으로 호출하는 대신, Django Ninja가 제공하는 PatchDict를 사용하면 의도가 더 명확해지고 코드가 간결해진다.
```

현재 코드:
```python
class ArticlePatch(Schema):
    title: str | None = None
    body: str | None = None

@router.patch('/{article_id}', response=ArticleOut)
def update_article(request, article_id: int, payload: ArticlePatch):
    article = get_object_or_404(Article, id=article_id, author=request.auth)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(article, attr, value)
    article.save(update_fields=list(payload.dict(exclude_unset=True).keys()) + ['updated_at'])
    return article
```

권장 코드:
```python
from ninja import PatchDict

@router.patch('/{article_id}', response=ArticleOut)
def update_article(request, article_id: int, payload: PatchDict[ArticleIn]):
    article = get_object_or_404(Article, id=article_id, author=request.auth)
    for attr, value in payload.items():
        setattr(article, attr, value)
    article.save(update_fields=list(payload.keys()) + ['updated_at'])
    return article
```

`PatchDict`는 기존 `ArticleIn`을 재활용하면서 모든 필드를 Optional로 만들고, 실제 제공된 필드만 포함하는 dict를 반환한다. `ArticlePatch` 클래스가 불필요해진다.

---

### 2. `payload.dict(exclude_unset=True)` 이중 호출

```
[Schema and Validation] -- update_article에서 payload.dict(exclude_unset=True)가 두 번 호출된다. 한 번 호출하여 변수에 저장한 뒤 재사용해야 한다.
```

현재 코드:
```python
for attr, value in payload.dict(exclude_unset=True).items():
    setattr(article, attr, value)
article.save(update_fields=list(payload.dict(exclude_unset=True).keys()) + ['updated_at'])
```

`PatchDict`를 도입하지 않더라도 최소한 다음과 같이 변수로 추출해야 한다:

```python
updated = payload.dict(exclude_unset=True)
for attr, value in updated.items():
    setattr(article, attr, value)
article.save(update_fields=list(updated.keys()) + ['updated_at'])
```

---

### 3. 엔드포인트 함수에 반환 타입 힌트 누락

```
[Baseline Requirements] -- 모든 엔드포인트 파라미터와 반환 타입에 타입 힌트가 필수다. 현재 모든 함수의 request 파라미터에 HttpRequest 타입 힌트가 없고, 반환 타입도 명시되어 있지 않다.
```

권장:
```python
from django.http import HttpRequest

@router.get('/{article_id}', response=ArticleOut)
def get_article(request: HttpRequest, article_id: int) -> ArticleOut:
    return get_object_or_404(Article, id=article_id)

@router.post('/', response={201: ArticleOut})
def create_article(request: HttpRequest, payload: ArticleIn) -> tuple[int, Article]:
    article = Article.objects.create(author=request.auth, **payload.dict())
    return 201, article
```

---

### 4. 에러 처리 부재 -- RFC 9457 Problem Details 미적용

```
[Error Handling] -- 커스텀 에러 처리가 전혀 없다. get_object_or_404는 Django의 Http404를 발생시키지만, 이것이 RFC 9457 Problem Details 형식으로 변환되지 않는다. API 소비자에게 일관된 에러 포맷을 제공하려면 exception_handler를 등록해야 한다.
```

이 코드가 등록되는 NinjaAPI 인스턴스 레벨에서 다음과 같은 글로벌 에러 핸들러가 필요하다:

```python
from ninja.errors import HttpError
from django.http import JsonResponse, Http404

@api.exception_handler(Http404)
def handle_404(request, exc):
    return JsonResponse(
        {
            "type": "about:blank",
            "title": "Not Found",
            "status": 404,
            "detail": str(exc),
            "instance": request.path,
        },
        status=404,
        content_type="application/problem+json",
    )
```

---

### 5. `get_article`에서 `select_related` 누락

```
[Routing] -- list_articles에서는 select_related('author')를 사용하지만, get_article에서는 사용하지 않는다. ArticleOut에 author_id가 포함되어 있으므로 현재는 추가 쿼리가 발생하지 않지만, 향후 author 정보가 중첩 스키마로 확장될 경우를 대비하여 일관성 있게 적용하는 것이 좋다.
```

---

### 6. `create_article`에서 `payload.dict()` 대신 `payload.model_dump()` 사용 권장

```
[Schema and Validation] -- Pydantic V2에서 .dict()는 deprecated이다. .model_dump()를 사용해야 한다. Django Ninja의 Schema는 Pydantic BaseModel을 상속하므로 동일하게 적용된다.
```

```python
# Before
article = Article.objects.create(author=request.auth, **payload.dict())

# After
article = Article.objects.create(author=request.auth, **payload.model_dump())
```

---

### 7. 쓰로틀링 미적용

```
[Error Handling and Throttling] -- 인증이 적용된 API이지만 쓰로틀링이 없다. 악의적 요청이나 과도한 사용을 방지하려면 Router 또는 NinjaAPI 레벨에서 쓰로틀을 설정해야 한다.
```

```python
from ninja.throttling import AuthRateThrottle

router = Router(tags=['articles'], auth=AuthBearer(), throttle=[AuthRateThrottle('100/m')])
```

---

### 8. `AuthBearer.authenticate`의 변수명이 혼동을 유발

```
[Authentication] -- authenticate 메서드에서 Token.objects.filter(...).first()의 결과를 user 변수에 저장하지만, 이 값은 Token 인스턴스이지 User가 아니다. 실제 User는 user.user로 접근한다. 변수명을 token_obj 등으로 변경해야 가독성이 좋아진다.
```

```python
class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        token_obj = Token.objects.filter(key=token).select_related('user').first()
        if token_obj:
            return token_obj.user
        return None
```

---

## Review Checklist

| 항목 | 결과 |
|------|------|
| DRF 패턴 사용 여부 | OK -- DRF 패턴 없음 |
| 엔드포인트 파라미터/반환 타입 힌트 | **개선 필요** -- request 및 반환 타입 힌트 누락 |
| Schema 필드 노출 범위 | OK -- 명시적 필드 선택 사용 |
| 인증 적용 여부 | OK -- Router 레벨 인증 적용 |
| 리스트 엔드포인트 페이지네이션 | OK -- @paginate 적용 |
| 에러 처리 | **개선 필요** -- RFC 9457 형식 핸들러 없음 |
| async 전환 가능성 | 해당 없음 -- 현재 규모에서는 sync로 충분 |
| FilterSchema 사용 | 해당 없음 -- 현재 필터링 로직 없음 |
| 입력 유효성 검증 | OK -- Schema로 요청 바디 검증 |
| 엔드포인트 책임 분리 | OK -- 각 엔드포인트가 단일 책임 수행 |
