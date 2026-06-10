#!/usr/bin/env python3
"""dddjango 컨텍스트 격리 결정적 백스톱 (SD-7 — 컨텍스트 간 통신).

`check-layer-skeleton.py`(구조 골격)의 *의존 방향* 짝이다. ACL/OHS 경로 *밖*에서 한 바운디드
컨텍스트(BC)가 다른 BC 의 `domain_layer`/`infra_layer` 를 직접 import 하는 것만 차단한다
(architecture-ddd §2.5·§3.2(3): 컨텍스트 간 접근은 ACL 또는 `published_service`(OHS)로만 —
다른 컨텍스트의 내부 계층을 직접 import 하지 않는다).

*왜 결정적 백스톱인가* — cross-context import 는 같은 BC 면 통과라 폴더-존재만 보는
`check-layer-skeleton.py` 가 못 잡고, 컴파일·테스트도 통과한다(green). discipline-reviewer
의미 게이트 한 점에만 의존하면 LLM 이 프로즈 규칙을 회피하는 표면이 된다 — 이 스크립트가
그 절반을 결정적으로 메운다(고정밀·저-recall, 거짓 양성 ≈0).

**ACL 면제(미스캘리브 차단)** — `infra_layer/acl/` 의 미이주 ACL 이 업스트림(타 BC) 모델·예외를
import·번역하는 건 표준 §2(houserules `final.md:128`/`:141`: "OHS 미이주·행잠금 불가피 시 ACL로
명시 — 구현(업스트림 모델·예외 번역)은 `infra_layer/acl/` 에 가둔다") **명시 허용**이라 차단하지
않는다. 진짜 위반은 ACL *밖*(도메인/응용/presentation)이 타 BC 내부를 직접 import(예: 예외
번역이 ACL 에 안 갇혀 presentation·application 으로 누수)다. ACL 자신이 OHS 미경유(OHS 존재
시)·도메인 누수(포트 ABC 미준수)인지는 의미 변종이라 discipline-reviewer 의미 체크 몫이다.
[근거: smoke4-claude(catalog 결합이 ACL 격리 → PASS) ↔ p1a-v3-claude(catalog 예외가
presentation·application 으로 누수 → FAIL)를 결정적으로 가르는 축.]

거짓 양성 회피 — AND 합성으로만 차단:
  1) 프로젝트가 표준 레이아웃(`application/` 컨테이너)을 쓴다. 없으면 기존 확립 규약(§1.1)이라
     적용 대상 아님 → exit 0.
  2) `application/<bc>/` 하위 프로덕션 파일(test 제외)이 `from application.<other>.domain_layer`
     또는 `…infra_layer` 를 import 하고 `<other>` 가 자기 BC 가 아니다.
  3) 그 파일이 `infra_layer/acl/` 가 아니다(ACL 면제 — 표준 §2 허용).
  4) (git 레포면) 그 파일이 이번 변경에서 새로 추가/수정됨 — 기존 커밋 코드는 존중(brownfield).
  `application_layer` 직접 import 는 보수적으로 불-차단(루브릭 SD-7=domain/infra; 거짓양성↓) —
  의미 레인 몫. presentation·application 이 타 BC 의 *예외*(domain_layer 하위)를 직접 import 하는
  건 (2)로 포착된다.

사용법: check-context-isolation.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean(또는 표준 레이아웃 미적용), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
TEST_DIR_NAMES = {"test", "tests"}

# 타 BC 내부 계층 직접 import. domain/infra 만(루브릭 SD-7) — application_layer 는 의미 레인.
IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+application\.([A-Za-z_]\w*)\.(?:domain_layer|infra_layer)\b"
)


def _has_application_container(root: Path) -> bool:
    """표준 앱 컨테이너(`application/`)가 있나 — 없으면 기존 규약이라 적용 대상 아님."""
    for path in root.rglob("application"):
        if path.is_dir() and not (set(path.parts) & SKIP_DIRS):
            return True
    return False


def _own_bc(parts: tuple[str, ...]) -> str | None:
    """`application/<bc>/...` 의 <bc>."""
    if "application" in parts:
        i = parts.index("application")
        if i + 1 < len(parts):
            return parts[i + 1]
    return None


def _prod_py_files(root: Path) -> list[Path]:
    """application/ 하위 프로덕션 .py — test·ACL 제외(venv 제외)."""
    out: list[Path] = []
    for path in root.rglob("*.py"):
        parts = path.parts
        if set(parts) & SKIP_DIRS:
            continue
        if "application" not in parts:
            continue
        if set(parts) & TEST_DIR_NAMES or path.name.startswith("test_") or path.name == "conftest.py":
            continue
        if "infra_layer" in parts and "acl" in parts:  # ACL 면제(표준 §2 허용)
            continue
        out.append(path)
    return out


def _is_new_or_modified(root: Path, file_path: Path) -> bool:
    """git 레포면 이번 변경(추가/수정)인지. git 아니면 True(가드 통과)."""
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
        changed = subprocess.run(["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", str(rel)])
        return changed.returncode != 0
    except (OSError, subprocess.SubprocessError):
        return True  # git 판단 불가 → 안전하게 가드 통과(나머지 AND 가 좁힌다).


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-context-isolation] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1
    if not _has_application_container(root):
        return 0  # 표준 레이아웃(`application/`) 미적용 → 해당 없음.

    findings: list[str] = []
    for f in _prod_py_files(root):
        if not _is_new_or_modified(root, f):
            continue
        own = _own_bc(f.parts)
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for n, ln in enumerate(lines, 1):
            m = IMPORT_RE.match(ln)
            if m and m.group(1) != own:  # 타 BC 의 내부 계층 직접 import
                findings.append(f"  - {f.relative_to(root)}:{n}  {ln.strip()}")

    if findings:
        print(
            "[check-context-isolation] BLOCKER — ACL 밖(도메인/응용/presentation)에서 타 BC 의 "
            "domain_layer/infra_layer 를 직접 import 함(컨텍스트 간 결합 누수):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: architecture-ddd §2.5·§3.2(3)·discipline-houserules §2. 컨텍스트 간 접근은 "
            "ACL 또는 published_service(OHS)로만 한다 — 다른 BC 의 내부 계층(예외 포함)을 직접 "
            "import 하지 않는다. ACL 이 업스트림 모델·예외를 번역해 격리하거나(infra_layer/acl/), "
            "OHS 를 경유하라. 접을 실질 사유가 있으면 코드에서 흘리지 말고 설계(G1)로 반송하라."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
