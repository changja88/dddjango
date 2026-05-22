수정 대상: evaluator
원인 분류: evaluator coverage gap

# architecture-api P4 validator 분석

## 범위

- bucket: `response`
- evaluator: `workspace/scripts/validate_eval_bucket_pack.py`
- 테스트: `workspace/scripts/test_validate_eval_bucket_pack.py`

## 발견 사항

### Major 1: architecture-api P4 coverage drift를 structural validator가 막지 못함

`response` bucket validator는 공통 family tag를 확인하지만, `architecture-api` P4에서 요구한 REST 계약 세부 축을 구조적으로 확인하지 않았다. 따라서 case/answer가 나중에 줄어들어도 `specialist-positive`나 `db-api-architecture` 같은 넓은 tag만 남으면 bucket pack validation이 통과할 수 있다.

필요한 structural coverage tag:

- `architecture-api`
- `rest-contract`
- `resource-url`
- `method-status`
- `problem-details`
- `auth-authz`
- `content-negotiation`
- `pagination`
- `versioning-deprecation`
- `rate-limit`
- `idempotency`
- `openapi-impact`
- `negative-architecture-api-boundary`
- `routing-boundary`

### Major 2: 일부 answer oracle overclaim

skill-creator 관점 리뷰에서 다음 overclaim이 확인됐다.

- positive API contract oracle이 GET/POST-only workflow에서 `204`가 필요 없는 이유까지 요구했다.
- negative boundary oracle이 REST 과적용을 막는 case인데도 auth, Problem Details, cache, rate limit을 모두 언급하도록 요구했다.

두 항목 모두 source/runtime reference의 "필요한 만큼" 기준보다 강하므로 answer 요구를 줄인다.

### Minor 1: negative boundary case의 exclusion coverage 일부 누락

negative case가 GraphQL, WebSocket, HATEOAS, API Gateway는 다루지만 `gRPC`, `SOAP`를 직접 언급하지 않았다. 같은 non-REST boundary 계열이지만, skill의 명시적 제외 조건을 더 직접 검증하도록 public case와 answer에 추가한다.

## 수정 방침

- evaluator에 response bucket 전용 P4 coverage tag 검사를 추가한다.
- 기존 broad required coverage와 architecture-db P4 coverage 검사는 유지한다.
- positive oracle에서 `204` negative justification 요구를 제거한다.
- negative oracle은 REST boundary를 제한된 resource/method/status 중심으로 줄이고, 나머지 API-visible 항목은 직접 관련될 때만 언급하도록 한다.
- public case나 answer oracle에 이전 run finding을 넣지 않는다.

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 3, 열린 Minor 1

Subagent 리뷰/순차 fallback: real-subagent. 독립 P4 eval alignment review가 validator drift 방지를 Major로 지적했고, skill-creator 관점 review가 oracle overclaim 2건을 Major로 지적했다.
