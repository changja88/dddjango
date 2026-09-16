#!/usr/bin/env bash
# dddjango-web 백스톱 자기 회귀 픽스처 (판형: dddart scripts/test/run_fixtures.sh)
# mktemp 임시 git 프로젝트 + assert 헬퍼 + 케이스마다 positive-control 짝.
set -u
SCRIPTS="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0; FAIL=0

run_backstop() { python3 "$SCRIPTS/backstop.py" "$@" 2>&1; }

assert() { # assert <이름> <기대exit> <있어야 할 패턴|-> <없어야 할 패턴|-> <실제exit> <출력>
  local name="$1" wantexit="$2" want="$3" unwant="$4" gotexit="$5" out="$6" ok=1
  [ "$gotexit" != "$wantexit" ] && ok=0
  [ "$want" != "-" ] && ! grep -q "$want" <<<"$out" && ok=0
  [ "$unwant" != "-" ] && grep -q "$unwant" <<<"$out" && ok=0
  if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS $name"; else
    FAIL=$((FAIL+1)); echo "FAIL $name (exit=$gotexit want=$wantexit)"; echo "$out" | head -20 | sed 's/^/    /'
  fi
}

assert_count() { # assert_count <이름> <기대exit> <패턴> <기대건수> <실제exit> <출력>
  local name="$1" wantexit="$2" pat="$3" wantn="$4" gotexit="$5" out="$6"
  local n; n=$(grep -c "$pat" <<<"$out" || true)
  if [ "$gotexit" = "$wantexit" ] && [ "$n" = "$wantn" ]; then
    PASS=$((PASS+1)); echo "PASS $name"
  else
    FAIL=$((FAIL+1)); echo "FAIL $name (exit=$gotexit want=$wantexit, $pat=$n want=$wantn)"
    echo "$out" | head -20 | sed 's/^/    /'
  fi
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

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# ---------- F0: 골격 자체가 green — gated 무변경 + 전역(--all) 둘 다 0
P="$T/f0"; BASE=$(mkproj "$P")
OUT=$(run_backstop "$P" --diff-base "$BASE"); E=$?
assert "F0a gated 무변경 green" 0 "blocker 0건" "BLOCKER" "$E" "$OUT"
OUT=$(run_backstop "$P" --all --diff-base "$BASE"); E=$?
assert "F0b 전역(--all) green(positive control 전수)" 0 "blocker 0건" "BLOCKER" "$E" "$OUT"

# ---------- F1: WS1 web/ 직속 화이트리스트
P="$T/f1"; BASE=$(mkproj "$P")
echo "x = 1" > "$P/web/junk.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws1); E=$?
assert "F1a WS1 web 직속 잡파일 발화" 2 "WS1" - "$E" "$OUT"
rm "$P/web/junk.py"; echo "# note" >> "$P/web/urls.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws1); E=$?
assert "F1b WS1 control — 고정 파일·마커만이면 clean" 0 - "WS1" "$E" "$OUT"

# ---------- F2: WS2 영역 직속 — urls.py·widget/·개념 폴더만
P="$T/f2"; BASE=$(mkproj "$P")
echo "def h(): pass" > "$P/web/orders/helper.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws2); E=$?
assert "F2a WS2 영역 직속 파일 발화" 2 "WS2" - "$E" "$OUT"
rm "$P/web/orders/helper.py"
mkdir -p "$P/web/billing/widget"
echo "urlpatterns = []" > "$P/web/billing/urls.py"
: > "$P/web/billing/widget/.gitkeep"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws); E=$?
assert "F2b WS control — 완비 신규 영역은 clean(WS5 포함)" 0 - "WS" "$E" "$OUT"

# ---------- F3: WS3 화면 개념 — 종류 폴더 밖 금지
P="$T/f3"; BASE=$(mkproj "$P")
mkdir -p "$P/web/orders/order_list/util"
echo "def h(): pass" > "$P/web/orders/order_list/util/helper.py"
echo "memo" > "$P/web/orders/order_list/readme.txt"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws3); E=$?
assert_count "F3a WS3 종류 밖 디렉터리+개념 직속 파일 2건" 2 "WS3" 2 "$E" "$OUT"
rm -rf "$P/web/orders/order_list/util" "$P/web/orders/order_list/readme.txt"
mkdir -p "$P/web/orders/order_list/form"
: > "$P/web/orders/order_list/form/__init__.py"
printf 'class OrderListForm:\n    pass\n' > "$P/web/orders/order_list/form/order_list_form.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws3); E=$?
assert "F3b WS3 control — form/ 조건 생성은 합법" 0 - "WS3" "$E" "$OUT"

# ---------- F4: WS4 design_system 2칸
P="$T/f4"; BASE=$(mkproj "$P")
echo "<i>x</i>" > "$P/web/design_system/component/note.html"
mkdir -p "$P/web/design_system/theme"
echo "a{}" > "$P/web/design_system/theme/dark.css"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws4); E=$?
assert_count "F4a WS4 component 직속 파일+theme 칸 2건" 2 "WS4" 2 "$E" "$OUT"
rm -rf "$P/web/design_system/component/note.html" "$P/web/design_system/theme"
printf '<button class="btn ghost">x</button>\n' > "$P/web/design_system/component/button/ghost_button.html"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws4); E=$?
assert "F4b WS4 control — 부품군 안 부품은 clean" 0 - "WS4" "$E" "$OUT"

# ---------- F5: WS5 골격 완비 — 신규 영역·신규 화면 개념
P="$T/f5"; BASE=$(mkproj "$P")
mkdir -p "$P/web/customers"
echo "urlpatterns = []" > "$P/web/customers/urls.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws5); E=$?
assert "F5a WS5 신규 영역 widget/ 누락 발화" 2 "widget/" - "$E" "$OUT"
mkdir -p "$P/web/customers/widget"; : > "$P/web/customers/widget/.gitkeep"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws5); E=$?
assert "F5b WS5 control — 영역 골격 완비 후 clean" 0 - "WS5" "$E" "$OUT"
mkdir -p "$P/web/orders/order_detail/view"
: > "$P/web/orders/order_detail/view/__init__.py"
printf 'def order_detail_view(request):\n    return None\n' > "$P/web/orders/order_detail/view/order_detail_view.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws5); E=$?
assert "F5c WS5 신규 화면 개념 종류 폴더 누락 발화" 2 "view_model/" - "$E" "$OUT"
mkdir -p "$P/web/orders/order_detail/view_model" "$P/web/orders/order_detail/state" "$P/web/orders/order_detail/section"
: > "$P/web/orders/order_detail/view_model/__init__.py"
: > "$P/web/orders/order_detail/state/__init__.py"
: > "$P/web/orders/order_detail/section/.gitkeep"
printf '<p>x</p>\n' > "$P/web/orders/order_detail/view/order_detail.html"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws); E=$?
assert "F5d WS control — 개념 골격 완비(정적 화면) clean" 0 - "WS" "$E" "$OUT"

# ---------- F6: WS6 static/ 허용 칸·직속 파일 금지
P="$T/f6"; BASE=$(mkproj "$P")
mkdir -p "$P/web/static/archive"
echo "x" > "$P/web/static/archive/a.bin"
echo "memo" > "$P/web/static/readme.txt"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws6); E=$?
assert_count "F6a WS6 허용 외 archive 칸+직속 파일 2건" 2 "WS6" 2 "$E" "$OUT"
rm -rf "$P/web/static/archive" "$P/web/static/readme.txt"
echo "png" > "$P/web/static/images/logo.png"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws6); E=$?
assert "F6b WS6 control — images/ 착지는 clean" 0 - "WS6" "$E" "$OUT"

# 검증된 폰트/다운로드 파일은 필요할 때만 해당 static 칸에 배선한다.
P="$T/f6_assets"; BASE=$(mkproj "$P")
mkdir -p "$P/web/static/fonts" "$P/web/static/files"
printf 'font fixture' > "$P/web/static/fonts/brand.woff2"
printf 'download fixture' > "$P/web/static/files/guide.txt"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws6); E=$?
assert "F6c WS6 fonts/files conditional directories are valid" 0 - "WS6" "$E" "$OUT"
mkdir -p "$P/web/static/arbitrary"
printf 'unknown' > "$P/web/static/arbitrary/blob.txt"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws6); E=$?
assert "F6d WS6 unknown static directory still blocked" 2 "WS6" - "$E" "$OUT"

# ---------- F7: WS7 영역·화면 이름 deny(종류명·컨테이너명)
P="$T/f7"; BASE=$(mkproj "$P")
mkdir -p "$P/web/state/widget"
echo "urlpatterns = []" > "$P/web/state/urls.py"
: > "$P/web/state/widget/.gitkeep"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws7); E=$?
assert "F7a WS7 영역 이름 state/ 발화" 2 "WS7" - "$E" "$OUT"
rm -rf "$P/web/state"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws7); E=$?
assert "F7b WS7 control — 기능 어휘 영역(orders)은 clean" 0 - "WS7" "$E" "$OUT"

# ---------- F8: WS8 client 컨테이너 형태
P="$T/f8"; BASE=$(mkproj "$P")
echo "def h(): pass" > "$P/web/client/util.py"
mkdir -p "$P/web/client/orders/helpers"
echo "x = 1" > "$P/web/client/orders/helpers/a.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws8); E=$?
assert_count "F8a WS8 client 직속 파일+BC 하위 잡폴더 2건" 2 "WS8" 2 "$E" "$OUT"
rm -rf "$P/web/client/util.py" "$P/web/client/orders/helpers"
printf 'class PaymentQueryClient:\n    pass\n' > "$P/web/client/orders/payment_query_client.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws8); E=$?
assert "F8b WS8 control — capability 파일 증가는 clean" 0 - "WS8" "$E" "$OUT"

# ---------- F9: WI1 백엔드 내부 import 금지(절대·상대 클램핑·주석/문자열 불발화)
P="$T/f9"; BASE=$(mkproj "$P")
cat > "$P/web/orders/order_list/view_model/evil.py" <<'EOF'
from application.orders.order.entity import Order
import framework.db
from config.settings import DEBUG
from .....application import services
from web.orders.order_list.state.order_list_state import OrderListState
url = "application.fake"
# import application.comment
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wi1); E=$?
assert_count "F9a WI1 절대2+프로젝트 패키지+상대 클램핑 4건(주석·문자열 불발화 짝 내장)" 2 "WI1" 4 "$E" "$OUT"
cat > "$P/web/orders/order_list/view_model/evil.py" <<'EOF'
from web.client.orders.order_query_client import OrderQueryClient
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wi1); E=$?
assert "F9b WI1 control — web 내부 import는 clean" 0 - "WI1" "$E" "$OUT"

# ---------- F10: WI2 API 호출 표면은 client/ 전속
P="$T/f10"; BASE=$(mkproj "$P")
cat > "$P/web/orders/order_list/view_model/fetcher.py" <<'EOF'
import requests
from urllib import request
from django.test import Client
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wi2); E=$?
assert_count "F10a WI2 requests·urllib.request·django.test 3건" 2 "WI2" 3 "$E" "$OUT"
rm "$P/web/orders/order_list/view_model/fetcher.py"
cat > "$P/web/client/orders/pay_query_client.py" <<'EOF'
import requests


class PayQueryClient:
    pass
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wi2); E=$?
assert "F10b WI2 control — client/ 안 호출 표면은 clean" 0 - "WI2" "$E" "$OUT"

# ---------- F11: WI3 client 밖 /api/ 리터럴 금지
P="$T/f11"; BASE=$(mkproj "$P")
cat > "$P/web/orders/order_list/view_model/urls_leak.py" <<'EOF'
API = "/api/orders/"
# 주석 속 /api/ 는 불발화
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wi3); E=$?
assert_count "F11a WI3 VM의 API URL 리터럴 1건(주석 불발화 짝 내장)" 2 "WI3" 1 "$E" "$OUT"
rm "$P/web/orders/order_list/view_model/urls_leak.py"
echo 'PAY_URL = "/api/payments/"' >> "$P/web/client/orders/order_query_client.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wi3); E=$?
assert "F11b WI3 control — client 안 리터럴은 clean" 0 - "WI3" "$E" "$OUT"

# ---------- F12: WI4 템플릿 하드코딩 URL
P="$T/f12"; BASE=$(mkproj "$P")
cat > "$P/web/orders/order_list/section/order_list_links.html" <<'EOF'
<a href="/orders/">bad</a>
<form action="/orders/save/">bad</form>
<a href="https://example.com/x">ok-external</a>
<a href="//cdn.example.com/x">ok-protocol-relative</a>
<a href="{% url 'order_list' %}">ok-url-tag</a>
<div hx-get="{% url 'order_list' %}">ok-hx</div>
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wi4); E=$?
assert_count "F12 WI4 루트상대 2건(외부·{% url %} 불발화 짝 내장)" 2 "WI4" 2 "$E" "$OUT"

# ---------- F13: added 줄 게이트 — 레거시 위반 불발화, 신규 줄만 발화
P="$T/f13"; BASE=$(mkproj "$P")
echo "import requests" >> "$P/web/orders/order_list/view_model/order_list_view_model.py"
BASE2=$(commit_all "$P" legacy)
echo "# touched" >> "$P/web/orders/order_list/view_model/order_list_view_model.py"
OUT=$(run_backstop "$P" --diff-base "$BASE2" --only wi); E=$?
assert "F13a 레거시 위반 import 불발화(added 줄 밖)" 0 - "WI2" "$E" "$OUT"
echo "import urllib.request" >> "$P/web/orders/order_list/view_model/order_list_view_model.py"
OUT=$(run_backstop "$P" --diff-base "$BASE2" --only wi); E=$?
assert_count "F13b 신규 위반 줄만 발화(WI2 1건)" 2 "WI2" 1 "$E" "$OUT"

# ---------- F14: WN1 종류 폴더 ↔ 접미사
P="$T/f14"; BASE=$(mkproj "$P")
printf 'class OrderListVm:\n    pass\n' > "$P/web/orders/order_list/view_model/order_list_vm.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn1); E=$?
assert "F14a WN1 축약 접미사 _vm.py 발화" 2 "WN1" - "$E" "$OUT"
rm "$P/web/orders/order_list/view_model/order_list_vm.py"
printf 'class OrderDetailResponse:\n    pass\n' > "$P/web/client/orders/response/order_detail_response.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn1); E=$?
assert "F14b WN1 control — 규약 접미사는 clean" 0 - "WN1" "$E" "$OUT"

# ---------- F15: WN2 section 접두 실재 대조
P="$T/f15"; BASE=$(mkproj "$P")
printf '<p>x</p>\n' > "$P/web/orders/order_list/section/summary.html"
printf '<p>y</p>\n' > "$P/web/orders/order_list/section/order_list_summary.html"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn2); E=$?
assert_count "F15 WN2 무접두 1건(접두 짝은 clean — positive control 내장)" 2 "WN2" 1 "$E" "$OUT"

# ---------- F16: WN3 widget 이름에 view 이름 금지
P="$T/f16"; BASE=$(mkproj "$P")
printf '<p>x</p>\n' > "$P/web/orders/widget/order_list_badge.html"
printf '<p>y</p>\n' > "$P/web/orders/widget/status_badge.html"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn3); E=$?
assert_count "F16 WN3 view 이름 포함 1건(무관 어휘 짝 clean)" 2 "WN3" 1 "$E" "$OUT"

# ---------- F17: WN4 페이지 템플릿 = 화면명
P="$T/f17"; BASE=$(mkproj "$P")
printf '<p>x</p>\n' > "$P/web/orders/order_list/view/wrong_name.html"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn4); E=$?
assert_count "F17 WN4 화면명 불일치 1건(order_list.html 짝은 base에서 green)" 2 "WN4" 1 "$E" "$OUT"

# ---------- F18: WN5 component 부품군 접미사
P="$T/f18"; BASE=$(mkproj "$P")
printf '<p>x</p>\n' > "$P/web/design_system/component/button/fancy_chip.html"
printf '<p>y</p>\n' > "$P/web/design_system/component/button/outline_button.html"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn5); E=$?
assert_count "F18 WN5 부품군 접미사 위반 1건(접미사 짝 clean)" 2 "WN5" 1 "$E" "$OUT"

# ---------- F19: WN6 삼총사 — VM 기준 대응·접두 불일치
P="$T/f19"; BASE=$(mkproj "$P")
mkdir -p "$P/web/orders/order_edit/view" "$P/web/orders/order_edit/view_model" \
  "$P/web/orders/order_edit/state" "$P/web/orders/order_edit/section"
: > "$P/web/orders/order_edit/view/__init__.py"
: > "$P/web/orders/order_edit/view_model/__init__.py"
: > "$P/web/orders/order_edit/state/__init__.py"
: > "$P/web/orders/order_edit/section/.gitkeep"
printf 'class OrderEditViewModel:\n    pass\n' > "$P/web/orders/order_edit/view_model/order_edit_view_model.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn6); E=$?
assert "F19a WN6 VM 대응 미완 발화" 2 "WN6" - "$E" "$OUT"
printf 'def order_edit_view(request):\n    return None\n' > "$P/web/orders/order_edit/view/order_edit_view.py"
printf 'class OrderEditState:\n    pass\n' > "$P/web/orders/order_edit/state/order_edit_state.py"
printf '<p>x</p>\n' > "$P/web/orders/order_edit/view/order_edit.html"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn6); E=$?
assert "F19b WN6 control — 1:1:1:1 완성 후 clean" 0 - "WN6" "$E" "$OUT"
printf 'class StrayState:\n    pass\n' > "$P/web/orders/order_edit/state/stray_state.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn6); E=$?
assert "F19c WN6 접두-화면 개념 불일치 발화" 2 "stray" - "$E" "$OUT"

# ---------- F20: WN7 접두에 _view 끼움 금지
P="$T/f20"; BASE=$(mkproj "$P")
printf 'class X:\n    pass\n' > "$P/web/orders/order_list/view_model/order_list_view_view_model.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn7); E=$?
assert "F20a WN7 order_list_view_view_model.py 발화" 2 "WN7" - "$E" "$OUT"
rm "$P/web/orders/order_list/view_model/order_list_view_view_model.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn7); E=$?
assert "F20b WN7 control — 규약 접두는 clean" 0 - "WN7" "$E" "$OUT"

# ---------- F21: WN8 파일명 snake_case
P="$T/f21"; BASE=$(mkproj "$P")
printf 'a{}\n' > "$P/web/static/css/Order-List.css"
printf 'b{}\n' > "$P/web/static/css/order_detail.css"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn8); E=$?
assert_count "F21 WN8 snake_case 위반 1건(snake 짝 clean)" 2 "WN8" 1 "$E" "$OUT"

# ---------- F22: WP1 기능 JS 허용·신규 legacy core 차단·motion 판형
P="$T/f22"; BASE=$(mkproj "$P")
printf 'console.log(1);\n' > "$P/web/static/js/app.js"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp1); E=$?
assert "F22a WP1 control — 평면 snake_case 기능 JS는 clean" 0 - "WP1" "$E" "$OUT"
printf '(function(){})();\n' > "$P/web/static/js/htmx.js"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp1); E=$?
assert "F22b WP1 신규 legacy htmx core·core 중복 발화" 2 "WP1" - "$E" "$OUT"
rm "$P/web/static/js/htmx.js"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp1); E=$?
assert "F22c WP1 control — canonical htmx core+기능 JS는 clean" 0 - "WP1" "$E" "$OUT"
cp "$SCRIPTS/../assets/motion.js" "$P/web/static/js/motion.js"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp1,wp5); E=$?
assert "F22d WP1·WP5 control — 판형 그대로의 motion.js 공존은 clean" 0 - "WP" "$E" "$OUT"
printf '\nwindow.fetch("/x");\n' >> "$P/web/static/js/motion.js"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp5); E=$?
assert "F22e WP5 motion.js 판형 이탈(수정) 발화" 2 "WP5" - "$E" "$OUT"
rm "$P/web/static/js/motion.js"

# ---------- F23: WP2 inline·CDN·fragment script 금지, page defer load 허용
P="$T/f23"; BASE=$(mkproj "$P")
printf 'document.documentElement.dataset.ready = "1";\n' > "$P/web/static/js/order_list.js"
cat > "$P/web/orders/order_list/section/order_list_head.html" <<'EOF'
<script>alert(1)</script>
<script src="https://cdn.example.com/lib.js"></script>
<script src="{% static 'web/js/order_list.js' %}" defer></script>
EOF
cat >> "$P/web/orders/order_list/view/order_list.html" <<'EOF'
{% block scripts %}
<script src="{% static 'web/js/order_list.js' %}" defer></script>
{% endblock %}
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp2); E=$?
assert_count "F23 WP2 inline+CDN+fragment 3건(page defer 짝 clean)" 2 "WP2" 3 "$E" "$OUT"

# ---------- F23b: WP2 CDN 위장·ghost src 차단, base motion 정확 경로 clean
P="$T/f23b"; BASE=$(mkproj "$P")
cp "$SCRIPTS/../assets/motion.js" "$P/web/static/js/motion.js"
cat > "$P/web/orders/order_list/section/order_list_tail.html" <<'EOF'
<script src="https://cdn.example.com/x.js" id="motion-loader"></script>
<script src="https://unpkg.com/htmx.org/dist/htmx.min.js"></script>
<script src="{% static 'web/js/ghost.js' %}" defer></script>
EOF
cat >> "$P/web/base/base.html" <<'EOF'
<script src="{% static 'web/js/motion.js' %}" defer></script>
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp2); E=$?
assert_count "F23b WP2 CDN 위장+ghost 3건(base motion 짝 clean)" 2 "WP2" 3 "$E" "$OUT"

# ---------- F24: WP3 인라인 이벤트 핸들러 속성 금지
P="$T/f24"; BASE=$(mkproj "$P")
cat > "$P/web/orders/order_list/section/order_list_actions.html" <<'EOF'
<button onclick="doIt()">bad</button>
<div hx-on:click="alert(1)">bad</div>
<div hx-get="{% url 'order_list' %}" hx-target="#list">ok</div>
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp3); E=$?
assert_count "F24 WP3 onclick+hx-on 2건(hx 선언 속성 짝 clean)" 2 "WP3" 2 "$E" "$OUT"

# ---------- F24b: WP3 htmx js: 채널·hx-trigger 조건식 금지
P="$T/f24b"; BASE=$(mkproj "$P")
cat > "$P/web/orders/order_list/section/order_list_filters.html" <<'EOF'
<div hx-post="{% url 'order_list' %}" hx-vals='js:{x: compute()}'>bad</div>
<form hx-headers='js:{"X-T": token()}'>bad</form>
<div hx-get="{% url 'order_list' %}" hx-trigger="click[ctrlKey]">bad</div>
<div hx-get="{% url 'order_list' %}" hx-vals='{"page": 2}' hx-trigger="click">ok</div>
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp3); E=$?
assert_count "F24b WP3 js:·조건식 3건(정적 JSON·이벤트명 짝 clean)" 2 "WP3" 3 "$E" "$OUT"

# ---------- F25: WP4 색 리터럴 — tokens.css만 예외
P="$T/f25"; BASE=$(mkproj "$P")
cat > "$P/web/static/css/order_theme.css" <<'EOF'
h1 { color: #ff0000; }
p { background: rgb(0, 0, 0); }
a { color: var(--color-primary); }
EOF
printf '%s\n' '--color-accent: #00ff00;' >> "$P/web/design_system/foundation/tokens.css"
printf '<a href="#anchor">ok</a>\n' > "$P/web/orders/order_list/section/order_list_jump.html"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp4); E=$?
assert_count "F25 WP4 색 리터럴 2건(tokens.css·var()·#anchor 짝 clean)" 2 "WP4" 2 "$E" "$OUT"

# ---------- F26: 비git 전역 퇴화 notice
P="$T/f26"; BASE=$(mkproj "$P")
P2="$T/f26_nogit"; cp -R "$P" "$P2"; rm -rf "$P2/.git"
OUT=$(run_backstop "$P2"); E=$?
assert "F26 비git 퇴화 notice + green 프로젝트 0" 0 "git 저장소 아님" "BLOCKER" "$E" "$OUT"

# ---------- F27: git이나 --diff-base 없음 — 전역 퇴화 notice
P="$T/f27"; BASE=$(mkproj "$P")
OUT=$(run_backstop "$P"); E=$?
assert "F27 --diff-base 없음 퇴화 notice" 0 "diff-base 없음" "BLOCKER" "$E" "$OUT"

# ---------- F28: --only 패밀리 필터
P="$T/f28"; BASE=$(mkproj "$P")
printf 'import requests\n' >> "$P/web/orders/order_list/view_model/order_list_view_model.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wn); E=$?
assert "F28a --only wn — WI 위반 비표시" 0 - "WI2" "$E" "$OUT"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wi); E=$?
assert "F28b --only wi — WI 위반 표시" 2 "WI2" - "$E" "$OUT"

# ---------- F29: 사용 오류 exit 1 계약
OUT=$(run_backstop); E=$?
assert "F29a 인자 없음 → 1" 1 "사용" - "$E" "$OUT"
OUT=$(run_backstop "$T/없는경로"); E=$?
assert "F29b 디렉터리 아님 → 1" 1 "디렉터리 아님" - "$E" "$OUT"
P="$T/f29"; BASE=$(mkproj "$P")
OUT=$(run_backstop "$P" --diff-base deadbeef99); E=$?
assert "F29c diff-base 해석 불가 → 1" 1 "해석 불가" - "$E" "$OUT"
OUT=$(run_backstop "$P" --frobnicate); E=$?
assert "F29d 알 수 없는 옵션 → 1" 1 "알 수 없는 옵션" - "$E" "$OUT"
P2="$T/f29_noweb"; mkdir -p "$P2"
OUT=$(run_backstop "$P2"); E=$?
assert "F29e web/ 없음(전제 실패) → 1" 1 "web/ 없음" - "$E" "$OUT"

echo
echo "fixtures_backstop: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
