수정 대상: answer

# runtime missing metadata answer 분석

## 배경

`case-runtime-missing-metadata` targeted run에서 with-ddjango는 metadata 영향과 prompt exposure 비교를 잘 설명했지만, answer oracle이 validation command output을 실제 artifact로 요구해 `pass-limited`가 됐다.

## 원인 분류

- 분류: `answer`
- 대상 case: `case-runtime-missing-metadata`
- 문제: public case는 어떤 파일/명령 결과를 증거로 남겨야 하는지 묻는 방법 설계 prompt다. 이 상황에서는 실제 validator 실행 output을 요구하기보다, 실행했다면 output을 첨부하고 실행하지 않았다면 exact command와 not-run marker를 남기도록 요구하는 것이 맞다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 수정 방향

answer oracle required behavior를 "validation command output or explicit not-run/proposed evidence marker"로 조정해 verification honesty를 유지한다.
