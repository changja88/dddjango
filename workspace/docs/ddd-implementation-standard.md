# DDD Implementation Standard

이 문서는 `dddjango`가 DDD를 Python/Django 코드로 구현할 때 따르는 기준이다. Django는 구현 생태계이며, 판단의 출발점은 도메인 모델이다.

## 1. 판단 순서

DDD 작업은 다음 순서로 판단한다.

1. 해결하려는 비즈니스 문제를 식별한다.
2. 하위 도메인이 Core, Supporting, Generic 중 무엇인지 판단한다.
3. 바운디드 컨텍스트 경계를 잡는다.
4. 컨텍스트 간 관계를 컨텍스트 맵으로 정리한다.
5. 유비쿼터스 언어를 정리한다.
6. 애그리거트, 엔티티, 값 객체, 불변식을 식별한다.
7. 유스케이스와 application service의 책임을 정한다.
8. 트랜잭션 경계와 일관성 요구를 판단한다.
9. Django ORM, DB schema, API, test로 매핑한다.

전략 설계 없이 repository, entity, service 같은 전술 패턴부터 적용하지 않는다.

## 2. 하위 도메인별 구현 강도

| 하위 도메인 | 기준 | 구현 전략 |
|---|---|---|
| Core | 경쟁력의 원천, 복잡하고 자주 바뀌는 규칙 | 풍부한 도메인 모델, 명시적 invariant, 테스트 우선 |
| Supporting | 비즈니스 보조, CRUD 중심, 낮은 복잡도 | Django다운 단순 구조, 필요한 service만 추가 |
| Generic | 업계 공통 문제, 차별화 낮음 | 외부 솔루션, 라이브러리, 기존 패키지 우선 |

모든 기능에 같은 수준의 DDD 구조를 강제하지 않는다. 구조의 무게는 도메인 복잡도와 변경 위험에 맞춘다.

## 3. 바운디드 컨텍스트와 언어

유비쿼터스 언어는 바운디드 컨텍스트 안에서만 일관된다. 같은 단어가 다른 컨텍스트에서 다른 의미를 갖는 경우 하나의 공통 모델로 억지로 합치지 않는다.

컨텍스트 간 통합은 관계 유형을 먼저 판단한다.

- Partnership: 두 컨텍스트가 함께 계획하고 함께 변경해야 할 때
- Shared Kernel: 작은 공통 모델을 두 팀이 함께 관리할 때
- Customer-Supplier: 상류/하류 팀의 요구 조율이 필요한 때
- Conformist: 하류가 상류 모델을 그대로 따르는 것이 더 현실적일 때
- Anti-Corruption Layer: 외부/레거시 모델이 내부 도메인을 오염시킬 위험이 있을 때
- Open Host Service: 다른 컨텍스트가 안정적으로 사용할 공개 API가 필요할 때
- Published Language: 통합 메시지나 API 계약의 공통 언어가 필요할 때
- Separated Ways: 통합 비용이 이득보다 클 때
- Big Ball of Mud: 경계가 무너진 레거시 모델을 격리해서 다뤄야 할 때

## 4. 애그리거트와 불변식

애그리거트는 불변식을 보호하는 최소 경계다.

애그리거트는 작게 유지한다. 한 애그리거트가 너무 많은 엔티티와 규칙을 소유하면 동시성, 성능, 이해 비용이 증가한다.

다른 애그리거트는 객체 참조보다 식별자 참조를 기본으로 한다. 여러 애그리거트를 한 번에 변경해야 한다면 경계가 잘못되었는지 먼저 의심한다.

하나의 트랜잭션은 기본적으로 하나의 애그리거트 불변식을 보호한다. 여러 애그리거트 간 일관성은 도메인 이벤트, eventual consistency, outbox를 검토한다.

값 객체는 식별자가 아니라 값과 불변식으로 정의한다. 금액, 기간, 좌표, 수량, 이메일, 정책 조건처럼 유효성 자체가 의미인 개념은 값 객체 후보로 본다.

## 5. Domain Events

도메인 이벤트는 이미 발생한 도메인 사실을 표현한다. 이름은 과거형으로 둔다.

도메인 이벤트를 사용할 때는 다음을 명시한다.

- 이벤트 이름
- 이벤트를 발생시키는 aggregate 또는 use case
- 영향을 받는 aggregate, bounded context, 외부 시스템
- 같은 트랜잭션 안에서 처리해야 하는지, eventual consistency로 처리해도 되는지
- transaction commit 전/후 dispatch timing
- outbox가 필요한지
- 내부 domain event인지, cross-context integration event인지

외부 메시지나 다른 bounded context로 공개되는 event는 Published Language와 하위 호환성을 함께 고려한다.

## 6. Application Service와 Domain Service

Application service는 유스케이스 흐름을 조정한다.

- 입력을 받는다.
- repository나 ORM을 통해 필요한 객체를 가져온다.
- 도메인 객체의 행위를 호출한다.
- 트랜잭션 경계를 관리한다.
- 결과를 반환한다.

Application service는 핵심 비즈니스 판단을 소유하지 않는다. 규칙은 가능한 한 entity, value object, aggregate method, domain service에 둔다.

Domain service는 특정 entity나 value object에 자연스럽게 속하지 않는 도메인 규칙이 있을 때만 만든다.

## 7. Django ORM 매핑

Django model을 도메인 객체로 사용할 수 있는 경우:

- 불변식이 단순하다.
- Django model method로 도메인 행위를 명확히 표현할 수 있다.
- ORM 세부사항이 도메인 규칙을 흐리지 않는다.
- 테스트가 느리거나 깨지기 쉬워지지 않는다.

도메인 모델과 ORM 모델을 분리할 수 있는 경우:

- 도메인 규칙이 복잡하다.
- ORM lifecycle, lazy loading, QuerySet, field type이 도메인 사고를 방해한다.
- 외부 시스템, DB transaction, API schema가 도메인 객체에 섞인다.
- 순수 단위 테스트로 도메인 규칙을 빠르게 검증해야 한다.

분리는 기본값이 아니다. 복잡도와 이득이 분명할 때 선택한다.

## 8. Repository와 Transaction

Repository는 도메인 관점의 컬렉션처럼 동작해야 한다. 단순 QuerySet wrapper를 만들기 위해 repository를 만들지 않는다.

트랜잭션은 유스케이스의 일관성 경계다. Django에서는 `transaction.atomic()`을 기본 도구로 사용하되, 외부 side effect는 transaction commit 이후로 미룬다.

동시성 위험이 있으면 optimistic locking, pessimistic locking, unique constraint, idempotency key 중 무엇이 문제에 맞는지 판단한다.

위험한 쓰기 작업은 다음 consistency block을 남긴다.

- transaction owner
- locking 전략
- uniqueness 또는 idempotency 저장 위치
- `Idempotency-Key` API 동작
- 외부 side effect를 `transaction.on_commit()` 또는 domain event 이후로 미루는 방식
- isolation level과 retry 필요 여부
- 통합 테스트 또는 동시성 테스트 기준

## 9. API 매핑

REST API는 유스케이스의 외부 계약이다.

Django Ninja Router는 얇은 adapter로 유지한다.

- request schema 검증
- auth/permission 연결
- usecase 호출
- domain/application error를 Problem Details로 변환
- response schema 반환
- OpenAPI schema 영향 확인

Router에 비즈니스 규칙, 상태 전이, 복잡한 ORM 쿼리, 외부 SDK 호출을 직접 두지 않는다.

## 10. Python 매핑

Python 구현은 도메인 계약을 명시적으로 표현해야 한다.

- 공개 함수와 method에는 입력/출력 타입을 명시한다.
- `Optional[T]`보다 `T | None`을 기본으로 사용한다.
- 컬렉션은 `list[Order]`, `dict[str, int]`처럼 내부 타입을 드러낸다.
- 유한 상태는 `Enum` 또는 `StrEnum`을 우선 고려한다.
- 값 객체는 필요할 때 `frozen=True`, `slots=True` dataclass로 표현한다.
- `Protocol`은 교체 가능한 boundary에서만 사용한다.
- pydantic v2는 외부 DTO, config, runtime validation에 사용하고 도메인 모델의 기본값으로 강제하지 않는다.

## 11. 테스트 매핑

도메인 규칙은 빠른 단위 테스트로 검증한다.

Application service는 repository fake나 필요한 test double을 사용해 유스케이스 흐름을 검증한다.

Django ORM, transaction, constraint, query 성능은 통합 테스트로 검증한다.

Django Ninja API는 TestClient로 request/response contract, status code, Problem Details, auth, pagination을 검증한다.

Mock은 외부 시스템과 관찰해야 하는 협력에 사용한다. 도메인 객체 간 협력은 가능한 한 실제 객체와 상태 검증을 우선한다.
