#!/usr/bin/env python3
"""dddjango 메커니즘-소유권 결정적 백스톱 (P2, move ④).

좁은 **고정밀·저-recall** 게이트다. 코더가 프로덕션 DB 엔진의 트랜잭션·락·격리
*메커니즘*을 명세 승인 없이 **커스텀 백엔드로 교체**한 정확한 형태(P2 스모크에서
실제로 난 claude-3 형태)만 차단한다. 런타임 몽키패치·시그널 같은 *의미적* 회피는
**일부러 잡지 않는다** — 그건 ② 표준 텍스트(§9.5·§16.4)와 ③ discipline-reviewer
의미 체크가 담당한다. 여기서 거짓 양성을 내면 정당한 stock `OPTIONS`·PostGIS·
third-party 백엔드·기존 코드를 막으므로, **모든 조건의 AND 합성으로만** 차단한다.

AND 조건(전부 참이어야 blocker):
  1) 프로덕션(비테스트) settings 의 DATABASES ENGINE 이 stock 이 아님
     (`django.db.backends.*` / `django.contrib.gis.db.backends.*` 제외).
  2) 그 ENGINE 점경로가 **레포-로컬** 모듈로 실재(third-party/site-packages 아님).
  3) 그 백엔드 모듈에 `DatabaseWrapper` 서브클래스 + 트랜잭션/락 의미 변경 마커
     (`_start_transaction_under_autocommit` / `BEGIN IMMEDIATE` / `BEGIN EXCLUSIVE`
      / `isolation_level` 조작).
  4) (git 레포면) 그 백엔드 파일이 이번 변경에서 새로 추가/수정됨 — 기존에
     커밋된 정당한 커스텀 백엔드(수정 모드)는 존중. git 아니면 이 가드는 건너뛴다.

사용법: check-mechanism-ownership.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean, 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from migration_scope import (
    is_migration_owned_path,
    iter_non_migration_files,
    validate_migration_scope,
)

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

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}


def _find_settings_files(root: Path) -> list[Path]:
    """프로덕션 settings 후보를 찾는다(test 전용 모듈·venv 제외)."""
    out: list[Path] = []
    for path in iter_non_migration_files(root, name_pattern="*.py"):
        parts = set(path.parts)
        if parts & SKIP_DIRS:
            continue
        name = path.name
        # settings.py 또는 settings/ 패키지 안의 모듈만.
        if name != "settings.py" and path.parent.name != "settings":
            continue
        # 테스트 전용 settings 는 프로덕션 배선이 아니다 → 제외.
        if "test" in name.lower():
            continue
        out.append(path)
    return out


def _candidate_backend_files(root: Path, engine: str) -> list[Path]:
    """ENGINE 점경로를 레포-로컬 파일 후보로 변환한다."""
    rel = engine.replace(".", os.sep)
    return [
        root / f"{rel}.py",
        root / rel / "__init__.py",
        root / rel / "base.py",
    ]


def _is_new_or_modified(root: Path, file_path: Path) -> bool:
    """git 레포면 이번 변경에서 추가/수정됐는지. git 아니면 True(가드 통과)."""
    if not (root / ".git").exists():
        return True
    try:
        rel = file_path.relative_to(root)
    except ValueError:
        return True
    try:
        # 추적되지 않으면(신규) error-unmatch 가 non-zero → 신규로 간주.
        tracked = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--error-unmatch", str(rel)],
            capture_output=True,
        )
        if tracked.returncode != 0:
            return True  # 신규 파일.
        # 추적 중이면 HEAD 대비 변경됐는지.
        changed = subprocess.run(
            ["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", str(rel)],
        )
        return changed.returncode != 0
    except (OSError, subprocess.SubprocessError):
        return True  # git 판단 불가 시 안전하게 가드 통과(나머지 AND 가 좁힘).


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-mechanism-ownership] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1
    if not validate_migration_scope(root, "check-mechanism-ownership"):
        return 1

    findings: list[str] = []
    for settings_file in _find_settings_files(root):
        try:
            text = settings_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for engine in ENGINE_RE.findall(text):
            # 조건 1: stock 엔진 제외.
            if engine.startswith(STOCK_ENGINE_PREFIXES):
                continue
            if "." not in engine:
                continue
            # 조건 2: 레포-로컬 백엔드 모듈 실재.
            backend_files = [
                p
                for p in _candidate_backend_files(root, engine)
                if not is_migration_owned_path(root, p) and p.is_file()
            ]
            if not backend_files:
                continue  # third-party/미실재 → 통과.
            # 조건 3: DatabaseWrapper 서브클래스 + 트랜잭션/락 의미 마커.
            for bf in backend_files:
                body = bf.read_text(encoding="utf-8", errors="replace")
                if "class DatabaseWrapper" not in body:
                    continue
                if not any(m in body for m in SEMANTIC_MARKERS):
                    continue
                # 조건 4: 이번 변경에서 추가/수정.
                if not _is_new_or_modified(root, bf):
                    continue
                findings.append(
                    f"  - {settings_file.relative_to(root)}: ENGINE='{engine}' → "
                    f"{bf.relative_to(root)} (DatabaseWrapper 서브클래스가 트랜잭션/락 의미 변경)"
                )

    if findings:
        print(
            "[check-mechanism-ownership] BLOCKER — 프로덕션 DB 엔진의 트랜잭션·락·격리 "
            "메커니즘이 커스텀 백엔드로 교체됨(명세 승인 없이 = 메커니즘-소유권 위반):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: implementation-django §16.4 · architecture-db §9.5. "
            "필요한 연결 튜닝은 stock OPTIONS(transaction_mode[5.1+]·timeout·안전 PRAGMA)로만. "
            "설계로 반송하라(설계가 명시 승인한 메커니즘이면 명세에 그 결정이 있어야 한다)."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
