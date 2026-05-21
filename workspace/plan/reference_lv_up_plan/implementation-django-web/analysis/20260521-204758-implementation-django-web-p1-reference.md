수정 대상: reference
원인 분류: source gap
리뷰 방식: sequential-fallback
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# implementation-django-web P1 reference 충분성 분석

## 평가 범위

- 대상 skill: `dddjango/skills/implementation-django-web/`
- 기대 source reference: `workspace/reference/implementation-django-web/reference/final.md`
- 현재 fallback 근거: `workspace/reference/implementation-django/reference/final.md`의 URL, 템플릿 철학/스타일, 뷰 철학/스타일, CBV/FBV, 폼, 보안, 미들웨어, 서비스 레이어 관련 기준
- P1 기준: TemplateView, templates, base template, component includes, static files, CSS/JS, HTMX, CSRF for AJAX, web forms, view auth/permission, render acceptance checks를 판단할 수 있어야 한다.

## 최초 평가

`workspace/reference/implementation-django-web/`가 존재하지 않는다. 현재 skill은 dedicated source reference가 없다고 선언하고 `implementation-django` reference와 bundled runtime reference를 fallback으로 사용한다. 이 상태에서는 Django Web이 first-class로 소유하는 템플릿 상속, base template, includes/components, static asset wiring, page CSS/JS, HTMX fragment, CSRF-aware AJAX, render acceptance check 기준이 source reference에 독립적으로 남아 있지 않다.

## 근거

- `rg --files workspace/reference/implementation-django-web` 실행 시 경로가 없음을 확인했다.
- `dddjango/skills/implementation-django-web/SKILL.md` frontmatter와 본문은 `Provisional until dedicated source reference exists` 및 fallback source 사용을 선언한다.
- bundled references는 운영 guidance로는 유용하지만 source reference가 아니라 runtime-facing 요약이다.
- `workspace/reference/implementation-django/reference/final.md`는 Django 일반 기준을 제공하지만 Django Web 전용 판단 축인 static file wiring, HTMX fragment, AJAX CSRF, render acceptance check를 한 파일에서 충분히 판정하게 하지는 않는다.

## 수정 필요 항목

| 항목 | 판정 | 필요한 수정 |
|---|---|---|
| dedicated source reference 부재 | Major | `workspace/reference/implementation-django-web/reference/final.md`를 생성한다. |
| TemplateView/CBV/FBV web adapter 기준 | Major | read-only page, CRUD/form CBV, custom FBV, thin view, selector/service handoff 기준을 명시한다. |
| templates/base/includes 기준 | Major | presentation-only template, base template block, include/component 사용 조건, optional display value 준비 위치를 명시한다. |
| static CSS/JS 기준 | Major | asset 위치, `{% static %}`, page-specific asset wiring, collectstatic/manifest 확인 기준을 명시한다. |
| HTMX/AJAX/CSRF 기준 | Major | state-changing HTMX/AJAX 요청의 CSRF token, fragment contract, ad hoc REST 회피 기준을 명시한다. |
| render acceptance checks | Major | context variable, optional empty value, auth/permission, form, HTMX fragment, static reference 검증 기준을 명시한다. |

## 수정하지 않을 항목

- eval case, answer oracle, evaluator는 P1 reference gap 수정 범위가 아니므로 수정하지 않는다.
- `implementation-django` source reference를 Django Web 전용 기준에 맞추기 위해 되돌리거나 확장하지 않는다.
- REST API, ORM/마이그레이션/트랜잭션, pytest fixture 상세는 owning skill/reference로 넘긴다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰/순차 fallback: 수정 전 분석은 `/Users/hyun/.codex/skills/.system/skill-creator/SKILL.md` 기준으로 순차 fallback을 수행했다. Dedicated source reference가 없는 상태이므로 우선 reference를 생성하고, 수정 후 real-subagent 리뷰를 수행해 이 문서의 리뷰 결과를 갱신한다.

skill-creator 리뷰: source reference 부재가 skill의 validation integrity를 약하게 만든다. SKILL.md와 bundled references가 아무리 잘 구성되어 있어도, runtime guidance가 source reference보다 앞서 있는 상태라 P1 종료 조건을 만족하지 못한다.

## 수정 후 재평가

`workspace/reference/implementation-django-web/reference/final.md`를 생성했고, TemplateView, templates, base template, includes/components, static CSS/JS, web forms, HTMX/AJAX, CSRF/security, view auth/permission, render acceptance checks 기준을 포함했다. 독립 P1 리뷰에서 기능 범위는 충분하다고 확인했고, provenance URL Minor는 `20260521-205920-implementation-django-web-p1-provenance-fix.md` 루프에서 닫았다.

최종 판정: Blocker 0, Major 0, 열린 Minor 0.
