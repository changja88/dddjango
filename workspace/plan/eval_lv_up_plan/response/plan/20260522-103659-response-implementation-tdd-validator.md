수정 대상: evaluator

# implementation-tdd P4 response validator 계획

## 수정 범위

- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 수정 순서

1. `RESPONSE_IMPLEMENTATION_TDD_P4_COVERAGE_TAGS`를 추가한다.
2. `has_implementation_tdd_direct_coverage`를 추가해 다음을 확인한다.
   - case id prefix: `case-response-tdd-`
   - source basis: `workspace/reference/implementation-tdd/reference/final.md`
   - runtime basis: `dddjango/skills/implementation-tdd/SKILL.md`
   - bundled reference: `dddjango/skills/implementation-tdd/references/*.md`
   - 필수 coverage tags 전체 포함
3. `validate_implementation_tdd_answer`를 추가해 target behavior가 필수 TDD 축을 required text에 포함하는지 확인한다.
4. response coverage gate가 direct case 없음을 finding으로 보고하게 한다.
5. unit test는 missing direct coverage, missing source/runtime/bundled basis, required term omission, valid direct case를 확인한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`

## 완료 조건

- implementation-tdd P4 직접 coverage 누락이 validator finding으로 잡힌다.
- direct answer가 source/runtime/bundled basis와 필수 target behavior를 갖출 때 validator가 통과한다.

