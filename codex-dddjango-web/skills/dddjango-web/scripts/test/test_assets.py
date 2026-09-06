#!/usr/bin/env python3
"""Exercise real acquisition CLI outputs; no remote services or decoder mocks."""
import base64
import functools
import hashlib
import http.server
import json
from pathlib import Path
import struct
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import zlib

SCRIPTS = Path(__file__).resolve().parents[1]


def png(pixel=b'\xff\0\0'):
    # One 1x1 RGB pixel, complete chunks + compressed scanline (not a magic stub).
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b'\0' + pixel)) + chunk(b'IEND', b'')


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.out = self.root / 'frozen'
        self.app = self.root / 'app'

    def put(self, name, data):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data.encode() if isinstance(data, str) else data)
        return path

    def run_cli(self, name, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / name), *map(str, args)], capture_output=True, text=True)

    def fetch(self):
        manifest = self.root / 'images.json'
        result = self.run_cli('fetch_images.py', self.source, '--asset-base', self.source, '--assets-root', self.app, '--out', manifest)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(manifest.read_text())

    def dc(self, label=None):
        tokens = self.root / 'tokens.json'
        tokens.write_text('{}')
        args = ['--screen-label', label] if label is not None else []
        return self.run_cli('extract_dc.py', self.source / 'renamed.dc.html', '--tokens', tokens, '--asset-base', self.source, '--assets-root', self.app, '--asset-manifest', self.root / 'images.json', '--meta', self.root / 'meta.json', *args)

    def freeze(self, entry='screen.html', *extra):
        result = self.run_cli('freeze_design.py', self.source / entry, '--out', self.out, *extra)
        return result

    def test_complete_image_is_landed_with_digest(self):
        self.put('good.png', png())
        self.put('screen.html', '<img src="good.png">')
        manifest = self.fetch()
        self.assertTrue(manifest.get('source_ready'), manifest)
        item = manifest['images'][0]
        self.assertEqual(item.get('size_bytes'), len(png()))
        self.assertEqual(item.get('sha256'), hashlib.sha256(png()).hexdigest())
        self.assertEqual((self.app / item['local_path']).read_bytes(), png())

    def test_acquired_asset_passes_the_plugin_filename_gate(self):
        self.put('logo.png', png())
        self.put('screen.html', '<img src="logo.png">')
        manifest = self.fetch()
        self.assertTrue(manifest['source_ready'])
        gate = self.run_cli('backstop.py', self.app, '--all', '--only', 'wn8')
        self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)

    def test_refresh_lands_new_content_without_overwriting_previous_asset(self):
        self.put('logo.png', png())
        self.put('screen.html', '<img src="logo.png">')
        old = self.fetch()['images'][0]
        self.put('logo.png', png(b'\0\xff\0'))
        refreshed = self.fetch()
        self.assertTrue(refreshed['source_ready'], refreshed)
        new = refreshed['images'][0]
        self.assertNotEqual(new['local_path'], old['local_path'])
        self.assertEqual((self.app / old['local_path']).read_bytes(), png())
        self.assertEqual((self.app / new['local_path']).read_bytes(), png(b'\0\xff\0'))

    def test_truncated_png_and_html_error_body_never_land(self):
        self.put('broken.png', png()[:-12])
        self.put('error.png', '<html><body>Not found</body></html>')
        self.put('empty.png', b'')
        self.put('screen.html', '<img src="broken.png"><img src="error.png"><img src="empty.png">')
        manifest = self.fetch()
        self.assertEqual([i['status'] for i in manifest['images']], ['failed'] * 3)
        self.assertFalse(manifest['source_ready'])
        self.assertTrue(all(i['reason'] and not i['local_path'] for i in manifest['images']))
        self.assertFalse(list(self.app.rglob('*.png')))

    def test_inline_truncated_png_is_failed_not_inline(self):
        encoded = base64.b64encode(png()[:30]).decode()
        self.put('screen.html', f'<img src="data:image/png;base64,{encoded}">')
        self.assertEqual(self.fetch()['images'][0]['status'], 'failed')

    def test_same_basename_is_not_overwritten(self):
        self.put('a/logo.png', png())
        other = png()  # Separate sources may legitimately reuse bytes.
        self.put('b/logo.png', other)
        self.put('screen.html', '<img src="a/logo.png"><img src="b/logo.png">')
        images = self.fetch()['images']
        self.assertNotEqual(images[0]['local_path'], images[1]['local_path'])
        self.assertEqual(len(list(self.app.rglob('*.png'))), 2)

    def test_label_selects_content_and_retains_explicit_frame_evidence(self):
        self.put('good.png', png())
        self.put('renamed.dc.html', '<!DOCTYPE html>\r\n<div data-screen-label="Summary"><span>Summary</span><section style="width: 640px; height: 400px"><img src="good.png"><span style="width: 9px; height: 9px"></span></section></div>')
        result = self.dc()
        self.assertEqual(result.returncode, 0, result.stderr)
        meta = json.loads((self.root / 'meta.json').read_text())
        self.assertEqual(meta['screen_label'], 'Summary')
        self.assertEqual(meta['explicit_frames'], [{'width_px': 640, 'height_px': 400}])
        self.assertEqual(meta['source_sha256'], hashlib.sha256((self.source / 'renamed.dc.html').read_bytes()).hexdigest())

    def test_ambiguous_screens_require_explicit_label(self):
        self.put('a.png', png())
        self.put('b.png', png())
        self.put('renamed.dc.html', '<section data-screen-label="Overview"><img src="a.png"></section><div data-screen-label="History"><img src="b.png"></div>')
        result = self.dc()
        self.assertNotEqual(result.returncode, 0, 'multiple screens were silently reduced to one')
        self.assertIn('screen-label', result.stderr)
        selected = self.dc('History')
        self.assertEqual(selected.returncode, 0, selected.stderr)
        self.assertEqual([i['src'] for i in json.loads((self.root / 'images.json').read_text())['images']], ['b.png'])

    def test_selected_screen_ingests_imported_component_and_css_images(self):
        self.put('renamed.dc.html', '<section data-screen-label="Summary"><div style="background:url(images/bg.png)"></div><x-import from="Panel.jsx"></x-import></section>')
        self.put('Panel.jsx', 'export default () => <img src="images/logo.png" alt="Brand"/>;')
        self.put('images/bg.png', png())
        self.put('images/logo.png', png())
        result = self.dc()
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((self.root / 'images.json').read_text())
        self.assertTrue(manifest['source_ready'])
        self.assertEqual({i['src'] for i in manifest['images']}, {'images/bg.png', 'images/logo.png'})
        self.assertEqual(len(list(self.app.rglob('*.png'))), 2)

    def test_freeze_collects_relative_files_css_imports_and_component_images(self):
        self.put('screen.html', '<link rel="stylesheet" href="css/base.css"><script src="support.js"></script><x-import from="./Panel.jsx"></x-import>')
        self.put('css/base.css', '@import "theme.css"; .a {background:url(../images/bg.png)}')
        self.put('css/theme.css', '.a {color: navy}')
        self.put('images/bg.png', png())
        self.put('support.js', '/* rendering dependency, retained verbatim */')
        self.put('Panel.jsx', 'export default () => <img src="./images/logo.png"/>;')
        self.put('images/logo.png', png())
        result = self.freeze()
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((self.out / 'source-manifest.json').read_text())
        self.assertTrue(manifest['source_ready'])
        self.assertEqual(len(manifest['files']), 7)
        for item in manifest['files']:
            self.assertEqual(item['status'], 'ok')
            payload = (self.out / item['local_path']).read_bytes()
            self.assertEqual(item['size_bytes'], len(payload))
            self.assertEqual(item['sha256'], hashlib.sha256(payload).hexdigest())
        self.assertEqual((self.out / 'css/base.css').read_bytes(), (self.source / 'css/base.css').read_bytes())
        # Existing complete snapshots can be validated in place, e.g. DesignSync manual get_file output.
        rerun = self.run_cli('freeze_design.py', self.out / 'screen.html', '--out', self.out)
        self.assertEqual(rerun.returncode, 0, rerun.stderr)

    def test_local_frozen_sources_feed_both_consumers_after_original_is_deleted(self):
        self.put('screen.dc.html', '<section data-screen-label="Example"><img src="images/logo.png"><link rel="stylesheet" href="css/style.css"></section>')
        self.put('css/style.css', '.x {background:url(../images/background.png)}')
        self.put('images/logo.png', png())
        self.put('images/background.png', png(b'\0\xff\0'))
        result = self.freeze('screen.dc.html')
        self.assertEqual(result.returncode, 0, result.stderr)
        shutil.rmtree(self.source)
        result = self.run_cli('fetch_images.py', self.out, '--asset-base', self.out, '--assets-root', self.app, '--out', self.root / 'images.json')
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((self.root / 'images.json').read_text())
        self.assertTrue(manifest['source_ready'], manifest)
        self.assertEqual(len(manifest['images']), 2)
        tokens = self.root / 'tokens.json'
        tokens.write_text('{}')
        result = self.run_cli('extract_dc.py', self.out / 'screen.dc.html', '--tokens', tokens, '--asset-base', self.out, '--assets-root', self.root / 'dc-app', '--asset-manifest', self.root / 'dc-images.json', '--meta', self.root / 'meta.json')
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((self.root / 'dc-images.json').read_text())
        self.assertTrue(manifest['source_ready'], manifest)
        self.assertEqual(len(manifest['images']), 2)

    def test_extensionless_frozen_html_and_css_are_read_by_manifest_kind(self):
        self.put('login', '<link rel="stylesheet" href="styles"><img src="images/logo.png">')
        self.put('styles', '.x {background:url(images/background.png)}')
        self.put('images/logo.png', png())
        self.put('images/background.png', png(b'\0\xff\0'))
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *_args):
                pass
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(self.source)))
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        result = self.run_cli('freeze_design.py', f'http://127.0.0.1:{server.server_port}/login', '--out', self.out)
        self.assertEqual(result.returncode, 0, result.stderr)
        shutil.rmtree(self.source)
        result = self.run_cli('fetch_images.py', self.out, '--asset-base', self.out, '--assets-root', self.app, '--out', self.root / 'images.json')
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((self.root / 'images.json').read_text())
        self.assertTrue(manifest['source_ready'], manifest)
        self.assertEqual(len(manifest['images']), 2)

    def test_sibling_manifest_is_supported_and_explicit_missing_manifest_fails(self):
        self.put('screen.html', '<img src="logo.png">')
        self.put('logo.png', png())
        path = self.root / 'source-manifest.json'
        result = self.freeze('screen.html', '--manifest', path)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli('fetch_images.py', self.out, '--asset-base', self.out, '--assets-root', self.app, '--source-manifest', path, '--out', self.root / 'images.json')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads((self.root / 'images.json').read_text())['source_ready'])
        missing = self.run_cli('fetch_images.py', self.out, '--assets-root', self.app, '--source-manifest', self.root / 'missing.json', '--out', self.root / 'images.json')
        self.assertNotEqual(missing.returncode, 0)

    def test_missing_dependency_is_unready_and_can_be_retried(self):
        self.put('screen.html', '<script src="missing.js"></script>')
        failed = self.freeze()
        self.assertNotEqual(failed.returncode, 0)
        self.assertTrue((self.out / 'source-manifest.json').exists(), failed.stderr)
        manifest = json.loads((self.out / 'source-manifest.json').read_text())
        self.assertFalse(manifest['source_ready'])
        self.assertEqual(len([i for i in manifest['files'] if i['status'] == 'failed']), 1)
        self.put('missing.js', 'const supported = true;')
        self.assertEqual(self.freeze().returncode, 0)

    def test_freeze_refuses_source_escape_and_existing_collision(self):
        (self.root / 'private.css').write_text('secret')
        self.put('screen.html', '<link href="../private.css" rel="stylesheet">')
        result = self.freeze()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.out / 'source-manifest.json').exists(), result.stderr)
        self.assertFalse((self.out / 'private.css').exists())
        self.put('screen.html', '<p>new source</p>')
        before = (self.out / 'screen.html').read_bytes()
        self.assertNotEqual(self.freeze().returncode, 0)
        self.assertEqual((self.out / 'screen.html').read_bytes(), before)

    def test_images_resolve_per_document_and_css_assets_are_ingested(self):
        self.put('a/screen.html', '<img src="logo.png">')
        self.put('b/screen.html', '<img src="logo.png">')
        self.put('a/logo.png', png())
        self.put('b/logo.png', png())
        self.put('style.css', '.a {background: url(a/logo.png)}')
        manifest = self.fetch()
        self.assertTrue(manifest.get('source_ready'), manifest)
        self.assertEqual(len(manifest['images']), 2)
        self.assertEqual(len(list(self.app.rglob('*.png'))), 2)

    def test_app_image_destination_symlink_cannot_escape_app(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.app / 'web/static').mkdir(parents=True)
        (self.app / 'web/static/images').symlink_to(outside, target_is_directory=True)
        self.put('screen.html', '<img src="logo.png">')
        self.put('logo.png', png())
        manifest = self.fetch()
        self.assertFalse(manifest.get('source_ready'), manifest)
        self.assertEqual(list(outside.iterdir()), [])

    def test_component_literal_image_is_relative_to_document_but_module_import_is_relative_to_component(self):
        self.put('screen.html', '<x-import from="components/Panel.jsx"></x-import>')
        self.put('components/Panel.jsx', 'import badge from "./badge.png"; export default () => <img src="images/logo.png"/>;')
        self.put('images/logo.png', png())
        self.put('components/badge.png', png())
        result = self.freeze()
        self.assertEqual(result.returncode, 0, result.stderr)
        files = json.loads((self.out / 'source-manifest.json').read_text())['files']
        self.assertEqual({i['local_path'] for i in files if i['kind'] == 'image'}, {'images/logo.png', 'components/badge.png'})

    def test_es_scanner_ignores_fake_imports_and_collects_real_forms_and_inline_modules(self):
        self.put('screen.html', '''<script type="module">
          const fake = "import './fake-inline.js'";
          import './inline.js';
        </script>''')
        self.put('inline.js', 'export { value } from "./value.js";')
        self.put('value.js', 'export const value = 1;')
        result = self.freeze()
        self.assertEqual(result.returncode, 0, result.stderr)
        paths = {row['local_path'] for row in json.loads((self.out / 'source-manifest.json').read_text())['files']}
        self.assertEqual(paths, {'screen.html', 'inline.js', 'value.js'})

    def test_nonliteral_and_bare_imports_and_jsx_src_expressions_block_freeze(self):
        self.put('screen.html', '<x-import from="Panel.jsx"></x-import>')
        self.put('Panel.jsx', '''
          import React from "react";
          import("./" + name);
          export default () => <img src={assetPath}/>;
        ''')
        result = self.freeze()
        self.assertNotEqual(result.returncode, 0)
        manifest = json.loads((self.out / 'source-manifest.json').read_text())
        reasons = '\n'.join(row['reason'] for row in manifest['files'] if row['status'] == 'failed')
        self.assertIn('bare module', reasons)
        self.assertIn('non-literal import', reasons)
        self.assertIn('JSX resource expression', reasons)

    def test_http_html_error_mime_is_not_accepted_as_stylesheet(self):
        self.put('screen.html', '<link rel="stylesheet" href="error.css">')
        self.put('error.css', '<h1>Temporarily unavailable</h1>')
        class ErrorPage(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *_args):
                pass
            def guess_type(self, path):
                return 'text/html' if str(path).endswith('.css') else super().guess_type(path)
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(ErrorPage, directory=str(self.source)))
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        result = self.run_cli('freeze_design.py', f'http://127.0.0.1:{server.server_port}/screen.html', '--out', self.out)
        self.assertNotEqual(result.returncode, 0)
        manifest = json.loads((self.out / 'source-manifest.json').read_text())
        self.assertFalse(manifest['source_ready'])
        self.assertEqual([i['status'] for i in manifest['files'] if i['kind'] == 'css'], ['failed'])

    def test_http_redirect_uses_final_document_base(self):
        self.put('nested/screen.html', '<link rel="stylesheet" href="style.css">')
        self.put('nested/style.css', '.a{color:green}')
        class Redirect(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *_args):
                pass
            def do_GET(self):
                if self.path == '/start':
                    self.send_response(302)
                    self.send_header('Location', '/nested/screen.html')
                    self.end_headers()
                else:
                    super().do_GET()
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Redirect, directory=str(self.source)))
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        result = self.run_cli('freeze_design.py', f'http://127.0.0.1:{server.server_port}/start', '--out', self.out)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((self.out / 'source-manifest.json').read_text())
        self.assertTrue(manifest['source_ready'])
        self.assertTrue(any(i['source'].endswith('/nested/style.css') and i['status'] == 'ok' for i in manifest['files']))

    def test_http_css_and_image_response_validation(self):
        self.put('screen.html', '<link rel="stylesheet" href="style.css"><img src="good.png">')
        self.put('style.css', '.a{color:blue}')
        self.put('good.png', png())
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *_args):
                pass
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(self.source)))
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f'http://127.0.0.1:{server.server_port}/screen.html'
        result = self.run_cli('freeze_design.py', url, '--out', self.out)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads((self.out / 'source-manifest.json').read_text())['source_ready'])
        # The source server may be gone: app ingestion must use the frozen URL mapping.
        self.put('good.png', b'')
        result = self.run_cli('fetch_images.py', self.out, '--assets-root', self.app, '--asset-base', self.out, '--out', self.root / 'http-images.json')
        self.assertEqual(result.returncode, 0, result.stderr)
        images = json.loads((self.root / 'http-images.json').read_text())
        self.assertTrue(images.get('source_ready'), images)
        self.assertEqual(len(images['images']), 1)
        self.assertEqual((self.app / images['images'][0]['local_path']).read_bytes(), png())
        self.put('good.png', '<html>200 Error</html>')
        failure = self.run_cli('freeze_design.py', url, '--out', self.root / 'http-failure')
        self.assertNotEqual(failure.returncode, 0)
        bad = json.loads((self.root / 'http-failure/source-manifest.json').read_text())
        self.assertFalse(bad['source_ready'])
        self.assertEqual([i['status'] for i in bad['files'] if i['kind'] == 'image'], ['failed'])


if __name__ == '__main__':
    unittest.main()
