수정 대상: answer

# P5 plugin reference split negative condition 수정 계획

## 수정 범위

- `workspace/develop/eval/plugin/answer/case-plugin-reference-split.yaml`

## 순서

1. target behavior에 negative conditions for skipped loading/use를 명시한다.
2. plugin bucket validator를 실행한다.
3. 수정 case targeted eval을 실행하고 pass run에 `validate_eval_run.py`를 실행한다.

## 완료 조건

- reference split case가 one-level reference 존재뿐 아니라 load/negative routing matrix를 평가한다.
