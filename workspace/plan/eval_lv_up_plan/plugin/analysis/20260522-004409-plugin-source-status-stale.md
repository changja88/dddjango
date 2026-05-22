수정 대상: case
원인 분류: case

# plugin provisional status case 분석

## 문제

`architecture-implementation-patterns`는 현재 `workspace/reference/architecture-implementation-patterns/reference/final.md` 전용 source reference와 runtime bundled references를 갖고 있다. 하지만 `plugin` bucket의 provisional handling goal/case/answer는 여전히 `architecture-implementation-patterns`, `implementation-django-ninja`, `implementation-django-web`를 전용 source reference가 부족한 provisional skill로 고정한다.

이 상태는 현재 source reference보다 부족하거나 반대되는 answer oracle을 요구한다.

## 영향

- P4 기준 4: answer oracle이 현재 reference 상태보다 부족한 요구를 한다.
- P4 기준 5: case와 answer가 source reference 기반 skill 목적 대신 오래된 provisional 상태를 검증한다.
- public case가 특정 결론을 유도하는 표현을 포함해 현재 상태 분류를 평가하기 어렵다.

## 수정 방향

- plugin provisional case를 "세 skill의 현재 source/reference status를 분류하고, dedicated source가 있는 skill과 source gap이 있는 skill을 구분하라"는 요청으로 바꾼다.
- answer oracle은 dedicated `final.md`가 존재하고 주요 판단 축을 다루는 경우 provisional로 부르지 말 것을 요구한다.
- `eval_goal.md`의 provisional handling 설명도 특정 skill을 고정하지 않고, source가 없는 skill을 조건부로 다루도록 갱신한다.

## 리뷰

리뷰 방식: not-run
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

수정 후 real-subagent 리뷰에서 source status와 validation integrity를 재확인한다.
