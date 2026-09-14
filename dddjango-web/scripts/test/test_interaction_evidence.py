#!/usr/bin/env python3
"""K3 상호작용 증거(interactions.json) 반례 픽스처 — 검사기 v2.

브라우저 없이 손으로 쓴 문서로 검사 하나씩을 고정한다(K5 «검사기(Python) 반례는
손으로 쓴 interactions.json fixture로 브라우저 없이 전부 고정한다»). 잔여 계산은
JS 정본(`assets/interaction_audit.js`의 `pure.residual`)과 같은 답을 내야 하므로
node로 실제 호출해 대조한다(K1 «한 표·두 구현»).
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
ASSETS = SCRIPTS.parent / 'assets'
FIXTURES = HERE / 'fixtures' / 'interaction'
for candidate in (str(HERE), str(SCRIPTS)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

import check_design_evidence as gate  # noqa: E402
from test_design_evidence import png  # noqa: E402

INTERACTIONS = 'captures/screen-interactions.json'
STEP_CAPTURE = 'captures/screen-step1.png'
UNIT_QUOTE = '데이터변이라서관찰에서제외한다'
SURFACE_QUOTE = '메뉴가 열린 표면은 시안 33으로 대신한다'
SCOPE_TEXT = f"""# A8 관계인 화면 범위

## 관계 메뉴

선택 옵션 b는 {UNIT_QUOTE} — 사용자 승인 2026-09-13.

## 표면

{SURFACE_QUOTE}고 사용자가 승인했다.
"""


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def entry(tid, enabled=True, checked=None, face=None, value_empty=None, surface=None,
          occluded=False, live=False):
    return {'id': tid, 'enabled': enabled, 'checked': checked, 'face': face,
            'value_empty': value_empty, 'surface': surface, 'occluded': occluded, 'live': live}


def target(role, name, kind, owner='', **extra):
    return dict({'role': role, 'name': name, 'input_type': '', 'owner': owner,
                 'owner_items_hash': '', 'dom_path': f'form/{name}', 'kind': kind,
                 'first_seen_step': 0, 'declared': False, 'found_by': ['semantic'],
                 'live': False}, **extra)


def node_residual(document: dict) -> list[list]:
    """JS 정본 `pure.residual`의 실제 출력(두 구현 동일성 대조용)."""
    script = ("const audit = require(process.argv[1]);"
              "const doc = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));"
              "process.stdout.write(JSON.stringify(audit.residual(doc)));")
    with tempfile.NamedTemporaryFile('w', suffix='.json', encoding='utf-8', delete=False) as handle:
        json.dump(document, handle, ensure_ascii=False)
        path = handle.name
    try:
        result = subprocess.run(['node', '-e', script, str(ASSETS / 'interaction_audit.js'), path],
                                capture_output=True, text=True, timeout=60)
    finally:
        Path(path).unlink()
    if result.returncode != 0:
        raise AssertionError(f'node pure.residual 실행 실패: {result.returncode} {result.stderr}')
    return [[row['target'], row['action'], row['option']] for row in json.loads(result.stdout)]


class InteractionEvidenceTests(unittest.TestCase):
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
        self.project = self.root / 'app'
        (self.project / 'web').mkdir(parents=True)
        (self.source / 'screen.dc.html').write_text(
            '<div data-screen-label="관계인"><script src="support.js"></script></div>', encoding='utf-8')
        (self.source / 'other.dc.html').write_text('<div data-screen-label="다른"></div>', encoding='utf-8')
        (self.source / 'support.js').write_text('window.runtime = true;')
        archived = subprocess.run(
            [sys.executable, str(SCRIPTS / 'archive_design.py'), str(self.source / 'screen.dc.html'),
             '--source-root', str(self.source), '--out', str(self.ref), '--manifest', str(self.manifest)],
            capture_output=True, text=True)
        self.assertEqual(archived.returncode, 0, archived.stderr)
        (self.build / 'scope.md').write_text(SCOPE_TEXT, encoding='utf-8')
        (self.build / 'original.png').write_bytes(png())
        (self.build / 'captures').mkdir()
        (self.build / STEP_CAPTURE).write_bytes(png())
        (self.build / 'browser-trace.json').write_text(json.dumps(
            {'url': 'http://127.0.0.1:9000/screen.dc.html', 'viewport': [390, 844], 'failures': []}))
        (self.build / 'screen-meta.json').write_text(json.dumps(
            {'screen_label': '관계인', 'title': '관계인', 'cards': [],
             'source_sha256': sha(self.ref / 'screen.dc.html')}, ensure_ascii=False), encoding='utf-8')
        self.doc = self.base_doc()
        self.observation = self.base_observation()
        self.second = None
        self.spec = self.base_spec()
        self.sync()

    # ---- 고정 픽스처 -------------------------------------------------
    def pointer(self, path, root=None):
        path = Path(path)
        return {'path': path.relative_to(root or self.build).as_posix(), 'sha256': sha(path)}

    def entrypoint(self):
        return self.pointer(self.ref / 'screen.dc.html', self.ref)

    def base_doc(self):
        entry_sha = sha(self.ref / 'screen.dc.html')
        targets = {
            'btn': target('button', '열기', 'button'),
            'agree': target('checkbox', '동의', 'checkbox'),
            'sel': target('listbox', '지역', 'select'),
            'opt-a': target('option', '서울', 'option', 'sel', value='a'),
            'opt-b': target('option', '부산', 'option', 'sel', value='b'),
            'ovl': target('dialog', '', 'overlay', scrim=True),
        }
        for index in range(1, 7):
            targets[f'f{index}'] = target('button', f'행{index}', 'button')
        form = [entry('btn'), entry('agree', checked=False), entry('sel')]
        form += [entry(f'f{index}') for index in range(1, 7)]
        opened = form + [entry('ovl')]
        checked = [entry('btn'), entry('agree', checked=True), entry('sel')]
        checked += [entry(f'f{index}') for index in range(1, 7)]
        capture = {'path': STEP_CAPTURE, 'sha256': sha(self.build / STEP_CAPTURE)}
        steps = [
            self.step(1, 'btn', 'click', None, form, opened, added=['ovl'],
                      surface='sf1', capture=capture),
            self.step(2, 'ovl', 'click', None, opened, form, removed=['ovl']),
            self.step(3, 'btn', 'click', None, form, opened, added=['ovl'],
                      surface='sf1', capture=capture),
            self.step(4, 'ovl', 'key', 'Escape', opened, form, removed=['ovl']),
            self.step(5, 'agree', 'click', False, form, checked),
            self.step(6, 'agree', 'click', True, checked, form),
            self.step(7, 'opt-a', 'select', 'a', form, form),
            self.step(8, 'opt-b', 'select', 'b', form, form),
        ]
        for index in range(1, 7):
            steps.append(self.step(8 + index, f'f{index}', 'click', None, form, form))
        return {
            'version': 1,
            'collector': {'name': 'interaction_audit', 'snippet_sha256': sha(ASSETS / 'interaction_audit.js'),
                          'driver': 'observe_interactions.pw.js',
                          'driver_sha256': sha(ASSETS / 'observe_interactions.pw.js'),
                          'path': 'node', 'capabilities': {'react_props': True, 'cdp_listeners': True}},
            'archive_sha256': sha(self.manifest),
            'entrypoint': {'path': 'screen.dc.html', 'sha256': entry_sha},
            'url': 'http://127.0.0.1:9000/screen.dc.html',
            'browser_viewport': [560, 1040],
            'content_crop': {'x': 85, 'y': 40, 'w': 390, 'h': 844},
            'root': {'selector': '[data-screen-label="관계인"]', 'found': True,
                     'fingerprint': {'tag': 'div', 'label': '관계인', 'descendants': 12,
                                     'rect': {'x': 85, 'y': 40, 'w': 390, 'h': 844}}},
            'outside_root': {'count': 0, 'sample': []},
            'excluded_regions': [],
            'served': {'screen.dc.html': entry_sha, 'support.js': sha(self.ref / 'support.js')},
            'declared': [], 'declared_unmatched': [],
            'observed_at': '2026-09-13T05:00:00Z',
            'targets': targets,
            'initial': {'inventory': form, 'state_hash': 'state-0', 'surface_key': 'sf0',
                        'capture': {'path': 'original.png', 'sha256': sha(self.build / 'original.png')}},
            'steps': steps,
            'discovery_limits': [], 'partial': False, 'caps_hit': [], 'environment_error': None,
        }

    def step(self, n, tid, action, option, before, after, added=(), removed=(),
             surface='sf0', capture=None, status='executed'):
        block = {'inventory': after, 'state_hash': f'state-{n}', 'surface_key': surface}
        if capture:
            block['capture'] = capture
        return {'n': n, 'path': [tid], 'target': tid, 'action': action, 'option': option,
                'value': None, 'context': f'ctx-{n}', 'status': status, 'error': None,
                'before': {'inventory': before, 'state_hash': f'state-{n - 1}'}, 'after': block,
                'changes': {'added': list(added), 'removed': list(removed), 'values': []},
                'navigated': None, 'discovery': False}

    def base_observation(self):
        return {'version': 2, 'archive_sha256': sha(self.manifest), 'entrypoint': self.entrypoint(),
                'case_id': 'related/list', 'screen': 'related', 'state': 'list',
                'viewport': [390, 844], 'url': 'http://127.0.0.1:9000/screen.dc.html',
                'observed_at': '2026-09-13T05:00:00Z',
                'capture': self.pointer(self.build / 'original.png'),
                'trace': self.pointer(self.build / 'browser-trace.json'),
                'interactions': {'path': INTERACTIONS, 'sha256': '0' * 64}}

    def base_spec(self):
        return {'version': 1, 'reference_root': 'design-ref', 'manifests': ['source-manifest.json'],
                'scope': self.pointer(self.build / 'scope.md'), 'coverage_review': None,
                'cases': [{'id': 'related/list', 'screen': 'related', 'state': 'list',
                           'viewport': [390, 844], 'scope_refs': ['scope.md#관계-메뉴'],
                           'entrypoint': self.entrypoint(),
                           'reference_capture': self.pointer(self.build / 'original.png'),
                           'reached_by': {'interactions': INTERACTIONS, 'step': 1},
                           'source_observation': {'path': 'observation.json', 'sha256': '0' * 64}}]}

    def sync(self):
        """문서 → 관찰 → design-input 순으로 포인터 sha를 다시 묶는다."""
        (self.build / INTERACTIONS).write_text(json.dumps(self.doc, ensure_ascii=False), encoding='utf-8')
        self.write_observation('observation.json', self.observation, 0)
        if self.second is not None:
            self.write_observation('observation-2.json', self.second, 1)
        (self.build / 'design-input.json').write_text(json.dumps(self.spec, ensure_ascii=False),
                                                      encoding='utf-8')

    def write_observation(self, name, observation, index):
        if 'interactions' in observation:  # v1 관찰에는 없는 필드다
            observation['interactions'] = self.pointer(self.build / INTERACTIONS)
        (self.build / name).write_text(json.dumps(observation, ensure_ascii=False), encoding='utf-8')
        self.spec['cases'][index]['source_observation'] = self.pointer(self.build / name)

    def add_second_case(self):
        """같은 interactions.json을 자기 관찰로 가리키는 두 번째 case(정상 운용)."""
        capture = self.build / 'original-2.png'
        capture.write_bytes(png())
        self.spec['cases'].append({
            'id': 'related/other', 'screen': 'related', 'state': 'other',
            'viewport': [390, 844], 'scope_refs': ['scope.md#표면'], 'entrypoint': self.entrypoint(),
            'reference_capture': self.pointer(capture),
            'reached_by': {'interactions': INTERACTIONS, 'step': 3},
            'source_observation': {'path': 'observation-2.json', 'sha256': '0' * 64}})
        self.second = {'version': 2, 'archive_sha256': sha(self.manifest), 'entrypoint': self.entrypoint(),
                       'case_id': 'related/other', 'screen': 'related', 'state': 'other',
                       'viewport': [390, 844], 'url': 'http://127.0.0.1:9000/screen.dc.html',
                       'observed_at': '2026-09-13T05:10:00Z', 'capture': self.pointer(capture),
                       'trace': self.pointer(self.build / 'browser-trace.json'),
                       'interactions': {'path': INTERACTIONS, 'sha256': '0' * 64}}
        self.sync()

    def run_gate(self, phase='prepare'):
        return subprocess.run([sys.executable, str(SCRIPTS / 'check_design_evidence.py'),
                               '--build', str(self.build), '--project-root', str(self.project),
                               '--phase', phase], capture_output=True, text=True, timeout=60)

    def review(self):
        result = self.run_gate('prepare')
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)['review_digest']
        (self.build / 'coverage-review.md').write_text(
            f'reviewed-input: {value}\nreview-result: pass\n원본을 직접 보고 대조했다.\n', encoding='utf-8')
        self.spec['coverage_review'] = self.pointer(self.build / 'coverage-review.md')
        self.sync()

    def reject(self, *fragments, phase='prepare', code=2):
        result = self.run_gate(phase)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        for fragment in fragments:
            self.assertIn(fragment, result.stderr)
        return result

    # ---- 정상 통과 ---------------------------------------------------
    def test_complete_v2_interaction_evidence_passes(self):
        self.assertEqual(self.run_gate('prepare').returncode, 0, self.run_gate('prepare').stderr)
        self.review()
        result = self.run_gate('inputs')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_shared_document_binds_every_case(self):
        """한 문서를 두 case가 공유해도 case별 결속(viewport·entrypoint)은 case마다 걸린다."""
        self.add_second_case()
        self.assertEqual(self.run_gate('prepare').returncode, 0, self.run_gate('prepare').stderr)
        other = self.pointer(self.ref / 'other.dc.html', self.ref)
        for mutation in ('viewport', 'entrypoint'):
            with self.subTest(mutation=mutation):
                self.spec['cases'][1]['viewport'] = [390, 844]
                self.second['viewport'] = [390, 844]
                self.spec['cases'][1]['entrypoint'] = self.entrypoint()
                self.second['entrypoint'] = self.entrypoint()
                if mutation == 'viewport':
                    self.spec['cases'][1]['viewport'] = [560, 1040]
                    self.second['viewport'] = [560, 1040]
                else:
                    self.spec['cases'][1]['entrypoint'] = other
                    self.second['entrypoint'] = other
                self.sync()
                result = self.reject('related/other')
                self.assertIn('content_crop' if mutation == 'viewport' else 'entrypoint', result.stderr)

    def test_initial_reached_by_with_surface_exception_passes(self):
        self.spec['cases'][0]['reached_by'] = {'interactions': INTERACTIONS, 'step': 'initial'}
        self.spec['cases'][0]['reference_capture'] = self.pointer(self.build / 'original.png')
        self.spec['interaction_exclusions'] = [
            {'surface': 'sf1', 'scope_ref': 'scope.md#표면', 'approval_quote': SURFACE_QUOTE}]
        self.sync()
        result = self.run_gate('prepare')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(SURFACE_QUOTE, result.stderr)
        self.assertIn('review_digest', json.loads(result.stdout))

    # ---- 잔여 ---------------------------------------------------------
    def test_residual_unit_blocks_with_tuple_in_message(self):
        self.doc['steps'] = [s for s in self.doc['steps'] if s['n'] != 8]
        self.sync()
        result = self.reject('opt-b')
        self.assertIn('select', result.stderr)
        self.assertIn("'b'", result.stderr)

    def test_failed_status_is_not_execution(self):
        for status in ('failed', 'unreachable', 'unclickable'):
            with self.subTest(status=status):
                self.doc = self.base_doc()
                for step in self.doc['steps']:
                    if step['n'] == 8:
                        step['status'] = status
                        step['error'] = '재생 실패'
                        step['after'] = None
                self.sync()
                self.reject('opt-b')

    def test_partial_with_residual_names_caps_and_count(self):
        self.doc['partial'] = True
        self.doc['caps_hit'] = ['max_steps']
        self.doc['steps'] = [s for s in self.doc['steps'] if s['n'] != 8]
        self.sync()
        result = self.reject('max_steps')
        self.assertIn('잔여 1건', result.stderr)

    def test_partial_without_residual_passes_with_stderr_notice(self):
        self.doc['partial'] = True
        self.doc['caps_hit'] = ['max_minutes']
        self.sync()
        result = self.run_gate('prepare')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('partial(caps_hit=max_minutes)', result.stderr)
        self.assertIn('잔여 0', result.stderr)
        self.assertIn('review_digest', json.loads(result.stdout))  # stdout은 순수 JSON이다

    def test_partial_false_with_caps_hit_blocks(self):
        self.doc['caps_hit'] = ['max_depth']
        self.sync()
        self.reject('caps_hit')

    # ---- step 정합 ----------------------------------------------------
    def test_executed_step_cannot_carry_error(self):
        self.doc['steps'][0]['error'] = '무언가 잘못됐다'
        self.sync()
        self.reject('error')

    def test_step_path_must_name_known_targets(self):
        self.doc['steps'][0]['path'] = ['ghost', 'btn']
        self.sync()
        self.reject('path')

    def test_executed_step_needs_an_active_target(self):
        for mutation in ('enabled', 'occluded'):
            with self.subTest(mutation=mutation):
                self.doc = self.base_doc()
                for row in self.doc['steps'][0]['before']['inventory']:
                    if row['id'] == 'btn':
                        row['enabled'] = mutation != 'enabled'
                        row['occluded'] = mutation == 'occluded'
                self.sync()
                self.reject('비활성·가림 대상', 'btn')

    def test_duplicate_step_number_blocks(self):
        self.doc['steps'][1]['n'] = 1
        self.sync()
        self.reject('duplicate step number')

    def test_unknown_step_field_blocks(self):
        self.doc['steps'][0]['exempt'] = True
        self.sync()
        self.reject('steps[0]', 'exempt')

    def test_navigated_step_must_end_the_state(self):
        self.doc['steps'][0]['navigated'] = 'http://127.0.0.1:9000/next.dc.html'
        self.sync()
        self.reject('navigated')

    def test_capture_is_kept_for_added_surfaces_only(self):
        capture = {'path': STEP_CAPTURE, 'sha256': sha(self.build / STEP_CAPTURE)}
        for mutation in ('missing', 'extra'):
            with self.subTest(mutation=mutation):
                self.doc = self.base_doc()
                if mutation == 'missing':
                    del self.doc['steps'][0]['after']['capture']
                else:
                    self.doc['steps'][4]['after']['capture'] = capture
                self.sync()
                self.reject('capture')

    def test_unreachable_replay_without_state_hash_passes(self):
        """재생에 실패해 상태를 못 본 step은 before.state_hash가 null일 수 있다(Ruling)."""
        form = self.doc['steps'][8]['before']['inventory']
        self.doc['steps'].append({
            'n': 15, 'path': ['f1'], 'target': 'f1', 'action': 'click', 'option': None, 'value': None,
            'context': 'ctx-15', 'status': 'unreachable', 'error': '재생 종점 해시가 달라졌다',
            'before': {'inventory': form, 'state_hash': None}, 'after': None,
            'changes': {'added': [], 'removed': [], 'values': []}, 'navigated': None, 'discovery': False})
        self.sync()
        result = self.run_gate('prepare')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_navigated_step_ends_the_document_without_capture(self):
        """이탈 step은 after: null·PNG 없음이 정상이다(K2)."""
        form = self.doc['steps'][8]['before']['inventory']
        self.doc['steps'].append({
            'n': 15, 'path': ['btn'], 'target': 'btn', 'action': 'click', 'option': None, 'value': None,
            'context': 'ctx-15', 'status': 'executed', 'error': None,
            'before': {'inventory': form, 'state_hash': 'state-14'}, 'after': None,
            'changes': {'added': [], 'removed': [], 'values': []},
            'navigated': 'http://127.0.0.1:9000/other.dc.html', 'discovery': False})
        self.sync()
        result = self.run_gate('prepare')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_initial_capture_is_checked_and_enters_the_digest(self):
        _spec, _digest, items = gate.validate_inputs(self.build, self.project, require_review=False)
        self.assertIn(('interaction-capture/original.png', (self.build / 'original.png').read_bytes()),
                      items)
        self.doc['initial']['capture'] = {'path': 'captures/missing.png', 'sha256': '0' * 64}
        self.sync()
        self.reject('initial.capture')

    def test_value_is_a_native_select_option_field_only(self):
        for target_id in ('btn', 'menu-opt'):
            with self.subTest(target=target_id):
                self.doc = self.base_doc()
                if target_id == 'btn':
                    self.doc['targets']['btn']['value'] = 'x'
                else:  # owner가 native select가 아닌 option(메뉴 항목)
                    self.doc['targets']['menu-opt'] = target('option', '메뉴항목', 'option', 'ovl',
                                                             value='x')
                self.sync()
                self.reject(target_id, 'value')

    # ---- 신뢰 경계 ----------------------------------------------------
    def test_collector_bytes_must_match_the_plugin(self):
        for field in ('snippet_sha256', 'driver_sha256'):
            with self.subTest(field=field):
                self.doc = self.base_doc()
                self.doc['collector'][field] = '1' * 64
                self.sync()
                self.reject(field)

    def test_root_selector_must_follow_screen_meta(self):
        self.doc['root']['selector'] = '[data-screen-label="다른화면"]'
        self.sync()
        self.reject('data-screen-label')

    def test_outside_root_count_is_a_defect_even_with_declarations(self):
        """스니펫 scanOutsideRoot가 excluded_regions 매칭을 이미 count에서 뺀다 — 문서의 count는
        «선언으로 닫히지 않은 잔여»이므로 선언 행이 있어도 count>0은 결함이다(최종 리뷰 검사기 I4)."""
        for declared in ([], [{'selector': '#toolbar', 'reason': '공용 툴바'}]):
            with self.subTest(declared=len(declared)):
                self.doc = self.base_doc()
                self.doc['outside_root'] = {'count': 2, 'sample': ['저장', '취소']}
                self.doc['excluded_regions'] = declared
                self.sync()
                result = self.reject('outside_root', '2개')
                self.assertIn(f'선언 {len(declared)}행', result.stderr)

    def test_mixed_checked_is_a_toggle_state(self):
        """aria-checked="mixed"(3상태 체크박스) — 스니펫 checkedOf가 'mixed'를 내므로 검사기도
        checked에 true|false|"mixed"|null을 허용하고, 잔여는 그 값을 하나의 관찰 상태로 센다."""
        targets = {'all': target('checkbox', '전체 선택', 'checkbox')}
        issues: list[str] = []
        gate._check_inventory([entry('all', checked='mixed')], targets, 'inv', issues)
        self.assertEqual(issues, [])
        gate._check_inventory([entry('all', checked='yes')], targets, 'inv', issues)
        self.assertEqual(len(issues), 1, issues)
        self.assertIn('"mixed"', issues[0])
        self.assertEqual(gate._required_units(targets['all'], ['mixed', True, False, 'mixed'], targets),
                         [('click', 'mixed'), ('click', True), ('click', False)])
        # 게이트 전 구간 — form 상태의 «동의»가 mixed로 관찰되면 그 상태에서 누른 step의 option도
        # 'mixed'다(드라이버는 before의 관찰값을 option으로 적는다).
        for step in self.doc['steps']:
            for side in ('before', 'after'):
                for row in step[side]['inventory']:
                    if row['id'] == 'agree' and row['checked'] is False:
                        row['checked'] = 'mixed'
            if step['n'] == 5:
                step['option'] = 'mixed'
        for row in self.doc['initial']['inventory']:
            if row['id'] == 'agree':
                row['checked'] = 'mixed'
        self.sync()
        result = self.run_gate('prepare')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_root_scroll_container_limit_row_uses_dot(self):
        """루트 자체가 스크롤 컨테이너면 드라이버는 dom_path를 '.'로 적는다(스니펫의 ''는 검사기의
        nonempty 요구와 어긋난다 — 최종 리뷰 검사기 I1). '.'는 통과, ''는 결함."""
        self.doc['discovery_limits'] = [{'kind': 'scroll-container', 'dom_path': '.',
                                         'reason': '7 위치를 훑어 재인벤토리했다(활성이 된 대상 0)(훑은 상태 1)'}]
        self.sync()
        result = self.run_gate('prepare')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.doc['discovery_limits'][0]['dom_path'] = ''
        self.sync()
        self.reject('discovery_limits[0]')

    def test_content_crop_must_equal_case_viewport(self):
        self.doc['content_crop'] = {'x': 85, 'y': 40, 'w': 300, 'h': 844}
        self.sync()
        self.reject('content_crop')

    def test_served_entrypoint_is_required_and_byte_equal(self):
        for mutation in ('missing', 'variant', 'unknown'):
            with self.subTest(mutation=mutation):
                self.doc = self.base_doc()
                if mutation == 'missing':
                    del self.doc['served']['screen.dc.html']
                elif mutation == 'variant':
                    self.doc['served']['screen.dc.html'] = '2' * 64
                else:
                    self.doc['served']['ghost.js'] = '3' * 64
                self.sync()
                self.reject('served')

    def test_served_url_basename_must_match_entrypoint(self):
        self.doc['url'] = 'http://127.0.0.1:9000/%EB%8B%A4%EB%A5%B8.dc.html'
        self.sync()
        self.reject('url')

    def test_observed_at_requires_timezone(self):
        self.doc['observed_at'] = '2026-09-13T05:00:00'
        self.sync()
        self.reject('observed_at')

    def test_environment_error_is_not_a_defect_but_an_unrun_check(self):
        self.doc['environment_error'] = '외부 번들 404'
        self.sync()
        self.reject('environment_error', code=1)

    # ---- 동결 연결 ----------------------------------------------------
    def test_added_surface_must_be_reached_by_a_case(self):
        self.doc['steps'][2]['after']['surface_key'] = 'sf2'
        self.sync()
        self.reject('sf2')

    def test_archive_case_requires_reached_by(self):
        del self.spec['cases'][0]['reached_by']
        self.sync()
        self.reject('reached_by')

    def test_reached_by_capture_must_be_the_frozen_bytes(self):
        other = self.build / 'captures' / 'other.png'
        other.write_bytes(png(b'\0\0\xff'))
        self.doc['steps'][0]['after']['capture'] = {'path': 'captures/other.png', 'sha256': sha(other)}
        self.doc['steps'][2]['after']['capture'] = {'path': 'captures/other.png', 'sha256': sha(other)}
        self.sync()
        self.reject('reference_capture')

    def test_reached_by_must_name_an_existing_step(self):
        self.spec['cases'][0]['reached_by'] = {'interactions': INTERACTIONS, 'step': 99}
        self.sync()
        self.reject('reached_by')

    def test_static_case_cannot_declare_reached_by(self):
        image = self.pointer(self.ref / 'support.js', self.ref)
        self.spec['cases'].append({'id': 'related/asset', 'screen': 'related', 'state': 'asset',
                                   'viewport': [390, 844], 'scope_refs': ['scope.md#표면'],
                                   'entrypoint': image,
                                   'reference_capture': self.pointer(self.build / 'original.png'),
                                   'reached_by': {'interactions': INTERACTIONS, 'step': 1}})
        self.sync()
        self.reject('reached_by')

    # ---- 예외 --------------------------------------------------------
    def test_exclusion_row_opens_one_unit_and_is_printed(self):
        self.doc['steps'] = [s for s in self.doc['steps'] if s['n'] != 8]
        self.spec['interaction_exclusions'] = [
            {'target': 'opt-b', 'action': 'select', 'option': 'b',
             'scope_ref': 'scope.md#관계-메뉴', 'approval_quote': UNIT_QUOTE}]
        self.sync()
        result = self.run_gate('prepare')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(UNIT_QUOTE, result.stderr)
        self.assertIn('opt-b', result.stderr)
        self.assertIn('review_digest', json.loads(result.stdout))

    def test_exclusion_rows_are_rejected_without_real_user_approval(self):
        rows = {
            'quote-absent': {'target': 'opt-b', 'action': 'select', 'option': 'b',
                             'scope_ref': 'scope.md#관계-메뉴', 'approval_quote': '없는문구를열자이상적는다'},
            'quote-short': {'target': 'opt-b', 'action': 'select', 'option': 'b',
                            'scope_ref': 'scope.md#관계-메뉴', 'approval_quote': UNIT_QUOTE[:9]},
            'anchor-absent': {'target': 'opt-b', 'action': 'select', 'option': 'b',
                              'scope_ref': 'scope.md#없는앵커', 'approval_quote': UNIT_QUOTE},
            'shape': {'target': 'opt-b', 'action': 'select', 'scope_ref': 'scope.md#관계-메뉴',
                      'approval_quote': UNIT_QUOTE},
        }
        self.assertEqual(len(UNIT_QUOTE[:9]), 9)
        for name, row in rows.items():
            with self.subTest(row=name):
                self.doc = self.base_doc()
                self.doc['steps'] = [s for s in self.doc['steps'] if s['n'] != 8]
                self.spec['interaction_exclusions'] = [row]
                self.sync()
                self.reject('interaction_exclusions')

    def test_exclusion_rows_stay_under_a_tenth_of_active_targets(self):
        self.doc = self.base_doc()
        self.doc['steps'] = [s for s in self.doc['steps'] if s['n'] not in (8, 14)]
        for block in [self.doc['initial']] + [s['before'] for s in self.doc['steps']] + \
                     [s['after'] for s in self.doc['steps']]:
            block['inventory'] = [row for row in block['inventory'] if row['id'] != 'f6']
        del self.doc['targets']['f6']
        self.spec['interaction_exclusions'] = [
            {'target': 'opt-b', 'action': 'select', 'option': 'b',
             'scope_ref': 'scope.md#관계-메뉴', 'approval_quote': UNIT_QUOTE}]
        self.sync()
        self.reject('10%')

    # ---- manifest·design-input 확장 ------------------------------------
    def test_manifest_row_accepts_carried_from_only(self):
        for field, value in (('carried_from', '4' * 64), ('carried_from', 'not-a-sha'), ('foo', 'bar')):
            with self.subTest(field=field, value=value[:8]):
                manifest = json.loads(self.manifest.read_text())
                for row in manifest['files']:
                    if row['local_path'] == 'support.js':
                        row.pop('carried_from', None)
                        row.pop('foo', None)
                        row[field] = value
                self.manifest.write_text(json.dumps(manifest, ensure_ascii=False), encoding='utf-8')
                self.doc = self.base_doc()
                self.doc['archive_sha256'] = sha(self.manifest)
                self.observation['archive_sha256'] = sha(self.manifest)
                self.sync()
                result = self.run_gate('prepare')
                expected = 0 if (field, value) == ('carried_from', '4' * 64) else 2
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

    def test_v1_observation_passes_only_in_legacy_mode(self):
        self.observation = {key: value for key, value in self.observation.items()
                            if key != 'interactions'}
        self.observation['version'] = 1
        del self.spec['cases'][0]['reached_by']
        self.sync()
        with self.assertRaises(gate.Defects) as blocked:
            gate.validate_inputs(self.build, self.project, require_review=False)
        self.assertTrue(any('interaction evidence required' in message
                            for message in blocked.exception.messages), blocked.exception.messages)
        spec, digest, _items = gate.validate_inputs(self.build, self.project, require_review=False,
                                                    legacy_v1=True)
        self.assertEqual(spec['version'], 1)
        self.assertEqual(len(digest), 64)

    def test_backstop_is_silent_about_legacy_v1_for_a_git_clean_v2_build(self):
        """`[info] legacy v1 observation` 통지는 관찰 문서가 실제로 v1일 때만 낸다(Task 6 리뷰 Concern 2) —
        git-clean이라 legacy_v1_allowed가 True여도 v2 빌드면 침묵한다."""
        import backstop  # noqa: E402  — SCRIPTS가 sys.path에 있다
        self.review()
        parsed, input_digest, _items = gate.validate_inputs(self.build, self.project)
        impl_digest = gate.implementation_digest(self.project, parsed)
        (self.build / 'visual-check.md').write_text('Compared directly with the original.\n', encoding='utf-8')
        (self.build / 'implementation.png').write_bytes(png())
        visual = {'version': 1, 'input_digest': input_digest, 'implementation_digest': impl_digest,
                  'visual_check': self.pointer(self.build / 'visual-check.md'),
                  'cases': [{'id': 'related/list', 'url': 'http://127.0.0.1/related', 'viewport': [390, 844],
                             'capture': self.pointer(self.build / 'implementation.png'), 'result': 'pass'}]}
        (self.build / 'visual-evidence.json').write_text(json.dumps(visual, ensure_ascii=False), encoding='utf-8')
        # 빌드를 프로젝트 안 .dddjango-web/ 아래로 옮겨 커밋한다 — legacy v1 게이트(추적·무변경)의 전제.
        tracked = self.project / '.dddjango-web' / 'v2'
        shutil.copytree(self.build, tracked)
        for args in (['init', '-q'], ['config', 'user.email', 'v2@example.invalid'],
                     ['config', 'user.name', 'V2 Test'], ['add', '-A'], ['commit', '-qm', 'v2 build']):
            subprocess.run(['git', '-C', str(self.project), *args], check=True, capture_output=True)
        self.assertTrue(backstop.legacy_v1_allowed(self.project, tracked, None))  # 허용 조건은 갖췄다
        result = subprocess.run([sys.executable, str(SCRIPTS / 'backstop.py'), str(self.project),
                                 '--all', '--only', 'zz'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('blocker 0건', result.stdout)
        self.assertNotIn('legacy v1 observation', result.stdout + result.stderr)

    def test_digest_takes_interactions_declared_and_step_captures_once(self):
        _spec, _digest, items = gate.validate_inputs(self.build, self.project, require_review=False)
        names = [name for name, _data in items]
        self.assertEqual(names.count(f'interactions/{INTERACTIONS}'), 1)
        self.assertEqual(names.count(f'interaction-capture/{STEP_CAPTURE}'), 1)
        self.assertIn((f'interaction-capture/{STEP_CAPTURE}', (self.build / STEP_CAPTURE).read_bytes()),
                      items)
        first = json.loads(self.run_gate('prepare').stdout)['review_digest']
        self.doc['declared'] = [{'selector': '[data-role=grip]', 'reason': '비의미 핸들러'}]
        self.doc['declared_unmatched'] = [{'selector': '[data-role=grip]', 'reason': '비의미 핸들러'}]
        self.sync()
        second = json.loads(self.run_gate('prepare').stdout)['review_digest']
        self.assertNotEqual(first, second)

    # ---- 한 표·두 구현 -------------------------------------------------
    def test_python_residual_equals_the_javascript_snippet(self):
        documents = {path.name: json.loads(path.read_text(encoding='utf-8'))
                     for path in sorted(FIXTURES.glob('expected/*.json'))}
        documents['r3-steps.json'] = json.loads((FIXTURES / 'r3-steps.json').read_text(encoding='utf-8'))
        documents['fixture-base.json'] = self.base_doc()
        partial = copy.deepcopy(self.base_doc())
        partial['steps'] = [s for s in partial['steps'] if s['n'] not in (2, 4, 5, 8)]
        documents['fixture-residual.json'] = partial
        # 8 = expected/*.json 5(register·edit·cascade·handler-toggle + mixed — aria-checked="mixed"
        # 3상태를 두 구현이 같은 관찰 상태로 세는지 고정, 최종 리뷰 검사기 I3) + r3 + base + residual.
        self.assertEqual(len(documents), 8)
        for name, document in documents.items():
            with self.subTest(document=name):
                expected = node_residual(document)
                actual = [list(unit) for unit in gate.interaction_residual(document)]
                self.assertEqual(actual, expected)

    def test_named_handler_is_a_surface_toggle(self):
        """D-H — 이름이 있는(대상 후손이 없는) handler는 관찰된 surface마다 click 단위다(K1)."""
        document = json.loads((FIXTURES / 'expected' / 'doc-handler-toggle.json').read_text(encoding='utf-8'))
        self.assertEqual(gate.interaction_residual(document),
                         [('leap-label', 'click', 'b' * 64)])
        # 이름이 빈 handler(컨테이너 — D-A)는 surface가 관찰돼도 click 1회다.
        container = {'kind': 'handler', 'name': ''}
        self.assertEqual(gate._required_units(container, ['a' * 64, 'b' * 64], {}), [('click', None)])
        named = {'kind': 'handler', 'name': '윤달'}
        self.assertEqual(gate._required_units(named, ['a' * 64, 'b' * 64, 'a' * 64], {}),
                         [('click', 'a' * 64), ('click', 'b' * 64)])
        # aria-label로 이름이 남은 컨테이너 handler(대상 후손이 있다)도 토글형이 아니다.
        nested = {'cover': {'kind': 'handler', 'name': '덮개', 'dom_path': 'span:nth-of-type(1)'},
                  'inner': {'kind': 'button', 'name': '덮개 안 버튼',
                            'dom_path': 'span:nth-of-type(1)/button:nth-of-type(1)'}}
        self.assertEqual(gate._required_units(nested['cover'], ['a' * 64, 'b' * 64], nested),
                         [('click', None)])
        sibling = {'leap': {'kind': 'handler', 'name': '윤달', 'dom_path': 'div:nth-of-type(1)'},
                   'other': {'kind': 'button', 'name': '저장',
                             'dom_path': 'div:nth-of-type(11)/button:nth-of-type(1)'}}
        self.assertEqual(gate._required_units(sibling['leap'], ['a' * 64, 'b' * 64], sibling),
                         [('click', 'a' * 64), ('click', 'b' * 64)])

    def test_r3_log_fixture_keeps_the_unclicked_menu_items(self):
        document = json.loads((FIXTURES / 'r3-steps.json').read_text(encoding='utf-8'))
        counts = {}
        for unit in gate.interaction_residual(document):
            owner = document['targets'][unit[0]].get('owner') or unit[0]
            counts[owner] = counts.get(owner, 0) + 1
        self.assertGreaterEqual(counts.get('rel-trigger', 0), 4)
        self.assertGreaterEqual(counts.get('sido-trigger', 0), 15)
        self.assertGreaterEqual(counts.get('sigungu-trigger', 0), 30)

    def test_linked_surfaces_and_collector_helpers(self):
        self.assertEqual(gate.linked_surfaces(self.doc), {'sf1'})
        self.assertTrue(gate.collector_assets_ok(self.doc, ASSETS))
        self.doc['collector']['driver_sha256'] = '5' * 64
        self.assertFalse(gate.collector_assets_ok(self.doc, ASSETS))


if __name__ == '__main__':
    unittest.main()
