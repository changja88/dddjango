수정 대상: case

# implementation-cleancode P4 coverage 수정 계획

## 범위

- `workspace/develop/eval/response/cases/plugin/public/`
- `workspace/develop/eval/response/answer/`

## 작업

1. `case-response-clean-code-refactor-boundary.md` public case를 추가한다.
   - 공개 문제는 legacy checkout/helper review-refactor 요청으로 작성한다.
   - answer-only field, private oracle 문구, 이전 run finding은 넣지 않는다.
2. `case-response-clean-code-refactor-boundary.yaml` answer oracle을 추가한다.
   - source reference, runtime skill, bundled references를 `reference_basis`로 명시한다.
   - required behavior에 findings-first review, responsibility separation, naming, function shape, encapsulation, abstraction/SOLID, knowledge-level DRY, error handling, Fat Schema/Router boundary, legacy characterization test를 포함한다.
   - forbidden behavior에 broad architecture rewrite, repository/UoW/hexagonal overreach, schema/router business logic 유지, unsupported verification/subagent claim을 둔다.
3. 기존 `case-response-fat-view-review.yaml`의 `reference_basis`를 `implementation-cleancode` 기준으로 보강한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- targeted eval 대표 case: `make eval-one BUCKET=response CASE=case-response-clean-code-refactor-boundary TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-cleancode-p4 EXTRA_ARGS=--rerun JOBS=1`
