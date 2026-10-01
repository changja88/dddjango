"""W8 v4 관측 계약·보고 CLI·결정성 회귀 시험(표준 라이브러리)."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'compare_style_census.py'
SOURCE = Path(os.environ.get('W8_TEST_SOURCE', SCRIPT))
spec = importlib.util.spec_from_file_location('comparator', SOURCE)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def census(text='공유', color='rgb(51, 51, 51)'):
    return {'meta': {'census_version': 4, 'root': '#app', 'root_matched': 1,
                     'route_set': None, 'root_rect': [0, 0, 390, 844],
                     'fonts': 'loaded', 'fonts_failed': [], 'partial': False,
                     'running_animations': 0, 'records_total': 1, 'pages': 1,
                     'vendor': [], 'sdk_globals': {}},
            'records': [{'i': 0, 'k': 'text', 'r': [10, 10, 30, 20], 'op': 1,
                         'sig': 'p.label', 'label': text, 't': text, 'anc': [],
                         's': {'fs': '16px', 'fw': '400', 'ff': 'sans-serif',
                               'lh': '20px', 'ls': '0px', 'c': color, 'lines': 1}}]}


class ComparatorTest(unittest.TestCase):
    def setUp(self):
        C.SDK_SCOPE = {}
        C.ALLOW_LEGACY = False
        C.DECLARED = set()

    def props(self, d, i, case='plain'):
        return [f['prop'] for f in C.compare_case(d, i, case)['findings']
                if f['kind'] == 'unrun']

    def test_v4_sdk_cross_check(self):
        plain = census()
        sdk = copy.deepcopy(plain)
        sdk['meta'].update(route_set=['operator-hosts'],
                           vendor=[{'path': '/static/vendor/sdk.js', 'status': 200}],
                           sdk_globals={'SDK': True})
        C.SDK_SCOPE = {'sdk': {'files': ['/static/vendor/sdk.js'], 'globals': ['SDK']}}
        self.assertEqual(self.props(sdk, sdk, 'sdk'), [])
        self.assertEqual(self.props(plain, plain), [])
        for key, value in [('route_set', None), ('sdk_globals', {'SDK': False}),
                           ('vendor', [{'path': '/static/vendor/sdk.js', 'status': 404}])]:
            bad = copy.deepcopy(sdk)
            bad['meta'][key] = value
            self.assertEqual(self.props(sdk, bad, 'sdk'), ['sdk-state'])
        self.assertEqual(self.props(plain, sdk), ['sdk-state'])

    def test_schema_root_and_partial_are_unrun(self):
        d = census()
        for key, value, prop in [('census_version', 3, 'schema-impl'),
                                  ('root_matched', 0, 'root-selector-impl'),
                                  ('root_matched', 2, 'root-selector-impl'),
                                  ('partial', True, 'unsettled-impl')]:
            i = copy.deepcopy(d)
            i['meta'][key] = value
            self.assertEqual(self.props(d, i), [prop])

    def test_declared_data_does_not_hide_style_difference(self):
        C.DECLARED = {'data'}
        result = C.compare_case(census(), census('다른 글', 'rgb(255, 0, 0)'), 'data')
        self.assertTrue(any(f['prop'] == 'text.c' and f['blocking'] for f in result['findings']))
        self.assertTrue(any(f['kind'] == 'uncompared' for f in result['findings']))

    def test_group_and_samples_are_hash_seed_independent(self):
        # Two tied groups and six members exercise both sorting and sample selection.
        code = '''
import importlib.util, json, sys
s=importlib.util.spec_from_file_location('c',sys.argv[1]); c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
fs=[]
for n in set('abcdef'):
 for value in set(('20px','30px')):
  fs.append(dict(member=n+value,case=n,kind='prop',prop='text.fs',design='16px',impl=value,
                 i_sig='p.label',d_sig='p.label',label=n,note='',d_r=[0,0,1,1],i_r=[0,0,1,1],blocking=True,variant=False))
print(json.dumps(c.group({'case':{'findings':fs}}),ensure_ascii=False,sort_keys=True))
'''
        outputs = [subprocess.check_output([sys.executable, '-B', '-c', code, str(SOURCE)],
                   env={**os.environ, 'PYTHONHASHSEED': str(seed)}) for seed in range(6)]
        self.assertEqual(len(set(outputs)), 1, 'group order / first four samples vary by hash seed')


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.paths = {}
        for name, value in [('design', {'plain': census()}),
                            ('impl', {'plain': census(color='rgb(255, 0, 0)')}),
                            ('mapping', {'plain': 'plain'}), ('sdk-scope', {})]:
            p = self.root / (name + '.json')
            p.write_text(json.dumps(value))
            self.paths[name] = p
        self.out = self.root / 'report.json'

    def run_cli(self):
        args = [sys.executable, '-B', str(SCRIPT)]
        for name, path in self.paths.items():
            args.extend(['--' + name, str(path)])
        return subprocess.run(args + ['--out', str(self.out)], capture_output=True, text=True)

    def test_candidates_are_reported_without_blocking_exit(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(self.out.read_text())
        self.assertEqual([(g['prop'], g['blocking']) for g in report['groups']], [('text.c', True)])

    def test_empty_duplicate_and_missing_mapping_fail(self):
        for mapping in ({}, {'plain': 'missing'}, {'plain': 'plain', 'other': 'plain'}):
            self.paths['mapping'].write_text(json.dumps(mapping))
            result = self.run_cli()
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertFalse(self.out.exists())

    def test_unrun_case_is_reported_and_not_success(self):
        i = census()
        i['meta']['root_matched'] = 2
        self.paths['impl'].write_text(json.dumps({'plain': i}))
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(self.out.read_text())['groups'][0]['kind'], 'unrun')

    def test_missing_page_is_not_success(self):
        i = census()
        i['meta'].update(pages=2, records_total=2)
        self.paths['impl'].write_text(json.dumps({'plain': i}))
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stderr)

    def test_malformed_json_is_usage_error(self):
        self.paths['mapping'].write_text('{')
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
