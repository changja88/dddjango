#!/usr/bin/env bash
# dddjango-web 빚 스캔·잔존 픽스처 (--debt-scan · --debt-residual — Phase 0 step 4′·G2).
# (바탕: v1.3.1 fixtures_debt.sh D1~D29 — 2.0.0 새 트리 · 새 검사 번호로 · D30~D38 의 빚 모드 WV 는 fixtures_sdk.sh)
# mktemp 임시 git 프로젝트 + 각 red 에 양성 대조 짝.
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

w() { mkdir -p "$(dirname "$1")"; printf '%s\n' "${@:2}" > "$1"; }   # w <파일> <줄…>

mkproj() { # mkproj <dir> — Django풍 루트 + 2.0.0 표준 web/ 트리(빚 0) + git 초기 커밋, BASE 출력
  local p="$1" W="$1/web" O="$1/web/application/order" k
  w "$p/config/settings.py" "SECRET_KEY = 'x'"
  w "$p/manage.py" "# manage"
  w "$p/requirements.txt" "Django==5.1.2" "pytest==8.3.3" "pytest-django==4.9.0"
  w "$W/__init__.py" ""
  w "$W/apps.py" "from django.apps import AppConfig" "" "" "class WebConfig(AppConfig):" '    name: str = "web"'
  w "$W/urls.py" "from web.root.router.root_router import urlpatterns" "" '__all__: list[str] = ["urlpatterns"]'
  w "$W/root/ruff.toml" '[lint]' 'select = ["ANN"]'
  w "$W/root/router/root_router.py" "from django.urls import include, path" "" "from web.application.order import order_router" "" \
    'urlpatterns: list[object] = [path("orders/", include((order_router.urlpatterns, order_router.app_name)))]'
  w "$W/root/scaffold/view/root_view.html" "{% load static %}" "<html><head>" \
    "<link rel=\"stylesheet\" href=\"{% static 'design_system/theme/app_theme.css' %}\">" \
    "<script src=\"{% static 'web/htmx/htmx.min.js' %}\" defer></script>" \
    "</head><body>{% block content %}{% endblock %}</body></html>"
  w "$W/root/scaffold/view_model/root_vm.py" "from web.root.scaffold.state.root_state import RootState" "" "" \
    "class RootVM:" "    def build(self) -> RootState:" '        return RootState(title="shop")'
  w "$W/root/scaffold/state/root_state.py" "from dataclasses import dataclass" "" "" \
    "@dataclass(frozen=True, slots=True, kw_only=True)" "class RootState:" "    title: str"
  w "$W/root/handler/root_request_handler.py" "class RootRequestHandler:" "    pass"
  w "$W/root/initializer/root_initializer.py" "class RootInitializer:" "    pass"
  for k in color typography spacing radius shadow duration asset; do
    case $k in duration) w "$W/design_system/foundation/app_$k.css" ":root { --duration-fast: 150ms; }" ;;
      *) w "$W/design_system/foundation/app_$k.css" ":root { --$k-base: 1px; }" ;; esac
  done
  w "$W/design_system/theme/app_theme.css" "body { margin: 0; font: var(--typography-base); }"
  w "$W/design_system/component/button/primary_button.html" '<a class="primary-button" href="{{ href }}">{{ label }}</a>'
  w "$W/design_system/component/button/primary_button.css" ".primary-button { color: var(--color-base); }"
  mkdir -p "$W/design_system/util"
  w "$W/common/network/api_client.py" "from django.test import Client" "" "" \
    "class ApiClient:" "    def get(self, path: str) -> object:" "        return Client().get(path)"
  mkdir -p "$W/common/enum" "$W/common/service" "$W/common/util"
  for k in use_case view_model state shared_state service; do mkdir -p "$O/application_layer/$k"; done
  for k in data_source repository service; do mkdir -p "$O/infra_layer/$k"; done
  for k in view section widget ui_extension; do mkdir -p "$O/presentation_layer/$k"; done
  for k in entity value_object enum domain_service specification; do mkdir -p "$O/domain_layer/order/$k"; done
  w "$O/ruff.toml" '[lint]' 'select = ["ANN"]'
  w "$O/order_router.py" "from django.urls import path" "" \
    "from web.application.order.presentation_layer.view.order_list_view import order_list_view" "" \
    'app_name: str = "order"' "" "" "class OrderRoutes:" '    LIST: str = "order:list"' "" "" \
    'urlpatterns: list[object] = [path("", order_list_view, name="list")]'
  w "$O/order_navigator.py" "from django.urls import reverse" "" "" "class OrderNavigator:" "    @staticmethod" \
    "    def list_href() -> str:" "        from web.application.order.order_router import OrderRoutes" \
    "        return reverse(OrderRoutes.LIST)"
  w "$O/domain_layer/order/order.py" "from dataclasses import dataclass" "" "" \
    "@dataclass(frozen=True, slots=True, kw_only=True)" "class Order:" "    order_id: str"
  w "$O/application_layer/view_model/order_list_vm.py" \
    "from web.application.order.application_layer.state.order_list_state import OrderListState" "" "" \
    "class OrderListVM:" "    def build(self) -> OrderListState:" "        return OrderListState(count=0)"
  w "$O/application_layer/state/order_list_state.py" "from dataclasses import dataclass" "" "" \
    "@dataclass(frozen=True, slots=True, kw_only=True)" "class OrderListState:" "    count: int"
  w "$O/presentation_layer/view/order_list_view.py" "from django.http import HttpRequest, HttpResponse" \
    "from django.shortcuts import render" "" \
    "from web.application.order.application_layer.view_model.order_list_vm import OrderListVM" "" "" \
    "def order_list_view(request: HttpRequest) -> HttpResponse:" \
    '    return render(request, "application/order/presentation_layer/view/order_list_view.html", {"state": OrderListVM().build()})'
  w "$O/presentation_layer/view/order_list_view.html" '{% extends "root/scaffold/view/root_view.html" %}' \
    "{% block content %}" '{% include "application/order/presentation_layer/section/order_list_summary_section.html" %}' \
    "{% endblock %}"
  w "$O/presentation_layer/section/order_list_summary_section.html" '<div class="order-list-summary">{{ state.count }}</div>'
  w "$W/static/htmx/htmx.min.js" 'var htmx={version:"2.0.10"};'
  w "$W/static/application/order/order_list_view.css" ".order-list { color: var(--color-base); }"
  mkdir -p "$W/static/images"
  w "$p/web_test/application/order/application_layer/order_list_vm_test.py" "def test_order_list_vm() -> None:" "    assert True"
  find "$W" -type d ! -path '*/design_system*' ! -path '*/static*' -exec touch {}/__init__.py \;
  find "$W" -type d -empty -exec touch {}/.gitkeep \;
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

bad_handlers() { # bad_handlers <proj> — ST9(root_ 접두 위반) 3건 커밋
  w "$1/web/root/handler/a_handler.py" "x: int = 1"
  w "$1/web/root/handler/c_handler.py" "x: int = 1"
  w "$1/web/root/handler/e_handler.py" "x: int = 1"
  commit_all "$1" bad-handlers >/dev/null
}

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# ---------- D1: 깨끗한 표준 트리 = 빚 0 · 기록 폴더는 dirty 판정 밖
P="$T/d1"; mkproj "$P" >/dev/null
mkdir -p "$P/.dddjango-web/run"
OUT=$(run_backstop "$P" --debt-scan --json "$P/.dddjango-web/run/debt-g0.json"); E=$?
assert "D1a 표준 트리 빚 0" 0 "빚 스캔 — 키 0 · 발견 0" "BLOCKER" "$E" "$OUT"
assert "D1b .dddjango-web 미추적은 dirty 아님" 0 "false" - 0 "$(field_of "$P/.dddjango-web/run/debt-g0.json" dirty)"
echo x > "$P/notes.txt"
run_backstop "$P" --debt-scan --json "$P/.dddjango-web/run/debt-g0.json" >/dev/null
assert "D1c 대조: 루트 미추적 파일은 dirty" 0 "true" - 0 "$(field_of "$P/.dddjango-web/run/debt-g0.json" dirty)"
assert "D1d scanner 지문(플러그인 판 · 검사 집합)" 0 '"checks"' - 0 "$(field_of "$P/.dddjango-web/run/debt-g0.json" scanner)"

# ---------- D2: .gitignore 가 무시하는 파일은 거짓 빚이 아니다(os.walk 대신 git 우주)
P="$T/d2"; mkproj "$P" >/dev/null
printf 'stray.txt\n' > "$P/.gitignore"; commit_all "$P" ignore >/dev/null
printf 'x' > "$P/web/static/stray.txt"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D2a 무시 파일 키 0" 0 "키 0" "stray.txt" "$E" "$OUT"
rm "$P/.gitignore"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D2b 대조: 무시 안 된 static 직속 파일은 빚(ST12)" 2 "[ST12] web/static/stray.txt" - "$E" "$OUT"

# ---------- D3: 브라운필드 legacy htmx core 1개 + 그 root_view 로드 태그(defer 없음) = 빚 아님 · 중복은 빚
P="$T/d3"; mkproj "$P" >/dev/null
rm "$P/web/static/htmx/htmx.min.js"; rmdir "$P/web/static/htmx"
w "$P/web/static/js/htmx.min.js" '(function(){})();'
w "$P/web/root/scaffold/view/root_view.html" "{% load static %}<html><body>{% block content %}{% endblock %}" \
  "<script src=\"{% static 'web/js/htmx.min.js' %}\"></script></body></html>"
commit_all "$P" legacy-core >/dev/null
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D3a legacy core 1개 + 로드 태그 키 0" 0 "키 0" "[PU" "$E" "$OUT"
w "$P/web/static/htmx/htmx.min.js" 'var htmx={version:"2.0.10"};'
run_backstop "$P" --debt-scan --json "$T/d3.json" >/dev/null; E=$?
assert "D3b 대조: legacy+canonical 공존 = PU1 · PU2 키" 2 \
  "PU1|static/js/htmx.min.js=1 PU2|root/scaffold/view/root_view.html=1" - "$E" "$(counts_of "$T/d3.json")"

# ---------- D4: 기존 단위 골격 미비(ST4)는 빚 아님 — 신규 단위만 G2 게이트가 본다
P="$T/d4"; BASE=$(mkproj "$P")
w "$P/web/application/billing/billing_router.py" "urlpatterns: list[object] = []"
w "$P/web/application/billing/__init__.py" ""
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D4a 골격 미비 BC 키 0(ST4 빚 모드 제외 notice)" 0 "ST4(골격 완비) 빚 모드 제외" "[ST4]" "$E" "$OUT"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only st4); E=$?
assert "D4b 대조: 같은 트리의 신규 단위는 diff 게이트 ST4 red" 2 "[ST4]" - "$E" "$OUT"

# ---------- D5: 작업 트리에서만 지운 추적 파일은 유령 키·오류가 아니다
P="$T/d5"; mkproj "$P" >/dev/null
echo "x = 1" > "$P/web/junk.py"; commit_all "$P" junk >/dev/null
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D5a 대조: 추적 파일 실재 시 ST0 빚" 2 "[ST0] web/junk.py" - "$E" "$OUT"
rm "$P/web/junk.py"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D5b 인덱스 전용 삭제 키 0·오류 0" 0 "키 0" "junk.py" "$E" "$OUT"

# ---------- D6: 같은 파일 2건 = 키 1 · 수 2
P="$T/d6"; mkproj "$P" >/dev/null
w "$P/web/design_system/component/button/primary_button.css" ".primary-button { color: #ffffff; }" ".primary-button--dark { color: #000000; }"
commit_all "$P" colors >/dev/null
run_backstop "$P" --debt-scan --json "$T/d6.json" >/dev/null; E=$?
assert "D6 같은 파일 2건 키 1·수 2" 2 "NM10|design_system/component/button/primary_button.css=2" - "$E" "$(counts_of "$T/d6.json")"

# ---------- D7: 위반 3건 → C1..C3 결정적
P="$T/d7"; mkproj "$P" >/dev/null; bad_handlers "$P"
run_backstop "$P" --debt-scan --json "$T/d7a.json" >/dev/null
run_backstop "$P" --debt-scan --json "$T/d7b.json" >/dev/null; E=$?
IDS_A=$(field_of "$T/d7a.json" ids); IDS_B=$(field_of "$T/d7b.json" ids)
assert "D7a C1..C3 키 정렬 순" 2 '{"C1": "ST9|root/handler/a_handler.py", "C2": "ST9|root/handler/c_handler.py", "C3": "ST9|root/handler/e_handler.py"}' - "$E" "$IDS_A"
assert "D7b 두 번 실행 동일" 0 "$IDS_A" - 0 "$IDS_B"

# ---------- D8: 잔존 — ⓐ 1 미해소 exit 2 · 해소 exit 0
P="$T/d8"; mkproj "$P" >/dev/null; bad_handlers "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1
요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D8a ⓐ 미해소 = 잔존 1" 2 "ⓐ 잔존 1 · 요구 잔존 0" - "$E" "$OUT"
git -C "$P" mv web/root/handler/a_handler.py web/root/handler/root_a_handler.py
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D8b ⓐ 해소 = 잔존 0" 0 "ⓐ 잔존 0 · 요구 잔존 0 · 재상정 제외 0 · G0 에 없던 키 0" - "$E" "$OUT"
assert "D8c G2 스캔은 debt-g2.json 에 · G0 동결본 불변" 0 "ST9|root/handler/a_handler.py" - 0 "$(field_of "$P/.dddjango-web/run/debt-g0.json" ids)"
[ -f "$P/.dddjango-web/run/debt-g2.json" ]; assert "D8d debt-g2.json 기록" 0 - - "$?" ""

# ---------- D9: 재승인 절이 앞 ⓐ 를 다시 적어도(누적 기록) 같은 판정
P="$T/d9"; mkproj "$P" >/dev/null; bad_handlers "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1
요구 키: -

## G0 재승인 @NOW@
ⓐ 키: C1 C2
요구 키: -'
git -C "$P" mv web/root/handler/c_handler.py web/root/handler/root_c_handler.py
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D9a 누적 행의 앞 ⓐ 미해소 = exit 2" 2 "잔존 ⓐ C1" "잔존 ⓐ C2" "$E" "$OUT"
git -C "$P" mv web/root/handler/a_handler.py web/root/handler/root_a_handler.py
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D9b 누적 ⓐ 전부 해소 = exit 0" 0 "ⓐ 잔존 0" - "$E" "$OUT"

# ---------- D10: 재상정 키는 잔존에서 빠진다
P="$T/d10"; mkproj "$P" >/dev/null; bad_handlers "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1 C2
요구 키: -

## ⓐ 재상정 @NOW@
재상정 키: C2'
git -C "$P" mv web/root/handler/a_handler.py web/root/handler/root_a_handler.py
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D10a 재상정 제외 = exit 0" 0 "ⓐ 잔존 0 · 요구 잔존 0 · 재상정 제외 1" - "$E" "$OUT"
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1 C2
요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D10b 대조: 재상정 절 없으면 C2 잔존" 2 "잔존 ⓐ C2" - "$E" "$OUT"

# ---------- D11: 요구 키 미해소 = exit 2
P="$T/d11"; mkproj "$P" >/dev/null; bad_handlers "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: -
요구 키: C3'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D11a 요구 키 미해소 = 요구 잔존 1" 2 "ⓐ 잔존 0 · 요구 잔존 1" - "$E" "$OUT"
git -C "$P" mv web/root/handler/e_handler.py web/root/handler/root_e_handler.py
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D11b 대조: 요구 키 해소 = exit 0" 0 "요구 잔존 0" - "$E" "$OUT"

# ---------- D12: 두 행 모두 `-`
P="$T/d12"; mkproj "$P" >/dev/null; bad_handlers "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
- ⓐ 키: -
- 요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D12 ⓐ·요구 모두 - = exit 0(미룬 키 잔존은 판정 밖)" 0 "ⓐ 잔존 0 · 요구 잔존 0" - "$E" "$OUT"

# ---------- D13: 판정 불가(exit 1)와 전이 규칙
P="$T/d13"; mkproj "$P" >/dev/null; bad_handlers "$P"; run_folder "$P" run
scope_md "$P" run '# 리팩터링 스코프

## 스캔
C1 | ST9|root/handler/a_handler.py'
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
P="$T/d14"; mkproj "$P" >/dev/null; bad_handlers "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1 C9
요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D14 없는 ID = exit 1" 1 "C9" - "$E" "$OUT"

# ---------- D15: 개명만 하고 안 고침 — 잔존은 «해소»로 보지만 diff 게이트가 새 경로를 red(두 게이트 짝)
P="$T/d15"; mkproj "$P" >/dev/null; bad_handlers "$P"; BASE=$(git -C "$P" rev-parse HEAD); run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1
요구 키: -'
git -C "$P" mv web/root/handler/a_handler.py web/root/handler/a2_handler.py
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D15a 잔존 판정은 키 대조라 exit 0 · 새 키 보고" 0 "G0 에 없던 키 1" - "$E" "$OUT"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only st9); E=$?
assert "D15b diff 게이트가 새 경로 발견 red" 2 "a2_handler.py" - "$E" "$OUT"
git -C "$P" mv web/root/handler/a2_handler.py web/root/handler/root_a_handler.py
OUT=$(run_backstop "$P" --diff-base "$BASE" --only st9); E=$?
assert "D15c 대조: 표준 이름으로 개명하면 diff 게이트 green" 0 "blocker 0건" - "$E" "$OUT"

# ---------- D16: 참조 치환 줄의 기존 위반(PU7 — added 줄 게이트)은 diff 게이트에서 새 줄 red — 묶음 규칙이 필요한 이유
P="$T/d16"; mkproj "$P" >/dev/null; S16="$P/web/application/order/presentation_layer/section"
printf 'png' > "$P/web/static/images/cloud-ornament.png"
w "$S16/order_list_hero_section.html" "{% load static %}" "<img src=\"{% static 'web/images/cloud-ornament.png' %}\" alt=\"{{ state.alt|safe }}\">"
w "$S16/order_list_logo_section.html" "{% load static %}" "<img src=\"{% static 'web/images/cloud-ornament.png' %}\">"
BASE=$(commit_all "$P" ref-lines)
git -C "$P" mv web/static/images/cloud-ornament.png web/static/images/cloud_ornament.png
python3 - "$S16/order_list_logo_section.html" <<'PY'
import sys; p = sys.argv[1]; t = open(p).read(); open(p, 'w').write(t.replace('cloud-ornament', 'cloud_ornament'))
PY
OUT=$(run_backstop "$P" --diff-base "$BASE" --only pu7); E=$?
assert "D16a 대조: 위반 없는 참조 줄 치환은 green" 0 "blocker 0건" - "$E" "$OUT"
python3 - "$S16/order_list_hero_section.html" <<'PY'
import sys; p = sys.argv[1]; t = open(p).read(); open(p, 'w').write(t.replace('cloud-ornament', 'cloud_ornament'))
PY
OUT=$(run_backstop "$P" --diff-base "$BASE" --only pu7); E=$?
assert "D16b 참조 줄의 기존 PU7 이 치환으로 새 줄 red" 2 "[PU7] BLOCKER — web/application/order/presentation_layer/section/order_list_hero_section.html:2" - "$E" "$OUT"

# ---------- D17: 빚 모드는 단독 — 범위 좁히기·게이트 혼용 금지
P="$T/d17"; BASE=$(mkproj "$P")
OUT=$(run_backstop "$P" --debt-scan --diff-base "$BASE"); E=$?
assert "D17a --debt-scan + --diff-base = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --debt-scan --only st9); E=$?
assert "D17b --debt-scan + --only = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
mkdir -p "$P/.dddjango-web/run"
OUT=$(run_backstop "$P" --debt-scan --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D17c --debt-scan + --debt-residual = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --json "$T/x.json"); E=$?
assert "D17d --json 단독 = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --debt-scan --design-build "$P/.dddjango-web/run"); E=$?
assert "D17e --debt-scan + --design-build = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --debt-scan --update-baseline); E=$?
assert "D17f --debt-scan + --update-baseline = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D17g 대조: --debt-scan 단독은 실행" 0 "빚 스캔 — 키 0" - "$E" "$OUT"

# ---------- D18: git 저장소가 아니면 빚 스캔 실행 불능(«빚 0» 아님)
P="$T/d18"; mkproj "$P" >/dev/null; rm -rf "$P/.git"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D18 비git = 실행 불능 exit 1" 1 "실행 불능" "키 0" "$E" "$OUT"

# ---------- D19: git 이 web/ 을 못 보면 실행 불능(«빚 0» 아님) — 심볼릭 링크 · git 밖·무시된 폴더
P="$T/d19a"; mkproj "$P" >/dev/null; bad_handlers "$P"
mv "$P/web" "$T/d19a-web"; ln -s "$T/d19a-web" "$P/web"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D19a web 심볼릭 링크 = 실행 불능 exit 1" 1 "심볼릭 링크" "키 0" "$E" "$OUT"
mkdir -p "$T/d19b"; git -C "$T/d19b" init -q; printf 'proj/\n' > "$T/d19b/.gitignore"
P="$T/d19b/proj"; mkproj "$P" >/dev/null; bad_handlers "$P"; rm -rf "$P/.git"
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
w "$P/web/static/stray.txt" "x"
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D20b G2: 새 코드의 키는 «G0 에 없던 키»(보고만) exit 0" 0 "G0 에 없던 키 1" - "$E" "$OUT"

# ---------- D21: 재승인 절이 앞 요구 키를 다시 적지 않아도 요구 키는 남는다 · 재상정 뒤 재승인은 되살린다
P="$T/d21"; mkproj "$P" >/dev/null; bad_handlers "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: -
요구 키: C1

## G0 재승인 @NOW@
ⓐ 키: C2
요구 키: -'
git -C "$P" mv web/root/handler/c_handler.py web/root/handler/root_c_handler.py
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D21a 앞 절 요구 키 C1 미해소 = 요구 잔존 1 exit 2" 2 "ⓐ 잔존 0 · 요구 잔존 1" - "$E" "$OUT"
git -C "$P" mv web/root/handler/a_handler.py web/root/handler/root_a_handler.py
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
git -C "$P" mv web/root/handler/root_a_handler.py web/root/handler/a_handler.py
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D21c 재상정 뒤 재승인이 다시 적은 키는 되살아난다" 2 "잔존 ⓐ C1" - "$E" "$OUT"

# ---------- D22: 이번 요청의 G0 절이 없으면(앞 요청 절만 남음) 판정 불가
P="$T/d22"; mkproj "$P" >/dev/null; bad_handlers "$P"; run_folder "$P" run
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
P="$T/d23"; mkproj "$P" >/dev/null; bad_handlers "$P"; run_folder "$P" run
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

# ---------- D24: 리팩토링 스캔(--refactor) — 기존 단위 골격 미비(ST4)도 빚 · notice 없음 · mode 기록
P="$T/d24"; mkproj "$P" >/dev/null
w "$P/web/application/billing/billing_router.py" "urlpatterns: list[object] = []"
w "$P/web/application/billing/__init__.py" ""
commit_all "$P" gaps >/dev/null
OUT=$(run_backstop "$P" --debt-scan --refactor --json "$T/d24.json"); E=$?
assert "D24a 리팩토링 스캔은 기존 단위 ST4 를 빚으로" 2 "[ST4]" "빚 모드 제외" "$E" "$OUT"
assert "D24b BC 단위 키 application/billing" 0 "ST4|application/billing=1" - 0 "$(counts_of "$T/d24.json")"
assert "D24c JSON mode = refactor" 0 '"refactor"' - 0 "$(field_of "$T/d24.json" mode)"
run_backstop "$P" --debt-scan --json "$T/d24f.json" >/dev/null
assert "D24d 대조: 기본 스캔은 mode feature" 0 '"feature"' - 0 "$(field_of "$T/d24f.json" mode)"
assert "D24e 대조: 기본 스캔 counts 에 ST4 없음" 0 - "ST4" 0 "$(counts_of "$T/d24f.json")"

# ---------- D25: legacy core 면제 해제는 로드 태그 면제가 없을 때만(PU1·PU2 한 쌍 — 리팩토링 스캔)
P="$T/d25"; mkproj "$P" >/dev/null
rm "$P/web/static/htmx/htmx.min.js"; rmdir "$P/web/static/htmx"
w "$P/web/static/js/htmx.min.js" '(function(){})();'
w "$P/web/root/scaffold/view/root_view.html" "{% load static %}<html><body>{% block content %}{% endblock %}" \
  "<script src=\"{% static 'web/js/htmx.min.js' %}\"></script></body></html>"
commit_all "$P" legacy-core >/dev/null
run_backstop "$P" --debt-scan --refactor --json "$T/d25.json" >/dev/null
assert "D25a defer 없는 legacy 태그 → PU1·PU2 한 쌍 면제 유지" 0 - "PU" 0 "$(counts_of "$T/d25.json")"
w "$P/web/root/scaffold/view/root_view.html" "{% load static %}<html><body>{% block content %}{% endblock %}" \
  "<script src=\"{% static 'web/js/htmx.min.js' %}\" defer></script></body></html>"
commit_all "$P" defer-tag >/dev/null
run_backstop "$P" --debt-scan --refactor --json "$T/d25b.json" >/dev/null
assert "D25b defer 있는 legacy 태그 → PU1 면제 걷힘" 0 "PU1|static/js/htmx.min.js=1" - 0 "$(counts_of "$T/d25b.json")"
run_backstop "$P" --debt-scan --json "$T/d25c.json" >/dev/null
assert "D25c 대조: 기본 스캔은 legacy core 면제 그대로" 0 - "PU1" 0 "$(counts_of "$T/d25c.json")"

# ---------- D26: --debt-residual 은 debt-g0.json mode 를 따른다(리팩토링 동결본 → ST4 잔존 판정)
P="$T/d26"; mkproj "$P" >/dev/null
w "$P/web/application/billing/billing_router.py" "urlpatterns: list[object] = []"
w "$P/web/application/billing/__init__.py" ""
commit_all "$P" gap >/dev/null
mkdir -p "$P/.dddjango-web/run"
run_backstop "$P" --debt-scan --refactor --json "$P/.dddjango-web/run/debt-g0.json" >/dev/null
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1
요구 키: -
의미 ⓐ 키: -
의미 audit: 20260927-120000'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D26a 리팩토링 동결본 — ST4 미해소 잔존 exit 2" 2 "잔존 ⓐ C1 ST4|application/billing" - "$E" "$OUT"
python3 - "$P/.dddjango-web/run/debt-g0.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d['mode'] = 'feature'; json.dump(d, open(sys.argv[1], 'w'))
PY
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D26b 대조: 같은 동결본을 mode feature 로 읽으면 ST4 를 보지 않아 해소 exit 0" 0 "ⓐ 잔존 0" - "$E" "$OUT"

# ---------- D27: --refactor·--subst-check·--names·--except·--build 배타
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
OUT=$(run_backstop "$P" --subst-check HEAD HEAD --only st); E=$?
assert "D27g --subst-check + --only = 사용 오류" 1 "단독 모드" - "$E" "$OUT"
OUT=$(run_backstop "$P" --subst-check HEAD); E=$?
assert "D27h --subst-check 값 하나 = 사용 오류" 1 "값 둘" - "$E" "$OUT"
OUT=$(run_backstop "$P" --subst-check HEAD HEAD); E=$?
assert "D27i 대조: --subst-check 단독은 실행(변경 0 = green)" 0 "치환 확인 — web/ 밖 변경 파일 0" - "$E" "$OUT"

# ---------- D28: 의미(M) 행 — C 판정 무변 · 값 검사는 접는 절에서만
P="$T/d28"; mkproj "$P" >/dev/null; bad_handlers "$P"; run_folder "$P" run
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

# ---------- D29: 명세 정형 행 파서(--subst-check --names) — `## 슬라이스 0` 절만
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

# ---------- D30: 표준 트리 밖 옛 배치 — 파일마다 ST0 키(게이트의 폴더 발견을 펼침) · 층 무관 IM(IM25)은 파일 키 · 층 의존 IM 은 키 아님
P="$T/d30"; mkproj "$P" >/dev/null; L="$P/web/chart/chart"
w "$P/web/chart/__init__.py" ""
w "$L/section/chart_app_bar.html" '{% extends "design_system/component/button/primary_button.html" %}'
w "$L/view/chart_view.py" "from application.chart.models import Chart" "from web.design_system.foundation import app_color"
commit_all "$P" legacy-layout >/dev/null
run_backstop "$P" --debt-scan --json "$T/d30.json" >/dev/null; E=$?
assert "D30a 옛 배치 파일마다 ST0 키" 2 "ST0|chart/__init__.py=1 ST0|chart/chart/section/chart_app_bar.html=1 ST0|chart/chart/view/chart_view.py=1" "ST0|chart=" "$E" "$(counts_of "$T/d30.json")"
OUT=$(run_backstop "$P" --diff-base HEAD --all --only st0); E=$?
assert "D30a′ 대조: 게이트(--all)는 폴더 발견 하나" 2 "[ST0] BLOCKER — web/chart" "chart_app_bar" "$E" "$OUT"
assert "D30b 옛 배치 파일의 백엔드 import = IM25 파일 키" 2 "IM25|chart/chart/view/chart_view.py=1" - "$E" "$(counts_of "$T/d30.json")"
assert "D30c 옛 배치 파일의 design_system 참조 = 층 의존 IM 키 아님" 2 - "IM13" "$E" "$(counts_of "$T/d30.json")"

# ---------- D31: 모델 형태(MD)·명명(NM)도 빚 — 기존 엔티티의 가변 클래스
P="$T/d31"; mkproj "$P" >/dev/null
w "$P/web/application/order/domain_layer/order/entity/order_line.py" "class OrderLine:" "    pass"
commit_all "$P" mutable-entity >/dev/null
run_backstop "$P" --debt-scan --json "$T/d31.json" >/dev/null; E=$?
assert "D31 기존 가변 엔티티 = MD1 키" 2 "MD1|application/order/domain_layer/order/entity/order_line.py=1" - "$E" "$(counts_of "$T/d31.json")"

# ---------- D32: --debt-residual · debt-g0.json scanner 판이 다름 — 판 경계
P="$T/d32"; mkproj "$P" >/dev/null; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: -
요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D32a 같은 판 — 판정" 0 "ⓐ 잔존 0" - "$E" "$OUT"
python3 - "$P/.dddjango-web/run/debt-g0.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d['scanner'] = {'plugin': '1.3.1', 'checks': 'old'}; json.dump(d, open(sys.argv[1], 'w'))
PY
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D32b scanner 판이 다름(v1.3.1 동결본) — exit 1 «판 경계»" 1 "판 경계 — G0 재스캔 필요" - "$E" "$OUT"
python3 - "$P/.dddjango-web/run/debt-g0.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d.pop('scanner'); json.dump(d, open(sys.argv[1], 'w'))
PY
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D32c scanner 없는 옛 동결본 — exit 1 «판 경계»" 1 "판 경계 — G0 재스캔 필요" - "$E" "$OUT"

P="$T/d32d"; mkproj "$P" >/dev/null; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: -
요구 키: -'
python3 - "$P/.dddjango-web/run/debt-g0.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d['scanner']['plugin'] = '0.0.0-other'; json.dump(d, open(sys.argv[1], 'w'))
PY
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D32d plugin 만 다름 — 알림 뒤 판정을 잇는다(exit 0)" 0 "ⓐ 잔존 0" "판 경계" "$E" "$OUT"
assert "D32d′ plugin 만 다름 — 플러그인 판 바뀜 알림" 0 "[info] 플러그인 판 바뀜 — G0 스캔 0.0.0-other → 지금 " - "$E" "$OUT"

P="$T/d32e"; mkproj "$P" >/dev/null; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: -
요구 키: -'
python3 - "$P/.dddjango-web/run/debt-g0.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d['scanner']['keys'] = 'old-keys'; json.dump(d, open(sys.argv[1], 'w'))
PY
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D32e keys 만 다름 — exit 1 «판 경계» · 알림 없음" 1 "판 경계 — G0 재스캔 필요" "플러그인 판 바뀜" "$E" "$OUT"

P="$T/d32f"; mkproj "$P" >/dev/null; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: -
요구 키: -'
python3 - "$P/.dddjango-web/run/debt-g0.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d['scanner']['checks'] = 'old'; json.dump(d, open(sys.argv[1], 'w'))
PY
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D32f checks 만 다름 — exit 1 «판 경계» · 알림 없음" 1 "판 경계 — G0 재스캔 필요" "플러그인 판 바뀜" "$E" "$OUT"

P="$T/d32g"; mkproj "$P" >/dev/null; bad_handlers "$P"; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: C1
요구 키: -'
python3 - "$P/.dddjango-web/run/debt-g0.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d['scanner']['plugin'] = '0.0.0-other'; json.dump(d, open(sys.argv[1], 'w'))
PY
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D32g plugin 만 다름 — ⓐ 잔존 판정을 잇는다(exit 2)" 2 "잔존 ⓐ C1" "판 경계" "$E" "$OUT"
assert "D32g′ plugin 만 다름 — ⓐ 잔존에도 플러그인 판 바뀜 알림" 2 "플러그인 판 바뀜" - "$E" "$OUT"

P="$T/d32h"; mkproj "$P" >/dev/null; run_folder "$P" run
scope_md "$P" run '## G0 @NOW@
ⓐ 키: -
요구 키: -'
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D32h 같은 판 — 잔존 0 · 플러그인 판 바뀜 알림 없음" 0 "ⓐ 잔존 0" "플러그인 판 바뀜" "$E" "$OUT"

P="$T/d32i"; mkdir -p "$P/.dddjango-web/run"
run_backstop "$P" --debt-scan --json "$P/.dddjango-web/run/debt-g0.json" >/dev/null
scope_md "$P" run '## G0 @NOW@
ⓐ 키: -
요구 키: -'
python3 - "$P/.dddjango-web/run/debt-g0.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d['scanner']['plugin'] = '0.0.0-other'; json.dump(d, open(sys.argv[1], 'w'))
PY
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D32i 비git 첫 실행 · plugin 만 다름 — 알림 뒤 판정을 잇는다(exit 0)" 0 "플러그인 판 바뀜" "판 경계" "$E" "$OUT"

# ---------- D33 (2.1.0 검토 r1 #1): 비git · web/ 없는 첫 실행 = 빚 0 — git 보다 web/ 부재를 먼저 본다 · 잔존도 판정할 키 0 이면 비git 이어도 exit 0
P="$T/d33"; w "$P/config/settings.py" "SECRET_KEY = 'x'"; mkdir -p "$P/.dddjango-web/run"
OUT=$(run_backstop "$P" --debt-scan --json "$P/.dddjango-web/run/debt-g0.json"); E=$?
assert "D33a 비git · web/ 없음 = 첫 실행 빚 0 exit 0" 0 "첫 실행" "실행 불능" "$E" "$OUT"
scope_md "$P" run '## G0 @NOW@
ⓐ 키: -
요구 키: -'
w "$P/web/__init__.py" ""
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D33b 비git 첫 실행의 G2 잔존 — 판정할 ⓐ·요구 키 0 이면 exit 0" 0 "ⓐ 잔존 0 · 요구 잔존 0" "판정 불가" "$E" "$OUT"
OUT=$(run_backstop "$P" --debt-scan); E=$?
assert "D33c 대조: 비git 인데 web/ 이 있으면 실행 불능 exit 1" 1 "실행 불능" "키 0" "$E" "$OUT"

# ---------- D34 (2.1.0 검토 r1 #2): 슬라이스 0 이 옛 배치를 새 BC 로 옮기기만 하면 TG1 을 새로 요구하지 않는다(기존 테스트 충분 가정) · 새 파일이 있으면 요구
P="$T/d34"; mkproj "$P" >/dev/null; L="$P/web/chart/chart/view"
w "$P/web/chart/__init__.py" ""
w "$L/chart_view.py" "from django.http import HttpRequest, HttpResponse" "from django.shortcuts import render" "" "" \
  "def chart_view(request: HttpRequest) -> HttpResponse:" '    return render(request, "chart/chart/view/chart.html", {"title": "chart"})'
w "$L/chart.html" "<main>{{ title }}</main>"
BASE=$(commit_all "$P" legacy-chart)
V="$P/web/application/chart/presentation_layer/view"; mkdir -p "$V"
git -C "$P" mv web/chart/chart/view/chart_view.py "$V/chart_view.py"
git -C "$P" mv web/chart/chart/view/chart.html "$V/chart_view.html"
git -C "$P" rm -q -r web/chart
commit_all "$P" slice-0-move >/dev/null
OUT=$(run_backstop "$P" --diff-base "$BASE" --only tg1); E=$?
assert "D34a 옮기기만 한 새 BC — TG1 불발화(알림)" 0 "옮긴 파일만" "TG1] BLOCKER" "$E" "$OUT"
w "$V/chart_detail_view.py" "def chart_detail_view(request: object) -> object:" "    return None"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only tg1); E=$?
assert "D34b 대조: 새 파일이 들어온 새 BC — TG1 발화" 2 "TG1] BLOCKER — web/application/chart" - "$E" "$OUT"
# D34c: 실제 슬라이스 0 꼴 — 옮기며 같은 커밋에서 import·템플릿 이름을 치환해 작은 파일의 git 유사도가 50% 밑(개명 미탐지)
P="$T/d34c"; mkproj "$P" >/dev/null; L="$P/web/chart/chart/view"
w "$P/web/chart/__init__.py" ""
w "$L/chart_view.py" "from django.http import HttpRequest, HttpResponse" "from django.shortcuts import render" \
  "from web.chart.chart.model.chart_model import load_chart" "" "" \
  "def chart_view(request: HttpRequest) -> HttpResponse:" \
  '    return render(request, "chart/chart/view/chart.html", {"chart": load_chart()})'
w "$P/web/chart/chart/model/chart_model.py" "def load_chart() -> dict:" "    return {}"
BASE=$(commit_all "$P" legacy-chart)
V="$P/web/application/chart/presentation_layer/view"; M="$P/web/application/chart/application_layer/view_model"
mkdir -p "$V" "$M"
git -C "$P" mv web/chart/chart/view/chart_view.py "$V/chart_view.py"
git -C "$P" mv web/chart/chart/model/chart_model.py "$M/chart_vm.py"
git -C "$P" rm -q -r web/chart
w "$V/chart_view.py" "from django.http import HttpRequest, HttpResponse" "from django.shortcuts import render" \
  "from web.application.chart.application_layer.view_model.chart_vm import load_chart" "" "" \
  "def chart_view(request: HttpRequest) -> HttpResponse:" \
  '    return render(request, "application/chart/presentation_layer/view/chart_view.html", {"chart": load_chart()})'
commit_all "$P" slice-0-move-edit >/dev/null
OUT=$(run_backstop "$P" --diff-base "$BASE" --only tg1); E=$?
assert "D34c 옮기며 참조 치환한 작은 파일(개명 유사도 50% 밑)도 옮긴 파일 — TG1 불발화" 0 "옮긴 파일만" "TG1] BLOCKER" "$E" "$OUT"

# ---------- D35 (F-X4-1): 폴더 발견(ST12 static/ 직속 허용 외 디렉터리)도 빚은 파일 단위다 — 범위가 소유한 파일(1)만 옮기면
#   ⓐ 잔존 0 · 같은 폴더에 남은 범위 밖 파일(10)은 «범위 밖 남은 빚»(보고만). ⓐ 고르기는 커맨드 빚 목록 규칙
#   (경로가 소유 파일인 키 + 그 파일을 품은 폴더 키)이라 고치기 전 판(폴더 키 하나)에서도 같은 명령이다.
P="$T/d35"; mkproj "$P" >/dev/null
w "$P/web/static/css/chart.css" ".chart { color: red; }"
for k in 01 02 03 04 05 06 07 08 09 10; do w "$P/web/static/css/screen_$k.css" ".screen-$k { color: red; }"; done
commit_all "$P" legacy-css >/dev/null
run_folder "$P" run
CID=$(python3 -c 'import json,sys
d = json.load(open(sys.argv[1])); own = "static/css/chart.css"
print(" ".join(c for c, k in sorted(d["ids"].items()) if k.split("|", 1)[1].rstrip("/") == own
               or own.startswith(k.split("|", 1)[1].rstrip("/") + "/")))' "$P/.dddjango-web/run/debt-g0.json")
scope_md "$P" run "## G0 @NOW@
ⓐ 키: $CID
요구 키: -"
assert "D35a G0 빚 키는 파일 단위 — 소유 파일 키 하나" 0 '"ST12|static/css/chart.css"' '"ST12|static/css"' 0 \
  "$(field_of "$P/.dddjango-web/run/debt-g0.json" ids)"
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D35b 대조: 소유 파일을 안 옮기면 ⓐ 잔존 1" 2 "ⓐ 잔존 1" - "$E" "$OUT"
git -C "$P" mv web/static/css/chart.css web/static/application/order/chart.css
commit_all "$P" slice-0-chart-css >/dev/null
OUT=$(run_backstop "$P" --debt-residual "$P/.dddjango-web/run"); E=$?
assert "D35c 소유 파일만 옮김 = ⓐ 잔존 0 · 같은 폴더 범위 밖 10 은 보고만" 0 "범위 밖 남은 빚 — 폴더 \`static/css/\` 키 10" "잔존 ⓐ" "$E" "$OUT"

# ---------- D36 (2.2.2 B·C): 옛 페이지·DataSource 의 역할은 알아보되 ST0 빚은 파일마다 유지
P="$T/d36"; mkproj "$P" >/dev/null; L="$P/web/chart/chart"
w "$L/view/chart.html" '{% extends "base/base.html" %}' '{% load static %}' '{% block scripts %}' \
  "<script defer src=\"{% static 'web/js/chart_flow.js' %}\"></script>" '{% endblock scripts %}'
w "$L/view/chart_inline.html" '{% extends "base/base.html" %}' '{% load static %}' '{% block scripts %}' \
  '<script>var a = 1;</script>' '{% endblock scripts %}'
w "$L/chart_catalog_data_source.py" 'CHART_PATH: str = "/api/charts"'
w "$P/web/static/js/chart_flow.js" 'document.addEventListener("click", () => {});'
commit_all "$P" legacy-roles >/dev/null
OUT=$(run_backstop "$P" --debt-scan --json "$T/d36.json"); E=$?
assert "D36a 옛 배치 역할의 빚 스캔 — exit 2" 2 '빚 스캔' - "$E" "$OUT"
KEYS=$(python3 - "$T/d36.json" <<'PY'
import json, sys
counts = json.load(open(sys.argv[1]))['counts']
want = {
    'PU2|chart/chart/view/chart_inline.html': True,
    'PU2|chart/chart/view/chart.html': False,
    'IM27|chart/chart/chart_catalog_data_source.py': False,
    'ST0|chart/chart/view/chart_inline.html': True,
    'ST0|chart/chart/view/chart.html': True,
    'ST0|chart/chart/chart_catalog_data_source.py': True,
}
got = {key: key in counts for key in want}
assert got == want, got
print('역할 키 일치 · 세 파일 ST0 유지')
PY
); E=$?
assert "D36b JSON — 인라인 PU2만 · DataSource IM27 없음 · 세 파일 ST0" 0 '역할 키 일치' - "$E" "$KEYS"

# ---------- SDK 비소비 순서는 빚이 아니며 같은 템플릿의 다른 PU2 키는 유지한다.
P="$T/d226"; python3 "$SCRIPTS/test/sdk_fixture.py" mkproj "$P" >/dev/null
python3 "$SCRIPTS/test/sdk_fixture.py" install "$P" >/dev/null
V="$P/web/application/chart/presentation_layer/view/chart_view.html"
w "$P/web/static/js/unrelated.js" 'const unrelated = 1;'
w "$V" '{% load static %}' '{% block scripts %}' \
  "<script defer src=\"{% static 'web/js/unrelated.js' %}\"></script>" \
  "<script defer src=\"{% static 'web/vendor/kakao_js_sdk/kakao.min.js' %}\"></script>" '{% endblock scripts %}'
OUT=$(run_backstop "$P" --debt-scan --json "$T/d226.json"); E=$?
KEYS=$(counts_of "$T/d226.json")
assert 'D226a 무관 JS 앞 SDK — SDK 순서 빚 0' 0 - '기능 JS 태그보다 뒤' 0 "$OUT"
assert 'D226b 무관 JS 앞 SDK — PU2 키 0' 0 - 'PU2|application/chart/presentation_layer/view/chart_view.html' 0 "$KEYS"
w "$V" '{% load static %}' '{% block scripts %}' \
  "<script defer src=\"{% static 'web/js/unrelated.js' %}\"></script>" \
  "<script async defer src=\"{% static 'web/vendor/kakao_js_sdk/kakao.min.js' %}\"></script>" '{% endblock scripts %}'
OUT=$(run_backstop "$P" --debt-scan --json "$T/d226-other.json"); E=$?
assert 'D226c 같은 파일 다른 PU2 — 키 유지' 0 'PU2|application/chart/presentation_layer/view/chart_view.html=1' - 0 "$(counts_of "$T/d226-other.json")"
assert 'D226d 다른 PU2 잔존에도 순서 사유 0' 0 'async 실행 금지' '기능 JS 태그보다 뒤' 0 "$OUT"
# 앞선 JS 가 그 SDK 를 부르면 빚 스캔에서도 순서 빚이다(빚 모드는 모두 새 것 — 게이트가 열린다).
w "$P/web/static/js/unrelated.js" 'window.Kakao.init("k");'
w "$V" '{% load static %}' '{% block scripts %}' \
  "<script defer src=\"{% static 'web/js/unrelated.js' %}\"></script>" \
  "<script defer src=\"{% static 'web/vendor/kakao_js_sdk/kakao.min.js' %}\"></script>" '{% endblock scripts %}'
OUT=$(run_backstop "$P" --debt-scan --json "$T/d226-consumer.json"); E=$?
assert 'D226e 소비 JS 앞 SDK — 순서 빚' 0 '그 SDK 를 부르는 기능 JS 태그보다 뒤 — static/vendor/kakao_js_sdk/kakao.min.js(앞선: static/js/unrelated.js)' - 0 "$OUT"
assert 'D226f 소비 JS 앞 SDK — PU2 키' 0 'PU2|application/chart/presentation_layer/view/chart_view.html=1' - 0 "$(counts_of "$T/d226-consumer.json")"

echo "fixtures_debt: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
