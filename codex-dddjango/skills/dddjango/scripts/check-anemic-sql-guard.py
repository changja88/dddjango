#!/usr/bin/env python3
"""dddjango 빈혈 SQL 가드 결정적 백스톱 (architecture-ddd §3.2 · architecture-db §9.5 — C형 빈혈).

비즈니스 판정(예: `stock>=qty`)을 도메인 규칙 메서드 없이 인프라 SQL 에만 둔 *C형 빈혈* 을
적출한다 — `.filter(...)`/`.exclude(...)` 의 WHERE 에 비-경합 컬럼의 단조 비교(`stock__gte=변수`
등)가 있고 `.update(...)` 로 이어지는데, 그 판정 SQL 이 속한 BC(앱) 에 `domain_layer/` 도메인
규칙 메서드가 0개인 경우.

표준(`architecture-db` §9.5·§9.6 Rule ownership · `design-architect` §API/데이터)은 "판정·불변식은
도메인 애그리거트/서비스가 소유, 인프라는 경합 가드(`version`)만"이라 박는다. 판정이 도메인 메서드로
살아있으면(예: `catalog/domain_layer/.../stock_policy.py` `can_decrement_stock` + SQL guard) 그건
*복제*(B형, DRY 위반이나 도메인이 규칙을 소유 — discipline-reviewer 의미 점검 몫)이지 빈혈이 아니다.
이 백스톱은 *도메인 규칙 메서드가 아예 없고* SQL 만이 판정하는 **C형** 만 결정적으로 막는다.

*왜 결정적 백스톱인가* — 빈혈은 의미 판정이라 reviewer 위임이 원칙이나(`check-app-container` 주석
참조), "판정 SQL + 그 BC `domain_layer` 도메인 메서드 0개" 동시 성립은 좁고 결정적이다(거짓양성 ≈0).
B형(메서드 존재)·CHECK 제약(`Q(...)` 은 `.filter().update()` 체인 아님)·경합 가드(`version`/`id`/`pk`)·
불변식 리터럴(`__gte=0`)은 다 통과한다. recall 갭(도메인 메서드를 `domain_layer` 밖에 둠)은
discipline-reviewer 의미 점검 몫. atomic conditional update 관용구의 표준 허용 여부(B형)는 이 백스톱의
범위 밖이며 표준 텍스트는 현행(인프라엔 경합 가드만)을 유지한다.

거짓양성 ≈ 0 — AND 합성:
  G1) production(`*.py`, `test`/`tests`/`migrations` 제외) 에서 AST 상 `.filter(…)`/`.exclude(…)` 가
      `.update(` 로 이어지고, 그 키워드 술어에 `<col>__(gte|gt|lte|lt)=<비리터럴>`
      (col ∉ {version, id, pk, *_id}). CHECK 제약 `Q(...)`·`version` 경합가드·리터럴 RHS(`__gte=0`)는
      구조상 매치되지 않는다(filter/exclude→update 체인의 키워드 인자만 본다).
  G2) 그 파일이 *이번 작업* 의 신규/수정분(git untracked/modified). git 아니거나 판정 불가면 스킵
      (차단 아님) — brownfield 무관 레거시 거짓양성 회피.
  G3) 판정 SQL 이 속한 BC(앱: 루트 평면 `<app>/` 또는 `application/<bc>/`) 에 `domain_layer/` 도메인
      규칙 메서드(`.py` 비-`__init__` 의 top-level `def`/`class`)가 0개. 있으면(B형) 면제.
  G1 ∧ G2 ∧ G3 → exit 2(blocker). 아니면 exit 0.

사용법: check-anemic-sql-guard.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean(또는 표준 미적용·판정불가), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {
    ".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__",
    "build", "dist", ".tox", ".mypy_cache", ".pytest_cache", ".eggs",
}
TEST_DIRS = {"test", "tests", "migrations"}

# 경합 가드·키 컬럼 — 비즈니스 판정이 아니므로 WHERE 에 두는 게 정상.
GUARD_COLS = {"version", "id", "pk"}
CMP_SUFFIXES = ("__gte", "__gt", "__lte", "__lt")

_DEF_RE = re.compile(r"^\s*(def|class)\s+\w", re.M)


def _is_judgment_predicate(kw: ast.keyword) -> bool:
    """filter/exclude 키워드가 *비즈니스 판정* 단조 비교인가(경합 가드·키·불변식 리터럴 제외)."""
    if not kw.arg:
        return False
    for suf in CMP_SUFFIXES:
        if kw.arg.endswith(suf):
            col0 = kw.arg[: -len(suf)].split("__")[0]
            if col0 in GUARD_COLS or col0.endswith("_id"):
                return False
            # 리터럴 RHS(`stock__gte=0` 같은 불변식 백스톱)는 판정이 아니다.
            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, (int, float)):
                return False
            return True
    return False


def _anemic_predicates(path: Path) -> list[str]:
    """파일에서 `.filter()/.exclude(...).update()` 체인의 판정 술어를 모은다(없으면 [])."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return []
    hits: list[str] = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "update"
        ):
            continue
        recv: ast.AST | None = node.func.value
        # `.update()` 의 receiver 체인을 거슬러 filter/exclude 술어를 검사한다.
        while recv is not None:
            if isinstance(recv, ast.Call) and isinstance(recv.func, ast.Attribute):
                if recv.func.attr in ("filter", "exclude"):
                    for kw in recv.keywords:
                        if _is_judgment_predicate(kw):
                            hits.append(f"{kw.arg} (line {recv.lineno})")
                recv = recv.func.value
            elif isinstance(recv, ast.Attribute):
                recv = recv.value
            else:
                break
    return hits


def _bc_root(path: Path, root: Path) -> Path:
    """판정 SQL 파일이 속한 BC(앱) 루트 — `application/<bc>/` 또는 루트 평면 `<app>/`."""
    parts = path.relative_to(root).parts
    if parts[0] == "application" and len(parts) >= 2:
        return root / "application" / parts[1]
    return root / parts[0]


def _bc_has_domain_method(bc: Path) -> bool:
    """BC 에 `domain_layer/` 도메인 규칙 메서드(비-__init__ .py 의 top-level def/class)가 있나."""
    dl = bc / "domain_layer"
    if not dl.is_dir():
        return False
    for p in dl.rglob("*.py"):
        if p.name == "__init__.py":
            continue
        if set(p.parts) & TEST_DIRS:
            continue
        try:
            txt = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if _DEF_RE.search(txt):
            return True
    return False


def _git_available(root: Path) -> bool:
    return (root / ".git").exists()


def _porcelain(root: Path, relpath: str) -> str | None:
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--", relpath],
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if res.returncode != 0:
        return None
    return res.stdout


def _is_new_or_modified(root: Path, file: Path) -> bool | None:
    """이번 작업이 이 파일을 새로 만들거나 수정했나. 판정 불가면 None(→ 스킵)."""
    if not _git_available(root):
        return None
    rel = file.relative_to(root).as_posix()
    out = _porcelain(root, rel)
    if out is None:
        return None
    return bool(out.strip())


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-anemic-sql-guard] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    findings: list[str] = []
    for path in root.rglob("*.py"):
        if set(path.parts) & SKIP_DIRS:
            continue
        if set(path.parts) & TEST_DIRS:
            continue
        preds = _anemic_predicates(path)
        if not preds:
            continue  # G1 미성립
        if _is_new_or_modified(root, path) is not True:
            continue  # G2: 미변경·비-git → 스킵(거짓양성 회피)
        bc = _bc_root(path, root)
        if _bc_has_domain_method(bc):
            continue  # G3 면제: 도메인 규칙 메서드 존재 = B형(복제, reviewer 위임)
        findings.append(
            f"  - {path.relative_to(root).as_posix()}  [BC={bc.name}, "
            f"domain_layer 규칙 메서드 0개]  판정 술어: {', '.join(preds)}"
        )

    if findings:
        print(
            "[check-anemic-sql-guard] BLOCKER — 비즈니스 판정이 도메인 규칙 메서드 없이 "
            "인프라 SQL 에만 있다(C형 빈혈):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: `architecture-ddd` §3.2 빈혈 차단 · `architecture-db` §9.5·§9.6 Rule ownership. "
            "판정·불변식은 도메인 애그리거트/서비스가 메서드로 소유하고 프로덕션에서 호출되어야 한다 — "
            "`.filter(...).update()` 의 WHERE 에 `stock>=qty` 류 판정만 있고 그 BC `domain_layer/` 에 "
            "규칙 메서드가 0개면 도메인이 규칙을 잃은 빈혈이다. 도메인 규칙 메서드를 `domain_layer/` 에 "
            "두고(예: `stock_policy.can_decrement_stock`) 프로덕션 경로에서 호출한 뒤, 인프라엔 경합 "
            "가드(`version`/CAS)만 둬라. 판정을 다른 BC 가 소유하면 ACL/포트로 통합한다(빈혈 방지). "
            "설계 결정이면 코드에서 방치 말고 G1 으로 반송하라."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
