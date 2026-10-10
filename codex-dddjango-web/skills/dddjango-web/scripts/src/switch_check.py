# dddjango-web 시험 전환 확인(0T) — `refactor_audit.py switch-check <산출물 폴더> --test-cmd '<시험 명령 앞부분>'`.
# (값 정본: 커맨드 «0T 창» · 명세 `## 슬라이스 0` 절의 `시험 전환:` 행 · build-state `slices[0].test_switch`)
#
# 입력: 명세 행 `시험 전환: <시험 파일>::<최상위 함수> · 행위 <옛 web. 대상> → <새 web. 대상> · 보호 분기 <web 파일>:<시작행>-<끝행>
#   · 반례 <산출물 폴더 상대 경로>[ <반례 …>]`(시험 파일 · 보호 분기 파일은 저장소 상대 경로) · build-state `git_snapshot` ·
#   `slices[]` 커밋 기록 · `slices[0].test_switch`(`state` · `commits` = T · `cancel_commits`).
# 차례(시작 전은 읽기만):
#   -. `--test-cmd` 에 시험을 고르거나 줄이는 선택지(-k · -m · --deselect · --lf · --ff · --sw · -x · --maxfail · --co ·
#      --ignore · --runxfail · -p no:<기록 플러그인>)가 있으면 아무것도 하지 않고 exit 1(대상 case 를 모두 돌려야 한다).
#   0. 남은 임시 변경 복구(아래 «복구 상태») — 무엇보다 먼저.
#   1. `.dddjango-web/` 밖 추적 · 미추적 변경 0(아니면 손대지 않고 exit 1).
#   2. test_switch 기록 — state 가 prepared · verifying · verified(cancelled 는 확인하지 않는다) · T ⊂ slices[0].commits ·
#      기능 슬라이스 기록과 배타.
#   3. 명세 행의 꼴 — 시험 파일은 web/ 밖 저장소 상대 시험 .py · 행위는 web. 점 경로 쌍 · 보호 분기는 web/ 비시험 파일.
#   4. git_snapshot..HEAD 첫 부모 사슬 — T 는 사슬 위 비병합 커밋이고 web/ 을 바꾸지 않으며 web/ 밖은 행에 적힌 시험 파일만
#      바꾼다(산출물 폴더 `.dddjango-web/` 는 따지지 않는다 — 치환 확인과 같은 기준) · 기록된 슬라이스 커밋이 T 보다 앞에 있으면 안 된다. T 뒤에 기록된 슬라이스 커밋(0C · 기능)이 이미 있으면 다시 돌릴 수 없다 — state 가
#      verified 이고 앞 증거가 지금 명세의 행 전체(시험 · 행위 · 보호 분기 · 반례 경로와 지문) · T 목록 · 기준 판과 같고
#      행 확인(아래 5 — 시험은 T 끝 판으로)을 통과하며 정상 통과 · 반례마다 옛 · 새 실패 기록이 갖춰졌으면 «이미 검증됨»
#      (exit 0 — 시험을 돌리지 않고 아무것도 쓰지 않는다), 아니면 exit 1(검증 전 0C 금지). 슬라이스 커밋이 없을 때: T 아닌
#      커밋이 행의 시험 파일을 바꾸면 안 되고, 보호 분기
#      파일은 기준 판 그대로여야 한다(기준 판 뒤의 연결 설정 · SDK 격리 커밋 같은 다른 커밋은 막지 않는다).
#   5. 행마다 — 시험 파일 · 함수가 기준 판(git_snapshot)과 HEAD 에 있음 · 그 함수(옛 · 새)의 assert 문 줄 범위가 서로
#      겹치지 않음(한 줄에 단언 둘이면 같은 순번 단언을 가릴 수 없다) · 반례는 파일 하나 · 보호 분기 파일만 · 기준 판 그
#      줄에 정확히 맞음 · 바뀐 줄이 보호 분기 줄 범위 안 → `git apply --check`.
# 행마다: ① 정상 제품 + 새 시험(HEAD 판) · 옛 시험(기준 판)이 case 마다 수집 · 실행 · 통과 ② 반례 적용(`git apply`) + 새
#   시험이 시험 함수의 k번째 assert 문에서 AssertionError(예외가 그 함수 프레임에서 났을 때만 — 도움 함수 · 제품 안
#   AssertionError 는 단언 실패가 아니다) ③ 같은 반례 + 옛 시험이 같은 k 에서 AssertionError ④ 반례 되돌림 → 끝에 작업 트리 ·
#   index · HEAD 가 시작 상태 그대로. 실행은 모두 두 번 해 결과가 같아야 한다(다르면 요동 — 미검증).
#   대상 case 는 기록 플러그인의 걸러지기 전 수집 목록으로 대조한다 — 대상(같은 파일 · 같은 최상위 함수) 밖 노드가 섞이면
#   입력 오류(exit 1), 걸러져 돌지 않은 case 가 있거나 반례 실행(옛 · 새)의 case 가 정상 실행과 다르면 미검증. 반복문 안
#   단언 · 시험 함수가 자신을 다시 부른 안쪽 단언에서 난 실패는 몇째 차례인지 가릴 수 없어 미검증이다.
# 옛 시험은 기준 판 원문을 시험 파일 옆 임시 파일(`<이름>__dddjango_switch_old.py`)에 써서 돌린다 — index · 작업 트리의
#   시험 파일은 건드리지 않는다.
# 복구 상태: 임시 변경(반례 · 옛 시험 임시 파일)은 하기 *전에* `<산출물 폴더>/test-switch/state.json` 의 `pending` 에 적고
#   (경로 · 시작 내용 sha256 · 바뀐 내용 sha256), 되돌린 뒤 지운다. 다시 불리면 먼저 그 기록대로 되돌린다 — 기록 꼴이
#   스키마 밖이거나, 경로가 명세 `시험 전환:` 행의 보호 분기 파일 · 옛 시험 임시 자리가 아니거나, 심볼릭 링크를 지나거나
#   저장소 밖으로 풀리거나, 파일 내용이 기록의 시작 · 바뀐 내용 어느 쪽도 아니거나, 지울 옛 시험 임시 파일이 git 에
#   추적된 파일(HEAD · index)이거나, 반례 자리의 바뀐 내용이 기록의 반례를 HEAD 내용에 그대로 적용한 결과가 아니거나,
#   HEAD 의 그 파일이 기록의 시작 내용이 아니면 아무것도 건드리지 않고 멈춘다(복구 불능 exit 1). 시험 실행에 쓰는 도구
#   임시 폴더도 경로를 `work` 에 적어 두고, 앞 실행이 끊겨 남은 것은 도구가 만든 꼴일 때만 다음 호출이 지운다.
# 판정 입력은 pytest 기록 플러그인(`switch_probe.py` — 빈 임시 폴더에 복사해 `-p` 로 싣는다)이 낸 JSON 줄이다. 화면
#   출력은 결과 줄(마지막 줄)만 증거에 옮긴다. 시험 명령에는 `-p no:cacheprovider` 도 붙이고 PYTHONDONTWRITEBYTECODE=1 로
#   돌린다(작업 트리에 캐시를 남기지 않는다).
# exit 0 = 모두 검증(증거 `<산출물 폴더>/test-switch/evidence.json`) · 2 = 반례 판정 어긋남 · 1 = 실행 불능 · 미검증
#   (시작 거절 · 복구 불능 포함). 첫 어긋남 · 미검증에서 멈춘다(남은 행은 확인하지 않는다). `[switch] 시작 거절 — …` 줄은
#   반례 · 임시 파일을 하나도 남기지 않은 입력 거절(명령 · 작업 트리 · 기록 · 행 · 반례 꼴 — 대상 밖 노드는 첫 실행에서
#   드러나도 이 줄)이고, 행 결과 줄의 `· 미검증` · `· 어긋남` 과 `[switch] 복구 불능 — …` 이 확인 실패다.
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .debt import SPEC_SLICE0_HEAD, SpecSwitch, parse_spec_switches

OUTPUT_ROOT: str = '.dddjango-web'
SWITCH_DIR: str = 'test-switch'
STATE_SCHEMA: str = 'dddjango-web-test-switch-state/1'
EVIDENCE_SCHEMA: str = 'dddjango-web-test-switch-evidence/1'
PROBE_SOURCE: Path = Path(__file__).resolve().parent / 'switch_probe.py'
PROBE_MODULE: str = 'dddjango_web_switch_probe'
PROBE_ENV: str = 'DDDJANGO_WEB_SWITCH_PROBE'
OLD_SUFFIX: str = '__dddjango_switch_old.py'
DEFAULT_TIMEOUT: int = 600
ASSERTION: str = 'builtins.AssertionError'
WORK_PREFIX: str = 'dddjango-web-switch-'
STATE_VERIFIED: str = 'verified'
STATE_CANCELLED: str = 'cancelled'
LIVE_STATES: tuple = ('prepared', 'verifying', STATE_VERIFIED)
EXIT_OK, EXIT_ERR, EXIT_RED = 0, 1, 2

_HASH_RE = re.compile(r'^[0-9a-f]{7,40}$')
_SHA256_RE = re.compile(r'^[0-9a-f]{64}$')
_WORK_FILE_RE = re.compile(r'^(?:run-\d+\.jsonl|probe|probe/%s\.py|probe/__pycache__|probe/__pycache__/[^/]+\.pyc)$'
                           % PROBE_MODULE)
_ENTRY_KEYS: dict = {'old-test': {'path', 'kind', 'original', 'changed'},
                     'mutant': {'path', 'kind', 'original', 'changed', 'mutant'}}
# `--test-cmd` 에서 시험을 고르거나 줄이는 선택지 — 대상 노드의 모든 case 를 끝까지 돌려야 판정이 선다.
_SELECT_LONG: tuple = ('--deselect', '--lf', '--last-failed', '--ff', '--failed-first', '--sw', '--stepwise', '--sw-skip',
                       '--stepwise-skip', '--exitfirst', '--maxfail', '--co', '--collect-only', '--collectonly', '--ignore',
                       '--ignore-glob', '--runxfail')
_SELECT_SHORT: str = 'kmx'           # -k · -m · -x
_SHORT_WITH_VALUE: str = 'cnoprW'    # 값을 받는 짧은 선택지 — 그 뒤 글자(또는 다음 인자)는 값이다
_SHORT_PLAIN: str = 'lqsv'           # 값 없는 짧은 선택지 — 묶어 쓸 수 있다
_PYTEST_PROGRAMS: tuple = ('pytest', 'py.test')
_HUNK_RE = re.compile(rb'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')
_PATCH_FORBIDDEN: tuple = (b'new file mode', b'deleted file mode', b'rename from', b'rename to', b'copy from',
                           b'copy to', b'old mode', b'new mode', b'similarity index', b'dissimilarity index',
                           b'Binary files', b'GIT binary patch')


class Unverified(Exception):
    """실행 불능 · 미검증 — exit 1."""


class RecoveryError(Unverified):
    """복구 불능 — 기록 밖 내용이라 손대지 않았다(exit 1)."""


class InputError(Unverified):
    """입력 오류 — 첫 실행에서 드러난 명령의 꼴(대상 밖 노드). 반례 · 임시 파일을 남기지 않고 시작 거절로 낸다(exit 1)."""


class Mismatch(Exception):
    """반례 판정 어긋남 — exit 2."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_sha(path: Path) -> str | None:
    return _sha(path.read_bytes()) if path.is_file() else None


def _short(sha: str) -> str:
    return sha[:12]


def _now() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _relative_ok(rel: str) -> bool:
    return bool(rel) and not rel.startswith('/') and '\\' not in rel and \
        all(part not in ('', '.', '..') for part in rel.split('/'))


def _pytest_args(argv: list) -> list:
    """시험 명령에서 pytest 에 가는 인자 — `pytest` · `py.test` 실행 파일이나 `-m pytest` 뒤. 못 찾으면 첫 낱말 뒤 전부."""
    for index, token in enumerate(argv):
        if os.path.basename(token) in _PYTEST_PROGRAMS or token == '-mpytest':
            return argv[index + 1:]
        if token == '-m' and argv[index + 1:index + 2] == ['pytest']:
            return argv[index + 2:]
    return argv[1:]


def selecting_option(argv: list) -> str | None:
    """`--test-cmd` 의 고르는 · 줄이는 선택지 이름(없으면 None) — 짧은 선택지 묶음(`-qk`)과 `=` 값 꼴도 읽는다."""
    args: list = _pytest_args(argv)
    index: int = 0
    while index < len(args):
        token: str = args[index]
        index += 1
        if token == '--':
            break
        if token.startswith('--'):
            name: str = token.split('=', 1)[0]
            if name in _SELECT_LONG:
                return name
            continue
        if len(token) < 2 or not token.startswith('-'):
            continue
        for at, char in enumerate(token[1:], 1):
            if char in _SELECT_SHORT:
                return '-' + char
            if char in _SHORT_WITH_VALUE:
                value: str = token[at + 1:]
                if not value and index < len(args):
                    value = args[index]
                    index += 1
                if char == 'p' and value == 'no:' + PROBE_MODULE:
                    return '-p no:' + PROBE_MODULE
                break
            if char not in _SHORT_PLAIN:
                break
    return None


def _entry_ok(entry: object) -> bool:
    """복구 기록 한 건이 이 도구가 쓰는 꼴인가 — kind · 칸 이름 · 경로 · sha256 · 반례 경로."""
    if not isinstance(entry, dict) or entry.get('kind') not in _ENTRY_KEYS or set(entry) != _ENTRY_KEYS[entry['kind']]:
        return False
    if not isinstance(entry['path'], str) or not _relative_ok(entry['path']):
        return False
    if not isinstance(entry['changed'], str) or not _SHA256_RE.match(entry['changed']):
        return False
    if entry['kind'] == 'old-test':
        return entry['original'] is None
    return isinstance(entry['original'], str) and bool(_SHA256_RE.match(entry['original'])) and \
        isinstance(entry['mutant'], str) and _relative_ok(entry['mutant'])


def _evidence_gap(proof: dict) -> str:
    """증거 한 행에 실행 기록이 갖춰졌는가 — 빠진 것의 이름(갖춰졌으면 '')."""
    def results(side: object) -> list | None:
        items = side.get('results') if isinstance(side, dict) else None
        if not isinstance(items, list) or not items or not all(
                isinstance(i, dict) and isinstance(i.get('case'), str) and isinstance(i.get('node'), str) for i in items):
            return None
        return items

    nodes = proof.get('nodes')
    normal = proof.get('normal') if isinstance(proof.get('normal'), dict) else {}
    new, old = results(normal.get('new')), results(normal.get('old'))
    if not isinstance(nodes, list) or not nodes or new is None or old is None or [i['node'] for i in new] != nodes \
            or [i['case'] for i in new] != [i['case'] for i in old] or any(i.get('result') != 'pass' for i in new + old):
        return '정상 통과 기록'
    cases: list = [i['case'] for i in new]
    mutants = proof.get('mutants')
    if not isinstance(mutants, list) or not mutants:
        return '반례 기록'
    for mutant in mutants:
        mutant = mutant if isinstance(mutant, dict) else {}
        got_new, got_old = results(mutant.get('new')), results(mutant.get('old'))
        ok: bool = got_new is not None and got_old is not None and [i['case'] for i in got_new] == cases \
            and [i['case'] for i in got_old] == cases and any(i.get('result') == 'assert' for i in got_new)
        for a, b in zip(got_new or [], got_old or []):
            if a.get('result') == b.get('result') == 'pass':
                continue
            k = a.get('assert')
            if not (a.get('result') == b.get('result') == 'assert' and type(k) is int and k >= 1 and b.get('assert') == k):
                ok = False
        if not ok:
            return '반례 %s 의 옛 · 새 실패 기록' % mutant.get('path')
    return ''


# ── git ──────────────────────────────────────────────────────────────────────

class Git:
    def __init__(self, root: Path) -> None:
        self.root = root

    def call(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(['git', '-C', str(self.root), '-c', 'core.quotePath=false', *args], capture_output=True,
                              env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))

    def text(self, *args: str) -> str:
        result = self.call(*args)
        if result.returncode:
            raise Unverified('git %s 실패 — %s' % (' '.join(args[:2]), result.stderr.decode('utf-8', 'replace').strip()[:200]))
        return result.stdout.decode('utf-8', 'replace')

    def commit(self, rev: str) -> str | None:
        result = self.call('rev-parse', '--verify', '--quiet', rev + '^{commit}')
        return result.stdout.decode().strip() if result.returncode == 0 else None

    def blob(self, rev: str, path: str) -> bytes | None:
        result = self.call('cat-file', 'blob', '%s:%s' % (rev, path))
        return result.stdout if result.returncode == 0 else None

    def dirty(self) -> list:
        """`.dddjango-web/` 밖 추적 · 미추적 변경 경로(무시 파일 제외)."""
        result = self.call('status', '--porcelain=v1', '-z', '--untracked-files=all', '--', '.',
                           ':(exclude)%s' % OUTPUT_ROOT)
        if result.returncode:
            raise Unverified('git status 실패 — %s' % result.stderr.decode('utf-8', 'replace').strip()[:200])
        paths: list = []
        skip: bool = False
        for entry in result.stdout.split(b'\0'):
            if skip:
                skip = False
                continue
            if len(entry) < 4:
                continue
            skip = entry[:1] in (b'R', b'C') or entry[1:2] in (b'R', b'C')
            paths.append(entry[3:].decode('utf-8', 'replace'))
        return paths

    def changed(self, parent: str, commit: str) -> list:
        out: str = self.text('diff-tree', '-r', '--no-commit-id', '--name-only', '--no-renames', '-z', parent, commit)
        return [p for p in out.split('\0') if p]


# ── 명세 행 ──────────────────────────────────────────────────────────────────

class Row:
    def __init__(self, parsed: SpecSwitch) -> None:
        self.number: int = parsed.number
        self.test: str = parsed.test
        self.func: str = parsed.func
        self.old: str = parsed.old
        self.new: str = parsed.new
        self.branch: str = parsed.branch
        self.start: int = parsed.start
        self.end: int = parsed.end
        self.mutants: list = list(parsed.mutants)

    @property
    def label(self) -> str:
        return '%s::%s' % (self.test, self.func)

    @property
    def branch_label(self) -> str:
        return '%s:%d-%d' % (self.branch, self.start, self.end)

    @property
    def old_temp(self) -> str:
        return self.test[:-len('.py')] + OLD_SUFFIX


def parse_rows(text: str) -> list:
    """명세 `## 슬라이스 0` 절의 `시험 전환:` 행. 행의 꼴은 치환 확인과 같은 한 곳(debt.parse_spec_switches)이 정한다 —
    백틱 · `- ` 머리는 `경로:` · `이름:` 행과 같은 폭이고, 코드 울타리 안과 절 밖은 읽지 않는다. 꼴이 어긋난 줄이 하나라도
    있으면 멈춘다(치환 확인은 그 줄을 읽지 않으므로 여기서 알린다)."""
    parsed, errors, heads = parse_spec_switches(text)
    if errors:
        raise Unverified(errors[0])
    if heads > 1:
        raise Unverified('명세에 `%s` 절 머리가 %d개다' % (SPEC_SLICE0_HEAD, heads))
    rows: list = [Row(item) for item in parsed]
    if not rows:
        raise Unverified('명세 `%s` 절에 `시험 전환:` 행이 없다' % SPEC_SLICE0_HEAD)
    seen: set = set()
    for row in rows:
        if row.label in seen:
            raise Unverified('`시험 전환:` 행이 같은 시험 함수를 두 번 적었다 — %s' % row.label)
        seen.add(row.label)
        if row.old == row.new:
            raise Unverified('`시험 전환:` 행의 옛 대상과 새 대상이 같다 %d행 — %s' % (row.number, row.old))
    return rows


def assert_spans(source: bytes, func: str, where: str) -> list:
    """최상위 함수 `func` 안 assert 문의 (첫 줄, 끝 줄, 반복문 안인가) — 원문 차례(중첩 함수 · 클래스 · lambda 안은 뺀다).
    두 단언의 줄 범위가 겹치면(한 줄에 단언 둘) 실패 줄로 순번을 가릴 수 없으므로 거절한다."""
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise Unverified('%s 를 해석할 수 없다 — %s' % (where, error)) from None
    defs: list = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func]
    if len(defs) != 1:
        raise Unverified('%s 에 최상위 함수 %s 가 %d개다(하나여야 한다)' % (where, func, len(defs)))
    spans: list = []

    def walk(node: ast.AST, looped: bool) -> None:
        for field, value in ast.iter_fields(node):
            inner: bool = looped or (isinstance(node, (ast.For, ast.AsyncFor, ast.While)) and field == 'body')
            for child in value if isinstance(value, list) else [value]:
                if not isinstance(child, ast.AST) or isinstance(
                        child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                    continue
                if isinstance(child, ast.Assert):
                    spans.append((child.lineno, getattr(child, 'end_lineno', None) or child.lineno, inner))
                walk(child, inner)

    walk(defs[0], False)
    spans.sort()
    for before, after in zip(spans, spans[1:]):
        if after[0] <= before[1]:
            raise Unverified('%s 의 시험 함수 %s 의 단언 둘이 같은 줄에 걸친다(%d행) — 한 줄에 단언은 하나만 둔다(같은 순번 '
                             '단언을 가릴 수 없다)' % (where, func, after[0]))
    return spans


# ── 반례 ─────────────────────────────────────────────────────────────────────

def _patch_path(header: bytes, prefix: bytes) -> str | None:
    value: bytes = header.rstrip(b'\r\n').split(b'\t', 1)[0]
    if value == b'/dev/null' or not value.startswith(prefix):
        return None
    return value[len(prefix):].decode('utf-8', 'replace')


def parse_patch(data: bytes, rel: str) -> tuple:
    """단일 파일 내용 diff → (경로, [(옛 시작, 옛 줄 수, 몸 줄 목록)]). 생성 · 삭제 · 개명 · 모드 · 이진은 받지 않는다."""
    lines: list = data.splitlines(keepends=True)
    files: list = []
    hunks: list = []
    gits: int = 0
    i: int = 0
    while i < len(lines):
        line: bytes = lines[i]
        if line.startswith(_PATCH_FORBIDDEN):
            raise Unverified('반례 %s 는 내용만 바꾸는 diff 여야 한다(%s)' % (rel, line.strip().decode('utf-8', 'replace')))
        if line.startswith(b'diff --git '):
            gits += 1
        if line.startswith(b'--- ') and i + 1 < len(lines) and lines[i + 1].startswith(b'+++ '):
            files.append((_patch_path(line[4:], b'a/'), _patch_path(lines[i + 1][4:], b'b/')))
            i += 2
            continue
        head = _HUNK_RE.match(line)
        if head:
            if not files:
                raise Unverified('반례 %s 형식 오류 — 파일 머리(---/+++) 없는 hunk' % rel)
            old_left: int = int(head[2]) if head[2] is not None else 1
            new_left: int = int(head[4]) if head[4] is not None else 1
            start, count = int(head[1]), old_left
            body: list = []
            i += 1
            while (old_left > 0 or new_left > 0) and i < len(lines):
                tag: bytes = lines[i][:1]
                if tag == b' ':
                    old_left, new_left = old_left - 1, new_left - 1
                elif tag == b'-':
                    old_left -= 1
                elif tag == b'+':
                    new_left -= 1
                elif tag != b'\\':
                    raise Unverified('반례 %s 형식 오류 — hunk 안 알 수 없는 줄 %r' % (rel, lines[i][:40]))
                body.append(lines[i])
                i += 1
            while i < len(lines) and lines[i].startswith(b'\\'):
                body.append(lines[i])
                i += 1
            if old_left or new_left:
                raise Unverified('반례 %s 형식 오류 — hunk 가 머리의 줄 수보다 짧다' % rel)
            hunks.append((start, count, body))
            continue
        i += 1
    if max(len(files), gits) != 1:
        raise Unverified('반례 %s 는 파일 하나만 바꾸는 diff 여야 한다(파일 %d)' % (rel, max(len(files), gits)))
    old, new = files[0]
    if old is None or new is None or old != new:
        raise Unverified('반례 %s 는 있는 파일 하나의 내용만 바꾸는 diff 여야 한다(%s → %s)' % (rel, old, new))
    if not hunks:
        raise Unverified('반례 %s 에 hunk 가 없다' % rel)
    return old, hunks


def apply_exact(original: bytes, hunks: list, row: Row, rel: str) -> bytes:
    """hunk 를 머리의 줄 번호 그대로(옮김 없이) 적용한 결과 — 맥락 · 지울 줄이 기준 판 그 줄과 다르면 거절하고, 바뀐 줄
    (지운 줄 · 끼운 자리)이 보호 분기 줄 범위 밖이면 거절한다. 끼움은 앞뒤 두 줄이 모두 범위 안일 때만 받는다."""
    src: list = original.splitlines(keepends=True)
    out: list = []
    pos: int = 0
    changed: bool = False
    for start, count, body in hunks:
        at: int = start - 1 if count > 0 else start
        if at < pos or at > len(src):
            raise Unverified('반례 %s 의 hunk 줄 번호가 겹치거나 파일 밖이다(%d행)' % (rel, start))
        out.extend(src[pos:at])
        pos = at
        ops: list = []
        for line in body:
            if line.startswith(b'\\'):
                if ops and ops[-1][1].endswith(b'\n'):
                    ops[-1] = (ops[-1][0], ops[-1][1][:-1])
                continue
            ops.append((line[:1], line[1:]))
        removed: list = []
        insert_at: int | None = None

        def close() -> None:
            nonlocal removed, insert_at
            if removed:
                outside = [n for n in removed if not row.start <= n <= row.end]
                if outside:
                    raise Unverified('반례 %s 가 보호 분기 %s 줄 범위 밖을 바꾼다(%d행)' % (rel, row.branch_label, outside[0]))
            elif insert_at is not None and not row.start <= insert_at < row.end:
                raise Unverified('반례 %s 가 보호 분기 %s 줄 범위 밖을 바꾼다(%d행 뒤 끼움)' % (rel, row.branch_label, insert_at))
            removed, insert_at = [], None

        for tag, content in ops:
            if tag in (b' ', b'-'):
                if pos >= len(src) or src[pos] != content:
                    raise Unverified('반례 %s 가 기준 판의 그 줄에 맞지 않는다(%d행) — git_snapshot 판에서 만든 diff 여야 한다'
                                     % (rel, pos + 1))
                if tag == b' ':
                    close()
                    out.append(content)
                else:
                    removed.append(pos + 1)
                    changed = True
                pos += 1
            else:
                if not removed and insert_at is None:
                    insert_at = pos
                out.append(content)
                changed = True
        close()
    out.extend(src[pos:])
    if not changed:
        raise Unverified('반례 %s 가 아무것도 바꾸지 않는다' % rel)
    return b''.join(out)


class Mutant:
    def __init__(self, rel: str, path: Path, data: bytes, original: bytes, expected: bytes) -> None:
        self.rel = rel
        self.path = path
        self.sha256 = _sha(data)
        self.original = original
        self.expected = expected


# ── 시험 실행 · 기록 해석 ────────────────────────────────────────────────────

class Outcome:
    def __init__(self, kind: str, k: int | None = None, line: int | None = None, detail: str = '') -> None:
        self.kind = kind          # pass · assert · again(몇째 차례인지 모르는 단언) · other · skip · xfail · xpass · error
        self.k = k
        self.line = line
        self.detail = detail

    def key(self) -> tuple:
        return self.kind, self.k, self.line, self.detail

    def describe(self) -> str:
        if self.kind == 'pass':
            return '통과'
        if self.kind == 'assert':
            return '실패 — 단언 %d(:%d)' % (self.k, self.line)
        if self.kind == 'again':
            return '실패 — %s 단언 %d(:%d)' % (self.detail, self.k, self.line)
        if self.kind == 'other':
            return '실패 — %s' % self.detail
        if self.kind == 'error':
            return '오류(%s)' % self.detail
        return self.kind


class RunResult:
    def __init__(self, rc: int, summary: str, nodeids: list, cases: dict, nodes: dict) -> None:
        self.rc = rc
        self.summary = summary
        self.nodeids = nodeids
        self.cases = cases        # case 표지('' 또는 '[id]') → Outcome — 수집 차례
        self.nodes = nodes        # case 표지 → 노드 id

    def signature(self) -> tuple:
        return self.rc, tuple((cid, o.key()) for cid, o in self.cases.items())

    def brief(self) -> str:
        return ', '.join(('%s %s' % (cid, o.describe())).strip() for cid, o in self.cases.items()) or 'case 0'


class Target:
    """실행 대상 — 노드 · 시험 함수 · 그 원문 파일(프레임 대조) · assert 줄 범위."""

    def __init__(self, rel: str, func: str, path: Path, spans: list) -> None:
        self.node = '%s::%s' % (rel, func)
        self.func = func
        self.real = os.path.realpath(path)
        self.spans = spans


class Runner:
    def __init__(self, project: Path, cmd: list, timeout: int, work: Path) -> None:
        self.project = project
        self.cmd = cmd
        self.timeout = timeout
        self.work = work
        self.probe_dir = work / 'probe'
        self.probe_dir.mkdir()
        shutil.copyfile(PROBE_SOURCE, self.probe_dir / (PROBE_MODULE + '.py'))
        self.count = 0

    def run(self, target: Target) -> RunResult:
        self.count += 1
        record: Path = self.work / ('run-%d.jsonl' % self.count)
        env: dict = dict(os.environ)
        env[PROBE_ENV] = str(record)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        env['PYTHONPATH'] = str(self.probe_dir) + (os.pathsep + env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
        argv: list = self.cmd + ['-p', 'no:cacheprovider', '-p', PROBE_MODULE, target.node]
        try:
            proc = subprocess.Popen(argv, cwd=str(self.project), env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, start_new_session=True)
        except OSError as error:
            raise Unverified('시험 명령을 실행할 수 없다 — %s: %s' % (argv[0], error.strerror or error)) from None
        try:
            raw, _ = proc.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)   # 이 도구가 띄운 시험 명령의 프로세스 묶음만
            except (AttributeError, OSError):
                proc.kill()
            proc.communicate()
            raise Unverified('시간 초과 %d초 — %s' % (self.timeout, target.node)) from None
        text: str = raw.decode('utf-8', 'replace')
        tail: str = ' | '.join([line.strip() for line in text.splitlines() if line.strip()][-3:])
        records: list = []
        if record.is_file():
            for line in record.read_text(encoding='utf-8').splitlines():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    raise Unverified('판독 불능 — 기록 줄을 읽을 수 없다(%s)' % line[:80]) from None
        try:
            return self._analyse(target, proc.returncode, text, tail, records)
        except (AttributeError, KeyError, TypeError, ValueError) as error:
            raise Unverified('판독 불능 — 기록 꼴이 아니다(%s: %s)' % (type(error).__name__, error)) from None

    def _analyse(self, target: Target, rc: int, text: str, tail: str, records: list) -> RunResult:
        if not any(r.get('event') == 'finish' for r in records):
            raise Unverified('판독 불능 — 시험 기록이 끝나지 않았다(기록 플러그인이 실리지 않았거나 실행이 중간에 끝났다 · '
                             '시험 명령 exit %d · %s)' % (rc, tail[:200]))
        errors: list = [r for r in records if r.get('event') == 'collect_error']
        if errors:
            last: str = (str(errors[0].get('text') or '').strip().splitlines() or [''])[-1]
            raise Unverified('수집 오류 — %s %s' % (errors[0].get('nodeid'), last[:200]))
        events: list = [r for r in records if r.get('event') == 'collected']
        if any(not isinstance(r.get('items'), list) or not isinstance(r.get('deselected'), list) for r in events):
            raise Unverified('판독 불능 — 기록에 걸러지기 전 수집 목록이 없다(기록 플러그인이 이 판이 아니다)')
        collected: list = list(dict.fromkeys(n for r in events for n in r.get('nodeids') or []))
        paths: dict = {}
        before: list = []
        for r in events:
            for node, path in r['items'] + r['deselected']:
                paths.setdefault(node, path)
            before.extend(node for node, _path in r['items'])
        before = list(dict.fromkeys(before))
        if not collected and not before:
            raise Unverified('수집 0 — %s(시험 명령 exit %d)' % (target.node, rc))
        for nodeid in dict.fromkeys(before + collected):      # 대상 = 같은 파일(실제 경로) · 같은 최상위 함수의 case
            last_part: str = str(nodeid).partition('::')[2]
            if paths.get(nodeid) != target.real or not (last_part == target.func or (
                    last_part.startswith(target.func + '[') and last_part.endswith(']'))):
                raise InputError('판독 불능 — 대상 밖 노드 %s 가 수집됐다(--test-cmd 에는 시험 경로 없이 명령 앞부분만)' % nodeid)
        kept: set = set(collected)
        dropped: list = [n for n in before if n not in kept]
        if dropped:
            told: set = {node for r in events for node, _path in r['deselected']}
            raise Unverified('판독 불능 — 대상 case %s 가 걸러져 돌지 않는다(%s · 걸러진 case %d) — 대상의 모든 case 를 돌려야 '
                             '판정이 선다' % (dropped[0], '선택지로 걸러짐' if dropped[0] in told else '수집 훅이 뺌', len(dropped)))
        if not collected:
            raise Unverified('수집 0 — %s(시험 명령 exit %d)' % (target.node, rc))
        if rc not in (0, 1):
            raise Unverified('시험 명령 exit %d — %s' % (rc, tail[:200]))
        phases: dict = {}
        for r in records:
            if r.get('event') != 'report':
                continue
            seen: dict = phases.setdefault(r.get('nodeid'), {})
            if r.get('when') not in seen or (r.get('exc') and not seen[r.get('when')].get('exc')):
                seen[r.get('when')] = r           # 같은 단계 기록이 겹치면 예외가 적힌 쪽을 쓴다
        cases: dict = {}
        nodes: dict = {}
        for nodeid in collected:
            cid: str = str(nodeid).partition('::')[2][len(target.func):]
            cases[cid] = self._outcome(target, phases.get(nodeid, {}), nodeid)
            nodes[cid] = nodeid
        summary: str = ''
        for line in reversed(text.strip().splitlines()):
            if line.strip():
                summary = line.strip().strip('=').strip()
                break
        return RunResult(rc, summary, collected, cases, nodes)

    def _outcome(self, target: Target, phases: dict, nodeid: str) -> Outcome:
        for when in ('setup', 'teardown'):
            if phases.get(when, {}).get('outcome') == 'failed':
                return Outcome('error', detail=when)
        setup, call = phases.get('setup'), phases.get('call')
        if setup and setup.get('outcome') == 'skipped':
            return Outcome('xfail' if setup.get('wasxfail') else 'skip')
        if call is None:
            raise Unverified('판독 불능 — %s 의 실행 기록이 없다' % nodeid)
        outcome, xfail = call.get('outcome'), bool(call.get('wasxfail'))
        if outcome == 'passed':
            return Outcome('xpass' if xfail else 'pass')
        if outcome == 'skipped':
            return Outcome('xfail' if xfail else 'skip')
        if xfail:
            return Outcome('xpass')       # strict xfail 이 통과해 실패로 보고된 꼴
        return self._failure(target, call.get('exc'))

    def _failure(self, target: Target, exc: dict | None) -> Outcome:
        frames: list = (exc or {}).get('frames') or []
        if not frames:
            return Outcome('other', detail='예외 기록 없음')
        file, line, name = frames[-1]
        root: str = os.path.realpath(self.project)
        real: str = os.path.realpath(os.path.join(root, str(file)))
        where: str = os.path.relpath(real, root) if real.startswith(root + os.sep) else real
        if exc.get('type') == ASSERTION and real == target.real and name == target.func:
            depth: int = sum(1 for f, _l, n in frames
                             if n == target.func and os.path.realpath(os.path.join(root, str(f))) == target.real)
            for k, (first, last, looped) in enumerate(target.spans, 1):
                if first <= int(line) <= last:
                    if looped or depth > 1:
                        return Outcome('again', k=k, line=int(line),
                                       detail='반복문 안' if looped else '시험 함수가 자신을 다시 부른 안쪽')
                    return Outcome('assert', k=k, line=int(line))
            return Outcome('other', detail='%s · %s:%s %s(assert 문 밖 줄)' % (exc.get('type'), where, line, name))
        return Outcome('other', detail='%s · %s:%s %s' % (exc.get('type'), where, line, name))


# ── 복구 상태 ────────────────────────────────────────────────────────────────

class StateFile:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: dict = {}

    def load(self) -> dict | None:
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as error:
            raise RecoveryError('복구 불능 — 복구 상태 %s 를 읽을 수 없다(%s) — 손대지 않음' % (self.path.name, error)) from None
        if not isinstance(data, dict) or not isinstance(data.get('pending', []), list):
            raise RecoveryError('복구 불능 — 복구 상태 %s 의 꼴이 아니다 — 손대지 않음' % self.path.name)
        self.data = data
        return data

    def save(self, **fields) -> None:
        self.data.update(fields, updated_at=_now())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp: Path = self.path.with_name(self.path.name + '.tmp')
        temp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.replace(temp, self.path)

    def add(self, entry: dict) -> None:
        self.save(pending=list(self.data.get('pending', [])) + [entry])

    def drop(self, entry: dict) -> None:
        self.save(pending=[e for e in self.data.get('pending', []) if e != entry])


KEEP, REMOVE, REWRITE = 'keep', 'remove', 'rewrite'


# ── 확인 ─────────────────────────────────────────────────────────────────────

class SwitchCheck:
    def __init__(self, project: Path, folder: Path, test_cmd: str, timeout: int | None) -> None:
        self.project = project.resolve()
        self.folder_arg = folder
        self.test_cmd = test_cmd
        self.timeout = DEFAULT_TIMEOUT if timeout is None else timeout
        self.git = Git(self.project)
        self.recovered = 0

    # 시작 전 ---------------------------------------------------------------

    def locate(self) -> None:
        top: str = self.git.text('rev-parse', '--show-toplevel').strip()
        if Path(top).resolve() != self.project:
            raise Unverified('대상 프로젝트 루트가 git 저장소 최상위가 아니다 — %s' % self.project)
        folder: Path = self.folder_arg if self.folder_arg.is_absolute() else Path.cwd() / self.folder_arg
        self.folder = folder.resolve()
        outputs: Path = (self.project / OUTPUT_ROOT).resolve()
        if outputs not in self.folder.parents or not self.folder.is_dir():
            raise Unverified('산출물 폴더는 대상 프로젝트의 %s/ 아래 폴더여야 한다 — %s' % (OUTPUT_ROOT, self.folder_arg))
        self.folder_rel = self.folder.relative_to(self.project).as_posix()
        self.state = StateFile(self.folder / SWITCH_DIR / 'state.json')
        self.evidence = self.folder / SWITCH_DIR / 'evidence.json'
        self.evidence_rel = '%s/%s/evidence.json' % (self.folder_rel, SWITCH_DIR)

    def recover(self) -> None:
        data: dict = self.state.load() or {}
        pending: list = data.get('pending') or []
        work = data.get('work')
        if not pending and work is None:
            return
        if data.get('schema') != STATE_SCHEMA or (work is not None and not (isinstance(work, str) and os.path.isabs(work))):
            raise RecoveryError('복구 불능 — 복구 상태 %s 의 꼴이 아니다(schema · work) — 손대지 않음' % self.state.path.name)
        for entry in pending:
            if not _entry_ok(entry):
                raise RecoveryError('복구 불능 — 복구 상태의 기록 꼴이 아니다(%r) — 손대지 않음' % (entry,))
        plans: list = []
        if pending:
            head: str | None = self.git.commit('HEAD')
            if head is None:
                raise RecoveryError('복구 불능 — HEAD 를 풀 수 없다 — 손대지 않음')
            try:
                rows: list = parse_rows(self.spec_text())
            except Unverified as error:
                raise RecoveryError('복구 불능 — 복구 상태의 경로를 확인할 수 없다(%s) — 손대지 않음' % error) from None
            plans = [(entry, self.restore_plan(entry, head, rows)) for entry in pending]   # 먼저 모두 확인
        for entry, (action, content) in plans:
            self.apply_plan(entry, action, content)
            if entry['kind'] == 'mutant':
                print('[switch] 복구 — %s %s' % (entry['path'], '반례 되돌림' if action != KEEP else '이미 시작 내용(그대로 둠)'))
            else:
                print('[switch] 복구 — %s %s' % (entry['path'], '옛 시험 임시 파일 지움' if action != KEEP
                                                 else '옛 시험 임시 파일 이미 없음'))
            self.state.drop(entry)
            self.recovered += 1
        if plans:
            self.state.save(stage='recovered')
        if work is not None:
            self.clear_work(Path(work))

    def restore_plan(self, entry: dict, head: str, rows: list) -> tuple:
        """기록 한 건을 되돌릴 방법 — (KEEP, None) 이미 시작 상태 · (REMOVE, None) 옛 시험 임시 파일을 지운다 ·
        (REWRITE, 시작 내용). 경로는 명세 행의 자리(보호 분기 파일 · 옛 시험 임시 자리)이고 저장소 안이어야 하며, 지울 파일은
        git 이 추적하지 않는 일반 파일 · 되돌릴 반례 자리는 기록의 반례를 HEAD 내용에 그대로 적용한 결과여야 한다 — 아니면
        RecoveryError. 읽기만 하므로 여러 건을 먼저 모두 확인한 뒤 되돌릴 수 있다."""
        rel: str = entry['path']
        owner: Row | None = None
        if entry['kind'] == 'old-test':
            if rel not in {row.old_temp for row in rows}:
                raise RecoveryError('복구 불능 — 기록의 %s 는 명세 `시험 전환:` 행의 옛 시험 임시 자리가 아니다 — 손대지 않음' % rel)
        else:
            owners: list = [row for row in rows if row.branch == rel and entry['mutant'] in row.mutants]
            if not owners:
                raise RecoveryError('복구 불능 — 기록의 %s 는 명세 `시험 전환:` 행의 보호 분기 파일 자리가 아니다(반례 %s) — '
                                    '손대지 않음' % (rel, entry['mutant']))
            owner = owners[0]
        path: Path = self.project / rel
        if os.path.realpath(path) != os.path.join(str(self.project), rel):
            raise RecoveryError('복구 불능 — 기록의 %s 가 심볼릭 링크를 지나거나 저장소 밖으로 풀린다 — 손대지 않음' % rel)
        if path.exists() and not path.is_file():
            raise RecoveryError('복구 불능 — 기록의 %s 가 일반 파일이 아니다 — 손대지 않음' % rel)
        current: str | None = _file_sha(path)
        if current == entry['original']:
            return KEEP, None
        if current != entry['changed']:
            raise RecoveryError('복구 불능 — %s 내용이 기록(시작 · %s)과 다르다 — 손대지 않음'
                                % (rel, '반례 적용' if entry['kind'] == 'mutant' else '옛 시험 임시 파일'))
        if entry['kind'] == 'old-test':
            if self.git.call('ls-files', '--error-unmatch', '--', rel).returncode == 0 or self.git.blob(head, rel) is not None:
                raise RecoveryError('복구 불능 — %s 가 git 에 추적된 파일이다(HEAD · index — 도구의 옛 시험 임시 파일이 아니다) — '
                                    '손대지 않음' % rel)
            return REMOVE, None
        data: bytes | None = self.git.blob(head, rel)
        if data is None or _sha(data) != entry['original']:
            raise RecoveryError('복구 불능 — HEAD 의 %s 가 기록의 시작 내용이 아니다 — 손대지 않음' % rel)
        try:
            target, hunks = parse_patch((self.folder / entry['mutant']).read_bytes(), entry['mutant'])
            expected: bytes | None = apply_exact(data, hunks, owner, entry['mutant']) if target == rel else None
        except (OSError, Unverified):
            expected = None
        if expected is None or _sha(expected) != entry['changed']:
            raise RecoveryError('복구 불능 — 기록의 %s 바뀐 내용이 반례 %s 를 HEAD 내용에 그대로 적용한 결과가 아니다 — 손대지 않음'
                                % (rel, entry['mutant']))
        return REWRITE, data

    def apply_plan(self, entry: dict, action: str, content: bytes | None) -> None:
        path: Path = self.project / entry['path']
        if action == REMOVE:
            path.unlink()
        elif action == REWRITE:
            path.write_bytes(content)

    def clear_work(self, work: Path) -> None:
        """앞 실행이 끊겨 남긴 도구 임시 폴더 — 도구가 만든 꼴(이름 머리 · 기록 플러그인 사본과 실행 기록뿐)일 때만 지운다."""
        if work.is_dir() and not work.is_symlink():
            shaped: bool = work.name.startswith(WORK_PREFIX) and all(
                not item.is_symlink() and _WORK_FILE_RE.match(item.relative_to(work).as_posix()) for item in work.rglob('*'))
            if shaped:
                shutil.rmtree(work)
                print('[switch] 복구 — 앞 실행이 남긴 도구 임시 폴더 지움')
            else:
                print('[switch] 복구 — 기록의 도구 임시 폴더가 도구가 만든 꼴이 아니다 — 그대로 둠(%s)' % work)
        self.state.data.pop('work', None)
        self.state.save()

    def require_clean(self) -> None:
        dirty: list = self.git.dirty()
        if dirty:
            shown: str = ' · '.join(dirty[:5]) + (' …' if len(dirty) > 5 else '')
            raise Unverified('작업 트리에 %s/ 밖 변경 %d: %s(손대지 않음)' % (OUTPUT_ROOT, len(dirty), shown))

    def load_build_state(self) -> None:
        path: Path = self.folder / 'build-state.json'
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as error:
            raise Unverified('build-state.json 을 읽을 수 없다 — %s' % error) from None
        slices = data.get('slices') if isinstance(data, dict) else None
        if not isinstance(slices, list) or not slices or not all(isinstance(s, dict) for s in slices):
            raise Unverified('build-state.json 의 slices 가 객체 목록이 아니다')
        switch = slices[0].get('test_switch')
        if not isinstance(switch, dict):
            raise Unverified('build-state slices[0].test_switch 기록이 없다 — 0T 창에서 T 커밋을 기록한 뒤 다시')
        self.switch_state = switch.get('state')
        if self.switch_state == STATE_CANCELLED:
            raise Unverified('build-state slices[0].test_switch.state 가 cancelled — 취소된 0T 는 확인하지 않는다')
        if self.switch_state not in LIVE_STATES:
            raise Unverified('build-state slices[0].test_switch.state 가 %s 가 아니다(%r)'
                             % (' · '.join(LIVE_STATES), self.switch_state))
        if switch.get('cancel_commits'):
            raise Unverified('build-state slices[0].test_switch.cancel_commits 가 있는데 state 가 cancelled 가 아니다')
        commits = switch.get('commits')
        if not isinstance(commits, list) or not commits:
            raise Unverified('build-state slices[0].test_switch.commits 가 비었다 — T 커밋을 기록한 뒤 다시')
        snapshot = data.get('git_snapshot')
        if not isinstance(snapshot, str) or not _HASH_RE.match(snapshot.strip()):
            raise Unverified('build-state.json 의 git_snapshot 이 커밋 해시가 아니다(%r)' % (snapshot,))
        self.snapshot = self.git.commit(snapshot.strip())
        if self.snapshot is None:
            raise Unverified('build-state git_snapshot %s 를 풀 수 없다' % snapshot)
        self.t_commits: list = []
        for raw in commits:
            if not isinstance(raw, str) or not _HASH_RE.match(raw.strip()):
                raise Unverified('build-state test_switch.commits 의 %r 가 커밋 해시(7~40 hex)가 아니다' % (raw,))
            sha = self.git.commit(raw.strip())
            if sha is None:
                raise Unverified('build-state test_switch.commits 의 %s 를 풀 수 없다' % raw)
            self.t_commits.append(sha)
        zero: list = self._resolved(slices[0])
        for sha in self.t_commits:
            if sha not in zero:
                raise Unverified('T 커밋 %s 가 slices[0].commits 에 없다 — T 는 슬라이스 0 커밋이다' % _short(sha))
        self.slice_commits: dict = {sha: 'slices[0]' for sha in zero if sha not in self.t_commits}   # T 밖 기록(0C · 기능)
        for index, item in enumerate(slices[1:], 1):
            name: str = item.get('name') if isinstance(item.get('name'), str) else 'slices[%d]' % index
            for sha in self._resolved(item):
                if sha in self.t_commits:
                    raise Unverified('T 커밋 %s 가 기능 슬라이스 %s 기록과 겹친다' % (_short(sha), name))
                self.slice_commits.setdefault(sha, name)

    def _resolved(self, item: dict) -> list:
        raw: list = ([item['commit']] if isinstance(item.get('commit'), str) else []) + \
            [c for c in item.get('commits') or [] if isinstance(c, str)]
        return [sha for sha in (self.git.commit(c.strip()) for c in raw if _HASH_RE.match(c.strip())) if sha]

    def spec_text(self) -> str:
        try:
            return (self.folder / 'design-spec.md').read_text(encoding='utf-8')
        except OSError as error:
            raise Unverified('명세 design-spec.md 를 읽을 수 없다 — %s' % error) from None

    def load_rows(self) -> None:
        self.rows: list = parse_rows(self.spec_text())
        self.head = self.git.commit('HEAD')

    def validate_rows(self, head: str | None = None) -> None:
        """행마다 — 시험 파일 · 함수가 기준 판과 `head`(기본 HEAD)에 있음 · 단언 줄 범위가 겹치지 않음 · 옛 시험 임시 자리
        비어 있음 · 보호 분기 · 반례(읽기만)."""
        head = head or self.head
        self.sources: dict = {}
        self.mutants: dict = {}
        for row in self.rows:
            old_src = self.git.blob(self.snapshot, row.test)
            if old_src is None:
                raise Unverified('시험 파일 %s 가 기준 판(git_snapshot %s)에 없다' % (row.test, _short(self.snapshot)))
            new_src = self.git.blob(head, row.test)
            if new_src is None:
                raise Unverified('시험 파일 %s 가 %s 에 없다' % (row.test, 'HEAD' if head == self.head else 'T 끝 판'))
            self.sources[row.label] = (assert_spans(new_src, row.func, row.test),
                                       assert_spans(old_src, row.func, '%s(기준 판)' % row.test), old_src)
            if (self.project / row.old_temp).exists() or self.git.blob(head, row.old_temp) is not None:
                raise Unverified('옛 시험 임시 자리 %s 가 이미 있다' % row.old_temp)
            original = self.git.blob(self.snapshot, row.branch)
            if original is None:
                raise Unverified('보호 분기 파일 %s 가 기준 판에 없다' % row.branch)
            if row.end > len(original.splitlines()):
                raise Unverified('보호 분기 %s 가 기준 판 줄 수(%d)를 넘는다' % (row.branch_label, len(original.splitlines())))
            for rel in row.mutants:
                path: Path = self.folder / rel
                if not path.is_file():
                    raise Unverified('반례 파일이 없다 — %s/%s' % (self.folder_rel, rel))
                data: bytes = path.read_bytes()
                target, hunks = parse_patch(data, rel)
                if target != row.branch:
                    raise Unverified('반례 %s 가 보호 분기 파일(%s)이 아닌 %s 를 바꾼다' % (rel, row.branch, target))
                self.mutants[(row.label, rel)] = Mutant(rel, path, data, original, apply_exact(original, hunks, row, rel))

    def check_chain(self) -> list:
        """git_snapshot..HEAD 첫 부모 사슬 확인 → T 뒤에 이미 있는 기록된 슬라이스 커밋(0C · 기능) 목록(없으면 빈 목록)."""
        listing: str = self.git.text('log', '--first-parent', '--format=%H %P', '%s..%s' % (self.snapshot, self.head))
        chain: list = [line.split() for line in reversed(listing.splitlines()) if line.strip()]
        if not chain:
            raise Unverified('git_snapshot 뒤 0T 커밋이 없다(HEAD 가 git_snapshot %s)' % _short(self.snapshot))
        if chain[0][1:2] != [self.snapshot]:
            raise Unverified('git_snapshot %s 이 HEAD 첫 부모 사슬 위에 없다' % _short(self.snapshot))
        order: list = [c[0] for c in chain]
        tests: set = {row.test for row in self.rows}
        for sha in self.t_commits:
            if sha not in order:
                raise Unverified('T 커밋 %s 가 git_snapshot..HEAD 첫 부모 사슬 밖이다' % _short(sha))
        last_t: int = max(order.index(sha) for sha in self.t_commits)
        self.t_head: str = order[last_t]
        after: list = []
        for index, (commit, *parents) in enumerate(chain):
            if commit in self.t_commits:
                if len(parents) != 1:
                    raise Unverified('T 커밋 %s 가 병합이다 — T 는 비병합 커밋이다' % _short(commit))
                changed: list = [p for p in self.git.changed(parents[0], commit) if not p.startswith(OUTPUT_ROOT + '/')]
                product: list = [p for p in changed if p.startswith('web/')]
                if product:
                    raise Unverified('T 커밋 %s 가 web/ 을 바꾼다 — 0T 는 제품을 고정한다 — %s' % (_short(commit), ' · '.join(product[:5])))
                outside: list = [p for p in changed if p not in tests]
                if outside:
                    raise Unverified('T 커밋 %s 가 행에 적힌 시험 파일 밖을 바꾼다 — %s' % (_short(commit), ' · '.join(outside[:5])))
            elif commit in self.slice_commits:
                if index < last_t:
                    raise Unverified('슬라이스 커밋 %s(%s)가 T 보다 앞이다 — 0T 는 첫 코드 커밋 앞에서 한 번이다'
                                     % (_short(commit), self.slice_commits[commit]))
                after.append(commit)
        if after:
            return after
        for commit, *parents in chain:
            if commit in self.t_commits:
                continue
            touched = [p for p in self.git.changed(parents[0], commit) if p in tests]
            if touched:
                raise Unverified('0T 커밋이 아닌 %s 가 행의 시험 파일 %s 를 바꾼다 — T 로 기록하거나 되돌린 뒤 다시'
                                 % (_short(commit), ' · '.join(touched)))
        for row in self.rows:
            if self.git.blob(self.head, row.branch) != self.git.blob(self.snapshot, row.branch):
                raise Unverified('보호 분기 파일 %s 가 git_snapshot 뒤 바뀌었다 — 반례 · 줄 범위는 기준 판 그대로의 제품에서만 확인한다'
                                 % row.branch)
        return []

    def already_verified(self, after: list) -> int:
        """T 뒤에 슬라이스 커밋이 있어 다시 돌릴 수 없을 때 — 검증 기록과 앞 증거가 지금 명세의 행 전체 · T 목록 · 기준 판과
        같고 행 확인(T 끝 판)을 통과하며 실행 기록이 갖춰졌으면 exit 0."""
        why: str = 'test_switch.state 가 %s' % self.switch_state if self.switch_state != STATE_VERIFIED else self.proof_gap()
        if why:
            raise Unverified('T 뒤에 슬라이스 커밋 %s(%s)가 있는데 0T 검증을 확인할 수 없다(%s) — 검증 전에는 0C 를 보내지 않는다'
                             % (_short(after[0]), self.slice_commits[after[0]], why))
        for row in self.rows:
            print('[switch] %s — 이미 검증됨(증거의 T %s · 반례 지문 같음) · T 뒤 슬라이스 커밋 %d — 다시 돌리지 않는다'
                  % (row.label, _short(self.t_head), len(after)))
        print('요약: switch-check 행 %d · 검증 %d(앞 증거) · 어긋남 0 · 미검증 0 · 증거 %s%s'
              % (len(self.rows), len(self.rows), self.evidence_rel, ' · 복구 %d' % self.recovered if self.recovered else ''))
        return EXIT_OK

    def proof_gap(self) -> str:
        """앞 증거가 지금 기록 · 명세와 맞지 않거나 실행 기록이 빠진 사유('' = 맞음)."""
        try:
            proof = json.loads(self.evidence.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            proof = None
        if not isinstance(proof, dict) or proof.get('schema') != EVIDENCE_SCHEMA or not isinstance(proof.get('rows'), list):
            return '증거 %s 가 없거나 꼴이 아니다' % self.evidence_rel
        if proof.get('t_head') != self.t_head or proof.get('snapshot') != self.snapshot or \
                proof.get('t_commits') != self.t_commits:
            return '증거의 T · 기준 판이 지금 기록과 다르다'
        rows: list = [r if isinstance(r, dict) else {} for r in proof['rows']]
        if len(rows) != len(self.rows):
            return '승인 행이 앞 증거와 다르다 — 행 %d · 증거 %d' % (len(self.rows), len(rows))
        for row, got in zip(self.rows, rows):
            mutants: list = [m if isinstance(m, dict) else {} for m in got['mutants']] \
                if isinstance(got.get('mutants'), list) else []
            if (got.get('test'), got.get('behavior'), got.get('branch'), [m.get('path') for m in mutants]) != \
                    (row.label, [row.old, row.new], row.branch_label, row.mutants):
                return '승인 행이 앞 증거와 다르다 — %s' % row.label
            if [m.get('sha256') for m in mutants] != [_file_sha(self.folder / m) for m in row.mutants]:
                return '증거의 행 · 반례 지문이 지금 명세 · 반례와 다르다'
        try:
            self.validate_rows(self.t_head)
        except Unverified as error:
            return str(error)
        for row, got in zip(self.rows, rows):
            gap: str = _evidence_gap(got)
            if gap:
                return '증거에 실행 기록이 갖춰지지 않았다(%s — %s)' % (gap, row.label)
        return ''

    def check_apply(self) -> None:
        for mutant in self.mutants.values():
            result = self.git.call('apply', '--check', str(mutant.path))
            if result.returncode:
                raise Unverified('반례 %s 가 적용되지 않는다(git apply --check) — %s'
                                 % (mutant.rel, result.stderr.decode('utf-8', 'replace').strip()[:200]))

    # 실행 ------------------------------------------------------------------

    def twice(self, step: str, target: Target) -> RunResult:
        """같은 실행을 두 번 — 결과가 다르면 요동(미검증). `step` 은 사유 머리에 붙는 걸음 이름이다."""
        try:
            first: RunResult = self.runner.run(target)
            second: RunResult = self.runner.run(target)
        except Unverified as error:
            raise type(error)('%s — %s' % (step, error)) from None
        if first.signature() != second.signature():
            raise Unverified('%s — 요동: 같은 실행 두 번의 결과가 다르다(%s / %s)' % (step, first.brief(), second.brief()))
        return first

    def apply_mutant(self, row: Row, mutant: Mutant) -> dict:
        entry: dict = {'path': row.branch, 'kind': 'mutant', 'original': _sha(mutant.original),
                       'changed': _sha(mutant.expected), 'mutant': mutant.rel}
        path: Path = self.project / row.branch
        before: bytes = path.read_bytes()              # 적용 전 실제 바이트(줄 끝 변환 · 실행 중 변경 포함)
        self.state.add(entry)
        result = self.git.call('apply', '--whitespace=nowarn', str(mutant.path))
        if result.returncode == 0 and _file_sha(path) == entry['changed']:
            return entry
        if not path.is_file() or path.read_bytes() != before:   # 방금 이 도구가 바꾼 내용 — 적용 전 바이트로 되돌린다
            path.write_bytes(before)
        self.state.drop(entry)
        raise Unverified('반례 %s 적용 결과가 기준 판에 그대로 적용한 내용과 다르다 — %s'
                         % (mutant.rel, result.stderr.decode('utf-8', 'replace').strip()[:200]))

    def undo(self, entry: dict) -> None:
        action, content = self.restore_plan(entry, self.start_head, self.rows)
        self.apply_plan(entry, action, content)
        self.state.drop(entry)

    def verify_row(self, index: int, row: Row) -> dict:
        new_spans, old_spans, old_src = self.sources[row.label]
        new = Target(row.test, row.func, self.project / row.test, new_spans)
        old = Target(row.old_temp, row.func, self.project / row.old_temp, old_spans)

        def step(name: str, target: Target) -> RunResult:
            self.state.save(stage='행 %d · %s' % (index, name))
            return self.twice(name, target)

        normal_new: RunResult = step('정상 제품 · 새 시험', new)
        self._require_pass(normal_new, '새 시험')
        entry: dict = {'path': row.old_temp, 'kind': 'old-test', 'original': None, 'changed': _sha(old_src)}
        self.state.add(entry)
        (self.project / row.old_temp).write_bytes(old_src)
        normal_old: RunResult = step('정상 제품 · 옛 시험', old)
        self._require_pass(normal_old, '옛 시험')
        if list(normal_new.cases) != list(normal_old.cases):
            raise Unverified('옛 · 새 시험의 case 가 다르다(새 %s · 옛 %s)' % (list(normal_new.cases), list(normal_old.cases)))
        results: list = []
        for rel in row.mutants:
            mutant: Mutant = self.mutants[(row.label, rel)]
            self.state.save(stage='행 %d · 반례 %s 적용' % (index, rel))
            applied: dict = self.apply_mutant(row, mutant)
            mut_new: RunResult = step('반례 %s · 새 시험' % rel, new)
            mut_old: RunResult = step('반례 %s · 옛 시험' % rel, old)
            self.undo(applied)
            if list(mut_new.cases) != list(normal_new.cases) or list(mut_old.cases) != list(normal_new.cases):
                raise Unverified('반례 %s 에서 돈 case 가 정상 실행과 다르다(정상 %s · 새 %s · 옛 %s)'
                                 % (rel, list(normal_new.cases), list(mut_new.cases), list(mut_old.cases)))
            judged: dict = self._judge(mutant, mut_new, mut_old)
            judged['new']['results'] = self._results(mut_new)
            judged['old']['results'] = self._results(mut_old)
            results.append(judged)
        self.undo(entry)
        return {'test': row.label, 'behavior': [row.old, row.new], 'branch': row.branch_label,
                'nodes': normal_new.nodeids,
                'normal': {'new': {'summary': normal_new.summary, 'results': self._results(normal_new)},
                           'old': {'summary': normal_old.summary, 'results': self._results(normal_old)}},
                'mutants': results}

    @staticmethod
    def _results(result: RunResult) -> list:
        """case 마다 노드 · 결과(단언 실패면 순번 · 줄) — 증거의 실행 기록."""
        out: list = []
        for cid, outcome in result.cases.items():
            item: dict = {'case': cid, 'node': result.nodes[cid], 'result': outcome.kind}
            if outcome.kind == 'assert':
                item.update({'assert': outcome.k, 'line': outcome.line})
            out.append(item)
        return out

    @staticmethod
    def _require_pass(result: RunResult, which: str) -> None:
        for cid, outcome in result.cases.items():
            if outcome.kind != 'pass':
                raise Unverified('정상 제품에서 %s이 통과하지 않는다(%s)' % (which, ('%s %s' % (cid, outcome.describe())).strip()))

    @staticmethod
    def _judge(mutant: Mutant, new: RunResult, old: RunResult) -> dict:
        for which, result in (('새', new), ('옛', old)):
            for cid, outcome in result.cases.items():
                if outcome.kind in ('skip', 'xfail', 'xpass', 'error'):
                    raise Unverified('반례 %s%s 에서 %s 시험이 %s' % (mutant.rel, ' ' + cid if cid else '', which,
                                                                outcome.describe()))
                if outcome.kind == 'again':
                    raise Unverified('반례 %s%s 에서 %s 시험이 %s 단언(%d)에서 실패한다 — 몇째 차례의 실패인지 가릴 수 없다(같은 '
                                     '순번 단언으로 세지 않는다)' % (mutant.rel, ' ' + cid if cid else '', which,
                                                                outcome.detail, outcome.k))
        if list(new.cases) != list(old.cases):
            raise Unverified('반례 %s 에서 옛 · 새 시험의 case 가 다르다' % mutant.rel)
        cases: list = []
        for cid in new.cases:
            n, o = new.cases[cid], old.cases[cid]
            at: str = '반례 %s%s' % (mutant.rel, ' ' + cid if cid else '')
            if n.kind == 'other':
                raise Mismatch('%s 에서 새 시험이 단언 밖에서 실패한다(%s)' % (at, n.detail))
            if o.kind == 'other':
                raise Mismatch('%s 에서 옛 시험이 단언 밖에서 실패한다(%s)' % (at, o.detail))
            if o.kind == 'assert' and n.kind == 'pass':
                raise Mismatch('%s 에서 새 시험이 통과한다(옛 시험은 단언 %d 실패) — 새 준비가 보호 분기를 지나지 않는다' % (at, o.k))
            if o.kind == 'pass' and n.kind == 'assert':
                raise Mismatch('%s 에서 옛 시험은 통과하는데 새 시험만 단언 %d 에서 실패한다' % (at, n.k))
            if o.kind == 'assert' and o.k != n.k:
                raise Mismatch('%s 에서 옛 단언 %d · 새 단언 %d — 같은 단언이 아니다' % (at, o.k, n.k))
            if o.kind == 'assert':
                cases.append({'case': cid, 'new': {'assert': n.k, 'line': n.line}, 'old': {'assert': o.k, 'line': o.line}})
        if not cases:
            raise Mismatch('반례 %s 에서 옛 시험이 통과한다 — 반례가 옛 시험이 지키던 실패가 아니다' % mutant.rel)
        return {'path': mutant.rel, 'sha256': mutant.sha256, 'cases': cases,
                'new': dict(cases[0]['new'], summary=new.summary), 'old': dict(cases[0]['old'], summary=old.summary)}

    # 입구 ------------------------------------------------------------------

    def main(self) -> int:
        try:
            cmd: list = shlex.split(self.test_cmd)
        except ValueError as error:
            raise Unverified('--test-cmd 를 나눌 수 없다 — %s' % error) from None
        if not cmd:
            raise Unverified('--test-cmd 가 비었다')
        option: str | None = selecting_option(cmd)
        if option:
            raise Unverified('판독 불능 — --test-cmd 에 시험을 고르거나 줄이는 선택지(%s)가 있다 — 대상의 모든 case 를 돌려야 '
                             '판정이 선다(그 프로젝트의 시험 명령 앞부분에서 빼고 다시)' % option)
        if self.timeout <= 0:
            raise Unverified('--timeout 은 양의 초다')
        self.locate()
        self.recover()
        self.require_clean()
        self.load_build_state()
        self.load_rows()
        after: list = self.check_chain()
        if after:
            return self.already_verified(after)
        self.validate_rows()
        self.check_apply()
        self.begin()
        verified, code, reason = self.verify_rows(cmd)
        return self.finish(verified, code, reason)

    def begin(self) -> None:
        """여기부터 쓴다 — 복구 상태를 먼저 적고, 앞 증거는 지운다(검증되면 다시 쓴다)."""
        self.start_head = self.head
        self.state.data = {'schema': STATE_SCHEMA}
        targets: list = sorted({r.branch for r in self.rows} | {r.old_temp for r in self.rows})
        self.state.save(start_head=self.start_head, t_head=self.t_head, snapshot=self.snapshot, targets=targets,
                        mutants={m.rel: m.sha256 for m in self.mutants.values()}, stage='start', pending=[],
                        result=None, reason='')
        if self.evidence.exists():
            self.evidence.unlink()

    def verify_rows(self, cmd: list) -> tuple:
        """행을 차례로 확인 → (검증된 행의 증거 목록, exit, 사유). 첫 어긋남 · 미검증에서 멈추고, 어떻게 끝나든 남은 임시
        변경을 되돌린다."""
        work: Path = Path(tempfile.mkdtemp(prefix=WORK_PREFIX))
        self.state.save(work=str(work))                # 끊기면 다음 호출이 이 폴더도 치운다
        verified: list = []
        code, reason = EXIT_OK, ''
        refused: InputError | None = None
        try:
            self.runner = Runner(self.project, cmd, self.timeout, work)
            for index, row in enumerate(self.rows, 1):
                try:
                    proof: dict = self.verify_row(index, row)
                except Mismatch as error:
                    code, reason = EXIT_RED, str(error)
                    print('[switch] %s — %s · 어긋남' % (row.label, error))
                    break
                except (RecoveryError, InputError) as error:
                    if isinstance(error, RecoveryError):
                        raise
                    refused = error
                    break
                except Unverified as error:
                    code, reason = EXIT_ERR, str(error)
                    print('[switch] %s — %s · 미검증' % (row.label, error))
                    break
                verified.append(proof)
                ks: str = ' · '.join('/'.join(dict.fromkeys(str(c['new']['assert']) for c in m['cases']))
                                     for m in proof['mutants'])
                print('[switch] %s — 정상 통과 · 반례 %d 모두 옛 · 새 같은 단언(%s) 실패 · 검증됨'
                      % (row.label, len(proof['mutants']), ks))
                for m in proof['mutants']:
                    for c in m['cases']:
                        print('  반례 %s%s — 새 %s:%d 단언 %d · 옛 %s:%d(기준 판) 단언 %d · AssertionError'
                              % (m['path'], ' ' + c['case'] if c['case'] else '', row.test, c['new']['line'],
                                 c['new']['assert'], row.test, c['old']['line'], c['old']['assert']))
        finally:
            try:
                for entry in list(self.state.data.get('pending', [])):
                    self.undo(entry)
            finally:
                shutil.rmtree(work, ignore_errors=True)
                self.state.data.pop('work', None)
                self.state.save()
        if refused is not None:                       # 입력 오류 — 임시 변경을 되돌린 뒤 시작 거절로 낸다
            self.state.save(stage='unverified', result='unverified', reason=str(refused))
            raise refused
        return verified, code, reason

    def finish(self, verified: list, code: int, reason: str) -> int:
        """끝 확인(작업 트리 · HEAD 가 시작 상태 그대로) → 복구 상태의 끝 단계 · 증거(모두 검증일 때만) · 요약 1행."""
        if code == EXIT_OK:
            dirty: list = self.git.dirty()
            if dirty or self.git.commit('HEAD') != self.start_head:
                code, reason = EXIT_ERR, '작업 트리 · HEAD 가 시작 상태와 다르다 — %s' % (' · '.join(dirty[:5]) or 'HEAD')
                print('[switch] 끝 확인 — %s · 미검증' % reason)
        stage: str = {EXIT_OK: STATE_VERIFIED, EXIT_RED: 'mismatch', EXIT_ERR: 'unverified'}[code]
        self.state.save(stage=stage, result=stage, reason=reason)
        tail: str = ''
        if code == EXIT_OK:
            self.evidence.write_text(json.dumps({
                'schema': EVIDENCE_SCHEMA, 'verified_at': _now(), 'snapshot': self.snapshot, 't_head': self.t_head,
                't_commits': self.t_commits, 'start_head': self.start_head, 'test_cmd': self.test_cmd,
                'rows': verified}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            tail = ' · 증거 %s' % self.evidence_rel
        left: int = len(self.rows) - len(verified) - int(code != EXIT_OK)
        print('요약: switch-check 행 %d · 검증 %d · 어긋남 %d · 미검증 %d%s%s%s'
              % (len(self.rows), len(verified), int(code == EXIT_RED), int(code == EXIT_ERR), tail,
                 ' · 확인 안 한 행 %d' % left if left > 0 else '', ' · 복구 %d' % self.recovered if self.recovered else ''))
        return code


def run(project: Path, folder: Path, test_cmd: str, timeout: int | None = None) -> int:
    """`refactor_audit.py switch-check` 입구 — 출력과 exit 은 이 모듈 머리말대로."""
    check = SwitchCheck(project, folder, test_cmd, timeout)
    try:
        return check.main()
    except RecoveryError as error:
        print('[switch] %s' % error)
        print('요약: switch-check 실행 불능 — %s' % str(error)[:160])
        return EXIT_ERR
    except Unverified as error:
        print('[switch] 시작 거절 — %s' % error)
        print('요약: switch-check 실행 불능 — %s' % str(error)[:160])
        return EXIT_ERR
