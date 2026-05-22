수정 대상: case

# workflow P5 positive composite case 계획

## 수정 범위

- `workspace/develop/eval/workflow/cases/plugin/public/case-workflow-positive-composite.md`

## 순서

1. Public prompt에 aggregate invariant, `Idempotency-Key` replay/conflict, transaction owner, locking/isolation, retry, side-effect timing, concurrency/integration tests를 추가한다.
2. Answer oracle의 required behavior와 coverage tags가 public prompt를 반영하는지 확인한다.
3. workflow bucket validator와 targeted eval을 실행한다.

## 완료 조건

- Positive composite case가 workflow decomposition과 risky-write consistency를 함께 유도한다.
- Public prompt는 private answer/evaluator 기준을 누설하지 않는다.
- Targeted eval pass run이 현재 파일 기준으로 남는다.
