수정 대상: evaluator
원인 분류: evaluator

# code small rename unittest validator 분석

## 문제

`case-code-small-rename` targeted run `20260522-144829-code-try01-targeted-p5-opt-out-restraint`에서 baseline과 with-ddjango 모두 `python3 -m unittest` 실행 artifact와 event stream evidence가 있었는데도 `validate_eval_run.py`가 다음과 같이 실패했다.

- `output claims validator execution without matching event evidence`

## 원인

generic execution claim detector가 한국어 `검증`을 validator 실행 주장으로 넓게 감지한다. code final response의 `검증: python3 -m unittest`는 code check artifact와 command event로 뒷받침되는 정상 보고지만, generic validator evidence pattern이 `unittest`를 포함하지 않아 false positive가 발생했다.

## 조치 방향

- generic validator evidence pattern에 `unittest`를 추가한다.
- code output이 `python3 -m unittest` 검증을 보고하고 matching code check artifact가 있을 때 통과하는 회귀 테스트를 추가한다.

## 리뷰

리뷰 방식: sequential-fallback
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

Subagent 리뷰: 추가 subagent 실행 없음. 원인은 run artifact, code check artifact, validator 구현을 대조해 확인했다.
