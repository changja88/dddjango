---
name: architecture-implementation-patterns
description: >
  Use when the user asks to apply hexagonal, clean, onion, layered
  architecture, ports/adapters, CQRS, event sourcing, repository, unit
  of work, data mapper, outbox, dependency injection, DIP, anti-corruption
  layer, or legacy migration. Korean triggers include 헥사고날 적용, 프로젝트
  구조, 레이어 분리, 의존성 역전, CQRS, 이벤트 소싱. Use for pattern
  selection, dependency direction, infrastructure abstraction, and repository
  interface ownership. If order/payment/ecommerce domain nouns appear with
  architecture, also use architecture-ddd. For Django specifics use
  implementation-django; for DB use architecture-db; for REST API use
  architecture-api. For ambiguous service layer or project structure questions,
  say the context is unclear or that the answer assumes Django before applying
  Django/dddjango guidance.
---

# 아키텍처 구현 패턴

이 스킬은 코드 의존성 구조화, 인프라 추상화, 바운디드 컨텍스트 통합을 위한
아키텍처 패턴을 다룬다. 도메인 모델링과 전략적/전술적 DDD 패턴에 대해서는
architecture-ddd에 위임한다. 데이터베이스 스키마 설계(정규화, 인덱스)에 대해서는
architecture-db에 위임한다. REST API 설계 원칙(엔드포인트, 버저닝)에 대해서는
architecture-api에 위임한다. Python 컨벤션(타입 힌트, 데이터클래스)에 대해서는
implementation-python에 위임한다. Django 코어(모델, ORM, 설정)에 대해서는
implementation-django에 위임한다. Django Ninja API(Schema, Router)에 대해서는
implementation-django-ninja에 위임한다. 클린 코드 원칙(SOLID, 네이밍)에
대해서는 implementation-cleancode에 위임한다.

**기본 요구사항 — 모든 모드에 적용:**
- 의존성은 항상 안쪽을 향한다: 도메인은 인프라에 의존해서는 안 된다.
- 추상화(인터페이스)는 구현하는 계층이 아니라 사용하는 계층이 소유한다
  (소유권 역전).
- 현재 복잡도를 처리할 수 있는 가장 단순한 패턴을 선택한다. 단순한 CRUD에는
  레이어드 아키텍처로 충분하다; 모든 곳에 헥사고날을 강제하지 않는다.
- 서비스 레이어 위치, 프로젝트 구조, 레이어 분리처럼 프레임워크가 명확하지
  않은 질문은 첫 문장에 반드시 "맥락이 불명확하므로 ..." 또는
  "Django 프로젝트라는 가정하에 ..."를 포함한다. `serializers.py` 같은 DRF
  암시 파일명은 쓰지 않는다. Django API 예시가 필요하면 `api.py`,
  `schemas.py`, `services.py`, `selectors.py`를 사용한다.

아래 섹션에서 다루는 주제를 작업할 때는 링크된 참조 파일을 읽고 상세한
컨벤션과 코드 예시를 확인한다.

**참조 로딩 규칙:**
- 설계 모드: 아키텍처를 제안하기 전에 관련 참조를 먼저 읽는다.
- 리뷰 모드: 결과를 확정하기 전에 인용된 모든 패턴의 참조를 읽는다.
- 리팩터링 모드: 변경 사항을 제시하기 전에 적용된 각 패턴의 참조를 읽는다.

## 도메인 설계가 동반되는 작업 — 강제 위임 규칙

이 스킬의 패턴(Hexagonal, CQRS, Repository, ACL)은 도메인 모델이 비어 있으면
빈 껍데기다. 다음 신호가 보이면 응답 작성 전에 architecture-ddd 스킬을 반드시
활성화하고 해당 reference를 함께 읽는다 — 단독 처리하지 않는다.

| 사용자 요청 신호 | 같이 읽어야 할 architecture-ddd reference |
|---|---|
| "도메인 설계", "BC 분리", "도메인 모델", "유비쿼터스 언어" | `bounded-context.md`, `subdomains.md`, `knowledge-crunching.md` |
| "주문/결제/배송/재고/예약" 같은 도메인 명사 + 아키텍처 | `aggregates.md`, `domain-events.md`, `value-objects-entities.md` |
| 비즈니스 규칙·상태 전이·불변식 언급 | `aggregates.md`, `value-objects-entities.md` |
| 외부 시스템 통합 + 어휘 정화 (Stripe/Toss/ERP 등 SDK 어휘 침투) | `supple-design.md`, `knowledge-crunching.md` |
| 파일/디렉토리 트리 작성 | `filetree-with-django.md` (의미군 묶음 의무, `domain/model/<aggregate>/` 깊이) |

위 신호 없이 단순한 패턴 적용(레포지토리 추출, ACL 도입, UoW 도입)만 요청된
경우에는 단독 처리한다.

**왜 강제인가**: 단독 invoke 시 결과물이 다음 패턴으로 실패한다.
- "Order Aggregate"라고 부르지만 불변식이 없음 → 단순 데이터 클래스
- `total_amount: int`가 그대로 노출 → `Money` VO 부재로 통화 혼합 위험
- `payment_token`, `charge.id` 같은 외부 SDK 어휘가 도메인 필드명에 침투
- Domain Event 클래스만 정의되고 `_record_event`/`collect_events` 수집 메커니즘 부재
- 파일 트리가 평탄(`domain/model/`)해서 다중 Aggregate 시 확장 불가

## 응답 작성 직전 — DDD 전술 체크리스트 (필수)

위 위임 규칙에 따라 architecture-ddd refs를 읽었더라도, 구현 코드를 제시할 때
자주 빠지는 항목이 있다. 응답을 사용자에게 제시하기 전에 반드시
`references/ddd-tactical-checklist.md`의 11개 체크 항목을 한 번 훑고 누락된
부분을 보강한다.

핵심 11개:
1. Ubiquitous Language 사전 표가 응답에 포함됨 (금지 동의어 컬럼 포함)
2. `AggregateRoot` 추상 베이스 + `_record_event`/`collect_events` 코드가 있음
3. Aggregate 라이프사이클 메서드가 셋트로 완성됨 (예: reserve/release/commit)
4. Domain Event(internal)와 Integration Event(published_language)가 폴더로 분리됨
5. Saga가 Command만 발행하고 외부 I/O는 Handler에서 수행함
6. Outbox 제시 시 at-least-once + 컨슈머 멱등성 한 줄이 있음
7. 멱등성 패턴 3중 적용이 모든 비멱등 경로에 일관됨
8. `transaction.on_commit` vs Outbox 선택 기준이 명시됨
9. 파일 트리가 의미군 묶음 (`domain/model/<aggregate>/`)
10. **Money VO + 도메인 ID VO(OrderId, PaymentId) + OrderLine 같은 명세 VO가
    실제 frozen=True dataclass 클래스 코드로 정의됨** — 개념 언급만으로는 fail.
    Price에 currency 필드만 추가하는 것도 fail. Money는 별도 클래스로 분리하고
    currency mismatch 검증(`__add__`에서 `CurrencyMismatch` 예외)이 있어야 함
11. **낙관적 잠금이 기본 동시성 제어** — `version: int = 0` 필드 + Repository
    save에서 같은 version으로만 UPDATE 성공 + `ConcurrencyError` 예외. 비관적
    잠금(`SELECT FOR UPDATE`)은 의도적 선택 + 근거(예: 충돌 빈도 매우 높은
    핫 아이템)를 명시할 때만 사용
12. **Context Map의 BC 간 관계에 유형 라벨이 붙어 있음** — Customer-Supplier /
    Conformist / Published Language / ACL / Shared Kernel / OHS / Partnership 중
    어떤 관계인지 명시. 단순 BC 목록 나열은 fail
13. **원전 인용이 패턴별로 다양화됨** — Hexagonal→Cockburn, Clean→R. Martin,
    Layered/Repository/UoW/Data Mapper→Fowler, CQRS→Greg Young, ACL/BC/Aggregate→Evans
14. **Repository 내부 `conn.commit()` 완전 제거** — Application Service가 UoW
    `commit()`을 호출하므로 Repository.save는 staging만 한다 (잔존하면 fail)
15. **멱등성 3중 분류는 정확한 명칭 사용** — "도메인 상태 검사 / Dedup 테이블 /
    PG idempotency-key". "낙관적 잠금"은 동시성 제어이지 멱등성이 아니므로 섞지 말 것
16. **리팩터링 모드: 원본의 모든 함수가 별도 Before/After/Reason 블록으로 처리됨** —
    "흡수됐다"는 말로 한 함수를 빠뜨리는 것은 fail

> Reference: `references/ddd-tactical-checklist.md` — 각 항목의 구현 스켈레톤

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
- **설계**: 애플리케이션 아키텍처 설계, 패턴 선택, 계층 정의
- **리뷰**: 기존 아키텍처의 패턴 위반 사항 평가
- **리팩터링**: 기존 구조를 아키텍처 패턴에 맞게 개선

의도가 모호한 경우 설계 모드를 기본으로 한다.

### 설계 모드

애플리케이션 아키텍처를 설계할 때 다음 순서를 따른다:

1. **복잡도를 먼저 평가한다.** 단순 CRUD -> 레이어드로 충분하다. 여러 통합이 있는
   복잡한 도메인 -> 헥사고날 또는 클린. 과도한 엔지니어링을 하지 않는다.

2. **의존성 방향을 정의한다.** 모든 소스 코드 의존성은 안쪽을 향한다. 도메인이
   인터페이스(포트)를 정의하고, 인프라가 이를 구현한다(어댑터).

3. **패턴을 선택적으로 적용한다.** CQRS와 이벤트 소싱은 최상위 아키텍처가 아니다
   — 이점이 있는 바운디드 컨텍스트에만 적용한다.

4. **통합 경계를 계획한다.** 외부 시스템은 ACL을 통해 통신한다. 내부 도메인
   이벤트는 내부에 유지하고, 통합 이벤트가 BC 경계를 넘는다.

### 리뷰 모드

잘 구성된 아키텍처를 리뷰할 때는 개선 사항을 나열하기 전에 강점을 먼저
인정한다. 각 발견 사항은 다음 형식으로 작성한다:

```
[패턴] -- 이 구조가 해당 패턴의 원칙을 위반하는 이유 설명
```

리뷰를 확정하기 전에 이 체크리스트의 모든 항목을 검증한다:

- [ ] 의존성이 안쪽을 향하는가 (도메인이 인프라를 import하지 않는가)
- [ ] 인터페이스를 구현하는 계층이 아닌 사용하는 계층이 소유하는가 (소유권 역전)
- [ ] 외부 시스템이 포트/어댑터 또는 ACL 뒤에 격리되어 있는가
- [ ] CQRS가 시스템 전체가 아닌 바운디드 컨텍스트별로 선택적으로 적용되었는가
- [ ] 도메인 이벤트가 통합 이벤트로 직접 노출되지 않는가
- [ ] 리포지토리 추상화가 테이블 단위가 아닌 애그리거트 단위인가
- [ ] Unit of Work가 트랜잭션 경계를 명시적으로 관리하는가
- [ ] 커맨드 메서드가 쿼리 데이터를 반환하지 않는가 (CQS 원칙)
- [ ] 계층 간 순환 의존성이 없는가
- [ ] 통합 이벤트가 내부 도메인 개념을 누출하지 않는가
- [ ] 어댑터 구현에 비즈니스 로직이 포함되어 있지 않은가
- [ ] 포트 인터페이스가 기술적 연산이 아닌 도메인 의도를 표현하는가
- [ ] 패턴의 복잡도가 문제의 복잡도에 부합하는가 (과도한 엔지니어링 없음)
- [ ] Aggregate Root에 불변식(invariant)이 주석/문서로 명시되어 있는가
- [ ] 상태 전이 규칙이 매트릭스로 정의되고 InvalidStateTransition으로 위반을
      차단하는가 (단순 `status = "..."` 직접 할당 금지)
- [ ] AggregateRoot 기반 클래스 + `_record_event`/`collect_events` 패턴으로
      도메인 이벤트가 수집·디스패치되는가
- [ ] 도메인 개념(금액·식별자·수량)이 원시 타입(int, str)에서 VO로 추출되었는가
      (Money에는 currency 포함, ProductCode·Quantity 등)
- [ ] 외부 SDK 어휘(`payment_token`, `charge.id`, `ZITEM_CD`)가 도메인
      필드명·클래스명에 침투하지 않았는가 (Ubiquitous Language 정화)
- [ ] 파일 트리가 평탄(`domain/model/`)이 아닌 의미군 묶음
      (`domain/model/<aggregate>/`)으로 구성되었는가

### 리팩터링 모드

변경 전/후를 보여주고 각 변경의 이유를 명시한다. 각 변경을 특정 패턴 원칙에
연결한다. 각 변경은 다음 형식으로 작성한다:

```
[Before]
<원래 구조/코드>

[After]
<개선된 구조/코드>

[Reason] 패턴 -- 이 변경이 해당 패턴에 부합하는 이유 설명
```

변경 사항을 제시하기 전에 아래의 적용 가능한 모든 개선을 적용한다:

- [ ] 도메인의 인프라 의존성 -> 포트 인터페이스 + 어댑터로 추출
- [ ] 직접 외부 시스템 호출 -> ACL로 래핑 (Facade + Adapter + Translator)
- [ ] 모놀리식 읽기/쓰기 모델 -> CQRS로 분리 (복잡도가 정당화하는 경우)
- [ ] 외부에 노출된 도메인 이벤트 -> 통합 이벤트로 변환
- [ ] 도메인의 DB 로직 -> 리포지토리/데이터 매퍼로 이동
- [ ] 분산된 트랜잭션 관리 -> Unit of Work로 통합
- [ ] 도메인 개념의 원시 타입 -> 값 객체로 추출
- [ ] 데이터를 반환하는 커맨드 메서드 -> 커맨드 + 쿼리로 분리
- [ ] 과도하게 엔지니어링된 단순 도메인 -> 적절한 패턴 수준으로 단순화
- [ ] 의도적으로 적용하지 않은 패턴과 그 이유를 명시
- [ ] 단순 데이터 클래스인 Aggregate -> 불변식 + 상태 전이 메서드를 가진 Root로
      재설계 (`order.confirm_payment(...)` 같은 도메인 메서드)
- [ ] 매직 스트링 상태값(`"confirmed"`) -> 상태 VO + 전이 매트릭스로 추출
- [ ] 흩어진 이벤트 발행 -> AggregateRoot 기반 + collect-and-dispatch 패턴
- [ ] 원시 타입 도메인 개념(금액·식별자) -> Value Object로 추출 (currency 포함)
- [ ] 외부 SDK 어휘 침투 -> ACL Translator + 도메인 어휘 사전으로 정화
- [ ] 평탄한 파일 트리 -> Aggregate 단위 의미군 묶음으로 재배치

---

## 1. 아키텍처 스타일

헥사고날(포트 & 어댑터), 클린 아키텍처, 어니언 아키텍처, 전통적인 레이어드
아키텍처를 비교한다. 모두 동일한 핵심 목표 — 도메인을 향한 의존성을 갖는
관심사 분리 — 를 공유하지만 내부 계층 구조화 방식이 다르다. DIP(의존성 역전
원칙)는 세 가지 현대 패턴 모두의 이론적 기반이다.

가장 적합한 단순한 스타일을 선택한다: 단순 CRUD에는 레이어드, 다중 통합
시스템에는 헥사고날, 내부 계층 구조화 가이드로는 어니언/클린을 참조한다.

> Reference: `references/hexagonal.md`

## 2. CQRS

CQRS(Command Query Responsibility Segregation)는 읽기 모델과 쓰기 모델을
분리한다. Meyer의 CQS(메서드 수준)에서 Young의 CQRS(모델 수준)로 발전했다.
최상위 아키텍처가 아니다 — 비대칭적 읽기/쓰기 최적화가 필요한 바운디드
컨텍스트에 선택적으로 적용한다.

세 가지 구현 수준: 동일 DB에 다른 모델, 별도 DB에 최종 일관성, 이벤트 기반
프로젝션.

> Reference: `references/cqrs.md`

## 3. 이벤트 소싱

현재 상태 대신 불변 이벤트의 시퀀스로 상태 변경을 저장한다. 관련 패턴 포함:
Outbox(신뢰할 수 있는 이벤트 발행), Snapshot(리플레이 성능), Projection(읽기
모델 구성), Event Upcasting(스키마 진화).

선택적으로 적용한다 — 모든 바운디드 컨텍스트에 이벤트 소싱이 필요한 것은
아니다. Greg Young은 이벤트 소싱 모놀리스가 가장 큰 안티패턴이라고 경고한다.

> Reference: `references/event-sourcing.md`

## 4. 영속성 패턴

Data Mapper, Unit of Work, Repository, Identity Map — 도메인 모델에서
영속성을 추상화하기 위한 구체적 접근법. Active Record 대 Data Mapper의
트레이드오프와 프레임워크별 고려사항(SQLAlchemy classical mapping 대
Django ORM)을 다룬다.

Django 특화 영속성 패턴에 대해서는 implementation-django도 참조한다.

> Reference: `references/persistence.md`

## 5. 통합 패턴

부패 방지 계층(ACL), 통합 이벤트, Bubble Context — 바운디드 컨텍스트를
연결하고 외부 또는 레거시 시스템과 통합하기 위한 패턴. ACL은 가장 방어적인
컨텍스트 매핑 패턴이다. 통합 이벤트는 내부 도메인 이벤트와 구별되어야 한다.

전략적 컨텍스트 매핑 패턴(파트너십, 고객-공급자, 순응자)에 대해서는
architecture-ddd를 참조한다.

> Reference: `references/integration.md`
