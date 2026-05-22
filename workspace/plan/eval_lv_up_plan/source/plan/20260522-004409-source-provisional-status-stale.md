수정 대상: case

# source provisional status case 계획

## 수정 범위

- 수정: `workspace/develop/eval/source/cases/plugin/public/case-source-provisional-drf.md`
- 수정: `workspace/develop/eval/source/answer/case-source-provisional-drf.yaml`

## 절차

1. Public case에서 "부족한" 단정을 제거하고, 세 영역의 현재 source reference status를 분류하게 한다.
2. Answer oracle은 `final.md` 존재와 주요 판단 축 coverage를 모두 확인하도록 요구한다.
3. `architecture-implementation-patterns`에는 dedicated source coverage를 인정하되, DRF guardrail은 별도 source decision으로 계속 검증한다.
4. Public case에는 answer field name, private scoring note, prior run finding을 넣지 않는다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket source`
- `make eval-one BUCKET=source CASE=case-source-provisional-drf TRY_NUMBER=1 SCOPE=targeted TOPIC=provisional-status-stale EXTRA_ARGS=--rerun JOBS=1`
- 필수 공통 validator와 독립 리뷰는 수정 후 실행한다.

## 완료 조건

- source provisional case가 현재 dedicated source reference를 부정하지 않는다.
- answer oracle이 source reference보다 과도하거나 부족한 요구를 하지 않는다.
- DRF guardrail은 provisional status와 분리되어 계속 검증된다.
