---
name: architecture-ddd
description: >
  Use for DDD/domain modeling: bounded contexts, context maps, ubiquitous
  language, aggregates, entities, value objects, repositories, domain services,
  domain events, business rules, and service responsibility splits. For
  hexagonal/clean/CQRS/event sourcing use architecture-implementation-patterns;
  for schema design use architecture-db; for REST API design use
  architecture-api; for Django/Ninja implementation use implementation-django
  and implementation-django-ninja. If a Django request mentions subagents or
  역할 분해, use workflow-dddjango-subagents first.
---

# DDD 원칙과 패턴

이 스킬은 도메인 주도 설계의 전략적 및 전술적 패턴을 다룬다.
아키텍처 패턴(헥사고날, 클린, CQRS, 이벤트 소싱)에 대해서는
architecture-implementation-patterns에 위임한다. 데이터베이스 스키마 설계
(정규화, 인덱스, 트랜잭션)에 대해서는 architecture-db에 위임한다. REST API
설계 원칙(엔드포인트, 상태 코드, 버저닝)에 대해서는 architecture-api에 위임한다.
Python 컨벤션(타입 힌트, 데이터클래스)에 대해서는 implementation-python에 위임한다.
Django 코어(모델, ORM, 설정)에 대해서는 implementation-django에 위임한다.
Django Ninja API(Schema, Router)에 대해서는 implementation-django-ninja에 위임한다.
클린 코드 원칙(SOLID, 네이밍)에 대해서는 implementation-cleancode에 위임한다.

**Subagent workflow guard.** 사용자가 서브에이전트, subagent/subagents,
역할 분해, 병렬 검토, 책임 분배, dddjango workflow를 요청하면 이 스킬 단독의
일반 설계 답변으로 끝내지 않는다. `workflow-dddjango-subagents`를 적용하고
`Role Map`, `Sequential Fallback`, `Handoff Contract`, `Integration Checklist`
섹션명을 영어 그대로 포함한다. `역할 분해`로 번역하지 않는다.

**기본 요구사항 — 모든 모드에 적용:**
- 전략적 설계(바운디드 컨텍스트, 컨텍스트 맵)는 항상 전술적 패턴보다 먼저 수행한다.
  잘못된 경계 안에서 좋은 전술적 패턴을 적용해도 복잡성은 해결되지 않는다.
- 모델은 유비쿼터스 언어를 반영해야 한다 — 클래스명과 메서드명이 도메인 전문가
  용어와 일치해야 한다.
- 애그리거트는 작게 유지한다 — 이상적으로 애그리거트당 엔티티 하나.
- 주문/결제 같은 애그리거트 경계 검토에서는 `작은 애그리거트`, `ID`,
  `도메인 이벤트`, `최종 일관성` literal을 포함한다. 서로 다른 생명주기와
  트랜잭션 경계를 가진 객체는 하나의 거대한 애그리거트로 묶지 않고, ID 참조와
  도메인 이벤트로 연결한다.

**Django feature skeleton.** Django Ninja 기능을 DDD 기준으로 설계하거나
구현할 때는 기존 프로젝트 구조가 없다는 전제에서 다음 기본 파일 경계를
제시한다. 기존 프로젝트가 이미 다른 구조를 쓰면 그 구조를 우선하고, 같은
책임 경계를 유지한다.

```text
apps/orders/
  domain/
    models.py        # Aggregate, Entity, Value Object, invariant
    exceptions.py    # domain exception
    events.py        # domain event
  services.py        # application service 또는 use case
  api/
    schemas.py       # Django Ninja Schema/ModelSchema
    router.py        # Router, response={...}
  tests/
    test_order_create.py
```

도메인 로직은 router/view에 두지 않는다. router는 Schema 검증과 use case 호출,
HTTP status-code response mapping만 담당한다. 성공/실패가 갈리는 정책은
bool, dict error, 문자열 코드만 반환하지 말고 `Result` 타입, 도메인 예외,
값 객체, 불변식으로 표현한다.
Django Ninja router 코드 예시를 함께 제시할 때는 `@router.post` 함수 안에
`for ... items`, `if ... status`, `inventory`, `discount`, `cancel` 같은
비즈니스 흐름을 넣지 않는다. 요청 변환은 `payload.to_command()` 같은 얇은
메서드로 감추고, 반복/분기/재고/할인/상태 전이 판단은 `services.py` 또는
domain 계층에 둔다. 주문 생성의 DB 일관성 설명에는 `transaction.atomic()`과
`select_for_update()` 또는 `version` 기반 locking을 함께 언급한다.
파일 트리/코드 골격 요청에서는 응답 구조보다 이 override가 우선한다. 첫
파일 트리 블록은 위 canonical layout을 기준으로 시작한다. 확장 구조를
추가하더라도 이 블록보다 먼저 `domain_layer`, `application_layer`,
`presentation_layer` 같은 대체 계층 구조를 제시하지 않는다.
파일 트리에는 확장 구조를 쓰더라도 `services.py`라는 파일명을 반드시 포함한다.
TDD 또는 구현 골격이 포함되면 먼저 `RED -> GREEN -> REFACTOR` 한 줄을 쓰고,
섹션 제목에 정확히 `RED`, `GREEN`, `REFACTOR`를 사용한다. 실패 테스트 -> 최소
구현 -> 리팩터링 순서를 지킨다.
사용자가 "파일 트리", "코드 골격", "domain, service/usecase, api schema/router,
tests 경계"를 요청하면 첫 파일 트리 블록에 반드시 `services.py`와
`api/schemas.py`를 literal로 포함하고, 코드 골격 전에 `RED -> GREEN ->
REFACTOR` 섹션을 둔다.

**도메인 코드 품질 / 에러 모델.** 사용자가 할인 쿠폰, 주문 정책 같은 도메인
로직을 코드 품질 중심으로 설계하면서 dict 에러나 bool 대신 Result/도메인
예외/값 객체/pytest를 요청하면, 답변은 `RED -> GREEN -> REFACTOR` 순서로
시작한다. 성공/업무상 거절은 타입이 드러나는 `Result`(`Ok`/`Err` 또는
명시적 dataclass union)로, 깨진 불변식은 `도메인 예외`로, 원시 문자열/숫자는
`값 객체`로 표현한다. 설명과 코드에서 literal JSON error payload를 쓰지
않는다. 특히 `{"error"` 형태의 문자열을 예시로도 출력하지 않는다. 금지
대안은 "dict error payload", "untyped error mapping"처럼 풀어 쓴다.
clean code 설명에는 `책임`, `함수`, `타입`, `분리`, `테스트`를 포함하고,
각 함수가 하나의 책임만 갖는 이유를 짧게 붙인다.

**주문 상태 전이 설계.** 결제 완료, 배송 시작, 취소 실패 조건이 있는 주문
상태 전이를 DDD 기준으로 설계할 때는 `Order` 애그리거트, `OrderId`,
`PaymentId`, `Money`, `CancellationReason` 값 객체, `TransitionOrderStatusResult`
Result 타입, `OrderDomainError` 도메인 예외, `PaymentConfirmed`,
`ShippingStarted`, `OrderCancellationFailed` 도메인 이벤트를 함께 제시한다.
답변에는 `값 객체`, `도메인 이벤트`, `타입`이라는 literal 표현을 섹션이나
표 설명에 포함한다.
상태 변경은 `confirm_payment()`, `start_shipping()`, `cancel()` 함수로 분리하고
각 함수의 책임을 설명한다. DB 일관성 섹션에는 `transaction.atomic()`,
`select_for_update()`, `version` 기반 optimistic locking, 상태 전이 중복
방지를 위한 `idempotency` key, `unique` constraint를 포함한다. 이 섹션은
검증 방법까지 포함해야 하며, 실제로 실행하지 않았다면 실행 결과를 확인한 것처럼 쓰지 않는다.

아래 섹션에서 다루는 주제를 작업할 때는 링크된 참조 파일을 읽고 상세한
컨벤션과 코드 예시를 확인한다.

**참조 로딩 규칙:**
- 설계 모드: 설계를 제안하기 전에 관련 참조를 먼저 읽는다.
- 리뷰 모드: 리뷰 결과를 확정하기 전에 인용된 모든 원칙의 참조를 읽는다.
- 리팩터링 모드: 변경 사항을 제시하기 전에 적용된 각 패턴의 참조를 읽는다.

## 응답 구조

모든 응답은 다음 구조를 따른다:

1. **[주요 내용]** -- 모드에 따른 코드, 리뷰, 리팩터링 결과
2. **[관련 스킬 참조]** -- 사용자의 다음 단계를 안내하는 연결점

이 스킬은 11개의 상호 연결된 스킬 체계의 일부이다.
사용자는 현재 작업 후 어떤 스킬을 호출해야 하는지 모르는 경우가
많으므로, 관련 스킬 참조가 워크플로우의 자연스러운 연결을 만든다.

ALWAYS use this exact template for the closing section:
```
---
> **관련 스킬 참조:**
> - [topic] → **[skill-name]** 스킬
```

## 운영 모드

사용자의 요청에 따라 모드를 선택한다:
- **설계**: 도메인 모델, 바운디드 컨텍스트, 애그리거트를 처음부터 설계
- **리뷰**: 기존 도메인 모델/설계의 DDD 위반 사항 평가
- **리팩터링**: 기존 설계를 DDD 원칙에 맞게 개선

의도가 모호한 경우 설계 모드를 기본으로 한다.

### 설계 모드

도메인 모델을 설계할 때 다음 순서를 따른다:

1. **전략적 설계부터 시작한다.** 바운디드 컨텍스트 경계를 먼저 정의한다.
   전술적 패턴(엔티티, 값 객체, 애그리거트)은 그 다음이다. 이 순서가 중요한
   이유는 잘못된 경계 안에서 좋은 전술적 패턴을 적용해도 복잡성 관리에 실패하기
   때문이다.

2. **유비쿼터스 언어를 코드에 반영한다.** 클래스명과 메서드명이 도메인 전문가
   용어와 일치해야 한다. `updateStatus()` 대신 `confirm()`, `cancel()`,
   `ship()`을 사용한다 — 이름이 비즈니스 의도를 드러내야 한다.

3. **애그리거트 설계 규칙을 적용한다.** Vernon의 4가지 규칙을 따른다: 진정한
   불변식을 일관성 경계로 보호하고, 작은 애그리거트를 설계하고, 다른 애그리거트는
   ID로만 참조하고, 경계 간 업데이트에는 최종 일관성을 사용한다.

4. **풍부한 도메인 모델을 지향한다.** 빈약한 도메인 모델(getter/setter만 있는
   엔티티, 모든 로직이 서비스에 존재)은 안티패턴이다. 비즈니스 로직은 엔티티와
   값 객체 내부에 속한다.

### 리뷰 모드

잘 구성된 설계를 리뷰할 때는 개선 사항을 나열하기 전에 설계가 잘된 부분을
먼저 인정한다. 부실한 설계를 리뷰할 때는 가장 영향이 큰 문제부터 집중한다.

각 발견 사항은 다음 형식으로 작성한다:

```
[원칙] -- 이 설계가 해당 원칙을 위반하는 이유 설명
```

리뷰를 확정하기 전에 이 체크리스트의 모든 항목을 검증한다:

- [ ] 바운디드 컨텍스트 경계가 명확한가 (같은 용어가 다른 의미로 사용되지 않는가)
- [ ] 애그리거트가 너무 크지 않은가 (하나의 트랜잭션에서 여러 엔티티를 수정하지 않는가)
- [ ] 애그리거트가 직접 객체 참조가 아닌 ID로 서로를 참조하는가
- [ ] 빈약한 도메인 모델이 아닌가 (비즈니스 로직이 서비스에 분산되어 있지 않는가)
- [ ] 값 객체여야 할 개념이 엔티티로 모델링되어 있지 않은가
- [ ] 애그리거트 간 통신이 직접 호출이 아닌 도메인 이벤트를 사용하는가
- [ ] 유비쿼터스 언어가 코드에 반영되어 있는가
- [ ] 서브도메인 유형(핵심/지원/범용)에 적절한 복잡도 수준이 적용되어 있는가

### 리팩터링 모드

리팩터링 시 변경 전/후를 보여주고 각 변경의 이유를 명시한다. 각 변경을
특정 DDD 원칙에 연결하여 근거를 추적할 수 있게 한다. 각 변경은 다음 형식으로
작성한다:

```
[Before]
<원래 설계/코드>

[After]
<개선된 설계/코드>

[Reason] 원칙 -- 이 변경이 DDD에 부합하는 이유 설명
```

변경 사항을 제시하기 전에 아래의 적용 가능한 모든 개선을 적용한다:

- [ ] 빈약한 도메인 모델 -> 비즈니스 로직을 엔티티/값 객체로 이동
- [ ] 큰 애그리거트 -> 작은 애그리거트로 분할 + 도메인 이벤트로 연결
- [ ] 직접 참조 -> ID 참조로 교체
- [ ] 원시 타입 -> 값 객체로 추출
- [ ] 서비스의 비즈니스 로직 -> 엔티티/값 객체 메서드로 이동
- [ ] 동기 호출 -> 도메인 이벤트 + 최종 일관성으로 교체
- [ ] 모호한 경계 -> 바운디드 컨텍스트로 분할

## 응답 작성 직전 체크리스트 (필수)

### 공통
- [ ] Aggregate Root 명시 + 불변식 docstring/코드 명시
- [ ] Value Object frozen=True dataclass + __post_init__ 검증
- [ ] Domain Event 과거형 명명 (PaidEvent, OrderConfirmedEvent)
- [ ] Ubiquitous Language 사전 표 + 금지 동의어 컬럼

### 설계 모드
- [ ] **Repository ABC 인터페이스를 도메인 계층에 정의 (`AuctionRepository(ABC)`, `find_by_id`/`save`)**
- [ ] **응용 서비스 분리 (`AuctionApplicationService`로 use case 조율, 도메인 레이어와 분리)**

### 리뷰 모드
- [ ] auction.save() 같은 영속성 호출이 도메인 모델 안에 있으면 Repository 분리 권고
- [ ] Vernon 4규칙 위반 명시(불변식 보호, 작은 Aggregate, 결과적 일관성, ID 참조)
- [ ] [원칙] -- 이유 형식
- [ ] **`raise Exception` 또는 일반 예외 발견 시 도메인 예외(`BidTooLowError`, `AuctionAlreadyClosedError`)로 교체 제안**

### 리팩토링 모드
- [ ] [Before] / [After] / [Reason] 형식 + DDD 원전 인용 (Evans, Vernon)
- [ ] 도메인 이벤트 발행 + 수집 메커니즘 코드 (_record_event/collect_events)
- [ ] **`ValueError`를 도메인 예외 클래스로 교체 (모듈 루트 도메인 예외 정의 후 사용)**

---

## 1. DDD 개요

핵심 요약, 전략적 설계 우선 원칙, 주요 참조 문헌의 관점. 전략적 설계가
전술적 패턴보다 선행한다는 원칙은 모든 DDD 적용의 출발점이다.

> Reference: `references/overview.md`

## 2. 지식 탐구와 유비쿼터스 언어

지식 탐구(Knowledge Crunching)는 도메인 전문가와의 반복적인 대화를 통해
모델을 정제하는 반복적 프로세스이다. 유비쿼터스 언어는 그 산출물이며 코드의
모든 이름에 반영되어야 한다.

> Reference: `references/knowledge-crunching.md`

## 3. 도메인, 서브도메인, 디스틸레이션

도메인을 핵심(Core), 지원(Supporting), 범용(Generic) 서브도메인으로 분류하여
투자 우선순위를 결정한다. 최고의 인재와 정교한 설계를 핵심 도메인에 집중하고,
범용 도메인에는 기존 솔루션을 활용한다.

> Reference: `references/subdomains.md`

## 4. 바운디드 컨텍스트와 컨텍스트 맵

같은 용어가 다른 의미로 사용되는 지점이 바운디드 컨텍스트의 경계이다. 컨텍스트
맵은 컨텍스트 간 관계(파트너십, 고객-공급자, ACL 등)를 정의한다. 부패 방지
계층(ACL)은 외부 모델 오염을 차단하는 핵심 패턴이다.

> Reference: `references/bounded-context.md`

## 5. 이벤트 스토밍과 팀 토폴로지

이벤트 스토밍은 도메인 이벤트를 중심으로 비즈니스 프로세스를 시각화하는 워크숍
기법이다. 바운디드 컨텍스트 경계를 팀 경계와 일치시켜 콘웨이 법칙을 역으로
활용한다.

> Reference: `references/event-storming.md`

## 6. 값 객체와 엔티티

값 객체는 속성 조합으로 식별되며 불변이다. 엔티티는 고유 식별자로 식별되며
생명주기를 가진다. 가능한 한 값 객체를 선호한다 — 불변성이 부수 효과를
제거한다.

> Reference: `references/value-objects-entities.md`

## 7. 애그리거트

애그리거트는 DDD의 핵심 전술적 패턴이다. Vernon의 4가지 규칙:
1) 진정한 불변식을 일관성 경계로 보호
2) 작은 애그리거트 설계
3) 다른 애그리거트는 ID로만 참조
4) 경계 간 업데이트에는 최종 일관성 사용

> Reference: `references/aggregates.md`

## 8. 리포지토리, 도메인 서비스, 애플리케이션 서비스

리포지토리는 애그리거트당 하나씩 제공된다. 도메인 서비스는 특정 엔티티에
속하지 않는 도메인 로직을 담는다. 애플리케이션 서비스는 유스케이스를 오케스트레이션
하며 도메인 로직을 포함해서는 안 된다.

> Reference: `references/repositories-services.md`

## 9. 도메인 이벤트와 스펙

도메인 이벤트는 "과거에 발생한 사실"을 표현하며, 애그리거트 간 최종 일관성을
구현하는 핵심 메커니즘이다. 스펙(Specification) 패턴은 복잡한 비즈니스 규칙을
조합 가능한 객체로 캡슐화한다.

> Reference: `references/domain-events.md`

## 10. 유연한 설계

Evans의 6가지 유연한 설계 패턴: 의도를 드러내는 인터페이스, 부수 효과 없는
함수, 단언(assertion), 개념적 윤곽, 독립형 클래스, 연산의 닫힘. 이 패턴들은
모델이 성숙할수록 더 큰 가치를 발휘한다.

> Reference: `references/supple-design.md`

## 11. DDD와 아키텍처

DDD는 특정 아키텍처를 강제하지 않지만 헥사고날/클린/레이어드 아키텍처와 자연스럽게
결합된다. 상세한 아키텍처 패턴 선택과 구현은 architecture-implementation-patterns에
위임한다.

> Reference: `references/architecture.md`

## 12. 구현 패턴

패키지 구조, 복잡도 스케일링(Transaction Script -> Active Record ->
Domain Model), 마이크로서비스 통합 패턴. Repository + UoW, Data Mapper,
Event Sourcing의 상세 구현은 architecture-implementation-patterns를 참조한다.

> Reference: `references/implementation.md`

## 13. 결정 가이드

서브도메인 유형별 복잡도 관리 원칙, 핵심 결정 요약 테이블, DDD 핵심 개념의
최종 통합.

> Reference: `references/decision-guide.md`

## 14. DDD + Django 프로젝트 구조

Django 프로젝트에 DDD를 적용하기 위한 권장 폴더 구조. 도메인 객체를
애그리거트별로 그룹화하고, Django 앱을 인프라 계층에 격리하여 도메인 모델이
프레임워크에 의존하지 않도록 한다. Django 프로젝트의 폴더 구조를 설계하거나
리뷰할 때 이 참조를 읽는다.

> Reference: `references/filetree-with-django.md`
