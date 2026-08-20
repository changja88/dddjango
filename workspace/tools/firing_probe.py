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

def _first(glob_root: Path, pattern: str) -> "Path | None":
    hits = sorted(glob_root.glob(pattern))
    return hits[-1] if hits else None


def _cli(scripts: Path, side: Path, extra: "list", cwd: Path) -> "tuple":
    """그 트리의 **실제 CLI** 를 subprocess 로 돌린다 → `(exit, stdout, stderr)`.

    앞선 판은 드라이버가 `assemble_prompt`·`select_graph` 를 **직접 호출**해 `_main()` 을
    우회했다(반증 레인 AT 4-2 실증: CLI 에서만 selector 를 snapshot 으로 강제하는 변이가
    probe green 을 통과했다 — `probe_has_rules True` ↔ `cli_has_rules False`). 발화 증명은
    **실런이 실제로 부르는 경로**에서 서야 한다.
    """
    proc = subprocess.run(
        [sys.executable, str(scripts / "regen_core.py"), "--introduced-json", str(side), *extra],
        capture_output=True, text=True, cwd=str(cwd),
        env={"PYTHONPATH": str(scripts), "PATH": "/usr/bin:/bin",
             "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    return proc.returncode, proc.stdout, proc.stderr


def run_tree(scripts: Path) -> "dict":
    """한 트리에 대해 A1~A5 를 **CLI 로** 실측한다."""
    import hashlib
    import shutil

    out: "dict" = {"errors": []}
    if not scripts.is_dir():
        return {"errors": [f"트리 부재: {scripts}"]}
    if not (scripts / "regen_core.py").is_file():
        return {"errors": [f"regen_core.py 부재: {scripts}"]}

    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        side = work / "introduced.json"
        side.write_text(json.dumps({"schema": "gate-introduced/0", "anchor": "x",
                                    "attributed_lines": ["a"], "records": FIXTURE,
                                    "unmatched_lines": []}, ensure_ascii=False),
                        encoding="utf-8")

        code, b, err = _cli(scripts, side, ["--selector", "snapshot"], work)
        if code != 0:
            return {"errors": [f"snapshot CLI exit {code}: {err.strip()[:160]}"]}
        out["b_sha"] = hashlib.sha256(b.encode("utf-8")).hexdigest()
        out["b_bytes"] = len(b.encode("utf-8"))

        cap = work / "cap.jsonl"
        code, c, err = _cli(scripts, side, ["--selector", "sparql", "--capacity-log", str(cap)], work)
        if code != 0:
            out["errors"].append(f"sparql CLI exit {code}: {err.strip()[:160]}")
            return out
        out["c_sha"] = hashlib.sha256(c.encode("utf-8")).hexdigest()
        out["has_rules"] = "<rules>" in c
        row = json.loads(cap.read_text(encoding="utf-8").strip().splitlines()[-1])
        out["rules_n"] = row["rules_n"]
        out["tiers"] = row["tiers"]
        out["identity_set"] = sorted(str(x["identity"]) for x in row["records_provenance"]
                                     if x["drop_reason"] is None)

        # A4-① 미지 selector 는 **argparse 단계에서** 거절되어야 한다(조용한 snapshot 금지)
        code, _, _ = _cli(scripts, side, ["--selector", "bogus"], work)
        if code == 0:
            out["errors"].append("A4: 미지 selector 값이 통과했다")

        # A4-③ selector 를 **아예 안 주면** 중단해야 한다(레인 AV 발견 4). 기본값이 있으면
        # C암 런이 조용히 B 처치를 받고 exit 0 으로 끝나며, 로그를 뒤지기 전에는 아무도 모른다.
        code, stdout_nosel, _ = _cli(scripts, side, [], work)
        if code == 0:
            out["errors"].append("A4: selector 미지정이 통과했다(조용한 snapshot 폴백)")
        if stdout_nosel:
            out["errors"].append("A4: selector 미지정인데 프롬프트가 나왔다")

        # A4-② 손상 팩 — 트리 사본에서 팩만 깨고 sparql 을 돌린다
        broken = work / "broken"
        shutil.copytree(scripts, broken, ignore=shutil.ignore_patterns("__pycache__"))
        (broken / "rulepack.json").write_text('{"schema":"x/9"}', encoding="utf-8")
        code, stdout_broken, _ = _cli(broken, side, ["--selector", "sparql"], work)
        if code == 0:
            out["errors"].append("A4: 손상 팩이 fail-closed 하지 않았다")
        if stdout_broken:
            out["errors"].append("A4: 손상 팩인데 프롬프트가 나왔다(조용한 폴백)")
    return out


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
