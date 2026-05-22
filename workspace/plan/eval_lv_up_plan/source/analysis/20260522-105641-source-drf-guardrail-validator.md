수정 대상: evaluator
원인 분류: evaluator undercheck

# source DRF guardrail validator 분석

## 문제

P4 real-subagent review에서 `case-source-provisional-drf` answer와 source bucket validator가 DRF guardrail source decision을 충분히 보호하지 못한다는 Major가 확인됐다.

## 근거

- `workspace/reference/source-reference-audit/reference/final.md`는 DRF guardrail을 source-reference-audit area가 소유하는 governance decision으로 두고, 다음 축을 별도로 trace하라고 정한다.
  - greenfield Django Ninja 구현 기준
  - framework-neutral `architecture-api` REST/API contract 기준
  - existing DRF maintenance/migration을 다루는 `implementation-django` 기준
  - runtime routing skill surface
- 기존 `case-source-provisional-drf` answer는 DRF가 legacy/migration/comparison only라고 요구하지만 `architecture-api`, `implementation-django`, runtime routing skill surface를 직접 reference basis로 들지 않았다.
- 기존 `validate_eval_bucket_pack.py`는 source bucket에 broad coverage tag만 요구하고 `provisional-handling` + `drf-guardrail` answer의 semantic terms를 구조적으로 검사하지 않았다.

## 대상

| bucket | case id | public | answer | evaluator 관련성 | 수정 여부 | targeted eval 필요 |
|---|---|---|---|---|---|---|
| source | `case-source-provisional-drf` | 변경 없음 | DRF guardrail source/runtime axes 보강 | source-specific semantic validator 추가 | answer/evaluator 수정 | 예 |
| source | bucket goal | 해당 없음 | 해당 없음 | provisional handling wording 보강 | eval_goal 수정 | 아니오 |

## 수정 방향

- `case-source-provisional-drf.yaml`의 `reference_basis`에 `architecture-api`, `implementation-django`, runtime routing `SKILL.md` surfaces를 추가한다.
- `target_behavior.required`가 DRF guardrail을 API contract, greenfield Django Ninja, existing DRF maintenance/migration, runtime routing row로 분리하도록 요구한다.
- `validate_eval_bucket_pack.py`에 source provisional/DRF answer semantic validator를 추가하고 regression test를 먼저 작성한다.
- `source/eval_goal.md` provisional handling wording을 `final.md` existence + substantive coverage로 맞춘다.

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 2, 열린 Minor 1

Subagent 리뷰/순차 fallback: 독립 review가 DRF guardrail answer under-spec, source validator undercheck, eval goal wording weakness를 보고했다. 메인 판단도 source reference와 대조해 채택한다.
