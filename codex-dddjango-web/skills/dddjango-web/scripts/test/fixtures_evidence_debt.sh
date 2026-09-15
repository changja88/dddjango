#!/usr/bin/env bash
# 증거 부채 술어(evidence_debt.py)·hook 스크립트(evidence_debt_hook.py) 자기 회귀 — run_fixtures.sh가 자동 수집.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
FAILED=0
python3 "$HERE/test_evidence_debt.py" || FAILED=1
python3 "$HERE/test_evidence_debt_hook.py" || FAILED=1
exit $FAILED
