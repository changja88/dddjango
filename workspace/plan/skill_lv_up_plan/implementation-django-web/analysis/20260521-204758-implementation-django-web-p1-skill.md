수정 대상: skill
원인 분류: skill-source drift
리뷰 방식: sequential-fallback
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# implementation-django-web P1 skill 반영 분석

## 평가 범위

- Source reference: `workspace/reference/implementation-django-web/reference/final.md`
- Source skill: `dddjango/skills/implementation-django-web/SKILL.md`
- Bundled references: `dddjango/skills/implementation-django-web/references/*.md`
- UI metadata: `dddjango/skills/implementation-django-web/agents/openai.yaml`

## 현재 평가

Dedicated source reference를 생성한 뒤 skill을 재평가했다. 현재 source skill은 dedicated reference가 없다고 선언하고 fallback source를 사용하라고 안내한다. Bundled references는 Django Web 판단 축을 대체로 포함하지만 모두 영어 runtime 요약이고, dedicated source 이후 필요한 source alignment와 한글 문서 제약을 만족하지 못한다.

## 근거

- `SKILL.md` frontmatter description이 `Provisional until dedicated source reference exists`라고 선언한다.
- `SKILL.md` 본문은 `Dedicated Django Web source reference does not exist yet`와 fallback source scope를 안내한다.
- `agents/openai.yaml`의 `short_description`은 provisional Django templates라고 표현한다.
- `references/templates.md`, `templateview-htmx.md`, `static-assets.md`, `csrf-ajax.md`는 P1 축을 대부분 담지만 dedicated source reference와 용어/범위가 정렬되어 있지 않고 한글 문서 제약에도 맞지 않는다.

## 수정 필요 항목

| 항목 | 판정 | 필요한 수정 |
|---|---|---|
| frontmatter description | Major | fallback/provisional 제거, 사용 조건과 제외 조건을 dedicated source 기준으로 갱신 |
| SKILL.md 본문 | Major | Fallback Source 섹션 제거, routing/reference loading/runtime rules를 source 기준으로 정리 |
| bundled references | Major | templates, TemplateView/HTMX, static assets, CSRF/AJAX 내용을 한글로 정리하고 source 기준 누락을 보강 |
| agents/openai.yaml | Minor | provisional 문구 제거, default prompt와 short description을 skill 목적에 맞게 갱신 |

## 수정하지 않을 항목

- source reference를 skill 상태에 맞추기 위해 다시 약화하지 않는다.
- eval case, answer oracle, evaluator는 P1 skill 반영 수정 범위가 아니다.
- REST API, ORM/마이그레이션/트랜잭션, detailed pytest fixture mechanics는 owning skill로 유지한다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰/순차 fallback: 수정 전 분석은 `/Users/hyun/.codex/skills/.system/skill-creator/SKILL.md` 기준으로 순차 fallback을 수행했다. 수정 후 real-subagent 리뷰를 수행해 이 문서의 리뷰 결과를 갱신한다.

skill-creator 리뷰: progressive disclosure 구조는 적절하다. `SKILL.md`는 reference 파일을 1단계로 직접 연결하며 500줄 미만이다. 다만 trigger description, metadata, runtime references가 stale provisional 상태라 skill 목적 명확성과 validation integrity에 Major 문제가 있다.

## 수정 후 재평가

Source skill과 bundled references를 dedicated source 기준으로 갱신했다. `SKILL.md`와 `agents/openai.yaml`에서 provisional/fallback 문구를 제거했고, bundled references를 Django Web source 기준에 맞췄다. Real-subagent 리뷰에서 발견된 runtime wording, auth/permission, metadata Minor/Major는 `20260521-205801-implementation-django-web-p1-review-fix.md` 루프에서 보완했다.

최종 판정: Blocker 0, Major 0, 열린 Minor 0.
