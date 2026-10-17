"""2.6.0 지속 셸 표준 글 · 셸 자료 두 줄 회귀. 실제 임시 git 프로젝트만 검사한다.

S1 = 규칙 글의 root_shell.js 표준 블록이 하나 · 첫 줄 판 표지(Coordinator G0 `head -1`) — 바탕 규칙 글(2.5.2)의 블록에는 표지가 없다.
S2 = 셸 템플릿 두 줄(탭 링크 `data-root-first` 두 벌 · `<main>` 안 `root-who`) · RootTabState `first_href` · RootState `who` — 바탕에는 없다.
S3 = «표준 글 그대로 칸»: 새 표준 셸 · 상태 블록으로 지은 프로젝트의 SH · NM blocker 0(T1 바탕 표준 셸에서 고친 게이트 · T3 새 기준점 그대로 · --all).
S4 = 두 줄의 꼴 위반은 SH2 가 잡는다 — 한 벌만(T4 → 꼴 ⑨) · `{% block content %}` 뒤 `root-who`(T5 → 꼴 ⑦).
바탕(BASELINE)이 이력에 없으면 바탕 대조만 건너뛴 사실을 낸다. 네트워크 · 브라우저는 쓰지 않는다.
"""
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TEST = Path(__file__).resolve().parent
SCRIPTS = TEST.parent
REPO = SCRIPTS.parents[1]
sys.path.insert(0, str(TEST))
sys.path.insert(0, str(SCRIPTS))
from fixtures_patch230 import ENV, FLAT_SHELL, TOKENS, backstop, found, mkbc, mkstd  # noqa: E402

BASELINE = 'de3c55cf'  # dddjango-web 2.5.2 배포 커밋 — 옛 판 대조는 HEAD 가 아니라 이 SHA 로
RULE_PATH = 'dddjango-web/skills/implementation-django/references/final.md'
RULE = REPO / RULE_PATH
SHELL_HEAD = '// web/static/js/root_shell.js'
MARKER = 'root_shell 2.6'
FIRST = ' data-root-first="{{ tab.first_href }}"'
WHO = '{{ root_state.who|json_script:"root-who" }}'
PASS = FAIL = 0


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok:
        print('    ' + str(detail).replace('\n', '\n    ')[:2400])


def rule_block(text, lang, head):
    """규칙 글에서 머리 줄로 시작하는 코드 블록 하나 — 없거나 둘 이상이면 픽스처가 실패한다(조용히 건너뛰지 않는다)."""
    blocks = [m.group(1) for m in re.finditer(r'^```' + lang + r'\n(.*?)\n```$', text, re.S | re.M)
              if m.group(1).startswith(head)]
    if len(blocks) != 1:
        raise RuntimeError('규칙 글 %s 블록 %r — %d 개(하나여야 한다)' % (lang, head, len(blocks)))
    return blocks[0]


def baseline_rule():
    got = subprocess.run(['git', '-C', str(REPO), 'show', '%s:%s' % (BASELINE, RULE_PATH)],
                         capture_output=True, text=True, env=ENV)
    if got.returncode:
        print('SKIP 바탕 대조 — 바탕 커밋 %s 없음' % BASELINE)
        return None
    return got.stdout


def standard_files(text):
    """규칙 글의 지속 셸 root_view.html · root_tab_state.py · root_state.py 블록 — foundation 자리표 한 줄만 여섯 줄로."""
    lines = rule_block(text, 'django', '{# root/scaffold/view/root_view.html — 지속 셸').split('\n')
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


def has_marker(text):
    """G0 판 가림 — 규칙 글에서 뽑은 표준 블록의 첫 줄(`head -1`)에 판 표지가 있는가."""
    return MARKER in rule_block(text, 'javascript', SHELL_HEAD).split('\n')[0]


def has_two_lines(text):
    """셸 자료 두 줄 — 탭 링크 두 벌 모두 data-root-first · <main> 안 content 앞 root-who · 상태 블록 새 칸."""
    files = standard_files(text)
    shell = files['web/' + FLAT_SHELL]
    main = shell[shell.index('<main'):shell.index('</main>')]
    return (shell.count(FIRST) == 2 and main.count(WHO) == 1 and main.index(WHO) < main.index('{% block content %}')
            and 'first_href: str' in files['web/root/scaffold/state/root_tab_state.py']
            and 'who: str | None' in files['web/root/scaffold/state/root_state.py'])


def project(tmp, files):
    """규칙 글 표준 셸 · 상태 블록으로 지은 프로젝트 — fixtures_patch240_shell.bundle_standard 와 같은 바탕."""
    p = mkstd(tmp)
    p.rm('web/static/application/order/order_list_view.css')  # 표준 셸이 싣지 않는 바탕 CSS(SH4 공유 머리)
    p.rm('web/design_system/component/button/primary_button.css')
    mkbc(p, 'application/channel', page=False)  # 표준 셸이 싣는 조각 CSS 의 주인 화면(NM19)
    view = 'web/application/channel/presentation_layer/view/channel_summary_view'
    p.w(view + '.py', 'from django.http import HttpRequest, HttpResponse', 'from django.shortcuts import render', '', '',
        'def channel_summary_view(request: HttpRequest) -> HttpResponse:',
        '    return render(request, "%s.html", {})' % view[len('web/'):])
    p.w(view + '.html', '{% extends "' + FLAT_SHELL + '" %}', '{% block content %}', '<p>channel</p>', '{% endblock %}')
    write(p, files)
    for arg in re.findall(r"\{% static '([^']+)' %\}", files['web/' + FLAT_SHELL]):
        rel = 'web/static/' + arg[len('web/'):] if arg.startswith('web/') else 'web/' + arg
        if (p.root / rel).exists():
            continue
        if rel.endswith('.css'):
            block = 'root-tab-bar' if rel.endswith('/static/root/root_view.css') else Path(rel).stem.replace('_', '-')
            p.w(rel, '.%s { color: var(--color-base); }' % block)
        else:
            p.w(rel, 'document.addEventListener("htmx:load", () => {});')
    return p, p.commit('standard-base')


def write(p, files):
    for rel, text in files.items():
        (p.root / rel).parent.mkdir(parents=True, exist_ok=True)
        (p.root / rel).write_text(text, encoding='utf-8')


def clean(got):
    return got[0] == 0 and 'BLOCKER' not in got[1] and '내부 오류' not in got[1]


def bundle_s1(tmp, base_text):
    text = RULE.read_text(encoding='utf-8')
    block = rule_block(text, 'javascript', SHELL_HEAD) + '\n'
    print('INFO 표준 블록 sha256 = %s · %d 줄' % (hashlib.sha256(block.encode()).hexdigest(), block.count('\n')))
    check('S1 표준 블록 하나 · 첫 줄 판 표지(G0 head -1)', has_marker(text), block.split('\n')[0])
    check('S1 판 표지는 첫 줄에만(둘째 줄 이하에 없음)', MARKER not in block.split('\n', 1)[1], block[:400])
    if base_text is not None:
        check('S1 붉음 먼저 — 바탕(%s) 규칙 글의 블록 첫 줄에는 표지 없음(옛 판)' % BASELINE, not has_marker(base_text),
              rule_block(base_text, 'javascript', SHELL_HEAD).split('\n')[0])


def bundle_s2(tmp, base_text):
    text = RULE.read_text(encoding='utf-8')
    check('S2 셸 자료 두 줄 · 상태 새 칸(규칙 글)', has_two_lines(text), standard_files(text)['web/' + FLAT_SHELL][-1600:])
    if base_text is not None:
        check('S2 붉음 먼저 — 바탕(%s) 규칙 글에는 두 줄 · 새 칸 없음' % BASELINE, not has_two_lines(base_text))


def bundle_s3(tmp, base_text):
    files = standard_files(RULE.read_text(encoding='utf-8'))
    if base_text is not None:  # T1 — 바탕 표준 셸(2.5.2)에서 새 표준 셸로 고친 게이트
        p, base = project(tmp / 't1', standard_files(base_text))
        write(p, files)
        got = backstop(p.root, '--diff-base', base, '--only', 'sh,nm')
        check('S3 T1 바탕 표준 셸 → 새 표준 셸 SH·NM blocker 0(게이트)', clean(got), got)
        got = backstop(p.root, '--diff-base', base, '--slice-end')  # 슬라이스 끝은 --only 와 함께 쓰지 않는다 — SH · NM 머리 줄만 본다
        check('S3 T1 바탕 표준 셸 → 새 표준 셸 SH·NM blocker 0(슬라이스 끝)',
              not re.search(r'^\[(SH|NM)\d+\] BLOCKER', got[1], re.M) and '내부 오류' not in got[1], got)
    p, base = project(tmp / 't3', files)  # T3 — 새 표준 셸이 기준점 · 그대로
    for args in (('--all',), ('--diff-base', base)):
        got = backstop(p.root, *args, '--only', 'sh,nm')
        check('S3 T3 새 표준 셸 그대로 SH·NM blocker 0(%s)' % args[0], clean(got), got)


def bundle_s4(tmp, base_text):
    files = standard_files(RULE.read_text(encoding='utf-8'))
    shell = files['web/' + FLAT_SHELL]
    p, base = project(tmp / 'form', files)
    one = shell.replace(FIRST, '', 1)  # T4 — template(첫 벌)에서 빼고 nav 벌에만
    if one.count(FIRST) != 1:
        raise RuntimeError('픽스처 오류 — data-root-first 두 벌')
    p.w('web/' + FLAT_SHELL, one)
    got = backstop(p.root, '--diff-base', base, '--only', 'sh2')
    check('S4 T4 data-root-first 한 벌만 → SH2(꼴 ⑨)', got[0] == 2 and found(got[1], 'SH2', FLAT_SHELL), got)
    p.reset(base)
    late = shell.replace('    ' + WHO + '\n', '', 1).replace('{% block content %}{% endblock content %}\n',
                                                              '{% block content %}{% endblock content %}\n    ' + WHO + '\n', 1)
    if late.count(WHO) != 1 or late.index(WHO) < late.index('{% block content %}'):
        raise RuntimeError('픽스처 오류 — root-who 자리')
    p.w('web/' + FLAT_SHELL, late)
    got = backstop(p.root, '--diff-base', base, '--only', 'sh2')
    check('S4 T5 root-who 를 content 뒤에 → SH2(꼴 ⑦)', got[0] == 2 and found(got[1], 'SH2', FLAT_SHELL), got)


def main():
    only = set(sys.argv[1:])
    base_text = baseline_rule()
    for bundle in (bundle_s1, bundle_s2, bundle_s3, bundle_s4):
        if only and bundle.__name__[7:] not in only:
            continue
        with tempfile.TemporaryDirectory(prefix='web260-') as tmp:
            try:
                bundle(Path(tmp), base_text)
            except Exception as error:
                check(bundle.__name__ + ' 준비·실행 오류', False, '%s: %s' % (type(error).__name__, error))
    print('2.6.0 지속 셸 표준 글 픽스처: PASS %d / FAIL %d' % (PASS, FAIL))
    return bool(FAIL)


if __name__ == '__main__':
    sys.exit(main())
