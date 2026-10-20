# 시험 범위(러너 모드 --test-scope — 검사 ID 가 아니다).
#
# 산출물 폴더 build-state.json 의 test_command · test_web_paths 를 읽어 시험 범위를 낸다 — make 를 펼치지 않고 시험을
# 돌지 않는다(실행은 Coordinator · coder-web). 정본 문면은 discipline-houserules §8 «시험 범위».
#   web 시험 경로(W) = web_test(없어도) · 루트 바로 아래 test/·tests/ 의 web/ · test_web_paths. 기록 폴더 아래는 W ·
#     시험 쪽 파일 · 소비자 · 바뀐 파일 어디에도 들지 않는다(TG2·TG3 와 같은 술어).
#   넓이 — exit 0 = 모든 단계의 시험 경로가 W 원소이고 W 원소마다 빠짐없이 모임 · 2 = 넓음 · 좁음 · 1 = 판정 불가.
#     설정 addopts 는 판정하지 않는다(프로젝트 기본).
#   소비자 — W · web/ · docs/ 밖 시험 쪽 파일 가운데 web 을 부르는 파일(늘 계산 · AST 상수 · import 만).
#   --since <커밋> — 바뀐 파일(그 커밋 뒤 첫 부모 사슬의 비병합 커밋 ∪ 병합이 들인 바꿈 ∪ 커밋 안 된 바꿈 ∪ 미추적
#     비무시 — 승인 병합이 상류판 그대로 들인 경로만 뺀다)로 계층 중 시험 · 슬라이스 끝 시험 · G2 더할 시험 · 프로젝트
#     전체 필요 줄을 단계마다 test_command 꼴로 낸다.

from __future__ import annotations

import ast
import configparser
import fnmatch
import json
import os
import posixpath
import re
import shlex
import subprocess
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .check_tests import _recorded, _support_name, conventional_test_path, js_in_test_tree
from .common import GIT_PINS, BackstopContext, _resolve, bc_dir_of, module_candidates

# pytest 의 값 받는 선택지(표 밖 긴 선택지 뒤 프로젝트 안 경로는 판정 불가 — 뜻 모름)
VALUED_SHORT: Set[str] = {'-c', '-p', '-m', '-k', '-n', '-o', '-W', '-r'}
VALUED_LONG: Set[str] = {'--ds', '--dc', '--rootdir', '--confcutdir', '--basetemp', '--import-mode', '--maxfail',
                         '--config-file', '--override-ini',
                         '--deselect', '--ignore', '--ignore-glob', '--junitxml', '--junit-xml', '--tb', '--durations',
                         '--log-level', '--dist', '--maxprocesses', '--numprocesses', '--postgresql-exec', '--postgresql-host',
                         '--postgresql-port', '--browser', '--browser-channel', '--base-url', '--output', '--tracing',
                         '--video', '--screenshot', '--timeout'}
SELECT_FLAGS: Set[str] = {'--lf', '--last-failed', '--sw', '--stepwise', '--sw-skip', '--stepwise-skip'}
DOC_EXTS: Set[str] = {'.md', '.rst', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.pdf'}
# web 전역 진입점 — 표준 트리 여덟 자리(호스트 settings · 루트 urls 가 부르는 web. 모듈 파일이 더해진다)
STANDARD_ENTRIES: Tuple[str, ...] = (
    'web/__init__.py', 'web/apps.py', 'web/urls.py', 'web/root/router/root_router.py',
    'web/root/handler/root_request_handler.py', 'web/root/handler/root_error_handler.py',
    'web/root/initializer/root_initializer.py', 'web/root/scaffold/view_model/root_vm.py')
DEFAULT_PATTERNS: List[str] = ['test_*.py', '*_test.py']
SLICE_END_WORKERS: int = 6  # 슬라이스 끝 시험 줄의 xdist 일꾼 상한(프로젝트 명령이 더 적으면 그대로 · 늘리지 않는다)
WEB_ALL: str = '<web 전체>'
_PLACEHOLDER: str = '\x00경로\x00'
_ENV_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*=')
_OPERATOR_RE = re.compile(r'^[();<>|&]+$')
_GLOB_CHARS: str = '*?[{}'  # 글롭 · 중괄호 펼침
_DOTTED_RE = re.compile(r'^web(?:\.\w+){2,}$')
_PATH_RE = re.compile(r'(?<![\w.-])web/([\w.-]+)')


class ScopeError(Exception):
    """판정 불가 사유(exit 1)."""


@dataclass
class Stage:
    index: int
    words: List[str]
    paths: List[Tuple[int, str]] = field(default_factory=list)  # (낱말 자리, 정규화 경로)
    marker: Optional[str] = None
    selectors: List[Tuple[str, str]] = field(default_factory=list)  # W 를 고르는 선택지(이름, 값 — 값 없는 선택지는 '')
    config: Optional[str] = None
    ds: Optional[str] = None
    fail_fast: Set[int] = field(default_factory=set)  # 떼어낼 낱말 자리
    xdist: Set[int] = field(default_factory=set)  # -n · --numprocesses 낱말 자리
    pytest_at: int = 0  # pytest 낱말 바로 뒤 자리
    workers: Optional[str] = None  # 단계의 -n 값(마지막)
    maxprocesses: Optional[str] = None  # 단계의 --maxprocesses 값
    maxprocesses_at: Set[int] = field(default_factory=set)  # --maxprocesses 낱말 자리
    addopts_workers: Optional[str] = None  # 설정 addopts 의 -n 값(없으면 None)
    addopts_max: Optional[str] = None  # 설정 addopts 의 --maxprocesses 값

    def _capped(self, cap: int) -> Tuple[List[str], Set[int]]:
        """일꾼 상한 cap — (pytest 낱말 바로 뒤에 넣을 낱말, 뺄 단계 낱말 자리). 단계 값이 이기고(없으면 addopts) ·
        auto · logical 은 그대로 두고 `--maxprocesses=<cap>`(--maxprocesses 가 이미 cap 이하면 그대로 · 단계의 더 큰 값은 뺀다 —
        xdist 가 둘 가운데 작은 쪽을 써 어느 기계에서도 늘지 않는다) · cap 보다 큰 수는 `-n <cap>` · 그 밖은 그대로."""
        value = self.workers if self.xdist else self.addopts_workers
        if value in ('auto', 'logical'):
            limit = self.maxprocesses if self.maxprocesses_at else self.addopts_max
            if limit is not None and limit.isdigit() and int(limit) <= cap:
                return [], set()
            return ['--maxprocesses=%d' % cap], set(self.maxprocesses_at)
        if value is not None and value.isdigit() and int(value) > cap:
            return ['-n', str(cap)], set(self.xdist)
        return [], set()

    def render(self, paths: List[str], keep_fail_fast: bool = True, serial: bool = False,
               cap: Optional[int] = None) -> str:
        """시험 경로 자리를 paths 로 둔 줄. serial 이면 일꾼 지정을 `-n0` 으로, cap 이면 일꾼을 cap 까지로(`_capped`) — 넣는
        낱말은 pytest 낱말 바로 뒤 · 일꾼 지정이 없는 단계는 그대로."""
        out: List[str] = []
        placed = False
        path_slots = {i for i, _p in self.paths}
        has_workers = bool(self.xdist) or self.addopts_workers is not None
        workers: List[str] = []
        drop: Set[int] = set()
        if serial and has_workers:
            workers, drop = ['-n0'], set(self.xdist)
        elif cap is not None:
            workers, drop = self._capped(cap)
        for i, word in enumerate(self.words):
            if workers and i == self.pytest_at:
                out.extend(workers)
            if i in drop:
                continue
            if i in path_slots:
                if not placed:
                    out.extend(paths)
                    placed = True
                continue
            if not keep_fail_fast and i in self.fail_fast:
                continue
            out.append(_shell_word(word))
        if workers and self.pytest_at >= len(self.words):
            out.extend(workers)
        if not placed:
            out.extend(paths)
        return ' '.join(out)


@dataclass
class Consumer:
    path: str
    reason: str
    targets: Set[str]  # web-상대 파일 · 폴더(또는 WEB_ALL) — 부르는 대상
    runs: List[str]  # 돌 경로(시험 파일 · conftest 폴더)
    shown_target: str = ''


# ---------------------------------------------------------------- 공통


def _shell_word(word: str) -> str:
    """한 낱말을 셸이 같은 낱말로 읽게 감싼다 — `이름=값` 은 `이름=` 뒤 값만 감싼다(앞 대입이 대입으로 남는다)."""
    if _ENV_RE.match(word):
        name, _eq, value = word.partition('=')
        return name + '=' + shlex.quote(value)
    return shlex.quote(word)


def _git(root: Path, *args: str, ok: Tuple[int, ...] = (0,), stdin: Optional[str] = None) -> str:
    r = subprocess.run(['git', *GIT_PINS, '-C', str(root), '-c', 'diff.relative=false', *args], capture_output=True,
                       input=stdin.encode('utf-8') if stdin is not None else None)
    if r.returncode not in ok:
        raise ScopeError('git %s 실패' % ' '.join(args[:2]))
    return r.stdout.decode('utf-8', 'surrogateescape')


def _norm(word: str, root: Path) -> str:
    """시험 경로 낱말 → root 상대 정규 경로(`경로::노드` 는 앞쪽 · 끝 `/` · `./` 정리 · 밖이면 절대 그대로)."""
    path = word.split('::', 1)[0]
    if os.path.isabs(path):
        try:
            path = os.path.relpath(path, str(root))
        except ValueError:
            return path
        if path.startswith('..'):
            return word.split('::', 1)[0]
    norm = posixpath.normpath(path.replace(os.sep, '/'))
    return norm


def _under(path: str, folder: str) -> bool:
    return folder == '.' or path == folder or path.startswith(folder.rstrip('/') + '/')


def _ancestors_only(paths: Iterable[str]) -> List[str]:
    out: List[str] = []
    for p in sorted(set(paths)):
        if not any(_under(p, q) for q in out):
            out.append(p)
    return out


# ---------------------------------------------------------------- 명령 읽기


def parse_command(command: str, root: Path) -> List[Stage]:
    if '$(' in command or '`' in command:
        raise ScopeError('명령 치환($( · 백틱)')
    lex = shlex.shlex(command, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    try:
        tokens = list(lex)
    except ValueError as error:
        raise ScopeError('명령 따옴표 해석 실패(%s)' % error)
    groups: List[List[str]] = [[]]
    for tok in tokens:
        value = tok.partition('=')[2] if _ENV_RE.match(tok) else ''
        if '$' in tok or tok.startswith('~') or '~' in value or any(c in tok for c in _GLOB_CHARS):
            raise ScopeError('셸이 풀 낱말(변수 · ~ · 글롭 · 중괄호 펼침) %s — 다시 감싸면 뜻이 바뀐다' % tok)
        if tok in ('&&', ';'):
            groups.append([])
        elif _OPERATOR_RE.match(tok):
            raise ScopeError('파이프 · 재지정 · 괄호 · 배경 실행(%s)' % tok)
        else:
            groups[-1].append(tok)
    if any(not g for g in groups):
        raise ScopeError('빈 단계')
    return [_parse_stage(i, words, root) for i, words in enumerate(groups, 1)]


def _parse_stage(index: int, words: List[str], root: Path) -> Stage:
    stage = Stage(index, words)
    j = 0
    while j < len(words) and _ENV_RE.match(words[j]):
        j += 1
    if j < len(words) and PurePosixPath(words[j]).name == 'make':
        raise ScopeError('단계 %d 이 make — 펼친 시험 실행 줄을 쓴다' % index)
    start = None
    for k in range(j, len(words)):
        if PurePosixPath(words[k]).name in ('pytest', 'py.test'):
            start = k + 1
            break
        if words[k] == '-m' and k + 1 < len(words) and words[k + 1] == 'pytest' and k > j:
            start = k + 2
            break
    if start is None:
        raise ScopeError('단계 %d 에 pytest 없음' % index)
    stage.pytest_at = start
    k = start
    positional_only = False
    while k < len(words):
        word = words[k]
        if positional_only or not word.startswith('-') or word == '-':
            stage.paths.append((k, _norm(word, root)))
            k += 1
            continue
        if word == '--':
            positional_only = True
            k += 1
            continue
        if word.startswith('--'):
            name, eq, value = word.partition('=')
            if name in ('--pyargs', '--rootdir'):
                raise ScopeError('단계 %d 의 %s' % (index, name))
            if name in VALUED_LONG:
                used = [k]
                if not eq:
                    if k + 1 >= len(words):
                        raise ScopeError('단계 %d 의 %s 값 없음' % (index, name))
                    value = words[k + 1]
                    used.append(k + 1)
                _option(stage, name, value, used, root)
                k += len(used)
                continue
            if name in SELECT_FLAGS:
                stage.selectors.append((word, ''))
            elif name == '--exitfirst':
                stage.fail_fast.add(k)
            elif not eq and k + 1 < len(words) and not words[k + 1].startswith('-') and (root / words[k + 1].split('::')[0]).exists():
                raise ScopeError('단계 %d 의 뜻 모를 선택지 %s 뒤 프로젝트 안 경로 %s' % (index, word, words[k + 1]))
            k += 1
            continue
        short = word[:2]
        if short in VALUED_SHORT:
            used = [k]
            value = word[2:]
            if not value:
                if k + 1 >= len(words):
                    raise ScopeError('단계 %d 의 %s 값 없음' % (index, short))
                value = words[k + 1]
                used.append(k + 1)
            _option(stage, short, value, used, root)
            k += len(used)
            continue
        if word == '-x':
            stage.fail_fast.add(k)
        k += 1
    return stage


def _option(stage: Stage, name: str, value: str, used: List[int], root: Path) -> None:
    if name == '-m':
        stage.marker = value
    elif name in ('-k', '--deselect', '--ignore', '--ignore-glob'):
        stage.selectors.append((name, value))  # W 를 가리키는지는 판정에서 가른다(-k 는 늘 좁음)
    elif name in ('-c', '--config-file'):
        stage.config = value
    elif name in ('-o', '--override-ini') and value.split('=', 1)[0].strip() == 'testpaths':
        raise ScopeError('단계 %d 의 %s testpaths' % (stage.index, name))
    elif name == '--ds':
        stage.ds = value
    elif name == '--maxfail':
        stage.fail_fast.update(used)
    elif name in ('-n', '--numprocesses'):
        stage.xdist.update(used)
        stage.workers = value
    elif name == '--maxprocesses':
        stage.maxprocesses = value
        stage.maxprocesses_at.update(used)


# ---------------------------------------------------------------- pytest 설정(첫 파일)


def _pytest_options(root: Path, config: Optional[str] = None) -> Tuple[Dict[str, object], Path]:
    """pytest 설정 → (옵션, 설정 파일 폴더). -c 파일이 없으면 pytest.ini → pyproject → tox.ini → setup.cfg 가운데 첫 파일."""
    def ini(path: Path, sections: Tuple[str, ...], required: bool) -> Optional[Dict[str, object]]:
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read(path, encoding='utf-8')
        for section in sections:
            if cfg.has_section(section):
                return dict(cfg.items(section))
        return None if required else {}

    def toml(path: Path) -> Optional[Dict[str, object]]:
        import tomllib
        found = tomllib.loads(path.read_text(encoding='utf-8')).get('tool', {}).get('pytest', {}).get('ini_options')
        return dict(found) if isinstance(found, dict) else None

    try:
        if config is not None:
            path = Path(config) if os.path.isabs(config) else root / config
            if not path.is_file():
                raise ScopeError('-c 설정 파일 없음 %s' % config)
            got = toml(path) if path.suffix == '.toml' else ini(path, ('pytest', 'tool:pytest'), False)
            return got or {}, path.parent
        for name in ('pytest.ini', 'pyproject.toml', 'tox.ini', 'setup.cfg'):
            path = root / name
            if not path.is_file():
                continue
            if name == 'pytest.ini':
                return ini(path, ('pytest',), False) or {}, root
            got = toml(path) if name == 'pyproject.toml' else ini(path, ('pytest',) if name == 'tox.ini' else ('tool:pytest',), True)
            if got is not None:
                return got, root
    except (configparser.Error, ValueError, OSError, UnicodeDecodeError) as error:
        raise ScopeError('pytest 설정 읽기 실패(%s)' % error)
    return {}, root


def _xdist_of(words: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """설정 addopts 낱말의 일꾼 지정(`-n` · `--numprocesses`) · `--maxprocesses` 마지막 값 — 없으면 None."""
    workers: Optional[str] = None
    limit: Optional[str] = None
    for i, w in enumerate(words):
        name, eq, value = w.partition('=')
        following = words[i + 1] if i + 1 < len(words) else ''
        if w.startswith('-n') and not w.startswith('--'):
            workers = w[2:] or following
        elif name == '--numprocesses':
            workers = value if eq else following
        elif name == '--maxprocesses':
            limit = value if eq else following
    return workers, limit


def _words(value: object) -> List[str]:
    if isinstance(value, str):
        try:
            return shlex.split(value)
        except ValueError as error:
            raise ScopeError('pytest 설정 읽기 실패(%s)' % error)
    if isinstance(value, list):
        return [str(v) for v in value]
    return []


# ---------------------------------------------------------------- 넓이


def _negates(a: Optional[str], b: Optional[str]) -> bool:
    if a is None or b is None:
        return False
    x, y = ' '.join(a.split()), ' '.join(b.split())
    return x in ('not ' + y, 'not (' + y + ')')


def judge(stages: List[Stage], web_paths: List[str], root: Path) -> Tuple[List[str], List[str]]:
    """넓음 · 좁음 줄."""
    broad: List[str] = []
    narrow: List[str] = []
    marks: Dict[str, List[Optional[str]]] = {w: [] for w in web_paths}
    for stage in stages:
        paths = [p for _i, p in stage.paths]
        source = ''
        if not paths:
            options, folder = _pytest_options(root, stage.config)
            testpaths = _words(options.get('testpaths', ''))
            if testpaths:
                base = os.path.relpath(str(folder), str(root))
                paths = [posixpath.normpath(posixpath.join(base.replace(os.sep, '/'), t)) for t in testpaths]
                source = '(testpaths)'
            else:
                broad.append('[test-scope] 넓음 — 단계 %d 경로 없음 — testpaths 도 없어 루트 전체' % stage.index)
                continue
        for p in paths:
            if p in marks:
                marks[p].append(stage.marker)
            elif not any(_under(p, w) for w in web_paths):
                broad.append('[test-scope] 넓음 — 단계 %d 경로 %s%s' % (stage.index, p, source))
        for name, value in stage.selectors:
            if name in ('--deselect', '--ignore', '--ignore-glob'):
                target = _norm(value, root)  # 글롭 문자는 명령 읽기에서 판정 불가 — 값은 경로 글자다
                if not any(_under(target, w) or _under(w, target) for w in web_paths):
                    continue
            narrow.append('[test-scope] 좁음 — 단계 %d 고르는 선택지 %s' % (stage.index, (name + ' ' + value).rstrip()))
    for w in web_paths:
        got = marks[w]
        if None in got or any(_negates(m2, m) for m in got for m2 in got):
            continue
        why = '모으는 단계 없음' if not got else '표식 %s 만 — 짝(-m "not …") 단계 없음' % ' · '.join(repr(m) for m in got)
        narrow.append('[test-scope] 좁음 — 빠진 web 시험 경로 %s(%s)' % (w, why))
    return broad, narrow


# ---------------------------------------------------------------- 파일 · 시험 쪽


class Project:
    def __init__(self, root: Path, patterns: List[str]) -> None:
        self.root = root
        self.patterns = patterns
        out = _git(root, 'ls-files', '-z', '--cached', '--others', '--exclude-standard', '--', '.')
        self.files: List[str] = sorted({p for p in out.split('\0') if p and not _recorded(p) and (root / p).is_file()})
        self.dirs: Set[str] = set()
        for p in self.files:
            parts = p.split('/')
            for k in range(1, len(parts)):
                self.dirs.add('/'.join(parts[:k]))
        self.tops: Set[str] = {p.split('/')[0] for p in self.files if '/' in p}
        self._trees: Dict[str, Optional[ast.AST]] = {}

    def test_side(self, rel: str) -> bool:
        if _recorded(rel):
            return False
        if rel.endswith('.py'):
            return conventional_test_path(rel) or any(fnmatch.fnmatch(PurePosixPath(rel).name, p) for p in self.patterns)
        return js_in_test_tree(rel)

    def runnable(self, rel: str) -> bool:
        name = PurePosixPath(rel).name
        return (rel.endswith('.py') and name != 'conftest.py' and not _support_name(rel) and not _recorded(rel)
                and any(fnmatch.fnmatch(name, p) for p in self.patterns))

    def text(self, rel: str) -> Optional[str]:
        try:
            return (self.root / rel).read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            return None

    def tree(self, rel: str) -> Optional[ast.AST]:
        if rel not in self._trees:
            text = self.text(rel)
            try:
                self._trees[rel] = ast.parse(text) if text is not None else None
            except (SyntaxError, ValueError, RecursionError):
                self._trees[rel] = None
        return self._trees[rel]

    def module_file(self, dotted: str, origin: Optional[str] = None, level: int = 0) -> Optional[str]:
        for cand in module_candidates(dotted, origin or '.', level):
            if (self.root / cand).is_file():
                return cand
        return None

    def longest_module(self, dotted: str) -> Optional[str]:
        """web.… 점 경로 → 가장 긴 실재 모듈 파일(`web` 은 web/apps.py)."""
        parts = dotted.split('.')
        if parts == ['web']:
            return 'web/apps.py'
        for cut in range(len(parts), 1, -1):
            found = self.module_file('.'.join(parts[:cut]))
            if found is not None:
                return found
        return None


def _web_paths(root: Path, extra: List[str]) -> List[str]:
    out = ['web_test'] + [p for p in ('test/web', 'tests/web') if (root / p).is_dir()]
    for p in extra:
        if p not in out:
            out.append(p)
    for p in extra:  # 원소마다 «같아야 모은다» — 조상 · 자손이 함께 있으면 어느 명령도 0 이 될 수 없다
        other = next((w for w in out if w != p and (_under(p, w) or _under(w, p))), None)
        if other is not None:
            raise ScopeError('test_web_paths 경로 %s 가 web 시험 경로 %s 의 조상 · 자손' % (p, other))
    return out


# ---------------------------------------------------------------- settings · 전역 진입점


def _settings_module(root: Path, stages: List[Stage], options: Dict[str, object]) -> Optional[str]:
    for stage in stages:
        if stage.ds:
            return stage.ds
    value = options.get('DJANGO_SETTINGS_MODULE') or options.get('django_settings_module')
    if isinstance(value, str) and value.strip():
        return value.strip()
    manage = root / 'manage.py'
    if manage.is_file():
        m = re.search(r'''DJANGO_SETTINGS_MODULE["']\s*,\s*["']([\w.]+)["']''', manage.read_text(encoding='utf-8', errors='replace'))
        if m:
            return m.group(1)
    return None


def _settings_files(project: Project, module: Optional[str]) -> Tuple[Set[str], Optional[str], Optional[str]]:
    """→ (settings 패키지 .py 들, 그 부모의 urls.py, ROOT_URLCONF 모듈 파일). 못 찾으면 빈 값."""
    if not module:
        return set(), None, None
    parts = module.split('.')
    cut = next((i for i, p in enumerate(parts) if p.startswith('settings')), len(parts) - 1)
    stem = '/'.join(parts[:cut + 1])
    if (project.root / stem).is_dir():
        files = {p for p in project.files if p.startswith(stem + '/') and p.endswith('.py')}
    elif (project.root / (stem + '.py')).is_file():
        files = {stem + '.py'}
    else:
        found = project.module_file(module)
        files = {found} if found else set()
    if not files:
        return set(), None, None
    parent = posixpath.dirname(stem)
    urls = posixpath.join(parent, 'urls.py') if parent else 'urls.py'
    urls_file = urls if (project.root / urls).is_file() else None
    urlconf = None
    for rel in sorted(files):
        tree = project.tree(rel)
        for node in ast.walk(tree) if tree is not None else []:
            if (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'ROOT_URLCONF' for t in node.targets)
                    and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
                urlconf = project.module_file(node.value.value)
    return files, urls_file, urlconf


def _global_entries(project: Project, settings: Set[str], urlconf: Optional[str]) -> Set[str]:
    entries: Set[str] = set(STANDARD_ENTRIES)
    for rel in sorted(settings | ({urlconf} if urlconf else set())):
        tree = project.tree(rel)
        for node in ast.walk(tree) if tree is not None else []:
            names: List[str] = []
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value == 'web' or node.value.startswith('web.'):
                    names.append(node.value)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module and (
                    node.module == 'web' or node.module.startswith('web.')):
                names += [node.module + '.' + a.name for a in node.names if a.name != '*'] or [node.module]
            elif isinstance(node, ast.Import):
                names += [a.name for a in node.names if a.name == 'web' or a.name.startswith('web.')]
            for name in names:
                found = project.longest_module(name)
                if found is not None and found.startswith('web/'):
                    entries.add(found)
    return entries


# ---------------------------------------------------------------- 소비자


def _web_refs(project: Project, rel: str, web_files: Set[str], web_dirs: Set[str]
              ) -> List[Tuple[str, Set[str], str]]:
    """한 파일이 web 을 부르는 자리 → [(까닭, 부르는 대상(web-상대 · WEB_ALL), 보이는 대상)]."""
    tree = project.tree(rel)
    if tree is None:
        return []
    parents: Dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
    out: List[Tuple[str, Set[str], str]] = []

    def module_targets(dotted: str, names: List[str]) -> Set[str]:
        parts = dotted.split('.')
        if parts[0] != 'web':
            return set()
        return {t for t in _resolve(parts[1:], names, web_files, web_dirs) if t in web_files}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                top = a.name.split('.')[0]
                if top in ('web', 'web_test'):
                    out.append(('import %s' % a.name, module_targets(a.name, []), a.name))
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            top = node.module.split('.')[0]
            if top in ('web', 'web_test'):
                names = [a.name for a in node.names if a.name != '*']
                out.append(('import %s' % node.module, module_targets(node.module, names), node.module))
        elif (isinstance(node, ast.Constant) and isinstance(node.value, str)
              and not isinstance(parents.get(id(node)), ast.Expr)):  # 독스트링 · 문 자리 글자는 걸리지 않는다
            s = node.value
            if _DOTTED_RE.match(s):
                parts = s.split('.')
                if (project.root / 'web' / parts[1] / parts[2]).is_dir() or (project.root / 'web' / parts[1] / (parts[2] + '.py')).is_file():
                    found = project.longest_module(s)
                    out.append(('점 경로 %s' % s, {found[4:]} if found else set(), s))
                    continue
            for m in _PATH_RE.finditer(s):
                tail = m.group(1)
                tail_path = s[m.start(1):].split('?')[0].split('#')[0]
                for cand in (tail_path, 'static/' + tail_path, tail, 'static/' + tail):
                    cand = posixpath.normpath(cand)
                    if (project.root / 'web' / cand).exists():
                        out.append(('경로 글자 %s' % s, {cand}, 'web/' + cand))
                        break
                else:
                    continue
                break
            if s == 'web':
                parent = parents.get(id(node))
                whole = False
                if isinstance(parent, (ast.Tuple, ast.List, ast.Set)):
                    whole = any(isinstance(e, ast.Constant) and isinstance(e.value, str) and e.value != 'web'
                                and e.value in project.tops for e in parent.elts)
                elif isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Div):
                    whole = True
                elif isinstance(parent, ast.Call):
                    name = parent.func.attr if isinstance(parent.func, ast.Attribute) else (
                        parent.func.id if isinstance(parent.func, ast.Name) else '')
                    full = ''
                    if isinstance(parent.func, ast.Attribute) and isinstance(parent.func.value, ast.Attribute):
                        full = parent.func.value.attr + '.' + name
                    whole = name in ('joinpath', 'Path') or full == 'path.join' or name == 'PurePath'
                if whole:
                    out.append(('web 전체를 읽음', {WEB_ALL}, 'web 전체'))
    return out


def _imports_of(project: Project, rel: str) -> Set[str]:
    """한 파일이 import 하는 프로젝트 파일(root 상대)."""
    tree = project.tree(rel)
    found: Set[str] = set()
    for node in ast.walk(tree) if tree is not None else []:
        if isinstance(node, ast.Import):
            for a in node.names:
                got = project.module_file(a.name)
                if got:
                    found.add(got)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ''
            for a in node.names:
                sub = project.module_file((mod + '.' + a.name) if mod else a.name, rel, node.level)
                if sub:
                    found.add(sub)
                    continue
                got = project.module_file(mod, rel, node.level) if (mod or node.level) else None
                if got:
                    found.add(got)
    return found


def _importers(project: Project, tests: Iterable[str]) -> Dict[str, Set[str]]:
    """import 되는 파일 → 그것을 import 하는 시험 파일(한 걸음 · tests 가운데 돌릴 수 있는 것)."""
    found: Dict[str, Set[str]] = {}
    for t in tests:
        if project.runnable(t):
            for dep in _imports_of(project, t):
                found.setdefault(dep, set()).add(t)
    return found


def _outside(rel: str, web_paths: List[str]) -> bool:
    """web 시험 경로 · web/ · docs/ · 기록 폴더 밖 — 소비자 · G2 더할 시험이 보는 자리."""
    return not (rel.startswith('web/') or rel.startswith('docs/') or _recorded(rel)
                or any(_under(rel, w) for w in web_paths))


def consumers(project: Project, web_paths: List[str], settings: Set[str], urls_file: Optional[str],
              urlconf: Optional[str], web_files: Set[str], web_dirs: Set[str]) -> Tuple[List[Consumer], List[str]]:
    """소비자 목록 · 해석 실패 알림."""
    notes: List[str] = []
    test_side = [p for p in project.files if p.endswith('.py') and _outside(p, web_paths) and project.test_side(p)]
    plain = [p for p in project.files if p.endswith('.py') and _outside(p, web_paths) and not project.test_side(p)
             and p not in settings and p != urls_file and p != urlconf]
    result: Dict[str, Consumer] = {}

    def refs_of(rel: str) -> List[Tuple[str, Set[str], str]]:
        text = project.text(rel)
        if text is None or 'web' not in text:
            return []
        if project.tree(rel) is None:
            notes.append('[test-scope] 알림 — %s 구문 해석 실패 · 소비자 판정 밖' % rel)
            return []
        return _web_refs(project, rel, web_files, web_dirs)

    for rel in test_side:
        refs = refs_of(rel)
        if refs:
            targets = set().union(*(t for _r, t, _s in refs))
            result[rel] = Consumer(rel, refs[0][0], targets, [], refs[0][2])
    bridges: Dict[str, Tuple[Set[str], str]] = {}
    for rel in plain:
        refs = refs_of(rel)
        if refs:
            bridges[rel] = (set().union(*(t for _r, t, _s in refs)), refs[0][2])
    if bridges:
        for rel in test_side:
            if rel in result:
                continue
            via = sorted(_imports_of(project, rel) & set(bridges))
            if via:
                targets = set().union(*(bridges[v][0] for v in via))
                result[rel] = Consumer(rel, '한 걸음 %s' % via[0], targets, [], bridges[via[0]][1])
    # 돌 경로 — 시험 파일은 그 파일 · conftest 는 그 폴더 · 지원 모듈은 그것을 import 하는 시험(한 걸음)
    importers: Optional[Dict[str, Set[str]]] = None
    for rel, item in sorted(result.items()):
        name = PurePosixPath(rel).name
        if name == 'conftest.py':
            folder = posixpath.dirname(rel) or '.'
            item.runs = [folder]
        elif project.runnable(rel):
            item.runs = [rel]
        else:
            if importers is None:
                importers = _importers(project, test_side)
            item.runs = sorted(importers.get(rel, set()))
    return [result[k] for k in sorted(result)], notes


# ---------------------------------------------------------------- --since


def changed_files(root: Path, since: str, folder: Path) -> Tuple[List[str], List[str]]:
    """바뀐 파일 · 알림 — 그 커밋 뒤 첫 부모 사슬의 비병합 커밋 ∪ 병합이 들인 바꿈(승인 병합 M 이 상류판 그대로 —
    blob(M,p) == blob(M^2,p) — 들인 경로만 뺀다 · 충돌 해소 · 미승인 병합은 센다) ∪ 커밋 안 된 바꿈 ∪ 미추적 비무시
    (기록 폴더 뺌). 승인 술어는 TG4 기준판과 같다."""
    from .debt import DebtError  # 함수 안 import: subst → debt → 검사 모듈 적재와 순환하지 않는다
    from .subst import _approved_merges, _chain, _names

    try:
        oid = _git(root, 'rev-parse', '--verify', since + '^{commit}').strip()
    except ScopeError:
        raise ScopeError('--since 커밋 해석 불가 %s' % since)
    logged = _git(root, 'log', '--first-parent', '--no-merges', '--no-renames', '--format=', '--name-only', '-z',
                  '--relative', '%s..HEAD' % oid, '--', '.')
    pending = _git(root, 'diff', '--no-ext-diff', '--no-textconv', '--name-only', '--no-renames', '--relative', '-z',
                   'HEAD', '--', '.')
    untracked = _git(root, 'ls-files', '--others', '--exclude-standard', '-z', '--', '.')
    names: Set[str] = set()
    for chunk in (logged, pending, untracked):
        names |= {p.strip('\n') for p in chunk.split('\0') if p.strip('\n')}
    notes: List[str] = []
    try:
        chain = _chain(root, oid, 'HEAD')
        merges = [(sha, parents) for sha, parents in chain if len(parents) > 1]
        approved: Dict[str, str] = {}
        if merges:
            try:
                approved, _notes = _approved_merges(root, folder, oid, chain)
            except DebtError as error:
                notes.append('[test-scope] 알림 — 승인 병합 판정 불가(%s) · 병합이 들인 바꿈을 모두 센다' % error)
        for sha, parents in merges:
            brought = _names(root, parents[0], sha, ['.'])
            if sha in approved:
                brought &= _names(root, parents[1], sha, ['.'])  # 상류판과 다른 경로(충돌 해소 · 레인 편집)만
            names |= brought
    except DebtError as error:
        raise ScopeError('병합 유입 읽기 실패(%s)' % error)
    return sorted(p for p in names if not _recorded(p)), notes


def _unit_of(rel: str, areas: Set[str]) -> Optional[str]:
    """web-상대 파일 → web_test 미러 단위(BC · root · common · design_system · 옛 배치 맨 위 폴더 · 조각 CSS 는 소유자)."""
    s = rel.split('/')
    if s[0] == 'application':
        return bc_dir_of(rel, areas) or ('/'.join(s[:2]) if len(s) > 2 else None)
    if s[0] == 'static':
        if len(s) >= 4 and s[1] == 'application':
            return '/'.join(['application'] + s[2:-1])
        if len(s) == 3 and s[1] == 'root':
            return 'root'
        return None
    if s[0] in ('root', 'common', 'design_system'):
        return s[0]
    if len(s) == 1 or s[0] == 'locale':
        return None
    return s[0]


def _closure_names(rel: str) -> List[str]:
    """닫힘 파일을 시험이 부르는 글자 — 저장소 상대 경로 · 템플릿 이름 · static 이름 · 점 경로."""
    names = ['web/' + rel]
    if rel.endswith('.html'):
        names.append(rel)
    if rel.startswith('static/'):
        names.append('web/' + rel[len('static/'):])
    if rel.startswith('design_system/'):
        names.append(rel)
    if rel.endswith('.py'):
        dotted = 'web.' + rel[:-3].replace('/', '.')
        if dotted.endswith('.__init__'):
            dotted = dotted[:-len('.__init__')]
        if dotted.count('.') >= 1:
            names.append(dotted)
    return names


def _grep(root: Path, patterns: Set[str], paths: List[str]) -> Set[str]:
    if not patterns or not paths:
        return set()
    # 사용자 git 설정 grep.fullName 이 켜져 있어도 적중 경로는 프로젝트 루트 기준이다 · 사용자 전역 속성(core.attributesFile)의
    # `-diff` 가 글 파일을 바이너리로 보이게 해 `-I` 가 건너뛰지 않게 그 파일을 끈다(debt.reference_lines 와 같다)
    out = _git(root, '-c', 'grep.fullName=false', '-c', 'core.attributesFile=', 'grep', '--untracked', '-I', '-l', '-F', '-z',
               '-f', '-', '--', *paths, ok=(0, 1), stdin='\n'.join(sorted(patterns)) + '\n')
    return {p for p in out.split('\0') if p}


def since_lines(project: Project, stages: List[Stage], web_paths: List[str], items: List[Consumer],
                entries: Set[str], since: str, folder: Path, web_files: Set[str], web_dirs: Set[str]) -> List[str]:
    root = project.root
    changed, out = changed_files(root, since, folder)
    present = [p for p in changed if (root / p).is_file()]
    w_existing = [w for w in web_paths if (root / w).exists()]
    w_tests = {p for p in project.files if project.runnable(p) and any(_under(p, w) for w in web_paths)}

    def in_w(rel: str) -> bool:
        return any(_under(rel, w) for w in web_paths)

    changed_tests = [p for p in present if project.runnable(p) and not p.startswith('docs/')]
    changed_support = [p for p in present if p.endswith('.py') and project.test_side(p) and not project.runnable(p)
                       and PurePosixPath(p).name != 'conftest.py']
    changed_conftests = [p for p in changed if PurePosixPath(p).name == 'conftest.py' and project.test_side(p)]

    # 바뀐 web 파일의 거꾸로 참조 닫힘(바뀐 web 파일이 없으면 BackstopContext 를 만들지 않는다 — 닫힘이 빈다)
    closure: Set[str] = set()
    areas: Set[str] = set()
    seeds = {p[len('web/'):] for p in changed if p.startswith('web/')}
    if seeds and (root / 'web').is_dir():
        ctx = BackstopContext.build(root, None, True)
        areas = ctx.areas
        reverse: Dict[str, Set[str]] = {}
        for f in ctx.files:
            for edge in ctx.edges_of(f):
                if edge.internal and edge.target:
                    reverse.setdefault(edge.target, set()).add(f)
        closure = set(seeds)
        stack = list(seeds)
        while stack:
            for src in reverse.get(stack.pop(), ()):
                if src not in closure:
                    closure.add(src)
                    stack.append(src)
    end: Set[str] = set()
    for rel in closure:  # ① 닫힘 단위의 web_test 미러
        unit = _unit_of(rel, areas)
        if unit and (root / 'web_test' / unit).is_dir():
            end.add('web_test/' + unit)
    if closure:  # ② 닫힘 모듈을 import 하는 W 시험 · ③ 닫힘 글자를 쓰는 W 파일
        for rel in sorted(w_tests):
            tree = project.tree(rel)
            for node in ast.walk(tree) if tree is not None else []:
                hit: Set[str] = set()
                if isinstance(node, ast.Import):
                    for a in node.names:
                        if a.name.split('.')[0] == 'web':
                            hit |= set(_resolve(a.name.split('.')[1:], [], web_files, web_dirs))
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module and node.module.split('.')[0] == 'web':
                    hit |= set(_resolve(node.module.split('.')[1:], [a.name for a in node.names], web_files, web_dirs))
                if hit & closure:
                    end.add(rel)
                    break
        patterns = {name for rel in closure for name in _closure_names(rel)}
        end |= {p for p in _grep(root, patterns, w_existing) if p in w_tests}
    end |= set(changed_tests)  # ④ 바뀐 시험 파일(W 안 · 밖)
    if changed_support:  # ⑤ 바뀐 지원 모듈을 import 하는 W 시험 · 바뀐 conftest 폴더의 시험
        support = set(changed_support)
        end |= {t for t in w_tests if _imports_of(project, t) & support}
    for conftest in changed_conftests:  # 루트 conftest 는 W 전체(프로젝트 전체는 G2 몫) · 지운 폴더는 넣지 않는다
        folder_of = posixpath.dirname(conftest)
        if not folder_of:
            end |= set(w_existing)
        elif (root / folder_of).is_dir():
            end.add(folder_of)
    root_conftest_consumer = False
    for item in items:  # ⑥ 닫힘에 닿는 소비자 · 닫힘이 비지 않으면 web 전체를 읽는 소비자
        if item.path == 'conftest.py':
            root_conftest_consumer = True
            continue
        touches = closure and (WEB_ALL in item.targets or any(
            t in closure or any(c.startswith(t.rstrip('/') + '/') for c in closure) for t in item.targets if t != WEB_ALL))
        if touches:
            end |= set(item.runs)
    whole = False
    selected = {t for t in w_tests if any(_under(t, e) for e in end)}
    if w_tests and w_tests <= selected:
        whole = True
        end = {e for e in end if not in_w(e)} | set(w_existing)
    # G2 더할 시험 — 소비자 전부 · 바뀐 W 밖 시험 파일 · 바뀐 W 밖 지원 모듈을 import 하는 W 밖 시험 · conftest 폴더(한 걸음 ·
    # 루트 conftest 면 프로젝트 전체 필요) · 바뀐 W 밖 conftest 폴더(루트 conftest 는 프로젝트 전체 필요)
    g2: Set[str] = {r for item in items if item.path != 'conftest.py' for r in item.runs}
    g2 |= {p for p in changed_tests if not in_w(p)}
    outside_support = {p for p in changed_support if _outside(p, web_paths)}
    support_root_conftest: List[str] = []
    if outside_support:
        outside_files = [p for p in project.files if _outside(p, web_paths)]
        importers = _importers(project, outside_files)
        g2 |= {t for dep in outside_support for t in importers.get(dep, ())}
        for conftest in (p for p in outside_files if PurePosixPath(p).name == 'conftest.py'):
            used = sorted(_imports_of(project, conftest) & outside_support)
            if not used:
                continue
            folder_of = posixpath.dirname(conftest)
            if folder_of:
                g2.add(folder_of)
            else:
                support_root_conftest += used
    g2 |= {posixpath.dirname(c) for c in changed_conftests
           if posixpath.dirname(c) and _outside(c, web_paths) and (root / posixpath.dirname(c)).is_dir()}

    def ext(rel: str) -> str:
        return PurePosixPath(rel).suffix.lower()

    project_wide: List[str] = []
    for rel in changed:
        if rel == 'conftest.py':
            project_wide.append('루트 conftest')
        elif rel in entries:
            project_wide.append('전역 진입점 %s' % rel)
        elif not (rel.startswith('web/') or rel.startswith('docs/') or in_w(rel) or project.test_side(rel)
                  or ext(rel) in DOC_EXTS):
            project_wide.append(rel)
    if root_conftest_consumer:
        project_wide.append('루트 conftest 가 web 을 부름')
    project_wide += ['루트 conftest 가 import 하는 지원 모듈 %s' % rel for rel in support_root_conftest]

    def lines(name: str, paths: Set[str], keep: bool, serial: bool = False, cap: Optional[int] = None) -> List[str]:
        if not paths:
            return []
        quoted = [shlex.quote(p) for p in _ancestors_only(paths)]
        return ['[test-scope] %s %d: %s' % (name, s.index, s.render(quoted, keep, serial, cap)) for s in stages]

    layer = lines('계층 중 시험', set(changed_tests), True, serial=True)  # 좁은 계층 실행은 일꾼 하나가 빠르다(G-5)
    out += layer
    if whole:
        out.append('[test-scope] 슬라이스 끝 시험 = web 시험 전체')
    slice_end = lines('슬라이스 끝 시험', end, False, cap=SLICE_END_WORKERS)  # 일꾼 최대 6(사용자 결정)
    out += slice_end
    more = lines('G2 더할 시험', g2, False)
    out += more
    out += ['[test-scope] 프로젝트 전체 필요 — %s' % why for why in project_wide]
    out.append('[test-scope] 계층 중 시험 줄 %d · 슬라이스 끝 시험 줄 %d · G2 더할 시험 줄 %d · 프로젝트 전체 필요 %d'
               % (len(layer), len(slice_end), len(more), len(project_wide)))
    return out


# ---------------------------------------------------------------- 진입


def _read_state(folder_arg: str, root: Path) -> Tuple[str, List[str], Path]:
    """산출물 폴더(프로젝트 루트 기준 · 기록 폴더 `.dddjango-web/` 아래 실재 폴더) → (test_command, test_web_paths, 폴더)."""
    records = (root / '.dddjango-web').resolve()
    folder = (Path(folder_arg) if os.path.isabs(folder_arg) else root / folder_arg).resolve()
    if not folder.is_relative_to(records) or folder == records:
        raise ScopeError('산출물 폴더는 %s/ 아래여야 한다 — %s' % (records, folder_arg))
    if not (folder / 'build-state.json').is_file():
        raise ScopeError('build-state.json 없음 — %s' % folder_arg)
    try:
        state = json.loads((folder / 'build-state.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise ScopeError('build-state.json 읽기 실패(%s)' % error)
    if not isinstance(state, dict) or not isinstance(state.get('test_command'), str) or not state['test_command'].strip():
        raise ScopeError('build-state.json 의 test_command 가 글자가 아님')
    extra = state.get('test_web_paths', [])
    if not isinstance(extra, list) or not all(isinstance(p, str) for p in extra):
        raise ScopeError('build-state.json 의 test_web_paths 가 글자 목록이 아님')
    paths: List[str] = []
    for p in extra:
        norm = _norm(p, root)
        if os.path.isabs(norm) or norm.startswith('..') or norm == '.' or not (root / norm).exists():
            raise ScopeError('test_web_paths 경로 없음 %s' % p)
        if _recorded(norm):
            raise ScopeError('test_web_paths 경로가 기록 폴더 안 %s' % p)
        paths.append(norm)
    return state['test_command'], paths, folder


def run_scope(root: Path, folder_arg: str, since: Optional[str]) -> Tuple[int, List[str]]:
    command, extra, folder = _read_state(folder_arg, root)
    if _git(root, 'rev-parse', '--is-inside-work-tree', ok=(0, 128)).strip() != 'true':
        raise ScopeError('git 저장소 아님')
    stages = parse_command(command, root)
    for stage in stages:
        stage.addopts_workers, stage.addopts_max = _xdist_of(_words(_pytest_options(root, stage.config)[0].get('addopts', '')))
    options, _folder = _pytest_options(root, next((s.config for s in stages if s.config), None))
    patterns = _words(options.get('python_files', '')) or list(DEFAULT_PATTERNS)
    project = Project(root, patterns)
    web_paths = _web_paths(root, extra)
    broad, narrow = judge(stages, web_paths, root)
    settings, urls_file, urlconf = _settings_files(project, _settings_module(root, stages, options))
    web_files: Set[str] = set()
    web_dirs: Set[str] = set()
    if (root / 'web').is_dir():
        web_files = {p[len('web/'):] for p in project.files if p.startswith('web/') and p.endswith('.py')}
        web_dirs = {d[len('web/'):] for d in project.dirs if d.startswith('web/')}
    items, notes = consumers(project, web_paths, settings, urls_file, urlconf, web_files, web_dirs)
    out: List[str] = []
    for stage in stages:
        out.append('[test-scope] 단계 %d: %s' % (stage.index, stage.render(['{경로}'])))
    shown = []
    for w in web_paths:
        if not (root / w).exists():
            shown.append('%s(없음)' % w)
        else:
            shown.append('%s(시험 파일 %d)' % (w, sum(1 for p in project.files if project.runnable(p) and _under(p, w))))
    out.append('[test-scope] web 시험 경로: ' + ' · '.join(shown))
    out.append('[test-scope] 소비자 %d:' % len(items))
    for item in items:
        out.append('  %s — %s · 부르는 대상 %s' % (item.path, item.reason, item.shown_target))
    out += notes
    out += broad + narrow
    if broad or narrow:
        out.append('[test-scope] 판정 — 쓰지 않는다 — exit 2')
        return 2, out
    if since is not None:
        entries = _global_entries(project, settings, urlconf)
        out += since_lines(project, stages, web_paths, items, entries, since, folder, web_files, web_dirs)
    out.append('[test-scope] 판정 — web 시험 경로만 · 소비자 %d — exit 0' % len(items))
    return 0, out


def cli_test_scope(root: Path, folder_arg: str, since: Optional[str]) -> int:
    try:
        code, lines = run_scope(root, folder_arg, since)
    except ScopeError as error:
        print('[test-scope] 판정 불가 — %s — exit 1' % error)
        return 1
    print('\n'.join(lines))
    return code
