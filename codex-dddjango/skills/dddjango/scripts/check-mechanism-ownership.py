#!/usr/bin/env python3
"""dddjango 메커니즘-소유권 검사기 — DB 메커니즘 교체 + migrations 규율의 결정적 백스톱.

두 슬라이스를 강제한다.

⑴ 현행 관할 — DB 엔진 메커니즘 교체 (P2, move ④ · 고정밀 AND 게이트, 무변):
  코더가 프로덕션 DB 엔진의 트랜잭션·락·격리 *메커니즘*을 명세 승인 없이
  커스텀 백엔드로 교체한 정확한 형태만 차단한다. AND 조건(전부 참이어야 blocker):
    1) 프로덕션(비테스트) settings 의 DATABASES ENGINE 이 stock 이 아님.
    2) 그 ENGINE 점경로가 레포-로컬 모듈로 실재.
    3) 그 모듈에 DatabaseWrapper 서브클래스 + 트랜잭션/락 의미 변경 마커.
    4) (git 레포면) 이번 변경에서 추가/수정됨 — git 아니면 가드 통과(fail-closed).

⑵ 트리 개정 명세 몫 — migrations 규율 4규칙 (트리 80·81행 · 조각 ⓑ):
  #336 마이그레이션은 `django_<bounded_context>/migrations/` 에 산다 — 중앙(BC 밖)
       마이그레이션 폴더 금지. BC «안» 오배치는 #325(check-db-table) 소유라 여기서
       중복으로 내지 않는다.
  #337 파일 이름은 django 가 매긴 번호 꼴(`0001_initial.py`)이다 — 사람이 짓지 않는다.
  #338 마이그레이션 파일 안에서 도메인 모듈(`domain_layer`)을 import 하지 않는다.
  #593 `migrations/` 안은 사람이 직접 손대지 않는다 — 도구 산출물 모양의 허용 목록
       (Migration 클래스 하나 · 대입은 initial/dependencies/operations/replaces 넷 ·
       operations 원소는 `migrations.*` 호출, RunPython/RunSQL 제외) 밖은 전부 위반.
       주어는 «사람»이라 도구가 만들고 지우는 변경은 손편집이 아니다 — 저장소 import
       는 stdlib·django 를 유보하고 저장소 어휘만 잡는다(#326 과 같은 판).

가드 계약 (명세 조각 ⓐ):
  - 대상 0건 가드(#74): 채택 신호는 있는데 settings 도 migrations 도 0건이면 exit 2.

사용법: check-mechanism-ownership.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).

그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
  alias 대장(`ontology/wiring/aliases.ttl`)이 소유한다. 조인 확정: 없음(대장 미등재 — T3 이월).
  미확정 #N 은 T3 이관에서 해소한다(현행 조인 3종 — 판단표
  `workspace/design/2026-08-20-ontology-t2-2-alias-ledger.md` §2·§5).
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys

import checker_target
from findings import Findings, emit_all, zero_target_guard
from pathlib import Path

try:
    import standard_tree as tree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango"}
DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")
NEW_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}

STOCK_ENGINE_PREFIXES = (
    "django.db.backends.",
    "django.contrib.gis.db.backends.",
)
# 트랜잭션·락·격리 '의미'를 바꾸는 마커(안전 PRAGMA 만으로는 매치 안 됨).
SEMANTIC_MARKERS = (
    "_start_transaction_under_autocommit",
    "BEGIN IMMEDIATE",
    "BEGIN EXCLUSIVE",
    "isolation_level",
)
ENGINE_RE = re.compile(r"""ENGINE['"]?\s*[:=]\s*['"]([^'"]+)['"]""")

MIGRATION_NAME_RE = re.compile(r"^\d{4}_\w+\.py$")
# Migration 클래스 본문에서 도구가 쓰는 대입 이름 넷 — 그 밖은 손편집 신호(#593).
ALLOWED_MIGRATION_ASSIGNS = {"initial", "dependencies", "operations", "replaces"}
BANNED_OPERATIONS = {"RunPython", "RunSQL"}
# 저장소 내부 어휘 — 이 마디가 import 경로에 보이면 저장소 코드다(#326 과 같은 도출).
REPO_VOCAB = (
    {c.name.rstrip("/") for c in tree.children(tree.bc_root())}
    | {"application", "framework"}
)


def _has_adoption_signal(bc_dir: Path) -> bool:
    """채택 신호원 둘(#78) — check-layer-skeleton 과 같은 판."""
    has_layer = any((bc_dir / n).is_dir() for n in NEW_LAYERS)
    has_marker = any((bc_dir / m).is_file() for m in DJANGO_APP_MARKERS) or any(
        p.is_dir() and p.name.startswith("django_") for p in bc_dir.iterdir()
    )
    return has_layer or has_marker


def _adopted(target: Path) -> bool:
    for c in target.rglob("application"):
        if not c.is_dir() or set(c.parts) & SKIP_DIRS:
            continue
        for bc in sorted(c.iterdir()):
            if bc.is_dir() and not bc.name.startswith(".") and _has_adoption_signal(bc):
                return True
    return False


# ── 슬라이스 ⑴ — DB 엔진 메커니즘 교체 (현행 관할 · 무변) ──────────────────

def _find_settings_files(root: Path) -> list[Path]:
    """프로덕션 settings 후보(test 전용 모듈·venv 제외)."""
    out: list[Path] = []
    for path in root.rglob("*.py"):
        if set(path.parts) & SKIP_DIRS:
            continue
        if any(seg.startswith(".") for seg in path.relative_to(root).parts[:-1]):
            continue  # 숨김 디렉터리 = 도구·하네스 영역(F-C 2026-08-14)
        if path.name != "settings.py" and path.parent.name != "settings":
            continue
        if "test" in path.name.lower():
            continue
        out.append(path)
    return out


def _candidate_backend_files(root: Path, engine: str) -> list[Path]:
    rel = engine.replace(".", os.sep)
    return [root / f"{rel}.py", root / rel / "__init__.py", root / rel / "base.py"]


def _is_new_or_modified(root: Path, file_path: Path) -> bool:
    """git 레포면 이번 변경에서 추가/수정됐는지. git 아니면 True(가드 통과 — fail-closed)."""
    if not (root / ".git").exists():
        return True
    try:
        rel = file_path.relative_to(root)
    except ValueError:
        return True
    try:
        tracked = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--error-unmatch", str(rel)],
            capture_output=True,
        )
        if tracked.returncode != 0:
            return True  # 신규 파일.
        changed = subprocess.run(
            ["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", str(rel)],
        )
        return changed.returncode != 0
    except (OSError, subprocess.SubprocessError):
        return True


def _check_engine_swap(root: Path, settings_files: list[Path], out: Findings) -> None:
    for settings_file in settings_files:
        try:
            text = settings_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for engine in ENGINE_RE.findall(text):
            if engine.startswith(STOCK_ENGINE_PREFIXES) or "." not in engine:
                continue
            backend_files = [p for p in _candidate_backend_files(root, engine) if p.is_file()]
            for bf in backend_files:
                body = bf.read_text(encoding="utf-8", errors="replace")
                if "class DatabaseWrapper" not in body:
                    continue
                if not any(m in body for m in SEMANTIC_MARKERS):
                    continue
                if not _is_new_or_modified(root, bf):
                    continue
                out.add(
                    "메커니즘", settings_file.relative_to(root),
                    f"ENGINE='{engine}' → {bf.relative_to(root)} — DatabaseWrapper 서브클래스가 "
                    "트랜잭션/락/격리 의미를 승인 없이 교체했다(stock OPTIONS 로만 튜닝한다)",
                )


# ── 슬라이스 ⑵ — migrations 규율 #336 · #337 · #338 · #593 ─────────────────

def _find_migration_dirs(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in root.rglob("migrations"):
        if p.is_dir() and not (set(p.parts) & SKIP_DIRS):
            out.append(p)
    return sorted(out)


def _classify_migration_dir(rel_parts: tuple[str, ...]) -> str:
    """'standard'(django_* 안) · 'bc'(BC 안 오배치 — #325 소유라 스킵) · 'central'(#336)."""
    if any(seg.startswith("django_") for seg in rel_parts[:-1]):
        return "standard"
    if "application" in rel_parts[:-1]:
        return "bc"
    return "central"


def _import_paths(node: ast.stmt) -> list[str]:
    if isinstance(node, ast.Import):
        return [a.name for a in node.names]
    if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
        return [node.module]
    return []


def _is_repo_import(path_str: str) -> bool:
    """저장소 내부 어휘를 가리키는 import 인가 — stdlib·django·서드파티는 판정 유보."""
    parts = path_str.split(".")
    if parts[0] in ("django", "__future__"):
        return False
    return any(p in REPO_VOCAB for p in parts) or any(p.startswith("django_") for p in parts)


def _check_migration_file(f: Path, rel: Path, out: Findings) -> None:
    """#337(이름) · #338(도메인 import) · #593(도구 산출물 모양 허용 목록)."""
    if f.name == "__init__.py":
        try:
            mod = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            return
        stmts = [s for s in mod.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
        if stmts:
            out.add("#593", rel, "`migrations/__init__.py` 는 도구가 빈 파일로 만든다 — 내용을 손으로 넣지 않는다")
        return

    if not MIGRATION_NAME_RE.match(f.name):
        out.add("#337", rel, "마이그레이션 파일 이름은 django 가 매긴 번호 꼴(`0001_initial.py`)이다 — 사람이 짓지 않는다")

    try:
        mod = ast.parse(f.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        out.add("분석", rel, "마이그레이션 파일을 파싱하지 못했다")
        return

    migration_classes: list[ast.ClassDef] = []
    body = list(mod.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        body = body[1:]  # 생성 주석/docstring 은 모양으로 세지 않는다
    for node in body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for p in _import_paths(node):
                if not _is_repo_import(p):
                    continue
                rule = "#338" if "domain_layer" in p.split(".") else "#593"
                what = "도메인 모듈" if rule == "#338" else "저장소 모듈"
                out.add(rule, rel, f"`{p}` import — 마이그레이션 파일 안에서 {what}을 import 하지 않는다(도구 산출물이 아니다)")
        elif isinstance(node, ast.ClassDef):
            migration_classes.append(node)
        else:
            out.add("#593", rel, f"마이그레이션 최상단에는 import 와 Migration 클래스만 온다 — `{ast.dump(node)[:40]}…` 는 손편집 신호다")

    if len(migration_classes) != 1 or migration_classes[0].name != "Migration":
        out.add("#593", rel, "마이그레이션 파일에는 `Migration` 클래스가 정확히 하나다 — 필요한 변경은 모델을 고쳐 다시 생성한다")
        return
    cls = migration_classes[0]
    if cls.decorator_list:
        out.add("#593", rel, "`Migration` 클래스에 데코레이터가 있다 — 도구는 데코레이터를 쓰지 않는다")
    for stmt in cls.body:
        if isinstance(stmt, ast.Assign):
            names = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
            if not names or any(n not in ALLOWED_MIGRATION_ASSIGNS for n in names):
                bad = ", ".join(names) or "비-이름 타깃"
                out.add("#593", rel, f"`Migration` 대입은 initial·dependencies·operations·replaces 넷뿐이다 — `{bad}`")
                continue
            if "operations" in names:
                _check_operations(stmt.value, rel, out)
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            continue  # docstring
        else:
            out.add("#593", rel, "`Migration` 본문에 대입 밖 문장(함수·분기·루프)이 있다 — 손편집 신호다")


def _check_operations(value: ast.expr, rel: Path, out: Findings) -> None:
    """operations 원소는 전부 `migrations.*` 호출 — RunPython/RunSQL 은 손편집이라 위반."""
    if not isinstance(value, (ast.List, ast.Tuple)):
        out.add("#593", rel, "`operations` 는 리스트 리터럴이다 — 계산식은 손편집 신호다")
        return
    for el in value.elts:
        if not isinstance(el, ast.Call):
            out.add("#593", rel, "`operations` 원소는 `migrations.*` 호출이다")
            continue
        func = el.func
        attr = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        owner = getattr(getattr(func, "value", None), "id", "")
        if attr in BANNED_OPERATIONS:
            out.add("#593", rel, f"`migrations.{attr}` 은 손으로 쓰는 연산이다 — 필요한 변경은 모델을 고쳐 다시 생성한다")
        elif owner != "migrations":
            out.add("#593", rel, f"`operations` 원소는 `migrations.*` 호출이어야 한다 — `{attr}`")


def _check_migrations(root: Path, mig_dirs: list[Path], out: Findings) -> None:
    for d in mig_dirs:
        rel_dir = d.relative_to(root)
        kind = _classify_migration_dir(rel_dir.parts)
        if kind == "central":
            out.add("#336", rel_dir, "마이그레이션은 `driven_layer/django_<bounded_context>/migrations/` 에 산다 — 중앙 폴더를 두지 않는다")
            continue
        if kind == "bc":
            continue  # BC 안 오배치는 #325(check-db-table) 소유 — 중복 진단 금지
        for f in sorted(d.glob("*.py")):
            _check_migration_file(f, f.relative_to(root), out)


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(f"사용법: {Path(sys.argv[0]).name} [TARGET_DIR]", file=sys.stderr)
        return 1
    target = Path(argv[0]).resolve() if argv else Path.cwd()
    bad_target_reason = checker_target.bc_shaped_target_reason(target)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {target}", file=sys.stderr)
        return 1

    adopted = _adopted(target)
    settings_files = _find_settings_files(target)
    mig_dirs = _find_migration_dirs(target)

    # 대상 0건 가드(#74) — 채택 신호는 있는데 settings 도 migrations 도 안 보이면
    # 경로 계약이 어긋난 것이다(조용한 무동작 금지).
    if adopted and not settings_files and not mig_dirs:
        guard = zero_target_guard(
            "blocker: 채택 신호는 있는데 settings·migrations 대상이 0건이다 — 조용한 무동작을 금지한다(#74)"
        )
        emit_all(guard, printer=print, indent="")
        return 2
    if not adopted and not settings_files and not mig_dirs:
        print("표준 레이아웃 미채택 — 검사 대상 없음 (clean)")
        return 0

    findings = Findings(defer=True)
    _check_engine_swap(target, settings_files, findings)
    _check_migrations(target, mig_dirs, findings)

    if findings:
        print(f"blocker {len(findings)}건 — 메커니즘 소유권·migrations 규율 위반")
        emit_all(findings, printer=print, indent="  ")
        return 2
    print(f"clean — settings {len(settings_files)}개 · migrations 폴더 {len(mig_dirs)}개 규율 일치 (트리 80·81행 · standard_tree {tree.SOURCE_SHA})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
