수정 대상: case

# small rename command honesty 수정 계획

## 수정 대상

- `workspace/develop/eval/code/cases/plugin/public/case-code-small-rename.md`
- `workspace/develop/eval/code/answer/case-code-small-rename.yaml`

## 절차

1. public case의 검증 요청을 `python3 -m unittest`로 제한한다.
2. answer oracle의 hard gate와 evidence를 unittest 중심으로 맞추고, 캡처되지 않은 compile/search/check 주장을 금지한다.
3. code bucket validator를 실행한다.
4. targeted eval을 다시 실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `make eval-one BUCKET=code CASE=case-code-small-rename TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- public prompt가 과도한 검증 주장을 유도하지 않는다.
- targeted eval이 pass한다.
