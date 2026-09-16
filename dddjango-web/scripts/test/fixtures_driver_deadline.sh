#!/usr/bin/env bash
# 관찰 드라이버 정지 방어 — 정적 자기집행 검사.
#
# `--max-steps`·`--max-minutes` 는 **항목 사이에서만** 재므로 한 `await` 가 안 풀리면
# 상한이 영영 발화하지 않는다(실측: A8 세션이 8시간 52분 정지 · CPU 0.0%).
# `page.setDefaultTimeout` 이 그걸 막아 주지만 Playwright 의 `evaluate` 계열과
# `CDPSession.send` 에는 타임아웃 인자가 없다 — 그 계열을 전부 `withDeadline()` 으로
# 통과시키는 것이 v1.1.20 의 보증이다.
#
# 이 픽스처가 그 보증의 **기제**다. 감싸지 않은 호출이 하나라도 새로 들어오면 red 다 —
# 규범만 적어 두면 다음 편집 한 줄로 구멍이 다시 열린다.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
DRIVER="$HERE/../../assets/observe_interactions.pw.js"
PASS=0; FAIL=0

check() {   # check <이름> <기대(ok|red)> <실제(ok|red)> [상세]
  if [ "$2" = "$3" ]; then PASS=$((PASS+1)); echo "PASS $1"
  else FAIL=$((FAIL+1)); echo "FAIL $1 — 기대 $2 · 실제 $3 ${4:-}"; fi
}

scan() {   # 감싸지 않은 evaluate/evaluateHandle/send 호출 줄 — withDeadline 정의 자체는 뺀다
  python3 - "$1" <<'PY'
import re, sys
from pathlib import Path
WRAP = "withDeadline("
text = Path(sys.argv[1]).read_text(encoding="utf-8")
start = text.find("function withDeadline(")
end = text.find("\n}\n", start) if start >= 0 else -1
# 수신자 사슬의 **앞이 단어·점이 아닐 때만** 시작으로 본다 — 그래야 이미 감싼
# `withDeadline(ctx.page.evaluate(` 의 안쪽 `page.evaluate(` 를 다시 잡지 않는다.
PAT = re.compile(r"(?<![\w.$])((?:ctx\.page|page|handle|element|frame|ctx\.cdp)"
                 r"\.(?:evaluate|evaluateHandle|send)\()")
bad = []
for m in PAT.finditer(text):
    at = m.start(1)
    if start >= 0 and start <= at <= end:
        continue
    if text[max(0, at - len(WRAP)):at] == WRAP:
        continue
    bad.append((text.count("\n", 0, at) + 1, m.group(1)))
for line, call in bad:
    print(f"{line}:{call}")
sys.exit(1 if bad else 0)
PY
}

# D1 — 정본 드라이버에 감싸지 않은 호출이 없다.
if out=$(scan "$DRIVER"); then check "D1_정본_전건_감쌈" ok ok
else check "D1_정본_전건_감쌈" ok red "$(printf '%s' "$out" | tr '\n' ' ')"; fi

# D2 — 검사가 실제로 잡는가(음성 대조). 감싸지 않은 호출을 하나 심은 사본은 red 여야 한다.
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
{ echo 'const _probe = async (page) => await page.evaluate(() => 1);'; cat "$DRIVER"; } > "$TMP/probe.js"
if scan "$TMP/probe.js" >/dev/null 2>&1; then check "D2_미감쌈_검출" red ok "심은 호출을 놓쳤다"
else check "D2_미감쌈_검출" red red; fi

# D3 — withDeadline 정의가 실재하고 워치독이 배선돼 있다.
grep -q "function withDeadline(" "$DRIVER" \
  && grep -q "function armWatchdog(" "$DRIVER" \
  && grep -q "disarm = armWatchdog(" "$DRIVER" \
  && check "D3_워치독_배선" ok ok || check "D3_워치독_배선" ok red

# D4 — 워치독은 문서를 쓰지 않는다(써 버리면 sha 가 실물과 어긋난 문서가 조용히 통과한다).
if python3 - "$DRIVER" <<'PY'
import sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding="utf-8")
start = text.index("function armWatchdog(")
body = text[start:text.index("\n}\n", start)]
sys.exit(1 if ("writeDocument" in body or "buildDocument" in body) else 0)
PY
then check "D4_워치독_문서_미작성" ok ok; else check "D4_워치독_문서_미작성" ok red; fi

# D5 — 문법이 유효하다(괄호 매칭 회귀).
if node --check "$DRIVER" >/dev/null 2>&1; then check "D5_문법" ok ok; else check "D5_문법" ok red; fi

echo "fixtures_driver_deadline: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ]
