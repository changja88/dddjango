EVAL_ITERATION ?= workspace/codex-eval/conformance-rerun-1
EVAL_SUITE ?= conformance-rerun
EVAL_VARIANT_SET ?= standard
EVAL_WITH_VARIANT ?= dddjango
RESIDUAL_SOURCE ?= workspace/codex-eval/plugin-real-1/conformance.json
RESIDUAL_SOURCE_CASES ?= evals/shared/cases/trigger.jsonl
RESIDUAL_CASES ?= workspace/codex-eval/residual-latest/cases.jsonl
CONFORMANCE_GATE_ITERATION ?= workspace/codex-eval/conformance-rerun-1
PLUGIN_REAL_GATE_ITERATION ?= workspace/codex-eval/plugin-real-residual-1

.PHONY: release test-release eval-init eval-run eval-report eval-gate smoke-eval full-eval eval-conformance eval-plugin-real eval-residual-cases eval-residual-init eval-residual eval-release-gate

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

eval-gate:
	python3 evals/codex/scripts/check_release_gate.py $(EVAL_ITERATION)

smoke-eval: EVAL_SUITE=smoke
smoke-eval: EVAL_ITERATION=workspace/codex-eval/smoke-1
smoke-eval: eval-init eval-run eval-report eval-gate

full-eval: EVAL_SUITE=benchmark
full-eval: EVAL_ITERATION=workspace/codex-eval/benchmark-latest
full-eval: eval-init eval-run eval-report eval-gate

eval-conformance: EVAL_SUITE=conformance-rerun
eval-conformance: EVAL_ITERATION=workspace/codex-eval/conformance-rerun-1
eval-conformance: eval-init eval-run eval-report eval-gate

eval-plugin-real: EVAL_SUITE=trigger
eval-plugin-real: EVAL_ITERATION=workspace/codex-eval/plugin-real-1
eval-plugin-real: EVAL_VARIANT_SET=plugin-real
eval-plugin-real: EVAL_WITH_VARIANT=dddjango-plugin
eval-plugin-real: eval-init eval-run eval-report eval-gate

eval-residual-cases:
	python3 evals/codex/scripts/build_residual_cases.py --source-conformance $(RESIDUAL_SOURCE) --source-cases $(RESIDUAL_SOURCE_CASES) --output $(RESIDUAL_CASES)

eval-residual-init: EVAL_ITERATION=workspace/codex-eval/residual-latest
eval-residual-init: EVAL_VARIANT_SET=plugin-real
eval-residual-init: eval-residual-cases
	python3 evals/codex/scripts/init_iteration.py --cases $(RESIDUAL_CASES) --output $(EVAL_ITERATION) --variant-set $(EVAL_VARIANT_SET)

eval-residual: EVAL_ITERATION=workspace/codex-eval/residual-latest
eval-residual: EVAL_VARIANT_SET=plugin-real
eval-residual: EVAL_WITH_VARIANT=dddjango-plugin
eval-residual:
	python3 evals/codex/scripts/run_residual_eval.py --source-conformance $(RESIDUAL_SOURCE) --source-cases $(RESIDUAL_SOURCE_CASES) --residual-cases $(RESIDUAL_CASES) --iteration $(EVAL_ITERATION) --variant-set $(EVAL_VARIANT_SET) --with-variant $(EVAL_WITH_VARIANT)

eval-release-gate:
	python3 evals/codex/scripts/check_release_gate.py $(CONFORMANCE_GATE_ITERATION)
	python3 evals/codex/scripts/check_release_gate.py $(PLUGIN_REAL_GATE_ITERATION)
