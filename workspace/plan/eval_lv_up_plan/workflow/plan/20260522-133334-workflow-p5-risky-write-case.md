수정 대상: case

# workflow P5 risky-write public case 계획

## 수정 범위

- `workspace/develop/eval/workflow/cases/plugin/public/case-workflow-risky-write.md`
- 필요하면 같은 case의 answer oracle을 public prompt와 맞게 좁게 보강한다.

## 순서

1. Public prompt에 결제 승인/알림 side effect가 scenario 일부임을 명시한다.
2. Public prompt 체크리스트에 aggregate invariant와 `Idempotency-Key` API behavior를 추가한다.
3. Answer oracle required behavior가 public prompt의 새 축을 과도하지 않게 반영하는지 확인하고 필요한 최소 문구만 보강한다.
4. workflow bucket validator와 targeted eval을 실행한다.

## 완료 조건

- Public case는 private answer oracle이나 scoring 표현을 누설하지 않는다.
- Risky write 필수 축이 public prompt와 answer oracle에서 모두 추적 가능하다.
- Targeted eval pass run이 현재 파일 기준으로 남는다.
