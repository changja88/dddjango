#!/usr/bin/env bash
# dddjango-web refactor_audit.py 픽스처 (plan · plan --against · plan --names · check · check-verdict · residual · self-test).
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
STAMP=$(ls "$F/residual" | sort | tail -1)
printf '| M | 판정 | 근거 |\n|---|---|---|\n| M9 | 해소 | web/home/home/view/home_view.py:2 |\n| M10 | 해소 | 이유만 적음 |\n' > "$F/residual/$STAMP/result-screen.md"
OUT=$(RA residual "$F" --finalize "$STAMP"); E=$?
assert "I3 새 파일:행 없는 해소는 잔존 exit 2" 2 "M_m=1(결정적 잔존 0 · 리뷰어 잔존 1" - "$E" "$OUT"
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

echo "fixtures_refactor_audit: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
