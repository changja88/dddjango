---
name: implementation-django-web
description: Django 서버렌더 표현계층 구현 지식 — TemplateView/Generic CBV/FBV 선택, Context 준비, 템플릿·base template·includes/components, Static files·CSS·JS, Web forms·POST flow, HTMX fragment·AJAX, CSRF·XSS·보안 설정, View auth·permission, Render acceptance checks. Django 서버렌더 뷰·템플릿·폼·HTMX 코드를 새로 작성하거나 리팩터링할 때 먼저 로드한다. Django 코어(모델·ORM·트랜잭션)는 implementation-django, JSON API 어댑터는 implementation-django-ninja, REST 계약 설계는 architecture-api로 위임.
---

# Django 서버렌더 표현계층 구현

## 언제 쓰나

Django TemplateView·Generic CBV/FBV·템플릿·웹폼·HTMX fragment·CSRF·view auth·render acceptance checks 코드를 설계·작성할 때 로드한다. 경계:

- REST 리소스·HTTP 상태·Problem Details·OpenAPI 계약 → `architecture-api`
- Django Ninja Router/Schema/API 어댑터 구현 → `implementation-django-ninja`
- 모델·QuerySet·Manager·마이그레이션·트랜잭션 → `implementation-django`
- DB locking·isolation·index·rollout/backfill → `architecture-db`
- pytest 픽스처·테스트더블·상세 테스트 구현 → `dddjango-implementation-test`
- 도메인 상태 전이·정책·불변식 → `dddjango-architecture-ddd`

## 핵심 운영 원칙

- 뷰는 얇은 어댑터: 요청 처리·auth/permission·form·context 조율·서비스 호출·응답 렌더링만 (§1)
- TemplateView/Generic CBV/FBV 선택은 흐름 복잡도 기준, mixin이 깊어지면 재검토 (§2)
- context에는 표시 값만; 도메인 동작은 서비스/usecase boundary로 분리 (§3)
- 템플릿은 presentation과 presentation-related branching만 담당 (§4)
- web form은 GET·valid POST·invalid POST·redirect·form error 경로를 모두 처리 (§6)
- HTMX fragment는 method·auth·permission·CSRF를 function/class view와 동일하게 보호 (§7)
- CSRF·XSS 설정과 보안 헤더는 Django 보안 프리미티브로 유지 (§8)
- render acceptance 보고는 실제 실행한 검증만 기재, 미실행은 미실행으로 명시 (§10)
- 에러는 출처로 분류 — 도메인 예외는 view-local 재렌더, 시스템·미식별은 `handler500`, transient는 미들웨어 503 (§11)

## 상세 레퍼런스

주제별로 [`references/final.md`](references/final.md)의 해당 절을 따른다:

| 주제 | 절 |
|---|---|
| 책임 범위와 handoff | §1 |
| TemplateView, Generic CBV, FBV 선택 | §2 |
| Context 준비와 표시 값 | §3 |
| Templates, base template, includes/components | §4 |
| Static files, CSS, JavaScript | §5 |
| Web forms와 POST flow | §6 |
| HTMX fragment와 AJAX | §7 |
| CSRF, XSS, security setting | §8 |
| View auth와 permission | §9 |
| Render acceptance checks | §10 |
| 서버렌더 에러 처리 (view-local 재렌더·handler500·transient 503·HTMX 에러) | §11 |

각 절은 [`references/final.md`](references/final.md)에서 필요한 항목만 읽는다(전체 로드 불필요).
