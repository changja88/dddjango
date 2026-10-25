"""2.8.2 IM5 «임베드 받는 페이지 머리의 자식 조각 CSS» 예외 회귀 — 임시 git 프로젝트만 쓰고 끝나면 지운다.

자리: 문서 셸을 글자로 extends 한 페이지가 셸 `<head>` 안 block 에서 `{% static %}` link 로, 그 페이지가 채널 ④ 로 실제로
임베드한 자식 view 가 그리는 템플릿의 짝 조각 CSS 를 실으면 IM5 가 아니다(증거 네 고리 — src/embed.py).
묶음: R 받음(2.8.1 IM5 → 이 판 0) · S 그대로(2.8.1 과 발견 경로:줄 같음 — 막음 · 받아들인 한계 · 못 읽어 막음 · 이 판 밖) ·
K 위반 줄 키 고정(I1 — 증거 파일만 다른 트리의 `위반:` 줄 글자 같음 · 부모 측정 판독) · H 교정 줄 셸 갈래(I2) ·
W 증거 파싱 경고가 stderr 로 새지 않음 · D 빚 지문 · M 검사기 변이(조건 하나를 빼면 그 장면이 뒤집힌다).
비교 판 = RELEASE_281 커밋의 scripts(`git archive` 로 임시 폴더에 푼다 — HEAD 에 묶지 않는다). 그 커밋이 이력에 없으면(얕은
clone 등) 2.8.1 대조만 건너뛰고 건너뛴 사실을 출력한다(실패로 세지 않는다). 이름은 모두 가짜다(부모 daily_note · 자식 gallery ·
손주 stamp)."""
import json
import os
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
sys.path.insert(0, str(SCRIPTS))
from fixtures_patch230 import ENV, Proj, git
from src.inflow import _read_findings

RELEASE_281 = 'cc664b6e11d2ce283a3172c5bfef219768cd3933'  # dddjango-web 2.8.1 배포 커밋 — «고치기 전 판» 의 고정 판
SHELL = 'web/root/scaffold/view/root_view.html'
PAGE = 'web/application/daily_note/presentation_layer/view/daily_note_view.html'
SEC = 'web/application/daily_note/presentation_layer/section/daily_note_screen_section.html'
VM = 'web/application/daily_note/application_layer/view_model/daily_note_vm.py'
SEC_CSS = 'web/static/application/daily_note/daily_note_screen_section.css'
G = 'web/application/gallery/'
CHILD = 'web/application/gallery/gallery_popular_view.css'  # {% static %} 인자(정적 뿌리 기준)
SLOT = 'hx-get="{{ state.popular_embed_href }}" hx-trigger="load" hx-swap="outerHTML"'
INCLUDE_SEC = ('{% include "application/daily_note/presentation_layer/section/daily_note_screen_section.html"'
               ' with state=state only %}')
GATE_ONLY = 'st,md,im,nm,tg,pj,pu,cs'  # 승인 유입 부모 측정과 같은 --only
PASS = FAIL = 0


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok and detail:
        print('    ' + str(detail).replace('\n', '\n    ')[:2400])


def run(scripts, root, *args):
    """backstop 실행 → (exit, stdout, stderr) — stderr 를 따로 본다(부모 측정은 stderr 를 실패로 읽는다)."""
    r = subprocess.run([sys.executable, '-B', str(scripts / 'backstop.py'), str(root), *map(str, args)],
                       capture_output=True, text=True, env=ENV)
    return r.returncode, r.stdout, r.stderr


def im5(out):
    """[(경로:줄, 위반 문장, 교정 줄)] — Finding 세 줄."""
    return re.findall(r'^\[IM5\] BLOCKER — (\S+)\n  위반: (.+)\n  교정: (.+)$', out, re.M)


def lines(out, path=PAGE):
    return sorted(int(n) for n in re.findall(r'^\[IM5\] BLOCKER — %s:(\d+)$' % re.escape(path), out, re.M))


def release_scripts(tmp):
    """RELEASE_281 커밋의 scripts 와 매니페스트를 `git archive` 로 임시 폴더에 푼다 → scripts 폴더(없으면 None)."""
    if subprocess.run(['git', '-C', str(REPO), 'cat-file', '-e', RELEASE_281 + '^{commit}'],
                      capture_output=True, env=ENV).returncode:
        return None
    tmp.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(['git', '-C', str(REPO), 'archive', RELEASE_281, 'dddjango-web/scripts',
                              'dddjango-web/.claude-plugin'], capture_output=True, env=ENV, check=True).stdout
    subprocess.run(['tar', '-xf', '-', '-C', str(tmp)], input=archive, check=True)
    return tmp / 'dddjango-web' / 'scripts'


# ====================================================================== 트리

def skeleton(p, rel):
    """골격 완비 BC(4계층 종류 폴더 · ruff.toml · 도메인 루트 모델)."""
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


def router(p, rel, app, cls, routes, imports):
    """`<bc>_router.py` — routes = [(상수, 이름, 경로, 함수)] · imports = import 줄들."""
    bc = rel.rsplit('/', 1)[-1]
    p.w('web/%s/%s_router.py' % (rel, bc), 'from django.urls import URLPattern, path', '', *imports, '',
        'app_name: str = "%s"' % app, '', '', 'class %s:' % cls,
        *['    %s: str = "%s:%s"' % (k, app, name) for k, name, _u, _f in routes], '', '',
        'urlpatterns: list[URLPattern] = [%s]' % ', '.join(
            'path("%s", %s, name="%s")' % (u, fn, name) for _k, name, u, fn in routes))


def navigator(p, rel, cls, routes_cls, methods):
    """`<bc>_navigator.py` — methods = [(메서드, 상수)] — 각 메서드가 reverse(<Routes>.<상수>)."""
    bc = rel.rsplit('/', 1)[-1]
    body = []
    for m, k in methods:
        body += ['    @staticmethod', '    def %s() -> str:' % m,
                 '        from web.%s.%s_router import %s' % (rel.replace('/', '.'), bc, routes_cls), '',
                 '        return reverse(%s.%s)' % (routes_cls, k), '']
    p.w('web/%s/%s_navigator.py' % (rel, bc), 'from django.urls import reverse', '', '', 'class %s:' % cls, *body[:-1])


def view_py(p, rel, screen, func, template, extra_imports=()):
    """`<화면>_view.py` — func 이 template(글자 상수)을 render 한다."""
    p.w('web/%s/presentation_layer/view/%s_view.py' % (rel, screen), 'from django.http import HttpRequest, HttpResponse',
        'from django.shortcuts import render', '', *extra_imports, '',
        '_TEMPLATE: str = "%s"' % template, '', '',
        'def %s(request: HttpRequest) -> HttpResponse:' % func, '    return render(request, _TEMPLATE, {})')


def link(asset, tail=''):
    return '<link rel="stylesheet" href="{% static \'' + asset + tail + '\' %}">'


def page(p, head=(link(CHILD),), body=(INCLUDE_SEC,), shell='root/scaffold/view/root_view.html', head_block='head',
         file=PAGE):
    """받는 페이지 — 1 extends · 2 load · 3 block head · 4… head 줄 · endblock · block content · body · endblock."""
    p.w(file, '{% extends "' + shell + '" %}', '{% load static %}', '{%% block %s %%}' % head_block,
        *['  ' + h for h in head], '  ' + link('web/application/daily_note/daily_note_view.css'),
        '{%% endblock %s %%}' % head_block, '{% block content %}', *['  ' + b for b in body], '{% endblock content %}')


def section(p, inner='<div class="daily-note-screen-section__popular" ' + SLOT + '></div>', file=SEC):
    p.w(file, '<div id="daily-note-screen" class="daily-note-screen-section">', '  ' + inner, '</div>')


def vm(p, value='GalleryNavigator.gallery_popular_embed_href()', pre=(), imports=None, tail=()):
    p.w(VM, 'from web.application.daily_note.application_layer.state.daily_note_state import DailyNoteState',
        *(['from web.application.gallery.gallery_navigator import GalleryNavigator'] if imports is None else imports), '', '',
        'class DailyNoteVM:', '    def build(self) -> DailyNoteState:', *['        ' + x for x in pre],
        '        return DailyNoteState(popular_embed_href=%s)' % value, *tail)


def base_tree(p, shell_body='<body>', head_block='head'):
    """root(문서 이동 셸 — `<head>` 안 block) + design_system + 자식 BC gallery(임베드되는 view 를 이미 가진 BC)."""
    w = p.w
    w('requirements.txt', 'Django==5.1.2', 'pytest==8.3.3', 'pytest-django==4.9.0')
    w('.dddjango-web/backstop-baseline.json', '{"cycle_pairs": []}')
    w('web/__init__.py', '')
    w('web/apps.py', 'from django.apps import AppConfig', '', '', 'class WebConfig(AppConfig):', '    name: str = "web"')
    w('web/urls.py', 'from web.root.router.root_router import urlpatterns', '', '__all__: list[str] = ["urlpatterns"]')
    w('web/root/ruff.toml', '[lint]', 'select = ["ANN"]')
    w('web/root/router/root_router.py', 'from django.urls import include, path', '',
      'from web.application.gallery import gallery_router', '',
      'urlpatterns: list[object] = [path("gallery/", include((gallery_router.urlpatterns, gallery_router.app_name)))]')
    w(SHELL, '{% load static %}', '<!doctype html>', '<html>', '<head>',
      "<link rel=\"stylesheet\" href=\"{% static 'design_system/theme/app_theme.css' %}\">",
      "<script src=\"{% static 'web/htmx/htmx.min.js' %}\" defer></script>",
      '{%% block %s %%}{%% endblock %s %%}' % (head_block, head_block), '</head>',
      shell_body + '{% block content %}{% endblock content %}</body>', '</html>')
    w('web/root/scaffold/view_model/root_vm.py', 'from web.root.scaffold.state.root_state import RootState', '', '',
      'class RootVM:', '    def build(self) -> RootState:', '        return RootState(title="t")')
    w('web/root/scaffold/state/root_state.py', 'from dataclasses import dataclass', '', '',
      '@dataclass(frozen=True, slots=True, kw_only=True)', 'class RootState:', '    title: str')
    for d in ('web/root/handler', 'web/root/initializer', 'web/design_system/component', 'web/design_system/util',
              'web/common/network', 'web/common/util', 'web/common/enum', 'web/common/service'):
        (p.root / d).mkdir(parents=True, exist_ok=True)
    for k in ('color', 'typography', 'spacing', 'radius', 'shadow', 'duration', 'asset'):
        w('web/design_system/foundation/app_%s.css' % k, ':root { --%s-base: 1px; }' % k)
    w('web/design_system/theme/app_theme.css', 'body { margin: 0; }')
    w('web/static/htmx/htmx.min.js', 'var htmx={version:"2.0.10"};')
    skeleton(p, 'application/gallery')
    router(p, 'application/gallery', 'gallery', 'GalleryRoutes',
           [('POPULAR_EMBED', 'popular_embed', 'popular/embed/', 'gallery_popular_embed_fragment')],
           ['from web.application.gallery.presentation_layer.view.gallery_popular_view import gallery_popular_embed_fragment'])
    navigator(p, 'application/gallery', 'GalleryNavigator', 'GalleryRoutes',
              [('gallery_popular_embed_href', 'POPULAR_EMBED')])
    w(G + 'application_layer/state/gallery_popular_state.py', 'from dataclasses import dataclass', '', '',
      '@dataclass(frozen=True, slots=True, kw_only=True)', 'class GalleryPopularState:', '    count: int')
    w(G + 'application_layer/view_model/gallery_popular_vm.py',
      'from web.application.gallery.application_layer.state.gallery_popular_state import GalleryPopularState', '', '',
      'class GalleryPopularVM:', '    def build(self) -> GalleryPopularState:', '        return GalleryPopularState(count=0)')
    view_py(p, 'application/gallery', 'gallery_popular', 'gallery_popular_embed_fragment',
            'application/gallery/presentation_layer/view/gallery_popular_view.html')
    w(G + 'presentation_layer/view/gallery_popular_view.html',
      '<div id="gallery-popular-view" class="gallery-popular-view">{{ state.count }}</div>')
    w('web/static/application/gallery/gallery_popular_view.css', '.gallery-popular-view { display: flex; }')
    w('web_test/application/gallery/application_layer/gallery_popular_vm_test.py', 'def test_x() -> None:', '    assert True')
    p.markers()


def parent_std(p):
    """부모 BC daily_note — 임베드 증거 있음 + 페이지 머리 link(4행) + section 안 자리(새 파일 — 전 줄 새 줄)."""
    skeleton(p, 'application/daily_note')
    p.w('web/application/daily_note/application_layer/state/daily_note_state.py', 'from dataclasses import dataclass', '', '',
        '@dataclass(frozen=True, slots=True, kw_only=True)', 'class DailyNoteState:', '    popular_embed_href: str')
    vm(p)
    p.w('web/application/daily_note/presentation_layer/view/daily_note_view.py',
        'from django.http import HttpRequest, HttpResponse', 'from django.shortcuts import render', '',
        'from web.application.daily_note.application_layer.view_model.daily_note_vm import DailyNoteVM', '',
        '_PAGE: str = "application/daily_note/presentation_layer/view/daily_note_view.html"', '', '',
        'def daily_note_view(request: HttpRequest) -> HttpResponse:',
        '    return render(request, _PAGE, {"state": DailyNoteVM().build()})')
    page(p)
    section(p)
    p.w('web/static/application/daily_note/daily_note_view.css', '.daily-note { display: block; }')
    p.w(SEC_CSS, '.daily-note-screen-section { display: block; }')
    p.w('web_test/application/daily_note/application_layer/daily_note_vm_test.py', 'def test_y() -> None:', '    assert True')
    p.markers()


def new_case(tmp, name, before_base=None):
    """바탕 커밋(+ before_base 가 바탕에 더하는 것) 뒤 부모를 새로 둔 프로젝트 → (Proj, 바탕 커밋)."""
    p = Proj(tmp / name)
    base_tree(p)
    if before_base:
        before_base(p)
    p.markers()
    git(p.root, 'init', '-q', '-b', 'main')
    base = p.commit('base')
    parent_std(p)
    return p, base


# ---- 장면 꼴(바탕 트리 위에 더하거나 바꾸는 것)

def child_routes_two(p):
    """자식 router 에 일반 라우트 하나 더(일반 이동 화면 함수 gallery_popular_page)."""
    router(p, 'application/gallery', 'gallery', 'GalleryRoutes',
           [('POPULAR_EMBED', 'popular_embed', 'popular/embed/', 'gallery_popular_embed_fragment'),
            ('POPULAR', 'popular', 'popular/', 'gallery_popular_page')],
           ['from web.application.gallery.presentation_layer.view.gallery_popular_view import '
            'gallery_popular_embed_fragment, gallery_popular_page'])
    p.append(G + 'presentation_layer/view/gallery_popular_view.py', '', '',
             'def gallery_popular_page(request: HttpRequest) -> HttpResponse:', '    return render(request, _TEMPLATE, {})')


def stamp_bc(p):
    """손주 BC stamp — 임베드 라우트가 section 을 그린다 · 자식 gallery view 가 손주를 임베드한다."""
    S = 'web/application/stamp/'
    skeleton(p, 'application/stamp')
    router(p, 'application/stamp', 'stamp', 'StampRoutes',
           [('CARD_EMBED', 'card_embed', 'card/embed/', 'stamp_card_embed_fragment')],
           ['from web.application.stamp.presentation_layer.view.stamp_card_view import stamp_card_embed_fragment'])
    navigator(p, 'application/stamp', 'StampNavigator', 'StampRoutes', [('stamp_card_embed_href', 'CARD_EMBED')])
    view_py(p, 'application/stamp', 'stamp_card', 'stamp_card_embed_fragment',
            'application/stamp/presentation_layer/section/stamp_card_body_section.html')
    p.w(S + 'presentation_layer/section/stamp_card_body_section.html', '<div class="stamp-card-body-section"></div>')
    p.w(S + 'presentation_layer/view/stamp_card_view.html', '<div class="stamp-card-view"></div>')
    p.w('web/static/application/stamp/stamp_card_body_section.css', '.stamp-card-body-section { display: block; }')
    p.w('web/static/application/stamp/stamp_card_view.css', '.stamp-card-view { display: block; }')
    p.w('web_test/application/stamp/application_layer/stamp_vm_test.py', 'def test_s() -> None:', '    assert True')
    p.w(G + 'application_layer/state/gallery_popular_state.py', 'from dataclasses import dataclass', '', '',
        '@dataclass(frozen=True, slots=True, kw_only=True)', 'class GalleryPopularState:', '    stamp_embed_href: str')
    p.w(G + 'application_layer/view_model/gallery_popular_vm.py',
        'from web.application.gallery.application_layer.state.gallery_popular_state import GalleryPopularState',
        'from web.application.stamp.stamp_navigator import StampNavigator', '', '',
        'class GalleryPopularVM:', '    def build(self) -> GalleryPopularState:',
        '        return GalleryPopularState(stamp_embed_href=StampNavigator.stamp_card_embed_href())')
    p.w(G + 'presentation_layer/view/gallery_popular_view.html',
        '<div id="gallery-popular-view" class="gallery-popular-view">',
        '  <div class="gallery-popular-view__stamp" hx-get="{{ state.stamp_embed_href }}" hx-trigger="load"></div>', '</div>')


def gallery_main(p):
    """자식 BC 에 임베드하지 않는 화면 하나(gallery_main_view — 문서 셸 페이지 · 짝 CSS)."""
    p.w(G + 'presentation_layer/view/gallery_main_view.html', '{% extends "root/scaffold/view/root_view.html" %}',
        '{% block content %}<div class="gallery-main-view"></div>{% endblock content %}')
    p.w('web/static/application/gallery/gallery_main_view.css', '.gallery-main-view { display: block; }')


def declare(p, products, guest_shell=False, guest_body='<body>'):
    p.w('web/product_registry.json', '{"schema": "dddjango-web-products/1", "products": %s}' % products)
    if guest_shell:
        text = p.read(SHELL).replace('<body>', guest_body)
        p.w('web/root/scaffold/view/root_guest_view.html', *text.rstrip('\n').split('\n'))
        for d in ('foundation', 'component', 'util'):
            (p.root / 'web/design_system/guest' / d).mkdir(parents=True, exist_ok=True)
        p.w('web/design_system/guest/theme/app_theme.css', 'body { margin: 0; }')


TWO_PRODUCTS = ('{"main": {"design_system": "flat", "bcs": ["gallery", "stamp"]}, '
                '"guest": {"design_system": "own", "bcs": ["daily_note"]}}')


# ====================================================================== 판정 도우미

class Judge:
    def __init__(self, tmp):
        self.old = release_scripts(tmp / 'rel281')
        if self.old is None:
            print('SKIP 2.8.1 대조 — 커밋 %s 가 이 저장소 이력에 없다(얕은 clone 등) — 2.8.1 대조만 건너뛴다(실패로 세지 않는다)'
                  % RELEASE_281[:8])

    def both(self, p, base, *args, only=('--only', 'im')):
        new = run(SCRIPTS, p.root, '--diff-base', base, *only, *args)
        old = run(self.old, p.root, '--diff-base', base, *only, *args) if self.old else None
        return new, old

    def received(self, name, p, base, old_lines=(4,), path=PAGE):
        """R — 이 판 IM5 0(exit 0 · stderr 없음) · 2.8.1 은 그 줄에 IM5."""
        new, old = self.both(p, base)
        check('R %s — 이 판 IM5 0' % name, new[0] == 0 and not im5(new[1]) and not new[2], new)
        if old is not None:
            check('R %s — 2.8.1 은 IM5 %s' % (name, list(old_lines)), lines(old[1], path) == list(old_lines), old)
        return new

    def same(self, name, p, base, want, path=PAGE):
        """S — 이 판 IM5 는 그 파일의 want(줄 목록)뿐이고, 그 파일의 IM5 줄이 2.8.1 과 같다(다른 파일의 받음은 R 몫)."""
        new, old = self.both(p, base)
        got = lines(new[1], path)
        check('S %s — 이 판 IM5 %s' % (name, want), got == list(want) and not new[2]
              and len(im5(new[1])) == len(want), new)
        if old is not None:
            check('S %s — 2.8.1 과 그 파일의 IM5 줄 같음' % name, lines(old[1], path) == got, (new[1], old[1]))
        return new


# ====================================================================== R — 받음

def bundle_r(tmp, j):
    p, base = new_case(tmp, 'r1')
    new = j.received('R1 장면 A(증거 있음 · 머리 link)', p, base)
    for flags, label in ((('--slice-end',), '--slice-end'), ((), '게이트 전체')):
        got = run(SCRIPTS, p.root, '--diff-base', base, *flags)
        check('R1 %s — blocker 0' % label, got[0] == 0 and 'blocker 0건' in got[1] and not got[2], got)

    p, base = new_case(tmp, 'r6')
    page(p, head=(link(CHILD, '?v=1'),))
    j.received('R6 `?v=` 꼬리 + 증거(허용 대조는 꼬리 뗀 실제 파일)', p, base)

    p, base = new_case(tmp, 'r6b')
    page(p, head=(link('/' + CHILD),))
    j.received('R6b static 인자 앞머리 `/` + 증거', p, base)

    p, base = new_case(tmp, 'r7')
    p.sub(G + 'presentation_layer/view/gallery_popular_view.py', 'def gallery_popular_embed_fragment',
          'async def gallery_popular_embed_fragment')
    j.received('R7 async 임베드 함수', p, base)

    p, base = new_case(tmp, 'r8')
    p.w(G + 'presentation_layer/section/gallery_popular_list_section.html',
        '<section id="gallery-popular-list" class="gallery-popular-list-section"></section>')
    p.w('web/static/application/gallery/gallery_popular_list_section.css', '.gallery-popular-list-section { display: block; }')
    p.sub(G + 'presentation_layer/view/gallery_popular_view.py', 'presentation_layer/view/gallery_popular_view.html',
          'presentation_layer/section/gallery_popular_list_section.html')
    page(p, head=(link('web/application/gallery/gallery_popular_list_section.css'),))
    j.received('R8 규칙 예 꼴(임베드가 section 을 render · section CSS)', p, base)

    p, base = new_case(tmp, 'r9')
    section(p, '<div ' + SLOT.replace('state.popular_embed_href', 'state.embed.popular_embed_href') + '></div>')
    j.received('R9 중첩 칸(state.embed.popular_embed_href — 끝 마디)', p, base)

    p, base = new_case(tmp, 'r10a', lambda q: declare(q, '{"app": {"design_system": "flat", "bcs": "*"}}'))
    j.received('R10a 제품 선언 한 제품', p, base)
    p, base = new_case(tmp, 'r10b', lambda q: declare(q, TWO_PRODUCTS, guest_shell=True))
    page(p, shell='root/scaffold/view/root_guest_view.html')
    j.received('R10b 두 제품 · 다른 제품 BC 임베드(제품을 넘어도 같다)', p, base)

    p, base = new_case(tmp, 'r11', lambda q: base_tree(q, head_block='extra_head'))
    page(p, head_block='extra_head')
    j.received('R11 셸 머리 block 이름이 head 가 아니다(extra_head)', p, base)

    p, base = new_case(tmp, 'r4', stamp_bc)
    page(p, head=(link(CHILD), link('web/application/stamp/stamp_card_body_section.css')))
    j.received('R4 손주(자식 view 가 임베드한 BC 의 렌더 CSS)', p, base, old_lines=(4, 5))

    p, base = new_case(tmp, 'r3w', lambda q: (q.w(G + 'presentation_layer/widget/gallery_card_widget.html', '<i class="gallery-card-widget"></i>'),
                                               q.w(G + 'presentation_layer/view/gallery_popular_view.html',
                                                   '<div class="gallery-popular-view">{% include "application/gallery/presentation_layer/widget/gallery_card_widget.html" only %}</div>'),
                                               q.w('web/static/application/gallery/gallery_card_widget.css', '.gallery-card-widget { display: block; }')))
    page(p, head=(link(CHILD), link('web/application/gallery/gallery_card_widget.css')))
    j.received('R3 자식 렌더 닫힘의 widget CSS', p, base, old_lines=(4, 5))

    p, base = new_case(tmp, 'r5', relay_tree)
    vm(p, value='DailyNoteNavigator.daily_note_side_embed_href()',
       imports=['from web.application.daily_note.daily_note_navigator import DailyNoteNavigator'])
    j.received('R5 같은 BC view 를 거친 다른 BC 임베드', p, base)

    bundle_field(tmp, j)


def relay_tree(p):
    """부모 BC 가 자기 BC view(daily_note_side)를 임베드하고 그 view 가 gallery 를 임베드한다 — 바탕에 둔다."""
    D = 'web/application/daily_note/'
    skeleton(p, 'application/daily_note')
    router(p, 'application/daily_note', 'daily_note', 'DailyNoteRoutes',
           [('SIDE_EMBED', 'side_embed', 'side/embed/', 'daily_note_side_embed_fragment')],
           ['from web.application.daily_note.presentation_layer.view.daily_note_side_view import daily_note_side_embed_fragment'])
    navigator(p, 'application/daily_note', 'DailyNoteNavigator', 'DailyNoteRoutes',
              [('daily_note_side_embed_href', 'SIDE_EMBED')])
    view_py(p, 'application/daily_note', 'daily_note_side', 'daily_note_side_embed_fragment',
            'application/daily_note/presentation_layer/view/daily_note_side_view.html')
    p.w(D + 'presentation_layer/view/daily_note_side_view.html',
        '<div class="daily-note-side-view"><div hx-get="{{ state.gallery_embed_href }}" hx-trigger="load"></div></div>')
    p.w(D + 'application_layer/state/daily_note_side_state.py', 'from dataclasses import dataclass', '', '',
        '@dataclass(frozen=True, slots=True, kw_only=True)', 'class DailyNoteSideState:', '    gallery_embed_href: str')
    p.w(D + 'application_layer/view_model/daily_note_side_vm.py',
        'from web.application.daily_note.application_layer.state.daily_note_side_state import DailyNoteSideState',
        'from web.application.gallery.gallery_navigator import GalleryNavigator', '', '',
        'class DailyNoteSideVM:', '    def build(self) -> DailyNoteSideState:',
        '        return DailyNoteSideState(gallery_embed_href=GalleryNavigator.gallery_popular_embed_href())')
    p.w('web/static/application/daily_note/daily_note_side_view.css', '.daily-note-side-view { display: block; }')


def bundle_field(tmp, j):
    """R2 현장 꼴 — area 아래 부모 BC(개념 1차) · 개념 1차 자식 · navigator 이름 ≠ 화면 · 도우미로 넘기는 키워드 ·
    include 두 단 아래 `{% elif %}` 안 자리 · 자식 렌더 닫힘 section · widget(template 안) · 손주 임베드."""
    p = Proj(tmp / 'field')
    base_tree(p)
    W = 'web/'
    C = W + 'application/gallery/'
    for f in ('presentation_layer/view/gallery_popular_view.py', 'presentation_layer/view/gallery_popular_view.html',
              'application_layer/view_model/gallery_popular_vm.py', 'application_layer/state/gallery_popular_state.py'):
        p.rm(C + f)
    p.rm(W + 'static/application/gallery/gallery_popular_view.css')
    router(p, 'application/gallery', 'gallery', 'GalleryRoutes',
           [('MAIN', 'main', 'gallery/', 'gallery_main_view'), ('POPULAR', 'popular', 'gallery/popular/', 'gallery_popular_embed_fragment')],
           ['from web.application.gallery.presentation_layer.pick.view.gallery_main_view import gallery_main_view',
            'from web.application.gallery.presentation_layer.pick.view.gallery_popular_view import (',
            '    gallery_popular_embed_fragment,', ')'])
    p.w(C + 'gallery_navigator.py', 'from urllib.parse import urlencode', '', 'from django.urls import reverse', '', '',
        'class GalleryNavigator:', '    @staticmethod', '    def main_href() -> str:',
        '        from web.application.gallery.gallery_router import GalleryRoutes', '', '        return reverse(GalleryRoutes.MAIN)', '',
        '    @staticmethod', '    def popular_embed_href(page: str = "") -> str:',
        '        from web.application.gallery.gallery_router import GalleryRoutes', '',
        '        href: str = reverse(GalleryRoutes.POPULAR)', '        query: dict[str, str] = {"page": page}',
        '        return f"{href}?{urlencode(query)}" if page else href')
    p.w(C + 'application_layer/pick/state/gallery_popular_state.py', 'from dataclasses import dataclass', '', '',
        '@dataclass(frozen=True, slots=True, kw_only=True)', 'class GalleryPopularState:', '    stamp_embed_href: str')
    p.w(C + 'application_layer/pick/view_model/gallery_popular_vm.py',
        'from web.application.gallery.application_layer.pick.state.gallery_popular_state import GalleryPopularState',
        'from web.application.stamp.stamp_navigator import StampNavigator', '', '',
        'class GalleryPopularVM:', '    def build(self) -> GalleryPopularState:',
        '        return GalleryPopularState(stamp_embed_href=StampNavigator.stamp_card_embed_href())')
    p.w(C + 'presentation_layer/pick/view/gallery_popular_view.py', 'from django.http import HttpRequest, HttpResponse',
        'from django.shortcuts import render', '',
        'from web.application.gallery.application_layer.pick.view_model.gallery_popular_vm import GalleryPopularVM', '',
        '_TEMPLATE: str = "application/gallery/presentation_layer/pick/view/gallery_popular_view.html"', '', '',
        'def gallery_popular_embed_fragment(request: HttpRequest) -> HttpResponse:',
        '    return render(request, _TEMPLATE, {"state": GalleryPopularVM().build()})')
    p.w(C + 'presentation_layer/pick/view/gallery_popular_view.html', '<div id="gallery-popular-view" class="gallery-popular-view">',
        '  {% include "application/gallery/presentation_layer/pick/section/gallery_popular_strip_section.html" with state=state only %}',
        '  <template>{% include "application/gallery/presentation_layer/pick/widget/reader_failure_widget.html" only %}</template>',
        '  <div class="gallery-popular-view__stamp" hx-get="{{ state.stamp_embed_href }}" hx-trigger="load" hx-swap="outerHTML"></div>',
        '</div>')
    p.w(C + 'presentation_layer/pick/section/gallery_popular_strip_section.html', '<ul class="gallery-popular-strip-section"></ul>')
    p.w(C + 'presentation_layer/pick/widget/reader_failure_widget.html', '<p class="reader-failure-widget">x</p>')
    p.w(C + 'presentation_layer/pick/view/gallery_main_view.py', 'from django.http import HttpRequest, HttpResponse',
        'from django.shortcuts import render', '', '', 'def gallery_main_view(request: HttpRequest) -> HttpResponse:',
        '    return render(request, "application/gallery/presentation_layer/pick/view/gallery_main_view.html", {})')
    p.w(C + 'presentation_layer/pick/view/gallery_main_view.html', '{% extends "root/scaffold/view/root_view.html" %}',
        '{% block content %}<div class="gallery-main-view"></div>{% endblock content %}')
    for s in ('gallery_popular_view', 'gallery_popular_strip_section', 'reader_failure_widget', 'gallery_main_view'):
        p.w(W + 'static/application/gallery/%s.css' % s, '.%s { display: block; }' % s.replace('_', '-'))
    stamp_bc(p)
    for f in ('application_layer/view_model/gallery_popular_vm.py', 'application_layer/state/gallery_popular_state.py',
              'presentation_layer/view/gallery_popular_view.html'):
        p.rm(C + f)  # stamp_bc 가 평면 자리에 쓴 자식 파일 — 이 장면은 개념 1차(pick) 자리만 쓴다
    p.markers()
    git(p.root, 'init', '-q', '-b', 'main')
    base = p.commit('base')
    A = W + 'application/visitor/daily_note/'
    skeleton(p, 'application/visitor/daily_note')
    p.w(A + 'application_layer/note/state/daily_note_state.py', 'from dataclasses import dataclass', '', '',
        '@dataclass(frozen=True, slots=True, kw_only=True)', 'class DailyNoteState:', '    status: str', '    popular_embed_href: str')
    p.w(A + 'application_layer/note/view_model/daily_note_vm.py',
        'from web.application.visitor.daily_note.application_layer.note.state.daily_note_state import DailyNoteState',
        'from web.application.gallery.gallery_navigator import GalleryNavigator', '', '',
        'class DailyNoteVM:', '    def build(self, popular_page: str) -> DailyNoteState:',
        '        return self._opened(popular_embed_href=GalleryNavigator.popular_embed_href(page=popular_page))', '',
        '    def _opened(self, *, popular_embed_href: str) -> DailyNoteState:',
        '        return DailyNoteState(status="opened", popular_embed_href=popular_embed_href)')
    V = A + 'presentation_layer/note/'
    p.w(V + 'view/daily_note_view.py', 'from django.http import HttpRequest, HttpResponse', 'from django.shortcuts import render', '',
        'from web.application.visitor.daily_note.application_layer.note.view_model.daily_note_vm import DailyNoteVM', '',
        '_TEMPLATE: str = "application/visitor/daily_note/presentation_layer/note/view/daily_note_view.html"', '', '',
        'def daily_note_view(request: HttpRequest) -> HttpResponse:',
        '    return render(request, _TEMPLATE, {"state": DailyNoteVM().build(popular_page="")})')
    fpage = V + 'view/daily_note_view.html'
    p.w(fpage, '{% extends "root/scaffold/view/root_view.html" %}', '{% load static %}', '', '{% block head %}',
        '  ' + link('web/application/gallery/gallery_popular_view.css'),            # 5 자식 view
        '  ' + link('web/application/gallery/gallery_popular_strip_section.css'),   # 6 자식 section
        '  ' + link('web/application/gallery/reader_failure_widget.css'),           # 7 자식 widget(template 안)
        '  ' + link('web/application/stamp/stamp_card_body_section.css'),           # 8 손주 렌더 CSS
        '  ' + link('web/application/stamp/stamp_card_view.css'),                   # 9 손주 임베드가 그리지 않는 view
        '  ' + link('web/application/gallery/gallery_main_view.css'),               # 10 임베드하지 않은 화면
        '  ' + link('web/application/visitor/daily_note/daily_note_view.css'),
        '{% endblock head %}', '', '{% block content %}',
        '  ' + link('web/application/gallery/gallery_popular_view.css'),            # 15 본문 link
        '  {% include "application/visitor/daily_note/presentation_layer/note/section/daily_note_frame_section.html" with state=state only %}',
        '{% endblock content %}')
    p.w(V + 'section/daily_note_frame_section.html', '<div class="daily-note-frame-section">',
        '  {% include "application/visitor/daily_note/presentation_layer/note/section/daily_note_screen_section.html" with state=state only %}',
        '</div>')
    p.w(V + 'section/daily_note_screen_section.html', '<div id="daily-note-screen" class="daily-note-screen-section">',
        '  {% if state.status == "before_open" %}<p>gate</p>', '  {% elif state.status == "opened" %}',
        '    <div class="daily-note-screen-section__popular" ' + SLOT + '></div>', '  {% endif %}', '</div>')
    for s in ('daily_note_view', 'daily_note_frame_section', 'daily_note_screen_section'):
        p.w(W + 'static/application/visitor/daily_note/%s.css' % s, '.%s { display: block; }' % s.replace('_', '-'))
    p.w('web_test/application/visitor/daily_note/application_layer/daily_note_vm_test.py', 'def test_y() -> None:', '    assert True')
    p.markers()
    fpage = fpage[len('web/'):]
    new, old = j.both(p, base)
    check('R2 현장 꼴 — 머리 6 + 본문 1 가운데 이 판 IM5 = 9 · 10 · 15(자식 view · section · widget · 손주 렌더 CSS 허용)',
          lines(new[1], 'web/' + fpage) == [9, 10, 15] and not new[2], new)
    if old is not None:
        check('R2 현장 꼴 — 2.8.1 은 5 ~ 10 · 15 모두 IM5', lines(old[1], 'web/' + fpage) == [5, 6, 7, 8, 9, 10, 15], old)
    return p, base


# ====================================================================== S — 그대로(2.8.1 과 같은 발견)

def bundle_s(tmp, j):
    p, base = new_case(tmp, 'b')
    vm(p, value='""')
    j.same('B 증거 없음(VM 이 빈 글)', p, base, [4])

    p, base = new_case(tmp, 's2')
    vm(p, value='href', pre=('href: str = GalleryNavigator.gallery_popular_embed_href()',))
    j.same('S2 다른 이름 지역 변수 경유', p, base, [4])

    p, base = new_case(tmp, 's3', child_routes_two)
    p.sub(G + 'gallery_router.py', 'gallery_popular_embed_fragment, name="popular_embed"', 'gallery_popular_page, name="popular_embed"')
    j.same('S3 그 라우트가 일반 이동 화면 함수', p, base, [4])

    p, base = new_case(tmp, 's4', gallery_main)
    page(p, head=(link('web/application/gallery/gallery_main_view.css'),))
    j.same('S4 렌더 닫힘 밖 CSS(임베드하지 않은 화면)', p, base, [4])

    p, base = new_case(tmp, 's5')
    page(p, head=(), body=(link(CHILD), INCLUDE_SEC))
    j.same('S5 본문 link', p, base, [7])

    p, base = new_case(tmp, 's6')
    p.w(SEC_CSS, '@import url("/static/web/application/gallery/gallery_popular_view.css");', '.daily-note-screen-section { display: block; }')
    j.same('S6 조각 CSS 의 @import', p, base, [1], path=SEC_CSS)

    p, base = new_case(tmp, 's7')
    p.w(SEC, '{% load static %}', link(CHILD), '<div class="daily-note-screen-section"><div ' + SLOT + '></div></div>')
    j.same('S7 section 템플릿 link', p, base, [2], path=SEC)

    p, base = new_case(tmp, 'fa2')
    section(p, '')
    p.append(PAGE, '<div ' + SLOT + '></div>')
    j.same('FA2 자리가 extends 페이지의 block 밖(Django 가 버림)', p, base, [4])

    p, base = new_case(tmp, 'fa3')
    section(p, '')
    p.append(PAGE, '{% block nowhere %}<div ' + SLOT + '></div>{% endblock nowhere %}')
    j.same('FA3 자리가 셸에 없는 block 안', p, base, [4])

    p, base = new_case(tmp, 'fa4')
    section(p, '{% verbatim %}<div ' + SLOT + '></div>{% endverbatim %}')
    j.same('FA4 자리가 verbatim 안', p, base, [4])

    p, base = new_case(tmp, 'fa5')
    section(p, '<div data-x-hx-get="{{ state.popular_embed_href }}"></div>')
    j.same('FA5 htmx 가 읽지 않는 속성 이름(data-x-hx-get)', p, base, [4])

    p, base = new_case(tmp, 'fa5b')
    section(p, '<code>hx-get="{{ state.popular_embed_href }}"</code>')
    j.same('FA5b 글자 본문의 hx-get', p, base, [4])

    p, base = new_case(tmp, 'fa7', child_routes_two)
    p.w(G + 'gallery_navigator.py', 'from django.urls import reverse', '', '',
        'class _Old:', '    @staticmethod', '    def gallery_popular_embed_href() -> str:',
        '        from web.application.gallery.gallery_router import GalleryRoutes', '',
        '        return reverse(GalleryRoutes.POPULAR_EMBED)', '', '',
        'class GalleryNavigator:', '    @staticmethod', '    def gallery_popular_embed_href() -> str:',
        '        from web.application.gallery.gallery_router import GalleryRoutes', '',
        '        return reverse(GalleryRoutes.POPULAR)')
    j.same('FA7 navigator 두 클래스(들여온 클래스는 일반 라우트)', p, base, [4])

    p, base = new_case(tmp, 'fa7b', child_routes_two)
    p.w(G + 'gallery_navigator.py', 'from django.urls import reverse', '', '',
        'class GalleryNavigator:', '    @staticmethod', '    def gallery_popular_embed_href() -> str:',
        '        from web.application.gallery.gallery_router import GalleryRoutes', '',
        '        _unused: str = GalleryRoutes.POPULAR_EMBED', '        return reverse(GalleryRoutes.POPULAR)')
    j.same('FA7b 임베드 상수는 읽기만 · reverse 는 일반 라우트', p, base, [4])

    p, base = new_case(tmp, 'fa8')
    p.w(PAGE, '{% load static %}', '{% block head %}' + link(CHILD) + '{% endblock head %}', INCLUDE_SEC)
    j.same('FA8 extends 없는 view(조각)의 block head link', p, base, [2])

    p, base = new_case(tmp, 'fa9')
    p.w(G + 'presentation_layer/view/gallery_popular_page.html',
        '{% extends "root/scaffold/view/root_view.html" %}{% block content %}x{% endblock content %}')
    p.w(G + 'gallery_router.py', 'from django.urls import URLPattern, path', '',
        'from web.application.gallery.presentation_layer.view.gallery_popular_view import gallery_popular_page as gallery_popular_embed_fragment',
        '', 'app_name: str = "gallery"', '', '', 'class GalleryRoutes:', '    POPULAR_EMBED: str = "gallery:popular_embed"', '', '',
        'urlpatterns: list[URLPattern] = [path("popular/embed/", gallery_popular_embed_fragment, name="popular_embed")]')
    p.append(G + 'presentation_layer/view/gallery_popular_view.py', '', '',
             'def gallery_popular_page(request: HttpRequest) -> HttpResponse:',
             '    return render(request, "application/gallery/presentation_layer/view/gallery_popular_page.html", {})')
    j.same('FA9 router 별칭(실제 라우트 함수는 다른 함수)', p, base, [4])

    p, base = new_case(tmp, 'fb2')
    page(p, body=(INCLUDE_SEC.replace('with state=state only', 'with embed_href=state.popular_embed_href only'),))
    section(p, '<div hx-get="{{ embed_href }}" hx-trigger="load"></div>')
    j.same('FB2 include with 로 이름을 바꿔 넘긴 자리(못 읽는 꼴)', p, base, [4])

    p, base = new_case(tmp, 'fb4')
    vm(p, value='gallery_navigator.GalleryNavigator.gallery_popular_embed_href()',
       imports=['from web.application.gallery import gallery_navigator'])
    j.same('FB4 navigator 모듈째 import(못 읽는 꼴)', p, base, [4])

    p, base = new_case(tmp, 'lk1')
    outside = tmp / 'outside-lk1'
    outside.mkdir()
    shutil.copy(p.root / VM, outside / 'vm.py')
    (p.root / VM).unlink()
    os.symlink(outside / 'vm.py', p.root / VM)
    j.same('LK1 짝 VM 이 web 밖 파일 링크', p, base, [4])

    p, base = new_case(tmp, 'lk2')
    outside = tmp / 'outside-lk2'
    outside.mkdir()
    shutil.copy(p.root / SEC, outside / 'section.html')
    (p.root / SEC).unlink()
    os.symlink(outside / 'section.html', p.root / SEC)
    j.same('LK2 자리 든 section 템플릿이 web 밖 파일 링크', p, base, [4])

    for name, content, tail in (('N1 자리 든 section 을 셸에 없는 block 안에서 include', '', '{% block nowhere %}' + INCLUDE_SEC + '{% endblock nowhere %}'),
                                ('N2 자리 든 section 을 block 밖에서 include', '', INCLUDE_SEC),
                                ('N3 자리 든 section 을 verbatim 안에서 include', '{% verbatim %}' + INCLUDE_SEC + '{% endverbatim %}', '')):
        p, base = new_case(tmp, name[:2].lower())
        page(p, body=(content,))
        if tail:
            p.append(PAGE, tail)
        j.same(name, p, base, [4])

    p, base = new_case(tmp, 'n6')
    section(p, '<textarea><div ' + SLOT + '></div></textarea>')
    j.same('N6 textarea 글자 안 자리', p, base, [4])

    p, base = new_case(tmp, 'n7')
    section(p, "<div class=\"x\" hx-vals='{\"hx-get\": \"{{ state.popular_embed_href }}\"}'></div>")
    j.same('N7 다른 속성 값 안의 hx-get 글자', p, base, [4])

    # 받아들인 한계 — 이 판은 받는다(2.8.1 은 IM5): 정적 거짓 가지 · VM 의 부르지 않는 함수 · 같은 이름 클래스 두 번 ·
    # 버린 reverse 뒤 다른 값 반환
    p, base = new_case(tmp, 'fa1')
    section(p, '{% if False %}<div ' + SLOT + '></div>{% endif %}')
    j.received('한계 FA1 `{% if False %}` 안 자리', p, base)
    p, base = new_case(tmp, 'fa6')
    vm(p, value='""', tail=('', '    def _never(self) -> dict[str, str]:',
                            '        return dict(popular_embed_href=GalleryNavigator.gallery_popular_embed_href())'))
    j.received('한계 FA6 VM 의 부르지 않는 함수 키워드', p, base)
    p, base = new_case(tmp, 'n4', child_routes_two)
    p.w(G + 'gallery_navigator.py', 'from django.urls import reverse', '', '',
        'class GalleryNavigator:', '    @staticmethod', '    def gallery_popular_embed_href() -> str:',
        '        from web.application.gallery.gallery_router import GalleryRoutes', '', '        return reverse(GalleryRoutes.POPULAR_EMBED)', '', '',
        'class GalleryNavigator:  # noqa: F811', '    @staticmethod', '    def gallery_popular_embed_href() -> str:',
        '        from web.application.gallery.gallery_router import GalleryRoutes', '', '        return reverse(GalleryRoutes.POPULAR)')
    j.received('한계 N4 navigator 같은 이름 클래스 두 번(앞 것을 읽는다)', p, base)
    p, base = new_case(tmp, 'n5')
    p.w(G + 'gallery_navigator.py', 'from django.urls import reverse', '', '',
        'class GalleryNavigator:', '    @staticmethod', '    def main_href() -> str:', '        return "/"', '',
        '    @staticmethod', '    def gallery_popular_embed_href() -> str:',
        '        from web.application.gallery.gallery_router import GalleryRoutes', '',
        '        _unused: str = reverse(GalleryRoutes.POPULAR_EMBED)', '        return GalleryNavigator.main_href()')
    j.received('한계 N5 버린 reverse 뒤 다른 값 반환', p, base)

    # 이 판 밖(둘 다 0 — 기존 구멍을 이 판에서 붉히지 않는다) · 증거를 지운 커밋의 옛 link 줄
    p, base = new_case(tmp, 'fa11')
    vm(p, value='""')
    page(p, head=(link('web/application/daily_note/../gallery/gallery_popular_view.css'),))
    j.same('FA11 `..` 로 돌린 다른 BC CSS(이 판 밖 — 둘 다 0)', p, base, [])

    p, base = new_case(tmp, 'pre1')
    vm(p, value='""')
    p.w('web/static/application/gallery/view/gallery_x.css', '.x { display: block; }')
    page(p, head=(link('web/application/gallery/view/gallery_x.css'),))
    j.same('PRE1 static/application/<bc>/view/ 아래 CSS(이 판 밖 — 둘 다 0)', p, base, [])

    p, base = new_case(tmp, 'gone')
    base2 = p.commit('evidence')
    vm(p, value='""')
    j.same('증거를 지운 커밋 — 옛 link 줄은 새 줄이 아니다(둘 다 0)', p, base2, [])
    got = run(SCRIPTS, p.root, '--diff-base', base, '--only', 'im')
    check('증거를 지운 트리를 처음부터 보면 IM5(그 줄이 새 줄)', lines(got[1]) == [4], got)


# ====================================================================== K — 위반 줄 키 고정(I1 · I4)

def key_trees(tmp):
    trees = []
    p, base = new_case(tmp, 'k_a')
    section(p, '')
    trees.append(('자리 없음', p, base))
    p, base = new_case(tmp, 'k_b')
    vm(p, value='href', pre=('href: str = GalleryNavigator.gallery_popular_embed_href()',))
    trees.append(('지역 이름 경유', p, base))
    p, base = new_case(tmp, 'k_c')
    p.rm(VM)
    trees.append(('짝 VM 없음', p, base))
    p, base = new_case(tmp, 'k_d', child_routes_two)
    p.sub(G + 'gallery_router.py', 'gallery_popular_embed_fragment, name="popular_embed"', 'gallery_popular_page, name="popular_embed"')
    trees.append(('라우트가 임베드 아님', p, base))
    return trees


def measure(tmp, p, scripts=SCRIPTS):
    """승인 유입의 부모 측정 꼴 — git 없는 사본 · 게이트 없음 · 같은 --only → (판독 키 IM5, stderr)."""
    snap = tmp / ('snap-' + p.root.name)
    shutil.copytree(p.root, snap, ignore=shutil.ignore_patterns('.git', '.dddjango-web'), symlinks=True)
    code, out, err = run(scripts, snap, '--only', GATE_ONLY)
    try:
        keys = sorted(k for k in _read_findings(out, code, snap) if k.startswith('[IM5]'))
    except ValueError as error:
        keys = ['판독 불가 — %s' % error]
    shutil.rmtree(snap)
    return keys, err


def bundle_k(tmp, j):
    trees = key_trees(tmp)
    found = [(name, im5(run(SCRIPTS, p.root, '--diff-base', base, '--only', 'im')[1])) for name, p, base in trees]
    violations = {f[0][1] for _name, f in found if f}
    fixes = [f[0][2] for _name, f in found if f]
    check('K 네 트리 모두 IM5 하나(페이지 4행)', all(len(f) == 1 and f[0][0].endswith('daily_note_view.html:4') for _n, f in found), found)
    check('K 증거 파일만 다른 네 트리의 `위반:` 줄 글자 같음', len(violations) == 1, violations)
    check('K 위반 줄이 대상 BC 폴더를 «없다»로 적는다(I4 — 조정자 미룸 ⓐ)',
          any('타 BC `application/gallery/` 임베드 증거가 없다' in v for v in violations), violations)
    check('K 교정 줄은 첫 빈 고리로 넷이 다르다', len(set(fixes)) == 4, fixes)
    first = [f.split(' — ')[0] for f in fixes]
    check('K 첫 빈 고리 문구(자리 · 지역 이름 · 짝 VM · 라우트)',
          first[0].startswith('이 페이지가 그리는 템플릿에 hx-get=') and '바로 넘기지 않는다' in first[1]
          and first[2].startswith('짝 VM(view_model/<화면>_vm.py)이 없다') and '<화면>_embed_fragment 에 묶이지 않는다' in first[3], first)
    for name, p, base in trees:
        out = run(SCRIPTS, p.root, '--diff-base', base, '--only', 'im')[1]
        block = re.search(r'^\[IM5\] BLOCKER — .+\n(?:  .+\n)*', out, re.M)
        check('K %s — 발견은 세 줄(교정 한 줄 · 개행 없음)' % name, block is not None and block.group().count('\n') == 3, out)
    measured = [measure(tmp, p) for _name, p, _base in trees]
    check('K 부모 측정 꼴 — 네 트리 IM5 키 같음 · 판독됨 · stderr 없음',
          all(m == measured[0] for m in measured) and measured[0][0] and not measured[0][1]
          and not measured[0][0][0].startswith('판독 불가'), measured)
    if j.old is not None:
        old = {im5(run(j.old, p.root, '--diff-base', base, '--only', 'im')[1])[0][1] for _n, p, base in trees}
        check('K 2.8.1 도 네 트리 위반 줄 같음(문구만 다르다 — 판 올림 뒤 이의 처분은 한 번 다시 묻는다)',
              len(old) == 1 and old != violations, (old, violations))


# ====================================================================== H — 교정 줄 셸 갈래(I2 · S5)

def bundle_h(tmp, j):
    p, base = new_case(tmp, 'h_doc')
    vm(p, value='""')
    p.w(SEC_CSS, '@import url("/static/web/application/gallery/gallery_popular_view.css");', '.x { display: block; }')
    found = {f[0]: f for f in im5(run(SCRIPTS, p.root, '--diff-base', base, '--only', 'im')[1])}
    spot = found.get('web/application/daily_note/presentation_layer/view/daily_note_view.html:4')
    other = found.get(SEC_CSS + ':1')
    check('H 문서 이동 셸 · 자리 맞음 — 교정 줄이 첫 빈 고리 + 네 고리', spot is not None
          and '임베드라면 네 고리를 맞춘다' in spot[2] and '자식 화면이 뒤 슬라이스면 그 슬라이스 끝에 선다' in spot[2], found)
    check('H 문서 이동 셸 · 그 밖 — 교정 줄이 «이 자리(CSS @import · url())는 예외가 아니다»', other is not None
          and other[2].startswith('이 자리(CSS @import · url())는 예외가 아니다') and '(문서 이동 셸이면 타 BC' in other[1], found)

    def persistent(q):
        q.sub(SHELL, '<body>', '<body data-root-shell="root_view@2.6">')
    p, base = new_case(tmp, 'h_shell', persistent)
    p.w(SEC_CSS, '@import url("/static/web/application/gallery/gallery_popular_view.css");', '.x { display: block; }')
    found = {f[0]: f for f in im5(run(SCRIPTS, p.root, '--diff-base', base, '--only', 'im')[1])}
    css = found.get(SEC_CSS + ':1')
    check('H 지속 셸 — 교정 줄이 SH4 갈래(셸 <head> 가 모두 싣는다 · 페이지 block head 는 SH3 금지)', css is not None
          and css[2].startswith('지속 셸이면 셸 <head> 가 그 제품 BC 조각 CSS 를 모두 싣는다(SH4)')
          and 'SH3 금지' in css[2] and '덧줄' not in css[2], found)
    check('H 지속 셸 — 위반 줄은 문서 이동 셸과 글자 같다(키는 셸 방식에 기대지 않는다)', css is not None and other is not None
          and css[1] == other[1], (css, other))
    sh = run(SCRIPTS, p.root, '--diff-base', base, '--only', 'sh')
    check('H 지속 셸 — 증거 있는 페이지의 block head 는 SH3 가 잡는다(빈틈 없음)', '[SH3] BLOCKER — ' + PAGE in sh[1], sh)

    p, base = new_case(tmp, 'h_s5', lambda q: declare(q, TWO_PRODUCTS, guest_shell=True,
                                                      guest_body='<body data-root-shell="root_guest_view@2.6">'))
    page(p, shell='root/scaffold/view/root_guest_view.html')
    p.w(SEC_CSS, '@import url("/static/web/application/gallery/gallery_popular_view.css");', '.x { display: block; }')
    found = {f[0]: f for f in im5(run(SCRIPTS, p.root, '--diff-base', base, '--only', 'im')[1])}
    css = found.get(SEC_CSS + ':1')
    check('H 지속 셸 + 다른 제품 BC — 교정 줄에 theme 뒤 덧줄 안내(S5)', css is not None and '덧줄' in css[2]
          and 'SH4 필요 집합 밖' in css[2], found)


# ====================================================================== W — 증거 파싱 경고(N-W)

def bundle_w(tmp, j):
    for name, slot in (('증거 있음', True), ('자리 없음 — 교정 줄이 VM 을 읽는다', False)):
        p, base = new_case(tmp, 'w-' + str(slot))
        p.append(VM, 'import re', '_DIGITS = re.compile("\\d+")')
        if not slot:
            section(p, '')
        got = run(SCRIPTS, p.root, '--diff-base', base, '--only', 'im')
        check('W %s — 잘못된 이스케이프가 있는 증거 파일: 게이트 stderr 없음 · IM5 %d' % (name, 0 if slot else 1),
              not got[2] and len(im5(got[1])) == (0 if slot else 1), got)
        keys, err = measure(tmp, p)
        check('W %s — 부모 측정 꼴 stderr 없음 · 판독됨' % name, not err and not any(k.startswith('판독 불가') for k in keys),
              (keys, err))


# ====================================================================== D — 빚 지문

def bundle_d(tmp, j):
    p, base = new_case(tmp, 'debt')
    p.commit('parent')
    target = p.root / '.git' / 'debt-282.json'
    got = run(SCRIPTS, p.root, '--debt-scan', '--json', target)
    data = json.loads(target.read_text(encoding='utf-8')) if target.exists() else {}
    key = 'IM5|application/daily_note/presentation_layer/view/daily_note_view.html'
    check('D 빚 스캔 — 임베드 받는 페이지 머리 link 키 없음', got[0] == 0 and key not in data.get('counts', {}) and not got[2], got)
    if j.old is not None:
        target.unlink()
        old = run(j.old, p.root, '--debt-scan', '--json', target)
        before = json.loads(target.read_text(encoding='utf-8')) if target.exists() else {}
        check('D 2.8.1 은 그 키가 있다', key in before.get('counts', {}), old)
        check('D 빚 지문(검사 집합 · 키 의미론) 두 판 같음',
              {k: v for k, v in data.get('scanner', {}).items() if k != 'plugin'}
              == {k: v for k, v in before.get('scanner', {}).items() if k != 'plugin'} and data.get('scanner'), (data, before))
        check('D 빚 키는 그 하나만 다르다(완화만 — 새 키 0)', set(data.get('counts', {})) == set(before.get('counts', {})) - {key},
              (data.get('counts'), before.get('counts')))


# ====================================================================== M — 검사기 변이

def mutant(tmp, name, edits):
    """scripts 사본(링크 아님)에 글자 바꿈 → 그 scripts 폴더. 바꿀 글자는 정확히 한 번 있어야 한다."""
    root = tmp / ('mut-' + name)
    shutil.copytree(SCRIPTS, root / 'scripts', ignore=shutil.ignore_patterns('__pycache__', 'test'))
    shutil.copytree(SCRIPTS.parent / '.claude-plugin', root / '.claude-plugin')
    for rel, old, new in edits:
        path = root / 'scripts' / rel
        text = path.read_text(encoding='utf-8')
        if text.count(old) != 1:
            raise RuntimeError('변이 %s — %s 에서 바꿀 글자가 %d번(정확히 한 번이어야 한다): %r' % (name, rel, text.count(old), old[:80]))
        path.write_text(text.replace(old, new), encoding='utf-8')
    return root / 'scripts'


MUTANTS = (
    ('셸 extends 조건', 'fa8', [('src/embed.py', "    target: Optional[str] = _extends(text) if text is not None else None\n",
                             "    target: Optional[str] = (_extends(text) if text is not None else None) or 'root/scaffold/view/root_view.html'\n")]),
    ('렌더 뷰(block · verbatim) — 자리', 'fa2 fa3 fa4', [('src/embed.py', '        text: Optional[str] = _rendered_text(ctx, t)\n        tags',
                                                     '        text: Optional[str] = ctx.mask_of(t).no_comments\n        tags')]),
    ('렌더 뷰 — include 닫힘', 'n1 n2 n3', [('src/embed.py', '    text: Optional[str] = _rendered_text(ctx, t)\n    if text is None:\n        return []',
                                          '    text: Optional[str] = ctx.mask_of(t).no_comments\n    if text is None:\n        return []')]),
    ('속성 정확 이름', 'fa5', [('src/embed.py', '            for name in _HX_ATTRS:\n',
                             "            for name in [a for a in tag.attrs if a.endswith('hx-get')]:\n")]),
    ('원래 클래스', 'fa7', [('src/embed.py', 'isinstance(n, ast.ClassDef) and n.name == cls), None)',
                          'isinstance(n, ast.ClassDef) and any(getattr(b, "name", "") == name for b in n.body)), None)')]),
    ('reverse 첫 인자 · 모두 임베드', 'fa7b', [
        ('src/embed.py', """        if not (isinstance(n, ast.Call) and ((isinstance(n.func, ast.Name) and n.func.id in _REVERSE)
                                             or (isinstance(n.func, ast.Attribute) and n.func.attr in _REVERSE))):
            continue
        arg: Optional[ast.expr] = n.args[0] if n.args else next((k.value for k in n.keywords if k.arg == 'viewname'), None)""",
         """        if not (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in nimports):
            continue
        arg: Optional[ast.expr] = n"""),
        ('src/embed.py', """                and base_name_of(view) == original[:-len(_FRAGMENT)] + '_view.py' and _top(vtree, None, original)):
            return None""", """                and base_name_of(view) == original[:-len(_FRAGMENT)] + '_view.py' and _top(vtree, None, original)):
            continue""")]),
    ('router 별칭 풀기', 'fa9', [('src/embed.py', '                bound[name] = rimports[n.args[1].id]',
                              '                bound[name] = (rimports[n.args[1].id][0], n.args[1].id)')]),
    ('링크 막음', 'lk1 lk2', [('src/embed.py', '        if path.is_symlink():\n            return False\n', ''),
                           ('src/embed.py', '        return os.path.commonpath([web, os.path.realpath(path)]) == web', '        return True')]),
    ('렌더 닫힘 좁힘', 's4', [('src/embed.py', '                    for t in sorted(_closure(ctx, rendered)):',
                             "                    for t in sorted(f for f in ctx.files if f.endswith('.html')):")]),
    ('자식의 자식', 'r4', [('src/embed.py', '                    work.append((rendered, _vms(ctx, bcdir, func[:-len(_FRAGMENT)]), False))',
                          '                    pass')]),
    ('꼬리 떼기', 'r6', [('src/check_imports.py', "    real: Optional[str] = loaded_file(e.uri.strip().lstrip('/')) if e.kind == 'static' else None",
                        "    real: Optional[str] = e.target if e.kind == 'static' else None")]),
    ('앞머리 / 떼기', 'r6b', [('src/check_imports.py', "    real: Optional[str] = loaded_file(e.uri.strip().lstrip('/')) if e.kind == 'static' else None",
                            "    real: Optional[str] = loaded_file(e.uri.strip()) if e.kind == 'static' else None")]),
    ('async 받음', 'r7', [('src/embed.py', "_Fn = Union[ast.FunctionDef, ast.AsyncFunctionDef]", "_Fn = ast.FunctionDef"),
                         ('src/embed.py', "isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name), None)",
                          "isinstance(n, ast.FunctionDef) and n.name == name), None)")]),
)


def mutant_case(tmp, key):
    """변이가 뒤집어야 하는 장면 → (Proj, 바탕, 이 판의 기대 IM5 줄, 경로)."""
    if key in ('fa2', 'fa3'):
        p, base = new_case(tmp, 'm-' + key)
        section(p, '')
        p.append(PAGE, ('<div ' + SLOT + '></div>') if key == 'fa2' else '{% block nowhere %}<div ' + SLOT + '></div>{% endblock nowhere %}')
        return p, base, [4], PAGE
    if key == 'fa4':
        p, base = new_case(tmp, 'm-fa4')
        section(p, '{% verbatim %}<div ' + SLOT + '></div>{% endverbatim %}')
        return p, base, [4], PAGE
    if key in ('n1', 'n2', 'n3'):
        p, base = new_case(tmp, 'm-' + key)
        page(p, body=('{% verbatim %}' + INCLUDE_SEC + '{% endverbatim %}' if key == 'n3' else '',))
        if key != 'n3':
            p.append(PAGE, '{% block nowhere %}' + INCLUDE_SEC + '{% endblock nowhere %}' if key == 'n1' else INCLUDE_SEC)
        return p, base, [4], PAGE
    if key == 'fa5':
        p, base = new_case(tmp, 'm-fa5')
        section(p, '<div data-x-hx-get="{{ state.popular_embed_href }}"></div>')
        return p, base, [4], PAGE
    if key == 'fa8':
        p, base = new_case(tmp, 'm-fa8')
        p.w(PAGE, '{% load static %}', '{% block head %}' + link(CHILD) + '{% endblock head %}', INCLUDE_SEC)
        return p, base, [2], PAGE
    if key in ('fa7', 'fa7b'):
        p, base = new_case(tmp, 'm-' + key, child_routes_two)
        head = ['from django.urls import reverse', '', '']
        old = ['class _Old:', '    @staticmethod', '    def gallery_popular_embed_href() -> str:',
               '        from web.application.gallery.gallery_router import GalleryRoutes', '',
               '        return reverse(GalleryRoutes.POPULAR_EMBED)', '', '']
        nav = ['class GalleryNavigator:', '    @staticmethod', '    def gallery_popular_embed_href() -> str:',
               '        from web.application.gallery.gallery_router import GalleryRoutes', '']
        p.w(G + 'gallery_navigator.py', *(head + old + nav + ['        return reverse(GalleryRoutes.POPULAR)'] if key == 'fa7' else
                                          head + nav + ['        _unused: str = GalleryRoutes.POPULAR_EMBED',
                                                        '        return reverse(GalleryRoutes.POPULAR)']))
        return p, base, [4], PAGE
    if key == 'fa9':
        p, base = new_case(tmp, 'm-fa9')
        p.w(G + 'gallery_router.py', 'from django.urls import URLPattern, path', '',
            'from web.application.gallery.presentation_layer.view.gallery_popular_view import gallery_popular_page as gallery_popular_embed_fragment',
            '', 'app_name: str = "gallery"', '', '', 'class GalleryRoutes:', '    POPULAR_EMBED: str = "gallery:popular_embed"', '', '',
            'urlpatterns: list[URLPattern] = [path("popular/embed/", gallery_popular_embed_fragment, name="popular_embed")]')
        p.append(G + 'presentation_layer/view/gallery_popular_view.py', '', '',
                 'def gallery_popular_page(request: HttpRequest) -> HttpResponse:', '    return render(request, _TEMPLATE, {})')
        return p, base, [4], PAGE
    if key in ('lk1', 'lk2'):
        p, base = new_case(tmp, 'm-' + key)
        rel = VM if key == 'lk1' else SEC
        outside = tmp / ('m-outside-' + key)
        outside.mkdir()
        shutil.copy(p.root / rel, outside / 'f')
        (p.root / rel).unlink()
        os.symlink(outside / 'f', p.root / rel)
        return p, base, [4], PAGE
    if key == 's4':
        p, base = new_case(tmp, 'm-s4', gallery_main)
        page(p, head=(link('web/application/gallery/gallery_main_view.css'),))
        return p, base, [4], PAGE
    if key == 'r4':
        p, base = new_case(tmp, 'm-r4', stamp_bc)
        page(p, head=(link(CHILD), link('web/application/stamp/stamp_card_body_section.css')))
        return p, base, [], PAGE
    if key in ('r6', 'r6b'):
        p, base = new_case(tmp, 'm-' + key)
        page(p, head=(link(CHILD, '?v=1') if key == 'r6' else link('/' + CHILD),))
        return p, base, [], PAGE
    if key == 'r7':
        p, base = new_case(tmp, 'm-r7')
        p.sub(G + 'presentation_layer/view/gallery_popular_view.py', 'def gallery_popular_embed_fragment',
              'async def gallery_popular_embed_fragment')
        return p, base, [], PAGE
    raise KeyError(key)


def bundle_m(tmp, j):
    for name, keys, edits in MUTANTS:
        try:
            scripts = mutant(tmp, name.replace(' ', '_').replace('/', '_'), edits)
        except RuntimeError as error:
            check('M %s — 변이를 걸 수 있다' % name, False, error)
            continue
        for key in keys.split():
            p, base, want, path = mutant_case(tmp, key)
            real = run(SCRIPTS, p.root, '--diff-base', base, '--only', 'im')
            mut = run(scripts, p.root, '--diff-base', base, '--only', 'im')
            check('M %s 빼면 %s 가 뒤집힌다(이 판 %s · 변이 %s)' % (name, key, want, lines(mut[1], path)),
                  lines(real[1], path) == want and lines(mut[1], path) != want, (real, mut))
    # 경고 막음 빼기 → 증거 파싱의 SyntaxWarning 이 stderr 로 샌다(N-W)
    scripts = mutant(tmp, 'warn', [('src/embed.py', "                        warnings.simplefilter('ignore')\n",
                                    "                        warnings.simplefilter('always')\n")])
    p, base = new_case(tmp, 'm-warn')
    p.append(VM, 'import re', '_DIGITS = re.compile("\\d+")')
    real, mut = run(SCRIPTS, p.root, '--diff-base', base, '--only', 'im'), run(scripts, p.root, '--diff-base', base, '--only', 'im')
    check('M 경고 막음 빼면 stderr 가 샌다(이 판 없음 · 변이 있음)', not real[2] and 'SyntaxWarning' in mut[2], (real, mut))
    # 위반 줄에 첫 빈 고리를 넣으면 증거 파일만 다른 트리의 위반 줄이 갈린다(I1)
    scripts = mutant(tmp, 'key', [('src/check_imports.py',
                                   "'(교차 BC 조각 CSS 는 그 BC view 를 채널 ④ 로 임베드한 페이지의 머리 link 만)' % (tbc, what, target, cdir))",
                                   "'(교차 BC 조각 CSS 는 그 BC view 를 채널 ④ 로 임베드한 페이지의 머리 link 만) %s' "
                                   "% (tbc, what, target, cdir, explain(ctx, f, real or '')))")])
    trees = key_trees(tmp / 'm-key')
    real = {im5(run(SCRIPTS, p.root, '--diff-base', base, '--only', 'im')[1])[0][1] for _n, p, base in trees}
    mut = {im5(run(scripts, p.root, '--diff-base', base, '--only', 'im')[1])[0][1] for _n, p, base in trees}
    check('M 위반 줄에 첫 빈 고리를 넣으면 네 트리 위반 줄이 갈린다(이 판 1 · 변이 %d)' % len(mut), len(real) == 1 and len(mut) > 1,
          (real, mut))


def main():
    only = set(sys.argv[1:])
    with tempfile.TemporaryDirectory(prefix='web282-') as top:
        j = Judge(Path(top))
        for bundle in (bundle_r, bundle_s, bundle_k, bundle_h, bundle_w, bundle_d, bundle_m):
            if only and bundle.__name__[7:] not in only:
                continue
            with tempfile.TemporaryDirectory(prefix='web282-%s-' % bundle.__name__[7:]) as tmp:
                try:
                    bundle(Path(tmp), j)
                except Exception as error:
                    check(bundle.__name__ + ' 준비·실행 오류', False, '%s: %s' % (type(error).__name__, error))
    print('2.8.2 임베드 CSS 픽스처: PASS %d / FAIL %d' % (PASS, FAIL))
    return bool(FAIL)


if __name__ == '__main__':
    sys.exit(main())
