SHELL := /bin/bash

# 릴리즈 대상 (dddjango)
NAME            := dddjango
PLUGIN          := dddjango
CLAUDE_MANIFEST := dddjango/.claude-plugin/plugin.json
CODEX_MANIFEST  := codex-dddjango/.codex-plugin/plugin.json

# DRY=1 이면 실제 변경/커밋/푸시/Release 없이 시뮬레이션만 (버전 선택·기록 미리보기까지 실제 로직 실행)
DRY ?= 0

.PHONY: release ontology-env ontology-hooks verify verify-ontology verify-base verify-web verify-mutation verify-firing verify-runready rulepack

VENV_PY := .venv/bin/python

# 저장소 검증 세트 단일 출처 (D1 — release [2/7] 이 이 타깃을 호출)
# 롤백·중단 시 되돌림: 아래 의존에서 verify-ontology 한 줄 삭제 (t0-plan §7)
verify: verify-ontology verify-base verify-web

verify-web:
	@set -euo pipefail; \
	echo "[verify-web] dddjango-web 픽스처(백스톱·절단 도구)"; \
	bash dddjango-web/scripts/test/run_fixtures.sh

# 온톨로지 단 — .venv 파이썬 고정 (T0 A8)
verify-ontology:
	@set -euo pipefail; \
	test -x $(VENV_PY) || { echo "ERROR: .venv 부재 — make ontology-env 필요"; exit 1; }; \
	echo "[verify-ontology 0/10] 도구 사슬 스모크"; \
	$(VENV_PY) workspace/tools/ontology_env_smoke.py; \
	echo "[verify-ontology 1/10] 4단 저작 게이트 (전 ttl)"; \
	PYTHONPATH=workspace/tools $(VENV_PY) workspace/tools/ontology_gate.py; \
	echo "[verify-ontology 2/10] meta-SHACL 2층"; \
	PYTHONPATH=workspace/tools $(VENV_PY) workspace/tools/ontology_meta_shacl.py; \
	echo "[verify-ontology 3/10] SHACL 본검증 (전량 병합)"; \
	PYTHONPATH=workspace/tools $(VENV_PY) workspace/tools/ontology_shacl_full.py; \
	echo "[verify-ontology 4/10] 계층 병합·적용 대상 계수 회귀"; \
	PYTHONPATH=workspace/tools $(VENV_PY) workspace/tools/ontology_hierarchy_check.py --with-golden; \
	echo "[verify-ontology 5/10] 골든 페어 red/green"; \
	PYTHONPATH=workspace/tools $(VENV_PY) workspace/tools/ontology_golden_check.py; \
	echo "[verify-ontology 6/10] 게이트 스모크 (오류 계열→차단 단 매핑 표)"; \
	PYTHONPATH=workspace/tools $(VENV_PY) workspace/tools/ontology_gate_smoke.py; \
	echo "[verify-ontology 7/10] ISSUED 대장↔정본 정합"; \
	python3 workspace/tools/ontology_issued_check.py; \
	echo "[verify-ontology 8/10] 원장 부식 검사 (LEDGER 926 기준선)"; \
	python3 workspace/tools/ontology_ledger_check.py; \
	echo "[verify-ontology 9/10] 렌더 동기 (투영물 == render(그래프))"; \
	PYTHONPATH=workspace/tools $(VENV_PY) workspace/tools/ontology_render_sync.py; \
	echo "[verify-ontology 10/11] 구조 검증 (SPARQL 7종·순서·datatype·alias 함수성·pathGlob)"; \
	PYTHONPATH=workspace/tools $(VENV_PY) workspace/tools/ontology_structural_check.py --self-test; \
	PYTHONPATH=workspace/tools $(VENV_PY) workspace/tools/ontology_structural_check.py; \
	echo "[verify-ontology 11/11] 질의 카탈로그 골든 (Q1~Q4 양성·음성·run 격리)"; \
	PYTHONPATH=workspace/tools $(VENV_PY) workspace/tools/query_golden_check.py

# 기존 릴리즈 검증 세트 — 시스템 python3 유지 (실측 기반 보존, t0-plan A8)
verify-base:
	@set -euo pipefail; \
	if [[ -n "$${DJR_FINDINGS_JSON:-}" ]]; then echo "[preflight] DJR_FINDINGS_JSON 감지 — 외부 레코드 경로 격리 고지(차단 아님 — S#7): 메타 하네스(baseline·count·cross·fixture·backstop·findings-smoke)는 subprocess env 에서 스스로 제거한다. 잔여: gate 스모크 3종(registry·bc·anchor)은 미격리 — 지정 경로에 스모크 레코드가 append 될 수 있다"; fi; \
	echo "[verify-base] 검증 세트 (corpus·corpus-lint·spec·checker·cross-matrix·tree·coverage·fixture·baseline·count-golden·findings-smoke·drift-golden·anchor-smoke·gate-smoke·backstop·bounce-counter·bounce-mutation·regen-golden·regen-loop·runtime-parity·byte-copy)"; \
	python3 workspace/tools/corpus_mirror_sync.py --check; \
	PYTHONUTF8=1 python3 workspace/tools/corpus_lint.py; \
	PYTHONUTF8=1 python3 workspace/tools/checker_cross_matrix.py; \
	PYTHONUTF8=1 python3 workspace/tools/spec_lint.py; \
	PYTHONUTF8=1 python3 workspace/tools/checker_lint.py; \
	PYTHONUTF8=1 python3 workspace/tools/tree_mirror_check.py; \
	PYTHONUTF8=1 python3 workspace/tools/reverse_coverage.py; \
	PYTHONUTF8=1 python3 workspace/tools/fixture_matrix.py; \
	PYTHONUTF8=1 python3 workspace/tools/checker_baseline_matrix.py; \
	PYTHONUTF8=1 python3 workspace/tools/findings_count_matrix.py; \
	PYTHONUTF8=1 python3 workspace/tools/findings_smoke.py; \
	PYTHONUTF8=1 python3 workspace/tools/construct_drift_report.py; \
	PYTHONUTF8=1 python3 workspace/tools/anchor_diff_smoke.py; \
	PYTHONUTF8=1 python3 workspace/tools/registry_gate_smoke.py; \
	PYTHONUTF8=1 python3 workspace/tools/bc_registry_smoke.py; \
	PYTHONUTF8=1 python3 workspace/tools/api_error_backstop_matrix.py; \
	PYTHONUTF8=1 python3 workspace/tools/session_bounce_counter.py --self-test; \
	PYTHONUTF8=1 python3 workspace/tools/session_bounce_counter.py --mutation-test; \
	PYTHONUTF8=1 python3 workspace/tools/regen_loop_prototype.py --self-test; \
	PYTHONUTF8=1 python3 workspace/tools/regen_loop_smoke.py; \
	PYTHONUTF8=1 python3 workspace/tools/runtime_parity_check.py; \
	PYTHONUTF8=1 python3 workspace/tools/rulepack_smoke.py; \
	PYTHONPATH=workspace/tools $(VENV_PY) workspace/tools/derive_path_globs.py --check; \
	PYTHONPATH=workspace/tools $(VENV_PY) workspace/tools/ontology_rulepack.py --check; \
	PYTHONUTF8=1 python3 workspace/tools/manifest_seal.py --check --draft; \
	PYTHONUTF8=1 python3 workspace/tools/manifest_seal.py --self-test; \
	PYTHONUTF8=1 python3 workspace/tools/ab_score.py --self-test; \
	diff -rq dddjango/scripts codex-dddjango/skills/dddjango/scripts --exclude=__pycache__

# 변이 자가검사 — 상시 verify 와 분리(T2-4 적대 리뷰 AQ-10: 검출력 증명은 무겁고 상시 아님).
# 팩·selector 를 건드린 커밋은 이 타깃도 green 이어야 한다.
verify-mutation:
	@set -euo pipefail; \
	PYTHONUTF8=1 python3 workspace/tools/rulepack_smoke.py --mutation-test

# C암 발화 증명 — 4트리(source 2 + 설치 cache 2) × 5단언. **T2-5 실런 진입의 hard gate**.
# 지금은 cache 가 2.11.0 이라 cache 두 레인이 red 인 것이 정상이고, 그 red 가 곧
# «T2-0b 설치본 갱신 전에는 C 실런 금지»의 기계적 표현이다(개발 중에는 ALLOW_STALE=1).
verify-firing:
	@set -euo pipefail; \
	PYTHONUTF8=1 python3 workspace/tools/firing_probe.py \
	  $(if $(filter 1,$(ALLOW_STALE)),--allow-stale-cache,)

# **T2-5 실런 진입 게이트** — 이것만이 C 실런의 허가다(사후 리뷰 AS-04).
# `verify` 는 firing probe 를 부르지 않으므로, stale cache 상태에서도 일반 검증은 green 이다.
# **release 는 이 타깃을 부르지 않는다**(반증 레인 AT 4-2 — 앞선 문면은 과장이었다):
# 설치본이 낡은 동안 release 를 막을 이유가 없고, 막아야 하는 것은 **C 실런**이다.
# **문면 정정(2026-08-20 전수 리뷰 AU 발견 5)**: 앞선 주석은 「T2-5 runner 는 이 타깃 성공
# 없이 기동하지 않는다」고 적었으나 그런 runner 는 존재하지 않는다 — 실런 세션은 **사람이**
# `claude`/`codex` 로 직접 기동하고(프로토콜 §2 ④ — 하네스 세션의 재귀 기동은 권한 분류기에
# 차단된다), 이 타깃을 부르는 코드는 저장소 어디에도 없다. 즉 이것은 **자발적 진단 명령**이다.
# 기동을 기계로 막을 자리가 없으므로 **채점 경계**에 건다: `--runready-receipt` 로 발행한
# 영수증이 없거나 봉인본과 다르면 `ab_score.py` 가 채점을 거절한다. 막지 못하면 세지 않는다.
#
# **T2-0b manifest 엄격 대조가 여기 붙는다**(2026-08-20). 부속서에 `PENDING` 이 남아 있거나
# status 가 `sealed` 가 아니면 red 다 — 그 red 가 «봉인 전에는 실런 금지»의 기계적 표현이다.
# `verify` 는 `--draft` 로 부르므로 봉인 전에도 상시 검증은 green 이다(firing probe 와 같은 배치).
verify-runready: verify verify-mutation
	@set -euo pipefail; \
	PYTHONUTF8=1 python3 workspace/tools/firing_probe.py; \
	PYTHONUTF8=1 python3 workspace/tools/manifest_seal.py --check; \
	echo "[runready] 실런 진입 조건 충족 — 상시 검증 + 변이 검출력 + 발화 증명 + manifest 봉인"

# 규칙 팩 재생성 — 그래프가 바뀌면 이걸 돌리고 커밋한다(투영물 · 직접 편집 금지)
rulepack:
	@PYTHONPATH=workspace/tools $(VENV_PY) workspace/tools/ontology_rulepack.py

# 설치본 위반 레코드 수집 (T2-2 — `.dddjango/violations/*.jsonl` → workspace/eval/violations/raw/)
# 원천 지정: make collect-violations FROM="<dir1> <dir2>" (미지정 시 DJR_VIOLATIONS_DIR·저장소 설치본)
collect-violations:
	@set -euo pipefail; \
	python3 workspace/tools/collect_violations.py $(foreach d,$(FROM),--from $(d))

# 훅 단일 루트 설치 (T0 A8 — D2): core.hooksPath = workspace/hooks
ontology-hooks:
	@set -euo pipefail; \
	if ls .git/hooks 2>/dev/null | grep -v '\.sample$$' | grep -q .; then \
		echo "경고: .git/hooks 에 비샘플 훅 존재 — core.hooksPath 전환 시 조용히 무시됨"; \
	fi; \
	chmod +x workspace/hooks/pre-commit; \
	git config core.hooksPath workspace/hooks; \
	echo "훅 단일 루트 = workspace/hooks (해제: git config --unset core.hooksPath)"

# 온톨로지 메인테이너 환경(.venv) 구축 — 버전 고정: workspace/tools/ontology-requirements.txt
# rdflib·pySHACL·rdfcanon 은 이 venv 전용 (플러그인 배포물 침투 금지 — 블루프린트 E7)
ontology-env:
	@set -euo pipefail; \
	PY=/opt/homebrew/bin/python3.14; \
	command -v "$$PY" >/dev/null || { echo "ERROR: python3.14 필요 — brew install python@3.14"; exit 1; }; \
	"$$PY" -m venv .venv; \
	.venv/bin/pip install --quiet --upgrade pip; \
	.venv/bin/pip install --quiet --no-deps -r workspace/tools/ontology-requirements.txt; \
	.venv/bin/python workspace/tools/ontology_env_smoke.py

# 새 버전 릴리즈: 버전 선택(patch/minor/major) → 두 마켓 manifest 동시 기록
#   → 커밋 → annotated 태그 → push(main+tag) → GitHub Release 페이지 생성.
# git 태그 · Claude 마켓 버전 · Codex 마켓 버전을 하나의 버전으로 완전히 일치시킨다.
# 미리보기:  make release DRY=1
release:
	@set -euo pipefail; \
	DRY="$(DRY)"; \
	command -v jq >/dev/null || { echo "ERROR: jq 필요"; exit 1; }; \
	if [[ "$$DRY" != 1 ]]; then command -v gh >/dev/null || { echo "ERROR: gh(GitHub CLI) 필요"; exit 1; }; fi; \
	if [[ "$$DRY" == 1 ]]; then echo "··· DRY-RUN 모드: 실제 변경/커밋/푸시 없음 ···"; echo ""; fi; \
	CLAUDE_V=$$(jq -r '.version' $(CLAUDE_MANIFEST)); \
	CODEX_V=$$(jq -r '.version' $(CODEX_MANIFEST)); \
	if [[ -z "$$CLAUDE_V" || "$$CLAUDE_V" == "null" ]]; then echo "ERROR: $(CLAUDE_MANIFEST)에 version 없음"; exit 1; fi; \
	if [[ "$$CLAUDE_V" != "$$CODEX_V" ]]; then echo "ERROR: 현재 버전 불일치 — Claude=$$CLAUDE_V Codex=$$CODEX_V"; exit 1; fi; \
	if [[ ! "$$CLAUDE_V" =~ ^[0-9]+\.[0-9]+\.[0-9]+$$ ]]; then echo "ERROR: 현재 버전이 X.Y.Z 형식 아님: $$CLAUDE_V"; exit 1; fi; \
	BR=$$(git rev-parse --abbrev-ref HEAD); \
	if [[ "$$BR" != "main" ]]; then \
		if [[ "$$DRY" == 1 ]]; then echo "[dry-run] 경고: main 브랜치 아님 ($$BR) — 실제 릴리즈는 차단됨"; \
		else echo "ERROR: main 브랜치에서만 릴리즈 (현재 $$BR)"; exit 1; fi; \
	fi; \
	if [[ -n "$$(git status --porcelain)" ]]; then \
		if [[ "$$DRY" == 1 ]]; then echo "[dry-run] 경고: worktree dirty — 실제 릴리즈는 차단됨"; \
		else echo "ERROR: worktree dirty — 커밋/스태시 후 진행"; git status --short; exit 1; fi; \
	fi; \
	if [[ "$$DRY" != 1 ]]; then \
		git fetch --quiet origin main || { echo "ERROR: git fetch 실패"; exit 1; }; \
		if git rev-parse -q --verify origin/main >/dev/null; then \
			if ! git merge-base --is-ancestor origin/main HEAD; then echo "ERROR: origin/main에 로컬에 없는 커밋 있음 — 먼저 pull"; exit 1; fi; \
		fi; \
	fi; \
	major=$${CLAUDE_V%%.*}; rest=$${CLAUDE_V#*.}; minor=$${rest%%.*}; patch=$${rest##*.}; \
	echo "현재 버전: v$$CLAUDE_V"; echo ""; \
	echo "  1) patch  v$$major.$$minor.$$((patch+1))   — 버그 수정"; \
	echo "  2) minor  v$$major.$$((minor+1)).0   — 새 기능"; \
	echo "  3) major  v$$((major+1)).0.0   — 큰 변경"; \
	echo ""; \
	read -r -p "버전 선택 [1/2/3]: " choice; \
	case "$$choice" in \
		1) V="$$major.$$minor.$$((patch+1))" ;; \
		2) V="$$major.$$((minor+1)).0" ;; \
		3) V="$$((major+1)).0.0" ;; \
		*) echo "잘못된 선택"; exit 1 ;; \
	esac; \
	TAG="$(NAME)--v$$V"; \
	if git rev-parse -q --verify "refs/tags/$$TAG" >/dev/null; then \
		if [[ "$$DRY" == 1 ]]; then echo "[dry-run] 경고: 로컬 태그 $$TAG 이미 존재"; \
		else echo "ERROR: 로컬 태그 $$TAG 이미 존재"; exit 1; fi; \
	fi; \
	if [[ "$$DRY" != 1 && -n "$$(git ls-remote --tags origin "refs/tags/$$TAG")" ]]; then echo "ERROR: 원격 태그 $$TAG 이미 존재"; exit 1; fi; \
	echo ""; \
	echo "  릴리즈 요약"; \
	echo "    대상      : $(NAME)"; \
	echo "    버전      : v$$CLAUDE_V → v$$V"; \
	echo "    git 태그  : $$TAG"; \
	echo "    기록 대상 : $(CLAUDE_MANIFEST), $(CODEX_MANIFEST)"; \
	echo "    원격      : origin/main + $$TAG + GitHub Release"; \
	echo ""; \
	read -r -p "진행할까요? [y/N]: " yn; \
	if [[ "$$yn" != "y" && "$$yn" != "Y" ]]; then echo "취소됨."; exit 1; fi; \
	if [[ "$$DRY" == 1 ]]; then \
		echo ""; echo "[dry-run] 버전 기록 미리보기 (실제 파일 미변경):"; \
		for f in $(CLAUDE_MANIFEST) $(CODEX_MANIFEST); do \
			tmp=$$(mktemp); cp "$$f" "$$tmp"; \
			sed -i '' "s/\"version\": *\"[^\"]*\"/\"version\": \"$$V\"/" "$$tmp"; \
			echo "  · $$f"; diff "$$f" "$$tmp" | sed 's/^/      /' || true; \
			rm -f "$$tmp"; \
		done; \
		echo ""; echo "[dry-run] 실제 실행 시 수행할 단계 (미실행):"; \
		echo "    [1] claude plugin validate $(PLUGIN) --strict"; \
		echo "    [2] 검증 세트 — corpus·corpus_lint·checker_cross_matrix·spec_lint·checker_lint·tree_mirror·reverse_coverage·fixture_matrix·anchor_diff_smoke·backstop_matrix·scripts byte-copy"; \
		echo "    [3] 두 manifest에 v$$V 기록 (위 미리보기)"; \
		echo "    [4] git commit -m 'release: v$$V' (manifest 2곳)"; \
		echo "    [5] git tag -a $$TAG -m '$(NAME) v$$V'"; \
		echo "    [6] git push origin main && git push origin $$TAG"; \
		echo "    [7] gh release create $$TAG --verify-tag --title '$(NAME) v$$V' --generate-notes"; \
		echo ""; echo "✅ [dry-run] v$$V 시뮬레이션 완료 — 실제 변경/커밋/푸시/Release 없음"; \
	else \
		echo "[1/7] manifest 검증 (claude --strict)"; \
		claude plugin validate $(PLUGIN) --strict; \
		echo "[2/7] 검증 세트 — make verify (verify-ontology + verify-base, D1 단일 출처)"; \
		$(MAKE) verify; \
		echo "[3/7] 버전 기록 (Claude·Codex)"; \
		sed -i '' "s/\"version\": *\"[^\"]*\"/\"version\": \"$$V\"/" $(CLAUDE_MANIFEST); \
		sed -i '' "s/\"version\": *\"[^\"]*\"/\"version\": \"$$V\"/" $(CODEX_MANIFEST); \
		NC=$$(jq -r '.version' $(CLAUDE_MANIFEST)); NX=$$(jq -r '.version' $(CODEX_MANIFEST)); \
		if [[ "$$NC" != "$$V" || "$$NX" != "$$V" ]]; then echo "ERROR: 버전 기록 검증 실패 (Claude=$$NC Codex=$$NX, 기대 $$V)"; exit 1; fi; \
		echo "[4/7] 커밋"; \
		git add $(CLAUDE_MANIFEST) $(CODEX_MANIFEST); \
		git commit -m "release: v$$V"; \
		echo "[5/7] annotated 태그 $$TAG"; \
		git tag -a "$$TAG" -m "$(NAME) v$$V"; \
		echo "[6/7] push (main + tag)"; \
		git push origin main; \
		git push origin "$$TAG"; \
		echo "[7/7] GitHub Release 생성"; \
		gh release create "$$TAG" --verify-tag --title "$(NAME) v$$V" --generate-notes; \
		echo ""; \
		echo "✅ $(NAME) v$$V 릴리즈 완료 — 태그 $$TAG · manifest 2곳 · GitHub Release"; \
	fi
