#!/usr/bin/env python3
"""dddjango 인프라 예외 검사기 — 합성 금지(ACL-EX2) + 전수 명시 매핑(#129)의 결정적 백스톱.

두 슬라이스를 강제한다. 대상은 driven 쪽(`driven_layer/`)이다.

⑴ 현행 관할 — 인프라 예외 *합성* (ACL-EX2 · 고정밀 AND 게이트, 무변):
  driven 경계가 *계산된* transient/경합을 신호하려고 raw 인프라 DB 예외
  (`OperationalError`/`DatabaseError`/`IntegrityError`)를 `from` 없이 새로
  생성(Call)해 raise 한 형태만 차단한다. AND 조건(전부 참이어야 blocker):
    1) 파일이 driven 층 안이다(`driven_layer`).
    2) raise 의 예외가 Call 이고 생성 타입이 위 셋 — 재던지기·bare 클래스 제외.
    3) `raise ... from X` 의 cause 부재 — `from` 보존 재던지기는 제외.
    4) (git 레포면) 이번 변경에서 추가/수정됨 — git 아니면 가드 통과(fail-closed).

⑵ 트리 개정 명세 몫 — #129 (D27):
  예외 번역은 «알려진 구체 예외의 전수 명시 매핑»으로 한다 — driven 층에서
  `except Exception`/`except BaseException`/bare `except:` 를 잡아 놓고 그 안에서
  «새 예외를 생성해» raise 하면(catch-all 번역) 위반이다. 알 수 없는 실패를
  번역하는 것은 매핑이 아니라 은폐다. 단순 정리 후 재던지기(`raise`/`raise e`)는
  번역이 아니라 잡지 않는다.

가드 계약 (명세 조각 ⓐ):
  - 대상 0건 가드(#74): 채택 신호는 있는데 driven 쪽 파일이 0건이면 exit 2.

사용법: check-synthetic-infra-exc.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).

그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
  alias 대장(`ontology/wiring/aliases.ttl`)이 소유한다. 조인 확정: rule#74 → djr:R-3229.
  미확정 #N 은 T3 이관에서 해소한다(대장 28종 — T3 게이트 조항 처분 2026-08-22 ·
  판단표 v2 + `workspace/eval/t3/memos/`).
"""
from __future__ import annotations

import ast
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
TEST_DIR_NAMES = {"test", "tests"}
DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")
NEW_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}

DRIVEN = "driven_layer"
DRIVEN_DIRS = (DRIVEN,)

TARGET_EXC = {"OperationalError", "DatabaseError", "IntegrityError"}
CATCH_ALL = {"Exception", "BaseException"}


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


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _find_driven_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in root.rglob("*.py"):
        parts = set(path.parts)
        if parts & SKIP_DIRS:
            continue
        if parts & TEST_DIR_NAMES or path.name.startswith("test_") or path.name == "conftest.py":
            continue
        if not (parts & set(DRIVEN_DIRS)):
            continue
        out.append(path)
    return sorted(out)


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


def _synthesis_raises(mod: ast.AST) -> list[tuple[int, str]]:
    """`from` 없이 인프라 DB 예외를 *생성*(Call)해 raise 하는 지점 — (lineno, exc_name)."""
    out: list[tuple[int, str]] = []
    for node in ast.walk(mod):
        if not isinstance(node, ast.Raise):
            continue
        if node.cause is not None:          # `raise ... from X` → 원본 보존(면제).
            continue
        exc = node.exc
        if not isinstance(exc, ast.Call):   # 변수 재던지기·bare 클래스 → 정당 전파(면제).
            continue
        nm = _call_name(exc.func)
        if nm in TARGET_EXC:
            out.append((node.lineno, nm))
    return out


def _is_catch_all(handler: ast.ExceptHandler) -> bool:
    t = handler.type
    if t is None:
        return True  # bare `except:`
    if isinstance(t, ast.Tuple):
        return any(_call_name(el) in CATCH_ALL for el in t.elts)
    return _call_name(t) in CATCH_ALL


def _catch_all_translations(mod: ast.AST) -> list[int]:
    """#129 — catch-all 로 잡아 «새 예외를 생성해» raise 하는 지점(lineno들)."""
    out: list[int] = []
    for node in ast.walk(mod):
        if not isinstance(node, ast.ExceptHandler) or not _is_catch_all(node):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Raise) and isinstance(sub.exc, ast.Call):
                out.append(sub.lineno)
    return out


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

    files = _find_driven_files(target)

    # 대상 0건 가드(#74) — 채택 신호는 있는데 driven 쪽 파일이 0건이면 경로 계약이 어긋난 것.
    if not files:
        if _adopted(target):
            guard = zero_target_guard(
                "blocker: 채택 신호는 있는데 driven 층 파일이 0건이다 — 조용한 무동작을 금지한다(#74)"
            )
            emit_all(guard, printer=print, indent="")
            return 2
        print("표준 레이아웃 미채택 — 검사 대상 없음 (clean)")
        return 0

    findings = Findings(defer=True)
    for f in files:
        try:
            mod = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError):
            continue
        rel = f.relative_to(target)
        hits = _synthesis_raises(mod)
        if hits and _is_new_or_modified(target, f):
            for lineno, exc_name in hits:
                findings.add("합성", f"{rel}:{lineno}", f"`raise {exc_name}(...)` — `from` 없이 raw 인프라 예외를 합성했다(계산된 실패는 같은 BC 의 concrete 예외로 정규화한다)")
        for lineno in _catch_all_translations(mod):
            findings.add("#129", f"{rel}:{lineno}", f"catch-all(`except Exception`/bare) 안에서 새 예외를 생성해 raise — 예외 번역은 알려진 구체 예외의 전수 명시 매핑으로 한다")

    if findings:
        print(f"blocker {len(findings)}건 — driven 층 예외 규율 위반")
        emit_all(findings, printer=print, indent="  ")
        return 2
    print(f"clean — driven 층 파일 {len(files)}개 규율 일치 (standard_tree {tree.SOURCE_SHA})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
