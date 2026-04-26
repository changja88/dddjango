# T22: implementation-django -> architecture-api

**Task:** "REST API URL 네이밍, 버저닝, RFC 9457 에러 포맷 설계는?"

**Source Skill:** implementation-django

## [주요 내용]

implementation-django 스킬은 Django 프레임워크 코드를 다루며,
API 레이어에 대해 명확한 위임 체인이 있다:
- API 엔드포인트 구현 -> **implementation-django-ninja**
- API 설계 원칙 -> **architecture-api**

SKILL.md 위임 규칙에 따른 판단:
- "REST API 설계 원칙(엔드포인트, 상태 코드, 버저닝)은 architecture-api에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. Django URL 패턴 설정 (urls.py)
2. DRF 대신 Django Ninja 사용 원칙
3. 서비스 레이어와 API의 연결

REST API URL 네이밍 규칙(복수 명사, kebab-case, 3단계 이하),
버저닝 전략(URL 경로, Sunset 헤더), RFC 9457 Problem Details 형식은
**architecture-api**로 위임한다.

Django Ninja에서의 구현(@exception_handler, HttpError, Router 버저닝)은
**implementation-django-ninja**로 위임한다.

---
> **관련 스킬 참조:**
> - REST API 설계 원칙 (URL, 버저닝, 에러) -> **architecture-api** 스킬
> - Django Ninja 에러 처리와 라우팅 -> **implementation-django-ninja** 스킬
