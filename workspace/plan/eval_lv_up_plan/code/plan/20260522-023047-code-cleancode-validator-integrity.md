수정 대상: evaluator

# code clean-code validator integrity 수정 계획

## 범위

- `workspace/develop/eval/code/answer/case-code-fat-model.yaml`
- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`
- 모순된 기존 analysis 문서의 리뷰 결과 요약

## 작업

1. `case-code-fat-model.yaml`에 `implementation-cleancode` coverage tag를 추가한다.
2. code bucket에서 `implementation-cleancode` tag가 있는 answer를 검증하는 함수를 추가한다.
   - `workspace/reference/implementation-cleancode/reference/final.md`
   - `dddjango/skills/implementation-cleancode/SKILL.md`
   - 하나 이상의 bundled implementation-cleancode reference
   - responsibility split, side-effect boundary, regression test, overengineering restraint terms
3. `validate_answer()`의 code branch에서 새 검증을 호출한다.
4. unit test를 추가한다.
5. stale analysis 문서의 리뷰 결과 요약을 Major/Minor 분류와 맞춘다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- 필요 시 `case-code-fat-model` targeted eval 재실행

## 완료 조건

- code bucket clean-code supporting case가 source/runtime basis drift를 validator에서 잡는다.
- 독립 리뷰 Major가 닫힌다.
- 남은 열린 Minor가 없다.
