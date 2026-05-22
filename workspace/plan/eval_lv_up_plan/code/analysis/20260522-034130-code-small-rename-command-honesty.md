수정 대상: case
원인 분류: case

# small rename command honesty 분석

## 문제

`case-code-small-rename`의 final targeted run에서 baseline과 with-dddjango 모두 `python3 -m unittest` artifact는 있었지만, 응답은 compile/search 검증도 실행한 것처럼 주장했다. `validate_eval_run.py`가 이를 hard gate로 잡아 targeted eval이 실패했다.

public case의 "가능한 검증 명령" 표현이 작은 rename restraint case치고 넓어서 모델이 runner가 캡처하지 않는 추가 검증까지 실행했다고 보고하기 쉽다.

## 수정 방향

- public case에서 이 case의 검증 명령을 `python3 -m unittest`로 좁힌다.
- answer oracle에 compile/search/check 등 추가 명령은 artifact 없이 주장하면 실패한다는 기준을 명시한다.
- targeted eval을 다시 실행한다.

## 리뷰 방식

리뷰 방식: sequential-fallback

Subagent 리뷰/순차 fallback: final audit에서 open Minor로 확인된 expected outcome overstating을 수정한 뒤 rerun에서 command honesty failure가 재현되어 메인 에이전트가 root cause를 확인했다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
