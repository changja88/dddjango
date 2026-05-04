#!/usr/bin/env python3
"""Create and publish a dddjango plugin release."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


SEMVER_RE = re.compile(r"^v(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)$")
VERSION_FILES = (
    Path(".codex-plugin/plugin.json"),
    Path(".claude-plugin/plugin.json"),
    Path(".claude-plugin/marketplace.json"),
    Path("README.md"),
)


class ReleaseError(Exception):
    def __init__(
        self,
        message: str,
        *,
        details: list[str] | None = None,
        hints: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or []
        self.hints = hints or []


def next_version(current: str, bump: str) -> str:
    match = SEMVER_RE.match(current)
    if not match:
        raise ValueError(f"버전은 vX.Y.Z 형식이어야 합니다: {current}")

    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch"))

    if bump == "patch":
        patch += 1
    elif bump == "minor":
        minor += 1
        patch = 0
    elif bump == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError(f"지원하지 않는 릴리즈 타입입니다: {bump}")

    return f"v{major}.{minor}.{patch}"


def current_version(root: Path) -> str:
    data = read_json(root / ".codex-plugin/plugin.json")
    version = data["version"]
    return version if version.startswith("v") else f"v{version}"


def update_release_files(root: Path, version: str) -> list[Path]:
    plain_version = version.removeprefix("v")
    changed = [
        update_plugin_json(root / ".codex-plugin/plugin.json", plain_version),
        update_plugin_json(root / ".claude-plugin/plugin.json", plain_version),
        update_marketplace_json(root / ".claude-plugin/marketplace.json", plain_version),
        update_readme(root / "README.md", version),
    ]
    return changed


def update_plugin_json(path: Path, version: str) -> Path:
    data = read_json(path)
    data["version"] = version
    write_json(path, data)
    return path


def update_marketplace_json(path: Path, version: str) -> Path:
    data = read_json(path)
    data.setdefault("metadata", {})["version"] = version
    for plugin in data.get("plugins", []):
        plugin["version"] = version
    write_json(path, data)
    return path


def update_readme(path: Path, version: str) -> Path:
    text = path.read_text()
    text = re.sub(
        r"codex plugin marketplace add changja88/dddjango --ref v\d+\.\d+\.\d+",
        f"codex plugin marketplace add changja88/dddjango --ref {version}",
        text,
    )
    text = re.sub(
        r"Tag the release, for example `v\d+\.\d+\.\d+`\.",
        f"Tag the release, for example `{version}`.",
        text,
    )
    path.write_text(text)
    return path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def print_header() -> None:
    print("dddjango release")
    print("=================")
    print()


def print_menu(current: str) -> dict[str, str]:
    choices = {
        "1": ("patch", next_version(current, "patch"), "버그 수정, 성능 개선"),
        "2": ("minor", next_version(current, "minor"), "새 기능 추가"),
        "3": ("major", next_version(current, "major"), "핵심 아키텍처 변경"),
    }

    print(f"현재 버전: {current}")
    print()
    for number, (label, version, description) in choices.items():
        print(f"{number}) {label:<6} ({version}) — {description}")
    print()
    return {number: version for number, (_, version, _) in choices.items()}


def print_section(title: str) -> None:
    print()
    print(title)


def print_step(label: str, *, ok: bool, stream=None) -> None:
    stream = stream or sys.stdout
    mark = "✓" if ok else "✗"
    print(f"  {mark} {label}", file=stream)


def run_step(label: str, action) -> None:
    try:
        action()
    except Exception:
        print_step(label, ok=False)
        raise
    print_step(label, ok=True)


def run(command: list[str], root: Path, *, quiet: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        return result

    details = [f"$ {' '.join(command)}"]
    if result.stdout:
        details.extend(result.stdout.rstrip().splitlines())
    if result.stderr:
        details.extend(result.stderr.rstrip().splitlines())
    raise ReleaseError("명령 실행에 실패했습니다.", details=details)


def ensure_git_repo(root: Path) -> None:
    result = run(["git", "rev-parse", "--is-inside-work-tree"], root, quiet=True)
    if result.stdout.strip() != "true":
        raise ReleaseError(
            "Git 저장소 안에서 실행해야 합니다.",
            hints=["git init", "git remote add origin https://github.com/changja88/dddjango.git"],
        )


def ensure_clean_worktree(root: Path) -> None:
    result = run(["git", "status", "--short"], root, quiet=True)
    status = result.stdout.strip()
    if status:
        raise ReleaseError(
            "커밋되지 않은 변경사항이 있습니다:",
            details=[line.strip() for line in status.splitlines()],
            hints=[
                "git diff",
                "git add <변경된 파일>",
                'git commit -m "chore: prepare release"',
            ],
        )


def ensure_tag_absent(root: Path, version: str) -> None:
    result = run(["git", "tag", "--list", version], root, quiet=True)
    if result.stdout.strip():
        raise ReleaseError(
            f"이미 존재하는 태그입니다: {version}",
            hints=[
                f"git tag -d {version}",
                f"git push origin :refs/tags/{version}",
            ],
        )


def preflight(root: Path, version: str) -> None:
    print_section("릴리즈 전 확인")
    run_step("Git 저장소 확인", lambda: ensure_git_repo(root))
    run_step("워크트리 상태 확인", lambda: ensure_clean_worktree(root))
    run_step("태그 중복 확인", lambda: ensure_tag_absent(root, version))


def validate(root: Path) -> None:
    print_section("검증")
    run_step("Codex plugin JSON", lambda: run(["python3", "-m", "json.tool", ".codex-plugin/plugin.json"], root, quiet=True))
    run_step("Claude plugin JSON", lambda: run(["python3", "-m", "json.tool", ".claude-plugin/plugin.json"], root, quiet=True))
    run_step("Claude marketplace JSON", lambda: run(["python3", "-m", "json.tool", ".claude-plugin/marketplace.json"], root, quiet=True))
    run_step("Codex marketplace JSON", lambda: run(["python3", "-m", "json.tool", ".agents/plugins/marketplace.json"], root, quiet=True))
    run_step("Claude plugin manifest", lambda: run(["claude", "plugin", "validate", ".claude-plugin/plugin.json"], root, quiet=True))
    run_step("Claude marketplace manifest", lambda: run(["claude", "plugin", "validate", "."], root, quiet=True))
    run_step("Git whitespace check", lambda: run(["git", "diff", "--check"], root, quiet=True))


def create_commit_and_tag(root: Path, version: str) -> None:
    print_section("Git 작업")
    run_step(
        "릴리즈 파일 스테이징",
        lambda: run(
            [
                "git",
                "add",
                ".codex-plugin/plugin.json",
                ".claude-plugin/plugin.json",
                ".claude-plugin/marketplace.json",
                "README.md",
            ],
            root,
            quiet=True,
        ),
    )
    run_step("릴리즈 커밋 생성", lambda: run(["git", "commit", "-m", f"chore: release {version}"], root, quiet=True))
    run_step("릴리즈 태그 생성", lambda: run(["git", "tag", version], root, quiet=True))


def current_branch(root: Path) -> str:
    result = run(["git", "branch", "--show-current"], root, quiet=True)
    branch = result.stdout.strip()
    if not branch:
        raise ReleaseError(
            "현재 브랜치를 확인할 수 없습니다.",
            hints=["detached HEAD 상태라면 브랜치를 체크아웃하세요."],
        )
    return branch


def push_release(root: Path, version: str, remote: str = "origin") -> None:
    print_section("원격 push")
    branch = current_branch(root)
    run_step(f"브랜치 push ({remote}/{branch})", lambda: run(["git", "push", remote, branch], root, quiet=True))
    run_step(f"태그 push ({version})", lambda: run(["git", "push", remote, version], root, quiet=True))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a local dddjango release.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--dry-run", action="store_true", help="Print the selected release without changing files")
    parser.add_argument("--remote", default="origin", help="Git remote name")
    parser.add_argument("--debug", action="store_true", help="Print Python traceback for unexpected failures")
    return parser.parse_args(argv)


def print_release_error(error: ReleaseError) -> None:
    print()
    print("릴리즈를 시작할 수 없습니다.")
    print()
    print(error.message)
    for detail in error.details:
        print(f"  - {detail}")
    if error.hints:
        print()
        print("먼저 아래 중 하나를 선택하세요:")
        for hint in error.hints:
            print(f"  {hint}")


def run_release(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    print_header()
    current = current_version(root)
    choices = print_menu(current)
    selected = input("릴리즈 타입을 선택하세요 [1-3]: ").strip()
    print()

    if selected not in choices:
        print("1, 2, 3 중 하나를 선택해야 합니다.", file=sys.stderr)
        return 2

    version = choices[selected]
    if args.dry_run:
        print(f"dry-run: {version} 릴리즈를 준비합니다.")
        return 0

    preflight(root, version)

    print_section("릴리즈 파일 업데이트")
    run_step("버전 파일 업데이트", lambda: update_release_files(root, version))

    validate(root)
    create_commit_and_tag(root, version)
    push_release(root, version, remote=args.remote)

    print()
    print(f"{version} 릴리즈 완료")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        return run_release(args)
    except ReleaseError as error:
        if args.debug:
            raise
        print_release_error(error)
        return 1
    except (OSError, ValueError, json.JSONDecodeError) as error:
        if args.debug:
            raise
        print_release_error(ReleaseError(str(error)))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
