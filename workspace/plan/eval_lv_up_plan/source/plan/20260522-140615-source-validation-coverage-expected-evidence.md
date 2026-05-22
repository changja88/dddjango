수정 대상: case

# source validation coverage expected evidence 수정 계획

## 수정 범위

- `workspace/develop/eval/source/cases/plugin/public/case-source-validation-coverage.md`

## 순서

1. public case에 expected evidence column 요구를 추가한다.
2. source bucket validator를 실행한다.
3. 해당 case targeted eval을 재실행한다.
4. pass run에 `validate_eval_run.py`를 실행한다.

## 완료 조건

- with-ddjango 결과가 expected evidence를 포함한 coverage map을 작성해 pass verdict를 받는다.
