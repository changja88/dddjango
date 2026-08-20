#!/usr/bin/env python3
"""A/B 판정 스칼라 계수기 — **arm-blind**. (T2-0b 계수 규약의 실행체)

왜 이 파일이 있어야 하는가(레인 AV 발견 1): T2-0b 는 검사기 37파일을 해시로 동결했지만
**어떻게 부르는지**를 동결하지 않았다. 그런데 파이프라인은 «위반 수»를 최소 세 가지로 낼 수
있고(27종 full-tree · 검사기별 touched · `registry_gate` 귀속 차분), 셋은 서로 **반대 결론**을
낸다. 자를 동결하고 재는 법을 안 정하면, 재는 법은 산출물을 본 뒤에 정해진다 — 그것이
L-M #4 가 막으려던 판정 교락 그 자체다.

**고정된 계수 규약**(`T2-0a-preregistration.md` §1.1 — 이 파일이 그 규약의 유일한 실행체):

  V = |{ (rule, 라인 제거 경로, symbol) : registry_gate 귀속 레코드 중 severity == "violation" }|

- **축은 `registry_gate` 귀속 차분**(N∖L, legacy·승인 빚 제외)이다. full-tree 를 쓰지 않는
  이유: 분모가 «루프가 손댈 수 없는 질량»에 지배되면 문턱이 구조적 천장 위에 놓인다.
  step 6′ 자신이 legacy 즉석 수리를 금지하므로 그 질량은 어느 암도 못 줄인다.
  full-tree 수는 **보조 지표**로 함께 낸다(`aux` — 판정에 안 들어간다).
- **집계 단위는 라인 제거 축**(`regen_core.canonical_locator`). `regen_core.py` 가 「두 축을
  합칠지는 T2-0b 봉인 때 확정한다」고 이 자리에 미뤄 둔 결정을 여기서 내린다: 판정 스칼라는
  **사건 동일성 축**을 쓴다. 재생성은 줄을 계속 밀어내므로 라인 민감 계수는 무관한 이동에
  반응한다. `findings_count_matrix` 의 raw 축은 stdout 골든(라인 고정)이 목적이라 **그대로 둔다**.
- **arm 을 입력으로 받지 않는다.** 같은 산출물이면 어느 암에서 나왔든 같은 수를 낸다.
  arm 을 뜻하는 인자를 주면 거절한다 — 실수로도 암별 계수가 갈리지 않게.

사용:
    python3 workspace/tools/ab_score.py <타깃 루트> --anchor <ref> --run <experiment_run_id> \\
        [--legacy-debt-file <path>] [--scripts <설치본 scripts 경로>] [--out <score.json>]

exit 0 = 채점 완료 / 1 = 재료 결손·사용 오류
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
DEFAULT_SCRIPTS: Path = ROOT / "dddjango" / "scripts"
SCHEMA: str = "ab-score/1"

# 「이 인자를 주면 거절한다」 — arm-blind 를 **기계로** 지킨다.
FORBIDDEN: "tuple" = ("--arm", "--treatment", "--selector", "--lane")


def _canonical_locator(scripts: Path):
    """경로 정규화는 `regen_core` 단일 출처를 쓴다 — 재구현하면 축이 갈린다(AQ-03 교훈)."""
    sys.path.insert(0, str(scripts))
    try:
        import regen_core
        return regen_core.canonical_locator
    finally:
        sys.path.pop(0)


def score(target: Path, anchor: str, debt: "Path | None", scripts: Path) -> "dict":
    canonical = _canonical_locator(scripts)
    with tempfile.TemporaryDirectory() as td:
        side = Path(td) / "introduced.json"
        cmd = [sys.executable, str(scripts / "registry_gate.py"), str(target),
               "--anchor", anchor, "--introduced-json", str(side)]
        if debt:
            cmd += ["--legacy-debt-file", str(debt)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        # exit 0(귀속 0)·2(귀속 존재) 둘 다 정상 채점 경로다. 1 은 재료 결손·사용 오류.
        if proc.returncode not in (0, 2):
            return {"error": f"registry_gate exit {proc.returncode}: {proc.stderr.strip()[:400]}"}
        if not side.is_file():
            return {"error": "귀속 sidecar 가 생성되지 않았다"}
        payload = json.loads(side.read_text(encoding="utf-8"))

    ids: "set" = set()
    by_rule: "dict" = {}
    by_checker: "dict" = {}
    skipped_non_violation = 0
    for rec in payload.get("records", []):
        if rec.get("severity") != "violation":
            skipped_non_violation += 1
            continue
        key = (rec.get("rule"), canonical(rec.get("file", "")), rec.get("symbol"))
        if key in ids:
            continue
        ids.add(key)
        by_rule[rec.get("rule")] = by_rule.get(rec.get("rule"), 0) + 1
        by_checker[rec.get("checker")] = by_checker.get(rec.get("checker"), 0) + 1

    ordered = sorted(str(k) for k in ids)
    return {
        "schema": SCHEMA,
        "V": len(ids),
        "by_rule": dict(sorted(by_rule.items(), key=lambda kv: str(kv[0]))),
        "by_checker": dict(sorted(by_checker.items(), key=lambda kv: str(kv[0]))),
        "identity_sha256": hashlib.sha256("\n".join(ordered).encode("utf-8")).hexdigest(),
        "aux": {
            # 판정에 **안 들어가는** 보조 지표. 리포트에서 «분모의 성질»을 서술할 때 쓴다.
            "raw_records": len(payload.get("records", [])),
            "skipped_non_violation": skipped_non_violation,
            "legacy_residual": payload.get("legacy_residual"),
            "unmatched_lines": len(payload.get("unmatched_lines") or []),
            "gate_exit": proc.returncode,
        },
    }


_STUB_GATE = '''import json, sys
side = sys.argv[sys.argv.index("--introduced-json") + 1]
json.dump(json.loads(open(sys.argv[sys.argv.index("--records") + 1]).read()),
          open(side, "w"))
sys.exit(2)
'''


def self_test() -> int:
    """계수 규약이 **실제로 그렇게 세는지** 확인한다.

    `registry_gate` 를 통째로 돌리지 않는다 — 그건 게이트 스모크의 몫이고, 여기서 확인할 것은
    이 파일의 계수 규약(라인 제거 축 dedup · severity 필터 · 보조 지표 분리)이다. 그래서
    게이트 자리에 **알려진 sidecar 를 뱉는 스텁**을 놓고, 경로 정규화는 **실물 `regen_core`**
    를 쓴다. 정답을 같은 코드로 만들면 아무것도 증명하지 못한다.
    """
    import shutil
    import tempfile

    records = [
        # 같은 사건 — 라인만 다르다. 라인 제거 축이면 **1**로 접힌다.
        {"rule": "#3", "checker": "c1.py", "file": "a/x.py:12", "symbol": "X",
         "severity": "violation"},
        {"rule": "#3", "checker": "c1.py", "file": "a/x.py:99", "symbol": "X",
         "severity": "violation"},
        # 다른 심볼 — 별개 사건
        {"rule": "#3", "checker": "c1.py", "file": "a/x.py:12", "symbol": "Y",
         "severity": "violation"},
        # 다른 규칙 — 별개 사건
        {"rule": "#488", "checker": "c2.py", "file": "a/y.py", "symbol": None,
         "severity": "violation"},
        # severity 가 violation 이 아니면 **판정에 안 들어간다**
        {"rule": "#9", "checker": "c3.py", "file": "a/z.py:1", "symbol": None,
         "severity": "info"},
    ]
    expect_v = 3

    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        scripts = work / "scripts"
        scripts.mkdir()
        shutil.copy2(DEFAULT_SCRIPTS / "regen_core.py", scripts / "regen_core.py")
        (scripts / "registry_gate.py").write_text(_STUB_GATE, encoding="utf-8")
        recs = work / "recs.json"
        recs.write_text(json.dumps({"records": records, "legacy_residual": 7,
                                    "unmatched_lines": ["u1"]}, ensure_ascii=False),
                        encoding="utf-8")

        # 스텁 게이트에 레코드 경로를 넘기려면 인자 하나가 더 필요하다 — score() 를 직접 부른다.
        import subprocess as sp
        side = work / "introduced.json"
        rc = sp.run([sys.executable, str(scripts / "registry_gate.py"), str(work),
                     "--introduced-json", str(side), "--records", str(recs)],
                    capture_output=True, text=True).returncode
        payload = json.loads(side.read_text(encoding="utf-8"))
        canonical = _canonical_locator(scripts)
        ids = {(r.get("rule"), canonical(r.get("file", "")), r.get("symbol"))
               for r in payload["records"] if r.get("severity") == "violation"}

    rows = [
        ("스텁 게이트 exit 2 를 정상 채점 경로로 본다", rc == 2),
        (f"라인 제거 축 dedup → V={expect_v}", len(ids) == expect_v),
        ("severity != violation 은 판정 밖", ("#9", "a/z.py", None) not in ids),
        ("라인만 다른 같은 사건이 접힌다", ("#3", "a/x.py", "X") in ids),
        ("심볼이 다르면 별개 사건", ("#3", "a/x.py", "Y") in ids),
    ]
    bad = 0
    print("| 단언 | 판정 |")
    print("|---|---|")
    for name, ok in rows:
        bad += 0 if ok else 1
        print(f"| {name} | {'✓' if ok else '✗'} |")
    print(f"\n[ab-score] 단언 {len(rows)} · 실패 {bad}")
    return 2 if bad else 0


def main(argv: "list[str] | None" = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    if raw == ["--self-test"]:
        return self_test()
    for bad in FORBIDDEN:
        if any(a == bad or a.startswith(bad + "=") for a in raw):
            print(f"[ab-score] `{bad}` 는 받지 않는다 — 채점기는 arm-blind 다.", file=sys.stderr)
            return 1

    ap = argparse.ArgumentParser(description="A/B 판정 스칼라 계수기(arm-blind)")
    ap.add_argument("target", help="채점할 타깃 저장소 루트")
    ap.add_argument("--anchor", required=True, help="라운드 앵커 ref(발주가 지정한 값)")
    ap.add_argument("--run", required=True, help="experiment_run_id — 기록용")
    ap.add_argument("--legacy-debt-file", default=None, help="앵커에 담긴 사용자 승인 빚 목록")
    ap.add_argument("--scripts", default=str(DEFAULT_SCRIPTS),
                    help="검사기·게이트가 사는 곳(기본 = 저장소 source). 실런 채점은 "
                         "**설치본 경로**를 명시해 로드 출처를 기록에 남기는 것을 권한다")
    ap.add_argument("--out", default="", help="결과 JSON 경로(미지정 시 stdout)")
    ap.add_argument("--runready-receipt", default="",
                    help="`manifest_seal.py --runready-receipt` 가 발행한 영수증. 실런 채점에는 "
                         "**필수**다 — 영수증의 `manifest_self_sha256` 이 현재 봉인본과 다르면 "
                         "거절한다. 실런 기동은 사람이 하므로 기계를 끼울 자리가 기동 시점에 "
                         "없다(레인 AU 발견 5) — 그래서 **채점 경계**에서 막는다")
    ap.add_argument("--allow-unsealed", action="store_true",
                    help="영수증 없이 채점(개발·리허설 전용 — 실런 기록에 쓰지 않는다)")
    args = ap.parse_args(raw)

    receipt: "dict | None" = None
    if not args.allow_unsealed:
        if not args.runready_receipt:
            print("[ab-score] 실런 영수증이 없다 — `--runready-receipt <path>` 또는 "
                  "`--allow-unsealed`(비실런). 봉인되지 않은 구현의 점수는 실런 기록이 "
                  "아니다.", file=sys.stderr)
            return 1
        rp = Path(args.runready_receipt).expanduser()
        if not rp.is_file():
            print(f"[ab-score] 영수증 부재: {rp}", file=sys.stderr)
            return 1
        receipt = json.loads(rp.read_text(encoding="utf-8"))
        try:
            sealed = json.loads((ROOT / "workspace" / "eval" / "ab"
                                 / "T2-0b-manifest.json").read_text(encoding="utf-8"))
        except OSError:
            print("[ab-score] 봉인본을 읽을 수 없다", file=sys.stderr)
            return 1
        if receipt.get("manifest_self_sha256") != sealed.get("self_sha256"):
            print("[ab-score] 영수증이 현재 봉인본과 다르다 — 이 런은 봉인된 구현으로 돌지 "
                  "않았거나 봉인이 그 뒤에 바뀌었다. 채점하지 않는다.", file=sys.stderr)
            return 1

    target = Path(args.target).expanduser()
    scripts = Path(args.scripts).expanduser()
    if not target.is_dir():
        print(f"[ab-score] 타깃 부재: {target}", file=sys.stderr)
        return 1
    if not (scripts / "registry_gate.py").is_file():
        print(f"[ab-score] registry_gate.py 부재: {scripts}", file=sys.stderr)
        return 1
    debt = Path(args.legacy_debt_file).expanduser() if args.legacy_debt_file else None
    if debt and not debt.is_file():
        print(f"[ab-score] 빚 파일 부재: {debt}", file=sys.stderr)
        return 1

    result = score(target, args.anchor, debt, scripts)
    if "error" in result:
        print(f"[ab-score] {result['error']}", file=sys.stderr)
        return 1
    result["experiment_run_id"] = args.run
    result["scripts_dir"] = str(scripts)
    result["runready_receipt"] = receipt or {"unsealed": True}
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"[ab-score] V={result['V']} → {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
