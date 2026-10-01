#!/usr/bin/env python3
"""static_delta — G2 전 정적 검사(린트·서식·타입) 도구 (dddjango-web).

정본: 커맨드 Phase 2 진입 준비 ①′ · step 3-1 «G2 전 정적 검사». 레인이 들인 위반만 막고 프로젝트가 뺀 파일·main 이
들인 위반으로 가짜로 막지 않는다. 검사는 아무 파일도 고치지 않는다(`ruff --fix`·쓰기 `ruff format` 없음) — 쓰는 것은
산출물 폴더의 기록 파일(`static-entry.txt` · `mypy-baseline*.txt`)뿐이다.

사용:
  python static_delta.py --project-root <루트> --build <산출물 폴더> --phase entry [--mypy-args "<대상·옵션>"]
  python static_delta.py --project-root <루트> --build <산출물 폴더> --phase g2 [--mypy-args …] [--base-branch <가지>]…

규칙:
  · 설정(도구마다): ruff = pyproject `[tool.ruff]`·`ruff.toml`·`.ruff.toml` · mypy = `mypy.ini`·`.mypy.ini`·
    pyproject `[tool.mypy]`·`setup.cfg [mypy]` — 또는 `.pre-commit-config.yaml` 훅·`Makefile`(설치 줄 말고 `ruff check|format`
    · `mypy` 를 부르는 줄)이 그 도구를 돌린다. ruff 설정 파일이 없으면(훅·Makefile 로만 감지) 서식은 «판정 불가»다 — 훅
    인자를 넘기지 않으므로 기본값 재포맷을 요구하지 않는다.
  · 실행기(고정 순서 · 이미 있는 환경만): `uv.lock` 이 있으면 `uv run --frozen --no-sync <도구>` → `.venv/bin/<도구>`.
    설정은 있는데 둘 다 안 되면 STOP(exit 3).
  · mypy 명령 = `--mypy-args` > 진입 기준선 머리 `# 대상` > pre-commit 훅(`pass_filenames: false` 의 entry 에서
    `mypy` 뒤) > Makefile 의 mypy 줄 — 없으면 «mypy 대상 미정 — 생략».
  · entry: 두 도구의 설정·실행기를 확인해 버전을 찍고 mypy 를 한 번 돌려 `<산출물 폴더>/mypy-baseline.txt` 를 쓴다.
    찍은 줄 전부를 `<산출물 폴더>/static-entry.txt` 로도 남긴다 — coder 는 그 `[static] ruff …` 줄이 «서식 판정 가능»일
    때만 그 실행기로 서식을 맞춘다.
  · g2 범위 기준 = build-state `pre_run_head`(없으면 `git_snapshot`).
    손댄 파일 = 기준..HEAD 첫 부모 비병합 커밋과 미커밋 편집이 바꾼 파일 + 둘째 부모가 기준 가지(main) 이력 안인 병합에서
    레인이 고친 파일(`git show --cc`) + 둘째 부모가 그 이력 밖인 병합이 들여온 파일 전부. 미추적은 `.dddjango-web/`
    밖과 이 산출물 폴더만. 이 산출물 폴더의 동결 원본(`design-input.json` `reference_root`, 기본 `design-ref`)은
    검사 밖이다(바이트 고정).
    병합 판 B = 기준..HEAD 첫 부모 병합 가운데 `git merge-base --is-ancestor <병합>^2 <기준 가지>` 가 참인 것 중
    가장 최근 것의 `^2`.
    ruff = `--force-exclude` · 파일마다 (code · message) 개수 차가 신규. 허용치(H) = 키마다 큰 쪽: 기준 판 개수 · B 판 위반
    가운데 그 줄이 지금도 그대로 있고(difflib 대응) 그 줄에 같은 키 위반이 남은 것의 개수 — main 이 들인 위반은 빼고, 레인이
    고치거나 새로 만든 줄의 위반은 레인 몫으로 센다. 구문 오류 파일은 «구문 오류 — 서식 판정 불가» 발견이고 검사는 계속한다.
    서식 = 손댄 파일 전체가 `ruff format --check` 를 통과해야 한다 — 단 슬라이스 0 커밋만 손댄 파일(빌드 폴더 밖)은
    신규만(옛 판 통과 → 새 판 불통과). 슬라이스 0 = build-state 의 `slice-0*` 이름 슬라이스 기록(`mode: refactor` 면
    모든 기록 · 이름 없는 slices[0] 은 `test_baseline` 이 있을 때만) — 기록 없는 커밋은 기능 쪽으로 센다.
    mypy = 진입 기준선(머리 HEAD 가 이번 실행 진입 HEAD 일 때 · 아니면 기준 판을 풀어 돈 결과) 대비 `error:` 행
    (파일 · 코드 · 메시지 — `line <숫자>` 는 `line N`) 개수 차. 허용치는 ruff 와 같은 H — B 판을 풀어 돈 결과의 오류 가운데
    그 줄이 지금도 그대로 있고 같은 키 오류가 남은 것 — 이고, 풀어 돈 환경이 기준 판에서 진입 기준선을 그대로 재현할 때만
    쓴다. 재현하지 못하면 레인이 손대지 않은 파일에서 B 판에도 그대로 있는 줄의 오류는 «mypy 판정 불가»(main 몫인지 가를 수 없음)이고, 기준선을 하나도
    못 얻으면 mypy 전체가 «판정 불가»다.
  · 판정 불가는 신규에 넣지 않는다(막지 않음) — 마지막 `[static] 배너 정적 검사 행:` 줄에 실어 G2 배너가 옮긴다.
    기준선 실행 «실패» = exit 가 0·1 이 아니거나 끝 요약 줄(`Success:`·`Found N error`)이 없음.

exit: 0 = (entry) 확인·기준선 끝 · (g2) 신규 0(판정 불가는 배너 행으로만)
      2 = (g2) 발견 ≥1 — 목록과 고칠 주인을 찍는다
      3 = STOP — 설정은 있는데 실행기가 없다 · 진입 기준선 mypy 실행이 깨졌다
      1 = 미실행 — 사용법·git·build-state·도구 출력 오류(통과가 아니다)
"""
from __future__ import annotations

import argparse
import contextlib
import difflib
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

BATCH = 200
BUILD_ROOT = '.dddjango-web'
MYPY_LINE = re.compile(r'^(?P<file>[^:\n]+):(?P<line>\d+)(?::\d+)?: error: (?P<msg>.*?)(?:\s+\[(?P<code>[a-z0-9-]+)\])?$')
MYPY_SUMMARY = re.compile(r'^(Success: no issues found|Found \d+ errors? in \d+ files?)', re.M)
LINE_NO = re.compile(r'\bline \d+\b')
INSTALL_LINE = re.compile(r'\b(pip|pipx|uv)\b.*\b(install|add)\b|\binstall\b')
CONFIG_FILES = ('pyproject.toml [tool.ruff]', 'ruff.toml', '.ruff.toml')
UNTOUCHED = '손대지 않은 파일(상호작용) — 원인 편집의 기능 슬라이스(모르면 마지막 기능 슬라이스) 재개봉'


class ToolError(Exception):
    """미실행(exit 1)."""


class Stop(Exception):
    """STOP(exit 3)."""


# ---------------------------------------------------------------- 실행 보조
def run(args: list[str], cwd: Path, data: bytes | None = None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(args, cwd=str(cwd), input=data, capture_output=True)
    except OSError as error:
        raise ToolError(f'실행 불가 {args[0]}: {error}')


def git(root: Path, *args: str) -> bytes:
    p = run(['git', '-C', str(root), *args], root)
    if p.returncode != 0:
        raise ToolError(f'git {" ".join(args[:3])} 실패 — {p.stderr.decode("utf-8", "replace").strip()}')
    return p.stdout


def git_z(root: Path, *args: str) -> list[str]:
    return [x for x in git(root, *args).decode('utf-8', 'surrogateescape').split('\0') if x]


def resolve(root: Path, rev: str) -> str | None:
    if not rev:
        return None
    p = run(['git', '-C', str(root), 'rev-parse', '--verify', '-q', rev + '^{commit}'], root)
    return p.stdout.decode().strip() if p.returncode == 0 else None


def is_ancestor(root: Path, older: str, newer: str) -> bool:
    p = run(['git', '-C', str(root), 'merge-base', '--is-ancestor', older, newer], root)
    if p.returncode not in (0, 1):
        raise ToolError(f'git merge-base --is-ancestor 실패 — {p.stderr.decode("utf-8", "replace").strip()}')
    return p.returncode == 0


_BLOBS: dict[tuple[str, str], bytes | None] = {}


def blob(root: Path, rev: str, path: str) -> bytes | None:
    key = (rev, path)
    if key not in _BLOBS:
        p = run(['git', '-C', str(root), 'show', f'{rev}:{path}'], root)
        _BLOBS[key] = p.stdout if p.returncode == 0 else None
    return _BLOBS[key]


# ---------------------------------------------------------------- ① 설정 감지
def _read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return ''


def precommit_hooks(text: str) -> list[dict[str, str]]:
    hooks: list[dict[str, str]] = []
    repo = ''
    for line in text.splitlines():
        if re.match(r'^\s*#', line):
            continue
        m = re.match(r'^\s*-\s+repo:\s*(\S+)', line)
        if m:
            repo = m.group(1)
            continue
        m = re.match(r'^\s*-\s+id:\s*(\S+)', line)
        if m:
            hooks.append({'id': m.group(1), 'repo': repo})
            continue
        m = re.match(r'^\s*(entry|args|pass_filenames):\s*(.*?)\s*$', line)
        if m and hooks:
            hooks[-1][m.group(1)] = re.sub(r'\s+#.*$', '', m.group(2))
    return hooks


def detect(root: Path) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {'ruff': [], 'mypy': []}
    pyproject = _read(root / 'pyproject.toml')
    if re.search(r'^\s*\[tool\.ruff(\.[^\]]+)?\]', pyproject, re.M):
        found['ruff'].append('pyproject.toml [tool.ruff]')
    for name in ('ruff.toml', '.ruff.toml'):
        if (root / name).is_file():
            found['ruff'].append(name)
    for name in ('mypy.ini', '.mypy.ini'):
        if (root / name).is_file():
            found['mypy'].append(name)
    if re.search(r'^\s*\[tool\.mypy\]', pyproject, re.M):
        found['mypy'].append('pyproject.toml [tool.mypy]')
    if re.search(r'^\s*\[mypy\]', _read(root / 'setup.cfg'), re.M):
        found['mypy'].append('setup.cfg [mypy]')
    for hook in precommit_hooks(_read(root / '.pre-commit-config.yaml')):
        text = ' '.join(hook.values())
        for tool in ('ruff', 'mypy'):
            if re.search(rf'\b{tool}\b', text) and '.pre-commit-config.yaml' not in found[tool]:
                found[tool].append('.pre-commit-config.yaml')
    for number, line in enumerate(_read(root / 'Makefile').splitlines(), 1):
        if line.lstrip().startswith('#') or INSTALL_LINE.search(line):
            continue
        for tool, pattern in (('ruff', r'\bruff\s+(check|format)\b'), ('mypy', r'\bmypy\b')):
            if re.search(pattern, line) and not any(s.startswith('Makefile') for s in found[tool]):
                found[tool].append(f'Makefile:{number}')
    return found


def mypy_args_detected(root: Path) -> tuple[list[str] | None, str]:
    for hook in precommit_hooks(_read(root / '.pre-commit-config.yaml')):
        entry = hook.get('entry', '')
        if hook.get('pass_filenames', '').lower() != 'false' or not re.search(r'\bmypy\b', entry):
            continue
        try:
            tokens = shlex.split(entry)
        except ValueError:
            continue
        if 'mypy' in tokens:
            extra: list[str] = []
            raw = hook.get('args', '')
            if raw.startswith('['):
                extra = [x.strip().strip('\'"') for x in raw.strip('[]').split(',') if x.strip()]
            return tokens[tokens.index('mypy') + 1:] + extra, f'.pre-commit-config.yaml 훅 {hook["id"]}'
    for number, line in enumerate(_read(root / 'Makefile').splitlines(), 1):
        if line.lstrip().startswith('#') or '$' in line or INSTALL_LINE.search(line):
            continue
        try:
            tokens = shlex.split(line.strip().lstrip('@-'))
        except ValueError:
            continue
        if 'mypy' in tokens:
            return tokens[tokens.index('mypy') + 1:], f'Makefile:{number}'
    return None, ''


# ---------------------------------------------------------------- ② 실행기
def executor(root: Path, tool: str) -> tuple[list[str] | None, str]:
    """부작용 없는 판정 — `uv run` 은 쓸 환경이 이미 있을 때만 부른다(없으면 uv 가 빈 `.venv` 를 만든다)."""
    env = os.environ.get('UV_PROJECT_ENVIRONMENT')
    venv_dir = Path(env) if env else root / '.venv'
    if not venv_dir.is_absolute():
        venv_dir = root / venv_dir
    if (root / 'uv.lock').is_file() and shutil.which('uv') and (venv_dir / 'pyvenv.cfg').is_file():
        cmd = ['uv', 'run', '--frozen', '--no-sync', tool]
        p = run(cmd + ['--version'], root)
        if p.returncode == 0 and p.stdout.strip():
            return cmd, p.stdout.decode('utf-8', 'replace').strip().splitlines()[0]
    venv = root / '.venv' / 'bin' / tool
    if venv.is_file() and os.access(venv, os.X_OK):
        p = run([str(venv), '--version'], root)
        if p.returncode == 0 and p.stdout.strip():
            return [str(venv)], p.stdout.decode('utf-8', 'replace').strip().splitlines()[0]
    return None, ''


def tools(root: Path, mypy_args: str | None) -> dict:
    """설정 감지 + 실행기 확인. 설정은 있는데 실행기가 없으면 Stop."""
    config = detect(root)
    info: dict = {}
    for tool in ('ruff', 'mypy'):
        if not config[tool]:
            info[tool] = None
            print(f'[static] {tool} 설정 없음 — 생략')
            continue
        exe, version = executor(root, tool)
        if exe is None:
            raise Stop(f'{tool} 설정 있음({", ".join(config[tool])}) · 실행기 없음(`uv run --frozen --no-sync {tool}` · '
                       f'`.venv/bin/{tool}` 둘 다 안 됨)')
        info[tool] = {'exe': exe, 'version': version, 'config': config[tool]}
        tail = ''
        if tool == 'ruff':
            info[tool]['format_ok'] = any(s in CONFIG_FILES for s in config[tool])
            tail = (' · 서식 판정 가능' if info[tool]['format_ok']
                    else ' · 서식 판정 불가(설정 파일 없음 — 훅·Makefile 로만 감지)')
        print(f'[static] {tool} 실행기 {" ".join(exe)} · {version} · 설정 {", ".join(config[tool])}{tail}')
    if info['mypy'] is not None:
        if mypy_args is not None:
            info['mypy']['args'], info['mypy']['source'] = shlex.split(mypy_args), '--mypy-args'
        else:
            info['mypy']['args'], info['mypy']['source'] = mypy_args_detected(root)
    return info


# ---------------------------------------------------------------- mypy 보조
def mypy_entries(text: str) -> list[tuple[tuple[str, str, str], int]]:
    """(키 (파일 · 코드 · 메시지 `line N` 정규화), 줄)."""
    out = []
    for line in text.splitlines():
        if line.startswith('#'):
            continue
        m = MYPY_LINE.match(line)
        if m:
            out.append(((m['file'], m['code'] or '', LINE_NO.sub('line N', m['msg'])), int(m['line'])))
    return out


def mypy_keys(text: str) -> Counter:
    keys: Counter = Counter()
    for line in text.splitlines():
        if line.startswith('#'):
            continue
        m = MYPY_LINE.match(line)
        if m:
            keys[(m['file'], m['code'] or '', LINE_NO.sub('line N', m['msg']))] += 1
    return keys


def mypy_valid(code: int, text: str, allow_fatal: bool = False) -> str:
    """빈 문자열 = 정상. 기준선(allow_fatal=False)은 exit 0·1 만 · G2 실행은 요약 줄이 있는 exit 2 도 받는다."""
    if code not in ((0, 1, 2) if allow_fatal else (0, 1)):
        return f'exit {code}'
    if not MYPY_SUMMARY.search(text):
        return '끝 요약 줄(Success: · Found N error) 없음'
    return ''


def mypy_run(exe: list[str], args: list[str], cwd: Path) -> tuple[int, str]:
    p = run(exe + args, cwd)
    return p.returncode, (p.stdout + p.stderr).decode('utf-8', 'replace')


def read_baseline(path: Path) -> tuple[dict[str, str], str] | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding='utf-8', errors='replace')
    head: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r'^# (\S+) (.*)$', line)
        if m:
            head.setdefault(m.group(1), m.group(2))
        elif line and not line.startswith('#'):
            break
    return head, text


def write_baseline(path: Path, head: dict[str, str], body: str) -> None:
    path.write_text(''.join(f'# {k} {v}\n' for k, v in head.items()) + body, encoding='utf-8')


def archive_mypy(root: Path, rev: str, args: list[str], name: str) -> tuple[int, str] | str:
    """rev 판을 `git archive` 로 풀어 레인 `.venv/bin/mypy` 로 돈다(`uv run` 없음). 실패면 사유 문자열."""
    mypy_bin = root / '.venv' / 'bin' / 'mypy'
    if not (mypy_bin.is_file() and os.access(mypy_bin, os.X_OK)):
        return '레인 .venv/bin/mypy 없음'
    tmp = Path(tempfile.mkdtemp(prefix=f'{name}-prerun-'))
    try:
        tar = tmp / 'tree.tar'
        p = run(['git', '-C', str(root), 'archive', '-o', str(tar), rev], root)
        if p.returncode != 0:
            return f'git archive 실패 — {p.stderr.decode("utf-8", "replace").strip()}'
        tree = tmp / 'tree'
        tree.mkdir()
        p = run(['tar', '-x', '-C', str(tree), '-f', str(tar)], root)
        if p.returncode != 0:
            return f'tar 실패 — {p.stderr.decode("utf-8", "replace").strip()}'
        return mypy_run([str(mypy_bin)], args, tree)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def cached_archive(root: Path, build: Path, kind: str, rev: str, args: list[str], name: str) -> tuple[Counter, str, str]:
    """(키, 실패 사유 — 빈 문자열이면 정상, 원문). 같은 판·같은 명령이면 산출물 폴더의 기준선 파일을 다시 쓴다."""
    path = build / f'mypy-baseline-{kind}-{rev[:9]}.txt'
    command = shlex.join(args)
    found = read_baseline(path)
    if found and found[0].get('HEAD') == rev and found[0].get('대상') == command:
        head, text = found
        reason = mypy_valid(int(head.get('exit', '-1')), text)
        return mypy_keys(text), reason, text
    got = archive_mypy(root, rev, args, name)
    if isinstance(got, str):
        return Counter(), got, ''
    code, text = got
    write_baseline(path, {'HEAD': rev, '대상': command, '실행기': str(root / '.venv/bin/mypy'), 'exit': str(code)}, text)
    return mypy_keys(text), mypy_valid(code, text), text


# ---------------------------------------------------------------- build-state · 손댄 파일
def build_state(build: Path) -> dict:
    try:
        data = json.loads((build / 'build-state.json').read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError) as error:
        raise ToolError(f'build-state.json 을 읽을 수 없다 — {error}')
    if not isinstance(data, dict):
        raise ToolError('build-state.json 이 객체가 아니다')
    return data


def slice_records(root: Path, state: dict) -> tuple[set[str], dict[str, str]]:
    """(슬라이스 0 커밋 · 기능 커밋 → 슬라이스 이름). 슬라이스 0 = `slice-0*` 이름 · 리팩토링 모드면 모든 기록 · 이름 없는
    slices[0] 은 슬라이스 0 이 있을 때(build-state `test_baseline`)만 — 서식 면제가 걸리므로 자리만으로 정하지 않는다.
    해시로 풀리지 않는 기록은 버린다."""
    refactor = state.get('mode') == 'refactor'
    has_zero = bool(str(state.get('test_baseline') or '').strip())   # 슬라이스 0 이 있을 때만 적는 기록
    zero: set[str] = set()
    feature: dict[str, str] = {}
    slices = state.get('slices') if isinstance(state.get('slices'), list) else []
    for index, item in enumerate(slices):
        if not isinstance(item, dict):
            continue
        name = item.get('name') if isinstance(item.get('name'), str) else f'slices[{index}]'
        listed = item.get('commits', [])
        values = [item.get('commit')] + (listed if isinstance(listed, list) else [listed])
        for value in values:
            if not isinstance(value, str) or not re.fullmatch(r'[0-9a-fA-F]{7,40}', value.strip()):
                continue
            sha = resolve(root, value.strip())
            if sha is None:
                continue
            if name.startswith('slice-0') or refactor or (index == 0 and not isinstance(item.get('name'), str) and has_zero):
                zero.add(sha)
            else:
                feature.setdefault(sha, name)
    for sha in zero:
        feature.pop(sha, None)
    return zero, feature


def main_refs(root: Path, names: list[str]) -> list[str]:
    return [sha for sha in (resolve(root, n) for n in names) if sha]


def in_main(root: Path, commit: str, refs: list[str]) -> bool:
    return any(is_ancestor(root, commit, ref) for ref in refs)


def touched_files(root: Path, base: str, build_rel: str, state: dict, refs_names: list[str]
                  ) -> tuple[dict[str, list[tuple[int, str, str]]], str | None, str | None, list[str]]:
    """손댄 파일 → [(순서, 종류, 표지)] · 병합 판 B · 그 병합 · 알림."""
    zero, feature = slice_records(root, state)
    snapshot = resolve(root, str(state.get('git_snapshot') or ''))
    chain = [line.split() for line in git(root, 'rev-list', '--reverse', '--first-parent', '--parents',
                                          f'{base}..HEAD').decode().splitlines()]
    merges = [ids for ids in chain if len(ids) > 2]
    refs = main_refs(root, refs_names) if merges else []
    notes: list[str] = []
    if merges and not refs:
        raise ToolError(f'레인 안 병합이 있는데 기준 가지({", ".join(refs_names)})를 풀 수 없다 — --base-branch 로 준다')
    touches: dict[str, list[tuple[int, str, str]]] = {}

    def add(paths: list[str], order: int, kind: str, label: str) -> None:
        for path in paths:
            touches.setdefault(path, []).append((order, kind, label))

    merge_side: str | None = None
    merge_commit: str | None = None
    for order, ids in enumerate(chain):
        commit, parents = ids[0], ids[1:]
        if len(parents) <= 1:
            files = git_z(root, 'diff-tree', '-r', '--no-commit-id', '--name-only', '-z', '--no-renames', commit)
            if commit in zero:
                add(files, order, 'slice0', '슬라이스 0')
            elif commit in feature:
                add(files, order, 'feature', feature[commit])
            elif commit == snapshot:
                add(files, order, 'snapshot', '진입 산출물 커밋')
            else:
                add(files, order, 'unrecorded', commit[:9])
        elif in_main(root, parents[1], refs):
            add(git_z(root, 'show', '--cc', '--name-only', '-z', '--format=', commit), order, 'merge', commit[:9])
            merge_side, merge_commit = parents[1], commit      # 사슬이 오래된 순이라 마지막이 최신
        else:
            add(git_z(root, 'diff', '--name-only', '-z', '--no-renames', parents[0], commit), order, 'sibling',
                commit[:9])
            notes.append(f'이력 밖 병합 {commit[:9]}(^2 {parents[1][:9]} 가 기준 가지 밖) — 들여온 파일 전부를 레인 몫으로 센다')
    last = len(chain)
    add(git_z(root, 'diff', '--name-only', '-z', '--no-renames', 'HEAD'), last, 'uncommitted', '미커밋')
    untracked = [p for p in git_z(root, 'ls-files', '--others', '--exclude-standard', '-z')
                 if not p.startswith(BUILD_ROOT + '/') or p.startswith(build_rel + '/')]
    add(untracked, last, 'uncommitted', '미추적')
    return touches, merge_side, merge_commit, notes


def owner(path: str, marks: list[tuple[int, str, str]]) -> str:
    if path.startswith(BUILD_ROOT + '/'):
        return '빌드 폴더 — 네가 고친다'
    features = [m for m in marks if m[1] == 'feature']
    if features:
        return f'기능 슬라이스 {max(features)[2]} — 재개봉'
    order, kind, label = max(marks)
    return {'slice0': '슬라이스 0 — 재개봉(자기 편집 안)',
            'snapshot': '진입 산출물 커밋(네 배선·골격) — 네가 고친다(서식 · 신규 줄만 손으로)',
            'unrecorded': f'기록 없는 커밋 {label} — build-state 에 파견 슬라이스를 적고 다시',
            'merge': f'병합 {label} 안 레인 편집 — 마지막 기능 슬라이스 재개봉',
            'sibling': f'이력 밖 병합 {label} 유입 — 마지막 기능 슬라이스 재개봉',
            'uncommitted': f'{label} — 만든 슬라이스(모르면 마지막 기능 슬라이스)로 커밋·기록하거나 버릴 파일이면 지운 뒤 다시'
            }[kind]


# ---------------------------------------------------------------- ③ ruff · 서식
def _rel(root: Path, filename: str) -> str:
    real = os.path.realpath(filename)
    base = os.path.realpath(str(root))
    return os.path.relpath(real, base) if real.startswith(base + os.sep) else filename


Item = tuple[tuple[str, str], int]   # ((code, message), 줄)


def _items(raw: bytes) -> list[dict]:
    return json.loads(raw.decode('utf-8') or '[]')


def _row(item: dict) -> int:
    return int((item.get('location') or {}).get('row') or 0)


def ruff_check(exe: list[str], root: Path, paths: list[str]) -> dict[str, list[Item]]:
    found: dict[str, list[Item]] = {}
    for i in range(0, len(paths), BATCH):
        p = run(exe + ['check', '--force-exclude', '--output-format', 'json', *paths[i:i + BATCH]], root)
        if p.returncode not in (0, 1):
            raise ToolError(f'ruff check 실패(exit {p.returncode}) — {p.stderr.decode("utf-8", "replace").strip()[:300]}')
        for item in _items(p.stdout):
            found.setdefault(_rel(root, item['filename']), []).append(((item['code'] or '', item['message']), _row(item)))
    return found


def ruff_check_stdin(exe: list[str], root: Path, path: str, data: bytes) -> list[Item]:
    p = run(exe + ['check', '--force-exclude', '--output-format', 'json', '--stdin-filename', path, '-'], root, data)
    if p.returncode not in (0, 1):
        raise ToolError(f'ruff check(옛 판 {path}) 실패 — {p.stderr.decode("utf-8", "replace").strip()[:300]}')
    return [((item['code'] or '', item['message']), _row(item)) for item in _items(p.stdout)]


def ruff_unformatted(exe: list[str], root: Path, paths: list[str]) -> tuple[set[str], set[str]]:
    """(서식 불통과 파일 · 구문 오류로 서식을 판정할 수 없는 파일). exit 2 라도 JSON 이 읽히면 받는다."""
    bad: set[str] = set()
    broken: set[str] = set()
    for i in range(0, len(paths), BATCH):
        chunk = paths[i:i + BATCH]
        p = run(exe + ['format', '--check', '--force-exclude', '--output-format', 'json', *chunk], root)
        if p.returncode in (0, 1, 2) and p.stdout.strip().startswith(b'['):
            for item in _items(p.stdout):
                (broken if item.get('code') == 'invalid-syntax' else bad).add(_rel(root, item['filename']))
            continue
        p = run(exe + ['format', '--check', '--force-exclude', *chunk], root)   # --output-format 없는 판
        if p.returncode not in (0, 1):
            raise ToolError(f'ruff format --check 실패(exit {p.returncode}) — '
                            f'{p.stderr.decode("utf-8", "replace").strip()[:300]}')
        for line in p.stdout.decode('utf-8', 'replace').splitlines():
            if line.startswith('Would reformat: '):
                bad.add(_rel(root, line[len('Would reformat: '):].strip()))
    return bad - broken, broken


def unformatted_stdin(exe: list[str], root: Path, path: str, data: bytes) -> bool:
    return run(exe + ['format', '--check', '--force-exclude', '--stdin-filename', path, '-'], root, data).returncode != 0


def line_map(old: bytes, new: bytes) -> dict[int, int]:
    """옛 판 줄 번호 → 지금 줄 번호(그대로 남은 줄만 · difflib 대응)."""
    a = old.decode('utf-8', 'replace').splitlines()
    b = new.decode('utf-8', 'replace').splitlines()
    mapping: dict[int, int] = {}
    for tag, i1, i2, j1, _j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                mapping[i1 + k + 1] = j1 + k + 1
    return mapping


def alive(side_items: list, now_items: list, mapping: dict[int, int]) -> Counter:
    """병합 판 위반 가운데 그 줄이 지금도 그대로 있고 그 줄에 같은 키 위반이 있는 것의 키별 개수(H 규칙)."""
    here = Counter(now_items)
    used: Counter = Counter()
    found: Counter = Counter()
    for key, row in side_items:
        target = mapping.get(row)
        if target is not None and here[(key, target)] - used[(key, target)] > 0:
            used[(key, target)] += 1
            found[key] += 1
    return found


# ---------------------------------------------------------------- 단계
def phase_entry(root: Path, build: Path, args: argparse.Namespace) -> int:
    info = tools(root, args.mypy_args)
    mypy = info['mypy']
    if mypy is None:
        return 0
    if not mypy['args']:
        print('[static] mypy 대상 미정 — 생략(프로젝트가 대상을 정해 두었으면 --mypy-args 로 다시)')
        return 0
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    code, text = mypy_run(mypy['exe'], mypy['args'], root)
    reason = mypy_valid(code, text)
    path = build / 'mypy-baseline.txt'
    write_baseline(path, {'HEAD': head, '대상': shlex.join(mypy['args']), '출처': mypy['source'],
                          '실행기': shlex.join(mypy['exe']), '버전': mypy['version'], 'exit': str(code)}, text)
    if reason:
        raise Stop(f'진입 기준선 mypy 실행이 깨졌다({reason}) — {path}')
    print(f'[static] mypy 진입 기준선 {path.name} · HEAD {head[:9]} · 명령 {shlex.join(mypy["exe"] + mypy["args"])} '
          f'(출처 {mypy["source"]}) · exit {code} · 오류 {sum(mypy_keys(text).values())}')
    return 0


def phase_g2(root: Path, build: Path, args: argparse.Namespace) -> int:
    state = build_state(build)
    pre = resolve(root, str(state.get('pre_run_head') or ''))
    snapshot = resolve(root, str(state.get('git_snapshot') or ''))
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    if pre and is_ancestor(root, pre, head):
        base, base_name = pre, 'pre_run_head'
    elif snapshot and is_ancestor(root, snapshot, head):
        base, base_name = snapshot, 'git_snapshot'
    else:
        raise ToolError('범위 기준 없음 — build-state 의 pre_run_head·git_snapshot 이 HEAD 의 조상으로 풀리지 않는다')
    entry_head = pre if pre else (resolve(root, snapshot + '^') if snapshot else None)
    found_baseline = read_baseline(build / 'mypy-baseline.txt')
    mypy_args = args.mypy_args
    if mypy_args is None and found_baseline and found_baseline[0].get('대상'):
        mypy_args = found_baseline[0]['대상']
    info = tools(root, mypy_args)
    build_rel = os.path.relpath(os.path.realpath(str(build)), os.path.realpath(str(root)))
    try:
        design = json.loads((build / 'design-input.json').read_text(encoding='utf-8'))
        reference = str(design.get('reference_root') or 'design-ref')
    except (OSError, UnicodeError, ValueError, AttributeError):
        reference = 'design-ref'
    touches, merge_side, merge_commit, notes = touched_files(root, base, build_rel, state, args.base_branch)
    frozen = build_rel + '/' + reference.strip('/') + '/'
    targets = sorted(p for p in touches if p.endswith('.py') and (root / p).is_file() and not p.startswith(frozen))
    skipped = sorted(p for p in touches if p.endswith('.py') and p.startswith(frozen) and (root / p).is_file())
    print(f'[static] 범위 기준 {base_name} {base[:9]} · HEAD {head[:9]} · 손댄 .py {len(targets)}'
          + (f' · 병합 판 {merge_commit[:9]}^2 {merge_side[:9]}(허용치 = 기준 판 개수와 지금도 같은 줄에 살아 있는 그 판 위반 수 가운데 큰 쪽)'
             if merge_side else ' · 병합 판 없음'))
    for note in notes:
        print(f'[static] {note}')
    if skipped:
        print(f'[static] 동결 원본 .py {len(skipped)}개 — 검사 밖(바이트 고정 · {frozen})')
    renames: dict[str, str] = {}
    entries = git_z(root, 'diff', '-M', '--name-status', '-z', base)
    i = 0
    while i < len(entries):
        status = entries[i]
        if status.startswith(('R', 'C')) and i + 2 < len(entries):
            renames[entries[i + 2]] = entries[i + 1]
            i += 3
        else:
            i += 2

    same_as_side: dict[str, bool] = {}

    def equals_side(path: str) -> bool:
        """지금 내용이 병합 판(main 쪽)과 같다 = 레인이 그 판 뒤로 이 파일을 바꾸지 않았다."""
        if path not in same_as_side:
            side = blob(root, merge_side, path) if merge_side else None
            try:
                same_as_side[path] = side is not None and (root / path).read_bytes() == side
            except OSError:
                same_as_side[path] = False
        return same_as_side[path]

    def side_blob(path: str) -> bytes | None:
        if not merge_side:
            return None
        return blob(root, merge_side, path) or blob(root, merge_side, renames.get(path, path))

    def worktree(path: str) -> bytes:
        try:
            return (root / path).read_bytes()
        except OSError:
            return b''

    def olds(path: str) -> list[bytes]:
        if equals_side(path):
            return [blob(root, merge_side, path)]
        a = blob(root, base, renames.get(path, path))
        return [a] if a is not None else []

    def slice0_only(path: str) -> bool:
        return not path.startswith(BUILD_ROOT + '/') and all(kind == 'slice0' for _o, kind, _l in touches[path])

    total = 0
    row: list[str] = []          # G2 배너 정적 검사 행
    undecided: list[str] = []    # 판정 불가 — 막지 않고 배너에 올린다
    if info['ruff'] is not None and targets:
        exe = info['ruff']['exe']
        current = ruff_check(exe, root, targets)
        lines: list[str] = []
        count = 0
        for path in sorted(current):
            if path not in touches:
                continue
            now = Counter(key for key, _row in current[path])
            base_data = blob(root, base, renames.get(path, path))
            allow = Counter(key for key, _row in ruff_check_stdin(exe, root, path, base_data)) if base_data else Counter()
            side_data = side_blob(path)
            if side_data is not None:     # H: 지금도 같은 줄에 살아 있는 병합 판 위반만 허용
                allow |= alive(ruff_check_stdin(exe, root, path, side_data), current[path],
                               line_map(side_data, worktree(path)))
            new = now - allow
            if new:
                count += sum(new.values())
                lines.append(f'  {path} [{owner(path, touches[path])}]')
                lines += [f'    {code} {message} ×{n}' for (code, message), n in sorted(new.items())]
        print(f'[static] ruff 신규 {count}')
        print('\n'.join(lines)) if lines else None
        total += count
        row.append(f'ruff 신규 {count}')
        if not info['ruff']['format_ok']:
            print('[static] 서식 판정 불가 — 설정 파일 없음(훅·Makefile 로만 감지 · 기본값 재포맷을 요구하지 않는다) — '
                  'G2 배너 정적 검사 행에 올린다 · 막지 않음')
            undecided.append('서식 판정 불가 — 설정 파일 없음')
        else:
            bad, broken = ruff_unformatted(exe, root, targets)
            lines, fmt, kept = [], 0, 0
            for path in sorted(broken):
                if path in touches:
                    fmt += 1
                    lines.append(f'  {path} [{owner(path, touches[path])}] 구문 오류 — 서식 판정 불가(고친 뒤 다시)')
            for path in sorted(bad):
                if path not in touches:
                    continue
                old_bad = any(unformatted_stdin(exe, root, path, data) for data in olds(path))
                if slice0_only(path):
                    if old_bad:
                        continue
                    tag = '신규(슬라이스 0 전용 파일 — 신규만)'
                else:
                    tag = '기존 불통과(손댄 파일 전체 정리)' if old_bad else '신규'
                    kept += old_bad
                fmt += 1
                lines.append(f'  {path} [{owner(path, touches[path])}] {tag}')
            print(f'[static] 서식 불통과 {fmt}(그중 기존 불통과 {kept}) — 손댄 파일 전체 · 슬라이스 0 전용 파일은 신규만')
            print('\n'.join(lines)) if lines else None
            total += fmt
            row.append(f'서식 {fmt}(기존 {kept})')
    elif info['ruff'] is not None:
        print('[static] ruff 대상 없음 — 생략(손댄 .py 0)')
        row.append('ruff 대상 없음')
    else:
        row.append('ruff 설정 없음')
    mypy = info['mypy']
    if mypy is None:
        row.append('mypy 설정 없음')
    elif not mypy['args']:
        print('[static] mypy 대상 미정 — 생략(프로젝트가 대상을 정해 두었으면 --mypy-args 로 다시)')
        row.append('mypy 대상 미정')
    else:
        code, text = mypy_run(mypy['exe'], mypy['args'], root)
        reason = mypy_valid(code, text, allow_fatal=True)
        if reason:
            raise ToolError(f'mypy 실행 실패({reason}) — 명령 {shlex.join(mypy["exe"] + mypy["args"])}')
        current = mypy_keys(text)
        name = Path(build_rel).name
        baseline: Counter | None = None
        source = ''
        if found_baseline and found_baseline[0].get('HEAD') == entry_head and found_baseline[0].get('대상') == shlex.join(mypy['args']):
            if not mypy_valid(int(found_baseline[0].get('exit', '-1')), found_baseline[1]):
                baseline, source = mypy_keys(found_baseline[1]), '진입 기준선'
        if baseline is None and pre:
            keys, failure, _t = cached_archive(root, build, 'archive', pre, mypy['args'], name)
            if not failure:
                baseline, source = keys, f'기준 판 {pre[:9]} 을 풀어 돈 결과(진입 기준선 없음·불일치)'
            else:
                print(f'[static] mypy 기준 판 풀어 돌기 실패 — {failure}')
        if baseline is None:
            print(f'[static] mypy 판정 불가 — 기준선 없음(진입 기준선·기준 판 풀어 돌기 모두 없음 · 오류 '
                  f'{sum(current.values())}) — G2 배너 정적 검사 행에 올린다 · 막지 않음')
            undecided.append(f'mypy 판정 불가 — 기준선 없음(오류 {sum(current.values())})')
            row.append('mypy 판정 불가')
            current = Counter()
            baseline = Counter()
        new = current - baseline
        absorbed = ''
        now_entries = [e for e in mypy_entries(text)]
        maps: dict[str, dict[int, int]] = {}

        def mapped(path: str) -> dict[int, int]:
            if path not in maps:
                side = side_blob(path)
                maps[path] = line_map(side, worktree(path)) if side is not None else {}
            return maps[path]

        # 병합 판에도 그대로 있는 줄의 오류만 main 몫일 수 있다
        maybe_main = Counter(key for key, row in now_entries
                             if new[key] and row in set(mapped(key[0]).values()))
        if merge_side and source and maybe_main:
            if source == '진입 기준선' and pre:
                fidelity, failure, _t = cached_archive(root, build, 'archive', pre, mypy['args'], name)
                if not failure and fidelity != baseline:
                    failure = '풀어 돈 환경이 기준 판에서 진입 기준선을 재현하지 못한다'
            else:
                failure = '' if pre else '범위 기준이 git_snapshot(dirty 시작) — 기준 판 환경 대조 불가'
            side_text = ''
            if not failure:
                _side, failure, side_text = cached_archive(root, build, 'merge', merge_side, mypy['args'], name)
            if failure:
                # main 몫인지 레인 상호작용인지 가를 수 없다 — 레인이 손대지 않은 파일에서 병합 판에도 그대로 있는 줄의 오류만 판정 불가(손댄 파일 안은 신규로 남긴다)
                unknown = Counter({k: min(n, maybe_main[k]) for k, n in new.items() if maybe_main[k] and k[0] not in touches})
                new = new - unknown
                absorbed = f' · 병합 판 기준선 실패 — {failure}'
                print(f'[static] mypy 판정 불가 {sum(unknown.values())} — 병합 판 기준선 실패: {failure}(손대지 않은 파일에서 병합 판에도 '
                      f'그대로 있는 줄의 오류 · G2 배너 정적 검사 행에 올린다 · 막지 않음)')
                for (path, code_name, message), n in sorted(unknown.items()):
                    print(f'  {path}: {code_name} {message} ×{n} [판정 불가 — 배너]')
                undecided.append(f'mypy 판정 불가 {sum(unknown.values())} — 병합 판 기준선 실패: {failure}')
            else:
                before = sum(new.values())
                side_entries = mypy_entries(side_text)
                live: Counter = Counter()
                for path in {key[0] for key, _row in side_entries}:
                    live += alive([(k, r) for k, r in side_entries if k[0] == path],
                                  [(k, r) for k, r in now_entries if k[0] == path], mapped(path))
                new = current - (baseline | live)
                absorbed = f' · 병합 판 {merge_side[:9]} 에서 지금도 같은 줄에 있는 오류 {before - sum(new.values())} 뺌'
        if source:
            print(f'[static] mypy 신규 {sum(new.values())} · exit {code} · 오류 {sum(current.values())} · 기준선 '
                  f'{source}{absorbed}')
            row.append(f'mypy 신규 {sum(new.values())}')
        for (path, code_name, message), n in sorted(new.items()):
            label = owner(path, touches[path]) if path in touches else UNTOUCHED
            print(f'  {path}: {code_name} {message} ×{n} [{label}]')
        total += sum(new.values())
    banner = ' · '.join(row) + ''.join(f' · {u}' for u in undecided)
    print(f'[static] 배너 정적 검사 행: 정적 검사(HEAD {head[:9]}): {banner}')
    print(f'[static] 결과 신규 합 {total} — exit {2 if total else 0}')
    return 2 if total else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='G2 전 정적 검사(린트·서식·타입)')
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--build', required=True, type=Path)
    parser.add_argument('--phase', required=True, choices=('entry', 'g2'))
    parser.add_argument('--mypy-args')
    parser.add_argument('--base-branch', action='append')
    args = parser.parse_args(argv)
    args.base_branch = args.base_branch or ['main', 'origin/main']
    root = args.project_root.resolve()
    build = args.build if args.build.is_absolute() else root / args.build
    if not root.is_dir() or not build.is_dir():
        print('[static] 미실행 — --project-root 와 --build 는 있는 폴더여야 한다')
        return 1
    if args.phase == 'g2':
        return guarded(lambda: phase_g2(root, build.resolve(), args))
    out = io.StringIO()   # 진입 출력은 `<산출물 폴더>/static-entry.txt` 로도 남긴다(coder 입력 · 재개 근거)
    with contextlib.redirect_stdout(out):
        code = guarded(lambda: phase_entry(root, build.resolve(), args))
    sys.stdout.write(out.getvalue())
    (build / 'static-entry.txt').write_text(out.getvalue(), encoding='utf-8')
    return code


def guarded(step) -> int:
    try:
        return step()
    except Stop as error:
        print(f'[static] STOP — {error}')
        return 3
    except ToolError as error:
        print(f'[static] 미실행 — {error}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
