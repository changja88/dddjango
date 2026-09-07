#!/usr/bin/env python3
"""Adversarial fixtures for the design evidence gate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

SCRIPTS = Path(__file__).resolve().parents[1]


def png(pixel=b'\xff\0\0'):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b'\0' + pixel)) + chunk(b'IEND', b'')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.reference = self.root / 'build' / 'design-ref'
        self.build = self.root / 'build'
        self.project = self.root / 'project'
        self.source.mkdir()
        (self.project / 'web').mkdir(parents=True)
        (self.project / 'web/app.js').write_text('const ready = true;')
        (self.source / 'screen.html').write_text('<script type="module" src="app.js"></script><img src="logo.png">')
        (self.source / 'app.js').write_text('import "./support.js";')
        (self.source / 'support.js').write_text('export const ok = true;')
        (self.source / 'logo.png').write_bytes(png())
        result = subprocess.run([sys.executable, str(SCRIPTS / 'freeze_design.py'), self.source / 'screen.html', '--out', self.reference], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        (self.build / 'scope.md').write_text('screen: login\n')
        (self.build / 'coverage-review.md').write_text('reviewed: login\n')
        (self.build / 'original.png').write_bytes(png())
        self.write_input()

    def ptr(self, path):
        return {'path': str(Path(path).relative_to(self.build)), 'sha256': digest(path)}

    def write_input(self, cases=None, manifests=None, host_files=None):
        entry = self.reference / 'screen.html'
        data = {
            'version': 1,
            'reference_root': 'design-ref',
            'manifests': manifests or ['design-ref/source-manifest.json'],
            'scope': self.ptr(self.build / 'scope.md'),
            'coverage_review': self.ptr(self.build / 'coverage-review.md'),
            'cases': cases or [{
                'id': 'login/default', 'screen': 'login', 'state': 'default',
                'viewport': [1280, 720], 'scope_refs': ['scope.md#login'],
                'entrypoint': {'path': 'screen.html', 'sha256': digest(entry)},
                'reference_capture': self.ptr(self.build / 'original.png'),
            }],
        }
        if host_files is not None:
            data['host_files'] = host_files
        (self.build / 'design-input.json').write_text(json.dumps(data, indent=2) + '\n')

    def run_gate(self, phase='inputs', fingerprint=False, build=None):
        args = [sys.executable, str(SCRIPTS / 'check_design_evidence.py'), '--build', build or self.build,
                '--project-root', self.project, '--phase', phase]
        if fingerprint:
            args.append('--fingerprint')
        return subprocess.run(args, capture_output=True, text=True, timeout=10)

    def fingerprint(self):
        result = self.run_gate('visual', True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def write_visual(self, result='pass', viewport=(1280, 720), media=None, same_file=False):
        (self.build / 'visual-check.md').write_text('Compared directly with the original.\n')
        capture = self.build / 'original.png' if same_file else self.build / 'implementation.png'
        if not same_file:
            capture.write_bytes(png())
        values = self.fingerprint()
        row = {'id': 'login/default', 'url': 'http://127.0.0.1/login', 'viewport': list(viewport),
               'capture': self.ptr(capture), 'result': result}
        if media is not None:
            row['media'] = media
        evidence = {'version': 1, **values, 'visual_check': self.ptr(self.build / 'visual-check.md'), 'cases': [row]}
        (self.build / 'visual-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')

    def test_complete_static_inputs_and_visual_capture_pass(self):
        self.assertEqual(self.run_gate().returncode, 0, self.run_gate().stderr)
        self.write_visual()
        result = self.run_gate('visual')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_image_only_and_multiple_entrypoints_pass(self):
        second_source = self.root / 'second-source'
        second_source.mkdir()
        (second_source / 'image2.png').write_bytes(png(b'\0\xff\0'))
        second_manifest = self.build / 'image-source-manifest.json'
        result = subprocess.run([sys.executable, str(SCRIPTS / 'freeze_design.py'), second_source / 'image2.png',
                                 '--out', self.reference, '--manifest', second_manifest], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        cases = json.loads((self.build / 'design-input.json').read_text())['cases']
        cases.append({'id': 'art/still', 'screen': 'art', 'state': 'still', 'viewport': [640, 480],
                      'scope_refs': ['scope.md#art'],
                      'entrypoint': {'path': 'image2.png', 'sha256': digest(self.reference / 'image2.png')},
                      'reference_capture': self.ptr(self.build / 'original.png')})
        self.write_input(cases, ['design-ref/source-manifest.json', 'image-source-manifest.json'])
        self.assertEqual(self.run_gate().returncode, 0, self.run_gate().stderr)

    def test_manifest_hash_dependency_and_render_tampering_fail(self):
        manifest_path = self.reference / 'source-manifest.json'
        original = json.loads(manifest_path.read_text())
        for mutation in ('hash', 'dependency', 'render'):
            manifest = json.loads(json.dumps(original))
            if mutation == 'hash':
                next(row for row in manifest['files'] if row['local_path'] == 'screen.html')['sha256'] = '0' * 64
                manifest_path.write_text(json.dumps(manifest))
            elif mutation == 'dependency':
                manifest['files'] = [row for row in manifest['files'] if row['local_path'] != 'support.js']
                manifest_path.write_text(json.dumps(manifest))
            else:
                (self.build / 'original.png').unlink()
            result = self.run_gate()
            self.assertEqual(result.returncode, 2, (mutation, result.stdout, result.stderr))
            manifest_path.write_text(json.dumps(original))
            if mutation == 'render':
                (self.build / 'original.png').write_bytes(png())
            self.write_input()

    def freeze_nested_components(self, absolute_image=False):
        (self.source / 'components/styles').mkdir(parents=True)
        (self.source / 'images').mkdir()
        (self.source / 'index.html').write_text('<x-import from="components/Outer.jsx"></x-import>')
        (self.source / 'components/Outer.jsx').write_text('import Inner from "./Inner.jsx"; import "./styles/base.css";')
        image_source = str(self.source / 'images/logo.png') if absolute_image else 'images/logo.png'
        (self.source / 'components/Inner.jsx').write_text(
            f'import badge from "./badge.png"; export default () => <img src="{image_source}"/>;')
        (self.source / 'components/styles/base.css').write_text('@import "theme.css"; .a {background:url(background.png)}')
        (self.source / 'components/styles/theme.css').write_text('.a {color: navy}')
        for name in ('images/logo.png', 'components/badge.png', 'components/styles/background.png'):
            (self.source / name).write_bytes(png())
        result = subprocess.run([sys.executable, str(SCRIPTS / 'freeze_design.py'), self.source / 'index.html',
                                 '--out', self.reference], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = json.loads((self.reference / 'source-manifest.json').read_text())
        self.assertIs(manifest['source_ready'], True)
        self.assertEqual({row['local_path'] for row in manifest['files']}, {
            'index.html', 'components/Outer.jsx', 'components/Inner.jsx', 'images/logo.png',
            'components/badge.png', 'components/styles/base.css', 'components/styles/theme.css',
            'components/styles/background.png',
        })
        case = json.loads((self.build / 'design-input.json').read_text())['cases'][0]
        case['entrypoint'] = {'path': 'index.html', 'sha256': digest(self.reference / 'index.html')}
        self.write_input([case])
        return manifest

    def test_nested_component_document_assets_and_file_relative_imports_pass(self):
        self.freeze_nested_components()
        shutil.rmtree(self.source)
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_nested_component_deleted_dependencies_and_manifest_entries_fail(self):
        original = self.freeze_nested_components()
        manifest_path = self.reference / 'source-manifest.json'
        dependencies = {
            'images/logo.png': 'images/logo.png',
            'components/Inner.jsx': './Inner.jsx',
            'components/badge.png': './badge.png',
            'components/styles/base.css': './styles/base.css',
            'components/styles/theme.css': 'theme.css',
            'components/styles/background.png': 'background.png',
        }
        for name, reference in dependencies.items():
            frozen = self.reference / name
            data = frozen.read_bytes()
            for mutation in ('file', 'entry', 'both'):
                with self.subTest(dependency=name, mutation=mutation):
                    manifest = json.loads(json.dumps(original))
                    if mutation in ('file', 'both'):
                        frozen.unlink()
                    if mutation in ('entry', 'both'):
                        manifest['files'] = [row for row in manifest['files'] if row['local_path'] != name]
                    manifest_path.write_text(json.dumps(manifest))
                    result = self.run_gate()
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    if mutation == 'file':
                        self.assertIn('missing path', result.stderr)
                    else:
                        self.assertIn(f'dependency absent from manifest: {reference!r}', result.stderr)
                    frozen.write_bytes(data)
                    manifest_path.write_text(json.dumps(original))

    def test_nested_component_malformed_or_cyclic_document_provenance_fails(self):
        original = self.freeze_nested_components(absolute_image=True)
        manifest_path = self.reference / 'source-manifest.json'
        for mutation in ('missing', 'empty', 'unknown', 'type', 'self-cycle', 'ancestor-cycle'):
            with self.subTest(provenance=mutation):
                manifest = json.loads(json.dumps(original))
                inner = next(row for row in manifest['files'] if row['local_path'] == 'components/Inner.jsx')
                outer = next(row for row in manifest['files'] if row['local_path'] == 'components/Outer.jsx')
                if mutation == 'missing':
                    del outer['source_document']
                elif mutation == 'empty':
                    outer['source_document'] = ''
                elif mutation == 'unknown':
                    outer['source_document'] = str(self.source / 'missing.jsx')
                elif mutation == 'type':
                    outer['source_document'] = []
                elif mutation == 'self-cycle':
                    inner['source_document'] = inner['source']
                else:
                    outer['source_document'] = inner['source']
                manifest_path.write_text(json.dumps(manifest))
                result = self.run_gate()
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn('document provenance', result.stderr)

    def freeze_nested_html_components(self):
        files = {
            'index.html': '<iframe src="pages/frame.html"></iframe>',
            'pages/frame.html': '<iframe src="nested/preview.html"></iframe>',
            'pages/nested/preview.html': (
                '<x-import from="../../components/Outer.jsx"></x-import>'
                '<iframe src="../../index.html"></iframe>'),
            'components/Outer.jsx': 'import Inner from "./Inner.jsx";',
            'components/Inner.jsx': 'import badge from "./badge.png"; export default () => <img src="images/logo.png"/>;',
            'components/badge.png': png(),
            'pages/nested/images/logo.png': png(),
        }
        for name, data in files.items():
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data.encode() if isinstance(data, str) else data)
        result = subprocess.run([sys.executable, str(SCRIPTS / 'freeze_design.py'), self.source / 'index.html',
                                 '--out', self.reference], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = json.loads((self.reference / 'source-manifest.json').read_text())
        self.assertIs(manifest['source_ready'], True)
        self.assertEqual({row['local_path'] for row in manifest['files']}, set(files))
        case = json.loads((self.build / 'design-input.json').read_text())['cases'][0]
        case['entrypoint'] = {'path': 'index.html', 'sha256': digest(self.reference / 'index.html')}
        self.write_input([case])
        return manifest

    def test_nested_html_document_origin_and_dependency_cycles_pass(self):
        manifest = self.freeze_nested_html_components()
        rows = {row['local_path']: row for row in manifest['files']}
        chain = ['components/Inner.jsx', 'components/Outer.jsx', 'pages/nested/preview.html',
                 'pages/frame.html', 'index.html']
        for child, parent in zip(chain, chain[1:]):
            self.assertEqual(rows[child]['source_document'], rows[parent]['source'])
        self.assertEqual(rows['index.html']['source_document'], '')
        self.assertFalse((self.reference / 'images/logo.png').exists())
        shutil.rmtree(self.source)
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_nested_html_invalid_importer_ancestry_fails(self):
        original = self.freeze_nested_html_components()
        manifest_path = self.reference / 'source-manifest.json'
        for name in ('pages/nested/preview.html', 'pages/frame.html', 'index.html'):
            for mutation in ('missing', 'empty', 'unknown', 'type', 'self-cycle', 'component-cycle'):
                if name == 'index.html' and mutation == 'empty':
                    continue  # The manifest entrypoint is the only valid empty importer.
                with self.subTest(ancestor=name, provenance=mutation):
                    manifest = json.loads(json.dumps(original))
                    row = next(row for row in manifest['files'] if row['local_path'] == name)
                    if mutation == 'missing':
                        del row['source_document']
                    elif mutation == 'empty':
                        row['source_document'] = ''
                    elif mutation == 'unknown':
                        row['source_document'] = str(self.source / 'missing.html')
                    elif mutation == 'type':
                        row['source_document'] = []
                    elif mutation == 'self-cycle':
                        row['source_document'] = row['source']
                    else:
                        row['source_document'] = str(self.source / 'components/Inner.jsx')
                    manifest_path.write_text(json.dumps(manifest))
                    result = self.run_gate()
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertIn('document provenance', result.stderr)
        with self.subTest(provenance='deleted-importer-row'):
            manifest = json.loads(json.dumps(original))
            manifest['files'] = [row for row in manifest['files'] if row['local_path'] != 'pages/frame.html']
            manifest_path.write_text(json.dumps(manifest))
            result = self.run_gate()
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn('document provenance importer absent from manifest', result.stderr)

    def test_standalone_component_document_origin_passes(self):
        self.freeze_nested_components()
        (self.source / 'components/images').mkdir()
        (self.source / 'components/images/logo.png').write_bytes(png())
        result = subprocess.run([sys.executable, str(SCRIPTS / 'freeze_design.py'), self.source / 'components/Outer.jsx',
                                 '--source-root', self.source, '--out', self.reference], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = json.loads((self.reference / 'source-manifest.json').read_text())
        self.assertIs(manifest['source_ready'], True)
        self.assertFalse(any(row['kind'] == 'html' for row in manifest['files']))
        self.assertIn('components/images/logo.png', {row['local_path'] for row in manifest['files']})
        case = json.loads((self.build / 'design-input.json').read_text())['cases'][0]
        case['entrypoint'] = {'path': 'components/Outer.jsx', 'sha256': digest(self.reference / 'components/Outer.jsx')}
        self.write_input([case])
        shutil.rmtree(self.source)
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_case_set_viewport_and_code_freshness_are_enforced(self):
        self.write_visual()
        visual = json.loads((self.build / 'visual-evidence.json').read_text())
        visual['cases'][0]['viewport'] = [800, 600]
        (self.build / 'visual-evidence.json').write_text(json.dumps(visual))
        self.assertEqual(self.run_gate('visual').returncode, 2)
        self.write_visual()
        (self.project / 'web/new.css').write_text('body{}')
        self.assertEqual(self.run_gate('visual').returncode, 2)
        (self.project / 'web/new.css').unlink()
        (self.project / 'web/app.js').write_text('const changed = true;')
        self.assertEqual(self.run_gate('visual').returncode, 2)
        self.write_visual()
        (self.project / 'web/app.js').unlink()
        self.assertEqual(self.run_gate('visual').returncode, 2)

    def test_closed_cache_exclusions_do_not_stale_visual(self):
        self.write_visual()
        (self.project / 'web/__pycache__').mkdir()
        (self.project / 'web/__pycache__/x.pyc').write_bytes(b'cache')
        (self.project / 'web/.DS_Store').write_bytes(b'meta')
        self.assertEqual(self.run_gate('visual').returncode, 0, self.run_gate('visual').stderr)

    def test_empty_duplicate_missing_and_unverified_cases_fail(self):
        data = json.loads((self.build / 'design-input.json').read_text())
        data['cases'] = []
        (self.build / 'design-input.json').write_text(json.dumps(data))
        self.assertEqual(self.run_gate().returncode, 2)
        self.write_input()
        self.write_visual('unverified')
        self.assertEqual(self.run_gate('visual').returncode, 2)
        self.write_visual()
        visual = json.loads((self.build / 'visual-evidence.json').read_text())
        visual['cases'].append(visual['cases'][0])
        (self.build / 'visual-evidence.json').write_text(json.dumps(visual))
        self.assertEqual(self.run_gate('visual').returncode, 2)

    def test_original_capture_same_file_or_hardlink_is_rejected_but_equal_copy_is_allowed(self):
        self.write_visual(same_file=True)
        self.assertEqual(self.run_gate('visual').returncode, 2)
        hardlink = self.build / 'implementation.png'
        hardlink.hardlink_to(self.build / 'original.png')
        self.write_visual()
        self.assertEqual(self.run_gate('visual').returncode, 2)
        hardlink.unlink()
        shutil.copyfile(self.build / 'original.png', hardlink)
        self.write_visual()
        self.assertEqual(self.run_gate('visual').returncode, 0, self.run_gate('visual').stderr)

    def write_two_case_visual(self, capture_kind):
        originals = [self.build / 'original.png', self.build / 'second-original.png']
        originals[1].write_bytes(png())
        self.assertFalse(originals[0].samefile(originals[1]))
        cases = json.loads((self.build / 'design-input.json').read_text())['cases']
        second = dict(cases[0], id='login/error', state='error', reference_capture=self.ptr(originals[1]))
        cases.append(second)
        self.write_input(cases)
        (self.build / 'visual-check.md').write_text('Compared both cases directly with their originals.\n')
        rows = []
        for index, case in enumerate(cases):
            original = originals[1 - index]
            capture = self.build / f'implementation-{index}.png'
            if capture_kind == 'direct':
                capture = original
            elif capture_kind == 'hardlink':
                capture.hardlink_to(original)
                self.assertTrue(capture.samefile(original))
            else:
                shutil.copyfile(original, capture)
                self.assertEqual(capture.read_bytes(), original.read_bytes())
                self.assertTrue(all(not capture.samefile(path) for path in originals))
            rows.append({'id': case['id'], 'url': 'http://127.0.0.1/login', 'viewport': case['viewport'],
                         'capture': self.ptr(capture), 'result': 'pass'})
        evidence = {'version': 1, **self.fingerprint(), 'visual_check': self.ptr(self.build / 'visual-check.md'),
                    'cases': rows}
        (self.build / 'visual-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')

    def test_cross_case_original_capture_direct_reuse_fails(self):
        self.write_two_case_visual('direct')
        result = self.run_gate('visual')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stderr.count('original file/hardlink reuse forbidden'), 2)

    def test_cross_case_original_capture_hardlink_reuse_fails(self):
        self.write_two_case_visual('hardlink')
        result = self.run_gate('visual')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stderr.count('original file/hardlink reuse forbidden'), 2)

    def test_two_case_independent_equal_bytes_captures_pass(self):
        self.write_two_case_visual('copy')
        result = self.run_gate('visual')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_media_response_browser_chain_passes_and_mutations_fail(self):
        requirement = {'id': 'hero', 'kind': 'video', 'environment': 'staging', 'endpoint': '/api/media/hero',
                       'identity_pointer': '/asset/id', 'source_pointer': '/asset/src'}
        case = json.loads((self.build / 'design-input.json').read_text())['cases'][0]
        case['media'] = [requirement]
        self.write_input([case])
        response_path = self.build / 'response.json'
        browser_path = self.build / 'browser.json'
        response = {'observed_at': '2026-09-06T12:00:00Z', 'environment': 'staging', 'endpoint': '/api/media/hero',
                    'status': 200, 'body': {'asset': {'id': 'hero-42', 'src': 'https://cdn.test/hero.mp4'}}}
        browser = {'observed_at': '2026-09-06T12:00:01Z', 'current_src': 'https://cdn.test/hero.mp4',
                   'status': 206, 'loaded': True, 'playback_start': 0.0, 'playback_end': 1.25}
        response_path.write_text(json.dumps(response)); browser_path.write_text(json.dumps(browser))
        media = [{'requirement_id': 'hero', 'response': self.ptr(response_path), 'browser': self.ptr(browser_path)}]
        self.write_visual(media=media)
        self.assertEqual(self.run_gate('visual').returncode, 0, self.run_gate('visual').stderr)
        self.write_visual(media=[])
        self.assertEqual(self.run_gate('visual').returncode, 2, 'missing media row')
        self.write_visual(media=media + media)
        self.assertEqual(self.run_gate('visual').returncode, 2, 'duplicate media row')
        for key in ('api', 'identity', 'src', 'stopped'):
            bad_response, bad_browser = dict(response), dict(browser)
            bad_response['body'] = json.loads(json.dumps(response['body']))
            if key == 'api': bad_response['status'] = 500
            if key == 'identity': bad_response['body']['asset'].pop('id')
            if key == 'src': bad_browser['current_src'] = 'https://samples.test/flower.mp4'
            if key == 'stopped': bad_browser['playback_end'] = 0.0
            response_path.write_text(json.dumps(bad_response)); browser_path.write_text(json.dumps(bad_browser))
            media = [{'requirement_id': 'hero', 'response': self.ptr(response_path), 'browser': self.ptr(browser_path)}]
            self.write_visual(media=media)
            self.assertEqual(self.run_gate('visual').returncode, 2, key)

    def test_fingerprint_does_not_modify_evidence_files(self):
        self.write_visual()
        before = (self.build / 'visual-evidence.json').read_bytes()
        result = self.run_gate('visual', True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.build / 'visual-evidence.json').read_bytes(), before)

    def test_directory_symlink_is_rejected_from_implementation_digest(self):
        shared = self.project / 'shared'
        shared.mkdir()
        (shared / 'asset.js').write_text('before')
        (self.project / 'web/assets').symlink_to(shared, target_is_directory=True)
        result = self.run_gate('visual', True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('directory symlink', result.stderr)

    def test_json_pointer_array_indexes_are_canonical_but_object_keys_remain_literal(self):
        sys.path.insert(0, str(SCRIPTS))
        from check_design_evidence import json_pointer
        document = {'a': ['zero', 'one'], 'object': {'01': 'literal', '-1': 'also-literal'}}
        for invalid in ('-1', '+1', '01'):
            issues = []
            self.assertIsNone(json_pointer(document, f'/a/{invalid}', 'pointer', issues))
            self.assertTrue(issues, invalid)
        issues = []
        self.assertEqual(json_pointer(document, '/a/1', 'pointer', issues), 'one')
        self.assertEqual(json_pointer(document, '/object/01', 'pointer', issues), 'literal')
        self.assertEqual(json_pointer(document, '/object/-1', 'pointer', issues), 'also-literal')
        self.assertEqual(issues, [])

    def test_backstop_only_cannot_disable_design_gate(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / 'backstop.py'), self.project,
                                 '--all', '--only', 'zz', '--design-build', self.root / 'missing-build'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('[DESIGN] BLOCKER', result.stdout)


if __name__ == '__main__':
    unittest.main()
