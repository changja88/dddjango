수정 대상: evaluator
원인 분류: evaluator

# code eval 검증 주장 gate 분석

## 문제

최종 real subagent 리뷰에서 `case-code-python-state` 최신 run `20260522-032121-code-try01-targeted-implementation-python-p4`가 실제 check command는 `python3 -m unittest`인데 `with-ddjango` 응답은 `pytest` 실행을 주장했다는 Blocker가 확인됐다.

현재 `validate_eval_run.py`는 deterministic check artifact 존재와 answer-oracle JSON schema/expected outcome은 확인하지만, code response 텍스트가 특정 검증 도구 실행을 주장했을 때 해당 도구 command artifact가 있는지 직접 확인하지 않는다. 따라서 answer oracle evaluator가 놓친 false verification claim이 run validation을 통과할 수 있다.

## 수정 방향

- code bucket run validation에서 variant output의 검증 도구 claim을 스캔한다.
- `pytest`, `compileall`, `ruff`, `mypy`, `pyright` 같은 도구 실행/통과 주장에는 matching check command artifact가 있어야 한다.
- `not run`, `미실행`, `실행하지 않음` 같은 부정/미실행 보고는 실패로 보지 않는다.
- `case-code-python-state` public prompt에 실행한 검증 명령 이름을 정확히 보고하도록 명시한다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: final skill-creator review가 검증 주장 mismatch를 Blocker로 보고했다.

리뷰 결과: Blocker 1, Major 0, 열린 Minor 0
