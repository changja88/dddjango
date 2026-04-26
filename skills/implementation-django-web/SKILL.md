---
name: implementation-django-web
description: >
  Use this skill when the user asks to "create a web page", "add a template",
  "build a page", "make a component", "add a design system component",
  "write a Django template", "organize static files", "add CSS/JS to a page",
  "create a TemplateView", "set up a base template", "review template code",
  "refactor templates", or when any Django web frontend (template, static
  asset, design system, TemplateView) code generation, review, or refactoring
  task occurs. Covers Django template inheritance, component-based template
  composition, static file management (collectstatic, ManifestStaticFilesStorage,
  WhiteNoise), CSS/JS asset pipeline, design system tokens and components,
  TemplateView patterns, HTMX integration, and CSRF handling for AJAX.
  Use this skill whenever Django web page code is being written, reviewed,
  or refactored — even for seemingly simple tasks like adding a block or
  an include. For Django core (models, ORM, settings), see
  implementation-django. For API endpoints (Django Ninja), see
  implementation-django-ninja. For API design principles, see
  architecture-api.
---

# Django 웹 프론트엔드 컨벤션과 패턴

이 스킬은 Django의 템플릿 시스템, 정적 파일 관리, 디자인 시스템, 뷰 레이어를 사용한
웹 페이지 구현 패턴을 다룬다. Django 코어(모델, QuerySet, 마이그레이션, 설정)는
implementation-django를 참조한다. API 엔드포인트(Django Ninja)는
implementation-django-ninja를 참조한다. Python 컨벤션(타입 힌트,
dataclasses)은 implementation-python을 참조한다.

**기본 요구사항 -- 모든 모드에 적용:**
- 페이지 레이아웃에 Django의 템플릿 상속(`{% extends %}`, `{% block %}`)을
  사용한다. 컴포넌트 합성에는 `{% include ... only %}`를 사용한다.
- 모든 정적 파일 참조에 `{% static %}` 태그를 사용한다. 정적 파일 경로를
  절대로 하드코딩하지 않는다.
- 서버에서 JS로 데이터를 전달할 때 `json_script` 필터를 사용한다.
  `<script>` 태그 안에서 `{{ value }}`를 직접 사용하지 않는다(XSS 위험).
- 디자인 토큰에 CSS Custom Properties를 사용한다. 컴포넌트 CSS에
  색상/간격 값을 절대로 하드코딩하지 않는다.
- 모든 AJAX POST/PUT/PATCH/DELETE 요청에 CSRF 토큰을 포함한다.
- 모든 CDN script/style 태그에 SRI(`integrity`, `crossorigin`)를 추가한다.

아래 섹션에서 다루는 주제를 작업할 때는, 상세한 컨벤션과 코드 예시를 위해
링크된 레퍼런스 파일을 읽는다.

**레퍼런스 로딩 규칙:**
- Writing 모드: 아래 주제와 관련된 코드를 생성하기 전에, 해당 레퍼런스 파일을 먼저 읽는다.
- Review 모드: 리뷰 결과를 확정하기 전에, 인용된 모든 컨벤션의 레퍼런스를 읽는다.
- Refactoring 모드: 변경사항을 제시하기 전에, 적용된 각 패턴의 레퍼런스를 읽는다.

## 응답 구조

모든 응답은 다음 구조를 따른다:

1. **[주요 내용]** -- 모드에 따른 코드, 리뷰, 리팩터링 결과
2. **[관련 스킬 참조]** -- 사용자의 다음 단계를 안내하는 연결점

이 스킬은 11개의 상호 연결된 스킬 체계의 일부이다.
사용자는 현재 작업 후 어떤 스킬을 호출해야 하는지 모르는 경우가
많으므로, 관련 스킬 참조가 워크플로우의 자연스러운 연결을 만든다.

ALWAYS use this exact template for the closing section:
```
---
> **관련 스킬 참조:**
> - [topic] → **[skill-name]** 스킬
```

## 운영 모드

사용자의 요청에 따라 모드를 선택한다:
- **Writing**: 사용자가 웹 페이지/템플릿/컴포넌트를 생성, 빌드 또는 구현하도록 요청
- **Review**: 사용자가 기존 템플릿/프론트엔드 코드를 리뷰, 검토 또는 평가하도록 요청
- **Refactoring**: 사용자가 템플릿/프론트엔드 코드를 리팩터링, 개선 또는 현대화하도록 요청

의도가 모호한 경우, Writing 모드를 기본으로 한다.

요청이 여러 모드에 걸치는 경우(예: "리뷰하고 리팩터링해줘"),
같은 코드에 대해 Review를 먼저 적용한 후 Refactoring을 적용한다.

### Writing 모드

모든 Django 웹 컨벤션을 묵시적으로 적용한다. 컨벤션을 설명하는
인라인 주석 없이 관용적인 템플릿과 뷰를 생성한다.

코드를 생성하기 전에, 관련 주제 영역의 레퍼런스 파일을 읽는다.

적용할 핵심 컨벤션:

**템플릿 아키텍처.** 베이스 템플릿과 함께 `{% extends %}`를 사용하여 페이지
레이아웃을 구성한다. 가독성을 위해 `{% endblock name %}`으로 블록 이름을 포함하여
닫는다. 부모 블록을 대체하지 않고 확장할 때 `{{ block.super }}`를 사용한다.
`{% load %}` 태그는 상속되지 않으므로 사용하는 모든 템플릿에서 로드해야 한다.
`{% extends %}`를 템플릿의 첫 번째 태그로 사용한다.

**컴포넌트 합성.** 컴포넌트에 `{% include "..." with var=val only %}`를
사용한다. `only` 키워드는 컨텍스트를 명시적으로 전달된 변수로 제한하여
컴포넌트 인터페이스를 명확하게 한다. 각 컴포넌트 상단에
`{# 필수 변수: ... #}`로 필수 변수를 문서화한다.
여러 페이지에서 사용되는 컴포넌트는 `design_system/`으로 이동한다.

**정적 파일.** 모든 정적 파일 경로에 `{% static %}`를 사용한다. 프로덕션
캐시 버스팅을 위해 `ManifestStaticFilesStorage` 또는 WhiteNoise를 설정한다.
파일 이름 충돌을 방지하기 위해 앱 수준 네임스페이싱(`myapp/static/myapp/`)을
따른다.

**디자인 시스템.** 디자인 토큰을 CSS Custom Properties로 3개 레이어로 정의한다:
primitive -> semantic -> component. 다크 모드 토큰(`[data-theme="dark"]`),
반응형 토큰(`@media`), 접근성 토큰(포커스 링, 모션 감소)을 포함한다.
Django 변수를 JS 문자열에 삽입할 때 `|escapejs` 필터를 사용한다.

**JavaScript.** 서버 데이터 전달에 `json_script` 필터를 사용한다(XSS 안전).
CDN 스크립트에 SRI 속성을 추가한다. 관심사를 분리한다: 서버 데이터(`json_script`),
앱 스크립트(`static/`), 공유 컴포넌트(`static/js/components.js`).

**뷰.** 페이지 뷰에 `TemplateView`와 `get_context_data`를 사용한다.
MRO에서 `TemplateView` 앞에 `LoginRequiredMixin`을 적용한다. 외부 서비스를
호출할 때 `get_context_data`에서 오류를 처리한다. 모든 템플릿에서 공유되는
데이터에는 context processor를 사용한다.

### Review 모드

잘 구조화된 Django 웹 코드를 리뷰할 때는, 개선사항을 나열하기 전에
코드가 잘한 점을 먼저 언급한다. 품질이 낮은 코드를 리뷰할 때는,
가장 영향력 있는 이슈에 먼저 집중한다.

각 발견사항의 형식:

```
[Convention] -- 이것이 관용적인 Django 웹 코드가 아닌 이유 설명
```

리뷰를 확정하기 전에, 아래의 모든 항목을 검증한다. 누락된 항목은 사용자가 나중에 직접 발견해야 하므로 모두 확인한다.
- [ ] 관련 스킬 참조 포함 -- 사용자의 다음 워크플로우를 위한 스킬 연결
- [ ] `{% static %}` 대신 하드코딩된 정적 파일 경로
- [ ] `json_script` 없이 `<script>` 안에 `{{ value }}` 사용 (XSS 위험)
- [ ] `integrity`와 `crossorigin` 속성이 없는 CDN 스크립트 (SRI)
- [ ] AJAX POST/PUT/PATCH/DELETE 요청에 CSRF 토큰 누락
- [ ] `only` 키워드 없는 `{% include %}` (암시적 컨텍스트 누출)
- [ ] 디자인 토큰(`var()`) 대신 하드코딩된 색상/간격 값
- [ ] 디자인 시스템 컴포넌트 스타일을 덮어쓰는 외부 CSS
- [ ] 템플릿 내 인라인 `<style>` (별도 CSS 파일이어야 함)
- [ ] `<script>` 내 인라인 앱 로직 (별도 JS 파일이어야 함)
- [ ] 부모 블록 콘텐츠를 보존해야 하는 곳에서 `{{ block.super }}` 누락
- [ ] 자식 템플릿에서 `{% load %}` 누락 (부모에서 상속되지 않음)
- [ ] 인증 페이지에서 TemplateView에 `LoginRequiredMixin` 누락
- [ ] 뷰에서 외부 서비스/API 호출 시 오류 처리 누락
- [ ] 닫는 `{% endblock %}` 태그에 `{% block %}` 이름 없음
- [ ] `var()` 폴백 값이 없는 디자인 토큰

리뷰 결과를 확정하기 전에, 인용된 모든 컨벤션의 레퍼런스를 읽어
정확성을 확인한다.

### Refactoring 모드

리팩터링할 때는 변경 전/후를 보여주고 각 변경의 이유를 명시한다.
각 변경을 특정 컨벤션에 연결하여 근거를 추적 가능하게 한다.
각 변경의 형식:

```
[Before]
<원래 코드>

[After]
<개선된 코드>

[Reason] Convention -- 이것이 Django 웹 모범 사례를 따르는 이유 설명
```

변경사항을 제시하기 전에, 아래의 모든 적용 가능한 개선사항을 적용한다. 적용 가능한 항목을 건너뛰면 사용자가 추가 리팩토링을 해야 하므로 모두 적용한다.
- [ ] 관련 스킬 참조 포함 -- 사용자의 다음 워크플로우를 위한 스킬 연결
- [ ] 하드코딩된 정적 경로 -> `{% static %}`로 교체
- [ ] 스크립트 내 `{{ value }}` -> `json_script` 필터로 변환
- [ ] SRI 없는 CDN -> `integrity`와 `crossorigin` 속성 추가
- [ ] CSRF 없는 AJAX -> 쿠키 리더와 함께 `X-CSRFToken` 헤더 추가
- [ ] `only` 없는 `{% include %}` -> `only` 키워드 추가
- [ ] 하드코딩된 색상/크기 값 -> CSS Custom Property 토큰으로 추출
- [ ] 외부 컴포넌트 스타일 덮어쓰기 -> 디자인 시스템 modifier로 이동
- [ ] 인라인 `<style>` -> 별도 CSS 파일로 추출
- [ ] 인라인 앱 `<script>` -> `static/` JS 파일로 추출
- [ ] `{{ block.super }}` 누락 -> 부모 콘텐츠가 필요한 곳에 추가
- [ ] 평탄한 템플릿 -> 컴포넌트 폴더로 재구조화
- [ ] 접근 제어 없음 -> `LoginRequiredMixin` 추가
- [ ] 뷰에서 오류 처리 없음 -> 서비스/API 호출에 try/except 추가
- [ ] 순수 `fetch()` AJAX -> HTML 프래그먼트 업데이트에 HTMX 고려

개별 변경 후, 사용자가 전체 구조를 파악할 수 있도록 **완전한 리팩터링된 코드**를
제공한다.

---

## 1. 템플릿 아키텍처

Django 템플릿 상속(베이스 템플릿, 블록, `{{ block.super }}`),
표준 3단계 패턴, 합성 기반 루트 패턴, `{% extends %}` 규칙,
TEMPLATES 설정, Django 6.0 `{% partialdef %}` / `{% partial %}`.

> Reference: `references/template-architecture.md`

---

## 2. 에셋 관리

정적 파일 설정(`STATIC_ROOT`, `STATIC_URL`, `STATICFILES_DIRS`,
`STATICFILES_FINDERS`), 앱 네임스페이싱, `collectstatic`,
`ManifestStaticFilesStorage`, WhiteNoise, CSS 관리, JavaScript
관리(`json_script`, SRI), `<script>`/`<style>` 주석 규칙,
CSP (Content Security Policy), django-compressor, django-vite.

> Reference: `references/asset-management.md`

---

## 3. 디자인 시스템

디자인 토큰(3레이어: primitive -> semantic -> component), `var()`
폴백, 다크 모드 / 테마, 반응형 토큰, 접근성 토큰(WCAG 대비,
포커스 링, 모션 감소), 폴더 구조, Atomic Design 참조, 컴포넌트 파일
컨벤션, 사용 규칙(`only` 키워드, 스타일 덮어쓰기 금지, modifier),
동적 동작(`escapejs`, 공유 JS 컴포넌트), 컴포넌트 문서화 도구.

> Reference: `references/design-system.md`

---

## 4. 뷰 레이어

뷰 아키텍처 패턴(직접 서비스 호출 vs Internal API Client),
접근 제어(LoginRequiredMixin, PermissionRequiredMixin), 뷰
분류(페이지 뷰, 웹 전용 플로우, DEBUG 전용), 오류 처리,
폴더 구조, URL 네임스페이싱, 페이지 렌더링 플로우(SSR, CSRF를
포함한 AJAX, HTMX), context processor.

> Reference: `references/view-layer.md`
