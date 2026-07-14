from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_PROMPTS = (
    REPO_ROOT / "dddjango" / "commands" / "dddjango.md",
    REPO_ROOT / "codex-dddjango" / "skills" / "dddjango" / "SKILL.md",
)
ROLE_PROMPTS = tuple(sorted((REPO_ROOT / "dddjango" / "agents").glob("*.md"))) + (
    REPO_ROOT / "codex-dddjango" / "skills" / "dddjango-acceptance-tester" / "SKILL.md",
    REPO_ROOT / "codex-dddjango" / "skills" / "dddjango-coder" / "SKILL.md",
    REPO_ROOT / "codex-dddjango" / "skills" / "dddjango-design-architect" / "SKILL.md",
    REPO_ROOT / "codex-dddjango" / "skills" / "dddjango-design-review-api" / "SKILL.md",
    REPO_ROOT / "codex-dddjango" / "skills" / "dddjango-design-review-db" / "SKILL.md",
    REPO_ROOT / "codex-dddjango" / "skills" / "dddjango-design-review-ddd" / "SKILL.md",
    REPO_ROOT / "codex-dddjango" / "skills" / "dddjango-discipline-reviewer" / "SKILL.md",
)


def _phase(text: str, number: int) -> str:
    start = text.index(f"## Phase {number}")
    remainder = text[start:]
    candidates = [
        index
        for marker in ("\n## Phase ", "\n## 수정 모드")
        if (index := remainder.find(marker, 1)) >= 0
    ]
    return remainder[: min(candidates)] if candidates else remainder


def _numbered_step(section: str, number: int) -> str:
    start = section.index(f"\n{number}. **")
    end = section.find(f"\n{number + 1}. **", start + 1)
    return section[start:] if end < 0 else section[start:end]


class RuntimePolicyTest(unittest.TestCase):
    def test_opaque_boundary_precedes_general_read_only_audit(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                phase_two = _phase(text, 2)
                step_6 = _numbered_step(phase_two, 6)
                step_7 = _numbered_step(phase_two, 7)
                self.assertIn("check-migration-boundary.py", step_6)
                self.assertIn("<현재 작업 사이클 G0 baseline 경로>", step_6)
                self.assertNotIn(" snapshot ", step_6)
                final_verify = step_7.index("step 6과 같은 G0 baseline")
                self.assertIn("check-layer-skeleton.py", step_7)
                self.assertIn("discipline-reviewer", step_7)
                self.assertGreater(final_verify, 0)
                self.assertNotIn("guard", step_7)
                self.assertNotIn(" snapshot ", step_7)
                self.assertIn("DDDJANGO_G0_BOUNDARY_STATE", step_7)
                self.assertIn(
                    "<현재 작업 사이클 G0 baseline 절대 경로>",
                    step_7,
                )
                self.assertIn("환경값이 없거나 다른 root/state면 exit 1", step_7)
                self.assertIn("PYTHONDONTWRITEBYTECODE=1", step_7)
                self.assertIn("python3 -B", step_7)
                self.assertIn(
                    "스크립트의 1·2나 감수 지적이 있어도",
                    step_7,
                )
                self.assertIn(
                    "모든 결과가 clean이면 파일 쓰기·추가 LLM 감사 없이 즉시 step 8",
                    step_7,
                )
                self.assertIn("waiting-concurrent", step_7)
                self.assertIn("Git worktree", step_7)

    def test_layer_uses_current_cycle_structural_baseline(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("현재 작업 사이클의 G0 structural baseline", text)
                self.assertIn("내부 반송·수정에도 새 snapshot을 만들지", text)
                self.assertIn("step 6과 같은 G0 baseline", text)
                self.assertNotIn("<최초 G0 boundary state 경로>", text)

    def test_boundary_scope_is_established_before_semantic_repository_read(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                start = text.split("## 시작: 모드 판별", 1)[1].split(
                    "## Phase 0",
                    1,
                )[0]
                preflight = start.index("preflight . .dddjango")
                semantic_read = start.index("이 경계 밖 대상만 읽어")
                self.assertLess(preflight, semantic_read)
                self.assertIn("migration_roots", start)
                self.assertIn("migration_alias_targets", start)
                self.assertIn("external_owned_opaque_paths", start)
                self.assertIn("exact prefix", start)

    def test_artifact_preflight_precedes_unique_run_snapshot(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                phase_zero = text.split("## Phase 0", 1)[1].split(
                    "## Phase 1",
                    1,
                )[0]
                step_four = phase_zero.split("\n4. ", 1)[1].split("\n5. ", 1)[0]
                preflight = step_four.index("preflight . .dddjango")
                snapshot = step_four.index(" snapshot . ")
                self.assertLess(preflight, snapshot)
                self.assertIn("shell-safe canonical JSON", step_four)
                self.assertIn("manifest v11", step_four)
                self.assertIn(".runs/<run-id>/", step_four)
                self.assertIn("정상/재개 흐름에서는 호출하지 않는다", step_four)
                self.assertNotIn("migration-boundary-coordinator.lock", step_four)

    def test_new_opaque_discovery_restarts_write_once_epoch_in_every_phase(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("Phase 1·2 어느 역할이든", text)
                self.assertIn("편집 전에 멈추고 path만 반환", text)
                self.assertIn("expanded canonical list", text)
                self.assertIn("현재 증거 전체를 stale", text)

    def test_non_migration_diff_is_constructed_from_exact_allowlist(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                step_7 = _numbered_step(_phase(text, 2), 7)
                self.assertIn("allowlisted non-migration diff", step_7)

    def test_test_inventory_fallback_includes_both_pytest_name_directions(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("`test_*.py`·`*_test.py`·`tests.py`", text)
                self.assertIn("concurrent/unknown", text)
                self.assertIn("shared-generation dependency", text)

    def test_cleanup_is_bound_to_exact_run_pair(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("cleanup TARGET_DIR STATE_FILE RUN_ID", text)
                self.assertIn("exact-own pair", text)
                self.assertIn("foreign pair", text)
                self.assertNotIn("migration-boundary-coordinator.lock", text)

    def test_same_feature_uses_short_seed_commit_protocol_before_implementation(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("<산출물 폴더>/.runs/<run-id>/scope.md", text)
                self.assertIn("<산출물 폴더>/.runs/<run-id>/design-spec.md", text)
                phase_zero = _phase(text, 0)
                phase_one = _phase(text, 1)
                phase_two = _phase(text, 2)
                phase_three = _phase(text, 3)
                self.assertIn("promote-run-artifacts.py", phase_zero)
                self.assertIn(" seed . ", phase_zero)
                self.assertIn("promote-run-artifacts.py", phase_one)
                self.assertIn(" commit . ", phase_one)
                self.assertIn(".promotion.lock", phase_one)
                self.assertIn("exit 2", phase_one)
                self.assertIn("rebase", phase_one)
                self.assertIn(".canonical-base-scope.md", phase_one)
                self.assertIn("기존 작업본을 보존", phase_one)
                self.assertIn("transaction marker", phase_one)
                self.assertIn("promote-run-artifacts.py", phase_two)
                self.assertIn(" check . ", phase_two)
                self.assertIn("promote-run-artifacts.py", phase_three)
                self.assertIn(" check", phase_three)
                self.assertNotIn(" commit . ", phase_three)

    def test_final_generation_discards_all_evidence_on_change(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("HEAD, exclusion-filtered index", text)
                self.assertIn("regular bytes·symlink payload·submodule state", text)
                step_seven = _numbered_step(_phase(text, 2), 7)
                for token in ("테스트", "17종", "reviewer", "final verify", "전부 버리고"):
                    self.assertIn(token, step_seven)
                self.assertIn("ABA", text)
                self.assertIn("shared working-tree generation", text)

    def test_deterministic_generation_helper_covers_current_docs_not_foreign_runs(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                phase_two = _phase(text, 2)
                step_five = _numbered_step(phase_two, 5)
                step_seven = _numbered_step(phase_two, 7)
                self.assertIn("check-working-tree-generation.py", step_five)
                self.assertIn("check-working-tree-generation.py", step_seven)
                self.assertIn("promote-run-artifacts.py check", step_seven)
                self.assertIn("current-run/canonical byte equality", step_five)
                self.assertIn("foreign `.runs/*`", step_five)
                self.assertIn("마지막 `after`", step_five)

    def test_g2_approval_wait_is_revalidated_before_exact_cleanup(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                phase_three = _phase(text, 3)
                verify = phase_three.index("baseline `verify`")
                promotion = phase_three.index("promote-run-artifacts.py")
                fingerprint = phase_three.index("check-working-tree-generation.py")
                cleanup = phase_three.index(" cleanup . ")
                self.assertLess(verify, promotion)
                self.assertLess(promotion, fingerprint)
                self.assertLess(fingerprint, cleanup)
                self.assertIn("G2 승인과 증거를 stale", phase_three)

    def test_exit_two_invalidates_and_cleans_only_current_run(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("종료코드 2는 귀속을 단정하지 않는 invalidation", text)
                self.assertIn("상태를 `invalidated`", text)
                self.assertIn("현재 run의 exact `scope.md`·`design-spec.md`", text)

    def test_all_role_prompts_preserve_external_owned_first_discovery_boundary(self) -> None:
        self.assertEqual(14, len(ROLE_PROMPTS))
        for prompt in ROLE_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("external-owned opaque paths", text)
                self.assertIn("migration_roots", text)
                self.assertIn("migration_alias_targets", text)
                self.assertIn("external_owned_opaque_paths", text)
                self.assertIn("Read/Grep/Glob 순회 전에 prune", text)
                self.assertIn("처음 알게 되면", text)
                self.assertIn("즉시 중단", text)
                self.assertIn("열", text)

    def test_test_writing_roles_reconcile_current_obligation_tests(self) -> None:
        writing_roles = tuple(
            prompt
            for prompt in ROLE_PROMPTS
            if "acceptance-tester" in prompt.as_posix()
            or prompt.name == "coder.md"
            or "dddjango-coder" in prompt.as_posix()
        )
        self.assertEqual(4, len(writing_roles))
        for prompt in writing_roles:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("현재 의무", text)
                self.assertIn("retain/update/delete/add", text)
                self.assertIn("observed before path-state", text)
                self.assertIn("path-state TARGET_DIR PATH", text)
                self.assertIn("자체 계산하지 않고", text)
                self.assertIn("next.before == previous.after", text)

    def test_discipline_reviewers_use_one_pending_g0_baseline(self) -> None:
        reviewers = (
            REPO_ROOT / "dddjango" / "agents" / "discipline-reviewer.md",
            REPO_ROOT
            / "codex-dddjango"
            / "skills"
            / "dddjango-discipline-reviewer"
            / "SKILL.md",
        )
        for prompt in reviewers:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("pre-audit-clean(pending final verify)", text)
                self.assertIn("same-baseline verify", text)
                self.assertNotIn("final-audit guard", text)
                self.assertIn("shared generation 폐쇄", text)
                self.assertIn("cleanup TARGET_DIR STATE_FILE RUN_ID", text)


if __name__ == "__main__":
    unittest.main()
