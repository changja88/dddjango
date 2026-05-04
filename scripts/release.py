#!/usr/bin/env python3
"""Prepare a local dddjango plugin release."""

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


def run(command: list[str], root: Path) -> None:
    print(f"$ {' '.join(command)}")
    subprocess.run(command, cwd=root, check=True)


def ensure_clean_worktree(root: Path) -> None:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    )
    if result.stdout.strip():
        raise RuntimeError("릴리즈 전 워크트리가 깨끗해야 합니다. 먼저 변경사항을 커밋하거나 정리하세요.")


def ensure_tag_absent(root: Path, version: str) -> None:
    result = subprocess.run(
        ["git", "tag", "--list", version],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    )
    if result.stdout.strip():
        raise RuntimeError(f"이미 존재하는 태그입니다: {version}")


def validate(root: Path) -> None:
    run(["python3", "-m", "json.tool", ".codex-plugin/plugin.json"], root)
    run(["python3", "-m", "json.tool", ".claude-plugin/plugin.json"], root)
    run(["python3", "-m", "json.tool", ".claude-plugin/marketplace.json"], root)
    run(["python3", "-m", "json.tool", ".agents/plugins/marketplace.json"], root)
    run(["claude", "plugin", "validate", ".claude-plugin/plugin.json"], root)
    run(["claude", "plugin", "validate", "."], root)
    run(["git", "diff", "--check"], root)


def create_commit_and_tag(root: Path, version: str) -> None:
    run(["git", "add", ".codex-plugin/plugin.json"], root)
    run(["git", "add", ".claude-plugin/plugin.json"], root)
    run(["git", "add", ".claude-plugin/marketplace.json"], root)
    run(["git", "add", "README.md"], root)
    run(["git", "commit", "-m", f"chore: release {version}"], root)
    run(["git", "tag", version], root)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a local dddjango release.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--dry-run", action="store_true", help="Print the selected release without changing files")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = args.root.resolve()
    current = current_version(root)
    choices = print_menu(current)
    selected = input("릴리즈 타입을 선택하세요 [1-3]: ").strip()

    if selected not in choices:
        print("1, 2, 3 중 하나를 선택해야 합니다.", file=sys.stderr)
        return 2

    version = choices[selected]
    if args.dry_run:
        print(f"dry-run: {version} 릴리즈를 준비합니다.")
        return 0

    ensure_clean_worktree(root)
    ensure_tag_absent(root, version)
    update_release_files(root, version)
    validate(root)
    create_commit_and_tag(root, version)

    print()
    print(f"{version} 로컬 릴리즈 준비가 끝났습니다.")
    print("푸시는 직접 실행하세요:")
    print("  git push")
    print(f"  git push origin {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
