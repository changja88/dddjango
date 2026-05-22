수정 대상: answer

# DRF-to-Ninja answer reference trace 보강 분석

## 배경

implementation-django-ninja P4 재검토에서 `case-response-drf-ninja` answer가 DRF filtering/pagination compatibility를 요구하지만 bundled reference 중 `auth-pagination-filtering.md`를 직접 cite하지 않는 Minor가 확인됐다.

## 원인 분류

- 분류: `answer`
- source final과 required behavior는 filtering/pagination compatibility를 이미 다루지만, answer oracle의 bundled reference trace가 해당 세부 기준을 직접 가리키지 않아 검토자가 근거를 한 번 더 추적해야 한다.
- public case에는 private 기준이나 이전 run finding 누설이 없고, evaluator 구조 결함은 아니다.

## 조치

`workspace/develop/eval/response/answer/case-response-drf-ninja.yaml`의 `reference_basis`에 `dddjango/skills/implementation-django-ninja/references/auth-pagination-filtering.md`를 추가한다.

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 1, Major 0, 열린 Minor 1

Subagent 리뷰에서 남은 Blocker는 targeted eval pass evidence 부재이며, 이번 문서는 repo-side Minor를 닫기 위한 후속이다.
