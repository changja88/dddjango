#!/usr/bin/env python3
"""Source archives must preserve originals without pretending to execute JSX."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from unittest import mock

from test_design_evidence import png

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import archive_design  # noqa: E402
import check_design_evidence  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nfc(name):
    return unicodedata.normalize('NFC', name)


def nfd(name):
    return unicodedata.normalize('NFD', name)


def renormalize(root, form):
    """Rename every name under root to one form, as a git checkout (NFC) or macOS unzip (NFD) writes it."""
    for path in sorted(root.rglob('*'), key=lambda p: len(p.parts), reverse=True):
        path.rename(path.with_name(unicodedata.normalize(form, path.name)))


def disk_names(root):
    return [path.relative_to(root).as_posix() for path in sorted(root.rglob('*'))]


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

    def archive(self, entry=None, source_root=None):
        return subprocess.run([sys.executable, str(SCRIPTS / 'archive_design.py'),
                               str(entry or self.source / 'screen.dc.html'), '--source-root', str(source_root or self.source),
                               '--out', str(self.ref), '--manifest', str(self.manifest)],
                              capture_output=True, text=True)

    def korean_export(self):
        """Return the NFD entry of an export unzipped by macOS: every Korean name is NFD on disk."""
        folder = self.source / nfd('내보내기')
        folder.mkdir()
        (folder / nfd('스크린샷 1.png')).write_bytes(png())
        entry = self.source / nfd('화면.dc.html')
        entry.write_text('<script src="support.js"></script>')
        return entry

    def legacy_nfd_archive(self):
        """Freeze the Korean export as collectors before NFC naming did: NFD names in the manifest and on disk."""
        self.assertEqual(self.archive(self.korean_export()).returncode, 0)
        renormalize(self.ref, 'NFD')
        manifest = json.loads(self.manifest.read_text())
        manifest['entrypoint'] = nfd(manifest['entrypoint'])
        for row in manifest['files']:
            row['local_path'] = nfd(row['local_path'])
        self.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        self.observe()
        self.review()
        self.assertIn(nfd('내보내기/스크린샷 1.png'), disk_names(self.ref))
        return manifest

    def rewrite_manifest(self, manifest):
        """Store an edited manifest and bind the observation to its new bytes."""
        self.manifest.write_text(json.dumps(manifest, ensure_ascii=False))
        self.observation['archive_sha256'] = sha(self.manifest)
        self.write_observation()
        self.spec['cases'][0]['source_observation'] = self.pointer(self.build / 'observation.json')
        self.write_spec()

    def pointer(self, path, root=None):
        return {'path': path.relative_to(root or self.build).as_posix(), 'sha256': sha(path)}

    def prepare(self, entry=None):
        result = self.archive(entry)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.observe()

    def observe(self):
        (self.build / 'scope.md').write_text('Original export, login/default at 390x844.\n')
        (self.build / 'original.png').write_bytes(png())
        (self.build / 'browser-trace.json').write_text(json.dumps({'url': 'http://127.0.0.1:9000/screen.dc.html',
            'viewport': [390, 844], 'selector': '[data-screen]', 'text': 'Login',
            'images': [{'currentSrc': 'http://127.0.0.1:9000/logo.png', 'complete': True, 'naturalWidth': 1}],
            'fonts': [{'family': 'system-ui', 'status': 'loaded'}], 'failures': []}))
        entry = self.pointer(self.ref / json.loads(self.manifest.read_text())['entrypoint'], self.ref)
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

    def gate(self, phase='inputs', *options):
        return subprocess.run([sys.executable, str(SCRIPTS / 'check_design_evidence.py'),
            '--build', str(self.build), '--project-root', str(self.project), '--phase', phase, *options],
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

    def test_legacy_nfd_archive_passes_in_a_nfc_checkout_with_the_same_digest(self):
        manifest = self.legacy_nfd_archive()
        frozen = self.gate('inputs', '--fingerprint')
        self.assertEqual(frozen.returncode, 0, frozen.stderr)
        renormalize(self.ref, 'NFC')  # git checkout of the committed build
        self.assertIn(nfc('내보내기/스크린샷 1.png'), disk_names(self.ref))
        checkout = self.gate('inputs', '--fingerprint')
        self.assertEqual(checkout.returncode, 0, checkout.stderr)
        self.assertEqual(json.loads(checkout.stdout)['input_digest'], json.loads(frozen.stdout)['input_digest'])
        items = check_design_evidence.validate_inputs(self.build.resolve(), self.project.resolve())[2]
        self.assertEqual({name for name, _ in items if name.startswith('source/')},
                         {f'source/{row["local_path"]}' for row in manifest['files']})  # digest names stay as recorded

    def test_legacy_nfd_archive_still_reports_real_differences_in_korean_names(self):
        self.legacy_nfd_archive()
        renormalize(self.ref, 'NFC')
        extra = self.ref / nfc('내보내기/추가.png')
        extra.write_bytes(png())
        result = self.gate()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(f"files without a manifest row: {nfc('내보내기/추가.png')!r}", result.stderr)
        extra.unlink()
        (self.ref / nfc('내보내기/스크린샷 1.png')).unlink()
        result = self.gate()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(f"manifest rows without a file: {nfc('내보내기/스크린샷 1.png')!r}", result.stderr)

    def test_nfc_archive_passes_on_nfd_disk_names(self):
        self.prepare(self.korean_export())  # NFD argument, as listed in the unzipped export
        self.assertEqual(json.loads(self.manifest.read_text())['entrypoint'], nfc('화면.dc.html'))
        self.review()
        frozen = self.gate()
        self.assertEqual(frozen.returncode, 0, frozen.stderr)
        renormalize(self.ref, 'NFD')  # the committed build unzipped by macOS
        self.assertIn(nfd('내보내기/스크린샷 1.png'), disk_names(self.ref))
        unzipped = self.gate()
        self.assertEqual(unzipped.returncode, 0, unzipped.stderr)
        self.assertEqual(json.loads(unzipped.stdout)['input_digest'], json.loads(frozen.stdout)['input_digest'])

    def test_nfc_equivalent_manifest_rows_collide(self):
        self.prepare(self.korean_export())
        manifest = json.loads(self.manifest.read_text())
        row = next(r for r in manifest['files'] if r['local_path'] == nfc('내보내기/스크린샷 1.png'))
        manifest['files'].append(dict(row, local_path=nfd(row['local_path'])))  # the same disk file twice
        self.rewrite_manifest(manifest)
        result = self.gate('prepare')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('manifest local_path names collide after Unicode NFC normalization: '
                      f"{nfc('내보내기/스크린샷 1.png')!r} — one name in two Unicode forms (NFC/NFD); keep one row",
                      result.stderr)
        self.assertNotIn('inventory differs', result.stderr)

    def test_nfc_equivalent_frozen_files_collide(self):
        # APFS cannot hold both forms in one folder; list a twin as a normalization-sensitive filesystem would.
        self.prepare(self.korean_export())
        real = check_design_evidence.archive_files

        def with_twin(root):
            return real(root) + [root / nfd('내보내기/스크린샷 1.png')]
        with mock.patch.object(check_design_evidence, 'archive_files', with_twin), \
                self.assertRaises(check_design_evidence.Defects) as caught:
            check_design_evidence.validate_inputs(self.build.resolve(), self.project.resolve(), require_review=False)
        self.assertEqual(caught.exception.messages, [
            "manifests[0]: frozen tree file names collide after Unicode NFC normalization: "
            f"{nfc('내보내기/스크린샷 1.png')!r} — one name in two Unicode forms (NFC/NFD); keep one file"])

    def test_two_rows_cannot_open_one_file(self):
        # HFS+/exFAT fold some distinct names onto one file; a hard link is the APFS stand-in.
        self.prepare()
        os.link(self.ref / 'logo.png', self.ref / 'logo-copy.png')
        manifest = json.loads(self.manifest.read_text())
        row = next(r for r in manifest['files'] if r['local_path'] == 'logo.png')
        manifest['files'].append(dict(row, local_path='logo-copy.png'))
        self.rewrite_manifest(manifest)
        result = self.gate('prepare')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(f'files[{len(manifest["files"]) - 1}].local_path: opens the same file as another row', result.stderr)

    def test_static_manifest_may_list_one_file_under_two_spellings(self):
        # freeze_design keeps a row per reference; APFS opens logo.png/LOGO.png and NFC/NFD 그림.png as one file each.
        (self.source / nfc('그림.png')).write_bytes(png())
        (self.source / 'static.html').write_text(
            f'<img src="logo.png"><img src="LOGO.png"><img src="{nfc("그림.png")}"><img src="{nfd("그림.png")}">')
        result = subprocess.run([sys.executable, str(SCRIPTS / 'freeze_design.py'), str(self.source / 'static.html'),
                                 '--out', str(self.ref), '--manifest', str(self.manifest)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = json.loads(self.manifest.read_text())['files']
        self.assertEqual(len({(self.ref / row['local_path']).stat().st_ino for row in rows}), len(rows) - 2)
        (self.build / 'scope.md').write_text('Static export, static/default at 390x844.\n')
        (self.build / 'original.png').write_bytes(png())
        self.spec = {'version': 1, 'reference_root': 'design-ref', 'manifests': ['source-manifest.json'],
            'scope': self.pointer(self.build / 'scope.md'), 'coverage_review': None,
            'cases': [{'id': 'static/default', 'screen': 'static', 'state': 'default', 'viewport': [390, 844],
                'scope_refs': ['scope.md#static'], 'entrypoint': self.pointer(self.ref / 'static.html', self.ref),
                'reference_capture': self.pointer(self.build / 'original.png')}]}
        self.write_spec()
        result = self.gate('prepare')
        self.assertEqual(result.returncode, 0, result.stderr)  # the one-file-one-row rule guards archive manifests only

    def test_unicode_form_mismatches_name_their_cause(self):
        self.prepare(self.korean_export())
        entry = self.observation['entrypoint']
        other = dict(entry, path=nfd(entry['path']))
        manifest = json.loads(self.manifest.read_text())
        manifest['entrypoint'] = other['path']
        self.observation['entrypoint'] = other
        self.rewrite_manifest(manifest)
        first = self.gate('prepare')
        self.observation['entrypoint'] = entry
        self.spec['cases'][0]['entrypoint'] = other
        self.rewrite_manifest(manifest)
        second = self.gate('prepare')
        self.assertEqual((first.returncode, second.returncode), (2, 2))
        hinted = {line.split(': ')[1] for result in (first, second) for line in result.stderr.splitlines()
                  if 'another Unicode form (NFC/NFD)' in line}
        self.assertEqual(hinted, {'manifests[0].entrypoint', 'cases[0].source_observation.entrypoint',
                                  'cases[0].entrypoint'})

    def test_archive_names_are_nfc_for_a_hand_typed_entry(self):
        self.korean_export()
        self.prepare(self.source / nfc('화면.dc.html'))  # typed argument; the disk name is NFD
        manifest = json.loads(self.manifest.read_text())
        names = [manifest['entrypoint'], *(r['local_path'] for r in manifest['files']), *disk_names(self.ref)]
        self.assertIn(nfc('내보내기/스크린샷 1.png'), names)
        self.assertEqual(names, [nfc(name) for name in names])  # a fresh --out on APFS
        entry = next(r for r in manifest['files'] if r['local_path'] == manifest['entrypoint'])
        self.assertEqual(entry['source'], str(self.source.resolve() / nfd('화면.dc.html')))  # provenance stays original

    def test_archive_checks_an_entry_typed_in_the_other_unicode_form(self):
        (self.source / nfd('빈 화면.html')).write_bytes(b'')
        result = self.archive(self.source / nfc('빈 화면.html'))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('empty original entrypoint', result.stderr)

    def test_archive_refuses_an_entry_spelled_unlike_its_listed_name(self):
        (self.source / 'Screen.html').write_text('<main>Original</main>')
        result = self.archive(self.source / 'screen.html')  # case-insensitive APFS still opens it
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertFalse(self.ref.exists())  # refused before any file was written
        self.assertFalse(self.manifest.exists())

    def test_archive_names_a_source_root_typed_in_the_other_unicode_form(self):
        root = self.root / nfd('춘몽 웹앱')
        root.mkdir()
        (root / 'screen.html').write_text('<main>Original</main>')
        result = self.archive(self.root / nfc('춘몽 웹앱') / 'screen.html', source_root=root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('different Unicode forms (NFC/NFD)', result.stderr)

    def test_archive_refuses_source_names_that_collide_after_nfc(self):
        # APFS cannot hold both forms in one folder; list a twin as a normalization-sensitive filesystem would.
        (self.source / nfc('로고.png')).write_bytes(png())
        real = archive_design.archive_files

        def with_twin(root):
            return real(root) + [root / nfd('로고.png')]
        with mock.patch.object(archive_design, 'archive_files', with_twin), \
                self.assertRaisesRegex(ValueError, 'source names collide after Unicode NFC normalization'):
            archive_design.archive(self.source / 'screen.dc.html', self.source, self.ref, self.manifest)
        self.assertFalse(self.ref.exists())
        self.assertFalse(self.manifest.exists())

    def test_archive_into_an_earlier_nfd_copy_still_passes_the_gate(self):
        entry = self.korean_export()
        shutil.copytree(self.source, self.ref, ignore=shutil.ignore_patterns('.DS_Store'))  # same bytes, NFD names
        self.prepare(entry)  # identical files are kept, so the manifest is NFC while the disk stays NFD
        self.assertIn(nfd('내보내기/스크린샷 1.png'), disk_names(self.ref))

    def test_archive_own_inventory_check_counts_a_twin_in_the_other_form(self):
        entry = self.korean_export()
        real, out = archive_design.archive_files, self.ref.resolve()

        def stale_twin(root):  # a normalization-sensitive filesystem may keep an older NFD copy
            return real(root) + ([root / nfd('내보내기/스크린샷 1.png')] if root == out else [])
        with mock.patch.object(archive_design, 'archive_files', stale_twin), \
                self.assertRaisesRegex(ValueError, 'output inventory differs'):
            archive_design.archive(entry, self.source, self.ref, self.manifest)

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
