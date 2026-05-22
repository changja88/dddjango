수정 대상: case

# P5 plugin-level workflow integrity case 계획

## 수정 범위

- 추가: `workspace/develop/eval/plugin/cases/plugin/public/case-plugin-p5-workflow-integrity.md`
- 추가: `workspace/develop/eval/plugin/answer/case-plugin-p5-workflow-integrity.yaml`
- 수정: `workspace/develop/eval/plugin/eval_goal.md`

## 절차

1. public case는 plugin-level 평가 요청만 담고 answer oracle 용어, scoring field, private run id를 노출하지 않는다.
2. answer oracle은 workflow 실행 승인, bounded sidecar, result collection, disjoint ownership, validation honesty, cache/source evidence를 required behavior로 둔다.
3. forbidden behavior에는 false actual delegation claim, pending result integration, overlapping ownership, cache-only completion, unsupported validation/browser/Serena/eval claim을 넣는다.
4. `coverage_tags`에는 기존 plugin coverage를 깨지 않는 범위에서 P5 workflow integrity를 식별할 tag를 추가한다.
5. plugin bucket validator와 targeted eval로 새 case를 검증한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket plugin`
- `.venv/bin/python -B workspace/scripts/run_eval_bucket.py --bucket plugin --scope targeted --topic p5-workflow-integrity --case case-plugin-p5-workflow-integrity`
- `.venv/bin/python -B workspace/scripts/evaluate_eval_run.py --bucket plugin --run-id <run-id> --case case-plugin-p5-workflow-integrity`
- `.venv/bin/python -B workspace/scripts/validate_eval_run.py --bucket plugin --run-id <run-id> --case case-plugin-p5-workflow-integrity`

## 완료 조건

- plugin bucket에 P5 workflow-integrity case와 answer oracle이 1:1로 존재한다.
- public case에 private evaluator material이 없다.
- targeted eval pass run과 run validation artifact가 남는다.
