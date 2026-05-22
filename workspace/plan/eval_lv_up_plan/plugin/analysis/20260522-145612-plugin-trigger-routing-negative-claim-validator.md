수정 대상: evaluator
원인 분류: evaluator

# plugin trigger-routing negative claim validator 분석

## 문제

`case-plugin-trigger-routing` pass run `20260522-142000-plugin-try01-targeted-p5-opt-out-restraint`를 현재 validator로 재검증하자 with-ddjango 응답의 라우팅 제외 문장을 실행 주장으로 오인했다.

검증 실패 문장:

- `평가 실행, evaluator/validator 구현, 애플리케이션 검증은 이 skill이 아님`

## 원인

generic execution claim detector는 `eval`, `validator`, `검증`, `실행`을 감지하지만, 한국어 부정 표현 `아님`, `아닌`을 negative marker로 보지 않았다. 따라서 "이 skill이 아님"이라는 exclusion guidance를 eval/validator 실행 claim으로 잘못 분류했다.

## 조치 방향

- generic execution negative pattern에 `아님`, `아닌`을 추가한다.
- 같은 라우팅 제외 문장이 pass하는 회귀 테스트를 추가한다.

## 리뷰

리뷰 방식: sequential-fallback
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

Subagent 리뷰: 추가 subagent 실행 없음. 원인은 run output line과 validator pattern을 대조해 확인했다.
