"""동일 방향 관계를 JSON 인접 목록과 RDF/SPARQL로 조회하는 실험이다."""

import json
import platform
from statistics import median
from time import perf_counter
from urllib.parse import quote

import rdflib
from rdflib import Graph, RDF, URIRef
from rdflib.plugins.sparql import prepareQuery


def _reachable(adjacency: dict[str, list[str]], seed: str) -> list[str]:
    visited = {seed}
    pending = [seed]
    while pending:
        for target in adjacency[pending.pop()]:
            if target not in visited:
                visited.add(target)
                pending.append(target)
    return sorted(visited)


def benchmark(
    nodes: list[str],
    edges: list[tuple[str, str]],
    seeds: list[str],
    repeats: int = 30,
) -> dict:
    """신규 메모리 구조의 준비 비용과 준비된 전체 seed 묶음의 조회를 잰다."""
    started = perf_counter()
    node_ids = sorted(set(nodes))
    directed_edges = sorted(set(edges))
    seed_ids = list(dict.fromkeys(seeds))
    known_nodes = set(node_ids)
    if repeats < 1 or not seed_ids:
        raise ValueError("측정에는 양수 반복 수와 하나 이상의 seed가 필요하다")
    if not set(seed_ids) <= known_nodes:
        raise ValueError("모든 seed는 nodes에 포함되어야 한다")
    if any(source not in known_nodes or target not in known_nodes
           for source, target in directed_edges):
        raise ValueError("모든 관계 끝점은 nodes에 포함되어야 한다")
    normalization_ms = (perf_counter() - started) * 1000

    started = perf_counter()
    adjacency = {node: [] for node in node_ids}
    for source, target in directed_edges:
        adjacency[source].append(target)
    json_build_ms = (perf_counter() - started) * 1000
    started = perf_counter()
    json_bytes = json.dumps(adjacency, ensure_ascii=False, separators=(",", ":")).encode()
    json_serialize_ms = (perf_counter() - started) * 1000
    started = perf_counter()
    loaded_adjacency = json.loads(json_bytes)
    json_parse_ms = (perf_counter() - started) * 1000

    started = perf_counter()
    node_uris = {node: URIRef("urn:spec-node:" + quote(node, safe="")) for node in node_ids}
    uri_ids = {uri: node for node, uri in node_uris.items()}
    relation = URIRef("urn:spec-bench:depends-on")
    graph = Graph()
    for uri in node_uris.values():
        graph.add((uri, RDF.type, URIRef("urn:spec-bench:Node")))
    for source, target in directed_edges:
        graph.add((node_uris[source], relation, node_uris[target]))
    rdf_build_ms = (perf_counter() - started) * 1000
    started = perf_counter()
    rdf_bytes = graph.serialize(format="turtle", encoding="utf-8")
    rdf_serialize_ms = (perf_counter() - started) * 1000
    started = perf_counter()
    loaded_graph = Graph().parse(data=rdf_bytes, format="turtle")
    rdf_parse_ms = (perf_counter() - started) * 1000
    started = perf_counter()
    query = prepareQuery(
        "SELECT DISTINCT ?node WHERE { ?seed <urn:spec-bench:depends-on>* ?node . }"
    )
    query_prepare_ms = (perf_counter() - started) * 1000

    def query_json() -> dict[str, list[str]]:
        return {seed: _reachable(loaded_adjacency, seed) for seed in seed_ids}

    def query_sparql() -> dict[str, list[str]]:
        return {
            seed: sorted({
                uri_ids[row[0]]
                for row in loaded_graph.query(query, initBindings={"seed": node_uris[seed]})
            })
            for seed in seed_ids
        }

    queries = {"json": query_json, "sparql": query_sparql}
    results = {}
    warmup_ms = {}
    for engine, execute in queries.items():
        started = perf_counter()
        results[engine] = execute()
        warmup_ms[engine] = (perf_counter() - started) * 1000
    samples = {engine: [] for engine in queries}
    for trial in range(repeats):
        order = ("json", "sparql") if trial % 2 == 0 else ("sparql", "json")
        for engine in order:
            started = perf_counter()
            measured_result = queries[engine]()
            samples[engine].append((perf_counter() - started) * 1000)
            if measured_result != results[engine]:
                raise RuntimeError("같은 관계의 반복 조회 결과가 달라졌다")
    per_seed = {
        seed: {
            "json": results["json"][seed],
            "sparql": results["sparql"][seed],
            "equivalent": results["json"][seed] == results["sparql"][seed],
        }
        for seed in seed_ids
    }
    return {
        "environment": {
            "python": platform.python_version(),
            "rdflib": rdflib.__version__,
            "platform": platform.platform(),
        },
        "node_count": len(node_ids),
        "edge_count": len(directed_edges),
        "rdf_triple_count": len(loaded_graph),
        "seeds": seed_ids,
        "repeats": repeats,
        "results": per_seed,
        "exact_equivalence": all(result["equivalent"] for result in per_seed.values()),
        "preparation": {
            "normalization_ms": normalization_ms,
            "json": {
                "build_ms": json_build_ms,
                "serialize_ms": json_serialize_ms,
                "parse_ms": json_parse_ms,
                "query_prepare_ms": 0.0,
                "serialized_bytes": len(json_bytes),
            },
            "rdf": {
                "build_ms": rdf_build_ms,
                "serialize_ms": rdf_serialize_ms,
                "parse_ms": rdf_parse_ms,
                "query_prepare_ms": query_prepare_ms,
                "serialized_bytes": len(rdf_bytes),
            },
        },
        "warm_queries": {
            engine: {
                "warmup_ms": warmup_ms[engine],
                "samples_ms": timings,
                "median_ms": median(timings),
                "min_ms": min(timings),
                "max_ms": max(timings),
            }
            for engine, timings in samples.items()
        },
        "measurement_notes": [
            "Preparation is one fresh in-memory build/serialize/parse per engine; not a process-cold measurement.",
            "Python startup and imports are excluded and were not measured by this module.",
            "Each warm sample evaluates all unique seeds and fully materializes sorted, deduplicated original IDs.",
            "One untimed-for-summary warmup batch per engine precedes alternating engine order across repeats.",
            "RDF type triples preserve isolated nodes; only depends-on triples are traversed in either representation.",
            "Node, edge and seed duplicates are removed before both engines receive the same inputs.",
            "These in-process microbenchmarks do not measure agent latency, token usage, code quality or semantic graph construction.",
        ],
    }
