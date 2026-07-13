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


class RuntimePolicyTest(unittest.TestCase):
    def test_opaque_boundary_precedes_general_read_only_audit(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                step_6 = text.split(
                    "6. **일반 검사 전 opaque boundary 사전 검증**:",
                    1,
                )[1].split(
                    "\n7. **선행 17종·layer→최종 독립 감사→동일 baseline 최종 verify**:",
                    1,
                )[0]
                step_7 = text.split(
                    "7. **선행 17종·layer→최종 독립 감사→동일 baseline 최종 verify**:",
                    1,
                )[1].split("\n8. **G2 배너**:", 1)[0]
                self.assertIn("check-migration-boundary.py", step_6)
                self.assertIn("<현재 작업 사이클 G0 baseline 경로>", step_6)
                self.assertNotIn(" snapshot ", step_6)
                layer = step_7.index("check-layer-skeleton.py")
                reviewer = step_7.index("discipline-reviewer")
                final_verify = step_7.index("step 6과 같은 G0 baseline")
                self.assertLess(layer, reviewer)
                self.assertLess(reviewer, final_verify)
                self.assertNotIn("guard", step_7)
                self.assertNotIn(" snapshot ", step_7)
                self.assertIn("DDDJANGO_G0_BOUNDARY_STATE", step_7)
                self.assertIn(
                    "<현재 작업 사이클 G0 baseline 절대 경로>",
                    step_7,
                )
                self.assertIn("17종은 환경값이 없거나 다른 root/state면 exit 1", step_7)
                self.assertIn("layer는 같은 절대 baseline 경로를 argv로 직접 검증", step_7)
                self.assertIn("PYTHONDONTWRITEBYTECODE=1", step_7)
                self.assertIn("python3 -B", step_7)
                self.assertIn(
                    "스크립트의 1·2나 감수 지적이 있어도 아직 귀속·반송·수정하지 않는다",
                    step_7,
                )
                self.assertIn(
                    "모든 결과가 clean이면 파일 쓰기·추가 LLM 감사 없이 즉시 step 8",
                    step_7,
                )

    def test_layer_uses_current_cycle_structural_baseline(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("현재 작업 사이클의 G0 structural baseline", text)
                self.assertIn(
                    "내부 감수 반송에는 이 baseline을 그대로 재사용",
                    text,
                )
                self.assertIn("같은 G0 baseline", text)
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

    def test_artifact_preflight_precedes_recover_snapshot_and_lock(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                phase_zero = text.split("## Phase 0", 1)[1].split(
                    "## Phase 1",
                    1,
                )[0]
                step_four = phase_zero.split("\n4. ", 1)[1].split("\n5. ", 1)[0]
                preflight = step_four.index("preflight . .dddjango")
                stale_remove = step_four.index("rmdir")
                recover = step_four.index(" recover . .dddjango")
                snapshot = step_four.index(" snapshot . ")
                lock = step_four.index("mkdir .dddjango/migration-boundary-coordinator.lock")
                self.assertLess(preflight, stale_remove)
                self.assertLess(stale_remove, recover)
                self.assertLess(recover, snapshot)
                self.assertLess(snapshot, lock)
                self.assertIn("shell-safe canonical JSON", step_four)
                self.assertIn("manifest v11", step_four)

    def test_new_opaque_discovery_restarts_write_once_epoch_in_every_phase(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("Phase 1·2 어느 역할이든", text)
                self.assertIn("manifest나 역할 입력을 같은 epoch에서 갱신하지 않는다", text)
                self.assertIn("expanded canonical exact-file list", text)
                self.assertIn("설계·테스트·구현 증거를 전부 stale", text)

    def test_non_migration_diff_is_constructed_from_exact_allowlist(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                step_7 = text.split(
                    "7. **선행 17종·layer→최종 독립 감사→동일 baseline 최종 verify**:",
                    1,
                )[1].split("\n8. **G2 배너**:", 1)[0]
                self.assertIn("git diff -- <allowlisted paths>", step_7)
                self.assertIn("전역 diff", step_7)
                self.assertIn("사후 내용 필터", step_7)

    def test_test_inventory_fallback_includes_both_pytest_name_directions(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn("`test_*.py`·`*_test.py`·`tests.py`", text)
                self.assertIn("decode·parse·요약·의미 분류·LLM 입력은 금지", text)

    def test_cleanup_rejects_dangling_symlink_artifacts(self) -> None:
        for prompt in RUNTIME_PROMPTS:
            with self.subTest(prompt=prompt):
                text = prompt.read_text(encoding="utf-8")
                self.assertIn('test ! -e "<경로>" && test ! -L "<경로>"', text)
                self.assertIn(
                    'test ! -e "<lock 경로>" && test ! -L "<lock 경로>"',
                    text,
                )

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
                self.assertIn("같은 G0 baseline", text)
                self.assertNotIn("final-audit guard", text)


if __name__ == "__main__":
    unittest.main()
