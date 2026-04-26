# T01: architecture-ddd -> architecture-implementation-patterns

**Task:** "주문 도메인에서 Aggregate와 Repository를 설계했습니다. 헥사고날 아키텍처로 포트/어댑터 구조를 잡고 싶은데요?"

**Source Skill:** architecture-ddd

## [주요 내용]

architecture-ddd 스킬은 Aggregate와 Repository의 전술적 설계를 다루지만,
헥사고날 아키텍처(포트/어댑터) 구조는 **이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "아키텍처 패턴(헥사고날, 클린, CQRS, 이벤트 소싱)에 대해서는 architecture-implementation-patterns에 위임한다."
- "DDD는 특정 아키텍처를 강제하지 않지만 헥사고날/클린/레이어드 아키텍처와 자연스럽게 결합된다. 상세한 아키텍처 패턴 선택과 구현은 architecture-implementation-patterns에 위임한다." (섹션 11)

DDD 스킬이 제공할 수 있는 부분:
1. 주문 Aggregate 설계 (Vernon의 4규칙 적용)
2. Repository 인터페이스 정의 (애그리거트당 하나)
3. 유비쿼터스 언어 반영 (`confirm()`, `cancel()`, `ship()`)

포트/어댑터 구조 설계는 **architecture-implementation-patterns**로 위임해야 한다.

---
> **관련 스킬 참조:**
> - 헥사고날 아키텍처 포트/어댑터 설계 -> **architecture-implementation-patterns** 스킬
> - Repository + UoW 영속성 패턴 구현 -> **architecture-implementation-patterns** 스킬
