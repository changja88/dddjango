#!/usr/bin/env python3
"""위반 그래프 어댑터 — findings/0 jsonl → `djr:Violation` Turtle (T2-2 · .venv 전용).

t2-plan §T2-2 «위반 그래프 어댑터»의 최소 경로. **조인 성립분만 적재**한다:
레코드의 `rule`(무접두 `#N`)을 alias 대장(`ontology/wiring/aliases.ttl` — `aliasText "rule#N"`)
으로 Work 에 조인하고, 그 Work 의 `currentExpression` 을 `violatesExpression` 으로 쓴다.

**미조인분은 적재하지 않는다**(설계 노트 `2026-08-20-ontology-t2-2-violation-adapter.md` §1):
`ViolationShape` 가 `violatesWork`/`violatesExpression` 을 `minCount 1` 로 요구하므로 선행 계약
(rule=null+contract_ref)·미이관 `#N`·가드 센티널은 **현행 셰이프로는 노드를 만들 수 없다**.
그 처분(셰이프 개정 A안 등)은 확정 전이며, 여기서는 **계수로만 보고**한다(침묵 탈락 금지).

violation_id = (**실런** × Work × 라인 제거 경로 × 심볼) — 심볼 부재 시 (…× 파일)로 강등(L-M #12).
노드 IRI 는 그 넷의 sha16 이라 **재실행 결정성**을 갖는다(같은 실런의 같은 사건 = 같은 노드).
실런 축은 T2-4 리뷰 AQ-02 가 강제했다(런 간 재발이 접히며 뒤 런이 소실되던 결함), 경로 정규화는
`regen_core.canonical_locator` 단일 출처를 쓴다(AQ-03 — 자체 재구현 금지).

사용: PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/violation_adapter.py
        --records <jsonl 또는 디렉터리>... [--out <ttl>] [--strip <경로 접두>] [--self-test]
exit 0 = 변환 완료 / 1 = 재료 결손·사용 오류 / 2 = 손상 레코드
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from ontology_canon import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "dddjango" / "scripts"))
import regen_core  # noqa: E402  — 경로 정규화 단일 출처(canonical_locator)

DJR = "https://numchida.com/ns/djr#"
ALIASES: Path = REPO_ROOT / "ontology" / "wiring" / "aliases.ttl"
SEVERITY_IRI = {
    "violation": "sh:Violation",
    "warning": "sh:Warning",
    "info": "sh:Info",
}


def load_alias_map(root: "Path | None" = None) -> "dict[str, tuple[str, str]]":
    """`#N` → (Work IRI, Expression IRI). 대장·정본 그래프에서만 읽는다(재구현 금지)."""
    from rdflib import Graph

    base: Path = root or REPO_ROOT
    g = Graph()
    for sub in ("rules", "wiring", "vocab"):
        for f in sorted((base / "ontology" / sub).glob("*.ttl")):
            g.parse(f, format="turtle")
    q = f"""PREFIX djr: <{DJR}>
    SELECT ?t ?w ?e WHERE {{
      ?a a djr:AliasEntry ; djr:aliasText ?t ; djr:aliasFor ?w .
      ?w djr:currentExpression ?e . }}"""
    out: "dict[str, tuple[str, str]]" = {}
    for t, w, e in g.query(q):
        text = str(t)
        if text.startswith("rule#"):
            out["#" + text.split("#", 1)[1]] = (str(w), str(e))  # rule 레인 키 = 레코드 판형의 무접두 #N
        elif text.startswith("contract#"):
            out[text] = (str(w), str(e))  # 계약 레인 키 = aliasText 원문(«contract#check-*.py»)
    return out


def _records(paths: "list[str]") -> "list[dict]":
    recs: "list[dict]" = []
    for p in paths:
        path = Path(p)
        files = sorted(path.glob("**/*.jsonl")) if path.is_dir() else [path]
        for f in files:
            if not f.is_file():
                raise FileNotFoundError(f"재료 결손: {f} 부재")
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    recs.append(json.loads(line))
    return recs


def _vid(work: str, file: str, symbol: "str | None", experiment: "str | None" = None) -> str:
    """사건 노드 키 = `(실런, Work, 라인 제거 경로, 심볼)` 의 sha16.

    **실런을 키에 넣는 이유**(T2-4 적대 리뷰 AQ-02): 넣지 않으면 서로 다른 실런에서 재발한
    같은 위반이 한 노드로 접히고 **뒤 런의 `runId` 가 통째로 사라진다**(실측: joined 2 →
    노드 1 · runId 는 앞 런 값만 잔존). 그러면 «현재 런 한정» 질의가 원리상 성립하지 않는다.
    한 런 **안**에서는 여전히 canonical identity 로 접힌다.

    **경로는 `regen_core.canonical_locator` 가 정규화한다**(AQ-03 — 재구현 금지): 라인번호만
    바뀐 같은 위반이 루프에서는 한 사건인데 여기서는 두 노드가 되던 갈라짐을 닫는다.

    **실런 축은 접미다**(사후 리뷰 AS-11): 앞에 빈 필드를 붙이면 실런이 없는 기존 위반의 노드
    IRI 까지 전부 바뀌어, 옛 그래프를 다시 적재할 때 같은 사건이 새 IRI 로 중복된다. 실런이
    있을 때만 뒤에 덧붙여 **실런 없는 키는 T2-3 형식 그대로** 남긴다(라인번호 정규화는 의도된
    변경이라 그 축에서만 달라진다).
    """
    parts: "list[str]" = [work, regen_core.canonical_locator(file), symbol or ""]
    if experiment:                       # 실런 축은 **있을 때만 뒤에 붙는다**(사후 리뷰 AS-11)
        parts.append(experiment)
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:16]


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def convert(recs: "list[dict]", alias: "dict[str, tuple[str, str]]",
            strip: str = "") -> "tuple[str, dict[str, int]]":
    tally = {"joined": 0, "rule_unjoined": 0, "contract_joined": 0, "contract_unjoined": 0,
             "sentinel": 0, "other": 0}
    blocks: "list[str]" = []
    seen: "set[str]" = set()
    for r in recs:
        rule = r.get("rule")
        if rule is None:
            if r.get("contract_ref"):
                # 계약 레인 조인(T3 게이트 조항 처분) — 검사기당 유일 규범을 대장이 문다(⑥ 함수성).
                c_hit = alias.get("contract#" + str(r.get("checker") or ""))
                if c_hit is None:
                    tally["contract_unjoined"] += 1  # 혼성 3종 등 — 침묵 탈락 금지(계수 보고)
                    continue
                rule = "contract"
                hit = c_hit
                tally["contract_joined"] += 1
            elif r.get("sentinel"):
                tally["sentinel"] += 1
                continue
            else:
                tally["other"] += 1
                continue
        else:
            hit = alias.get(rule)
        if hit is None:
            tally["rule_unjoined"] += 1
            continue
        work, expr = hit
        f = r.get("file", "")
        if strip and f.startswith(strip):
            f = f[len(strip):].lstrip("/")
        sym = r.get("symbol")
        exp = r.get("experiment_run_id")
        vid = _vid(work, f, sym, exp)
        if rule != "contract":
            tally["joined"] += 1  # rule 레인 계수(계약 레인은 contract_joined 가 이미 셌다)
        if vid in seen:
            continue  # 한 실런 안의 같은 사건은 한 노드(런 간 재발은 위 키가 갈라 놓는다)
        seen.add(vid)
        lines = [
            f"djr:v-{vid} a djr:Violation ;",
            f"    djr:byChecker <{DJR}c/{r['checker']}> ;",
            f'    djr:detectedAt "{r["ts"]}"^^xsd:dateTime ;',
            f'    djr:evidence "{_esc(r.get("message", ""))}" ;',
        ]
        if exp:
            lines.append(f'    djr:experimentRun "{_esc(exp)}" ;')
        lines += [
            f'    djr:runId "{_esc(r.get("run_id", ""))}" ;',
            f"    djr:severity {SEVERITY_IRI[r['severity']]} ;",
            f'    djr:targetFile "{_esc(f)}" ;',
        ]
        if sym:
            lines.append(f'    djr:targetSymbol "{_esc(sym)}" ;')
        lines.append(f"    djr:violatesExpression <{expr}> ;")
        lines.append(f"    djr:violatesWork <{work}> .")
        blocks.append("\n".join(lines))
    header = (f"@prefix djr: <{DJR}> .\n"
              "@prefix sh: <http://www.w3.org/ns/shacl#> .\n"
              "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n")
    ttl = header + ("\n" + "\n\n".join(sorted(blocks)) + "\n" if blocks else "")
    return ttl, tally


def self_test() -> int:
    """대장 조인이 실제로 성립하는지 — 정본 대장으로 합성 레코드 1건을 변환한다."""
    alias = load_alias_map()
    rec = {"schema": "findings/0", "run_id": "st-run", "ts": "2026-08-20T00:00:00Z",
           "record_id": "st-run:0001", "rule": "#488", "sentinel": None, "contract_ref": None,
           "checker": "check-layer-skeleton.py", "file": "application/shop/composition_root",
           "symbol": None, "severity": "violation", "message": "고정 칸 부재", "expression": None}
    noise = dict(rec, rule="#999999", message="미조인")
    crec = dict(rec, record_id="st-run:0002", rule=None, checker="check-app-container.py",
                contract_ref="선행 계약(08-04 API-error) 소유", message="계약 레인")
    ttl, tally = convert([rec, noise, crec], alias)
    ok_join = tally["joined"] == 1 and tally["rule_unjoined"] == 1 and tally["contract_joined"] == 1
    # 기대 Work 는 하드코딩하지 않고 대장에서 파생(재귀속 재발 방지 — 메모 리뷰 B2)
    exp_rule = alias.get("#488", ("", ""))[0].rsplit("#", 1)[-1]
    exp_contract = alias.get("contract#check-app-container.py", ("", ""))[0].rsplit("#", 1)[-1]
    ok_work = bool(exp_rule) and exp_rule in ttl and "violatesExpression" in ttl
    ok_contract = bool(exp_contract) and exp_contract in ttl
    print("| self-test 단언 | 판정 | 실측 |")
    print("|---|---|---|")
    print(f"| 대장 조인(#488→Work·contract#→Work) | {'✓' if ok_join else '✗'} | {tally} |")
    print(f"| Work·Expression 실값 적재 | {'✓' if ok_work else '✗'} | {(exp_rule + ' 왕복') if ok_work else ttl[:80]} |")
    print(f"| 계약 레인 적재 | {'✓' if ok_contract else '✗'} | {(exp_contract + ' 왕복') if ok_contract else ttl[:80]} |")
    if not (ok_join and ok_work and ok_contract):
        print("[violation-adapter] self-test 실패", file=sys.stderr)
        return 2
    print(f"[violation-adapter] self-test 통과 — 대장 {len(alias)}종 조인 가능")
    return 0


def main(argv: "list[str]") -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--records", action="append", default=[], help="jsonl 파일 또는 디렉터리(반복)")
    ap.add_argument("--out", default="", help="출력 ttl 경로(생략 시 stdout)")
    ap.add_argument("--strip", default="", help="targetFile 절대 경로 접두 제거")
    ap.add_argument("--self-test", action="store_true", help="정본 대장으로 조인 성립 실증")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.records:
        print("사용 오류: --records 필요", file=sys.stderr)
        return 1
    try:
        recs = _records(args.records)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"손상 레코드: {exc}", file=sys.stderr)
        return 2
    ttl, tally = convert(recs, load_alias_map(), args.strip)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(ttl, encoding="utf-8")
        print(f"[violation-adapter] {args.out} 생성")
    else:
        sys.stdout.write(ttl)
    print(f"[violation-adapter] 레코드 {len(recs)} — 적재 {tally['joined']} · "
          f"미조인 #N {tally['rule_unjoined']} · 계약 조인 {tally['contract_joined']} · "
          f"계약 미조인 {tally['contract_unjoined']} · "
          f"센티널 {tally['sentinel']} · 기타 {tally['other']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
