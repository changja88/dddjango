"""멈춘 시험 깨우기 탐침 — `test_watch.py run` 이 `PYTEST_PLUGINS` 로 싣는 pytest 플러그인(스레드 없음 · 판정 없음).

시험마다 `TEST_WATCH_NOTES` 파일에 `start <시각> <pid> <nodeid>` 와 `end <시각> <pid> <nodeid>` 를 한 줄씩 덧붙이기(O_APPEND)만 한다.
오래 도는 시험은 도구가 이 줄들로 계산한다. 시험을 실패시키지 않고 출력도 늘리지 않는다 — 쓰기 실패는 버린다.
변수가 없으면 아무것도 하지 않는다. 대상 프로젝트의 pytest 안에서 돌므로 표준 라이브러리와 pytest 만 쓴다.
"""
import os
import time

import pytest

_NOTES: str = os.environ.get('TEST_WATCH_NOTES', '')


def _note(kind: str, nodeid: str) -> None:
    line: str = '%s %.3f %d %s\n' % (kind, time.time(), os.getpid(), nodeid.replace('\n', '\\n'))
    try:
        fd: int = os.open(_NOTES, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    except OSError:
        return
    try:
        os.write(fd, line.encode('utf-8', 'replace'))
    except OSError:
        pass
    finally:
        os.close(fd)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):  # type: ignore[no-untyped-def]
    if not _NOTES:
        yield
        return
    _note('start', item.nodeid)
    try:
        yield
    finally:
        _note('end', item.nodeid)
