#!/usr/bin/env python3
"""표준 트리 삼중 동기 검사·재생성 도구 (메인테이너/빌드타임 — 런타임 게이트 아님).

배경: 트리 140행이 «생성기 안»(docs/mkrev2.py:ROWS)에 살아 검사기가 못 읽었다(#609).
플러그인에 기계 가독 사본(`dddjango/scripts/standard_tree.py`)을 두고, 이 도구가
정본과의 동기를 지킨다. `corpus_mirror_sync.py` 와 같은 부류다.

세 자리:
  A 정본     docs/file_tree.html 의 `data-r` 행 140개 — 명세 «자리»의 「트리 N행」이 이 번호다.
             (mkrev2.py:ROWS 가 아니라 «생성된 HTML»을 읽는 까닭: data-r 는 파트 순서라
              ROWS 리스트 인덱스와 다르고, 사용자 정본은 HTML 이다.)
  B 플러그인  dddjango/scripts/standard_tree.py — 검사기들이 import 하는 유일한 트리 데이터.
  C 문서     dddjango/skills/discipline-houserules/references/final.md 의 TREE 블록.

불변식:  A ≡ B (r·depth·name·kind) · A ≡ C (r·depth·name)
--write: A 로부터 B 전체와 C 블록을 다시 쓴다(정본→배포 한 방향).

fail-CLOSED: 파일 부재·행 수 ≠ 140·마커 부재는 exit 3.

exit:  0 = in-sync   2 = drift (--write 로 해소)   3 = 구조 전제 깨짐   1 = usage
"""
from __future__ import annotations

import argparse
import hashlib
import html as html_mod
import re
import sys
from pathlib import Path

EXIT_IN_SYNC = 0
EXIT_USAGE = 1
EXIT_DRIFT = 2
EXIT_STRUCTURE = 3

CANON_REL = "docs/file_tree.html"
PLUGIN_REL = "dddjango/scripts/standard_tree.py"
FINAL_REL = "dddjango/skills/discipline-houserules/references/final.md"
TREE_ROW_COUNT = 140
TREE_BEGIN = "<!-- TREE:BEGIN — tree_mirror_check 가 쓴다 · 손으로 고치지 않는다 -->"
TREE_END = "<!-- TREE:END -->"


class StructureError(Exception):
    pass


RowT = tuple[int, int, str, str, bool]  # (r, depth, name, kind, swappable)


def extract_canonical(root: Path) -> list[RowT]:
    p = root / CANON_REL
    if not p.is_file():
        raise StructureError(f"정본 부재: {p}")
    text = p.read_text(encoding="utf-8")
    pat = re.compile(
        r'<div data-r="(\d+)" class="tr[^"]*" style="--d:(\d+)"( data-sw="1")?>\s*<span class="path">(.*?)</span>',
        re.S,
    )
    rows: list[tuple[int, int, str, bool]] = []
    for m in pat.finditer(text):
        nm = re.search(r'<b class="nm">(.*?)</b>', m.group(4))
        name = html_mod.unescape(re.sub(r"<[^>]+>", "", nm.group(1) if nm else m.group(4))).strip()
        swappable = m.group(3) is not None
        if swappable and name.endswith("/"):
            raise StructureError(f"data-sw 는 파일 칸에만 붙는다 — r{m.group(1)} {name}")
        rows.append((int(m.group(1)), int(m.group(2)), name, swappable))
    if len(rows) != TREE_ROW_COUNT or [r for r, _, _, _ in rows] != list(range(1, TREE_ROW_COUNT + 1)):
        raise StructureError(f"정본에서 {len(rows)}행 — {TREE_ROW_COUNT}행·연속 data-r 이어야 한다")
    # kind — 제1원칙 #491: 조상이 연 <토큰> 집합으로 셋 중 하나
    tok_pat = re.compile(r"<([a-z_]+)>")
    stack: list[tuple[int, set[str]]] = []
    out: list[RowT] = []
    for r, d, name, sw in rows:
        while stack and stack[-1][0] >= d:
            stack.pop()
        bound: set[str] = set().union(*[s[1] for s in stack]) if stack else set()
        toks = set(tok_pat.findall(name))
        kind = "fixed" if not toks else ("reappear" if toks <= bound else "placeholder")
        out.append((r, d, name, kind, sw))
        stack.append((d, bound | toks))
    return out


def read_plugin(root: Path) -> list[RowT]:
    p = root / PLUGIN_REL
    if not p.is_file():
        raise StructureError(f"플러그인 트리 부재: {p}")
    import importlib.util

    spec = importlib.util.spec_from_file_location("standard_tree", p)
    if spec is None or spec.loader is None:
        raise StructureError(f"import 실패: {p}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["standard_tree"] = mod  # dataclass 가 문자열 애너테이션을 풀 때 모듈 조회가 필요하다
    spec.loader.exec_module(mod)
    return [(row.r, row.depth, row.name, row.kind, bool(getattr(row, 'swappable', False))) for row in mod.ROWS]


def render_block(rows: list[RowT]) -> str:
    return "\n".join(f"{r:>3} " + "  " * d + name for r, d, name, *_ in rows)


def read_final_block(root: Path) -> list[tuple[int, int, str]]:
    p = root / FINAL_REL
    if not p.is_file():
        raise StructureError(f"문서 부재: {p}")
    text = p.read_text(encoding="utf-8")
    if TREE_BEGIN not in text or TREE_END not in text:
        raise StructureError(f"TREE 마커 부재: {p}")
    block = text.split(TREE_BEGIN, 1)[1].split(TREE_END, 1)[0]
    rows: list[tuple[int, int, str]] = []
    for line in block.splitlines():
        m = re.match(r"^\s*(\d+) ((?:  )*)(\S.*)$", line)
        if m:
            rows.append((int(m.group(1)), len(m.group(2)) // 2, m.group(3).strip()))
    return rows


def emit_plugin(rows: list[RowT], root: Path) -> None:
    sha = hashlib.sha256((root / CANON_REL).read_bytes()).hexdigest()[:16]
    body = ",\n".join(
        f"    Row({r}, {d}, {name!r}, {kind!r}" + (", swappable=True)" if sw else ")")
        for r, d, name, kind, sw in rows
    )
    module = f'''"""dddjango 표준 파일트리 — 정본의 기계 가독 사본 (데이터 모듈 · 게이트 아님).

정본은 저장소의 `docs/file_tree.html`(트리 140행)이고, 이 파일은 검사기 19종이
import 하는 유일한 트리 데이터다. **손으로 고치지 않는다** — 정본이 개정되면
`workspace/tools/tree_mirror_check.py --write` 가 이 파일을 다시 쓰고,
`--check` 가 «정본 ≡ 이 파일 ≡ houserules final.md 트리 블록» 삼중 동기를 지킨다.

칸의 유형은 셋뿐이다(제1원칙 · 명세 #491):
  fixed        고정 이름 — 부모가 있으면 반드시 있다(#488)
  placeholder  `<>` 첫 등장 — 그 개념이 실제로 생길 때 0개 이상(#489)
  reappear     `<>` 재등장 — 조상이 이미 연 낱말이라 값이 채워져 fixed 와 같다(#491)

swappable=True 는 «동명 폴더 승격» 허용 표기다(#490 교체형 실현 — 파일 칸이
`<이름>.py` ⇄ `<이름>/`(본체+`__init__.py`) 두 실현을 갖는다). 칸 유형이 아니라
실현 형태의 직교 속성이며, 값의 정본은 docs/file_tree.html 의 data-sw 다.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SOURCE: str = "docs/file_tree.html"
SOURCE_SHA: str = "{sha}"  # 생성 시점 정본 sha256[:16] — 출처 표시(동기 판정은 행 비교로 한다)

Kind = Literal["fixed", "placeholder", "reappear"]


@dataclass(frozen=True)
class Row:
    r: int          # 정본의 data-r (파트 순서 — 명세 «자리»의 「트리 N행」이 이 번호다)
    depth: int
    name: str       # 리프 이름 — admin·templates 처럼 하위 경로를 품은 이름도 있다
    kind: Kind
    swappable: bool = False  # 동명 폴더 승격 허용 표기(#490 교체형 — 정본은 data-sw)


ROWS: tuple[Row, ...] = (
{body},
)


def children(parent: Row | None) -> tuple[Row, ...]:
    """parent 의 직계 자식 행. parent=None 이면 최상위 셋(BC·framework·<project>)."""
    if parent is None:
        return tuple(r for r in ROWS if r.depth == 0)
    idx = ROWS.index(parent)
    out: list[Row] = []
    for row in ROWS[idx + 1 :]:
        if row.depth <= parent.depth:
            break
        if row.depth == parent.depth + 1:
            out.append(row)
    return tuple(out)


def bc_root() -> Row:
    """`application/<bounded_context>/` — BC 서브트리의 뿌리(트리 1행)."""
    return ROWS[0]


def required_children(parent: Row) -> tuple[Row, ...]:
    """부모 인스턴스가 있으면 반드시 있어야 하는 자식(#488) — fixed·reappear."""
    return tuple(c for c in children(parent) if c.kind in ("fixed", "reappear"))


def is_dir(row: Row) -> bool:
    return row.name.endswith("/")


def concrete_name(row: Row, bindings: dict[str, str]) -> str:
    """`<토큰>` 을 채운 실제 이름 — 재등장 칸의 기대 이름을 만든다."""
    name = row.name
    for token, value in bindings.items():
        name = name.replace(f"<{{token}}>", value)
    return name
'''
    (root / PLUGIN_REL).write_text(module, encoding="utf-8")


def splice_final(rows: list[RowT], root: Path) -> None:
    p = root / FINAL_REL
    text = p.read_text(encoding="utf-8")
    if TREE_BEGIN not in text or TREE_END not in text:
        raise StructureError(f"TREE 마커 부재: {p}")
    head, rest = text.split(TREE_BEGIN, 1)
    _, tail = rest.split(TREE_END, 1)
    p.write_text(head + TREE_BEGIN + "\n```text\n" + render_block(rows) + "\n```\n" + TREE_END + tail, encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.root)
    try:
        canon = extract_canonical(root)
        if args.write:
            emit_plugin(canon, root)
            splice_final(canon, root)
            print(f"재생성: {PLUGIN_REL} · {FINAL_REL} TREE 블록 ({len(canon)}행)")
            return EXIT_IN_SYNC
        drift: list[str] = []
        plugin = read_plugin(root)
        if plugin != canon:
            diffs = [f"  r{c[0]}: 정본={c[1:]} ↔ 플러그인={p[1:]}" for c, p in zip(canon, plugin) if c != p]
            drift.append(f"A≠B ({len(diffs)}행):\n" + "\n".join(diffs[:10]))
        doc = read_final_block(root)
        canon3 = [(r, d, n) for r, d, n, *_ in canon]
        if doc != canon3:
            drift.append(f"A≠C (문서 블록 {len(doc)}행 ↔ 정본 {len(canon3)}행)")
    except StructureError as e:
        print(f"구조 전제 깨짐: {e}", file=sys.stderr)
        return EXIT_STRUCTURE
    if drift:
        print("\n".join(drift))
        print("→ --write 로 해소")
        return EXIT_DRIFT
    print(f"in-sync: 정본 ≡ 플러그인 ≡ 문서 ({TREE_ROW_COUNT}행)")
    return EXIT_IN_SYNC


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
