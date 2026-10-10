"""2.3.1 시험 전환 확인(`refactor_audit.py switch-check`) 회귀 픽스처 — 임시 git 저장소만 만들고 끝나면 지운다.

시험 명령은 pytest 대신 가짜 실행기다(이 파일이 임시 폴더에 쓰는 작은 스크립트 — 시험 함수를 실제로 불러 pytest 기록
플러그인과 같은 꼴의 JSON 줄과 pytest 꼴 결과 줄을 낸다). Django · pytest 가 없는 환경에서도 같은 판정을 만든다.
기록 플러그인(`src/switch_probe.py`) 자체는 P 묶음이 가짜 `pytest` 모듈을 끼워 훅을 직접 불러 확인한다.
묶음: U 무변(2.3.0 과 같은 입력의 refactor_audit 출력 byte 대조) · S 정상 · B 보호 분기 비켜 감 · R 반례 거절 ·
N 미검증(skip · xfail · 수집 0 · 수집 오류 · 정상 실패 · 시간 초과 · 요동 · 판독 불능) · M 어긋남(반례 무효 · 단언 다름 ·
단언 밖 실패 · 매개 case) · C 중단 뒤 재개 복구 · A 검증 뒤 0C 가 시작된 다음 다시 불림 · D dirty 트리 ·
L 생명주기(build-state · 0T 커밋 사슬 · 명세 행) · P 기록 플러그인 · X 승인 행 판독은 한 곳(치환 확인 · plan --names ·
switch-check 가 받는 행이 같다) · J 이어 붙인 흐름(0T → 치환 확인 → switch-check → 기록 → 0C → 치환 확인 · 음성 넷 ·
임시 변경이 남은 채 취소로 적힌 모순 상태).
고치기 전 판 = BASELINE 커밋의 scripts(`git show <커밋>:<경로>` 로 임시 폴더에 푼다 — 작업 사본을 stash 하지 않는다).
그 커밋이 이력에 없으면(얕은 clone 등) U 묶음을 건너뛰고 건너뛴 사실을 출력한다(실패로 세지 않는다)."""
import hashlib
import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import traceback
import types
from pathlib import Path

TEST = Path(__file__).resolve().parent
SCRIPTS = TEST.parent
PLUGIN = SCRIPTS.parent
REPO = SCRIPTS.parents[1]
BASELINE = 'f349f878'  # 고치기 전 판(배포된 dddjango-web 2.3.0) — 판마다 바탕 커밋으로 올린다
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
for _name in ('FAKE_KILL_WHEN', 'FAKE_COUNTER', 'DDDJANGO_WEB_SWITCH_PROBE'):
    ENV.pop(_name, None)
RUN = '.dddjango-web/run'
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


def run_script(script, *args, cwd=None, env=None):
    r = subprocess.run([sys.executable, '-B', str(script), *map(str, args)], capture_output=True, text=True,
                       env=env or ENV, cwd=cwd)
    return r.returncode, r.stdout + r.stderr


# ====================================================================== 가짜 시험 실행기

FAKE = r'''
import importlib.util, json, os, signal, sys, traceback


def main():
    out = os.environ.get('DDDJANGO_WEB_SWITCH_PROBE', '')

    def write(record):
        if out:
            with open(out, 'a', encoding='utf-8') as stream:
                stream.write(json.dumps(record) + '\n')

    kill = os.environ.get('FAKE_KILL_WHEN')
    if kill:
        with open('web/app/view.py', encoding='utf-8') as stream:
            if kill in stream.read():
                os.kill(os.getppid(), signal.SIGKILL)
                return 3
    sys.path.insert(0, os.getcwd())
    nodes = [a for a in sys.argv[1:] if '::' in a]
    collected, runs = [], []
    for node in nodes:
        path, func = node.split('::', 1)
        if not os.path.isfile(path):
            print('ERROR: file or directory not found: %s' % node)
            write({'event': 'finish', 'exitstatus': 4})
            return 4
        spec = importlib.util.spec_from_file_location('fake_' + path.replace('/', '_')[:-3], os.path.abspath(path))
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception:
            write({'event': 'collect_error', 'nodeid': path, 'text': traceback.format_exc()})
            print('ERROR collecting %s' % path)
            print('1 error in 0.01s')
            write({'event': 'finish', 'exitstatus': 2})
            return 2
        fn = getattr(module, func, None)
        if fn is None:
            print('ERROR: not found: %s' % node)
            write({'event': 'finish', 'exitstatus': 4})
            return 4
        if getattr(fn, 'collect', True) is False:
            continue
        cases = getattr(fn, 'cases', None)
        for case in (cases if cases is not None else [None]):
            nodeid = '%s::%s' % (path, func) + ('' if case is None else '[%s]' % case)
            collected.append(nodeid)
            runs.append((nodeid, fn, case))
    write({'event': 'collected', 'nodeids': collected})
    counts = {'passed': 0, 'failed': 0, 'skipped': 0, 'xfailed': 0, 'xpassed': 0}
    for nodeid, fn, case in runs:
        def report(when, outcome, xfail=False, exc=None):
            write({'event': 'report', 'nodeid': nodeid, 'when': when, 'outcome': outcome, 'wasxfail': xfail,
                   'exc': exc})
        if getattr(fn, 'skip', False):
            report('setup', 'skipped')
            report('teardown', 'passed')
            counts['skipped'] += 1
            continue
        report('setup', 'passed')
        xfail = bool(getattr(fn, 'xfail', False))
        try:
            fn() if case is None else fn(case)
        except Exception as error:
            frames = [[f.filename, f.lineno, f.name] for f in traceback.extract_tb(error.__traceback__)]
            exc = {'type': '%s.%s' % (type(error).__module__, type(error).__qualname__), 'frames': frames}
            report('call', 'skipped' if xfail else 'failed', xfail, exc)
            counts['xfailed' if xfail else 'failed'] += 1
        else:
            report('call', 'passed', xfail)
            counts['xpassed' if xfail else 'passed'] += 1
        report('teardown', 'passed')
    if not collected:
        print('no tests ran in 0.01s')
        write({'event': 'finish', 'exitstatus': 5})
        return 5
    print(', '.join('%d %s' % (n, k) for k, n in counts.items() if n) + ' in 0.01s')
    status = 1 if counts['failed'] else 0
    write({'event': 'finish', 'exitstatus': status})
    return status


sys.exit(main())
'''


def fake_cmd(tmp):
    path = Path(tmp) / 'fake_pytest.py'
    if not path.exists():
        path.write_text(FAKE, encoding='utf-8')
    return '%s -B %s' % (shlex.quote(sys.executable), shlex.quote(str(path)))


# ====================================================================== 장면(작은 web 프로젝트 · 0T 커밋)

VIEW = [
    "CHOICE_URL = '/choose/'",
    '',
    '',
    'class Response:',
    "    def __init__(self, status, location=''):",
    '        self.status = status',
    '        self.location = location',
    '',
    '',
    'def _render_page(request, vm):',
    "    if vm['needs_choice']:",
    '        return Response(302, CHOICE_URL)',
    '    return Response(200)',
    '',
    '',
    'def page_view(request):',
    "    context = request.get('context')",
    '    if context is None:',
    '        return Response(302, CHOICE_URL)',
    "    return _render_page(request, {'needs_choice': context['employees'] > 1 and context['selected'] is None})",
]
OLD_TEST = [
    'from web.app.view import _render_page',
    '',
    '',
    'def test_gate():',
    "    response = _render_page({}, {'needs_choice': True})",
    '    assert response.status == 302',
    "    assert response.location == '/choose/'",
]
NEW_TEST = [
    'from web.app.view import page_view',
    '',
    '',
    'def test_gate():',
    "    request = {'context': {'employees': 2, 'selected': None}}",
    '    response = page_view(request)',
    '    assert response.status == 302',
    "    assert response.location == '/choose/'",
]
MUT_URL = (12, "        return Response(302, '/elsewhere/')")     # 보호 분기 안 — 단언 2 를 깬다
MUT_IF = (11, '    if False:')                                      # 보호 분기 안 — 단언 1 을 깬다
MUT_COMMON = (1, "CHOICE_URL = '/elsewhere/'")                      # 보호 분기 밖(두 길이 함께 쓰는 값)
MUT_NOOP = (12, '        return Response(302, CHOICE_URL)  # 관찰 안 됨')
MUT_RAISE = (12, "        raise RuntimeError('boom')")
ROW = ('- 시험 전환: `tests/test_gate.py::test_gate` · 행위 `web.app.view._render_page` → `web.app.view.page_view` · '
       '보호 분기 `web/app/view.py:11-12` · 반례 %s')


class Scene:
    def __init__(self, tmp, name, new_test=None, old_test=None, mutants=(MUT_URL,), row=None, spec=None,
                 test_switch=None, view=None, extra=None):
        self.tmp = Path(tmp)
        self.root = Path(tmp) / name
        self.root.mkdir(parents=True)
        git(self.root, 'init', '-q')
        self.w('web/__init__.py')
        self.w('web/app/__init__.py')
        self.w('web/app/view.py', *(view or VIEW))
        self.w('tests/test_gate.py', *(old_test or OLD_TEST))
        for rel, lines in (extra or {}).items():        # 바탕에 더 두는 파일(경로 → 줄 목록)
            self.w(rel, *lines)
        self.base = self.commit('base')
        self.folder = self.root / RUN
        (self.folder / 'test-switch').mkdir(parents=True)
        self.mutants = []
        for i, (line, text) in enumerate(mutants, 1):
            lines = self.read('web/app/view.py').split('\n')
            lines[line - 1] = text
            (self.root / 'web/app/view.py').write_text('\n'.join(lines), encoding='utf-8')
            diff = subprocess.run(['git', '-C', str(self.root), 'diff', '--', 'web/app/view.py'], capture_output=True,
                                  env=ENV, check=True).stdout
            rel = 'test-switch/%d.mutant.diff' % i
            (self.folder / rel).write_bytes(diff)
            git(self.root, 'checkout', '--', 'web/app/view.py')
            self.mutants.append(rel)
        text = spec if spec is not None else '# 설계 명세\n\n## 슬라이스 0\n\n%s\n\n## 슬라이스 1\n' % (
            row if row is not None else ROW % ' '.join('`%s`' % m for m in self.mutants))
        (self.folder / 'design-spec.md').write_text(text, encoding='utf-8')
        self.snapshot = self.commit('docs: 산출물')
        self.w('tests/test_gate.py', *(new_test or NEW_TEST))
        self.t = self.commit('test(web): 0T 시험 전환')
        self.state(test_switch)

    def w(self, rel, *lines):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('\n'.join(lines) + ('\n' if lines else ''), encoding='utf-8')

    def read(self, rel):
        return (self.root / rel).read_text(encoding='utf-8')

    def commit(self, message):
        git(self.root, 'add', '-A')
        git(self.root, 'commit', '-qm', message)
        return git(self.root, 'rev-parse', 'HEAD')

    def state(self, test_switch=None, slices=None, snapshot=None):
        ts = test_switch if test_switch is not None else {'state': 'verifying', 'commits': [self.t],
                                                          'cancel_commits': [], 'evidence': ''}
        zero = {'name': 'slice-0-debt', 'status': 'in-progress', 'commits': [self.t]}
        if ts != 'none':
            zero['test_switch'] = ts
        data = {'phase': 'implement', 'mode': 'modify', 'git_snapshot': snapshot or self.snapshot,
                'slices': slices or [zero, {'name': 'slice-1-gate', 'status': 'pending', 'commits': []}]}
        (self.folder / 'build-state.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def switch(self, *extra, env=None, cmd=None, folder=RUN):
        args = ['--project', self.root, 'switch-check', folder, '--test-cmd', cmd or fake_cmd(self.tmp), *extra]
        scratch = self.tmp / 'tool-tmp'       # 도구의 임시 폴더를 묶음 임시 폴더 안에 둔다(죽인 실행이 남긴 것도 함께 지워진다)
        scratch.mkdir(exist_ok=True)
        return run_script(SCRIPTS / 'refactor_audit.py', *args, cwd=self.root,
                          env=dict(ENV, TMPDIR=str(scratch), **(env or {})))

    def clean(self):
        return git(self.root, 'status', '--porcelain', '--untracked-files=all', '--', '.', ':(exclude).dddjango-web')

    def state_json(self):
        path = self.folder / 'test-switch' / 'state.json'
        return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None

    def evidence(self):
        path = self.folder / 'test-switch' / 'evidence.json'
        return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


OK_LINE = '[switch] tests/test_gate.py::test_gate — 정상 통과 · 반례 %d 모두 옛 · 새 같은 단언(%s) 실패 · 검증됨'


def untouched(s, name):
    """시작 거절 꼴 — 작업 트리 · 복구 상태 · 증거에 손대지 않았다."""
    check('%s — 작업 트리 그대로 · state.json · evidence.json 없음' % name,
          s.clean() == '' and s.state_json() is None and s.evidence() is None,
          'status=%r state=%r' % (s.clean(), s.state_json()))


# ====================================================================== S — 정상

def bundle_normal(tmp):
    s = Scene(tmp, 's1', mutants=(MUT_URL, MUT_IF))
    e, out = s.switch()
    check('S1 정상 — exit 0', e == 0, out[-1500:])
    check('S1 행 결과 줄(반례 2 · 단언 2 · 1)', (OK_LINE % (2, '2 · 1')) in out, out[-1500:])
    check('S1 반례마다 옛 · 새 실패 자리(새 :8 단언 2 · 옛 기준 판 :7 단언 2)',
          '  반례 test-switch/1.mutant.diff — 새 tests/test_gate.py:8 단언 2 · 옛 tests/test_gate.py:7(기준 판) 단언 2 · '
          'AssertionError' in out and
          '  반례 test-switch/2.mutant.diff — 새 tests/test_gate.py:7 단언 1 · 옛 tests/test_gate.py:6(기준 판) 단언 1 · '
          'AssertionError' in out, out[-1500:])
    check('S1 요약 — 행 1 · 검증 1 · 증거 경로',
          '요약: switch-check 행 1 · 검증 1 · 어긋남 0 · 미검증 0 · 증거 %s/test-switch/evidence.json' % RUN in out,
          out[-600:])
    ev = s.evidence() or {}
    row = (ev.get('rows') or [{}])[0]
    muts = row.get('mutants') or [{}, {}]
    check('S1 evidence.json — T sha · 기준 · 반례 sha256 · 노드 · 단언 순번 · 결과 줄',
          ev.get('t_head') == s.t and ev.get('t_commits') == [s.t] and ev.get('snapshot') == s.snapshot
          and row.get('test') == 'tests/test_gate.py::test_gate' and row.get('nodes') == ['tests/test_gate.py::test_gate']
          and row.get('branch') == 'web/app/view.py:11-12'
          and [m.get('path') for m in muts] == s.mutants
          and [m.get('sha256') for m in muts] == [sha256(s.folder / m) for m in s.mutants]
          and [m['new']['assert'] for m in muts] == [2, 1] and [m['old']['assert'] for m in muts] == [2, 1]
          and muts[0]['new']['summary'] == '1 failed in 0.01s'
          and row['normal']['new']['summary'] == '1 passed in 0.01s'
          and row['normal']['old']['summary'] == '1 passed in 0.01s', json.dumps(ev, ensure_ascii=False)[:1800])
    st = s.state_json() or {}
    check('S1 state.json — 시작 HEAD · T HEAD · 대상 경로 · 반례 sha256 · 단계 verified · 남은 임시 변경 0',
          st.get('start_head') == s.t and st.get('t_head') == s.t and st.get('stage') == 'verified'
          and st.get('pending') == [] and 'web/app/view.py' in st.get('targets', [])
          and st.get('mutants') == {m: sha256(s.folder / m) for m in s.mutants}, json.dumps(st, ensure_ascii=False)[:1500])
    check('S1 작업 트리 · index 가 시작 상태 그대로(옛 시험 임시 파일 없음)', s.clean() == '' and
          git(s.root, 'rev-parse', 'HEAD') == s.t, s.clean())
    e2, out2 = s.switch()
    check('S1 다시 돌려도 exit 0(검증 상태에서 재확인)', e2 == 0 and (OK_LINE % (2, '2 · 1')) in out2, out2[-800:])
    # 산출물 커밋(.dddjango-web/ 만)이 0T 뒤에 와도 받는다
    s.commit('docs: build-state')
    e3, out3 = s.switch()
    check('S2 0T 뒤 산출물 커밋(.dddjango-web/ 만) — exit 0', e3 == 0 and (OK_LINE % (2, '2 · 1')) in out3, out3[-900:])
    # 매개 case — case 마다 옛 · 새 같은 단언
    pre = ['from web.app.view import _render_page', '', '']
    old = pre + ['def test_gate(case):', "    response = _render_page({}, {'needs_choice': True})",
                 '    assert response.status == 302', "    assert response.location == '/choose/'", '',
                 '', "test_gate.cases = ['a', 'b']"]
    new = ['from web.app.view import page_view', '', '', 'def test_gate(case):',
           "    request = {'context': {'employees': 2, 'selected': None}}", '    response = page_view(request)',
           '    assert response.status == 302', "    assert response.location == '/choose/'", '', '',
           "test_gate.cases = ['a', 'b']"]
    p = Scene(tmp, 's3', old_test=old, new_test=new)
    e, out = p.switch()
    ev = p.evidence() or {}
    check('S3 매개 case 둘 — exit 0 · 노드 둘', e == 0 and (OK_LINE % (1, '2')) in out and
          (ev.get('rows') or [{}])[0].get('nodes') == ['tests/test_gate.py::test_gate[a]', 'tests/test_gate.py::test_gate[b]'],
          out[-900:])


# ====================================================================== B — 보호 분기를 비켜 가는 새 시험

def bundle_bypass(tmp):
    new = list(NEW_TEST)
    new[4] = "    request = {'context': None}"
    s = Scene(tmp, 'b1', new_test=new)
    e, out = s.switch()
    check('B1 입력을 바꿔 다른 분기로 가는 새 시험 — exit 2(반례에서 새 시험이 통과)', e == 2 and
          '[switch] tests/test_gate.py::test_gate — 반례 test-switch/1.mutant.diff 에서 새 시험이 통과한다(옛 시험은 단언 2 실패)'
          in out and '· 어긋남' in out, out[-1200:])
    check('B1 요약 — 어긋남 1 · 증거 없음', '요약: switch-check 행 1 · 검증 0 · 어긋남 1 · 미검증 0' in out
          and s.evidence() is None, out[-500:])
    check('B1 반례를 되돌려 작업 트리 그대로 · state 단계 mismatch', s.clean() == '' and
          (s.state_json() or {}).get('stage') == 'mismatch' and (s.state_json() or {}).get('pending') == [],
          '%r %r' % (s.clean(), s.state_json()))


# ====================================================================== R — 반례 거절(실행 전)

def bundle_reject(tmp):
    new = list(NEW_TEST)
    new[4] = "    request = {'context': None}"
    s = Scene(tmp, 'r1', new_test=new, mutants=(MUT_COMMON,))
    e, out = s.switch()
    check('R1 보호 분기 밖 공통 부분만 깨는 반례 — exit 1(줄 범위 밖 거절)', e == 1 and
          '[switch] 시작 거절 — 반례 test-switch/1.mutant.diff 가 보호 분기 web/app/view.py:11-12 줄 범위 밖을 바꾼다(1행)'
          in out, out[-900:])
    untouched(s, 'R1')
    # 두 파일 · 다른 파일 · 줄 번호 어긋남 · 분기 앞 끼움 · 반례 없음 · 시험 파일인 보호 분기
    s2 = Scene(tmp, 'r2')
    diff = (s2.folder / s2.mutants[0]).read_text(encoding='utf-8')
    (s2.folder / s2.mutants[0]).write_text(diff + diff.replace('web/app/view.py', 'web/app/other.py'), encoding='utf-8')
    e, out = s2.switch()
    check('R2 두 파일을 바꾸는 반례 — exit 1', e == 1 and '파일 하나만 바꾸는 diff 여야 한다' in out, out[-600:])
    (s2.folder / s2.mutants[0]).write_text(diff.replace('web/app/view.py', 'web/app/__init__.py'), encoding='utf-8')
    e, out = s2.switch()
    check('R3 보호 분기 파일이 아닌 파일을 바꾸는 반례 — exit 1', e == 1 and
          '보호 분기 파일(web/app/view.py)이 아닌 web/app/__init__.py 를 바꾼다' in out, out[-600:])
    (s2.folder / s2.mutants[0]).write_text(diff.replace('@@ -9,7 +9,7 @@', '@@ -10,7 +10,7 @@'), encoding='utf-8')
    e, out = s2.switch()
    check('R4 줄 번호가 기준 판과 어긋난 반례 — exit 1', e == 1 and '기준 판의 그 줄에 맞지 않는다' in out, out[-600:])
    (s2.folder / s2.mutants[0]).write_text(
        'diff --git a/web/app/view.py b/web/app/view.py\n--- a/web/app/view.py\n+++ b/web/app/view.py\n'
        '@@ -9,3 +9,4 @@\n \n+_HOOK = 1\n def _render_page(request, vm):\n     if vm[\'needs_choice\']:\n', encoding='utf-8')
    e, out = s2.switch()
    check('R5 보호 분기 바로 앞에 끼우는 반례 — exit 1(범위 밖)', e == 1 and '줄 범위 밖을 바꾼다' in out, out[-600:])
    (s2.folder / s2.mutants[0]).unlink()
    e, out = s2.switch()
    check('R6 반례 파일 없음 — exit 1', e == 1 and '반례 파일이 없다' in out, out[-600:])
    untouched(s2, 'R2~R6')
    s3 = Scene(tmp, 'r7', row=ROW.replace('web/app/view.py:11-12', 'tests/test_gate.py:5-6') % '`test-switch/1.mutant.diff`')
    e, out = s3.switch()
    check('R7 보호 분기가 web/ 비시험 파일이 아님 — exit 1', e == 1 and '보호 분기는 web/ 비시험 파일이다' in out, out[-600:])


# ====================================================================== N — 미검증(exit 1)

def bundle_unverified(tmp):
    def variant(name, extra, **kw):
        s = Scene(tmp, name, new_test=NEW_TEST + extra, **kw)
        e, out = s.switch()
        return s, e, out

    s, e, out = variant('n1', ['', '', 'test_gate.skip = True'])
    check('N1 새 시험 skip — exit 1 미검증', e == 1 and '정상 제품에서 새 시험이 통과하지 않는다(skip)' in out and
          '· 미검증' in out and '요약: switch-check 행 1 · 검증 0 · 어긋남 0 · 미검증 1' in out, out[-900:])
    check('N1 미검증이어도 작업 트리 그대로', s.clean() == '' and (s.state_json() or {}).get('stage') == 'unverified',
          s.clean())
    s, e, out = variant('n2', ['', '', 'test_gate.xfail = True'])
    check('N2 새 시험 xfail(정상에서 xpass) — exit 1', e == 1 and '정상 제품에서 새 시험이 통과하지 않는다(xpass)' in out,
          out[-900:])
    s, e, out = variant('n3', ['', '', 'test_gate.collect = False'])
    check('N3 수집 0 — exit 1', e == 1 and '수집 0' in out and '· 미검증' in out, out[-900:])
    s, e, out = variant('n4', ['', '', "raise ImportError('x')"])
    check('N4 수집 오류(import 오류) — exit 1', e == 1 and '수집 오류' in out and '· 미검증' in out, out[-900:])
    bad = list(NEW_TEST)
    bad[4] = "    request = {'context': {'employees': 1, 'selected': None}}"
    s = Scene(tmp, 'n5', new_test=bad)
    e, out = s.switch()
    check('N5 새 시험이 정상 제품에서 실패 — exit 1', e == 1 and
          '정상 제품에서 새 시험이 통과하지 않는다(실패 — 단언 1' in out, out[-900:])
    slow = list(NEW_TEST)
    slow.insert(5, '    __import__("time").sleep(30)')
    s = Scene(tmp, 'n6', new_test=slow)
    e, out = s.switch('--timeout', '2')
    check('N6 시간 초과 — exit 1', e == 1 and '시간 초과 2초' in out and s.clean() == '', out[-900:])
    counter = Path(tmp) / 'flaky-counter'
    flaky = list(NEW_TEST) + ['', '', 'def _flaky():', "    path = __import__('os').environ['FAKE_COUNTER']",
                              "    n = int(open(path).read()) if __import__('os').path.exists(path) else 0",
                              "    open(path, 'w').write(str(n + 1))", '    return n % 2 == 0']
    flaky.insert(7, '    assert _flaky()')
    s = Scene(tmp, 'n7', new_test=flaky)
    e, out = s.switch(env={'FAKE_COUNTER': str(counter)})
    check('N7 요동(같은 실행 두 번 결과가 다름) — exit 1', e == 1 and '요동' in out and '· 미검증' in out
          and s.clean() == '', out[-900:])
    s = Scene(tmp, 'n8')
    e, out = s.switch(cmd='%s -c pass' % shlex.quote(sys.executable))
    check('N8 기록 없는 시험 명령 — exit 1 판독 불능', e == 1 and '판독 불능' in out, out[-900:])
    e, out = s.switch(cmd='/nonexistent/pytest-x')
    check('N9 실행할 수 없는 시험 명령 — exit 1', e == 1 and '시험 명령을 실행할 수 없다' in out and s.clean() == '',
          out[-900:])
    odd = Path(tmp) / 'odd_records.py'
    odd.write_text(
        "import json, os, sys\n"
        "node = [a for a in sys.argv[1:] if '::' in a][0]\n"
        "rows = [{'event': 'collected', 'nodeids': [node]},\n"
        "        {'event': 'report', 'nodeid': node, 'when': 'call', 'outcome': 'failed', 'wasxfail': False,\n"
        "         'exc': {'type': 'builtins.AssertionError', 'frames': [['only-one-field']]}},\n"
        "        {'event': 'finish', 'exitstatus': 1}]\n"
        "with open(os.environ['DDDJANGO_WEB_SWITCH_PROBE'], 'a') as f:\n"
        "    f.write(''.join(json.dumps(r) + '\\n' for r in rows))\n"
        "sys.exit(1)\n", encoding='utf-8')
    e, out = s.switch(cmd='%s -B %s' % (shlex.quote(sys.executable), shlex.quote(str(odd))))
    check('N11 꼴이 어긋난 기록 — exit 1 판독 불능(도구가 죽지 않는다)', e == 1 and '판독 불능 — 기록 꼴이 아니다' in out
          and '· 미검증' in out and s.clean() == '', out[-900:])
    broken = list(OLD_TEST)
    broken[6] = "    assert response.location == '/wrong/'"
    s = Scene(tmp, 'n10', old_test=broken)
    e, out = s.switch()
    check('N10 옛 시험이 정상 제품에서 이미 실패 — exit 1(헛 반례 대조 막음)', e == 1 and
          '정상 제품에서 옛 시험이 통과하지 않는다' in out and s.clean() == '', out[-900:])


# ====================================================================== M — 어긋남(exit 2)

def bundle_mismatch(tmp):
    s = Scene(tmp, 'm1', mutants=(MUT_NOOP,))
    e, out = s.switch()
    check('M1 옛 시험도 통과하는 반례(반례 무효) — exit 2', e == 2 and
          '반례 test-switch/1.mutant.diff 에서 옛 시험이 통과한다' in out, out[-900:])
    swapped = list(NEW_TEST)
    swapped[6], swapped[7] = swapped[7], swapped[6]
    s = Scene(tmp, 'm2', new_test=swapped)
    e, out = s.switch()
    check('M2 옛 · 새 다른 단언에서 실패 — exit 2', e == 2 and
          '반례 test-switch/1.mutant.diff 에서 옛 단언 2 · 새 단언 1 — 같은 단언이 아니다' in out, out[-900:])
    s = Scene(tmp, 'm3', mutants=(MUT_RAISE,))
    e, out = s.switch()
    check('M3 단언이 아닌 예외로 실패(제품 RuntimeError) — exit 2', e == 2 and
          '반례 test-switch/1.mutant.diff 에서 새 시험이 단언 밖에서 실패한다(builtins.RuntimeError' in out, out[-900:])
    helper = list(NEW_TEST)
    helper[7] = '    _check(response)'
    helper += ['', '', 'def _check(response):', "    assert response.location == '/choose/'"]
    s = Scene(tmp, 'm4', new_test=helper)
    e, out = s.switch()
    check('M4 도움 함수 안 assert 로 실패 — exit 2(시험 함수의 단언이 아님)', e == 2 and
          '새 시험이 단언 밖에서 실패한다(builtins.AssertionError · tests/test_gate.py:12 _check)' in out, out[-900:])
    pre = ['from web.app.view import _render_page', '', '']
    old = pre + ['def test_gate(case):', "    response = _render_page({}, {'needs_choice': True})",
                 '    assert response.status == 302', "    assert response.location == '/choose/'", '', '',
                 "test_gate.cases = ['a', 'b']"]
    new = ['from web.app.view import page_view', '', '', 'def test_gate(case):',
           "    request = {'context': None if case == 'b' else {'employees': 2, 'selected': None}}",
           '    response = page_view(request)', '    assert response.status == 302',
           "    assert response.location == '/choose/'", '', '', "test_gate.cases = ['a', 'b']"]
    s = Scene(tmp, 'm5', old_test=old, new_test=new)
    e, out = s.switch()
    check('M5 매개 case 하나가 보호 분기를 비켜 감 — exit 2', e == 2 and
          '반례 test-switch/1.mutant.diff [b] 에서 새 시험이 통과한다(옛 시험은 단언 2 실패)' in out, out[-900:])


# ====================================================================== C — 반례 적용 중 중단 뒤 재개

def bundle_crash(tmp):
    s = Scene(tmp, 'c1', mutants=(MUT_URL, MUT_IF))
    e, out = s.switch(env={'FAKE_KILL_WHEN': "'/elsewhere/'"})
    st = s.state_json() or {}
    old_tmp = [p['path'] for p in st.get('pending', []) if p.get('kind') == 'old-test']
    check('C1 반례 적용 중 도구가 죽음 — state.json 에 남은 임시 변경(반례 · 옛 시험 임시 파일)',
          e != 0 and {p.get('kind') for p in st.get('pending', [])} == {'mutant', 'old-test'}
          and "'/elsewhere/'" in s.read('web/app/view.py') and old_tmp and (s.root / old_tmp[0]).exists(),
          'exit=%d state=%s' % (e, json.dumps(st, ensure_ascii=False)[:900]))
    e, out = s.switch()
    check('C1 재실행 — 기록대로 먼저 복구한 뒤 검증 exit 0', e == 0 and
          '[switch] 복구 — web/app/view.py 반례 되돌림' in out and
          '[switch] 복구 — %s 옛 시험 임시 파일 지움' % (old_tmp[0] if old_tmp else '?') in out and
          (OK_LINE % (2, '2 · 1')) in out and '· 복구 2' in out, out[-1200:])
    check('C1 복구 뒤 작업 트리 그대로', s.clean() == '' and (s.state_json() or {}).get('pending') == [], s.clean())
    # 복구 불능 — 기록 밖 내용(죽은 뒤 사람이 같은 파일을 고침)
    s2 = Scene(tmp, 'c2')
    e, out = s2.switch(env={'FAKE_KILL_WHEN': "'/elsewhere/'"})
    with (s2.root / 'web/app/view.py').open('a', encoding='utf-8') as f:
        f.write('# 사람이 고침\n')
    edited = s2.read('web/app/view.py')
    e, out = s2.switch()
    check('C2 기록 밖 내용이면 복구 불능 — exit 1 · 손대지 않음', e == 1 and '[switch] 복구 불능 — web/app/view.py' in out
          and s2.read('web/app/view.py') == edited and (s2.state_json() or {}).get('pending'), out[-900:])
    # 이미 되돌려진 기록(되돌린 뒤 · 기록 갱신 전에 죽은 꼴)
    s3 = Scene(tmp, 'c3')
    s3.switch(env={'FAKE_KILL_WHEN': "'/elsewhere/'"})
    git(s3.root, 'checkout', '--', 'web/app/view.py')
    e, out = s3.switch()
    check('C3 반례가 이미 되돌려져 있으면 그 자리는 그대로 두고 임시 파일만 지움 — exit 0', e == 0 and
          '[switch] 복구 — web/app/view.py 이미 시작 내용' in out and '옛 시험 임시 파일 지움' in out
          and s3.clean() == '', out[-1200:])
    # 죽은 뒤 산출물 커밋으로 HEAD 가 움직여도 — 그 파일의 HEAD 내용이 기록의 시작 내용이면 되돌린다
    s4 = Scene(tmp, 'c4')
    s4.switch(env={'FAKE_KILL_WHEN': "'/elsewhere/'"})
    git(s4.root, 'add', '.dddjango-web')
    git(s4.root, 'commit', '-qm', 'docs: 산출물(죽은 뒤)')
    e, out = s4.switch()
    check('C4 죽은 뒤 산출물 커밋으로 HEAD 가 움직임 — 복구하고 exit 0', e == 0 and
          '[switch] 복구 — web/app/view.py 반례 되돌림' in out and s4.clean() == '', out[-1200:])
    # 반례가 실수로 커밋됨 — HEAD 의 그 파일이 기록의 시작 내용이 아니다
    s5 = Scene(tmp, 'c5')
    s5.switch(env={'FAKE_KILL_WHEN': "'/elsewhere/'"})
    git(s5.root, 'add', 'web/app/view.py')
    git(s5.root, 'commit', '-qm', 'oops: 반례를 커밋')
    mutated = s5.read('web/app/view.py')
    e, out = s5.switch()
    check('C5 반례가 커밋돼 버림 — 복구 불능 exit 1 · 손대지 않음', e == 1 and
          '[switch] 복구 불능 — HEAD 의 web/app/view.py 가 기록의 시작 내용이 아니다' in out
          and s5.read('web/app/view.py') == mutated and (s5.state_json() or {}).get('pending'), out[-900:])


# ====================================================================== A — 검증 뒤(0C 가 시작된 뒤 다시 불림)

def bundle_after(tmp):
    s = Scene(tmp, 'a1')
    e, out = s.switch()
    check('A0 0T 검증 — exit 0', e == 0, out[-600:])
    proof = (s.folder / 'test-switch' / 'evidence.json').read_bytes()
    with (s.root / 'web/app/view.py').open('a', encoding='utf-8') as f:
        f.write('# 0C 정리\n')
    git(s.root, 'add', 'web/app/view.py')
    git(s.root, 'commit', '-qm', 'refactor(web): 0C')
    zero_c = git(s.root, 'rev-parse', 'HEAD')

    def record(state, *more):
        s.state(slices=[{'name': 'slice-0-debt', 'commits': [s.t, zero_c],
                         'test_switch': {'state': state, 'commits': [s.t], 'cancel_commits': [],
                                         'evidence': RUN + '/test-switch/evidence.json'}}, *more])

    record('verified')
    before = (s.folder / 'test-switch' / 'state.json').read_bytes()
    e, out = s.switch(cmd='/nonexistent/pytest-x')
    check('A1 0C 뒤 다시 불림(재개) — 앞 증거가 같은 T · 같은 반례면 exit 0 · 시험을 돌리지 않는다', e == 0 and
          '[switch] tests/test_gate.py::test_gate — 이미 검증됨(증거의 T %s · 반례 지문 같음) · T 뒤 슬라이스 커밋 1' % s.t[:12]
          in out and '요약: switch-check 행 1 · 검증 1(앞 증거) · 어긋남 0 · 미검증 0 · 증거 %s/test-switch/evidence.json' % RUN
          in out, out[-900:])
    check('A1 증거 · 복구 상태를 다시 쓰지 않는다', (s.folder / 'test-switch' / 'evidence.json').read_bytes() == proof
          and (s.folder / 'test-switch' / 'state.json').read_bytes() == before and s.clean() == '')
    s.w('tests/test_gate.py', 'def test_renamed():', '    assert True')
    git(s.root, 'add', 'tests/test_gate.py')
    git(s.root, 'commit', '-qm', 'feat: 기능 슬라이스가 그 시험을 바꿈')
    feature = git(s.root, 'rev-parse', 'HEAD')
    record('verified', {'name': 'slice-1-gate', 'commits': [feature]})
    e, out = s.switch(cmd='/nonexistent/pytest-x')
    check('A5 뒤 기능 슬라이스가 그 시험 함수를 없앤 뒤에도 — 앞 증거로 exit 0(HEAD 의 시험을 다시 따지지 않는다)', e == 0 and
          '이미 검증됨' in out and 'T 뒤 슬라이스 커밋 2' in out, out[-700:])
    record('verifying')
    e, out = s.switch()
    check('A2 검증 기록 없이 0C 가 있음 — exit 1(검증 전 0C 금지)', e == 1 and
          'T 뒤에 슬라이스 커밋 %s(slices[0])가 있는데 0T 검증을 확인할 수 없다(test_switch.state 가 verifying)' % zero_c[:12]
          in out and '검증 전에는 0C 를 보내지 않는다' in out, out[-700:])
    record('verified')
    mutant = s.folder / s.mutants[0]
    original = mutant.read_bytes()
    mutant.write_bytes(original + b'\n')
    e, out = s.switch()
    check('A3 증거 뒤 반례가 바뀜 — exit 1', e == 1 and '증거의 행 · 반례 지문이 지금 명세 · 반례와 다르다' in out, out[-700:])
    mutant.write_bytes(original)
    (s.folder / 'test-switch' / 'evidence.json').unlink()
    e, out = s.switch()
    check('A4 증거 파일 없음 — exit 1', e == 1 and 'evidence.json 가 없거나 꼴이 아니다' in out, out[-700:])


# ====================================================================== D — dirty 트리

def bundle_dirty(tmp):
    s = Scene(tmp, 'd1')
    s.w('notes.txt', 'x')
    e, out = s.switch()
    check('D1 미추적 파일 — exit 1 · 손대지 않음', e == 1 and
          '[switch] 시작 거절 — 작업 트리에 .dddjango-web/ 밖 변경 1: notes.txt(손대지 않음)' in out
          and (s.root / 'notes.txt').exists() and s.state_json() is None, out[-700:])
    (s.root / 'notes.txt').unlink()
    with (s.root / 'web/app/view.py').open('a', encoding='utf-8') as f:
        f.write('# 고침\n')
    e, out = s.switch()
    check('D2 추적 파일 수정 — exit 1 · 손대지 않음', e == 1 and 'web/app/view.py(손대지 않음)' in out
          and s.read('web/app/view.py').endswith('# 고침\n') and s.state_json() is None, out[-700:])
    git(s.root, 'checkout', '--', 'web/app/view.py')
    (s.folder / 'scratch.md').write_text('x', encoding='utf-8')
    e, out = s.switch()
    check('D3 .dddjango-web/ 안 변경은 받는다 — exit 0', e == 0, out[-700:])


# ====================================================================== L — 생명주기 · 명세 행

def bundle_lifecycle(tmp):
    s = Scene(tmp, 'l1')
    t = s.t

    def expect(name, needle):
        e, out = s.switch()
        check('%s — exit 1' % name, e == 1 and needle in out, out[-700:])

    s.state({'state': 'cancelled', 'commits': [t], 'cancel_commits': [t], 'evidence': ''})
    expect('L1 취소된 0T', 'test_switch.state 가 cancelled')
    s.state('none')
    expect('L2 test_switch 기록 없음', 'slices[0].test_switch 기록이 없다')
    s.state({'state': 'verifying', 'commits': [], 'cancel_commits': [], 'evidence': ''})
    expect('L3 T 커밋 없음', 'test_switch.commits 가 비었다')
    s.state({'state': 'verifying', 'commits': [t], 'cancel_commits': [], 'evidence': ''},
            slices=[{'name': 'slice-0-debt', 'commits': [], 'test_switch': {'state': 'verifying', 'commits': [t]}}])
    expect('L4 T 가 slices[0].commits 밖', 'slices[0].commits 에 없다')
    s.state(slices=[{'name': 'slice-0-debt', 'commits': [t], 'test_switch': {'state': 'verifying', 'commits': [t]}},
                    {'name': 'slice-1-gate', 'commits': [t]}])
    expect('L5 T 가 기능 커밋과 겹침', '기능 슬라이스 slice-1-gate 기록과 겹친다')
    s.state(snapshot=t)
    expect('L6 git_snapshot 뒤 0T 커밋이 없다', '0T 커밋이 없다')
    s.state({'state': 'verifying', 'commits': ['zz'], 'cancel_commits': [], 'evidence': ''})
    expect('L7 해시 꼴 아님', '커밋 해시(7~40 hex)가 아니다')
    s.state()
    s.w('web/app/view.py', *VIEW, '# 0T 안 제품 변경')
    git(s.root, 'add', 'web/app/view.py')
    git(s.root, 'commit', '-qm', 'test(web): 제품도 바꾼 0T')
    tip = git(s.root, 'rev-parse', 'HEAD')
    s.state({'state': 'verifying', 'commits': [t, tip], 'cancel_commits': [], 'evidence': ''},
            slices=[{'name': 'slice-0-debt', 'commits': [t, tip],
                     'test_switch': {'state': 'verifying', 'commits': [t, tip]}}])
    expect('L8 T 커밋이 web/ 제품을 바꿈', 'T 커밋 %s 가 web/ 을 바꾼다 — 0T 는 제품을 고정한다 — web/app/view.py' % tip[:12])
    s.state()
    expect('L9 T 아닌 커밋이 보호 분기 파일을 바꿈', '보호 분기 파일 web/app/view.py 가 git_snapshot 뒤 바뀌었다')
    s6 = Scene(tmp, 'l16')
    s6.w('tests/test_gate.py', *NEW_TEST, '# T 로 기록하지 않은 시험 편집')
    git(s6.root, 'add', 'tests/test_gate.py')
    git(s6.root, 'commit', '-qm', 'test: 기록 없는 시험 편집')
    stray = git(s6.root, 'rev-parse', 'HEAD')
    e, out = s6.switch()
    check('L16 T 아닌 커밋이 행의 시험 파일을 바꿈 — exit 1', e == 1 and
          '0T 커밋이 아닌 %s 가 행의 시험 파일 tests/test_gate.py 를 바꾼다' % stray[:12] in out, out[-600:])
    s7 = Scene(tmp, 'l17')
    s7.w('web/app/other.py', 'CONNECTED = True')
    s7.w('config/settings.py', "INSTALLED_APPS = ['web']")
    git(s7.root, 'add', 'web/app/other.py', 'config/settings.py')
    git(s7.root, 'commit', '-qm', 'chore: 연결 설정(기준 판 뒤 · 슬라이스 기록 밖)')
    e, out = s7.switch()
    check('L17 기준 판 뒤 다른 커밋(연결 설정 꼴 — 시험 · 보호 분기 파일 밖)은 막지 않는다 — exit 0', e == 0 and
          (OK_LINE % (1, '2')) in out, out[-700:])
    s8 = Scene(tmp, 'l18')
    s8.w('web/app/other.py', 'FEATURE = 1')
    git(s8.root, 'add', 'web/app/other.py')
    git(s8.root, 'commit', '-qm', 'feat: 기능 슬라이스 커밋')
    feature = git(s8.root, 'rev-parse', 'HEAD')
    s8.w('tests/test_gate.py', *NEW_TEST, '# 둘째 T')
    git(s8.root, 'add', 'tests/test_gate.py')
    git(s8.root, 'commit', '-qm', 'test(web): 0T 둘째')
    t2 = git(s8.root, 'rev-parse', 'HEAD')
    s8.state(slices=[{'name': 'slice-0-debt', 'commits': [s8.t, t2],
                      'test_switch': {'state': 'verifying', 'commits': [s8.t, t2]}},
                     {'name': 'slice-1-gate', 'commits': [feature]}])
    e, out = s8.switch()
    check('L18 기록된 슬라이스 커밋이 T 보다 앞 — exit 1', e == 1 and
          '슬라이스 커밋 %s(slice-1-gate)가 T 보다 앞이다' % feature[:12] in out, out[-600:])
    s2 = Scene(tmp, 'l10', spec='# 명세\n\n## 슬라이스 0\n\n- 경로: `a.py` → `b.py`\n')
    e, out = s2.switch()
    check('L10 명세에 시험 전환 행 없음 — exit 1', e == 1 and '`## 슬라이스 0` 절에 `시험 전환:` 행이 없다' in out, out[-600:])
    s3 = Scene(tmp, 'l11', row='- 시험 전환: tests/test_gate.py::test_gate · 반례 test-switch/1.mutant.diff')
    e, out = s3.switch()
    check('L11 시험 전환 행 형식 오류 — exit 1', e == 1 and '`시험 전환:` 행 형식 오류' in out, out[-600:])
    e, out = s3.switch(folder='elsewhere')
    check('L12 산출물 폴더가 .dddjango-web/ 밖 — exit 1', e == 1 and '.dddjango-web/ 아래' in out, out[-600:])
    s4 = Scene(tmp, 'l13', row=ROW.replace('tests/test_gate.py', 'tests/test_new.py') % '`test-switch/1.mutant.diff`')
    git(s4.root, 'reset', '-q', '--hard', s4.snapshot)
    s4.w('tests/test_new.py', *NEW_TEST)
    git(s4.root, 'add', 'tests/test_new.py')
    git(s4.root, 'commit', '-qm', 'test(web): 0T — 새 시험 파일')
    s4.t = git(s4.root, 'rev-parse', 'HEAD')
    s4.state()
    e, out = s4.switch()
    check('L13 기준 판에 없는 시험 파일 — exit 1', e == 1 and 'tests/test_new.py 가 기준 판' in out, out[-600:])
    s5 = Scene(tmp, 'l14')
    s5.w('tests/test_gate.py', *NEW_TEST, '# 다듬음')
    second = s5.commit('test(web): 0T 둘째 — build-state 도 함께')
    s5.state({'state': 'verifying', 'commits': [s5.t, second], 'cancel_commits': [], 'evidence': ''},
             slices=[{'name': 'slice-0-debt', 'commits': [s5.t, second],
                      'test_switch': {'state': 'prepared', 'commits': [s5.t, second]}}])
    e, out = s5.switch()
    check('L14 T 커밋이 산출물 폴더(.dddjango-web/)를 함께 담음 — 따지지 않는다(치환 확인과 같은 기준) exit 0', e == 0 and
          (OK_LINE % (1, '2')) in out and (s5.evidence() or {}).get('t_head') == second, out[-600:])
    s5.w('tests/test_gate.py', *NEW_TEST, '# 셋째')
    s5.w('tests/helper.py', 'VALUE = 1')
    git(s5.root, 'add', 'tests/test_gate.py', 'tests/helper.py')
    git(s5.root, 'commit', '-qm', 'test(web): 0T 셋째 — 행 밖 파일도 함께')
    third = git(s5.root, 'rev-parse', 'HEAD')
    s5.state(slices=[{'name': 'slice-0-debt', 'commits': [s5.t, second, third],
                      'test_switch': {'state': 'verifying', 'commits': [s5.t, second, third]}}])
    e, out = s5.switch()
    check('L19 T 커밋이 행 밖 파일(web/ 밖)을 바꿈 — exit 1', e == 1 and
          'T 커밋 %s 가 행에 적힌 시험 파일 밖을 바꾼다 — tests/helper.py' % third[:12] in out, out[-600:])
    s10 = Scene(tmp, 'l20', row=ROW.replace('tests/test_gate.py', 'web/app/tests/test_gate.py') % '`test-switch/1.mutant.diff`')
    e, out = s10.switch()
    check('L20 시험 파일이 web/ 안 — exit 1(T 는 web/ 을 바꿀 수 없다)', e == 1 and
          '시험 파일은 web/ 밖 저장소 상대 경로의 시험 .py 다' in out, out[-600:])
    s9 = Scene(tmp, 'l15')
    (s9.root / 'tests' / 'test_gate__dddjango_switch_old.py').write_text('x = 1\n', encoding='utf-8')
    git(s9.root, 'add', 'tests/test_gate__dddjango_switch_old.py')
    git(s9.root, 'commit', '-qm', 'docs: 임시 자리를 먼저 차지한 파일')
    e, out = s9.switch()
    check('L15 옛 시험 임시 자리가 이미 있음 — exit 1', e == 1 and
          '옛 시험 임시 자리 tests/test_gate__dddjango_switch_old.py 가 이미 있다' in out, out[-600:])


# ====================================================================== P — 기록 플러그인(가짜 pytest 로 훅 직접 호출)

def bundle_probe(tmp):
    out = Path(tmp) / 'probe.jsonl'
    stub = types.ModuleType('pytest')
    stub.hookimpl = lambda **_kw: (lambda fn: fn)
    saved = sys.modules.get('pytest')
    sys.modules['pytest'] = stub
    os.environ['DDDJANGO_WEB_SWITCH_PROBE'] = str(out)
    try:
        spec = importlib.util.spec_from_file_location('switch_probe_under_test', SCRIPTS / 'src' / 'switch_probe.py')
        probe = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(probe)
    finally:
        os.environ.pop('DDDJANGO_WEB_SWITCH_PROBE', None)
        if saved is None:
            sys.modules.pop('pytest', None)
        else:
            sys.modules['pytest'] = saved
    item = types.SimpleNamespace(nodeid='tests/test_gate.py::test_gate')
    probe.pytest_collection_finish(types.SimpleNamespace(items=[item]))
    probe.pytest_collectreport(types.SimpleNamespace(failed=True, nodeid='tests/test_bad.py', longrepr='boom'))
    probe.pytest_collectreport(types.SimpleNamespace(failed=False, nodeid='tests', longrepr=None))
    try:
        assert 1 == 2
    except AssertionError:
        excinfo = types.SimpleNamespace(type=AssertionError, tb=sys.exc_info()[2])
    probe.pytest_runtest_makereport(item, types.SimpleNamespace(when='call', excinfo=excinfo))
    probe.pytest_runtest_makereport(item, types.SimpleNamespace(when='setup', excinfo=None))
    probe.pytest_runtest_logreport(types.SimpleNamespace(nodeid=item.nodeid, when='setup', outcome='passed'))
    rep = types.SimpleNamespace(nodeid=item.nodeid, when='call', outcome='failed')
    probe.pytest_runtest_logreport(rep)
    xf = types.SimpleNamespace(nodeid=item.nodeid, when='call', outcome='skipped', wasxfail='')
    probe.pytest_runtest_logreport(xf)
    probe.pytest_sessionfinish(None, 1)
    records = [json.loads(line) for line in out.read_text(encoding='utf-8').splitlines()]
    here = traceback.extract_tb(excinfo.tb)[-1]
    check('P1 기록 줄 — 수집 · 수집 오류 · 단계별 결과 · 예외 형과 프레임 · 세션 끝', [r['event'] for r in records] ==
          ['collected', 'collect_error', 'report', 'report', 'report', 'finish']
          and records[0]['nodeids'] == [item.nodeid] and records[1]['nodeid'] == 'tests/test_bad.py'
          and records[2]['exc'] is None and records[3]['exc']['type'] == 'builtins.AssertionError'
          and records[3]['exc']['frames'][-1] == [here.filename, here.lineno, here.name]
          and records[3]['wasxfail'] is False and records[4]['wasxfail'] is True and records[5]['exitstatus'] == 1,
          json.dumps(records, ensure_ascii=False)[:1500])


# ====================================================================== U — 무변(2.3.0 과 byte 동일)

def old_scripts(tmp):
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


def bundle_unchanged(tmp):
    if subprocess.run(['git', '-C', str(REPO), 'cat-file', '-e', BASELINE + '^{commit}'], capture_output=True,
                      env=ENV).returncode:
        print('SKIP U — 바탕 커밋 %s 이 이 저장소 이력에 없다(얕은 clone 등) — 무변 묶음(U)을 건너뛴다(실패로 세지 않는다)'
              % BASELINE)
        return
    old = old_scripts(Path(tmp) / 'old')
    check('U0 고치기 전 판(%s) scripts 를 풀 수 있다' % BASELINE, (old / 'refactor_audit.py').is_file())
    s = Scene(tmp, 'u')
    folder = s.root / '.dddjango-web' / 'debt'
    folder.mkdir(parents=True)
    run_script(old / 'backstop.py', s.root, '--debt-scan', '--refactor', '--json', folder / 'debt-g0.json')
    (folder / 'refactor-scope.md').write_text('## G0 2026-10-10 12:00\n- ⓐ 키: -\n- 요구 키: -\n', encoding='utf-8')
    (folder / 'build-state.json').write_text(json.dumps({'git_snapshot': s.snapshot, 'mode': 'refactor'}), encoding='utf-8')
    root = ['--project', s.root]
    cases = [
        ('standing', ['standing']),
        ('standing --gate', ['standing', '.dddjango-web/debt', '--gate']),
        ('residual', ['residual', '.dddjango-web/debt']),
        ('residual 인자 없음(하위 명령 사용법)', ['residual']),
        ('check 폴더 없음', ['--platform', 'claude', '--plugin-root', PLUGIN, 'check', 'nope']),
        ('self-test', ['--platform', 'claude', '--plugin-root', PLUGIN, '--self-test']),
    ]
    for name, args in cases:
        new = run_script(SCRIPTS / 'refactor_audit.py', *root, *args, cwd=s.root)
        before = run_script(old / 'refactor_audit.py', *root, *args, cwd=s.root)
        check('U %s — 고치기 전 판과 byte 동일' % name, new == before,
              '새 판 exit=%d\n%s\n옛 판 exit=%d\n%s' % (new[0], new[1][-700:], before[0], before[1][-700:]))
    outs = []
    for scripts in (old, SCRIPTS):
        audit = s.root / '.dddjango-web' / 'audit'
        shutil.rmtree(audit, ignore_errors=True)
        e, out = run_script(scripts / 'refactor_audit.py', *root, 'plan', 'web/app', '--debt',
                            '.dddjango-web/debt/debt-g0.json', '--out', '.dddjango-web/audit', cwd=s.root)
        outs.append((e, out, (audit / 'plan.md').read_bytes() if (audit / 'plan.md').exists() else None))
    check('U plan — 출력 · plan.md 가 고치기 전 판과 byte 동일(헛대조 아님)', outs[0] == outs[1] and outs[0][2],
          '%r\n%r' % (outs[0][:2], outs[1][:2]))
    # 주 사용법 줄(하위 명령 없음 · 알 수 없는 선택지 · 알 수 없는 하위 명령)은 하위 명령 목록을 싣는다 — 새 하위 명령
    # 이름 하나만 더해지고 그 밖은 byte 동일이어야 한다.
    corpus = ['--platform', 'claude', '--plugin-root', PLUGIN]   # 풀어 둔 옛 scripts 자리는 플랫폼을 구조로 판별하지 못한다
    for name, args in (('하위 명령 없음', corpus), ('알 수 없는 선택지', ['--bogus']), ('알 수 없는 하위 명령', ['bogus'])):
        new = run_script(SCRIPTS / 'refactor_audit.py', *root, *args, cwd=s.root)
        before = run_script(old / 'refactor_audit.py', *root, *args, cwd=s.root)
        stripped = new[1].replace(',switch-check', '').replace(", 'switch-check'", '')
        check('U %s — 사용법의 하위 명령 목록에 switch-check 하나만 더해짐(그 밖 byte 동일)' % name,
              new[0] == before[0] and 'switch-check' in new[1] and stripped == before[1],
              '새 판\n%s\n옛 판\n%s' % (new[1][-500:], before[1][-500:]))


# ====================================================================== X — 승인 행 판독은 한 곳

def _row_modules():
    """scripts 의 src 꾸러미를 이 프로세스에 싣는다(바이트코드는 쓰지 않는다)."""
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(SCRIPTS))
    try:
        from src import debt, subst, switch_check
    finally:
        sys.path.remove(str(SCRIPTS))
    return debt, subst, switch_check


def bundle_rows(tmp):
    """같은 행 묶음을 세 입구에 넣는다 — 치환 확인(subst.parse_spec_approvals) · switch-check(switch_check.parse_rows) ·
    plan --names(debt.parse_spec_methods). 한 입구가 받는 행을 다른 입구가 버리는 꼴이 0 이어야 한다."""
    debt, subst, switch_check = _row_modules()
    test, old, new = 'tests/test_gate.py::test_gate', 'web.app.view._render_page', 'web.app.view.page_view'
    branch, m1, m2 = 'web/app/view.py:11-12', 'test-switch/1.mutant.diff', 'test-switch/2.mutant.diff'

    def switch_row(head='', test=test, old=old, new=new, branch=branch, mutants=m1, arrow='→', tick=''):
        return '%s시험 전환: %s%s%s · 행위 %s%s%s %s %s%s%s · 보호 분기 %s%s%s · 반례 %s' % (
            head, tick, test, tick, tick, old, tick, arrow, tick, new, tick, tick, branch, tick,
            ' '.join(tick + m + tick for m in mutants.split()))

    def spec_of(line, section='## 슬라이스 0'):
        return '# 명세\n\n%s\n\n%s\n\n## 슬라이스 1\n' % (section, line)

    def read_switch(spec):
        """(치환 확인이 읽은 행, switch-check 가 읽은 행 또는 None, switch-check 사유)."""
        left = [(s.path, s.func, s.old, s.new) for s in subst.parse_spec_approvals(spec)[1]]
        try:
            right = [(r.test, r.func, r.old, r.new) for r in switch_check.parse_rows(spec)]
            why = ''
        except switch_check.Unverified as error:
            right, why = None, str(error)
        return left, right, why

    accepted = [
        ('맨 줄', switch_row()),
        ('`- ` 머리', switch_row('- ')),
        ('`* ` 머리', switch_row('* ')),
        ('들여쓴 `- ` 머리', switch_row('  - ')),
        ('칸마다 백틱', switch_row('- ', tick='`')),
        ('반례 둘', switch_row('- ', mutants='%s %s' % (m1, m2))),
        ('반례 둘 · 백틱', switch_row('- ', mutants='%s %s' % (m1, m2), tick='`')),
        ('web_test/ 미러 시험', switch_row(test='web_test/app/view_test.py::test_gate')),
        ('보호 분기 한 줄(17-17)', switch_row(branch='web/app/view.py:17-17')),
    ]
    for label, line in accepted:
        left, right, why = read_switch(spec_of(line))
        check('X1 받는 행(%s) — 치환 확인 · switch-check 둘 다 같은 행 하나' % label,
              len(left) == 1 and left == right, '치환 확인 %r\nswitch-check %r %s\n%s' % (left, right, why, line))
    rejected = [
        ('머리 뒤 공백 둘', switch_row('-  '), '형식 오류'),
        ('줄 전체를 백틱 한 쌍으로', '- `%s`' % switch_row(), '형식 오류'),
        ('칸 사이 백틱(→ 를 감쌈)', switch_row(arrow='`→`'), '형식 오류'),
        ('ASCII 화살표', switch_row(arrow='->'), '형식 오류'),
        ('보호 분기 줄 범위 없음', switch_row(branch='web/app/view.py:11'), '형식 오류'),
        ('보호 분기가 web 기준 상대 경로', switch_row(branch='app/view.py:11-12'), '보호 분기는 web/ 비시험 파일이다'),
        ('보호 분기가 시험 파일', switch_row(branch='tests/test_gate.py:5-6'), '보호 분기는 web/ 비시험 파일이다'),
        ('보호 분기 줄 범위 뒤집힘', switch_row(branch='web/app/view.py:12-11'), '줄 범위가 잘못됐다'),
        ('보호 분기 0행', switch_row(branch='web/app/view.py:0-3'), '줄 범위가 잘못됐다'),
        ('반례 없음', switch_row().rsplit(' · 반례', 1)[0], '형식 오류'),
        ('반례 절대 경로', switch_row(mutants='/tmp/1.mutant.diff'), '반례는 산출물 폴더 상대 경로다'),
        ('반례 .. 성분', switch_row(mutants='../1.mutant.diff'), '반례는 산출물 폴더 상대 경로다'),
        ('시험 파일이 web/ 안', switch_row(test='web/app/tests/test_gate.py::test_gate'), '시험 파일은 web/ 밖'),
        ('시험 파일이 아님', switch_row(test='scripts/run.py::main'), '시험 파일은 web/ 밖'),
        ('클래스 안 시험', switch_row(test='tests/test_gate.py::TestGate::test_gate'), '시험 파일은 web/ 밖'),
        ('시험 경로 글롭', switch_row(test='tests/test_*.py::test_gate'), '시험 파일은 web/ 밖'),
        ('시험 경로 ./ 머리', switch_row(test='./tests/test_gate.py::test_gate'), '시험 파일은 web/ 밖'),
        ('시험 경로 절대', switch_row(test='/tests/test_gate.py::test_gate'), '시험 파일은 web/ 밖'),
        ('시험 함수 이름에 한글', switch_row(test='tests/test_gate.py::test_게이트'), '형식 오류'),
        ('행위가 web. 경로가 아님', switch_row(old='app.view._render_page'), '행위는 web. 으로 시작하는 점 경로 쌍'),
        ('산문 줄', '시험 전환: 아래 두 함수를 0T 에서 먼저 바꾼다', '형식 오류'),
    ]
    for label, line, needle in rejected:
        left, right, why = read_switch(spec_of(line))
        check('X2 버리는 행(%s) — 치환 확인은 읽지 않고 switch-check 는 사유를 낸다' % label,
              left == [] and right is None and needle in why, '치환 확인 %r\nswitch-check %r %s\n%s' % (left, right, why, line))
    both = spec_of('%s\n%s' % (switch_row('- '), switch_row('-  ', test='tests/test_gate.py::test_other')))
    left, right, why = read_switch(both)
    check('X3 받는 행 + 꼴 어긋난 행 — 치환 확인은 받는 행만 · switch-check 는 멈춘다(exit 1 감)', len(left) == 1 and
          right is None and '형식 오류' in why, '%r %r %s' % (left, right, why))
    for label, spec in (('절 밖', spec_of(switch_row('- '), '## 다른 절')),
                        ('코드 울타리 안', spec_of('```\n%s\n```' % switch_row('- ')))):
        left, right, why = read_switch(spec)
        check('X4 %s 행 — 둘 다 읽지 않는다' % label, left == [] and right is None and '행이 없다' in why,
              '%r %r %s' % (left, right, why))
    same = spec_of(switch_row('- ', new=old))
    left, right, why = read_switch(same)
    try:
        subst._check_approvals([], subst.parse_spec_approvals(same)[1], [])
        conflict = ''
    except debt.DebtError as error:
        conflict = str(error)
    check('X5 옛 대상 = 새 대상 — 치환 확인 판정 불가 · switch-check 도 멈춘다', '옛 대상과 새 대상이 같다' in conflict
          and right is None and '옛 대상과 새 대상이 같다' in why, '%r | %r %s' % (conflict, right, why))

    o, n, t = 'web.home.vm.HomeVM.go', 'web.auth.vm.LoginVM.go', 'tests/web/test_home.py::test_a'

    def move_row(head='', old=o, new=n, tests=t, tick='', arrow='→'):
        return '%s메서드 이동: %s%s%s %s %s%s%s · 시험 %s' % (head, tick, old, tick, arrow, tick, new, tick,
                                                         ' '.join(tick + x + tick for x in tests.split()))

    moves = [
        ('맨 줄', move_row(), 1), ('`- ` 머리', move_row('- '), 1), ('`* ` 머리', move_row('* '), 1),
        ('들여쓴 머리', move_row('  - '), 1), ('백틱', move_row('- ', tick='`'), 1),
        ('시험 둘', move_row('- ', tests='%s tests/web/test_b.py::test_b' % t), 1),
        ('머리 뒤 공백 둘', move_row('-  '), 0), ('줄 전체 백틱', '- `%s`' % move_row(), 0),
        ('ASCII 화살표', move_row(arrow='->'), 0), ('시험 없음', move_row().rsplit(' 시험', 1)[0] + ' 시험', 0),
        ('뒤에 글', move_row() + ' (근거 아래)', 0), ('모듈 대문자', move_row(old='web.Home.vm.HomeVM.go'), 0),
        ('클래스 소문자', move_row(old='web.home.vm.homevm.go'), 0),
        ('클래스 이름에 비 ASCII', move_row(old='web.home.vm.Homé.go'), 0),
        ('메서드 이름에 비 ASCII', move_row(old='web.home.vm.HomeVM.gó'), 0),
        ('시험 함수 이름에 한글', move_row(tests='tests/web/test_home.py::test_가'), 0),
        ('시험 경로 글롭', move_row(tests='tests/web/test_*.py::test_a'), 0),
        ('클래스 안 시험', move_row(tests='tests/web/test_home.py::TestA::test_a'), 0),
        ('시험 파일이 아님', move_row(tests='scripts/run.py::main'), 0),
        ('시험 경로 절대', move_row(tests='/tests/web/test_home.py::test_a'), 0),
        ('시험 경로 .. 성분', move_row(tests='tests/../tests/test_home.py::test_a'), 0),
        ('시험 경로 ./ 머리', move_row(tests='./tests/web/test_home.py::test_a'), 0),
    ]
    for label, line, want in moves:
        spec = spec_of(line)
        plan = debt.parse_spec_methods(spec)
        approved = [(m.old, m.new) for m in subst.parse_spec_approvals(spec)[0]]
        check('X6 메서드 이동 행(%s) — plan --names · 치환 확인이 같은 행을 읽는다(%d)' % (label, want),
              plan == approved and len(plan) == want, 'plan --names %r\n치환 확인 %r\n%s' % (plan, approved, line))


    # 글 ↔ 도구 — Coordinator 문면의 0T 확인 명령은 self-test 가 도구의 하위 명령 · 선택지 이름과 대조한다(두 플랫폼)
    needle = "refactor_audit.py switch-check <산출물 폴더> --test-cmd '<그 프로젝트의 시험 명령 앞부분>'"
    codex = PLUGIN.parent / 'codex-dddjango-web'
    for platform, source, doc in (('claude', PLUGIN, 'commands/dddjango-web.md'),
                                  ('codex', codex, 'skills/dddjango-web/SKILL.md')):
        if not (source / doc).is_file():
            print('SKIP X7 %s — 그 플랫폼 문서가 옆에 없다(설치본) — 실패로 세지 않는다' % platform)
            continue
        copy = Path(tmp) / ('plug-' + platform)
        for part in ('commands', 'agents', 'skills'):
            if (source / part).is_dir():
                shutil.copytree(source / part, copy / part)
        args = ['--platform', platform, '--plugin-root', copy, '--self-test']
        e, out = run_script(SCRIPTS / 'refactor_audit.py', *args)
        check('X7 %s 문면 사본 self-test — green(0T 확인 명령 원문이 있다)' % platform, e == 0 and 'red 0' in out and
              needle in (copy / doc).read_text(encoding='utf-8'), out[-600:])
        original = (copy / doc).read_text(encoding='utf-8')
        for label, bad in (('선택지 이름이 다름', original.replace(needle, needle.replace('--test-cmd', '--test-command'))),
                           ('하위 명령 이름이 다름', original.replace(needle, needle.replace('switch-check', 'switch-verify'))),
                           ('명령 인자 표기가 다름', original.replace(needle, needle.replace('<산출물 폴더> ', '')))):
            (copy / doc).write_text(bad, encoding='utf-8')
            e, out = run_script(SCRIPTS / 'refactor_audit.py', *args)
            check('X7 %s 문면의 0T 확인 명령 — %s = red' % (platform, label), e == 2 and
                  '0T 확인 명령이 Coordinator 문면에 글자 그대로 없다' in out, out[-600:])
        (copy / doc).write_text(original, encoding='utf-8')

# ====================================================================== J — 이어 붙인 흐름(0T → switch-check → 기록 → 0C → 치환 확인)

J_VIEW = [
    "CHOICE_URL = '/choose/'",
    '',
    '',
    'class Response:',
    "    def __init__(self, status, location=''):",
    '        self.status = status',
    '        self.location = location',
    '',
    '',
    'def _render_page(request, employees, selected):',
    '    if employees > 1 and selected is None:',
    '        return Response(302, CHOICE_URL)',
    '    return Response(200)',
    '',
    '',
    'def page_view(request):',
    "    context = request.get('context')",
    '    if context is None:',
    '        return Response(302, CHOICE_URL)',
    "    return _render_page(request, context['employees'], context['selected'])",
]
J_VIEW_INLINED = J_VIEW[:9] + [
    'def page_view(request):',
    "    context = request.get('context')",
    '    if context is None:',
    '        return Response(302, CHOICE_URL)',
    "    if context['employees'] > 1 and context['selected'] is None:",
    '        return Response(302, CHOICE_URL)',
    '    return Response(200)',
]
# 기존 시험은 도움 함수를 함수 안 import 로 들여 직접 부른다 — 0T 는 그 함수의 준비 · 호출과 전용 import 만 바꾼다
J_OLD = [
    'def test_gate():',
    '    from web.app.view import _render_page',
    '    request = {}',
    '    response = _render_page(request, 2, None)',
    '    assert response.status == 302',
    "    assert response.location == '/choose/'",
]
J_NEW = [
    'def test_gate():',
    '    from web.app.view import page_view',
    '    request = {}',
    "    request['context'] = {'employees': 2, 'selected': None}",
    '    response = page_view(request)',
    '    assert response.status == 302',
    "    assert response.location == '/choose/'",
]
J_VM = ['class LegacyVM:', '    def greeting(self):', "        return 'hi'", '', '    def farewell(self):', "        return 'bye'",
        '', '', 'class GreetingVM:', '    def name(self):', "        return 'greeting'"]
J_VM_MOVED = ['class LegacyVM:', '    def farewell(self):', "        return 'bye'", '', '', 'class GreetingVM:',
              '    def name(self):', "        return 'greeting'", '', '    def greeting(self):', "        return 'hi'"]
J_GREET = ['from web.app.vm import LegacyVM', '', '', 'def test_greeting():', "    assert LegacyVM().greeting() == 'hi'"]
J_GREET_MOVED = ['from web.app.vm import GreetingVM', '', '', 'def test_greeting():',
                 "    assert GreetingVM().greeting() == 'hi'"]
J_MOVE_ROW = '- 메서드 이동: `web.app.vm.LegacyVM.greeting` → `web.app.vm.GreetingVM.greeting` · 시험 `tests/test_greeting.py::test_greeting`'
J_OK = OK_LINE % (2, '2 · 1')


def j_scene(tmp, name, **kw):
    return Scene(tmp, name, view=J_VIEW, old_test=J_OLD, new_test=J_NEW, mutants=(MUT_URL, MUT_IF), **kw)


def j_record(state, commits, cancels=(), evidence=''):
    return {'state': state, 'commits': list(commits), 'cancel_commits': list(cancels), 'evidence': evidence}


def j_state(s, commits, switch):
    zero = {'name': 'slice-0-debt', 'status': 'in-progress', 'commits': list(commits)}
    if switch is not None:
        zero['test_switch'] = switch
    s.state(slices=[zero, {'name': 'slice-1-gate', 'status': 'pending', 'commits': []}])


def j_subst(s, names=None):
    return run_script(SCRIPTS / 'backstop.py', s.root, '--subst-check', s.snapshot, 'HEAD', '--build', s.folder,
                      '--names', names or s.folder / 'design-spec.md', cwd=s.root)


def j_commit(s, message, *paths):
    git(s.root, 'add', '--', *paths)
    git(s.root, 'commit', '-qm', message)
    return git(s.root, 'rev-parse', 'HEAD')


def bundle_joined(tmp):
    evidence = RUN + '/test-switch/evidence.json'
    s = j_scene(tmp, 'j1', test_switch=j_record('prepared', []))
    t = s.t
    j_state(s, [t], j_record('prepared', [t]))
    e, out = j_subst(s)
    check('J1 0T 커밋 뒤(state=prepared) — 치환 확인이 0T 꼴을 받는다 exit 0', e == 0 and '[subst]' not in out, out[-900:])
    j_state(s, [t], j_record('verifying', [t]))
    e, out = s.switch()
    check('J2 switch-check — exit 0 · 행 결과 줄 · 증거', e == 0 and J_OK in out and (s.evidence() or {}).get('t_head') == t,
          out[-900:])
    j_state(s, [t], j_record('verified', [t], evidence=evidence))
    s.w('web/app/view.py', *J_VIEW_INLINED)
    c = j_commit(s, 'refactor(web): 0C', 'web/app/view.py')
    j_state(s, [t, c], j_record('verified', [t], evidence=evidence))
    e, out = j_subst(s)
    check('J3 0C(제품만) 뒤 · verified 기록 — 치환 확인 exit 0', e == 0 and '[subst]' not in out and
          'web/ 밖 변경 파일 1' in out, out[-900:])
    e, out = s.switch(cmd='/nonexistent/pytest-x')
    check('J4 0C 뒤 switch-check 다시 — «이미 검증됨» exit 0(시험을 돌리지 않는다)', e == 0 and '이미 검증됨' in out, out[-700:])
    # ⓐ verified 기록 없이 0C
    j_state(s, [t, c], None)
    e, out = j_subst(s)
    check('J5 ⓐ test_switch 기록 없이 0C — 0T 커밋이 보통 슬라이스 0 걸음으로 대조돼 exit 2', e == 2 and
          '[subst] tests/test_gate.py' in out and '0T 시험 전환' not in out, out[-900:])
    for name in ('prepared', 'verifying'):
        j_state(s, [t, c], j_record(name, [t]))
        e, out = j_subst(s)
        check('J5 ⓐ state=%s 인데 0C 커밋 — exit 2' % name, e == 2 and '0T 검증 전(state=%s)인데 0C 커밋 %s 가 있다'
              % (name, c[:12]) in out, out[-900:])
    e, out = s.switch()
    check('J5 ⓐ switch-check — 검증 기록 없이 T 뒤에 0C 가 있다 exit 1', e == 1 and '검증 전에는 0C 를 보내지 않는다' in out,
          out[-700:])
    # ⓑ T 뒤 시험을 더 고침
    s.w('tests/test_gate.py', *J_NEW[:-1])
    x = j_commit(s, 'test(web): 0C 뒤 시험을 더 고침 — 단언 하나 뺌', 'tests/test_gate.py')
    j_state(s, [t, c, x], j_record('verified', [t], evidence=evidence))
    e, out = j_subst(s)
    check('J6 ⓑ 0C 뒤 시험을 더 고침(단언 뺌) — 치환 확인 exit 2', e == 2 and
          '[subst] tests/test_gate.py' in out and '치환만으로 설명되지 않는다' in out and x[:12] in out, out[-900:])
    s2 = j_scene(tmp, 'j2')
    s2.w('tests/test_gate.py', *[line.replace("'employees': 2", "'employees': 3") for line in J_NEW])
    y = j_commit(s2, 'test(web): T 뒤 준비를 더 고침(T 로 기록하지 않음)', 'tests/test_gate.py')
    j_state(s2, [s2.t], j_record('verifying', [s2.t]))       # y 는 어느 슬라이스에도 적지 않았다(기록 없는 커밋)
    e, out = s2.switch()
    check('J6 ⓑ T 뒤(0C 앞) T 아닌 커밋이 시험을 더 고침 — switch-check exit 1', e == 1 and
          '0T 커밋이 아닌 %s 가 행의 시험 파일 tests/test_gate.py 를 바꾼다' % y[:12] in out, out[-700:])
    e, out = j_subst(s2)
    check('J6 ⓑ 같은 꼴 — 치환 확인 exit 2', e == 2 and '[subst] tests/test_gate.py' in out, out[-900:])
    # ⓒ 0T 취소
    s3 = j_scene(tmp, 'j3')
    git(s3.root, 'revert', '--no-edit', s3.t)
    x3 = git(s3.root, 'rev-parse', 'HEAD')
    j_state(s3, [s3.t, x3], j_record('cancelled', [s3.t], [x3]))
    e, out = j_subst(s3)
    check('J7 ⓒ 0T 취소(역 커밋 · cancel_commits) — 치환 확인이 T + 취소를 빼고 exit 0', e == 0 and '[subst]' not in out,
          out[-900:])
    e, out = s3.switch()
    check('J7 ⓒ switch-check — 취소된 0T 는 확인하지 않는다 exit 1', e == 1 and 'test_switch.state 가 cancelled' in out,
          out[-600:])
    untouched(s3, 'J7 ⓒ switch-check')
    # 모순 상태 — 확인이 끊겨 반례 · 옛 시험 임시 파일이 남았는데 취소 커밋을 얹고 cancelled 로 적음
    s4 = j_scene(tmp, 'j4')
    s4.switch(env={'FAKE_KILL_WHEN': "'/elsewhere/'"})
    pending = (s4.state_json() or {}).get('pending') or []
    old_tmp = [p['path'] for p in pending if p.get('kind') == 'old-test']
    check('J8 픽스처 자체 — 끊긴 확인이 반례 · 옛 시험 임시 파일을 남겼다', {p.get('kind') for p in pending} ==
          {'mutant', 'old-test'} and "'/elsewhere/'" in s4.read('web/app/view.py'), json.dumps(pending, ensure_ascii=False))
    git(s4.root, 'revert', '--no-edit', s4.t)
    x4 = git(s4.root, 'rev-parse', 'HEAD')
    j_state(s4, [s4.t, x4], j_record('cancelled', [s4.t], [x4]))
    e, out = j_subst(s4)
    check('J8 모순 상태(임시 변경이 남은 채 cancelled) — 치환 확인은 통과하지 않는다 exit 1(미커밋 web/ 밖 변경)', e == 1 and
          '미커밋 web/ 밖 변경' in out and bool(old_tmp) and old_tmp[0] in out, out[-700:])
    e, out = s4.switch()
    check('J8 switch-check — 먼저 복구한 뒤 «취소된 0T 는 확인하지 않는다» exit 1', e == 1 and
          '[switch] 복구 — web/app/view.py 반례 되돌림' in out and '옛 시험 임시 파일 지움' in out and
          out.index('[switch] 복구') < out.index('test_switch.state 가 cancelled'), out[-900:])
    check('J8 복구 뒤 — 작업 트리 깨끗 · 남은 임시 변경 0 · 제품이 HEAD 그대로', s4.clean() == '' and
          (s4.state_json() or {}).get('pending') == [] and "'/elsewhere/'" not in s4.read('web/app/view.py'),
          '%r %r' % (s4.clean(), s4.state_json()))
    e, out = j_subst(s4)
    check('J8 복구 뒤 치환 확인 — T + 취소를 빼고 exit 0', e == 0 and '[subst]' not in out, out[-700:])
    # ⓓ 메서드 이동 행과 시험 전환 행이 한 명세에
    rows = '%s\n%s' % (ROW % '`test-switch/1.mutant.diff` `test-switch/2.mutant.diff`', J_MOVE_ROW)
    s5 = j_scene(tmp, 'j5', row=rows, extra={'web/app/vm.py': J_VM, 'tests/test_greeting.py': J_GREET})
    e, out = s5.switch()
    check('J9 ⓓ 두 행이 같이 든 명세 — switch-check exit 0(메서드 이동 행은 건드리지 않는다)', e == 0 and J_OK in out, out[-900:])
    s5.w('web/app/view.py', *J_VIEW_INLINED)
    s5.w('web/app/vm.py', *J_VM_MOVED)
    s5.w('tests/test_greeting.py', *J_GREET_MOVED)
    c5 = j_commit(s5, 'refactor(web): 0C — 도움 함수 넣기 + 메서드 이동', 'web/app/view.py', 'web/app/vm.py',
                  'tests/test_greeting.py')
    j_state(s5, [s5.t, c5], j_record('verified', [s5.t], evidence=evidence))
    e, out = j_subst(s5)
    check('J9 ⓓ 치환 확인 — 두 행이 모두 서서 exit 0', e == 0 and '[subst]' not in out and
          '[info] 메서드 이동 web.app.vm.LegacyVM.greeting → web.app.vm.GreetingVM.greeting — 승인 시험 함수 1' in out and
          '[info] 메서드 이동 자리 정규화 tests/test_greeting.py — 1곳' in out and 'web/ 밖 변경 파일 2' in out, out[-1200:])
    spec = s5.read(RUN + '/design-spec.md')
    only_switch = s5.tmp / 'j5-only-switch.md'
    only_switch.write_text('\n'.join(l for l in spec.split('\n') if '메서드 이동:' not in l), encoding='utf-8')
    only_move = s5.tmp / 'j5-only-move.md'
    only_move.write_text('\n'.join(l for l in spec.split('\n') if '시험 전환:' not in l), encoding='utf-8')
    e, out = j_subst(s5, only_switch)
    check('J9 ⓓ 대조 — 메서드 이동 행을 빼면 그 시험이 어긋난다 exit 2', e == 2 and
          '[subst] tests/test_greeting.py' in out and '[subst] tests/test_gate.py' not in out, out[-900:])
    e, out = j_subst(s5, only_move)
    check('J9 ⓓ 대조 — 시험 전환 행을 빼면 0T 커밋이 어긋난다 exit 2', e == 2 and 'tests/test_gate.py' in out and
          '[subst] tests/test_greeting.py' not in out, out[-900:])


def main():
    bundles = [bundle_unchanged, bundle_normal, bundle_bypass, bundle_reject, bundle_unverified, bundle_mismatch,
               bundle_crash, bundle_after, bundle_dirty, bundle_lifecycle, bundle_probe, bundle_rows, bundle_joined]
    only = set(sys.argv[1:])
    for bundle in bundles:
        if only and bundle.__name__[len('bundle_'):] not in only:
            continue
        with tempfile.TemporaryDirectory(prefix='web231s-') as tmp:
            try:
                bundle(Path(tmp))
            except Exception as error:  # noqa: BLE001 — 묶음이 죽어도 실패로 세고 다음 묶음을 돈다
                check('%s — 묶음 실행 오류' % bundle.__name__, False,
                      '%s: %s\n%s' % (type(error).__name__, error, traceback.format_exc()[-1200:]))
    print('2.3.1 switch-check 픽스처: PASS %d / FAIL %d' % (PASS, FAIL))
    return bool(FAIL)


if __name__ == '__main__':
    sys.exit(main())
