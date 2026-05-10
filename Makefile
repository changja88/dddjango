PYTHON ?= python3
RUN_ID ?= $(shell date +%Y%m%d-%H%M-initial-full)
JOBS ?= 3
MODEL ?= gpt-5.5
REASONING ?= xhigh
EVALUATOR_MODEL ?= $(MODEL)
EVALUATOR_REASONING ?= high
TIMEOUT_SECONDS ?= 1800
EXTRA_ARGS ?=
EVAL_BUCKETS ?= response code plugin runtime source workflow

.PHONY: eval-all-parallel
eval-all-parallel:
	@printf "%s\n" $(EVAL_BUCKETS) | xargs -P "$(JOBS)" -I{} \
		$(PYTHON) -B workspace/scripts/run_initial_eval.py \
			--bucket {} \
			--run-id "$(RUN_ID)" \
			--model "$(MODEL)" \
			--reasoning "$(REASONING)" \
			--evaluator-model "$(EVALUATOR_MODEL)" \
			--evaluator-reasoning "$(EVALUATOR_REASONING)" \
			--timeout-seconds "$(TIMEOUT_SECONDS)" \
			$(EXTRA_ARGS)
