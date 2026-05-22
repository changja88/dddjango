수정 대상: evaluator

# implementation-cleancode semantic validator 분석

## 리뷰 방식

리뷰 방식: not-run

리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

## 배경

새 P4 validator는 clean-code coverage tag 누락을 잡지만, tag만 있으면 source/reference basis가 비어도 통과할 수 있다. P4 목표는 case, answer, evaluator가 같은 skill 목적을 검증하는지 확인하므로 최소한 tagged answer가 clean-code source/runtime basis를 갖는지 구조적으로 검증해야 한다.

## 현재 증거

- `RESPONSE_IMPLEMENTATION_CLEANCODE_P4_COVERAGE_TAGS`는 bucket-level tag 집합만 강제한다.
- `case-response-clean-code-refactor-boundary`는 충분한 basis를 갖지만, validator가 이를 보장하지 않는다.
- `case-response-fat-view-review`는 review 과정에서 broad basis가 발견되어 수정이 필요했다.

## gap 분류

Minor. 현재 case는 수동 검토로 정렬됐지만 evaluator enforcement가 약하다.

## 수정 방향

- `implementation-cleancode` 또는 `clean-code-exclusion` tag가 있는 response answer에 대해 clean-code runtime/source basis를 요구한다.
- positive clean-code answer에는 핵심 behavior term 일부를 요구한다.
- exclusion answer에는 `implementation-cleancode/SKILL.md` basis와 forbidden overreach terms를 요구한다.
- unit test를 추가한다.
