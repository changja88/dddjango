# T17: implementation-django -> implementation-django-web

**Task:** "관리자 대시보드 웹 페이지의 템플릿 상속과 디자인 시스템 토큰은?"

**Source Skill:** implementation-django

## [주요 내용]

implementation-django 스킬은 Django 코어(모델, ORM, 뷰, 설정)를 다루지만,
웹 페이지의 템플릿 상속과 디자인 시스템 토큰은 **이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "웹 페이지(템플릿, 정적 파일, 디자인 시스템, TemplateView)는 implementation-django-web에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. 뷰 패턴: TemplateView, Generic CBV (섹션 5: `references/views.md`)
2. 캐싱: template fragment 캐싱 (섹션 10: `references/performance-caching.md`)
3. 프로젝트 구조에서 templates 디렉토리 배치

템플릿 상속(base.html, block 구조), 디자인 시스템 토큰(CSS 변수, 컴포넌트),
정적 파일 관리는 **implementation-django-web**으로 위임한다.

---
> **관련 스킬 참조:**
> - 템플릿 상속과 디자인 시스템 -> **implementation-django-web** 스킬
> - CBV/FBV 뷰 패턴 -> **implementation-django** 스킬 (현재)
