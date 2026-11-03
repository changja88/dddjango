#!/usr/bin/env python3
# 멈춘 시험 깨우기 — 시험 명령을 새 묶음으로 띄워 지켜보고, 결과 줄 하나로 끝낸다(dddjango-web · dddjango 같은 파일 · Codex byte 미러).
#
# 사용:
#   python3 test_watch.py run    [--quiet 10] [--after 5] -- '<셸 명령 한 덩이>'
#   python3 test_watch.py attach <감시 폴더> [--quiet 10]
#   python3 test_watch.py stop   <감시 폴더>
#   python3 test_watch.py list
#
# 감시 폴더: `run` 이 `<git 디렉터리>/test-watch/<UTC 시각>-<무작위>/` 를 새로 만든다 — 그 자리에 쓸 수 없으면
#   `${TMPDIR}/test-watch/<작업 트리 뿌리 경로 해시>/<시각>-<무작위>/` 로 물러난다. 안: out.log(시험 출력) · notes(probe 의
#   시험 시작 · 끝) · stalled(멈춤 의심 순간의 오래 도는 시험) · exit(끝 코드) · meta.json(PGID · 지도자 시작 시각 · 표지 · 명령).
# 값: --quiet = 출력(out.log · notes)이 그대로인 분 · --after = 시작한 뒤 끝나지 않은 시험을 «오래 도는 시험» 으로 보는 분.
#   어느 값도 시험을 실패시키지 않는다.
# 결과 줄(늘 마지막 줄 — 규칙은 exit 가 아니라 이 줄로 판정한다):
#   [watch] 결과: 끝 exit <c>                                         → exit <c>
#   [watch] 결과: 끝 코드 모름(…)                                     → exit 70
#   [watch] 결과: 멈춤 의심 — <q>분 출력 없음 · 오래 도는 시험 … · 폴더 … → exit 75(자식은 끄지 않는다)
#   [watch] 결과: 끊김 — 감시가 신호 <n> 을 받음 · 자식에 INT 넘김 · 폴더 … → exit 128+<n>
#   [watch] 결과: 도구 오류 — …                                       → exit 70
#   stop: [watch] 결과: 끔 — … · 묶음 끝 — …                          → exit 0 / 도구 오류 70
# probe 를 싣지 못하는 명령(셸 낱말 `PYTHONPATH=…` · `-I` · `-E`, 또는 시작 단계의 probe 적재 오류)은 probe 없이 지켜보고
# 결과 줄에 `probe 없음` 을 붙인다.

import argparse
import hashlib
import json
import os
import re
import secrets
import shlex
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple

QUIET_MINUTES: float = 10.0
AFTER_MINUTES: float = 5.0
STOP_INT_WAIT_SECONDS: float = 120.0       # stop 사다리 — INT 뒤 기다림
STOP_TERM_WAIT_SECONDS: float = 120.0      # stop 사다리 — TERM 뒤 기다림
STOP_KILL_WAIT_SECONDS: float = 10.0       # KILL 뒤 묶음이 사라지는지 보는 시간
EXIT_STALL: int = 75
EXIT_TOOL: int = 70
WATCH_DIR: str = 'test-watch'
# git 출력에 사용자 설정이 끼지 않게 — dddjango-web scripts/src/common.py 의 GIT_PINS 와 같은 값(이 파일은 두 플러그인에 홀로 실린다)
GIT_PINS: Tuple[str, ...] = ('-c', 'color.ui=never', '-c', 'color.diff=never', '-c', 'color.grep=never',
                             '-c', 'grep.column=false', '-c', 'log.showSignature=false', '-c', 'diff.interHunkContext=0')
PROBE_DIR: Path = Path(__file__).resolve().parent / 'watch_probe'
PROBE_MODULE: str = 'test_watch_probe'
PROBE_IMPORT_ERROR: str = 'Error importing plugin "%s"' % PROBE_MODULE
# 명령은 하위 셸에서 eval — 명령 안 `exit` 가 끝 코드 줄을 건너뛰지 않는다. 끝 코드는 임시 파일에 쓴 뒤 옮겨 놓는다(쓰다 만 파일을 읽지 않게).
WRAPPER: str = '(eval "$TEST_WATCH_CMD"); echo $? > "$TEST_WATCH_EXIT.tmp" && mv -f "$TEST_WATCH_EXIT.tmp" "$TEST_WATCH_EXIT"'
FORWARDED: Tuple[int, ...] = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)
SIGNAL_NAMES: Dict[int, str] = {signal.SIGINT: 'INT', signal.SIGTERM: 'TERM', signal.SIGKILL: 'KILL'}

_RECEIVED: List[int] = []                  # 감시가 받은 신호(처리기가 덧붙이고 감시 고리가 본다)
_LAUNCHED: List['subprocess.Popen[bytes]'] = []   # 이 run 이 띄운 자식(거두기 전이라 번호가 다른 묶음에 다시 쓰이지 않는다)


class ToolError(Exception):
    """도구 오류 — 결과 줄 `도구 오류` · exit 70."""


class Outcome(NamedTuple):
    kind: str                              # end · unknown · stall · cut
    code: int = 0                          # end: 끝 코드 · cut: 받은 신호
    detail: str = ''                       # unknown: 까닭
    nodes: Tuple[str, ...] = ()            # stall: 오래 도는 시험
    left: int = 0                          # end: 끝났지만 남은 프로세스 수


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise ToolError('인자 — %s' % message)


def say(line: str) -> None:
    try:
        print(line, flush=True)
    except (BrokenPipeError, OSError):
        pass


def _minutes(text: str) -> float:
    try:
        value: float = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError('분은 수다: %r' % text)
    if not value > 0:
        raise argparse.ArgumentTypeError('분은 0 보다 커야 한다: %r' % text)
    return value


# ---------- 감시 폴더 자리

def _git(*args: str) -> Optional[str]:
    try:
        done = subprocess.run(['git', *GIT_PINS, *args], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
    except OSError:
        return None
    out: str = done.stdout.decode('utf-8', 'surrogateescape').strip()
    return out if done.returncode == 0 and out else None


def _places() -> Tuple[Path, Path]:
    """(git 디렉터리 아래 자리, TMPDIR 아래 물러날 자리)."""
    git_dir: Optional[str] = _git('rev-parse', '--absolute-git-dir')
    top: Optional[str] = _git('rev-parse', '--show-toplevel')
    if not git_dir or not top:
        raise ToolError('git 작업 트리가 아님 — 감시 폴더 자리를 정할 수 없다(%s)' % os.getcwd())
    digest: str = hashlib.sha256(top.encode('utf-8', 'surrogateescape')).hexdigest()[:16]
    return Path(git_dir) / WATCH_DIR, Path(tempfile.gettempdir()) / WATCH_DIR / digest


def _new_folder() -> Path:
    tried: List[str] = []
    for parent in _places():
        try:
            parent.mkdir(parents=True, exist_ok=True)
            for _ in range(5):
                name: str = '%s-%s' % (time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()), secrets.token_hex(4))
                try:
                    (parent / name).mkdir()
                except FileExistsError:
                    continue
                return parent / name
        except OSError as error:
            tried.append('%s (%s)' % (parent, error.strerror or error))
            continue
        tried.append('%s (이름 겹침)' % parent)
    raise ToolError('감시 폴더를 만들 수 없음 — ' + ' · '.join(tried))


def _write_atomic(path: Path, text: str) -> None:
    tmp: Path = path.with_name(path.name + '.tmp')
    tmp.write_text(text, encoding='utf-8')
    os.replace(str(tmp), str(path))


def _read_meta(folder: Path) -> Dict[str, object]:
    try:
        meta = json.loads((folder / 'meta.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise ToolError('감시 폴더가 아님 — %s/meta.json 을 읽을 수 없다(%s)' % (folder, error))
    if not isinstance(meta, dict) or not isinstance(meta.get('pgid'), int) or not meta.get('marker'):
        raise ToolError('감시 폴더가 아님 — %s/meta.json 에 PGID · 표지가 없다' % folder)
    return meta


# ---------- 프로세스 묶음

def _process_table() -> Dict[int, List[int]]:
    """PGID → 좀비 아닌 구성원 pid."""
    try:
        done = subprocess.run(['ps', '-A', '-o', 'pid=', '-o', 'pgid=', '-o', 'stat='], stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, env=dict(os.environ, LC_ALL='C'))
    except OSError as error:
        raise ToolError('ps 를 부를 수 없음 — %s' % error)
    table: Dict[int, List[int]] = {}
    for row in done.stdout.decode('ascii', 'replace').splitlines():
        cells: List[str] = row.split()
        if len(cells) < 3 or not cells[0].isdigit() or not cells[1].isdigit() or cells[2].startswith('Z'):
            continue
        table.setdefault(int(cells[1]), []).append(int(cells[0]))
    return table


def _start_time(pid: int) -> str:
    try:
        done = subprocess.run(['ps', '-o', 'lstart=', '-p', str(pid)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              env=dict(os.environ, LC_ALL='C'))
    except OSError:
        return ''
    return done.stdout.decode('ascii', 'replace').strip()


def _has_marker(pid: int, marker: str) -> bool:
    token: str = 'TEST_WATCH_RUN=' + marker
    environ: Path = Path('/proc/%d/environ' % pid)
    if environ.exists():
        try:
            return token.encode() in environ.read_bytes().split(b'\0')
        except OSError:
            return False
    try:
        done = subprocess.run(['ps', '-E', '-ww', '-o', 'command=', '-p', str(pid)], stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, env=dict(os.environ, LC_ALL='C'))
    except OSError:
        return False
    return token in done.stdout.decode('utf-8', 'replace').split()


def _identity(meta: Dict[str, object], table: Optional[Dict[int, List[int]]] = None) -> str:
    """ours · gone(구성원 0) · foreign(지도자가 살아 있는데 시작 시각이 다르고 표지도 없음 — 번호 재사용 의심) ·
    unverified(지도자 없이 남은 구성원에서 표지를 읽지 못함 — macOS 시스템 실행 파일은 환경을 보이지 않는다 · 신호를 보내지 않되 목록에는 보인다)."""
    pgid: int = int(meta['pgid'])  # type: ignore[arg-type]
    members: List[int] = (table if table is not None else _process_table()).get(pgid, [])
    if not members:
        return 'gone'
    leader_start: str = str(meta.get('leader_start') or '')
    if pgid in members and leader_start:
        if _start_time(pgid) == leader_start:
            return 'ours'
        return 'ours' if any(_has_marker(pid, str(meta['marker'])) for pid in members) else 'foreign'
    if any(_has_marker(pid, str(meta['marker'])) for pid in members):
        return 'ours'
    return 'unverified'


def _group_alive(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _forward_int(pgid: int) -> None:
    try:
        os.killpg(pgid, signal.SIGINT)
    except OSError:
        pass


def _on_signal(signum: int, _frame: object) -> None:
    _RECEIVED.append(signum)


def _catch_signals() -> None:
    for signum in FORWARDED:
        signal.signal(signum, _on_signal)


def _child_defaults() -> None:
    """자식 시작 전(fork 뒤 exec 앞) — 감시가 INT · TERM 을 무시하도록 물려받았어도 자식은 기본 처리로 시작한다."""
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)


# ---------- probe · 출력 읽기

def blocks_probe(command: str) -> bool:
    """셸 낱말에 `PYTHONPATH=` 대입이나 `-I` · `-E` 가 있으면 probe 를 실을 수 없다(낱말 단위 — `-rfE` · 노드 id 안 글자는 아님)."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        words: List[str] = list(lexer)
    except ValueError:
        words = command.split()
    return any(w.startswith('PYTHONPATH=') or w in ('-I', '-E') for w in words)


def _size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return -1


def long_tests(notes: Path, after_seconds: float, now: float) -> List[str]:
    """notes 에서 `start` 뒤 `end` 가 없고 시작한 지 after_seconds 를 넘은 노드 id(시작 차례)."""
    try:
        text: str = notes.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return []
    running: Dict[Tuple[str, str], float] = {}
    for line in text.splitlines():
        cells: List[str] = line.split(' ', 3)
        if len(cells) != 4:
            continue
        try:
            at: float = float(cells[1])
        except ValueError:
            continue
        key: Tuple[str, str] = (cells[2], cells[3])
        if cells[0] == 'start':
            running[key] = at
        elif cells[0] == 'end':
            running.pop(key, None)
    nodes: List[str] = []
    for at, (_pid, node) in sorted((at, key) for key, at in running.items()):
        if now - at >= after_seconds and node not in nodes:
            nodes.append(node)
    return nodes


def _read_exit(folder: Path) -> Optional[int]:
    try:
        return int((folder / 'exit').read_text(encoding='ascii').strip())
    except (OSError, ValueError):
        return None


def _log_has(folder: Path, needle: str) -> bool:
    try:
        return needle in (folder / 'out.log').read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False


def _log_line(folder: Path) -> str:
    try:
        text: str = (folder / 'out.log').read_text(encoding='utf-8', errors='replace')
    except OSError:
        text = ''
    failed: int = len(re.findall(r'^FAILED\b', text, re.M))
    errors: int = len(re.findall(r'^ERROR\b', text, re.M))
    return '[watch] 로그 %s · FAILED 줄 %d · ERROR 줄 %d' % (folder / 'out.log', failed, errors)


# ---------- 지켜보기

def _stall(folder: Path, after_minutes: float) -> Outcome:
    """멈춤 의심 — 그 순간의 오래 도는 시험을 stalled 에 적는다(끈 뒤의 notes 는 끊긴 시험에도 end 가 찍혀 다시 읽지 않는다)."""
    nodes: List[str] = long_tests(folder / 'notes', after_minutes * 60, time.time())
    _write_atomic(folder / 'stalled', ''.join(node + '\n' for node in nodes))
    return Outcome('stall', nodes=tuple(nodes))


def _poll_seconds(quiet_seconds: float) -> float:
    return max(0.05, min(1.0, quiet_seconds / 10))


def _left(pgid: int) -> int:
    try:
        return len(_process_table().get(pgid, []))
    except ToolError:
        return 0                               # ps 를 못 불러도 끝 판정은 exit 파일로 선다


def _watch_child(folder: Path, proc: 'subprocess.Popen[bytes]', quiet: float, after: float) -> Outcome:
    quiet_seconds: float = quiet * 60
    poll: float = _poll_seconds(quiet_seconds)
    seen: Tuple[int, int] = (_size(folder / 'out.log'), _size(folder / 'notes'))
    changed: float = time.monotonic()
    while True:
        if _RECEIVED:
            _forward_int(proc.pid)
            return Outcome('cut', code=_RECEIVED[0])
        status: Optional[int] = proc.poll()
        if status is not None:
            code: Optional[int] = _read_exit(folder)
            if code is not None:
                return Outcome('end', code=code, left=_left(proc.pid))
            why: str = '신호 %d' % -status if status < 0 else 'exit 파일 없음 · sh exit %d' % status
            return Outcome('unknown', detail=why)
        now_seen: Tuple[int, int] = (_size(folder / 'out.log'), _size(folder / 'notes'))
        if now_seen != seen:
            seen, changed = now_seen, time.monotonic()
        elif time.monotonic() - changed >= quiet_seconds:
            return _stall(folder, after)
        time.sleep(poll)


def _watch_group(folder: Path, meta: Dict[str, object], quiet: float) -> Outcome:
    pgid: int = int(meta['pgid'])  # type: ignore[arg-type]
    code: Optional[int] = _read_exit(folder)
    if code is not None:
        return Outcome('end', code=code, left=_left(pgid))
    who: str = _identity(meta)
    if who == 'gone':
        return Outcome('unknown', detail='묶음 사라짐 · exit 파일 없음')
    if who == 'foreign':
        return Outcome('unknown', detail='묶음 끝(번호 재사용 의심) · exit 파일 없음')
    quiet_seconds: float = quiet * 60
    poll: float = _poll_seconds(quiet_seconds)
    seen: Tuple[int, int] = (_size(folder / 'out.log'), _size(folder / 'notes'))
    changed: float = time.monotonic()
    while True:
        if _RECEIVED:
            _forward_int(pgid)
            return Outcome('cut', code=_RECEIVED[0])
        code = _read_exit(folder)
        if code is not None:
            return Outcome('end', code=code, left=_left(pgid))
        if not _group_alive(pgid):
            code = _read_exit(folder)
            if code is not None:
                return Outcome('end', code=code)
            return Outcome('unknown', detail='묶음 사라짐 · exit 파일 없음')
        now_seen: Tuple[int, int] = (_size(folder / 'out.log'), _size(folder / 'notes'))
        if now_seen != seen:
            seen, changed = now_seen, time.monotonic()
        elif time.monotonic() - changed >= quiet_seconds:
            return _stall(folder, float(meta.get('after', AFTER_MINUTES)))  # type: ignore[arg-type]
        time.sleep(poll)


def _report(folder: Path, outcome: Outcome, quiet: float, probe: bool) -> int:
    tail: str = '' if probe else ' · probe 없음'
    say(_log_line(folder))
    if outcome.kind == 'end':
        left: str = ' · 끝났지만 남은 프로세스 %d' % outcome.left if outcome.left else ''
        say('[watch] 결과: 끝 exit %d%s%s' % (outcome.code, left, tail))
        return outcome.code
    if outcome.kind == 'unknown':
        say('[watch] 결과: 끝 코드 모름(%s)%s' % (outcome.detail, tail))
        return EXIT_TOOL
    if outcome.kind == 'stall':
        nodes: str = ' '.join(outcome.nodes) if outcome.nodes else '없음'
        say('[watch] 결과: 멈춤 의심 — %g분 출력 없음 · 오래 도는 시험 %s · 폴더 %s%s' % (quiet, nodes, folder, tail))
        return EXIT_STALL
    say('[watch] 결과: 끊김 — 감시가 신호 %d 을 받음 · 자식에 INT 넘김 · 폴더 %s%s' % (outcome.code, folder, tail))
    return 128 + outcome.code


def _launch(command: str, quiet: float, after: float, probe: bool) -> Tuple[Path, 'subprocess.Popen[bytes]']:
    folder: Path = _new_folder()
    marker: str = folder.name
    env: Dict[str, str] = dict(os.environ, TEST_WATCH_RUN=marker, TEST_WATCH_NOTES=str(folder / 'notes'),
                               TEST_WATCH_EXIT=str(folder / 'exit'), TEST_WATCH_CMD=command)
    if probe:
        old_path: str = os.environ.get('PYTHONPATH', '')
        env['PYTHONPATH'] = str(PROBE_DIR) + (os.pathsep + old_path if old_path else '')
        plugins: List[str] = [p for p in os.environ.get('PYTEST_PLUGINS', '').split(',') if p.strip()]
        if PROBE_MODULE not in [p.strip() for p in plugins]:
            plugins.append(PROBE_MODULE)
        env['PYTEST_PLUGINS'] = ','.join(plugins)
    with open(str(folder / 'out.log'), 'ab') as out:
        proc = subprocess.Popen(['sh', '-c', WRAPPER], stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT,
                                env=env, start_new_session=True, preexec_fn=_child_defaults)
    _LAUNCHED.append(proc)
    meta: Dict[str, object] = {
        'pgid': proc.pid, 'leader_start': _start_time(proc.pid), 'marker': marker, 'command': command,
        'quiet': quiet, 'after': after, 'probe': probe, 'cwd': os.getcwd(),
        'started': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }
    _write_atomic(folder / 'meta.json', json.dumps(meta, ensure_ascii=False, indent=1) + '\n')
    say('[watch] 폴더 %s · PGID %d' % (folder, proc.pid))
    return folder, proc


# ---------- 하위 명령

def cmd_run(command: str, quiet: float, after: float) -> int:
    probe: bool = not blocks_probe(command)
    _catch_signals()
    folder, proc = _launch(command, quiet, after, probe)
    if not probe:
        say('[watch] probe 없이 지켜본다 — 셸 낱말에 PYTHONPATH= 대입 · -I · -E 가 있다')
    outcome: Outcome = _watch_child(folder, proc, quiet, after)
    if probe and outcome.kind == 'end' and outcome.code != 0 and _log_has(folder, PROBE_IMPORT_ERROR):
        say(_log_line(folder))
        say('[watch] probe 를 싣지 못해 끝남(exit %d · %s) — probe 없이 새 폴더에서 한 번 다시 띄운다' % (outcome.code, PROBE_IMPORT_ERROR))
        probe = False
        folder, proc = _launch(command, quiet, after, probe)
        outcome = _watch_child(folder, proc, quiet, after)
    return _report(folder, outcome, quiet, probe)


def cmd_attach(folder: Path, quiet: float) -> int:
    folder = folder.resolve()
    meta: Dict[str, object] = _read_meta(folder)
    _catch_signals()
    say('[watch] 다시 지켜봄 — 폴더 %s · PGID %s' % (folder, meta['pgid']))
    return _report(folder, _watch_group(folder, meta, quiet), quiet, bool(meta.get('probe', True)))


def _wait_gone(pgid: int, seconds: float) -> bool:
    deadline: float = time.monotonic() + seconds
    while True:
        if not _group_alive(pgid):
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.2)


def cmd_stop(folder: Path) -> int:
    """결정적 사다리 — INT → 기다림 → TERM → 기다림 → KILL. 단계마다 «내 묶음» 인지 먼저 본다."""
    folder = folder.resolve()
    meta: Dict[str, object] = _read_meta(folder)
    pgid: int = int(meta['pgid'])  # type: ignore[arg-type]
    for signum, wait in ((signal.SIGINT, STOP_INT_WAIT_SECONDS), (signal.SIGTERM, STOP_TERM_WAIT_SECONDS),
                         (signal.SIGKILL, STOP_KILL_WAIT_SECONDS)):
        name: str = SIGNAL_NAMES[signum]
        who: str = _identity(meta)
        if who == 'gone':
            say('[watch] 결과: 묶음 끝 — PGID %d 구성원 0 · %s 안 보냄' % (pgid, name))
            return 0
        if who == 'foreign':
            say('[watch] 결과: 묶음 끝(번호 재사용 의심) — PGID %d 지도자 시작 시각 · 표지가 안 맞음 · 신호 안 보냄' % pgid)
            return 0
        if who == 'unverified':
            say('[watch] 결과: 도구 오류 — 내 묶음인지 확인 못 함(PGID %d · 지도자 없음 · 구성원 표지를 읽을 수 없음) · %s 안 보냄 · 폴더 %s'
                % (pgid, name, folder))
            return EXIT_TOOL
        try:
            os.killpg(pgid, signum)
        except ProcessLookupError:
            say('[watch] 결과: 묶음 끝 — PGID %d 구성원 0 · %s 안 보냄' % (pgid, name))
            return 0
        except PermissionError:
            say('[watch] 결과: 도구 오류 — 다른 실행 환경(PGID %d 에 신호를 보낼 권한 없음) — run 과 같은 환경(샌드박스 밖이면 밖)에서 다시' % pgid)
            return EXIT_TOOL
        say('[watch] %s 보냄 — PGID %d · %g초 기다림' % (name, pgid, wait))
        if _wait_gone(pgid, wait):
            say('[watch] 결과: 끔 — %s 뒤 묶음 0 · 폴더 %s' % (name, folder))
            return 0
    say('[watch] 결과: 도구 오류 — KILL 뒤에도 PGID %d 묶음이 남음' % pgid)
    return EXIT_TOOL


def cmd_list() -> int:
    places: Tuple[Path, Path] = _places()
    table: Dict[int, List[int]] = _process_table()
    alive: int = 0
    now: float = time.time()
    for parent in places:
        if not parent.is_dir():
            continue
        for folder in sorted(parent.iterdir()):
            try:
                meta: Dict[str, object] = _read_meta(folder)
            except ToolError:
                continue
            who: str = _identity(meta, table)
            if who not in ('ours', 'unverified'):
                continue
            alive += 1
            nodes: List[str] = long_tests(folder / 'notes', float(meta.get('after', AFTER_MINUTES)) * 60, now)  # type: ignore[arg-type]
            command: str = str(meta.get('command', '')).replace('\n', '\\n')
            mark: str = '' if who == 'ours' else '(내 묶음인지 확인 못 함 — stop 은 신호를 보내지 않는다)'
            say('[watch] 살아 있음%s: 폴더 %s · PGID %s · 시작 %s · 오래 도는 시험 %s · 명령 %s'
                % (mark, folder, meta['pgid'], meta.get('started', '?'), ' '.join(nodes) if nodes else '없음', command))
    say('[watch] 살아 있는 묶음 %d' % alive)
    return 0


def _parse(argv: List[str]) -> Tuple[str, argparse.Namespace, Optional[str]]:
    if not argv or argv[0] not in ('run', 'attach', 'stop', 'list'):
        raise ToolError('하위 명령은 run · attach · stop · list 중 하나')
    sub: str = argv[0]
    parser = _Parser(prog='test_watch.py ' + sub, add_help=False)
    command: Optional[str] = None
    rest: List[str] = argv[1:]
    if sub == 'run':
        if '--' not in rest:
            raise ToolError("run 은 -- 뒤에 셸 명령 한 덩이를 받는다 — test_watch.py run [--quiet 분] [--after 분] -- '<명령>'")
        cut: int = rest.index('--')
        tail: List[str] = rest[cut + 1:]
        if len(tail) != 1 or not tail[0].strip():
            raise ToolError('-- 뒤 인자는 하나다(셸 글 한 덩이를 따옴표로 묶는다) — 받은 인자 %d' % len(tail))
        command, rest = tail[0], rest[:cut]
        parser.add_argument('--quiet', type=_minutes, default=QUIET_MINUTES)
        parser.add_argument('--after', type=_minutes, default=AFTER_MINUTES)
    elif sub == 'attach':
        parser.add_argument('folder', type=Path)
        parser.add_argument('--quiet', type=_minutes, default=QUIET_MINUTES)
    elif sub == 'stop':
        parser.add_argument('folder', type=Path)
    return sub, parser.parse_args(rest), command


def main(argv: List[str]) -> int:
    try:
        sub, args, command = _parse(argv)
        if sub == 'run':
            assert command is not None
            return cmd_run(command, args.quiet, args.after)
        if sub == 'attach':
            return cmd_attach(args.folder, args.quiet)
        if sub == 'stop':
            return cmd_stop(args.folder)
        return cmd_list()
    except Exception as error:  # ToolError 와 뜻밖의 오류 — 띄운 자식이 감시 없이 남지 않게 INT 를 넘기고 끝낸다
        handed: bool = False
        for proc in _LAUNCHED:
            if proc.poll() is None:
                _forward_int(proc.pid)
                handed = True
        why: str = str(error) if isinstance(error, ToolError) else '%s: %s' % (type(error).__name__, error)
        say('[watch] 결과: 도구 오류 — %s%s' % (why, ' · 감시 없이 남지 않게 띄운 묶음에 INT 를 넘김' if handed else ''))
        return EXIT_TOOL


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
