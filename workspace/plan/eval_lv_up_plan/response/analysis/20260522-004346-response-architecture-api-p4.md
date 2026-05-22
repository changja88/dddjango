수정 대상: case
원인 분류: case coverage gap

# architecture-api P4 평가 분석

## 범위

- 대상 skill: `dddjango/skills/architecture-api/`
- source reference: `workspace/reference/architecture-api/reference/final.md`
- runtime reference: `dddjango/skills/architecture-api/references/*.md`
- 평가 bucket: `workspace/develop/eval/response/`

## 근거

`architecture-api`의 목적은 REST API 계약 설계다. `SKILL.md`, `agents/openai.yaml`, bundled references, source reference는 다음 축을 모두 다룬다.

- REST resource/URL shape
- HTTP method/status behavior
- request/response/header contract
- RFC 9457 Problem Details
- auth/authz
- content negotiation
- pagination
- versioning/deprecation
- rate limit
- `Idempotency-Key`
- OpenAPI impact

현재 관련 response case는 다음과 같다.

| case id | public | answer | evaluator 관련성 | 수정 여부 | targeted eval 필요 |
|---|---|---|---|---|---|
| `case-response-order-create` | 주문 생성 API, 도메인/DB/API/테스트 통합 설계 | idempotency, Problem Details, OpenAPI, auth를 요구 | composite risky DB/API 평가라 architecture-api 단독 목적 검증은 부분적 | 유지 | 대표 회귀 가능 |
| `case-response-drf-ninja` | DRF에서 Django Ninja 전환 계획 | API contract와 implementation boundary 검증 | mixed-boundary 평가라 status/error/OpenAPI를 일부 검증 | 유지 | 필요 시 회귀 |
| `case-response-fat-view-review` | fat model/router review | Router boundary를 검증 | clean-code/view boundary 중심이며 REST 계약 축은 보조 | 유지 | 불필요 |

workflow/code bucket에도 `Idempotency-Key`, Problem Details, OpenAPI 관련 case가 있지만, 여러 skill 연계 또는 구현 diff 평가다. P4 기준 6에 따라 workflow 자체와 다중 skill 통합 평가는 P5로 넘긴다.

## 발견 사항

### Major 1: architecture-api 단독 positive coverage 부족

- 현재 positive API case는 주문 생성의 DDD/DB/API/Test 통합 설계에 묶여 있다.
- REST resource/URL, method/status, Problem Details, auth/authz, header/content negotiation, pagination, versioning, rate limit, `Idempotency-Key`, OpenAPI를 한 skill 목적 안에서 모두 검증하는 public case와 answer oracle이 없다.
- 영향: `architecture-api` reference가 충분해도 eval이 개별 skill 목적을 정확히 검증했다는 증거가 약하다.

### Major 2: architecture-api 제외 조건 negative coverage 부족

- `architecture-api`는 GraphQL, gRPC, SOAP, WebSocket, HATEOAS, API Gateway design을 범위 밖으로 둔다.
- 현재 negative response case는 simple rename, false claim, leakage 등 일반 restraint 중심이고, API boundary 제외 조건을 직접 검증하지 않는다.
- 영향: REST 계약 skill이 비-REST 설계를 과적용하지 않는지 P4에서 확인할 수 없다.

## 수정 방침

- response bucket에 case/answer만 추가한다.
- source reference와 runtime skill은 현재 평가 기준을 제공하므로 수정하지 않는다.
- evaluator script는 구조적 schema와 leakage 검증을 이미 제공하므로 수정하지 않는다.
- public case에는 answer oracle, private 기준, 이전 run finding을 넣지 않는다.

## 리뷰 방식

리뷰 방식: not-run

리뷰 결과: Blocker 0, Major 2, 열린 Minor 0

Subagent 리뷰/순차 fallback: not-run. 수정 전 inventory 확정 단계이며, 수정 후 real subagent 리뷰를 별도로 실행한다.
