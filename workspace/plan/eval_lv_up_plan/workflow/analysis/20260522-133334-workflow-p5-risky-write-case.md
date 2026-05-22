수정 대상: case
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

# workflow P5 risky-write public case 분석

## 배경

P5 risky-write case는 aggregate invariant, transaction owner, locking/isolation, uniqueness/idempotency storage, `Idempotency-Key`, side-effect timing, retry, concurrency/integration test를 함께 보도록 유도해야 한다.

## 현재 증거

`case-workflow-risky-write` public prompt는 재고 차감과 예약 확정을 먼저 말하고, 체크리스트 문장에서 외부 결제 side effect timing을 언급한다. 이 때문에 answer oracle의 payment side-effect 판정은 타당하지만 public scenario 자체가 결제 승인/알림 흐름을 명확히 포함하지 않는다.

## 원인 분류

원인 분류는 `case`다. Answer oracle은 risky-write 축을 요구하지만 public prompt가 payment side effect와 `Idempotency-Key` API behavior를 반복 가능하게 유도하기에는 약하다.

## 수정 판단

Public prompt에 결제 승인/알림이 흐름의 일부임을 한 문장으로 추가하고, 체크리스트에 aggregate invariant와 `Idempotency-Key` API behavior를 제품 수준 표현으로 넣는다. Private oracle 용어, scoring field, 이전 run finding은 공개하지 않는다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰: real-subagent. skill-creator 관점 sidecar가 public case 명확성 문제를 Minor로 보고했고, 메인 판단도 P5 종료조건상 열린 Minor를 닫기 위해 수정한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket workflow`
- `make eval-one BUCKET=workflow CASE=case-workflow-risky-write TRY_NUMBER=1 SCOPE=targeted TOPIC=workflow-p5-risky-write-case EXTRA_ARGS=--rerun JOBS=1`
