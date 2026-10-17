#!/usr/bin/env python3
"""2.6.0 SH5 회귀 — 공유 머리 CSS 를 무엇으로 다시 재는가(실림 · 갈래 열쇠 · 개수 · 열쇠 만들기).

2.6.0 의 SH5 는 «새로 실린 CSS 파일»과 «기준점에 같은 갈래 열쇠((묶음 at-rule 머리, 선택자, 몸))가 남아 있지 않은 규칙»만
잰다. load 태그 순서만 · 규칙 차례만 · 뜻 없는 공백 · 주석만 바뀐 규칙은 다시 세지 않는다. 열쇠는 문자열 · 이스케이프를
글자 그대로 한 단위로 두고, 주석은 문자열 밖에서만 지운다(빈 글자). 쌍점 앞 · `!` 뒤 공백은 지우지 않는다(2.5.2 처럼 다시 셈).

장면마다 같은 합성 프로젝트에 두 러너를 돌린다 — 이 판(SCRIPTS)과 배포판 2.5.2(RELEASE_252 를 `git archive` 로 임시 폴더에 푼
scripts — HEAD 에 묶지 않는다). 칸은 셋이다.
  RED  — 2.5.2 에서 붉음 먼저: 2.5.2 의 SH5 수가 기대와 다르고 이 판은 기대와 같다. 이 판 발견 줄은 2.5.2 발견 줄의 부분
         집합이다(새로 실린 CSS 를 2.6.0 이 새로 재는 장면 NEW 만 예외).
  SAME — 2.5.2 와 같아야 함: 이 판의 출력(exit · SH5 줄 · SH5 알림 줄)이 2.5.2 와 글자 그대로 같다.
  MUT  — 고침 되돌림 변형: 이 판 scripts 를 임시 폴더에 복사해 고친 자리 하나를 되돌리면 지정 장면이 붉다(기대와 다르다).
2.5.2 커밋이 이력에 없으면(얕은 clone 등) RED · SAME 의 2.5.2 대조만 건너뛰고 건너뛴 사실을 낸다(실패로 세지 않는다).
임시 git 저장소만 만들고 끝나면 지운다(네트워크 · 브라우저 없음). 인자로 장면 이름을 주면 그 장면만 돈다."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TEST = Path(__file__).resolve().parent
SCRIPTS = TEST.parent
REPO = SCRIPTS.parents[1]
sys.path.insert(0, str(TEST))
from fixtures_patch230 import ENV, FLAT_SHELL, GUEST_SHELL, TOKENS, git, mkbc, mkstd, own_root, run_script  # noqa: E402
from fixtures_patch240_shell import PARSER_WRAPPER, load, shell_text  # noqa: E402

RELEASE_252 = 'de3c55cf'  # 2.5.2 배포 커밋(SH5 가 load 순서 · 차례 · 공백 · 주석만 바뀐 규칙도 다시 재던 판) — 올리지 않는다
PASS = FAIL = 0

B = 'static/application/board/'
BODY, FEED, POST, SEARCH = (B + 'board_list_body_section.css', B + 'board_list_feedback_section.css',
                            B + 'board_post_view.css', B + 'board_list_search_section.css')
CSS = {  # 기준점부터 있던 위반: board-list block 을 세 파일이 나눠 씀 · 맨 선택자 h1
    BODY: ['.board-list { padding: 0; }', '.board-list__bar { position: sticky; }', '.board-list__header h1 { margin: 0; }'],
    FEED: ['.board-list > .status-feedback { margin: 0; }'],
    POST: ['.board-post-view { display: block; }', 'h1 { font-size: 2rem; }'],
    SEARCH: ['.board-list:has([data-search]:not([hidden])) .board-list__header { display: none; }'],
}
HEAD_PRE = (['design_system/foundation/app_%s.css' % t for t in TOKENS]
            + ['design_system/theme/app_theme.css', 'static/root/root_view.css',
               'design_system/component/button/primary_button.css'])
HEAD_POST = ['static/application/order/order_list_view.css', 'static/htmx/htmx.min.js', 'static/js/root_shell.js']
ORDER = sorted([SEARCH, POST, FEED, BODY])  # 경로 순(SH4)
LEGACY = [SEARCH, POST, FEED, BODY]  # 경로 순이 아닌 옛 순서
GHEAD = (['design_system/guest/foundation/app_%s.css' % t for t in TOKENS]
         + ['design_system/guest/theme/app_theme.css', 'static/root/root_guest_view.css'])
LOBBY_CSS = 'static/application/lobby/lobby_view.css'


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok and detail:
        print('    ' + str(detail).replace('\n', '\n    ')[:2400])


def head(order, shell=FLAT_SHELL):
    return shell_text(shell, HEAD_PRE + order + HEAD_POST)


def project(root, kind):
    """장면 바탕 → (Proj, 기준점 sha, 실행 루트). flat = 경로 순 head · legacy = 옛 순서 head · sub = 저장소 하위 폴더 ·
    decl = 두 제품 선언(flat 운영자 셸 + own 손님 셸) · unread = 옛 순서 head(기준점 셸을 파서가 못 읽게 만드는 장면용)."""
    git_top = None
    if kind == 'sub':
        git_top = root
        root = root / 'svc'
    p = mkstd(root, git_top=git_top)
    p.w('web/static/js/root_shell.js', 'document.addEventListener("htmx:load", () => {});')
    p.w('web/static/root/root_view.css', '.root-tab-bar { display: flex; }')
    mkbc(p, 'application/board', page=False)
    for path, rules in CSS.items():
        p.w('web/' + path, *rules)
        stem = Path(path).stem
        p.w('web/application/board/presentation_layer/%s/%s.html' % ('view' if stem.endswith('_view') else 'section', stem),
            '<div class="%s"></div>' % stem)
    if kind == 'decl':
        p.w('web/static/root/root_guest_view.css', '.root-tab-bar { display: flex; }')
        mkbc(p, 'application/lobby', page=False)
        p.w('web/' + LOBBY_CSS, '.lobby-view { display: block; }', 'h3 { margin: 0; }')
        own_root(p, 'guest')
        p.declare({'operator': {'design_system': 'flat', 'bcs': ['order', 'board']},
                   'guest': {'design_system': 'own', 'bcs': '*'}})
        p.w('web/' + GUEST_SHELL, shell_text(GUEST_SHELL, GHEAD + [LOBBY_CSS, 'static/htmx/htmx.min.js',
                                                                    'static/js/root_shell.js']))
    p.w('web/' + FLAT_SHELL, head(LEGACY if kind in ('legacy', 'sub', 'unread') else ORDER))
    p.markers()
    if git_top is not None:
        git(git_top, 'add', '-A')
        git(git_top, 'commit', '-qm', 'base')
        return p, git(git_top, 'rev-parse', 'HEAD'), root
    return p, p.commit('base'), p.root


def sh5(scripts, root, base, wrapper=None):
    """SH5 만 돈 출력 → (exit, SH5 발견 줄(머리 + 위반 줄) · SH5 알림 줄 목록, 원문)."""
    args = ['--diff-base', base, '--only', 'sh5']
    if wrapper is None:
        code, out = run_script(scripts / 'backstop.py', root, *args)
    else:
        r = subprocess.run([sys.executable, '-B', str(wrapper), str(scripts / 'backstop.py'), str(root), *args],
                           capture_output=True, text=True, env=ENV)
        code, out = r.returncode, r.stdout + r.stderr
    got = out.splitlines()
    lines = []
    for i, line in enumerate(got):
        if line.startswith('[SH5]'):
            lines.append(line + ' | ' + (got[i + 1].strip() if i + 1 < len(got) else ''))
        elif line.startswith('[info] SH5') or '내부 오류' in line or 'Traceback' in line:
            lines.append(line)
    return code, lines, out


def count(result):
    return sum(1 for line in result[1] if line.startswith('[SH5]'))


# ── 장면 ── 각 setup(p, base) 은 base 상태의 프로젝트를 바꾸고, 다른 기준점을 쓰면 그 sha 를 돌려준다.

def rule_base(p, rel, *rules):
    p.w('web/' + rel, *rules)
    return p.commit('scene base')


def post_base(p, *rules):
    return rule_base(p, POST, '.board-post-view { display: block; }', *rules)


def body_base(p, selector, decl='position: sticky;'):
    return rule_base(p, BODY, '.board-list { padding: 0; }', selector + ' { ' + decl + ' }', '.board-list__header h1 { margin: 0; }')


def edit(rel, old, new):
    return lambda p, base: p.sub('web/' + rel, old, new)


def post_edit(rules, old, new):
    def setup(p, base):
        b2 = post_base(p, *rules)
        p.sub('web/' + POST, old, new)
        return b2
    return setup


def body_edit(selector, old, new, decl='position: sticky;'):
    def setup(p, base):
        b2 = body_base(p, selector, decl)
        p.sub('web/' + BODY, old, new)
        return b2
    return setup


def reorder(order):
    return lambda p, base: p.w('web/' + FLAT_SHELL, head(order))


def s_r1prime(p, base):
    p.w('web/' + FLAT_SHELL, head([POST, BODY, FEED, SEARCH]))
    alt = p.commit('다른 옛 순서')
    p.w('web/' + FLAT_SHELL, head(ORDER))
    return alt


def s_cb(p, base):
    p.w('web/' + FLAT_SHELL, head(ORDER))
    p.append('web/' + SEARCH, 'h2 { margin: 0; }')
    p.append('web/' + SEARCH, '.board-list__footer { margin: 0; }')
    p.append('web/' + POST, '.board-post-view__title { margin: 0; }')


def new_section(p):
    new = B + 'board_list_empty_section.css'
    p.w('web/' + new, '.board-list__empty { color: gray; }')
    p.w('web/application/board/presentation_layer/section/board_list_empty_section.html', '<div class="board-list__empty"></div>')
    return new


def s_cc(p, base):
    new = new_section(p)
    p.sub('web/' + FLAT_SHELL, load(FEED), load(FEED) + '\n' + load(new))


def s_cc2(p, base):
    p.w('web/' + FLAT_SHELL, head(sorted(LEGACY + [new_section(p)])))


def s_p3b(p, base):
    frame = B + 'board_frame_section.css'
    p.w('web/' + frame, '.board-frame { height: 100%; }', '.board-frame__mount { min-height: 1px; }')
    p.w('web/application/board/presentation_layer/section/board_frame_section.html', '<div class="board-frame"></div>')
    p.sub('web/' + FLAT_SHELL, load(BODY), load(BODY) + '\n' + load(frame))
    p.commit('frame 파일')
    p.append('web/' + BODY, '.board-frame:has([data-layer]:not(:empty)) .board-list__bar { visibility: hidden; }')
    landed = p.commit('문맥 규칙 착륙')
    p.w('web/' + FLAT_SHELL, head(sorted(LEGACY + [frame])))
    return landed


def s_h1(p, base):
    b2 = rule_base(p, BODY, '.board-list { padding: 0; }', '.board-list__bar { position: sticky; }',
                   '.board-list__header h1, h2 { margin: 0; }')
    p.sub('web/' + BODY, '.board-list__header h1, h2 { margin: 0; }', 'h2, .board-list__header h1 { margin: 0; }')
    return b2


def s_h1b(p, base):
    b2 = s_h1(p, base)
    p.sub('web/' + BODY, 'h2, .board-list__header h1 { margin: 0; }', 'h2 , .board-list__header  h1 { margin: 0; } /* x */')
    return b2


def s_h1c(p, base):
    b2 = s_h1(p, base)
    p.sub('web/' + BODY, 'h2, .board-list__header h1 { margin: 0; }', 'h2,.board-list__header>h1 { margin: 0; }')
    return b2


def load_off(wrap):
    def setup(p, base):
        shell = p.read('web/' + FLAT_SHELL)
        line = load(POST)
        p.w('web/' + FLAT_SHELL, shell.replace(line, wrap(line)))
        b2 = p.commit('post load 꺼 둠')
        p.w('web/' + FLAT_SHELL, shell)
        return b2
    return setup


def s_rev_tail(p, base):
    shell = p.read('web/' + FLAT_SHELL)
    rev = '?v={{ root_state.shell_rev }}'
    p.w('web/' + FLAT_SHELL, shell.replace("board_post_view.css' %}" + rev, "board_post_view.css' %}"))
    b2 = p.commit('post load 꼬리 없음')
    p.w('web/' + FLAT_SHELL, shell)
    return b2


def s_dotdot(p, base):
    p.sub('web/' + FLAT_SHELL, "'web/application/board/board_post_view.css'",
          "'web/application/board/../board/board_post_view.css'")


def s_rename(p, base):
    new = B + 'board_post_detail_view.css'
    p.mv('web/' + POST, 'web/' + new)
    p.w('web/' + FLAT_SHELL, head(sorted([SEARCH, new, FEED, BODY])))


def s_swap(p, base):
    a, b = p.read('web/' + BODY), p.read('web/' + FEED)
    (p.root / 'web' / BODY).write_text(b, encoding='utf-8')
    (p.root / 'web' / FEED).write_text(a, encoding='utf-8')


def s_move(p, base):
    p.sub('web/' + BODY, '.board-list__bar { position: sticky; }\n', '')
    p.append('web/' + FEED, '.board-list__bar { position: sticky; }')


def s_move_bare(p, base, value='2rem'):
    p.sub('web/' + POST, 'h1 { font-size: 2rem; }\n', '')
    p.append('web/' + SEARCH, 'h1 { font-size: %s; }' % value)


def s_media_out(p, base):
    b2 = post_base(p, '@media (min-width: 1px) { h1 { font-size: 2rem; } }')
    p.w('web/' + POST, '.board-post-view { display: block; }', 'h1 { font-size: 2rem; }')
    return b2


def s_a7(p, base):
    b2 = post_base(p, '@media (min-width:1px) { h1 { font-size: 2rem; } }')
    p.w('web/' + POST, '.board-post-view { display: block; }', 'h1 { font-size: 2rem; }',
        '@media (min-width: 1px) { h1 { font-size: 2rem; } }')
    return b2


def s_print_unwrap(p, base):
    b2 = rule_base(p, BODY, '.board-list { padding: 0; }', '@media print {', 'h2 { margin: 0; }', '}')
    p.w('web/' + BODY, '.board-list { padding: 0; }', 'h2 { margin: 0; }')
    return b2


def s_multi(new_decl):
    def setup(p, base):
        b2 = post_base(p, 'h1 {', '  font-size: 2rem;', '}')
        p.sub('web/' + POST, '  font-size: 2rem;', new_decl)
        return b2
    return setup


def s_fold(p, base):
    b2 = post_base(p, 'h1 {', '  font-size: 2rem;', '}')
    p.w('web/' + POST, '.board-post-view { display: block; }', 'h1 { font-size: 2rem; }')
    return b2


def s_nested_value(p, base):
    b2 = rule_base(p, BODY, '.board-list { padding: 0; & h4 { margin: 0; } }', '.board-list__bar { position: sticky; }',
                   '.board-list__header h1 { margin: 0; }')
    p.sub('web/' + BODY, '& h4 { margin: 0; }', '& h4 { margin: 1px; }')
    return b2


def s_brace_string(p, base):
    b2 = rule_base(p, POST, '.board-post-view::after { content: "}"; }', 'h1 { font-size: 2rem; }')
    p.sub('web/' + POST, 'h1 { font-size: 2rem; }', 'h1 { font-size: 3rem; }')
    return b2


def s_list3(p, base):
    b2 = rule_base(p, BODY, '.board-list { padding: 0; }', 'h2, h3, .board-list__bar { margin: 0; }',
                   '.board-list__header h1 { margin: 0; }')
    p.sub('web/' + BODY, 'h2, h3, .board-list__bar { margin: 0; }', 'h2, h3, .board-list__bar { margin: 1px; }')
    return b2


def s_extra(p, base):  # 이스케이프 · 공백 수 · 따옴표 안 공백을 한 바탕에(맨 선택자 h3 ~ h6 · 겹친 card block)
    p.append('web/' + POST, 'h4 { --token: \\61; }', 'h5 { color:red; }', 'h6 {  color: red;  }', 'h3 {', '  margin: 0;', '}',
             '.card[data-key="a  b"] { color: red; }')
    p.append('web/' + FEED, '.card__name { margin: 0; }')  # card block 을 두 파일이 나눠 씀(겹침)
    return p.commit('extra base')


def extra(old, new, rel=POST):
    def setup(p, base):
        b2 = s_extra(p, base)
        p.sub('web/' + rel, old, new)
        return b2
    return setup


def s_x3(p, base):
    b2 = s_extra(p, base)
    p.w('web/' + FLAT_SHELL, head(list(reversed(ORDER))))
    p.sub('web/' + POST, 'h5 { color:red; }', 'h5 { color: red }')
    return b2


def s_n1(p, base):
    b2 = post_base(p, 'h1 { font-size: 2rem; }', '@media (min-width: 1px) { h1 { font-size: 2rem; } }')
    p.w('web/' + POST, '@media (min-width: 1px) { h1 { font-size: 2rem; } }', '.board-post-view { display: block; }',
        'h1 { font-size: 2rem; }', '@media (min-width: 1px) { h1 { font-size: 2rem; } }')
    return b2


def s_two_new(p, base):
    p.sub('web/' + POST, 'h1 { font-size: 2rem; }\n', '')
    p.append('web/' + FEED, 'h1 { font-size: 2rem; }')
    p.append('web/' + SEARCH, 'h1 { font-size: 2rem; }')


def s_sub_extra(p, base):
    p.w('web/' + FLAT_SHELL, head(ORDER))
    p.append('web/' + POST, 'h1 { color: red; }')


def s_guest_loads(p, base):
    g = p.read('web/' + GUEST_SHELL)
    p.w('web/' + GUEST_SHELL, g.replace(load(LOBBY_CSS), load(LOBBY_CSS) + '\n' + load(POST)))


def s_guest_move(p, base):
    p.declare({'operator': {'design_system': 'flat', 'bcs': ['order']}, 'guest': {'design_system': 'own', 'bcs': '*'}})


def s_unread(p, base):
    s = p.read('web/' + FLAT_SHELL)
    p.w('web/' + FLAT_SHELL, s.replace('</head>', '<![foo]></head>'))
    b2 = p.commit('기준점 셸을 파서가 못 읽음(흉내)')
    p.w('web/' + FLAT_SHELL, head(ORDER))
    return b2


H1 = 'h1 { font-size: 2rem; }'
URL_N1 = ('h1 { background-image: url(old.png); background-image: url(! a.png); }', 'url(! a.png)', 'url(!a.png)')
URL_N2 = ('h1 { background-image: url(old.png); background-image: url(https://example.test/x;a :b); }', ';a :b)', ';a:b)')

# (이름, 제목, 바탕, setup, 기대 SH5 수, 칸 'RED' | 'NEW'(RED 이되 2.6.0 이 새로 재는 장면 — 부분 집합 예외) | 'SAME')
SCENES = [
    # 실림 — load 순서만 · 꼬리 · 경로 꼴(새로 실린 파일이 아니다)
    ('R1', 'load 태그 순서만 경로 순으로', 'legacy', reorder(ORDER), 0, 'RED'),
    ('R1b', '다른 옛 순서 → 같은 경로 순 head', 'legacy', s_r1prime, 0, 'RED'),
    ('P3b', '착륙 뒤 기준점에서 순서만(문맥 파일 줄이 움직임)', 'legacy', s_p3b, 0, 'RED'),
    ('Cb', '순서 바꿈 + 안 움직인 파일에 새 규칙 셋(겹친 block · 맨 선택자만 잼)', 'legacy', s_cb, 2, 'RED'),
    ('Cc2', '새 CSS 파일 하나 + 경로 순 재배치(새 파일만 잼)', 'legacy', s_cc2, 1, 'RED'),
    ('s1', '하위 폴더 루트 · 순서만', 'sub', reorder(ORDER), 0, 'RED'),
    ('s2', '하위 폴더 루트 · 순서만 + 맨 h1 새 규칙', 'sub', s_sub_extra, 1, 'RED'),
    ('i1', 'load 줄에 ?v= 꼬리만 더함', 'flat', s_rev_tail, 0, 'RED'),
    ('i3', 'load 경로를 ../ 로만 다르게(같은 파일)', 'flat', s_dotdot, 0, 'RED'),
    ('k1', '기준점에 여러 줄 HTML 주석으로 꺼 둔 load 를 켬(새로 실림)', 'flat',
     load_off(lambda line: '<!--\n' + line + '\n-->'), 1, 'NEW'),
    ('k2', '기준점에 {% comment %} 로 꺼 둔 load 를 켬(새로 실림)', 'flat',
     load_off(lambda line: '{% comment %}\n' + line + '\n{% endcomment %}'), 1, 'NEW'),
    # 갈래 열쇠 — 차례 · 공백 · 주석만(같은 규칙)
    ('h1', '선택자 목록 차례만 바꿈', 'flat', s_h1, 0, 'RED'),
    ('h1b', '선택자 목록 공백 · 뒤 주석만 바꿈', 'flat', s_h1b, 0, 'RED'),
    ('h1c', '결합자 둘레 공백을 없앰(.a h1 → .a>h1 은 다른 선택자 · 차례만인 h2 는 침묵)', 'flat', s_h1c, 1, 'RED'),
    ('a7', '@media 머리 쌍점 뒤 공백만 다른 규칙 + 맨 위 새 h1(새 h1 만)', 'flat', s_a7, 1, 'RED'),
    ('q4', '속성 선택자 깃발 앞 공백만 없앰', 'flat',
     body_edit('.board-list__bar[data-k="a" i]', '[data-k="a" i]', '[data-k="a"i]'), 0, 'RED'),
    ('q5', '선택자 뒤 주석만 더함', 'flat',
     edit(BODY, '.board-list__bar { position: sticky; }', '.board-list__bar /* 막대 */ { position: sticky; }'), 0, 'RED'),
    ('c3', '선언 쌍점 뒤 공백만 더함', 'flat', post_edit(['h1 { font-size:2rem; }'], 'font-size:2rem', 'font-size: 2rem'),
     0, 'RED'),
    ('c2', '끝 쌍반점만 더함', 'flat', post_edit(['h1 { font-size: 2rem }'], '2rem }', '2rem; }'), 0, 'RED'),
    ('c4', '선언 사이에 주석만 넣음(공백 없이)', 'flat',
     post_edit(['h1 { font-size: 2rem;color: red; }'], '2rem;color', '2rem;/* 크기 */color'), 0, 'RED'),
    ('c4b', '선언 사이에 주석만 넣음(공백 둘레)', 'flat',
     post_edit(['h1 { font-size: 2rem; color: red; }'], '2rem; color', '2rem; /* 크기 */ color'), 0, 'RED'),
    ('c10', '여러 줄 h1 규칙을 한 줄로 접음', 'flat', s_fold, 0, 'RED'),
    ('e2', '쌍점 뒤 공백만(h5)', 'flat', extra('h5 { color:red; }', 'h5 { color: red; }'), 0, 'RED'),
    ('e3', '이미 있던 공백 수만(h6)', 'flat', extra('h6 {  color: red;  }', 'h6 { color: red; }'), 0, 'RED'),
    ('x2', '따옴표 밖 공백만', 'flat',
     extra('.card[data-key="a  b"] { color: red; }', '.card[data-key="a  b"]  {  color: red;  }'), 0, 'RED'),
    ('x3', '순서 바꿈 + 쌍점 공백 · 끝 쌍반점만', 'flat', s_x3, 0, 'RED'),
    ('w6', ':nth-child(2n + 1) → (2n+1)', 'flat',
     body_edit('.board-list__bar:nth-child(2n + 1)', '(2n + 1)', '(2n+1)'), 0, 'RED'),
    ('w7', '[x = "y"] → [x="y"]', 'flat', body_edit('.board-list__bar[data-k = "y"]', '[data-k = "y"]', '[data-k="y"]'),
     0, 'RED'),
    ('w8', '사용자 속성 값 안 공백 둘 → 하나', 'flat', post_edit(['h1 { --gap: a  b; }'], 'a  b', 'a b'), 0, 'RED'),
    ('w10', 'url( "x" ) → url("x")', 'flat',
     post_edit(['h1 { background: url( "x.png" ); }'], 'url( "x.png" )', 'url("x.png")'), 0, 'RED'),
    ('k7', '자손 공백 사이에 주석만 넣음', 'flat', body_edit('.board-list__bar .x', '__bar .x', '__bar /* c */ .x'), 0, 'RED'),
    ('m5', '"/*" 문자열 뒤에 진짜 주석만 더함', 'flat',
     post_edit(['h1 { content: "/*"; color: red; }'], '"/*"; color', '"/*"; /* note */ color'), 0, 'RED'),
    # 2.5.2 와 같아야 함 — 새 규칙 · 개수 · 값 · 문맥 · 옮김 · 파일
    ('b1', '맨 h1 을 같은 파일에 새 규칙으로 한 번 더', 'flat', lambda p, b: p.append('web/' + POST, 'h1 { color: red; display: none; }'),
     1, 'SAME'),
    ('b2', '겹친 block 의 기존 갈래를 같은 파일에 한 번 더', 'flat',
     lambda p, b: p.append('web/' + BODY, '.board-list__bar { top: 0; z-index: 9; }'), 1, 'SAME'),
    ('b3', '같은 갈래를 새 @media 문맥에', 'flat',
     lambda p, b: p.append('web/' + BODY, '@media (min-width: 1px) { .board-list__bar { top: 0; } }'), 1, 'SAME'),
    ('a3', '같은 규칙을 다른(이미 실린) 파일에도 하나 더', 'flat', lambda p, b: p.append('web/' + SEARCH, H1), 1, 'SAME'),
    ('a4', '같은 h1 규칙을 기존 규칙 위에 하나 더(개수 1 → 2)', 'flat',
     lambda p, b: p.w('web/' + POST, H1, '.board-post-view { display: block; }', H1), 1, 'SAME'),
    ('a5', '맨 h1 을 @media 안으로 옮김(문맥 바뀜)', 'flat',
     lambda p, b: p.w('web/' + POST, '.board-post-view { display: block; }', '@media (min-width: 1px) { ' + H1 + ' }'), 1, 'SAME'),
    ('a6', '@media 안 h1 을 맨 위로 꺼냄', 'flat', s_media_out, 1, 'SAME'),
    ('n1', '두 문맥에 같은 h1 — 차례 바꿈 + @media 안 h1 하나 더', 'flat', s_n1, 1, 'SAME'),
    ('n5', '맨 h1 을 걷고 다른 두 파일에 붙임', 'flat', s_two_new, 2, 'SAME'),
    ('v1', '맨 h1 규칙의 선언만 바꿈(한 줄)', 'flat', edit(POST, H1, 'h1 { font-size: 2rem; display: none; }'), 1, 'SAME'),
    ('v2', '여러 줄 h1 규칙의 선언 줄만 더함(선택자 줄 무변 — 2.5.2 범위)', 'flat', s_multi('  font-size: 2rem;\n  color: red;'),
     0, 'SAME'),
    ('c9', '여러 줄 h1 규칙의 선언 줄 값만 바꿈(2.5.2 범위)', 'flat', s_multi('  font-size: 2rem; display: none;'), 0, 'SAME'),
    ('c1', '선언 차례만 바꿈(몸이 다름)', 'flat',
     post_edit(['h1 { font-size: 2rem; color: red; }'], 'font-size: 2rem; color: red;', 'color: red; font-size: 2rem;'), 1, 'SAME'),
    ('c5', '!important 더함', 'flat', edit(POST, H1, 'h1 { font-size: 2rem !important; }'), 1, 'SAME'),
    ('c6', '중첩 규칙(&) 안의 값만 바꿈', 'flat', s_nested_value, 1, 'SAME'),
    ('c7', '문자열 안 } 가 있는 파일에서 h1 값 바꿈', 'flat', s_brace_string, 1, 'SAME'),
    ('c8', '선택자 목록 셋 규칙의 값만 바꿈', 'flat', s_list3, 3, 'SAME'),
    ('e1', '이스케이프 값 바꿈(\\61 → \\6 1)', 'flat', extra('h4 { --token: \\61; }', 'h4 { --token:\\6 1; }'), 1, 'SAME'),
    ('e4', '한 줄 규칙 값 바꿈', 'flat', extra('h5 { color:red; }', 'h5 { color:blue; }'), 1, 'SAME'),
    ('e5', '여러 줄 규칙 선언 줄만 값 바꿈(2.5.2 범위)', 'flat', extra('  margin: 0;\n}', '  margin: 4px;\n}'), 0, 'SAME'),
    ('x1', '따옴표 안 공백만 다른 선택자', 'flat', extra('.card[data-key="a  b"]', '.card[data-key="a b"]'), 1, 'SAME'),
    ('q1', '따옴표 안 공백만 바꿈(겹친 block)', 'flat',
     body_edit('.board-list__bar[data-k="a b"]', '[data-k="a b"]', '[data-k="a  b"]'), 1, 'SAME'),
    ('q3', '속성 선택자 i → s 깃발', 'flat', body_edit('.board-list__bar[data-k="a" i]', '"a" i]', '"a" s]'), 1, 'SAME'),
    ('q6', '자손 공백을 주석으로(.a .b → .a/**/.b)', 'flat',
     body_edit('.board-list .board-list__bar', '.board-list .board-list__bar', '.board-list/* x */.board-list__bar'), 1, 'SAME'),
    ('q7', '작은따옴표 안 큰따옴표 + 공백 바꿈', 'flat',
     body_edit(".board-list__bar[data-k='it\"s  x']", "'it\"s  x'", "'it\"s x'"), 1, 'SAME'),
    ('k6', '자손 공백을 주석으로(.a .x → .a/* c */.x)', 'flat', body_edit('.board-list__bar .x', '__bar .x', '__bar/* c */.x'),
     1, 'SAME'),
    ('w1', 'calc(1px + 2px) → calc(1px+2px)', 'flat', post_edit(['h1 { width: calc(1px + 2px); }'], '1px + 2px', '1px+2px'),
     1, 'SAME'),
    ('w5', '.x :hover → .x:hover', 'flat', body_edit('.board-list__bar :hover', '__bar :hover', '__bar:hover'), 1, 'SAME'),
    ('w9', '문자열 안 공백 둘 → 하나', 'flat', post_edit(['h1 { content: "a  b"; }'], '"a  b"', '"a b"'), 1, 'SAME'),
    ('w11', '.x *.y → .x*.y', 'flat', body_edit('.board-list__bar *.x', '__bar *.x', '__bar*.x'), 1, 'SAME'),
    # 문자열 안 주석 모양(Codex 반례 B9 · m1 · m3) — 문자열은 글자 그대로
    ('b9b', 'B9 몸 — content:"/*alice*/" → "/*bob*/"', 'flat',
     post_edit(['h1::before { content:"/*alice*/"; }'], '/*alice*/', '/*bob*/'), 1, 'SAME'),
    ('b9s', 'B9 선택자 — [data-key="/*alice*/"] → "/*bob*/"', 'flat',
     body_edit('.board-list__bar[data-key="/*alice*/"]', '/*alice*/', '/*bob*/'), 1, 'SAME'),
    ('m1', '[data-k="/*a*/"] → "/*b*/"(겹친 block)', 'flat', body_edit('.board-list__bar[data-k="/*a*/"]', '/*a*/', '/*b*/'),
     1, 'SAME'),
    ('m3', 'content: "/*" 뒤 선언 더함(닫히지 않은 주석 모양)', 'flat',
     post_edit(['h1 { content: "/*"; color: red; }'], 'color: red;', 'color: red; display: none;'), 1, 'SAME'),
    # 쌍점 앞 · ! 뒤 공백은 지우지 않음(2.5.2 처럼 다시 셈 — Codex 반례 N1 ~ N3b 와 같은 자리)
    ('w2', '! important → !important', 'flat', post_edit(['h1 { color: red ! important; }'], 'red ! imp', 'red !imp'),
     1, 'SAME'),
    ('w3', 'color : red → color: red', 'flat', post_edit(['h1 { color : red; }'], 'color : red', 'color: red'), 1, 'SAME'),
    ('w4', '@media (min-width : 1px) → (min-width: 1px)', 'flat',
     post_edit(['@media (min-width : 1px) { h1 { font-size: 2rem; } }'], 'width : 1px', 'width: 1px'), 1, 'SAME'),
    ('N1', 'url(! a.png) → url(!a.png)(다른 그림)', 'flat', post_edit([URL_N1[0]], URL_N1[1], URL_N1[2]), 1, 'SAME'),
    ('N2', 'url(…;a :b) → url(…;a:b)(URL 안 ;)', 'flat', post_edit([URL_N2[0]], URL_N2[1], URL_N2[2]), 1, 'SAME'),
    ('N3', '@supports (…:ur\\6c(https ://…)) → (https://…)', 'flat',
     post_edit(['@supports (background-image:ur\\6c(https ://example.test/x)) { h1 { color: red; } }'], 'https :', 'https:'),
     1, 'SAME'),
    ('N3b', '@supports selecto\\72(a :hover) → (a:hover)', 'flat',
     post_edit(['@supports selecto\\72(a :hover) { h1 { color: red; } }'], '(a :hover)', '(a:hover)'), 1, 'SAME'),
    ('w15', '@supports selector(a :hover) → (a:hover)', 'flat',
     post_edit(['@supports selector(a :hover) { h1 { font-size: 2rem; } }'], '(a :hover)', '(a:hover)'), 1, 'SAME'),
    ('w16', '중첩 & :hover → &:hover', 'flat',
     body_edit('.board-list__bar', '& :hover', '&:hover', 'color: red; & :hover { color: blue; }'), 1, 'SAME'),
    ('w18', '문자열 안 "a : b" → "a: b"', 'flat', post_edit(['h1 { content: "a : b"; }'], '"a : b"', '"a: b"'), 1, 'SAME'),
    # 파일 · 셸 · 제품 · 그 밖
    ('a1', '규칙을 이미 실린 다른 파일로 옮김', 'flat', s_move, 1, 'SAME'),
    ('a2', '맨 h1 을 다른 파일로 옮김', 'flat', s_move_bare, 1, 'SAME'),
    ('e2m', '맨 h1 을 다른 파일로 옮기며 값도 바꿈', 'flat', lambda p, b: s_move_bare(p, b, '3rem'), 1, 'SAME'),
    ('c1f', '파일 이름 바꿈(git mv) + load 줄도 새 이름', 'flat', s_rename, 1, 'SAME'),
    ('c2f', '두 실린 파일의 내용을 서로 바꿈', 'flat', s_swap, 4, 'SAME'),
    ('Cc', '새 CSS 파일 하나를 옛 순서 사이에 실음', 'legacy', s_cc, 1, 'SAME'),
    ('P2a', '순서 그대로 · 기존 한 줄 규칙 값만', 'legacy', edit(SEARCH, 'display: none;', 'display: none; visibility: hidden;'),
     1, 'SAME'),
    ('f1', '겹친 block 새 규칙', 'flat', lambda p, b: p.append('web/' + FEED, '.board-list__bar2 { top: 0; }'), 1, 'SAME'),
    ('f2', '겹침 없는 새 규칙', 'flat', lambda p, b: p.append('web/' + POST, '.board-post-view__title { margin: 0; }'), 0, 'SAME'),
    ('g1', '@media print 감싸기를 걷음(안쪽 줄 무변 — 2.5.2 범위)', 'flat', s_print_unwrap, 0, 'SAME'),
    ('k3', '기준점에 {# #} 로 꺼 둔 load 를 켬', 'flat', load_off(lambda line: '{# ' + line + ' #}'), 1, 'SAME'),
    ('k4', '실린 load 를 주석으로 끔', 'flat', edit(FLAT_SHELL, load(POST), '<!-- ' + load(POST) + ' -->'), 0, 'SAME'),
    ('d0', '두 제품 선언 바탕 그대로', 'decl', lambda p, b: None, 0, 'SAME'),
    ('d1', '다른 셸이 싣던 CSS 를 손님 셸이 새로 실음', 'decl', s_guest_loads, 1, 'SAME'),
    ('d2', '선언만 바꿔 BC 를 손님 제품으로 옮김(load 줄 무변)', 'decl', s_guest_move, 0, 'SAME'),
    ('j1', '기준점 셸을 파서가 못 읽음 + 순서만(줄 기준으로 내려감)', 'unread', s_unread, 4, 'SAME'),
]

# 고침 되돌림 변형 — (이름, 되돌릴 글(check_shell.py 안에 정확히 한 번), 바꿀 글, 붉어야 할 장면)
NEWLY = ('newly = (_changed(ctx, shell, ms, tag.start, tag.open_end) if loaded_before is None\n'
         '                 else path not in loaded_before)')
PREPASS = ('        if before is not None:  # 새 줄 밖에 그대로 남은 갈래가 기준점 몫을 먼저 쓴다(개수 — 같은 갈래를 하나 더 쓰면 그것은 새것)\n'
           '            for start, end, selector, context, body in records:\n'
           '                key = (context, _norm(css.original[start:end]), body)\n'
           '                if not _changed(ctx, file, css, start, end) and before[key] > 0:\n'
           '                    before[key] -= 1\n')
UNITS = ("        match = (_CSS_ESCAPE_RE.match(text, i) if char == '\\\\' else\n"
         "                 _CSS_STRING_RE.match(text, i) if char in ('\"', \"'\") else None)")
COMMENT = ("            i = len(text) if close < 0 else close + 2\n"
           "            continue")
TIGHT = "_TIGHT = {'sel': ('>+~,=([', '>+~,=)]'), 'body': (':,;(', ';,)!')}"
UNITS_START = "    units: List[Tuple[str, str]] = []  # ('c' 글자 | 'u' 문자열·이스케이프 단위 | 's' 공백, 글자)\n"
MUTANTS = [
    ('실림을 줄 기준으로', NEWLY, 'newly = _changed(ctx, shell, ms, tag.start, tag.open_end)', ('R1', 's1')),
    ('개수 먼저 쓰기를 뺌', PREPASS, '', ('a4',)),
    ('문자열 · 이스케이프 단위를 뺌', UNITS, '        match = None', ('x1', 'q1', 'w9')),
    ('주석을 공백으로', COMMENT,
     "            i = len(text) if close < 0 else close + 2\n"
     "            if not units or units[-1][0] != 's':\n"
     "                units.append(('s', ' '))\n"
     "            continue", ('q6', 'k6')),
    ('뜻 없는 공백 지우기를 뺌', TIGHT, "_TIGHT = {'sel': ('', ''), 'body': ('', '')}", ('c3', 'e2')),
    ('`!` 뒤 공백도 지움(덜어 낸 꼴)', TIGHT, "_TIGHT = {'sel': ('>+~,=([', '>+~,=)]'), 'body': (':,;(!', ';,)!')}", ('N1', 'w2')),
    ('문자열 안 주석 지우기(v3 꼴)', UNITS_START,
     UNITS_START + "    text = re.sub(r'/\\*.*?(?:\\*/|\\Z)', '', text, flags=re.S)\n", ('b9b', 'b9s', 'm1', 'm3')),
]


def release_scripts(tmp, sha):
    """커밋 sha 의 scripts 를 임시 폴더에 푼다 → scripts 폴더(이력에 없으면 None)."""
    archive = subprocess.run(['git', '-C', str(REPO), 'archive', sha, 'dddjango-web/scripts', 'dddjango-web/.claude-plugin'],
                             capture_output=True, env=ENV)
    if archive.returncode:
        print('SKIP 2.5.2 대조 — 배포 커밋 %s 가 이 저장소 이력에 없다(얕은 clone 등) — 그 대조만 건너뛴다(실패로 세지 않는다)' % sha)
        return None
    tmp.mkdir()
    subprocess.run(['tar', '-xf', '-', '-C', str(tmp)], input=archive.stdout, check=True)
    return tmp / 'dddjango-web' / 'scripts'


def mutant_scripts(tmp, name, old, new):
    """이 판 scripts 를 tmp 에 복사(링크 아님)하고 check_shell.py 의 한 자리를 되돌린다 → scripts 폴더(자리가 없으면 None)."""
    plugin = tmp / 'dddjango-web'
    shutil.copytree(SCRIPTS, plugin / 'scripts', ignore=shutil.ignore_patterns('__pycache__', 'test'))
    shutil.copytree(SCRIPTS.parent / '.claude-plugin', plugin / '.claude-plugin')
    target = plugin / 'scripts/src/check_shell.py'
    text = target.read_text(encoding='utf-8')
    if text.count(old) != 1:
        check('MUT %s — 되돌릴 자리가 check_shell.py 에 정확히 한 번 있다' % name, False, '찾은 수 %d' % text.count(old))
        return None
    target.write_text(text.replace(old, new), encoding='utf-8')
    return plugin / 'scripts'


def play(tmp, scene, runners):
    """장면 하나를 새 바탕에 만들고 러너마다 SH5 를 돈다 → {러너 이름: 결과}."""
    name, _title, kind, setup, _expect, _cell = scene
    box = tmp / ('scene-' + name)
    p, base, root = project(box, kind)
    diff_base = setup(p, base) or base
    wrapper = None
    if kind == 'unread':
        wrapper = tmp / 'unreadable_parser.py'
        wrapper.write_text(PARSER_WRAPPER, encoding='utf-8')
    out = {label: sh5(scripts, root, diff_base, wrapper) for label, scripts in runners}
    shutil.rmtree(box)
    return out


def main():
    only = set(sys.argv[1:])
    with tempfile.TemporaryDirectory(prefix='web260-sh5-') as tmp_name:
        tmp = Path(tmp_name).resolve()
        old = release_scripts(tmp / 'release', RELEASE_252)
        by_name = {scene[0]: scene for scene in SCENES}
        for scene in SCENES:
            name, title, _kind, _setup, expect, cell = scene
            if only and name not in only:
                continue
            runners = [('new', SCRIPTS)] + ([('old', old)] if old is not None else [])
            try:
                got = play(tmp, scene, runners)
            except Exception as error:
                check('%s 준비 · 실행 오류' % name, False, '%s: %s' % (type(error).__name__, error))
                continue
            new = got['new']
            check('%s %s — SH5 %d(exit %d)' % (name, title, expect, 2 if expect else 0),
                  count(new) == expect and new[0] == (2 if expect else 0) and not any('내부 오류' in line or 'Traceback' in line
                                                                                      for line in new[1]),
                  'exit %d\n%s' % (new[0], '\n'.join(new[1]) or new[2][-1500:]))
            if 'old' not in got:
                continue
            was = got['old']
            if cell == 'SAME':
                check('%s — 2.5.2(%s)와 같은 출력' % (name, RELEASE_252), (was[0], was[1]) == (new[0], new[1]),
                      '2.5.2 exit %d\n%s\n--- 이 판 exit %d\n%s' % (was[0], '\n'.join(was[1]), new[0], '\n'.join(new[1])))
            else:
                check('%s — 2.5.2(%s)는 SH5 %d 이었다(붉음 먼저)' % (name, RELEASE_252, count(was)), count(was) != expect,
                      '\n'.join(was[1]))
                if cell == 'RED':
                    extra_lines = [line for line in new[1] if line not in was[1]]
                    check('%s — 이 판 발견 줄은 2.5.2 발견 줄의 부분 집합' % name, not extra_lines, '\n'.join(extra_lines))
        for index, (label, before, after, scenes) in enumerate(MUTANTS):
            targets = [by_name[s] for s in scenes if not only or s in only]
            if not targets:
                continue
            scripts = mutant_scripts(tmp / ('mutant-%d' % index), label, before, after)
            if scripts is None:
                continue
            for scene in targets:
                try:
                    got = play(tmp, scene, [('mutant', scripts)])['mutant']
                except Exception as error:
                    check('MUT %s · %s 준비 · 실행 오류' % (label, scene[0]), False, '%s: %s' % (type(error).__name__, error))
                    continue
                check('MUT %s → %s 붉음(SH5 %d ≠ 기대 %d)' % (label, scene[0], count(got), scene[4]), count(got) != scene[4],
                      '\n'.join(got[1]))
    print('2.6.0 SH5 픽스처: PASS %d / FAIL %d' % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
