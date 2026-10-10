#!/usr/bin/env python3
"""계약 C: 실제 CLI · 임시 저장소 · 2.3.0 byte 대조. 재현 장면(옛 배치 파일 셋 · G0 동결본 · refactor-scope 변형)은
이 파일이 임시 폴더에 스스로 만든다 — 저장소 밖 파일을 읽지 않는다. 바탕 커밋이 이력에 없으면(얕은 clone 등) 2.3.0 과의
byte 대조만 건너뛰고 건너뛴 사실을 출력한다(실패로 세지 않는다)."""
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / 'dddjango-web/scripts'
BASE = 'f349f878'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
WHEN = '2026-10-10 23:00'
AUDIT = '20261010-230000'
# 재현 장면 — 옛 배치 파일 셋(빚 C1 · C2 = legacy 폴더 · C3 = other 폴더)과 그 G0 동결본 · refactor-scope.md 변형 v1 ~ v5.
# 픽스처가 임시 폴더에 스스로 만든다(저장소 밖 파일을 읽지 않는다).
REPRO_WEB = {
    '__init__.py': '',
    'legacy/alpha.py': 'def a() -> int:\n    return 1\n',
    'legacy/beta.py': 'def b() -> int:\n    return 2\n',
    'other/gamma.py': 'def c() -> int:\n    return 3\n',
}
REPRO_G0 = '''{
  "counts": {
    "ST0|legacy/alpha.py": 1,
    "ST0|legacy/beta.py": 1,
    "ST0|other/gamma.py": 1
  },
  "dirty": false,
  "files": [
    "__init__.py",
    "legacy/alpha.py",
    "legacy/beta.py",
    "other/gamma.py"
  ],
  "findings": [
    {
      "check": "ST0",
      "folder": "legacy",
      "key": "ST0|legacy/alpha.py",
      "line": null,
      "message": "표준 트리 밖 옛 배치 파일 — 층 판정 불가 레거시(슬라이스 0 이 새 배치로 옮긴다)",
      "path": "legacy/alpha.py"
    },
    {
      "check": "ST0",
      "folder": "legacy",
      "key": "ST0|legacy/beta.py",
      "line": null,
      "message": "표준 트리 밖 옛 배치 파일 — 층 판정 불가 레거시(슬라이스 0 이 새 배치로 옮긴다)",
      "path": "legacy/beta.py"
    },
    {
      "check": "ST0",
      "folder": "other",
      "key": "ST0|other/gamma.py",
      "line": null,
      "message": "표준 트리 밖 옛 배치 파일 — 층 판정 불가 레거시(슬라이스 0 이 새 배치로 옮긴다)",
      "path": "other/gamma.py"
    }
  ],
  "head": "b69e2e0f8b222fbf9955ac907c4334881051d2ce",
  "ids": {
    "C1": "ST0|legacy/alpha.py",
    "C2": "ST0|legacy/beta.py",
    "C3": "ST0|other/gamma.py"
  },
  "mode": "feature",
  "scanned_at": "2026-10-10T20:07:43+09:00",
  "scanner": {
    "checks": "e49c83776ff9faf6",
    "keys": "st-folder-to-file",
    "plugin": "2.2.6"
  },
  "schema": "dddjango-web-debt/1"
}
'''
REPRO_VARIANTS = (
    # v1
    '''# refactor-scope (측정용)

## G0 2026-10-10 20:08
C1 · 결정 = ⓐ · 사유 = 측정 · 출처 = 본인 직접(2026-10-10 20:08)
C2 · 결정 = 플러그인 결함(수리 대기 · 이 정리만 빼고 진행) · 출처 = 본인 직접(2026-10-10 20:08)
C3 · 결정 = 다른 요청 몫 · 출처 = 본인 직접(2026-10-10 20:08)
ⓐ 키: C1
요구 키: -
''',
    # v2
    '''# refactor-scope (측정용)

## G0 2026-10-10 20:08
C1 C2 · 결정 = ⓐ · 사유 = 측정 · 출처 = 본인 직접(2026-10-10 20:08)
ⓐ 키: C1 C2
요구 키: -

## ⓐ 재상정 2026-10-10 20:09
C2 · web/legacy/beta.py · ST0 · 처분 = 플러그인 결함 · 결정 = 본인 직접(2026-10-10 20:09)
재상정 키: C2
''',
    # v3
    '''# refactor-scope (측정용)

## G0 2026-10-10 20:08
C1 · 결정 = ⓐ · 출처 = 본인 직접(2026-10-10 20:08)
ⓐ 키: C1
요구 키: -

## G0 재승인 2026-10-10 20:09
C2 · 결정 = 플러그인 수리 대기 · C3 · 결정 = 다른 요청 몫 · 출처 = 본인 직접(2026-10-10 20:09)
ⓐ 키: -
요구 키: -
수리 대기 키: C2
다른 요청 몫 키: C3
''',
    # v4
    '''# refactor-scope (측정용)

## G0 2026-10-10 20:08
C1 · 결정 = ⓐ · 출처 = 본인 직접(2026-10-10 20:08)
ⓐ 키: C1
요구 키: -

## G0 수리 대기 2026-10-10 20:09
C2 · 결정 = 플러그인 수리 대기
''',
    # v5
    '''# refactor-scope (측정용)

## G0 2026-10-10 20:08
C1 · 결정 = ⓐ · 출처 = 본인 직접(2026-10-10 20:08)
ⓐ 키: C1
요구 키: -

## G0 재승인 2026-10-10 20:09
C2 · 결정 = 플러그인 수리 대기 · 출처 = 본인 직접(2026-10-10 20:09)
''',
)
# 시간만 고정한다. 양쪽 CLI·git·스캔·JSON 직렬화는 실제 구현을 실행한다.
RUN = '''
import datetime, importlib.util, pathlib, sys
scripts, entry, *args = sys.argv[1:]
sys.path.insert(0, scripts)
class Clock(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        value = cls(2026, 10, 10, 22, 0, tzinfo=datetime.timezone.utc)
        return value.astimezone(tz) if tz else value.replace(tzinfo=None)
from src import debt
debt.datetime = Clock
spec = importlib.util.spec_from_file_location('fixture_cli', pathlib.Path(scripts) / entry)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
if hasattr(mod, 'datetime'): mod.datetime = Clock
sys.exit(mod.main(args))
'''


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def git(project, *args):
    return subprocess.check_output(['git', '-C', str(project), *args], env=ENV, stderr=subprocess.PIPE).decode().strip()


def commit(project):
    git(project, 'add', 'web')
    git(project, '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'fixture')
    return git(project, 'rev-parse', 'HEAD')


def decision(key, kind='일반', source='본인 직접(2026-10-10 23:00)', extra=None):
    fields = {'일반': '', '수리 대기': ' · 수리 = FIX1 · 충돌 증거 = rules.py:1 · web/legacy/beta.py:1',
              '다른 요청': ' · 담당 요청 = 요청1 · 레인1 · 폴더1 · 재개 조건 = 착륙 확인'}
    return f'- 결정 줄: {key} · 결정 = ⓑ · 사유 = 이번 요청에서 미룸 · 미룸 유형 = {kind}' + (
        fields[kind] if extra is None else extra) + f' · 출처 = {source}\n'


def section(a='-', required='-', body='', kind='G0', meaning=None):
    text = f'## {kind} {WHEN}\nⓐ 키: {a}\n요구 키: {required}\n'
    if meaning is not None:
        text += f'의미 ⓐ 키: {meaning}\n'
        if kind == 'G0':
            text += f'의미 audit: {AUDIT}\n'
    return text + body


def resubmit(keys, body='', meaning='-'):
    return f'## ⓐ 재상정 {WHEN}\n재상정 키: {keys}\n의미 재상정 키: {meaning}\n' + body


class ContractC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='web231-debt-')
        cls.tmp = Path(cls.temp.name)
        cls.old = None
        if subprocess.run(['git', 'cat-file', '-e', BASE + '^{commit}'], cwd=ROOT, env=ENV, capture_output=True).returncode:
            print('SKIP 2.3.0 byte 대조 — 바탕 커밋 %s 이 이 저장소 이력에 없다(얕은 clone 등) — 그 대조만 건너뛴다(실패로 세지 '
                  '않는다)' % BASE, file=sys.stderr)
            return
        archive = subprocess.check_output(['git', 'archive', BASE, 'dddjango-web/scripts',
                                          'dddjango-web/.claude-plugin/plugin.json'], cwd=ROOT, env=ENV)
        with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
            bundle.extractall(cls.tmp / 'baseline', filter='data')
        cls.old = cls.tmp / 'baseline/dddjango-web/scripts'

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.p = self.tmp / self.id().split('.')[-1]
        self.p.mkdir()
        for rel, body in REPRO_WEB.items():
            write(self.p / 'web' / rel, body)
        git(self.p, 'init', '-q')
        self.anchor = commit(self.p)
        self.f = self.p / '.dddjango-web/run'
        self.f.mkdir(parents=True)
        frozen = json.loads(REPRO_G0)
        frozen.update(head=self.anchor, scanned_at='2026-10-10T20:07:43+09:00')
        # 재현 동결본의 판도 보존한다. 기존 판 바뀜 알림까지 양쪽에서 대조한다.
        write(self.f / 'debt-g0.json', json.dumps(frozen))

    def cli(self, entry, *args, old=False):
        if old and self.old is None:
            self.skipTest('바탕 커밋 %s 없음 — 2.3.0 byte 대조 건너뜀' % BASE)
        return subprocess.run([sys.executable, '-B', '-c', RUN, str(self.old if old else SCRIPTS), entry,
                               *map(str, args)], cwd=self.p, env=ENV, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT)

    def c(self, text, code=0, want='', absent='', old=False):
        write(self.f / 'refactor-scope.md', text)
        out = self.cli('backstop.py', self.p, '--debt-residual', self.f, old=old)
        self.assertEqual(out.returncode, code, out.stdout.decode())
        self.assertIn(want.encode(), out.stdout)
        if absent:
            self.assertNotIn(absent.encode(), out.stdout)
        return out

    def m_setup(self):
        data = json.loads((self.f / 'debt-g0.json').read_text())
        data['mode'] = 'refactor'
        write(self.f / 'debt-g0.json', json.dumps(data))
        write(self.f / 'build-state.json', json.dumps({'git_snapshot': self.anchor}))
        audit = self.f / 'audit' / AUDIT
        write(audit / 'plan.md', '- 단위: `web/legacy`\n## 범위 파일\n- `web/legacy/alpha.py`\n'
              '## 범위 안 키\n- 없음\n## 줄 편집\n- 없음\n## 참조 치환 줄\n- 없음\n'
              '## 파견\n| ui-01.md | ui | 01 | reviewer |\n')
        write(audit / 'ui-01.md', '| 1 | 규칙 | - | web/legacy/alpha.py:1 | 위반 | 가능 | 파일 | - |\n'
              '| 2 | 규칙 | - | web/legacy/beta.py:1 | 위반 | 가능 | 파일 | - |\n')
        write(audit / 'verdict-final.md', '| M1 | ui-01#1 | 의미 위반 | 근거 | web/legacy/alpha.py:1 |\n'
              '| M2 | ui-01#2 | 의미 위반 | 근거 | web/legacy/beta.py:1 |\n')

    def m(self, text, code=0, want='', finalize=None):
        write(self.f / 'refactor-scope.md', text)
        args = ['residual', self.f]
        if finalize:
            args += ['--finalize', finalize]
        out = self.cli('refactor_audit.py', *args)
        self.assertEqual(out.returncode, code, out.stdout.decode())
        self.assertIn(want.encode(), out.stdout)
        return out

    def test_c_all_types_report_and_outside_exclusion(self):
        self.c(section(body=decision('C1') + decision('C2', '수리 대기') + decision('C3', '다른 요청') +
                       'ⓑ 키: C1\nⓑ 수리 대기 키: C2\nⓑ 다른 요청 키: C3\n'), want=
               'legacy 잔존 ⓑ 3(일반 1 · 수리 대기 1 · 다른 요청 1)')
        out = self.c(section(a='C1', body=decision('C2', '수리 대기') + decision('C3', '다른 요청') +
                             'ⓑ 수리 대기 키: C2\nⓑ 다른 요청 키: C3\n'), 2,
                     'legacy 잔존 ⓑ(수리 대기) C2 ST0|legacy/beta.py — 발견 1(해소 아님 · 보고만)',
                     '범위 밖 남은 빚 — 폴더')
        self.assertIn('legacy 잔존 ⓑ(다른 요청) C3'.encode(), out.stdout)

    def test_c_plain_old_prose_ignored(self):
        text = section(a='C1', body='ⓑ 키: 다음 요청에서 논의\nⓑ 수리 대기 키: 옛 산문\n')
        new = self.c(text, 2, absent='legacy 잔존 ⓑ')
        old = self.c(text, 2, old=True)
        self.assertEqual((new.returncode, new.stdout), (old.returncode, old.stdout))

    def test_c_resubmit_then_defer(self):
        text = section(a='C1 C2') + resubmit('C2', decision('C2', '수리 대기') + 'ⓑ 수리 대기 키: C2\n')
        self.c(text, 2, '재상정 제외 1', absent='범위 밖 남은 빚 — 폴더')

    def test_c_readopt_and_type_change(self):
        first = section(body=decision('C2') + 'ⓑ 키: C2\n')
        self.c(first + section(body=decision('C2', '다른 요청') + 'ⓑ 다른 요청 키: C2\n',
                               kind='G0 재승인'), want='legacy 잔존 ⓑ 1(일반 0 · 수리 대기 0 · 다른 요청 1)')
        self.c(first + section(a='C2', kind='G0 재승인'), 2, '잔존 ⓐ C2',
               'legacy 잔존 ⓑ(일반) C2')
        self.c(first + section(required='C2', kind='G0 재승인'), 2, '잔존 요구 C2')

    def test_c_latest_g0_increment_and_fences(self):
        old = section(body=decision('C99') + 'ⓑ 키: C99\n')
        text = old + section(body=decision('C2') + 'ⓑ 키: C2\n') + section(kind='G0 재승인')
        self.c(text, want='legacy 잔존 ⓑ 1(일반 1')
        self.c(section(a='C1', body='```\n' + decision('C1') + 'ⓑ 키: C1\n```\n'), 2,
               '잔존 ⓐ C1', 'legacy 잔존 ⓑ')
        self.c(section(a='C1') + '## 기타\n' + decision('C1') + 'ⓑ 키: C1\n', 2,
               '잔존 ⓐ C1', 'legacy 잔존 ⓑ')

    def test_c_activation_is_per_section_and_stop_is_ignored(self):
        text = section(body='ⓑ 키: 다음 요청에서 논의\n') + section(
            body=decision('C2') + 'ⓑ 키: C2\n', kind='G0 재승인')
        self.c(text, want='legacy 잔존 ⓑ 1(일반 1')
        self.c(text + section(kind='G0 정지', body=decision('C99') + 'ⓑ 키: C99\n'),
               want='legacy 잔존 ⓑ 1(일반 1')

    def test_c_readopt_releases_movement_dependency(self):
        text = section(body=decision('C2') + 'ⓑ 키: C2\n') + section(a='C2', kind='G0 재승인')
        write(self.f / 'design-spec.md', '## 슬라이스 0\n경로: legacy/beta.py → moved/beta.py\n')
        self.c(text, 2, '잔존 ⓐ C2', 'legacy 잔존 ⓑ(일반) C2')

    def test_c_source_user_original(self):
        self.c(section(body=decision('C2', source='사용자 원문(scope.md:1)') + 'ⓑ 키: C2\n'),
               want='legacy 잔존 ⓑ(일반) C2')

    def test_resubmit_same_section_overlap_is_rejected(self):
        self.c(section(a='C2') + resubmit('C2', 'ⓐ 키: C2\n' + decision('C2') + 'ⓑ 키: C2\n'),
               1, '판정 불가')
        self.m_setup()
        self.m(section(meaning='M2') + resubmit('-', '의미 ⓐ 키: M2\n' + decision('M2') +
                                               '의미 ⓑ 키: M2\n', meaning='M2'), 1, '실행 불능')

    def test_c_negative_table(self):
        cases = [
            ('live', section(a='C1') + section(body=decision('C1') + 'ⓑ 키: C1\n', kind='G0 재승인')),
            ('same', section(a='C1', body=decision('C1') + 'ⓑ 키: C1\n')),
            ('required', section(required='C1') + resubmit('C1') + section(
                body=decision('C1') + 'ⓑ 키: C1\n', kind='G0 재승인')),
            ('unknown', section(body=decision('C99') + 'ⓑ 키: C99\n')),
            ('duplicate', section(body=decision('C2') + 'ⓑ 키: C2\nⓑ 키: C2\n')),
            ('overlap', section(body=decision('C2') + 'ⓑ 키: C2\nⓑ 수리 대기 키: C2\n')),
            ('type', section(body=decision('C2', '수리 대기') + 'ⓑ 키: C2\n')),
            ('missing_decision', section(body=decision('C3') + 'ⓑ 키: C2\n')),
            ('missing_reason', section(body=decision('C2').replace('사유 = 이번 요청에서 미룸', '사유 = ') + 'ⓑ 키: C2\n')),
            ('proxy', section(body=decision('C2', source='대리 판단(담당 배정)') + 'ⓑ 키: C2\n')),
            ('assigned', section(body=decision('C2', source='담당 배정') + 'ⓑ 키: C2\n')),
            ('schedule', section(body=decision('C2', source='일정') + 'ⓑ 키: C2\n')),
            ('other_lane', section(body=decision('C2', source='다른 레인 처분') + 'ⓑ 키: C2\n')),
            ('source_suffix', section(body=decision('C2', source='본인 직접인 듯') + 'ⓑ 키: C2\n')),
            ('repair_id', section(body=decision('C2', '수리 대기', extra=' · 충돌 증거 = rules.py:1 · code.py:1') + 'ⓑ 수리 대기 키: C2\n')),
            ('repair_evidence', section(body=decision('C2', '수리 대기', extra=' · 수리 = FIX1 · 충돌 증거 = rules.py:1') + 'ⓑ 수리 대기 키: C2\n')),
            ('request', section(body=decision('C2', '다른 요청', extra=' · 재개 조건 = 착륙') + 'ⓑ 다른 요청 키: C2\n')),
            ('resume', section(body=decision('C2', '다른 요청', extra=' · 담당 요청 = 요청1') + 'ⓑ 다른 요청 키: C2\n')),
            ('resubmit_subset', section() + resubmit('C1', decision('C2', '수리 대기') + 'ⓑ 수리 대기 키: C2\n')),
            ('wrong_id_form', section(body=decision('C2') + 'ⓑ 키: M2\n')),
        ]
        for name, text in cases:
            with self.subTest(name=name):
                self.c(text, 1, '판정 불가')

    def test_c_undeferrable_and_movement(self):
        text = section(body=decision('C2') + 'ⓑ 키: C2\n')
        frozen = json.loads((self.f / 'debt-g0.json').read_text())
        frozen['findings'][1]['undeferrable'] = True
        write(self.f / 'debt-g0.json', json.dumps(frozen))
        self.c(text, 1, '미룰 수 없음')
        frozen['findings'][1].pop('undeferrable')
        write(self.f / 'debt-g0.json', json.dumps(frozen))
        for path in ('legacy/beta.py', 'legacy/'):
            write(self.f / 'design-spec.md', f'## 슬라이스 0\n경로: {path} → moved/{"" if path.endswith("/") else "beta.py"}\n')
            self.c(text, 1, '이동 묶음 의존')
        (self.f / 'design-spec.md').unlink()
        (self.p / 'web/moved').mkdir()
        git(self.p, 'mv', 'web/legacy/beta.py', 'web/moved/beta.py')
        self.c(text, 1, '이동 묶음 의존')

    def test_c_missing_current_key_is_not_solved(self):
        (self.p / 'web/legacy/beta.py').unlink()
        self.c(section(body=decision('C2') + 'ⓑ 키: C2\n'), want='legacy 잔존 ⓑ 0(일반 0')
        self.assertNotIn('solved', json.loads((self.f / 'debt-g2.json').read_text()))

    def test_c_gate_does_not_exempt_new_violation(self):
        self.c(section(body=decision('C2') + 'ⓑ 키: C2\n'))
        out = self.cli('backstop.py', self.p, '--diff-base', self.anchor, '--slice-end')
        # 새 파일에 같은 미룸을 주장해도 일반/슬라이스 끝 게이트는 scope 를 읽지 않는다.
        write(self.p / 'web/new_legacy/new.py', 'x = 1\n')
        git(self.p, 'add', 'web/new_legacy/new.py')
        for opts in ([], ['--slice-end']):
            out = self.cli('backstop.py', self.p, '--diff-base', self.anchor, *opts)
            self.assertEqual(out.returncode, 2, out.stdout.decode())
            self.assertIn(b'[ST0]', out.stdout)

    def test_m_early_finalize_and_nonstorage(self):
        self.m_setup()
        text = section(meaning='-', body=decision('M1', '수리 대기') + '의미 ⓑ 수리 대기 키: M1\n')
        self.m(text, want='legacy 잔존 ⓑ(수리 대기) M1')
        out_dir = next((self.f / 'residual').iterdir())
        self.assertEqual(json.loads((out_dir / 'result.json').read_text())['solved'], {})
        self.m(text, want='legacy 잔존 ⓑ 1(일반 0 · 수리 대기 1', finalize=out_dir.name)
        self.assertEqual(json.loads((out_dir / 'result.json').read_text())['solved'], {})
        bad = text.replace('본인 직접(', '대리 판단(')
        self.m(bad, 1, '실행 불능')
        self.m(bad, 1, '실행 불능', finalize=out_dir.name)

    def test_m_readopt_and_type_change(self):
        self.m_setup()
        first = section(meaning='M1') + resubmit('-', decision('M1') + '의미 ⓑ 키: M1\n', meaning='M1')
        self.m(first, want='legacy 잔존 ⓑ(일반) M1')
        write(self.p / 'web/legacy/alpha.py', 'value = 2\n')
        text = first + section(kind='G0 재승인', meaning='M1')
        self.m(text, want='리뷰어 확인 대상 1')
        self.m(first + section(kind='G0 재승인', meaning='-', body=decision('M1', '다른 요청') +
                              '의미 ⓑ 다른 요청 키: M1\n'), want='legacy 잔존 ⓑ 1(일반 0 · 수리 대기 0 · 다른 요청 1)')

    def test_m_readopt_does_not_carry_predeferral_solved(self):
        import hashlib
        self.m_setup()
        write(self.p / 'web/legacy/alpha.py', 'value = 2\n')
        prior = self.f / 'residual/20261010-2100/result.json'
        fingerprint = hashlib.sha256((self.p / 'web/legacy/alpha.py').read_bytes()).hexdigest()[:16]
        write(prior, json.dumps({'stamp': '20261010-2100', 'audit': AUDIT, 'snapshot': self.anchor,
                                 'solved': {'M1': {'web/legacy/alpha.py': fingerprint}}}))
        text = section(meaning='-', body=decision('M1') + '의미 ⓑ 키: M1\n') + section(
            kind='G0 재승인', meaning='M1')
        out = self.m(text, want='리뷰어 확인 대상 1')
        self.assertNotIn('해소 유지'.encode(), out.stdout)

    def test_m_movement_and_undeferrable(self):
        self.m_setup()
        text = section(meaning='-', body=decision('M2') + '의미 ⓑ 키: M2\n')
        write(self.f / 'design-spec.md', '## 슬라이스 0\n경로: legacy/beta.py → moved/beta.py\n')
        self.m(text, 1, '이동 묶음 의존')
        self.m(text + section(kind='G0 재승인', meaning='M2'), 2, 'M_m=1')
        (self.f / 'design-spec.md').unlink()
        frozen = json.loads((self.f / 'debt-g0.json').read_text())
        frozen['findings'][1]['undeferrable'] = True
        write(self.f / 'debt-g0.json', json.dumps(frozen))
        audit = self.f / 'audit' / AUDIT
        write(audit / 'ui-01.md', (audit / 'ui-01.md').read_text().replace('| 파일 | - |', '| 파일 | C2 |'))
        self.m(text, 1, '미룰 수 없음')

    def test_m_merged_origin_movement_is_checked(self):
        self.m_setup()
        audit = self.f / 'audit' / AUDIT
        write(audit / 'verdict-final.md', '| M1 | ui-01#1 | 의미 위반 | 근거 | web/legacy/alpha.py:1 |\n'
              '| M2 | ui-01#2 | 병합 → M1 | 근거 | web/legacy/beta.py:1 |\n')
        write(self.f / 'design-spec.md', '## 슬라이스 0\n경로: legacy/beta.py → moved/beta.py\n')
        self.m(section(meaning='-', body=decision('M1') + '의미 ⓑ 키: M1\n'), 1, '이동 묶음 의존')

    def test_m_negative_table(self):
        self.m_setup()
        for name, body, adopted in (
            ('live', decision('M1') + '의미 ⓑ 키: M1\n', 'M1'),
            ('unknown', decision('M99') + '의미 ⓑ 키: M99\n', '-'),
            ('overlap', decision('M1') + '의미 ⓑ 키: M1\n의미 ⓑ 다른 요청 키: M1\n', '-'),
            ('duplicate', decision('M1') + '의미 ⓑ 키: M1\n의미 ⓑ 키: M1\n', '-'),
            ('repair', decision('M1', '수리 대기', extra='') + '의미 ⓑ 수리 대기 키: M1\n', '-'),
            ('type', decision('M1', '다른 요청') + '의미 ⓑ 키: M1\n', '-'),
            ('proxy', decision('M1', source='대리 판단') + '의미 ⓑ 키: M1\n', '-'),
        ):
            with self.subTest(name=name):
                self.m(section(meaning=adopted, body=body), 1, '실행 불능')

    def test_m_finalize_with_active_item(self):
        self.m_setup()
        write(self.p / 'web/legacy/alpha.py', 'value = 2\n')
        text = section(meaning='M1', body=decision('M2', '다른 요청') + '의미 ⓑ 다른 요청 키: M2\n')
        self.m(text, want='리뷰어 확인 대상 1')
        out_dir = next((self.f / 'residual').iterdir())
        write(out_dir / 'result-ui.md', '| M1 | 해소 | web/legacy/alpha.py:1 — 판단을 한 곳에 둠 |\n'
              '| M2 | 해소 | web/legacy/beta.py:1 — 미룸을 해소로 가장 |\n')
        self.m(text, want='legacy 잔존 ⓑ(다른 요청) M2', finalize=out_dir.name)
        solved = json.loads((out_dir / 'result.json').read_text())['solved']
        self.assertEqual(set(solved), {'M1'})

    def test_m_old_prose_ignored_byte(self):
        self.m_setup()
        write(self.f / 'refactor-scope.md', section(meaning='-', body='의미 ⓑ 키: 다음 요청에서 논의\n'))
        old = self.cli('refactor_audit.py', 'residual', self.f, old=True)
        old_files = {p.relative_to(self.f): p.read_bytes() for p in (self.f / 'residual').rglob('*') if p.is_file()}
        shutil.rmtree(self.f / 'residual')
        new = self.cli('refactor_audit.py', 'residual', self.f)
        new_files = {p.relative_to(self.f): p.read_bytes() for p in (self.f / 'residual').rglob('*') if p.is_file()}
        self.assertEqual((new.returncode, new.stdout, new_files), (old.returncode, old.stdout, old_files))
        self.assertEqual(new.returncode, 0)
        stamp = next((self.f / 'residual').iterdir()).name
        old = self.cli('refactor_audit.py', 'residual', self.f, '--finalize', stamp, old=True)
        final_old = {p.relative_to(self.f): p.read_bytes() for p in (self.f / 'residual').rglob('*') if p.is_file()}
        shutil.rmtree(self.f / 'residual')
        for path, data in new_files.items():
            (self.f / path).parent.mkdir(parents=True, exist_ok=True)
            (self.f / path).write_bytes(data)
        new = self.cli('refactor_audit.py', 'residual', self.f, '--finalize', stamp)
        final_new = {p.relative_to(self.f): p.read_bytes() for p in (self.f / 'residual').rglob('*') if p.is_file()}
        self.assertEqual(new.returncode, 0)
        self.assertEqual((new.returncode, new.stdout, final_new), (old.returncode, old.stdout, final_old))

    def test_names_method_hits(self):
        write(self.p / 'web/legacy/alpha.py', 'class Old:\n    def move(self): pass\n')
        write(self.p / 'web/other/gamma.py', 'from web.legacy.alpha import Old\nOld().move()\nOld().move2()\n')
        write(self.p / 'web/other/unrelated.py', 'def move(): pass\n')
        spec = self.f / 'design-spec.md'
        write(spec, '## 슬라이스 0\n- 메서드 이동: `web.legacy.alpha.Old.move` → `web.new.beta.New.run` · 시험 tests/test_a.py::test_move\n')
        out = self.cli('refactor_audit.py', 'plan', 'web/legacy', '--debt', self.f / 'debt-g0.json',
                       '--out', self.f / 'names', '--names', spec)
        self.assertEqual(out.returncode, 0, out.stdout.decode())
        self.assertIn(' · 메서드 1'.encode(), out.stdout)
        body = (self.f / 'names/plan-names.md').read_text()
        found = body.split('## 명세 참조 줄 (나)')[1].split('\n## ')[0]
        self.assertIn('`web/other/gamma.py:2`', found)
        self.assertNotIn('gamma.py:3', found)
        self.assertNotIn('unrelated.py', found)

    def test_names_parent_test_path_is_ignored(self):
        spec = self.f / 'design-spec.md'
        write(spec, '## 슬라이스 0\n메서드 이동: web.legacy.alpha.Old.move → web.new.beta.New.run · 시험 `../tests/test_a.py::test_move`\n')
        args = ('plan', 'web/legacy', '--debt', self.f / 'debt-g0.json', '--out', self.f / 'names', '--names', spec)
        old = self.cli('refactor_audit.py', *args, old=True)
        old_files = {p.name: p.read_bytes() for p in (self.f / 'names').iterdir()}
        new = self.cli('refactor_audit.py', *args)
        self.assertEqual(new.returncode, 0)
        self.assertEqual((new.returncode, new.stdout, {p.name: p.read_bytes() for p in (self.f / 'names').iterdir()}),
                         (old.returncode, old.stdout, old_files))

    def test_byte_baseline_variants_and_commands(self):
        for i, code in enumerate((2, 2, 2, 1, 1), 1):
            text = REPRO_VARIANTS[i - 1]
            new = self.c(text, code)
            new_json = (self.f / 'debt-g2.json').read_bytes() if (self.f / 'debt-g2.json').exists() else None
            old = self.c(text, code, old=True)
            old_json = (self.f / 'debt-g2.json').read_bytes() if (self.f / 'debt-g2.json').exists() else None
            self.assertEqual((new.returncode, new.stdout, new_json), (old.returncode, old.stdout, old_json), f'v{i}')
        for opts in ([], ['--refactor']):
            args = (self.p, '--debt-scan', '--json', self.f / 'scan.json', *opts)
            old = self.cli('backstop.py', *args, old=True)
            old_json = (self.f / 'scan.json').read_bytes()
            new = self.cli('backstop.py', *args)
            self.assertEqual((new.returncode, new.stdout, (self.f / 'scan.json').read_bytes()),
                             (old.returncode, old.stdout, old_json))
        for spec_text in ('## 슬라이스 0\n경로: legacy/alpha.py → new/alpha.py\n',
                          '## 슬라이스 0\n메서드 이동: 다음 요청에서 논의\n',
                          '## 기타\n메서드 이동: web.legacy.alpha.Old.move → web.new.beta.New.run · 시험 tests/test_a.py::test_move\n## 슬라이스 0\n'):
            spec = self.f / 'design-spec.md'
            write(spec, spec_text)
            args = ('plan', 'web/legacy', '--debt', self.f / 'debt-g0.json', '--out', self.f / 'names', '--names', spec)
            old = self.cli('refactor_audit.py', *args, old=True)
            old_files = {p.name: p.read_bytes() for p in (self.f / 'names').iterdir()}
            new = self.cli('refactor_audit.py', *args)
            self.assertEqual((new.returncode, new.stdout, {p.name: p.read_bytes() for p in (self.f / 'names').iterdir()}),
                             (old.returncode, old.stdout, old_files))


if __name__ == '__main__':
    outcome = unittest.main(verbosity=2, exit=False).result
    bad = len(outcome.failures) + len(outcome.errors)
    skipped = len(outcome.skipped)
    sys.stderr.flush()
    print('2.3.1 빚 미룸 정형 픽스처: PASS %d / FAIL %d%s' % (outcome.testsRun - bad - skipped, bad,
                                                         ' · 건너뜀 %d' % skipped if skipped else ''))
    sys.exit(0 if outcome.wasSuccessful() else 1)
