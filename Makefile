PYTHON ?= python3
RUN_ID ?= $(shell date +%Y%m%d-%H%M-initial-full)
JOBS ?= 3
MODEL ?= gpt-5.5
REASONING ?= xhigh
EVALUATOR_MODEL ?= $(MODEL)
EVALUATOR_REASONING ?= high
TIMEOUT_SECONDS ?= 1800
EXTRA_ARGS ?=
BUCKETS ?= response code plugin runtime source workflow
BUCKET ?= workflow
CASE ?=
CASE_ARG = $(if $(CASE),--case "$(CASE)")

# 전체 평가 항목(response/code/plugin/runtime/source/workflow)을 병렬로 실행한다.
# 사용: make eval-all
# 예: make eval-all RUN_ID=20260511-full EXTRA_ARGS=--rerun JOBS=3
.PHONY: eval-all
eval-all:
	@printf "%s\n" $(BUCKETS) | xargs -P "$(JOBS)" -I{} \
		$(PYTHON) -B workspace/scripts/run_initial_eval.py \
			--bucket {} \
			--run-id "$(RUN_ID)" \
			--model "$(MODEL)" \
			--reasoning "$(REASONING)" \
			--evaluator-model "$(EVALUATOR_MODEL)" \
			--evaluator-reasoning "$(EVALUATOR_REASONING)" \
			--timeout-seconds "$(TIMEOUT_SECONDS)" \
			$(EXTRA_ARGS)

# 특정 평가 항목(bucket) 하나만 실행한다.
# 사용: make eval-one BUCKET=workflow
# 단일 case만 다시 실행: make eval-one BUCKET=workflow CASE=case-workflow-tiny-restraint EXTRA_ARGS=--rerun
.PHONY: eval-one
eval-one:
	$(PYTHON) -B workspace/scripts/run_initial_eval.py \
		--bucket "$(BUCKET)" \
		--run-id "$(RUN_ID)" \
		--model "$(MODEL)" \
		--reasoning "$(REASONING)" \
		--evaluator-model "$(EVALUATOR_MODEL)" \
		--evaluator-reasoning "$(EVALUATOR_REASONING)" \
		--timeout-seconds "$(TIMEOUT_SECONDS)" \
		$(CASE_ARG) $(EXTRA_ARGS)

# 이전 이름 호환용 alias. 새 명령은 eval-all / eval-one을 사용한다.
.PHONY: eval-all-parallel eval-bucket eval-workflow
eval-all-parallel: eval-all

eval-bucket:
	$(MAKE) eval-one BUCKET="$(or $(EVAL_BUCKET),$(BUCKET))"

eval-workflow:
	$(MAKE) eval-one BUCKET=workflow
