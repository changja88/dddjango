"""evidence_debt_hook 행동 테스트 — 프로젝트 탐색·이벤트별 출력·JSON 형태·항상 exit 0."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOOK = HERE.parent / 'evidence_debt_hook.py'
sys.path.insert(0, str(HERE))
from test_evidence_debt import make_build, observation  # noqa: E402

ANCHOR = '[dddjango-web] evidence debt — '


def run_hook(event: str, *, cwd: Path, stdin_cwd: Path | None = None, project_dir: Path | None = None,
             argv: list[str] | None = None) -> tuple[int, str, str]:
    env = {k: v for k, v in os.environ.items() if k != 'CLAUDE_PROJECT_DIR'}
    if project_dir is not None:
        env['CLAUDE_PROJECT_DIR'] = str(project_dir)
    payload = json.dumps({'cwd': str(stdin_cwd)} if stdin_cwd is not None else {})
    args = [sys.executable, str(HOOK)] + (argv if argv is not None else [event])
    done = subprocess.run(args, cwd=str(cwd), env=env, input=payload, capture_output=True, text=True, timeout=30)
    return done.returncode, done.stdout, done.stderr


def parse(stdout: str) -> dict:
    return json.loads(stdout)


class HookOutput(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.project = self.root / 'proj'
        self.project.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_no_dddjango_web_anywhere_is_silent(self) -> None:
        for event in ('session-start', 'user-prompt'):
            code, out, err = run_hook(event, cwd=self.project)
            self.assertEqual((code, out, err), (0, '', ''))

    def test_session_start_always_reports_active_line(self) -> None:
        make_build(self.project, 'clean', observations=[observation(2)])
        code, out, _ = run_hook('session-start', cwd=self.project)
        self.assertEqual(code, 0)
        doc = parse(out)
        self.assertEqual(doc['hookSpecificOutput']['hookEventName'], 'SessionStart')
        context = doc['hookSpecificOutput']['additionalContext']
        self.assertIn('[dddjango-web] evidence hook active — scanned 1 build(s): undecided 0 · deferred 0 · observing 0', context)
        self.assertNotIn(ANCHOR, context)
        self.assertIn('evidence hook active', doc['systemMessage'])

    def test_user_prompt_silent_when_clear(self) -> None:
        make_build(self.project, 'clean', observations=[observation(2)])
        code, out, _ = run_hook('user-prompt', cwd=self.project)
        self.assertEqual((code, out), (0, ''))

    def test_user_prompt_reports_undecided(self) -> None:
        make_build(self.project, '20260912-1640-web-related-persons', observations=[observation(1), observation(1), observation(2)])
        code, out, _ = run_hook('user-prompt', cwd=self.project)
        self.assertEqual(code, 0)
        doc = parse(out)
        self.assertEqual(doc['hookSpecificOutput']['hookEventName'], 'UserPromptSubmit')
        context = doc['hookSpecificOutput']['additionalContext']
        self.assertIn(ANCHOR + '20260912-1640-web-related-persons: 2/3 archive case without interaction evidence (observation v1/absent) · decision required before any run on this folder', context)
        self.assertIn('[dddjango-web] evidence debt: 1 undecided build(s). Record the user\'s decision in build-state.json evidence_debt', context)
        self.assertIn('ⓐ observe', context)
        self.assertIn('ⓑ defer', context)
        self.assertEqual(doc['systemMessage'], '[dddjango-web] evidence debt: undecided 1 · deferred 0 · observing 0')

    def test_decided_builds_only_on_session_start(self) -> None:
        defer = {'decision': 'defer', 'at': '2026-09-15T10:00:00+09:00', 'quote': '지금은 재동결만 확인하고 넘어가자', 'reason': 'r', 'cases': 1}
        observe = {'decision': 'observe', 'at': '2026-09-15T11:00:00+09:00', 'quote': '드라이버 돌려서 전부 수집해줘', 'reason': 'r', 'cases': 1}
        make_build(self.project, 'a-defer', observations=[observation(1)], decision=defer)
        make_build(self.project, 'b-observe', observations=[observation(1)], decision=observe)
        code, out, _ = run_hook('user-prompt', cwd=self.project)
        self.assertEqual((code, out), (0, ''))
        code, out, _ = run_hook('session-start', cwd=self.project)
        context = parse(out)['hookSpecificOutput']['additionalContext']
        self.assertIn('scanned 2 build(s): undecided 0 · deferred 1 · observing 1', context)
        self.assertIn(ANCHOR + 'a-defer: deferred since 2026-09-15T10:00:00+09:00 — "지금은 재동결만 확인하고 넘어가자"', context)
        self.assertIn(ANCHOR + 'b-observe: observation pending since 2026-09-15T11:00:00+09:00', context)

    def test_quote_truncated_to_20_chars(self) -> None:
        defer = {'decision': 'defer', 'at': 't', 'quote': 'x' * 30, 'reason': 'r', 'cases': 1}
        make_build(self.project, 'a', observations=[observation(1)], decision=defer)
        _, out, _ = run_hook('session-start', cwd=self.project)
        self.assertIn('— "' + 'x' * 20 + '…"', parse(out)['hookSpecificOutput']['additionalContext'])

    def test_non_archive_and_in_progress_builds_not_counted(self) -> None:
        make_build(self.project, 'static', archive=False, observations=[observation(1)])
        make_build(self.project, 'pending', design_status='pending', observations=[observation(1)])
        _, out, _ = run_hook('session-start', cwd=self.project)
        self.assertIn('scanned 2 build(s): undecided 0 · deferred 0 · observing 0', parse(out)['hookSpecificOutput']['additionalContext'])
        _, out, _ = run_hook('user-prompt', cwd=self.project)
        self.assertEqual(out, '')

    def test_error_build_reported_and_exit_zero(self) -> None:
        build = make_build(self.project, 'bad')
        (build / 'design-input.json').write_text('{broken', encoding='utf-8')
        code, out, _ = run_hook('user-prompt', cwd=self.project)
        self.assertEqual(code, 0)
        self.assertIn(ANCHOR + 'bad: cannot evaluate (', parse(out)['hookSpecificOutput']['additionalContext'])

    def test_unknown_event_treated_as_user_prompt_and_exit_zero(self) -> None:
        make_build(self.project, 'a', observations=[observation(1)])
        code, out, _ = run_hook('user-prompt', cwd=self.project, argv=['something-else'])
        self.assertEqual(code, 0)
        self.assertEqual(parse(out)['hookSpecificOutput']['hookEventName'], 'UserPromptSubmit')
        code, out, _ = run_hook('user-prompt', cwd=self.project, argv=[])
        self.assertEqual(code, 0)

    def test_stdout_is_single_json_document(self) -> None:
        make_build(self.project, 'a', observations=[observation(1)])
        _, out, _ = run_hook('user-prompt', cwd=self.project)
        parse(out)  # 유일한 문서 — 파싱 실패면 여기서 예외
        self.assertEqual(out.count('\n'), out.rstrip('\n').count('\n') + 1)


class ProjectDiscovery(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_upward_from_subdirectory(self) -> None:
        project = self.root / 'proj'
        make_build(project, 'a', observations=[observation(1)])
        deep = project / 'web' / 'static'
        deep.mkdir(parents=True)
        _, out, _ = run_hook('user-prompt', cwd=deep)
        self.assertIn(ANCHOR + 'a:', parse(out)['hookSpecificOutput']['additionalContext'])

    def test_downward_depth_two_from_repo_root(self) -> None:
        backend = self.root / 'mono' / 'services' / 'backend'
        make_build(backend, 'a', observations=[observation(1)])
        (self.root / 'mono' / 'node_modules' / 'pkg').mkdir(parents=True)
        make_build(self.root / 'mono' / 'node_modules' / 'pkg', 'ignored', observations=[observation(1)])
        _, out, _ = run_hook('user-prompt', cwd=self.root / 'mono')
        context = parse(out)['hookSpecificOutput']['additionalContext']
        self.assertIn(ANCHOR + 'a:', context)
        self.assertNotIn('ignored', context)

    def test_depth_three_not_found(self) -> None:
        deep = self.root / 'mono' / 'a' / 'b' / 'c'
        make_build(deep, 'a', observations=[observation(1)])
        code, out, _ = run_hook('user-prompt', cwd=self.root / 'mono')
        self.assertEqual((code, out), (0, ''))

    def test_claude_project_dir_and_stdin_cwd_union(self) -> None:
        one = self.root / 'one'
        two = self.root / 'two'
        make_build(one, 'from-env', observations=[observation(1)])
        make_build(two, 'from-stdin', observations=[observation(1)])
        elsewhere = self.root / 'elsewhere'
        elsewhere.mkdir()
        _, out, _ = run_hook('user-prompt', cwd=elsewhere, stdin_cwd=two, project_dir=one)
        context = parse(out)['hookSpecificOutput']['additionalContext']
        self.assertIn(ANCHOR + 'from-env:', context)
        self.assertIn(ANCHOR + 'from-stdin:', context)
        self.assertIn('2 undecided build(s)', context)

    def test_same_project_via_two_candidates_counted_once(self) -> None:
        project = self.root / 'proj'
        make_build(project, 'a', observations=[observation(1)])
        _, out, _ = run_hook('session-start', cwd=project, stdin_cwd=project, project_dir=project)
        self.assertIn('scanned 1 build(s)', parse(out)['hookSpecificOutput']['additionalContext'])

    def test_invalid_stdin_is_tolerated(self) -> None:
        project = self.root / 'proj'
        make_build(project, 'a', observations=[observation(1)])
        done = subprocess.run([sys.executable, str(HOOK), 'user-prompt'], cwd=str(project), input='not json',
                              capture_output=True, text=True, timeout=30)
        self.assertEqual(done.returncode, 0)
        self.assertIn(ANCHOR + 'a:', parse(done.stdout)['hookSpecificOutput']['additionalContext'])


if __name__ == '__main__':
    unittest.main()
