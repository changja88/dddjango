수정 대상: answer

# P5 runtime wrong-routing basis 분석

## 배경

독립 source-governance review에서 `case-runtime-wrong-routing`이 Django TemplateView/web routing을 검증하면서도 `implementation-django-web` skill metadata와 bundled web references를 `reference_basis`에 직접 포함하지 않는다고 지적했다.

## 원인 분류

- 분류: `answer`
- 대상 case: `case-runtime-wrong-routing`
- 문제: role-map과 source-reference-audit boundary만으로는 template/static/web 요청에서 실제 web skill metadata가 노출되고 선택되어야 한다는 runtime routing 근거가 약하다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 수정 방향

`implementation-django-web`의 `SKILL.md`, `agents/openai.yaml`, template/static bundled references를 answer basis와 expected evidence에 추가한다.
