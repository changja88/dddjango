"""2.4.0 지속 셸 SH1~SH5 · PU2 · 승인 유입 회귀. 실제 임시 git 프로젝트만 검사한다.

Z0 = 표지 없는 바탕과 출력 대조, Z1~Z6 = 설계의 양성/음성 짝, Z7 = 러너, Z8 = 승인 유입.
BASELINE 이 이력에 없으면 Z0 의 옛 러너 대조만 건너뛴 사실을 낸다. 네트워크·브라우저는 쓰지 않는다.
"""
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
sys.path.insert(0, str(SCRIPTS))
from fixtures_patch230 import (ENV, FLAT_SHELL, GUEST_SHELL, ORDER_PAGE, LOBBY_PAGE, REGISTRY, TOKENS,
                               backstop, fix_of, found, git, message_of, mkbc, mkstd, mkdeclared, plugin_version,
                               scope_folder, strip_stamp)

BASELINE = 'a73dfadc'
RULE = REPO / 'dddjango-web/skills/implementation-django/references/final.md'
COUNT_TOKENS = (('검사 93종 중 86종', '검사 #종 중 #종'), ('검사 92종 중 85종', '검사 #종 중 #종'),
                ('검사 86종 중 79종', '검사 #종 중 #종'), ('[backstop] 검사 93종', '[backstop] 검사 #종'),
                ('[backstop] 검사 92종', '[backstop] 검사 #종'), ('[backstop] 검사 86종', '[backstop] 검사 #종'))
PASS = FAIL = 0
REV = '?v={{ root_state.shell_rev }}'
SDK = 'static/vendor/kakao_js_sdk/kakao.min.js'
SCRIPT = '<script src="{% static \'web/js/sample.js\' %}" defer></script>'
SECTION = 'application/order/presentation_layer/section/order_list_summary_section.html'


def counts_normalized(text):
    for old, new in COUNT_TOKENS:
        text = text.replace(old, new)
    # 2.7.0 — 새 검사 TG4 의 알림 줄은 옛 판 출력에 없다(TG4 는 fixtures_patch270_browser.py 가 본다)
    return '\n'.join(line for line in text.split('\n') if not line.startswith('[info] TG4 '))


def normalized(result):
    return result[0], counts_normalized(result[1])


def baseline_scripts(tmp):
    archive = subprocess.run(['git', '-C', str(REPO), 'archive', BASELINE, 'dddjango-web/scripts',
                              'dddjango-web/.claude-plugin'], capture_output=True, env=ENV)
    if archive.returncode:
        print('SKIP U — 바탕 커밋 %s 없음: 옛 러너 대조만 건너뜀' % BASELINE)
        return None
    tmp.mkdir()
    subprocess.run(['tar', '-xf', '-', '-C', str(tmp)], input=archive.stdout, check=True)
    return tmp / 'dddjango-web/scripts'


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok:
        print('    ' + str(detail).replace('\n', '\n    ')[:2400])


def asset(path):
    return 'web/' + path[7:] if path.startswith('static/') else path


def load(path):
    if path.endswith('.css'):
        return '<link rel="stylesheet" href="{% static \'' + asset(path) + '\' %}' + REV + '">'
    return '<script src="{% static \'' + asset(path) + '\' %}' + REV + '" defer></script>'


TABS = '''{% for tab in root_state.tabs %}
<a id="root-tab-{{ tab.key }}" class="root-tab-bar__tab root-tab-bar__tab--{{ tab.key }}{% if tab.is_current %} root-tab-bar__tab--current{% endif %}"
   href="{{ tab.href }}"{% if tab.is_current %} aria-current="page"{% endif %}>{{ tab.label }}</a>
{% endfor %}'''


def shell_text(shell=FLAT_SHELL, paths=()):
    stem = Path(shell).stem
    return '''{% load static %}
<!doctype html><html lang="ko"><head>
<meta name="htmx-config" content='{"historyCacheSize":0}'>
<title>{% block title %}채널{% endblock title %}</title>
''' + '\n'.join(load(path) for path in paths) + '''
</head><body data-testid="root-view" data-root-shell="''' + stem + '''@{{ root_state.shell_rev }}">
<main id="root-content" hx-history-elt>
{% block content %}{% endblock content %}
<template><div id="root-tab-items" class="root-tab-bar__items" hx-swap-oob="innerHTML">
''' + TABS + '''
</div></template>
</main>
<nav id="root-tab-bar" class="root-tab-bar" hx-boost="true" hx-sync="this:replace">
<div id="root-tab-items" class="root-tab-bar__items">
''' + TABS + '''
</div></nav>
</body></html>'''


def paths_for(p, shell):
    own = shell == GUEST_SHELL
    ds = 'design_system/guest' if own else 'design_system'
    foundation = [ds + '/foundation/app_' + t + '.css' for t in TOKENS]  # 관례 순(color … asset)
    extra = ([ds + '/component/button/primary_button.css'] if not own else [])
    extra += ['static/application/lobby/lobby_view.css'] if own else ['static/application/order/order_list_view.css']
    # own 셸 CSS 는 픽스처의 고정 기대 집합이다.
    return foundation + [ds + '/theme/app_theme.css', 'static/root/' + Path(shell).stem + '.css'] + sorted(extra) + [
        'static/htmx/htmx.min.js', 'static/js/root_shell.js']


def prepare(tmp, declared=False, persistent=True):
    if declared:
        p, _ = mkdeclared(tmp)
        shell, page = GUEST_SHELL, LOBBY_PAGE
        p.w('web/static/application/lobby/lobby_view.css', '.lobby-view {}')
    else:
        p = mkstd(tmp)
        shell, page = FLAT_SHELL, ORDER_PAGE
    p.w('web/static/js/root_shell.js', 'document.addEventListener("htmx:load", () => {});')
    for s in ([FLAT_SHELL, GUEST_SHELL] if declared else [FLAT_SHELL]):
        p.w('web/static/root/' + Path(s).stem + '.css', '.root-tab-bar { display: flex; }')
    if persistent:
        p.w('web/' + shell, shell_text(shell, paths_for(p, shell)))
    return p, shell, page, p.commit('fixture-base')


def expect(p, base, cid, red, name, path=None, extra=()):
    got = backstop(p.root, '--diff-base', base, '--only', cid, *extra)
    hit = found(got[1], cid.upper(), path) if path else ('[' + cid.upper() + '] BLOCKER' in got[1])
    check(name, got[0] == (2 if red else 0) and hit == red and '내부 오류' not in got[1], got)
    return got


def bundle_z0(tmp):
    old = baseline_scripts(tmp / 'old')
    for declared in (False, True):
        p, shell, page, base = prepare(tmp / str(declared), declared, False)
        # 등재 SDK 와 hx-get 조각이 있는 문서 이동 프로젝트도 새 갈래가 침묵해야 한다.
        install_sdk(p)
        p.append('web/' + page, '{% block scripts %}', load(SDK).replace(REV, ''), '{% endblock %}')
        base = p.commit('document-sdk')
        p.append('web/' + page, '<div hx-get="/fragment/">fragment</div>')
        expect(p, base, 'sh', False, 'Z0 문서 이동 셸 sh 무발화(%s)' % declared)
        for args in (('--diff-base', base), ('--diff-base', base, '--slice-end'), ('--all',)):
            got = backstop(p.root, *args)
            check('Z0 표지 없는 호스트 SH info 0(%s %s)' % (declared, args[-1]), '[SH' not in got[1])
            if old:
                check('Z0 출력 양쪽 정규화 뒤 byte 동일(%s %s)' % (declared, args[-1]),
                      normalized(got) == normalized(backstop(p.root, *args, scripts=old)), got)
        non = tmp / ('nongit' + str(declared))
        shutil.copytree(p.root, non, ignore=shutil.ignore_patterns('.git'))
        got = backstop(non, '--only', 'sh')
        check('Z0 비git SH2 info 0(%s)' % declared, got[0] == 0 and 'git 저장소 아님' in got[1]
              and '기준점 본문 없음' not in got[1] and '[SH' not in got[1], got)
        if old:
            check('Z0 비git 전체 출력 동일(%s)' % declared,
                  normalized(backstop(non, '--all')) == normalized(backstop(non, '--all', scripts=old)))
        for extra in ((), ('--refactor',)):
            e, out, data = p.scan(*extra)
            check('Z0 빚 지문 실측', data.get('scanner', {}).get('checks') == 'e49c83776ff9faf6', data.get('scanner'))
            if old:
                e0, out0, data0 = p.scan(*extra, scripts=old)
                check('Z0 빚 출력·JSON 동일(%s %s)' % (declared, extra),
                      (e, out) == (e0, out0) and strip_stamp(data) == strip_stamp(data0))
        if old:
            folder = scope_folder(p, 'frozen', scripts=old)
            got = backstop(p.root, '--debt-residual', folder)
            notices = re.findall(r'^\[info\] 플러그인 판 바뀜', got[1], re.M)
            check('Z0 옛 G0 동결본 잔존 0 · 판 경계 0 · 판 글자 알림만', got[0] == 0 and '판 경계' not in got[1]
                  and len(notices) == int(plugin_version(old) != plugin_version(SCRIPTS)), got)


def bundle_z1(tmp):
    for declared in (False, True):
        p, shell, page, base = prepare(tmp / str(declared), declared)
        section = page.replace('/view/', '/section/').replace('_view.html', '_section.html')
        cases = [(page, '<form hx-boost="true"></form>', True), (page, '<main hx-boost></main>', True),
                 (page, '<section hx-boost="true"></section>', True), (page, '<a href="/" hx-boost="yes">x</a>', True),
                 (page, '<form data-hx-boost="true"></form>', True),
                 (page, '{% verbatim %}<form hx-boost="true">{% endverbatim %}', True),
                 (page, '<a href="/" hx-boost="true" hx-get="/x/">x</a>', True),
                 (page, '<a\n href="/"\n data-hx-boost="yes">x</a>', True),
                 (page, '<div hx-history="false"></div>', True), (page, '<div data-hx-history="false"></div>', True),
                 (section, '<div hx-swap-oob="true"></div>', True),
                 (section, '<a href="/" hx-boost="true">x</a>', False),
                 (section, '<a href="/" data-hx-boost="false">x</a>', False),
                 (page, '<!-- <form hx-boost="true"> -->', False),
                 (page, '&lt;form hx-boost="true"&gt;', False),
                 ('design_system/component/button/primary_button.html', '<a href="/" hx-boost="true">x</a>', True),
                 (page.replace('/view/', '/ui_extension/'), '<a href="/" hx-boost="true">x</a>', True),
                 ('legacy/stray.html', '<a href="/" hx-boost="true">x</a>', True)]
        if declared:
            cases.append((ORDER_PAGE, '<a href="/" hx-boost="true">x</a>', True))
        for i, (file, text, red) in enumerate(cases):
            p.reset(base)
            p.append('web/' + file, text) if (p.root / 'web' / file).exists() else p.w('web/' + file, text)
            expect(p, base, 'sh1', red, 'Z1 %s %d' % (declared, i), file if red else None)
        p.reset(base)
        p.w('web/base/base.html', '{% extends "' + shell + '" %}')
        p.w('web/legacy/view/old.html', '{% extends "base/base.html" %}', '<a href="/" hx-boost="true">x</a>')
        expect(p, base, 'sh1', False, 'Z1 옛 2단 상속 페이지 허용')
        p.append('web/legacy/view/old.html', '<form hx-boost="true"></form>')
        landed = p.commit('land-old')
        p.append('web/legacy/view/old.html', '<p>added</p>')
        expect(p, landed, 'sh1', False, 'Z1 기존 위반 줄 게이트 침묵')
    p, _, _, base = prepare(tmp / 'document', persistent=False)
    p.w('web/base/base.html', '<body data-root-shell="legacy"></body>')
    expect(p, base, 'sh1', True, 'Z1 지속 셸 없는 표준 셸 밖 표지', 'base/base.html')


def bundle_z1_alias(tmp):
    message = '같은 요소의 hx-* · data-hx-* 별칭 값이 다름 — '
    for declared in (False, True):
        p, shell, page, base = prepare(tmp / str(declared), declared)
        for first, second in (('true', 'false'), ('false', 'true'), ('true', 'true'), ('false', 'false')):
            p.reset(base)
            p.append('web/' + page, '<a href="/" hx-boost="%s" data-hx-boost="%s">x</a>' % (first, second))
            red = first != second
            got = expect(p, base, 'sh1', red, 'Z1 화면 별칭 값(%s %s/%s)' % (declared, first, second), page if red else None)
            check('Z1 별칭 충돌 문구(%s %s/%s)' % (declared, first, second),
                  (message + 'hx-boost' in got[1]) == red, got)
        for name in ('hx-history', 'hx-history-elt', 'hx-swap-oob', 'hx-get'):
            p.reset(base)
            boost = ' hx-boost="true"' if name == 'hx-get' else ''
            p.append('web/' + page, '<a href="/"%s %s="true" data-%s="false">x</a>' % (boost, name, name))
            got = expect(p, base, 'sh1', True, 'Z1 기존 판독 속성 충돌(%s %s)' % (declared, name), page)
            check('Z1 기존 판독 속성 충돌 문구(%s %s)' % (declared, name), message + name in got[1], got)
    old = baseline_scripts(tmp / 'old')
    p, shell, page, base = prepare(tmp / 'document', persistent=False)
    for name in ('hx-get', 'hx-post', 'hx-target', 'hx-swap'):
        p.reset(base)
        p.append('web/' + page, '<a href="/" %s="true" data-%s="false">x</a>' % (name, name))
        got = expect(p, base, 'sh1', False, 'Z0 무표지 일반 속성 충돌 침묵 ' + name)
        if old:
            check('Z0 무표지 일반 속성 충돌 출력 무변 ' + name,
                  normalized(backstop(p.root, '--diff-base', base)) ==
                  normalized(backstop(p.root, '--diff-base', base, scripts=old)), got)
    p.reset(base)
    p.append('web/' + page, '<a href="/" hx-boost="true" data-hx-boost="false">x</a>')
    landed = p.commit('old-document-boost-conflict')
    p.append('web/' + page, '<p>added</p>')
    expect(p, landed, 'sh1', False, 'Z0 무표지 기존 부스트 충돌 diff 침묵')


def bundle_z2(tmp):
    for declared in (False, True):
        p, shell, page, base = prepare(tmp / str(declared), declared)
        good = p.read('web/' + shell)
        mutations = [good.replace('<meta name="htmx-config"', '<meta name="wrong"'),
                     good.replace('{% block title %}채널{% endblock title %}', '채널'),
                     good.replace('</head>', '</head>' + load('static/js/root_shell.js')),
                     good.replace(' defer', ''), good.replace('{% block content %}', '{% block head %}{% endblock %}{% block content %}'),
                     good.replace(Path(shell).stem + '@', 'wrong@'), good.replace(' hx-history-elt', ''),
                     good.replace('hx-sync="this:replace"', 'hx-sync="this:drop"'),
                     good.replace('{{ tab.label }}', 'wrong', 1), good.replace('href="{{ tab.href }}"', 'href="/"'),
                     good.replace('<main id=', '<main hx-target="body" id='), good.replace('<body ', '<body ').replace(
                         '<main id=', '{{ root_state.data|json_script:"root-data" }}<main id='),
                     good.replace(REV, '')]
        for i, text in enumerate(mutations, 1):
            p.w('web/' + shell, text)
            expect(p, base, 'sh2', True, 'Z2 꼴 %d 빠짐(%s)' % (i, declared), shell)
        variants = [good, good.replace('hx-history-elt', 'data-hx-history-elt'),
                    good.replace('hx-history-elt', 'hx-history-elt data-hx-history-elt'),
                    good.replace('hx-history-elt', 'hx-history-elt data-hx-history-elt=""'),
                    good.replace('hx-boost=', 'data-hx-boost=').replace('hx-sync=', 'data-hx-sync='),
                    good.replace('{% block content %}', '{{ root_state.data|json_script:"root-data" }}\n{% block content %}')]
        for i, text in enumerate(variants):
            p.w('web/' + shell, text + '\n')
            expect(p, base, 'sh2', False, 'Z2 완전·별칭·자료(%s %d)' % (declared, i))
        for text in (good.replace('hx-boost="true"', 'hx-boost="true" data-hx-boost="false"'),
                     good.replace('채널', ' {# empty #} '), good.replace('root_state.shell_rev', 'state.revision')):
            p.w('web/' + shell, text)
            expect(p, base, 'sh2', True, 'Z2 별칭 충돌·빈 제목·다른 꼬리', shell)
        for i, marker in enumerate(('<body data-root-shell="x"></body>', '<nav hx-boost="true"></nav>',
                                    '<main hx-history-elt></main>', '<main data-hx-history-elt></main>')):
            p.w('web/' + shell, marker)
            expect(p, base, 'sh2', True, 'Z2 후보 표지 하나 %d' % i, shell)
            p.w('web/base/base.html', marker)
            expect(p, base, 'sh1', True, 'Z2 표준 셸 밖 후보 %d' % i, 'base/base.html')
            p.rm('web/base/base.html')
        p.w('web/' + shell, '<html><body></body></html>')
        got = expect(p, base, 'sh2', False, 'Z2 표지 전부 걷음')
        check('Z2 표지 걷음 info', '[info] 지속 셸 표지가 기준점 뒤 없어졌다' in got[1], got)
        p.w('web/' + shell, good)
        non = tmp / ('non' + str(declared))
        shutil.copytree(p.root, non, ignore=shutil.ignore_patterns('.git'))
        got = backstop(non, '--only', 'sh2')
        check('Z2 비git 표지 기준점 알림 하나', got[0] == 0 and got[1].count('기준점 본문 없음 — 표지 걷음 판정 생략') == 1, got)


def bundle_z3(tmp):
    for declared in (False, True):
        p, shell, page, base = prepare(tmp / str(declared), declared)
        for text, red in [('{% block scripts %}{% endblock %}', True), (SCRIPT, True),
                          ('<link rel="stylesheet" href="x.css">', True),
                          ('{{ state.data|json_script:"data" }}', False), ('<script type="application/json">{}</script>', False),
                          ('{% block title %}{% endblock %}', True), ('{% block title %} {# empty #} {% endblock %}', True),
                          ('{% block title %}{{ state.title }}{% endblock %}', False)]:
            p.reset(base)
            p.append('web/' + page, text)
            expect(p, base, 'sh3', red, 'Z3 added 자산·제목(%s %s)' % (declared, text[:30]), page if red else None)
        p.reset(base)
        p.append('web/' + page, '{% block scripts %}' + SCRIPT + '{% endblock %}')
        badbase = p.commit('old-block')
        p.append('web/' + page, '<p>new</p>')
        expect(p, badbase, 'sh3', False, 'Z3 기존 block 침묵')
        p.w('web/' + shell, '<html><body></body></html>')
        off = p.commit('shell-off')
        p.w('web/' + shell, shell_text(shell, paths_for(p, shell)))
        expect(p, off, 'sh3', True, 'Z3 켜는 diff 전수', page)
        # 새 include 는 기존 대상·그 부모·상대 부모까지 파일 전체를 검사한다.
        p.reset(base)
        p.w('web/legacy/card.html', '{% extends "./card_base.html" %}')
        p.w('web/legacy/card_base.html', SCRIPT)
        p.w('web/legacy/widget.html', SCRIPT)
        old = p.commit('old-targets')
        p.append('web/' + page, '{% include "legacy/card.html" %}')
        expect(p, old, 'sh3', True, 'Z3 include 뒤 상대 상속', 'legacy/card_base.html')
        p.reset(old)
        p.append('web/' + page, '{% include "legacy/widget.html" %}')
        expect(p, old, 'sh3', True, 'Z3 새 include 기존 대상', 'legacy/widget.html')
        p.reset(old)
        p.w('web/legacy/standalone.html', '<head>' + SCRIPT + '</head>')
        p.w('web/' + page, '{% extends "legacy/standalone.html" %}', '{% include "legacy/widget.html" %}')
        before = p.commit('old-parent')
        p.sub('web/' + page, 'legacy/standalone.html', shell)
        expect(p, before, 'sh3', True, 'Z3 extends 한 줄이 페이지 닫힘 전수', 'legacy/widget.html')
        p.reset(old)
        p.w('web/base/base.html', '{% extends "legacy/standalone.html" %}')
        p.w('web/legacy/standalone.html', '<head>' + SCRIPT + '</head>')
        p.w('web/legacy/view/page.html', '{% extends "base/base.html" %}', '{% block head %}{% endblock %}',
            '{% include "legacy/widget.html" %}')
        before = p.commit('old-chain')
        p.sub('web/base/base.html', 'legacy/standalone.html', shell)
        expect(p, before, 'sh3', True, 'Z3 사슬 아래 페이지 전수', 'legacy/view/page.html')
        expect(p, before, 'sh3', True, 'Z3 사슬 아래 include 닫힘 전수', 'legacy/widget.html')
        p.reset(old)
        p.w('web/legacy/standalone.html', '<head>' + SCRIPT + '</head>')
        p.w('web/' + page, '{% extends "legacy/standalone.html" %}')
        expect(p, old, 'sh3', False, 'Z3 소속만 있는 페이지 문서 부모 오탐 없음')
        p.reset(old)
        p.append('web/' + page, '{% include "./part.html" %}')
        part = page.rsplit('/', 1)[0] + '/part.html'
        p.w('web/' + part, '{% extends "../base.html" %}')
        parent = page.rsplit('/', 2)[0] + '/base.html'
        p.w('web/' + parent, SCRIPT)
        expect(p, old, 'sh3', True, 'Z3 상대 include·부모', parent)
        for text in ('{% extends base_var %}', '{% include card_var %}',
                     '{% include "./empty.html" %}{% include card_var %}', '{% include "../../../outside.html" %}',
                     '{% extends "./tree_node.html" %}'):
            p.reset(old)
            p.append('web/' + page, '{% include "legacy/tree_node.html" %}')
            p.w('web/legacy/tree_node.html', text)
            got = expect(p, old, 'sh3', False, 'Z3 동적·뿌리 밖·자기 extends 알림')
            check('Z3 판독 불가 원문 행', '[info]' in got[1] and '판독 불가' in got[1] and 'legacy/tree_node.html:1' in got[1], got)
        p.reset(old)
        p.append('web/' + page, '{% include "legacy/tree_node.html" %}')
        p.w('web/legacy/tree_node.html', '{% if depth %}{% include "./tree_node.html" %}{% endif %}')
        got = expect(p, old, 'sh3', False, 'Z3 자기 include 방문 집합')
        check('Z3 자기 include 판독 불가 아님', '판독 불가' not in got[1], got)
    p, shell, page, base = prepare(tmp / 'move', True)
    p.append('web/' + ORDER_PAGE, SCRIPT)
    base = p.commit('old-other-product')
    registry = json.loads(p.read(REGISTRY))
    registry['products']['operator']['bcs'] = []
    p.w(REGISTRY, json.dumps(registry))
    expect(p, base, 'sh3', True, 'Z3 선언으로 BC 이동 전수', ORDER_PAGE)


def bundle_z3_verbatim(tmp):
    for declared in (False, True):
        p, shell, page, base = prepare(tmp / str(declared), declared)
        p.w('web/legacy/widget.html', SCRIPT)
        old = p.commit('old-verbatim-target')
        for opening, closing in (('{% verbatim %}', '{% endverbatim %}'),
                                 ('{% verbatim sample %}', '{% endverbatim sample %}'),
                                 ('{%verbatim  sample%}', '{%endverbatim  sample%}')):  # 안쪽 공백까지 같은 짝
            label = '%s %s' % (declared, opening)
            for body, red in [('{% include "legacy/widget.html" %}', False),
                              ('{% extends "legacy/widget.html" %}', False),
                              ('{% block scripts %}{% endblock %}', False),
                              ('{% block head %}{% endblock %}', False),
                              ('{% block title %}{% endblock %}', False),
                              ('{% include card_var %}', False), (SCRIPT, True)]:
                p.reset(old)
                p.sub('web/' + page, '{% block content %}', '{% block content %}\n' + opening + body + closing)
                got = expect(p, old, 'sh3', red, 'Z3 verbatim 지시문·HTML(%s %s)' % (label, body[:30]), page if red else None)
                if body == '{% include card_var %}':
                    check('Z3 verbatim 동적 include 판독 불가 아님 ' + label, '판독 불가' not in got[1], got)
            p.reset(old)
            p.sub('web/' + page, '{% block content %}', '{% block content %}\n' + opening +
                  '{% include "legacy/widget.html" %}' + closing + '\n{% include "legacy/widget.html" %}')
            expect(p, old, 'sh3', True, 'Z3 verbatim 밖 실제 include ' + label, 'legacy/widget.html')
            p.reset(old)
            p.sub('web/' + shell, '</head>', opening + '{% block scripts %}{% endblock %}' + closing + '</head>')
            expect(p, old, 'sh2', False, 'Z2 verbatim 안 block 정의 제외 ' + label)
        p.reset(old)
        p.sub('web/' + page, '{% block content %}', '{% block content %}\n{% verbatim sample %}' +
              '{% endverbatim other %}{% include "legacy/widget.html" %}{% endverbatim sample %}')
        expect(p, old, 'sh3', False, 'Z3 이름 다른 endverbatim 은 글자(%s)' % declared)
        # 토큰 경계와 verbatim 끝은 Django Lexer 와 같게 읽는다 — 실제로 렌더되는 include 만 간선이다.
        include = '{% include "legacy/widget.html" %}'
        for name, body, red in [
                ('HTML 주석 속 endverbatim 은 구간을 끝낸다', '{% verbatim %}<!-- {% endverbatim %} -->\n' + include, True),
                ('Django 주석 속 endverbatim 은 글자', '{% verbatim %}{# {% endverbatim %} #}' + include + '{% endverbatim %}', False),
                ('변수 토큰 속 verbatim 은 시작이 아니다', '{{ "{% verbatim %}" }}' + include, True),
                ('변수 토큰 속 include 는 글자', '{{ "{% include \'legacy/widget.html\' %}" }}', False),
                ('안쪽 공백이 다른 endverbatim 은 글자',
                 '{% verbatim sample %}\n{% endverbatim  sample %}' + include + '\n{% endverbatim sample %}', False),
                ('안쪽 공백이 다른 endverbatim 뒤 block 도 글자',
                 '{% verbatim sample %}\n{% endverbatim  sample %}{% block scripts %}{% endblock %}\n{% endverbatim sample %}', False),
                ('여러 줄에 걸친 include 글자는 지시문이 아니다', '{% include\n"legacy/widget.html" %}', False)]:
            p.reset(old)
            p.sub('web/' + page, '{% block content %}', '{% block content %}\n' + body)
            expect(p, old, 'sh3', red, 'Z3 Lexer 경계 — %s(%s)' % (name, declared), 'legacy/widget.html' if red else None)
        # 실제 지시문 토큰 안의 글자는 그대로다 — 이름에 `{%` 가 든 템플릿도 따라간다.
        p.reset(old)
        p.w('web/legacy/{%/widget.html', SCRIPT)
        odd = p.commit('old-odd-name-target')
        p.sub('web/' + page, '{% block content %}', '{% block content %}\n{% include "legacy/{%/widget.html" %}')
        expect(p, odd, 'sh3', True, 'Z3 Lexer 경계 — 실제 include 인자 안의 `{%% ` 글자 보존(%s)' % declared, 'legacy/{%/widget.html')
        p.reset(old)
        p.sub('web/' + shell, '</head>', '{% verbatim sample %}{% endverbatim  sample %}{% block scripts %}{% endblock %}' +
              '{% endverbatim sample %}</head>')
        expect(p, old, 'sh2', False, 'Z2 Lexer 경계 — 안쪽 공백이 다른 endverbatim 뒤 block 정의 제외(%s)' % declared)
        p.reset(old)
        p.sub('web/' + shell, '</head>', '{% verbatim %}<!-- {% endverbatim %} --></head>')
        expect(p, old, 'sh2', False, 'Z2 Lexer 경계 — HTML 주석 속 endverbatim 뒤 content block 은 실제 정의(%s)' % declared)
        # 가짜 extends 는 옛 배치 파일을 지속 셸 상속 사슬·SH1 화면 허용 범위에 들이지 않는다.
        p.reset(old)
        p.w('web/legacy/view/literal.html', '{% verbatim sample %}{% extends "' + shell + '" %}{% endverbatim sample %}',
            '<a href="/" hx-boost="true">x</a>')
        expect(p, old, 'sh1', True, 'Z1 verbatim extends 가짜 소속(%s)' % declared, 'legacy/view/literal.html')
        # HTML 표지와 CSS 로드 태그는 verbatim 안에서도 실제 출력이다.
        p.reset(old)
        p.w('web/' + shell, '{% verbatim sample %}<main hx-history-elt></main>{% endverbatim sample %}')
        expect(p, old, 'sh2', True, 'Z2 verbatim HTML 후보 표지 유지(%s)' % declared, shell)
        p.reset(old)
        p.w('web/static/application/order/literal.css', 'h2 {}')
        p.sub('web/' + shell, '</head>', '{% verbatim sample %}' + load('static/application/order/literal.css') +
              '{% endverbatim sample %}</head>')
        expect(p, old, 'sh5', True, 'Z5 verbatim HTML CSS 로드 유지(%s)' % declared, 'static/application/order/literal.css')


def install_sdk(p):
    # 기존 SDK 픽스처의 fake fetch(table)를 그대로 쓴다 — 네트워크 0.
    got = subprocess.run([sys.executable, '-B', str(TEST / 'sdk_fixture.py'), 'install', str(p.root), '--no-commit'],
                         capture_output=True, text=True, env=ENV)
    if got.returncode:
        raise RuntimeError(got.stdout + got.stderr)


def bundle_z4(tmp):
    old = baseline_scripts(tmp / 'old')
    p, shell, page, base = prepare(tmp / 'assets')
    good = p.read('web/' + shell)
    p.append('web/' + shell, '')
    expect(p, base, 'sh4', False, 'Z4 완전 머리 · root_shell 기능 묶음에서 제외')
    for label, text in [('빠짐', good.replace(load('static/js/root_shell.js'), '')),
                        ('중복', good.replace('</head>', load('static/js/root_shell.js') + '</head>')),
                        ('순서', good.replace(load('static/htmx/htmx.min.js') + '\n' + load('static/js/root_shell.js'),
                                             load('static/js/root_shell.js') + '\n' + load('static/htmx/htmx.min.js'))),
                        ('없는 파일', good.replace('</head>', load('static/js/missing.js') + '</head>'))]:
        p.reset(base)
        p.w('web/' + shell, text)
        got = expect(p, base, 'sh4', True, 'Z4 ' + label, shell)
        if label == '빠짐':
            check('Z4 넣을 줄 원문·꼬리', '넣을 줄' in got[1] and load('static/js/root_shell.js') in got[1], got)
    for operation in ('added', 'deleted', 'renamed'):
        p.reset(base)
        path = 'web/static/application/order/order_list_view.css'
        if operation == 'added':
            p.w('web/static/application/order/extra.css', '.order-extra {}')
        elif operation == 'deleted':
            p.rm(path)
        else:
            p.mv(path, 'web/static/application/order/renamed.css')
        expect(p, base, 'sh4', True, 'Z4 CSS ' + operation, shell)
    p.reset(base)
    p.w('web/static/css/legacy.css', '.legacy {}')
    p.sub('web/' + shell, '<meta name="htmx-config"', load('static/css/legacy.css') + '\n<meta name="htmx-config"')
    expect(p, base, 'sh4', True, 'Z4 옛 배치 자산도 theme 뒤', shell)
    for version, red in [('var htmx={version:"2.0.9"};', True), ('var htmx={version: \'2.0.10\'};', False),
                         ('var htmx={};', True)]:
        p.reset(base)
        p.w('web/static/htmx/htmx.min.js', version)
        got = expect(p, base, 'sh4', red, 'Z4 core 판 ' + version, shell if red else None)
        if 'version' not in version:
            check('Z4 core 판 못 읽음 교정', 'core 판을 읽지 못함 — 지속 셸은 2.0.10 확인이 필요' in got[1], got)
            check('Z4 PJ2 출력 무변', backstop(p.root, '--all', '--only', 'pj2')[0] == 0)
            if old:
                check('Z4 PJ2 못 읽는 판 바탕과 byte 동일',
                      normalized(backstop(p.root, '--all', '--only', 'pj2')) ==
                      normalized(backstop(p.root, '--all', '--only', 'pj2', scripts=old)))
    p.reset(base)
    p.mv('web/static/htmx/htmx.min.js', 'web/static/js/htmx.js')
    p.sub('web/' + shell, 'web/htmx/htmx.min.js', 'web/js/htmx.js')
    legacy = p.commit('legacy-core')
    p.append('web/' + shell, '')
    expect(p, legacy, 'sh4', False, 'Z4 브라운필드 core 기능 묶음에서 제외')
    p, shell, page, base = prepare(tmp / 'sdk')
    install_sdk(p)
    p.w('web/static/js/sample.js', 'window.Kakao.init();')
    expect(p, base, 'sh4', True, 'Z4 SDK·기능 JS 빠짐', shell)
    p.sub('web/' + shell, '</head>', load(SDK) + '\n' + load('static/js/sample.js') + '\n</head>')
    expect(p, base, 'sh4', False, 'Z4 SDK·기능 JS 정렬')
    p.w('web/static/js/sample.js', 'console.log("quiet");')
    p.sub('web/' + shell, load(SDK) + '\n', '')
    quiet = p.commit('no-consumer')
    p.sub('web/' + shell, '</head>', load(SDK) + '\n</head>')
    expect(p, quiet, 'sh4', True, 'Z4 선택 SDK 도 기능 JS 앞', shell)
    expect(p, quiet, 'sh2', True, 'Z2 꼴 4 선택 SDK·기능 JS 순서', shell)
    p.reset(quiet)
    p.sub('web/' + shell, load('static/js/sample.js'), load(SDK) + '\n' + load('static/js/sample.js'))
    expect(p, quiet, 'sh4', False, 'Z4 선택 SDK 정렬된 자리')
    p.reset(quiet)
    p.append('web/static/js/sample.js', 'window.Kakao.init();')
    expect(p, quiet, 'sh4', True, 'Z4 기존 JS SDK 참조 한 줄 added', shell)
    p, shell, page, base = prepare(tmp / 'move', True)
    registry = json.loads(p.read(REGISTRY))
    registry['products']['operator']['bcs'] = []
    p.w(REGISTRY, json.dumps(registry))
    expect(p, base, 'sh4', True, 'Z4 선언으로 BC 자산 이동', shell)


def bundle_z5(tmp):
    p, shell, page, base = prepare(tmp / 'css')
    css = 'static/application/order/order_list_view.css'
    for text, red, info in [('body {}', True, False), ('h2 {}', True, False), (':root {}', True, False),
                            ('* {}', True, False), ('::selection {}', True, False),
                            ('@keyframes x { from {} to {} }', False, False), ('@font-face { font-family: x; }', False, False),
                            ('@property --x { syntax: "<color>"; }', False, False), ('@counter-style x { system: cyclic; }', False, False),
                            ('@media (width > 1px) { h2 {} }', True, False), ('.a, h2 {}', True, False),
                            (':is(.a, .b) .c {}', False, True), (':where(.a) .b {}', False, True),
                            ('.x.htmx-request {} .x--on {} .x__item {}', False, False),
                            ('.primary-button--wide {}', True, False)]:
        p.reset(base)
        p.w('web/' + css, text)
        got = expect(p, base, 'sh5', red, 'Z5 ' + text, css if red else None)
        check('Z5 판독 불가 여부 ' + text, ('판독 불가' in got[1]) == info, got)
    p.reset(base)
    p.w('web/design_system/util/global.css', 'html {}')
    p.sub('web/' + shell, load('static/application/order/order_list_view.css'),
          load('design_system/util/global.css') + '\n' + load('static/application/order/order_list_view.css'))
    expect(p, base, 'sh5', True, 'Z5 util 맨 선택자', 'design_system/util/global.css')
    p.reset(base)
    p.w('web/static/application/order/extra.css', '.order-list__item {}')
    p.sub('web/' + shell, load(css), load('static/application/order/extra.css') + '\n' + load(css))
    expect(p, base, 'sh5', True, 'Z5 두 파일 같은 BEM block')
    landed = p.commit('old-overlap')
    p.append('web/' + css, '.new-block {}')
    expect(p, landed, 'sh5', False, 'Z5 손대지 않은 기존 선택자 침묵')
    p.reset(base)
    p.append('web/design_system/foundation/app_color.css', ':root {}')
    p.append('web/design_system/theme/app_theme.css', 'body {}')
    expect(p, base, 'sh5', False, 'Z5 foundation·theme 제외')
    p.reset(base)
    p.w('web/' + css, '.x,', 'h2 {}')
    landed = p.commit('old-bare-branch')
    p.w('web/' + css, '.x,', '.new-branch,', 'h2 {}')
    expect(p, landed, 'sh5', False, 'Z5 새 목록 갈래만 검사 · 기존 맨 갈래 침묵')
    p.reset(base)
    p.w('web/' + css, '.book-cover-widget {}')
    p.w('web/static/application/lobby/lobby_view.css', '.book-cover-widget__cover {}')
    p.sub('web/' + shell, load(css), load('static/application/lobby/lobby_view.css') + '\n' + load(css))
    expect(p, base, 'sh5', True, 'Z5 두 BC 같은 book-cover-widget block')


def bundle_z6(tmp):
    old = baseline_scripts(tmp / 'old')
    p, shell, page, base = prepare(tmp / 'pu', True)
    install_sdk(p)
    p.w('web/static/js/sample.js', 'window.Kakao.init();')
    p.sub('web/' + shell, '</head>', load(SDK) + '\n' + load('static/js/sample.js') + '\n</head>')
    expect(p, base, 'pu2', False, 'Z6 own 지속 셸 SDK·기능 JS·꼬리')
    if old:
        got = backstop(p.root, '--diff-base', base, '--only', 'pu2', scripts=old)
        check('Z6 바탕 러너는 지속 셸 꼬리 붉음', got[0] == 2 and found(got[1], 'PU2', shell), got)
    p.sub('web/' + shell, load(SDK) + '\n' + load('static/js/sample.js'), load('static/js/sample.js') + '\n' + load(SDK))
    got = expect(p, base, 'pu2', True, 'Z6 지속 셸 SDK 교정 문구', shell)
    check('Z6 교정 문구 셸 head', '셸 `<head>`' in got[1], got)
    for file in (shell, page):
        p.reset(base)
        install_sdk(p)
        p.w('web/' + shell, '<html><head></head><body>{% block content %}{% endblock %}</body></html>')
        p.append('web/' + file, load(SDK))
        got = expect(p, base, 'pu2', True, 'Z6 문서 이동 셸·페이지 꼬리 거절 ' + file, file)
        check('Z6 정확한 static 위반', '정확한 `{% static %}`' in got[1], got)
        if old:
            check('Z6 문서 이동 꼬리 출력 바탕과 동일 ' + file, normalized(got) ==
                  normalized(backstop(p.root, '--diff-base', base, '--only', 'pu2', scripts=old)))


def bundle_z7(tmp):
    p, shell, page, base = prepare(tmp / 'runner', persistent=False)
    got = backstop(p.root, '--diff-base', base)
    check('Z7 합계 정확', got[0] == 0 and '[backstop] 검사 93종' in got[1], got)
    got = backstop(p.root, '--diff-base', base, '--slice-end')
    check('Z7 슬라이스 끝 정확', got[0] == 0 and '검사 93종 중 86종(슬라이스 끝 — 미룸 7:' in got[1], got)
    expect(p, base, 'sh', False, 'Z7 --only sh')
    got = backstop(p.root, '--only', 'shx')
    check('Z7 알 수 없는 패밀리', got[0] == 1 and '알 수 없는 --only 값 shx' in got[1], got)
    usage = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'backstop.py')], capture_output=True, text=True, env=ENV)
    check('Z7 사용 줄 sh', usage.returncode == 1 and ',pu,sh,cs,wv]' in usage.stderr, usage.stderr)


def bundle_z8(tmp):
    p, shell, page, base = prepare(tmp / 'inflow')
    git(p.root, 'checkout', '-qb', 'lane')
    p.w('lane.txt', 'lane')
    p.commit('lane')
    folder = p.root / '.dddjango-web/build'
    folder.mkdir(parents=True)
    (folder / 'build-state.json').write_text(json.dumps({'git_snapshot': base, 'slices': []}))
    git(p.root, 'checkout', '-q', 'main')
    p.sub('web/' + shell, '채널', '새 채널')
    p.commit('upstream-head')
    git(p.root, 'checkout', '-q', 'lane')
    git(p.root, 'merge', '--no-ff', '-q', '-m', 'receive', 'main')
    (folder / 'approved-merges.txt').write_text(git(p.root, 'rev-parse', 'HEAD') + ' main\n')
    p.w('web/static/application/order/extra.css', '.order-extra {}')
    p.commit('lane-forgot-head')
    got = backstop(p.root, '--diff-base', base, '--only', 'sh4', '--design-build', folder)
    blocker, _, approved = got[1].partition('== 승인 유입(')
    check('Z8 SH4 가름 제외 · exit 2 · L 증명 없음', got[0] == 2 and found(blocker, 'SH4', shell)
          and '가름 제외 검사' in blocker and '[SH4]' not in approved, got)


def rule_block(text, lang, head):
    """규칙 글에서 머리 줄로 시작하는 코드 블록 하나 — 없거나 둘 이상이면 픽스처가 실패한다(조용히 건너뛰지 않는다)."""
    blocks = [m.group(1) for m in re.finditer(r'^```' + lang + r'\n(.*?)\n```$', text, re.S | re.M)
              if m.group(1).startswith(head)]
    if len(blocks) != 1:
        raise RuntimeError('규칙 글 %s 블록 %r — %d 개(하나여야 한다)' % (lang, head, len(blocks)))
    return blocks[0]


def standard_files():
    """규칙 글의 지속 셸 root_view.html · root_tab_state.py · root_state.py 블록 — foundation 자리표 한 줄만 여섯 줄로."""
    text = RULE.read_text(encoding='utf-8')
    template = rule_block(text, 'django', '{# root/scaffold/view/root_view.html — 지속 셸')
    lines = template.split('\n')
    holder = [i for i, line in enumerate(lines) if line.strip() == '{# … foundation 나머지 여섯 … #}']
    color = [line for line in lines if '/foundation/app_color.css' in line]
    if len(holder) != 1 or len(color) != 1:
        raise RuntimeError('규칙 글 지속 셸 블록의 foundation 줄 꼴이 바뀜 — 자리표 %d · color 줄 %d' % (len(holder), len(color)))
    lines[holder[0]:holder[0] + 1] = [color[0].replace('app_color.css', 'app_%s.css' % t) for t in TOKENS[1:]]
    return {'web/' + FLAT_SHELL: '\n'.join(lines) + '\n',
            'web/root/scaffold/state/root_tab_state.py':
                rule_block(text, 'python', '# root/scaffold/state/root_tab_state.py') + '\n',
            'web/root/scaffold/state/root_state.py':
                rule_block(text, 'python', '# root/scaffold/state/root_state.py — 지속 셸이면') + '\n'}


def bundle_standard(tmp):
    files = standard_files()
    p = mkstd(tmp / 'standard')
    # 표준 글의 셸이 싣지 않는 바탕 CSS 는 걷는다 — 공유 머리는 그 제품 CSS 전부를 요구한다(SH4).
    p.rm('web/static/application/order/order_list_view.css')
    p.rm('web/design_system/component/button/primary_button.css')
    # 표준 글의 셸이 싣는 조각 CSS(channel_summary_view.css)의 주인 화면 — 조각 CSS 는 같은 stem 의 템플릿 곁에만(NM19).
    mkbc(p, 'application/channel', page=False)
    view = 'web/application/channel/presentation_layer/view/channel_summary_view'
    p.w(view + '.py', 'from django.http import HttpRequest, HttpResponse', 'from django.shortcuts import render', '', '',
        'def channel_summary_view(request: HttpRequest) -> HttpResponse:',
        '    return render(request, "%s.html", {})' % view[len('web/'):])
    p.w(view + '.html', '{% extends "' + FLAT_SHELL + '" %}', '{% block content %}', '<p>channel</p>', '{% endblock %}')
    base = p.commit('document-base')
    for rel, text in files.items():
        (p.root / rel).write_text(text, encoding='utf-8')
    shell = files['web/' + FLAT_SHELL]
    for arg in re.findall(r"\{% static '([^']+)' %\}", shell):
        rel = 'web/static/' + arg[len('web/'):] if arg.startswith('web/') else 'web/' + arg
        if (p.root / rel).exists():
            continue
        if rel.endswith('.css'):
            block = 'root-tab-bar' if rel.endswith('/static/root/root_view.css') else Path(rel).stem.replace('_', '-')
            p.w(rel, '.%s { color: var(--color-base); }' % block)
        else:
            p.w(rel, 'document.addEventListener("htmx:load", () => {});')
    for args in (('--all',), ('--diff-base', base)):
        got = backstop(p.root, *args, '--only', 'sh,nm')
        check('표준 글 그대로 지속 셸 SH·NM blocker 0(%s)' % args[0],
              got[0] == 0 and 'BLOCKER' not in got[1] and '내부 오류' not in got[1], got)


def bundle_z2_tabs(tmp):
    nav = '<div id="root-tab-items" class="root-tab-bar__items">\n'
    for declared in (False, True):
        p, shell, page, base = prepare(tmp / str(declared), declared)
        good = p.read('web/' + shell)
        if good.count(nav + TABS) != 1:
            raise RuntimeError('픽스처 오류 — nav 탭 목록 자리')
        deeper = nav + '\n'.join('      ' + line for line in TABS.split('\n'))
        p.w('web/' + shell, good.replace(nav + TABS, deeper))
        expect(p, base, 'sh2', False, 'Z2 꼴 9 들여쓰기만 다른 두 벌(%s)' % declared)
        p.w('web/' + shell, good.replace(nav + TABS, deeper.replace('{{ tab.label }}', '{{ tab.name }}')))
        got = expect(p, base, 'sh2', True, 'Z2 꼴 9 글자 다른 두 벌(%s)' % declared, shell)
        check('Z2 꼴 9 문구(%s)' % declared, '꼴 9' in got[1], got)


def bundle_z4_legacy(tmp):
    for legacy in ('static/js/htmx.min.js', 'static/js/htmx.js'):
        name = Path(legacy).name
        p, shell, page, base = prepare(tmp / name)
        p.mv('web/static/htmx/htmx.min.js', 'web/' + legacy)
        p.sub('web/' + shell, 'web/htmx/htmx.min.js', 'web/js/' + name)
        p.commit('legacy-core')
        for args in (('--all',), ('--diff-base', 'HEAD', '--all')):
            got = backstop(p.root, *args, '--only', 'sh')
            check('Z4 옛 자리 core %s SH 0(%s)' % (name, ' '.join(args)), got[0] == 0 and '[SH' not in got[1], got)
        non = tmp / ('non-' + name)
        shutil.copytree(p.root, non, ignore=shutil.ignore_patterns('.git'))
        got = backstop(non, '--only', 'sh')
        check('Z4 옛 자리 core %s 비git SH 0' % name,
              got[0] == 0 and 'git 저장소 아님' in got[1] and '[SH' not in got[1], got)
        # 기준점이 있는 게이트에서 옛 자리에 새로 놓은 core 는 core 로 보지 않는다(새 설치는 static/htmx 만).
        p.reset(base)
        p.mv('web/static/htmx/htmx.min.js', 'web/' + legacy)
        p.sub('web/' + shell, 'web/htmx/htmx.min.js', 'web/js/' + name)
        expect(p, base, 'sh4', True, 'Z4 기준점 게이트 옛 자리 새 core 붉음 ' + name, shell)


def bundle_z4_order(tmp):
    p, shell, page, base = prepare(tmp / 'order')
    good = p.read('web/' + shell)
    convention = '\n'.join(load('design_system/foundation/app_%s.css' % t) for t in TOKENS)
    if convention not in good:
        raise RuntimeError('픽스처 오류 — foundation 관례 순 일곱 줄')
    p.append('web/' + shell, '')
    expect(p, base, 'sh4', False, 'Z4 foundation 관례 순 일곱')
    p.w('web/' + shell, good.replace(convention, '\n'.join(load('design_system/foundation/app_%s.css' % t)
                                                          for t in sorted(TOKENS))))
    got = expect(p, base, 'sh4', True, 'Z4 foundation 알파벳 순 일곱', shell)
    check('Z4 foundation 순서 위반 문구', '공유 머리 묶음·경로 순서 위반' in message_of(got[1], 'SH4', shell), got)
    fix = fix_of(got[1], 'SH4', shell)
    positions = [fix.find('/foundation/app_%s.css' % t) for t in TOKENS]
    check('Z4 교정 줄 foundation 관례 순', -1 not in positions and positions == sorted(positions), fix)


PARSER_WRAPPER = '''import html.parser
import runpy
import sys

_original = html.parser.HTMLParser.parse_html_declaration


def _unreadable(self, i):  # 파이썬 3.9 의 `<![foo` 파서 예외를 판과 무관하게 흉내 낸다
    if self.rawdata.startswith('<![foo', i):
        raise NotImplementedError('subclasses of ParserBase must override error()')
    return _original(self, i)


html.parser.HTMLParser.parse_html_declaration = _unreadable
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
'''


def bundle_minor(tmp):
    p, shell, page, base = prepare(tmp / 'minor')
    p.w('web/legacy/widget.html', SCRIPT)
    old = p.commit('widget')
    # 사소 1 — 글자 인자 뒤 인자에 % 가 있어도 include 간선을 따른다.
    p.append('web/' + page, '{% include "legacy/widget.html" with width="50%" %}')
    expect(p, old, 'sh3', True, '사소 1 % 든 인자의 include 간선', 'legacy/widget.html')
    # 사소 3 — 값 있는 hx-history-elt 는 붉음 그대로 · 문구가 까닭을 알린다.
    p.reset(old)
    good = p.read('web/' + shell)
    p.w('web/' + shell, good.replace(' hx-history-elt>', ' hx-history-elt="true">'))
    got = expect(p, old, 'sh2', True, '사소 3 값 있는 hx-history-elt', shell)
    check('사소 3 문구 값 없이', '값 없이 쓴다' in message_of(got[1], 'SH2', shell), got)
    # 사소 5 — 게이트에서 새로 추가된 지속 셸에는 «기준점 본문 없음» 알림을 내지 않는다(--all 은 냄).
    p.reset(old)
    p.rm('web/' + shell)
    gone = p.commit('no-shell')
    p.w('web/' + shell, good)
    got = expect(p, gone, 'sh2', False, '사소 5 새 지속 셸 게이트')
    check('사소 5 새 파일 기준점 알림 없음', '기준점 본문 없음' not in got[1], got)
    got = backstop(p.root, '--all', '--only', 'sh2')
    check('사소 5 --all 기준점 알림 하나', got[0] == 0 and got[1].count('기준점 본문 없음 — 표지 걷음 판정 생략') == 1, got)
    # 사소 4 — 파서 예외는 러너를 죽이지 않고 그 파일을 판독 불가로 내린다.
    wrapper = tmp / 'unreadable_parser.py'
    wrapper.write_text(PARSER_WRAPPER, encoding='utf-8')

    def emulated(root, *args):
        r = subprocess.run([sys.executable, '-B', str(wrapper), str(SCRIPTS / 'backstop.py'), str(root), *args],
                           capture_output=True, text=True, env=ENV)
        return r.returncode, r.stdout + r.stderr

    q, _qshell, qpage, qbase = prepare(tmp / 'document', persistent=False)
    q.append('web/' + qpage, '<p><![foo]></p>')
    got = emulated(q.root, '--diff-base', qbase)
    check('사소 4 표지 없는 호스트 판독 불가 info · 러너 생존', got[0] == 0 and '내부 오류' not in got[1]
          and '[info] SH 판독 불가 — web/' + qpage in got[1] and '[SH' not in got[1], got)
    p.reset(old)
    p.append('web/' + page, '<p><![foo]></p>')
    got = emulated(p.root, '--diff-base', old, '--only', 'sh')
    check('사소 4 지속 셸 제품 페이지 판독 불가 info', got[0] == 0 and '[info] SH 판독 불가 — web/' + page in got[1], got)
    p.reset(old)
    p.append('web/' + page, '{% block scripts %}{% endblock %}<![foo]>')
    got = emulated(p.root, '--diff-base', old, '--only', 'sh3')
    check('사소 4 판독 불가 페이지의 block 검사는 그대로', got[0] == 2 and found(got[1], 'SH3', page), got)
    p.reset(old)
    p.sub('web/' + shell, '</head>', '<![foo]></head>')
    got = emulated(p.root, '--diff-base', old, '--only', 'sh2')
    check('사소 4 지속 셸 판독 불가 붉음', got[0] == 2 and found(got[1], 'SH2', shell)
          and '판독 불가' in message_of(got[1], 'SH2', shell), got)
    for python in (sys.executable, '/usr/bin/python3'):
        if not Path(python).exists():
            continue
        probe = subprocess.run([python, '-c', 'import html.parser as h; h.HTMLParser().feed("<![foo]>")'],
                               capture_output=True, env=ENV)
        r = subprocess.run([python, '-B', str(SCRIPTS / 'backstop.py'), str(q.root), '--diff-base', qbase, '--only', 'sh'],
                           capture_output=True, text=True, env=ENV)
        out = r.stdout + r.stderr
        check('사소 4 실제 글자 러너 생존(%s)' % python, r.returncode == 0 and '내부 오류' not in out
              and ('판독 불가' in out) == bool(probe.returncode), (probe.returncode, r.returncode, out))


# F4-91 바로 앞 배포판(dddjango-web 2.4.3) — SH1 밖 출력 대조의 옛 러너. HEAD 로 잡으면 커밋 뒤 새 판 자신이 된다.
DRAWN_BASELINE = '1328eba4'
BOOST = '<a href="/next/" hx-boost="true">next</a>'


def drawn_project(tmp, declared):
    """F4-91 경우표 — 지속 셸 화면이 그리는 조각. 이름 → (파일, SH1 붉음)."""
    p, shell, page, _ = prepare(tmp, declared)
    bc = page.split('/presentation_layer/')[0]
    stem = bc.rsplit('/', 1)[1]
    concept = bc + '/presentation_layer/%s_pick/' % stem
    cases, drawn = {}, []

    def case(name, file, red, text=None, include=True):
        cases[name] = (file, red)
        if text is not None:
            p.w('web/' + file, text)
        if include:
            drawn.append(file)

    def inc(file):
        return '{% include "' + file + '" %}'

    view = concept + 'view/%s_pick_view.html' % stem
    section = concept + 'section/%s_pick_card_section.html' % stem
    p.w('web/' + view, '{% extends "' + shell + '" %}', '{% block title %}pick{% endblock title %}',
        '{% block content %}' + inc(section) + '{% endblock content %}')
    case('① 개념 폴더 section', section, False, '<div>card</div>', False)
    case('개념 폴더 view 화면 자체', view, False, None, False)
    p.w('web/parlor/talk/section/talk_mount.html', inc('parlor/talk/section/talk_header.html'))
    p.w('web/parlor/talk/section/talk_header.html', '<header>' + inc('parlor/talk/section/talk_back_link_section.html') + '</header>')
    drawn.append('parlor/talk/section/talk_mount.html')
    case('② 옛 배치 include 세 단', 'parlor/talk/section/talk_back_link_section.html', False, '<span>back</span>', False)
    case('include 안 된 옛 조각(hx-get 응답 포함 — 한계)', 'parlor/stray/stray_link.html', True, '<span>stray</span>', False)
    case('design_system 부품', 'design_system/component/button/primary_button.html', True)
    case('개념 폴더 두 단', bc + '/presentation_layer/a_pick/b_sub/section/deep_section.html', True, '<span>deep</span>')
    case('view/x/section 씨앗', bc + '/presentation_layer/view/x/section/odd_section.html', False, '<span>odd</span>', False)
    case('변수 include 대상(한계)', 'parlor/var/var_part.html', True, '<span>var</span>', False)
    p.w('web/parlor/layout/doc_base.html', '<html><body>' + inc('parlor/layout/doc_nav.html'),
        '{% block content %}{% endblock content %}</body></html>')
    p.w('web/parlor/doc/view/doc_page.html', '{% extends "parlor/layout/doc_base.html" %}',
        '{% block content %}' + inc('parlor/docpart/doc_only.html') + '{% endblock content %}')
    p.w('web/parlor/card/card.html', '{% extends "parlor/layout/doc_base.html" %}', '{% block content %}c{% endblock content %}')
    drawn.append('parlor/card/card.html')
    case('include 대상이 extends 하는 옛 문서 레이아웃의 조각', 'parlor/layout/doc_nav.html', True, '<nav>n</nav>', False)
    case('옛 문서 레이아웃만 그리는 조각', 'parlor/docpart/doc_only.html', True, '<span>doc</span>', False)
    p.w('web/parlor/rel/rel_mid.html', '{% include "./rel_part.html" with a=1 only %}')
    drawn.append('parlor/rel/rel_mid.html')
    case('상대 경로 · with only include', 'parlor/rel/rel_part.html', False, '<span>rel</span>', False)
    p.w('web/parlor/cardbase/card_base.html', '<div>' + inc('parlor/cardbase/card_title.html') + '{% block body %}{% endblock body %}</div>')
    p.w('web/parlor/cardbase/user_card.html', '{% extends "parlor/cardbase/card_base.html" %}', '{% block body %}u{% endblock body %}')
    drawn.append('parlor/cardbase/user_card.html')
    case('카드 base 부모가 include 하는 조각(보수)', 'parlor/cardbase/card_title.html', True, '<h3>t</h3>', False)
    case('common 조각', 'common/util/common_part.html', True, '<span>c</span>')
    p.sub('web/' + shell, '</head>', inc('root/scaffold/view/root_head_part.html') + '\n</head>')
    case('셸 머리 root 조각', 'root/scaffold/view/root_head_part.html', False, '<meta name="x" content="y">', False)
    menu = 'root/scaffold/view/root_doc_menu.html'
    case('문서 셸이 그리는 root 조각', menu, declared, '<div>menu</div>', False)
    if declared:
        p.sub('web/' + FLAT_SHELL, '<body>', '<body>' + inc(menu))
        p.w('web/parlor/embed/doc_embed.html', '{% extends "' + FLAT_SHELL + '" %}', '{% block content %}e{% endblock %}')
        drawn.append('parlor/embed/doc_embed.html')
        order = 'application/order/presentation_layer/section/'
        case('다른 제품 BC 조각을 지속 옛 화면만 그림', order + 'order_extra_section.html', False, '<div>x</div>')
        doc = []
        for name, file, red, persistent in [
                ('문서 화면과 함께 그리는 다른 제품 조각', order + 'order_shared_section.html', True, True),
                ('문서 화면만 그리는 조각', order + 'order_doc_only_section.html', True, False),
                ('문서 화면과 함께 그리는 옛 조각', 'parlor/shared/shared_badge.html', True, True),
                ('지속 제품 자기 section 을 문서 화면도 그림(한계)', bc + '/presentation_layer/section/%s_flat_section.html' % stem, False, False),
                ('개념 폴더 section 을 문서 화면도 그림', concept + 'section/%s_doc_section.html' % stem, True, False)]:
            case(name, file, red, '<div>s</div>', persistent)
            doc.append(file)
        p.w('web/parlor/flatdoc/view/flat_doc.html', '{% extends "' + FLAT_SHELL + '" %}',
            '{% block content %}' + ''.join(inc(f) for f in doc) + '{% endblock content %}')
        hidden = 'parlor/shared/hidden_pick_section.html'
        case('문서 화면이 변수 include 로 함께 그리는 옛 조각(한계)', hidden, False, '<div>h</div>')
        p.w('web/parlor/flatdoc/view/flat_var.html', '{% extends "' + FLAT_SHELL + '" %}',
            '{% block content %}{% with part_name="' + hidden + '" %}{% include part_name %}{% endwith %}{% endblock content %}')
    p.w('web/parlor/front/view/front.html', '{% extends "' + shell + '" %}', '{% block title %}front{% endblock title %}',
        '{% block content %}' + ''.join(inc(f) for f in drawn) + '{% include part_name %}{% endblock content %}')
    return p, p.commit('drawn-base'), cases


def without_sh1(text):
    # 2.4.3 러너에는 CS1(2.5.0) · TG4(2.7.0)가 없다 — CS1 줄 · TG4 알림 줄과 검사 종수는 대조에서 뺀다.
    out, skip = [], False
    for line in text.splitlines():
        if line.startswith(('[SH1] BLOCKER', '[CS1] BLOCKER')):
            skip = True
        elif not (skip and line.startswith('  ')):
            skip = False
            if line and not line.startswith(('[info] CS1', '[info] TG4 ')):  # 발견 사이 빈 줄 수는 발견 수를 따라 바뀐다
                out.append(re.sub(r'blocker \d+건', 'blocker #건', line))
    return re.sub(r'검사 \d+종(?: 중 \d+종)?', '검사 #종', '\n'.join(out))


def bundle_z9(tmp):
    # F4-91: SH1 화면 = 옛 몫 ∪ (사슬 + 글자 include 닫힘 · 개념 폴더 한 단 − 표준 문서 셸이 그리는 것).
    old = None
    archive = subprocess.run(['git', '-C', str(REPO), 'archive', DRAWN_BASELINE, 'dddjango-web/scripts',
                              'dddjango-web/.claude-plugin'], capture_output=True, env=ENV)
    if archive.returncode:
        print('SKIP Z9 — 바탕 커밋 %s 없음: 옛 러너 대조만 건너뜀' % DRAWN_BASELINE)
    else:
        (tmp / 'old').mkdir()
        subprocess.run(['tar', '-xf', '-', '-C', str(tmp / 'old')], input=archive.stdout, check=True)
        old = tmp / 'old/dddjango-web/scripts'
    for declared in (False, True):
        p, base, cases = drawn_project(tmp / str(declared), declared)
        for name, (file, red) in cases.items():
            p.reset(base)
            p.append('web/' + file, BOOST)
            expect(p, base, 'sh1', red, 'Z9 %s %s' % (declared, name), file if red else None)
        p.reset(base)
        for file, _ in cases.values():
            p.append('web/' + file, BOOST)
        if old is None:
            continue
        for args in (('--diff-base', base), ('--diff-base', base, '--slice-end'), ('--all',)):
            new_code, new_out = backstop(p.root, *args)
            old_code, old_out = backstop(p.root, *args, scripts=old)
            check('Z9 대조 실행이 검사까지 돎(%s %s)' % (declared, args[-1]),
                  new_code in (0, 2) and old_code in (0, 2), (new_code, old_code, new_out[-300:]))
            check('Z9 SH1 밖 출력 2.4.3 과 같음(%s %s)' % (declared, args[-1]),
                  without_sh1(new_out) == without_sh1(old_out), (new_out, old_out))
            heads = lambda out: {line for line in out.splitlines() if line.startswith('[SH1] BLOCKER')}
            check('Z9 SH1 은 줄기만 한다(%s %s)' % (declared, args[-1]), heads(new_out) <= heads(old_out),
                  sorted(heads(new_out) - heads(old_out)))


def main():
    only = set(sys.argv[1:])
    for bundle in (bundle_z0, bundle_z1, bundle_z1_alias, bundle_z2, bundle_z2_tabs, bundle_z3, bundle_z3_verbatim,
                   bundle_z4, bundle_z4_legacy, bundle_z4_order, bundle_z5, bundle_z6, bundle_z7, bundle_z8,
                   bundle_minor, bundle_standard, bundle_z9):
        if only and bundle.__name__[7:] not in only:
            continue
        with tempfile.TemporaryDirectory(prefix='web240-') as tmp:
            try:
                bundle(Path(tmp))
            except Exception as error:
                check(bundle.__name__ + ' 준비·실행 오류', False, '%s: %s' % (type(error).__name__, error))
    print('2.4.0 지속 셸 픽스처: PASS %d / FAIL %d' % (PASS, FAIL))
    return bool(FAIL)


if __name__ == '__main__':
    sys.exit(main())
