수정 대상: evaluator
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 2, 열린 Minor 1

# workflow P5 combined validator hardening 분석

## 배경

P5 combined workflow validator는 단일 case가 role decomposition, handoff, integration owner, risky-write consistency를 함께 요구하는지 구조적으로 막아야 한다.

## 현재 증거

독립 workflow review sidecar가 다음 evaluator undercheck를 찾았다.

- `has_workflow_p5_combined_coverage`가 `target_behavior.required`와 `target_behavior.forbidden`을 합친 텍스트에서 필수 risky-write 용어를 찾는다. 이러면 "누락하면 실패" 같은 forbidden 문장만으로 required coverage가 충족될 수 있다.
- 같은 helper가 role decomposition과 full handoff fields를 text-level로 확인하지 않는다. Tags만 있으면 단일 consistency 문장으로 combined coverage가 통과할 수 있다.
- `case-workflow-risky-write` answer도 full handoff field 중 `Files` with `May edit`/`Must not edit`와 `Output`을 명시하지 않는다.
- 추가 sidecar는 combined guard가 bucket-level이라 `case-workflow-positive-composite`가 나중에 P5 shape를 잃어도 `case-workflow-risky-write`만으로 bucket이 green일 수 있다고 지적했다.

## 원인 분류

주된 원인 분류는 `evaluator`다. Answer도 좁게 보강하지만, structural guard가 required text를 직접 검증하지 못하면 같은 회귀가 재발한다.

## 수정 판단

- combined P5 required groups는 `target_behavior.required`에서만 찾는다.
- 별도 role decomposition 그룹과 handoff field 그룹을 추가한다.
- `case-workflow-risky-write`와 `case-workflow-positive-composite`를 지정 combined P5 case로 보고 각각 helper를 통과해야 bucket validator가 통과하도록 한다.
- 단위 테스트는 forbidden-only 용어로 통과하지 못하는 negative case와 full role/handoff required 문구가 있어야 통과하는 positive case로 갱신한다.
- `case-workflow-risky-write`와 `case-workflow-positive-composite` answer required 문구에 `Files`/`May edit`/`Must not edit`와 `Output`을 추가한다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰: real-subagent. 독립 workflow review sidecar가 Major 2, Minor 1을 보고했고, 메인 판단도 이를 채택한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket workflow`
