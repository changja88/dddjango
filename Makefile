EVAL_ITERATION ?= workspace/codex-eval/conformance-rerun-1
EVAL_SUITE ?= conformance-rerun
EVAL_VARIANT_SET ?= standard
EVAL_WITH_VARIANT ?= dddjango

.PHONY: release test-release eval-init eval-run eval-report smoke-eval full-eval eval-conformance eval-plugin-real

release:
	python3 scripts/release.py

test-release:
	python3 -m unittest discover -s tests

eval-init:
	python3 evals/codex/scripts/init_iteration.py --suite $(EVAL_SUITE) --output $(EVAL_ITERATION) --variant-set $(EVAL_VARIANT_SET)

eval-run:
	python3 evals/codex/scripts/run_prompts.py --iteration $(EVAL_ITERATION) --variant baseline --keep-going
	python3 evals/codex/scripts/run_prompts.py --iteration $(EVAL_ITERATION) --variant $(EVAL_WITH_VARIANT) --keep-going

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

eval-plugin-real: EVAL_SUITE=trigger
eval-plugin-real: EVAL_ITERATION=workspace/codex-eval/plugin-real-1
eval-plugin-real: EVAL_VARIANT_SET=plugin-real
eval-plugin-real: EVAL_WITH_VARIANT=dddjango-plugin
eval-plugin-real: eval-init eval-run eval-report
