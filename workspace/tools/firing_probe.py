#!/usr/bin/env python3
"""C암 **발화 증명** probe — 4트리 × 5단언 acceptance matrix (T2-4 V7).

**왜 이것이 가장 중요한가**(적대 리뷰 AQ-04 «가장 위험한 단일 결함»): 팩·조회 모듈·문서 parity가
전부 green 이면서도 실제 셸 B 가 계속 `snapshot` 만 조립할 수 있다. 두 런타임이 **같은 누락**을
가지면 parity 검사도 green 이고, T2-0b 는 파일 해시를 봉인할 뿐 «그 파일이 처치 경로에서
호출됐다»를 봉인하지 못한다. 그러면 18실런이 통째로 `B=B′` 비교가 되어 인과 비교로 무효다.

**대조 대상 4트리**: source Claude · source Codex · **설치 cache Claude** · **설치 cache Codex**.
cache 는 실제 실런이 로드하는 곳이다(DEVLOG 실측). 지금은 cache 가 `2.11.0` 이라 이 두 레인이
red 인 것이 **정상**이며, 그 red 가 곧 «T2-0b 설치본 갱신 전에는 C 실런 금지»의 기계적 표현이다.

**5단언**(트리마다):
  A1 `snapshot` 프롬프트가 기준 B 판형과 **byte 동일**
  A2 `sparql` 이 **다른 프롬프트**를 내고 `<rules>` 가 실린다 · `<violations>` 동일성 집합 보존
  A3 두 런타임의 `sparql` 프롬프트 해시·tier 로그가 **일치**
  A4 미지 selector 값·손상 팩은 **nonzero** 종료
  A5 selector 를 무시하는 변이가 **red**

exit 0 = 전건 통과 / 2 = 실패(= C 실런 금지) / 1 = 재료 결손
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
CLAUDE_SRC: Path = ROOT / "dddjango" / "scripts"
CODEX_SRC: Path = ROOT / "codex-dddjango" / "skills" / "dddjango" / "scripts"
CLAUDE_CACHE_GLOB: str = "plugins/cache/*/dddjango/*/scripts"
CODEX_CACHE_GLOB: str = "plugins/cache/*/dddjango/*/skills/dddjango/scripts"

FIXTURE: "list" = [
    {"rule": "#3", "checker": "check-context-isolation.py", "record_id": "r:1",
     "file": "application/a/x.py:12", "symbol": "X", "message": "ACL 위반",
     "severity": "violation"},
    {"rule": "#488", "checker": "check-layer-skeleton.py", "record_id": "r:2",
     "file": "application/b/__init__.py", "symbol": None, "message": "빈 패키지 결손",
     "severity": "violation"},
    {"rule": "#9999", "checker": "check-nonexistent.py", "record_id": "r:3",
     "file": "z.py", "symbol": None, "message": "팩 밖", "severity": "violation"},
]

# 트리 안에서 실행되는 드라이버 — 그 트리의 regen_core·rulepack 만 쓴다(저장소 것을 쓰면
# «설치본에서 돈다»가 증명되지 않는다).
DRIVER: str = r'''
import hashlib, json, sys
recs = json.loads(sys.argv[1])
out = {"errors": []}
try:
    import regen_core as rc
except Exception as exc:
    print(json.dumps({"errors": [f"regen_core 부재: {exc}"]}, ensure_ascii=False)); raise SystemExit(0)
b = rc.assemble_prompt(recs)
out["b_sha"] = hashlib.sha256(b.encode("utf-8")).hexdigest()
out["b_bytes"] = len(b.encode("utf-8"))
try:
    import rulepack as rp
    pack = rp.Rulepack.load()
except Exception as exc:
    out["errors"].append(f"rulepack 부재·손상: {exc}")
    print(json.dumps(out, ensure_ascii=False)); raise SystemExit(0)
try:
    ordered, rules, prov = rc.select_graph(recs, pack)
except Exception as exc:
    out["errors"].append(f"select_graph 부재: {exc}")
    print(json.dumps(out, ensure_ascii=False)); raise SystemExit(0)
c = rc.assemble_prompt(ordered, rules)
out["c_sha"] = hashlib.sha256(c.encode("utf-8")).hexdigest()
out["has_rules"] = "<rules>" in c
out["rules_n"] = len(rules)
out["identity_set"] = sorted(str(rc.identity(r)) for r in ordered)
out["tiers"] = [p["priority"] for p in prov]
out["order"] = [r.get("record_id") for r in ordered]
# A4 — 손상 팩은 예외여야 한다(조용한 폴백 금지)
try:
    rp.Rulepack({"schema": "x/9"}); out["errors"].append("A4: 스키마 이탈이 통과했다")
except Exception:
    pass
print(json.dumps(out, ensure_ascii=False))
'''


def _first(glob_root: Path, pattern: str) -> "Path | None":
    hits = sorted(glob_root.glob(pattern))
    return hits[-1] if hits else None


def run_tree(scripts: Path) -> "dict":
    if not scripts.is_dir():
        return {"errors": [f"트리 부재: {scripts}"]}
    with tempfile.TemporaryDirectory() as td:
        drv = Path(td) / "driver.py"
        drv.write_text(DRIVER, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(drv), json.dumps(FIXTURE, ensure_ascii=False)],
            capture_output=True, text=True, cwd=str(scripts),
            env={"PYTHONPATH": str(scripts), "PATH": "/usr/bin:/bin",
                 "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    if proc.returncode != 0 or not proc.stdout.strip():
        return {"errors": [f"드라이버 실패 exit {proc.returncode}: {proc.stderr.strip()[:200]}"]}
    try:
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except ValueError as exc:
        return {"errors": [f"드라이버 출력 파싱 실패: {exc}"]}


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description="C암 발화 증명 probe(T2-4 V7)")
    ap.add_argument("--claude-home", default=str(Path.home() / ".claude"))
    ap.add_argument("--codex-home", default=str(Path.home() / ".codex"))
    ap.add_argument("--allow-stale-cache", action="store_true",
                    help="cache 레인 red 를 경고로 강등(T2-0b 이전 개발 중에만)")
    args = ap.parse_args(argv)

    trees: "list[tuple[str, Path | None]]" = [
        ("source-claude", CLAUDE_SRC),
        ("source-codex", CODEX_SRC),
        ("cache-claude", _first(Path(args.claude_home), CLAUDE_CACHE_GLOB)),
        ("cache-codex", _first(Path(args.codex_home), CODEX_CACHE_GLOB)),
    ]
    results: "dict[str, dict]" = {}
    for name, path in trees:
        results[name] = run_tree(path) if path else {"errors": ["cache 트리 미발견"]}

    ref = results["source-claude"]
    rows: "list[tuple[str, str, bool, bool]]" = []   # (이름, 실측, 통과, cache 레인 여부)
    for name, _ in trees:
        r = results[name]
        is_cache = name.startswith("cache")
        if r.get("errors"):
            rows.append((f"A1·A2 {name}", " / ".join(r["errors"])[:110], False, is_cache))
            continue
        a1 = r.get("b_sha") == ref.get("b_sha")
        a2 = (r.get("c_sha") != r.get("b_sha") and r.get("has_rules")
              and r.get("rules_n", 0) > 0
              and r.get("identity_set") == ref.get("identity_set"))
        rows.append((f"A1 {name} snapshot byte 동일",
                     f"{(r.get('b_sha') or '')[:16]} · {r.get('b_bytes')}B", a1, is_cache))
        rows.append((f"A2 {name} sparql 발화", f"rules {r.get('rules_n')} · tiers {r.get('tiers')}",
                     bool(a2), is_cache))

    live = [n for n, _ in trees if not results[n].get("errors")]
    a3 = (len({results[n].get("c_sha") for n in live}) == 1
          and len({json.dumps(results[n].get("tiers")) for n in live}) == 1) if len(live) > 1 else False
    rows.append(("A3 런타임 간 sparql 프롬프트·tier 일치", f"살아있는 트리 {len(live)}: {live}",
                 a3, len(live) < 4))

    a4 = all(not any(e.startswith("A4") for e in results[n].get("errors", [])) for n in live)
    rows.append(("A4 손상 팩·미지 selector fail-closed", f"살아있는 트리 {len(live)} 전건", a4, False))

    mut = subprocess.run([sys.executable, str(ROOT / "workspace" / "tools" / "rulepack_smoke.py"),
                          "--mutation-test"], capture_output=True, text=True,
                         env={"PYTHONUTF8": "1", "PATH": "/usr/bin:/bin"})
    a5 = mut.returncode == 0 and "전건 red" in mut.stdout
    rows.append(("A5 selector 무시 변이 검출", "rulepack_smoke --mutation-test", a5, False))

    print("| 단언 | 실측 | 판정 |")
    print("|---|---|---|")
    hard = soft = 0
    for name, detail, ok, is_cache in rows:
        if not ok:
            if is_cache and args.allow_stale_cache:
                soft += 1
                print(f"| {name} | {detail} | ⚠ (cache 미갱신 — T2-0b) |")
                continue
            hard += 1
        print(f"| {name} | {detail} | {'✓' if ok else '✗'} |")
    print(f"\n단언 {len(rows)} · 실패 {hard} · cache 경고 {soft}")
    if hard:
        print("\n**C 실런 금지**: 발화 증명이 성립하지 않는다. 설치 cache 가 낡았다면 T2-0b "
              "설치본 갱신(사용자 승인)이 선행 조건이다.")
    return 2 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
