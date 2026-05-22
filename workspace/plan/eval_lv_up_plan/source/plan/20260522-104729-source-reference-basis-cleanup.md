수정 대상: answer

# source reference basis cleanup 계획

## 수정 범위

- `workspace/develop/eval/source/eval_goal.md`
- `workspace/develop/eval/source/answer/case-source-docs-coherence.yaml`

## 절차

1. `source/eval_goal.md` Reference Basis에서 중복 `dddjango/skills/source-reference-audit/SKILL.md` 항목을 제거한다.
2. `case-source-docs-coherence.yaml`의 `reference_basis`에서 중복 항목을 제거한다.
3. Public case는 수정하지 않는다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket source`
- `make eval-one BUCKET=source CASE=case-source-docs-coherence TRY_NUMBER=1 SCOPE=targeted TOPIC=source-docs-coherence-dedup EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- source eval goal과 docs-coherence answer에 중복 reference basis가 없다.
- source bucket validator가 통과한다.
- targeted eval 결과 또는 실패 run artifact와 원인 분류를 남긴다.
