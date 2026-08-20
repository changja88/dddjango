#!/usr/bin/env python3
"""규칙 팩 생성기 — 그래프(SPARQL) → 무의존 인덱스 JSON (T2-4 · .venv 전용).

**왜 빌드타임인가**(동결 E7 배포 경계): rdflib·pySHACL 은 메인테이너 저장소 전용이고 설치본에
침투하지 않는다. 실런 3암은 **설치 cache 에서 로드**되므로 런타임에 rdflib 를 요구하면 C암만
실행 환경이 달라져 처치 밖 교란이 된다. 그래서 여기서 팩을 사전 렌더하고, 설치본은
`dddjango/scripts/rulepack.py`(표준 라이브러리)로 **조회만** 한다.

**팩에 규범 본문은 없다**(동결 E8 · 절차 정본 step 6′ · 개정 8). 싣는 것은 구조 인덱스와
**명칭**(`skos:prefLabel` — E5 가 «명칭만»으로 못박은 필드)뿐이다. 블록 리터럴이 팩에 존재하지
않으므로 코드가 실수해도 실을 본문이 없다.

**정렬은 생성기가 소유한다**: `order_rank`(0..N-1 정수)를 미리 박아 넣는다. 소비자가 절 번호를
다시 자연 정렬하면 두 구현이 갈라질 수 있어서다 — 팩이 순서의 단일 출처다.

**결정성**: 같은 그래프 → byte 동일 팩. 배열은 전부 명시 정렬 키를 갖는다(`sort_keys=True` 는
객체 키만 정렬하고 배열은 건드리지 않는다 — T2-4 적대 리뷰 AQ-11).

사용: .venv/bin/python workspace/tools/ontology_rulepack.py [--out <json>] [--check] [--quiet]
exit 0 = 정상 / 2 = `--check` 표류 또는 fail-closed 위반 / 1 = 재료 결손·사용 오류
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from ontology_canon import REPO_ROOT

SCHEMA: str = "rulepack/1"
GENERATED_BY: str = "ontology_rulepack.py — 직접 편집 금지(투영물 · 정본은 ontology/ 그래프)"
QUERIES: Path = REPO_ROOT / "workspace" / "tools" / "queries"
GRAPH_DIRS: "tuple[str, str, str]" = ("rules", "wiring", "vocab")
DEFAULT_OUT: Path = REPO_ROOT / "dddjango" / "scripts" / "rulepack.json"
MIRROR_OUT: Path = (REPO_ROOT / "codex-dddjango" / "skills" / "dddjango"
                    / "scripts" / "rulepack.json")
SEP: str = ";"   # GROUP_CONCAT 구분자 — 값에 섞이면 fail-closed
_WORK_RE: "re.Pattern[str]" = re.compile(r"R-\d{4}\Z")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _graph_files(root: Path) -> "list[Path]":
    out: "list[Path]" = []
    for sub in GRAPH_DIRS:
        out.extend(sorted((root / "ontology" / sub).glob("*.ttl")))
    if not out:
        raise FileNotFoundError(f"재료 결손: {root}/ontology 에 정본 ttl 이 없다")
    return out


def _natural(text: str) -> "tuple":
    """절 번호 자연 정렬 키 — "3.2" → (3, 2) · "10" → (10,).

    사전순이면 "10" < "8" 이 된다. 파일럿 4절은 우연히 사전순도 맞지만 T3 에서 §10 이 생기면
    조용히 어긋난다 — 지금 닫는다. 숫자 아닌 성분은 (문자열, ) 로 밀어 뒤로 보낸다.
    """
    parts: "list" = []
    for chunk in str(text).split("."):
        parts.append((0, int(chunk)) if chunk.isdigit() else (1, chunk))
    return tuple(parts)


def _split(value: str) -> "list[str]":
    return [v for v in str(value).split(SEP) if v]


_KIND_PREFIX: "re.Pattern[str]" = re.compile(r"\A[a-z]/")


def _local(iri: str) -> str:
    """IRI → 팩 키. fragment 를 떼고 **종별 접두 한 글자**(`c/`·`a/`·`d/`·`s/`)도 뗀다.

    검사기 키가 `c/check-domain-model.py` 로 남으면 위반 레코드의 `checker` 값
    (`Path(sys.argv[0]).name` = **bare filename**)과 영원히 맞지 않는다 — selector 가 조용히
    전건 tier 3(폴백)으로 흘러가고 로그에만 남는다. 접두를 여기서 한 번만 벗긴다.
    """
    return _KIND_PREFIX.sub("", str(iri).rsplit("#", 1)[-1])


def build(root: "Path | None" = None) -> "tuple[dict, list[str]]":
    """팩 dict + 리포트 행. rdflib 는 이 함수 안에서만 쓴다."""
    from rdflib import Graph

    base: Path = root or REPO_ROOT
    files: "list[Path]" = _graph_files(base)
    g = Graph()
    for f in files:
        g.parse(f, format="turtle")

    rows = list(g.query((QUERIES / "q4-injection-order.rq").read_text(encoding="utf-8")))

    works: "dict[str, dict]" = {}
    problems: "list[str]" = []
    ordered: "list[tuple]" = []
    for r in rows:
        work_iri: str = str(r.work)
        wid: str = _local(work_iri)
        if not _WORK_RE.fullmatch(wid):
            problems.append(f"채번 형식 밖 Work: {work_iri}")
            continue
        if wid in works:                                   # 한 Work = 한 블록 계약
            problems.append(f"Work {wid} 가 블록 2개 이상에서 진술된다 — 정렬 키가 모호하다")
            continue
        label: str = str(r.label)
        checkers: "list[str]" = sorted(_local(c) for c in _split(r.checkers))
        agents: "list[str]" = sorted(_local(a) for a in _split(r.agents))
        aliases: "list[str]" = sorted(_split(r.aliases))
        for field, values in (("checkers", checkers), ("aliases", aliases)):
            for v in values:
                if SEP in v:
                    problems.append(f"{wid}.{field} 값에 구분자 {SEP!r} 가 섞였다: {v!r}")
        works[wid] = {
            "label": label,
            "document": _local(str(r.document)),
            "section": _local(str(r.section)),
            "section_number": str(r.sectionNumber),
            "block": _local(str(r.block)),
            "block_order": int(r.blockOrder),
            "expression": str(r.expression) if r.expression is not None else None,
            "checkers": checkers,
            "agents": agents,
            "aliases": aliases,
        }
        ordered.append((str(r.document), _natural(str(r.sectionNumber)),
                        int(r.blockOrder), wid))

    for rank, (_, _, _, wid) in enumerate(sorted(ordered)):
        works[wid]["order_rank"] = rank

    by_alias: "dict[str, str]" = {}
    for wid, w in works.items():
        for alias in w["aliases"]:
            key: str = "#" + alias.split("#", 1)[1] if "#" in alias else alias
            if key in by_alias and by_alias[key] != wid:
                problems.append(f"alias {key} 가 {by_alias[key]}·{wid} 둘을 가리킨다(함수성 위반)")
                continue
            by_alias[key] = wid

    by_checker: "dict[str, list[str]]" = {}
    for wid, w in sorted(works.items(), key=lambda kv: kv[1]["order_rank"]):
        for checker in w["checkers"]:
            by_checker.setdefault(checker, []).append(wid)

    by_section: "dict[str, dict]" = {}
    for wid, w in sorted(works.items(), key=lambda kv: kv[1]["order_rank"]):
        entry = by_section.setdefault(w["section"], {"number": w["section_number"], "works": []})
        entry["works"].append(wid)

    # Q1 — 경로 축(**처치 밖 분석 카탈로그**: selector 는 이 인덱스를 쓰지 않는다).
    by_path: "list" = []
    for row in g.query((QUERIES / "q1-path-to-norms.rq").read_text(encoding="utf-8")):
        sec: str = _local(str(row.section))
        by_path.append({"glob": str(row.glob), "section": sec,
                        "works": list(by_section.get(sec, {}).get("works", []))})
    by_path.sort(key=lambda e: (e["glob"], e["section"]))

    pack: "dict" = {
        "_generated": GENERATED_BY,
        "by_path": by_path,
        "schema": SCHEMA,
        "built_from": [{"path": str(f.relative_to(base)), "sha256": _sha256(f)} for f in files],
        "works": works,
        "by_alias": by_alias,
        "by_checker": by_checker,
        "by_section": by_section,
    }

    unreached: "list[str]" = sorted(w for w, v in works.items() if not v["checkers"])
    report: "list[str]" = [
        f"[rulepack] Work {len(works)} · 검사기 {len(by_checker)} · alias {len(by_alias)} · 절 {len(by_section)}",
        f"[rulepack] 검사기 도달 불가 규범 {len(unreached)}건 — selector 진입로 없음(침묵 탈락 금지)",
        f"[rulepack] 재료 ttl {len(files)}개 · 본문(text) 미동봉 — 개정 8",
        f"[rulepack] 경로 글롭 {len(by_path)}건(Q1 — 처치 밖 카탈로그)",
    ]
    return pack, report + [f"[rulepack] RED {p}" for p in problems]


def dumps(pack: "dict") -> str:
    return json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description="규칙 팩 생성기(T2-4)")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--mirror", default=str(MIRROR_OUT),
                    help="codex 미러 경로(--check 에서도 대조한다)")
    ap.add_argument("--check", action="store_true",
                    help="쓰지 않고 커밋본과 byte 대조만 — verify 상시 검사용")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    try:
        pack, report = build()
    except FileNotFoundError as exc:
        print(f"[rulepack] 재료 결손: {exc}", file=sys.stderr)
        return 1
    text: str = dumps(pack)
    red: "list[str]" = [line for line in report if " RED " in line]
    if not args.quiet:
        for line in report:
            print(line)
    if red:
        return 2

    targets: "list[Path]" = [Path(args.out), Path(args.mirror)]
    if args.check:
        drift: "list[str]" = []
        for t in targets:
            if not t.is_file():
                drift.append(f"{t} 부재 — `make rulepack` 미실행")
            elif t.read_text(encoding="utf-8") != text:
                drift.append(f"{t} 가 그래프와 어긋난다(팩 노후 또는 수기 편집)")
        for d in drift:
            print(f"[rulepack] RED {d}")
        if drift:
            return 2
        print("[rulepack] 정합 — 팩 == render(그래프) · 양 런타임 미러 동일")
        return 0

    for t in targets:
        t.write_text(text, encoding="utf-8")
        print(f"[rulepack] 기록 {t.relative_to(REPO_ROOT)} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
