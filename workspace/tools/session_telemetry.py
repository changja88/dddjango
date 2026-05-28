#!/usr/bin/env python3
"""dddjango 파이프라인 세션 텔레메트리 파서 (재사용).

Claude Code 세션 jsonl 1개 이상을 받아 시간·토큰 분해를 같은 잣대로 출력한다.
실행시간/토큰 최적화에서 "추측 말고 측정"을 위해 쓴다.

핵심 주의:
- 서브에이전트 호출 도구 이름은 `Agent`다(`Task` 아님 — 환경에 따라 다름. 둘 다 인식).
- 병렬 여부는 "같은 턴 디스패치"가 아니라 **실행 구간(start=end-duration, end=결과반환) 겹침**으로
  판정한다. 코디네이터가 Agent를 10초 간격으로 연달아 던지면 같은 턴이 아니어도 동시 실행된다.
- 토큰은 **원시 카운트**와 **과금 비용 단위**가 다르다. cache_read 는 0.1x(가장 쌈)라
  '88% cache_read'는 비용이 아니라 컨텍스트 크기 신호다. 비용 절감 타깃은 보통 output·cache_creation.

토큰 비용 가중(입력 1 기준 근사): cache_read 0.1 · cache_creation 1.25 · input 1.0 · output 5.0.

사용:
  python session_telemetry.py <session.jsonl> [...]
  python session_telemetry.py --smoke 3 4 5
"""
import json
import sys
import glob
import os
import datetime

COST_W = {"cache_read": 0.1, "cache_creation": 1.25, "input": 1.0, "output": 5.0}


def load_rows(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return rows


def ts(r):
    t = r.get("timestamp")
    if not t:
        return None
    try:
        return datetime.datetime.fromisoformat(t.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def intervals_overlap(a, b):
    return a[1] > b[0] and b[1] > a[0]


def analyze(path):
    rows = load_rows(path)
    times = [t for t in (ts(r) for r in rows) if t]
    wall_min = (max(times) - min(times)).total_seconds() / 60 if times else 0.0

    # 서브에이전트: agentType별 집계 + 실행 구간(겹침 판정용)
    agents = {}
    intervals = []  # (start, end, agentType)
    for r in rows:
        tur = r.get("toolUseResult")
        if isinstance(tur, dict) and tur.get("totalDurationMs") is not None:
            a = tur.get("agentType") or tur.get("subagentType") or "?"
            ms = tur.get("totalDurationMs") or 0
            tok = tur.get("totalTokens") or 0
            slot = agents.setdefault(a, {"n": 0, "ms": 0, "tok": 0})
            slot["n"] += 1
            slot["ms"] += ms
            slot["tok"] += tok
            end = ts(r)
            if end:
                intervals.append((end - datetime.timedelta(seconds=ms / 1000), end, a))

    sub_ms = sum(s["ms"] for s in agents.values())
    sub_tok = sum(s["tok"] for s in agents.values())

    # 병렬 쌍: 실행 구간이 겹치는 서브에이전트 쌍 수
    intervals.sort(key=lambda x: x[0])
    parallel_pairs = sum(
        1
        for i in range(len(intervals))
        for j in range(i + 1, len(intervals))
        if intervals_overlap(intervals[i], intervals[j])
    )
    # wall 직렬 기여 근사: 겹친 구간을 병합한 총 점유 시간
    merged = 0.0
    if intervals:
        cur_s, cur_e = intervals[0][0], intervals[0][1]
        for s, e, _ in intervals[1:]:
            if s <= cur_e:
                cur_e = max(cur_e, e)
            else:
                merged += (cur_e - cur_s).total_seconds()
                cur_s, cur_e = s, e
        merged += (cur_e - cur_s).total_seconds()
    sub_wall_min = merged / 60

    # 코디네이터(메인 assistant, 사이드체인 제외) usage
    cc = cr = out = inp = turns = 0
    for r in rows:
        if r.get("type") == "assistant" and not r.get("isSidechain"):
            u = r.get("message", {}).get("usage", {})
            if u:
                turns += 1
                cc += u.get("cache_creation_input_tokens", 0)
                cr += u.get("cache_read_input_tokens", 0)
                out += u.get("output_tokens", 0)
                inp += u.get("input_tokens", 0)
    coord_grand = cc + cr + out + inp
    coord_cost = (cr * COST_W["cache_read"] + cc * COST_W["cache_creation"]
                  + inp * COST_W["input"] + out * COST_W["output"])

    return {
        "path": path, "wall_min": wall_min, "agents": agents,
        "sub_calls": len(intervals), "sub_min": sub_ms / 1000 / 60,
        "sub_wall_min": sub_wall_min, "sub_tok": sub_tok, "parallel_pairs": parallel_pairs,
        "coord_turns": turns, "coord_cc": cc, "coord_cr": cr, "coord_out": out,
        "coord_inp": inp, "coord_grand": coord_grand, "coord_cost": coord_cost,
        "human_coord_min": wall_min - sub_wall_min,
    }


def fmt(res):
    print(f"\n{'='*72}\n{os.path.basename(res['path'])}\n{'='*72}")
    print(f"WALL {res['wall_min']:.1f}m | 서브에이전트 {res['sub_calls']}회 (직렬합 {res['sub_min']:.1f}m, "
          f"겹침병합 {res['sub_wall_min']:.1f}m, 병렬쌍 {res['parallel_pairs']}) | 코디+게이트≈{res['human_coord_min']:.1f}m")
    print("  --- 서브에이전트 (시간 내림차순) ---")
    for a, v in sorted(res["agents"].items(), key=lambda x: -x[1]["ms"]):
        print(f"  {a:30s} n={v['n']:2d}  {v['ms']/1000/60:6.2f}m  tok={v['tok']:>9,}")
    g = res["coord_grand"] or 1
    print("  --- 코디네이터 토큰: 원시(raw) vs 과금단위(cost) ---")
    print(f"  turns={res['coord_turns']}  raw_grand={g/1e6:.2f}M  cost_units={res['coord_cost']/1e6:.2f}M")
    for label, raw in [("cache_read", res["coord_cr"]), ("cache_creation", res["coord_cc"]),
                       ("output", res["coord_out"]), ("input", res["coord_inp"])]:
        cost = raw * COST_W[label]
        print(f"    {label:15s} raw {raw:>10,} ({100*raw/g:4.1f}%)   cost {cost/1e6:5.2f}M "
              f"({100*cost/(res['coord_cost'] or 1):4.1f}%)")


def compare(results):
    print(f"\n\n{'#'*72}\n비교표\n{'#'*72}")
    hdr = (f"{'session':9s}{'wall':>7s}{'sub병합':>8s}{'sub호출':>7s}{'턴':>5s}"
           f"{'raw_M':>7s}{'cost_M':>7s}{'cr_raw':>7s}{'out_cost':>9s}")
    print(hdr + "\n" + "-" * len(hdr))
    for res in results:
        name = os.path.basename(os.path.dirname(res["path"])).split("dddjango-")[-1][:8]
        print(f"{name:9s}{res['wall_min']:7.1f}{res['sub_wall_min']:8.1f}{res['sub_calls']:7d}"
              f"{res['coord_turns']:5d}{res['coord_grand']/1e6:7.2f}{res['coord_cost']/1e6:7.2f}"
              f"{res['coord_cr']/1e6:7.2f}{res['coord_out']*COST_W['output']/1e6:9.2f}")
    print("\n  raw_M=원시토큰 합 · cost_M=과금단위 합 · cr_raw=cache_read 원시 · out_cost=output 과금단위(×5)")


def main():
    args = sys.argv[1:]
    if args and args[0] == "--smoke":
        paths = []
        for s in args[1:]:
            d = os.path.expanduser(f"~/.claude/projects/-Users-hyun-Desktop-dddjango-smoke{s}")
            paths.extend(sorted(glob.glob(os.path.join(d, "*.jsonl"))))
    else:
        paths = args
    if not paths:
        print(__doc__)
        sys.exit(1)
    results = [analyze(p) for p in paths]
    for res in results:
        fmt(res)
    if len(results) > 1:
        compare(results)


if __name__ == "__main__":
    main()
