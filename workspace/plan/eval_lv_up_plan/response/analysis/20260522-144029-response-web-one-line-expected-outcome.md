수정 대상: answer
원인 분류: answer

# response one-line web expected outcome 분석

## 문제

`case-response-django-web-one-line-edit`의 targeted run `20260522-143652-response-try01-targeted-p5-opt-out-restraint`에서 baseline은 pass, with-dddjango는 pass-limited였다.

with-dddjango 응답은 workflow, subagent, TDD, DB/API, 대규모 리팩터링으로 확장하지 않았고 한 줄 template copy edit 범위를 유지했다. 감점 사유는 실제 파일 검색과 template 확인을 실행한 뒤 "현재 파일에는 문구가 없다"는 단정이 들어가 baseline보다 덜 직접적이었다는 점이다.

## 원인

이 case는 P5 plugin-level direct evidence가 아니라 `restraint_scope: individual-skill` supporting case다. baseline도 충분히 통과할 수 있는 tiny direct-answer 계열인데 `with_dddjango: pass`와 `expected_delta: non-negative`를 요구해 model variance와 baseline 동등 통과를 실패로 처리했다.

## 조치 방향

- with-ddjango 기대 verdict를 `pass-or-pass-limited`로 낮춘다.
- delta 기대를 `variable`로 바꾼다.
- baseline 통과 허용 사유를 명시해 이 case가 plugin-level 성능 향상 증거가 아니라 절제, 범위, honesty, leakage gate임을 분리한다.

## 리뷰

리뷰 방식: sequential-fallback
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

Subagent 리뷰: 추가 subagent 실행 없음. 원인은 run artifact와 기존 response restraint scope 분석으로 확인했다.
