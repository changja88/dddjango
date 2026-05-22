수정 대상: evaluator
원인 분류: evaluator

# response protocol prompt-input 검증 분석

## 문제

독립 리뷰에서 `validate_eval_run.py`는 prompt-input JSON array를 허용하도록 갱신됐지만, `validate_eval_protocol.py`는 여전히 prompt-input artifact를 JSON object로만 검증한다는 Minor가 나왔다.

response eval goal은 protocol validation을 completion gate로 언급하므로 두 validator의 prompt-input artifact shape 기준이 어긋나면 targeted run은 통과하지만 protocol 검증이 실패할 수 있다.

## 수정 방향

- `validate_eval_protocol.py`에 prompt-input 전용 JSON object-or-array validator를 추가한다.
- 일반 JSON artifact는 object-only 검증을 유지한다.
- `test_validate_eval_protocol.py`에 message-array prompt-input 회귀 테스트를 추가한다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 2, 열린 Minor 1

Subagent 리뷰/순차 fallback: 독립 P4 eval review subagent가 protocol consistency를 Minor로 보고했다. 본 분석은 해당 Minor를 닫기 위한 후속이다.

skill-creator 리뷰: validation integrity 관점에서 run validator와 protocol validator의 artifact contract를 맞춘다.
