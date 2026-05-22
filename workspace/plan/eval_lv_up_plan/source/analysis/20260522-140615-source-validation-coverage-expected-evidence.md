수정 대상: case

# source validation coverage expected evidence 분석

## 배경

`case-source-validation-coverage` targeted run `20260522-135100-source-try01-targeted-p5-source-remaining`에서 with-dddjango 결과가 `pass-limited`로 판정됐다. 출력은 coverage map을 제안했지만 source-reference-audit가 요구하는 `expected evidence` 열을 명시하지 않았다.

## 원인 분류

- 분류: `case`
- 대상 case: `case-source-validation-coverage`
- 문제: public case가 coverage map을 요구하지만 expected evidence column을 명시하지 않아 모델이 일반 coverage 표로 답해도 자연스러운 여지가 있다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

## 수정 방향

public case에 coverage map의 필수 열로 expected evidence를 명시한다. 이는 source skill의 공개 동작 기준이며 answer oracle 누설이 아니다.
