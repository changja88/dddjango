"""test_watch.py · probe 픽스처 — 멈춘 시험 깨우기 도구의 결정적 시험(임시 git 저장소만 쓰고 끝나면 지운다).

묶음(설계 4판 §6 도구 시험 ①~⑨ + 덧붙임):
  stall    ① 조용히 자는 명령 → 멈춤 의심 · 묶음 생존 / pytest 멈춤 → 오래 도는 시험 노드 id · stalled 는 멈춤 순간에 고정
  alive    ② 느리지만 출력(out.log) 이 이어지거나 notes 만 자라는 명령 → 멈춤 의심 없음
  exit     ③ 끝 코드 전달 · 신호로 끝난 실행 → 끝 코드 모름 · 앞 실행 폴더와 섞이지 않음 · 끝 코드는 tmp → mv(빈칸 든 경로)
  attach   ④ attach 끝 · 다시 멈춤 · exit 파일 뒤 남은 구성원 · 묶음 사라짐
  probe    ⑤ probe 노드 id(클래스 · 매개변수 · 빈칸 · xdist 2) · 스레드 수 시험 통과 · 기존 PYTHONPATH · PYTEST_PLUGINS 보존
  probeoff 셸 낱말 `PYTHONPATH=` · `-I` · `-E` → 처음부터 probe 없음(`-rfE` · 노드 id 안 글자는 아님) · 적재 오류 → 곧바로 한 번 다시
  sigint   감시가 INT 무시로 띄워져도 자식은 INT 기본 처리
  stop     ⑥ stop 사다리(INT → TERM → KILL · 기다림 상수를 줄인 사본) · 지도자 없이 표지로 내 묶음 · 남의 묶음(표지 없음)에 신호 0
  cut      ⑦ 감시가 TERM 을 받으면 자식에 INT(감시는 INT 무시로 띄움) → pytest 가 끝남
  args     ⑧ `--` 뒤 인자 둘 거절 · `--` 없음 거절 · git 아님 도구 오류
  list     ⑨ list — 살아 있는 묶음만 · 명령 · 오래 도는 시험 / TMPDIR 로 물러난 폴더도 본다
pytest 가 드는 묶음은 저장소 뿌리의 `.venv-probe`(pytest · xdist)로 돈다 — 없으면 FAIL 로 알린다(make probe-env).
신호는 이 픽스처가 띄운 프로세스와, 도구가 첫 줄에 찍은 묶음(meta.json 의 지도자 시작 시각 · 표지가 맞을 때)에만 보낸다.

사용: python3 fixtures_test_watch.py [--tool <test_watch.py>] [묶음 이름 …]   (--tool 기본 = 이 폴더 위의 test_watch.py)
exit 0 = 전건 통과 · 1 = 실패 있음.
"""
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

sys.dont_write_bytecode = True

TEST: Path = Path(__file__).resolve().parent
REPO: Path = TEST.parents[2]
PROBE_PY: Path = REPO / '.venv-probe' / 'bin' / 'python'
PY: str = sys.executable
PASS = FAIL = 0
GROUPS: List[Tuple[int, Path]] = []          # 도구가 첫 줄에 찍은 (PGID, 감시 폴더) — 끝에 남았으면 거둔다
PROCS: List['subprocess.Popen[bytes]'] = []  # 이 픽스처가 직접 띄운 프로세스
ENV: Dict[str, str] = {k: v for k, v in os.environ.items()
                       if not k.startswith('TEST_WATCH_') and k not in ('PYTEST_PLUGINS', 'PYTEST_ADDOPTS')}
ENV['PYTHONDONTWRITEBYTECODE'] = '1'      # probe 폴더 · 장난감에 __pycache__ 를 남기지 않는다
PYTEST: str = '%s -m pytest -q -p no:cacheprovider' % shlex.quote(str(PROBE_PY))

TOY_FILES: Dict[str, str] = {
    'pytest.ini': '[pytest]\n',
    'test_h.py': 'import time\n\n\ndef test_quick():\n    pass\n\n\ndef test_hang():\n    time.sleep(60)\n',
    'test_ids.py': (
        'import threading\nimport time\n\nimport pytest\n\n\n'
        "@pytest.mark.parametrize('i', range(4))\ndef test_fast(i):\n    time.sleep(0.05)\n\n\n"
        "class TestBox:\n    @pytest.mark.parametrize('b', ['x', 'y'])\n    def test_slow(self, b):\n        time.sleep(0.3)\n\n\n"
        "@pytest.mark.parametrize('s', ['a b'])\ndef test_space(s):\n    pass\n\n\n"
        'def test_thread_count():\n    assert threading.active_count() == 1\n\n\n'
        'def test_join_all():\n    for t in threading.enumerate():\n        if t is not threading.main_thread():\n'
        '            t.join(timeout=1)\n            assert not t.is_alive()\n'),
    'test_a.py': "import pytest\n\n\ndef test_a():\n    pass\n\n\n@pytest.mark.parametrize('v', ['-I'])\ndef test_p(v):\n    pass\n",
    'test_fail.py': 'def test_f():\n    assert False\n',
    'myplug.py': "import os\n\n\ndef pytest_configure(config):\n    with open(os.environ['MYPLUG_MARK'], 'a') as fh:\n        fh.write('configured\\n')\n",
}
IDS: Tuple[str, ...] = ('test_ids.py::test_fast[0]', 'test_ids.py::test_fast[3]', 'test_ids.py::TestBox::test_slow[x]',
                        'test_ids.py::TestBox::test_slow[y]', 'test_ids.py::test_space[a b]', 'test_ids.py::test_thread_count',
                        'test_ids.py::test_join_all')


def check(name: str, ok: object, detail: object = '') -> bool:
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name, flush=True)
    if not ok and detail:
        print('    ' + str(detail).replace('\n', '\n    ')[:2400], flush=True)
    return bool(ok)


# ---------- 준비 · 부르기

def new_repo(parent: Path, name: str, toy: bool = False) -> Path:
    root: Path = parent / name
    root.mkdir(parents=True)
    subprocess.run(['git', 'init', '-q', str(root)], check=True, env=ENV)
    if toy:
        for rel, text in TOY_FILES.items():
            (root / rel).write_text(text, encoding='utf-8')
    return root


def _record(out: str) -> None:
    for folder, pgid in re.findall(r'^\[watch\] 폴더 (.+?) · PGID (\d+)$', out, re.M):
        GROUPS.append((int(pgid), Path(folder)))


def tool(tool_path: Path, args: List[str], cwd: Path, env: Optional[Dict[str, str]] = None,
         timeout: float = 60) -> Tuple[Optional[int], str]:
    try:
        done = subprocess.run([PY, str(tool_path)] + args, cwd=str(cwd), env=env or ENV, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=timeout)
        rc: Optional[int] = done.returncode
        out: str = done.stdout.decode('utf-8', 'replace')
    except subprocess.TimeoutExpired as error:
        rc, out = None, (error.output or b'').decode('utf-8', 'replace') + '\n<시간 초과 %gs>' % timeout
    _record(out)
    return rc, out


def spawn(tool_path: Path, args: List[str], cwd: Path, ignore_int: bool = False,
          env: Optional[Dict[str, str]] = None) -> 'subprocess.Popen[bytes]':
    """도구를 배경으로 띄운다 — ignore_int 면 셸 `&` · `nohup … &` 처럼 INT 를 무시하도록 물려준다."""
    def _ign() -> None:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    proc = subprocess.Popen([PY, str(tool_path)] + args, cwd=str(cwd), env=env or ENV, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, preexec_fn=_ign if ignore_int else None)
    PROCS.append(proc)
    return proc


def collect(proc: 'subprocess.Popen[bytes]', timeout: float) -> Tuple[Optional[int], str]:
    try:
        data, _ = proc.communicate(timeout=timeout)
        rc: Optional[int] = proc.returncode
    except subprocess.TimeoutExpired:
        proc.kill()
        data, _ = proc.communicate()
        rc = None
    out: str = data.decode('utf-8', 'replace')
    _record(out)
    return rc, out


def last(out: str) -> str:
    lines: List[str] = [line for line in out.splitlines() if line.strip()]
    return lines[-1] if lines else ''


def folders(out: str) -> List[Path]:
    return [Path(f) for f in re.findall(r'^\[watch\] 폴더 (.+?) · PGID \d+$', out, re.M)]


def pgids(out: str) -> List[int]:
    return [int(p) for p in re.findall(r'^\[watch\] 폴더 .+? · PGID (\d+)$', out, re.M)]


def alive(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def wait_for(pred: Callable[[], bool], seconds: float) -> bool:
    deadline: float = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if pred():
            return True
        time.sleep(0.1)
    return pred()


def read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return ''


def mutant(tmp: Path, tool_path: Path, name: str, edits: List[Tuple[str, str]]) -> Path:
    """도구 사본(probe 폴더 함께) — 상수를 줄이는 등 글자 바꾸기. 바꿀 글자가 정확히 한 번 있어야 한다."""
    where: Path = tmp / ('mutant-' + name)
    where.mkdir()
    shutil.copytree(str(tool_path.parent / 'watch_probe'), str(where / 'watch_probe'))
    text: str = tool_path.read_text(encoding='utf-8')
    for old, new in edits:
        if text.count(old) != 1:
            raise RuntimeError('사본 %s: 바꿀 글자가 %d 번 — %r' % (name, text.count(old), old))
        text = text.replace(old, new)
    (where / 'test_watch.py').write_text(text, encoding='utf-8')
    return where / 'test_watch.py'


def fast_stop(tmp: Path, tool_path: Path) -> Path:
    return mutant(tmp, tool_path, 'stop', [('STOP_INT_WAIT_SECONDS: float = 120.0', 'STOP_INT_WAIT_SECONDS: float = 1.0'),
                                           ('STOP_TERM_WAIT_SECONDS: float = 120.0', 'STOP_TERM_WAIT_SECONDS: float = 1.0')])


def need_pytest() -> bool:
    return check('pytest 장난감 인터프리터 %s 있음(없으면 make probe-env)' % PROBE_PY, os.access(str(PROBE_PY), os.X_OK))


# ---------- 묶음

def bundle_stall(tmp: Path, tool_path: Path) -> None:
    repo: Path = new_repo(tmp, 'stall', toy=True)
    t0: float = time.monotonic()
    rc, out = tool(tool_path, ['run', '--quiet', '0.03', '--', 'echo hi; sleep 30'], repo, timeout=30)
    took: float = time.monotonic() - t0
    f: List[Path] = folders(out)
    check('① 조용히 자는 명령 → 멈춤 의심 exit 75(%s)' % rc, rc == 75 and '[watch] 결과: 멈춤 의심 — 0.03분 출력 없음 · 오래 도는 시험 없음 · 폴더 ' in last(out), out)
    check('① 무변화 시간을 채운 뒤에 깨어남(%.1f초 ≥ 1.8초)' % took, took >= 1.8, out)
    check('① 멈춤 의심 뒤에도 묶음은 산다(자식을 끄지 않음)', bool(pgids(out)) and alive(pgids(out)[0]), out)
    check('① stalled 파일을 적음(오래 도는 시험 없음 = 빈 파일)', bool(f) and (f[0] / 'stalled').is_file() and read(f[0] / 'stalled') == '', out)
    for g in f:
        tool(tool_path, ['stop', str(g)], repo)
    if not need_pytest():
        return
    rc, out = tool(tool_path, ['run', '--quiet', '0.1', '--after', '0.01', '--', PYTEST + ' test_h.py'], repo, timeout=40)
    f = folders(out)
    check('① pytest 멈춤 → 결과 줄에 오래 도는 시험 노드 id', rc == 75 and '· 오래 도는 시험 test_h.py::test_hang · 폴더 ' in last(out), out)
    stalled: str = read(f[0] / 'stalled') if f else ''
    check('① stalled = 멈춤 순간의 오래 도는 시험', stalled == 'test_h.py::test_hang\n', repr(stalled))
    rc_l, out_l = tool(tool_path, ['list'], repo)
    check('⑨ list 가 멈춘 pytest 묶음 · 오래 도는 시험 · 명령을 찍는다',
          rc_l == 0 and re.search(r'살아 있음: 폴더 .+ · 오래 도는 시험 test_h\.py::test_hang · 명령 .+-m pytest -q -p no:cacheprovider test_h\.py$',
                                  out_l, re.M) is not None, out_l)
    if f:
        rc_s, out_s = tool(tool_path, ['stop', str(f[0])], repo, timeout=60)
        check('① stop(INT) 으로 pytest 묶음이 끝남', rc_s == 0 and '[watch] 결과: 끔 — INT 뒤 묶음 0' in last(out_s), out_s)
        notes: str = read(f[0] / 'notes')
        check('① 끊긴 시험에도 notes 에 end 가 찍힌다(그래서 stalled 를 멈춤 순간에 적는다)',
              re.search(r'^end \S+ \d+ test_h\.py::test_hang$', notes, re.M) is not None, notes)
        check('① 끈 뒤에도 stalled 는 그대로', read(f[0] / 'stalled') == 'test_h.py::test_hang\n', read(f[0] / 'stalled'))


def bundle_alive(tmp: Path, tool_path: Path) -> None:
    repo: Path = new_repo(tmp, 'alive')
    rc, out = tool(tool_path, ['run', '--quiet', '0.05', '--', 'for i in 1 2 3 4 5 6 7 8 9 10; do echo $i; sleep 0.5; done'], repo, timeout=30)
    check('② 출력이 이어지면 무변화 상한(3초)을 넘겨 돌아도 멈춤 의심 없음', rc == 0 and last(out) == '[watch] 결과: 끝 exit 0', out)
    cmd: str = 'for i in 1 2 3 4 5 6 7 8 9 10; do echo "start 0 1 x$i" >> "$TEST_WATCH_NOTES"; sleep 0.5; done'
    rc, out = tool(tool_path, ['run', '--quiet', '0.05', '--', cmd], repo, timeout=30)
    check('② notes 만 자라도 진행 중', rc == 0 and last(out) == '[watch] 결과: 끝 exit 0', out)


def bundle_exit(tmp: Path, tool_path: Path) -> None:
    repo: Path = new_repo(tmp, 'exit')
    rc, out = tool(tool_path, ['run', '--quiet', '0.5', '--', 'echo one; exit 7'], repo)
    check('③ 끝 코드 전달(명령 안 exit 7 → 끝 exit 7 · 도구 exit 7)', rc == 7 and last(out) == '[watch] 결과: 끝 exit 7', out)
    first: List[Path] = folders(out)
    rc, out = tool(tool_path, ['run', '--quiet', '0.5', '--', 'kill -TERM $$'], repo)
    second: List[Path] = folders(out)
    check('③ 셸이 신호로 끝남 → 끝 코드 모름(신호 15) · exit 70', rc == 70 and last(out) == '[watch] 결과: 끝 코드 모름(신호 15)', out)
    check('③ 실행마다 새 폴더 — 앞 실행의 exit 파일과 섞이지 않음',
          len(first) == 1 and len(second) == 1 and first[0] != second[0] and not (second[0] / 'exit').exists()
          and read(first[0] / 'exit') == '7\n', (first, second))
    spaced: Path = new_repo(tmp / 'with space', 'repo with space')
    rc, out = tool(tool_path, ['run', '--quiet', '0.5', '--', 'printf "%s\\n" "$TEST_WATCH_EXIT" > where.txt; exit 4'], spaced)
    f: List[Path] = folders(out)
    check('③ 빈칸 든 경로 — 끝 코드 파일 경로는 환경 변수 · exit 파일 4 · 임시 파일 안 남음',
          rc == 4 and bool(f) and read(spaced / 'where.txt') == str(f[0] / 'exit') + '\n' and read(f[0] / 'exit') == '4\n'
          and not (f[0] / 'exit.tmp').exists(), (out, read(spaced / 'where.txt')))
    rc, out = tool(tool_path, ['run', '--quiet', '0.5', '--', 'mkdir "$TEST_WATCH_EXIT.tmp"'], repo)
    f = folders(out)
    check('③ 끝 코드는 임시 파일을 거쳐 옮긴다(임시 자리를 막으면 exit 파일이 생기지 않고 끝 코드 모름)',
          rc == 70 and last(out).startswith('[watch] 결과: 끝 코드 모름(') and bool(f) and not (f[0] / 'exit').exists(), out)


def bundle_attach(tmp: Path, tool_path: Path) -> None:
    repo: Path = new_repo(tmp, 'attach')
    rc, out = tool(tool_path, ['run', '--quiet', '0.02', '--', 'sleep 5; echo done'], repo)
    f: List[Path] = folders(out)
    if check('④ 준비 — 5초 자는 명령이 먼저 멈춤 의심', rc == 75 and bool(f), out):
        rc, out = tool(tool_path, ['attach', str(f[0]), '--quiet', '0.5'], repo)
        check('④ attach → exit 파일이 생기면 끝 exit 0', rc == 0 and last(out) == '[watch] 결과: 끝 exit 0', out)
    rc, out = tool(tool_path, ['run', '--quiet', '0.02', '--', 'sleep 30'], repo)
    f = folders(out)
    if check('④ 준비 — 30초 자는 명령 멈춤 의심', rc == 75 and bool(f), out):
        (f[0] / 'stalled').unlink()
        rc, out = tool(tool_path, ['attach', str(f[0]), '--quiet', '0.02'], repo)
        check('④ attach 도 무변화면 다시 멈춤 의심 · stalled 를 다시 적음',
              rc == 75 and '[watch] 결과: 멈춤 의심 — 0.02분 출력 없음 · 오래 도는 시험 없음 · 폴더 %s' % f[0] in last(out)
              and (f[0] / 'stalled').is_file(), out)
        tool(tool_path, ['stop', str(f[0])], repo)
    sleeper: str = '%s -c "import time; time.sleep(30)" & sleep 4; echo end' % shlex.quote(PY)
    rc, out = tool(tool_path, ['run', '--quiet', '0.02', '--', sleeper], repo)
    f = folders(out)
    if check('④ 준비 — 배경 구성원을 남기는 명령 멈춤 의심', rc == 75 and bool(f), out):
        rc, out = tool(tool_path, ['attach', str(f[0]), '--quiet', '0.5'], repo)
        check('④ exit 파일 뒤 남은 구성원 → 끝 exit 0 · 끝났지만 남은 프로세스 1',
              rc == 0 and last(out) == '[watch] 결과: 끝 exit 0 · 끝났지만 남은 프로세스 1', out)
        stop_tool: Path = fast_stop(tmp, tool_path)
        rc, out = tool(stop_tool, ['stop', str(f[0])], repo)
        check('⑥ 지도자(sh) 없이 남은 구성원 — 표지로 내 묶음 · 배경 작업은 INT 를 무시해 TERM 에서 끝남',
              rc == 0 and 'INT 보냄' in out and 'TERM 보냄' in out and '[watch] 결과: 끔 — TERM 뒤 묶음 0' in last(out), out)
    rc, out = tool(tool_path, ['run', '--quiet', '0.5', '--', 'kill -KILL $$'], repo)
    f = folders(out)
    if check('④ 준비 — KILL 로 끝난 실행 → 끝 코드 모름(신호 9)', rc == 70 and last(out) == '[watch] 결과: 끝 코드 모름(신호 9)' and bool(f), out):
        rc, out = tool(tool_path, ['attach', str(f[0]), '--quiet', '0.5'], repo)
        check('④ 묶음이 사라졌는데 exit 파일 없음 → 끝 코드 모름', rc == 70 and last(out) == '[watch] 결과: 끝 코드 모름(묶음 사라짐 · exit 파일 없음)', out)


def bundle_probe(tmp: Path, tool_path: Path) -> None:
    if not need_pytest():
        return
    repo: Path = new_repo(tmp, 'probe', toy=True)
    rc, out = tool(tool_path, ['run', '--quiet', '0.5', '--', PYTEST + ' -n 2 test_ids.py'], repo, timeout=60)
    f: List[Path] = folders(out)
    notes: str = read(f[0] / 'notes') if f else ''
    log: str = read(f[0] / 'out.log') if f else ''
    check('⑤ pytest -n 2 통과 · 끝 exit 0(스레드 수 · 모든 스레드 기다림 시험 포함)', rc == 0 and last(out) == '[watch] 결과: 끝 exit 0'
          and '9 passed' in log, (out, log))
    for node in IDS:
        check('⑤ notes 에 정확한 노드 id 의 start · end — %s' % node,
              re.search(r'^start \d+\.\d{3} \d+ %s$' % re.escape(node), notes, re.M) is not None
              and re.search(r'^end \d+\.\d{3} \d+ %s$' % re.escape(node), notes, re.M) is not None, notes)
    workers: set = set(re.findall(r'^start \S+ (\d+) ', notes, re.M))
    check('⑤ xdist 일꾼 둘이 notes 에 적음(pid %d 개)' % len(workers), len(workers) == 2, notes)
    check('⑤ probe 는 출력을 늘리지 않는다', 'test_watch_probe' not in out and 'TEST_WATCH' not in out, out)
    env: Dict[str, str] = dict(ENV, PYTHONPATH=str(repo), PYTEST_PLUGINS='myplug', MYPLUG_MARK=str(repo / 'myplug.mark'),
                               PYTEST_ADDOPTS='-p no:randomly')
    rc, out = tool(tool_path, ['run', '--quiet', '0.5', '--', PYTEST + ' test_a.py'], repo, env=env, timeout=60)
    f = folders(out)
    check('⑤ 기존 PYTHONPATH · PYTEST_PLUGINS · PYTEST_ADDOPTS 보존 — 프로젝트 플러그인과 probe 가 함께 실림',
          rc == 0 and 'configured' in read(repo / 'myplug.mark') and bool(f) and 'start ' in read(f[0] / 'notes'), out)


def bundle_probeoff(tmp: Path, tool_path: Path) -> None:
    if not need_pytest():
        return
    repo: Path = new_repo(tmp, 'probeoff', toy=True)
    py: str = shlex.quote(str(PROBE_PY))
    for label, cmd in (('PYTHONPATH= 대입', 'PYTHONPATH=. ' + PYTEST + ' test_a.py'),
                       ('-I', py + ' -I -m pytest -q -p no:cacheprovider test_a.py'),
                       ('-E', py + ' -E -m pytest -q -p no:cacheprovider test_a.py')):
        rc, out = tool(tool_path, ['run', '--quiet', '0.5', '--', cmd], repo, timeout=60)
        f: List[Path] = folders(out)
        check('probe 없음 — 셸 낱말 %s → 처음부터 probe 없이 · 다시 띄우지 않음 · 첫 줄은 폴더 · PGID' % label,
              rc == 0 and last(out) == '[watch] 결과: 끝 exit 0 · probe 없음' and len(f) == 1
              and out.splitlines()[0].startswith('[watch] 폴더 ') and '다시 띄운다' not in out
              and read(f[0] / 'notes') == '', out)
    rc, out = tool(tool_path, ['run', '--quiet', '0.5', '--', PYTEST + ' -rfE "test_a.py::test_p[-I]"'], repo, timeout=60)
    f = folders(out)
    check('probe 있음 — `-rfE` · 노드 id 안 `-I` 는 낱말이 아니다',
          rc == 0 and last(out) == '[watch] 결과: 끝 exit 0' and bool(f) and 'start ' in read(f[0] / 'notes'), out)
    cmd: str = PYTEST + ' test_a.py && env -u PYTHONPATH ' + PYTEST + ' test_a.py'
    rc, out = tool(tool_path, ['run', '--quiet', '0.5', '--', cmd], repo, timeout=60)
    f = folders(out)
    check('probe 적재 오류(앞 pytest 는 probe 로 돎 · 뒤 pytest 만 못 실음) → probe 없이 새 폴더에서 한 번 다시 · 끝 exit 0 · probe 없음',
          rc == 0 and last(out) == '[watch] 결과: 끝 exit 0 · probe 없음' and len(f) == 2 and f[0] != f[1]
          and 'probe 를 싣지 못해 끝남' in out and 'start ' in read(f[0] / 'notes') and read(f[1] / 'notes') == '', out)
    rc, out = tool(tool_path, ['run', '--quiet', '0.5', '--', PYTEST + ' test_fail.py'], repo, timeout=60)
    check('시험 실패(적재 오류 줄 없음)는 다시 띄우지 않음 · FAILED 줄 수',
          rc == 1 and last(out) == '[watch] 결과: 끝 exit 1' and len(folders(out)) == 1 and 'FAILED 줄 1 ·' in out, out)


def bundle_sigint(tmp: Path, tool_path: Path) -> None:
    repo: Path = new_repo(tmp, 'sigint')
    show: str = ('%s -c "import signal; h = signal.getsignal(signal.SIGINT); '
                 'print(\'INT\', \'IGN\' if h == signal.SIG_IGN else \'DFL\' if h is signal.default_int_handler else h)"'
                 % shlex.quote(PY))
    control = subprocess.run(['sh', '-c', show], env=ENV, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN))
    check('준비 — INT 무시로 띄운 프로세스의 자식은 INT 를 무시한다(대조)', b'INT IGN' in control.stdout, control.stdout)
    rc, out = collect(spawn(tool_path, ['run', '--quiet', '0.5', '--', show], repo, ignore_int=True), 30)
    f: List[Path] = folders(out)
    log: str = read(f[0] / 'out.log') if f else ''
    check('감시가 INT 무시로 띄워져도 자식은 INT 기본 처리', rc == 0 and 'INT DFL' in log, (out, log))


def bundle_stop(tmp: Path, tool_path: Path) -> None:
    repo: Path = new_repo(tmp, 'stop')
    stop_tool: Path = fast_stop(tmp, tool_path)
    py: str = shlex.quote(PY)
    rc, out = tool(tool_path, ['run', '--quiet', '0.02', '--', "trap '' INT; %s -c 'import time; time.sleep(60)'" % py], repo)
    f: List[Path] = folders(out)
    if check('⑥ 준비 — INT 를 무시하는 명령 멈춤 의심', rc == 75 and bool(f), out):
        rc, out = tool(stop_tool, ['stop', str(f[0])], repo)
        check('⑥ 사다리 INT → TERM(INT 무시 묶음은 TERM 에서 끝남 · KILL 안 보냄)',
              rc == 0 and 'INT 보냄' in out and 'TERM 보냄' in out and 'KILL' not in out
              and last(out) == '[watch] 결과: 끔 — TERM 뒤 묶음 0 · 폴더 %s' % f[0], out)
    hard: str = "trap '' INT TERM; %s -c 'import time; time.sleep(60)'" % py
    rc, out = tool(tool_path, ['run', '--quiet', '0.02', '--', hard], repo)
    f = folders(out)
    if check('⑥ 준비 — INT · TERM 을 무시하는 명령 멈춤 의심', rc == 75 and bool(f), out):
        rc, out = tool(stop_tool, ['stop', str(f[0])], repo)
        check('⑥ 사다리 INT → TERM → KILL', rc == 0 and 'KILL 보냄' in out and '[watch] 결과: 끔 — KILL 뒤 묶음 0' in last(out)
              and not alive(pgids_of(f[0])), out)
        rc, out = tool(stop_tool, ['stop', str(f[0])], repo)
        check('⑥ 이미 끝난 묶음 → 묶음 끝 · 신호 안 보냄', rc == 0 and '[watch] 결과: 묶음 끝 — PGID ' in last(out) and '보냄 —' not in out, out)
    other = subprocess.Popen([PY, '-c', 'import time; time.sleep(30)'], env=ENV, start_new_session=True)
    PROCS.append(other)
    fake: Path = tmp / 'fake-watch' / 'x'
    fake.mkdir(parents=True)
    (fake / 'meta.json').write_text(json.dumps({'pgid': other.pid, 'leader_start': 'Thu Jan  1 00:00:00 1970',
                                                'marker': 'not-this-run', 'command': 'sleep', 'after': 5, 'probe': True}),
                                    encoding='utf-8')
    time.sleep(0.3)
    rc, out = tool(stop_tool, ['stop', str(fake)], repo)
    check('⑥ 남의 묶음(지도자 시작 시각 다름 · 표지 없음)에 신호 0',
          rc == 0 and '[watch] 결과: 묶음 끝(번호 재사용 의심)' in last(out) and '보냄 —' not in out and other.poll() is None, out)
    other.kill()
    other.wait()


def pgids_of(folder: Path) -> int:
    try:
        return int(json.loads(read(folder / 'meta.json'))['pgid'])
    except (ValueError, KeyError):
        return -1


def bundle_cut(tmp: Path, tool_path: Path) -> None:
    if not need_pytest():
        return
    repo: Path = new_repo(tmp, 'cut', toy=True)
    proc = spawn(tool_path, ['run', '--quiet', '1', '--', PYTEST + ' test_h.py'], repo, ignore_int=True)
    notes_ready: List[Path] = []

    def started() -> bool:
        for f in sorted((repo / '.git' / 'test-watch').glob('*')):
            if re.search(r'^start \S+ \d+ test_h\.py::test_hang$', read(f / 'notes'), re.M):
                notes_ready[:] = [f]
                return True
        return False
    if not check('⑦ 준비 — 멈추는 시험이 시작됨', wait_for(started, 30)):
        collect(proc, 1)
        return
    folder: Path = notes_ready[0].resolve()
    pgid: int = pgids_of(folder)
    proc.send_signal(signal.SIGTERM)
    rc, out = collect(proc, 15)
    check('⑦ 감시가 TERM 을 받으면 끊김 결과 줄 · exit 143(%s)' % rc,
          rc == 143 and last(out) == '[watch] 결과: 끊김 — 감시가 신호 15 을 받음 · 자식에 INT 넘김 · 폴더 %s' % folder, out)
    check('⑦ 자식 묶음은 INT 로 끝남(감시는 INT 무시로 띄움 · pytest 끝 코드 2)',
          wait_for(lambda: not alive(pgid), 15) and wait_for(lambda: read(folder / 'exit') == '2\n', 5), read(folder / 'out.log'))


def bundle_args(tmp: Path, tool_path: Path) -> None:
    repo: Path = new_repo(tmp, 'args')
    rc, out = tool(tool_path, ['run', '--', 'echo', 'two'], repo)
    check('⑧ -- 뒤 인자 둘 → 도구 오류 · exit 70', rc == 70 and last(out).startswith('[watch] 결과: 도구 오류 — -- 뒤 인자는 하나다')
          and not folders(out), out)
    rc, out = tool(tool_path, ['run', 'echo hi'], repo)
    check('⑧ -- 없음 → 도구 오류', rc == 70 and last(out).startswith('[watch] 결과: 도구 오류 — run 은 -- 뒤에'), out)
    plain: Path = tmp / 'not-git'
    plain.mkdir()
    env: Dict[str, str] = dict(ENV, GIT_CEILING_DIRECTORIES=str(tmp))
    rc, out = tool(tool_path, ['run', '--', 'echo hi'], plain, env=env)
    check('⑧ git 저장소 아님 → 도구 오류 · exit 70', rc == 70 and last(out).startswith('[watch] 결과: 도구 오류 — git 작업 트리가 아님'), out)
    rc, out = tool(tool_path, ['list'], plain, env=env)
    check('⑧ git 저장소 아님 — list 도 도구 오류', rc == 70 and '도구 오류' in last(out), out)


def bundle_list(tmp: Path, tool_path: Path) -> None:
    repo: Path = new_repo(tmp, 'list')
    rc, out = tool(tool_path, ['list'], repo)
    check('⑨ 빈 저장소 list → 살아 있는 묶음 0', rc == 0 and last(out) == '[watch] 살아 있는 묶음 0', out)
    tool(tool_path, ['run', '--quiet', '0.5', '--', 'echo finished'], repo)
    one: List[Path] = folders(tool(tool_path, ['run', '--quiet', '0.02', '--', 'sleep 30 # 하나'], repo)[1])
    two: List[Path] = folders(tool(tool_path, ['run', '--quiet', '0.02', '--', 'sleep 31 # 둘'], repo)[1])
    rc, out = tool(tool_path, ['list'], repo)
    rows: List[str] = [line for line in out.splitlines() if line.startswith('[watch] 살아 있음: ')]
    check('⑨ list — 살아 있는 묶음 둘만(끝난 실행 뺌) · 폴더 · PGID · 시작 · 명령',
          rc == 0 and last(out) == '[watch] 살아 있는 묶음 2' and len(rows) == 2 and bool(one) and bool(two)
          and any(str(one[0]) in r and r.endswith('· 명령 sleep 30 # 하나') for r in rows)
          and any(str(two[0]) in r and r.endswith('· 명령 sleep 31 # 둘') for r in rows)
          and all(re.search(r' · PGID \d+ · 시작 \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ · 오래 도는 시험 없음 · ', r) for r in rows), out)
    for f in one + two:
        tool(tool_path, ['stop', str(f)], repo)
    # TMPDIR 로 물러남 — git 디렉터리에 쓸 수 없을 때(Codex workspace-write 샌드박스 꼴)
    ro: Path = new_repo(tmp, 'readonly-git')
    tmpdir: Path = tmp / 'tmpdir'
    tmpdir.mkdir()
    env: Dict[str, str] = dict(ENV, TMPDIR=str(tmpdir))
    os.chmod(str(ro / '.git'), 0o555)
    try:
        rc, out = tool(tool_path, ['run', '--quiet', '0.02', '--', 'sleep 30'], ro, env=env)
        f: List[Path] = folders(out)
        check('git 디렉터리에 못 쓰면 TMPDIR/test-watch/<해시>/ 로 물러남',
              rc == 75 and bool(f) and str(f[0]).startswith(str(tmpdir / 'test-watch') + os.sep)
              and f[0].parent.parent == tmpdir / 'test-watch', out)
        rc, out = tool(tool_path, ['list'], ro, env=env)
        check('⑨ list 가 물러난 자리도 본다', rc == 0 and last(out) == '[watch] 살아 있는 묶음 1' and bool(f) and str(f[0]) in out, out)
        for g in f:
            tool(tool_path, ['stop', str(g)], ro, env=env)
    finally:
        os.chmod(str(ro / '.git'), 0o755)


def bundle_failsafe(tmp: Path, tool_path: Path) -> None:
    """ps 를 못 부르는 환경 · 지도자 없이 표지를 못 읽는 구성원 — 감시 없이 남지 않거나 남의 것일 수 있는 묶음에 신호를 보내지 않는다."""
    repo: Path = new_repo(tmp, 'failsafe')
    bin_dir: Path = tmp / 'bin'
    bin_dir.mkdir()
    for name in ('sh', 'mv', 'sleep', 'git'):
        found: Optional[str] = shutil.which(name)
        if found:
            os.symlink(found, str(bin_dir / name))
    no_ps: Dict[str, str] = dict(ENV, PATH=str(bin_dir))
    rc, out = tool(tool_path, ['run', '--quiet', '0.5', '--', 'sleep 0'], repo, env=no_ps)
    check('ps 없음 — 끝 판정은 exit 파일로 선다(끝 exit 0 · traceback 없음)',
          rc == 0 and last(out) == '[watch] 결과: 끝 exit 0' and 'Traceback' not in out, out)
    rc, out = tool(tool_path, ['run', '--quiet', '0.02', '--', 'sleep 30'], repo, env=no_ps)
    group: List[int] = pgids(out)
    if check('ps 없음 — 멈춤 의심은 그대로 낸다', rc == 75 and bool(group), out):
        rc, out = tool(tool_path, ['stop', str(folders(out)[0])], repo, env=no_ps)
        check('ps 없음 — stop 은 도구 오류로 끝나고 신호를 보내지 않는다(내 묶음인지 못 봄)',
              rc == 70 and last(out).startswith('[watch] 결과: 도구 오류 — ps 를 부를 수 없음') and alive(group[0]), out)
        os.killpg(group[0], signal.SIGKILL)
        wait_for(lambda: not alive(group[0]), 5)
    rc, out = tool(tool_path, ['run', '--quiet', '0.5', '--', 'sleep 30 & exit 0'], repo)
    group = pgids(out)
    f: List[Path] = folders(out)
    if check('준비 — 지도자가 끝나고 sleep 만 남음(끝났지만 남은 프로세스 1)',
             rc == 0 and last(out) == '[watch] 결과: 끝 exit 0 · 끝났지만 남은 프로세스 1' and bool(f), out):
        rc, out = tool(fast_stop(tmp, tool_path), ['stop', str(f[0])], repo)
        rc_l, out_l = tool(tool_path, ['list'], repo)
        if sys.platform == 'darwin':     # macOS 는 시스템 실행 파일(/bin/sleep)의 환경을 보이지 않는다 — 표지를 못 읽음
            check('지도자 없이 표지를 못 읽는 구성원 → 확인 못 함 · 신호 안 보냄 · 도구 오류 · 묶음은 산다',
                  rc == 70 and '내 묶음인지 확인 못 함' in last(out) and 'INT 보냄' not in out and alive(group[0]), out)
            check('⑨ list 는 확인 못 한 묶음도 보인다(표시와 함께)',
                  rc_l == 0 and '[watch] 살아 있음(내 묶음인지 확인 못 함' in out_l and last(out_l) == '[watch] 살아 있는 묶음 1', out_l)
        else:                            # /proc 환경을 읽는 곳은 표지로 내 묶음
            check('지도자 없이 남은 구성원 — 표지로 내 묶음 · 끔', rc == 0 and '[watch] 결과: 끔 —' in last(out), out)
        if group and alive(group[0]):
            os.killpg(group[0], signal.SIGKILL)
            wait_for(lambda: not alive(group[0]), 5)


BUNDLES: Tuple[Callable[[Path, Path], None], ...] = (bundle_stall, bundle_alive, bundle_exit, bundle_attach, bundle_probe,
                                                     bundle_probeoff, bundle_sigint, bundle_stop, bundle_cut, bundle_args, bundle_list,
                                                     bundle_failsafe)


# ---------- 거두기

def _ours(pgid: int, folder: Path) -> bool:
    """도구가 찍은 묶음이 아직 그 실행의 것인지 — 지도자 시작 시각이 meta 와 같거나 구성원 환경에 표지가 있을 때만."""
    try:
        meta = json.loads(read(folder / 'meta.json'))
    except ValueError:
        return False
    if int(meta.get('pgid', -1)) != pgid:
        return False
    table = subprocess.run(['ps', '-A', '-o', 'pid=', '-o', 'pgid='], stdout=subprocess.PIPE, env=dict(ENV, LC_ALL='C'))
    members: List[int] = [int(a) for a, b in (row.split() for row in table.stdout.decode().splitlines() if len(row.split()) == 2)
                          if int(b) == pgid]
    if pgid in members:
        start = subprocess.run(['ps', '-o', 'lstart=', '-p', str(pgid)], stdout=subprocess.PIPE, env=dict(ENV, LC_ALL='C'))
        if meta.get('leader_start') and start.stdout.decode().strip() == meta['leader_start']:
            return True
    token: str = 'TEST_WATCH_RUN=' + str(meta.get('marker'))
    for pid in members:
        shown = subprocess.run(['ps', '-E', '-ww', '-o', 'command=', '-p', str(pid)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if token in shown.stdout.decode('utf-8', 'replace').split():
            return True
    return False


def sweep() -> List[str]:
    """남은 것 거두기 — 이 픽스처가 띄운 프로세스 · 도구가 찍은 묶음(내 묶음일 때만). 거둔 것을 돌려준다."""
    swept: List[str] = []
    for proc in PROCS:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
            swept.append('pid %d' % proc.pid)
    for pgid, folder in GROUPS:
        if alive(pgid) and _ours(pgid, folder):
            try:
                os.killpg(pgid, signal.SIGKILL)
                swept.append('PGID %d' % pgid)
            except OSError:
                pass
    return swept


def main() -> int:
    argv: List[str] = sys.argv[1:]
    tool_path: Path = TEST.parent / 'test_watch.py'
    if '--tool' in argv:
        at: int = argv.index('--tool')
        tool_path = Path(argv[at + 1]).resolve()
        argv = argv[:at] + argv[at + 2:]
    only: set = set(argv)
    top: Path = Path(tempfile.mkdtemp(prefix='test-watch-fx-'))
    try:
        for bundle in BUNDLES:
            name: str = bundle.__name__[len('bundle_'):]
            if only and name not in only:
                continue
            tmp: Path = top / name
            tmp.mkdir()
            try:
                bundle(tmp, tool_path)
            except Exception as error:  # noqa: BLE001 — 묶음 하나의 준비 · 실행 오류는 FAIL 로 세고 다음 묶음으로
                check(name + ' 준비 · 실행 오류', False, '%s: %s' % (type(error).__name__, error))
    finally:
        left: List[str] = sweep()
        shutil.rmtree(str(top), ignore_errors=True)
    check('끝 — 거둘 것이 남지 않음(멈춤 의심 뒤 묶음은 각 시험이 stop 으로 끔)', not left, left)
    print('test_watch 픽스처(%s): PASS %d / FAIL %d' % (tool_path, PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
