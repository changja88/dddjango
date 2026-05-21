수정 대상: reference

# source-reference-audit P1 reference 분석

## 평가 요약

`workspace/reference/source-reference-audit/reference/final.md`는 artifact role, path boundary, leakage category, run artifact status, boundary scan evidence, public wording, validation expectation을 제공한다. 그러나 P1 기준에서 요구한 source/reference governance, final/review/internal/external material, runtime metadata, provenance, source gap, provisional/fallback, DRF guardrail, validation coverage, eval traceability를 모두 판단하기에는 source decision이 부족하다.

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 2, 열린 Minor 0

Subagent 리뷰/순차 fallback: real-subagent 2개를 실행했다. skill-creator 관점 리뷰는 Blocker 0, Major 0, Minor 1을 보고했으며, 해당 Minor는 skill validation 자동화 강도에 대한 선택 개선으로 P1 종료 전 필수 수정은 아니라고 판정했다. 독립 P1 리뷰는 source reference gap Major 2건과 eval follow-up Minor 1건을 보고했다.

skill-creator 리뷰: `SKILL.md` 목적, trigger description, progressive disclosure, `agents/openai.yaml` alignment는 충분하다고 보았다. 단 `validate_skill_docs.py`가 `agents/openai.yaml` semantic alignment를 완전히 자동 증명하지는 못한다고 지적했다. 현재 P1에서는 manual semantic review와 validator output을 함께 evidence로 남기면 닫을 수 있는 Minor로 판단한다.

## 근거

- `final.md` 1-87행: role/path/leakage/run/evidence/public wording/validation expectation은 있으나 source material precedence, dedicated source 판정, provisional/fallback ledger, DRF guardrail audit source, metadata semantic evidence, eval traceability evidence contract가 독립 section으로 없다.
- `dddjango/skills/source-reference-audit/SKILL.md` 19-24행: skill은 `final.md`, 필요 시 `review.md`, `internal.md`, `external.md`, runtime metadata semantic alignment를 요구한다.
- `workspace/develop/eval/source/answer/case-source-provisional-drf.yaml`: `source-reference-audit/reference/final.md`를 Reference Gap and DRF Guardrail basis로 인용하지만, 기존 `final.md`에는 해당 audit decision이 부족하다.
- `workspace/reference/source-reference-audit/reference/`에는 `final.md`만 있다. 이것이 source-final-only 상태인지, 다른 source material이 없어서 읽을 수 없는 것인지가 문서화되어 있지 않다.

## 발견 사항

### Major 1. DRF guardrail과 provisional source-gap audit decision 부족

현 상태의 `final.md`는 open gap/provisional/fallback status를 산출물에서 구분해야 한다고만 말한다. 그러나 어떤 경우 dedicated source reference로 판정하고, 어떤 경우 fallback/provisional로 판정하며, DRF guardrail을 어떤 source evidence로 확인해야 하는지가 없다.

허용 claim:

- source audit은 DRF guardrail과 provisional source handling을 별도 row로 검토해야 한다.
- dedicated source가 확인되지 않으면 fallback/provisional 또는 open gap으로 표시해야 한다.

금지 claim:

- `source-reference-audit` skill 또는 eval oracle의 존재만으로 DRF guardrail source decision이 충분하다고 주장한다.
- dedicated `final.md`가 없는 영역을 dedicated-source-complete로 표시한다.

### Major 2. final/review/internal/external material 상태 결정 부족

P1은 final/review/internal/external material handling을 요구한다. 현재 source-reference-audit reference area에는 `review.md`, `internal.md`, `external.md`가 없으며, `final.md`가 단일 source decision인지, 다른 material 부재를 어떻게 보고해야 하는지 명시하지 않는다.

허용 claim:

- `final.md`가 기본 decision source다.
- `review.md`, `internal.md`, `external.md`가 없으면 `not provided` 또는 `not present`로 보고하고, 부재 자체를 conflict-free 증거로 확대하지 않는다.

금지 claim:

- 읽지 않았거나 존재하지 않는 material을 검토했다고 주장한다.
- supplemental material이 없다는 이유만으로 모든 conflict/gap이 resolved라고 주장한다.

## 수정 필요 범위

- `workspace/reference/source-reference-audit/reference/final.md`에 source material precedence, provenance/crosswalk, dedicated/provisional source 판단, DRF guardrail audit source, runtime metadata evidence, eval traceability, validation coverage, completion gate를 보강한다.
- eval bucket의 duplicated reference basis는 P1에서 직접 고치지 않고 `workspace/plan/eval_lv_up_plan/source/analysis/`에 후속 대상으로 분류한다.

## 수정하지 말아야 할 범위

- `workspace/develop/eval/source/eval_goal.md` 중복 항목은 이번 P1에서 수정하지 않는다.
- private answer oracle, public case, eval runner는 이번 P1에서 수정하지 않는다.
- runtime skill은 reference 재평가 후 실제 반영 부족이 있을 때만 수정한다.

## 재평가 기준

- `final.md`만으로 P1이 요구한 source/reference governance, material precedence, provenance, source gap, DRF guardrail, metadata/runtime sync, validation coverage, eval traceability, leakage boundary 판단 기준을 설명할 수 있다.
- `source-reference-audit` reference area의 supplemental material 부재가 명시되어 있으며, 부재를 과장하지 않는 reporting rule이 있다.
- 독립 리뷰 Major 2건이 닫힌다.
