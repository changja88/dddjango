---
name: architecture-db
description: 관계형 데이터베이스 설계 지식 — ERD·정규화·역정규화, 인덱스 아키텍처(B+Tree·복합·커버링·부분), 제약조건·중복 방지·멱등성 저장소, 트랜잭션·격리 수준·락·Risky Write, outbox 전달 보장, 쿼리 최적화(EXPLAIN ANALYZE·N+1), 운영 rollout/backfill/migration safety, 계층·상속 모델링 패턴. 데이터 신뢰성·인덱스 전략·트랜잭션 경계·outbox 전달 보장·스키마 rollout을 결정할 때 먼저 로드한다. Django ORM·마이그레이션 코드 구현은 implementation-django, 도메인 이벤트 채택 여부는 architecture-ddd로 위임.
user-invocable: false
---

# 데이터베이스 설계

## 언제 쓰나

관계형 DB 아키텍처 결정(데이터 모델링·인덱스 설계·제약조건·트랜잭션 격리·락 전략·멱등성 저장소·outbox 전달·rollout 안전성)이 필요할 때 로드한다. 경계:

- Django ORM·마이그레이션 코드 작성 → `implementation-django`
- 도메인 이벤트 채택 여부·애그리거트 경계 → `architecture-ddd`
- REST 계약·API 멱등성 키 정책 → `architecture-api`

## 핵심 운영 원칙

- 성능 최적화 순서를 지킨다: 슬로우 쿼리 최적화 → 인덱스 적용 → 캐시 → 역정규화. 역정규화는 최후 수단이며, 정규화 먼저 한 뒤 필요한 경우에만 적용한다 (§4, §5)
- 복합 인덱스는 선택도 높은 컬럼을 앞에, 커버링 인덱스로 Index-Only Scan을 목표로, 부분 인덱스로 쓰기 비용을 최소화한다 — 인덱스 설계는 실제 액세스 패턴 기반으로 결정한다 (§7)
- 비즈니스 불변식이 DB 경계에서 지켜져야 하면 unique constraint·FK·check constraint를 사용하고, 제약조건 rollout은 lock risk를 고려한 단계적 순서를 따른다 (§8)
- 격리 수준은 필요 이상으로 높이지 않는다: 대부분의 OLTP는 Read Committed, 일관된 읽기가 필요하면 Repeatable Read, 정확성이 최우선인 금융·결제는 Serializable + retry (§9.4)
- Risky Write(주문·결제·재고·예약·권한·ledger)에는 Transaction owner·Locking strategy·Idempotency storage·Side-effect timing·Isolation/retry와 위험·failure 후보인 Test criteria를 명시한다. Test criteria 자체는 테스트 의무가 아니며, 독자 DB failure와 기존 보호를 비교한 `discipline-tdd` 입장 결정이 `add`일 때만 coder가 새 테스트를 작성한다 (§9.6)
- 외부 결제·알림·메시지 발행은 DB 트랜잭션 내부에서 실행하지 않는다. 메시지 유실이 허용되지 않으면 트랜잭셔널 Outbox로 at-least-once 전달을 보장하고, consumer는 중복 수신을 무시할 수 있어야 한다 (§9.7)
- 운영 컬럼·인덱스·constraint 변경은 Expand / Backfill / Contract 단계를 따르고, 대용량 backfill은 슬롯·lock risk를 고려한 배치 처리를 계획한다 (§11)

## 상세 레퍼런스

주제별로 [`references/final.md`](references/final.md)의 해당 절을 따른다:

| 주제 | 절 |
|---|---|
| 데이터베이스 모델링 프로세스 | §1 |
| 개념적 데이터 모델링 (ERD) | §2 |
| 정규화 (1NF — BCNF) | §3 |
| 역정규화 (Denormalization) | §4 |
| 성능 최적화 순서 | §5 |
| 인덱스 아키텍처: B+Tree | §6 |
| 인덱스 설계 베스트 프랙티스 | §7 |
| 제약조건과 중복 방지 | §8 |
| 트랜잭션, 격리 수준, 락 | §9 |
| 쿼리 최적화 | §10 |
| 운영 rollout, backfill, migration safety | §11 |
| 데이터 모델링 패턴: 계층 구조 | §12 |
| 데이터 모델링 패턴: 상속과 다형성 | §13 |

각 절은 [`references/final.md`](references/final.md)에서 필요한 항목만 읽는다(전체 로드 불필요).
