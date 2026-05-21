수정 대상: reference
원인 분류: source gap
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# Architecture API P1 Reference Analysis

## 평가 범위

- Source reference: `workspace/reference/architecture-api/reference/final.md`
- 비교 대상 runtime guidance: `dddjango/skills/architecture-api/SKILL.md`, `dddjango/skills/architecture-api/references/*.md`
- P1 기준: REST API contract, resource modeling, URL shape, HTTP method/status, Problem Details, auth/authz, headers/content negotiation, pagination, versioning/deprecation, rate limiting, `Idempotency-Key`, OpenAPI 판단 기준

## 현재 평가

- `final.md`는 REST 원칙, HTTP 메서드/상태 코드, URL/리소스, Problem Details, 헤더/콘텐츠 협상, 인증/인가, 페이지네이션, 버전/하위 호환성/deprecation, rate limit, `Idempotency-Key`, OpenAPI를 모두 다룬다.
- 다만 P1의 “판단하기에 충분한 reference” 기준으로 보면 세부 기준 일부가 약하다.
- `Idempotency-Key`는 첫 요청의 상태 코드와 응답 본문 저장, 보관 기간, 동시 요청 race 처리를 언급하지만, 키 scope, 동일 키+다른 request content 충돌, replay가 현재 mutable state를 재계산하면 안 된다는 기준이 없다.
- OpenAPI는 용도와 명세 유지 필요성은 있으나, path/method/status별 response schema, Problem Details response, auth, pagination, rate limit, idempotency header 등 계약 변경 표면을 어떤 단위로 명세해야 하는지 부족하다.
- request/response contract는 표현과 상태 코드 중심으로 흩어져 있고, request body required/optional field, response body/status/header 조합, `Location`, async result, error body 같은 계약 산출물 체크 기준이 명시적이지 않다.
- PATCH는 non-idempotent로만 표시되어 있고, patch document 자체가 멱등하게 설계될 수 있다는 nuance가 runtime reference보다 약하다.

## 최초 판정

- Major: `Idempotency-Key`와 OpenAPI의 source 기준이 bundled runtime reference보다 약해 runtime guidance의 일부 판단 근거가 `final.md`만으로는 충분하지 않다.
- Minor: request/response contract 체크 기준이 분산되어 있어 API 계약 산출물을 검토할 때 누락 가능성이 있다.
- Minor: PATCH 멱등성 nuance가 source reference에 부족하다.
- Blocker: 없음. 기존 source reference의 방향은 P1 범위와 일치하며, 보강으로 닫을 수 있다.

## 수정 후 재평가

- `final.md`에 요청/응답 계약 섹션을 추가해 request field, response status/body/header, Problem Details, auth, compatibility, OpenAPI 체크 기준을 명시했다.
- `Idempotency-Key` 섹션에 key scope, replay, same-key different-content conflict, retention, concurrency, storage handoff, original-result replay 기준을 추가했다.
- OpenAPI 섹션에 path/method/request/response/error/auth/pagination/rate-limit/idempotency/versioning 반영 표면을 추가했다.
- PATCH 섹션에 patch document 자체가 멱등하게 설계될 수 있다는 nuance를 추가했다.
- 재평가 결과: source reference는 P1의 REST API contract 판단 축을 충분히 다루며 runtime bundled references보다 약한 unsupported source gap이 남아 있지 않다.

## 최종 판정

- Blocker: 0
- Major: 0
- 열린 Minor: 0

## Subagent 리뷰/순차 fallback

- Subagent 리뷰/순차 fallback: real-subagent. 독립 리뷰에서 보고한 PATCH 멱등성 nuance와 OpenAPI impact traceability Minor는 source reference 보강으로 닫았다.
- skill-creator 리뷰: real-subagent. Reference에는 직접 Blocker/Major를 제기하지 않았고, content negotiation runtime 반영과 metadata alignment Minor는 skill 보강으로 닫았다.

## 수정 필요 범위

- `workspace/reference/architecture-api/reference/final.md`에 request/response contract 체크 기준, `Idempotency-Key` replay/conflict/scope 기준, OpenAPI 반영 표면을 보강한다.
- PATCH method 설명에 patch document idempotency nuance를 추가한다.

## 수정하지 말아야 할 범위

- eval case, answer oracle, evaluator는 P1 reference 보강 대상이 아니므로 수정하지 않는다.
- GraphQL, gRPC, SOAP, WebSocket, API Gateway 등 기존 범위 밖 항목을 새 범위로 확장하지 않는다.
