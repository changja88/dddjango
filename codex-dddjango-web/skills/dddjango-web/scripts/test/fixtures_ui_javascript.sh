#!/usr/bin/env bash
# UI JavaScript·HTMX 통합 계약의 결정적 경계 fixture.
# 각 케이스는 실제 backstop을 임시 git 프로젝트에 실행해 경로·태그·diff gate를 검증한다.
set -u
SCRIPTS="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0; FAIL=0

run_backstop() { python3 "$SCRIPTS/backstop.py" "$@" 2>&1; }

assert() {
  local name="$1" wantexit="$2" want="$3" unwant="$4" gotexit="$5" out="$6" ok=1
  [ "$gotexit" != "$wantexit" ] && ok=0
  [ "$want" != "-" ] && ! grep -qF -- "$want" <<<"$out" && ok=0
  [ "$unwant" != "-" ] && grep -qF -- "$unwant" <<<"$out" && ok=0
  if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS $name"; else
    FAIL=$((FAIL+1)); echo "FAIL $name (exit=$gotexit want=$wantexit)"; echo "$out" | head -24 | sed 's/^/    /'
  fi
}

assert_count() {
  local name="$1" wantexit="$2" pat="$3" wantn="$4" gotexit="$5" out="$6"
  local n; n=$(grep -cF -- "$pat" <<<"$out" || true)
  if [ "$gotexit" = "$wantexit" ] && [ "$n" = "$wantn" ]; then
    PASS=$((PASS+1)); echo "PASS $name"
  else
    FAIL=$((FAIL+1)); echo "FAIL $name (exit=$gotexit want=$wantexit, $pat=$n want=$wantn)"
    echo "$out" | head -24 | sed 's/^/    /'
  fi
}

commit_all() {
  git -C "$1" -c user.name=t -c user.email=t@t add -A >/dev/null
  git -C "$1" -c user.name=t -c user.email=t@t commit -qm "$2"
  git -C "$1" rev-parse HEAD
}

mkproj() {
  local p="$1"
  mkdir -p "$p/web/base" "$p/web/static/css" "$p/web/static/js" \
    "$p/web/static/htmx" "$p/web/static/images" \
    "$p/web/orders/order_list/view" "$p/web/orders/order_list/section"
  cat > "$p/web/base/base.html" <<'EOF'
{% load static %}
<html><body>
{% block content %}{% endblock %}
<script src="{% static 'web/htmx/htmx.min.js' %}" defer></script>
{% block scripts %}{% endblock %}
</body></html>
EOF
  printf '(function(){})();\n' > "$p/web/static/htmx/htmx.min.js"
  : > "$p/web/static/css/.gitkeep"
  : > "$p/web/static/js/.gitkeep"
  : > "$p/web/static/images/.gitkeep"
  cat > "$p/web/orders/order_list/view/order_list.html" <<'EOF'
{% extends "base/base.html" %}
{% load static %}
{% block content %}{% include "orders/order_list/section/order_list_panel.html" %}{% endblock %}
EOF
  printf '<div id="orders">orders</div>\n' > "$p/web/orders/order_list/section/order_list_panel.html"
  git -C "$p" init -q
  commit_all "$p" base
}

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# J1: 기능 JS + page defer + HTMX include + 실제 json_script는 모두 허용한다.
P="$T/j1"; BASE=$(mkproj "$P")
cat > "$P/web/static/js/password_visibility.js" <<'EOF'
document.querySelectorAll('[data-password-visibility]');
const payload = JSON.parse(document.getElementById('ui-data').textContent);
EOF
cat > "$P/web/static/htmx/order_refresh.html" <<'EOF'
<button hx-get="{% url 'order_list_panel' %}" hx-target="#orders">refresh</button>
EOF
cat >> "$P/web/orders/order_list/view/order_list.html" <<'EOF'
{% block scripts %}<script src="{% static 'web/js/password_visibility.js' %}" defer></script>{% endblock %}
EOF
cat > "$P/web/orders/order_list/section/order_list_panel.html" <<'EOF'
<div data-password-visibility>
  {% include "static/htmx/order_refresh.html" with state=state %}
  {{ state.ui_data|json_script:"ui-data" }}
</div>
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws6,wp1,wp2,wp3,wn8); E=$?
assert "J1 기능 JS·page defer·HTMX include·json_script positive" 0 "blocker 0건" "BLOCKER" "$E" "$OUT"

# J2: 기능 파일은 static/js 평면 <기능>.js만 허용한다.
P="$T/j2"; BASE=$(mkproj "$P")
mkdir -p "$P/web/scripts" "$P/web/static/js/nested"
printf 'void 0;\n' > "$P/web/scripts/wrong_place.js"
printf 'void 0;\n' > "$P/web/static/js/nested/password_visibility.js"
printf 'void 0;\n' > "$P/web/static/js/vendor.min.js"
printf 'void 0;\n' > "$P/web/static/js/module.mjs"
printf 'void 0;\n' > "$P/web/static/js/common.cjs"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp1); E=$?
assert_count "J2 WP1 wrong/nested/min/mjs/cjs 5건" 2 "[WP1]" 5 "$E" "$OUT"

# J3: static/htmx도 평면이며 선언 html과 canonical core 외 파일을 받지 않는다.
P="$T/j3"; BASE=$(mkproj "$P")
mkdir -p "$P/web/static/htmx/nested"
printf '<button>bad</button>\n' > "$P/web/static/htmx/nested/order_refresh.html"
printf 'void 0;\n' > "$P/web/static/htmx/order_refresh.js"
printf 'void 0;\n' > "$P/web/static/htmx/extra.mjs"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ws6); E=$?
assert_count "J3 WS6 htmx nested·wrong js·mjs 3건" 2 "[WS6]" 3 "$E" "$OUT"

# J4: src는 실제 src 속성 + 정확한 Django static 인자 + 존재하는 로컬 파일이어야 한다.
P="$T/j4"; BASE=$(mkproj "$P")
printf 'void 0;\n' > "$P/web/static/js/password_visibility.js"
cat >> "$P/web/orders/order_list/view/order_list.html" <<'EOF'
{% block scripts %}
<script data-src="{% static 'web/js/password_visibility.js' %}" defer></script>
<script src="https://cdn.example/x.js" defer></script>
<script src="data:text/javascript,alert(1)" defer></script>
<script src="javascript:alert(1)" defer></script>
<script src="{% static 'web/js/ghost.js' %}" defer></script>
<script src="{% static 'web/js/Password_visibility.js' %}" defer></script>
<script src="/static/web/js/password_visibility.js?x=js/password_visibility.js" defer></script>
<script src="{% static 'web/js/password_visibility.js' %}?v=1" defer></script>
<script src="{% static 'web/js/password_visibility.js' %}" data-note=" defer "></script>
</script>
{% endblock %}
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp2); E=$?
assert_count "J4 WP2 actual src/defer·CDN·data·javascript·ghost·case·suffix 9건" 2 "[WP2]" 9 "$E" "$OUT"

# J4b: quoted `>`는 opener 경계가 아니며 실제 뒤쪽 src/defer를 보존한다.
P="$T/j4b"; BASE=$(mkproj "$P")
printf 'void 0;\n' > "$P/web/static/js/toggle.js"
cat >> "$P/web/base/base.html" <<'EOF'
<script data-label="a > b" src="{% static 'web/js/toggle.js' %}" defer></script>
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp2); E=$?
assert "J4b quoted greater-than opener positive" 0 "blocker 0건" "BLOCKER" "$E" "$OUT"

# J5: 실행 위치와 속성 — page/base, classic defer, module만 허용한다.
P="$T/j5"; BASE=$(mkproj "$P")
printf 'void 0;\n' > "$P/web/static/js/password_visibility.js"
cat >> "$P/web/base/base.html" <<'EOF'
<script src="{% static 'web/js/password_visibility.js' %}" defer></script>
<script src="{% static 'web/js/password_visibility.js' %}" type="module"></script>
EOF
cat >> "$P/web/orders/order_list/view/order_list.html" <<'EOF'
<script src="{% static 'web/js/password_visibility.js' %}"></script>
<script src="{% static 'web/js/password_visibility.js' %}" type="module" async></script>
EOF
cat >> "$P/web/orders/order_list/section/order_list_panel.html" <<'EOF'
<script src="{% static 'web/js/password_visibility.js' %}" defer></script>
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp2); E=$?
assert "J5 WP2 no-defer·async·fragment·duplicate 발화" 2 "classic 외부 스크립트는 defer" - "$E" "$OUT"
assert "J5 WP2 fragment 위치 발화" 2 "fragment" - "$E" "$OUT"
assert "J5 WP2 page/base 중복 로드 발화" 2 "중복 로드" - "$E" "$OUT"

# J5b: type=module은 defer 없이도 독립적으로 허용한다.
P="$T/j5b"; BASE=$(mkproj "$P")
printf 'export {};\n' > "$P/web/static/js/password_visibility.js"
cat >> "$P/web/orders/order_list/view/order_list.html" <<'EOF'
{% load static %}<script src="{% static 'web/js/password_visibility.js' %}" type="module"></script>
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp2); E=$?
assert "J5b isolated module positive" 0 "blocker 0건" "BLOCKER" "$E" "$OUT"

# J5c: 같은 템플릿의 기존 로드에 신규 중복을 더하면 diff gate에서도 잡는다.
P="$T/j5c"; BASE=$(mkproj "$P")
printf 'void 0;\n' > "$P/web/static/js/password_visibility.js"
cat >> "$P/web/orders/order_list/view/order_list.html" <<'EOF'
{% load static %}<script src="{% static 'web/js/password_visibility.js' %}" defer></script>
EOF
BASE2=$(commit_all "$P" existing-feature-load)
cat >> "$P/web/orders/order_list/view/order_list.html" <<'EOF'
<script src="{% static 'web/js/password_visibility.js' %}" defer></script>
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE2" --only wp2); E=$?
assert "J5c duplicate against unchanged baseline load" 2 "중복 로드" - "$E" "$OUT"

# J5d: 신규 중복이 기존 load보다 앞에 삽입되어도 문서 순서와 무관하게 잡는다.
P="$T/j5d"; BASE=$(mkproj "$P")
printf 'void 0;\n' > "$P/web/static/js/toggle.js"
cat >> "$P/web/base/base.html" <<'EOF'
<div>stable</div>
<script src="{% static 'web/js/toggle.js' %}" defer></script>
EOF
BASE2=$(commit_all "$P" existing-later-load)
cat > "$P/web/base/base.html" <<'EOF'
{% load static %}
<html><body>
{% block content %}{% endblock %}
<script src="{% static 'web/htmx/htmx.min.js' %}" defer></script>
{% block scripts %}{% endblock %}
</body></html>
<script src="{% static 'web/js/toggle.js' %}" defer></script>
<div>stable</div>
<script src="{% static 'web/js/toggle.js' %}" defer></script>
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE2" --only wp2); E=$?
assert "J5d prepended duplicate before unchanged baseline load" 2 "중복 로드" - "$E" "$OUT"

# J6: opener가 레거시 줄이어도 변경된 multiline 속성을 diff gate가 검사한다.
P="$T/j6"; BASE=$(mkproj "$P")
printf 'void 0;\n' > "$P/web/static/js/password_visibility.js"
cat >> "$P/web/orders/order_list/view/order_list.html" <<'EOF'
<script
  data-label="a > b"
  src="{% static 'web/js/password_visibility.js' %}"
  defer
></script>
EOF
BASE2=$(commit_all "$P" multiline)
cat > "$P/web/orders/order_list/view/order_list.html" <<'EOF'
{% extends "base/base.html" %}
{% load static %}
{% block content %}{% include "orders/order_list/section/order_list_panel.html" %}{% endblock %}
<script
  data-label="a > b"
  src="{% static 'web/js/password_visibility.js' %}"
  async
></script>
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE2" --only wp2); E=$?
assert "J6 WP2 multiline 기존 opener 내부 async 변경 검출" 2 "async" - "$E" "$OUT"

# J7: 기존 legacy core는 diff gate에서 소비 가능하지만 새 canonical 이중 설치는 차단한다.
P="$T/j7"; BASE=$(mkproj "$P")
rm "$P/web/static/htmx/htmx.min.js"
printf '(function(){})();\n' > "$P/web/static/js/htmx.min.js"
cat > "$P/web/base/base.html" <<'EOF'
{% load static %}<html><body><script src="{% static 'js/htmx.min.js' %}"></script></body></html>
EOF
BASE2=$(commit_all "$P" legacy-core)
printf 'void 0;\n' > "$P/web/static/js/password_visibility.js"
cat >> "$P/web/orders/order_list/view/order_list.html" <<'EOF'
{% load static %}<script src="{% static 'web/js/password_visibility.js' %}" defer></script>
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE2" --only wp1,wp2); E=$?
assert "J7a genuine legacy baseline core remains consumable" 0 "blocker 0건" "BLOCKER" "$E" "$OUT"
printf '(function(){})();\n' > "$P/web/static/htmx/htmx.min.js"
OUT=$(run_backstop "$P" --diff-base "$BASE2" --only wp1); E=$?
assert "J7b canonical+legacy core duplicate blocked" 2 "core 중복" - "$E" "$OUT"

# J8: reserved core/motion 이름은 일반 기능 파일로 위장할 수 없다.
P="$T/j8"; BASE=$(mkproj "$P")
printf 'void 0;\n' > "$P/web/static/js/htmx.js"
printf 'void 0;\n' > "$P/web/static/js/motion.js"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp1,wp5); E=$?
assert "J8a 신규 legacy htmx 이름 reserved" 2 "예약 이름" - "$E" "$OUT"
assert "J8b motion 이름은 byte 판형으로만 허용" 2 "WP5" - "$E" "$OUT"

# J9: 기존 WP3 채널은 UI JS 허용 뒤에도 그대로 차단한다.
P="$T/j9"; BASE=$(mkproj "$P")
cat >> "$P/web/orders/order_list/section/order_list_panel.html" <<'EOF'
<button onclick="bad()">bad</button>
<button hx-on:click="bad()">bad</button>
<button hx-vals='js:{x: bad()}'>bad</button>
<button hx-trigger="click[ctrlKey]">bad</button>
EOF
OUT=$(run_backstop "$P" --diff-base "$BASE" --only wp3); E=$?
assert_count "J9 WP3 inline/hx-on/js:/조건식 회귀 4건" 2 "[WP3]" 4 "$E" "$OUT"

echo "fixtures_ui_javascript: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
