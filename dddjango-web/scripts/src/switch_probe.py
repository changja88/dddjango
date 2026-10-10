# dddjango-web 시험 전환 확인(`refactor_audit.py switch-check`)이 대상 프로젝트의 pytest 에 싣는 기록 플러그인.
#
# 도구가 이 파일을 빈 임시 폴더에 `dddjango_web_switch_probe.py` 로 복사해 PYTHONPATH 맨 앞에 두고
# `-p dddjango_web_switch_probe` 로 싣는다(그 폴더에는 이 모듈 하나뿐 — 대상 프로젝트의 모듈 이름을 가리지 않는다).
# 환경 변수 DDDJANGO_WEB_SWITCH_PROBE 가 가리키는 파일에 JSON 한 줄씩 덧붙인다 — 수집된 노드 · 수집 오류 ·
# 단계(setup · call · teardown)별 결과와 xfail 표지 · 예외(형 · 원시 traceback 프레임의 파일 · 줄 · 함수 이름) · 세션 끝.
# 판정은 하지 않는다(도구가 한다). 도구 밖에서 이 파일을 import 하지 않는다.
import json
import os

import pytest

_OUT = os.environ.get('DDDJANGO_WEB_SWITCH_PROBE', '')
_EXC = {}


def _write(record):
    if _OUT:
        with open(_OUT, 'a', encoding='utf-8') as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')


def pytest_collection_finish(session):
    _write({'event': 'collected', 'nodeids': [item.nodeid for item in session.items]})


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
