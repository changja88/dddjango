수정 대상: answer

# workflow answer basis and mode P4 계획

## 수정 순서

1. `case-workflow-risky-write.yaml`, `case-workflow-cache-sync.yaml`, `case-workflow-opt-out.yaml`의 `reference_basis`를 workflow rule source와 정렬한다. Risky-write case는 consistency block 자체를 검증하는 direct design answer를 허용하되 승인 없는 actual subagent execution은 금지한다.
2. `case-workflow-risky-write.yaml`, `case-workflow-actual-subagent-trace.yaml`, `case-workflow-parallel-ownership.yaml`의 `workflow_execution_expectation`을 public case intent와 맞춘다.
3. workflow bucket validator를 실행한다.
4. answer가 수정된 case를 targeted eval로 확인한다.

## 완료 조건

- answer oracle source basis와 machine execution expectation이 reference와 public case intent보다 과도하거나 부족하지 않다.
- public case에는 answer oracle, private criteria, previous run finding이 누설되지 않는다.
