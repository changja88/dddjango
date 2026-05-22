수정 대상: answer
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 3, 열린 Minor 0

# workflow answer basis and mode P4 분석

## 배경

P4 기준은 answer oracle이 reference보다 과도하거나 부족하지 않고, case와 answer와 evaluator가 같은 workflow skill 목적을 검증해야 한다. Sidecar review 결과 몇몇 workflow answer의 source basis 또는 machine execution expectation이 public case 의도와 어긋나는 것으로 확인됐다.

## 원인

원인 분류는 `answer`다. Public case 자체는 evaluator-only wording을 누설하지 않지만, 일부 oracle이 실제 workflow rule source보다 부정확한 reference를 가리키거나 conceptual/direct 설명 case를 execution-mode gate와 과도하게 묶고 있다.

## 수정 판단

- `case-workflow-risky-write`는 workflow skill의 risky-write output contract와 integration checklist를 직접 source basis로 삼고, public prompt가 실제 subagent 실행을 승인하지 않았으므로 actual subagent는 금지한다. 다만 이 case의 목적은 role map 강제가 아니라 Risky Write Consistency Block 자체 검증이므로 direct design answer도 허용한다.
- `case-workflow-cache-sync`는 cache sync 기준이 정의된 integration checklist를 source basis로 삼는다.
- `case-workflow-opt-out`은 direct/opt-out restraint 기준이 정의된 delegation rules를 source basis로 삼는다.
- `case-workflow-actual-subagent-trace`는 실행을 요구하는 case가 아니라 evidence protocol 설명 case이므로 `direct`를 acceptable mode로 허용한다.
- `case-workflow-parallel-ownership`은 runtime blocker를 partial로 인정한다는 oracle 문장과 machine expectation이 충돌하므로 `trace_not_captured`, `trace_missing`, `not_run`을 acceptable mode로 추가하고 evaluator가 explicit blocker 품질을 판단하게 둔다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket workflow`
- 수정 answer별 targeted eval
