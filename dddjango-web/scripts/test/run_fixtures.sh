#!/usr/bin/env bash
# dddjango-web 백스톱 픽스처 테스트 (판형: dddart scripts/test/run_fixtures.sh)
# F0 깨끗한 새 트리(blocker 0) / F1 위반 diff(검사 ID 전수 발화) / F2 상대 import web/ 클램핑
# F3 주석·docstring 속 import 불발화 / F4 added 줄 게이트(레거시 면책) / F5 CY1 래칫
# F6 area 하위 BC 골격·테스트·area 직속 파일 / F7 사용 오류 exit 1 / F8 CSS 참조 분류
# F9~F14 검토 r1 고침 막이: #3 NM12 htmx 상태 클래스 · #5 json_field(MD2·IM19) · #8 PJ2 브라운필드 ·
#   #10 최소 root ST4 · #11 NM10 ID 선택자 · #16 --only 검증
# F15·F16 W4 결함 둘: 옛 배치 파일 층 의존 IM 불발화(층 무관 IM25 는 발화) · IM26 조각의 component extends
# 픽스처는 mktemp -d 안의 git 저장소로 만들고 끝나면 지운다(Django 설치 불필요 — 파일 검사기).
set -u
SCRIPTS="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0; FAIL=0

run_backstop() { python3 "$SCRIPTS/backstop.py" "$@" 2>&1; }

assert() { # assert <이름> <기대exit> <출력에 있어야 할 패턴|-> <출력에 없어야 할 패턴|-> <실제exit> <출력>
  local name="$1" wantexit="$2" want="$3" unwant="$4" gotexit="$5" out="$6" ok=1
  [ "$gotexit" != "$wantexit" ] && ok=0
  [ "$want" != "-" ] && ! grep -q -- "$want" <<<"$out" && ok=0
  [ "$unwant" != "-" ] && grep -q -- "$unwant" <<<"$out" && ok=0
  if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS $name"; else
    FAIL=$((FAIL+1)); echo "FAIL $name (exit=$gotexit want=$wantexit)"; echo "$out" | head -30 | sed 's/^/    /'
  fi
}

expect_ids() { # expect_ids <이름> <출력> <ID…> — ID 마다 `[ID] BLOCKER` 가 있는지 하나씩 센다
  local name="$1" out="$2"; shift 2
  local id
  for id in "$@"; do
    if grep -q "^\[$id\] BLOCKER" <<<"$out"; then PASS=$((PASS+1)); echo "PASS $name $id"
    else FAIL=$((FAIL+1)); echo "FAIL $name $id 미발화"; fi
  done
}

G() { git -C "$1" -c user.name=t -c user.email=t@t "${@:2}"; }
commit() { G "$1" add -A; G "$1" commit -qm "${2:-base}"; G "$1" rev-parse HEAD; }
w() { mkdir -p "$(dirname "$1")"; printf '%s\n' "${@:2}" > "$1"; }   # w <파일> <줄…>
markers() { # Python 경로 폴더마다 __init__.py · design_system·static 의 빈 폴더는 .gitkeep
  find "$1/web" -type d ! -path '*/design_system*' ! -path '*/static*' -exec touch {}/__init__.py \;
  find "$1/web" -type d -empty -exec touch {}/.gitkeep \;
}

mkproj() { # mkproj <dir> — web/ 진입 3파일 + git 초기 커밋, BASE 출력
  local p="$1"; mkdir -p "$p/web"
  w "$p/web/__init__.py" ""
  w "$p/web/apps.py" "from django.apps import AppConfig" "" "" "class WebConfig(AppConfig):" '    name: str = "web"'
  w "$p/web/urls.py" "from web.root.router.root_router import urlpatterns" "" "__all__: list[str] = [\"urlpatterns\"]"
  git -C "$p" init -q; commit "$p"
}

mkbc() { # mkbc <proj> <bc경로(web-상대)> — 골격 완비 BC(ST4 통과형)
  local base="$1/web/$2" bc cls k; bc="$(basename "$2")"
  cls="$(printf '%s' "$bc" | awk '{print toupper(substr($0,1,1)) substr($0,2)}')"
  for k in use_case view_model state shared_state service; do mkdir -p "$base/application_layer/$k"; done
  for k in data_source repository service; do mkdir -p "$base/infra_layer/$k"; done
  for k in view section widget ui_extension; do mkdir -p "$base/presentation_layer/$k"; done
  for k in entity value_object enum domain_service specification; do mkdir -p "$base/domain_layer/$bc/$k"; done
  w "$base/ruff.toml" '[lint]' 'select = ["ANN"]'
  w "$base/domain_layer/$bc/$bc.py" "from dataclasses import dataclass" "" "" \
    "@dataclass(frozen=True, slots=True, kw_only=True)" "class $cls:" "    key: str"
}

mkclean() { # mkclean <proj> — 표준 트리 완비 + order BC 실코드(모든 패밀리 무발화 기대)
  local p="$1" W="$1/web" O="$1/web/application/order"
  # root
  w "$W/root/ruff.toml" '[lint]' 'select = ["ANN"]'
  w "$W/root/router/root_router.py" "from django.urls import include, path" "" \
    "from web.application.order import order_router" "" \
    'urlpatterns: list[object] = [path("orders/", include((order_router.urlpatterns, order_router.app_name)))]'
  w "$W/root/scaffold/view/root_view.html" "{% load static %}" "<!doctype html>" "<html>" "<head>" \
    "<link rel=\"stylesheet\" href=\"{% static 'design_system/theme/app_theme.css' %}\">" \
    "<link rel=\"stylesheet\" href=\"{% static 'web/root/root_view.css' %}\">" \
    "<script src=\"{% static 'web/htmx/htmx.min.js' %}\" defer></script>" \
    "</head>" "<body>{% block content %}{% endblock %}</body>" "</html>"
  w "$W/root/scaffold/view_model/root_vm.py" "from web.root.scaffold.state.root_state import RootState" "" "" \
    "class RootVM:" "    def build(self) -> RootState:" '        return RootState(title="shop")' "" "" \
    "def root_context(request: object) -> dict[str, object]:" '    return {"root": RootVM().build()}'
  w "$W/root/scaffold/state/root_state.py" "from dataclasses import dataclass" "" "" \
    "@dataclass(frozen=True, slots=True, kw_only=True)" "class RootState:" "    title: str"
  w "$W/root/handler/root_request_handler.py" "from web.common.network.api_client import ApiClient" "" "" \
    "class RootRequestHandler:" "    def __init__(self, get_response: object) -> None:" \
    "        self.get_response: object = get_response" "        self.client: type[ApiClient] = ApiClient"
  w "$W/root/initializer/root_initializer.py" "from django.template import Library" "" \
    "from web.application.order.presentation_layer.ui_extension import order_status_ui_extension" "" \
    "register: Library = Library()" "register.filters.update(order_status_ui_extension.register.filters)" "" "" \
    "class RootInitializer:" "    ready: bool = True"
  # design_system
  w "$W/design_system/foundation/app_color.css" ":root { --color-primary: #1a73e8; --color-on-primary: #ffffff; }"
  w "$W/design_system/foundation/app_typography.css" ':root { --typography-body: 400 16px/1.5 "Inter", sans-serif; }'
  w "$W/design_system/foundation/app_spacing.css" ":root { --spacing-md: 16px; }"
  w "$W/design_system/foundation/app_radius.css" ":root { --radius-md: 8px; }"
  w "$W/design_system/foundation/app_shadow.css" ":root { --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2); }"
  w "$W/design_system/foundation/app_duration.css" ":root { --duration-fast: 150ms; --easing-standard: ease; }"
  w "$W/design_system/foundation/app_asset.css" ':root { --asset-logo: url("../../static/images/logo.svg"); }'
  w "$W/design_system/theme/app_theme.css" "body { margin: 0; font: var(--typography-body); color: var(--color-primary); }"
  w "$W/design_system/component/button/primary_button.html" '<a class="primary-button" href="{{ href }}">{{ label }}</a>'
  w "$W/design_system/component/button/primary_button.css" \
    ".primary-button { background: var(--color-primary); color: var(--color-on-primary); width: 120px; }" \
    "@media (min-width: 600px) { .primary-button--wide { width: 240px; } }"
  mkdir -p "$W/design_system/util"
  # common
  w "$W/common/network/api_client.py" "from django.test import Client" "" "" \
    "class ApiClient:" "    def get(self, path: str) -> object:" "        return Client(raise_request_exception=False).get(path)"
  w "$W/common/util/either.py" "from dataclasses import dataclass" "from typing import Generic, TypeVar" "" \
    'L = TypeVar("L")' 'R = TypeVar("R")' "" "" \
    "@dataclass(frozen=True, slots=True, kw_only=True)" "class Left(Generic[L]):" "    value: L" "" "" \
    "@dataclass(frozen=True, slots=True, kw_only=True)" "class Right(Generic[R]):" "    value: R" "" "" \
    "Either = Left[L] | Right[R]"
  mkdir -p "$W/common/enum" "$W/common/service"
  # BC order
  mkbc "$p" application/order
  w "$O/order_router.py" "from django.urls import path" "" \
    "from web.application.order.presentation_layer.view.order_list_view import order_list_view" "" \
    'app_name: str = "order"' "" "" "class OrderRoutes:" '    LIST: str = "order:list"' "" "" \
    'urlpatterns: list[object] = [path("", order_list_view, name="list")]'
  w "$O/order_navigator.py" "from django.urls import reverse" "" "" \
    "class OrderNavigator:" "    @staticmethod" "    def list_href() -> str:" \
    "        from web.application.order.order_router import OrderRoutes" "        return reverse(OrderRoutes.LIST)"
  w "$O/domain_layer/order/order.py" "from dataclasses import dataclass" "from typing import Self" "" \
    "from web.application.order.domain_layer.order.entity.order_line import OrderLine" "" "" \
    "@dataclass(frozen=True, slots=True, kw_only=True)" "class Order:" "    order_id: str" "    lines: tuple[OrderLine, ...]" "" \
    "    @classmethod" "    def from_json(cls, data: dict[str, object]) -> Self:" \
    '        return cls(order_id=str(data["id"]), lines=tuple(OrderLine.from_json(x) for x in data["lines"]))'
  w "$O/domain_layer/order/entity/order_line.py" "from dataclasses import dataclass" "from typing import Self" "" "" \
    "@dataclass(frozen=True, slots=True, kw_only=True)" "class OrderLine:" "    sku: str" "" \
    "    @classmethod" "    def from_json(cls, data: dict[str, object]) -> Self:" '        return cls(sku=str(data["sku"]))'
  w "$O/domain_layer/order/value_object/order_date.py" "from dataclasses import dataclass" "from datetime import date" \
    "from typing import Self" "" "" "@dataclass(frozen=True, slots=True, kw_only=True)" "class OrderDate:" "    value: date" "" \
    "    @classmethod" "    def from_api(cls, raw: str) -> Self:" "        if len(raw) != 10:" \
    '            raise ValueError(raw)' "        return cls(value=date.fromisoformat(raw))"
  w "$O/domain_layer/order/enum/order_status.py" "from enum import Enum" "" "" "class OrderStatus(Enum):" '    PAID = "paid"'
  w "$O/domain_layer/order/exception.py" "class OrderNotFound(Exception):" "    pass" "" "" "class OrderClosed(Exception):" "    pass"
  w "$O/application_layer/use_case/get_orders_use_case.py" \
    "from web.application.order.domain_layer.order.order import Order" \
    "from web.application.order.infra_layer.repository.order_repo import OrderRepo" \
    "from web.common.util.either import Either" "" "" \
    "class GetOrdersUseCase:" "    def execute(self) -> Either[str, list[Order]]:" "        return OrderRepo().fetch_all()"
  w "$O/application_layer/view_model/order_list_vm.py" \
    "from web.application.order.application_layer.state.order_list_state import OrderListLoaded, OrderListState" \
    "from web.application.order.application_layer.use_case.get_orders_use_case import GetOrdersUseCase" \
    "from web.application.order.order_navigator import OrderNavigator" "" "" \
    "class OrderListVM:" "    def build(self) -> OrderListState:" "        GetOrdersUseCase().execute()" \
    "        return OrderListLoaded(count=0, more_href=OrderNavigator.list_href())"
  w "$O/application_layer/state/order_list_state.py" "from dataclasses import dataclass" "" "" \
    "@dataclass(frozen=True, slots=True, kw_only=True)" "class OrderListLoaded:" "    count: int" "    more_href: str" "" "" \
    "@dataclass(frozen=True, slots=True, kw_only=True)" "class OrderListEmpty:" "    message: str" "" "" \
    "OrderListState = OrderListLoaded | OrderListEmpty"
  w "$O/infra_layer/data_source/order_data_source.py" "from web.common.network.api_client import ApiClient" "" \
    'ORDERS_PATH: str = "/api/orders/"' "" "" "class OrderDataSource:" "    def fetch(self) -> object:" \
    "        return ApiClient().get(ORDERS_PATH)"
  w "$O/infra_layer/repository/order_repo.py" \
    "from web.application.order.infra_layer.data_source.order_data_source import OrderDataSource" "" "" \
    "class OrderRepo:" "    def fetch_all(self) -> object:" "        return OrderDataSource().fetch()"
  w "$O/presentation_layer/view/order_list_view.py" "from django.http import HttpRequest, HttpResponse" \
    "from django.shortcuts import render" "" \
    "from web.application.order.application_layer.view_model.order_list_vm import OrderListVM" \
    "from web.application.order.order_navigator import OrderNavigator" "" \
    'PAGE: str = "application/order/presentation_layer/view/order_list_view.html"' \
    'SUMMARY: str = "application/order/presentation_layer/section/order_list_summary_section.html"' "" "" \
    "def order_list_view(request: HttpRequest) -> HttpResponse:" '    return render(request, PAGE, {"state": OrderListVM().build()})' "" "" \
    "def order_list_summary_fragment(request: HttpRequest) -> HttpResponse:" \
    '    return render(request, SUMMARY, {"state": OrderListVM().build(), "back": OrderNavigator.list_href()})'
  w "$O/presentation_layer/view/order_list_view.html" '{% extends "root/scaffold/view/root_view.html" %}' "{% load static %}" \
    "{% block content %}" '<section class="order-list">' \
    '  {% include "application/order/presentation_layer/section/order_list_summary_section.html" %}' \
    '  {% include "application/order/presentation_layer/widget/price_tag_widget.html" with amount=state.count %}' \
    '  {% include "design_system/component/button/primary_button.html" with label="more" href=state.more_href %}' \
    '  <button hx-get="{{ state.more_href }}" hx-target="#list">{{ state.count|order_status_class }}</button>' \
    "</section>" \
    "<link rel=\"stylesheet\" href=\"{% static 'web/application/order/order_list_view.css' %}\">" \
    "<script src=\"{% static 'web/vendor/chart/4.4.1/chart.umd.js' %}\" defer></script>" \
    "<script src=\"{% static 'web/js/order_filter.js' %}\" defer></script>" "{% endblock %}"
  w "$O/presentation_layer/section/order_list_summary_section.html" '<div class="order-list-summary">{{ state.count }}</div>'
  w "$O/presentation_layer/widget/price_tag_widget.html" '<span class="price-tag">{{ amount }}</span>'
  w "$O/presentation_layer/ui_extension/order_status_ui_extension.py" "from django.template import Library" "" \
    "from web.application.order.domain_layer.order.enum.order_status import OrderStatus" "" \
    "register: Library = Library()" '_CLASS: dict[OrderStatus, str] = {OrderStatus.PAID: "status-paid"}' "" "" \
    "@register.filter" "def order_status_class(status: OrderStatus) -> str:" "    return _CLASS[status]"
  # static · 테스트 · 선언
  w "$W/static/htmx/htmx.min.js" 'var htmx={version:"2.0.10"};'
  w "$W/static/js/order_filter.js" 'document.addEventListener("htmx:afterSwap", () => {});'
  w "$W/static/vendor/chart/4.4.1/chart.umd.js" "window.Chart = {};"
  w "$W/static/root/root_view.css" '@import url("../../design_system/foundation/app_color.css");' \
    ".root-shell { background: var(--color-primary); }"
  w "$W/static/application/order/order_list_view.css" \
    ".order-list { color: var(--color-primary); font: var(--typography-body); width: 320px; height: 48px; }"
  mkdir -p "$W/static/images"
  w "$p/web_test/application/order/application_layer/order_list_vm_test.py" "def test_order_list_vm_builds() -> None:" "    assert True"
  w "$p/requirements.txt" "Django==5.1.2" "pytest==8.3.3" "pytest-django==4.9.0"
  w "$p/.dddjango-web/backstop-baseline.json" '{"cycle_pairs": []}'
  markers "$p"
}

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# ---------- F0: 깨끗한 새 트리 — 전 패밀리 무발화(거짓양성 반증)
P="$T/f0"; BASE=$(mkproj "$P"); mkclean "$P"
OUT=$(run_backstop "$P" --diff-base "$BASE"); E=$?
assert "F0 깨끗한 새 트리 — blocker 0" 0 "blocker 0건" "BLOCKER" "$E" "$OUT"

# ---------- F1: 위반 diff — 깨끗한 트리를 기준점으로, 패밀리마다 위반을 더해 검사 ID 전수 발화
P="$T/f1"; mkproj "$P" >/dev/null; mkclean "$P"; BASE=$(commit "$P" clean)
W="$P/web"; O="$W/application/order"; A="$O/application_layer"; R="$O/presentation_layer"
# ST
w "$W/models.py" "x: int = 1"                                                  # ST0
w "$W/application/helpers.py" "x: int = 1"                                     # ST1
w "$O/order_utils.py" "x: int = 1"                                             # ST2
w "$O/presenter/__init__.py" ""                                                # ST3
w "$W/application/coupon/presentation_layer/view/coupon_view.py" "def coupon_view(request: object) -> object:" \
  "    from web.application.order.application_layer.use_case.get_orders_use_case import GetOrdersUseCase" \
  "    return GetOrdersUseCase"                                                      # ST4·TG1·CY1(함수 안 import)
w "$O/domain_layer/helper.py" "x: int = 1"                                     # ST5
w "$O/infra_layer/cache/__init__.py" ""                                        # ST6
w "$A/viewmodel/__init__.py" ""                                                # ST7
w "$W/root/root_helper.py" "x: int = 1"                                        # ST8
w "$W/root/handler/error_handler.py" "x: int = 1"                              # ST9
w "$W/design_system/foundation/app_motion.css" ":root { --Motion_Fast: 1s; }"  # ST10·NM11
w "$W/common/provider/__init__.py" ""                                          # ST11
w "$W/static/styles/site.css" "body {}"                                        # ST12
# IM
w "$A/use_case/probe_use_case.py" \
  "from web.root.scaffold.state.root_state import RootState" \
  "from web.application.coupon.infra_layer.repository.coupon_repo import CouponRepo" \
  "from web.application.order.presentation_layer.view.order_list_view import order_list_view" \
  "from django.http import HttpRequest" \
  "from web.design_system.foundation import app_color" \
  "from web.application.order.order_navigator import OrderNavigator" \
  "from .get_orders_use_case import GetOrdersUseCase" \
  "from application.order.models import OrderModel" \
  "import requests" "" "" "class ProbeUseCase:" "    pass"                   # IM2·IM5·IM11·IM12·IM13·IM20·IM24·IM25·IM27
w "$A/view_model/probe_vm.py" "from web.application.order.infra_layer.repository.order_repo import OrderRepo" "" \
  'PATH: str = "/api/orders/"' "" "" "class ProbeVM:" "    pass"                 # IM7·IM27·NM4
w "$A/service/probe_service.py" "from web.application.order.order_navigator import OrderNavigator" "" "" \
  "class ProbeService:" "    def go(self) -> str:" "        return reverse(OrderNavigator.list_href())"  # IM14
w "$W/common/util/probe_util.py" "from web.application.order.order_router import OrderRoutes" "from web import urls" "" "" \
  "class ProbeUtil:" "    pass" "" "" "class Other:" "    pass"                   # IM3·IM15·NM3
w "$W/design_system/component/card/plain_card.html" \
  '{% include "application/order/presentation_layer/section/order_list_summary_section.html" %}'   # IM4
w "$W/design_system/component/card/plain_card.css" ".card-x { width: 1px; }"   # NM12(클래스 접두)
w "$W/design_system/component/card/ds_card.html" "<div></div>"                 # NM12(ds_)
w "$W/root/handler/root_probe_handler.py" "from web.application.order.infra_layer.repository.order_repo import OrderRepo" \
  "" "" "class RootProbeHandler:" "    pass"                                      # IM6
w "$R/ui_extension/probe_ui_extension.py" \
  "from web.application.order.application_layer.state.order_list_state import OrderListState" "" "" \
  "class Mapper:" "    pass" "" "" "def helper() -> str:" '    return ""'          # IM8·NM14
w "$R/widget/probe_widget.html" \
  '{% include "application/order/presentation_layer/section/order_list_summary_section.html" %}'   # IM9
printf '%s\n' "from web.application.order.presentation_layer.view.order_list_view import order_list_view" \
  "from datetime import date" "TODAY: str = date.today().isoformat()" "" "" "def probe() -> None:" \
  "    from web.application.order.domain_layer.order.order import Order" >> "$O/order_navigator.py"  # IM10·IM21(함수 안)·IM23
printf '%s\n' "from web.application.order.order_router import OrderRoutes" >> "$W/apps.py"   # IM16
w "$R/view/probe_view.py" "from django.shortcuts import render" "from django.urls import path, reverse" "" \
  "from web.application.order.infra_layer.repository.order_repo import OrderRepo" \
  "from web.application.order.application_layer.use_case.get_orders_use_case import GetOrdersUseCase" "" \
  'HREF: str = reverse("order:list")' 'urlpatterns: list[object] = [path("x", None)]' "" "" \
  "def helper(request: object) -> object:" '    return render(request, "x.html")'   # IM17·NM9·NM13·NM17·NM18
w "$O/infra_layer/service/probe_service.py" \
  "from web.application.order.application_layer.state.order_list_state import OrderListState" "" "" \
  "class ProbeService:" "    pass"                                             # IM18
w "$O/domain_layer/order/entity/order_note.py" "from django.db import models" "from web.common.util.either import Either" "" "" \
  "class OrderNote:" "    @classmethod" "    def from_json(cls, data: dict[str, object]) -> object:" \
  "        try:" '            return cls(text=data.get("text", ""))' "        except KeyError:" "            return None"  # IM1·IM19·MD1·MD2
printf '%s\n' "from web.application.order.infra_layer.repository.order_repo import OrderRepo" >> "$O/order_router.py"  # IM22
w "$R/section/order_list_extra_section.html" '{% extends "root/scaffold/view/root_view.html" %}'  # IM26(조각 → root_view)
# NM
w "$A/use_case/order_helper.py" "x: int = 1"                                   # NM1
w "$A/state/order_view_state.py" "x: int = 1"                                  # NM2
w "$W/common/service/probe_signal_service.py" "from django.dispatch import receiver" "" "" \
  '@receiver(object())' "def on_saved() -> None:" "    pass"                     # NM8
w "$R/section/stray_section.html" "<div></div>"                                # NM5
w "$R/widget/order_list_badge_widget.html" "<span></span>"                     # NM6
w "$R/section/order_list_color_section.html" '<div style="color: #ff0000; font-size: 14px">x</div>' \
  "<a href=\"{% url 'order:list' %}\">x</a>" '<script src="https://cdn.example.com/x.js"></script>' \
  '<button onclick="go()">x</button>' "{# open" "comment #}" "{{ state.note|safe }}"   # NM10·NM13·PU2·PU3·PU6·PU7
w "$O/domain_layer/order/orders.py" "x: int = 1"                               # NM15
w "$O/infra_layer/repository/probe_repo.py" "from abc import ABC" "" "" "class ProbeRepo(ABC):" "    pass"   # NM16
w "$W/static/application/order/stray.css" ".stray { width: 1px; }"             # NM19
w "$W/static/root/stray_root.css" ".x { width: 1px; }"                        # NM19(root)
w "$R/widget/PriceBadge_widget.html" "<span></span>"                           # NM20
# PJ · PU
w "$P/requirements.txt" "Django==5.1.2" "pytest==8.3.3"                        # PJ1
w "$W/static/js/htmx.min.js" 'var htmx={version:"2.0.10"};'                    # PJ2·PU1(legacy 이름)
w "$W/static/vendor/lodash/lodash.min.js" "window._ = {};"                     # PJ3
w "$R/view/inline.js" "x = 1;"                                                 # PU1
w "$W/static/js/probe_eval.js" 'eval("1 + 1");'                                # PU8
OUT=$(run_backstop "$P" --diff-base "$BASE"); E=$?
assert "F1 위반 diff — exit 2" 2 "blocker" - "$E" "$OUT"
expect_ids "F1" "$OUT" ST0 ST1 ST2 ST3 ST4 ST5 ST6 ST7 ST8 ST9 ST10 ST11 ST12 \
  IM1 IM2 IM3 IM4 IM5 IM6 IM7 IM8 IM9 IM10 IM11 IM12 IM13 IM14 IM15 IM16 IM17 IM18 IM19 IM20 IM21 IM22 IM23 \
  IM24 IM25 IM26 IM27 NM1 NM2 NM3 NM4 NM5 NM6 NM8 NM9 NM10 NM11 NM12 NM13 NM14 NM15 NM16 NM17 NM18 NM19 NM20 \
  CY1 TG1 MD1 MD2 PJ1 PJ2 PJ3 PU1 PU2 PU3 PU6 PU7 PU8
assert "F1 깨끗한 기존 파일 불발화(order_list_view·either)" 2 - 'BLOCKER — web/application/order/presentation_layer/view/order_list_view\|BLOCKER — web/common/util/either' "$E" "$OUT"
assert "F1 함수 안 import 도 IM 이 센다(IM21)" 2 "IM21\] BLOCKER — web/application/order/order_navigator.py:15" - "$E" "$OUT"
assert "F1 NM19 root 조각 CSS" 2 "BLOCKER — web/static/root/stray_root.css" - "$E" "$OUT"
assert "F1 같은 BC router↔navigator 는 순환 아님" 2 - "order ↔ application/order" "$E" "$OUT"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only im5,cy); E=$?
assert "F1 --only 검사ID·패밀리 필터" 2 "IM5" 'IM2\]\|ST0' "$E" "$OUT"

# ---------- F2: 상대 import 클램핑 — 잉여 점이 web/ 루트에서 멈춰 IM7 검출(+IM24)
P="$T/f2"; BASE=$(mkproj "$P")
w "$P/web/application/chat/application_layer/view_model/chat_vm.py" \
  "from ..........common.network.api_client import ApiClient" "" "" "class ChatVM:" "    pass"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only im); E=$?
assert "F2 상대 import web/ 클램핑(IM7)" 2 "IM7" - "$E" "$OUT"
assert "F2 상대 import 금지(IM24)" 2 "IM24" - "$E" "$OUT"

# ---------- F3: 주석·docstring·문자열 속 import — 불발화
P="$T/f3"; BASE=$(mkproj "$P")
w "$P/web/application/chat/domain_layer/chat/entity/msg.py" '"""' "from django.db import models" '"""' \
  "# from django.db import models" 'NOTE: str = "import django"' "" "" "class Msg:" "    pass"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only im); E=$?
assert "F3 주석·docstring 속 import 불발화" 0 - "IM1" "$E" "$OUT"

# ---------- F4: added 줄 게이트 — 레거시 위반 import 불발화, 신규 위반 줄만 발화
P="$T/f4"; mkproj "$P" >/dev/null
w "$P/web/application/chat/domain_layer/chat/entity/old.py" "from django.db import models" "" "" "class Old:" "    pass"
BASE=$(commit "$P" legacy)
echo "# touched" >> "$P/web/application/chat/domain_layer/chat/entity/old.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only im); E=$?
assert "F4a 레거시 위반 import 불발화(added 줄 밖)" 0 - "IM1" "$E" "$OUT"
echo "import django.utils" >> "$P/web/application/chat/domain_layer/chat/entity/old.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only im); E=$?
assert "F4b 신규 위반 줄 발화(IM1)" 2 "IM1" - "$E" "$OUT"

# ---------- F5: CY1 래칫 — 생성→동결→신규 쌍 발화
P="$T/f5"; BASE=$(mkproj "$P")
U="application_layer/use_case"; D="application_layer.use_case"
w "$P/web/application/a/$U/a_use_case.py" "from web.application.b.$D.b_use_case import BUseCase" "class AUseCase:" "    pass"
w "$P/web/application/b/$U/b_use_case.py" "from web.application.a.$D.a_use_case import AUseCase" "class BUseCase:" "    pass"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only cy); E=$?
assert "F5a 베이스라인 자동 생성(exit 0·동결 보고)" 0 "베이스라인 생성" "CY1\] BLOCKER" "$E" "$OUT"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only cy); E=$?
assert "F5b 동결 쌍 면책" 0 - "CY1\] BLOCKER" "$E" "$OUT"
w "$P/web/application/c/$U/c_use_case.py" "from web.application.a.$D.a_use_case import AUseCase" "class CUseCase:" "    pass"
w "$P/web/application/a/$U/a2_use_case.py" "from web.application.c.$D.c_use_case import CUseCase" "class A2UseCase:" "    pass"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only cy); E=$?
assert "F5c 신규 순환 쌍 발화" 2 "CY1" - "$E" "$OUT"

# ---------- F6: area 하위 BC — 골격 완비·web_test/ area 미러면 ST4·TG1 불발화, 미완비 BC 는 BC명으로 발화
P="$T/f6"; BASE=$(mkproj "$P")
mkbc "$P" application/fleet/driver_trip
w "$P/web_test/application/fleet/driver_trip/application_layer/driver_trip_vm_test.py" "def test_x() -> None:" "    assert True"
markers "$P"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only st,tg); E=$?
assert "F6a area BC 골격 완비 — ST/TG 불발화" 0 - 'ST4\|TG1\|ST3\|ST2\|ST1' "$E" "$OUT"
mkdir -p "$P/web/application/fleet/rider_trip/presentation_layer/view"; touch "$P/web/application/fleet/rider_trip/presentation_layer/view/__init__.py"
w "$P/web/application/fleet/ruff.toml" "[lint]"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only st); E=$?
assert "F6b area 하위 미완비 BC — ST4가 BC명(rider_trip)을 지목" 2 'rider_trip' 'fleet` 골격' "$E" "$OUT"
assert "F6c area 직속 ruff.toml — ST1" 2 'ST1\] BLOCKER — web/application/fleet/ruff.toml' - "$E" "$OUT"

# ---------- F8: CSS 참조도 센다 — 조각 CSS 의 타 BC @import 는 IM5(소유자 presentation 자리로 분류)
P="$T/f8"; BASE=$(mkproj "$P")
w "$P/web/static/application/order/order_list_view.css" '@import "../coupon/coupon_view.css";'
OUT=$(run_backstop "$P" --diff-base "$BASE" --only im5); E=$?
assert "F8 조각 CSS 교차 BC @import — IM5" 2 'IM5\] BLOCKER — web/static/application/order/order_list_view.css:1' - "$E" "$OUT"

# ---------- F9 (검토 r1 #3): NM12 — htmx 상태 클래스는 부품 접두와 겹친 복합 선택자에서만 허용
P="$T/f9"; BASE=$(mkproj "$P"); L="$P/web/design_system/component/loading"
w "$L/spinner_loading.html" '<div class="spinner-loading htmx-indicator"></div>'
w "$L/spinner_loading.css" ".spinner-loading.htmx-request { opacity: 1; }" ".spinner-loading.htmx-indicator, .spinner-loading--wide { width: 2px; }"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only nm12); E=$?
assert "F9a 부품 접두 + htmx 상태 클래스 복합 선택자 — NM12 불발화" 0 - "NM12" "$E" "$OUT"
w "$L/bar_loading.html" '<div class="bar-loading"></div>'
w "$L/bar_loading.css" ".htmx-request { opacity: 1; }"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only nm12); E=$?
assert "F9b htmx 상태 클래스 단독 선택자 — NM12 발화" 2 'NM12\] BLOCKER — web/design_system/component/loading/bar_loading.css' - "$E" "$OUT"

# ---------- F10 (검토 r1 #5): 직파싱 json_field — MD2·IM19 불발화, 다른 common import 는 IM19
P="$T/f10"; BASE=$(mkproj "$P"); E10="$P/web/application/chat/domain_layer/chat/entity"
w "$P/web/common/util/json_field.py" "def json_field(data: dict[str, object], key: str, kind: type) -> object:" \
  "    value: object = data[key]" "    if type(value) is not kind:" "        raise TypeError(key)" "    return value"
w "$E10/msg.py" "from dataclasses import dataclass" "from typing import Self" "" "from web.common.util.json_field import json_field" "" "" \
  "@dataclass(frozen=True, slots=True, kw_only=True)" "class Msg:" "    text: str" "" "    @classmethod" \
  "    def from_json(cls, data: dict[str, object]) -> Self:" '        return cls(text=json_field(data, "text", str))'
OUT=$(run_backstop "$P" --diff-base "$BASE" --only md,im19); E=$?
assert "F10a json_field 직파싱 — MD2·IM19 불발화" 0 - "MD2\|IM19" "$E" "$OUT"
w "$E10/note.py" "from web.common.util.either import Either" "" "" "class Note:" "    pass"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only im19); E=$?
assert "F10b json_field 밖 common import — IM19 발화" 2 'IM19\] BLOCKER — web/application/chat/domain_layer/chat/entity/note.py' 'msg.py' "$E" "$OUT"

# ---------- F11 (검토 r1 #8): PJ2 — 브라운필드 기존 core 는 판이 달라도·둘이어도 불발화, 새 core 를 더하면 발화
P="$T/f11"; mkproj "$P" >/dev/null
w "$P/web/static/htmx/htmx.min.js" 'var htmx={version:"1.9.12"};'
w "$P/web/static/js/htmx.min.js" 'var htmx={version:"1.9.12"};'
BASE=$(commit "$P" legacy)
echo "/* touched */" >> "$P/web/static/htmx/htmx.min.js"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only pj2); E=$?
assert "F11a 브라운필드 기존 core(1.9.12·둘) — PJ2 불발화" 0 - "PJ2" "$E" "$OUT"
w "$P/web/static/js/htmx.js" 'var htmx={version:"2.0.10"};'
OUT=$(run_backstop "$P" --diff-base "$BASE" --only pj2); E=$?
assert "F11b 새 core 추가 — PJ2 이중 설치 발화" 2 'PJ2\] BLOCKER — web/static/js/htmx.js' - "$E" "$OUT"

# ---------- F12 (검토 r1 #10): 기준점 뒤 별도 커밋으로 더한 최소 root — 골격 폴더·ruff.toml 이 빠지면 ST4 발화
P="$T/f12"; BASE=$(mkproj "$P")
w "$P/web/root/router/root_router.py" 'urlpatterns: list[object] = []'
w "$P/web/root/scaffold/view/root_view.html" "<html></html>"
markers "$P"; commit "$P" minimal-root >/dev/null
OUT=$(run_backstop "$P" --diff-base "$BASE" --only st4); E=$?
assert "F12 최소 root(커밋 뒤) — ST4 발화(ruff.toml·handler 누락)" 2 'ST4\] BLOCKER — web/root$' - "$E" "$OUT"
assert "F12 누락 목록에 ruff.toml·handler·view_model" 2 'handler/.*ruff.toml\|ruff.toml.*handler/' - "$E" "$OUT"

# ---------- F13 (검토 r1 #11): NM10 — CSS ID 선택자는 색 리터럴이 아니다, 선언 값의 hex 만 발화
P="$T/f13"; BASE=$(mkproj "$P"); mkdir -p "$P/web/application/order/presentation_layer/view"
w "$P/web/static/application/order/order_list_view.css" "#add { color: var(--color-primary); }" "#fab .order-list:hover { width: 1px; }"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only nm10); E=$?
assert "F13a ID 선택자 #add·#fab — NM10 불발화" 0 - "NM10" "$E" "$OUT"
echo ".order-list { border: 1px solid #add; }" >> "$P/web/static/application/order/order_list_view.css"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only nm10); E=$?
assert "F13b 선언 값의 hex — NM10 발화(3행)" 2 'NM10\] BLOCKER — web/static/application/order/order_list_view.css:3' 'css:1\|css:2' "$E" "$OUT"

# ---------- F14 (검토 r1 #16): --only 의 없는 패밀리·검사 ID — exit 1, 아는 값은 실행
P="$T/f14"; BASE=$(mkproj "$P")
OUT=$(run_backstop "$P" --diff-base "$BASE" --only typo); E=$?
assert "F14a 없는 패밀리 typo — exit 1" 1 "알 수 없는 --only 값 typo" - "$E" "$OUT"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only st,nm7,pu4); E=$?
assert "F14b 비운 번호 nm7·pu4 — exit 1" 1 "nm7, pu4" - "$E" "$OUT"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only ST4,im,PU8); E=$?
assert "F14c 아는 패밀리·검사 ID(대소문자 무관) — 실행" 0 "blocker 0건" - "$E" "$OUT"

# ---------- F15 (W4 결함 1): 표준 트리 밖 옛 배치 파일 = 층 판정 불가 레거시 — 층 의존 IM 불발화 · 층 무관 IM(IM25) 발화
# 원본: <S>/w4/a f89fa1af5 web/chart/chart/section/chart_app_bar.html · web/design_system/component/bar/app_bar.html (복사만)
P="$T/f15"; mkproj "$P" >/dev/null; LG="$P/web/chart/chart"
w "$LG/section/chart_app_bar.html" "{# legacy #}"
w "$LG/view/chart_view.py" "x: int = 1"
BASE=$(commit "$P" legacy)
mkdir -p "$P/web/design_system/component/bar"
cat > "$P/web/design_system/component/bar/app_bar.html" <<'TPL'
{% comment %}
  AppBar — 화면 상단 바(iconsOnly · transparent). leading 슬롯에 back(plain IconButton)을 glass 캡슐로 감싼다.
{% endcomment %}
<header class="app-bar{% block app_bar_classes %}{% endblock app_bar_classes %}">
  <div class="app-bar__lead">
    {% block app_bar_leading %}
    {% include "design_system/component/button/icon_button.html" with icon="chevron-left" label=back_label|default:"이전" size="md" href=back_href hx_get=back_hx_get hx_target=back_hx_target hx_swap=back_hx_swap only %}
    {% endblock app_bar_leading %}
  </div>
  {% block app_bar_actions %}{% endblock app_bar_actions %}
</header>
TPL
cat > "$LG/section/chart_app_bar.html" <<'TPL'
{% extends "design_system/component/bar/app_bar.html" %}

{% comment %}
  chart_app_bar — 공용 iconsOnly AppBar를 chart 전용 modifier로 확장한다. 뒤로는 plain md 링크이며,
  chart 모드의 저장·공유는 표시-비활성(aria-disabled · href·핸들러·JS 훅·tabindex 0)이다.
{% endcomment %}

{% block app_bar_classes %} chart-app-bar{% endblock app_bar_classes %}

{% block app_bar_leading %}
  {% include "design_system/component/button/icon_button.html" with icon="chevron-left" label="뒤로" size="md" href=state.back_url only %}
{% endblock app_bar_leading %}

{% block app_bar_actions %}
  {% if state.mode == "chart" %}
    <div class="app-bar__actions chart-app-bar__actions">
      <span class="icon-button icon-button--md" role="button" aria-disabled="true" aria-label="저장하기">
        <i class="icon-download" aria-hidden="true"></i>
      </span>
      <span class="icon-button icon-button--md" role="button" aria-disabled="true" aria-label="공유하기">
        <i class="icon-share-2" aria-hidden="true"></i>
      </span>
    </div>
  {% endif %}
{% endblock app_bar_actions %}
TPL
OUT=$(run_backstop "$P" --diff-base "$BASE" --only im); E=$?
assert "F15a 옛 배치 파일의 design_system extends·include — IM13·IM26 불발화" 0 - "BLOCKER" "$E" "$OUT"
printf '%s\n' "from application.chart.models import Chart" "from web.design_system.foundation import app_color" >> "$LG/view/chart_view.py"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only im); E=$?
assert "F15b 옛 배치 파일의 백엔드 import — IM25 발화" 2 'IM25\] BLOCKER — web/chart/chart/view/chart_view.py:2' 'IM13' "$E" "$OUT"

# ---------- F16 (W4 결함 2): IM26 — 조각은 design_system component extends(block 채우기)만 · 페이지는 root_view.html 만
P="$T/f16"; BASE=$(mkproj "$P"); RP="$P/web/application/chart/presentation_layer"
mkdir -p "$RP/section"; cp "$T/f15/web/chart/chart/section/chart_app_bar.html" "$RP/section/chart_app_bar_section.html"
OUT=$(run_backstop "$P" --diff-base "$BASE" --only im26); E=$?
assert "F16a section 이 component extends(W4 원본) — IM26 불발화" 0 - "IM26" "$E" "$OUT"
w "$RP/section/chart_shell_section.html" '{% extends "root/scaffold/view/root_view.html" %}'
w "$RP/view/chart_view.html" '{% extends "design_system/component/bar/app_bar.html" %}'
w "$RP/view/chart_detail_view.html" '{% extends "root/scaffold/view/root_view.html" %}'
OUT=$(run_backstop "$P" --diff-base "$BASE" --only im26); E=$?
assert "F16b section 이 root_view extends — IM26 발화" 2 'IM26\] BLOCKER — web/application/chart/presentation_layer/section/chart_shell_section.html' - "$E" "$OUT"
assert "F16c 페이지가 component extends — IM26 발화 · 페이지 → root_view 불발화" 2 'IM26\] BLOCKER — web/application/chart/presentation_layer/view/chart_view.html' 'chart_detail_view' "$E" "$OUT"

# ---------- F7: 사용 오류 — exit 1(미실행은 통과가 아니다)
OUT=$(run_backstop --help); E=$?
assert "F7a 알 수 없는 옵션 --help → exit 1" 1 "사용 오류" - "$E" "$OUT"
OUT=$(run_backstop); E=$?
assert "F7b 대상 없음 → exit 1" 1 "사용:" - "$E" "$OUT"
mkdir -p "$T/noweb"
OUT=$(run_backstop "$T/noweb"); E=$?
assert "F7c web/ 없음 → exit 1" 1 "web/ 없음" - "$E" "$OUT"
OUT=$(run_backstop "$T/f0" --diff-base deadbeef); E=$?
assert "F7d 해석 불가 기준점 → exit 1" 1 "해석 불가" - "$E" "$OUT"

echo ""
echo "결과: PASS $PASS / FAIL $FAIL"

# ---------- 추출 도구 픽스처(v1.3.1 판 그대로 — 도구가 byte 동일): 시안 절단 3종 · 계약 절단
SUB=0
OUT=$(bash "$(dirname "$0")/fixtures_extract.sh" 2>&1) || SUB=1; echo "$OUT" | tail -1
OUT=$(bash "$(dirname "$0")/fixtures_contract.sh" 2>&1) || SUB=1; echo "$OUT" | tail -1
[ $FAIL = 0 ] && [ $SUB = 0 ]
