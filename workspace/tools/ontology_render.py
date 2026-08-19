"""렌더 투영기 (T1-4 — .venv 전용).

그래프 정본(rules/<doc_key>.ttl)의 그래프 소유 절을 markdown으로 투영한다.
절 렌더 = headingSnapshot 라인 + 마커 1행 + 블록 리터럴 단순 연결(구분자 삽입 0 — §13).
등가: 마커 라인 제거 후 이관 시점 원문과 byte 잔차 0(구조적 성립).

마커 문면(고정 — corpus_lint 오탐 회피: 경로에 workspace/ 미포함·«#숫자» 미포함·파일 선두 금지):
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

사용: PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_render.py [doc_key…]
      --apply : 코퍼스 파일의 그래프 소유 절 구간을 렌더 산출로 치환(=마커 삽입 — 소유 전환 커밋 재료)
exit 0 / 1 렌더 불일치(--apply 아닌 검사 용도 아님 — 검사는 ontology_render_sync.py) / 2 도구 오류
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from ontology_canon import REPO_ROOT

DJR = "https://numchida.com/ns/djr#"
MARKER = "<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->"
MANIFEST = REPO_ROOT / "workspace/design/2026-08-19-ontology-t1-census/corpus-manifest.tsv"


def manifest_paths() -> dict[str, str]:
    out = {}
    with open(MANIFEST, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            out[r["doc_key"]] = r["path"]
    return out


def load_doc_graph(doc_key: str):
    from rdflib import Graph

    p = REPO_ROOT / "ontology" / "rules" / f"{doc_key}.ttl"
    if not p.is_file():
        return None
    g = Graph()
    g.parse(p, format="turtle")
    return g


def graph_sections(g, path: str) -> dict[str, str]:
    """{절 키: 렌더 텍스트(마커 포함)} — 그래프 소유 절만."""
    from rdflib import Namespace, URIRef

    djr = Namespace(DJR)
    from urllib.parse import unquote

    from ontology_canon import frag_encode

    expected_prefix = f"{DJR}s/{frag_encode(path)}/"
    out = {}
    for s in g.subjects(URIRef(f"{DJR}sectionOwner"), djr["owner-graph"]):
        s_iri = str(s)
        # L-H #1: Section IRI 의 문서 경로가 이 doc 의 manifest 경로와 일치해야 한다
        if not s_iri.startswith(expected_prefix):
            raise ValueError(f"Section IRI 경로 불일치 — {s_iri} 가 {path} 소속이 아님")
        section_key_enc = s_iri[len(expected_prefix):]
        if "/" in section_key_enc:
            raise ValueError(f"Section IRI 형식 위반(절 키에 '/' 포함): {s_iri}")
        section_key = unquote(section_key_enc)
        heading = None
        for h in g.objects(s, djr.headingSnapshot):
            heading = str(h)
        blocks = []
        for b in g.subjects(djr.inSection, s):
            order = int(next(g.objects(b, djr.order)))
            text = str(next(g.objects(b, djr.text)))
            blocks.append((order, text))
        blocks.sort()
        orders = [o for o, _ in blocks]
        if orders != list(range(1, len(orders) + 1)):
            raise ValueError(f"{section_key}: 블록 order 불연속 {orders}")
        out[section_key] = heading + "\n" + MARKER + "\n" + "".join(t for _, t in blocks)
    return out


def apply_to_corpus(doc_key: str, path: str, rendered: dict[str, str]) -> bool:
    """코퍼스 파일에서 그래프 소유 절 스팬을 렌더 산출로 치환. 변경 여부 반환.

    원자성(L-H #10): 전 절의 치환을 메모리에서 검증·수행한 뒤 한 번만 기록한다 —
    중간 절에서 실패해도 파일은 원상이다."""
    from ontology_census import parse_sections

    p = REPO_ROOT / path
    content = p.read_bytes()
    original = content
    for skey, text in sorted(rendered.items()):
        secs = {s["section_key"]: s for s in parse_sections(content)}
        if skey not in secs:
            raise ValueError(f"{doc_key}/{skey}: 현재 분할에 절 없음")
        cur = secs[skey]["span"]
        new = text.encode("utf-8")
        if cur == new:
            continue
        if content.count(cur) != 1:
            raise ValueError(f"{doc_key}/{skey}: 절 스팬이 유일하지 않음")
        content = content.replace(cur, new, 1)
    if content != original:
        p.write_bytes(content)
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="렌더 투영기")
    ap.add_argument("doc_keys", nargs="*")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    paths = manifest_paths()
    targets = args.doc_keys or sorted(
        p.stem for p in (REPO_ROOT / "ontology" / "rules").glob("*.ttl"))
    rc = 0
    for dk in targets:
        if dk not in paths:
            print(f"[render] {dk}: manifest에 없음", file=sys.stderr)
            rc = 2
            continue
        g = load_doc_graph(dk)
        if g is None:
            print(f"[render] {dk}: rules 정본 없음", file=sys.stderr)
            rc = 2
            continue
        rendered = graph_sections(g, paths[dk])
        print(f"[render] {dk}: 그래프 소유 절 {len(rendered)} — {', '.join(sorted(rendered))}")
        if args.apply:
            changed = apply_to_corpus(dk, paths[dk], rendered)
            print(f"[render] {dk}: {'투영 적용(변경)' if changed else '이미 동기'}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
