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


class SheetTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sheet = SCRIPT.with_name('style_value_sheet.py')

    def sheet_for(self, data, tokens, seed=0):
        cp, tp, out = (self.root / name for name in ('census.json', 'tokens.css', 'sheet.md'))
        cp.write_text(json.dumps(data))
        if tokens is not None:
            tp.write_text(tokens)
        result = subprocess.run([sys.executable, '-B', str(self.sheet), '--census', str(cp),
                                 '--tokens', str(tp), '--out', str(out)], capture_output=True, text=True,
                                env={**os.environ, 'PYTHONHASHSEED': str(seed)})
        self.assertEqual(result.returncode, 0, result.stderr)
        return out.read_text()

    def test_exact_values_and_aliases_exclude_near_values(self):
        c = census(color='rgba(1, 2, 3, 0.1)')
        c['records'][0]['s']['fs'] = '26px'
        sheet = self.sheet_for({'a': c}, '''
        :root { --size: 26px; --alias: var(--size); --near: 26.4px;
                --unitless: 26; --ink: rgba(1,2,3,.1); --near-alpha: rgba(1,2,3,.11); }
        ''')
        for name in ('--size', '--alias', '--ink'):
            self.assertIn('`' + name + '`', sheet)
        for name in ('--near', '--unitless', '--near-alpha'):
            self.assertNotIn('`' + name + '`', sheet)

    def test_shadow_matches_whole_ordered_layers(self):
        c = census()
        c['records'][0]['s']['sh'] = 'rgb(0, 0, 0) 0px 1px 2px 0px, rgb(255, 255, 255) 0px 0px 1px 0px inset'
        sheet = self.sheet_for({'a': c}, '''
        :root { --shadow: 0 1px 2px #000, inset 0 0 1px #fff;
                --one-layer: 0 1px 2px #000;
                --reversed: inset 0 0 1px #fff, 0 1px 2px #000; }
        ''')
        self.assertIn('`--shadow`', sheet)
        self.assertNotIn('`--one-layer`', sheet)
        self.assertNotIn('`--reversed`', sheet)

    def test_four_sides_and_corners_keep_exact_tokens(self):
        c = census()
        c['records'][0]['s'].update(rad='26px 26px 34px 34px',
                                    pad='2px 4px 2px 4px', gap='8px 12px',
                                    bd='1px solid rgb(1, 2, 3) | 0 | 2px solid rgb(4, 5, 6) | 0')
        sheet = self.sheet_for({'a': c}, '''
        :root { --r26: 26px; --r34: 34px; --padding: 2px 4px;
                --gap: 8px 12px; --top: #010203; --bottom: #040506; }
        ''')
        for name in ('--r26', '--r34', '--padding', '--gap', '--top', '--bottom'):
            self.assertIn('`' + name + '`', sheet)
        for prop in ('bd.top', 'bd.bottom', 'rad.top-left', 'rad.bottom-right'):
            self.assertIn('`' + prop + '`', sheet)
        self.assertNotIn('`bd.right`', sheet)
        self.assertNotIn('`bd.left`', sheet)

    def test_variants_and_child_effects_remain_separate(self):
        c = census()
        c['records'][0].update(k='box', sig='div.panel', s={'bg': 'rgb(255, 255, 255)'})
        child = copy.deepcopy(c['records'][0])
        child.update(i=1, k='pseudo', pn='::before', c=0, anc=[0], s={'sh': 'rgb(0, 0, 0) 0px 0px 2px 0px'})
        variant = copy.deepcopy(c['records'][0])
        variant.update(i=2, s={'bg': 'rgb(0, 0, 0)'})
        c['records'].extend([child, variant])
        c['meta']['records_total'] = 3
        sheet = self.sheet_for({'a': c}, ':root { --white: #fff; --black: #000; }')
        self.assertEqual(sheet.count('| S-'), 3)
        self.assertIn('::before', sheet)
        self.assertIn('a#1', sheet)
        self.assertIn('자식 효과', sheet)
        self.assertIn('`--white`', sheet)
        self.assertIn('`--black`', sheet)

    def test_ambiguous_and_unresolved_values_do_not_get_guessed(self):
        c = census()
        sheet = self.sheet_for({'a': c}, '''
        :root { --duplicate: 16px; --cycle-a: var(--cycle-b); --cycle-b: var(--cycle-a);
                --relative: 1rem; --calc: calc(8px + 8px); --alias: var(--duplicate); }
        .other { --duplicate: 18px; }
        ''')
        for name in ('--duplicate', '--cycle-a', '--cycle-b', '--relative', '--calc', '--alias'):
            self.assertNotIn('`' + name + '`', sheet)
        self.assertNotIn('신규 등록 필요', sheet)
        self.assertIn('수동 확인', sheet)

    def test_missing_token_file_is_a_reference_sheet_not_a_gate(self):
        sheet = self.sheet_for({'a': census()}, None)
        self.assertIn('토큰 파일 없음', sheet)
        self.assertIn('신규 등록 필요', sheet)

    def test_multiword_font_quotes_preserve_exact_family(self):
        c = census()
        c['records'][0]['s']['ff'] = 'Noto Sans'
        sheet = self.sheet_for({'a': c}, ':root { --font: "Noto Sans"; --other: "Noto Serif"; }')
        self.assertIn('`--font`', sheet)
        self.assertNotIn('`--other`', sheet)

    def test_v4_truncated_value_is_visible_but_never_an_exact_match(self):
        c = census()
        c['records'][0].update(k='pseudo', pn='::before')
        c['records'][0]['s']['bgi'] = 'linear-gradient(rgb(255, 0, 0), rgb(0, 0,'
        c['records'][0]['s']['content'] = '"abcdefghijklmno'
        sheet = self.sheet_for({'a': c}, ':root { --size: 16px; }')
        self.assertIn('linear-gradient', sheet)
        self.assertIn('v4 길이 상한', sheet)
        self.assertIn('`--size`', sheet)

    def test_hex_alpha_matches_indistinguishable_browser_serialization(self):
        c = census(color='rgba(1, 2, 3, 0.5)')
        sheet = self.sheet_for({'a': c}, ':root { --exact: rgba(1,2,3,.5); --rounded: #01020380; }')
        self.assertIn('`--exact`', sheet)
        self.assertIn('`--rounded`', sheet)

    def test_p1_serialized_colors_shadow_and_font_find_existing_tokens(self):
        c = census()
        c['records'][0]['s'] = {
            'bg': 'color(srgb 1 0.992157 0.976471 / 0.52)',
            'c': 'color(srgb 0.309804 0.541176 0.423529 / 0.14)',
            'fill': 'color(srgb 0.121569 0.109804 0.0941176 / 0.06)',
            'sh': ('color(srgb 0.121569 0.109804 0.0941176 / 0.07) 0px 2px 6px 0px, '
                   'color(srgb 0.121569 0.109804 0.0941176 / 0.1) 0px 10px 28px 0px'),
            'ff': 'Pretendard Variable',
        }
        sheet = self.sheet_for({'p1': c}, '''
        :root { --ink-900: #1F1C18; --jade-500: #4F8A6C;
          --glass-tint-strong: rgba(255,253,249,.52);
          --success-soft: color-mix(in srgb,var(--jade-500) 14%,transparent);
          --surface-muted: color-mix(in srgb,var(--ink-900) 6%,transparent);
          --shadow-2: 0 2px 6px rgba(31,28,24,.07), 0 10px 28px rgba(31,28,24,.10);
          --shadow-near: 0 2px 6px rgba(31,28,24,.07), 0 10px 28px rgba(31,28,24,.11);
          --font-sans: "Pretendard Variable", Pretendard, system-ui, sans-serif; }
        ''')
        for name in ('--glass-tint-strong', '--success-soft', '--surface-muted', '--shadow-2', '--font-sans'):
            self.assertIn('`' + name + '`', sheet)
        self.assertNotIn('`--shadow-near`', sheet)
        self.assertIn('첫 서체 일치(스택 확인)', sheet)

    def test_srgb_visible_alpha_precision_is_not_collapsed(self):
        c = census(color='color(srgb 0.1 0.2 0.3 / 0.5005)')
        sheet = self.sheet_for({'a': c}, '''
        :root { --exact: color(srgb .1 .2 .3 / .5005);
                --near: color(srgb .1 .2 .3 / .5); }
        ''')
        self.assertIn('`--exact`', sheet)
        self.assertNotIn('`--near`', sheet)

    def test_unresolved_tokens_make_matching_property_manual(self):
        c = census()
        c['records'][0]['s'] = {'fs': '16px', 'c': 'rgb(1, 2, 3)'}
        sheet = self.sheet_for({'a': c}, '''
        :root { --fs-relative: 1rem; --fs-calculated: calc(8px + 8px);
                --ink-mix: color-mix(in oklab, #123 20%, transparent); }
        ''')
        for value in ('16px', 'rgb(1, 2, 3)'):
            row = next(line for line in sheet.splitlines() if '| `' + value + '` |' in line)
            self.assertIn('수동 확인', row)
            self.assertNotIn('신규 등록 필요', row)

    def test_unsupported_named_color_is_not_reported_as_missing(self):
        c = census(color='rgb(102, 51, 153)')
        sheet = self.sheet_for({'a': c}, ':root { --border-ink: rebeccapurple; }')
        row = next(line for line in sheet.splitlines() if '| `rgb(102, 51, 153)` |' in line)
        self.assertIn('수동 확인', row)
        self.assertNotIn('신규 등록 필요', row)

    def test_defaults_and_wrong_token_families_do_not_enter_reference_rows(self):
        c = census()
        c['records'][0]['s'] = {'bg': 'rgba(0, 0, 0, 0)', 'bf': 'none', 'maxh': 'none',
                              'pad': '0px 0px 0px 0px', 'gap': 'normal normal', 'op': '1',
                              'bd': '1px solid rgb(1, 2, 3) | 0 | 0 | 0', 'lh': '13px'}
        sheet = self.sheet_for({'a': c}, '''
        :root { --settings-toast-z: 1; --shadow-0: none; --ls-caption: 0px;
                --fs-caption: 13px; --chat-review-stars-tracking: 1px;
                --border-width: 1px; --line-height: 13px; }
        ''')
        for name in ('--settings-toast-z', '--shadow-0', '--ls-caption', '--fs-caption', '--chat-review-stars-tracking'):
            self.assertNotIn('`' + name + '`', sheet)
        for name in ('--border-width', '--line-height'):
            self.assertIn('`' + name + '`', sheet)
        self.assertNotIn('| `bd` |', sheet)
        for value in ('none', 'normal normal', '0px 0px 0px 0px', 'rgba(0, 0, 0, 0)'):
            self.assertNotIn('| `' + value + '` |', sheet)

    def test_lane_sized_sheet_bounds_lists_and_deduplicates_value_index(self):
        c = census()
        c['records'] = []
        # P1 233묶음과 비슷한 240묶음, 7,200 records. 반복 구성원 폭증을 잡는다.
        for group in range(240):
            for repeat in range(30):
                i = len(c['records'])
                c['records'].append({'i': i, 'k': 'box', 'sig': f'div.panel-{group}',
                    'r': [0, 0, 100, 100], 'op': 1, 'anc': [0] if i else [],
                    's': {'bg': 'rgb(1, 2, 3)', 'rad': '26px 26px 26px 26px',
                          'pad': '8px 12px 8px 12px', 'bf': 'none', 'minh': 'auto',
                          'bd': '0 | 0 | 0 | 0', 'gap': 'normal normal',
                          'fs': f'{12 + group % 24}px', 'lh': f'{20 + group % 30}px',
                          'c': f'rgb({group % 24}, 51, 153)',
                          'sh': f'rgba(31, 28, 24, 0.1) 0px {group % 12}px {group % 20}px 0px'}})
        c['meta']['records_total'] = len(c['records'])
        sheet = self.sheet_for({'lane': c}, ':root { --ink: #010203; --radius: 26px; --space: 8px 12px; }')
        self.assertLessEqual(len(sheet.encode()), 100_000)
        self.assertIn('값 → 토큰', sheet)
        self.assertEqual(sheet.count('| S-'), 240)
        self.assertIn('7199', sheet)  # 루트의 전체 자식 수는 표본 절단 뒤에도 남는다.
        self.assertNotIn('lane#7199', sheet)
        self.assertLess(sheet.count('`--ink`'), 3)

    def test_sheet_bytes_are_independent_of_map_record_and_token_order(self):
        a = census()
        r = copy.deepcopy(a['records'][0])
        r.update(i=1, sig='p.other')
        a['records'].append(r)
        a['meta']['records_total'] = 2
        b = census(color='rgb(255, 0, 0)')
        one = self.sheet_for({'a': a, 'b': b}, ':root { --a: 16px; --b: #f00; }')
        a['records'].reverse()
        two = self.sheet_for({'b': b, 'a': a}, ':root { --b: #f00; --a: 16px; }', seed=7)
        self.assertEqual(one, two)


if __name__ == '__main__':
    unittest.main()
