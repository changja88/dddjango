# T21: implementation-django -> architecture-implementation-patterns

**Task:** "Django에 헥사고날 아키텍처를 도입하려면 포트/어댑터 분리는?"

**Source Skill:** implementation-django

## [주요 내용]

implementation-django 스킬은 Django 프레임워크 레이어의 코드를 다루며,
서비스 레이어와 관련된 내용을 제공한다:
- "Django ORM은 Active Record이다 -- 완전한 Repository 패턴은 거의 필요 없다." (섹션 14)
- 서비스 레이어 도입 기준: 모델 500줄 초과, 다중 모델 로직, 외부 서비스 혼합

그러나 헥사고날 아키텍처의 포트/어댑터 분리는 **이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "아키텍처 패턴(헥사고날, CQRS, 이벤트 소싱)은 architecture-implementation-patterns에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. Django 서비스 레이어 패턴 (`<entity>_<action>`)
2. 프로젝트 구조 (config/ + apps/ 레이아웃)
3. Django ORM을 통한 영속성 계층

헥사고날 아키텍처의 의존성 방향 설계, 포트 인터페이스 정의,
어댑터 구현 패턴, DIP 적용은 **architecture-implementation-patterns**로 위임한다.

---
> **관련 스킬 참조:**
> - 헥사고날 아키텍처 포트/어댑터 -> **architecture-implementation-patterns** 스킬
> - DDD + Django 프로젝트 구조 -> **architecture-ddd** 스킬 (섹션 14)
