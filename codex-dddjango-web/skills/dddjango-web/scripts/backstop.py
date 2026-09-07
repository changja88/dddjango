#!/usr/bin/env python3
# dddjango-web 결정적 백스톱 러너 — 단일 엔트리, 검사 26종 인프로세스 실행.
# (판형: dddart scripts/backstop.dart · 값 정본: discipline-web-houserules §1~§5·§7)
#
# 사용:
#   python backstop.py <대상 프로젝트 루트> [--diff-base <commit>] [--all]
#                      [--only ws,wi,wn,wp|<검사ID>…]
#                      [--design-build <증거 build 디렉터리>]
#
# 종료코드: 0=clean / 1=사용·내부 오류(미실행 — 통과가 아니다) / 2=blocker(발견 일괄
# 출력 — fail-fast 금지). (houserules §7 exit 계약)
# 게이트: 구조·명명=added 파일/디렉터리, 격리·순수성=touched 파일의 added 줄,
# 골격 완비=신규 단위 → 레거시 불발화. 비git·기준 부재 시 전역 검사로 퇴화 notice.
# 디자인 작업은 인자와 프로젝트의 현재/추적 원본 표식으로 식별한다.

import sys
import json
import subprocess
import traceback
from pathlib import Path
from typing import List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.common import BackstopContext, Finding  # noqa: E402
from src.check_structure import run_structure  # noqa: E402
from src.check_imports import run_imports  # noqa: E402
from src.check_naming import run_naming  # noqa: E402
from src.check_purity import run_purity  # noqa: E402
from check_design_evidence import Defects, implementation_digest, validate_inputs, validate_visual  # noqa: E402

TOTAL_CHECKS: int = 26  # WS8 + WI4 + WN8 + WP6

_USAGE: str = ('사용: python backstop.py <대상 프로젝트 루트> '
               '[--diff-base <commit>] [--all] [--only ws,wi,wn,wp] '
               '[--design-build <dir>]')


def project_design_record(root: Path, name: str) -> dict | None:
    """Read the current record, or its index/HEAD bytes if it was deleted."""
    path = root / name
    if not path.resolve().is_relative_to(root):
        raise ValueError('project design record escapes project root')
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    for revision in ('', 'HEAD'):
        result = subprocess.run(['git', '-C', str(root), 'show', f'{revision}:./{name}'],
                                capture_output=True)
        if result.returncode == 0:
            return json.loads(result.stdout.decode('utf-8'))
    return None


def project_design_builds(root: Path) -> tuple[list[Path], bool, dict[Path, dict]]:
    """Discover source-bearing builds, including tracked files deleted in this run."""
    folder = root / '.dddjango-web'
    if not folder.resolve().is_relative_to(root):
        raise ValueError('project design directory escapes project root')
    names = {path.relative_to(root).as_posix() for path in folder.rglob('*')}
    for command in (['ls-files', '-z', '--', '.dddjango-web'],
                    ['ls-tree', '-rz', '--name-only', 'HEAD', '--', '.dddjango-web']):
        result = subprocess.run(['git', '-C', str(root), *command], capture_output=True)
        if result.returncode == 0:
            names.update(result.stdout.decode('utf-8').strip('\0').split('\0'))
    markers = {'design-ref', 'design-input.json', 'source-manifest.json', 'render-audit.json'}
    builds = set()
    states = {}
    for name in names:
        parts = Path(name).parts
        if len(parts) >= 3 and parts[0] == '.dddjango-web' and parts[2] in markers:
            builds.add(folder / parts[1])
        if len(parts) == 3 and parts[0] == '.dddjango-web' and parts[2] == 'build-state.json':
            state = project_design_record(root, name)
            if state:
                states[(folder / parts[1]).resolve()] = state
                if state.get('has_design_screen') is True:
                    builds.add(folder / parts[1])
    configured = False
    if '.dddjango-web/config.json' in names:
        config = project_design_record(root, '.dddjango-web/config.json')
        source = config.get('design_source') if config else None
        configured = (isinstance(source, dict) and (source.get('type') == 'PROJECT'
                      or ('type' not in source and source.get('engine') == 'claude-design')))
    if any(not build.resolve().is_relative_to(root) for build in builds):
        raise ValueError('project design build escapes project root')
    return sorted(build.resolve() for build in builds), configured, states


def design_commit(root: Path, reference: str) -> str | None:
    result = subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', '--end-of-options',
                             reference + '^{commit}'], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def current_nondesign_scope(root: Path, diff_base: str | None, builds: list[Path],
                           states: dict[Path, dict]) -> bool:
    """Skip only completed, unchanged history for one explicit non-design snapshot."""
    if not diff_base or not builds:
        return False
    base = design_commit(root, diff_base)
    if base is None:
        return False
    matching = []
    for build, state in states.items():
        snapshot = state.get('git_snapshot')
        if isinstance(snapshot, str) and snapshot and design_commit(root, snapshot) == base:
            matching.append((build, state))
    if len(matching) != 1:
        return False
    current, state = matching[0]
    if (state.get('has_design_screen') is not False or current in builds
            or not (current / 'build-state.json').is_file()):
        return False
    for build in builds:
        prior = states.get(build, {})
        if (prior.get('has_design_screen') is not True or prior.get('phase') != 'finalize'
                or prior.get('g2_approved') is not True or prior.get('implementation_visual') != 'verified'
                or prior.get('design_status') != 'ready'):
            return False
        if 'slices' in prior and (not isinstance(prior['slices'], list)
                or any(not isinstance(row, dict) or row.get('status') != 'done' for row in prior['slices'])):
            return False
    for command in (['diff', '--relative', '--name-only', '-z', '--no-renames', base, '--', '.dddjango-web'],
                    ['ls-files', '--others', '-z', '--', '.dddjango-web']):
        result = subprocess.run(['git', '-C', str(root), *command], capture_output=True)
        if result.returncode != 0:
            return False
        for name in result.stdout.decode('utf-8').strip('\0').split('\0'):
            parts = Path(name).parts
            if (name == '.dddjango-web/config.json'
                    or (len(parts) >= 3 and parts[0] == '.dddjango-web' and parts[1] != current.name)):
                return False
    return True


def main(argv: List[str]) -> int:
    target: Optional[str] = None
    diff_base: Optional[str] = None
    all_mode: bool = False
    only: Set[str] = set()
    design_build: Optional[str] = None

    i: int = 0
    while i < len(argv):
        a: str = argv[i]
        if a == '--diff-base':
            i += 1
            if i >= len(argv):
                print('[backstop] 사용 오류: --diff-base 값 없음', file=sys.stderr)
                return 1
            diff_base = argv[i]
        elif a == '--all':
            all_mode = True
        elif a == '--only':
            i += 1
            if i >= len(argv):
                print('[backstop] 사용 오류: --only 값 없음', file=sys.stderr)
                return 1
            only.update(s.strip().lower() for s in argv[i].split(',') if s.strip())
        elif a == '--design-build':
            i += 1
            if i >= len(argv):
                print('[backstop] 사용 오류: --design-build 값 없음', file=sys.stderr)
                return 1
            design_build = argv[i]
        elif a.startswith('--'):
            print('[backstop] 사용 오류: 알 수 없는 옵션 %s' % a, file=sys.stderr)
            return 1
        else:
            target = a
        i += 1

    if target is None:
        print(_USAGE, file=sys.stderr)
        return 1
    root: Path = Path(target).resolve()
    if not root.is_dir():
        print('[backstop] 사용 오류: 디렉터리 아님 — %s' % target, file=sys.stderr)
        return 1

    def family_on(fam: str) -> bool:
        return (not only) or fam in only or any(o.startswith(fam) and len(o) > 2 for o in only)

    def id_on(check_id: str) -> bool:
        if not only:
            return True
        l: str = check_id.lower()
        return l in only or l[:2] in only

    ctx: BackstopContext = BackstopContext.build(root=root, diff_base=diff_base,
                                                 all_mode=all_mode)

    if not ctx.git_repo:
        ctx.notices.append('[info] git 저장소 아님 — 게이트 불가, 전역 검사로 퇴화'
                           '(레거시 발견 폭주 가능). 파이프라인 경로는 git 프로젝트에서 '
                           'Phase 2 진입 스냅샷을 주입한다(houserules §7).')
    elif diff_base is None and not all_mode:
        ctx.notices.append('[info] --diff-base 없음 — 게이트 불가, 전역 검사로 퇴화. '
                           '파이프라인 호출은 Phase 2 진입 스냅샷(git_snapshot)을 '
                           '주입한다(houserules §7).')

    findings: List[Finding] = []
    try:
        if family_on('ws'):
            findings.extend(run_structure(ctx))
        if family_on('wi'):
            findings.extend(run_imports(ctx))
        if family_on('wn'):
            findings.extend(run_naming(ctx))
        if family_on('wp'):
            findings.extend(run_purity(ctx))
    except Exception:
        print('[backstop] 내부 오류:\n%s' % traceback.format_exc(), file=sys.stderr)
        return 1

    shown: List[Finding] = sorted(
        (f for f in findings if id_on(f.check_id)),
        key=lambda f: (f.check_id, f.path, f.line or 0))

    design_defects: List[str] = []
    try:
        discovered, configured, states = project_design_builds(root)
        builds = discovered
        if design_build is not None:
            selected = Path(design_build).resolve()
            if discovered and selected not in discovered:
                design_defects.append('--design-build must select a project design build: %s' %
                                      ', '.join(str(path) for path in discovered))
                builds = []
            else:
                builds = [selected]
        elif current_nondesign_scope(root, diff_base, discovered, states):
            builds = []
            ctx.notices.append('[info] git_snapshot이 일치하는 현재 비시안 작업 — '
                               '완료된 과거 시안 빌드 %d개의 visual 검사 생략' % len(discovered))
        elif configured and not discovered:
            design_defects.append('design_source is configured but no design build was found; --design-build required')
        for build in builds:
            if not build.is_dir():
                design_defects.append('design build 디렉터리/증거가 없음: %s' % build)
            else:
                try:
                    design_spec, input_value, _items = validate_inputs(build, root)
                    implementation_value: str = implementation_digest(root, design_spec)
                    validate_visual(build, root, design_spec, input_value, implementation_value)
                except Defects as error:
                    design_defects.extend(f'{build}: {message}' for message in error.messages)
    except Exception:
        print('[backstop] design evidence 내부 오류:\n%s' % traceback.format_exc(), file=sys.stderr)
        return 1

    for n in ctx.notices:
        print(n)
    if ctx.notices:
        print()
    for f in shown:
        print(f)
        print()
    for message in design_defects:
        print('[DESIGN] BLOCKER — %s' % message)
        print()
    if ctx.gated and diff_base is not None:
        mode: str = 'gated(diff-base %s)' % diff_base[:8]
    elif all_mode:
        mode = 'all'
    else:
        mode = '전역 퇴화'
    print('[backstop] 검사 %d종(%s) — blocker %d건 (구조 %d · 시안 %d)' %
          (TOTAL_CHECKS, mode, len(shown) + len(design_defects), len(shown), len(design_defects)))
    return 0 if not shown and not design_defects else 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
