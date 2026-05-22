수정 대상: answer

# code fat-model clean-code basis 분석

## 리뷰 방식

리뷰 방식: not-run

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 배경

`case-code-fat-model`은 "minimal clean-code refactor around model/service responsibilities and side-effect timing"을 검증한다. P4 목표에서는 related case/answer가 개별 skill 목적과 source reference를 정확히 검증해야 하므로, clean-code case라면 `implementation-cleancode` source/runtime basis가 직접 연결되어야 한다.

## 현재 증거

- `workspace/develop/eval/code/answer/case-code-fat-model.yaml`
  - intent와 target behavior는 responsibility split과 side-effect boundary를 검증한다.
  - `reference_basis`는 `code/eval_goal`, broad `workspace/develop/eval`, workflow role-map만 포함한다.
  - `workspace/reference/implementation-cleancode/reference/final.md`, runtime `implementation-cleancode/SKILL.md`, bundled `responsibility.md`가 빠져 있다.

## gap 분류

Major. answer oracle이 clean-code 목적을 검증하지만 source reference 연결이 약하다.

## 수정 방향

- broad `workspace/develop/eval` basis를 제거하거나 좁힌다.
- `workspace/reference/implementation-cleancode/reference/final.md`, `dddjango/skills/implementation-cleancode/SKILL.md`, `dddjango/skills/implementation-cleancode/references/responsibility.md`, `legacy-review.md`를 basis에 추가한다.
- side-effect timing은 workflow role-map보다 Django/transaction 쪽 기준이 더 직접적이면 별도 source로 보강하되, P4 clean-code scope에서는 최소 basis만 추가한다.
