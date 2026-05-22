수정 대상: skill
원인 분류: skill

# implementation-django-ninja P5 TestClient metadata 분석

## 문제

P5 skill-creator 관점 리뷰에서 `implementation-django-ninja/agents/openai.yaml`의 short description이 "테스트 구현"이라고 표현해 Ninja adapter skill이 pytest/test implementation 책임까지 갖는 것처럼 보일 수 있다고 지적했다.

`SKILL.md` 본문은 Django Ninja Router/Schema endpoint adapter와 TestClient acceptance criteria를 다루고, pytest fixture/mock/factory mechanics는 `implementation-test`로 넘긴다. 따라서 UI metadata도 같은 책임 경계를 반영해야 한다.

## 영향

API 구현은 architecture-api 계약과 implementation-django-ninja adapter 책임을 구분해야 하고, test/TDD는 테스트 절차와 pytest mechanics를 분리해야 한다. metadata가 "테스트 구현"을 말하면 P5 boundary 평가에서 Minor ambiguity가 남는다.

## 조치 방향

- short description에서 "테스트 구현"을 제거한다.
- Django Ninja skill의 책임을 Router, Schema, 오류, TestClient 기준으로 제한해 표현한다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

Subagent 리뷰/순차 fallback: `Herschel` subagent가 metadata wording ambiguity를 Minor로 보고했다.

skill-creator 리뷰: `Herschel` subagent가 skill metadata와 SKILL.md 본문 책임 경계를 비교했다. 메인 판단은 metadata 표현만 좁게 수정하면 충분하다.
