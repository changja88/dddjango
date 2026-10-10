"""IM27 리터럴 절반 — 들어온 요청의 경로를 비교하는 글자 예외 픽스처(임시 git 저장소만 만들고 끝나면 지운다).

묶음: C 꼴(빠질 것 · 그대로 설 것 · 다른 IM 과 함께) · R 재현(오류 처리기 두 줄만 빠지고 VM 셋 그대로) · D 빚 스캔(같은 판정) ·
U 무변(고치기 전 판 scripts 와 같은 입력의 출력 byte 대조 · 위 꼴이 든 프로젝트는 그 자리의 IM27 만 빠진다).
꼴 파일은 줄 끝 주석 `# IM27` 로 «이 줄에 IM27 한 건이 선다» 를 적는다(두 건이면 `# IM27 IM27`) — 표지 없는 줄은 0 건이다.
고치기 전 판 = BASELINE 커밋의 scripts(`git show <커밋>:<경로>` 로 임시 폴더에 푼다 — 작업 사본을 stash 하지 않는다).
그 커밋이 이력에 없으면(얕은 clone 등) U 묶음을 건너뛰고 건너뛴 사실을 출력한다(실패로 세지 않는다)."""
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

TEST = Path(__file__).resolve().parent
SCRIPTS = TEST.parent
REPO = SCRIPTS.parents[1]
BASELINE = 'f349f878'  # 고치기 전 판(배포된 dddjango-web 2.3.0)
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
HANDLER = 'root/handler/'
CHART = 'application/chart/'
VM = CHART + 'application_layer/view_model/chart_view_model.py'
SERVICE = CHART + 'application_layer/service/chart_path_service.py'
TEMPLATE = CHART + 'presentation_layer/view/chart_view.html'
ERROR_HANDLER = HANDLER + 'root_error_handler.py'
LITERAL = 'DataSource 밖 API URL 리터럴 `/api/…`'
PASS = FAIL = 0


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok and detail:
        print('    ' + str(detail).replace('\n', '\n    ')[:2400])


def git(root, *args):
    r = subprocess.run(['git', '-C', str(root), '-c', 'user.name=t', '-c', 'user.email=t@t', *args],
                       capture_output=True, text=True, env=ENV)
    if r.returncode:
        raise RuntimeError('git %s — %s' % (' '.join(args[:2]), r.stderr))
    return r.stdout.strip()


def backstop(root, *args, scripts=SCRIPTS):
    r = subprocess.run([sys.executable, '-B', str(scripts / 'backstop.py'), str(root), *map(str, args)],
                       capture_output=True, text=True, env=ENV)
    return r.returncode, r.stdout + r.stderr


def lines_of(out, cid, path):
    """`[ID] BLOCKER — web/<path>:<행>` 의 행 목록(같은 행 두 건이면 두 번)."""
    return sorted(int(n) for n in re.findall(r'^\[%s\] BLOCKER — web/%s:(\d+)$' % (cid, re.escape(path)), out, re.M))


def im27(out, path):
    return lines_of(out, 'IM27', path)


def message_of(out, cid, path, line):
    m = re.search(r'^\[%s\] BLOCKER — web/%s:%d\n  위반: (.+)$' % (cid, re.escape(path), line), out, re.M)
    return m.group(1) if m else ''


def marked(lines):
    """줄 끝 표지(`# IM27` · `# IM27 IM27`)가 적은 행 목록(건수만큼)."""
    out = []
    for i, line in enumerate(lines, 1):
        m = re.search(r'#\s*((?:IM27\s*)+)$', line)
        out += [i] * (len(re.findall('IM27', m.group(1))) if m else 0)
    return out


class Proj:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def w(self, rel, *lines):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    def markers(self):
        web = self.root / 'web'
        for cur, _dirs, _files in os.walk(web):
            rel = os.path.relpath(cur, web).replace(os.sep, '/')
            if rel.split('/')[0] not in ('design_system', 'static'):
                (Path(cur) / '__init__.py').touch()
        for cur, dirs, files in os.walk(web):
            if not dirs and not files:
                (Path(cur) / '.gitkeep').touch()

    def commit(self, message='c'):
        git(self.root, 'add', '-A')
        git(self.root, 'commit', '-qm', message)
        return git(self.root, 'rev-parse', 'HEAD')


def mkproj(root):
    """작은 표준 web/ 트리(chart BC 골격 · 허용 자리의 API 주소 둘) · git 초기화 + 바탕 커밋 → (Proj, BASE)."""
    p = Proj(root)
    w = p.w
    w('config/settings.py', "SECRET_KEY = 'x'")
    w('manage.py', '# manage')
    w('web/__init__.py', '')
    w('web/apps.py', 'from django.apps import AppConfig', '', '', 'class WebConfig(AppConfig):', '    name: str = "web"')
    w('web/urls.py', 'from web.root.router.root_router import urlpatterns', '', '__all__: list[str] = ["urlpatterns"]')
    w('web/root/ruff.toml', '[lint]', 'select = ["ANN"]')
    w('web/root/router/root_router.py', 'urlpatterns: list[object] = []')
    w('web/root/scaffold/view/root_view.html', '<!doctype html>', '<html><body>{% block content %}{% endblock %}</body></html>')
    w('web/common/network/api_client.py', 'from django.test import Client', '', 'API_ROOT: str = "/api/"', '', '',
      'class ApiClient:', '    def get(self, path: str) -> object:', '        return Client().get(path)')
    base = 'web/' + CHART
    for layer, kinds in (('application_layer', ('use_case', 'view_model', 'state', 'shared_state', 'service')),
                         ('infra_layer', ('data_source', 'repository', 'service')),
                         ('presentation_layer', ('view', 'section', 'widget', 'ui_extension')),
                         ('domain_layer/chart', ('entity', 'value_object', 'enum', 'domain_service', 'specification'))):
        for k in kinds:
            (p.root / base / layer / k).mkdir(parents=True, exist_ok=True)
    w(base + 'ruff.toml', '[lint]', 'select = ["ANN"]')
    w(base + 'domain_layer/chart/chart.py', 'from dataclasses import dataclass', '', '',
      '@dataclass(frozen=True, slots=True, kw_only=True)', 'class Chart:', '    key: str')
    w(base + 'infra_layer/data_source/chart_data_source.py', 'CHART_PATH: str = "/api/v1/charts"')
    w('.dddjango-web/backstop-baseline.json', '{"cycle_pairs": []}')
    p.markers()
    git(p.root, 'init', '-q', '-b', 'main')
    return p, p.commit('base')


# ---------------------------------------------------------------- 꼴 — 빠지는 글자가 든 파일(표지 줄만 남는다)

CHANGED = {
    # a) 요청 경로를 바로 startswith
    HANDLER + 'case_a.py': [
        'def handle(request: object) -> int:',
        '    if request.path.startswith("/api/"):',
        '        return 1',
        '    return 0'],
    # b) 한 번 P 로만 바인딩된 지역 이름(주석 달린 대입 · 그냥 대입) — 재현 꼴 그대로 · != · endswith
    HANDLER + 'case_b.py': [
        'def handle(request: object) -> int:',
        '    path: str = request.path',
        '    if path == "/api" or path.startswith("/api/") or path == "/admin" or path.startswith("/admin/"):',
        '        return 1',
        '    return 0',
        '',
        '',
        'def handle_info(request: object) -> bool:',
        '    path = request.path_info',
        '    return path != "/api/x" and path.endswith("/api/")'],
    # c) in · not in — 튜플 · 리스트 · 집합 리터럴의 원소
    HANDLER + 'case_c.py': [
        'def handle(request: object) -> bool:',
        '    a: bool = request.path_info in ("/api", "/api/")',
        '    b: bool = request.path not in ["/api/a", "/api/b"]',
        '    c: bool = request.path in {"/api/c"}',
        '    return a and b and c'],
    # d) get_full_path() · get_full_path_info() — startswith 튜플 · endswith
    HANDLER + 'case_d.py': [
        'def handle(request: object) -> int:',
        '    if request.get_full_path().startswith(("/api/", "/admin/")):',
        '        return 1',
        '    return int(request.get_full_path_info().endswith("/api/"))'],
    # e) 글자가 왼쪽 · META 의 PATH_INFO
    HANDLER + 'case_e.py': [
        'def handle(request: object) -> bool:',
        '    a: bool = "/api/" != request.path',
        '    b: bool = "/api/x" == request.META["PATH_INFO"]',
        '    c: bool = request.META.get("PATH_INFO") == "/api/y"',
        '    return a and b and c'],
    # 미들웨어의 __call__(self, request) — path_info · 여러 줄 호출 · lambda 인자
    HANDLER + 'case_middleware.py': [
        'class ApiPathMiddleware:',
        '    def __init__(self, get_response: object) -> None:',
        '        self.get_response = get_response',
        '',
        '    def __call__(self, request: object) -> object:',
        '        if request.path_info.startswith("/api/"):',
        '            return self.get_response(request)',
        '        if request.path.startswith(',
        '            "/api/",',
        '        ):',
        '            return None',
        '        return self.get_response(request)',
        '',
        '',
        'IS_API = lambda request: request.path.startswith("/api/")  # noqa: E731'],
    # 여러 줄 비교 — 글자가 제 줄에 따로 있다
    HANDLER + 'case_multiline.py': [
        'def handle(request: object) -> bool:',
        '    return (',
        '        request.path',
        '        == "/api/x"',
        '    ) or request.path in (',
        '        "/api/a",',
        '        "/api/b",',
        '    )'],
    # k) 같은 줄 — 비교 글자는 빠지고 호출 글자는 선다 · 앞에 한글 이름이 있는 줄 · 같은 값을 비교와 호출에 쓴 꼴
    HANDLER + 'case_k.py': [
        'def handle(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x": api_client.get("/api/y")  # IM27',
        '    request.path.startswith("/api/") and api_client.get("/api/z")  # IM27',
        '    이름: str = "가나다"; ok: bool = 이름 == "/api/q" or request.path.startswith("/api/")  # IM27',
        '    if request.path == "/api/same": api_client.get("/api/same")  # IM27',
        '    if request.path == "/api/next":',
        '        api_client.get("/api/next")  # IM27'],
    # 안쪽 범위의 가림은 바깥 판정에 섞이지 않는다 — comprehension 대상 · 안쪽 함수의 인자와 지역 이름 · lambda 인자
    HANDLER + 'case_shadow.py': [
        'def handle(request: object) -> bool:',
        '    path: str = request.path',
        '    names: list[str] = [path for path in ("a", "b")]',
        '',
        '    def inner(path: str) -> str:',
        '        return path',
        '',
        '    def local() -> str:',
        '        path = "x"',
        '        return path',
        '',
        '    echo = lambda request: request  # noqa: E731',
        '    return path == "/api/x" and bool(names) and inner("a") == local() and echo(1) == 1'],
    # 다른 IM 과 함께 — IM27 import 절반(HTTP 표면)은 그대로 선다
    HANDLER + 'case_httpx.py': [
        'import httpx  # IM27',
        '',
        '',
        'def handle(request: object) -> object:',
        '    if request.path.startswith("/api/"):',
        '        return None',
        '    return httpx'],
    # 다른 IM 과 함께 — application_layer 의 요청 객체 토큰(IM12)은 그대로 선다
    SERVICE: [
        'def is_api(request: object) -> bool:',
        '    return request.META["PATH_INFO"] == "/api/x"'],
    # 옛 배치 파일(표준 트리 밖)도 같은 꼴이면 빠진다
    'legacy/middleware.py': [
        'def skip(request: object) -> bool:',
        '    return request.path.startswith("/api/")'],
    # 오류 처리기의 실제 꼴 — 경로를 먼저 로그에 넘기고 지역 이름으로 비교한다(comprehension 은 request 의 다른 속성만 읽는다)
    ERROR_HANDLER: [
        'import logging',
        '',
        'from django.conf import settings',
        'from django.views.defaults import page_not_found',
        '',
        '',
        'def handler404(request: object, exception: Exception) -> object:',
        '    logging.getLogger(__name__).warning("Web page not found: %s", request.path)',
        '    path: str = request.path',
        '    if path == "/api" or path.startswith("/api/") or path == "/admin" or path.startswith("/admin/"):',
        '        return page_not_found(request, exception)',
        '    context = REQUEST_CONTEXT.get()',
        '    if context is not None:',
        '        return fallback_view(request)',
        '    cookies: dict[str, str] = {',
        '        name: request.COOKIES[name]',
        '        for name in (settings.SESSION_COOKIE_NAME, settings.CSRF_COOKIE_NAME)',
        '        if name in request.COOKIES',
        '    }',
        '    return page_not_found(request, exception) if cookies else None'],
    # logging 출처의 로그 문장 인자로 읽는 것은 다시 쓰는 것으로 세지 않는다 — 비교 갈래 안 로그 · P 와 지역 이름 각각의 위치 인자 ·
    #    키워드 값 · f-문자열 · 리터럴 `%` · extra 사전 · 모듈 수준 logger · 함수 안 logger 한 번 · log(level, …).
    #    로그 인자 안의 `/api/` 글자는 그대로 선다(같은 글자가 비교에도 있으면 비교 자리만 빠진다)
    HANDLER + 'case_log.py': [
        'import logging',
        '',
        'logger = logging.getLogger(__name__)',
        '',
        '',
        'def in_branch(request: object) -> None:',
        '    if request.path.startswith("/api/"):',
        '        logger.info("api %s", request.path)',
        '',
        '',
        'def positional(request: object) -> bool:',
        '    logging.warning("not found: %s", request.path)',
        '    logging.getLogger("web").error("not found: %s", request.path)',
        '    return request.path == "/api/x"',
        '',
        '',
        'def keyword_value(request: object) -> bool:',
        '    logger.info(msg=request.path)',
        '    return request.path == "/api/x"',
        '',
        '',
        'def formatted(request: object) -> bool:',
        '    logger.warning(f"not found: {request.path}")',
        '    return request.path == "/api/x"',
        '',
        '',
        'def percent(request: object, a: str) -> bool:',
        '    logger.error("x %s" % request.path)',
        '    logger.error("x %s %s" % (a, request.path))',
        '    return request.path != "/api/x"',
        '',
        '',
        'def extra(request: object) -> bool:',
        '    logger.info("request", extra={"path": request.path})',
        '    return request.path in ("/api/a", "/api/b")',
        '',
        '',
        'def alias_forms(request: object, a: str) -> bool:',
        '    path = request.path',
        '    logger.debug("p=%s", path)',
        '    logger.debug(msg=path)',
        '    logger.debug(f"p={path}")',
        '    logger.debug("p=%s" % path)',
        '    logger.debug("p=%s %s" % (a, path))',
        '    logger.debug("p", extra={"path": path})',
        '    return path.startswith("/api/")',
        '',
        '',
        'def local_logger(request: object) -> bool:',
        '    log = logging.getLogger("x")',
        '    log.critical("p=%s", request.path)',
        '    return request.path.endswith("/api/")',
        '',
        '',
        'def level(request: object) -> bool:',
        '    logger.log(logging.WARNING, "%s", request.path)',
        '    logger.exception("p=%s", request.path)',
        '    return request.path != "/api/x"',
        '',
        '',
        'def same_literal(request: object) -> bool:',
        '    logger.info("/api/ %s", request.path)  # IM27',
        '    return request.path.startswith("/api/")'],
    # logging 출처의 다른 꼴 — `import logging as X` · `from logging import getLogger as Y` · 그 Y 로 만든 모듈 수준 이름
    HANDLER + 'case_log_from.py': [
        'import logging as lg',
        'from logging import getLogger as get_logger',
        '',
        'log = get_logger(__name__)',
        '',
        '',
        'def direct(request: object) -> bool:',
        '    get_logger(__name__).warning("p=%s", request.path)',
        '    return request.path == "/api/x"',
        '',
        '',
        'def named(request: object) -> bool:',
        '    log.info("p=%s", request.path)',
        '    return request.path == "/api/x"',
        '',
        '',
        'def module_alias(request: object) -> bool:',
        '    lg.info("p=%s", request.path)',
        '    lg.getLogger("web").info("p=%s", request.path)',
        '    return request.path == "/api/x"'],
}

# ---------------------------------------------------------------- 꼴 — 고치기 전과 판정이 같은 파일(`/api/` 글자 전부 그대로)

SAME = {
    # f · g · h) VM 의 호출 주소 · f-문자열 주소 · DataSource 밖 상수 — 재현 꼴 그대로
    VM: [
        'CHART_URL: str = "/api/v1/charts"  # IM27',
        '',
        '',
        'class ChartViewModel:',
        '    def load(self, api_client: object, chart_id: int) -> str:',
        '        api_client.get("/api/v1/charts/me")  # IM27',
        '        url: str = f"/api/v1/charts/{chart_id}"  # IM27',
        '        return url'],
    # i) 지역 이름의 바인딩 경계 — 재대입 · P 두 번 · 인자 · for · with as · except as · walrus · del · global · nonlocal
    HANDLER + 'case_i.py': [
        'def reassigned(request: object) -> bool:',
        '    path: str = request.path',
        '    path = "/api/x"  # IM27',
        '    return path == "/api/y"  # IM27',
        '',
        '',
        'def twice(request: object) -> bool:',
        '    path = request.path',
        '    path = request.path_info',
        '    return path.startswith("/api/")  # IM27',
        '',
        '',
        'def param(request: object, path: str) -> bool:',
        '    return path == "/api/"  # IM27',
        '',
        '',
        'def looped(request: object) -> bool:',
        '    path = request.path',
        '    for path in ("a",):',
        '        pass',
        '    return path == "/api/"  # IM27',
        '',
        '',
        'def managed(request: object, lock: object) -> bool:',
        '    path = request.path',
        '    with lock as path:',
        '        pass',
        '    return path == "/api/"  # IM27',
        '',
        '',
        'def caught(request: object) -> bool:',
        '    path = request.path',
        '    try:',
        '        pass',
        '    except ValueError as path:',
        '        pass',
        '    return path == "/api/"  # IM27',
        '',
        '',
        'def walrus(request: object) -> bool:',
        '    path = request.path',
        '    if (path := "a"):',
        '        pass',
        '    return path == "/api/"  # IM27',
        '',
        '',
        'def deleted(request: object) -> bool:',
        '    path = request.path',
        '    del path',
        '    return path == "/api/"  # IM27',
        '',
        '',
        'PATH: str = ""',
        '',
        '',
        'def global_alias(request: object) -> bool:',
        '    global PATH',
        '    PATH = request.path',
        '    return PATH == "/api/"  # IM27',
        '',
        '',
        'def nonlocal_alias(request: object) -> object:',
        '    path: str = ""',
        '',
        '    def inner() -> bool:',
        '        nonlocal path',
        '        path = request.path',
        '        return path == "/api/"  # IM27',
        '    return inner',
        '',
        '',
        'def nonlocal_rebind(request: object) -> bool:',
        '    path = request.path',
        '',
        '    def swap() -> None:',
        '        nonlocal path',
        '        path = "b"',
        '    swap()',
        '    return path == "/api/"  # IM27',
        '',
        '',
        'def two_targets(request: object) -> bool:',
        '    path = other = request.path',
        '    return path == "/api/" and bool(other)  # IM27'],
    # j) request 의 경계 — 다른 이름 · self.request · 모듈 수준 · 재대입 · for · with as · except as · walrus · del · *request ·
    #    바깥 함수의 request 를 쓰는 안쪽 함수
    HANDLER + 'case_j.py': [
        'def other(obj: object) -> bool:',
        '    return obj.path.startswith("/api/")  # IM27',
        '',
        '',
        'def short(req: object) -> bool:',
        '    return req.path == "/api/"  # IM27',
        '',
        '',
        'class ChartView:',
        '    def get(self) -> bool:',
        '        return self.request.path.startswith("/api/")  # IM27',
        '',
        '',
        'request = object()',
        'AT_IMPORT: bool = request.path == "/api/"  # IM27',
        '',
        '',
        'def rebound(request: object, backend: object, api_client: object) -> None:',
        '    request = backend',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.path)',
        '',
        '',
        'def looped(request: object) -> bool:',
        '    for request in (object(),):',
        '        pass',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def managed(request: object, lock: object) -> bool:',
        '    with lock as request:',
        '        pass',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def caught(request: object) -> bool:',
        '    try:',
        '        pass',
        '    except ValueError as request:',
        '        pass',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def walrus(request: object) -> bool:',
        '    if (request := object()):',
        '        pass',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def deleted(request: object) -> bool:',
        '    del request',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def starred(*request: object) -> bool:',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def outer(request: object) -> object:',
        '    def inner() -> bool:',
        '        return request.path.startswith("/api/")  # IM27',
        '    return inner'],
    # 비교 밖에서 경로 값을 다시 쓰는 함수 — 그 함수의 비교 글자는 빠지지 않는다
    HANDLER + 'case_reuse.py': [
        'def passed(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.path)',
        '',
        '',
        'def chosen(request: object, api_client: object) -> None:',
        '    chart_url = request.path if request.path == "/api/v1/charts" else None  # IM27',
        '    if chart_url:',
        '        api_client.get(chart_url)',
        '',
        '',
        'def returned(request: object) -> str:',
        '    if request.path.startswith("/api/"):  # IM27',
        '        return request.path',
        '    return ""',
        '',
        '',
        'def alias_passed(request: object, api_client: object) -> None:',
        '    path = request.path',
        '    if path == "/api/x":  # IM27',
        '        api_client.get(path)',
        '',
        '',
        'def alias_copied(request: object) -> str:',
        '    path = request.path',
        '    target = path',
        '    return target if path == "/api/x" else ""  # IM27',
        '',
        '',
        'def closure(request: object, api_client: object) -> object:',
        '    path = request.path',
        '',
        '    def fetch() -> object:',
        '        return api_client.get(path)',
        '    return fetch() if path == "/api/x" else None  # IM27',
        '',
        '',
        'def defaulted(request: object, api_client: object) -> object:',
        '    path = request.path',
        '',
        '    def fetch(url: str = path) -> object:',
        '        return api_client.get(url)',
        '    return fetch() if path == "/api/x" else None  # IM27',
        '',
        '',
        'def comprehended(request: object, api_client: object) -> list[object]:',
        '    if request.path == "/api/x":  # IM27',
        '        return [api_client.get(request.path) for _ in range(1)]',
        '    return []',
        '',
        '',
        'def lambda_read(request: object, api_client: object) -> object:',
        '    fetch = lambda: api_client.get(request.path)  # noqa: E731',
        '    return fetch() if request.path == "/api/x" else None  # IM27',
        '',
        '',
        'def lowered(request: object) -> bool:',
        '    return request.path == "/api/x" and request.path.lower() == "y"  # IM27',
        '',
        '',
        'def assigned(request: object) -> bool:',
        '    request.path = "/api/x"  # IM27',
        '    return request.path == "/api/y"  # IM27'],
    # 계약 밖 비교 꼴 — 부분 문자열 · f-문자열 · 이어 붙인 글자 · 연쇄 비교 · 인접 문자열 결합 · walrus 로 담은 컨테이너 ·
    #    변수 컨테이너 · 정규식 · 인자가 있는 경로 메서드 · startswith 의 둘째 인자
    HANDLER + 'case_shape.py': [
        'import re',
        '',
        '',
        'def substring(request: object) -> bool:',
        '    return "/api/" in request.path  # IM27',
        '',
        '',
        'def formatted(request: object, x: str) -> bool:',
        '    return request.path == f"/api/{x}"  # IM27',
        '',
        '',
        'def joined(request: object, x: str) -> bool:',
        '    return request.path == x + "/api/"  # IM27',
        '',
        '',
        'def chained(request: object, x: str) -> bool:',
        '    return x == request.path == "/api/x"  # IM27',
        '',
        '',
        'def chained_first(request: object, x: str) -> bool:',
        '    return request.path == "/api/y" == x  # IM27',
        '',
        '',
        'def adjacent(request: object) -> bool:',
        '    return request.path == "/api/" "x"  # IM27',
        '',
        '',
        'def adjacent_lines(request: object) -> bool:',
        '    return request.path in (',
        '        "/api/a"  # IM27',
        '        "/api/b",  # IM27',
        '    )',
        '',
        '',
        'def kept(request: object, api_client: object) -> object:',
        '    if request.path in (urls := ("/api/x", "/api/y")):  # IM27 IM27',
        '        return api_client.get(urls[0])',
        '    return None',
        '',
        '',
        'def kept_prefix(request: object) -> bool:',
        '    return request.path.startswith((prefixes := ("/api/",)))  # IM27',
        '',
        '',
        'def variable(request: object) -> bool:',
        '    urls: tuple[str, ...] = ("/api/a", "/api/b")  # IM27 IM27',
        '    return request.path in urls',
        '',
        '',
        'def searched(request: object) -> bool:',
        '    return re.search("/api/", request.path) is not None  # IM27',
        '',
        '',
        'def with_args(request: object) -> bool:',
        '    return request.get_full_path(True).startswith("/api/")  # IM27',
        '',
        '',
        'def with_default(request: object) -> bool:',
        '    return request.META.get("PATH_INFO", "") == "/api/"  # IM27',
        '',
        '',
        'def sliced(request: object) -> bool:',
        '    return request.path.startswith("/api/", 0)  # IM27'],
    # 로그 예외의 경계 — 하나라도 어기면 그 함수의 비교 글자는 빠지지 않는다: 로그가 아닌 호출(비교 앞 · 뒤) · logging 출처로
    #    확인되지 않는 받는 쪽(다시 붙인 메서드 · 다른 객체 · self.logger · 인자 · 가림 · 재바인딩 · 함수 안 import · 바깥 함수의 이름) ·
    #    독립 문장이 아닌 로그 호출(반환 · 대입 · 바깥 호출의 인자 · 첨자) · log 의 level 자리 · 로그 호출까지 가는 길의 다른 노드 ·
    #    다른 연산 · 받는 쪽에서 읽기 · 간접 호출 · 응답과 이동 호출(과보고로 남는 알려진 한계)
    HANDLER + 'case_log_keep.py': [
        'import logging',
        '',
        'logger = logging.getLogger(__name__)',
        '',
        '',
        'def call_before(request: object, client: object) -> bool:',
        '    client.get(request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def call_after(request: object, client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        client.get(request.path)',
        '',
        '',
        'def rebound_method(request: object, client: object) -> None:',
        '    client.log = client.get',
        '    if request.path.startswith("/api/"):  # IM27',
        '        client.log(request.path)',
        '',
        '',
        'def foreign_warning(request: object, messages: object) -> bool:',
        '    messages.warning(request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'class Handler:',
        '    def handle(self, request: object) -> bool:',
        '        self.logger.info("p=%s", request.path)',
        '        return request.path == "/api/x"  # IM27',
        '',
        '',
        'def logger_param(request: object, logger: object) -> bool:',
        '    logger.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def logging_param(request: object, logging: object) -> bool:',
        '    logging.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def logging_param_get_logger(request: object, logging: object) -> bool:',
        '    logging.getLogger("x").info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def local_from_param(request: object, logging: object) -> bool:',
        '    log = logging.getLogger("x")',
        '    log.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def logger_rebound(request: object, client: object) -> bool:',
        '    logger = client',
        '    logger.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def local_twice(request: object, client: object) -> bool:',
        '    log = logging.getLogger("x")',
        '    log = client',
        '    log.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def local_foreign(request: object, client: object) -> bool:',
        '    log = client.getLogger("x")',
        '    log.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def local_import(request: object) -> bool:',
        '    import logging',
        '    logging.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def local_import_get_logger(request: object) -> bool:',
        '    import logging',
        '    logging.getLogger("x").info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def local_nonlocal(request: object, client: object) -> bool:',
        '    log = logging.getLogger("x")',
        '',
        '    def swap() -> None:',
        '        nonlocal log',
        '        log = client',
        '    swap()',
        '    log.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def outer_shadow(logger: object) -> object:',
        '    def view(request: object) -> bool:',
        '        logger.info("p=%s", request.path)',
        '        return request.path == "/api/x"  # IM27',
        '    return view',
        '',
        '',
        'def outer_shadow_module(logging: object) -> object:',
        '    def view(request: object) -> bool:',
        '        logging.getLogger("x").warning("p=%s", request.path)',
        '        return request.path == "/api/x"  # IM27',
        '    return view',
        '',
        '',
        'def returned(request: object) -> object:',
        '    if request.path == "/api/x":  # IM27',
        '        return logger.info("p=%s", request.path)',
        '    return None',
        '',
        '',
        'def assigned(request: object) -> bool:',
        '    done = logger.info("p=%s", request.path)',
        '    return bool(done) and request.path == "/api/x"  # IM27',
        '',
        '',
        'def passed_on(request: object, client: object) -> bool:',
        '    client.get(logger.info("p=%s", request.path))',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def subscripted(request: object) -> bool:',
        '    logger.info(request.path)[0]',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def level_position(request: object) -> bool:',
        '    logger.log(request.path, "x")',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def level_missing(request: object) -> bool:',
        '    logger.log(msg=request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def through_call(request: object, client: object) -> bool:',
        '    logger.info(client.get(request.path))',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def through_walrus(request: object) -> bool:',
        '    logger.info(x := request.path)',
        '    return request.path == "/api/x" and bool(x)  # IM27',
        '',
        '',
        'async def through_await(request: object) -> bool:',
        '    logger.info(await request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def through_yield(request: object) -> object:',
        '    logger.info((yield request.path))',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def through_starred(request: object) -> bool:',
        '    logger.info(*(request.path,))',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def through_conditional(request: object, quiet: bool) -> bool:',
        '    logger.info("" if quiet else request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def through_subscript(request: object) -> bool:',
        '    logger.info(request.path[1:])',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def through_attribute(request: object) -> bool:',
        '    logger.info(request.path.__class__)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def through_method(request: object) -> bool:',
        '    logger.info(request.path.lower())',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def through_list(request: object) -> bool:',
        '    logger.info([request.path])',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def through_lambda(request: object) -> bool:',
        '    logger.info(lambda: request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def through_comprehension(request: object) -> bool:',
        '    path = request.path',
        '    logger.info([path for _ in range(1)])',
        '    return path == "/api/x"  # IM27',
        '',
        '',
        'def inner_function(request: object) -> bool:',
        '    path = request.path',
        '',
        '    def note() -> None:',
        '        logger.info("p=%s", path)',
        '    note()',
        '    return path == "/api/x"  # IM27',
        '',
        '',
        'def matmul(request: object, sender: object) -> bool:',
        '    logger.info(request.path @ sender)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def concatenated(request: object) -> bool:',
        '    logger.info("a" + request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def percent_left(request: object, x: object) -> bool:',
        '    logger.info(request.path % x)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def percent_variable(request: object, template: str) -> bool:',
        '    logger.info(template % request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def receiver(request: object) -> bool:',
        '    request.path.info("x")',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def receiver_format(request: object) -> bool:',
        '    ("%s" % request.path).info("x")',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def receiver_argument(request: object) -> bool:',
        '    logging.getLogger(request.path).info("x")',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def indirect(request: object) -> bool:',
        '    getattr(logger, "info")(request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def plain_function(request: object) -> bool:',
        '    info(request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def json_response(request: object) -> object:',
        '    path = request.path',
        '    if path == "/api/x":  # IM27',
        '        return JsonResponse({"path": path})',
        '    return None',
        '',
        '',
        'def redirected(request: object) -> object:',
        '    if request.path == "/api/x":  # IM27',
        '        return redirect(request.path)',
        '    return None'],
    # 모듈 범위의 logging 출처가 확인되지 않는 파일 — logger 를 두 번 바인딩 · 어느 함수가 global 로 다시 씀 ·
    #    `logging` 이름을 다시 바인딩 · logging 에서 오지 않은 이름
    HANDLER + 'case_log_twice.py': [
        'import logging',
        '',
        'logger = logging.getLogger(__name__)',
        'logger = logging.getLogger("other")',
        '',
        '',
        'def view(request: object) -> bool:',
        '    logger.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27'],
    HANDLER + 'case_log_global.py': [
        'import logging',
        '',
        'logger = logging.getLogger(__name__)',
        '',
        '',
        'def swap(client: object) -> None:',
        '    global logger',
        '    logger = client',
        '',
        '',
        'def view(request: object) -> bool:',
        '    logger.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27'],
    HANDLER + 'case_log_module.py': [
        'import logging',
        'import logging.handlers as handlers',
        '',
        'logging = object()',
        'tracer = object()',
        'handler_logger = handlers.getLogger("x")',
        '',
        '',
        'def module_twice(request: object) -> bool:',
        '    logging.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def get_logger_unverified(request: object) -> bool:',
        '    logging.getLogger("x").info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def foreign(request: object) -> bool:',
        '    tracer.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def other_module(request: object) -> bool:',
        '    handlers.info("p=%s", request.path)',
        '    handler_logger.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27'],
    # 문법 오류 파일 — 판정하지 못하니 지금처럼 선다
    HANDLER + 'case_broken.py': [
        'def handle(request: object) -> bool:',
        '    if request.path.startswith("/api/")  # IM27',
        '        return True'],
    # 주석 · docstring — 주석 안 글자는 지금처럼 0 · docstring 안 따옴표 글자는 지금처럼 선다
    HANDLER + 'case_text.py': [
        'def handle(request: object) -> bool:',
        '    """요청 경로가 "/api/" 로 시작하는지 본다."""  # IM27',
        '    # 주석의 "/api/" 는 잡히지 않는다',
        '    return bool(request)'],
    # 옛 배치 파일의 호출 주소 · 옛 배치의 DataSource(허용 자리)
    'legacy/caller.py': [
        'def call(request: object, api_client: object) -> object:',
        '    return api_client.get("/api/legacy")  # IM27'],
    'legacy/chart_data_source.py': [
        'CHART_PATH: str = "/api/v1/legacy"'],
}
# l) 템플릿의 같은 꼴(이번엔 그대로)
TEMPLATE_LINES = ['{% if request.path == "/api/" %}<p>api</p>{% endif %}']
WANT = {rel: marked(lines) for rel, lines in {**CHANGED, **SAME}.items()}
WANT[TEMPLATE] = [1]


def write_cases(p, cases):
    for rel, lines in cases.items():
        p.w('web/' + rel, *lines)
    p.w('web/' + TEMPLATE, *TEMPLATE_LINES)


# ====================================================================== C — 꼴

def bundle_cases(tmp):
    p, base = mkproj(tmp / 'c')
    write_cases(p, {**CHANGED, **SAME})
    e, out = backstop(p.root, '--diff-base', base, '--only', 'im')
    for rel in CHANGED:
        check('C 빠짐 — %s IM27 행 %s' % (rel, WANT[rel]), im27(out, rel) == WANT[rel], im27(out, rel))
    for rel in list(SAME) + [TEMPLATE]:
        check('C 그대로 — %s IM27 행 %s' % (rel, WANT[rel]), im27(out, rel) == WANT[rel], im27(out, rel))
    check('C 그대로 선 글자의 사유 · 교정 문구 그대로(표준 자리)',
          '[IM27] BLOCKER — web/%s:6\n  위반: %s (제1 규약 §3.4)\n'
          '  교정: API path 는 그 BC infra_layer/data_source/<개념>_data_source.py 에만 둔다.\n' % (VM, LITERAL) in out, out[-1200:])
    check('C 그대로 선 글자의 교정 문구 그대로(옛 배치)',
          '[IM27] BLOCKER — web/legacy/caller.py:2\n  위반: %s (제1 규약 §3.4)\n'
          '  교정: 옛 배치 단위에서는 API path 를 <개념>_data_source.py 파일에만 둔다(표준 단위는 그 BC infra_layer/data_source/).\n'
          % LITERAL in out, out[-1200:])
    total = sum(len(v) for v in WANT.values())
    check('C 허용 자리(표준 · 옛 배치 DataSource · common/network)는 지금처럼 0 · 합계 %d건' % total,
          im27(out, CHART + 'infra_layer/data_source/chart_data_source.py') == []
          and im27(out, 'legacy/chart_data_source.py') == [] and im27(out, 'common/network/api_client.py') == []
          and len(re.findall(r'^\[IM27\] BLOCKER', out, re.M)) == total, out[-800:])
    check('C 다른 IM 과 함께 — IM27 import 절반(httpx)은 그대로 · 그 파일의 비교 글자만 빠진다',
          message_of(out, 'IM27', HANDLER + 'case_httpx.py', 1) == 'common/network 밖 HTTP 호출 표면 `httpx` import (제1 규약 §3.4·§6)',
          message_of(out, 'IM27', HANDLER + 'case_httpx.py', 1))
    check('C 다른 IM 과 함께 — application_layer 의 요청 객체 토큰(IM12)은 그대로 · 그 줄의 비교 글자만 빠진다',
          lines_of(out, 'IM12', SERVICE) == [2] and im27(out, SERVICE) == [], lines_of(out, 'IM12', SERVICE))
    # 게이트 — 바탕에 이미 있던 줄은 지금처럼 불발화(예외가 게이트를 바꾸지 않는다)
    head = p.commit('cases')
    lines = CHANGED[HANDLER + 'case_k.py'] + ['    api_client.get("/api/new")']
    p.w('web/' + HANDLER + 'case_k.py', *lines)
    e, out = backstop(p.root, '--diff-base', head, '--only', 'im')
    check('C 게이트 — 새 줄만(옛 줄은 불발화)', im27(out, HANDLER + 'case_k.py') == [len(lines)]
          and len(re.findall(r'^\[IM27\] BLOCKER', out, re.M)) == 1, out[-800:])


# ====================================================================== R — 재현(오류 처리기 · VM)

def bundle_repro(tmp):
    p = Proj(tmp / 'r')
    p.w('web/__init__.py', '')
    p.w('web/root/handler/root_error_handler.py',
        'from django.views.defaults import page_not_found', '', '',
        'def handler404(request, exception):',
        '    path: str = request.path',
        '    if path == "/api" or path.startswith("/api/") or path == "/admin" or path.startswith("/admin/"):',
        '        return page_not_found(request, exception)',
        '    if request.path.startswith("/api/"):',
        '        return page_not_found(request, exception)',
        '    return page_not_found(request, exception)')
    p.w('web/' + VM, 'CHART_URL: str = "/api/v1/charts"', '', '', 'class ChartViewModel:',
        '    def load(self, api_client, chart_id: int):', '        api_client.get("/api/v1/charts/me")',
        '        url: str = f"/api/v1/charts/{chart_id}"', '        return url')
    git(p.root, 'init', '-q', '-b', 'main')
    git(p.root, 'commit', '-q', '--allow-empty', '-m', 'base')
    git(p.root, 'add', 'web/root/handler/root_error_handler.py', 'web/' + VM)
    e, out = backstop(p.root, '--diff-base', 'HEAD', '--only', 'im')
    check('R 오류 처리기 :6 · :8 사라짐', im27(out, 'root/handler/root_error_handler.py') == [], out[-1500:])
    check('R VM :1 · :6 · :7 그대로 · exit 2 · blocker 3건', im27(out, VM) == [1, 6, 7] and e == 2
          and out.rstrip().endswith('blocker 3건'), 'exit=%d\n%s' % (e, out[-1500:]))


# ====================================================================== D — 빚 스캔

def bundle_debt(tmp):
    p, _base = mkproj(tmp / 'd')
    write_cases(p, {**CHANGED, **SAME})
    p.commit('cases')
    target = p.root / '.git' / 'debt.json'
    e, out = backstop(p.root, '--debt-scan', '--json', target)
    counts = json.loads(target.read_text(encoding='utf-8')).get('counts', {}) if target.exists() else {}
    got = {k.split('|', 1)[1]: n for k, n in counts.items() if k.startswith('IM27|')}
    want = {rel: len(v) for rel, v in WANT.items() if v}
    check('D 빚 스캔 IM27 키 · 건수 — 그대로 선 글자만(빠질 글자만 든 파일은 키 없음)', got == want,
          'exit=%d · 다른 것 %s' % (e, sorted(set(got.items()) ^ set(want.items()))))


# ====================================================================== U — 무변

def old_scripts(tmp):
    """BASELINE 커밋의 scripts(test/ 제외)와 매니페스트를 임시 폴더에 푼다 → 옛 scripts 폴더."""
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


def without(out, dropped):
    """옛 판 출력에서 (경로, 행) 마다 IM27 리터럴 발견 묶음 하나를 빼고 끝 줄의 건수를 맞춘다 → (뺀 출력, 뺀 수)."""
    n = 0
    for rel, line in dropped:
        head = '[IM27] BLOCKER — web/%s:%d\n  위반: %s (제1 규약 §3.4)\n  교정: ' % (rel, line, LITERAL)
        out, k = re.subn(re.escape(head) + r'[^\n]+\n\n', '', out, count=1)
        n += k
    tally = list(re.finditer(r'blocker (\d+)건', out))
    if tally:
        m = tally[-1]
        out = out[:m.start(1)] + str(int(m.group(1)) - n) + out[m.end(1):]
    return out, n


def bundle_unchanged(tmp):
    if subprocess.run(['git', '-C', str(REPO), 'cat-file', '-e', BASELINE + '^{commit}'],
                      capture_output=True, env=ENV).returncode:
        print('SKIP U — 바탕 커밋 %s 이 이 저장소 이력에 없다(얕은 clone 등) — 무변 묶음(U)을 건너뛴다(실패로 세지 않는다)' % BASELINE)
        return
    old = old_scripts(tmp / 'old')
    check('U0 고치기 전 판(%s) scripts 를 풀 수 있다' % BASELINE, (old / 'backstop.py').is_file())

    # U1 — 빠질 글자가 없는 프로젝트(선언 없음): 그대로 설 꼴 전부 + 다른 검사의 발견(옛 배치 · 층 · 명명)
    p, _ = mkproj(tmp / 'u1')
    write_cases(p, SAME)
    p.w('web/application/chart/domain_layer/chart/entity/chart_note.py', 'from django.db import models', '', '',
        'class ChartNote:', '    pass')
    p.w('web/stray/thing.py', 'from application.models import User', 'URL: str = "/api/stray"')
    p.markers()
    base = p.commit('base')
    written = dict(SAME, **{VM: SAME[VM] + ['        return "/api/v2/charts"  # IM27'],
                            HANDLER + 'case_new.py': ['def handle(obj: object) -> bool:',
                                                      '    return obj.path == "/api/new"  # IM27']})
    for rel in (VM, HANDLER + 'case_new.py'):
        p.w('web/' + rel, *written[rel])

    def both(name, *args, nonempty=None):
        new = backstop(p.root, *args)
        before = backstop(p.root, *args, scripts=old)
        check('U1 %s — 고치기 전 판과 byte 동일' % name, new == before,
              '새 판 exit=%d\n%s\n옛 판 exit=%d\n%s' % (new[0], new[1][-900:], before[0], before[1][-900:]))
        if nonempty:
            check('U1 %s — 헛대조 아님(%s)' % (name, nonempty), nonempty in new[1], new[1][-600:])
        return before

    both('게이트(--diff-base)', '--diff-base', base, nonempty='[IM27] BLOCKER')
    both('--slice-end', '--diff-base', base, '--slice-end', nonempty='슬라이스 끝')
    both('--only st(전역 퇴화)', '--only', 'st', nonempty='BLOCKER')
    both('--only im,nm(--diff-base)', '--diff-base', base, '--only', 'im,nm', nonempty='[IM27] BLOCKER')
    both('--only cy', '--diff-base', base, '--only', 'cy', nonempty='blocker 0건')
    everything = both('--all', '--all', nonempty='[IM27] BLOCKER')
    check('U1 픽스처 자체 — 그대로 설 파일의 표지가 고치기 전 판의 IM27 행과 같다(빠질 글자가 섞이지 않았다)',
          all(im27(everything[1], rel) == marked(lines) for rel, lines in written.items())
          and im27(everything[1], TEMPLATE) == WANT[TEMPLATE],
          [(rel, im27(everything[1], rel), marked(lines)) for rel, lines in written.items()
           if im27(everything[1], rel) != marked(lines)])
    for label, extra in (('--debt-scan', ()), ('--debt-scan --refactor', ('--refactor',))):
        outs = []
        for scripts in (SCRIPTS, old):
            target = p.root / '.git' / 'debt-u.json'
            if target.exists():
                target.unlink()
            e, out = backstop(p.root, '--debt-scan', *extra, '--json', target, scripts=scripts)
            data = json.loads(target.read_text(encoding='utf-8'))
            data.pop('scanned_at', None)
            data['scanner'] = {k: v for k, v in data.get('scanner', {}).items() if k != 'plugin'}
            outs.append((e, out, data))
        check('U1 %s 출력 · JSON(스캔 시각 · 판 글자 빼고) — 고치기 전 판과 같음' % label, outs[0] == outs[1]
              and any(k.startswith('IM27|') for k in outs[0][2].get('counts', {})), outs[0][1][-600:])

    # U2 — 빠질 글자가 든 프로젝트: 표지가 적은 만큼만 IM27 리터럴 발견이 빠지고 나머지 출력은 byte 그대로
    p, base = mkproj(tmp / 'u2')
    write_cases(p, {**CHANGED, **SAME})
    for args in (('--diff-base', base), ('--all',), ('--diff-base', base, '--only', 'im')):
        new = backstop(p.root, *args)
        before = backstop(p.root, *args, scripts=old)
        dropped = sorted((Counter({(rel, n): c for rel in CHANGED for n, c in Counter(im27(before[1], rel)).items()})
                          - Counter({(rel, n): c for rel in CHANGED for n, c in Counter(WANT[rel]).items()})).elements())
        trimmed, n = without(before[1], dropped)
        check('U2 %s — 옛 판 출력에서 빠질 글자의 IM27 %d건만 빼면 새 판과 byte 동일' % (' '.join(args[:1] + args[2:]), n),
              n == len(dropped) >= len(CHANGED) and (new[0], new[1]) == (before[0], trimmed),
              '새 판 exit=%d\n%s\n옛 판(뺀 뒤) exit=%d\n%s' % (new[0], new[1][-900:], before[0], trimmed[-900:]))


def main():
    bundles = [bundle_cases, bundle_repro, bundle_debt, bundle_unchanged]
    only = set(sys.argv[1:])
    for bundle in bundles:
        if only and bundle.__name__[len('bundle_'):] not in only:
            continue
        with tempfile.TemporaryDirectory(prefix='webim27-') as tmp:
            try:
                bundle(Path(tmp))
            except Exception as error:  # noqa: BLE001 — 묶음이 죽어도 실패로 세고 다음 묶음을 돈다
                check('%s — 묶음 실행 오류' % bundle.__name__, False, '%s: %s' % (type(error).__name__, error))
    print('IM27 요청 경로 비교 픽스처: PASS %d / FAIL %d' % (PASS, FAIL))
    return bool(FAIL)


if __name__ == '__main__':
    sys.exit(main())
