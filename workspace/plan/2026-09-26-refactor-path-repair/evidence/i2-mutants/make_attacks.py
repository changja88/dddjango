"""R8-I2 적대 리뷰 — 새 세탁 공격(R*)과 흔한 리팩토링 모양(G*) 탐침.

바탕 = diag-D2 `c_domain_seed_inline` 트리(진단 탐침과 같은 바탕). 도메인 ActionKind 에 리뷰 전용 메서드를 붙이고
(진단 탐침 메서드와 이름이 겹치지 않는다) 클래스 수준 공격은 별도 모듈로 둔다. 트리마다 유스케이스 1개.
기대: red = 조회된(받은) 인스턴스가 원소로 샌다 · green = 원소가 도메인 본문에서 새로 태어난다 ·
lim = 이상은 red 지만 설계상 가정 밖(문서화 대상) · fc = 이상은 green 이지만 fail-closed red 수용 후보.
"""
from __future__ import annotations

import shutil
import textwrap
from pathlib import Path

DOM = "application/orders/domain_layer/action_kind"
UC = "application/orders/application_layer/action_kind"

HEADER_EXTRA = '''import copy
import dataclasses
import operator
from collections.abc import Iterator
from typing import ClassVar

stash: list["ActionKind"] = []
picked: "ActionKind | None" = None


def _pick(kinds: Sequence["ActionKind"]) -> None:
    global picked
    picked = kinds[0]


def _launder2(fn: object) -> object:
    return fn


class _Grabber:
    def __init__(self, kinds: Sequence["ActionKind"]) -> None:
        self._kinds = kinds

    def __radd__(self, other: list["ActionKind"]) -> list["ActionKind"]:
        other.extend(self._kinds)
        return other

    def __eq__(self, other: object) -> bool:
        if isinstance(other, list):
            other.extend(self._kinds)
        return False

    __hash__ = None  # type: ignore[assignment]
'''

METHODS = '''
    _CACHE: ClassVar[dict[str, "ActionKind"]] = {}

    @classmethod
    def rv_for(cls, code: str) -> ActionKind:
        return cls(code=code, name=code)

    @classmethod
    def rv_adopt(cls, kinds: Sequence[ActionKind]) -> None:
        for kind in kinds:
            cls._CACHE[kind.code] = kind
        stash.extend(kinds)
        _pick(kinds)

    # ── 복제 계열 ──
    @classmethod
    def rc_type_call(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return tuple(type(k)(code=k.code, name=k.name) for k in kinds)

    @classmethod
    def rc_dunder_class(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return tuple(k.__class__(code=k.code, name=k.name) for k in kinds)

    @classmethod
    def rc_copy_copy(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return tuple(copy.copy(k) for k in kinds)

    @classmethod
    def rc_vars_splat(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return tuple(cls(**vars(k)) for k in kinds)

    @classmethod
    def rc_asdict(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return tuple(cls(**dataclasses.asdict(k)) for k in kinds)

    @classmethod
    def rc_shared_dict(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = []
        for k in kinds:
            fresh: ActionKind = object.__new__(cls)
            fresh.__dict__ = k.__dict__
            items.append(fresh)
        return tuple(items)

    # ── 누적 우회 ──
    @classmethod
    def ra_extend_iter(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.rv_for(c) for c in codes]
        items.extend(iter(kinds))
        return items

    @classmethod
    def ra_iadd_tuple(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.rv_for(c) for c in codes]
        items += tuple(kinds)
        return items

    @classmethod
    def ra_setitem_dunder(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.rv_for(c) for c in codes]
        items.__setitem__(slice(0, 0), kinds)
        return items

    @classmethod
    def ra_operator_iadd(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.rv_for(c) for c in codes]
        operator.iadd(items, kinds)
        return items

    @classmethod
    def ra_default_arg_alias(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls.rv_for(c) for c in codes]

        def grow(acc: list[ActionKind] = items) -> None:
            acc.extend(kinds)

        grow()
        return tuple(items)

    @classmethod
    def ra_literal_alias(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls.rv_for(c) for c in codes]
        [items][0].extend(kinds)
        return tuple(items)

    @classmethod
    def ra_set_update_genexp(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        items: set[ActionKind] = set()
        items.update(k for k in kinds)
        return tuple(items)

    @classmethod
    def ra_radd_grabber(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls.rv_for(c) for c in codes]
        _ = items + _Grabber(kinds)
        return tuple(items)

    @classmethod
    def ra_eq_grabber(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls.rv_for(c) for c in codes]
        if _Grabber(kinds) == items:
            pass
        return tuple(items)

    @classmethod
    def ra_scope_acc(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        def _unused() -> None:
            stash: list[ActionKind] = []  # noqa: F841

        return tuple(stash)

    @classmethod
    def ra_scope_elem(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        class _Shadow:
            picked = cls.rv_for("x")

        return tuple(picked for _ in codes)

    @classmethod
    def ra_loop_alias_acc(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls.rv_for(c) for c in codes]
        for acc in (items,):
            acc.extend(kinds)
        return tuple(items)

    # ── return 경로 ──
    @classmethod
    def rr_finally_return(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        try:
            return tuple(cls.rv_for(c) for c in codes)
        finally:
            return tuple(kinds)  # noqa: B012

    @classmethod
    def rr_except_return(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        try:
            fresh: tuple[ActionKind, ...] = tuple(cls.rv_for(c) for c in codes)
        except ValueError:
            return tuple(kinds)
        return fresh

    @classmethod
    def rr_walrus_return(cls, kinds: Sequence[ActionKind]) -> list[ActionKind]:
        return (got := list(kinds))

    @classmethod
    def rr_match_return(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        match codes:
            case []:
                return tuple(kinds)
            case _:
                return tuple(cls.rv_for(c) for c in codes)

    @classmethod
    def rr_map_identity(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return tuple(map(lambda k: k, kinds))

    # ── 원소 출처 ──
    @classmethod
    def re_cache_setdefault(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls._CACHE.setdefault(c, cls(code=c, name=c)) for c in codes)

    @classmethod
    def re_selector_delegate(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return cls.enabled_among(kinds)

    @classmethod
    def rv_pick_first(cls, kinds: Sequence[ActionKind]) -> ActionKind:
        return kinds[0] if kinds else cls(code="", name="")

    @classmethod
    def re_scalar_selector(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return (cls.rv_pick_first(kinds),)

    @classmethod
    def re_reconcile_boolop(cls, existing: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        by_code: dict[str, ActionKind] = {k.code: k for k in existing}
        return tuple(by_code.get(c) or cls(code=c, name=c) for c in codes)

    @classmethod
    def re_nested_nonlocal_elem(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        item: ActionKind = cls.rv_for("x")

        def swap() -> None:
            nonlocal item
            item = kinds[0]

        swap()
        return (item,)

    @_launder2
    @classmethod
    def rd_outer_decorator(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls.rv_for(c) for c in codes)

    @classmethod
    def twin_batch(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return tuple(kinds)

    # ── 흔한 리팩토링 모양(이상 green 또는 fc) ──
    @classmethod
    def g_enumerate(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls(code=c, name=str(i)) for i, c in enumerate(codes))

    @classmethod
    def g_zip(cls, codes: Sequence[str], names: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls(code=c, name=n) for c, n in zip(codes, names))

    @classmethod
    def g_dict_values(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple({c: cls(code=c, name=c) for c in codes}.values())

    @classmethod
    def g_sorted_fresh(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(sorted((cls(code=c, name=c) for c in codes), key=lambda k: k.code))

    @classmethod
    def g_map_factory(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(map(cls.rv_for, codes))

    @classmethod
    def g_create(cls, *, code: str) -> ActionKind:
        if not code:
            raise ValueError("code")
        return cls(code=code, name=code)

    @classmethod
    def g_create_many(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls.g_create(code=c) for c in codes)

    @classmethod
    def g_loop_over_proven(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = []
        for x in cls.open_many(codes):
            if x.code:
                items.append(x)
        return tuple(items)

    @classmethod
    def g_filter_nested(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls(code=c, name=n) for c in codes if c for n in ("a", "b"))

    @classmethod
    def g_dedupe(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        seen: set[str] = set()
        items: list[ActionKind] = []
        for c in codes:
            if c in seen:
                continue
            seen.add(c)
            items.append(cls.rv_for(c))
        if not items:
            raise ValueError("empty")
        assert all(isinstance(x, cls) for x in items)
        return tuple(items)

    @classmethod
    def g_validated_single(cls, code: str) -> ActionKind:
        obj: ActionKind = cls(code=code, name=code)
        obj.disable()
        return obj

    @classmethod
    def g_validated_many(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = []
        for c in codes:
            try:
                items.append(cls.g_validated_single(c))
            except ValueError:
                continue
        return tuple(items) if items else ()

    @classmethod
    def g_copy_method(cls, codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.rv_for(c) for c in codes]
        return items.copy()

    @classmethod
    def g_reversed(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls.rv_for(c) for c in codes]
        return tuple(reversed(items))

    @classmethod
    def g_star_tail(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls.rv_for(c) for c in codes]
        return (*items, cls.rv_for("tail"))

    @classmethod
    def g_splat_dict(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls(**{"code": c, "name": c}) for c in codes)

    @classmethod
    def g_varargs(cls, *codes: str) -> tuple[ActionKind, ...]:
        return tuple(cls(code=c, name=c) for c in codes)

    @classmethod
    def g_log_len(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls.rv_for(c) for c in codes]
        message: str = f"built {len(items)}"
        del message
        return tuple(items)

    @classmethod
    def g_ann_then_assign(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind]
        items = list()
        for c in codes:
            items.append(cls.rv_for(c))
        return tuple(items)

    @classmethod
    def g_local_lambda(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        make = cls.rv_for
        return tuple(make(c) for c in codes)

    @staticmethod
    def g_static_create(codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(ActionKind.g_create(code=c) for c in codes)

'''

SUBCLASS2 = '''

class SubKind2(ActionKind):
    @classmethod
    def rv_for(cls, code: str) -> SubKind2:
        return _LOADED2[0]

    @classmethod
    def teller2(cls, codes: Sequence[str]) -> tuple[SubKind2, ...]:
        return tuple(cls.rv_for(c) for c in codes)


_LOADED2: list[SubKind2] = []


class SubKind3(ActionKind):
    @classmethod
    def super_select(cls, kinds: Sequence[ActionKind]) -> tuple[SubKind3, ...]:
        return super().enabled_among(kinds)

    @classmethod
    def super_fresh(cls, codes: Sequence[str]) -> tuple[SubKind3, ...]:
        return tuple(super().open_many(codes))

    @classmethod
    def nested_gen(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[SubKind3, ...]:
        def _gen() -> Iterator[SubKind3]:
            yield from kinds

        return tuple(cls(code=c, name=c) for c in codes)
'''

SIDE = {
    "df_kind.py": '''from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True, kw_only=True)
class DfKind:
    code: str
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.code:
            raise ValueError("code")

    @classmethod
    def create(cls, *, code: str) -> DfKind:
        return cls(code=code)

    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple[DfKind, ...]:
        return tuple(cls.create(code=c) for c in codes)
''',
    "global_rebind_kind.py": '''from __future__ import annotations

from collections.abc import Sequence


class GlobalRebindKind:
    def __init__(self, code: str = "") -> None:
        self.code = code

    @staticmethod
    def open_many(kinds: Sequence["GlobalRebindKind"]) -> tuple["GlobalRebindKind", ...]:
        global GlobalRebindKind
        return tuple(GlobalRebindKind(k.code) for k in kinds)
''',
    "if_redef_kind.py": '''from __future__ import annotations

from collections.abc import Sequence

_LOADED: list["IfRedefKind"] = []


class IfRedefKind:
    @classmethod
    def one(cls, code: str) -> "IfRedefKind":
        return cls()

    if True:
        @classmethod
        def one(cls, code: str) -> "IfRedefKind":  # noqa: F811
            return _LOADED[0]

    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["IfRedefKind", ...]:
        return tuple(cls.one(c) for c in codes)

    @classmethod
    def adopt(cls, kinds: Sequence["IfRedefKind"]) -> None:
        _LOADED.extend(kinds)
''',
    "import_override_kind.py": '''from __future__ import annotations

from collections.abc import Sequence


class ImportOverrideKind:
    @classmethod
    def one(cls, code: str) -> "ImportOverrideKind":
        return cls()

    from application.orders.domain_layer.action_kind.evil_helpers import one  # noqa: E402,F811

    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["ImportOverrideKind", ...]:
        return tuple(cls.one(c) for c in codes)
''',
    "evil_helpers.py": '''from __future__ import annotations

_LOADED: list[object] = []


def one(code: str) -> object:
    return _LOADED[0]


def adopt(kinds: object) -> None:
    _LOADED.extend(kinds)  # type: ignore[arg-type]
''',
    "new_assign_kind.py": '''from __future__ import annotations

from collections.abc import Sequence

_LOADED: list["NewAssignKind"] = []


def _pooled_new(cls: type, *args: object, **kwargs: object) -> "NewAssignKind":
    return _LOADED[0]


class NewAssignKind:
    __new__ = _pooled_new

    def __init__(self, code: str = "") -> None:
        pass

    @classmethod
    def adopt(cls, kinds: Sequence["NewAssignKind"]) -> None:
        _LOADED.extend(kinds)

    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["NewAssignKind", ...]:
        return tuple(cls(c) for c in codes)
''',
    "new_in_if_kind.py": '''from __future__ import annotations

from collections.abc import Sequence

_LOADED: list["NewInIfKind"] = []


class NewInIfKind:
    if True:
        def __new__(cls, *args: object) -> "NewInIfKind":
            return _LOADED[0]

    @classmethod
    def adopt(cls, kinds: Sequence["NewInIfKind"]) -> None:
        _LOADED.extend(kinds)

    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["NewInIfKind", ...]:
        return tuple(cls(c) for c in codes)
''',
    "meta_base_kind.py": '''from __future__ import annotations

from collections.abc import Sequence

_LOADED: list[object] = []


class _Meta(type):
    def __call__(cls, *args: object, **kwargs: object) -> object:
        return _LOADED[0]


class _Base(metaclass=_Meta):
    pass


class MetaBaseKind(_Base):
    @classmethod
    def adopt(cls, kinds: Sequence["MetaBaseKind"]) -> None:
        _LOADED.extend(kinds)

    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["MetaBaseKind", ...]:
        return tuple(cls(c) for c in codes)
''',
    "base_new_kind.py": '''from __future__ import annotations

from collections.abc import Sequence

_LOADED: list[object] = []


class _PoolBase:
    def __new__(cls, *args: object) -> object:
        return _LOADED[0]


class BaseNewKind(_PoolBase):
    @classmethod
    def adopt(cls, kinds: Sequence["BaseNewKind"]) -> None:
        _LOADED.extend(kinds)

    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["BaseNewKind", ...]:
        return tuple(cls(c) for c in codes)
''',
    "class_deco_kind.py": '''from __future__ import annotations

from collections.abc import Sequence

_LOADED: list[object] = []


def _swap(c: type) -> type:
    c.__new__ = staticmethod(lambda k, *a, **kw: _LOADED[0])  # type: ignore[assignment]
    return c


@_swap
class ClassDecoKind:
    def __init__(self, code: str = "") -> None:
        pass

    @classmethod
    def adopt(cls, kinds: Sequence["ClassDecoKind"]) -> None:
        _LOADED.extend(kinds)

    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["ClassDecoKind", ...]:
        return tuple(cls(c) for c in codes)
''',
}

# 같은 이름 다른 모듈 — 진짜 ActionKind.twin_batch 는 선별 헬퍼(위 METHODS), archive 쪽은 증명되는 팩토리.
ARCHIVE = {
    "application/orders/domain_layer/archive/__init__.py": "",
    "application/orders/domain_layer/archive/action_kind.py": '''from __future__ import annotations

from collections.abc import Sequence


class ActionKind:
    def __init__(self, code: str = "") -> None:
        self.code = code

    @classmethod
    def twin_batch(cls, kinds: Sequence["ActionKind"]) -> tuple["ActionKind", ...]:
        return tuple(cls(k.code) for k in kinds)
''',
}

HDR = '''from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.action_kind.action_kind_repository import ActionKindRepository
{imports}

class {cls}:
    def __init__(self, repository: ActionKindRepository, unit_of_work: OrdersUnitOfWork) -> None:
        self._repository: ActionKindRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work

    def execute(self, codes: list[str]) -> None:
        with self._unit_of_work:
{body}
'''
AK = "from application.orders.domain_layer.action_kind.action_kind import ActionKind"
LIST = "self._repository.list_all()"
GOOD = "for kind in {call}:\n    self._repository.save(kind)\n"
BAD = "for kind in {call}:\n    kind.is_enabled = False\n    self._repository.save(kind)\n"
ADOPT = f"ActionKind.rv_adopt({LIST})\n"

CASES: list[tuple[str, str, str, str]] = []   # (이름, 기대, 본문, 추가 import)


def case(name: str, want: str, body: str, imports: str = "") -> None:
    CASES.append((name, want, body, imports))


# 복제 계열
case("RC1_type_call", "red", BAD.format(call=f"ActionKind.rc_type_call({LIST})"))
case("RC2_dunder_class", "red", BAD.format(call=f"ActionKind.rc_dunder_class({LIST})"))
case("RC3_copy_copy", "red", BAD.format(call=f"ActionKind.rc_copy_copy({LIST})"))
case("RC4_vars_splat", "lim", BAD.format(call=f"ActionKind.rc_vars_splat({LIST})"))
case("RC5_asdict", "lim", BAD.format(call=f"ActionKind.rc_asdict({LIST})"))
case("RC6_shared_dict", "lim", BAD.format(call=f"ActionKind.rc_shared_dict({LIST})"))
# 누적 우회
for nm, meth in [("RA1_extend_iter", "ra_extend_iter"), ("RA2_iadd_tuple", "ra_iadd_tuple"),
                 ("RA3_setitem_dunder", "ra_setitem_dunder"), ("RA4_operator_iadd", "ra_operator_iadd"),
                 ("RA5_default_arg_alias", "ra_default_arg_alias"), ("RA6_literal_alias", "ra_literal_alias"),
                 ("RA9_radd_grabber", "ra_radd_grabber"), ("RA10_eq_grabber", "ra_eq_grabber"),
                 ("RA13_loop_alias_acc", "ra_loop_alias_acc")]:
    case(nm, "red", BAD.format(call=f"ActionKind.{meth}({LIST}, codes)"))
case("RA7_set_update_genexp", "red", BAD.format(call=f"ActionKind.ra_set_update_genexp({LIST})"))
case("RA11_scope_acc_module_list", "red", ADOPT + BAD.format(call="ActionKind.ra_scope_acc(codes)"))
case("RA12_scope_elem_module_name", "red", ADOPT + BAD.format(call="ActionKind.ra_scope_elem(codes)"))
# return 경로
for nm, meth in [("RR1_finally_return", "rr_finally_return"), ("RR2_except_return", "rr_except_return"),
                 ("RR4_match_return", "rr_match_return")]:
    case(nm, "red", BAD.format(call=f"ActionKind.{meth}({LIST}, codes)"))
case("RR3_walrus_return", "red", BAD.format(call=f"ActionKind.rr_walrus_return({LIST})"))
case("RR5_map_identity", "red", BAD.format(call=f"ActionKind.rr_map_identity({LIST})"))
# 원소 출처
case("RE1_cache_setdefault", "red", ADOPT + BAD.format(call="ActionKind.re_cache_setdefault(codes)"))
case("RE2_selector_delegate", "red", BAD.format(call=f"ActionKind.re_selector_delegate({LIST})"))
case("RE3_scalar_selector", "red", BAD.format(call=f"ActionKind.re_scalar_selector({LIST})"))
case("RE4_reconcile_boolop", "red", BAD.format(call=f"ActionKind.re_reconcile_boolop({LIST}, codes)"))
case("RE5_nested_nonlocal_elem", "red", BAD.format(call=f"ActionKind.re_nested_nonlocal_elem({LIST})"))
case("RD1_outer_decorator", "red", BAD.format(call=f"ActionKind.rd_outer_decorator({LIST}, codes)"))
case("RS1_static_global_rebind", "red", BAD.format(call=f"GlobalRebindKind.open_many({LIST})"),
     "from application.orders.domain_layer.action_kind.global_rebind_kind import GlobalRebindKind")
case("RI1_subclass_override_scalar", "red", BAD.format(call="SubKind2.teller2(codes)"),
     "from application.orders.domain_layer.action_kind.action_kind import SubKind2")
case("RN1_same_name_real_selector", "red", BAD.format(call=f"ActionKind.twin_batch({LIST})"))
case("RN2_same_name_archive_clone", "lim", BAD.format(call=f"ArchKind.twin_batch({LIST})"),
     "from application.orders.domain_layer.archive.action_kind import ActionKind as ArchKind")
case("RU1_super_selector", "red", BAD.format(call=f"SubKind3.super_select({LIST})"),
     "from application.orders.domain_layer.action_kind.action_kind import SubKind3")
case("GU2_super_fresh", "fc", GOOD.format(call="SubKind3.super_fresh(codes)"),
     "from application.orders.domain_layer.action_kind.action_kind import SubKind3")
case("GU3_nested_generator_helper", "fc", GOOD.format(call=f"SubKind3.nested_gen({LIST}, codes)"),
     "from application.orders.domain_layer.action_kind.action_kind import SubKind3")
case("G20_dataclass_default_factory", "green", GOOD.format(call="DfKind.open_many(codes)"),
     "from application.orders.domain_layer.action_kind.df_kind import DfKind")
case("GC1_callsite_enumerate", "fc", "for i, kind in enumerate(ActionKind.open_many(codes)):\n    self._repository.save(kind)\n")
case("GC2_callsite_zip", "fc", "for kind, code in zip(ActionKind.open_many(codes), codes):\n    self._repository.save(kind)\n")
case("GC3_callsite_sorted", "fc", "for kind in sorted(ActionKind.open_many(codes), key=lambda k: k.code):\n    self._repository.save(kind)\n")
case("GC4_callsite_after_loaded_then_method", "green", f"for kind in ActionKind.after(tuple({LIST}), 2):\n    kind.disable()\n    self._repository.save(kind)\n")
# 클래스 수준
for nm, cls, mod, want in [("RK1_if_block_redef", "IfRedefKind", "if_redef_kind", "red"),
                           ("RK2_class_body_import", "ImportOverrideKind", "import_override_kind", "red"),
                           ("RK3_new_assigned", "NewAssignKind", "new_assign_kind", "red"),
                           ("RK4_new_in_if", "NewInIfKind", "new_in_if_kind", "red"),
                           ("RK5_metaclass_via_base", "MetaBaseKind", "meta_base_kind", "lim"),
                           ("RK6_base_new", "BaseNewKind", "base_new_kind", "lim"),
                           ("RK7_class_decorator", "ClassDecoKind", "class_deco_kind", "lim")]:
    case(nm, want, BAD.format(call=f"{cls}.open_many(codes)"),
         f"from application.orders.domain_layer.action_kind.{mod} import {cls}")
# 흔한 리팩토링 모양
for nm, call, want in [
    ("G01_enumerate", "ActionKind.g_enumerate(codes)", "green"),
    ("G02_zip", "ActionKind.g_zip(codes, codes)", "green"),
    ("G03_dict_values", "ActionKind.g_dict_values(codes)", "fc"),
    ("G04_sorted_fresh", "ActionKind.g_sorted_fresh(codes)", "fc"),
    ("G05_map_factory", "ActionKind.g_map_factory(codes)", "fc"),
    ("G06_create_kw", "ActionKind.g_create_many(codes)", "green"),
    ("G07_loop_over_proven", "ActionKind.g_loop_over_proven(codes)", "fc"),
    ("G08_filter_nested", "ActionKind.g_filter_nested(codes)", "green"),
    ("G09_dedupe_assert", "ActionKind.g_dedupe(codes)", "green"),
    ("G10_validated_try", "ActionKind.g_validated_many(codes)", "green"),
    ("G11_copy_method", "ActionKind.g_copy_method(codes)", "fc"),
    ("G12_reversed", "ActionKind.g_reversed(codes)", "fc"),
    ("G13_star_tail", "ActionKind.g_star_tail(codes)", "green"),
    ("G14_splat_dict", "ActionKind.g_splat_dict(codes)", "green"),
    ("G15_varargs", "ActionKind.g_varargs(*codes)", "green"),
    ("G16_log_len_fstring", "ActionKind.g_log_len(codes)", "green"),
    ("G17_ann_then_assign", "ActionKind.g_ann_then_assign(codes)", "green"),
    ("G18_local_alias_factory", "ActionKind.g_local_lambda(codes)", "fc"),
    ("G19_static_create", "ActionKind.g_static_create(codes)", "green"),
]:
    case(nm, want, GOOD.format(call=call))


def build(base: Path, trees: Path) -> list[tuple[str, str]]:
    """바탕 트리 base 에 탐침을 얹어 trees/<이름>/ 에 쓰고 (이름, 기대) 목록을 돌려준다."""
    if trees.exists():
        shutil.rmtree(trees)
    trees.mkdir()
    src0 = (base / DOM / "action_kind.py").read_text(encoding="utf-8")
    dom = src0.replace("from collections.abc import Sequence\n",
                       "from collections.abc import Sequence\n" + HEADER_EXTRA, 1)
    dom = dom.replace("    def disable(self) -> None:", METHODS.lstrip("\n") + "    def disable(self) -> None:", 1)
    dom = dom.rstrip("\n") + "\n" + SUBCLASS2
    compile(dom, "action_kind.py", "exec")
    for text in SIDE.values():
        compile(text, "side.py", "exec")
    rows = []
    for name, want, body, extra in CASES:
        t = trees / name
        shutil.copytree(base, t)
        shutil.rmtree(t / UC / "c_domain_seed_inline")
        (t / DOM / "action_kind.py").write_text(dom, encoding="utf-8")
        for fn, text in SIDE.items():
            (t / DOM / fn).write_text(text, encoding="utf-8")
        for rel, text in ARCHIVE.items():
            p = t / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        low = name.lower()
        (t / UC / low).mkdir(parents=True)
        cls = "".join(p.capitalize() for p in low.split("_")) + "UseCase"
        imports = AK + ("\n" + extra if extra else "")
        # 클래스 수준 공격은 먼저 조회 결과를 도메인 상태에 들인다(B33·B34 판형).
        if name.startswith("RK") and name != "RK2_class_body_import":
            cname = extra.split()[-1]
            body = f"{cname}.adopt({LIST})\n" + body
        if name == "RK2_class_body_import":
            imports += "\nfrom application.orders.domain_layer.action_kind import evil_helpers"
            body = f"evil_helpers.adopt({LIST})\n" + body
        src = HDR.format(imports=imports, cls=cls,
                         body=textwrap.indent(textwrap.dedent(body).strip("\n"), " " * 12))
        compile(src, name, "exec")
        (t / UC / low / f"{low}_use_case.py").write_text(src, encoding="utf-8")
        rows.append(f"{name}\t{want}")
    return [(r.split("\t")[0], r.split("\t")[1]) for r in rows]


if __name__ == "__main__":
    import sys
    print(f"{len(build(Path(sys.argv[1]), Path(sys.argv[2])))} trees → {sys.argv[2]}")
