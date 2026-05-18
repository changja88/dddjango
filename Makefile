PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
RUN_ID ?=
TRY_NUMBER ?= 1
SCOPE ?= full
TOPIC ?= current-baseline
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
RUN_ID_ARG = $(if $(RUN_ID),--run-id "$(RUN_ID)")

# 전체 평가 항목(response/code/plugin/runtime/source/workflow)을 병렬로 실행한다.
# 사용: make eval-all
# 예: make eval-all TRY_NUMBER=1 SCOPE=full TOPIC=current-baseline EXTRA_ARGS=--rerun JOBS=3
.PHONY: eval-all
eval-all:
	@status=0; refresh_status=0; \
	printf "%s\n" $(BUCKETS) | xargs -P "$(JOBS)" -I{} \
		$(PYTHON) -B workspace/scripts/run_initial_eval.py \
			--bucket {} \
			--try-number "$(TRY_NUMBER)" \
			--scope "$(SCOPE)" \
			--topic "$(TOPIC)" \
			--model "$(MODEL)" \
			--reasoning "$(REASONING)" \
			--evaluator-model "$(EVALUATOR_MODEL)" \
			--evaluator-reasoning "$(EVALUATOR_REASONING)" \
			--timeout-seconds "$(TIMEOUT_SECONDS)" \
			$(EXTRA_ARGS) || status=$$?; \
	$(PYTHON) -B workspace/scripts/render_eval_review_html.py --refresh-latest || refresh_status=$$?; \
	if [ "$$status" -ne 0 ]; then exit "$$status"; fi; \
	exit "$$refresh_status"

# 특정 평가 항목(bucket) 하나를 실행한다. JOBS는 bucket 내부 case 병렬 수다.
# 사용: make eval-one BUCKET=workflow JOBS=4
# 기존 run을 다시 렌더/검증할 때만 canonical RUN_ID를 지정한다.
# 단일 case만 다시 실행: make eval-one BUCKET=workflow CASE=case-workflow-tiny-restraint EXTRA_ARGS=--rerun
.PHONY: eval-one
eval-one:
	$(PYTHON) -B workspace/scripts/run_initial_eval.py \
		--bucket "$(BUCKET)" \
		$(RUN_ID_ARG) \
		--try-number "$(TRY_NUMBER)" \
		--scope "$(SCOPE)" \
		--topic "$(TOPIC)" \
		--model "$(MODEL)" \
		--reasoning "$(REASONING)" \
		--evaluator-model "$(EVALUATOR_MODEL)" \
		--evaluator-reasoning "$(EVALUATOR_REASONING)" \
		--timeout-seconds "$(TIMEOUT_SECONDS)" \
		--case-jobs "$(JOBS)" \
		$(CASE_ARG) $(EXTRA_ARGS)

# 이전 이름 호환용 alias. 새 명령은 eval-all / eval-one을 사용한다.
.PHONY: eval-all-parallel eval-bucket eval-workflow
eval-all-parallel: eval-all

eval-bucket:
	$(MAKE) eval-one BUCKET="$(or $(EVAL_BUCKET),$(BUCKET))"

eval-workflow:
	$(MAKE) eval-one BUCKET=workflow
