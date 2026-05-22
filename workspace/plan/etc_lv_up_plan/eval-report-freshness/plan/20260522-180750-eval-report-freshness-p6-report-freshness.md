수정 대상: tooling

# P6 HTML report 최신성 계획

## 수정 범위

- `workspace/scripts/render_eval_review_html.py`
- `workspace/scripts/test_render_eval_review_html.py`
- `workspace/scripts/run_initial_eval.py`
- `workspace/scripts/test_run_initial_eval.py`

## 절차

1. 실패 근거 artifact 링크가 report data와 상세 dialog에 드러나는지 실패 테스트를 먼저 추가한다.
2. eval bucket 중간 실패 시에도 가능한 경우 renderer가 실행되는지 실패 테스트를 먼저 추가한다.
3. renderer는 variant별 raw output, stderr, command, exit, answer-oracle evaluation 근거를 run-relative evidence link로 제공한다.
4. renderer는 answer YAML의 private 기준 필드를 HTML payload에 싣지 않고, evaluator/answer-oracle artifact link만 제공한다.
5. `run_initial_eval.py`는 bucket pipeline 실패 후에도 best-effort로 validator와 renderer를 실행하되, 원래 실패 exit는 유지한다.
6. 최신 alias는 최신 full attempt report를 가리키고 latest-valid는 검증 통과 full run만 가리키도록 기존 선택 기준을 유지한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_render_eval_review_html.py`
- `.venv/bin/python -B workspace/scripts/test_run_initial_eval.py`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `.venv/bin/python -B workspace/scripts/validate_eval_run.py --bucket response --run-id 20260522-175638-response-try01-full-current-baseline --allow-skipped-exits`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket plugin`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket runtime`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket source`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket workflow`
- `.venv/bin/python -B workspace/scripts/render_eval_review_html.py --refresh-latest`

## 완료 조건

- 최신성 점검표의 열린 항목이 닫힌다.
- 실패 case 상세에서 raw output, stderr, command/exit, answer-oracle 근거 링크를 따라갈 수 있다.
- eval-all이 중간 실패해도 생성 가능한 bucket report와 최신 alias가 유실되지 않는다.
- 독립 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이 된다.
