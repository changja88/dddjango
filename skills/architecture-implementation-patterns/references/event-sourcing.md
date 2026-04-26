# Event Sourcing과 관련 패턴

## 1. Event Sourcing

### 정의

> 출처: Martin Fowler (2005), Greg Young (2010)

> "Event Sourcing ensures that all changes to application state are stored as a sequence of events." — Martin Fowler

상태를 현재 값(current state)이 아니라 **이벤트의 시퀀스**로 저장한다. 현재 상태는 이벤트를 처음부터 재실행(replay)하여 재구성한다.

### 3가지 핵심 능력

| 능력 | 설명 |
|---|---|
| Complete Rebuild | 이벤트 로그에서 애플리케이션 상태를 완전히 재구축 |
| Temporal Query | 특정 시점까지의 이벤트만 재실행하여 과거 상태 확인 |
| Event Replay | 잘못된 이벤트를 역전시키고 수정된 이벤트로 재실행 |

### 적합한 경우

- 완전한 audit trail이 필요한 도메인 (금융, 보험, 의료)
- 규제 준수(regulatory compliance)가 요구되는 시스템
- 비즈니스 규칙의 rollback이나 시간 여행 쿼리가 필요한 경우
- 도메인 전문가가 자연스럽게 이벤트 언어로 말하는 도메인

### 부적합한 경우

- 현재 상태만 중요하고 이력이 불필요한 시스템
- 단순 CRUD
- **GDPR 등 개인정보 삭제 의무** — append-only, immutable 특성과 충돌. 설계 초기부터 고려 필요
- Audit log만 필요한 경우 — Event Store가 audit log를 대체하지 않는다

### 외부 시스템 문제 (Fowler의 경고)

- **External Queries**: 상태 재구축 시 과거 외부 쿼리 응답이 필요
- **External Updates**: replay 시 외부 시스템에 update 메시지가 재전송되는 문제
- **해결책**: 외부 시스템을 **Gateway**로 감싸고, replay 중에는 비활성화

### CQRS와의 관계

> "You can use CQRS without Event Sourcing, but with Event Sourcing you must use CQRS." — Greg Young

Event Store가 write model이 되고, Projection이 query side(read model)가 된다. Event Sourcing 단독으로는 "이름이 X인 사용자 찾기" 같은 쿼리가 어렵기 때문에 CQRS가 사실상 필수이다.

### Greg Young의 경고

전체 시스템을 Event Sourcing으로 구축하는 것(event sourced monolith)은 **지난 10년간 본 가장 큰 안티패턴**이다. 시스템의 일부에만 선택적으로 적용해야 한다.

---

## 2. Outbox Pattern

> 출처: Chris Richardson, microservices.io

### 해결하는 문제: Dual Write Problem

하나의 연산이 **DB 쓰기 + 메시지 브로커 발행**을 동시에 수행해야 할 때, 두 시스템 간의 원자성을 보장할 수 없는 문제. Richardson은 이것을 "rule, not optimization"이라고 정의한다.

### 작동 방식

```
[Service] --같은 DB 트랜잭션--> [Business Table] + [Outbox Table]
                                                       |
                                             [Message Relay] → [Message Broker]
```

1. 비즈니스 데이터 저장 시 **같은 DB 트랜잭션** 내에서 Outbox 테이블에도 INSERT
2. 별도의 Message Relay가 Outbox를 읽어 브로커로 발행
3. 발행 완료 후 해당 레코드를 삭제하거나 완료 표시

### Relay 구현 비교

| 방식 | Polling Publisher | Transaction Log Tailing (CDC) |
|---|---|---|
| 동작 | 주기적으로 Outbox 테이블 조회 | DB WAL을 직접 읽어 변경 감지 |
| 도구 | 별도 불필요 | Debezium 등 CDC 도구 필요 |
| 지연 | 초~분 단위 | 거의 실시간 (밀리초) |
| DB 부하 | 폴링 쿼리로 증가 | 경량 (replication log 읽기) |
| 순서 보장 | 어려움 | 트랜잭션 커밋 순서 유지 |
| 권장 | **대부분의 경우 여기서 시작** | 높은 처리량 또는 엄격한 SLA 필요 시 |

---

## 3. Snapshot Pattern

> 출처: Kurrent, Domain Centric

### 문제

Aggregate 상태를 복원하려면 해당 stream의 모든 이벤트를 재실행해야 한다. 이벤트 수가 많아지면 성능이 저하된다.

### 작동 방식

```
[Snapshot (v=1000)] + [Event 1001] + ... + [Event 1050]
        |                                       |
        v                                       v
   스냅샷에서 복원          →          이후 50개만 replay
```

1. N개 이벤트마다 (예: 1,000개) 현재 상태의 스냅샷 저장
2. 로딩 시: 가장 최근 스냅샷 찾기 → 그 이후 이벤트만 replay
3. 스냅샷은 이벤트 스트림을 **대체하지 않는다** — 이벤트가 source of truth

### 핵심 원칙

> "Don't introduce snapshots until you actually encounter performance issues."

- 스냅샷은 **최적화**이지 패턴의 핵심이 아니다
- replay 시간이 hot aggregate 기준 **100ms를 초과**할 때 고려
- 스냅샷 저장 비용 vs rehydration 절약 시간의 균형

---

## 4. Projection Pattern

> 출처: Event-Driven.io, Marten

이벤트 스트림으로부터 **읽기 전용 모델(read model)**을 구축하는 과정. CQRS의 query side를 구성하는 핵심 메커니즘이다.

### Projection 유형

| 유형 | 실행 시점 | 일관성 | 적합한 경우 |
|---|---|---|---|
| Inline | 이벤트 기록과 **같은 트랜잭션** | Strong | 실시간 정합성 필수 |
| Async | 백그라운드 프로세스가 처리 | Eventual | **대부분의 read model에 적합** |
| Live | 요청 시 on-demand로 계산 | 실시간 | 일회성 리포트, 복잡한 집계 |

### 핵심 원칙

- Event Store = write model이자 single source of truth
- Read model은 **highly denormalized** 형태로 쿼리에 최적화
- 하나의 이벤트가 **여러 read model을 업데이트**할 수 있다
- 실무에서는 혼합: 실시간 필요한 aggregate는 inline, 나머지는 async

---

## 5. Event Upcasting (Schema Evolution)

> 출처: Event-Driven.io, Akka

### 문제

Event Store의 이벤트는 immutable하지만, 비즈니스 요구사항 변화에 따라 이벤트 스키마도 진화해야 한다.

### 진화 전략 (단순 → 복잡 순)

| 전략 | 설명 | 적용 시기 |
|---|---|---|
| Weak Schema | 새 필드에 기본값 부여. 없는 필드는 기본값 처리 | 초기, backward compatible 변경 |
| Versioned Events | 이벤트 타입에 버전 번호 부여 (`OrderCreated_V2`) | 초기, 가장 단순 |
| Upcasting | 읽기 시점에 old → new 스키마로 변환하는 middleware | 스키마 변경 누적 시 |
| Copy-and-Transform | 전체 이벤트 스트림을 새 스키마로 복사 | 최후의 수단 |

### Upcasting 동작

```
[Event Store (raw)] → [Deserialize] → [Upcaster Chain: v1→v2→v3] → [Application]
```

- 역직렬화와 애플리케이션 로직 사이에 삽입되는 **pluggable middleware**
- 체인으로 연결: 애플리케이션 코드는 **최신 버전만 처리**하면 된다
- **주의**: 매 역직렬화 시 실행되므로 무거운 연산 포함 시 성능 저하

---

## 6. 패턴 간 관계

```
Event Sourcing (이벤트를 source of truth로 저장)
  ├── CQRS (읽기/쓰기 분리) ── 사실상 필수
  │     └── Projection (Read Model 구축)
  ├── Snapshot (Event Replay 성능 최적화) ── 선택
  └── Event Upcasting (스키마 진화) ── 장기 운영 시 필요

Outbox (DB+Broker 원자성) ── Event Sourcing 여부와 무관하게 독립 적용 가능
```
