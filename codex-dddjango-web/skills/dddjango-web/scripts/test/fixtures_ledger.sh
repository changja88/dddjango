#!/usr/bin/env bash
# dddjango-web 미검증 원장(ledger) 행동 시험 러너.
# test_ledger.py 는 test_interaction_evidence 의 합성 빌드 하네스를 상속한다 —
# 부모 시험(45건)도 같이 돌아 원장 삽입이 기존 판정을 바꾸지 않았음을 함께 보증한다.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 "$HERE/test_ledger.py"
