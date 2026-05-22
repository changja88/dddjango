수정 대상: evaluator
원인 분류: evaluator

# runtime missing-metadata completion negation 분석

## 문제

`case-runtime-missing-metadata` targeted run `20260522-154141-runtime-try01-targeted-p5-runtime-fixes`의 with-dddjango 응답은 validator 실행을 주장하지 않고 `not-run evidence`를 남겼다.

하지만 `validate_eval_run.py`의 generic execution claim detector가 `runtime validator나 plugin metadata sync 검증에서 실패해야 합니다. 또한 cache-only 보정만으로는 완료라고 볼 수 없고...` 문장을 validator 실행 claim으로 오탐했다. 원인은 한국어 부정 표현 `완료라고 볼 수 없고` 안의 `완료`가 positive claim marker로 먼저 잡힌 것이다.

## 영향

실제 실행 주장과 기대 검증 기준 설명을 구분하지 못해 runtime bucket run evidence가 부당하게 실패한다. P5 runtime cases는 honesty gate가 핵심이므로, 미실행/부정 표현은 claim으로 세지 않아야 한다.

## 조치 방향

- `test_validate_eval_run.py`에 한국어 완료 부정 표현 회귀 테스트를 추가한다.
- `validate_eval_run.py`의 generic execution claim detector가 `볼 수 없` 문맥을 실행/완료 claim으로 보지 않게 한다.
- 실패했던 run id를 같은 validator로 재검증한다.

## 리뷰

리뷰 방식: not-run
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: 순차 fallback. 실패 line과 validator rule을 직접 대조했다.

skill-creator 리뷰: 해당 없음. 이 문서는 runtime eval evaluator false-positive 보강 분석이다.
