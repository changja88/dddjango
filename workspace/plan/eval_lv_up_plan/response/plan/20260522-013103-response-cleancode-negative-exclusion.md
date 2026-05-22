수정 대상: case

# implementation-cleancode negative exclusion 수정 계획

## 범위

- `workspace/develop/eval/response/cases/plugin/public/`
- `workspace/develop/eval/response/answer/`

## 작업

1. `case-response-clean-code-tiny-naming.md` public case를 추가한다.
   - 공개 문제는 tiny naming/one-line request로 작성한다.
   - answer-only field, private oracle, prior run finding을 넣지 않는다.
2. matching answer oracle을 추가한다.
   - required behavior: 짧은 직접 답변, 필요하면 한두 개 naming option, refactor/review/workflow/subagent ceremony 금지.
   - forbidden behavior: findings-first full review, role map, broad clean-code lecture, file inspection/test/subagent claim.
3. clean-code P4 coverage validator에 `clean-code-exclusion`, `tiny-task-restraint`를 포함한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- targeted eval은 response bucket representative clean-code case 또는 negative case 중 하나로 실행한다. 현재 app-server sandbox 실패가 있어 외부 eval 실행은 별도 승인 필요.
