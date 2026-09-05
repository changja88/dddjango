#!/usr/bin/env bash
# dddjango-web 시안 절단 도구 3종 자기 회귀 픽스처 (extract_design·extract_dc·fetch_images).
# 케이스마다 negative(오류 검출)에 positive-control(정상 통과) 짝을 둔다:
#   D1(정상) ↔ D2(tokens[] 부재)·D3(토큰 0)·U1(사용법)
#   H1(정상) ↔ H2(HTML 0)·H3(토큰 0)
#   C1(정상) ↔ C2(tokens 부재·순서 계약)·C3(.screen 부재)·C4(.dc.html 부재)
#   F1(정상·혼합 status)·F3(토큰 충돌·결정론) ↔ F2(design-ref 부재)
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

assert_file() { # assert_file <이름> <파일> <있어야 할 고정문자열|-> <없어야 할 고정문자열|->
  local name="$1" file="$2" want="$3" unwant="$4" ok=1
  [ ! -f "$file" ] && ok=0
  [ $ok = 1 ] && [ "$want" != "-" ] && ! grep -qF -- "$want" "$file" && ok=0
  [ $ok = 1 ] && [ "$unwant" != "-" ] && grep -qF -- "$unwant" "$file" && ok=0
  if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS $name"; else
    FAIL=$((FAIL+1)); echo "FAIL $name ($file)"
    [ -f "$file" ] && head -30 "$file" | sed 's/^/    /' || echo "    (파일 없음)"
  fi
}

png_fixture() { python3 - "$SCRIPTS/test" "$1" <<'PYPNG'
import pathlib, sys
sys.path.insert(0, sys.argv[1])
from test_assets import png
pathlib.Path(sys.argv[2]).write_bytes(png())
PYPNG
} # 실제 complete PNG: 매직 헤더만으로 성공시키지 않는다.

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# ========== extract_design — ds-manifest 모드 ==========

# ---------- D1(positive control): kind 버킷 분류·var() 해소·other drop
P="$T/d1"; mkdir -p "$P"
cat > "$P/_ds_manifest.json" <<'EOF'
{
  "tokens": [
    {"name": "--brand", "value": "#1173D4", "kind": "color"},
    {"name": "--accent", "value": "var(--brand)", "kind": "color"},
    {"name": "--fs-lg", "value": "18px", "kind": "font"},
    {"name": "--sp-2", "value": "8px", "kind": "spacing"},
    {"name": "--radius-card", "value": "12px", "kind": "radius"},
    {"name": "--shadow-card", "value": "0 1px 2px rgba(0,0,0,.1)", "kind": "shadow"},
    {"name": "--z-modal", "value": "40", "kind": "other"}
  ]
}
EOF
OUT=$(run_py extract_design.py --from-ds-manifest "$P/_ds_manifest.json" --out "$P/design-tokens.json"); E=$?
assert "D1 dsManifest 정상(exit 0)" 0 "[extract-design] dsManifest" - "$E" "$OUT"
assert_file "D1 var() 자기참조 해소" "$P/design-tokens.json" '"--accent": "#1173D4"' -
assert_file "D1 shadow 버킷·other drop" "$P/design-tokens.json" '"--shadow-card"' '--z-modal'

# ---------- D2: tokens[] 부재 → exit 1
P="$T/d2"; mkdir -p "$P"
echo '{"name": "no-tokens-here"}' > "$P/_ds_manifest.json"
OUT=$(run_py extract_design.py --from-ds-manifest "$P/_ds_manifest.json" --out "$P/out.json"); E=$?
assert "D2 tokens[] 부재 fail-loud" 1 "tokens 배열 없음" - "$E" "$OUT"

# ---------- D3: kind other만 → 토큰 0 fail-loud
P="$T/d3"; mkdir -p "$P"
echo '{"tokens": [{"name": "--z", "value": "40", "kind": "other"}]}' > "$P/_ds_manifest.json"
OUT=$(run_py extract_design.py --from-ds-manifest "$P/_ds_manifest.json" --out "$P/out.json"); E=$?
assert "D3 토큰 0 fail-loud" 1 "토큰 0" - "$E" "$OUT"

# ---------- U1: 사용법(인자 없음) → exit 1
OUT=$(run_py extract_design.py); E=$?
assert "U1 extract_design 사용법" 1 "사용" - "$E" "$OUT"

# ========== extract_design — 참조 HTML 모드 ==========

# ---------- H1(positive control): tailwind-config 명명 토큰 + 빈도 후보 + 임의값
P="$T/h1"; mkdir -p "$P/design-ref"
cat > "$P/design-ref/ref.html" <<'EOF'
<!doctype html>
<title>Ref</title>
<script id="tailwind-config">
tailwind.config = {
  theme: {
    extend: {
      colors: { primary: "#1173d4", surface: { light: "#f6f7f8" } },
      spacing: { gutter: "24px" },
      borderRadius: { card: "12px" },
      fontFamily: { display: ["Inter", "sans-serif"] },
      fontSize: { hero: ["32px", { lineHeight: "40px" }] },
    },
  },
}
</script>
<style>
.a { color: #222222; margin: 8px 16px; border-radius: 6px; box-shadow: 0 1px 2px #00000022; }
.b { color: #222222; font-size: 14px; }
</style>
<div class="p-[13px] hover:bg-[#ff0000]" style="color:#e63946; padding: 4px">x</div>
EOF
OUT=$(run_py extract_design.py "$P/design-ref" --out "$P/design-tokens.json"); E=$?
assert "H1 참조 HTML 정상(exit 0)" 0 "[extract-design] 참조 HTML 1" - "$E" "$OUT"
assert_file "H1 tailwind 명명 색(중첩 평탄화)" "$P/design-tokens.json" '"surface-light": "#f6f7f8"' -
assert_file "H1 빈도 1위 색 후보" "$P/design-tokens.json" '"color-1": "#222222"' -
assert_file "H1 타이포(config fontSize)" "$P/design-tokens.json" '"size": "32px"' -
assert_file "H1 임의값 클래스(변형 접두 제거)" "$P/design-tokens.json" '"bg-[#ff0000]"' 'hover:'
# H1b: 단일 .html 위치 인자(커맨드 115행 호출형)도 동작
OUT=$(run_py extract_design.py "$P/design-ref/ref.html" --out "$P/design-tokens-single.json"); E=$?
assert "H1b 단일 파일 위치 인자" 0 "[extract-design] 참조 HTML 1" - "$E" "$OUT"

# ---------- H2: 디렉터리에 HTML 0 → exit 1
P="$T/h2"; mkdir -p "$P/design-ref"
OUT=$(run_py extract_design.py "$P/design-ref" --out "$P/out.json"); E=$?
assert "H2 동결 HTML 없음 fail-loud" 1 "동결 HTML 없음" - "$E" "$OUT"

# ---------- H3: 스타일 없는 HTML → 토큰 0 fail-loud
P="$T/h3"; mkdir -p "$P/design-ref"
echo '<html><body><p>hello</p></body></html>' > "$P/design-ref/plain.html"
OUT=$(run_py extract_design.py "$P/design-ref" --out "$P/out.json"); E=$?
assert "H3 토큰 0 fail-loud" 1 "토큰 0" - "$E" "$OUT"

# ========== extract_dc ==========

mk_dc() { # mk_dc <파일> — .screen + device-chrome(.stage/.phone/.statusbar/.decor) 구분 미니 .dc.html
  cat > "$1" <<'EOF'
<!doctype html>
<div class="stage">
  <div class="phone">
    <div class="statusbar"><span>9:41</span><img src="chrome-battery.png"></div>
    <div class="screen">
      <div class="title">주문 목록</div>
      <div class="subtitle">오늘의 주문</div>
      <div class="card"><div class="rtitle">배송 준비</div></div>
      <div class="card"><div class="rtitle">배송 완료</div></div>
      <img src="assets/logo.png" alt="로고">
    </div>
    <div class="decor"></div>
  </div>
</div>
EOF
}

# ---------- C1(positive control): .screen만 절단·chrome 제외·meta·로컬 img 복사
P="$T/c1"; mkdir -p "$P/design-ref/assets" "$P/root"
mk_dc "$P/design-ref/order-list.dc.html"
png_fixture "$P/design-ref/assets/logo.png"
cp "$T/d1/design-tokens.json" "$P/design-tokens.json" # 순서 계약: extract_design 산출 선행
OUT=$(run_py extract_dc.py "$P/design-ref/order-list.dc.html" --tokens "$P/design-tokens.json" \
  --asset-manifest "$P/asset-manifest.json" --assets-root "$P/root" \
  --asset-base "$P/design-ref" --meta "$P/screen-meta.json"); E=$?
assert "C1 extract_dc 정상(exit 0)" 0 "[extract-dc] order-list.dc.html" - "$E" "$OUT"
assert_file "C1 게이트 텍스트 title" "$P/screen-meta.json" '"title": "주문 목록"' -
assert_file "C1 게이트 텍스트 cards" "$P/screen-meta.json" '"배송 완료"' -
assert_file "C1 이미지 ok·device-chrome 제외" "$P/asset-manifest.json" '"local_path": "web/static/images/logo_b1ff9c8ea3a7.png"' 'chrome-battery'
assert_file "C1 이미지 바이트 착지" "$P/root/web/static/images/logo_b1ff9c8ea3a7.png" - -

# ---------- C2: design-tokens.json 부재 → 순서 계약 위반 exit 1
P="$T/c2"; mkdir -p "$P/design-ref" "$P/root"
mk_dc "$P/design-ref/order-list.dc.html"
OUT=$(run_py extract_dc.py "$P/design-ref/order-list.dc.html" --tokens "$P/design-tokens.json" \
  --asset-manifest "$P/asset-manifest.json" --assets-root "$P/root" \
  --asset-base "$P/design-ref" --meta "$P/screen-meta.json"); E=$?
assert "C2 tokens 부재(순서 계약 MF-3)" 1 "design-tokens.json 부재" - "$E" "$OUT"

# ---------- C3: .screen 부재(.stage/.phone 크롬만) → exit 1
P="$T/c3"; mkdir -p "$P/design-ref" "$P/root"
cat > "$P/design-ref/chrome-only.dc.html" <<'EOF'
<div class="stage"><div class="phone"><div class="statusbar">9:41</div></div></div>
EOF
echo '{}' > "$P/design-tokens.json"
OUT=$(run_py extract_dc.py "$P/design-ref/chrome-only.dc.html" --tokens "$P/design-tokens.json" \
  --asset-manifest "$P/asset-manifest.json" --assets-root "$P/root" \
  --asset-base "$P/design-ref" --meta "$P/screen-meta.json"); E=$?
assert "C3 .screen 부재 fail-loud" 1 ".screen" - "$E" "$OUT"

# ---------- C4: .dc.html 부재 → exit 1
P="$T/c4"; mkdir -p "$P"
echo '{}' > "$P/design-tokens.json"
OUT=$(run_py extract_dc.py "$P/no-such.dc.html" --tokens "$P/design-tokens.json" \
  --asset-manifest "$P/asset-manifest.json" --assets-root "$P" \
  --asset-base "$P" --meta "$P/screen-meta.json"); E=$?
assert "C4 .dc.html 부재 fail-loud" 1 ".dc.html 부재" - "$E" "$OUT"

# ========== fetch_images ==========

# ---------- F1(positive control): 혼합 status(ok/inline/failed/skipped) — 부분 실패에도 exit 0
P="$T/f1"; mkdir -p "$P/design-ref/images" "$P/root"
png_fixture "$P/design-ref/images/hero.png"
cat > "$P/design-ref/ref.html" <<'EOF'
<img src="images/hero.png" alt="hero">
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC">
<img src="images/missing.png">
<img src=http://127.0.0.1:9/x.png>
<img src={dynamicExpr}>
EOF
OUT=$(run_py fetch_images.py "$P/design-ref" --assets-root "$P/root" \
  --asset-base "$P/design-ref" --out "$P/asset-manifest.json"); E=$?
assert "F1 혼합 status·부분 실패 exit 0" 0 "ok 1·failed 2·inline 1·skipped 1" - "$E" "$OUT"
assert "F1 실패 [warn] stderr 표면화" 0 "[warn] 이미지 failed: images/missing.png" - "$E" "$OUT"
assert_file "F1 로컬 상대경로 해소(ok)" "$P/asset-manifest.json" '"token": "hero"' -
assert_file "F1 인라인 착지" "$P/root/web/static/images/ref_2_b1ff9c8ea3a7.png" - -

# ---------- F2: design-ref 부재 → exit 1
OUT=$(run_py fetch_images.py "$T/no-such-dir" --assets-root "$T" --out "$T/out.json"); E=$?
assert "F2 design-ref 부재" 1 "design-ref 디렉터리 없음" - "$E" "$OUT"

# ---------- F3: 소스명 토큰 충돌 → 해시 접미 + 2회 실행 결정론
P="$T/f3"; mkdir -p "$P/design-ref/a" "$P/design-ref/b" "$P/root"
png_fixture "$P/design-ref/a/logo.png"
png_fixture "$P/design-ref/b/logo.png"
cat > "$P/design-ref/ref.html" <<'EOF'
<img src="a/logo.png"><img src="b/logo.png">
EOF
OUT=$(run_py fetch_images.py "$P/design-ref" --assets-root "$P/root" \
  --asset-base "$P/design-ref" --out "$P/out1.json"); E=$?
assert "F3 충돌 해시 접미(exit 0·ok 2)" 0 "ok 2" - "$E" "$OUT"
assert_file "F3 첫 토큰은 slug 그대로" "$P/out1.json" '"token": "logo"' -
assert_file "F3 충돌분은 해시 접미" "$P/out1.json" '"token": "logo_' -
OUT=$(run_py fetch_images.py "$P/design-ref" --assets-root "$P/root" \
  --asset-base "$P/design-ref" --out "$P/out2.json"); E=$?
if cmp -s "$P/out1.json" "$P/out2.json"; then PASS=$((PASS+1)); echo "PASS F3 2회 실행 결정론(byte 동일)"; else
  FAIL=$((FAIL+1)); echo "FAIL F3 2회 실행 결정론"; diff "$P/out1.json" "$P/out2.json" | head -10 | sed 's/^/    /'
fi

# ========== 결과 ==========
echo "----------------------------------------"
echo "fixtures_extract: PASS $PASS · FAIL $FAIL"
[ "$FAIL" = 0 ] || exit 1
