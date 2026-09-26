#!/usr/bin/env python3
"""behavior_guard.py 픽스처 러너 — 합성 git 저장소로 0C/0T 판정·마이그레이션·창 절차를 고정한다(로드맵 4 · 설계 v4 §4).

각 사례는 새 임시 저장소에서 «기준 커밋 → open → 편집(커밋 또는 작업 트리) → close» 를 돌려 exit 와 요약을 대조한다.
현장 재생(spring_dream 5커밋 green · 계약 변경 7커밋 red)은 구현 리뷰 기록(scratch)이 맡고, 여기서는 규칙마다 양성·음성을 둔다.
exit 0 = 전건 기대 일치 · 1 = 불일치.
"""
from __future__ import annotations

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
        code, out = _guard(repo, "open", "--kind", kind)
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
        code, out = _guard(repo, "open", "--kind", "code")
        if code != 1 or "build_anchor" not in out:
            fails.append(f"앵커 선행: exit {code}\n{out}")
        anchor.write_text(saved, encoding="utf-8")
        code, out = _guard(repo, "verify")
        if code != 2 or "창 누락" not in out:
            fails.append(f"verify 창 누락: exit {code}\n{out}")
        _guard(repo, "open", "--kind", "code")
        code, out = _guard(repo, "open", "--kind", "code")
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
        code, out = _guard(repo, "open", "--kind", "test")
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
        _guard(repo, "open", "--kind", "test")
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
        _guard(repo, "open", "--kind", "code")
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
        _guard(repo, "open", "--kind", "code")
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
        _guard(repo, "open", "--kind", "code")
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
    return fails


def main() -> int:
    fails: "list[str]" = []
    for case in cases():
        msg = run_case(*case)
        print(("  ✗ " if msg else "  ✓ ") + case[0])
        if msg:
            fails.append(msg)
    proc = procedure_checks()
    print(("  ✗ " if proc else "  ✓ ") + "창 절차(앵커 선행 · 창 누락 · 재open 거부 · 열린 창 · close 재실행 · 두 번째 창 · 재상정 · 머지)")
    fails += proc
    if fails:
        print("\nFAIL — behavior_guard 픽스처 기대 불일치:")
        for f in fails:
            print("  - " + f.replace("\n", "\n    "))
        return 1
    print(f"\nPASS — behavior_guard 픽스처 {len(cases())}사례 + 창 절차 기대 일치")
    return 0


if __name__ == "__main__":
    sys.exit(main())
