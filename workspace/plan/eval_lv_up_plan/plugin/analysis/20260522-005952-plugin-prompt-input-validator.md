수정 대상: evaluator
원인 분류: evaluator

# plugin targeted eval prompt-input validator 분석

## 문제

`case-plugin-provisional-overclaim` targeted eval은 baseline/with-dddjango 실행과 answer oracle evaluation까지 생성했지만 `validate_eval_run.py`가 with-ddjango prompt-input artifact를 실패 처리했다.

실제 prompt-input debug output은 현재 Codex debug 형식상 top-level JSON array일 수 있다. 기존 validator는 해당 artifact를 JSON object로만 허용해, 유효한 prompt-input artifact를 구조 오류로 오판했다.

## 근거

- 실패 run: `20260522-005032-plugin-try01-targeted-source-status-stale`
- 실패 위치: `with-ddjango-prompt-input.json` artifact shape 검증
- root cause: artifact는 유효한 JSON array였고, validator가 object만 허용했다.
- answer oracle evaluation 자체는 `with_dddjango`를 pass로 판정했다.

## 수정 방향

- `validate_eval_run.py`의 prompt-input artifact 검증만 object 또는 array를 허용하도록 좁게 고친다.
- oracle, run meta, baseline isolation, workflow trace처럼 object schema가 필요한 artifact의 검증은 그대로 유지한다.
- `test_validate_eval_run.py`에 top-level message array prompt-input을 허용하는 회귀 테스트를 추가한다.

## 리뷰

리뷰 방식: not-run
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

수정 후 real-subagent 리뷰와 validator 재실행으로 확인한다.
