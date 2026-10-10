"""`{% static %}` 의 닫는 따옴표 뒤 «공백 + 다른 토큰» 꼴 회귀 픽스처 — 임시 git 저장소만 만들고 끝나면 지운다.

Django 의 static 태그는 둘째 조각(따옴표 문자열)만 경로로 읽고 공백 뒤의 나머지 토큰은 버린다 — 그 파일을 그대로 싣는다.
제품 혼입 판정(IM13 제품 분기 — 제품 선언이 있을 때)은 그 꼴을 «싣는 파일» 로 확정한다. 따옴표에 공백 없이 붙은 필터 ·
변수 인자는 동적 경로라 판정 밖 그대로다.
묶음: T 술어(parse_template_loads 직접) · L 새로 서는 꼴 · D 그대로 0 인 꼴 · K 그대로 서는 꼴 · U 무변(2.3.0 과 byte 대조).
고치기 전 판 = RELEASE_230 커밋의 scripts(`git archive` 로 임시 폴더에 푼다 — 작업 사본을 stash 하지 않는다).
그 커밋이 이력에 없으면(얕은 clone 등) U 묶음을 건너뛰고 건너뛴 사실을 출력한다(실패로 세지 않는다).
표준 트리 · 실행 · 출력 읽기 도우미는 fixtures_patch230 의 것을 그대로 쓴다(같은 두 제품 트리 — 운영자 flat · 손님 own)."""
import subprocess
import sys
import tempfile
from pathlib import Path

TEST = Path(__file__).resolve().parent
SCRIPTS = TEST.parent
REPO = SCRIPTS.parents[1]
sys.path.insert(0, str(TEST))
sys.path.insert(0, str(SCRIPTS))
from fixtures_patch230 import (ENV, GUEST_SHELL, LOBBY_PAGE, ORDER_PAGE, REGISTRY, backstop, lines_of, link, mkdeclared,
                               plugin_version)
from src.common import mask_html, parse_template_loads

RELEASE_230 = 'f349f87896e7cd338a27ad43b1b629bf8ff6d95b'  # dddjango-web 2.3.0 — «고치기 전 판» 의 고정 커밋
FLAT = 'design_system/foundation/app_color.css'        # 운영자(평면 뿌리) 표준 자리 CSS — 손님 문서가 실으면 혼입
OWN = 'design_system/guest/foundation/app_color.css'   # 손님(own 뿌리) 표준 자리 CSS — 손님 문서의 자기 제품
THEME = 'design_system/theme/app_theme.css'
PASS = FAIL = 0


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok and detail:
        print('    ' + str(detail).replace('\n', '\n    ')[:2400])


def tag(rest):
    """`{% static <rest>` 를 href 로 둔 링크 한 줄 — rest 는 인자부터 태그 끝까지 글자 그대로."""
    return '<link rel="stylesheet" href="{% static ' + rest + '">'


# (이름, 줄) — 닫는 따옴표 뒤 공백을 두고 다른 토큰이 온다. Django 는 그 토큰을 버리고 따옴표 문자열의 파일을 싣는다.
SPACED = [
    ("공백 뒤 `|cut:'x'`(필터가 아니라 버려지는 토큰)", tag("'" + FLAT + "' |cut:'x' %}")),
    ('공백 뒤 낱말 하나(`extra`)', tag("'" + FLAT + "' extra %}")),
    ('이름 없는 `as`', tag("'" + FLAT + "' as %}")),
    ('`as css` 뒤에 토큰이 더 있다', tag("'" + FLAT + "' as css extra %}")),
    ('토큰 여럿(`a b c`)', tag("'" + FLAT + "' a b c %}")),
    ('토큰 뒤 `-%}` 로 닫는다', tag("'" + FLAT + "' extra -%}")),
    ('큰따옴표', tag('"' + FLAT + '" extra %}')),
    ('탭 뒤 토큰', tag("'" + FLAT + "'\textra %}")),
    ('토큰이 `%}` 에 붙었다', tag("'" + FLAT + "' extra%}")),
    ('꼬리 `?v=1` + 토큰', tag("'" + THEME + "?v=1' extra %}")),
    ('앞머리 `./` + 토큰', tag("'./" + FLAT + "' extra %}")),
    ('토큰 뒤 같은 줄에 다른 태그', tag("'" + FLAT + "' extra %}") + '<i>{% if x %}y{% endif %}</i>'),
]
SPACED_LINES = [line for _name, line in SPACED]

# 판정 밖 그대로 — 동적 경로(붙은 필터 · 변수 인자) · 닫히지 않는 꼴 · 다음 줄에서야 닫히는 꼴 · 자기 제품 파일.
DYNAMIC_LINES = [
    tag("'" + FLAT + "'|cut:'x' %}"),          # 붙은 필터 — 진짜 필터
    tag("'" + FLAT + "'|default:x extra %}"),  # 붙은 필터 + 공백 뒤 토큰
    tag('css_path %}'),                        # 변수 인자
    tag('css_path extra %}'),                  # 변수 인자 + 토큰
    tag("'" + FLAT + "'x %}"),                 # 따옴표에 붙은 글자
]
QUIET_LINES = DYNAMIC_LINES + [
    tag("'" + OWN + "' extra %}"),             # 자기 제품 — 확정되지만 혼입이 아니다
    tag("'" + OWN + "' |cut:'x' %}"),          # 자기 제품
    "{% static '" + FLAT + "' extra",          # 공백 뒤 토큰 — 다음 줄에서야 닫힌다
    '%}',
    "{% static '" + FLAT + "' extra",          # 공백 뒤 토큰 — 닫는 `%}` 가 없다
]

# 2.3.0 에서도 서던 꼴 — (줄, 그 줄이 발견 행인가)
KEPT = [
    (link(FLAT), True),                                        # 따옴표 뒤 ` %}`
    ("{% static '" + FLAT + "' as css %}", True),              # `as <이름>`
    (link('./' + FLAT), True),                                 # 앞머리 `./`
    (link(FLAT + '?v=1'), True),                               # 꼬리 `?v=1`
    (tag("'" + FLAT + "' -%}"), True),                         # `-%}`
    (tag("'" + FLAT + "'%}"), True),                           # 공백 없이 닫힘
    ("{% static '" + FLAT + "'", True),                        # 다음 줄의 `%}` 로 닫힘(토큰 없음) — 2.3.0 그대로 받는다
    ('%}', False),
]
KEPT_LINES = [line for line, _hit in KEPT]


def put(p, lines):
    """손님 페이지(lobby)의 `<p>lobby</p>` 자리(4행)부터 lines 를 넣는다 → 첫 줄의 행 번호."""
    p.sub('web/' + LOBBY_PAGE, '<p>lobby</p>', '\n'.join(list(lines) + ['<p>lobby</p>']))
    return 4


def im13(out):
    return lines_of(out, 'IM13', LOBBY_PAGE)


def release_scripts(tmp):
    """RELEASE_230 커밋의 scripts 와 매니페스트를 `git archive` 로 임시 폴더에 푼다 → 그 scripts 폴더."""
    tmp.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(['git', '-C', str(REPO), 'archive', RELEASE_230, 'dddjango-web/scripts',
                              'dddjango-web/.claude-plugin'], capture_output=True, env=ENV, check=True).stdout
    subprocess.run(['tar', '-xf', '-', '-C', str(tmp)], input=archive, check=True)
    return tmp / 'dddjango-web' / 'scripts'


# ====================================================================== T — 술어(parse_template_loads 직접)

def loads(*lines):
    return parse_template_loads(mask_html('\n'.join(lines) + '\n'))


def bundle_predicate(tmp):
    for name, line in SPACED:
        want = THEME if THEME in line else FLAT
        check('T 확정 — %s' % name, loads('{% load static %}', line) == [(2, want)], loads('{% load static %}', line))
    check('T 확정 — 한 줄의 두 태그 모두(공백 뒤 토큰 꼴 둘)',
          loads("{% static '" + FLAT + "' x %}{% static '" + THEME + "' |y %}") == [(1, FLAT), (1, THEME)])
    check('T 확정 — 정적 접두 `web/` 도 같은 술어(`web/htmx/htmx.min.js` defer)',
          loads("{% static 'web/htmx/htmx.min.js' defer %}") == [(1, 'static/htmx/htmx.min.js')])
    check('T 확정 — 자기 제품 파일도 싣는 파일이다(혼입 여부는 판정 쪽 몫)', loads(tag("'" + OWN + "' extra %}")) == [(1, OWN)])
    for line in DYNAMIC_LINES:
        check('T 동적 — %s' % line[len('<link rel="stylesheet" href="'):-2], loads(line) == [], loads(line))
    check('T 동적 — 붙은 필터 뒤에 같은 줄의 다른 태그가 와도 앞 태그는 판정 밖',
          loads("{% static '" + FLAT + "'|cut:'x' %}{% static '" + THEME + "' %}") == [(1, THEME)])
    check('T 판정 밖 — 공백 뒤 토큰 꼴이 다음 줄에서야 닫힌다', loads("{% static '" + FLAT + "' extra", '%}') == [])
    check('T 판정 밖 — 공백 뒤 토큰 꼴에 닫는 `%}` 가 없다(뒤 줄의 다른 태그로 닫지 않는다)',
          loads("{% static '" + FLAT + "' extra", '<p>x</p>', '{% endblock %}') == [])
    check('T 판정 밖 — `as css` 뒤 토큰이 다음 줄에 있다', loads("{% static '" + FLAT + "' as css", 'extra %}') == [])
    kept = loads(*KEPT_LINES)
    check('T 그대로 — 2.3.0 에서 받던 꼴(` %}` · `as css` · `./` · `?v=1` · `-%}` · `\'%}` · 다음 줄 `%}`)',
          kept == [(n, FLAT) for n, (_line, hit) in enumerate(KEPT, 1) if hit], kept)
    check('T 그대로 — 줄바꿈이 낀 `as <이름>` · 앞머리 `/` · `{%- static`',
          loads("{% static '" + FLAT + "'", '  as css', '%}', "{% static '/" + FLAT + "' %}", "{%- static '" + FLAT + "' %}")
          == [(1, FLAT), (4, FLAT), (5, FLAT)])


# ====================================================================== L — 새로 서는 꼴(IM13)

def bundle_loaded(tmp):
    p, base = mkdeclared(tmp / 'l')
    first = put(p, SPACED_LINES)
    want = list(range(first, first + len(SPACED_LINES)))
    e, out = backstop(p.root, '--diff-base', base, '--only', 'im13')
    check('L1 공백 뒤 토큰 꼴 %d 줄 — 줄마다 IM13 · exit 2' % len(SPACED_LINES), e == 2 and im13(out) == want,
          'exit=%d %r\n%s' % (e, im13(out), out[-1800:]))
    for offset, (name, _line) in enumerate(SPACED):
        check('L1 %s — IM13' % name, first + offset in im13(out), im13(out))
    check('L1 사유의 실린 경로는 따옴표 문자열의 파일 그대로(버려진 토큰 · 꼬리 글자 없음)',
          out.count('표준 자리 CSS `%s` 를 싣는다' % FLAT) == len(SPACED_LINES) - 1
          and out.count('표준 자리 CSS `%s` 를 싣는다' % THEME) == 1 and '?v=1` 를 싣는다' not in out, out[-1800:])
    e, out = backstop(p.root, '--diff-base', base)
    check('L1 검사 전체를 돌려도 같은 줄 · 다른 검사의 새 발견 0', e == 2 and im13(out) == want
          and out.count('BLOCKER') == len(want), 'exit=%d %r\n%s' % (e, im13(out), out[-1800:]))
    p.commit('spaced tokens land as debt')
    counts = p.scan()[2].get('counts', {})
    check('L2 빚 스캔도 같은 판정 — 발견 수 %d' % len(SPACED_LINES), counts.get('IM13|' + LOBBY_PAGE) == len(SPACED_LINES),
          sorted(counts.items()))
    p.reset(base)

    # 방향 반대(운영자 페이지 → 손님 표준 CSS) · 셸(손님 셸 → 운영자 theme)
    p.sub('web/' + ORDER_PAGE, '{% block content %}', '{% block content %}\n' + tag("'" + OWN + "' extra %}"))
    p.sub('web/' + GUEST_SHELL, '</head>', tag("'" + THEME + "' |cut:'x' %}") + '\n</head>')
    e, out = backstop(p.root, '--diff-base', base, '--only', 'im13')
    check('L3 운영자 페이지가 손님 표준 CSS 를 공백 뒤 토큰 꼴로 싣는다 — IM13', lines_of(out, 'IM13', ORDER_PAGE) == [4], out[-1200:])
    check('L3 손님 셸이 운영자 theme 을 공백 뒤 토큰 꼴로 싣는다 — IM13', lines_of(out, 'IM13', GUEST_SHELL) == [5], out[-1200:])


# ====================================================================== D — 그대로 0 인 꼴

def bundle_quiet(tmp):
    p, base = mkdeclared(tmp / 'd')
    put(p, QUIET_LINES)
    e, out = backstop(p.root, '--diff-base', base, '--only', 'im13')
    check('D1 붙은 필터 · 변수 인자 · 자기 제품 · 닫히지 않는 꼴 · 다음 줄에서야 닫히는 꼴 — IM13 0 · exit 0',
          e == 0 and 'BLOCKER' not in out, 'exit=%d %r\n%s' % (e, im13(out), out[-1800:]))
    p.commit('quiet forms')
    counts = p.scan()[2].get('counts', {})
    check('D2 빚 스캔도 0', 'IM13|' + LOBBY_PAGE not in counts, sorted(counts.items()))


# ====================================================================== K — 그대로 서는 꼴

def bundle_kept(tmp):
    p, base = mkdeclared(tmp / 'k')
    first = put(p, KEPT_LINES)
    want = [first + n for n, (_line, hit) in enumerate(KEPT) if hit]
    e, out = backstop(p.root, '--diff-base', base, '--only', 'im13')
    check('K1 2.3.0 에서 서던 꼴(` %}` · `as css` · `./` · `?v=1` · `-%}` · `\'%}` · 다음 줄 `%}`) — 그대로 IM13',
          e == 2 and im13(out) == want, 'exit=%d %r\n%s' % (e, im13(out), out[-1800:]))


# ====================================================================== U — 무변(2.3.0 과 byte 대조)

def strip_stamp(data, same_version):
    """빚 스캔 JSON 에서 실행마다 다른 스캔 시각만 뺀다(두 판의 매니페스트 판 글자가 다르면 그 글자도)."""
    out = dict(data)
    out.pop('scanned_at', None)
    if not same_version:
        out['scanner'] = {k: v for k, v in data.get('scanner', {}).items() if k != 'plugin'}
    return out


def bundle_unchanged(tmp):
    if subprocess.run(['git', '-C', str(REPO), 'cat-file', '-e', RELEASE_230 + '^{commit}'], capture_output=True, env=ENV).returncode:
        print('SKIP U — 바탕 커밋 %s 이 이 저장소 이력에 없다(얕은 clone 등) — 무변 묶음(U)을 건너뛴다(실패로 세지 않는다)' % RELEASE_230[:8])
        return
    old = release_scripts(tmp / 'old')
    check('U0 고치기 전 판(%s) scripts 를 풀 수 있다' % RELEASE_230[:8], (old / 'backstop.py').is_file())
    same_version = plugin_version(old) == plugin_version(SCRIPTS)

    def both(p, label, base, nonempty=None):
        for name, args in (('게이트(--diff-base)', ('--diff-base', base)), ('--slice-end', ('--diff-base', base, '--slice-end')),
                           ('--only im', ('--diff-base', base, '--only', 'im')), ('--all', ('--all',))):
            new = backstop(p.root, *args)
            before = backstop(p.root, *args, scripts=old)
            check('U %s · %s — 2.3.0 과 byte 동일' % (label, name), new == before,
                  '새 판 exit=%d\n%s\n옛 판 exit=%d\n%s' % (new[0], new[1][-900:], before[0], before[1][-900:]))
            if name == '--all' and nonempty:
                check('U %s · --all — 헛대조 아님(%s)' % (label, nonempty), nonempty in new[1], new[1][-600:])
        p.commit('land as debt')
        for name, extra in (('--debt-scan', ()), ('--debt-scan --refactor', ('--refactor',))):
            e1, out1, data1 = p.scan(*extra)
            e0, out0, data0 = p.scan(*extra, scripts=old)
            check('U %s · %s 출력 — 2.3.0 과 byte 동일' % (label, name), (e1, out1) == (e0, out0),
                  out1[-600:] + '\n---\n' + out0[-600:])
            check('U %s · %s JSON — scanned_at 빼고 같음' % (label, name),
                  strip_stamp(data1, same_version) == strip_stamp(data0, same_version) and bool(data1.get('scanner')),
                  '%r\n%r' % (sorted(data1.get('counts', {}).items()), sorted(data0.get('counts', {}).items())))

    # 선언 없는 프로젝트 — 공백 뒤 토큰 꼴이 들어 있어도 혼입 판정 자체가 없다
    p, _base = mkdeclared(tmp / 'none')
    p.rm(REGISTRY)
    base = p.commit('undeclare')
    put(p, SPACED_LINES + KEPT_LINES + QUIET_LINES)
    p.sub('web/' + ORDER_PAGE, '{% block content %}', '{% block content %}\n' + tag("'" + OWN + "' extra %}"))
    both(p, '선언 없음(공백 뒤 토큰 꼴 있음)', base, 'BLOCKER')

    # 선언 있음 — 공백 뒤 토큰 꼴이 없는 입력(2.3.0 에서 서던 꼴 + 동적 꼴)
    p, base = mkdeclared(tmp / 'declared')
    put(p, KEPT_LINES + DYNAMIC_LINES)
    both(p, '선언 있음(공백 뒤 토큰 꼴 없음)', base, 'IM13] BLOCKER')

    # 선언 있음 — 공백 뒤 토큰 꼴이 자기 제품 파일만 가리키거나 닫히지 않는다(확정돼도 혼입이 아니다)
    p, base = mkdeclared(tmp / 'own')
    put(p, QUIET_LINES)
    both(p, '선언 있음(공백 뒤 토큰 꼴 = 자기 제품 · 닫히지 않음)', base)

    # 바뀌는 곳은 공백 뒤 토큰 꼴뿐이다 — 2.3.0 은 그 줄을 놓치고(IM13 0) 지금 판은 줄마다 선다
    p, base = mkdeclared(tmp / 'diff')
    first = put(p, SPACED_LINES)
    e0, out0 = backstop(p.root, '--diff-base', base, '--only', 'im13', scripts=old)
    e1, out1 = backstop(p.root, '--diff-base', base, '--only', 'im13')
    check('U 선언 있음(공백 뒤 토큰 꼴 = 남의 표준 CSS) — 2.3.0 은 0(exit 0) · 지금 판은 줄마다 IM13(exit 2)',
          e0 == 0 and im13(out0) == [] and e1 == 2 and im13(out1) == list(range(first, first + len(SPACED_LINES))),
          '옛 판 exit=%d %r\n새 판 exit=%d %r' % (e0, im13(out0), e1, im13(out1)))


def main():
    bundles = [bundle_predicate, bundle_loaded, bundle_quiet, bundle_kept, bundle_unchanged]
    only = set(sys.argv[1:])
    for bundle in bundles:
        if only and bundle.__name__[len('bundle_'):] not in only:
            continue
        with tempfile.TemporaryDirectory(prefix='web231-static-') as tmp:
            try:
                bundle(Path(tmp))
            except Exception as error:  # noqa: BLE001 — 묶음이 죽어도 실패로 세고 다음 묶음을 돈다
                check('%s — 묶음 실행 오류' % bundle.__name__, False, '%s: %s' % (type(error).__name__, error))
    print('static 공백 뒤 토큰 픽스처: PASS %d / FAIL %d' % (PASS, FAIL))
    return bool(FAIL)


if __name__ == '__main__':
    sys.exit(main())
