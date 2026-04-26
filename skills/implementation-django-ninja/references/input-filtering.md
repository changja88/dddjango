# 입력 처리와 필터링 레퍼런스

> Django Ninja 공식 문서 기반 레퍼런스. Path/Query/Body 자동 감지, Form/File 처리, FilterSchema, FilterLookup, 커스텀 필터를 다룬다.

---

## 1. Path / Query / Body 자동 감지

Django Ninja는 함수 파라미터의 위치와 타입으로 입력 소스를 자동 감지한다:

| 조건 | 파라미터 소스 |
|------|-------------|
| URL 경로에 `{param}` 존재 | Path 파라미터 |
| 단순 타입 (`int`, `str`, `float`, `bool`) | Query 파라미터 |
| `Schema`/`BaseModel` 타입 | Request Body (JSON) |

```python
@api.post("/items/{item_id}")
def update(request, item_id: int, item: Item, q: str):
    return {"item_id": item_id, "item": item.dict(), "q": q}
    # item_id -> Path (URL에 {item_id} 존재)
    # item    -> Body (Schema 타입)
    # q       -> Query (단순 str 타입)
```

### Query 파라미터 기본값과 필수 여부

```python
@api.get("/weapons")
def list_weapons(request, limit: int = 10, offset: int = 0):
    # limit, offset은 기본값이 있으므로 선택적
    return weapons[offset: offset + limit]

@api.get("/weapons/search")
def search_weapons(request, q: str, offset: int = 0):
    # q는 기본값이 없으므로 필수
    results = [w for w in weapons if q in w.lower()]
    return results[offset: offset + 10]
```

### Query 타입 변환

```python
from datetime import date

@api.get("/example")
def example(request, s: str = None, b: bool = None, d: date = None, i: int = None):
    return [s, b, d, i]
```

- **str**: 그대로 전달
- **bool**: `"1"`, `"true"`, `"True"`, `"on"`, `"yes"` -> `True`, 그 외 -> `False`
- **date**: ISO 형식 (`"2020-01-01"`) 또는 Unix 타임스탬프 (`1577836800`) 지원
- **int**: 정수로 변환, 실패 시 검증 오류

### Schema 기반 Query 파라미터

복잡한 쿼리 파라미터를 스키마로 그룹화할 수 있다:

```python
from typing import List
from pydantic import Field
from ninja import Query, Schema

class Filters(Schema):
    limit: int = 100
    offset: int = None
    query: str = None
    category__in: List[str] = Field(None, alias="categories")

@api.get("/filter")
def events(request, filters: Query[Filters]):
    return {"filters": filters.dict()}
```

---

## 2. Form[Schema] 폼 데이터

`application/x-www-form-urlencoded` 또는 `multipart/form-data` 형식의 요청 데이터를 처리한다.

### 개별 폼 필드

```python
from ninja import NinjaAPI, Form

@api.post("/login")
def login(request, username: Form[str], password: Form[str]):
    return {'username': username, 'password': '*****'}
```

### Schema를 사용한 폼 데이터

```python
from ninja import Form, Schema

class Item(Schema):
    name: str
    description: str = None
    price: float
    quantity: int

@api.post("/items")
def create(request, item: Form[Item]):
    return item
```

### 다중 소스 결합

폼 데이터를 경로 및 쿼리 파라미터와 결합할 수 있다:

```python
@api.post("/items/{item_id}")
def update(request, item_id: int, q: str, item: Form[Item]):
    return {"item_id": item_id, "item": item.dict(), "q": q}
```

### 빈 폼 필드 처리

Pydantic 유효성 검증기로 빈 문자열을 기본값으로 변환한다:

```python
from typing import Annotated, TypeVar
from pydantic import WrapValidator
from pydantic_core import PydanticUseDefault
from ninja import Form, Schema

def _empty_str_to_default(v, handler, info):
    if isinstance(v, str) and v == '':
        raise PydanticUseDefault
    return handler(v)

T = TypeVar('T')
EmptyStrToDefault = Annotated[T, WrapValidator(_empty_str_to_default)]

class Item(Schema):
    name: str
    description: str = None
    price: EmptyStrToDefault[float] = 0.0
    quantity: EmptyStrToDefault[int] = 0
    in_stock: EmptyStrToDefault[bool] = True

@api.post("/items-blank-default")
def update(request, item: Form[Item]):
    return item.dict()
```

### Annotated 구문 지원

```python
from typing import Annotated

@api.get("/annotated")
def annotated(request, data: Annotated[SomeData, Form()]):
    return {"data": data.dict()}
```

---

## 3. File[UploadedFile] 파일 업로드

### 단일 파일 업로드

```python
from ninja import NinjaAPI, File
from ninja.files import UploadedFile

@api.post("/upload")
def upload(request, file: File[UploadedFile]):
    data = file.read()
    return {'name': file.name, 'len': len(data)}
```

`UploadedFile`는 Django의 네이티브 업로드 기능을 감싸며 다음을 제공한다:
- 메서드: `read()`, `multiple_chunks()`, `chunks()`
- 속성: `name`, `size`, `content_type`, `charset` 등

### 다중 파일 업로드

```python
from typing import List
from ninja import NinjaAPI, File
from ninja.files import UploadedFile

@api.post("/upload-many")
def upload_many(request, files: File[List[UploadedFile]]):
    return [f.name for f in files]
```

### 파일 + 추가 필드 (Form과 결합)

파일과 메타데이터를 함께 보내려면 `multipart/form-data` 인코딩이 필요하다:

```python
from ninja import NinjaAPI, Schema, UploadedFile, Form, File
from datetime import date

class UserDetails(Schema):
    first_name: str
    last_name: str
    birthdate: date

@api.post('/users')
def create_user(request, details: Form[UserDetails], file: File[UploadedFile]):
    return [details.dict(), file.name]
```

### 다중 파일 + 추가 필드

```python
@api.post('/users')
def create_user(request, details: Form[UserDetails], files: File[list[UploadedFile]]):
    return [details.dict(), [f.name for f in files]]
```

### 선택적 파일 업로드

```python
@api.post('/users')
def create_user(request, details: Form[UserDetails], avatar: File[UploadedFile] = None):
    user = add_user_to_database(details)
    if avatar is not None:
        set_user_avatar(user)
```

### PUT/PATCH 파일 업로드

Django는 기본적으로 PUT/PATCH에서 `request.FILES`를 채우지 않는다. 호환성 미들웨어로 해결한다:

```python
# settings.py
MIDDLEWARE = [
    "ninja.compatibility.files.fix_request_files_middleware",
    # ... 기타 미들웨어
]
```

이 미들웨어는 PUT/PATCH 요청의 multipart 데이터를 자동으로 파싱한다.

---

## 4. FilterSchema

`FilterSchema`는 사용자 대면 필터링 파라미터를 Django Q 표현식으로 변환하는 특수 스키마 클래스다.

### 기본 설정

```python
from ninja import FilterSchema
from typing import Optional
from datetime import datetime

class BookFilterSchema(FilterSchema):
    name: Optional[str] = None
    author: Optional[str] = None
    created_after: Optional[datetime] = None
```

### API 핸들러에서 사용

```python
from ninja import Query

@api.get("/books")
def list_books(request, filters: Query[BookFilterSchema]):
    books = Book.objects.all()
    books = filters.filter(books)  # FilterSchema가 QuerySet에 필터 적용
    return books
```

수동 Q 표현식과 결합:

```python
@api.get("/books")
def list_books(request, filters: Query[BookFilterSchema]):
    q = Q(author__is_active=True) | Q(publisher__is_active=True)
    q &= filters.get_filter_expression()  # Q 표현식 직접 획득
    return Book.objects.filter(q)
```

---

## 5. FilterLookup

필드별 커스텀 조회 타입을 지정한다.

### 단일 조회

```python
from ninja import FilterSchema, FilterLookup
from typing import Annotated, Optional

class BookFilterSchema(FilterSchema):
    name: Annotated[Optional[str], FilterLookup("name__icontains")] = None
```

### 다중 조회 (기본적으로 OR로 결합)

하나의 필터 값으로 여러 필드를 동시에 검색할 때 유용하다:

```python
class BookFilterSchema(FilterSchema):
    search: Annotated[Optional[str], FilterLookup([
        "name__icontains",
        "author__name__icontains",
        "publisher__name__icontains"
    ])]
```

### 재사용 가능한 제네릭 필드

```python
IContainsField = Annotated[Optional[str], FilterLookup('__icontains')]

class BookFilterSchema(FilterSchema):
    name: IContainsField = None
```

---

## 6. Expression Connectors (OR, AND, XOR)

필터 표현식의 결합 방식을 제어한다.

### 기본 동작

- **필드 내부 표현식**: OR로 결합 (다중 조회 시)
- **필드 간 표현식**: AND로 결합

### 필드 수준 connector

```python
from ninja import FilterConfigDict, FilterLookup, FilterSchema

class BookFilterSchema(FilterSchema):
    active: Annotated[
        Optional[bool],
        FilterLookup(
            ["is_active", "publisher__is_active"],
            expression_connector="AND"  # 이 필드 내부를 AND로 결합
        )
    ] = None
```

### 클래스 수준 connector

```python
class BookFilterSchema(FilterSchema):
    name: Annotated[Optional[str], FilterLookup("name__icontains")] = None
    author: Annotated[Optional[str], FilterLookup("author__name__icontains")] = None

    model_config = FilterConfigDict(expression_connector="OR")
    # 필드 간 표현식을 OR로 결합 (기본값은 AND)
```

### 전체 예시

```python
class BookFilterSchema(FilterSchema):
    active: Annotated[
        Optional[bool],
        FilterLookup(
            ["is_active", "publisher__is_active"],
            expression_connector="AND"
        )
    ] = None
    name: Annotated[Optional[str], FilterLookup("name__icontains")] = None

    model_config = FilterConfigDict(expression_connector="OR")
```

사용 가능한 connector 값: `"OR"`, `"AND"`, `"XOR"` (XOR은 Django 4.1+ 필요)

---

## 7. ignore_none

`None` 값을 가진 필터 필드의 처리 방식을 제어한다.

### 필드 수준

```python
class BookFilterSchema(FilterSchema):
    tag: Annotated[Optional[str], FilterLookup("tag", ignore_none=False)] = None
    # ignore_none=False: None이어도 필터에 포함 (tag=None인 레코드 검색)
```

### 클래스 수준

```python
class BookFilterSchema(FilterSchema):
    model_config = FilterConfigDict(ignore_none=False)
    # 모든 필드에서 None을 무시하지 않음
```

기본값은 `ignore_none=True`로, `None` 값의 필터 필드는 무시된다.

---

## 8. 커스텀 필터 메서드 (filter_<field>)

### 필드별 커스텀 필터

특정 필드에 대해 커스텀 Q 표현식을 반환하는 메서드를 정의한다:

```python
class BookFilterSchema(FilterSchema):
    popular: Optional[bool] = None

    def filter_popular(self, value: bool) -> Q:
        return (
            Q(view_count__gt=1000) | Q(download_count__gt=100)
            if value
            else Q()
        )
```

### custom_expression 전체 오버라이드

전체 FilterSchema의 필터 로직을 커스텀한다. `custom_expression`은 다른 모든 정의보다 **우선**한다:

```python
class BookFilterSchema(FilterSchema):
    name: Optional[str] = None
    popular: Optional[bool] = None

    def custom_expression(self) -> Q:
        q = Q()
        if self.name:
            q &= Q(name__icontains=self.name)
        if self.popular:
            q &= (
                Q(view_count__gt=1000) |
                Q(downloads__gt=100) |
                Q(tag='popular')
            )
        return q
```

> `custom_expression` 메서드는 다른 모든 필터 정의(FilterLookup, filter_<field> 등)보다 우선한다.

---

## 9. 종합 예시: FilterSchema + Pagination

```python
from typing import List, Optional
from ninja import FilterSchema, FilterLookup, Query, Schema
from ninja.pagination import paginate, PageNumberPagination

class BookSchema(Schema):
    id: int
    name: str
    author: str
    price: float

class BookFilterSchema(FilterSchema):
    search: Annotated[Optional[str], FilterLookup([
        "name__icontains",
        "author__icontains",
    ])] = None
    min_price: Annotated[Optional[float], FilterLookup("price__gte")] = None
    max_price: Annotated[Optional[float], FilterLookup("price__lte")] = None

@api.get("/books", response=List[BookSchema])
@paginate(PageNumberPagination)
def list_books(request, filters: Query[BookFilterSchema]):
    books = Book.objects.all()
    books = filters.filter(books)
    return books
```

요청 예시: `/api/books?search=django&min_price=10&max_price=50&page=2`

---

## 10. Header와 Cookie 파라미터

### Header 파라미터

HTTP 헤더 값을 함수 파라미터로 추출한다:

```python
from ninja import Header

@api.get("/items")
def list_items(request, x_request_id: str = Header(...)):
    """X-Request-Id 헤더를 자동으로 추출"""
    return {"request_id": x_request_id}

# 선택적 헤더 (기본값 제공)
@api.get("/items")
def list_items(request, accept_language: str = Header("ko", alias="Accept-Language")):
    return {"language": accept_language}
```

**규칙**: 파라미터 이름은 언더스코어(`_`)를 하이픈(`-`)으로 자동 변환한다. `x_request_id` → `X-Request-Id`.

### Cookie 파라미터

HTTP 쿠키 값을 함수 파라미터로 추출한다:

```python
from ninja import Cookie

@api.get("/items")
def list_items(request, session_id: str = Cookie(...)):
    """session_id 쿠키를 자동으로 추출"""
    return {"session": session_id}

# 선택적 쿠키
@api.get("/items")
def list_items(request, theme: str = Cookie("light")):
    return {"theme": theme}
```

> 출처: Django Ninja 공식 문서 - Header Parameters, Cookie Parameters
