RESIDUAL_SOURCE ?= workspace/codex-eval/plugin-real-1/conformance.json
RESIDUAL_SOURCE_CASES ?= evals/shared/cases/trigger.jsonl
RESIDUAL_CASES ?= workspace/codex-eval/residual-latest/cases.jsonl
CONFORMANCE_GATE_ITERATION ?= workspace/codex-eval/conformance-rerun-1
PLUGIN_REAL_GATE_ITERATION ?= workspace/codex-eval/plugin-real-1

.PHONY: release test-release eval-conformance eval-plugin-real eval-residual eval-release-gate

# 플러그인 버전을 올리고, 검증/커밋/태그 생성 후 현재 브랜치와 태그를 origin에 push한다.
release:
	python3 scripts/release.py

# 릴리즈/평가 자동화와 스킬 mirror 동기화 회귀 테스트를 실행한다.
test-release:
	python3 -m unittest discover -s tests

# 로컬 skills/ 내용을 주입해 dddjango 컨벤션 준수도 5-case 평가를 실행하고 HTML 리포트와 release gate를 생성한다.
eval-conformance:
	python3 evals/codex/scripts/init_iteration.py --suite conformance-rerun --output workspace/codex-eval/conformance-rerun-1 --variant-set standard
	python3 evals/codex/scripts/run_prompts.py --iteration workspace/codex-eval/conformance-rerun-1 --variant baseline --keep-going
	python3 evals/codex/scripts/run_prompts.py --iteration workspace/codex-eval/conformance-rerun-1 --variant dddjango --keep-going
	python3 evals/codex/scripts/auto_grade_outputs.py workspace/codex-eval/conformance-rerun-1
	python3 evals/codex/scripts/grade_conformance.py workspace/codex-eval/conformance-rerun-1
	python3 evals/codex/scripts/render_report.py workspace/codex-eval/conformance-rerun-1
	python3 evals/codex/scripts/check_release_gate.py workspace/codex-eval/conformance-rerun-1

# 설치된 Codex marketplace 플러그인(dddjango-plugin variant)을 실제 로딩 경로로 평가한다.
eval-plugin-real:
	python3 evals/codex/scripts/init_iteration.py --suite trigger --output workspace/codex-eval/plugin-real-1 --variant-set plugin-real
	python3 evals/codex/scripts/run_prompts.py --iteration workspace/codex-eval/plugin-real-1 --variant baseline --keep-going
	python3 evals/codex/scripts/run_prompts.py --iteration workspace/codex-eval/plugin-real-1 --variant dddjango-plugin --keep-going
	python3 evals/codex/scripts/auto_grade_outputs.py workspace/codex-eval/plugin-real-1
	python3 evals/codex/scripts/grade_conformance.py workspace/codex-eval/plugin-real-1
	python3 evals/codex/scripts/render_report.py workspace/codex-eval/plugin-real-1
	python3 evals/codex/scripts/check_release_gate.py workspace/codex-eval/plugin-real-1

# 이전 conformance 결과에서 실패한 케이스만 뽑아 plugin-real 방식으로 재평가한다. 실패 케이스가 없으면 no-op으로 끝난다.
eval-residual:
	python3 evals/codex/scripts/run_residual_eval.py --source-conformance $(RESIDUAL_SOURCE) --source-cases $(RESIDUAL_SOURCE_CASES) --residual-cases $(RESIDUAL_CASES) --iteration workspace/codex-eval/residual-latest --variant-set plugin-real --with-variant dddjango-plugin

# 이미 생성된 conformance/plugin-real 평가 결과가 release gate를 통과하는지 확인한다.
eval-release-gate:
	python3 evals/codex/scripts/check_release_gate.py $(CONFORMANCE_GATE_ITERATION)
	python3 evals/codex/scripts/check_release_gate.py $(PLUGIN_REAL_GATE_ITERATION)
