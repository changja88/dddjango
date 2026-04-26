# B04 Out-of-Scope Request Test

**Prompt:** "React로 프론트엔드를 만들고 Django를 백엔드로 쓰려고 해. SPA 구조 설계 좀 도와줘."

---

## [주요 내용]

이 스킬(**implementation-django-web**)은 Django 템플릿 시스템 기반의 웹 프론트엔드를 다룹니다. 구체적으로 다음 영역이 범위입니다:

- Django 템플릿 상속(`{% extends %}`, `{% block %}`)
- 컴포넌트 합성(`{% include ... only %}`)
- 정적 파일 관리(`{% static %}`, `ManifestStaticFilesStorage`, WhiteNoise)
- 디자인 시스템(CSS Custom Properties 토큰)
- TemplateView 패턴과 HTMX 통합

**React SPA 구조 설계는 이 스킬의 범위 밖입니다.** React를 프론트엔드로, Django를 순수 백엔드 API 서버로 분리하는 SPA 아키텍처는 Django 템플릿을 사용하지 않으므로 이 스킬이 제공하는 컨벤션(템플릿 상속, `{% static %}`, 디자인 토큰, TemplateView 등)이 적용되지 않습니다.

다만 Django 백엔드 측면에서 도움이 될 수 있는 방향을 안내합니다:

1. **API 엔드포인트 설계** -- React SPA가 소비할 REST/JSON API는 Django Ninja로 구현하며, 이는 **implementation-django-ninja** 스킬에서 다룹니다.
2. **API 설계 원칙** -- 리소스 모델링, 버전 관리, 에러 응답 형식 등 API 아키텍처는 **architecture-api** 스킬에서 다룹니다.
3. **Django 코어** -- 모델, ORM, 마이그레이션, 설정 등 백엔드 기반은 **implementation-django** 스킬에서 다룹니다.

만약 React 대신 Django 템플릿 + HTMX 조합으로 SPA와 유사한 인터랙티브 경험을 구현하고 싶다면, 이 스킬이 직접 도움을 드릴 수 있습니다. HTMX를 사용한 HTML 프래그먼트 업데이트, CSRF 처리, 서버 렌더링 기반의 동적 UI 패턴을 안내할 수 있습니다.

---

> **관련 스킬 참조:**
> - [React SPA용 API 엔드포인트 구현] → **implementation-django-ninja** 스킬
> - [API 리소스 설계, 버전 관리, 에러 형식] → **architecture-api** 스킬
> - [Django 모델, ORM, 설정] → **implementation-django** 스킬
> - [Django 템플릿 + HTMX 기반 대안] → **implementation-django-web** 스킬 (현재 스킬)
