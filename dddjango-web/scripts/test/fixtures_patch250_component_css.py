"""2.5.0 CS1 회귀 — A~J·U, 임시 git 프로젝트만 쓴다(브라우저·호스트 실행 없음)."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

TEST = Path(__file__).resolve().parent
SCRIPTS = TEST.parent
REPO = SCRIPTS.parents[1]
sys.path.insert(0, str(TEST))
sys.path.insert(0, str(SCRIPTS))
from fixtures_patch230 import (ENV, FLAT_SHELL, ORDER_PAGE, REGISTRY, backstop, git, mkstd, strip_stamp)
from fixtures_patch240_shell import prepare as persistent_project

PASS = FAIL = 0
BASELINE = '981693be'
BADGE = 'design_system/component/badge/soft_badge.html'
CSS = BADGE[:-5] + '.css'
SECTION = 'application/order/presentation_layer/section/order_list_summary_section.html'


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok:
        print('    ' + str(detail).replace('\n', '\n    ')[:2400])


def include(file=BADGE, tail=''):
    return '{% include "' + file + '"' + tail + ' %}'


def link(css=CSS, tail='', attrs=''):
    asset = 'web/' + css[7:] if css.startswith('static/') else css
    return '<link rel="stylesheet" href="{% static \'' + asset + '\' %}' + tail + '"' + attrs + '>'


def page(p, head='', body=None, file=ORDER_PAGE, shell=FLAT_SHELL):
    p.w('web/' + file, '{% extends "' + shell + '" %}', '{% load static %}',
        '{% block head %}' + head + '{% endblock head %}',
        '{% block content %}' + (include() if body is None else body) + '{% endblock content %}')


def component(p, file=BADGE, body='<span class="soft-badge">x</span>', css=True):
    p.w('web/' + file, body)
    if css:
        p.w('web/' + file[:-5] + '.css', '.soft-badge { color: var(--color-base); }')


def project(tmp):
    p = mkstd(tmp)
    p.w('web/' + FLAT_SHELL, '{% load static %}<html><head>',
        '{% block head %}{% endblock %}', '</head><body>{% block content %}{% endblock %}</body></html>')
    component(p)
    page(p, body='')
    return p, p.commit('base')


def expect(p, base, count, name, info=None, args=(), only='cs'):
    flags = ('--diff-base', base) if base else ('--all',)
    got = backstop(p.root, *flags, *(() if only is None else ('--only', only)), *args)
    check(name, got[0] == (2 if count else 0) and got[1].count('[CS1] BLOCKER') == count
          and '내부 오류' not in got[1] and (info is None or info in got[1]), got)
    return got


def bundle_a(tmp):
    p, base = project(tmp / 'basic')
    page(p)
    got = expect(p, base, 1, 'A 직접 include')
    check('A 위반·교정 문장', '부품 CSS 가 이 문서에 실리지 않는다 — ' + CSS in got[1]
          and link() in got[1] and '들어온 길:' in got[1], got)
    page(p, head=link())
    expect(p, base, 0, 'A 페이지 head')
    p.w('web/' + SECTION, include())
    page(p, body=include(SECTION))
    expect(p, base, 1, 'A 조각 경유')
    outer = 'design_system/component/panel/outer_panel.html'
    component(p, outer, include(), css=False)
    page(p, body=include(outer))
    expect(p, base, 1, 'A 부품 안 부품')
    p.w('web/' + SECTION, '{% extends "' + BADGE + '" %}')
    page(p, body=include(SECTION))
    expect(p, base, 1, 'A slot 부품 extends')
    p, base = project(tmp / 'field')
    names = ['design_system/component/badge/field%d_badge.html' % n for n in range(13)]
    for file in names:
        component(p, file)
    page(p, head=link(names[0][:-5] + '.css'), body=''.join(include(f) for f in names))
    got = expect(p, base, 12, 'A 현장 꼴 13 부품·1 link = 12 쌍')
    check('A 쌍마다 한 발견', all(got[1].count('위반: 부품 CSS 가 이 문서에 실리지 않는다 — ' +
          f[:-5] + '.css') == 1 for f in names[1:]), got)


def bundle_b(tmp):
    p, base = project(tmp)
    for name, head in [('꼬리', link(tail='?v=1#x')), ('rel 공백', link().replace('stylesheet', ' stylesheet '))]:
        page(p, head=head)
        expect(p, base, 0, 'B ' + name)
    page(p, head="{% static '" + CSS + "' as badge_css %}<link rel=\"stylesheet\" href=\"{{ badge_css }}?v=1\">")
    expect(p, base, 1, 'B static as 는 literal 아님', '동적 link 주소')
    p.sub('web/' + FLAT_SHELL, '<head>', '<head>' + link())
    page(p)
    expect(p, base, 0, 'B 셸 머리')
    p.reset(base)
    head = 'root/scaffold/view/root_head.html'
    p.w('web/' + head, link())
    p.sub('web/' + FLAT_SHELL, '<head>', '<head>' + include(head))
    page(p)
    expect(p, base, 0, 'B 머리 안 include')
    p.w('web/' + FLAT_SHELL, '<html>' + include(head) + '<body>{% block content %}{% endblock %}</body></html>')
    p.w('web/' + head, '<head>' + link() + '</head>')
    expect(p, base, 0, 'B 머리 통째 include')
    p.w('web/' + head, '<head><title>x</title></head>')
    expect(p, base, 1, 'B 머리 통째 include 빠짐')
    p.reset(base)
    p.sub('web/' + FLAT_SHELL, 'block head', 'block styles')
    page(p, head=link())
    p.sub('web/' + ORDER_PAGE, 'block head', 'block styles')
    expect(p, base, 0, 'B 옛 셸 styles')
    p.reset(base)
    screen = 'static/application/order/order_list_view.css'
    for suffix in ('', ' all', ' screen'):
        p.w('web/' + screen, '@import url("../../../' + CSS + '")' + suffix + ';')
        page(p, head=link(screen))
        expect(p, base, 0, 'B 화면 CSS import' + suffix)
    nested = 'design_system/component/badge/import_badge.css'
    p.w('web/' + nested, '@import "soft_badge.css";')
    p.w('web/' + screen, '@import "../../../' + nested + '";')
    expect(p, base, 0, 'B import 닫힘')
    page(p, head="{% static '" + CSS + "' as badge_css %}{% verbatim %}"
         '<link rel="stylesheet" href="{{ badge_css }}">{% endverbatim %}')
    expect(p, base, 1, 'B verbatim 안 변수 주소는 실림 아님')


def bundle_c(tmp):
    p, base = project(tmp)
    page(p, body=link() + include())
    expect(p, base, 1, 'C 본문 link', '실리지 않는다(본문 ')
    for name, head in [('print', link(attrs=' media="print"')), ('disabled', link(attrs=' disabled')),
                       ('alternate', link().replace('stylesheet', 'alternate stylesheet')),
                       ('media query', link(attrs=' media="screen and (width > 1px)"'))]:
        page(p, head=head)
        expect(p, base, 1, 'C 죽은 link ' + name, '인쇄 전용 · disabled · alternate link 뿐')
    screen = 'static/application/order/order_list_view.css'
    for name, text in [('url', '.x { background: url("../../../' + CSS + '"); }'),
                       ('print', '@import "../../../' + CSS + '" print;'),
                       ('supports', '@import "../../../' + CSS + '" supports(display: grid);'),
                       ('late', '.x {} @import "../../../' + CSS + '";')]:
        p.w('web/' + screen, text)
        page(p, head=link(screen))
        expect(p, base, 1, 'C import 아님 ' + name)
    p.w('web/' + FLAT_SHELL, '<html><head>{% block head %}' + link() + '{% endblock %}</head>',
        '<body>{% block content %}{% endblock %}</body></html>')
    page(p)
    expect(p, base, 1, 'C 빈 block 덮음')
    page(p, head='{{ block.super }}')
    expect(p, base, 0, 'C block.super')
    page(p, head='{% verbatim %}{{ block.super }}{% endverbatim %}')
    expect(p, base, 1, 'C verbatim 안 super 는 글자')
    middle = 'legacy/middle.html'
    p.w('web/' + middle, '{% extends "' + FLAT_SHELL + '" %}', '{% block head %}{{ block.super }}{% endblock %}')
    page(p, head='{{ block.super }}', shell=middle)
    expect(p, base, 0, 'C 세 겹 block.super')


def bundle_d(tmp):
    p, base = project(tmp)
    p.rm('web/' + CSS)
    page(p)
    expect(p, base, 0, 'D CSS 없는 부품')
    p.reset(base)
    for name, body in [('HTML 주석', '<!-- ' + include() + ' -->'), ('Django 주석', '{# ' + include() + ' #}'),
                       ('comment', '{% comment %}' + include() + '{% endcomment %}'),
                       ('verbatim', '{% verbatim x %}' + include() + '{% endverbatim x %}')]:
        page(p, body=body)
        expect(p, base, 0, 'D ' + name)
    p.sub('web/' + FLAT_SHELL, '{% block content %}', '{% block content %}' + include())
    page(p, body='')
    expect(p, base, 0, 'D 덮인 block include')
    p.reset(base)
    page(p, body='')
    p.append('web/' + ORDER_PAGE, include())
    expect(p, base, 0, 'D 아래 템플릿 block 밖')
    for name, body in [('if', '{% if flag %}' + include() + '{% endif %}'),
                       ('for', '{% for x in xs %}' + include() + '{% endfor %}'),
                       ('template', '<template>' + include() + '</template>')]:
        page(p, body=body)
        expect(p, base, 1, 'D 한 번이라도 렌더 ' + name)


def bundle_e(tmp):
    p, base = project(tmp)
    outer = 'design_system/component/sheet/bottom_sheet.html'
    component(p, outer, '{% include content_template %}', css=False)
    p.w('web/' + SECTION, include())
    page(p, body=include(outer, ' with content_template="' + SECTION + '" only'))
    expect(p, base, 1, 'E 글자 대입 풀이')
    page(p, body=include(outer, ' with content_template="' + SECTION + '"|cut:"x" only'))
    expect(p, base, 0, 'E 필터 붙은 대입은 글자 상수가 아님', '변수 include `content_template`')
    page(p, body='{% include state.template_name %}')
    expect(p, base, 0, 'E 진짜 변수 include', '미검증(못 읽음)')
    p.reset(base)
    for opener, closer in [('if flag', 'endif'), ('for x in xs', 'endfor'), ('ifchanged x', 'endifchanged')]:
        page(p, head='{% ' + opener + ' %}' + link() + '{% ' + closer + ' %}')
        expect(p, base, 0, 'E 조건부 ' + opener, 'CS1 미검증 1건')
    head = 'root/scaffold/view/root_head.html'
    p.w('web/' + head, link())
    page(p, head='{% if flag %}' + include(head) + '{% endif %}')
    expect(p, base, 0, 'E 조건 안 include 된 link', '미검증(조건부)')
    p.reset(base)
    p.w('web/' + ORDER_PAGE, '{% extends layout %}')
    expect(p, base, 0, 'E 변수 extends', '변수 extends')
    page(p, head='<link rel="stylesheet" href="{% static state.css %}">', body='')
    expect(p, base, 0, 'E 동적 link', '동적 link 주소')
    page(p, body='<link rel="stylesheet" href="{{ runtime_css }}">' + include())
    got = expect(p, base, 1, 'E 본문 동적 link 는 실림 후보 아님')
    check('E 본문 주소가 안 읽혀도 머리 누락은 확정', 'CS1 미검증' not in got[1], got)
    p.reset(base)
    inner = 'application/order/presentation_layer/widget/order_inner_widget.html'
    p.w('web/' + inner, include())
    p.w('web/' + SECTION, include(inner))
    got = expect(p, base, 0, 'E 조각 뿌리', 'CS1 미검증 1건')
    check('E 안쪽 조각은 따로 안 냄', got[1].count('미검증(조각)') == 1 and
          '미검증(조각) — web/' + SECTION in got[1], got)
    component(p, 'design_system/component/panel/slot_panel.html', '{% block content %}{% include content_template %}{% endblock %}', False)
    p.w('web/' + inner, '{% extends "design_system/component/panel/slot_panel.html" %}')
    page(p, body=include(inner, ' with content_template="' + SECTION + '" only'))
    p.w('web/' + SECTION, include())
    expect(p, base, 1, 'E 묶음은 사슬 전체')
    p.w('web/' + SECTION, include(outer, ' only'))
    component(p, outer, '{% include content_template %}', css=False)
    got = expect(p, base, 0, 'E only 바깥 대입 지움', '변수 include `content_template`')
    check('E 묶음 줄 있음', re.search(r'CS1 미검증 \d+건 — 통과가 아니다:', got[1]) is not None, got)


def bundle_f(tmp):
    p, base = project(tmp)
    page(p)
    old = p.commit('old-missing')
    expect(p, old, 0, 'F 안 건드린 옛 누락')
    expect(p, None, 1, 'F all 옛 누락')
    p.sub('web/' + ORDER_PAGE, '{% load static %}', '{% load static %}\n{# 줄만 고침 #}')
    expect(p, old, 0, 'F 다른 줄만 고침', 'CS1 기존 누락')
    button = 'design_system/component/button/primary_button.html'
    page(p, body=include() + include(button))
    got = expect(p, old, 1, 'F 새 include 새 쌍만', 'CS1 기존 누락')
    check('F 새 쌍 CSS', '위반: 부품 CSS 가 이 문서에 실리지 않는다 — ' + button[:-5] + '.css' in got[1], got)
    page(p, head=link())
    loaded = p.commit('loaded')
    page(p)
    expect(p, loaded, 1, 'F 머리 link 삭제')
    p.rm('web/' + CSS)
    empty = p.commit('no-css')
    component(p)
    expect(p, empty, 1, 'F 기존 문서에 CSS 새로')
    p.reset(empty)
    component(p)
    page(p, file=ORDER_PAGE.replace('order_list_view', 'order_new_view'))
    expect(p, empty, 2, 'F 미추적 새 페이지')
    p.reset(base)
    page(p, body='{% include state.template_name %}')
    unknown = p.commit('unknown')
    p.sub('web/' + ORDER_PAGE, '{% load static %}', '\n\n{% load static %}')
    got = expect(p, unknown, 0, 'F 못 읽는 자리 줄 이동')
    check('F 옛 미검증 안 냄', 'CS1 미검증' not in got[1], got)
    p.reset(base)
    page(p, head='{% if flag %}' + link() + '{% endif %}')
    conditional = p.commit('conditional')
    p.append('web/' + ORDER_PAGE, '{# 다른 줄 #}')
    got = expect(p, conditional, 0, 'F 옛 조건부 안 냄')
    check('F 옛 조건부 재출력 없음', 'CS1 미검증' not in got[1], got)
    p.reset(base)
    dynamic = '<link rel="stylesheet" href="{{ first_css }}">'
    page(p, head=dynamic, body='')
    unknown = p.commit('old-dynamic-link')
    page(p, head=dynamic + '<link rel="stylesheet" href="{{ second_css }}">', body='')
    got = expect(p, unknown, 0, 'F 다른 동적 주소는 새 자리', 'CS1 미검증 1건')
    check('F 새 주소 하나만 미검증', got[1].count('미검증(못 읽음)') == 1, got)
    p.reset(base)
    p.w('web/' + ORDER_PAGE, '{% extends first_layout %}')
    unknown = p.commit('old-variable-extends')
    p.w('web/' + ORDER_PAGE, '{% extends second_layout %}')
    expect(p, unknown, 0, 'F 다른 변수 extends 는 새 자리', '변수 extends')


def design(p, rows):
    folder = p.root / '.dddjango-web/build'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'design-spec.md').write_text('## 슬라이스 0\n' + '\n'.join('경로: ' + a + ' → ' + b for a, b in rows) + '\n')
    return folder


def bundle_g(tmp):
    p, base = project(tmp / 'rename')
    page(p)
    old = p.commit('old')
    new = ORDER_PAGE.replace('order_list_view', 'order_new_view')
    p.mv('web/' + ORDER_PAGE, 'web/' + new)
    expect(p, old, 0, 'G git mv 문서', 'CS1 기존 누락')
    p.reset(old)
    text = p.read('web/' + ORDER_PAGE)
    p.rm('web/' + ORDER_PAGE)
    p.w('web/' + new, text + '{# 전혀 다른 줄 #}' * 30)
    folder = design(p, [(ORDER_PAGE, new)])
    expect(p, old, 0, 'G 명세 경로 행', 'CS1 기존 누락', args=('--design-build', folder))
    p.reset(old)
    p.w('web/' + new, text)
    folder = design(p, [(ORDER_PAGE, new)])
    expect(p, old, 1, 'G 옛 파일 남은 거짓 행', args=('--design-build', folder))
    p.reset(old)
    page(p, file=new, body='')
    both = p.commit('both')
    p.rm('web/' + ORDER_PAGE)
    page(p, file=new)
    folder = design(p, [(ORDER_PAGE, new)])
    expect(p, both, 1, 'G 기준점에도 새 파일 거짓 행', args=('--design-build', folder))
    p.reset(old)
    renamed = BADGE.replace('soft_badge', 'new_badge')
    p.mv('web/' + BADGE, 'web/' + renamed)
    p.mv('web/' + CSS, 'web/' + renamed[:-5] + '.css')
    page(p, body=include(renamed))
    expect(p, old, 0, 'G 부품 html·css 개명', 'CS1 기존 누락')
    p.reset(old)
    p.sub('web/' + FLAT_SHELL, '<head>', '<head>' + link())
    loaded = p.commit('loaded')
    p.mv('web/' + ORDER_PAGE, 'web/' + new)
    other = 'legacy/new_shell.html'
    p.w('web/' + other, '<html><head></head><body>{% block content %}{% endblock %}</body></html>')
    page(p, file=new, shell=other)
    expect(p, loaded, 1, 'G 이동 중 셸 변경 새 누락')
    p, _ = project(tmp / 'product')
    p.declare({'operator': {'design_system': 'flat', 'bcs': []}, 'guest': {'design_system': 'own', 'bcs': '*'}})
    own = BADGE.replace('design_system/', 'design_system/guest/')
    component(p, own)
    guest = 'root/scaffold/view/root_guest_view.html'
    p.w('web/' + guest, p.read('web/' + FLAT_SHELL))
    page(p, body=include(own), shell=guest)
    old = p.commit('guest')
    git(p.root, 'mv', 'web/design_system/guest', 'web/design_system/customer')
    p.mv('web/' + guest, 'web/' + guest.replace('guest', 'customer'))
    p.mv('web/' + ORDER_PAGE, 'web/' + new)
    p.sub(REGISTRY, 'guest', 'customer')
    p.sub('web/' + new, 'guest', 'customer')
    folder = design(p, [(ORDER_PAGE, new), ('design_system/guest/', 'design_system/customer/')])
    expect(p, old, 0, 'G 제품 뿌리·선언·문서·셸 개명', 'CS1 기존 누락', args=('--design-build', folder))


def bundle_h(tmp):
    p, base = project(tmp / 'own')
    p.declare({'operator': {'design_system': 'flat', 'bcs': []}, 'guest': {'design_system': 'own', 'bcs': '*'}})
    own = BADGE.replace('design_system/', 'design_system/guest/')
    component(p, own)
    shell = 'root/scaffold/view/root_guest_view.html'
    p.w('web/' + shell, p.read('web/' + FLAT_SHELL))
    page(p, head=link(own[:-5] + '.css'), body=include(own), shell=shell)
    expect(p, base, 0, 'H own CSS 실림')
    page(p, head=link(), body=include(own), shell=shell)
    got = expect(p, base, 1, 'H 평면 CSS 혼입', only='cs,im13')
    check('H IM13 함께', '[IM13] BLOCKER' in got[1], got)
    p.rm('web/' + own[:-5] + '.css')
    expect(p, base, 1, 'H own 뿌리 CSS 없음', '제품 guest 뿌리에 이 부품 CSS 가 없다')
    p, shell, file, base = persistent_project(tmp / 'persistent')
    button = 'design_system/component/button/primary_button.html'
    page(p, body=include(button), file=file, shell=shell)
    expect(p, base, 0, 'H 같은 제품 지속 셸 SH4 초록', only='cs,sh4')
    component(p)
    page(p, file=file, shell=shell)
    expect(p, base, 1, 'H SH4 안 돌려도 새 include', only='cs')
    p, _ = project(tmp / 'foreign')
    p.declare({'operator': {'design_system': 'flat', 'bcs': []}, 'guest': {'design_system': 'own', 'bcs': '*'}})
    p.sub('web/' + FLAT_SHELL, '<body>', '<body data-root-shell="root_view@{{ root_state.shell_rev }}">')
    component(p, own)
    old = p.commit('foreign-shell')
    page(p, body=include(own))
    expect(p, old, 1, 'H 다른 제품 지속 셸 상속 기존 페이지')
    p, base = project(tmp / 'rev-tail')
    page(p, head=link(tail='?v={{ root_state.shell_rev }}'))
    expect(p, base, 0, 'H SH4 꼬리 ?v={{ root_state.shell_rev }} 만 떼고 읽음')
    page(p, head=link(tail='?v={{root_state.shell_rev}}'))
    expect(p, base, 0, 'H SH4 꼬리 공백 없는 꼴')
    for tail in ('?v={{ other_rev }}', '?v={{ root_state.shell_rev|upper }}',
                 '?v={{ root_state.shell_rev }}&x={{ y }}', '?w={{ root_state.shell_rev }}'):
        page(p, head=link(tail=tail))
        expect(p, base, 1, 'H 다른 변수 꼬리는 동적 ' + tail, '동적 link 주소')


def merger(p, base):
    git(p.root, 'checkout', '-qb', 'lane')
    p.w('lane.txt', 'lane')
    p.commit('lane')
    folder = p.root / '.dddjango-web/build'
    folder.mkdir(parents=True)
    (folder / 'build-state.json').write_text(json.dumps({'git_snapshot': base, 'slices': []}))
    git(p.root, 'checkout', '-q', 'main')
    return folder


def receive(p, folder):
    p.commit('upstream')
    git(p.root, 'checkout', '-q', 'lane')
    git(p.root, 'merge', '--no-ff', '-q', '-m', 'receive', 'main')
    sha = git(p.root, 'rev-parse', 'HEAD')
    with (folder / 'approved-merges.txt').open('a') as out:
        out.write(sha + ' main\n')
    return sha


def inflow_expect(p, base, folder, name, received=True):
    got = backstop(p.root, '--diff-base', base, '--only', 'cs', '--design-build', folder)
    main, _, approved = got[1].partition('== 승인 유입(')
    check(name, got[0] == (0 if received else 2) and ('[CS1] BLOCKER' in approved) == received
          and ('[CS1] BLOCKER' in main) != received and '측정 무효' not in got[1], got)
    return got


def bundle_i(tmp):
    p, base = project(tmp / 'runner')
    page(p)
    expect(p, base, 1, 'I --only cs1', only='cs1')
    got = expect(p, base, 1, 'I 슬라이스 끝', args=('--slice-end',), only=None)
    check('I 92종 중 85종', '검사 92종 중 85종(슬라이스 끝 — 미룸 7:' in got[1], got)
    for kind in ('document', 'head', 'head-deleted', 'import'):
        p, base = project(tmp / kind)
        head = 'root/scaffold/view/root_head.html'
        screen = 'static/application/order/order_list_view.css'
        if kind in ('head', 'head-deleted'):
            p.w('web/' + head, link())
            p.sub('web/' + FLAT_SHELL, '<head>', '<head>' + include(head))
            page(p)
        elif kind == 'import':
            p.w('web/' + screen, '@import "../../../' + CSS + '";')
            page(p, head=link(screen))
        else:
            p.rm('web/' + ORDER_PAGE)  # 승인 병합이 실제로 새 문서를 들인다.
        p.w('web/application/order/presentation_layer/widget/order_unknown_widget.html', '{% include runtime_template %}')
        base = p.commit('before-merge')
        original = p.read('web/' + ORDER_PAGE) if kind != 'document' else ''
        folder = merger(p, base)
        if kind == 'document':
            page(p)
        elif kind == 'head':
            p.w('web/' + head, '<meta name="x">')
        elif kind == 'head-deleted':
            p.rm('web/' + head)
        else:
            p.w('web/' + screen, '.order-list {}')
        receive(p, folder)
        inflow_expect(p, base, folder, 'I 승인 병합 ' + kind)
        if kind != 'document':
            check('I 문서 blob 그대로 ' + kind, p.read('web/' + ORDER_PAGE) == original)
            from src.common import BackstopContext
            from src.products import preflight
            from src.check_component_css import run_component_css
            ctx = BackstopContext.build(p.root, base, False)
            preflight(ctx)
            findings = run_component_css(ctx)
            cause = screen if kind == 'import' else head
            check('I 바뀐·지워진 원인만 기록 ' + kind,
                  len(findings) == 1 and findings[0].causes == ('web/' + cause,), findings)
        if kind == 'head':
            p.append('web/' + head, '<meta name="lane">')
            p.commit('lane-edit')
            got = inflow_expect(p, base, folder, 'I 받은 뒤 원인 조각 수정', False)
            check('I 원인 파일 사유', '원인 파일이 한 승인 병합의 상류판 그대로가 아님' in got[1], got)
    p, base = project(tmp / 'two-merges')
    h1, h2 = 'legacy/head1.html', 'legacy/head2.html'
    p.w('web/' + h1, link())
    p.w('web/' + h2, link())
    p.sub('web/' + FLAT_SHELL, '<head>', '<head>' + include(h1) + include(h2))
    page(p)
    base = p.commit('two-links')
    folder = merger(p, base)
    p.w('web/' + h1, '<meta name="one">')
    receive(p, folder)
    git(p.root, 'checkout', '-q', 'main')
    p.w('web/' + h2, '<meta name="two">')
    receive(p, folder)
    inflow_expect(p, base, folder, 'I 원인 파일 두 병합 분산', False)


def bundle_j(tmp):
    p, base = project(tmp)
    child = ORDER_PAGE.replace('order_list_view', 'order_child_view')
    p.w('web/' + child, '{% extends "' + ORDER_PAGE + '" %}', '{% block content %}{% endblock %}')
    base = p.commit('child')
    page(p)
    expect(p, base, 1, 'J 상속당하는 view 페이지')
    p.reset(base)
    fragment = ORDER_PAGE.replace('order_list_view', 'order_embed_view')
    p.w('web/' + fragment, include())
    expect(p, base, 0, 'J 머리 없는 view 조각', '미검증(조각) — web/' + fragment)
    p.reset(base)
    p.w('web/legacy/old.html', '<html><head></head><body>' + include() + '</body></html>')
    expect(p, base, 1, 'J view 밖 잎 문서')


def baseline_scripts(tmp):
    files = git(REPO, 'ls-tree', '-r', '--name-only', BASELINE, '--', 'dddjango-web/scripts', 'dddjango-web/.claude-plugin').splitlines()
    for file in files:
        if '/test/' in file:
            continue
        content = subprocess.run(['git', '-C', str(REPO), 'show', BASELINE + ':' + file],
                                 capture_output=True, check=True, env=ENV).stdout
        dest = tmp / file
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
    return tmp / 'dddjango-web/scripts'


def normalized(out):
    return re.sub(r'검사 (?:92|91)종(?: 중 (?:85|84)종)?',
                  lambda m: '검사 #종 중 #종' if ' 중 ' in m[0] else '검사 #종', out)


def bundle_u(tmp):
    old = baseline_scripts(tmp / 'old')
    p, base = project(tmp / 'unchanged')
    for args in (('--diff-base', base), ('--diff-base', base, '--slice-end'), ('--all',)):
        now = backstop(p.root, *args)
        before = backstop(p.root, *args, scripts=old)
        check('U CS 발견 없는 출력 byte 동일 ' + str(args),
              (now[0], normalized(now[1])) == (before[0], normalized(before[1])), (now, before))
    page(p)
    now, before = p.scan(), p.scan(scripts=old)
    check('U 누락 있는 트리 빚 키·발견 무변', now[:2] == before[:2] and strip_stamp(now[2]) == strip_stamp(before[2]), (now, before))
    from src.common import Finding
    from src import debt
    import backstop as runner
    check('U 지문·상수', (debt.scanner_stamp()['checks'], runner.TOTAL_CHECKS, len(runner.SLICE_END_DEFERRED)) ==
          ('e49c83776ff9faf6', 92, 7))
    f = Finding('IM1', 'x.py', 2, '위반', '규약', '고침')
    check('U Finding 출력 무변', str(f) == '[IM1] BLOCKER — web/x.py:2\n  위반: 위반 (규약)\n  교정: 고침')
    check('U causes 기본값', getattr(f, 'causes', None) == ())


def bundle_r(tmp):
    # R: 코드 검토 재현. 기준점이 옳았는데 현재 빠진 경우는 반드시 새 blocker 다.
    from src.common import BackstopContext
    from src.products import preflight
    from src import check_component_css as cs
    p, _ = project(tmp / 'sub/svc')
    shutil.rmtree(p.root / '.git')
    git(p.root.parent, 'init', '-q', '-b', 'main')
    page(p)
    old = p.commit('subfolder-old-missing')
    p.append('web/' + ORDER_PAGE, '{# 다른 줄 #}')
    expect(p, old, 0, 'R F1 하위 폴더 옛 누락', 'CS1 기존 누락')
    p.reset(old)
    page(p, head=link())
    loaded = p.commit('subfolder-loaded')
    page(p)
    expect(p, loaded, 1, 'R F1 하위 폴더 link 삭제')
    p.reset(old)
    moved = ORDER_PAGE.replace('order_list_view', 'order_moved_view')
    p.mv('web/' + ORDER_PAGE, 'web/' + moved)
    expect(p, old, 0, 'R F1 하위 폴더 이동', 'CS1 기존 누락')

    p, _ = project(tmp / 'keys')
    slot = 'design_system/component/sheet/bottom_sheet.html'
    component(p, slot, '{% include content_template %}', False)
    page(p, body=include(slot, ' with content_template=state.first'))
    old = p.commit('old-slot')
    new = ORDER_PAGE.replace('order_list_view', 'order_new_view')
    page(p, body=include(slot, ' with content_template=state.second'), file=new)
    got = expect(p, old, 0, 'R F2 새 문서 공용 변수 include',
                 'web/' + new + ' ← web/' + slot + ':1 · 변수 include `content_template`')
    check('R F2 새 받는 문서 하나만', got[1].count('미검증(못 읽음)') == 1, got)
    ctx = BackstopContext.build(p.root, old, False)
    preflight(ctx)
    keys = cs._calculate(cs.Tree(ctx)).unverified
    check('R F2 문서 키', ('못 읽음', new, slot + ' include content_template') in keys, keys)
    p.w('web/' + SECTION, include(slot, ' with content_template=state.third'))
    ctx = BackstopContext.build(p.root, old, False)
    preflight(ctx)
    keys = cs._calculate(cs.Tree(ctx)).unverified
    check('R F2 조각 뿌리 키', ('못 읽음', SECTION, slot + ' include content_template') in keys, keys)
    got = expect(p, old, 0, 'R M6 미검증 두 건', 'CS1 미검증 2건')
    p.reset(old)
    page(p, body='{% include state.template_name %}')
    got = expect(p, old, 0, 'R F2 문서 자신의 줄 모양',
                 'web/' + ORDER_PAGE + ':4 · 변수 include `state.template_name`')
    check('R F2 자기 지시문은 화살표 없음', ' ← ' not in got[1], got)

    p, _ = project(tmp / 'fragment')
    p.w('web/' + SECTION, include())
    page(p, head=link(), body=include(SECTION))
    old = p.commit('included-fragment')
    page(p, body='<div hx-get="/orders/summary"></div>')
    expect(p, old, 0, 'R F3 조각이 새 뿌리', '미검증(조각) — web/' + SECTION)

    p, old = project(tmp / 'spec')
    p.w('web/application/order/domain_layer/order/order.py',
        'from dataclasses import dataclass',
        'from web.application.order.application_layer.state.order_list_state import OrderListState',
        '@dataclass(frozen=True, slots=True, kw_only=True)', 'class Order:', '    key: str')
    folder = design(p, [])
    for name, content in [('정형 행', '## 슬라이스 0\n경로: a.py → b.py (설명)\n'.encode()),
                          ('절 중복', '## 슬라이스 0\n## 슬라이스 0 보충\n'.encode()),
                          ('UTF8', b'\xff')]:
        (folder / 'design-spec.md').write_bytes(content)
        got = backstop(p.root, '--diff-base', old, '--slice-end', '--design-build', folder)
        check('R F4 명세 판독 불가 ' + name, got[0] == 2 and '[IM19] BLOCKER' in got[1]
              and '내부 오류' not in got[1] and got[1].count('CS1 이동 대응 생략 — 명세 슬라이스 0 절 판독 불가(') == 1, got)

    p, old = project(tmp / 'shadow')
    button = 'design_system/component/button/primary_button.html'
    button_css = button[:-5] + '.css'
    outer = include(SECTION, ' with content_template="' + BADGE + '" only')
    p.w('web/' + SECTION, '{% with content_template="' + button + '" %}{% include content_template %}{% endwith %}')
    page(p, head=link(), body=outer)
    expect(p, old, 1, 'R F5 with 가림 정확한 안쪽 부품')
    p.w('web/' + SECTION, '{% for content_template in state.templates %}{% include content_template %}{% endfor %}')
    expect(p, old, 0, 'R F5 for 가림은 미검증', '변수 include `content_template`')
    p.w('web/' + SECTION, '{% with content_template=state.template %}{% include content_template %}{% endwith %}')
    expect(p, old, 0, 'R F5 with 변수 가림은 미검증', '변수 include `content_template`')
    p.w('web/' + SECTION, '{% with content_template="' + button + '" %}{% include content_template %}{% endwith %}')
    page(p, head=link(button_css), body=outer)
    loaded = p.commit('inner-with-loaded')
    p.w('web/' + SECTION, '{% include content_template %}')
    got = expect(p, loaded, 1, 'R F5 가림 제거 새 누락')
    check('R F5 세탁 없음', 'CS1 기존 누락' not in got[1], got)

    p, old = project(tmp / 'aliases')
    assign = "{% static '" + CSS + "' as css %}"
    dynamic = '<link rel="stylesheet" href="{{ css }}">'
    page(p, head=assign + dynamic + "{% static '" + button_css + "' as css %}" + dynamic,
         body=include() + include(button))
    expect(p, old, 2, 'R F6 별칭 순서대로 재대입도 literal 아님', '동적 link 주소')
    page(p, head=assign + '{% static state.css as css %}' + dynamic)
    expect(p, old, 1, 'R F6 변수로 재대입은 미검증', '동적 link 주소')
    page(p, head=assign + '{% with css="' + CSS + '" %}' + dynamic + '{% endwith %}')
    expect(p, old, 1, 'R F6 with 글자는 static 별칭 아님', '동적 link 주소')
    page(p, head='{% with css=state.css %}' + assign + dynamic + '{% endwith %}')
    expect(p, old, 1, 'R F6 with 안 실제 static 대입도 literal 아님', '동적 link 주소')
    for name, head, body in [('뒤 대입', dynamic, include() + assign),
                             ('조건 대입', '{% if flag %}' + assign + '{% endif %}' + dynamic, include()),
                             ('덮인 block 대입', dynamic, include())]:
        if name == '덮인 block 대입':
            p.sub('web/' + FLAT_SHELL, '<head>', '<head>{% block alias %}' + assign + '{% endblock %}' + dynamic)
            head = ''
        page(p, head=head, body=body)
        if name == '덮인 block 대입':
            p.append('web/' + ORDER_PAGE, '{% block alias %}{% endblock %}')
        expect(p, old, 1, 'R F6 ' + name, '동적 link 주소')

    p, old = project(tmp / 'inactive')
    head_file = 'root/scaffold/view/root_head.html'
    for ancestor in ('template', 'noscript'):
        page(p, head='<' + ancestor + '>' + link() + '</' + ancestor + '>')
        expect(p, old, 1, 'R F7 비활성 ' + ancestor)
        p.w('web/' + head_file, link())
        page(p, head='<' + ancestor + '>' + include(head_file) + '</' + ancestor + '>')
        expect(p, old, 1, 'R F7 include 비활성 ' + ancestor)
        p.w('web/' + head_file, '<' + ancestor + '>' + link() + '</' + ancestor + '>')
        page(p, head=include(head_file))
        expect(p, old, 1, 'R F7 include 안 비활성 ' + ancestor)

    p, old = project(tmp / 'href')
    for name, href in [('겹따옴표', '"{% static "' + CSS + '" %}"'),
                       ('따옴표 없음', "{% static '" + CSS + "' %}")]:
        page(p, head='<link rel="stylesheet" href=' + href + '>')
        got = expect(p, old, 0, 'R F8 static 주소 ' + name)
        check('R F8 동적 오인 없음 ' + name, '미검증' not in got[1], got)
        loaded = p.commit('loaded-' + name)
        page(p)
        expect(p, loaded, 1, 'R F8 그 주소 삭제 ' + name)

    p, old = project(tmp / 'symlinks')
    head_file = 'root/scaffold/view/root_head.html'
    target = 'root/scaffold/view/shared_head.html'
    p.w('web/' + target, link())
    (p.root / 'web' / head_file).symlink_to('shared_head.html')
    p.sub('web/' + FLAT_SHELL, '<head>', '<head>' + include(head_file))
    page(p)
    loaded = p.commit('symlink-head-loaded')
    p.w('web/' + target, '<meta name="changed">')
    got = expect(p, loaded, 1, 'R F9 링크 대상 변경 새 누락')
    check('R F9 현재 대상 기준점 세탁 없음', 'CS1 기존 누락' not in got[1], got)
    p.append('web/' + ORDER_PAGE, '{# 다른 줄 #}')
    expect(p, loaded, 1, 'R F9 문서 고침도 새 누락')
    ctx = BackstopContext.build(p.root, loaded, False)
    preflight(ctx)
    ctx.touched.discard(target)
    findings = cs.run_component_css(ctx)
    check('R F9 기준점 링크 대상은 항상 blob', len(findings) == 1
          and not any('CS1 기존 누락' in line for line in ctx.notices), (findings, ctx.notices))
    ctx = BackstopContext.build(p.root, loaded, False)
    preflight(ctx)
    raw = cs._git_raw
    def failed_modes(root, args):
        return None if args[0] == 'ls-tree' and '--name-only' not in args else raw(root, args)
    with patch.object(cs, '_git_raw', side_effect=failed_modes):
        findings = cs.run_component_css(ctx)
    check('R F9 링크 형식 판독 실패도 세탁 없음', len(findings) == 1
          and not any('CS1 기존 누락' in line for line in ctx.notices), (findings, ctx.notices))
    check('R M4 링크 형식 판독 실패 미검증', any('기준점 파일 판독 불가' in line
          and ORDER_PAGE in line for line in ctx.notices), ctx.notices)
    p.reset(old)
    screen = 'static/application/order/order_list_view.css'
    target = 'static/application/order/shared.css'
    p.w('web/' + target, '@import "../../../' + CSS + '";')
    p.rm('web/' + screen)
    (p.root / 'web' / screen).symlink_to('shared.css')
    page(p, head=link(screen))
    loaded = p.commit('symlink-css-loaded')
    p.w('web/' + target, '.changed {}')
    expect(p, loaded, 1, 'R F9 CSS 링크 대상 변경')

    p, old = project(tmp / 'small')
    p.sub('web/' + FLAT_SHELL, 'block head %}', 'block head %}' + link())
    page(p, head='{{ block.super|safe }}')
    expect(p, old, 0, 'R M1 super 필터')
    ctx = BackstopContext.build(p.root, None, True)
    preflight(ctx)
    with patch.object(cs, 'parsed_tags', return_value=None):
        cs.run_component_css(ctx)
    check('R M2 HTML 판독 불가 문서 이름', any('미검증(못 읽음) — web/' + ORDER_PAGE
          in line and 'HTML 판독 불가' in line for line in ctx.notices), ctx.notices)

    p, _ = project(tmp / 'rename')
    page(p)
    old = p.commit('old-missing')
    p.mv('web/' + ORDER_PAGE, 'web/' + moved)
    # git 설정 파일을 바꾸지 않고 한 실행의 환경으로만 diff.renames=false 를 재현한다.
    with patch.dict(ENV, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='diff.renames', GIT_CONFIG_VALUE_0='false'):
        expect(p, old, 0, 'R M3 개명 설정 무관', 'CS1 기존 누락')

    p, _ = project(tmp / 'reads')
    p.w('web/' + head_file, link())
    p.sub('web/' + FLAT_SHELL, '<head>', '<head>' + include(head_file))
    page(p)
    loaded = p.commit('readable-loaded')
    p.w('web/' + head_file, '<meta name="changed">')
    ctx = BackstopContext.build(p.root, loaded, False)
    preflight(ctx)
    raw = cs._git_raw
    def failed_show(root, args):
        return None if args[0] == 'show' and head_file in args[-1] else raw(root, args)
    with patch.object(cs, '_git_raw', side_effect=failed_show):
        findings = cs.run_component_css(ctx)
    check('R M4 기준점 git show 실패 미검증', any('미검증(못 읽음)' in line and '기준점 파일 판독 불가'
          in line and ORDER_PAGE in line for line in ctx.notices), ctx.notices)
    check('R M4 읽기 실패는 기존 누락 아님', len(findings) == 1 and not any('CS1 기존 누락' in line
          for line in ctx.notices), (findings, ctx.notices))
    ctx = BackstopContext.build(p.root, loaded, False)
    preflight(ctx)
    read_text = Path.read_text
    def failed_read(path, *args, **kwargs):
        if path == p.root / 'web' / head_file:
            raise OSError('fixture read failure')
        return read_text(path, *args, **kwargs)
    with patch.object(Path, 'read_text', failed_read):
        cs.run_component_css(ctx)
    check('R M4 현재 읽기 실패 미검증', any('미검증(못 읽음)' in line and '파일 판독 불가'
          in line and ORDER_PAGE in line for line in ctx.notices), ctx.notices)
    p.reset(loaded)
    (p.root / 'web' / head_file).write_bytes(b'\xff')
    unreadable_base = p.commit('invalid-utf8')
    p.w('web/' + head_file, '<meta name="changed">')
    got = expect(p, unreadable_base, 1, 'R M4 기준점 UTF8 실패', '기준점 파일 판독 불가')
    check('R M4 기준점 UTF8 세탁 없음', 'CS1 기존 누락' not in got[1], got)

    p, old = project(tmp / 'own-fix')
    p.declare({'operator': {'design_system': 'flat', 'bcs': []}, 'guest': {'design_system': 'own', 'bcs': '*'}})
    own = BADGE.replace('design_system/', 'design_system/guest/')
    component(p, own, css=False)
    shell = 'root/scaffold/view/root_guest_view.html'
    p.w('web/' + shell, p.read('web/' + FLAT_SHELL))
    page(p, body=include(own), shell=shell)
    got = expect(p, old, 1, 'R M5 own CSS 없는 교정', '제품 guest 뿌리에 이 부품 CSS 가 없다')
    fix = next(line for line in got[1].splitlines() if line.startswith('  교정:'))
    check('R M5 없는 파일을 먼저 작성', '작성' in fix and '<link' not in fix, fix)

    p, _ = project(tmp / 'skip')
    page(p)
    old = p.commit('old-missing')
    got = expect(p, old, 0, 'R M6 안 건드린 기존 누락 알림 생략')
    check('R M6 안 건드린 기존 알림 없음', 'CS1 기존 누락' not in got[1], got)
    p, _ = project(tmp / 'non-git')
    page(p)
    shutil.rmtree(p.root / '.git')
    got = backstop(p.root, '--only', 'cs')
    check('R M6 비git 전역 검사', got[0] == 2 and '[CS1] BLOCKER' in got[1]
          and 'git 저장소 아님' in got[1], got)


def bundle_s(tmp):
    # 2차 A P1/P1b·include 별칭, B n1~n4: 별칭·필터 효과를 해석하지 않는다.
    assign = "{% static '" + CSS + "' as css %}"
    dynamic = '<link rel="stylesheet" href="{{ css }}">'
    head_file = 'root/scaffold/view/root_css_link.html'
    for name in ('A P1 block 밖 별칭', 'A P1b 형제 block 별칭',
                 'A include 별칭 B n2', 'B n3 with 범위와 자식 block'):
        p, _ = project(tmp / name.split()[1])
        if 'P1b' in name:
            p.w('web/' + FLAT_SHELL, '<html><head>{% block vars %}{% endblock %}',
                '{% block head %}{% endblock %}</head><body>{% block content %}{% endblock %}</body></html>')
        elif 'P1 ' in name:
            p.sub('web/' + FLAT_SHELL, '</head>', dynamic + '</head>')
        elif 'n3' in name:
            p.sub('web/' + FLAT_SHELL, '{% block head %}{% endblock %}',
                  '{% with css=state.css %}' + assign + '{% block head %}{% endblock %}{% endwith %}')
        else:
            p.w('web/' + head_file, dynamic)
        old = p.commit('alias-shell')
        if 'P1b' in name:
            page(p, head=dynamic)
            p.append('web/' + ORDER_PAGE, '{% block vars %}' + assign + '{% endblock %}')
        elif 'P1 ' in name:
            page(p, head=assign)
        elif 'n3' in name:
            page(p, head=dynamic)
        else:
            page(p, head=assign + include(head_file))
        got = expect(p, old, 1, 'S ' + name, None if 'P1 ' in name else '동적 link 주소')
        if 'P1 ' in name:
            check('S A P1 옛 동적 키는 재출력 없음', '미검증(못 읽음)' not in got[1], got)
        check('S literal 교정 ' + name, link() in got[1], got)
        page(p, head=link())
        expect(p, old, 0, 'S literal로 고침 ' + name)

    p, _ = project(tmp / 'n2b')
    p.w('web/' + head_file, dynamic)
    page(p, head=assign + include(head_file))
    old = p.commit('alias-is-unreadable-baseline')
    got = expect(p, None, 1, 'S B n2b 별칭 기준점도 실림 아님', '동적 link 주소')
    page(p)
    got = expect(p, old, 0, 'S B n2b 별칭 제거는 literal 기준 기존 누락', 'CS1 기존 누락')
    check('S B n2b 옛 동적 줄은 재출력 안 함', '미검증(못 읽음)' not in got[1], got)

    p, _ = project(tmp / 'n1')
    p.sub('web/' + FLAT_SHELL, 'block head %}', 'block head %}' + link())
    page(p, head='{{ block.super|safe }}')
    old = p.commit('safe-super-loaded')
    for suffix in ('|striptags', '|default:""', '|safe|striptags'):
        page(p, head='{{ block.super' + suffix + ' }}')
        got = expect(p, old, 1, 'S B n1 super ' + suffix, 'block.super 필터 판독 불가')
        check('S B n1 필터 literal 교정 ' + suffix, link() in got[1], got)
    for suffix in ('', '|safe'):
        page(p, head='{{ block.super' + suffix + ' }}')
        expect(p, old, 0, 'S super 보존 ' + suffix)

    p, old = project(tmp / 'attributes')
    for name, head in [
        ('B n4 조건부 rel', link().replace('rel="stylesheet"', 'rel="{% if flag %} stylesheet {% endif %}"')),
        ('rel 변수', link().replace('rel="stylesheet"', 'rel="{{ rel }}"')),
        ('media 조건', link(attrs=' media="{% if flag %}screen{% endif %}"')),
        ('media 변수', link(attrs=' media="{{ media }}"')),
        ('disabled 조건', link(attrs=' disabled="{% if flag %}disabled{% endif %}"')),
        ('disabled 변수', link(attrs=' disabled="{{ disabled }}"')),
        ('href 변수 꼬리', link(tail='?v={{ revision }}')),
        ('href 태그 꼬리', link(tail='?v={% cycle 1 2 %}')),
        ('href 필터', '<link rel="stylesheet" href="{% static \'' + CSS + '\'|cut:\'x\' %}">'),
        ('href 표현식', '<link rel="stylesheet" href="{% static state.css %}">')]:
        page(p, head=head)
        got = expect(p, old, 1, 'S 동적 속성 ' + name, '동적 link 주소')
        check('S 동적 속성 교정 ' + name, link() in got[1], got)
    for name, href in [('단일 따옴표', "{% static '" + CSS + "' %}"),
                       ('겹따옴표', '{% static "' + CSS + '" %}'),
                       ('literal URL', '/static/' + CSS)]:
        page(p, head='<link rel="stylesheet" href="' + href + '">')
        expect(p, old, 0, 'S literal 주소 ' + name)
    page(p, head='<link rel="stylesheet" href="' + CSS + '">')
    expect(p, old, 1, 'S 맨 앞 / 없는 글자 경로는 페이지 기준 — 실림 아님')

    p, _ = project(tmp / 'p5b')
    legacy = ORDER_PAGE.replace('order_list_view', 'order_legacy_view')
    new = ORDER_PAGE.replace('order_list_view', 'order_board_view')
    def board(file, title):
        p.w('web/' + file, '{% extends "' + FLAT_SHELL + '" %}', '{% load static %}',
            '{% block head %}{% endblock head %}', '{% block content %}',
            '<h1>' + title + '</h1>', '<section class="order">' + include() + '</section>', '{% endblock content %}')
    board(legacy, '주문')
    old = p.commit('legacy')
    p.rm('web/' + legacy)
    board(new, '주문 보드')
    git(p.root, 'add', '-A')
    status = git(p.root, 'diff', '-M', '--name-status', old)
    check('S A P5b 실제 유사 rename', re.search(r'^R(?!100)\d+\t', status, re.M) is not None, status)
    expect(p, old, 1, 'S A P5b 유사 rename 새 누락')
    folder = design(p, [(legacy, new)])
    expect(p, old, 0, 'S A P5b 명세 이동이면 기존 누락', 'CS1 기존 누락', args=('--design-build', folder))
    p.reset(old)
    (p.root / 'web' / legacy).rename(p.root / 'web' / new)
    expect(p, old, 1, 'S A P6 unstaged 이동은 대응 없음')


def bundle_t(tmp):
    # 2차 A P3~P3e: 목록 밖 파일은 양쪽에서 같은 부재다. 진짜 읽기 실패와 구별한다.
    head_file = 'legacy/head_css.html'
    absent_css = 'design_system/theme/legacy_theme.css'
    outside = 'legacy/partials/footer.html'
    screen = 'static/application/order/order_list_view.css'
    for name in ('P3', 'P3b', 'P3c', 'P3d', 'P3e', 'import 없음', 'extends 없음', 'CSS 링크 대상 없음'):
        p, _ = project(tmp / name.replace(' ', '-'))
        if name == 'P3c':
            p.w(head_file, link())  # web 밖 TEMPLATES 입력은 CS의 파일 집합 밖이다.
            p.sub('web/' + FLAT_SHELL, '<head>', '<head>' + include(head_file))
            page(p)
        elif name in ('P3e', 'CSS 링크 대상 없음'):
            if name == 'CSS 링크 대상 없음':
                (p.root / 'web' / absent_css).symlink_to('absent.css')
            p.sub('web/' + FLAT_SHELL, '<head>', '<head>' + link(absent_css))
            page(p)
        elif name == 'import 없음':
            p.w('web/' + screen, '@import "/static/' + absent_css + '";')
            page(p, head=link(screen))
        elif name == 'extends 없음':
            p.w('web/' + SECTION, '{% extends "legacy/absent.html" %}' + include())
            page(p, body=include(SECTION))
        else:
            p.w(outside, '<footer>x</footer>')
            page(p, head=link() if name in ('P3b', 'P3d') else '',
                 body='<p>안녕</p>' + include(outside) + include())
        old = p.commit('same-absence')
        if name == 'P3d':
            p.sub('web/' + ORDER_PAGE, '안녕', '반가워')
        else:
            p.w('web/application/order/presentation_layer/section/order_other_section.html', '<p>lane</p>')
        got = expect(p, old, 0, 'T A ' + name + ' 같은 부재')
        check('T A ' + name + ' 기준점 소음 없음', 'CS1 미검증' not in got[1]
              and '기준점 판독' not in got[1] and '기준점 파일 판독' not in got[1], got)
        if name in ('P3', 'P3c', 'P3e', 'import 없음', 'extends 없음', 'CSS 링크 대상 없음'):
            got = expect(p, None, 1, 'T A ' + name + ' all 누락 유지')
            check('T A ' + name + ' 부재는 기준점 실패 아님', '기준점 ' not in got[1], got)
        if name in ('P3e', 'import 없음', 'CSS 링크 대상 없음'):
            check('T A ' + name + ' CSS 부재는 못 읽음 아님', '미검증(못 읽음)' not in got[1], got)

    from src.common import BackstopContext
    from src.products import preflight
    from src import check_component_css as cs
    p, _ = project(tmp / 'real-failure')
    p.w('web/' + head_file, '<meta name="old">')
    page(p, head=include(head_file))
    old = p.commit('old-missing')
    p.w('web/' + head_file, '<meta name="new">')
    ctx = BackstopContext.build(p.root, old, False)
    preflight(ctx)
    raw = cs._git_raw
    def failed_show(root, args):
        return None if args[0] == 'show' and head_file in args[-1] else raw(root, args)
    with patch.object(cs, '_git_raw', side_effect=failed_show):
        findings = cs.run_component_css(ctx)
    check('T P3 진짜 git show 실패는 새 누락', len(findings) == 1 and not any('CS1 기존 누락' in n
          for n in ctx.notices) and any('기준점 파일 판독 불가(git show 실패)' in n for n in ctx.notices),
          (findings, ctx.notices))


def bundle_v(tmp):
    # P2: 판독 실패를 주입해도 같은 입력이면 새 blocker를 낼 수 없다.
    from src.common import BackstopContext
    from src.products import preflight
    from src import check_component_css as cs
    p, _ = project(tmp)
    middle = 'legacy/middle.html'
    head_file = 'root/scaffold/view/root_css_link.html'
    screen = 'static/application/order/order_list_view.css'
    imported = 'static/application/order/imported.css'
    p.w('web/' + middle, '{% extends "' + FLAT_SHELL + '" %}', '{% block head %}{{ block.super }}{% endblock %}')
    p.w('web/' + head_file, link(screen))
    p.sub('web/' + FLAT_SHELL, '<head>', '<head>' + include(head_file))
    p.w('web/' + screen, '@import "imported.css";')
    p.w('web/' + imported, '.old {}')
    p.w('web/' + SECTION, include())
    page(p, head='{{ block.super }}', body=include(SECTION), shell=middle)
    p.declare({'operator': {'design_system': 'flat', 'bcs': '*'}})
    old = p.commit('same-judged-inputs')
    original_read = cs.Tree.read
    def failed_read(tree, file, *args, **kwargs):
        if tree.baseline and file == head_file:
            tree.read_errors[file] = 'git show 실패'
            return None
        return original_read(tree, file, *args, **kwargs)
    def judge(name, count, edit=None):
        p.reset(old)
        if edit:
            edit()
        ctx = BackstopContext.build(p.root, old, False)
        preflight(ctx)
        with patch.object(cs.Tree, 'read', failed_read):
            findings = cs.run_component_css(ctx)
        check('V P2 ' + name, len(findings) == count and not any('CS1 기존 누락' in n for n in ctx.notices),
              (findings, ctx.notices))
        check('V P2 미검증은 파일 거름 없음 ' + name,
              any('기준점 파일 판독 불가(git show 실패)' in n for n in ctx.notices), ctx.notices)
    judge('그대로는 blocker 없음', 0)
    judge('무관한 변경도 blocker 없음', 0, lambda: p.w('web/legacy/unrelated.html', '<p>x</p>'))
    judge('실행 권한만 바뀌면 입력 동일', 0, lambda: (p.root / 'web' / ORDER_PAGE).chmod(0o755))
    judge('추적에서 빠져도 같은 바이트면 입력 동일', 0, lambda: git(p.root, 'rm', '--cached', 'web/' + ORDER_PAGE))
    for name, file in [('문서', ORDER_PAGE), ('extends 셸', FLAT_SHELL), ('block 출처', middle),
                       ('include', SECTION), ('head include', head_file), ('link CSS', screen),
                       ('import CSS', imported)]:
        judge(name + ' 변경은 다시 판정', 1, lambda file=file: p.append('web/' + file, '{# changed #}' if file.endswith('.html') else '/* changed */'))
    judge('필요 CSS 삭제는 요구가 사라짐', 0, lambda: p.rm('web/' + CSS))  # CSS 없는 부품은 필요가 없다.
    judge('제품 선언 변경은 다시 판정', 1, lambda: p.append(REGISTRY, ' '))
    judge('필요 CSS 내용만 변경은 입력 동일', 0, lambda: p.append('web/' + CSS, '/* unlinked content */'))

    p.reset(old)
    p.rm('web/' + CSS)
    no_css = p.commit('need-css-absent')
    component(p)
    expect(p, no_css, 1, 'V P2 필요 CSS 생성은 다시 판정')
    p.reset(old)
    page(p, head=link(), body=include(SECTION), shell=middle)
    loaded = p.commit('literal-loaded')
    p.w('web/' + SECTION, include() + include('design_system/component/button/primary_button.html'))
    expect(p, loaded, 1, 'V P2 include 새 요구는 다시 판정')

    p, _ = project(tmp / 'own-existence')
    p.declare({'operator': {'design_system': 'flat', 'bcs': []}, 'guest': {'design_system': 'own', 'bcs': '*'}})
    own = CSS.replace('design_system/', 'design_system/guest/')
    p.w('web/' + own, '.soft-badge {}')
    guest = 'root/scaffold/view/root_guest_view.html'
    p.w('web/' + guest, p.read('web/' + FLAT_SHELL))
    page(p, head=link(own), shell=guest)
    loaded = p.commit('own-css-loaded')
    p.rm('web/' + own)
    expect(p, loaded, 1, 'V P2 own 필요 CSS 삭제는 다시 판정', '제품 guest 뿌리에 이 부품 CSS 가 없다')

    p, _ = project(tmp / 'listing-failure')
    page(p)
    old = p.commit('old-missing')
    raw = cs._git_raw
    def failed_listing(root, args):
        return None if args[0] == 'ls-tree' and '--name-only' in args else raw(root, args)
    def listing_judge(name, base, count):
        ctx = BackstopContext.build(p.root, base, False)
        preflight(ctx)
        with patch.object(cs, '_git_raw', side_effect=failed_listing):
            findings = cs.run_component_css(ctx)
        check('V P2 기준점 목록 실패 ' + name, len(findings) == count and
              any('기준점 파일 목록 판독 불가' in n for n in ctx.notices), (findings, ctx.notices))
    listing_judge('같은 입력은 blocker 없음', old, 0)
    (p.root / 'web' / ORDER_PAGE).chmod(0o755)
    listing_judge('실행 권한만 변경은 입력 동일', old, 0)
    p.reset(old)
    p.append('web/' + CSS, '/* unlinked content only */')
    listing_judge('필요 CSS 내용만 변경은 입력 동일', old, 0)
    p.reset(old)
    p.rm('web/' + CSS)
    no_css = p.commit('absent-css')
    component(p)
    listing_judge('필요 CSS 생성은 다시 판정', no_css, 1)

    p, _ = project(tmp / 'own-unused-flat')
    p.declare({'operator': {'design_system': 'flat', 'bcs': []}, 'guest': {'design_system': 'own', 'bcs': '*'}})
    own = BADGE.replace('design_system/', 'design_system/guest/')
    component(p, own)
    p.rm('web/' + CSS)
    guest = 'root/scaffold/view/root_guest_view.html'
    p.w('web/' + guest, p.read('web/' + FLAT_SHELL))
    page(p, shell=guest)
    old = p.commit('own-css-exists')
    component(p)
    listing_judge('own CSS가 있으면 새 flat CSS는 그 문서 입력 아님', old, 0)

    p, _ = project(tmp / 'fragment-inputs')
    p.w('web/' + SECTION, include())
    old = p.commit('old-fragment')
    p.w('web/legacy/unrelated.html', '<p>x</p>')
    got = expect(p, old, 0, 'V P2 조각 입력 그대로')
    check('V P2 옛 조각 키만 거름', '미검증(조각)' not in got[1], got)
    p.w('web/' + SECTION, include() + include('design_system/component/button/primary_button.html'))
    expect(p, old, 0, 'V P2 새 조각 요구는 키로 비교', '미검증(조각) — web/' + SECTION)

    p, _ = project(tmp / 'same-blob-type')
    head_file = 'root/scaffold/view/root_css_link.html'
    target = 'root/scaffold/view/shared_head.html'
    p.w('web/' + target, link())
    (p.root / 'web' / head_file).symlink_to('shared_head.html')
    page(p, head=include(head_file))
    old = p.commit('symlink-head-loaded')
    (p.root / 'web' / head_file).unlink()
    (p.root / 'web' / head_file).write_text('shared_head.html')
    check('V P2 형식 변경의 blob 바이트는 같음', git(p.root, 'diff', '--numstat', old) == '0\t0\tweb/' + head_file)
    expect(p, old, 1, 'V P2 링크가 일반 파일이 되면 렌더 입력 변경')


def bundle_w(tmp):
    # 3차 검토: 제품 소속 변화 · HTML 기호 주소 · literal 경로 + SH4 꼬리 · 본문 super 필터 · CSS 아닌 link.
    p, _ = project(tmp / 'area')
    p.rm('web/' + ORDER_PAGE)
    market = 'application/market/order/presentation_layer/view/order_list_view.html'
    p.w('web/' + market, '{% load static %}<html><head>' + link() + '</head><body>' + include() + '</body></html>')
    p.w('web/application/market/market.py', 'x: int = 1')
    p.declare({'operator': {'design_system': 'flat', 'bcs': ['market']}, 'guest': {'design_system': 'own', 'bcs': '*'}})
    own = CSS.replace('design_system/', 'design_system/guest/')
    p.w('web/' + own, '.soft-badge {}')
    for folder in ('foundation', 'theme', 'util'):
        shutil.copytree(p.root / 'web/design_system' / folder, p.root / 'web/design_system/guest' / folder)
    p.w('web/root/scaffold/view/root_guest_view.html', p.read('web/' + FLAT_SHELL))
    old = p.commit('operator-market')
    p.rm('web/application/market/market.py')  # market 이 BC 에서 area 로 — 문서가 guest 제품이 된다.
    expect(p, old, 1, 'W P2 제품 소속이 바뀌면 다시 판정', own)
    p.reset(old)
    p.rm('web/application/market/market.py')
    p.w('web/' + market, '{% load static %}<html><head>' + link(own) + '</head><body>' + include() + '</body></html>')
    guest = p.commit('market-area-guest')
    (p.root / 'web/application/market/domain_layer').mkdir()  # 빈 폴더 — 파일 변경 없이 market 이 BC 로
    expect(p, guest, 1, 'W 파일 변경 없는 제품 소속 변화(빈 폴더)도 다시 판정')
    (p.root / 'web/application/market/domain_layer').rmdir()

    # 5차: 판독 실패 보호는 기준점 제품을 잃은 문서만 — 제품이 확정된(guest) 문서의 소속 변화는 다른 렌더 파일 판독 실패와 함께여도 판정한다.
    from src.common import BackstopContext
    from src.products import preflight
    from src import check_component_css as cs
    p.w('web/application/market/market.py', 'x: int = 1')
    original_read = cs.Tree.read
    def badge_failed(tree, file, *args, **kwargs):
        if tree.baseline and file == BADGE:
            tree.read_errors[file] = 'git show 실패'
            return None
        return original_read(tree, file, *args, **kwargs)
    ctx = BackstopContext.build(p.root, guest, False)
    preflight(ctx)
    with patch.object(cs.Tree, 'read', badge_failed):
        findings = cs.run_component_css(ctx)
    check('W 제품 확정 문서는 다른 파일 판독 실패에도 소속 변화 판정', len(findings) == 1, (findings, ctx.notices))
    p.rm('web/application/market/market.py')

    # 4차: 제품 소속만 바뀐 발견도 승인 유입으로 가른다 — area 를 가른 삭제가 원인.
    p.reset(old)
    folder = merger(p, old)
    p.rm('web/application/market/market.py')
    receive(p, folder)
    inflow_expect(p, old, folder, 'W 승인 병합이 바꾼 제품 소속은 승인 유입')
    # 5차: 레인이 그 area 아래 만든 무시 파일은 원인이고 HEAD 에 없다 — 승인 유입으로 넘기지 않는다.
    (p.root / '.git/info/exclude').write_text('web/application/market/order/lane.md\n')
    p.w('web/application/market/order/lane.md', 'lane note')
    inflow_expect(p, old, folder, 'W 원인에 레인의 무시 파일이 있으면 이 레인 몫', received=False)
    p.rm('web/application/market/order/lane.md')
    git(p.root, 'checkout', '-q', 'main')

    # 5차: 선언 변경으로 제품이 바뀐 문서는 선언이 원인 — 레인이 같은 BC 에 만든 무관한 파일을 원인에 넣지 않는다.
    p.reset(old)
    git(p.root, 'branch', '-D', 'lane')
    shutil.rmtree(p.root / '.dddjango-web')
    folder = merger(p, old)
    git(p.root, 'checkout', '-q', 'lane')
    p.w('web/application/market/order/presentation_layer/section/order_new_section.html', '<p>new</p>')
    p.commit('lane-new-section')
    git(p.root, 'checkout', '-q', 'main')
    p.declare({'operator': {'design_system': 'flat', 'bcs': []}, 'guest': {'design_system': 'own', 'bcs': '*'}})
    receive(p, folder)
    inflow_expect(p, old, folder, 'W 승인 병합의 선언 변경은 레인의 같은 BC 새 파일과 무관하게 승인 유입')
    git(p.root, 'checkout', '-q', 'main')

    # 4차: 기준점 판독 실패로 제품을 못 정한 root 문서는 소속 변화로 세지 않는다(같은 입력 보호).
    from src.common import BackstopContext
    from src.products import preflight
    from src import check_component_css as cs
    p, _ = project(tmp / 'root-read')
    doc = 'root/home/view/root_home_view.html'
    p.w('web/' + doc, '{% extends "' + FLAT_SHELL + '" %}', '{% block content %}' + include() + '{% endblock %}')
    p.declare({'operator': {'design_system': 'flat', 'bcs': '*'}})
    old = p.commit('root-doc-old-missing')
    p.w('web/legacy/unrelated.html', '<p>x</p>')
    original_read = cs.Tree.read
    def failed_read(tree, file, *args, **kwargs):
        if tree.baseline and file == doc:
            tree.read_errors[file] = 'git show 실패'
            return None
        return original_read(tree, file, *args, **kwargs)
    ctx = BackstopContext.build(p.root, old, False)
    preflight(ctx)
    with patch.object(cs.Tree, 'read', failed_read):
        findings = cs.run_component_css(ctx)
    check('W 기준점 판독 실패 root 문서는 새 blocker 없음', not findings
          and any('기준점 파일 판독 불가(git show 실패)' in n for n in ctx.notices), (findings, ctx.notices))

    p, base = project(tmp / 'entity')
    page(p, head='<link rel="stylesheet" href="&#123;% static &#39;' + CSS + '&#39; %&#125;">')
    got = expect(p, base, 1, 'W HTML 기호로 적은 static 글자는 실림 아님')
    check('W HTML 기호 주소는 동적 아님', '동적 link 주소' not in got[1], got)
    page(p, head='<link rel="stylesheet" href="/static/' + CSS + '?v=&#123;&#123; x &#125;&#125;">')
    expect(p, base, 0, 'W HTML 기호 꼬리는 글자 주소')

    page(p, head='<link rel="stylesheet" href="/static/' + CSS + '?v={{ root_state.shell_rev }}">')
    expect(p, base, 0, 'W SH4 꼬리 + literal URL')
    page(p, head='<link rel="stylesheet" href="/static/' + CSS + '?v={{ other_rev }}">')
    expect(p, base, 1, 'W 다른 꼬리 + literal URL', '동적 link 주소')
    page(p, head='<link rel="stylesheet" href="' + CSS + '?v={{ root_state.shell_rev }}">')
    expect(p, base, 1, 'W SH4 꼬리 + 맨 앞 / 없는 경로는 실림 아님')
    # 4차: 토큰 출처는 조각마다 — HTML 기호 static + 진짜 꼬리 / 진짜 static + HTML 기호 꼬리.
    entity = '&#123;% static &#39;' + CSS + '&#39; %&#125;'
    for tail in ('?v={{ root_state.shell_rev }}', '?v={{root_state.shell_rev}}', '?v={{ other_rev }}'):
        page(p, head='<link rel="stylesheet" href="' + entity + tail + '">')
        expect(p, base, 1, 'W HTML 기호 static + 진짜 꼬리 ' + tail)
    page(p, head=link(tail='?q=&#123;&#123; x &#125;&#125;'))
    expect(p, base, 0, 'W 진짜 static + HTML 기호 꼬리는 글자 꼬리')
    page(p, head=link(tail='?q={{ x\n}}'))
    expect(p, base, 0, 'W 진짜 static + 줄 넘는 {{ 꼬리는 글자(Django 한 줄 토큰)')
    # 5차: static 태그 뒤 공백은 주소 안 글자(%20) — 떼어 낸 SH4 꼬리 앞 공백도 같다. 주소 끝 공백은 브라우저가 뗀다.
    for tail in (' ?q=1', ' #x', ' ?v={{ root_state.shell_rev }}'):
        page(p, head=link(tail=tail))
        expect(p, base, 1, 'W static 태그 뒤 공백 꼬리는 실림 아님' + tail)
    page(p, head=link(tail='?v={{ root_state.shell_rev }} '))
    expect(p, base, 0, 'W SH4 꼬리 뒤 주소 끝 공백은 실림')

    p, base = project(tmp / 'super-body')
    p.sub('web/' + FLAT_SHELL, '{% block content %}{% endblock %}', '{% block content %}' + include() + '{% endblock %}')
    for suffix in ('|upper', '|striptags'):
        page(p, body='{{ block.super' + suffix + ' }}')
        got = expect(p, base, 1, 'W 본문 super ' + suffix + ' 도 부모 부품 요구')
        check('W 본문 super 는 미검증 줄 없음 ' + suffix, '미검증' not in got[1], got)
        page(p, head=link(), body='{{ block.super' + suffix + ' }}')
        expect(p, base, 0, 'W 본문 super ' + suffix + ' + 머리 literal 실림')
    p.sub('web/' + FLAT_SHELL, '{% block head %}{% endblock %}', '{% block head %}' + include() + '{% endblock %}')
    page(p, head='{{ block.super|upper }}', body='')
    expect(p, base, 1, 'W 머리 super 필터도 부모 부품 요구', 'block.super 필터 판독 불가')

    p, base = project(tmp / 'not-css')
    for head in ('<link rel="canonical" href="{{ request.build_absolute_uri }}">',
                 '<link rel="icon" href="{% static \'favicon.ico\' %}?v={{ revision }}">',
                 '<link rel="preconnect" href="{{ cdn }}">'):
        page(p, head=link() + head)
        got = expect(p, base, 0, 'W stylesheet 아닌 동적 link ' + head[11:20])
        check('W stylesheet 아닌 동적 link 는 미검증 없음 ' + head[11:20], '미검증' not in got[1], got)
    page(p, head='<link rel="{{ rel }}" href="{{ cdn }}">')
    expect(p, base, 1, 'W 동적 rel 은 그대로 미검증', '동적 link 주소')


def main():
    only = set(sys.argv[1:])
    for bundle in (bundle_a, bundle_b, bundle_c, bundle_d, bundle_e, bundle_f, bundle_g, bundle_h, bundle_i, bundle_j, bundle_u, bundle_r,
                   bundle_s, bundle_t, bundle_v, bundle_w):
        if only and bundle.__name__[7:] not in only:
            continue
        with tempfile.TemporaryDirectory(prefix='web250-') as tmp:
            try:
                bundle(Path(tmp))
            except Exception as error:
                check(bundle.__name__ + ' 준비·실행 오류', False, '%s: %s' % (type(error).__name__, error))
    print('2.5.0 부품 CSS 픽스처: PASS %d / FAIL %d' % (PASS, FAIL))
    return bool(FAIL)


if __name__ == '__main__':
    sys.exit(main())
