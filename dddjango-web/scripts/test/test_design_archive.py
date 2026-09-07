#!/usr/bin/env python3
"""Source archives must preserve originals without pretending to execute JSX."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_design_evidence import png

SCRIPTS = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'export'
        self.source.mkdir()
        self.build = self.root / 'build'
        self.build.mkdir()
        self.ref = self.build / 'design-ref'
        self.manifest = self.build / 'source-manifest.json'
        (self.source / 'screen.dc.html').write_text('<script src="support.js"></script><x-import from="Logo.jsx" component="Logo"></x-import>')
        (self.source / 'support.js').write_text('window.runtime = true;')
        (self.source / 'Logo.jsx').write_text('export function Logo({src}) { return <img src={src} />; }')
        (self.source / 'logo.png').write_bytes(png())
        (self.source / '.DS_Store').write_bytes(b'metadata')
        self.project = self.root / 'app'
        (self.project / 'web').mkdir(parents=True)

    def archive(self):
        return subprocess.run([sys.executable, str(SCRIPTS / 'archive_design.py'),
                               str(self.source / 'screen.dc.html'), '--source-root', str(self.source),
                               '--out', str(self.ref), '--manifest', str(self.manifest)],
                              capture_output=True, text=True)

    def pointer(self, path, root=None):
        return {'path': path.relative_to(root or self.build).as_posix(), 'sha256': sha(path)}

    def prepare(self):
        result = self.archive()
        self.assertEqual(result.returncode, 0, result.stderr)
        (self.build / 'scope.md').write_text('Original export, login/default at 390x844.\n')
        (self.build / 'original.png').write_bytes(png())
        (self.build / 'browser-trace.json').write_text(json.dumps({'url': 'http://127.0.0.1:9000/screen.dc.html',
            'viewport': [390, 844], 'selector': '[data-screen]', 'text': 'Login',
            'images': [{'currentSrc': 'http://127.0.0.1:9000/logo.png', 'complete': True, 'naturalWidth': 1}],
            'fonts': [{'family': 'system-ui', 'status': 'loaded'}], 'failures': []}))
        entry = self.pointer(self.ref / 'screen.dc.html', self.ref)
        self.observation = {'version': 1, 'archive_sha256': sha(self.manifest),
            'entrypoint': entry, 'case_id': 'login/default', 'screen': 'login', 'state': 'default',
            'viewport': [390, 844], 'url': 'http://127.0.0.1:9000/screen.dc.html',
            'observed_at': '2026-09-07T03:30:00Z', 'capture': self.pointer(self.build / 'original.png'),
            'trace': self.pointer(self.build / 'browser-trace.json')}
        self.write_observation()
        self.spec = {'version': 1, 'reference_root': 'design-ref', 'manifests': ['source-manifest.json'],
            'scope': self.pointer(self.build / 'scope.md'), 'coverage_review': None,
            'cases': [{'id': 'login/default', 'screen': 'login', 'state': 'default',
                'viewport': [390, 844], 'scope_refs': ['scope.md#login'], 'entrypoint': entry,
                'reference_capture': self.pointer(self.build / 'original.png'),
                'source_observation': self.pointer(self.build / 'observation.json')}]}
        self.write_spec()
        ready = self.gate('prepare')
        self.assertEqual(ready.returncode, 0, ready.stderr)

    def write_observation(self):
        (self.build / 'observation.json').write_text(json.dumps(self.observation))

    def write_spec(self):
        (self.build / 'design-input.json').write_text(json.dumps(self.spec))

    def gate(self, phase='inputs'):
        return subprocess.run([sys.executable, str(SCRIPTS / 'check_design_evidence.py'),
            '--build', str(self.build), '--project-root', str(self.project), '--phase', phase],
            capture_output=True, text=True)

    def review(self):
        result = self.gate('prepare')
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)['review_digest']
        (self.build / 'coverage-review.md').write_text(f'reviewed-input: {value}\nreview-result: pass\nObserved the original and compared scope.\n')
        self.spec['coverage_review'] = self.pointer(self.build / 'coverage-review.md')
        self.write_spec()

    def test_archive_preserves_all_bytes_without_claiming_static_closure(self):
        result = self.archive()
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads(self.manifest.read_text())
        self.assertEqual(manifest['collection'], 'archive')
        self.assertIs(manifest['source_ready'], False)
        self.assertIs(manifest['archive_ready'], True)
        self.assertEqual({r['local_path'] for r in manifest['files']},
                         {'screen.dc.html', 'support.js', 'Logo.jsx', 'logo.png'})
        for row in manifest['files']:
            self.assertEqual((self.source / row['local_path']).read_bytes(), (self.ref / row['local_path']).read_bytes())

    def test_archive_rejects_symlinks_and_output_inside_source(self):
        (self.source / 'escape').symlink_to(self.root)
        result = self.archive()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('symlink', result.stderr)
        (self.source / 'escape').unlink()
        result = subprocess.run([sys.executable, str(SCRIPTS / 'archive_design.py'), str(self.source / 'screen.dc.html'),
            '--source-root', str(self.source), '--out', str(self.source / 'output'), '--manifest', str(self.manifest)],
            capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.source / 'output').exists())

    def test_archive_rejects_collision(self):
        self.assertEqual(self.archive().returncode, 0)
        (self.source / 'support.js').write_text('changed')
        result = self.archive()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.ref / 'support.js').read_text(), 'window.runtime = true;')

    def test_archive_preserves_literal_filenames(self):
        for name, data in [('logo%20x.png', png()), ('logo x.png', png(b'\0\xff\0')),
                           ('notes#one?.txt', b'literal path')]:
            (self.source / name).write_bytes(data)
        result = self.archive()
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ('logo%20x.png', 'logo x.png', 'notes#one?.txt'):
            self.assertEqual((self.source / name).read_bytes(), (self.ref / name).read_bytes())

    def test_archive_preserves_empty_nonentry_files(self):
        (self.source / '.gitkeep').write_bytes(b'')
        self.prepare()
        self.assertEqual((self.ref / '.gitkeep').read_bytes(), b'')

    def test_archive_accepts_entry_with_literal_url_delimiters(self):
        for index, name in enumerate(('screen#one.dc.html', 'screen?one.dc.html')):
            with self.subTest(name=name):
                entry = self.source / name
                entry.write_text('<main>Original</main>')
                result = subprocess.run([sys.executable, str(SCRIPTS / 'archive_design.py'), str(entry),
                    '--source-root', str(self.source), '--out', str(self.build / f'ref-{index}'),
                    '--manifest', str(self.build / f'manifest-{index}.json')], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((self.build / f'ref-{index}' / name).read_bytes(), entry.read_bytes())

    def test_archive_gate_uses_literal_file_suffixes(self):
        for name in ('asset.css#variant.js', 'theme.js?variant.css'):
            (self.source / name).write_text('/* original bytes */')
        self.prepare()
        self.review()
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_archive_uses_one_manifest_for_all_original_entrypoints(self):
        self.prepare()
        entry = self.pointer(self.ref / 'Logo.jsx', self.ref)
        self.spec['cases'][0]['entrypoint'] = entry
        self.observation['entrypoint'] = entry
        self.write_observation()
        self.spec['cases'][0]['source_observation'] = self.pointer(self.build / 'observation.json')
        self.write_spec()
        self.review()
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_archive_rejects_duplicate_inventory_manifests(self):
        self.prepare()
        second = self.build / 'second-manifest.json'
        second.write_bytes(self.manifest.read_bytes())
        self.spec['manifests'].append(second.name)
        self.write_spec()
        result = self.gate('prepare')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('exactly one full-tree archive manifest', result.stderr)

    def test_empty_raw_observation_is_not_browser_evidence(self):
        self.prepare()
        (self.build / 'browser-trace.json').write_text('   \n')
        self.observation['trace'] = self.pointer(self.build / 'browser-trace.json')
        self.write_observation()
        self.spec['cases'][0]['source_observation'] = self.pointer(self.build / 'observation.json')
        self.write_spec()
        self.assertEqual(self.gate('prepare').returncode, 2)

    def test_archive_cannot_turn_an_image_into_an_unobserved_source(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / 'archive_design.py'), str(self.source / 'logo.png'),
            '--source-root', str(self.source), '--out', str(self.ref), '--manifest', str(self.manifest)],
            capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)

    def test_archive_image_case_cannot_bypass_observation(self):
        self.prepare()
        manifest = json.loads(self.manifest.read_text())
        manifest['entrypoint'] = 'logo.png'
        self.manifest.write_text(json.dumps(manifest))
        self.spec['cases'][0]['entrypoint'] = self.pointer(self.ref / 'logo.png', self.ref)
        del self.spec['cases'][0]['source_observation']
        self.write_spec()
        result = self.gate('prepare')
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_archive_with_original_observation_and_current_review_passes(self):
        self.prepare()
        self.review()
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_archive_cannot_pass_without_browser_observation_or_independent_review(self):
        self.prepare()
        self.assertNotEqual(self.gate().returncode, 0)
        del self.spec['cases'][0]['source_observation']
        self.write_spec()
        result = self.gate('prepare')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('source_observation', result.stderr)

    def test_archive_detects_missing_extra_and_modified_files(self):
        self.prepare()
        self.review()
        for mutation in ('extra', 'missing', 'changed'):
            with self.subTest(mutation=mutation):
                target = self.ref / 'Logo.jsx'
                original = target.read_bytes()
                if mutation == 'extra':
                    (self.ref / 'unrecorded.css').write_text('body{color:red}')
                elif mutation == 'missing':
                    target.unlink()
                else:
                    target.write_text('different component')
                self.assertNotEqual(self.gate().returncode, 0)
                if mutation == 'extra':
                    (self.ref / 'unrecorded.css').unlink()
                else:
                    target.write_bytes(original)

    def test_new_source_manifest_does_not_validate_old_observation(self):
        self.prepare()
        manifest = json.loads(self.manifest.read_text())
        (self.ref / 'Logo.jsx').write_text('new source')
        for row in manifest['files']:
            if row['local_path'] == 'Logo.jsx':
                row.update(sha256=sha(self.ref / 'Logo.jsx'), size_bytes=len(b'new source'))
        self.manifest.write_text(json.dumps(manifest))
        result = self.gate('prepare')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('archive_sha256', result.stderr)

    def test_observation_case_capture_viewport_and_trace_cannot_be_swapped(self):
        self.prepare()
        baseline = dict(self.observation)
        for key, value in [('case_id', 'signup/default'), ('viewport', [800, 600]),
                           ('archive_sha256', '0' * 64), ('capture', {'path': 'original.png', 'sha256': '0' * 64}),
                           ('trace', {'path': '../outside.json', 'sha256': '0' * 64})]:
            with self.subTest(key=key):
                self.observation = dict(baseline, **{key: value})
                self.write_observation()
                self.spec['cases'][0]['source_observation'] = self.pointer(self.build / 'observation.json')
                self.write_spec()
                self.assertNotEqual(self.gate('prepare').returncode, 0)

    def test_old_coverage_review_cannot_authorize_new_case_version(self):
        self.prepare()
        self.review()
        self.spec['cases'][0]['scope_refs'].append('scope.md#new-requirement')
        self.write_spec()
        result = self.gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('reviewed-input', result.stderr)


if __name__ == '__main__':
    unittest.main()
