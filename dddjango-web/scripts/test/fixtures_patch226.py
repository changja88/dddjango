"""기록 사본·TG 수신 증명 회귀 픽스처. 실제 임시 git 저장소만 변경한다.

A = 기록 폴더(.dddjango-web/ · .dddjango/)는 시험 자리가 아니다 · B = TG2·TG3 승인 유입의 수신 증명.
«숨김 0» 묶음은 이 레인이 손댄 시험의 발견이 승인 유입으로 빠지지 않음을 본다(하나라도 빠지면 FAIL).
HEAD 러너(고치기 전)는 별도 임시 사본으로 꺼내 출력 byte 를 대조한다.
"""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from src.common import BackstopContext
from src.check_tests import run_tests

PASS = FAIL = 0
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
TEST = 'web_test/test_x.py'
BAD = 'from pathlib import Path\ndef test_x():\n    open("/private/tmp/x").read()\n    Path(dynamic()).read_text()\n'
LANE_LINE = '    open("/private/tmp/lane").read()\n'
IMAGE = 'def test_x():\n    expect(page).to_have_screenshot("x.png")\n'
SAFE = 'def test_x():\n    pass\n'
LINKED = 'from pathlib import Path\ndef test_x():\n    (Path(__file__).parent / "data" / "x.json").read_text()\n'
PROOF = '(수신 증명 — 기준 뒤 이 파일을 바꾼 걸음 = 승인 병합의 상류판 그대로뿐) · 파일 그대로'
GATHERED = '[info] TG2 일부 흐름 자동 판정 밖 — 승인 병합이 그대로 들인 시험 %d 파일은 이 레인 감수 대상이 아니다(승인 유입)'
FLOW = '[info] TG2 일부 흐름 자동 판정 밖 — %s:%s 동적/미지원 입력은 무관함의 증명이 아니며 discipline 감수 대상'
KEPT = '  ↳ 이 레인 몫으로 남김: '
WIDE = 'st,md,im,nm,tg,pj,pu,wv'  # 순환(CY)은 기준선 파일을 쓰므로 두 러너 대조에서 뺀다


def git(root, *args, check=True):
    p = subprocess.run(['git', '-C', str(root), '-c', 'user.name=t', '-c', 'user.email=t@t', *args],
                       capture_output=True, text=True, env=ENV)
    if check and p.returncode:
        raise RuntimeError(p.stderr)
    return p.stdout.strip()


def write(root, rel, source):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding='utf-8')


def commit(root, title):
    git(root, 'add', '-A')
    git(root, 'commit', '-qm', title)
    return git(root, 'rev-parse', 'HEAD')


def check(name, ok, detail=''):
    global PASS, FAIL
    PASS += bool(ok)
    FAIL += not ok
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok:
        print('    ' + str(detail).replace('\n', '\n    ')[:2200])


def project(temp, name, initial=None, nested=False):
    repo = temp / name
    root = repo / 'host' if nested else repo
    write(root, 'web/__init__.py', '')
    write(root, 'requirements.txt', 'pytest==8.3.3\npytest-django==4.9.0\n')
    write(root, 'web/static/htmx/htmx.min.js', 'var htmx={version:"2.0.10"};\n')
    for rel, source in (initial or {}).items():
        write(root, rel, source)
    git(repo, 'init', '-q', '-b', 'main')
    base = commit(repo, 'base')
    git(repo, 'checkout', '-qb', 'lane')
    write(root, 'lane.txt', 'lane\n')
    commit(repo, 'lane')
    folder = root / '.dddjango-web/run'
    write(root, '.dddjango-web/run/build-state.json', json.dumps({'git_snapshot': base}))
    return repo, root, base, folder


def incoming(repo, root, changes, folder, approve=True, resolve=None, prepare=None):
    """main 에 상류 커밋을 만들고 lane 이 받는다(--no-ff). resolve = 병합 커밋 전에 작업 트리를 고친다."""
    git(repo, 'checkout', '-q', 'main')
    for rel, source in changes.items():
        write(root, rel, source)
    if prepare:
        prepare()
    git(repo, 'add', '-A', '--', ':!.dddjango-web', ':!host/.dddjango-web')
    git(repo, 'commit', '-qm', 'upstream')
    git(repo, 'checkout', '-q', 'lane')
    git(repo, 'merge', '--no-ff', '--no-commit', 'main', check=False)
    if resolve:
        resolve()
    # 기록은 커밋하지 않는다.
    git(repo, 'add', '-A', '--', ':!.dddjango-web', ':!host/.dddjango-web')
    git(repo, 'commit', '-qm', 'receive')
    sha = git(repo, 'rev-parse', 'HEAD')
    if approve:
        with (folder / 'approved-merges.txt').open('a', encoding='utf-8') as f:
            f.write(sha + ' upstream\n')
    return sha


def lane_commit(repo, title, *paths):
    git(repo, 'add', '--', *paths)
    git(repo, 'commit', '-qm', title)
    return git(repo, 'rev-parse', 'HEAD')


def run(root, base, extra=(), only='tg2,tg3', runner=None, fault=None):
    """fault = (git 하위 명령, 마지막 인자) — inflow 의 그 git 조회 하나만 실패시킨다."""
    script = runner or SCRIPTS / 'backstop.py'
    args = [str(root), '--diff-base', base]
    if only:
        args += ['--only', only]
    args += list(extra)
    if fault:
        code = ('import sys,runpy; sys.path.insert(0,sys.argv[1]); import src.inflow as i; '
                'original=i._git; sub,last=sys.argv[2],sys.argv[3]; '
                'i._git=lambda r,*a: (_ for _ in ()).throw(RuntimeError("fixture receipt query")) '
                'if a[0]==sub and a[-1]==last else original(r,*a); '
                'sys.argv=sys.argv[4:]; runpy.run_path(sys.argv[0],run_name="__main__")')
        cmd = [sys.executable, '-B', '-c', code, str(SCRIPTS), fault[0], fault[1], str(script), *args]
    else:
        cmd = [sys.executable, '-B', str(script), *args]
    p = subprocess.run(cmd, capture_output=True, text=True, env=ENV)
    return p.returncode, p.stdout + p.stderr


def tg(root, base):
    ctx = BackstopContext.build(root, base, False)
    return [f for f in run_tests(ctx) if f.check_id in ('TG2', 'TG3')], ctx.notices


def sections(output):
    parts = output.split('== 승인 유입(', 1)
    return parts[0], parts[1] if len(parts) == 2 else ''


def heads(text, cid):
    """그 절의 발견 머리 — `<경로>:<행>` 목록."""
    return re.findall(r'^\[%s\] BLOCKER — (\S+)$' % cid, text, flags=re.M)


def received(name, got, merge, cid='TG2', info=False, count=1):
    code, out = got
    lane, upstream = sections(out)
    ok = code == 0 and not heads(lane, cid) and len(heads(upstream, cid)) == count
    ok &= upstream.count('    ↳ 유입: ' + merge[:12] + PROOF) == count
    ok &= ' · ^1 ' in upstream and ' · ^2 ' in upstream and '승인 유입 %d건(종료 코드 제외)' % count in out
    ok &= KEPT not in out
    if info:
        notice = GATHERED % count
        ok &= out.count(notice) == 1 and 'discipline 감수 대상' not in out
        ok &= notice in out and out.index(notice) < out.index('[' + cid + '] BLOCKER')
    else:
        ok &= '이 레인 감수 대상이 아니다' not in out
    check(name, ok, got)


def retained(name, got, cid='TG2', reason=None, notice=None, flow=None, same=None):
    """이 레인 몫 유지 — exit 2 · 발견은 전부 승인 유입 절 밖 · 수신 증명 표지와 고지 모음이 없다."""
    code, out = got
    lane, upstream = sections(out)
    ok = code == 2 and bool(heads(lane, cid)) and not heads(upstream, 'TG2') and not heads(upstream, 'TG3')
    ok &= '수신 증명' not in out and '이 레인 감수 대상이 아니다' not in out
    if reason is not None:
        ok &= lane.count(KEPT + reason) == len(heads(lane, cid))
    if notice is not None:
        ok &= notice in out
    if flow is not None:
        ok &= out.count(FLOW % flow) == 1
    if same is not None:
        # 고치기 전에도 같은 글자로 막던 꼴 — 출력 전체가 그대로다.
        ok &= got == same
    check('숨김 0 ' + name, ok, (got, same))


def shape(name, ok, detail=''):
    """픽스처가 뜻한 git 꼴을 실제로 만들었는가(헛통과 방지)."""
    if not ok:
        check('꼴 불성립 — ' + name, False, detail)


with tempfile.TemporaryDirectory(prefix='web226-') as tmp:
    temp = Path(tmp).resolve()
    previous = temp / 'previous'
    previous.mkdir()
    archive = subprocess.run(['git', '-C', str(SCRIPTS.parents[1]), 'archive', 'HEAD', 'dddjango-web/scripts'],
                             capture_output=True, check=True, env=ENV)
    subprocess.run(['tar', '-x', '-C', str(previous)], input=archive.stdout, check=True)
    old_runner = previous / 'dddjango-web/scripts/backstop.py'
    outside = temp / 'outside-data'
    outside.mkdir()

    def before(root, base, extra=(), only='tg2,tg3'):
        return run(root, base, extra, only, runner=old_runner)

    # ================= A. 기록 폴더는 시험 자리가 아니다
    for folder_name in ('.dddjango-web/run/captures/g2-return', '.dddjango/run'):
        top = folder_name.split('/')[0]
        for tracked in (False, True):
            for cid, source in (('TG2', BAD), ('TG3', IMAGE)):
                repo, root, base, folder = project(temp, 'record-%s-%s-%s' % (top, tracked, cid))
                write(root, folder_name + '/test_x.py', source)
                if tracked:
                    commit(repo, 'record')
                fs, notices = tg(root, base)
                check('A %s %s %s 불발화' % (folder_name, '추적' if tracked else '미추적', cid),
                      not fs and not any(top + '/' in n for n in notices), (fs, notices))
                if tracked and cid == 'TG2':
                    for extra, only in (([], 'tg2,tg3'), (['--slice-end'], None), (['--design-build', str(folder)], 'tg2,tg3')):
                        got = run(root, base, extra, only)
                        check('A %s 러너 %s' % (folder_name, ' '.join(extra[:1]) or '기본'),
                              got[0] == 0 and '[TG' not in got[1] and top + '/' not in got[1], got)
    for folder_name in ('.dddjango-web/run/captures', '.dddjango/run'):
        top = folder_name.split('/')[0]
        for name in ('conftest.py', '_support.py', 'arbitrary.py'):
            repo, root, base, folder = project(temp, 'support-' + top + name)
            rel = folder_name + '/' + name
            write(root, rel, BAD + IMAGE)
            write(root, 'pytest.ini', '[pytest]\ntestpaths = ' + folder_name + '\n')
            write(root, '.dddjango-web/run/build-state.json', json.dumps({'git_snapshot': base, 'test_command': 'pytest ' + rel}))
            fs, notices = tg(root, base)
            check('A 지원·설정 뿌리·명시 경로 ' + rel, not fs and not any(top + '/' in n for n in notices), (fs, notices))
    for mode in ('copy', 'rename', 'git-mv', 'rename-사본-둘'):
        for cid, source in (('TG2', BAD), ('TG3', IMAGE)):
            initial = {'.dddjango-web/old/test_x.py': source}
            if mode == 'rename-사본-둘':
                initial['.dddjango/old/test_x.py'] = source
            repo, root, base, folder = project(temp, mode + cid, initial)
            if mode == 'git-mv':
                (root / 'web_test').mkdir()
                git(repo, 'mv', '.dddjango-web/old/test_x.py', TEST)
                git(repo, 'commit', '-qm', 'adopt')
            else:
                write(root, TEST, source)
                if mode != 'copy':
                    for rel in initial:
                        (root / rel).unlink()
            fs, notices = tg(root, base)
            check('A 기록→영구 %s %s 전 줄 새 줄' % (mode, cid),
                  [(f.check_id, f.path) for f in fs] == [(cid, TEST)] and not any('모호' in n for n in notices), (fs, notices))
    repo, root, base, folder = project(temp, 'real')
    write(root, TEST, BAD + IMAGE)
    check('A 진짜 시험 TG2·TG3', {f.check_id for f in tg(root, base)[0]} == {'TG2', 'TG3'})
    write(root, '.custom/test_x.py', BAD)
    check('A 다른 점 폴더 보존', any(f.path == '.custom/test_x.py' for f in tg(root, base)[0]))

    # ================= B. 수신 증명 성립 — 승인 유입 절 · exit 0 · 표지 · 고지 모음
    for name, initial, source in [('신규', {}, BAD), ('기존', {TEST: SAFE}, BAD), ('TG3', {}, IMAGE)]:
        repo, root, base, folder = project(temp, 'good-' + name, initial)
        m = incoming(repo, root, {TEST: source}, folder)
        cid = 'TG3' if name == 'TG3' else 'TG2'
        received('B ' + name + '(자동 탐색)', run(root, base), m, cid, name != 'TG3')
        if name == '신규':
            received('B design-build 명시', run(root, base, ['--design-build', str(folder)]), m, info=True)
            received('B slice-end', run(root, base, ['--slice-end'], only=None), m, info=True)
            git(repo, 'branch', '-D', 'main')
            got = run(root, base)
            received('B TG만 역방향 의심', got, m, info=True)
            check('B TG만 의심 알림 출력', '    ↳ 승인 병합 ' + m[:12] in got[1] and '역방향/합성 병합 의심' in got[1], got)
    repo, root, base, folder = project(temp, 'twice')
    first = incoming(repo, root, {TEST: BAD}, folder)
    m = incoming(repo, root, {TEST: BAD + '# upstream two\n'}, folder)
    got = run(root, base)
    received('B 승인 둘·마지막 귀속', got, m, info=True)
    check('B 승인 둘·앞 병합에는 0건', '[M %s] receive' % first[:12] in got[1] and '유입: ' + first[:12] not in got[1], got)
    repo, root, base, folder = project(temp, 'prefix', nested=True)
    m = incoming(repo, root, {TEST: BAD}, folder)
    received('B root 하위 폴더 prefix', run(root, base), m, info=True)
    repo, root, base, folder = project(temp, 'two-files')
    m = incoming(repo, root, {TEST: BAD, 'web_test/test_y.py': BAD}, folder)
    received('B 수신 파일 둘 — 고지 한 줄', run(root, base), m, info=True, count=2)
    repo, root, base, folder = project(temp, 'notice-only')
    incoming(repo, root, {TEST: 'from pathlib import Path\nPath(dynamic()).read_text()\n'}, folder)
    got = run(root, base)
    check('B 발견 없는 수신 파일 고지 모음', got[0] == 0 and got[1].count(GATHERED % 1) == 1
          and 'discipline 감수 대상' not in got[1] and '승인 유입(' not in got[1], got)
    repo, root, base, folder = project(temp, 'with-lane-test')
    m = incoming(repo, root, {TEST: BAD}, folder)
    write(root, 'web_test/test_lane.py', BAD)
    lane = lane_commit(repo, 'lane-test', 'web_test/test_lane.py')
    code, out = got = run(root, base)
    lane_part, upstream = sections(out)
    check('B 수신 + 레인 시험 혼재 — 레인 몫은 그대로',
          code == 2 and heads(lane_part, 'TG2') == ['web_test/test_lane.py:3'] and heads(upstream, 'TG2') == [TEST + ':3']
          and KEPT + '비머지 커밋 경유 ' + lane[:12] in lane_part and '유입: ' + m[:12] + PROOF in upstream
          and out.count(FLOW % ('web_test/test_lane.py', '4')) == 1 and out.count(GATHERED % 1) == 1
          and FLOW % (TEST, '4') not in out and out.index(GATHERED % 1) < out.index('[TG2] BLOCKER')
          and 'blocker 1건 · 승인 유입 1건(종료 코드 제외)' in out, got)
    repo, root, base, folder = project(temp, 'upstream-link')
    m = incoming(repo, root, {TEST: LINKED}, folder, prepare=lambda: os.symlink(str(outside), root / 'web_test/data'))
    received('B 상류가 함께 들인 심볼릭 링크', run(root, base), m)
    for rel in ('application/order/test/order_flow.py', 'tests/_support.py', 'quality/conftest.py'):
        repo, root, base, folder = project(temp, 'place-' + rel.replace('/', '-'))
        m = incoming(repo, root, {rel: BAD}, folder)
        received('B 관례 시험 자리 ' + rel, run(root, base), m, info=True)
    repo, root, base, folder = project(temp, 'inside-link')
    m = incoming(repo, root, {TEST: BAD}, folder)
    write(root, 'web_test/fixtures/a.json', '{}\n')
    os.symlink('fixtures', root / 'web_test/data')
    lane_commit(repo, 'lane-inside-link', 'web_test/fixtures', 'web_test/data')
    received('B 레인이 더한 root 안 심볼릭 링크는 막지 않는다', run(root, base), m, info=True)

    # ================= B. 숨김 0 — 전부 이 레인 몫(blocker)으로 남는다
    for mode in ('commit', 'commit-slice-end', 'staged', 'unstaged', 'untracked', 'skip-worktree', 'assume-unchanged',
                 'rename', 'rename-pure', 'recreate-commit', 'missing-folder', 'ambiguous', 'missing-list',
                 'invalid-list', 'merge-head', 'shallow', 'query-failure'):
        repo, root, base, folder = project(temp, 'hidden-' + mode)
        m = incoming(repo, root, {TEST: BAD}, folder)
        extra, only, fault, reason, notice, flow, compare = [], 'tg2,tg3', None, None, None, (TEST, '4'), True
        if mode in ('commit', 'commit-slice-end', 'staged', 'unstaged'):
            write(root, TEST, BAD + '# lane change\n')
            reason = '작업 트리 수정 중'
            if mode.startswith('commit'):
                reason = '레인 커밋 수정 %s(승인 머지 %s 이후)' % (lane_commit(repo, 'lane-change', TEST)[:12], m[:12])
                if mode == 'commit-slice-end':
                    extra, only = ['--slice-end'], None
            elif mode == 'staged':
                git(repo, 'add', TEST)
        elif mode == 'untracked':
            git(repo, 'rm', '--cached', '-q', TEST)
            (root / TEST).unlink()
            write(root, TEST, BAD)
            reason = '작업 트리 수정 중'
            shape(mode, git(repo, 'show', 'HEAD:' + TEST) + '\n' == BAD
                  and '?? ' + TEST in git(repo, 'status', '--porcelain', '--untracked-files=all'))
        elif mode in ('skip-worktree', 'assume-unchanged'):
            # git status 가 못 보는 수정 — 현물 blob 대조가 막는다(고치기 전에는 «이중 원인» 꼬리표였다).
            git(repo, 'update-index', '--' + mode, TEST)
            write(root, TEST, BAD + LANE_LINE)
            reason, compare = '작업 트리 수정 중', False
            shape(mode, TEST not in git(repo, 'status', '--porcelain', '--untracked-files=all'))
        elif mode in ('rename', 'rename-pure'):
            git(repo, 'mv', TEST, 'web_test/test_renamed.py')
            if mode == 'rename':
                write(root, 'web_test/test_renamed.py', BAD + LANE_LINE)
            reason = '비머지 커밋 경유 ' + lane_commit(repo, 'rename', 'web_test')[:12]
            flow = ('web_test/test_renamed.py', '4')
            shape(mode, mode == 'rename' or git(repo, 'rev-parse', 'HEAD:web_test/test_renamed.py') == git(repo, 'rev-parse', m + '^2:' + TEST))
        elif mode == 'recreate-commit':
            git(repo, 'rm', '-q', TEST)
            git(repo, 'commit', '-qm', 'drop')
            write(root, TEST, BAD)
            # 지웠다 같은 내용으로 다시 넣었다 — 현재판은 상류판과 같지만 레인 걸음이 끼어 있다.
            reason, compare = '레인 커밋 수정 %s(승인 머지 %s 이후)' % (lane_commit(repo, 'recreate', TEST)[:12], m[:12]), False
            shape(mode, git(repo, 'rev-parse', 'HEAD:' + TEST) == git(repo, 'rev-parse', m + '^2:' + TEST))
        elif mode == 'missing-folder':
            shutil.rmtree(folder)
            notice = '[info] 승인 유입 판정 불가 — 산출물 폴더 없음'
        elif mode == 'ambiguous':
            write(root, '.dddjango-web/other/build-state.json', json.dumps({'git_snapshot': base}))
            notice = '[info] 승인 유입 판정 불가 — 산출물 폴더 없음'
        elif mode == 'missing-list':
            (folder / 'approved-merges.txt').unlink()
            notice = '[info] 승인 유입 판정 불가 — approved-merges.txt 없음'
        elif mode == 'invalid-list':
            (folder / 'approved-merges.txt').write_text('invalid\n')
            notice = '[info] 승인 유입 판정 불가 — approved-merges.txt 줄 형식 오류'
        elif mode == 'merge-head':
            (repo / '.git/MERGE_HEAD').write_text(git(repo, 'rev-parse', m + '^2') + '\n')
            notice = '[info] 병합 중(MERGE_HEAD)'
        elif mode == 'shallow':
            (repo / '.git/shallow').write_text(base + '\n')
            notice = '[info] 승인 유입 판정 불가 — 얕은 이력'
        elif mode == 'query-failure':
            fault, reason, compare = ('ls-tree', git(repo, 'rev-parse', m + '^2')), '유입 증명 실패(경로 추적 불능)', False
        retained(mode, run(root, base, extra, only, fault=fault), reason=reason, notice=notice, flow=flow,
                 same=before(root, base, extra, only) if compare else None)

    for mode in ('unapproved', 'unapproved-first', 'conflict', 'reject-commit', 'reject-merge', 'reject-clean-commit',
                 'overwrite-after-lane-edit', 'before-base', 'before-base-later-merge', 'outside-chain'):
        conflicting = mode in ('conflict', 'reject-commit', 'reject-merge')
        repo, root, base, folder = project(temp, 'hidden-' + mode, {TEST: SAFE} if conflicting or mode == 'reject-clean-commit' else {})
        if conflicting:
            write(root, TEST, 'def test_x():\n    lane()\n')
            lane_commit(repo, 'lane-before', TEST)
        resolve = None
        if mode == 'conflict':
            resolve = lambda: write(root, TEST, BAD + '# conflict resolution\n')
        elif mode.startswith('reject-'):
            resolve = lambda: write(root, TEST, SAFE)  # 승인 병합이 상류 금지 줄을 받지 않았다
        m = incoming(repo, root, {TEST: BAD}, folder, approve=not mode.startswith('unapproved'), resolve=resolve)
        reason, notice, flow, compare = None, None, (TEST, '4'), True
        if mode == 'unapproved':
            (folder / 'approved-merges.txt').write_text('// 승인한 병합 없음\n')
            reason = '미승인 머지 경유 ' + m[:12]
        elif mode == 'unapproved-first':
            # 뒤 승인 병합은 같은 파일의 다른 줄만 바꿨고 상류판 그대로다 — 앞 미승인 병합 몫을 면제하지 않는다.
            second = incoming(repo, root, {TEST: BAD + '# next upstream\n'}, folder)
            reason, compare = '미승인 머지 경유 ' + m[:12], False
            shape(mode, git(repo, 'rev-parse', 'HEAD:' + TEST) == git(repo, 'rev-parse', second + '^2:' + TEST)
                  and second in (folder / 'approved-merges.txt').read_text() and m not in (folder / 'approved-merges.txt').read_text())
        elif mode == 'conflict':
            reason = '충돌 해소분(M≠M^2) — ' + m[:12]
        elif mode in ('reject-commit', 'reject-clean-commit'):
            write(root, TEST, BAD)
            again = lane_commit(repo, 'reintroduce', TEST)
            reason = ('레인 커밋 수정 %s(승인 머지 %s 이후)' % (again[:12], m[:12]) if mode == 'reject-commit'
                      else '비머지 커밋 경유 ' + again[:12])
            shape(mode, git(repo, 'rev-parse', 'HEAD:' + TEST) == git(repo, 'rev-parse', m + '^2:' + TEST)
                  and git(repo, 'show', m + ':' + TEST) + '\n' == SAFE)
        elif mode == 'reject-merge':
            git(repo, 'checkout', '-qb', 'other')
            write(root, TEST, BAD)
            lane_commit(repo, 'reintroduce', TEST)
            git(repo, 'checkout', '-q', 'lane')
            git(repo, 'merge', '--no-ff', '-qm', 'unapproved', 'other')
            reason = '미승인 머지 경유 ' + git(repo, 'rev-parse', 'HEAD')[:12]
            shape(mode, git(repo, 'rev-parse', 'HEAD:' + TEST) == git(repo, 'rev-parse', m + '^2:' + TEST))
        elif mode == 'overwrite-after-lane-edit':
            # 레인이 고친 뒤 승인 병합이 상류판으로 덮었다 — 현재판은 상류판과 같지만 레인 걸음이 끼어 있다.
            write(root, TEST, BAD + LANE_LINE)
            edit = lane_commit(repo, 'lane-edit', TEST)
            upstream_two = BAD + '# upstream two\n'
            second = incoming(repo, root, {TEST: upstream_two}, folder, resolve=lambda: write(root, TEST, upstream_two))
            reason, compare = '레인 커밋 수정 %s(승인 머지 %s 이후)' % (edit[:12], m[:12]), False
            shape(mode, git(repo, 'rev-parse', 'HEAD:' + TEST) == git(repo, 'rev-parse', second + '^2:' + TEST))
        elif mode == 'before-base':
            base = m
            git(repo, 'mv', TEST, 'web_test/test_renamed.py')
            write(root, 'web_test/test_renamed.py', BAD + LANE_LINE)
            lane_commit(repo, 'after-base', 'web_test')
            flow = ('web_test/test_renamed.py', '4')
        elif mode == 'before-base-later-merge':
            # 기준 이전 병합이 들인 파일을 레인이 고쳤고, 기준 뒤 승인 병합은 다른 파일만 들였다.
            base = m
            folder = root / '.dddjango-web/later'
            write(root, '.dddjango-web/later/build-state.json', json.dumps({'git_snapshot': base}))
            write(root, TEST, BAD + LANE_LINE)
            edit = lane_commit(repo, 'lane-edit', TEST)
            incoming(repo, root, {'web_test/test_other.py': SAFE}, folder)
            reason = '비머지 커밋 경유 ' + edit[:12]
        elif mode == 'outside-chain':
            base = git(repo, 'rev-parse', m + '^2')
            write(root, TEST, BAD + LANE_LINE)
            lane_commit(repo, 'lane-after', TEST)
            notice = '[info] 승인 유입 판정 불가 — 기준 %s 가 HEAD 첫 부모 사슬 밖' % base[:12]
        retained(mode, run(root, base), reason=reason, notice=notice, flow=flow, same=before(root, base) if compare else None)

    repo, root, base, folder = project(temp, 'hidden-tg3')
    m = incoming(repo, root, {TEST: IMAGE}, folder)
    write(root, TEST, IMAGE + '    expect(page).to_have_screenshot("y.png")\n')
    edit = lane_commit(repo, 'lane-change', TEST)
    retained('TG3 commit', run(root, base), 'TG3', '레인 커밋 수정 %s(승인 머지 %s 이후)' % (edit[:12], m[:12]), same=before(root, base))
    repo, root, base, folder = project(temp, 'hidden-prefix', nested=True)
    m = incoming(repo, root, {TEST: BAD}, folder)
    write(root, TEST, BAD + LANE_LINE)
    edit = lane_commit(repo, 'lane-change', 'host/' + TEST)
    retained('root 하위 폴더 commit', run(root, base), reason='레인 커밋 수정 %s(승인 머지 %s 이후)' % (edit[:12], m[:12]),
             flow=(TEST, '4'), same=before(root, base))
    # 수집 설정·G0 명시 경로에 기대 시험이 된 상류 파일 — 레인의 설정 변경 탓일 수 있어 수신 증명이 서지 않는다.
    for mode in ('pytest-pattern', 'pytest-testpaths', 'explicit-path'):
        repo, root, base, folder = project(temp, 'hidden-config-' + mode)
        rel = 'quality/_support.py' if mode == 'pytest-testpaths' else 'quality/check_home.py'
        m = incoming(repo, root, {rel: BAD}, folder)
        got = run(root, base)
        shape('설정 앞 발견 0 ' + mode, got[0] == 0 and '[TG2]' not in got[1], got)
        if mode == 'explicit-path':
            write(root, '.dddjango-web/run/build-state.json', json.dumps({'git_snapshot': base, 'test_command': 'pytest ' + rel}))
        else:
            write(root, 'pytest.ini', '[pytest]\n' + ('python_files = check_*.py\n' if mode == 'pytest-pattern' else 'testpaths = quality\n'))
            lane_commit(repo, 'lane-config', 'pytest.ini')
        retained('수집 설정에 기댄 상류 파일 ' + mode, run(root, base), reason='유입 증명 실패(수집 설정에 기댄 시험 경로)', flow=(rel, '4'))
    # 심볼릭 링크 — TG2 의 경로 판정은 링크를 풀어 본다. 레인이 손댄 링크가 있으면 받은 파일의 발견도 남긴다.
    for mode in ('committed', 'untracked'):
        repo, root, base, folder = project(temp, 'hidden-link-' + mode)
        m = incoming(repo, root, {TEST: LINKED}, folder)
        got = run(root, base)
        shape('link 앞 발견 0', got[0] == 0 and '[TG2]' not in got[1], got)
        os.symlink(str(outside), root / 'web_test/data')
        if mode == 'committed':
            lane_commit(repo, 'lane-link', 'web_test/data')
        retained('레인이 더한 심볼릭 링크 ' + mode, run(root, base), reason='유입 증명 실패(레인이 손댄 심볼릭 링크)')
    repo, root, base, folder = project(temp, 'hidden-link-file')
    m = incoming(repo, root, {'web_test/impl_body.py': BAD}, folder, prepare=lambda: os.symlink('impl_body.py', root / TEST))
    write(root, 'web_test/impl_body.py', BAD + LANE_LINE)
    lane_commit(repo, 'lane-change', 'web_test/impl_body.py')
    code, out = got = run(root, base)
    shape('link-file', git(repo, 'ls-tree', 'HEAD', TEST).startswith('120000') and TEST + ':5' in heads(out, 'TG2'), got)
    retained('시험이 심볼릭 링크 — 가리키는 파일을 레인이 수정', got)
    # 증명 조회 실패는 그 경로만 — 다른 수신 파일의 가름으로 번지지 않는다.
    repo, root, base, folder = project(temp, 'hidden-fault-one')
    m = incoming(repo, root, {TEST: BAD, 'web_test/test_y.py': BAD}, folder)
    code, out = got = run(root, base, fault=('hash-object', 'web_test/test_y.py'))
    lane_part, upstream = sections(out)
    check('숨김 0 조회 실패는 그 경로만',
          code == 2 and heads(lane_part, 'TG2') == ['web_test/test_y.py:3'] and heads(upstream, 'TG2') == [TEST + ':3']
          and KEPT + '유입 증명 실패(경로 추적 불능)' in lane_part and '유입: ' + m[:12] + PROOF in upstream
          and out.count(GATHERED % 1) == 1 and out.count(FLOW % ('web_test/test_y.py', '4')) == 1
          and '승인 유입 판정 불가' not in out and 'blocker 1건 · 승인 유입 1건(종료 코드 제외)' in out, got)

    # ================= B. 무변 대조 — 고치기 전 러너와 출력 byte 동일
    repo, root, base, folder = project(temp, 'same-no-merge')
    write(root, TEST, BAD + IMAGE)
    for extra, only in (([], 'tg2,tg3'), (['--slice-end'], None), ([], WIDE)):
        now = run(root, base, extra, only)
        check('B byte 병합 없음 %s' % (' '.join(extra) or only),
              now == before(root, base, extra, only) and now[0] == 2 and '[TG2] BLOCKER' in now[1] and FLOW % (TEST, '4') in now[1], now)
    repo, root, base, folder = project(temp, 'same-no-tg')
    incoming(repo, root, {'web/old/bad.py': 'class Bad:\n    pass\n', TEST: SAFE}, folder)
    for only in ('nm', 'tg2,tg3', WIDE):
        now = run(root, base, only=only)
        check('B byte TG 없는 병합 %s' % only, now == before(root, base, only=only) and '수신 증명' not in now[1], now)
    write(root, 'web_test/test_lane.py', BAD)
    lane_commit(repo, 'lane-test', 'web_test/test_lane.py')
    now = run(root, base)
    check('B byte 병합 + 레인 시험만 TG', now == before(root, base) and now[0] == 2 and FLOW % ('web_test/test_lane.py', '4') in now[1], now)
    repo, root, base, folder = project(temp, 'mixed')
    view = 'web/application/sample/presentation_layer/view/sample_view.py'
    m = incoming(repo, root, {TEST: BAD, view: 'def sample_view(request):\n    return request\n'}, folder)
    code, out = got = run(root, base, only='nm,tg2,tg3')
    lane_part, upstream = sections(out)
    check('B L·수신 증명 동시', code == 0 and not heads(lane_part, 'NM18') and not heads(lane_part, 'TG2')
          and re.search(r'^\[NM18\] BLOCKER — %s\n  위반: [^\n]+\n  교정: [^\n]+\n    ↳ 유입: %s\(L 증명\) · 파일 그대로$' % (re.escape(view), m[:12]), upstream, re.M)
          and re.search(r'^\[TG2\] BLOCKER — %s:3\n  위반: [^\n]+\n  교정: [^\n]+\n    ↳ 유입: %s%s$' % (re.escape(TEST), m[:12], re.escape(PROOF)), upstream, re.M)
          and '== 승인 유입(발주자 승인 병합 경유 · 증명 — 종료 코드 제외 · G2 배너에 올린다) 2건 ==' in out
          and 'blocker 0건 · 승인 유입 2건(종료 코드 제외)' in out, got)
    # TG 수신 증명은 부모 측정·스냅숏을 만들지 않는다.
    import src.inflow as inflow
    from unittest.mock import patch
    ctx = BackstopContext.build(root, base, False)
    with patch.object(inflow.tempfile, 'mkdtemp', side_effect=AssertionError('TG snapshot forbidden')):
        res = inflow.split_inflow(ctx, [f for f in run_tests(ctx) if f.check_id in ('TG2', 'TG3')], str(folder))
    check('B TG 부모 측정·스냅숏 0', [(f.check_id, sha) for f, sha in res.inflow] == [('TG2', m)] and not res.remaining
          and not res.notices and res.received_tests == {TEST}, (res.inflow, res.remaining, res.notices))

print(f'fixtures_patch226: PASS={PASS} FAIL={FAIL}')
sys.exit(bool(FAIL))
