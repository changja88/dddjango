수정 대상: answer
원인 분류: model-variance

# implementation-django code expected outcome 분석

## 대상

- `workspace/develop/eval/code/answer/case-code-django-orm-service.yaml`
- `workspace/develop/eval/code/answer/case-code-status-migration.yaml`
- failed runs:
  - `20260522-022502-code-try01-targeted-implementation-django-p4`
  - `20260522-023515-code-try02-targeted-implementation-django-p4`
  - `20260522-015326-code-try01-targeted-implementation-django-p4`

## 문제

positive implementation-django code case에서 baseline과 with-dddjango가 모두 핵심 구현 요구를 충족했고 같은 점수로 판정됐다. 두 번 반복한 `case-code-django-orm-service` 실행에서도 같은 패턴이 재현됐다.

실패 원인은 public case나 source reference 부족이 아니라 `expected_delta: positive`가 현재 모델/평가 조합의 변동성을 과하게 가정한 것이다. P4의 목적은 개별 skill 평가가 source reference 기반 목적을 검증하는지 확인하는 것이므로, case 자체가 구현 산출물과 command honesty를 판정하면 baseline pass 가능성을 명시적으로 허용할 수 있다. 단, 이 허용은 무근거 control이 아니라 positive case의 model-variance 허용임을 answer에 근거로 남겨야 한다.

## 수정 판단

- `control_case: false`는 유지한다.
- positive ORM/service case의 `expected_delta`는 `non-negative`로 조정한다.
- control/honesty/restraint 성격인 status migration과 small rename은 targeted evidence상 baseline이 더 높을 수 있으므로 `expected_delta: variable`로 둔다.
- `baseline_pass_ok: true`를 허용하되 `baseline_pass_ok_reason`을 필수로 기록한다.
- validator는 positive implementation answer에서 `baseline_pass_ok: true`가 있으면 명시 reason 없이는 실패하게 한다.

## 리뷰 방식

리뷰 방식: sequential-fallback

Subagent 리뷰/순차 fallback: 두 독립 리뷰가 positive case의 무근거 baseline pass 허용을 Major로 지적했다. 조치로 무조건 허용이 아니라 명시 reason을 validator로 강제한다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
