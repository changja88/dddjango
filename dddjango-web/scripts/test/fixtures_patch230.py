"""2.3.0 제품 선언(web/product_registry.json) 회귀 픽스처 — 임시 git 저장소만 만들고 끝나면 지운다.

묶음: U 무변(선언 없는 프로젝트 — 고치기 전 판과 byte 동일) · E 선언 오류 × 입구(exit 1) · P 제품 자리(ST10 · ST4 · NM10~12) ·
S 셸(IM2 · IM26) · M 혼입(IM13 제품 분기) · R 해석(area · 예정 BC · `"*"` · 빚 스캔 from_files) · N 알림 · A 첫 등록 ·
I 승인 병합 유입 · X 치환 확인의 static 접두 횡단 이동 · H 호스트 1단계 이관 재현.
고치기 전 판 = BASELINE 커밋의 scripts(`git show <커밋>:<경로>` 로 임시 폴더에 푼다 — 작업 사본을 stash 하지 않는다).
BASELINE 은 판마다 그 판의 바탕 커밋으로 올린다(U 묶음은 «이 판이 선언 없는 프로젝트의 출력을 바꾸지 않았다» 의 대조다).
그 커밋이 이력에 없으면(얕은 clone 등) U 묶음을 건너뛰고 건너뛴 사실을 출력한다(실패로 세지 않는다)."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

TEST = Path(__file__).resolve().parent
SCRIPTS = TEST.parent
REPO = SCRIPTS.parents[1]
BASELINE = '1e4344a6'  # 고치기 전 판(배포된 dddjango-web 2.2.5) — 판마다 바탕 커밋으로 올린다
VERSION_NOTICE = re.compile(r'^\[info\] 플러그인 판 바뀜 — G0 스캔 (\S+) → 지금 (\S+?)'
                            r'\(검사 집합·키 의미론이 같아 잔존 판정을 잇는다\)\n', re.M)
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
REGISTRY = 'web/product_registry.json'
FLAT_SHELL = 'root/scaffold/view/root_view.html'
GUEST_SHELL = 'root/scaffold/view/root_guest_view.html'
TOKENS = ('color', 'typography', 'spacing', 'radius', 'shadow', 'duration', 'asset')
PASS = FAIL = 0


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok and detail:
        print('    ' + str(detail).replace('\n', '\n    ')[:2400])


def git(root, *args, check_rc=True):
    r = subprocess.run(['git', '-C', str(root), '-c', 'user.name=t', '-c', 'user.email=t@t', *args],
                       capture_output=True, text=True, env=ENV)
    if check_rc and r.returncode:
        raise RuntimeError('git %s — %s' % (' '.join(args[:2]), r.stderr))
    return r.stdout.strip()


def run_script(script, *args):
    r = subprocess.run([sys.executable, '-B', str(script), *map(str, args)], capture_output=True, text=True, env=ENV)
    return r.returncode, r.stdout + r.stderr


def backstop(root, *args, scripts=SCRIPTS):
    return run_script(scripts / 'backstop.py', root, *args)


def audit(root, *args, scripts=SCRIPTS):
    return run_script(scripts / 'refactor_audit.py', '--project', root, *args)


def found(out, cid, path, line=None):
    """`[ID] BLOCKER — web/<path>[:<행>]` 머리 줄이 있는가(행을 주면 그 행만)."""
    tail = (':%d' % line) if line is not None else r'(?::\d+)?'
    return re.search(r'^\[%s\] BLOCKER — web/%s%s$' % (cid, re.escape(path), tail), out, re.M) is not None


def blockers(out):
    return sorted(set(re.findall(r'^\[([A-Z]+\d+)\] BLOCKER — (\S+?)(?::\d+)?$', out, re.M)))


def message_of(out, cid, path):
    m = re.search(r'^\[%s\] BLOCKER — web/%s(?::\d+)?\n  위반: (.+)$' % (cid, re.escape(path)), out, re.M)
    return m.group(1) if m else ''


def fix_of(out, cid, path):
    m = re.search(r'^\[%s\] BLOCKER — web/%s(?::\d+)?\n  위반: .+\n  교정: (.+)$' % (cid, re.escape(path)), out, re.M)
    return m.group(1) if m else ''


def lines_of(out, cid, path):
    return sorted(int(n) for n in re.findall(r'^\[%s\] BLOCKER — web/%s:(\d+)$' % (cid, re.escape(path)), out, re.M))


class Proj:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def w(self, rel, *lines):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    def read(self, rel):
        return (self.root / rel).read_text(encoding='utf-8')

    def sub(self, rel, old, new):
        text = self.read(rel)
        if old not in text:
            raise RuntimeError('픽스처 오류 — %s 에 %r 없음' % (rel, old))
        (self.root / rel).write_text(text.replace(old, new), encoding='utf-8')

    def append(self, rel, *lines):
        with (self.root / rel).open('a', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')

    def rm(self, rel):
        (self.root / rel).unlink()

    def mv(self, old, new):
        (self.root / new).parent.mkdir(parents=True, exist_ok=True)
        git(self.root, 'mv', old, new)

    def commit(self, message='c'):
        git(self.root, 'add', '-A')
        git(self.root, 'commit', '-qm', message)
        return git(self.root, 'rev-parse', 'HEAD')

    def reset(self, sha):
        git(self.root, 'reset', '-q', '--hard', sha)
        git(self.root, 'clean', '-fdq')

    def declare(self, products, schema='dddjango-web-products/1'):
        self.w(REGISTRY, json.dumps({'schema': schema, 'products': products}, ensure_ascii=False, indent=2))

    def markers(self):
        web = self.root / 'web'
        for cur, _dirs, _files in os.walk(web):
            rel = os.path.relpath(cur, web).replace(os.sep, '/')
            if rel.split('/')[0] not in ('design_system', 'static'):
                (Path(cur) / '__init__.py').touch()
        for cur, dirs, files in os.walk(web):
            if not dirs and not files:
                (Path(cur) / '.gitkeep').touch()

    def scan(self, *extra, scripts=SCRIPTS):
        """--debt-scan --json → (exit, 출력, JSON 사전)."""
        target = self.root / '.git' / 'debt-fixture.json'
        if target.exists():
            target.unlink()
        e, out = backstop(self.root, '--debt-scan', *extra, '--json', target, scripts=scripts)
        return e, out, (json.loads(target.read_text(encoding='utf-8')) if target.exists() else {})

    def keys(self, *extra):
        return set(self.scan(*extra)[2].get('counts', {}))


PRODUCTS = {'operator': {'design_system': 'flat', 'bcs': ['order']},
            'guest': {'design_system': 'own', 'bcs': '*'}}


def shell_lines(theme):
    return ['{% load static %}', '<html><head>',
            "<link rel=\"stylesheet\" href=\"{% static '" + theme + "' %}\">",
            "<script src=\"{% static 'web/htmx/htmx.min.js' %}\" defer></script>",
            '</head><body>{% block content %}{% endblock %}</body></html>']


def mkstd(root, git_top=None):
    """2.0.0 표준 web/ 트리(빚 0 — fixtures_debt.sh mkproj 와 같은 꼴) · git 초기화만(커밋은 부르는 쪽).
    git_top 을 주면 저장소 뿌리는 거기다(프로젝트 루트가 저장소 하위 폴더인 꼴)."""
    p = Proj(root)
    w = p.w
    o = 'web/application/order/'
    w('config/settings.py', "SECRET_KEY = 'x'")
    w('manage.py', '# manage')
    w('requirements.txt', 'Django==5.1.2', 'pytest==8.3.3', 'pytest-django==4.9.0')
    w('web/__init__.py', '')
    w('web/apps.py', 'from django.apps import AppConfig', '', '', 'class WebConfig(AppConfig):', '    name: str = "web"')
    w('web/urls.py', 'from web.root.router.root_router import urlpatterns', '', '__all__: list[str] = ["urlpatterns"]')
    w('web/root/ruff.toml', '[lint]', 'select = ["ANN"]')
    w('web/root/router/root_router.py', 'from django.urls import include, path', '',
      'from web.application.order import order_router', '',
      'urlpatterns: list[object] = [path("orders/", include((order_router.urlpatterns, order_router.app_name)))]')
    w('web/' + FLAT_SHELL, *shell_lines('design_system/theme/app_theme.css'))
    w('web/root/scaffold/view_model/root_vm.py', 'from web.root.scaffold.state.root_state import RootState', '', '',
      'class RootVM:', '    def build(self) -> RootState:', '        return RootState(title="shop")')
    w('web/root/scaffold/state/root_state.py', 'from dataclasses import dataclass', '', '',
      '@dataclass(frozen=True, slots=True, kw_only=True)', 'class RootState:', '    title: str')
    w('web/root/handler/root_request_handler.py', 'class RootRequestHandler:', '    pass')
    w('web/root/initializer/root_initializer.py', 'class RootInitializer:', '    pass')
    for k in TOKENS:
        w('web/design_system/foundation/app_%s.css' % k,
          ':root { --duration-fast: 150ms; }' if k == 'duration' else ':root { --%s-base: 1px; }' % k)
    w('web/design_system/theme/app_theme.css', 'body { margin: 0; font: var(--typography-base); }')
    w('web/design_system/component/button/primary_button.html', '<a class="primary-button" href="{{ href }}">{{ label }}</a>')
    w('web/design_system/component/button/primary_button.css', '.primary-button { color: var(--color-base); }')
    (p.root / 'web/design_system/util').mkdir(parents=True)
    w('web/common/network/api_client.py', 'from django.test import Client', '', '',
      'class ApiClient:', '    def get(self, path: str) -> object:', '        return Client().get(path)')
    for k in ('enum', 'service', 'util'):
        (p.root / 'web/common' / k).mkdir(parents=True)
    mkbc(p, 'application/order', page=False)
    w(o + 'order_router.py', 'from django.urls import path', '',
      'from web.application.order.presentation_layer.view.order_list_view import order_list_view', '',
      'app_name: str = "order"', '', '', 'class OrderRoutes:', '    LIST: str = "order:list"', '', '',
      'urlpatterns: list[object] = [path("", order_list_view, name="list")]')
    w(o + 'order_navigator.py', 'from django.urls import reverse', '', '', 'class OrderNavigator:', '    @staticmethod',
      '    def list_href() -> str:', '        from web.application.order.order_router import OrderRoutes',
      '        return reverse(OrderRoutes.LIST)')
    w(o + 'application_layer/view_model/order_list_vm.py',
      'from web.application.order.application_layer.state.order_list_state import OrderListState', '', '',
      'class OrderListVM:', '    def build(self) -> OrderListState:', '        return OrderListState(count=0)')
    w(o + 'application_layer/state/order_list_state.py', 'from dataclasses import dataclass', '', '',
      '@dataclass(frozen=True, slots=True, kw_only=True)', 'class OrderListState:', '    count: int')
    w(o + 'presentation_layer/view/order_list_view.py', 'from django.http import HttpRequest, HttpResponse',
      'from django.shortcuts import render', '',
      'from web.application.order.application_layer.view_model.order_list_vm import OrderListVM', '', '',
      'def order_list_view(request: HttpRequest) -> HttpResponse:',
      '    return render(request, "application/order/presentation_layer/view/order_list_view.html", {"state": OrderListVM().build()})')
    w(o + 'presentation_layer/view/order_list_view.html', '{% extends "' + FLAT_SHELL + '" %}', '{% load static %}',
      '{% block content %}', '{% include "application/order/presentation_layer/section/order_list_summary_section.html" %}',
      '{% endblock %}')
    w(o + 'presentation_layer/section/order_list_summary_section.html', '<div class="order-list-summary">{{ state.count }}</div>')
    w('web/static/htmx/htmx.min.js', 'var htmx={version:"2.0.10"};')
    w('web/static/application/order/order_list_view.css', '.order-list { color: var(--color-base); }')
    (p.root / 'web/static/images').mkdir(parents=True)
    w('web_test/application/order/application_layer/order_list_vm_test.py', 'def test_order_list_vm() -> None:', '    assert True')
    w('.dddjango-web/backstop-baseline.json', '{"cycle_pairs": []}')
    p.markers()
    git(git_top or p.root, 'init', '-q', '-b', 'main')
    return p


def mkbc(p, rel, page=True, shell=FLAT_SHELL):
    """골격 완비 BC(ST4 통과형) — page 면 `<bc>_view.py`·`.html` 한 쌍(셸 = shell)."""
    base = 'web/' + rel + '/'
    bc = rel.rsplit('/', 1)[-1]
    cls = ''.join(part.capitalize() for part in bc.split('_'))
    for layer, kinds in (('application_layer', ('use_case', 'view_model', 'state', 'shared_state', 'service')),
                         ('infra_layer', ('data_source', 'repository', 'service')),
                         ('presentation_layer', ('view', 'section', 'widget', 'ui_extension')),
                         ('domain_layer/' + bc, ('entity', 'value_object', 'enum', 'domain_service', 'specification'))):
        for k in kinds:
            (p.root / base / layer / k).mkdir(parents=True, exist_ok=True)
    p.w(base + 'ruff.toml', '[lint]', 'select = ["ANN"]')
    p.w(base + 'domain_layer/%s/%s.py' % (bc, bc), 'from dataclasses import dataclass', '', '',
        '@dataclass(frozen=True, slots=True, kw_only=True)', 'class %s:' % cls, '    key: str')
    if page:
        template = rel + '/presentation_layer/view/%s_view.html' % bc
        p.w(base + 'presentation_layer/view/%s_view.py' % bc, 'from django.http import HttpRequest, HttpResponse',
            'from django.shortcuts import render', '', '',
            'def %s_view(request: HttpRequest) -> HttpResponse:' % bc,
            '    return render(request, "%s", {})' % template)
        p.w('web/' + template, '{% extends "' + shell + '" %}', '{% load static %}', '{% block content %}',
            '<p>%s</p>' % bc, '{% endblock %}')
    p.markers()


def own_root(p, pid, shell=True):
    """own 제품 뿌리 골격(네 폴더 + 빈 표준 7 파일 + theme) · 셸."""
    root = 'web/design_system/%s/' % pid
    for k in TOKENS:
        p.w(root + 'foundation/app_%s.css' % k, '')
    p.w(root + 'theme/app_theme.css', 'body { margin: 0; }')
    for k in ('component', 'util'):
        (p.root / root / k).mkdir(parents=True, exist_ok=True)
        (p.root / root / k / '.gitkeep').touch()
    if shell:
        p.w('web/root/scaffold/view/root_%s_view.html' % pid, *shell_lines('design_system/%s/theme/app_theme.css' % pid))


def mkdeclared(root, git_top=None):
    """두 제품 표준 트리(빚 0): 운영자(flat · order) + 손님(own · `*` — lobby) · 선언 포함 커밋 → (Proj, BASE)."""
    p = mkstd(root, git_top)
    mkbc(p, 'application/lobby', shell=GUEST_SHELL)
    own_root(p, 'guest')
    p.declare(PRODUCTS)
    return p, p.commit('base')


ORDER_PAGE = 'application/order/presentation_layer/view/order_list_view.html'
LOBBY_PAGE = 'application/lobby/presentation_layer/view/lobby_view.html'
LOBBY_CSS = 'static/application/lobby/lobby_view.css'


def link(target):
    return "<link rel=\"stylesheet\" href=\"{% static '" + target + "' %}\">"


def plugin_version(scripts):
    return json.loads((scripts.parent / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))['version']


def bumped_scripts(tmp, version):
    """지금 scripts(test/ 제외) 사본 + 판 글자만 올린 매니페스트 → 그 scripts 폴더(사본 매니페스트는 건드리지 않는다)."""
    target = Path(tmp) / 'dddjango-web'
    shutil.copytree(SCRIPTS, target / 'scripts', ignore=shutil.ignore_patterns('__pycache__', 'test'))
    manifest = json.loads((SCRIPTS.parent / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))
    manifest['version'] = version
    (target / '.claude-plugin').mkdir()
    (target / '.claude-plugin' / 'plugin.json').write_text(json.dumps(manifest, ensure_ascii=False), encoding='utf-8')
    return target / 'scripts'


def old_scripts(tmp):
    """BASELINE 커밋의 scripts(test/ 제외)와 매니페스트를 임시 폴더에 푼다 → 옛 scripts 폴더."""
    names = git(REPO, 'ls-tree', '-r', '--name-only', BASELINE, '--', 'dddjango-web/scripts',
                'dddjango-web/.claude-plugin').splitlines()
    for name in names:
        if '/scripts/test/' in name:
            continue
        data = subprocess.run(['git', '-C', str(REPO), 'show', '%s:%s' % (BASELINE, name)],
                              capture_output=True, env=ENV, check=True).stdout
        target = Path(tmp) / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return Path(tmp) / 'dddjango-web' / 'scripts'


def strip_stamp(data):
    """빚 스캔 JSON 에서 실행마다 다른 값(스캔 시각 · 플러그인 판 글자)만 뺀다."""
    out = dict(data)
    out.pop('scanned_at', None)
    out['scanner'] = {k: v for k, v in data.get('scanner', {}).items() if k != 'plugin'}
    return out


def scope_folder(p, name, a_keys='-', scripts=SCRIPTS):
    """`.dddjango-web/<name>/` 에 G0 동결(debt-g0.json)과 `## G0` 절."""
    folder = p.root / '.dddjango-web' / name
    folder.mkdir(parents=True, exist_ok=True)
    backstop(p.root, '--debt-scan', '--json', folder / 'debt-g0.json', scripts=scripts)
    (folder / 'refactor-scope.md').write_text(
        '## G0 %s\n- ⓐ 키: %s\n- 요구 키: -\n' % (datetime.now().strftime('%Y-%m-%d %H:%M'), a_keys), encoding='utf-8')
    return folder


# ====================================================================== U — 무변(선언 없는 프로젝트)

def bundle_unchanged(tmp):
    if subprocess.run(['git', '-C', str(REPO), 'cat-file', '-e', BASELINE + '^{commit}'], capture_output=True, env=ENV).returncode:
        print('SKIP U — 바탕 커밋 %s 이 이 저장소 이력에 없다(얕은 clone 등) — 무변 묶음(U)을 건너뛴다(실패로 세지 않는다)' % BASELINE)
        return
    old = old_scripts(tmp / 'old')
    check('U0 고치기 전 판(%s) scripts 를 풀 수 있다' % BASELINE, (old / 'backstop.py').is_file())
    p = mkstd(tmp / 'u')
    mkbc(p, 'application/lobby', shell=GUEST_SHELL)
    w = p.w
    # 평면 design_system 의 빚 · 선언 없는 중첩 폴더(지금처럼 무검사) · 선언 없는 둘째 셸(게이트 화면 취급)
    w('web/design_system/foundation/tokens.css', ':root { --chat-bg: #101010; }')
    w('web/design_system/foundation/motion.css', '@keyframes cm-rise { from { opacity: 0; } to { opacity: 1; } }')
    w('web/design_system/theme/dark_theme.css', 'body { margin: 0; }')
    w('web/design_system/component/loose.css', '.loose { width: 1px; }')
    w('web/design_system/component/etc/thing_etc.html', '<i></i>')
    w('web/design_system/guest/foundation/tokens.css', ':root { --Bad_Name: #fff; }')
    w('web/design_system/guest/component/card/guest_card.css', '.wrong { color: #fff; font-size: 12px; }')
    w('web/design_system/guest/extra/readme.css', 'body {}')
    w('web/' + GUEST_SHELL, *shell_lines('design_system/guest/theme/app_theme.css'))
    # 옛 배치 폴더 · 옛 정적 칸
    w('web/base/base.html', '{% load static %}', '<html><head>', link('web/css/base.css'),
      "<script defer src=\"{% static 'web/htmx/htmx.min.js' %}\"></script>", '</head><body>{% block content %}{% endblock %}</body></html>')
    w('web/auth/login/view/login.html', "{% extends 'base/base.html' %}", '{% block content %}<form></form>{% endblock %}')
    w('web/auth/login/view/login_view.py', 'from application.models import User', '', '',
      'def login_view(request: object) -> object:', '    return User')
    w('web/static/css/base.css', 'body { margin: 0; }')
    # BC 안 빚 — 층 의존 · 명명 · 셸
    w('web/application/order/domain_layer/order/entity/order_note.py', 'from django.db import models', '', '',
      'class OrderNote:', '    pass')
    w('web/application/order/presentation_layer/section/stray_section.html', '<div style="color: #ff0000">x</div>')
    p.append('web/' + LOBBY_PAGE, link('design_system/guest/component/card/guest_card.css'),
             link('design_system/theme/app_theme.css'))
    w('web/static/application/lobby/lobby_view.css', '@import url("../../../design_system/foundation/app_color.css");',
      '.lobby { width: 1px; }')
    p.markers()
    base = p.commit('base')
    g0 = scope_folder(p, 'run-old', 'C1', scripts=old)
    g0_json = (g0 / 'debt-g0.json').read_bytes()
    # 게이트가 볼 미커밋 변경 — 새 파일 · 기존 파일의 새 줄
    w('web/design_system/guest/theme/dark.css', 'body { color: #000; }')
    w('web/design_system/partner/foundation/app_color.css', ':root { --x: 1px; }')
    w('web/root/scaffold/view/root_partner_view.html', '{% extends "' + GUEST_SHELL + '" %}')
    w('web/application/order/presentation_layer/view/order_extra_view.html', '{% extends "' + GUEST_SHELL + '" %}',
      '{% load static %}', link('design_system/guest/theme/app_theme.css'))
    p.sub('web/' + LOBBY_PAGE, '<p>lobby</p>', '<p>lobby</p>\n' + link('design_system/component/button/primary_button.css'))
    p.sub('web/' + ORDER_PAGE, '{% block content %}', '{% block content %}\n' + link('web/root/root_guest_view.css'))
    p.append('web/auth/login/view/login.html', link('design_system/theme/app_theme.css'))

    def both(name, *args, nonempty=None):
        new = backstop(p.root, *args)
        before = backstop(p.root, *args, scripts=old)
        check('U %s — 고치기 전 판과 byte 동일' % name, new == before,
              '새 판 exit=%d\n%s\n옛 판 exit=%d\n%s' % (new[0], new[1][-900:], before[0], before[1][-900:]))
        if nonempty:
            check('U %s — 헛대조 아님(%s)' % (name, nonempty), nonempty in new[1], new[1][-600:])
        return new

    both('게이트(--diff-base)', '--diff-base', base, nonempty='IM26] BLOCKER')
    both('--slice-end', '--diff-base', base, '--slice-end', nonempty='슬라이스 끝')
    both('--only st(전역 퇴화)', '--only', 'st', nonempty='ST10] BLOCKER')
    both('--only im,nm(--diff-base)', '--diff-base', base, '--only', 'im,nm', nonempty='IM2] BLOCKER')
    both('--only cy', '--diff-base', base, '--only', 'cy', nonempty='blocker 0건')
    both('--all', '--all', nonempty='ST0] BLOCKER')
    for label, extra in (('--debt-scan', ()), ('--debt-scan --refactor', ('--refactor',))):
        e1, out1, data1 = p.scan(*extra)
        e0, out0, data0 = p.scan(*extra, scripts=old)
        check('U %s 출력 — 고치기 전 판과 byte 동일' % label, (e1, out1) == (e0, out0) and e1 == 2, out1[-600:] + '\n---\n' + out0[-600:])
        check('U %s JSON — scanner.plugin · scanned_at 빼고 같음' % label, strip_stamp(data1) == strip_stamp(data0) and bool(data1.get('counts')))
        check('U %s 지문 — scanner.checks · scanner.keys 같음' % label,
              data1.get('scanner', {}).get('checks') == data0.get('scanner', {}).get('checks') is not None
              and data1.get('scanner', {}).get('keys') == data0.get('scanner', {}).get('keys') is not None)
    # 옛 판 G0 동결본으로 새 판이 잔존을 실제로 판정한다(판 경계 없음). 매니페스트 판 글자가 다르면 새 판만
    # «플러그인 판 바뀜» 알림 한 줄을 낸다 — 그 한 줄만 빼고 byte 대조하고, 그 줄은 판이 다를 때만 · 그 꼴로 나오는지 따로 본다.
    before = backstop(p.root, '--debt-residual', g0, scripts=old)
    g2_old = json.loads((g0 / 'debt-g2.json').read_text(encoding='utf-8'))
    old_version = plugin_version(old)
    check('U --debt-residual 옛 판 — 판 알림 없음(자기 동결본)', not VERSION_NOTICE.search(before[1]), before[1])
    for label, scripts in (('지금 매니페스트', SCRIPTS), ('판 올림 변형 99.0.0', bumped_scripts(tmp / 'bumped', '99.0.0'))):
        (g0 / 'debt-g0.json').write_bytes(g0_json)
        new = backstop(p.root, '--debt-residual', g0, scripts=scripts)
        g2_new = json.loads((g0 / 'debt-g2.json').read_text(encoding='utf-8'))
        version = plugin_version(scripts)
        notices = VERSION_NOTICE.findall(new[1])
        check('U --debt-residual(%s) — 판 알림 한 줄을 뺀 나머지가 고치기 전 판과 byte 동일' % label,
              (new[0], VERSION_NOTICE.sub('', new[1])) == before, '%r\n%r' % (new, before))
        check('U --debt-residual(%s) — 판 알림은 판이 다를 때만 · 그 꼴로(%s → %s)' % (label, old_version, version),
              notices == ([(old_version, version)] if version != old_version else [])
              and (version == old_version or new[1].startswith('[info] 플러그인 판 바뀜 — ')), new[1][:300])
        check('U --debt-residual(%s) — 옛 동결본으로 잔존 판정 수행(판 경계 0)' % label, '판 경계' not in new[1]
              and '빚 잔존 — ⓐ 잔존 1' in new[1] and new[0] == 2, new[1])
        check('U --debt-residual(%s) 의 debt-g2.json — 같음' % label, strip_stamp(g2_new) == strip_stamp(g2_old))
    # 리팩토링 판정 도구 — plan 요약과 plan.md
    plans = []
    for scripts in (SCRIPTS, old):
        out_dir = g0 / 'audit'
        shutil.rmtree(out_dir, ignore_errors=True)
        got = audit(p.root, 'plan', 'web/design_system', '--debt', g0 / 'debt-g0.json', '--out', out_dir, scripts=scripts)
        plans.append((got, (out_dir / 'plan.md').read_text(encoding='utf-8') if (out_dir / 'plan.md').exists() else None))
    check('U refactor_audit plan — 요약 · plan.md 가 고치기 전 판과 byte 동일', plans[0] == plans[1] and plans[0][0][0] == 0
          and plans[0][1] is not None, '%r\n%r' % (plans[0][0], plans[1][0]))
    # 검사 집합 상수 — 새 검사 ID 0
    probe = ('import json,sys; sys.path.insert(0, sys.argv[1]); import backstop; from src import common, debt; '
             'print(json.dumps([list(common.CORE_CHECK_IDS), list(common.CORE_FAMILIES), list(debt.CHECK_IDS), debt.KEY_SCHEME, '
             'list(debt.DEBT_FAMILIES), backstop.CHECK_IDS, backstop.TOTAL_CHECKS, backstop.SLICE_END_DEFERRED, '
             '{k: v for k, v in debt.scanner_stamp().items() if k != "plugin"}]))')
    consts = [subprocess.run([sys.executable, '-B', '-c', probe, str(s)], capture_output=True, text=True, env=ENV).stdout
              for s in (SCRIPTS, old)]
    check('U 검사 집합 상수(CORE_CHECK_IDS · CHECK_IDS · KEY_SCHEME · DEBT_FAMILIES · 86 · SLICE_END_DEFERRED · 지문) 무변',
          consts[0] == consts[1] and '"IM27"' in consts[0] and json.loads(consts[0])[6] == 86, consts[0][:300] + '\n' + consts[1][:300])
    # 치환 확인 — static 접두를 건너지 않는 이동(같은 쪽)은 고치기 전 판과 byte 동일
    q = mkstd(tmp / 'u2')
    q.w('web/static/css/a.css', 'body { margin: 0; }', 'a { width: 1px; }')
    q.w('web/design_system/util/x.css', '.x { width: 1px; }', '.x2 { width: 2px; }')
    q.w('web/legacy/page.html', '<html>', '<body>legacy</body>', '</html>')
    q.w('tests/test_same_side.py', 'CSS: str = "web/static/css/a.css"', 'URL: str = "/static/web/css/a.css"',
        'UTIL: str = "design_system/util/x.css"', 'PAGE: str = "legacy/page.html"')
    q.w('tests/notes.txt', 'web/css/a.css', 'web/design_system/util/x.css')
    start = q.commit('base')
    q.mv('web/static/css/a.css', 'web/static/root/root_view.css')
    q.mv('web/design_system/util/x.css', 'web/design_system/util/y.css')
    q.mv('web/legacy/page.html', 'web/older/page.html')
    q.w('tests/test_same_side.py', 'CSS: str = "web/static/root/root_view.css"', 'URL: str = "/static/web/root/root_view.css"',
        'UTIL: str = "design_system/util/y.css"', 'PAGE: str = "older/page.html"')
    q.w('tests/notes.txt', 'web/root/root_view.css', 'web/design_system/util/y.css')
    end = q.commit('same-side move')
    new = backstop(q.root, '--subst-check', start, end)
    check('U --subst-check 같은 쪽 이동(static → static · design_system → design_system · 옛 배치 폴더) — 고치기 전 판과 byte 동일',
          new == backstop(q.root, '--subst-check', start, end, scripts=old) and new[0] == 0 and 'web/ 밖 변경 파일 2' in new[1], new[1][-600:])


# ====================================================================== E — 선언 오류 × 입구

def bundle_errors(tmp):
    p, base = mkdeclared(tmp / 'e')
    folder = scope_folder(p, 'run')
    good = p.read(REGISTRY)
    debt = folder / 'debt-g0.json'
    unit = 'web/application/order'
    audit(p.root, 'plan', unit, '--debt', debt, '--out', folder / 'audit-kept')          # --against 가 대조할 기록 plan
    (folder / 'design-spec.md').write_text(
        '## 슬라이스 0\n- 경로: application/order/order_router.py → application/order/order_routes.py\n', encoding='utf-8')

    baseline = p.root / '.dddjango-web' / 'backstop-baseline.json'
    baseline_bytes = baseline.read_bytes()
    (folder / 'build-state.json').write_text(json.dumps({'git_snapshot': base, 'slices': []}), encoding='utf-8')

    def update_baseline():
        """--update-baseline 실행 → (exit, 출력 + 기준선 파일을 썼는가 표지) — 끝나면 기준선을 되돌린다."""
        e, out = backstop(p.root, '--diff-base', base, '--update-baseline')
        wrote = baseline.read_bytes() != baseline_bytes
        baseline.write_bytes(baseline_bytes)
        return e, out + ('\nBLOCKER(픽스처) — 선언 오류인데 기준선 파일을 썼다' if wrote and e == 1 else '')

    def entries():
        audit_out = folder / 'audit'
        shutil.rmtree(audit_out, ignore_errors=True)
        return [('게이트', backstop(p.root, '--diff-base', base)),
                ('--slice-end', backstop(p.root, '--diff-base', base, '--slice-end')),
                ('--only cy', backstop(p.root, '--only', 'cy')),
                ('--all', backstop(p.root, '--all')),
                ('--update-baseline', update_baseline()),
                ('--design-build', backstop(p.root, '--diff-base', base, '--design-build', folder)),
                ('--debt-scan', backstop(p.root, '--debt-scan')),
                ('--debt-scan --refactor', backstop(p.root, '--debt-scan', '--refactor')),
                ('--debt-residual', backstop(p.root, '--debt-residual', folder)),
                ('refactor_audit plan', audit(p.root, 'plan', unit, '--debt', debt, '--out', audit_out)),
                ('refactor_audit plan --names', audit(p.root, 'plan', unit, '--debt', debt, '--out', audit_out,
                                                      '--names', folder / 'design-spec.md')),
                ('refactor_audit plan --against', audit(p.root, 'plan', unit, '--debt', debt,
                                                        '--against', folder / 'audit-kept' / 'plan.md'))]

    for name, (e, out) in entries():
        check('E 올바른 선언 · %s — exit 0(헛대조 아님)' % name, e == 0 and '판정 불가' not in out, 'exit=%d\n%s' % (e, out[-500:]))
    # 선언 파일은 리팩토링 판정 도구의 어느 단위도 아니다(컨테이너 `web/*.py` 범위에도 들지 않는다)
    out_dir = folder / 'audit-container'
    e, out = audit(p.root, 'plan', 'web/*.py', '--debt', debt, '--out', out_dir)
    plan = (out_dir / 'plan.md').read_text(encoding='utf-8') if (out_dir / 'plan.md').exists() else ''
    scope = plan.partition('## 범위 파일')[2].partition('\n## ')[0]
    check('E 선언 파일은 «어느 단위도 아님» — `web/*.py` 범위 파일에 없다', e == 0 and '`web/urls.py`' in scope
          and 'product_registry.json' not in scope, 'exit=%d\n%s\n%s' % (e, out[-300:], scope[:600]))
    e, out = audit(p.root, 'plan', 'web/product_registry.json', '--debt', debt, '--out', folder / 'audit-x')
    check('E 선언 파일을 단위로 주면 실행 불능(exit 1 · 단위가 아니다)', e == 1 and '단위가 아니다' in out and '제품 선언' in out, out[-300:])

    def decl(products, **top):
        body = {'schema': 'dddjango-web-products/1', 'products': products}
        body.update(top)
        return json.dumps(body, ensure_ascii=False)

    flat = {'design_system': 'flat', 'bcs': ['order']}
    own = {'design_system': 'own', 'bcs': '*'}
    cases = [
        ('JSON 파손', '{'),
        ('빈 파일', ''),
        ('UTF-8 아님', b'\xff\xfe{}'),
        ('중복 키(최상위)', '{"schema": "dddjango-web-products/1", "products": {}, "products": %s}' % json.dumps(PRODUCTS)),
        ('중복 키(제품 id)', '{"schema": "dddjango-web-products/1", "products": {"operator": %s, "guest": %s, "guest": %s}}'
         % (json.dumps(flat), json.dumps(own), json.dumps(own))),
        ('schema 다름', json.dumps({'schema': 'dddjango-web-products/2', 'products': PRODUCTS})),
        ('schema 없음', json.dumps({'products': PRODUCTS})),
        ('products 없음', json.dumps({'schema': 'dddjango-web-products/1'})),
        ('최상위 타입(배열)', json.dumps([PRODUCTS])),
        ('products 타입(배열)', decl([flat, own])),
        ('제품 값 타입(문자열)', decl({'operator': 'flat', 'guest': own})),
        ('bcs 타입(숫자)', decl({'operator': flat, 'guest': {'design_system': 'own', 'bcs': 3}})),
        ('bcs 타입(문자열 — "*" 아님)', decl({'operator': flat, 'guest': {'design_system': 'own', 'bcs': 'lobby'}})),
        ('bcs 항목 타입(숫자)', decl({'operator': flat, 'guest': {'design_system': 'own', 'bcs': ['lobby', 3]}})),
        ('모르는 키(최상위)', decl(PRODUCTS, note='x')),
        ('모르는 키(제품)', decl({'operator': dict(flat, shell='x.html'), 'guest': own})),
        ('design_system 없음', decl({'operator': flat, 'guest': {'bcs': '*'}})),
        ('bcs 없음', decl({'operator': flat, 'guest': {'design_system': 'own'}})),
        ('design_system 값(preserved)', decl({'operator': flat, 'guest': {'design_system': 'preserved', 'bcs': '*'}})),
        ('flat 0', decl({'operator': {'design_system': 'own', 'bcs': ['order']}, 'guest': own})),
        ('flat 2', decl({'operator': flat, 'guest': {'design_system': 'flat', 'bcs': '*'}})),
        ('제품 0', decl({})),
        ('id 꼴(대문자)', decl({'operator': flat, 'Guest': own})),
        ('id 꼴(하이픈)', decl({'operator': flat, 'guest-app': own})),
        ('id 가 종류 폴더 이름(theme)', decl({'operator': flat, 'theme': own})),
        ('"*" 둘', decl({'operator': {'design_system': 'flat', 'bcs': '*'}, 'guest': own})),
        ('같은 BC 가 두 제품', decl({'operator': flat, 'guest': {'design_system': 'own', 'bcs': ['lobby', 'order']}})),
        ('한 제품 안 중복 BC', decl({'operator': {'design_system': 'flat', 'bcs': ['order', 'order']}, 'guest': own})),
        ('BC 경로 꼴(절대 경로)', decl({'operator': {'design_system': 'flat', 'bcs': ['/order']}, 'guest': own})),
        ('BC 경로 꼴(..)', decl({'operator': {'design_system': 'flat', 'bcs': ['../order']}, 'guest': own})),
        ('BC 경로 꼴(빈 성분)', decl({'operator': {'design_system': 'flat', 'bcs': ['admin//order']}, 'guest': own})),
        ('BC 경로 꼴(끝 빗금)', decl({'operator': {'design_system': 'flat', 'bcs': ['order/']}, 'guest': own})),
        ('BC 경로 꼴(빈 문자열)', decl({'operator': {'design_system': 'flat', 'bcs': ['']}, 'guest': own})),
        ('BC 경로 꼴(세 성분)', decl({'operator': {'design_system': 'flat', 'bcs': ['a/b/c']}, 'guest': own})),
    ]
    # BC 이름 꼴 — 성분마다 소문자 snake_case 식별자 · 층 폴더 이름 금지 · "*" 는 배열 밖 문자열로만
    for bad in ('*', 'Lobby', 'lobby view', ' lobby', 'lobby ', 'lobby.x', 'lobby\\x', 'lobby-x', '1lobby', 'admin/Lobby',
                'presentation_layer', 'lobby/presentation_layer', 'application_layer/lobby', 'domain_layer', 'infra_layer'):
        cases.append(('BC 이름 꼴(%r)' % bad, decl({'operator': flat, 'guest': {'design_system': 'own', 'bcs': [bad]}})))
    cases.append(('BOM', b'\xef\xbb\xbf' + good.encode('utf-8')))
    registry = p.root / REGISTRY
    for label, body in cases:
        registry.write_bytes(body if isinstance(body, bytes) else body.encode('utf-8'))
        for name, (e, out) in entries():
            say = '실행 불능' if name.startswith('refactor_audit') else '[backstop] 판정 불가 — '
            check('E %s · %s — exit 1' % (label, name), e == 1 and say in out and 'product_registry.json' in out
                  and 'Traceback' not in out and 'BLOCKER' not in out, 'exit=%d\n%s' % (e, out[-500:]))
    registry.unlink()
    registry.mkdir()
    for name, (e, out) in entries():
        check('E 선언 자리가 폴더 · %s — exit 1' % name, e == 1 and 'product_registry.json' in out and 'Traceback' not in out,
              'exit=%d\n%s' % (e, out[-500:]))
    registry.rmdir()
    # 선언 자리가 링크(올바른 내용을 가리켜도) · 끊긴 링크 — 일반 파일만 선언이다
    p.w('web/registry_target.json', good.rstrip('\n'))
    for label, target in (('링크', 'registry_target.json'), ('끊긴 링크', 'no_such_file.json')):
        os.symlink(target, registry)
        for name, (e, out) in entries():
            check('E 선언 자리가 %s · %s — exit 1' % (label, name), e == 1 and 'product_registry.json' in out
                  and 'Traceback' not in out and 'BLOCKER' not in out, 'exit=%d\n%s' % (e, out[-500:]))
        registry.unlink()
    p.rm('web/registry_target.json')
    if os.geteuid() == 0:
        print('SKIP E 읽기 불능 · web/ 조사 불능 — root 권한이라 chmod 000 이 접근을 막지 못한다(건너뜀)')
    else:
        # 선언 파일 읽기 불능
        registry.write_text(good, encoding='utf-8')
        registry.chmod(0)
        try:
            for name, (e, out) in entries():
                check('E 선언 읽기 불능(chmod 000) · %s — exit 1' % name, e == 1 and 'product_registry.json' in out
                      and 'Traceback' not in out and 'BLOCKER' not in out, 'exit=%d\n%s' % (e, out[-500:]))
        finally:
            registry.chmod(0o644)
        # web/ 탐색 권한 없음 — 선언이 있는지조차 조사할 수 없다. «선언 없음 · 빈 목록 · exit 0» 으로 내려앉지 않는다.
        web = p.root / 'web'
        web.chmod(0)
        try:
            for name, args in (('--all --only im13', ('--all', '--only', 'im13')), ('--only cy', ('--only', 'cy')),
                               ('--debt-scan', ('--debt-scan',)), ('--debt-residual', ('--debt-residual', folder))):
                e, out = backstop(p.root, *args)
                check('E web/ 조사 불능(chmod 000) · %s — exit 1 «판정 불가»(무선언 폴백 아님)' % name,
                      e == 1 and '[backstop] 판정 불가 — ' in out and 'product_registry.json' in out and 'blocker 0건' not in out
                      and 'Traceback' not in out, 'exit=%d\n%s' % (e, out[-500:]))
            e, out = backstop(p.root, '--diff-base', base)
            check('E web/ 조사 불능 · 게이트(--diff-base) — exit 1', e == 1 and 'blocker 0건' not in out, 'exit=%d\n%s' % (e, out[-500:]))
            e, out = audit(p.root, 'plan', unit, '--debt', debt, '--out', folder / 'audit-denied')
            check('E web/ 조사 불능 · refactor_audit plan — exit 1', e == 1 and '실행 불능' in out, 'exit=%d\n%s' % (e, out[-500:]))
        finally:
            web.chmod(0o755)
    # web/ 가 없는 첫 실행은 선언 없음 그대로(빚 0 · 판정 불가 아님)
    first = tmp / 'first-run'
    first.mkdir()
    git(first, 'init', '-q', '-b', 'main')
    e, out = backstop(first, '--debt-scan')
    check('E web/ 없는 첫 실행 — 선언 없음 그대로(빚 스캔 exit 0)', e == 0 and '판정 불가' not in out and '첫 실행' in out, out[-400:])
    # 치환 확인은 선언을 읽지 않는다 — 깨진 선언이어도 그대로 돈다
    registry.write_text('{', encoding='utf-8')
    e, out = backstop(p.root, '--subst-check', base, base)
    check('E 깨진 선언 · --subst-check — 선언을 읽지 않는다(exit 0)', e == 0 and '판정 불가' not in out, 'exit=%d\n%s' % (e, out[-400:]))
    registry.write_text(good, encoding='utf-8')
    e, out = backstop(p.root, '--diff-base', base)
    check('E 선언을 되돌리면 게이트 exit 0', e == 0 and 'blocker 0건' in out, out[-400:])

    # ---- 프로젝트 루트가 저장소 하위 폴더 — 그 루트의 web/ 선언을 읽는다(저장소 뿌리의 것이 아니다)
    top = tmp / 'sub'
    q, sub_base = mkdeclared(top / 'server', git_top=top)
    sub_folder = scope_folder(q, 'run')

    def sub_entries():
        shutil.rmtree(sub_folder / 'audit', ignore_errors=True)
        # 게이트는 st·im·nm 만 — 하위 폴더 루트에서는 2.2.5 부터 기준점 트리가 비어 읽혀 새 BC 판별(TG1)이 과하게 선다(이 판 범위 밖)
        return [('게이트(--only st,im,nm)', backstop(q.root, '--diff-base', sub_base, '--only', 'st,im,nm')),
                ('--all', backstop(q.root, '--all')),
                ('--debt-scan', backstop(q.root, '--debt-scan')),
                ('refactor_audit plan', audit(q.root, 'plan', unit, '--debt', sub_folder / 'debt-g0.json',
                                              '--out', sub_folder / 'audit'))]

    (top / 'web').mkdir()
    (top / 'web' / 'product_registry.json').write_text('{', encoding='utf-8')     # 저장소 뿌리의 미끼(깨진 선언) — 읽지 않는다
    for name, (e, out) in sub_entries():
        check('E 하위 폴더 루트 · 올바른 선언 · %s — exit 0(저장소 뿌리의 깨진 미끼를 읽지 않는다)' % name,
              e == 0 and '판정 불가' not in out, 'exit=%d\n%s' % (e, out[-500:]))
    (q.root / REGISTRY).write_text('{', encoding='utf-8')
    for name, (e, out) in sub_entries():
        check('E 하위 폴더 루트 · 깨진 선언 · %s — exit 1' % name, e == 1 and 'product_registry.json' in out
              and 'BLOCKER' not in out, 'exit=%d\n%s' % (e, out[-500:]))


# ====================================================================== P — 제품 자리(ST10 · ST4 · NM10~12)

def bundle_places(tmp):
    p, base = mkdeclared(tmp / 'p')
    w = p.w
    g = 'design_system/guest/'
    e, out = backstop(p.root, '--diff-base', base)
    check('P0 두 제품 표준 트리 — 게이트 blocker 0', e == 0 and 'blocker 0건' in out, out[-600:])
    e, out, data = p.scan()
    check('P0 두 제품 표준 트리 — 빚 0', e == 0 and data.get('counts') == {}, out[-800:])

    w('web/' + g + 'foundation/tokens.css', ':root { --chat-bg: 1px; }')                        # ST10 7 파일 밖
    w('web/' + g + 'foundation/app_color.css', ':root { --spacing-x: 1px; --Color_Bad: 1px; }')  # NM11 ×2
    w('web/' + g + 'theme/dark_theme.css', 'body { margin: 0; }')                                # ST10 theme 직속
    w('web/' + g + 'component/loose.css', '.loose { width: 1px; }')                              # ST10 component 직속
    w('web/' + g + 'component/etc/thing_etc.html', '<i></i>')                                    # ST10 정크드로어 군
    w('web/' + g + 'util/helper.py', 'x: int = 1')                                               # ST10 Python
    w('web/' + g + 'component/card/guest_card.css', '.guest-card { color: #fff; font-size: 12px; }', '.wrong { width: 1px; }')
    w('web/' + g + 'component/card/ds_card.html', '<div></div>')                                 # NM12 ds_ 접두
    w('web/' + g + 'component/card/panel.html', '<div style="color: #ff0000">x</div>')           # NM12 파일명 · NM10
    w('web/' + g + 'util/motion.css', '.cm-rise { color: #fff; font-size: 12px; }')              # util — 리터럴 검사 없음(범위 무변)
    p.append('web/' + g + 'theme/app_theme.css', 'h1 { color: #101010; font-size: 20px; }')       # theme — 리터럴 검사 없음
    e, out = backstop(p.root, '--diff-base', base)
    check('P1 own 뿌리 foundation 표준 7 파일 밖 — ST10', found(out, 'ST10', g + 'foundation/tokens.css'), out[-900:])
    check('P1 기존 파일 수정은 명명 게이트(added) 밖 그대로 — NM11 0', not found(out, 'NM11', g + 'foundation/app_color.css'))
    e_all, out_all = backstop(p.root, '--all', '--only', 'nm11')
    check('P1 own 뿌리 foundation 토큰 접두 · 표기 — NM11 2건(--all)',
          found(out_all, 'NM11', g + 'foundation/app_color.css', 1)
          and out_all.count('[NM11] BLOCKER — web/' + g + 'foundation/app_color.css') == 2
          and out_all.count('[NM11] BLOCKER') == 2, out_all[-900:])
    check('P1 own 뿌리 theme 직속 — ST10', found(out, 'ST10', g + 'theme/dark_theme.css'))
    check('P1 own 뿌리 component 직속 파일 — ST10', found(out, 'ST10', g + 'component/loose.css'))
    check('P1 own 뿌리 component 정크드로어 군 — ST10', found(out, 'ST10', g + 'component/etc'))
    check('P1 own 뿌리 안 Python — ST10', found(out, 'ST10', g + 'util/helper.py'))
    check('P1 own 뿌리 component 시각 리터럴 — NM10(CSS 2 · HTML 1)',
          out.count('[NM10] BLOCKER — web/' + g + 'component/card/guest_card.css') == 2 and found(out, 'NM10', g + 'component/card/panel.html'), out[-900:])
    check('P1 own 뿌리 component 클래스 접두 — NM12', found(out, 'NM12', g + 'component/card/guest_card.css', 2))
    check('P1 own 뿌리 component `ds_` 접두 · 군 접미 — NM12',
          found(out, 'NM12', g + 'component/card/ds_card.html') and found(out, 'NM12', g + 'component/card/panel.html'))
    check('P1 theme · util 은 리터럴 검사 범위 밖 그대로(NM10 0)',
          not found(out, 'NM10', g + 'util/motion.css') and not found(out, 'NM10', g + 'theme/app_theme.css'))
    check('P1 Finding 경로는 실제 물리 경로(제품 뿌리를 떼지 않는다)',
          'BLOCKER — web/foundation/' not in out and 'BLOCKER — web/design_system/foundation/tokens.css' not in out)
    p.reset(base)

    w('web/' + g + 'tokens/legacy.css', 'body {}')
    w('web/design_system/partner/foundation/app_color.css', ':root { --color-x: 1px; }')
    w('web/design_system/themes/app_theme.css', 'body {}')
    e, out = backstop(p.root, '--diff-base', base)
    check('P2 own 뿌리 안 허용 밖 폴더 — ST10(폴더)', found(out, 'ST10', g + 'tokens') and '`guest`' in message_of(out, 'ST10', g + 'tokens'), out[-900:])
    check('P2 평면 뿌리의 선언 밖 폴더 — ST10(폴더) · 선언된 뿌리 이름을 적는다',
          found(out, 'ST10', 'design_system/partner') and 'guest' in message_of(out, 'ST10', 'design_system/partner'), out[-900:])
    check('P2 평면 뿌리 종류 폴더 오타 — ST10 + 오타 의심', '`theme/` 오타 의심' in message_of(out, 'ST10', 'design_system/themes'), out[-900:])
    check('P2 선언된 뿌리 · 종류 폴더는 허용 밖이 아니다',
          not found(out, 'ST10', 'design_system/guest') and not found(out, 'ST10', g + 'foundation') and not found(out, 'ST10', 'design_system/util'))
    keys = p.keys()
    check('P2 빚 스캔 — 허용 밖 폴더 발견은 그 아래 파일 키로 펼친다',
          {'ST10|' + g + 'tokens/legacy.css', 'ST10|design_system/partner/foundation/app_color.css',
           'ST10|design_system/themes/app_theme.css'} <= keys and 'ST10|design_system/partner' not in keys, sorted(keys))
    p.reset(base)

    # ---- ST4: 선언된 own 제품의 뿌리 골격 · 셸 — 신설 여부와 무관
    p.declare(dict(PRODUCTS, partner={'design_system': 'own', 'bcs': []}))
    e, out = backstop(p.root, '--diff-base', base)
    shell = 'root/scaffold/view/root_partner_view.html'
    check('P3 선언된 뿌리 · 셸 통째 부재 — ST4 2건 · exit 2',
          e == 2 and found(out, 'ST4', 'design_system/partner') and found(out, 'ST4', shell), out[-900:])
    e, out = backstop(p.root, '--diff-base', base, '--slice-end')
    check('P3 슬라이스 끝에서는 지금처럼 미룬다(ST4 0 · exit 0)', e == 0 and 'ST4] BLOCKER' not in out, out[-600:])
    e, out = backstop(p.root, '--only', 'st4')
    check('P3 기준점 없이도 선언된 뿌리 · 셸 ST4', found(out, 'ST4', 'design_system/partner') and found(out, 'ST4', shell), out[-600:])
    e, out, data = p.scan()
    keys = set(data.get('counts', {}))
    check('P3 빚 스캔에도 선언된 뿌리 · 셸 ST4 키', {'ST4|design_system/partner', 'ST4|' + shell} <= keys, sorted(keys))
    rows = [r for r in data.get('findings', []) if r['check'] == 'ST4']
    check('P3 그 ST4 두 키는 «미룰 수 없음»(JSON undeferrable · 출력 표지)',
          len(rows) == 2 and all(r.get('undeferrable') is True for r in rows) and out.count('[ST4] (미룰 수 없음) web/') == 2, out[-900:])
    notice = [ln for ln in out.splitlines() if ln.startswith('[info] ST4(')]
    check('P3 ST4 알림이 그 키와 모순되지 않는다(«신설 단위 골격» 으로 좁힘 · 선언된 own 뿌리 · 셸은 따로 센다고 적는다)',
          len(notice) == 1 and notice[0].startswith('[info] ST4(신설 단위 골격) 빚 모드 제외') and '미룰 수 없음' in notice[0]
          and '골격 완비' not in notice[0], notice)
    e, out = backstop(p.root, '--only', 'st4')
    notice = [ln for ln in out.splitlines() if ln.startswith('[info] ST4(')]
    check('P3 기준점 없는 게이트의 ST4 생략 알림도 선언된 own 뿌리 · 셸은 본다고 적는다',
          len(notice) == 1 and notice[0].startswith('[info] ST4(골격 완비) 생략 — git 기준점 없음') and '기준점 없이도 본다' in notice[0], notice)
    check('P3 ST4 교정문 — 이 실행이 들인 선언이 아니면 들인 쪽에서 골격 · 셸을 함께',
          all('선언을 들인 쪽에서 골격 · 셸을 함께 넣은 뒤 다시 받는다' in fix_of(out, 'ST4', x) for x in ('design_system/partner', shell)), out[-900:])
    own_root(p, 'partner')
    p.rm('web/design_system/partner/foundation/app_asset.css')
    p.rm('web/design_system/partner/util/.gitkeep')
    (p.root / 'web/design_system/partner/util').rmdir()
    e, out = backstop(p.root, '--diff-base', base)
    msg = message_of(out, 'ST4', 'design_system/partner')
    check('P3 부분 골격 — 누락 목록(util/ · foundation/app_asset.css) · 셸은 통과',
          'util/' in msg and 'foundation/app_asset.css' in msg and 'app_color.css' not in msg and not found(out, 'ST4', shell), out[-900:])
    own_root(p, 'partner')
    e, out = backstop(p.root, '--diff-base', base)
    check('P3 골격 · 셸을 채우면 ST4 0 · exit 0', e == 0 and 'BLOCKER' not in out, out[-600:])
    p.reset(base)

    # ---- 둘째 셸만 더함 — VM · state 짝을 요구하지 않는다
    q = mkstd(tmp / 'p2')
    base2 = q.commit('base')
    own_root(q, 'guest')
    q.declare(PRODUCTS)
    q.w('web/static/root/root_guest_view.css', '.guest-frame { width: 480px; }')
    e, out = backstop(q.root, '--diff-base', base2)
    check('P4 선언 + 손님 골격 + 둘째 셸 · 틀 CSS 만 더함(VM · state 추가 0) — blocker 0', e == 0 and 'blocker 0건' in out, out[-900:])


# ====================================================================== S — 셸(IM2 · IM26)

def bundle_shells(tmp):
    p, base = mkdeclared(tmp / 's')
    page = 'web/' + LOBBY_PAGE
    p.sub(page, GUEST_SHELL, FLAT_SHELL)
    e, out = backstop(p.root, '--diff-base', base)
    msg = message_of(out, 'IM26', LOBBY_PAGE)
    check('S1 손님 BC 페이지가 root_view.html 을 extends(새 줄) — IM26 · exit 2', e == 2 and found(out, 'IM26', LOBBY_PAGE, 1), out[-900:])
    check('S1 사유에 제품과 그 제품 셸 · 규약 표지(제품 셸)', 'guest' in msg and GUEST_SHELL in msg
          and msg.endswith('(discipline-houserules §1·§3·§5 제품 셸)'), msg)
    check('S1 선언된 셸의 extends 는 root 참조 예외(IM2 0)', 'IM2] BLOCKER' not in out, out[-600:])
    p.sub(page, FLAT_SHELL, GUEST_SHELL)
    e, out = backstop(p.root, '--diff-base', base)
    check('S1 손님 셸로 바꾸면 0', e == 0 and 'BLOCKER' not in out, out[-600:])
    p.sub('web/' + ORDER_PAGE, FLAT_SHELL, GUEST_SHELL)
    e, out = backstop(p.root, '--diff-base', base)
    check('S2 운영자 BC 페이지가 손님 셸을 extends — IM26', found(out, 'IM26', ORDER_PAGE, 1) and 'operator' in message_of(out, 'IM26', ORDER_PAGE), out[-900:])
    p.reset(base)
    new_page = 'application/lobby/presentation_layer/view/lobby_event_view.html'
    p.w('web/' + new_page, '{% extends "' + FLAT_SHELL + '" %}')
    p.w('web/' + new_page[:-5] + '.py', 'def lobby_event_view(request: object) -> object:', '    return request')
    e, out = backstop(p.root, '--diff-base', base)
    check('S3 새 손님 페이지가 운영자 셸 — IM26', found(out, 'IM26', new_page, 1), out[-900:])
    p.reset(base)
    # 선언 안 된 root_<x>_view.html 은 지금처럼 게이트 화면 — 셸로 쓰면 IM2 + IM26
    p.w('web/root/scaffold/view/root_partner_view.html', '{% extends "' + GUEST_SHELL + '" %}')
    p.sub(page, GUEST_SHELL, 'root/scaffold/view/root_partner_view.html')
    e, out = backstop(p.root, '--diff-base', base)
    check('S4 선언 안 된 root_<x>_view.html 을 extends — IM2 + IM26', found(out, 'IM2', LOBBY_PAGE, 1) and found(out, 'IM26', LOBBY_PAGE, 1), out[-900:])
    check('S4 게이트 화면(선언 밖 root_<x>_view)은 선언된 셸 어느 것이든 extends 가능', not found(out, 'IM26', 'root/scaffold/view/root_partner_view.html'))
    p.reset(base)
    p.sub('web/' + GUEST_SHELL, '{% load static %}', '{% extends "' + FLAT_SHELL + '" %}\n{% load static %}')
    e, out = backstop(p.root, '--diff-base', base)
    check('S5 제품 셸은 독립 문서 — 다른 셸을 extends 하면 IM26', found(out, 'IM26', GUEST_SHELL, 1), out[-900:])
    p.reset(base)
    # 조각의 extends 대상 = 어느 뿌리든 component/**.html
    p.w('web/design_system/guest/component/card/guest_card.html', '<div class="guest-card">{% block body %}{% endblock %}</div>')
    p.w('web/application/lobby/presentation_layer/section/lobby_card_section.html',
        '{% extends "design_system/guest/component/card/guest_card.html" %}', '{% block body %}x{% endblock %}')
    p.w('web/application/lobby/presentation_layer/section/lobby_button_section.html',
        '{% extends "design_system/component/button/primary_button.html" %}')
    p.w('web/application/lobby/presentation_layer/widget/badge_widget.html', '{% extends "' + GUEST_SHELL + '" %}')
    p.sub(page, '<p>lobby</p>', '{% include "design_system/component/button/primary_button.html" with label="go" href=href only %}\n'
          '{% include "design_system/guest/component/card/guest_card.html" %}')
    e, out = backstop(p.root, '--diff-base', base)
    check('S6 조각이 own 뿌리 component 를 extends — 통과',
          not found(out, 'IM26', 'application/lobby/presentation_layer/section/lobby_card_section.html'), out[-900:])
    check('S6 조각이 평면 component 를 extends — 통과',
          not found(out, 'IM26', 'application/lobby/presentation_layer/section/lobby_button_section.html'))
    badge = 'application/lobby/presentation_layer/widget/badge_widget.html'
    check('S6 조각이 셸을 extends — IM26 그대로', found(out, 'IM26', badge, 1))
    check('S6 선언 모드의 조각 사유 · 교정 문구 — root_view.html · 평면 component 고정이 아니다',
          'root_view.html' not in message_of(out, 'IM26', badge) + fix_of(out, 'IM26', badge)
          and '어느 제품 뿌리든' in message_of(out, 'IM26', badge) and '어느 제품 뿌리든' in fix_of(out, 'IM26', badge),
          message_of(out, 'IM26', badge) + '\n' + fix_of(out, 'IM26', badge))
    check('S6 공용 마크업(평면 component html) · 제품 마크업 include — 통과', not found(out, 'IM13', LOBBY_PAGE) and not found(out, 'IM2', LOBBY_PAGE), out[-900:])
    p.reset(base)
    # 남의 셸 CSS · 자기 셸 CSS 직접 링크 — IM2 그대로(예외를 만들지 않는다)
    p.w('web/static/root/root_view.css', '.root-frame { width: 1px; }')
    p.w('web/static/root/root_guest_view.css', '.guest-frame { width: 1px; }')
    p.sub(page, '<p>lobby</p>', link('web/root/root_view.css') + '\n' + link('web/root/root_guest_view.css'))
    e, out = backstop(p.root, '--diff-base', base)
    check('S7 페이지가 남의 셸 CSS · 자기 셸 CSS 를 직접 링크 — IM2 2건(예외 없음)',
          found(out, 'IM2', LOBBY_PAGE, 4) and found(out, 'IM2', LOBBY_PAGE, 5), out[-900:])
    p.reset(base)

    # ---- 선언이 없으면 지금처럼 — root_view.html 만
    q = mkstd(tmp / 's2')
    mkbc(q, 'application/lobby')
    own_root(q, 'guest')
    base2 = q.commit('base')
    q.sub(page, '<p>lobby</p>', '<p>lobby 2</p>')
    q.sub('web/' + LOBBY_PAGE, '{% extends "' + FLAT_SHELL + '" %}', "{% extends '" + FLAT_SHELL + "' %}")
    e, out = backstop(q.root, '--diff-base', base2)
    check('S8 선언 없음 — 손님 화면이 root_view.html 을 extends 해도 지금처럼 통과', e == 0 and 'BLOCKER' not in out, out[-600:])
    q.sub('web/' + LOBBY_PAGE, FLAT_SHELL, GUEST_SHELL)
    e, out = backstop(q.root, '--diff-base', base2)
    check('S8 선언 없음 — 둘째 셸 extends 는 지금처럼 IM2 + IM26',
          found(out, 'IM2', LOBBY_PAGE, 1) and found(out, 'IM26', LOBBY_PAGE, 1) and 'root_view.html 하나' in message_of(out, 'IM26', LOBBY_PAGE), out[-900:])
    q.w('web/application/lobby/presentation_layer/widget/badge_widget.html', '{% extends "' + FLAT_SHELL + '" %}')
    e, out = backstop(q.root, '--diff-base', base2, '--only', 'im26')
    badge = 'application/lobby/presentation_layer/widget/badge_widget.html'
    check('S8 선언 없음 — 조각 IM26 의 사유 · 교정 문구는 글자 그대로',
          message_of(out, 'IM26', badge) == '`{% extends %}` 대상 `root/scaffold/view/root_view.html` — 조각 템플릿의 상속 대상은 '
          'design_system/component/**/*.html(부품의 block 채우기) (제1 규약 §3.6·§5)'
          and fix_of(out, 'IM26', badge) == '페이지는 root_view.html 을 extends 하고, 조각은 값은 include … only 로·마크업 자리는 '
          'design_system component 를 extends 해 block 만 채운다.', message_of(out, 'IM26', badge) + '\n' + fix_of(out, 'IM26', badge))

    # ---- 소속 있는 페이지의 개명만 — 전 줄이 새 줄이라 옛 잘못된 셸이 한꺼번에 선다(지금 동작의 단언)
    r, _ = mkdeclared(tmp / 's3')
    r.sub('web/' + LOBBY_PAGE, GUEST_SHELL, FLAT_SHELL)
    wrong = r.commit('wrong shell lands as debt')
    e, out = backstop(r.root, '--diff-base', wrong)
    check('S9 옛 잘못된 셸(기준점에 이미 있음) — 게이트 0', e == 0 and 'BLOCKER' not in out, out[-600:])
    moved = 'application/lobby/presentation_layer/view/lobby_home_view.html'
    r.mv('web/' + LOBBY_PAGE, 'web/' + moved)
    r.mv('web/' + LOBBY_PAGE[:-5] + '.py', 'web/' + moved[:-5] + '.py')
    e, out = backstop(r.root, '--diff-base', wrong, '--only', 'im26')
    check('S9 그 페이지의 개명만 — 새 경로 전 줄이 새 줄이라 IM26 이 선다', found(out, 'IM26', moved, 1), out[-900:])


# ====================================================================== M — 혼입(IM13 제품 분기)

def bundle_mixing(tmp):
    p, base = mkdeclared(tmp / 'm')
    page = 'web/' + LOBBY_PAGE
    # 기준점에 이미 있는 옛 혼입 링크(운영자 부품 CSS)와 옛 @import
    p.sub(page, '<p>lobby</p>', link('design_system/component/button/primary_button.css') + '\n<p>lobby</p>')
    p.w('web/' + LOBBY_CSS, '@import url("../../../design_system/foundation/app_color.css");', '.lobby { width: 1px; }')
    base = p.commit('old-mixing')
    button_css = 'design_system/component/button/primary_button.css'

    p.sub(page, '<p>lobby</p>', '<p>lobby again</p>')
    p.append('web/' + LOBBY_CSS, '.lobby-more { width: 2px; }')
    e, out = backstop(p.root, '--diff-base', base)
    check('M1 파일을 손댔을 뿐 — 옛 링크 · 옛 @import 불발화', e == 0 and 'BLOCKER' not in out, out[-900:])
    p.reset(base)

    p.sub(page, '<p>lobby</p>', link('design_system/theme/app_theme.css') + '\n<p>lobby</p>')
    e, out = backstop(p.root, '--diff-base', base)
    msg = message_of(out, 'IM13', LOBBY_PAGE)
    check('M2 새 링크 줄 — 그 줄만 IM13(옛 링크 줄은 그대로)', e == 2 and found(out, 'IM13', LOBBY_PAGE, 5)
          and out.count('[IM13] BLOCKER') == 1, out[-900:])
    check('M2 사유에 두 제품 id 와 실린 경로 · 규약 표지(제품 CSS 혼입)', '`guest`' in msg and '`operator`' in msg
          and 'design_system/theme/app_theme.css' in msg and msg.endswith('(discipline-houserules §5·§6 제품 CSS 혼입)'), msg)
    p.reset(base)

    p.sub(page, '{% extends "' + GUEST_SHELL + '" %}', "{% extends '" + GUEST_SHELL + "' %}")
    e, out = backstop(p.root, '--diff-base', base)
    check('M3 extends 줄이 새 줄 — 그 문서의 직접 CSS 링크 전부(옛 링크 줄 4)', found(out, 'IM13', LOBBY_PAGE, 4)
          and button_css in message_of(out, 'IM13', LOBBY_PAGE), out[-900:])
    p.reset(base)

    p.declare(dict(PRODUCTS, operator={'design_system': 'flat', 'bcs': ['order', 'admin/desk']}))
    e, out = backstop(p.root, '--diff-base', base)
    check('M4 선언 파일만 바뀜 — 기존 참조를 새 줄로 보지 않는다(blocker 0)', e == 0 and 'BLOCKER' not in out, out[-900:])
    p.reset(base)
    # 소속 있는 페이지의 개명만 — 전 줄이 새 줄이라 옛 혼입 링크가 선다(지금 동작의 단언)
    renamed = 'application/lobby/presentation_layer/view/lobby_home_view.html'
    p.mv(page, 'web/' + renamed)
    e, out = backstop(p.root, '--diff-base', base, '--only', 'im13')
    check('M4 옛 혼입 링크가 있는 페이지의 개명만 — 새 경로에서 IM13 이 선다', lines_of(out, 'IM13', renamed) == [4], out[-900:])
    p.reset(base)
    keys = p.keys()
    check('M4 빚 스캔은 전수 — 옛 링크 · 옛 @import 의 IM13 키', {'IM13|' + LOBBY_PAGE, 'IM13|' + LOBBY_CSS} <= keys, sorted(keys))
    e, out = backstop(p.root, '--all', '--only', 'im13')
    check('M4 --all 도 같은 해석(게이트 build 와 빚 스캔 from_files 가 같은 resolver)',
          found(out, 'IM13', LOBBY_PAGE, 4) and found(out, 'IM13', LOBBY_CSS, 1), out[-900:])

    # 표준 자리 종류 넷 · 표준 7 파일 밖 foundation 은 판정 밖
    p.w('web/design_system/util/flat_util.css', '.u { width: 1px; }')
    p.w('web/design_system/foundation/tokens.css', ':root { --chat-bg: 1px; }')
    base = p.commit('flat-extras')
    p.sub(page, '<p>lobby</p>', '\n'.join([link('design_system/foundation/app_spacing.css'), link('design_system/theme/app_theme.css'),
                                          link('design_system/util/flat_util.css'), link('design_system/foundation/tokens.css'),
                                          link('design_system/foundation/motion.css'), link('design_system/guest/theme/app_theme.css'),
                                          link('design_system/guest/foundation/app_color.css'), '<p>lobby</p>']))
    e, out = backstop(p.root, '--diff-base', base)
    lines = sorted(int(n) for n in re.findall(r'^\[IM13\] BLOCKER — web/%s:(\d+)$' % re.escape(LOBBY_PAGE), out, re.M))
    check('M5 표준 자리(foundation 7 · theme · util) 새 링크 — IM13 · 7 파일 밖 foundation 과 자기 제품 CSS 는 판정 밖',
          lines == [5, 6, 7], '%r\n%s' % (lines, out[-900:]))
    p.reset(base)

    # @import — 조각 CSS · 제품 CSS · 틀 CSS
    p.append('web/' + LOBBY_CSS, '@import url("../../../design_system/theme/app_theme.css");',
             '@import url("../../../design_system/guest/foundation/app_color.css");',
             '@import "../../../design_system/foundation/tokens.css";')
    p.append('web/design_system/guest/theme/app_theme.css', '@import url("../../foundation/app_color.css");',
             '@import url("../foundation/app_color.css");')
    p.w('web/static/root/root_guest_view.css', '@import url("../../design_system/util/flat_util.css");', '.guest-frame { width: 1px; }')
    p.append('web/design_system/theme/app_theme.css', '@import url("../guest/util/motion.css");')
    e, out = backstop(p.root, '--diff-base', base)
    check('M6 BC 조각 CSS 의 새 @import — 남의 표준 자리만 IM13(자기 제품 · 7 파일 밖은 통과)',
          [int(n) for n in re.findall(r'^\[IM13\] BLOCKER — web/%s:(\d+)$' % re.escape(LOBBY_CSS), out, re.M)] == [3], out[-1200:])
    check('M6 own 뿌리 CSS 가 평면 표준 CSS 를 @import — IM13 · 자기 뿌리는 통과',
          [int(n) for n in re.findall(r'^\[IM13\] BLOCKER — web/design_system/guest/theme/app_theme.css:(\d+)$', out, re.M)] == [2], out[-1200:])
    check('M6 틀 CSS(static/root/root_guest_view.css)= 그 셸의 제품 — 평면 util @import 는 IM13', found(out, 'IM13', 'static/root/root_guest_view.css', 1))
    check('M6 평면 CSS 가 own 뿌리 util 을 @import — IM13(operator ← guest)',
          found(out, 'IM13', 'design_system/theme/app_theme.css', 2) and '`operator`' in message_of(out, 'IM13', 'design_system/theme/app_theme.css'))
    p.reset(base)

    # 셸 · 운영자 페이지 · 옛 배치 페이지
    p.sub('web/' + GUEST_SHELL, '<html><head>', '<html><head>\n' + link('design_system/theme/app_theme.css') + '\n' + link('design_system/foundation/tokens.css'))
    p.sub('web/' + FLAT_SHELL, '<html><head>', '<html><head>\n' + link('design_system/guest/theme/app_theme.css'))
    p.sub('web/' + ORDER_PAGE, '{% block content %}', '{% block content %}\n' + link('design_system/guest/util/motion.css'))
    p.w('web/auth/login/view/login.html', '{% extends "' + GUEST_SHELL + '" %}', '{% load static %}',
        link('design_system/theme/app_theme.css'), link('design_system/guest/theme/app_theme.css'))
    e, out = backstop(p.root, '--diff-base', base)
    check('M7 손님 셸이 운영자 theme 을 싣는다 — IM13 · 옛 값 파일(tokens.css)은 판정 밖',
          [int(n) for n in re.findall(r'^\[IM13\] BLOCKER — web/%s:(\d+)$' % re.escape(GUEST_SHELL), out, re.M)] == [3], out[-1200:])
    check('M7 운영자 셸이 손님 theme 을 싣는다 — IM13', found(out, 'IM13', FLAT_SHELL, 3))
    check('M7 운영자 페이지가 손님 util 을 싣는다 — IM13', found(out, 'IM13', ORDER_PAGE, 4))
    check('M7 옛 배치 페이지는 어느 제품에도 속하지 않는다 — IM13 · IM26 0', not found(out, 'IM13', 'auth/login/view/login.html')
          and not found(out, 'IM26', 'auth/login/view/login.html'))
    p.reset(base)

    # 꼬리(query · fragment)가 붙었거나 정규화 안 된(`..` · `./`) 경로 — 제품 판정은 실제로 실리는 파일로 한다
    theme = 'design_system/guest/theme/app_theme.css'
    p.append('web/' + theme, '@import url("../../foundation/app_color.css?v=1");',      # 운영자 foundation(꼬리 ?)
             '@import "../../foundation/app_spacing.css#top";',                           # 운영자 foundation(꼬리 #)
             '@import url("../../guest/../theme/./app_theme.css");',                      # 운영자 theme(.. · ./)
             '@import url("../foundation/app_color.css?v=2");',                           # 자기 제품(꼬리 ?) — 통과
             '@import url("../../guest/foundation/../theme/app_theme.css");')             # 자기 제품(..) — 통과
    p.sub(page, '<p>lobby</p>', '\n'.join([link('design_system/guest/../foundation/app_color.css'),      # 운영자(..)
                                          link('design_system/./theme/app_theme.css'),                    # 운영자(./)
                                          link('web/../design_system/util/flat_util.css'),                # 운영자(static 접두 밖으로 ..)
                                          link('design_system/guest/theme/../theme/app_theme.css'),       # 자기 제품(..) — 통과
                                          link('design_system/foundation/../foundation/tokens.css'),      # 7 파일 밖 — 판정 밖
                                          '<p>lobby</p>']))
    e, out = backstop(p.root, '--diff-base', base, '--only', 'im13')
    check('M9 CSS @import 의 꼬리(?v=1 · #top) · `..`/`./` — 실제 대상이 남의 표준 자리면 IM13(자기 제품은 통과)',
          lines_of(out, 'IM13', theme) == [2, 3, 4], '%r\n%s' % (lines_of(out, 'IM13', theme), out[-1500:]))
    check('M9 `{% static %}` 의 `..` · `./` · `web/../` — 실제 대상이 남의 표준 자리면 IM13(자기 제품 · 7 파일 밖은 통과)',
          lines_of(out, 'IM13', LOBBY_PAGE) == [5, 6, 7], '%r\n%s' % (lines_of(out, 'IM13', LOBBY_PAGE), out[-1500:]))
    msgs = '\n'.join(re.findall(r'^  위반: (.+)$', out, re.M))
    check('M9 사유의 실린 경로는 정규화한 실제 CSS · Finding 경로는 문서의 물리 경로 그대로',
          '`design_system/foundation/app_color.css`' in msgs and '`design_system/util/flat_util.css`' in msgs
          and '?v=1' not in msgs and '/../' not in msgs and '/./' not in msgs, msgs)
    p.commit('tails and dots land as debt')
    e, out, data = p.scan()
    counts = data.get('counts', {})
    check('M9 빚 스캔도 같은 판정 — 키는 문서의 물리 경로 · 발견 수 3 · 3(+ 옛 링크 1)',
          counts.get('IM13|' + theme) == 3 and counts.get('IM13|' + LOBBY_PAGE) == 4, sorted(counts.items()))
    p.reset(base)

    # 선언이 없으면 혼입 판정 자체가 없다
    p.rm(REGISTRY)
    base = p.commit('undeclare')
    p.sub(page, '<p>lobby</p>', link('design_system/theme/app_theme.css') + '\n<p>lobby</p>')
    e, out = backstop(p.root, '--diff-base', base, '--only', 'im13')
    check('M8 선언 없음 — 같은 새 링크에 IM13 0', e == 0 and 'BLOCKER' not in out, out[-600:])


# ====================================================================== R — 해석(area · 예정 BC · "*" · 빚 스캔)

def bundle_resolve(tmp):
    p = mkstd(tmp / 'r')
    for rel in ('application/admin/desk', 'application/shop/desk', 'application/misc'):
        mkbc(p, rel)
    own_root(p, 'guest')
    p.declare({'operator': {'design_system': 'flat', 'bcs': ['order', 'admin/desk']},
               'guest': {'design_system': 'own', 'bcs': ['shop/desk']}})
    base = p.commit('base')
    admin = 'application/admin/desk/presentation_layer/view/desk_view.html'
    shop = 'application/shop/desk/presentation_layer/view/desk_view.html'
    misc = 'application/misc/presentation_layer/view/misc_view.html'
    for rel in (admin, shop, misc):
        p.sub('web/' + rel, '{% extends "' + FLAT_SHELL + '" %}', "{% extends '" + FLAT_SHELL + "' %}")
    e, out = backstop(p.root, '--diff-base', base)
    check('R1 같은 BC 이름 · 다른 area — 전체 경로로 가른다(shop/desk 만 IM26)',
          found(out, 'IM26', shop, 1) and not found(out, 'IM26', admin) and not found(out, 'IM26', misc), out[-900:])
    for rel in (admin, shop, misc):
        p.sub('web/' + rel, FLAT_SHELL, GUEST_SHELL)
    e, out = backstop(p.root, '--diff-base', base)
    check('R1 손님 셸로 — admin/desk 만 IM26 · 선언 밖 BC(misc)는 선언된 셸 어느 것이든',
          found(out, 'IM26', admin, 1) and not found(out, 'IM26', shop) and not found(out, 'IM26', misc)
          and 'IM2] BLOCKER' not in out, out[-900:])
    p.reset(base)

    # area 이름만 적음 — 오류는 아니고(area 판별이 휴리스틱) [info] 한 줄 · 그 아래 BC 와는 맞지 않는다
    p.declare({'operator': {'design_system': 'flat', 'bcs': ['order', 'admin']}, 'guest': {'design_system': 'own', 'bcs': ['shop']}})
    e, out = backstop(p.root, '--diff-base', base)
    info = [ln for ln in out.splitlines() if 'area 폴더다' in ln]
    check('R1b 선언에 area 이름만 — [info] 한 줄(exit 0 · 예정 BC 알림은 아님)', e == 0 and len(info) == 1
          and info[0].startswith('[info] 제품 선언의 ') and 'operator → admin' in info[0] and 'guest → shop' in info[0]
          and '<area>/<bc> 전체 경로로 적는다' in info[0] and '예정 BC' not in out, out[-700:])
    e, out, _data = p.scan()
    check('R1b 빚 스캔에도 같은 [info]', sum('area 폴더다' in ln for ln in out.splitlines()) == 1, out[-500:])
    p.reset(base)
    e, out = backstop(p.root, '--diff-base', base)
    check('R1b 전체 경로로 적으면 알림 없음', 'area 폴더다' not in out, out[-400:])

    # 예정 BC · "*"
    p.declare({'operator': {'design_system': 'flat', 'bcs': ['order', 'admin/desk', 'admin/operator_teller']},
               'guest': {'design_system': 'own', 'bcs': '*'}})
    base = p.commit('planned')
    e, out = backstop(p.root, '--diff-base', base)
    info = [ln for ln in out.splitlines() if ln.startswith('[info] 제품 선언의 BC')]
    check('R2 예정 BC — 오류가 아니라 [info] 한 줄(exit 0)', e == 0 and len(info) == 1 and 'admin/operator_teller' in info[0]
          and 'admin/desk' not in info[0], out[-600:])
    e, out, _data = p.scan()
    check('R2 빚 스캔에도 같은 [info] 한 줄', sum(ln.startswith('[info] 제품 선언의 BC') for ln in out.splitlines()) == 1, out[-600:])
    for rel in (shop, misc):
        p.sub('web/' + rel, '{% extends "' + FLAT_SHELL + '" %}', "{% extends '" + FLAT_SHELL + "' %}")
    promo = 'application/promo/presentation_layer/view/promo_view.html'
    p.w('web/' + promo, '{% extends "' + FLAT_SHELL + '" %}')
    teller = 'application/admin/operator_teller/presentation_layer/view/operator_teller_view.html'
    p.w('web/' + teller, '{% extends "' + FLAT_SHELL + '" %}')
    e, out = backstop(p.root, '--diff-base', base)
    check('R3 "*" = application 아래 나머지 BC 전부(shop/desk · misc · 새 promo 가 손님)',
          found(out, 'IM26', shop, 1) and found(out, 'IM26', misc, 1) and found(out, 'IM26', promo, 1), out[-1200:])
    check('R3 예정 BC 가 생기면 그 제품(operator) — root_view.html extends 통과 · [info] 사라짐',
          not found(out, 'IM26', teller) and '[info] 제품 선언의 BC' not in out, out[-1200:])
    # area 판별이 안 선 중간 상태(area 직속 코드 파일)에서도 선언한 전체 경로가 이긴다
    p.w('web/application/admin/notes.py', 'x: int = 1')
    e, out = backstop(p.root, '--diff-base', base, '--only', 'im26')
    check('R4 area 판별 전이어도 선언한 `<area>/<bc>` 전체 경로가 이긴다', not found(out, 'IM26', teller) and found(out, 'IM26', promo, 1), out[-900:])
    p.sub('web/' + teller, FLAT_SHELL, GUEST_SHELL)
    e, out = backstop(p.root, '--diff-base', base, '--only', 'im26')
    check('R4 그 BC 가 손님 셸을 extends — IM26', found(out, 'IM26', teller, 1), out[-900:])
    p.reset(base)

    # resolver 직접 — build 와 from_files 가 같은 해석
    probe = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
from pathlib import Path
from src.common import BackstopContext
from src.debt import debt_universe
from src.products import products_state
root = Path(sys.argv[2])
out = []
for ctx in (BackstopContext.build(root, None, False), BackstopContext.from_files(root, debt_universe(root))):
    s = products_state(ctx)
    out.append({
        'declared': s.declared, 'flat': s.flat, 'own': list(s.own), 'shells': sorted(s.shells),
        'split': [list(map(list, [[s.ds_split(f)[0]], s.ds_split(f)[1]])) for f in (
            'design_system/foundation/app_color.css', 'design_system/guest/foundation/app_color.css',
            'design_system/partner/x.css', 'design_system/guest')],
        'bc': [s.product_of_bc(b) for b in ('order', 'admin/desk', 'admin/operator_teller', 'shop/desk', 'nope')],
        'file': [s.product_of(f, ctx.areas) for f in (
            'application/admin/desk/presentation_layer/view/desk_view.html', 'application/shop/desk/x.py',
            'static/application/shop/desk/desk_view.css', 'static/application/order/order_list_view.css',
            'root/scaffold/view/root_view.html', 'root/scaffold/view/root_guest_view.html', 'static/root/root_view.css',
            'static/root/root_guest_view.css', 'root/scaffold/view/root_login_view.html', 'static/root/other.css',
            'design_system/component/button/primary_button.html', 'design_system/guest/util/motion.css',
            'auth/login/view/login.html', 'common/util/x.py', 'urls.py')],
        'std': [s.standard_css_owner(f) for f in (
            'design_system/foundation/app_color.css', 'design_system/foundation/tokens.css', 'design_system/theme/app_theme.css',
            'design_system/theme/dark.css', 'design_system/component/button/primary_button.css',
            'design_system/component/button/primary_button.html', 'design_system/component/loose.css',
            'design_system/util/a.css', 'design_system/guest/util/a.css', 'design_system/guest/foundation/app_asset.css',
            'static/css/base.css')],
    })
print(json.dumps(out))
'''
    r = subprocess.run([sys.executable, '-B', '-c', probe, str(SCRIPTS), str(p.root)], capture_output=True, text=True, env=ENV)
    try:
        got = json.loads(r.stdout)
    except ValueError:
        got = None
    want = {
        'declared': True, 'flat': 'operator', 'own': ['guest'], 'shells': [GUEST_SHELL, FLAT_SHELL],
        'split': [[['operator'], ['foundation', 'app_color.css']], [['guest'], ['foundation', 'app_color.css']],
                  [['operator'], ['partner', 'x.css']], [['guest'], []]],
        'bc': ['operator', 'operator', 'operator', 'guest', 'guest'],
        'file': ['operator', 'guest', 'guest', 'operator', 'operator', 'guest', 'operator', 'guest', None, None,
                 'operator', 'guest', None, None, None],
        'std': ['operator', None, 'operator', None, 'operator', None, None, 'operator', 'guest', 'guest', None],
    }
    check('R5 resolver — 경로 → (제품, 뿌리 안 상대 경로) · 셸 · BC · 파일 소속 · 표준 자리 CSS(build)', got is not None and got[0] == want,
          '%s\n%r' % (r.stderr[-600:], got and got[0]))
    check('R5 resolver — build 와 from_files 가 같은 해석', got is not None and got[0] == got[1], repr(got))
    p.rm(REGISTRY)
    r = subprocess.run([sys.executable, '-B', '-c', probe, str(SCRIPTS), str(p.root)], capture_output=True, text=True, env=ENV)
    try:
        got = json.loads(r.stdout)[0]
    except ValueError:
        got = None
    check('R6 선언 없음 — «기본 한 제품»(뿌리 하나 · 셸 하나 · 소속 없음)', got is not None and got['declared'] is False
          and got['flat'] is None and got['own'] == [] and got['shells'] == [FLAT_SHELL]
          and got['split'][1] == [[None], ['guest', 'foundation', 'app_color.css']] and set(got['file']) == {None}
          and set(got['bc']) == {None} and set(got['std']) == {None}, '%s\n%r' % (r.stderr[-600:], got))


# ====================================================================== N — 알림 · A — 첫 등록

def bundle_notices(tmp):
    p, base = mkdeclared(tmp / 'n')
    head = '[info] 제품 선언이 기준점 뒤 바뀌었다 — G2 배너에 diff 원문'
    e, out = backstop(p.root, '--diff-base', base)
    check('N1 선언 무변 — 알림 없음', e == 0 and head not in out, out[-400:])
    p.declare(dict(PRODUCTS, operator={'design_system': 'flat', 'bcs': ['order', 'admin/desk']}))
    e, out = backstop(p.root, '--diff-base', base)
    check('N2 선언 미커밋 수정 — [info] 한 줄(exit 는 그대로 0)', e == 0 and sum(ln.startswith(head) for ln in out.splitlines()) == 1, out[-600:])
    mid = p.commit('declare-more')
    e, out = backstop(p.root, '--diff-base', base)
    check('N2 선언 커밋 수정 — [info]', e == 0 and head in out, out[-600:])
    e, out = backstop(p.root, '--diff-base', mid)
    check('N2 기준점을 그 뒤로 — 알림 없음', e == 0 and head not in out, out[-600:])
    e, out = backstop(p.root)
    check('N2 기준점 없음(전역 퇴화) — 알림 없음', head not in out, out[-600:])
    p.rm(REGISTRY)
    e, out = backstop(p.root, '--diff-base', mid)
    check('N3 선언 삭제 — [info] · 선언 없는 해석으로 돈다', head in out, out[-600:])
    p.reset(mid)
    q = mkstd(tmp / 'n2')
    base2 = q.commit('base')
    own_root(q, 'guest')
    q.declare(PRODUCTS)
    e, out = backstop(q.root, '--diff-base', base2)
    check('N4 새 선언(미추적) — [info]', e == 0 and head in out, out[-600:])


def bundle_first_registration(tmp):
    """이미 있는 own 경로의 첫 등록 — 적법해지는 키와 새로 보이는 키의 기대표."""
    p = mkstd(tmp / 'a')
    mkbc(p, 'application/lobby', shell=GUEST_SHELL)
    own_root(p, 'guest')
    p.w('web/design_system/guest/foundation/tokens.css', ':root { --chat-bg: 1px; }')
    p.w('web/design_system/guest/component/card/guest_card.css', '.wrong { width: 1px; }')
    p.w('web/design_system/guest/legacy/old.css', 'body {}')
    # 옛 배치 · 평면 빚(선언만으로 줄지 않아야 하는 키)
    p.w('web/base/base.html', '<html></html>')
    p.w('web/design_system/foundation/motion.css', '.m { width: 1px; }')
    p.w('web/static/css/base.css', 'body {}')
    p.commit('base')
    before = p.keys()
    lawful = {'IM2|' + LOBBY_PAGE, 'IM26|' + LOBBY_PAGE}
    flat_legacy = {'ST0|base/base.html', 'ST10|design_system/foundation/motion.css', 'ST12|static/css/base.css'}
    check('A1 선언 전 — 손님 셸 상속은 IM2 · IM26 빚, 중첩 폴더는 무검사', before == lawful | flat_legacy, sorted(before))
    p.declare(PRODUCTS)
    p.commit('declare')
    after = p.keys()
    newly = {'ST10|design_system/guest/foundation/tokens.css', 'NM12|design_system/guest/component/card/guest_card.css',
             'ST10|design_system/guest/legacy/old.css'}
    check('A2 첫 등록 뒤 — 적법해진 키(IM2 · IM26)만 사라지고 own 뿌리 검사 키가 새로 보인다',
          after == flat_legacy | newly, sorted(after))
    check('A2 초기 선언만 더함 — 기존 평면 · 옛 배치 키 감소 0', flat_legacy <= after)


# ====================================================================== I — 승인 병합 유입

def bundle_inflow(tmp):
    p = mkstd(tmp / 'i')
    mkbc(p, 'application/lobby')
    base = p.commit('base')
    git(p.root, 'checkout', '-qb', 'lane')
    event = 'application/lobby/presentation_layer/view/lobby_event_view.html'
    p.w('web/' + event, '{% extends "' + FLAT_SHELL + '" %}')
    p.w('web/' + event[:-5] + '.py', 'def lobby_event_view(request: object) -> object:', '    return request')
    p.commit('lane-page')
    folder = p.root / '.dddjango-web' / 'build'
    folder.mkdir(parents=True)
    (folder / 'build-state.json').write_text(json.dumps({'git_snapshot': base, 'slices': []}), encoding='utf-8')
    e, out = backstop(p.root, '--diff-base', base, '--design-build', folder)
    check('I0 선언 유입 전 — 레인의 손님 화면(root_view.html extends)은 통과', e == 0 and 'BLOCKER' not in out, out[-600:])
    # main: 선언 + 손님 골격 + (선언대로면 잘못된 셸인) 새 페이지
    git(p.root, 'checkout', '-q', 'main')
    own_root(p, 'guest')
    p.declare(PRODUCTS)
    promo = 'application/lobby/presentation_layer/view/lobby_promo_view.html'
    p.w('web/' + promo, '{% extends "' + FLAT_SHELL + '" %}')
    p.w('web/' + promo[:-5] + '.py', 'def lobby_promo_view(request: object) -> object:', '    return request')
    p.commit('main-declares')
    git(p.root, 'checkout', '-q', 'lane')
    git(p.root, 'merge', '--no-ff', '-q', '-m', 'receive-main', 'main')
    merge = git(p.root, 'rev-parse', 'HEAD')
    (folder / 'approved-merges.txt').write_text(merge + ' main\n', encoding='utf-8')
    e, out = backstop(p.root, '--diff-base', base, '--design-build', folder)
    blocker, _, approved = out.partition('== 승인 유입(')
    check('I1 병합이 들인 파일의 선언 위반 — 승인 유입(부모 스냅숏에 선언이 실린다)',
          found(approved, 'IM26', promo, 1) and not found(blocker, 'IM26', promo) and '(L 증명)' in approved, out[-1500:])
    check('I1 선언 유입으로 판정만 바뀐 레인 파일 — 이 레인 몫(유입으로 가르지 않는다) · exit 2',
          e == 2 and found(blocker, 'IM26', event, 1) and '이 레인 몫으로 남김' in blocker, out[-1500:])
    check('I1 선언 변경 [info]', '[info] 제품 선언이 기준점 뒤 바뀌었다' in blocker)

    # 승인 병합으로 «선언만»(골격 · 셸 없이) 받은 레인 — 선언된 뿌리 · 셸 부재 ST4 는 유입으로 갈리지 않고 이 레인 몫이다
    q = mkstd(tmp / 'i2')
    base = q.commit('base')
    git(q.root, 'checkout', '-qb', 'lane')
    q.w('lane.txt', 'lane')
    q.commit('lane')
    folder = q.root / '.dddjango-web' / 'build'
    folder.mkdir(parents=True)
    (folder / 'build-state.json').write_text(json.dumps({'git_snapshot': base, 'slices': []}), encoding='utf-8')
    git(q.root, 'checkout', '-q', 'main')
    q.declare(PRODUCTS)
    q.commit('main-declares-only')
    git(q.root, 'checkout', '-q', 'lane')
    git(q.root, 'merge', '--no-ff', '-q', '-m', 'receive-main', 'main')
    (folder / 'approved-merges.txt').write_text(git(q.root, 'rev-parse', 'HEAD') + ' main\n', encoding='utf-8')
    e, out = backstop(q.root, '--diff-base', base, '--design-build', folder)
    blocker, _, approved = out.partition('== 승인 유입(')
    check('I2 선언만 받은 레인 — 선언된 뿌리 · 셸 ST4 두 건은 이 레인 몫(승인 유입 아님) · exit 2',
          e == 2 and found(blocker, 'ST4', 'design_system/guest') and found(blocker, 'ST4', GUEST_SHELL)
          and 'ST4] BLOCKER' not in approved and blocker.count('이 레인 몫으로 남김') == 2, out[-1500:])
    e, out = backstop(q.root, '--diff-base', base, '--design-build', folder, '--slice-end')
    check('I2 슬라이스 끝에서는 그 ST4 를 미룬다(exit 0)', e == 0 and 'ST4] BLOCKER' not in out, out[-600:])


# ====================================================================== X — 치환 확인의 static 접두 횡단 이동

TEST_REFS = '''from django.templatetags.static import static

CSS_PATH: str = "web/static/css/base.css"
CSS_DIR: str = "web/static/css/"
FRAME_PATH: str = "web/design_system/util/frame.css"


def test_static_urls(storages: dict) -> None:
    assert static("web/css/base.css") == "/static/web/css/base.css"
    assert storages["staticfiles"].url("web/css/base.css") == "/static/web/css/base.css"
    assert static("web/css/extra.css")
    assert static("design_system/util/frame.css") == "/static/design_system/util/frame.css"
    assert static("design_system/theme/app_theme.css") != static("web/css/base.css")
'''


def bundle_crossing(tmp):
    p = mkstd(tmp / 'x')
    p.w('web/static/css/base.css', 'body { margin: 0; }', 'a { width: 1px; }')
    p.w('web/static/css/extra.css', 'p { margin: 0; }', 'b { width: 2px; }')
    p.w('web/design_system/util/frame.css', '.frame { width: 480px; }', '.frame__body { width: 100%; }')
    (p.root / 'tests').mkdir()
    (p.root / 'tests/test_static_refs.py').write_text(TEST_REFS, encoding='utf-8')
    p.w('tests/fixtures/page.txt', 'web/static/css/base.css', '/static/web/css/base.css', "{% static 'web/css/base.css' %}")
    base = p.commit('base')
    p.mv('web/static/css/base.css', 'web/design_system/legacy/base.css')
    p.mv('web/static/css/extra.css', 'web/design_system/legacy/extra.css')
    p.mv('web/design_system/util/frame.css', 'web/static/root/root_view.css')
    moved = (TEST_REFS.replace('"web/static/css/', '"web/design_system/legacy/')
             .replace('web/css/base.css', 'design_system/legacy/base.css')
             .replace('web/css/extra.css', 'design_system/legacy/extra.css')
             .replace('"web/design_system/util/frame.css"', '"web/static/root/root_view.css"')
             .replace('design_system/util/frame.css', 'web/root/root_view.css'))
    (p.root / 'tests/test_static_refs.py').write_text(moved, encoding='utf-8')
    p.w('tests/fixtures/page.txt', 'web/design_system/legacy/base.css', '/static/design_system/legacy/base.css',
        "{% static 'design_system/legacy/base.css' %}")
    target = p.commit('move')
    e, out = backstop(p.root, '--subst-check', base, target)
    check('X1 static 접두를 건너는 이동(static → design_system · design_system → static · 폴더째)의 참조 치환 — exit 0',
          e == 0 and '어긋남' not in out, 'exit=%d\n%s' % (e, out[-1200:]))
    check('X1 헛대조 아님 — 시험 파일 둘을 실제로 대조', 'web/ 밖 변경 파일 2' in out, out[-400:])
    # 잘못된 꼴 — 저장소 경로를 static 식별자 자리에 · 치환 아닌 변경
    wrong = moved.replace('static("design_system/legacy/base.css") == ', 'static("web/design_system/legacy/base.css") == ')
    (p.root / 'tests/test_static_refs.py').write_text(wrong, encoding='utf-8')
    bad = p.commit('wrong-form')
    e, out = backstop(p.root, '--subst-check', base, bad)
    check('X2 static 식별자 자리에 저장소 경로 꼴 — 치환으로 받지 않는다(exit 2)', e == 2 and 'tests/test_static_refs.py' in out, out[-600:])
    (p.root / 'tests/test_static_refs.py').write_text(moved.replace('!= static', '== static'), encoding='utf-8')
    bad = p.commit('assert-change')
    e, out = backstop(p.root, '--subst-check', base, bad)
    check('X2 단언을 바꾼 변경 — exit 2 그대로', e == 2 and 'tests/test_static_refs.py' in out, out[-600:])
    # 알려진 한계(fail-closed): web 기준 상대 경로 꼴(`_WEB_ROOT / "static/css/…"`)은 새 쪽에서 static 식별자 꼴과 글자가 같아
    # 가를 수 없다 — static 식별자로 읽어 exit 2(조용한 통과가 아니다). 이 꼴을 받게 고치면 이 단언을 뒤집는다.
    q = mkstd(tmp / 'x3')
    q.w('web/static/css/base.css', 'body { margin: 0; }', 'a { width: 1px; }')
    q.w('tests/test_web_relative.py', 'CSS: str = "static/css/base.css"')
    base = q.commit('base')
    q.mv('web/static/css/base.css', 'web/design_system/util/base.css')
    q.w('tests/test_web_relative.py', 'CSS: str = "design_system/util/base.css"')
    e, out = backstop(q.root, '--subst-check', base, q.commit('move'))
    check('X3 알려진 한계 — web 기준 상대 경로 꼴의 접두 횡단 치환은 못 받는다(exit 2 · fail-closed)',
          e == 2 and 'tests/test_web_relative.py' in out, 'exit=%d\n%s' % (e, out[-600:]))


# ====================================================================== H — 호스트 1단계 이관 재현(합성)

HOST_SHELL = '''{% load static %}
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>{% block title %}춘몽{% endblock title %}</title>
  <link rel="stylesheet" href="{% static 'design_system/foundation/tokens.css' %}">
  <link rel="stylesheet" href="{% static 'design_system/foundation/motion.css' %}">
  <link rel="stylesheet" href="{% static 'web/css/base.css' %}">
  <link rel="stylesheet" href="{% static 'web/css/app_shell.css' %}">
  <link rel="stylesheet" href="{% static 'web/css/components.css' %}">
  {% block styles %}{% endblock styles %}
</head>
<body>
  <div class="app-shell">
    <main class="app-frame__content">
      {% block content %}{% endblock content %}
    </main>
  </div>
  <script defer src="{% static 'web/htmx/htmx.min.js' %}"></script>
  <script defer src="{% static 'web/js/select_menu.js' %}"></script>
  {# 기능 UI JS — classic defer · 전역 idempotent #}
  <script defer src="{% static 'web/js/password_visibility.js' %}"></script>
  <script defer src="{% static 'web/js/submit_lock.js' %}"></script>
  {% block scripts %}{% endblock scripts %}
</body>
</html>
'''

HOST_TEST = '''from django.templatetags.static import static

BASE_CSS: str = "web/static/css/base.css"
MOTION_CSS: str = "web/design_system/foundation/motion.css"
SHELL: str = "web/base/base.html"
_INPUT_PAGE: str = """{% extends 'base/base.html' %}{% load static %}
{% block content %}<form></form>{% endblock %}"""


def test_login_stylesheets(stylesheets: list[str], storages: dict) -> None:
    assert stylesheets == [
        static("design_system/foundation/tokens.css"),
        static("design_system/foundation/motion.css"),
        static("web/css/base.css"),
        static("web/css/app_shell.css"),
        static("web/css/components.css"),
        static("web/css/login.css"),
    ]
    assert static("design_system/theme/app_theme.css") not in stylesheets
    assert not any(href.startswith(static("design_system/foundation/app_")) for href in stylesheets)
    assert storages["staticfiles"].url("web/css/base.css") == "/static/web/css/base.css"
'''

HOST_WEB_TEST = '''import pytest


@pytest.mark.parametrize("template", ["base/base.html", "root/scaffold/view/root_view.html"])
def test_shell_renders(template: str) -> None:
    assert template
'''


def bundle_host(tmp):
    p = mkstd(tmp / 'h')
    w = p.w
    mkbc(p, 'application/signup_flow')                       # 손님 BC — 운영자 셸을 고른 채(1단계에서는 그대로 둔다)
    signup = 'application/signup_flow/presentation_layer/view/signup_flow_view.html'
    p.sub('web/' + signup, '{% block content %}', '{% block styles %}\n' + link('design_system/foundation/tokens.css') + '\n'
          + link('design_system/foundation/motion.css') + '\n' + link('web/css/base.css') + '\n' + link('web/css/app_shell.css')
          + '\n' + link('design_system/component/button/primary_button.css') + '\n{% endblock styles %}\n{% block content %}')
    (p.root / 'web/base').mkdir()
    (p.root / 'web/base/base.html').write_text(HOST_SHELL, encoding='utf-8')
    w('web/static/css/base.css', '/* web 기반 스타일 — 리셋 · 웹폰트 로드 */',
      '@import url("https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&display=swap");',
      'body { margin: 0; font-family: "Pretendard Variable", sans-serif; color: #1a1a1a; }', 'a { color: inherit; }')
    w('web/static/css/app_shell.css', '.app-shell { width: 480px; }')
    w('web/static/css/components.css', '.btn { color: #fff; }')
    w('web/static/css/login.css', '.login { width: 1px; }')
    w('web/design_system/foundation/tokens.css', '@import "app_typography.css";', ':root { --chat-bg: #101010; }')
    w('web/design_system/foundation/motion.css', '/* 공용 모션 */', '@keyframes cm-rise {',
      '  from { opacity: 0; transform: translateY(10px); }', '  to { opacity: 1; transform: none; }', '}',
      '.cm-rise { animation: cm-rise var(--duration-fast) both; }')
    for name in ('select_menu', 'password_visibility', 'submit_lock'):
        w('web/static/js/%s.js' % name, 'document.addEventListener("htmx:afterSwap", () => {});')
    for rel in ('auth/login/view/login.html', 'home/home/view/home.html'):
        w('web/' + rel, '{% extends "base/base.html" %}', '{% load static %}', '{% block styles %}',
          link('web/css/login.css'), '{% endblock styles %}', '{% block content %}<form class="login"></form>{% endblock content %}')
    (p.root / 'tests/web').mkdir(parents=True)
    (p.root / 'tests/web/test_login_shell.py').write_text(HOST_TEST, encoding='utf-8')
    (p.root / 'web_test/root/handler').mkdir(parents=True)
    (p.root / 'web_test/root/handler/root_request_handler_test.py').write_text(HOST_WEB_TEST, encoding='utf-8')
    p.markers()
    host = p.commit('host')
    e, out, d0 = p.scan()
    k0 = d0.get('counts', {})
    old_keys = {'ST0|base/base.html', 'PU2|base/base.html', 'ST10|design_system/foundation/motion.css', 'ST12|static/css/base.css'}
    check('H0 호스트 꼴 — 옛 키 넷이 있다(PU2 는 실행 태그 넷)', old_keys <= set(k0) and k0.get('PU2|base/base.html') == 4, sorted(k0))

    # 초기 선언만 — 기존 키 감소 0
    p.declare({'operator': {'design_system': 'flat', 'bcs': ['order', 'admin/operator_teller']},
               'guest': {'design_system': 'own', 'bcs': '*'}})
    declared = p.commit('chore(web-products): declare')
    e, out, d1 = p.scan()
    k1 = d1.get('counts', {})
    check('H1 초기 선언만 더한 커밋 — 기존 키 감소 0(발견 수도)', bool(k0) and all(k1.get(k, 0) >= n for k, n in k0.items()),
          sorted(set(k0) - set(k1)))
    check('H1 선언만으로 보이는 새 키 — 손님 뿌리 · 셸 부재(ST4) · 잘못된 셸(IM26) · 혼입(IM13)',
          set(k1) - set(k0) == {'ST4|design_system/guest', 'ST4|' + GUEST_SHELL, 'IM26|' + signup, 'IM13|' + signup},
          sorted(set(k1) - set(k0)))

    # 1단계: 손님 골격(빈 7 파일 — 셸이 링크하지 않는다) + 세 파일 이동 + 참조 치환(링크 수 · 순서 그대로)
    for k in TOKENS:
        w('web/design_system/guest/foundation/app_%s.css' % k, '')
    (p.root / 'web/design_system/guest/component').mkdir(parents=True)
    (p.root / 'web/design_system/guest/component/.gitkeep').touch()
    p.mv('web/base/base.html', 'web/' + GUEST_SHELL)
    p.mv('web/static/css/base.css', 'web/design_system/guest/theme/app_theme.css')
    p.mv('web/design_system/foundation/motion.css', 'web/design_system/guest/util/motion.css')
    swaps = [('design_system/foundation/motion.css', 'design_system/guest/util/motion.css'),
             ('web/static/css/base.css', 'web/design_system/guest/theme/app_theme.css'),
             ('web/css/base.css', 'design_system/guest/theme/app_theme.css'),
             ('web/base/base.html', 'web/' + GUEST_SHELL), ('base/base.html', GUEST_SHELL)]
    for rel in ('web/' + GUEST_SHELL, 'web/' + signup, 'web/auth/login/view/login.html', 'web/home/home/view/home.html',
                'tests/web/test_login_shell.py', 'web_test/root/handler/root_request_handler_test.py'):
        text = p.read(rel)
        for old, new in swaps:
            text = text.replace(old, new)
        (p.root / rel).write_text(text, encoding='utf-8')
    moved = p.commit('refactor(web): 손님 셸 · theme · 모션을 제품 자리로')
    check('H2 픽스처 자체 — 시험 문자열 세 꼴이 치환됐다',
          'static("design_system/guest/theme/app_theme.css")' in p.read('tests/web/test_login_shell.py')
          and '"/static/design_system/guest/theme/app_theme.css"' in p.read('tests/web/test_login_shell.py')
          and '"web/design_system/guest/theme/app_theme.css"' in p.read('tests/web/test_login_shell.py')
          and "{% extends '" + GUEST_SHELL + "' %}" in p.read('tests/web/test_login_shell.py'))
    e, out, d2 = p.scan()
    k2 = d2.get('counts', {})
    check('H2 옛 키 넷이 사라진다', not (old_keys & set(k2)), sorted(old_keys & set(k2)))
    new_paths = (GUEST_SHELL, 'design_system/guest/')
    check('H2 옮긴 새 경로의 키 0', not [k for k in k2 if k.split('|', 1)[1].startswith(new_paths)],
          [k for k in k2 if k.split('|', 1)[1].startswith(new_paths)])
    check('H2 아직 안 옮긴 옛 값 파일의 키는 남는다(tokens.css · app_shell.css · components.css)',
          {'ST10|design_system/foundation/tokens.css', 'ST12|static/css/app_shell.css', 'ST12|static/css/components.css'} <= set(k2))
    e, out = backstop(p.root, '--diff-base', declared)
    check('H3 --diff-base(이동 전) 게이트 — exit 0', e == 0 and 'blocker 0건' in out, 'exit=%d\n%s' % (e, out[-1500:]))
    e, out = backstop(p.root, '--diff-base', declared, '--slice-end')
    check('H3 --slice-end — exit 0', e == 0 and 'blocker 0건' in out, 'exit=%d\n%s' % (e, out[-900:]))
    e, out = backstop(p.root, '--diff-base', host)
    check('H3 --diff-base(선언 전 — 선언 + 골격 + 이동 + 치환을 한 구간으로) — exit 0 · 선언 변경 [info]',
          e == 0 and 'blocker 0건' in out and '[info] 제품 선언이 기준점 뒤 바뀌었다' in out, 'exit=%d\n%s' % (e, out[-1500:]))
    for label, start in (('이동 전', declared), ('선언 전', host)):
        e, out = backstop(p.root, '--subst-check', start, moved)
        check('H4 --subst-check(%s 기준 — static(...) · /static/… · 저장소 경로 문자열 · 템플릿 이름) — exit 0' % label,
              e == 0 and '어긋남' not in out and 'web/ 밖 변경 파일 2' in out, 'exit=%d\n%s' % (e, out[-1500:]))
    folder = p.root / '.dddjango-web' / 'host-run'
    folder.mkdir(parents=True)
    (folder / 'debt-g0.json').write_text(json.dumps(d1), encoding='utf-8')
    ids = {key: cid for cid, key in d1['ids'].items()}
    (folder / 'refactor-scope.md').write_text('## G0 %s\n- ⓐ 키: %s\n- 요구 키: -\n' % (
        datetime.now().strftime('%Y-%m-%d %H:%M'), ' '.join(sorted(ids[k] for k in old_keys))), encoding='utf-8')
    e, out = backstop(p.root, '--debt-residual', folder)
    check('H5 --debt-residual — ⓐ 넷 잔존 0(판 경계 없음)', e == 0 and 'ⓐ 잔존 0 · 요구 잔존 0' in out and '판 경계' not in out, out[-900:])


def main():
    bundles = [bundle_unchanged, bundle_errors, bundle_places, bundle_shells, bundle_mixing, bundle_resolve,
               bundle_notices, bundle_first_registration, bundle_inflow, bundle_crossing, bundle_host]
    only = set(sys.argv[1:])
    for bundle in bundles:
        if only and bundle.__name__[len('bundle_'):] not in only:
            continue
        with tempfile.TemporaryDirectory(prefix='web230-') as tmp:
            try:
                bundle(Path(tmp))
            except Exception as error:  # noqa: BLE001 — 묶음이 죽어도 실패로 세고 다음 묶음을 돈다
                check('%s — 묶음 실행 오류' % bundle.__name__, False, '%s: %s' % (type(error).__name__, error))
    print('2.3.0 픽스처: PASS %d / FAIL %d' % (PASS, FAIL))
    return bool(FAIL)


if __name__ == '__main__':
    sys.exit(main())
