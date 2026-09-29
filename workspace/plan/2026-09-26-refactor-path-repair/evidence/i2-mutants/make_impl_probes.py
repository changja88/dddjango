"""R8-I2 구현 리뷰·최종 재검토 탐침 — 무인자 경로(P1z 유지)·클래스 본문 데코레이터 가림(리뷰 M-2)·sorted/reversed
재배열·역순 반복자 별칭 누출(재검토 F-1)·모듈 함수 `global` 내장 가림(재검토 F-2).

바탕 = diag-D2 `c_domain_seed_inline` 트리(`base_tree.json`). 트리마다 유스케이스 1개.
기대: green = 원소가 도메인 본문에서 새로 태어난다 · red = 조회된(받은) 인스턴스가 원소로 샌다 ·
lim = 이상은 red 지만 문서화한 가정 밖(무인자 호출의 클래스·모듈 상태 세탁 — R8-D2 와 같다) ·
fc = 이상은 green 이지만 fail-closed red 를 받아들인다.
"""
from __future__ import annotations

import shutil
import textwrap
from pathlib import Path

DOM = "application/orders/domain_layer/action_kind"
UC = "application/orders/application_layer/action_kind"

HEADER_EXTRA = '''import functools
from typing import ClassVar

# 모듈 전역 공유 가변 list — 유스케이스가 조회 결과를 들일 수 있다(A40 모양).
_SHARED: list["ActionKind"] = []


def _kind(code: str, name: str) -> "ActionKind":
    """모듈 수준 생성 헬퍼."""
    return ActionKind(code=code, name=name)


def _smuggle(it: object, kinds: object) -> None:
    """역순 반복자에서 원본 list 를 꺼내 받은 인스턴스를 밀어 넣는다(__reduce__ 노출 · 재검토 F-1)."""
    it.__reduce__()[1][0][:0] = list(kinds)
'''

EXTRA_METHODS = '''    _STASH: ClassVar[list["ActionKind"]] = []

    # ── 무인자(선언만 본다 · P1z) ──
    @classmethod
    def remember(cls, kinds: Sequence[ActionKind]) -> None:
        cls._STASH.extend(kinds)

    @classmethod
    def remembered(cls) -> tuple[ActionKind, ...]:
        """클래스 속성에 담아 둔 인스턴스를 인자 없이 돌려준다(L1 모양)."""
        return tuple(cls._STASH)

    @classmethod
    def shared(cls) -> list[ActionKind]:
        """모듈 전역 공유 list 를 그대로 돌려준다(A40 모양)."""
        return _SHARED

    @classmethod
    def with_default(cls, pool: Sequence[ActionKind] = _SHARED) -> tuple[ActionKind, ...]:
        """기본값 인자로 모듈 전역을 받아 돌려준다 — 호출 지점은 무인자(L7 모양)."""
        return tuple(pool)

    @classmethod
    @functools.cache
    def cached_seeds(cls) -> tuple[ActionKind, ...]:
        """본문은 새로 짓지만 호출 사이에 같은 인스턴스를 돌려준다(L6 모양)."""
        return tuple(cls(code=code, name=name) for code, name in _SEED_ACTION_KINDS)

    @classmethod
    def sorted_catalog(cls) -> tuple[ActionKind, ...]:
        """무인자 · 새로 지은 원소를 정렬해 돌려준다(구현 리뷰 F1 모양)."""
        return tuple(sorted((cls(code=c, name=n) for c, n in _SEED_ACTION_KINDS), key=lambda k: k.code))

    @classmethod
    def helper_catalog(cls) -> tuple[ActionKind, ...]:
        """무인자 · 모듈 헬퍼로 짓는다(구현 리뷰 F4 모양 — 응용 쪽 같은 모양은 green)."""
        return tuple(_kind(c, n) for c, n in _SEED_ACTION_KINDS)

    # ── 인자 있음 · sorted/reversed 재배열 ──
    @classmethod
    def sorted_many(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        return tuple(sorted((cls(code=c, name=c) for c in codes), key=lambda k: k.code, reverse=True))

    @classmethod
    def reversed_acc(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = []
        for c in codes:
            items.append(cls(code=c, name=c))
        return tuple(reversed(items))

    @classmethod
    def sorted_acc_return(cls, codes: Sequence[str]) -> list[ActionKind]:
        items: list[ActionKind] = [cls(code=c, name=c) for c in codes]
        return sorted(items, key=lambda k: k.code)

    @classmethod
    def sorted_received(cls, kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return tuple(sorted(kinds, key=lambda k: k.code))

    @classmethod
    def sorted_mixed(cls, codes: Sequence[str], kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls(code=c, name=c) for c in codes]
        items.extend(kinds)
        return tuple(sorted(items, key=lambda k: k.code))

    @classmethod
    def reversed_concat(cls, codes: Sequence[str], kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        return tuple(reversed([cls(code=c, name=c) for c in codes] + list(kinds)))

    @classmethod
    def sorted_kwsplat(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        opts: dict[str, bool] = {"reverse": True}
        return tuple(sorted([cls(code=c, name=c) for c in codes], **opts))

    @classmethod
    def sorted_local_shadow(cls, codes: Sequence[str], kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        sorted = lambda xs, **kw: list(kinds)  # noqa: E731
        return tuple(sorted([cls(code=c, name=c) for c in codes]))

    # ── 인자 있음 · 역순 반복자(원본을 쥔다 · 재검토 F-1) ──
    @classmethod
    def reversed_smuggle(cls, codes: Sequence[str], kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls(code=c, name=c) for c in codes]
        _smuggle(reversed(items), kinds)
        return tuple(items)

    @classmethod
    def reversed_reduce_inline(cls, codes: Sequence[str], kinds: Sequence[ActionKind]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls(code=c, name=c) for c in codes]
        reversed(items).__reduce__()[1][0][:0] = list(kinds)
        return tuple(items)

    @classmethod
    def reversed_loop_read(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls(code=c, name=c) for c in codes]
        count: int = 0
        for k in reversed(items):
            count += len(k.code)
        return tuple(items) if count >= 0 else ()

    @classmethod
    def reversed_named_reused(cls, codes: Sequence[str]) -> tuple[ActionKind, ...]:
        items: list[ActionKind] = [cls(code=c, name=c) for c in codes]
        r = reversed(items)
        a = tuple(r)
        return a + tuple(r)

'''

# 클래스 본문에서 데코레이터 이름을 가린다(구현 리뷰 M-2 · X1 모양).
SIDE = {"deco_class_shadow_kind.py": '''from __future__ import annotations

import builtins
from collections.abc import Sequence
from dataclasses import dataclass

_SHARED: list["DecoClassShadowKind"] = []


def _launder(f: object) -> object:
    def g(cls: type, *a: object, **k: object) -> tuple["DecoClassShadowKind", ...]:
        return tuple(_SHARED)
    return builtins.classmethod(g)


@dataclass(kw_only=True)
class DecoClassShadowKind:
    code: str
    name: str
    is_enabled: bool = True

    classmethod = _launder

    @classmethod
    def open_many(cls, codes: Sequence[str]) -> list["DecoClassShadowKind"]:
        return [cls(code=code, name=code) for code in codes]

    @staticmethod
    def adopt(kinds: Sequence[object]) -> None:
        _SHARED.extend(kinds)
''',
        # 모듈 함수가 `global` 로 내장 `list` 를 다시 묶는다(재검토 F-2 · S_global_fn_tuple 모양).
        "global_shadow_kind.py": '''from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

_POOL: list["GlobalShadowKind"] = []


def _evil(xs: object) -> "tuple[GlobalShadowKind, ...]":
    return tuple(_POOL)


def _poison() -> None:
    global list
    list = _evil


_poison()


@dataclass(kw_only=True)
class GlobalShadowKind:
    code: str
    name: str
    is_enabled: bool = True

    @classmethod
    def open_many(cls, codes: Sequence[str]) -> tuple["GlobalShadowKind", ...]:
        return tuple(list([cls(code=c, name=c) for c in codes]))

    @staticmethod
    def adopt(kinds: Sequence[object]) -> None:
        _POOL.extend(kinds)
'''}

HDR = '''from __future__ import annotations

from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
from application.orders.domain_layer.action_kind.action_kind import ActionKind
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

GOOD = """
for kind in {call}:
    self._repository.save(kind)
"""
BAD = """
for kind in {call}:
    kind.is_enabled = False
    self._repository.save(kind)
"""
LIST = "self._repository.list_all()"
DECO = "from application.orders.domain_layer.action_kind.deco_class_shadow_kind import DecoClassShadowKind"

CASES: list[tuple[str, str, str, str]] = [
    # 무인자 — 선언 전파(P1z) 그대로
    ("N0_noarg_seed", "green", GOOD.format(call="ActionKind.seed_catalog()"), ""),
    ("N0b_noarg_append", "green", GOOD.format(call="ActionKind.append_catalog()"), ""),
    ("N1_noarg_class_stash", "lim", f"ActionKind.remember({LIST})\n" + BAD.format(call="ActionKind.remembered()"), ""),
    ("N2_noarg_module_list", "lim",
     f"ActionKind.shared().extend({LIST})\n" + BAD.format(call="ActionKind.shared()"), ""),
    ("N3_noarg_default_param", "lim",
     f"ActionKind.shared().extend({LIST})\n" + BAD.format(call="ActionKind.with_default()"), ""),
    ("N4_noarg_prebuilt", "lim", GOOD.format(call="ActionKind.prebuilt_catalog()"), ""),
    ("N5_noarg_functools_cache", "lim", GOOD.format(call="ActionKind.cached_seeds()"), ""),
    ("N6_noarg_sorted", "green", GOOD.format(call="ActionKind.sorted_catalog()"), ""),
    ("N7_noarg_module_helper", "green", GOOD.format(call="ActionKind.helper_catalog()"), ""),
    # 인자 있음 — 클래스 본문 데코레이터 가림
    ("D1_classbody_decorator_shadow", "red",
     f"DecoClassShadowKind.adopt({LIST})\n" + BAD.format(call="DecoClassShadowKind.open_many(codes)"), DECO),
    # 인자 있음 — sorted/reversed 재배열
    ("S1_sorted_key_reverse", "green", GOOD.format(call="ActionKind.sorted_many(codes)"), ""),
    ("S2_reversed_acc", "green", GOOD.format(call="ActionKind.reversed_acc(codes)"), ""),
    ("S3_sorted_acc_return", "green", GOOD.format(call="ActionKind.sorted_acc_return(codes)"), ""),
    ("S4_sorted_received", "red", BAD.format(call=f"ActionKind.sorted_received({LIST})"), ""),
    ("S5_sorted_mixed", "red", BAD.format(call=f"ActionKind.sorted_mixed(codes, {LIST})"), ""),
    ("S6_reversed_concat_received", "red", BAD.format(call=f"ActionKind.reversed_concat(codes, {LIST})"), ""),
    ("S7_sorted_kwsplat", "fc", GOOD.format(call="ActionKind.sorted_kwsplat(codes)"), ""),
    ("S8_sorted_local_shadow", "red", BAD.format(call=f"ActionKind.sorted_local_shadow(codes, {LIST})"), ""),
    # 인자 있음 — 역순 반복자(재검토 F-1)
    ("R1_reversed_iter_smuggle", "red", BAD.format(call=f"ActionKind.reversed_smuggle(codes, {LIST})"), ""),
    ("R2_reversed_reduce_inline", "red", BAD.format(call=f"ActionKind.reversed_reduce_inline(codes, {LIST})"), ""),
    ("R3_reversed_loop_read", "green", GOOD.format(call="ActionKind.reversed_loop_read(codes)"), ""),
    ("R4_reversed_named_reused", "fc", GOOD.format(call="ActionKind.reversed_named_reused(codes)"), ""),
    # 인자 있음 — 모듈 함수 `global` 내장 가림(재검토 F-2)
    ("G1_module_fn_global_builtin", "red",
     f"GlobalShadowKind.adopt({LIST})\n" + BAD.format(call="GlobalShadowKind.open_many(codes)"),
     "from application.orders.domain_layer.action_kind.global_shadow_kind import GlobalShadowKind"),
]


def build(base: Path, trees: Path) -> list[tuple[str, str]]:
    """바탕 트리 base 에 탐침을 얹어 trees/<이름>/ 에 쓰고 (이름, 기대) 목록을 돌려준다."""
    if trees.exists():
        shutil.rmtree(trees)
    trees.mkdir()
    src0 = (base / DOM / "action_kind.py").read_text(encoding="utf-8")
    dom = src0.replace("from dataclasses import dataclass\n", "from dataclasses import dataclass\n" + HEADER_EXTRA, 1)
    dom = dom.replace("    def disable(self) -> None:", EXTRA_METHODS + "    def disable(self) -> None:", 1)
    assert "_SHARED" in dom and "sorted_local_shadow" in dom
    compile(dom, "action_kind.py", "exec")
    for text in SIDE.values():
        compile(text, "side.py", "exec")
    rows = []
    for name, want, body, imports in CASES:
        t = trees / name
        shutil.copytree(base, t)
        shutil.rmtree(t / UC / "c_domain_seed_inline")
        (t / DOM / "action_kind.py").write_text(dom, encoding="utf-8")
        for fn, text in SIDE.items():
            (t / DOM / fn).write_text(text, encoding="utf-8")
        low = name.lower()
        (t / UC / low).mkdir(parents=True)
        cls = "".join(p.capitalize() for p in low.split("_")) + "UseCase"
        src = HDR.format(cls=cls, imports=imports,
                         body=textwrap.indent(textwrap.dedent(body).strip("\n"), " " * 12))
        compile(src, name, "exec")
        (t / UC / low / f"{low}_use_case.py").write_text(src, encoding="utf-8")
        rows.append((name, want))
    return rows


if __name__ == "__main__":
    import sys
    print(f"{len(build(Path(sys.argv[1]), Path(sys.argv[2])))} trees → {sys.argv[2]}")
