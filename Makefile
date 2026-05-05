.PHONY: release test-release eval-calibrate eval-smoke eval-dddjango eval-report

EVAL_RUN_ARGS = $(if $(SUITE),--suite $(SUITE),) $(if $(CASE),--case $(CASE),) $(if $(VARIANT),--variant $(VARIANT),)
EVAL_REPORT_ARGS = $(if $(SUITE),--suite $(SUITE),) $(if $(CASE),--case $(CASE),)

# 플러그인 버전을 올리고, 검증/커밋/태그 생성 후 현재 브랜치와 태그를 origin에 push한다.
release:
	python3 scripts/release.py

# 릴리즈 자동화와 스킬 mirror 동기화 회귀 테스트를 실행한다.
test-release:
	python3 -m unittest discover -s tests

# dddjango 평가 항목이 좋은/나쁜/경계 샘플에 기대대로 반응하는지 검증한다.
eval-calibrate:
	python3 evals/dddjango/scripts/run_calibration.py --write-report

# dddjango 평가 파이프라인이 동작하는지 fixture 기반 smoke 리포트를 생성한다. 실제 성능 평가는 아니다.
eval-smoke:
	python3 evals/dddjango/scripts/validate_eval_config.py
	python3 evals/dddjango/scripts/run_calibration.py --write-report
	python3 evals/dddjango/scripts/run_evaluation.py --mode fixture $(EVAL_RUN_ARGS)
	python3 evals/dddjango/scripts/score_outputs.py --latest $(EVAL_REPORT_ARGS)
	python3 evals/dddjango/scripts/render_report.py --latest $(EVAL_REPORT_ARGS)

# dddjango를 설치하지 않은 Codex와 설치한 Codex를 같은 prompt로 live 실행해 성능표를 생성한다.
eval-dddjango:
	python3 evals/dddjango/scripts/validate_eval_config.py
	python3 evals/dddjango/scripts/run_calibration.py --write-report
	python3 evals/dddjango/scripts/run_evaluation.py --mode live $(EVAL_RUN_ARGS)
	@status=0; python3 evals/dddjango/scripts/score_outputs.py --latest $(EVAL_REPORT_ARGS) || status=$$?; python3 evals/dddjango/scripts/render_report.py --latest $(EVAL_REPORT_ARGS); exit $$status

# 가장 최근 dddjango 평가 결과를 HTML 리포트로 다시 렌더링한다.
eval-report:
	python3 evals/dddjango/scripts/render_report.py --latest
