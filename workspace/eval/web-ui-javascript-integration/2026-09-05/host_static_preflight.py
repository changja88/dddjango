"""Verify corrected host serves real core/CSS HTTP bytes, without UI generation."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import urllib.request

ROOT = Path('/tmp/dddjango-web-js-integration-20260905')
PYTHON = '/tmp/dddjango-ui-js-20260905/venv/bin/python'

for lane, port in [('claude', 18741), ('codex', 18742)]:
    app = ROOT / lane / 'app'
    with (ROOT / lane / 'host-http-server.txt').open('w') as log:
        process = subprocess.Popen([PYTHON, 'manage.py', 'runserver', f'127.0.0.1:{port}', '--noreload'], cwd=app, stdout=log, stderr=log)
        results = []
        try:
            for attempt in range(40):
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/static/web/htmx/htmx.min.js', timeout=1) as response:
                        data = response.read()
                        results.append({'url': response.url, 'status': response.status, 'sha256': hashlib.sha256(data).hexdigest()})
                    break
                except OSError:
                    if process.poll() is not None:
                        raise RuntimeError('Django server stopped: ' + (ROOT / lane / 'host-http-server.txt').read_text())
                    time.sleep(.1)
            else:
                raise RuntimeError('Django server did not become ready')
            assert results[0]['sha256'] == '71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de'
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/static/design_system/foundation/tokens.css') as response:
                results.append({'url': response.url, 'status': response.status, 'bytes': len(response.read())})
            (ROOT / lane / 'host-http-preflight.json').write_text(json.dumps(results, indent=2))
            print(lane, results)
        finally:
            process.terminate()
            process.wait(timeout=10)
