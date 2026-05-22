수정 대상: evaluator

# P5 plugin run validation honesty 계획

## 수정 범위

- 수정: `workspace/scripts/validate_eval_run.py`
- 수정: `workspace/scripts/test_validate_eval_run.py`

## 절차

1. 응답 line 단위로 validator, eval, browser, Serena 실행 완료 claim을 찾는다.
2. 부정/미실행 문맥은 허용한다.
3. claim이 있으면 같은 variant event stream에 대응 command/tool evidence가 있는지 확인한다.
4. evidence 없는 claim은 run validation failure로 처리한다.
5. unit test와 plugin targeted run validation을 재실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_run.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_run.py --bucket plugin --run-id 20260522-134130-plugin-try01-targeted-p5-workflow-integrity --case case-plugin-p5-workflow-integrity`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket plugin`

## 완료 조건

- unrun validator/eval/browser/Serena completion claim은 deterministic validator에서 실패한다.
- not-run/honesty wording은 계속 통과한다.
