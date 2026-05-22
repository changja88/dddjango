수정 대상: case

원인 분류: case

대상 case:

- 신규 `case-response-django-ninja-endpoint`

문제:

- 현재 implementation-django-ninja 관련 평가는 `case-response-order-create`, `case-response-drf-ninja`, `case-code-order-api` 등에 흩어져 있다.
- 이 조합은 Django Ninja가 greenfield API 구현 목표이고 DRF가 legacy/migration 입력이라는 방향은 확인하지만, 개별 skill P4 기준인 Router, Schema/ModelSchema, endpoint adapter, auth/permission, filtering/sorting, pagination, Problem Details, OpenAPI, TestClient를 한 case/answer 흐름에서 직접 검증하지 못한다.
- 특히 list endpoint의 `FilterSchema`/query binding, public sort key 제한, page size 상한, auth/permission wiring, ModelSchema field whitelist, OpenAPI/TestClient 검증 정직성은 현재 response bucket에서 implementation-django-ninja 단일 skill 기준으로 닫혀 있지 않다.

수정 방향:

- response bucket에 implementation-django-ninja 단일 skill positive case를 추가한다.
- public case는 사용자가 실제 파일 수정을 요청하지 않은 설계/구현 방향 질문으로 유지하고, answer oracle에만 evaluator-only 기준을 둔다.
- answer oracle은 source reference보다 과도한 요구를 하지 않도록 REST 계약 자체, DB transaction/storage, domain invariant, pytest fixture 세부 구현은 handoff로 두고 Django Ninja adapter 기준만 필수화한다.
- public case에는 answer field, private 기준, 이전 run finding, 내부 파일 경로를 넣지 않는다.

Inventory:

| bucket | case id | public | answer | evaluator 관련성 | 수정 여부 | targeted eval 필요 | run id | status |
|---|---|---|---|---|---|---|---|---|
| response | case-response-django-ninja-endpoint | 신규 | 신규 | implementation-django-ninja P4 coverage tags로 검증 | 완료 | 필요 | 20260522-021325-response-try01-targeted-implementation-django-ninja-p4 | fail: sandbox app-server 초기화 실패, exit 1, answer-oracle artifact 없음 |
| response | case-response-drf-ninja | 기존 | 기존 | DRF-to-Ninja/compatibility 일부 검증 | 없음 | 불필요 | 미실행 | reference inventory |
| response | case-response-order-create | 기존 | 기존 | risky order API mixed-boundary 일부 검증 | 없음 | 불필요 | 미실행 | reference inventory |
| code | case-code-order-api | 기존 | 기존 | code-backed thin Router/idempotency 일부 검증 | 없음 | 불필요 | 미실행 | reference inventory |
| plugin | case-plugin-provisional-overclaim | 기존 | 기존 | source status honesty 검증 | 없음 | 불필요 | 미실행 | reference inventory |
| source | case-source-provisional-drf | 기존 | 기존 | DRF guardrail/source status 검증 | 없음 | 불필요 | 미실행 | reference inventory |

리뷰 방식: real-subagent

리뷰 결과: Blocker 1, Major 4, 열린 Minor 1

Subagent 리뷰/순차 fallback: real subagent 리뷰에서 targeted eval 미완료 Blocker와 validator/DRF-to-Ninja answer alignment Major가 지적됨.

skill-creator 리뷰: trigger, 목적, reference, progressive disclosure는 대체로 적합하나 validation integrity Major가 있어 수정한다.

Targeted eval 상태:

- `case-response-django-ninja-endpoint`: sandbox 실행 run `20260522-021325-response-try01-targeted-implementation-django-ninja-p4` 생성. baseline/with-ddjango 모두 exit 1. stderr 원인은 `failed to initialize in-process app-server client: Operation not permitted`. `validate_eval_run.py` 기준 with-ddjango prompt-input JSON과 answer-oracle evaluation artifact가 없어 pass run으로 인정할 수 없다.
- 외부 실행 승인은 goal에서 주어졌으나 approval reviewer가 unsandboxed eval 실행을 거부했으므로 반복 요청하지 않는다.
