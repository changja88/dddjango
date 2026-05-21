수정 대상: skill
원인 분류: source reflection gap
대상: implementation-django-ninja
생성 시각: 2026-05-21 20:48:29 KST
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

## 최초 평가

Source skill과 bundled references는 Router thinness, Schema 분리, auth/pagination/filtering,
Problem Details, OpenAPI, TestClient, DRF-to-Ninja migration을 대체로 다루지만, 전용
source reference가 없다는 전제 때문에 `provisional`과 fallback source 의존을 강조한다.
새 source reference가 생기면 source skill은 다음과 같이 갱신되어야 한다.

- frontmatter description에서 provisional/fallback 표현 제거
- 본문 첫 단락을 dedicated source reference 기반으로 전환
- fallback source를 source boundary와 related source로 재분류
- bundled references에서 `provisional` 문구 제거
- Django Ninja 공식 기능명(FilterSchema, Query binding, exception handler, TestClient)을
  source reference와 같은 경계로 정리
- `agents/openai.yaml`의 short description을 source skill 목적과 맞게 갱신

## 부족 항목

| 파일 | 부족 내용 | 영향 |
|---|---|---|
| `dddjango/skills/implementation-django-ninja/SKILL.md` | provisional/fallback 설명 | dedicated reference 생성 후 metadata가 stale해짐 |
| `dddjango/skills/implementation-django-ninja/agents/openai.yaml` | "Provisional fallback" short description | UI metadata가 skill 목적과 충돌 |
| `references/router-schema.md` | provisional 문구와 thin boundary 보강 필요 | source reference와 runtime guidance 불일치 |
| `references/auth-pagination-filtering.md` | FilterSchema/Query, auth scope 기준 보강 필요 | implementation guidance가 과소 지정됨 |
| `references/problem-details-openapi.md` | Django Ninja exception handler와 validation error mapping 보강 필요 | Problem Details 적용 방식이 간접적임 |
| `references/testclient.md` | TestClient scope와 OpenAPI/compatibility not-run 보고 기준 보강 필요 | validation integrity가 약함 |

## 최초 판정

Major 1: dedicated reference가 생긴 뒤에도 skill이 provisional fallback이라고 말하면 source
reflection과 runtime metadata가 맞지 않는다.

Minor 1: bundled references 일부는 source reference보다 framework feature명이 덜 명시적이다.

## 수정

다음 runtime skill surface를 수정했다.

- `dddjango/skills/implementation-django-ninja/SKILL.md`: provisional/fallback 설명을 제거하고
  dedicated source boundary, routing, output shape, reference loading, runtime rule을 한글
  중심으로 갱신했다.
- `dddjango/skills/implementation-django-ninja/agents/openai.yaml`: UI metadata를 Django Ninja
  adapter 구현 목적과 full runtime scope에 맞게 갱신했다.
- `dddjango/skills/implementation-django-ninja/references/router-schema.md`: Router/Schema 경계,
  status-specific response schema, `ModelSchema` field 제한, DRF-to-Ninja conversion, 예시를
  보강했다.
- `dddjango/skills/implementation-django-ninja/references/auth-pagination-filtering.md`:
  auth scope, `FilterSchema`, `Query`, pagination hook, rate limiting/versioning 기준을 보강했다.
- `dddjango/skills/implementation-django-ninja/references/problem-details-openapi.md`:
  Django Ninja exception handler, validation error mapping, Problem Details, OpenAPI 검증 기준을
  보강했다.
- `dddjango/skills/implementation-django-ninja/references/testclient.md`: TestClient scope,
  API contract test 항목, verification reporting 기준을 보강했다.

## 재평가

수정 후 독립 review 2건 모두 skill 반영도와 skill-creator 관점에서 Blocker 0, Major 0,
열린 Minor 0으로 판정했다. 남은 note는 bundled reference가 source detail을 의도적으로
압축한다는 점, `agents/openai.yaml`의 `short_description`이 짧다는 점, validator 내부의
provisional list가 source reference 존재 시 우회된다는 점이며 모두 P1 closure를 막지 않는
비차단 note다.

최종 판정: Blocker 0, Major 0, 열린 Minor 0.

## Subagent 리뷰/순차 fallback

Subagent 리뷰를 실행했다. 수정 전 review는 missing source reference, provisional wording,
metadata undercoverage, framework-specific detail 부족을 지적했다. 수정 후 review 2건은
open Blocker/Major/Minor가 없다고 판정했다.

## skill-creator 리뷰

수정 전 자체 점검 기준과 수정 후 통합 판단:

- 목적 명확성: `provisional` 표현을 제거하고 Django Ninja adapter 구현 목적을 명확히 했다.
- trigger description: DRF greenfield 요청을 Django Ninja로 전환하는 trigger를 유지했다.
- progressive disclosure: SKILL.md는 core workflow만 두고 세부 항목은 references로 나누는 구조를 유지했다.
- reference 중복/누락: bundled references는 source reference의 판단 축을 runtime에 필요한 수준으로 반영한다.
- validation integrity: 실행하지 않은 TestClient/OpenAPI/schema diff를 보고하지 않는 규칙을 유지했다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`: 통과
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`: 통과
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: 통과
