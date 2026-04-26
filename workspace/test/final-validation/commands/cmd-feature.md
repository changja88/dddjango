# /feature 커맨드 실행 결과

**요청:** "회원 가입/로그인 기능을 개발해줘"

**로드된 스킬:**
- implementation-cleancode (Writing 모드)
- implementation-python (Writing 모드)
- implementation-django (Writing 모드)
- architecture-ddd (Design 모드)
- architecture-implementation-patterns (Design 모드)
- architecture-db (Design 모드)
- architecture-api (Design 모드)
- implementation-django-ninja (Writing 모드)

**TDD 여부:** No (TDD 없이 진행)

---

## Phase 1: 도메인 설계

> **스킬:** `architecture-ddd` / **모드:** Design

### 1.1 바운디드 컨텍스트 식별

| 바운디드 컨텍스트 | 서브도메인 유형 | 설명 |
|---|---|---|
| **Identity (인증/인가)** | 지원(Supporting) | 회원 가입, 로그인, 토큰 관리 |

이 기능은 단일 바운디드 컨텍스트(`Identity`)로 충분하다. 회원 가입과 로그인은 동일한 "사용자 신원" 개념을 공유하므로 분리할 필요가 없다.

### 1.2 유비쿼터스 언어 정의

| 용어 | 정의 |
|---|---|
| **Member** | 서비스에 가입한 사용자. 이메일과 비밀번호로 식별된다 |
| **Email** | 회원의 고유 식별자이자 로그인 수단. 형식 검증이 필요한 값 객체 |
| **Password** | 해싱된 비밀번호. 평문은 절대 저장하지 않는다 |
| **Sign Up (가입)** | 새로운 Member를 생성하는 행위 |
| **Sign In (로그인)** | 자격 증명을 검증하고 인증 토큰을 발급하는 행위 |
| **Authentication Token** | 인증된 사용자임을 증명하는 Bearer 토큰 |
| **Member Registered Event** | 새 회원이 가입 완료되었음을 알리는 도메인 이벤트 |

### 1.3 Aggregate, Entity, Value Object 설계

**Aggregate: Member (애그리거트 루트)**

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


# --- 값 객체 ---

@dataclass(frozen=True, slots=True)
class Email:
    """이메일 값 객체 -- 형식 검증을 캡슐화"""
    address: str

    def __post_init__(self) -> None:
        if not self.address or "@" not in self.address:
            raise ValueError(f"유효하지 않은 이메일: {self.address}")


@dataclass(frozen=True, slots=True)
class HashedPassword:
    """해싱된 비밀번호 값 객체 -- 평문을 절대 저장하지 않는다"""
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("비밀번호 해시는 비어있을 수 없습니다")


class MemberStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


# --- 도메인 이벤트 ---

@dataclass(frozen=True)
class MemberRegisteredEvent:
    """회원 가입 완료 이벤트"""
    member_id: str
    email: str
    occurred_at: datetime


# --- 애그리거트 루트 ---

@dataclass
class Member:
    """회원 애그리거트 루트

    - Member가 애그리거트 루트이다
    - Email, HashedPassword는 값 객체
    - 모든 상태 변경은 Member를 통해서만 수행한다
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    email: Email = None
    _password: HashedPassword = None
    nickname: str = ""
    _status: MemberStatus = MemberStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    _events: list = field(default_factory=list)

    @classmethod
    def register(
        cls,
        email: Email,
        hashed_password: HashedPassword,
        nickname: str,
    ) -> Member:
        """회원 가입 팩토리 메서드 -- 비즈니스 규칙을 캡슐화"""
        if not nickname:
            raise ValueError("닉네임은 필수입니다")

        member = cls(
            email=email,
            _password=hashed_password,
            nickname=nickname,
        )
        member._events.append(
            MemberRegisteredEvent(
                member_id=member.id,
                email=email.address,
                occurred_at=datetime.now(),
            )
        )
        return member

    def verify_password(self, hashed_input: str) -> bool:
        """비밀번호 검증 -- 해싱된 값 비교"""
        return self._password.value == hashed_input

    def deactivate(self) -> None:
        if self._status != MemberStatus.ACTIVE:
            raise ValueError("이미 비활성화된 회원입니다")
        self._status = MemberStatus.INACTIVE

    def collect_domain_events(self) -> list:
        events = list(self._events)
        self._events.clear()
        return events
```

### 1.4 도메인 이벤트 정의

| 이벤트 | 발생 시점 | 후속 처리 |
|---|---|---|
| `MemberRegisteredEvent` | 회원 가입 완료 시 | 환영 이메일 발송, 초기 설정 생성 등 (최종 일관성) |

---

## Phase 2: 아키텍처 선택

> **스킬:** `architecture-implementation-patterns` / **모드:** Design

### 2.1 아키텍처 패턴 선택

**선택: 레이어드 아키텍처 (Layered Architecture)**

회원 가입/로그인은 복잡한 도메인 로직이 아니라 지원(Supporting) 서브도메인이다. 외부 통합이 적고 CRUD에 가까우므로 레이어드 아키텍처로 충분하다. 헥사고날을 적용하면 과도한 엔지니어링이 된다.

### 2.2 레이어 분리 및 의존성 방향

```
Presentation Layer (API)  -->  Application Layer (Service)  -->  Domain Layer  -->  Infra Layer (ORM)
```

- **Presentation**: Django Ninja Router, Schema
- **Application**: 유스케이스 조율 (가입 서비스, 로그인 서비스)
- **Domain**: Member 애그리거트, 값 객체, 도메인 이벤트
- **Infra**: Django ORM 모델, 리포지토리 구현

### 2.3 프로젝트 폴더 구조

```
applications/
└── identity/                          # Identity 바운디드 컨텍스트
    ├── domain_layer/
    │   ├── member/                    # Member 애그리거트
    │   │   ├── member.py              # 애그리거트 루트
    │   │   ├── email.py               # Email 값 객체
    │   │   └── hashed_password.py     # HashedPassword 값 객체
    │   ├── value_object/
    │   ├── repository/
    │   │   └── member_repo.py         # MemberRepository ABC
    │   └── event/
    │       └── member_events.py       # MemberRegisteredEvent
    │
    ├── application_layer/
    │   ├── signup_service.py           # 회원 가입 유스케이스
    │   ├── signin_service.py           # 로그인 유스케이스
    │   └── token_service.py            # 토큰 생성/검증
    │
    ├── infra_layer/
    │   ├── django_identity/            # Django 앱
    │   │   ├── apps.py
    │   │   ├── models/
    │   │   │   ├── __init__.py
    │   │   │   └── member_model.py     # MemberModel (ORM)
    │   │   └── admin.py
    │   ├── repository/
    │   │   └── member_repo.py          # DjangoMemberRepository
    │   └── password_hasher/
    │       └── django_hasher.py        # Django 비밀번호 해싱 어댑터
    │
    ├── presentation_layer/
    │   ├── routers.py                  # identity 라우터 등록
    │   ├── api/
    │   │   └── auth_api.py             # 가입/로그인 엔드포인트
    │   └── schema/
    │       ├── auth_schema.py          # 요청/응답 스키마
    │       └── error_codes.py          # 에러 코드 상수
    │
    └── tests/
        ├── conftest.py
        ├── domain/
        ├── application/
        ├── infra/
        └── api/
```

---

## Phase 3: DB 스키마 설계

> **스킬:** `architecture-db` / **모드:** Design

### 3.1 정규화 수준: 3NF

회원 테이블은 단일 엔티티이므로 정규화 위반 가능성이 낮다. 3NF를 기본으로 유지한다.

### 3.2 테이블 설계

**members 테이블**

| 컬럼 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| `id` | UUID | PK | 대리키 (uuid4) |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | 로그인 식별자 |
| `password` | VARCHAR(128) | NOT NULL | bcrypt 해시 |
| `nickname` | VARCHAR(50) | NOT NULL | 표시 이름 |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'active' | active/inactive |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW | 가입 일시 |
| `updated_at` | TIMESTAMP | NOT NULL, AUTO UPDATE | 수정 일시 |

### 3.3 인덱스 전략

| 인덱스 | 컬럼 | 유형 | 근거 |
|---|---|---|---|
| `pk` | `id` | B+Tree (PK) | 기본키 |
| `ix_members_email` | `email` | B+Tree UNIQUE | 로그인 시 이메일 조회 (WHERE email = ?) |
| `ix_members_status` | `status` | 부분 인덱스 (WHERE status = 'active') | 활성 회원 필터링 |

### 3.4 Django ORM 모델

```python
import uuid

from django.db import models


class MemberModel(models.Model):
    """회원 ORM 모델"""

    class Status(models.TextChoices):
        ACTIVE = "active", "활성"
        INACTIVE = "inactive", "비활성"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=128)
    nickname = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_default=models.Value("active"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "members"
        indexes = [
            models.Index(
                fields=["status"],
                name="ix_members_status",
                condition=models.Q(status="active"),
            ),
        ]

    def __str__(self) -> str:
        return f"Member({self.email})"
```

---

## Phase 4: REST API 설계

> **스킬:** `architecture-api` / **모드:** Design

### 4.1 URL 구조 및 리소스 설계

| 메서드 | URL | 설명 | 인증 |
|---|---|---|---|
| `POST` | `/api/v1/auth/signup` | 회원 가입 | 불필요 (auth=None) |
| `POST` | `/api/v1/auth/signin` | 로그인 (토큰 발급) | 불필요 (auth=None) |
| `GET` | `/api/v1/auth/me` | 현재 사용자 정보 조회 | Bearer Token |
| `POST` | `/api/v1/auth/token/refresh` | 토큰 갱신 | 불필요 (Refresh Token) |

### 4.2 HTTP 메서드/상태코드 매핑

| 엔드포인트 | 성공 | 실패 |
|---|---|---|
| `POST /auth/signup` | 201 Created | 400 Bad Request, 409 Conflict (이메일 중복) |
| `POST /auth/signin` | 200 OK | 401 Unauthorized (잘못된 자격 증명) |
| `GET /auth/me` | 200 OK | 401 Unauthorized |
| `POST /auth/token/refresh` | 200 OK | 401 Unauthorized |

### 4.3 에러 포맷 (RFC 9457)

```json
{
  "type": "https://api.example.com/probs/duplicate-email",
  "title": "Email already registered.",
  "status": 409,
  "detail": "The email 'user@example.com' is already in use.",
  "instance": "/api/v1/auth/signup"
}
```

```json
{
  "type": "https://api.example.com/probs/invalid-credentials",
  "title": "Invalid credentials.",
  "status": 401,
  "detail": "Email or password is incorrect.",
  "instance": "/api/v1/auth/signin"
}
```

### 4.4 요청/응답 스키마

**POST /auth/signup**
```json
// Request
{
  "email": "user@example.com",
  "password": "SecureP@ss123",
  "nickname": "Hyun"
}

// Response (201)
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "nickname": "Hyun"
}
```

**POST /auth/signin**
```json
// Request
{
  "email": "user@example.com",
  "password": "SecureP@ss123"
}

// Response (200)
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**GET /auth/me**
```json
// Response (200)
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "nickname": "Hyun",
  "status": "active",
  "created_at": "2026-04-06T12:00:00Z"
}
```

### 4.5 페이지네이션/버저닝 전략

- **버저닝**: URL 경로 기반 (`/api/v1/`)
- **페이지네이션**: 이 기능에서는 목록 엔드포인트가 없으므로 불필요

---

## Phase 5: Django Ninja 구현

> **스킬:** `implementation-django-ninja` / **모드:** Writing

### 5.1 Schema 정의

```python
# presentation_layer/schema/auth_schema.py

from datetime import datetime

from ninja import Schema


class SignUpIn(Schema):
    """회원 가입 요청"""
    email: str
    password: str
    nickname: str


class SignUpOut(Schema):
    """회원 가입 응답"""
    id: str
    email: str
    nickname: str


class SignInIn(Schema):
    """로그인 요청"""
    email: str
    password: str


class TokenOut(Schema):
    """토큰 응답"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class MemberOut(Schema):
    """회원 정보 응답"""
    id: str
    email: str
    nickname: str
    status: str
    created_at: datetime


class RefreshIn(Schema):
    """토큰 갱신 요청"""
    refresh_token: str


class ErrorOut(Schema):
    """RFC 9457 Problem Details 에러 응답"""
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""
```

### 5.2 인증 클래스

```python
# presentation_layer/schema/auth_bearer.py

from ninja.security import HttpBearer

from applications.identity.application_layer.token_service import TokenService


class AuthBearer(HttpBearer):
    """Bearer 토큰 인증"""

    def authenticate(self, request, token: str):
        token_service = TokenService()
        payload = token_service.verify_access_token(token)
        if payload is None:
            return None
        return payload
```

### 5.3 Application Service (유스케이스 조율)

```python
# application_layer/signup_service.py

from applications.identity.domain_layer.member.email import Email
from applications.identity.domain_layer.member.hashed_password import HashedPassword
from applications.identity.domain_layer.member.member import Member
from applications.identity.domain_layer.repository.member_repo import MemberRepository


class SignUpService:
    """회원 가입 유스케이스"""

    def __init__(self, member_repo: MemberRepository, password_hasher) -> None:
        self._member_repo = member_repo
        self._password_hasher = password_hasher

    def execute(self, email: str, password: str, nickname: str) -> Member:
        email_vo = Email(address=email)

        if self._member_repo.exists_by_email(email_vo):
            raise DuplicateEmailError(email)

        hashed = HashedPassword(
            value=self._password_hasher.hash(password),
        )
        member = Member.register(
            email=email_vo,
            hashed_password=hashed,
            nickname=nickname,
        )
        self._member_repo.save(member)
        return member


class DuplicateEmailError(Exception):
    """이메일 중복 에러"""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"이미 등록된 이메일입니다: {email}")
```

```python
# application_layer/signin_service.py

from applications.identity.domain_layer.member.email import Email
from applications.identity.domain_layer.repository.member_repo import MemberRepository


class SignInService:
    """로그인 유스케이스"""

    def __init__(
        self,
        member_repo: MemberRepository,
        password_hasher,
        token_service,
    ) -> None:
        self._member_repo = member_repo
        self._password_hasher = password_hasher
        self._token_service = token_service

    def execute(self, email: str, password: str) -> dict:
        email_vo = Email(address=email)
        member = self._member_repo.find_by_email(email_vo)

        if member is None:
            raise InvalidCredentialsError()

        if not member.verify_password(
            self._password_hasher.hash(password),
        ):
            raise InvalidCredentialsError()

        access_token = self._token_service.create_access_token(member.id)
        refresh_token = self._token_service.create_refresh_token(member.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,
        }


class InvalidCredentialsError(Exception):
    """인증 실패 에러"""

    def __init__(self) -> None:
        super().__init__("이메일 또는 비밀번호가 올바르지 않습니다")
```

### 5.4 Repository 인터페이스 및 구현

```python
# domain_layer/repository/member_repo.py

from abc import ABC, abstractmethod

from applications.identity.domain_layer.member.email import Email
from applications.identity.domain_layer.member.member import Member


class MemberRepository(ABC):
    """회원 리포지토리 인터페이스"""

    @abstractmethod
    def save(self, member: Member) -> None: ...

    @abstractmethod
    def find_by_id(self, member_id: str) -> Member | None: ...

    @abstractmethod
    def find_by_email(self, email: Email) -> Member | None: ...

    @abstractmethod
    def exists_by_email(self, email: Email) -> bool: ...
```

```python
# infra_layer/repository/member_repo.py

from applications.identity.domain_layer.member.email import Email
from applications.identity.domain_layer.member.hashed_password import HashedPassword
from applications.identity.domain_layer.member.member import Member, MemberStatus
from applications.identity.domain_layer.repository.member_repo import MemberRepository
from applications.identity.infra_layer.django_identity.models import MemberModel


class DjangoMemberRepository(MemberRepository):
    """Django ORM 기반 회원 리포지토리"""

    def save(self, member: Member) -> None:
        MemberModel.objects.update_or_create(
            id=member.id,
            defaults={
                "email": member.email.address,
                "password": member._password.value,
                "nickname": member.nickname,
                "status": member._status.value,
            },
        )

    def find_by_id(self, member_id: str) -> Member | None:
        try:
            model = MemberModel.objects.get(id=member_id)
            return self._to_domain(model)
        except MemberModel.DoesNotExist:
            return None

    def find_by_email(self, email: Email) -> Member | None:
        try:
            model = MemberModel.objects.get(email=email.address)
            return self._to_domain(model)
        except MemberModel.DoesNotExist:
            return None

    def exists_by_email(self, email: Email) -> bool:
        return MemberModel.objects.filter(email=email.address).exists()

    @staticmethod
    def _to_domain(model: MemberModel) -> Member:
        member = Member(
            id=str(model.id),
            email=Email(address=model.email),
            _password=HashedPassword(value=model.password),
            nickname=model.nickname,
            _status=MemberStatus(model.status),
            created_at=model.created_at,
        )
        return member
```

### 5.5 Router 및 엔드포인트 구현

```python
# presentation_layer/api/auth_api.py

from django.http import HttpRequest
from ninja import Router

from applications.identity.application_layer.signin_service import (
    InvalidCredentialsError,
    SignInService,
)
from applications.identity.application_layer.signup_service import (
    DuplicateEmailError,
    SignUpService,
)
from applications.identity.application_layer.token_service import TokenService
from applications.identity.infra_layer.password_hasher.django_hasher import (
    DjangoPasswordHasher,
)
from applications.identity.infra_layer.repository.member_repo import (
    DjangoMemberRepository,
)
from applications.identity.presentation_layer.schema.auth_bearer import AuthBearer
from applications.identity.presentation_layer.schema.auth_schema import (
    ErrorOut,
    MemberOut,
    RefreshIn,
    SignInIn,
    SignUpIn,
    SignUpOut,
    TokenOut,
)

router = Router(tags=["auth"])

_member_repo = DjangoMemberRepository()
_password_hasher = DjangoPasswordHasher()
_token_service = TokenService()


@router.post(
    "/signup",
    response={201: SignUpOut, 409: ErrorOut},
    auth=None,
)
def signup(request: HttpRequest, payload: SignUpIn) -> tuple[int, SignUpOut | ErrorOut]:
    """회원 가입"""
    service = SignUpService(
        member_repo=_member_repo,
        password_hasher=_password_hasher,
    )
    try:
        member = service.execute(
            email=payload.email,
            password=payload.password,
            nickname=payload.nickname,
        )
    except DuplicateEmailError:
        return 409, ErrorOut(
            type="https://api.example.com/probs/duplicate-email",
            title="Email already registered.",
            status=409,
            detail=f"The email '{payload.email}' is already in use.",
            instance="/api/v1/auth/signup",
        )

    return 201, SignUpOut(
        id=member.id,
        email=member.email.address,
        nickname=member.nickname,
    )


@router.post(
    "/signin",
    response={200: TokenOut, 401: ErrorOut},
    auth=None,
)
def signin(request: HttpRequest, payload: SignInIn) -> tuple[int, TokenOut | ErrorOut]:
    """로그인"""
    service = SignInService(
        member_repo=_member_repo,
        password_hasher=_password_hasher,
        token_service=_token_service,
    )
    try:
        token_data = service.execute(
            email=payload.email,
            password=payload.password,
        )
    except InvalidCredentialsError:
        return 401, ErrorOut(
            type="https://api.example.com/probs/invalid-credentials",
            title="Invalid credentials.",
            status=401,
            detail="Email or password is incorrect.",
            instance="/api/v1/auth/signin",
        )

    return 200, TokenOut(**token_data)


@router.get(
    "/me",
    response=MemberOut,
    auth=AuthBearer(),
)
def me(request: HttpRequest) -> MemberOut:
    """현재 사용자 정보 조회"""
    member_id = request.auth["member_id"]
    member = _member_repo.find_by_id(member_id)
    return MemberOut(
        id=member.id,
        email=member.email.address,
        nickname=member.nickname,
        status=member._status.value,
        created_at=member.created_at,
    )


@router.post(
    "/token/refresh",
    response={200: TokenOut, 401: ErrorOut},
    auth=None,
)
def refresh_token(
    request: HttpRequest,
    payload: RefreshIn,
) -> tuple[int, TokenOut | ErrorOut]:
    """토큰 갱신"""
    member_id = _token_service.verify_refresh_token(payload.refresh_token)
    if member_id is None:
        return 401, ErrorOut(
            type="https://api.example.com/probs/invalid-token",
            title="Invalid refresh token.",
            status=401,
            detail="The refresh token is invalid or expired.",
            instance="/api/v1/auth/token/refresh",
        )

    access_token = _token_service.create_access_token(member_id)
    refresh_token = _token_service.create_refresh_token(member_id)

    return 200, TokenOut(
        access_token=access_token,
        refresh_token=refresh_token,
    )
```

### 5.6 라우터 등록

```python
# presentation_layer/routers.py

from ninja import NinjaAPI

from applications.identity.presentation_layer.api.auth_api import router as auth_router

api_v1 = NinjaAPI(version="1.0.0", title="Identity API")
api_v1.add_router("/auth/", auth_router)
```

```python
# config/urls.py

from django.urls import path

from applications.identity.presentation_layer.routers import api_v1

urlpatterns = [
    path("api/v1/", api_v1.urls),
]
```

### 5.7 에러 핸들러 (글로벌)

```python
# presentation_layer/error_handler.py

from ninja import NinjaAPI

from applications.identity.presentation_layer.schema.auth_schema import ErrorOut


def register_error_handlers(api: NinjaAPI) -> None:
    """글로벌 에러 핸들러 등록"""

    @api.exception_handler(ValueError)
    def handle_value_error(request, exc):
        return api.create_response(
            request,
            ErrorOut(
                type="https://api.example.com/probs/validation-error",
                title="Validation Error",
                status=422,
                detail=str(exc),
                instance=request.path,
            ).dict(),
            status=422,
        )

    @api.exception_handler(Exception)
    def handle_unexpected_error(request, exc):
        return api.create_response(
            request,
            ErrorOut(
                type="https://api.example.com/probs/internal-error",
                title="Internal Server Error",
                status=500,
                detail="An unexpected error occurred.",
                instance=request.path,
            ).dict(),
            status=500,
        )
```

---

> **관련 스킬 참조:**
> - 비밀번호 해싱/보안 강화 --> **implementation-django** 스킬 (보안 섹션)
> - JWT 토큰 구현 상세 --> **implementation-django-ninja** 스킬 (인증 섹션)
> - 회원 관련 추가 기능 (프로필, 권한) --> **architecture-ddd** 스킬 (도메인 확장)
> - 이메일 인증 비동기 처리 --> **architecture-implementation-patterns** 스킬 (이벤트 소싱/CQRS)
> - DB 쿼리 최적화 --> **architecture-db** 스킬 (인덱스/성능)
> - API 확장 (소셜 로그인, OAuth) --> **architecture-api** 스킬 (인증/인가)
