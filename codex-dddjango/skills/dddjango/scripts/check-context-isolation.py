#!/usr/bin/env python3
"""dddjango 컨텍스트 격리 결정적 백스톱 (SD-7 — 컨텍스트 간 통신).

`check-layer-skeleton.py`(구조 골격)의 *의존 방향* 짝이다. 세 슬라이스를 잡는다:

  S1  cross-BC 내부 결합 — ACL/OHS 경로 *밖*에서 한 바운디드 컨텍스트(BC)가 다른 BC 의
      `domain_layer`/`infra_layer` 를 직접 import 하는 것(architecture-ddd §2.5·§3.2(3):
      컨텍스트 간 접근은 ACL 또는 `published_service`(OHS)로만 — 다른 컨텍스트의 내부
      계층을 직접 import 하지 않는다).
  S2  OHS contract 무의존 위반 — `published_service/*/contract/` 모듈이 (자기 BC 포함
      어느 BC 든) `domain_layer`/`application_layer`/`infra_layer` 를 import 하는 것
      (houserules `references/final.md` §2 OHS 내부 구조: contract 는 표준 라이브러리·
      같은 서비스 contract 만 — 소비 BC 의 계약 import 가 무거운 그래프(Django 앱 로딩)를
      끌고 오지 않게 하는 격리이자 도메인 enum 노출 차단).
  S3  published 계약 관통 — 자기 BC 의 `domain_layer`/`application_layer`/`infra_layer`
      프로덕션 파일이 *자기* BC 의 `published_service` 를 import 하는 것(houserules §2
      OHS 시그니처 계약: published 계약 타입을 application_layer 안으로 관통시키지 않는다
      — 응용은 domain 에만 의존, OHS 가 필드 단위로 언랩·재조립한다. *타* BC 의
      published_service 소비는 표준 경로라 대상이 아니고, presentation 의 자기 published
      import 도 대상 밖이다. `infra_layer/acl/` 도 3계층이므로 자기 published 역-import 는
      S3 대상이다 — ACL 면제는 S1(업스트림 번역) 한정).

*왜 결정적 백스톱인가* — 세 슬라이스 모두 **AST import 노드** 직격의 FP≈0 직접형이고
(`ast.parse` — 문자열·주석 안의 import 유사 텍스트에 오발화하지 않는다; `import x`·
`from x import y`·콤마 다중·별칭 전 형태, 함수 내부 지연 import 포함), 어느 것도 컴파일·
테스트를 깨지 않는다(green). discipline-reviewer 의미 게이트 한 점에만 의존하면 LLM 이
프로즈 규칙을 회피하는 표면이 된다 — 이 스크립트가 직접형을 결정적으로 메우고, 의미 변종
(변수 우회·간접 재수출·상대 import(`from ..domain_layer import x`)·문자열 동적 import)은
reviewer 몫이다(고정밀·저-recall, 거짓 양성 ≈0). 파싱 불가 파일은 fail-open(스킵)한다.

**ACL 면제(미스캘리브 차단)** — `infra_layer/acl/`(인접 경로 한정 — `repository/acl/` 류
은닉 배치는 면제 아님) 의 미이주 ACL 이 업스트림(타 BC) 모델·예외를 import·번역하는 건
표준 §2(houserules `references/final.md` §2 컨텍스트 간 통신: "OHS 미이주·행잠금 불가피 시
ACL로 명시 — 구현(업스트림 모델·예외 번역)은 `infra_layer/acl/` 에 가둔다") **명시 허용**이라
차단하지 않는다. 진짜 위반은 ACL *밖*(도메인/응용/presentation)이 타 BC 내부를 직접
import(예: 예외 번역이 ACL 에 안 갇혀 presentation·application 으로 누수)다. ACL 자신이
OHS 미경유(OHS 존재 시)·도메인 누수(포트 ABC 미준수)인지는 의미 변종이라 discipline-reviewer
의미 체크 몫이다. [근거: smoke4-claude(catalog 결합이 ACL 격리 → PASS) ↔ p1a-v3-claude
(catalog 예외가 presentation·application 으로 누수 → FAIL)를 결정적으로 가르는 축.]

거짓 양성 회피 — AND 합성으로만 차단:
  1) 프로젝트가 표준 레이아웃(`application/` 컨테이너)을 쓴다. 없으면 기존 확립 규약(§1.1)이라
     적용 대상 아님 → exit 0. **경로 판정은 전부 TARGET_DIR 기준 상대 경로다** — 체크아웃
     조상 디렉터리명(`…/application/…`·`…/venv/…` 등)에 오염되지 않는다(TARGET_DIR 는
     프로젝트 루트를 전제한다 — `application/` 컨테이너 자체를 넘기면 대상 없음 exit 0).
  2) `application/<bc>/` 하위 프로덕션 파일(test 디렉터리·`test_*.py`·`conftest.py` 제외 —
     프로덕션 파일명에 `test_` 접두를 쓰지 않는 표준 명명을 전제한다)이 슬라이스 패턴에
     걸린다. 컨테이너 직하 비-BC 파일(`application/glue.py`)의 BC 내부 import 는 보수적으로
     S1 로 본다(BC 밖에서의 내부 접근).
  3) (git 레포면) 그 파일이 이번 변경에서 새로 추가/수정됨 — 기존 커밋 코드는 존중(brownfield).
     구 read/write 평면 OHS·이주 호환 심은 §2 이주 조문상 허용이라 어느 슬라이스에도 안 걸린다.
  `application_layer` 의 cross-BC 직접 import 는 보수적으로 불-차단(루브릭 SD-7=domain/infra;
  거짓양성↓) — 의미 레인 몫. presentation·application 이 타 BC 의 *예외*(domain_layer 하위)를
  직접 import 하는 건 S1 로 포착된다.

사용법: check-context-isolation.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리 — 프로젝트 루트)
종료코드: 0=clean(또는 표준 레이아웃 미적용), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

from migration_scope import (
    is_migration_owned_path,
    iter_non_migration_files,
    validate_migration_scope,
)
from typing import Iterator

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
TEST_DIR_NAMES = {"test", "tests"}
LAYER_DIR_NAMES = {"domain_layer", "application_layer", "infra_layer"}

# S1: 타 BC 내부 계층. domain/infra 만(루브릭 SD-7) — application_layer 는 의미 레인.
CROSS_BC_RE = re.compile(r"^application\.([A-Za-z_]\w*)\.(?:domain_layer|infra_layer)(?:\.|$)")
# S2: contract 모듈의 계층 import — BC 불문 3계층 전부(무의존 규칙이라 application_layer 포함).
LAYER_ANY_RE = re.compile(
    r"^application\.[A-Za-z_]\w*\.(?:domain_layer|application_layer|infra_layer)(?:\.|$)"
)
# S3: 자기 BC published_service 역-import(관통).
PUBLISHED_RE = re.compile(r"^application\.([A-Za-z_]\w*)\.published_service(?:\.|$)")


def _has_application_container(root: Path) -> bool:
    """표준 앱 컨테이너(`application/`)가 있나 — 없으면 기존 규약이라 적용 대상 아님."""
    return any(
        not is_migration_owned_path(root, path) and path.is_dir()
        for path in (root / "application", root / "src" / "application")
    )


def _own_bc(rel_parts: tuple[str, ...]) -> str | None:
    """`application/<bc>/...` 의 <bc> (TARGET_DIR 기준 상대 경로에서)."""
    if "application" in rel_parts:
        i = rel_parts.index("application")
        if i + 1 < len(rel_parts):
            return rel_parts[i + 1]
    return None


def _prod_py_files(root: Path) -> list[tuple[Path, tuple[str, ...]]]:
    """application/ 하위 프로덕션 .py 와 그 상대 parts — test 제외. ACL 면제는 S1 판정에서만."""
    out: list[tuple[Path, tuple[str, ...]]] = []
    for path in iter_non_migration_files(root, name_pattern="*.py"):
        rel_parts = path.relative_to(root).parts
        if set(rel_parts) & SKIP_DIRS:
            continue
        if "application" not in rel_parts:
            continue
        if set(rel_parts) & TEST_DIR_NAMES or path.name.startswith("test_") or path.name == "conftest.py":
            continue
        out.append((path, rel_parts))
    return out


def _is_contract_file(rel_parts: tuple[str, ...]) -> bool:
    """`published_service/…/contract/…` 하위인가(S2 대상)."""
    return (
        "published_service" in rel_parts
        and "contract" in rel_parts
        and rel_parts.index("published_service") < rel_parts.index("contract")
    )


def _is_acl_file(rel_parts: tuple[str, ...]) -> bool:
    """`infra_layer/acl/` 직하 계열인가(S1 면제 — 인접 경로 한정, `repository/acl/` 은닉은 비면제)."""
    return any(
        rel_parts[i] == "infra_layer" and rel_parts[i + 1] == "acl"
        for i in range(len(rel_parts) - 1)
    )


def _imported_paths(tree: ast.AST) -> Iterator[tuple[int, str]]:
    """모든 import 노드의 (lineno, 점경로) — 절대 import 만(상대 import 는 reviewer 몫)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # 상대 import — 저-recall 설계(docstring), 의미 레인 몫.
                continue
            if node.module:
                yield node.lineno, node.module
                for alias in node.names:  # `from application.x import domain_layer` 형태 포착
                    if alias.name != "*":
                        yield node.lineno, f"{node.module}.{alias.name}"


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
        changed = subprocess.run(
            ["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", str(rel)],
            capture_output=True,  # 커밋 0개 레포의 'bad revision' stderr 누출 방지.
        )
        return changed.returncode != 0
    except (OSError, subprocess.SubprocessError):
        return True  # git 판단 불가 → 안전하게 가드 통과(나머지 AND 가 좁힌다).


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-context-isolation] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1
    if not validate_migration_scope(root, "check-context-isolation"):
        return 1
    if not _has_application_container(root):
        return 0  # 표준 레이아웃(`application/`) 미적용 → 해당 없음.

    s1_findings: list[str] = []  # cross-BC 내부 결합
    s2_findings: list[str] = []  # contract 무의존 위반
    s3_findings: list[str] = []  # published 계약 관통
    for f, rel_parts in _prod_py_files(root):
        if not _is_new_or_modified(root, f):
            continue
        own = _own_bc(rel_parts)
        try:
            source = f.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)
        except (OSError, SyntaxError):
            continue  # 파싱 불가 → fail-open(스킵) — green 전제라 실코드는 파싱된다.
        src_lines = source.splitlines()
        is_contract = _is_contract_file(rel_parts)
        is_acl = _is_acl_file(rel_parts)
        in_layer = bool(set(rel_parts) & LAYER_DIR_NAMES)
        rel = f.relative_to(root)
        seen: set[tuple[int, str]] = set()  # (lineno, slice) — 한 import 문 1발화
        for lineno, dotted in _imported_paths(tree):
            shown = src_lines[lineno - 1].strip() if 0 < lineno <= len(src_lines) else dotted
            if is_contract:
                # S2 — contract 는 어느 계층도 import 하지 않는다(자기 BC 포함).
                if LAYER_ANY_RE.match(dotted) and (lineno, "s2") not in seen:
                    seen.add((lineno, "s2"))
                    s2_findings.append(f"  - {rel}:{lineno}  {shown}")
                continue  # contract 파일은 S2 전담(중복 계상 방지).
            m = CROSS_BC_RE.match(dotted)
            if m and m.group(1) != own and not is_acl and (lineno, "s1") not in seen:
                seen.add((lineno, "s1"))  # S1 — 타 BC 내부 계층(ACL 면제)
                s1_findings.append(f"  - {rel}:{lineno}  {shown}")
            p = PUBLISHED_RE.match(dotted)
            if p and p.group(1) == own and in_layer and (lineno, "s3") not in seen:
                seen.add((lineno, "s3"))  # S3 — 자기 published 역-import(관통)
                s3_findings.append(f"  - {rel}:{lineno}  {shown}")

    if not (s1_findings or s2_findings or s3_findings):
        return 0

    if s1_findings:
        print(
            "[check-context-isolation] BLOCKER — ACL 밖(도메인/응용/presentation)에서 타 BC 의 "
            "domain_layer/infra_layer 를 직접 import 함(컨텍스트 간 결합 누수):"
        )
        for line in s1_findings:
            print(line)
        print(
            "  근거: architecture-ddd §2.5·§3.2(3)·discipline-houserules §2. 컨텍스트 간 접근은 "
            "ACL 또는 published_service(OHS)로만 한다 — 다른 BC 의 내부 계층(예외 포함)을 직접 "
            "import 하지 않는다. ACL 이 업스트림 모델·예외를 번역해 격리하거나(infra_layer/acl/), "
            "OHS 를 경유하라. 접을 실질 사유가 있으면 코드에서 흘리지 말고 설계(G1)로 반송하라."
        )
    if s2_findings:
        print(
            "[check-context-isolation] BLOCKER — OHS contract 모듈이 계층"
            "(domain/application/infra)을 import 함(contract 무의존 위반):"
        )
        for line in s2_findings:
            print(line)
        print(
            "  근거: discipline-houserules `references/final.md` §2 OHS 내부 구조(contract 무의존). "
            "contract 는 표준 라이브러리·같은 서비스 contract 만 import 한다 — 계약 타입은 wire 형"
            "(str·Literal)으로 선언하고, 도메인 enum·모델을 계약 필드로 노출하지 않는다."
        )
    if s3_findings:
        print(
            "[check-context-isolation] BLOCKER — 자기 BC 의 계층(domain/application/infra)이 "
            "자기 published_service 를 import 함(published 계약 관통):"
        )
        for line in s3_findings:
            print(line)
        print(
            "  근거: discipline-houserules `references/final.md` §2 OHS 시그니처 계약. published "
            "계약 타입을 application_layer 안으로 관통시키지 않는다 — 응용은 자기 DTO"
            "(`<feature>/dto/<usecase>_request.py`·`<usecase>_result.py`)를 소유하고, OHS 가 "
            "계약↔응용 DTO 를 필드 단위로 언랩·재조립한다(타 BC 의 published_service 소비는 정상)."
        )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
