"""R8-I2 탐침 — 인자 받는 도메인 컬렉션 팩토리(h 계열)와 본문 증명 세탁 공격.

바탕 = diag-D2 `c_domain_seed_inline` 트리(good fixture 사본 + action_kind 애그리거트). 트리마다 유스케이스 1개.
기대(ideal): green = 원소가 도메인 본문에서 새로 태어난다 · red = 조회된(받은) 인스턴스가 원소로 샌다.
표기: 기대 열의 `fc` = 이상은 green 이지만 fail-closed red 를 받아들이는 모양, `lim` = 이상은 red 이지만
      문서화할 한계(green 을 받아들이는 모양). run 표의 ✗ 는 ideal 과 다름.
"""
from __future__ import annotations

import shutil
import textwrap
from pathlib import Path

DOM = "application/orders/domain_layer/action_kind"
UC = "application/orders/application_layer/action_kind"

EXTRA_METHODS = '''
    _REGISTRY: ClassVar[dict[str, "ActionKind"]] = {}
    _POOL: ClassVar[list["ActionKind"]] = []

    # ── 이상 green: 인자를 받아도 원소는 본문에서 새로 태어난다 ──
    @classmethod
    def for_code(cls, code: str) -> ActionKind:
        return cls(code=code, name=code)

    @classmethod
    def teller_like(
        cls,
        *,
        codes: Sequence[str],
        text: str,
        widgets: tuple[Mapping[str, object], ...] = (),
    ) -> tuple[ActionKind, ...]:
        """현장 ConversationItem.teller_items 모양 — 빈 리스트 + 단일 팩토리 append + tuple 복사."""
        items: list[ActionKind] = []
        if text:
            items.append(cls.for_code(text))
        for code in codes:
            items.append(cls.for_code(code))
        for widget in widgets:
            if widget.get("marker"):
                items.append(cls.for_marker(marker=widget))
            else:
                items.append(cls(code=str(widget.get("code")), name=""))
        return tuple(items)

    @classmethod
    def for_marker(cls, *, marker: Mapping[str, object]) -> ActionKind:
        code: str = str(marker.get("code"))
        kind: ActionKind = cls(code=code, name="marker")
        return kind

    @classmethod
    def after(cls, existing: tuple[ActionKind, ...], count: int) -> tuple[ActionKind, ...]:
        """현장 DisplayOrder.after 모양 — existing(조회 결과일 수 있다)은 읽기만 한다."""
        start: int = max((len(kind.code) for kind in existing), default=-1) + 1
        return tuple(cls(code=f"k{start + offset}", name="") for offset in range(count))

    @classmethod
    def pair(cls, a: str, b: str) -> tuple[ActionKind, ActionKind]:
        return (cls(code=a, name=a), cls(code=b, name=b))

    @classmethod
    def delegated(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls.for_code(code) for code in codes)

    @staticmethod
    def of_codes(codes: Sequence[str]) -> list[ActionKind]:
        return [ActionKind(code=code, name=code) for code in codes]

    @classmethod
    def with_extra(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls.open_many(codes)) + (cls(code="extra", name="extra"),)

    @classmethod
    def maybe_empty(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        if not codes:
            return ()
        return tuple(cls(code=code, name=code) for code in codes)

    @classmethod
    def accumulate_mixed(cls, codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls(code="head", name="head")]
        items.extend(cls.for_code(code) for code in codes)
        items += [cls(code="tail", name="tail")]
        items.insert(0, cls.for_code("first"))
        if len(items) > 10:
            items.sort(key=lambda k: k.code)
        return items

    @classmethod
    def local_var_elems(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = []
        for code in codes:
            item: ActionKind = cls.for_code(code)
            items.append(item)
        return tuple(items)

    @classmethod
    def ifexp_elems(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls.for_code(code) if code else cls(code="none", name="") for code in codes)

    @classmethod
    def klass_param(klass, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(klass(code=code, name=code) for code in codes)

    @staticmethod
    def static_delegate(codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(ActionKind.for_code(code) for code in codes)

    @classmethod
    def recursive(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        if not codes:
            return ()
        return (cls.for_code(codes[0]),) + cls.recursive(codes[1:])

    @classmethod
    def raw_for_code(cls, code: str) -> ActionKind:
        """object.__new__ 관용(현장 GenerationAudit.start 모양) — 공개 생성자를 거치지 않는 새 인스턴스."""
        kind: ActionKind = object.__new__(cls)
        object.__setattr__(kind, "code", code)
        object.__setattr__(kind, "name", code)
        object.__setattr__(kind, "is_enabled", True)
        return kind

    @classmethod
    def raw_many(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls.raw_for_code(code) for code in codes)

    @classmethod
    def object_shadow(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        object = _PickFirst(kinds)  # noqa: A001
        return tuple(object.__new__(cls) for code in codes)

    @classmethod
    def copies(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        """받은 인스턴스의 필드를 베껴 새로 짓는 복제 팩토리(한계 — 스칼라 `C(**vars(x))` 와 같은 부류)."""
        return tuple(cls(code=k.code, name=k.name, is_enabled=k.is_enabled) for k in kinds)

    # ── 이상 red: 받은(조회된) 인스턴스가 원소로 샌다 ──
    @classmethod
    def seeded_from(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = list(kinds)
        items.append(cls.for_code("x"))
        return items

    @classmethod
    def extended_with(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        items.extend(kinds)
        return items

    @classmethod
    def loop_appends(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = []
        for kind in kinds:
            items.append(kind)
        return tuple(items)

    @classmethod
    def identity_appends(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = []
        for kind in kinds:
            items.append(cls.identity(kind))
        return tuple(items)

    @classmethod
    def helper_fills(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = []
        _fill(items, kinds)
        return tuple(items)

    @classmethod
    def branch_returns_arg(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        if not codes:
            return tuple(kinds)
        return tuple(cls.for_code(code) for code in codes)

    @classmethod
    def ifexp_arg_elem(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return tuple(cls(code=k.code, name=k.name) if not k.is_enabled else k for k in kinds)

    @classmethod
    def cls_rebound(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        cls = lambda **kw: kinds[0]  # noqa: E731
        return tuple(cls(code=k.code) for k in kinds)

    @classmethod
    def comp_rebinds_cls(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return tuple(cls() for cls in kinds)

    @staticmethod
    def static_cls_param(cls: Callable[..., ActionKind], kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return tuple(cls(kind) for kind in kinds)

    @staticmethod
    def own_name_rebound(kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        ActionKind = lambda **kw: kinds[0]  # noqa: E731,N806
        return tuple(ActionKind(code=k.code) for k in kinds)

    @classmethod
    @_launder
    def decorated(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls.for_code(code) for code in codes)

    @classmethod
    def gen_yield(cls, kinds: Sequence[ActionKind]) -> Iterator[ActionKind]:
        yield from kinds

    @classmethod
    def gen_yield_return(cls, kinds: Sequence[ActionKind]) -> Iterator[ActionKind]:
        yield from kinds
        return ()

    @classmethod
    def nested_append(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]

        def add() -> None:
            items.append(kinds[0])

        add()
        return tuple(items)

    @classmethod
    def key_append(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = []
        for code in sorted(codes, key=lambda c: items.append(kinds[0]) or c):
            items.append(cls.for_code(code))
        return tuple(items)

    @classmethod
    def subscript_store(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        items[0] = kinds[0]
        return items

    @classmethod
    def iadd_arg(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        items += list(kinds)
        return items

    @classmethod
    def slice_store(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        items[:] = kinds
        return items

    @classmethod
    def rebind_concat(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        items = items + list(kinds)
        return items

    @classmethod
    def elem_var_rebound(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = []
        for code in codes:
            item: ActionKind = cls.for_code(code)
            item = kinds[0]
            items.append(item)
        return tuple(items)

    @classmethod
    def walrus_elem(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = []
        for code in codes:
            items.append(item := kinds[0])
        return tuple(items)

    @classmethod
    def lookup(cls, code: str) -> ActionKind:
        return cls._REGISTRY[code]

    @classmethod
    def remember(cls, kinds: Sequence[ActionKind]) -> None:
        for kind in kinds:
            cls._REGISTRY[kind.code] = kind
            cls._POOL.append(kind)

    @classmethod
    def registry_elems(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls.lookup(code) for code in codes)

    @classmethod
    def locals_extend(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        locals()["items"].extend(kinds)
        return items

    @classmethod
    def dunder_iadd(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        items.__iadd__(kinds)
        return items

    @classmethod
    def insert_arg(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        items.insert(0, kinds[0])
        return items

    @classmethod
    def return_concat_arg(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        return tuple(items) + tuple(kinds)

    @classmethod
    def return_star_arg(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        return (*items, *kinds)

    @classmethod
    def global_acc(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        global _ACC
        for code in codes:
            _ACC.append(cls.for_code(code))
        return tuple(_ACC)

    @classmethod
    def class_pool(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        for code in codes:
            cls._POOL.append(cls.for_code(code))
        return tuple(cls._POOL)

    @classmethod
    def alias_extend(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        alias: list[ActionKind] = items
        alias.extend(kinds)
        return items

    @classmethod
    def replaced(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return tuple(dataclasses.replace(k) for k in kinds)

    @classmethod
    def sorted_arg(cls, kinds: Sequence[ActionKind]) -> list[ActionKind]:
        return sorted(kinds, key=lambda k: k.code)

    @classmethod
    def nested_return(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        def pick() -> Sequence[ActionKind]:
            return kinds

        return tuple(pick())

    @classmethod
    def ifexp_return_arg(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        return tuple(items) if codes else tuple(kinds)

    @classmethod
    def nonlocal_rebind(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]

        def reset() -> None:
            nonlocal items
            items = list(kinds)

        reset()
        return tuple(items)

    @classmethod
    def unbound_append(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        list.append(items, kinds[0])
        return items

    @classmethod
    def vars_extend(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls.for_code(code) for code in codes]
        vars()["items"].extend(kinds)
        return items

    @classmethod
    def extend_genexp_arg(cls, kinds: Sequence[ActionKind]) -> list[ActionKind]:
        items: list[ActionKind] = []
        items.extend(k for k in kinds)
        return items

    @classmethod
    def extend_unproven(cls, kinds: Sequence[ActionKind]) -> list[ActionKind]:
        items: list[ActionKind] = []
        items.extend(cls.touched(kinds))
        return items

    @classmethod
    def append_max(cls, kinds: Sequence[ActionKind]) -> list[ActionKind]:
        items: list[ActionKind] = []
        items.append(max(kinds, key=lambda k: k.code))
        return items

    @classmethod
    def dict_values(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        by_code: dict[str, ActionKind] = {code: cls.for_code(code) for code in codes}
        return tuple(by_code.values())

    @classmethod
    def tuple_shadow(cls, kinds: Sequence[ActionKind], codes: Sequence[str]) -> tuple[ActionKind, ...]:
        tuple = lambda xs: kinds  # noqa: A001,E731
        return tuple(cls.for_code(code) for code in codes)

    @classmethod
    def pick_objects(cls, rows: Sequence[object]) -> tuple[ActionKind, ...]:
        return tuple(r for r in rows if isinstance(r, ActionKind))

    @classmethod
    def pick_any(cls, rows: Sequence[Any]) -> tuple[ActionKind, ...]:
        return tuple(rows)

    @classmethod
    def dup(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(cls.for_code(code) for code in codes)

    dup = staticmethod(lambda kinds, codes: tuple(kinds))  # noqa: F811

'''

DOMAIN_HEADER_EXTRA = '''import dataclasses
from collections.abc import Callable, Iterator, Mapping
from typing import Any, ClassVar


def _launder(fn: Callable[..., object]) -> Callable[..., object]:
    def wrapper(cls: type, kinds: Sequence["ActionKind"], codes: Sequence[str]) -> tuple["ActionKind", ...]:
        return tuple(kinds)
    return wrapper


def _fill(items: list["ActionKind"], kinds: Sequence["ActionKind"]) -> None:
    items.extend(kinds)


_ACC: list["ActionKind"] = []


class _PickFirst:
    def __init__(self, kinds: Sequence["ActionKind"]) -> None:
        self._kinds = kinds

    def __new__(cls, *args: object) -> "_PickFirst":  # noqa: D102
        return super().__new__(cls)
'''

SUBCLASS = '''

class SubKind(ActionKind):
    pass
'''

# 별도 모듈 — 클래스 수준 가정 공격(`__new__`·metaclass·모듈 범위 재결속·내장 가림).
SIDE_MODULES = {
    "cached_kind.py": '''from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar


class CachedKind:
    _POOL: ClassVar[dict[str, "CachedKind"]] = {}

    def __new__(cls, code: str) -> "CachedKind":
        return cls._POOL.setdefault(code, super().__new__(cls))

    def __init__(self, code: str) -> None:
        self.code = code

    @classmethod
    def adopt(cls, kinds: Sequence["CachedKind"]) -> None:
        for kind in kinds:
            cls._POOL[kind.code] = kind

    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["CachedKind", ...]:
        return tuple(cls(code) for code in codes)
''',
    "sealed_kind.py": '''from __future__ import annotations

from collections.abc import Sequence


class SealedKind:
    """이름 있는 팩토리로만 태어난다(현장 CallerLabel 모양 — 공개 생성자 금지)."""

    code: str

    def __new__(cls) -> "SealedKind":
        raise TypeError("SealedKind 는 create 로만 만든다")

    @classmethod
    def create(cls, code: str) -> "SealedKind":
        kind: SealedKind = object.__new__(cls)
        object.__setattr__(kind, "code", code)
        return kind

    @classmethod
    def many(cls, codes: Sequence[str]) -> tuple["SealedKind", ...]:
        return tuple(cls.create(code) for code in codes)
''',
    "pooled_kind.py": '''from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar


class PooledKind:
    _POOL: ClassVar[list["PooledKind"]] = []

    def __new__(cls) -> "PooledKind":
        return cls._POOL[0] if cls._POOL else super().__new__(cls)

    @classmethod
    def adopt(cls, kinds: Sequence["PooledKind"]) -> None:
        cls._POOL.extend(kinds)

    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["PooledKind", ...]:
        return tuple(cls.__new__(cls) for code in codes)
''',
    "patched_kind.py": '''from __future__ import annotations

from collections.abc import Sequence

_LOADED: list["PatchedKind"] = []


class PatchedKind:
    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["PatchedKind", ...]:
        return tuple(cls() for code in codes)


PatchedKind.open_many = classmethod(lambda cls, codes: tuple(_LOADED))  # type: ignore[method-assign]
''',
    "deco_shadow_kind.py": '''from __future__ import annotations

from collections.abc import Callable, Sequence

_LOADED: list["DecoShadowKind"] = []


def classmethod(fn: Callable[..., object]) -> object:  # noqa: A001
    return lambda *args: tuple(_LOADED)


class DecoShadowKind:
    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["DecoShadowKind", ...]:
        return tuple(cls() for code in codes)
''',
    "meta_kind.py": '''from __future__ import annotations

from collections.abc import Sequence


class _Meta(type):
    def __call__(cls, *args: object, **kwargs: object) -> object:
        return _LOADED[0]


_LOADED: list[object] = []


class MetaKind(metaclass=_Meta):
    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["MetaKind", ...]:
        return tuple(cls(code) for code in codes)
''',
    "rebound_kind.py": '''from __future__ import annotations

from collections.abc import Sequence


class ReboundKind:
    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["ReboundKind", ...]:
        return tuple(ReboundKind(code) for code in codes)


def _wrap(c: type) -> type:
    return c


ReboundKind = _wrap(ReboundKind)  # noqa: F811
''',
    "shadow_kind.py": '''from __future__ import annotations

from collections.abc import Sequence

_LOADED: list["ShadowKind"] = []


def tuple(xs: object) -> "tuple[ShadowKind, ...]":  # noqa: A001
    return _LOADED  # type: ignore[return-value]


class ShadowKind:
    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["ShadowKind", ...]:
        return tuple(cls() for code in codes)
''',
}

HDR = '''from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.action_kind.action_kind_repository import ActionKindRepository
{imports}

class {cls}:
    def __init__(self, repository: ActionKindRepository, unit_of_work: OrdersUnitOfWork{init_extra}) -> None:
        self._repository: ActionKindRepository = repository
        self._unit_of_work: OrdersUnitOfWork = unit_of_work
{init_body}
    def execute(self, codes: list[str]{params}) -> None:
        with self._unit_of_work:
{body}
'''
AK = "from application.orders.domain_layer.action_kind.action_kind import ActionKind"

GOOD_LOOP = """
for kind in {call}:
    self._repository.save(kind)
"""
BAD_LOOP = """
for kind in {call}:
    kind.is_enabled = False
    self._repository.save(kind)
"""
LIST = "self._repository.list_all()"

CASES: list[tuple[str, str, str, dict]] = []


def case(name: str, want: str, body: str, **kw: str) -> None:
    CASES.append((name, want, body, kw))


# ── h 계열(이상 green) ──
case("H0_open_many_positional", "green", GOOD_LOOP.format(call="ActionKind.open_many(codes)"))
case("H1_teller_inline_kw", "green", GOOD_LOOP.format(
    call='ActionKind.teller_like(codes=codes, text="hello", widgets=({"code": "w"},))'))
case("H1n_teller_named", "green", """
batch: tuple[ActionKind, ...] = ActionKind.teller_like(codes=codes, text="hello")
for kind in batch:
    self._repository.save(kind)
""")
case("H1f_teller_field_assign", "green", BAD_LOOP.format(call='ActionKind.teller_like(codes=codes, text="")'))
case("H2_after_query_arg_inline", "green", BAD_LOOP.format(call=f"ActionKind.after(tuple({LIST}), len(codes))"))
case("H2n_after_query_arg_named", "green", f"""
batch: tuple[ActionKind, ...] = ActionKind.after(tuple({LIST}), 2)
for kind in batch:
    self._repository.save(kind)
""")
case("H3_pair_literal", "green", GOOD_LOOP.format(call='ActionKind.pair("a", "b")'))
case("H4_delegated_scalar", "green", GOOD_LOOP.format(call="ActionKind.delegated(codes)"))
case("H5_static_ctor_by_name", "green", GOOD_LOOP.format(call="ActionKind.of_codes(codes)"))
case("H6_coll_recursion_concat", "green", GOOD_LOOP.format(call="ActionKind.with_extra(codes)"))
case("H7_early_empty_return", "green", GOOD_LOOP.format(call="ActionKind.maybe_empty(codes)"))
case("H8_accumulate_mixed", "green", GOOD_LOOP.format(call="ActionKind.accumulate_mixed(codes)"))
case("H9_local_var_elem", "green", GOOD_LOOP.format(call="ActionKind.local_var_elems(codes)"))
case("H10_ifexp_elem", "green", GOOD_LOOP.format(call="ActionKind.ifexp_elems(codes)"))
case("H11_klass_first_param", "green", GOOD_LOOP.format(call="ActionKind.klass_param(codes)"))
case("H12_static_delegate", "green", GOOD_LOOP.format(call="ActionKind.static_delegate(codes)"))
case("H13_wrapped_callsite", "green", GOOD_LOOP.format(call="tuple(ActionKind.open_many(codes))"))
case("H14_star_arg_callsite", "green", GOOD_LOOP.format(call="ActionKind.open_many(*[codes])"))
case("H15_collective_save", "green", """
batch: list[ActionKind] = ActionKind.open_many(codes)
self._repository.save_all(batch)
""")
case("H21_object_new_delegate", "green", GOOD_LOOP.format(call="ActionKind.raw_many(codes)"))
case("H22_sealed_named_factory", "green", GOOD_LOOP.format(call="SealedKind.many(codes)"),
     imports="from application.orders.domain_layer.action_kind.sealed_kind import SealedKind")
case("H16_recursive_fc", "fc", GOOD_LOOP.format(call="ActionKind.recursive(codes)"))
case("H17_inherited_fc", "fc", GOOD_LOOP.format(call="SubKind.open_many(codes)"),
     imports="from application.orders.domain_layer.action_kind.action_kind import SubKind")
case("H18_dict_values_fc", "fc", GOOD_LOOP.format(call="ActionKind.dict_values(codes)"))
case("H19_copy_ctor_lim", "lim", BAD_LOOP.format(call=f"ActionKind.copies({LIST})"))
case("H23_module_monkeypatch_lim", "lim", BAD_LOOP.format(call="PatchedKind.open_many(codes)"),
     imports="from application.orders.domain_layer.action_kind.patched_kind import PatchedKind")
case("H20_mixed_after_factory", "red", f"""
batch: list[ActionKind] = list(ActionKind.open_many(codes))
batch.extend({LIST})
for kind in batch:
    kind.is_enabled = False
    self._repository.save(kind)
""")
# ── 본문 증명 세탁(이상 red) ──
for nm, call in [
    ("B1_acc_seeded_from_arg", f"ActionKind.seeded_from({LIST}, codes)"),
    ("B2_extend_arg", f"ActionKind.extended_with({LIST}, codes)"),
    ("B3_loop_append_arg", f"ActionKind.loop_appends({LIST})"),
    ("B4_identity_append", f"ActionKind.identity_appends({LIST})"),
    ("B5_helper_fills_acc", f"ActionKind.helper_fills({LIST})"),
    ("B6_branch_returns_arg", f"ActionKind.branch_returns_arg({LIST}, codes)"),
    ("B7_ifexp_arg_elem", f"ActionKind.ifexp_arg_elem({LIST})"),
    ("B8_cls_rebound", f"ActionKind.cls_rebound({LIST})"),
    ("B8b_comprehension_rebinds_cls", f"ActionKind.comp_rebinds_cls({LIST})"),
    ("B9_static_param_named_cls", f"ActionKind.static_cls_param(lambda k: k, {LIST})"),
    ("B10_own_name_rebound_local", f"ActionKind.own_name_rebound({LIST})"),
    ("B12_extra_decorator", f"ActionKind.decorated({LIST}, codes)"),
    ("B13_yield_from_arg", f"ActionKind.gen_yield({LIST})"),
    ("B13b_yield_then_return_empty", f"ActionKind.gen_yield_return({LIST})"),
    ("B14_nested_def_append", f"ActionKind.nested_append({LIST}, codes)"),
    ("B15_lambda_key_append", f"ActionKind.key_append({LIST}, codes)"),
    ("B16_subscript_store", f"ActionKind.subscript_store({LIST}, codes)"),
    ("B17_iadd_arg", f"ActionKind.iadd_arg({LIST}, codes)"),
    ("B18_slice_store", f"ActionKind.slice_store({LIST}, codes)"),
    ("B19_rebind_concat", f"ActionKind.rebind_concat({LIST}, codes)"),
    ("B20_elem_var_rebound", f"ActionKind.elem_var_rebound({LIST}, codes)"),
    ("B21_walrus_elem", f"ActionKind.walrus_elem({LIST}, codes)"),
    ("B27_locals_extend", f"ActionKind.locals_extend({LIST}, codes)"),
    ("B28_dunder_iadd", f"ActionKind.dunder_iadd({LIST}, codes)"),
    ("B30_insert_arg", f"ActionKind.insert_arg({LIST}, codes)"),
    ("B31_return_concat_arg", f"ActionKind.return_concat_arg({LIST}, codes)"),
    ("B32_return_star_arg", f"ActionKind.return_star_arg({LIST}, codes)"),
    ("B35_alias_extend", f"ActionKind.alias_extend({LIST}, codes)"),
    ("B38_dataclasses_replace", f"ActionKind.replaced({LIST})"),
    ("B40_sorted_arg", f"ActionKind.sorted_arg({LIST})"),
    ("B41_nested_return_arg", f"ActionKind.nested_return({LIST})"),
    ("B44_ifexp_return_arg", f"ActionKind.ifexp_return_arg({LIST}, codes)"),
    ("B45_nonlocal_rebind", f"ActionKind.nonlocal_rebind({LIST}, codes)"),
    ("B47_unbound_list_append", f"ActionKind.unbound_append({LIST}, codes)"),
    ("B48_vars_extend", f"ActionKind.vars_extend({LIST}, codes)"),
    ("B49_extend_genexp_arg", f"ActionKind.extend_genexp_arg({LIST})"),
    ("B50_extend_unproven_factory", f"ActionKind.extend_unproven({LIST})"),
    ("B51_append_max_arg", f"ActionKind.append_max({LIST})"),
    ("B56a_tuple_shadow_local", f"ActionKind.tuple_shadow({LIST}, codes)"),
    ("B59a_param_object_select", f"ActionKind.pick_objects({LIST})"),
    ("B59b_param_any_select", f"ActionKind.pick_any({LIST})"),
    ("B61_dup_name_class_attr", f"ActionKind.dup({LIST}, codes)"),
    ("B62_object_shadow_local", f"ActionKind.object_shadow({LIST}, codes)"),
]:
    case(nm, "red", BAD_LOOP.format(call=call))
case("B23_registry_scalar", "red", f"""
ActionKind.remember({LIST})
for kind in ActionKind.registry_elems(codes):
    kind.is_enabled = False
    self._repository.save(kind)
""")
case("B33_global_acc", "red", f"""
ActionKind.remember({LIST})
for kind in ActionKind.global_acc(codes):
    kind.is_enabled = False
    self._repository.save(kind)
""")
case("B34_class_pool", "red", f"""
ActionKind.remember({LIST})
for kind in ActionKind.class_pool(codes):
    kind.is_enabled = False
    self._repository.save(kind)
""")
for nm, cls, mod in [("B26_module_rebound_class", "ReboundKind", "rebound_kind"),
                     ("B56b_tuple_shadow_module", "ShadowKind", "shadow_kind"),
                     ("B57_dunder_new_pool", "CachedKind", "cached_kind"),
                     ("B58_metaclass_call", "MetaKind", "meta_kind"),
                     ("B63_cls_new_in_pool_class", "PooledKind", "pooled_kind"),
                     ("B65_decorator_name_shadow", "DecoShadowKind", "deco_shadow_kind")]:
    case(nm, "red", f"""
for kind in {cls}.open_many(codes):
    kind.is_enabled = False
    self._repository.save(kind)
""", imports=f"from application.orders.domain_layer.action_kind.{mod} import {cls}")
# (나) 인자 출처 공격 — 조회 포트가 리포지토리가 아니거나 호출자가 넘긴 인스턴스.
case("O1_bypass_query_arg", "red", """
for kind in ActionKind.enabled_among(self._query.list_all()):
    kind.is_enabled = False
    self._repository.save(kind)
""", init_extra=", query: ActionKindQuery", init_body="        self._query: ActionKindQuery = query\n",
     imports="from application.orders.application_layer.port.query.action_kind_query import ActionKindQuery")
case("O2_caller_passed_instances", "red", """
for kind in ActionKind.enabled_among(loaded):
    kind.is_enabled = False
    self._repository.save(kind)
""", params=", loaded: list[ActionKind]")

QUERY_PORT = '''from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from application.orders.domain_layer.action_kind.action_kind import ActionKind


class ActionKindQuery(ABC):
    @abstractmethod
    def list_all(self) -> Sequence[ActionKind]: ...
'''


def build(base: Path, trees: Path) -> list[tuple[str, str]]:
    """바탕 트리 base 에 탐침을 얹어 trees/<이름>/ 에 쓰고 (이름, 기대) 목록을 돌려준다."""
    if trees.exists():
        shutil.rmtree(trees)
    trees.mkdir()
    src0 = (base / DOM / "action_kind.py").read_text(encoding="utf-8")
    dom = src0.replace("from collections.abc import Sequence\n",
                       "from collections.abc import Sequence\n" + DOMAIN_HEADER_EXTRA, 1)
    dom = dom.replace("    def disable(self) -> None:", EXTRA_METHODS.lstrip("\n") + "    def disable(self) -> None:", 1)
    dom = dom.rstrip("\n") + "\n" + SUBCLASS
    assert "teller_like" in dom and "_launder" in dom
    rows = []
    for name, want, body, kw in CASES:
        t = trees / name
        shutil.copytree(base, t)
        shutil.rmtree(t / UC / "c_domain_seed_inline")
        (t / DOM / "action_kind.py").write_text(dom, encoding="utf-8")
        for fn, text in SIDE_MODULES.items():
            (t / DOM / fn).write_text(text, encoding="utf-8")
        qdir = t / "application/orders/application_layer/port/query"
        qdir.mkdir(parents=True, exist_ok=True)
        (qdir / "action_kind_query.py").write_text(QUERY_PORT, encoding="utf-8")
        low = name.lower()
        (t / UC / low).mkdir(parents=True)
        cls = "".join(p.capitalize() for p in low.split("_")) + "UseCase"
        imports = AK + ("\n" + kw["imports"] if "imports" in kw else "")
        src = HDR.format(imports=imports, cls=cls, params=kw.get("params", ""),
                         init_extra=kw.get("init_extra", ""), init_body=kw.get("init_body", ""),
                         body=textwrap.indent(textwrap.dedent(body).strip("\n"), " " * 12))
        (t / UC / low / f"{low}_use_case.py").write_text(src, encoding="utf-8")
        rows.append(f"{name}\t{want}")
    return [(r.split("\t")[0], r.split("\t")[1]) for r in rows]


if __name__ == "__main__":
    import sys
    print(f"{len(build(Path(sys.argv[1]), Path(sys.argv[2])))} trees → {sys.argv[2]}")
