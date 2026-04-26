# T20: implementation-django -> architecture-db

**Task:** "모델 필드 추가 시 정규화 재검토와 복합 인덱스 컬럼 순서 기준은?"

**Source Skill:** implementation-django

## [주요 내용]

implementation-django 스킬은 Django 모델 설계와 마이그레이션을 다룬다:
- 모델 필드 순서: db 필드 -> managers -> Meta -> __str__ -> save -> 커스텀 메서드
- 무중단 배포를 위한 3단계: nullable 추가 -> 백필 -> 제약조건
- 프로파일링 기반 데이터베이스 인덱스 추가
- (섹션 3: `references/model-design.md`, 섹션 9: `references/migrations.md` 참조)

그러나 정규화 수준 재검토(1NF-BCNF)와 복합 인덱스 컬럼 순서 원칙은
**이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "일반 RDB 설계 원칙(정규화, 인덱스 아키텍처, 격리 수준)은 architecture-db에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. Django 모델 필드 타입 선택 (`DecimalField`, `TextChoices`)
2. `Meta.indexes`에 인덱스 선언
3. Django 5.x `db_default`, `GeneratedField` 활용

정규화 위반 탐지, 복합 인덱스의 최좌선 접두사 규칙(동등 > 범위),
비정규화 판단 기준은 **architecture-db**로 위임한다.

---
> **관련 스킬 참조:**
> - 정규화와 복합 인덱스 설계 -> **architecture-db** 스킬
> - Django PostgreSQL 특수 인덱스 -> **implementation-django** 스킬 (섹션 17)
