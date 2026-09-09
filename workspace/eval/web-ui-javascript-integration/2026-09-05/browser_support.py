"""Independent browser instrumentation; not supplied to runtime generators."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import struct
import subprocess
import time
import urllib.request
import zlib

ROOT = Path(os.environ.get('DDDJANGO_WEB_EVAL_ROOT', '/tmp/dddjango-web-js-integration-20260905'))
PYTHON = os.environ.get('DDDJANGO_WEB_EVAL_PYTHON', '/tmp/dddjango-ui-js-20260905/venv/bin/python')
CHROME = os.environ.get('DDDJANGO_WEB_EVAL_CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')

RESOURCE_TRACKER = '''(() => {
  const create = URL.createObjectURL.bind(URL);
  const revoke = URL.revokeObjectURL.bind(URL);
  window.__resourceEvidence = {created: [], revoked: [], typeAssignments: []};
  window.__htmxSettled = [];
  document.addEventListener('htmx:afterSettle', event => {
    window.__htmxSettled.push({id: event.detail.elt.id, revision: event.detail.elt.getAttribute('data-revision')});
  });
  const typeDescriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'type');
  Object.defineProperty(HTMLInputElement.prototype, 'type', {...typeDescriptor, set(value) {
    window.__resourceEvidence.typeAssignments.push({id: this.id, value});
    return typeDescriptor.set.call(this, value);
  }});
  const setAttribute = Element.prototype.setAttribute;
  Element.prototype.setAttribute = function(name, value) {
    if (this instanceof HTMLInputElement && name.toLowerCase() === 'type') {
      window.__resourceEvidence.typeAssignments.push({id: this.id, value});
    }
    return setAttribute.call(this, name, value);
  };
  URL.createObjectURL = (blob) => {
    const url = create(blob);
    window.__resourceEvidence.created.push({url, size: blob.size, type: blob.type});
    return url;
  };
  URL.revokeObjectURL = (url) => {
    window.__resourceEvidence.revoked.push(url);
    return revoke(url);
  };
})();'''

def png(rgb):
    def chunk(kind, content):
        return struct.pack('!I', len(content)) + kind + content + struct.pack('!I', zlib.crc32(kind + content))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', 2, 2, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress((b'\x00' + bytes(rgb) * 2) * 2)) + chunk(b'IEND', b'')

def local_image(name, rgb=(220, 40, 60)):
    return {'name': name, 'mimeType': 'image/png', 'buffer': png(rgb)}

@contextmanager
def django_server(lane, port, label):
    directory = ROOT / lane
    app = directory / 'app'
    with (directory / (label + '.server.log')).open('w') as log:
        process = subprocess.Popen([PYTHON, 'manage.py', 'runserver', f'127.0.0.1:{port}', '--noreload'], cwd=app, stdout=log, stderr=log)
        try:
            for _ in range(100):
                try:
                    urllib.request.urlopen(f'http://127.0.0.1:{port}/static/web/htmx/htmx.min.js', timeout=1).close()
                    break
                except OSError:
                    if process.poll() is not None:
                        raise RuntimeError('Django exited before browser evaluation')
                    time.sleep(.1)
            else:
                raise RuntimeError('Django server readiness timeout')
            yield f'http://127.0.0.1:{port}'
        finally:
            process.terminate()
            process.wait(timeout=10)

class Evidence:
    def __init__(self, lane, label):
        self.path = ROOT / lane / (label + '.json')
        self.data = {'lane': lane, 'label': label, 'checks': {}, 'requests': [], 'htmx_responses': [], 'console_errors': [], 'page_errors': []}

    def save(self):
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))

    def passed(self, check, detail):
        self.data['checks'][check] = {'status': 'PASS', 'detail': detail}
        self.save()

    def failed(self, check, error):
        self.data['checks'][check] = {'status': 'FAIL', 'detail': str(error)}
        self.save()

    def attach(self, page):
        page.on('request', lambda request: self.data['requests'].append({'url': request.url, 'method': request.method, 'type': request.resource_type, 'htmx': request.headers.get('hx-request')}))
        page.on('pageerror', lambda error: self.data['page_errors'].append(str(error)))
        page.on('console', lambda message: self.data['console_errors'].append(message.text) if message.type == 'error' else None)

    def resource_state(self, page):
        return page.evaluate('window.__resourceEvidence')
