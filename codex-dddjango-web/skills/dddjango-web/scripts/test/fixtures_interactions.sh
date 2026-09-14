#!/usr/bin/env bash
# K3 상호작용 관찰 증거 자기 회귀 픽스처 — 검사기(Python)·순수 JS 정본·브라우저 드라이버
# 3종을 한 러너로 묶는다. 브라우저 스위트(test_observe_interactions.mjs)는 SKIP 의미론을
# 스스로 소유한다(env 미설정 → `SKIP: …` 한 줄 + exit 0, `DDDJANGO_WEB_REQUIRE_BROWSER=1`
# 이면 `ERROR:` + exit 1) — 이 러너와 `make verify-web`은 env를 그대로 물려줄 뿐 판단하지
# 않는다. 실제 브라우저 실행은 별도 타깃 `make verify-web-browser`가 env를 채워 돈다.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 "$HERE/test_interaction_evidence.py"
node --test "$HERE/test_interaction_audit.mjs"
node --test "$HERE/test_observe_interactions.mjs"
