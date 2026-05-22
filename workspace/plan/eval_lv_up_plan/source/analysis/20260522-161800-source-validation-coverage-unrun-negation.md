수정 대상: evaluator
원인 분류: evaluator

# source validation-coverage unrun negation 분석

## 문제

`case-source-validation-coverage` run `20260522-140700-source-try01-targeted-source-validation-coverage`의 with-ddjango 응답 line 8은 expected evidence table에서 `실행했거나 못 한 검증 보고`를 요구했다.

이는 실제 validator 실행 주장이 아니라 실행 또는 미실행 보고를 남기라는 evidence 기준이다. 하지만 `validate_eval_run.py`의 generic execution claim detector는 `검증`과 `실행`만 보고 validator 실행 claim으로 오탐했고, 한국어 띄어쓰기형 부정 `못 한`을 negative marker로 인식하지 못했다.

## 영향

Coverage map의 expected evidence 표현이 실행 주장으로 잘못 실패하면 source bucket의 validation coverage case가 부당하게 막힌다. 실행 정직성 gate는 실제 완료 claim과 expected/not-run evidence guidance를 구분해야 한다.

## 조치 방향

- `test_validate_eval_run.py`에 `실행했거나 못 한 검증 보고` 회귀 테스트를 추가한다.
- `validate_eval_run.py`의 generic execution claim detector에 `못 한`/`못한` marker를 추가한다.
- 실패했던 source run을 재검증한다.

## 리뷰

리뷰 방식: not-run
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: 순차 fallback. 실패 line과 detector 조건을 직접 대조했다.

skill-creator 리뷰: 해당 없음. 이 문서는 source eval run validator 보강 분석이다.
