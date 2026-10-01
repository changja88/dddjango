"""v4 test_dv4_v5 브라우저 합성 재사용. 서버/네트워크 없이 route fulfill만 쓴다.

Playwright가 설치된 Python으로 실행한다. --chromium은 기존 로컬 실행 파일 경로다.
"""
import argparse
import copy
from pathlib import Path

from playwright.sync_api import sync_playwright
from test_style_census import C


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chromium')
    args = parser.parse_args()
    source = (Path(__file__).resolve().parents[2] / 'assets/style_census.js').read_text()
    C.SDK_SCOPE = {'sdk': {'globals': ['SDK'], 'files': ['/static/vendor/sdk.js']}}
    html = '<html><head>{script}</head><body><main id="app"><p style="color:#333">공유</p></main></body></html>'
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=args.chromium)
        def capture(status=200, vendor=True, routes=None, root='#app'):
            page = browser.new_page()
            def serve(route):
                if route.request.url == 'http://w8.test/':
                    route.fulfill(status=200, content_type='text/html', body=html.format(
                        script='<script src="/static/vendor/sdk.js"></script>' if vendor else ''))
                elif route.request.url == 'http://w8.test/static/vendor/sdk.js':
                    route.fulfill(status=status, content_type='application/javascript',
                                  body='window.SDK={};' if status == 200 else '')
                else:
                    route.abort()
            page.route('**/*', serve)
            page.goto('http://w8.test/')
            page.evaluate('() => document.fonts.ready')
            result = page.evaluate(source, {'root': root, 'routeSet': routes, 'sdkGlobals': ['SDK']})
            page.close()
            return result
        ok = capture(routes=['operator-hosts'])
        missing = capture(status=404, routes=['operator-hosts'])
        undeclared = capture()
        plain = capture(vendor=False)
        root_missing = capture(vendor=False, root='#missing')
        root_many = capture(vendor=False, root='main,p')
        browser.close()
    def unrun(d, i, case):
        return [f['prop'] for f in C.compare_case(d, i, case)['findings'] if f['kind'] == 'unrun']
    assert ok['meta']['census_version'] == 4
    assert ok['meta']['vendor'] == [{'path': '/static/vendor/sdk.js', 'status': 200}]
    assert ok['meta']['sdk_globals'] == {'SDK': True}
    assert missing['meta']['vendor'] == [{'path': '/static/vendor/sdk.js', 'status': 404}]
    assert unrun(ok, ok, 'sdk') == []
    assert unrun(ok, missing, 'sdk') == ['sdk-state']
    assert unrun(ok, undeclared, 'sdk') == ['sdk-state']
    assert unrun(plain, undeclared, 'plain') == ['sdk-state']
    assert unrun(plain, plain, 'plain') == []
    legacy = copy.deepcopy(plain)
    legacy['meta']['census_version'] = 3
    legacy['meta'].pop('root_matched')
    legacy['meta'].pop('route_set')
    assert unrun(plain, legacy, 'plain') == ['schema-impl']
    assert root_missing['meta']['root_matched'] == 0 and root_missing['records'] == []
    assert root_many['meta']['root_matched'] == 2 and root_many['records'] == []
    print('W8 browser: v4 SDK six scenarios + root zero/multiple PASS (network intercepted)')


if __name__ == '__main__':
    main()
