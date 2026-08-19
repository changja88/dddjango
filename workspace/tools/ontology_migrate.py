"""이관 조립 도구 (T1-3 — 공정 §15 ①~④의 기계 부분, .venv 전용).

이관 명세 JSON(migrate-spec/1 — LLM이 저작)을 받아 rules/·wiring/ 정본 ttl과
ISSUED·LEDGER 갱신을 조립한다. 블록 리터럴은 언제나 **원문 스팬 verbatim**을 원문
파일에서 직접 잘라 넣는다(재타이핑 금지 — byte 등가의 기계 보장).

명세 스키마(migrate-spec/1):
{ "schema": "migrate-spec/1", "doc_key": "...", "path": "...",
  "sections": [ { "section_key": "s022-6.1", "line_start": 471, "line_end": 500,
    "blocks": [ { "lines": [472, 474], "kind": "prose" },
                { "lines": [475, 475], "kind": "norm", "norms": [
                    { "label": "200 매핑", "class": "Obligation",
                      "enforcedBy": ["check-x.py"], "delegatedTo": ["agent-y"],
                      "basis": "4원 근거 한 줄" } ] } ] } ] }

- kind: norm|prose|code|table-row|checklist-item. 리터럴 datatype: norm/prose/checklist=@ko,
  code/table-row=xsd:string (§16). blocks의 lines는 [시작, 끝](1-indexed·포함)이며 첫 블록
  시작 = line_start+1(헤딩 다음 행 — 절 선두 구분자는 첫 블록 선두 귀속 §13), 연속·비중첩·
  절 끝까지 전체 커버를 도구가 단언한다(무손실).
- 채번: ISSUED 마지막 번호+1부터 명세 등장 순. Expression = <…R-NNNN@이관일>·revision 1.
- 검증만(기본): 산출물을 stdout 요약. --write: rules/wiring ttl 기록+ISSUED append+
  LEDGER append(owner=graph·이관 필드 — 소유 전환은 T1-4 한 커밋 규율의 작업 트리 단계).

사용: PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py SPEC.json [--write]
      … ontology_migrate.py --emit-registry [--write]  (wiring/registry.ttl — Checker 27+Agent 8)
exit 0 정상 / 1 검증 실패 / 2 도구 오류
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

from ontology_canon import REPO_ROOT, canon_turtle, frag_encode, load_prefix_registry

DJR = "https://numchida.com/ns/djr#"
MANIFEST = REPO_ROOT / "workspace/design/2026-08-19-ontology-t1-census/corpus-manifest.tsv"
SECTIONS_TSV = REPO_ROOT / "workspace/design/2026-08-19-ontology-t1-census/sections.tsv"
KIND_LANG = {"norm": "ko", "prose": "ko", "checklist-item": "ko"}
NORM_CLASSES = {"Obligation", "Prohibition", "Permission", "Exception", "Override"}

enc = frag_encode  # §14 인코딩 단일 출처 = ontology_canon.frag_encode (L-H #12)


def section_iri(path: str, section_key: str) -> str:
    return f"{DJR}s/{enc(path)}/{enc(section_key)}"


def load_issued() -> tuple[int, dict[str, list[str]]]:
    """(마지막 번호, 경로별 기존 rid 목록 — 등재 순). 재실행 시 같은 문서의 기존 rid를
    명세 등장 순으로 재사용해 재채번을 막는다(명세의 기존 절 부분은 불변 관례)."""
    issued = REPO_ROOT / "ontology" / "ISSUED"
    last = 0
    by_path: dict[str, list[str]] = {}
    if issued.is_file():
        for line in issued.read_text(encoding="utf-8").splitlines():
            if line.startswith("R-"):
                rid, _, p = line.split("\t")
                last = max(last, int(rid[2:]))
                by_path.setdefault(p, []).append(rid)
    return last, by_path


def load_census_row(doc_key: str, section_key: str) -> dict | None:
    with open(SECTIONS_TSV, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["doc_key"] == doc_key and r["section_key"] == section_key:
                return r
    return None


def build_graphs(spec: dict, start_num: int, reuse: list[str] | None = None):
    """(rules Graph, wiring Graph, issued_rows, ledger_rows, 요약) — 검증 실패 시 ValueError."""
    from rdflib import Graph, Literal, Namespace, URIRef
    from rdflib.namespace import RDF, XSD

    djr = Namespace(DJR)
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")
    prov = Namespace("http://www.w3.org/ns/prov#")
    g = Graph()
    w = Graph()

    doc_key, path = spec["doc_key"], spec["path"]
    # L-H #1: 명세 doc_key↔path 는 manifest 쌍과 정확 일치해야 한다(다른 파일 투영 차단)
    manifest_pairs: dict[str, str] = {}
    with open(MANIFEST, encoding="utf-8") as _f:
        for _r in csv.DictReader(_f, delimiter="\t"):
            manifest_pairs[_r["doc_key"]] = _r["path"]
    if manifest_pairs.get(doc_key) != path:
        raise ValueError(f"{doc_key}: 명세 path {path!r} ≠ manifest 등재 {manifest_pairs.get(doc_key)!r}")
    data = (REPO_ROOT / path).read_bytes()
    # 재실행 안전: 이미 투영 적용된 절의 마커 라인을 제거한 «복원 원문» 위에서
    # 명세 좌표(센서스 동결 시점 기준)를 해석한다 — 절 해시 검증이 복원 정합을 단언.
    from ontology_render import MARKER as _MARKER
    data = data.replace(b"\n" + _MARKER.encode("utf-8") + b"\n", b"\n")
    parts = data.split(b"\n")
    offs, off = [0], 0
    for p in parts:
        off += len(p) + 1
        offs.append(off)

    def span(a: int, b: int) -> bytes:  # 1-indexed 포함 범위의 raw 스팬
        end = min(offs[b], len(data))
        return data[offs[a - 1]:end]

    doc_iri = URIRef(f"{DJR}d/{enc(path)}")
    g.add((doc_iri, RDF.type, djr.Document))
    g.add((doc_iri, skos.prefLabel, Literal(doc_key, lang="ko")))

    today = dt.date.today().isoformat()
    num = start_num
    reuse_queue = list(reuse or [])
    # L-H #2·#3: 재사용 rid 는 기존 정본과 (label·class) 정합해야 하고 Expression(날짜)을 보존한다
    prev: dict[str, dict] = {}
    prev_rules = REPO_ROOT / "ontology" / "rules" / f"{doc_key}.ttl"
    if reuse_queue and prev_rules.is_file():
        pg = Graph()
        pg.parse(prev_rules, format="turtle")
        for w_ in pg.subjects(URIRef(f"{DJR}currentExpression"), None):
            rid_ = str(w_).rsplit("#", 1)[-1]
            cls_ = str(next(pg.objects(w_, RDF.type))).rsplit("#", 1)[-1]
            lbl_ = str(next(pg.objects(w_, URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))))
            expr_ = next(pg.objects(w_, URIRef(f"{DJR}currentExpression")))
            prev[rid_] = {"label": lbl_, "class": cls_, "expr": expr_}
    issued_rows, ledger_rows = [], []
    summary = []

    for sec in spec["sections"]:
        skey, ls, le = sec["section_key"], sec["line_start"], sec["line_end"]
        census = load_census_row(doc_key, skey)
        if census is None:
            raise ValueError(f"{skey}: 센서스에 없는 절")
        if int(census["line_start"]) != ls or int(census["line_end"]) != le:
            raise ValueError(f"{skey}: 좌표 불일치 — 센서스 {census['line_start']}-{census['line_end']}")
        sec_span = span(ls, le)
        if hashlib.sha256(sec_span).hexdigest() != census["sha256"]:
            raise ValueError(f"{skey}: 절 스팬 해시 ≠ 센서스 기준선(원문 변경?)")

        s_iri = URIRef(section_iri(path, skey))
        heading_line = parts[ls - 1].decode("utf-8")
        g.add((s_iri, RDF.type, djr.Section))
        g.add((s_iri, djr.headingSnapshot, Literal(heading_line, lang="ko")))
        if census["anchor"]:
            g.add((s_iri, djr.sectionNumber, Literal(census["anchor"], datatype=XSD.string)))
        g.add((s_iri, djr.sectionOwner, djr["owner-graph"]))
        g.add((s_iri, djr.inDocument, doc_iri))

        blocks = sec["blocks"]
        expect = ls + 1
        joined = b""
        n_norm_sentences = 0
        for order, blk in enumerate(blocks, 1):
            a, b = blk["lines"]
            if a != expect:
                raise ValueError(f"{skey} b{order}: 블록 시작 {a} ≠ 기대 {expect}(연속·무손실 위반)")
            expect = b + 1
            blk_span = span(a, b)
            joined += blk_span
            kind = blk["kind"]
            if kind not in ("norm", "prose", "code", "table-row", "checklist-item"):
                raise ValueError(f"{skey} b{order}: 미지 kind {kind}")
            b_iri = URIRef(f"{section_iri(path, skey)}/b{order}")
            g.add((b_iri, RDF.type, djr.Block))
            g.add((b_iri, djr.inSection, s_iri))
            g.add((b_iri, djr.kind, djr[f"kind-{kind}"]))
            g.add((b_iri, djr.order, Literal(order, datatype=XSD.integer)))
            text = blk_span.decode("utf-8")
            if kind in KIND_LANG:
                g.add((b_iri, djr.text, Literal(text, lang=KIND_LANG[kind])))
            else:
                g.add((b_iri, djr.text, Literal(text, datatype=XSD.string)))
            for target in blk.get("restates", []):
                # "<manifest path의 doc_key>/<section_key>/b<order>" — 정본 블록(그래프 내) 지시
                t_doc, t_skey, t_b = target.rsplit("/", 2)
                t_path = spec["restates_paths"][t_doc] if "restates_paths" in spec else None
                if t_path is None:
                    raise ValueError(f"{skey} b{order}: restates 대상 {t_doc} 경로 미지정(restates_paths)")
                g.add((b_iri, djr.restates,
                       URIRef(f"{section_iri(t_path, t_skey)}/{t_b}")))
            for norm in blk.get("norms", []):
                if norm["class"] not in NORM_CLASSES:
                    raise ValueError(f"{skey} b{order}: 미지 규범 유형 {norm['class']}")
                if not norm.get("enforcedBy") and not norm.get("delegatedTo"):
                    raise ValueError(f"{skey} b{order} «{norm['label']}»: 무소유(enforcedBy∨delegatedTo 필요)")
                n_norm_sentences += 1
                if reuse_queue:
                    rid = reuse_queue.pop(0)  # 기존 채번 재사용(등재 순 = 명세 등장 순 관례)
                    new_issue = False
                    pv = prev.get(rid)
                    if pv is None or pv["label"] != norm["label"] or pv["class"] != norm["class"]:
                        raise ValueError(
                            f"{skey} b{order}: {rid} 재사용 정합 위반 — 기존 정본"
                            f"({pv and pv['class']}/{pv and pv['label']}) ≠ 명세({norm['class']}/{norm['label']})."
                            " 명세의 기존 절 부분은 불변 관례 — 변경하려면 ISSUED 클린 재채번(미커밋 한정)")
                    e_iri = pv["expr"]  # Expression(최초 이관일) 보존 — 재실행 멱등
                else:
                    num += 1
                    rid = f"R-{num:04d}"
                    new_issue = True
                    e_iri = URIRef(f"{DJR}{rid}@{today}")
                w_iri = URIRef(f"{DJR}{rid}")
                g.add((w_iri, RDF.type, djr[norm["class"]]))
                g.add((w_iri, skos.prefLabel, Literal(norm["label"], lang="ko")))
                g.add((w_iri, djr.currentExpression, e_iri))
                g.add((e_iri, RDF.type, djr.Expression))
                g.add((e_iri, djr.revision, Literal(1, datatype=XSD.integer)))
                g.add((e_iri, prov.specializationOf, w_iri))
                g.add((b_iri, djr.statesNorm, w_iri))
                for c in norm.get("enforcedBy", []):
                    w.add((w_iri, djr.enforcedBy, URIRef(f"{DJR}c/{enc(c)}")))
                for a_ in norm.get("delegatedTo", []):
                    w.add((w_iri, djr.delegatedTo, URIRef(f"{DJR}a/{enc(a_)}")))
                if new_issue:
                    issued_rows.append(f"{rid}\t{today}\trules/{doc_key}.ttl")
        if expect != le + 1:
            raise ValueError(f"{skey}: 마지막 블록 끝 {expect - 1} ≠ 절 끝 {le}(무손실 위반)")
        head_span = span(ls, ls)
        if head_span + joined != sec_span:
            raise ValueError(f"{skey}: 헤딩+블록 연결 ≠ 절 스팬(byte 등가 위반)")
        ledger_rows.append([doc_key, skey, census["sha256"], "graph",
                            hashlib.sha256(sec_span).hexdigest(), str(len(blocks)),
                            str(n_norm_sentences), "pending",
                            f"migrate:t1-pilot {today} (commit 해시는 검수 패키지 단계 ⑦에서 기입)"])
        summary.append(f"{skey}: 블록 {len(blocks)} · Work {n_norm_sentences}")
    return g, w, issued_rows, ledger_rows, summary


AGENTS = ["command-dddjango", "agent-acceptance-tester", "agent-coder", "agent-design-architect",
          "agent-design-review-api", "agent-design-review-db", "agent-design-review-ddd",
          "agent-discipline-reviewer"]


def emit_registry(write: bool) -> int:
    from rdflib import Graph, Literal, Namespace, URIRef
    from rdflib.namespace import RDF

    djr = Namespace(DJR)
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")
    g = Graph()
    checkers = sorted(p.name for p in (REPO_ROOT / "dddjango" / "scripts").glob("check-*.py"))
    for c in checkers:
        iri = URIRef(f"{DJR}c/{enc(c)}")
        g.add((iri, RDF.type, djr.Checker))
        g.add((iri, skos.prefLabel, Literal(c, lang="ko")))
    for a in AGENTS:
        iri = URIRef(f"{DJR}a/{enc(a)}")
        g.add((iri, RDF.type, djr.Agent))
        g.add((iri, skos.prefLabel, Literal(a, lang="ko")))
    registry = load_prefix_registry(REPO_ROOT / "ontology" / "prefixes.ttl")
    text = canon_turtle(g, registry, allow_lists=False)
    out = REPO_ROOT / "ontology" / "wiring" / "registry.ttl"
    if write:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"[migrate] wiring/registry.ttl 기록 — Checker {len(checkers)} · Agent {len(AGENTS)}")
    else:
        print(f"[migrate] (dry) registry: Checker {len(checkers)} · Agent {len(AGENTS)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="이관 조립 도구 (migrate-spec/1)")
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--emit-registry", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        assert enc("a b#c%d") == "a%20b%23c%25d"
        assert enc("한글·§6.2") == "한글·§6.2"
        from urllib.parse import unquote
        for s in ("a b", "100%", "x`y", "절 6.2"):
            assert unquote(enc(s)) == s, s
        print("self-test OK (enc 왕복 항등)")
        return 0
    if args.emit_registry:
        return emit_registry(args.write)
    if not args.spec:
        print("SPEC.json 필요", file=sys.stderr)
        return 2

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    if spec.get("schema") != "migrate-spec/1":
        print("schema ≠ migrate-spec/1", file=sys.stderr)
        return 2
    last, by_path = load_issued()
    reuse = by_path.get(f"rules/{spec['doc_key']}.ttl", [])
    try:
        g, w, issued_rows, ledger_rows, summary = build_graphs(spec, last, reuse)
    except ValueError as exc:
        print(f"[migrate] 검증 실패: {exc}", file=sys.stderr)
        return 1
    # 재실행 시 LEDGER 중복 append 방지 — 단 owner=graph 라도 메타(해시·블록 계수)가
    # 달라졌으면 새 행을 append 해 원장을 현행과 정합시킨다(L-H #4)
    up_to_date = set()
    ledger_path = REPO_ROOT / "ontology" / "LEDGER.tsv"
    if ledger_path.is_file():
        eff = {}
        with open(ledger_path, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                eff[(r["doc_key"], r["section_key"])] = r
        for row in ledger_rows:
            cur = eff.get((row[0], row[1]))
            if cur and cur["owner"] == "graph" and (
                cur["migrated_sha256"], cur["block_total"], cur["block_norm"]
            ) == (row[4], row[5], row[6]):
                up_to_date.add((row[0], row[1]))
    ledger_rows = [r for r in ledger_rows if (r[0], r[1]) not in up_to_date]

    registry = load_prefix_registry(REPO_ROOT / "ontology" / "prefixes.ttl")
    rules_text = canon_turtle(g, registry, allow_lists=False)
    wiring_text = canon_turtle(w, registry, allow_lists=False)
    doc_key = spec["doc_key"]
    for line in summary:
        print(f"[migrate] {line}")
    print(f"[migrate] Work 신규 채번 {len(issued_rows)}건 · 재사용 {len(reuse)}건 소진 대상")

    if args.write:
        (REPO_ROOT / "ontology" / "rules").mkdir(parents=True, exist_ok=True)
        (REPO_ROOT / "ontology" / "wiring").mkdir(parents=True, exist_ok=True)
        (REPO_ROOT / "ontology" / "rules" / f"{doc_key}.ttl").write_text(rules_text, encoding="utf-8")
        (REPO_ROOT / "ontology" / "wiring" / f"{doc_key}.ttl").write_text(wiring_text, encoding="utf-8")
        with open(REPO_ROOT / "ontology" / "ISSUED", "a", encoding="utf-8") as f:
            for row in issued_rows:
                f.write(row + "\n")
        with open(REPO_ROOT / "ontology" / "LEDGER.tsv", "a", encoding="utf-8", newline="") as f:
            wcsv = csv.writer(f, delimiter="\t", lineterminator="\n")
            for r in ledger_rows:
                wcsv.writerow(r)
        print(f"[migrate] rules/{doc_key}.ttl · wiring/{doc_key}.ttl · ISSUED+{len(issued_rows)} · LEDGER+{len(ledger_rows)} 기록")
    else:
        print("[migrate] (dry) --write 로 기록")
    return 0


if __name__ == "__main__":
    sys.exit(main())
