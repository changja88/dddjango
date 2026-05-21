수정 대상: skill
원인 분류: skill reflection gap
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# Architecture API P1 Skill Analysis

## 평가 범위

- Source skill: `dddjango/skills/architecture-api/SKILL.md`
- Bundled references: `dddjango/skills/architecture-api/references/*.md`
- Metadata: `dddjango/skills/architecture-api/agents/openai.yaml`
- Source reference: `workspace/reference/architecture-api/reference/final.md`

## 현재 평가

- `SKILL.md`는 API architecture의 목적, routing, reference loading, runtime rules를 간결하게 제공한다.
- Bundled references는 네 개 파일로 나뉘어 progressive disclosure 구조를 유지한다.
- `rest-contracts.md`, `problem-details.md`, `pagination-versioning.md`, `idempotency-openapi.md`는 P1 주요 영역을 대부분 반영한다.
- 다만 request/response contract가 `rest-contracts.md`에서 별도 항목으로 명시되어 있지 않아 P1의 “request/response contracts” 축이 상태 코드와 OpenAPI 항목에 묻힌다.
- `agents/openai.yaml`의 short/default prompt는 errors/auth/pagination/OpenAPI 중심이며 resource modeling, URL/status, version/deprecation, rate limit, `Idempotency-Key`의 검색/선택 신호가 약하다.
- skill-creator 관점 리뷰에서 content negotiation의 q-value와 specificity priority가 bundled reference에 약하다는 Minor가 보고되었다.

## 최초 판정

- Minor: request/response contract와 metadata coverage가 P1 축 전체를 직접 드러내지 않는다.
- Minor: content negotiation 세부 기준(q-value, specificity priority)이 bundled reference에 부족하다.
- Major: 없음. core skill routing과 reference split은 적절하다.
- Blocker: 없음.

## 수정 후 재평가

- `SKILL.md` reference loading과 runtime rules에 request/response contract를 명시했다.
- `rest-contracts.md`에 request/response contract section을 추가했다.
- `rest-contracts.md` content negotiation guidance에 q-value와 specificity priority 기준을 추가했다.
- `agents/openai.yaml` default prompt에 resources, URLs, status codes, headers, versioning, rate limits, idempotency를 반영했다.
- `problem-details.md`, `pagination-versioning.md`, `idempotency-openapi.md`는 source reference 보강 후 unsupported claim이 남지 않아 수정하지 않았다.

## 최종 판정

- Blocker: 0
- Major: 0
- 열린 Minor: 0

## Subagent 리뷰/순차 fallback

- Subagent 리뷰/순차 fallback: real-subagent. 독립 리뷰의 source/skill/runtime alignment 지적 중 PATCH nuance와 OpenAPI traceability는 reference 보강으로 닫았다.
- skill-creator 리뷰: real-subagent. `SKILL.md` trigger description과 progressive disclosure는 양호했고, content negotiation bundled guidance와 metadata coverage Minor는 skill 보강으로 닫았다.

## 수정 필요 범위

- `dddjango/skills/architecture-api/references/rest-contracts.md`에 request/response contract 항목을 추가한다.
- `dddjango/skills/architecture-api/SKILL.md`의 reference loading 설명과 runtime rules에 request/response contract를 더 명시한다.
- `dddjango/skills/architecture-api/agents/openai.yaml` metadata를 architecture-api 목적 범위와 더 잘 맞춘다.
- `rest-contracts.md` content negotiation guidance에 q-value와 specificity priority를 반영한다.

## 수정하지 말아야 할 범위

- 상세 reference 내용을 `SKILL.md` 본문에 과도하게 복제하지 않는다.
- Django Ninja 구현 지침이나 pytest mechanics를 architecture-api에 끌어오지 않는다.
- eval pack 문제는 발견되어도 P1에서 고치지 않고 별도 eval plan 대상으로 분류한다.
