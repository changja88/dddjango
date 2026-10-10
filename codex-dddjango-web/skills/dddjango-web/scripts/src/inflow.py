"""출력 직전 승인 유입 분할: W ∧ F1 ∧ L. 검사·게이트 집합은 건드리지 않는다.

서버 registry_gate의 provenance 차분을 본뜬다. F2는 생략하며 CY·WV·ST12·PU1·PU2는
항상 남긴다. 증명 실패/예외는 blocker 유지, 부모 측정 무효는 해당 병합에서만 불참이다.
TG2·TG3 은 기준점 없이 못 재므로(부모 측정 불가) L 대신 수신 증명으로 가른다 — 작업 트리가 그대로이고
기준 뒤 그 파일을 바꾼 첫 부모 걸음이 전부 승인 병합의 상류판 그대로 수신일 때만(_split 의 receipt).
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Dict, List, Optional, Set, Tuple

from .check_tests import UnsupportedTestFlow, conventional_test_path
from .common import BackstopContext, Finding


@dataclass
class InflowResult:
    remaining: List[Finding]
    notices: List[str] = field(default_factory=list)
    reasons: Dict[int, str] = field(default_factory=dict)
    inflow: List[Tuple[Finding, str]] = field(default_factory=list)
    # 승인 사슬 순서: (M, ^1, ^2, 제목, 역방향 의심 알림)
    merges: List[Tuple[str, str, str, str, List[str]]] = field(default_factory=list)
    # 수신 증명이 선 시험 파일(root 상대) 가운데 미지원 흐름 고지가 있는 것 → 그 파일을 마지막으로 들인 승인 병합
    # (출력이 그 고지를 한 줄로 모으고 병합을 함께 적는다)
    received_tests: Dict[str, str] = field(default_factory=dict)


def _git(root: Path, *args: str) -> bytes:
    proc = subprocess.run(['git', '-C', str(root), *args], capture_output=True,
                          env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
    if proc.returncode:
        raise RuntimeError('git %s 실패 — %s' % (' '.join(args[:2]), proc.stderr.decode('utf-8', 'replace').strip()))
    return proc.stdout


def _key(f: Finding) -> str:
    loc = ('' if f.root_rel else 'web/') + f.path + (':N' if f.line is not None else '')
    return '[%s] %s\n  위반: %s (%s)' % (f.check_id, loc, f.message, f.rule)


def _read_findings(output: str, exitcode: int, target: Path) -> Set[str]:
    """Finding.__str__의 세 줄과 기존 전역 요약을 엄격히 읽는다. 미판독 ≠ 빈 집합."""
    lines = output.splitlines()
    keys: Set[str] = set()
    count = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line or (count == 0 and line.startswith('[info] ')):
            i += 1
            continue
        head = re.fullmatch(r'\[([A-Z]+\d+)\] BLOCKER — (.+)', line)
        if head:
            if (i + 2 >= len(lines) or not re.fullmatch(r'  위반: .+ \(.+\)', lines[i + 1])
                    or not re.fullmatch(r'  교정: .+', lines[i + 2])):
                raise ValueError('부모 출력 판독 불가(Finding)')
            # 경로의 실제 행번호만 정규화한다. 문장 안의 숫자는 그대로다.
            loc = head[2]
            numbered = re.fullmatch(r'(.+):\d+', loc)
            if numbered and (target / numbered[1]).is_file():
                if (target / loc).exists():
                    raise ValueError('부모 출력 경로/행번호 모호')
                loc = numbered[1] + ':N'
            keys.add('[%s] %s\n%s' % (head[1], loc, lines[i + 1]))
            count += 1
            i += 3
            continue
        summary = re.fullmatch(r'\[backstop\] 검사 \d+종\(전역 퇴화\) — blocker (\d+)건', line)
        if (summary and int(summary[1]) == count and not any(lines[i + 1:])
                and exitcode == (2 if count else 0)):
            return keys
        raise ValueError('부모 출력 판독 불가')
    raise ValueError('부모 출력 요약 없음')


def _parse_fail_paths(snapshot: Path) -> Set[str]:
    failed: Set[str] = set()
    for path in sorted(snapshot.rglob('*.py')):
        rel = path.relative_to(snapshot)
        if any(part.startswith('.') for part in rel.parts[:-1]):
            continue
        try:
            ast.parse(path.read_text(encoding='utf-8'))
        except (SyntaxError, UnicodeDecodeError):
            failed.add(rel.as_posix())
    return failed


def _split(ctx: BackstopContext, shown: List[Finding], design_build: Optional[str]) -> InflowResult:
    res = InflowResult(list(shown))
    # 병합 존재 확인 전 조회 실패는 새 출력 없이 2.2.2의 발견을 보존한다.
    try:
        repo = Path(_git(ctx.root, 'rev-parse', '--show-toplevel').decode().strip())
        prefix = ctx.root.relative_to(repo).as_posix()
        prefix = '' if prefix == '.' else prefix + '/'
        merging = subprocess.run(['git', '-C', str(repo), 'rev-parse', '-q', '--verify', 'MERGE_HEAD'],
                                 capture_output=True, env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
        if merging.returncode == 0:
            res.notices.append('[info] 병합 중(MERGE_HEAD) — 승인 유입을 가르지 않는다(병합을 커밋하고 승인 목록에 적은 뒤 다시 돈다)')
            return res
        if merging.returncode != 1:
            raise RuntimeError('MERGE_HEAD 조회 실패')
        base = _git(repo, 'rev-parse', '--verify', (ctx.diff_base or '') + '^{commit}').decode().strip()
        head = _git(repo, 'rev-parse', '--verify', 'HEAD^{commit}').decode().strip()
        if not _git(repo, 'rev-list', '--first-parent', '--min-parents=2', '--max-parents=2',
                    '--max-count=1', '%s..%s' % (base, head)).strip():
            return res
    except (Exception, SystemExit):
        return res

    # 함수 안 import: check_vendor → subst 및 러너의 모듈 적재와 순환하지 않는다.
    from .check_vendor import _find_build
    from .subst import _approved_merges, _chain, _is_ancestor

    chain = _chain(repo, base, head)
    merges = [(sha, parents) for sha, parents in chain if len(parents) == 2]
    if not merges:
        return res  # 무병합 실행: 새 알림·사유 없이 2.2.2와 byte 동일
    if (not _is_ancestor(repo, base, head) or not chain or chain[0][1][:1] != [base]):
        raise ValueError('기준 %s 가 HEAD 첫 부모 사슬 밖' % base[:12])
    folder = _find_build(ctx, design_build)
    approved, notes = _approved_merges(repo, folder, base, chain)
    for sha, _parents in merges:
        if sha not in approved:
            location = str(folder) if folder is not None else '<산출물 폴더>'
            suffix = ' · 산출물 폴더를 찾지 못함: --design-build 로 준다' if folder is None else ''
            res.notices.append('[info] 승인 목록 밖 병합 %s — 이 병합이 들인 지적은 이 레인 몫으로 남는다'
                               '(main 을 받은 병합이면 발주자가 %s/approved-merges.txt 에 «%s [메모]» 한 줄을 적은 뒤 다시 돈다)%s'
                               % (sha[:9], location, sha, suffix))
    if folder is None or not (folder / 'approved-merges.txt').is_file():
        reason = '산출물 폴더 없음' if folder is None else 'approved-merges.txt 없음'
        res.notices.append('[info] 승인 유입 판정 불가 — %s(모든 지적을 이 레인 몫으로 센다)' % reason)
        return res
    active = [(sha, parents) for sha, parents in merges if sha in approved]
    for sha, parents in active:
        subject = _git(repo, 'show', '-s', '--format=%s', sha).decode('utf-8', 'replace').strip()
        warnings = [n for n in notes if n.startswith('승인 병합 ' + sha[:12]) and '기준 이전' not in n]
        res.merges.append((sha, parents[0], parents[1], subject, warnings))

    trees: Dict[str, Dict[str, Tuple[str, str]]] = {}

    def tree(sha: str) -> Dict[str, Tuple[str, str]]:
        if sha not in trees:
            blobs: Dict[str, Tuple[str, str]] = {}
            for entry in _git(repo, 'ls-tree', '-r', '-z', '--full-tree', sha).split(b'\0'):
                if not entry:
                    continue
                meta, path = entry.split(b'\t', 1)
                mode, kind, blob = meta.decode().split()
                if kind == 'blob':
                    blobs[path.decode('utf-8', 'surrogateescape')] = (mode, blob)
            trees[sha] = blobs
        return trees[sha]

    def blob(sha: str, path: str) -> Optional[str]:
        entry = tree(sha).get(path)
        return entry[1] if entry else None

    dirty: Set[str] = set()
    entries = _git(repo, 'status', '--porcelain', '--untracked-files=all', '-z').decode('utf-8', 'surrogateescape').split('\0')
    i = 0
    while i < len(entries) and entries[i]:
        entry = entries[i]
        if len(entry) < 4 or entry[2] != ' ':
            raise ValueError('git status 판독 불가')
        dirty.add(entry[3:])
        if 'R' in entry[:2] or 'C' in entry[:2]:
            i += 1
            if i >= len(entries) or not entries[i]:
                raise ValueError('git status 개명 판독 불가')
            dirty.add(entries[i])
        i += 1

    order = {sha: i for i, (sha, _parents) in enumerate(chain)}

    def step_reason(sha: str, parents: List[str], path: str) -> str:
        if len(parents) >= 2:
            return ('충돌 해소분(M≠M^2) — ' if sha in approved else '미승인 머지 경유 ') + sha[:12]
        delivered = next((m for m, ps in active if order[m] < order[sha]
                          and blob(m, path) != blob(ps[0], path)), None)
        if delivered:
            return '레인 커밋 수정 %s(승인 머지 %s 이후)' % (sha[:12], delivered[:12])
        return '비머지 커밋 경유 ' + sha[:12]

    def retained_reason(path: str) -> str:
        for sha, parents in reversed(chain):
            if blob(sha, path) == (blob(parents[0], path) if parents else None):
                continue
            return step_reason(sha, parents, path)
        return '유입 증명 실패(경로 추적 불능)'

    links: List[bool] = []

    def lane_links() -> bool:
        """저장소 안에 레인이 손댄, root 밖으로 풀리는 심볼릭 링크가 있는가(한 번만 잰다 · 현물을 본다).

        TG2 의 경로 판정은 현물 링크를 풀어 root 밖인지 본다 — 그대로 받은 시험의 발견도 레인이 바꾼 링크 탓일 수
        있어, 그런 링크가 있으면 수신 증명을 하지 않는다. 조사 범위는 root 아래만이 아니라 저장소 전체다 — root 가
        저장소 하위 폴더면 시험이 root 밖(저장소 안)의 링크를 거쳐 읽을 수 있고, 레인이 그 링크를 root 밖으로 돌리면
        판정이 뒤집힌다. 색인(git status)은 assume-unchanged·skip-worktree·무시 규칙에 가려지므로 믿지 않고 추적
        경로의 현물을 lstat 한다. 손댄 링크 =
        ⓐ git status 가 낸 바뀐·미추적 링크
        ⓑ HEAD 가 링크로 아는 경로의 현물이 그 링크가 아닌 것(os.readlink != HEAD blob), 또는 현물은 그대로지만
           기준과 다르고 그 걸음이 전부 «승인 병합의 상류판 그대로 수신» 은 아닌 것
        ⓒ HEAD 가 일반 파일·폴더로 아는 경로(추적 파일과 저장소 안 그 부모 폴더들)가 현물에서는 링크인 것
        가운데 root 밖으로 풀리는 것이다. root 안으로 풀리는 링크는 판정을 밖으로 뒤집지 못해 세지 않는다
        (기준판부터 있던 링크가 현물 그대로면 어디를 가리키든 손댄 것이 아니다).
        대조 실패·판독 불능은 손댄 링크로 센다(증명 실패). 한계: git 이 무시하는 미추적 링크(.venv 류)와 저장소 밖의
        링크는 보지 않는다 · root 밖 자리의 링크는 대개 root 밖으로 풀리므로, root 가 하위 폴더인 저장소에서는 레인이
        그런 링크를 손대기만 해도 수신 증명이 서지 않는다(막는 쪽)."""
        if not links:
            try:
                links.append(touched_link())
            except (Exception, SystemExit):
                links.append(True)
        return links[0]

    def touched_link() -> bool:
        inside = os.path.realpath(ctx.root)

        def leaves(path: str) -> bool:
            return os.path.commonpath([os.path.realpath(repo / path), inside]) != inside

        if any(os.path.islink(repo / p) and leaves(p) for p in dirty):
            return True
        folders: Set[str] = set()
        for path, entry in tree(head).items():
            parent = os.path.dirname(path)
            while parent and parent not in folders:
                folders.add(parent)
                parent = os.path.dirname(parent)
            linked = os.path.islink(repo / path)
            if entry[0] != '120000' or not (
                    linked and os.fsencode(os.readlink(repo / path)) == _git(repo, 'cat-file', 'blob', entry[1])):
                if linked and leaves(path):
                    return True  # HEAD 가 아는 것과 다른 현물 링크
                continue
            if tree(base).get(path) == entry or not leaves(path):
                continue
            for sha, parents in chain:
                current = tree(sha).get(path)
                if current == (tree(parents[0]).get(path) if parents else None):
                    continue
                if not (sha in approved and len(parents) == 2 and current == tree(parents[1]).get(path)):
                    return True
        return any(os.path.islink(repo / folder) and leaves(folder) for folder in folders)

    receipts: Dict[str, Tuple[Optional[str], str]] = {}

    def receipt(path: str) -> Tuple[Optional[str], str]:
        """TG 수신 증명 — (그 경로를 마지막으로 들인 승인 병합 | None, 남긴 사유).

        ① 경로가 HEAD tree 의 blob 이고 작업 트리 현물이 그대로다 — git status 에 없고, 현물 바이트를 필터 없이
           다시 해시한 blob 이 HEAD 와 같다(색인 플래그·clean 필터가 가린 수정을 막는다 · TG 분석이 읽는 것이 그
           현물이다 · 심볼릭 링크인 시험은 가리키는 파일의 내용이 해시돼 서지 않는다). 줄 끝 변환·필터 때문에 현물
           바이트가 blob 과 다른 파일은 같음을 증명하지 못해 서지 않는다(보수 쪽 한계).
        ② 기준..HEAD 첫 부모 사슬에서 그 blob 을 바꾼 걸음이 하나 이상이고, 전부 승인 병합이며 각각
           blob(M) == blob(M^2)(상류판 그대로 수신)다.
        ③ 경로가 관례 시험 자리다(conventional_test_path) — 수집 설정·G0 명시 경로에 기대 시험이 된 파일은
           레인의 설정 변경 탓일 수 있어 서지 않는다.
        ④ 저장소 안 어디에도 레인이 손댄, root 밖으로 풀리는 현물 심볼릭 링크가 없다(lane_links).
        하나라도 어긋나면 이 레인 몫이다 — 사유는 증명을 깬 가장 늦은 걸음의 기존 문구. 부모 측정·스냅숏은 없다
        (TG2·TG3 은 기준점 없이 못 잰다). git 조회·판독 실패는 그 경로의 면제 증명 실패다(다른 발견으로 번지지 않는다).
        """
        if path not in receipts:
            receipts[path] = (None, '유입 증명 실패(경로 추적 불능)')
            try:
                entry = tree(head).get(path)
                if entry is None:
                    receipts[path] = (None, '비-blob 경로')
                elif (path in dirty
                      or _git(repo, 'hash-object', '--no-filters', '--', path).decode().strip() != entry[1]):
                    receipts[path] = (None, '작업 트리 수정 중')
                else:
                    last: Optional[str] = None
                    broken: Optional[Tuple[str, List[str]]] = None
                    for sha, parents in chain:
                        if blob(sha, path) == (blob(parents[0], path) if parents else None):
                            continue
                        if sha in approved and len(parents) == 2 and blob(sha, path) == blob(parents[1], path):
                            last = sha
                        else:
                            broken = (sha, parents)
                    if broken is not None:
                        receipts[path] = (None, step_reason(broken[0], broken[1], path))
                    elif last is None:
                        pass  # 기준 뒤 이 경로를 바꾼 걸음이 없다 — 기본 사유
                    elif not conventional_test_path(path[len(prefix):]):
                        receipts[path] = (None, '유입 증명 실패(관례 시험 자리 밖)')
                    elif lane_links():
                        receipts[path] = (None, '유입 증명 실패(레인이 손댄 심볼릭 링크)')
                    else:
                        receipts[path] = (last, '')
            except (Exception, SystemExit):
                pass
        return receipts[path]

    # 미지원 흐름 고지도 같은 술어로 가른다(그 파일에 TG 발견이 없어도). 승인 병합이 없으면 설 증명이 없다.
    for notice in (ctx.notices if active else []):
        deliver = receipt(prefix + notice.path)[0] if isinstance(notice, UnsupportedTestFlow) else None
        if deliver:
            res.received_tests[notice.path] = deliver

    candidates: List[Tuple[Finding, str]] = []
    for f in shown:
        path = prefix + ('' if f.root_rel else 'web/') + f.path
        if f.check_id.startswith(('CY', 'WV')) or f.check_id in ('ST12', 'PU1', 'PU2'):
            res.reasons[id(f)] = '가름 제외 검사'
        elif path not in tree(head):
            res.reasons[id(f)] = '비-blob 경로'
        elif path in dirty:
            res.reasons[id(f)] = '작업 트리 수정 중'
        elif f.check_id in ('TG2', 'TG3'):
            deliver, reason = receipt(path)
            if deliver:
                res.inflow.append((f, deliver))
            else:
                res.reasons[id(f)] = reason
        else:
            deliver = next((sha for sha, ps in active
                            if blob(ps[0], path) != blob(sha, path)
                            and blob(sha, path) == blob(ps[1], path) == blob(head, path)), None)
            if deliver:
                candidates.append((f, deliver))
            else:
                res.reasons[id(f)] = retained_reason(path)

    def settle() -> InflowResult:
        # 승인 유입 절의 차례는 발견 정렬 그대로다(수신 증명·L 증명이 섞여도).
        position = {id(f): i for i, f in enumerate(shown)}
        res.inflow.sort(key=lambda item: position[id(item[0])])
        moved = {id(f) for f, _sha in res.inflow}
        res.remaining = [f for f in shown if id(f) not in moved]
        return res

    if not candidates:
        return settle()

    # SHA별 측정 캐시: 실패도 저장한다. 스냅숏은 후보가 있을 때만 만든다.
    td = Path(tempfile.mkdtemp(prefix='dddjango-web-inflow-'))
    measurements: Dict[str, Tuple[Set[str], Set[str], Optional[str]]] = {}
    script = Path(__file__).resolve().parents[1] / 'backstop.py'

    def measure(sha: str) -> Tuple[Set[str], Set[str], Optional[str]]:
        if sha not in measurements:
            try:
                if any(mode == '120000' for mode, _blob in tree(sha).values()):
                    raise ValueError('부모 트리 심볼릭 링크')
                dest = td / sha
                dest.mkdir()
                tops = [p.decode('utf-8', 'surrogateescape') for p in
                        _git(repo, 'ls-tree', '-z', '--name-only', sha).split(b'\0')
                        if p and p not in (b'.dddjango-web', b'.dddjango')]
                if tops:
                    with subprocess.Popen(['git', '-C', str(repo), 'archive', sha, '--', *tops],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          env=dict(os.environ, GIT_OPTIONAL_LOCKS='0')) as archive:
                        try:
                            untar = subprocess.run(['tar', '-x', '-C', str(dest)], stdin=archive.stdout, capture_output=True)
                        finally:
                            if archive.stdout is not None:
                                archive.stdout.close()
                        _, error = archive.communicate()
                        if archive.returncode or untar.returncode:
                            raise ValueError('스냅숏 실패 — ' + error.decode('utf-8', 'replace').strip())
                failed = _parse_fail_paths(dest)
                proc = subprocess.run([sys.executable, '-B', str(script), str(dest / prefix), '--only', 'st,md,im,nm,tg,pj,pu'],
                                      capture_output=True, env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
                if proc.returncode not in (0, 2) or proc.stderr:
                    raise ValueError('부모 실행 실패')
                measurements[sha] = (_read_findings(proc.stdout.decode('utf-8'), proc.returncode, dest / prefix), failed, None)
            except (Exception, SystemExit) as error:
                measurements[sha] = (set(), set(), str(error))
        return measurements[sha]

    try:
        for f, deliver in candidates:
            invalid: List[str] = []
            parents = dict(active)
            for sha in [deliver] + [m for m, _ps in active if m != deliver]:
                r1, fail1, error1 = measure(parents[sha][0])
                r2, fail2, error2 = measure(parents[sha][1])
                if error1 or error2 or fail1 != fail2:
                    why = error1 or error2 or '부모 Python 파싱 실패 비대칭'
                    invalid.append('측정 무효(%s) — %s' % (why, sha[:12]))
                    continue
                if _key(f) in r2 - r1:
                    res.inflow.append((f, sha))
                    break
            else:
                res.reasons[id(f)] = invalid[0] if invalid else '유입 증명 실패(이중 원인)'
        return settle()
    finally:
        shutil.rmtree(td)


def split_inflow(ctx: BackstopContext, shown: List[Finding], design_build: Optional[str]) -> InflowResult:
    if not ctx.gated:
        return InflowResult(list(shown))
    # 기존 읽기 도우미에는 env 인자가 없다. 그 호출까지 잠금 없는 Git 환경을 씌우고 복원한다.
    previous = os.environ.get('GIT_OPTIONAL_LOCKS')
    os.environ['GIT_OPTIONAL_LOCKS'] = '0'
    try:
        return _split(ctx, shown, design_build)
    except (Exception, SystemExit) as error:
        return InflowResult(list(shown), ['[info] 승인 유입 판정 불가 — %s(모든 지적을 이 레인 몫으로 센다)' % error])
    finally:
        if previous is None:
            os.environ.pop('GIT_OPTIONAL_LOCKS', None)
        else:
            os.environ['GIT_OPTIONAL_LOCKS'] = previous
