"""2.2.5의 닫힌 계약 회귀 픽스처. 임시 git 사본만 변경한다."""
from pathlib import Path
import subprocess
import json
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.common import BackstopContext
from src.check_naming import run_naming
from src.check_tests import run_tests
from src.check_imports import run_imports

PASS = FAIL = 0

def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), '-c', 'user.name=t', '-c', 'user.email=t@t', *args], stderr=subprocess.DEVNULL).decode().strip()

def write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text + '\n')

def check(name, got, want):
    global PASS, FAIL
    ok = got == want
    PASS += ok
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name + ('' if ok else f' got={got!r} want={want!r}'))

def findings(root, base, family=run_tests):
    return family(BackstopContext.build(root, base, False))

def ids(root, base, family=run_tests):
    return {f.check_id for f in findings(root, base, family)}

with tempfile.TemporaryDirectory(prefix='web225-') as tmp:
    root = Path(tmp)
    write(root, 'web/__init__.py', '')
    git(root, 'init', '-q'); git(root, 'add', '.'); git(root, 'commit', '-qm', 'base')
    base = git(root, 'rev-parse', 'HEAD')
    view = 'web/application/sample/presentation_layer/view/sample_view.py'
    protocols = [
        ('현장 signup', 'from typing import Protocol\nclass _Signup(Protocol):\n    email: str\n    checked: bool'),
        ('현장 user info', 'from typing import Protocol\nclass _Info(Protocol):\n    label: str'),
        ('현장 screen', 'from typing import Protocol\nclass _Screen(Protocol):\n    entries: list[str]'),
        ('typing.Protocol', 'import typing\nclass _P(typing.Protocol):\n    field: str'),
        ('typing 별칭', 'from typing import Protocol as P\nclass _P(P):\n    field: str'),
        ('typing 모듈 별칭', 'import typing as t\nclass _P(t.Protocol):\n    field: str'),
        ('extensions 별칭', 'from typing_extensions import Protocol as P\nclass _P(P):\n    field: str'),
        ('extensions 모듈 별칭', 'import typing_extensions as t\nclass _P(t.Protocol):\n    field: str'),
    ]
    negatives = [
        ('별칭 재바인딩', 'from typing import Protocol as P\nP = object\nclass _P(P):\n    field: str'),
        ('모듈 재바인딩', 'import typing as t\nt = other\nclass _P(t.Protocol):\n    field: str'),
        ('조건부 import', 'if flag:\n    from typing import Protocol\nclass _P(Protocol):\n    field: str'),
        ('가짜 Protocol', 'from fake import Protocol\nclass _P(Protocol):\n    field: str'),
        ('추가 베이스', 'from typing import Protocol\nclass _P(Protocol, Mixin):\n    field: str'),
        ('metaclass', 'from typing import Protocol\nclass _P(Protocol, metaclass=Meta):\n    field: str'),
        ('annotation 호출', 'from typing import Protocol\nclass _P(Protocol):\n    field: make_type()'),
        ('annotation 대입식', 'from typing import Protocol\nclass _P(Protocol):\n    field: (kind := str)'),
        ('attribute annotation', 'from typing import Protocol\nclass _P(Protocol):\n    obj.field: str'),
        ('pass', 'from typing import Protocol\nclass _P(Protocol):\n    pass'),
        ('ellipsis', 'from typing import Protocol\nclass _P(Protocol):\n    ...'),
        ('docstring', 'from typing import Protocol\nclass _P(Protocol):\n    "doc"\n    field: str'),
        ('메서드', 'from typing import Protocol\nclass _P(Protocol):\n    def action(self): ...'),
        ('초깃값', 'from typing import Protocol\nclass _P(Protocol):\n    field: str = "x"'),
        ('데코레이터', 'from typing import Protocol\n@decorate\nclass _P(Protocol):\n    field: str'),
        ('일반 private', 'class _P:\n    field: str'),
        ('공개 Protocol', 'from typing import Protocol\nclass Public(Protocol):\n    field: str'),
        ('추가 함수', 'def extra():\n    pass'),
        ('AST 실패', 'from typing import Protocol\nclass _P(Protocol):\n    field: str\ninvalid !!!'),
    ]
    for blocked, cases in [(False, protocols), (True, negatives)]:
        for name, source in cases:
            write(root, view, source + '\ndef sample_view(request):\n    return request')
            check('NM17 ' + name, 'NM17' in ids(root, base, run_naming), blocked)
    for name, rebind in [
        ('wildcard import', 'from foreign import *'),
        ('match capture', 'match value:\n    case P:\n        pass'),
        ('match mapping', 'match value:\n    case {"key": P}:\n        pass'),
        ('match rest', 'match value:\n    case {**P}:\n        pass'),
        ('함수 default 대입식', 'def sample_view(request=(P := object)):\n    pass'),
        ('함수 decorator 대입식', '@(P := decorate)\ndef sample_view(request):\n    pass'),
        ('클래스 global 대입', 'class Holder:\n    global P\n    P = object'),
        ('중첩 클래스 global 대입', 'class Holder:\n    class Inner:\n        global P\n        P = object'),
    ]:
        write(root, view, 'from typing import Protocol as P\n' + rebind + '\nclass _P(P):\n    field: str')
        fs = findings(root, base, run_naming)
        check('NM17 무효화 ' + name, any(f.check_id == 'NM17' and '`_P`' in f.message for f in fs), True)
    for name, declaration in [
        ('함수 몸통은 미실행', 'def sample_view(request):\n    P = object'),
        ('클래스 local 바인딩', 'class Holder:\n    P = object'),
        ('메서드 global은 미실행', 'class Holder:\n    P = object\n    def method(self):\n        global P\n        P = object'),
    ]:
        write(root, view, 'from typing import Protocol as P\n' + declaration + '\nclass _P(P):\n    field: str')
        check('NM17 선언 실행 경계 ' + name, any(f.check_id == 'NM17' and '`_P`' in f.message for f in findings(root, base, run_naming)), False)
    write(root, view, 'class _P:\n    field: str')
    fs = [f for f in findings(root, base, run_naming) if f.check_id == 'NM17']
    check('NM17 사용자 허용 목록', any('private 필드 전용 Protocol' in f.message for f in fs), True)
    check('NM17 클래스 교정 안내', any('architecture-ui §2' in f.fix and '조건에 맞지 않음' in f.fix for f in fs), True)
    (root / view).unlink()
    for name, css, blocked in [
        ('아이콘 raw', '.icon-check {font-size:16px}', True),
        ('혼합 raw', '.icon-check, .text {font-size:16px}', True),
        ('아이콘 토큰', '.icon-check {font-size:var(--spacing-icon-sm)}', False),
        ('박스 직접 값', '.icon-check {width:16px;height:16px}', False),
    ]:
        write(root, 'web/static/application/sample/sample_view.css', css)
        check('NM10 ' + name, 'NM10' in ids(root, base, run_naming), blocked)
    write(root, 'web/application/landing/landing_router.py', 'HOME_URL: str = "/"')
    write(root, 'web/application/landing/landing_navigator.py', 'class LandingNavigator:\n    @staticmethod\n    def home_href():\n        from web.application.landing.landing_router import HOME_URL\n        return HOME_URL')
    nav = 'web/application/sample/sample_navigator.py'
    write(root, nav, 'class SampleNavigator:\n    def home_href(self):\n        from web.application.landing.landing_navigator import LandingNavigator\n        return LandingNavigator.home_href()')
    check('홈 navigator 사슬', 'IM5' in ids(root, base, run_imports), False)
    write(root, nav, 'from web.application.landing.landing_router import HOME_URL')
    check('타 BC router 직접 import', 'IM5' in ids(root, base, run_imports), True)

    test = 'tests/test_patch.py'
    tg2_cases = [
        ('기록 읽기', 'p = Path(".dddjango-web/run/fixture")\np.read_text()', True),
        ('기록 쓰기', 'open(".dddjango-web/run/result", "w").write("ok")', True),
        ('외부 기준판', 'BASELINE = Path("/Users/other/cache/base")\nBASELINE.read_bytes()', True),
        ('home 결합', 'p = Path.home() / ".cache" / "base"\np.read_text()', True),
        ('문자열 연결', 'p = ".dddjango" + "-web/run/data"\nopen(p).read()', True),
        ('Path 결합', 'p = Path(".dddjango-web") / "run" / "data"\np.write_text("x")', True),
        ('서버 실행', 'p = Path(".dddjango-web/fixture_server.py")\nsubprocess.Popen(["python", str(p)])', True),
        ('현장 ROOT BUILD', 'ROOT = Path(__file__).resolve().parents[1]\nBUILD = ROOT / ".dddjango-web/run"\nsubprocess.Popen(["python", str(BUILD / "fixture.py")])', True),
        ('현장 기준판 서버', 'BASELINE = Path("/Users/other/cache/base")\nwith fixture_server(BASELINE) as origin:\n    assert origin', True),
        ('조건식 with sink', 'BASELINE = Path("/Users/other/cache/base")\nwith fixture_server(BASELINE) if cond else other() as x:\n    assert x', True),
        ('조건식 대입 sink', 'P = Path(".dddjango-web/run/data")\nx = run_server(P) if c else None', True),
        ('조건식 else sink', 'P = Path(".dddjango-web/run/data")\nx = None if c else run_server(P)', True),
        ('조건식 조건 sink', 'P = Path(".dddjango-web/run/data")\nx = True if run_server(P) else False', True),
        ('조건식 안전 sink', 'P = Path("/Users/other/cache/base")\nx = run_server("tests/data") if c else run_server("tests/other")', False),
        ('BoolOp sink', 'P = Path(".dddjango-web/run/data")\nx = ready and run_server(P)', True),
        ('BoolOp 조건식 sink', 'P = Path(".dddjango-web/run/data")\nx = ready or (run_server(P) if c else None)', True),
        ('호출 인자 안 조건식 sink', 'P = Path(".dddjango-web/run/data")\nconsume(result=run_server(P) if c else None)', True),
        ('여러 with 항목 조건식 sink', 'P = Path(".dddjango-web/run/data")\nwith other() as first, fixture_server(P) if c else other() as second:\n    assert second', True),
        ('재검토② with 앞 항목 바인딩', 'from contextlib import nullcontext\np = Path(".dddjango-web/unused")\nwith nullcontext(Path("tests/data")) as p, p.open() as stream:\n    pass', False),
        ('재검토② async with 앞 항목 바인딩', 'p = Path(".dddjango-web/unused")\nasync def test_read():\n    async with context() as p, p.open() as stream:\n        pass', False),
        ('재검토② with 바인딩 전 표현식', 'p = Path(".dddjango-web/data")\nwith p.open() as p, other() as stream:\n    pass', True),
        ('BoolOp 안전 sink', 'P = Path(".dddjango-web/unused")\nx = ready and run_server("tests/data")', False),
        ('JS argv 기록 쓰기', 'JS = \'const [build] = process.argv.slice(1); fs.writeFileSync(build+"/result.json", "ok");\'\nsubprocess.run(["node", "-e", JS, ".dddjango-web/run"])', True),
        ('subprocess 인자', 'BASELINE = "/home/other/base"\nsubprocess.run(["node", "server.js", BASELINE])', True),
        ('단언 내부 I/O', 'assert Path("/Users/other/cache/base").read_text() == expected', True),
        ('JS 기록 쓰기', 'JS = \'fs.writeFileSync(".dddjango-web/result.json", "ok");\'\nsubprocess.run(["node", "-e", JS])', True),
        ('재검토③ harmless eval 주석', 'subprocess.run(["node", "-e", "/* harmless */ console.log(\'ok\')"])', False),
        ('재검토③ 동적 미사용 argv eval 주석', 'subprocess.run(["node", "-e", "/* harmless */ console.log(\'ok\')", dynamic()])', False),
        ('재검토③ 미사용 금지 argv', 'JS = "const [build, unused] = process.argv.slice(1); fs.readFileSync(build);"\nsubprocess.run(["node", "-e", JS, "tests/data", "/Users/hyun/cache/unused"])', False),
        ('재검토③ 사용 금지 argv', 'JS = "const [build] = process.argv.slice(1); fs.readFileSync(build);"\nsubprocess.run(["node", "-e", JS, "/Users/hyun/cache/used"])', True),
        ('JS 기준판 인자', 'JS = \'fs.readFileSync(process.argv[1]);\'\nBASE = "/home/other/cache/base"\nsubprocess.run(["node", "-e", JS, BASE])', True),
        ('시험 고정물 임시 기록', 'p = Path("tests/fixtures/data")\np.read_text()\n(tmp_path / "result").write_text("ok")', False),
        ('프로젝트 안 절대', f'Path({str(root / "tests/data")!r}).read_text()', False),
        ('결합 후 프로젝트 안 절대', f'(Path({str(root.parent)!r}) / {root.name!r} / "tests/data").read_text()', False),
        ('함수 인자 shadow', 'p = Path("/Users/other/cache/base")\ndef test_read(p):\n    p.read_text()', False),
        ('주석 docstring', '\'\'\'open("/Users/other/cache/base")\'\'\'\n# open(".dddjango-web/run")', False),
        ('URL', 'url = "https://example.com/a"\nassert url.endswith("/a")', False),
        ('검증 대상 경로', 'assert result == "/Users/other/cache/base"', False),
        ('도구 탐색', 'node = shutil.which("node")\nsubprocess.run([node, "server.js"])', False),
        ('정상 환경 시험', 'assert os.environ["DJANGO_SETTINGS_MODULE"] == "settings"', False),
        ('미실행 JS 문자열', 'JS = \'fs.writeFileSync(".dddjango-web/result", "ok");\'', False),
        ('JS 가짜 문자열 정규식', 'JS = \'const doc = "fs.readFileSync(\\"/home/cache/x\\")"; const re = /fs.readFileSync(".dddjango-web")/;\'\nsubprocess.run(["node", "-e", JS])', False),
        ('조건부 안전 대입', 'p = Path(".dddjango-web/unused")\ndef test_read():\n    if ready:\n        p = Path("tests/data")\n        p.read_text()', False),
        ('loop target 무효화', 'p = Path(".dddjango-web/unused")\nfor p in paths:\n    p.read_text()', False),
        ('import 무효화', 'p = Path(".dddjango-web/unused")\nimport other as p\np.read_text()', False),
        ('예외 바인딩 무효화', 'p = Path(".dddjango-web/unused")\ntry:\n    work()\nexcept Error as p:\n    p.read_text()', False),
        ('finally 재바인딩 무효화', 'p = Path(".dddjango-web/unused")\ntry:\n    p = Path("tests/data")\nfinally:\n    p.read_text()', False),
        ('분기 후 무효화', 'p = Path(".dddjango-web/unused")\nif ready:\n    p = dynamic()\np.read_text()', False),
        ('grep eval 제외', 'subprocess.run(["grep", "-e", \'fs.readFileSync(".dddjango-web/x")\'])', False),
    ]
    tg3_cases = [
        ('Python 단언 API', 'expect(page).to_have_screenshot("x.png")', True),
        ('Python camel API', 'expect(page).toHaveScreenshot("x.png")', True),
        ('Python sync 비교', 'def test_image():\n    before = page.screenshot()\n    after = page.screenshot()\n    assert before == after', True),
        ('Python async 비교', 'async def test_image():\n    before = await page.screenshot()\n    after = await page.screenshot()\n    assert before != after', True),
        ('Python snapshot screenshot', 'expect(page.screenshot()).toMatchSnapshot()', True),
        ('동일 screenshot 별칭 둘', 'def test_alias():\n    a = page.screenshot()\n    b = a\n    assert a == b', False),
        ('Python 함수 밖 결과 비교', 'a = page.screenshot()\nb = page.screenshot()\nassert a == b', False),
        ('JS 사건 원본', 'JS = "const before = await old.screenshot(); const after = await now.screenshot(); assert.ok(before.equals(after));"\nsubprocess.run(["node", "-e", JS])', True),
        ('재검토⑥ ASI 사건 새 파일', 'JS = """async function test_image() {\nconst before = await old.screenshot()\nconst after = await now.screenshot()\nassert.ok(before.equals(after))\n}"""\nsubprocess.run(["node", "-e", JS])', True),
        ('재검토⑥ 다음 선언 경계', 'JS = """const before = old.screenshot()\nconst after = now.screenshot(); Buffer.compare(before, after);"""\nsubprocess.run(["node", "-e", JS])', True),
        ('재검토⑥ 여러 줄 RHS 유지', 'JS = """const before = await old.screenshot(\n{ fullPage: true }\n)\nconst after = await now.screenshot()\nassert.ok(before.equals(after))"""\nsubprocess.run(["node", "-e", JS])', True),
        ('JS Buffer.compare', 'JS = "const a = await page.screenshot(); const b = await page.screenshot(); assert.equal(Buffer.compare(a,b),0);"\nsubprocess.run(["node", "-e", JS])', True),
        ('JS screenshot snapshot', 'JS = "const a = await page.screenshot(); expect(a).toMatchSnapshot();"\nsubprocess.run(["node", "-e", JS])', True),
        ('JS Buffer 문자열 snapshot', 'JS = "const a = page.screenshot()+text; expect(a).toMatchSnapshot();"\nsubprocess.run(["node", "-e", JS])', False),
        ('JS 동일 screenshot 별칭 둘', 'JS = "const a = page.screenshot(); const b = a; a.equals(b);"\nsubprocess.run(["node", "-e", JS])', False),
        ('JS screenshot을 인자로 전달한 결과', 'JS = "expect(encode(page.screenshot())).toMatchSnapshot();"\nsubprocess.run(["node", "-e", JS])', False),
        ('갈무리 자체', 'def test_capture():\n    page.screenshot(path="proof.png")', False),
        ('일반 bytes', 'def test_bytes():\n    before = b"old"\n    after = b"now"\n    assert before == after', False),
        ('재대입', 'def test_reassign():\n    a = page.screenshot()\n    a = b"x"\n    b = page.screenshot()\n    assert a == b', False),
        ('다른 함수 동명', 'def capture():\n    a = page.screenshot()\ndef test_other():\n    b = page.screenshot()\n    assert a == b', False),
        ('텍스트 snapshot', 'expect("text").toMatchSnapshot()', False),
        ('Python 주석 문자열', '# expect(page).to_have_screenshot()\nDOC = "expect(page).toHaveScreenshot()"', False),
        ('JS 문자열 정규식', 'JS = \'const doc = "expect(page).toHaveScreenshot()"; const re = /toHaveScreenshot()/; // before.equals(after)\'\nsubprocess.run(["node", "-e", JS])', False),
        ('JS 재대입', 'JS = "let a = await page.screenshot(); a = bytes; const b = await page.screenshot(); a.equals(b);"\nsubprocess.run(["node", "-e", JS])', False),
        ('JS 다른 블록', 'JS = "function one() { const a = page.screenshot(); } function two() { const b = page.screenshot(); a.equals(b); }"\nsubprocess.run(["node", "-e", JS])', False),
        ('JS 미실행', 'JS = "expect(page).toHaveScreenshot();"', False),
        ('Python 자기 비교', 'def test_self():\n    a = page.screenshot()\n    assert a == a\n    self.assertEqual(a, a)', False),
        ('Python 인접 chained 비교', 'def test_chain():\n    a = page.screenshot()\n    b = page.screenshot()\n    assert a == b"x" == b', False),
        ('Python chained 실제 비교', 'def test_chain():\n    a = page.screenshot()\n    b = page.screenshot()\n    assert b"x" == a != b', True),
        ('JS 자기 비교', 'JS = "const a = page.screenshot(); a.equals(a); Buffer.compare(a,a);"\nsubprocess.run(["node", "-e", JS])', False),
        ('grep eval 제외', 'subprocess.run(["grep", "-e", "toHaveScreenshot()", "input.txt"])', False),
        ('재검토④ 옵션 종료 뒤 eval 인자', 'subprocess.run(["node", "--", "tests/worker.js", "-e", "toHaveScreenshot()"])', False),
        ('재검토④ entry 뒤 eval 인자', 'subprocess.run(["node", "tests/worker.js", "--eval", "toHaveScreenshot()"])', False),
        ('재검토④ 옵션 값 뒤 실제 eval', 'subprocess.run(["node", "--require", "tests/preload.js", "--eval", "toHaveScreenshot()"])', True),
        ('which node 실행', 'node = shutil.which("node")\nsubprocess.run([node, "-e", "toHaveScreenshot()"] )', True),
        ('불명 실행기 제외', 'node = dynamic()\nsubprocess.run([node, "-e", "toHaveScreenshot()"] )', False),
        ('JS arrow 정규식', 'JS = "const pattern = () => /toHaveScreenshot()/;"\nsubprocess.run(["node", "-e", JS])', False),
        ('JS and 정규식', 'JS = "const pattern = ready && /toHaveScreenshot()/;"\nsubprocess.run(["node", "-e", JS])', False),
        ('JS or 정규식', 'JS = "const pattern = ready || /toHaveScreenshot()/;"\nsubprocess.run(["node", "-e", JS])', False),
        ('JS 조건 뒤 정규식', 'JS = "if (ready) /toHaveScreenshot()/.test(label);"\nsubprocess.run(["node", "-e", JS])', False),
        ('JS equality 뒤 정규식', 'JS = "const pattern = value === /toHaveScreenshot()/;"\nsubprocess.run(["node", "-e", JS])', False),
        ('JS 단항 plus 뒤 정규식', 'JS = "const pattern = +/toHaveScreenshot()/;"\nsubprocess.run(["node", "-e", JS])', False),
        ('JS 나눗셈 실제 호출', 'JS = "const value = 1 / toHaveScreenshot();"\nsubprocess.run(["node", "-e", JS])', True),
        ('Python 예외 screenshot 무효화', 'def test_exception():\n    a = page.screenshot()\n    b = page.screenshot()\n    try:\n        work()\n    except Error as a:\n        assert a == b', False),
        ('Python 패턴 screenshot 무효화', 'def test_pattern():\n    a = page.screenshot()\n    b = page.screenshot()\n    match value:\n        case a:\n            assert a == b', False),
    ]
    for keyword, context in [
        ('typeof', 'const kind = typeof REGEX;'), ('void', 'void REGEX;'), ('delete', 'delete REGEX;'),
        ('in', 'const found = "x" in REGEX;'), ('instanceof', 'const found = obj instanceof REGEX;'),
        ('return', 'function f() { return REGEX; }'), ('throw', 'throw REGEX;'),
        ('case', 'switch (x) { case REGEX: break; }'), ('yield', 'function* f() { yield REGEX; }'),
        ('await', 'async function f() { await REGEX; }'),
    ]:
        tg3_cases.append(('재검토⑤ ' + keyword + ' 뒤 정규식', 'JS = ' + repr(context.replace('REGEX', '/toHaveScreenshot()/')) + '\nsubprocess.run(["node", "-e", JS])', False))
    for cid, cases in [('TG2', tg2_cases), ('TG3', tg3_cases)]:
        for name, source, blocked in cases:
            write(root, test, source)
            check(cid + ' ' + name, cid in ids(root, base), blocked)
    bad = 'Path(".dddjango-web/data").read_text()\nexpect(page).to_have_screenshot()'
    write(root, test, bad)
    fs = [f for f in findings(root, base) if f.check_id in {'TG2', 'TG3'}]
    check('TG root 상대 발견', len(fs) == 2 and all(f.root_rel and f.path == test for f in fs), True)
    out = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / 'backstop.py'), str(root), '--diff-base', base, '--slice-end'], capture_output=True, text=True).stdout
    check('TG2 slice-end', '[TG2] BLOCKER' in out, True)
    check('TG3 slice-end', '[TG3] BLOCKER' in out, True)
    (root / test).unlink()
    for rel in ['web_test/application/x/x_test.py', 'test/test_x.py', 'tests/conftest.py', 'tests/_support.py', 'tests/helpers.py']:
        write(root, rel, bad)
        check('시험 지원 범위 ' + rel, 'TG2' in ids(root, base), True)
        (root / rel).unlink()
    write(root, 'pytest.ini', '[pytest]\ntestpaths = quality\npython_files = check_*.py tests.py')
    for rel, blocked in [('quality/check_home.py', True), ('quality/tests.py', True), ('quality/_support.py', True), ('quality/model.py', False)]:
        write(root, rel, bad)
        check('pytest 설정 범위 ' + rel, 'TG2' in ids(root, base), blocked)
        (root / rel).unlink()
    git(root, 'tag', 'g0-base', base)
    write(root, 'custom/flow_case.py', bad)
    for snapshot, diff_base in [(base, base), (base, base[:10]), (base, 'g0-base'), (base[:10], base), ('g0-base', base)]:
        write(root, '.dddjango-web/run/build-state.json', json.dumps({'git_snapshot': snapshot, 'test_command': 'pytest custom/flow_case.py --ds=settings'}))
        check('G0 관례 밖 경로 ' + snapshot[:10] + '/' + diff_base[:10], 'TG2' in ids(root, diff_base), True)
    (root / 'custom/flow_case.py').unlink()
    write(root, 'tests/test_existing.py', bad)
    git(root, 'add', '.'); git(root, 'commit', '-qm', 'host')
    host = git(root, 'rev-parse', 'HEAD')
    write(root, 'tests/test_normal.py', 'assert label == "home"')
    check('정상 변경과 기존 금지 의존 면책', ids(root, host), set())
    write(root, 'tests/test_existing.py', bad + '\nassert True')
    check('무관한 추가 줄 기존 시험', ids(root, host), set())
    git(root, 'add', '.')
    check('staged 무관한 추가 줄', ids(root, host), set())
    git(root, 'commit', '-qm', 'slice')
    check('커밋된 무관한 추가 줄', ids(root, host), set())
    git(root, 'mv', 'tests/test_existing.py', 'tests/test_renamed.py')
    check('순수 rename 새 경로', any(f.path == 'tests/test_renamed.py' for f in findings(root, host)), False)
    (root / 'tests/test_renamed.py').unlink()
    check('삭제 제외', ids(root, host), set())
    write(root, '.gitignore', 'tests/test_ignored.py')
    write(root, 'tests/test_ignored.py', bad)
    check('무시 미추적 제외', ids(root, host), set())
    ctx = BackstopContext.build(root, None, False)
    check('기준점 없음 미실행', {f.check_id for f in run_tests(ctx)}, set())
    check('기준점 없음 범위 고지', any('TG2' in n and '범위 미확정' in n for n in ctx.notices), True)
    check('ctx.files 불확장', all(not f.startswith(('tests/', 'web_test/')) for f in ctx.files), True)

with tempfile.TemporaryDirectory(prefix='web225-state-') as tmp:
    root = Path(tmp)
    write(root, 'web/__init__.py', '')
    git(root, 'init', '-q'); git(root, 'add', '.'); git(root, 'commit', '-qm', 'base')
    base = git(root, 'rev-parse', 'HEAD')
    test = 'web_test/home/home/view/home_browser_test.py'
    regression_source = '\n'.join(f'Path(".dddjango-web/run/data{i}").read_text()' for i in range(8)) + '\nexpect(page).to_have_screenshot()'
    write(root, test, regression_source)
    states = [
        ('해소 불가 snapshot', '00-old', json.dumps({'git_snapshot': '8cc85252503008fd77426247c4f144db05092eab', 'test_command': 'pytest custom/foreign_case.py'})),
        ('깨진 JSON', '01-broken', '{'),
        ('snapshot 필드 없음', '02-missing', json.dumps({'test_command': 'pytest custom/foreign_case.py'})),
        ('재검토⑦ null command', '04-null', json.dumps({'git_snapshot': base, 'test_command': None})),
        ('재검토⑦ 비문자열 command', '05-nonstring', json.dumps({'git_snapshot': base, 'test_command': ['pytest']})),
        ('재검토⑦ 깨진 quoting', '06-quoting', json.dumps({'git_snapshot': base, 'test_command': 'pytest "custom/flow_case.py'})),
    ]
    def state_counts(diff_base=base, with_paths=False):
        ctx = BackstopContext.build(root, diff_base, False)
        try:
            fs = run_tests(ctx)
        except (TypeError, AttributeError, ValueError) as error:
            return (type(error).__name__, str(error))
        counts = (sum(f.check_id == 'TG2' for f in fs), sum(f.check_id == 'TG3' for f in fs))
        return counts + (({f.path for f in fs},) if with_paths else ()) + (bool(ctx.notices),)
    for name, lane, source in states:
        state_path = '.dddjango-web/' + lane + '/build-state.json'
        write(root, state_path, source)
        check('G0 기록 격리 ' + name, state_counts(), (8, 1, False))
        (root / state_path).unlink()
    for name, lane, source in states:
        write(root, '.dddjango-web/' + lane + '/build-state.json', source)
    check('G0 불량 기록 6종 공존 새 시험 TG2·TG3', state_counts(), (8, 1, False))
    # 디렉터리를 파일 자리에 둬 권한·실행 사용자에 무관하게 read_text OSError를 재현한다.
    (root / '.dddjango-web/03-unreadable/build-state.json').mkdir(parents=True)
    check('G0 기록 읽기 실패 새 시험 TG2·TG3', state_counts(), (8, 1, False))
    (root / test).unlink()
    write(root, 'custom/flow_case.py', regression_source)
    write(root, 'custom/foreign_case.py', regression_source)
    git(root, 'tag', 'g0-base', base)
    git(root, 'commit', '--allow-empty', '-qm', 'other snapshot')
    other = git(root, 'rev-parse', 'HEAD')
    write(root, '.dddjango-web/10-current/build-state.json', json.dumps({'git_snapshot': 'g0-base', 'test_command': 'pytest custom/flow_case.py --ds=settings'}))
    write(root, '.dddjango-web/11-other/build-state.json', json.dumps({'git_snapshot': other, 'test_command': 'pytest custom/foreign_case.py --ds=settings'}))
    check('G0 불량 기록 공존 같은 commit 명시 경로 수집', state_counts(base[:10], True), (8, 1, {'custom/flow_case.py'}, False))

chain = ('p = Path(".dddjango-web/data")\nq = p\ndef test_image():\n'
         '    q.read_text()\n    a = page.screenshot()\n    b = page.screenshot()\n    assert a == b')

def gate_case(name, before, after, want, operation=None):
    with tempfile.TemporaryDirectory(prefix='web225-gate-') as tmp:
        root = Path(tmp)
        write(root, 'web/__init__.py', '')
        write(root, 'tests/test_chain.py', before)
        git(root, 'init', '-q'); git(root, 'add', '.'); git(root, 'commit', '-qm', 'base')
        base = git(root, 'rev-parse', 'HEAD')
        write(root, 'tests/test_chain.py', after)
        if operation:
            operation(root)
        check('줄 게이트 ' + name, ids(root, base), want)

for assertion in ('assertEqual', 'assertNotEqual'):
    image_call = ('def test_image(self):\n    a = page.screenshot()\n    b = page.screenshot()\n'
                  '    self.' + assertion + '(\n        a,\n        b,\n        msg="old",\n    )')
    gate_case('재검토① ' + assertion + ' msg만 수정', image_call, image_call.replace('msg="old"', 'msg="new"'), set())
    gate_case('재검토① ' + assertion + ' 비교 입력 수정', image_call, image_call.replace('        a,', '        page.screenshot(),'), {'TG3'})
    gate_case('재검토① ' + assertion + ' 생성 수정', image_call, image_call.replace('a = page.screenshot()', 'a = old.screenshot()'), {'TG3'})
    gate_case('재검토① ' + assertion + ' 함수 위치 수정', image_call, image_call.replace('self.' + assertion, 'other.' + assertion), {'TG3'})
    gate_case('재검토① ' + assertion + ' 새 파일', '', image_call, {'TG3'})

for name, after, want in [
    ('무관한 앞줄 삽입', '# unrelated\n' + chain, set()),
    ('무관한 끝줄 수정', chain + '\nassert True', set()),
    ('생성 줄 수정', chain.replace('data', 'changed'), {'TG2'}),
    ('중간 대입 수정', chain.replace('q = p', 'q = str(p)'), {'TG2'}),
    ('sink 수정', chain.replace('q.read_text()', 'q.read_bytes()'), {'TG2'}),
    ('screenshot 생성 수정', chain.replace('a = page.screenshot()', 'a = old.screenshot()'), {'TG3'}),
    ('비교 수정', chain.replace('a == b', 'a != b'), {'TG3'}),
    ('함수 선언만 수정', chain.replace('test_image', 'test_other'), set()),
    ('클래스 선언만 수정', 'class Changed:\n' + '\n'.join('    ' + s for s in chain.splitlines()), set()),
]:
    if name == '클래스 선언만 수정':
        before = after.replace('Changed', 'Original')
    else:
        before = chain
    for state, operation in [('unstaged', None), ('staged', lambda r: git(r, 'add', '.')),
                             ('committed', lambda r: (git(r, 'add', '.'), git(r, 'commit', '-qm', 'slice')))]:
        gate_case(name + ' ' + state, before, after, want, operation)

gate_case('안전한 재대입 삭제', chain.replace('q = p', 'p = Path("tests/data")\nq = p'), chain, {'TG2'})
gate_case('출처 무효화 삭제', chain.replace('q = p', 'import other as p\nq = p'), chain, {'TG2'})
gate_case('wildcard 출처 무효화 삭제', chain.replace('q = p', 'from foreign import *\nq = p'), chain, {'TG2'})
gate_case('screenshot 재대입 삭제', chain.replace('    b = page.screenshot()', '    a = b"safe"\n    b = page.screenshot()'), chain, {'TG3'})
gate_case('무관한 삭제', '# unrelated\n' + chain, chain, set())
two_inputs = 'a = Path(".dddjango-web/a")\nb = Path(".dddjango-web/b")\nshutil.copy(a, b)'
gate_case('두 입력 중 안전 대입 삭제', two_inputs.replace('shutil.copy', 'b = Path("tests/data")\nshutil.copy'), two_inputs, {'TG2'})
multiline_process = ('NODE: str = "/opt/homebrew/bin/node"\n'
                     'def test_run():\n'
                     '    process = subprocess.run(\n'
                     '        [NODE, x],\n'
                     '        input=json.dumps({\n'
                     '            "initial": document,\n'
                     '        }),\n'
                     '        text=True,\n'
                     '    )')
gate_case('TG2 여러 줄 호출 input JSON만 추가', multiline_process,
          multiline_process.replace('"initial": document,', '"initial": document,\n            "navigation_history": history,'), set())
gate_case('TG2 여러 줄 호출 다른 키워드만 수정', multiline_process,
          multiline_process.replace('text=True', 'text=False'), set())
gate_case('TG2 여러 줄 호출 금지 인자 수정', multiline_process,
          multiline_process.replace('[NODE, x]', '[NODE, y]'), {'TG2'})
gate_case('TG2 여러 줄 호출 NODE 정의 수정', multiline_process,
          multiline_process.replace('/opt/homebrew/bin/node', '/usr/local/bin/node'), {'TG2'})
gate_case('TG2 여러 줄 호출 함수 이름 수정', multiline_process,
          multiline_process.replace('subprocess.run(', 'subprocess.check_output('), {'TG2'})
with tempfile.TemporaryDirectory(prefix='web225-tg2-scenes-') as tmp:
    root = Path(tmp)
    write(root, 'web/__init__.py', '')
    git(root, 'init', '-q'); git(root, 'add', '.'); git(root, 'commit', '-qm', 'base')
    base = git(root, 'rev-parse', 'HEAD')
    test = 'web_test/home/home/view/home_browser_test.py'
    rows = [''] * 339
    rows[0] = 'from pathlib import Path'
    rows[17] = 'BASELINE: Path = Path("/Users/hyun/.cache/codex-consultation-6-3-23/baseline-1a82c8cb-vy25661z")'
    rows[330] = 'def test_behavior(behavior):'
    rows[337] = '    with fixture_server(BASELINE) if behavior == "B13" else _empty_origin() as before:'
    rows[338] = '        assert before'
    write(root, test, '\n'.join(rows))
    check('TG2 사건 조건식 새 파일 18→338', [(f.path, f.line) for f in findings(root, base) if f.check_id == 'TG2'], [(test, 338)])
    (root / test).unlink()
    write(root, 'tests/test_multiline.py', multiline_process)
    check('TG2 여러 줄 호출 새 파일', [(f.path, f.line) for f in findings(root, base) if f.check_id == 'TG2'], [('tests/test_multiline.py', 3)])
gate_case('순수 rename git 설정 off', chain, chain, set(), lambda r: (git(r, 'config', 'diff.renames', 'false'), git(r, 'mv', 'tests/test_chain.py', 'tests/test_moved.py')))
gate_case('rename 추가 사슬 줄', chain, chain.replace('data', 'changed'), {'TG2'}, lambda r: git(r, 'mv', 'tests/test_chain.py', 'tests/test_moved.py'))
gate_case('D/A 동일 blob 이동', chain, chain, set(), lambda r: (write(r, 'tests/test_moved.py', chain), (r / 'tests/test_chain.py').unlink()))
gate_case('copy 새 시험', chain, chain, {'TG2', 'TG3'}, lambda r: write(r, 'tests/test_copy.py', chain))
gate_case('기준판 파일 미추적 무관 수정', chain, chain + '\nassert True', set(), lambda r: git(r, 'rm', '--cached', 'tests/test_chain.py'))
gate_case('기준판 파일 미추적 사슬 수정', chain, chain.replace('data', 'changed'), {'TG2'}, lambda r: git(r, 'rm', '--cached', 'tests/test_chain.py'))
gate_case('기준판 파일 미추적 후 ignore 사슬 수정', chain, chain.replace('data', 'changed'), {'TG2'}, lambda r: (write(r, '.gitignore', 'tests/test_chain.py'), git(r, 'rm', '--cached', 'tests/test_chain.py')))
with tempfile.TemporaryDirectory(prefix='web225-outside-') as tmp:
    root = Path(tmp)
    write(root, 'web/__init__.py', '')
    write(root, 'custom/flow_case.py', chain)
    git(root, 'init', '-q'); git(root, 'add', '.'); git(root, 'commit', '-qm', 'base')
    base = git(root, 'rev-parse', 'HEAD')
    (root / 'tests').mkdir()
    git(root, 'mv', 'custom/flow_case.py', 'tests/test_chain.py')
    check('줄 게이트 시험 밖 rename 편입', ids(root, base), {'TG2', 'TG3'})
    ctx = BackstopContext.build(root, base, False)
    ctx.diff_base = 'missing-ref'
    check('잘못된 기준점 미실행', {f.check_id for f in run_tests(ctx)}, set())
    check('잘못된 기준점 범위 고지', any('범위 미확정' in n for n in ctx.notices), True)

js = 'JS = "const a = page.screenshot();\\nconst b = page.screenshot();\\na.equals(b);"\nCODE = JS\nsubprocess.run(["node", "-e", CODE])'
gate_case('JS 무관한 앞줄 이동', js, '# unrelated\n' + js, set())
gate_case('JS 문자열 생성', js, js.replace('page.screenshot()', 'old.screenshot()', 1), {'TG3'})
gate_case('JS 중간 대입', js, js.replace('CODE = JS', 'CODE = str(JS)'), {'TG3'})
gate_case('JS 실행 인자', js, js.replace('"-e", CODE', '"--eval", CODE'), {'TG3'})
multiline_js = 'JS = """const a = page.screenshot();\nconst b = page.screenshot();\nconst label = "old";\na.equals(b);"""\nsubprocess.run(["node", "-e", JS])'
gate_case('JS 내용 무관한 줄 수정', multiline_js, multiline_js.replace('"old"', '"new"'), set())
js_path = 'JS = """let p = ".dddjango-web/x";\np = "tests/data";\nfs.readFileSync(p);"""\nsubprocess.run(["node", "-e", JS])'
gate_case('JS 안전 대입 삭제', js_path, js_path.replace('p = "tests/data";\n', ''), {'TG2'})
js_two_sinks = 'JS = """let p = ".dddjango-web/x";\nlet q = ".dddjango-web/y";\np = "tests/data";\nfs.readFileSync(p); fs.readFileSync(q);"""\nsubprocess.run(["node", "-e", JS])'
gate_case('JS 같은 행 두 sink 안전 대입 삭제', js_two_sinks, js_two_sinks.replace('p = "tests/data";\n', ''), {'TG2'})
js_argv = 'BASE = ".dddjango-web/data"\nJS = """\nconst [build] = process.argv.slice(1);\nfs.readFileSync(build);\n"""\nsubprocess.run(["node", "-e", JS, BASE])'
gate_case('JS argv 분해 중간 대입 수정', js_argv, js_argv.replace('const [build]', 'let [build]'), {'TG2'})
js_multiline_process = ('JS = """const p = ".dddjango-web/data";\nfs.readFileSync(p);"""\n'
                        'subprocess.run(\n'
                        '    ["node", "-e", JS],\n'
                        '    input="old",\n'
                        '    text=True,\n'
                        ')')
gate_case('TG2 JS 추출 호출 다른 인자만 수정', js_multiline_process,
          js_multiline_process.replace('input="old"', 'input="new"'), set())
gate_case('TG2 JS 추출 호출 코드 인자 수정', js_multiline_process,
          js_multiline_process.replace('"-e", JS', '"--eval", JS'), {'TG2'})
js_multiline_sink = ('JS = """const p = ".dddjango-web/data";\n'
                     'fs.writeFileSync(\n'
                     '    p,\n'
                     '    "old"\n'
                     ');"""\nsubprocess.run(["node", "-e", JS])')
gate_case('TG2 JS 여러 줄 sink 다른 인자만 수정', js_multiline_sink,
          js_multiline_sink.replace('"old"', '"new"'), set())
gate_case('TG2 JS 여러 줄 sink 금지 인자 수정', js_multiline_sink,
          js_multiline_sink.replace('    p,', '    p + "/result",'), {'TG2'})
js_unused_argv = ('BASE = ".dddjango-web/data"\n'
                  'UNUSED = "tests/old"\n'
                  'JS = "const [build, unused] = process.argv.slice(1); fs.readFileSync(build);"\n'
                  'subprocess.run(["node", "-e", JS, BASE, UNUSED])')
gate_case('TG2 JS 미사용 argv 정의 수정', js_unused_argv,
          js_unused_argv.replace('tests/old', 'tests/new'), set())
gate_case('TG2 JS 사용 argv 정의 수정', js_unused_argv,
          js_unused_argv.replace('.dddjango-web/data', '.dddjango-web/changed'), {'TG2'})
js_forbidden_unused = js_unused_argv.replace('tests/old', '/Users/hyun/cache/old')
gate_case('재검토③ 미사용 금지 argv 값만 수정', js_forbidden_unused,
          js_forbidden_unused.replace('/Users/hyun/cache/old', '/Users/hyun/cache/new'), set())
with tempfile.TemporaryDirectory(prefix='web225-map-') as tmp:
    root = Path(tmp)
    write(root, 'web/__init__.py', '')
    git(root, 'init', '-q'); git(root, 'add', '.'); git(root, 'commit', '-qm', 'base')
    base = git(root, 'rev-parse', 'HEAD')
    for name, source, line in [
        ('이스케이프 개행', js, 1),
        ('문자열 결합', 'A = "const a = page.screenshot();\\n"\nB = "const b = page.screenshot();\\n"\nJS = A + B + "a.equals(b);"\nsubprocess.run(["node", "-e", JS])', 3),
        ('삼중 문자열', 'JS = """const a = page.screenshot();\nconst b = page.screenshot();\na.equals(b);"""\nsubprocess.run(["node", "-e", JS])', 3),
    ]:
        write(root, 'tests/test_js.py', source)
        check('JS 원본 좌표 ' + name, [f.line for f in findings(root, base) if f.check_id == 'TG3'], [line])
print(f'2.2.5 픽스처: PASS {PASS} / FAIL {FAIL}')
sys.exit(bool(FAIL))
