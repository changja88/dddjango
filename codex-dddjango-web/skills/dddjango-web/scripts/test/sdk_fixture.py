"""fixtures_sdk.sh 보조 — 합성 프로젝트 · 카카오 꼴 시험 SDK · 가짜 fetch 로 sdk_vendor.py 실행 · 목록 편집 · WV8 표본.

사용: python sdk_fixture.py <하위 명령> …
  mkproj <디렉터리>                                   표준 web/ 골격(green) + settings(KAKAO_JAVASCRIPT_KEY) + 첫 커밋
  sdkjs <경로> [<변형 낱말>]                           카카오 꼴 시험 사본(운영자 호스트 · this.<이름공간>= · 함수 · api 경로)
  docs <경로> <사본> [nosri|badsri|nocite]             원본 경로·sha384 를 인용하는 운영자 문서
  install <프로젝트> [--id X] [--variant V] [--draft JSON] [--source S] [--no-commit] [--message M]
          [--version V] [--extra-api P] [--replace] [--scope-add …] [--register-existing 경로] [--dry-run]
                                                      후보 → 설치(가짜 fetch) → `chore(web-sdk):` 커밋
  vendor <sdk_vendor 인자…>                            가짜 fetch(SDKFX_FETCH json: url → [최종 URL, Content-Type, 파일])
  edit <프로젝트> <id> <JSON 패치> [--rebind] [--rename NEW]   목록 항목 칸 바꾸기(결속 재계산은 --rebind)
  wv8                                                  WV8 리터럴 단위 표본 대조(어긋남 0 이면 exit 0)
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


def sdk_bytes(version='2.8.3', variant='', paths=None):
    text = SDK_JS.replace('@VERSION@', version).replace('@VARIANT@', variant)
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


def mkproj(d):
    p = Path(d)
    for sub in ('config', 'web/base', 'web/design_system/foundation', 'web/design_system/component/button',
                'web/static/css', 'web/static/js', 'web/static/htmx', 'web/static/images', 'web/chart/widget',
                'web/chart/chart/view', 'web/chart/chart/view_model', 'web/chart/chart/state',
                'web/chart/chart/section', 'docs'):
        (p / sub).mkdir(parents=True, exist_ok=True)
    (p / 'config/settings.py').write_text("SECRET_KEY = 'x'\nKAKAO_JAVASCRIPT_KEY: str = ''\n")
    (p / 'manage.py').write_text('# manage\n')
    (p / 'web/__init__.py').write_text('')
    (p / 'web/urls.py').write_text('urlpatterns = []\n')
    (p / 'web/apps.py').write_text('from django.apps import AppConfig\n\n\nclass WebConfig(AppConfig):\n    name = "web"\n')
    (p / 'web/base/base.html').write_text('{% load static %}\n<html>\n<body>\n{% block content %}{% endblock %}\n'
                                          '<script src="{% static \'web/htmx/htmx.min.js\' %}" defer></script>\n'
                                          '{% block scripts %}{% endblock scripts %}\n</body>\n</html>\n')
    (p / 'web/design_system/foundation/tokens.css').write_text(':root { --color-text: #222222; }\n')
    (p / 'web/design_system/foundation/motion.css').write_text('/* motion */\n')
    (p / 'web/design_system/component/button/primary_button.html').write_text('<button>ok</button>\n')
    (p / 'web/static/css/site.css').write_text('body { color: var(--color-text); }\n')
    (p / 'web/static/htmx/htmx.min.js').write_text('(function(){})();\n')
    (p / 'web/static/images/.gitkeep').write_text('')
    (p / 'web/chart/urls.py').write_text('urlpatterns = []\n')
    (p / 'web/chart/widget/.gitkeep').write_text('')
    for kind in ('view', 'view_model', 'state'):
        (p / 'web/chart/chart' / kind / '__init__.py').write_text('')
    (p / 'web/chart/chart/view/chart_view.py').write_text('def chart_view(request):\n    return None\n')
    (p / 'web/chart/chart/view/chart.html').write_text('{% extends "base.html" %}\n{% load static %}\n'
                                                       '{% block scripts %}\n{% endblock scripts %}\n')
    (p / 'web/chart/chart/section/.gitkeep').write_text('')
    (p / 'docs/.gitkeep').write_text('')
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
    a = ap.parse_args(argv)
    p = Path(a.proj).resolve()
    paths = [x for x in API_PATHS if x not in a.drop_api] + a.extra_api
    data = sdk_bytes(a.version, a.variant, paths)
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
    print('알 수 없는 명령 %s' % cmd)
    return 1


if __name__ == '__main__':
    sys.exit(main())
