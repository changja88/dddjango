#!/usr/bin/env bash
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 "$HERE/test_design_evidence.py"
python3 "$HERE/test_design_archive.py"
