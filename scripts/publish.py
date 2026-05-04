#!/usr/bin/env python3
"""Push the current dddjango branch and latest release tag."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from release import ReleaseError, print_section, print_step, run


SEMVER_TAG_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def print_header() -> None:
    print("dddjango publish")
    print("=================")


def semver_key(tag: str) -> tuple[int, int, int]:
    match = SEMVER_TAG_RE.match(tag)
    if not match:
        raise ValueError(f"semver 태그가 아닙니다: {tag}")
    return tuple(int(part) for part in match.groups())


def current_branch(root: Path) -> str:
    result = run(["git", "branch", "--show-current"], root, quiet=True)
    branch = result.stdout.strip()
    if not branch:
        raise ReleaseError(
            "현재 브랜치를 확인할 수 없습니다.",
            hints=["detached HEAD 상태라면 브랜치를 체크아웃하세요."],
        )
    return branch


def ensure_git_repo(root: Path) -> None:
    result = run(["git", "rev-parse", "--is-inside-work-tree"], root, quiet=True)
    if result.stdout.strip() != "true":
        raise ReleaseError(
            "Git 저장소 안에서 실행해야 합니다.",
            hints=["git init", "git remote add origin https://github.com/changja88/dddjango.git"],
        )


def latest_semver_tag(root: Path) -> str:
    result = run(["git", "tag", "--list"], root, quiet=True)
    tags = [tag for tag in result.stdout.splitlines() if SEMVER_TAG_RE.match(tag)]
    if not tags:
        raise ReleaseError(
            "push할 릴리즈 태그가 없습니다.",
            hints=["make release"],
        )
    return max(tags, key=semver_key)


def run_step(label: str, action) -> None:
    try:
        action()
    except Exception:
        print_step(label, ok=False)
        raise
    print_step(label, ok=True)


def publish(root: Path, remote: str = "origin") -> None:
    print_header()

    print_section("배포 전 확인")
    run_step("Git 저장소 확인", lambda: ensure_git_repo(root))
    branch = current_branch(root)
    tag = latest_semver_tag(root)
    print_step(f"현재 브랜치: {branch}", ok=True)
    print_step(f"최신 태그: {tag}", ok=True)

    print_section("원격 push")
    run_step(f"브랜치 push ({remote}/{branch})", lambda: run(["git", "push", remote, branch], root, quiet=True))
    run_step(f"태그 push ({tag})", lambda: run(["git", "push", remote, tag], root, quiet=True))

    print()
    print("배포 push가 끝났습니다.")
    print(f"  branch: {branch}")
    print(f"  tag: {tag}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Push the current branch and latest dddjango release tag.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--remote", default="origin", help="Git remote name")
    parser.add_argument("--debug", action="store_true", help="Print Python traceback for unexpected failures")
    return parser.parse_args(argv)


def print_publish_error(error: ReleaseError) -> None:
    print()
    print("배포 push를 완료할 수 없습니다.")
    print()
    print(error.message)
    for detail in error.details:
        print(f"  - {detail}")
    if error.hints:
        print()
        print("먼저 아래 중 하나를 선택하세요:")
        for hint in error.hints:
            print(f"  {hint}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        publish(args.root.resolve(), remote=args.remote)
        return 0
    except ReleaseError as error:
        if args.debug:
            raise
        print_publish_error(error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
