#!/usr/bin/env python3
"""behavior_guard.py 픽스처 러너 — 합성 git 저장소로 0C/0T 판정·마이그레이션·창 절차를 고정한다(로드맵 4 · 설계 v4 §4).

각 사례는 새 임시 저장소에서 «기준 커밋 → open → 편집(커밋 또는 작업 트리) → close» 를 돌려 exit 와 요약을 대조한다.
현장 재생(spring_dream 5커밋 green · 계약 변경 7커밋 red)은 구현 리뷰 기록(scratch)이 맡고, 여기서는 규칙마다 양성·음성을 둔다.
기능 모드 사례(`--mode feature`)는 지금 판정 그대로다. 리팩토링 모드 사례(설계 v15.2 §4 · §8 B0 «+약 40»)는 처분 · r4 · r5 · 보충 ·
감사 단위 · 묶음 자료 · D · 감사 키 · DB · 창을 보고, 모든 사례에서 «바이트가 바뀐 시험 쪽 파일 수 = 감사 키 낸 파일 + red 파일»
(자동 초록 0)을 따로 센다. G1 스냅숏(refactor_audit.changes_snapshot)은 사례가 정한 값을 돌려주는 대역으로 바꿔 끼운다(명세
판형은 refactor_audit 픽스처 몫) — `--stub-support` 면 behavior_support 도 k0 서명 그대로의 대역을 쓴다.
exit 0 = 전건 기대 일치 · 1 = 불일치.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

ROOT: Path = Path(__file__).resolve().parents[2]
GUARD: Path = ROOT / "dddjango" / "scripts" / "behavior_guard.py"

BASE: "dict[str, str]" = {
    "pyproject.toml": '[project]\nname = "x"\n\n[tool.pytest.ini_options]\nDJANGO_SETTINGS_MODULE = "proj.settings"\n'
                      'testpaths = ["app"]\n',
    "app/__init__.py": "",
    "app/core/__init__.py": "",
    "app/core/apps.py": 'class CoreConfig:\n    name = "app.core"\n    label: str = "core"\n',
    "app/core/money.py": ('"""돈."""\nfrom dataclasses import dataclass\n\n\n@dataclass(frozen=True)\nclass Money:\n'
                          '    v: int\n\n    def add(self, other: "Money") -> "Money":\n        return Money(self.v + other.v)\n'),
    "app/core/service.py": "from app.core.money import Money\n\n\ndef total(a: int, b: int) -> int:\n"
                           "    return Money(a).add(Money(b)).v\n",
    "app/core/other.py": "class Money:\n    def __init__(self, v: int) -> None:\n        self.v = v * 2\n",
    "app/core/migrations/__init__.py": "",
    "app/core/migrations/0001_initial.py": "class Migration:\n    initial = True\n",
    "app/support/__init__.py": "",
    "app/support/helpers.py": "def make(v: int) -> int:\n    return v\n",
    "app/test/__init__.py": "",
    "app/test/golden.json": '{"total": 3}\n',
    "app/test/factories/__init__.py": "",
    "app/test/factories/money_factory.py": "from app.core.money import Money\n\n\ndef money(v: int = 1) -> Money:\n"
                                           "    return Money(v)\n",
    "app/test/test_money.py": ('from unittest import mock\n\nfrom app.core.money import Money\nfrom app.support.helpers import make\n\n\n'
                               'def test_add() -> None:\n    assert Money(1).add(Money(2)).v == 3\n\n\n'
                               'def test_patch() -> None:\n    with mock.patch("app.core.money.Money.add") as m:\n'
                               '        Money(1).add(Money(make(2)))\n    assert m.called\n'),
    "app/test/test_service.py": ("from app.core.service import total\nfrom app.test.factories.money_factory import money\n\n\n"
                                 "def test_total() -> None:\n    assert total(1, 2) == 3\n\n\n"
                                 "def test_factory() -> None:\n    assert money(3).v == 3\n"),
}
SCOPE: str = "실행 · G0 승인 20260927-0300\n\n- r1 · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(0300)\n"
FOLDER: str = ".dddjango/f"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def _write(repo: Path, files: "dict[str, str | None]") -> None:
    for rel, body in files.items():
        target: Path = repo / rel
        if body is None:
            target.unlink()
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")


def _repo(td: Path, pre: "dict[str, str | None] | None" = None) -> Path:
    repo: Path = td / "r"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    _write(repo, {k: v for k, v in {**BASE, **(pre or {})}.items() if v is not None})
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    folder: Path = repo / FOLDER
    folder.mkdir(parents=True)
    (folder / "refactor-scope.md").write_text(SCOPE, encoding="utf-8")
    (folder / "build_anchor").write_text(_git(repo, "rev-parse", "HEAD"), encoding="utf-8")
    return repo


def _guard(repo: Path, *args: str) -> "tuple[int, str]":
    proc = subprocess.run([sys.executable, str(GUARD), args[0], FOLDER, *args[1:]], cwd=repo, capture_output=True,
                          text=True)
    return proc.returncode, proc.stdout + proc.stderr


def _commit(repo: Path, message: str = "edit") -> None:
    _git(repo, "add", "-A", "--", ".", ":!.dddjango")
    _git(repo, "commit", "-qm", message)


def moved_money(pkg: str = "app/shared") -> "dict[str, str | None]":
    body: str = BASE["app/core/money.py"]
    return {"app/core/money.py": None, f"{pkg}/__init__.py": "", f"{pkg}/money.py": body,
            "app/core/service.py": BASE["app/core/service.py"].replace("app.core.money", pkg.replace("/", ".") + ".money")}


def with_test_paths(files: "dict[str, str | None]", old: str, new: str) -> "dict[str, str | None]":
    out: "dict[str, str | None]" = dict(files)
    for rel in ("app/test/test_money.py", "app/test/factories/money_factory.py"):
        out[rel] = BASE[rel].replace(old, new)
    return out


# (라벨, open 종류, 편집 함수, 커밋 여부, 기대 exit, 요약·출력에 있어야 할 문구)
Case = "tuple[str, str, Callable[[Path], None], bool, int, str]"


def cases() -> "list[tuple]":
    renamed: str = BASE["app/core/money.py"].replace("class Money", "class Amount").replace('"Money"', '"Amount"') \
        .replace("return Money(", "return Amount(")
    promote: "dict[str, str | None]" = {
        "app/core/money.py": None, "app/core/money/__init__.py": "",
        "app/core/money/money.py": BASE["app/core/money.py"],
        "app/core/service.py": BASE["app/core/service.py"].replace("app.core.money", "app.core.money.money")}
    return [
        # ── 0C 음성(green) ──
        ("0C 모듈 이동 + import·patch 문자열 치환", "code",
         lambda r: _write(r, with_test_paths(moved_money(), "app.core.money", "app.shared.money")), True, 0, "close green"),
        ("0C 작업 트리(미커밋) 이동도 같다", "code",
         lambda r: _write(r, with_test_paths(moved_money(), "app.core.money", "app.shared.money")), False, 0, "close green"),
        ("0C 파일→패키지 승격(후속 모듈)", "code",
         lambda r: _write(r, with_test_paths(promote, "app.core.money", "app.core.money.money")), True, 0, "close green"),
        ("0C isort 재배열 + 치환", "code",
         lambda r: _write(r, {**moved_money(), "app/test/test_money.py": BASE["app/test/test_money.py"]
                              .replace("from app.core.money import Money\nfrom app.support.helpers import make\n",
                                       "from app.support.helpers import make\nfrom app.shared.money import Money\n")
                              .replace('"app.core.money.Money.add"', '"app.shared.money.Money.add"'),
                              "app/test/factories/money_factory.py": BASE["app/test/factories/money_factory.py"]
                              .replace("app.core.money", "app.shared.money")}), True, 0, "close green"),
        ("0C 이름 대응 개명(결정 9)", "code",
         lambda r: _write(r, {"app/core/money.py": renamed,
                              "app/core/service.py": BASE["app/core/service.py"].replace("Money", "Amount"),
                              "app/test/test_money.py": BASE["app/test/test_money.py"].replace("Money", "Amount"),
                              "app/test/factories/money_factory.py": BASE["app/test/factories/money_factory.py"]
                              .replace("Money", "Amount")}), True, 0, "개명 1"),
        ("0C 분류 경계 이동(제품 → 테스트 자리 · 분류 중립)", "code",
         lambda r: _write(r, {"app/support/helpers.py": None, "app/test/support/__init__.py": "",
                              "app/test/support/helpers.py": BASE["app/support/helpers.py"],
                              "app/test/test_money.py": BASE["app/test/test_money.py"]
                              .replace("app.support.helpers", "app.test.support.helpers")}), True, 0, "close green"),
        ("0C 제품만 변경(테스트 무접촉)", "code",
         lambda r: _write(r, {"app/core/service.py": BASE["app/core/service.py"] + "\n\nX = 1\n"}), True, 0, "close green"),
        # ── 0C 양성(red) ──
        ("0C 단언 변경", "code",
         lambda r: _write(r, {"app/test/test_money.py": BASE["app/test/test_money.py"].replace("== 3", "== 4")}),
         True, 2, "치환으로 설명되지 않는"),
        ("0C 동명 다른 정의로 재결합", "code",
         lambda r: _write(r, {"app/test/test_money.py": BASE["app/test/test_money.py"]
                              .replace("from app.core.money import Money", "from app.core.other import Money")}),
         True, 2, "참조 −"),
        ("0C 대응표 밖 patch 대상", "code",
         lambda r: _write(r, with_test_paths(moved_money(), "app.core.money", "app.shared.money")
                          | {"app/test/test_money.py": BASE["app/test/test_money.py"]
                             .replace("app.core.money import", "app.shared.money import")
                             .replace('"app.core.money.Money.add"', '"app.core.service.total"')}), True, 2, "치환으로"),
        ("0C golden 수정", "code",
         lambda r: _write(r, {"app/test/golden.json": '{"total": 4}\n'}), True, 2, "비 .py 오라클"),
        ("0C pytest 설정 수정", "code",
         lambda r: _write(r, {"pyproject.toml": BASE["pyproject.toml"].replace('["app"]', '["app/core"]')}),
         True, 2, "pytest 설정 변경"),
        ("0C 테스트 추가", "code",
         lambda r: _write(r, {"app/test/test_new.py": "def test_x() -> None:\n    assert True\n"}), True, 2, "테스트 파일 추가"),
        ("0C 마이그레이션 수정", "code",
         lambda r: _write(r, {"app/core/migrations/0001_initial.py": "class Migration:\n    initial = False\n"}),
         True, 2, "마이그레이션 수정"),
        ("0C 앱 재배치(라벨 같음 — 마이그레이션 무변)", "code",
         lambda r: _write(r, {"app/core/apps.py": None, "app/core/migrations/__init__.py": None,
                              "app/core/migrations/0001_initial.py": None,
                              "driven/django_core/apps.py": BASE["app/core/apps.py"],
                              "driven/django_core/migrations/__init__.py": "",
                              "driven/django_core/migrations/0001_initial.py": BASE["app/core/migrations/0001_initial.py"]}),
         True, 0, "마이그레이션 정적 무변"),
        # ── 0T ──
        ("0T factories 이동 + 테스트 import 수정", "test",
         lambda r: _write(r, {"app/test/factories/money_factory.py": None, "app/test/fake/__init__.py": "",
                              "app/test/fake/money_factory.py": BASE["app/test/factories/money_factory.py"],
                              "app/test/test_service.py": BASE["app/test/test_service.py"]
                              .replace("app.test.factories", "app.test.fake")}), True, 0, "close green"),
        ("0T 제품 1줄 수정", "test",
         lambda r: _write(r, {"app/core/service.py": BASE["app/core/service.py"].replace("a: int", "a: int ")
                              + "# x\n"}), True, 2, "제품 쪽 변경"),
        ("0T 케이스 삭제", "test",
         lambda r: _write(r, {"app/test/test_service.py": BASE["app/test/test_service.py"].split("\n\n\ndef test_factory")[0]
                              + "\n"}), True, 2, "케이스 감소"),
        ("0T 케이스 삭제(G1 remove 행)", "test",
         lambda r: (_write(r, {"app/test/test_service.py": BASE["app/test/test_service.py"]
                               .split("\n\n\ndef test_factory")[0] + "\n"}),
                    (r / FOLDER / "design-spec.md").write_text(
                        "| decision | owner/path |\n|---|---|\n| remove | `app/test/test_service.py::test_factory` |\n",
                        encoding="utf-8")), True, 0, "close green"),
        ("0T 케이스 추가", "test",
         lambda r: _write(r, {"app/test/test_service.py": BASE["app/test/test_service.py"]
                              + "\n\ndef test_more() -> None:\n    assert True\n"}), True, 2, "케이스 추가"),
    ] + review_j_cases()


def _move(repo: Path, old: str, new: str, *subs: "tuple[str, str]") -> None:
    body: str = (repo / old).read_text(encoding="utf-8")
    (repo / old).unlink()
    for a, b in subs:
        body = body.replace(a, b)
    _write(repo, {new: body})


# 구현 리뷰 J 반례(2026-09-27) — 디렉터리·패키지 이동 · 정의 이동 · 연쇄 개명(거짓 red 였다) · 이름 문자열 · 수집 밖 이동 ·
# unittest 클래스 · remove 칸(거짓 green 이었다). 사례마다 기준 커밋에 더할 파일(pre)을 둔다.
BC: "dict[str, str | None]" = {
    "app/bc/__init__.py": "", "app/bc/domain.py": "def price(v: int) -> int:\n    return v * 2\n",
    "app/bc/test/__init__.py": "", "app/bc/test/unit/__init__.py": "",
    "app/bc/test/unit/README.md": "run: pytest app/bc/test/unit\n",
    "app/bc/test/unit/test_domain.py": ('"""app/bc/test/unit/test_domain.py — app.bc.domain 검증."""\n'
                                        "from app.bc.domain import price\n\n\ndef test_price() -> None:\n"
                                        "    assert price(2) == 4, 'see app/bc/domain.py'\n"),
}
PORT: "dict[str, str | None]" = {
    "app/core/port/__init__.py": "",
    "app/core/port/money_out.py": "from dataclasses import dataclass\n\n\n@dataclass(frozen=True)\nclass MoneyOut:\n    v: int\n",
    "app/core/port/money_port.py": ("from app.core.port.money_out import MoneyOut\n\n\nclass MoneyPort:\n"
                                    "    def get(self) -> MoneyOut:\n        raise NotImplementedError\n"),
    "app/test/fake/__init__.py": "",
    "app/test/fake/money_port.py": ("from app.core.port.money_out import MoneyOut\nfrom app.core.port.money_port import MoneyPort\n"
                                    "\n\nclass FakeMoneyOutPort(MoneyPort):\n    def get(self) -> MoneyOut:\n        return MoneyOut(1)\n"),
    "app/test/test_port.py": ("from app.core.port import money_out\nfrom app.test.fake.money_port import FakeMoneyOutPort\n\n\n"
                              "def test_get() -> None:\n    assert FakeMoneyOutPort().get() == money_out.MoneyOut(1)\n"),
}
ERR: "dict[str, str | None]" = {
    "app/core/errors.py": "class InsufficientFunds(Exception):\n    pass\n",
    "app/core/api.py": "def handle(exc: Exception) -> str:\n    return type(exc).__name__\n",
    "app/test/test_errors.py": ("from app.core.api import handle\nfrom app.core.errors import InsufficientFunds\n\n\n"
                                "def test_code() -> None:\n    assert handle(InsufficientFunds()) == \"InsufficientFunds\"\n"),
}


def _bc_move(r: Path) -> None:
    for p in [k for k in BC]:
        _move(r, p, p.replace("app/bc/", "app/pricing/"), ("app.bc.", "app.pricing."), ("app/bc/", "app/pricing/"))


def _port_rename(r: Path) -> None:
    _move(r, "app/core/port/money_out.py", "app/core/port/money_in.py", ("MoneyOut", "MoneyIn"))
    _move(r, "app/test/fake/money_port.py", "app/test/fake/money_in_port.py", ("money_out", "money_in"),
          ("MoneyOut", "MoneyIn"))
    for rel in ("app/core/port/money_port.py", "app/test/test_port.py"):
        _write(r, {rel: (r / rel).read_text(encoding="utf-8").replace("money_out", "money_in").replace("MoneyOut", "MoneyIn")
                   .replace("app.test.fake.money_port", "app.test.fake.money_in_port")})


def review_j_cases() -> "list[tuple]":
    return [
        ("0C BC 패키지 통째 이동(빈 __init__·README·자기 경로 문자열·docstring)", "code", _bc_move, True, 0, "close green", BC),
        ("0C 정의 부분 이동 + 모듈 속성 접근(calc.add → arith.add)", "code",
         lambda r: _write(r, {"app/core/calc.py": "def mul(a: int, b: int) -> int:\n    return a * b\n",
                              "app/core/arith.py": "def add(a: int, b: int) -> int:\n    return a + b\n",
                              "app/test/test_calc.py": "from app.core import arith, calc\n\n\ndef test_add() -> None:\n"
                                                       "    assert arith.add(1, 2) == 3 and calc.mul(2, 3) == 6\n"}),
         True, 0, "close green",
         {"app/core/calc.py": "def add(a: int, b: int) -> int:\n    return a + b\n\n\ndef mul(a: int, b: int) -> int:\n"
                              "    return a * b\n",
          "app/test/test_calc.py": "from app.core import calc\n\n\ndef test_add() -> None:\n"
                                   "    assert calc.add(1, 2) == 3 and calc.mul(2, 3) == 6\n"}),
        ("0C 재수출 __init__ 패키지 이동(from app.wallet import Coin)", "code",
         lambda r: (_move(r, "app/wallet/coin.py", "app/purse/coin.py"),
                    _move(r, "app/wallet/__init__.py", "app/purse/__init__.py", ("app.wallet", "app.purse")),
                    _write(r, {"app/test/test_wallet.py": "from app.purse import Coin\n\n\ndef test_coin() -> None:\n"
                                                          "    assert Coin.v == 1\n"})),
         True, 0, "close green",
         {"app/wallet/__init__.py": "from app.wallet.coin import Coin\n", "app/wallet/coin.py": "class Coin:\n    v: int = 1\n",
          "app/test/test_wallet.py": "from app.wallet import Coin\n\n\ndef test_coin() -> None:\n    assert Coin.v == 1\n"}),
        ("0C `_out`→`_in` 모듈·클래스 개명 + 페이크 연쇄 개명(결정 7·9 · #577)", "code", _port_rename, True, 0, "close green",
         PORT),
        ("0C 개명 + 같은 파일의 무관 문자열 \"create\" 은 그대로", "code",
         lambda r: _write(r, {"app/core/orders.py": "def create_order(n: int) -> dict:\n    return {\"n\": n}\n",
                              "app/test/test_orders.py": "from app.core.orders import create_order\n\n\ndef test_c() -> None:\n"
                                                         "    assert create_order(1)[\"n\"] == 1 and {\"action\": \"create\"}\n"}),
         True, 0, "개명 1",
         {"app/core/orders.py": "def create(n: int) -> dict:\n    return {\"n\": n}\n",
          "app/test/test_orders.py": "from app.core.orders import create\n\n\ndef test_c() -> None:\n"
                                     "    assert create(1)[\"n\"] == 1 and {\"action\": \"create\"}\n"}),
        ("0C 모듈 상수 개명(MAX_RETRY → RETRY_LIMIT)", "code",
         lambda r: _write(r, {"app/core/limits.py": "RETRY_LIMIT = 3\n",
                              "app/test/test_limits.py": "from app.core.limits import RETRY_LIMIT\n\n\ndef test_l() -> None:\n"
                                                         "    assert RETRY_LIMIT == 3\n"}), True, 0, "개명 1",
         {"app/core/limits.py": "MAX_RETRY = 3\n",
          "app/test/test_limits.py": "from app.core.limits import MAX_RETRY\n\n\ndef test_l() -> None:\n"
                                     "    assert MAX_RETRY == 3\n"}),
        ("0C 옮긴 함수를 따라간 마이그레이션 import 경로 수정", "code",
         lambda r: (_move(r, "app/core/paths.py", "app/core/storage/paths.py"), _write(r, {
             "app/core/storage/__init__.py": "",
             "app/core/migrations/0002_avatar.py": "import app.core.storage.paths\n\n\nclass Migration:\n"
                                                   "    upload_to = app.core.storage.paths.avatar_path\n"})),
         True, 0, "close green",
         {"app/core/paths.py": "def avatar_path(instance, filename):\n    return 'a/' + filename\n",
          "app/core/migrations/0002_avatar.py": "import app.core.paths\n\n\nclass Migration:\n"
                                                "    upload_to = app.core.paths.avatar_path\n"}),
        ("0C 개명 + 관찰 이름(type(e).__name__) 단언을 따라 고침", "code",
         lambda r: _write(r, {"app/core/errors.py": "class NotEnoughFunds(Exception):\n    pass\n",
                              "app/test/test_errors.py": ERR["app/test/test_errors.py"]
                              .replace("InsufficientFunds", "NotEnoughFunds")}), True, 2, "치환으로", ERR),
        ("0C 테스트 파일을 수집 밖 이름으로 이동", "code",
         lambda r: _move(r, "app/test/test_money.py", "app/test/money_cases.py"), True, 2, "수집 밖"),
        ("0T unittest 클래스(MoneyTests(TestCase)) 케이스 삭제", "test",
         lambda r: _write(r, {"app/test/test_ut.py": "from django.test import TestCase\n\n\nclass MoneyTests(TestCase):\n"
                                                     "    def test_a(self) -> None:\n        self.assertEqual(1, 1)\n"}),
         True, 2, "MoneyTests::test_b",
         {"app/test/test_ut.py": "from django.test import TestCase\n\n\nclass MoneyTests(TestCase):\n"
                                 "    def test_a(self) -> None:\n        self.assertEqual(1, 1)\n\n"
                                 "    def test_b(self) -> None:\n        self.assertEqual(2, 2)\n"}),
        ("0T remove 행의 coverage 칸 테스트까지 삭제", "test",
         lambda r: (_write(r, {"app/test/test_service.py": "\n"}), (r / FOLDER / "design-spec.md").write_text(
             "| candidate | protected | failure | existing authoritative coverage | decision | owner/path |\n"
             "|---|---|---|---|---|---|\n| f | c | x | `app/test/test_service.py::test_total` | remove | "
             "`app/test/test_service.py::test_factory` |\n", encoding="utf-8")), True, 2, "test_service.py::test_total"),
        ("0T pytest 설정 절 수정(설정 ⓐ)", "test",
         lambda r: _write(r, {"pyproject.toml": BASE["pyproject.toml"] + 'addopts = "-p no:cacheprovider"\n'}),
         True, 0, "pytest 설정 절 변경"),
    ]


def run_case(label: str, kind: str, edit: "Callable[[Path], None]", commit: bool, want: int, needle: str,
             pre: "dict[str, str | None] | None" = None) -> "str | None":
    with tempfile.TemporaryDirectory(prefix="bg-fx-") as td:
        repo: Path = _repo(Path(td), pre)
        code, out = _guard(repo, "open", "--kind", kind, "--mode", "feature")
        if code != 0:
            return f"{label}: open exit {code}\n{out}"
        edit(repo)
        if commit:
            _commit(repo)
        code, out = _guard(repo, "close")
        if code != want or needle not in out:
            return f"{label}: close exit {code} (기대 {want} · «{needle}»)\n{out}"
    return None


def procedure_checks() -> "list[str]":
    fails: "list[str]" = []
    with tempfile.TemporaryDirectory(prefix="bg-proc-") as td:
        repo: Path = _repo(Path(td))
        anchor: Path = repo / FOLDER / "build_anchor"
        saved: str = anchor.read_text(encoding="utf-8")
        anchor.unlink()
        code, out = _guard(repo, "open", "--kind", "code", "--mode", "feature")
        if code != 1 or "build_anchor" not in out:
            fails.append(f"앵커 선행: exit {code}\n{out}")
        anchor.write_text(saved, encoding="utf-8")
        code, out = _guard(repo, "verify")
        if code != 2 or "창 누락" not in out:
            fails.append(f"verify 창 누락: exit {code}\n{out}")
        _guard(repo, "open", "--kind", "code", "--mode", "feature")
        code, out = _guard(repo, "open", "--kind", "code", "--mode", "feature")
        if code != 1 or "열린 창" not in out:
            fails.append(f"재open 거부: exit {code}\n{out}")
        code, out = _guard(repo, "verify")
        if code != 2 or "열린 창" not in out:
            fails.append(f"verify 열린 창: exit {code}\n{out}")
        _write(repo, {"app/test/test_money.py": BASE["app/test/test_money.py"].replace("== 3", "== 4")})
        code, out = _guard(repo, "close")
        if code != 2:
            fails.append(f"close red: exit {code}\n{out}")
        _write(repo, {"app/test/test_money.py": BASE["app/test/test_money.py"]})  # 철회
        code, out = _guard(repo, "close")
        if code != 0 or "판정 2회째" not in out:
            fails.append(f"철회 뒤 close 재실행: exit {code}\n{out}")
        code, out = _guard(repo, "verify")
        if code != 0 or "동작 보존 green" not in out:
            fails.append(f"verify green: exit {code}\n{out}")
        code, out = _guard(repo, "open", "--kind", "test", "--mode", "feature")
        if code != 0 or "w2" not in out:
            fails.append(f"두 번째 창: exit {code}\n{out}")
    with tempfile.TemporaryDirectory(prefix="bg-proc2-") as td:  # ⓐ 재상정만 — 해당 없음
        repo = _repo(Path(td))
        (repo / FOLDER / "refactor-scope.md").write_text(SCOPE + "\n## ⓐ 재상정 20260927-0310\n- r1 · 결정 = 작업 중단\n",
                                                          encoding="utf-8")
        code, out = _guard(repo, "verify")
        if code != 0 or "해당 없음" not in out:
            fails.append(f"verify 재상정: exit {code}\n{out}")
    with tempfile.TemporaryDirectory(prefix="bg-merge-") as td:  # 창 안 머지 — 경로 제외 · 겹침 exit 1
        repo = _repo(Path(td))
        _git(repo, "checkout", "-qb", "up")
        _write(repo, {"app/core/other.py": BASE["app/core/other.py"] + "\nY = 2\n"})
        _commit(repo, "upstream")
        _git(repo, "checkout", "-q", "main")
        _guard(repo, "open", "--kind", "test", "--mode", "feature")
        _write(repo, {"app/test/golden.json": '{"total": 3, "x": 1}\n'})
        _commit(repo, "lane")
        _git(repo, "merge", "-q", "--no-ff", "--no-edit", "up")
        code, out = _guard(repo, "close")
        if code != 2 or "미승인 머지" not in out:
            fails.append(f"미승인 머지 = 레인 편집: exit {code}\n{out}")
        (repo / FOLDER / "approved-merges.txt").write_text(_git(repo, "rev-parse", "HEAD").strip() + " up\n",
                                                           encoding="utf-8")
        code, out = _guard(repo, "close")
        if code != 0 or "머지 제외 1경로" not in out:
            fails.append(f"승인 머지 경로 제외: exit {code}\n{out}")
    with tempfile.TemporaryDirectory(prefix="bg-side-") as td:  # 레인 곁가지 약화 → 자기 머지(미승인) = 판정 대상
        repo = _repo(Path(td))
        _guard(repo, "open", "--kind", "code", "--mode", "feature")
        _git(repo, "checkout", "-qb", "side")
        _write(repo, {"app/test/test_money.py": BASE["app/test/test_money.py"].replace("== 3", "== 3 or True")})
        _commit(repo, "weaken")
        _git(repo, "checkout", "-q", "main")
        _git(repo, "merge", "-q", "--no-ff", "--no-edit", "side")
        code, out = _guard(repo, "close")
        if code != 2 or "치환으로" not in out:
            fails.append(f"곁가지 머지 세탁: exit {code}\n{out}")
    with tempfile.TemporaryDirectory(prefix="bg-reset-") as td:  # 창 기준 커밋이 조상이 아니다(reset·rebase) → exit 1
        repo = _repo(Path(td))
        _write(repo, {"app/core/other.py": BASE["app/core/other.py"] + "\nY = 2\n"})
        _commit(repo, "lane 1")
        _guard(repo, "open", "--kind", "code", "--mode", "feature")
        _git(repo, "reset", "-q", "--hard", "HEAD~1")
        _write(repo, {"app/core/other.py": BASE["app/core/other.py"] + "\nZ = 3\n"})
        _commit(repo, "lane 1 rewritten")
        code, out = _guard(repo, "close")
        if code != 1 or "조상이 아니다" not in out:
            fails.append(f"rebase·reset 판정 불가: exit {code}\n{out}")
    with tempfile.TemporaryDirectory(prefix="bg-merge2-") as td:
        repo = _repo(Path(td))
        _git(repo, "checkout", "-qb", "up")
        _write(repo, {"app/core/other.py": BASE["app/core/other.py"] + "\nY = 2\n"})
        _commit(repo, "upstream")
        _git(repo, "checkout", "-q", "main")
        _guard(repo, "open", "--kind", "code", "--mode", "feature")
        _write(repo, {"app/core/other.py": "Z = 1\n" + BASE["app/core/other.py"]})
        _commit(repo, "lane")
        subprocess.run(["git", "-C", str(repo), "merge", "-q", "--no-ff", "--no-edit", "up"], capture_output=True)
        if (repo / ".git" / "MERGE_HEAD").exists():  # 충돌이면 레인 쪽으로 해소
            _git(repo, "checkout", "--ours", "app/core/other.py")
            _commit(repo, "merge")
        (repo / FOLDER / "approved-merges.txt").write_text(_git(repo, "rev-parse", "HEAD").strip() + "\n", encoding="utf-8")
        code, out = _guard(repo, "close")
        if code != 1 or "머지 겹침" not in out:
            fails.append(f"머지 겹침: exit {code}\n{out}")
    with tempfile.TemporaryDirectory(prefix="bg-items-") as td:  # close 기록이 대응 원소(옛 → 새 경로)를 싣는다(로드맵 5 G2 잔존)
        repo = _repo(Path(td))
        _guard(repo, "open", "--kind", "code", "--mode", "feature")
        _write(repo, with_test_paths(moved_money(), "app.core.money", "app.shared.money"))
        _commit(repo)
        code, out = _guard(repo, "close")
        import json
        closes = json.loads((repo / FOLDER / "behavior" / "20260927-0300" / "w1-close.json").read_text(encoding="utf-8"))
        items = closes[-1].get("map_items") or {}
        if code != 0 or items.get("pairs", {}).get("app/core/money.py") != "app/shared/money.py" \
                or items.get("fm", {}).get("app/core/money.py") != "app/shared/money.py":
            fails.append(f"close 대응 원소 기록: exit {code} · map_items {items}\n{out}")
    return fails


# ── 리팩토링 모드(설계 v15.2 §4 · §8 B0 «behavior_guard_fixture_run.py +약 40») ─────────────────────────────

RFOLDER: str = ".dddjango/20261004-0300-refactor-core"
RUN: str = "20261004-0300"
AUDIT_STAMP: str = "20261004-0200"
RSCOPE: str = (f"실행 · G0 승인 {RUN} · 모드 리팩토링 · audit {AUDIT_STAMP}\n\n"
               "- M1 · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(0300)\n")
RUN_DEF: str = "aaaaaaaaaaaa"
TP: str = "application/core/test/test_check.py"
RB: "dict[str, str]" = {
    "pyproject.toml": '[project]\nname = "x"\n\n[tool.pytest.ini_options]\nDJANGO_SETTINGS_MODULE = "proj.settings"\n'
                      'testpaths = ["application"]\n',
    "application/__init__.py": "",
    "application/core/__init__.py": "",
    "application/core/apps.py": 'class CoreConfig:\n    name = "application.core"\n    label: str = "core"\n',
    "application/core/product.py": "class Old:\n    pass\n\n\ndef product():\n    return 9\n",
    "application/core/old.py": "def product():\n    return 9\n",
    "application/core/real.py": "def product():\n    return 9\n",
    "application/core/fake_impl.py": "def product():\n    return 5\n",
    "application/core/migrations/__init__.py": "",
    "application/core/migrations/0001_initial.py": "from django.db import migrations\n\n\nclass Migration(migrations.Migration):\n"
                                                   "    initial = True\n    operations = []\n",
    "application/core/test/__init__.py": "",
    "application/billing/__init__.py": "",
    "application/billing/api.py": "def charge():\n    return 1\n",
}
RENAME: "dict[str, str | None]" = {"application/core/product.py": "class New:\n    pass\n\n\ndef product():\n    return 9\n"}
MOVE: "dict[str, str | None]" = {"application/core/old.py": None, "application/core/new.py": "def product():\n    return 9\n"}
SIMPLE: str = "from application.core.product import product\n\n\ndef test_check():\n    assert product() == 9\n"

STUB_AUDIT: str = r'''"""refactor_audit 대역(behavior_guard 픽스처 · k0 §4-4 서명) — 승인판 스냅숏은 사례가 `<폴더>/stub-snapshot.json` 에 둔다."""
import hashlib
import json
import re
from pathlib import Path


def snapshot_digest(snap):
    text = json.dumps(snap, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def changes_snapshot(folder, project):
    path = Path(folder) / "stub-snapshot.json"
    if not path.is_file():
        raise RuntimeError("대역: stub-snapshot.json 없음(명세 승인판 없음)")
    return json.loads(path.read_text(encoding="utf-8"))


def g1_confirmed(folder):
    scope = Path(folder) / "refactor-scope.md"
    text = re.split(r"(?m)^#+\s*앞 실행", scope.read_text(encoding="utf-8") if scope.is_file() else "")[0]
    found = re.findall(r"G1 변경판 확정\s+(\S+)\s*·\s*digest\s+([0-9a-f]{12})\s*·\s*후보\s+([0-9a-f]{12})", text)
    return tuple(found[-1]) if found else None


def load_candidate(folder, candidate_digest):
    snap = changes_snapshot(folder, None)
    if snapshot_digest(snap) != candidate_digest:
        raise RuntimeError("대역: 후보 없음")
    return snap
'''

STUB_SUPPORT: str = r'''"""behavior_support 대역(behavior_guard 픽스처 · k0 §4-5 서명 · --stub-support)."""
import hashlib
import json
from pathlib import Path

import behavior_guard as bg


def fingerprint(repo):
    repo = Path(repo)
    head = bg._git(repo, "rev-parse", "--verify", "-q", "HEAD^{commit}", check=False).strip() or "unborn"
    h = hashlib.sha256(head.encode("utf-8") + b"\0")
    for rel in bg._dirty(repo):
        p = repo / rel
        sha = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "없음"
        h.update(rel.encode("utf-8", "surrogateescape") + b"\0" + sha.encode("utf-8") + b"\0")
    return h.hexdigest()[:12]


def latest_suite_record(folder):
    run_dir = bg._run_dir(Path(folder))
    files = sorted(run_dir.glob("suite-*.json")) if run_dir.is_dir() else []
    return json.loads(files[-1].read_text(encoding="utf-8")) if files else None


def cmd_support(folder, repo):
    print("요약: 대역 support")
    return 0


def cmd_suite(folder, repo):
    print("요약: 대역 suite")
    return 0
'''

# 대역 폴더(사례 전체가 나눠 쓴다) · 이 프로세스에 적재한 behavior_guard(분류 · 불변식) · behavior_support(suite 기록 지문)
STATE: "dict[str, object]" = {}
WRAP: str = ("import runpy, sys; stub, scripts = sys.argv[1], sys.argv[2]; sys.argv = sys.argv[3:]; "
             "sys.path[:0] = [stub, scripts]; runpy.run_path(sys.argv[0], run_name='__main__')")


def _setup_refactor(stub_dir: Path, stub_support: bool) -> None:
    (stub_dir / "refactor_audit.py").write_text(STUB_AUDIT, encoding="utf-8")
    if stub_support:
        (stub_dir / "behavior_support.py").write_text(STUB_SUPPORT, encoding="utf-8")
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(stub_dir), str(GUARD.parent)]
    import behavior_guard  # noqa: PLC0415 — 대역 폴더 · 스크립트 폴더를 경로에 둔 뒤
    import behavior_support  # noqa: PLC0415
    STATE.update({"stub": stub_dir, "bg": behavior_guard, "bs": behavior_support, "suite_seq": 0, "totals": [0, 0, 0, 0],
                  "invariant_fails": []})


def _rguard(repo: Path, *args: str, folder: str = RFOLDER) -> "tuple[int, str]":
    proc = subprocess.run([sys.executable, "-c", WRAP, str(STATE["stub"]), str(GUARD.parent), str(GUARD), args[0], folder,
                           *args[1:]], cwd=repo, capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    out: str = proc.stdout + proc.stderr
    if args[0] == "close" and folder == RFOLDER and proc.returncode in (0, 2):   # 판정한 close 마다 자동 초록 0 을 따로 센다
        problem, (files, keyed, reds) = _invariant(repo)
        totals: "list[int]" = STATE["totals"]  # type: ignore[assignment]
        totals[:] = [totals[0] + 1, totals[1] + files, totals[2] + keyed, totals[3] + reds]
        if problem:
            STATE["invariant_fails"].append(f"{problem}\n{out}")  # type: ignore[attr-defined]
    return proc.returncode, out


def _rrepo(td: Path, files: "dict[str, str | None]") -> Path:
    repo: Path = td / "r"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    _write(repo, {k: v for k, v in {**RB, **files}.items() if v is not None})
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    folder: Path = repo / RFOLDER
    folder.mkdir(parents=True)
    (folder / "refactor-scope.md").write_text(RSCOPE, encoding="utf-8")
    (folder / "build_anchor").write_text(_git(repo, "rev-parse", "HEAD"), encoding="utf-8")
    plan: Path = folder / "audit" / AUDIT_STAMP / "plan.md"
    plan.parent.mkdir(parents=True)
    plan.write_text("# refactor_audit plan\n\n- BC: `core`\n", encoding="utf-8")
    return repo


def _k0_digest(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                          .encode("utf-8")).hexdigest()[:12]


def _v(vid: str, case: "str | None" = None, expect_old: "tuple[str, ...] | list[str]" = (), expect_add: int = 0,
       verb: str = "update", ops: "tuple[tuple[str, str], ...]" = ()) -> dict:
    tests = [{"row": f"| {case} | {verb} |", "verb": verb, "owner": "coder", "case": case, "expect_old": list(expect_old),
              "expect_add": expect_add}] if case else []
    return {"id": vid, "kinds": ["내부 약속"] if case else ["DB 구조"], "basis": "M1 #1", "slice": "S1", "before_after": "전 → 후",
            "tests": tests, "ops": [{"app": app, "call": call, "op": call.split("(")[0].rsplit(".", 1)[-1], "key": ""}
                                    for app, call in ops], "data": None, "impact": None}


def _row(case: str) -> str:
    return f"| {case} | update | coder | M1 ⓐ 단언 형태 |"


def _snap(*vs: dict, retain: "tuple[str, ...]" = (), other: "tuple[tuple[str, str, str], ...]" = (),
          update: "tuple[tuple[str, str | None], ...]" = (), remove: "tuple[tuple[str, str | None], ...]" = ()) -> dict:
    """G1 스냅숏 대역(k0 §4-4 판형) — `update` · `remove` = 입장 표 update · remove 행 (경로::케이스, 딸린 V | None)."""
    return {"version": 1, "V": list(vs), "other_bc_edits": [{"path": p, "kind": k, "ref": r} for p, k, r in other],
            "linked_rows": [], "retain_rows": [{"path": p, "case": None, "why": "기대 의미 그대로"} for p in retain],
            "update_rows": [{"case": c, "owner": "coder", "row": _row(c), "v": v} for c, v in update],
            "remove_rows": [{"case": c, "owner": "coder", "row": f"| {c} | remove | coder | M1 ⓐ |", "v": v} for c, v in remove],
            "run_definition_digest": RUN_DEF, "support_record": "20261004T020000Z"}


def _stage(repo: Path, snap: dict) -> str:
    """명세 승인판만 바꾼다(G1 변경판 확정 줄은 쓰지 않는다)."""
    (repo / RFOLDER / "stub-snapshot.json").write_text(json.dumps(snap, ensure_ascii=False), encoding="utf-8")
    return _k0_digest(snap)


def _bind(repo: Path, snap: dict, stamp: str = "2026-10-04T03:10Z") -> str:
    """명세 승인판 + `G1 변경판 확정` 줄(이번 실행 몫)."""
    digest: str = _stage(repo, snap)
    with (repo / RFOLDER / "refactor-scope.md").open("a", encoding="utf-8") as f:
        f.write(f"\n## G1 변경 결정 {stamp} · 후보 digest {digest}\n\nG1 변경판 확정 {stamp} · digest {digest} · 후보 {digest}\n")
    return digest


def _run_dir(repo: Path) -> Path:
    return repo / RFOLDER / "behavior" / RUN


def _last_close(repo: Path) -> dict:
    files = sorted(_run_dir(repo).glob("w*-close.json"), key=lambda p: int(p.name[1:].split("-")[0]))
    return json.loads(files[-1].read_text(encoding="utf-8"))[-1] if files else {}


def _audit(repo: Path, n: int, rows: "list[str]", round_no: int = 1) -> None:
    (repo / RFOLDER / f"audit-tests-w{n}-{round_no}.md").write_text(
        f"# 감사 기록 w{n} · {round_no}회차\n\n" + "\n".join(rows) + "\n", encoding="utf-8")


def _rows(record: dict, verdict: "str | None" = None) -> "list[str]":
    """감사 기록 행 — 키마다 close 가 남긴 요구 판정의 첫 값(verdict 를 주면 모든 키에 그 값)."""
    out: "list[str]" = []
    for d in record.get("dispositions", []):
        wanted: "list[str]" = d.get("요구 판정") or ["기대 의미 그대로"] * len(d["keys"])
        out += [f"{k} | 판정 = {verdict or w.split(' · ')[0]} | 픽스처" for k, w in zip(d["keys"], wanted)]
    return out


GOOD_COUNTS: "dict[str, int]" = {
    "commands": 1, "collected": 3, "selected": 3, "calls": 3, "skips": 0, "complete": 3, "proof_ok": 3, "proof_total": 3,
    "reentry": 0, "anchor": 0, "suspend": 0, "observer_files": 2, "observer_hits": 0, "nolist": 0, "unresolved": 0, "late": 0,
    "hooks": 0, "M": 2, "failed": 0, "optimize": 0}


def _suite(repo: Path, digest: str, **over: object) -> None:
    fp: str = STATE["bs"].fingerprint(repo)  # type: ignore[attr-defined]
    STATE["suite_seq"] = int(STATE["suite_seq"]) + 1  # type: ignore[call-overload]
    record: dict = {
        "version": 1, "run": RUN, "started": "2026-10-04T04:00:00Z", "ended": "2026-10-04T04:00:09Z",
        "support_record": "20261004T020000Z", "run_definition_digest": RUN_DEF,
        "g1": {"at": "2026-10-04T03:10Z", "digest": digest, "candidate": digest, "run_definition_digest": RUN_DEF,
               "support_record": "20261004T020000Z"},
        "fingerprints": {"start": fp, "between": [fp], "end": fp},
        "commands": [{"argv": ["pytest", "-q"], "exit": 0, "probe_exit": 0, "outputs": 1, "workers_ready": 0,
                      "worker_outputs": 0, "seconds": 0.5}],
        "counts": dict(GOOD_COUNTS),
        "g0_keep": [], "reasons": [], "verdict": "green"}
    record.update(over)
    _run_dir(repo).mkdir(parents=True, exist_ok=True)
    (_run_dir(repo) / f"suite-20261004T0400{int(STATE['suite_seq']):02d}Z.json").write_text(  # type: ignore[call-overload]
        json.dumps(record, ensure_ascii=False), encoding="utf-8")


def _invariant(repo: Path) -> "tuple[str | None, tuple[int, int, int]]":
    """«바이트가 바뀐 시험 쪽 파일 수 = 감사 키 낸 파일 + red 파일»(자동 초록 0) — 마지막 창의 기준선(open 기록의 head · dirty0)에
    대어 git 으로 따로 센 바뀐 경로 가운데 시험 쪽인 것(이동이면 전 · 후 어느 쪽이든 — 시험 쪽 경로마다)을 마지막 close 의 처분이
    빠짐없이 덮는가(시험 → 시험 이동은 옛 · 새 경로 한 처분) · 처분마다 키 xor red 인가."""
    bg = STATE["bg"]
    opens = sorted(_run_dir(repo).glob("w*-open.json"), key=lambda p: int(p.name[1:].split("-")[0]))
    opened: dict = json.loads(opens[-1].read_text(encoding="utf-8"))
    record: dict = _last_close(repo)
    head, dirty0 = opened["head"], opened["dirty"]
    lines = lambda *a: [p for p in _git(repo, *a).splitlines() if p and not p.startswith(".dddjango/")]  # noqa: E731
    now_files = lines("ls-files", "-co", "--exclude-standard")
    then_files = sorted((set(lines("ls-tree", "-r", "--name-only", head)) | {p for p, e in dirty0.items() if e["sha"]})
                        - {p for p, e in dirty0.items() if not e["sha"]})

    def sha_then(path: str) -> "str | None":
        if path in dirty0:
            return dirty0[path]["sha"]
        blob = subprocess.run(["git", "-C", str(repo), "show", f"{head}:{path}"], capture_output=True)
        return hashlib.sha256(blob.stdout).hexdigest() if blob.returncode == 0 else None

    def sha_now(path: str) -> "str | None":
        f = repo / path
        return hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else None

    candidates = set(lines("diff", "--no-renames", "--name-only", head)) | set(lines("ls-files", "-o", "--exclude-standard")) \
        | {p for p in dirty0 if not p.startswith(".dddjango/")}
    changed = {p for p in candidates if sha_now(p) != sha_then(p)}
    test_dirs = bg._test_dirs(sorted(now_files)) | bg._test_dirs(then_files)  # type: ignore[attr-defined]
    test_changed = {p for p in changed if bg._is_test_refactor(p, test_dirs)}  # type: ignore[attr-defined]
    disps: "list[dict]" = record.get("dispositions", [])
    keyed = sum(1 for d in disps if d["keys"])
    reds = sum(1 for d in disps if d["처분"] == "red")
    problems: "list[str]" = []
    both = [d["path"] for d in disps if bool(d["keys"]) == (d["처분"] == "red")]
    if both:
        problems.append(f"키 xor red 어긋남(자동 초록 · 키 있는 red) {both}")
    covered = {d["path"] for d in disps} | {d["from"] for d in disps}
    missing = sorted(test_changed - covered)
    if missing:
        problems.append(f"처분 없는 바뀐 시험 쪽 파일 {missing}")
    stray = sorted(covered - changed)
    if stray:
        problems.append(f"바뀌지 않은 경로의 처분 {stray}")
    return ("불변식: " + " · ".join(problems) if problems else None), (len(disps), keyed, reds)


def run_rcase(case: dict) -> "tuple[str | None, tuple[int, int, int]]":
    """리팩토링 모드 처분 사례 — 기준 커밋 → (G1) → open → 편집 → close → 처분 · 키 단위 · 불변식."""
    with tempfile.TemporaryDirectory(prefix="bg-rx-") as td:
        repo: Path = _rrepo(Path(td), case.get("files", {}))
        _bind(repo, case["snap"] if case.get("snap") is not None else _snap())   # 0T · 0C close 도 G1 확정판을 읽는다
        if case.get("before_open"):
            case["before_open"](repo)
        code, out = _rguard(repo, "open", "--kind", case["kind"], "--mode", "refactor")
        if code != 0:
            return f"open exit {code}\n{out}", (0, 0, 0)
        case["edit"](repo)
        if case.get("commit", True):
            _commit(repo)
        code, out = _rguard(repo, "close")
        record: dict = _last_close(repo)
        problems: "list[str]" = []
        expect: "dict[str, tuple]" = case["expect"]
        want: int = case.get("exit", 2 if any(e[0] == "red" for e in expect.values()) else 0)
        if code != want:
            problems.append(f"close exit {code} (기대 {want})")
        problems += [f"출력에 «{n}» 없음" for n in case.get("needles", ()) if n not in out]
        by_path: "dict[str, dict]" = {d["path"]: d for d in record.get("dispositions", [])}
        for path, (disposition, units, *more) in expect.items():
            d = by_path.get(path)
            if d is None:
                problems.append(f"{path} 처분 없음")
                continue
            if d["처분"] != disposition:
                problems.append(f"{path} 처분 {d['처분']} (기대 {disposition}) · 사유 {d['사유']}")
            got_units = sorted(k.split(" · ")[2] for k in d["keys"])
            if units is not None and got_units != sorted(units):
                problems.append(f"{path} 단위 {got_units} (기대 {sorted(units)})")
            fields = {"reason": d["사유"], "no_reason": d["사유"], "rules": d["묶음"], "file_reason": d["file_reason"],
                      "text_only": d["text_only"], "keys": [key.split(" · ", 2)[2] for key in d["keys"]]}
            for k, v in (more[0] if more else {}).items():
                got = fields[k]
                bad = v not in got if k == "reason" else v in got if k == "no_reason" else got != v
                if bad:
                    problems.append(f"{path} {k} {got!r} (기대 {v!r})")
        extra = sorted(set(by_path) - set(expect))
        if extra:
            problems.append(f"기대 밖 처분 {extra}")
        inv, counts = _invariant(repo)
        if inv:
            problems.append(inv)
        if case.get("post"):
            problems += case["post"](repo, record, out)
        return ("\n".join(problems) + f"\n{out}" if problems else None), counts


def _edit(prod: "dict[str, str | None]", test: "str | None" = None, path: str = TP,
          more: "dict[str, str | None] | None" = None) -> "Callable[[Path], None]":
    return lambda r: _write(r, {**prod, **({path: test} if test is not None else {}), **(more or {})})


def _request(repo: Path, n: int = 1) -> str:
    f = _run_dir(repo) / f"w{n}-audit-request.md"
    return f.read_text(encoding="utf-8") if f.is_file() else ""


def _in_request(*needles: str, absent: "tuple[str, ...]" = ()) -> "Callable[[Path, dict, str], list[str]]":
    def check(repo: Path, _record: dict, _out: str) -> "list[str]":
        text = _request(repo)
        return [f"감사 요청에 «{x}» 없음" for x in needles if x not in text] + [f"감사 요청에 «{x}» 있음" for x in absent if x in text]
    return check


def _retain(*paths: str) -> dict:
    return _snap(retain=paths or (TP,))


# r4 반례 · 처분 대조(원형 b0_v5 · 모듈 경로만 application/core 로)
R41: str = ("from application.core.product import Old, product\n\n\ndef should_check(cls):\n    return \"Old\" in repr(cls)\n\n\n"
            "def test_check():\n    subject = Old\n    if should_check(subject):\n        assert product() == 5\n")
R41B: str = ("from application.core.product import Old, product\n\n\ndef test_check():\n    subject = Old\n"
             "    if getattr(subject, \"__name__\") == \"Old\":\n        assert product() == 5\n")
R42: str = ("from application.core.real import product\n\n\ndef helper():\n    from application.core.fake_impl import product\n"
            "    return product\n\n\ndef test_check():\n    assert product() == 5\n")
R42B: str = "from application.core.real import product\n\n\ndef test_check():\n    assert product() == 5\n"
R43: str = "from application.core.product import Old, product\n\n\ndef test_check() -> Old:\n    assert product() == 5\n"
R44: str = ("from unittest.mock import patch\nimport application.core.old as product_module\n\n\ndef test_check():\n"
            "    with patch(\"application.core.old.product\", return_value=5):\n        assert product_module.product() == 5\n")
R44B: str = ("from unittest.mock import patch\nimport application.core.old as product_module\n\n\ndef _patched():\n"
             "    return patch(\"application.core.old.product\", return_value=5)\n\n\ndef test_check():\n    with _patched():\n"
             "        assert product_module.product() == 5\n")
IMPORT_ONLY: str = "from application.core.old import product\n\n\ndef test_check():\n    assert product() == 9\n"
COMMENT: str = "from application.core.real import product\n\n\ndef test_check():\n    # 옛 설명\n    assert product() == 9\n"
ORDER: str = "def a():\n    return 1\n\n\ndef test_check():\n    assert a() == 1\n"
OLD_TO_NEW: "Callable[[str], str]" = lambda s: s.replace("application.core.old", "application.core.new")  # noqa: E731
OLD_RULE: str = "application.core.product.Old → application.core.product.New"
# r5 · 보충(원형 b0_v6)
B6: str = ("from application.core.product import product\n\nregistry = []\n\n\ndef register(fn):\n    registry.append(fn)\n    return fn"
           "\n\n\n@register\ndef a():\n    return product()\n\n\n@register\ndef b():\n    return 9\n\n\n"
           "def test_check():\n    assert registry[0]() == 9\n")
B6_AUDITED: str = "# new\n" + B6
B6_SWAPPED: str = B6_AUDITED.replace("@register\ndef a():\n    return product()\n\n\n@register\ndef b():\n    return 9\n",
                                     "@register\ndef b():\n    return 9\n\n\n@register\ndef a():\n    return product()\n")
B6_V1: str = B6_AUDITED + "\n\n@register\ndef c():\n    return 9\n"
B6_V2: str = B6_AUDITED.replace("@register\ndef a():", "@register\ndef c():\n    return 9\n\n\n@register\ndef a():")
MOD_BASE: str = "X = []\n\n\ndef a():\n    return 1\n\n\ndef test_check():\n    assert a() == 1\n"
MOD_MOVED: str = "\n\ndef a():\n    return 1\nX = []\n\n\ndef test_check():\n    assert a() == 1\n"
# D — v1 반례 8(확정 3 · 공유 5) · M20 꼴
DHEAD: str = "import pytest\nfrom unittest.mock import Mock, call\n\nfrom application.core.product import product\n\n\n"
D_FIXED_CASES: "list[tuple[str, str, str]]" = [
    ("기대값을 제품 호출로", "def test_check():\n    expected = 5\n    assert product() == expected\n",
     "def test_check():\n    expected = product()\n    assert product() == expected\n"),
    ("mock 기대를 call_args 에서", "def test_check():\n    m = Mock()\n    m(1)\n    expected = call(1)\n    m.assert_has_calls([expected])\n",
     "def test_check():\n    m = Mock()\n    m(1)\n    expected = m.call_args\n    m.assert_has_calls([expected])\n"),
    ("단언을 if False 안으로", "def test_check():\n    assert product() == 5\n",
     "def test_check():\n    if False:\n        assert product() == 5\n"),
]
D_SHARED_CASES: "list[tuple[str, str, str]]" = [
    ("모듈 상수", "EXPECTED = 5\n\n\ndef test_check():\n    assert product() == EXPECTED\n",
     "EXPECTED = 9\n\n\ndef test_check():\n    assert product() == EXPECTED\n"),
    ("fixture return", "@pytest.fixture\ndef expected():\n    return 5\n\n\ndef test_check(expected):\n    assert product() == expected\n",
     "@pytest.fixture\ndef expected():\n    return product()\n\n\ndef test_check(expected):\n    assert product() == expected\n"),
    ("parametrize 상수 표", "CASES = [(1, 1)]\n\n\n@pytest.mark.parametrize(\"a,b\", CASES)\ndef test_check(a, b):\n    assert a == b\n",
     "CASES = [(1, 2)]\n\n\n@pytest.mark.parametrize(\"a,b\", CASES)\ndef test_check(a, b):\n    assert a == b\n"),
    ("예외 상수", "ERR = ValueError\n\n\ndef test_check():\n    with pytest.raises(ERR):\n        raise ValueError()\n",
     "ERR = Exception\n\n\ndef test_check():\n    with pytest.raises(ERR):\n        raise ValueError()\n"),
    ("루프 안 재대입", "def test_check():\n    expected = 1\n    for x in [1]:\n        assert x == expected\n        expected = 1\n",
     "def test_check():\n    expected = 1\n    for x in [1]:\n        assert x == expected\n        expected = 2\n"),
]
M20: str = ("def test_rt():\n    expected_by_id = {1: 'a', 2: 'b'}\n    found = {1: 'a', 2: 'b'}\n"
            "    assert set(found) == set(expected_by_id)\n    pricing_candidates = [1]\n"
            "    assert {c for c in pricing_candidates} == set(expected_by_id)\n")
M20_EDIT: str = M20.replace("    pricing_candidates = [1]\n",
                            "    expected_by_id = {k: v for k, v in expected_by_id.items() if k == 1}\n    pricing_candidates = [1]\n")
M20_A100: str = "assert {c for c in pricing_candidates} == set(expected_by_id)"
# DB — 승인 연산 다중집합
MIG: Callable[..., str] = lambda *ops: ("from django.db import migrations, models\n\n\nclass Migration(migrations.Migration):\n"  # noqa: E731
                                        "    dependencies = [(\"core\", \"0001_initial\")]\n    operations = [\n"
                                        + "".join(f"        {op},\n" for op in ops) + "    ]\n")
ADD_F: str = 'migrations.AddField(model_name="wallet", name="active", field=models.BooleanField(default=False))'
ADD_T: str = ADD_F.replace("False", "True")
ADD_G: str = 'migrations.AddField(model_name="wallet", name="limit", field=models.IntegerField(default=0))'
RM_OTHER: str = 'migrations.RemoveField(model_name="ledger", name="note")'
RUN_PY: str = "migrations.RunPython(migrations.RunPython.noop)"
MIG_PATH: str = "application/core/migrations/0002_v.py"
ERRORS: str = "class InsufficientFunds(Exception):\n    pass\n"
RAISE_TEST: str = ("import pytest\n\nfrom application.core.errors import InsufficientFunds\n\n\ndef test_raise():\n"
                   "    with pytest.raises(InsufficientFunds):\n        raise InsufficientFunds()\n")


def rcases() -> "list[dict]":
    """리팩토링 모드 처분 사례(설계 §8 B0 — 처분 · r4 · r5 · 보충 · r3 · r2 · 감사 단위 · 묶음 자료 · D · DB · 대상 BC 밖 · 케이스)."""
    out: "list[dict]" = []

    def add(label: str, kind: str, files: dict, edit: "Callable[[Path], None]", expect: dict, **kw: object) -> None:
        out.append({"label": label, "kind": kind, "files": files, "edit": edit, "expect": expect, **kw})

    # 처분 — r4 반례 넷 · 대응표 없는 대상 교체 · with patch · 헬퍼 안 patch · import 만 · 주석만 · 정의 순서만 · 바이트 그대로 옮김
    add("r4-1 바뀌지 않은 헬퍼의 이름 관찰(개명) → 묶음 감사 · 옛 이름 문자열 자리(바뀌지 않은 conftest 포함)", "code",
        {TP: R41, "application/core/test/conftest.py": 'NAME = "Old"\n'},
        _edit(RENAME, R41.replace("import Old,", "import New,").replace("subject = Old", "subject = New")),
        {TP: ("묶음 감사", ["<module>", "test_check"], {"rules": ["Old → New"]})},
        post=_in_request(f"{TP}:5 «Old»", "application/core/test/conftest.py:1 «Old»", "## 대응표 묶음 B1 — Old → New",
                         OLD_RULE))
    add("r4-1b getattr(…, \"__name__\") 관찰(개명) → 묶음 감사", "code", {TP: R41B},
        _edit(RENAME, R41B.replace("import Old,", "import New,").replace("subject = Old", "subject = New")),
        {TP: ("묶음 감사", ["<module>", "test_check"], {"rules": ["Old → New"]})})
    add("r4-2 전역 import 바인딩(대응표 없음) → 개별 감사(닿은 항목 없음 · 묶음 밖)", "code", {TP: R42},
        _edit({}, R42.replace("from application.core.real import product\n", "from application.core.fake_impl import product\n", 1)),
        {TP: ("개별 감사", ["<module>"], {"reason": "닿은 항목 없음", "rules": []})},
        post=_in_request("## 개별", absent=("## 대응표 묶음",)))
    add("r4-2b 대응표 없는 대상 교체 · code → red", "code", {TP: R42B},
        _edit({}, R42B.replace("application.core.real", "application.core.fake_impl")), {TP: ("red", None)})
    add("r4-2b 대응표 없는 대상 교체 · follow 허용 파일 밖 → red(까닭 «retain 재조직 행에 없는 파일»)", "follow", {TP: R42B},
        _edit({}, R42B.replace("application.core.real", "application.core.fake_impl")),
        {TP: ("red", None, {"reason": "`retain` 재조직 행(0F 허용 파일)에 없는 파일"})}, snap=_snap())
    add("r4-2b 대응표 없는 대상 교체 · code → red(허용 파일 문구 없음)", "code", {TP: R42B},
        _edit({}, R42B.replace("application.core.real", "application.core.fake_impl")),
        {TP: ("red", None, {"no_reason": "재조직 행"})})
    add("r4-2b 대응표 없는 대상 교체 · follow 허용 파일 → 개별 감사", "follow", {TP: R42B},
        _edit({}, R42B.replace("application.core.real", "application.core.fake_impl")), {TP: ("개별 감사", ["<module>"])},
        snap=_retain())
    add("r4-3 반환 주석 개명 → 묶음 감사", "code", {TP: R43},
        _edit(RENAME, R43.replace("Old", "New")), {TP: ("묶음 감사", ["<module>", "test_check"])})
    add("r4-4 with patch 문자열 치환(모듈 이동) → 묶음 감사 · D «맥락만» 사유", "code", {TP: R44},
        _edit(MOVE, OLD_TO_NEW(R44)),
        {TP: ("묶음 감사", ["<module>", "test_check"], {"reason": "D 맥락만 1", "rules": ["old → new"]})})
    add("r4-4b 헬퍼 안 patch 문자열 치환 → 묶음 감사", "code", {TP: R44B},
        _edit(MOVE, OLD_TO_NEW(R44B)), {TP: ("묶음 감사", ["<module>", "_patched"])})
    add("import 만 이동 → 묶음 감사", "code", {TP: IMPORT_ONLY},
        _edit(MOVE, OLD_TO_NEW(IMPORT_ONLY)), {TP: ("묶음 감사", ["<module>"])})
    add("`#` 주석만 → 개별 감사(글 묶음)", "code", {TP: COMMENT},
        _edit({}, COMMENT.replace("옛 설명", "새 설명")), {TP: ("개별 감사", ["test_check"], {"text_only": True})},
        post=_in_request("## 글 묶음"))
    add("정의 순서만 · code → red", "code", {TP: ORDER},
        _edit({}, "def test_check():\n    assert a() == 1\n\n\ndef a():\n    return 1\n"), {TP: ("red", None)})
    add("정의 순서만 · follow 허용 파일 → `<file>` 감사", "follow", {TP: ORDER},
        _edit({}, "def test_check():\n    assert a() == 1\n\n\ndef a():\n    return 1\n"),
        {TP: ("개별 감사", ["<file>"], {"file_reason": "배치 순서 변화"})}, snap=_retain())
    moved_to = "application/core/test/unit/test_check.py"
    add("바이트 그대로 옮긴 시험 파일 → `<file>` 묶음 감사(+ 새 빈 __init__ `<file>`)", "code", {TP: SIMPLE},
        lambda r: _write(r, {TP: None, moved_to: SIMPLE, "application/core/test/unit/__init__.py": ""}),
        {moved_to: ("묶음 감사", ["<file>"], {"file_reason": "바이트 그대로 옮긴 파일"}),
         "application/core/test/unit/__init__.py": ("개별 감사", ["<file>"], {"keys": ["<file> · 전 없음 · 후 e3b0c44298fc"]})},
        post=_in_request("### 단위 `<file>` 전", "### 단위 `<file>` 후", "def test_check():\n    assert product() == 9",
                         "(바이트 차이만 — 줄 diff 없음)"))
    # 이동 전 · 후 어느 쪽이든 시험 쪽이면 처분(T13-C #1)
    prod_src, test_src = "application/core/helpers_src.py", "application/core/test/support/helpers_src.py"
    helper = "def make():\n    return 1\n"
    h12 = hashlib.sha256(helper.encode()).hexdigest()[:12]
    add("이동: 제품 → 시험 자리(code) → 새 시험 쪽 파일 `<file>` 개별 감사(전 없음)", "code", {TP: SIMPLE, prod_src: helper},
        lambda r: _write(r, {prod_src: None, test_src: helper}),
        {test_src: ("개별 감사", ["<file>"], {"keys": [f"<file> · 전 없음 · 후 {h12}"], "reason": "새 파일"})})
    add("이동: 제품 → 시험 자리(0T) → 새 시험 쪽 파일 감사 + 옛 제품 경로 red", "test", {TP: SIMPLE, prod_src: helper},
        lambda r: _write(r, {prod_src: None, test_src: helper}), {test_src: ("개별 감사", ["<file>"])}, exit=2,
        needles=(f"{prod_src} — 제품 쪽 변경(0T 는 제품 코드 고정)",))
    th = "application/core/test/helper_mod.py"
    add("이동: 시험 → 제품 자리(code) → 짝 없는 삭제 `<file>` 개별 감사(후 없음)", "code", {TP: SIMPLE, th: helper},
        lambda r: _write(r, {th: None, "application/core/helper_mod.py": helper}),
        {th: ("개별 감사", ["<file>"], {"keys": [f"<file> · 전 {h12} · 후 없음"], "reason": "짝 없는 삭제"})})
    add("이동: 시험 → 제품 자리(0T) → 짝 없는 삭제 감사 + 새 제품 경로 red", "test", {TP: SIMPLE, th: helper},
        lambda r: _write(r, {th: None, "application/core/helper_mod.py": helper}), {th: ("개별 감사", ["<file>"])}, exit=2,
        needles=("application/core/helper_mod.py — 제품 쪽 변경(0T 는 제품 코드 고정)",))
    # D — 중첩 클래스 메서드(T13-C #4)
    nested = "class TestA:\n    class TestB:\n        def test_m(self):\n            assert 1 + 1 == 2\n"
    add("D 중첩 클래스 메서드의 단언 변경 · follow 허용 파일 → red(③ D 확정)", "follow", {TP: nested},
        _edit({}, nested.replace("== 2", ">= 2")), {TP: ("red", None, {"reason": "D 확정"})}, snap=_retain())
    add("D 중첩 클래스 메서드 · update 행 `경로::바깥::안::메서드` → 0T 개별 감사", "test", {TP: nested},
        _edit({}, nested.replace("== 2", ">= 2")), {TP: ("개별 감사", ["TestA"])},
        snap=_snap(update=((f"{TP}::TestA::TestB::test_m", None),)))
    # 루트 pytest.ini — 0T 예외는 [pytest] 절만(T13-C #5)
    ini = "[pytest]\naddopts = -q\n\n[flake8]\nmax-line-length = 100\n"
    add("0T 루트 pytest.ini 의 [pytest] 절 변경 → 통과(지금 규칙)", "test", {TP: SIMPLE, "pytest.ini": ini},
        _edit({"pytest.ini": ini.replace("-q", "-q -p no:cacheprovider")}), {}, exit=0, needles=("pytest.ini — pytest 설정 절 변경",))
    add("0T 루트 pytest.ini 의 [pytest] 절 밖 변경 → red", "test", {TP: SIMPLE, "pytest.ini": ini},
        _edit({"pytest.ini": ini.replace("100", "120")}), {}, exit=2,
        needles=("pytest.ini — 0T 는 대상 BC(`application/core/`) 밖 편집 없음",))
    # 옛 이름 문자열 자리 — 상한 넘으면 총수 · 생략 수 · 곁 파일 전체(T13-C #8)
    many = "".join(f'N{i} = "Old"\n' for i in range(305))

    def spots_side(repo: Path, _rec: dict, _out: str) -> "list[str]":
        text = _request(repo)
        side = _run_dir(repo) / "w1-audit-spots-B1.txt"
        lines = side.read_text(encoding="utf-8").splitlines() if side.is_file() else []
        return ([] if "총 306곳 · 여기 300곳 · 생략 6곳 — 전체 목록 `w1-audit-spots-B1.txt`" in text else ["총수 · 생략 수 표시 없음"]) \
            + ([] if len(lines) == 306 and "application/core/test/conftest.py:305 «Old»" in lines else [f"곁 파일 {len(lines)}줄"])
    add("옛 이름 문자열 자리 306곳 → 300곳 + 총수 · 생략 수 · 곁 파일 전체", "code",
        {TP: R41, "application/core/test/conftest.py": many},
        _edit(RENAME, R41.replace("import Old,", "import New,").replace("subject = Old", "subject = New")),
        {TP: ("묶음 감사", ["<module>", "test_check"])}, post=spots_side)
    # r5 · 보충
    add("r5 빈 __init__.py 생성 · 삭제 → `<file>` 키 하나(없음 · e3b0c44298fc 구분)", "code",
        {TP: SIMPLE, "application/core/test/helpers/__init__.py": ""},
        lambda r: _write(r, {"application/core/test/helpers/__init__.py": None, "application/core/test/sub/__init__.py": ""}),
        {"application/core/test/sub/__init__.py": ("개별 감사", ["<file>"], {"keys": ["<file> · 전 없음 · 후 e3b0c44298fc"]}),
         "application/core/test/helpers/__init__.py": ("개별 감사", ["<file>"], {"keys": ["<file> · 전 e3b0c44298fc · 후 없음"]})})
    add("r5 빈 __init__.py 생성 · 삭제(작업 트리 · 커밋 없음)", "code",
        {TP: SIMPLE, "application/core/test/helpers/__init__.py": ""},
        lambda r: _write(r, {"application/core/test/helpers/__init__.py": None, "application/core/test/sub/__init__.py": ""}),
        {"application/core/test/sub/__init__.py": ("개별 감사", ["<file>"]),
         "application/core/test/helpers/__init__.py": ("개별 감사", ["<file>"])}, commit=False)
    exp = "application/core/fixtures/expected.json"
    add("r5 fixtures/expected.json 변경 · code → red(시험 쪽 · v6 분류)", "code", {TP: SIMPLE, exp: '{"a": 1}\n'},
        _edit({}, more={exp: '{"a": 2}\n'}), {exp: ("red", None)})
    add("r5 fixtures/expected.json 변경 · follow 허용 파일 → `<file>` 감사", "follow", {TP: SIMPLE, exp: '{"a": 1}\n'},
        _edit({}, more={exp: '{"a": 2}\n'}), {exp: ("개별 감사", ["<file>"], {"file_reason": "비 `.py`"})}, snap=_retain(exp))
    dirty0, edited = '{"a": 2}\n', '{"a": 3}\n'
    key12 = [hashlib.sha256(t.encode("utf-8")).hexdigest()[:12] for t in (dirty0, edited)]
    add("창 기준선 = open 때 미커밋 원문(dirty0) — 키의 «전»은 그 원문", "follow", {TP: SIMPLE, exp: '{"a": 1}\n'},
        _edit({}, more={exp: edited}), {exp: ("개별 감사", ["<file>"], {"keys": [f"<file> · 전 {key12[0]} · 후 {key12[1]}"]})},
        snap=_retain(exp), commit=False, before_open=lambda r: _write(r, {exp: dirty0}))
    add("보충 모듈 문장을 정의 너머로 옮김 → `<file>`", "follow", {TP: MOD_BASE},
        _edit({}, MOD_MOVED), {TP: ("개별 감사", ["<file>"], {"file_reason": "배치 순서 변화"})}, snap=_retain())
    cases_json = "application/core/cases/expected.json"
    add("보충 인정 경로 밖 자료(cases/expected.json)는 제품 쪽(사각 고정 확인)", "code", {TP: SIMPLE, cases_json: "1\n"},
        _edit({}, more={cases_json: "2\n"}), {})
    # r3 반례 넷 · r2 반례 둘 → 감사(초록 아님)
    r31 = ("from application.core.old import product\n\n\ndef _target():\n    return \"application.core.old.product\"\n\n\n"
           "def test_check():\n    assert product() == 9\n    assert _target()\n")
    add("r3 헬퍼 반환 문자열을 이동에 맞춰 바꿈 → 묶음 감사", "code", {TP: r31},
        _edit(MOVE, OLD_TO_NEW(r31)), {TP: ("묶음 감사", ["<module>", "_target"])})
    r32 = "def mark(v):\n    return v\n\n\ndef test_check():\n    class K:\n        x: mark(False) = 1\n    assert K.x == 1\n"
    add("r3 시험 함수 안 중첩 클래스 주석 mark(False)→mark(True) · code → red", "code", {TP: r32},
        _edit({}, r32.replace("mark(False)", "mark(True)")), {TP: ("red", None)})
    add("r3 시험 함수 안 중첩 클래스 주석 mark(False)→mark(True) · follow → 개별 감사", "follow", {TP: r32},
        _edit({}, r32.replace("mark(False)", "mark(True)")), {TP: ("개별 감사", ["test_check"])}, snap=_retain())
    r33 = "def _helper() -> \"int\":\n    return 1\n\n\ndef test_check():\n    assert _helper() == 1\n"
    add("r3 반환 문자열 주석 \"int\" → int → 개별 감사(0C 합격 · 초록 아님)", "code", {TP: r33},
        _edit({}, r33.replace('-> "int"', "-> int")), {TP: ("개별 감사", ["_helper"])})
    r34 = "def test_check():\n    \"\"\"check\"\"\"\n    assert 1 == 1\n"
    add("r3 시험 함수 docstring \"check\" → \"skip\" → 개별 감사(글 묶음)", "code", {TP: r34},
        _edit({}, r34.replace("check\"\"\"", "skip\"\"\"")), {TP: ("개별 감사", ["test_check"], {"text_only": True})})
    r21 = "def _make(v=5):\n    return v\n\n\ndef test_check():\n    assert _make() == 5\n"
    add("r2 기본 인자 제거 · follow → 개별 감사", "follow", {TP: r21},
        _edit({}, "def _make(v):\n    return v\n\n\ndef test_check():\n    assert _make(5) == 5\n"),
        {TP: ("개별 감사", ["_make", "test_check"])}, snap=_retain())
    r22 = ("SEEN = []\n\n\ndef note(x):\n    SEEN.append(x)\n    return x\n\n\ndef _make(v: note(\"a\") = 5):\n    return v\n\n\n"
           "def test_check():\n    assert _make() == 5\n")
    add("r2 매개변수 주석 부작용 · follow → 개별 감사", "follow", {TP: r22},
        _edit({}, r22.replace('note("a")', 'note("b")')), {TP: ("개별 감사", ["_make"])}, snap=_retain())
    # ① 이 ② 보다 먼저 · 혼합 파일 · 비 .py 대응표 치환
    add("0C 합격 + 승인 원소 D(승인된 예외 클래스 개명) · change → 승인 변경 감사", "change",
        {TP: RAISE_TEST, "application/core/errors.py": ERRORS},
        _edit({"application/core/errors.py": ERRORS.replace("InsufficientFunds", "NotEnoughFunds")},
              RAISE_TEST.replace("InsufficientFunds", "NotEnoughFunds")),
        {TP: ("승인 변경 감사", ["<module>", "test_raise"], {"reason": "D 확정 전부 승인 원소"})},
        snap=_snap(_v("V1", f"{TP}::test_raise", ["with pytest.raises(InsufficientFunds):"])),
        post=lambda repo, rec, _o: [] if rec.get("approved_hits") == {
            f"{TP}::test_raise": {"old": ["with pytest.raises(InsufficientFunds):"], "add": 0}} else [
            f"approved_hits {rec.get('approved_hits')}"])
    mixed = ("from unittest.mock import patch\n\nfrom application.core.old import product\n\n\ndef test_check():\n"
             "    with patch(\"application.core.real.product\", return_value=5):\n        assert product() == 9\n")
    add("같은 파일 혼합(대응표 치환 + 맥락 변화 + retain 편집) · follow → red", "follow", {TP: mixed},
        _edit(MOVE, OLD_TO_NEW(mixed).replace("application.core.real.product", "application.core.fake_impl.product")),
        {TP: ("red", None, {"reason": "D 확정"})}, snap=_retain())
    data = "application/core/test/data/paths.txt"
    add("비 .py 시험 데이터 대응표 치환 → 묶음 감사", "code", {TP: SIMPLE, data: "src: application/core/old.py\n"},
        _edit(MOVE, more={data: "src: application/core/new.py\n"}), {data: ("묶음 감사", ["<file>"], {"file_reason": "비 `.py`"})})
    add("비 .py 시험 데이터 그 밖 변경 · code → red", "code", {TP: SIMPLE, data: "src: a\n"},
        _edit({}, more={data: "src: b\n"}), {data: ("red", None)})
    # 감사 단위 — 정의 밖 주석 · 정의 하나 더함 · 이름 충돌
    add("감사 단위: 정의 밖 주석만 → `<module>` 키", "code", {TP: SIMPLE},
        _edit({}, SIMPLE.replace("\n\ndef test_check", "\n# 설명\ndef test_check")), {TP: ("개별 감사", ["<module>"])})
    add("감사 단위: 정의 하나 더함 → 그 정의 키 + `<module>` 키", "follow", {TP: SIMPLE},
        _edit({}, SIMPLE + "\n\ndef _h():\n    return 1\n"), {TP: ("개별 감사", ["<module>", "_h"])}, snap=_retain())
    clash = ("def helper():\n    return 1\n\n\nsaved = helper\n\n\ndef helper():\n    return 2\n\n\n"
             "def test_check():\n    assert saved() == 1\n")
    add("감사 단위: 이름 충돌(helper 두 번 · 앞 것만 바꿈) → `<file>`", "follow", {TP: clash},
        _edit({}, clash.replace("return 1\n\n\nsaved", "return 3\n\n\nsaved")),
        {TP: ("개별 감사", ["<file>"], {"file_reason": "같은 이름 최상위 정의가 둘 이상"})}, snap=_retain())
    # 묶음 자료 — 묶음 규칙 줄이기
    pkg = {"application/core/ai_chat/__init__.py": "", "application/core/ai_chat/a.py": "def fa():\n    return 1\n",
           "application/core/ai_chat/b.py": "def fb():\n    return 2\n", "application/core/ai_chat/c.py": "def fc():\n    return 3\n"}
    chat = ("from application.core.ai_chat.a import fa\nfrom application.core.ai_chat.b import fb\n"
            "from application.core.ai_chat.c import fc\n\n\ndef test_check():\n    assert fa() + fb() + fc() == 6\n")
    add("묶음 자료: 모듈 여럿 이동 → 묶음 규칙 하나(ai_chat → chat_relay)", "code", {TP: chat, **pkg},
        _edit({**{k: None for k in pkg}, **{k.replace("ai_chat", "chat_relay"): v for k, v in pkg.items()}},
              chat.replace("ai_chat", "chat_relay")),
        {TP: ("묶음 감사", ["<module>"], {"rules": ["ai_chat → chat_relay"]})},
        post=_in_request("## 대응표 묶음 B1 — ai_chat → chat_relay"))
    # D — 원문 AST(별칭 개명 → 기대식 · 주석만 → D 없음 + 키)
    alias = "import application.core.price_catalog_adapter as price_catalog_adapter\n\n\ndef test_check():\n    assert 1 == price_catalog_adapter.X\n"
    add("D 원문 AST: 별칭 개명 → «기대식» 사유(0C 합격 · 묶음 감사)", "code",
        {TP: alias, "application/core/price_catalog_adapter.py": "X = 1\n"},
        _edit({"application/core/price_catalog_adapter.py": None, "application/core/product_price_catalog_adapter.py": "X = 1\n"},
              alias.replace("price_catalog_adapter", "product_price_catalog_adapter")),
        {TP: ("묶음 감사", ["<module>", "test_check"], {"reason": "D 기대식 1"})})
    ann = "def test_check():\n    x: int = 1\n    assert x == 1\n"
    add("D 원문 AST: 변수 주석만 바뀜 → D 없음 + 감사 키", "follow", {TP: ann},
        _edit({}, ann.replace("x: int", "x: str")), {TP: ("개별 감사", ["test_check"], {"no_reason": "D "})}, snap=_retain())
    for name, before, after in D_FIXED_CASES:
        add(f"D v1 반례(확정) {name} · follow → red", "follow", {TP: DHEAD + before}, _edit({}, DHEAD + after),
            {TP: ("red", None, {"reason": "D 확정"})}, snap=_retain())
    for name, before, after in D_SHARED_CASES:
        add(f"D v1 반례(공유) {name} · follow 허용 파일 → 개별 감사", "follow", {TP: DHEAD + before}, _edit({}, DHEAD + after),
            {TP: ("개별 감사", None, {"reason": "공유 정의 변화"})}, snap=_retain())
    m20 = "application/core/test/test_round_trip.py"
    add("D M20 꼴 재대입 · change 에서 100행만 승인 → 99행 보존 인정 · 승인 변경 감사", "change", {TP: SIMPLE, m20: M20},
        _edit({}, M20_EDIT, path=m20), {m20: ("승인 변경 감사", ["test_rt"])},
        snap=_snap(_v("V1", f"{m20}::test_rt", [M20_A100])))
    add("D M20 꼴 · 같은 사본에서 99행도 바꾸면 red", "change", {TP: SIMPLE, m20: M20},
        _edit({}, M20_EDIT.replace("assert set(found) == set(expected_by_id)", "assert set(found) >= set(expected_by_id)"),
              path=m20), {m20: ("red", None, {"reason": "«바뀌는 기대» 밖"})},
        snap=_snap(_v("V1", f"{m20}::test_rt", [M20_A100])))
    add("D M20 꼴 재대입 · follow → red", "follow", {TP: SIMPLE, m20: M20},
        _edit({}, M20_EDIT, path=m20), {m20: ("red", None)}, snap=_retain(m20))
    # DB — 승인 연산 다중집합 · 기존 마이그레이션 · 산출 밖 연산
    db = lambda approved: _snap(_v("V1", ops=tuple(("core", op) for op in approved)))  # noqa: E731
    add("DB: AddField default=False 승인에 default=True 생성 → red", "change", {TP: SIMPLE},
        _edit({MIG_PATH: MIG(ADD_T)}), {}, snap=db([ADD_F]), exit=2, needles=("승인 밖 연산",))
    add("DB: 같은 앱 다른 모델 RemoveField 끼움 → red", "change", {TP: SIMPLE},
        _edit({MIG_PATH: MIG(ADD_F, RM_OTHER)}), {}, snap=db([ADD_F]), exit=2, needles=("승인 밖 연산 ×1",))
    add("DB: 같은 연산 두 번(중복 수 다름) → red", "change", {TP: SIMPLE},
        _edit({MIG_PATH: MIG(ADD_F, ADD_F)}), {}, snap=db([ADD_F]), exit=2, needles=("승인 밖 연산 ×1",))
    add("DB: 순서만 다름 → green", "change", {TP: SIMPLE},
        _edit({MIG_PATH: MIG(ADD_G, ADD_F)}), {}, snap=db([ADD_F, ADD_G]), exit=0,
        post=lambda repo, rec, _o: [] if len(rec.get("ops", [])) == 2 and rec.get("verdict") == "green" else [f"ops {rec.get('ops')}"])
    add("DB: 기존 마이그레이션 수정 → red", "change", {TP: SIMPLE},
        _edit({"application/core/migrations/0001_initial.py": RB["application/core/migrations/0001_initial.py"] + "# x\n"}),
        {}, snap=db([]), exit=2, needles=("기존 마이그레이션 수정",))
    add("DB: RunPython → red(makemigrations 산출 밖)", "change", {TP: SIMPLE},
        _edit({MIG_PATH: MIG(RUN_PY)}), {}, snap=db([]), exit=2, needles=("산출 밖 연산 RunPython",))
    add("DB: 0C 창 새 마이그레이션 → red(지금 규칙)", "code", {TP: SIMPLE},
        _edit({MIG_PATH: MIG(ADD_F)}), {}, exit=2, needles=("마이그레이션 추가",))
    # 대상 BC 밖 경로 ⊆ 다른 BC 편집 목록(창 종류가 허락한 갈래만)
    billing = {"application/billing/api.py": "def charge():\n    return 2\n"}
    add("대상 BC 밖: change · 목록 안 경로 → 통과", "change", {TP: SIMPLE}, _edit(billing), {}, exit=0,
        snap=_snap(_v("V1"), other=(("application/billing/api.py", "받는 쪽 어댑터", "V1"),)))
    add("대상 BC 밖: change · 목록 밖 경로 → red", "change", {TP: SIMPLE},
        _edit({**billing, "application/billing/other.py": "X = 1\n"}), {}, exit=2, needles=("application/billing/other.py — 대상 BC",),
        snap=_snap(_v("V1"), other=(("application/billing/api.py", "받는 쪽 어댑터", "V1"),)))
    add("대상 BC 밖: follow · 프로젝트 합성 목록 안 → 통과", "follow", {TP: SIMPLE, "config/settings.py": "A = 1\n"},
        _edit({"config/settings.py": "A = 2\n"}), {}, exit=0, snap=_snap(other=(("config/settings.py", "프로젝트 합성", "0F"),)))
    add("대상 BC 밖: follow · 받는 쪽 어댑터 갈래는 허락 밖 → red", "follow", {TP: SIMPLE}, _edit(billing), {}, exit=2,
        needles=("application/billing/api.py — 대상 BC",),
        snap=_snap(other=(("application/billing/api.py", "받는 쪽 어댑터", "0F"),)))
    bill_test = "application/billing/test/test_bill.py"
    bill_src = "from application.billing.api import charge\n\n\ndef test_bill():\n    assert charge() == 1\n"
    add("대상 BC 밖: 0T · 다른 BC 시험 파일 편집 → red(파일은 개별 감사 키)", "test", {TP: SIMPLE, bill_test: bill_src},
        _edit({}, bill_src.replace("    assert", "    # 설명\n    assert"), path=bill_test),
        {bill_test: ("개별 감사", ["test_bill"])}, exit=2,
        needles=(f"{bill_test} — 0T 는 대상 BC(`application/core/`) 밖 편집 없음(루트 pytest 설정 절만)",),
        post=lambda repo, rec, _o: [] if rec.get("outside_bc") == [bill_test] else [f"outside_bc {rec.get('outside_bc')}"])
    add("대상 BC 밖: 0T · 루트 pytest 설정 절 변경 → 통과(감사 키 없음 — 지금 규칙)", "test", {TP: SIMPLE},
        _edit({"pyproject.toml": RB["pyproject.toml"] + 'addopts = "-p no:cacheprovider"\n'}), {}, exit=0,
        needles=("pytest 설정 절 변경(0T 허용", "시험 쪽 무변"),
        post=lambda repo, rec, _o: [] if rec.get("outside_bc") == [] and rec.get("keys") == [] else [f"기록 {rec.get('outside_bc')}"])
    add("대상 BC 밖: 0T · 루트 설정 파일의 pytest 절 밖 변경 → red", "test", {TP: SIMPLE},
        _edit({"pyproject.toml": RB["pyproject.toml"].replace('name = "x"', 'name = "y"')}), {}, exit=2,
        needles=("pyproject.toml — 0T 는 대상 BC(`application/core/`) 밖 편집 없음",))
    shared = "application/shared/contracts.py"
    add("대상 BC 밖: 0C · 목록 안 공유 표면 치환(제품 파일) → 통과", "code", {TP: SIMPLE, shared: "NAME = 'old'\n"},
        _edit({shared: "NAME = 'new'\n"}), {}, exit=0, snap=_snap(other=((shared, "공유 표면", "0C"),)),
        post=lambda repo, rec, _o: [] if rec.get("outside_bc") == [] else [f"outside_bc {rec.get('outside_bc')}"])
    add("대상 BC 밖: 0C · 목록 밖 다른 BC 파일 → red", "code", {TP: SIMPLE, shared: "NAME = 'old'\n"},
        _edit({**billing, shared: "NAME = 'new'\n"}), {}, exit=2, snap=_snap(other=((shared, "공유 표면", "0C"),)),
        needles=("application/billing/api.py — 대상 BC(`application/core/`) 밖 경로가 다른 BC 편집 목록 밖(창 0C 허용 갈래: "
                 "공유 표면 · 프로젝트 합성)",),
        post=lambda repo, rec, _o: [] if rec.get("outside_bc") == ["application/billing/api.py"] else [
            f"outside_bc {rec.get('outside_bc')}"])
    add("대상 BC 밖: 0C · 갈래가 허락 밖(받는 쪽 어댑터 줄)인 경로 → red", "code", {TP: SIMPLE}, _edit(billing), {}, exit=2,
        needles=("application/billing/api.py — 대상 BC",),
        snap=_snap(other=(("application/billing/api.py", "받는 쪽 어댑터", "0C"),)))
    add("대상 BC 밖: 0C · 다른 BC 시험 파일의 대응표 치환도 목록 밖이면 red(파일은 묶음 감사 키)", "code",
        {TP: SIMPLE, bill_test: IMPORT_ONLY.replace("test_check", "test_bill")},
        _edit(MOVE, OLD_TO_NEW(IMPORT_ONLY.replace("test_check", "test_bill")), path=bill_test),
        {bill_test: ("묶음 감사", ["<module>"])}, exit=2, needles=(f"{bill_test} — 대상 BC",))
    # 케이스 증감 — change 는 add/remove 행 그대로
    add("케이스: change · 승인 add 행의 새 케이스 → 승인 변경 감사", "change", {TP: SIMPLE},
        _edit({}, SIMPLE + "\n\ndef test_new():\n    assert 1 == 1\n"), {TP: ("승인 변경 감사", ["<module>", "test_new"])},
        snap=_snap(_v("V1", f"{TP}::test_new", (), 1, verb="add")))
    add("케이스: change · add 행 밖 새 케이스 → red", "change", {TP: SIMPLE},
        _edit({}, SIMPLE + "\n\ndef test_new():\n    assert 1 == 1\n"), {TP: ("red", None)}, snap=_snap(),
        needles=("승인판 add 행 밖",))
    two = SIMPLE + "\n\ndef test_old():\n    assert 2 == 2\n"
    add("케이스: change · 승인 remove 행 → 승인 변경 감사 · G0 유지 예외(rel::cls::func)", "change", {TP: two},
        _edit({}, SIMPLE), {TP: ("승인 변경 감사", ["<module>", "test_old"])},
        snap=_snap(_v("V1", f"{TP}::test_old", ["assert 2 == 2"], verb="remove")),
        post=lambda repo, rec, _o: [] if rec["g0_keep_exceptions"]["removed"] == [f"{TP}::::test_old"] else [
            f"g0_keep_exceptions {rec['g0_keep_exceptions']}"])
    add("승인 변경 미검출: 승인 케이스 파일인데 확정 변화 없음 → 개별 감사 + 보고", "change", {TP: SIMPLE},
        _edit({}, SIMPLE.replace("    assert", "    # 설명\n    assert")),
        {TP: ("개별 감사", ["test_check"], {"reason": "승인 변경 미검출"})},
        snap=_snap(_v("V1", f"{TP}::test_check", ["assert product() == 9"])), needles=("보고:", "승인 변경 미검출"))
    # 0T(리팩토링 모드) — 제품 고정 · 시험 쪽은 바뀐 단위마다 감사 키 · D 확정은 red(입장 표 remove 행의 케이스 삭제만 감사)
    add("0T 시험 쪽 주석 편집 → 개별 감사", "test", {TP: SIMPLE},
        _edit({}, SIMPLE.replace("    assert", "    # 설명\n    assert")), {TP: ("개별 감사", ["test_check"], {"reason": "0T"})})
    add("0T D 확정(단언 값 변경) → red", "test", {TP: SIMPLE},
        _edit({}, SIMPLE.replace("== 9", "== 8")), {TP: ("red", None, {"reason": "D 확정"})})
    add("0T 제품 쪽 변경 → red", "test", {TP: SIMPLE}, _edit(RENAME), {}, exit=2, needles=("제품 쪽 변경(0T 는 제품 코드 고정)",))
    add("0T 비 .py 시험 자료 변경 → 개별 감사", "test", {TP: SIMPLE, data: "src: a\n"},
        _edit({}, more={data: "src: b\n"}), {data: ("개별 감사", ["<file>"], {"reason": "0T 시험 자료 변경"})})
    spec_remove = lambda r: (r / RFOLDER / "design-spec.md").write_text(  # noqa: E731
        f"| decision | owner/path |\n|---|---|\n| remove | `{TP}::test_old` |\n", encoding="utf-8")
    rm_old = _snap(remove=((f"{TP}::test_old", None),))
    add("0T 케이스 삭제(G1 확정판 remove_rows) → 개별 감사 · G0 유지 예외", "test", {TP: two}, _edit({}, SIMPLE),
        {TP: ("개별 감사", ["<module>", "test_old"], {"reason": "입장 표 remove 행 케이스 삭제"})}, snap=rm_old,
        post=lambda repo, rec, _o: [] if rec["g0_keep_exceptions"]["removed"] == [f"{TP}::::test_old"] else [
            f"g0_keep_exceptions {rec['g0_keep_exceptions']}"])
    add("0T 케이스 삭제(remove 행 없음) → red", "test", {TP: two}, _edit({}, SIMPLE), {TP: ("red", None)},
        needles=("테스트 케이스 감소",))
    add("0T 케이스 삭제 · remove 행이 design-spec.md 에만(G1 확정판 밖) → red", "test", {TP: two},
        lambda r: (_write(r, {TP: SIMPLE}), spec_remove(r)), {TP: ("red", None)},
        needles=("테스트 케이스 감소", "G1 확정판 입장 표 remove 행 밖"))
    add("0T 케이스 삭제 · V 에 딸린 remove 행 → red", "test", {TP: two}, _edit({}, SIMPLE), {TP: ("red", None)},
        snap=_snap(remove=((f"{TP}::test_old", "V1"),)), needles=("테스트 케이스 감소",))
    add("0T remove 행 케이스의 단언만 지움(케이스는 남음) → red", "test", {TP: two},
        _edit({}, two.replace("    assert 2 == 2\n", "    pass\n")), {TP: ("red", None, {"reason": "D 확정"})}, snap=rm_old)
    factory = "application/core/test/factories/money_factory.py"
    uses = "from application.core.test.factories.money_factory import money\n\n\ndef test_check():\n    assert money() == 1\n"
    add("0T 시험 파일 이동(factories → fake) + import 수정 → `<file>` 묶음 감사 + 개별 감사", "test",
        {TP: uses, factory: "def money():\n    return 1\n", "application/core/test/factories/__init__.py": ""},
        lambda r: _write(r, {factory: None, factory.replace("factories", "fake"): "def money():\n    return 1\n",
                             "application/core/test/fake/__init__.py": "", TP: uses.replace("factories", "fake")}),
        {factory.replace("factories", "fake"): ("묶음 감사", ["<file>"]),
         "application/core/test/fake/__init__.py": ("개별 감사", ["<file>"]), TP: ("개별 감사", ["<module>"])})
    # 0T 의 D 확정 — V 에 딸리지 않은 입장 표 update 행의 케이스(글자 그대로 일치)만 개별 감사 · 바뀐 단위 전부 키(k0 §4-4)
    upd = ("def helper():\n    return 9\n\n\ndef test_check():\n    assert helper() == 9\n\n\n"
           "def test_check_extra():\n    assert helper() > 0\n")
    upd_row = upd.replace("assert helper() == 9", "assert helper() >= 9")
    upd_all = "# 정리\n" + upd_row.replace("    return 9\n", "    # 값\n    return 9\n")

    def all_units(path: str, before: str, after: str, rows: "list[str]") -> "Callable[[Path, dict, str], list[str]]":
        """«update 행 파일에서 바뀐 단위 일부만 키로 올라가는 꼴이 없다» — 따로 잰 바뀐 단위 = 키 · 행 원문이 기록 · 감사 요청에."""
        def check(repo: Path, rec: dict, _out: str) -> "list[str]":
            d = next(x for x in rec["dispositions"] if x["path"] == path)
            want = sorted(u for u, _b, _a in STATE["bg"].audit_keys(before.encode(), after.encode(), True)[0])  # type: ignore[attr-defined]
            got = sorted(k.split(" · ")[2] for k in d["keys"])
            text = _request(repo)
            line = "요구 판정: 승인 후와 같음 · 기대 의미 그대로(0T update 행이 승인한 범위 안이면 승인 후와 같음) — 0T update 행 — "
            return ([f"바뀐 단위 {want} ≠ 키 {got}"] if want != got or not want else []) \
                + ([f"update_rows {d['update_rows']}"] if d["update_rows"] != rows else []) \
                + ([f"요구 판정 {d['요구 판정']}"] if d["요구 판정"] != ["승인 후와 같음 · 기대 의미 그대로"] * len(d["keys"]) else []) \
                + [f"감사 요청 키 줄의 요구 판정에 «0T update 행 — {row}» 없음" for row in rows
                   if text.count(line + row) != len(d["keys"])]
        return check

    case_fn = f"{TP}::test_check"
    add("0T update 행(모듈 함수 케이스) D 확정 → 개별 감사 · 바뀐 단위 전부 키", "test", {TP: upd}, _edit({}, upd_all),
        {TP: ("개별 감사", ["<module>", "helper", "test_check"], {"reason": f"0T update 행 — {_row(case_fn)}"})},
        snap=_snap(update=((case_fn, None),)), post=all_units(TP, upd, upd_all, [_row(case_fn)]))
    upd_cls = ("class TestBox:\n    def test_m(self):\n        assert 1 + 1 == 2\n\n    def test_n(self):\n        assert True\n\n\n"
               "def note():\n    return 1\n")
    upd_cls_new = upd_cls.replace("== 2", ">= 2").replace("    return 1\n", "    # 값\n    return 1\n")
    case_m = f"{TP}::TestBox::test_m"
    add("0T update 행(클래스 메서드 케이스 `경로::클래스::메서드`) D 확정 → 개별 감사 · 바뀐 단위 전부 키", "test", {TP: upd_cls},
        _edit({}, upd_cls_new), {TP: ("개별 감사", ["TestBox", "note"], {"reason": f"0T update 행 — {_row(case_m)}"})},
        snap=_snap(update=((case_m, None),)), post=all_units(TP, upd_cls, upd_cls_new, [_row(case_m)]))
    add("0T update 행과 이름이 비슷한 다른 케이스(접두)의 D 확정 → red", "test", {TP: upd},
        _edit({}, upd.replace("assert helper() > 0", "assert helper() > 1")),
        {TP: ("red", None, {"reason": f"`{TP}::test_check_extra`"})}, snap=_snap(update=((case_fn, None),)))
    add("0T 한 파일에 update 행 케이스의 D 확정 + 행 밖 케이스의 D 확정 → red(파일 통째 · 키 0)", "test", {TP: upd},
        _edit({}, upd_row.replace("assert helper() > 0", "assert helper() > 1")),
        {TP: ("red", [], {"reason": f"밖: `{TP}::test_check_extra`"})}, snap=_snap(update=((case_fn, None),)))
    add("0T V 에 딸린 update 행 케이스의 D 확정 → red(변경 슬라이스 몫)", "test", {TP: upd}, _edit({}, upd_row),
        {TP: ("red", None, {"reason": f"`{TP}::test_check`"})},
        snap=_snap(_v("V1", case_fn, ["assert helper() == 9"]), update=((case_fn, "V1"),)))
    add("0T update 행 케이스 + remove 행 케이스 통째 삭제가 한 파일에 → 개별 감사", "test", {TP: upd},
        _edit({}, upd_row.split("\n\n\ndef test_check_extra")[0] + "\n"),
        {TP: ("개별 감사", ["<module>", "test_check", "test_check_extra"], {"reason": "입장 표 remove 행 케이스 삭제"})},
        snap=_snap(update=((case_fn, None),), remove=((f"{TP}::test_check_extra", None),)))
    # follow · change 의 ② · ④ · 설정 · 케이스 · 수집 밖 · 파싱 불가
    add("follow: 구조 이동을 따라간 import → 묶음 감사(0C 검사 합격)", "follow", {TP: IMPORT_ONLY},
        _edit(MOVE, OLD_TO_NEW(IMPORT_ONLY)), {TP: ("묶음 감사", ["<module>"], {"rules": ["old → new"]})}, snap=_snap())
    add("change: 승인 케이스 파일의 0C 불합격 · D 없는 편집 → 개별 감사(허용 파일)", "change", {TP: SIMPLE},
        _edit({}, SIMPLE + "\n\ndef _h():\n    return 1\n"), {TP: ("개별 감사", ["<module>", "_h"], {"reason": "허용 파일"})},
        snap=_snap(_v("V1", f"{TP}::test_check", ["assert product() == 9"])))
    other = "application/core/test/test_other.py"
    other_src = "def test_o():\n    x = 1\n    assert x\n"
    add("change: 허용 밖 파일의 0C 불합격 편집 → red", "change", {TP: SIMPLE, other: other_src},
        _edit({}, other_src + "\n\ndef _h():\n    return 1\n", path=other),
        {other: ("red", None, {"reason": "0C 검사 불합격 · " + "application/core/test/test_other.py — 치환으로 설명되지 않는 변경"})},
        needles=("승인 케이스 파일이 아니고 `retain` 재조직 행(0F 허용 파일)에 없는 파일",),
        snap=_snap(_v("V1", f"{TP}::test_check", ["assert product() == 9"])))
    add("pytest 설정 변경 · code → red", "code", {TP: SIMPLE},
        _edit({"pyproject.toml": RB["pyproject.toml"].replace('["application"]', '["application/core"]')}), {}, exit=2,
        needles=("pytest 설정 변경",))
    add("케이스 이름 변화 · code → red", "code", {TP: SIMPLE},
        _edit({}, SIMPLE.replace("test_check", "test_check2")), {TP: ("red", None)}, needles=("수집 테스트 케이스 변화",))
    outside_name = "application/core/test/check_cases.py"
    add("시험 파일을 수집 밖 이름으로 이동 · code → red(파일은 `<file>` 키)", "code", {TP: SIMPLE},
        lambda r: _write(r, {TP: None, outside_name: SIMPLE}), {outside_name: ("묶음 감사", ["<file>"])}, exit=2,
        needles=("수집 밖으로",))
    add("파싱 불가 · code → red", "code", {TP: SIMPLE}, _edit({}, "def test_check(:\n"), {TP: ("red", None)})
    add("파싱 불가 · follow 허용 파일 → `<file>` 감사(D 계산 불가 · 케이스 규칙은 red)", "follow", {TP: SIMPLE},
        _edit({}, "def test_check(:\n"), {TP: ("개별 감사", ["<file>"], {"file_reason": "파싱 불가", "reason": "D 계산 불가"})},
        snap=_retain(), exit=2, needles=("수집 테스트 케이스 변화",))
    return out


def d_checks() -> "list[str]":
    """D 함수 수준(설계 §4-2) — 같은 이름 정의의 발생 순번 짝 · 승인 원소 대조용 옛 문장 원문 · 파싱 못 하면 None."""
    bg = STATE["bg"]
    fails: "list[str]" = []
    dup = "def helper():\n    assert f() == 1\n\n\ndef helper():\n    assert f() == 2\n"
    got = [(c.func, c.state, sorted(bg.element_texts(dup, c.old))) for c in bg.d_changes(dup, dup.replace("== 1", "== 5"))]  # type: ignore[attr-defined]
    if got != [("helper", "확정 변화", ["assert f() == 1"])]:
        fails.append(f"발생 순번 짝(앞 정의만 바꿈): {got}")
    src = ("import pytest\n\n\n@pytest.mark.parametrize('a', [1, 2])\ndef test_a(a, m):\n    with pytest.raises(ValueError):\n"
           "        f(a)\n    try:\n        g()\n    except KeyError as exc:\n        pass\n    m.assert_called_once_with(a)\n"
           "    assert f(a) == a, 'msg'\n")
    new = (src.replace("[1, 2]", "[1, 3]").replace("ValueError", "TypeError").replace("KeyError", "IndexError")
           .replace("assert_called_once_with(a)", "assert_called_once_with(a, 1)").replace("== a, 'msg'", "!= a, 'msg'"))
    texts = sorted(t for c in bg.d_changes(src, new) for t in bg.element_texts(src, c.old))  # type: ignore[attr-defined]
    want = sorted(["pytest.mark.parametrize('a', [1, 2])", "@pytest.mark.parametrize('a', [1, 2])",
                   "with pytest.raises(ValueError):", "except KeyError as exc:", "m.assert_called_once_with(a)",
                   "assert f(a) == a, 'msg'"])
    if texts != want:
        fails.append(f"옛 문장 원문: {texts}")
    feed = "X = 1\n\x0c\ndef test_a():\n    assert X == 1\n"    # `\f` 줄 — str.splitlines 로 나누면 줄 번호가 밀린다
    texts = sorted(t for c in bg.d_changes(feed, feed.replace("X == 1", "X == 2")) for t in bg.element_texts(feed, c.old))  # type: ignore[attr-defined]
    if texts != ["assert X == 1"]:
        fails.append(f"`\\f` 든 원문의 옛 문장: {texts}")
    if bg.d_changes("def f(:\n", "") is not None or bg.d_changes(None, "") is not None:  # type: ignore[attr-defined]
        fails.append("파싱 못 하는 판 · 없는 원문은 None 이어야 한다")
    if bg.d_changes("", "def test_n():\n    assert 1\n")[0].state != "추가":  # type: ignore[attr-defined]
        fails.append("빈 판 → 새 함수의 원소는 «추가»")
    return fails


def property_checks() -> "list[str]":
    """배치 결속 속성 시험(설계 §8 감사 단위) — 합성 표본(`\\f` · `\\r\\n` · `\\r` · 끝 줄바꿈 없음 · BOM · latin-1 표지 · decorator ·
    주석)마다 ① 역변환(`<module>` 의 자리 표시를 단위 원문으로 바꾸면 원래 바이트) ② 한 기준에 대한 변형들의 키 집합이 같으면 바이트가
    같다(서로 다른 변형이 같은 키 집합을 내지 않는다)."""
    bg = STATE["bg"]
    fails: "list[str]" = []
    samples: "list[bytes]" = [s.encode("utf-8") for s in (
        B6, B6_AUDITED, B6_SWAPPED, B6_V1, B6_V2, MOD_BASE, MOD_MOVED, R41, R44B, M20, "",
        "def a():\n    return 1\n\x0c\ndef test_x():\n    assert a() == 1\n",
        "import os\r\n\r\n\r\n@deco\r\ndef test_a():\r\n    assert os\r\n# 끝 주석",
        "X = 1\rdef f():\r    return X\r\r\rclass T:\r    def test_m(self):\r        assert f() == 1\r",
        "\ufeff# bom\n@pytest.mark.parametrize('a', [1])\n# 사이 주석\ndef test_p(a):\n    assert a\n\nY = 2  # 꼬리",
        "def g(): return 1; x = 2\n\n\nif True:\n    def h():\n        pass\n\n\ndef test_g():\n    assert g() == 1")]
    samples.append("# -*- coding: latin-1 -*-\nX = '\xe9'\n\n\ndef test_l():\n    assert X == '\xe9'\n".encode("latin-1"))
    for i, data in enumerate(samples):
        split, why = bg.audit_split(data)  # type: ignore[attr-defined]
        if split is None or bg.audit_join(split) != data:  # type: ignore[attr-defined]
            fails.append(f"역변환 표본 {i}: {why or '바이트 다름'}")
    for i, base in enumerate(samples[:-1]):
        text = base.decode("utf-8")
        variants: "set[bytes]" = {base}
        lines = text.splitlines(keepends=True)
        for j in range(len(lines)):
            variants.add("".join(lines[:j] + ["\n"] + lines[j:]).encode("utf-8"))          # 빈 줄 끼움
            variants.add("".join(lines[:j] + ["# c\n"] + lines[j:]).encode("utf-8"))       # 주석 끼움
            if j + 1 < len(lines):
                variants.add("".join(lines[:j] + [lines[j + 1], lines[j]] + lines[j + 2:]).encode("utf-8"))  # 이웃 줄 맞바꿈
        variants.add((text + "\n").encode("utf-8"))
        variants.add(text.rstrip("\n").encode("utf-8"))
        seen: "dict[frozenset, bytes]" = {}
        for v in variants:
            keys = frozenset(bg.audit_keys(base, v, True)[0])  # type: ignore[attr-defined]
            if keys in seen and seen[keys] != v:
                fails.append(f"키 집합 충돌 표본 {i}: 서로 다른 두 판이 같은 키 {sorted(keys)}")
            seen[keys] = v
    return fails


def window_checks() -> "list[str]":
    """창 절차(리팩토링 모드) — 모드 동결 · digest 불일치 open 거부 · rebind(기준선 유지) · rebind 없이 close 실행 불능 · 옛 기록."""
    fails: "list[str]" = []

    def expect(label: str, got: "tuple[int, str]", code: int, *needles: str) -> None:
        missing = [n for n in needles if n not in got[1]]
        if got[0] != code or missing:
            fails.append(f"{label}: exit {got[0]} (기대 {code} · 없는 글 {missing})\n{got[1]}")

    with tempfile.TemporaryDirectory(prefix="bg-rw-") as td:
        repo = _rrepo(Path(td), {TP: SIMPLE})
        expect("--mode 빠짐", _rguard(repo, "open", "--kind", "code"), 1, "--mode refactor|feature 가 필요하다")
        expect("모드 · 폴더 어긋남(refactor 폴더에 feature)", _rguard(repo, "open", "--kind", "code", "--mode", "feature"), 1, "어긋난다")
        expect("명세 승인판 못 읽음 → follow open 실행 불능", _rguard(repo, "open", "--kind", "follow", "--mode", "refactor"), 1,
               "refactor_audit.changes_snapshot 실패")
        _stage(repo, _snap(retain=(TP,)))
        expect("G1 확정 없음 → follow open 거부", _rguard(repo, "open", "--kind", "follow", "--mode", "refactor"), 1,
               "`G1 변경판 확정` 줄이 없다")
        _bind(repo, _snap(retain=(TP,)))
        _stage(repo, _snap(retain=(TP, "x.py")))
        expect("digest 불일치 open 거부", _rguard(repo, "open", "--kind", "change", "--mode", "refactor"), 1, "≠ 마지막 `G1 변경판 확정`")
        _bind(repo, _snap(retain=(TP, "x.py")), "2026-10-04T03:20Z")
        got = _rguard(repo, "open", "--kind", "follow", "--mode", "refactor")
        expect("digest 같음 → open(요약에 open 기록 경로 — 폴더 인자부터)", got, 0, "G1 digest",
               f"open 기록 {RFOLDER}/behavior/{RUN}/w1-open.json")
        said = got[1].rsplit("open 기록 ", 1)[-1].split()[0] if "open 기록 " in got[1] else ""
        baseline = repo / said                            # Coordinator 가 요약 경로를 그대로 `changes --baseline` 에 넘긴다(cwd = 저장소)
        if not (said and baseline.is_file() and {"head", "dirty"} <= set(json.loads(baseline.read_text(encoding="utf-8")))):
            fails.append(f"요약의 open 기록 경로 «{said}» 를 그대로 열어 head · dirty 를 읽지 못했다")
        expect("rebind — 새 G1 없음", _rguard(repo, "rebind"), 1, "새 `G1 변경판 확정` 이 없다")
        expect("follow close(무변) → green", _rguard(repo, "close"), 0, "시험 쪽 무변")
        expect("다음 창 open(앞 창 닫힘)", _rguard(repo, "open", "--kind", "code", "--mode", "refactor"), 0, "w2",
               f"open 기록 {RFOLDER}/behavior/{RUN}/w2-open.json")
        if not (repo / RFOLDER / "behavior" / RUN / "w2-open.json").is_file():
            fails.append("요약이 가리킨 open 기록 파일이 없다")
        expect("rebind — code 창", _rguard(repo, "rebind"), 1, "follow · change 창이 아니다")
    with tempfile.TemporaryDirectory(prefix="bg-rw2-") as td:  # rebind 뒤 기준선 유지(5 → 9 · 창 기준선 «== 5»)
        value = "def value():\n    return 5\n\n\ndef test_v():\n    assert value() == 5\n"
        repo = _rrepo(Path(td), {TP: value})
        _bind(repo, _snap())
        expect("change open", _rguard(repo, "open", "--kind", "change", "--mode", "refactor"), 0, "변경")
        _write(repo, {TP: value.replace("== 5", "== 7")})
        expect("승인 밖 기대 변화 → red", _rguard(repo, "close"), 2, "red")
        _write(repo, {TP: value.replace("== 5", "== 9")})
        g1b = _snap(_v("V1", f"{TP}::test_v", ["assert value() == 5"]))
        _stage(repo, g1b)
        expect("승인판 바뀜 · rebind 없이 close → 실행 불능", _rguard(repo, "close"), 1, "rebind")
        _bind(repo, g1b, "2026-10-04T03:30Z")
        expect("G1′ 확정 · rebind 없이 close → 실행 불능", _rguard(repo, "close"), 1, "rebind")
        expect("rebind", _rguard(repo, "rebind"), 0, "rebind 1회째")
        got = _rguard(repo, "close")
        expect("rebind 뒤 close — 창 기준선 «== 5» 대조 → 승인 변경 감사", got, 0, "승인 변경 감사 1")
        opened = json.loads((_run_dir(repo) / "w1-open.json").read_text(encoding="utf-8"))
        if len(opened.get("rebinds", [])) != 1 or opened.get("g1_digest") != _k0_digest(g1b):
            fails.append(f"rebind 기록 {opened.get('rebinds')} · {opened.get('g1_digest')}")
    with tempfile.TemporaryDirectory(prefix="bg-rw6-") as td:  # 0C close — 허용 표를 동결하지 않고 G1 확정판에서 읽는다
        repo = _rrepo(Path(td), {TP: SIMPLE})
        expect("0C open 은 G1 확정이 없어도 연다(동결 없음)", _rguard(repo, "open", "--kind", "code", "--mode", "refactor"), 0, "0C")
        expect("0C close — 명세 승인판 못 읽음 → 실행 불능", _rguard(repo, "close"), 1, "refactor_audit.changes_snapshot 실패")
        _stage(repo, _snap())
        expect("0C close — G1 확정 없음 → 실행 불능", _rguard(repo, "close"), 1, "`G1 변경판 확정` 줄이 없다 — 리팩토링 모드 0C close")
        _bind(repo, _snap())
        expect("0C close — 승인판 = G1 확정 → 판정", _rguard(repo, "close"), 0, "시험 쪽 무변")
        _stage(repo, _snap(other=(("application/billing/api.py", "공유 표면", "0C"),)))
        _write(repo, {"application/billing/api.py": "def charge():\n    return 2\n"})
        expect("0C close — 스냅숏 digest ≠ G1 확정 → 실행 불능", _rguard(repo, "close"), 1, "승인판이 G1 확정과 다르다")
        _bind(repo, _snap(other=(("application/billing/api.py", "공유 표면", "0C"),)), "2026-10-04T03:40Z")
        expect("0C close — G1′ 확정 뒤 목록 안 경로 → 통과", _rguard(repo, "close"), 0, "판정 2회째")
        (repo / RFOLDER / "audit" / AUDIT_STAMP / "plan.md").unlink()
        expect("대상 BC 를 못 읽음 → close 실행 불능", _rguard(repo, "close"), 1, "대상 BC 를 모른다")
    with tempfile.TemporaryDirectory(prefix="bg-rw7-") as td:  # 0T close — D 확정 유무와 무관하게 G1 확정판을 읽는다
        repo = _rrepo(Path(td), {TP: SIMPLE})
        row_snap = _snap(update=((f"{TP}::test_check", None),))
        expect("0T open 은 G1 확정이 없어도 연다(동결 없음)", _rguard(repo, "open", "--kind", "test", "--mode", "refactor"), 0, "0T")
        _stage(repo, _snap())
        expect("0T close — G1 확정 없음 → 실행 불능", _rguard(repo, "close"), 1, "`G1 변경판 확정` 줄이 없다 — 리팩토링 모드 0T close")
        _bind(repo, _snap())
        expect("0T close — 승인판 = G1 확정 → 판정", _rguard(repo, "close"), 0, "시험 쪽 무변")
        _stage(repo, row_snap)
        expect("0T close — 스냅숏 digest ≠ G1 확정 → 실행 불능(D 확정이 없어도)", _rguard(repo, "close"), 1, "승인판이 G1 확정과 다르다")
        _write(repo, {TP: SIMPLE.replace("== 9", ">= 9")})
        expect("0T close — 스냅숏 digest ≠ G1 확정 → 실행 불능(update 행 케이스의 D 확정)", _rguard(repo, "close"), 1,
               "승인판이 G1 확정과 다르다")
        _bind(repo, row_snap, "2026-10-04T03:40Z")
        expect("0T close — G1′ 확정 뒤 update 행 케이스 → 개별 감사", _rguard(repo, "close"), 0, "감사 요청 키 1", "개별 감사 1")
        (repo / RFOLDER / "audit" / AUDIT_STAMP / "plan.md").unlink()
        expect("0T close — 대상 BC 를 못 읽음 → 실행 불능", _rguard(repo, "close"), 1, "대상 BC 를 모른다")
    with tempfile.TemporaryDirectory(prefix="bg-rw8-") as td:  # 0T — G1 뒤 명세에 remove 행이 더해짐 → 스냅숏 digest 다름
        two_cases = SIMPLE + "\n\ndef test_old():\n    assert 2 == 2\n"
        repo = _rrepo(Path(td), {TP: two_cases})
        _bind(repo, _snap())
        _rguard(repo, "open", "--kind", "test", "--mode", "refactor")
        _write(repo, {TP: SIMPLE})
        _stage(repo, _snap(remove=((f"{TP}::test_old", None),)))
        expect("0T — G1 뒤 remove 행 추가 → 실행 불능", _rguard(repo, "close"), 1, "승인판이 G1 확정과 다르다")
        _bind(repo, _snap(remove=((f"{TP}::test_old", None),)), "2026-10-04T03:50Z")
        expect("0T — G1′ 확정 뒤 remove 행 케이스 삭제 → 개별 감사", _rguard(repo, "close"), 0, "감사 요청 키 2")
    with tempfile.TemporaryDirectory(prefix="bg-rw5-") as td:  # 변경 창 둘 — 승인 V 연산 − 앞 창 생성분
        repo = _rrepo(Path(td), {TP: SIMPLE})
        digest = _bind(repo, _snap(_v("V1", ops=(("core", ADD_F), ("core", ADD_G)))))
        _rguard(repo, "open", "--kind", "change", "--mode", "refactor")
        _write(repo, {MIG_PATH: MIG(ADD_F)})
        _commit(repo)
        expect("변경 창 1 — 승인 연산 하나 생성", _rguard(repo, "close"), 0, "시험 쪽 무변")
        _rguard(repo, "open", "--kind", "change", "--mode", "refactor")
        third = "application/core/migrations/0003_w.py"
        _write(repo, {third: MIG(ADD_F)})
        _commit(repo)
        expect("변경 창 2 — 앞 창에서 이미 생성된 연산을 또 생성 → red", _rguard(repo, "close"), 2, "승인 밖 연산 ×1")
        _write(repo, {third: MIG(ADD_G)})
        _commit(repo)
        expect("변경 창 2 — 남은 승인 연산 생성 → green", _rguard(repo, "close"), 0, "판정 2회째")
        _suite(repo, digest)
        expect("verify — 연산 누계 = 승인 다중집합", _rguard(repo, "verify"), 0, "창 2(0T 0 · 0C 0 · 0F 0 · 변경 2)",
               "연산 승인 2 = 생성 2(다중집합)", "감사 키 일치 0/0")
    with tempfile.TemporaryDirectory(prefix="bg-rw3-") as td:  # 모드 칸 없는 옛 창(리팩토링 폴더) → 실행 불능
        repo = _rrepo(Path(td), {TP: SIMPLE})
        _rguard(repo, "open", "--kind", "code", "--mode", "refactor")
        f = _run_dir(repo) / "w1-open.json"
        record = json.loads(f.read_text(encoding="utf-8"))
        record.pop("mode")
        f.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
        expect("옛 open 기록(모드 칸 없음) close → 실행 불능", _rguard(repo, "close"), 1, "모드 칸이 없다")
        expect("옛 open 기록 verify → 실행 불능", _rguard(repo, "verify"), 1, "모드 칸이 없다")
    with tempfile.TemporaryDirectory(prefix="bg-rw4-") as td:  # 기능 폴더(`-refactor-` 없음)
        repo = _repo(Path(td))
        expect("기능 폴더 --mode 빠짐", _rguard(repo, "open", "--kind", "code", folder=FOLDER), 1, "--mode refactor|feature 가 필요하다")
        expect("기능 폴더에 --mode refactor", _rguard(repo, "open", "--kind", "code", "--mode", "refactor", folder=FOLDER), 1,
               "어긋난다")
        expect("기능 모드 follow", _rguard(repo, "open", "--kind", "follow", "--mode", "feature", folder=FOLDER), 1,
               "리팩토링 모드 창")
        expect("support --collect 빠짐", _rguard(repo, "support", folder=FOLDER), 1, "--collect")
        got = _rguard(repo, "support", "--collect", folder=FOLDER)
        if "요약:" not in got[1] or got[0] not in (0, 1, 2):
            fails.append(f"support --collect 위임: exit {got[0]}\n{got[1]}")
        got = _rguard(repo, "suite", folder=FOLDER)
        if "요약:" not in got[1] or got[0] not in (0, 1, 2):
            fails.append(f"suite 위임: exit {got[0]}\n{got[1]}")
    return fails


def verify_checks() -> "list[str]":
    """verify(리팩토링 모드) — 세 줄 · 감사 키 일대일(중복 · 누락 · 추가 · 낡음 · 다름) · r5 · 보충 · 승인 V 실행 흔적 · suite 대조."""
    fails: "list[str]" = []

    def expect(label: str, got: "tuple[int, str]", code: int, *needles: str) -> None:
        missing = [n for n in needles if n not in got[1]]
        if got[0] != code or missing:
            fails.append(f"{label}: exit {got[0]} (기대 {code} · 없는 글 {missing})\n{got[1]}")

    def window(td: str, kind: str, files: dict, edit: "Callable[[Path], None]", snap: dict) -> "tuple[Path, str, dict]":
        repo = _rrepo(Path(td), files)
        digest = _bind(repo, snap)
        _rguard(repo, "open", "--kind", kind, "--mode", "refactor")
        edit(repo)
        _commit(repo)
        _rguard(repo, "close")
        return repo, digest, _last_close(repo)

    r41_new = R41.replace("import Old,", "import New,").replace("subject = Old", "subject = New")
    with tempfile.TemporaryDirectory(prefix="bg-rv-") as td:
        repo, digest, record = window(td, "code", {TP: R41}, _edit(RENAME, r41_new), _snap())
        expect("suite 기록 없음 → red", _rguard(repo, "verify"), 2, "suite 기록 없음", "suite: 기록 없음")
        _audit(repo, 1, _rows(record))
        _suite(repo, digest)
        expect("일대일 green", _rguard(repo, "verify"), 0, "동작 보존: 창 1(0T 0 · 0C 1 · 0F 0 · 변경 0)",
               "감사 키 일치 2/2(중복 0 · 누락 0 · 추가 0 · 낡음 0 · 다름 0)", "바뀐 것 실행: 승인 V 0건",
               "suite: 실행 정의 aaaaaaaaaaaa = G1 결속", "요약: 동작 보존 green")
        rows = _rows(record)
        for label, written, needle in (
                ("중복", rows + rows[:1], "중복 1"), ("누락", rows[:1], "누락 1"),
                ("추가", rows + [f"{RUN}/w1 · {TP} · helper · 전 없음 · 후 aaaaaaaaaaaa | 판정 = 기대 의미 그대로 | x"], "추가 1"),
                ("다름", [rows[0], rows[1].replace("기대 의미 그대로", "다름")], "다름 1"),
                ("승인 변경 밖 키의 «승인 후와 같음»", [rows[0], rows[1].replace("기대 의미 그대로", "승인 후와 같음")], "다름 1"),
                ("판형 줄 베낌(값 셋을 칸으로)", [rows[0], rows[1].replace(
                    "| 판정 = 기대 의미 그대로 |", "| 판정 = 기대 의미 그대로 | 승인 후와 같음 | 다름 |")], "판정 형식 밖"),
                ("값 둘을 `/` 로", [rows[0], rows[1].replace("기대 의미 그대로", "기대 의미 그대로 / 다름")], "판정 = 기대 의미 그대로 / 다름"),
                ("판정 칸 비움", [rows[0], rows[1].replace("판정 = 기대 의미 그대로", "판정 =")], "판정 = 없음"),
                ("닫힌 셋 밖 값", [rows[0], rows[1].replace("기대 의미 그대로", "통과")], "판정 = 통과"),
                ("판정 칸 둘", [rows[0], rows[1].replace("| 픽스처", "| 판정 = 다름 | 픽스처")], "판정 형식 밖")):
            _audit(repo, 1, written)
            judged_form: "tuple[str, ...]" = ("다름 1",) if needle.startswith(("판정 형식 밖", "판정 = ")) else ()
            expect(f"감사 키 {label} → red", _rguard(repo, "verify"), 2, needle, *judged_form, "요약: 동작 보존 red")
        for label, written in (
                ("정상 행", rows),
                ("근거에 판정 낱말이 든 정상 행", [x.replace("| 픽스처", "| 승인 후와 같음 아님 — 다름 없이 같은 대상을 부른다")
                                             for x in rows]),
                ("키 백틱 · 앞 `- ` · 판정 값 꾸밈 없음", [f"- `{x.split(' | ', 1)[0]}` | " + x.split(" | ", 1)[1] for x in rows])):
            _audit(repo, 1, written)
            expect(f"감사 키 {label} → green", _rguard(repo, "verify"), 0, "감사 키 일치 2/2", "요약: 동작 보존 green")
        _audit(repo, 1, rows)
        _audit(repo, 1, [rows[0], rows[1].split(" | ")[0]], round_no=2)
        expect("최신 회차의 미판정 키 줄 → red(앞 회차 판정으로 되돌아가지 않음)", _rguard(repo, "verify"), 2, "다름 1",
               "판정 칸 · 구분자 없는 키 줄(미판정)")
        _audit(repo, 1, [rows[0], f"  - `{rows[1].split(' | ')[0]}` — 요구 판정: 기대 의미 그대로"], round_no=2)
        expect("최신 회차에 감사 요청 키 줄을 베낌 → red", _rguard(repo, "verify"), 2, "다름 1", "미판정")
        _audit(repo, 1, rows, round_no=2)
        expect("최신 회차를 정상 행으로 → green", _rguard(repo, "verify"), 0, "요약: 동작 보존 green")
        close_file = _run_dir(repo) / "w1-close.json"
        saved_close = close_file.read_text(encoding="utf-8")
        hacked = json.loads(saved_close)
        hacked[-1]["dispositions"] = []
        hacked[-1]["keys"] = []
        close_file.write_text(json.dumps(hacked, ensure_ascii=False), encoding="utf-8")
        expect("close 기록의 처분이 빠진 바뀐 시험 쪽 경로 → 자동 초록 red", _rguard(repo, "verify"), 2,
               f"w1 처분 없는 바뀐 시험 쪽 경로 {TP}", "자동 초록 1")
        close_file.write_text(saved_close, encoding="utf-8")
        _write(repo, {TP: r41_new + "\n# 감사 뒤 편집\n"})
        got = _rguard(repo, "verify")
        expect("suite 기록 뒤 시험 쪽 파일 편집 → 지문 다름 red(마지막 close 안내 없음)", got, 2, "지문 다름")
        if "마지막 창 close 뒤에 커밋" in got[1]:
            fails.append(f"suite 뒤 편집인데 «마지막 창 close 뒤» 안내가 나왔다\n{got[1]}")
        _write(repo, {TP: r41_new})
        _suite(repo, digest, verdict="red", reasons=["대역 사유"])
        expect("suite red → red", _rguard(repo, "verify"), 2, "suite 판정 red")
        _suite(repo, digest, counts={**GOOD_COUNTS, "failed": 1})
        expect("suite 실패 보고 1 → red", _rguard(repo, "verify"), 2, "suite 실패 보고 1")
        _suite(repo, digest, counts={**GOOD_COUNTS, "selected": 2})
        expect("suite 선택 합 ≠ 수집 합 → red", _rguard(repo, "verify"), 2, "suite 선택 합 2 ≠ 수집 합 3")
        _suite(repo, digest, counts={**GOOD_COUNTS, "proof_ok": 2})
        expect("suite 결과 증거 모자람 → red", _rguard(repo, "verify"), 2, "suite 결과 증거 2/3")
        _suite(repo, digest, commands=[{"argv": ["pytest"], "exit": 1, "probe_exit": 1, "outputs": 1, "workers_ready": 0,
                                        "worker_outputs": 0, "seconds": 0.1}])
        expect("suite 명령 exit 1 → red", _rguard(repo, "verify"), 2, "suite 명령 exit")
        _suite(repo, "0" * 12)
        expect("suite 의 G1 결속 다름 → red", _rguard(repo, "verify"), 2, "G1 결속", "≠ G1 결속")
        _suite(repo, digest, g0_keep=["파일 단위: application/core/test/test_check.py"])
        expect("suite G0 유지 위반 → red", _rguard(repo, "verify"), 2, "suite G0 유지: 파일 단위")
        _suite(repo, digest)
        expect("suite 다시 → green", _rguard(repo, "verify"), 0, "요약: 동작 보존 green")
        _write(repo, {"application/core/real.py": "def product():\n    return 9  # 뒤\n"})
        _commit(repo, "after close")
        _suite(repo, digest)
        expect("마지막 close 뒤 커밋 · suite 는 그 뒤 → red + 안내(close 다시)", _rguard(repo, "verify"), 2,
               "— 마지막 창 close 뒤에 커밋 · 편집이 있었다: 그 창 close 를 다시 돌린 뒤 suite 를 다시 돈다")
        _rguard(repo, "close")
        _suite(repo, digest)
        expect("그 창 close 다시 · suite 다시 → green", _rguard(repo, "verify"), 0, "요약: 동작 보존 green")
        _rguard(repo, "open", "--kind", "code", "--mode", "refactor")
        _write(repo, {TP: r41_new.replace("== 5", "== 6")})
        _rguard(repo, "close")
        _suite(repo, digest)
        expect("열린 창(red close) → red", _rguard(repo, "verify"), 2, "열린 창 w2")
    with tempfile.TemporaryDirectory(prefix="bg-rv8-") as td:  # 창 누락 — ⓐ 결정이 있는데 창이 없다
        repo = _rrepo(Path(td), {TP: SIMPLE})
        expect("창 누락 → red", _rguard(repo, "verify"), 2, "창 누락", "`G1 변경판 확정` 줄 없음", "suite 기록 없음",
               "동작 보존: 창 0(0T 0 · 0C 0 · 0F 0 · 변경 0)")
    with tempfile.TemporaryDirectory(prefix="bg-rv2-") as td:  # 낡음 — 감사 뒤 단위 편집
        repo, digest, record = window(td, "follow", {TP: B6}, _edit({}, B6_V1), _retain())
        _audit(repo, 1, _rows(record))
        _write(repo, {TP: B6_V2})
        _commit(repo)
        expect("닫힌 마지막 창을 다시 close(감사 뒤 편집)", _rguard(repo, "close"), 0, "판정 2회째", "감사 요청 키 2")
        _suite(repo, digest)
        expect("보충: 감사 뒤 새 정의의 자리만 옮김 → `<module>` 낡음 red", _rguard(repo, "verify"), 2, "낡음 1", "누락 0")
    with tempfile.TemporaryDirectory(prefix="bg-rv3-") as td:  # r5 — 감사 뒤 정의 순서 교환
        repo, digest, record = window(td, "follow", {TP: B6}, _edit({}, B6_AUDITED), _retain())
        _audit(repo, 1, _rows(record))
        _write(repo, {TP: B6_SWAPPED})
        _commit(repo)
        expect("닫힌 마지막 창을 다시 close(감사 뒤 순서 교환)", _rguard(repo, "close"), 0, "판정 2회째", "감사 요청 키 1")
        _suite(repo, digest)
        expect("r5: 감사 뒤 정의 순서 교환 → 옛 키 «추가» · 새 `<file>` 키 «누락» red", _rguard(repo, "verify"), 2, "추가 1", "누락 1")
        _audit(repo, 1, _rows(_last_close(repo)), round_no=2)
        expect("r5: 새 `<file>` 키만 다시 감사(2회차) → green", _rguard(repo, "verify"), 0, "요약: 동작 보존 green")
    with tempfile.TemporaryDirectory(prefix="bg-rv4-") as td:  # 변경 창 — 승인 V 실행 흔적 · 연산 다중집합
        snap = _snap(_v("V1", f"{TP}::test_raise", ["with pytest.raises(InsufficientFunds):"]),
                     _v("V2", ops=(("core", ADD_F),)))
        edit = _edit({"application/core/errors.py": ERRORS.replace("InsufficientFunds", "NotEnoughFunds"), MIG_PATH: MIG(ADD_F)},
                     RAISE_TEST.replace("InsufficientFunds", "NotEnoughFunds"))
        repo, digest, record = window(td, "change", {TP: RAISE_TEST, "application/core/errors.py": ERRORS}, edit, snap)
        _audit(repo, 1, _rows(record))
        _suite(repo, digest)
        expect("변경 창 green — 승인 V · 연산 · 기대 원소 흔적", _rguard(repo, "verify"), 0,
               "동작 보존: 창 1(0T 0 · 0C 0 · 0F 0 · 변경 1)", "승인 변경 2",
               "바뀐 것 실행: 승인 V 2건 · 연산 승인 1 = 생성 1(다중집합) · 기존 마이그레이션 변경 0 · 승인 기대 원소 1 중 변경 1 · "
               f"목록 밖 다른 BC 파일 0 · digest {digest} = G1 변경판 확정")
        wanted = dict(zip(record["dispositions"][0]["keys"], record["dispositions"][0]["요구 판정"]))
        unit_of = {k.split(" · ")[2]: k for k in wanted}
        if (wanted[unit_of["test_raise"]], wanted[unit_of["<module>"]]) != ("승인 후와 같음", "기대 의미 그대로"):
            fails.append(f"승인 변경 파일의 키별 요구 판정 {wanted}")
        if "`" + unit_of["test_raise"] + "` — 요구 판정: 승인 후와 같음(후 = V1)" not in _request(repo):
            fails.append("감사 요청에 승인 원소 단위의 요구 판정 줄이 없다")
        _audit(repo, 1, [f"{unit_of['test_raise']} | 판정 = 기대 의미 그대로 | x", f"{unit_of['<module>']} | 판정 = 기대 의미 그대로 | x"])
        expect("승인 원소 단위에 «기대 의미 그대로» → red(승인 변경 미검출 · G1′)", _rguard(repo, "verify"), 2, "다름 1",
               "승인 변경 미검출 — 승인 원소 단위가 «기대 의미 그대로»: V 를 지우고 0F 로(G1′)")
        _audit(repo, 1, [f"{unit_of['test_raise']} | 판정 = 승인 후와 같음 | x", f"{unit_of['<module>']} | 판정 = 승인 후와 같음 | x"])
        expect("승인 원소 밖 단위에 «승인 후와 같음» → red", _rguard(repo, "verify"), 2, "다름 1",
               "판정 = 승인 후와 같음 · 요구 판정 기대 의미 그대로")
    with tempfile.TemporaryDirectory(prefix="bg-rv5-") as td:  # 승인 기대 원소 실행 흔적 없음(연산은 없음 — 이것만으로 red)
        snap = _snap(_v("V1", f"{TP}::test_check", ["assert product() == 9"]))
        repo, digest, record = window(td, "change", {TP: SIMPLE}, _edit({}, SIMPLE.replace("    assert", "    # 설명\n    assert")),
                                      snap)
        _audit(repo, 1, _rows(record))
        _suite(repo, digest)
        expect("승인 변경 미검출 → red", _rguard(repo, "verify"), 2, "승인 기대 원소 1 중 변경 0 — 실행 흔적 없음 1",
               "연산 승인 0 = 생성 0(다중집합)", "감사 키 일치 1/1")
    with tempfile.TemporaryDirectory(prefix="bg-rv7-") as td:  # 승인 연산 미생성(기대 원소는 없음 — 이것만으로 red)
        repo, digest, record = window(td, "change", {TP: SIMPLE}, _edit({"application/core/real.py": "def product():\n    return 8\n"}),
                                      _snap(_v("V2", ops=(("core", ADD_F),))))
        _suite(repo, digest)
        expect("승인 연산 미생성 → red", _rguard(repo, "verify"), 2, "연산 승인 1 ≠ 생성 0(다중집합 — 실행 흔적 없음 1 · 승인 밖 0)",
               "승인 기대 원소 0 중 변경 0", "감사 키 일치 0/0")
    with tempfile.TemporaryDirectory(prefix="bg-rv9-") as td:  # 0T update 행 승인 키 — «승인 후와 같음»도 받는다
        case = f"{TP}::test_check"
        repo, digest, record = window(td, "test", {TP: SIMPLE}, _edit({}, "# 정리\n" + SIMPLE.replace("== 9", ">= 9")),
                                      _snap(update=((case, None),)))
        same = [f"{k} | 판정 = 승인 후와 같음 | update 행 승인 범위 안" for k in record["keys"]]
        _suite(repo, digest)
        _audit(repo, 1, same)
        expect("0T update 행 승인 키에 «승인 후와 같음» → green", _rguard(repo, "verify"), 0, "개별 감사 2", "감사 키 일치 2/2",
               "요약: 동작 보존 green")
        _audit(repo, 1, [same[0], same[1].replace("승인 후와 같음", "기대 의미 그대로")])
        expect("0T update 행 승인 키에 «기대 의미 그대로» → green", _rguard(repo, "verify"), 0, "감사 키 일치 2/2")
        _audit(repo, 1, [same[0], same[1].replace("승인 후와 같음", "다름")])
        expect("0T update 행 승인 키에 «다름» → red", _rguard(repo, "verify"), 2, "다름 1")
    with tempfile.TemporaryDirectory(prefix="bg-rv10-") as td:  # 0T 일반 개별 감사 키 — «승인 후와 같음»은 지금대로 «다름»
        repo, digest, record = window(td, "test", {TP: SIMPLE}, _edit({}, SIMPLE.replace("    assert", "    # 설명\n    assert")),
                                      _snap(update=((f"{TP}::test_check", None),)))
        _suite(repo, digest)
        _audit(repo, 1, [f"{k} | 판정 = 승인 후와 같음 | x" for k in record["keys"]])
        expect("0T 일반 개별 감사 키(D 확정 없음)에 «승인 후와 같음» → red", _rguard(repo, "verify"), 2, "다름 1", "감사 키 일치 0/1")
    with tempfile.TemporaryDirectory(prefix="bg-rv6-") as td:  # 창 넷(0T → 0C → 0F → 변경) — 창마다 감사 기록 · 한 줄 집계
        imp, raising = "application/core/test/test_imp.py", "application/core/test/test_raise.py"
        repo = _rrepo(Path(td), {TP: SIMPLE, imp: IMPORT_ONLY, raising: RAISE_TEST, "application/core/errors.py": ERRORS})
        digest = _bind(repo, _snap(_v("V1", f"{raising}::test_raise", ["with pytest.raises(InsufficientFunds):"]), retain=(TP,)))
        steps = (("test", _edit({}, SIMPLE.replace("    assert", "    # 설명\n    assert"))),
                 ("code", _edit(MOVE, OLD_TO_NEW(IMPORT_ONLY), path=imp)),
                 ("follow", _edit({}, SIMPLE.replace("    assert", "    # 설명\n    assert") + "\n\ndef _h():\n    return 1\n")),
                 ("change", _edit({"application/core/errors.py": ERRORS.replace("InsufficientFunds", "NotEnoughFunds")},
                                  RAISE_TEST.replace("InsufficientFunds", "NotEnoughFunds"), path=raising)))
        for n, (kind, edit) in enumerate(steps, 1):
            expect(f"창 넷 — w{n} open", _rguard(repo, "open", "--kind", kind, "--mode", "refactor"), 0, f"w{n}")
            edit(repo)
            _commit(repo)
            expect(f"창 넷 — w{n} close", _rguard(repo, "close"), 0, "감사 요청 키")
            _audit(repo, n, _rows(_last_close(repo)))
        _suite(repo, digest)
        expect("창 넷 verify green", _rguard(repo, "verify"), 0, "동작 보존: 창 4(0T 1 · 0C 1 · 0F 1 · 변경 1) · 열린 창 0",
               "묶음 감사 1(묶음 1) · 개별 감사 3 · 승인 변경 2 · red 0 · 자동 초록 0 · 감사 키 일치 6/6",
               "승인 V 1건", "승인 기대 원소 1 중 변경 1", "요약: 동작 보존 green")
    return fails


def main() -> int:
    stub_support: bool = "--stub-support" in sys.argv[1:]
    fails: "list[str]" = []
    for case in cases():
        msg = run_case(*case)
        print(("  ✗ " if msg else "  ✓ ") + case[0])
        if msg:
            fails.append(msg)
    proc = procedure_checks()
    print(("  ✗ " if proc else "  ✓ ") + "창 절차(앵커 선행 · 창 누락 · 재open 거부 · 열린 창 · close 재실행 · 두 번째 창 · 재상정 · 머지 · 대응 원소 기록)")
    fails += proc
    with tempfile.TemporaryDirectory(prefix="bg-stub-") as stub:
        _setup_refactor(Path(stub), stub_support)
        print(f"  — 리팩토링 모드(G1 스냅숏 대역 · behavior_support {'대역' if stub_support else '진짜'})")
        refactor = rcases()
        for case in refactor:
            msg, (files, keyed, reds) = run_rcase(case)
            print(("  ✗ " if msg else "  ✓ ") + f"{case['label']} · 시험 쪽 바뀐 파일 {files} = 키 {keyed} + red {reds}")
            if msg:
                fails.append(f"{case['label']}: {msg}")
        for label, check in (("배치 결속 속성(역변환 · 키 집합 = 바이트)", property_checks),
                             ("D 함수 수준(발생 순번 짝 · 옛 문장 원문 · 파싱 불가)", d_checks),
                             ("창 절차(모드 동결 · digest · rebind · 옛 기록 · support/suite 위임)", window_checks),
                             ("verify(세 줄 · 감사 키 일대일 · r5 · 보충 · 승인 V 흔적 · suite 대조)", verify_checks)):
            got = check()
            print(("  ✗ " if got else "  ✓ ") + label)
            fails += [f"{label}: {g}" for g in got]
        totals: "list[int]" = STATE["totals"]  # type: ignore[assignment]
        broken: "list[str]" = STATE["invariant_fails"]  # type: ignore[assignment]
        print(("  ✗ " if broken else "  ✓ ") + f"자동 초록 0 — 리팩토링 close {totals[0]}회 전부에서 시험 쪽 바뀐 파일 {totals[1]} = "
              f"감사 키 낸 파일 {totals[2]} + red 파일 {totals[3]}")
        fails += [f"자동 초록 0: {b}" for b in broken]
    if fails:
        print("\nFAIL — behavior_guard 픽스처 기대 불일치:")
        for f in fails:
            print("  - " + f.replace("\n", "\n    "))
        return 1
    print(f"\nPASS — behavior_guard 픽스처 기능 모드 {len(cases())}사례 + 창 절차 · 리팩토링 모드 {len(refactor)}사례 + 속성 · D · "
          f"창 절차 · verify 기대 일치(리팩토링 close {totals[0]}회 · 시험 쪽 바뀐 파일 {totals[1]} = 감사 키 {totals[2]} + "
          f"red {totals[3]} · 자동 초록 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
