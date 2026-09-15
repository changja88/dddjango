"""refreeze.py — 전량 폐기 후 재동결의 결정적 집행 단위 시험.

설계: workspace/design/2026-09-15-web-refreeze-full-rebuild.md v5
파괴적 구간(폐기 집합 계산·교체·롤백)을 산문이 아니라 도구가 집행하는지 본다.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import refreeze  # noqa: E402


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write(path: Path, data: bytes | str) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = data if isinstance(data, bytes) else data.encode('utf-8')
    path.write_bytes(raw)
    return raw


def pointer(build: Path, rel: str) -> dict:
    return {'path': rel, 'sha256': sha((build / rel).read_bytes())}


def observation_v2(build: Path) -> dict:
    """evidence_debt.has_interaction_evidence의 정확 필드 집합을 갖춘 v2 관찰."""
    return {
        'version': 2,
        'archive_sha256': sha((build / 'source-manifest.json').read_bytes()),
        'entrypoint': pointer(build, 'design-ref/screen.dc.html'),
        'case_id': 'screen/list',
        'screen': 'screen',
        'state': '목록',
        'viewport': [390, 844],
        'url': 'file:///design-ref/screen.dc.html',
        'observed_at': '2026-09-15T00:00:00+09:00',
        'capture': pointer(build, 'captures/screen-original.png'),
        'trace': pointer(build, 'captures/screen-trace.json'),
        'interactions': pointer(build, 'captures/screen-interactions.json'),
    }


class Fixture:
    """v2 관찰 1 case + 구현 증거 + 고아를 가진 최소 빌드."""

    def __init__(self, root: Path):
        self.root = root
        self.build = root / '.dddjango-web' / '20260101-0000-screen'
        self.build.mkdir(parents=True)
        write(self.root / 'web' / 'static' / 'images' / 'logo_abc123.png', b'img')

        write(self.build / 'design-ref' / 'screen.dc.html', b'<html>original</html>')
        write(self.build / 'source-manifest.json', json.dumps({'collection': 'archive', 'files': []}))
        for name in ('design-tokens.json', 'asset-manifest.json', 'screen-meta.json',
                     'render-audit.json'):
            write(self.build / name, json.dumps({'name': name}))
        write(self.build / 'scope.md', '# scope\n\n승인 원문: 이 화면을 이렇게 만든다.\n')
        write(self.build / 'coverage-review.md', '# review\n')
        write(self.build / 'design-spec.md', '# spec\n')
        write(self.build / 'visual-check.md', '# visual\n')
        write(self.build / 'motion-notes.md', '# motion\n')
        write(self.build / 'screen-declared.json', json.dumps([{'selector': '.x', 'reason': 'deco'}]))

        caps = self.build / 'captures'
        write(caps / 'screen-original.png', b'orig')
        write(caps / 'screen-initial.png', b'init')
        write(caps / 'screen-step-1.png', b'step1')
        write(caps / 'screen-trace.json', json.dumps({'trace': True}))
        write(caps / 'screen-impl.png', b'impl')
        write(caps / 'smoke-login.png', b'smoke')          # 고아
        write(caps / 'external' / 'lucide.css', b'.i{}')   # 고아 · 재수집 불가 입력

        interactions = {
            'version': 2,
            'initial': {'capture': pointer(self.build, 'captures/screen-initial.png')},
            'steps': [{'after': {'capture': pointer(self.build, 'captures/screen-step-1.png')}}],
        }
        write(caps / 'screen-interactions.json', json.dumps(interactions))
        write(caps / 'screen-source-observation.json', json.dumps(observation_v2(self.build)))

        spec = {
            'version': 1,
            'reference_root': 'design-ref',
            'manifests': ['source-manifest.json'],
            'scope': pointer(self.build, 'scope.md'),
            'coverage_review': pointer(self.build, 'coverage-review.md'),
            'cases': [{
                'id': 'screen/list',
                'reference_capture': pointer(self.build, 'captures/screen-original.png'),
                'source_observation': pointer(self.build, 'captures/screen-source-observation.json'),
            }],
        }
        write(self.build / 'design-input.json', json.dumps(spec))
        write(self.build / 'visual-evidence.json', json.dumps({
            'version': 1,
            'cases': [{'id': 'screen/list', 'capture': pointer(self.build, 'captures/screen-impl.png')}],
        }))
        write(self.build / 'build-state.json', json.dumps({
            'design_status': 'ready', 'has_design_screen': True, 'has_render_audit': True,
            'g2_approved': True, 'implementation_visual': 'verified',
            'evidence_debt': {'decision': 'defer', 'quote': '지금은 재동결만', 'at': '2026-09-15T00:00:00+09:00',
                              'reason': 'r', 'cases': 1},
        }))

    def staging(self) -> Path:
        found = sorted(self.build.glob('_refreeze-*'))
        return found[0] if found else None

    def fill_staging(self) -> Path:
        """재수집이 끝난 상태를 흉내낸다 — staging에 전 축을 새 바이트로 만든다."""
        staging = self.staging()
        write(staging / 'design-ref' / 'screen.dc.html', b'<html>NEW</html>')
        write(staging / 'source-manifest.json', json.dumps({'collection': 'archive', 'files': [], 'new': 1}))
        for name in ('design-tokens.json', 'asset-manifest.json', 'screen-meta.json',
                     'render-audit.json'):
            write(staging / name, json.dumps({'name': name, 'new': 1}))
        write(staging / 'coverage-review.md', '# review NEW\n')
        caps = staging / 'captures'
        write(caps / 'screen-original.png', b'ORIG2')
        write(caps / 'screen-initial.png', b'INIT2')
        write(caps / 'screen-step-1.png', b'STEP2')
        write(caps / 'screen-trace.json', json.dumps({'trace': 2}))
        interactions = {
            'version': 2,
            'initial': {'capture': pointer(staging, 'captures/screen-initial.png')},
            'steps': [{'after': {'capture': pointer(staging, 'captures/screen-step-1.png')}}],
        }
        write(caps / 'screen-interactions.json', json.dumps(interactions))
        write(staging / 'design-ref' / 'screen.dc.html', b'<html>NEW</html>')
        write(caps / 'screen-source-observation.json', json.dumps(observation_v2(staging)))
        spec = json.loads((staging / 'design-input.json').read_text()) if (staging / 'design-input.json').is_file() else None
        spec = spec or json.loads((self.build / 'design-input.json').read_text())
        spec['scope'] = pointer(staging, 'scope.md')
        spec['coverage_review'] = pointer(staging, 'coverage-review.md')
        spec['cases'][0]['reference_capture'] = pointer(staging, 'captures/screen-original.png')
        spec['cases'][0]['source_observation'] = pointer(staging, 'captures/screen-source-observation.json')
        write(staging / 'design-input.json', json.dumps(spec))
        return staging


class RefreezeTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.fx = Fixture(self.tmp)
        self.build = self.fx.build
        self.root = self.tmp
        # verified 단계의 외부 게이트는 합성 빌드가 통과할 수 없다 — 포인터 건강으로 대역한다.
        # 기본 구현이 실제로 check_design_evidence.py를 부르는지는 VerifyInputsTests가 본다.
        original = refreeze.verify_inputs
        refreeze.verify_inputs = lambda build, root: (
            (lambda issues: (not issues, '\n'.join(issues)))(refreeze.pointer_health(Path(build))))
        self.addCleanup(setattr, refreeze, 'verify_inputs', original)

    def run_cli(self, *args: str) -> int:
        return refreeze.main([*args])

    def begin(self) -> int:
        return self.run_cli('begin', '--build', str(self.build),
                            '--project-root', str(self.root), '--quote', '기존 동결분 무시하고 다시 동결해')

    def state(self) -> dict:
        return json.loads((self.build / 'build-state.json').read_text())

    def journal(self) -> dict:
        return json.loads((self.fx.staging() / 'journal.json').read_text())


class DiscardSetTests(RefreezeTestCase):
    def test_three_level_pointer_walk(self):
        """3겹 — case → 관찰 문서 → interactions 문서 안의 상태 캡처까지."""
        discard = set(refreeze.discard_set(self.build))
        for rel in ('captures/screen-original.png', 'captures/screen-source-observation.json',
                    'captures/screen-trace.json', 'captures/screen-interactions.json',
                    'captures/screen-initial.png', 'captures/screen-step-1.png'):
            self.assertIn(rel, discard, rel)

    def test_fixed_targets_are_files_not_directories(self):
        discard = set(refreeze.discard_set(self.build))
        self.assertIn('design-ref/screen.dc.html', discard)
        self.assertNotIn('design-ref', discard)
        for rel in ('source-manifest.json', 'design-tokens.json', 'asset-manifest.json',
                    'screen-meta.json', 'render-audit.json', 'design-input.json',
                    'coverage-review.md', 'scope.md', 'screen-declared.json'):
            self.assertIn(rel, discard, rel)

    def test_preserved_never_in_discard(self):
        discard = set(refreeze.discard_set(self.build))
        for rel in ('captures/screen-impl.png', 'visual-evidence.json', 'motion-notes.md',
                    'design-spec.md', 'visual-check.md', 'build-state.json'):
            self.assertNotIn(rel, discard, rel)

    def test_orphans_reported_not_discarded(self):
        discard = set(refreeze.discard_set(self.build))
        orphans = set(refreeze.orphan_set(self.build))
        self.assertIn('captures/smoke-login.png', orphans)
        self.assertIn('captures/external/lucide.css', orphans)
        self.assertFalse(orphans & discard)


class BeginTests(RefreezeTestCase):
    def test_creates_staging_journal_and_copies_inputs(self):
        self.assertEqual(self.begin(), 0)
        staging = self.fx.staging()
        self.assertIsNotNone(staging)
        journal = self.journal()
        self.assertEqual(journal['quote'], '기존 동결분 무시하고 다시 동결해')
        self.assertTrue(journal['has_render_audit'])
        self.assertIsNone(journal['completed_at'])
        self.assertEqual(journal['scope_sha256_at_begin'],
                         sha((self.build / 'scope.md').read_bytes()))
        self.assertIn('web/static/images/logo_abc123.png', journal['images_before'])
        self.assertIn('captures/external/lucide.css', journal['orphans'])
        self.assertIn('scope.md', journal['copied_inputs'])
        self.assertIn('screen-declared.json', journal['copied_inputs'])
        self.assertTrue((staging / 'scope.md').is_file())
        self.assertTrue((staging / 'screen-declared.json').is_file())

    def test_records_evidence_debt_observe_and_keeps_previous(self):
        self.assertEqual(self.begin(), 0)
        debt = self.state()['evidence_debt']
        self.assertEqual(debt['decision'], 'observe')
        self.assertEqual(debt['quote'], '기존 동결분 무시하고 다시 동결해')
        self.assertEqual(self.journal()['evidence_debt_before']['decision'], 'defer')

    def test_live_untouched(self):
        before = sha((self.build / 'design-input.json').read_bytes())
        self.assertEqual(self.begin(), 0)
        self.assertEqual(sha((self.build / 'design-input.json').read_bytes()), before)

    def test_refuses_when_staging_exists(self):
        self.assertEqual(self.begin(), 0)
        self.assertEqual(self.begin(), 2)


class CheckTests(RefreezeTestCase):
    def test_incomplete_staging_exits_3(self):
        self.begin()
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 3)

    def test_complete_staging_exits_0(self):
        self.begin()
        self.fx.fill_staging()
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 0)

    def test_render_audit_skipped_lowers_journal_and_passes(self):
        self.begin()
        self.fx.fill_staging()
        (self.fx.staging() / 'render-audit.json').unlink()
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 3)
        self.assertEqual(self.run_cli('check', '--build', str(self.build),
                                      '--render-audit-skipped', '원본 열람 불가'), 0)
        self.assertFalse(self.journal()['has_render_audit'])
        self.assertEqual(self.journal()['render_audit_skip_reason'], '원본 열람 불가')

    def test_self_check_discard_covers_pointers(self):
        """폐기 집합이 3겹 포인터를 덮지 못하면 check가 막는다."""
        self.begin()
        self.fx.fill_staging()
        journal = self.journal()
        journal['discard_set'] = [p for p in journal['discard_set']
                                  if p != 'captures/screen-step-1.png']
        (self.fx.staging() / 'journal.json').write_text(json.dumps(journal), encoding='utf-8')
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 3)


class CommitTests(RefreezeTestCase):
    def prepare(self):
        self.begin()
        self.fx.fill_staging()
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 0)

    def test_scope_drift_stops_before_touching_live(self):
        self.prepare()
        (self.build / 'scope.md').write_text('# scope\n\n딴 세션이 쓴 줄\n', encoding='utf-8')
        self.assertEqual(self.run_cli('commit', '--build', str(self.build)), 1)
        self.assertTrue((self.build / 'design-ref' / 'screen.dc.html').is_file())
        self.assertEqual((self.build / 'design-ref' / 'screen.dc.html').read_bytes(),
                         b'<html>original</html>')

    def test_full_swap(self):
        self.prepare()
        self.assertEqual(self.run_cli('commit', '--build', str(self.build)), 0)
        self.assertEqual((self.build / 'design-ref' / 'screen.dc.html').read_bytes(), b'<html>NEW</html>')
        self.assertEqual((self.build / 'captures' / 'screen-original.png').read_bytes(), b'ORIG2')
        self.assertEqual((self.build / 'captures' / 'screen-impl.png').read_bytes(), b'impl')
        self.assertEqual((self.build / 'captures' / 'external' / 'lucide.css').read_bytes(), b'.i{}')
        self.assertEqual((self.build / 'captures' / 'smoke-login.png').read_bytes(), b'smoke')
        self.assertFalse(sorted(self.build.glob('_refreeze-*')))
        self.assertFalse(sorted(self.build.glob('_prev-*')))

    def test_done_updates_build_state(self):
        self.prepare()
        self.run_cli('commit', '--build', str(self.build))
        state = self.state()
        self.assertEqual(state['implementation_visual'], 'pending')
        self.assertEqual(state['design_status'], 'ready')
        self.assertTrue(state['g2_approved'])
        self.assertNotIn('evidence_debt', state)

    def test_stop_after_discarded_then_resume(self):
        self.prepare()
        self.assertEqual(self.run_cli('commit', '--build', str(self.build),
                                      '--stop-after', 'discarded'), 3)
        prev = sorted(self.build.glob('_prev-*'))
        self.assertTrue(prev)
        plan = json.loads((prev[0] / 'swap-plan.json').read_text())
        self.assertEqual(plan['phase'], 'discarded')
        self.assertEqual(self.run_cli('commit', '--build', str(self.build), '--resume'), 0)
        self.assertEqual((self.build / 'design-ref' / 'screen.dc.html').read_bytes(), b'<html>NEW</html>')

    def test_installed_overwrites_name_collision(self):
        """폐기 집합 밖의 live 파일과 staging 산출물 이름이 겹쳐도 새 산출물이 이긴다."""
        self.prepare()
        write(self.fx.staging() / 'captures' / 'smoke-login.png', b'SMOKE2')
        self.assertEqual(self.run_cli('commit', '--build', str(self.build)), 0)
        self.assertEqual((self.build / 'captures' / 'smoke-login.png').read_bytes(), b'SMOKE2')

    def test_requires_resume_flag_when_plan_exists(self):
        self.prepare()
        self.run_cli('commit', '--build', str(self.build), '--stop-after', 'discarded')
        self.assertEqual(self.run_cli('commit', '--build', str(self.build)), 1)


class RegressionTests(RefreezeTestCase):
    """구현 리뷰(2026-09-15)가 실증한 BLOCKER·MAJOR의 재현 시험."""

    def staged(self):
        self.begin()
        self.fx.fill_staging()
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 0)

    def test_rewind_after_mid_stage_interruption_restores_originals(self):
        """BLOCKER-1 — phase가 아직 planned인 채 discarded 도중 죽어도 원본이 살아난다."""
        self.staged()
        before = sha((self.build / 'asset-manifest.json').read_bytes())
        prev = self.build / '_prev-mid'
        prev.mkdir()
        (prev / 'journal.json').write_bytes((self.fx.staging() / 'journal.json').read_bytes())
        refreeze.dump_json(prev / 'swap-plan.json', {
            'version': 1, 'phase': 'planned', 'created_at': 'x',
            'staging': self.fx.staging().name, 'prev': prev.name,
            'discard': json.loads((self.fx.staging() / 'journal.json').read_text())['discard_set'],
            'install': [],
        })
        # 단계 «도중» — 두 파일만 옮겨진 상태를 손으로 만든다.
        for rel in ('asset-manifest.json', 'captures/screen-original.png'):
            (prev / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.build / rel).rename(prev / rel)
        self.assertEqual(self.run_cli('abort', '--build', str(self.build)), 0)
        self.assertTrue((self.build / 'asset-manifest.json').is_file())
        self.assertEqual(sha((self.build / 'asset-manifest.json').read_bytes()), before)
        self.assertTrue((self.build / 'captures' / 'screen-original.png').is_file())

    def test_resume_after_stop_at_installed_does_not_redo_discard(self):
        """BLOCKER-2 — installed 뒤 재개가 phase를 되감아 원본을 덮지 않는다."""
        self.staged()
        self.assertEqual(self.run_cli('commit', '--build', str(self.build),
                                      '--stop-after', 'installed'), 3)
        self.assertEqual(self.run_cli('commit', '--build', str(self.build), '--resume'), 0)
        self.assertEqual((self.build / 'design-ref' / 'screen.dc.html').read_bytes(), b'<html>NEW</html>')
        self.assertEqual((self.build / 'captures' / 'screen-impl.png').read_bytes(), b'impl')

    def test_resume_after_stop_at_verified(self):
        self.staged()
        self.assertEqual(self.run_cli('commit', '--build', str(self.build),
                                      '--stop-after', 'verified'), 3)
        self.assertEqual(self.run_cli('commit', '--build', str(self.build), '--resume'), 0)
        self.assertFalse(sorted(self.build.glob('_prev-*')))

    def test_install_collision_backs_up_preserved_file(self):
        """MAJOR-2 — 폐기 집합 밖 동명 파일이 덮이면 _prev에 피신했다가 되감기로 살아난다."""
        self.begin()
        self.fx.fill_staging()
        write(self.fx.staging() / 'captures' / 'screen-impl.png', b'IMPL2')
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 0)
        spec = json.loads((self.fx.staging() / 'design-input.json').read_text())
        spec['cases'][0]['reference_capture']['sha256'] = '0' * 64
        (self.fx.staging() / 'design-input.json').write_text(json.dumps(spec), encoding='utf-8')
        self.assertEqual(self.run_cli('commit', '--build', str(self.build)), 3)
        self.assertEqual((self.build / 'captures' / 'screen-impl.png').read_bytes(), b'impl')

    def test_journal_less_staging_can_be_cleared(self):
        """MAJOR-3 — begin이 깨져 journal 없는 staging이 남아도 abort가 치운다."""
        (self.build / '_refreeze-broken').mkdir()
        self.assertEqual(self.run_cli('abort', '--build', str(self.build)), 0)
        self.assertFalse(sorted(self.build.glob('_refreeze-*')))

    def test_bom_in_design_input_is_not_silently_swallowed(self):
        """MAJOR-6 — BOM이 붙어도 폐기 집합이 줄지 않는다."""
        path = self.build / 'design-input.json'
        path.write_bytes(b'\xef\xbb\xbf' + path.read_bytes())
        self.assertIn('captures/screen-step-1.png', refreeze.discard_set(self.build))

    def test_commit_requires_check(self):
        """MINOR-10 — check 없이 곧장 commit 하면 전량 폐기 전에 막는다."""
        self.begin()
        self.fx.fill_staging()
        self.assertEqual(self.run_cli('commit', '--build', str(self.build)), 1)
        self.assertEqual((self.build / 'design-ref' / 'screen.dc.html').read_bytes(),
                         b'<html>original</html>')

    def test_render_audit_skip_reason_must_be_enum(self):
        self.begin()
        self.fx.fill_staging()
        self.assertEqual(self.run_cli('check', '--build', str(self.build),
                                      '--render-audit-skipped', '귀찮아서'), 1)

    def test_install_backup_never_overwrites_an_existing_prev_original(self):
        """N-1 — 피신이 이미 _prev 에 있는 폐기 원본을 덮지 않는다."""
        self.staged()
        self.assertEqual(self.run_cli('commit', '--build', str(self.build),
                                      '--stop-after', 'discarded'), 3)
        # 폐기가 끝난 자리에 침입 바이트가 생긴 상태를 만든다.
        write(self.build / 'asset-manifest.json', b'INTRUDER')
        self.assertEqual(self.run_cli('commit', '--build', str(self.build), '--resume'), 0)
        prev = sorted(self.build.glob('_prev-*'))
        self.assertFalse(prev)
        self.assertNotEqual((self.build / 'asset-manifest.json').read_bytes(), b'INTRUDER')

    def test_abort_after_staging_removed_leaves_nothing(self):
        """N-2 — 되감기가 지워진 staging 을 되살려 두 번 abort 하게 만들지 않는다."""
        self.staged()
        self.assertEqual(self.run_cli('commit', '--build', str(self.build),
                                      '--stop-after', 'discarded'), 3)
        shutil.rmtree(self.fx.staging())
        self.assertEqual(self.run_cli('abort', '--build', str(self.build)), 0)
        self.assertFalse(sorted(self.build.glob('_refreeze-*')))
        self.assertFalse(sorted(self.build.glob('_prev-*')))
        self.assertEqual((self.build / 'design-ref' / 'screen.dc.html').read_bytes(),
                         b'<html>original</html>')

    def test_inherited_render_audit_off_needs_an_explicit_reason(self):
        """M-1 — 사유 없이 상속된 false 를 그대로 통과시키지 않는다."""
        state = json.loads((self.build / 'build-state.json').read_text())
        state['has_render_audit'] = False
        write(self.build / 'build-state.json', json.dumps(state))
        self.begin()
        self.fx.fill_staging()
        (self.fx.staging() / 'render-audit.json').unlink()
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 3)
        self.assertEqual(self.run_cli('check', '--build', str(self.build),
                                      '--render-audit-skipped', '브라우저 채널 부재'), 0)

    def test_staging_outside_build_is_rejected(self):
        self.begin()
        self.assertEqual(self.run_cli('check', '--build', str(self.build),
                                      '--staging', str(self.tmp)), 1)


class HardwallTests(RefreezeTestCase):
    """§4 — 재동결이 «어떤 이유로든 불가능» 해지지 않는다. 대신 사실을 지우지도 않는다."""

    def break_evidence(self):
        """증거 포인터를 읽을 수 없게 만든다 — 재동결이 고쳐야 할 바로 그 상태다."""
        self.intact = (self.build / 'design-input.json').read_text(encoding='utf-8')
        (self.build / 'design-input.json').write_text('{ 깨진 json', encoding='utf-8')

    def recollect(self):
        """재동결의 본론 — 새로 동결한 증거로 staging 을 채운다(깨진 원본은 폐기 대상이다)."""
        (self.build / 'design-input.json').write_text(self.intact, encoding='utf-8')
        self.fx.fill_staging()

    def discarded(self):
        return sorted(p.name for p in self.build.glob('_discarded-*'))

    def test_begin_records_unreadable_and_proceeds(self):
        """판독 실패로 begin 이 죽으면 재동결이 고칠 대상이 재동결을 막는다."""
        self.break_evidence()
        self.assertEqual(self.begin(), 0)
        self.assertTrue(self.journal()['unreadable'], '사실이 journal 에 남아야 한다')

    def test_check_warns_on_unreadable_instead_of_blocking(self):
        """begin 만 고치면 벽이 check 로 한 칸 밀린다."""
        self.break_evidence()
        self.begin()
        self.recollect()
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 0,
                         '판독 실패를 이유로 check 가 막으면 벽이 한 칸 밀린 것뿐이다')

    def test_commit_preserves_one_generation_and_stays_resumable(self):
        """폐기분을 한 세대 남기되 `_prev` 의 «진행 중» 표식 의미는 건드리지 않는다."""
        self.begin()
        self.fx.fill_staging()
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 0)
        self.assertEqual(self.run_cli('commit', '--build', str(self.build)), 0)
        kept = self.discarded()
        self.assertEqual(len(kept), 1, kept)
        self.assertTrue((self.build / kept[0] / 'journal.json').is_file())
        self.assertFalse(list(self.build.glob('_prev-*')), '_prev 는 그대로 사라져야 한다')
        self.assertFalse(list(self.build.glob('_refreeze-*')))

    def test_discarded_leftover_does_not_block_the_next_refreeze(self):
        """백업이 다음 재동결을 «진행 중» 으로 오인시키면 새 하드월이다."""
        self.begin()
        self.fx.fill_staging()
        self.run_cli('check', '--build', str(self.build))
        self.run_cli('commit', '--build', str(self.build))
        self.assertTrue(self.discarded())
        self.assertEqual(self.begin(), 0, '_discarded-* 가 있어도 다시 시작할 수 있어야 한다')

    def test_abort_backs_up_journalless_leftover_before_deleting(self):
        """journal 없는 `_prev` 를 지우는 유일한 문이 abort 다 — 유일본이 들어 있을 수 있다."""
        orphan = self.build / '_prev-20260101-000000'
        orphan.mkdir()
        (orphan / 'only-copy.json').write_text('{"유일본": true}', encoding='utf-8')
        self.assertEqual(self.run_cli('abort', '--build', str(self.build)), 0)
        self.assertFalse(orphan.is_dir())
        kept = self.discarded()
        self.assertEqual(len(kept), 1, kept)
        self.assertTrue((self.build / kept[0] / 'only-copy.json').is_file(), '유일본이 살아 있어야 한다')

    def downgrade_observation(self):
        """드라이버를 못 돌린 상태 — 브라우저 채널이 없으면 이게 유일하게 가능한 결과다."""
        staging = self.fx.staging()
        rel = 'captures/screen-source-observation.json'
        doc = json.loads((staging / rel).read_text())
        doc['version'] = 1
        doc.pop('interactions', None)
        write(staging / rel, json.dumps(doc))
        spec = json.loads((staging / 'design-input.json').read_text())
        spec['cases'][0]['source_observation'] = pointer(staging, rel)
        write(staging / 'design-input.json', json.dumps(spec))

    def test_observation_skip_reason_opens_the_browserless_axis(self):
        """렌더 실측 축에만 탈출구가 있고 조작 상태 축에는 없으면 재동결이 «불가능» 해진다."""
        self.begin()
        self.fx.fill_staging()
        self.downgrade_observation()
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 3)
        self.assertEqual(self.run_cli('check', '--build', str(self.build),
                                      '--render-audit-skipped', '브라우저 채널 부재'), 3,
                         '렌더 실측 사유가 조작 상태 축을 열면 안 된다')
        self.assertEqual(self.run_cli('check', '--build', str(self.build),
                                      '--observation-skipped', '브라우저 채널 부재'), 0)
        self.assertEqual(self.journal()['observation_skip_reason'], '브라우저 채널 부재')

    def test_observation_skip_reason_is_an_enum(self):
        self.begin()
        self.fx.fill_staging()
        self.assertEqual(self.run_cli('check', '--build', str(self.build),
                                      '--observation-skipped', '그냥'), 1)

    def test_unverified_facts_survive_into_build_state(self):
        """벽을 없앤 자리에 표면이 없으면 열린 길이 무엇이 미검증인지 지운다(불변식 II)."""
        self.break_evidence()
        self.begin()
        self.recollect()
        self.downgrade_observation()
        self.assertEqual(self.run_cli('check', '--build', str(self.build),
                                      '--observation-skipped', '브라우저 채널 부재'), 0)
        self.assertEqual(self.run_cli('commit', '--build', str(self.build)), 0)
        facts = self.state()['refreeze_unverified']
        self.assertTrue(facts['unreadable'])
        self.assertEqual(facts['observation_skipped'], '브라우저 채널 부재')

    def test_preserve_never_collides(self):
        import refreeze as module
        source = self.build / '_prev-x'
        source.mkdir()
        (source / 'a.txt').write_text('a', encoding='utf-8')
        module._preserve(source, '시험')
        module._preserve(source, '시험')
        self.assertEqual(len(self.discarded()), 2, self.discarded())


class RollbackTests(RefreezeTestCase):
    def test_abort_restores_images_and_debt(self):
        self.begin()
        write(self.root / 'web' / 'static' / 'images' / 'new_def456.png', b'new-img')
        self.assertEqual(self.run_cli('abort', '--build', str(self.build)), 0)
        self.assertFalse((self.root / 'web' / 'static' / 'images' / 'new_def456.png').exists())
        self.assertTrue((self.root / 'web' / 'static' / 'images' / 'logo_abc123.png').exists())
        self.assertEqual(self.state()['evidence_debt']['decision'], 'defer')
        self.assertFalse(sorted(self.build.glob('_refreeze-*')))

    def test_abort_refused_after_completion(self):
        self.begin()
        self.fx.fill_staging()
        self.run_cli('check', '--build', str(self.build))
        self.run_cli('commit', '--build', str(self.build))
        write(self.root / 'web' / 'static' / 'images' / 'new_def456.png', b'new-img')
        self.assertEqual(self.run_cli('abort', '--build', str(self.build)), 1)
        self.assertTrue((self.root / 'web' / 'static' / 'images' / 'new_def456.png').exists())

    def test_verified_failure_rolls_back_everything(self):
        self.begin()
        self.fx.fill_staging()
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 0)
        write(self.root / 'web' / 'static' / 'images' / 'new_def456.png', b'new-img')
        # check 통과 뒤 포인터를 깨 verified 만 실패시킨다.
        spec = json.loads((self.fx.staging() / 'design-input.json').read_text())
        spec['cases'][0]['reference_capture']['sha256'] = '0' * 64
        (self.fx.staging() / 'design-input.json').write_text(json.dumps(spec), encoding='utf-8')
        self.assertEqual(self.run_cli('commit', '--build', str(self.build)), 3)
        self.assertEqual((self.build / 'design-ref' / 'screen.dc.html').read_bytes(),
                         b'<html>original</html>')
        self.assertEqual((self.build / 'captures' / 'screen-original.png').read_bytes(), b'orig')
        self.assertFalse((self.root / 'web' / 'static' / 'images' / 'new_def456.png').exists())
        self.assertEqual(self.state()['evidence_debt']['decision'], 'defer')

    def test_discarded_missing_on_both_sides_is_error(self):
        self.begin()
        self.fx.fill_staging()
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 0)
        journal = self.journal()
        journal['discard_set'].append('captures/does-not-exist.png')
        (self.fx.staging() / 'journal.json').write_text(json.dumps(journal), encoding='utf-8')
        self.assertEqual(self.run_cli('commit', '--build', str(self.build)), 1)


class StagingSelectionTests(RefreezeTestCase):
    def test_ambiguous_staging_is_error(self):
        self.begin()
        (self.build / '_refreeze-other').mkdir()
        self.assertEqual(self.run_cli('check', '--build', str(self.build)), 1)


class VerifyInputsTests(unittest.TestCase):
    def test_default_shells_out_to_checker_with_inputs_phase(self):
        import types
        seen = {}

        def fake_run(cmd, **kwargs):
            seen['cmd'] = cmd
            return types.SimpleNamespace(returncode=0, stdout='', stderr='')

        original = refreeze.subprocess.run
        refreeze.subprocess.run = fake_run
        try:
            ok, _detail = refreeze.verify_inputs(Path('/b'), Path('/r'))
        finally:
            refreeze.subprocess.run = original
        self.assertTrue(ok)
        self.assertIn('check_design_evidence.py', ' '.join(seen['cmd']))
        self.assertIn('--phase', seen['cmd'])
        self.assertEqual(seen['cmd'][seen['cmd'].index('--phase') + 1], 'inputs')


if __name__ == '__main__':
    unittest.main()
