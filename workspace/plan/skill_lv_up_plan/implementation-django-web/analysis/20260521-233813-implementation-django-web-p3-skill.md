수정 대상: skill
원인 분류: P3 책임 경계와 progressive disclosure 조정

# implementation-django-web P3 분석

## 점검 범위

- 대상 skill: `dddjango/skills/implementation-django-web/`
- source reference: `workspace/reference/implementation-django-web/reference/final.md`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web/`
- 인접 skill 경계: `architecture-api`, `architecture-db`, `architecture-ddd`, `implementation-django`, `implementation-django-ninja`, `implementation-test`, `workflow-dddjango-subagents`, `source-reference-audit`

## 현재 판정

| 항목 | 판정 | 근거 |
|---|---|---|
| 직접 책임 | 충족 | `SKILL.md` frontmatter와 본문이 TemplateView/CBV/FBV, templates, static files, forms, HTMX, CSRF, auth/permission, render acceptance를 직접 범위로 둔다. |
| handoff 기준 | 보완 필요 | API, ORM/DB, domain, workflow handoff는 명확하나 browser automation/test mechanics 문구가 web render acceptance와 약간 겹쳐 보일 수 있다. |
| 역할 침범 | 충족 | source reference와 runtime skill 모두 REST API, ORM/migration/transaction, DB architecture, domain modeling, detailed pytest mechanics를 owning skill로 넘긴다. |
| progressive disclosure | 보완 필요 | `SKILL.md`는 43줄로 500줄 미만이고 bundled reference가 1단계 링크지만, runtime rules 일부가 reference의 상세 규칙과 중복된다. |
| reference 구조 | 충족 | `templates.md`, `static-assets.md`, `templateview-htmx.md`, `csrf-ajax.md`가 모두 `SKILL.md`에서 직접 연결된다. nested reference는 없다. |
| source reference 충분성 | 충족 | `final.md`가 책임 범위, handoff, view/template/form/static/HTMX/CSRF/render acceptance 기준을 직접 제공한다. 별도 reference 후속 분석은 필요하지 않다. |
| source/runtime cache | 현재 충족 | 점검 시점의 `diff -qr` 결과는 차이가 없었다. skill 수정 후에는 runtime-sync 분석/계획과 동기화가 필요하다. |

## 발견 항목

### Minor 1. `SKILL.md` 상세 규칙 중복

- 상태: closed
- 근거: `SKILL.md` Runtime Rules가 `templates.md`, `static-assets.md`, `templateview-htmx.md`, `csrf-ajax.md`의 세부 규칙을 여러 줄로 반복한다.
- 영향: 현재 줄 수는 작지만 같은 정보가 skill 본문과 bundled reference에 나뉘어 있어 이후 불일치와 컨텍스트 낭비를 만들 수 있다.
- 수정 결과: `SKILL.md`에는 핵심 역할과 reference loading 판단만 남기고, `ModelForm.Meta.fields`, optional display path, static asset reference, concrete verification matrix는 bundled reference로 연결했다. 단, validator가 요구하는 render/static phrase는 상세 규칙이 아니라 acceptance signal label로만 유지했다.

### Minor 2. render/browser acceptance와 test mechanics handoff 문구

- 상태: closed
- 근거: `SKILL.md`가 browser automation을 `implementation-test`로 넘기면서도 web render acceptance checks를 직접 범위에 둔다.
- 영향: visible web 구현에서 render/browser acceptance 기준은 이 skill이 소유하지만, 상세 테스트 도구 구현은 `implementation-test`가 소유한다는 경계가 더 명확해야 한다.
- 수정 결과: 이 skill은 web implementation acceptance criteria와 가능한 render/browser 확인 필요성을 소유하고, detailed pytest/browser automation mechanics는 `implementation-test`로 넘긴다고 명시했다.

### Note. 인접 `implementation-test`의 역방향 handoff

- 상태: target-scope 밖 후속 관찰
- 근거: 독립 리뷰에서 `implementation-test`가 production web owner를 `implementation-django-web`으로 직접 언급하지 않는 점을 지적했다.
- 판단: 이번 P3 대상과 허용 수정 범위는 `implementation-django-web/**`이다. 인접 skill 수정은 수행하지 않는다. 후속 post-patch 리뷰도 이 항목을 "target skill defect가 아닌 adjacent test skill clarity gap"으로 분류했으므로, 대상 skill P3의 열린 Minor로 보지 않는다.

### Note. validator-visible phrase 유지

- 상태: target-scope 내 수용
- 근거: `validate_skill_docs.py --phase all`이 render/static acceptance phrase를 `SKILL.md`에서 직접 요구한다.
- 판단: 세부 규칙은 bundled reference로 넘겼고, validator가 요구하는 phrase는 상세 절차가 아니라 acceptance signal label로 압축해 유지했다. 이는 validation integrity를 지키기 위한 최소 중복이다.

## 리뷰 방식

리뷰 방식: real-subagent
- skill-creator 리뷰: real subagent가 `SKILL.md`, `agents/openai.yaml`, bundled references를 읽고 Blocker 0, Major 0, Minor 2, Note 4로 보고했다.
- 독립 P3 리뷰: real subagent가 대상 skill과 인접 skill 경계를 읽고 Blocker 0, Major 0, Minor 1, Note 5로 보고했다.
- post-patch 리뷰: real subagent가 현재 파일을 다시 읽고 target skill 기준 Blocker 0, Major 0, 열린 Minor 0으로 보고했다. 인접 `implementation-test` 역방향 handoff는 대상 skill 결함이 아닌 adjacent skill clarity gap으로 분리했다.
- 통합 판단: 중복과 browser/test handoff 문구는 대상 skill 수정으로 닫았다. 인접 `implementation-test` 역방향 handoff는 이번 target-scope 밖 Note로 기록하고 대상 skill의 open Minor로 보지 않는다.
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

## 완료 조건

- `SKILL.md` Runtime Rules가 핵심 절차 중심으로 줄어든다.
- 상세 규칙은 1단계 bundled reference에서 발견 가능하다.
- web render/browser acceptance와 detailed test mechanics handoff가 분리된다.
- source skill과 runtime cache가 동기화된다.
- 검증 명령과 `diff -qr`가 통과한다.
