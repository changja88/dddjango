#!/usr/bin/env python3
"""2.5.2 git 출력 · 이름 · 밖 읽기 회귀 — 잰 사용자 git 설정 · 속성과 git 이 감싸 표시하던 파일 이름에 판정이 흔들리지 않고,
고친 자리가 프로젝트 밖(링크 너머 · `..` · 프로젝트 밖 작업 파일)을 읽지 않는가. 임시 git 저장소만 만들고 끝나면 지운다
(네트워크 · 브라우저 없음).

사용자 git 설정은 시험 안에서만 건다 — 장면마다 임시 전역 설정 파일(`GIT_CONFIG_GLOBAL`) · 시스템 설정 끔
(`GIT_CONFIG_NOSYSTEM=1`). 실행하는 사람의 전역 설정은 읽지도 바꾸지도 않는다(기본 칸도 이름 · 메일만 든 임시 파일).

장면마다 셋을 본다.
  ① 꼴 — 맨 위 출력이 장면이 뜻한 판정이다(exit · 있어야 할 글자 · 없어야 할 글자).
  ② 같음 — 하위 폴더 출력이 맨 위 출력과 같다(커밋 해시 · 임시 경로 · 시각만 가린다 · 하위 폴더를 받지 않는 0T 장면은 맨 위만 ·
     프로젝트 밖이 있어야 뜻이 서는 장면은 하위 폴더만 — 장면 표의 넷째 칸 `'sub'`).
  ③ R — 고정 판(RELEASE_251 · 2.5.1 배포 — 올리지 않는다)은 이 장면에서 틀렸다(붉음 먼저): `top` 장면은 고정 판의 출력이
     꼴을 어기고, `sub` 장면은 고정 판의 하위 폴더 출력이 맨 위와 다르다. 대조 장면(None)은 고정 판도 꼴을 지키고 출력이
     이 판과 같다. 커밋이 이력에 없으면(얕은 clone 등) R 만 건너뛰고 건너뛴 사실을 낸다(실패로 세지 않는다).
그 밖에 정적 대조 둘 — S1: test/ 밖의 프로세스 실행 자리가 알려진 자리 표(`EXPECTED_LAUNCH`)와 같고, git 은 모두 공용 상수
`GIT_PINS` 를 실은 목록이며, 셸 · 해석 못 하는 실행 꼴이 없다(고정 판은 붉다 · 정직한 코드의 새 자리를 잡는 울타리 — 일부러
숨긴 꼴은 보지 않는다, `launch_census`). S2: 그 대조가 잡는 꼴의 표본(`BYPASS`)이 하나씩 그 규칙의 까닭으로 잡힌다(표본마다 규칙 하나에만 걸리게 갈랐다).

묶음: C 사용자 설정 · 속성(`color.ui` · `color.diff` · `color.grep` · `grep.column` · `diff.external` · textconv ·
`diff.algorithm` · 속성 드라이버 알고리즘 · `-diff`/`binary`(사용자 · 저장소 · 내용 NUL) · `diff.interHunkContext` ·
서명 + `log.showSignature` · `apply.whitespace`) · N 이름(따옴표 · 역빗금 · 탭 · 줄바꿈 · CR · BEL · 백스페이스 · `:` ·
줄 글의 U+2028 · 폼 피드) · L 밖 읽기(plan 조각 셈 · SDK 사본 링크와 `hash-object` 입력 · O7 `..`) · T 갈래(0T 최상위 끝
공백 · 빚 잔존의 web 범위 개명 조회 — 개명 탐지 한도 · web/ 밖 지움이 짝을 가로채지 않음 · 사용자 `diff.relative` · 승인 병합
계보 · 프로젝트 밖 작업 파일을 git 자식에게도 읽히지 않음) · S 정적 둘."""
import ast
import collections
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

TEST = Path(__file__).resolve().parent
SCRIPTS = TEST.parent
sys.path.insert(0, str(TEST))
import fixtures_patch230 as fx  # noqa: E402
import fixtures_patch231_debt as fd  # noqa: E402
import fixtures_patch231_switch as sw  # noqa: E402
import fixtures_patch251_subfolder as b  # noqa: E402

RELEASE_251 = '11d84153'  # R 의 고정 판(배포된 dddjango-web 2.5.1) — 올리지 않는다(R 이 이 판의 결함에 묶여 있다)
PASS = FAIL = 0
ENVS = (fx.ENV, fd.ENV, sw.ENV)  # 픽스처 모듈들의 git · 도구 실행 환경(b.ENV 는 fx.ENV 와 같은 사전)
VM = b.VM
HELPER = 'web/application/order/helpers/order_helper.py'
# 감사 hook 실행기 — 프로그램이 연 파일 · 나열한 폴더 가운데 실제 경로가 밖 폴더 안인 것을 stderr 에 낸다
HOOK = ('import os, runpy, sys\n'
        'OUT = os.path.realpath(sys.argv[1])\n'
        'sys.argv = sys.argv[2:]\n'
        'def hook(ev, args):\n'
        '    if ev in ("open", "os.listdir", "os.scandir") and args and isinstance(args[0], (str, bytes, os.PathLike)):\n'
        '        try:\n'
        '            real = os.path.realpath(os.fsdecode(args[0]))\n'
        '        except Exception:\n'
        '            return\n'
        '        if real == OUT or real.startswith(OUT + os.sep):\n'
        '            sys.stderr.write("OUTSIDE %s %s\\n" % (ev, os.path.basename(real)))\n'
        'sys.addaudithook(hook)\n'
        'sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[0])))\n'
        'runpy.run_path(sys.argv[0], run_name="__main__")\n')
# 참조 조회 한 번(debt.reference_lines)의 줄 글
REFS = ('import sys\nfrom pathlib import Path\nsys.path.insert(0, sys.argv[1])\nfrom src import debt\n'
        'print(debt.reference_lines(Path(sys.argv[2]), [sys.argv[3]], word=True))\n')
# O7 등재 사본 바이트 읽기(sdk_registry.registered_copy_bytes) — 링크 너머 · `..` · 정규형 아닌 경로면 None 이어야 한다
COPY_BYTES = ('import json, sys\nfrom pathlib import Path\nsys.path.insert(0, sys.argv[1])\n'
              'from src.sdk_registry import registered_copy_bytes\n'
              'root = Path(sys.argv[2])\n'
              'for sid, entry in sorted(json.loads((root / "web/sdk_registry.json").read_text())["sdks"].items()):\n'
              '    data = registered_copy_bytes(root, entry)\n'
              '    print(sid, None if data is None else "%d B" % len(data))\n'
              'for rel in ("static/vendor/x/../../../../../o7out/sdk.js", "static/vendor/./x/a.js", "static/vendor//x/a.js"):\n'
              '    print(rel, registered_copy_bytes(root, {"file": rel}))\n')
# git 감싸개 — `hash-object` 의 표준 입력(그 git 자식이 읽을 경로들)을 기록하고 진짜 git 을 부른다
REAL_GIT = shutil.which('git')
GITWRAP = ('#!%s\nimport os, subprocess, sys\nargs = sys.argv[1:]\n'
           "data = sys.stdin.buffer.read() if 'hash-object' in args else None\n"
           'r = subprocess.run([%r, *args], input=data)\n'
           "if data is not None:\n    with open(os.environ['GITWRAP_LOG'], 'ab') as f:\n        f.write(data)\n"
           'sys.exit(r.returncode)\n')


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok and detail:
        print('    ' + str(detail).replace('\n', '\n    ')[:3000])


# ====================================================================== 사용자 git 설정(시험 안에서만)

class Configs:
    """임시 전역 설정 파일들 — 기본(이름 · 메일만) + 장면이 거는 설정. 서명 열쇠는 처음 쓸 때 만든다."""

    def __init__(self, tmp):
        self.dir = tmp / 'gitconfig'
        self.dir.mkdir()
        self.base = self.write('base', ())
        self.signing = None

    def write(self, name, pairs):
        path = self.dir / name
        lines = ['[user]', '\tname = t', '\temail = t@t']
        for key, value in pairs:
            section, _, leaf = key.rpartition('.')
            if '.' in section:   # gpg.ssh.allowedSignersFile → [gpg "ssh"]
                head, _, sub = section.partition('.')
                section = '%s "%s"' % (head, sub)
            lines += ['[%s]' % section, '\t%s = %s' % (leaf, value)]
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return path

    def sign(self):
        """ssh 서명 열쇠(이 묶음 전용) → 서명 설정 쌍. ssh-keygen 이 없거나 git 이 ssh 서명을 못 하면 None."""
        if self.signing is None:
            self.signing = ()
            key = self.dir / 'key'
            if shutil.which('ssh-keygen') and subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', str(key)],
                                                             capture_output=True).returncode == 0:
                allowed = self.dir / 'allowed'
                allowed.write_text('t@t %s' % (self.dir / 'key.pub').read_text(), encoding='utf-8')
                pairs = (('commit.gpgSign', 'true'), ('gpg.format', 'ssh'), ('user.signingKey', str(key)),
                         ('gpg.ssh.allowedSignersFile', str(allowed)))
                probe = self.dir / 'probe'
                probe.mkdir()
                env = dict(fx.ENV, GIT_CONFIG_GLOBAL=str(self.write('probe.cfg', pairs)))
                subprocess.run(['git', '-C', str(probe), 'init', '-q'], env=env, capture_output=True)
                ok = subprocess.run(['git', '-C', str(probe), 'commit', '-q', '--allow-empty', '-m', 'p'], env=env,
                                    capture_output=True).returncode == 0
                self.signing = pairs if ok else ()
        return self.signing or None


@contextmanager
def gitconfig(path):
    """픽스처 모듈들의 실행 환경에 전역 설정 파일을 건다(준비 커밋 · 도구 실행 모두) — 끝나면 기본으로."""
    saved = [env.get('GIT_CONFIG_GLOBAL') for env in ENVS]
    for env in ENVS:
        env['GIT_CONFIG_GLOBAL'] = str(path)
    try:
        yield
    finally:
        for env, value in zip(ENVS, saved):
            env['GIT_CONFIG_GLOBAL'] = value


# ====================================================================== 장면 재료

def lane_relative_import(s):
    """레인이 기존 VM 끝에 상대 import 한 줄(IM24) + plan 이 참조를 찾을 소비 파일 · 빚 스캔 → (기준 커밋, 산출물 폴더)."""
    p = s.std()
    p.w(HELPER, 'def order_help() -> int:', '    return 1')
    p.w('web/root/extra/uses_helper.py', 'from web.application.order.helpers.order_helper import order_help', '',
        'x: int = order_help()')
    p.markers()
    base = p.commit('base')
    p.append(VM, 'from ..state import order_list_state  # lane')
    p.commit('lane: relative import')
    folder = p.root / '.dddjango-web/run'
    folder.mkdir(parents=True)
    return base, folder


def gate_and_plan(s, gate=True, plan=True):
    base, folder = lane_relative_import(s)
    if gate:
        s.backstop('IM24', '--diff-base', base, '--only', 'im24')
    if plan:
        s.backstop('빚 스캔', '--debt-scan', '--refactor', '--json', folder / 'debt-g0.json')
        s.tool('plan', 'refactor_audit.py', 'plan', 'web/application/order', '--debt', folder / 'debt-g0.json',
               '--out', folder / 'audit')
        s.section('참조 치환 줄', folder / 'audit/plan.md', '## 참조 치환 줄')


def debt_project(s, beta='beta.py', extra=()):
    """fixtures_patch231_debt 재현 장면 — 파일 이름을 JSON 글자로 적는다(따옴표 · 탭 · 줄바꿈 이름) → (기준, 산출물 폴더).
    extra = 기준 커밋에 함께 넣을 (경로, 글) — web 파일을 덮어쓰거나 web/ 밖 · 프로젝트 밖 파일을 둔다."""
    root = s.bare()
    for rel, body in fd.REPRO_WEB.items():
        fd.write(root / 'web' / rel.replace('beta.py', beta), body)
    for path, body in extra:
        fd.write(path, body)
    if extra:
        fd.git(s.top, 'add', '--', *(str(path) for path, _body in extra))
    anchor = fd.commit(root)
    folder = root / '.dddjango-web/run'
    folder.mkdir(parents=True)
    frozen = json.loads(fd.REPRO_G0.replace('legacy/beta.py', json.dumps('legacy/' + beta)[1:-1]))
    frozen.update(head=anchor, scanned_at='2026-10-10T20:07:43+09:00')
    fd.write(folder / 'debt-g0.json', json.dumps(frozen))
    fd.write(folder / 'refactor-scope.md', fd.section(body=fd.decision('C2') + 'ⓑ 키: C2\n'))
    return anchor, folder


def hooked(s, name, outside, script, *args):
    """감사 hook 아래에서 도구 하나 — 밖 폴더(outside) 안을 연 · 나열한 자리를 `OUTSIDE …` 줄로 함께 남긴다."""
    s._record(name, [sys.executable, '-B', '-c', HOOK, str(outside), str(s.scripts / script), *map(str, args)])


# ====================================================================== C — 사용자 git 설정

def c_im24(pairs):
    def scene(s):
        with gitconfig(s.cfg.write('c-im24', pairs)):
            gate_and_plan(s, plan=False)
    return scene


def c_plan(pairs):
    def scene(s):
        with gitconfig(s.cfg.write('c-plan', pairs)):
            gate_and_plan(s, gate=False)
    return scene


def c_external(s):
    """diff.external — 전역으로 건 외부 diff 도구가 더한 줄 범위 diff 를 대신 그리면 안 된다."""
    tool = s.box / 'extdiff.sh'
    tool.write_text('#!/bin/sh\necho "EXTERNAL DIFF $*"\n', encoding='utf-8')
    tool.chmod(0o755)
    with gitconfig(s.cfg.write('c-ext', (('diff.external', str(tool)),))):
        gate_and_plan(s, plan=False)


def c_inter_hunk(s):
    """diff.interHunkContext=10 — 기준점에 이미 있는 상대 import(빚) 위아래 두 줄만 레인이 고쳤다. 덩이를 합쳐 그 줄을 더한
    줄로 읽으면 안 된다(IM24 0)."""
    p = s.std()
    p.w(HELPER, 'from ..state import order_list_state', 'A: int = 1', 'B: int = 2', 'C: int = 3', 'D: int = 4',
        'E: int = 5', 'F: int = 6', 'G: int = 7', 'from ..view_model import order_list_vm', 'H: int = 8', 'I: int = 9',
        'J: int = 10', 'K: int = 11')
    p.markers()
    base = p.commit('base')
    p.sub(HELPER, 'B: int = 2', 'B: int = 20')
    p.sub(HELPER, 'J: int = 10', 'J: int = 100')
    p.commit('lane: two small edits')
    with gitconfig(s.cfg.write('c-inter', (('diff.interHunkContext', '10'),))):
        s.backstop('IM24 문맥', '--diff-base', base, '--only', 'im24')


REORDER_BASE = ['# same'] * 3 + ['from ..state import order_list_state'] + ['# same'] * 3
REORDER_LANE = ['from ..state import order_list_state'] + ['# same'] * 6


def c_reorder(pairs=(), attrs=None):
    """기준점에 있던 상대 import 한 줄을 레인이 반복 줄 사이에서 맨 앞으로 옮김 — git 기본(myers) diff 로는 1행이 더한
    줄(IM24). 사용자 diff.algorithm · 속성 드라이버 알고리즘 · `-diff` 속성이 그 판정을 바꾸면 안 된다."""
    def scene(s):
        p = s.std()
        p.w(HELPER, *REORDER_BASE)
        p.markers()
        base = p.commit('base')
        p.w(HELPER, *REORDER_LANE)
        p.commit('lane: reorder')
        extra = ()
        if attrs is not None:
            path = s.box / 'attributes'
            path.write_text(attrs, encoding='utf-8')
            extra = (('core.attributesFile', str(path)),)
        with gitconfig(s.cfg.write('c-reorder', extra + tuple(pairs))):
            s.backstop('IM24 순서', '--diff-base', base, '--only', 'im24')
    return scene


def c_textconv(s):
    """사용자 속성 textconv(`*.py diff=shift` · `sed 1d`) — 줄 번호를 옮겨 그린 diff 로 더한 줄을 읽으면 안 된다(외부 diff 와 따로)."""
    path = s.box / 'attributes'
    path.write_text('*.py diff=shift\n', encoding='utf-8')
    with gitconfig(s.cfg.write('c-textconv', (('core.attributesFile', str(path)), ('diff.shift.textconv', 'sed 1d')))):
        gate_and_plan(s, plan=False)


def c_attr_grep(s):
    """사용자 전역 속성 `-diff`(core.attributesFile) — git grep 이 글 파일을 바이너리로 보아 plan 참조 조회(`-I`)가 건너뛰거나
    SDK 도구의 템플릿 참조 줄이 «Binary file … matches» 로 바뀌면 안 된다."""
    path = s.box / 'attributes'
    path.write_text('*.py -diff\n*.html -diff\n', encoding='utf-8')
    with gitconfig(s.cfg.write('c-attr-grep', (('core.attributesFile', str(path)),))):
        gate_and_plan(s, gate=False)
        s.code('템플릿 참조 줄', b.TEMPLATE_REFS, s.root, 'web/htmx/htmx.min.js')


def c_repo_binary(s):
    """저장소 .gitattributes 의 `binary`(= `-diff`) — 사용자 설정이 기본이어도 더한 줄 범위를 비우면 안 된다(IM24)."""
    p = s.std()
    fd.write(s.root / '.gitattributes', '*.py binary\n')
    p.w(HELPER, 'def order_help() -> int:', '    return 1')
    p.markers()
    base = p.commit('base')
    p.append(VM, 'from ..state import order_list_state  # lane')
    p.commit('lane: relative import')
    s.backstop('IM24', '--diff-base', base, '--only', 'im24')


def c_nul_js(s):
    """속성 없이 git 이 내용(NUL)으로 바이너리로 보는 기능 JS — 레인이 둘째 줄을 외부 주소 호출로 바꿈. 더한 줄 범위가 비면
    안 된다(WV8 · 참 발견)."""
    p = s.std()
    fd.write(s.root / 'web/static/js/order_net.js', '/*\0*/\nvar x = 1;\n')
    p.markers()
    base = p.commit('base')
    fd.write(s.root / 'web/static/js/order_net.js', '/*\0*/\nfetch("https://bad.example/api");\n')
    p.commit('lane: fetch')
    s.backstop('게이트', '--diff-base', base, '--only', 'wv8')


def c_refs_column(s):
    """grep.column=true — 참조 조회의 줄 글에 열 번호가 붙으면 안 된다(함수 출력)."""
    p = s.std()
    p.w('web/root/extra/uses_helper.py', 'x = 1', 'from web.application.order.helpers.order_helper import order_help')
    p.commit('base')
    with gitconfig(s.cfg.write('c-col', (('grep.column', 'true'),))):
        s.code('참조 줄', REFS, p.root, 'web.application.order.helpers.order_helper')


def signed(s, extra=(('log.showSignature', 'true'),)):
    pairs = s.cfg.sign()
    if pairs is None:
        raise Skip('ssh 서명 불가(ssh-keygen 없음 또는 git 이 ssh 서명을 못 함)')
    return s.cfg.write('c-sign', pairs + tuple(extra))


def c_wv10_subject(s):
    """서명 커밋 + log.showSignature — sdk 격리 커밋 제목(`chore(web-sdk):`)을 서명 확인 줄로 읽으면 안 된다(WV10 0)."""
    with gitconfig(signed(s)):
        b.sdk_proj(s, 'server')
        snap = fx.git(s.root, 'rev-parse', 'HEAD')
        r = subprocess.run([sys.executable, '-B', str(s.scripts / 'test/sdk_fixture.py'), 'install', str(s.root)],
                           env=fx.ENV, capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError('install 준비 실패 — %s' % (r.stdout + r.stderr)[-400:])
        sdk = fx.git(s.root, 'rev-parse', 'HEAD')
        folder = s.root / '.dddjango-web/wv10'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'build-state.json').write_text(json.dumps({'git_snapshot': snap, 'sdk_commits': [sdk], 'slices': []}),
                                                 encoding='utf-8')
        s.backstop('게이트 · wv10', '--diff-base', snap, '--only', 'wv10', '--design-build', folder)


def c_standing(s):
    """서명 커밋 + log.showSignature — 상시 답의 커밋 · 때를 서명 확인 줄에서 읽으면 안 된다."""
    with gitconfig(signed(s)):
        b.a_standing(s)


def c_inflow_subject(s):
    """서명 커밋 + log.showSignature — 승인 병합 제목(표시)에 서명 확인 줄이 들면 안 된다."""
    with gitconfig(signed(s)):
        b.t_received_link(s)


class Skip(Exception):
    pass


# ---- 0T 확인(switch-check) — fixtures_patch231_switch 의 장면 · 가짜 시험 실행기를 쓴다(맨 위만 — 하위 폴더는 받지 않는다)

WS_MUTANT = (12, "        return Response(302, '/elsewhere/')   ")   # 보호 분기 안 — 끝 공백이 붙은 반례


def switch_scene(s, config, mutants=(sw.MUT_URL,)):
    with gitconfig(config):
        scene = sw.Scene(s.box, 'switch', mutants=mutants)
        scratch = s.box / 'tool-tmp'
        scratch.mkdir(exist_ok=True)
        r = subprocess.run([sys.executable, '-B', str(s.scripts / 'refactor_audit.py'), '--project', str(scene.root),
                            'switch-check', sw.RUN, '--test-cmd', sw.fake_cmd(s.box)], cwd=str(scene.root),
                           env=dict(sw.ENV, TMPDIR=str(scratch)), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = r.stdout.decode('utf-8', 'replace').replace(str(scene.root), '<루트>').replace(str(s.box), '<상자>')
    s.runs.append(('switch-check', r.returncode, fx.counts_normalized(re.sub(r'\b[0-9a-f]{7,40}\b', '<해시>', out))))


def c_switch_signed(s):
    switch_scene(s, signed(s))


def c_switch_sign_only(s):
    switch_scene(s, signed(s, extra=()))


def c_switch_whitespace(s):
    switch_scene(s, s.cfg.write('c-apply', (('apply.whitespace', 'error'),)), mutants=(WS_MUTANT,))


# ====================================================================== N — 이름 · 줄 글자(기본 설정)

NAMES = (('따옴표', 'be"ta.py'), ('탭', 'be\tta.py'), ('줄바꿈', 'be\nta.py'), ('역빗금', 'be\\ta.py'),
         ('BEL', 'be\x07ta.py'), ('백스페이스', 'be\x08ta.py'), ('CR', 'be\rta.py'))


def n_debt_names(s):
    """미룬 ⓑ 키(C2)의 파일 이름에 따옴표 · 탭 · 줄바꿈 · 역빗금 — 레인이 git mv → «ⓑ 이동 묶음 의존»(ASCII 이름과 같다)."""
    for label, beta in NAMES:
        one = b.Stage(s.box / ('n-%d' % len(s.runs)), s.layout, s.scripts)
        _anchor, folder = debt_project(one, beta)
        (one.root / 'web/moved').mkdir()
        fd.git(one.root, 'mv', 'web/legacy/' + beta, 'web/moved/' + beta)
        one.backstop('옮긴 뒤 ' + label, '--debt-residual', folder, clock=True)
        s.runs.extend(one.runs)


def n_inflow_quote(s):
    """승인 병합(main 받기)이 따옴표 이름 파일(미룬 키 C2)의 이동을 들임 — 승인 전 멈춤 · 승인 뒤 알림과 함께 지남."""
    beta = 'be"ta.py'
    anchor, folder = debt_project(s, beta)
    merge = b.upstream_move(s, anchor, folder, beta)
    s.backstop('승인 전', '--debt-residual', folder, clock=True)
    fd.write(folder / 'approved-merges.txt', merge + ' main 받기\n')
    s.backstop('승인 뒤', '--debt-residual', folder, clock=True)


def residual_project(s, name):
    """A1 꼴 — 의미 항목 M1 의 파일이 `web/legacy/<name>` 인 리팩토링 실행 자리 → 산출물 폴더."""
    files = ('legacy/' + name, 'legacy/beta.py')
    _anchor, folder = b.debt_proj(s)
    fd.write(s.root / 'web' / files[0], 'def a() -> int:\n    return 1\n')
    anchor = fd.commit(s.root)
    data = json.loads((folder / 'debt-g0.json').read_text(encoding='utf-8'))
    data.update(mode='refactor', head=anchor)
    fd.write(folder / 'debt-g0.json', json.dumps(data))
    fd.write(folder / 'build-state.json', json.dumps({'git_snapshot': anchor}))
    audit = folder / 'audit' / fd.AUDIT
    fd.write(audit / 'plan.md', '- 단위: `web/legacy`\n## 범위 파일\n- `web/legacy/alpha.py`\n'
             '## 범위 안 키\n- 없음\n## 줄 편집\n- 없음\n## 참조 치환 줄\n- 없음\n'
             '## 파견\n| ui-01.md | ui | 01 | reviewer |\n')
    fd.write(audit / 'ui-01.md', ''.join('| %d | 규칙 | - | web/%s:1 | 위반 | 가능 | 파일 | - |\n' % (k, f)
                                         for k, f in enumerate(files, 1)))
    fd.write(audit / 'verdict-final.md', ''.join('| M%d | ui-01#%d | 의미 위반 | 근거 | web/%s:1 |\n' % (k, k, f)
                                                 for k, f in enumerate(files, 1)))
    fd.write(folder / 'refactor-scope.md',
             fd.section(meaning='M1', body=fd.decision('M2', '다른 요청') + '의미 ⓑ 다른 요청 키: M2\n'))
    (s.root / 'web/moved').mkdir()
    return folder


def n_residual_quote(s):
    """refactor_audit residual — 의미 항목 M1 의 파일 이름에 따옴표. ① git mv 로 옮김 → 리뷰어 확인 대상(무변 잔존 아님) ·
    개명 쌍이 그 이름 그대로 ② 그냥 mv(새 자리는 미추적)로 옮기고 새 자리를 해소 근거로 → 해소."""
    name = 'al"pha.py'
    folder = residual_project(s, name)
    fd.git(s.root, 'mv', 'web/legacy/' + name, 'web/moved/' + name)
    s.tool('residual', 'refactor_audit.py', 'residual', folder, clock=True)
    stamps = sorted((folder / 'residual').iterdir()) if (folder / 'residual').is_dir() else []
    s.section('개명 쌍', stamps[0] / 'review-ui.md' if stamps else folder / '-', '## 슬라이스 0 개명 쌍(옛 경로 → 새 경로)')
    two = b.Stage(s.box / 'plain-mv', s.layout, s.scripts)
    folder = residual_project(two, name)
    (two.root / 'web/legacy' / name).rename(two.root / 'web/moved' / name)
    two.tool('residual · 그냥 mv', 'refactor_audit.py', 'residual', folder, clock=True)
    stamps = sorted((folder / 'residual').iterdir()) if (folder / 'residual').is_dir() else []
    if stamps:
        fd.write(stamps[0] / 'result-ui.md', '| M1 | 해소 | web/moved/%s:1 — 판단을 한 곳에 둠 |\n' % name)
        two.tool('finalize · 그냥 mv', 'refactor_audit.py', 'residual', folder, '--finalize', stamps[0].name, clock=True)
    s.runs.extend(two.runs)


CR_NAMES = ('import json, subprocess, sys\nfrom pathlib import Path\nsys.path.insert(0, sys.argv[1])\nimport refactor_audit as r\n'
            'root = Path(sys.argv[2])\n'
            'anchor = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()\n'
            'print("개명", repr(sorted(r._renamed_since(root, anchor).items())))\n'
            'print("바뀐 파일", repr(sorted(p for p in r._changed_since(root, anchor) if "ta.py" in p or "free" in p)))\n')


def n_residual_cr(s):
    """refactor_audit residual 의 개명 쌍 · 바뀐 파일 읽기 — 이름 속 CR 을 줄바꿈으로 바꾸지 않는다(git 개명 · 미추적)."""
    debt_project(s, 'be\rta.py')
    (s.root / 'web/moved').mkdir()
    fd.git(s.root, 'mv', 'web/legacy/be\rta.py', 'web/moved/be\rta.py')
    fd.write(s.root / 'web/moved/free\rname.py', 'x = 1\n')
    s.code('CR 이름', CR_NAMES, s.root)


def n_plan_odd(s):
    """plan 참조 조회 — 맞는 파일 이름에 `:` · 맞는 줄에 U+2028 · 폼 피드가 있어도 실행 불능이 아니다(기본 설정)."""
    for label, rel, body in (
            ('콜론 이름', 'web/root/extra/a:b.html',
             '<p>x</p>\n<!-- application/order/helpers/order_helper.py -->\n'),
            ('U+2028 줄', 'web/root/extra/uses.js', '// web.application.order.helpers.order_helper   x\nconst a = 1;\n'),
            ('폼 피드 줄', 'web/root/extra/uses2.py',
             'from web.application.order.helpers.order_helper import order_help  # \x0c\n')):
        one = b.Stage(s.box / ('p-%d' % len(s.runs)), s.layout, s.scripts)
        p = one.std()
        p.w(HELPER, 'def order_help() -> int:', '    return 1')
        (p.root / rel).parent.mkdir(parents=True, exist_ok=True)
        (p.root / rel).write_text(body, encoding='utf-8')
        p.markers()
        p.commit('base')
        folder = p.root / '.dddjango-web/run'
        folder.mkdir(parents=True)
        one.backstop('빚 스캔 · ' + label, '--debt-scan', '--refactor', '--json', folder / 'debt-g0.json')
        one.tool('plan · ' + label, 'refactor_audit.py', 'plan', 'web/application/order', '--debt',
                 folder / 'debt-g0.json', '--out', folder / 'audit')
        one.section('참조 치환 줄 · ' + label, folder / 'audit/plan.md', '## 참조 치환 줄')
        s.runs.extend(one.runs)


def n_vendor_units(s):
    """목록 이전 같은 자리 사본(벤더 폴더 이름에 따옴표 · 탭 · 줄바꿈)이 있어도 SDK 정식 등재가 선다(거짓 WV13 없음)."""
    for label, unit in (('따옴표', 'ka"kao_tmp'), ('탭', 'ka\tkao_tmp'), ('줄바꿈', 'ka\nkao_tmp')):
        one = b.Stage(s.box / ('v-%d' % len(s.runs)), s.layout, s.scripts)
        b.sdk_proj(one, 'server', unit)
        one.tool('install · ' + label, 'test/sdk_fixture.py', 'install', one.root)
        s.runs.extend(one.runs)


def n_vendor_folder(s):
    """하위 폴더(프로젝트 폴더) 이름에 따옴표 — 맨 위 꼴은 대조(이름 무관), 하위 폴더 꼴이 맨 위와 같아야 한다."""
    b.sdk_proj(s, 'ser"ver')
    s.tool('install', 'test/sdk_fixture.py', 'install', s.root)


# ====================================================================== L — 밖 읽기

def l_plan_link(s):
    """plan 조각 셈 — 범위 파일이 프로젝트 밖 6,010행 파일을 가리키는 링크여도 그 파일을 열지 않는다(조각 1 · 파견 5)."""
    p = s.std()
    p.w(HELPER, 'def order_help() -> int:', '    return 1')
    p.markers()
    p.commit('base')
    out = s.box / 'outside'
    out.mkdir()
    (out / 'big.py').write_text(''.join('x%d = %d\n' % (k, k) for k in range(6010)), encoding='utf-8')
    folder = p.root / '.dddjango-web/run'
    folder.mkdir(parents=True)
    s.backstop('빚 스캔', '--debt-scan', '--refactor', '--json', folder / 'debt-g0.json')
    (p.root / HELPER).unlink()
    os.symlink(out / 'big.py', p.root / HELPER)
    hooked(s, 'plan', out, 'refactor_audit.py', 'plan', 'web/application/order', '--debt', folder / 'debt-g0.json',
           '--out', folder / 'audit')


def sdk_installed(s):
    """sdk_fixture 표준 프로젝트를 이 꼴에 놓고 kakao SDK 를 정식 등재(준비는 늘 이 판의 시험 도구) → 등재 사본 폴더."""
    made = s.box / 'sdkproj'
    subprocess.run([sys.executable, '-B', str(TEST / 'sdk_fixture.py'), 'mkproj', str(made)], env=fx.ENV,
                   capture_output=True, check=True)
    shutil.rmtree(made / '.git')
    s.root.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(made), str(s.root))
    fd.git(s.top, 'init', '-q', '-b', 'main')
    s.bait()
    s.commit_all('base')
    r = subprocess.run([sys.executable, '-B', str(TEST / 'sdk_fixture.py'), 'install', str(s.root)], env=fx.ENV,
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError('install 준비 실패 — %s' % (r.stdout + r.stderr)[-400:])
    return s.root / 'web/static/vendor/kakao_js_sdk'


def l_sdk_link(s):
    """등재 SDK 사본 파일 · 폴더를 프로젝트 밖 같은 바이트 사본의 링크로 — WV2 로 거절하되 링크 너머는 읽지 않는다."""
    for kind in ('파일', '폴더'):
        one = b.Stage(s.box / ('k-%d' % len(s.runs)), s.layout, s.scripts)
        unit = sdk_installed(one)
        out = one.box / 'outside'
        shutil.copytree(unit, out)
        if kind == '파일':
            target = sorted(x for x in unit.rglob('*') if x.is_file())[0]
            target.unlink()
            os.symlink(out / target.relative_to(unit), target)
        else:
            shutil.rmtree(unit)
            os.symlink(out, unit)
        hooked(one, 'verify · ' + kind, out, 'sdk_vendor.py', 'verify', one.root)
        hash_inputs(one, 'hash-object 입력 · ' + kind, 'sdk_vendor.py', 'verify', one.root)
        hooked(one, '게이트 · ' + kind, out, 'backstop.py', one.root, '--diff-base', 'HEAD', '--only', 'wv')
        one.code('사본 바이트 · ' + kind, COPY_BYTES, one.root)
        s.runs.extend(one.runs)


def hash_inputs(s, name, script, *args):
    """PATH 앞의 git 감싸개로 도구를 한 번 — `git hash-object --stdin-paths` 에 넘긴 경로(그 git 자식이 읽는 파일)를
    실행 기록 끝 줄에 덧붙인다."""
    wrap = s.box / 'gitwrap'
    wrap.mkdir(exist_ok=True)
    (wrap / 'git').write_text(GITWRAP % (sys.executable, REAL_GIT), encoding='utf-8')
    (wrap / 'git').chmod(0o755)
    log = s.box / ('hash-%d.log' % len(s.runs))
    log.write_bytes(b'')
    env = dict(fx.ENV, PATH=str(wrap) + os.pathsep + fx.ENV.get('PATH', ''), GITWRAP_LOG=str(log))
    r = subprocess.run([sys.executable, '-B', str(s.scripts / script), *map(str, args)], cwd=str(s.root), env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    paths = ' '.join(sorted(log.read_bytes().decode('utf-8', 'replace').split()))
    s.runs.append((name, r.returncode, s.mask(r.stdout.decode('utf-8', 'replace') + '\nhash-object 입력: [%s]\n' % paths)))


def l_o7_outside(s):
    """등재 항목 file 을 `..` 로 프로젝트 밖(같은 바이트 사본)을 가리키게 고친 뒤 범위 넓힘(O7) — 거절 전에 밖을 읽지 않는다."""
    unit = sdk_installed(s)
    out = s.root.parent / 'o7out'
    out.mkdir(exist_ok=True)
    shutil.copyfile(sorted(x for x in unit.rglob('*') if x.is_file())[0], out / 'sdk.js')
    registry = s.root / 'web/sdk_registry.json'
    data = json.loads(registry.read_text(encoding='utf-8'))
    data['sdks']['kakao_js_sdk']['file'] = 'static/vendor/kakao_js_sdk/../../../../../o7out/sdk.js'
    registry.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    hooked(s, 'scope-add', out, 'test/sdk_fixture.py', 'install', s.root, '--scope-add', 'Kakao.Share.uploadImage')
    s.code('사본 바이트', COPY_BYTES, s.root)


# ====================================================================== T — 맨 위 갈래

def t_repo_space(s):
    """이름이 공백으로 끝나는 저장소(`repo `)의 맨 위 프로젝트 — 0T 확인이 최상위 확인을 지나 다음 입력까지 간다."""
    s.adopt(s.box / 'repo ')
    p = s.std()
    p.commit('base')
    folder = p.root / '.dddjango-web/run'
    folder.mkdir(parents=True)
    s.tool('switch-check', 'refactor_audit.py', '--project', p.root, 'switch-check', folder, '--test-cmd', 'true')


def upstream_move_to(s, anchor, folder, dest, beta='beta.py', drop=None):
    """상류(upstream 가지)가 web/legacy/<beta> 를 dest(저장소 안 절대 경로)로 옮기고(drop 이 있으면 그 프로젝트 상대 파일도
    지우고) 레인이 그 병합을 받는다 → 병합 커밋."""
    root = s.root
    fd.write(folder / 'build-state.json', json.dumps({'git_snapshot': anchor}))
    lane = fd.git(root, 'symbolic-ref', '--short', 'HEAD')
    fd.git(root, 'checkout', '-q', '-b', 'upstream', anchor)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd.git(s.top, 'mv', str(root / 'web/legacy' / beta), str(dest))
    if drop:
        fd.git(root, 'rm', '-q', drop)
    fd.git(s.top, 'add', '-A')
    fd.git(s.top, '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'upstream move')
    fd.git(root, 'checkout', '-q', lane)
    fd.write(root / 'web/legacy/alpha.py', 'def a() -> int:\n    return 10\n')
    fd.commit(root)
    fd.git(root, '-c', 'user.name=t', '-c', 'user.email=t@t', 'merge', '-q', '--no-ff', '-m', 'main', 'upstream')
    return fd.git(root, 'rev-parse', 'HEAD')


BETA_BODY = 'def b() -> int:\n    return 2\n' + ''.join('# line %d of beta helper text\n' % k for k in range(30))


def t_steal(outside, body, name=None):
    """기준점에 web/ 밖 파일 outside(글 body)를 함께 두고, 레인이 미룬 키 파일을 web/ 안에서 옮기며(그 파일 이름 ·
    글을 밖 파일 쪽으로 맞춤) 밖 파일을 지운다 — 무관한 web/ 밖 지움이 개명 짝을 가로채 이동을 놓치면 안 된다(2.5.1 짝)."""
    def scene(s):
        root = s.root
        _anchor, folder = debt_project(s, extra=((root / 'web/legacy/beta.py', BETA_BODY), (root / outside, body)))
        dest = root / 'web/moved' / (name or posixpath.basename(outside))
        dest.parent.mkdir(parents=True)
        fd.git(root, 'mv', 'web/legacy/beta.py', str(dest))
        fd.write(dest, body)
        fd.git(root, 'rm', '-q', outside)
        fd.git(root, 'add', '-A', 'web')
        s.backstop('옮긴 뒤', '--debt-residual', folder, clock=True)
    return scene


def t_steal_inflow(s):
    """승인 병합(main 받기)이 미룬 키 파일을 web/ 안에서 옮기며 web/ 밖 같은 글 · 같은 이름 파일을 지워 들임 — 계보 조회에서도
    무관한 web/ 밖 지움이 짝을 가로채면 안 된다(승인 뒤 알림과 함께 지남 · 2.5.1 과 같다)."""
    root = s.root
    anchor, folder = debt_project(s, extra=((root / 'web/legacy/beta.py', BETA_BODY),
                                            (root / 'outside_pkg/beta_renamed.py', BETA_BODY)))
    merge = upstream_move_to(s, anchor, folder, root / 'web/moved/beta_renamed.py', drop='outside_pkg/beta_renamed.py')
    fd.write(folder / 'approved-merges.txt', merge + ' main 받기\n')
    s.backstop('승인 뒤', '--debt-residual', folder, clock=True)


def t_colon_folder(s):
    """하위 폴더 이름이 `:` 로 시작(`:srv`) — 승인 병합이 미룬 키 파일을 web/ 안에서 옮겨 들임. 승인 판정의 저장소 기준 경로
    조회가 그 이름을 pathspec 마법으로 읽으면 승인 뒤에도 레인 이동으로 센다(2.5.1 은 알림과 함께 지났다)."""
    if s.layout == 'sub':
        s.adopt(s.top, ':srv')
    anchor, folder = debt_project(s)
    merge = upstream_move_to(s, anchor, folder, s.root / 'web/moved/beta.py')
    fd.write(folder / 'approved-merges.txt', merge + ' main 받기\n')
    s.backstop('승인 뒤', '--debt-residual', folder, clock=True)


def t_relative_lane(s):
    """사용자 diff.relative=true — 미룬 키 파일을 web/ 안에서 옮김. 개명 조회가 사용자 설정을 따르면(하위 폴더) 짝을 못 읽는다."""
    _anchor, folder = debt_project(s)
    (s.root / 'web/moved').mkdir()
    fd.git(s.root, 'mv', 'web/legacy/beta.py', 'web/moved/beta.py')
    with gitconfig(s.cfg.write('t-rel', (('diff.relative', 'true'),))):
        s.backstop('옮긴 뒤', '--debt-residual', folder, clock=True)


def t_relative_inflow(s):
    """사용자 diff.relative=true — 승인 병합이 미룬 키 파일을 web/ 안에서 옮겨 들임. 승인 판정의 바뀐 항목 조회 · 계보 조회가
    사용자 설정을 따르면(하위 폴더) 상류판 그대로 수신을 못 세운다."""
    anchor, folder = debt_project(s)
    merge = upstream_move_to(s, anchor, folder, s.root / 'web/moved/beta.py')
    fd.write(folder / 'approved-merges.txt', merge + ' main 받기\n')
    with gitconfig(s.cfg.write('t-rel-in', (('diff.relative', 'true'),))):
        s.backstop('승인 뒤', '--debt-residual', folder, clock=True)


SPY = ('#!%s\nimport os, sys\ndata = sys.stdin.buffer.read()\n'
       "with open(os.environ['SPY_LOG'], 'ab') as f:\n    f.write(data)\nsys.stdout.buffer.write(data)\n")


def t_outside_clean(s):
    """하위 폴더 프로젝트 — 프로젝트 밖 작업 파일(stat 만 바뀐 추적 파일 · 색인에 올린 뒤 고친 새 파일)에 clean filter(받은
    바이트를 기록)를 걸고, 레인이 미룬 키 파일을 지움(색인) · web 파일 둘의 stat 만 바꿈. 빚 잔존의 web 범위 개명 조회가 끝에
    색인 전체를 새로 고치며 git 자식에게 프로젝트 밖 작업 파일을 읽히지 않는다(기록 0 바이트 · 2.5.1 은 읽었다)."""
    top = s.top
    _anchor, folder = debt_project(s, extra=((top / '.gitattributes', '/outside*.txt filter=spy\n'),
                                             (top / 'outside.txt', 'kept outside\n'),
                                             (s.root / 'notes.txt', 'project file outside web\n')))
    fd.git(s.root, 'rm', '-q', 'web/legacy/beta.py')
    fd.write(top / 'outside_new.txt', 'brand new outside file\n' * 3)
    fd.git(top, 'add', '--', 'outside_new.txt')
    with open(top / 'outside_new.txt', 'a', encoding='utf-8') as f:
        f.write('edited after add\n')
    for path in (s.root / 'web/legacy/alpha.py', s.root / 'web/other/gamma.py', s.root / 'notes.txt', top / 'outside.txt'):
        os.utime(path, (2000000000, 2000000000))   # stat 만 바뀜(글 그대로) — git 이 색인을 새로 고치며 글을 읽는 자리
    spy = s.box / 'spy.py'
    spy.write_text(SPY % sys.executable, encoding='utf-8')
    spy.chmod(0o755)
    log = s.box / 'spy.log'
    log.write_bytes(b'')
    saved = [env.get('SPY_LOG') for env in ENVS]
    for env in ENVS:
        env['SPY_LOG'] = str(log)
    try:
        with gitconfig(s.cfg.write('t-spy', (('filter.spy.clean', str(spy)),))):
            s.backstop('지운 뒤', '--debt-residual', folder, clock=True)
    finally:
        for env, value in zip(ENVS, saved):
            env.pop('SPY_LOG') if value is None else env.update(SPY_LOG=value)
    s.runs.append(('git 자식의 밖 입력', 0, '밖 입력 %d 바이트\n' % len(log.read_bytes())))


def big_outside(n, pairs=(), also=False):
    """기준 뒤 web/ 밖에서 n 파일을 지우고 다른 n 파일을 더하고, 미룬 키 파일의 이름을 바꿔 옮긴 뒤 한 줄 고침 — 개명 탐지
    한도(git 기본 · 사용자 diff.renameLimit)에 막혀 이동을 놓치면 안 된다. also 면 web 파일 하나를 더 이름 바꿔 고친다
    (web/ 안 개명 후보 2 × 2 — 사용자 한도 1 이면 git 이 비슷함 탐지를 건너뛴다)."""
    def scene(s):
        root = s.bare()
        body = 'def b() -> int:\n    return 2\n' + ''.join('# line %d of beta helper text\n' % k for k in range(30))
        for rel, text in fd.REPRO_WEB.items():
            fd.write(root / 'web' / rel, body if rel == 'legacy/beta.py' else text)
        for k in range(n):
            fd.write(root / ('old_pkg/m%04d.py' % k), 'OLD_%d = "%s"\n' % (k, 'o' * 40 + str(k)))
        fd.git(root, 'add', '-A')
        fd.git(root, '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'anchor')
        anchor = fd.git(root, 'rev-parse', 'HEAD')
        folder = root / '.dddjango-web/run'
        folder.mkdir(parents=True)
        frozen = json.loads(fd.REPRO_G0)
        frozen.update(head=anchor, scanned_at='2026-10-10T20:07:43+09:00')
        fd.write(folder / 'debt-g0.json', json.dumps(frozen))
        fd.write(folder / 'refactor-scope.md', fd.section(body=fd.decision('C2') + 'ⓑ 키: C2\n'))
        fd.git(root, 'rm', '-rq', 'old_pkg')
        for k in range(n):
            fd.write(root / ('new_pkg/n%04d.py' % k), 'NEW_%d = %d\n' % (k, k * 7919))
        (root / 'web/moved').mkdir()
        fd.git(root, 'mv', 'web/legacy/beta.py', 'web/moved/beta_renamed.py')
        with open(root / 'web/moved/beta_renamed.py', 'a', encoding='utf-8') as f:
            f.write('# lane edit\n')
        if also:
            fd.git(root, 'mv', 'web/legacy/alpha.py', 'web/moved/alpha_renamed.py')
            with open(root / 'web/moved/alpha_renamed.py', 'a', encoding='utf-8') as f:
                f.write('# lane edit\n')
        fd.git(root, 'add', '-A')
        with gitconfig(s.cfg.write('t-big', tuple(pairs))):
            s.backstop('옮긴 뒤', '--debt-residual', folder, clock=True)
    return scene


# ====================================================================== 장면 표

IM24 = [('IM24', 2, ['[IM24] BLOCKER — ' + VM + ':7'], [])]
REORDER = [('IM24 순서', 2, ['[IM24] BLOCKER — ' + HELPER + ':1'], [])]
PLAN = [('plan', 0, ['참조 치환 줄 1'], ['실행 불능']), ('참조 치환 줄', 0, ['web/root/extra/uses_helper.py:1'], [])]
MOVED = '빚 잔존 판정 불가 — ⓑ 이동 묶음 의존 — 이동도 빼고 재상정: C2'
OK_SWITCH = sw.OK_LINE % (1, '2')
# (장면 이름, 장면, 붉음 먼저 'top' | 'sub' | None(대조), 하위 폴더도 도는가, 맨 위 꼴 = [(실행 이름, exit, 있어야 할, 없어야 할)])
SCENES = (
    ('C1 color.ui=always — 더한 줄 범위(IM24)', c_im24((('color.ui', 'always'),)), 'top', True, IM24),
    ('C2 color.diff=always — 더한 줄 범위(IM24)', c_im24((('color.diff', 'always'),)), 'top', True, IM24),
    ('C3 diff.external — 더한 줄 범위(IM24)', c_external, 'top', True, IM24),
    ('C4 diff.interHunkContext=10 — 옛 빚 줄은 더한 줄이 아니다', c_inter_hunk, 'top', True,
     [('IM24 문맥', 0, ['blocker 0건'], ['[IM24]'])]),
    ('C5 color.ui=always — plan 참조 조회', c_plan((('color.ui', 'always'),)), 'top', True, PLAN),
    ('C6 color.grep=always — plan 참조 조회', c_plan((('color.grep', 'always'),)), 'top', True, PLAN),
    ('C7 grep.column=true — 참조 조회 줄 글', c_refs_column, 'top', True,
     [('참조 줄', 0, ["2, 'from web.application.order.helpers.order_helper import order_help')"], [])]),
    ('C8 대조: 기본 설정 — IM24 · plan', c_im24(()), None, True, IM24),
    ('C15 diff.algorithm=histogram — 순서 바꾼 옛 import 줄', c_reorder((('diff.algorithm', 'histogram'),)), 'top', True, REORDER),
    ('C16 속성 드라이버 diff.<drv>.algorithm=histogram — 순서 바꿈', c_reorder((('diff.pyalg.algorithm', 'histogram'),),
                                                                         '*.py diff=pyalg\n'), 'top', True, REORDER),
    ('C17 속성 `-diff` — 순서 바꿈', c_reorder((), '*.py -diff\n'), 'top', True, REORDER),
    ('C18 속성 textconv(`sed 1d`) — 더한 줄 범위(IM24)', c_textconv, 'top', True, IM24),
    ('C19 대조: 기본 설정 — 순서 바꿈', c_reorder(), None, True, REORDER),
    ('C20 저장소 .gitattributes `*.py binary` — 더한 줄 범위(IM24)', c_repo_binary, 'top', True, IM24),
    ('C21 사용자 속성 `-diff` — plan 참조 조회 · 템플릿 참조 줄', c_attr_grep, 'top', True,
     PLAN + [('템플릿 참조 줄', 0, ['  참조: web/root/scaffold/view/', '저장소 템플릿이 아직 htmx 를 가리킨다'],
              ['Binary file'])]),
    ('C22 속성 없이 내용(NUL)으로 바이너리인 기능 JS — 더한 줄 범위(WV8)', c_nul_js, 'top', True,
     [('게이트', 2, ['[WV8] BLOCKER — web/static/js/order_net.js:2'], [])]),
    ('C9 서명 + log.showSignature — WV10 격리 커밋 제목', c_wv10_subject, 'top', True,
     [('게이트 · wv10', 0, ['blocker 0건'], ['[WV10]'])]),
    ('C10 서명 + log.showSignature — 상시 답 커밋 · 때', c_standing, 'top', True,
     [('standing', 0, ['상시 답: 인식 — .dddjango/standing-answer.md:3(커밋 <해시> · <때>)'], ['Good', 'signature'])]),
    ('C11 서명 + log.showSignature — 승인 병합 제목(표시)', c_inflow_subject, 'top', True,
     [('게이트', 0, ['receive-main · ^1'], ['Good', 'signature'])]),
    ('C12 서명 + log.showSignature — 0T 확인', c_switch_signed, 'top', False, [('switch-check', 0, [OK_SWITCH], [])]),
    ('C13 대조: 서명만 — 0T 확인', c_switch_sign_only, None, False, [('switch-check', 0, [OK_SWITCH], [])]),
    ('C14 apply.whitespace=error — 끝 공백 반례의 0T 확인', c_switch_whitespace, 'top', False,
     [('switch-check', 0, [OK_SWITCH], ['적용되지 않는다'])]),
    ('N1 빚 잔존 — 미룬 키 파일 이름의 따옴표 · 탭 · 줄바꿈 · 역빗금', n_debt_names, 'top', True,
     [('옮긴 뒤 ' + label, 1, [MOVED], []) for label, _n in NAMES]),
    ('N2 승인 병합이 따옴표 이름 파일 이동을 들임', n_inflow_quote, 'top', True,
     [('승인 전', 1, [MOVED], []),
      ('승인 뒤', 0, ['[info] 승인 병합이 들인 이동 1파일 — 이 실행의 이동이 아니라 ⓑ 이동 묶음 의존에서 뺀다: legacy/be"ta.py'],
       ['판정 불가'])]),
    ('N3 refactor_audit residual — 따옴표 이름 의미 항목 파일 개명', n_residual_quote, 'top', True,
     [('residual', 0, ['리뷰어 확인 대상 1(ui)'], ['결정적 잔존 1']),
      ('개명 쌍', 0, ['\n- web/legacy/al"pha.py → web/moved/al"pha.py\n'], ['- 없음']),
      ('residual · 그냥 mv', 0, ['리뷰어 확인 대상 1(ui)'], ['결정적 잔존 1']),
      ('finalize · 그냥 mv', 0, ['해소 1'], ['리뷰어 잔존 1'])]),
    ('N7 refactor_audit residual — CR 이 든 이름의 개명 · 미추적', n_residual_cr, 'top', True,
     [('CR 이름', 0, [r"('web/legacy/be\rta.py', 'web/moved/be\rta.py')", r"'web/moved/free\rname.py'"], [r"\nta.py", r"\nname"])]),
    ('N4 plan 참조 조회 — `:` 이름 · U+2028 · 폼 피드 줄', n_plan_odd, 'top', True,
     [('plan · ' + label, 0, ['참조 치환 줄 1'], ['실행 불능']) for label in ('콜론 이름', 'U+2028 줄', '폼 피드 줄')]),
    ('N5 벤더 시대 — 벤더 폴더 이름의 따옴표 · 탭 · 줄바꿈', n_vendor_units, 'top', True,
     [('install · ' + label, 0, ['[sdk] 설치 kakao_js_sdk'], ['WV13', '되돌림']) for label in ('따옴표', '탭', '줄바꿈')]),
    ('N6 벤더 시대 — 하위 폴더 이름의 따옴표', n_vendor_folder, 'sub', True,
     [('install', 0, ['[sdk] 설치 kakao_js_sdk'], ['WV13', '되돌림'])]),
    ('L1 plan 조각 셈 — 밖 6,010행 파일 링크', l_plan_link, 'top', True,
     [('plan', 0, ['조각 1 · 파견 5'], ['OUTSIDE'])]),
    ('L2 SDK 사본 — 밖 사본 파일 · 폴더 링크', l_sdk_link, 'top', True,
     [('verify · 파일', 2, ['[WV2] BLOCKER', '심볼릭 링크 성분'], ['OUTSIDE']),
      ('게이트 · 파일', 2, ['[WV2] BLOCKER'], ['OUTSIDE']),
      ('verify · 폴더', 2, ['[WV2] BLOCKER', '심볼릭 링크 성분'], ['OUTSIDE']),
      ('게이트 · 폴더', 2, ['[WV2] BLOCKER', '[WV5] BLOCKER'], ['OUTSIDE']),
      ('사본 바이트 · 파일', 0, ['kakao_js_sdk None'], ['B\n']),
      ('사본 바이트 · 폴더', 0, ['kakao_js_sdk None'], ['B\n']),
      ('hash-object 입력 · 파일', 2, ['hash-object 입력: []'], []),
      ('hash-object 입력 · 폴더', 2, ['hash-object 입력: []'], [])]),
    ('L3 O7 범위 넓힘 — 등재 file 이 `..` 로 밖 사본을 가리킴', l_o7_outside, 'top', True,
     [('scope-add', 2, ['[sdk] 거절'], ['OUTSIDE']),
      ('사본 바이트', 0, ['static/vendor/x/../../../../../o7out/sdk.js None', 'static/vendor/./x/a.js None',
                      'static/vendor//x/a.js None'], [])]),
    ('T1 0T 확인 — 이름이 공백으로 끝나는 저장소(맨 위)', t_repo_space, 'top', False,
     [('switch-check', 1, ['build-state.json 을 읽을 수 없다'], ['최상위가 아니다'])]),
    ('T5 대조: web/ 밖 큰 변경(1,100 지움 · 1,100 더함) + 미룬 키 파일 이름 바꿔 고친 이동', big_outside(1100), None, True,
     [('옮긴 뒤', 1, [MOVED], [])]),
    ('T6 사용자 diff.renameLimit=1 — web 파일 둘을 이름 바꿔 고친 이동(개명 탐지 한도)', big_outside(
        10, (('diff.renameLimit', '1'),), True), 'top', True, [('옮긴 뒤', 1, [MOVED], [])]),
    ('T7 대조: web/ 밖 비슷한 파일을 지운 레인 — 미룬 키 파일 이동의 짝을 지킴', t_steal('backend/helpers.py', BETA_BODY.replace(
        '    return 2\n', '    return 2  # merged\n'), 'beta.py'), None, True, [('옮긴 뒤', 1, [MOVED], [])]),
    ('T8 대조: web/ 밖 같은 글 · 같은 basename 파일을 지운 레인 — 짝을 지킴', t_steal('outside_pkg/beta_renamed.py', BETA_BODY),
     None, True, [('옮긴 뒤', 1, [MOVED], [])]),
    ('T9 대조: 사용자 diff.relative=true — 미룬 키 파일 web/ 안 이동', t_relative_lane, None, True, [('옮긴 뒤', 1, [MOVED], [])]),
    ('T10 대조: 사용자 diff.relative=true — 승인 병합의 web/ 안 이동', t_relative_inflow, None, True,
     [('승인 뒤', 0, ['[info] 승인 병합이 들인 이동 1파일 — 이 실행의 이동이 아니라 ⓑ 이동 묶음 의존에서 뺀다: legacy/beta.py'],
       ['판정 불가'])]),
    ('T11 대조: 승인 병합이 web/ 안 이동과 함께 web/ 밖 같은 글 파일을 지워 들임 — 계보 짝을 지킴', t_steal_inflow, None, True,
     [('승인 뒤', 0, ['[info] 승인 병합이 들인 이동 1파일 — 이 실행의 이동이 아니라 ⓑ 이동 묶음 의존에서 뺀다: legacy/beta.py'],
       ['판정 불가'])]),
    ('T16 대조: 하위 폴더 이름이 `:` 로 시작 — 승인 병합의 web/ 안 이동', t_colon_folder, None, 'sub',
     [('승인 뒤', 0, ['[info] 승인 병합이 들인 이동 1파일 — 이 실행의 이동이 아니라 ⓑ 이동 묶음 의존에서 뺀다: legacy/beta.py'],
       ['판정 불가'])]),
    ('T13 하위 폴더: 프로젝트 밖 작업 파일을 git 자식에게도 읽히지 않음(clean filter 기록)', t_outside_clean, 'top', 'sub',
     [('지운 뒤', 0, ['legacy 잔존 ⓑ(일반) C2'], ['판정 불가']), ('git 자식의 밖 입력', 0, ['밖 입력 0 바이트'], [])]),
)


def play(tmp, cfg, index, scene, layout, scripts, tag):
    st = b.Stage(tmp / ('%02d-%s-%s' % (index, layout, tag)), layout, scripts)
    st.cfg = cfg
    scene(st)
    return st.runs


def safe_play(tmp, cfg, index, scene, layout, scripts, tag):
    """하위 폴더 · 고정 판 실행 — 준비 · 실행 중 예외는 실행 기록 한 줄로 남긴다(대조에서 다름으로 셈)."""
    try:
        return play(tmp, cfg, index, scene, layout, scripts, tag)
    except Exception as error:
        return [('장면 예외', -1, '%s: %s' % (type(error).__name__, str(error)[-600:]))]


def shape_ok(runs, shape):
    for run_name, code, must, never in shape:
        got = next((r for r in runs if r[0] == run_name), None)
        if got is None or got[1] != code or not all(m in got[2] for m in must) or any(n in got[2] for n in never):
            return False
    return True


# ====================================================================== S — 정적: 프로세스 실행 자리 대조

# 실행 함수(모듈 → 이름) — 이 밖의 실행 길(별칭 · getattr 등)은 «부르지 않고 꺼냄» 으로 막는다
LAUNCH = {'subprocess': {'run', 'Popen', 'call', 'check_call', 'check_output', 'getoutput', 'getstatusoutput'},
          'os': {'system', 'popen', 'execv', 'execve', 'execvp', 'execvpe', 'execl', 'execle', 'execlp', 'execlpe',
                 'spawnv', 'spawnve', 'spawnvp', 'spawnvpe', 'spawnl', 'spawnle', 'spawnlp', 'spawnlpe',
                 'posix_spawn', 'posix_spawnp'},
          'pty': {'spawn'}, 'asyncio': {'create_subprocess_exec', 'create_subprocess_shell'}}
SHELL_LAUNCH = {('subprocess', 'getoutput'), ('subprocess', 'getstatusoutput'), ('os', 'system'), ('os', 'popen'),
                ('asyncio', 'create_subprocess_shell')}
# 알려진 실행 자리(파일, 감싼 함수, 프로그램) → 수. git 은 모두 `*GIT_PINS` 를 실은 목록이어야 한다(아래 «git 목록» 대조).
# 새 실행 자리는 이 표에 이유와 함께 올려야 초록이다 — 조용히 늘지 않게.
EXPECTED_LAUNCH = {
    ('refactor_audit.py', '_git', 'git'): 1, ('refactor_audit.py', '_git_try', 'git'): 1,
    ('sdk_vendor.py', '_no_template_refs', 'git'): 1,
    ('src/check_component_css.py', 'Tree._content_changes', 'git'): 1, ('src/check_component_css.py', 'Tree.read', 'git'): 1,
    ('src/check_tests.py', '_collect_once.git', 'git'): 1, ('src/check_tests.py', '_commit_oid', 'git'): 1,
    ('src/check_tests.py', '_rename_targets', 'git'): 1,
    ('src/check_vendor.py', '_git', 'git'): 1, ('src/common.py', '_git_raw', 'git'): 1,
    ('src/debt.py', '_git_out', 'git'): 1, ('src/debt.py', 'debt_universe', 'git'): 1,
    ('src/debt.py', 'reference_lines', 'argv=cmd'): 1,                  # cmd = ['git', *GIT_PINS, …] (git 목록 대조가 본다)
    ('src/inflow.py', '_git', 'git'): 1, ('src/inflow.py', '_split', 'git'): 1, ('src/inflow.py', '_split.measure', 'git'): 1,
    ('src/inflow.py', '_split.measure', 'sys.executable'): 1,           # 부모 판 스냅숏에 backstop.py
    ('src/inflow.py', '_split.measure', 'tar'): 1,                      # git archive 풀기
    ('src/scope.py', '_git', 'git'): 1,                                # 2.7.0 시험 범위(--test-scope)
    ('src/sdk_registry.py', '_git', 'git'): 1, ('src/sdk_registry.py', 'wv2_problems', 'git'): 3,
    ('src/subst.py', '_approved_merges', 'git'): 2, ('src/subst.py', '_blob', 'git'): 1, ('src/subst.py', '_git', 'git'): 1,
    ('src/subst.py', '_history', 'git'): 1, ('src/subst.py', '_is_ancestor', 'git'): 1, ('src/subst.py', '_records', 'git'): 1,
    ('src/subst.py', '_switch_record.commits', 'git'): 1,
    ('src/switch_check.py', 'Git.call', 'git'): 1,
    ('src/switch_check.py', 'Runner.run', 'argv=argv'): 1,              # 사용자 시험 명령(0T)
}


def launch_census(scripts):
    """test/ 밖 .py 의 프로세스 실행 자리 → (자리 [(파일, 감싼 함수, 프로그램)], 문제 [글]) — 정직한 코드의 새 실행 자리를
    잡는 울타리다. 보는 것: import 로 묶은 이름(`import subprocess` · `import os.path` · `from os import system` · 다른
    모듈이 다시 내보낸 이름)의 모듈 수준 실행 함수 부름. 문제 = 셸 실행 · shell= · `*GIT_PINS` 없는 git 목록 · 튜플(절대
    경로 포함) · 그 실행 함수를 부르지 않고 꺼냄 · 그 모듈을 값으로 씀(별칭 · getattr) · `from <실행 모듈> import *` · 이름
    `sys.modules` · 속성 `__dict__` · 이름 `__import__` · importlib. 일부러 숨긴 꼴(`sys` 별칭 · `from sys import modules` ·
    `from os import __dict__` · `__getattribute__` · `os.path.os` · 하위 모듈 경로 `asyncio.subprocess` · 이벤트 루프 메서드 ·
    다른 모듈 속성 · `builtins.__import__` · `globals()` · 다른 표준 모듈이 안에서 띄우는 길(`_posixsubprocess` ·
    `webbrowser` · `platform` · ctypes · multiprocessing) · 문자열 exec/eval)은 보지 않는다."""
    sites, problems = [], []
    for path in sorted(Path(scripts).rglob('*.py')):
        rel = path.relative_to(scripts).as_posix()
        if 'test' in rel.split('/')[:-1]:
            continue
        tree = ast.parse(path.read_text(encoding='utf-8'))
        modules, funcs, parents = {}, {}, {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
            if isinstance(node, ast.Import):
                # `import os.path` 도 이름 `os` 를 묶는다 · `import os as o` 는 `o`
                modules.update({a.asname or a.name: a.name for a in node.names if a.name in LAUNCH})
                modules.update({top: top for top in (a.name.split('.')[0] for a in node.names if not a.asname)
                                if top in LAUNCH})
            elif isinstance(node, ast.ImportFrom) and node.module not in LAUNCH:
                # 다른 모듈이 다시 내보낸 실행 모듈(`from .common import subprocess`)도 그 모듈이다
                modules.update({a.asname or a.name: a.name for a in node.names if a.name in LAUNCH})
            elif isinstance(node, ast.ImportFrom):
                funcs.update({a.asname or a.name: (node.module, a.name) for a in node.names
                              if a.name in LAUNCH[node.module]})
                if any(a.name == '*' for a in node.names):
                    problems.append('%s:%d from %s import * — 실행 함수 이름을 가릴 수 없다(해석 불가)'
                                    % (rel, node.lineno, node.module))

        def owner(node):
            names = []
            while node in parents:
                node = parents[node]
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    names.append(node.name)
            return '.'.join(reversed(names)) or '<모듈>'

        def launcher(func):
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id in modules:
                return (modules[func.value.id], func.attr) if func.attr in LAUNCH[modules[func.value.id]] else None
            return funcs.get(func.id) if isinstance(func, ast.Name) else None

        called = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or launcher(node.func) is None:
                continue
            kind = launcher(node.func)
            called.add(id(node.func))
            where = '%s:%d' % (rel, node.lineno)
            if kind in SHELL_LAUNCH:
                problems.append('%s %s.%s — 셸 실행' % (where, *kind))
            if any(k.arg == 'shell' and not (isinstance(k.value, ast.Constant) and k.value.value is False)
                   for k in node.keywords):
                problems.append('%s shell= — 셸 실행' % where)
            argv = node.args[0] if node.args else next((k.value for k in node.keywords if k.arg == 'args'), None)
            if isinstance(argv, ast.BinOp) and isinstance(argv.left, (ast.List, ast.Tuple)):
                argv = argv.left                       # ['git', *GIT_PINS, …] + args
            if isinstance(argv, (ast.List, ast.Tuple)) and argv.elts:
                head = argv.elts[0]
                program = (posixpath.basename(head.value) if isinstance(head, ast.Constant) and isinstance(head.value, str)
                           else ast.unparse(head))
            else:
                program = 'argv=' + (ast.unparse(argv) if argv is not None else '?')
            sites.append((rel, owner(node), program))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in modules \
                    and node.attr in LAUNCH[modules[node.value.id]] and id(node) not in called:
                problems.append('%s:%d %s.%s — 실행 함수를 부르지 않고 꺼냄(해석 불가)' % (rel, node.lineno, node.value.id, node.attr))
            elif isinstance(node, ast.Name) and node.id in modules and not isinstance(parents.get(node), ast.Attribute):
                problems.append('%s:%d 모듈 %s 를 값으로 씀(해석 불가)' % (rel, node.lineno, node.id))
            elif isinstance(node, ast.Attribute) and (node.attr == '__dict__' or (
                    node.attr == 'modules' and isinstance(node.value, ast.Name) and node.value.id == 'sys')):
                problems.append('%s:%d %s — 모듈 속을 이름 글자로 꺼냄(해석 불가)'
                                % (rel, node.lineno, 'sys.modules' if node.attr == 'modules' else '__dict__'))
            elif isinstance(node, ast.Name) and node.id in funcs and id(node) not in called:
                problems.append('%s:%d %s — 실행 함수를 부르지 않고 꺼냄(해석 불가)' % (rel, node.lineno, node.id))
            elif (isinstance(node, ast.Name) and node.id == '__import__'
                  or isinstance(node, ast.Import) and any(a.name.split('.')[0] == 'importlib' for a in node.names)
                  or isinstance(node, ast.ImportFrom) and (node.module or '').split('.')[0] == 'importlib'):
                problems.append('%s:%d 동적 import(해석 불가)' % (rel, node.lineno))
            elif isinstance(node, (ast.List, ast.Tuple)) and node.elts and isinstance(node.elts[0], ast.Constant) \
                    and isinstance(node.elts[0].value, str) and posixpath.basename(node.elts[0].value) == 'git':
                joined = isinstance(parents.get(node), ast.Call) and isinstance(parents[node].func, ast.Attribute) \
                    and parents[node].func.attr == 'join'
                second = node.elts[1] if len(node.elts) > 1 else None
                if joined:
                    continue                       # 사람에게 보이는 명령 글(문자열을 잇는 목록) — 실행이 아니다
                if isinstance(node, ast.Tuple) or node.elts[0].value != 'git':
                    problems.append('%s:%d git 실행은 이름 `git` 의 목록 꼴로만(튜플 · 경로 붙은 git 금지)' % (rel, node.lineno))
                elif not (isinstance(second, ast.Starred) and isinstance(second.value, ast.Name)
                          and second.value.id == 'GIT_PINS'):
                    problems.append('%s:%d git 목록의 둘째 원소가 *GIT_PINS 가 아니다' % (rel, node.lineno))
    return sites, problems


def launch_issues(scripts, expected):
    """실행 자리 대조 → 어긋남 글 목록(비면 초록): 문제 + 표에 없는 새 자리 + 표에 있는데 사라진 자리."""
    sites, problems = launch_census(scripts)
    got = collections.Counter(sites)
    want = collections.Counter(expected)
    return (problems + ['새 실행 자리 %s(%d) — 알려진 자리 표에 없다' % (k, n) for k, n in (got - want).items()]
            + ['사라진 실행 자리 %s(%d)' % (k, n) for k, n in (want - got).items()])


def _site(program):
    """표본 파일 하나의 알려진 자리 표 — 그 표본의 실행 자리를 «알려진» 것으로 두어 «새 실행 자리» 를 빼고 다른 규칙만 본다."""
    return {('src/sample.py', '<모듈>', program): 1}


# (표본 이름, 글, 알려진 자리 표, 잡는 까닭 글자) — 표본마다 대조 규칙 하나에만 걸리게 갈랐다(그 규칙만 지우면 그 표본이 붉다).
BYPASS = (
    ('튜플', 'import subprocess\nGIT_PINS = ()\nsubprocess.run(("git", *GIT_PINS, "status"))\n', _site('git'),
     '목록 꼴로만(튜플 · 경로 붙은 git 금지)'),
    ('절대 경로 git', 'import subprocess\nGIT_PINS = ()\nsubprocess.run(["/usr/bin/git", *GIT_PINS, "status"])\n', _site('git'),
     '목록 꼴로만(튜플 · 경로 붙은 git 금지)'),
    ('shell=True 문자열', 'import subprocess\nsubprocess.run("git status", shell=True)\n', _site("argv='git status'"),
     'shell= — 셸 실행'),
    ('os.system', 'import os\nos.system("git status")\n', _site("argv='git status'"), 'os.system — 셸 실행'),
    ('os.popen', 'import os\nos.popen("git status").read()\n', _site("argv='git status'"), 'os.popen — 셸 실행'),
    ('Popen 상수 없음', 'import subprocess\nsubprocess.Popen(["git", "archive", "HEAD"])\n', _site('git'),
     '둘째 원소가 *GIT_PINS 가 아니다'),
    ('실행 함수 꺼내 담기', 'import subprocess\nrun = subprocess.run\nrun(["sh", "-c", "git status"])\n', {},
     'subprocess.run — 실행 함수를 부르지 않고 꺼냄'),
    ('from 으로 묶은 실행 함수 꺼내 담기', 'from subprocess import run\nf = run\nf(["sh", "-c", "git status"])\n', {},
     ' run — 실행 함수를 부르지 않고 꺼냄'),
    ('별칭 변수', 'import subprocess\nexe = "git"\nsubprocess.run([exe, "status"])\n', {}, '새 실행 자리'),
    ('from-import 별칭', 'from subprocess import run as r\nr(["sh", "-c", "git status"])\n', {}, '새 실행 자리'),
    ('모듈 별칭', 'import subprocess as sp\nsp.check_output(["sh", "-c", "git log"])\n', {}, '새 실행 자리'),
    ('asyncio exec', 'import asyncio\nasyncio.create_subprocess_exec("git", "status")\n', {}, '새 실행 자리'),
    ('os.execvp', 'import os\nGIT_PINS = ()\nos.execvp("git", ["git", *GIT_PINS, "status"])\n', {}, '새 실행 자리'),
    ('sh -c', 'import subprocess\nsubprocess.run(["sh", "-c", "git status"])\n', {}, '새 실행 자리'),
    ('상수 실은 새 git 자리', 'import subprocess\nGIT_PINS = ()\nsubprocess.run(["git", *GIT_PINS, "status"])\n', {},
     '새 실행 자리'),
    ('다른 모듈이 다시 내보낸 subprocess', 'from .common import subprocess\nsubprocess.run(["sh", "-c", "git status"])\n', {},
     '새 실행 자리'),
    ('import os.path 뒤 os.system', 'import os.path\nos.system("git status")\n', {}, 'os.system — 셸 실행'),
    ('getattr', 'import subprocess\ngetattr(subprocess, "run")(["sh", "-c", "git status"])\n', {}, '모듈 subprocess 를 값으로 씀'),
    ('os getattr', 'import os\ngetattr(os, "system")("git status")\n', {}, '모듈 os 를 값으로 씀'),
    ('os 모듈 별칭', 'import os\nm = os\nm.system("git status")\n', {}, '모듈 os 를 값으로 씀'),
    ('asyncio getattr', 'import asyncio\ngetattr(asyncio, "create_subprocess_exec")("git", "status")\n', {},
     '모듈 asyncio 를 값으로 씀'),
    ('pty getattr', 'import pty\ngetattr(pty, "spawn")(["sh", "-c", "git status"])\n', {}, '모듈 pty 를 값으로 씀'),
    ('star import subprocess', 'from subprocess import *\nrun(["sh", "-c", "git status"])\n', {},
     'import * — 실행 함수 이름을 가릴 수 없다'),
    ('star import os', 'from os import *\nsystem("git status")\n', {}, 'import * — 실행 함수 이름을 가릴 수 없다'),
    ('sys.modules', 'import sys\nsys.modules["subprocess"].run(["sh", "-c", "git status"])\n', {}, 'sys.modules — 모듈 속을'),
    ('__dict__', 'import subprocess\nsubprocess.__dict__["run"](["sh", "-c", "git status"])\n', {}, '__dict__ — 모듈 속을'),
    ('__import__', '__import__("subprocess").run(["sh", "-c", "git status"])\n', {}, '동적 import'),
    ('importlib', 'import importlib\nimportlib.import_module("subprocess").run(["sh", "-c", "git status"])\n', {},
     '동적 import'),
)


def main():
    os.environ['GIT_CONFIG_NOSYSTEM'] = '1'
    for env in ENVS:
        env['GIT_CONFIG_NOSYSTEM'] = '1'
    with tempfile.TemporaryDirectory(prefix='web252-') as tmp_name:
        tmp = Path(tmp_name).resolve()
        cfg = Configs(tmp)
        for env in ENVS:
            env['GIT_CONFIG_GLOBAL'] = str(cfg.base)
        fixed = b.release_scripts(tmp / 'release', RELEASE_251, 'R')
        issues = launch_issues(SCRIPTS, EXPECTED_LAUNCH)
        check('S1 프로세스 실행 자리(test/ 밖) = 알려진 자리 표 · git 은 모두 `*GIT_PINS` 를 실은 목록 · 셸 · 해석 못 할 실행 없음',
              not issues, '\n'.join(issues))
        for label, source, known, reason in BYPASS:
            box = tmp / 'bypass' / label.replace(' ', '_').replace('/', '_')
            (box / 'src').mkdir(parents=True)
            (box / 'src/sample.py').write_text(source, encoding='utf-8')
            found = launch_issues(box, known)
            check('S2 정적 대조 표본 — %s 는 «%s» 로 잡힌다' % (label, reason.strip()), any(reason in i for i in found),
                  '\n'.join(found))
        if fixed is not None:
            check('R S1 — 고정 판(%s)은 어긋났다(붉음 먼저)' % RELEASE_251, bool(launch_issues(fixed, EXPECTED_LAUNCH)))
        only = [k for k in os.environ.get('FIXTURES_252_ONLY', '').split(',') if k]   # 고친 자리 되돌림 실험용 장면 고르기
        if only:
            print('[info] FIXTURES_252_ONLY — 장면 %s 만 돈다' % ' '.join(only))
        for index, (name, scene, red, both, shape) in enumerate(SCENES, 1):
            if only and name.split(' ')[0] not in only:
                continue
            first = 'sub' if both == 'sub' else 'top'   # 'sub' = 하위 폴더에서만 뜻이 있는 장면(프로젝트 밖)
            try:
                top = play(tmp, cfg, index, scene, first, SCRIPTS, 'new')
            except Skip as why:
                print('SKIP %s — %s(실패로 세지 않는다)' % (name, why))
                continue
            except Exception as error:   # 준비 · 실행 중 예외 — 이 장면만 실패로 세고 다음 장면으로
                check('%s — 장면 실행' % name, False, '%s: %s' % (type(error).__name__, str(error)[-1200:]))
                continue
            for run_name, code, must, never in shape:
                got = next((r for r in top if r[0] == run_name), (run_name, None, '(실행 없음)'))
                check('%s · 꼴 — %s: exit %d' % (name, run_name, code),
                      got[1] == code and all(m in got[2] for m in must) and not any(n in got[2] for n in never),
                      'exit=%s\n%s' % (got[1], got[2][-1500:]))
            if both is True:
                sub = safe_play(tmp, cfg, index, scene, 'sub', SCRIPTS, 'new')
                check('%s — 하위 폴더 출력 = 맨 위 출력(실행 %d)' % (name, len(top)), sub == top, b.first_difference(top, sub))
            if fixed is None:
                continue
            old = safe_play(tmp, cfg, index, scene, first, fixed, 'old')
            if red == 'top':
                check('R %s — 고정 판(%s)은 %s에서 이 꼴을 어겼다(붉음 먼저)'
                      % (name, RELEASE_251, '하위 폴더' if first == 'sub' else '맨 위'), not shape_ok(old, shape))
            elif red == 'sub':
                old_sub = safe_play(tmp, cfg, index, scene, 'sub', fixed, 'old')
                check('R %s — 고정 판(%s)은 하위 폴더에서 맨 위와 달랐다(붉음 먼저)' % (name, RELEASE_251), old_sub != old)
            else:
                check('R %s — 대조: 고정 판(%s)도 꼴을 지키고 %s 출력이 같다' % (name, RELEASE_251, '하위 폴더' if first == 'sub' else '맨 위'),
                      shape_ok(old, shape) and old == top, b.first_difference(old, top))
        if fixed is None:
            print('SKIP R — 고정 판 커밋 %s 가 이 저장소 이력에 없다(얕은 clone 등) — 붉음 먼저 대조만 건너뛴다' % RELEASE_251)
    print('fixtures_patch252_gitout: PASS=%d FAIL=%d' % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
