#!/usr/bin/env python3
"""dddjango smoke1~7 비교 분석 HTML 리포트 생성기.

세션 jsonl(시간·토큰·디스패치) + 메모리 근거 서술(개선/가설·이벤트·결과)을 결합해
self-contained HTML 표를 만든다. session_telemetry.py 와 같은 파싱 규칙을 쓴다.

기계시간 = wall − Σ(사람 대기 갭). 갭(>120s) 분류:
  - 갭을 끝내는 행에 서브에이전트 toolUseResult.totalDurationMs 있음 → 서브에이전트 실행(기계, 유지)
  - 없음(AskUserQuestion 답변·사람 메시지) → 게이트/사람 대기(제외)

사용: python smoke_report.py   (→ smoke_timeline.html 생성)
"""
import json
import glob
import os
import datetime
from collections import Counter

COST_W = {"cache_read": 0.1, "cache_creation": 1.25, "input": 1.0, "output": 5.0}
PROJ = os.path.expanduser("~/.claude/projects")

# (smoke 라벨, 폴더/세션 prefix, 날짜) — 폴더 번호는 smoke3부터. smoke1·smoke2는 공유 -smoke 폴더.
SESSIONS = [
    ("smoke1a", "smoke/a4ef25ae", "05-26"),
    ("smoke1b", "smoke/655f2453", "05-26"),
    ("smoke1c", "smoke/7e71310d", "05-27"),
    ("smoke2",  "smoke/d3eb9734", "05-27"),
    ("smoke3",  "smoke3/a0d03aed", "05-27"),
    ("smoke4",  "smoke4/4cc77948", "05-27"),
    ("smoke5",  "smoke5/5494f4d0", "05-27"),
    ("smoke6",  "smoke6/17a0b9b6", "05-27"),
    ("smoke7",  "smoke7/1a5c44a8", "05-28"),
    ("smoke8",  "smoke8/25fd3ae4", "05-28"),
]

# 개선/가설·결과 서술 (메모리 + 세션 로그 근거)
NARR = {
    "smoke1a": ("최초 풀 파이프라인 + ninja(JSON·415) 어댑터 도입",
                "discipline-reviewer가 저위험 415 어댑터 슬라이스에서 important 구조개선 적발(미들웨어 승격)",
                "베이스라인 확보 — 파이프라인 첫 완주"),
    "smoke1b": ("베이스라인 반복(주문 1건 구조)",
                "정상 흐름(architect 2·coder 4·감사 2)",
                "베이스라인 ~안정(기계 27m)"),
    "smoke1c": ("베이스라인(주문) — G2 명세 정정 패턴 첫 관측",
                "architect 3회(명세 §3.4 정정 재디스패치 = 후일 진단된 'over-annotated 정합 정정' 낭비)",
                "베이스라인 82m wall, 정정 왕복 씨앗"),
    "smoke2":  ("동시성 기능 — coder 메커니즘 대체 토끼굴 노출(문제 발견)",
                "coder가 명세에 없는 커스텀 BEGIN IMMEDIATE 백엔드 자작(33분) → 홀리스틱 감사 적발 → 다음 coder가 도로 제거. coder 6회·architect 4회",
                "느린 런(164m wall). 토끼굴 = 가드레일 도입 동기"),
    "smoke3":  ("coder 메커니즘 가드레일 + 표준강화(§0/§4/ACL/ninja) 검증",
                "sqlite 데드락 마주치자 coder가 우회 안 만들고 설계로 반송. 최장 슬라이스 5.7분(33분 토끼굴 소멸). §4 명명·ACL 분리 PASS",
                "가드레일 정적·동적 검증 통과"),
    "smoke4":  ("BC 배치 비결정성 노출(같은 프롬프트, 다른 경계)",
                "smoke3은 주문을 별도 order 앱에, smoke4는 catalog 앱 내부에 배치 — 경계가 런마다 달라지는 재현불가 드러남(가볍지만 비결정)",
                "BC 고정 레버 도입 동기"),
    "smoke5":  ("BC 배치 비결정성 수정 검증(G0 배치 고정 + 규칙4 가드)",
                "G0에서 '이 기능 둘 자리' 사용자 확정 → 새 독립 BC orders + catalog ACL 연결. 규칙4 오용 가드 준수",
                "동적검증 PASS · 커밋 15ff62d"),
    "smoke6":  ("extended thinking OFF A/B (vs smoke5)",
                "thinking 21→0 블록. 코디 output cost −50%·총 cost −24%. 테스트 35개 통과(품질 무손실). thinking은 플러그인이 아닌 사용자 세션 설정",
                "✅ 검증된 비용 레버(−24%)"),
    "smoke7":  ("서브에이전트 모델 다운그레이드 A/B (vs smoke6)",
                "architect만 Opus, 나머지 Sonnet. 약한 coder가 게이트 첫 통과 실패로 반송 폭증(coder 2→6·discipline 1→3)",
                "❌ 역효과(시간+14%·비용+47%) — 원복·금지"),
    "smoke8":  ("커밋된 HEAD(15ff62d) 최종 확인 (thinking off)",
                "역대 가장 깨끗: architect 2회(정정 재디스패치 0)·coder 최장 6.5분(토끼굴 0)·테스트 20/20·§0/§4/ACL 전부 충족·OrderModel·BC orders 결정론",
                "🟢 합격 — 회귀 없음. cost 1.58M(최저)·기계 41m"),
}


def load(path):
    out = []
    for line in open(path):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def ts(r):
    t = r.get("timestamp")
    if not t:
        return None
    try:
        return datetime.datetime.fromisoformat(t.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def analyze(rs):
    ev = sorted([(ts(r), r) for r in rs if ts(r)], key=lambda x: x[0])
    wall = (ev[-1][0] - ev[0][0]).total_seconds() / 60 if len(ev) > 1 else 0

    # 서브에이전트 실행 구간 [end-dur, end] (병렬 처리·기계시간 판정용)
    iv = []
    for t, r in ev:
        tur = r.get("toolUseResult")
        if isinstance(tur, dict) and tur.get("totalDurationMs"):
            iv.append((t - datetime.timedelta(seconds=tur["totalDurationMs"] / 1000), t))

    def covered(a, b):
        return any(s < b and a < e for s, e in iv)

    # 기계시간 = wall − 유휴(서브에이전트 구간에 안 걸치는 >120s 갭 = 게이트·자리비움)
    idle = sum((ev[i + 1][0] - ev[i][0]).total_seconds()
               for i in range(len(ev) - 1)
               if (ev[i + 1][0] - ev[i][0]).total_seconds() > 120
               and not covered(ev[i][0], ev[i + 1][0]))
    machine = wall - idle / 60

    # 서브에이전트 병합시간(겹침 제거)
    merged = 0.0
    if iv:
        ivs = sorted(iv)
        cs, ce = ivs[0]
        for s, e in ivs[1:]:
            if s <= ce:
                ce = max(ce, e)
            else:
                merged += (ce - cs).total_seconds()
                cs, ce = s, e
        merged += (ce - cs).total_seconds()
    sub_merged = merged / 60

    # 디스패치 설명 매핑(tool_use id → 설명) + 코디 토큰 + 기능
    idmap = {}
    cc = cr = out = inp = turns = nag = 0
    feature = "?"
    agent_cnt = Counter()
    for r in rs:
        if r.get("type") == "assistant" and not r.get("isSidechain"):
            u = r.get("message", {}).get("usage", {})
            if u:
                turns += 1
                cc += u.get("cache_creation_input_tokens", 0)
                cr += u.get("cache_read_input_tokens", 0)
                out += u.get("output_tokens", 0)
                inp += u.get("input_tokens", 0)
            for c in r.get("message", {}).get("content", []):
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    if c["name"] in ("Agent", "Task"):
                        nag += 1
                        st = c.get("input", {}).get("subagent_type", "?").split(":")[-1]
                        agent_cnt[st] += 1
                        idmap[c["id"]] = (st, (c.get("input", {}).get("description") or "")[:34])
                    if c["name"] == "AskUserQuestion" and feature == "?":
                        qs = c.get("input", {}).get("questions", [])
                        if qs:
                            feature = qs[0].get("question", "")[:60]

    # 타임라인: 순서대로 (agent, desc, dur_min, tokens)
    timeline = []
    for r in rs:
        tur = r.get("toolUseResult")
        if isinstance(tur, dict) and tur.get("totalDurationMs") is not None:
            tuid = None
            c = r.get("message", {}).get("content")
            if isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        tuid = b.get("tool_use_id")
            agent, desc = idmap.get(tuid, (tur.get("agentType", "?"), ""))
            timeline.append((agent, desc, tur["totalDurationMs"] / 1000 / 60, tur.get("totalTokens", 0)))

    raw = cc + cr + out + inp
    cost = cr * COST_W["cache_read"] + cc * COST_W["cache_creation"] + inp + out * COST_W["output"]
    return dict(wall=wall, machine=machine, sub_merged=sub_merged, turns=turns, nag=nag,
                agent_cnt=dict(agent_cnt), raw=raw, cost=cost, cr=cr, out=out,
                feature=feature, timeline=timeline)


def main():
    data = []
    for label, sp, date in SESSIONS:
        fs = glob.glob(os.path.join(PROJ, f"-Users-hyun-Desktop-dddjango-{sp}*.jsonl"))
        if not fs:
            continue
        sid = sp.split("/")[-1]
        a = analyze(load(fs[0]))
        a.update(label=label, sid=sid, date=date)
        data.append(a)

    rows_html = []
    timelines_html = []
    for d in data:
        imp, ev, res = NARR.get(d["label"], ("", "", ""))
        agents = " ".join(f"{k.split('-')[0]}{v}" for k, v in d["agent_cnt"].items())
        cls = "slow" if d["label"] == "smoke2" else ("bad" if d["label"] == "smoke7" else
              ("good" if d["label"] in ("smoke3", "smoke5", "smoke6", "smoke8") else ""))
        rows_html.append(f"""<tr class="{cls}">
<td class="lbl"><a href="#tl-{d['label']}">{d['label']}</a><br><span class="sid">{d['sid']}<br>{d['date']}</span></td>
<td class="feat">{d['feature']}</td>
<td class="imp">{imp}</td>
<td class="ev">{ev}</td>
<td class="num"><b>{d['machine']:.0f}</b><br><span class="muted">{d['wall']:.0f}</span></td>
<td class="num">{d['nag']}<br><span class="muted">{d['turns']}턴</span><br><span class="ag">{agents}</span></td>
<td class="num">{d['raw']/1e6:.1f}<br><span class="muted">{d['cost']/1e6:.1f}</span></td>
<td class="res">{res}</td>
</tr>""")

        # smoke별 펼침 타임라인
        maxdur = max((t[2] for t in d["timeline"]), default=1) or 1
        tl_rows = []
        for i, (agent, desc, dur, tok) in enumerate(d["timeline"], 1):
            barw = int(dur / maxdur * 160)
            hot = "hot" if dur >= 15 else ""
            tl_rows.append(f"""<tr>
<td class="num muted">{i}</td><td class="agc">{agent}</td><td class="feat">{desc}</td>
<td class="num {hot}"><b>{dur:.1f}</b></td>
<td><div class="bar {hot}" style="width:{barw}px"></div></td>
<td class="num">{tok:,}</td></tr>""")
        sub_sum = sum(t[2] for t in d["timeline"])
        coord = d["machine"] - d["sub_merged"]
        timelines_html.append(f"""<details id="tl-{d['label']}" class="tl {cls}">
<summary><b>{d['label']}</b> · {d['feature'][:45]} · 기계 {d['machine']:.0f}m (서브병합 {d['sub_merged']:.0f}m + 코디 {coord:.0f}m) · 디스패치 {d['nag']}회</summary>
<table class="tlt"><thead><tr><th>#</th><th>에이전트</th><th>작업</th><th>소요분</th><th>　</th><th>토큰</th></tr></thead>
<tbody>{''.join(tl_rows)}</tbody>
<tfoot><tr><td colspan="3">디스패치 소요 합(직렬 기준 {sub_sum:.0f}m, 병렬 리뷰어 겹침 제거 시 {d['sub_merged']:.0f}m)</td>
<td class="num"><b>{sub_sum:.0f}</b></td><td></td><td></td></tr></tfoot></table>
</details>""")

    html = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<title>dddjango smoke1~7 비교 분석</title>
<style>
body{{font-family:-apple-system,'Apple SD Gothic Neo',sans-serif;margin:24px;color:#1a1a1a;background:#fafafa}}
h1{{font-size:20px}} .note{{color:#666;font-size:12px;margin-bottom:14px;line-height:1.6}}
table{{border-collapse:collapse;width:100%;font-size:12.5px;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
th,td{{border:1px solid #e3e3e3;padding:7px 9px;vertical-align:top;text-align:left}}
th{{background:#2d3748;color:#fff;font-size:12px;position:sticky;top:0}}
.lbl{{font-weight:700;white-space:nowrap}} .sid{{font-weight:400;color:#999;font-size:10px}}
.num{{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}}
.muted{{color:#999;font-size:10.5px}} .ag{{color:#3182ce;font-size:10px}}
.imp{{font-weight:600;color:#2b6cb0}} .feat{{color:#444;font-size:11.5px}}
.ev{{color:#555;font-size:11px;line-height:1.5}} .res{{font-size:11px;line-height:1.5}}
tr.slow{{background:#fff5f5}} tr.bad{{background:#fff0f0}} tr.good{{background:#f0fff4}}
tr.slow .lbl,tr.bad .lbl{{color:#c53030}} tr.good .lbl{{color:#276749}}
.legend{{margin-top:12px;font-size:11px;color:#666;line-height:1.7}}
.lbl a{{color:inherit;text-decoration:none;border-bottom:1px dotted #aaa}}
h2{{font-size:15px;margin:26px 0 8px}}
details.tl{{margin:6px 0;border:1px solid #e0e0e0;border-radius:5px;background:#fff;padding:4px 10px}}
details.tl summary{{cursor:pointer;font-size:12.5px;padding:4px 0}}
details.tl.slow summary,details.tl.bad summary{{color:#c53030}} details.tl.good summary{{color:#276749}}
table.tlt{{margin:8px 0 4px;font-size:11.5px;box-shadow:none}}
table.tlt th{{background:#edf2f7;color:#2d3748;position:static}}
table.tlt td{{padding:3px 8px;border:1px solid #eee}}
.agc{{color:#3182ce;white-space:nowrap;font-size:11px}}
.bar{{height:11px;background:#90cdf4;border-radius:2px}} .bar.hot{{background:#fc8181}}
td.hot{{color:#c53030}}
table.tlt tfoot td{{background:#fafafa;font-size:10.5px;color:#666}}
</style></head><body>
<h1>dddjango /dddjango 파이프라인 — smoke1~7 비교 분석</h1>
<div class="note">
폴더 번호는 <b>smoke3부터</b> 붙었고, smoke1·smoke2는 공유 <code>-smoke</code> 폴더에 실행 4개가 섞여 있어 a/b/c로 세분(smoke2=d3eb9734=164분 느린 런만 메모리로 확정).
<b>기계시간</b>=사람 대기(게이트 승인) 제외 활성 시간 / <span class="muted">회색=wall(대기 포함)</span>.
<b>토큰</b>=코디네이터 raw(M) / <span class="muted">회색=cost 가중단위(M): cache_read×0.1·cache_creation×1.25·output×5</span>.
</div>
<table>
<thead><tr>
<th>smoke</th><th>만든 기능(G0 질문)</th><th>개선·검증한 가설</th><th>주요 이벤트</th>
<th>기계분<br><span style="font-weight:400">/wall</span></th><th>서브콜<br><span style="font-weight:400">/턴</span></th>
<th>raw M<br><span style="font-weight:400">/cost</span></th><th>결과</th>
</tr></thead>
<tbody>
{''.join(rows_html)}
</tbody></table>
<div class="legend">
<b>읽는 법</b> — 만든 기능은 대부분 "주문+재고 차감"으로 유사하므로, 분석축은 <b>'개선·검증한 가설'</b> 열이다.
빨강=문제/역효과 런(smoke2 토끼굴·smoke7 모델 다운그레이드), 초록=검증·이득 런(smoke3 가드레일·smoke5 BC고정·smoke6 thinking off).
기계시간(사람 대기 제외)은 ~47~60분에 수렴(smoke2만 114분=33분 토끼굴) → 품질우선 다단계·게이트·TDD 설계에 내재. smoke 라벨을 누르면 단계별 타임라인으로 이동.
</div>

<h2>smoke별 단계 타임라인 — 어디서 시간·토큰이 들었나 (펼치기)</h2>
<div class="note">각 디스패치의 소요분(빨강 막대=15분↑ 병목)과 토큰. 설계 리뷰어 3종은 병렬이라 직렬 합보다 병합시간이 짧다. 코디네이터 오케스트레이션 = 기계시간 − 서브병합.</div>
{''.join(timelines_html)}
</body></html>"""

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smoke_timeline.html")
    with open(out_path, "w") as fh:
        fh.write(html)
    print(f"생성: {out_path}")
    for d in data:
        print(f"  {d['label']:8s} machine={d['machine']:5.1f}m wall={d['wall']:6.1f}m "
              f"turns={d['turns']:3d} agent={d['nag']:2d} raw={d['raw']/1e6:5.2f}M "
              f"cost={d['cost']/1e6:5.2f}M cr={d['cr']/1e6:5.2f}M")


if __name__ == "__main__":
    main()
