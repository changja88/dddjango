# CY1 — BC 순환 래칫. 게이트: 전역 + 베이스라인.
#
# *왜 결정적 백스톱인가*: 순환은 두 BC의 합작이라 touched 한정이 불가능한 유일한
# 검사다. BC 참조 그래프(Python import(함수 안 포함) + 템플릿 include·static + CSS 참조 — 같은 BC 안
# router↔navigator 같은 내부 간선은 세지 않는다 · 합법 4채널 포함, §9-15는 채널
# 무관)의 SCC에서 같은 컴포넌트에 속한 무순서쌍을 산출하고, 베이스라인
# (`.dddjango-web/backstop-baseline.json`, 커밋 대상)에 없는 신규 쌍만 blocker. 쌍 단위인 이유:
# 경로는 리팩터링으로 형태가 바뀌어도 같은 순환이 남는다 — "A와 B가 서로에게 닿는가"가 안정적 최소 단위.
# (판형: dddart check_cycles.dart)

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

from .common import BackstopContext, Finding, bc_of, ref_path

BASELINE: str = '.dddjango-web/backstop-baseline.json'


def run_cycles(ctx: BackstopContext, update_baseline: bool) -> List[Finding]:
    out: List[Finding] = []

    # BC 그래프 (전역 — 게이트 없음)
    edges: Dict[str, Set[str]] = {}
    for f in ctx.files:
        a: Optional[str] = bc_of(ref_path(f), ctx.areas)
        if a is None:
            continue
        for e in ctx.edges_of(f):
            if not e.internal or not e.target:
                continue
            b: Optional[str] = bc_of(ref_path(e.target), ctx.areas)
            if b is not None and b != a:
                edges.setdefault(a, set()).add(b)
    nodes: Set[str] = set(edges) | {x for s in edges.values() for x in s}

    current: Set[str] = {'|'.join(sorted(p)) for p in _scc_pairs(nodes, edges)}

    baseline_file: Path = ctx.root / BASELINE
    if not baseline_file.exists():
        baseline_file.parent.mkdir(parents=True, exist_ok=True)
        _write(baseline_file, current)
        ctx.notices.append('[info] CY1 베이스라인 생성 — 현재 순환 쌍 %d개 동결 '
                           '(%s — 커밋하고 다음 게이트 배너에 표면화할 것)' % (len(current), BASELINE))
        return out
    try:
        data = json.loads(baseline_file.read_text(encoding='utf-8'))
        baseline: Set[str] = {'|'.join(sorted(p)) for p in data['cycle_pairs']}
    except (ValueError, KeyError, TypeError) as exc:
        print('[backstop] 사용 오류: %s 해석 불가 — %s' % (BASELINE, exc), file=sys.stderr)
        sys.exit(1)
    if update_baseline:
        _write(baseline_file, current)
        ctx.notices.append('[info] CY1 베이스라인 갱신 — %d쌍 → %d쌍' % (len(baseline), len(current)))
        return out

    for key in sorted(current - baseline):
        p: List[str] = key.split('|')
        out.append(Finding('CY1', 'application/%s ↔ application/%s' % (p[0], p[1]), None,
            'BC 신규 순환 — `%s`와 `%s`가 서로에게 닿는다(직·간접)' % (p[0], p[1]), '제1 규약 §9-15',
            '합법 채널 참조의 조합도 순환이면 blocker다 — 한쪽 의존을 끊는다: 화면 이동이면 root 경유 진입 URL'
            '(root_destination_handler)로, 데이터면 방향을 정해 한쪽만 UseCase를 호출하게. '
            '의도된 구조면 사용자 승인 후 --update-baseline.'))
    stale: Set[str] = baseline - current
    if stale:
        ctx.notices.append('[info] CY1 베이스라인에 있으나 현재 미발생인 쌍 %d개(%s) — --update-baseline 권장(래칫 되감기)'
                           % (len(stale), ', '.join(s.replace('|', '↔') for s in sorted(stale))))
    return out


def _write(f: Path, pair_keys: Set[str]) -> None:
    pairs: List[List[str]] = [k.split('|') for k in sorted(pair_keys)]
    f.write_text(json.dumps({'cycle_pairs': pairs}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def _scc_pairs(nodes: Set[str], edges: Dict[str, Set[str]]) -> List[List[str]]:
    """Tarjan SCC(반복형 — 깊은 그래프에서 재귀 한도 회피) → 같은 컴포넌트 무순서쌍."""
    index: Dict[str, int] = {}
    low: Dict[str, int] = {}
    on_stack: Set[str] = set()
    stack: List[str] = []
    pairs: List[List[str]] = []
    counter: int = 0
    for v0 in sorted(nodes):
        if v0 in index:
            continue
        work: List[tuple] = [(v0, iter(sorted(edges.get(v0, ()))))]
        index[v0] = low[v0] = counter
        counter += 1
        stack.append(v0)
        on_stack.add(v0)
        while work:
            v, it = work[-1]
            advanced: bool = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter
                    counter += 1
                    stack.append(w)
                    on_stack.add(w)
                    work.append((w, iter(sorted(edges.get(w, ())))))
                    advanced = True
                    break
                if w in on_stack:
                    low[v] = min(low[v], index[w])
            if advanced:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[v])
            if low[v] == index[v]:
                comp: List[str] = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                if len(comp) > 1:
                    comp.sort()
                    for i in range(len(comp)):
                        for j in range(i + 1, len(comp)):
                            pairs.append([comp[i], comp[j]])
    return pairs
