수정 대상: evaluator

# implementation-django-ninja P4 리뷰 후속 수정 분석

## 배경

독립 P4 감사에서 repo-side로 수정 가능한 Major 2건과 Minor 1건이 확인됐다.

## 발견

1. `case-response-drf-ninja`의 `evidence_required`가 response bucket goal의 evidence capture 기준보다 좁다.
2. `has_implementation_django_ninja_direct_coverage()`가 P5/workflow/subagent tag를 명시적으로 제외하지 않아, 향후 P5-adjacent case가 P4 direct coverage를 닫을 수 있다.
3. implementation-django-ninja semantic term check가 `schema`만으로 `schema-modelschema`, `auth`만으로 `auth-permission`, `filter`만으로 `filtering-sorting`을 통과시킬 수 있다.

## 원인 분류

- 분류: `answer`, `evaluator`
- case public leakage나 source reference 부족은 아니다.
- targeted eval Blocker는 별도 `sandbox/authorization` 문제이며 이 수정으로 pass evidence가 생기지는 않는다.

## 조치

- DRF-to-Ninja answer의 required evidence를 response bucket evidence list와 맞춘다.
- Django Ninja direct coverage gate에 workflow/subagent/P5 tag exclusion을 추가한다.
- semantic term validator를 paired dimension 단위로 강화한다.

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 1, Major 2, 열린 Minor 1

Subagent 리뷰/순차 fallback: 독립 P4 auditor가 targeted eval pass evidence 부재 Blocker와 repo-side Major/Minor를 보고했다. 이 문서는 repo-side Major/Minor를 닫기 위한 후속이다.
