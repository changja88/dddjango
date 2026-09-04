#!/usr/bin/env python3
"""무손실 판정 — old/new 레코드·발화 라인 다중집합 차분 (fr2 rv6 diff.py 판형 + 현장 보고 3 허용 규칙).

허용:
  B∖A : rule ∈ NEW_RULES(#646 #647 #648 #649 #650)
  A∖B : (info, #645) 이고 같은 (경로, 줄) 에 B 의 (violation, #647) 가 있는 것(#645 nested ⓓ → #647 배타 · 1:1)
그 밖의 차분은 전부 RED. stdout 은 `[ⓓ?#N]` 발화 라인만 비교(요약·계수 행 제외).
사용: lossless_diff.py <out-dir>
"""
import collections
import json
import re
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
NEW_RULES = {"#646", "#647", "#648", "#649", "#650"}
EXCLUDE_PREFIX = ("mp_probe_",)  # 타 조사자 untracked 시제품(사본 오염) — 양쪽에서 제외
LINE_RE = re.compile(r"^\s*(\[ⓓ?#\d+\].*)$")
LOC_RE = re.compile(r"^(.*?):(\d+)$")
RULE_LINE_RE = re.compile(r"^\[ⓓ?(#\d+)\]")


def load(p: Path):
    c = collections.Counter()
    locs = collections.defaultdict(set)  # (sev, rule) -> {(path, line)}
    if not p.is_file():
        return c, locs
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        f = str(r.get("file", ""))
        if f.startswith("./"):
            f = f[2:]
        if f.startswith(EXCLUDE_PREFIX):
            continue
        key = (r.get("severity"), r.get("rule"), f, r.get("message"))
        c[key] += 1
        m = LOC_RE.match(f)
        if m:
            locs[(r.get("severity"), r.get("rule"))].add((m.group(1), int(m.group(2))))
    return c, locs


def lines_of(p: Path):
    c = collections.Counter()
    if not p.is_file():
        return c
    for raw in p.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE_RE.match(raw)
        if m and not any(seg in m.group(1) for seg in EXCLUDE_PREFIX):
            c[m.group(1)] += 1
    return c


def judge(name: str, old_jsonl: Path, new_jsonl: Path, old_out: Path, new_out: Path):
    a, la = load(old_jsonl)
    b, lb = load(new_jsonl)
    AmB, BmA = a - b, b - a
    by_rule = lambda cnt: dict(collections.Counter((k[0], k[1]) for k in cnt.elements()))
    # 슬롯 키(rv5-A N-8): (경로, 줄, 라벨) — #645 nested ⓓ 의 라벨 ↔ #647 «값 자리가 `Any`» 위반의 라벨
    def label645(msg):
        msg = msg.split(" — 물음: ")[0]  # 후보 라인은 «메시지 — 물음: …» 판형
        for suf in (" 의 타입 안에 `Any`", " 안에 `Any`", " 주석에 `Any`(nested)"):
            if msg.endswith(suf):
                return msg[: -len(suf)] + (" 주석" if suf == " 주석에 `Any`(nested)" else "")
        return None
    def label647(msg):
        i = msg.find("의 값 자리가 `Any`")
        return msg[:i] if i > 0 else None
    b647 = set()
    for (sev, rule, f, msg), _n in b.items():
        m = LOC_RE.match(f)
        if sev == "violation" and rule == "#647" and m and label647(msg) is not None:
            b647.add((m.group(1), int(m.group(2)), label647(msg)))
    bad_B = {k: v for k, v in BmA.items() if k[1] not in NEW_RULES}
    matched = unmatched = 0
    bad_A = {}
    for k, v in AmB.items():
        m = LOC_RE.match(k[2])
        if k[0] == "info" and k[1] == "#645" and m and (m.group(1), int(m.group(2)), label645(k[3])) in b647:
            matched += v
        elif k[0] == "info" and k[1] == "#645":
            unmatched += v
        else:
            bad_A[k] = v
    r493 = (sum(v for k, v in a.items() if k[1] == "#493"), sum(v for k, v in b.items() if k[1] == "#493"))
    ex_o = (old_out.with_suffix(".exit").read_text().strip() if old_out.with_suffix(".exit").is_file() else "?")
    ex_n = (new_out.with_suffix(".exit").read_text().strip() if new_out.with_suffix(".exit").is_file() else "?")
    # stdout 발화 라인 — 신규 규칙 라인 제거 · 1:1 로 접힌 ⓓ#645 는 레코드 판정에 맡기고 라인은 규칙별 계수만
    lo, ln = lines_of(old_out), lines_of(new_out)
    lo_f = collections.Counter({k: v for k, v in lo.items() if RULE_LINE_RE.match(k).group(1) not in NEW_RULES})
    ln_f = collections.Counter({k: v for k, v in ln.items() if RULE_LINE_RE.match(k).group(1) not in NEW_RULES})
    l_AmB, l_BmA = lo_f - ln_f, ln_f - lo_f
    l_res_A = {k: v for k, v in l_AmB.items() if not k.startswith("[ⓓ#645]")}
    ok = not bad_A and not bad_B and unmatched == 0 and not l_res_A and not l_BmA
    print(f"{'OK ' if ok else 'RED'} {name}: old={sum(a.values())} new={sum(b.values())} exit {ex_o}->{ex_n} "
          f"| A∖B={sum(AmB.values())} {by_rule(AmB)} (ⓓ#645→#647 1:1 matched={matched} unmatched={unmatched}) "
          f"| B∖A={sum(BmA.values())} {by_rule(BmA)} | 비허용 A∖B={sum(bad_A.values())} B∖A={sum(bad_B.values())} "
          f"| #493 {r493[0]}/{r493[1]} | 발화라인 old={sum(lo.values())} new={sum(ln.values())} 잔여차 A∖B={sum(l_res_A.values())} B∖A={sum(l_BmA.values())}")
    for k in list(bad_A)[:5]:
        print("   비허용 A∖B:", k)
    for k in list(bad_B)[:5]:
        print("   비허용 B∖A:", k)
    return ok


CHECKERS = ("check-public-surface-annotation.py", "check-api-error-controller-contract.py",
            "check-openapi-error-declaration.py")
all_ok = True
for repo in ("spring", "spring-d2eaafe", "spring-f5ee428", "kkebi"):
    for chk in CHECKERS:
        all_ok &= judge(f"{repo} {chk}", OUT / f"{repo}.old.{chk}.jsonl", OUT / f"{repo}.new.{chk}.jsonl",
                        OUT / f"{repo}.old.{chk}.out", OUT / f"{repo}.new.{chk}.out")
fx_keys = sorted({p.name.split(".old.")[0] for p in OUT.glob("fx.*.old.*.jsonl")} |
                 {p.name.split(".old.")[0] for p in OUT.glob("fx.*.old.*.out")})
fx_ok = 0
fx_bad = []
for key in fx_keys:
    for chk in CHECKERS:
        o = OUT / f"{key}.old.{chk}.out"
        if not o.is_file():
            continue
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = judge(f"{key} {chk}", OUT / f"{key}.old.{chk}.jsonl", OUT / f"{key}.new.{chk}.jsonl", o,
                       OUT / f"{key}.new.{chk}.out")
        if ok:
            fx_ok += 1
        else:
            fx_bad.append(buf.getvalue())
        all_ok &= ok
print(f"fixtures: OK {fx_ok} · RED {len(fx_bad)}")
for s in fx_bad:
    print(s, end="")
print("VERDICT:", "LOSSLESS" if all_ok else "RED")
