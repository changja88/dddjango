#!/usr/bin/env python3
"""dddjango 유스케이스 데이터 계약 배치 결정적 백스톱 (houserules §3 표 dto/ — 연산 모듈 인라인 금지).

표준 레이아웃(`application/<bc>/application_layer/<feature>/{command,query}/`)의 연산 모듈에서
*이번 작업이 만든* 유스케이스 데이터 계약(dataclass)의 인라인 정의를 잡는다. 두 슬라이스:

  S1  공개 dataclass 인라인 — 연산 모듈(`*_command.py`/`*_query.py`) 최상위에 공개
      (`_` 비접두) dataclass 가 정의됨(이름이 `Command`/`Query` 로 끝나는 연산 클래스 자체는
      제외 — DI 필드 스타일 `@dataclass class …Command` 는 정당). 반환 계약은
      `<feature>/dto/<usecase>_result.py`, 입력은 `<usecase>_request.py` 소유다
      (houserules `references/final.md` §3 표 dto/ 행 — 소비처 불문).
  S2  `_` 위장 반환 — `_` 접두(사설) dataclass 가 같은 모듈 연산 클래스의 `execute` **반환
      어노테이션**에 등장. 사설 표기는 내부 스테이징(private 헬퍼 간 전달) 한정이 정당하고,
      execute 가 반환하면 그건 공개 유스케이스 반환 계약이다 — S1 반송 후 최저비용 우회
      (`Result`→`_Result` 개명)를 결정적으로 봉쇄한다.

*왜 결정적 백스톱인가* — 둘 다 AST 직격의 FP≈0 직접형이고(모듈 최상위 ClassDef·데코레이터
4형태 `dataclass`/`dataclasses.dataclass`/호출형·execute 반환 어노테이션의 이름 원자),
어느 것도 컴파일·테스트를 깨지 않아 TDD Red 로 안 잡힌다(인라인이어도 Green). 실증:
적용 프로젝트 8 BC·56 연산 모듈에서 위반 6건(pairing 5·accounts 1 — 전원 execute 공개 반환
dataclass 인라인)·정당 사설 4건(ai_chat 내부 스테이징) 관측, 본 규칙 소급 적용 시 6/6 적중·
0/4 오탐. 의미 변종(NamedTuple/TypedDict/pydantic Model 공개 계약·`_` 사설의 타 모듈 import·
연산 클래스 내부 중첩 공개 결과 클래스·유스케이스 반환 계약의 service 모듈 정의(정책 내부
Decision 페이로드·타 모듈 소유 반환 타입 재사용은 정당)·명명/경로 규약 위반 파일 안의 인라인·
`<usecase>_result.py` 명명 축(파일명은 이 백스톱 비검사))은 discipline-reviewer 의미 레인 몫.

거짓 양성 회피 — AND 합성으로만 차단:
  1) 표준 레이아웃을 쓴다 = 레포에 `application/` 컨테이너가 있다. 없으면 §1.1 기존 규약이라
     적용 대상이 아니다 → exit 0. 경로 판정은 TARGET_DIR 상대이며 **TARGET_DIR 는 프로젝트
     루트를 전제한다**(porcelain 경로와의 정렬 조건).
  2) git 레포다. touched 한정 규약이라 git 없이는 식별 불가 → exit 0(보수적).
  3) 그 파일이 이번 변경에서 touched 다 — `git status --porcelain -uall` 기준(**-uall 필수**:
     기본 porcelain 은 미추적 디렉터리를 `?? dir/` 한 줄로 접어 트리-통째 신규 BC 의 개별
     파일이 안 보인다 — 실증 위반 6건 전원이 접힌 신규 트리에서 출생, -uall 없이는 6/6 무발화).
     신규(`??`/`A`)는 전체, 수정(`M`)은 **추가된 라인**(git diff HEAD -U0)에 anchor 라인
     — S1 은 {class 라인}∪{데코레이터 라인들}(기존 공개 클래스에 `@dataclass` 만 얹는 편집
     포획), S2 는 거기에 execute def·returns 라인 합집합 — 이 있을 때만 잡는다(기존 인라인은
     grandfather, §1.1). 스테이징 리네임(R)은 신규·수정 어느 쪽에도 안 잡혀 자연 면제(수정
     특례·RM 은 M 으로 검사)이고, plain mv(`D`+`??`)는 신규 취급이다(내용 동일성 대조는
     비결정적이라 하지 않는다 — 이동 시 기존 인라인이 발화하면 그 기회에 정화하거나 이동을
     커밋 후 재실행). **백스톱은 이번 작업분이 미커밋 상태에서 실행하는 게 전제다** — 중간
     커밋 후 재실행은 touched 공집합이라 무의미하다.
  4) 연산 모듈 한정 — 상대경로에 `application_layer` 포함 + 직속 부모 디렉터리 `command`|
     `query` + 파일명 `*_command.py`|`*_query.py`. 테스트 경로(`test`/`tests`·`test_*.py`·
     `conftest.py`)·SKIP_DIRS 제외. dto/·service/·domain_layer 는 비대상(§3 표 소유 구분).
  5) 파싱 불가 파일 fail-open(스킵) — 런타임 게이트 공통.

사용법: check-usecase-dto-placement.py [TARGET_DIR]   (기본=현재 디렉터리 — 프로젝트 루트)
종료코드: 0=clean(또는 표준 레이아웃 미적용·non-git), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
TEST_DIR_NAMES = {"test", "tests"}
OPERATION_SUFFIXES = ("Command", "Query")
HUNK_RE = re.compile(r"^@@ [^+]*\+(\d+)(?:,(\d+))? @@")
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _touched_map(root: Path) -> dict[str, str] | None:
    """rel posix 경로 → porcelain XY 코드. None=git 조회 실패(보수적 skip)."""
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "-uall"],
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if res.returncode != 0:
        return None
    out: dict[str, str] = {}
    for line in res.stdout.splitlines():
        if len(line) < 4:
            continue
        code, path = line[:2], line[3:]
        if " -> " in path:  # R/C: `old -> new` — 새 경로 기준.
            path = path.split(" -> ", 1)[1]
        out[path.strip('"')] = code
    return out


def _added_lines(root: Path, rel: Path) -> set[int]:
    """수정(M) 파일에서 이번 변경으로 *추가된* 라인 번호 집합(git diff HEAD -U0)."""
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "diff", "HEAD", "--unified=0", "--no-color", "--", str(rel)],
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return set()
    if res.returncode != 0:
        return set()
    lines: set[int] = set()
    for ln in res.stdout.splitlines():
        m = HUNK_RE.match(ln)
        if m:
            start = int(m.group(1))
            count = int(m.group(2)) if m.group(2) is not None else 1
            lines.update(range(start, start + count))
    return lines


def _candidate_files(root: Path) -> list[Path]:
    """`application/**/application_layer/**/{command,query}/*_{command,query}.py` 프로덕션 파일."""
    app = root / "application"
    if not app.is_dir():
        return []
    files: list[Path] = []
    for f in sorted(app.rglob("*.py")):
        rel_parts = f.relative_to(root).parts
        parts = set(rel_parts)
        if parts & SKIP_DIRS or parts & TEST_DIR_NAMES:
            continue
        if f.name.startswith("test_") or f.name == "conftest.py":
            continue
        if "application_layer" not in rel_parts:
            continue
        parent = f.parent.name
        if parent == "command" and f.name.endswith("_command.py"):
            files.append(f)
        elif parent == "query" and f.name.endswith("_query.py"):
            files.append(f)
    return files


def _is_dataclass_decorated(node: ast.ClassDef) -> bool:
    """데코레이터 4형태: dataclass · dataclasses.dataclass · 각각의 호출형(pydantic
    dataclasses 포함 — 공개 데이터 계약 인라인이라는 위반 성격이 동일해 구분하지 않는다)."""
    for deco in node.decorator_list:
        target = deco.func if isinstance(deco, ast.Call) else deco
        if isinstance(target, ast.Attribute) and target.attr == "dataclass":
            return True
        if isinstance(target, ast.Name) and target.id == "dataclass":
            return True
    return False


def _anchor_lines(node: ast.ClassDef) -> set[int]:
    """M 파일 판정 anchor — class 라인 ∪ 데코레이터 라인들(데코레이터만 얹는 편집 포획)."""
    return {node.lineno} | {d.lineno for d in node.decorator_list}


def _annotation_idents(node: ast.expr | None) -> set[str]:
    """반환 어노테이션의 이름 원자(문자열 어노테이션은 식별자 정규식으로 보수 추출)."""
    if node is None:
        return set()
    out: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.update(IDENT_RE.findall(n.value))
    return out


def _file_findings(path: Path, root: Path, added: set[int] | None) -> list[str]:
    """added=None 이면 신규 파일(전 라인 대상). M 파일은 anchor∩added 로만 발화."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return []  # fail-open.
    rel = path.relative_to(root)

    top_classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    dataclasses_ = [n for n in top_classes if _is_dataclass_decorated(n)]
    private_dc = {n.name: n for n in dataclasses_ if n.name.startswith("_")}

    findings: list[str] = []

    # S1 — 공개 dataclass 인라인(연산 클래스 자체는 제외).
    for node in dataclasses_:
        if node.name.startswith("_") or node.name.endswith(OPERATION_SUFFIXES):
            continue
        if added is not None and not (_anchor_lines(node) & added):
            continue  # grandfather — 이번 변경이 만든 정의가 아님.
        findings.append(f"  - {rel}:{node.lineno}: {node.name} — 공개 dataclass 인라인(S1)")

    # S2 — `_` 사설 dataclass 가 execute 반환 어노테이션에 등장(위장 반환).
    for op in top_classes:
        if not op.name.endswith(OPERATION_SUFFIXES):
            continue
        for meth in op.body:
            if not isinstance(meth, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if meth.name != "execute":
                continue
            leaked = _annotation_idents(meth.returns) & set(private_dc)
            for name in sorted(leaked):
                dc = private_dc[name]
                anchors = _anchor_lines(dc) | {meth.lineno}
                if meth.returns is not None:
                    anchors.add(meth.returns.lineno)
                if added is not None and not (anchors & added):
                    continue
                findings.append(
                    f"  - {rel}:{meth.lineno}: {op.name}.execute -> {name} — `_` 위장 반환(S2)"
                )
    return findings


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-usecase-dto-placement] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    candidates = _candidate_files(root)
    if not candidates:
        return 0  # 표준 레이아웃(`application/`) 미적용 또는 연산 모듈 없음 → 해당 없음.
    if not (root / ".git").exists():
        return 0  # touched 한정 규약 — git 없이는 식별 불가 → 스킵(보수적).
    touched = _touched_map(root)
    if touched is None:
        return 0  # git 조회 실패 — fail-open.

    findings: list[str] = []
    for f in candidates:
        rel = f.relative_to(root).as_posix()
        code = touched.get(rel)
        if code is None:
            continue  # 이번 변경이 안 건드림 — grandfather.
        if "?" in code or "A" in code:
            added: set[int] | None = None  # 신규 — 전 라인 대상.
        elif "M" in code:
            added = _added_lines(root, f.relative_to(root))
            if not added:
                continue
        else:
            continue  # R 등 — 수정 특례(자연 면제).
        findings.extend(_file_findings(f, root, added))

    if findings:
        print(
            "[check-usecase-dto-placement] BLOCKER — command/query 연산 모듈에 유스케이스 "
            "데이터 계약(dataclass)이 인라인 정의됐다(`discipline-houserules` §3 표 dto/):"
        )
        for x in findings:
            print(x)
        print(
            "  근거: `discipline-houserules` `references/final.md` §3 표 dto/ 행 — 유스케이스 "
            "반환 DTO 는 소비처 불문 `<feature>/dto/<usecase>_result.py`(`@dataclass class "
            "…Result`), 입력은 `<usecase>_request.py` 소유다. 연산 모듈의 공개 표면은 연산 "
            "클래스뿐이다. 처방 — ① 반환·공유 계약은 dto/ 로 이주(기본). ② `_` 사설화는 "
            "execute() 반환도 타 모듈 import 도 아닌 내부 스테이징 한정 — execute 가 반환하면 "
            "공개 계약이라 동일 위반(S2)이다. ③ 예외 페이로드는 domain_layer 예외 모듈 소유고, "
            "연산 클래스 자체를 dataclass 로 선언한 것(`@dataclass class …Command`)은 정상이니 "
            "§4 명명(`…Command`/`…Query` 접미)을 확인하라."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
