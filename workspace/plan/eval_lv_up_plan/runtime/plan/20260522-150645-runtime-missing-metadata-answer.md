수정 대상: answer

# runtime missing metadata answer 수정 계획

## 수정 범위

- `workspace/develop/eval/runtime/answer/case-runtime-missing-metadata.yaml`
- 필요 시 `workspace/develop/eval/runtime/cases/plugin/public/case-runtime-missing-metadata.md`

## 순서

1. answer oracle에서 validation output 요구를 executed-or-not-run evidence로 조정한다.
2. public case에도 실행하지 않은 명령은 not-run으로 표시하도록 명시한다.
3. runtime bucket validator를 실행한다.
4. 수정 case targeted eval을 재실행하고 pass run에 `validate_eval_run.py`를 실행한다.

## 완료 조건

- missing metadata case가 file existence only를 거부하면서도 실행하지 않은 validator를 실행했다고 요구하지 않는다.
