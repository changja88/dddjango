# T07: architecture-implementation-patterns -> architecture-api

**Task:** "CQRS Read Model을 REST API로 노출할 때 버저닝과 페이지네이션은?"

**Source Skill:** architecture-implementation-patterns

## [주요 내용]

architecture-implementation-patterns 스킬은 CQRS 패턴의 구조적 설계를 다룬다:
- 읽기 모델과 쓰기 모델의 분리
- 세 가지 구현 수준 (동일 DB, 별도 DB, 이벤트 기반 프로젝션)
- CQS 원칙: 커맨드 메서드가 쿼리 데이터를 반환하지 않는다
- (섹션 2: `references/cqrs.md` 참조)

그러나 REST API 버저닝 전략과 페이지네이션 패턴은 **이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "REST API 설계 원칙(엔드포인트, 버저닝)에 대해서는 architecture-api에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. CQRS Read Model의 프로젝션 설계 (비정규화된 읽기 전용 뷰)
2. 쿼리 서비스와 커맨드 서비스의 분리
3. 읽기 최적화 모델 구조

버저닝(URL 경로, Sunset 헤더), 페이지네이션(Cursor vs Offset),
상태 코드는 **architecture-api**로 위임한다.

---
> **관련 스킬 참조:**
> - API 버저닝과 페이지네이션 설계 -> **architecture-api** 스킬
> - Django Ninja로 Read Model API 구현 -> **implementation-django-ninja** 스킬
