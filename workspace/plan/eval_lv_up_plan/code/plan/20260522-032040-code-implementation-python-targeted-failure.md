수정 대상: case

# implementation-python code targeted eval 실패 수정 계획

## 수정 대상

- `workspace/develop/eval/code/cases/plugin/public/case-code-python-state.md`
- `workspace/develop/eval/code/answer/case-code-python-state.yaml`

## 절차

1. public case에 허용 변경 범위를 명시한다.
2. public case에 실행한 검증만 보고하라는 검증 정직성 조건을 추가한다.
3. answer oracle의 allowed_paths를 public case와 맞춘다.
4. code bucket validator를 실행한다.
5. targeted eval `case-code-python-state`를 재실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `make eval-one BUCKET=code CASE=case-code-python-state TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-python-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- case, answer, evaluator가 같은 변경 범위와 verification honesty 기준을 검증한다.
- targeted eval이 pass 상태로 남는다.
