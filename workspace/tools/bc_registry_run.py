#!/usr/bin/env python3
"""결정적 백스톱 27종을 한 BC 에 일괄 실행 — 클린룸 리빌드 라운드의 C축(registry 판정).

검사기는 저장소 루트 모양(fixture 와 동일: application/ + <project>/ + framework/)을
받으므로, 대상 BC 하나만 담은 «그림자 사본»을 임시로 지어 실행한다 —
⑴ 이웃 BC 의 위반이 판정에 섞이지 않고 ⑵ 사본은 비-git 이라 검사기의 touched
슬라이스가 커밋 상태에 따라 흔들리지 않는다(fixture_matrix 와 같은 hermetic 이유).

27종 목록은 fixture_matrix 의 쌍 목록에서 그대로 가져온다(두 곳에 적지 않는다):
skeleton 1 + plain 23 + API-error 3(--error-profile auto). checker_lint 는 검사기의
검사기라 BC 판정이 아니다 — 제외.

사용: python3 bc_registry_run.py <저장소 루트> <bc 이름>
exit 0 = 27종 전부 exit 0 / exit 2 = 위반 존재 / exit 1 = 재료 결손.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture_matrix import AUTO_PAIRS, PLAIN_PAIRS, S  # noqa: E402


def _project_dirs(root: Path) -> "list[Path]":
    """루트 직계에서 <project>/ 후보를 찾는다 — settings(폴더·파일)나 wsgi.py 를 가진 폴더."""
    out: "list[Path]" = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name == "application":
            continue
        if (d / "settings").exists() or (d / "settings.py").is_file() or (d / "wsgi.py").is_file():
            out.append(d)
    return out


def build_shadow(root: Path, bc: str, dest: Path) -> None:
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".git")
    shutil.copytree(root / "application" / bc, dest / "application" / bc, ignore=ignore)
    app_init: Path = root / "application" / "__init__.py"
    if app_init.is_file():
        shutil.copy2(app_init, dest / "application" / "__init__.py")
    if (root / "framework").is_dir():
        shutil.copytree(root / "framework", dest / "framework", ignore=ignore)
    for proj in _project_dirs(root):
        shutil.copytree(proj, dest / proj.name, ignore=ignore)
    if (root / "manage.py").is_file():
        shutil.copy2(root / "manage.py", dest / "manage.py")


def main(argv: "list[str]") -> int:
    if len(argv) != 2:
        print("사용: bc_registry_run.py <저장소 루트> <bc 이름>", file=sys.stderr)
        return 1
    root: Path = Path(argv[0]).resolve()
    bc: str = argv[1]
    if not (root / "application" / bc).is_dir():
        print(f"재료 결손: {root / 'application' / bc} 없음", file=sys.stderr)
        return 1

    checkers: "list[tuple[str, list[str]]]" = (
        [("check-layer-skeleton.py", [])]
        + [(script, []) for script, _ in PLAIN_PAIRS]
        + [(script, ["--error-profile", "auto"]) for script, _ in AUTO_PAIRS]
    )
    assert len(checkers) == 27, f"registry 는 27종이어야 한다 — 지금 {len(checkers)}"
    for script, _ in checkers:
        if not (S / script).is_file():
            print(f"재료 결손: {S / script} 없음", file=sys.stderr)
            return 1

    red: int = 0
    lines: "list[str]" = ["| 검사기 | exit | 판정 |", "|---|---|---|"]
    details: "list[str]" = []
    with tempfile.TemporaryDirectory() as td:
        shadow: Path = Path(td) / "shadow"
        build_shadow(root, bc, shadow)
        for script, extra in checkers:
            proc = subprocess.run(
                [sys.executable, str(S / script), str(shadow)] + extra,
                capture_output=True, text=True,
            )
            ok: bool = proc.returncode == 0
            if not ok:
                red += 1
                body: str = (proc.stdout + proc.stderr).strip()
                if body:
                    details.append(f"── {script} (exit {proc.returncode})\n{body}")
            lines.append(f"| `{script}` | {proc.returncode} | {'✓' if ok else '✗'} |")
    print(f"# registry 27종 — {root.name} · BC {bc}")
    print("\n".join(lines))
    print(f"green {27 - red} · red {red}")
    if details:
        print("\n".join(details))
    return 0 if red == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
