#!/usr/bin/env python3
"""Adversarial fixtures for the component-identity gate (1.1.20).

시안이 component-from-global-scope 로 선언한 커스텀 컴포넌트를 구현이 native 등가로
평탄화하면 잡는다. 이탈 표(산문)를 읽지 않으므로 override 불가.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from check_design_evidence import validate_component_identity  # noqa: E402


SELECT_DECL = (
    '<div component-from-global-scope="ChunmongDesignSystem_9ad494.Select" '
    'label="관계" placeholder="관계를 선택해주세요"></div>'
)
INPUT_ONLY_DECL = (
    '<div component-from-global-scope="ChunmongDesignSystem_9ad494.Input" label="이름"></div>'
)
NATIVE = '<div class="select-field"><select class="select-field__select" name="rel"></select></div>'
CUSTOM = (
    '<div class="cm-select" data-cm-select>\n'
    '  <button type="button" class="cm-select__trigger" aria-haspopup="listbox">관계를 선택해주세요</button>\n'
    '  <ul class="cm-select__menu" role="listbox"><li role="option">부모</li></ul>\n'
    '</div>'
)


class ComponentIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.build = root / 'build'
        self.project = root / 'project'
        self.dref = self.build / 'design-ref'
        self.web = self.project / 'web'
        self.dref.mkdir(parents=True)
        self.web.mkdir(parents=True)

    def screen(self, body):
        (self.dref / 'screen.dc.html').write_text(body, encoding='utf-8')

    def impl(self, body, name='step.html'):
        (self.web / name).write_text(body, encoding='utf-8')

    def run_check(self):
        return validate_component_identity(self.build, self.project)

    def test_declared_select_flattened_to_native_fails(self):
        self.screen(SELECT_DECL)
        self.impl(NATIVE)
        issues = self.run_check()
        self.assertTrue(issues, 'native <select> 평탄화는 결함이어야 한다')
        self.assertIn('component-identity', issues[0])

    def test_faithful_custom_dropdown_passes(self):
        self.screen(SELECT_DECL)
        self.impl(CUSTOM)
        self.assertEqual(self.run_check(), [])

    def test_faithful_dropdown_with_rationale_comment_passes(self):
        # 이 코드베이스의 지배적 스타일은 근거 주석 — 올바른 수리에도 주석에 <select> 가 남을 수 있다.
        self.screen(SELECT_DECL)
        self.impl(
            '{% comment %} 이전에는 native <select> 를 썼으나 커스텀 드롭다운으로 교체했다. {% endcomment %}\n'
            '{# 참고: <select> 금지 #}\n'
            '<!-- 과거 <select> 흔적 -->\n' + CUSTOM
        )
        self.assertEqual(self.run_check(), [], '주석 안 리터럴 <select> 는 오탐 금지')

    def test_no_custom_select_declared_native_not_flagged(self):
        self.screen(INPUT_ONLY_DECL)
        self.impl(NATIVE)
        self.assertEqual(self.run_check(), [], '커스텀 Select 미선언이면 발화 안 함')

    def test_ds_definitions_do_not_over_declare(self):
        # _ds 내부 컴포넌트 정의(engine)에 component-from-global-scope 가 있어도
        # 화면 dc.html 이 Select 를 선언 안 했으면 발화하지 않는다(화면 파일 직속만 파싱).
        self.screen(INPUT_ONLY_DECL)
        ds = self.dref / '_ds'
        ds.mkdir()
        (ds / '_ds_bundle.js').write_text(
            'component-from-global-scope="ChunmongDesignSystem_9ad494.Select"', encoding='utf-8')
        self.impl(NATIVE)
        self.assertEqual(self.run_check(), [], '_ds 정의는 화면 선언으로 세지 않는다')

    def test_no_dc_html_is_noop(self):
        # design-ref 에 .dc.html 이 없으면(이미지 단독·비시안) no-op.
        self.impl(NATIVE)
        self.assertEqual(self.run_check(), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
