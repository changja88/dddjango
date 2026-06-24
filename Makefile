SHELL := /bin/bash

# 릴리즈 대상 (dddjango)
NAME            := dddjango
PLUGIN          := dddjango
CLAUDE_MANIFEST := dddjango/.claude-plugin/plugin.json
CODEX_MANIFEST  := codex-dddjango/.codex-plugin/plugin.json

# DRY=1 이면 실제 변경/커밋/푸시/Release 없이 시뮬레이션만 (버전 선택·기록 미리보기까지 실제 로직 실행)
DRY ?= 0

.PHONY: release

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
		echo "    [2] python3 workspace/tools/corpus_mirror_sync.py --check"; \
		echo "    [3] 두 manifest에 v$$V 기록 (위 미리보기)"; \
		echo "    [4] git commit -m 'release: v$$V' (manifest 2곳)"; \
		echo "    [5] git tag -a $$TAG -m '$(NAME) v$$V'"; \
		echo "    [6] git push origin main && git push origin $$TAG"; \
		echo "    [7] gh release create $$TAG --verify-tag --title '$(NAME) v$$V' --generate-notes"; \
		echo ""; echo "✅ [dry-run] v$$V 시뮬레이션 완료 — 실제 변경/커밋/푸시/Release 없음"; \
	else \
		echo "[1/7] manifest 검증 (claude --strict)"; \
		claude plugin validate $(PLUGIN) --strict; \
		echo "[2/7] corpus mirror 검사"; \
		python3 workspace/tools/corpus_mirror_sync.py --check; \
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
