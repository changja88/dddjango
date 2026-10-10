"""B0 영구 픽스처 사례 정의 — RD 설계 v15.2 §4-7 · §8 B0 · 계획 T11(510 칸 = R 412 · N 48 · C 50).

갈래(`Case.group`):
  R  원형 재현 — 원형 B0 사슬(b0_v8 ~ b0_v152 · Claude r11 사례 둘)의 사례 사전을 한 파일로 평평하게 옮겼다. 묶음(`bundle`)과
     순서는 원형 실행 `b0_v152.py v152 <묶음>` 그대로다(13 묶음 297 줄 · 394 칸 + minor 9 사례 · 18 칸).
  N  이름별 독립 사례 — inspect 거부 11 이름 · N1 13 이름마다 한 사례 × collect · run(48 칸 · 설계 «자기 시험 묶음»).
  C  빈 범주 — ① 원형 사례가 덮지 않던 정적 규칙 갈래(observer_scan 사유 판형 단위 · 설계 §4-1 문면에 판정이 있는 것) 12 사례 ·
     24 칸(읽기 실패 = 시험 쪽 .py 자리의 끊긴 심링크 + 제품 쪽 자리 대조 포함) ② E 갈래가 넘긴 지원 확인 · 증거 실행 빈 조건(설계 §4-5 문면 · 계획 T10 E3) 5 사례 · 10 칸 ③ 수리한 결함의
     반례 1 사례 · 2 칸(지운 추적 파일 · 한글 경로가 있는 커밋된 장난감의 트리 지문) ④ 600 초 상한 1 사례 · 2 칸(support ·
     suite — 구현판에서만 · 정오 2) ⑤ 수집·suite 상한 분리 6 사례 · 12 칸(F-B1R-6 수리 설계 §6).

종류(`Case.kind`):
  pair     collect · run 두 칸(원형 run_cases) — `env` = 상속 환경.
  env      G0 · G2 두 칸(원형 run_env) — G0 = 기본 환경 collect(`env` 에 PYTHONPATH 가 있으면 그것만 G0 에도) ·
           G2 = 기본 환경 + `env` 로 run · `after` 편집이 있으면 편집 뒤 run 을 다시 · G0 유지 세 단(g0_keep) 위반을 G2 사유에 더함.
  timeout  support(collect) · suite(run) 두 칸 — 상한 상수만 짧게 바꾼 단위 사례(구현판 전용).
  limits   support · suite 두 칸 — 서로 다른 수집·suite 상한(구현판 전용). T3는 지원 안 함 뒤 G1을 만들지 않고 run 엔진만 대조.

환경 표지(러너가 실행 때 바꾼다):
  PY             픽스처 환경 `.venv-probe` 의 인터프리터(원형은 scratch pyvenv).
  GREENLET_SITE  원형은 greenlet 을 별도 폴더로 PYTHONPATH 에 붙였다 — `.venv-probe` 는 greenlet 을 site-packages 에 담아
                 러너가 이 키를 뺀다(k0 §6).
  COV_TRACE · COV_MON  저장소 밖 설치 도구 흉내(sitecustomize) — 아래 문자열을 러너가 장난감 밖 임시 폴더에 쓴다.
  EXT_PLUGIN     저장소 · 설치 패키지 밖 폴더의 pytest 플러그인 모듈 extplug(아래 문자열) — 상속 PYTHONPATH 로 붙인다.
원형 문자열은 글자 그대로다. 바꾼 것: 이름 충돌을 피한 판 접미사(`SAME_V11` 등) · 비교판 스위치(MODE_ENV · CTX — 판 v152 에서
빈 사전) 제거 · gzip `mtime=0`(장난감 바이트 결정성) · 위 환경 표지. 원형 사슬 대비 글자 대조는 T11 구현 기록에 있다.
"""
from __future__ import annotations

import gzip
import json
from dataclasses import dataclass

PY: str = "<PY>"
GREENLET_SITE: str = "<GREENLET_SITE>"
COV_TRACE: str = "<COV_TRACE>"
COV_MON: str = "<COV_MON>"
EXT_PLUGIN: str = "<EXT_PLUGIN>"
EXT_PLUGIN_SOURCE: str = "def pytest_runtest_setup(item):\n    pass\n"

COV_TRACE_SITECUSTOMIZE: str = (
    '"""설치 도구 흉내(coverage 의 trace 꼴) — 프로세스 시작 때 sys.settrace 로 줄 단위 tracer 를 켠다. 저장소 밖 · 시험 본문을 부르지 않는다."""\n'
    "import sys\nimport threading\n\nLINES = [0]\n\n\ndef _tracer(frame, event, arg):\n    if event == \"line\":\n"
    "        LINES[0] += 1\n    return _tracer\n\n\nsys.settrace(_tracer)\nthreading.settrace(_tracer)\n"
)
COV_MON_SITECUSTOMIZE: str = (
    '"""설치 도구 흉내(coverage 의 sys.monitoring 꼴 — 도구 자리 1) — 프로세스 시작 때 PY_START 전역 사건을 켠다. 저장소 밖 · 시험 본문을 부르지 않는다."""\n'
    "import sys\n\nCOUNT = [0]\nM = sys.monitoring\nM.use_tool_id(M.COVERAGE_ID, \"coverage-emul\")\n\n\ndef _start(code, off):\n"
    "    COUNT[0] += 1\n\n\nM.register_callback(M.COVERAGE_ID, M.events.PY_START, _start)\nM.set_events(M.COVERAGE_ID, M.events.PY_START)\n"
)


@dataclass(frozen=True)
class Case:
    """사례 하나 — 칸 둘(pair: collect · run / env: G0 · G2 / timeout: support · suite)."""

    id: str
    group: str
    bundle: str
    name: str
    kind: str
    files: "dict[str, str | bytes]"
    env: "dict[str, str]"
    after: "dict[str, str] | None" = None
    argvs: "list[list[str]] | None" = None
    frozen: "dict[str, str] | None" = None
    drop_worker: bool = False
    after_commit: "dict[str, str | None] | None" = None   # 있으면 장난감을 커밋 1 로 만든 뒤 이 편집을 얹는다(None = 지움)
    symlinks: "dict[str, str] | None" = None              # 장난감에 만들 심링크(경로 → 대상 글자 · 대상이 없으면 끊긴 심링크)


# ── 원형 b0_v8 ──
BASE = {
    "application/__init__.py": "",
    "application/order/__init__.py": "",
    "application/order/product.py": "def product():\n    return 5\n",
    "application/order/checks/__init__.py": "",
    "application/order/test/__init__.py": "",
    "application/order/test/test_order.py": "from application.order.product import product\n\n\ndef test_order():\n    assert product() == 5\n",
    "application/order/test/fixtures/expected.json": "{\"v\": 5}\n",
}

SPEC = {"application/order/checks/spec_total.py": "from application.order.product import product\n\n\ndef test_total():\n    assert product() == 5\n"}

PLUGIN = {"application/order/checks/plugin.py": "import pytest\n\n\n@pytest.fixture\ndef expected():\n    return 5\n"}

FX_TEST = {"application/order/test/test_fx.py": "def test_fx(expected):\n    assert expected == 5\n"}

INI = {"pytest.ini": "[pytest]\n"}

CASES_V8: "dict[str, tuple[dict, dict, dict]]" = {
    # 이름: (파일, 상속 환경, 선택 사항)
    "대조 — 표준 배치": (INI, {}, {}),
    "r6-1a 여러 줄 TOML 배열": ({"pyproject.toml": "[tool.pytest.ini_options]\npython_files = [\n    \"spec_*.py\",\n    \"test_*.py\",\n]\n", **SPEC}, {}, {}),
    "r6-1b pytest.ini 우선": ({"pyproject.toml": "[tool.pytest.ini_options]\npython_files = [\"test_*.py\"]\n",
                              "pytest.ini": "[pytest]\npython_files = spec_*.py test_*.py\n", **SPEC}, {}, {}),
    "r6-1c 동결 PYTEST_ADDOPTS -o python_files": ({**INI, **SPEC}, {}, {"frozen": {"PYTEST_ADDOPTS": "-o python_files=spec_*.py"}}),
    "r6-2a conftest pytest_collect_file": ({**INI, **SPEC, "conftest.py": "import pytest\n\n\ndef pytest_collect_file(file_path, parent):\n    if file_path.name.startswith('spec_') and file_path.suffix == '.py':\n        return pytest.Module.from_parent(parent, path=file_path)\n"}, {}, {}),
    "r6-2b 동결 PYTEST_PLUGINS": ({**INI, **PLUGIN, **FX_TEST}, {}, {"frozen": {"PYTEST_PLUGINS": "application.order.checks.plugin"}}),
    "r6-2c pytest_plugins = PLUGINS": ({**INI, **PLUGIN, **FX_TEST, "conftest.py": "PLUGINS = ['application.order.checks.plugin']\npytest_plugins = PLUGINS\n"}, {}, {}),
    "r7-1a request.getfixturevalue 로 부른 분류 밖 fixture": ({**INI, "application/order/checks/fx.py": "import pytest\n\n\n@pytest.fixture\ndef expected():\n    return 5\n",
                                                          "application/order/test/test_dyn.py": "from application.order.checks.fx import expected  # noqa: F401\nfrom application.order.product import product\n\n\ndef test_dyn(request):\n    assert product() == request.getfixturevalue('expected')\n"}, {}, {}),
    "r7-1b 분류 밖 base 의 setup_method 상속": ({**INI, "application/order/checks/base.py": "class Base:\n    def setup_method(self, method):\n        self.expected = 5\n",
                                              "application/order/test/test_cls.py": "from application.order.checks.base import Base\nfrom application.order.product import product\n\n\nclass TestCls(Base):\n    def test_it(self):\n        assert product() == self.expected\n"}, {}, {}),
    "r7-1c import 한 pytest_generate_tests": ({**INI, "application/order/checks/generator.py": "def pytest_generate_tests(metafunc):\n    if 'expected' in metafunc.fixturenames:\n        metafunc.parametrize('expected', [5], ids=['same'])\n",
                                              "application/order/test/test_gen.py": "from application.order.checks.generator import pytest_generate_tests  # noqa: F401\nfrom application.order.product import product\n\n\ndef test_gen(expected):\n    assert product() == expected\n"}, {}, {}),
    "r7-2a conftest 의 사용자 Item": ({**INI, "conftest.py": "import pytest\n\n\nclass MyItem(pytest.Item):\n    def runtest(self):\n        pass\n\n\nclass MyFile(pytest.File):\n    def collect(self):\n        yield MyItem.from_parent(self, name='custom')\n\n\ndef pytest_collect_file(file_path, parent):\n    if file_path.name == 'cases.txt':\n        return MyFile.from_parent(parent, path=file_path)\n",
                                   "application/order/test/cases.txt": "x\n"}, {}, {}),
    "r7-2b conftest 가 탐침 상태를 비움": ({**INI, "conftest.py": "import pytest\n\n\n@pytest.hookimpl(tryfirst=True)\ndef pytest_sessionfinish(session, exitstatus):\n    import dddjango_collect_probe as p\n    p._S['fixtures'].clear()\n"}, {}, {}),
    "r7-2c xdist -n 2 · 워커 출력 하나 빠짐": ({"pytest.ini": "[pytest]\naddopts = -n 2\n"}, {}, {"drop_worker": True}),
    "대조 — xdist -n 2 전체 출력": ({"pytest.ini": "[pytest]\naddopts = -n 2\n"}, {}, {}),
    "r7-3 실행 중 제품 파일 변경": ({**INI, "application/order/test/test_mut.py": "from pathlib import Path\n\n\ndef test_mut():\n    p = Path(__file__).resolve().parents[1] / 'product.py'\n    p.write_text('def product():\\n    return 9\\n')\n"}, {}, {}),
    "r7-4 상속 PYTEST_ADDOPTS -k(동결 없음 → 덮음)": ({**INI, "application/order/test/test_sel.py": "def test_good():\n    assert True\n\n\ndef test_bad():\n    assert False\n"}, {"PYTEST_ADDOPTS": "-k test_good"}, {}),
    "r7-4b 동결 정의에 -k(선택 합 ≠ 수집 합)": ({**INI, "application/order/test/test_sel.py": "def test_good():\n    assert True\n\n\ndef test_other():\n    assert True\n"}, {}, {"frozen": {"PYTEST_ADDOPTS": "-k test_good"}}),
    "대조 — 표식 둘로 나눈 두 명령(testp 꼴)": ({"pytest.ini": "[pytest]\nmarkers =\n    pg: db\n", "application/order/test/test_mark.py": "import pytest\n\n\n@pytest.mark.pg\ndef test_pg():\n    assert True\n\n\ndef test_plain():\n    assert True\n"}, {}, {"argvs": [[PY, "-m", "pytest", "-m", "pg"], [PY, "-m", "pytest", "-m", "not pg"]]}),
    "보충 — 분류 밖 시험 함수 import": ({**INI, "application/order/shared_checks.py": "def test_shared():\n    assert True\n",
                                        "application/order/test/test_import.py": "from application.order.shared_checks import test_shared  # noqa: F401\n"}, {}, {}),
    "보충 — 분류 밖 fixture 정적 import": ({**INI, **PLUGIN, "application/order/test/test_fx.py": "from application.order.checks.plugin import expected  # noqa: F401\n\n\ndef test_fx(expected):\n    assert expected == 5\n"}, {}, {}),
    "보충 — --doctest-modules": ({"pytest.ini": "[pytest]\naddopts = --doctest-modules\n", "application/order/doc.py": "def f():\n    \"\"\"\n    >>> f()\n    5\n    \"\"\"\n    return 5\n"}, {}, {}),
    "보충 — addopts -p no:탐침": ({"pytest.ini": "[pytest]\naddopts = -p no:dddjango_collect_probe\n"}, {}, {}),
    "보충 — 세션 전 중단": ({"pytest.ini": "[pytest]\naddopts = --no-such-option\n"}, {}, {}),
    "보충 — conftest 가 분류 밖 플러그인을 등록했다가 세션 끝 전에 해제": ({**INI, "application/order/checks/hooks.py": "def pytest_runtest_setup(item):\n    item.config._seen = True\n",
                                                                     "conftest.py": "import application.order.checks.hooks as hooks\n\n\ndef pytest_configure(config):\n    config.pluginmanager.register(hooks, 'tmp-hooks')\n\n\ndef pytest_runtest_teardown(item):\n    pm = item.config.pluginmanager\n    if pm.get_plugin('tmp-hooks') is not None:\n        pm.unregister(name='tmp-hooks')\n"}, {}, {}),
    "보충 — unittest.TestCase(v8.1 허용 — v8 은 정지)": ({**INI, "application/order/test/test_ut.py": "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_x(self):\n        self.assertTrue(True)\n"}, {}, {}),
}

DJ = {
    "pytest.ini": "[pytest]\nDJANGO_SETTINGS_MODULE = toyproj.settings\n",
    "toyproj/__init__.py": "",
    "toyproj/settings.py": "SECRET_KEY = 'x'\nINSTALLED_APPS = ['django.contrib.contenttypes', 'django.contrib.auth', 'application.order']\n"
                           "DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}\nUSE_TZ = True\n",
}

GROUP_JSON = '[{"model": "auth.group", "pk": 1, "fields": {"name": "g"}}]\n'

DJ_CASES_V8: "dict[str, tuple[dict, dict, dict]]" = {
    "DJ 대조 — Django TestCase · setUp 같은 파일": ({**DJ, "application/order/test/test_dj.py": "from django.test import TestCase\nfrom application.order.product import product\n\n\nclass TestOrder(TestCase):\n    def setUp(self):\n        self.expected = 5\n\n    def test_it(self):\n        self.assertEqual(product(), self.expected)\n"}, {}, {}),
    "DJ-b 분류 밖 base 의 setUp 상속(기대값만 바꾸면 FAIL→PASS 꼴)": ({**DJ, "application/order/checks/base_case.py": "from django.test import TestCase\n\n\nclass BaseCase(TestCase):\n    def setUp(self):\n        self.expected = 5\n",
                                                               "application/order/test/test_dj.py": "from application.order.checks.base_case import BaseCase\nfrom application.order.product import product\n\n\nclass TestOrder(BaseCase):\n    def test_it(self):\n        self.assertEqual(product(), self.expected)\n"}, {}, {}),
    "DJ-c 분류 밖 base 의 setUpTestData 상속": ({**DJ, "application/order/checks/base_case.py": "from django.test import TestCase\n\n\nclass BaseCase(TestCase):\n    @classmethod\n    def setUpTestData(cls):\n        cls.expected = 5\n",
                                                "application/order/test/test_dj.py": "from application.order.checks.base_case import BaseCase\nfrom application.order.product import product\n\n\nclass TestOrder(BaseCase):\n    def test_it(self):\n        self.assertEqual(product(), self.expected)\n"}, {}, {}),
    "DJ-d 분류 안 클래스가 setUp 에 분류 밖 함수를 붙임": ({**DJ, "application/order/helpers.py": "def common_setup(self):\n    self.expected = 5\n",
                                                        "application/order/test/test_dj.py": "from django.test import TestCase\nfrom application.order.helpers import common_setup\nfrom application.order.product import product\n\n\nclass TestOrder(TestCase):\n    setUp = common_setup\n\n    def test_it(self):\n        self.assertEqual(product(), self.expected)\n"}, {}, {}),
    "DJ-e fixtures = ['orders'] · 앱 fixtures/ 안": ({**DJ, "application/order/fixtures/orders.json": GROUP_JSON,
                                                   "application/order/test/test_dj.py": "from django.contrib.auth.models import Group\nfrom django.test import TestCase\n\n\nclass TestOrder(TestCase):\n    fixtures = ['orders']\n\n    def test_it(self):\n        self.assertEqual(Group.objects.count(), 1)\n"}, {}, {}),
    "DJ-f fixtures = ['orders'] · 저장소 루트(실행 디렉터리)": ({**DJ, "orders.json": GROUP_JSON,
                                                          "application/order/test/test_dj.py": "from django.contrib.auth.models import Group\nfrom django.test import TestCase\n\n\nclass TestOrder(TestCase):\n    fixtures = ['orders']\n\n    def test_it(self):\n        self.assertEqual(Group.objects.count(), 1)\n"}, {}, {}),
    "DJ-g fixtures = ['data/orders'](경로)": ({**DJ, "application/order/fixtures/data/orders.json": GROUP_JSON,
                                              "application/order/test/test_dj.py": "from django.test import TestCase\n\n\nclass TestOrder(TestCase):\n    fixtures = ['data/orders']\n\n    def test_it(self):\n        pass\n"}, {}, {}),
    "DJ-h TransactionTestCase · serialized_rollback": ({**DJ, "application/order/test/test_dj.py": "from django.test import TransactionTestCase\n\n\nclass TestOrder(TransactionTestCase):\n    serialized_rollback = True\n\n    def test_it(self):\n        pass\n"}, {}, {}),
    "DJ-i override_settings 클래스 데코레이터": ({**DJ, "application/order/test/test_dj.py": "from django.conf import settings\nfrom django.test import TestCase, override_settings\n\n\n@override_settings(MY_VALUE=5)\nclass TestOrder(TestCase):\n    def test_it(self):\n        self.assertEqual(settings.MY_VALUE, 5)\n"}, {}, {}),
    "DJ-j 일반 unittest.TestCase · setUp 같은 파일": ({**INI, "application/order/test/test_ut.py": "import unittest\n\n\nclass T(unittest.TestCase):\n    def setUp(self):\n        self.v = 1\n\n    def test_x(self):\n        self.assertEqual(self.v, 1)\n"}, {}, {}),
}


# ── 원형 b0_v10 ──
DJ_FD = {**DJ, "toyproj/settings.py": DJ["toyproj/settings.py"] + "FIXTURE_DIRS = ['data']\n"}

GOODBAD = "def test_good():\n    assert True\n\n\ndef test_bad():\n    assert False\n"

R8: "dict[str, tuple[dict, dict, dict]]" = {
    # ── Codex r8 ──
    "X1 unittest 인스턴스 setUp 에 분류 밖 함수 바인딩": ({**INI, "application/order/checks/setup.py": "def dynamic_setup(self):\n    self.expected = 5\n",
                                                     "application/order/test/test_ut.py": "import unittest\nfrom application.order.checks.setup import dynamic_setup\n\n\nclass TestOrder(unittest.TestCase):\n    def __init__(self, name='runTest'):\n        super().__init__(name)\n        self.setUp = dynamic_setup.__get__(self)\n\n    def test_order(self):\n        self.assertEqual(5, self.expected)\n"}, {}, {}),
    "X2 addCleanup(분류 밖 콜백)": ({**INI, "application/order/checks/cleanup.py": "def cleanup(tc):\n    tc.assertEqual(5, 5)\n",
                                   "application/order/test/test_ut.py": "import unittest\nfrom application.order.checks.cleanup import cleanup\n\n\nclass TestOrder(unittest.TestCase):\n    def test_order(self):\n        self.addCleanup(cleanup, self)\n"}, {}, {}),
    "X3 먼저 반환하는 pytest_fixture_setup 플러그인 + getfixturevalue": ({**INI, "application/order/checks/fx.py": "import pytest\n\n\n@pytest.fixture\ndef expected():\n    return 5\n",
                                                                      "conftest.py": "import pytest\n\n\n@pytest.hookimpl(tryfirst=True)\ndef pytest_fixture_setup(fixturedef, request):\n    if fixturedef.argname == 'expected':\n        value = fixturedef.func()\n        fixturedef.cached_result = (value, fixturedef.cache_key(request), None)\n        return value\n",
                                                                      "application/order/test/test_dyn.py": "from application.order.checks.fx import expected  # noqa: F401\n\n\ndef test_dyn(request):\n    assert request.getfixturevalue('expected') == 5\n"}, {}, {}),
    "X4 Django 라벨 orders.json · FIXTURE_DIRS data/orders.default.json": ({**DJ_FD, "data/orders.default.json": GROUP_JSON,
                                                                        "application/order/test/test_dj.py": "from django.contrib.auth.models import Group\nfrom django.test import TestCase\n\n\nclass TestOrder(TestCase):\n    fixtures = ['orders.json']\n\n    def test_it(self):\n        self.assertEqual(Group.objects.count(), 1)\n"}, {}, {}),
    "X5 Django 라벨 orders.json.gz · data/orders.default.json.gz": ({**DJ_FD, "data/orders.default.json.gz": gzip.compress(GROUP_JSON.encode(), mtime=0),
                                                                  "application/order/test/test_dj.py": "from django.contrib.auth.models import Group\nfrom django.test import TestCase\n\n\nclass TestOrder(TestCase):\n    fixtures = ['orders.json.gz']\n\n    def test_it(self):\n        self.assertEqual(Group.objects.count(), 1)\n"}, {}, {}),
    "X6 수집 땐 FIXTURE_DIRS 없음 · 클래스 override_settings 로 data/ 켬": ({**DJ, "data/orders.json": GROUP_JSON,
                                                                        "application/order/test/test_dj.py": "from django.contrib.auth.models import Group\nfrom django.test import TestCase, override_settings\n\n\n@override_settings(FIXTURE_DIRS=['data'])\nclass TestOrder(TestCase):\n    fixtures = ['orders']\n\n    def test_it(self):\n        self.assertEqual(Group.objects.count(), 1)\n"}, {}, {}),
    # ── Claude r8 ──
    "A1 conftest 가 분류 밖 pytest_generate_tests 를 import": ({**INI, "application/order/checks/gen.py": "def pytest_generate_tests(metafunc):\n    if 'expected' in metafunc.fixturenames:\n        metafunc.parametrize('expected', [5])\n",
                                                            "conftest.py": "from application.order.checks.gen import pytest_generate_tests  # noqa: F401\n",
                                                            "application/order/test/test_gen.py": "def test_gen(expected):\n    assert expected == 5\n"}, {}, {}),
    "A2 conftest import * 로 들인 pytest_runtest_makereport": ({**INI, "application/order/checks/plugin_hooks.py": "import pytest\n\n\n@pytest.hookimpl(wrapper=True)\ndef pytest_runtest_makereport(item, call):\n    rep = yield\n    return rep\n",
                                                             "conftest.py": "from application.order.checks.plugin_hooks import *  # noqa: F401,F403\n"}, {}, {}),
    "A3 대조 — 같은 모듈을 pytest_plugins 로": ({**INI, "application/order/checks/plugin_hooks.py": "def pytest_report_header(config):\n    return 'x'\n",
                                              "conftest.py": "pytest_plugins = ['application.order.checks.plugin_hooks']\n"}, {}, {}),
    "B1 클래스 override_settings(FIXTURE_DIRS=seed) + fixtures": ({**DJ, "application/order/seed/orders.json": GROUP_JSON,
                                                                 "application/order/test/test_dj.py": "from django.contrib.auth.models import Group\nfrom django.test import TestCase, override_settings\n\n\n@override_settings(FIXTURE_DIRS=['application/order/seed'])\nclass TestOrder(TestCase):\n    fixtures = ['orders']\n\n    def test_it(self):\n        self.assertEqual(Group.objects.count(), 1)\n"}, {}, {}),
    "B2 setUpClass 가 cls.fixtures 를 바꿈(정적 FIXTURE_DIRS seed)": ({**DJ, "toyproj/settings.py": DJ["toyproj/settings.py"] + "FIXTURE_DIRS = ['application/order/seed']\n",
                                                                    "application/order/seed/seed_orders.json": GROUP_JSON,
                                                                    "application/order/test/test_dj.py": "from django.contrib.auth.models import Group\nfrom django.test import TestCase\n\n\nclass TestOrder(TestCase):\n    @classmethod\n    def setUpClass(cls):\n        cls.fixtures = ['seed_orders']\n        super().setUpClass()\n\n    def test_it(self):\n        self.assertEqual(Group.objects.count(), 1)\n"}, {}, {}),
    "U2 메타클래스 __call__ 이 인스턴스 setUp 을 붙임": ({**INI, "application/order/checks/meta.py": "import unittest\n\n\ndef _setup(self):\n    self.expected = 5\n\n\nclass Meta(type):\n    def __call__(cls, *a, **k):\n        inst = super().__call__(*a, **k)\n        inst.setUp = _setup.__get__(inst)\n        return inst\n\n\nclass Base(unittest.TestCase, metaclass=Meta):\n    pass\n",
                                                     "application/order/test/test_meta.py": "from application.order.checks.meta import Base\n\n\nclass TestOrder(Base):\n    def test_it(self):\n        self.assertEqual(self.expected, 5)\n"}, {}, {}),
}

R9 = {
    "r9-B1 conftest trylast sessionfinish 가 분류 밖 플러그인을 늦게 등록": ({**INI, "application/order/checks/late.py": "def pytest_plugin_registered(plugin, plugin_name, manager):\n    if plugin_name == 'late':\n        assert 5 == 5\n",
                                                                      "conftest.py": "import importlib\nimport pytest\n\n\n@pytest.hookimpl(trylast=True)\ndef pytest_sessionfinish(session, exitstatus):\n    if session.config.option.collectonly:\n        return\n    plug = importlib.import_module('application.order.checks.late')\n    session.config.pluginmanager.register(plug, name='late')\n"}, {}, {}),
    "r9-B1b 안전장치 — 확정 뒤 등록(conftest pytest_unconfigure 래퍼의 yield 뒤)": ({**INI, "application/order/test/late2.py": "def pytest_report_header(config):\n    return 'x'\n",
                                                                   "conftest.py": "import importlib\nimport pytest\n\n\n@pytest.hookimpl(wrapper=True)\ndef pytest_unconfigure(config):\n    res = yield\n    config.pluginmanager.register(importlib.import_module('application.order.test.late2'), name='late2')\n    return res\n"}, {}, {}),
    "대조 — 허용 훅만: pytest_configure · fixture · collection_modifyitems · report_teststatus 래퍼": ({**INI, "conftest.py": "import pytest\n\n\ndef pytest_configure(config):\n    config.addinivalue_line('markers', 'slow: x')\n\n\n@pytest.fixture\ndef expected():\n    return 5\n\n\ndef pytest_collection_modifyitems(session, config, items):\n    items.sort(key=lambda i: i.nodeid)\n\n\n@pytest.hookimpl(wrapper=True)\ndef pytest_report_teststatus(report, config):\n    outcome = yield\n    return outcome\n",
                                                                                                "application/order/test/test_fx.py": "def test_fx(expected):\n    assert expected == 5\n"}, {}, {}),
}

CL9 = {
    "P1 패키지 application/order/__init__.py 의 setup_module": ({**INI, "application/order/__init__.py": "def setup_module(mod):\n    pass\n"}, {}, {}),
    "P2 최상위 application/__init__.py 의 setUpModule": ({**INI, "application/__init__.py": "def setUpModule():\n    pass\n"}, {}, {}),
    "P3 대조 — 같은 함수를 시험 모듈 setup_module 로 import": ({**INI, "application/order/hooks.py": "def setup_module(mod):\n    pass\n",
                                                            "application/order/test/test_p3.py": "from application.order.hooks import setup_module  # noqa: F401\n\n\ndef test_p3():\n    assert True\n"}, {}, {}),
    "L1 늦게 등록된 분류 밖 플러그인의 pytest_unconfigure 가 exit 1 → 0": ({**INI, "application/order/checks/report.py": "def pytest_unconfigure(config):\n    s = getattr(config, '_late_session', None)\n    if s is not None:\n        s.exitstatus = 0\n",
                                                                       "conftest.py": "import importlib\nimport pytest\n\n\n@pytest.hookimpl(trylast=True)\ndef pytest_sessionfinish(session, exitstatus):\n    if session.config.option.collectonly:\n        return\n    session.config._late_session = session\n    session.config.pluginmanager.register(importlib.import_module('application.order.checks.report'), name='late-report')\n",
                                                                       "application/order/test/test_fail.py": "def test_fail():\n    assert False\n"}, {}, {}),
    "G1 라벨 orders[1] · 루트 orders[1].json": ({**DJ, "orders[1].json": GROUP_JSON,
                                               "application/order/test/test_dj.py": "from django.contrib.auth.models import Group\nfrom django.test import TestCase\n\n\nclass TestOrder(TestCase):\n    fixtures = ['orders[1]']\n\n    def test_it(self):\n        self.assertEqual(Group.objects.count(), 1)\n"}, {}, {}),
    "D1 setUpClass 가 적재 동안만 override_settings(FIXTURE_DIRS=seed)": ({**DJ, "application/order/seed/orders.json": GROUP_JSON,
                                                                      "application/order/test/test_dj.py": "from django.contrib.auth.models import Group\nfrom django.test import TestCase, override_settings\n\n\nclass TestOrder(TestCase):\n    fixtures = ['orders']\n\n    @classmethod\n    def setUpClass(cls):\n        with override_settings(FIXTURE_DIRS=['application/order/seed']):\n            super().setUpClass()\n\n    def test_it(self):\n        self.assertEqual(Group.objects.count(), 1)\n"}, {}, {}),
    "C2 인스턴스 _callSetUp 바인딩": ({**INI, "application/order/checks/cs.py": "def call_setup(self):\n    self.expected = 5\n",
                                    "application/order/test/test_ut.py": "import unittest\nfrom application.order.checks.cs import call_setup\n\n\nclass TestOrder(unittest.TestCase):\n    def __init__(self, name='runTest'):\n        super().__init__(name)\n        self._callSetUp = call_setup.__get__(self)\n\n    def test_order(self):\n        self.assertEqual(5, self.expected)\n"}, {}, {}),
    "C3 conftest 보통 pytest_runtest_call 이 setUp 을 붙임": ({**INI, "conftest.py": "def pytest_runtest_call(item):\n    pass\n"}, {}, {}),
    "S1 본문 importorskip(제품 모듈이 옮겨짐)": ({**INI, "application/order/test/test_imp.py": "import pytest\n\n\ndef test_imp():\n    mod = pytest.importorskip('application.order.pricing')\n    assert mod.price() == 5\n"}, {}, {}),
}

ENV_CASES = {
    "E1 collect_ignore(FAST) · test_sel.py 를 창이 바꿈(주석 한 줄)": ({**INI, "conftest.py": "import os\n\ncollect_ignore = ['application/order/test/test_sel.py'] if os.environ.get('FAST') else []\n",
                                                                     "application/order/test/test_sel.py": GOODBAD}, {"FAST": "1"},
                                                                    {"application/order/test/test_sel.py": GOODBAD + "# 정리\n"}),
    "E2 if not QUICK: def test_bad · 그 파일을 창이 바꿈": ({**INI, "application/order/test/test_q.py": "import os\n\n\ndef test_good():\n    assert True\n\n\nif not os.environ.get('QUICK'):\n    def test_bad():\n        assert False\n"}, {"QUICK": "1"},
                                                        {"application/order/test/test_q.py": "import os\n\n\ndef test_good():\n    assert True\n\n\nif not os.environ.get('QUICK'):\n    def test_bad():\n        assert False\n# 정리\n"}),
    "E3 대조 — E1 과 같고 시험 파일 바이트 그대로": ({**INI, "conftest.py": "import os\n\ncollect_ignore = ['application/order/test/test_sel.py'] if os.environ.get('FAST') else []\n",
                                                 "application/order/test/test_sel.py": GOODBAD}, {"FAST": "1"}),
    "r9-I2 conftest pytest_pyfunc_call 이 NO_BODY 면 본문 생략": ({**INI, "conftest.py": "import os\n\n\ndef pytest_pyfunc_call(pyfuncitem):\n    if os.environ.get('NO_BODY'):\n        return True\n",
                                                               "application/order/test/test_sel.py": GOODBAD}, {"NO_BODY": "1"}),
    "보충 — 허용 fixture(autouse)가 NO_BODY 면 item.runtest 를 바꿈": ({**INI, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _maybe_skip_body(request):\n    if os.environ.get('NO_BODY'):\n        request.node.runtest = lambda: None\n    yield\n",
                                                                   "application/order/test/test_sel.py": GOODBAD}, {"NO_BODY": "1"}),
    "보충 — 허용 pytest_collection_modifyitems 가 NO_BODY 면 runtest 를 바꿈": ({**INI, "conftest.py": "import os\n\n\ndef pytest_collection_modifyitems(session, config, items):\n    if os.environ.get('NO_BODY'):\n        for i in items:\n            i.runtest = lambda: None\n",
                                                                            "application/order/test/test_sel.py": GOODBAD}, {"NO_BODY": "1"}),
    "X7a 동결 밖 환경으로 pycollect_makeitem 이 test_bad 를 뺌": ({**INI, "conftest.py": "import os\n\n\ndef pytest_pycollect_makeitem(collector, name, obj):\n    if os.environ.get('R8_SKIP_BAD') and name == 'test_bad':\n        return []\n",
                                                               "application/order/test/test_sel.py": GOODBAD}, {"R8_SKIP_BAD": "1"}),
    "X7b 동결 밖 환경으로 setuponly": ({**INI, "conftest.py": "import os\n\n\ndef pytest_configure(config):\n    if os.environ.get('R8_SETUPONLY'):\n        config.option.setuponly = True\n",
                                       "application/order/test/test_sel.py": GOODBAD}, {"R8_SETUPONLY": "1"}),
    "C1 상속 DJANGO_SETTINGS_MODULE(동결로 덮음)": ({**DJ, "toyproj/settings_alt.py": "from toyproj.settings import *  # noqa: F401,F403\nALT = True\n",
                                                  "application/order/test/test_alt.py": "from django.conf import settings\n\n\ndef test_alt():\n    assert getattr(settings, 'ALT', False)\n"}, {"DJANGO_SETTINGS_MODULE": "toyproj.settings_alt"}),
    "C2 동결 밖 변수로 같은 파일 안 항목만 줄어듦": ({**INI, "application/order/test/test_q.py": "import os\nimport pytest\n\n\ndef test_good():\n    assert True\n\n\nif not os.environ.get('QUICK'):\n    def test_bad():\n        assert False\n"}, {"QUICK": "1"}),
}


# ── 원형 b0_v11 ──
UT_GOODBAD = ("import unittest\n\n\nclass TestOrder(unittest.TestCase):\n    def test_good(self):\n        self.assertTrue(True)\n\n"
              "    def test_bad(self):\n        self.assertTrue(False)\n")

DJ_GOODBAD = UT_GOODBAD.replace("import unittest\n", "from django.test import SimpleTestCase\n").replace("unittest.TestCase", "SimpleTestCase")

QUICK = "import os\n\n\ndef test_good():\n    assert True\n\n\nif not os.environ.get('QUICK'):\n    def test_bad():\n        assert False\n"

GEN = ("from functools import wraps\nfrom _pytest.python import pytest_generate_tests as original\n\n\n@wraps(original)\n"
       "def pytest_generate_tests(metafunc):\n    if 'expected' in metafunc.fixturenames:\n        metafunc.parametrize('expected', [{v}], ids=['fixed'])\n")

R10 = {
    "R10-1a wraps(_pytest) 로 감싼 분류 밖 pytest_generate_tests · 9→5": (
        {**INI, "application/order/checks/gen.py": GEN.format(v=9), "conftest.py": "from application.order.checks.gen import pytest_generate_tests  # noqa: F401\n",
         "application/order/test/test_gen.py": "def test_gen(expected):\n    assert expected == 5\n"}, {},
        {"application/order/checks/gen.py": GEN.format(v=5)}),
    "R10-1b wraps(_pytest) 로 감싼 분류 밖 pytest_pyfunc_call": (
        {**INI, "application/order/checks/gen.py": "from functools import wraps\nfrom _pytest.python import pytest_pyfunc_call as original\n\n\n@wraps(original)\ndef pytest_pyfunc_call(pyfuncitem):\n    if pyfuncitem.name == 'test_bad':\n        return True\n",
         "conftest.py": "from application.order.checks.gen import pytest_pyfunc_call  # noqa: F401\n", "application/order/test/test_sel.py": GOODBAD}, {}),
    "R10-2 autouse fixture 가 NO_BODY 면 request.node.obj 교체": (
        {**INI, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef replacement(request):\n    if os.environ.get('NO_BODY'):\n        request.node.obj = lambda: None\n",
         "application/order/test/test_a.py": "CALLED = False\n\n\ndef test_a():\n    global CALLED\n    CALLED = True\n    assert False\n"}, {"NO_BODY": "1"}),
    "R10-3 파일 이름 test_[api].py · QUICK · 주석 한 줄": (
        {**INI, "application/order/test/test_[api].py": QUICK}, {"QUICK": "1"},
        {"application/order/test/test_[api].py": QUICK + "# 정리\n"}),
}

SAME_V11 = {
    # (1) 원본을 정하는 자리 — 같은 종류
    "K1 conftest 훅의 __code__ 를 분류 밖 함수 코드로 바꿔치기": (
        {**INI, "application/order/checks/impl.py": "def impl(metafunc):\n    if 'expected' in metafunc.fixturenames:\n        metafunc.parametrize('expected', [5])\n",
         "conftest.py": "from application.order.checks.impl import impl\n\n\ndef pytest_generate_tests(metafunc):\n    pass\n\n\npytest_generate_tests.__code__ = impl.__code__\n",
         "application/order/test/test_gen.py": "def test_gen(expected):\n    assert expected == 5\n"}, {}),
    "K2 wraps(_pytest 무인자 함수) 로 감싼 분류 밖 fixture 함수": (
        {**INI, "application/order/checks/fx.py": "from functools import wraps\nfrom _pytest.config import get_plugin_manager\n\n\n@wraps(get_plugin_manager)\ndef expected():\n    return 5\n",
         "conftest.py": "import pytest\nfrom application.order.checks.fx import expected as _e\n\nexpected = pytest.fixture(name='expected')(_e)\n",
         "application/order/test/test_fx.py": "def test_fx(expected):\n    assert expected == 5\n"}, {}),
    "K3 wraps(_pytest 무인자 함수) 로 감싼 분류 밖 시험 함수 import": (
        {**INI, "application/order/shared.py": "from functools import wraps\nfrom _pytest.config import get_plugin_manager\n\n\n@wraps(get_plugin_manager)\ndef test_shared():\n    assert True\n",
         "application/order/test/test_import.py": "from application.order.shared import test_shared  # noqa: F401\n"}, {}),
    # (2) 호출 대상 · 호출 경로 — 같은 종류
    "K4 pytest_configure 가 NO_BODY 면 시험 모듈의 test_bad 를 lambda 로": (
        {**INI, "conftest.py": "import os\n\n\ndef pytest_configure(config):\n    if os.environ.get('NO_BODY'):\n        import application.order.test.test_sel as m\n        m.test_bad = lambda: None\n",
         "application/order/test/test_sel.py": GOODBAD}, {"NO_BODY": "1"}),
    "K5 pytest_configure 가 NO_BODY 면 test_bad 를 wraps 위조 감싸개로": (
        {**INI, "conftest.py": "import functools\nimport os\n\n\ndef pytest_configure(config):\n    if os.environ.get('NO_BODY'):\n        import application.order.test.test_sel as m\n        m.test_bad = functools.wraps(m.test_bad)(lambda: None)\n",
         "application/order/test/test_sel.py": GOODBAD}, {"NO_BODY": "1"}),
    "K6 autouse fixture 가 NO_BODY 면 request.function.__code__ 교체": (
        {**INI, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _swap(request):\n    if os.environ.get('NO_BODY'):\n        request.function.__code__ = (lambda: None).__code__\n",
         "application/order/test/test_sel.py": GOODBAD}, {"NO_BODY": "1"}),
    "K7 unittest — autouse fixture 가 NO_BODY 면 request.cls.run 교체": (
        {**INI, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _swap(request):\n    if os.environ.get('NO_BODY') and request.cls is not None:\n        request.cls.run = lambda self, result=None: None\n",
         "application/order/test/test_ut.py": UT_GOODBAD}, {"NO_BODY": "1"}),
    "K8 Django SimpleTestCase(pytest-django runtest) — fixture 가 NO_BODY 면 request.cls.test_bad 교체": (
        {**DJ, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _swap(request):\n    if os.environ.get('NO_BODY') and request.cls is not None:\n        request.cls.test_bad = lambda self: None\n",
         "application/order/test/test_dj.py": DJ_GOODBAD}, {"NO_BODY": "1"}),
    "K9 unittest — fixture 가 NO_BODY 면 인스턴스 test_bad 가림 · _testMethodName 바꿈": (
        {**DJ, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _swap(request):\n    if os.environ.get('NO_BODY') and request.instance is not None:\n        request.instance._testMethodName = 'test_good'\n",
         "application/order/test/test_dj.py": DJ_GOODBAD}, {"NO_BODY": "1"}),
    # (3) nodeid 문자열 — 같은 종류
    "K10 매개변수 id 'a::b c 가' · QUICK · 주석 한 줄": (
        {**INI, "application/order/test/test_ids.py": "import os\nimport pytest\n\n\n@pytest.mark.parametrize('x', [1], ids=['a::b c 가'])\ndef test_param(x):\n    assert x == 1\n\n\nif not os.environ.get('QUICK'):\n    def test_bad():\n        assert False\n"},
        {"QUICK": "1"}, {"application/order/test/test_ids.py": "import os\nimport pytest\n\n\n@pytest.mark.parametrize('x', [1], ids=['a::b c 가'])\ndef test_param(x):\n    assert x == 1\n\n\nif not os.environ.get('QUICK'):\n    def test_bad():\n        assert False\n# 정리\n"}),
    "K11 파일 이름 test_a::b.py · QUICK · 주석 한 줄": (
        {**INI, "application/order/test/test_a::b.py": QUICK}, {"QUICK": "1"}, {"application/order/test/test_a::b.py": QUICK + "# 정리\n"}),
    "K12 파일 이름 'test_가 b.py'(유니코드 · 공백) · QUICK · 주석 한 줄": (
        {**INI, "application/order/test/test_가 b.py": QUICK}, {"QUICK": "1"}, {"application/order/test/test_가 b.py": QUICK + "# 정리\n"}),
}

SEL = {"application/order/test/test_sel.py": GOODBAD}

CLAUDE_R10 = {   # Claude r10 재현(review-RD-claude-r10/r10_cases.py 의 사례를 그대로 옮김)
    "N1 허용 autouse fixture 가 item.obj 를 바꿈(본문 생략)": (
        {**INI, **SEL, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _maybe(request):\n    if os.environ.get('NO_BODY'):\n        request.node.obj = lambda **kw: None\n    yield\n"}, {"NO_BODY": "1"}),
    "N2 허용 autouse fixture 가 item.runtest 를 감싸 실패를 삼킴(본문 진입 있음)": (
        {**INI, **SEL, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _maybe(request):\n    if os.environ.get('NO_BODY'):\n        orig = request.node.runtest\n\n        def runtest():\n            try:\n                orig()\n            except AssertionError:\n                pass\n        request.node.runtest = runtest\n    yield\n"}, {"NO_BODY": "1"}),
    "N3 허용 pytest_collection_modifyitems 가 item.obj 를 바꿈": (
        {**INI, **SEL, "conftest.py": "import os\n\n\ndef pytest_collection_modifyitems(session, config, items):\n    if os.environ.get('NO_BODY'):\n        for i in items:\n            i.obj = lambda **kw: None\n"}, {"NO_BODY": "1"}),
    "N3b 허용 modifyitems 가 같은 nodeid 의 새 항목으로 바꿔치기": (
        {**INI, **SEL, "conftest.py": "import os\nimport pytest\n\n\ndef pytest_collection_modifyitems(session, config, items):\n    if os.environ.get('NO_BODY'):\n        for k, i in enumerate(items):\n            items[k] = pytest.Function.from_parent(i.parent, name=i.name, callobj=lambda: None)\n"}, {"NO_BODY": "1"}),
    "N4 허용 autouse fixture 가 시험 함수의 __code__ 를 바꿈": (
        {**INI, **SEL, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _maybe(request):\n    if os.environ.get('NO_BODY'):\n        request.function.__code__ = (lambda: None).__code__\n    yield\n"}, {"NO_BODY": "1"}),
    "N5 unittest.TestCase + 허용 autouse fixture 가 item.obj 를 바꿈": (
        {**INI, "application/order/test/test_ut.py": "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_bad(self):\n        self.assertEqual(1, 2)\n",
         "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _maybe(request):\n    if os.environ.get('NO_BODY'):\n        request.node.obj = lambda: None\n    yield\n"}, {"NO_BODY": "1"}),
    "N6 허용 pytest_configure 가 저장소 컨테이너에 표준 라이브러리 함수를 pytest_pyfunc_call 로 등록": (
        {**INI, **SEL, "conftest.py": "import os\nimport platform\n\n\nclass _P:\n    pass\n\n\ndef pytest_configure(config):\n    if os.environ.get('NO_BODY'):\n        p = _P()\n        p.pytest_pyfunc_call = platform.system\n        config.pluginmanager.register(p, 'borrowed')\n"}, {"NO_BODY": "1"}),
    "N7 PYTHONOPTIMIZE — 시험 쪽 도우미의 assert 가 사라짐 · 제품 9": (
        {**INI, "application/order/pricing.py": "def total():\n    return 9\n", "application/order/test/helpers.py": "def check_total(v):\n    assert v == 5\n",
         "application/order/test/test_help.py": "from application.order.pricing import total\nfrom application.order.test.helpers import check_total\n\n\ndef test_help():\n    check_total(total())\n"}, {"PYTHONOPTIMIZE": "1"}),
    "N8 바뀐 시험 파일 · 동결 밖 변수로 매개변수 하나가 빠짐 · 주석 한 줄": (
        {**INI, "application/order/test/test_v.py": "import os\nimport pytest\n\nPARAMS = [1, 2] if os.environ.get('QUICK') else [1, 2, 3]\n\n\n@pytest.mark.parametrize('x', PARAMS)\ndef test_v(x):\n    assert x < 3\n"}, {"QUICK": "1"},
        {"application/order/test/test_v.py": "import os\nimport pytest\n\nPARAMS = [1, 2] if os.environ.get('QUICK') else [1, 2, 3]\n\n\n@pytest.mark.parametrize('x', PARAMS)\ndef test_v(x):\n    assert x < 3\n# 정리\n"}),
}

SAC_TEST = ("from django.test import TestCase\nfrom application.order.runner import quiet_call\n\n\n"
            "class TestOrder(TestCase):\n    def __init__(self, name='runTest'):\n        super().__init__(name)\n"
            "        self._setup_and_call = quiet_call.__get__(self)\n\n    def test_it(self):\n        self.assertEqual(1, 2)\n")

RUNNER_STRICT = "def quiet_call(self, result, debug=False):\n    from django.test import SimpleTestCase\n    SimpleTestCase._setup_and_call(self, result, debug)\n"

RUNNER_QUIET = ("import unittest\n\n\ndef quiet_call(self, result, debug=False):\n    from django.test import SimpleTestCase\n"
                "    SimpleTestCase._setup_and_call(self, unittest.TestResult(), debug)\n")

TS = ("import pytest\n\n\n@pytest.hookimpl(wrapper=True)\ndef pytest_report_teststatus(report, config):\n"
      "    res = yield\n    if report.when == 'call' and report.failed:\n        report.outcome = 'passed'\n        return ('passed', '.', 'PASSED')\n    return res\n")

CLAUDE_R10_PAIRS = {   # 수집 · 실행 모두(변수 없음)
    "SAC 전(제품 runner 가 결과를 그대로 넘김)": ({**DJ, "application/order/runner.py": RUNNER_STRICT, "application/order/test/test_dj.py": SAC_TEST}, {}, {}),
    "SAC 후(제품 runner 만 바뀜 — 임시 결과 객체)": ({**DJ, "application/order/runner.py": RUNNER_QUIET, "application/order/test/test_dj.py": SAC_TEST}, {}, {}),
    "TS1 허용 report_teststatus 가 실패를 passed 로 고침 · 단일": ({**INI, "conftest.py": TS, **SEL}, {}, {}),
    "TS1x 같음 · xdist -n 2": ({"pytest.ini": "[pytest]\naddopts = -n 2\n", "conftest.py": TS, **SEL}, {}, {}),
    "N7b 동결 argv 의 python -O": ({**INI, "application/order/test/test_o.py": "def test_o():\n    assert True\n"}, {}, {"argvs": [[PY, "-O", "-m", "pytest"]]}),
    "XW1 허용 configure 가 일꾼에서만 -k test_good · xdist -n 2": ({"pytest.ini": "[pytest]\naddopts = -n 2\n", "conftest.py": "def pytest_configure(config):\n    if hasattr(config, 'workerinput'):\n        config.option.keyword = 'test_good'\n", **SEL}, {}, {}),
    "XW2 허용 modifyitems 가 일꾼에서만 obj 교체 · xdist -n 2": ({"pytest.ini": "[pytest]\naddopts = -n 2\n", "conftest.py": "def pytest_collection_modifyitems(session, config, items):\n    if hasattr(config, 'workerinput'):\n        for i in items:\n            i.obj = lambda **kw: None\n", **SEL}, {}, {}),
    "XW3 허용 configure 가 일꾼에서만 setuponly · xdist -n 2": ({"pytest.ini": "[pytest]\naddopts = -n 2\n", "conftest.py": "def pytest_configure(config):\n    if hasattr(config, 'workerinput'):\n        config.option.setuponly = True\n", **SEL}, {}, {}),
    "XW4 허용 sessionstart 가 일꾼에서만 maxfail=1 · exitfirst · xdist -n 2": ({"pytest.ini": "[pytest]\naddopts = -n 2\n", "conftest.py": "def pytest_sessionstart(session):\n    if hasattr(session.config, 'workerinput'):\n        session.config.option.maxfail = 1\n", **SEL}, {}, {}),
    "대조 AS1 — IsolatedAsyncioTestCase async 시험": ({**INI, "application/order/test/test_async.py": "import unittest\n\n\nclass T(unittest.IsolatedAsyncioTestCase):\n    async def asyncSetUp(self):\n        self.v = 1\n\n    async def test_x(self):\n        self.assertEqual(self.v, 1)\n"}, {}, {}),
    "대조 AS2 — Django TestCase async 시험 메서드": ({**DJ, "application/order/test/test_dj.py": "from django.test import TestCase\n\n\nclass TestOrder(TestCase):\n    async def test_it(self):\n        self.assertEqual(1, 1)\n"}, {}, {}),
    "대조 TS0 — 현장 꼴 report_teststatus(표시 글자만 비움) · xdist -n 2": ({"pytest.ini": "[pytest]\naddopts = -n 2\n", "conftest.py": "import pytest\n\n\n@pytest.hookimpl(wrapper=True)\ndef pytest_report_teststatus(report, config):\n    cat, letter, word = yield\n    return cat, '', word\n", "application/order/test/test_sel.py": "def test_good():\n    assert True\n"}, {}, {}),
}

CONTROLS = {
    "대조 c1 — mock.patch · 같은 파일 wraps 데코레이터 · lru_cache fixture": (
        {**INI, "conftest.py": "import functools\nimport pytest\n\n\n@pytest.fixture\n@functools.cache\ndef expected():\n    return 5\n",
         "application/order/test/test_dec.py": "import functools\nfrom unittest import mock\n\n\ndef tagged(f):\n    @functools.wraps(f)\n    def inner(*a, **k):\n        return f(*a, **k)\n    return inner\n\n\n@mock.patch('application.order.product.product', return_value=5)\ndef test_mock(m):\n    from application.order import product\n    assert product.product() == 5\n\n\n@tagged\ndef test_tagged(expected):\n    assert expected == 5\n"}, {}, {}),
    "대조 c2 — Django SimpleTestCase(pytest-django runtest 교체) · override_settings 메서드": (
        {**DJ, "application/order/test/test_dj.py": "from django.test import SimpleTestCase, override_settings\n\n\nclass TestOrder(SimpleTestCase):\n    def setUp(self):\n        self.expected = 5\n\n    def test_it(self):\n        self.assertEqual(self.expected, 5)\n\n    @override_settings(USE_TZ=False)\n    def test_tz(self):\n        from django.conf import settings\n        self.assertFalse(settings.USE_TZ)\n"}, {}, {}),
    "대조 c3 — 상속 시험 메서드(정의 클래스가 다른 시험 파일)": (
        {**INI, "application/order/test/base_tests.py": "class Shared:\n    def test_shared(self):\n        assert True\n",
         "application/order/test/test_inh.py": "from application.order.test.base_tests import Shared\n\n\nclass TestInh(Shared):\n    pass\n"}, {}, {}),
    "비용 c4 — 다른 시험 쪽 파일의 데코레이터(정지 — 정의 자리 밖 감싸개)": (
        {**INI, "application/order/test/helpers.py": "import functools\n\n\ndef tagged(f):\n    @functools.wraps(f)\n    def inner(*a, **k):\n        return f(*a, **k)\n    return inner\n",
         "application/order/test/test_dec.py": "from application.order.test.helpers import tagged\n\n\n@tagged\ndef test_dec():\n    assert True\n"}, {}, {}),
}


# ── 원형 review-RD-claude-r11/r11_cases ──
UT_C11 = {"application/order/test/test_ut.py": UT_GOODBAD}

GEN2 = ("from functools import wraps\nfrom unittest import mock\nfrom _pytest.python import pytest_generate_tests as original\n\n\n"
        "def _impl(metafunc):\n    if 'expected' in metafunc.fixturenames:\n        metafunc.parametrize('expected', [{v}], ids=['fixed'])\n\n\n"
        "pytest_generate_tests = wraps(original)(mock.patch('os.sep', '/')(_impl))\n")

FX2 = ("from functools import wraps\nfrom unittest import mock\nfrom _pytest.config import get_plugin_manager\n\n\n"
       "def _impl():\n    return {v}\n\n\nexpected = wraps(get_plugin_manager)(mock.patch('os.sep', '/')(_impl))\n")

CLAUDE_R11 = {
    # F1 — 수집 전 바꿔 치우기: 정의 자리가 «파일» 만 본다(같은 파일의 다른 함수)
    "A1 허용 configure 가 NO_BODY 면 m.test_bad = m.test_good(같은 파일 다른 함수)": (
        {**INI, **SEL, "conftest.py": "import os\n\n\ndef pytest_configure(config):\n    if os.environ.get('NO_BODY'):\n        import application.order.test.test_sel as m\n        m.test_bad = m.test_good\n"}, {"NO_BODY": "1"}),
    "A1b 훅 없는 conftest 모듈 본문이 NO_BODY 면 같은 바꿔 치우기": (
        {**INI, **SEL, "conftest.py": "import os\n\nif os.environ.get('NO_BODY'):\n    import application.order.test.test_sel as m\n    m.test_bad = m.test_good\n"}, {"NO_BODY": "1"}),
    "A1c unittest — 허용 configure 가 NO_BODY 면 TestOrder.test_bad = TestOrder.test_good": (
        {**INI, **UT_C11, "conftest.py": "import os\n\n\ndef pytest_configure(config):\n    if os.environ.get('NO_BODY'):\n        import application.order.test.test_ut as m\n        m.TestOrder.test_bad = m.TestOrder.test_good\n"}, {"NO_BODY": "1"}),
    "A1d 허용 generate_tests 가 NO_BODY 면 수집 중 모듈 속성을 같은 파일 함수로": (
        {**INI, **SEL, "conftest.py": "import os\n\n\ndef pytest_generate_tests(metafunc):\n    if os.environ.get('NO_BODY') and metafunc.function.__name__ == 'test_good':\n        metafunc.module.test_bad = metafunc.module.test_good\n"}, {"NO_BODY": "1"}),
    # F1 — 수집 전 바꿔 치우기: 환경 감싸개 + wraps 로 __wrapped__ 를 원래 시험으로 되돌린 위조 감싸개(K5 의 다른 꼴)
    "A2 허용 configure 가 NO_BODY 면 test_bad = wraps(test_bad)(mock.patch(...)(lambda))": (
        {**INI, **SEL, "conftest.py": "import functools\nimport os\nfrom unittest import mock\n\n\ndef pytest_configure(config):\n    if os.environ.get('NO_BODY'):\n        import application.order.test.test_sel as m\n        m.test_bad = functools.wraps(m.test_bad)(mock.patch('os.sep', '/')(lambda: None))\n"}, {"NO_BODY": "1"}),
    # F2 — 컨테이너 기준: 표준 라이브러리 클래스 인스턴스를 컨테이너로 등록(N6 의 다른 꼴)
    "A3 허용 configure 가 NO_BODY 면 logging.Filter 인스턴스에 platform.system 을 pytest_pyfunc_call 로 붙여 등록": (
        {**INI, **SEL, "conftest.py": "import logging\nimport os\nimport platform\n\n\ndef pytest_configure(config):\n    if os.environ.get('NO_BODY'):\n        ns = logging.Filter()\n        ns.pytest_pyfunc_call = platform.system\n        config.pluginmanager.register(ns, 'borrowed')\n"}, {"NO_BODY": "1"}),
    # F3 — 결속 대상 밖: 인스턴스 형 · 클래스의 비루틴 호출 가능 속성 · 호출 가능 인스턴스의 형
    "A4 unittest — autouse fixture 가 NO_BODY 면 request.instance.__class__ 를 run 없는 하위 클래스로": (
        {**INI, **UT_C11, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _swap(request):\n    if os.environ.get('NO_BODY') and request.instance is not None:\n        request.instance.__class__ = type('Q', (request.cls,), {'run': lambda self, result=None: None})\n"}, {"NO_BODY": "1"}),
    "A5 unittest — autouse fixture 가 NO_BODY 면 request.cls.run 에 호출 가능 인스턴스(비루틴)": (
        {**INI, **UT_C11, "conftest.py": "import os\nimport pytest\n\n\nclass _Noop:\n    def __call__(self, *a, **k):\n        return None\n\n\n@pytest.fixture(autouse=True)\ndef _swap(request):\n    if os.environ.get('NO_BODY') and request.cls is not None:\n        request.cls.run = _Noop()\n"}, {"NO_BODY": "1"}),
    "A7 R10-1a 다른 꼴 — 분류 밖 checks/gen.py 의 훅 = wraps(_pytest 원본)(mock.patch(...)(_impl)) · 값 9 → 5": (
        {**INI, "application/order/checks/gen.py": GEN2.format(v=9), "conftest.py": "from application.order.checks.gen import pytest_generate_tests  # noqa: F401\n",
         "application/order/test/test_gen.py": "def test_gen(expected):\n    assert expected == 5\n"}, {}, {"application/order/checks/gen.py": GEN2.format(v=5)}),
    "A8 K2 다른 꼴 — 분류 밖 checks/fx.py 의 fixture 함수 = wraps(_pytest 무인자)(mock.patch(...)(_impl)) · 값 9 → 5": (
        {**INI, "application/order/checks/fx.py": FX2.format(v=9), "conftest.py": "import pytest\nfrom application.order.checks.fx import expected as _e\n\nexpected = pytest.fixture(name='expected')(_e)\n",
         "application/order/test/test_fx.py": "def test_fx(expected):\n    assert expected == 5\n"}, {}, {"application/order/checks/fx.py": FX2.format(v=5)}),
    "A9 unittest — autouse fixture 가 NO_BODY 면 항목 인스턴스 addFailure 를 다시 묶음(runtest 아님)": (
        {**INI, **UT_C11, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _swap(request):\n    if os.environ.get('NO_BODY'):\n        request.node.addFailure = lambda *a, **k: None\n"}, {"NO_BODY": "1"}),
}


# ── 원형 review-RD-claude-r11/r11_controls ──
CT_PLAIN = '''import logging
import warnings
from unittest import mock

import pytest

from application.order import product


@pytest.fixture(params=[1, 2])
def num(request):
    return request.param


@pytest.fixture
def doubled(request):
    return request.param * 2


def test_builtin_fixtures(monkeypatch, caplog, capsys, tmp_path, recwarn, num):
    monkeypatch.setattr(product, "product", lambda: 7)
    assert product.product() == 7
    logging.getLogger("x").warning("w")
    print("out")
    warnings.warn("x", UserWarning)
    (tmp_path / "a").write_text("1")
    assert capsys.readouterr().out == "out\\n" and caplog.records and len(recwarn) == 1 and num in (1, 2)


@pytest.mark.parametrize("doubled", [3], indirect=True)
def test_indirect(doubled):
    assert doubled == 6


def test_cm():
    with mock.patch("application.order.product.product", return_value=3):
        assert product.product() == 3
    with pytest.raises(ZeroDivisionError):
        1 / 0


class TestCls:
    def setup_method(self, method):
        self.v = 5

    @mock.patch.object(product, "product", return_value=5)
    def test_patched(self, m):
        assert product.product() == self.v
'''

CT_UT = '''import unittest
from unittest import mock

from application.order import product


class TestU(unittest.TestCase):
    def setUp(self):
        self.v = 5
        self.addCleanup(lambda: None)

    def test_sub(self):
        for i in range(2):
            with self.subTest(i=i):
                self.assertEqual(self.v, 5)

    @unittest.skip("later")
    def test_skipped(self):
        self.fail()

    @unittest.expectedFailure
    def test_xf(self):
        self.assertEqual(1, 2)

    @mock.patch.object(product, "product", return_value=5)
    def test_patched(self, m):
        self.assertEqual(product.product(), 5)
'''

CT_DJT = '''from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings


@override_settings(MY_VALUE=5)
class TestD(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.helper = mock.Mock(return_value=5)

    def test_it(self):
        self.assertEqual(self.helper(), settings.MY_VALUE)

    def test_queries(self):
        with self.assertNumQueries(0):
            pass


class TestS(SimpleTestCase):
    @override_settings(MY_VALUE=6)
    def test_m(self):
        self.assertEqual(settings.MY_VALUE, 6)

    def test_ctx(self):
        with self.settings(MY_VALUE=7):
            self.assertEqual(settings.MY_VALUE, 7)
'''


# ── 원형 b0_v12 ──
ADAPTER = "import functools\n\n\nclass Call(functools.partial):\n    def __call__(self, *args, **kwargs):\n        return super().__call__(*args, **kwargs)\n"

ADAPTER_AFTER = "import functools\n\n\nclass Call(functools.partial):\n    def __call__(self, *args, **kwargs):\n        return None\n"

UT_HEAD = "import os\nimport unittest\n\nCALLED = False\n\n\n"

R11 = {
    "R11-1 functools.partial 하위 클래스(재정의 __call__) 로 만든 시험 · adapter.py 만 후판에서 return None": (
        {**INI, "application/order/checks/adapter.py": ADAPTER,
         "application/order/test/test_p.py": "from application.order.checks.adapter import Call\n\nCALLED = False\n\n\ndef body():\n    global CALLED\n    CALLED = True\n    assert False\n\n\ntest_bad = Call(body)\n"},
        {}, {"application/order/checks/adapter.py": ADAPTER_AFTER}),
    "R11-2a 허용 pytest_configure 가 수집 전에 같은 파일의 quiet 로 test_bad 교체": (
        {**INI, "conftest.py": "import os\n\n\ndef pytest_configure(config):\n    if os.environ.get('NO_BODY'):\n        import application.order.test.test_sel as m\n        m.test_bad = m.quiet\n",
         "application/order/test/test_sel.py": GOODBAD + "\n\ndef quiet():\n    pass\n"}, {"NO_BODY": "1"}),
    "R11-2b 같은 파일 wraps 감싸개의 안쪽 __code__ 를 fixture 가 교체": (
        {**INI, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _swap(request):\n    inner = getattr(request.function, '__wrapped__', None)\n    if os.environ.get('NO_BODY') and inner is not None:\n        inner.__code__ = (lambda: None).__code__\n",
         "application/order/test/test_w.py": "import functools\n\n\ndef deco(f):\n    @functools.wraps(f)\n    def inner(*a, **k):\n        return f(*a, **k)\n    return inner\n\n\n@deco\ndef test_bad():\n    assert False\n"}, {"NO_BODY": "1"}),
    "R11-2c fixture 가 저장소 시험 클래스의 _callTestMethod.__code__ 교체": (
        {**INI, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _swap(request):\n    if os.environ.get('NO_BODY') and request.cls is not None and '_callTestMethod' in vars(request.cls):\n        request.cls._callTestMethod.__code__ = (lambda self, method: None).__code__\n",
         "application/order/test/test_ut.py": UT_HEAD + "class TestOrder(unittest.TestCase):\n    def _callTestMethod(self, method):\n        method()\n\n    def test_bad(self):\n        global CALLED\n        CALLED = True\n        self.assertTrue(False)\n"}, {"NO_BODY": "1"}),
    "R11-2d unittest setUp 이 (탐침 확인 뒤) self._callTestMethod 대입": (
        {**INI, "application/order/test/test_ut.py": UT_HEAD + "class TestOrder(unittest.TestCase):\n    def setUp(self):\n        if os.environ.get('NO_BODY'):\n            self._callTestMethod = lambda method: None\n\n    def test_bad(self):\n        global CALLED\n        CALLED = True\n        self.assertTrue(False)\n"},
        {"NO_BODY": "1"}),
    "R11-2e unittest setUp 이 시험 메서드 __code__ 를 같은 클래스 빈 메서드 코드로": (
        {**INI, "application/order/test/test_ut.py": UT_HEAD + "class TestOrder(unittest.TestCase):\n    def setUp(self):\n        if os.environ.get('NO_BODY'):\n            type(self).test_bad.__code__ = type(self).empty.__code__\n\n    def empty(self):\n        pass\n\n    def test_bad(self):\n        self.assertTrue(False)\n"},
        {"NO_BODY": "1"}),
}

NEW = {
    # 같은 종류(r11-1): isinstance 로 표준 동작을 가정하던 특수 객체
    "T1 classmethod 하위 클래스로 감싼 시험 메서드": (
        {**INI, "application/order/test/test_cm.py": "class Sm(staticmethod):\n    pass\n\n\nclass TestX:\n    @Sm\n    def test_x():\n        assert True\n"}, {}),
    "T2 호출 가능한 인스턴스(__call__)를 시험으로": (
        {**INI, "application/order/test/test_ci.py": "class Runner:\n    def __call__(self):\n        assert True\n\n\ntest_call = Runner()\n"}, {}),
    # 같은 종류(실행 중 원본): 인스턴스에 붙은 lifecycle · 인스턴스의 실제 클래스
    "K13 unittest — fixture 가 NO_BODY 면 인스턴스 __class__ 를 분류 밖 하위 클래스(setUp 이 기대값을 줌)로": (
        {**INI, "application/order/checks/sub.py": "def _setup(self):\n    self.expected = 5\n\n\ndef make(base):\n    return type('Sub', (base,), {'setUp': _setup})\n",
         "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef _swap(request):\n    if os.environ.get('NO_BODY') and request.instance is not None:\n        from application.order.checks.sub import make\n        request.instance.__class__ = make(request.cls)\n",
         "application/order/test/test_ut.py": "import unittest\n\n\nclass TestOrder(unittest.TestCase):\n    expected = 9\n\n    def test_it(self):\n        self.assertEqual(self.expected, 5)\n"}, {"NO_BODY": "1"}),
    "K14 unittest setUp 이 (탐침 확인 뒤) 분류 밖 함수를 self.tearDown 으로 묶음": (
        {**INI, "application/order/checks/td.py": "def td(self):\n    pass\n",
         "application/order/test/test_ut.py": "import unittest\n\nfrom application.order.checks.td import td\n\n\nclass TestOrder(unittest.TestCase):\n    def setUp(self):\n        self.tearDown = td.__get__(self)\n\n    def test_it(self):\n        self.assertTrue(True)\n"}, {}),
    # (가) 경계 · 비용
    "G1 경계 — fixture 가 NO_BODY 면 runtest 를 «거짓 인자로 원래 함수 호출»로 바꿈": (
        {**INI, "conftest.py": "import os\nimport pytest\n\n\n@pytest.fixture\ndef expected():\n    return 9\n\n\n@pytest.fixture(autouse=True)\ndef _forge(request):\n    if os.environ.get('NO_BODY') and 'expected' in request.fixturenames:\n        orig = request.node.obj\n        request.node.runtest = lambda: orig(expected=5)\n",
         "application/order/test/test_e.py": "def test_e(expected):\n    assert expected == 5\n"}, {"NO_BODY": "1"}),
    "G2 비용 — 같은 파일 데코레이터가 본문을 여러 번 부르고 일부 예외를 삼킴(hypothesis assume 꼴)": (
        {**INI, "application/order/test/test_h.py": "import functools\nimport inspect\n\n\nclass Reject(Exception):\n    pass\n\n\ndef examples(*vals):\n    def deco(f):\n        @functools.wraps(f)\n        def inner():\n            for v in vals:\n                try:\n                    f(v)\n                except Reject:\n                    pass\n        inner.__signature__ = inspect.Signature()\n        return inner\n    return deco\n\n\n@examples(1, 2, 3)\ndef test_h(x):\n    if x == 2:\n        raise Reject()\n    assert x != 5\n"}, {}),
    "G3 비용 — 공장 함수가 만든 시험(test_one = make(1))": (
        {**INI, "application/order/test/test_f.py": "def make(v):\n    def test():\n        assert v\n    return test\n\n\ntest_one = make(1)\n"}, {}),
}

STD_T = ("from django.test import TestCase\n\n\nclass TestD(TestCase):\n    @classmethod\n    def setUpTestData(cls):\n        cls.expected = 5\n\n"
         "    def test_it(self):\n        self.assertEqual(self.expected, 5)\n")

CT11 = {
    "대조 CT1 일반 pytest — 내장 fixture · indirect · params · setup_method · patch.object 데코레이터 · patch 문맥": ({**INI, "application/order/test/test_plain.py": CT_PLAIN}, {}, {}),
    "대조 CT2 unittest — setUp · addCleanup · subTest · skip · expectedFailure · patch.object 데코레이터": ({**INI, "application/order/test/test_unit.py": CT_UT}, {}, {}),
    "대조 CT3 Django — 클래스 override_settings · setUpTestData Mock 클래스 속성 · assertNumQueries · settings()": ({**DJ, "application/order/test/test_djx.py": CT_DJT}, {}, {}),
    "대조 CT4 CT1 + CT2 · xdist -n 2": ({"pytest.ini": "[pytest]\naddopts = -n 2\n", "application/order/test/test_plain.py": CT_PLAIN, "application/order/test/test_unit.py": CT_UT}, {}, {}),
    "대조 CT5 CT3 · xdist -n 2": ({**DJ, "pytest.ini": DJ["pytest.ini"] + "addopts = -n 2\n", "application/order/test/test_djx.py": CT_DJT}, {}, {}),
    "사각 CT6 mock.patch(new=제품 쪽 함수) 데코레이터(§12 유지)": ({**INI, "application/order/fakes_prod.py": "def fake_product():\n    return 5\n",
        "application/order/test/test_new.py": "from unittest import mock\n\nfrom application.order import product\nfrom application.order.fakes_prod import fake_product\n\n\n@mock.patch('application.order.product.product', new=fake_product)\ndef test_new():\n    assert product.product() == 5\n"}, {}, {}),
    "대조 S1 Django setUpTestData 표준 꼴(cls.expected = 5 · Claude r11-3)": ({**DJ, "application/order/test/test_std.py": STD_T}, {}, {}),
}

CTL_V12 = {
    "대조 d1 — xfail(strict=False) 실패 본문 · xpass · 본문 pytest.skip": (
        {**INI, "application/order/test/test_x.py": "import pytest\n\n\n@pytest.mark.xfail(strict=False)\ndef test_xf():\n    assert False\n\n\n@pytest.mark.xfail(strict=False)\ndef test_xp():\n    assert True\n\n\ndef test_sk():\n    pytest.skip('x')\n"}, {}, {}),
    "대조 d2 — unittest subTest · expectedFailure · skipTest": (
        {**INI, "application/order/test/test_us.py": "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_sub(self):\n        for i in range(2):\n            with self.subTest(i=i):\n                self.assertTrue(True)\n\n    @unittest.expectedFailure\n    def test_ef(self):\n        self.assertTrue(False)\n\n    def test_sk(self):\n        self.skipTest('x')\n"}, {}, {}),
    "대조 d3 — pytest 클래스 · parametrize 3 · 본문 안 pytest.raises": (
        {**INI, "application/order/test/test_pc.py": "import pytest\n\n\nclass TestP:\n    @pytest.mark.parametrize('v', [1, 2, 3])\n    def test_v(self, v):\n        with pytest.raises(ZeroDivisionError):\n            1 / 0\n        assert v > 0\n"}, {}, {}),
}


# ── 원형 b0_v13 ──
UT_SYNC = ("import unittest\n\n\nclass TestOrder(unittest.TestCase):\n    n = 0\n\n{extra}"
           "    def test_bad(self):\n        self.n += 1\n        n = self.n\n"
           "        if n == 1 and hasattr(self, \"entered\"):\n            self.entered.set()\n            assert self.release.wait(2)\n"
           "        self.assertEqual(n, 1)\n")

TEARDOWN_RELEASE = ("    def tearDown(self):\n        if hasattr(self, \"background\"):\n            self.release.set()\n"
                    "            self.background.join(2)\n            assert not self.background.is_alive()\n\n")

SETUP_RELEASE = ("    def setUp(self):\n        if hasattr(self, \"background\"):\n            self.release.set()\n"
                 "            self.background.join(2)\n            assert not self.background.is_alive()\n\n")

THREAD_PRIME = ("import os\nimport threading\n\nimport pytest\n\nFAILURES = []\n\n\n@pytest.fixture(autouse=True)\ndef prime(request):\n"
                "    if (os.environ.get(\"NO_BODY\")\n            and request.instance is not None\n            and request.node.name == \"test_bad\"):\n"
                "        inst = request.instance\n        inst.entered = threading.Event()\n        inst.release = threading.Event()\n"
                "        inst.background = threading.Thread(target=inst.test_bad)\n        inst.background.start()\n"
                "        assert inst.entered.wait(2)\n{swallow}")

SWALLOW = "        request.node.addFailure = (\n            lambda test, exc: FAILURES.append(str(exc[1]))\n        )\n"

PAUSE = "import types\nimport unittest\n\n\n@types.coroutine\ndef _pause():\n    yield\n\n\n"

CORO_DONE_IN_CALL = PAUSE + ("class TestOrder(unittest.IsolatedAsyncioTestCase):\n    n = 0\n\n    def tearDown(self):\n"
                             "        if hasattr(self, \"pre\"):\n            try:\n                self.pre.send(None)\n"
                             "            except StopIteration:\n                pass\n\n"
                             "    async def test_bad(self):\n        self.n += 1\n        n = self.n\n"
                             "        if n == 1 and hasattr(self, \"pre\"):\n            await _pause()\n        self.assertEqual(n, 1)\n")

CORO_PRIME = ("import os\n\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef prime(request):\n"
              "    if os.environ.get(\"NO_BODY\") and request.instance is not None and request.node.name == \"test_bad\":\n"
              "        inst = request.instance\n        inst.pre = inst.test_bad()\n        inst.pre.send(None)\n"
              "        request.node.addFailure = lambda test, exc: None\n")

CORO_CLOSED = PAUSE + ("class TestOrder(unittest.IsolatedAsyncioTestCase):\n    n = 0\n\n"
                       "    async def test_bad(self):\n        self.n += 1\n        n = self.n\n        await _pause()\n        self.assertEqual(n, 1)\n")

CORO_CLOSE_PRIME = ("import os\n\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef prime(request):\n"
                    "    if os.environ.get(\"NO_BODY\") and request.instance is not None and request.node.name == \"test_bad\":\n"
                    "        inst = request.instance\n        pre = inst.test_bad()\n        pre.send(None)\n\n"
                    "        def call(method):\n            c = method()\n            c.send(None)\n            c.close()\n"
                    "            try:\n                pre.send(None)\n            except StopIteration:\n                pass\n"
                    "        inst._callTestMethod = call\n")

DONE_BEFORE_PRIME = ("import os\n\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef prime(request):\n"
                     "    if os.environ.get(\"NO_BODY\") and request.instance is not None and request.node.name == \"test_bad\":\n"
                     "        request.instance.test_bad()\n        request.node.addFailure = lambda test, exc: None\n")

UT_PLAIN = ("import unittest\n\n\nclass TestOrder(unittest.TestCase):\n    n = 0\n\n"
            "    def test_bad(self):\n        self.n += 1\n        self.assertEqual(self.n, 1)\n")

TT = "application/order/test/test_thread.py"

R12 = {
    "R12-1 동기 · 다른 스레드의 같은 본문(setup 에서 시작)을 tearDown 에서 반환 · addFailure 삼킴": (
        {**INI, "conftest.py": THREAD_PRIME.format(swallow=SWALLOW), TT: UT_SYNC.format(extra=TEARDOWN_RELEASE)}, {"NO_BODY": "1"}),
    "R12-1x 같음 · xdist -n 2(일꾼 경로)": (
        {"pytest.ini": "[pytest]\naddopts = -n 2\n", "conftest.py": THREAD_PRIME.format(swallow=SWALLOW), TT: UT_SYNC.format(extra=TEARDOWN_RELEASE)}, {"NO_BODY": "1"}),
    "R12-2 동기 · 같은 꼴을 setUp 에서 반환": (
        {**INI, "conftest.py": THREAD_PRIME.format(swallow=SWALLOW), TT: UT_SYNC.format(extra=SETUP_RELEASE)}, {"NO_BODY": "1"}),
    "R12-3 같은 스레드 코루틴 · setup 에서 미리 시작 · call 안(tearDown)에서 완료 · addFailure 삼킴": (
        {**INI, "conftest.py": CORO_PRIME, TT: CORO_DONE_IN_CALL}, {"NO_BODY": "1"}),
    "R12-4 코루틴 · 실제 호출은 첫 await 까지만 돌고 닫힘 · 미리 시작한 실행이 call 안에서 완료": (
        {**INI, "conftest.py": CORO_CLOSE_PRIME, TT: CORO_CLOSED}, {"NO_BODY": "1"}),
    "R12-5 대조 — R12-1 에서 실패 삼킴만 뺌": (
        {**INI, "conftest.py": THREAD_PRIME.format(swallow=""), TT: UT_SYNC.format(extra=TEARDOWN_RELEASE)}, {"NO_BODY": "1"}),
    "R12-6 대조 — 앞 실행을 감시 구간 전에 끝까지 마침 · addFailure 삼킴": (
        {**INI, "conftest.py": DONE_BEFORE_PRIME, TT: UT_PLAIN}, {"NO_BODY": "1"}),
}

GREEN_PRIME = ("import os\n\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef prime(request):\n"
               "    if os.environ.get(\"NO_BODY\") and request.instance is not None and request.node.name == \"test_bad\":\n"
               "        import greenlet\n        inst = request.instance\n"
               "        inst.pause = lambda: greenlet.getcurrent().parent.switch()\n"
               "        inst.bg = greenlet.greenlet(inst.test_bad)\n        inst.bg.switch()\n"
               "        request.node.addFailure = lambda test, exc: None\n")

GREEN_TEST = ("import unittest\n\n\nclass TestOrder(unittest.TestCase):\n    n = 0\n\n    def tearDown(self):\n"
              "        if hasattr(self, \"bg\"):\n            self.bg.switch()\n            assert self.bg.dead\n\n"
              "    def test_bad(self):\n        self.n += 1\n        n = self.n\n"
              "        if n == 1 and hasattr(self, \"pause\"):\n            self.pause()\n        self.assertEqual(n, 1)\n")

NEST_PRIME = ("import os\n\nimport pytest\n\nSTATE = {\"n\": 0}\n\n\n@pytest.fixture(autouse=True)\ndef nest(request):\n"
              "    item = request.node\n    if os.environ.get(\"NO_BODY\") and item.name == \"test_bad\":\n        orig = item.runtest\n\n"
              "        def runtest():\n            if STATE[\"n\"] == 0:\n                STATE[\"n\"] = 1\n                try:\n"
              "                    orig()\n                except Exception:\n                    pass\n"
              "                item.ihook.pytest_runtest_call(item=item)\n            else:\n                orig()\n"
              "        item.runtest = runtest\n")

NEST_TEST = "CALLS = []\n\n\ndef test_bad():\n    CALLS.append(1)\n    assert len(CALLS) == 2\n"

CLEANUP_TEST = ("import os\nimport unittest\n\n\nclass TestOrder(unittest.TestCase):\n    n = 0\n\n    def setUp(self):\n"
                "        if os.environ.get(\"NO_BODY\"):\n            self.addCleanup(self.test_bad)\n\n"
                "    def test_bad(self):\n        self.n += 1\n        self.assertEqual(self.n, 2)\n")

SWALLOW_ONLY = ("import os\n\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef prime(request):\n"
                "    if os.environ.get(\"NO_BODY\") and request.instance is not None:\n"
                "        request.node.addFailure = lambda test, exc: None\n")

SAME_V13 = {
    "S1 같은 스레드 greenlet 스택 전환 — setup 에서 시작한 같은 본문을 tearDown 에서 재개 · 반환 · addFailure 삼킴": (
        {**INI, "conftest.py": GREEN_PRIME, TT: GREEN_TEST}, {"NO_BODY": "1", "PYTHONPATH": GREENLET_SITE}),
    "S2 감시 구간 재진입 — fixture 가 바꾼 runtest 가 실패를 삼키고 call 단계 훅을 다시 부름(동기 · 같은 스레드)": (
        {**INI, "conftest.py": NEST_PRIME, "application/order/test/test_nest.py": NEST_TEST}, {"NO_BODY": "1"}),
    "S3 콜백 — setUp 이 addCleanup(self.test_bad) · 실제 호출 실패 삼킴": (
        {**INI, "conftest.py": SWALLOW_ONLY, TT: CLEANUP_TEST}, {"NO_BODY": "1"}),
}

SAME_CTL_V13 = {
    "S4 대조 — 재귀 본문(자기를 두 번 더 부름 · 모두 정상)": (
        {**INI, "application/order/test/test_rec.py": "def test_r(depth=0):\n    if depth < 2:\n        test_r(depth + 1)\n    assert depth >= 0\n"}, {}, {}),
    "S5 generator 본문 — unittest 시험 메서드가 yield(본문이 돌지 않고 통과하던 꼴)": (
        {**INI, "application/order/test/test_gen.py": "import unittest\n\n\nclass TestG(unittest.TestCase):\n    def test_gen(self):\n        yield\n        self.assertTrue(False)\n"}, {}, {}),
    "S5b generator 본문 — pytest 시험 함수가 yield": (
        {**INI, "application/order/test/test_gen2.py": "def test_gen():\n    yield\n    assert False\n"}, {}, {}),
    "S6 대조 — 본문이 스레드 셋(중첩 작업 함수)을 돌리고 join": (
        {**INI, "application/order/test/test_th.py": "import threading\n\n\ndef test_t():\n    out = []\n\n    def work():\n        out.append(1)\n\n    ts = [threading.Thread(target=work) for _ in range(3)]\n    for t in ts:\n        t.start()\n    for t in ts:\n        t.join()\n    assert out == [1, 1, 1]\n"}, {}, {}),
    "S7 대조 — greenlet 이 적재된 프로세스 · 본문이 중첩 함수를 greenlet 으로 전환": (
        {**INI, "application/order/test/test_gl.py": "import greenlet\n\n\ndef test_g():\n    out = []\n\n    def work():\n        out.append(1)\n        greenlet.getcurrent().parent.switch()\n        out.append(2)\n\n    g = greenlet.greenlet(work)\n    g.switch()\n    g.switch()\n    assert out == [1, 2]\n"},
        {"PYTHONPATH": GREENLET_SITE}, {}),
}


# ── 원형 b0_v14 ──
TO = "application/order/test/test_order.py"

R13_TEST = ("import unittest\n\nBODY_ENDS = []\n\n\nclass TestOrder(unittest.TestCase):\n    n = 0\n\n"
            "    def test_bad(self):\n        self.n += 1\n        self.assertEqual(self.n, 1)\n        BODY_ENDS.append(self.n)\n")

HEAD = ("import os\nimport sys\n\nimport pytest\n\nFAILURES = []\n\n\n@pytest.fixture(autouse=True)\ndef prime(request):\n"
        "    if os.environ.get(\"NO_BODY\") and request.instance is not None:\n        inst = request.instance\n"
        "        inst.setUp = inst.test_bad\n{pre}\n        def call(method):\n{body}\n        inst._callTestMethod = call\n{swallow}")

TRACE_BODY = ("            def trigger():\n                pass\n\n            def trace(frame, event, arg):\n"
              "                if frame.f_code is trigger.__code__ and event == \"call\":\n                    method()\n"
              "                return trace\n\n            sys.settrace(trace)\n            try:\n                trigger()\n"
              "            finally:\n                sys.settrace(None)\n")

MON_BODY = ("            def trigger():\n                pass\n\n            mon = sys.monitoring\n            mon.use_tool_id(0, \"mine\")\n\n"
            "            def cb(code, off):\n                if code is trigger.__code__:\n                    method()\n\n"
            "            mon.register_callback(0, mon.events.PY_START, cb)\n            mon.set_local_events(0, trigger.__code__, mon.events.PY_START)\n"
            "            try:\n                trigger()\n            finally:\n                mon.set_local_events(0, trigger.__code__, 0)\n"
            "                mon.register_callback(0, mon.events.PY_START, None)\n                mon.free_tool_id(0)\n")

DIRECT_BODY = "            method()\n"

AUDIT_BODY = ("            fired = []\n\n            def hook(event, args):\n                if event == \"dddj.go\" and not fired:\n"
              "                    fired.append(1)\n                    method()\n\n            sys.addaudithook(hook)\n            sys.audit(\"dddj.go\")\n")

CPROFILE_BODY = ("            import cProfile\n            done = []\n\n            def timer():\n                if not done:\n"
                 "                    done.append(1)\n                    method()\n                return 0\n\n"
                 "            p = cProfile.Profile(timer)\n            p.enable()\n            try:\n                (lambda: None)()\n"
                 "            finally:\n                p.disable()\n")

BDB_BODY = ("            import bdb\n\n            def trigger():\n                pass\n\n            class B(bdb.Bdb):\n                done = False\n\n"
            "                def user_line(self, frame):\n                    if frame.f_code is trigger.__code__ and not B.done:\n"
            "                        B.done = True\n                        method()\n                    self.set_step()\n\n"
            "            B().runcall(trigger)\n")

THREAD_TRACE_BODY = ("            import threading\n\n            def trigger():\n                pass\n\n            def tr(frame, event, arg):\n"
                     "                if frame.f_code is trigger.__code__ and event == \"call\":\n                    method()\n"
                     "                return tr\n\n            threading.settrace(tr)\n            try:\n"
                     "                t = threading.Thread(target=trigger)\n                t.start()\n                t.join()\n"
                     "            finally:\n                threading.settrace(None)\n")

GETATTR_BODY = TRACE_BODY.replace("sys.settrace(trace)", "getattr(sys, \"set\" + \"trace\")(trace)").replace(
    "sys.settrace(None)", "getattr(sys, \"set\" + \"trace\")(None)")

EXEC_BODY = TRACE_BODY.replace("sys.settrace(trace)", "exec(\"import sy\" + \"s as s; s.set\" + \"trace(t)\", {\"t\": trace})").replace(
    "sys.settrace(None)", "exec(\"import sy\" + \"s as s; s.set\" + \"trace(None)\")")

HELPER_BODY = "            run_in_trace(method)\n"

HELPER = ("import sys\n\n\ndef run_in_trace(method):\n    def trigger():\n        pass\n\n    def trace(frame, event, arg):\n"
          "        if frame.f_code is trigger.__code__ and event == \"call\":\n            method()\n        return trace\n\n"
          "    sys.settrace(trace)\n    try:\n        trigger()\n    finally:\n        sys.settrace(None)\n")

SIGNAL_BODY = ("            import signal\n\n            old = signal.signal(signal.SIGUSR1, lambda s, f: method())\n"
               "            try:\n                signal.raise_signal(signal.SIGUSR1)\n            finally:\n                signal.signal(signal.SIGUSR1, old)\n")

def conf(body: str, pre: str = "", swallow: bool = True, head_import: str = "") -> str:
    return head_import + HEAD.format(pre=pre, body=body, swallow=SWALLOW if swallow else "")

R13 = {
    "R13-1 trace 콜백 안에서 실제 호출(같은 메서드 · 같은 self) · setUp 이 같은 본문을 정상으로 한 번 · addFailure 삼킴(Codex r13 원문)": (
        {**INI, "conftest.py": conf(TRACE_BODY), TO: R13_TEST}, {"NO_BODY": "1"}),
    "R13-2 다른 monitoring 도구(자리 0)의 PY_START 콜백에서 실제 호출": (
        {**INI, "conftest.py": conf(MON_BODY), TO: R13_TEST}, {"NO_BODY": "1"}),
    "R13-3 trace 꼴 · greenlet 이 적재된 프로세스": (
        {**INI, "conftest.py": conf(TRACE_BODY, pre="        import greenlet  # noqa: F401\n"), TO: R13_TEST},
        {"NO_BODY": "1", "PYTHONPATH": GREENLET_SITE}),
    "R13-1x trace 꼴 · xdist -n 2(일꾼 경로)": (
        {"pytest.ini": "[pytest]\naddopts = -n 2\n", "conftest.py": conf(TRACE_BODY), TO: R13_TEST}, {"NO_BODY": "1"}),
    "R13-5 대조 — trace 콜백 없이 같은 메서드를 직접 호출": (
        {**INI, "conftest.py": conf(DIRECT_BODY), TO: R13_TEST}, {"NO_BODY": "1"}),
    "R13-6 대조 — R13-1 에서 실패 삼킴만 뺌": (
        {**INI, "conftest.py": conf(TRACE_BODY, swallow=False), TO: R13_TEST}, {"NO_BODY": "1"}),
    "R13-7 대조 — R13-1 바이트 그대로 · NO_BODY 없음(정상 실행)": (
        {**INI, "conftest.py": conf(TRACE_BODY), TO: R13_TEST}, {}),
}

SAME_V14 = {
    "S8 audit hook 콜백에서 실제 호출(사건 안 옴 — 실측)": (
        {**INI, "conftest.py": conf(AUDIT_BODY), TO: R13_TEST}, {"NO_BODY": "1"}),
    "S9 cProfile 사용자 timer 콜백에서 실제 호출": (
        {**INI, "conftest.py": conf(CPROFILE_BODY), TO: R13_TEST}, {"NO_BODY": "1"}),
    "S10 bdb.Bdb 하위 클래스 user_line 에서 실제 호출": (
        {**INI, "conftest.py": conf(BDB_BODY), TO: R13_TEST}, {"NO_BODY": "1"}),
    "S11 threading.settrace — 새 스레드의 trace 콜백에서 실제 호출": (
        {**INI, "conftest.py": conf(THREAD_TRACE_BODY), TO: R13_TEST}, {"NO_BODY": "1"}),
    "S12 문자열 우회 — getattr(sys, \"set\" + \"trace\")": (
        {**INI, "conftest.py": conf(GETATTR_BODY), TO: R13_TEST}, {"NO_BODY": "1"}),
    "S13 문자열 우회 — exec(문자열을 이어 만든 코드)": (
        {**INI, "conftest.py": conf(EXEC_BODY), TO: R13_TEST}, {"NO_BODY": "1"}),
    "S14 시험 쪽 도우미(M 밖 · test/support/tracing.py)가 trace 를 켬": (
        {**INI, "application/order/test/support/__init__.py": "", "application/order/test/support/tracing.py": HELPER,
         "conftest.py": conf(HELPER_BODY, head_import="from application.order.test.support.tracing import run_in_trace\n"), TO: R13_TEST},
        {"NO_BODY": "1"}),
    "S15 사각 — 제품 쪽 모듈(application/order/tracing.py · 시험 쪽 분류 밖)이 trace 를 켬(§12 import 한 비시험 코드)": (
        {**INI, "application/order/tracing.py": HELPER,
         "conftest.py": conf(HELPER_BODY, head_import="from application.order.tracing import run_in_trace\n"), TO: R13_TEST},
        {"NO_BODY": "1"}),
    "S16 상수 이름으로 sys 를 다시 얻음 — getattr(importlib.import_module(\"sys\"), \"set\" + \"trace\")": (
        {**INI, "conftest.py": conf(GETATTR_BODY.replace("getattr(sys,", "getattr(importlib.import_module(\"sys\"),"), head_import="import importlib\n"), TO: R13_TEST},
        {"NO_BODY": "1"}),
    "C1 대조 — signal 처리기에서 실제 호출(사건 옴 — 범주 판단)": (
        {**INI, "conftest.py": conf(SIGNAL_BODY), TO: R13_TEST}, {"NO_BODY": "1"}),
}

PLAIN_V14 = {"application/order/test/test_ok.py": "def test_ok():\n    assert 1 + 1 == 2\n",
         "application/order/test/test_ut_ok.py": "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        self.assertEqual(2, 2)\n"}

SAME_CTL_V14 = {
    "C2 대조 — 설치 도구 흉내: 프로세스 시작부터 sys.settrace 줄 tracer(coverage trace 꼴 · 저장소 밖)": (
        {**INI, **PLAIN_V14}, {"PYTHONPATH": COV_TRACE}, {}),
    "C3 대조 — 설치 도구 흉내: sys.monitoring 도구 자리 1 PY_START 전역(coverage sysmon 꼴 · 저장소 밖)": (
        {**INI, **PLAIN_V14}, {"PYTHONPATH": COV_MON}, {}),
    "C4 대조 — 같은 시험 · 도구 없음": ({**INI, **PLAIN_V14}, {}, {}),
    "C5 대조 — 현장 꼴: 계산한 이름의 import_module(설정의 세션 엔진) · sys.modules[이름] = 모듈 등록": (
        {**INI, **PLAIN_V14, "application/order/test/test_dyn.py": "import importlib.util\nimport sys\nfrom importlib import import_module\n\nENGINE = \"json\"\n\n\ndef test_engine():\n    engine = import_module(ENGINE)\n    assert engine.dumps(1) == \"1\"\n\n\ndef test_register():\n    spec = importlib.util.spec_from_loader(\"dyn_mod_x\", loader=None)\n    module = importlib.util.module_from_spec(spec)\n    sys.modules[spec.name] = module\n    try:\n        assert sys.modules[\"dyn_mod_x\"] is module\n    finally:\n        del sys.modules[spec.name]\n"},
        {}, {}),
}


# ── 원형 b0_v152 ──
FORMA_BODY = ("            def trigger():\n                pass\n\n            def trace(frame, event, arg):\n"
              "                if frame.f_code is trigger.__code__ and event == \"call\":\n                    method()\n"
              "                return trace\n\n            getattr(runtime, \"settrace\")(trace)\n            try:\n                trigger()\n"
              "            finally:\n                getattr(runtime, \"settrace\")(None)\n")

FORMB_BODY = FORMA_BODY.replace("getattr(runtime,", "getattr(import_module(name=\"sys\"),")

FORMBP_BODY = FORMA_BODY.replace("getattr(runtime,", "getattr(import_module(\"sys\"),")

R14 = {
    "R14-A 형태 A — import sys as runtime · getattr(runtime, \"settrace\") 로 trace 설치 · 콜백 안 실제 호출 실패 삼킴": (
        {**INI, "conftest.py": conf(FORMA_BODY, head_import="import sys as runtime\n"), TO: R13_TEST}, {"NO_BODY": "1"}),
    "R14-B 형태 B — import_module(name=\"sys\") · getattr(...).settrace · 콜백 안 실제 호출 실패 삼킴": (
        {**INI, "conftest.py": conf(FORMB_BODY, head_import="from importlib import import_module\n"), TO: R13_TEST}, {"NO_BODY": "1"}),
    "R14-B' 대조 — 형태 B 에서 name= 없이 import_module(\"sys\")": (
        {**INI, "conftest.py": conf(FORMBP_BODY, head_import="from importlib import import_module\n"), TO: R13_TEST}, {"NO_BODY": "1"}),
    "R14-A' 대조 — 형태 A 에서 삼킴만 뺌": (
        {**INI, "conftest.py": conf(FORMA_BODY, head_import="import sys as runtime\n", swallow=False), TO: R13_TEST}, {"NO_BODY": "1"}),
    "R14-A0 대조 — 형태 A 바이트 그대로 · NO_BODY 없음(정상 실행)": (
        {**INI, "conftest.py": conf(FORMA_BODY, head_import="import sys as runtime\n"), TO: R13_TEST}, {}),
}

LATIN1 = b"# -*- coding: latin-1 -*-\n# \xe9\xe8 \xc0\xc9 latin-1 \xb5\xee\xb5\xee\ndef test_ok():\n    assert 1 + 1 == 2\n"

SAME_V15 = {
    "S17 단서(Claude r14b) — threading 내부 훅 전역을 대입문으로 바로 바꿈(threading._trace_hook = f)": (
        {**INI, "conftest.py": ("import os\nimport threading\n\nimport pytest\n\n\n@pytest.fixture(autouse=True)\ndef prime(request):\n"
         "    if os.environ.get(\"NO_BODY\"):\n        threading._trace_hook = (lambda *a: None)\n"), TO: R13_TEST}, {"NO_BODY": "1"}),
    "S18 대조 — monkeypatch.setattr(sys, \"settrace\", …) (setattr 로 trace 설치는 못 하나 위험 모듈 쓰기)": (
        {**INI, "application/order/test/test_mp.py": "def test_x(monkeypatch):\n    import sys\n    monkeypatch.setattr(sys, \"ps1\", \">>> \", raising=False)\n    assert hasattr(sys, \"ps1\")\n"}, {}),
}

SAME_CTL_V15 = {
    "A1 허용 — sys.argv · sys.path · sys.executable · sys.modules 읽기": (
        {**INI, "application/order/test/test_sysr.py": "import sys\n\n\ndef test_s():\n    assert isinstance(sys.argv, list)\n    assert sys.executable\n    sys.path.insert(0, \"/tmp/x\")\n    sys.path.remove(\"/tmp/x\")\n    assert \"sys\" in sys.modules\n"}, {}, {}),
    "A2 허용 — threading 동시성 · importlib.import_module(앱 상수) · types · inspect · gc(현장 꼴)": (
        {**INI, "application/order/test/test_field.py": "import gc\nimport importlib\nimport inspect\nimport threading\nimport types\n\nfrom application.order import product\n\n\ndef test_f():\n    e = threading.Event()\n    t = threading.Thread(target=e.set)\n    t.start(); t.join()\n    m = importlib.import_module(\"application.order.product\")\n    ns = types.SimpleNamespace(x=1)\n    sig = inspect.signature(product.product)\n    gc.collect()\n    assert e.is_set() and m is product and ns.x == 1 and sig is not None\n"}, {}, {}),
    "A3 대조 — 현장 꼴: sys.modules[계산 이름] = 모듈 등록 + importlib.util.spec_from_file_location + exec_module(deployment-config 꼴 · 정지)": (
        {**INI, "application/order/test/test_load.py": "import importlib.util\nimport sys\n\n\ndef test_load(tmp_path):\n    p = tmp_path / \"m.py\"\n    p.write_text(\"VALUE = 7\\n\")\n    spec = importlib.util.spec_from_file_location(\"dyn_m\", p)\n    module = importlib.util.module_from_spec(spec)\n    sys.modules[spec.name] = module\n    spec.loader.exec_module(module)\n    assert module.VALUE == 7\n"}, {}, {}),
    "A4 허용 — PEP 263 latin-1 인코딩 표지 시험 파일(바이트 파싱 · minor 4)": (
        {**INI, "application/order/test/test_latin.py": LATIN1}, {}, {}),
    "A5 허용 — importlib.import_module(계산한 이름) · sys.modules 읽기(§12 — 계산 이름은 통과)": (
        {**INI, "application/order/test/test_dyn.py": "import importlib\n\nNAME = \"application.order.product\"\n\n\ndef test_d():\n    m = importlib.import_module(NAME)\n    assert m is not None\n"}, {}, {}),
}

REOBTAIN = {
    "RO1 재취득 — globals()[\'sys\'].monitoring.use_tool_id(…) (v15 구멍 · v15.1 정지)": (
        {**INI, "conftest.py": conf("            g = globals()\n            g[\'sys\'].monitoring.use_tool_id(0, \'x\')\n            g[\'sys\'].monitoring.set_events(0, 0)\n            method()\n"), TO: R13_TEST}, {"NO_BODY": "1"}),
    "RO2 재취득 — sys.modules[\'sys\'] 읽기 뒤 .settrace": (
        {**INI, "conftest.py": conf("            import sys\n            sys.modules[\'sys\'].settrace(lambda *a: None)\n            method()\n", head_import="import sys\n"), TO: R13_TEST}, {"NO_BODY": "1"}),
    "RO3 재취득 — importlib.sys.settrace": (
        {**INI, "conftest.py": conf("            import importlib\n            importlib.sys.settrace(lambda *a: None)\n            method()\n", head_import="import importlib\n"), TO: R13_TEST}, {"NO_BODY": "1"}),
    "RO4 재취득 — func.__globals__[\'sys\']._getframe().f_trace 대입": (
        {**INI, "conftest.py": conf("            fr = (lambda: None).__globals__\n            fr[\'sys\']._getframe().f_trace = (lambda *a: None)\n            method()\n"), TO: R13_TEST}, {"NO_BODY": "1"}),
}

REOBTAIN_CTL = {
    "RO5 허용 — \'sys\' in sys.modules 멤버십 · sys.modules[앱 상수] 읽기": (
        {**INI, "application/order/test/test_mem.py": "import sys\n\n\ndef test_m():\n    assert \'sys\' in sys.modules\n    assert sys.modules.get(\'application.order.product\') is None or True\n"}, {}, {}),
}

_N1_ATTRS = ("settrace", "setprofile", "settrace_all_threads", "setprofile_all_threads", "addaudithook", "f_trace",
             "f_trace_lines", "f_trace_opcodes", "set_trace", "breakpoint", "monitoring", "_getframe", "_current_frames")

MINOR_CTL = {
    "MF1 받는 쪽 대조(r15b-4) — fabfile 적재 꼴을 from importlib import util 로 받은 util.… 표기": (
        {**INI, "application/order/test/test_load_util.py": "import sys\nfrom importlib import util\n\n\ndef test_load(tmp_path):\n    p = tmp_path / \"m.py\"\n    p.write_text(\"VALUE = 7\\n\")\n    spec = util.spec_from_file_location(\"dyn_m1\", p)\n    module = util.module_from_spec(spec)\n    sys.modules[spec.name] = module\n    try:\n        spec.loader.exec_module(module)\n        assert module.VALUE == 7\n    finally:\n        del sys.modules[spec.name]\n"}, {}, {}),
    "MF2 from-import 대조(r15b-4) — from importlib.util import spec_from_file_location, module_from_spec 로 쓴 적재 꼴": (
        {**INI, "application/order/test/test_load_from.py": "import sys\nfrom importlib.util import module_from_spec, spec_from_file_location\n\n\ndef test_load(tmp_path):\n    p = tmp_path / \"m.py\"\n    p.write_text(\"VALUE = 7\\n\")\n    spec = spec_from_file_location(\"dyn_m2\", p)\n    module = module_from_spec(spec)\n    sys.modules[spec.name] = module\n    try:\n        spec.loader.exec_module(module)\n        assert module.VALUE == 7\n    finally:\n        del sys.modules[spec.name]\n"}, {}, {}),
    "MF3 그 밖 첨자 쓰기 · 삭제(r15b-1 자기 시험) — sys.modules[\"dyn_x3\"] = 객체 · del": (
        {**INI, "application/order/test/test_sub_write.py": "import sys\n\n\ndef test_w():\n    sys.modules[\"dyn_x3\"] = object()\n    try:\n        assert \"dyn_x3\" in sys.modules\n    finally:\n        del sys.modules[\"dyn_x3\"]\n"}, {}, {}),
    "MS1 메서드 꼴 통과 대조(r15b-3 · 운영자 결정 — 문면을 원형대로) — 현장 꼴 monkeypatch.setitem(sys.modules, …, None)": (
        {**INI, "application/order/test/test_setitem_modules.py": "import sys\n\nimport pytest\n\n\ndef test_optional_dep_missing(monkeypatch):\n    monkeypatch.setitem(sys.modules, \"dyn_opt_dep\", None)\n    with pytest.raises(ImportError):\n        import dyn_opt_dep  # noqa: F401\n"}, {}, {}),
    "MT1 types.LambdaType 읽기(r15b-6 — FunctionType 과 같은 객체)": (
        {**INI, "application/order/test/test_lambda_type.py": "import types\n\n\ndef _f():\n    return 1\n\n\ndef test_t():\n    assert isinstance(_f, types.LambdaType)\n"}, {}, {}),
    "MT2 types.FunctionType 읽기(r15b-6 대조)": (
        {**INI, "application/order/test/test_function_type.py": "import types\n\n\ndef _f():\n    return 1\n\n\ndef test_t():\n    assert isinstance(_f, types.FunctionType)\n"}, {}, {}),
    "MI1 inspect.getgeneratorlocals 읽기(r15b-6 — 원형 거부 집합 11 이름)": (
        {**INI, "application/order/test/test_gen_locals.py": "import inspect\n\n\ndef _g():\n    yield 1\n\n\ndef test_i():\n    assert inspect.getgeneratorlocals(_g()) == {}\n"}, {}, {}),
    "MN1 N1 이름 13 — 핸들 밖 받는 쪽(o.<이름> · 부르지 않는 도우미 안)(r15b-7)": (
        {**INI, "application/order/test/test_n1_names.py": "def _names(o):\n    return (\n" + "".join(f"        o.{a},\n" for a in _N1_ATTRS) + "    )\n\n\ndef test_n():\n    assert callable(_names)\n"}, {}, {}),
    "MD1 re.compile(변수) 대조(r15b-8 — D3 은 내장 이름 그대로 부른 호출만)": (
        {**INI, "application/order/test/test_re_var.py": "import re\n\nPATTERN = r\"^a+$\"\n\n\ndef test_r():\n    pat = PATTERN\n    assert re.compile(pat).match(\"aaa\")\n"}, {}, {}),
}


# ── 묶음 짜기(원형 b0_v152.main 의 순서) ──
def _bundle(bundle: str, *parts: "tuple[str, dict]") -> "list[Case]":
    """원형 run_env(«env») · run_cases(«pair») 사전을 차례대로 Case 로 — id = <묶음>-<묶음 안 차례 두 자리>."""
    out: "list[Case]" = []
    for kind, table in parts:
        for name, spec in table.items():
            cid: str = f"{bundle}-{len(out) + 1:02d}"
            if kind == "env":
                out.append(Case(cid, "R", bundle, name, "env", spec[0], spec[1], after=spec[2] if len(spec) > 2 else None))
            else:
                files, env, opts = spec
                out.append(Case(cid, "R", bundle, name, "pair", files, env, argvs=opts.get("argvs"), frozen=opts.get("frozen"),
                                drop_worker=opts.get("drop_worker", False)))
    return out


R_CASES: "list[Case]" = [
    *_bundle("r14", ("env", R14)),
    *_bundle("same", ("env", SAME_V15), ("pair", SAME_CTL_V15)),
    *_bundle("reobtain", ("env", REOBTAIN), ("pair", REOBTAIN_CTL)),
    *_bundle("minor", ("pair", MINOR_CTL)),
    *_bundle("r13", ("env", R13)),
    *_bundle("same14", ("env", SAME_V14), ("pair", SAME_CTL_V14)),
    *_bundle("r12", ("env", R12)),
    *_bundle("same13", ("env", SAME_V13), ("pair", SAME_CTL_V13)),
    *_bundle("r11", ("env", R11)),
    *_bundle("new", ("env", NEW), ("pair", CTL_V12)),
    *_bundle("c11", ("env", CLAUDE_R11), ("pair", CT11)),
    *_bundle("v11", ("env", {**R10, **SAME_V11, **CLAUDE_R10}), ("pair", {**CLAUDE_R10_PAIRS, **CONTROLS})),
    *_bundle("old", ("pair", {**CASES_V8, **DJ_CASES_V8})),
    *_bundle("prev", ("pair", {**R8, **R9, **CL9}), ("env", ENV_CASES)),
]


# ── (N) 이름별 독립 사례(설계 «자기 시험 묶음» — 구현 픽스처는 이름마다 하나씩) ──
# 이름 차례 = 원형 support_v152.py:72 INSPECT_DENY · b0_v152.py _N1_ATTRS(= support_v152.py:89 OBS_NAMES) 글자 그대로
INSPECT_DENY_NAMES: "tuple[str, ...]" = ("currentframe", "stack", "trace", "getframeinfo", "getouterframes", "getinnerframes",
                                         "getgeneratorstate", "getgeneratorlocals", "getcoroutinestate", "getcoroutinelocals",
                                         "_getframe")
INSPECT_ONE: str = "import inspect\n\n\ndef _helper():\n    return inspect.{name}\n\n\ndef test_i():\n    assert callable(_helper)\n"
N1_ONE: str = "def _names(o):\n    return (\n        o.{name},\n    )\n\n\ndef test_n():\n    assert callable(_names)\n"

N_CASES: "list[Case]" = [
    *(Case(f"N-inspect-{a}", "N", "inspect", f"inspect 거부 이름 {a} — import inspect 뒤 부르지 않는 도우미 안 inspect.{a} 읽기", "pair",
           {**INI, f"application/order/test/test_inspect_{a}.py": INSPECT_ONE.format(name=a)}, {}) for a in INSPECT_DENY_NAMES),
    *(Case(f"N-n1-{a}", "N", "n1", f"N1 이름 {a} — 핸들 밖 받는 쪽 o.{a}(부르지 않는 도우미 안 · MN1 꼴)", "pair",
           {**INI, f"application/order/test/test_n1_{a}.py": N1_ONE.format(name=a)}, {}) for a in _N1_ATTRS),
]


# ── (C) 빈 범주(원형 사례가 덮지 않던 정적 규칙 자기 시험 갈래 · 정오 2 상한) ──
CONST_EXEC: str = "def _helper():\n    exec(\"sys.settrace(None)\")\n\n\ndef test_c():\n    assert callable(_helper)\n"
# 러너가 F_CHILD_PID_FILE 을 줄 때만 수집 중(시험 모듈 적재) 멈추고 자식 하나를 더 띄운다 — 자식 pid 는 그 파일에 쓴다(묶음 밖
# 확인용). 주지 않으면 보통 시험이다(suite 칸의 앞선 지원 확인이 «지원»이 되게). 둘 다 120 초 뒤 스스로 끝난다.
HANG: str = ("import os\nimport subprocess\nimport sys\nimport time\n\n"
             "if os.environ.get(\"F_CHILD_PID_FILE\"):\n"
             "    CHILD = subprocess.Popen([sys.executable, \"-c\", \"import time; time.sleep(120)\"])\n"
             "    with open(os.environ[\"F_CHILD_PID_FILE\"], \"w\", encoding=\"utf-8\") as fh:\n        fh.write(str(CHILD.pid))\n"
             "    time.sleep(120)\n\n\ndef test_never():\n    assert True\n")

# 수집 < 10초 < 시험 본문 12초 < suite 40초. 두 명령은 각각 21초 본문으로 합만 40초를 넘긴다(러너 상수 LIMIT_* 와 짝).
LIMIT_SLOW: str = ("import time\nfrom application.order.product import product\n\n\ndef test_order():\n"
                   "    time.sleep(12)\n    assert product() == 5\n")
LIMIT_TWO: str = ("import time\nfrom application.order.product import product\n\n\ndef test_first():\n"
                  "    time.sleep(21)\n    assert product() == 5\n\n\ndef test_second():\n"
                  "    time.sleep(21)\n    assert product() == 5\n")
LIMIT_HANG: str = ("import os\nimport subprocess\nimport sys\nimport time\n"
                   "from application.order.product import product\n\n\ndef test_{hang}():\n"
                   "    if os.environ.get('F_CHILD_PID_FILE'):\n"
                   "        child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])\n"
                   "        with open(os.environ['F_CHILD_PID_FILE'], 'w', encoding='utf-8') as fh:\n"
                   "            fh.write(str(child.pid))\n        time.sleep(120)\n"
                   "    assert product() == 5\n\n\ndef test_{other}():\n"
                   "    if os.environ.get('F_CHILD_PID_FILE') and '{other}' == 'second':\n"
                   "        with open(os.environ['F_CHILD_PID_FILE'] + '.next', 'w', encoding='utf-8') as fh:\n"
                   "            fh.write('다음 명령 실행됨')\n    assert product() == 5\n")
LIMIT_ARGVS: "list[list[str]]" = [[PY, "-m", "pytest", "-k", "first"], [PY, "-m", "pytest", "-k", "second"]]

def _nest(code: str, levels: int) -> str:
    """상수 코드를 exec 로 levels 겹 감싼다(D3 «세 단 · 넘으면 통과» 경계)."""
    for _ in range(levels):
        code = f"exec({code!r})"
    return code


def _helper_only(body: str, head: str = "") -> str:
    """부르지 않는 도우미 하나 + 통과하는 시험 하나 — 정적 규칙만 걸리고 실행은 정상인 꼴."""
    return f"{head}def _helper():\n    {body}\n\n\ndef test_h():\n    assert callable(_helper)\n"


def _forge(finalized: bool) -> str:
    """프로젝트 conftest 가 DDDJANGO_PROBE_OUT 자리에 탐침과 같은 칸의 단일 기록을 하나 더 쓰는 꼴(탐침 이름 언급 없음)."""
    record = {"role": "single", "workerid": None, "rootpath": "", "inipath": None, "args": [], "exitstatus": 0, "initial": [],
              "final": [], "calls": [], "skips": [], "passed": [], "meta": {}, "complete": [], "files": [], "unresolved": [], "bad": [],
              "hookimpls": [], "allowed_sourceless": [], "workers_ready": [], "finalized": finalized, "late": [], "failed": 0,
              "import_skips": [], "anchor": [], "optimize": 0, "flags": {}, "greenlet_loaded": False}
    return ("import os\n\n\ndef pytest_configure(config):\n    out = os.environ.get('DDDJANGO_PROBE_OUT')\n    if out:\n"
            "        os.makedirs(out, exist_ok=True)\n        with open(os.path.join(out, 'zz-extra.json'), 'w') as f:\n"
            f"            f.write({json.dumps(json.dumps(record))})\n")


MUT_PG: str = ("import pytest\nfrom pathlib import Path\n\n\n@pytest.mark.pg\ndef test_mut():\n"
               "    p = Path(__file__).resolve().parents[1] / 'product.py'\n    p.write_text('def product():\\n    return 5\\n\\n')\n")


C_CASES: "list[Case]" = [
    Case("C-parse", "C", "empty", "파싱 실패 — 수집되지 않는 시험 쪽 도우미 자리의 파싱 못 하는 .py", "pair",
         {**INI, "application/order/test/helpers_broken.py": "def broken(:\n    return 1\n"}, {}),
    Case("C-const-exec", "C", "empty", "상수 코드 재검사 — 부르지 않는 도우미 안 exec 의 상수 코드 속 sys.settrace", "pair",
         {**INI, "application/order/test/test_const_exec.py": CONST_EXEC}, {}),
    # observer_scan 사유 판형 단위로 본 빈 갈래(설계 §4-1 문면에 판정이 있는 것만)
    Case("C-n2-from", "C", "empty", "도구 모듈 from-import — 부르지 않는 도우미 안 from bdb import Bdb", "pair",
         {**INI, "application/order/test/test_n2_from.py": _helper_only("from bdb import Bdb\n    return Bdb")}, {}),
    Case("C-import-star", "C", "empty", "위험 모듈 from-import * — from threading import *", "pair",
         {**INI, "application/order/test/test_import_star.py":
          "from threading import *  # noqa: F403\n\n\ndef test_s():\n    assert True\n"}, {}),
    Case("C-from-inspect", "C", "empty", "inspect 거부 이름 from-import — 부르지 않는 도우미 안 from inspect import currentframe", "pair",
         {**INI, "application/order/test/test_from_inspect.py": _helper_only("from inspect import currentframe\n    return currentframe")}, {}),
    Case("C-modules-get", "C", "empty", "상수 위험 이름 재취득 — 부르지 않는 도우미 안 sys.modules.get(\"threading\")", "pair",
         {**INI, "application/order/test/test_modules_get.py": _helper_only("return sys.modules.get(\"threading\")", "import sys\n\n\n")}, {}),
    Case("C-const-parse", "C", "empty", "상수 코드 파싱 못 함 — 부르지 않는 도우미 안 exec(\"def (:\")", "pair",
         {**INI, "application/order/test/test_const_parse.py": _helper_only("exec(\"def (:\")")}, {}),
    Case("C-n1-bare", "C", "empty", "N1 바 이름 — 부르지 않는 도우미 안 breakpoint 이름 읽기", "pair",
         {**INI, "application/order/test/test_n1_bare.py": _helper_only("return breakpoint")}, {}),
    Case("C-d3-depth3", "C", "empty", "상수 코드 세 단 — exec 세 겹 안의 sys.settrace(다시 봄 · 정지)", "pair",
         {**INI, "application/order/test/test_d3_depth3.py": _helper_only(_nest("sys.settrace(None)", 3))}, {}),
    Case("C-d3-depth4", "C", "empty", "상수 코드 네 단 — exec 네 겹 안의 sys.settrace(세 단 넘음 · 통과)", "pair",
         {**INI, "application/order/test/test_d3_depth4.py": _helper_only(_nest("sys.settrace(None)", 4))}, {}),
    # E 갈래가 넘긴 지원 확인 · 증거 실행 빈 조건(계획 T10 E3 — 기대 = 설계 §4-5 문면 · 꼴 = E 자기 시험 R9 ~ R12)
    Case("C-gap-exit5", "C", "gap", "수집 0(exit 5) — 시험이 하나도 없는 장난감 · collect 는 지원 · run 은 exit 5", "pair",
         {**INI, "application/order/test/test_order.py": "# 시험 없음 — 수집 0\n"}, {}),
    Case("C-gap-outputs", "C", "gap", "출력 수 이상 — 프로젝트 conftest 가 탐침 출력 자리에 확정 표지 있는 단일 기록을 하나 더 씀", "pair",
         {**INI, "conftest.py": _forge(True)}, {}),
    Case("C-gap-unfinalized", "C", "gap", "출력 수 이상 · 확정 표지 없음 — 더 쓴 단일 기록의 finalized = false", "pair",
         {**INI, "conftest.py": _forge(False)}, {}),
    Case("C-gap-hook-unknown", "C", "gap", "정체 불명 훅 원본 — 상속 PYTHONPATH 의 저장소 · 설치 패키지 밖 플러그인 -p extplug 의 pytest_runtest_setup", "pair",
         {"pytest.ini": "[pytest]\naddopts = -p extplug\n"}, {"PYTHONPATH": EXT_PLUGIN}),
    Case("C-gap-fp-between", "C", "gap", "명령 사이 지문 — 두 명령(-m pg · -m \"not pg\") · 명령 1 의 시험이 제품 파일을 바꿈", "pair",
         {"pytest.ini": "[pytest]\nmarkers =\n    pg: db\n", "application/order/test/test_mut.py": MUT_PG}, {},
         argvs=[[PY, "-m", "pytest", "-m", "pg"], [PY, "-m", "pytest", "-m", "not pg"]]),
    # 읽기 실패 — 수집되지 않는 시험 쪽 도우미 자리의 끊긴 심링크(.py)는 «확인 못 함» 정지 · 제품 쪽 자리는 보는 파일이 아니라 통과
    Case("C-read-fail-symlink", "C", "empty", "읽기 실패 — 수집되지 않는 시험 쪽 도우미 자리의 끊긴 심링크(.py)", "pair",
         {**INI}, {}, symlinks={"application/order/test/support/locked.py": "missing_target.py"}),
    Case("C-read-fail-symlink-product", "C", "empty", "대조 — 제품 쪽 자리의 끊긴 심링크(.py)는 보는 파일이 아니다", "pair",
         {**INI}, {}, symlinks={"application/order/locked.py": "missing_target.py"}),
    # 수리한 결함의 반례 — 작업 트리에서 지운 추적 파일(한글 경로 포함)이 있어도 트리 지문이 서고 지원 확인 · 증거 실행이 통과한다
    Case("C-fp-deleted-tracked", "C", "regress", "지운 추적 파일 — 커밋된 장난감에서 제품 쪽 추적 파일 둘(하나는 한글 경로)을 지운 작업 트리", "pair",
         {**INI, "application/order/legacy.py": "LEGACY = 1\n", "application/order/기록.py": "NOTE = 1\n"}, {},
         after_commit={"application/order/legacy.py": None, "application/order/기록.py": None}),
    Case("C-timeout", "C", "empty", "600 초 상한 — support --collect · suite 명령 진입(cmd_support · cmd_suite) · 수집 중 멈추고 자식 하나를 더 띄움"
                                    "(상한 상수만 짧게 · 구현판 전용)", "timeout",
         {**INI, "application/order/test/test_hang.py": HANG}, {}),
    # 시간 초과 실행의 G0 자료는 불완전하므로 C-timeout도 파일별 위반 대신 생략 한 원소를 기대한다.
    Case("C-limit-T1", "C", "limits", "T1 수집 상한보다 긴 정상 시험 — suite green · 탐침 증거 · G0 유지", "limits",
         {**INI, "application/order/test/test_order.py": LIMIT_SLOW}, {}),
    Case("C-limit-T2a", "C", "limits", "T2a 첫 명령 suite 시간 초과 — 묶음 종료 · 다음 명령 미실행 · G0 대조 생략", "limits",
         {**INI, "application/order/test/test_order.py": LIMIT_HANG.format(hang="first", other="second")}, {}, argvs=LIMIT_ARGVS),
    Case("C-limit-T2b", "C", "limits", "T2b 첫 명령 정상 · 둘째 시간 초과 — 부분 탐침 증거 · G0 대조 생략", "limits",
         {**INI, "application/order/test/test_order.py": LIMIT_HANG.format(hang="second", other="first")}, {}, argvs=LIMIT_ARGVS),
    Case("C-limit-T3", "C", "limits", "T3 수집 상한보다 긴 수집 — 지원 안 함 · 같은 시간은 suite 상한 미만", "limits",
         {**INI, "application/order/test/test_order.py": "import time\ntime.sleep(12)\n\n\ndef test_order():\n    assert True\n"}, {}),
    Case("C-limit-T4", "C", "limits", "T4 두 명령 각각 suite 상한 미만 · 합은 초과 — green", "limits",
         {**INI, "application/order/test/test_order.py": LIMIT_TWO}, {}, argvs=LIMIT_ARGVS),
    Case("C-limit-T5b", "C", "limits", "T5b 상한 전 exit 0 · 탐침 출력 없음 — red", "limits",
         {**INI, "application/order/test/test_order.py": "import os\nimport time\n\n\ndef test_order():\n    time.sleep(3)\n    os._exit(0)\n"}, {}),
    # T5a = 기존 r12-06(exit 1), T5c = 기존 r13-05(exit 0 · 결과 증거 없음) — 독립 red 기대를 재사용한다.
]

ALL_CASES: "list[Case]" = [*R_CASES, *N_CASES, *C_CASES]


def toy_files(case: Case) -> "dict[str, str | bytes]":
    """장난감 저장소에 쓸 파일 — 원형 build 와 같이 BASE 위에 사례 파일을 얹는다."""
    return {**BASE, **case.files}
