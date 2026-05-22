수정 대상: case

# plugin provisional status case 계획

## 수정 범위

- 수정: `workspace/develop/eval/plugin/eval_goal.md`
- 수정: `workspace/develop/eval/plugin/cases/plugin/public/case-plugin-provisional-overclaim.md`
- 수정: `workspace/develop/eval/plugin/answer/case-plugin-provisional-overclaim.yaml`

## 절차

1. `eval_goal.md`의 provisional handling을 특정 skill 고정 목록에서 현재 source status 분류 기준으로 바꾼다.
2. Public case는 dedicated/provisional 정답을 단정하지 않고 source reference status를 검토하게 한다.
3. Answer oracle은 `workspace/reference/*/reference/final.md`가 실제 skill 주요 판단 축을 다루는지 확인하도록 요구한다.
4. DRF greenfield guardrail과 runtime metadata honesty는 유지하되, dedicated source가 있는 skill에 fallback/provisional 표시를 강제하지 않는다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket plugin`
- `make eval-one BUCKET=plugin CASE=case-plugin-provisional-overclaim TRY_NUMBER=1 SCOPE=targeted TOPIC=source-status-stale EXTRA_ARGS=--rerun JOBS=1`
- 필수 공통 validator와 독립 리뷰는 수정 후 실행한다.

## 완료 조건

- plugin provisional case가 현재 source reference 상태를 기준으로 dedicated/provisional/gap을 구분한다.
- answer oracle이 `architecture-implementation-patterns` 전용 source reference 존재를 부정하지 않는다.
- public case에 private answer나 scoring 기준이 노출되지 않는다.
