# 통합 패턴

## 1. Anti-Corruption Layer (ACL)

> 출처: Eric Evans, *Domain-Driven Design* (2003); Vaughn Vernon, *Implementing DDD* (2013)

> "Create an isolating layer to provide your system with functionality of the upstream system in terms of your own domain model." — Evans

### 구성 요소: Facade + Adapter + Translator

Evans의 원래 설계에서 ACL은 3개의 GoF 패턴을 조합한다:

| 구성 요소 | 역할 |
|---|---|
| Facade | 외부 시스템의 복잡한 인터페이스를 단순화하여 노출 |
| Adapter | 외부 인터페이스를 내 도메인 모델의 인터페이스로 변환 |
| Translator | 외부 도메인 개념/데이터를 내 도메인 개념/데이터로 매핑 |

### ACL이 필요한 상황

- Legacy 시스템과의 통합 (복잡한 스키마, 구식 API)
- 개발팀이 통제할 수 없는 외부 시스템과의 통합
- 점진적 마이그레이션에서 신규/레거시 공존 시
- 두 subsystem이 서로 다른 semantics를 가지지만 통신이 필요할 때

### Context Mapping에서의 위치

ACL은 Context Mapping 관계 중 **가장 방어적인** 패턴이다:

| 패턴 | 설명 | ACL 필요 여부 |
|---|---|---|
| Shared Kernel | 공유하기로 합의한 도메인 부분집합 | 불필요 |
| Conformist | downstream이 upstream 모델을 그대로 따름 | 불필요 |
| Customer/Supplier | 계약 협상으로 제공 | 선택적 |
| Open Host Service | 통합 프로토콜을 공개 제공 | 보완적 |
| **Anti-Corruption Layer** | 번역 계층으로 완전 격리 | - |

Vernon은 OHS와 ACL이 DDD 통합의 "bread and butter"(핵심 두 가지)라고 강조한다.

### 실무 고려사항 (Microsoft Azure Architecture Center)

- 두 시스템 간 호출에 **latency를 추가**할 수 있다
- 관리/유지보수해야 할 **추가 서비스**가 된다
- **스케일링** 방법을 고려해야 한다
- 영구적인지 vs 레거시 마이그레이션 완료 후 **폐기**할지 결정

---

## 2. Integration Event vs Domain Event

> 출처: Cesar de la Torre (Microsoft), Vaughn Vernon

### 핵심 구분

| 측면 | Domain Event | Integration Event |
|---|---|---|
| 범위 | Bounded Context **내부** | Bounded Context **간** |
| 처리 방식 | 동기/비동기 모두 가능 | **반드시 비동기** |
| 트랜잭션 | 동일 논리적 트랜잭션 내 | 원본 트랜잭션 커밋 **후** 발행 |
| 인프라 | In-memory mediator | Message Bus, Kafka 등 |
| 데이터 | 내부 도메인 모델 사용 | **Published Language로 변환** |

### Vernon의 관점

Vernon은 "domain event"과 "integration event"라는 분류 자체가 오해를 유발한다고 본다. 대안적 분류:

- 모든 이벤트는 비즈니스 사실을 나타내는 Domain Event이다
- 대신 **internal(private)** vs **external(public)**로 구분
- BC 외부로 발행되는 이벤트는 반드시 **Published Language로 정의**

### 변환 흐름

```
1. Aggregate가 Domain Event를 raise
2. Domain Event Handler가 같은 트랜잭션 내에서 side effect 처리
3. 필요시 Integration Event로 변환하여 Event Bus에 발행
4. 반드시 원본 트랜잭션 커밋 후에만 Integration Event 발행
```

### 이벤트 수신 규칙 (Vernon)

> "이벤트를 수신할 때, 그 이벤트를 모델 내부 깊숙이 소비하지 말라. 경계에서 반드시 Command로 번역하라."

```
[Upstream BC] --발행-→ Domain Event (Published Language)
       |
       v
[Downstream BC의 ACL] --번역-→ Internal Command
       |
       v
[Domain Model] --처리-→ Internal Domain Event
```

### 내부 이벤트 직접 노출의 안티패턴

| 안티패턴 | 문제 |
|---|---|
| 내부 데이터 구조를 이벤트에 그대로 담아 발행 | database-level coupling |
| Event Sourcing을 글로벌 스케일로 사용 | persistence layer가 곧 public API |
| 다른 서비스의 데이터를 로컬 캐시로 복제 | 인식하지 못한 coupling |

**올바른 접근**: outside events는 **public 계약(contract)**이다. 이벤트가 곧 API이므로 API처럼 관리해야 한다.

---

## 3. Bubble Context

> 출처: Eric Evans, *Getting Started with DDD When Surrounded by Legacy Systems* (2011/2013)

### Evans의 레거시 대응 4가지 전략

| 전략 | 설명 |
|---|---|
| **Bubble Context** | ACL을 통해 레거시에 완전히 의존하는 작은 BC |
| **Autonomous Bubble** | 자체 데이터 저장소를 가진 독립적 bubble |
| Exposing Legacy as Services | OHS로 레거시 자산 노출 |
| Event Streams | 도메인 이벤트로 컨텍스트 간 통합 |

### Bubble Context의 작동 방식

레거시 모델 앞에 새로운 도메인 모델을 점진적으로 구축한다. 새 모델(bubble)에 로직이 더 많이 구축될수록 레거시에 위임하는 양이 줄어든다.

**Umbilical ACL**: Bubble Context는 부모 컨텍스트에 완전히 의존하며, 모든 데이터를 ACL을 통해 끌어온다 — 마치 탯줄(umbilical cord)처럼.

```
1. Bubble 내에서 객체 필요 → Repository에 요청
2. Repository → ACL을 통해 레거시 DB 조회
3. 레거시 데이터 → 새로운 도메인 개념으로 변환하여 bubble에 전달
```

**장점**: DDD에 대한 큰 투자 없이 시작 가능. 작은 팀도 점진적 목표 달성 가능.

### Autonomous Bubble (확장 패턴)

| 측면 | Bubble Context | Autonomous Bubble |
|---|---|---|
| 데이터 저장소 | 없음 (레거시에서 실시간 조회) | **자체 저장소** 보유 |
| 의존성 | 레거시에 완전 의존 | 일시적 분리 가능 |
| 동기화 | 실시간 조회/변환 | ACL이 비동기 동기화 |
| 설계 자유도 | 제한적 | 높음 |

### Strangler Fig Pattern과의 관계

- **Strangler Fig**: 레거시를 점진적으로 교체하는 전체 마이그레이션 전략
- **Bubble Context**: Strangler Fig 실행 시 DDD 관점에서 신규 BC를 구성하는 구체 패턴
- 전환 기간 동안 이벤트로 신규/레거시를 동기화

---

## 4. 흔한 실수 정리

1. **Domain Event를 그대로 외부에 노출** — 내부 구현이 public API가 되어 강한 coupling
2. **Integration Event를 동기적으로 처리** — 반드시 비동기
3. **ACL 없이 외부 모델을 직접 사용** — 외부 변경이 내부를 "오염(corrupt)"
4. **수신한 이벤트를 모델 깊숙이 직접 소비** — 경계에서 Command로 번역
5. **Bubble Context에서 자체 데이터 없이 복잡한 로직** — Autonomous Bubble로 전환 필요
