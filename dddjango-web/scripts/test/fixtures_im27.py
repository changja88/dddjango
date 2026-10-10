"""IM27 리터럴 절반 — 들어온 요청의 경로를 비교하는 글자 예외 픽스처(임시 git 저장소만 만들고 끝나면 지운다).

묶음: C 꼴(빠질 것 · 그대로 설 것 · 다른 IM 과 함께) · R 재현(오류 처리기 두 줄만 빠지고 VM 셋 그대로) · D 빚 스캔(같은 판정) ·
U 무변(고치기 전 판 scripts 와 같은 입력의 exit · stdout · stderr byte 대조 · 위 꼴이 든 프로젝트는 그 자리의 IM27 만 빠진다 ·
파서가 받지 못하는 파일은 지금 판정 그대로).
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


def run(root, *args, scripts=SCRIPTS, flags=()):
    """backstop 실행 → (exit, stdout, stderr). flags = 인터프리터 옵션(`-W error` 등)."""
    r = subprocess.run([sys.executable, *flags, '-B', str(scripts / 'backstop.py'), str(root), *map(str, args)],
                       capture_output=True, text=True, env=ENV)
    return r.returncode, r.stdout, r.stderr


def backstop(root, *args, scripts=SCRIPTS):
    e, out, err = run(root, *args, scripts=scripts)
    return e, out + err


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


# 로그 출처의 오염 — 꼴 하나에 파일 하나다(한 파일에 오염이 하나라도 있으면 그 파일의 로그 예외가 전부 꺼지므로 꼴마다
# 따로 둬야 그 꼴 하나가 잡히는지 볼 수 있다). 로그는 고치지 않은 다른 이름(clean · logging)으로 남긴다 — 그래도 선다.
LOGGER_HEAD = ['import logging', '', 'clean = logging.getLogger("clean")', 'other = logging.getLogger("other")']
MODULE_HEAD = ['import logging', 'import logging as other']
FACTORY_HEAD = ['import logging', 'from logging import getLogger as other']
LOGGER_LOG = 'clean.info(request.path)'
MODULE_LOG = 'logging.warning(request.path)'


def log_file(head, body, log, mark='  # IM27'):
    """머리 줄들 · patch 함수의 몸 · 비교 갈래 안에서 log 로 남기는 view. mark 를 비우면 비교 글자가 빠지는 파일이다."""
    return [*head, '', '', 'def patch(api_client: object) -> object:', *('    ' + line for line in body), '', '',
            'def view(request: object) -> None:', '    if request.path == "/api/x":' + mark, '        ' + log]


TAINTS = {
    # logger 이름 — 속성 대입 · setattr · del · 증강 대입 · 맨이름 읽기(인자 · 대입 · 컨테이너 · f-문자열 · 반환 · getattr) ·
    #    `__dict__` · `__class__` · 속성 사슬 끝의 대입 · 첨자 대입 · 바로 부르기
    'logger_assign': (LOGGER_HEAD, ['other.info = api_client.get'], LOGGER_LOG),
    'logger_setattr': (LOGGER_HEAD, ['setattr(other, "info", api_client.get)'], LOGGER_LOG),
    'logger_delete': (LOGGER_HEAD, ['del other.info'], LOGGER_LOG),
    'logger_augmented': (LOGGER_HEAD, ['other.calls += 1'], LOGGER_LOG),
    'logger_passed': (LOGGER_HEAD, ['api_client.keep(other)'], LOGGER_LOG),
    'logger_copied': (LOGGER_HEAD, ['alias = other'], LOGGER_LOG),
    'logger_listed': (LOGGER_HEAD, ['registry = [other]'], LOGGER_LOG),
    'logger_formatted': (LOGGER_HEAD, ['text = f"{other}"'], LOGGER_LOG),
    'logger_returned': (LOGGER_HEAD, ['return other'], LOGGER_LOG),
    'logger_getattr': (LOGGER_HEAD, ['getattr(other, "info")("x")'], LOGGER_LOG),
    'logger_dict': (LOGGER_HEAD, ['other.__dict__["info"] = api_client.get'], LOGGER_LOG),
    'logger_class': (LOGGER_HEAD, ['kind = other.__class__'], LOGGER_LOG),
    'logger_chain': (LOGGER_HEAD, ['other.parent.info = api_client.get'], LOGGER_LOG),
    'logger_item': (LOGGER_HEAD, ['other.handlers[0] = api_client'], LOGGER_LOG),
    'logger_called': (LOGGER_HEAD, ['other("x")'], LOGGER_LOG),
    # 출처가 될 수 있는 이름은 어느 범위에서 묶였든 본다 — 다른 함수의 지역 logger · 대상 둘 대입 · walrus · 주석 달린 대입
    'logger_local': (LOGGER_HEAD[:3], ['local = logging.getLogger("local")', 'local.info = api_client.get'], LOGGER_LOG),
    'logger_pair': (LOGGER_HEAD[:3], ['first = second = logging.getLogger("pair")', 'second.info = api_client.get'], LOGGER_LOG),
    'logger_walrus': (LOGGER_HEAD[:3], ['if (found := logging.getLogger("found")):', '    found.info = api_client.get'],
                      LOGGER_LOG),
    'logger_annotated': (LOGGER_HEAD[:3], ['noted: logging.Logger = logging.getLogger("noted")', 'noted.info = api_client.get'],
                         LOGGER_LOG),
    # getLogger 이름으로 만든 logger 도 출처가 될 수 있는 이름이다
    'logger_by_factory': (['import logging', 'from logging import getLogger', '', 'made = getLogger("made")'],
                          ['made.info = api_client.get'], MODULE_LOG),
    # 같은 글자의 인자를 고치는 다른 함수(가림을 따지지 않는다)
    'logger_shadow': (LOGGER_HEAD + ['', '', 'def configure(other: object, api_client: object) -> None:',
                                     '    other.info = api_client.get'], ['return None'], LOGGER_LOG),
    # logging 모듈의 별칭 — 모듈 함수 대입 · `Logger` 메서드 대입 · getLogger 결과의 메서드 대입 · setattr 둘 · del · `__dict__` ·
    #    맨이름 읽기 · 함수 안에서 들여온 별칭
    'module_assign': (MODULE_HEAD, ['other.warning = api_client.get'], MODULE_LOG),
    'module_class': (MODULE_HEAD, ['other.Logger.warning = api_client.get'], MODULE_LOG),
    'module_result': (MODULE_HEAD, ['other.getLogger("x").warning = api_client.get'], MODULE_LOG),
    'module_setattr': (MODULE_HEAD, ['setattr(other, "warning", api_client.get)'], MODULE_LOG),
    'module_setattr_class': (MODULE_HEAD, ['setattr(other.Logger, "warning", api_client.get)'], MODULE_LOG),
    'module_delattr_class': (MODULE_HEAD, ['delattr(other.Logger, "warning")'], MODULE_LOG),
    'module_delete': (MODULE_HEAD, ['del other.warning'], MODULE_LOG),
    'module_dict': (MODULE_HEAD, ['other.__dict__["warning"] = api_client.get'], MODULE_LOG),
    'module_bare': (MODULE_HEAD, ['return other'], MODULE_LOG),
    'module_inner': (MODULE_HEAD[:1], ['import logging as inner', 'inner.warning = api_client.get'], MODULE_LOG),
    'module_submodule': (MODULE_HEAD[:1] + ['import logging.handlers'], ['logging.handlers.emit = api_client.get'],
                         'logging.getLogger("x").warning(request.path)'),
    # getLogger 이름 — 값으로 넘김 · 속성 대입 · 결과의 메서드 대입 · 속성 읽기
    'factory_passed': (FACTORY_HEAD, ['factory = other'], MODULE_LOG),
    'factory_attribute': (FACTORY_HEAD, ['other.cache = api_client'], MODULE_LOG),
    'factory_result': (FACTORY_HEAD, ['other("x").warning = api_client.get'], MODULE_LOG),
    'factory_read': (FACTORY_HEAD, ['note = other.cache'], MODULE_LOG),
}
# 같은 틀에서 허용된 꼴만 쓰는 파일 — 비교 글자가 빠진다(위 파일들이 서는 까닭이 오염 한 줄뿐임을 보인다)
CLEANS = {
    'logger': (LOGGER_HEAD, ['other.setLevel(logging.DEBUG)', 'return other.name'], LOGGER_LOG),
    'module': (MODULE_HEAD, ['other.basicConfig(level=other.INFO)', 'return other.getLogger("x").name'], MODULE_LOG),
    'factory': (FACTORY_HEAD, ['other("x").setLevel(logging.DEBUG)', 'return other("x").name'], MODULE_LOG),
    # logging 에서 오지 않은 이름(상대 import 의 getLogger · 그것으로 만든 것)은 어떻게 쓰든 이 파일의 출처를 흐리지 않는다
    'relative': (['import logging', 'from .logging import getLogger as local_factory', '', 'local = local_factory("local")'],
                 ['local.info = api_client.get', 'return local_factory'], MODULE_LOG),
}


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
    # 헤더를 읽는 미들웨어 — 문자열 키로 읽는 META 가운데 경로 키가 아닌 것은 경로 읽기가 아니다(비교 글자는 그대로 빠진다)
    HANDLER + 'case_headers.py': [
        'class HeaderMiddleware:',
        '    def __init__(self, get_response: object) -> None:',
        '        self.get_response = get_response',
        '',
        '    def __call__(self, request: object) -> object:',
        '        agent = request.META.get("HTTP_USER_AGENT")',
        '        address = request.META["REMOTE_ADDR"]',
        '        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")',
        '        if request.path.startswith("/api/") and agent and address and forwarded:',
        '            return None',
        '        return self.get_response(request)',
        '',
        '',
        'def has_header(request: object) -> bool:',
        '    if "HTTP_AUTHORIZATION" in request.META and "HTTP_X_SKIP" not in request.META:',
        '        return request.path.startswith("/api/")',
        '    return False'],
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
        '    return request.path.startswith("/api/")',
        '',
        '',
        'def loose_logged(request: object) -> bool:',
        '    logger.warning("not found %s", request.build_absolute_uri())',
        '    logger.debug("meta %s scope %s", request.META, request.scope)',
        '    return request.path == "/api/x"',
        '',
        '',
        'def not_found(request: object) -> bool:',
        '    logger.warning("Not Found: %s", request.path, extra={"status_code": 404, "request": request})',
        '    return request.path.startswith("/api/")'],
    # `import logging` 과 `import logging.handlers` · 거듭된 `import logging` 은 같은 모듈 한 번이다
    HANDLER + 'case_log_handlers.py': [
        'import logging',
        'import logging.handlers',
        'import logging',
        '',
        'logger = logging.getLogger(__name__)',
        'logger.addHandler(logging.handlers.RotatingFileHandler("web.log"))',
        '',
        '',
        'def handler404(request: object, exception: Exception) -> object:',
        '    logging.getLogger(__name__).warning("Web page not found: %s", request.path)',
        '    path: str = request.path',
        '    if path == "/api" or path.startswith("/api/"):',
        '        return None',
        '    logger.info("fallback %s", path)',
        '    return exception'],
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
    # 글자 자리 — 탭 들여쓰기와 탭 사이 · 삼중 따옴표 · r / u 접두 · 같은 줄의 비교 둘과 호출 하나 · 조건 갈래 안에서만 묶인 지역 이름
    HANDLER + 'case_position.py': [
        'def tabbed(request: object) -> int:',
        '\tif request.path ==\t"/api/x":',
        '\t\treturn 1',
        '\treturn 0',
        '',
        '',
        'def triple(request: object) -> bool:',
        '    return request.path == """/api/x""" or request.path == \'\'\'/api/y\'\'\'',
        '',
        '',
        'def prefixed(request: object) -> bool:',
        '    return request.path == r"/api/x" or request.path.startswith(u"/api/y") or request.path in (R"/api/z",)',
        '',
        '',
        'def two_and_call(request: object, api_client: object) -> None:',
        '    if request.path == "/api/a" or request.path == "/api/b": api_client.get("/api/c")  # IM27',
        '',
        '',
        'def branch_alias(request: object, flag: bool) -> bool:',
        '    if flag:',
        '        path = request.path',
        '    return path == "/api/x"',
        '',
        '',
        'def keyword_only(*, request: object) -> bool:',
        '    return request.path == "/api/x"',
        '',
        '',
        'def beside(request: object) -> tuple[bool, str]:',
        '    return (request.path == "/api/a","/api/b")  # IM27'],
    # 컨테이너 — 직접 놓인 원소만 빠진다(호출 인자 · 조건식 · 안쪽 튜플의 글자는 선다 · 별표 원소 옆의 직접 원소는 빠진다)
    HANDLER + 'case_container.py': [
        'def call_element(request: object, api_client: object) -> bool:',
        '    return request.path in (api_client.get("/api/x"), "/api/y")  # IM27',
        '',
        '',
        'def conditional_element(request: object, flag: bool) -> bool:',
        '    return request.path in ("/api/x" if flag else "/api/y", "/api/z")  # IM27 IM27',
        '',
        '',
        'def nested_tuple(request: object) -> bool:',
        '    return request.path in (("/api/x",), "/api/z")  # IM27',
        '',
        '',
        'def prefix_nested(request: object) -> bool:',
        '    return request.path.startswith((("/api/x",), "/api/z"))  # IM27',
        '',
        '',
        'def starred_element(request: object, more: tuple[str, ...]) -> bool:',
        '    return request.path in (*more, "/api/x")'],
    # logging 을 평범하게 쓰는 꼴은 출처 그대로 — 주석 달린 대입(`logging.Logger`) · 수준 · 핸들러 설정 · 상수 읽기
    HANDLER + 'case_log_setup.py': [
        'import logging',
        '',
        'logger: logging.Logger = logging.getLogger(__name__)',
        'logger.setLevel(logging.DEBUG)',
        'logger.addHandler(logging.StreamHandler())',
        'logging.basicConfig(level=logging.INFO)',
        '',
        '',
        'def view(request: object) -> bool:',
        '    if logger.isEnabledFor(logging.DEBUG):',
        '        logger.debug("p=%s", request.path)',
        '    logger.warning("not found: %s", request.path)',
        '    return request.path == "/api/x"'],
    # 출처 이름이 여럿이어도 모두 허용된 꼴이면 그대로 출처다 — 모듈 별칭 둘 · getLogger 이름 둘 · logger 셋(밑줄 이름 · 주석 달린
    #    대입) · 함수마다 제 지역 logger · `import logging.handlers`
    HANDLER + 'case_log_many.py': [
        'import logging',
        'import logging as lg',
        'import logging.handlers',
        'from logging import getLogger',
        'from logging import getLogger as get_logger',
        '',
        '_logger: logging.Logger = logging.getLogger(__name__)',
        'audit = lg.getLogger("audit")',
        'access = get_logger("access")',
        'audit.setLevel(logging.INFO)',
        'audit.addHandler(logging.handlers.RotatingFileHandler("audit.log"))',
        '',
        '',
        'def first(request: object) -> bool:',
        '    log = logging.getLogger("first")',
        '    log.info("p=%s", request.path)',
        '    return request.path == "/api/x"',
        '',
        '',
        'def second(request: object) -> bool:',
        '    log = getLogger("second")',
        '    log.info("p=%s", request.path)',
        '    return request.path == "/api/x"',
        '',
        '',
        'def host(request: object) -> object:',
        '    _logger.warning("Web page not found: %s", request.path)',
        '    path: str = request.path',
        '    if path == "/api" or path.startswith("/api/"):',
        '        return None',
        '    audit.info("fallback %s", path)',
        '    access.info("fallback %s", path)',
        '    lg.debug("fallback %s", path)',
        '    return request'],
    **{HANDLER + 'case_clean_%s.py' % name: log_file(*spec, mark='') for name, spec in CLEANS.items()},
    # 별표 import 가 하나라도 있는 파일 — logging 이름이 덮였는지 알 수 없어 로그 예외를 전부 끈다(로그 없는 비교는 그대로 빠진다)
    HANDLER + 'case_log_star.py': [
        'import logging',
        'from web.common.util.names import *',
        '',
        'logger = logging.getLogger(__name__)',
        '',
        '',
        'def plain(request: object) -> bool:',
        '    return request.path == "/api/x"',
        '',
        '',
        'def by_module(request: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        logging.warning(request.path)',
        '',
        '',
        'def by_direct(request: object) -> bool:',
        '    logging.getLogger(__name__).warning("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def by_logger(request: object) -> bool:',
        '    logger.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def by_local(request: object) -> bool:',
        '    log = logging.getLogger("x")',
        '    log.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27'],
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
        '    return path == "/api/" and bool(other)  # IM27',
        '',
        '',
        'def bound_before(request: object) -> bool:',
        '    path = ""',
        '    path = request.path',
        '    return path == "/api/"  # IM27'],
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
        '    return inner',
        '',
        '',
        'def imported(request: object) -> bool:',
        '    from os import path as request',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def unpacked(request: object, pair: tuple[object, object]) -> bool:',
        '    request, other = pair',
        '    return request.path == "/api/" and bool(other)  # IM27',
        '',
        '',
        'def augmented(request: object) -> bool:',
        '    request += 1',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def matched(request: object, command: object) -> bool:',
        '    match command:',
        '        case request:',
        '            pass',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def matched_rest(request: object, command: object) -> bool:',
        '    match command:',
        '        case {**request}:',
        '            pass',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def matched_star(request: object, command: object) -> bool:',
        '    match command:',
        '        case [*request]:',
        '            pass',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def comprehension_walrus(request: object, items: list[object]) -> bool:',
        '    seen = [(request := item) for item in items]',
        '    return request.path == "/api/" and bool(seen)  # IM27',
        '',
        '',
        'def import_plain(request: object) -> bool:',
        '    import request',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def import_from(request: object) -> bool:',
        '    from os import request',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def function_named(request: object) -> bool:',
        '    def request() -> None:',
        '        pass',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def class_named(request: object) -> bool:',
        '    class request:',
        '        pass',
        '    return request.path == "/api/"  # IM27',
        '',
        '',
        'def inner_nonlocal(request: object, other: object) -> bool:',
        '    def swap() -> None:',
        '        nonlocal request',
        '        request = other',
        '    swap()',
        '    return request.path == "/api/"  # IM27'],
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
        '    return request.path == "/api/y"  # IM27',
        '',
        '',
        'def or_default(request: object, api_client: object) -> None:',
        '    target = request.path or "/"',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(target)',
        '',
        '',
        'def nested_twice(request: object) -> object:',
        '    path = request.path',
        '',
        '    def collect() -> list[str]:',
        '        return [path for _ in range(1)]',
        '    return collect() if path == "/api/x" else None  # IM27',
        '',
        '',
        'def full_path_keyword(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.get_full_path(force_append_slash=True))',
        '',
        '',
        'def full_path_positional(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.get_full_path(True))',
        '',
        '',
        'def full_path_info_argument(request: object, api_client: object) -> object:',
        '    if request.path == "/api/x":  # IM27',
        '        return api_client.get(request.get_full_path_info(False))',
        '    return None',
        '',
        '',
        'def meta_default(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.META.get("PATH_INFO", ""))',
        '',
        '',
        'def meta_default_alias(request: object, api_client: object) -> None:',
        '    url = request.META.get("PATH_INFO", "")',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(url)',
        '',
        '',
        'def absolute_uri(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.build_absolute_uri())',
        '',
        '',
        'def environ_read(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.environ["PATH_INFO"])',
        '',
        '',
        'def scope_read(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.scope["path"])',
        '',
        '',
        'def meta_alias(request: object, api_client: object) -> None:',
        '    meta = request.META',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(meta["PATH_INFO"])',
        '',
        '',
        'def method_alias(request: object, api_client: object) -> None:',
        '    reader = request.get_full_path',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(reader())',
        '',
        '',
        'def meta_variable_key(request: object, api_client: object, key: str) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.META[key])',
        '',
        '',
        'def meta_variable_get(request: object, api_client: object, key: str) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.META.get(key))',
        '',
        '',
        'def meta_spread(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.post(**request.META)',
        '',
        '',
        'def meta_request_uri(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.META["REQUEST_URI"])',
        '',
        '',
        'def meta_raw_uri(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.META.get("RAW_URI"))',
        '',
        '',
        'def meta_script_name(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.META.get("SCRIPT_NAME", ""))',
        '',
        '',
        'def meta_path_info_call(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.META["PATH_INFO"])',
        '',
        '',
        'def inner_loose(request: object, api_client: object) -> object:',
        '    def fetch() -> object:',
        '        return api_client.get(request.get_full_path(True))',
        '    return fetch() if request.path == "/api/x" else None  # IM27',
        '',
        '',
        'def inner_meta(request: object, api_client: object) -> object:',
        '    fetch = lambda: api_client.get(request.META.get("PATH_INFO", ""))  # noqa: E731',
        '    return fetch() if request.path == "/api/x" else None  # IM27',
        '',
        '',
        'def full_path_plain(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.get_full_path())',
        '',
        '',
        'def full_path_info_plain(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.get_full_path_info())',
        '',
        '',
        'def path_info_reuse(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.path_info)',
        '',
        '',
        'def meta_get_reuse(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.get(request.META.get("PATH_INFO"))',
        '',
        '',
        'def unbound_prefix(request: object, api_client: object) -> bool:',
        '    starts = request.path.startswith',
        '    api_client.keep(starts)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def meta_has_path_key(request: object) -> bool:',
        '    return "PATH_INFO" in request.META and request.path == "/api/x"  # IM27',
        '',
        '',
        'def meta_has_variable_key(request: object, key: str) -> bool:',
        '    return key in request.META and request.path == "/api/x"  # IM27',
        '',
        '',
        'def meta_has_chained(request: object, headers: object) -> bool:',
        '    return "HTTP_X" in request.META in headers and request.path == "/api/x"  # IM27',
        '',
        '',
        'def meta_contains_reversed(request: object) -> bool:',
        '    return request.META in ("HTTP_X",) and request.path == "/api/x"  # IM27',
        '',
        '',
        'def meta_items(request: object, api_client: object) -> None:',
        '    if request.path == "/api/x":  # IM27',
        '        api_client.post(dict(request.META.items()))',
        '',
        '',
        'def absolute_uri_argument(request: object) -> object:',
        '    if request.path == "/api/x":  # IM27',
        '        return redirect(request.build_absolute_uri("/login/"))',
        '    return None'],
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
        '    return request.path.startswith("/api/", 0)  # IM27',
        '',
        '',
        'def bytes_literal(request: object) -> bool:',
        '    return request.path == b"/api/x"  # IM27',
        '',
        '',
        'def mapping(request: object) -> bool:',
        '    return request.path in {"/api/x": 1}  # IM27',
        '',
        '',
        'def ordered(request: object) -> bool:',
        '    return request.path < "/api/x"  # IM27',
        '',
        '',
        'def identity(request: object) -> bool:',
        '    return request.path is "/api/x"  # IM27'],
    # 로그 예외의 경계 — 하나라도 어기면 그 함수의 비교 글자는 빠지지 않는다: 로그가 아닌 호출(비교 앞 · 뒤) · logging 출처로
    #    확인되지 않는 받는 쪽(다시 붙인 메서드 · 다른 객체 · self.logger · 인자 · 가림 · 재바인딩 · 함수 안 import · 바깥 함수의 이름) ·
    #    독립 문장이 아닌 로그 호출(반환 · 대입 · 바깥 호출의 인자 · 첨자) · log 의 level 자리 · 로그 호출까지 가는 길의 다른 노드 ·
    #    다른 연산 · 받는 쪽에서 읽기 · 로그가 아닌 함수 호출 · 응답과 이동 호출(과보고로 남는 알려진 한계)
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
        '    return None',
        '',
        '',
        'def comprehension_logger(request: object, clients: list[object]) -> bool:',
        '    seen = [(logger := client) for client in clients]',
        '    logger.info("p=%s", request.path)',
        '    return request.path == "/api/x" and bool(seen)  # IM27',
        '',
        '',
        'def loose_logged_argument(request: object) -> bool:',
        '    logger.warning("not found %s", request.get_full_path(True))',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def loose_logged_subscript(request: object) -> bool:',
        '    logger.warning("not found %s", request.environ["PATH_INFO"])',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def loose_logged_default(request: object) -> bool:',
        '    logger.warning("not found %s", request.META.get("PATH_INFO", ""))',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def named_by_path(request: object) -> bool:',
        '    logging.getLogger(request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def child_by_path(request: object) -> bool:',
        '    logger.getChild(request.path)',
        '    return request.path == "/api/x"  # IM27'],
    # 이름이 logging 으로 시작할 뿐인 다른 모듈
    HANDLER + 'case_log_lookalike.py': [
        'import loggingx',
        '',
        '',
        'def view(request: object) -> bool:',
        '    loggingx.warning("p=%s", request.path)',
        '    loggingx.getLogger("x").warning("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27'],
    # 조건 갈래 · try 안의 별표 import 도 별표 import 다
    HANDLER + 'case_log_star_branch.py': [
        'import logging',
        '',
        'if logging.root.handlers:',
        '    from web.common.util.names import *',
        '',
        '',
        'def view(request: object) -> bool:',
        '    logging.warning("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27'],
    HANDLER + 'case_log_star_try.py': [
        'import logging',
        '',
        'try:',
        '    from web.common.util.names import *',
        'except ImportError:',
        '    pass',
        '',
        '',
        'def view(request: object) -> bool:',
        '    logging.warning("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27'],
    # 상대 import 의 getLogger 는 logging 출처가 아니다
    HANDLER + 'case_log_relative.py': [
        'from .logging import getLogger',
        '',
        'logger = getLogger(__name__)',
        '',
        '',
        'def direct(request: object) -> bool:',
        '    getLogger(__name__).warning("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27',
        '',
        '',
        'def named(request: object) -> bool:',
        '    logger.info("p=%s", request.path)',
        '    return request.path == "/api/x"  # IM27'],
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
    # 로그 출처의 오염 — 꼴 하나에 파일 하나(TAINTS)
    **{HANDLER + 'case_taint_%s.py' % name: log_file(*spec) for name, spec in TAINTS.items()},
    # 같은 logging 모듈을 다른 별칭으로 — 한 별칭의 함수를 바꾸면 다른 별칭으로 남긴 로그도 그 함수다
    HANDLER + 'case_taint_alias_pair.py': [
        'import logging as a',
        'import logging as b',
        '',
        '',
        'def view(request: object, api_client: object) -> None:',
        '    a.warning = api_client.get',
        '    if request.path == "/api/x":  # IM27',
        '        b.warning(request.path)'],
    # 같은 logger 를 다시 얻음 — 이름으로 고친 logger 를 직접 꼴(`logging.getLogger(…).info`)로 다시 쓴다
    HANDLER + 'case_taint_reacquired.py': [
        'import logging',
        '',
        '',
        'def view(request: object, api_client: object) -> None:',
        '    logger = logging.getLogger(__name__)',
        '    logger.info = api_client.get',
        '    if request.path == "/api/x":  # IM27',
        '        logging.getLogger(__name__).info(request.path)'],
    # 한 logger 에 속성을 대입한 파일 — 같은 파일의 다른 logger 로 남긴 로그도 예외를 못 쓴다(과보고로 남는 알려진 한계)
    HANDLER + 'case_taint_propagate.py': [
        'import logging',
        '',
        '_audit: logging.Logger = logging.getLogger("audit")',
        '_audit.propagate = False',
        '_logger: logging.Logger = logging.getLogger(__name__)',
        '',
        '',
        'def handler(request: object) -> object:',
        '    _logger.warning("not found: %s", request.path)',
        '    if request.path.startswith("/api/"):  # IM27',
        '        return None',
        '    return request'],
    # 문법 오류 파일 — 판정하지 못하니 지금처럼 선다
    HANDLER + 'case_broken.py': [
        'def handle(request: object) -> bool:',
        '    if request.path.startswith("/api/")  # IM27',
        '        return True'],
    # 잘못된 이스케이프가 든 파일(비교 없음 · 문법 오류와 함께) — 보조 파싱이 경고를 stderr 에 흘리지 않는다
    HANDLER + 'case_escape.py': [
        'API_URL: str = "/api/x"  # IM27',
        'PATTERN: str = "\\d+"'],
    HANDLER + 'case_escape_broken.py': [
        'PATTERN: str = "\\d+"',
        '',
        '',
        'def handle(request: object) -> bool:',
        '    if request.path.startswith("/api/")  # IM27',
        '        return True'],
    # 별표 import 의 대상(`/api/` 글자 없음)
    'common/util/names.py': [
        'class Sender:',
        '    def warning(self, path: str) -> str:',
        '        return path',
        '',
        '',
        'logging = Sender()',
        '__all__ = ["logging"]'],
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
    e, out, err = run(p.root, '--diff-base', base, '--only', 'im')
    check('C stderr 0 줄(잘못된 이스케이프가 든 파일 둘 포함 — 보조 파싱이 경고를 흘리지 않는다)', err == '' and e == 2, err[:600])
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


def nested(depth):
    """괄호 없는 lambda 를 depth 겹 겹친 함수가 든 파일(비교 없음 · 첫 줄에 API 주소 글자)."""
    return ['URL: str = "/api/v1"', '', '', 'def view(request: object) -> object:', '    return ' + 'lambda: ' * depth + '1']


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
        new = run(p.root, *args)
        before = run(p.root, *args, scripts=old)
        check('U1 %s — 고치기 전 판과 exit · stdout · stderr byte 동일' % name, new == before,
              '새 판 exit=%d\n%s\nstderr: %s\n옛 판 exit=%d\n%s\nstderr: %s'
              % (new[0], new[1][-900:], new[2][-600:], before[0], before[1][-900:], before[2][-600:]))
        if nonempty:
            check('U1 %s — 헛대조 아님(%s)' % (name, nonempty), nonempty in new[1], new[1][-600:])
        return before

    both('게이트(--diff-base)', '--diff-base', base, nonempty='[IM27] BLOCKER')
    only_im = both('--only im(--all)', '--all', '--only', 'im', nonempty='web/%scase_escape.py:1' % HANDLER)
    check('U1 --only im — 옛 판도 stderr 0 줄(대조할 바탕이 빈 줄 그대로다)', only_im[2] == '', only_im[2][:600])
    both('--slice-end', '--diff-base', base, '--slice-end', nonempty='슬라이스 끝')
    both('--only st(전역 퇴화)', '--only', 'st', nonempty='BLOCKER')
    both('--only im,nm(--diff-base)', '--diff-base', base, '--only', 'im,nm', nonempty='[IM27] BLOCKER')
    both('--only cy', '--diff-base', base, '--only', 'cy', nonempty='blocker 0건')
    everything = both('--all', '--all', nonempty='[IM27] BLOCKER')
    everything = (everything[0], everything[1] + everything[2])
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
            e, out, err = run(p.root, '--debt-scan', *extra, '--json', target, scripts=scripts)
            data = json.loads(target.read_text(encoding='utf-8'))
            data.pop('scanned_at', None)
            data['scanner'] = {k: v for k, v in data.get('scanner', {}).items() if k != 'plugin'}
            outs.append((e, out, err, data))
        check('U1 %s — exit · stdout · stderr 는 고치기 전 판과 byte 동일 · JSON 은 scanned_at · scanner.plugin 을 뺀 파싱 결과가 같음'
              % label, outs[0] == outs[1]
              and any(k.startswith('IM27|') for k in outs[0][3].get('counts', {})), outs[0][1][-600:] + outs[0][2][-600:])

    # U2 — 빠질 글자가 든 프로젝트: 표지가 적은 만큼만 IM27 리터럴 발견이 빠지고 나머지 출력은 byte 그대로
    p, base = mkproj(tmp / 'u2')
    write_cases(p, {**CHANGED, **SAME})
    for args in (('--diff-base', base), ('--all',), ('--diff-base', base, '--only', 'im')):
        new = run(p.root, *args)
        before = run(p.root, *args, scripts=old)
        dropped = sorted((Counter({(rel, n): c for rel in CHANGED for n, c in Counter(im27(before[1], rel)).items()})
                          - Counter({(rel, n): c for rel in CHANGED for n, c in Counter(WANT[rel]).items()})).elements())
        trimmed, n = without(before[1], dropped)
        check('U2 %s — 옛 판 stdout 에서 빠질 글자의 IM27 %d건만 빼면 새 판과 byte 동일 · exit · stderr 도 같음'
              % (' '.join(args[:1] + args[2:]), n),
              n == len(dropped) >= len(CHANGED) and new == (before[0], trimmed, before[2]),
              '새 판 exit=%d\n%s\nstderr: %s\n옛 판(뺀 뒤) exit=%d\n%s\nstderr: %s'
              % (new[0], new[1][-900:], new[2][-600:], before[0], trimmed[-900:], before[2][-600:]))

    # U3 — 파서가 받지 못하는 파일(깊은 식 둘 · NUL 글자)과 경고를 내는 파일(잘못된 이스케이프): 보조 파싱이 죽지도 흘리지도
    #      않고 지금 판정 그대로다. 판정이 따라 내려가지 못할 만큼 깊게 겹친 파일도 같다. 경고를 오류로 올린 실행(-W error)에서도 같다
    p, base = mkproj(tmp / 'u3')
    hard = {HANDLER + 'case_deep_sum.py': ['URL: str = "/api/v1/x"', 'BIG: str = ' + '+'.join(['"a"'] * 200000)],
            HANDLER + 'case_deep_not.py': ['URL: str = "/api/v1/y"', 'FLAG: bool = ' + 'not ' * 20000 + 'True'],
            HANDLER + 'case_nul.py': ['URL: str = "/api/v1/z"', 'NUL: str = "\x00"'],
            HANDLER + 'case_escape_new.py': ['URL: str = "/api/v1/w"', 'PATTERN: str = "\\d+"'],
            # 파서는 받지만 판정이 따라 내려가지 못할 만큼 깊게 겹친 lambda
            HANDLER + 'case_nest_1000.py': nested(1000), HANDLER + 'case_nest_1100.py': nested(1100)}
    # 그보다 얕게 겹친 파일은 여느 파일처럼 판정한다 — 로그 없는 비교 글자가 빠진다(옛 판은 선다)
    shallow = HANDLER + 'case_nest_900.py'
    p.w('web/' + shallow, *nested(900), '', '', 'def plain(request: object) -> bool:', '    return request.path == "/api/x"')
    for rel, lines in hard.items():
        p.w('web/' + rel, *lines)
    for args, flags in ((('--diff-base', base, '--only', 'im'), ()), (('--all', '--only', 'im'), ()),
                        (('--all', '--only', 'im'), ('-W', 'error'))):
        new = run(p.root, *args, flags=flags)
        before = run(p.root, *args, scripts=old, flags=flags)
        trimmed, n = without(before[1], [(shallow, 9)])
        check('U3 %s%s — 파서가 못 받는 파일 셋 · 경고 파일 하나 · 깊게 겹친 파일 둘: 고치기 전 판과 exit · stderr byte 동일 · stdout 은 '
              '얕게 겹친 파일의 비교 글자 한 건만 다름 · exit 2 · stderr 0 줄 · 각 파일 첫 줄 IM27'
              % (' '.join(args[:1] + args[2:]), ' (-W error)' if flags else ''),
              n == 1 and new == (before[0], trimmed, before[2]) and new[0] == 2 and new[2] == ''
              and all(im27(new[1], rel) == [1] for rel in list(hard) + [shallow]),
              '새 판 exit=%d\n%s\nstderr: %s\n옛 판 exit=%d\n%s\nstderr: %s'
              % (new[0], new[1][-900:], new[2][-900:], before[0], trimmed[-600:], before[2][-600:]))


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
