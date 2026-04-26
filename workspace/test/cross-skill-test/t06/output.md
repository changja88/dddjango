# T06: architecture-implementation-patterns -> architecture-db

**Task:** "Data Mapper에서 테이블 정규화와 인덱스 설계는?"

**Source Skill:** architecture-implementation-patterns

## [주요 내용]

architecture-implementation-patterns 스킬은 Data Mapper 패턴의 구조적 설계를 다룬다:
- 도메인 모델에서 영속성을 추상화하는 구체적 접근법
- Active Record vs Data Mapper 트레이드오프
- (섹션 4: `references/persistence.md` 참조)

그러나 테이블 정규화(1NF-BCNF)와 인덱스 설계(B+Tree, 복합 인덱스)는
**이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "데이터베이스 스키마 설계(정규화, 인덱스)에 대해서는 architecture-db에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. Data Mapper와 Repository의 역할 분리
2. Unit of Work의 트랜잭션 경계 관리
3. Identity Map을 통한 객체 동일성 보장

정규화 수준 결정, 인덱스 컬럼 순서, B+Tree 아키텍처는
**architecture-db**로 위임한다.

---
> **관련 스킬 참조:**
> - 테이블 정규화와 인덱스 설계 -> **architecture-db** 스킬
> - Django ORM에서의 Data Mapper 적용 -> **implementation-django** 스킬
