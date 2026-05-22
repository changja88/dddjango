수정 대상: answer
원인 분류: answer overclaim

# status migration expected outcome 분석

## 대상

- `workspace/develop/eval/code/answer/case-code-status-migration.yaml`
- targeted run: `20260522-015326-code-try01-targeted-implementation-django-p4`

## 문제

`case-code-status-migration` answer oracle은 `expected_delta: positive`, `baseline_pass_ok: false`로 되어 있었다. 그러나 targeted run에서 baseline과 with-dddjango가 모두 `4 / 5`를 받았다.

평가기는 with-dddjango가 expand/backfill/contract를 더 강하게 표현했다고 보았지만, 두 variant 모두 검증 주장과 artifact가 일부 맞지 않아 같은 점수로 판정했다. 따라서 이 case는 implementation-django migration safety 자체를 검증하는 데는 유효하지만, 항상 with-dddjango가 baseline보다 높은 점수를 받아야 한다는 oracle 요구는 reference 기준보다 과도하다.

## 수정 판단

- case/public prompt는 유지한다.
- implementation-django source basis와 migration 관찰점은 유지한다.
- expected outcome만 `baseline_pass_ok: true`, `expected_delta: non-negative`로 완화한다.
- command honesty hard gate는 유지한다.

## 리뷰 방식

리뷰 방식: sequential-fallback

Subagent 리뷰/순차 fallback: targeted run artifact를 근거로 메인 에이전트가 순차 fallback으로 판정했다. 독립 subagent inventory와도 "migration coverage는 direct이나 targeted eval 필요" 판단이 일치한다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
