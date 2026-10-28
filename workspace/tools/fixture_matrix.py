#!/usr/bin/env python3
"""전수 fixture 실측표 — 검사기 × 위반 fixture × 기대/실측 exit (5번 계획 Phase 4-3).

「백스톱 실측 0」(5차 리뷰 최대 발견)의 종결 장치: 검사기마다 자기 위반
fixture 에서 exit 2 가 나는지를 전수로 실측하고 표로 남긴다. eval v5 는
FROZEN 이므로 실측은 이 fixture 결정 레인만 쓴다.

케이스: skeleton 7 + 기존 15종×2 + API-error 3종×2(--error-profile auto)
       + 신설 8종×2 + checker_lint 2 + 호출 계약 27 + 수정 사이클 레인 3×2 + 음성 · 양성 단독 레인
       = exit 대조 116 + 줄 대조 14(GROUP_CASES — 아래) = 130(실행 표 끝 «케이스» 줄이 실측이다).

의미 묶음 줄 대조(2.28.0 · #654~#656 · 설계 7.4): exit 만 보는 레인은 ⓓ 후보 줄(exit 불산입)과
줄 글자(#656 주어)를 못 본다 — 이 레인은 거름 규칙의 줄 전부를 글자 그대로 기대와 대조한다.
같은 틀로 위반 픽스처에 더한 줄도 고정한다 — F4-126(#647 시험 본문 · 별칭) · #658(루트 시험 폴더).
`--mutation` 은 설계 7.4 고침을 하나씩 옛 코드로 되돌린 사본(MUTATIONS)에서 이 레인을 돌려
변이마다 한 줄 이상 어긋나는지(죽는지) 본다.

호출 계약 레인(라운드 1 P2 — 2026-08-12): TARGET 에 «BC 폴더»를 주면 검사기가
«표준 미채택 clean(exit 0)»으로 조용히 통과하던 사각을 고정한다 — BC 모양
TARGET 은 사용 오류 exit 1 이어야 한다(child_settings 라운드에서 파이프라인이
정확히 이 호출로 V1 트리를 전부 green 처리했다).

사용: python3 workspace/tools/fixture_matrix.py [--emit <md 경로>]
      python3 workspace/tools/fixture_matrix.py --mutation
exit 0 = 전수 일치(변이는 모두 죽음) / exit 2 = 불일치 존재(변이 생존) / exit 1 = 재료 결손.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
S: Path = ROOT / "dddjango" / "scripts"
F: Path = ROOT / "workspace" / "eval" / "fixtures"
TOOLS: Path = ROOT / "workspace" / "tools"

PLAIN_PAIRS: "list[tuple[str, str]]" = [
    ("check-context-isolation.py", "context_isolation"),
    ("check-usecase-dto-placement.py", "usecase_dto"),
    ("check-mechanism-ownership.py", "mechanism_ownership"),
    ("check-synthetic-infra-exc.py", "synthetic_infra_exc"),
    ("check-ninja-boundary-middleware.py", "ninja_boundary_middleware"),
    ("check-transient-overmapping.py", "transient_overmapping"),
    ("check-idempotency-scope-creep.py", "idempotency_scope_creep"),
    ("check-common-container.py", "common_container"),
    ("check-app-container.py", "app_container"),
    ("check-public-surface-annotation.py", "public_surface"),
    ("check-choices-literal-consumption.py", "choices_literal"),
    ("check-test-config.py", "test_config"),
    ("check-response-schema-bypass.py", "response_schema_bypass"),
    ("check-composition-root.py", "composition_root"),
    ("check-db-table.py", "db_table"),
    ("check-transaction-boundary.py", "transaction_boundary"),
    ("check-event-publish.py", "event_publish"),
    ("check-broker-contract.py", "broker_contract"),
    ("check-missable-entrance.py", "missable_entrance"),
    ("check-naming.py", "naming"),
    ("check-domain-model.py", "domain_model"),
    ("check-business-vocabulary.py", "business_vocabulary"),
    ("check-port-adapter-pairing.py", "port_adapter_pairing"),
]
AUTO_PAIRS: "list[tuple[str, str]]" = [
    ("check-error-centralization.py", "error_centralization"),
    ("check-api-error-controller-contract.py", "api_error_controller"),
    ("check-openapi-error-declaration.py", "openapi_error_declaration"),
]
# 라운드 1′ 수정 사이클 레인(2026-08-12) — 검사기 «행동 변화» 고정용 추가 쌍.
# PLAIN_PAIRS 와 분리한 이유: 그 목록은 registry 27종 로스터의 재료(bc_registry_run
# import·호출 계약 레인)라 같은 검사기의 중복 등재가 로스터 assert 를 깨뜨린다.
EXTRA_LANES: "list[tuple[str, str]]" = [
    ("check-test-config.py", "test_config_entrance"),
    ("check-event-publish.py", "event_publish_leaf"),
    ("check-db-table.py", "db_table_choices"),
    # S2 F-B(2026-08-14) — #210 도메인 예외 면제: good=실선언 예외 클래스 직접 catch(구판 red→신판 green) ·
    # bad_rules=예외 칸 세탁 2종(함수 import·__init__ 재수출)은 계속 red.
    ("check-usecase-dto-placement.py", "usecase_dto_domain_exception"),
]

# Z-3A false-positive regression lanes. These fixtures express deliberate
# non-adoption or a domain meaning that shares a suffix with boundary DTOs.
NEGATIVE_LANES: "list[tuple[str, str, str]]" = [
    ("check-broker-contract.py", "broker_contract", "no_adoption"),
    ("check-composition-root.py", "composition_root", "no_api"),
    ("check-usecase-dto-placement.py", "usecase_dto", "no_api"),
    # F4-86 — REST BC 안의 창구 전용 영역도 응용 영역의 짝이다.
    ("check-usecase-dto-placement.py", "usecase_dto", "ohs_only_area"),
    ("check-naming.py", "naming", "domain_results"),
    # 결정 2(2026-09-04) — 내용 없는 골격 파일(skeleton_placeholder)은 내용 규칙(#219·#635)의 대상이 아니다.
    ("check-port-adapter-pairing.py", "port_adapter_pairing", "skeleton_placeholder"),
    ("check-usecase-dto-placement.py", "usecase_dto", "skeleton_placeholder"),
    # F4-92 — `event` 는 기술 낱말(불용어)이다: 영역이 `OrderPlacedEvent`·`shipment_event.py` 같은 이름을 가져도
    # broker(#518 — 봉투 `event_id`)·framework 계약(#47·#617)이 그 낱말을 쓰는 것은 clean.
    ("check-broker-contract.py", "broker_contract", "event_kind_word"),
    ("check-business-vocabulary.py", "business_vocabulary", "event_kind_word"),
    # F4-92 «받아들인 한계» — 바라는 동작이 아니라 선언한 한계의 고정이다: `event` 를 업무 명사로 쓰는 영역
    # (`EventBooking`)을 framework 가 `event_id`·`event_name` 꼴로만 알면 이 검사기는 못 잡는다(exit 0 — 따로 보게 하는 규칙도 없다).
    ("check-business-vocabulary.py", "business_vocabulary", "event_noun_leak_limit"),
]

POSITIVE_LANES: "list[tuple[str, str, str]]" = [
    ("check-usecase-dto-placement.py", "usecase_dto", "registrar_only"),
    ("check-usecase-dto-placement.py", "usecase_dto", "orphan_area"),
    ("check-usecase-dto-placement.py", "usecase_dto", "api_only_area"),
    # F4-92 가드 — 위 한계의 경계: 같은 영역의 다른 업무 낱말(`booked` — 폴더 이름에는 없는 낱말)이 `event` 와 함께
    # 새면 그 낱말로 계속 잡는다.
    ("check-business-vocabulary.py", "business_vocabulary", "event_noun_leak_guard"),
    # F4-92 가드 — 같은 칸 낱말 `entity`·`object` 와 복수형 `events` 는 불용어가 아니다(현장 근거 없음): 영역 낱말이면
    # 그 낱말 하나로 잡는다(낱말마다 픽스처 하나 — 레인은 exit 만 본다).
    ("check-business-vocabulary.py", "business_vocabulary", "entity_word_guard"),
    ("check-business-vocabulary.py", "business_vocabulary", "object_word_guard"),
    ("check-business-vocabulary.py", "business_vocabulary", "events_word_guard"),
]


# 로스터 단일 출처 대조(2026-08-12 P3′) — 쌍 목록이 checker_registry 와 어긋나면 재료 결손.
sys.path.insert(0, str(S))
from checker_registry import REGISTRY  # noqa: E402

_pairs_roster: "dict[str, bool]" = {"check-layer-skeleton.py": False}
_pairs_roster.update({s: False for s, _ in PLAIN_PAIRS})
_pairs_roster.update({s: True for s, _ in AUTO_PAIRS})
assert _pairs_roster == {name: auto for name, auto in REGISTRY}, (
    "fixture 쌍 목록이 checker_registry 로스터와 어긋난다"
)


# 사본에만 만드는 캐시만 남은 폴더(`.gitignore` 가 `__pycache__/` 를 빼므로 저장소에 둘 수 없다 — 설계 7.4 의 20).
RUNTIME_CACHE: "dict[str, tuple[str, ...]]" = {
    "skeleton/good_grouped": (
        "application/orders/domain_layer/shared_value_object/removed/__pycache__/gone.cpython-39.pyc",
        "application/orders/domain_layer/domain_service/pricing/old/__pycache__/gone.cpython-39.pyc",
    ),
    "composition_root/bad_rules": (
        "application/orders/domain_layer/order/value_object/stale/__pycache__/stale_amount.cpython-39.pyc",
    ),
}

_D: str = "application/orders/domain_layer/"
_PO: str = "application/orders/application_layer/order/place_order/"
_M647: str = ("값 자리가 `{v}` 다 — 키가 정해진 값 묶음은 `TypedDict`(파싱한 JSON 은 `TypeAdapter` 검증 파싱)"
              " · 조회표는 `dict[K, 구체 V]` · 통과 값은 `JsonValue`")
_LEAK: str = " — 반환·속성에 남은 `object` 는 좁히지 않은 누수다"
_ALL: str = ""
_M652: str = (
    "wiring_material.py 는 결선 재료만 둔다 — `from application.orders.domain_layer.{m} import {c}` 는 허용 import 셋"
    "(`from __future__ import annotations` · `from django.conf import settings` · 자기 BC 값 객체 모듈의 클래스) 밖이다(F2)"
)

# (라벨, 검사기, fixture, 거름(줄에 search 하는 정규식 · 빈 글 = 모든 줄), 기대 줄) — 기대는 리터럴(고침 번호는 설계 7.4).
GROUP_CASES: "list[tuple[str, str, str, str, tuple[str, ...]]]" = [
    # 19 · 20 — 묶음 · C2 · 묶음 안 승격 · 캐시만 남은 폴더(부모 · 묶음 안)는 0 줄.
    ("skeleton/good_grouped", "check-layer-skeleton.py", "skeleton/good_grouped", _ALL, ()),
    # #654 · #655 · 16(파일 폐쇄) · 15(서비스 묶음 안 파일 · 묶음 안 승격 부품 ⓓ#644).
    ("skeleton/bad_grouped", "check-layer-skeleton.py", "skeleton/bad_grouped", _ALL, (
        f"[#654] {_D}shared_value_object/address/nested: 묶음 안 폴더 — 묶음은 한 계층이다(서비스 칸 묶음 안 승격만 파일 하나로 센다)",
        f"[#654] {_D}domain_service/pricing/tiers: 묶음 안 폴더 — 묶음은 한 계층이다(서비스 칸 묶음 안 승격만 파일 하나로 센다)",
        f"[#655] {_D}order/value_object/money/__init__.py: 묶음 폴더에 `__init__.py` 가 없다 — 비워 둔다(0바이트 · docstring · 주석뿐)",
        f"[#655] {_D}order/event/placed/__init__.py: 묶음 `__init__.py` 는 내용이 없다 — 0바이트 · docstring · 주석뿐(재수출 · 코드를 두지 않는다)",
        f"[#490] {_D}order/exception/payment/notes.txt: 묶음 안 파일이 부모 칸의 파일 모양이 아니다 — 트리에 없는 경로",
        f"[ⓓ#644] {_D}domain_service/pricing/quote_price.py: 행위 칸 실현 201행(>200) — 캐스케이드 판정 의무 (트리 75행)"
        " — 물음: 역할 밖 응집 단위가 있는가 — ①이동/②동명 폴더 승격/③유지 (houserules §1 캐스케이드)",
        f"[ⓓ#644] {_D}domain_service/pricing/discount_rule/discount_step.py: 행위 칸 승격 부품 201행(>200) — 캐스케이드 판정 의무 (트리 75행)"
        " — 물음: 역할 밖 응집 단위가 있는가 — ①이동/②동명 폴더 승격/③유지 (houserules §1 캐스케이드)",
    )),
    # 1 ~ 9 · 22 · 25 · #656 — 묶음 · 평평한 상대 import(25)가 있는 맞는 트리는 0 줄.
    ("domain_model/good", "check-domain-model.py", "domain_model/good", _ALL, ()),
    # 놓침 회귀(묶음 안 위반) · #459 걷음(22) · #656 네 줄 꼴(설계 7.3) · 상대 import 거짓 위반 걷힘(25).
    ("domain_model/bad_rules", "check-domain-model.py", "domain_model/bad_rules",
     r"^\[(ⓓ)?#(260|264|267|276|290|298|308|459|542|547|656)\]", (
        f"[#260] {_D}order/entity/order_line_entity.py:4: `OrderLine` 에 식별자(id·*_id) 필드가 없다 — entity/ 판정은 «식별자를 갖고 값이 바뀌어도 같은 것인가»다(#259)",
        f"[#260] {_D}order/entity/order_line_entity.py:9: `LineNote` 에 식별자(id·*_id) 필드가 없다 — entity/ 판정은 «식별자를 갖고 값이 바뀌어도 같은 것인가»다(#259)",
        f"[#260] {_D}shipment/entity/parcel/parcel_box.py:4: `ParcelBox` 에 식별자(id·*_id) 필드가 없다 — entity/ 판정은 «식별자를 갖고 값이 바뀌어도 같은 것인가»다(#259)",
        f"[#264] {_D}order/value_object/money.py:12: `set_amount` 에서 self.amount 대입 — 값 객체는 불변이다(__init__ 밖 자기 속성 대입 금지)",
        f"[#264] {_D}order/value_object/tax/tax_rate.py:15: `set_value` 에서 self.value 대입 — 값 객체는 불변이다(__init__ 밖 자기 속성 대입 금지)",
        f"[#267] {_D}order/value_object/money.py: 공개 클래스 2개 — 값 객체 하나 = 파일 하나다",
        f"[#267] {_D}shared_value_object/tariff/tariff_rate.py: 공개 클래스 2개 — 값 객체 하나 = 파일 하나다",
        f"[#276] {_D}order/event/order_placed.py:10: 이벤트에 메서드 `as_dict` — 필드만 있는 자료구조다",
        f"[#276] {_D}order/event/refund/refund_issued.py:10: 이벤트에 메서드 `describe` — 필드만 있는 자료구조다",
        f"[#290] {_D}ledger/exception/errors.py: 한 파일에 예외 2개 — 깨진 불변식 하나 = 파일 하나다",
        f"[#290] {_D}ledger/exception/posting/posting_failed.py: 한 파일에 예외 2개 — 깨진 불변식 하나 = 파일 하나다",
        f"[#298] {_D}shared_value_object/percent.py:3: shared_value_object 가 `application.orders.domain_layer.order.order` 를 import 한다 — 같은 폴더 안과 exception 모듈 말고는 아무것도 import 하지 않는다",
        f"[#298] {_D}shared_value_object/tariff/tariff_zone.py:5: shared_value_object 가 `application.orders.domain_layer.order.order` 를 import 한다 — 같은 폴더 안과 exception 모듈 말고는 아무것도 import 하지 않는다",
        f"[#308] {_D}domain_service/order_pricing_service.py:17: `can_refund` 이 bool 을 돌려준다 — 규칙 위반의 알림은 «도메인 예외»다",
        f"[#308] {_D}domain_service/tariff/check_order_tariff.py:7: `check_order_tariff` 이 bool 을 돌려준다 — 규칙 위반의 알림은 «도메인 예외»다",
        f"[#308] {_D}domain_service/tariff/split_order_tariff/split_order_tariff.py:9: `split_order_tariff` 이 bool 을 돌려준다 — 규칙 위반의 알림은 «도메인 예외»다",
        "[#542] application/orders/application_layer/order/place_order/place_order_use_case.py:16: 유스케이스가 도메인 이벤트 `OrderPlaced` 를 지어낸다 — 사실은 «애그리거트»가 상태를 바꾼 그 메서드 안에서 기록한다",
        "[#542] application/orders/application_layer/order/refund_order/refund_order_use_case.py:10: 유스케이스가 도메인 이벤트 `RefundIssued` 를 지어낸다 — 사실은 «애그리거트»가 상태를 바꾼 그 메서드 안에서 기록한다",
        f"[#656] {_D}shared_value_object/__init__.py: 묶음 `meter/` 을(를) 만든다",
        f"[#656] {_D}shared_value_object/legacy/__init__.py: 묶음 `legacy/` 을(를) 푼다",
        f"[#656] {_D}shared_value_object/tariff/percent_cap.py: 부모에 둔다",
        f"[#656] {_D}shared_value_object/tariff_fee.py: 묶음 `tariff/` 에 둔다",
        f"[ⓓ#547] {_D}order/order.py: 엔티티 3개 + 무제한 컬렉션 필드 — 루트가 비대하다 — 물음: 이 둘이 «동시에» 일어나면 업무가 정말 막아야 하나",
        f"[ⓓ#547] {_D}shipment/shipment.py: 엔티티 4개 + 무제한 컬렉션 필드 — 루트가 비대하다 — 물음: 이 둘이 «동시에» 일어나면 업무가 정말 막아야 하나",
        "[ⓓ#547] application/orders: `order_repository` 를 여러 <area>/ ['billing_area', 'order'] 가 쓴다 — 경계가 너무 묶였을 신호다(트랜잭션을 늘리지 말고 «경계를 쪼갠다») — 물음: 서로 다른 일을 하는 두 사용자가 이 경계로 충돌하나",
    )),
    # 11(#30 종류는 묶음 위 칸) · 12(#44 묶음 안 · 승격 본체 · 주어 실제 경로) · 13(C2 는 승격 면제 없음 — #41 · #481).
    ("naming/bad_rules", "check-naming.py", "naming/bad_rules", r"^\[#(30|41|44|481)\]", (
        f"[#30] {_D}order/value_object/money_value_object.py: `_value_object` 재접미 — 폴더가 종류를 말하는 자리표시자 자리(`<value_object>.py`)는 접미사를 달지 않는다(가르는 자는 「이름이 곧 서술문인가」 — D41)",
        f"[#30] {_D}order/value_object/tax/tax_rate_value_object.py: `_value_object` 재접미 — 폴더가 종류를 말하는 자리표시자 자리(`<value_object>.py`)는 접미사를 달지 않는다(가르는 자는 「이름이 곧 서술문인가」 — D41)",
        "[#41] application/orders/application_layer/port/email_port: Port·Adapter·Gateway 는 폴더 이름에 나오지 않는다 — 파일이 접미사로 종류를 진다(`<capability>_port.py`)",
        f"[#41] {_D}shared_value_object/harbor_port: Port·Adapter·Gateway 는 폴더 이름에 나오지 않는다 — 파일이 접미사로 종류를 진다(`<capability>_port.py`)",
        f"[#44] {_D}domain_service/levy/levy_code.py: 도메인 서비스 `levy_code` 이 같은 BC 의 값 객체와 겹친다 — 행위 이름으로 짓는다(`settle_turn` 처럼)",
        f"[#44] {_D}domain_service/levy/levy_rate/levy_rate.py: 도메인 서비스 `levy_rate` 이 같은 BC 의 값 객체와 겹친다 — 행위 이름으로 짓는다(`settle_turn` 처럼)",
        f"[#44] {_D}domain_service/refund.py: 도메인 서비스 `refund` 이 같은 BC 의 값 객체와 겹친다 — 행위 이름으로 짓는다(`settle_turn` 처럼)",
        f"[#44] {_D}domain_service/tax_band.py: 도메인 서비스 `tax_band` 이 같은 BC 의 값 객체와 겹친다 — 행위 이름으로 짓는다(`settle_turn` 처럼)",
        f"[#481] {_D}order/event/event_stream: 자식 폴더가 부모 `event/` 의 낱말을 반복한다 — 파일의 접두·접미 반복(#30·#568)만 정상이다",
        "[#481] application/orders/driving_layer/open_host_service/contract/request/request_contract: 자식 폴더가 부모 `request/` 의 낱말을 반복한다 — 파일의 접두·접미 반복(#30·#568)만 정상이다",
    )),
    # 10 — 이벤트 묶음 안 사실 이름.
    ("event_publish/bad_rules", "check-event-publish.py", "event_publish/bad_rules", r"^\[(ⓓ)?#271\]", (
        f"[#271] {_D}order/event/stock/reduce_stock.py:7: 사실 이름 `ReduceStock` 의 첫 토큰이 애그리거트 공개 메서드 `reduce` 와 같다 — 이벤트는 명령이 아니라 과거형 사실이다(ReduceInventory ✗ → OrderPlaced ✓)",
        "[#271] application/orders/published_event/bad_fact.py:9: 사실 이름 `ReduceOrder` 의 첫 토큰이 애그리거트 공개 메서드 `reduce` 와 같다 — 이벤트는 명령이 아니라 과거형 사실이다(ReduceInventory ✗ → OrderPlaced ✓)",
        f"[ⓓ#271] {_D}order/event/order_archive.py:7: 사실 이름 `OrderArchive` 의 끝 토큰 `archive` 이 과거형이 아니다 — 물음: 이 이름이 «이미 일어난 사실»을 말하나",
        "[ⓓ#271] application/orders/published_event/bad_fact.py:17: 사실 이름 `OrderShipment` 의 끝 토큰 `shipment` 이 과거형이 아니다 — 물음: 이 이름이 «이미 일어난 사실»을 말하나",
    )),
    # 14 — 이벤트가 묶음 안에만 있어도 반쪽 채택.
    ("port_adapter_pairing/bad_rules", "check-port-adapter-pairing.py", "port_adapter_pairing/bad_rules", r"^\[ⓓ#545\]", (
        "[ⓓ#545] application/orders/driven_layer/adapter/persistence/repository/shelf_repository.py:10: `shelf` 는 event/ 만 있고 루트 pending 상태/API 가 없다 — 가드 대상이 없어 준수 불능(반쪽 채택) — 물음: 이벤트 채택을 완성할 것인가, event/ 를 걷어낼 것인가",
        "[ⓓ#545] application/orders/driven_layer/adapter/persistence/repository/tray_repository.py:10: `tray` 는 event/ 만 있고 루트 pending 상태/API 가 없다 — 가드 대상이 없어 준수 불능(반쪽 채택) — 물음: 이벤트 채택을 완성할 것인가, event/ 를 걷어낼 것인가",
    )),
    # 23 — 결선 재료가 묶음 안 값 객체 모듈(길이 4 · 3)을 들인다.
    ("composition_root/good", "check-composition-root.py", "composition_root/good", _ALL, ()),
    # 23 반례 — 가운데가 실제 묶음이 아니면(없는 폴더 · 캐시만 남은 폴더) · 두 칸이면 그대로 F2 밖.
    ("composition_root/bad_rules", "check-composition-root.py", "composition_root/bad_rules",
     r"^\[#652\] .*(ghost_|\.stale\.|\.limit\.)", tuple(
        f"[#652] application/orders/composition_root/wiring_material.py:{n}: " + _M652.format(m=m, c=c)
        for n, m, c in ((141, "order.value_object.ghost_limit.limit_amount", "GhostLimitAmount"),
                        (142, "order.value_object.stale.stale_amount", "StaleAmount"),
                        (143, "shared_value_object.ghost_locale.locale_tag", "GhostLocaleTag"),
                        (144, "order.value_object.limit.extra.limit_amount", "DeepLimitAmount")))),
    # 24 — 예외 칸 묶음 안 실선언 예외 클래스는 면제.
    ("usecase_dto_domain_exception/good", "check-usecase-dto-placement.py", "usecase_dto_domain_exception/good", _ALL, ()),
    # 24 반례(Goodhart ⑴) — 애그리거트 예외 칸의 묶음이 아닌 한 칸 · 두 칸은 그대로 #210.
    ("usecase_dto_domain_exception/bad_rules", "check-usecase-dto-placement.py", "usecase_dto_domain_exception/bad_rules",
     r"^\[#210\]", tuple(
        "[#210] application/orders/driving_layer/api/order/order_controller.py: 컨트롤러는 `<use_case>_result` 만 보고 "
        f"응답을 만든다 — `application.orders.domain_layer.{m}` 로 도메인을 들여다본다(예외 면제는 같은 BC `exception/` 직계 · "
        "그 묶음 한 칸 안 모듈의 실선언 예외 클래스뿐 — #95)"
        for m in ("domain_service.exception.fee.fee_rejected", "order.exception.order_not_payable",
                  "order.exception.payment.card.card_declined", "order.exception"))),
    # 26 — #291 · #292 새 문면.
    ("context_isolation/bad_rules", "check-context-isolation.py", "context_isolation/bad_rules",
     r"^\[#29[12]\] application/[a-z_]+/domain_layer/", (
        f"[#291] {_D}exception.py: BC 바로 밑 `domain_layer/exception.py` 를 두지 않는다 — 도메인 예외의 자리는 애그리거트 밑 `exception/` 과 공유 개념의 `shared_value_object/` 둘이다(#657)",
        "[#292] application/billing/domain_layer/exception: 예외의 자리는 넷으로 갈린다 — 한 애그리거트 업무 규칙은 `domain_layer/<aggregate>/exception/` · 여러 애그리거트가 함께 쓰는 개념은 `shared_value_object/`(#657) · 남에게 공개하는 실패는 OHS `contract/exception/` · 바깥 행위자는 `port/<capability>/exception.py` 다",
    )),
    # F4-126 — 시험 본문은 #647 차단만(주석 없는 지역 변수 · 반환 타입 없는 시험 함수 · assert 는 줄 없음) · 모듈 수준 별칭은 펼쳐 같은 자리로.
    ("public_surface/bad_rules", "check-public-surface-annotation.py", "public_surface/bad_rules",
     r"(/test/|record_alias_leak\.py)", (
        f"[#647] {_PO}record_alias_leak.py:7: `payload_of()` 반환 타입의 {_M647.format(v='object')}{_LEAK}",
        f"[#647] {_PO}record_alias_leak.py:11: `snapshot_of()` 반환 타입의 {_M647.format(v='object')}{_LEAK}",
        f"[#647] application/orders/test/unit/test_record_leak.py:4: `_session_state()` 반환 타입의 {_M647.format(v='object')}{_LEAK}",
        f"[#647] application/orders/test/unit/test_record_leak.py:9: `state` 주석의 {_M647.format(v='Any')}",
    )),
    # #658 — 루트 시험 폴더 파일 · 루트 시험 import 는 파일마다 한 줄(빈 `tests/__init__.py` · `tests/web/` 은 줄 없음).
    ("test_config/bad_rules", "check-test-config.py", "test_config/bad_rules", r"^\[#658\]", (
        "[#658] application/orders/test/unit/test_root_helper.py: 저장소 루트 시험 폴더(`tests` · `test` 패키지)를 import 한다"
        " — 필요한 fixture · 도우미는 이 시험의 표준 자리(`test/conftest.py` · `test/fake/`)에 새로 쓴다",
        "[#658] tests/helpers.py: 저장소 루트 시험 폴더 — 시험은 주인의 표준 시험 자리(BC `test/` · 전역 규칙은 `framework/test/unit/`)에 둔다",
    )),
]

# 설계 7.4 고침을 하나씩 옛 코드로 되돌린 변이(+ 계획 단계 2 의 둘) — (이름, 파일, 옛 글, 새 글, 돌릴 검사기).
_SK: str = "check-layer-skeleton.py"
_DM: str = "check-domain-model.py"
_NM: str = "check-naming.py"
_EP: str = "check-event-publish.py"
_PA: str = "check-port-adapter-pairing.py"
_CR: str = "check-composition-root.py"
_UC: str = "check-usecase-dto-placement.py"
_CI: str = "check-context-isolation.py"
MUTATIONS: "list[tuple[str, str, str, str, str]]" = [
    ("19 묶음 허용 칸 하위 폴더를 recognize 로 가르지 않음", _SK,
     'if kan_row is not None and getattr(kan_row, "groupable", False):', "if kan_row is not None and False:", _SK),
    ("19 묶음 안 승격을 알아보지 않음", _SK,
     'if kind == "promotion":\n            if (group / (sd.name', 'if False:\n            if (group / (sd.name', _SK),
    ("20 부모의 캐시만 폴더 면제 걷음", _SK,
     'kind = folder_group.recognize(p, kan_row.r)\n            if kind == "cache":\n                continue\n',
     'kind = folder_group.recognize(p, kan_row.r)\n', _SK),
    ("20 묶음 안 캐시만 폴더 면제 걷음", _SK,
     'kind = folder_group.recognize(sd, crow.r)\n        if kind == "cache":\n            continue\n',
     'kind = folder_group.recognize(sd, crow.r)\n', _SK),
    ("15 서비스 묶음 안 파일 ⓓ#644 걷음", _SK,
     "if crow.r in PROMO_ACTION_ROWS:\n            n = _phys_lines(f)", "if False:\n            n = _phys_lines(f)", _SK),
    ("16 묶음 안 파일 폐쇄 걷음", _SK,
     "if not any(_file_pattern_ok(f.name, pat) for pat in file_patterns):", "if False:", _SK),
    ("#654 줄 걷음", _SK, 'out.add("#654", sd,', '(lambda *a: None)("#654", sd,', _SK),
    ("#655 없음 줄 걷음", _SK, "if not init.is_file():\n        out.add(\"#655\"", "if False:\n        out.add(\"#655\"", _SK),
    ("#655 «docstring · 주석뿐»을 0 바이트만으로", _SK,
     "elif not checker_target.skeleton_placeholder(init):", "elif init.stat().st_size != 0:", _SK),
    ("1 shared 값 객체 파일을 직계 glob 으로", _DM,
     'for py in folder_group.group_members(shared, "*.py", promotable=False):\n                _check_value_object_file',
     'for py in sorted(shared.glob("*.py")):\n                _check_value_object_file', _DM),
    ("2 shared import 검사를 직계 glob 으로", _DM,
     'for py in folder_group.group_members(shared, "*.py", promotable=False):\n        mod = _parse(py)',
     'for py in sorted(shared.glob("*.py")):\n        mod = _parse(py)', _DM),
    ("3 예외 칸을 직계 glob 으로", _DM, 'folder_group.group_members(exc_dir, "*.py", promotable=False)',
     'sorted(exc_dir.glob("*.py"))', _DM),
    ("4 엔티티 칸을 직계 glob 으로", _DM, 'folder_group.group_members(ent_dir, "*.py", promotable=False)',
     'sorted(ent_dir.glob("*.py"))', _DM),
    ("5 값 객체 칸을 직계 glob 으로", _DM, 'folder_group.group_members(vo_dir, "*.py", promotable=False)',
     'sorted(vo_dir.glob("*.py"))', _DM),
    ("6 이벤트 칸을 직계 glob 으로", _DM, 'folder_group.group_members(ev_dir, "*.py", promotable=False)',
     'sorted(ev_dir.glob("*.py"))', _DM),
    ("7 서비스 칸을 slot_glob 으로", _DM, 'folder_group.group_members(ds, "*.py", promotable=True)',
     'checker_target.slot_glob(ds, "*.py")', _DM),
    ("7 서비스 묶음 안 승격 본체를 빼고", _DM, 'folder_group.group_members(ds, "*.py", promotable=True)',
     'folder_group.group_members(ds, "*.py", promotable=False)', _DM),
    ("8 응용 쪽 이벤트 클래스를 */event/*.py 로", _DM,
     'for py in [e for d in sorted(domain.iterdir()) if d.is_dir()\n                   for e in folder_group.group_members(d / "event", "*.py", promotable=False)]:\n            mod = _parse(py)',
     'for py in domain.glob("*/event/*.py"):\n            mod = _parse(py)', _DM),
    ("9 #547 엔티티 셈을 직계만", _DM,
     'folder_group.group_members(agg / "entity", "*.py", promotable=False)',
     '((agg / "entity").glob("*.py") if (agg / "entity").is_dir() else [])', _DM),
    ("22 shared 하위 폴더 #459 되살림", _DM,
     '        _check_group_places(root, bc, f)\n        shared = domain / "shared_value_object"\n        if shared.is_dir():\n',
     '        _check_group_places(root, bc, f)\n        shared = domain / "shared_value_object"\n        if shared.is_dir():\n'
     '            for p in sorted(shared.iterdir()):\n                if p.is_dir() and p.name != "__pycache__":\n'
     '                    f.add("#459", _rel(root, p), "shared_value_object/ 하위 폴더 — 파일 규칙은 애그리거트 안 값 객체와 '
     '똑같고 다른 것은 «사는 폴더»뿐이다")\n', _DM),
    ("25 #298 상대 import 를 모듈 글자 그대로", _DM,
     "m = _absolute_module(package, node.level, node.module)", 'm = node.module or ""', _DM),
    ("#656 줄 걷음", _DM, 'f.add("#656", where, msg)', "pass", _DM),
    ("#656 «만든다» 주어를 부모 __init__ 대신 첫 파일로", "folder_group.py",
     'out.append((f"{parent}/__init__.py", MAKE.format(g)))',
     'out.append((min(p for p, fp in placement.files.items() if fp.member.slot.parent == parent and fp.group == g), '
     'MAKE.format(g)))', _DM),
    ("#656 «푼다» 주어를 묶음 __init__ 대신 첫 파일로", "folder_group.py",
     'return init if init in inside else (inside[0] if inside else f"{parent}/{g}/")',
     'return next((q for q in inside if not q.endswith("/__init__.py")), f"{parent}/{g}/")', _DM),
    ("10 이벤트 이름 검사를 */event/*.py 로", _EP,
     'for py in [e for d in sorted(domain.iterdir()) if d.is_dir()\n                   for e in folder_group.group_members(d / "event", "*.py", promotable=False)]:',
     'for py in sorted(domain.glob("*/event/*.py")):', _EP),
    ("11 #30 종류를 부모 폴더 그대로", _NM, "parent = _kind_folder(root, py)", "parent = py.parent.name", _NM),
    ("12 #44 값 객체를 직계 glob 으로", _NM, 'for p in folder_group.group_members(v, "*.py", promotable=False)',
     'for p in sorted(v.glob("*.py"))', _NM),
    ("12 #44 서비스를 slot_glob 으로", _NM,
     'folder_group.group_members(domain / "domain_service", "*.py", promotable=True)',
     'checker_target.slot_glob(domain / "domain_service", "*.py")', _NM),
    ("12 #44 서비스 묶음 안 승격 본체를 빼고", _NM,
     'folder_group.group_members(domain / "domain_service", "*.py", promotable=True)',
     'folder_group.group_members(domain / "domain_service", "*.py", promotable=False)', _NM),
    ("12 #44 주어를 domain_service/<이름>.py 고정으로", _NM, 'f.add("#44", _rel(root, py),',
     'f.add("#44", _rel(root, domain / "domain_service" / f"{py.stem}.py"),', _NM),
    ("13 동명 폴더면 승격(#41 · #481 면제)", _NM, "promoted = _promoted(root, d)",
     'promoted = (d / f"{name}.py").is_file() or checker_target.adapter_bundle(d)', _NM),
    ("14 이벤트 채택을 직계 파일만", _PA,
     'event_adopted = any(  # 묶음 안 이벤트 파일도 센다(#654~#656)\n'
     '        p.stem != "__init__" for p in folder_group.group_members(event_dir, "*.py", promotable=False))',
     'event_adopted = event_dir.is_dir() and any(\n'
     '        p.suffix == ".py" and p.stem != "__init__" for p in event_dir.iterdir())', _PA),
    ("23 결선 재료 값 객체 모듈 길이 3 · 2 고정", _CR,
     'if len(rest) in (3, 4) and rest[1] == "value_object":', 'if len(rest) == 3 and rest[1] == "value_object":', _CR),
    ("23 결선 재료 shared 길이 2 고정", _CR,
     'elif len(rest) in (2, 3) and rest[0] == "shared_value_object":',
     'elif len(rest) == 2 and rest[0] == "shared_value_object":', _CR),
    ("23 가운데 칸이 실제 묶음인지 안 봄", _CR,
     'if hit is None or not group.is_dir() or folder_group.recognize(group, hit[0].row) != "group":',
     "if False:", _CR),
    ("23 가운데 칸을 폴더 있음만으로(캐시만 남은 폴더 통과)", _CR,
     'if hit is None or not group.is_dir() or folder_group.recognize(group, hit[0].row) != "group":',
     "if hit is None or not group.is_dir():", _CR),
    ("24 예외 import 길이 6 고정", _UC, "if len(parts) not in (6, 7) or", "if len(parts) != 6 or", _UC),
    ("24 길이 7 이 애그리거트 예외 칸 묶음인지 안 봄", _UC,
     "if hit is None or hit[0].row != row or len(hit[1]) != 2 or not group.is_dir() \\\n"
     '                or folder_group.recognize(group, row) != "group":',
     "if not group.is_dir():", _UC),
    ("24 길이 상한 걷음(두 칸 통과)", _UC, "if len(parts) not in (6, 7) or", "if len(parts) < 6 or", _UC),
    ("26 #291 옛 문면", _CI,
     "도메인 예외의 자리는 애그리거트 밑 `exception/` 과 공유 개념의 `shared_value_object/` 둘이다(#657)",
     "도메인 예외의 표준 자리는 애그리거트 밑 하나뿐이다", _CI),
    ("26 #292 옛 문면", _CI,
     "예외의 자리는 넷으로 갈린다 — 한 애그리거트 업무 규칙은 `domain_layer/<aggregate>/exception/` · 여러 애그리거트가 "
     "함께 쓰는 개념은 `shared_value_object/`(#657) · 남에게 공개하는 실패는 OHS `contract/exception/` · 바깥 행위자는 "
     "`port/<capability>/exception.py` 다",
     "예외의 자리는 셋으로 갈린다 — 업무 규칙 위반은 `domain_layer/<aggregate>/exception/` 이다", _CI),
]


def build_cases() -> "list[tuple[str, list[str], str, int]]":
    """(라벨, argv, fixture 상대경로, 기대 exit)"""
    cases: list[tuple[str, list[str], str, int]] = []
    sk = "check-layer-skeleton.py"
    for sub, want in (("good_bc", 0), ("bad_legacy_flat", 2), ("bad_missing", 2),
                      ("good_promoted", 0), ("bad_promoted", 2), ("good_grouped", 0), ("bad_grouped", 2)):
        fx = F / "skeleton" / sub
        cases.append((f"skeleton/{sub}", [sys.executable, str(S / sk), str(fx)], f"skeleton/{sub}", want))
    for script, fixture in PLAIN_PAIRS:
        for sub, want in (("good", 0), ("bad_rules", 2)):
            fx = F / fixture / sub
            cases.append((f"{fixture}/{sub}", [sys.executable, str(S / script), str(fx)], f"{fixture}/{sub}", want))
    for script, fixture, sub in NEGATIVE_LANES:
        fx = F / fixture / sub
        cases.append(
            (f"{fixture}/{sub}", [sys.executable, str(S / script), str(fx)], f"{fixture}/{sub}", 0))
    for script, fixture, sub in POSITIVE_LANES:
        fx = F / fixture / sub
        cases.append((f"{fixture}/{sub}", [sys.executable, str(S / script), str(fx)], f"{fixture}/{sub}", 2))
    for script, fixture in AUTO_PAIRS:
        for sub, want in (("good", 0), ("bad_rules", 2)):
            fx = F / fixture / sub
            cases.append(
                (f"{fixture}/{sub} (auto)",
                 [sys.executable, str(S / script), str(fx), "--error-profile", "auto"],
                 f"{fixture}/{sub}", want)
            )
    for script, fixture in EXTRA_LANES:
        for sub, want in (("good", 0), ("bad_rules", 2)):
            fx = F / fixture / sub
            cases.append((f"{fixture}/{sub}", [sys.executable, str(S / script), str(fx)], f"{fixture}/{sub}", want))
    for sub, want in (("good", 0), ("bad_rules", 2)):
        fx = F / "checker_lint" / sub
        cases.append(
            (f"checker_lint/{sub}",
             [sys.executable, str(TOOLS / "checker_lint.py"), "--scripts-dir", str(fx)],
             f"checker_lint/{sub}", want)
        )
    # selector(scope) 모드 레인(2026-08-15 S3-r2′ 수정 사이클) — composition 의
    # «ROOT_API_CONSTRUCTORS 직접 상속 로컬 클래스 팩토리» 인식 행동 고정.
    # good=직접 생성 기준선(exit 0) · bad_rules=subclass 팩토리는 분석이 «진행»돼
    # #437 위반으로 열거된다(exit 2 — 구판은 exit 1 분석 불능이라 앵커 차분 격리가
    # 불가능했다) · bad_usage=비상속 로컬 클래스 팩토리는 여전히 분석 불능(exit 1 —
    # 닫힌 허용 목록이 열리지 않았음 실증).
    comp_selector_args = [
        "--error-profile", "dddjango-code-json", "--scope", "public-v1",
        "--api-module", "config/api.py", "--urlconf-module", "config/urls.py",
        "--registrar-module", "application/lesson/driving_layer/api/api_router.py",
    ]
    for sub, want in (("good", 0), ("bad_rules", 2), ("bad_usage", 1)):
        fx = F / "composition_selector" / sub
        cases.append(
            (f"composition_selector/{sub} (selector)",
             [sys.executable, str(S / "check-composition-root.py"), str(fx), *comp_selector_args],
             f"composition_selector/{sub}", want)
        )
    # 호출 계약 레인 — TARGET=BC 폴더(층 폴더 직계 보유)는 clean 이 아니라 사용 오류다.
    bc_dir = F / "skeleton" / "good_bc" / "application" / "orders"
    for script in [sk] + [s for s, _ in PLAIN_PAIRS]:
        cases.append((f"invocation/{script}", [sys.executable, str(S / script), str(bc_dir)], "skeleton/good_bc(orders)", 1))
    for script, _ in AUTO_PAIRS:
        cases.append(
            (f"invocation/{script} (auto)",
             [sys.executable, str(S / script), str(bc_dir), "--error-profile", "auto"],
             "skeleton/good_bc(orders)", 1)
        )
    return cases


def _copy_fixture(src: Path, dest: Path, rel: str) -> None:
    shutil.copytree(src, dest)
    for cache in RUNTIME_CACHE.get(rel, ()):
        target: Path = dest / cache
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"\0")


_LINE: "re.Pattern[str]" = re.compile(r"^\s*\[(?:ⓓ)?(#\d+)\]\s")


def run_lines(scripts: Path, checker: str, fixture: str) -> "tuple[int, list[str], str]":
    """검사기를 fixture 사본에 돌려 (exit, 규칙 줄(사본 접두를 뗀 것), stderr 끝)."""
    env: "dict[str, str]" = dict(os.environ)
    env.pop("DJR_FINDINGS_JSON", None)
    with tempfile.TemporaryDirectory() as td:
        tmp_fx: Path = Path(td) / "fixture"
        _copy_fixture(F / fixture, tmp_fx, fixture)
        prefixes: "list[str]" = sorted({str(tmp_fx) + "/", str(tmp_fx.resolve()) + "/"}, key=len, reverse=True)
        proc = subprocess.run([sys.executable, str(scripts / checker), str(tmp_fx)], cwd=str(ROOT),
                              capture_output=True, text=True, env=env)
    out: "list[str]" = []
    for ln in proc.stdout.splitlines():
        if _LINE.match(ln):
            text: str = ln.strip()
            for pre in prefixes:
                text = text.replace(pre, "")
            out.append(text)
    return proc.returncode, out, proc.stderr.strip()[-300:]


def check_group_case(scripts: Path, case: "tuple[str, str, str, str, tuple[str, ...]]") -> "list[str]":
    label, checker, fixture, keep, want = case
    code, got, err = run_lines(scripts, checker, fixture)
    if code not in (0, 2):
        return [f"{label}: exit {code} — {err}"]
    picked: "list[str]" = sorted(ln for ln in got if re.search(keep, ln))
    expected: "list[str]" = sorted(want)
    if picked == expected:
        return []
    return ([f"{label}: 빠진 줄 {ln}" for ln in expected if ln not in picked]
            + [f"{label}: 남는 줄 {ln}" for ln in picked if ln not in expected])


def mutation(scripts: Path) -> int:
    """MUTATIONS 를 사본에 하나씩 — 돌릴 검사기의 줄 대조 레인 하나 이상이 어긋나야(죽어야) green."""
    survived: "list[str]" = [] if MUTATIONS else ["변이 표가 비었다"]

    def one(item: "tuple[str, str, str, str, str]") -> "tuple[str, str]":
        name, file, old, new, checker = item
        src: str = (scripts / file).read_text(encoding="utf-8")
        if src.count(old) != 1:
            return name, f"변이 지점이 정확히 한 곳이 아니다({src.count(old)}) — 변이 표를 코드에 맞춰라"
        cases = [c for c in GROUP_CASES if c[1] == checker]
        if not cases:
            return name, f"{checker} 의 줄 대조 레인이 없다"
        with tempfile.TemporaryDirectory(prefix="fm-mutant-") as tmp:
            copy: Path = Path(tmp) / "scripts"
            shutil.copytree(scripts, copy, symlinks=False, ignore=shutil.ignore_patterns("__pycache__"))
            (copy / file).write_text(src.replace(old, new, 1), encoding="utf-8")
            for case in cases:
                if check_group_case(copy, case):
                    return name, ""
        return name, "변이가 살아남음(줄 대조 레인이 못 잡는다)"

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 2)) as pool:
        for name, why in pool.map(one, MUTATIONS):
            if why:
                survived.append(f"{name}: {why}")
            else:
                print(f"  죽음 {name}")
    if survived:
        print(f"[fixture_matrix --mutation] 생존 변이 {len(survived)}건", file=sys.stderr)
        for s in survived:
            print(f"  {s}", file=sys.stderr)
        return 2
    print(f"[fixture_matrix --mutation] 변이 {len(MUTATIONS)}종 모두 죽음 — 줄 대조 레인 검출력 확인")
    return 0


def main(argv: "list[str]") -> int:
    if argv[:1] == ["--mutation"]:
        return mutation(S)
    emit: "Path | None" = None
    if argv[:1] == ["--emit"]:
        if len(argv) < 2:
            print("사용: fixture_matrix.py [--emit <md 경로>]", file=sys.stderr)
            return 1
        emit = Path(argv[1])
    cases = build_cases()
    for _, cmd, fx_rel, _w in cases:
        if not Path(cmd[1]).is_file():
            print(f"재료 결손: {cmd[1]} 없음", file=sys.stderr)
            return 1
        fx_path = cmd[3] if cmd[2] == "--scripts-dir" else cmd[2]
        if not Path(fx_path).is_dir():
            print(f"재료 결손: fixture {fx_rel} 없음", file=sys.stderr)
            return 1

    lines: list[str] = [
        "| 검사기 | fixture | 기대 | 실측 | 판정 |",
        "|---|---|---|---|---|",
    ]
    mismatch: int = 0
    for label, cmd, _fx, want in cases:
        # fixture 는 git 밖 «임시 사본»으로 실행한다(hermetic) — 저장소 안 원본을 직접 주면
        # 검사기의 git/touched 인식이 커밋 상태에 따라 결과를 바꾼다(2026-08-12 release 게이트
        # 실측: fixture 가 untracked 일 땐 «신규»로 발화했는데 커밋 직후 tracked-무변이 되자
        # touched 슬라이스가 0건 — 임시 사본은 비-git이라 «전 후보 검사» fail-closed 레인을 탄다).
        fx_i: int = 3 if cmd[2] == "--scripts-dir" else 2
        with tempfile.TemporaryDirectory() as td:
            tmp_fx: Path = Path(td) / "fixture"
            _copy_fixture(Path(cmd[fx_i]), tmp_fx, _fx)
            run_cmd: list[str] = list(cmd)
            run_cmd[fx_i] = str(tmp_fx)
            # 사용자 환경의 DJR_FINDINGS_JSON 을 상속하면 이 하네스가 사용자의 실제
            # 레코드 파일에 테스트 레코드를 append 한다(T2-1 적대 검증 레인 S 7번 —
            # checker_baseline_matrix 판형). exit 만 재는 도구이므로 sink 를 아예 끊는다.
            env: "dict[str, str]" = dict(os.environ)
            env.pop("DJR_FINDINGS_JSON", None)
            got: int = subprocess.run(run_cmd, cwd=str(ROOT), stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL, env=env).returncode
        ok: bool = got == want
        if not ok:
            mismatch += 1
        checker: str = Path(cmd[1]).name if "--scripts-dir" not in cmd else "checker_lint.py"
        lines.append(f"| `{checker}` | {label} | {want} | {got} | {'✓' if ok else '✗ 불일치'} |")
    for case in GROUP_CASES:
        problems = check_group_case(S, case)
        if problems:
            mismatch += 1
            for pr in problems:
                print(f"  ✗ {pr}", file=sys.stderr)
        lines.append(f"| `{case[1]}` | {case[0]} (줄 대조) | 줄 {len(case[4])} | "
                     f"{'같음' if not problems else '다름'} | {'✓' if not problems else '✗ 불일치'} |")
    total: int = len(cases) + len(GROUP_CASES)
    summary: str = f"케이스 {total} · 일치 {total - mismatch} · 불일치 {mismatch}"
    table: str = "\n".join(lines)
    print(table)
    print(summary)
    if emit is not None:
        emit.write_text(
            "# 전수 fixture 실측표 — 검사기 × 위반 fixture × exit\n\n"
            f"생성: {date.today().isoformat()} · `workspace/tools/fixture_matrix.py` 실행 산출물"
            "(손으로 고치지 않는다 — 재실행으로 재생성).\n\n"
            "「백스톱 실측 0」(5차 리뷰)의 종결 기록 — 검사기마다 자기 위반 fixture 에서 exit 2.\n"
            "eval v5 FROZEN — 실측은 이 fixture 결정 레인만.\n\n"
            f"{table}\n\n{summary}\n",
            encoding="utf-8",
        )
        print(f"실측표 기록: {emit}")
    return 0 if mismatch == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
