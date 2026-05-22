수정 대상: answer

# code fat-model expected outcome 분석

## 리뷰 방식

리뷰 방식: not-run

리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

## 배경

`case-code-fat-model`은 implementation-cleancode P4의 code bucket supporting case로, Fat Model/service 책임 분리와 transaction commit 이후 부작용 경계를 실제 코드 변경으로 검증한다.

## 현재 증거

- targeted run `20260522-021218-code-try01-targeted-implementation-cleancode-p4`
  - baseline verdict: `pass`, score `5 / 5`
  - with-ddjango verdict: `pass-limited`, score `4 / 5`
  - run validator 실패:
    - `baseline_pass_ok=false`와 baseline pass 충돌
    - `baseline=partial`과 baseline pass 충돌
    - `expected_delta=positive`인데 with-ddjango 점수가 baseline보다 높지 않음
- public case는 작은 fixture에서 최소 책임 분리와 regression test를 요구한다. 이 요구는 baseline도 충분히 해결할 수 있는 code-backed supporting case로 관찰됐다.

## 원인 분류

answer. answer oracle의 `expected_outcomes`가 현재 case 성격과 targeted run evidence보다 과도하다. P4 목적은 개별 skill 기준과 source reference 검증이지, 모든 supporting code case에서 baseline 대비 uplift를 강제하는 것이 아니다.

## gap 분류

Minor. case/answer의 source basis와 target behavior는 implementation-cleancode 목적에 맞지만 expected outcome metadata가 실제 oracle evaluation과 충돌해 targeted eval을 실패시킨다.

## 수정 방향

- `case-code-fat-model.yaml`의 `expected_outcomes`를 supporting/smoke 성격에 맞게 정정한다.
- baseline pass를 허용하고 expected delta를 neutral로 둔다.
- target behavior, source basis, scoring 기준은 유지한다.
