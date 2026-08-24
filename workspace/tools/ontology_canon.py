"""정본 Turtle 직렬화기 (T0 A5) — 규칙 명세: workspace/tools/ontology-authoring.md §3.

정렬: 접두(접두명 순) → 주어(IRI 코드포인트 순) → 술어(rdf:type 우선, 이후 IRI 순) → 목적어(토큰 순).
blank node: SHACL 리스트 인자의 cons 셀만 허용(«( … )» 인라인) — 그 외는 CanonError.
직렬화 규칙 변경 시 CANON_VERSION 증가 + 전 코퍼스 재직렬화 전용 커밋(authoring §4).

.venv 파이썬 전용(rdflib·rdfcanon 의존 — E7 배포 경계).
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path

from rdflib import BNode, Dataset, Graph, Literal, URIRef
from rdflib.namespace import RDF, XSD

CANON_VERSION = "canon/1"

REPO_ROOT = Path(__file__).resolve().parents[2]
PREFIXES_TTL = REPO_ROOT / "ontology" / "prefixes.ttl"
VANN_PREFIX = URIRef("http://purl.org/vocab/vann/preferredNamespacePrefix")
VANN_URI = URIRef("http://purl.org/vocab/vann/preferredNamespaceUri")

SHACL_LIST_PREDICATES = frozenset(
    URIRef("http://www.w3.org/ns/shacl#" + local)
    for local in ("in", "or", "and", "xone", "languageIn", "ignoredProperties")
)

PN_LOCAL_SAFE = re.compile(r"[0-9A-Za-z_-]+$")
INTEGER_LEXICAL = re.compile(r"[+-]?[0-9]+$")

ECHAR = {
    "\\": "\\\\",
    '"': '\\"',
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
    "\b": "\\b",
    "\f": "\\f",
}


class CanonError(Exception):
    """정본 직렬화 불능 — {node} 필드로 위치를 보고한다."""

    def __init__(self, reason: str, node: str = "") -> None:
        super().__init__(reason)
        self.reason = reason
        self.node = node


# §14 폐쇄 인코딩 집합 — fragment 세그먼트의 percent-encoding 대상 문자(% 자기 포함·가역).
ENCODE_CHARS = set(' #%`<>"{}|\\^') | {chr(c) for c in range(0x20)} | {chr(c) for c in range(0x7F, 0xA0)}


def frag_encode(segment: str) -> str:
    """§14 폐쇄 인코딩(대문자 hex 정규형) — frag_encode(unquote(x)) == x 가 정규형 판정."""
    out = []
    for ch in segment:
        if ch in ENCODE_CHARS:
            out.extend(f"%{b:02X}" for b in ch.encode("utf-8"))
        else:
            out.append(ch)
    return "".join(out)


def load_prefix_registry(path: Path = PREFIXES_TTL) -> dict[str, str]:
    """prefixes.ttl의 vann 등재 (접두 → 네임스페이스 IRI). 등재 무결성도 검사."""
    g = Graph()
    g.parse(path, format="turtle")
    registry: dict[str, str] = {}
    for ns_iri, _, prefix_lit in g.triples((None, VANN_PREFIX, None)):
        uri_lit = g.value(ns_iri, VANN_URI)
        if uri_lit is None or str(uri_lit) != str(ns_iri):
            raise CanonError(
                f"vann 등재 불일치 — 주어 {ns_iri} 와 preferredNamespaceUri 가 문자 단위로 일치해야 한다",
                node=str(ns_iri),
            )
        prefix = str(prefix_lit)
        if prefix in registry and registry[prefix] != str(ns_iri):
            raise CanonError(f"접두 중복 등재: {prefix}", node=str(ns_iri))
        registry[prefix] = str(ns_iri)
    return registry


def _escape_literal(text: str) -> str:
    out = []
    for ch in text:
        if ch in ECHAR:
            out.append(ECHAR[ch])
        elif ord(ch) < 0x20 or ord(ch) == 0x7F:
            out.append(f"\\u{ord(ch):04X}")
        else:
            out.append(ch)
    return "".join(out)


class CanonSerializer:
    def __init__(self, graph: Graph, registry: dict[str, str], allow_lists: bool) -> None:
        self.g = graph
        self.registry = sorted(registry.items(), key=lambda kv: -len(kv[1]))
        self.allow_lists = allow_lists
        self.used_prefixes: set[str] = set()
        self.list_heads: dict[BNode, list] = {}
        self.consumed_cells: set[BNode] = set()

    def _collect_lists(self) -> None:
        """well-formed RDF 컬렉션(cons 셀 사슬)을 수집 — 그 외 blank node는 오류."""
        bnodes = set()
        for s, p, o in self.g:
            for term in (s, o):
                if isinstance(term, BNode):
                    bnodes.add(term)
        if not bnodes:
            return
        if not self.allow_lists:
            raise CanonError("blank node 금지(rules/·wiring/·vocab/ — E4)", node=str(next(iter(bnodes))))

        incoming: dict[BNode, list] = {b: [] for b in bnodes}
        for s, p, o in self.g:
            if isinstance(o, BNode):
                incoming[o].append((s, p))

        heads = [b for b in bnodes if not any(p == RDF.rest for _, p in incoming[b])]
        for head in heads:
            refs = incoming[head]
            if len(refs) != 1 or refs[0][1] not in SHACL_LIST_PREDICATES:
                raise CanonError(
                    "blank node 는 SHACL 리스트 인자의 cons 셀만 허용(E4) — "
                    f"허용 술어 밖 참조: {refs[0][1] if refs else '무참조'}",
                    node=str(head),
                )
            items, cells, cur = [], [], head
            while cur != RDF.nil:
                if not isinstance(cur, BNode):
                    raise CanonError("리스트 cons 셀이 blank node 가 아님", node=str(cur))
                firsts = list(self.g.objects(cur, RDF.first))
                rests = list(self.g.objects(cur, RDF.rest))
                others = [(p, o) for p, o in self.g.predicate_objects(cur) if p not in (RDF.first, RDF.rest)]
                if len(firsts) != 1 or len(rests) != 1 or others:
                    raise CanonError("리스트 cons 셀 형상 불량(first/rest 각 1 필요)", node=str(cur))
                if isinstance(firsts[0], BNode):
                    raise CanonError("중첩 리스트 금지 — 리스트 항은 IRI/리터럴만", node=str(cur))
                items.append(firsts[0])
                cells.append(cur)
                cur = rests[0]
            self.list_heads[head] = items
            self.consumed_cells.update(cells)

        leftovers = bnodes - set(self.list_heads) - self.consumed_cells
        if leftovers:
            raise CanonError(
                "cons 셀 사슬에 속하지 않는 blank node — 셰이프 노드는 IRI 의무(E4)",
                node=str(next(iter(leftovers))),
            )

    def _iri(self, term: URIRef) -> str:
        iri = unicodedata.normalize("NFC", str(term))
        for prefix, ns in self.registry:
            if iri.startswith(ns):
                local = iri[len(ns):]
                if local and PN_LOCAL_SAFE.fullmatch(local):
                    self.used_prefixes.add(prefix)
                    return f"{prefix}:{local}"
        return f"<{iri}>"

    def _literal(self, term: Literal) -> str:
        lex = _escape_literal(unicodedata.normalize("NFC", str(term)))
        if term.language:
            return f'"{lex}"@{term.language.lower()}'
        if term.datatype and term.datatype != XSD.string:
            if term.datatype == XSD.integer and INTEGER_LEXICAL.fullmatch(str(term)):
                return str(term)
            if term.datatype == XSD.boolean and str(term) in ("true", "false"):
                return str(term)
            return f'"{lex}"^^{self._iri(term.datatype)}'
        return f'"{lex}"'

    def _object(self, term) -> str:
        if isinstance(term, BNode):
            if term in self.list_heads:
                inner = " ".join(self._object(i) for i in self.list_heads[term])
                return f"( {inner} )" if inner else "( )"
            raise CanonError("직렬화 불능 blank node", node=str(term))
        if isinstance(term, Literal):
            return self._literal(term)
        return self._iri(term)

    def serialize(self) -> str:
        self._collect_lists()
        blocks: dict[str, dict] = {}
        for s, p, o in self.g:
            if isinstance(s, BNode):
                if s in self.consumed_cells or s in self.list_heads:
                    continue
                raise CanonError("주어 자리 blank node 금지", node=str(s))
            key = unicodedata.normalize("NFC", str(s))
            entry = blocks.setdefault(key, {"subject": s, "preds": {}})
            entry["preds"].setdefault(p, []).append(o)

        body_parts: list[str] = []
        for key in sorted(blocks):
            entry = blocks[key]
            subj_tok = self._iri(entry["subject"])
            pred_items = []
            for p, objects in entry["preds"].items():
                pred_key = (0, "") if p == RDF.type else (1, unicodedata.normalize("NFC", str(p)))
                pred_tok = "a" if p == RDF.type else self._iri(p)
                obj_toks = sorted(self._object(o) for o in objects)
                pred_items.append((pred_key, pred_tok, obj_toks))
            pred_items.sort(key=lambda t: t[0])

            lines = []
            for idx, (_, pred_tok, obj_toks) in enumerate(pred_items):
                sep = " ;" if idx < len(pred_items) - 1 else " ."
                joined = ", ".join(obj_toks)
                if idx == 0:
                    lines.append(f"{subj_tok} {pred_tok} {joined}{sep}")
                else:
                    lines.append(f"    {pred_tok} {joined}{sep}")
            body_parts.append("\n".join(lines))

        prefix_lines = [
            f"@prefix {prefix}: <{ns}> ."
            for prefix, ns in sorted((p, n) for p, n in dict(self.registry).items() if p in self.used_prefixes)
        ]
        sections = []
        if prefix_lines:
            sections.append("\n".join(prefix_lines))
        sections.extend(body_parts)
        return "\n\n".join(sections) + "\n"


def canon_turtle(graph: Graph, registry: dict[str, str], allow_lists: bool) -> str:
    return CanonSerializer(graph, registry, allow_lists).serialize()


def rdfc10_hash(graph: Graph) -> str:
    """RDFC-1.0 정본화(rdfcanon) 후 sha256 — 게이트 ③의 트리플 집합 불변 증명."""
    import contextlib
    import io

    from rdfcanon import RDFCanon, RDFCanonTimeTicker

    ds = Dataset()
    for triple in graph:
        ds.add(triple)
    # RDFCanonTimeTicker 의 max_time 단위는 **밀리초**(time_ns/1e6 대비 비교)다 — 60.0 은
    # 의도(60초)와 달리 60ms 예산이라, 게이트 병렬 워커 경합에서 djr-shapes(bnode 13·
    # 무부하 12ms)의 canonize 가 비결정적으로 TimeoutError 를 냈다(2026-08-24 릴리즈 실측).
    # 60초로 교정 — 독(poison) 그래프 가드로는 여전히 유효(정상 최대 대비 수천 배 여유).
    canon = RDFCanon("sha256", ds, RDFCanonTimeTicker(60_000.0))
    with contextlib.redirect_stdout(io.StringIO()):
        text = canon.canonize()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
