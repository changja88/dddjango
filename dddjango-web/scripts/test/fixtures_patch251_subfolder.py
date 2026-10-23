#!/usr/bin/env python3
"""2.5.1 하위 폴더 프로젝트 회귀 — 프로젝트 루트가 git 저장소의 하위 폴더(`<저장소>/server/`)여도 러너 · 도구가 맨 위
프로젝트와 같은 판정을 내는가. 임시 git 저장소만 만들고 끝나면 지운다(네트워크 · 브라우저 없음).

장면마다 같은 합성 프로젝트를 두 꼴(맨 위 · 하위 폴더)로 만들어 같은 일을 하고 다섯을 본다.
  ① 꼴 — 맨 위 출력이 장면이 뜻한 판정이다(헛통과 방지).
  ② 같음 — 하위 폴더 출력이 맨 위 출력과 같다(커밋 해시 · 임시 경로 · 시각만 가린다).
  ③ U — 맨 위 출력이 바탕 판(BASELINE — 판마다 바탕 커밋으로 올린다)과 같다(이 판이 맨 위 프로젝트의 출력을 바꾸지
     않았다). 이 판이 일부러 바꾼 맨 위 실행(TOP_CHANGED)은 거꾸로 바탕 판과 «다른지» 본다(BASELINE 을 올리면 비운다).
     글만 바꾼 자리(TOP_TEXT_CHANGED)는 바탕 판 출력에 그 바꿈을 넣은 뒤 «같음»을 본다(BASELINE 을 올리면 비운다).
  ④ R — 고정 판(RELEASE_250 · 하위 폴더 결함이 있던 2.5.0 — 올리지 않는다)은 하위 폴더에서 맨 위와 다른 출력을 냈다
     (붉음 먼저 — 대조 장면은 그 판도 같아야 한다).
  ⑤ 철자 — 프로젝트 루트를 대소문자만 다른 철자(`…/REPO` · `…/repo/SERVER`)로 넘겨도 두 꼴 모두 정상 철자와 같은 출력이다.
     고정 판은 맨 위에서 달랐다(CASE_RED 장면 — 붉음 먼저). 대소문자를 가리는 볼륨에는 그런 철자의 폴더가 없으므로 이
     대조만 건너뛰고 건너뛴 사실을 낸다(실패로 세지 않는다).
  두 커밋은 HEAD 에 묶지 않는다. 이력에 없으면(얕은 clone 등) 그 대조만 건너뛰고 건너뛴 사실을 낸다(실패로 세지 않는다).
하위 폴더 꼴의 저장소 뿌리에는 프로젝트 밖 파일(README.md)과 미끼(`web/` · `web_test/` — 프로젝트 것으로 읽으면 안 된다)를 둔다.
프로젝트 폴더 이름은 `server` 다 — 이름에 걸리는 판정을 보는 장면(W2 `web` · G12 · T3 · W3 공백으로 시작하는 이름 ·
W4 · W5 한글 이름)만 바꾼다. 저장소 폴더 이름은 `repo` 다 — T5 · T6 만 공백 · 줄바꿈으로 끝나는 이름을 쓴다.

묶음: G 게이트(기준점 파일 목록 · git 설정 diff.relative) · T 바뀐 시험(TG2 · TG3) · S 치환 확인(--subst-check) ·
D 빚 잔존(--debt-residual · 한글 이름 개명) · A refactor_audit(residual · standing --gate · 프로젝트 밖 파일에 닿는 위치 ·
check-verdict 의 별도 요청 편집할 곳 · plan 의 참조 조회와 git 설정 grep.fullName) · W SDK(사용자 원문 자리 · 벤더 검사의
git 읽기 · 한글 이름 하위 폴더 · git 설정 log.showRoot)."""
import hashlib
import json
import os
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
import fixtures_patch230 as fx  # noqa: E402
import fixtures_patch231_debt as fd  # noqa: E402
import fixtures_patch231_subst as sx  # noqa: E402
import fixtures_patch240_shell as sh  # noqa: E402
import fixtures_patch250_component_css as cs  # noqa: E402

BASELINE = '11d84153'  # U 의 바탕 판(배포된 dddjango-web 2.5.1) — 판마다 바탕 커밋으로 올린다
RELEASE_250 = 'cfa41f58'  # R 의 고정 판(배포된 dddjango-web 2.5.0) — 올리지 않는다(R 이 이 판의 하위 폴더 결함에 묶여 있다)
W1 = 'W1 SDK 사용자 원문 — 프로젝트 web/ · .dddjango-web/ 안은 출처가 아니다'
A4 = 'A4 refactor_audit residual — 프로젝트 밖으로 풀리는 근거 링크는 근거가 아니다'
A5 = 'A5 refactor_audit residual — 밖 링크를 따라 읽은 해소 지문은 이월하지 않는다'
A6 = 'A6 대조: 프로젝트 루트를 링크로 넘겨도 A4 와 같다'
W2 = 'W2 대조: 프로젝트 폴더 이름이 web 이어도 프로젝트 안 문서는 출처다'
W3 = 'W3 프로젝트 폴더 이름이 공백으로 시작해도 그 폴더의 web/ 안은 출처가 아니다'
W6 = 'W6 git 설정 log.showRoot=false — 목록 시대 첫 커밋에 생긴 벤더 내용은 WV13'
W7 = 'W7 한글 이름 벤더 폴더의 목록 이전 같은 자리 사본 — SDK 정식 등재'
A8 = 'A8 refactor_audit check-verdict — 별도 요청(web/ 밖)의 편집할 곳이 프로젝트 밖 파일이면 채택'
D3 = 'D3 미룬 키의 한글 이름 파일을 레인이 옮김'
D4 = 'D4 승인 병합이 들인 한글 이름 파일 이동'
T5 = 'T5 T2 를 공백으로 끝나는 저장소 폴더 이름으로'
T6 = 'T6 T2 를 줄바꿈으로 끝나는 저장소 폴더 이름으로'
KOREAN = '한글빚.py'
# 이 판이 맨 위 출력을 일부러 바꾼 실행(장면 이름 → 실행 이름들) — 2.5.2 는 이 묶음 45 장면의 맨 위 출력을 바꾸지 않는다.
# BASELINE 을 올리면 비운다.
TOP_CHANGED = {}
# 이 판이 바탕 판 맨 위 출력의 글만 바꾼 자리(옛 글, 새 글) — U 는 바탕 판 출력에 이 바꿈을 넣은 뒤 «같음»을 본다.
# 2.8.0: TG1 교정(안내) 글(판정 · exit 무변). BASELINE 을 올리면 비운다.
TOP_TEXT_CHANGED = (('명세 행위목록 각 항목마다 그 행위를',
                     '명세 시험 입장 표의 add 행대로(시험 입장 표가 없는 실행은 명세 행위 목록대로) 그 행위를'),)
# 고정 판(RELEASE_250)이 맨 위에서 대소문자만 다른 루트 철자에 정상 철자와 다른 출력을 낸 장면(기준점 목록 · 바뀐 파일 ·
# 승인 유입 가르기를 넘겨받은 루트 글자로 셈했다) — 올리지 않는다.
CASE_RED = ('G1', 'G2', 'G3', 'G6', 'G7', 'G8', 'G10', 'G11', 'G12', 'T2', 'T3', 'T4')
ENV = fx.ENV
PASS = FAIL = 0
VM = 'web/application/order/application_layer/view_model/order_list_vm.py'
SHELL = fx.FLAT_SHELL
ORDER_TEST = 'web_test/application/order/application_layer/order_list_vm_test.py'
UPSTREAM_TEST = 'web_test/application/order/application_layer/order_upstream_test.py'
BAIT = (('README.md', 'monorepo\n'), ('web/top_bait.py', 'def top_bait() -> int:\n    return 1\n'),
        ('web_test/top_bait_test.py', 'def test_top_bait() -> None:\n    assert True\n'))
# SDK 승인 «사용자 원문» 한 줄 읽기(sdk_registry.source_line) — 경로 글자가 꼴마다 달라 판정 낱말만 낸다
SOURCE_LINE = ('import sys\nfrom pathlib import Path\nsys.path.insert(0, sys.argv[1])\nfrom src.sdk_registry import source_line\n'
               'raw, problems, _notes = source_line(Path(sys.argv[2]), {"path": sys.argv[3], "commit": sys.argv[4], "line": 1})\n'
               'print("줄 읽음" if raw is not None and not problems else "거절")\n')
# 벤더 검사의 git 읽기(check_vendor._git_text)가 낸 diff 경로 — 프로젝트 접두를 뗀 꼴로 낸다(저장소 기준이 아니면 `??`)
VENDOR_DIFF = ('import subprocess, sys\nfrom pathlib import Path\nsys.path.insert(0, sys.argv[1])\nfrom src import check_vendor\n'
               'root = Path(sys.argv[2])\n'
               'prefix = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-prefix"], capture_output=True, text=True).stdout.strip()\n'
               'names = check_vendor._git_text(root, "diff", "--name-only", sys.argv[3], "HEAD").split()\n'
               'print(" ".join(sorted(n[len(prefix):] if n.startswith(prefix) else "??" + n for n in names)))\n')
# SDK 제거 · 판 올림 앞의 «저장소 템플릿이 아직 가리킨다» 거절(sdk_vendor._no_template_refs)이 보이는 참조 줄
TEMPLATE_REFS = ('import sys\nfrom pathlib import Path\nsys.path.insert(0, sys.argv[1])\nimport sdk_vendor\n'
                 'try:\n    sdk_vendor._no_template_refs(Path(sys.argv[2]), "htmx", sys.argv[3])\n'
                 'except sdk_vendor.Refused as error:\n    print(error)\n')
# 리뷰어 행 위치 · 해소 근거 위치를 받는 한 함수(refactor_audit._location_ok) — 그 경로의 1행을 받는가
# (명령 인자에는 NUL 을 실을 수 없어 `<NUL>` 로 적어 넘긴다)
LOCATION = ('import sys\nfrom pathlib import Path\nsys.path.insert(0, sys.argv[1])\nimport refactor_audit\n'
            'rel = sys.argv[3].replace("<NUL>", chr(0))\n'
            'ok = refactor_audit._location_ok(Path(sys.argv[2]).resolve(), (rel, 1, 1))\n'
            'print("위치 받음" if ok else "위치 거절")\n')


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok and detail:
        print('    ' + str(detail).replace('\n', '\n    ')[:3000])


def release_scripts(tmp, sha, use):
    """커밋 sha 의 scripts 를 임시 폴더 tmp 에 푼다 → 그 scripts 폴더(없으면 None). 매니페스트는 지금 판 것을 덮는다 —
    판 글자를 읽는 알림 줄이 두 러너에서 같아, 판을 올린 커밋에서도 그 줄을 가리지 않고 대조한다."""
    archive = subprocess.run(['git', '-C', str(REPO), 'archive', sha, 'dddjango-web/scripts',
                              'dddjango-web/.claude-plugin'], capture_output=True, env=ENV)
    if archive.returncode:
        print('SKIP %s — 판 커밋 %s 가 이 저장소 이력에 없다(얕은 clone 등) — 그 대조만 건너뛴다(실패로 세지 않는다)' % (use, sha))
        return None
    tmp.mkdir()
    subprocess.run(['tar', '-xf', '-', '-C', str(tmp)], input=archive.stdout, check=True)
    shutil.copyfile(SCRIPTS.parent / '.claude-plugin' / 'plugin.json', tmp / 'dddjango-web/.claude-plugin/plugin.json')
    return tmp / 'dddjango-web' / 'scripts'


class Stage:
    """장면 한 번(한 꼴 · 한 러너) — 프로젝트 자리와 실행 기록."""

    def __init__(self, box, layout, scripts, spelling='same'):
        self.box = Path(box)
        self.box.mkdir(parents=True)
        self.layout = layout
        self.scripts = scripts
        self.spelling = spelling  # 'same' 그대로 · 'case' 명령에 프로젝트 루트를 대소문자만 다른 철자로 넘긴다
        self.link = None  # 장면이 걸면 — 명령에 프로젝트 루트 대신 넘기는(그 루트를 가리키는) 심볼릭 링크
        self.runs = []  # (실행 이름, exit, 가린 출력)
        self.adopt(self.box / 'repo')

    def adopt(self, top, folder='server'):
        """저장소 뿌리를 정한다 — 프로젝트 루트는 맨 위 꼴이면 그 자리, 하위 폴더 꼴이면 `<뿌리>/<folder>`."""
        self.top = Path(top)
        self.root = self.top if self.layout == 'top' else self.top / folder

    def prefix(self):
        """저장소 안 프로젝트 접두(맨 위 꼴은 빈 글자) — 폴더 이름 앞뒤 공백을 그대로 둔다."""
        return '' if self.layout == 'top' else self.root.relative_to(self.top).as_posix() + '/'

    def shown(self):
        """명령에 넘기는 프로젝트 루트 글자 — 장면이 건 링크(또는 그 루트) · 철자 대조면 마지막 이름을 대문자로."""
        shown = self.link if self.link is not None else self.root
        return shown.with_name(shown.name.upper()) if self.spelling == 'case' else shown

    def bait(self):
        if self.layout == 'sub':
            for rel, text in BAIT:
                fd.write(self.top / rel, text)

    def outside(self):
        """프로젝트 밖 폴더(top_bait.py 가 든) — 하위 폴더 꼴은 저장소 뿌리의 미끼 web/(저장소 안 · 프로젝트 밖), 맨 위 꼴은 저장소 밖."""
        if self.layout == 'sub':
            return self.top / 'web'
        fd.write(self.box / 'outside/top_bait.py', BAIT[1][1])
        return self.box / 'outside'

    def std(self):
        """fixtures_patch230 의 표준 트리(빚 0) — git 초기화만(커밋은 장면이)."""
        p = fx.mkstd(self.root, None if self.layout == 'top' else self.top)
        self.bait()
        return p

    def bare(self):
        """빈 프로젝트 자리 + git 초기화(파일은 장면이 쓴다)."""
        self.root.mkdir(parents=True)
        fd.git(self.top, 'init', '-q', '-b', 'main')
        self.bait()
        return self.root

    def commit_all(self, message):
        fx.git(self.root, 'add', '-A')
        fx.git(self.root, 'commit', '-qm', message)
        return fx.git(self.root, 'rev-parse', 'HEAD')

    def mask(self, text):
        text = text.replace(str(self.shown()), '<루트>')
        text = text.replace(str(self.root.resolve()), '<루트>').replace(str(self.top.resolve()), '<저장소>')
        text = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})', '<때>', text)
        text = re.sub(r'\b\d{8}-\d{4,6}\b', '<시각>', text)
        return fx.counts_normalized(re.sub(r'\b[0-9a-f]{7,40}\b', '<해시>', text))

    def _record(self, name, cmd):
        cmd = [a.replace(str(self.root), str(self.shown())) for a in cmd]
        r = subprocess.run(cmd, cwd=str(self.shown()), env=ENV, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.runs.append((name, r.returncode, self.mask(r.stdout.decode('utf-8', 'replace'))))

    def backstop(self, name, *args, clock=False):
        self.tool(name, 'backstop.py', self.root, *args, clock=clock)

    def tool(self, name, script, *args, clock=False):
        """clock 이면 fixtures_patch231_debt 의 고정 시계 실행기로 돈다(시각을 찍는 잔존 판정)."""
        argv = [str(a) for a in args]
        head = ['-c', fd.RUN, str(self.scripts), script] if clock else [str(self.scripts / script)]
        self._record(name, [sys.executable, '-B', *head, *argv])

    def code(self, name, source, *args):
        self._record(name, [sys.executable, '-B', '-c', source, str(self.scripts), *map(str, args)])

    def section(self, name, path, head):
        """도구가 쓴 기록 파일의 한 절(머리 줄부터 다음 `## ` 앞까지)을 실행 기록처럼 남긴다(파일 · 절이 없으면 «(없음)»)."""
        text = Path(path).read_text(encoding='utf-8') if Path(path).is_file() else ''
        found = re.search(r'^%s\n(.*?)(?=^## |\Z)' % re.escape(head), text, re.M | re.S)
        self.runs.append((name, 0, self.mask(head + '\n' + found.group(1) if found else '(없음)')))


# ====================================================================== G — 게이트(기준점 파일 목록)

def legacy_tree(p):
    """기준점에 이미 있는 규약 밖 옛 배치 — 전부 «있던 폴더» 다(레인은 건드리지 않는다)."""
    o = 'web/application/order/'
    p.w('web/templates/legacy_page.html', '<p>legacy</p>')                                      # ST0
    p.w('web/application/billing/presentation_layer/view/billing_view.py',                       # ST4 골격 미비 BC · TG1
        'from django.http import HttpRequest, HttpResponse', '', '',
        'def billing_view(request: HttpRequest) -> HttpResponse:', '    return HttpResponse("ok")')
    p.w(o + 'helpers/order_helper.py', 'def order_help() -> int:', '    return 1')               # ST3
    p.w('web/common/misc/misc_tool.py', 'def misc_tool() -> int:', '    return 1')               # ST11
    p.w('web/static/css/site.css', '.site { margin: 0; }')                                       # ST12
    p.w('web/root/extra/root_extra.py', 'def root_extra() -> int:', '    return 1')              # ST8
    p.w('web/design_system/component/etc/etc_badge.html', '<span class="etc-badge">b</span>')    # ST10
    p.w(o + 'infra_layer/cache/order_cache.py', 'def order_cache() -> int:', '    return 1')     # ST6
    p.w(o + 'application_layer/repo/order_repo.py', 'def order_repo() -> int:', '    return 1')  # ST7 · ST4(개념 폴더)
    p.w(o + 'domain_layer/coupon/coupon.py', 'from dataclasses import dataclass', '', '',        # ST4 애그리거트 골격 미비
        '@dataclass(frozen=True, slots=True, kw_only=True)', 'class Coupon:', '    code: str')
    p.markers()


def small_change(p, message='lane: small unrelated change'):
    p.sub(VM, 'count=0', 'count=1')
    return p.commit(message)


def g_legacy(s):
    p = s.std()
    legacy_tree(p)
    base = p.commit('base: legacy tree')
    small_change(p)
    s.backstop('게이트', '--diff-base', base)
    s.backstop('슬라이스 끝', '--diff-base', base, '--slice-end')


def g_declared(s):
    p = s.std()
    fx.mkbc(p, 'application/lobby', shell=fx.GUEST_SHELL)
    fx.own_root(p, 'guest')
    p.declare(fx.PRODUCTS)
    base = p.commit('base: declared')
    s.backstop('게이트', '--diff-base', base)


def g_rest(s):
    p = s.std()
    p.w('web/application/order/domain_layer/order/helpers/order_calc.py', 'def order_calc() -> int:', '    return 1')  # ST5
    p.w('web/static/vendor/unknown_sdk/unknown.js', 'var unknown = 1;')                                                  # ST12 vendor
    p.markers()
    shutil.rmtree(p.root / 'web/root/initializer')       # ST4 root 단위 골격 미비(기준점부터)
    shutil.rmtree(p.root / 'web/design_system/util')     # ST4 design_system 단위 골격 미비(기준점부터)
    base = p.commit('base')
    small_change(p)
    s.backstop('게이트', '--diff-base', base)


def persistent(p):
    p.w('web/static/js/root_shell.js', 'document.addEventListener("htmx:load", () => {});')
    p.w('web/static/root/' + Path(SHELL).stem + '.css', '.root-tab-bar { display: flex; }')
    p.w('web/' + SHELL, sh.shell_text(SHELL, sh.paths_for(p, SHELL)))


def g_core_tag(s):
    """문서 이동 셸 + 옛 자리 htmx core(기준점부터) — 레인이 그 script 줄에 속성 하나를 더한다(PU2)."""
    p = s.std()
    p.commit('std')
    p.mv('web/static/htmx/htmx.min.js', 'web/static/js/htmx.min.js')
    p.sub('web/' + SHELL, "web/htmx/htmx.min.js' %}\" defer>", "web/js/htmx.min.js' %}\" defer>")
    base = p.commit('base: legacy core')
    p.sub('web/' + SHELL, "web/js/htmx.min.js' %}\" defer>", "web/js/htmx.min.js' %}\" defer data-core=\"1\">")
    p.commit('lane: edit tag line')
    s.backstop('슬라이스 끝', '--diff-base', base, '--slice-end')


def g_shell_core(s):
    """지속 셸 + 옛 자리 htmx core(기준점부터) — 레인이 셸에 빈 줄 하나(SH4)."""
    p = s.std()
    persistent(p)
    p.commit('persistent shell')
    p.mv('web/static/htmx/htmx.min.js', 'web/static/js/htmx.js')
    p.sub('web/' + SHELL, 'web/htmx/htmx.min.js', 'web/js/htmx.js')
    base = p.commit('base: legacy core')
    p.append('web/' + SHELL, '')
    p.commit('lane: touch shell')
    s.backstop('슬라이스 끝', '--diff-base', base, '--slice-end')


def g_shell_css(s):
    """지속 셸 — 레인이 공유 머리가 싣는 CSS 를 지운다(셸 파일은 그대로) — SH4 는 서야 한다."""
    p = s.std()
    persistent(p)
    base = p.commit('base: persistent shell')
    p.rm('web/static/application/order/order_list_view.css')
    p.commit('lane: delete css')
    s.backstop('게이트', '--diff-base', base, '--only', 'sh4')


def g_registry(s):
    """선언 있는 프로젝트 — 레인이 선언 파일을 지운다 → «제품 선언이 기준점 뒤 바뀌었다» 알림."""
    p = s.std()
    fx.mkbc(p, 'application/lobby', shell=fx.GUEST_SHELL)
    fx.own_root(p, 'guest')
    p.declare(fx.PRODUCTS)
    base = p.commit('base: declared')
    p.rm(fx.REGISTRY)
    p.commit('lane: delete registry')
    s.backstop('게이트', '--diff-base', base, '--only', 'st0')


def g_registry_shell(s):
    """선언 + 지속 셸 — 레인이 선언 파일을 지워 다른 제품이던 파일이 지속 셸 제품으로 들어온다 — SH3 는 서야 한다."""
    p = s.std()
    fx.mkbc(p, 'application/lobby', shell=fx.GUEST_SHELL)
    fx.own_root(p, 'guest')
    p.declare(fx.PRODUCTS)
    persistent(p)
    p.append('web/' + fx.ORDER_PAGE, '{% block scripts %}{% endblock %}')
    base = p.commit('base: declared + persistent shell')
    p.rm(fx.REGISTRY)
    p.commit('lane: delete registry')
    s.backstop('게이트', '--diff-base', base, '--only', 'sh')


def g_new_bc(s):
    """대조 — 레인이 정말로 새 BC 를 골격 없이 들인다(두 꼴 모두 붉어야 한다 · 고치기 전 판도 같다)."""
    p = s.std()
    base = p.commit('base')
    p.w('web/application/coupon/presentation_layer/view/coupon_view.py', 'def coupon_view() -> int:', '    return 1')
    p.markers()
    p.commit('lane: new bc without skeleton')
    s.backstop('게이트', '--diff-base', base, '--only', 'st4,tg1')


def g_inflow(s):
    """기준점의 옛 폴더(web/templates) + 상류가 새 위반 폴더(web/common/extra)를 들이고 레인이 승인 병합으로 받는다."""
    p = s.std()
    p.w('web/templates/legacy_page.html', '<p>legacy</p>')
    p.markers()
    base = p.commit('base')
    fx.git(p.root, 'checkout', '-qb', 'lane')
    small_change(p, 'lane: small change')
    folder = p.root / '.dddjango-web' / 'build'
    folder.mkdir(parents=True)
    (folder / 'build-state.json').write_text(json.dumps({'git_snapshot': base, 'slices': []}), encoding='utf-8')
    fx.git(p.root, 'checkout', '-q', 'main')
    p.w('web/common/extra/extra_tool.py', 'def extra_tool() -> int:', '    return 1')
    p.markers()
    p.commit('main: upstream adds a folder')
    fx.git(p.root, 'checkout', '-q', 'lane')
    fx.git(p.root, 'merge', '--no-ff', '-q', '-m', 'receive-main', 'main')
    (folder / 'approved-merges.txt').write_text(fx.git(p.root, 'rev-parse', 'HEAD') + ' main\n', encoding='utf-8')
    s.backstop('게이트', '--diff-base', base, '--design-build', folder)


def g_relative_config(s):
    """사용자 git 설정 diff.relative=true — 레인이 기존 파일에 상대 import 줄(IM24)을, 새 최상위 폴더(ST0)를 더한다."""
    p = s.std()
    base = p.commit('base')
    fx.git(p.root, 'config', 'diff.relative', 'true')
    p.append(VM, 'from ..state import order_list_state  # lane')
    p.w('web/templates/new_page.html', '<p>new</p>')
    p.commit('lane: relative import line + new top-level folder')
    s.backstop('게이트', '--diff-base', base)
    s.code('벤더 검사의 diff 경로', VENDOR_DIFF, p.root, base)


def g_folder_space(s):
    """프로젝트 폴더 이름이 공백으로 시작하는 하위 폴더 프로젝트 — git 이 낸 접두의 앞 공백을 깎지 않는다: 기준점의 옛 폴더는
    «있던 폴더»(ST0), 기준점부터 빠져 있던 부품 CSS 는 «기존 누락»(CS1 — 문서를 git 개명으로 옮겨도), 기준점의 링크가 가리키는
    파일을 바꾸면 새 누락(CS1), 슬라이스 커밋의 벤더 파일 변경은 WV10 이다."""
    s.adopt(s.top, ' srv')
    p = s.std()
    p.w('web/' + SHELL, '{% load static %}<html><head>', '{% block head %}{% endblock %}',
        '</head><body>{% block content %}{% endblock %}</body></html>')
    cs.component(p)
    cs.page(p)  # 부품을 쓰지만 그 CSS 를 싣지 않는다(기준점부터)
    p.w('web/templates/legacy_page.html', '<p>legacy</p>')
    p.markers()
    base = p.commit('base')
    p.append('web/' + fx.ORDER_PAGE, '{# 다른 줄 #}')
    p.w('web/static/vendor/some_sdk/some.js', 'var some = 1;')
    slice_commit = p.commit('slice 1: page line + vendor file')
    folder = s.box / 'build'  # 저장소 밖
    folder.mkdir()
    (folder / 'build-state.json').write_text(json.dumps(
        {'git_snapshot': base, 'slices': [{'name': 'slice-1', 'commit': slice_commit}]}), encoding='utf-8')
    s.backstop('옛 폴더', '--diff-base', base, '--only', 'st0')
    s.backstop('CS1 기존 누락', '--diff-base', base, '--only', 'cs')
    s.backstop('WV10', '--diff-base', base, '--design-build', folder, '--only', 'wv10')
    name, code, out = s.runs[-1]  # WV10 의 위반 글은 저장소 기준 경로를 보인다(표시 글 — 판정과 무관) — 접두만 가린다
    s.runs[-1] = (name, code, out.replace(s.prefix() + 'web/static/', 'web/static/'))
    p.reset(base)
    p.mv('web/' + fx.ORDER_PAGE, 'web/' + fx.ORDER_PAGE.replace('order_list_view', 'order_moved_view'))
    s.backstop('CS1 이동', '--diff-base', base, '--only', 'cs')
    p.reset(base)
    p.w('web/root/scaffold/view/shared_head.html', cs.link())
    (p.root / 'web/root/scaffold/view/root_head.html').symlink_to('shared_head.html')
    p.sub('web/' + SHELL, '<head>', '<head>' + cs.include('root/scaffold/view/root_head.html'))
    loaded = p.commit('css loaded through a linked head')
    p.w('web/root/scaffold/view/shared_head.html', '<meta name="changed">')
    s.backstop('CS1 링크 대상 변경', '--diff-base', loaded, '--only', 'cs')


# ====================================================================== T — 바뀐 시험(TG2 · TG3)

def t_existing_test(s):
    """레인이 기준점부터 있던 시험 파일에 머신 고정 절대 경로를 읽는 줄을 더한다 — TG2 는 서야 한다."""
    p = s.std()
    base = p.commit('base')
    p.append(ORDER_TEST, '', '', 'def test_reads_outside() -> None:', '    assert open("/private/tmp/outside.txt").read()')
    p.commit('lane: existing test reads an absolute path')
    s.backstop('게이트', '--diff-base', base, '--only', 'tg')


def received_proj(s):
    """상류가 들인 시험(머신 고정 경로 줄 — TG2)을 레인이 승인 병합으로 받은 프로젝트 → (Proj, 기준 커밋, 산출물 폴더)."""
    p = s.std()
    base = p.commit('base')
    fx.git(p.root, 'checkout', '-qb', 'lane')
    small_change(p, 'lane: small change')
    folder = p.root / '.dddjango-web' / 'build'
    folder.mkdir(parents=True)
    (folder / 'build-state.json').write_text(json.dumps({'git_snapshot': base, 'slices': []}), encoding='utf-8')
    fx.git(p.root, 'checkout', '-q', 'main')
    p.w(UPSTREAM_TEST, 'def test_upstream() -> None:', '    assert open("/private/tmp/outside.txt").read()')
    fx.git(p.root, 'add', 'web_test')
    fx.git(p.root, 'commit', '-qm', 'main: upstream adds a test')
    fx.git(p.root, 'checkout', '-q', 'lane')
    fx.git(p.root, 'merge', '--no-ff', '-q', '-m', 'receive-main', 'main')
    (folder / 'approved-merges.txt').write_text(fx.git(p.root, 'rev-parse', 'HEAD') + ' main\n', encoding='utf-8')
    return p, base, folder


def t_received_link(s):
    """승인 병합이 상류판 그대로 들인 시험의 TG2 는 이 레인 몫이 아니다(수신 증명) — 레인이 더한 프로젝트 안 심볼릭 링크는 그
    증명을 막지 않는다(링크가 프로젝트 밖으로 풀리는지는 넘겨받은 루트 글자가 아니라 실제 자리로 본다)."""
    p, base, folder = received_proj(s)
    p.w('web_test/fixtures/a.json', '{}')
    os.symlink('fixtures', p.root / 'web_test/data')
    fx.git(p.root, 'add', 'web_test')
    fx.git(p.root, 'commit', '-qm', 'lane: link inside the project')
    s.backstop('게이트', '--diff-base', base, '--design-build', folder, '--only', 'tg2,tg3')


def t_received_link_space(s):
    """T2 를 공백으로 시작하는 프로젝트 폴더 이름으로 — 승인 유입 가르기도 접두의 앞 공백을 깎지 않는다."""
    s.adopt(s.top, ' srv')
    t_received_link(s)


def t_lane_link_outside(s):
    """레인이 프로젝트 밖 폴더를 가리키는 링크를 커밋하면(하위 폴더 꼴은 저장소 뿌리의 폴더 — 저장소 안 · 프로젝트 밖, 맨 위
    꼴은 저장소 밖 폴더) 승인 병합이 들인 시험의 수신 증명이 서지 않는다 — «레인이 손댄 심볼릭 링크» 로 이 레인 몫이다."""
    p, base, folder = received_proj(s)
    os.symlink(s.outside(), p.root / 'web_test/data')
    fx.git(p.root, 'add', 'web_test')
    fx.git(p.root, 'commit', '-qm', 'lane: link outside the project')
    s.backstop('게이트', '--diff-base', base, '--design-build', folder, '--only', 'tg2,tg3')


def t_repo_space(s):
    """T2 를 공백으로 끝나는 저장소 폴더 이름(`<자리>/repo `)으로 — 승인 유입 가르기가 저장소 최상위 경로의 끝을 깎지 않는다."""
    s.adopt(s.box / 'repo ')
    t_received_link(s)


def t_repo_newline(s):
    """T2 를 줄바꿈으로 끝나는 저장소 폴더 이름으로 — 최상위 경로 출력에서 끝 줄바꿈 하나만 뗀다."""
    s.adopt(s.box / 'repo\n')
    t_received_link(s)


# ====================================================================== S — 치환 확인(--subst-check)

def price_tool(p):
    p.w('web/legacy/price_tool.py', 'def price_of(count: int) -> int:', '    return count * 2')
    p.w('web_test/legacy/price_tool_test.py', 'from web.legacy.price_tool import price_of', '', '',
        'def test_price() -> None:', '    assert price_of(2) == 4')
    p.markers()


def s_move(s):
    """슬라이스 0 이 web/ 안 파일을 옮기고 web/ 밖 시험의 import 를 그에 맞춰 치환한다."""
    p = s.std()
    price_tool(p)
    base = p.commit('base')
    p.mv('web/legacy/price_tool.py', 'web/common/util/price_tool.py')
    p.sub('web_test/legacy/price_tool_test.py', 'web.legacy.price_tool', 'web.common.util.price_tool')
    head = p.commit('slice 0: move + test substitution')
    s.backstop('치환 확인', '--subst-check', base, head)


def s_mirror(s):
    """SUT 와 함께 web_test/ 미러 시험도 옮긴다(옛 경로 판 → 새 경로 판을 한 구간으로 대조)."""
    p = s.std()
    price_tool(p)
    base = p.commit('base')
    p.mv('web/legacy/price_tool.py', 'web/common/util/price_tool.py')
    p.mv('web_test/legacy/price_tool_test.py', 'web_test/common/util/price_tool_test.py')
    p.sub('web_test/common/util/price_tool_test.py', 'web.legacy.price_tool', 'web.common.util.price_tool')
    head = p.commit('slice 0: move sut + mirror test')
    s.backstop('치환 확인', '--subst-check', base, head)


def s_outside(s):
    """슬라이스 0 이 web/ 밖 비테스트 파일 · 문서(docs/ · 루트 .md)도 바꾼다 — 문서는 빼고, 비테스트는 --except 로만 뺀다."""
    p = s.std()
    price_tool(p)
    p.w('docs/guide.md', '# guide')
    p.w('NOTES.md', 'notes')
    base = p.commit('base')
    p.mv('web/legacy/price_tool.py', 'web/common/util/price_tool.py')
    p.sub('web_test/legacy/price_tool_test.py', 'web.legacy.price_tool', 'web.common.util.price_tool')
    p.append('config/settings.py', "LANGUAGE_CODE = 'ko'")
    p.append('docs/guide.md', 'moved price_tool')
    p.append('NOTES.md', 'moved price_tool')
    head = p.commit('slice 0: move + settings + docs')
    s.backstop('제외 없음', '--subst-check', base, head)
    s.backstop('--except', '--subst-check', base, head, '--except', 'config/settings.py')


def s_except_forms(s):
    """정규형이 아닌 `--except` 글자(`a//b` · `x/../a`) — 2.5.0 처럼 «트리에 있는 파일 경로만 받는다» 로 거절한다(맨 위 무변)."""
    p = s.std()
    price_tool(p)
    base = p.commit('base')
    p.mv('web/legacy/price_tool.py', 'web/common/util/price_tool.py')
    p.sub('web_test/legacy/price_tool_test.py', 'web.legacy.price_tool', 'web.common.util.price_tool')
    p.append('config/settings.py', "LANGUAGE_CODE = 'ko'")
    head = p.commit('slice 0: move + settings')
    s.backstop('겹 빗금', '--subst-check', base, head, '--except', 'config//settings.py')
    s.backstop('x/../', '--subst-check', base, head, '--except', 'x/../config/settings.py')


def s_except_outside(s):
    """프로젝트 밖으로 나가는 `--except` 글자(`../a` · `./` 뒤의 `../a`) — 하위 폴더에서도 저장소 뿌리 파일(README.md — 미끼)에
    닿지 않고 맨 위(저장소 밖 → 없음)처럼 거절한다."""
    p = s.std()
    price_tool(p)
    base = p.commit('base')
    p.mv('web/legacy/price_tool.py', 'web/common/util/price_tool.py')
    p.sub('web_test/legacy/price_tool_test.py', 'web.legacy.price_tool', 'web.common.util.price_tool')
    head = p.commit('slice 0: move')
    s.backstop('../', '--subst-check', base, head, '--except', '../README.md')
    s.backstop('./../', '--subst-check', base, head, '--except', '././../README.md')


class SubProj(sx.Proj):
    """fixtures_patch231_subst 의 Proj 를 하위 폴더 꼴로 — 프로젝트 루트 `<자리>/server` · 저장소 뿌리 `<자리>`."""

    def __init__(self, top):
        self.root = Path(top) / 'server'
        self.root.mkdir(parents=True, exist_ok=True)
        sx.git(top, 'init', '-q')


def subst_proj(s, build):
    """fixtures_patch231_subst 의 장면 만들기 build(tmp) → (Proj, 기준 커밋)을 이 꼴로 돈다."""
    with patch.object(sx, 'Proj', sx.Proj if s.layout == 'top' else SubProj):
        p, base = build(s.box)
    s.adopt(p.root if s.layout == 'top' else p.root.parent)
    s.bait()
    return p, base


def spec_file(s, *rows):
    path = s.box / 'design-spec.md'  # 저장소 밖
    path.write_text('# 명세\n\n\n## 슬라이스 0\n\n%s\n' % '\n'.join(rows), encoding='utf-8')
    return path


def s_method_move(s):
    """명세의 `메서드 이동:` 승인 행 — 제품 쪽 def 를 git blob 으로 읽어 확인하고 시험의 수신자 바꿈을 받는다."""
    p, base = subst_proj(s, sx.mk_move)
    sx.move_product(p)
    sx.move_tests(p)
    moved = p.commit('move')
    s.backstop('치환 확인', '--subst-check', base, moved, '--names', spec_file(s, sx.row(sx.REDIRECT, sx.DOC)))


def s_switch(s):
    """시험 전환 0T(검증됨) + 0C — build-state 의 test_switch 기록과 명세 `시험 전환:` 행의 시험 파일 경로를 맞댄다."""
    p, base = subst_proj(s, sx.mk_switch)
    spec = spec_file(s, sx.SWITCH_ROW)
    p.w(sx.GATE_PATH, sx.GATE % sx.GATE_NEW)
    t = p.commit('0T')
    p.w('web/intake/user_info_view.py', sx.UI_VIEW_INLINED)
    c = p.commit('0C')
    folder = s.box / 'build'  # 저장소 밖
    (folder / 'test-switch').mkdir(parents=True)
    (folder / 'test-switch' / 'evidence.json').write_text('{}\n', encoding='utf-8')
    slices = [{'name': 'slice-0-debt', 'commits': [t, c], 'test_switch': sx.ts('verified', [t])}]
    (folder / 'build-state.json').write_text(json.dumps({'mode': 'modify', 'slices': slices}), encoding='utf-8')
    s.backstop('치환 확인', '--subst-check', base, c, '--build', folder, '--names', spec)


# ====================================================================== D — 빚 잔존(--debt-residual)

def debt_proj(s, beta='beta.py'):
    """fixtures_patch231_debt 의 재현 장면(옛 배치 파일 셋 + G0 동결본 — C2 = legacy/<beta>) → (기준 커밋, 산출물 폴더)."""
    root = s.bare()
    for rel, body in fd.REPRO_WEB.items():
        fd.write(root / 'web' / rel.replace('beta.py', beta), body)
    anchor = fd.commit(root)
    folder = root / '.dddjango-web/run'
    folder.mkdir(parents=True)
    frozen = json.loads(fd.REPRO_G0.replace('legacy/beta.py', 'legacy/' + beta))
    frozen.update(head=anchor, scanned_at='2026-10-10T20:07:43+09:00')
    fd.write(folder / 'debt-g0.json', json.dumps(frozen))
    return anchor, folder


def d_moved(s):
    """레인이 미룬 키(ⓑ)의 파일을 git mv 로 옮긴다 → «ⓑ 이동 묶음 의존» 으로 멈춰야 한다."""
    _anchor, folder = debt_proj(s)
    fd.write(folder / 'refactor-scope.md', fd.section(body=fd.decision('C2') + 'ⓑ 키: C2\n'))
    s.backstop('옮기기 전', '--debt-residual', folder, clock=True)
    (s.root / 'web/moved').mkdir()
    fd.git(s.root, 'mv', 'web/legacy/beta.py', 'web/moved/beta.py')
    s.backstop('옮긴 뒤', '--debt-residual', folder, clock=True)


def upstream_move(s, anchor, folder, beta='beta.py'):
    """상류(upstream 가지)가 legacy/<beta> 를 옮기고 레인이 그 병합을 받는다 → 병합 커밋."""
    root = s.root
    fd.write(folder / 'build-state.json', json.dumps({'git_snapshot': anchor}))
    lane = fd.git(root, 'symbolic-ref', '--short', 'HEAD')
    fd.git(root, 'checkout', '-q', '-b', 'upstream', anchor)
    (root / 'web/moved').mkdir()
    fd.git(root, 'mv', 'web/legacy/' + beta, 'web/moved/' + beta)
    fd.commit(root)
    fd.git(root, 'checkout', '-q', lane)
    fd.write(root / 'web/legacy/alpha.py', 'def a() -> int:\n    return 10\n')
    fd.commit(root)
    fd.git(root, '-c', 'user.name=t', '-c', 'user.email=t@t', 'merge', '-q', '--no-ff', '-m', 'main', 'upstream')
    return fd.git(root, 'rev-parse', 'HEAD')


def d_inflow_move(s):
    """승인 병합이 상류판 그대로 들인 이동은 이 실행의 이동이 아니다 — 승인 전에는 멈추고, 승인 뒤에는 알림과 함께 지난다."""
    anchor, folder = debt_proj(s)
    fd.write(folder / 'refactor-scope.md', fd.section(body=fd.decision('C2') + 'ⓑ 키: C2\n'))
    merge = upstream_move(s, anchor, folder)
    s.backstop('승인 전', '--debt-residual', folder, clock=True)
    fd.write(folder / 'approved-merges.txt', merge + ' main 받기\n')
    s.backstop('승인 뒤', '--debt-residual', folder, clock=True)


def d_moved_korean(s):
    """D1 을 한글 이름 파일로 — git 기본 설정(core.quotePath=true)이 따옴표로 감싸 내는 개명도 이동으로 본다."""
    _anchor, folder = debt_proj(s, KOREAN)
    fd.write(folder / 'refactor-scope.md', fd.section(body=fd.decision('C2') + 'ⓑ 키: C2\n'))
    (s.root / 'web/moved').mkdir()
    fd.git(s.root, 'mv', 'web/legacy/' + KOREAN, 'web/moved/' + KOREAN)
    s.backstop('옮긴 뒤', '--debt-residual', folder, clock=True)


def d_inflow_move_korean(s):
    """D2 를 한글 이름 파일로 — 승인 병합이 상류판 그대로 들인 한글 이름 개명도 «승인 병합이 들인 이동» 이다."""
    anchor, folder = debt_proj(s, KOREAN)
    fd.write(folder / 'refactor-scope.md', fd.section(body=fd.decision('C2') + 'ⓑ 키: C2\n'))
    merge = upstream_move(s, anchor, folder, KOREAN)
    s.backstop('승인 전', '--debt-residual', folder, clock=True)
    fd.write(folder / 'approved-merges.txt', merge + ' main 받기\n')
    s.backstop('승인 뒤', '--debt-residual', folder, clock=True)


# ====================================================================== A — refactor_audit(residual · standing --gate)

def audit_proj(s, files):
    """리팩토링 실행의 자리 — 의미 항목 M<k> 의 원 행이 `web/<files[k-1]>:1` 인 audit 를 둔다 → (기준 커밋, 산출물 폴더)."""
    anchor, folder = debt_proj(s)
    data = json.loads((folder / 'debt-g0.json').read_text(encoding='utf-8'))
    data['mode'] = 'refactor'
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
    return anchor, folder


def a_residual(s):
    """리팩토링 잔존 판정 — 고친 의미 항목(M1 의 파일을 git 개명으로 옮김)은 «파일 무변 → 잔존» 이 아니라 리뷰어 확인
    대상이고, 리뷰 묶음의 «슬라이스 0 개명 쌍» 은 프로젝트 루트 기준 경로이며, 해소 근거 위치(새 자리)를 받는다."""
    _anchor, folder = audit_proj(s, ('legacy/alpha.py', 'legacy/beta.py'))
    (s.root / 'web/moved').mkdir()
    fd.git(s.root, 'mv', 'web/legacy/alpha.py', 'web/moved/alpha.py')
    fd.write(folder / 'refactor-scope.md',
             fd.section(meaning='M1', body=fd.decision('M2', '다른 요청') + '의미 ⓑ 다른 요청 키: M2\n'))
    s.tool('residual', 'refactor_audit.py', 'residual', folder, clock=True)
    stamps = sorted((folder / 'residual').iterdir()) if (folder / 'residual').is_dir() else []
    s.section('개명 쌍', stamps[0] / 'review-ui.md' if stamps else folder / '-', '## 슬라이스 0 개명 쌍(옛 경로 → 새 경로)')
    if stamps:
        fd.write(stamps[0] / 'result-ui.md', '| M1 | 해소 | web/moved/alpha.py:1 — 판단을 한 곳에 둠 |\n')
        s.tool('finalize', 'refactor_audit.py', 'residual', folder, '--finalize', stamps[0].name, clock=True)


ITEM_FILES = ('legacy/alpha.py', 'legacy/beta.py', 'other/gamma.py')
LINK_ROWS = ('| M1 | 해소 | web/fixed/out_file.py:1 — 프로젝트 밖 파일을 가리키는 링크 |\n'
             '| M2 | 해소 | web/fixed/out_dir/top_bait.py:1 — 프로젝트 밖 폴더를 가리키는 링크 아래 |\n'
             '| M3 | 해소 | web/fixed/alias.py:1 — 프로젝트 안 파일을 가리키는 링크 |\n')


def link_grounds(s):
    """해소 근거로 적힐 새 자리 — 프로젝트 밖 파일을 가리키는 파일 링크 · 프로젝트 밖 폴더를 가리키는 폴더 링크 · 프로젝트 안
    파일을 가리키는 링크 둘(상대 · 절대 — 대조). 원 항목 파일 셋도 고친다(«파일 무변 → 잔존» 이 아니라 리뷰어 확인 대상)."""
    out = s.outside()
    fixed = s.root / 'web/fixed'
    fd.write(fixed / 'real.py', 'def fixed() -> int:\n    return 0\n')
    fd.write(fixed / 'deep/deep.py', 'def deep() -> int:\n    return 0\n')  # 깊이가 다른 자리(조상 견줌이 한 단계에 묶이지 않는다)
    os.symlink(out / 'top_bait.py', fixed / 'out_file.py')
    os.symlink(out, fixed / 'out_dir')
    os.symlink('real.py', fixed / 'alias.py')
    os.symlink(fixed / 'real.py', fixed / 'alias_abs.py')
    for rel in ITEM_FILES:
        fd.write(s.root / 'web' / rel, 'def tidy() -> int:\n    return 0\n')


def a_link_ground(s):
    """해소 근거가 심볼릭 링크를 따라 프로젝트 밖 파일에 닿으면 근거가 아니다(«근거 판형 아님» — 그 행을 다시 받는다 · 밖
    파일을 읽어 «해소» 로 확정하지 않는다). 프로젝트 안을 가리키는 링크는 그대로 받는다. 리뷰어 행 위치(check)도 같은 함수다."""
    _anchor, folder = audit_proj(s, ITEM_FILES)
    link_grounds(s)
    fd.write(folder / 'refactor-scope.md', fd.section(meaning='M1 M2 M3'))
    s.tool('residual', 'refactor_audit.py', 'residual', folder, clock=True)
    stamps = sorted((folder / 'residual').iterdir()) if (folder / 'residual').is_dir() else []
    if stamps:
        fd.write(stamps[0] / 'result-ui.md', LINK_ROWS)
        s.tool('finalize', 'refactor_audit.py', 'residual', folder, '--finalize', stamps[0].name, clock=True)
    out = os.path.relpath(s.outside() / 'top_bait.py', s.root)  # 링크 없이 프로젝트 밖 파일(`../…`)
    for label, rel in (('밖 파일 링크', 'web/fixed/out_file.py'), ('밖 폴더 링크 아래', 'web/fixed/out_dir/top_bait.py'),
                       ('안쪽 링크', 'web/fixed/alias.py'), ('안쪽 절대 링크', 'web/fixed/alias_abs.py'),
                       ('일반 파일', 'web/fixed/real.py'), ('밖 파일(../)', out),
                       ('밖 파일(절대 경로)', str(s.outside() / 'top_bait.py')), ('밖 파일(./x/../../)', './web/../' + out),
                       ('깊이 다른 자리', 'web/fixed/deep/deep.py'), ('NUL 글자', 'web/legacy/al<NUL>pha.py')):
        s.code('위치 · ' + label, LOCATION, s.root, rel)


def a_link_carry(s):
    """앞 판이 밖 링크를 따라 읽어 확정한 해소 지문(M1)은 이월하지 않는다 — 그 항목은 다시 리뷰어 확인 대상이다.
    프로젝트 안 파일의 지문(M3 — 안쪽 링크 포함)은 그대로 이월한다(대조)."""
    anchor, folder = audit_proj(s, ITEM_FILES)
    link_grounds(s)
    fd.write(folder / 'refactor-scope.md',
             fd.section(meaning='M1 M3', body=fd.decision('M2', '다른 요청') + '의미 ⓑ 다른 요청 키: M2\n'))
    web = s.root / 'web'
    solved = {m: {'web/' + rel: hashlib.sha256((web / rel).read_bytes()).hexdigest()[:16] for rel in rels}
              for m, rels in (('M1', ('legacy/alpha.py', 'fixed/out_file.py')), ('M3', ('other/gamma.py', 'fixed/alias.py')))}
    solved['M3']['web/fixed'] = None  # 앞 판 지문의 «파일 아님»(폴더) — 지금도 폴더면 같다(읽지 않는다)
    fd.write(folder / 'residual/20261010-2100/result.json', json.dumps(
        {'stamp': '20261010-2100', 'audit': fd.AUDIT, 'snapshot': anchor, 'solved': solved}))
    s.tool('residual', 'refactor_audit.py', 'residual', folder, clock=True)


def a_link_root(s):
    """대조 — 프로젝트 루트를 그 루트를 가리키는 링크로 넘겨도 A4 와 같은 판정이다(루트 자체가 링크인 꼴은 프로젝트 안)."""
    s.link = s.box / 'root-link'
    os.symlink(s.root, s.link)
    a_link_ground(s)


RULES = 'skills/rules/references/final.md'


def a_separate_edit(s):
    """check-verdict — 별도 요청(동작 불변 정리 가능 = 아니오 — web/ 밖)의 «편집할 곳» 이 프로젝트 밖 파일이면(링크를 따라 ·
    `..` · 절대 경로) 편집할 곳이 없는 것으로 보고 채택으로 재분류한다(밖 파일을 읽지 않는다). 프로젝트 안 파일 · 안쪽 링크는
    별도 요청 그대로."""
    _anchor, folder = audit_proj(s, ('legacy/alpha.py',))
    audit = folder / 'audit' / fd.AUDIT
    plugin = s.box / 'plugin'
    fd.write(plugin / 'commands/dddjango-web.md', '# coordinator\n')
    fd.write(plugin / RULES, '# rules\n\n## §1. 규칙\n\n공용 헬퍼는 금지다.\n')
    fd.write(s.root / 'config/settings.py', "SECRET_KEY = 'x'\n")
    os.symlink('settings.py', s.root / 'config/in_link.py')
    fd.write(s.root.parent / 'outside.py', 'OUT = 1\n')  # 프로젝트 밖(하위 폴더 꼴은 저장소 뿌리 · 맨 위 꼴은 저장소 밖)
    os.symlink(s.root.parent / 'outside.py', s.root / 'config/out_link.py')
    for label, edit in (('안 파일', 'config/settings.py:1'), ('안쪽 링크', 'config/in_link.py:1'),
                        ('밖 파일(../)', '../outside.py:1'), ('밖 파일(절대 경로)', '%s:1' % (s.root.parent / 'outside.py')),
                        ('밖 파일(./x/../../)', './config/../../outside.py:1'), ('밖 파일 링크', 'config/out_link.py:1')):
        fd.write(audit / 'ui-01.md', '| 1 | %s §1 «공용 헬퍼는 금지다» | — | web/legacy/alpha.py:1 | 정리 | 아니오 — web/ 밖 | %s '
                 '| — |\n' % (RULES, edit))
        fd.write(audit / 'verdict.md', '| M1 | ui-01#1 | 별도 요청 | web/ 밖 — 설정 | web/legacy/alpha.py:1 |\n')
        (audit / 'verdict-log.md').unlink(missing_ok=True)
        s.tool(label, 'refactor_audit.py', '--platform', 'claude', '--plugin-root', plugin, 'check-verdict', audit)


def a_nul_ground(s):
    """해소 근거 위치에 NUL 이 든 글자 — 경로가 될 수 없으므로 «근거 판형 아님»(실행 불능이 아니다 · 2.5.0 과 같다)."""
    _anchor, folder = audit_proj(s, ('legacy/alpha.py',))
    fd.write(s.root / 'web/legacy/alpha.py', 'def tidy() -> int:\n    return 0\n')
    fd.write(folder / 'refactor-scope.md', fd.section(meaning='M1'))
    s.tool('residual', 'refactor_audit.py', 'residual', folder, clock=True)
    stamps = sorted((folder / 'residual').iterdir()) if (folder / 'residual').is_dir() else []
    if stamps:
        fd.write(stamps[0] / 'result-ui.md', '| M1 | 해소 | web/legacy/al\x00pha.py:1 — 판단을 한 곳에 둠 |\n')
        s.tool('finalize', 'refactor_audit.py', 'residual', folder, '--finalize', stamps[0].name, clock=True)


def a_plan_grep(s):
    """사용자 git 설정 grep.fullName=true — refactor_audit plan 의 참조 조회(경계 교차 소비자 · 참조 치환 줄 · --names 의 (나) 줄)는
    적중 경로를 프로젝트 루트 기준으로 읽는다(설정이 켜져 있으면 git grep 이 저장소 기준 경로를 낸다). SDK 도구가 보이는
    템플릿 참조 줄도 같은 기준이다(표시)."""
    p = s.std()
    p.w('web/application/order/helpers/order_helper.py', 'def order_help() -> int:', '    return 1')
    p.w('web/root/extra/uses_helper.py', 'from web.application.order.helpers.order_helper import order_help', '',
        'x: int = order_help()')
    p.w('web_test/application/order/helper_test.py', 'from web.application.order.helpers.order_helper import order_help', '', '',
        'def test_help() -> None:', '    assert order_help() == 1')
    p.markers()
    p.commit('base')
    fx.git(p.root, 'config', 'grep.fullName', 'true')
    folder = p.root / '.dddjango-web' / 'run'
    folder.mkdir(parents=True)
    unit = ('plan', 'web/application/order', '--debt', folder / 'debt-g0.json')
    s.backstop('빚 스캔', '--debt-scan', '--refactor', '--json', folder / 'debt-g0.json')
    s.tool('plan', 'refactor_audit.py', *unit, '--out', folder / 'audit')
    s.section('참조 치환 줄', folder / 'audit/plan.md', '## 참조 치환 줄')
    s.tool('plan --names', 'refactor_audit.py', *unit, '--out', folder / 'audit', '--names', spec_file(
        s, '- 경로: application/order/helpers/order_helper.py → application/order/application_layer/service/order_helper.py'))
    s.code('템플릿 참조 줄', TEMPLATE_REFS, p.root, 'web/htmx/htmx.min.js')


STANDING_M5 = 'tests/web/test_home.py:2'
STANDING_M7 = 'home/view/home_view.py:2-4 · tests/web/test_home.py:3'


def standing_scope(source, m5=STANDING_M5, m7=STANDING_M7):
    """상시 답 두 줄(M5 · M7)을 담은 refactor-scope.md — 막는 위치 글자만 바꿔 쓴다."""
    return ('## G0 2026-09-29 10:00\n\n'
            '- 결정 줄: M3 M5 M8 M9 · 결정 = ⓐ · 사유 = 빚은 먼저 정리 · 출처 = 대리 답 ⓐ /x/scope.md:50(2026-09-29 09:59)\n'
            '- 결정 줄: M7 · 결정 = ⓐ · 사유 = 사용자 판단 «위반 — 정리» · 출처 = 사용자 원문 /x/user-answers.md:10(2026-09-29 09:59)\n\n'
            '의미 audit: 20260929-100000\n의미 ⓐ 키: M3 M5 M7 M8 M9\nⓐ 키: -\n요구 키: -\n'
            '\n## ⓐ 재상정 2026-09-29 10:20\n\n- 상시 답 적용 2건\n'
            '- 결정 줄: M5 · 결정 = 별도 요청 · 사유 = 동작 불변 불가(테스트 본문 동반 — ' + m5 + ') · ' + source + '\n'
            '- M7 · 결정 = 별도 요청 · 사유 = 동작 불변 불가(외부 관찰 동작 · 테스트 새 판정 — ' + m7 + ') · ' + source + '\n'
            '\n재상정 키: -\n의미 재상정 키: M5 M7\n')


def standing_project(s):
    """상시 답 파일을 커밋한 프로젝트 → (산출물 폴더, 출처 칸 글자)."""
    root = s.bare()
    fd.write(root / 'web/home/view/home_view.py', 'a\nb\nc\nd\ne\n')
    fd.write(root / 'tests/web/test_home.py', 'x\ny\nz\n')
    if s.layout == 'sub':  # 저장소 뿌리의 같은 이름 파일(프로젝트 밖 미끼) — `../tests/…` 위치가 여기에 닿으면 안 된다
        fd.write(s.top / 'tests/web/test_home.py', ''.join('bait %d\n' % k for k in range(1, 10)))  # 9행 — 프로젝트 것은 3행
    s.commit_all('base')
    fd.write(root / '.dddjango/standing-answer.md',
             '# 상시 답\n\n«동작 변경이나 테스트 수정이 필요해 이번에 못 끝내는 항목은 별도 요청으로.»\n')
    answer = s.commit_all('standing')
    folder = root / '.dddjango-web/r'
    fd.write(folder / 'build-state.json', json.dumps({'git_snapshot': answer, 'mode': 'refactor'}))
    return folder, '출처 = 상시 답 .dddjango/standing-answer.md:3@' + answer[:12]


def a_standing(s):
    """상시 답 — 출처 커밋 판의 `.dddjango/standing-answer.md` 와 git_snapshot 판의 막는 위치(파일:행)를 읽는다."""
    folder, source = standing_project(s)
    fd.write(folder / 'refactor-scope.md', standing_scope(source))
    s.tool('standing', 'refactor_audit.py', 'standing')
    s.tool('standing --gate', 'refactor_audit.py', 'standing', folder, '--gate')


def a_standing_forms(s):
    """정규형이 아닌 · 프로젝트 밖으로 나가는 막는 위치 글자 — 맨 위(= 2.5.0)와 같게: `a/./b` · `x/../a` 는 ③ red(접어 읽지
    않는다) · `./a` 는 프로젝트 루트 기준으로 읽는다 · `../a` · `./../a` 는 하위 폴더에서도 저장소 뿌리의 같은 이름 파일에
    닿지 않고 ③ red. 정규형 위치의 9행은 저장소 뿌리의 같은 이름 파일(9행)에만 있다 — 프로젝트 파일(3행)로 읽어 ③ red."""
    folder, source = standing_project(s)
    for label, where in (('a/./b', 'tests/./web/test_home.py:2'), ('./a', './tests/web/test_home.py:2'),
                         ('../a', '../tests/web/test_home.py:2'), ('./../a', './../tests/web/test_home.py:2'),
                         ('x/../a', 'web/../tests/web/test_home.py:2'), ('뿌리에만 있는 줄', 'tests/web/test_home.py:9')):
        fd.write(folder / 'refactor-scope.md', standing_scope(source, m5=where))
        s.tool('--gate ' + label, 'refactor_audit.py', 'standing', folder, '--gate')


# ====================================================================== W — SDK(사용자 원문 자리)

def source_proj(s):
    """출처로 들 파일 넷(web 안 · 기록 안 · 문서 · 이름이 web 으로 시작하는 다른 폴더)을 커밋한 프로젝트 → (Proj, 커밋, 접두)."""
    p = s.std()
    p.w('web/common/util/note.py', '# 2026-10-13 note')
    p.w('.dddjango-web/build/note.md', '2026-10-13 build note')
    p.w('docs/request.md', '2026-10-13 request')
    p.w('webapp/notes.md', '2026-10-13 webapp note')  # 이름이 web 으로 시작하는 다른 폴더 — 금지 자리가 아니다
    return p, p.commit('base'), s.prefix()


def w_source(s):
    """SDK 승인 «사용자 원문» 출처 — 프로젝트의 web/ · .dddjango-web/ 안 파일은 출처가 아니다(경로는 저장소 상대로 적는다 ·
    `./` 로 시작하면 git 이 프로젝트 루트 기준으로 읽으므로 그 자리로 본다)."""
    p, head, prefix = source_proj(s)
    s.code('web 안', SOURCE_LINE, p.root, prefix + 'web/common/util/note.py', head)
    s.code('./web 안', SOURCE_LINE, p.root, './web/common/util/note.py', head)
    s.code('./기록 안', SOURCE_LINE, p.root, './.dddjango-web/build/note.md', head)
    s.code('web 폴더', SOURCE_LINE, p.root, prefix + 'web', head)                  # 폴더 자체 — git show 가 목록을 낸다
    s.code('./web 폴더', SOURCE_LINE, p.root, './web', head)
    s.code('기록 폴더', SOURCE_LINE, p.root, prefix + '.dddjango-web', head)
    s.code('./기록 폴더', SOURCE_LINE, p.root, './.dddjango-web', head)
    s.code('web 밖', SOURCE_LINE, p.root, prefix + 'docs/request.md', head)
    s.code('./web 밖', SOURCE_LINE, p.root, './docs/request.md', head)
    s.code('webapp 안', SOURCE_LINE, p.root, prefix + 'webapp/notes.md', head)
    s.code('docs 폴더', SOURCE_LINE, p.root, prefix + 'docs', head)
    # 접두 없이 쓴 `web/…` — 맨 위 꼴은 프로젝트의 web/, 하위 폴더 꼴은 저장소 뿌리의 다른 web/(미끼 파일이 커밋돼 있다) — 둘 다 거절
    s.code('접두 없는 web/', SOURCE_LINE, p.root, BAIT[1][0], head)


def w_folder_web(s):
    """프로젝트 폴더 이름이 `web` 인 하위 폴더 프로젝트 — 프로젝트 안 문서를 `./` 로 든 출처는 읽힌다(자리 금지는 프로젝트의
    web/ · .dddjango-web/ 에 걸리지 프로젝트 폴더 이름에 걸리지 않는다). 그 프로젝트의 web/ 안은 어느 철자로든 거절."""
    s.adopt(s.top, 'web')
    p, head, prefix = source_proj(s)
    s.code('./문서', SOURCE_LINE, p.root, './docs/request.md', head)
    s.code('./web 안', SOURCE_LINE, p.root, './web/common/util/note.py', head)
    s.code('web 안', SOURCE_LINE, p.root, prefix + 'web/common/util/note.py', head)


def sdk_proj(s, folder, unit='kakao_tmp'):
    """sdk_fixture 의 표준 프로젝트(하위 폴더 꼴이면 프로젝트 폴더 이름 folder · git 은 저장소 뿌리) + 등재할 SDK 와 같은 바이트의
    목록 이전 임시 사본(`web/static/vendor/<unit>/kakao.min.js`)을 커밋한다."""
    s.adopt(s.top, folder)
    made = s.box / 'sdkproj'
    tool = [sys.executable, '-B', str(TEST / 'sdk_fixture.py')]
    subprocess.run(tool + ['mkproj', str(made)], env=ENV, capture_output=True, check=True)
    shutil.rmtree(made / '.git')
    s.root.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(made), str(s.root))
    fd.git(s.top, 'init', '-q', '-b', 'main')
    s.bait()
    s.commit_all('base')
    (s.root / 'web/static/vendor' / unit).mkdir(parents=True)
    subprocess.run(tool + ['sdkjs', str(s.root / 'web/static/vendor' / unit / 'kakao.min.js')], env=ENV,
                   capture_output=True, check=True)
    s.commit_all('vendor copy before the registry')


def w_korean_install(s):
    """한글 이름 하위 폴더(`서버/`) — 목록 이전에 같은 자리에서 태어난 사본은 빚(WV12)이라 그 SDK 의 정식 등재가 선다(거짓
    WV13 으로 등재가 되돌려지지 않는다)."""
    sdk_proj(s, '서버')
    s.tool('install', 'test/sdk_fixture.py', 'install', s.root)
    s.backstop('게이트 · wv', '--diff-base', 'HEAD', '--only', 'wv')


def w_korean_unit(s):
    """W4 를 한글 이름 벤더 폴더(`web/static/vendor/카카오_tmp/`)로 — 같은 결함의 맨 위 갈래(벤더 경로를 따옴표 없이 읽는다)."""
    sdk_proj(s, 'server', '카카오_tmp')
    s.tool('install', 'test/sdk_fixture.py', 'install', s.root)


def w_korean_gate(s):
    """한글 이름 하위 폴더 — 등재된 상태(등재는 core.quotePath=false 로 해 둔다)의 게이트가 같은 자리 사본을 WV13 으로 막지 않는다."""
    sdk_proj(s, '서버')
    fd.git(s.top, 'config', 'core.quotepath', 'false')
    subprocess.run([sys.executable, '-B', str(s.scripts / 'test/sdk_fixture.py'), 'install', str(s.root)], env=ENV,
                   capture_output=True, check=True)
    fd.git(s.top, 'config', '--unset', 'core.quotepath')
    s.backstop('게이트 · wv', '--diff-base', 'HEAD', '--only', 'wv')


def w_log_root(s):
    """사용자 git 설정 log.showRoot=false — 목록과 벤더 파일을 함께 들인 첫 커밋도 «목록 시대» 로 본다(목록을 지운 뒤 남은
    미등재 벤더 내용은 늘 막는 WV13)."""
    root = s.bare()
    fd.write(root / 'web/sdk_registry.json', '{"schema":"dddjango-web-sdk-registry/1","sdks":{}}\n')
    fd.write(root / 'web/static/vendor/foo/foo.js', 'const foo = 1;\n')
    s.commit_all('registry era: first commit')
    (root / 'web/sdk_registry.json').unlink()
    s.commit_all('remove registry')
    fd.git(s.top, 'config', 'log.showRoot', 'false')
    s.backstop('--all · wv12 · wv13', '--all', '--only', 'wv12,wv13')


def w_folder_space(s):
    """프로젝트 폴더 이름이 공백으로 시작하는 하위 폴더 프로젝트 — 접두의 앞 공백을 깎지 않는다(그 폴더의 web/ 안은 거절)."""
    s.adopt(s.top, ' srv')
    p, head, prefix = source_proj(s)
    s.code('web 안', SOURCE_LINE, p.root, prefix + 'web/common/util/note.py', head)
    s.code('./web 안', SOURCE_LINE, p.root, './web/common/util/note.py', head)
    s.code('web 밖', SOURCE_LINE, p.root, prefix + 'docs/request.md', head)


# (장면 이름, 장면, 고치기 전 판이 하위 폴더에서 틀렸는가, 맨 위 꼴 = [(실행 이름, exit, 있어야 할 글자들, 없어야 할 글자들)])
SCENES = (
    ('G1 옛 폴더가 있는 프로젝트 + 상관없는 한 줄', g_legacy, True,
     [('게이트', 0, ['blocker 0건'], ['BLOCKER']), ('슬라이스 끝', 0, ['blocker 0건'], ['BLOCKER'])]),
    ('G2 선언 있는 프로젝트 · 레인 변경 0', g_declared, True, [('게이트', 0, ['blocker 0건'], ['BLOCKER'])]),
    ('G3 옛 폴더 나머지 갈래(ST5 · ST12 vendor · ST4 root · design_system)', g_rest, True,
     [('게이트', 0, ['blocker 0건'], ['BLOCKER'])]),
    ('G4 옛 자리 htmx core 줄 고침(PU2)', g_core_tag, True, [('슬라이스 끝', 0, ['blocker 0건'], ['BLOCKER'])]),
    ('G5 지속 셸 + 옛 자리 htmx core(SH4)', g_shell_core, True, [('슬라이스 끝', 0, ['blocker 0건'], ['BLOCKER'])]),
    ('G6 지속 셸 · 공유 머리 CSS 삭제 — SH4 는 선다', g_shell_css, True,
     [('게이트', 2, ['[SH4] BLOCKER', '공유 머리 자산 파일 없음'], [])]),
    ('G7 선언 파일 삭제 — 알림 줄', g_registry, True, [('게이트', 0, ['[info] 제품 선언이 기준점 뒤 바뀌었다'], [])]),
    ('G8 선언 삭제 + 지속 셸 — SH3 는 선다', g_registry_shell, True, [('게이트', 2, ['[SH3] BLOCKER'], [])]),
    ('G9 대조: 정말 새 BC(골격 · 시험 없음)', g_new_bc, False, [('게이트', 2, ['[ST4] BLOCKER', '[TG1] BLOCKER'], [])]),
    ('G10 승인 병합 유입 + 기준점의 옛 폴더', g_inflow, True,
     [('게이트', 2, ['[ST11] BLOCKER — web/common/extra'], ['[ST0] BLOCKER'])]),
    ('G11 git 설정 diff.relative=true', g_relative_config, True,
     [('게이트', 2, ['[IM24] BLOCKER', '[ST0] BLOCKER — web/templates'], []),
      ('벤더 검사의 diff 경로', 0, [VM, 'web/templates/new_page.html'], ['??'])]),
    ('G12 프로젝트 폴더 이름이 공백으로 시작 — 옛 폴더 · CS1 · WV10', g_folder_space, True,
     [('옛 폴더', 0, ['blocker 0건'], ['BLOCKER']),
      ('CS1 기존 누락', 0, ['CS1 기존 누락', 'blocker 0건'], ['BLOCKER']),
      ('WV10', 2, ['[WV10] BLOCKER', '가 목록·벤더를 바꾼다'], []),
      ('CS1 이동', 0, ['CS1 기존 누락', 'blocker 0건'], ['BLOCKER']),
      ('CS1 링크 대상 변경', 2, ['[CS1] BLOCKER'], ['CS1 기존 누락'])]),
    ('T1 기존 시험에 머신 고정 경로 줄 — TG2 는 선다', t_existing_test, True,
     [('게이트', 2, ['[TG2] BLOCKER — ' + ORDER_TEST], ['TG2·TG3 미실행'])]),
    # T2 · T3 — 고정 판도 두 꼴이 같았다(새 시험 파일의 수신 증명은 하위 폴더에서도 섰다). 맨 위에서 루트 철자에 걸렸다(CASE_RED)
    ('T2 승인 병합이 들인 시험의 TG2 수신 증명 — 레인이 더한 프로젝트 안 링크는 막지 않는다', t_received_link, False,
     [('게이트', 0, ['[TG2] BLOCKER — ' + UPSTREAM_TEST, '수신 증명', 'blocker 0건 · 승인 유입 1건(종료 코드 제외)'],
       ['이 레인 몫으로 남김'])]),
    ('T3 T2 를 공백으로 시작하는 프로젝트 폴더 이름으로', t_received_link_space, False,
     [('게이트', 0, ['[TG2] BLOCKER — ' + UPSTREAM_TEST, '수신 증명', 'blocker 0건 · 승인 유입 1건(종료 코드 제외)'],
       ['이 레인 몫으로 남김'])]),
    # T4 — 대조: 고정 판도 두 꼴이 같았다(링크 조사의 «프로젝트 자리» 를 접두로 잡는 고침 ③ 을 못 박는다)
    ('T4 레인이 프로젝트 밖 폴더로 링크 — 승인 유입의 수신 증명이 서지 않는다', t_lane_link_outside, False,
     [('게이트', 2, ['[TG2] BLOCKER — ' + UPSTREAM_TEST, '이 레인 몫으로 남김: 유입 증명 실패(레인이 손댄 심볼릭 링크)'],
       ['수신 증명'])]),
    (T5, t_repo_space, False,  # 고정 판은 두 꼴 모두 가르기를 건너뛰었다(맨 위에서 틀린 갈래 · TOP_CHANGED)
     [('게이트', 0, ['[TG2] BLOCKER — ' + UPSTREAM_TEST, '수신 증명', 'blocker 0건 · 승인 유입 1건(종료 코드 제외)'],
       ['이 레인 몫으로 남김'])]),
    (T6, t_repo_newline, False,
     [('게이트', 0, ['[TG2] BLOCKER — ' + UPSTREAM_TEST, '수신 증명', 'blocker 0건 · 승인 유입 1건(종료 코드 제외)'],
       ['이 레인 몫으로 남김'])]),
    ('S1 옮기기 + 시험 import 치환', s_move, True, [('치환 확인', 0, ['치환 확인 — web/ 밖 변경 파일 1 · 쌍 2'], ['[subst]'])]),
    ('S2 미러 시험도 함께 옮김', s_mirror, True, [('치환 확인', 0, ['치환 확인 — web/ 밖 변경 파일 1'], ['[subst]'])]),
    ('S3 web/ 밖 비테스트 · 문서 · --except', s_outside, True,
     [('제외 없음', 2, ['[subst] config/settings.py 테스트 밖 web/ 밖 파일 변경(M)', '문서 제외(docs/ · .dddjango/ · 루트 .md) 2',
                     '어긋남 1 ·'], []),
      ('--except', 0, ['제외 1 — config/settings.py'], ['[subst]'])]),
    ('S4 메서드 이동 승인 행', s_method_move, True, [('치환 확인', 0, ['치환 확인 — web/ 밖 변경 파일 2'], ['[subst]', '실행 불능'])]),
    ('S5 시험 전환 0T(검증됨) + 0C', s_switch, True, [('치환 확인', 0, ['치환 확인 — web/ 밖 변경 파일 1'], ['[subst]', '실행 불능'])]),
    ('S6 대조: 정규형이 아닌 --except 글자는 2.5.0 처럼 거절', s_except_forms, False,
     [('겹 빗금', 1, ['--except 는 기준·대상 트리에 있는 파일 경로만 받는다(폴더·글롭 불가) — config//settings.py'], []),
      ('x/../', 1, ['--except 는 기준·대상 트리에 있는 파일 경로만 받는다(폴더·글롭 불가) — x/../config/settings.py'], [])]),
    ('S7 프로젝트 밖으로 나가는 --except 글자는 하위 폴더에서도 거절', s_except_outside, True,
     [('../', 1, ['--except 는 기준·대상 트리에 있는 파일 경로만 받는다(폴더·글롭 불가) — ../README.md'], []),
      ('./../', 1, ['--except 는 기준·대상 트리에 있는 파일 경로만 받는다(폴더·글롭 불가) — ././../README.md'], [])]),
    ('D1 미룬 키의 파일을 레인이 옮김', d_moved, True,
     [('옮기기 전', 0, ['legacy 잔존 ⓑ 1'], ['이동 묶음 의존']), ('옮긴 뒤', 1, ['ⓑ 이동 묶음 의존 — 이동도 빼고 재상정: C2'], [])]),
    ('D2 승인 병합이 들인 이동', d_inflow_move, True,
     [('승인 전', 1, ['ⓑ 이동 묶음 의존'], []),
      ('승인 뒤', 0, ['승인 병합이 들인 이동 1파일 — 이 실행의 이동이 아니라 ⓑ 이동 묶음 의존에서 뺀다: legacy/beta.py'], [])]),
    (D3, d_moved_korean, False,  # 고정 판은 두 꼴 모두 한글 이름 개명을 놓쳤다(맨 위에서 틀린 갈래 · TOP_CHANGED)
     [('옮긴 뒤', 1, ['ⓑ 이동 묶음 의존 — 이동도 빼고 재상정: C2'], [])]),
    (D4, d_inflow_move_korean, False,
     [('승인 전', 1, ['ⓑ 이동 묶음 의존'], []),
      ('승인 뒤', 0, ['승인 병합이 들인 이동 1파일 — 이 실행의 이동이 아니라 ⓑ 이동 묶음 의존에서 뺀다: legacy/' + KOREAN], [])]),
    ('A1 refactor_audit residual — 고친(옮긴) 의미 항목', a_residual, True,
     [('residual', 0, ['결정적 잔존 0', '리뷰어 확인 대상 1'], []),
      ('개명 쌍', 0, ['\n- web/legacy/alpha.py → web/moved/alpha.py\n'], ['server/', '- 없음']),
      ('finalize', 0, ['해소 1'], ['리뷰어 잔존 1'])]),
    ('A2 refactor_audit standing — 인식 · --gate', a_standing, True,
     [('standing', 0, ['요약: standing 인식'], []), ('standing --gate', 0, ['상시 답 줄 2 · 대체 0 · red 0'], [])]),
    ('A3 refactor_audit standing --gate — 정규형이 아닌 · 프로젝트 밖 위치 글자는 맨 위(= 2.5.0)처럼', a_standing_forms, True,
     [('--gate a/./b', 2, ['③ 위치 `tests/./web/test_home.py:2` 가', 'red 1'], []),
      ('--gate ./a', 0, ['red 0'], ['③']),
      ('--gate ../a', 2, ['③ 위치 `../tests/web/test_home.py:2` 가', 'red 1'], []),
      ('--gate ./../a', 2, ['③ 위치 `./../tests/web/test_home.py:2` 가', 'red 1'], []),
      ('--gate x/../a', 2, ['③ 위치 `web/../tests/web/test_home.py:2` 가', 'red 1'], []),
      ('--gate 뿌리에만 있는 줄', 2, ['③ 위치 `tests/web/test_home.py:9` 가', 'red 1'], [])]),
    (A4, a_link_ground, True,
     [('residual', 0, ['리뷰어 확인 대상 3'], []),
      ('finalize', 2, ['근거 판형 아님 2', '해소 1', 'M1(ui: `web/fixed/out_file.py:1`)', 'M2(ui: `web/fixed/out_dir/top_bait.py:1`)'],
       ['해소 2', '해소 3']),
      ('위치 · 밖 파일 링크', 0, ['위치 거절'], []), ('위치 · 밖 폴더 링크 아래', 0, ['위치 거절'], []),
      ('위치 · 안쪽 링크', 0, ['위치 받음'], []), ('위치 · 안쪽 절대 링크', 0, ['위치 받음'], []),
      ('위치 · 일반 파일', 0, ['위치 받음'], []), ('위치 · 밖 파일(../)', 0, ['위치 거절'], []),
      ('위치 · 밖 파일(절대 경로)', 0, ['위치 거절'], []), ('위치 · 밖 파일(./x/../../)', 0, ['위치 거절'], []),
      ('위치 · 깊이 다른 자리', 0, ['위치 받음'], []), ('위치 · NUL 글자', 0, ['위치 거절'], [])]),
    (A5, a_link_carry, False,  # 이월 대조는 파일만 읽는다 — 고정 판도 두 꼴이 같았다(맨 위에서 틀린 갈래 · TOP_CHANGED)
     [('residual', 0, ['해소 유지 1', '리뷰어 확인 대상 1'], ['해소 유지 2'])]),
    (A6, a_link_root, True,
     [('finalize', 2, ['근거 판형 아님 2', '해소 1'], ['해소 2', '해소 3']),
      ('위치 · 밖 파일 링크', 0, ['위치 거절'], []), ('위치 · 안쪽 링크', 0, ['위치 받음'], [])]),
    (A8, a_separate_edit, False,  # 고정 판도 두 꼴이 같았다(밖 파일을 읽어 받았다 — 맨 위에서 바뀐 갈래 · TOP_CHANGED)
     [('안 파일', 0, ['별도 요청 1'], ['재분류']), ('안쪽 링크', 0, ['별도 요청 1'], ['재분류']),
      ('밖 파일(../)', 0, ['재분류: M1 별도 요청 → 채택', '채택 1 · 사용자 판단 0 · 별도 요청 0'], []),
      ('밖 파일(절대 경로)', 0, ['재분류: M1 별도 요청 → 채택', '별도 요청 0'], []),
      ('밖 파일(./x/../../)', 0, ['재분류: M1 별도 요청 → 채택', '별도 요청 0'], []),
      ('밖 파일 링크', 0, ['재분류: M1 별도 요청 → 채택', '별도 요청 0'], [])]),
    ('A9 refactor_audit residual — NUL 이 든 해소 근거 위치는 근거 판형 아님', a_nul_ground, True,
     [('finalize', 2, ['근거 판형 아님 1'], ['실행 불능'])]),
    ('A7 refactor_audit plan — git 설정 grep.fullName=true', a_plan_grep, True,
     [('plan', 0, ['소비자 2', '참조 치환 줄 1'], []),
      ('참조 치환 줄', 0, ['web/root/extra/uses_helper.py'], ['server/', '- 없음']),
      ('plan --names', 0, ['(나) 줄 1'], []),
      ('템플릿 참조 줄', 0, ['  참조: web/root/scaffold/view/', '저장소 템플릿이 아직 htmx 를 가리킨다'], ['참조: server/'])]),
    (W1, w_source, True,
     [('web 안', 0, ['거절'], ['줄 읽음']), ('./web 안', 0, ['거절'], ['줄 읽음']), ('./기록 안', 0, ['거절'], ['줄 읽음']),
      ('web 폴더', 0, ['거절'], ['줄 읽음']), ('./web 폴더', 0, ['거절'], ['줄 읽음']),
      ('기록 폴더', 0, ['거절'], ['줄 읽음']), ('./기록 폴더', 0, ['거절'], ['줄 읽음']),
      ('web 밖', 0, ['줄 읽음'], ['거절']), ('./web 밖', 0, ['줄 읽음'], ['거절']),
      ('webapp 안', 0, ['줄 읽음'], ['거절']), ('docs 폴더', 0, ['줄 읽음'], ['거절']),
      ('접두 없는 web/', 0, ['거절'], ['줄 읽음'])]),
    (W2, w_folder_web, False,  # 고정 판도 두 꼴이 같았다(`./` 철자를 둘 다 받았다 — 맨 위에서 틀린 갈래 · TOP_CHANGED)
     [('./문서', 0, ['줄 읽음'], ['거절']), ('./web 안', 0, ['거절'], ['줄 읽음']), ('web 안', 0, ['거절'], ['줄 읽음'])]),
    (W3, w_folder_space, True,
     [('web 안', 0, ['거절'], ['줄 읽음']), ('./web 안', 0, ['거절'], ['줄 읽음']), ('web 밖', 0, ['줄 읽음'], ['거절'])]),
    ('W4 한글 이름 하위 폴더 — 목록 이전 같은 자리 사본이 있어도 SDK 정식 등재', w_korean_install, True,
     [('install', 0, ['[sdk] 후보 kakao_js_sdk@2.8.3'], ['WV13', '되돌림']), ('게이트 · wv', 0, ['blocker 0건'], ['[WV13]'])]),
    ('W5 한글 이름 하위 폴더 — 등재된 상태의 게이트에 거짓 WV13 없음', w_korean_gate, True,
     [('게이트 · wv', 0, ['blocker 0건'], ['[WV13]'])]),
    (W6, w_log_root, False,  # 고정 판은 두 꼴 모두 첫 커밋을 못 봤다(맨 위에서 틀린 갈래 · TOP_CHANGED)
     [('--all · wv12 · wv13', 2, ['[WV13] BLOCKER — web/static/vendor/foo/'], [])]),
    (W7, w_korean_unit, False,  # 고정 판은 두 꼴 모두 거짓 WV13 으로 등재를 되돌렸다(맨 위에서 틀린 갈래 · TOP_CHANGED)
     [('install', 0, ['[sdk] 설치 kakao_js_sdk'], ['WV13', '되돌림'])]),
)


def play(tmp, index, scene, layout, scripts, tag, spelling='same'):
    stage = Stage(tmp / ('%02d-%s-%s' % (index, layout, tag)), layout, scripts, spelling)
    scene(stage)
    return stage.runs


def case_blind(tmp):
    """이 볼륨이 대소문자를 가리지 않는가(대소문자만 다른 철자로 같은 폴더에 닿는가)."""
    (tmp / 'CaseProbe').mkdir()
    return (tmp / 'caseprobe').is_dir()


def with_text_changes(runs):
    """바탕 판 실행 기록에 이 판이 일부러 바꾼 글(TOP_TEXT_CHANGED)을 넣는다."""
    out = []
    for run_name, code, text in runs:
        for was, now in TOP_TEXT_CHANGED:
            text = text.replace(was, now)
        out.append((run_name, code, text))
    return out


def first_difference(a, b):
    for x, y in zip(a, b):
        if x != y:
            return '실행 %s\n--- 앞 exit %d\n%s\n--- 뒤 exit %d\n%s' % (x[0], x[1], x[2][-1200:], y[1], y[2][-1200:])
    return '실행 수 %d ≠ %d' % (len(a), len(b))


def main():
    with tempfile.TemporaryDirectory(prefix='web251-') as tmp_name:
        tmp = Path(tmp_name).resolve()
        base = release_scripts(tmp / 'baseline', BASELINE, 'U · R' if RELEASE_250 == BASELINE else 'U')
        fixed = base if RELEASE_250 == BASELINE else release_scripts(tmp / 'release', RELEASE_250, 'R')
        blind = case_blind(tmp)
        if not blind:
            print('SKIP 철자 — 이 볼륨은 대소문자를 가린다(대소문자만 다른 루트 철자의 폴더가 없다) — 그 대조만 건너뛴다'
                  '(실패로 세지 않는다)')
        for index, (name, scene, red, shape) in enumerate(SCENES, 1):
            top = play(tmp, index, scene, 'top', SCRIPTS, 'new')
            sub = play(tmp, index, scene, 'sub', SCRIPTS, 'new')
            for run_name, code, must, never in shape:
                got = next((r for r in top if r[0] == run_name), (run_name, None, '(실행 없음)'))
                check('%s · 꼴 — %s: exit %d' % (name, run_name, code),
                      got[1] == code and all(m in got[2] for m in must) and not any(n in got[2] for n in never),
                      'exit=%s\n%s' % (got[1], got[2][-1500:]))
            check('%s — 하위 폴더 출력 = 맨 위 출력(실행 %d)' % (name, len(top)), sub == top, first_difference(top, sub))
            for layout, same in (('top', top), ('sub', sub)) if blind else ():
                other = play(tmp, index, scene, layout, SCRIPTS, 'case', 'case')
                check('%s — 철자: %s 꼴에서 대소문자만 다른 루트 철자 = 정상 철자' % (name, '맨 위' if layout == 'top' else '하위 폴더'),
                      other == same, first_difference(same, other))
            top_base = play(tmp, index, scene, 'top', base, 'base') if base is not None else None
            if top_base is not None:
                changed = TOP_CHANGED.get(name, ())
                base_now = with_text_changes(top_base)
                check('U %s — 맨 위: 바탕 판(%s)과 같은 출력%s' % (name, BASELINE, ' · 일부러 바꾼 %d 실행 밖' % len(changed)
                                                             if changed else ''),
                      [r for r in base_now if r[0] not in changed] == [r for r in top if r[0] not in changed],
                      first_difference(base_now, top))
                for run_name in changed:
                    was = next((r for r in top_base if r[0] == run_name), None)
                    now = next((r for r in top if r[0] == run_name), None)
                    check('U %s · %s — 이 판이 일부러 바꾼 맨 위 출력(바탕 판과 다르다)' % (name, run_name),
                          was is not None and now is not None and was[1:] != now[1:], (was, now))
            if fixed is None:
                continue
            top_old = top_base if fixed is base else play(tmp, index, scene, 'top', fixed, 'old')
            sub_old = play(tmp, index, scene, 'sub', fixed, 'old')
            if blind and name.split(' ')[0] in CASE_RED:
                check('R %s — 철자: 고치기 전 판(%s)은 맨 위에서 대소문자만 다른 루트 철자에 다른 출력을 냈다(붉음 먼저)'
                      % (name, RELEASE_250), play(tmp, index, scene, 'top', fixed, 'case-old', 'case') != top_old)
            if red:
                check('R %s — 고치기 전 판(%s)은 하위 폴더에서 맨 위와 달랐다(붉음 먼저)' % (name, RELEASE_250),
                      sub_old != top_old)
            else:
                check('R %s — 고치기 전 판(%s)도 하위 폴더 = 맨 위(대조 장면)' % (name, RELEASE_250), sub_old == top_old,
                      first_difference(top_old, sub_old))
    print('fixtures_patch251_subfolder: PASS=%d FAIL=%d' % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
