수정 대상: case
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

# workflow P5 positive composite case 분석

## 배경

`case-workflow-positive-composite`는 workflow bucket의 flagship composite case다. P5 기준에서는 role decomposition만 묻는 것이 아니라 risky-write consistency 필수 축을 public prompt에서 충분히 유도해야 한다.

## 현재 증거

Public prompt는 주문 생성, 재고 예약, 결제 승인, 중복 요청 방지, API, Django, 테스트를 함께 언급하지만 `Idempotency-Key`, replay/conflict, aggregate invariant, transaction owner, locking/isolation, retry, side-effect timing 같은 P5 risky-write 축을 직접 요구하지 않는다.

## 원인 분류

원인 분류는 `case`다. Answer oracle은 risky-write block을 요구하지만 public prompt가 구체 축을 충분히 유도하지 않아 얕은 role-map 답변이 통과할 위험이 있다.

## 수정 판단

Public prompt에 P5 risky-write 필수 축을 사용자 요구 형태로 추가한다. Private oracle field, scoring text, previous run finding은 공개하지 않는다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰: real-subagent. 독립 workflow review sidecar가 positive composite public prompt의 P5 유도 부족을 Major로 보고했고, 메인 판단도 이를 채택한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket workflow`
- `make eval-one BUCKET=workflow CASE=case-workflow-positive-composite TRY_NUMBER=1 SCOPE=targeted TOPIC=workflow-p5-positive-case EXTRA_ARGS=--rerun JOBS=1`
