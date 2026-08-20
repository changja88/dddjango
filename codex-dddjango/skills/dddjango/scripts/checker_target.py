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

import re
import sys
from pathlib import Path

_BC_LAYER_DIRS: "tuple[str, ...]" = ("domain_layer", "application_layer", "driving_layer", "driven_layer")


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
