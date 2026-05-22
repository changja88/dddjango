수정 대상: evaluator

# 계획

1. renderer 회귀 테스트를 먼저 추가한다.
   - trace event agent message에 `/private/tmp/dddjango-eval-workspaces/...` 링크를 넣는다.
   - rendered HTML에 temporary workspace path가 남지 않아야 한다.

2. renderer를 수정한다.
   - `sanitize_report_value()`를 추가해 문자열, list, dict를 재귀 sanitize한다.
   - `trace_data()`가 raw trace를 그대로 반환하지 않고 sanitized trace를 반환하게 한다.

3. validator 회귀 테스트를 먼저 추가한다.
   - `검증: 실제 코드/테스트 실행은 하지 않았습니다.`는 실행 주장으로 보지 않아야 한다.

4. validator 부정 패턴을 수정한다.
   - 영어 표현은 단어 경계를 유지한다.
   - 한국어 `미실행`, `실행하지`, `하지 않았`, `안 했`, `안함`은 별도 alternation으로 매칭한다.

5. 검증한다.
   - 추가한 단일 테스트 red/green
   - 전체 `test_render_eval_review_html.py`
   - 전체 `test_validate_eval_run.py`
   - 실패했던 targeted run 재검증
