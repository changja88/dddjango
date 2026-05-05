EVAL_ITERATION ?= workspace/codex-eval/conformance-rerun-1
EVAL_SUITE ?= conformance-rerun

.PHONY: release test-release eval-init eval-run eval-report smoke-eval full-eval eval-conformance

release:
	python3 scripts/release.py

test-release:
	python3 -m unittest discover -s tests

eval-init:
	python3 evals/codex/scripts/init_iteration.py --suite $(EVAL_SUITE) --output $(EVAL_ITERATION)

eval-run:
	python3 evals/codex/scripts/run_prompts.py --iteration $(EVAL_ITERATION) --variant baseline --keep-going
	python3 evals/codex/scripts/run_prompts.py --iteration $(EVAL_ITERATION) --variant dddjango --keep-going

eval-report:
	python3 evals/codex/scripts/auto_grade_outputs.py $(EVAL_ITERATION)
	python3 evals/codex/scripts/grade_conformance.py $(EVAL_ITERATION)
	python3 evals/codex/scripts/render_report.py $(EVAL_ITERATION)

smoke-eval: EVAL_SUITE=smoke
smoke-eval: EVAL_ITERATION=workspace/codex-eval/smoke-1
smoke-eval: eval-init eval-run eval-report

full-eval: EVAL_SUITE=benchmark
full-eval: EVAL_ITERATION=workspace/codex-eval/benchmark-latest
full-eval: eval-init eval-run eval-report

eval-conformance: EVAL_SUITE=conformance-rerun
eval-conformance: EVAL_ITERATION=workspace/codex-eval/conformance-rerun-1
eval-conformance: eval-init eval-run eval-report
