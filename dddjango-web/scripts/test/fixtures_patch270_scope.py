#!/usr/bin/env python3
"""2.7.0 시험 범위(러너 모드 `--test-scope`) 회귀 — 넓이 · 소비자 · `--since` 줄 · 프로젝트 전체 필요 · 사용 오류.

장면마다 임시 git 저장소에 합성 프로젝트를 만들고 build-state.json 의 test_command(· test_web_paths)를 둔 뒤
`backstop.py <루트> --test-scope <산출물 폴더> [--since <커밋>]` 출력(exit · `[test-scope]` 줄)을 본다 — 시험은 돌지 않는다.
  W  넓이 — 경로 없음 · 빠진 web 시험 경로 · 표식 짝 · 판정 불가 꼴 · 표 밖 선택지 · 러너 앞부분 · 기록 폴더 · web/ 없는 첫 실행 ·
        고르는 선택지 · 깊은 tests/web · build-state 오류 · pytest 설정 첫 파일 · 셸이 풀 낱말(앞 대입 · $ · ~ · 글롭) ·
        중괄호 펼침 · 긴 이름 선택지 · 설정 따옴표 오류 · web 시험 경로 조상 · 자손 · 산출물 폴더 자리
  C  소비자 — import · 점 경로 · 경로 글자 · web 전체를 읽음 · 한 걸음 · settings · 루트 urls 제외 · 기록 폴더 · 걸리지 않는 꼴
  S  --since — 닫힘 미러 · 템플릿 이름 · 공용 부품 · 루트 셸(= web 시험 전체) · import 로만 부르는 W 시험 · 미추적 W 시험 ·
        web 전체 소비자 · 바뀐 지원 모듈 · 계층 중 시험 · G2 더할 시험 · fail-fast 떼기 · 일꾼 · 앞 대입 단계 줄 · W 밖 지원 모듈 ·
        conftest(그 지원 모듈을 import 하는 conftest 포함) · 사용자 git 설정(grep.fullName · 전역 속성 -diff) · 병합 유입
        (승인 병합이 상류판 그대로 들인 경로만 뺌 · 충돌 해소 · 미승인 · 목록 오류는 셈)
  P  프로젝트 전체 필요 — web 밖 파일 · 전역 진입점(표준 · settings 가 부르는 web. 모듈) · 진입점 아래 BC 파일 · settings 없음 ·
        루트 conftest · 문서 · 기록 폴더 · web 시험 경로 아래 파일 · 승인 병합 유입 · 하위 폴더 루트 · 한글 파일 이름
  U  사용 오류 · MUT 고침 되돌림 변형(이 판 scripts 를 임시 폴더에 복사해 한 자리를 되돌리면 지정 장면이 붉다)
임시 git 저장소만 만들고 끝나면 지운다(네트워크 · 브라우저 · 시험 실행 없음). 인자로 묶음 글자(W C S P U)를 주면 그 묶음만 돈다."""
import json
import re
import shlex
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

TEST = Path(__file__).resolve().parent
SCRIPTS = TEST.parent
sys.path.insert(0, str(TEST))
import fixtures_patch230 as fx  # noqa: E402
from fixtures_patch230 import Proj, git, mkbc, mkstd, run_script  # noqa: E402

PASS = FAIL = 0
RUN = '.dddjango-web/20261020-0000-scope'
ORDER_PAGE = 'web/application/order/presentation_layer/view/order_list_view.html'
ORDER_VM = 'web/application/order/application_layer/view_model/order_list_vm.py'
SHELL = 'web/root/scaffold/view/root_view.html'
BUTTON = 'web/design_system/component/button/primary_button.html'


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok and detail:
        print('    ' + str(detail).replace('\n', '\n    ')[:2400])


def state(p, command, extra=None, run=RUN):
    data = {'test_command': command}
    if extra is not None:
        data['test_web_paths'] = extra
    p.w(run + '/build-state.json', json.dumps(data, ensure_ascii=False))


def scope(root, *args, scripts=SCRIPTS, run=RUN):
    return run_script(scripts / 'backstop.py', root, '--test-scope', run, *args)


def lines(out, head):
    return [line for line in out.splitlines() if line.startswith('[test-scope] ' + head)]


def has(out, text):
    return any(text in line for line in out.splitlines())


@contextmanager
def user_gitconfig(folder, *pairs):
    """도구 실행 환경에만 임시 전역 git 설정(이름 · 메일 + pairs)을 건다 — 시스템 설정 끔 · 끝나면 되돌린다(실행하는 사람의
    전역 설정은 읽지도 바꾸지도 않는다)."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'gitconfig'
    text = ['[user]', '\tname = t', '\temail = t@t']
    for key, value in pairs:
        section, _dot, leaf = key.partition('.')
        text += ['[%s]' % section, '\t%s = %s' % (leaf, value)]
    path.write_text('\n'.join(text) + '\n', encoding='utf-8')
    saved = {k: fx.ENV.get(k) for k in ('GIT_CONFIG_GLOBAL', 'GIT_CONFIG_NOSYSTEM')}
    fx.ENV.update(GIT_CONFIG_GLOBAL=str(path), GIT_CONFIG_NOSYSTEM='1')
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                fx.ENV.pop(k, None)
            else:
                fx.ENV[k] = v


def base_project(root, with_tests_web=True):
    """표준 트리 + tests/web 시험 하나 + 커밋 → (Proj, BASE)."""
    p = mkstd(root)
    if with_tests_web:
        p.w('tests/web/test_pages.py', 'def test_pages() -> None:', '    assert True')
    p.w('tests/__init__.py', '')
    return p, p.commit('base')


# ---------------------------------------------------------------- W 넓이


def bundle_w(tmp):
    p, _base = base_project(tmp / 'w')
    root = p.root
    ok_cmd = 'pytest web_test tests/web --import-mode=importlib --ds=config.settings'
    cases = [
        ('W1 경로 없음 + testpaths 밖 → 넓음', 'pytest --ds=config.settings', None, 2, '넓음 — 단계 1 경로 tests(testpaths)',
         lambda: p.w('pytest.ini', '[pytest]', 'testpaths = tests')),
        ('W2 web_test 만(tests/web 있음) → 좁음', 'pytest web_test --ds=config.settings', None, 2,
         '좁음 — 빠진 web 시험 경로 tests/web(모으는 단계 없음)', None),
        ('W3 web_test tests/web → 0 · 단계 꼴', ok_cmd, None, 0,
         '단계 1: pytest {경로} --import-mode=importlib --ds=config.settings', None),
        ('W4 -m 짝 두 단계 → 0', 'pytest -m postgresql web_test tests/web && pytest -m "not postgresql" web_test tests/web',
         None, 0, '판정 — web 시험 경로만', None),
        ('W4b 한 단계에 tests/web 빠짐 → 좁음', 'pytest -m postgresql web_test tests/web && pytest -m "not postgresql" web_test',
         None, 2, "좁음 — 빠진 web 시험 경로 tests/web(표식 'postgresql' 만", None),
        ('W5 make test-web → 판정 불가', 'make test-web', None, 1, '판정 불가 — 단계 1 이 make', None),
        ('W6a 파이프 → 판정 불가', ok_cmd + ' | tee log', None, 1, '파이프 · 재지정', None),
        ('W6b 재지정 → 판정 불가', ok_cmd + ' > log', None, 1, '파이프 · 재지정', None),
        ('W6c 명령 치환 → 판정 불가', 'pytest $(cat paths)', None, 1, '명령 치환', None),
        ('W6d --pyargs → 판정 불가', ok_cmd + ' --pyargs', None, 1, '--pyargs', None),
        ('W6e -o testpaths → 판정 불가', ok_cmd + ' -o testpaths=x', None, 1, '-o testpaths', None),
        ('W6f --rootdir → 판정 불가', ok_cmd + ' --rootdir .', None, 1, '--rootdir', None),
        ('W7a 표 밖 선택지 뒤 실재 경로 → 판정 불가', 'pytest --foo docs web_test tests/web', None, 1,
         '뜻 모를 선택지 --foo 뒤 프로젝트 안 경로 docs', lambda: p.w('docs/readme.md', 'x')),
        ('W7b --postgresql-exec 값 → 0', 'pytest --postgresql-exec /opt/x/pg_ctl web_test tests/web', None, 0,
         '판정 — web 시험 경로만', None),
        ('W8a test_web_paths ui_tests → 0', 'pytest web_test tests/web ui_tests', ['ui_tests'], 0,
         'web 시험 경로: web_test(시험 파일 1) · tests/web(시험 파일 1) · ui_tests(시험 파일 1)',
         lambda: p.w('ui_tests/test_ui.py', 'def test_ui() -> None:', '    assert True')),
        ('W8b test_web_paths 없는 경로 → 판정 불가', ok_cmd, ['nowhere'], 1, 'test_web_paths 경로 없음 nowhere', None),
        ('W8c test_web_paths 기록 폴더 안 → 판정 불가', ok_cmd, ['.dddjango-web/x'], 1, '기록 폴더 안',
         lambda: p.w('.dddjango-web/x/t.py', 'x = 1')),
        ('W9a 러너 앞부분(env · 감싸개 · uv run) → 0', 'env X=1 ./run.sh uv run pytest web_test tests/web', None, 0,
         '단계 1: env X=1 ./run.sh uv run pytest {경로}', None),
        ('W9b python -m pytest → 0', 'python -m pytest web_test tests/web', None, 0, '단계 1: python -m pytest {경로}', None),
        ('W9c (F1) 앞 이름=값 대입 → 0 · 단계 꼴에서도 대입으로', 'PYTEST_ADDOPTS="-p no:cacheprovider" pytest web_test tests/web',
         None, 0, "단계 1: PYTEST_ADDOPTS='-p no:cacheprovider' pytest {경로}", None),
        ('W9d (F1) $ 변수 낱말 → 판정 불가', 'pytest --postgresql-exec $PG/bin/pg_ctl web_test tests/web', None, 1,
         '셸이 풀 낱말', None),
        ('W9e (F1) 맨 앞 ~ → 판정 불가', '~/.venv/bin/pytest web_test tests/web', None, 1, '셸이 풀 낱말', None),
        ('W9f (F1) 글롭 낱말 → 판정 불가', ok_cmd + ' --ignore-glob=*.tmp', None, 1, '셸이 풀 낱말', None),
        ('W9g (F1) 대입 값의 ~ → 판정 불가', 'X=~/y pytest web_test tests/web', None, 1, '셸이 풀 낱말', None),
        ('W9h (A-N1) 중괄호 펼침 낱말 → 판정 불가', ok_cmd + ' --ignore=node_modules/{a,b}', None, 1, '셸이 풀 낱말', None),
        ('W16a (F8) -r 값 띄어 씀 → 0', 'pytest -r F web_test tests/web', None, 0, '판정 — web 시험 경로만', None),
        ('W16b (F8) --numprocesses 값 띄어 씀 → 0', 'pytest --numprocesses 4 web_test tests/web', None, 0,
         '판정 — web 시험 경로만', None),
        ('W16c (F8) --override-ini=testpaths → 판정 불가', ok_cmd + ' --override-ini=testpaths=x', None, 1,
         '--override-ini testpaths', None),
        ('W16d (F8) --sw-skip → 좁음', ok_cmd + ' --sw-skip', None, 2, '고르는 선택지 --sw-skip', None),
        ('W16e (F8) --config-file 의 testpaths(그 파일 폴더 기준)', 'pytest --config-file=cfg/web.ini --ds=config.settings', None, 0,
         '판정 — web 시험 경로만', lambda: p.w('cfg/web.ini', '[pytest]', 'testpaths = ../web_test ../tests/web')),
        ('W12a 한 단계 -m "not postgresql" → 좁음', 'pytest -m "not postgresql" web_test tests/web', None, 2,
         "좁음 — 빠진 web 시험 경로 web_test(표식 'not postgresql' 만", None),
        ('W12b -k → 좁음', ok_cmd + ' -k smoke', None, 2, '좁음 — 단계 1 고르는 선택지 -k smoke', None),
        ('W12c --deselect W 안 → 좁음', ok_cmd + ' --deselect web_test/a_test.py::t', None, 2,
         '좁음 — 단계 1 고르는 선택지 --deselect web_test/a_test.py::t', None),
        ('W12d --ignore=node_modules → 0', ok_cmd + ' --ignore=node_modules', None, 0, '판정 — web 시험 경로만', None),
        ('W12e --lf → 좁음', ok_cmd + ' --lf', None, 2, '고르는 선택지 --lf', None),
        ('W12f -n0 붙은 값 · -mE 붙은 값 짝 → 0', 'pytest -n0 -mdb web_test tests/web && pytest -n auto "-mnot db" web_test tests/web',
         None, 0, '판정 — web 시험 경로만', None),
        ('W13 깊은 application/x/tests/web → 넓음', ok_cmd + ' application/x/tests/web', None, 2,
         '넓음 — 단계 1 경로 application/x/tests/web', None),
        ('W14b test_command 비문자열 → 판정 불가', None, None, 1, 'test_command 가 글자가 아님', None),
    ]
    for name, command, extra, want, text, setup in cases:
        if setup:
            setup()
        if command is None:
            p.w(RUN + '/build-state.json', json.dumps({'test_command': ['pytest']}))
        else:
            state(p, command, extra)
        code, out = scope(root)
        check(name, code == want and has(out, text), 'exit %d\n%s' % (code, out))
        if (root / 'pytest.ini').exists():
            (root / 'pytest.ini').unlink()
    # W12g addopts 의 고르는 선택지는 판정 밖(프로젝트 기본)
    p.w('pytest.ini', '[pytest]', 'addopts = -m "not slow"')
    state(p, ok_cmd)
    code, out = scope(root)
    check('W12g addopts 의 -m 은 판정 밖 → 0', code == 0, out)
    (root / 'pytest.ini').unlink()
    # W15 pytest 설정 첫 파일 — pytest.ini 가 pyproject 를 이긴다
    p.w('pytest.ini', '[pytest]', 'testpaths = web_test tests/web')
    p.w('pyproject.toml', '[tool.pytest.ini_options]', 'testpaths = ["tests"]')
    state(p, 'pytest --ds=config.settings')
    code, out = scope(root)
    check('W15a pytest.ini testpaths 가 먼저 → 0', code == 0 and has(out, '판정 — web 시험 경로만'), out)
    (root / 'pytest.ini').unlink()
    code, out = scope(root)
    check('W15b pyproject 만 → testpaths tests 넓음', code == 2 and has(out, '넓음 — 단계 1 경로 tests(testpaths)'), out)
    (root / 'pyproject.toml').unlink()
    # W14a build-state 없음
    code, out = run_script(SCRIPTS / 'backstop.py', root, '--test-scope', '.dddjango-web/none')
    check('W14a build-state 없음 → 판정 불가', code == 1 and has(out, 'build-state.json 없음'), out)
    # W17 (F9) 설정 testpaths 따옴표 짝이 안 맞으면 판정 불가 줄(traceback 아님)
    p.w('pytest.ini', '[pytest]', 'testpaths = "web_test')
    state(p, 'pytest --ds=config.settings')
    code, out = scope(root)
    check('W17 (F9) 설정 따옴표 짝 안 맞음 → 판정 불가 — pytest 설정 읽기 실패',
          code == 1 and has(out, '판정 불가 — pytest 설정 읽기 실패') and 'Traceback' not in out, out)
    (root / 'pytest.ini').unlink()
    # W8d · W8e (R-N9) test_web_paths 가 다른 web 시험 경로의 조상 · 자손이면 판정 불가
    p.w('web_test/sub/test_s.py', 'def test_s() -> None:', '    assert True')
    state(p, ok_cmd + ' web_test/sub', ['web_test/sub'])
    code, out = scope(root)
    check('W8d (R-N9) test_web_paths 가 web_test 의 자손 → 판정 불가', code == 1 and has(out, '조상 · 자손'), out)
    shutil.rmtree(root / 'web_test/sub')
    state(p, ok_cmd + ' tests', ['tests'])
    code, out = scope(root)
    check('W8e (R-N9) test_web_paths 가 tests/web 의 조상 → 판정 불가', code == 1 and has(out, '조상 · 자손'), out)
    # W18 (F12) 산출물 폴더는 프로젝트 루트 기준 · 기록 폴더 아래만(절대 경로도 받는다)
    p.w('other/run/build-state.json', json.dumps({'test_command': ok_cmd}))
    code, out = run_script(SCRIPTS / 'backstop.py', root, '--test-scope', 'other/run')
    check('W18a (F12) 기록 폴더 밖 산출물 폴더 → 판정 불가', code == 1 and has(out, '산출물 폴더는'), out)
    shutil.rmtree(root / 'other')
    state(p, ok_cmd)
    code, out = run_script(SCRIPTS / 'backstop.py', root, '--test-scope', str(root / RUN))
    check('W18b (F12) 절대 경로 산출물 폴더 → 0', code == 0 and has(out, '판정 — web 시험 경로만'), out)
    # W10 (B1) 기록 폴더 안 사본의 tests/web 은 W 가 아니다 · 그 안 시험 파일도 세지 않는다
    p.w('.dddjango-web/20261001-0000-old/before/tests/web/test_x.py', 'from web.application.order import order_router',
        'def test_x() -> None:', '    assert order_router')
    p.commit('record copy')
    state(p, ok_cmd)
    code, out = scope(root)
    check('W10 기록 폴더 안 tests/web 사본 — W 아님 · 소비자 아님 · 0',
          code == 0 and has(out, 'web 시험 경로: web_test(시험 파일 1) · tests/web(시험 파일 1)')
          and not has(out, '.dddjango-web/20261001') and has(out, '소비자 0'), out)
    # W11 (B2) web/ · web_test 없는 첫 실행
    q = Proj(tmp / 'w11')
    q.w('manage.py', '# manage')
    git(q.root, 'init', '-q')
    q.commit('base')
    state(q, 'pytest web_test --import-mode=importlib --ds=m')
    code, out = scope(q.root)
    check('W11 web/ · web_test 없음 → 0 · web_test(없음)', code == 0 and has(out, 'web 시험 경로: web_test(없음)'), out)
    code, out = scope(q.root, '--since', 'HEAD')
    check('W11b web/ 없이 --since → 0 · 줄 0', code == 0 and has(out, '계층 중 시험 줄 0 · 슬라이스 끝 시험 줄 0'), out)


# ---------------------------------------------------------------- C 소비자


def consumer_project(root):
    p, _base = base_project(root)
    p.w('web/static/css/base.css', 'body { margin: 0; }')
    p.w('web/static/js/x.js', 'void 0;')
    p.w('application/__init__.py', '')
    p.w('application/tools/__init__.py', '')
    p.w('config/settings.py', "SECRET_KEY = 'x'", 'ROOT_URLCONF = "config.urls"', 'INSTALLED_APPS = ["web"]')
    p.w('config/urls.py', 'from django.urls import include, path', 'urlpatterns = [path("", include("web.urls"))]')
    p.w('config/__init__.py', '')
    p.w('tests/api/test_a.py', 'from web.application.order.order_router import OrderRoutes', '',
        'def test_a() -> None:', '    assert OrderRoutes')
    p.w('tests/api/test_b.py', 'TARGET = "web.application.order.order_router.OrderRoutes"', '',
        'def test_b() -> None:', '    assert TARGET')
    p.w('tests/static/test_c.py', 'def test_c() -> None:', '    assert "web/css/base.css"')
    p.w('tests/static/test_c2.py', 'def test_c2() -> None:', '    assert "web/static/js/x.js"')
    p.w('tests/rag/test_d.py', 'CODE_ROOTS = ("application", "web")', '', 'def test_d() -> None:', '    assert CODE_ROOTS')
    p.w('tests/rag/test_e.py', 'from pathlib import Path', 'REPO = Path(__file__).parents[2]', '',
        'def test_e() -> None:', '    assert (REPO / "web" / "root").is_dir()')
    p.w('tests/misc/test_n.py', '"""web/application 을 보지 않는다 · web.application.order 도."""',
        '# web.application.order.order_router', 'VARIANT = {"variant": "web"}', 'WEB = "web"', '', '',
        'def test_n(web) -> None:', '    """web/root 를 읽지 않는다."""', '    assert web.status_code', '    assert "web/nothere/x"')
    p.w('application/tools/web_links.py', 'from web.application.order import order_router', '', 'LINKS = order_router')
    p.w('tests/tools/test_links.py', 'from application.tools.web_links import LINKS', '',
        'def test_links() -> None:', '    assert LINKS')
    p.w('tests/conf/test_settings.py', 'from config import settings', '', 'def test_settings() -> None:',
        '    assert settings')
    p.w('tests/helpers/web_tools.py', 'from web.application.order import order_router', '', 'ROUTER = order_router')
    p.w('tests/other/test_uses_tools.py', 'from tests.helpers.web_tools import ROUTER', '',
        'def test_uses() -> None:', '    assert ROUTER')
    p.w('tests/helpers/__init__.py', '')
    return p, p.commit('consumers')


def bundle_c(tmp):
    p, _base = consumer_project(tmp / 'c')
    state(p, 'pytest web_test tests/web --import-mode=importlib --ds=config.settings')
    code, out = scope(p.root)
    want = {
        'C-A import': 'tests/api/test_a.py — import web.application.order.order_router',
        'C-B 점 경로': 'tests/api/test_b.py — 점 경로 web.application.order.order_router.OrderRoutes',
        'C-C 경로 글자(static 이름)': 'tests/static/test_c.py — 경로 글자 web/css/base.css',
        'C-C (I9) web/static 경로 글자': 'tests/static/test_c2.py — 경로 글자 web/static/js/x.js',
        "C-C′ 다른 맨 위 폴더와 함께 쓴 'web'": 'tests/rag/test_d.py — web 전체를 읽음',
        "C-C′ REPO / 'web'": 'tests/rag/test_e.py — web 전체를 읽음',
        'C-D 한 걸음(web 밖 비시험 모듈)': 'tests/tools/test_links.py — 한 걸음 application/tools/web_links.py',
        'C-지원 모듈 소비자': 'tests/helpers/web_tools.py — import web.application.order',
    }
    for name, text in want.items():
        check(name, code == 0 and has(out, text), out)
    check('C-음성 사전 값 · 대입 · 지역 속성 · 주석 · docstring · 없는 경로 글자 — 소비자 아님', not has(out, 'tests/misc/test_n.py'), out)
    check('C-음성 settings 를 import 하는 시험 — 소비자 아님(settings · 루트 urls 한 걸음 제외)', not has(out, 'tests/conf/test_settings.py'), out)
    check('C-소비자 수', has(out, '[test-scope] 소비자 8:'), out)
    # E 루트 conftest 가 web 을 부름 → --since 에서 프로젝트 전체 필요
    p.w('conftest.py', 'import web  # noqa: F401')
    base = p.commit('root conftest')
    code, out = scope(p.root, '--since', base)
    check('C-E 루트 conftest 가 web 을 부름 → 프로젝트 전체 필요',
          code == 0 and has(out, '[test-scope] 프로젝트 전체 필요 — 루트 conftest 가 web 을 부름'), out)
    # 지원 모듈 소비자의 돌 경로는 그것을 import 하는 시험
    g2 = lines(out, 'G2 더할 시험 1:')
    check('C-G2 더할 시험 = 소비자 돌 경로(지원 모듈 → import 하는 시험)',
          g2 and 'tests/other/test_uses_tools.py' in g2[0] and 'tests/helpers/web_tools.py' not in g2[0]
          and 'tests/api/test_a.py' in g2[0] and 'tests/misc' not in g2[0], out)


# ---------------------------------------------------------------- S --since


def since_project(root):
    p, _base = base_project(root)
    mkbc(p, 'application/board')
    p.w('web/application/board/presentation_layer/view/board_view.html', '{% extends "root/scaffold/view/root_view.html" %}',
        '{% block content %}', '{% include "design_system/component/button/primary_button.html" %}', '{% endblock %}')
    p.w('web_test/application/board/presentation_layer/board_view_test.py', 'def test_board_view() -> None:', '    assert True')
    p.w('tests/web/test_order_page.py', 'PAGE = "application/order/presentation_layer/view/order_list_view.html"', '',
        'def test_order_page() -> None:', '    assert PAGE')
    p.w('tests/web/test_vm_import.py', 'from web.application.order.application_layer.view_model.order_list_vm import OrderListVM',
        '', 'def test_vm() -> None:', '    assert OrderListVM')
    p.w('tests/web/_support.py', 'def helper() -> int:', '    return 1')
    p.w('tests/web/test_helper_user.py', 'from tests.web._support import helper', '', 'def test_support() -> None:',
        '    assert helper()')
    p.w('tests/web/__init__.py', '')
    p.w('tests/rag/test_snapshot.py', 'from pathlib import Path', 'REPO = Path(__file__).parents[2]', '',
        'def test_snapshot() -> None:', '    assert (REPO / "web").is_dir()')
    p.w('tests/test_unrelated.py', 'def test_unrelated() -> None:', '    assert True')
    p.w('tests/api/factories.py', 'def make() -> int:', '    return 1')
    p.w('tests/api/test_orders.py', 'from tests.api.factories import make', '', 'def test_orders() -> None:', '    assert make()')
    p.w('tests/api/conftest.py', 'X = 1')
    state(p, 'pytest web_test tests/web -x --maxfail=1 --import-mode=importlib --ds=config.settings')
    return p, p.commit('since base')


def bundle_s(tmp):
    p, base = since_project(tmp / 's')

    def run(name, edit, judge):
        p.reset(base)
        edit()
        code, out = scope(p.root, '--since', base)
        try:
            ok = code == 0 and judge(out)
        except Exception as error:  # noqa: BLE001
            ok, out = False, '%s\n%s' % (error, out)
        check(name, ok, 'exit %d\n%s' % (code, out))

    def end(out):
        got = lines(out, '슬라이스 끝 시험 1:')
        return got[0] if got else ''

    run('S1 BC 템플릿 → 그 BC 미러 + 템플릿 이름을 쓰는 tests/web 시험',
        lambda: p.append(ORDER_PAGE, '<!-- x -->'),
        lambda out: 'web_test/application/order' in end(out) and 'tests/web/test_order_page.py' in end(out)
        and 'web_test/application/board' not in end(out))
    run('S2 공용 부품 → include 하는 다른 BC 화면 미러',
        lambda: p.append(BUTTON, '<span></span>'),
        lambda out: 'web_test/application/board' in end(out) and 'web_test/application/order' not in end(out))
    run('S3 루트 셸 → = web 시험 전체(W 시험이 모두 닫힘에 닿을 때)',
        lambda: (p.append(SHELL, '<!-- shell -->'), p.w('tests/web/test_pages.py', 'SHELL = "root/scaffold/view/root_view.html"'),
                 [git(p.root, 'rm', '-q', rel) for rel in ('tests/web/test_vm_import.py', 'tests/web/test_helper_user.py')]),
        lambda out: has(out, '[test-scope] 슬라이스 끝 시험 = web 시험 전체')
        and ' tests/web web_test ' in ' ' + end(out) + ' ')
    run('S4 (I9) import 로만 부르는 W 시험이 슬라이스 끝에',
        lambda: p.append(ORDER_VM, '# x'),
        lambda out: 'tests/web/test_vm_import.py' in end(out))
    run('S5 미추적 W 시험이 닫힘 경로 글자를 씀 → 슬라이스 끝에',
        lambda: (p.append(ORDER_VM, '# y'),
                 p.w('tests/web/test_new_path.py', 'P = "web/application/order/application_layer/view_model/order_list_vm.py"',
                     'def test_p() -> None:', '    assert P')),
        lambda out: 'tests/web/test_new_path.py' in end(out))
    run('S6 (I6) 라우터 .py 만 → web 전체 소비자가 슬라이스 끝에',
        lambda: p.append('web/application/order/order_router.py', '# z'),
        lambda out: 'tests/rag/test_snapshot.py' in end(out))
    run('S7 바뀐 _support.py → 그것을 import 하는 W 시험',
        lambda: p.append('tests/web/_support.py', '# s'),
        lambda out: 'tests/web/test_helper_user.py' in end(out) and not lines(out, '계층 중 시험 1:'))
    run('S8 바뀐 시험 파일만 → 계층 중 시험 줄(옵션 그대로)',
        lambda: p.append('tests/web/test_order_page.py', '# t'),
        lambda out: lines(out, '계층 중 시험 1:') == [
            '[test-scope] 계층 중 시험 1: pytest tests/web/test_order_page.py -x --maxfail=1 --import-mode=importlib '
            '--ds=config.settings'])
    run('S9 (S6) 슬라이스 끝 · G2 줄은 fail-fast 를 뗀다',
        lambda: p.append('tests/test_unrelated.py', '# u'),
        lambda out: '-x' not in end(out).split() and '--maxfail=1' not in end(out)
        and '--maxfail=1' not in lines(out, 'G2 더할 시험 1:')[0] and '-x' in lines(out, '계층 중 시험 1:')[0].split())
    run('S10 G2 더할 시험 = 소비자 전부 + 바뀐 W 밖 시험',
        lambda: p.append('tests/test_unrelated.py', '# v'),
        lambda out: 'tests/rag/test_snapshot.py' in lines(out, 'G2 더할 시험 1:')[0]
        and 'tests/test_unrelated.py' in lines(out, 'G2 더할 시험 1:')[0])
    # S13 ~ S15 일꾼 — 계층 중 시험 줄은 -n0(G-5 나) · 슬라이스 끝 시험 줄은 최대 6(사용자 결정 — auto · logical 은 그대로 두고
    # pytest 낱말 바로 뒤에 --maxprocesses=6(이미 6 이하면 그대로 · 단계의 더 큰 값은 뺌) · 6 보다 큰 수는 -n 6 · 6 이하 ·
    # 지정 없음은 그대로) · G2 더할 시험 줄은 프로젝트 명령 그대로. end_head = pytest 낱말 바로 뒤에 들어간 낱말
    layer_n0 = 'pytest -n0 tests/web/test_order_page.py '
    ds = ' --ds=config.settings'
    for label, command, ini, layer_want, end_workers, end_head, g2_workers in (
            ('S13 단계의 -n auto', 'pytest web_test tests/web -n auto --import-mode=importlib' + ds, None,
             layer_n0 + '--import-mode=importlib --ds=config.settings', ['--maxprocesses=6', '-n', 'auto'],
             ['--maxprocesses=6'], ['-n', 'auto']),
            ('S13b 단계의 --numprocesses=12', 'pytest --numprocesses=12 web_test tests/web' + ds, None,
             layer_n0 + '--ds=config.settings', ['-n', '6'], ['-n', '6'], ['--numprocesses=12']),
            ('S13c (A-S1) 단계의 -n auto --maxprocesses=12', 'pytest -n auto --maxprocesses=12 web_test tests/web' + ds, None,
             'pytest -n0 --maxprocesses=12 tests/web/test_order_page.py --ds=config.settings',
             ['--maxprocesses=6', '-n', 'auto'], ['--maxprocesses=6'], ['-n', 'auto', '--maxprocesses=12']),
            ('S13d (A-S1) 단계의 -n auto --maxprocesses 4(6 이하)', 'pytest -n auto --maxprocesses 4 web_test tests/web' + ds, None,
             'pytest -n0 --maxprocesses 4 tests/web/test_order_page.py --ds=config.settings',
             ['-n', 'auto', '--maxprocesses', '4'], [], ['-n', 'auto', '--maxprocesses', '4']),
            ('S13e (A-S1) 앞 대입으로 auto 일꾼 4 — 늘리지 않는다', 'PYTEST_XDIST_AUTO_NUM_WORKERS=4 pytest -n auto web_test tests/web' + ds,
             None, 'PYTEST_XDIST_AUTO_NUM_WORKERS=4 pytest -n0 tests/web/test_order_page.py --ds=config.settings',
             ['--maxprocesses=6', '-n', 'auto'], ['--maxprocesses=6'], ['-n', 'auto']),
            ('S14 단계의 --numprocesses=4(6 이하)', 'pytest --numprocesses=4 web_test tests/web' + ds, None,
             layer_n0 + '--ds=config.settings', ['--numprocesses=4'], [], ['--numprocesses=4']),
            ('S14b 단계의 -n 4(6 이하)', 'pytest -n 4 web_test tests/web' + ds, None,
             layer_n0 + '--ds=config.settings', ['-n', '4'], [], ['-n', '4']),
            ('S15 addopts 에만 -n 4', 'pytest web_test tests/web' + ds, 'addopts = -n 4',
             layer_n0 + '--ds=config.settings', [], [], []),
            ('S15b addopts 에만 -n auto', 'pytest web_test tests/web' + ds, 'addopts = -n auto',
             layer_n0 + '--ds=config.settings', ['--maxprocesses=6'], ['--maxprocesses=6'], []),
            ('S15d (A-S1) addopts 에 -n auto --maxprocesses=4', 'pytest web_test tests/web' + ds, 'addopts = -n auto --maxprocesses=4',
             layer_n0 + '--ds=config.settings', [], [], []),
            ('S15e (A-S1) addopts 에만 -n 12', 'pytest web_test tests/web' + ds, 'addopts = -n 12',
             layer_n0 + '--ds=config.settings', ['-n', '6'], ['-n', '6'], []),
            ('S15c 일꾼 지정 없음(한 줄 실행)', 'pytest web_test tests/web' + ds, None,
             'pytest tests/web/test_order_page.py --ds=config.settings', [], [], [])):
        p.reset(base)
        state(p, command)
        if ini:
            p.w('pytest.ini', '[pytest]', ini)
        p.append('tests/web/test_order_page.py', '# n')
        code, out = scope(p.root, '--since', base)
        ends = [shlex.split(line.split(': ', 1)[1]) for line in lines(out, '슬라이스 끝 시험 1:')]
        g2s = [shlex.split(line.split(': ', 1)[1]) for line in lines(out, 'G2 더할 시험 1:')]

        def workers(words):
            return [w for i, w in enumerate(words) if w.startswith('-n') and not w.startswith('--')
                    or w.startswith('--numprocesses') or w.startswith('--maxprocesses')
                    or (i and words[i - 1] in ('-n', '--maxprocesses'))]

        def head(words):
            at = words.index('pytest') + 1
            return words[at:at + len(end_head)]
        check('%s → 슬라이스 끝 %s · G2 %s · 계층 중 줄' % (label, ' '.join(end_workers) or '지정 없음',
                                                   ' '.join(g2_workers) or '지정 없음'),
              code == 0 and lines(out, '계층 중 시험 1:') == ['[test-scope] 계층 중 시험 1: ' + layer_want]
              and len(ends) == 1 and workers(ends[0]) == end_workers and head(ends[0]) == end_head
              and len(g2s) == 1 and workers(g2s[0]) == g2_workers, out)
    p.reset(base)
    state(p, 'pytest --ds=config.settings')
    code, out = scope(p.root, '--since', base)
    check('S11 넓음이면 --since 줄 없음', code == 2 and not lines(out, '계층 중 시험 줄') and not lines(out, '슬라이스 끝'), out)
    p.reset(base)
    # S16 (F1) 앞 이름=값 대입은 계층 중 줄에서도 대입으로 남는다
    state(p, 'PYTEST_ADDOPTS="-p no:cacheprovider" pytest web_test tests/web --ds=config.settings')
    p.append('tests/web/test_order_page.py', '# a')
    code, out = scope(p.root, '--since', base)
    layer = lines(out, '계층 중 시험 1:')
    check('S16 (F1) 앞 대입 단계의 계층 중 줄 — 셸이 같은 대입으로 읽는다',
          code == 0 and layer == ["[test-scope] 계층 중 시험 1: PYTEST_ADDOPTS='-p no:cacheprovider' pytest "
                                  "tests/web/test_order_page.py --ds=config.settings"]
          and shlex.split(layer[0].split(': ', 1)[1])[0] == 'PYTEST_ADDOPTS=-p no:cacheprovider', out)
    # S17 (F2) W 밖 지원 모듈 · conftest 를 바꾸면 그것을 쓰는 W 밖 시험이 G2 더할 시험에
    run('S17a (F2) 바뀐 W 밖 지원 모듈 → 그것을 import 하는 W 밖 시험이 G2 더할 시험에',
        lambda: p.append('tests/api/factories.py', '# f'),
        lambda out: 'tests/api/test_orders.py' in ' '.join(lines(out, 'G2 더할 시험'))
        and 'tests/api/test_orders.py' not in end(out))
    run('S17b (F2) 바뀐 W 밖 conftest → 그 폴더가 G2 더할 시험에',
        lambda: p.append('tests/api/conftest.py', '# c'),
        lambda out: ' tests/api ' in ' ' + ' '.join(lines(out, 'G2 더할 시험')) + ' ')
    # S17c (A-I2) 바뀐 W 밖 지원 모듈을 W 밖 conftest 만 import(고정물로 넘김) → 그 conftest 폴더가 G2 더할 시험에
    p.reset(base)
    b2 = conftest_support(p)
    p.append('tests/shop/factories.py', '# f')
    code, out = scope(p.root, '--since', b2)
    check('S17c (A-I2) 바뀐 W 밖 지원 모듈을 W 밖 conftest 가 import → 그 conftest 폴더가 G2 더할 시험에',
          code == 0 and ' tests/shop ' in ' ' + ' '.join(lines(out, 'G2 더할 시험')) + ' '
          and not lines(out, '프로젝트 전체 필요 —'), out)
    # S17d (A-I2) 루트 conftest 가 바뀐 W 밖 지원 모듈을 import → 프로젝트 전체 필요
    p.reset(base)
    conftest_support(p)
    p.w('tests/common/__init__.py', '')
    p.w('tests/common/builders.py', 'def build() -> int:', '    return 1')
    p.w('conftest.py', 'import pytest', 'from tests.common.builders import build', '', '', '@pytest.fixture',
        'def built() -> int:', '    return build()')
    b3 = p.commit('root conftest builders')
    p.append('tests/common/builders.py', '# b')
    code, out = scope(p.root, '--since', b3)
    check('S17d (A-I2) 루트 conftest 가 바뀐 W 밖 지원 모듈을 import → 프로젝트 전체 필요',
          code == 0 and has(out, '[test-scope] 프로젝트 전체 필요 — 루트 conftest 가 import 하는 지원 모듈 tests/common/builders.py'),
          out)
    # S18 (A-I1) 슬라이스 끝 ③(닫힘 글자를 쓰는 W 시험 — git grep)은 사용자 git 설정에 흔들리지 않는다
    p.reset(base)
    p.append(ORDER_PAGE, '<!-- x -->')
    attrs = tmp / 'user-attributes'
    attrs.write_text('*.py -diff\n', encoding='utf-8')
    with user_gitconfig(tmp / 'cfg-attr', ('core.attributesFile', str(attrs))):
        code, out = scope(p.root, '--since', base)
    check('S18b (A-I1) 사용자 전역 속성 *.py -diff — 템플릿 이름을 쓰는 tests/web 시험이 그대로 슬라이스 끝에',
          code == 0 and 'tests/web/test_order_page.py' in end(out), out)
    code, out = grep_fullname_scene(tmp / 'sub', tmp / 'cfg-fullname')
    check('S18a (A-I1) 하위 폴더 루트 + 사용자 grep.fullName=true — 템플릿 이름을 쓰는 tests/web 시험이 그대로 슬라이스 끝에',
          code == 0 and 'tests/web/test_order_page.py' in end(out), out)
    # S12 (R-B1 · R-S2) 병합 유입 — 승인 병합이 상류판 그대로 들인 경로만 바뀐 파일에서 뺀다
    for label, approve, resolve, inside in (
            ('S12 (R-B1) 승인 병합이 상류판 그대로 들인 tests/test_y.py · web 밖 파일 — 바뀐 파일 아님', 'ok', False, False),
            ('S12b (R-S2) 미승인 병합이 들인 시험 · web 밖 파일 — 바뀐 파일', None, False, True),
            ('S12c (R-S2) 승인 병합 안 충돌 해소(상류판과 다른 판) — 바뀐 파일', 'ok', True, True),
            ('S12d (R-S2) 승인 목록 오류 — 알림 · 병합 유입을 모두 셈', 'bad', False, True)):
        p.reset(base)
        merge = merge_case(p, approve, resolve)
        code, out = scope(p.root, '--since', base)
        g2 = ' '.join(lines(out, 'G2 더할 시험'))
        wide = has(out, '프로젝트 전체 필요 — application/billing.py')
        ok = (code == 0 and 'web_test/application/order' in ' '.join(lines(out, '슬라이스 끝 시험'))
              and wide == inside and (('tests/test_y.py' in g2) == (inside and not resolve)))
        if approve == 'bad':
            ok = ok and has(out, '[test-scope] 알림 — 승인 병합 판정 불가')
        check(label, ok, 'merge %s\n%s' % (merge, out))
        git(p.root, 'checkout', '-q', 'main')
        git(p.root, 'branch', '-q', '-D', 'mainline')


def conftest_support(p):
    """W 밖 지원 모듈(tests/shop/factories.py)을 W 밖 conftest 만 import 해 고정물로 넘기고 시험은 고정물만 받는 꼴 → 커밋."""
    p.w('tests/shop/__init__.py', '')
    p.w('tests/shop/factories.py', 'def make_cart() -> dict:', '    return {"items": []}')
    p.w('tests/shop/conftest.py', 'import pytest', 'from tests.shop.factories import make_cart', '', '', '@pytest.fixture',
        'def cart() -> dict:', '    return make_cart()')
    p.w('tests/shop/test_cart.py', 'def test_cart(cart: dict) -> None:', '    assert cart["items"] == []')
    return p.commit('conftest support')


def grep_fullname_scene(top, cfg, scripts=SCRIPTS):
    """하위 폴더 루트(저장소 뿌리 밑 svc/) · BC 템플릿 한 줄 바꿈 · tests/web 시험이 그 템플릿 이름 글자를 씀 — 사용자 전역
    grep.fullName=true 아래 --since 실행 → (exit, 출력)."""
    q = mkstd(top / 'svc', git_top=top)
    q.w('tests/__init__.py', '')
    q.w('tests/web/test_pages.py', 'def test_pages() -> None:', '    assert True')
    q.w('tests/web/test_order_page.py', 'PAGE = "application/order/presentation_layer/view/order_list_view.html"', '',
        'def test_order_page() -> None:', '    assert PAGE')
    state(q, 'pytest web_test tests/web --import-mode=importlib --ds=config.settings')
    git(top, 'add', '-A')
    git(top, 'commit', '-qm', 'base')
    base = git(top, 'rev-parse', 'HEAD')
    q.append(ORDER_PAGE, '<!-- x -->')
    with user_gitconfig(cfg, ('grep.fullName', 'true')):
        return scope(q.root, '--since', base, scripts=scripts)


def merge_case(p, approve, resolve):
    """기준점 → mainline 가지에 W 밖 시험 · web 밖 파일 → main 에 레인 커밋 → 병합(resolve 면 병합 커밋 안에서 web 밖 파일을
    상류판과 다르게 고침) → 승인 목록(approve 'ok' · 'bad' · None). → 병합 sha."""
    git(p.root, 'checkout', '-q', '-b', 'mainline')
    p.w('tests/test_y.py', 'def test_y() -> None:', '    assert True')
    p.w('application/billing.py', 'X = 1')
    upstream = p.commit('upstream')
    git(p.root, 'checkout', '-q', 'main')
    p.append(ORDER_PAGE, '<!-- lane -->')
    p.commit('lane')
    if resolve:
        git(p.root, 'merge', '-q', '--no-ff', '--no-commit', upstream)
        p.w('application/billing.py', 'X = 2')
        p.commit('merge main · 충돌 해소')
    else:
        git(p.root, 'merge', '-q', '--no-ff', '-m', 'merge main', upstream)
    merge = git(p.root, 'rev-parse', 'HEAD')
    if approve == 'ok':
        p.w(RUN + '/approved-merges.txt', merge + ' main 받기')
    elif approve == 'bad':
        p.w(RUN + '/approved-merges.txt', 'not-a-sha')
    return merge


# ---------------------------------------------------------------- P 프로젝트 전체 필요


def bundle_p(tmp):
    p, _b = base_project(tmp / 'p')
    p.w('config/settings.py', "SECRET_KEY = 'x'", 'ROOT_URLCONF = "config.urls"',
        'MIDDLEWARE = ["web.extra.mw.Middleware"]', 'INSTALLED_APPS = ["web.apps.WebConfig"]')
    p.w('config/urls.py', 'from django.urls import include, path', 'urlpatterns = [path("", include("web.urls"))]')
    p.w('web/extra/mw.py', 'class Middleware:', '    pass')
    p.w('web/extra/__init__.py', '')
    state(p, 'pytest web_test tests/web --import-mode=importlib --ds=config.settings')
    base = p.commit('p base')

    def run(name, edit, want, unwant=None, commit=True):
        p.reset(base)
        edit()
        if commit:
            p.commit('edit')
        code, out = scope(p.root, '--since', base)
        wide = lines(out, '프로젝트 전체 필요 —')
        ok = code == 0 and all(any(w in line for line in wide) for w in want) and (not unwant or not wide)
        check(name, ok, 'exit %d\n%s' % (code, out))

    run('P1 config/settings.py 커밋 → 까닭 그 파일', lambda: p.append('config/settings.py', 'DEBUG = True'),
        ['프로젝트 전체 필요 — config/settings.py'])
    run('P2 uv.lock · pytest.ini → 걸림', lambda: (p.w('uv.lock', 'x'), p.w('pytest.ini', '[pytest]')),
        ['프로젝트 전체 필요 — uv.lock', '프로젝트 전체 필요 — pytest.ini'])
    run('P3 (B3) 요청 처리기 → 전역 진입점', lambda: p.append('web/root/handler/root_request_handler.py', '# x'),
        ['전역 진입점 web/root/handler/root_request_handler.py'])
    run('P4 settings MIDDLEWARE 의 비표준 web. 모듈 → 전역 진입점', lambda: p.append('web/extra/mw.py', '# x'),
        ['전역 진입점 web/extra/mw.py'])
    run('P5 진입점이 import 하는 BC 파일만 → 안 걸림', lambda: p.append('web/application/order/order_router.py', '# x'),
        [], unwant=True)
    run('P6 (S9) 루트 conftest 바꿈 → 걸림', lambda: p.w('conftest.py', 'X = 1'), ['프로젝트 전체 필요 — 루트 conftest'])
    run('P7 기록 폴더 · docs/ · 문서 · 그림 → 안 걸림',
        lambda: (p.w('.dddjango-web/note.txt', 'x'), p.w('docs/a.txt', 'x'), p.w('x.md', 'x'), p.w('captures/y.png', 'x')),
        [], unwant=True)
    run('P8 커밋 안 된 바꿈도 셈', lambda: p.append('config/settings.py', 'DEBUG = False'),
        ['프로젝트 전체 필요 — config/settings.py'], commit=False)
    run('P9 (2.5.2) 한글 파일 이름', lambda: p.w('config/로컬 설정.toml', 'x = 1'), ['프로젝트 전체 필요 — config/로컬 설정.toml'])
    run('P12 (R-N7) web 시험 경로 아래 비-.py 자산 → 안 걸림',
        lambda: (p.w('web_test/fixtures/data.json', '{}'), p.w('tests/web/assets/a.css', 'a { color: red; }')), [], unwant=True)
    # P13 (F10) test_web_paths 아래 관례 밖 이름의 지원 파일 → 안 걸림
    p.reset(base)
    p.w('ui_tests/test_ui.py', 'def test_ui() -> None:', '    assert True')
    state(p, 'pytest web_test tests/web ui_tests --import-mode=importlib --ds=config.settings', ['ui_tests'])
    b3 = p.commit('ui tests')
    p.w('ui_tests/helpers.py', 'X = 1')
    code, out = scope(p.root, '--since', b3)
    check('P13 (F10) test_web_paths 아래 helpers.py → 안 걸림', code == 0 and not lines(out, '프로젝트 전체 필요 —'), out)
    # settings 를 못 찾으면 표준 여덟 자리만
    p.reset(base)
    state(p, 'pytest web_test tests/web --import-mode=importlib')
    p.w('manage.py', '# manage')
    b2 = p.commit('no ds')
    p.append('web/extra/mw.py', '# y')
    code, out = scope(p.root, '--since', b2)
    check('P10 settings 못 찾음 → 표준 여덟 자리만(비표준 web. 모듈은 안 걸림)',
          code == 0 and not lines(out, '프로젝트 전체 필요 —'), out)
    p.append('web/urls.py', '# y')
    code, out = scope(p.root, '--since', b2)
    check('P10b settings 못 찾아도 표준 진입점 web/urls.py 는 걸림', code == 0 and has(out, '전역 진입점 web/urls.py'), out)
    # 하위 폴더 루트(2.5.1) — 저장소 뿌리 밑 svc/ 가 프로젝트
    top = tmp / 'psub'
    q = mkstd(top / 'svc', git_top=top)
    q.w('tests/web/test_pages.py', 'def test_pages() -> None:', '    assert True')
    state(q, 'pytest web_test tests/web --import-mode=importlib --ds=config.settings')
    git(top, 'add', '-A')
    git(top, 'commit', '-qm', 'base')
    sub_base = git(top, 'rev-parse', 'HEAD')
    q.append('web/root/handler/root_request_handler.py', '# x')
    q.append('config/settings.py', 'DEBUG = True')
    (top / 'outside.txt').write_text('x\n', encoding='utf-8')
    code, out = scope(q.root, '--since', sub_base)
    wide = lines(out, '프로젝트 전체 필요 —')
    check('P11 (2.5.1) 하위 폴더 루트 — 같은 결과 · 루트 밖 파일은 세지 않는다',
          code == 0 and any('전역 진입점 web/root/handler/root_request_handler.py' in w for w in wide)
          and any(w.endswith('— config/settings.py') for w in wide) and not any('outside.txt' in w for w in wide), out)


# ---------------------------------------------------------------- U 사용 오류 · MUT


def bundle_u(tmp):
    p, base = base_project(tmp / 'u')
    state(p, 'pytest web_test tests/web --ds=config.settings')
    code, out = run_script(SCRIPTS / 'backstop.py', p.root, '--test-scope', RUN, '--diff-base', base)
    check('U1 --test-scope + --diff-base → 사용 오류 exit 1', code == 1 and '단독 모드' in out, out)
    code, out = run_script(SCRIPTS / 'backstop.py', p.root, '--since', base)
    check('U2 --since 홀로 → 사용 오류 exit 1', code == 1 and '단독 모드' in out, out)
    code, out = run_script(SCRIPTS / 'backstop.py', p.root, '--test-scope')
    check('U3 --test-scope 값 없음 → 사용 오류 exit 1', code == 1 and '값 없음' in out, out)
    code, out = run_script(SCRIPTS / 'backstop.py', p.root, '--test-scope', RUN, '--slice-end')
    check('U4 --test-scope + --slice-end → 사용 오류 exit 1', code == 1 and '단독 모드' in out, out)
    code, out = scope(p.root, '--since', 'nope-commit')
    check('U5 --since 해석 불가 → 판정 불가 exit 1', code == 1 and '--since 커밋 해석 불가' in out, out)


def mut_w9c(tmp, scripts):
    p, _base = base_project(tmp)
    state(p, 'PYTEST_ADDOPTS="-p no:cacheprovider" pytest web_test tests/web')
    code, out = scope(p.root, scripts=scripts)
    return not has(out, "단계 1: PYTEST_ADDOPTS='-p no:cacheprovider' pytest {경로}"), out


def mut_w11(tmp, scripts):
    q = Proj(tmp)
    q.w('manage.py', '# manage')
    git(q.root, 'init', '-q')
    q.commit('base')
    state(q, 'pytest web_test --import-mode=importlib --ds=m')
    code, out = scope(q.root, scripts=scripts)
    return code != 0, out


def mut_p3(tmp, scripts):
    p, base = base_project(tmp)
    state(p, 'pytest web_test tests/web --ds=config.settings')
    base = p.commit('state')
    p.append('web/root/handler/root_request_handler.py', '# x')
    code, out = scope(p.root, '--since', base, scripts=scripts)
    return not has(out, '전역 진입점 web/root/handler/root_request_handler.py'), out


def mut_p12(tmp, scripts):
    p, base = base_project(tmp)
    state(p, 'pytest web_test tests/web --ds=config.settings')
    base = p.commit('state')
    p.w('web_test/fixtures/data.json', '{}')
    code, out = scope(p.root, '--since', base, scripts=scripts)
    return bool(lines(out, '프로젝트 전체 필요 —')), out


def mut_merge(approve, inside):
    def scene(tmp, scripts):
        p, base = since_project(tmp)
        merge_case(p, approve, False)
        code, out = scope(p.root, '--since', base, scripts=scripts)
        return ('tests/test_y.py' in ' '.join(lines(out, 'G2 더할 시험'))) != inside, out
    return scene


def mut_workers(command, want):
    def scene(tmp, scripts):
        p, base = since_project(tmp)
        state(p, command)
        base = p.commit('workers')
        p.append('tests/web/test_order_page.py', '# n')
        code, out = scope(p.root, '--since', base, scripts=scripts)
        ends = lines(out, '슬라이스 끝 시험 1:')
        return not (ends and want in ends[0]), out
    return scene


def mut_s17c(tmp, scripts):
    p, base = since_project(tmp)
    base = conftest_support(p)
    p.append('tests/shop/factories.py', '# f')
    code, out = scope(p.root, '--since', base, scripts=scripts)
    return ' tests/shop ' not in ' ' + ' '.join(lines(out, 'G2 더할 시험')) + ' ', out


def mut_s18a(tmp, scripts):
    code, out = grep_fullname_scene(tmp / 'sub', tmp / 'cfg', scripts=scripts)
    got = [line for line in out.splitlines() if line.startswith('[test-scope] 슬라이스 끝 시험 1:')]
    return not (got and 'tests/web/test_order_page.py' in got[0]), out


def mut_s17a(tmp, scripts):
    p, base = since_project(tmp)
    p.append('tests/api/factories.py', '# f')
    code, out = scope(p.root, '--since', base, scripts=scripts)
    return 'tests/api/test_orders.py' not in ' '.join(lines(out, 'G2 더할 시험')), out


MUTANTS = [
    ('바뀐 파일을 전체 diff 로(병합 유입 포함)',
     "    logged = _git(root, 'log', '--first-parent', '--no-merges', '--no-renames', '--format=', '--name-only', '-z',\n"
     "                  '--relative', '%s..HEAD' % oid, '--', '.')\n",
     "    logged = _git(root, 'diff', '--name-only', '--no-renames', '--relative', '-z', oid, '--', '.')\n", 'S12',
     mut_merge('ok', False)),
    ('승인 술어를 뺌(승인 병합이 그대로 들인 경로도 셈)',
     "            if sha in approved:\n                brought &= _names(root, parents[1], sha, ['.'])",
     "            if False:\n                brought &= _names(root, parents[1], sha, ['.'])", 'S12', mut_merge('ok', False)),
    ('병합 유입을 모두 뺌(--no-merges 만)', "            names |= brought\n", "            pass\n", 'S12b',
     mut_merge(None, True)),
    ('단계 줄 낱말을 통째로 감쌈(앞 대입이 명령 이름이 됨)', "            out.append(_shell_word(word))\n",
     "            out.append(shlex.quote(word))\n", 'W9c', mut_w9c),
    ('슬라이스 끝 일꾼 상한을 뺌', "    slice_end = lines('슬라이스 끝 시험', end, False, cap=SLICE_END_WORKERS)",
     "    slice_end = lines('슬라이스 끝 시험', end, False)", 'S13',
     mut_workers('pytest web_test tests/web -n auto --ds=config.settings', ': pytest --maxprocesses=6 ')),
    ('6 이하 일꾼도 상한으로 바꿈(늘림)', "        if value is not None and value.isdigit() and int(value) > cap:\n",
     "        if value is not None and value.isdigit():\n", 'S14b',
     mut_workers('pytest -n 4 web_test tests/web --ds=config.settings', ': pytest -n 4 ')),
    ('auto 를 -n 6 으로 바꿈(auto 가 6 보다 적은 기계에서 늘림)',
     "            return ['--maxprocesses=%d' % cap], set(self.maxprocesses_at)\n",
     "            return ['-n', str(cap)], set(self.xdist)\n", 'S13',
     mut_workers('pytest web_test tests/web -n auto --ds=config.settings', ': pytest --maxprocesses=6 ')),
    ('git grep 의 사용자 설정 고정을 뺌',
     "    out = _git(root, '-c', 'grep.fullName=false', '-c', 'core.attributesFile=', 'grep', '--untracked', '-I', '-l', '-F', '-z',\n",
     "    out = _git(root, 'grep', '--untracked', '-I', '-l', '-F', '-z',\n", 'S18a', mut_s18a),
    ('W 밖 지원 모듈을 import 하는 conftest 폴더를 G2 에서 뺌',
     "            g2.add(folder_of)\n", "            pass\n", 'S17c', mut_s17c),
    ('W 밖 지원 모듈을 import 하는 시험을 G2 에서 뺌',
     "        g2 |= {t for dep in outside_support for t in importers.get(dep, ())}\n", "        pass\n", 'S17a', mut_s17a),
    ('web 시험 경로 아래 파일을 프로젝트 전체 필요에 셈',
     "        elif not (rel.startswith('web/') or rel.startswith('docs/') or in_w(rel) or project.test_side(rel)\n",
     "        elif not (rel.startswith('web/') or rel.startswith('docs/') or project.test_side(rel)\n", 'P12', mut_p12),
    ('web_test 는 실재할 때만 W', "    out = ['web_test'] + [p for p in ('test/web', 'tests/web') if (root / p).is_dir()]\n",
     "    out = [p for p in ('web_test', 'test/web', 'tests/web') if (root / p).is_dir()]\n", 'W11', mut_w11),
    ('전역 진입점 판정을 뺌', "        elif rel in entries:\n", "        elif False:\n", 'P3', mut_p3),
]


def mutant_scripts(tmp, old, new):
    shutil.copytree(SCRIPTS, tmp / 'scripts', ignore=shutil.ignore_patterns('__pycache__', 'test'))
    shutil.copytree(SCRIPTS.parent / '.claude-plugin', tmp / '.claude-plugin')
    target = tmp / 'scripts/src/scope.py'
    text = target.read_text(encoding='utf-8')
    if text.count(old) != 1:
        return None
    target.write_text(text.replace(old, new), encoding='utf-8')
    return tmp / 'scripts'


def bundle_mut(tmp):
    for index, (label, old, new, name, scene) in enumerate(MUTANTS):
        scripts = mutant_scripts(tmp / ('mut%d' % index), old, new)
        if scripts is None:
            check('MUT %s — 되돌릴 자리가 scope.py 에 정확히 한 번' % label, False)
            continue
        red, out = scene(tmp / ('mut%d-p' % index), scripts)
        check('MUT %s → %s 붉음' % (label, name), red, out)


def main():
    only = set(sys.argv[1:])
    with tempfile.TemporaryDirectory(prefix='web270-scope-') as name:
        tmp = Path(name).resolve()
        if not only or 'W' in only:
            bundle_w(tmp / 'W')
        if not only or 'C' in only:
            bundle_c(tmp / 'C')
        if not only or 'S' in only:
            bundle_s(tmp / 'S')
        if not only or 'P' in only:
            bundle_p(tmp / 'P')
        if not only or 'U' in only:
            bundle_u(tmp / 'U')
            bundle_mut(tmp / 'MUT')
    print('2.7.0 시험 범위 픽스처: PASS %d / FAIL %d' % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
