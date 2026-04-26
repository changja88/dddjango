# T12: architecture-api -> implementation-django-ninja

**Task:** "REST API 설계 완료 후 Django Ninja로 구현하려면?"

**Source Skill:** architecture-api

## [주요 내용]

architecture-api 스킬은 프레임워크 비종속적 REST API 설계 원칙을 다룬다:
- 리소스 식별, URL 정의, 메서드 선택, 요청/응답 설계
- RFC 9457 Problem Details 에러 형식
- 페이지네이션, 버저닝, 멱등성
- (섹션 1-10의 참조 파일들)

그러나 Django Ninja 프레임워크 구현(Schema, Router, 인증, 테스트)은
**이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "Django Ninja API 구현(Schema, Router, 스로틀링)에 대해서는 implementation-django-ninja에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. URL 설계 규칙 (복수 명사, kebab-case, 3단계 이하)
2. HTTP 메서드-리소스 매트릭스
3. 상태 코드 표준 (201 Created, 204 No Content, 409 Conflict 등)
4. OpenAPI 스펙 형식

Django Ninja Schema/ModelSchema, Router 데코레이터, @paginate,
FilterSchema, HttpBearer 인증은 **implementation-django-ninja**로 위임한다.

---
> **관련 스킬 참조:**
> - Django Ninja Schema/Router 구현 -> **implementation-django-ninja** 스킬
> - Django 모델/서비스 레이어 -> **implementation-django** 스킬
