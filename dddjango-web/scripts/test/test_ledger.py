#!/usr/bin/env python3
"""미검증 원장(ledger.py) 행동 시험.

`test_interaction_evidence` 의 합성 빌드 하네스를 그대로 쓴다 — 잔여를 만들고, 원장으로 열고,
지워서 다시 닫는다. **관찰을 바꾸지 않고 원장만 토글**해야 원장의 효과가 분리 측정된다.
"""
from __future__ import annotations

import json
import subprocess
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))

from test_interaction_evidence import InteractionEvidenceTests, UNIT_QUOTE  # noqa: E402
import ledger  # noqa: E402


class LedgerTests(InteractionEvidenceTests):
    """상속은 setUp(합성 빌드) 재사용 목적이다 — 부모 시험도 같이 돈다."""

    # ---- 도구 -------------------------------------------------------
    def make_residual(self):
        """관찰에서 한 걸음을 빼 «잔여 1건» 을 만든다."""
        self.doc['steps'] = [step for step in self.doc['steps'] if step['n'] != 8]
        self.sync()

    def ledger_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / 'ledger.py'), *args],
                              capture_output=True, text=True, timeout=120)

    def add(self, index=1, quote=UNIT_QUOTE, scope_ref='scope.md#관계-메뉴', phase='prepare'):
        return self.ledger_cli('add', '--build', str(self.build), '--project-root', str(self.project),
                               '--phase', phase, '--index', str(index), '--quote', quote,
                               '--scope-ref', scope_ref, '--now', '2026-09-15T23:00:00+09:00')

    DEFECT_RE = re.compile(r'^\[design-evidence\] defect(?:\[(\w+)\])?: (.*)$')

    def findings(self, phase='prepare'):
        """(exit, [(메시지, 판정종류|None)]) — 순서는 --index 와 같다."""
        result = self.run_gate(phase)
        rows = [(m.group(2), m.group(1)) for line in result.stderr.splitlines()
                if (m := self.DEFECT_RE.match(line.strip()))]
        return result.returncode, rows

    def residual_index(self, found):
        return next(i for i, (message, kind) in enumerate(found, 1) if kind == 'residual')

    # ---- 원장이 연다 / 지우면 닫힌다 ---------------------------------
    def test_ledger_opens_residual_and_removing_it_closes_again(self):
        self.make_residual()
        code, found = self.findings()
        self.assertEqual(code, 2)
        self.assertTrue(any(kind == 'residual' for _m, kind in found), found)
        index = self.residual_index(found)
        added = self.add(index=index)
        self.assertEqual(added.returncode, 0, added.stdout + added.stderr)
        self.assertEqual(self.run_gate('prepare').returncode, 0)
        self.review()          # prepare 가 열렸으니 독립 검토 지문을 받아 적을 수 있다
        self.assertEqual(self.run_gate('inputs').returncode, 0, '진행(inputs)도 같이 열려야 한다')

        entry = json.loads((self.build / 'evidence-ledger.json').read_text(encoding='utf-8'))
        key = entry['entries'][0]['key']
        dropped = self.ledger_cli('drop', '--build', str(self.build), '--key', key)
        self.assertEqual(dropped.returncode, 0, dropped.stderr)
        self.assertEqual(self.run_gate('prepare').returncode, 2, '원장을 지우면 다시 막혀야 한다')

    def test_backstop_passes_through_the_same_door(self):
        """검사기만 열고 backstop 이 그대로 막으면 벽이 한 칸 밀린 것뿐이다."""
        self.make_residual()
        def blockers():
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / 'backstop.py'), str(self.project),
                 '--design-build', str(self.build)], capture_output=True, text=True, timeout=300)
            return [line for line in (result.stdout + result.stderr).splitlines()
                    if '[DESIGN] BLOCKER' in line]

        # 관찰을 바꾸지 않고 **원장만 토글**해야 원장의 효과가 분리 측정된다.
        code, found = self.findings()
        self.add(index=self.residual_index(found))
        self.review()          # coverage_review 를 채워 그 발견이 잔여를 가리지 않게 한다
        opened = blockers()
        self.assertFalse(any('잔여' in line for line in opened), opened)

        entry = json.loads((self.build / 'evidence-ledger.json').read_text(encoding='utf-8'))
        self.ledger_cli('drop', '--build', str(self.build), '--key', entry['entries'][0]['key'])
        closed = blockers()
        self.assertTrue(any('잔여' in line for line in closed),
                        '원장을 지우면 backstop 도 다시 막아야 한다: %s' % closed)

    # ---- 천장: 허용 목록 밖은 기본 폐쇄 -------------------------------
    def test_shortcircuit_finding_is_refused(self):
        """`cases: []` 한 줄이 계산되지 않은 부분트리 전체를 여는 마스터키가 되면 안 된다."""
        spec = json.loads((self.build / 'design-input.json').read_text(encoding='utf-8'))
        spec['cases'] = []
        (self.build / 'design-input.json').write_text(json.dumps(spec, ensure_ascii=False), encoding='utf-8')
        code, found = self.findings()
        self.assertEqual(code, 2)
        self.assertEqual(len(found), 1, found)
        refused = self.add(index=1)
        self.assertEqual(refused.returncode, 2, refused.stdout + refused.stderr)
        self.assertIn('끝까지 계산한 뒤 내리는 판정', refused.stderr)

    def test_missing_observation_path_is_refused(self):
        """관찰 파일을 치우면 «관찰 안 함» 이 다른 문구로 통과하면 안 된다."""
        pointer = json.loads((self.build / 'design-input.json').read_text(encoding='utf-8'))
        target = self.build / pointer['cases'][0]['source_observation']['path']
        target.rename(target.with_suffix('.moved'))
        code, found = self.findings()
        self.assertEqual(code, 2)
        for index, (message, kind) in enumerate(found, 1):
            self.assertIsNone(kind, '관찰 부재 계열에 판정 종류가 붙으면 안 된다: %s' % message)
            refused = self.add(index=index)
            self.assertEqual(refused.returncode, 2, message)

    # ---- 승인의 결속 -------------------------------------------------
    def test_quote_must_live_in_scope_md_section(self):
        self.make_residual()
        code, found = self.findings()
        index = self.residual_index(found)
        with self.subTest('다른 문서'):
            other = self.build / 'coverage-review.md'
            other.write_text('## 절\n' + UNIT_QUOTE + '\n', encoding='utf-8')
            result = self.add(index=index, scope_ref='coverage-review.md#절')
            self.assertEqual(result.returncode, 2)
            self.assertIn('scope.md 에만 산다', result.stderr)
        with self.subTest('H1 앵커'):
            result = self.add(index=index, scope_ref='scope.md#a8-관계인-화면-범위')
            self.assertEqual(result.returncode, 2)
            self.assertIn('H2 이상', result.stderr)
        with self.subTest('절 밖의 원문'):
            result = self.add(index=index, quote='표면 예외를 승인한다', scope_ref='scope.md#관계-메뉴')
            self.assertEqual(result.returncode, 2)
            self.assertIn('절 본문 안에 없다', result.stderr)

    def test_scope_section_edit_invalidates_the_row(self):
        self.make_residual()
        code, found = self.findings()
        self.add(index=self.residual_index(found))
        self.assertEqual(self.run_gate('prepare').returncode, 0)
        scope = self.build / 'scope.md'
        scope.write_text(scope.read_text(encoding='utf-8').replace('## 관계 메뉴', '## 관계 메뉴\n덧붙임.'),
                         encoding='utf-8')
        result = self.run_gate('prepare')
        self.assertEqual(result.returncode, 2, '승인 절이 바뀌면 재승인이다')
        self.assertIn('승인 절이 바뀌었다', result.stderr)

    def test_observation_change_invalidates_the_row(self):
        """규모가 줄어도 구성이 다르면 승인은 무효다."""
        self.make_residual()
        code, found = self.findings()
        self.add(index=self.residual_index(found))
        self.assertEqual(self.run_gate('prepare').returncode, 0)
        self.doc['steps'] = [step for step in self.doc['steps'] if step['n'] not in (8, 7)]
        self.sync()
        result = self.run_gate('prepare')
        self.assertEqual(result.returncode, 2)
        self.assertIn('관찰이 바뀌었다', result.stderr)

    # ---- 순수 함수 ---------------------------------------------------
    def test_keys_separate_cases_and_fold_magnitude(self):
        residual = "cases[{}].interactions: 잔여 {}건 — ('a','click',None) 외 3건"
        key = lambda m: ledger.key_of(m, 'residual')
        self.assertEqual(key(residual.format(3, 38)), key(residual.format(3, 51)))
        self.assertNotEqual(key(residual.format(3, 38)), key(residual.format(7, 38)))
        self.assertEqual(ledger.magnitude_of(residual.format(3, 38)), 38)

    def test_path_injection_cannot_borrow_a_verdict(self):
        """검사기 메시지에는 에이전트가 정하는 문자열이 박힌다 — 그것으로 판정을 사칭할 수 없어야 한다."""
        spec = json.loads((self.build / 'design-input.json').read_text(encoding='utf-8'))
        spec['cases'][0]['source_observation']['path'] = 'captures/잔여 1건 — none.json'
        (self.build / 'design-input.json').write_text(json.dumps(spec, ensure_ascii=False), encoding='utf-8')
        code, found = self.findings()
        self.assertEqual(code, 2)
        for index, (message, kind) in enumerate(found, 1):
            self.assertIsNone(kind, '경로 주입이 판정을 얻으면 안 된다: %s' % message)
            self.assertEqual(self.add(index=index).returncode, 2, message)

    def test_handwritten_row_is_not_a_right_of_way(self):
        """`ledger.py` 만 쓴다는 규범에는 기제가 없다 — 조회가 다시 본다."""
        self.make_residual()
        code, found = self.findings()
        message, kind = found[self.residual_index(found) - 1]
        for row in ({'key': ledger.key_of(message, kind)},
                    {'key': ledger.key_of(message, kind), 'label': message, 'kind': kind,
                     'quote': '승인한다', 'scope_ref': 'scope.md#관계-메뉴'}):
            with self.subTest(fields=sorted(row)):
                (self.build / 'evidence-ledger.json').write_text(
                    json.dumps({'version': 1, 'entries': [row]}, ensure_ascii=False), encoding='utf-8')
                result = self.run_gate('prepare')
                self.assertEqual(result.returncode, 2, '손으로 쓴 행은 통행권이 아니다')
                self.assertIn('승인 근거 필드가 빠졌다', result.stderr)

    def test_shortcircuit_finding_has_no_verdict_kind(self):
        """마스터키 공격은 «종류가 없다» 로 구조적으로 닫힌다 — 손으로 써도 열리지 않는다."""
        spec = json.loads((self.build / 'design-input.json').read_text(encoding='utf-8'))
        spec['cases'] = []
        (self.build / 'design-input.json').write_text(json.dumps(spec, ensure_ascii=False), encoding='utf-8')
        code, found = self.findings()
        message, kind = found[0]
        self.assertIsNone(kind)
        for guess in ledger.KINDS:
            (self.build / 'evidence-ledger.json').write_text(json.dumps(
                {'version': 1, 'entries': [{'key': ledger.key_of(message, guess), 'label': message,
                                            'kind': guess, 'quote': 'x' * 10,
                                            'scope_ref': 'scope.md#관계-메뉴', 'anchor_sha256': 'x',
                                            'observation_sha256': 'x'}]}, ensure_ascii=False), encoding='utf-8')
            self.assertEqual(self.run_gate('prepare').returncode, 2, guess)

    def test_surface_name_is_kept_in_the_key(self):
        surface = "cases[1].interactions: 새 표면 {!r}에 도달한 case reached_by도 승인 예외도 없다"
        key = lambda m: ledger.key_of(m, 'surface')
        self.assertNotEqual(key(surface.format('메뉴')), key(surface.format('시트')))

    def test_magnitude_ceiling_blocks_a_bigger_residual(self):
        """승인은 «그때 본 규모까지» 다 — 커지면 재승인이다."""
        self.make_residual()
        code, found = self.findings()
        index = self.residual_index(found)
        message = found[index - 1][0]
        self.add(index=index)
        smaller = message.replace('잔여 1건', '잔여 1건')
        verdicts = {smaller: 'residual'}
        remaining, opened, _dead = ledger.filter_issues(self.build, [smaller], verdicts)
        self.assertEqual(opened, [smaller])
        bigger = message.replace('잔여 1건', '잔여 9건')
        remaining, opened, _dead = ledger.filter_issues(self.build, [bigger], {bigger: 'residual'})
        self.assertEqual(opened, [])
        self.assertIn('승인 규모 1 초과', remaining[0])


if __name__ == '__main__':
    unittest.main(verbosity=1)
