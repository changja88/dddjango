"""검사기 TARGET 호출 계약 — «BC 폴더 모양» 대상 거절 (라운드 1 P2 · 2026-08-12).

검사기 27종의 TARGET 은 «저장소 루트»다(application/ 의 부모). BC 폴더나
application/ 컨테이너 자체를 주면 그 밑에서 application/ 컨테이너를 못 찾아
«표준 미채택 clean(exit 0)»으로 조용히 통과한다 — 라운드 1 실측: 파이프라인이
`check-layer-skeleton.py application/child_settings` 호출로 V1 트리를 전부
green 처리했다. 조용 통과 대신 소리내어 거절한다(#74 「조용한 무동작 금지」와
같은 정신 — 행동 고정은 fixture_matrix «호출 계약 레인» 27케이스가 진다).

여기에 «인터프리터 하한 게이트»(2026-08-14 S2 F-A)도 산다: 대상 저장소가
`pyproject.toml` 로 `requires-python >=X.Y` 를 선언했는데 검사기가 그보다 낮은
인터프리터로 돌면, 검사기의 `_parse`(SyntaxError→None) fail-open 이 3.12+ 문법
파일을 «침묵 clean» 처리한다 — 라운드 3 실측: python3.9 실행이 controller 를
통째로 스킵해 #210 발화 0 오판 2건(라운드 2 waiver 사문 판정·라운드 3 대리 답변
근거)을 만들었다. 27종 전부가 이 모듈을 거치므로 여기 한 곳이 직접 실행
채널까지 봉인한다. fixture 는 pyproject 가 없어 게이트 무발화(판정 무변).

이 모듈은 수기 소유다(standard_tree.py 는 tree_mirror_check --write 가 전체
재생성하는 기계 사본이라 여기 두지 않는다).
"""
from __future__ import annotations

import ast
import re
import sys
import fnmatch
from pathlib import Path

_BC_LAYER_DIRS: "tuple[str, ...]" = ("domain_layer", "application_layer", "driving_layer", "driven_layer")


def skeleton_placeholder(path: Path) -> bool:
    """빈 골격 파일인가 — docstring 밖 문장이 0개(0바이트·공백·주석-only·docstring-only).

    표준 트리가 자리만 요구해 만들어 둔 파일은 aggregate·구현 의무의 대상이 아니다
    (판정 ④ 2026-08-25 — #256·#351 이 이 술어로 건너뛴다). 의미는 #114 렌더 계약의
    `_skeleton_placeholder_module`(check-error-centralization — 그쪽은 root 상대 경로
    서명이라 별도 실체)과 같다. `pass` 등 문장이 실재하거나 읽기·파싱 불능이면
    placeholder 가 아니다(fail-closed — 기존 진단 유지).
    """
    try:
        body = ast.parse(path.read_text(encoding="utf-8")).body
    except (OSError, UnicodeError, SyntaxError, ValueError):
        return False
    return not body or (
        len(body) == 1
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    )


def _interpreter_gap_reason(root: Path) -> "str | None":
    """대상의 `requires-python` 하한을 현 인터프리터가 못 미치면 사용 오류 «사유»."""
    py = root / "pyproject.toml"
    if not py.is_file():
        return None
    try:
        text = py.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r'requires-python\s*=\s*"[^"]*>=\s*(\d+)\.(\d+)', text)
    if m is None:
        return None
    lo = (int(m.group(1)), int(m.group(2)))
    if sys.version_info[:2] >= lo:
        return None
    cur = f"{sys.version_info[0]}.{sys.version_info[1]}"
    return (
        f"대상은 python >={lo[0]}.{lo[1]} 선언(pyproject.toml)인데 이 인터프리터는 {cur} 다 — "
        "AST 파싱 실패 파일이 침묵 스킵(fail-open)돼 거짓 clean 이 된다. "
        "대상 저장소의 .venv 인터프리터로 재실행하라"
    )


def bc_shaped_target_reason(target: "Path | str") -> "str | None":
    """TARGET 이 BC 폴더·application/ 컨테이너 모양이면 사용 오류 «사유»를 돌려준다.

    판정 + 대상 pyproject 1파일 읽기(인터프리터 하한 게이트)만 한다 — 호출자가
    자기 사용 오류 경로(print+return 1 또는 UsageError)로 보낸다. 존재하지 않거나
    디렉터리가 아닌 TARGET 은 각 검사기의 기존 오류 경로 몫이라 None 을 돌려준다.
    """
    p = Path(target)
    if not p.is_dir():
        return None
    # 위반 레코드 sink 의 «대상 저장소» 등록(T2-2) — 27종이 전부 이 모듈을 거치므로
    # 여기 한 곳이 설치본 기본 경로(`<root>/.dddjango/violations/`)를 봉인한다.
    try:
        import findings

        findings.set_target(p)
    except Exception:  # 레코드 채널은 «추가» 채널 — 등록 실패가 검사를 죽이지 않는다
        pass
    if (p / "application").is_dir():
        return _interpreter_gap_reason(p)  # 루트 모양 — 호출 계약 정상·인터프리터 하한만 확인
    layers = [n for n in _BC_LAYER_DIRS if (p / n).is_dir()]
    if layers:
        return (
            f"TARGET 이 BC 폴더로 보인다(층 폴더 직계: {', '.join(layers)}) — "
            "검사기의 대상은 저장소 루트다(application/ 의 부모)"
        )
    if p.name == "application" and any(
        child.is_dir() and any((child / n).is_dir() for n in _BC_LAYER_DIRS) for child in p.iterdir()
    ):
        return "TARGET 이 application/ 컨테이너 자체다 — 검사기의 대상은 저장소 루트다(application/ 의 부모)"
    return None

# ── 동명 폴더 승격(#490 교체형) 경로 해소 — 2026-09-01 ──────────────────────

def slot_file(expected: "Path") -> "Path | None":
    """칸 경로 `<…>/<이름>.py` 의 실현 — 파일이면 그 파일, 유효 승격이면 본체, 없으면 None."""
    if expected.is_file():
        return expected
    name = expected.name
    if name.endswith(".py"):
        promo = expected.parent / name[:-3]
        body = promo / name
        if promo.is_dir() and body.is_file():
            return body
    return None


def slot_glob(directory: "Path", pattern: str) -> "list[Path]":
    """단층 glob 의 승격 인지판 — `pattern` 파일 + (이름+`.py` 가 pattern 인 폴더의) 승격 본체."""
    out: "list[Path]" = sorted(directory.glob(pattern))
    if directory.is_dir():
        for p in sorted(directory.iterdir()):
            if p.is_dir():
                body = p / (p.name + ".py")
                if body.is_file() and fnmatch.fnmatch(p.name + ".py", pattern):
                    out.append(body)
    return out
