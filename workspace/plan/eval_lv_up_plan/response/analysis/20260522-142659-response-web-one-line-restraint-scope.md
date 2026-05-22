수정 대상: answer
원인 분류: answer

# response one-line web restraint scope 분석

## 문제

`case-response-django-web-one-line-edit`는 한 줄 Django Web template copy edit restraint를 다루지만 P5 plugin-level restraint처럼 분류되어 있다. 실제 요구는 full workflow/plugin restraint가 아니라 individual-skill/supporting restraint다.

## 영향

P5 plugin-level restraint와 P4 individual-skill restraint가 섞여 보인다. P5 목표의 "작은 rename, tiny assertion, one-line web edit 과적용 방지"는 필요하지만, 이 case 자체를 full P5 integration evidence로 세면 안 된다.

## 조치 방향

- intent를 individual-skill/supporting restraint로 정리한다.
- `restraint_scope: individual-skill`로 바꾼다.
- `p5-plugin-restraint` tag를 제거한다.
- validator의 known restraint scope map에 이 case를 추가한다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: `Noether` subagent가 classification gap을 Major로 보고했다.

skill-creator 리뷰: 해당 없음. 이 문서는 response answer classification 수정 분석이다.
