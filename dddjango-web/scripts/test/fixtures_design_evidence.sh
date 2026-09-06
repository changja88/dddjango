#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 "$HERE/test_design_evidence.py"
