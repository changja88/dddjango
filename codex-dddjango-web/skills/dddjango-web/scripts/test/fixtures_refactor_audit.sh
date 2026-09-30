#!/usr/bin/env bash
# dddjango-web refactor_audit.py 픽스처 (plan · plan --against · plan --names · check · check-verdict · residual · standing · self-test).
# 합성 web 프로젝트 + 합성 플러그인 루트(판정 문장을 고정) — 각 red 에 양성 대조 짝.
set -u
SCRIPTS="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0; FAIL=0

assert() { # assert <이름> <기대exit> <있어야 할 문자열|-> <없어야 할 문자열|-> <실제exit> <출력>
  local name="$1" wantexit="$2" want="$3" unwant="$4" gotexit="$5" out="$6" ok=1
  [ "$gotexit" != "$wantexit" ] && ok=0
  [ "$want" != "-" ] && ! grep -qF -- "$want" <<<"$out" && ok=0
  [ "$unwant" != "-" ] && grep -qF -- "$unwant" <<<"$out" && ok=0
  if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS $name"; else
    FAIL=$((FAIL+1)); echo "FAIL $name (exit=$gotexit want=$wantexit)"; echo "$out" | head -20 | sed 's/^/    /'
  fi
}

commit_all() {
  git -C "$1" -c user.name=t -c user.email=t@t add -A >/dev/null
  git -C "$1" -c user.name=t -c user.email=t@t commit -qm "$2"
  git -C "$1" rev-parse HEAD
}

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
P="$T/proj"
RA() { (cd "$P" && python3 "$SCRIPTS/refactor_audit.py" "$@" 2>&1); }
RAP() { (cd "$P" && python3 "$SCRIPTS/refactor_audit.py" --platform claude --plugin-root "$T/plugin" "$@" 2>&1); }

# ---------- 합성 프로젝트: 영역 home·chart · base · 정적(css·js·images) · client
mkdir -p "$P/config" "$P/web/base" "$P/web/home/home/view" "$P/web/home/home/section" \
  "$P/web/chart/chart/section" "$P/web/chart/chart/view" "$P/web/chart/chart/view_model" \
  "$P/web/static/css" "$P/web/static/js" "$P/web/static/images" "$P/web/client/users/response" "$P/tests/web"
echo "SECRET_KEY = 'x'" > "$P/config/settings.py"
: > "$P/web/__init__.py"
echo "urlpatterns = []" > "$P/web/urls.py"
cat > "$P/web/base/base.html" <<'EOF'
{% load static %}
<script src="{% static 'js/toast.js' %}"></script>
EOF
cat > "$P/web/home/urls.py" <<'EOF'
from django.urls import path

urlpatterns = [
    path("", lambda r: None, name="home"),
]
EOF
cat > "$P/web/home/home/view/home_view.py" <<'EOF'
def _render_page(request):
    return None


def redirect_home():
    return _render_page(None)
EOF
printf 'X = 1\n' > "$P/web/home/home/view/home_view2.py"
cat > "$P/web/home/home/view/home.html" <<'EOF'
{% load static %}
<link rel="stylesheet" href="{% static 'css/home.css' %}">
<script src="{% static 'js/shared.js' %}"></script>
<script src="{% static 'js/toast.js' %}"></script>
EOF
cat > "$P/web/home/home/section/home_card.html" <<'EOF'
<img src="{% static 'images/bad-name.png' %}" style="color: #ffffff">
<p style="color: #000000">card</p>
EOF
cat > "$P/web/chart/chart/section/chart_panel.html" <<'EOF'
<script src="{% static 'js/shared.js' %}"></script>
{% include "home/home/section/home_card.html" %}
EOF
cat > "$P/web/chart/chart/view/chart_view.py" <<'EOF'
def _render_page(request):
    return None


def chart(request):
    return _render_page(request)
EOF
cat > "$P/web/chart/chart/view_model/chart_view_model.py" <<'EOF'
from web.home.home.view.home_view import redirect_home
from web.home.home.view.home_view2 import X


def go():
    return redirect_home(), X
EOF
printf '.home { color: var(--c); background: url("../images/bg_home.png"); }\n' > "$P/web/static/css/home.css"
printf 'png' > "$P/web/static/images/bg_home.png"
printf '(function(){})();\n' > "$P/web/static/js/shared.js"
printf '(function(){})();\n' > "$P/web/static/js/toast.js"
printf 'png' > "$P/web/static/images/bad-name.png"
printf 'png' > "$P/web/static/images/orphan.png"
cat > "$P/web/client/users/response/user_response.py" <<'EOF'
def parse(payload):
    return dict(
        birth_date=_optional_str(payload, "birth_date"),
        name=_optional_str(payload, "user_name"),
    )
EOF
printf 'def test_home():\n    assert True\n' > "$P/tests/web/test_home.py"
git -C "$P" init -q
BASE=$(commit_all "$P" base)
mkdir -p "$P/.dddjango-web/run"
python3 "$SCRIPTS/backstop.py" "$P" --debt-scan --refactor --json "$P/.dddjango-web/run/debt-g0.json" >/dev/null

# ---------- A: plan — 정적 파일 소유 판정 순서 · 경계 교차 소비자 · 줄 편집 (가)
A="$P/.dddjango-web/run/audit/20260927-120000"
OUT=$(RA plan web/home --debt .dddjango-web/run/debt-g0.json --out "$A"); E=$?
assert "A1 plan web/home 실행" 0 "요약: plan 단위 web/home" - "$E" "$OUT"
PLAN=$(cat "$A/plan.md" 2>/dev/null)
assert "A2 css/home.css = 영역 전속(범위 파일)" 0 '`web/static/css/home.css` — 영역 전속 정적' - 0 "$PLAN"
assert "A3 js/shared.js = 경계 교차(소유 chart·home)" 0 '`web/static/js/shared.js` — 소유 chart·home' - 0 "$PLAN"
assert "A4 js/toast.js = 비영역 참조(base 로드) — 범위 밖" 0 "| web/static/js/toast.js | 비영역 참조 |" '`web/static/js/toast.js` — 영역' 0 "$PLAN"
assert "A5 orphan.png 은 home 판정표에 없음(무참조)" 0 - "orphan.png" 0 "$PLAN"
assert "A6 경계 교차 소비자 = chart_panel include 줄" 0 '`web/chart/chart/section/chart_panel.html:2`' - 0 "$PLAN"
assert "A7 줄 편집 (가) = 범위 파일을 가리키는 범위 밖 include 줄" 0 '`web/chart/chart/section/chart_panel.html:2` — (가)' - 0 "$PLAN"
OUT=$(RA plan web/home --debt .dddjango-web/run/debt-g0.json --out "$A"); E=$?
assert "A8 --out 에 plan.md 가 있으면 덮지 않음" 1 "덮지 않는다" - "$E" "$OUT"
OUT=$(RA plan web/home/home --debt .dddjango-web/run/debt-g0.json --out "$T/x"); E=$?
assert "A9 단위 안쪽 경로 = 실행 불능" 1 "단위 안쪽 경로" - "$E" "$OUT"
OUT=$(RA plan web/nope --debt .dddjango-web/run/debt-g0.json --out "$T/x"); E=$?
assert "A10 없는 단위 = 실행 불능" 1 "단위 없음" - "$E" "$OUT"
assert "A11 영역 전속 CSS 만 참조하는 이미지 = 소유자 전이로 영역 전속" 0 '`web/static/images/bg_home.png` — 영역 전속 정적' - 0 "$PLAN"


# ---------- A′ (R8d ②-A): 경계 교차 소비자 = 범위 파일을 가리키는 범위 밖 web/ 줄 중 정적 로드만 하는 줄 밖 전부(모양 무관)
PSEC() { sed -n "/^## $2\$/,/^## /p" "$1"; }
assert "A12 다른 영역 VM 의 from-import 두 줄 = 경계 교차 소비자(Python 모양)" 0 '`web/chart/chart/view_model/chart_view_model.py:2`' - 0 "$(PSEC "$A/plan.md" '경계 교차 소비자')"
assert "A12′ 같은 줄은 줄 편집 (가) 아님(정적 로드 줄이 아니다)" 0 - 'chart_view_model.py:1` — (가)' 0 "$PLAN"
Q="$T/projq"
mkdir -p "$Q/config" "$Q/web/home/home/view_model" "$Q/web/home/home/view" "$Q/web/home/home/section" "$Q/web/home/home/state" \
  "$Q/web/auth/login/view" "$Q/web/chart/chart/view" "$Q/tests/web"
echo "SECRET_KEY = 'x'" > "$Q/config/settings.py"
for d in web web/home web/home/home web/home/home/view_model web/home/home/view web/home/home/state web/auth web/chart; do : > "$Q/$d/__init__.py"; done
echo "urlpatterns = []" > "$Q/web/urls.py"
printf 'class HomeViewModel:\n    def redirect_authenticated(self, k):\n        return None\n' > "$Q/web/home/home/view_model/home_view_model.py"
printf 'class HomeState:\n    pass\n' > "$Q/web/home/home/state/home_state.py"
printf '<nav></nav>\n' > "$Q/web/home/home/section/home_bottom_nav.html"
printf '<div>{%% include "home/home/section/home_bottom_nav.html" %%}</div>\n' > "$Q/web/home/home/view/home.html"
V="$Q/web/auth/login/view"
printf 'from web.home.home.view_model.home_view_model import HomeViewModel\n' > "$V/s_a_from_import.py"
printf 'import web.home.home.view_model.home_view_model as hvm\n' > "$V/s_b_import_as.py"
printf 'from web.home.home.view_model import home_view_model\n' > "$V/s_c_pkg_import.py"
printf 'from ....home.home.view_model.home_view_model import HomeViewModel\n' > "$V/s_d_relative.py"
printf 'TARGET = "web.home.home.view_model.home_view_model.HomeViewModel"\n' > "$V/s_e_string.py"
printf 'from web.home.home.view_model.home_view_model import (\n    HomeViewModel,\n)\n' > "$V/s_f_multiline.py"
printf 'def f():\n    from web.home.home.view_model.home_view_model import HomeViewModel\n    return HomeViewModel()\n' > "$V/s_g_local_import.py"
printf 'def v(request):\n    return render(request, "home/home/view/home.html", {})\n' > "$V/s_h_render_tpl.py"
printf 'from web.home.home.state.home_state import HomeState\n' > "$V/s_i_state.py"
printf 'import importlib\nm = importlib.import_module("web.home.home.view_model.home_view_model")\n' > "$V/s_j_importlib.py"
C="$Q/web/chart/chart/view"
printf '{%% include "home/home/section/home_bottom_nav.html" %%}\n' > "$C/s_k_include.html"
printf '{%% extends "home/home/view/home.html" %%}\n' > "$C/s_l_extends.html"
printf '{%% include "home/home/section/"|add:"home_bottom_nav.html" %%}\n' > "$C/s_m_dyn_include.html"
printf '<a href="{%% url %s %%}">h</a>\n' "'home:home'" > "$C/s_n_url.html"
printf 'from web.home.home.view_model.home_view_model import HomeViewModel\n' > "$Q/tests/web/test_home_vm.py"
printf '# web.home.home.view_model.home_view_model의 HomeViewModel 을 쓴다\n' > "$Q/web/chart/chart/view/s_o_korean.py"
mkdir -p "$Q/web/client/users/response"
printf 'def parse(payload):\n    return payload\n' > "$Q/web/client/users/response/user_response.py"
printf 'from web.client.users.response.user_response import parse\n' > "$Q/web/chart/chart/view/s_r_client.py"
git -C "$Q" init -q; commit_all "$Q" base >/dev/null
mkdir -p "$Q/.dddjango-web/run"
python3 "$SCRIPTS/backstop.py" "$Q" --debt-scan --refactor --json "$Q/.dddjango-web/run/debt-g0.json" >/dev/null
RQ() { (cd "$Q" && python3 "$SCRIPTS/refactor_audit.py" "$@" 2>&1); }
AQ="$Q/.dddjango-web/run/audit/20260930-120000"
OUT=$(RQ plan web/home --debt .dddjango-web/run/debt-g0.json --out "$AQ"); E=$?
CQ=$(PSEC "$AQ/plan.md" '경계 교차 소비자')
assert "AQ0 plan web/home(모양 표본 저장소)" 0 "소비자 12" - "$E" "$OUT"
for s in s_a_from_import.py:1 s_b_import_as.py:1 s_c_pkg_import.py:1 s_e_string.py:1 s_f_multiline.py:1 s_g_local_import.py:2 \
         s_h_render_tpl.py:2 s_i_state.py:1 s_j_importlib.py:2; do
  assert "AQ1 Python·문자열 모양 $s = 소비자" 0 "\`web/auth/login/view/$s\`" - 0 "$CQ"
done
assert "AQ2 include = 소비자 + 줄 편집 (가)" 0 '`web/chart/chart/view/s_k_include.html:1` — (가)' - 0 "$(PSEC "$AQ/plan.md" '줄 편집')"
assert "AQ2′ extends = 소비자" 0 '`web/chart/chart/view/s_l_extends.html:1`' - 0 "$CQ"
assert "AQ2″ include = 소비자(소비자 절 단위)" 0 '`web/chart/chart/view/s_k_include.html:1`' - 0 "$CQ"
assert "AQ3 한계 고정 — 상대 import 미탐" 0 - "s_d_relative" 0 "$CQ"
assert "AQ3′ 한계 고정 — 동적 include 미탐" 0 - "s_m_dyn_include" 0 "$CQ"
assert "AQ3″ 한계 고정 — URL 이름 참조 미탐" 0 - "s_n_url" 0 "$CQ"
assert "AQ4 web/ 밖(tests/) 적중 = web/ 밖 참조 줄" 0 '`tests/web/test_home_vm.py:1`' - 0 "$(PSEC "$AQ/plan.md" 'web\/ 밖 참조 줄(치환 후보)')"
assert "AQ4′ web/ 밖(tests/) 적중 = 소비자 아님" 0 - "test_home_vm" 0 "$CQ"
OUT=$(RQ plan web/home --debt .dddjango-web/run/debt-g0.json --against "$AQ/plan.md"); E=$?
assert "AQ5 같은 트리 --against = 같음" 0 "plan --against 같음" - "$E" "$OUT"
grep -v 'web/auth/login/view/' "$AQ/plan.md" > "$T/plan-old-consumers.md"
OUT=$(RQ plan web/home --debt .dddjango-web/run/debt-g0.json --against "$T/plan-old-consumers.md"); E=$?
assert "AQ6 수리 전 plan.md(Python 소비자 없음) --against = 다름 경계 교차 소비자(새 점검 · fail-closed)" 2 "다름 경계 교차 소비자" - "$E" "$OUT"
assert "AQ7 주석 줄(한글이 바로 붙은 점 경로) = 소비자" 0 '`web/chart/chart/view/s_o_korean.py:1`' - 0 "$CQ"
OUT=$(RQ plan web/client/users --debt .dddjango-web/run/debt-g0.json --out "$T/aqc"); E=$?
assert "AQ8 client 단위 — 다른 영역의 import 줄 = 소비자(HEAD 는 0 → G2 영향 화면 공백)" 0 '`web/chart/chart/view/s_r_client.py:1`' - "$E" "$(PSEC "$T/aqc/plan.md" '경계 교차 소비자')"

# ---------- B: plan --against — 여섯 목록 대조(쓰지 않는다)
OUT=$(RA plan web/home --debt .dddjango-web/run/debt-g0.json --against "$A/plan.md"); E=$?
assert "B1 같은 트리 = 같음 exit 0" 0 "plan --against 같음" - "$E" "$OUT"
printf '<link href="{%% static %s %%}">\n' "'css/home.css'" > "$P/web/chart/chart/section/chart_legend.html"
OUT=$(RA plan web/home --debt .dddjango-web/run/debt-g0.json --against "$A/plan.md"); E=$?
assert "B2 다른 영역이 범위 정적 파일을 참조 = 다름 exit 2" 2 "다름 범위 파일" - "$E" "$OUT"
rm "$P/web/chart/chart/section/chart_legend.html"
printf '# 한 줄 변경\n' >> "$P/web/home/home/view/home_view2.py"
OUT=$(RA plan web/home --debt .dddjango-web/run/debt-g0.json --against "$A/plan.md"); E=$?
assert "B3 범위 파일 작업 트리 변경(목록 같음) = 다름 ② exit 2" 2 "② 기록 HEAD" - "$E" "$OUT"
git -C "$P" checkout -q -- web/home/home/view/home_view2.py
printf 'x\n' > "$P/web/home/home/view/scratch.txt"
OUT=$(RA plan web/home --debt .dddjango-web/run/debt-g0.json --against "$A/plan.md"); E=$?
assert "B4 단위 안 미추적 파일 = 다름 ③ exit 2" 2 "③ 범위 미추적 파일" - "$E" "$OUT"
rm "$P/web/home/home/view/scratch.txt"
sed 's/^- 범위 미커밋 변경 0$/- 범위 미커밋 변경 1/' "$A/plan.md" > "$T/plan-dirty.md"
OUT=$(RA plan web/home --debt .dddjango-web/run/debt-g0.json --against "$T/plan-dirty.md"); E=$?
assert "B5 기록 plan 의 범위 미커밋 변경 1 = 다름 ① exit 2" 2 "① 기록 plan 의 범위 미커밋 변경" - "$E" "$OUT"
OUT=$(RA plan web/home --debt .dddjango-web/run/debt-g0.json --against "$A/plan.md"); E=$?
assert "B6 되돌린 뒤 = 같음 exit 0" 0 "plan --against 같음" - "$E" "$OUT"

# ---------- C: 편집 줄 키 · 키 전체 줄 (다) — web/static/images 실행
C="$P/.dddjango-web/run/audit/c"
OUT=$(RA plan web/static/images --debt .dddjango-web/run/debt-g0.json --out "$C"); E=$?
PLANC=$(cat "$C/plan.md" 2>/dev/null)
assert "C1 WN8 키 범위 안" 0 '`WN8|static/images/bad-name.png`' - "$E" "$PLANC"
assert "C2 참조 치환 줄 = home_card:1" 0 '`web/home/home/section/home_card.html:1`' - 0 "$PLANC"
assert "C3 참조 치환 줄의 WP4 = 편집 줄 키" 0 '`WP4|home/home/section/home_card.html` — ' - 0 "$PLANC"
assert "C4 그 키의 다른 발견 줄 = 키 전체 줄 (다)" 0 '`web/home/home/section/home_card.html:2` — (다)' - 0 "$PLANC"

# ---------- D: plan --names — 맨 이름은 옛 모듈을 참조하는 파일에서만 · 점 성분 경계
cat > "$T/spec.md" <<'EOF'
# 명세

## 슬라이스 0

이름: web.home.home.view.home_view._render_page → web.home.home.view.home_page._render_page
이름: web.home.home.view.home_view.redirect_home → web.home.home.view.home_nav.go_home

## 슬라이스 1

이름: 여기는 읽지 않는다
EOF
OUT=$(RA plan web/home --debt .dddjango-web/run/debt-g0.json --out "$A" --names "$T/spec.md"); E=$?
NAMES=$(cat "$A/plan-names.md" 2>/dev/null)
assert "D1 plan --names 실행(plan.md 무변 · 절 밖 줄 무시)" 0 "요약: plan --names 쌍 경로 0 · 이름 2" - "$E" "$OUT"
assert "D2 옛 모듈 import 줄 (나)" 0 '`web/chart/chart/view_model/chart_view_model.py:1`' - 0 "$NAMES"
assert "D3 옛 이름 호출 줄 (나)" 0 '`web/chart/chart/view_model/chart_view_model.py:6`' - 0 "$NAMES"
assert "D4 다른 영역이 스스로 정의한 같은 이름 helper 는 (나) 밖" 0 - "chart_view.py" 0 "$NAMES"
assert "D5 home_view2 import 줄은 점 성분 경계로 (나) 밖" 0 - "chart_view_model.py:2" 0 "$NAMES"
printf '## 슬라이스 0\n\n' > "$T/spec0.md"
OUT=$(RA plan web/home --debt .dddjango-web/run/debt-g0.json --out "$A" --names "$T/spec0.md"); E=$?
assert "D6 쌍 0 = exit 0 (나) 0" 0 "(나) 줄 0" - "$E" "$OUT"
printf '## 슬라이스 0\n이름: home.x → home.y\n' > "$T/specbad.md"
OUT=$(RA plan web/home --debt .dddjango-web/run/debt-g0.json --out "$A" --names "$T/specbad.md"); E=$?
assert "D7 이름: 형식 어긋남 = 실행 불능" 1 "web. 으로 시작하는 전체 점 경로" - "$E" "$OUT"

# ---------- R (R8d 리뷰 보강): 정적 단위 분류 고정(②-A)
OUT=$(RA plan web/static/js --debt .dddjango-web/run/debt-g0.json --out "$T/rj"); E=$?
assert "R1 정적 단위: <script src> 로드 줄 = 줄 편집 (가)" 0 '`web/home/home/view/home.html:3` — (가)' - "$E" "$(PSEC "$T/rj/plan.md" '줄 편집')"
assert "R1′ 정적 단위: 로드 전용 줄은 소비자 아님" 0 - 'home.html:3' 0 "$(PSEC "$T/rj/plan.md" '경계 교차 소비자')"
assert "R2 정적 단위: 비로드 참조 줄(<img>) = 소비자" 0 '`web/home/home/section/home_card.html:1`' - 0 "$(PSEC "$C/plan.md" '경계 교차 소비자')"

# ---------- 합성 플러그인 루트(판정 문장 고정)
PL="$T/plugin"
mkdir -p "$PL/commands" "$PL/agents" "$PL/skills/rules/references"
cat > "$PL/commands/dddjango-web.md" <<'EOF'
# coordinator

## 리팩토링 모드 (입구 `/dddjango-web:refactor`)

**적용 범위 규범**: 이 점검은 기존 코드 전체에 허용한다. 적용 한정 어구(닫힌 목록): «touched» · «이번 작업».

그 밖의 문단이다.

리뷰어가 같은 다발을 반복하는 것은 위반이 아니다.
EOF
cat > "$PL/skills/rules/references/final.md" <<'EOF'
# rules

## §1. 규칙

공용 헬퍼는 금지다.
마커 파일은 «직속 파일 금지»의 명시 예외다.
view 는 진입점뿐이다.
짧은 예외를 허용하지 않는다.
상태는 불변이다(예외: 폼 1종 허용).
공용 헬퍼는 금지이고 단일 화면 전속은 허용한다.
touched 파일의 이름은 짧아도 된다.
공용 헬퍼는 둘 수 있다.

## §2. 요건

section 은 dumb 해야 한다. 단 화면 state 를 받는 경우만 해당한다.

다른 문단의 요건 문구다.
EOF
R='skills/rules/references/final.md'
LOC='web/home/home/view/home_view.py:1'
{
  echo '| 행# | 규칙 | 반대 방향 규칙 | 파일:행 | 위반 요지 | 동작 불변 정리 가능 | 편집할 곳 | 같은 검사기 키 |'
  echo '|---|---|---|---|---|---|---|---|'
  echo "| 1 | $R §1 «공용 헬퍼는 금지다» | — | $LOC | a | 예 | — | — |"
  echo "| 2 | $R §1 «없는 문장» | — | $LOC | b | 예 | — | — |"
  echo "| 3 | $R §1 «공용 헬퍼는 금지다» | — | web/chart/chart/view/chart_view.py:1 | c | 예 | — | — |"
  echo "| 4 | 근거 없음(불편 #1) | — | $LOC | d | 예 | — | — |"
  echo "| 5 | $R §1 «상태는 불변이다» | — | $LOC | e | 예 | — | — |"
  echo "| 6 | $R §1 «공용 헬퍼는 금지이고» | — | $LOC | f | 예 | — | — |"
  echo "| 7 | $R §2 «section 은 dumb 해야 한다» | — | $LOC | g | 예 | — | — |"
  echo "| 8 | $R §1 «공용 헬퍼는 금지다» | $R §1 «공용 헬퍼는 둘 수 있다» | $LOC | h | 예 | — | — |"
  echo "| 9 | $R §1 «공용 헬퍼는 금지다» | — | web/home/urls.py:4 | i | 아니오 — 외부 동작 | — | — |"
  echo "| 10 | $R §1 «공용 헬퍼는 금지다» | — | $LOC | j | 아니오 — 경계 교차 | web/chart/chart/section/chart_panel.html:1 | — |"
  echo "| 11 | $R §1 «공용 헬퍼는 금지다» | — | $LOC | k | 아니오 — 경계 교차 | web/chart/chart/view_model/chart_view_model.py:1 | — |"
  echo "| 12 | $R §1 «공용 헬퍼는 금지다» | — | $LOC | l | 아니오 — web/ 밖 | config/settings.py:1 | — |"
  echo "| 13 | $R §1 «공용 헬퍼는 금지다» | — | $LOC | m | 아니오 — web/ 밖 | tests/web/test_home.py:1 | — |"
  echo "| 14 | $R §1 «공용 헬퍼는 금지다» | — | $LOC | n | 예 | — | WN8\|static/images/bad-name.png |"
} > "$A/screen-01.md"
printf '| 행# | 규칙 |\n|---|---|\n' > "$A/discipline-01.md"

# ---------- F: check — 인용 실재 · 위치 범위
OUT=$(RAP check "$A"); E=$?
assert "F1 check 인용 불일치 2(없는 인용 · 범위 밖 위치) = exit 2" 2 "통과 11 · 인용 불일치 2 · 규칙 근거 없는 불편 1" - "$E" "$OUT"
CHK=$(cat "$A/check.md")
assert "F2 범위 밖 위치 사유" 0 "범위 밖: web/chart/chart/view/chart_view.py:1" - 0 "$CHK"
printf '| 행# | 규칙 |\n|---|---|\n| R4 | 규칙 | %s | 요지 |\n' "$LOC" > "$A/discipline-01.md"
OUT=$(RAP check "$A"); E=$?
assert "F3 첫 칸 비숫자 짧은 행(위치 토큰 있음) = 칸 부족 인용 불일치(버리지 않음)" 2 "인용 불일치 3" - "$E" "$OUT"
assert "F3b check.md 에 그 행이 칸 부족으로" 0 "칸 부족" - 0 "$(cat "$A/check.md")"
printf '| 행# | 규칙 |\n|---|---|\n' > "$A/discipline-01.md"

# ---------- G: check-verdict — 빼는 출구 검사
verdict() { { echo '| M | 원 행 | 판정 | 근거 | 파일:행 |'; echo '|---|---|---|---|---|'; cat; } > "$A/verdict.md"; }
V1="| M1 | screen-01#1 | 제외 | $R §1 «마커 파일은 «직속 파일 금지»의 명시 예외다» | $LOC |
| M2 | screen-01#5 | 제외 | $R §1 «폼 1종 허용» | $LOC |
| M3 | screen-01#7 | 오탐 | «단 화면 state 를 받는 경우만 해당한다» | $LOC |
| M4 | screen-01#8 | 사용자 판단 | — | $LOC |
| M5 | screen-01#9 | 별도 요청 | 외부 동작 — urls path | $LOC |
| M6 | screen-01#10 | 별도 요청 | 경계 교차 — chart 줄 | $LOC |
| M7 | screen-01#12 | 별도 요청 | web/ 밖 — settings | $LOC |
| M8 | screen-01#14 | 병합 → WN8\|static/images/bad-name.png | — | $LOC |
| M9 | screen-01#6 | 채택 | — | $LOC |
| M10 | screen-01#11 | 채택 | — | $LOC |
| M11 | screen-01#13 | 채택 | — | $LOC |"
echo "$V1" | verdict
OUT=$(RAP check-verdict "$A"); E=$?
assert "G1 양성 출구 전부 통과 exit 0" 0 "red 0" - "$E" "$OUT"
assert "G2 계수" 0 "채택 3 · 사용자 판단 1 · 별도 요청 3 · 제외 2 · 오탐 1 · 병합→검사기 1" - 0 "$OUT"
LISTS=$(cat "$A/g0-lists.md")
assert "G3 G0 목록 제외 행은 위반 인용 ↔ 제외 인용" 0 "↔ 제외 $R §1 «마커 파일은" - 0 "$LISTS"
rm -f "$A/verdict-log.md"
cv() { echo "$1" | verdict; rm -f "$A/verdict-log.md"; RAP check-verdict "$A"; }
OUT=$(cv "$(echo "$V1" | sed 's/«마커 파일은 «직속 파일 금지»의 명시 예외다»/«view 는 진입점뿐이다»/')"); E=$?
assert "G4 긍정 술어 없는 문장 근거 제외 red" 2 "② 인용이 든 문장에 유효한 긍정 술어가 없다" - "$E" "$OUT"
OUT=$(cv "$(echo "$V1" | sed 's/«마커 파일은 «직속 파일 금지»의 명시 예외다»/«짧은 예외를 허용하지 않는다»/')"); E=$?
assert "G5 부정형 문장 근거 제외 red" 2 "② 인용이 든 문장에 유효한 긍정 술어가 없다" - "$E" "$OUT"
OUT=$(cv "$(echo "$V1" | sed 's/| M9 | screen-01#6 | 채택 | — |/| M9 | screen-01#6 | 제외 | skills\/rules\/references\/final.md §1 «단일 화면 전속은 허용한다» |/')"); E=$?
assert "G6 제외 인용과 위반 인용이 같은 문장(괄호 밖) red" 2 "⑤ 제외 인용과 위반 인용이 같은 문장이다" - "$E" "$OUT"
OUT=$(cv "$(echo "$V1" | sed 's/«마커 파일은 «직속 파일 금지»의 명시 예외다»/«touched 파일의 이름은 짧아도 된다»/')"); E=$?
assert "G7 적용 한정 어구 문장 근거 제외 red" 2 "③ 인용이 든 문장에 적용 한정 어구 «touched»" - "$E" "$OUT"
OUT=$(cv "$(echo "$V1" | sed 's#'"$R"' §1 «마커 파일은 «직속 파일 금지»의 명시 예외다»#commands/dddjango-web.md §리팩토링 모드 (입구 `/dddjango-web:refactor`) «이 점검은 기존 코드 전체에 허용한다»#')"); E=$?
assert "G8 적용 범위 규범 문단 자신 인용 red" 2 "③ 인용이 적용 범위 규범 문단 자신이다" - "$E" "$OUT"
OUT=$(cv "$(echo "$V1" | sed 's/«단 화면 state 를 받는 경우만 해당한다»/«다른 문단의 요건 문구다»/')"); E=$?
assert "G9 같은 절 다른 문단 오탐 red" 2 "오탐 인용이 위반으로 인용된 그 문단에 없다" - "$E" "$OUT"
OUT=$(cv "$(echo "$V1" | sed 's/| M4 | screen-01#8 | 사용자 판단 |/| M4 | screen-01#1 | 사용자 판단 |/; s/| M1 | screen-01#1 | 제외 |/| M1 | screen-01#8 | 제외 |/')"); E=$?
assert "G10 반대 방향 규칙 없는 사용자 판단 red" 2 "리뷰어 행에 반대 방향 규칙이 없다" - "$E" "$OUT"
OUT=$(cv "$(echo "$V1" | sed 's/| M11 | screen-01#13 | 채택 | — |/| M11 | screen-01#13 | 별도 요청 | web\/ 밖 — tests |/; s/| M10 | screen-01#11 | 채택 | — |/| M10 | screen-01#11 | 별도 요청 | 경계 교차 — import |/')"); E=$?
assert "G11 테스트 파일 web/ 밖 · 항목 모듈 import 줄 경계 교차 → 채택 재분류(exit 0)" 0 "재분류: M10 별도 요청 → 채택" - "$E" "$OUT"
assert "G12 테스트 파일 web/ 밖 → 채택 재분류" 0 "재분류: M11 별도 요청 → 채택" - "$E" "$OUT"
OUT=$(cv "$(echo "$V1" | sed 's/| M8 | screen-01#14 | 병합 → [^|]*|static\/images\/bad-name.png |/| M8 | screen-01#14 | 병합 → M1 |/')"); E=$?
assert "G13 채택 아닌 대상으로 M→M 병합 red" 2 "병합 대상 M1 이 채택 항목이 아니다" - "$E" "$OUT"
OUT=$(cv "$(echo "$V1" | sed 's/| M9 | screen-01#6 | 채택 | — |/| M9 | screen-01#6 | 별도 요청 | 외부 동작 |/')"); E=$?
assert "G14 «아니오» 없는 별도 요청 → 채택 재분류" 0 "재분류: M9 별도 요청 → 채택(리뷰어 «동작 불변 정리 가능 = 아니오» 없음)" - "$E" "$OUT"
OUT=$(cv "$(echo "$V1" | sed 's/| M9 | screen-01#6 | 채택 | — |/| M9 | screen-01#6 | 제외 | skills\/rules\/references\/final.md §1 «금지이고 단일 화면 전속은 허용한다» |/')"); E=$?
assert "G17 제외 인용이 위반 인용 구간과 겹침 red" 2 "④ 제외 인용이 위반 인용 구간과 겹친다" - "$E" "$OUT"
OUT=$(cv "$(echo "$V1" | sed 's#'"$R"' §1 «마커 파일은 «직속 파일 금지»의 명시 예외다»#commands/dddjango-web.md §리팩토링 모드 (입구 `/dddjango-web:refactor`) «리뷰어가 같은 다발을 반복하는 것은 위반이 아니다»#')"); E=$?
assert "G18 Coordinator 절차 문장 근거 제외 red(규칙 문서 아님)" 2 "① 근거 문서가 규칙 문서(skills/·agents/)가 아니다" - "$E" "$OUT"
OUT=$(cv "$(echo "$V1" | sed 's/«단 화면 state 를 받는 경우만 해당한다»/«section 은 dumb 해야 한다»/')"); E=$?
assert "G19 오탐 근거 = 위반 인용 문구 자체 red" 2 "오탐 인용이 위반 인용 구간과 겹친다" - "$E" "$OUT"
# 대리 출처 축소 · --final
echo "$V1" | verdict; rm -f "$A/verdict-log.md"; RAP check-verdict "$A" >/dev/null
echo "$V1" | sed 's/| M9 | screen-01#6 | 채택 | — |/| M9 | screen-01#6 | 오탐 | «단 화면 state 를 받는 경우만 해당한다» |/' | verdict
printf '출처 = 발주자 대리 답\n판정 근거 오류 지적\n' > "$T/fb.md"
OUT=$(RAP check-verdict "$A" --feedback "$T/fb.md"); E=$?
assert "G15 대리 출처의 채택 축소 red" 2 "대리 출처의 채택 축소(채택 → 오탐)" - "$E" "$OUT"
OUT=$(RAP check-verdict "$A" --feedback "$T/fb.md" --final); E=$?
assert "G16 --final 은 남은 red 를 채택으로 기록 exit 0" 0 "red 0" - "$E" "$OUT"
assert "G16b --final 확정 표 = verdict-final.md(채택으로 되돌린 M9)" 0 "| M9 | screen-01#6 | 채택 |" - 0 "$(cat "$A/verdict-final.md")"
echo "$V1" | grep -v '| M11 |' | verdict; rm -f "$A/verdict-log.md" "$A/verdict-final.md"
OUT=$(RAP check-verdict "$A"); E=$?
assert "G20 통과 행 판정 누락 red · verdict-final.md 없음" 2 - - "$E" "$OUT"
assert "G20b red 판에는 확정 표를 쓰지 않는다" 0 - - 0 "$( [ -f "$A/verdict-final.md" ] && echo EXISTS )"
OUT=$(RAP check-verdict "$A" --final); E=$?
assert "G21 --final 이 판정 없는 통과 행을 새 번호로 채택" 0 "판정 없는 통과 행 screen-01#13 → 채택(새 번호)" - "$E" "$OUT"
assert "G21b 새 번호 M11 이 verdict-final.md 에(verdict.md 에는 없음)" 0 "| M11 | screen-01#13 | 채택 |" - 0 "$(cat "$A/verdict-final.md")"

# ---------- H: 별도 요청 기계 근거 — API 계약 리터럴 결속 · 외부 동작 render 상수(함수 직접)
OUT=$(cd "$P" && python3 - "$SCRIPTS" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import refactor_audit as ra
p = Path('.')
loc = [('web/client/users/response/user_response.py', 3, 3)]
print('attr=key', ra._api_contract(p, loc, '근거 "birth_date"'))
loc = [('web/client/users/response/user_response.py', 4, 4)]
print('key literal', ra._api_contract(p, loc, '근거 "user_name"'))
print('no literal', ra._api_contract(p, loc, '근거 이름 정리'))
Path('web/home/home/view/section_view.py').write_text(
    '_SECTION = "home/home/section/home_card.html"\n\n\ndef card(request):\n    return render(\n        request,\n        _SECTION,\n    )\n')
print('render const', ra._external_behavior(p, [('web/home/home/view/section_view.py', 6, 6)]))
print('urls path', ra._external_behavior(p, [('web/home/urls.py', 4, 4)]))
print('plain line', ra._external_behavior(p, [('web/home/home/view/home_view.py', 1, 1)]))
PY
)
assert "H1 속성 이름 = 키 행은 API 계약 근거 불성립" 0 "attr=key False" - 0 "$OUT"
assert "H2 키 리터럴 + 근거 칸 리터럴 = 성립" 0 "key literal True" - 0 "$OUT"
assert "H3 근거 칸에 리터럴 없음 = 불성립" 0 "no literal False" - 0 "$OUT"
assert "H4 모듈 상수 section 템플릿 render 여러 줄 호출 = 외부 동작" 0 "render const True" - 0 "$OUT"
assert "H5 urls path( 구간 = 외부 동작" 0 "urls path True" - 0 "$OUT"
assert "H6 일반 줄 = 불성립" 0 "plain line False" - 0 "$OUT"
printf '<img src="{%% static %s %%}">\n' "'images/k_card.png'" > "$P/web/home/home/section/카드.html"
OUT=$(cd "$P" && python3 - "$SCRIPTS" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from src.debt import reference_lines
print(reference_lines(Path('.'), ['images/k_card.png']))
PY
)
assert "H7 비 ASCII 경로 참조 줄 = 인용 없는 web/ 경로" 0 "web/home/home/section/카드.html" '\\' 0 "$OUT"
rm "$P/web/home/home/section/카드.html"

# ---------- I: residual — M 행 접기 · 결정적 바닥 · 리뷰어 확인 · 근거 없는 해소
echo "$V1" | verdict; rm -f "$A/verdict-log.md"; RAP check-verdict "$A" >/dev/null
F="$P/.dddjango-web/run"
printf '{"git_snapshot": "%s", "mode": "refactor"}\n' "$BASE" > "$F/build-state.json"
cat > "$F/refactor-scope.md" <<EOF
## G0 $(date '+%Y-%m-%d %H:%M')
ⓐ 키: -
요구 키: -
의미 ⓐ 키: M9 M10
의미 audit: 20260927-120000
EOF
OUT=$(RA residual "$F"); E=$?
assert "I1 무변 파일 항목 = 결정적 잔존 exit 2" 2 "M_m=2(결정적 잔존 2)" - "$E" "$OUT"
printf 'def _render_page(request):\n    return 1\n' > "$P/web/home/home/view/home_view.py"
commit_all "$P" fix >/dev/null
OUT=$(RA residual "$F"); E=$?
assert "I2 바뀐 파일 항목 = 리뷰어 확인 묶음(M_m 미정 exit 0)" 0 "리뷰어 확인 대상 2(screen) · M_m 미정" - "$E" "$OUT"
STAMP=$(sed -n 's/.*--finalize \([^ ]*\) .*/\1/p' <<<"$OUT")
BUNDLE=$(cat "$F/residual/$STAMP/review-screen.md" 2>/dev/null)
assert "I2b 묶음 머리 = 근거 칸 판형(\` — \` 앞 위치만 · 줄임 없이) + web 예시" 0 "\` — \` 앞에는 저장소 루트 기준 새 위치만" - 0 "$BUNDLE"
assert "I2c 묶음 머리 web 예시" 0 "예: \`M3 | 해소 | web/<영역>/<화면>/view_model/<화면>_view_model.py:15-16 — " - 0 "$BUNDLE"
# 같은 시각 재확정은 판형 아님·답 없음 행만 다시 본다(동결) — 사례마다 시각을 새로 연다(앞 시각 폴더를 지워 이월 없이).
OPEN() { rm -rf "$F/residual"; local s; s=$(RA residual "$F" | sed -n 's/.*--finalize \([^ ]*\) .*/\1/p'); echo "${s:-(열리지 않음)}"; }
FIN() { # FIN <시각> <M10 결과 행> — M9 는 판형대로 해소 · result-screen.md 를 쓰고 그 시각으로 확정(+ result.md)
  [ "$1" = "(열리지 않음)" ] && { echo "시각이 열리지 않았다"; return 9; }
  mkdir -p "$F/residual/$1"
  printf '| M | 판정 | 근거 |\n|---|---|---|\n| M9 | 해소 | web/home/home/view/home_view.py:2 |\n%s\n' "$2" > "$F/residual/$1/result-screen.md"
  RA residual "$F" --finalize "$1"; local e=$?; cat "$F/residual/$1/result.md" 2>/dev/null; return $e; }
H='web/home/home/view/home_view.py'
S=$(OPEN)
OUT=$(FIN "$S" '| M10 | 해소 | 이유만 적음 |'); E=$?
assert "I3 머리가 위치가 아닌 해소 = 근거 판형 아님(리뷰어 잔존 아님) exit 2" 2 "M_m=1(결정적 잔존 0 · 리뷰어 잔존 0 · 근거 판형 아님 1 · 판단 불가 0)" - "$E" "$OUT"
assert "I3′ \`요약:\` 뒤 재기재 안내(렌즈·불량 토큰 · 같은 시각)" 2 "  근거 판형 아님: M10(screen: \`이유만\`) — 그 행만 같은 렌즈 리뷰어에게" - "$E" "$OUT"
assert "I3″ 재기재 안내의 같은 시각 --finalize" 2 "--finalize $S 한 번 더" - "$E" "$OUT"
OUT=$(FIN "$S" "| M10 | 해소 | $H:2 — 이유를 고쳐 적음 |"); E=$?
assert "I3‴ 같은 시각에 판형대로 고쳐 재확정 = 해소 exit 0" 0 "M_m=0" - "$E" "$OUT"
S=$(OPEN); OUT=$(FIN "$S" "| M10 | 해소 | $H:2의 정의 |"); E=$?
assert "I3a 머리에 조사(WR2 M11 모양) = 판형 아님" 2 "근거 판형 아님 1" - "$E" "$OUT"
S=$(OPEN); OUT=$(FIN "$S" "| M10 | 해소 | $H:2 — $H:1의 정의 한 곳 |"); E=$?
assert "I3b 조사가 꼬리 = 해소" 0 "M_m=0" - "$E" "$OUT"
S=$(OPEN); OUT=$(FIN "$S" "| M10 | 해소 | $H:1-2 — 남은 두 return(:46 · :49)은 표기(design-spec.md:103에) |"); E=$?
assert "I3c 괄호·설계 근거가 꼬리(WR2 M10 모양) = 해소" 0 "M_m=0" - "$E" "$OUT"
S=$(OPEN); OUT=$(FIN "$S" "| M10 | 해소 | home/home/view/home_view.py:2 — 정의 한 곳 |"); E=$?
assert "I3d web/ 없는 머리 = 해소(_repo_path 유지)" 0 "M_m=0" - "$E" "$OUT"
S=$(OPEN); OUT=$(FIN "$S" "| M10 | 해소 | — 남은 $H:2 는 제외 범주 |"); E=$?
assert "I3e 꼬리에만 위치 = 판형 아님(해소 아님)" 2 "근거 판형 아님 1" "| M10 | 해소 |" "$E" "$OUT"
S=$(OPEN); OUT=$(FIN "$S" "| M10 | 해소 | web/base/base.html:1 — 로드 줄 |"); E=$?
assert "I3f 무변 파일 머리 = 잔존(판형 아님 아님)" 2 "리뷰어 잔존 1 · 근거 판형 아님 0" - "$E" "$OUT"
S=$(OPEN); OUT=$(FIN "$S" "| M10 | 해소 | .dddjango-web/run/refactor-scope.md:1 — 명세에 적었다 |"); E=$?
assert "I3h 산출물 폴더 파일 머리 = 잔존(해소 아님)" 2 "리뷰어 잔존 1" "| M10 | 해소 |" "$E" "$OUT"
S=$(OPEN); OUT=$(FIN "$S" "| M10 | 해소 | $P/$H:2 — 고침 |"); E=$?
assert "I3i 절대 경로 머리(실재 · 바뀐 파일) = 판형 아님" 2 "근거 판형 아님 1" - "$E" "$OUT"
S=$(OPEN); OUT=$(FIN "$S" "| M10 | 해소 | $H:2 – 고침 |"); E=$?
assert "I3j 대시 변형(en dash) = 판형 아님" 2 "근거 판형 아님 1" - "$E" "$OUT"
S=$(OPEN); OUT=$(FIN "$S" "| M10 | 해소 안 됨 | $H:2 — 남아 있다 |"); E=$?
assert "I3k 판정 칸 «해소 안 됨» = 판단 불가(접두어로 해소 아님)" 2 "판단 불가 1" - "$E" "$OUT"
S=$(OPEN); OUT=$(FIN "$S" "| M10 | 해소 | $H:2 · web/base/base.html:1 — 둘 다 고침 |"); E=$?
assert "I3n 머리에 바뀐 파일·무변 파일 섞임 = 잔존" 2 "리뷰어 잔존 1 · 근거 판형 아님 0" - "$E" "$OUT"
S=$(OPEN); OUT=$(FIN "$S" $'| M10 | 잔존 | 남았다 |\n| M10 | 해소 | 고쳤다 |'); E=$?
assert "I3o 같은 M 두 행 잔존 + 판형 아님 해소 = 리뷰어 잔존 1 · 판형 아님 0" 2 "리뷰어 잔존 1 · 근거 판형 아님 0" - "$E" "$OUT"
S=$(OPEN); OUT=$(FIN "$S" "| M10 | 해소 | $H:999 — 고침 |"); E=$?
assert "I3p 행 범위 밖 머리 = 판형 아님" 2 "근거 판형 아님 1" - "$E" "$OUT"
S=$(OPEN); FIN "$S" "| M10 | 해소 | $H:2 — 고침 |" >/dev/null
OUT=$(FIN "$S" '| M10 | 잔존 | 다시 보니 남음 |'); E=$?
assert "I3r 같은 시각 재확정에서 앞 판 해소를 잔존으로 고쳐 씀 = 잔존(나빠지는 쪽은 막지 않는다)" 2 "리뷰어 잔존 1" "| M10 | 해소 |" "$E" "$OUT"
S=$(OPEN); FIN "$S" "| M10 | 해소 | $H:2 — 고침 |" >/dev/null
OUT=$(FIN "$S" ''); E=$?
assert "I3s 짝 — 같은 시각 재확정에 M10 행 없음 = 앞 판 해소 유지" 0 "M_m=0" - "$E" "$OUT"
S=$(OPEN); FIN "$S" "| M10 | 해소 | $H:2 — 고침 |" >/dev/null
OUT=$(FIN "$S" '| M10 | 판단 불가 | 다시 보니 모름 |'); E=$?
assert "I3x 앞 판 해소 → 이번 판단 불가 = 판단 불가(exit 2)" 2 "판단 불가 1" "| M10 | 해소 |" "$E" "$OUT"
S=$(OPEN); FIN "$S" "| M10 | 해소 | $H:2 — 고침 |" >/dev/null
OUT=$(FIN "$S" '| M10 | 해소 | 고쳤다 |'); E=$?
assert "I3y 앞 판 해소 → 이번 판형 아님 행 = 판형 아님(exit 2)" 2 "근거 판형 아님 1" "| M10 | 해소 |" "$E" "$OUT"
S=$(OPEN); FIN "$S" '| M10 | 판단 불가 | 모름 |' >/dev/null
OUT=$(FIN "$S" "| M10 | 해소 | $H:2 — 고침 |"); E=$?
assert "I3z 앞 판 판단 불가 → 이번 해소 = 판단 불가 유지" 2 "판단 불가 1" "| M10 | 해소 |" "$E" "$OUT"
S=$(OPEN); FIN "$S" '| M10 | 잔존 | 남음 |' >/dev/null
OUT=$(FIN "$S" '| M10 | 해소 | 고쳤다 |'); E=$?
assert "I3z′ 앞 판 잔존 → 이번 판형 아님 행 = 잔존 유지(판형 아님 경유 우회 봉쇄)" 2 "리뷰어 잔존 1 · 근거 판형 아님 0" - "$E" "$OUT"
S=$(OPEN); FIN "$S" '| M10 | 해소 | 고쳤다 |' >/dev/null; FIN "$S" '' >/dev/null
OUT=$(FIN "$S" '| M10 | 해소 | 고쳤다 |'); E=$?
assert "I3t 판형 아님 → 행 삭제(답 없음) → 판형 아님 = 잔존(근거 판형 아님 반복)" 2 "| M10 | 잔존(근거 판형 아님 반복) |" - "$E" "$OUT"
mkdir -p "$P/.dddjango"; printf 'a\nb\n' > "$P/.dddjango/note.md"
S=$(OPEN); OUT=$(FIN "$S" '| M10 | 해소 | .dddjango/note.md:1 — 적었다 |'); E=$?
assert "I3u core 산출물 폴더(.dddjango/…) 머리 = 잔존(해소 아님)" 2 "리뷰어 잔존 1" "| M10 | 해소 |" "$E" "$OUT"
rm -rf "$P/.dddjango"
S=$(OPEN); [ -d "$F/residual/$S" ] && printf '{"stamp": "%s", "solved": {}, "states": ["M10"]}\n' "$S" > "$F/residual/$S/result.json"
OUT=$(FIN "$S" "| M10 | 해소 | $H:2 — 고침 |"); E=$?
assert "I3v result.json states 가 dict 아님 = 실행 불능(exit 1)" 1 "실행 불능" - "$E" "$OUT"
S=$(OPEN); FIN "$S" "| M10 | 해소 | $H:2 — 고침 |" >/dev/null
cp "$P/$H" "$T/hv.bak"; printf '# 재확정 사이 편집\n' >> "$P/$H"
FIN "$S" "| M10 | 해소 | $H:2 — 고침 |" >/dev/null
OUT=$(RA residual "$F"); E=$?
assert "I3w 1차 해소 → 편집 → 같은 시각 2차(앞 판 지문 유지) → 새 시각은 이월 없이 다시 묶는다" 0 "리뷰어 확인 대상 2(screen) · M_m 미정" "해소 유지" "$E" "$OUT"
cp "$T/hv.bak" "$P/$H"
cp "$A/verdict-final.md" "$T/vf.bak"; cp "$A/discipline-01.md" "$T/d01.bak"
printf '| 행# | 규칙 | 반대 방향 규칙 | 파일:행 | 위반 요지 | 동작 불변 정리 가능 | 편집할 곳 | 같은 검사기 키 |\n|---|---|---|---|---|---|---|---|\n| 1 | %s §1 «공용 헬퍼는 금지다» | — | %s | z | 예 | — | — |\n' "$R" "$LOC" > "$A/discipline-01.md"
sed -i.bak 's/^| M10 | screen-01#11 |/| M10 | screen-01#11 · discipline-01#1 |/' "$A/verdict-final.md"; rm -f "$A/verdict-final.md.bak"
S=$(OPEN); OUT=$(FIN "$S" "| M10 | 해소 | $H:2 — 정의 한 곳 |"); E=$?
assert "I3l 렌즈 완전성 — 두 렌즈 항목에 screen 만 해소 = 판단 불가(discipline 답 없음)" 2 "M_m=1(결정적 잔존 0 · 리뷰어 잔존 0 · 근거 판형 아님 0 · 판단 불가 1)" - "$E" "$OUT"
DISC() { [ -d "$F/residual/$1" ] && printf '| M | 판정 | 근거 |\n|---|---|---|\n%s\n' "$2" > "$F/residual/$1/result-discipline.md"; }
S=$(OPEN); DISC "$S" '| M10 | 해소 | 고쳤다 |'
OUT=$(FIN "$S" '| M10 | 잔존(일부) | 남음 |'); E=$?
assert "I3q screen «잔존(일부)» + discipline 판형 아님 = 잔존(판단 불가·판형 아님 아님)" 2 "리뷰어 잔존 1 · 근거 판형 아님 0 · 판단 불가 0" - "$E" "$OUT"
DISC "$S" "| M10 | 해소 | $H:2 — 고침 |"
OUT=$(FIN "$S" "| M10 | 해소 | $H:2 — 고침 |"); E=$?
assert "I3q′ 같은 시각 2차에 두 렌즈 해소로 고쳐도 잔존 유지(동결)" 2 "리뷰어 잔존 1" - "$E" "$OUT"
S=$(OPEN); DISC "$S" "| M10 | 해소 | $H:2 — 고침 |"; FIN "$S" '| M10 | 잔존 | 남음 |' >/dev/null
OUT=$(FIN "$S" ''); E=$?
assert "I3q″ 잔존 → screen 행 삭제(답 없음) = 잔존 유지" 2 "리뷰어 잔존 1 · 근거 판형 아님 0 · 판단 불가 0" - "$E" "$OUT"
DISC "$S" "| M10 | 해소 | $H:2 — 고침 |"
OUT=$(FIN "$S" "| M10 | 해소 | $H:2 — 고침 |"); E=$?
assert "I3q‴ 이어서 두 렌즈 해소 = 잔존 유지(답 없음 경유 이탈 없음)" 2 "리뷰어 잔존 1" - "$E" "$OUT"
cp "$T/vf.bak" "$A/verdict-final.md"; cp "$T/d01.bak" "$A/discipline-01.md"
S=$(OPEN)
OUT=$(FIN "$S" "| M10 | 해소 | — 남은 $H:2 는 제외 범주 |"); E=$?
OUT=$(FIN "$S" "| M10 | 해소 | — 남은 $H:2 는 제외 범주 |"); E=$?
assert "I3g 같은 시각 재확정에도 판형 아님 = 잔존(근거 판형 아님 반복)" 2 "| M10 | 잔존(근거 판형 아님 반복) |" - "$E" "$OUT"
OUT=$(FIN "$S" "| M10 | 해소 | $H:2 — 고침 |"); E=$?
assert "I3g′ 세 번째 재확정(판형대로)도 잔존 유지(동결)" 2 "리뷰어 잔존 1" - "$E" "$OUT"
S=$(OPEN); FIN "$S" '| M10 | 잔존 | 남았다 |' >/dev/null
OUT=$(FIN "$S" "| M10 | 해소 | $H:2 — 다시 보니 해소 |"); E=$?
assert "I3m 같은 시각 재확정으로 잔존을 해소로 뒤집기 = 잔존 유지(동결 · 끝 판 M9 해소)" 2 "리뷰어 잔존 1" - "$E" "$OUT"
cat >> "$F/refactor-scope.md" <<EOF

## ⓐ 재상정 $(date '+%Y-%m-%d %H:%M')
재상정 키: -
의미 재상정 키: M10
EOF
OUT=$(RA residual "$F"); E=$?
assert "I4 재상정 뺀 M10 은 판정 밖 · 확정 해소 M9 는 파일 무변이면 이월" 0 "해소 유지 1 · 리뷰어 확인 대상 0" "M10" "$E" "$OUT"
sed -i.bak '/의미 audit/d' "$F/refactor-scope.md"; rm -f "$F/refactor-scope.md.bak"
OUT=$(RA residual "$F"); E=$?
assert "I5 의미 audit 행 없음 = 실행 불능" 1 "의미 audit" - "$E" "$OUT"
python3 - "$F/debt-g0.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d['mode'] = 'feature'; json.dump(d, open(sys.argv[1], 'w'))
PY
OUT=$(RA residual "$F"); E=$?
assert "I6 mode feature 폴더 = 실행 불능" 1 "mode 가 refactor 가 아니다" - "$E" "$OUT"

# ---------- K: 재사용 폴더의 새 점검 — 앞 실행 해소를 M 번호로 잇지 않는다 · --final 새 번호도 residual 이 읽는다
python3 - "$F/debt-g0.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d['mode'] = 'refactor'; json.dump(d, open(sys.argv[1], 'w'))
PY
A2="$F/audit/20260927-130000"
mkdir -p "$A2"; cp "$A/plan.md" "$A/screen-01.md" "$A/discipline-01.md" "$A2/"
echo "$V1" | verdict; cp "$A/verdict.md" "$A2/verdict.md"; RAP check-verdict "$A2" >/dev/null
HEAD2=$(git -C "$P" rev-parse HEAD)
printf '{"git_snapshot": "%s", "mode": "refactor"}\n' "$HEAD2" > "$F/build-state.json"
cat > "$F/refactor-scope.md" <<EOF
## G0 $(date '+%Y-%m-%d %H:%M')
ⓐ 키: -
요구 키: -
의미 ⓐ 키: M9
의미 audit: 20260927-130000
EOF
OUT=$(RA residual "$F"); E=$?
assert "K1 새 점검의 M9(파일 무변) = 결정적 잔존 — 앞 실행 해소 이월 없음" 2 "M_m=1(결정적 잔존 1)" "해소 유지" "$E" "$OUT"
echo "$V1" | grep -v '| M11 |' | verdict; cp "$A/verdict.md" "$A2/verdict.md"; rm -f "$A2/verdict-log.md"
RAP check-verdict "$A2" >/dev/null; RAP check-verdict "$A2" --final >/dev/null
sed -i.bak 's/^의미 ⓐ 키: M9$/의미 ⓐ 키: M11/' "$F/refactor-scope.md"; rm -f "$F/refactor-scope.md.bak"
printf '{"git_snapshot": "%s", "mode": "refactor"}\n' "$BASE" > "$F/build-state.json"
OUT=$(RA residual "$F"); E=$?
assert "K2 --final 새 번호 M11 을 residual 이 verdict-final.md 에서 읽음" 0 "리뷰어 확인 대상 1" "실행 불능" "$E" "$OUT"
rm -f "$A2/verdict-final.md"
OUT=$(RA residual "$F"); E=$?
assert "K3 확정 표 없음 = 실행 불능" 1 "verdict-final.md" - "$E" "$OUT"
echo "$V1" | verdict; cp "$A/verdict.md" "$A2/verdict.md"; rm -f "$A2/verdict-log.md"; RAP check-verdict "$A2" >/dev/null
cat > "$F/refactor-scope.md" <<EOF
## G0 2026-09-27 13:00
ⓐ 키: -
요구 키: -
의미 ⓐ 키: M9 M10
의미 audit: 20260927-130000

## ⓐ 재상정 2026-09-27 13:10
재상정 키: -
의미 재상정 키: M10

## G0 재승인 2026-09-27 13:20
ⓐ 키: -
요구 키: -
의미 ⓐ 키: M10
EOF
OUT=$(RA residual "$F"); E=$?
assert "K4 재상정 뒤 재승인이 다시 적은 M10 은 되살아난다" 0 "리뷰어 확인 대상 2" - "$E" "$OUT"
sed -i.bak 's/^의미 ⓐ 키: M9 M10$/의미 ⓐ 키: C1/' "$F/refactor-scope.md"; rm -f "$F/refactor-scope.md.bak"
OUT=$(RA residual "$F"); E=$?
assert "K5 의미 ⓐ 키 값 형식 어긋남(C1) = 실행 불능" 1 "실행 불능" - "$E" "$OUT"

# ---------- L: WN6 «대응 미완»(생성)은 개명·이동 교정이 아니다 — 참조 치환 줄에 올리지 않는다(접두 불일치 대조 짝)
Q="$T/wn6"
mkdir -p "$Q/web/home/home/view_model" "$Q/web/chart/chart/view"
: > "$Q/web/__init__.py"
printf 'def go():\n    return 1\n' > "$Q/web/home/home/view_model/home_view_model.py"
printf 'from web.home.home.view_model.home_view_model import go\n' > "$Q/web/chart/chart/view/chart_view.py"
git -C "$Q" init -q; commit_all "$Q" base >/dev/null
wn6_plan() {
  rm -rf "$Q/.dddjango-web"; mkdir -p "$Q/.dddjango-web/r"
  python3 "$SCRIPTS/backstop.py" "$Q" --debt-scan --refactor --json "$Q/.dddjango-web/r/debt-g0.json" >/dev/null
  python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print([f['message'][:60] for f in d['findings'] if f['check']=='WN6'])" "$Q/.dddjango-web/r/debt-g0.json"
  (cd "$Q" && python3 "$SCRIPTS/refactor_audit.py" plan web/home --debt .dddjango-web/r/debt-g0.json --out "$Q/.dddjango-web/r/audit/x" 2>&1)
}
OUT=$(wn6_plan); E=$?
assert "L1 WN6 대응 미완 키의 파일 참조 줄은 참조 치환 줄이 아니다" 0 "참조 치환 줄 0" "소속 화면 개념" "$E" "$OUT"
assert "L1b 그 WN6 은 대응 미완" 0 "대응 미완" - 0 "$OUT"
git -C "$Q" mv web/home/home/view_model/home_view_model.py web/home/home/view_model/card_view_model.py
printf 'from web.home.home.view_model.card_view_model import go\n' > "$Q/web/chart/chart/view/chart_view.py"
commit_all "$Q" card >/dev/null
OUT=$(wn6_plan); E=$?
assert "L2 대조: WN6 접두 불일치(개명 교정) 키의 참조 줄 = 참조 치환 줄 1" 0 "참조 치환 줄 1" - "$E" "$OUT"

# ---------- M: standing — 상시 답 인식(core 와 같은 블록) · --gate ① 출처 ② 처분 ③ 항목·범주·위치 ④ 자리 ⑤ 키 행 · 대체 · 재사용 폴더
SP="$T/standing"
mkdir -p "$SP/web/home/view" "$SP/tests/web"
printf 'a\nb\nc\nd\ne\n' > "$SP/web/home/view/home_view.py"
printf 'x\ny\nz\n' > "$SP/tests/web/test_home.py"
git -C "$SP" init -q; commit_all "$SP" base >/dev/null
SR() { (cd "$SP" && python3 "$SCRIPTS/refactor_audit.py" standing "$@" 2>&1); }
OUT=$(SR); E=$?
assert "M1 파일 없음 = 상시 답 없음 · 출처 값 없음" 0 "요약: standing 없음 — 적용 0" "상시 답 출처" "$E" "$OUT"
mkdir -p "$SP/.dddjango"
printf '# 상시 답\n\n«동작 변경이나 테스트 수정이 필요해 이번에 못 끝내는 항목은 별도 요청으로.»\n' > "$SP/.dddjango/standing-answer.md"
OUT=$(SR); E=$?
assert "M2a 미추적 = 인식 안 함 + 기대 문장" 0 "기대 문장: 동작 변경이나 테스트 수정이" "상시 답 출처" "$E" "$OUT"
assert "M2a′ 사유 미추적" 0 "인식 안 함(미추적) — 적용 0" - "$E" "$OUT"
C1=$(commit_all "$SP" standing); C12=${C1:0:12}
OUT=$(SR); E=$?
assert "M2b 커밋본 = 인식 · 출처 값(행·커밋 12자)" 0 "상시 답 출처: 상시 답 .dddjango/standing-answer.md:3@$C12" - "$E" "$OUT"
printf '더함\n' >> "$SP/.dddjango/standing-answer.md"
OUT=$(SR); E=$?
assert "M2c 커밋되지 않은 수정 = 인식 안 함" 0 "인식 안 함(커밋되지 않은 수정)" "상시 답 출처" "$E" "$OUT"
git -C "$SP" checkout -q -- .dddjango/standing-answer.md
F2="$SP/.dddjango-web/r"; mkdir -p "$F2"
printf '{"git_snapshot": "%s", "mode": "refactor"}\n' "$(git -C "$SP" rev-parse HEAD)" > "$F2/build-state.json"
SRC="출처 = 상시 답 .dddjango/standing-answer.md:3@$C12"
G0='## G0 2026-09-29 10:00

- 결정 줄: M3 M5 M8 M9 · 결정 = ⓐ · 사유 = 빚은 먼저 정리 · 출처 = 대리 답 ⓐ /x/scope.md:50(2026-09-29 09:59)
- 결정 줄: M7 · 결정 = ⓐ · 사유 = 사용자 판단 «위반 — 정리» · 출처 = 사용자 원문 /x/user-answers.md:10(2026-09-29 09:59)

의미 audit: 20260929-100000
의미 ⓐ 키: M3 M5 M7 M8 M9
ⓐ 키: -
요구 키: -'
USER() { printf '\n## ⓐ 재상정 %s\n\n- 결정 줄: %s · 결정 = 별도 요청 · 사유 = 동작 불변 정리 불가 · 출처 = 본인 직접(%s)\n\n재상정 키: -\n의미 재상정 키: %s\n' "$1" "$2" "$1" "$2"; }
SEC() { # SEC <시각> <결정 줄…> — 표지 · 줄 · 키 행(상시 답 절 정형)
  local when="$1" keys=""; shift
  printf '\n## ⓐ 재상정 %s\n\n- 상시 답 적용 %s건\n' "$when" "$#"
  for l in "$@"; do printf '%s\n' "$l"; keys="$keys $(grep -oE '^- (결정 줄: )?M[0-9]+' <<<"$l" | grep -oE 'M[0-9]+')"; done
  printf '\n재상정 키: -\n의미 재상정 키:%s\n' "$keys"
}
GATE() { { echo "$G0"; printf '%s' "$@"; } > "$F2/refactor-scope.md"; SR "$F2" --gate; }
L() { echo "- 결정 줄: $1 · 결정 = 별도 요청 · 사유 = 동작 불변 불가($2) · $SRC"; }
L5=$(L M5 "테스트 본문 동반 — tests/web/test_home.py:2")
L7="- M7 · 결정 = 별도 요청 · 사유 = 동작 불변 불가(외부 관찰 동작 · 테스트 새 판정 — home/view/home_view.py:2-4 · tests/web/test_home.py:3) · $SRC"
OUT=$(GATE "$(USER '2026-09-29 10:05' M3)"); E=$?
assert "M3a 사용자 출처 재상정만(파일 무관 흐름) = gate exit 0 · 상시 답 줄 0" 0 "상시 답 줄 0 · 대체 0 · red 0" - "$E" "$OUT"
OUT=$(GATE "$(USER '2026-09-29 10:05' M3)" "$(SEC '2026-09-29 10:20' "$L5" "$L7")"); E=$?
assert "M3b 정상(결정 줄 머리 · web 상대 위치 · G0 사용자 판단 줄 뒤 M7) = exit 0" 0 "상시 답 줄 2 · 대체 0 · red 0" - "$E" "$OUT"
OUT=$(GATE "$(SEC '2026-09-29 10:20' "$(L M5 '경계 교차 — tests/web/test_home.py:2')" \
  "$(L M7 '외부 관찰 동작 · 경계 교차 — tests/web/test_home.py:3')" "$(L C3 '외부 관찰 동작 — tests/web/test_home.py:1')" \
  "$(L M4 '외부 관찰 동작 — tests/web/test_home.py:1')")"); E=$?
assert "M4a 범주 셋 밖(단독) = 묻는다" 2 "③ 범주 ['경계 교차'] 가" - "$E" "$OUT"
assert "M4b 범주 혼합 = 묻는다" 2 "③ 범주 ['외부 관찰 동작', '경계 교차'] 가 외부 관찰 동작 · 테스트 본문 동반 · 테스트 새 판정 셋 안이 아니다 — 묻는다" - "$E" "$OUT"
assert "M4c C 키 = 묻는다" 2 "③ \`C<n>\` 에는 상시 답을 쓰지 않는다 — 묻는다" - "$E" "$OUT"
assert "M4d G0 의미 ⓐ 밖 M = 고친 줄" 2 "③ M4 이 마지막 \`## G0\` 의 의미 ⓐ 항목이 아니다 — 고친 줄" - "$E" "$OUT"
NOANC=$(git -C "$SP" commit-tree "$C1^{tree}" -m orphan)
OUT=$(GATE "$(SEC '2026-09-29 10:20' "${L5/:3@/:2@}" "${L7/@$C12/@${NOANC:0:12}}" \
  "- M8 · 결정 = ⓑ · 사유 = 동작 불변 불가(외부 관찰 동작 — tests/web/test_home.py:1) · $SRC")"); E=$?
assert "M5a 출처 행 어긋남 = ①" 2 "① 커밋 $C12 판의 2행이 유일한 인식 줄이 아니다" - "$E" "$OUT"
assert "M5b 출처 커밋이 HEAD 조상 아님 = ①" 2 "이 HEAD 의 조상이 아니다" - "$E" "$OUT"
assert "M5c 처분 ⓑ = ②" 2 "② 처분이 «별도 요청»이 아니다" - "$E" "$OUT"
OUT=$(GATE "$(SEC '2026-09-29 10:20' "- 결정 줄: M5 결정 = 별도 요청 · 사유 = 동작 불변 불가(테스트 본문 동반 — tests/web/test_home.py:2) · $SRC")"); E=$?
assert "M5d 칸 모양이 틀린 상시 답 줄도 검사 대상(조용히 빠지지 않음) = ②" 2 "② 처분이 «별도 요청»이 아니다" - "$E" "$OUT"
OUT=$(GATE "$(printf '\n## ⓐ 재상정 2026-09-29 10:20\n\n%s\n\n재상정 키: -\n의미 재상정 키: M5\n' "$L5")"); E=$?
assert "M6a 표지 없는 재상정 절 = ④" 2 "④ 첫 줄 \`- 상시 답 적용 k건\` 이 있는 \`ⓐ 재상정\` 절 밖이다" - "$E" "$OUT"
OUT=$(GATE "$(printf '\n%s\n' "$L5")" "$(SEC '2026-09-29 10:20' "$L7" "- 결정 줄: M9 · 결정 = 별도 요청 · 사유 = 동작 불변 정리 불가 · 출처 = 본인 직접(10:20)")"); E=$?
assert "M6b G0 절 안 상시 답 줄 = ④" 2 "④ 첫 줄 \`- 상시 답 적용 k건\` 이 있는 \`ⓐ 재상정\` 절 밖이다" - "$E" "$OUT"
assert "M6c 상시 답 절 안 사용자 결정 줄 = ④" 2 "④ 상시 답 절에 상시 답 아닌 결정 줄이 있다" - "$E" "$OUT"
OUT=$(GATE "$(USER '2026-09-29 10:05' M3)" "$(SEC '2026-09-29 10:20' "$(L M3 '외부 관찰 동작 — home/view/home_view.py:1')")"); E=$?
assert "M7 앞선 재상정 사용자 답 뒤 상시 답 줄 = ④(사용자 답이 이긴다)" 2 "④ M3 의 앞선 재상정 사용자 답 줄보다 뒤다" - "$E" "$OUT"
OUT=$(GATE "$(SEC '2026-09-29 10:20' "$(L M5 '경계 교차 — tests/web/test_home.py:2')" "$(L M7 '외부 관찰 동작 — :67')")" \
  "$(USER '2026-09-29 10:30' M5)" "$(SEC '2026-09-29 10:31' "$L7")"); E=$?
assert "M8 대체 — 뒤 절 사용자 답 · 고친 상시 답 줄이 앞 red 줄을 대체" 0 "상시 답 줄 3 · 대체 2 · red 0" - "$E" "$OUT"
OUT=$(GATE "$(SEC '2026-09-29 10:20' "$(L M5 '테스트 본문 동반 — :2')" "$(L M7 '외부 관찰 동작 — tests/web/test_home.py:2·3')" \
  "$(L M8 '외부 관찰 동작 — home/view/home_view.py:9')" "$(L M9 '외부 관찰 동작 — tests/web/test_home.py:2 단언')")"); E=$?
assert "M9a 맨 \`:행\` = ③ 형식" 2 "③ 위치 \`:2\` 가 \`파일:행[-행]\`(저장소 상대 · 1 ≤ 시작 ≤ 끝) 정형이 아니다" - "$E" "$OUT"
assert "M9b \`행·행\` 이어 적기 = ③ 형식(조용히 버리지 않음)" 2 "③ 위치 \`3\` 가" - "$E" "$OUT"
assert "M9c git_snapshot 판 줄 수 밖 = ③" 2 "③ 위치 \`home/view/home_view.py:9\` 가 git_snapshot 판" - "$E" "$OUT"
assert "M9e 위치 뒤 꼬리 글 = ③ 형식(앞머리만 맞춰 통과시키지 않음)" 2 "③ 위치 \`tests/web/test_home.py:2 단언\` 가 \`파일:행[-행]\`(저장소 상대" - "$E" "$OUT"
printf 'a\n' > "$SP/web/home/view/home_view.py"; commit_all "$SP" slice0 >/dev/null
OUT=$(GATE "$(SEC '2026-09-29 10:20' "$L7")"); E=$?
assert "M9d 슬라이스 0 뒤 파일이 줄어도 git_snapshot 판 기준 = exit 0" 0 "상시 답 줄 1 · 대체 0 · red 0" - "$E" "$OUT"
OUT=$(GATE "$(SEC '2026-09-29 10:20' "$L5" "$L7" | sed -e 's/^의미 재상정 키:.*/의미 재상정 키: M5/' -e 's/^재상정 키: -$/재상정 키: C1/')"); E=$?
assert "M10a 의미 재상정 키 ≠ 상시 답 줄 키 = ⑤" 2 "⑤ \`의미 재상정 키:\` ['M5'] ≠ 상시 답 줄 키 ['M5', 'M7']" - "$E" "$OUT"
assert "M10b 재상정 키 ≠ - = ⑤" 2 "⑤ \`재상정 키:\` 가 \`-\` 한 행이 아니다" - "$E" "$OUT"
{ printf '%s\n' '## G0 2026-09-28 09:00' '의미 audit: 20260928-090000' '의미 ⓐ 키: M5 M7' 'ⓐ 키: -' '요구 키: -'
  SEC '2026-09-28 09:10' "${L5/:3@/:2@}"; USER '2026-09-28 09:20' M7; echo
  printf '%s\n' '## G0 2026-09-29 10:00' '의미 audit: 20260929-100000' '의미 ⓐ 키: M7' 'ⓐ 키: -' '요구 키: -'; } > "$F2/refactor-scope.md"
{ cat "$F2/refactor-scope.md"; SEC '2026-09-29 10:20' "$L7"; } > "$F2/scope.tmp"; mv "$F2/scope.tmp" "$F2/refactor-scope.md"
OUT=$(SR "$F2" --gate); E=$?
assert "M11 재사용 폴더 — 마지막 \`## G0\` 앞 실행 줄은 보지 않는다" 0 "상시 답 줄 1 · 대체 0 · red 0" - "$E" "$OUT"
printf '바꿈\n' > "$SP/.dddjango/standing-answer.md"; commit_all "$SP" edit >/dev/null
git -C "$SP" rm -q .dddjango/standing-answer.md; commit_all "$SP" delete >/dev/null
OUT=$(GATE "$(SEC '2026-09-29 10:20' "$L5" "$L7")"); E=$?
assert "M12 적용 커밋 뒤 파일 수정·삭제 = 커밋 기준으로 유효 exit 0" 0 "상시 답 줄 2 · 대체 0 · red 0" - "$E" "$OUT"
OUT=$(SR); E=$?
assert "M12′ 삭제 뒤 standing = 없음(다음 BC 부터 원래대로)" 0 "요약: standing 없음 — 적용 0" - "$E" "$OUT"
OUT=$(GATE "$(SEC '2026-09-29 10:20' "- M3(+M12) · 결정 = 별도 요청 · 사유 = 동작 불변 불가(외부 관찰 동작 — tests/web/test_home.py:1) · $SRC")"); E=$?
assert "M13 병합 괄호 M3(+M12) — 괄호 안은 키가 아니다 = exit 0" 0 "상시 답 줄 1 · 대체 0 · red 0" - "$E" "$OUT"
OUT=$(GATE "$(SEC '2026-09-29 10:20' "$(L M5 '경계 교차 — tests/web/test_home.py:2')")" \
  "$(printf '\n## G0 재승인 2026-09-29 10:30\n\n- 결정 줄: M5 · 결정 = 별도 요청 · 사유 = x · 출처 = 본인 직접(10:30)\n\nⓐ 키: -\n요구 키: -\n')"); E=$?
assert "M14 대체는 뒤 재상정 절만 — G0 재승인 절 사용자 줄은 대체하지 않는다" 2 "③ 범주 ['경계 교차'] 가" "대체 1" "$E" "$OUT"
OUT=$(GATE "$(SEC '2026-09-29 10:20' "$(L 'M3 M5' '경계 교차 — tests/web/test_home.py:2')")" "$(USER '2026-09-29 10:30' M3)"); E=$?
assert "M15 다중 키 줄을 뒤 사용자 답이 일부 키만 다루면 나머지 키는 계속 검사(키별 대체)" 2 "③ 범주 ['경계 교차'] 가" "대체 1" "$E" "$OUT"
OUT=$(GATE "$(SEC '2026-09-29 10:20' "$(L M7 '`외부 관찰 동작`, `테스트 새 판정` — tests/web/test_home.py:1')")"); E=$?
assert "M16 범주를 백틱째·쉼표로 옮겨도 인식 = exit 0" 0 "상시 답 줄 1 · 대체 0 · red 0" - "$E" "$OUT"
printf '\x89PNG\r\n\x1a\n\xff\xfe' > "$SP/web/logo.png"; commit_all "$SP" logo >/dev/null
printf '{"git_snapshot": "%s", "mode": "refactor"}\n' "$(git -C "$SP" rev-parse HEAD)" > "$F2/build-state.json"
OUT=$(GATE "$(SEC '2026-09-29 10:20' "$(L M5 '테스트 본문 동반 — logo.png:1 · tests:1 · tests/web/test_home.py:3-2 · /etc/hosts:1')")"); E=$?
assert "M17a 비UTF-8 파일 = red(실행 불능 아님)" 2 "③ 위치 \`logo.png:1\` 가 git_snapshot 판" - "$E" "$OUT"
assert "M17b 디렉터리 = red" 2 "③ 위치 \`tests:1\` 가 git_snapshot 판" - "$E" "$OUT"
assert "M17c 역순 행 = 형식 red" 2 "③ 위치 \`tests/web/test_home.py:3-2\` 가 \`파일:행[-행]\`(저장소 상대" - "$E" "$OUT"
assert "M17d 절대 경로 = 형식 red" 2 "③ 위치 \`/etc/hosts:1\` 가 \`파일:행[-행]\`(저장소 상대" - "$E" "$OUT"

echo "fixtures_refactor_audit: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
