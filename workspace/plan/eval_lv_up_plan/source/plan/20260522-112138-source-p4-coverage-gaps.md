수정 대상: case

# source P4 coverage gap 계획

## 수정 범위

- `workspace/develop/eval/source/eval_goal.md`
- `workspace/develop/eval/source/cases/plugin/public/case-source-metadata-cache-sync.md`
- `workspace/develop/eval/source/answer/case-source-metadata-cache-sync.yaml`
- `workspace/develop/eval/source/cases/plugin/public/case-source-routing-exclusion.md`
- `workspace/develop/eval/source/answer/case-source-routing-exclusion.yaml`
- `workspace/develop/eval/source/answer/case-source-conflict-gap.yaml`
- `workspace/develop/eval/source/answer/case-source-provenance-crosswalk.yaml`

## 절차

1. source eval goal에 runtime metadata/cache sync와 source-audit exclusion coverage를 case family와 minimum coverage로 추가한다.
2. metadata/cache sync public case와 answer를 추가하고 `SKILL.md`, `agents/openai.yaml`, bundled reference, validation output, cache/source parity evidence를 요구한다.
3. routing exclusion public case와 answer를 추가하고 positive source audit routing과 Django implementation/test mechanics exclusion을 함께 검증한다.
4. conflict-gap answer에 `internal.md`, `external.md` consulted evidence를 보강한다.
5. provenance-crosswalk answer에 per-skill `workspace/reference/*/reference/final.md` source basis를 보강한다.
6. Public case에 answer-only schema field, private scoring note, previous run conclusion이 없는지 validator로 확인한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket source`
- `make eval-one BUCKET=source CASE=case-source-metadata-cache-sync TRY_NUMBER=1 SCOPE=targeted TOPIC=source-metadata-cache-sync EXTRA_ARGS=--rerun JOBS=1`
- `make eval-one BUCKET=source CASE=case-source-routing-exclusion TRY_NUMBER=1 SCOPE=targeted TOPIC=source-routing-exclusion EXTRA_ARGS=--rerun JOBS=1`
- `make eval-one BUCKET=source CASE=case-source-conflict-gap TRY_NUMBER=1 SCOPE=targeted TOPIC=source-conflict-gap-basis EXTRA_ARGS=--rerun JOBS=1`
- `make eval-one BUCKET=source CASE=case-source-provenance-crosswalk TRY_NUMBER=1 SCOPE=targeted TOPIC=source-provenance-crosswalk-basis EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- source bucket coverage tags가 P4의 source-reference-audit 목적을 직접 덮는다.
- 신규/수정 answer oracle이 source reference보다 과도하거나 부족한 요구를 하지 않는다.
- 추가/수정 case의 targeted eval 결과 또는 실패 run artifact와 원인 분류가 남는다.
