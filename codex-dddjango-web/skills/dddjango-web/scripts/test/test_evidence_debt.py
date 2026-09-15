"""evidence_debt 술어 단위 테스트 — 구조 판정(메시지 grep 없음)·대상 한정·사유 분류·결정 분류·검사기 단일 출처."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import evidence_debt  # noqa: E402


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')


def observation(version: int, *, interactions: bool = True) -> dict:
    doc = {'version': version, 'archive_sha256': '0' * 64, 'entrypoint': 'login.dc.html',
           'case_id': 'c1', 'screen': 'login', 'state': 'initial', 'viewport': [390, 844],
           'url': 'http://127.0.0.1:1/login.dc.html', 'observed_at': '2026-09-15T00:00:00+00:00',
           'capture': {'path': 'captures/c1.png', 'sha256': '0' * 64},
           'trace': {'path': 'captures/c1-trace.json', 'sha256': '0' * 64}}
    if version == 2 and interactions:
        doc['interactions'] = {'path': 'captures/login-interactions.json', 'sha256': '0' * 64}
    return doc


def make_build(root: Path, name: str, *, archive: bool = True, design_status: str | None = 'ready',
               observations: list | None = None, decision: dict | None = None,
               build_state: bool = True, pointer_keys: set | None = None) -> Path:
    """observations: 항목마다 dict(관찰 문서) | 'missing' | 'broken' | 'escape' | 'nopointer'."""
    build = root / '.dddjango-web' / name
    build.mkdir(parents=True)
    write_json(build / 'source-manifest.json',
               {'version': 1, 'collection': 'archive' if archive else 'static', 'files': []})
    cases = []
    for index, spec in enumerate(observations if observations is not None else [observation(2)]):
        case = {'id': f'c{index}', 'screen': 'login', 'state': 'initial', 'viewport': [390, 844],
                'entrypoint': 'login.dc.html'}
        rel = f'captures/c{index}-source-observation.json'
        pointer = {'path': rel, 'sha256': '0' * 64}
        if pointer_keys is not None:
            pointer = {key: pointer.get(key, 'x') for key in pointer_keys}
        if spec == 'nopointer':
            pass
        elif spec == 'escape':
            case['source_observation'] = {'path': '../outside.json', 'sha256': '0' * 64}
        elif spec == 'missing':
            case['source_observation'] = pointer
        elif spec == 'broken':
            case['source_observation'] = pointer
            (build / rel).parent.mkdir(parents=True, exist_ok=True)
            (build / rel).write_text('{not json', encoding='utf-8')
        else:
            case['source_observation'] = pointer
            write_json(build / rel, spec)
        cases.append(case)
    write_json(build / 'design-input.json',
               {'version': 1, 'reference_root': 'design-ref', 'manifests': ['source-manifest.json'],
                'scope': {}, 'coverage_review': {}, 'cases': cases})
    if build_state:
        state = {'phase': 'implement', 'design_status': design_status}
        if decision is not None:
            state['evidence_debt'] = decision
        write_json(build / 'build-state.json', state)
    return build


class Predicates(unittest.TestCase):
    def test_loose_predicate_truth_table(self) -> None:
        loose = evidence_debt.is_interaction_observation
        self.assertTrue(loose(observation(2)))
        self.assertFalse(loose(observation(1)))
        self.assertFalse(loose(observation(2, interactions=False)))
        self.assertFalse(loose(None))
        self.assertFalse(loose({'version': '2', 'interactions': {}}))

    def test_strict_predicate_rejects_what_checker_rejects(self) -> None:
        strict = evidence_debt.has_interaction_evidence
        self.assertTrue(strict(observation(2)))
        self.assertFalse(strict(observation(1)))
        extra = dict(observation(2), unknown='x')
        self.assertFalse(strict(extra))
        short = observation(2)
        del short['trace']
        self.assertFalse(strict(short))
        null_pointer = dict(observation(2), interactions=None)
        self.assertFalse(strict(null_pointer))
        bad_pointer = dict(observation(2), interactions={'path': 'x'})
        self.assertFalse(strict(bad_pointer))


class BuildDebtCases(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_v2_with_interactions_is_clear(self) -> None:
        build = make_build(self.root, 'a', observations=[observation(2), observation(2)])
        debt = evidence_debt.build_debt(build)
        self.assertIsNotNone(debt)
        self.assertEqual((debt.cases_total, debt.cases_debt, debt.status), (2, 0, 'clear'))

    def test_v1_is_static_only_debt_and_undecided(self) -> None:
        build = make_build(self.root, 'a', observations=[observation(1), observation(2)])
        debt = evidence_debt.build_debt(build)
        self.assertEqual((debt.cases_total, debt.cases_debt, debt.status), (2, 1, 'undecided'))
        self.assertEqual(debt.reasons, {'static_only': 1, 'missing': 0, 'unreadable': 0, 'malformed': 0})

    def test_v2_without_interactions_key_is_malformed_debt(self) -> None:
        build = make_build(self.root, 'a', observations=[observation(2, interactions=False)])
        debt = evidence_debt.build_debt(build)
        self.assertEqual((debt.cases_debt, debt.reasons['malformed']), (1, 1))

    def test_missing_broken_escape_nopointer_reasons(self) -> None:
        build = make_build(self.root, 'a', observations=['missing', 'broken', 'escape', 'nopointer'])
        debt = evidence_debt.build_debt(build)
        self.assertEqual((debt.cases_total, debt.cases_debt, debt.status), (4, 4, 'undecided'))
        self.assertEqual(debt.reasons, {'static_only': 0, 'missing': 3, 'unreadable': 1, 'malformed': 0})

    def test_pointer_key_set_must_be_exact(self) -> None:
        extra = make_build(self.root, 'x', observations=[observation(2)], pointer_keys={'path', 'sha256', 'note'})
        self.assertEqual(evidence_debt.build_debt(extra).reasons['missing'], 1)
        short = make_build(self.root, 's', observations=[observation(2)], pointer_keys={'path'})
        self.assertEqual(evidence_debt.build_debt(short).reasons['missing'], 1)

    def test_observation_field_set_must_be_exact(self) -> None:
        build = make_build(self.root, 'a', observations=[dict(observation(2), unknown='x'), dict(observation(2), interactions=None)])
        debt = evidence_debt.build_debt(build)
        self.assertEqual((debt.cases_debt, debt.reasons['malformed']), (2, 2))

    def test_absolute_pointer_is_missing(self) -> None:
        build = make_build(self.root, 'a', observations=[observation(2)])
        spec = json.loads((build / 'design-input.json').read_text(encoding='utf-8'))
        spec['cases'][0]['source_observation']['path'] = str(build / 'captures' / 'c0-source-observation.json')
        write_json(build / 'design-input.json', spec)
        self.assertEqual(evidence_debt.build_debt(build).reasons['missing'], 1)

    def test_static_collection_not_applicable(self) -> None:
        build = make_build(self.root, 'a', archive=False, observations=[observation(1)])
        self.assertIsNone(evidence_debt.build_debt(build))

    def test_not_ready_or_no_build_state_not_applicable(self) -> None:
        pending = make_build(self.root, 'p', design_status='pending', observations=[observation(1)])
        self.assertIsNone(evidence_debt.build_debt(pending))
        none = make_build(self.root, 'n', design_status=None, observations=[observation(1)])
        self.assertIsNone(evidence_debt.build_debt(none))
        absent = make_build(self.root, 's', build_state=False, observations=[observation(1)])
        self.assertIsNone(evidence_debt.build_debt(absent))

    def test_no_design_input_not_applicable(self) -> None:
        folder = self.root / '.dddjango-web' / 'x'
        folder.mkdir(parents=True)
        self.assertIsNone(evidence_debt.build_debt(folder))

    def test_decision_classification(self) -> None:
        defer = {'decision': 'defer', 'at': '2026-09-15T10:00:00+09:00', 'quote': '지금은 재동결만 확인하자', 'reason': 'r', 'cases': 1}
        observe = {'decision': 'observe', 'at': '2026-09-15T10:00:00+09:00', 'quote': '드라이버 돌려서 다 수집해', 'reason': 'r', 'cases': 1}
        d = evidence_debt.build_debt(make_build(self.root, 'd', observations=[observation(1)], decision=defer))
        o = evidence_debt.build_debt(make_build(self.root, 'o', observations=[observation(1)], decision=observe))
        m = evidence_debt.build_debt(make_build(self.root, 'm', observations=[observation(1)], decision={'decision': 'later'}))
        self.assertEqual((d.status, d.decision['quote']), ('deferred', defer['quote']))
        self.assertEqual(o.status, 'observing')
        self.assertEqual((m.status, m.decision), ('undecided', None))

    def test_decision_ignored_when_clear(self) -> None:
        defer = {'decision': 'defer', 'at': 't', 'quote': 'q' * 10, 'reason': 'r', 'cases': 1}
        debt = evidence_debt.build_debt(make_build(self.root, 'a', observations=[observation(2)], decision=defer))
        self.assertEqual(debt.status, 'clear')

    def test_invalid_design_input_is_error(self) -> None:
        build = make_build(self.root, 'a')
        (build / 'design-input.json').write_text('{broken', encoding='utf-8')
        debt = evidence_debt.build_debt(build)
        self.assertEqual(debt.status, 'error')
        self.assertIn('design-input.json', debt.error)

    def test_unreadable_manifest_is_error(self) -> None:
        build = make_build(self.root, 'a')
        (build / 'source-manifest.json').unlink()
        self.assertEqual(evidence_debt.build_debt(build).status, 'error')

    def test_cases_not_list_is_error(self) -> None:
        build = make_build(self.root, 'a')
        spec = json.loads((build / 'design-input.json').read_text(encoding='utf-8'))
        spec['cases'] = {'not': 'list'}
        write_json(build / 'design-input.json', spec)
        self.assertEqual(evidence_debt.build_debt(build).status, 'error')


class CheckerParity(unittest.TestCase):
    """검사기 `_source_observation`의 필드 집합·version 판정이 같은 출처를 쓴다."""

    def test_checker_imports_predicate_and_field_sets(self) -> None:
        import check_design_evidence
        self.assertIs(check_design_evidence.is_interaction_observation, evidence_debt.is_interaction_observation)
        self.assertIs(check_design_evidence.OBSERVATION_V1_FIELDS, evidence_debt.OBSERVATION_V1_FIELDS)
        self.assertIs(check_design_evidence.OBSERVATION_V2_FIELDS, evidence_debt.OBSERVATION_V2_FIELDS)
        # 검사기 자체의 INTERACTION_FIELDS(interactions.json 문서 집합)는 관찰 문서 집합과 다른 상수다 — 겹치면 안 된다.
        self.assertNotEqual(set(check_design_evidence.INTERACTION_FIELDS), set(evidence_debt.OBSERVATION_V2_FIELDS))

    def test_strict_predicate_implies_checker_field_check_passes(self) -> None:
        doc = observation(2)
        self.assertTrue(evidence_debt.has_interaction_evidence(doc))
        self.assertEqual(set(doc), evidence_debt.OBSERVATION_V2_FIELDS)


if __name__ == '__main__':
    unittest.main()
