수정 대상: case

# implementation-tdd P4 response 직접 coverage 계획

## 수정 범위

- `workspace/develop/eval/response/cases/plugin/public/case-response-tdd-loop-selection.md`
- `workspace/develop/eval/response/answer/case-response-tdd-loop-selection.yaml`

## 수정 순서

1. public case는 answer oracle, private 기준, 이전 run finding을 드러내지 않고 TDD 설계 요청만 담는다.
2. answer oracle은 source reference, runtime `SKILL.md`, bundled references 5개를 모두 근거로 둔다.
3. target behavior는 test list, failing-test-first, Red-Green-Refactor, Inside-Out/Outside-In, acceptance/unit loop, boundary cases, refactor checkpoint, state vs behavior, mock role, BDD/ATDD handoff, validation honesty를 요구한다.
4. forbidden behavior는 pytest-bdd/Gherkin/fixture/factory mechanics를 `implementation-tdd`가 직접 맡는 오답, DB/API/Django 구현 설계 과적용, 실행하지 않은 Red/Green claim으로 둔다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- targeted eval:
  - `make eval-one BUCKET=response CASE=case-response-tdd-loop-selection TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-tdd-p4 EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- 새 response case와 answer가 같은 implementation-tdd 목적을 검증한다.
- public prompt에 evaluator-only 필드, private 기준, 이전 run finding이 없다.
- answer oracle이 reference보다 과도하거나 부족한 요구를 하지 않는다.
- targeted eval run id/status가 기록된다.

