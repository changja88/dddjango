from __future__ import annotations

import concurrent.futures
import fcntl
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
BOUNDARY = REPO_ROOT / "dddjango" / "scripts" / "check-migration-boundary.py"
FINGERPRINT = REPO_ROOT / "dddjango" / "scripts" / "check-working-tree-generation.py"
PROMOTE = REPO_ROOT / "dddjango" / "scripts" / "promote-run-artifacts.py"


class ParallelRunHelperTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name) / "project"
        self.project.mkdir()
        (self.project / "tracked.py").write_text("VALUE = 1\n", encoding="utf-8")
        for command in (
            ["git", "init", "-q"],
            ["git", "add", "."],
            [
                "git",
                "-c",
                "user.name=dddjango-test",
                "-c",
                "user.email=dddjango@example.invalid",
                "commit",
                "-q",
                "-m",
                "baseline",
            ],
        ):
            result = subprocess.run(
                command,
                cwd=self.project,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def _boundary(
        self,
        action: str,
        state: Path,
        run_id: str | None = None,
        opaque_paths: list[str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["DDDJANGO_EXTERNAL_OWNED_OPAQUE_PATHS_JSON"] = json.dumps(
            opaque_paths or []
        )
        command = [sys.executable, str(BOUNDARY), action, str(self.project), str(state)]
        if run_id is not None:
            command.append(run_id)
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )

    def _fingerprint(self, state: Path, run_directory: Path) -> str:
        result = subprocess.run(
            [
                sys.executable,
                str(FINGERPRINT),
                str(self.project),
                str(state),
                str(run_directory),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result.stdout.strip().split("sha256=", 1)[1]

    def _path_state(self, path: Path) -> str:
        result = subprocess.run(
            [
                sys.executable,
                str(FINGERPRINT),
                "path-state",
                str(self.project),
                str(path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result.stdout.strip().split("path-state=", 1)[1]

    def _promotion_module(self, name: str):
        module_spec = importlib.util.spec_from_file_location(name, PROMOTE)
        self.assertIsNotNone(module_spec)
        self.assertIsNotNone(module_spec.loader)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module

    def test_fingerprint_tracks_current_docs_and_tree_but_ignores_foreign_run(self) -> None:
        run_id = "run-local-1234"
        run_directory = self.project / ".dddjango" / "feature" / ".runs" / run_id
        run_directory.mkdir(parents=True)
        scope = run_directory / "scope.md"
        design = run_directory / "design-spec.md"
        scope.write_text("scope-a\n", encoding="utf-8")
        design.write_text("design-a\n", encoding="utf-8")
        canonical_scope = run_directory.parent.parent / "scope.md"
        canonical_design = run_directory.parent.parent / "design-spec.md"
        canonical_scope.write_bytes(scope.read_bytes())
        canonical_design.write_bytes(design.read_bytes())
        state = run_directory / f"migration-boundary-epoch-20260714-{run_id}.json"
        snapshot = self._boundary("snapshot", state)
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)

        baseline = self._fingerprint(state, run_directory)
        self.assertEqual(baseline, self._fingerprint(state, run_directory))
        transaction = run_directory.parent / ".promotion-transaction.json"
        transaction.write_text("{}\n", encoding="utf-8")
        blocked = subprocess.run(
            [
                sys.executable,
                str(FINGERPRINT),
                str(self.project),
                str(state),
                str(run_directory),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(1, blocked.returncode, blocked.stdout + blocked.stderr)
        self.assertIn("transaction", blocked.stderr)
        transaction.unlink()
        scope.write_text("scope-b\n", encoding="utf-8")
        canonical_scope.write_text("scope-b\n", encoding="utf-8")
        self.assertNotEqual(baseline, self._fingerprint(state, run_directory))
        scope.write_text("scope-a\n", encoding="utf-8")
        canonical_scope.write_text("scope-a\n", encoding="utf-8")

        canonical_scope.write_text("canonical-scope\n", encoding="utf-8")
        mismatch = subprocess.run(
            [
                sys.executable,
                str(FINGERPRINT),
                str(self.project),
                str(state),
                str(run_directory),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(1, mismatch.returncode, mismatch.stdout + mismatch.stderr)
        self.assertIn("rebase", mismatch.stderr)
        canonical_scope.write_text("scope-a\n", encoding="utf-8")
        self.assertEqual(baseline, self._fingerprint(state, run_directory))

        foreign = (
            self.project
            / ".dddjango"
            / "feature"
            / ".runs"
            / "run-foreign-1234"
        )
        foreign.mkdir()
        (foreign / "design-spec.md").write_text("foreign-a\n", encoding="utf-8")
        self.assertEqual(baseline, self._fingerprint(state, run_directory))
        (foreign / "design-spec.md").write_text("foreign-b\n", encoding="utf-8")
        self.assertEqual(baseline, self._fingerprint(state, run_directory))
        subprocess.run(
            ["git", "add", "-f", str(foreign / "design-spec.md")],
            cwd=self.project,
            check=True,
            capture_output=True,
        )
        self.assertEqual(baseline, self._fingerprint(state, run_directory))

        (self.project / "tracked.py").write_text("VALUE = 2\n", encoding="utf-8")
        self.assertNotEqual(baseline, self._fingerprint(state, run_directory))

    def test_fingerprint_rejects_boundary_state_from_another_run(self) -> None:
        first_id = "run-first-1234"
        first = self.project / ".dddjango" / "feature" / ".runs" / first_id
        second = (
            self.project / ".dddjango" / "feature" / ".runs" / "run-second-5678"
        )
        first.mkdir(parents=True)
        second.mkdir(parents=True)
        for run in (first, second):
            (run / "scope.md").write_text("scope\n", encoding="utf-8")
            (run / "design-spec.md").write_text("design\n", encoding="utf-8")
        state = first / f"migration-boundary-epoch-20260714-{first_id}.json"
        snapshot = self._boundary("snapshot", state)
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)

        result = subprocess.run(
            [
                sys.executable,
                str(FINGERPRINT),
                str(self.project),
                str(state),
                str(second),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("expected run-id exact pair", result.stderr)

    def test_fingerprint_covers_staged_mode_and_symlink_but_excludes_cache_and_opaque(self) -> None:
        run_id = "run-surface-1234"
        run = self.project / ".dddjango" / "feature" / ".runs" / run_id
        run.mkdir(parents=True)
        (run / "scope.md").write_text("scope\n", encoding="utf-8")
        (run / "design-spec.md").write_text("design\n", encoding="utf-8")
        feature = run.parent.parent
        (feature / "scope.md").write_text("scope\n", encoding="utf-8")
        (feature / "design-spec.md").write_text("design\n", encoding="utf-8")
        opaque = self.project / "opaque-owned.txt"
        opaque.write_text("opaque-a\n", encoding="utf-8")
        state = run / f"migration-boundary-epoch-20260714-{run_id}.json"
        snapshot = self._boundary(
            "snapshot",
            state,
            opaque_paths=["opaque-owned.txt"],
        )
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)
        baseline = self._fingerprint(state, run)

        cache_file = self.project / ".pytest_cache" / "foreign"
        cache_file.parent.mkdir()
        cache_file.write_text("cache\n", encoding="utf-8")
        opaque.write_text("opaque-b\n", encoding="utf-8")
        self.assertEqual(baseline, self._fingerprint(state, run))

        link = self.project / "untracked-link"
        try:
            link.symlink_to("target-a")
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        self.assertNotEqual(baseline, self._fingerprint(state, run))
        link.unlink()
        self.assertEqual(baseline, self._fingerprint(state, run))

        tracked = self.project / "tracked.py"
        tracked.chmod(0o755)
        self.assertNotEqual(baseline, self._fingerprint(state, run))
        tracked.chmod(0o644)
        self.assertEqual(baseline, self._fingerprint(state, run))

        tracked.write_text("VALUE = 3\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "tracked.py"],
            cwd=self.project,
            check=True,
            capture_output=True,
        )
        self.assertNotEqual(baseline, self._fingerprint(state, run))

    def test_fingerprint_tracks_submodule_status(self) -> None:
        submodule_source = self.project.parent / "submodule-source"
        submodule_source.mkdir()
        (submodule_source / "value.txt").write_text("one\n", encoding="utf-8")
        for command in (
            ["git", "init", "-q"],
            ["git", "add", "value.txt"],
            [
                "git",
                "-c",
                "user.name=dddjango-test",
                "-c",
                "user.email=dddjango@example.invalid",
                "commit",
                "-q",
                "-m",
                "submodule baseline",
            ],
        ):
            result = subprocess.run(
                command,
                cwd=submodule_source,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        add = subprocess.run(
            [
                "git",
                "-c",
                "protocol.file.allow=always",
                "submodule",
                "add",
                "-q",
                str(submodule_source),
                "vendor/submodule",
            ],
            cwd=self.project,
            capture_output=True,
            text=True,
            check=False,
        )
        if add.returncode != 0:
            self.skipTest(f"local submodule unavailable: {add.stderr.strip()}")

        run_id = "run-submodule-1234"
        run = self.project / ".dddjango" / "feature" / ".runs" / run_id
        run.mkdir(parents=True)
        (run / "scope.md").write_text("scope\n", encoding="utf-8")
        (run / "design-spec.md").write_text("design\n", encoding="utf-8")
        feature = run.parent.parent
        (feature / "scope.md").write_text("scope\n", encoding="utf-8")
        (feature / "design-spec.md").write_text("design\n", encoding="utf-8")
        state = run / f"migration-boundary-epoch-20260714-{run_id}.json"
        snapshot = self._boundary("snapshot", state)
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)
        baseline = self._fingerprint(state, run)

        (self.project / "vendor" / "submodule" / "value.txt").write_text(
            "two\n",
            encoding="utf-8",
        )

        self.assertNotEqual(baseline, self._fingerprint(state, run))

    def test_path_state_distinguishes_create_update_mode_type_and_delete(self) -> None:
        path = self.project / "ledger-entry"
        self.assertEqual("absent", self._path_state(path))

        path.write_text("one\n", encoding="utf-8")
        created = self._path_state(path)
        self.assertRegex(created, r"^[0-9a-f]{64}$")
        path.write_text("two\n", encoding="utf-8")
        updated = self._path_state(path)
        self.assertNotEqual(created, updated)

        path.chmod(0o755)
        mode_changed = self._path_state(path)
        self.assertNotEqual(updated, mode_changed)
        path.unlink()
        try:
            path.symlink_to("target")
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        type_changed = self._path_state(path)
        self.assertNotEqual(mode_changed, type_changed)
        path.unlink()
        self.assertEqual("absent", self._path_state(path))

    def test_same_anchor_concurrent_promotion_has_one_winner(self) -> None:
        feature = self.project / ".dddjango" / "feature"
        feature.mkdir(parents=True)
        canonical_scope = feature / "scope.md"
        canonical_design = feature / "design-spec.md"
        canonical_scope.write_text("scope-base\n", encoding="utf-8")
        canonical_design.write_text("design-base\n", encoding="utf-8")
        expected = (
            hashlib.sha256(canonical_scope.read_bytes()).hexdigest(),
            hashlib.sha256(canonical_design.read_bytes()).hexdigest(),
        )
        run_ids = ("run-alpha-1234", "run-beta-5678")
        contents = {
            run_ids[0]: (b"scope-alpha\n", b"design-alpha\n"),
            run_ids[1]: (b"scope-beta\n", b"design-beta\n"),
        }
        runs: list[Path] = []
        for run_id in run_ids:
            run = feature / ".runs" / run_id
            run.mkdir(parents=True)
            (run / "scope.md").write_bytes(contents[run_id][0])
            (run / "design-spec.md").write_bytes(contents[run_id][1])
            runs.append(run)
        barrier = threading.Barrier(2)

        def promote(run: Path) -> subprocess.CompletedProcess[str]:
            barrier.wait(timeout=5)
            return subprocess.run(
                [
                    sys.executable,
                    str(PROMOTE),
                    "commit",
                    str(self.project),
                    str(run),
                    expected[0],
                    expected[1],
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            results = tuple(executor.map(promote, runs))
        self.assertEqual([0, 2], sorted(result.returncode for result in results))
        promoted = (canonical_scope.read_bytes(), canonical_design.read_bytes())
        self.assertIn(promoted, contents.values())

    def test_seed_and_commit_share_one_pair_lock(self) -> None:
        feature = self.project / ".dddjango" / "feature"
        canonical_scope = feature / "scope.md"
        canonical_design = feature / "design-spec.md"
        feature.mkdir(parents=True)
        canonical_scope.write_text("scope-base\n", encoding="utf-8")
        canonical_design.write_text("design-base\n", encoding="utf-8")
        expected = (
            hashlib.sha256(canonical_scope.read_bytes()).hexdigest(),
            hashlib.sha256(canonical_design.read_bytes()).hexdigest(),
        )
        writer = feature / ".runs" / "run-writer-1234"
        reader = feature / ".runs" / "run-reader-5678"
        writer.mkdir(parents=True)
        reader.mkdir(parents=True)
        (writer / "scope.md").write_text("scope-next\n", encoding="utf-8")
        (writer / "design-spec.md").write_text("design-next\n", encoding="utf-8")
        barrier = threading.Barrier(2)

        def run(command: list[str]) -> subprocess.CompletedProcess[str]:
            barrier.wait(timeout=5)
            return subprocess.run(command, capture_output=True, text=True, check=False)

        seed_command = [
            sys.executable,
            str(PROMOTE),
            "seed",
            str(self.project),
            str(reader),
        ]
        commit_command = [
            sys.executable,
            str(PROMOTE),
            "commit",
            str(self.project),
            str(writer),
            expected[0],
            expected[1],
        ]
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            seed_result, commit_result = tuple(
                executor.map(run, (seed_command, commit_command))
            )
        self.assertEqual(0, seed_result.returncode, seed_result.stdout + seed_result.stderr)
        self.assertEqual(
            0, commit_result.returncode, commit_result.stdout + commit_result.stderr
        )
        seeded = (
            (reader / "scope.md").read_bytes(),
            (reader / "design-spec.md").read_bytes(),
        )
        self.assertIn(
            seeded,
            {
                (b"scope-base\n", b"design-base\n"),
                (b"scope-next\n", b"design-next\n"),
            },
        )

    def test_seed_waits_for_feature_pair_lock(self) -> None:
        feature = self.project / ".dddjango" / "feature"
        runs = feature / ".runs"
        reader = runs / "run-reader-1234"
        reader.mkdir(parents=True)
        (feature / "scope.md").write_text("scope\n", encoding="utf-8")
        (feature / "design-spec.md").write_text("design\n", encoding="utf-8")
        lock_path = runs / ".promotion.lock"
        with lock_path.open("a+b") as lock_stream:
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(PROMOTE),
                    "seed",
                    str(self.project),
                    str(reader),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                with self.assertRaises(subprocess.TimeoutExpired):
                    process.wait(timeout=0.5)
            finally:
                fcntl.flock(lock_stream.fileno(), fcntl.LOCK_UN)
        stdout, stderr = process.communicate(timeout=5)
        self.assertEqual(0, process.returncode, stdout + stderr)
        self.assertEqual(b"scope\n", (reader / "scope.md").read_bytes())
        self.assertEqual(b"design\n", (reader / "design-spec.md").read_bytes())

    def test_rebase_snapshot_preserves_current_run_documents(self) -> None:
        feature = self.project / ".dddjango" / "feature"
        run = feature / ".runs" / "run-rebase-1234"
        run.mkdir(parents=True)
        (feature / "scope.md").write_text("scope-latest\n", encoding="utf-8")
        (feature / "design-spec.md").write_text(
            "design-latest\n", encoding="utf-8"
        )
        current = (b"scope-current\n", b"design-current\n")
        (run / "scope.md").write_bytes(current[0])
        (run / "design-spec.md").write_bytes(current[1])

        result = subprocess.run(
            [
                sys.executable,
                str(PROMOTE),
                "rebase",
                str(self.project),
                str(run),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(current[0], (run / "scope.md").read_bytes())
        self.assertEqual(current[1], (run / "design-spec.md").read_bytes())
        self.assertEqual(
            b"scope-latest\n", (run / ".canonical-base-scope.md").read_bytes()
        )
        self.assertEqual(
            b"design-latest\n",
            (run / ".canonical-base-design-spec.md").read_bytes(),
        )

    def test_later_canonical_commit_makes_earlier_run_check_conflict(self) -> None:
        feature = self.project / ".dddjango" / "feature"
        feature.mkdir(parents=True)
        canonical = (feature / "scope.md", feature / "design-spec.md")
        canonical[0].write_text("scope-base\n", encoding="utf-8")
        canonical[1].write_text("design-base\n", encoding="utf-8")
        anchors = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in canonical)
        first = feature / ".runs" / "run-first-1234"
        second = feature / ".runs" / "run-second-5678"
        first.mkdir(parents=True)
        second.mkdir(parents=True)
        for path, content in zip(
            (first / "scope.md", first / "design-spec.md"),
            (b"scope-first\n", b"design-first\n"),
            strict=True,
        ):
            path.write_bytes(content)
        first_commit = subprocess.run(
            [sys.executable, str(PROMOTE), "commit", str(self.project), str(first), *anchors],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, first_commit.returncode, first_commit.stdout + first_commit.stderr)
        first_anchors = tuple(
            hashlib.sha256(path.read_bytes()).hexdigest() for path in canonical
        )
        (second / "scope.md").write_text("scope-both\n", encoding="utf-8")
        (second / "design-spec.md").write_text("design-both\n", encoding="utf-8")
        second_commit = subprocess.run(
            [
                sys.executable,
                str(PROMOTE),
                "commit",
                str(self.project),
                str(second),
                *first_anchors,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, second_commit.returncode, second_commit.stdout + second_commit.stderr)

        check = subprocess.run(
            [sys.executable, str(PROMOTE), "check", str(self.project), str(first)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(2, check.returncode, check.stdout + check.stderr)
        self.assertIn("rebase", check.stderr)

    def test_external_canonical_change_after_commit_allows_new_seed(self) -> None:
        feature = self.project / ".dddjango" / "feature"
        feature.mkdir(parents=True)
        canonical = (feature / "scope.md", feature / "design-spec.md")
        canonical[0].write_text("scope-base\n", encoding="utf-8")
        canonical[1].write_text("design-base\n", encoding="utf-8")
        expected = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in canonical)
        old_run = feature / ".runs" / "run-old-1234"
        old_run.mkdir(parents=True)
        (old_run / "scope.md").write_text("scope-committed\n", encoding="utf-8")
        (old_run / "design-spec.md").write_text("design-committed\n", encoding="utf-8")
        commit = subprocess.run(
            [
                sys.executable,
                str(PROMOTE),
                "commit",
                str(self.project),
                str(old_run),
                *expected,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, commit.returncode, commit.stdout + commit.stderr)

        external = (b"scope-external\n", b"design-external\n")
        canonical[0].write_bytes(external[0])
        canonical[1].write_bytes(external[1])
        new_run = feature / ".runs" / "run-new-5678"
        new_run.mkdir(parents=True)
        seed = subprocess.run(
            [sys.executable, str(PROMOTE), "seed", str(self.project), str(new_run)],
            capture_output=True,
            text=True,
            check=False,
        )
        old_check = subprocess.run(
            [sys.executable, str(PROMOTE), "check", str(self.project), str(old_run)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, seed.returncode, seed.stdout + seed.stderr)
        self.assertEqual(external[0], (new_run / "scope.md").read_bytes())
        self.assertEqual(external[1], (new_run / "design-spec.md").read_bytes())
        self.assertEqual(2, old_check.returncode, old_check.stdout + old_check.stderr)

    def test_commit_rolls_back_if_current_run_changes_during_locked_copy(self) -> None:
        module = self._promotion_module("promotion_for_source_overlap")
        feature = self.project / ".dddjango" / "feature"
        run = feature / ".runs" / "run-overlap-1234"
        run.mkdir(parents=True)
        canonical = (feature / "scope.md", feature / "design-spec.md")
        canonical[0].write_text("scope-base\n", encoding="utf-8")
        canonical[1].write_text("design-base\n", encoding="utf-8")
        original = tuple(path.read_bytes() for path in canonical)
        expected = tuple(hashlib.sha256(content).hexdigest() for content in original)
        (run / "scope.md").write_text("scope-next\n", encoding="utf-8")
        (run / "design-spec.md").write_text("design-next\n", encoding="utf-8")
        original_replace = module._replace
        injected = False

        def mutate_source_after_scope_copy(path: Path, content: bytes) -> None:
            nonlocal injected
            original_replace(path, content)
            if path == canonical[0].resolve() and not injected:
                injected = True
                (run / "design-spec.md").write_text("foreign-overlap\n", encoding="utf-8")

        with mock.patch.object(module, "_replace", mutate_source_after_scope_copy):
            with self.assertRaises(module.PromotionError):
                module._promote(self.project.resolve(), run.resolve(), *expected)

        self.assertEqual(original, tuple(path.read_bytes() for path in canonical))
        self.assertFalse((feature / ".runs" / ".promotion-transaction.json").exists())

    def test_commit_rolls_back_pair_when_second_replace_fails(self) -> None:
        module = self._promotion_module("promotion_for_second_replace_failure")
        feature = self.project / ".dddjango" / "feature"
        run = feature / ".runs" / "run-replace-1234"
        run.mkdir(parents=True)
        canonical = (feature / "scope.md", feature / "design-spec.md")
        canonical[0].write_text("scope-base\n", encoding="utf-8")
        canonical[1].write_text("design-base\n", encoding="utf-8")
        original = tuple(path.read_bytes() for path in canonical)
        expected = tuple(hashlib.sha256(content).hexdigest() for content in original)
        (run / "scope.md").write_text("scope-next\n", encoding="utf-8")
        (run / "design-spec.md").write_text("design-next\n", encoding="utf-8")
        original_replace = module._replace
        injected = False

        def fail_second_target_once(path: Path, content: bytes) -> None:
            nonlocal injected
            if path == canonical[1].resolve() and not injected:
                injected = True
                raise PermissionError("injected second target failure")
            original_replace(path, content)

        with mock.patch.object(module, "_replace", fail_second_target_once):
            with self.assertRaises(PermissionError):
                module._promote(self.project.resolve(), run.resolve(), *expected)

        self.assertEqual(original, tuple(path.read_bytes() for path in canonical))
        self.assertFalse((feature / ".runs" / ".promotion-receipt.json").exists())
        self.assertFalse((feature / ".runs" / ".promotion-transaction.json").exists())

    def test_incomplete_pair_transaction_is_fail_closed_on_restart(self) -> None:
        module = self._promotion_module("promotion_for_torn_pair")
        feature = self.project / ".dddjango" / "feature"
        runs = feature / ".runs"
        reader = runs / "run-reader-1234"
        reader.mkdir(parents=True)
        canonical = (feature / "scope.md", feature / "design-spec.md")
        canonical[0].write_text("scope-base\n", encoding="utf-8")
        canonical[1].write_text("design-base\n", encoding="utf-8")
        previous = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in canonical)
        intended_bytes = (b"scope-next\n", b"design-next\n")
        intended = tuple(hashlib.sha256(content).hexdigest() for content in intended_bytes)
        (runs / ".promotion-transaction.json").write_bytes(
            module._transaction_bytes(previous, intended)
        )
        canonical[0].write_bytes(intended_bytes[0])

        result = subprocess.run(
            [sys.executable, str(PROMOTE), "seed", str(self.project), str(reader)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("torn pair", result.stderr)
        self.assertFalse((reader / "scope.md").exists())

    def test_pre_replace_transaction_marker_is_safely_recovered(self) -> None:
        module = self._promotion_module("promotion_for_pre_replace_crash")
        feature = self.project / ".dddjango" / "feature"
        runs = feature / ".runs"
        reader = runs / "run-reader-5678"
        reader.mkdir(parents=True)
        canonical = (feature / "scope.md", feature / "design-spec.md")
        canonical[0].write_text("scope-base\n", encoding="utf-8")
        canonical[1].write_text("design-base\n", encoding="utf-8")
        previous = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in canonical)
        intended = tuple(
            hashlib.sha256(content).hexdigest()
            for content in (b"scope-next\n", b"design-next\n")
        )
        transaction = runs / ".promotion-transaction.json"
        transaction.write_bytes(module._transaction_bytes(previous, intended))

        result = subprocess.run(
            [sys.executable, str(PROMOTE), "seed", str(self.project), str(reader)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertFalse(transaction.exists())
        self.assertEqual(canonical[0].read_bytes(), (reader / "scope.md").read_bytes())
        self.assertEqual(
            canonical[1].read_bytes(),
            (reader / "design-spec.md").read_bytes(),
        )

    def test_completed_pair_with_crash_tail_marker_is_safely_recovered(self) -> None:
        module = self._promotion_module("promotion_for_completed_crash_tail")
        feature = self.project / ".dddjango" / "feature"
        runs = feature / ".runs"
        reader = runs / "run-reader-9012"
        reader.mkdir(parents=True)
        canonical = (feature / "scope.md", feature / "design-spec.md")
        canonical[0].write_text("scope-intended\n", encoding="utf-8")
        canonical[1].write_text("design-intended\n", encoding="utf-8")
        intended = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in canonical)
        previous = tuple(
            hashlib.sha256(content).hexdigest()
            for content in (b"scope-previous\n", b"design-previous\n")
        )
        transaction = runs / ".promotion-transaction.json"
        receipt = runs / ".promotion-receipt.json"
        transaction.write_bytes(module._transaction_bytes(previous, intended))
        receipt.write_bytes(module._receipt_bytes(intended))

        result = subprocess.run(
            [sys.executable, str(PROMOTE), "seed", str(self.project), str(reader)],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertFalse(transaction.exists())
        self.assertTrue(receipt.is_file())
        self.assertEqual(canonical[0].read_bytes(), (reader / "scope.md").read_bytes())
        self.assertEqual(
            canonical[1].read_bytes(),
            (reader / "design-spec.md").read_bytes(),
        )

    def test_promotion_rejects_symlink_run_alias(self) -> None:
        runs = self.project / ".dddjango" / "feature" / ".runs"
        real_run = runs / "run-real-1234"
        alias_run = runs / "run-alias-5678"
        real_run.mkdir(parents=True)
        try:
            alias_run.symlink_to(real_run, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")

        result = subprocess.run(
            [
                sys.executable,
                str(PROMOTE),
                "seed",
                str(self.project),
                str(alias_run),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("symlink", result.stderr)

    def test_cleanup_rolls_receipt_back_when_state_unlink_fails(self) -> None:
        run_id = "run-rollback-1234"
        run_directory = self.project / ".dddjango" / "feature" / ".runs" / run_id
        state = run_directory / f"migration-boundary-epoch-20260714-{run_id}.json"
        snapshot = self._boundary("snapshot", state)
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)
        receipt = state.with_name(f"{state.name}.write-once")
        receipt_before = receipt.read_bytes()
        module_spec = importlib.util.spec_from_file_location("boundary_for_rollback", BOUNDARY)
        self.assertIsNotNone(module_spec)
        self.assertIsNotNone(module_spec.loader)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        original_unlink = Path.unlink

        def fail_state_unlink(path: Path, missing_ok: bool = False) -> None:
            if path == state:
                raise PermissionError("injected state unlink failure")
            original_unlink(path, missing_ok=missing_ok)

        with mock.patch.object(Path, "unlink", fail_state_unlink):
            with self.assertRaises(module.ManifestError):
                module._cleanup(self.project.resolve(), state, run_id)
        self.assertTrue(state.is_file())
        self.assertEqual(receipt_before, receipt.read_bytes())

    def test_cleanup_rejects_pair_outside_exact_run_directory(self) -> None:
        run_id = "run-legacy-1234"
        state = self.project / f"migration-boundary-epoch-20260714-{run_id}.json"
        snapshot = self._boundary("snapshot", state)
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)

        cleanup = self._boundary("cleanup", state, run_id)

        self.assertEqual(1, cleanup.returncode, cleanup.stdout + cleanup.stderr)
        self.assertIn(".runs/<RUN_ID>", cleanup.stderr)
        self.assertTrue(state.is_file())

    def test_cleanup_rejects_nested_non_feature_run_directory(self) -> None:
        run_id = "run-nested-1234"
        state = (
            self.project
            / ".dddjango"
            / "group"
            / "feature"
            / ".runs"
            / run_id
            / f"migration-boundary-epoch-20260714-{run_id}.json"
        )
        snapshot = self._boundary("snapshot", state)
        self.assertEqual(0, snapshot.returncode, snapshot.stdout + snapshot.stderr)

        cleanup = self._boundary("cleanup", state, run_id)

        self.assertEqual(1, cleanup.returncode, cleanup.stdout + cleanup.stderr)
        self.assertIn(".dddjango/<feature>/.runs/<RUN_ID>", cleanup.stderr)
        self.assertTrue(state.is_file())


if __name__ == "__main__":
    unittest.main()
