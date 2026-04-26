# T02: architecture-ddd -> architecture-db

**Task:** "주문 Aggregate를 물리적 테이블로 매핑할 때 정규화 수준과 인덱스 전략은?"

**Source Skill:** architecture-ddd

## [주요 내용]

architecture-ddd 스킬은 주문 Aggregate의 논리적 구조(엔티티, 값 객체, 불변식)를 설계하지만,
물리적 테이블 매핑, 정규화, 인덱스 전략은 **이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "데이터베이스 스키마 설계(정규화, 인덱스, 트랜잭션)에 대해서는 architecture-db에 위임한다."
- 구현 패턴 섹션(12): "Repository + UoW, Data Mapper, Event Sourcing의 상세 구현은 architecture-implementation-patterns를 참조한다."

DDD 스킬이 제공할 수 있는 부분:
1. 주문 Aggregate 경계 정의 (Order -> OrderLine은 같은 Aggregate)
2. 값 객체 식별 (Money, Address, OrderStatus)
3. Aggregate 간 ID 참조 규칙 (Order -> Customer는 customer_id로만 참조)

정규화 수준(1NF-BCNF)과 인덱스 설계(B+Tree, 복합 인덱스)는 **architecture-db**로 위임한다.

---
> **관련 스킬 참조:**
> - 테이블 정규화와 인덱스 설계 -> **architecture-db** 스킬
> - Aggregate를 테이블로 매핑하는 Data Mapper 패턴 -> **architecture-implementation-patterns** 스킬
