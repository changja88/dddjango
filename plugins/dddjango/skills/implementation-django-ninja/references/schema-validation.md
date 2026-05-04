# Schema와 유효성 검증 레퍼런스

> Django Ninja 공식 문서 기반 레퍼런스. Schema 정의, ModelSchema, 동적 생성, 리졸버, 별칭, 자기 참조 등을 다룬다.

---

## 1. Schema 기본 사용

Django Ninja의 `Schema`는 Pydantic의 `BaseModel`을 상속하며, 요청/응답 데이터의 유효성 검증과 직렬화를 담당한다. Django의 `Model`과 이름 충돌을 피하기 위해 `Schema`라는 이름을 사용한다.

```python
from ninja import Schema

class UserIn(Schema):
    username: str
    password: str

class UserOut(Schema):
    id: int
    username: str

@api.post("/users/", response=UserOut)
def create_user(request, data: UserIn):
    user = User(username=data.username)
    user.set_password(data.password)
    user.save()
    return user  # UserOut에 선언된 필드만 반환됨
```

핵심 동작:
- `response=UserOut`을 지정하면 반환 데이터에서 **선언된 필드만** 포함된다 (password 등 미선언 필드는 자동 제외)
- JSON 요청 본문의 타입 변환과 유효성 검증이 자동으로 수행된다
- OpenAPI 문서가 자동 생성된다

### 중첩 객체

```python
class UserSchema(Schema):
    id: int
    first_name: str
    last_name: str

class TaskSchema(Schema):
    id: int
    title: str
    is_completed: bool
    owner: UserSchema = None  # 중첩 스키마, 선택적
```

### QuerySet 반환

QuerySet을 직접 반환하면 자동으로 리스트로 평가된다:

```python
@api.get("/tasks", response=List[TaskSchema])
def tasks(request):
    return Task.objects.all()
```

### FileField / ImageField

파일/이미지 필드는 자동으로 URL 문자열로 변환된다:

```python
class PictureSchema(Schema):
    title: str
    image: str  # FileField/ImageField -> URL 문자열

# 출력: {"title": "Zebra", "image": "/static/images/zebra.jpg"}
```

---

## 2. ModelSchema

`ModelSchema`는 Django 모델에서 자동으로 스키마를 생성하는 특수 기반 클래스다. 모델과 API 스키마를 수동으로 동기화할 필요가 없다.

### 기본 사용

```python
from django.contrib.auth.models import User
from ninja import ModelSchema

class UserSchema(ModelSchema):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
```

위 코드는 아래와 동일한 스키마를 생성한다:

```python
class UserSchema(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
```

### Meta.fields 옵션

```python
class UserSchema(ModelSchema):
    class Meta:
        model = User
        fields = ['id', 'username']          # 명시적 필드 목록
        # fields = '__all__'                 # 모든 필드 (보안 위험 - 비권장)
```

> **주의**: `fields = '__all__'`은 해시된 비밀번호 등 민감한 데이터가 노출될 수 있으므로 사용을 피해야 한다.

### Meta.exclude 옵션

포함 대신 제외할 필드를 지정하는 역방향 접근:

```python
class UserSchema(ModelSchema):
    class Meta:
        model = User
        exclude = ['password', 'last_login', 'user_permissions']
```

### Meta.fields_optional

지정 필드를 선택적(Optional)으로 변환한다. PATCH 작업에 유용하다:

```python
class PatchGroupSchema(ModelSchema):
    class Meta:
        model = Group
        fields = ['id', 'name', 'description']
        fields_optional = '__all__'  # 모든 필드를 Optional로
        # fields_optional = ['description']  # 특정 필드만 Optional로
```

### 필드 타입 오버라이드

어노테이션으로 기본 필드 타입을 변경하거나 새 필드를 추가할 수 있다:

```python
class UserSchema(ModelSchema):
    groups: List[GroupSchema] = []  # 커스텀 타입으로 오버라이드

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
```

### 커스텀 Django 필드 매핑

사용자 정의 Django 필드를 Python 타입에 등록할 수 있다:

```python
from ninja.orm import register_field

register_field('VectorField', list[float])
```

---

## 3. create_schema() 동적 생성

런타임에 Django 모델로부터 동적으로 스키마를 생성한다.

### 함수 시그니처

```python
def create_schema(
    model,                              # Django 모델
    name="",                            # 생성될 클래스 이름 (기본값: 모델 이름)
    depth=0,                            # 중첩 관계 탐색 깊이
    fields: list[str] = None,           # 포함할 필드
    exclude: list[str] = None,          # 제외할 필드
    optional_fields: list[str] = None,  # Optional 필드
    custom_fields: list[tuple] = None   # 필드 타입 오버라이드
)
```

### 기본 사용

```python
from django.contrib.auth.models import User
from ninja.orm import create_schema

UserSchema = create_schema(User, fields=['id', 'username'])
```

### exclude 사용

```python
UserSchema = create_schema(User, exclude=[
    'password', 'last_login', 'is_superuser',
    'is_staff', 'groups', 'user_permissions'
])
```

### depth 사용 (관계 탐색)

```python
UserSchema = create_schema(User, depth=1, fields=['username', 'groups'])
# groups가 List[Group] 형태로 한 단계 깊이까지 탐색됨
```

> **보안 주의**: `create_schema`는 기본적으로 모든 모델 필드를 포함하므로, 반드시 `fields` 또는 `exclude`를 명시해야 한다.

---

## 4. resolve_<field> 메서드

필드 값을 동적으로 계산할 때 사용한다.

### 기본 리졸버

```python
class TaskSchema(Schema):
    id: int
    lower_title: str
    owner: Optional[str] = None

    @staticmethod
    def resolve_owner(obj):
        if not obj.owner:
            return
        return f"{obj.owner.first_name} {obj.owner.last_name}"

    @staticmethod
    def resolve_lower_title(obj):
        return obj.title.lower()
```

### Context 접근 (request 객체 활용)

리졸버에서 `context` 파라미터를 통해 요청 객체 등 추가 컨텍스트에 접근할 수 있다:

```python
class Data(Schema):
    a: int
    path: str = ""

    @staticmethod
    def resolve_path(obj, context):
        request = context["request"]
        return request.path
```

```python
class Payload(Schema):
    id: int
    name: str
    request_path: str

    @staticmethod
    def resolve_request_path(data, context):
        request = context["request"]
        return request.get_full_path()
```

> **V1 변경사항**: 기존의 `resolve_xxx(self, ...)` 패턴은 더 이상 지원되지 않으며, Pydantic의 내장 기능을 사용하는 `@staticmethod` 형태를 권장한다.

---

## 5. PatchDict

`PatchDict`는 모든 필드를 선택적으로 만들고, 실제 제공된 필드만 포함하는 딕셔너리를 반환하는 컨테이너다. PATCH 요청에 이상적이다.

```python
from ninja import PatchDict

class GroupSchema(Schema):
    name: str
    description: str
    due_date: date

@api.patch("/patch/{pk}")
def modify_data(request, pk: int, payload: PatchDict[GroupSchema]):
    obj = MyModel.objects.get(pk=pk)
    # payload는 유효성 검증을 통과한 제공된 필드만 포함하는 dict
    for attr, value in payload.items():
        setattr(obj, attr, value)
    obj.save()
```

기존 방식과 비교:

```python
# 기존 방식: exclude_unset=True 사용
@api.patch("/patch/{pk}")
def patch(request, pk: int, payload: PatchGroupSchema):
    updated_fields = payload.dict(exclude_unset=True)
    obj = MyModel.objects.get(pk=pk)
    for attr, value in updated_fields.items():
        setattr(obj, attr, value)
    obj.save()
```

`PatchDict`가 더 간결하고 명확한 의도를 전달한다.

---

## 6. 필드 Alias

### 기본 별칭 (alias)

Django 템플릿 변수 접근 구문과 호출 가능 객체 실행을 지원한다:

```python
from ninja import Field

class TaskSchema(Schema):
    completed: bool = Field(..., alias="is_completed")
    owner_first_name: str = Field(None, alias="owner.first_name")  # 점 표기법
    type_display: str = Field(None, alias="get_type_display")      # 호출 가능
```

### alias_generator (model_config)

`model_config`의 `alias_generator`를 사용하여 필드 이름을 일괄 변환할 수 있다:

```python
from pydantic import ConfigDict
from ninja import Schema

def to_camel(string: str) -> str:
    words = string.split('_')
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

class CamelModelSchema(Schema):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # 원래 이름과 별칭 모두 허용
    )
    str_field_name: str
    float_field_name: float
```

### by_alias 응답

응답에서 별칭을 적용하려면 `by_alias=True` 파라미터를 사용한다:

```python
@api.get("/users", response=list[UserSchema], by_alias=True)
def get_users(request):
    return User.objects.all()
# is_staff -> isStaff 형태로 변환되어 응답
```

---

## 7. from_orm() 직렬화

뷰 외부에서 Django 객체를 직접 직렬화할 때 사용한다:

```python
# 단일 객체
person = Person.objects.get(id=1)
data = PersonSchema.from_orm(person)
data.dict()  # {'id': 1, 'name': 'Mr. Smith'}
data.json()  # '{"id":1,"name":"Mr. Smith"}'

# 다수 객체
persons = Person.objects.all()
data = [PersonSchema.from_orm(i).dict() for i in persons]
```

---

## 8. 자기 참조 스키마 (Self-Referencing)

### Schema에서 자기 참조

인용 부호로 감싼 타입 이름을 사용하고, 정의 후 `model_rebuild()`를 호출해야 한다:

```python
class Organization(Schema):
    title: str
    part_of: 'Organization' = None  # 문자열로 자기 참조

Organization.model_rebuild()  # 반드시 호출
```

### create_schema()에서 자기 참조

`name` 파라미터를 반드시 지정하고, `custom_fields`에 문자열로 자기 참조를 설정한다:

```python
UserSchema = create_schema(
    User,
    name='UserSchema',  # name 파라미터 필수
    fields=['id', 'username'],
    custom_fields=[('manager', 'UserSchema', None)]
)
UserSchema.model_rebuild()  # 반드시 호출
```

> `create_schema()`로 생성한 스키마에서 `model_rebuild()`를 사용하려면 `name` 파라미터가 네임스페이스에 있어야 한다.
