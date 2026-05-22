수정 대상: answer

# P5 source eval traceability 수정 계획

## 수정 범위

- `workspace/develop/eval/source/answer/case-source-eval-traceability.yaml`

## 순서

1. required behavior를 per-case traceability proof 중심으로 구체화한다.
2. scoring/evidence에 run artifact/status mapping을 추가한다.
3. source bucket validator를 실행한다.
4. 수정 case targeted eval을 실행하고 pass run에 `validate_eval_run.py`를 실행한다.

## 완료 조건

- source traceability case가 bucket-level presence가 아니라 per-case public/answer/source/run 연결을 평가한다.
