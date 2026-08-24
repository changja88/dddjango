#!/usr/bin/env bash
# dddjango-web G2 렌더 실측 대조 도구(compare_render_audit) 자기 회귀 픽스처.
# 케이스마다 negative(오류 검출)에 positive-control(정상 통과) 짝을 둔다:
#   A1(정상·중복 키 그룹 포함) ↔ A2(크기)·A3(pinned 소실)·A4(상대 위치)·A5(그룹 분포)·A6(행간 normal)
#   A7(미조인만 → diff 0) · V1(--validate 정상) ↔ S1(audit_version 부재)·U1(사용법)
#   DET(결정론 — 같은 입력 2회 byte 동일 출력; compare 출력이 G2 증적이므로 필수)
# 입력 JSON은 render_audit.js 스키마(audit_version 1)의 수제 표본이다 — 스키마가
# 어긋나면 S1 계열 fail-loud가 잡는다(생산자-소비자 결정적 연결).
set -u
SCRIPTS="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0; FAIL=0

run_py() { python3 "$SCRIPTS/$1" "${@:2}" 2>&1; }

assert() { # assert <이름> <기대exit> <출력에 있어야 할 고정문자열|-> <없어야 할 고정문자열|-> <실제exit> <출력>
  local name="$1" wantexit="$2" want="$3" unwant="$4" gotexit="$5" out="$6" ok=1
  [ "$gotexit" != "$wantexit" ] && ok=0
  [ "$want" != "-" ] && ! grep -qF -- "$want" <<<"$out" && ok=0
  [ "$unwant" != "-" ] && grep -qF -- "$unwant" <<<"$out" && ok=0
  if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS $name"; else
    FAIL=$((FAIL+1)); echo "FAIL $name (exit=$gotexit want=$wantexit)"; echo "$out" | head -20 | sed 's/^/    /'
  fi
}

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# 표본 생성 — 목표(base)와 변형들(결정론: json.dump 고정 인자)
python3 - "$T" <<'EOF'
import copy, json, sys
T = sys.argv[1]

def text(key, txt, size, weight, lh, align, color, x, y, w=100, h=20):
    return {"key": key, "text": txt, "fontSize": size, "weight": weight,
            "lineHeight": lh, "textAlign": align, "color": color,
            "fontFamily": "Pretendard", "rect": {"x": x, "y": y, "w": w, "h": h}}

base = {
    "audit_version": 1, "url": "http://t/saju", "viewport": {"w": 1440, "h": 900},
    "column": {"width": 430, "x": 505}, "scroll": {"mode": "document", "height": 7000},
    "textsTruncated": False, "pinnedTruncated": False, "partial": False,
    "texts": [
        text("헤더", "헤더", "16px", 700, "21px", "start", "rgb(255, 255, 255)", 706, 10),
        text("카드 제목", "카드 제목", "18px", 700, "24px", "center", "rgb(255, 255, 255)", 616, 445),
        # 중복 키 그룹(숫자 접기 «#%») — A1 green의 그룹 경로 커버
        text("#%", "50%", "12px", 700, "16px", "start", "rgb(25, 31, 40)", 547, 319, 27, 16),
        text("#%", "70%", "12px", 700, "16px", "start", "rgb(25, 31, 40)", 547, 519, 27, 16),
    ],
    "pinned": [{"position": "sticky", "rect": {"x": 505, "y": 774, "w": 430, "h": 126},
                "key": "#명 확인 중", "text": "2,274명 확인 중"}],
}

def dump(name, obj):
    with open(f"{T}/{name}.json", "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, sort_keys=True)

dump("target", base)
dump("same", copy.deepcopy(base))

v = copy.deepcopy(base); v["texts"][0]["fontSize"] = "18px"; dump("size-diff", v)
v = copy.deepcopy(base); v["pinned"] = []; dump("pinned-lost", v)
# 부분 소실 — 목표 pinned 2개 중 구현엔 1개만 (키 차집합 발화 검증)
v = copy.deepcopy(base)
v["pinned"] = [dict(v["pinned"][0]), {"position": "sticky", "rect": {"x": 505, "y": 0, "w": 430, "h": 40},
               "key": "고정 헤더", "text": "고정 헤더"}]
dump("target-pinned2", v)
v2 = copy.deepcopy(v); v2["pinned"] = [dict(v["pinned"][0])]; dump("pinned-partial", v2)
v = copy.deepcopy(base); v["texts"][1]["rect"]["x"] = 525; dump("pos-diff", v)  # Δcenter-x 91px/430 > 5%
v = copy.deepcopy(base); v["texts"][2]["weight"] = 600; dump("group-diff", v)
v = copy.deepcopy(base); v["texts"][0]["lineHeight"] = "normal"; dump("lh-normal", v)
v = copy.deepcopy(base); v["texts"][0]["key"] = "다른 문구"; v["texts"][0]["text"] = "다른 문구"; dump("unjoined", v)
v = copy.deepcopy(base); del v["audit_version"]; dump("no-version", v)
EOF

# ---------- V1(positive control): --validate 정상
OUT=$(run_py compare_render_audit.py --validate "$T/target.json"); E=$?
assert "V1 validate 정상" 0 "validate OK" - "$E" "$OUT"

# ---------- A1(positive control): 동일 실측 → diff 0 (중복 키 그룹 경로 포함)
OUT=$(run_py compare_render_audit.py "$T/target.json" "$T/same.json"); E=$?
assert "A1 동일 실측 diff 0" 0 "diff 0건" "DIFF" "$E" "$OUT"

# ---------- A2: font-size 어긋남 → exit 2
OUT=$(run_py compare_render_audit.py "$T/target.json" "$T/size-diff.json"); E=$?
assert "A2 font-size diff" 2 "font-size 16px ↔ 18px" - "$E" "$OUT"

# ---------- A3: pinned 소실 → exit 2
OUT=$(run_py compare_render_audit.py "$T/target.json" "$T/pinned-lost.json"); E=$?
assert "A3 고정 요소 소실" 2 "고정 요소 소실" - "$E" "$OUT"

# ---------- A3b: pinned 부분 소실(2→1 — 키 차집합) → exit 2
OUT=$(run_py compare_render_audit.py "$T/target-pinned2.json" "$T/pinned-partial.json"); E=$?
assert "A3b 고정 요소 부분 소실" 2 "가 구현 pinned에 없음" - "$E" "$OUT"

# ---------- A4: 상대 위치(center-x) → exit 2
OUT=$(run_py compare_render_audit.py "$T/target.json" "$T/pos-diff.json"); E=$?
assert "A4 상대 위치 diff" 2 "상대 위치 center-x" - "$E" "$OUT"

# ---------- A5: 중복 키 그룹 분포 불일치 → exit 2
OUT=$(run_py compare_render_audit.py "$T/target.json" "$T/group-diff.json"); E=$?
assert "A5 그룹 분포 불일치" 2 "축 분포 불일치" - "$E" "$OUT"

# ---------- A6: line-height normal↔px → exit 2
OUT=$(run_py compare_render_audit.py "$T/target.json" "$T/lh-normal.json"); E=$?
assert "A6 line-height normal 특례" 2 "line-height" - "$E" "$OUT"

# ---------- A7: 미조인만 → 정보 표기·diff 0·exit 0
OUT=$(run_py compare_render_audit.py "$T/target.json" "$T/unjoined.json"); E=$?
assert "A7 미조인만 diff 0" 0 "미조인" "DIFF" "$E" "$OUT"

# ---------- S1: audit_version 부재 → fail-loud exit 1
OUT=$(run_py compare_render_audit.py "$T/target.json" "$T/no-version.json"); E=$?
assert "S1 audit_version fail-loud" 1 "audit_version" - "$E" "$OUT"

# ---------- U1: 사용법 → exit 1
OUT=$(run_py compare_render_audit.py); E=$?
assert "U1 사용법" 1 "사용" - "$E" "$OUT"

# ---------- DET: 결정론 — 같은 red 입력 2회 byte 동일 출력
O1=$(run_py compare_render_audit.py "$T/target.json" "$T/size-diff.json")
O2=$(run_py compare_render_audit.py "$T/target.json" "$T/size-diff.json")
if [ "$O1" = "$O2" ]; then PASS=$((PASS+1)); echo "PASS DET 결정론(2회 동일)"; else
  FAIL=$((FAIL+1)); echo "FAIL DET 결정론(2회 동일)"; diff <(echo "$O1") <(echo "$O2") | head -10 | sed 's/^/    /'
fi

echo "----------------------------------------"
echo "fixtures_audit: PASS $PASS · FAIL $FAIL"
[ $FAIL = 0 ] || exit 1
