수정 대상: skill
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# architecture-api P3 분석

## 점검 범위

- Source skill: `dddjango/skills/architecture-api/`
- Source reference: `workspace/reference/architecture-api/reference/final.md`
- Runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api/`
- 비교 대상 skill: `architecture-ddd`, `architecture-db`, `architecture-implementation-patterns`, `implementation-django`, `implementation-django-ninja`, `implementation-test`, `workflow-dddjango-subagents`, `source-reference-audit`

## 현재 상태

- `SKILL.md`는 최초 45줄, 최종 40줄로 500줄 미만이다.
- bundled reference는 `SKILL.md`에서 1단계 직접 링크로 발견 가능하다.
- source skill과 runtime cache는 최초 점검 시 `diff -qr` 결과 차이가 없었다.
- source reference `final.md`는 REST API 설계, Problem Details, header/content negotiation, auth, pagination, versioning, rate limit, `Idempotency-Key`, OpenAPI를 충분히 다룬다.

## P3 평가

| 기준 | 판정 | 근거 |
|---|---|---|
| 직접 책임과 handoff 기준 | 보완 필요 | routing은 존재하지만 `Runtime Rules`가 계약 세부 판단을 직접 나열해 reference와 경계가 일부 겹친다. |
| 다른 skill과 책임 충돌 | 보완 필요 | DB 저장/락, Django Ninja 구현, pytest 계약 테스트 handoff는 있으나 실행 절차에서 "직접 결정/기록할 것"과 "넘길 것"의 구분이 더 압축될 수 있다. |
| architecture/implementation/test/source audit/workflow 경계 | 보완 필요 | source/reference audit은 이 점검에서 사용하는 skill이지만 runtime `architecture-api` routing에는 source audit handoff가 없다. Skill 자체는 사용자 API 설계 task용이므로 source audit을 runtime routing에 넣지는 않는다. |
| progressive disclosure | 보완 필요 | `SKILL.md`가 이미 짧지만 status code, Problem Details, pagination, compatibility, OpenAPI 세부 규칙을 반복한다. 핵심 절차만 남기고 세부 규칙은 reference로 유도하는 편이 낫다. |
| 500줄 미만 및 1단계 reference | 충족 | 45줄, reference 4개 모두 직접 링크. |
| 중복 저장과 컨텍스트 낭비 | 보완 필요 | `rest-contracts.md`, `problem-details.md`, `pagination-versioning.md`, `idempotency-openapi.md`와 `Runtime Rules` 사이에 같은 판단 기준이 반복된다. |
| 깊거나 숨은 reference 연결 | 충족 | reference가 `references/*.md` 한 단계에 있고 `SKILL.md`에서 모두 직접 링크된다. |

## 원인 분류

- `SKILL.md`가 P2 이후 충분히 짧아졌지만, 여전히 reference 내용을 축약 반복하는 bullet이 많다.
- API 계약 skill은 "계약 산출 순서와 handoff 판단"이 핵심이고, 상태 코드별 세부 기준이나 pagination 선택 기준은 bundled reference가 맡아도 된다.

## 수정 방향

- `SKILL.md`를 한글 중심의 runtime 지침으로 정리한다.
- `Routing`은 유지하되 직접 책임과 handoff 기준을 더 선명하게 쓴다.
- `Reference Loading`은 1단계 직접 링크를 유지한다.
- `Runtime Rules`는 세부 설계 규칙 목록이 아니라 "계약 결정 순서, reference 선택, handoff, acceptance criteria, 실제 실행 보고" 중심으로 줄인다.
- bundled reference의 세부 기준은 유지하고, source reference 자체는 이번 P3에서 직접 수정하지 않는다.

## Reference 후속 분류

- `workspace/reference/architecture-api/reference/final.md`는 P3 기준에서 source decision 부족으로 보이지 않는다.
- reference 후속 분석/계획은 새로 만들지 않는다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

### 리뷰 통합

- 독립 boundary 리뷰는 `SKILL.md` 책임 경계, handoff, 500줄 미만, 1단계 reference, source/runtime cache sync를 충족한다고 보았다.
- 독립 boundary 리뷰의 Minor 2건은 bundled reference가 DB/test ownership과 implementation ordering을 일부 침범한다는 내용이었다. `idempotency-openapi.md`는 API-visible replay guarantee 중심으로 고치고 persistence/test mechanics를 각각 `architecture-db`, `implementation-test`로 handoff했다. `pagination-versioning.md`는 rate limit의 API-visible policy/header만 남기고 middleware/adapter placement를 implementation handoff로 정리했다.
- skill-creator 리뷰의 UI metadata Minor는 `agents/openai.yaml` short description에 versioning/idempotency를 드러내도록 수정했다.
- skill-creator 리뷰의 concrete example 제안은 Note로 통합했다. 현재 bundled reference는 P3 목표인 핵심 절차와 progressive disclosure를 우선하므로 예시 추가는 필수 수정으로 보지 않는다.
- skill-creator 리뷰의 validator semantic coverage 지적은 tooling hardening 제안으로 통합했다. 이번 P3의 수정 범위는 `dddjango/skills/architecture-api/**`와 runtime sync이며, validator 구현 변경은 skill 책임 경계와 bundled reference progressive disclosure 목표 밖이다. 현재 P3 완료 판단은 manual review, source/reference inspection, validator, cache parity로 증명한다.

## skill-creator 리뷰

- 최종 판정: 목적과 trigger description은 명확하고, bundled reference는 1단계 링크로 발견 가능하며, `SKILL.md`는 세부 계약 규칙이 아니라 routing과 계약 산출 절차 중심으로 정리됐다.

## 재평가

| 기준 | 최종 판정 | 근거 |
|---|---|---|
| 직접 책임과 handoff 기준 | 충족 | `SKILL.md`가 REST API 계약을 직접 책임으로 두고 DDD/DB/Django Ninja/Test/Workflow handoff를 분리한다. |
| 다른 skill과 책임 충돌 | 충족 | reference Minor를 수정해 DB persistence, test mechanics, middleware placement를 다른 skill로 넘겼다. |
| architecture/implementation/test/source audit/workflow 경계 | 충족 | implementation/test/workflow는 routing과 runtime rule에서 handoff로만 다룬다. Source audit은 runtime API 설계 skill의 직접 routing에 넣지 않는다. |
| progressive disclosure | 충족 | `SKILL.md`는 40줄이며 세부 규칙은 `references/*.md`로 직접 연결된다. |
| 500줄 미만 및 1단계 reference | 충족 | `wc -l` 기준 `SKILL.md` 40줄, reference 4개 모두 `SKILL.md`에서 직접 링크된다. |
| 중복 저장과 컨텍스트 낭비 | 충족 | 상세 status/error/pagination/idempotency/OpenAPI 기준은 bundled reference에 있고 `SKILL.md`는 산출 절차와 handoff 중심이다. |
| 깊거나 숨은 reference 연결 | 충족 | bundled reference는 skill-local `references/*.md` 한 단계에 있다. |
