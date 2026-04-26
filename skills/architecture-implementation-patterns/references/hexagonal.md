# 아키텍처 스타일과 의존성 역전

## 1. Layered Architecture (계층형)

> 출처: Martin Fowler, *Patterns of Enterprise Application Architecture* (2002)

```
Presentation → Domain → Data Source
```

**핵심 원칙:**
- 위에서 아래로 단방향 의존
- 각 레이어는 자신의 소비자(위 레이어)를 모른다
- 레이어 간 낮은 결합, 레이어 내 높은 응집

**한계:**
- DB가 최하위 레이어 → 암묵적으로 DB 중심 설계가 됨
- 도메인 로직이 인프라(Data Source 계층)에 결합됨
- DIP 없이는 도메인이 DB 구현에 직접 의존

---

## 2. Hexagonal Architecture (Ports & Adapters)

> 출처: Alistair Cockburn (2005), *Hexagonal Architecture Explained* (2023)

> "Create your application to work without either a UI or a database so you can run automated regression-tests against the application, work when the database becomes unavailable, and link applications together without any user involvement."

### 핵심 개념

**Port (포트)**: 애플리케이션의 목적 있는 대화(purposeful conversation)를 정의하는 인터페이스. 대부분의 애플리케이션에 최소 2개 이상의 포트가 존재하므로, 1차원 레이어 다이어그램으로는 표현이 불가하다 — 이것이 육각형을 사용하는 이유이다.

**Adapter (어댑터)**: 특정 기술을 사용하여 포트와 상호작용하는 구현체. 하나의 포트에 여러 어댑터 가능 (SQL, flat file, mock 등).

| 구분 | Driving (Primary) | Driven (Secondary) |
|---|---|---|
| 방향 | 외부 → 애플리케이션 | 애플리케이션 → 외부 |
| 역할 | 애플리케이션을 구동 | 애플리케이션이 구동 |
| 예시 | REST Controller, CLI, Test | DB Adapter, 외부 API, Mock |

### 코드 구조

```
application/              # 핵심 비즈니스 로직
  ports/
    driving/              # Primary actor가 호출하는 인터페이스 (Use Case)
    driven/               # Application이 외부에 요청하는 인터페이스
adapters/
  driving/                # UI controller, REST, CLI, test harness
  driven/                 # DB adapter, mock adapter, 외부 API adapter
```

---

## 3. Clean Architecture

> 출처: Robert C. Martin, *The Clean Architecture* (2012)

> "Source code dependencies can only point inwards. Nothing in an inner circle can know anything at all about something in an outer circle." — The Dependency Rule

### 4가지 독립성 목표
1. **Independent of Frameworks** — 프레임워크를 도구로 사용하되 시스템을 끼워맞추지 않음
2. **Testable** — UI, DB, Web Server 없이 비즈니스 규칙 테스트 가능
3. **Independent of UI** — 비즈니스 규칙 변경 없이 UI 교체 가능
4. **Independent of Database** — DB 기술 교체 가능

### 동심원 4계층 (바깥에서 안으로)

| 계층 | 내용 | 위치 |
|---|---|---|
| Frameworks & Drivers | DB, Web Framework, glue code | 최외곽 |
| Interface Adapters | Controllers, Presenters, Gateways | 3층 |
| Use Cases | 유스케이스 캡슐화, 데이터 흐름 조율 | 2층 |
| Entities | 엔터프라이즈 비즈니스 규칙 | 최내곽 |

**경계 횡단 규칙**: 오직 simple data structures(DTO, hashmap, 함수 인자)만 경계를 넘어야 한다. Entity나 DB Row를 직접 전달하면 Dependency Rule 위반이다.

---

## 4. Onion Architecture

> 출처: Jeffrey Palermo (2008)

> "The database is not the center. It is external."

### 5가지 핵심 원칙

1. 독립적 객체 모델 중심으로 구축
2. 내부 레이어가 인터페이스를 정의
3. 외부 레이어가 인터페이스를 구현
4. 결합 방향은 항상 중심을 향함
5. 인프라 없이 핵심 코드가 컴파일/실행 가능

### 동심원 구조 (안에서 밖으로)

1. **Domain Model** — Entity, Value Object
2. **Domain Services** — 도메인 인터페이스, 도메인 서비스
3. **Application Services** — Use Case 조율, Repository 인터페이스 정의
4. **Infrastructure / UI / Tests** — DB 구현, UI, 외부 서비스

Hexagonal 위에 DDD 개념을 결합하여 비즈니스 로직의 내부 구조를 명시적으로 조직화한 것이 핵심 기여이다.

---

## 5. DIP (Dependency Inversion Principle)

> 출처: Robert C. Martin, *The Dependency Inversion Principle*, C++ Report (1996)

### 원칙 정의

**A.** 고수준 모듈이 저수준 모듈에 의존해서는 안 된다. 둘 다 추상화에 의존해야 한다.

**B.** 추상화가 세부사항에 의존해서는 안 된다. 세부사항이 추상화에 의존해야 한다.

### Ownership Inversion (소유권 역전)

단순히 의존성 방향만 역전하는 것이 아니라, **인터페이스의 소유권**도 역전시켜야 한다. 추상화(인터페이스)는 상위/정책 레이어가 정의하고, 하위 레이어가 이를 구현한다.

```python
from abc import ABC, abstractmethod

# 도메인 계층이 인터페이스를 정의하고 소유한다
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: Money, method: PaymentMethod) -> PaymentResult: ...

# 인프라 계층이 구현한다
class StripePaymentGateway(PaymentGateway):
    def charge(self, amount: Money, method: PaymentMethod) -> PaymentResult:
        # Stripe API 호출
        ...
```

### DIP vs DI

- **DIP**: 설계 원칙 — 의존성 방향에 대한 규칙
- **DI (Dependency Injection)**: 구현 기법 — 런타임에 구체 구현을 주입하는 메커니즘
- DI는 DIP를 달성하는 수단 중 하나이지만, DIP 자체는 아니다

---

## 6. 비교와 선택 기준

### 공통점

R. Martin이 Clean Architecture에서 직접 언급: *"Though these architectures all vary somewhat in their details, they are very similar. They all have the same objective, which is the separation of concerns."*

| 공통 특성 | 설명 |
|---|---|
| 도메인 중심 | 비즈니스 로직이 아키텍처의 중심에 위치 |
| 의존성 방향 | 결합 방향이 항상 안쪽(도메인)을 향함 |
| DIP 기반 | 내부가 인터페이스를 정의하고, 외부가 구현 |
| 테스트 용이성 | 외부 장치 없이 비즈니스 규칙 테스트 가능 |

### 차이점

| 기준 | Layered | Hexagonal | Onion | Clean |
|---|---|---|---|---|
| 의존성 방향 | 위→아래 | 안↔밖 (대칭) | 밖→안 | 밖→안 |
| DIP 적용 | 선택적 | 필수 | 필수 | 필수 |
| 내부 구조 | 3층 | 미지정 | 3층 (DDD 기반) | 4층 |
| DB 위치 | 최하위 (중심) | 외부 Adapter | 최외곽 | 최외곽 |
| 주요 초점 | 기술적 관심사 분리 | 외부 교체 가능성 | DDD 도메인 구조 | 아키텍처 경계 |

### 진화 계보

```
Layered (2002, Fowler)
  → 한계: DB 중심, 도메인-인프라 결합
Hexagonal (2005, Cockburn)
  → DIP를 아키텍처 수준으로, 안/밖 대칭
Onion (2008, Palermo)
  → Hexagonal + DDD, 내부 레이어 명시
Clean (2012, R. Martin)
  → Hexagonal + Onion 통합, 4계층 일반화
```

### 선택 기준

| 상황 | 적합한 패턴 |
|---|---|
| 단순 CRUD, 빠른 프로토타이핑 | Layered |
| 외부 통합 다수, 진입점 다양 | Hexagonal |
| DDD 적용, 도메인 구조 명시 필요 | Onion |
| 대규모 시스템, 엄격한 경계 관리 | Clean |
| **실무적 권고** | Hexagonal을 기본으로 채택하고, 도메인 내부 구조는 Onion/Clean 참고 |
