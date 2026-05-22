수정 대상: answer
원인 분류: answer underclaim

# architecture-db P4 answer oracle 분석

## 문제

real subagent 리뷰에서 architecture-db 관련 response answer oracle 일부가 eval goal보다 약한 증거 요구를 담고 있거나, DB 판단을 요구하면서 architecture-db source/runtime reference를 직접 basis로 들지 않는 문제가 확인됐다.

## 근거

- `workspace/develop/eval/response/eval_goal.md`는 response evidence로 public prompt, baseline/with output, baseline isolation, prompt-input artifact, command, exit code, event stream, stderr, answer-oracle notes, machine-readable answer-oracle artifact를 요구한다.
- 신규 DB answer oracle 3개는 `evidence_required`가 baseline/with response, baseline isolation, answer-oracle notes 정도로 좁아 eval goal보다 부족했다.
- `case-response-order-create`는 DB uniqueness/idempotency storage, transaction boundary, locking/retry tradeoff를 요구하지만 `architecture-db` source/runtime reference를 직접 basis로 들지 않는다.
- `case-response-operational-migration`은 rollout/backfill/index risk를 다루지만 broad `workspace/develop/eval` basis가 있고 runtime `architecture-db` reference를 직접 들지 않는다.
- 후속 리뷰에서 `case-response-order-create`의 DDD/API/Django Ninja/Test 혼합 요구도 owning reference에 직접 trace해야 한다는 Major가 추가 확인됐다.

## 수정 방향

- 신규 DB direct answer oracle의 `evidence_required`를 response eval goal과 맞춘다.
- `case-response-order-create`와 `case-response-operational-migration`의 `reference_basis`에 architecture-db source/runtime references를 추가한다.
- `case-response-order-create`의 non-DB mixed dimensions는 `architecture-ddd`, `architecture-api`, `implementation-django-ninja`, `implementation-test` source/runtime reference를 추가해 traceability를 닫는다.
- answer oracle 요구는 reference 범위를 넘지 않는다. concrete Django migration 구현, API contract, test mechanics는 해당 skill handoff 또는 mixed-case 범위로 유지한다.

## 리뷰 방식

리뷰 방식: real-subagent

- skill-creator 관점 리뷰: source/reference alignment Major, validation integrity Major/Blocker.
- 독립 리뷰: mixed/supporting case source basis Minor, targeted eval/evidence Major.
- 후속 skill-creator 관점 리뷰: evidence underclaim Major, order-create mixed source basis Major.

리뷰 결과: Blocker 1, Major 5, 열린 Minor 1
