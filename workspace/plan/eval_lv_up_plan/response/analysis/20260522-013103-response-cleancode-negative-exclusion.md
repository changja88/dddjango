수정 대상: case

# implementation-cleancode negative exclusion 분석

## 리뷰 방식

리뷰 방식: not-run

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 배경

P4 기준은 positive case뿐 아니라 사용 조건과 제외 조건도 검증해야 한다. `implementation-cleancode`는 maintainability review/refactor가 중심일 때 사용하고, tiny naming, typo-only, formatter-only, one-line explanation 요청은 직접 처리해야 한다.

## 현재 증거

- `case-response-clean-code-refactor-boundary`는 positive review/refactor case를 덮는다.
- `case-response-simple-rename`은 workflow/subagent ceremony restraint를 검증하지만 `implementation-cleancode` 제외 조건 자체가 reference basis에 없다.
- `case-code-small-rename`은 code-producing control case라 response routing/exclusion을 직접 검증하지 않는다.

## gap 분류

Major. clean-code positive coverage는 생겼지만 tiny naming/typo/formatter/one-line explanation 제외 조건을 직접 검증하는 response case가 없다.

## 수정 방향

- response bucket에 clean-code exclusion 전용 public case와 answer oracle을 추가한다.
- 공개 문제는 짧은 이름 질문으로 만들고, review/refactor ceremony가 필요 없다는 사용자 범위를 명확히 한다.
- answer oracle은 `implementation-cleancode` SKILL.md 제외 조건과 eval goal negative case를 basis로 둔다.
- coverage tag에 `clean-code-exclusion`과 `tiny-task-restraint`를 추가하고, evaluator가 이 tag를 요구하도록 한다.
