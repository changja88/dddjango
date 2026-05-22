수정 대상: evaluator

# implementation-cleancode semantic validator 수정 계획

## 범위

- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 작업

1. clean-code response answer validator를 추가한다.
2. `implementation-cleancode` tag가 있으면 다음 reference path를 요구한다.
   - `workspace/reference/implementation-cleancode/reference/final.md`
   - `dddjango/skills/implementation-cleancode/SKILL.md`
3. `clean-code-exclusion` tag가 있으면 `dddjango/skills/implementation-cleancode/SKILL.md` basis와 `target_behavior`의 brief/direct/no ceremony 성격을 요구한다.
4. positive answer에는 `responsibility`, `naming`, `function`, `encapsulation`, `dry`, `error`, `schema` 또는 동등한 핵심 term이 target/scoring/failure text에 있는지 확인한다.
5. unit test로 basis 누락을 실패시킨다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
