#!/usr/bin/env python3
"""결정적 백스톱 27종을 한 BC 에 일괄 실행 — 클린룸 리빌드 라운드의 C축(registry 판정).

검사기는 저장소 루트 모양(fixture 와 동일: application/ + <project>/ + framework/)을
받으므로, 대상 BC 하나만 담은 «그림자 사본»을 임시로 지어 실행한다 —
⑴ 이웃 BC 의 위반이 판정에 섞이지 않고 ⑵ 사본은 비-git 이라 검사기의 touched
슬라이스가 커밋 상태에 따라 흔들리지 않는다(fixture_matrix 와 같은 hermetic 이유).

27종 목록은 플러그인의 `checker_registry.py`(단일 출처 — commands 순서·auto 플래그)에서
가져온다(두 곳에 적지 않는다). checker_lint 는 검사기의 검사기라 BC 판정이 아니다 — 제외.

two-pass(2026-08-12 · 라운드 1′ H2 / 2026-08-13 · 라운드 2 H4′ 확장): 25종은 이웃 없는
그림자에 돌리고, 로스터 소비 검사기 2종 — `check-context-isolation.py`(타 BC import
분류 #12·#51)·`check-port-adapter-pairing.py`(ACL 상대의 «우리 BC» 판정 #365) — 만
이웃 BC «빈 스텁»(이름만)을 얹은 뒤 돌린다. 스텁이 skeleton 등에 가짜 골격
blocker(#488 — 15 BC × 7칸 실측)를 만들지 않게 순서로 격리한다. (#365 과탐은 라운드 2
레인 A에서 실측 — 이웃이 로스터에 없어 정당한 ACL 3폴더가 «저장소 밖 상대»로 발화.
검사기는 파일트리 기반·무결이라 수정처는 이 하네스다 — `bc_registry_smoke.py` 가 고정.)
한계(분업): 이웃 «내용»이 필요한 규칙(#505 류 — 타 BC 파일 스캔)은 이 단일-BC 그림자가
원리상 판정할 수 없다 — 그 몫은 루트 실행 게이트(registry_gate)가 진다.

사용: python3 bc_registry_run.py <저장소 루트> <bc 이름>
exit 0 = 27종 전부 exit 0 / exit 2 = 위반 존재 / exit 1 = 재료 결손.
"""
from __future__ import annotations

import ast
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

S: Path = Path(__file__).resolve().parents[2] / "dddjango" / "scripts"
sys.path.insert(0, str(S))
from checker_registry import REGISTRY  # noqa: E402
import checker_target  # noqa: E402


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


def add_neighbor_stubs(root: Path, bc: str, shadow: Path) -> int:
    """이웃 BC 를 «이름만 있는 빈 스텁»으로 그림자에 얹는다 — two-pass 둘째 판 전용.

    골격 없는 스텁은 skeleton 검사에 가짜 #488 을 만들므로(15 BC × 고정 칸 7 실측),
    반드시 1차 판 실행 «후» 에 만들고 로스터 소비 검사기(context-isolation·
    port-adapter-pairing)만 본다."""
    made: int = 0
    for d in sorted((root / "application").iterdir()):
        if not d.is_dir() or d.name.startswith((".", "__")) or d.name == bc:
            continue
        stub: Path = shadow / "application" / d.name
        if not stub.exists():
            stub.mkdir(parents=True)
            (stub / "__init__.py").write_text("", encoding="utf-8")
            made += 1
    return made


ROSTER_AWARE: "frozenset[str]" = frozenset({"check-context-isolation.py", "check-port-adapter-pairing.py"})


def main(argv: "list[str]") -> int:
    if len(argv) != 2:
        print("사용: bc_registry_run.py <저장소 루트> <bc 이름>", file=sys.stderr)
        return 1
    root: Path = Path(argv[0]).resolve()
    bc: str = argv[1]
    if not (root / "application" / bc).is_dir():
        print(f"재료 결손: {root / 'application' / bc} 없음", file=sys.stderr)
        return 1

    # F-A(2026-08-14): 그림자에는 pyproject 가 없어 checker_target 하한 게이트가 하위
    # 검사기에서 무발화한다 — 실행기가 «소스 루트» 기준으로 대신 거른다(fail-closed).
    gap: "str | None" = checker_target._interpreter_gap_reason(root)
    if gap is not None:
        print(f"사용 오류: {gap}", file=sys.stderr)
        return 1

    checkers: "list[tuple[str, list[str]]]" = [
        (script, ["--error-profile", "auto"] if auto else []) for script, auto in REGISTRY
    ]
    assert len(checkers) == 27, f"registry 는 27종이어야 한다 — 지금 {len(checkers)}"
    for script, _ in checkers:
        if not (S / script).is_file():
            print(f"재료 결손: {S / script} 없음", file=sys.stderr)
            return 1

    red: int = 0
    lines: "list[str]" = ["| 검사기 | exit | 판정 |", "|---|---|---|"]
    details: "list[str]" = []
    results: "dict[str, int]" = {}
    stubs: int = 0
    with tempfile.TemporaryDirectory() as td:
        shadow: Path = Path(td) / "shadow"
        build_shadow(root, bc, shadow)

        # F-A pre-scan: 하한 충족 인터프리터인데도 파싱 불가면 «깨진 파일»이다 —
        # 침묵 스킵(fail-open) 대신 합성 blocker 로 소리낸다(적대 리뷰: red 소거 우회 차단).
        parse_fail: "list[str]" = []
        for p in sorted(shadow.rglob("*.py")):
            try:
                ast.parse(p.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                parse_fail.append(str(p.relative_to(shadow)))
        if parse_fail:
            print(f"blocker [parse-fail] {len(parse_fail)}건 — 이 인터프리터({sys.version_info[0]}.{sys.version_info[1]})로 파싱 불가한 검사 대상:")
            for rel in parse_fail:
                print(f"  {rel}")
            return 2

        def run_one(script: str, extra: "list[str]") -> None:
            nonlocal red
            proc = subprocess.run(
                [sys.executable, str(S / script), str(shadow)] + extra,
                capture_output=True, text=True,
            )
            results[script] = proc.returncode
            if proc.returncode != 0:
                red += 1
                body: str = (proc.stdout + proc.stderr).strip()
                if body:
                    details.append(f"── {script} (exit {proc.returncode})\n{body}")

        for script, extra in checkers:
            if script not in ROSTER_AWARE:
                run_one(script, extra)
        stubs = add_neighbor_stubs(root, bc, shadow)
        for script, extra in checkers:
            if script in ROSTER_AWARE:
                run_one(script, extra)
    for script, _extra in checkers:
        code: int = results[script]
        lines.append(f"| `{script}` | {code} | {'✓' if code == 0 else '✗'} |")
    print(f"# registry 27종 — {root.name} · BC {bc} (two-pass · 이웃 스텁 {stubs})")
    print("\n".join(lines))
    print(f"green {27 - red} · red {red}")
    if details:
        print("\n".join(details))
    return 0 if red == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
