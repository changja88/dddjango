# T05: architecture-implementation-patterns -> architecture-ddd

**Task:** "헥사고날에서 Aggregate 경계와 Bounded Context를 어떻게 분리하나요?"

**Source Skill:** architecture-implementation-patterns

## [주요 내용]

architecture-implementation-patterns 스킬은 헥사고날 아키텍처의 포트/어댑터 구조,
의존성 방향, 계층 분리를 다루지만, Aggregate 경계와 Bounded Context 분리는
**이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "도메인 모델링과 전략적/전술적 DDD 패턴에 대해서는 architecture-ddd에 위임한다."
- 통합 패턴 섹션(5): "전략적 컨텍스트 매핑 패턴(파트너십, 고객-공급자, 순응자)에 대해서는 architecture-ddd를 참조한다."

이 스킬이 제공할 수 있는 부분:
1. 헥사고날 아키텍처에서 의존성 방향 (도메인 -> 인프라 금지)
2. 포트 인터페이스가 도메인 의도를 표현하도록 설계
3. ACL을 통한 바운디드 컨텍스트 간 통합

Aggregate 설계 규칙(Vernon의 4규칙)과 Bounded Context 경계 식별은
**architecture-ddd**로 위임한다.

---
> **관련 스킬 참조:**
> - Aggregate 설계와 Bounded Context 분리 -> **architecture-ddd** 스킬
> - 컨텍스트 맵과 전략적 설계 -> **architecture-ddd** 스킬
