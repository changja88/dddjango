수정 대상: skill
원인 분류: P2 skill metadata/source alignment gap

# implementation-django-web P2 skill analysis

## 점검 대상

- Source skill: `dddjango/skills/implementation-django-web/SKILL.md`
- Metadata: `dddjango/skills/implementation-django-web/agents/openai.yaml`
- Source reference: `workspace/reference/implementation-django-web/reference/final.md`
- Runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web/`
- OpenAI metadata 기준: `/Users/hyun/.codex/skills/.system/skill-creator/references/openai_yaml.md`

## 근거 요약

`workspace/reference/implementation-django-web/reference/final.md`는 `implementation-django-web`의 범위를 Django 서버 렌더링 화면 구현으로 정의하고, TemplateView, Generic CBV/FBV 선택, templates/base/includes, static files, web forms, HTMX fragment, AJAX/HTMX CSRF, view auth/permission, render acceptance checks를 포함한다.

현재 `SKILL.md`는 전반 목적과 handoff를 대체로 반영하지만 P2 기준에서 다음 gap이 남아 있다.

1. Frontmatter `description`이 TemplateView는 포함하지만 Generic CBV/FBV와 대표 Generic CBV 이름을 trigger 용어로 충분히 드러내지 않는다.
2. `agents/openai.yaml`의 `default_prompt`도 TemplateView는 언급하지만 Generic CBV/FBV 선택을 충분히 드러내지 않는다.
3. Reference loading map에서 `templateview-htmx.md`가 view auth/permission 기준도 담고 있음을 드러내지 않는다.
4. `SKILL.md` runtime rule의 static asset 문구가 "referenced or reported unused"로 되어 있어, source reference의 "page-specific changed asset이 rendered page에서 참조되지 않으면 unfinished" 기준보다 느슨하게 읽힐 수 있다.

## 리뷰 방식과 결과

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 2

skill-creator 리뷰:

- Major: frontmatter와 OpenAI UI metadata가 Generic CBV/FBV 선택 범위를 충분히 trigger하지 않는다.
- Minor: Reference loading navigation이 auth/permission guidance 위치를 충분히 노출하지 않는다.
- Minor: Static asset runtime rule이 source decision보다 느슨하다.

독립 리뷰:

- Blocker/Major/Minor 없음으로 판정했다.
- `validate_skill_docs.py`, `test_validate_plan_constraints.py`, source-runtime diff 통과를 보고했다.
- `validate_plan_constraints.py`는 unrelated `implementation-django` plan 문서 metadata 문제로 실패했다고 보고했다.

통합 판단:

- skill-creator 리뷰의 Major는 source reference line 21, 36-50의 Generic CBV/FBV 범위와 skill-creator 기준의 frontmatter trigger 중요성에 직접 연결되므로 채택한다.
- 독립 리뷰의 "문제 없음"은 현재 description이 넓게 Django web work를 포함한다는 판단으로 이해하되, P2 종료 조건의 목적/trigger 명확성 기준에는 stricter correction이 필요하다.

## 수정 필요 항목

- `SKILL.md` frontmatter `description`에 Generic CBV/FBV, 대표 CBV, Django web page/view/form/HTMX/CSRF trigger를 명확히 반영한다.
- `SKILL.md` body 첫 문단과 Reference Loading 항목에 Generic CBV/FBV와 auth/permission reference 위치를 드러낸다.
- `SKILL.md` static runtime rule을 source reference와 맞춰 page-specific changed asset은 rendered page에서 참조되어야 하며 unreferenced page-specific asset은 unfinished로 보고하게 바꾼다.
- `agents/openai.yaml`의 `short_description`과 `default_prompt`를 SKILL.md 범위와 맞추되 optional interface field는 추가하지 않는다.

## Reference 후속 여부

수정 대상 reference 후속 분석은 만들지 않는다. Dedicated source reference는 현재 P2 판단에 충분하며, 부족한 것은 runtime skill/metadata 반영도다.

## Runtime sync 여부

초기 `diff -qr`는 source와 runtime cache가 같음을 보였다. Source skill 수정 후 runtime cache가 달라질 것이므로 별도 `runtime-sync` 분석/계획을 작성하고 cache sync를 수행해야 한다.

## 수정 후 재평가

P2 skill 수정 후 다음 상태를 확인했다.

- `SKILL.md` frontmatter와 목적 문단은 TemplateView뿐 아니라 Generic CBV/FBV와 대표 CBV trigger를 드러낸다.
- Reference Loading map은 `templateview-htmx.md`가 auth/permission guidance도 담고 있음을 드러낸다.
- Static asset runtime rule은 validator가 요구하는 phrase를 유지하면서, page-specific changed asset이 rendered page에서 참조되지 않으면 unfinished work로 보고하도록 source reference와 맞췄다.
- `agents/openai.yaml`은 `display_name`, `short_description`, `default_prompt`만 포함하며 optional interface field를 추가하지 않았다.
- Source skill과 runtime cache는 `diff -qr` 무출력으로 일치한다.

재평가 결과: Blocker 0, Major 0, 열린 Minor 0

## 완료 판정 기준

- 수정 후 재평가에서 Blocker 0, Major 0, 열린 Minor 0이어야 한다.
- `agents/openai.yaml`은 `display_name`, `short_description`, `default_prompt`만 유지해야 한다.
- source skill과 runtime cache가 `diff -qr` 무출력으로 일치해야 한다.
- 필수 검증 명령을 실행하고 결과를 기록해야 한다.
