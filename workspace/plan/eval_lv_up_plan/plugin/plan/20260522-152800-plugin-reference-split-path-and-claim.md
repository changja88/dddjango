수정 대상: case

# plugin reference-split path and claim 계획

## 수정 범위

- `workspace/develop/eval/plugin/cases/plugin/public/case-plugin-reference-split.md`
- `workspace/develop/eval/plugin/answer/case-plugin-reference-split.yaml`
- `workspace/scripts/validate_eval_run.py`
- `workspace/scripts/test_validate_eval_run.py`

## 절차

1. validator false-positive 회귀 테스트를 추가한다.
2. reference routing/load-condition 문맥은 generic execution claim으로 보지 않게 한다.
3. public prompt가 실제 file link 대신 runtime-relative paths만 요구하게 수정한다.
4. answer oracle hard gate에 temp path/absolute link 금지와 unsupported validator/eval/browser/Serena claim 금지를 명시한다.
5. plugin bucket validator, run validator tests, targeted eval을 재실행한다.

## 완료 조건

- reference split 응답이 runtime-relative reference inventory를 제공하되 임시 workspace path를 노출하지 않는다.
- reference routing 문장이 validator/eval 실행 claim으로 오탐되지 않는다.
- `case-plugin-reference-split` targeted eval과 `validate_eval_run.py`가 통과한다.
