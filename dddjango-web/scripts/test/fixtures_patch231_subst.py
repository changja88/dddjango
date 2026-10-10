"""2.3.1 치환 확인 회귀 픽스처 — 메서드 이동 승인 행 · 0T 시험 전환 대조. 임시 git 저장소만 만들고 끝나면 지운다.

묶음: U 무변(새 입력 없는 실행 — 고치기 전 판과 출력 · exit byte 동일) · M 메서드 이동(자리 꼴 · 음성 꼴 · 대응 충돌 ·
제품 쪽 확인) · T 0T 시험 전환(`_contrast_switch` 규칙 · T 이력 · 취소) · R 재현 장면(F4-75 sc1 — 환경 변수
DDDJANGO_WEB_F75_SCENE 가 그 저장소를 가리킬 때만 · 없으면 건너뛴다 · 장면은 `git clone --shared --no-checkout` 사본에서만 쓴다).
고치기 전 판 = BASELINE 커밋의 scripts(`git show <커밋>:<경로>` 로 임시 폴더에 푼다 — 작업 사본을 stash 하지 않는다).
BASELINE 이 이력에 없으면(얕은 clone 등) byte 대조를 건너뛰고 건너뛴 사실을 출력한다(실패로 세지 않는다)."""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TEST = Path(__file__).resolve().parent
SCRIPTS = TEST.parent
REPO = SCRIPTS.parents[1]
BASELINE = 'f349f878'  # 고치기 전 판(배포된 dddjango-web 2.3.0) — 판마다 바탕 커밋으로 올린다
SCENE = os.environ.get('DDDJANGO_WEB_F75_SCENE', '')
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
PASS = FAIL = 0
_OLD = {}


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok and detail:
        print('    ' + str(detail).replace('\n', '\n    ')[:2400])


def git(root, *args, check_rc=True, env=None, data=None):
    r = subprocess.run(['git', '-C', str(root), '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false',
                        *args], capture_output=True, env=env or ENV, input=data)
    if check_rc and r.returncode:
        raise RuntimeError('git %s — %s' % (' '.join(args[:2]), r.stderr.decode('utf-8', 'replace')))
    return r.stdout.decode('utf-8', 'replace').strip()


def backstop(root, *args, scripts=SCRIPTS):
    r = subprocess.run([sys.executable, '-B', str(scripts / 'backstop.py'), str(root), *map(str, args)],
                       capture_output=True, env=ENV)
    return r.returncode, (r.stdout + r.stderr).decode('utf-8', 'replace')


def old_scripts():
    """BASELINE 커밋의 scripts(test/ 제외)를 임시 폴더에 푼다 → 옛 scripts 폴더(없으면 None)."""
    if 'dir' in _OLD:
        return _OLD['dir']
    _OLD['dir'] = None
    if subprocess.run(['git', '-C', str(REPO), 'cat-file', '-e', BASELINE + '^{commit}'],
                      capture_output=True, env=ENV).returncode:
        print('SKIP byte 대조 — 바탕 커밋 %s 이 이 저장소 이력에 없다(얕은 clone 등)' % BASELINE)
        return None
    target = Path(_OLD['tmp'].name)
    for name in git(REPO, 'ls-tree', '-r', '--name-only', BASELINE, '--', 'dddjango-web/scripts',
                    'dddjango-web/.claude-plugin').splitlines():
        if '/scripts/test/' in name:
            continue
        data = subprocess.run(['git', '-C', str(REPO), 'show', '%s:%s' % (BASELINE, name)],
                              capture_output=True, env=ENV, check=True).stdout
        (target / name).parent.mkdir(parents=True, exist_ok=True)
        (target / name).write_bytes(data)
    _OLD['dir'] = target / 'dddjango-web' / 'scripts'
    return _OLD['dir']


def same_as_old(name, root, *args):
    """새 판과 고치기 전 판의 출력 · exit 이 byte 동일한가(고치기 전 판이 없으면 건너뜀)."""
    old = old_scripts()
    new = backstop(root, *args)
    if old is None:
        return new
    before = backstop(root, *args, scripts=old)
    check('%s — 고치기 전 판(%s)과 byte 동일(exit %d)' % (name, BASELINE, new[0]), new == before,
          'new exit=%d\n%s\n--- old exit=%d\n%s' % (new[0], new[1][-1200:], before[0], before[1][-1200:]))
    return new


class Proj:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        git(self.root, 'init', '-q')

    def w(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def read(self, rel):
        return (self.root / rel).read_text(encoding='utf-8')

    def sub(self, rel, old, new, count=1):
        text = self.read(rel)
        if old not in text:
            raise RuntimeError('픽스처 오류 — %s 에 %r 없음' % (rel, old))
        self.w(rel, text.replace(old, new, count))

    def commit(self, message='c'):
        git(self.root, 'add', '-A')
        git(self.root, 'commit', '-qm', message, '--allow-empty')
        return git(self.root, 'rev-parse', 'HEAD')

    def reset(self, sha):
        git(self.root, 'reset', '-q', '--hard', sha)
        git(self.root, 'clean', '-fdq')

    def spec(self, name, *rows, head='## 슬라이스 0', pre=''):
        path = self.root.parent / ('%s-%s.md' % (self.root.name, name))
        path.write_text('# 명세\n\n%s\n%s\n\n%s\n' % (pre, head, '\n'.join(rows)), encoding='utf-8')
        return path

    def build(self, name, slices, mode='modify'):
        folder = self.root.parent / ('%s-build-%s' % (self.root.name, name))
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'build-state.json').write_text(json.dumps({'mode': mode, 'slices': slices}, ensure_ascii=False),
                                                 encoding='utf-8')
        return folder


# ====================================================================== M — 메서드 이동(합성 · case2 꼴)

HOME_VM = '''class HomeVM:
    def render(self) -> str:
        return "home"

    def redirect(self, key: str | None) -> str | None:
        return "/home/" if key else None
'''
HOME_VM_MOVED = '''class HomeVM:
    def render(self) -> str:
        return "home"
'''
LOGIN_VM = '''class LoginVM:
    def render_initial(self) -> str:
        return "state"
'''
LOGIN_VM_MOVED = '''class LoginVM:
    def redirect(self, key: str | None) -> str | None:
        return "/home/" if key else None

    def render_initial(self) -> str:
        return "state"
'''
LOGIN_VIEW = '''from web.auth.login_vm import LoginVM
from web.home.home_vm import HomeVM


def login_view(key):
    destination = HomeVM().redirect(key)
    if destination is not None:
        return destination
    return LoginVM().render_initial()
'''
LOGIN_VIEW_MOVED = '''from web.auth.login_vm import LoginVM


def login_view(key):
    view_model = LoginVM()
    destination = view_model.redirect(key)
    if destination is not None:
        return destination
    return view_model.render_initial()
'''
TEST_HOME = '''from web.home.home_vm import HomeVM


def test_redirect():
    destination = HomeVM().redirect("k")
    assert destination == "/home/"


def test_other():
    assert HomeVM().redirect(None) is None


def test_render():
    assert HomeVM().render() == "home"
'''
TEST_ICON = '''from importlib import import_module
from unittest.mock import MagicMock


def test_doc(monkeypatch):
    view_module = import_module("web.auth.login_view")
    monkeypatch.setattr(view_module.HomeVM, "redirect", MagicMock(return_value=None))
    monkeypatch.setattr(view_module.LoginVM, "render_initial", MagicMock(return_value="s"))
    assert view_module.login_view("k") == "s"
'''
TEST_MISC = '''from importlib import import_module
from unittest.mock import MagicMock, patch

from web.auth.login_view import login_view
from web.home.home_vm import HomeVM


class FakeMP:
    def setattr(self, *args):
        return None


def make_vm():
    return object()


def test_seed():
    assert HomeVM(seed=1).redirect("k") == "/home/"


def test_patch_string():
    with patch("web.home.home_vm.HomeVM.redirect", return_value="/x/"):
        assert login_view("k") == "/x/"


def test_expect():
    assert "web.home.home_vm.HomeVM.redirect".endswith("redirect")


def test_local():
    vm = HomeVM()
    result = vm.redirect("k")
    assert result == "/home/"


def test_rebind():
    vm = HomeVM()
    vm = make_vm()
    assert vm.redirect("k")


def test_builtin():
    setattr(HomeVM, "redirect", lambda self, key: None)
    assert login_view("k") == "state"


def test_patch_object():
    with patch.object(HomeVM, "redirect", return_value=None):
        assert login_view("k") == "state"


def test_mocker(mocker):
    mocker.patch.object(HomeVM, "redirect", return_value=None)
    spy = mocker.spy(HomeVM, "redirect")
    assert spy is not None


def test_local_mp():
    monkeypatch = FakeMP()
    monkeypatch.setattr(HomeVM, "redirect", None)
    assert True


def test_static():
    assert HomeVM.redirect(HomeVM(), "k") == "/home/"


def test_chain4():
    mod = import_module("web.re.r1")
    assert mod.HomeVM().redirect("k") == "/home/"


def test_chain5():
    mod = import_module("web.re.q1")
    assert mod.HomeVM().redirect("k") == "/home/"


def test_cycle():
    mod = import_module("web.re.c1")
    assert mod.HomeVM().redirect("k") == "/home/"


def test_korean():
    이름 = "한글"; 결과 = ("가나다", HomeVM().redirect("키"))
    assert 결과[1] == "/home/", "한글 메시지 " + 이름


def test_mp_string(monkeypatch, mocker):
    monkeypatch.setattr("web.home.home_vm.HomeVM.redirect", lambda self, key: None)
    mocker.patch("web.home.home_vm.HomeVM.redirect", return_value=None)
    assert login_view("k") == "state"


def test_local_import():
    from web.home.home_vm import HomeVM as VM
    assert VM().redirect("k") == "/home/"
'''
TEST_SHADOW = '''from web.home.home_vm import HomeVM
from mylib import patch


def setattr(*args):
    return None


def test_shadowed():
    setattr(HomeVM, "redirect", None)
    assert True


def test_user_patch():
    with patch.object(HomeVM, "redirect"):
        assert True


def mocker():
    return object()


def test_own_fixture(mocker):
    mocker.patch.object(HomeVM, "redirect")
    assert True
'''
OLD = 'web.home.home_vm.HomeVM.redirect'
NEW = 'web.auth.login_vm.LoginVM.redirect'
LABEL = '%s → %s' % (OLD, NEW)
REDIRECT = 'tests/web/test_home.py::test_redirect'
DOC = 'tests/web/test_icon.py::test_doc'


def row(*tests, old=OLD, new=NEW):
    return '메서드 이동: %s → %s · 시험 %s' % (old, new, ' '.join(tests))


def chain_module(nxt):
    return 'from %s import HomeVM, LoginVM\n' % nxt


def mk_move(tmp):
    p = Proj(tmp / 'mv')
    for rel in ('web/__init__.py', 'web/home/__init__.py', 'web/auth/__init__.py', 'web/re/__init__.py'):
        p.w(rel, '')
    p.w('web/home/home_vm.py', HOME_VM)
    p.w('web/auth/login_vm.py', LOGIN_VM)
    p.w('web/auth/login_view.py', LOGIN_VIEW)
    leaf = 'from web.auth.login_vm import LoginVM\nfrom web.home.home_vm import HomeVM\n'
    for prefix, n in (('r', 4), ('q', 5)):
        for i in range(1, n + 1):
            p.w('web/re/%s%d.py' % (prefix, i), leaf if i == n else chain_module('web.re.%s%d' % (prefix, i + 1)))
    p.w('web/re/c1.py', 'from web.home.home_vm import HomeVM\nfrom web.re.c2 import LoginVM\n')
    p.w('web/re/c2.py', 'from web.re.c1 import LoginVM\n')
    p.w('tests/web/test_home.py', TEST_HOME)
    p.w('tests/web/test_icon.py', TEST_ICON)
    p.w('tests/web/test_misc.py', TEST_MISC)
    p.w('tests/web/test_shadow.py', TEST_SHADOW)
    return p, p.commit('base')


def move_product(p, login_vm=LOGIN_VM_MOVED, home_vm=HOME_VM_MOVED):
    p.w('web/home/home_vm.py', home_vm)
    p.w('web/auth/login_vm.py', login_vm)
    p.w('web/auth/login_view.py', LOGIN_VIEW_MOVED)


IMPORT_HOME = 'from web.home.home_vm import HomeVM\n'
IMPORT_BOTH = IMPORT_HOME + 'from web.auth.login_vm import LoginVM\n'


def move_tests(p):
    p.sub('tests/web/test_home.py', IMPORT_HOME, IMPORT_BOTH)
    p.sub('tests/web/test_home.py', 'destination = HomeVM().redirect("k")', 'destination = LoginVM().redirect("k")')
    p.sub('tests/web/test_icon.py', 'view_module.HomeVM, "redirect"', 'view_module.LoginVM, "redirect"')


def misc_swap(p, old, new, rel='tests/web/test_misc.py'):
    """시험 파일의 한 자리를 바꾼다 — 새 글이 맨 이름 LoginVM 을 쓰면 모듈 머리 import 도 더한다."""
    p.sub(rel, old, new)
    if re.search(r'(?<![\w."])LoginVM\b', new) and IMPORT_BOTH not in p.read(rel):
        p.sub(rel, IMPORT_HOME, IMPORT_BOTH)


def bundle_move(tmp):
    p, base = mk_move(tmp)
    move_product(p)
    move_tests(p)
    moved = p.commit('move')
    s_none = p.spec('none')
    s_row = p.spec('row', row(REDIRECT, DOC))
    e, out = backstop(p.root, '--subst-check', base, moved, '--names', s_none)
    check('M1 메서드 이동 행 없음 — 지금처럼 red(exit 2)', e == 2 and 'tests/web/test_home.py' in out, out[-900:])
    e, out = backstop(p.root, '--subst-check', base, moved, '--names', s_row)
    check('M2 승인 행(두 시험 함수) — case2 꼴(수신자 · patch 대상 · 자리 전용 import) exit 0',
          e == 0 and '[subst]' not in out and 'web/ 밖 변경 파일 2' in out, out[-1500:])
    check('M2 알림 — 행마다 승인 범위 · 파일마다 정규화 자리 수 · 자리 전용 import',
          '[info] 메서드 이동 %s — 승인 시험 함수 2' % LABEL in out
          and '[info] 메서드 이동 자리 정규화 tests/web/test_home.py — 1곳' in out
          and '[info] 메서드 이동 자리 정규화 tests/web/test_icon.py — 1곳' in out
          and "자리 전용 import 대조 밖 — tests/web/test_home.py:1 더함 ['web.auth.login_vm.LoginVM']" in out, out[-1500:])
    check('M2 옮긴 본문이 같으면 «본문 다름» 알림 없음', '옮긴 본문 다름' not in out, out[-600:])
    styled = p.spec('styled', '- 메서드 이동: `%s` → `%s` · 시험 `%s` `%s`' % (OLD, NEW, REDIRECT, DOC))
    e, out = backstop(p.root, '--subst-check', base, moved, '--names', styled)
    check('M2 백틱 · `- ` 머리 꼴도 같은 승인', e == 0 and '[subst]' not in out, out[-900:])
    e, out = backstop(p.root, '--subst-check', base, moved, '--names', p.spec('one', row(REDIRECT)))
    check('M3 목록 밖 시험 함수(test_doc 빠짐) — 그 자리는 정규화하지 않는다(exit 2)',
          e == 2 and '[subst] tests/web/test_icon.py' in out and '[subst] tests/web/test_home.py' not in out, out[-900:])

    # 자리가 쓰지 않는 import 는 K′ 의 모듈이라도 자리 전용이 아니다
    p.reset(moved)
    p.sub('tests/web/test_home.py', IMPORT_BOTH, IMPORT_BOTH + 'import web.auth.login_vm\n')
    e, out = backstop(p.root, '--subst-check', base, p.commit('unused-import'), '--names', s_row)
    check('M3 자리가 쓰지 않는 import(K′ 의 모듈) 더함 — 자리 전용이 아니라 exit 2',
          e == 2 and "더함 ['web.auth.login_vm']" in out, out[-900:])

    # 옮긴 본문 다름 — 알림만(판정 밖)
    p.reset(base)
    move_product(p, login_vm=LOGIN_VM_MOVED.replace('return "/home/" if key', 'return "/home" if key'))
    move_tests(p)
    e, out = backstop(p.root, '--subst-check', base, p.commit('move-body'), '--names', s_row)
    check('M4 옮긴 본문 다름 — exit 0 · [info] 알림', e == 0 and '[info] 메서드 이동 %s — 옮긴 본문 다름(동작 불변 근거는 명세 · 감수)'
          % LABEL in out, out[-900:])

    # X2 꼴 — 단언 완화
    p.reset(moved)
    p.sub('tests/web/test_home.py', 'assert destination == "/home/"', 'assert destination')
    e, out = backstop(p.root, '--subst-check', base, p.commit('x2'), '--names', s_row)
    check('M5 X2 꼴(단언 한 줄 완화) — exit 2', e == 2 and 'tests/web/test_home.py' in out, out[-900:])

    # 오염 — 옛 판에 승인 자리가 없던 위치(같은 클래스의 다른 메서드 patch)에 새 메서드 자리를 만듦
    p.reset(moved)
    p.sub('tests/web/test_icon.py', 'view_module.LoginVM, "render_initial"', 'view_module.LoginVM, "redirect"')
    e, out = backstop(p.root, '--subst-check', base, p.commit('pollute'), '--names', s_row)
    check('M6 오염(render_initial patch 자리를 redirect 로) — 같은 위치 대응이 아니라 exit 2',
          e == 2 and 'tests/web/test_icon.py' in out, out[-900:])
    p.reset(moved)
    p.sub('tests/web/test_home.py', 'assert HomeVM().render() == "home"', 'assert LoginVM().render() == "home"')
    e, out = backstop(p.root, '--subst-check', base, p.commit('other-method'),
                      '--names', p.spec('render', row(REDIRECT, DOC, 'tests/web/test_home.py::test_render')))
    check('M6 같은 클래스의 다른 메서드(render) 수신자 바꿈 — 승인 대응 밖이라 exit 2',
          e == 2 and 'tests/web/test_home.py' in out, out[-900:])

    # 목록 밖 함수 — test_other 도 바꿈
    p.reset(moved)
    p.sub('tests/web/test_home.py', 'assert HomeVM().redirect(None) is None', 'assert LoginVM().redirect(None) is None')
    other = p.commit('other')
    e, out = backstop(p.root, '--subst-check', base, other, '--names', s_row)
    check('M7 목록 밖 함수(test_other)의 같은 대응 — exit 2', e == 2 and 'tests/web/test_home.py' in out, out[-900:])
    e, out = backstop(p.root, '--subst-check', base, other,
                      '--names', p.spec('other', row(REDIRECT, DOC, 'tests/web/test_home.py::test_other')))
    check('M7 대조: test_other 를 목록에 넣으면 exit 0', e == 0 and '[subst]' not in out, out[-900:])

    # test_misc 의 꼴들 — 함수마다 따로 목록에 넣는다
    def misc(label, old_text, new_text, func, want):
        p.reset(base)
        move_product(p)
        misc_swap(p, old_text, new_text)
        e, out = backstop(p.root, '--subst-check', base, p.commit(label),
                          '--names', p.spec(label, row('tests/web/test_misc.py::%s' % func)))
        ok = (e == 0 and '[subst]' not in out) if want == 0 else (e == 2 and 'tests/web/test_misc.py' in out)
        check('%s — exit %d' % (label, want), ok, 'exit=%d\n%s' % (e, out[-900:]))

    misc('M8 생성자 인자 그대로(seed=1) — (a) 수신자 이름만 표지', 'HomeVM(seed=1).redirect', 'LoginVM(seed=1).redirect', 'test_seed', 0)
    misc('M8 생성자 인자 바뀜(seed=1 → 2) — red', 'HomeVM(seed=1).redirect', 'LoginVM(seed=2).redirect', 'test_seed', 2)
    misc('M9 문자열 patch 대상(검증된 patch API 의 대상 인자) — (d) 정규화',
         'patch("web.home.home_vm.HomeVM.redirect"', 'patch("web.auth.login_vm.LoginVM.redirect"', 'test_patch_string', 0)
    misc('M9 문자열 기대값(단언 안 같은 경로 문자열) — 정규화하지 않는다(red)',
         '"web.home.home_vm.HomeVM.redirect".endswith', '"web.auth.login_vm.LoginVM.redirect".endswith', 'test_expect', 2)
    misc('M10 (e) 한 번 대입된 지역 이름(v = R() · v.m 만) — 정규화', 'vm = HomeVM()\n    result', 'vm = LoginVM()\n    result',
         'test_local', 0)
    misc('M10 (e) 재대입(v = R() 뒤 v = 다른 것) — 자리 아님(red)', 'vm = HomeVM()\n    vm = make_vm()',
         'vm = LoginVM()\n    vm = make_vm()', 'test_rebind', 2)
    misc('M11 내장 setattr(가려지지 않음) — (c) 정규화', 'setattr(HomeVM, "redirect"', 'setattr(LoginVM, "redirect"', 'test_builtin', 0)
    misc('M11 unittest.mock patch.object — (c) 정규화', 'patch.object(HomeVM, "redirect"', 'patch.object(LoginVM, "redirect"',
         'test_patch_object', 0)
    p.reset(base)
    move_product(p)
    misc_swap(p, 'mocker.patch.object(HomeVM, "redirect"', 'mocker.patch.object(LoginVM, "redirect"')
    misc_swap(p, 'mocker.spy(HomeVM, "redirect")', 'mocker.spy(LoginVM, "redirect")')
    e, out = backstop(p.root, '--subst-check', base, p.commit('mocker'),
                      '--names', p.spec('mocker', row('tests/web/test_misc.py::test_mocker')))
    check('M11 fixture mocker.patch.object · mocker.spy — 정규화 2곳', e == 0 and '[subst]' not in out
          and '정규화 tests/web/test_misc.py — 2곳' in out, out[-900:])
    misc('M12 patch API 가림 — 지역 이름 monkeypatch(fixture 인자 아님) red', 'monkeypatch.setattr(HomeVM',
         'monkeypatch.setattr(LoginVM', 'test_local_mp', 2)
    misc('M12 (b) 클래스 속성 참조 R.m — 정규화', 'HomeVM.redirect(HomeVM(), "k")', 'LoginVM.redirect(HomeVM(), "k")',
         'test_static', 0)
    for label, func, old_text, new_text in (
            ('M12 patch API 가림 — 모듈이 setattr 를 정의(내장 아님) red', 'test_shadowed', 'setattr(HomeVM', 'setattr(LoginVM'),
            ('M12 patch API 가림 — 사용자 모듈의 patch(unittest.mock 아님) red', 'test_user_patch', 'with patch.object(HomeVM',
             'with patch.object(LoginVM'),
            ('M12 patch API 가림 — 이 모듈이 mocker 를 따로 정의(pytest-mock fixture 가 아닐 수 있다) red', 'test_own_fixture',
             'mocker.patch.object(HomeVM', 'mocker.patch.object(LoginVM')):
        p.reset(base)
        move_product(p)
        misc_swap(p, old_text, new_text, 'tests/web/test_shadow.py')
        e, out = backstop(p.root, '--subst-check', base, p.commit(func),
                          '--names', p.spec(func, row('tests/web/test_shadow.py::%s' % func)))
        check(label, e == 2 and 'tests/web/test_shadow.py' in out, 'exit=%d\n%s' % (e, out[-900:]))
    misc('M12 같은 줄 앞에 여러 바이트 글자(열 = utf-8 바이트) — 정규화', '("가나다", HomeVM().redirect("키"))',
         '("가나다", LoginVM().redirect("키"))', 'test_korean', 0)
    p.reset(base)
    move_product(p)
    p.sub('tests/web/test_misc.py', 'monkeypatch.setattr("web.home.home_vm.HomeVM.redirect"',
          'monkeypatch.setattr("web.auth.login_vm.LoginVM.redirect"')
    p.sub('tests/web/test_misc.py', 'mocker.patch("web.home.home_vm.HomeVM.redirect"',
          'mocker.patch("web.auth.login_vm.LoginVM.redirect"')
    e, out = backstop(p.root, '--subst-check', base, p.commit('fixture-strings'),
                      '--names', p.spec('fs', row('tests/web/test_misc.py::test_mp_string')))
    check('M12 fixture monkeypatch.setattr("…") · mocker.patch("…") 문자열 대상 — (d) 정규화 2곳', e == 0 and '[subst]' not in out
          and '정규화 tests/web/test_misc.py — 2곳' in out, out[-900:])
    p.reset(base)
    move_product(p)
    p.sub('tests/web/test_misc.py', 'from web.home.home_vm import HomeVM as VM', 'from web.auth.login_vm import LoginVM as VM')
    e, out = backstop(p.root, '--subst-check', base, p.commit('local-import'),
                      '--names', p.spec('li', row('tests/web/test_misc.py::test_local_import')))
    check('M12 함수 안 별칭 import(옛 뺌 · 새 더함 모두 자리 전용) — exit 0 · 알림에 더함 · 뺌', e == 0 and '[subst]' not in out
          and "더함 ['web.auth.login_vm.LoginVM as VM'] · 뺌 ['web.home.home_vm.HomeVM as VM']" in out, out[-900:])
    misc('M13 재수출 4칸 건넘(r1→r2→r3→r4→정의) — 정규화', 'web.re.r1")\n    assert mod.HomeVM()', 'web.re.r1")\n    assert mod.LoginVM()',
         'test_chain4', 0)
    misc('M13 재수출 5칸(4칸 초과) — 해석 불가 · red', 'web.re.q1")\n    assert mod.HomeVM()', 'web.re.q1")\n    assert mod.LoginVM()',
         'test_chain5', 2)
    misc('M13 재수출 순환(c1 ↔ c2) — 해석 불가 · red', 'web.re.c1")\n    assert mod.HomeVM()', 'web.re.c1")\n    assert mod.LoginVM()',
         'test_cycle', 2)

    # 기준 판에 이미 있던 새 메서드 사용 — 정규화하지 않는다(그대로면 같음 · 거꾸로 바꾸면 red)
    p.reset(base)
    p.sub('tests/web/test_home.py', IMPORT_HOME, IMPORT_BOTH)
    p.sub('tests/web/test_home.py', '    assert destination == "/home/"\n',
          '    assert destination == "/home/"\n    assert LoginVM().redirect("z") == "/home/"\n')
    pre = p.commit('pre-existing')
    move_product(p)
    p.sub('tests/web/test_home.py', 'destination = HomeVM().redirect("k")', 'destination = LoginVM().redirect("k")')
    e, out = backstop(p.root, '--subst-check', pre, p.commit('pre-move'), '--names', p.spec('pre', row(REDIRECT)))
    check('M14 기준 판에 이미 있던 새 메서드 사용 — 그대로 두면 exit 0 · 정규화는 옛 자리 1곳뿐',
          e == 0 and '정규화 tests/web/test_home.py — 1곳' in out, out[-900:])
    p.reset(pre)
    move_product(p)
    p.sub('tests/web/test_home.py', 'destination = HomeVM().redirect("k")', 'destination = LoginVM().redirect("k")')
    p.sub('tests/web/test_home.py', 'assert LoginVM().redirect("z")', 'assert HomeVM().redirect("z")')
    e, out = backstop(p.root, '--subst-check', pre, p.commit('reverse'), '--names', p.spec('pre', row(REDIRECT)))
    check('M14 역방향(새 → 옛) 자리 — 정규화하지 않는다(exit 2)', e == 2 and 'tests/web/test_home.py' in out, out[-900:])

    # 이름도 바뀌는 이동(redirect → go)
    p.reset(base)
    move_product(p, login_vm=LOGIN_VM_MOVED.replace('def redirect(', 'def go('))
    p.w('web/auth/login_view.py', LOGIN_VIEW_MOVED.replace('view_model.redirect(key)', 'view_model.go(key)'))
    move_tests(p)
    p.sub('tests/web/test_home.py', 'LoginVM().redirect("k")', 'LoginVM().go("k")')
    p.sub('tests/web/test_icon.py', 'view_module.LoginVM, "redirect"', 'view_module.LoginVM, "go"')
    e, out = backstop(p.root, '--subst-check', base, p.commit('rename'),
                      '--names', p.spec('go', row(REDIRECT, DOC, new='web.auth.login_vm.LoginVM.go')))
    check('M15 메서드 이름도 바뀌는 이동(redirect → go) — exit 0', e == 0 and '[subst]' not in out, out[-900:])

    # 제품 쪽 확인
    p.reset(base)
    move_product(p, home_vm=HOME_VM)
    move_tests(p)
    e, out = backstop(p.root, '--subst-check', base, p.commit('copy'), '--names', s_row)
    check('M16 옛 메서드가 대상 판에 남음(복사) — 이동이 아니다(exit 2)',
          e == 2 and '[subst] 메서드 이동 %s — 대상 판' % LABEL in out and '옛 메서드 def 가 남아 있다(이동이 아니다)' in out, out[-900:])
    e, out = backstop(p.root, '--subst-check', base, moved,
                      '--names', p.spec('nonew', row(REDIRECT, DOC, new='web.auth.login_vm.LoginVM.redirect2')))
    check('M16 새 메서드 def 가 대상 판에 없음 — exit 2', e == 2 and '새 메서드 def 가 없다' in out, out[-900:])
    e, out = backstop(p.root, '--subst-check', base, moved,
                      '--names', p.spec('noold', row(REDIRECT, DOC, old='web.home.home_vm.HomeVM.missing')))
    check('M16 옛 메서드 def 가 기준 판에 없음 — exit 2', e == 2 and '옛 메서드 def 가 없다' in out, out[-900:])

    # 대응 충돌 — 판정 불가(exit 1)
    for label, rows in (
            ('같은 옛 메서드 두 행', (row(REDIRECT), row(REDIRECT, new='web.auth.login_vm.LoginVM.go'))),
            ('여러 옛 → 한 새', (row(REDIRECT), row(REDIRECT, old='web.home.home_vm.HomeVM.render'))),
            ('역방향(A→B · B→A)', (row(REDIRECT), row(REDIRECT, old=NEW, new=OLD))),
            ('`이름:` 행과 클래스 경로 겹침', (row(REDIRECT), '이름: web.home.home_vm.HomeVM → web.auth.login_vm.LoginVM'))):
        e, out = backstop(p.root, '--subst-check', base, moved, '--names', p.spec('conflict', *rows))
        check('M17 대응 충돌 — %s · 판정 불가(exit 1)' % label, e == 1 and '메서드 이동 대응 충돌' in out, out[-600:])
    p.reset(moved)
    p.sub('tests/web/test_home.py', 'def test_redirect():\n', 'def test_redirect():\n    # __dddjango_m0__\n')
    e, out = backstop(p.root, '--subst-check', base, p.commit('marker'), '--names', s_row)
    check('M17 대응 충돌 — 표지 이름이 원문에 이미 있음 · 판정 불가(exit 1)', e == 1 and '표지 이름' in out, out[-600:])

    # 꼴이 어긋난 행 — 승인으로 읽지 않고 알림도 없다(행 없음과 byte 동일)
    base_out = backstop(p.root, '--subst-check', base, moved, '--names', s_none)
    for label, line in (('· 시험 부분 없음', '메서드 이동: %s → %s' % (OLD, NEW)),
                        ('클래스 소문자', row(REDIRECT, old='web.home.home_vm.homevm.redirect')),
                        ('클래스 안 시험(::Class::func)', row('tests/web/test_home.py::TestX::test_redirect')),
                        ('시험 파일이 아님', row('web/home/home_vm.py::render'))):
        got = backstop(p.root, '--subst-check', base, moved, '--names', p.spec('bad', line))
        check('M18 꼴 어긋난 행(%s) — 행 없음과 byte 동일(알림 없음)' % label, got == base_out, got[1][-600:])
    got = backstop(p.root, '--subst-check', base, moved, '--names', p.spec('fence', '```', row(REDIRECT, DOC), '```'))
    check('M18 코드 울타리 안 행 — 읽지 않는다', got == base_out, got[1][-600:])
    got = backstop(p.root, '--subst-check', base, moved,
                   '--names', p.spec('outside', head='## 슬라이스 0', pre='## 다른 절\n\n%s\n' % row(REDIRECT, DOC)))
    check('M18 절 밖 행 — 읽지 않는다', got == base_out, got[1][-600:])


# ====================================================================== T — 0T 시험 전환(합성 · case1 꼴)

STATUS = '''class Status:
    ENTERED = "entered"
    EMPTY = "empty"
'''
UI_VM = '''class UserInfoVM:
    def __init__(self, started: bool, status: str) -> None:
        self.started = started
        self.status = status

    def enter(self) -> str:
        return "choice" if self.status == "entered" else "page"
'''
UI_VIEW = '''from web.intake.user_info_vm import UserInfoVM


class _Ctx:
    started: bool
    status: str


def user_info_view(request):
    view_model = UserInfoVM(request.started, request.status)
    if request.route == "page":
        return _render_page(request, view_model)
    return None


def _render_page(request, view_model):
    if view_model.enter() == "choice":
        return "redirect"
    return "page"
'''
UI_VIEW_INLINED = '''from web.intake.user_info_vm import UserInfoVM


class _Ctx:
    started: bool
    status: str


def user_info_view(request):
    view_model = UserInfoVM(request.started, request.status)
    if request.route == "page":
        if view_model.enter() == "choice":
            return "redirect"
        return "page"
    return None
'''
GATE = '''from types import SimpleNamespace

from web.intake.status import Status
from web.intake.user_info_vm import UserInfoVM

_CHOICE: str = "redirect"


def test_gate(mocker):
    """도움 함수가 선택 필요를 redirect 로 옮긴다."""
    page_url = "/user-info/"
%s

def test_other():
    assert Status.EMPTY == "empty"
'''
GATE_OLD = '''    from web.intake.user_info_view import _render_page

    request = SimpleNamespace(path=page_url)
    mocker.patch.object(UserInfoVM, "enter", return_value="choice")

    response = _render_page(request, UserInfoVM(started=False, status=Status.ENTERED))

    assert response == _CHOICE
    assert isinstance(response, str)
'''
GATE_NEW = '''    from typing import cast
    from web.intake.user_info_view import _Ctx, user_info_view

    request = SimpleNamespace(path=page_url)
    request.route = "page"
    context = cast("_Ctx", request)
    context.started = False
    context.status = Status.ENTERED
    mocker.patch.object(UserInfoVM, "enter", return_value="choice")

    response = user_info_view(request)

    assert response == _CHOICE
    assert isinstance(response, str)
'''
GATE_PATH = 'tests/web/test_gate.py'
SWITCH_ROW = ('시험 전환: %s::test_gate · 행위 web.intake.user_info_view._render_page → web.intake.user_info_view.user_info_view'
              ' · 보호 분기 web/intake/user_info_view.py:11-12 · 반례 test-switch/1.mutant.diff' % GATE_PATH)


def mk_switch(tmp, name='sw'):
    p = Proj(tmp / name)
    for rel in ('web/__init__.py', 'web/intake/__init__.py'):
        p.w(rel, '')
    p.w('web/intake/status.py', STATUS)
    p.w('web/intake/user_info_vm.py', UI_VM)
    p.w('web/intake/user_info_view.py', UI_VIEW)
    p.w('config/settings.py', "SECRET_KEY = 'x'\n")
    p.w(GATE_PATH, GATE % GATE_OLD)
    p.w('tests/web/test_misc.py', 'def test_misc():\n    assert 1 == 1\n')
    return p, p.commit('base')


def ts(state, commits, cancels=None):
    record = {'state': state, 'commits': commits, 'evidence': 'test-switch/evidence.json'}
    if cancels is not None:
        record['cancel_commits'] = cancels
    return record


def bundle_switch(tmp):
    p, base = mk_switch(tmp)
    spec = p.spec('switch', SWITCH_ROW)
    p.w(GATE_PATH, GATE % GATE_NEW)
    t = p.commit('0T')
    p.w('web/intake/user_info_view.py', UI_VIEW_INLINED)
    c = p.commit('0C')

    def run(target, slices, *extra, start=base, names=spec):
        return backstop(p.root, '--subst-check', start, target, '--build', p.build('b', slices), '--names', names, *extra)

    zero = [{'name': 'slice-0-debt', 'commits': [t, c]}]
    e, out = run(c, zero)
    check('T1 test_switch 기록 없음 — 지금처럼 red(exit 2)', e == 2 and GATE_PATH in out, out[-900:])
    e, out = run(c, [dict(zero[0], test_switch=ts('verified', [t]))])
    check('T2 0T(검증됨) + 0C — case1 꼴(함수 안 import · 준비 대입 · 행위 바꿈) exit 0',
          e == 0 and '[subst]' not in out and 'web/ 밖 변경 파일 1' in out, out[-1500:])
    e, out = run(t, [{'name': 'slice-0-debt', 'commits': [t], 'test_switch': ts('prepared', [t])}])
    check('T3 0T 시점(state=prepared · 0C 없음) — exit 0', e == 0 and '[subst]' not in out, out[-900:])
    e, out = run(c, [dict(zero[0], test_switch=ts('prepared', [t]))])
    check('T3 검증 전(state=prepared)에 0C 커밋 — exit 2', e == 2 and '0T 검증 전(state=prepared)' in out, out[-900:])

    def variant(label, edit, want_reason, rows=None):
        p.reset(base)
        p.w(GATE_PATH, edit(GATE % GATE_NEW))
        tv = p.commit(label)
        e, out = run(tv, [{'name': 'slice-0-debt', 'commits': [tv], 'test_switch': ts('verified', [tv])}],
                     names=p.spec('v', *(rows or [SWITCH_ROW])))
        check('%s — exit 2 · %s' % (label, want_reason), e == 2 and want_reason in out
              and '— 0T 커밋 %s' % tv[:12] in out, 'exit=%d\n%s' % (e, out[-1200:]))

    rep = lambda old, new: (lambda text: text.replace(old, new, 1) if old in text else text + '\n#픽스처오류')
    variant('T4 X1 꼴(단언 한 줄 완화)', rep('assert isinstance(response, str)', 'assert isinstance(response, (str, bytes))'),
            '0T 시험 전환 test_gate — 단언 문장이 다르다')
    variant('T5 응답 직접 생성(새 행위 없음)', rep('response = user_info_view(request)', 'response = _CHOICE'),
            '0T 시험 전환 test_gate — 새 행위 문장')
    variant('T5 승인 밖 대상 호출', rep('response = user_info_view(request)', 'response = other_view(request)'),
            '0T 시험 전환 test_gate — 새 행위 문장')
    variant('T6 입력 값 바꿈(ENTERED → EMPTY)', rep('context.status = Status.ENTERED', 'context.status = Status.EMPTY'),
            '0T 시험 전환 test_gate — 옛 행위 입력 값')
    variant('T6 입력 하나 뺌(started)', rep('    context.started = False\n', ''), '0T 시험 전환 test_gate — 옛 행위 입력 값')
    variant('T7 patch 반환값 바꿈', rep('return_value="choice"', 'return_value="page"'), '0T 시험 전환 test_gate — 뺀 문장')
    variant('T7 patch 더함', rep('    response = user_info_view', '    mocker.patch.object(UserInfoVM, "__init__", return_value=None)\n'
                                '    response = user_info_view'), '0T 시험 전환 test_gate — 더한 문장')
    variant('T7 속성 대입으로 제품 바꿈(UserInfoVM.enter = …)',
            rep('    response = user_info_view', '    UserInfoVM.enter = lambda self: "choice"\n    response = user_info_view'),
            '0T 시험 전환 test_gate — 더한 문장이 patch · mock 이다')
    variant('T7 patch 대입 꼴(fake = mocker.patch.object(…))',
            rep('    response = user_info_view', '    fake = mocker.patch.object(UserInfoVM, "__init__", return_value=None)\n'
                '    response = user_info_view'), '0T 시험 전환 test_gate — 더한 문장이 patch · mock 이다')
    variant('T7 patch 를 부르지 않고 꺼내기만(g = getattr(mocker, "patch"))',
            rep('    response = user_info_view', '    g = getattr(mocker, "patch")\n    response = user_info_view'),
            '0T 시험 전환 test_gate — 더한 문장이 patch · mock 이다')
    variant('T7 이미 있는 이름을 다시 바인딩(UserInfoVM = …) — 남은 patch 문장의 뜻이 바뀐다',
            rep('    request = SimpleNamespace', '    UserInfoVM = SimpleNamespace\n    request = SimpleNamespace'),
            '0T 시험 전환 test_gate — 더한 문장이 이미 있는 이름 UserInfoVM 를 다시 바인딩한다')
    variant('T7 새 준비 · 새 행위 입력이 아닌 지역 객체를 고침(page_url.x = …)',
            rep('    response = user_info_view', '    page_url.x = 1\n    response = user_info_view'),
            '0T 시험 전환 test_gate — 더한 문장이 새 준비 · 새 행위 입력이 아닌 객체 page_url 를 고친다')
    p.reset(base)
    p.w(GATE_PATH, (GATE % GATE_NEW).replace('    context.started = False\n',
                                             '    box = SimpleNamespace("k")\n    box.started = False\n'
                                             '    context.started = box.started\n'))
    tv = p.commit('local-object')
    e, out = run(tv, [{'name': 'slice-0-debt', 'commits': [tv], 'test_switch': ts('verified', [tv])}])
    check('T7 대조: 글자 인자 하나로 만든 지역 객체의 속성 대입은 준비다 — exit 0', e == 0 and '[subst]' not in out, out[-900:])
    variant('T8 fixture 인자 더함', rep('def test_gate(mocker):', 'def test_gate(mocker, client):'),
            '0T 시험 전환 test_gate — 함수 머리')
    variant('T8 decorator 더함', rep('def test_gate(mocker):', '@slow\ndef test_gate(mocker):'), '0T 시험 전환 test_gate — 함수 머리')
    variant('T8 함수 이름 바꿈', rep('def test_gate(mocker):', 'def test_gate_view(mocker):'), '0T 시험 전환 test_gate — 최상위 함수')
    variant('T9 단언이 읽는 이름 재준비', rep('    response = user_info_view', '    _CHOICE = "redirect"\n    response = user_info_view'),
            '0T 시험 전환 test_gate — 더한 문장이 단언이 읽는 이름')
    variant('T9 더한 import 안 쓰임', rep('    from typing import cast\n', '    from typing import cast\n    from os import path\n'),
            '0T 시험 전환 test_gate — 더한 import')
    variant('T9 뺀 문장이 행위 · 그 import 가 아님(docstring 뺌)', rep('    """도움 함수가 선택 필요를 redirect 로 옮긴다."""\n', ''),
            '0T 시험 전환 test_gate — 뺀 문장')
    variant('T10 행 밖 함수(test_other) 바꿈', rep('assert Status.EMPTY == "empty"', 'assert Status.EMPTY'),
            '0T 시험 전환 — 행에 적힌 함수 밖 모듈 내용이 다르다')
    variant('T10 행에 없는 시험 파일 내용', lambda text: text, '0T 시험 전환 — 명세 `시험 전환:` 행에 없는 시험 파일',
            rows=[SWITCH_ROW.replace(GATE_PATH, 'tests/web/test_misc.py').replace('::test_gate', '::test_misc')])

    # T 이력
    def history(label, steps, slices_of, want_exit, want, *extra, target=None):
        p.reset(base)
        shas = []
        for step in steps:
            step()
            shas.append(p.commit(label))
        e, out = run(target(shas) if target else shas[-1], slices_of(shas), *extra)
        ok = e == want_exit and (want in out if want else '[subst]' not in out)
        check('%s — exit %d%s' % (label, want_exit, ' · ' + want if want else ''), ok, 'exit=%d\n%s' % (e, out[-1200:]))

    def gate_new():
        p.w(GATE_PATH, GATE % GATE_NEW)

    def inline():
        p.w('web/intake/user_info_view.py', UI_VIEW_INLINED)

    def web_touch():
        p.w('web/intake/status.py', STATUS + '# touched\n')

    def web_back():
        p.w('web/intake/status.py', STATUS)

    def zero_with(shas, record, extra_slices=()):
        return [{'name': 'slice-0-debt', 'commits': list(shas), 'test_switch': record}, *extra_slices]

    history('T11 0T 커밋이 제품을 바꾼 뒤 다음 0T 가 되돌림', [lambda: (gate_new(), web_touch()), web_back, inline],
            lambda s: zero_with(s, ts('verified', s[:2])), 2, '가 web/ 을 바꿨다')
    history('T12 --except 우회(0T 가 web/ 밖 비테스트를 바꿈)', [lambda: (gate_new(), p.w('config/settings.py', "SECRET_KEY = 'y'\n")), inline],
            lambda s: zero_with(s, ts('verified', s[:1])), 2, '시험 전환 행 밖 파일을 바꿨다', '--except', 'config/settings.py')
    history('T13 기능 슬라이스와 겹침(0T 커밋이 slices[1] 에만)', [gate_new, inline],
            lambda s: zero_with(s[1:], ts('verified', s[:1]), ({'name': 'slice-1', 'commits': s[:1]},)), 2,
            'slices[0] commits 에 없다')
    history('T14 첫 0C 뒤 0T', [inline, gate_new], lambda s: zero_with(s, ts('verified', s[1:])), 2, '첫 0C 커밋')
    history('T14 기록 없는 커밋이 0T 앞에서 제품을 바꿈', [inline, gate_new], lambda s: zero_with(s[1:], ts('verified', s[1:])), 2,
            '0T 앞 커밋')
    history('T15 0T 뒤 0C 가 시험을 다시 고침(단언)', [gate_new, lambda: (inline(), p.w(GATE_PATH, (GATE % GATE_NEW).replace(
        'assert response == _CHOICE', 'assert response')))], lambda s: zero_with(s, ts('verified', s[:1])), 2, '치환만으로 설명되지 않는다')

    def move_view():
        git(p.root, 'mv', 'web/intake/user_info_view.py', 'web/intake/view_user_info.py')
        p.w(GATE_PATH, (GATE % GATE_NEW).replace('web.intake.user_info_view import', 'web.intake.view_user_info import'))

    history('T15 대조: 0T 뒤 S 구간은 0T 끝 판에서 — 개명 + import 경로 치환만이면 exit 0',
            [gate_new, move_view, lambda: p.w('web/intake/view_user_info.py', UI_VIEW_INLINED)],
            lambda s: zero_with(s, ts('verified', s[:1])), 0, None)
    history('T16 여러 0T 커밋(준비 · 행위 나눠) — 한 창으로 대조 exit 0',
            [lambda: p.w(GATE_PATH, GATE % GATE_NEW.replace('    response = user_info_view(request)\n',
                                                           '    response = _render_page(request, UserInfoVM(started=False, '
                                                           'status=Status.ENTERED))\n').replace(
                '_Ctx, user_info_view', '_Ctx, _render_page, user_info_view')), gate_new, inline],
            lambda s: zero_with(s, ts('verified', s[:2])), 0, None)
    history('T17 0T 커밋이 사슬에 없음(풀 수 없는 해시)', [gate_new, inline],
            lambda s: zero_with(s, ts('verified', ['deadbeefdeadbeef'])), 2, '풀 수 없다')
    history('T17 0T 커밋이 기준..대상 사슬 밖(기준 커밋 자신)', [gate_new, inline],
            lambda s: zero_with(s, ts('verified', [base])), 2, '첫 부모 사슬 밖')

    p.reset(base)
    gate_new()
    t1 = p.commit('0T')
    git(p.root, 'revert', '--no-edit', t1)
    x1 = git(p.root, 'rev-parse', 'HEAD')
    inline()
    c1 = p.commit('0C')
    e, out = run(c1, zero_with([t1, x1, c1], ts('cancelled', [t1], [x1])))
    check('T18 0T 취소(정확한 역 커밋) — 둘 다 비교에서 빼고 exit 0', e == 0 and '[subst]' not in out, out[-900:])
    e, out = run(c1, zero_with([t1, x1, c1], ts('verified', [t1], [x1])))
    check('T18 취소 커밋이 있는데 state=verified — 기록 모순 exit 2', e == 2 and '기록 모순' in out, out[-900:])
    e, out = run(c1, zero_with([t1, x1, c1], ts('cancelled', [t1])))
    check('T18 state=cancelled 인데 취소 커밋 없음 — exit 2', e == 2 and '취소 커밋이 없다' in out, out[-900:])
    p.reset(t1)
    p.w(GATE_PATH, (GATE % GATE_OLD).replace('assert isinstance(response, str)', 'assert response'))
    x2 = p.commit('partial-revert')
    inline()
    c2 = p.commit('0C')
    e, out = run(c2, zero_with([t1, x2, c2], ts('cancelled', [t1], [x2])))
    check('T18 취소가 시험 파일을 다 되돌리지 않음 — exit 2', e == 2 and '0T 취소가 시험 파일을 되돌리지 않았다' in out, out[-900:])
    e, out = run(c, [dict(zero[0], test_switch={'state': 'done', 'commits': [t]})])
    check('T19 test_switch state 값 오류 — 판정 불가(exit 1)', e == 1 and 'test_switch' in out, out[-600:])
    e, out = run(c, [dict(zero[0], test_switch=[t])])
    check('T19 test_switch 가 객체가 아님 — 판정 불가(exit 1)', e == 1 and 'test_switch' in out, out[-600:])
    for label, rows in (('같은 시험 함수 두 행', (SWITCH_ROW, SWITCH_ROW.replace('test-switch/1', 'test-switch/2'))),
                        ('옛 대상 = 새 대상', (SWITCH_ROW.replace('→ web.intake.user_info_view.user_info_view',
                                                              '→ web.intake.user_info_view._render_page'),))):
        e, out = run(c, [dict(zero[0], test_switch=ts('verified', [t]))], names=p.spec('dup', *rows))
        check('T20 시험 전환 행 충돌 — %s · 판정 불가(exit 1)' % label, e == 1 and '시험 전환' in out, out[-600:])


# ====================================================================== U — 무변(새 입력 없음 — byte 대조)

def bundle_unchanged(tmp):
    if old_scripts() is None:
        return
    p, base = mk_move(tmp)
    move_product(p)
    move_tests(p)
    moved = p.commit('move')
    same_as_old('U1 메서드 이동 꼴 · 행 없음(--names 없음)', p.root, '--subst-check', base, moved)
    same_as_old('U2 `이름:` 행만 있는 명세', p.root, '--subst-check', base, moved, '--names',
                p.spec('names', '이름: web.home.home_vm.HomeVM.render → web.home.home_vm.HomeVM.show'))
    for i, line in enumerate(('메서드 이동: %s → %s' % (OLD, NEW), row(REDIRECT, old='web.home.home_vm.homevm.redirect'),
                              row('tests/web/test_home.py::TestX::test_redirect'), row('web/home/home_vm.py::render'),
                              '메서드 이동: 설명 산문 — 다음 판에서')):
        same_as_old('U3 꼴 어긋난 `메서드 이동:` 줄 %d' % (i + 1), p.root, '--subst-check', base, moved, '--names',
                    p.spec('bad%d' % i, line))
    same_as_old('U4 울타리 · 절 밖 `메서드 이동:` 행', p.root, '--subst-check', base, moved, '--names',
                p.spec('fence', '```', row(REDIRECT, DOC), '```', pre='## 다른 절\n\n%s\n' % row(REDIRECT, DOC)))
    q, qbase = mk_switch(tmp, 'sw-u')
    q.w(GATE_PATH, GATE % GATE_NEW)
    t = q.commit('0T')
    q.w('web/intake/user_info_view.py', UI_VIEW_INLINED)
    c = q.commit('0C')
    same_as_old('U5 0T 꼴 · test_switch 기록 없음(--build)', q.root, '--subst-check', qbase, c, '--build',
                q.build('u5', [{'name': 'slice-0-debt', 'commits': [t, c]}]))
    same_as_old('U6 같은 변경을 기능 슬라이스로(--build)', q.root, '--subst-check', qbase, c, '--build',
                q.build('u6', [{'name': 'slice-0-debt', 'commits': [c]}, {'name': 'slice-1', 'commits': [t]}]))
    same_as_old('U7 --build 없음', q.root, '--subst-check', qbase, c)
    q.reset(qbase)
    git(q.root, 'mv', 'web/intake/user_info_view.py', 'web/intake/view_user_info.py')
    q.w(GATE_PATH, (GATE % GATE_OLD).replace('web.intake.user_info_view import', 'web.intake.view_user_info import'))
    same_as_old('U8 개명 + import 경로 치환(green)', q.root, '--subst-check', qbase, q.commit('mv'))


# ====================================================================== R — 재현 장면(sc1)

SCENE_COMMITS = {'base0': 'c527da876', 'case1': 'e06edc4f2', 'case2': '43e5c9500', 'X1': 'b591b79a6',
                 'X2': '68b42dfe0', 'Y1': 'ab54e6940', 'Y2': '38846d129'}
HOME_T = 'tests/web/home/test_home_conversation.py'
ICON_T = 'tests/web/design_system/test_icon_button_soft_variant.py'
GATE_T = 'tests/web/intake/test_user_info_employee_gate.py'
UIV = 'web/application/intake/presentation_layer/view/user_info_view.py'
SC_OLD = 'web.home.home.view_model.home_view_model.HomeViewModel.redirect_authenticated'
SC_NEW = 'web.application.auth.application_layer.login.view_model.login_vm.LoginVM.redirect_authenticated'
SC_HOME_F = HOME_T + '::test_login_redirect_contract_does_not_load_conversation'
SC_ICON_F = ICON_T + '::test_guest_document_keeps_guest_styles_and_does_not_load_operator_styles'
SC_GATE_F = 'test_render_page_redirects_when_employee_choice_required'
SC_SWITCH = ('시험 전환: %s::%s · 행위 web.application.intake.presentation_layer.view.user_info_view._render_page → '
             'web.application.intake.presentation_layer.view.user_info_view.user_info_view · 보호 분기 %s:85-92 · '
             '반례 test-switch/1.mutant.diff' % (GATE_T, SC_GATE_F, UIV))


SCENE_STAMP = '\n# 2.3.1 fixture(scene_commit) — 장면에 없는 객체\n'.encode('utf-8')


def scene_commit(root, parent, files, message):
    """작업 트리 없이(임시 index) parent 위에 files(경로 → bytes) 를 얹은 커밋. 파일 끝에 표지 주석을 붙여 blob · 그 위
    tree 가 모두 장면에 없는 새 객체가 되게 한다 — git 은 이미 있는 객체를 다시 쓰면 대체 저장소(장면) 파일의 mtime 을
    건드린다."""
    index = root / '.git' / 'fixture-index'
    env = dict(ENV, GIT_INDEX_FILE=str(index))
    git(root, 'read-tree', parent, env=env)
    for path, data in files.items():
        blob = git(root, 'hash-object', '-w', '--stdin', data=data + SCENE_STAMP)
        git(root, 'update-index', '--add', '--cacheinfo', '100644,%s,%s' % (blob, path), env=env)
    tree = git(root, 'write-tree', env=env)
    index.unlink()
    return git(root, 'commit-tree', tree, '-p', parent, '-m', message)


def scene_snapshot(scene):
    """장면 저장소 .git 과 그 대체 저장소(objects/info/alternates 사슬)의 파일 → (크기, mtime)."""
    todo, seen, found = [Path(scene) / '.git'], set(), {}
    while todo:
        top = todo.pop()
        if top in seen or not top.is_dir():
            continue
        seen.add(top)
        for cur, _dirs, names in os.walk(top):
            for name in names:
                stat = (Path(cur) / name).stat()
                found[str(Path(cur) / name)] = (stat.st_size, stat.st_mtime_ns)
        for listed in (top / 'objects' / 'info' / 'alternates', top / 'info' / 'alternates'):
            if listed.is_file():
                todo.extend(Path(line) for line in listed.read_text(encoding='utf-8').split('\n') if line.strip())
    return found


def bundle_scene(tmp):
    if not SCENE or not (Path(SCENE) / '.git').exists():
        print('SKIP R — 재현 장면 없음(DDDJANGO_WEB_F75_SCENE 미설정 · 경로 없음) — 실패로 세지 않는다')
        return
    before = scene_snapshot(SCENE)
    try:
        scene_checks(tmp)
    finally:
        after = scene_snapshot(SCENE)
        changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        check('R9 장면 저장소 무변 — .git(대체 저장소 포함) 파일 %d개의 크기 · mtime 그대로' % len(before), not changed, changed[:10])


def scene_checks(tmp):
    root = tmp / 'sc'
    subprocess.run(['git', 'clone', '-q', '--shared', '--no-checkout', SCENE, str(root)], check=True, env=ENV,
                   capture_output=True)
    c = {k: git(root, 'rev-parse', v + '^{commit}') for k, v in SCENE_COMMITS.items()}
    git(root, 'update-ref', '--no-deref', 'HEAD', c['base0'])     # 대상이 HEAD 가 아니게(작업 트리 없음)
    spec_dir = tmp / 'spec'
    spec_dir.mkdir()

    def spec(name, *rows):
        path = spec_dir / (name + '.md')
        path.write_text('# 측정용 명세\n\n## 슬라이스 0\n\n%s\n' % '\n'.join(rows), encoding='utf-8')
        return path

    def build(name, slices):
        folder = tmp / ('build-' + name)
        folder.mkdir()
        (folder / 'build-state.json').write_text(json.dumps({'mode': 'modify', 'slices': slices}), encoding='utf-8')
        return folder

    name_row = spec('name-row', '이름: %s → %s' % (SC_OLD, SC_NEW))
    class_row = spec('class-row', '이름: %s → %s' % (SC_OLD.rsplit('.', 1)[0], SC_NEW.rsplit('.', 1)[0]))
    for label, args in (('case1', (c['base0'], c['case1'])), ('case2', (c['base0'], c['case2'])),
                        ('X1', (c['base0'], c['X1'])), ('X2', (c['base0'], c['X2'])), ('Y1', (c['Y1'] + '^', c['Y1'])),
                        ('Y2', (c['base0'], c['Y2'])), ('case2 `이름:` 메서드 경로 행', (c['base0'], c['case2'], '--names', name_row)),
                        ('case2 `이름:` 클래스 행', (c['base0'], c['case2'], '--names', class_row)),
                        ('case1 slices[0] 기록', (c['base0'], c['case1'], '--build',
                                                build('u-case1', [{'name': 'slice-0-debt', 'commits': [c['case1']]}])))):
        same_as_old('R0 장면 %s — 새 입력 없음' % label, root, '--subst-check', *args)
    move = spec('move', '메서드 이동: %s → %s · 시험 %s %s' % (SC_OLD, SC_NEW, SC_HOME_F, SC_ICON_F))
    e, out = backstop(root, '--subst-check', c['base0'], c['case2'], '--names', move)
    check('R1 장면 case2(home · icon) + 메서드 이동 행 — exit 0', e == 0 and '[subst]' not in out, out[-1500:])
    check('R1 옮긴 본문 다름 알림(reverse → HomeNavigator)', '옮긴 본문 다름' in out, out[-900:])
    e, out = backstop(root, '--subst-check', c['base0'], c['case2'], '--names', move, '--build',
                      build('case2', [{'name': 'slice-0-debt', 'commits': [c['case2']]}]))
    check('R1 같은 장면 --build(slices[0]) — exit 0', e == 0 and '[subst]' not in out, out[-900:])
    e, out = backstop(root, '--subst-check', c['base0'], c['X2'], '--names', move)
    check('R2 장면 X2(단언 완화) + 행 — exit 2', e == 2 and HOME_T in out, out[-900:])
    e, out = backstop(root, '--subst-check', c['base0'], c['case2'], '--names',
                      spec('icon-only', '메서드 이동: %s → %s · 시험 %s' % (SC_OLD, SC_NEW, SC_ICON_F)))
    check('R3 장면 목록 밖 함수(home 시험 빠짐) — exit 2', e == 2 and HOME_T in out and ICON_T + ':' not in out, out[-900:])
    icon = git(root, 'show', '%s:%s' % (c['case2'], ICON_T))
    polluted = icon.replace('monkeypatch.setattr(view_module.LoginVM, "render_initial"',
                            'monkeypatch.setattr(view_module.LoginVM, "redirect_authenticated"', 1)
    check('R4 픽스처 자체 — :318 오염 꼴을 만들었다', polluted != icon)
    pc = scene_commit(root, c['case2'], {ICON_T: polluted.encode('utf-8')}, 'pollute 318')
    e, out = backstop(root, '--subst-check', c['base0'], pc, '--names', move)
    check('R4 장면 :318 오염(render_initial patch 자리를 옮긴 메서드로) — exit 2', e == 2 and ICON_T in out, out[-900:])
    home = git(root, 'show', '%s:%s' % (c['case2'], HOME_T))
    seeded = home.replace('LoginVM().redirect_authenticated(', 'LoginVM(1).redirect_authenticated(', 1)
    check('R4 픽스처 자체 — 생성자 인자 바꾼 꼴을 만들었다', seeded != home)
    sc = scene_commit(root, c['case2'], {HOME_T: seeded.encode('utf-8')}, 'ctor arg')
    e, out = backstop(root, '--subst-check', c['base0'], sc, '--names', move)
    check('R4 장면 생성자 인자 바꿈(LoginVM(1)) — 자리는 표시되지만 인자가 달라 exit 2',
          e == 2 and '[subst] ' + HOME_T in out and '정규화 %s — 1곳' % HOME_T in out, out[-900:])
    gate_new = subprocess.run(['git', '-C', str(root), 'show', '%s:%s' % (c['case1'], GATE_T)], capture_output=True,
                              env=ENV, check=True).stdout
    view_new = subprocess.run(['git', '-C', str(root), 'show', '%s:%s' % (c['case1'], UIV)], capture_output=True,
                              env=ENV, check=True).stdout
    t = scene_commit(root, c['base0'], {GATE_T: gate_new}, '0T')
    c0 = scene_commit(root, t, {UIV: view_new}, '0C')
    sw = spec('switch', SC_SWITCH)
    e, out = backstop(root, '--subst-check', c['base0'], c0, '--names', sw, '--build',
                      build('case1', [{'name': 'slice-0-debt', 'commits': [t, c0],
                                       'test_switch': {'state': 'verified', 'commits': [t], 'evidence': 'x'}}]))
    check('R5 장면 case1 = 0T(시험만) + 0C(제품만) 기록 — exit 0', e == 0 and '[subst]' not in out, out[-1500:])
    loose = gate_new.replace(b'assert response.status_code == 302', b'assert response.status_code in (301, 302)')
    check('R6 픽스처 자체 — X1 꼴 단언 완화를 만들었다', loose != gate_new)
    tx = scene_commit(root, c['base0'], {GATE_T: loose}, '0T-loose')
    e, out = backstop(root, '--subst-check', c['base0'], tx, '--names', sw, '--build',
                      build('x1', [{'name': 'slice-0-debt', 'commits': [tx],
                                    'test_switch': {'state': 'verified', 'commits': [tx], 'evidence': 'x'}}]))
    check('R6 장면 X1 꼴 0T(단언 완화) — exit 2 · 단언 문장이 다르다', e == 2 and '단언 문장이 다르다' in out, out[-1200:])


def main():
    bundles = [bundle_unchanged, bundle_move, bundle_switch, bundle_scene]
    only = set(sys.argv[1:])
    _OLD['tmp'] = tempfile.TemporaryDirectory(prefix='web231-old-')
    try:
        for bundle in bundles:
            if only and bundle.__name__[len('bundle_'):] not in only:
                continue
            with tempfile.TemporaryDirectory(prefix='web231-') as tmp:
                try:
                    bundle(Path(tmp))
                except Exception as error:  # noqa: BLE001 — 묶음이 죽어도 실패로 세고 다음 묶음을 돈다
                    check('%s — 묶음 실행 오류' % bundle.__name__, False, '%s: %s' % (type(error).__name__, error))
    finally:
        _OLD['tmp'].cleanup()
    print('2.3.1 치환 확인 픽스처: PASS %d / FAIL %d' % (PASS, FAIL))
    return bool(FAIL)


if __name__ == '__main__':
    sys.exit(main())
