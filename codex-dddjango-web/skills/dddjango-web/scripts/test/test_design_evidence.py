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
        return subprocess.run(args, capture_output=True, text=True)

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
