#!/usr/bin/env python3
"""2.7.0 TG4(브라우저 시험 꼴) 회귀 — 이번 실행이 늘린 띄움 자리 · 띄우는 시험 경우만 막는다.

장면마다 표준 트리 합성 프로젝트(임시 git 저장소)의 기준점 뒤에 시험 쪽 파일을 바꾸고 `backstop.py --diff-base <기준> --only tg4`
출력을 본다. 칸은 다섯이다.
  POS  — 늘어난 띄움: 직접 띄우기 · 브라우저 단위 고정물 덮기 · 다른 모듈의 띄우는 고정물을 받는 새 고정물 · 고정물이 준 실행기 ·
         with_name 로 부르는 기존 러너 · 새 JS 러너 · 생성식 매개변수 · 브라우저 실행 파일(동적 실행 파일 + `--headless` 와 브라우저
         전용 낱말) · Playwright CLI · Selenium · `import a.b.c` 점 사슬 도우미 · 도우미 순환
  NEG  — 늘지 않음: 기존 시험 고침 · 이름 바꿈 · 도우미 옮김 · 작은 파일 D/A · 인라인 셋을 도우미로 · 오라클 · 주석 · 탐침 ·
         page 받는 새 시험 · 승인 병합이 들인 띄움 · 함께 고친 지원 모듈(기준판 쪽은 기준판으로) · `--headless` 하나뿐인 다른 도구
  NOTE — 알림 · 발견 자리: 충돌 해소 병합 · 동적 하위 프로세스 인자 · 셀 수 없는 매개변수 · 해석 실패는 그 파일만(이름 바꿈 짝도) ·
         이름 바꿈 + 다른 파일 새 띄움(발견은 다른 파일 하나) · 아주 큰 range
  SAME — TG2 · TG3 판정이 2.6.1 배포판(RELEASE_261 을 `git archive` 로 임시 폴더에 푼 scripts — HEAD 에 묶지 않는다)과 같다
  COUNT · MUT — 검사 수 93 · 슬라이스 끝 86 · 빚 지문 무변 · --slice-end · --only · 가름 제외 / 고침 되돌림 변형
2.6.1 커밋이 이력에 없으면(얕은 clone 등) SAME 과 빚 지문 대조만 건너뛰고 건너뛴 사실을 낸다(실패로 세지 않는다).
임시 git 저장소만 만들고 끝나면 지운다(네트워크 · 브라우저 · 시험 실행 없음). 인자로 장면 이름을 주면 그 장면만 돈다."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TEST = Path(__file__).resolve().parent
SCRIPTS = TEST.parent
REPO = SCRIPTS.parents[1]
sys.path.insert(0, str(TEST))
from fixtures_patch230 import ENV, git, mkstd, run_script  # noqa: E402

RELEASE_261 = 'be9f2d490a8dded8ee1507bd9620e7678e743b1a'  # dddjango-web 2.6.1 배포 커밋 — 올리지 않는다
PASS = FAIL = 0
BOARD = 'web_test/board/board_browser_test.py'
RUNNER = 'web_test/board/_board_runner.cjs'
OTHER = 'tests/web/other_browser_test.py'
SUPPORT = 'tests/web/_support.py'
RUN = '.dddjango-web/20261020-0000-tg4'
LAUNCH_JS = "const { chromium } = require('playwright'); (async () => { const b = await chromium.launch(); await b.close(); })();"


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok and detail:
        print('    ' + str(detail).replace('\n', '\n    ')[:2400])


def tg4(root, base, *extra, scripts=SCRIPTS):
    code, out = run_script(scripts / 'backstop.py', root, '--diff-base', base, *extra)
    return code, out, re.findall(r'^\[TG4\] BLOCKER — (\S+)$', out, re.M)


# ---------------------------------------------------------------- 바탕


BOARD_TEXT = '''import subprocess
from pathlib import Path

import pytest

JS = "%s"


@pytest.fixture
def node_tools():
    return ("node", "x", "y")


def test_board_opens(node_tools):
    node, _, _ = node_tools
    subprocess.run([node, "-e", JS], check=True)


def test_board_runner(node_tools):
    node, _, _ = node_tools
    subprocess.run([node, str(Path(__file__).with_name("_board_runner.cjs"))], check=True)
''' % LAUNCH_JS.replace('"', '\\"')

OTHER_TEXT = '''import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def shared_chrome():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


def test_other(shared_chrome):
    assert shared_chrome
'''

INLINE_TEXT = '''from playwright.sync_api import sync_playwright


def test_a():
    with sync_playwright() as p:
        b = p.chromium.launch()
        b.close()


def test_b():
    with sync_playwright() as p:
        b = p.chromium.launch()
        b.close()


def test_c():
    with sync_playwright() as p:
        b = p.chromium.launch()
        b.close()
'''

PARAM_TEXT = '''import pytest

CASES = tuple(f"B{i}" for i in range(1, 22))
PAIRS = [(a, b) for a in ("x", "y") for b in (1, 2, 3)]


@pytest.mark.parametrize("case", CASES)
def test_cases(shared_chrome, case):
    assert shared_chrome


@pytest.mark.parametrize("pair", PAIRS)
def test_pairs(shared_chrome, pair):
    assert shared_chrome
'''


def project(root):
    """표준 트리 + 기존 브라우저 시험(node 하위 프로세스 · 세션 띄움 고정물 · 인라인 셋 · 매개변수) → (Proj, BASE)."""
    p = mkstd(root)
    p.w(BOARD, BOARD_TEXT.rstrip('\n'))
    p.w(RUNNER, "const { chromium } = require('playwright');", '(async () => {', '  const b = await chromium.launch();',
        '  await b.close();', '})();')
    p.w(OTHER, OTHER_TEXT.rstrip('\n'))
    p.w('tests/web/conftest.py', 'from tests.web.other_browser_test import shared_chrome  # noqa: F401')
    p.w('tests/web/inline_browser_test.py', INLINE_TEXT.rstrip('\n'))
    p.w('tests/web/param_browser_test.py', PARAM_TEXT.rstrip('\n'))
    p.w('tests/web/small_browser_test.py', 'def test_small(shared_chrome):', '    assert shared_chrome')
    p.w('tests/web/page_browser_test.py', 'import pytest', '', '', '@pytest.fixture(scope="session")',
        'def browser_type_launch_args():', '    return {"headless": True}', '', '', 'def test_page(page):', '    assert page')
    p.w('tests/__init__.py', '')
    p.w('tests/web/__init__.py', '')
    return p, p.commit('base')


def add(rel, *lines):
    return lambda p: p.append(rel, '', '', *lines)


def write(rel, *lines):
    return lambda p: p.w(rel, *lines)


def sub(rel, old, new):
    return lambda p: p.sub(rel, old, new)


def steps(*edits):
    def run(p):
        for edit in edits:
            edit(p)
    return run


def rename(old, new):
    return lambda p: p.mv(old, new)


# ---------------------------------------------------------------- 장면 — (이름, 제목, 바꿈, 발견 파일 목록)

SCENES = [
    # POS
    ('P1', '새 시험 chromium.launch', write('tests/web/new_browser_test.py', 'from playwright.sync_api import sync_playwright',
     '', '', 'def test_new():', '    with sync_playwright() as p:', '        p.chromium.launch().close()'),
     ['tests/web/new_browser_test.py:5']),
    ('P2', '시험 모듈의 browser_type_launch_args 덮기', write('tests/web/args_browser_test.py', 'import pytest', '', '',
     '@pytest.fixture(scope="session")', 'def browser_type_launch_args():', '    return {"args": ["--x"]}', '', '',
     'def test_args(page):', '    assert page'), ['tests/web/args_browser_test.py:5']),
    ('P3', '새 _support 가 다른 모듈의 세션 띄움 고정물 import → 그것을 받는 새 고정물 → 새 시험(자리 0 · 경우 +3)',
     steps(write(SUPPORT, 'import pytest', 'from tests.web.other_browser_test import shared_chrome  # noqa: F401', '', '',
                 '@pytest.fixture', 'def chrome_page(shared_chrome):', '    page = shared_chrome.new_page()', '    yield page',
                 '    page.close()'),
           write('tests/web/screen_browser_test.py', 'import pytest', 'from tests.web._support import chrome_page  # noqa: F401',
                 '', '', '@pytest.mark.parametrize("n", [1, 2, 3])', 'def test_screen(chrome_page, n):',
                 '    assert chrome_page')),
     ['tests/web/screen_browser_test.py:5']),
    ('P4', '(I3①) 고정물이 준 실행기로 -e 띄움 JS 를 도는 새 시험',
     add(BOARD, 'def test_board_more(node_tools):', '    node, _, _ = node_tools', '    subprocess.run([node, "-e", JS], check=True)'),
     [BOARD + ':26']),
    ('P5', '(I3②) with_name 으로 기존 러너를 부르는 새 시험',
     add(BOARD, 'def test_board_runner_2(node_tools):', '    node, _, _ = node_tools',
         '    subprocess.run([node, str(Path(__file__).with_name("_board_runner.cjs"))], check=True)'), [BOARD + ':26']),
    ('P6', '새 .cjs 러너의 chromium.launch(', write('web_test/board/_second_runner.cjs', "const { chromium } = require('playwright');",
     'chromium.launch().then((b) => b.close());'), ['web_test/board/_second_runner.cjs:2']),
    ('P7', '(I3③) 생성식 range(1, 22) → range(1, 23)', sub('tests/web/param_browser_test.py', 'range(1, 22)', 'range(1, 23)'),
     ['tests/web/param_browser_test.py:3']),
    ('P8', '(I3③) 리터럴 내포 경우 +1', sub('tests/web/param_browser_test.py', 'b in (1, 2, 3)', 'b in (1, 2, 3, 4)'),
     ['tests/web/param_browser_test.py:4']),
    ('P9', '(I3④) 브라우저 실행 파일 --headless --dump-dom', write('tests/web/dump_browser_test.py', 'import subprocess', '',
     'CHROME = "/usr/bin/google-chrome"', '', '', 'def test_dump():',
     '    subprocess.run([CHROME, "--headless", "--dump-dom", "http://x"], check=True)'), ['tests/web/dump_browser_test.py:7']),
    ('P10', '(I3④) npx playwright test · os.system', write('tests/web/cli_browser_test.py', 'import os', 'import subprocess', '',
     '', 'def test_cli():', '    subprocess.run(["npx", "playwright", "test"], check=True)', '', '', 'def test_cli2():',
     '    os.system("npx playwright test")'), ['tests/web/cli_browser_test.py:6']),
    ('P11', '(I3④) import selenium', write('tests/web/sel_browser_test.py', 'from selenium import webdriver', '', '',
     'def test_sel():', '    assert webdriver'), ['tests/web/sel_browser_test.py:1']),
    ('P12', '(R-N6) 동적 실행 파일 + --headless 와 브라우저 전용 낱말 → 브라우저 실행 파일',
     write('tests/web/shot_cli_browser_test.py', 'import subprocess', '', '', 'def test_shot(chrome_bin):',
           '    subprocess.run([chrome_bin, "--headless=new", "--screenshot", "http://x"], check=True)'),
     ['tests/web/shot_cli_browser_test.py:5']),
    # NEG
    ('N1', '기존 node 띄움 시험의 JS 단언만 고침', sub(BOARD, 'await b.close();', 'await b.close(); console.log(1);'), []),
    ('N2', '기존 launch 줄 옵션만 고침', sub(OTHER, 'p.chromium.launch()', 'p.chromium.launch(headless=True)'), []),
    ('N3', '(I4) launch 시험 함수 이름만 바꿈', sub('tests/web/inline_browser_test.py', 'def test_a():', 'def test_alpha():'), []),
    ('N4', '(I4) 띄우는 도우미를 _support.py 로 옮김',
     steps(write('tests/web/inline_browser_test.py', 'from tests.web._support import open_chrome', '', '', 'def test_a():',
                 '    open_chrome()', '', '', 'def test_b():', '    open_chrome()', '', '', 'def test_c():', '    open_chrome()'),
           write(SUPPORT, 'from playwright.sync_api import sync_playwright', '', '', 'def open_chrome():',
                 '    with sync_playwright() as p:', '        p.chromium.launch().close()',
                 '        p.chromium.launch().close()', '        p.chromium.launch().close()')), []),
    ('N5', '(I4) 작은 시험 파일 rename + 고침(유사도 50% 밑 D/A)',
     steps(rename('tests/web/small_browser_test.py', 'tests/web/tiny_browser_test.py'),
           write('tests/web/tiny_browser_test.py', 'def test_tiny(shared_chrome):', '    assert shared_chrome is not None')), []),
    ('N6', '(I4) 인라인 launch 셋을 도우미 하나로 묶음',
     write('tests/web/inline_browser_test.py', 'from playwright.sync_api import sync_playwright', '', '', 'def _open():',
           '    with sync_playwright() as p:', '        p.chromium.launch().close()', '', '', 'def test_a():', '    _open()', '', '',
           'def test_b():', '    _open()', '', '', 'def test_c():', '    _open()'), []),
    ('N7', 'node vm 오라클 · 탐침 typeof · --version · 주석 · 문자열',
     write('tests/web/oracle_test.py', 'import subprocess', '', 'VM = "const vm = require(\'vm\'); vm.runInNewContext(\'1\');"',
           'PROBE = "console.log(typeof chromium.launch); // chromium.launch()"', 'TEXT = "chromium.launch() 는 쓰지 않는다"', '', '',
           'def test_oracle(browser):', '    subprocess.run(["node", "-e", VM], check=True)',
           '    subprocess.run(["node", "-e", PROBE], check=True)', '    subprocess.run([browser, "--version"], check=True)',
           '    # chromium.launch()', '    assert TEXT'), []),
    ('N8', 'page 받는 새 시험 · 기존 덮기가 있는 모듈에 page 받는 새 시험',
     steps(write('tests/web/plain_browser_test.py', 'def test_plain(page):', '    assert page'),
           add('tests/web/page_browser_test.py', 'def test_page_more(page, context):', '    assert page')), []),
    ('N9', '(S13) _support.py 와 시험을 함께 고침(띄움 그대로)',
     steps(write(SUPPORT, 'def label():', '    return "x"'),
           sub(OTHER, 'def test_other(shared_chrome):\n    assert shared_chrome',
               'from tests.web._support import label\n\n\ndef test_other(shared_chrome):\n    assert shared_chrome and label()')),
     []),
    ('N10', '(R-N6) --headless 하나뿐인 다른 도구(브라우저 아님)', write('tests/web/office_test.py', 'import subprocess', '', '',
     'def test_office():', '    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "x.docx"], check=True)'), []),
    ('R1', '(R-S4) 기존 launch 시험 이름 바꿈 + 다른 파일 새 띄움 → 발견은 그 다른 파일 하나',
     steps(sub('tests/web/small_browser_test.py', 'def test_small(', 'def test_small_renamed('),
           write('tests/web/new_browser_test.py', 'def test_new(shared_chrome):', '    assert shared_chrome')),
     ['tests/web/new_browser_test.py:1']),
]


def play(tmp, scene, scripts=SCRIPTS):
    name, _title, edit, _want = scene
    p, base = project(tmp / ('scene-' + name))
    edit(p)
    got = tg4(p.root, base, '--only', 'tg4', scripts=scripts)
    shutil.rmtree(p.root)
    return got


def bundle_scenes(tmp, only):
    for scene in SCENES:
        name, title, _edit, want = scene
        if only and name not in only:
            continue
        code, out, found = play(tmp, scene)
        check('%s %s — TG4 %s' % (name, title, ' · '.join(want) or '0'),
              sorted(found) == sorted(want) and code == (2 if want else 0) and 'Traceback' not in out, out[-2400:])


# ---------------------------------------------------------------- 승인 병합 · 알림


def merge_scene(tmp, name, upstream, lane=None, approve=True):
    """기준점 → upstream 가지 바꿈 → main 에 (lane 바꿈) → 병합 → 승인 목록 · build-state(git_snapshot = 기준점)."""
    p, base = project(tmp / name)
    p.w(RUN + '/build-state.json', json.dumps({'git_snapshot': base, 'test_command': 'pytest web_test tests/web'}))
    git(p.root, 'checkout', '-q', '-b', 'up')
    upstream(p)
    up = p.commit('upstream')
    git(p.root, 'checkout', '-q', 'main')
    if lane is not None:
        lane(p)
        p.commit('lane before merge')
    git(p.root, 'merge', '-q', '--no-ff', '-m', 'merge main', up)
    merge = git(p.root, 'rev-parse', 'HEAD')
    if approve:
        p.w(RUN + '/approved-merges.txt', merge + ' main 받기')
    return p, base


def bundle_merges(tmp, only):
    if not only or 'I5a' in only:
        p, base = merge_scene(tmp, 'i5a', write('web_test/board/_merged_runner.cjs', "const { chromium } = require('playwright');",
                                                 'chromium.launch();'))
        code, out, found = tg4(p.root, base, '--only', 'tg4')
        check('I5a 승인 병합이 새 .cjs(띄움)를 들임 → 0', code == 0 and not found, out)
    if not only or 'I5b' in only:
        p, base = merge_scene(tmp, 'i5b', write('tests/web/merged_browser_test.py', 'import subprocess', '',
                                                 'SETUP = 1', 'JS = "chromium.launch()"', '', '', 'def test_m():',
                                                 '    subprocess.run(["node", "-e", JS], check=True)'))
        p.sub('tests/web/merged_browser_test.py', 'SETUP = 1', 'SETUP = 2')
        code, out, found = tg4(p.root, base, '--only', 'tg4')
        check('I5b 병합으로 든 node 시험의 준비 한 줄만 고침 → 0', code == 0 and not found, out)
    if not only or 'A1' in only:
        p, base = merge_scene(tmp, 'a1', add(OTHER, 'def test_up(shared_chrome):', '    assert shared_chrome'),
                              lane=sub(OTHER, 'import pytest\n', 'import pytest  # lane\n'))
        code, out, found = tg4(p.root, base, '--only', 'tg4')
        check('A1 충돌 해소 병합(M≠M^2)이 든 띄움 → 기준점 판 기준이라 발화', code == 2 and found == [OTHER + ':17'], out)
    if not only or 'A6' in only:
        p, base = merge_scene(tmp, 'a6', write('web_test/board/_merged_runner.cjs', "const { chromium } = require('playwright');",
                                               'chromium.launch();'), approve=False)
        p.w(RUN + '/approved-merges.txt', 'invalid')
        code, out, found = tg4(p.root, base, '--only', 'tg4')
        check('A6 승인 목록을 못 읽으면 기준점 판으로 센다(TG4 를 끄지 않는다 · 병합이 든 띄움도 이 레인 몫)',
              code == 2 and found == ['web_test/board/_merged_runner.cjs:2'] and '승인 유입 판정 불가' in out
              and 'TG4 미실행' not in out, out)
    if not only or 'K6' in only:
        p, base = merge_scene(tmp, 'k6', write('docs/upstream.txt', 'x'))
        p.w('tests/web/new_browser_test.py', 'def test_new(shared_chrome):', '    assert shared_chrome')
        code, out, found = tg4(p.root, base, '--only', 'tg4')
        check('K6 TG4 발견은 승인 유입 가름 밖 — ↳ 가름 제외 검사', code == 2 and found
              and '↳ 이 레인 몫으로 남김: 가름 제외 검사' in out, out)


def scene_f3(tmp, scripts=SCRIPTS):
    """(F3) 기존 `_support.py` 의 띄우는 도우미를 `import tests.web._support` 뒤 점 사슬로 부르는 새 시험."""
    p, _base = project(tmp)
    p.w(SUPPORT, 'from playwright.sync_api import sync_playwright', '', '', 'def open_chrome():',
        '    with sync_playwright() as p:', '        p.chromium.launch().close()')
    base = p.commit('support')
    p.w('tests/web/dotted_browser_test.py', 'import tests.web._support', '', '', 'def test_dotted():',
        '    tests.web._support.open_chrome()')
    return tg4(p.root, base, '--only', 'tg4', scripts=scripts) + (['tests/web/dotted_browser_test.py:4'],)


def scene_a7(tmp, scripts=SCRIPTS):
    """(F6) 기준판만 구문 오류인 띄움 시험 파일을 고치며 이름을 바꿈 — 옛 이름 · 새 이름 둘 다 셈에서 빠진다."""
    p, _base = project(tmp)
    body = ['from playwright.sync_api import sync_playwright', '', '', 'def test_a():', '    with sync_playwright() as p:',
            '        p.chromium.launch().close()']
    p.w('tests/web/a_browser_test.py', *body, '', '', 'def broken(:', '    pass')
    base = p.commit('broken base')
    p.mv('tests/web/a_browser_test.py', 'tests/web/b_browser_test.py')
    p.w('tests/web/b_browser_test.py', *body)
    return tg4(p.root, base, '--only', 'tg4', scripts=scripts) + ([],)


def scene_f15(tmp, scripts=SCRIPTS):
    """(F15) 도우미 순환(_x → _y → _x · _x → _z 띄움) — 먼저 센 시험의 차례와 무관하게 _y 를 부르는 새 시험이 닿는다."""
    p, _base = project(tmp)
    p.w('tests/web/cycle_browser_test.py', 'from playwright.sync_api import sync_playwright', '', '', 'def _x():', '    _y()',
        '    _z()', '', '', 'def _y():', '    _x()', '', '', 'def _z():', '    with sync_playwright() as p:',
        '        p.chromium.launch().close()', '', '', 'def test_one():', '    _x()')
    base = p.commit('cycle base')
    p.append('tests/web/cycle_browser_test.py', '', '', 'def test_two():', '    _y()')
    return tg4(p.root, base, '--only', 'tg4', scripts=scripts) + (['tests/web/cycle_browser_test.py:22'],)


CUSTOM = {'F3': ('(F3) `import a.b.c` 뒤 점 사슬로 띄우는 도우미를 부르는 새 시험 → 경우 +1', scene_f3),
          'A7': ('(F6) 기준판만 해석 실패한 파일을 고치며 이름 바꿈 → 짝도 두 쪽 셈에서 빼 발견 없음', scene_a7),
          'F15': ('(F15) 도우미 순환 — 순환 도중의 «아님» 을 기억하지 않아 새 시험이 닿는다', scene_f15)}


def bundle_custom(tmp, only):
    for name, (title, scene) in CUSTOM.items():
        if only and name not in only:
            continue
        code, out, found, want = scene(tmp / name)
        ok = sorted(found) == sorted(want) and code == (2 if want else 0) and 'Traceback' not in out
        if name == 'A7':
            ok = ok and ('[info] TG4 일부 흐름 자동 판정 밖 — tests/web/a_browser_test.py 기준판/현재판 파이썬 구문 해석 실패'
                         in out)
        check('%s %s' % (name, title), ok, out[-2400:])


def bundle_notes(tmp, only):
    def scene(name, edit):
        p, base = project(tmp / name)
        edit(p)
        return tg4(p.root, base, '--only', 'tg4')

    if not only or 'A2' in only:
        code, out, found = scene('a2', write('tests/web/dyn_browser_test.py', 'import subprocess', '', '',
                                             'def test_dyn(cmd):', '    subprocess.run(cmd, check=True)'))
        check('A2 동적 하위 프로세스 인자 새 줄 → [info] TG4 일부 흐름 자동 판정 밖',
              code == 0 and '[info] TG4 일부 흐름 자동 판정 밖 — tests/web/dyn_browser_test.py:5 · 하위 프로세스 인자 동적' in out, out)
    if not only or 'A3' in only:
        code, out, found = scene('a3', write('tests/web/many_browser_test.py', 'import pytest', 'from x import make', '', '',
                                             '@pytest.mark.parametrize("n", make())', 'def test_many(shared_chrome, n):',
                                             '    assert shared_chrome'))
        check('A3 셀 수 없는 매개변수 새 줄 → [info] TG4 매개변수 경우 판정 밖(경우 1 로 셈)',
              '[info] TG4 매개변수 경우 판정 밖 — tests/web/many_browser_test.py:5' in out and found, out)
    if not only or 'A4' in only:
        code, out, found = scene('a4', steps(
            write('web_test/board/bad_runner.cjs', 'chromium.launch();', 'const re = /unterminated'),
            write('tests/web/new_browser_test.py', 'def test_new(shared_chrome):', '    assert shared_chrome')))
        check('A4 (R-S6) JS 해석 실패는 그 파일만 알림 · 다른 파일 새 띄움은 그대로 발화',
              '[info] TG4 일부 흐름 자동 판정 밖 — web_test/board/bad_runner.cjs 기준판/현재판 JS 토큰 해석 실패' in out
              and found == ['tests/web/new_browser_test.py:1'] and 'TG4 미실행' not in out, out)
    if not only or 'A5' in only:
        p, base = project(tmp / 'a5')
        p.w('tests/web/broken_browser_test.py', 'def test_x(:', '    pass')
        base = p.commit('broken base')
        p.w('tests/web/broken_browser_test.py', 'def test_x(shared_chrome):', '    assert shared_chrome')
        p.w('tests/web/new_browser_test.py', 'def test_new(shared_chrome):', '    assert shared_chrome')
        code, out, found = tg4(p.root, base, '--only', 'tg4')
        check('A5 기준판 구문 오류는 그 파일만 두 쪽 셈에서 뺀다 · 다른 파일은 판정',
              '[info] TG4 일부 흐름 자동 판정 밖 — tests/web/broken_browser_test.py 기준판/현재판 파이썬 구문 해석 실패' in out
              and found == ['tests/web/new_browser_test.py:1'], out)
    if not only or 'A8' in only:
        code, out, found = scene('a8', write('tests/web/huge_browser_test.py', 'import pytest', '', '',
                                             '@pytest.mark.parametrize("n", tuple(i for i in range(100000000000000000000)))',
                                             'def test_huge(shared_chrome, n):', '    assert shared_chrome'))
        check('A8 (F14) 아주 큰 range 내포 → 경우 수 판정 밖 알림(내부 오류 아님)',
              '[info] TG4 매개변수 경우 판정 밖 — tests/web/huge_browser_test.py:4' in out and found
              and 'Traceback' not in out, out)
    if not only or 'K7' in only:
        p, _base = project(tmp / 'k7')
        code, out = run_script(SCRIPTS / 'backstop.py', p.root, '--all', '--only', 'tg4')
        check('K7 기준점 없음 → [info] TG4 미실행', '[info] TG4 미실행 — git 기준점 없음 · 변경 시험 범위 미확정' in out, out)


# ---------------------------------------------------------------- SAME · COUNT · MUT


SAME_SCENES = [
    ('S1', 'TG2 기록 폴더 경로 읽기', write('tests/web/rec_test.py', 'from pathlib import Path', '', '',
     'def test_rec():', '    Path(".dddjango-web/x.json").read_text()')),
    ('S2', 'TG2 node -e 의 fs.readFileSync 기록 폴더', write('tests/web/node_rec_test.py', 'import subprocess', '', '',
     'def test_node():', '    subprocess.run(["node", "-e", "require(\'fs\').readFileSync(\'.dddjango-web/x\')"], check=True)')),
    ('S3', 'TG3 스크린샷 두 출처 비교', write('tests/web/shot_browser_test.py', 'def test_shot(page):', '    a = page.screenshot()',
     '    b = page.screenshot()', '    assert a == b')),
    ('S4', 'TG2 동적 흐름 알림 · 브라우저 시험 고침', add(BOARD, 'def test_dyn(node_tools, cmd):',
     '    subprocess.run(cmd, check=True)')),
    ('S5', 'TG2·TG3 해당 없음(page 받는 새 시험)', write('tests/web/plain_test.py', 'def test_plain(page):', '    assert page')),
]


def release_scripts(tmp, sha):
    """커밋 sha 의 scripts 를 임시 폴더에 푼다 → scripts 폴더(이력에 없으면 None)."""
    archive = subprocess.run(['git', '-C', str(REPO), 'archive', sha, 'dddjango-web/scripts', 'dddjango-web/.claude-plugin'],
                             capture_output=True, env=ENV)
    if archive.returncode:
        print('SKIP 2.6.1 대조 — 배포 커밋 %s 가 이 저장소 이력에 없다(얕은 clone 등) — 그 대조만 건너뛴다(실패로 세지 않는다)' % sha[:12])
        return None
    tmp.mkdir(parents=True)
    subprocess.run(['tar', '-xf', '-', '-C', str(tmp)], input=archive.stdout, check=True)
    return tmp / 'dddjango-web' / 'scripts'


def tg23(out):
    """TG2 · TG3 발견 세 줄 · TG2 알림 줄 · 요약 밖 판정 줄만."""
    rows = out.splitlines()
    keep = []
    for i, line in enumerate(rows):
        if re.match(r'^\[(TG2|TG3)\] BLOCKER', line):
            keep += rows[i:i + 3]
        elif line.startswith('[info] TG2'):
            keep.append(line)
    return keep


def bundle_same(tmp, only, old):
    for name, title, edit in SAME_SCENES:
        if only and name not in only:
            continue
        p, base = project(tmp / ('same-' + name))
        edit(p)
        now = run_script(SCRIPTS / 'backstop.py', p.root, '--diff-base', base, '--only', 'tg2,tg3')
        was = run_script(old / 'backstop.py', p.root, '--diff-base', base, '--only', 'tg2,tg3')
        check('%s %s — TG2·TG3 줄 · exit 가 2.6.1 과 같다' % (name, title),
              (now[0], tg23(now[1])) == (was[0], tg23(was[1])) and 'Traceback' not in now[1],
              '2.6.1 exit %d\n%s\n--- 이 판 exit %d\n%s' % (was[0], '\n'.join(tg23(was[1])), now[0], '\n'.join(tg23(now[1]))))


def bundle_counts(tmp, only, old):
    if only and 'K' not in only:
        return
    p, base = project(tmp / 'k')
    code, out = run_script(SCRIPTS / 'backstop.py', p.root, '--diff-base', base)
    check('K1 [backstop] 검사 93종', '[backstop] 검사 93종(' in out, out[-800:])
    p.w('tests/web/new_browser_test.py', 'def test_new(shared_chrome):', '    assert shared_chrome')
    code, out = run_script(SCRIPTS / 'backstop.py', p.root, '--diff-base', base, '--slice-end')
    check('K2 슬라이스 끝 93 중 86 · 미룸 7 그대로', '검사 93종 중 86종(슬라이스 끝 — 미룸 7: CY1 · NM4 · NM5 · NM18 · NM19 · ST4 · TG1'
          in out, out[-800:])
    check('K4 --slice-end 에서 TG4 발화', '[TG4] BLOCKER — tests/web/new_browser_test.py:1' in out, out[-1600:])
    for only_value in ('tg', 'tg4'):
        code, out = run_script(SCRIPTS / 'backstop.py', p.root, '--diff-base', base, '--only', only_value)
        check('K5 --only %s 에서 TG4 발화' % only_value, code == 2 and '[TG4] BLOCKER' in out, out[-800:])
    if old is None:
        return
    probe = ('import json, sys; sys.path.insert(0, sys.argv[1]); from src import debt; '
             'print(json.dumps([debt.scanner_stamp()["checks"], list(debt.CHECK_IDS), debt.KEY_SCHEME]))')
    stamps = [subprocess.run([sys.executable, '-B', '-c', probe, str(s)], capture_output=True, text=True, env=ENV).stdout
              for s in (SCRIPTS, old)]
    check('K3 빚 지문(검사 집합 해시 · 키 의미론) 무변 — 2.6.1 과 같다', stamps[0] == stamps[1] and stamps[0], stamps)


MUTANTS = [
    ('with_name 접기를 뺌', "    return _value(_Fold(env).visit(copy.deepcopy(node)), env)\n", "    return _value(node, env)\n", 'P5'),
    ('승인 병합 기준판을 뺌', "                    self.verbatim[path] = sha\n", "                    pass\n", 'I5a'),
    ('발견을 새쪽 추가 줄 파일마다(R-S4 전 꼴)',
     "    grown = [p for p in files if counts['cur'].get(p) is not None\n"
     "             and ((d_sites > 0 and delta(p)[0] > 0) or (d_cases > 0 and delta(p)[1] > 0))]\n",
     "    grown = []\n", 'R1'),
    ('해석 실패를 TG4 전체 미실행으로',
     "    files = [p for p in files if p not in gone]\n",
     "    if broken:\n        ctx.notices.append('[info] TG4 미실행 — 해석 실패')\n        return []\n", 'A4'),
    ('해석 실패 파일의 이름 바꿈 짝을 남김(F6 전 꼴)',
     "    gone = (set(broken) | {new for new, old in got.pairs.items() if old in broken}\n",
     "    gone = (set(broken) | set()\n", 'A7'),
    ('점 사슬 import 를 맨 앞 이름으로만 풂(F3 전 꼴)', "        for cut in range(len(parts) - 1, 1, -1):\n",
     "        for cut in range(0):\n", 'F3'),
    ('--headless 하나로 자리(R-N6 전 꼴)', "    if flags and any(", "    if flags or any(", 'N10'),
    ('순환 도중의 «아님» 도 기억함(F15 전 꼴)', "        if result or not cut or not self._busy:", "        if True:", 'F15'),
]


def mutant_scripts(tmp, old, new):
    shutil.copytree(SCRIPTS, tmp / 'scripts', ignore=shutil.ignore_patterns('__pycache__', 'test'))
    shutil.copytree(SCRIPTS.parent / '.claude-plugin', tmp / '.claude-plugin')
    target = tmp / 'scripts/src/check_browser.py'
    text = target.read_text(encoding='utf-8')
    if text.count(old) != 1:
        return None
    target.write_text(text.replace(old, new), encoding='utf-8')
    return tmp / 'scripts'


def bundle_mut(tmp, only):
    by_name = {s[0]: s for s in SCENES}
    for index, (label, old, new, scene) in enumerate(MUTANTS):
        if only and scene not in only:
            continue
        scripts = mutant_scripts(tmp / ('mut%d' % index), old, new)
        if scripts is None:
            check('MUT %s — 되돌릴 자리가 check_browser.py 에 정확히 한 번' % label, False)
            continue
        if scene in by_name:
            code, out, found = play(tmp / ('mut%d-run' % index), by_name[scene], scripts)
            red = sorted(found) != sorted(by_name[scene][3])
        elif scene in CUSTOM:
            code, out, found, want = CUSTOM[scene][1](tmp / ('mut%d-run' % index), scripts)
            red = sorted(found) != sorted(want)
        elif scene == 'I5a':
            p, base = merge_scene(tmp / ('mut%d-run' % index), 'm', write('web_test/board/_merged_runner.cjs',
                                  "const { chromium } = require('playwright');", 'chromium.launch();'))
            code, out, found = tg4(p.root, base, '--only', 'tg4', scripts=scripts)
            red = bool(found)
        else:  # A4
            p, base = project(tmp / ('mut%d-run' % index) / 'a4')
            p.w('web_test/board/bad_runner.cjs', 'chromium.launch();', 'const re = /unterminated')
            p.w('tests/web/new_browser_test.py', 'def test_new(shared_chrome):', '    assert shared_chrome')
            code, out, found = tg4(p.root, base, '--only', 'tg4', scripts=scripts)
            red = not found
        check('MUT %s → %s 붉음' % (label, scene), red, out[-1200:])


def main():
    only = set(sys.argv[1:])
    with tempfile.TemporaryDirectory(prefix='web270-tg4-') as name:
        tmp = Path(name).resolve()
        bundle_scenes(tmp / 'scenes', only)
        bundle_merges(tmp / 'merges', only)
        bundle_custom(tmp / 'custom', only)
        bundle_notes(tmp / 'notes', only)
        old = release_scripts(tmp / 'release', RELEASE_261) if (not only or only & {'S1', 'S2', 'S3', 'S4', 'S5', 'K'}) else None
        if old is not None:
            bundle_same(tmp / 'same', only, old)
        bundle_counts(tmp / 'counts', only, old)
        bundle_mut(tmp / 'mut', only)
    print('2.7.0 TG4 픽스처: PASS %d / FAIL %d' % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
