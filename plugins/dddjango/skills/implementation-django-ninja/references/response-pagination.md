# 응답과 페이지네이션 레퍼런스

> Django Ninja 공식 문서 기반 레퍼런스. 다중 응답 스키마, 빈 응답, 내장 페이지네이터, 커스텀 페이지네이션, RouterPaginated를 다룬다.

---

## 1. 상태 코드별 다중 응답 스키마

### 기본 사용

딕셔너리로 상태 코드와 스키마를 매핑하여 다양한 응답 형태를 정의한다:

```python
from ninja import Schema

class Token(Schema):
    token: str
    expires: date

class Message(Schema):
    message: str

@api.post('/login', response={200: Token, 401: Message, 402: Message})
def login(request, payload: Auth):
    if auth_not_valid:
        return 401, {'message': 'Unauthorized'}
    if negative_balance:
        return 402, {'message': 'Insufficient balance amount...'}
    return 200, {'token': xxx, ...}
```

**tuple 반환 패턴**: `return 상태코드, 데이터` 형식으로 반환한다. 이것이 Django Ninja 공식 문서의 기본 패턴이다.

### 코드 범위 (Code Ranges)

사전 정의된 HTTP 코드 범위를 사용하여 중복을 줄인다:

```python
from ninja.responses import codes_4xx

@api.post('/login', response={200: Token, codes_4xx: Message})
def login(request, payload: Auth):
    ...
```

사용 가능한 범위:
- `codes_1xx` -- 정보 응답
- `codes_2xx` -- 성공
- `codes_3xx` -- 리다이렉션
- `codes_4xx` -- 클라이언트 에러
- `codes_5xx` -- 서버 에러

### 커스텀 코드 범위

`frozenset`으로 직접 코드 범위를 정의할 수 있다:

```python
my_codes = frozenset({416, 418, 425, 429, 451})

@api.post('/login', response={200: Token, my_codes: Message})
def login(request, payload: Auth):
    ...
```

---

## 2. 빈 응답 (204 No Content)

응답 본문이 없는 경우 `None`을 지정한다:

```python
@api.post("/no_content", response={204: None})
def no_content(request):
    return 204, None
```

HTTP 명세에 따라 "응답 본문이 비어있음"을 나타낸다.

---

## 3. Django HTTP 응답 직접 반환

Django의 표준 HTTP 응답을 직접 반환할 수 있다:

```python
from django.http import HttpResponse
from django.shortcuts import redirect

@api.get("/http")
def result_django(request):
    return HttpResponse('some data')

@api.get("/something")
def some_redirect(request):
    return redirect("/some-path")
```

---

## 4. 내장 페이지네이터

Django Ninja는 3가지 내장 페이지네이션 클래스를 제공한다.

### LimitOffsetPagination (기본값)

두 파라미터를 사용한다:
- `limit`: 페이지당 항목 수 (기본값: 100, `NINJA_PAGINATION_PER_PAGE`로 설정 가능)
- `offset`: 페이지 창 오프셋 (0부터 시작)

```python
from ninja.pagination import paginate, LimitOffsetPagination

@api.get('/users', response=List[UserSchema])
@paginate(LimitOffsetPagination)
def list_users(request):
    return User.objects.all()
```

요청 예시: `/api/users?limit=10&offset=0`

### PageNumberPagination

1부터 시작하는 페이지 번호를 사용한다:

```python
from ninja.pagination import paginate, PageNumberPagination

@api.get('/users', response=List[UserSchema])
@paginate(PageNumberPagination)
def list_users(request):
    return User.objects.all()
```

요청 예시: `/api/users?page=2`

커스텀 페이지 크기 설정:

```python
@api.get("/users")
@paginate(PageNumberPagination, page_size=50)
def list_users(request):
    ...
```

동적 `page_size` 파라미터도 지원한다: `/api/users?page=2&page_size=20`

### CursorPagination

자주 변경되는 데이터셋에 안정적인 페이지네이션을 제공한다. Base64 인코딩된 토큰을 사용한다:

```python
from ninja.pagination import paginate, CursorPagination

@api.get('/events', response=List[EventSchema])
@paginate(CursorPagination)
def list_events(request):
    return Event.objects.all()
```

요청 예시: `/api/events?cursor=eyJwIjoiMjAyNC0wMS0wMSIsInIiOmZhbHNlLCJvIjowfQ==`

설정 가능한 항목:
- `ordering`: 정렬 필드 튜플 (기본값: `("-pk",)`, `NINJA_PAGINATION_DEFAULT_ORDERING`으로 변경 가능)
- `page_size`: 기본 페이지 크기 (기본값: 100)
- `max_page_size`: 최대 허용 크기 (기본값: 100)
- `NINJA_PAGINATION_MAX_OFFSET`: 악의적 요청 제한 (기본값: 100)

뷰별 커스텀 설정:

```python
@api.get("/events")
@paginate(CursorPagination, ordering=("start_date", "end_date"),
          page_size=20, max_page_size=100)
def list_events(request):
    return Event.objects.all()
```

CursorPagination 응답 형식:

```json
{
  "next": "http://api.example.com/events?cursor=...",
  "previous": "http://api.example.com/events?cursor=...",
  "results": [
    {"id": 1, "title": "Event 1", "start_date": "2024-01-01"},
    {"id": 2, "title": "Event 2", "start_date": "2024-01-02"}
  ]
}
```

---

## 5. @paginate 데코레이터

`@paginate` 데코레이터의 핵심 사용법:

```python
from ninja.pagination import paginate

# 기본 페이지네이션 (LimitOffsetPagination)
@api.get('/users', response=List[UserSchema])
@paginate
def list_users(request):
    return User.objects.all()

# 특정 페이지네이터 지정
@api.get('/users', response=List[UserSchema])
@paginate(PageNumberPagination)
def list_users(request):
    return User.objects.all()

# 추가 옵션 지정
@api.get('/users', response=List[UserSchema])
@paginate(PageNumberPagination, page_size=50)
def list_users(request):
    return User.objects.all()
```

뷰 함수는 전체 QuerySet 또는 리스트를 반환하면 되며, 실제 슬라이싱은 페이지네이터가 처리한다.

---

## 6. 커스텀 페이지네이션 (PaginationBase)

`PaginationBase`를 상속하고 `Input`, `Output` 스키마와 `paginate_queryset` 메서드를 오버라이드한다:

```python
from typing import Any, List
from ninja import Schema
from ninja.pagination import paginate, PaginationBase

class CustomPagination(PaginationBase):
    class Input(Schema):
        skip: int

    class Output(Schema):
        items: List[Any]
        meta: dict[str, int]

    def paginate_queryset(self, queryset, pagination: Input, **params):
        skip = pagination.skip
        per_page = 5
        items = queryset[skip: skip + per_page]
        return {
            'items': items,
            'meta': {
                'total': queryset.count(),
                'limit': per_page,
                'offset': skip,
            },
        }

@api.get('/users', response=List[UserSchema])
@paginate(CustomPagination)
def list_users(request):
    return User.objects.all()
```

### request 객체 접근

`params`에서 request 객체를 가져올 수 있다:

```python
def paginate_queryset(self, queryset, pagination: Input, **params):
    request = params["request"]
    # request 활용 로직
    ...
```

### 커스텀 items 속성 이름

기본값인 `'items'` 대신 다른 속성 이름을 사용할 수 있다:

```python
class CustomPagination(PaginationBase):
    class Output(Schema):
        results: List[Any]  # 'items' 대신 'results' 사용
        total: int
        per_page: int

    items_attribute: str = "results"  # 속성 이름 오버라이드
```

### 비동기 페이지네이션

비동기 지원이 필요한 경우 `AsyncPaginationBase`를 상속하고 `apaginate_queryset`을 오버라이드한다.

---

## 7. RouterPaginated

`List[Schema]`를 반환하는 모든 작업에 자동으로 페이지네이션을 적용하는 라우터다:

```python
from ninja.pagination import RouterPaginated

router = RouterPaginated()

@router.get("/items", response=List[MySchema])
def items(request):
    return MyModel.objects.all()

@router.get("/other-items", response=List[OtherSchema])
def other_items(request):
    return OtherModel.objects.all()
```

`List[Schema]` 응답을 가진 모든 엔드포인트에 수동으로 `@paginate`를 붙일 필요 없이 일괄 적용된다.

### 전역 적용

`NinjaAPI`의 기본 라우터를 `RouterPaginated`로 교체한다:

```python
api = NinjaAPI(default_router=RouterPaginated())
```

---

## 8. pass_parameter

페이지네이션 정보를 뷰 함수 내에서 접근할 수 있게 한다:

```python
@api.get("/someview")
@paginate(pass_parameter="pagination_info")
def someview(request, **kwargs):
    page = kwargs["pagination_info"].page
    # 페이지네이션 정보를 활용한 로직
    return ...
```

`pass_parameter`에 지정한 이름으로 `kwargs`에서 페이지네이션 Input 객체를 가져올 수 있다.
