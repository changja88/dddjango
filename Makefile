SHELL := /bin/bash

.PHONY: relase

relase:
	@set -euo pipefail; \
	CLAUDE_VERSION=$$(jq -r '.version' dddjango/.claude-plugin/plugin.json); \
	CODEX_VERSION=$$(jq -r '.version' codex-dddjango/.codex-plugin/plugin.json); \
	if [[ -z "$$CLAUDE_VERSION" || "$$CLAUDE_VERSION" == "null" ]]; then \
		echo "ERROR: Claude plugin version is missing"; \
		exit 1; \
	fi; \
	if [[ "$$CLAUDE_VERSION" != "$$CODEX_VERSION" ]]; then \
		echo "ERROR: version mismatch"; \
		echo "  Claude: $$CLAUDE_VERSION"; \
		echo "  Codex:  $$CODEX_VERSION"; \
		exit 1; \
	fi; \
	VERSION="$$CLAUDE_VERSION"; \
	TAG="dddjango--v$$VERSION"; \
	HEAD_SHA=$$(git rev-parse HEAD); \
	echo "[1/7] Release summary"; \
	echo "  Git tag:        $$TAG"; \
	echo "  Claude version: $$CLAUDE_VERSION"; \
	echo "  Codex version:  $$CODEX_VERSION"; \
	echo "  Commit:         $$HEAD_SHA"; \
	echo "  Remote:         origin/main + $$TAG"; \
	printf "\nType 'relase $$VERSION' to continue: "; \
	read -r CONFIRM; \
	if [[ "$$CONFIRM" != "relase $$VERSION" ]]; then \
		echo "Aborted."; \
		exit 1; \
	fi; \
	echo "[2/7] Check worktree"; \
	if [[ -n "$$(git status --porcelain)" ]]; then \
		echo "ERROR: worktree is dirty. Commit or stash changes before release."; \
		git status --short; \
		exit 1; \
	fi; \
	echo "[3/7] Validate plugin manifests"; \
	claude plugin validate dddjango --strict; \
	jq -e '.version == "'$$VERSION'"' dddjango/.claude-plugin/plugin.json >/dev/null; \
	jq -e '.version == "'$$VERSION'"' codex-dddjango/.codex-plugin/plugin.json >/dev/null; \
	echo "[4/7] Check corpus mirror"; \
	python3 workspace/tools/corpus_mirror_sync.py --check; \
	echo "[5/7] Check git refs"; \
	REMOTE_HEAD=$$(git ls-remote origin refs/heads/main | awk '{print $$1}'); \
	if [[ -n "$$REMOTE_HEAD" && "$$REMOTE_HEAD" != "$$HEAD_SHA" ]]; then \
		echo "ERROR: origin/main ($$REMOTE_HEAD) does not match HEAD ($$HEAD_SHA). Push or sync main first."; \
		exit 1; \
	fi; \
	REMOTE_TAG=$$(git ls-remote origin "refs/tags/$$TAG^{}" | awk '{print $$1}'); \
	if [[ -z "$$REMOTE_TAG" ]]; then \
		REMOTE_TAG=$$(git ls-remote origin "refs/tags/$$TAG" | awk '{print $$1}'); \
	fi; \
	if [[ -n "$$REMOTE_TAG" && "$$REMOTE_TAG" != "$$HEAD_SHA" ]]; then \
		echo "ERROR: remote tag $$TAG points to $$REMOTE_TAG, not HEAD $$HEAD_SHA"; \
		exit 1; \
	fi; \
	if git rev-parse -q --verify "refs/tags/$$TAG" >/dev/null; then \
		TAG_SHA=$$(git rev-list -n 1 "$$TAG"); \
		if [[ "$$TAG_SHA" != "$$HEAD_SHA" ]]; then \
			echo "ERROR: local tag $$TAG points to $$TAG_SHA, not HEAD $$HEAD_SHA"; \
			exit 1; \
		fi; \
		echo "  Local tag $$TAG already points to HEAD."; \
	else \
		git tag -a "$$TAG" -m "dddjango $$VERSION"; \
		echo "  Created local tag $$TAG."; \
	fi; \
	echo "[6/7] Push main"; \
	git push origin main; \
	echo "[7/7] Push tag"; \
	if [[ -n "$$REMOTE_TAG" ]]; then \
		echo "  Remote tag $$TAG already points to HEAD."; \
	else \
		git push origin "$$TAG"; \
	fi; \
	echo "Release $$VERSION complete."
