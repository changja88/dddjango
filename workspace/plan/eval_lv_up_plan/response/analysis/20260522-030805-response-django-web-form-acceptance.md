수정 대상: case
원인 분류: case

## 배경

P4 최종 독립 리뷰에서 `case-response-django-web-page` targeted run의 answer-oracle evaluation이 `with-dddjango`를 pass로 판정하면서도 invalid POST, error rendering, `ModelForm.Meta.fields` 명시가 약하다고 적은 점을 Minor로 지적했다.

## 문제

- answer oracle은 web form의 GET, valid POST, invalid POST, error rendering, `ModelForm.Meta.fields`를 required로 둔다.
- public case는 `web form`을 일반 표현으로만 요청해, 모델 출력과 oracle required detail 사이에 유도 강도 차이가 있었다.
- scoring check도 해당 form subpath 누락을 pass 금지 조건으로 충분히 강조하지 않았다.

## 수정 방향

- public case의 web form bullet에 GET, valid POST, invalid POST, error rendering, `ModelForm.Meta.fields` 명시를 공개 요구로 추가한다.
- answer scoring check에 form subpath 누락 시 fail 조건을 추가한다.

## 리뷰 기록

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

Subagent 리뷰/순차 fallback: 독립 P4 re-review가 residual evaluator-strength gap을 Minor로 보고했다.
