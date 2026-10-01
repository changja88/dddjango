#!/usr/bin/env python3
"""lane_metrics — 현장 레인 세션 기록에서 속도 지표를 뽑아 기준 레인과 나란히 비교한다(읽기 전용).

세션 기록만 읽는다. 레인 워크트리는 `--repo` 를 줄 때만 `git log`·`git cat-file`(읽기)로 명세 크기를 잰다.

사용
  # Claude Code 레인 — ~/.claude/projects/<레인 워크트리를 바꾼 이름>/ 아래 메인 세션과 서브에이전트 기록
  python3 workspace/tools/lane_metrics.py claude ~/.claude/projects/-Users-hyun--herdr-worktrees-spring-dream-server-lane-8-C-0 \
      [--session <세션 id> ...] [--since 2026-09-30T03:41] [--until 2026-09-30T21:47] [--repo <레인 워크트리>] --out new.json
  # Codex 레인 — ~/.codex/sessions/**/rollout-*.jsonl 가운데 cwd 가 레인 워크트리인 것
  python3 workspace/tools/lane_metrics.py codex ~/.herdr/worktrees/spring_dream_server/lane-6-3-11 [--since …] [--until …] --out p1.json
  # 나란히 비교(첫 파일이 기준)
  python3 workspace/tools/lane_metrics.py compare base.json new.json [--md out.md]

시각 인자에 시간대가 없으면 KST(+09:00)로 읽는다.
"""
import argparse
import collections
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))
COLD_WRITE = 100_000          # 요청 하나의 캐시 쓰기가 이보다 크면 «대화 전체 재처리»로 센다
ROUND_GAP_S = 15 * 60         # 리뷰어 호출 시작이 이 간격 안이면 같은 라운드
REVIEWER_ROLES = {'design-review-ddd', 'design-review-api', 'design-review-db', 'discipline-reviewer',
                  'design-review-web', 'discipline-reviewer-web'}
CMD_CATS = [  # (분류, 정규식) — 위에서부터 첫 일치
    ('pregate', r'design_pregate'),
    ('registry_gate', r'registry_gate'),
    ('w8_census', r'style_census|compare_style_census'),
    ('design_evidence', r'check_design_evidence|render_audit'),
    ('backstop', r'backstop\.py'),
    ('debt_scan', r'--debt-scan|check-[a-z0-9-]+\.py'),
    ('tests', r'\bpytest\b|make test|manage\.py test'),
    ('git', r'^\s*git\b'),
]
MARKERS = ['TREE_CONTRACT_MISMATCH', 'ARRANGE_BLOCKED', 'G1′', 'G1″', 'G1‴']


def P(ts):
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))


def parse_when(s):
    if not s:
        return None
    d = datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=KST)


def kst(d):
    return d.astimezone(KST).strftime('%m-%d %H:%M') if d else None


def in_window(t, since, until):
    return (since is None or t >= since) and (until is None or t <= until)


def merge(intervals):
    out = []
    for a, b in sorted(i for i in intervals if i[1] > i[0]):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def total_min(intervals):
    return sum((b - a).total_seconds() for a, b in merge(intervals)) / 60


def minus_min(intervals, minus):
    """intervals 합집합에서 minus 합집합과 겹치는 부분을 뺀 분."""
    a, m = merge(intervals), merge(minus)
    tot = 0.0
    for s, e in a:
        cut = s
        for ms, me in m:
            if me <= cut or ms >= e:
                continue
            if ms > cut:
                tot += (ms - cut).total_seconds()
            cut = max(cut, me)
        if cut < e:
            tot += (e - cut).total_seconds()
    return tot / 60


def cmd_cat(cmd):
    for name, rx in CMD_CATS:
        if re.search(rx, cmd or ''):
            return name
    return 'other'


def clip(a, b, since, until):
    if since and a < since:
        a = since
    if until and b > until:
        b = until
    return (a, b) if b > a else None


def new_role():
    return {'agents': 0, 'requests': 0, 'model_min': 0.0, 'tool_min': 0.0, 'input_sum': 0, 'input_max': 0,
            'cache_write': 0, 'cache_read': 0, 'output': 0, 'cold_rewrites': 0, 'compacts': 0}


def finish_roles(roles):
    out = {}
    for r, v in sorted(roles.items()):
        n = v['requests'] or 1
        out[r] = {'agents': v['agents'], 'requests': v['requests'], 'model_min': round(v['model_min'], 1),
                  'tool_min': round(v['tool_min'], 1), 'avg_input_k': round(v['input_sum'] / n / 1000, 1),
                  'max_input_k': round(v['input_max'] / 1000, 1), 'cache_write_M': round(v['cache_write'] / 1e6, 2),
                  'cache_read_M': round(v['cache_read'] / 1e6, 1), 'output_k': round(v['output'] / 1000, 1),
                  'cold_rewrites': v['cold_rewrites'], 'compacts': v['compacts']}
    return out


def spec_sizes(repo, since, until, build=None):
    """레인 워크트리의 `.dddjango*/*/design-spec.md` 커밋별 크기(읽기 전용 git)."""
    if not repo:
        return None
    try:
        log = subprocess.run(['git', '-C', repo, 'log', '--format=@@%H %cI', '--name-only', '--',
                              '.dddjango/*/design-spec.md', '.dddjango-web/*/design-spec.md'],
                             capture_output=True, text=True, check=True).stdout
    except Exception as e:  # noqa: BLE001 — 측정 도구: 실패는 결과에 적고 계속한다
        return {'error': str(e)}
    rows, cur = [], None
    for line in log.splitlines():
        if line.startswith('@@'):
            h, t = line[2:].split(' ', 1)
            cur = (h, P(t))
        elif line.strip() and cur and in_window(cur[1], since, until):
            try:
                size = int(subprocess.run(['git', '-C', repo, 'cat-file', '-s', f'{cur[0]}:{line.strip()}'],
                                          capture_output=True, text=True, check=True).stdout)
            except Exception:  # noqa: BLE001 — 지운 판 등
                continue
            rows.append({'commit': cur[0][:9], 'at': kst(cur[1]), 'path': line.strip(), 'bytes': size})
    rows.reverse()
    per = collections.Counter(r['path'] for r in rows)
    others = {k: v for k, v in per.items()}
    pick = build if build else (per.most_common(1)[0][0] if per else None)
    rows = [r for r in rows if pick and (r['path'] == pick or r['path'].split('/')[1] == pick)]
    sizes = [r['bytes'] for r in rows]
    return {'revisions': len(rows), 'first_kb': round(sizes[0] / 1024) if sizes else None,
            'last_kb': round(sizes[-1] / 1024) if sizes else None, 'max_kb': round(max(sizes) / 1024) if sizes else None,
            'path': rows[0]['path'] if rows else None, 'all_paths': others, 'rows': rows}


# ----------------------------------------------------------------------------------------------- Claude Code
def claude_events(path):
    """한 기록 파일 → (사건 목록, 요청별 usage, tool_use 사전, 원문 줄 목록)."""
    evs, reqs, uses, lines = [], {}, {}, []
    for line in open(path, encoding='utf-8'):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        ts, t = d.get('timestamp'), d.get('type')
        if not ts:
            continue
        lines.append(d)
        when = P(ts)
        if t == 'assistant':
            m = d.get('message', {})
            rid = d.get('requestId') or m.get('id')
            if m.get('usage') and rid:
                reqs[rid] = m['usage']
            names = []
            for b in m.get('content', []) or []:
                if isinstance(b, dict) and b.get('type') == 'tool_use':
                    uses[b['id']] = {'name': b['name'], 'ts': when, 'input': b.get('input') or {}}
                    names.append(b['name'])
            evs.append((when, 'A', None))
        elif t == 'user':
            c = d.get('message', {}).get('content')
            if isinstance(c, list) and any(isinstance(b, dict) and b.get('type') == 'tool_result' for b in c):
                for b in c:
                    if isinstance(b, dict) and b.get('type') == 'tool_result' and b.get('tool_use_id') in uses:
                        uses[b['tool_use_id']]['rts'] = when
                first = next((b for b in c if isinstance(b, dict) and b.get('type') == 'tool_result'), {})
                evs.append((when, 'R', uses.get(first.get('tool_use_id'), {}).get('name', '?')))
            else:
                txt = c if isinstance(c, str) else ' '.join(b.get('text', '') for b in (c or []) if isinstance(b, dict))
                if '<task-notification>' in txt:
                    kind = 'notif'
                elif 'Subagent hand-back' in txt or 'agent-message' in txt:
                    kind = 'handback'
                elif d.get('isCompactSummary'):
                    kind = 'compact'
                elif d.get('isMeta'):
                    kind = 'meta'
                else:
                    kind = 'human'
                evs.append((when, 'U', kind))
        elif t == 'system' and d.get('subtype') == 'compact_boundary':
            evs.append((when, 'C', None))
        elif t == 'system' and d.get('subtype') == 'informational':
            evs.append((when, 'I', d.get('content') or ''))
    evs.sort(key=lambda e: e[0])
    return evs, reqs, uses, lines


def gap_intervals(evs, since, until):
    """연속 사건 사이 구간을 뒤 사건 종류로 분류: model · tool · compact · limit · idle."""
    out = collections.defaultdict(list)
    for (t0, _k0, _x0), (t1, k1, x1) in zip(evs, evs[1:]):
        iv = clip(t0, t1, since, until)
        if not iv:
            continue
        if k1 == 'A':
            cat = 'model'
        elif k1 == 'R':
            cat = 'tool'
        elif k1 == 'C':
            cat = 'compact'
        elif k1 == 'I':
            cat = 'limit' if re.search(r'reset|limit', x1 or '', re.I) else 'model'
        else:
            cat = 'idle'
        out[cat].append(iv)
    return out


def add_usage(role, reqs):
    for u in reqs.values():
        inp = (u.get('input_tokens', 0) + u.get('cache_read_input_tokens', 0) + u.get('cache_creation_input_tokens', 0))
        role['requests'] += 1
        role['input_sum'] += inp
        role['input_max'] = max(role['input_max'], inp)
        role['cache_write'] += u.get('cache_creation_input_tokens', 0)
        role['cache_read'] += u.get('cache_read_input_tokens', 0)
        role['output'] += u.get('output_tokens', 0)
        if u.get('cache_creation_input_tokens', 0) > COLD_WRITE:
            role['cold_rewrites'] += 1


def window_reqs(lines, since, until):
    reqs = {}
    for d in lines:
        if d.get('type') != 'assistant' or not in_window(P(d['timestamp']), since, until):
            continue
        m = d.get('message', {})
        rid = d.get('requestId') or m.get('id')
        if m.get('usage') and rid:
            reqs[rid] = m['usage']
    return reqs


def text_of(d):
    c = d.get('message', {}).get('content')
    if isinstance(c, str):
        return c
    parts = []
    for b in c or []:
        if not isinstance(b, dict):
            continue
        if b.get('type') == 'text':
            parts.append(b.get('text', ''))
        elif b.get('type') == 'tool_result':
            r = b.get('content')
            parts.append(r if isinstance(r, str) else ' '.join(x.get('text', '') for x in r or [] if isinstance(x, dict)))
    return '\n'.join(parts)


def run_claude(a):
    since, until = parse_when(a.since), parse_when(a.until)
    base = os.path.expanduser(a.path.rstrip('/'))
    mains = sorted(glob.glob(os.path.join(base, '*.jsonl')))
    if a.session:
        mains = [m for m in mains if os.path.basename(m)[:-6] in a.session]
    active, limit, roles = [], [], collections.defaultdict(new_role)
    bash = collections.defaultdict(lambda: {'n': 0, 'min': 0.0, 'bg_n': 0, 'bg_min': 0.0})
    sub_bash = collections.Counter()
    spawns, sends = [], 0
    note_bytes = 0
    markers = collections.Counter()
    human = {'messages': 0, 'rejections': 0}
    versions = collections.Counter()
    first = last = None
    sessions_used = []
    for mpath in mains:
        evs, _reqs, uses, lines = claude_events(mpath)
        if not any(in_window(e[0], since, until) for e in evs):
            continue
        sid = os.path.basename(mpath)[:-6]
        sessions_used.append(sid)
        ws = [e[0] for e in evs if in_window(e[0], since, until)]
        first = min(filter(None, [first, ws[0]]))
        last = max(filter(None, [last, ws[-1]]))
        g = gap_intervals(evs, since, until)
        active += g['model'] + g['tool'] + g['compact']
        limit += g['limit']
        role = roles['main']
        role['agents'] += 1
        role['model_min'] += total_min(g['model'])
        role['tool_min'] += total_min(g['tool'])
        role['compacts'] += sum(1 for e in evs if e[1] == 'C' and in_window(e[0], since, until))
        add_usage(role, window_reqs(lines, since, until))
        raw = open(mpath, encoding='utf-8').read()
        versions.update(re.findall(r'plugins/cache/[^/"\s]+/(dddjango(?:-web)?)/(\d+\.\d+\.\d+)', raw))
        # 메인 도구 사용
        notif_end = {}
        for d in lines:
            if d.get('type') == 'user':
                for tid in re.findall(r'<tool-use-id>(toolu_[A-Za-z0-9]+)</tool-use-id>', text_of(d)):
                    notif_end.setdefault(tid, P(d['timestamp']))
        for uid, u in uses.items():
            if not in_window(u['ts'], since, until):
                continue
            name, inp = u['name'], u['input']
            if name == 'Bash':
                cat = cmd_cat(inp.get('command', ''))
                if inp.get('run_in_background'):
                    end = notif_end.get(uid)
                    bash[cat]['bg_n'] += 1
                    if end:
                        iv = clip(u['ts'], end, since, until)
                        if iv:
                            active.append(iv)
                            bash[cat]['bg_min'] += (iv[1] - iv[0]).total_seconds() / 60
                else:
                    bash[cat]['n'] += 1
                    if u.get('rts'):
                        bash[cat]['min'] += (u['rts'] - u['ts']).total_seconds() / 60
                if re.search(r'cat\s*>.*(review|note|노트)', inp.get('command', ''), re.I):
                    note_bytes += len(inp.get('command', '').encode())
            elif name == 'Write' and re.search(r'(review|note|노트)', inp.get('file_path', ''), re.I):
                note_bytes += len((inp.get('content') or '').encode())
            elif name == 'Agent':
                spawns.append((u['ts'], inp.get('subagent_type', '?'), inp.get('description', '') or ''))
            elif name == 'SendMessage':
                sends += 1
        agent_ids = {uid for uid, u in uses.items() if u['name'] == 'Agent'}
        for d in lines:
            if not in_window(P(d['timestamp']), since, until):
                continue
            txt = text_of(d)
            c = d.get('message', {}).get('content')
            report = d.get('type') == 'user' and (
                'hand-back' in txt or (isinstance(c, list) and any(isinstance(b, dict) and b.get('type') == 'tool_result'
                                                                   and b.get('tool_use_id') in agent_ids for b in c)))
            if report:
                for mk in MARKERS:
                    if mk in txt:
                        markers[mk] += 1
            if d.get('type') == 'user' and isinstance(d.get('message', {}).get('content'), str) \
                    and not d.get('isMeta') and '<task-notification>' not in txt and 'hand-back' not in txt:
                human['messages'] += 1
                if '반송' in txt:
                    human['rejections'] += 1
        # 서브에이전트
        for f in sorted(glob.glob(os.path.join(base, sid, 'subagents', 'agent-*.jsonl'))):
            meta_p = f[:-6] + '.meta.json'
            meta = json.load(open(meta_p, encoding='utf-8')) if os.path.exists(meta_p) else {}
            rname = (meta.get('agentType') or 'sub').split(':')[-1]
            sevs, _sreqs, suses, slines = claude_events(f)
            if not any(in_window(e[0], since, until) for e in sevs):
                continue
            sws = [e[0] for e in sevs if in_window(e[0], since, until)]
            first, last = min(first, sws[0]), max(last, sws[-1])
            sg = gap_intervals(sevs, since, until)
            active += sg['model'] + sg['tool'] + sg['compact']
            r = roles[rname]
            r['agents'] += 1
            r['model_min'] += total_min(sg['model'])
            r['tool_min'] += total_min(sg['tool'])
            r['compacts'] += sum(1 for e in sevs if e[1] == 'C' and in_window(e[0], since, until))
            add_usage(r, window_reqs(slines, since, until))
            for u in suses.values():
                if u['name'] == 'Bash' and in_window(u['ts'], since, until):
                    c = cmd_cat(u['input'].get('command', ''))
                    if c in ('pregate', 'registry_gate'):
                        sub_bash[f'{rname}:{c}'] += 1
    if first is None:
        sys.exit('창 안에 사건이 없다 — 경로·--since·--until 을 확인')
    wall = (last - first).total_seconds() / 60
    work = total_min(active)
    limit_only = minus_min(limit, active)
    rounds = review_rounds([s for s in spawns if s[1].split(':')[-1] in REVIEWER_ROLES
                            and not re.search(r'감사|audit|UNIT_AUDIT', s[2], re.I)])
    return {
        'runtime': 'claude', 'source': base, 'sessions': sessions_used,
        'window': {'first': kst(first), 'last': kst(last)},
        'plugin_versions': ['%s %s ×%d' % (k[0], k[1], n) for k, n in versions.most_common()],
        'time': {'wall_min': round(wall, 1), 'work_min': round(work, 1), 'limit_min': round(limit_only, 1),
                 'idle_min': round(wall - work - limit_only, 1)},
        'roles': finish_roles(roles),
        'main_commands': {k: {kk: round(vv, 1) if isinstance(vv, float) else vv for kk, vv in v.items()}
                          for k, v in sorted(bash.items())},
        'sub_gate_runs': dict(sub_bash),
        'spawns': dict(collections.Counter(s[1].split(':')[-1] for s in spawns)),
        'send_message': sends,
        'review_rounds': rounds,
        'main_note_bytes': note_bytes,
        'markers': dict(markers),
        'human': human,
        'spec': spec_sizes(a.repo, since, until, a.build),
    }


def review_rounds(spawns):
    rounds, cur = [], None
    for t, *_rest in sorted(spawns, key=lambda s: s[0]):
        if cur and (t - cur['last']).total_seconds() <= ROUND_GAP_S:
            cur['n'] += 1
            cur['last'] = t
        else:
            cur = {'start': t, 'last': t, 'n': 1}
            rounds.append(cur)
    return {'count': len(rounds), 'starts': [f"{kst(r['start'])}×{r['n']}" for r in rounds]}


# ----------------------------------------------------------------------------------------------- Codex
def coarse_role(name):
    """Codex 하위 스레드는 역할 대신 작업 이름(`/root/coder_slice_1`)으로 남는다 — 비교용으로 역할 묶음을 만든다."""
    n = name.lower()
    for key, role in (('guardian', 'guardian'), ('architect', 'design-architect'), ('coder', 'coder'),
                      ('visual', 'visual'), ('audit', 'discipline-audit'), ('discipline', 'discipline-audit'),
                      ('review', 'review'), ('accept', 'acceptance-tester')):
        if key in n:
            return role
    return 'other-sub'


def run_codex(a):
    since, until = parse_when(a.since), parse_when(a.until)
    lane = os.path.realpath(os.path.expanduser(a.path))
    files = []
    for f in glob.glob(os.path.expanduser('~/.codex/sessions/*/*/*/rollout-*.jsonl')):
        try:
            with open(f, encoding='utf-8') as fh:
                d = json.loads(fh.readline())
        except (ValueError, OSError):
            continue
        p = d.get('payload', {})
        if d.get('type') == 'session_meta' and os.path.realpath(p.get('cwd', '')).startswith(lane):
            files.append((f, p))
    active, roles, threads = [], collections.defaultdict(new_role), collections.defaultdict(new_role)
    cmds = collections.defaultdict(lambda: {'n': 0, 'min': 0.0})
    calls = collections.Counter()
    wait_timeouts = 0
    markers = collections.Counter()
    human = {'messages': 0, 'rejections': 0}
    first = last = None
    used = []
    for f, meta in files:
        src = meta.get('source')
        if isinstance(src, dict) and 'subagent' in src:
            sp = src['subagent'].get('thread_spawn') if isinstance(src['subagent'], dict) else None
            rname = (sp or {}).get('agent_role') or (sp or {}).get('agent_path') or 'guardian'
            tname = str(rname).split('/')[-1]
            rname = coarse_role(tname)
        else:
            rname = tname = 'main'
        r = roles[rname]
        th = threads[tname]
        started, pend, seen = None, {}, False
        task_ms = 0.0
        tool_iv = []
        for line in open(f, encoding='utf-8'):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            ts = d.get('timestamp')
            if not ts:
                continue
            t = P(ts)
            if not in_window(t, since, until):
                continue
            seen = True
            first = t if first is None or t < first else first
            last = t if last is None or t > last else last
            p = d.get('payload', {}) if isinstance(d.get('payload'), dict) else {}
            typ, pt = d.get('type'), p.get('type')
            if typ == 'event_msg' and pt == 'task_started':
                started = t
            elif typ == 'event_msg' and pt in ('task_complete', 'turn_aborted'):
                if rname != 'main':
                    for mk in MARKERS:
                        if mk in (p.get('last_agent_message') or ''):
                            markers[mk] += 1
                if started:
                    active.append((started, t))
                    task_ms += (t - started).total_seconds() * 1000
                started = None
            elif typ == 'token_usage_record':
                u = p.get('usage', {})
                inp = u.get('input_tokens', 0)
                r['requests'] += 1
                r['input_sum'] += inp
                r['input_max'] = max(r['input_max'], inp)
                r['cache_read'] += u.get('cached_input_tokens', 0)
                r['cache_write'] += u.get('cache_write_input_tokens', 0)
                r['output'] += u.get('output_tokens', 0)
            elif typ == 'compacted':
                r['compacts'] += 1
            elif typ == 'response_item' and pt in ('function_call', 'custom_tool_call'):
                name = p.get('name', '?')
                args = p.get('arguments') or p.get('input') or ''
                pend[p.get('call_id')] = (t, name, args)
                if rname == 'main':
                    calls[name] += 1
            elif typ == 'response_item' and pt in ('function_call_output', 'custom_tool_call_output'):
                st = pend.pop(p.get('call_id'), None)
                if st:
                    tool_iv.append((st[0], t))
                    out = p.get('output')
                    out = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)
                    if st[1] == 'wait_agent' and re.search(r'timed out', out or '', re.I):
                        wait_timeouts += 1
                    if rname == 'main' or st[1] not in ('wait_agent',):
                        c = cmd_cat(st[2] if isinstance(st[2], str) else json.dumps(st[2]))
                        if c != 'other' and rname == 'main':
                            cmds[c]['n'] += 1
                            cmds[c]['min'] += (t - st[0]).total_seconds() / 60
            elif typ == 'event_msg' and pt == 'item_completed' and rname == 'main':
                it = p.get('item', {})
                if it.get('type') == 'UserMessage':
                    txt = ' '.join(x.get('text', '') for x in it.get('content', []) if isinstance(x, dict))
                    human['messages'] += 1
                    if '반송' in txt:
                        human['rejections'] += 1
        if not seen:
            continue
        used.append(os.path.basename(f))
        r['agents'] += 1
        tool = total_min(tool_iv)
        r['tool_min'] += tool
        r['model_min'] += max(task_ms / 60000 - tool, 0)
        if tname != 'main':
            th['agents'] += 1
            th['tool_min'] += tool
            th['model_min'] += max(task_ms / 60000 - tool, 0)
    if first is None:
        sys.exit('창 안에 사건이 없다 — 경로·--since·--until 을 확인')
    wall = (last - first).total_seconds() / 60
    work = total_min(active)
    versions = collections.Counter()
    for f, meta in files:
        if os.path.basename(f) in used and not isinstance(meta.get('source'), dict):
            raw = open(f, encoding='utf-8').read()
            versions.update(re.findall(r'plugins/cache/[^/"\s]+/(dddjango(?:-web)?)/(\d+\.\d+\.\d+)', raw))
    return {
        'runtime': 'codex', 'source': lane, 'sessions': used,
        'window': {'first': kst(first), 'last': kst(last)},
        'plugin_versions': ['%s %s ×%d' % (k[0], k[1], n) for k, n in versions.most_common()],
        'time': {'wall_min': round(wall, 1), 'work_min': round(work, 1), 'limit_min': None,
                 'idle_min': round(wall - work, 1)},
        'roles': finish_roles(roles),
        'threads': {k: {'model_min': round(v['model_min'], 1), 'tool_min': round(v['tool_min'], 1)}
                    for k, v in sorted(threads.items())},
        'main_commands': {k: {kk: round(vv, 1) if isinstance(vv, float) else vv for kk, vv in v.items()}
                          for k, v in sorted(cmds.items())},
        'main_calls': dict(calls), 'wait_timeouts': wait_timeouts,
        'markers': dict(markers), 'human': human,
        'spec': spec_sizes(a.repo, since, until, a.build),
    }


# ----------------------------------------------------------------------------------------------- 비교
def core_rows(m):
    t, roles = m['time'], m['roles']
    allr = list(roles.values())
    cmd = m.get('main_commands', {})

    def c(name):
        v = cmd.get(name)
        if not v:
            return '0'
        bg = f" / 백그라운드 {v['bg_n']}회 {v['bg_min']}분" if v.get('bg_n') else ''
        return f"{v['n']}회 {v['min']}분{bg}"
    arch = roles.get('design-architect', {})
    rows = [
        ('벽시계(분)', t['wall_min']),
        ('작업(분) — 에이전트 하나라도 도는 시간', t['work_min']),
        ('사용 한도 대기(분)', t.get('limit_min')),
        ('아무것도 안 돈 시간(분) — 사람·발주자 대기 · compact', t['idle_min']),
        ('모델 시간 합(분) — 전 역할', round(sum(r['model_min'] for r in allr), 1)),
        ('요청 수 합 — 전 역할', sum(r['requests'] for r in allr)),
        ('메인 평균 입력(k)', roles.get('main', {}).get('avg_input_k')),
        ('설계자 평균 입력(k)', arch.get('avg_input_k')),
        ('설계자 재처리 횟수(캐시 만료로 대화 전체 재기록)', arch.get('cold_rewrites')),
        ('compact 합', sum(r['compacts'] for r in allr)),
        ('리뷰 라운드(Phase 1 · 확인 재리뷰)', (m.get('review_rounds') or {}).get('count')),
        ('메인 pre-gate', c('pregate')),
        ('메인 registry_gate', c('registry_gate')),
        ('메인 inputs·render 검사', c('design_evidence')),
        ('메인 W8 대조', c('w8_census')),
        ('메인 시험', c('tests')),
        ('서브가 돌린 게이트(C6 지표)', sum((m.get('sub_gate_runs') or {}).values()) if 'sub_gate_runs' in m else None),
        ('메인이 옮겨 적은 노트(바이트 · C4 지표)', m.get('main_note_bytes')),
        ('wait_agent 시간 초과(폴링 왕복 · K5 지표)', m.get('wait_timeouts')),
        ('발주자 메시지 · 그중 «반송»', f"{m['human']['messages']} · {m['human']['rejections']}"),
    ]
    for k in MARKERS:
        rows.append((f'보고에 나온 {k}', m.get('markers', {}).get(k, 0)))
    s = m.get('spec') or {}
    if 'revisions' in s:
        rows.append(('명세 판 수 · 처음→끝 KB · 최대 KB', f"{s['revisions']} · {s['first_kb']}→{s['last_kb']} · {s['max_kb']}"))
    return rows


def run_compare(a):
    ms = [json.load(open(p, encoding='utf-8')) for p in a.files]
    names = [os.path.basename(p)[:-5] if p.endswith('.json') else os.path.basename(p) for p in a.files]
    tables = [dict(core_rows(m)) for m in ms]
    keys = [k for k, _ in core_rows(ms[0])]
    for t in tables[1:]:
        keys += [k for k in t if k not in keys]
    head = ['지표'] + [f"{n} ({m['runtime']} · {m['window']['first']}~{m['window']['last']})" for n, m in zip(names, ms)]
    if len(ms) > 1:
        head.append('끝 ÷ 첫')
    out = ['## 핵심 지표', '', '| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    for k in keys:
        vals = [t.get(k, '—') for t in tables]
        row = [k] + ['—' if v is None else str(v) for v in vals]
        if len(ms) > 1:
            x, y = vals[0], vals[-1]
            row.append(f'{(y / x - 1) * 100:+.0f}%' if isinstance(x, (int, float)) and isinstance(y, (int, float))
                       and x else '')
        out.append('| ' + ' | '.join(row) + ' |')
    out += ['', '## 역할별', '', '| 레인 | 역할 | 호출 | 요청 | 모델(분) | 도구(분) | 평균 입력(k) | 최대 입력(k) | 재처리 | compact |',
            '|---|---|---|---|---|---|---|---|---|---|']
    for n, m in zip(names, ms):
        for r, v in m['roles'].items():
            out.append(f"| {n} | {r} | {v['agents']} | {v['requests']} | {v['model_min']} | {v['tool_min']} | "
                       f"{v['avg_input_k']} | {v['max_input_k']} | {v['cold_rewrites']} | {v['compacts']} |")
    out += ['', '플러그인 판(기록에서 읽음): ' + ' / '.join(f"{n}: {', '.join(m.get('plugin_versions', [])) or '—'}"
                                                   for n, m in zip(names, ms))]
    text = '\n'.join(out) + '\n'
    if a.md:
        open(a.md, 'w', encoding='utf-8').write(text)
    print(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('claude', 'codex'):
        s = sub.add_parser(name)
        s.add_argument('path')
        s.add_argument('--session', action='append')
        s.add_argument('--since')
        s.add_argument('--until')
        s.add_argument('--repo')
        s.add_argument('--build', help='명세 크기를 잴 빌드 폴더 이름(없으면 창 안 판 수가 가장 많은 것)')
        s.add_argument('--out', required=True)
    c = sub.add_parser('compare')
    c.add_argument('files', nargs='+')
    c.add_argument('--md')
    a = ap.parse_args()
    if a.cmd == 'compare':
        return run_compare(a)
    m = run_claude(a) if a.cmd == 'claude' else run_codex(a)
    json.dump(m, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: m[k] for k in ('window', 'time', 'plugin_versions') if k in m}, ensure_ascii=False))


if __name__ == '__main__':
    main()
