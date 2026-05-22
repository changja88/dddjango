수정 대상: case

# implementation-cleancode P4 coverage 분석

## 배경

`implementation-cleancode` P4 목표는 개별 skill 평가가 maintainability, review/refactor, responsibility separation, naming, function shape, encapsulation, abstraction, SOLID, duplication/DRY, error handling, Fat Model/View/Router/Schema 기준을 reference 기반으로 검증하는지 확인하는 것이다.

## 현재 증거

- `workspace/develop/eval/response/answer/case-response-fat-view-review.yaml`
  - Fat Model, View/Router, findings-first review를 검증한다.
  - 그러나 `reference_basis`가 `dddjango/skills/source-reference-audit/SKILL.md`를 가리켜 clean-code runtime/source 기준과 직접 연결되지 않는다.
  - coverage tag도 `clean-code`, `view-logic-review`, `fat-model-review`에 머물러 naming, function shape, encapsulation, abstraction, SOLID, duplication/DRY, error handling, Fat Schema, legacy refactoring을 직접 표시하지 않는다.
- `workspace/develop/eval/response/answer/case-response-simple-rename.yaml`
  - simple negative/restraint는 검증하지만 clean-code 사용 조건과 제외 조건을 직접 검증한다고 보기 어렵다.
- `workspace/develop/eval/code/answer/case-code-fat-model.yaml`
  - 실제 코드 변경에서 responsibility split과 side-effect timing을 검증한다.
  - 하지만 P4의 broad clean-code review/refactor 판단 축 전체를 response answer oracle에서 직접 덮지는 않는다.

## gap 분류

Major. 관련 positive case는 있으나 coverage가 Fat Model/View 중심이라 개별 skill 목적 전체를 검증하기에는 부족하다. public case/answer를 추가하고 기존 answer의 source basis를 보강해야 한다.

리뷰 방식: not-run

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 수정 방향

- response bucket에 clean-code review/refactor 전용 public case와 answer oracle을 추가한다.
- 새 case는 공개 문제에서 review/refactor 요청만 드러내고 answer oracle, private 기준, prior run finding은 포함하지 않는다.
- answer oracle은 `workspace/reference/implementation-cleancode/reference/final.md`, runtime `implementation-cleancode/SKILL.md`, bundled references를 직접 basis로 둔다.
- 기존 Fat View case answer는 reference basis를 clean-code skill/source로 바로 잡는다.
