"""4단 저작 게이트 (T0 A5 — 블루프린트 E4).

① 파스(rdflib) → ② 정본 직렬화 diff=0(+NFC·접두 등재 대조·blank node 정책)
→ ③ RDFC-1.0 해시 전후 비교(트리플 집합 불변) → ④ SHACL(pySHACL -i none,
데이터 그래프 = 대상 파일+vocab+wiring 병합 — E2, 판정은 리포트 그래프 질의 severity 별).

shapes/golden/ 은 ①~③만 적용(④는 골든 하네스가 기대 판정 대조 — E4).
실패 시 구조화 되먹임 리포트(gate-report/1)를 --json 으로 방출 — LLM 수리 루프 재료.

사용: .venv/bin/python workspace/tools/ontology_gate.py [--write] [--json] [파일…]
      (파일 생략 시 ontology/ 전체) · exit 0 green / 1 red / 2 도구 오류
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

from ontology_canon import (
    REPO_ROOT,
    CanonError,
    canon_turtle,
    load_prefix_registry,
    rdfc10_hash,
)

DEFAULT_ROOT = REPO_ROOT / "ontology"
LIST_ALLOWED_DIRS = ("shapes",)
PREFIX_DECL = re.compile(r"^@prefix\s+([A-Za-z][\w.-]*):\s*<([^>]*)>\s*\.\s*$")
SEVERITY_QUERY = """
SELECT ?severity (COUNT(?result) AS ?n) WHERE {
    ?report <http://www.w3.org/ns/shacl#result> ?result .
    ?result <http://www.w3.org/ns/shacl#resultSeverity> ?severity .
} GROUP BY ?severity
"""
VIOLATION_DETAIL_QUERY = """
SELECT ?focus ?shape ?message WHERE {
    ?report <http://www.w3.org/ns/shacl#result> ?result .
    ?result <http://www.w3.org/ns/shacl#resultSeverity> <http://www.w3.org/ns/shacl#Violation> .
    OPTIONAL { ?result <http://www.w3.org/ns/shacl#focusNode> ?focus . }
    OPTIONAL { ?result <http://www.w3.org/ns/shacl#sourceShape> ?shape . }
    OPTIONAL { ?result <http://www.w3.org/ns/shacl#resultMessage> ?message . }
} ORDER BY ?focus ?shape LIMIT 20
"""


def target_files(args: list[str], root: Path) -> list[Path]:
    if args:
        return [Path(a).resolve() for a in args]
    return sorted(p for p in root.rglob("*.ttl"))


def allow_lists(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    return bool(rel.parts) and rel.parts[0] in LIST_ALLOWED_DIRS


def is_golden(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root / "shapes" / "golden")
        return True
    except ValueError:
        return False


def check_prefix_decls(source: str, registry: dict[str, str]) -> list[dict]:
    errors = []
    for line in source.splitlines():
        if not line.startswith("@prefix"):
            continue
        m = PREFIX_DECL.match(line)
        if not m:
            errors.append({"node": line.strip(), "reason": "@prefix 선언 형식 불량"})
            continue
        prefix, ns = m.group(1), m.group(2)
        if registry.get(prefix) != ns:
            errors.append(
                {
                    "node": f"{prefix}: <{ns}>",
                    "reason": "미등록(또는 불일치) 접두사 — prefixes.ttl vann 등재 쌍과 정확 일치 필요",
                }
            )
    return errors


def merged_data_graph(file_graph, path: Path, root: Path):
    from rdflib import Graph

    merged = Graph()
    for triple in file_graph:
        merged.add(triple)
    for extra_dir in (root / "vocab", root / "wiring"):
        for extra in sorted(extra_dir.glob("*.ttl")):
            if extra.resolve() == path.resolve():
                continue
            merged.parse(extra, format="turtle")
    return merged


def shapes_graph(root: Path):
    from rdflib import Graph

    g = Graph()
    found = False
    for shp in sorted((root / "shapes").glob("*.ttl")):
        g.parse(shp, format="turtle")
        found = True
    return g if found else None


def run_gate(path: Path, registry: dict[str, str], write: bool, root: Path) -> dict:
    import os

    from rdflib import Graph

    try:
        rel = str(path.relative_to(REPO_ROOT))
    except ValueError:
        rel = str(path)
    result = {"file": rel, "stages": [], "verdict": "pass"}

    def stage(name: str, errors: list[dict]) -> bool:
        status = "fail" if errors else "pass"
        result["stages"].append({"stage": name, "status": status, "errors": errors})
        if errors:
            result["verdict"] = "fail"
        return not errors

    source = path.read_text(encoding="utf-8")

    g = Graph()
    try:
        g.parse(data=source, format="turtle")
    except Exception as exc:
        stage("1-parse", [{"node": "", "reason": f"Turtle 파스 실패: {exc}"}])
        return result
    stage("1-parse", [])

    errors2: list[dict] = []
    if not unicodedata.is_normalized("NFC", source):
        errors2.append({"node": "", "reason": "유니코드 NFC 위반(authoring §3)"})
    errors2.extend(check_prefix_decls(source, registry))
    canon_text = None
    try:
        canon_text = canon_turtle(g, registry, allow_lists=allow_lists(path, root))
    except CanonError as exc:
        errors2.append({"node": exc.node, "reason": exc.reason})
    if canon_text is not None:
        if write and canon_text != source:
            path.write_text(canon_text, encoding="utf-8")
            source = canon_text
        if canon_text != source:
            errors2.append(
                {"node": "", "reason": "정본 직렬화 diff≠0 — --write 로 정본형 재작성 가능"}
            )
    if not stage("2-canon", errors2):
        return result

    if os.environ.get("ONTOLOGY_GATE_FAULT") == "hash-mutation":
        canon_text = canon_text + "<https://numchida.com/ns/djr#fault-injected> <https://numchida.com/ns/djr#kind> <https://numchida.com/ns/djr#kind-prose> .\n"
    reparsed = Graph()
    reparsed.parse(data=canon_text, format="turtle")
    h_before, h_after = rdfc10_hash(g), rdfc10_hash(reparsed)
    stage(
        "3-hash",
        []
        if h_before == h_after
        else [{"node": "", "reason": f"RDFC-1.0 해시 불일치 — 재직렬화가 트리플 집합을 바꿈({h_before[:12]}≠{h_after[:12]})"}],
    )
    if result["verdict"] == "fail":
        return result

    if is_golden(path, root):
        return result

    shp = shapes_graph(root)
    if shp is None or len(shp) == 0:
        stage("4-shacl", [])
        return result

    from pyshacl import validate

    data = merged_data_graph(g, path, root)
    _, report_graph, _ = validate(
        data_graph=data, shacl_graph=shp, inference="none", advanced=True
    )
    errors4 = []
    violation_total = 0
    for severity, n in report_graph.query(SEVERITY_QUERY):
        if str(severity).rsplit("#", 1)[-1] == "Violation":
            violation_total = int(n)
    if violation_total:
        for focus, shape, message in report_graph.query(VIOLATION_DETAIL_QUERY):
            errors4.append(
                {
                    "node": str(focus) if focus else "",
                    "reason": f"SHACL 위반 [{str(shape) if shape else '?'}]: {str(message) if message else '(메시지 없음)'}",
                }
            )
        if violation_total > len(errors4):
            errors4.append({"node": "", "reason": f"…외 sh:Violation {violation_total - len(errors4)}건(상한 20 초과분)"})
    stage("4-shacl", errors4)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="온톨로지 4단 저작 게이트")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--write", action="store_true", help="정본형으로 파일 재작성(저작 도우미)")
    ap.add_argument("--json", action="store_true", help="gate-report/1 JSON 방출(수리 루프 재료)")
    ap.add_argument("--root", default=str(DEFAULT_ROOT), help="온톨로지 트리 루트(스모크용 임시 트리 지원)")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    try:
        registry = load_prefix_registry(root / "prefixes.ttl")
    except Exception as exc:
        print(f"[ontology-gate] 도구 오류: prefixes.ttl 등재 로드 실패 — {exc}")
        return 2

    results = [run_gate(p, registry, args.write, root) for p in target_files(args.files, root)]
    report = {"schema": "gate-report/1", "results": results}
    failed = [r for r in results if r["verdict"] == "fail"]

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for r in results:
            mark = "green" if r["verdict"] == "pass" else "RED"
            print(f"[ontology-gate] {mark:5} {r['file']}")
            for st in r["stages"]:
                for err in st["errors"]:
                    node = f" [{err['node']}]" if err["node"] else ""
                    print(f"    {st['stage']}{node}: {err['reason']}")
    print(f"[ontology-gate] {len(results)}파일 — green {len(results) - len(failed)} · red {len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
