수정 대상: answer

원인 분류: answer

대상 case:

- `case-response-drf-ninja`

문제:

- public case는 기존 DRF ViewSet 주문 API를 Django Ninja Router/Schema로 옮기는 직접 DRF-to-Ninja migration 질문이다.
- answer oracle은 DRF guardrail과 mixed-boundary를 검증하지만, implementation-django-ninja source reference, runtime SKILL.md, bundled DRF-to-Ninja reference를 직접 `reference_basis`에 연결하지 않는다.
- coverage tag도 `implementation-django-ninja`가 없어 새 validator의 source/runtime/bundled basis 검증을 우회한다.

수정 방향:

- `reference_basis`에 implementation-django-ninja source reference, SKILL.md, router-schema/problem-details/testclient bundled references를 추가한다.
- coverage tag에 `implementation-django-ninja`, `drf-to-ninja`, `openapi-impact`, `testclient`, `routing-boundary`, `validation-honesty`를 추가한다.
- target behavior에 Router/Schema migration, Problem Details, OpenAPI diff, TestClient compatibility checks, domain rule Router 금지, false verification 금지를 명확히 둔다.
- public case는 변경하지 않아 private oracle 기준을 누설하지 않는다.

Inventory:

| bucket | case id | public | answer | evaluator 관련성 | 수정 여부 | targeted eval 필요 | run id | status |
|---|---|---|---|---|---|---|---|---|
| response | case-response-drf-ninja | 기존 | 수정 완료 | DRF-to-Ninja related case가 implementation-django-ninja answer 검증을 통과해야 함 | 완료 | 필요 | 20260522-022105-response-try01-targeted-implementation-django-ninja-p4 | fail: sandbox app-server 초기화 실패, exit 1, answer-oracle artifact 없음 |

리뷰 방식: real-subagent

리뷰 결과: Blocker 1, Major 4, 열린 Minor 1

Subagent 리뷰/순차 fallback: real subagent 리뷰에서 DRF-to-Ninja answer basis 누락이 Major로 지적됨.

skill-creator 리뷰: validation integrity 관점에서 related case가 source/runtime basis 검증을 우회하지 않도록 보강한다.

Targeted eval 상태:

- `case-response-drf-ninja`: sandbox 실행 run `20260522-022105-response-try01-targeted-implementation-django-ninja-p4` 생성. baseline/with-ddjango 모두 exit 1. stderr 원인은 `failed to initialize in-process app-server client: Operation not permitted`. `validate_eval_run.py` 기준 with-ddjango prompt-input JSON과 answer-oracle evaluation artifact가 없어 pass run으로 인정할 수 없다.
- 외부 실행 승인은 goal에서 주어졌으나 approval reviewer가 unsandboxed eval 실행을 거부했으므로 반복 요청하지 않는다.
