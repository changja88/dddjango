# 구현 아키텍처 패턴 source reference

> 이 문서는 `architecture-implementation-patterns` skill의 전용 source reference다. DDD 모델이 어느 정도 확인된 뒤 구현 구조, 의존성 방향, 포트/어댑터, repository, Unit of Work, CQRS, event sourcing, saga, outbox, ACL, service layer 선택을 판단하는 기준을 제공한다.
>
> 근거 역할:
> - `workspace/reference/architecture-ddd/reference/final.md`: 전략 설계 우선, 계층 아키텍처, DIP, aggregate 단위 repository, application service, domain event, outbox, ACL, CQRS 선택 적용 기준.
> - `workspace/reference/implementation-django/reference/final.md`: Django 모델 메서드, 서비스/셀렉터, Fat Model 완화, Repository 도입 비용, Django 배터리 보존 기준.
> - `workspace/reference/implementation-python/reference/final.md`: Python `Protocol` 등 구조적 경계와 타입 기반 협력 표현.

---

## 1. 적용 순서

구현 아키텍처 패턴은 도메인 전략을 대신하지 않는다. 다음 순서로 판단한다.

1. 바운디드 컨텍스트, aggregate, invariant, use case, 외부 통합 경계를 확인한다.
2. 실제 압력을 분류한다: framework leakage, persistence mapping, transaction boundary, read/write model divergence, external side effect reliability, legacy/upstream language conflict, test seam, replacement need.
3. 현재 압력을 해결하는 가장 가벼운 패턴을 선택한다.
4. 선택하지 않은 무거운 패턴과 그 이유를 함께 적는다.
5. DB locking/isolation, REST idempotency, Django 구체 구현, pytest/concurrency 검증은 owning skill로 넘긴다.

단순 CRUD, 작은 필드 변경, 지원 하위 도메인의 직선적 흐름에는 repository, custom Unit of Work, CQRS, event sourcing, saga, outbox, ACL을 기본으로 도입하지 않는다.

---

## 2. 기본 구조 선택

### 2.1 Layered architecture

기본 방향은 표현 또는 인터페이스 계층에서 application 계층을 호출하고, application 계층이 domain 정책을 조율하며, infrastructure가 외부 세부사항을 구현하는 흐름이다.

허용되는 책임:

| 계층 | 책임 | 금지 |
|---|---|---|
| presentation/interface | HTTP, CLI, admin, task, message 입력 변환, 인증/인가 연결, response mapping | 핵심 상태 전이와 aggregate invariant 소유 |
| application | use case orchestration, transaction boundary, repository/port 호출, DTO 변환 | framework request/response 타입에 직접 의존 |
| domain | entity, value object, aggregate, domain service, invariant, domain event | ORM, SDK, HTTP, filesystem, environment 세부사항 |
| infrastructure | ORM, SDK, broker, cache, filesystem, external API adapter 구현 | domain language를 외부 모델에 종속 |

### 2.2 Clean architecture / hexagonal architecture

Clean 또는 hexagonal 구조는 핵심 정책이 framework, ORM, 외부 SDK, message broker에 의해 흔들릴 때 선택한다. 핵심 규칙은 의존성이 안쪽 정책으로 향하는 것이다. Port는 application/domain이 필요로 하는 역할이며 adapter는 framework 또는 외부 세부사항을 번역한다.

선택 조건:

- 외부 service, broker, 결제/재고/권한 provider, legacy system이 domain model을 오염시킬 위험이 있다.
- persistence shape과 domain language가 다르다.
- use case를 framework 없이 테스트해야 하는 가치가 크다.
- 교체 가능성이 실제 요구이거나 장애 격리, 계약 안정성이 중요하다.

회피 조건:

- Django conventions가 흐름을 더 명확하게 만든다.
- port가 기술명만 감춘 얇은 wrapper다.
- 구현이 하나뿐이고 바뀔 가능성도 낮으며 테스트 seam도 필요하지 않다.

---

## 3. Dependency direction과 port 설계

의존성 방향은 정책 쪽으로 향해야 한다. domain/application은 ORM, SDK, HTTP client, settings, filesystem 같은 외부 세부사항을 직접 알지 않는다.

Port 작성 기준:

- port 이름은 기술이 아니라 역할을 표현한다. 예: `PaymentGateway`, `InventoryReservationPort`.
- port method는 좁고 use case 언어를 따른다.
- 입출력은 domain/application DTO, value object, 식별자를 사용한다.
- Python에서는 구조적 협력이 필요하면 `Protocol`을 우선 고려하고, 명시적 상속이나 runtime registration이 필요할 때 ABC를 고려한다.
- 모든 class에 interface를 만들지 않는다.

Adapter 배치 기준:

- Django view, Ninja router, DRF view/serializer, template view, form, management command, Celery task, message handler는 interface adapter다.
- ORM repository, external SDK client, broker publisher, cache/filesystem 구현은 infrastructure adapter다.
- adapter는 input validation, auth 연결, DTO 변환, use case 호출, response mapping을 담당할 수 있지만 핵심 policy를 소유하지 않는다.

---

## 4. Repository와 Unit of Work

### 4.1 Repository

Repository는 aggregate collection처럼 저장과 조회를 표현할 때 도입한다. aggregate root 단위로 설계하며 child entity마다 repository를 기본 생성하지 않는다.

선택 조건:

- domain/application이 Django ORM 또는 QuerySet 세부사항을 몰라야 한다.
- aggregate persistence mapping이 복잡하거나 ORM model과 domain model을 분리한다.
- application service 테스트에서 fake repository의 가치가 크다.
- 외부 persistence 또는 data mapper 교체가 현실적 요구다.

회피 조건:

- `Model.objects.filter(...)`를 이름만 바꿔 감싸는 thin wrapper다.
- QuerySet composition, `select_related`, `prefetch_related`, annotation이 핵심 장점이다.
- Django model method와 service/selector가 더 명확하다.
- 단순 CRUD 또는 supporting workflow다.

### 4.2 Unit of Work

Unit of Work는 하나의 use case transaction boundary를 명시하고 여러 repository 또는 adapter 협력을 한 번에 commit/rollback해야 할 때 도입한다.

Django에서는 `transaction.atomic()`이 실용적 Unit of Work 역할을 할 수 있다. custom UoW abstraction은 use case boundary, fake persistence, framework 독립성이 실제 이득을 줄 때만 만든다.

외부 side effect는 rollback mismatch를 만들 수 있으므로 DB transaction 내부에서 직접 실행하지 않는다. 단순 후속 작업은 `transaction.on_commit()`을 고려하고, cross-service message delivery의 신뢰성이 중요하면 durable outbox를 고려한다.

---

## 5. Service layer

Service layer는 view/router와 model/domain 사이에서 use case를 조율하는 application layer다. 핵심 business policy를 직접 소유하기보다 aggregate, value object, domain service에 위임하고 transaction, repository, external port 호출 순서를 관리한다.

Django 기본 경로:

- model method: 한 model 또는 aggregate 내부 상태 전이와 invariant를 캡슐화한다.
- service function: 여러 model, 외부 service, transaction을 조율하는 write/use case를 담당한다.
- selector function: read/query logic, QuerySet optimization, filtering, sorting을 담당한다.

서비스 레이어 도입 신호:

- 하나의 business action이 여러 model을 조율한다.
- view/router에 business policy와 transaction이 섞인다.
- 같은 write workflow가 여러 entrypoint에서 반복된다.
- external service 호출이 model 또는 view에 직접 섞인다.

주의:

- service가 domain rule을 모두 흡수해 빈약한 domain model을 만들지 않는다.
- 단순 model method로 충분한 invariant를 service로 빼지 않는다.

---

## 6. CQRS, Event Sourcing, Saga

### 6.1 CQRS

CQRS는 command model과 query model의 요구가 실제로 다를 때 일부 bounded context 또는 use case에 선택 적용하는 보조 패턴이다. 최상위 architecture로 기본 선택하지 않는다.

선택 조건:

- write invariant와 read projection/aggregation이 서로 다른 모델을 요구한다.
- read side 성능, denormalized projection, reporting model이 command model을 왜곡한다.
- command 처리와 query 최적화의 변경 이유가 분리되어 있다.

회피 조건:

- selector 또는 QuerySet 최적화로 충분하다.
- read/write 분리가 단순 CRUD를 더 어렵게만 만든다.
- eventual consistency를 감당할 제품/운영 기준이 없다.

### 6.2 Event sourcing

Event sourcing은 현재 상태보다 event history, audit, replay, temporal reconstruction이 domain의 핵심일 때만 선택한다. domain event를 사용한다고 event sourcing이 필요한 것은 아니다.

선택 조건:

- 상태의 근거와 변경 이력이 법적, 회계적, 운영적으로 핵심이다.
- 과거 시점 재구성, replay, compensation analysis가 주요 요구다.
- event schema evolution과 projection rebuild 운영을 감당할 수 있다.

회피 조건:

- 단순 audit log 또는 integration notification만 필요하다.
- team이 event versioning, projection, replay 운영 복잡도를 감당할 준비가 없다.

### 6.3 Saga

Saga는 하나의 local transaction으로 보호할 수 없는 long-running 또는 distributed business process에 사용한다. 각 step은 local transaction이며 실패 시 compensation이 명시되어야 한다.

선택 조건:

- 여러 service/context에 걸쳐 순차 단계와 보상 단계가 있다.
- 하나의 DB transaction으로 묶을 수 없고, eventual consistency를 제품이 수용한다.
- compensation action이 idempotent하게 설계될 수 있다.

회피 조건:

- 하나의 local invariant를 transaction으로 보호할 수 있다.
- 단순 background job이나 retry만으로 충분하다.

---

## 7. Domain event, integration event, outbox

Domain event는 aggregate 내부 또는 같은 bounded context에서 발생한 business fact다. Integration event는 context/service 경계를 넘어가는 published language이며 내부 aggregate 구조를 그대로 노출하지 않는다.

Outbox는 state change와 message publication을 같은 DB transaction에 기록하고, 별도 dispatcher가 message broker 또는 외부 channel로 발행하는 패턴이다.

Outbox 선택 조건:

- DB commit 이후 external message delivery가 유실되면 안 된다.
- at-least-once delivery와 consumer idempotency를 설계할 수 있다.
- retry, dead-letter, dispatch ownership이 필요하다.

회피 조건:

- 외부 side effect가 없다.
- 단순 in-process follow-up이며 `transaction.on_commit()`으로 충분하다.
- 유실 가능성을 제품이 수용하거나 별도 운영 부담이 과하다.

Outbox 판단 시 명시할 항목:

- aggregate와 outbox message를 쓰는 transaction owner
- dispatcher owner
- delivery guarantee
- consumer idempotency 기준
- retry/dead-letter 정책의 owning skill 또는 후속 작업
- published language field

---

## 8. Anticorruption Layer

ACL은 upstream 또는 legacy model이 downstream bounded context language와 충돌할 때 translation boundary로 둔다. 데이터 shape뿐 아니라 status, unit, identifier, lifecycle semantics를 번역한다.

선택 조건:

- 외부/legacy 용어가 aggregate, value object, ubiquitous language로 누수될 위험이 있다.
- upstream lifecycle과 downstream lifecycle이 다르다.
- public integration contract와 내부 model의 의미가 다르다.

회피 조건:

- 외부 모델이 이미 bounded context language와 일치한다.
- 단순 field rename 수준이며 별도 semantic translation이 없다.

ACL은 boundary 근처에 둔다. 여러 domain object 내부에 산발적으로 translation logic을 넣지 않는다. 공개 API의 published language와 versioning이 관련되면 `architecture-api`로 넘긴다.

---

## 9. Risky Write Consistency Block

결제, 재고, 예약, 환불, 권한, ledger처럼 실패 비용이 큰 write에서는 pattern-level 판단을 명시한다. 이 skill은 어떤 architecture pattern을 쓸지 결정하고, 세부 DB/API/test 구현은 owning skill로 넘긴다.

필수 항목:

| 항목 | 적을 내용 | owning handoff |
|---|---|---|
| transaction owner | 어느 use case 또는 service가 transaction boundary를 소유하는지 | `implementation-django`, `architecture-db` |
| pattern decision | Django-native transaction, service layer, port/adapter, outbox, saga, ACL, no extra pattern 중 선택 | 이 skill |
| side-effect timing | transaction 내부 금지 여부, after commit, outbox, saga step 등 | 이 skill, `implementation-django` |
| uniqueness/idempotency storage | 저장 필요 여부만 판단 | `architecture-db`, `architecture-api` |
| DB concurrency | locking, isolation, retry 상세 | `architecture-db` |
| API behavior | `Idempotency-Key`, status code, Problem Details | `architecture-api` |
| tests | integration, replay, concurrency, idempotency test | `implementation-test` |

---

## 10. Handoff 기준

| 상황 | 우선 skill |
|---|---|
| bounded context, aggregate, invariant가 불명확함 | `architecture-ddd` |
| schema, constraint, index, locking, isolation, migration rollout가 핵심임 | `architecture-db` |
| REST resource, method/status, Problem Details, idempotency header가 핵심임 | `architecture-api` |
| Django model/service/selector/migration 구현이 핵심임 | `implementation-django` |
| Django Ninja router/schema/API 구현이 핵심임 | `implementation-django-ninja` |
| Python typing, `Protocol`, exception, dataclass 구현 품질이 핵심임 | `implementation-python` |
| pytest, fake/mock, concurrency/idempotency test 구현이 핵심임 | `implementation-test` |
| 여러 role이 결합된 위험 작업 또는 subagent workflow가 필요함 | `workflow-dddjango-subagents` |

---

## 11. 금지와 honesty 기준

- 전략 설계가 불명확한데 repository, CQRS, outbox 같은 전술 패턴을 먼저 확정하지 않는다.
- Django 장점을 모두 버리는 순수 domain 분리를 기본값으로 강제하지 않는다.
- fallback 또는 provisional source라고 말하지 않는다. 이 문서가 dedicated source reference다.
- 실제로 실행하지 않은 validator, eval, test, subagent, browser check, Serena 사용을 실행했다고 쓰지 않는다.
- source reference가 정한 범위보다 강한 claim을 runtime skill이나 eval answer에 요구하지 않는다.
