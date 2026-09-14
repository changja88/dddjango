#!/usr/bin/env bash
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 "$HERE/test_design_evidence.py"
python3 "$HERE/test_design_archive.py"
# test_interaction_evidence.py(K3 검사기)는 fixtures_interactions.sh가 돌린다 — 한 곳에서만(Task 10 리뷰 Minor).
