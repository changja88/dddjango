#!/usr/bin/env bash
# 재동결 집행 도구(refreeze.py) 자기 회귀 — run_fixtures.sh가 자동 수집.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
FAILED=0
python3 "$HERE/test_refreeze.py" || FAILED=1
exit $FAILED
