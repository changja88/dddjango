#!/usr/bin/env bash
# dddjango-web 빚 스캔·잔존 픽스처 (--debt-scan · --debt-residual — Phase 0 step 4′·G2).
# mktemp 임시 git 프로젝트 + 각 red 에 양성 대조 짝. mkproj 판형은 fixtures_backstop.sh 와 같다.
set -u
SCRIPTS="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0; FAIL=0

run_backstop() { python3 "$SCRIPTS/backstop.py" "$@" 2>&1; }

assert() { # assert <이름> <기대exit> <있어야 할 문자열|-> <없어야 할 문자열|-> <실제exit> <출력>
  local name="$1" wantexit="$2" want="$3" unwant="$4" gotexit="$5" out="$6" ok=1
  [ "$gotexit" != "$wantexit" ] && ok=0
  [ "$want" != "-" ] && ! grep -qF -- "$want" <<<"$out" && ok=0
  [ "$unwant" != "-" ] && grep -qF -- "$unwant" <<<"$out" && ok=0
  if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS $name"; else
    FAIL=$((FAIL+1)); echo "FAIL $name (exit=$gotexit want=$wantexit)"; echo "$out" | head -20 | sed 's/^/    /'
  fi
}

counts_of() { # counts_of <debt json> — "키=수" 정렬 목록
  python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(" ".join("%s=%d" % (k, d["counts"][k]) for k in sorted(d["counts"])))' "$1"
}

field_of() { # field_of <debt json> <필드> — JSON 값(키 정렬)
  python3 -c 'import json,sys; print(json.dumps(json.load(open(sys.argv[1]))[sys.argv[2]], sort_keys=True, ensure_ascii=False))' "$1" "$2"
}

commit_all() { # commit_all <dir> <msg> — HEAD 해시 출력
  git -C "$1" -c user.name=t -c user.email=t@t add -A >/dev/null
  git -C "$1" -c user.name=t -c user.email=t@t commit -qm "$2"
  git -C "$1" rev-parse HEAD
}

mkproj() { # mkproj <dir> — Django풍 루트 + 표준 web/ 골격(green) + git 초기 커밋, BASE 출력
  local p="$1"
  mkdir -p "$p/config" "$p/web/base" \
    "$p/web/design_system/foundation" "$p/web/design_system/component/button" \
    "$p/web/static/css" "$p/web/static/js" "$p/web/static/htmx" "$p/web/static/images" \
    "$p/web/orders/widget" \
    "$p/web/orders/order_list/view" "$p/web/orders/order_list/view_model" \
    "$p/web/orders/order_list/state" "$p/web/orders/order_list/section" \
    "$p/web/client/orders/response"
  echo "SECRET_KEY = 'x'" > "$p/config/settings.py"
  echo "# manage" > "$p/manage.py"
  : > "$p/web/__init__.py"
  echo "urlpatterns = []" > "$p/web/urls.py"
  printf 'from django.apps import AppConfig\n\n\nclass WebConfig(AppConfig):\n    name = "web"\n' > "$p/web/apps.py"
  cat > "$p/web/base/base.html" <<'EOF'
{% load static %}
<html>
  <head><title>app</title></head>
  <body>
    <a href="{% url 'order_list' %}">orders</a>
    <script src="{% static 'web/htmx/htmx.min.js' %}" defer></script>
  </body>
</html>
EOF
  printf ':root { --color-text: #222222; --color-primary: rgb(10, 20, 30); }\n' > "$p/web/design_system/foundation/tokens.css"
  printf '/* 공용 keyframes·모션 유틸(motion-*) — 값 정의는 tokens.css */\n' > "$p/web/design_system/foundation/motion.css"
  printf '<button class="btn">ok</button>\n' > "$p/web/design_system/component/button/primary_button.html"
  printf 'body { color: var(--color-text); }\n' > "$p/web/static/css/site.css"
  printf '(function(){})();\n' > "$p/web/static/htmx/htmx.min.js"
  : > "$p/web/static/images/.gitkeep"
  echo "urlpatterns = []" > "$p/web/orders/urls.py"
  printf '<span class="badge">ok</span>\n' > "$p/web/orders/widget/order_status_badge.html"
  : > "$p/web/orders/order_list/view/__init__.py"
  printf 'def order_list_view(request):\n    return None\n' > "$p/web/orders/order_list/view/order_list_view.py"
  printf '{%% extends "base.html" %%}\n' > "$p/web/orders/order_list/view/order_list.html"
  : > "$p/web/orders/order_list/view_model/__init__.py"
  cat > "$p/web/orders/order_list/view_model/order_list_view_model.py" <<'EOF'
from web.client.orders.order_query_client import OrderQueryClient


class OrderListViewModel:
    pass
EOF
  : > "$p/web/orders/order_list/state/__init__.py"
  cat > "$p/web/orders/order_list/state/order_list_state.py" <<'EOF'
from dataclasses import dataclass


@dataclass
class OrderListState:
    total: int = 0
EOF
  cat > "$p/web/orders/order_list/section/order_list_filter_bar.html" <<'EOF'
<div hx-get="{% url 'order_list' %}">filter</div>
EOF
  : > "$p/web/client/__init__.py"
  : > "$p/web/client/orders/__init__.py"
  cat > "$p/web/client/orders/order_query_client.py" <<'EOF'
ORDERS_URL = "/api/orders/"


class OrderQueryClient:
    pass
EOF
  : > "$p/web/client/orders/response/__init__.py"
  printf 'class OrderSummaryResponse:\n    pass\n' > "$p/web/client/orders/response/order_summary_response.py"
  git -C "$p" init -q
  commit_all "$p" base
}

run_folder() { # run_folder <proj> <폴더> — .dddjango-web/<폴더>/ 생성 + G0 동결(debt-g0.json)
  mkdir -p "$1/.dddjango-web/$2"
  run_backstop "$1" --debt-scan --json "$1/.dddjango-web/$2/debt-g0.json" >/dev/null
}

scope_md() { # scope_md <proj> <폴더> <본문> — refactor-scope.md 기록(@NOW@ = 지금 분 — G0 절은 스캔 뒤에 쓴다)
  local body="${3//@NOW@/$(date '+%Y-%m-%d %H:%M')}"
  printf '%s\n' "$body" > "$1/.dddjango-web/$2/refactor-scope.md"
}

bad_images() { # bad_images <proj> — WN8 파일명 위반 3건(현장형 kebab-case) 커밋
  printf 'png' > "$1/web/static/images/a-b.png"
  printf 'png' > "$1/web/static/images/c-d.png"
  printf 'png' > "$1/web/static/images/e-f.png"
  commit_all "$1" bad-images >/dev/null
}

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# ---------- D1: 깨끗한 표준 골격 = 빚 0 · 기록 폴더는 dirty 판정 밖
P="$T/d1"; mkproj "$P" >/dev/null
mkdir -p "$P/.dddjango-web/run"
OUT=$(run_backstop "$P" --debt-scan --json "$P/.dddjango-web/run/debt-g0.json"); E=$?
assert "D1a 표준 골격 빚 0" 0 "빚 스캔 — 키 0 · 발견 0" "BLOCKER" "$E" "$OUT"
assert "D1b .dddjango-web 미추적은 dirty 아님" 0 "false" - 0 "$(field_of "$P/.dddjango-web/run/debt-g0.json" dirty)"
echo x > "$P/notes.txt"
run_backstop "$P" --debt-scan --json "$P/.dddjango-web/run/debt-g0.json" >/dev/null
assert "D1c 대조: 루트 미추적 파일은 dirty" 0 "true" - 0 "$(field_of "$P/.dddjango-web/run/debt-g0.json" dirty)"

# ---------- D2: .gitignore 가 무시하는 파일은 거짓 빚이 아니다(os.walk 대신 git 우주)
P="$T/d2"; mkproj "$P" >/dev/null
printf '.DS_Store\n' > "$P/.gitignore"; commit_all "$P" ignore >/dev/null
printf 'x' > "$P/web/static/images/.DS_Store"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D2a 무시 파일 .DS_Store 키 0" 0 "키 0" ".DS_Store" "$E" "$OUT"
rm "$P/.gitignore"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D2b 대조: 무시 안 된 .DS_Store 는 빚" 2 ".DS_Store" - "$E" "$OUT"

# ---------- D3: 브라운필드 legacy htmx core 1개 + 그 base 로드 태그(defer 없음) = 빚 아님 · 중복은 빚
P="$T/d3"; mkproj "$P" >/dev/null
rm "$P/web/static/htmx/htmx.min.js"
printf '(function(){})();\n' > "$P/web/static/js/htmx.min.js"
cat > "$P/web/base/base.html" <<'HTML'
{% load static %}<html><body><script src="{% static 'js/htmx.min.js' %}"></script></body></html>
HTML
commit_all "$P" legacy-core >/dev/null
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D3a legacy core 1개 + 로드 태그 키 0" 0 "키 0" "BLOCKER" "$E" "$OUT"
printf '(function(){})();\n' > "$P/web/static/htmx/htmx.min.js"
run_backstop "$P" --debt-scan --json "$T/d3.json" >/dev/null; E=$?
assert "D3b 대조: legacy+canonical 공존 = WP1 2키 + WP2 1키" 2 \
  "WP1|static/htmx/htmx.min.js=1 WP1|static/js/htmx.min.js=2 WP2|base/base.html=1" - "$E" "$(counts_of "$T/d3.json")"

# ---------- D4: 기존 단위 골격 미비(WS5)는 빚 아님 — 신규 단위만 G2 게이트가 본다
P="$T/d4"; BASE=$(mkproj "$P")
mkdir -p "$P/web/billing"; echo "urlpatterns = []" > "$P/web/billing/urls.py"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D4a 골격 미비 영역 키 0(WS5 빚 모드 제외 notice)" 0 "WS5(골격 완비) 빚 모드 제외" "[WS5]" "$E" "$OUT"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws5); E=$?
assert "D4b 대조: 같은 트리의 신규 단위는 diff 게이트 WS5 red" 2 "[WS5]" - "$E" "$OUT"

# ---------- D5: 작업 트리에서만 지운 추적 파일은 유령 키·오류가 아니다
P="$T/d5"; mkproj "$P" >/dev/null
echo "x = 1" > "$P/web/junk.py"; commit_all "$P" junk >/dev/null
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D5a 대조: 추적 파일 실재 시 WS1 빚" 2 "[WS1] web/junk.py" - "$E" "$OUT"
rm "$P/web/junk.py"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D5b 인덱스 전용 삭제 키 0·오류 0" 0 "키 0" "junk.py" "$E" "$OUT"

# ---------- D6: 같은 파일 2건 = 키 1 · 수 2
P="$T/d6"; mkproj "$P" >/dev/null
printf 'a { color: #ffffff; }\nb { color: #000000; }\n' > "$P/web/static/css/site.css"
commit_all "$P" colors >/dev/null
run_backstop "$P" --debt-scan --json "$T/d6.json" >/dev/null; E=$?
assert "D6 같은 파일 2건 키 1·수 2" 2 "WP4|static/css/site.css=2" - "$E" "$(counts_of "$T/d6.json")"

# ---------- D7: 파일명 위반 3건 → C1..C3 결정적
P="$T/d7"; mkproj "$P" >/dev/null; bad_images "$P"
run_backstop "$P" --debt-scan --json "$T/d7a.json" >/dev/null
run_backstop "$P" --debt-scan --json "$T/d7b.json" >/dev/null; E=$?
IDS_A=$(field_of "$T/d7a.json" ids); IDS_B=$(field_of "$T/d7b.json" ids)
assert "D7a C1..C3 키 정렬 순" 2 '{"C1": "WN8|static/images/a-b.png", "C2": "WN8|static/images/c-d.png", "C3": "WN8|static/images/e-f.png"}' - "$E" "$IDS_A"
assert "D7b 두 번 실행 동일" 0 "$IDS_A" - 0 "$IDS_B"

# ---------- D8: 잔존 — ⓐ 1 미해소 exit 2 · 해소 exit 0
P="$T/d8"; mkproj "$P" >/dev/null; bad_images "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1
요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D8a ⓐ 미해소 = 잔존 1" 2 "ⓐ 잔존 1 · 요구 잔존 0" - "$E" "$OUT"
git -C "$P" mv web/static/images/a-b.png web/static/images/a_b.png
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D8b ⓐ 해소 = 잔존 0" 0 "ⓐ 잔존 0 · 요구 잔존 0 · 재상정 제외 0 · G0 에 없던 키 0" - "$E" "$OUT"
assert "D8c G2 스캔은 debt-g2.json 에 · G0 동결본 불변" 0 "WN8|static/images/a-b.png" - 0 "$(field_of "$P/.dddjango-web/run/debt-g0.json" ids)"
[ -f "$P/.dddjango-web/run/debt-g2.json" ]; assert "D8d debt-g2.json 기록" 0 - - "$?" ""

# ---------- D9: 재승인 절이 앞 ⓐ 를 다시 적어도(누적 기록) 같은 판정
P="$T/d9"; mkproj "$P" >/dev/null; bad_images "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1
요구 키: -

## G0 재승인 2026-09-27 11:00
ⓐ 키: C1 C2
요구 키: -'
git -C "$P" mv web/static/images/c-d.png web/static/images/c_d.png
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D9a 누적 행의 앞 ⓐ 미해소 = exit 2" 2 "잔존 ⓐ C1" "잔존 ⓐ C2" "$E" "$OUT"
git -C "$P" mv web/static/images/a-b.png web/static/images/a_b.png
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D9b 누적 ⓐ 전부 해소 = exit 0" 0 "ⓐ 잔존 0" - "$E" "$OUT"

# ---------- D10: 재상정 키는 잔존에서 빠진다
P="$T/d10"; mkproj "$P" >/dev/null; bad_images "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1 C2
요구 키: -

## ⓐ 재상정 2026-09-27 12:00
재상정 키: C2'
git -C "$P" mv web/static/images/a-b.png web/static/images/a_b.png
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D10a 재상정 제외 = exit 0" 0 "ⓐ 잔존 0 · 요구 잔존 0 · 재상정 제외 1" - "$E" "$OUT"
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1 C2
요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D10b 대조: 재상정 절 없으면 C2 잔존" 2 "잔존 ⓐ C2" - "$E" "$OUT"

# ---------- D11: 요구 키 미해소 = exit 2
P="$T/d11"; mkproj "$P" >/dev/null; bad_images "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: -
요구 키: C3'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D11a 요구 키 미해소 = 요구 잔존 1" 2 "ⓐ 잔존 0 · 요구 잔존 1" - "$E" "$OUT"
git -C "$P" mv web/static/images/e-f.png web/static/images/e_f.png
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D11b 대조: 요구 키 해소 = exit 0" 0 "요구 잔존 0" - "$E" "$OUT"

# ---------- D12: 두 행 모두 `-` = M 0
P="$T/d12"; mkproj "$P" >/dev/null; bad_images "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
- ⓐ 키: -
- 요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D12 ⓐ·요구 모두 - = exit 0(legacy 잔존은 판정 밖)" 0 "ⓐ 잔존 0 · 요구 잔존 0" - "$E" "$OUT"

# ---------- D13: 판정 불가(exit 1)와 전이 규칙
P="$T/d13"; mkproj "$P" >/dev/null; bad_images "$P"; run_folder "$P" run
scope_md "$P" run '# 리팩터링 스코프

## 스캔
C1 | WN8|static/images/a-b.png'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D13a G0 절 없음 = 판정 불가" 1 "G0" - "$E" "$OUT"
scope_md "$P" run '## G0 @NOW@
ⓐ 키 C1'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D13b 정형 행 없음 = 판정 불가" 1 "정확히 한 번" - "$E" "$OUT"
scope_md "$P" run '## G0 재승인(G1) 2026-09-27 10:00
ⓐ 키: C1
요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D13c 변형 절 머리 = 판정 불가" 1 "알 수 없는 절 머리" - "$E" "$OUT"
rm "$P/.dddjango-web/run/refactor-scope.md"
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D13d debt-g0.json 만 있음 = 판정 불가" 1 "refactor-scope.md 가 없음" - "$E" "$OUT"
rm "$P/.dddjango-web/run/debt-g0.json"
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D13e 둘 다 없음 = 해당 없음(규칙 이전 G0) exit 0" 0 "잔존 판정 해당 없음(규칙 이전 G0)" - "$E" "$OUT"
OUT=$(run_backstop "$P" --debt-residual "$T"); E=$?
assert "D13f .dddjango-web 밖 폴더 = 판정 불가" 1 "아래의 실재 폴더" - "$E" "$OUT"

# ---------- D14: debt-g0.json 에 없는 C<n> = 판정 불가
P="$T/d14"; mkproj "$P" >/dev/null; bad_images "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1 C9
요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D14 없는 ID = exit 1" 1 "C9" - "$E" "$OUT"

# ---------- D15: 개명만 하고 안 고침 — 잔존은 «해소»로 보지만 diff 게이트가 새 경로를 red(두 게이트 짝)
P="$T/d15"; BASE=$(mkproj "$P"); bad_images "$P"; BASE=$(git -C "$P" rev-parse HEAD); run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1
요구 키: -'
git -C "$P" mv web/static/images/a-b.png web/static/images/a-b-2.png
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D15a 잔존 판정은 키 대조라 exit 0 · 새 키 X 보고" 0 "G0 에 없던 키 1" - "$E" "$OUT"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn8); E=$?
assert "D15b diff 게이트가 새 경로 발견 red" 2 "a-b-2.png" - "$E" "$OUT"
git -C "$P" mv web/static/images/a-b-2.png web/static/images/a_b.png
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn8); E=$?
assert "D15c 대조: 표준 이름으로 개명하면 diff 게이트 green" 0 "blocker 0건" - "$E" "$OUT"

# ---------- D16: 참조 치환 줄의 기존 WP4 는 diff 게이트에서 새 줄 red — 묶음 규칙이 필요한 이유
P="$T/d16"; mkproj "$P" >/dev/null
printf 'png' > "$P/web/static/images/cloud-ornament.png"
cat > "$P/web/orders/order_list/section/order_list_hero.html" <<'HTML'
{% load static %}
<img src="{% static 'web/images/cloud-ornament.png' %}" style="color: #ffffff">
HTML
cat > "$P/web/orders/order_list/section/order_list_logo.html" <<'HTML'
{% load static %}
<img src="{% static 'web/images/cloud-ornament.png' %}">
HTML
BASE=$(commit_all "$P" ref-lines)
git -C "$P" mv web/static/images/cloud-ornament.png web/static/images/cloud_ornament.png
sed -i.bak 's/cloud-ornament/cloud_ornament/' "$P/web/orders/order_list/section/order_list_logo.html"
rm "$P/web/orders/order_list/section/order_list_logo.html.bak"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp4,wn8); E=$?
assert "D16a 대조: 색 리터럴 없는 참조 줄 치환은 green" 0 "blocker 0건" - "$E" "$OUT"
sed -i.bak 's/cloud-ornament/cloud_ornament/' "$P/web/orders/order_list/section/order_list_hero.html"
rm "$P/web/orders/order_list/section/order_list_hero.html.bak"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp4,wn8); E=$?
assert "D16b 참조 줄의 기존 WP4 가 치환으로 새 줄 red" 2 "[WP4] BLOCKER — web/orders/order_list/section/order_list_hero.html:2" - "$E" "$OUT"

# ---------- D17: 빚 모드는 단독 — 범위 좁히기·게이트 혼용 금지
P="$T/d17"; BASE=$(mkproj "$P")
OUT=$(run_backstop "$P" --debt-scan --diff-base "$BASE"); E=$?
assert "D17a --debt-scan + --diff-base = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --debt-scan --only wn8); E=$?
assert "D17b --debt-scan + --only = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
mkdir -p "$P/.dddjango-web/run"
OUT=$(run_backstop "$P" --debt-scan --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D17c --debt-scan + --debt-residual = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --json "$T/x.json"); E=$?
assert "D17d --json 단독 = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D17e 대조: --debt-scan 단독은 실행" 0 "빚 스캔 — 키 0" - "$E" "$OUT"

# ---------- D18: git 저장소가 아니면 빚 스캔 실행 불능(«빚 0» 아님)
P="$T/d18"; mkproj "$P" >/dev/null; rm -rf "$P/.git"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D18 비git = 실행 불능 exit 1" 1 "실행 불능" "키 0" "$E" "$OUT"

# ---------- D19: git 이 web/ 을 못 보면 실행 불능(«빚 0» 아님) — 심볼릭 링크 · git 밖·무시된 폴더
P="$T/d19a"; mkproj "$P" >/dev/null; bad_images "$P"
mv "$P/web" "$T/d19a-web"; ln -s "$T/d19a-web" "$P/web"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D19a web 심볼릭 링크 = 실행 불능 exit 1" 1 "심볼릭 링크" "키 0" "$E" "$OUT"
mkdir -p "$T/d19b"; git -C "$T/d19b" init -q; printf 'proj/\n' > "$T/d19b/.gitignore"
P="$T/d19b/proj"; mkproj "$P" >/dev/null; bad_images "$P"; rm -rf "$P/.git"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D19b 상위 저장소가 무시한 비git 프로젝트 = 실행 불능 exit 1" 1 "git 우주가 비었는데" "키 0" "$E" "$OUT"
rm "$T/d19b/.gitignore"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D19c 대조: 무시가 풀리면 상위 저장소 우주로 스캔(빚 3)" 2 "키 3" - "$E" "$OUT"

# ---------- D20: git 저장소 · web/ 부재 = 첫 실행 빚 0(exit 0) — 비git(D18)과 다르다
P="$T/d20"; mkproj "$P" >/dev/null; rm -rf "$P/web"; commit_all "$P" no-web >/dev/null
mkdir -p "$P/.dddjango-web/run"
OUT=$(run_backstop "$P" --debt-scan --json "$P/.dddjango-web/run/debt-g0.json"); E=$?
assert "D20a web/ 부재 = 첫 실행 빚 0 exit 0" 0 "첫 실행" "실행 불능" "$E" "$OUT"
scope_md "$P" run '## G0 @NOW@
ⓐ 키: -
요구 키: -'
mkdir -p "$P/web/static/images"; printf 'png' > "$P/web/static/images/x-y.png"
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D20b G2: 새 코드의 키는 «G0 에 없던 키»(보고만) exit 0" 0 "G0 에 없던 키 1" - "$E" "$OUT"

# ---------- D21: 재승인 절이 앞 요구 키를 다시 적지 않아도 요구 키는 남는다
P="$T/d21"; mkproj "$P" >/dev/null; bad_images "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: -
요구 키: C1

## G0 재승인 @NOW@
ⓐ 키: C2
요구 키: -'
git -C "$P" mv web/static/images/c-d.png web/static/images/c_d.png
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D21a 앞 절 요구 키 C1 미해소 = 요구 잔존 1 exit 2" 2 "ⓐ 잔존 0 · 요구 잔존 1" - "$E" "$OUT"
git -C "$P" mv web/static/images/a-b.png web/static/images/a_b.png
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D21b 대조: C1 해소 = exit 0" 0 "ⓐ 잔존 0 · 요구 잔존 0" - "$E" "$OUT"
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1 C2
요구 키: -

## ⓐ 재상정 @NOW@
재상정 키: C1

## G0 재승인 @NOW@
ⓐ 키: C1 C2
요구 키: -'
git -C "$P" mv web/static/images/a_b.png web/static/images/a-b.png
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D21c 재상정 뒤 재승인이 다시 적은 키는 되살아난다" 2 "잔존 ⓐ C1" - "$E" "$OUT"

# ---------- D22: 이번 요청의 G0 절이 없으면(앞 요청 절만 남음) 판정 불가
P="$T/d22"; mkproj "$P" >/dev/null; bad_images "$P"; run_folder "$P" run
scope_md "$P" run '## G0 2026-01-01 10:00
ⓐ 키: -
요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D22a 마지막 G0 절이 스캔보다 이르다 = exit 1" 1 "이번 요청의 G0 절 없음" - "$E" "$OUT"
scope_md "$P" run '## G0 2026-01-01 10:00
ⓐ 키: -
요구 키: -

## G0 @NOW@
ⓐ 키: C1
요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D22b 대조: 이번 요청 G0 절이 있으면 그 절로 판정" 2 "잔존 ⓐ C1" - "$E" "$OUT"

# ---------- D23: 코드 펜스 안의 머리 모양 줄은 절이 아니다
P="$T/d23"; mkproj "$P" >/dev/null; bad_images "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1
요구 키: -

```text
## G0 @NOW@
ⓐ 키: -
요구 키: -
```'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D23a 펜스 안 예시 절은 무시 — C1 잔존 exit 2" 2 "잔존 ⓐ C1" - "$E" "$OUT"
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1
요구 키: -

## G0 @NOW@
ⓐ 키: -
요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D23b 대조: 펜스 밖이면 새 G0 절(요청 경계)로 판정 exit 0" 0 "ⓐ 잔존 0" - "$E" "$OUT"

# ---------- D24: 리팩토링 스캔(--refactor) — 기존 단위 골격 미비(WS5)도 빚 · notice 없음 · mode 기록
P="$T/d24"; mkproj "$P" >/dev/null
mkdir -p "$P/web/billing"; echo "urlpatterns = []" > "$P/web/billing/urls.py"
rm "$P/web/static/images/.gitkeep"; commit_all "$P" gaps >/dev/null
OUT=$(run_backstop "$P" --debt-scan --refactor --json "$T/d24.json"); E=$?
assert "D24a 리팩토링 스캔은 기존 단위 WS5 를 빚으로" 2 "[WS5]" "빚 모드 제외" "$E" "$OUT"
assert "D24b 영역 폴더 키 billing/" 0 "WS5|billing/=1" - 0 "$(counts_of "$T/d24.json")"
assert "D24c 컨테이너 빈 경로 키" 0 "WS5|=1" - 0 "$(counts_of "$T/d24.json")"
assert "D24d JSON mode = refactor" 0 '"refactor"' - 0 "$(field_of "$T/d24.json" mode)"
run_backstop "$P" --debt-scan --json "$T/d24f.json" >/dev/null
assert "D24e 대조: 기본 스캔은 WS5 키 0 · mode feature" 0 '"feature"' - 0 "$(field_of "$T/d24f.json" mode)"
assert "D24f 대조: 기본 스캔 counts 에 WS5 없음" 0 - "WS5" 0 "$(counts_of "$T/d24f.json")"

# ---------- D25: legacy core 면제 해제는 로드 태그 면제가 없을 때만(WP1·WP2 한 쌍)
P="$T/d25"; mkproj "$P" >/dev/null
rm "$P/web/static/htmx/htmx.min.js"; rmdir "$P/web/static/htmx"
printf '(function(){})();\n' > "$P/web/static/js/htmx.min.js"
cat > "$P/web/base/base.html" <<'HTML'
{% load static %}<html><body><script src="{% static 'js/htmx.min.js' %}"></script></body></html>
HTML
commit_all "$P" legacy-core >/dev/null
run_backstop "$P" --debt-scan --refactor --json "$T/d25.json" >/dev/null
assert "D25a defer 없는 legacy 태그 → WP1·WP2 한 쌍 면제 유지" 0 - "WP1" 0 "$(counts_of "$T/d25.json")"
assert "D25b 쌍 유지 + 컨테이너 골격 누락(static/htmx/) → WS5| 키로 fail-closed" 0 "WS5|=1" "WP2" 0 "$(counts_of "$T/d25.json")"
cat > "$P/web/base/base.html" <<'HTML'
{% load static %}<html><body><script src="{% static 'js/htmx.min.js' %}" defer></script></body></html>
HTML
commit_all "$P" defer-tag >/dev/null
run_backstop "$P" --debt-scan --refactor --json "$T/d25b.json" >/dev/null
assert "D25c defer 있는 legacy 태그 → WP1 면제 걷힘" 0 "WP1|static/js/htmx.min.js=1" - 0 "$(counts_of "$T/d25b.json")"
run_backstop "$P" --debt-scan --json "$T/d25c.json" >/dev/null
assert "D25d 대조: 기본 스캔은 legacy core 면제 그대로" 0 - "WP1" 0 "$(counts_of "$T/d25c.json")"

# ---------- D26: --debt-residual 은 debt-g0.json mode 를 따른다(리팩토링 동결본 → WS5 잔존 판정)
P="$T/d26"; mkproj "$P" >/dev/null
mkdir -p "$P/web/billing"; echo "urlpatterns = []" > "$P/web/billing/urls.py"; commit_all "$P" gap >/dev/null
mkdir -p "$P/.dddjango-web/run"
run_backstop "$P" --debt-scan --refactor --json "$P/.dddjango-web/run/debt-g0.json" >/dev/null
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1
요구 키: -
의미 ⓐ 키: -
의미 audit: 20260927-120000'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D26a 리팩토링 동결본 — WS5 미해소 잔존 exit 2(mkproj 의 빈 static/js/ 가 컨테이너 키)" 2 "잔존 ⓐ C1 WS5|" - "$E" "$OUT"
python3 - "$P/.dddjango-web/run/debt-g0.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d['mode'] = 'feature'; json.dump(d, open(sys.argv[1], 'w'))
PY
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D26b 대조: 같은 동결본을 mode feature 로 읽으면 WS5 를 보지 않아 해소 exit 0" 0 "ⓐ 잔존 0" - "$E" "$OUT"

# ---------- D27: --refactor·--subst-check·--names·--except 배타
P="$T/d27"; mkproj "$P" >/dev/null
OUT=$(run_backstop "$P" --refactor); E=$?
assert "D27a --refactor 단독 = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --debt-scan --refactor --diff-base HEAD); E=$?
assert "D27b --refactor + --diff-base = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
mkdir -p "$P/.dddjango-web/run"
OUT=$(run_backstop "$P" --refactor --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D27c --refactor + --debt-residual = 사용 오류(모드는 debt-g0.json 이 정한다)" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --names x.md); E=$?
assert "D27d --names 단독 = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --except config/settings.py); E=$?
assert "D27e --except 단독 = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --subst-check HEAD HEAD --debt-scan); E=$?
assert "D27f --subst-check + --debt-scan = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --subst-check HEAD HEAD); E=$?
assert "D27g 대조: --subst-check 단독은 실행(변경 0 = green)" 0 "치환 확인 — web/ 밖 변경 파일 0" - "$E" "$OUT"

# ---------- D28: 의미(M) 행 — 6a C 판정 무변 · 값 검사는 접는 절에서만
P="$T/d28"; mkproj "$P" >/dev/null; bad_images "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1
요구 키: -
의미 ⓐ 키: M1 M2
의미 audit: 20260927-120000'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D28a 의미 행이 있어도 C 판정 무변(C1 잔존)" 2 "잔존 ⓐ C1" - "$E" "$OUT"
scope_md "$P" run '## G0 2026-01-01 09:00
ⓐ 키: -
요구 키: -
의미 ⓐ 키: C1

## G0 @NOW@
ⓐ 키: -
요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D28b 옛 절의 어긋난 의미 행은 판정 입력 아님 exit 0" 0 "ⓐ 잔존 0" - "$E" "$OUT"

# ---------- D29: 명세 정형 행 파서(--subst-check --names · plan --names 공통) — `## 슬라이스 0` 절만
P="$T/d29"; mkproj "$P" >/dev/null
printf '# 명세\n이름: web.x.y → broken\n\n## 슬라이스 0\n이름: web.a.m.f → web.b.n.f\n\n## 슬라이스 1\n경로: nope\n' > "$T/d29-ok.md"
OUT=$(run_backstop "$P" --subst-check HEAD HEAD --names "$T/d29-ok.md"); E=$?
assert "D29a 절 밖 어긋난 행은 무시 — green" 0 "치환 확인 — web/ 밖 변경 파일 0 · 쌍 1" - "$E" "$OUT"
printf '## 슬라이스 0\n이름: web.a.m.f → n.f\n' > "$T/d29-bad.md"
OUT=$(run_backstop "$P" --subst-check HEAD HEAD --names "$T/d29-bad.md"); E=$?
assert "D29b 절 안 형식 어긋남 = 실행 불능" 1 "web. 으로 시작하는 전체 점 경로" - "$E" "$OUT"
printf '## 슬라이스 0\n\n## 슬라이스 0 — 둘째\n' > "$T/d29-dup.md"
OUT=$(run_backstop "$P" --subst-check HEAD HEAD --names "$T/d29-dup.md"); E=$?
assert "D29c 절 머리 중복 = 실행 불능" 1 "절 머리가 2개" - "$E" "$OUT"
printf '# 명세\n' > "$T/d29-none.md"
OUT=$(run_backstop "$P" --subst-check HEAD HEAD --names "$T/d29-none.md"); E=$?
assert "D29d 절 머리 없음(--names 를 준 호출) = 실행 불능" 1 "절이 없다" - "$E" "$OUT"

# ---------- D30~D38: 공식 SDK 등재(WV · houserules §9) — 빚 스캔 의미론
SX() { python3 "$SCRIPTS/test/sdk_fixture.py" "$@" 2>&1; }
sdk_proj() { # sdk_proj <dir> — 등재 + 페이지 로드 줄(커밋)
  SX mkproj "$1" >/dev/null; SX install "$1" >/dev/null
  printf '{%% extends "base.html" %%}\n{%% load static %%}\n{%% block scripts %%}\n<script src="{%% static '"'"'web/vendor/kakao_js_sdk/kakao.min.js'"'"' %%}" defer></script>\n{%% endblock scripts %%}\n' > "$1/web/chart/chart/view/chart.html"
  commit_all "$1" page >/dev/null
}
P="$T/d30"; sdk_proj "$P"
OUT=$(run_backstop "$P" --debt-scan --json "$T/d30.json"); E=$?
assert "D30 정상 등재 — WV 키 0" 0 "키 0" "[WV" "$E" "$OUT"
P="$T/d31"; SX mkproj "$P" >/dev/null; SX install "$P" >/dev/null
OUT=$(run_backstop "$P" --debt-scan --json "$T/d31.json"); E=$?
assert "D31 사용처 0 — WV11(미룰 수 있음)" 2 "[WV11] web/static/vendor/kakao_js_sdk/kakao.min.js" "미룰 수 없음" "$E" "$OUT"
P="$T/d32"; sdk_proj "$P"; printf 'x' >> "$P/web/static/vendor/kakao_js_sdk/kakao.min.js"
OUT=$(run_backstop "$P" --debt-scan --json "$T/d32.json"); E=$?
assert "D32 지문 불일치 — WV2 · undeferrable · exit 2" 2 "[WV2] (미룰 수 없음)" - "$E" "$OUT"
assert "D32b JSON 행 undeferrable: true" 0 '"undeferrable": true' - 0 "$(cat "$T/d32.json")"
assert "D33 빚 스캔 — «WV10 빚 모드 생략» notice" 2 "WV10(SDK 변경 격리) 빚 모드 생략" - "$E" "$OUT"
# D34: --debt-residual 에서 ⓐ WV2 복원 — 잔존 0
mkdir -p "$P/.dddjango-web/run"; run_backstop "$P" --debt-scan --json "$P/.dddjango-web/run/debt-g0.json" >/dev/null
CID=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print([c for c,k in d["ids"].items() if k.startswith("WV2|")][0])' "$P/.dddjango-web/run/debt-g0.json")
scope_md "$P" run "## G0 @NOW@
ⓐ 키: $CID
요구 키: -"
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D34a 복원 전 — ⓐ 잔존 1" 2 "잔존 ⓐ $CID WV2|" - "$E" "$OUT"
git -C "$P" checkout -- web/static/vendor/kakao_js_sdk/kakao.min.js
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D34b ⓐ WV2 복원 뒤 — 잔존 0" 0 "ⓐ 잔존 0" - "$E" "$OUT"
P="$T/d35"; SX mkproj "$P" >/dev/null; SX install "$P" >/dev/null; printf 'x' >> "$P/web/static/vendor/kakao_js_sdk/kakao.min.js"
OUT=$(run_backstop "$P" --debt-scan --refactor); E=$?
assert "D35 --refactor — D31·D32 와 같은 키" 2 "[WV2] (미룰 수 없음)" - "$E" "$OUT"
assert "D35b --refactor — WV11 도" 2 "[WV11]" - "$E" "$OUT"
# D36: 디렉터리 심볼릭 링크 벤더(ls-files 우주에 없음)
P="$T/d36"; sdk_proj "$P"; mv "$P/web/static/vendor/kakao_js_sdk" "$T/d36-real"; ln -s "$T/d36-real" "$P/web/static/vendor/kakao_js_sdk"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D36a 디렉터리 링크 — WV2 키 · undeferrable" 2 "[WV2] (미룰 수 없음)" - "$E" "$OUT"
assert "D36b 디렉터리 링크 — WV5 키 · undeferrable" 2 "[WV5] (미룰 수 없음)" - "$E" "$OUT"
# D37: 목록 없는 벤더 사본 — WV12 + WS6/WP1(미룰 수 있음) · notice
P="$T/d37"; SX mkproj "$P" >/dev/null; mkdir -p "$P/web/static/vendor/legacy"; echo 'x()' > "$P/web/static/vendor/legacy/legacy.min.js"; commit_all "$P" legacy >/dev/null
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D37a 목록 없는 사본 — WV12 키" 2 "[WV12] web/static/vendor/legacy/" "미룰 수 없음" "$E" "$OUT"
assert "D37b WS6·WP1 키(미룰 수 있음)" 2 "[WP1] web/static/vendor/legacy/legacy.min.js" - "$E" "$OUT"
assert "D37c G0 알림 notice" 2 "미등재 벤더 단위: static/vendor/legacy/(WV12)" - "$E" "$OUT"
# D38: --debt-residual · debt-g0.json scanner 판이 다름 — 판 경계
P="$T/d38"; SX mkproj "$P" >/dev/null; mkdir -p "$P/.dddjango-web/run"
run_backstop "$P" --debt-scan --json "$P/.dddjango-web/run/debt-g0.json" >/dev/null
scope_md "$P" run "## G0 @NOW@
ⓐ 키: -
요구 키: -"
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D38a 같은 판 — 판정" 0 "ⓐ 잔존 0" - "$E" "$OUT"
python3 - "$P/.dddjango-web/run/debt-g0.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d['scanner'] = {'plugin': '1.1.25', 'checks': 'old'}; json.dump(d, open(sys.argv[1], 'w'))
PY
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D38b scanner 판이 다름 — exit 1 «판 경계»" 1 "판 경계 — G0 재스캔 필요" - "$E" "$OUT"
python3 - "$P/.dddjango-web/run/debt-g0.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d.pop('scanner'); json.dump(d, open(sys.argv[1], 'w'))
PY
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D38c scanner 없는 옛 동결본 — exit 1 «판 경계»" 1 "판 경계 — G0 재스캔 필요" - "$E" "$OUT"

echo "fixtures_debt: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
