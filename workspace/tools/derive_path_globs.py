#!/usr/bin/env python3
"""경로 글롭 기계 유도 — 표준 트리 + 절↔행 대응표 → `ontology/wiring/paths.ttl` (T2-4 Q1).

**왜 기계 유도인가**(적대 리뷰 AP-08): 글롭을 손으로 쓰면 «O-7 발주가 만들 경로를 이미 아는
상태에서 그것에 맞춰 저작했다»는 의심을 기계적으로 배제할 수 없다. 그래서 글롭 **문자열**은
표준 트리(`dddjango/scripts/standard_tree.py` — 140행 단일 출처)에서 유도하고, 저자의 판단은
**«이 절이 어느 서브트리를 관장하는가»** 한 줄로 좁혀 `section-path-map.tsv` 에 공개한다.
그 판단은 절의 주제에서만 나오며 발주 산출물을 참조하지 않는다(자인 W5′).

**글롭 문법(폐쇄 정의 — 적대 리뷰 AP-09·AQ-07)**:
  · 값은 저장소 상대 **POSIX** 경로 · 절대 경로·`\\`·`..` 금지 · 전체 일치(prefix 아님)
  · `*` = 한 세그먼트 내 임의(`/` 불포함) · `**` = 0개 이상 세그먼트 · case sensitive
  · 표준 트리의 `<placeholder>` 는 `*` 로, 디렉터리 행은 `/**` 로 닫는다
매칭 **구현**은 `dddjango/scripts/rulepack.py` 가 소유하고 이 문법을 따른다 —
정적 셰이프(문법·중복)와 런타임 matcher 는 **다른 게이트**다(AR 4-4).

**Q1 은 처치 밖이다**: 여기서 만든 글롭은 «이 파일에 어떤 규범이 적용되나» 조회에만 쓰이며
C암 selector 는 경로 축을 쓰지 않는다. C 효과 주장에 사용하지 않는다.

사용: python3 workspace/tools/derive_path_globs.py [--check]
exit 0 = 정상 / 2 = `--check` 표류·유도 실패 / 1 = 재료 결손
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dddjango" / "scripts"))
import standard_tree as st  # noqa: E402

MAP: Path = ROOT / "workspace" / "tools" / "section-path-map.tsv"
OUT: Path = ROOT / "ontology" / "wiring" / "paths.ttl"
DJR: str = "https://numchida.com/ns/djr#"
_PLACEHOLDER: "re.Pattern[str]" = re.compile(r"<[^>]+>")


def tree_path(row_number: int) -> "tuple[str, bool]":
    """표준 트리 행 번호 → (경로, 디렉터리 여부). 경로는 조상 사슬을 이어 만든다."""
    stack: "dict[int, str]" = {}
    for row in st.ROWS:
        stack[row.depth] = row.name
        if row.r == row_number:
            path: str = "".join(stack[d] for d in range(row.depth + 1))
            return path, path.endswith("/")
    raise KeyError(f"표준 트리에 행 {row_number} 가 없다")


def to_glob(path: str, is_dir: bool) -> str:
    """트리 경로 → 글롭. `<placeholder>` → `*` · 디렉터리 → `/**`."""
    glob: str = _PLACEHOLDER.sub("*", path)
    return (glob + "**") if is_dir else glob


def load_map() -> "list[dict]":
    if not MAP.is_file():
        raise FileNotFoundError(f"재료 결손: {MAP}")
    lines = [ln for ln in MAP.read_text(encoding="utf-8").splitlines() if ln.strip()]
    header = lines[0].split("\t")
    if header != ["doc", "section_number", "tree_row", "rationale"]:
        raise ValueError(f"대응표 헤더 이탈: {header}")
    return [dict(zip(header, ln.split("\t", 3))) for ln in lines[1:]]


def section_iri(doc: str, number: str, graph_dir: Path) -> str:
    """절 IRI 는 **그래프 질의**로 찾는다 — 정규식 TTL 파싱은 금지다(사후 리뷰 AS-13).

    앞선 구현은 `<IRI> a djr:Section ;` 모양을 정규식으로 찾고 **그 뒤 400자**에서 첫
    `sectionNumber` 를 집었다. 실측된 파손 3종: 접두 IRI 표기(`djr:s/foo`)는 못 찾고,
    선언에서 401자 뒤의 번호도 못 찾으며, **번호 없는 절 A 뒤에 절 B 의 번호가 있으면 A 의
    IRI 를 B 의 번호로 돌려준다** — 실패가 아니라 **틀린 `paths.ttl`** 을 만든다.

    카디널리티도 함께 잠근다: `(문서, 절번호)` 는 정확히 1건이어야 한다.
    """
    from rdflib import Graph

    g = Graph()
    g.parse(graph_dir / f"{doc}.ttl", format="turtle")
    q = f"""PREFIX djr: <{DJR}>
    SELECT ?s WHERE {{ ?s a djr:Section ; djr:sectionNumber "{number}" }}"""
    hits = sorted(str(r[0]) for r in g.query(q))
    if len(hits) != 1:
        raise KeyError(f"{doc} §{number} 절 IRI 카디널리티 {len(hits)} (정확히 1건이어야 한다)")
    return hits[0]


def render() -> "tuple[str, list[str]]":
    rows = load_map()
    graph_dir: Path = ROOT / "ontology" / "rules"
    entries: "list[tuple[str, str]]" = []
    report: "list[str]" = []
    for row in rows:
        path, is_dir = tree_path(int(row["tree_row"]))
        glob = to_glob(path, is_dir)
        for bad, why in (("\\", "역슬래시"), ("..", "상위 참조"), (" ", "공백")):
            if bad in glob:
                report.append(f"RED 글롭 문법 위반({why}): {glob!r}")
        if glob.startswith("/"):
            report.append(f"RED 절대 경로 금지: {glob!r}")
        entries.append((section_iri(row["doc"], row["section_number"], graph_dir), glob))
        report.append(f"[paths] {row['doc']} §{row['section_number']} → 트리 {row['tree_row']} → {glob}")

    seen: "dict[str, str]" = {}
    for iri, glob in entries:
        if glob in seen and seen[glob] != iri:
            report.append(f"[paths] 주의 글롭 공유: {glob} ← 절 2개 이상(포함 관계 검사는 구조 검사 소유)")
        seen.setdefault(glob, iri)

    body: "list[str]" = ["@prefix djr: <https://numchida.com/ns/djr#> .", ""]
    for iri, glob in sorted(entries):
        body.append(f"<{iri}> djr:pathGlob \"{glob}\" .")
        body.append("")
    return "\n".join(body).rstrip("\n") + "\n", report


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description="경로 글롭 기계 유도(T2-4 Q1)")
    ap.add_argument("--check", action="store_true", help="쓰지 않고 커밋본과 byte 대조")
    args = ap.parse_args(argv)
    try:
        text, report = render()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"[paths] 재료 결손: {exc}", file=sys.stderr)
        return 1
    for line in report:
        print(line if line.startswith("[paths]") else f"[paths] {line}")
    if any("RED" in line for line in report):
        return 2
    if args.check:
        if not OUT.is_file():
            print(f"[paths] RED {OUT} 부재 — 유도 미실행")
            return 2
        if OUT.read_text(encoding="utf-8") != text:
            print(f"[paths] RED {OUT} 가 대응표·표준 트리와 어긋난다(수기 편집 또는 노후)")
            return 2
        print("[paths] 정합 — paths.ttl == derive(표준 트리 × 대응표)")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"[paths] 기록 {OUT.relative_to(ROOT)} ({len(text)} bytes · {text.count('pathGlob')} 트리플)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
