"""온톨로지 도구 사슬 스모크 — verify-ontology 선두 [0] (T0 A1).

검사 항목:
  1. 인터프리터 버전(3.14.x — ontology-requirements.txt 확정)
  2. rdflib·pySHACL·rdfcanon 임포트 + 설치 버전 == 고정 버전
  3. RDFC-1.0 정합 벡터 3종(W3C rdf-canon 스위트 발췌 — 지면/이중 링크/다이아몬드 N-Degree)
  4. pySHACL 마이크로 검증 1회(conforms 왕복)

exit 0 = green · exit 1 = 도구 사슬 이상(블루프린트 §7: 게이트 도구 고장 시 편집 불능 방지).
.venv 파이썬으로 실행한다: .venv/bin/python workspace/tools/ontology_env_smoke.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_PYTHON = (3, 14)
REQ_FILE = Path(__file__).with_name("ontology-requirements.txt")
CHECKED = ("rdflib", "pyshacl", "rdfcanon")

RDFC_VECTORS = [
    (
        "ground triple",
        "sha256",
        '<http://example.org/test#example1> <http://example.org/vocab#p> <http://example.org/test#example2> .\n',
        '<http://example.org/test#example1> <http://example.org/vocab#p> <http://example.org/test#example2> .\n',
    ),
    (
        "blank node dual link",
        "sha256",
        '<http://example.org/test> <http://example.org/vocab#A> _:e0 .\n'
        '<http://example.org/test> <http://example.org/vocab#B> _:e0 .\n'
        '<http://example.org/test> <http://example.org/vocab#embed> _:e0 .\n',
        '<http://example.org/test> <http://example.org/vocab#A> _:c14n0 .\n'
        '<http://example.org/test> <http://example.org/vocab#B> _:c14n0 .\n'
        '<http://example.org/test> <http://example.org/vocab#embed> _:c14n0 .\n',
    ),
    (
        "blank node diamond (N-Degree)",
        "sha256",
        '<http://example.org/vocab#test> <http://example.org/vocab#A> _:e0 .\n'
        '<http://example.org/vocab#test> <http://example.org/vocab#B> _:e1 .\n'
        '_:e0 <http://example.org/vocab#next> _:e2 .\n'
        '_:e1 <http://example.org/vocab#next> _:e2 .\n',
        '<http://example.org/vocab#test> <http://example.org/vocab#A> _:c14n2 .\n'
        '<http://example.org/vocab#test> <http://example.org/vocab#B> _:c14n0 .\n'
        '_:c14n0 <http://example.org/vocab#next> _:c14n1 .\n'
        '_:c14n2 <http://example.org/vocab#next> _:c14n1 .\n',
    ),
]

SHACL_SHAPES = """\
@prefix ex: <http://example.org/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
ex:PersonShape a sh:NodeShape ;
    sh:targetClass ex:Person ;
    sh:property ex:PersonShape-name .
ex:PersonShape-name a sh:PropertyShape ;
    sh:path ex:name ;
    sh:minCount 1 .
"""
SHACL_DATA_GREEN = """\
@prefix ex: <http://example.org/> .
ex:alice a ex:Person ; ex:name "alice" .
"""
SHACL_DATA_RED = """\
@prefix ex: <http://example.org/> .
ex:bob a ex:Person .
"""


def fail(msg: str) -> None:
    print(f"[ontology-env-smoke] FAIL: {msg}")
    sys.exit(1)


def pinned_versions() -> dict[str, str]:
    pins: dict[str, str] = {}
    for line in REQ_FILE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+)==(\S+)$", line.strip())
        if m:
            pins[m.group(1).lower()] = m.group(2)
    return pins


def check_python() -> None:
    if sys.version_info[:2] != REQUIRED_PYTHON:
        fail(
            f"파이썬 {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}.x 필요 — 현재 {sys.version.split()[0]}. "
            "make ontology-env 로 .venv 를 재구축하고 .venv/bin/python 으로 실행하라."
        )


def check_imports_and_versions() -> None:
    from importlib.metadata import version as dist_version

    pins = pinned_versions()
    for mod in CHECKED:
        try:
            __import__(mod)
        except ImportError as exc:
            fail(f"{mod} 임포트 실패({exc}) — make ontology-env 실행 필요")
        installed = dist_version(mod)
        if pins.get(mod) and installed != pins[mod]:
            fail(f"{mod} 버전 불일치 — 설치 {installed} ≠ 고정 {pins[mod]} (ontology-requirements.txt)")


def check_rdfc10() -> None:
    import contextlib
    import io

    from rdfcanon import RDFCanon, RDFCanonTimeTicker
    from rdflib import Dataset

    for name, algo, src, expected in RDFC_VECTORS:
        ds = Dataset()
        ds.parse(data=src, format="nquads")
        canon = RDFCanon(algo, ds, RDFCanonTimeTicker(30.0))
        with contextlib.redirect_stdout(io.StringIO()):
            got = canon.canonize()
        if got != expected:
            fail(f"RDFC-1.0 벡터 «{name}» 불일치:\n--- got ---\n{got}--- expected ---\n{expected}")


def check_pyshacl() -> None:
    from pyshacl import validate
    from rdflib import Graph

    shapes = Graph().parse(data=SHACL_SHAPES, format="turtle")
    for data_ttl, expect in ((SHACL_DATA_GREEN, True), (SHACL_DATA_RED, False)):
        data = Graph().parse(data=data_ttl, format="turtle")
        conforms, _, _ = validate(data_graph=data, shacl_graph=shapes, inference="none")
        if conforms is not expect:
            fail(f"pySHACL 왕복 이상 — conforms={conforms}, 기대 {expect}")


def main() -> None:
    check_python()
    check_imports_and_versions()
    check_rdfc10()
    check_pyshacl()
    print("[ontology-env-smoke] OK — python·rdflib·pySHACL·rdfcanon 사슬 green")


if __name__ == "__main__":
    main()
