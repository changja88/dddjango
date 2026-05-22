수정 대상: evaluator

# P5 runtime semantic validator 분석

## 배경

runtime bucket은 stale cache, wrong routing, missing metadata, private material, prompt exposure 같은 P5 governance case를 갖지만 validator는 missing metadata case에만 특화된 semantic check를 제공한다.

## 원인 분류

- 분류: `evaluator`
- 문제: wrong-routing answer가 web skill metadata를 빠뜨려도 structural validator가 잡지 못한다. stale-cache와 cache/source consistency도 목표 대비 semantic check가 약하다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 수정 방향

runtime wrong-routing과 stale-cache answer semantic validator를 추가해 role-map, implementation-django-web metadata, prompt-input/cache-source evidence가 빠지면 실패하게 한다.
