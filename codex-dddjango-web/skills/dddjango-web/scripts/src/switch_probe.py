# dddjango-web 시험 전환 확인(`refactor_audit.py switch-check`)이 대상 프로젝트의 pytest 에 싣는 기록 플러그인.
#
# 도구가 이 파일을 빈 임시 폴더에 `dddjango_web_switch_probe.py` 로 복사해 PYTHONPATH 맨 앞에 두고
# `-p dddjango_web_switch_probe` 로 싣는다(그 폴더에는 이 모듈 하나뿐 — 대상 프로젝트의 모듈 이름을 가리지 않는다).
# 환경 변수 DDDJANGO_WEB_SWITCH_PROBE 가 가리키는 파일에 JSON 한 줄씩 덧붙인다 — 수집된 노드 · 수집 오류 ·
# 단계(setup · call · teardown)별 결과와 xfail 표지 · 예외(형 · 원시 traceback 프레임의 파일 · 줄 · 함수 이름) · 세션 끝.
# 수집 기록은 셋이다: 끝까지 남아 도는 노드(`nodeids`) · 걸러지기 전에 수집된 항목(`items` — [노드, 그 파일의 실제 경로]) ·
# 걸러졌다고 알려진 항목(`deselected`). 걸러지기 전 목록은 항목이 만들어질 때마다(pytest_itemcollected) 적고, 수집 훅
# 가운데 가장 먼저 도는 자리에서 한 번 더 적는다 — `-k` · `-m` · `--deselect` · addopts · conftest 의 수집 훅이 뺀 case 를
# 도구가 알아야 하기 때문이다(tryfirst 훅끼리는 늦게 등록된 conftest 가 먼저 돌 수 있어 앞의 것이 바탕이다).
# 판정은 하지 않는다(도구가 한다). 도구 밖에서 이 파일을 import 하지 않는다.
import json
import os

import pytest

_OUT = os.environ.get('DDDJANGO_WEB_SWITCH_PROBE', '')
_EXC = {}
_SEEN = []
_GONE = []


def _write(record):
    if _OUT:
        with open(_OUT, 'a', encoding='utf-8') as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')


def _entry(item):
    path = getattr(item, 'path', None) or getattr(item, 'fspath', None)
    return [item.nodeid, os.path.realpath(str(path)) if path else '']


def _unique(entries):
    seen, out = set(), []
    for entry in entries:
        if entry[0] not in seen:
            seen.add(entry[0])
            out.append(entry)
    return out


def pytest_itemcollected(item):
    _SEEN.append(_entry(item))


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    _SEEN.extend(_entry(item) for item in items)


def pytest_deselected(items):
    _GONE.extend(_entry(item) for item in items)


def pytest_collection_finish(session):
    _write({'event': 'collected', 'nodeids': [item.nodeid for item in session.items], 'items': _unique(_SEEN),
            'deselected': _unique(_GONE)})


def pytest_collectreport(report):
    if report.failed:
        _write({'event': 'collect_error', 'nodeid': report.nodeid, 'text': str(report.longrepr)[-4000:]})


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    """보고를 만들기 전에 예외의 형과 원시 프레임만 적어 둔다 — None 을 돌려 보고는 pytest 가 만든다."""
    if call.excinfo is None:
        return None
    frames = []
    tb = call.excinfo.tb
    while tb is not None:
        code = tb.tb_frame.f_code
        frames.append([code.co_filename, tb.tb_lineno, code.co_name])
        tb = tb.tb_next
    kind = call.excinfo.type
    _EXC[(item.nodeid, call.when)] = {'type': '%s.%s' % (kind.__module__, kind.__qualname__), 'frames': frames}
    return None


def pytest_runtest_logreport(report):
    _write({'event': 'report', 'nodeid': report.nodeid, 'when': report.when, 'outcome': report.outcome,
            'wasxfail': hasattr(report, 'wasxfail'), 'exc': _EXC.pop((report.nodeid, report.when), None)})


def pytest_sessionfinish(session, exitstatus):
    _write({'event': 'finish', 'exitstatus': int(exitstatus)})
