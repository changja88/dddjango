수정 대상: skill
원인 분류: skill

# workflow role-map Idempotency-Key Minor 분석

## 문제

최종 독립 리뷰에서 `role-map.md`의 API Agent row가 REST contract, status code, Problem Details, OpenAPI만 적고 `Idempotency-Key` API behavior를 직접 언급하지 않는다고 지적했다.

`integration-checklist.md`의 Risky Write Consistency Block에는 `Idempotency-Key` API behavior가 이미 있지만, role-map만 보고 role output을 구성하는 경우 order-create P5 guidance가 약해질 수 있다.

## 영향

P5 종료 기준의 열린 Minor 0에 걸린다. 특히 주문 생성 API처럼 idempotency가 핵심인 workflow에서 API Agent ownership이 덜 명시적으로 보인다.

## 수정 방향

- `dddjango/skills/workflow-dddjango-subagents/references/role-map.md`의 API Agent responsibility에 `Idempotency-Key API behavior`를 추가한다.
- runtime cache의 동일 reference도 동기화한다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

Subagent 리뷰/순차 fallback: 최종 workflow-integrity review subagent가 role-map omission을 open Minor로 보고했다.

skill-creator 리뷰: role-map row의 짧은 responsibility 보강만 수행해 progressive disclosure를 해치지 않는다.
