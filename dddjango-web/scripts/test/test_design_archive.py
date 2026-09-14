#!/usr/bin/env python3
"""Source archives must preserve originals without pretending to execute JSX."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_design_evidence import png

SCRIPTS = Path(__file__).resolve().parents[1]
ASSETS = SCRIPTS.parent / 'assets'


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
        self.observation = {'version': 2, 'archive_sha256': sha(self.manifest),
            'entrypoint': entry, 'case_id': 'login/default', 'screen': 'login', 'state': 'default',
            'viewport': [390, 844], 'url': 'http://127.0.0.1:9000/screen.dc.html',
            'observed_at': '2026-09-07T03:30:00Z', 'capture': self.pointer(self.build / 'original.png'),
            'trace': self.pointer(self.build / 'browser-trace.json')}
        self.write_interactions(entry)
        self.spec = {'version': 1, 'reference_root': 'design-ref', 'manifests': ['source-manifest.json'],
            'scope': self.pointer(self.build / 'scope.md'), 'coverage_review': None,
            'cases': [{'id': 'login/default', 'screen': 'login', 'state': 'default',
                'viewport': [390, 844], 'scope_refs': ['scope.md#login'], 'entrypoint': entry,
                'reference_capture': self.pointer(self.build / 'original.png'),
                'reached_by': {'interactions': 'interactions.json', 'step': 'initial'},
                'source_observation': self.pointer(self.build / 'observation.json')}]}
        self.write_spec()
        ready = self.gate('prepare')
        self.assertEqual(ready.returncode, 0, ready.stderr)

    def write_observation(self):
        (self.build / 'observation.json').write_text(json.dumps(self.observation))

    def interactions(self, entry):
        """조작 대상이 없는 원본의 최소 v2 증거(K7) — 잔여·표면 모두 비어 있다."""
        name = entry['path'].rsplit('/', 1)[-1]
        return {
            'version': 1,
            'collector': {'name': 'interaction_audit', 'snippet_sha256': sha(ASSETS / 'interaction_audit.js'),
                          'driver': 'observe_interactions.pw.js',
                          'driver_sha256': sha(ASSETS / 'observe_interactions.pw.js'),
                          'path': 'node', 'capabilities': {'react_props': True, 'cdp_listeners': True}},
            'archive_sha256': sha(self.manifest), 'entrypoint': entry,
            'url': f'http://127.0.0.1:9000/{name}', 'browser_viewport': [390, 844],
            'content_crop': {'x': 0, 'y': 0, 'w': 390, 'h': 844},
            'root': {'selector': '[data-screen]', 'found': True,
                     'fingerprint': {'tag': 'div', 'label': None, 'descendants': 1,
                                     'rect': {'x': 0, 'y': 0, 'w': 390, 'h': 844}}},
            'outside_root': {'count': 0, 'sample': []}, 'excluded_regions': [],
            'served': {name: entry['sha256']}, 'declared': [], 'declared_unmatched': [],
            'observed_at': '2026-09-07T03:30:00Z', 'targets': {},
            'initial': {'inventory': [], 'state_hash': 'state-0', 'surface_key': 'surface-0',
                        'capture': self.pointer(self.build / 'original.png')},
            'steps': [], 'discovery_limits': [], 'partial': False, 'caps_hit': [],
            'environment_error': None,
        }

    def write_interactions(self, entry):
        path = self.build / 'interactions.json'
        path.write_text(json.dumps(self.interactions(entry), ensure_ascii=False), encoding='utf-8')
        self.observation['interactions'] = self.pointer(path)
        self.write_observation()

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

    def test_archive_reports_missing_component_before_observation(self):
        (self.source / 'Logo.jsx').unlink()
        result = self.archive()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('Logo.jsx', result.stderr)
        manifest = json.loads(self.manifest.read_text())
        self.assertIs(manifest['archive_ready'], True)  # Collected bytes remain available for repair.
        self.assertIs(manifest['source_ready'], False)
        missing = [row for row in manifest['dependencies'] if row['status'] == 'missing']
        self.assertEqual([(row['source_document'], row['source']) for row in missing],
                         [('screen.dc.html', 'Logo.jsx')])

    def test_archive_checks_nested_runtime_css_and_font_dependencies(self):
        (self.source / 'support.js').write_text('import "./runtime.js";')
        (self.source / 'runtime.js').write_text('window.originalRuntime = true;')
        (self.source / 'screen.dc.html').write_text(
            '<script src="support.js"></script><link rel="stylesheet" href="theme.css">')
        (self.source / 'theme.css').write_text('@import "nested/fields.css";')
        (self.source / 'nested').mkdir()
        (self.source / 'nested/fields.css').write_text('@font-face{src:url("../fonts/body.woff2")}')
        result = self.archive()
        self.assertEqual(result.returncode, 1, result.stdout)
        manifest = json.loads(self.manifest.read_text())
        edges = manifest['dependencies']
        self.assertIn(('support.js', './runtime.js', 'ok'),
                      [(r['source_document'], r['source'], r['status']) for r in edges])
        self.assertIn(('nested/fields.css', '../fonts/body.woff2', 'missing'),
                      [(r['source_document'], r['source'], r['status']) for r in edges])

    def test_archive_records_dynamic_and_remote_edges_without_claiming_them_acquired(self):
        (self.source / 'support.js').write_text('import "react"; import(runtimePath);')
        (self.source / 'screen.dc.html').write_text(
            '<script src="support.js"></script><script src="https://example.invalid/runtime.js"></script>')
        result = self.archive()
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads(self.manifest.read_text())
        self.assertIs(manifest['source_ready'], False)
        edges = {(r['source'], r['status']) for r in manifest['dependencies']}
        self.assertIn(('{bare module:react}', 'runtime'), edges)
        self.assertIn(('{non-literal import}', 'runtime'), edges)
        self.assertIn(('https://example.invalid/runtime.js', 'external'), edges)

    def test_archive_resolves_component_resources_from_the_html_document(self):
        (self.source / 'pages').mkdir()
        (self.source / 'components').mkdir()
        (self.source / 'pages/logo x.png').write_bytes(png())
        (self.source / 'pages/login.html').write_text(
            '<x-import from="../components/Mark.jsx" component="Mark"></x-import>')
        (self.source / 'components/Mark.jsx').write_text(
            'export function Mark() { return <img src="logo%20x.png?v=2#image" />; }')
        (self.source / 'screen.dc.html').write_text('<iframe src="pages/login.html"></iframe>')
        result = self.archive()
        self.assertEqual(result.returncode, 0, result.stderr)
        edges = json.loads(self.manifest.read_text())['dependencies']
        image = next(r for r in edges if r['source'] == 'logo%20x.png?v=2#image')
        self.assertEqual(image['local_path'], 'pages/logo x.png')
        self.assertEqual(image['status'], 'ok')

    def test_archive_does_not_resolve_local_references_outside_the_export(self):
        (self.root / 'outside.css').write_text('body{color:red}')
        (self.source / 'screen.dc.html').write_text('<link rel="stylesheet" href="../outside.css">')
        result = self.archive()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('escapes', result.stderr)
        self.assertFalse((self.ref / 'outside.css').exists())

    def test_archive_uses_the_first_html_base_href(self):
        (self.source / 'assets').mkdir()
        (self.source / 'assets/logo.png').write_bytes(png())
        (self.source / 'screen.dc.html').write_text(
            '<template><base href="inert/"></template>'
            '<base target="_blank"><base href="assets/"><base href="wrong/">'
            '<img src="logo.png">')
        self.prepare()
        edges = json.loads(self.manifest.read_text())['dependencies']
        self.assertEqual([(r['source'], r['local_path'], r['status']) for r in edges],
                         [('logo.png', 'assets/logo.png', 'ok')])

    def test_archive_base_does_not_accept_a_file_at_the_unbased_path(self):
        (self.source / 'screen.dc.html').write_text('<base href="assets/"><img src="logo.png">')
        result = self.archive()
        self.assertEqual(result.returncode, 1, result.stdout)
        edges = json.loads(self.manifest.read_text())['dependencies']
        self.assertEqual([(r['local_path'], r['status']) for r in edges],
                         [('assets/logo.png', 'missing')])

    def test_archive_propagates_html_base_to_component_resources(self):
        (self.source / 'pages').mkdir()
        (self.source / 'assets').mkdir()
        (self.source / 'components').mkdir()
        (self.source / 'assets/logo.png').write_bytes(png())
        (self.source / 'pages/login.html').write_text(
            '<base href="/assets/"><x-import from="../components/Mark.jsx" component="Mark"></x-import>')
        (self.source / 'components/Mark.jsx').write_text(
            'import "./mark.css"; export function Mark() { return <img src="logo.png" />; }')
        (self.source / 'components/mark.css').write_text('body { color: red; }')
        (self.source / 'screen.dc.html').write_text('<iframe src="pages/login.html"></iframe>')
        result = self.archive()
        self.assertEqual(result.returncode, 0, result.stderr)
        edges = json.loads(self.manifest.read_text())['dependencies']
        self.assertIn(('logo.png', 'assets/logo.png', 'ok'),
                      [(r['source'], r['local_path'], r['status']) for r in edges])
        self.assertIn(('./mark.css', 'components/mark.css', 'ok'),
                      [(r['source'], r['local_path'], r['status']) for r in edges])

    def test_archive_leaves_remote_html_base_resources_for_observation(self):
        (self.source / 'screen.dc.html').write_text(
            '<base href="https://example.invalid/assets/"><img src="remote.png">'
            '<iframe src="local.html"></iframe>')
        (self.source / 'local.html').write_text('<img src="also-missing.png">')
        result = self.archive()
        self.assertEqual(result.returncode, 0, result.stderr)
        edges = json.loads(self.manifest.read_text())['dependencies']
        self.assertEqual([(r['source'], r['status']) for r in edges],
                         [('remote.png', 'external'), ('local.html', 'external')])

    def test_archive_ignores_inert_markup_in_component_strings_and_comments(self):
        (self.source / 'Logo.jsx').write_text('''
const debug = '<img src="missing-string.png">';
const template = `<img src="missing-template.png">`;
const nested = `${`<img src="missing-nested-template.png">`}`;
// <img src="missing-line-comment.png">
/* <img src="missing-block-comment.png"> */
export function Logo({src}) {
  return <div>{/* <img src="missing-jsx-comment.png"> */}
    <img src="logo.png" /><img src={src} />
  </div>;
}
''')
        self.prepare()
        edges = json.loads(self.manifest.read_text())['dependencies']
        self.assertEqual({r['source'] for r in edges if r['status'] == 'ok'},
                         {'support.js', 'Logo.jsx', 'logo.png'})
        self.assertTrue(any(r['status'] == 'runtime' for r in edges))
        self.assertEqual((self.ref / 'Logo.jsx').read_bytes(), (self.source / 'Logo.jsx').read_bytes())

    def test_archive_keeps_real_jsx_images_between_text_apostrophes(self):
        (self.source / 'Logo.jsx').write_text('''
export function Logo() { return <div>It's <img src="missing.png" /> don't forget.</div>; }
''')
        result = self.archive()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('missing.png', result.stderr)

    def test_archive_keeps_interpolated_markup_templates_explicitly_runtime(self):
        (self.source / 'Logo.jsx').write_text('''
const markup = `<img src="${imagePath}">`;
export function Logo() { return <div dangerouslySetInnerHTML={{__html: markup}} />; }
''')
        result = self.archive()
        self.assertEqual(result.returncode, 0, result.stderr)
        edges = json.loads(self.manifest.read_text())['dependencies']
        self.assertTrue(any(r['status'] == 'runtime' for r in edges))

    def test_gate_rechecks_dependencies_even_if_inventory_and_observation_agree(self):
        self.prepare()
        (self.ref / 'Logo.jsx').unlink()
        manifest = json.loads(self.manifest.read_text())
        manifest['files'] = [r for r in manifest['files'] if r['local_path'] != 'Logo.jsx']
        manifest.pop('dependencies', None)  # Old archives had no dependency report.
        self.manifest.write_text(json.dumps(manifest))
        self.observation['archive_sha256'] = sha(self.manifest)
        self.write_observation()
        self.spec['cases'][0]['source_observation'] = self.pointer(self.build / 'observation.json')
        self.write_spec()
        result = self.gate('prepare')
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn('Logo.jsx', result.stderr)

    def test_gate_checks_the_case_entrypoint_not_just_the_archive_entrypoint(self):
        (self.source / 'other.html').write_text('<x-import from="Missing.jsx" component="Other"></x-import>')
        self.prepare()
        entry = self.pointer(self.ref / 'other.html', self.ref)
        self.spec['cases'][0]['entrypoint'] = entry
        self.observation['entrypoint'] = entry
        self.write_observation()
        self.spec['cases'][0]['source_observation'] = self.pointer(self.build / 'observation.json')
        self.write_spec()
        result = self.gate('prepare')
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn('Missing.jsx', result.stderr)

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
        self.write_interactions(entry)
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


class RefreezeCompareTests(unittest.TestCase):
    """K4 재동결 기계 대조(`archive_design.py --compare-build`) 판형 9개."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.build = self.root / 'build'
        self.build.mkdir()
        self.baseline_source = self.root / 'baseline-export'
        self.baseline_source.mkdir()
        (self.baseline_source / 'screen.dc.html').write_text(
            '<script src="support.js"></script><img src="logo.png">')
        (self.baseline_source / 'support.js').write_text('window.runtime = true;')
        (self.baseline_source / 'logo.png').write_bytes(png())
        self.ref = self.build / 'design-ref'
        self.base_manifest = self.build / 'source-manifest.json'
        baseline = self.run_archive(self.baseline_source, self.ref, self.base_manifest)
        self.assertEqual(baseline.returncode, 0, baseline.stderr)
        (self.build / 'design-input.json').write_text(json.dumps(
            {'version': 1, 'reference_root': 'design-ref', 'manifests': ['source-manifest.json']}))

    def run_archive(self, source_root, out, manifest_path, compare_out=None, carried=None):
        args = [sys.executable, str(SCRIPTS / 'archive_design.py'), str(source_root / 'screen.dc.html'),
                '--source-root', str(source_root), '--out', str(out), '--manifest', str(manifest_path)]
        if compare_out is not None:
            args += ['--compare-build', str(self.build), '--compare-out', str(compare_out)]
        for local in (carried or []):
            args += ['--carried', local]
        return subprocess.run(args, capture_output=True, text=True)

    def test_compare_build_all_same_exits_0(self):
        staging = self.root / 'staging-same'
        shutil.copytree(self.baseline_source, staging)
        out = self.build / '_staging-1' / 'design-ref'
        manifest = self.build / '_staging-1' / 'source-manifest.json'
        diff = self.build / 'refreeze-diff.json'
        result = self.run_archive(staging, out, manifest, compare_out=diff)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(diff.read_text())
        self.assertEqual(payload['summary'], {'same': 3, 'changed': 0, 'added': 0, 'removed': 0, 'carried': 0})
        self.assertTrue(all(row['status'] == 'same' for row in payload['rows']))

    def test_compare_build_changed_file_exits_3(self):
        staging = self.root / 'staging-changed'
        shutil.copytree(self.baseline_source, staging)
        (staging / 'support.js').write_text('window.runtime = false; // edited')
        out = self.build / '_staging-2' / 'design-ref'
        manifest = self.build / '_staging-2' / 'source-manifest.json'
        diff = self.build / 'refreeze-diff.json'
        result = self.run_archive(staging, out, manifest, compare_out=diff)
        self.assertEqual(result.returncode, 3, result.stderr)
        payload = json.loads(diff.read_text())
        self.assertEqual(payload['summary'], {'same': 2, 'changed': 1, 'added': 0, 'removed': 0, 'carried': 0})
        changed = next(row for row in payload['rows'] if row['local_path'] == 'support.js')
        self.assertEqual(changed['status'], 'changed')

    def test_compare_build_added_file_exits_3(self):
        staging = self.root / 'staging-added'
        shutil.copytree(self.baseline_source, staging)
        (staging / 'extra.css').write_text('body{color:blue}')
        out = self.build / '_staging-3' / 'design-ref'
        manifest = self.build / '_staging-3' / 'source-manifest.json'
        diff = self.build / 'refreeze-diff.json'
        result = self.run_archive(staging, out, manifest, compare_out=diff)
        self.assertEqual(result.returncode, 3, result.stderr)
        payload = json.loads(diff.read_text())
        self.assertEqual(payload['summary'], {'same': 3, 'changed': 0, 'added': 1, 'removed': 0, 'carried': 0})
        added = next(row for row in payload['rows'] if row['local_path'] == 'extra.css')
        self.assertEqual(added['status'], 'added')

    def test_compare_build_removed_file_exits_3(self):
        staging = self.root / 'staging-removed'
        shutil.copytree(self.baseline_source, staging)
        (staging / 'logo.png').unlink()
        (staging / 'screen.dc.html').write_text('<script src="support.js"></script>')
        out = self.build / '_staging-4' / 'design-ref'
        manifest = self.build / '_staging-4' / 'source-manifest.json'
        diff = self.build / 'refreeze-diff.json'
        result = self.run_archive(staging, out, manifest, compare_out=diff)
        self.assertEqual(result.returncode, 3, result.stderr)
        payload = json.loads(diff.read_text())
        self.assertEqual(payload['summary']['removed'], 1)
        removed = next(row for row in payload['rows'] if row['local_path'] == 'logo.png')
        self.assertEqual(removed['status'], 'removed')
        self.assertIsNone(removed['mtime'])

    def test_compare_build_carried_outside_closure_exits_4(self):
        staging = self.root / 'staging-carried-outside'
        shutil.copytree(self.baseline_source, staging)
        (staging / 'orphan.png').write_bytes(png())  # entrypoint closure 밖(어디서도 참조 안 됨)
        out = self.build / '_staging-5' / 'design-ref'
        manifest = self.build / '_staging-5' / 'source-manifest.json'
        diff = self.build / 'refreeze-diff.json'
        result = self.run_archive(staging, out, manifest, compare_out=diff, carried=['orphan.png'])
        self.assertEqual(result.returncode, 4, result.stderr)
        payload = json.loads(diff.read_text())
        self.assertEqual(payload['summary'], {'same': 3, 'changed': 0, 'added': 0, 'removed': 0, 'carried': 1})
        row = next(r for r in payload['rows'] if r['local_path'] == 'orphan.png')
        self.assertEqual(row['status'], 'carried')
        self.assertEqual(row['carried_from'], payload['base_manifest_sha256'])
        new_manifest = json.loads(manifest.read_text())
        new_row = next(r for r in new_manifest['files'] if r['local_path'] == 'orphan.png')
        self.assertEqual(new_row['status'], 'ok')
        self.assertEqual(new_row['carried_from'], payload['base_manifest_sha256'])

    def test_compare_build_carried_inside_closure_exits_1(self):
        staging = self.root / 'staging-carried-inside'
        shutil.copytree(self.baseline_source, staging)
        out = self.build / '_staging-6' / 'design-ref'
        manifest = self.build / '_staging-6' / 'source-manifest.json'
        diff = self.build / 'refreeze-diff.json'
        result = self.run_archive(staging, out, manifest, compare_out=diff, carried=['support.js'])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('carried dependency', result.stderr)
        self.assertIn('support.js', result.stderr)
        self.assertFalse(diff.exists())

    def test_compare_build_carried_unknown_path_exits_1(self):
        """staging에도 기준에도 없는 `--carried` 경로(오타)는 조용히 지나가지 않는다(Task 7 리뷰 Minor 2)."""
        staging = self.root / 'staging-carried-unknown'
        shutil.copytree(self.baseline_source, staging)
        out = self.build / '_staging-7' / 'design-ref'
        manifest = self.build / '_staging-7' / 'source-manifest.json'
        diff = self.build / 'refreeze-diff.json'
        result = self.run_archive(staging, out, manifest, compare_out=diff, carried=['orphan.pngg'])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('carried target not in staging: orphan.pngg', result.stderr)
        self.assertFalse(diff.exists())

    def test_compare_build_auto_carried_reference_root_exits_4(self):
        out = self.root / 'design-ref-new'
        manifest = self.root / 'design-ref-new-manifest.json'
        diff = self.build / 'refreeze-diff.json'
        # 원본이 아니라 이미 설치된 reference_root 자체에서 재스테이징 — 기계는 이걸 미확인으로 본다.
        result = self.run_archive(self.ref, out, manifest, compare_out=diff)
        self.assertEqual(result.returncode, 4, result.stderr)
        payload = json.loads(diff.read_text())
        self.assertEqual(payload['summary'], {'same': 0, 'changed': 0, 'added': 0, 'removed': 0, 'carried': 3})
        self.assertTrue(all(row['status'] == 'carried' for row in payload['rows']))
        self.assertTrue(all(row['carried_from'] == payload['base_manifest_sha256'] for row in payload['rows']))

    def test_compare_build_excludes_current_staging_parent_from_auto_carried(self):
        ts_dir = self.build / '_staging-99'
        staging = ts_dir / 'export'
        shutil.copytree(self.baseline_source, staging)
        out = ts_dir / 'design-ref'
        manifest = ts_dir / 'source-manifest.json'
        diff = self.build / 'refreeze-diff.json'
        result = self.run_archive(staging, out, manifest, compare_out=diff)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(diff.read_text())
        self.assertEqual(payload['summary'], {'same': 3, 'changed': 0, 'added': 0, 'removed': 0, 'carried': 0})

    def test_compare_out_format_includes_base_sha_and_mtime(self):
        staging = self.root / 'staging-format'
        shutil.copytree(self.baseline_source, staging)
        out = self.build / '_staging-9' / 'design-ref'
        manifest = self.build / '_staging-9' / 'source-manifest.json'
        diff = self.build / 'refreeze-diff.json'
        result = self.run_archive(staging, out, manifest, compare_out=diff)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(diff.read_text())
        self.assertEqual(payload['version'], 1)
        self.assertEqual(payload['base_manifest_sha256'], sha(self.base_manifest))
        self.assertRegex(payload['generated_at'], r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
        self.assertEqual(len(payload['rows']), 3)
        for row in payload['rows']:
            self.assertEqual(set(row) - {'carried_from'}, {'local_path', 'status', 'size_bytes', 'sha12', 'mtime'})
            self.assertEqual(len(row['sha12']), 12)
            self.assertIsInstance(row['mtime'], float)
        self.assertEqual(payload['summary'], {'same': 3, 'changed': 0, 'added': 0, 'removed': 0, 'carried': 0})


if __name__ == '__main__':
    unittest.main()
