# T09: architecture-db -> architecture-ddd

**Task:** "ERD 설계 중 주문과 결제가 같은 Bounded Context인지 판단 기준은?"

**Source Skill:** architecture-db

## [주요 내용]

architecture-db 스킬은 ERD 설계(개념적 -> 논리적 -> 물리적 모델링)를 다루지만,
Bounded Context 경계 판단은 **이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "도메인 모델 설계(애그리거트, 바운디드 컨텍스트)에 대해서는 architecture-ddd에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. 주문과 결제 테이블 간 관계 모델링 (FK, 참조 무결성)
2. 개념적 ERD에서 엔티티/관계 식별
3. 모델링 프로세스: 요구사항 -> 개념적(ERD) -> 논리적(정규화) -> 물리적(인덱스)
- (섹션 1: `references/modeling.md` 참조)

Bounded Context 경계 판단(같은 용어의 다른 의미, 컨텍스트 맵, 서브도메인 분류)은
**architecture-ddd**로 위임한다.

---
> **관련 스킬 참조:**
> - Bounded Context 경계 판단과 컨텍스트 맵 -> **architecture-ddd** 스킬
> - 컨텍스트 간 통합 패턴 (ACL) -> **architecture-implementation-patterns** 스킬
