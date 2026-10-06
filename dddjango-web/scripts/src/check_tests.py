# TG — 행위검증 테스트 산출 1종. 게이트: 신규 BC(web-side is_added_dir).
#
# *왜 결정적 백스톱인가*: coder 산출이 green=py_compile·manage.py check 신규 0으로만 정의되면
# 행위검증 테스트가 창발에 맡겨진다. 신규 BC가 대응 `web_test/`에 행위 테스트를 *갖는가*는
# 입력 불변의 기계 사실이다. 신규 BC 판별은 web-side is_added_dir(유효 게이트) · web_test/ 검사는
# 파일 I/O(ST4 _skeleton과 동일 기법 — web-상대 정본 불변식 불침해). web_test/ 파일엔
# NM/import 규약을 적용하지 않는다.
# 한계(정직): 테스트 *존재*는 결정적이나 *비-vacuity*(행위를 진짜 두드림)는 미보장 —
# 그건 coder 책무(행위당 깨지면-red 테스트)+discipline-reviewer 의미감사의 분업이다.
# (판형: dddart check_tests.dart)

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Set

from .common import BackstopContext, Finding, base_name_of, segs_of

_RULE_TG: str = 'discipline-test — coder 행위검증 테스트 산출(green=pytest web_test)'


def run_tests(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    if not ctx.can_detect_new_units:
        ctx.notices.append('[info] TG(행위테스트) 생략 — git 기준점 없음(신규 BC 판별 불가)')
        return out
    test_root: Path = ctx.root / 'web_test'
    moved: Set[str] = _rename_targets(ctx)
    for d in sorted(ctx.dirs):
        s: List[str] = segs_of(d)
        # BC = `application/<bc>` 또는 `application/<area>/<bc>` — web_test/는 web/ 1:1 미러라 area 경로를 그대로 따른다.
        is_bc: bool = s[0] == 'application' and (
            (len(s) == 2 and s[1] not in ctx.areas) or (len(s) == 3 and s[1] in ctx.areas))
        if not (is_bc and ctx.is_added_dir(d)):
            continue
        # 옮기기만 한 새 BC(슬라이스 0 이동 — 행위 파일이 전부 기준점에서 옮겨 온 파일)는 새 행위가 없다 —
        # 행위 테스트를 새로 요구하지 않는다(기존 테스트 충분 가정 · 미러 테스트는 함께 옮긴다).
        behavior: List[str] = [f for f in ctx.files if f.startswith(d + '/') and base_name_of(f) != '__init__.py']
        if behavior and all(f in moved for f in behavior):
            ctx.notices.append('[info] TG1 — 신규 BC `%s` 는 옮긴 파일만(기준점에서 옮겨 온 파일 %d개) — '
                               '행위 테스트를 새로 요구하지 않는다(기존 테스트 충분 가정)' % (d, len(behavior)))
            continue
        bc_test_dir: Path = test_root / d
        has_test: bool = bc_test_dir.is_dir() and any(p.is_file() for p in bc_test_dir.rglob('*_test.py'))
        if not has_test:
            out.append(Finding('TG1', d, None,
                '신규 BC `%s` 행위검증 테스트 부재 — `web_test/%s/`에 `*_test.py` 0건. '
                'green 빌드가 비-vacuous 검증으로 안 이어진다.' % (s[-1], d),
                _RULE_TG,
                '명세 행위목록 각 항목마다 그 행위를 두드리는(깨지면 red) pytest 테스트를 `web_test/%s/<계층>/`에 '
                '산출한다(페이지·조각 GET 200 스모크만으로는 불충분).' % d))
    return out


def _rename_targets(ctx: BackstopContext) -> Set[str]:
    """기준점 → 작업 트리에서 기준점 파일을 옮겨 온 경로(web-상대) — git 개명(유사도 30% 이상) 대상과, 이름이 같은
    기준점 파일이 사라진 경로. 슬라이스 0 은 옮기며 import·템플릿 이름을 치환하므로 작은 파일은 git 기본 개명
    유사도(50%) 밑으로 떨어진다 — 그래도 옮긴 파일이다."""
    r = subprocess.run(['git', '-C', str(ctx.root), 'diff', '-M30%', '--name-status', '-z', '--relative',
                        str(ctx.diff_base), '--', 'web/'], capture_output=True)
    if r.returncode != 0:
        return set()
    tok: List[str] = r.stdout.decode('utf-8', 'surrogateescape').split('\0')
    out: Set[str] = set()
    added: Set[str] = set()
    gone: Set[str] = set()
    i: int = 0
    while i < len(tok) - 1:
        st: str = tok[i]
        if not st:
            i += 1
            continue
        if st[0] in 'RC':
            new: str = tok[i + 2] if i + 2 < len(tok) else ''
            if st[0] == 'R' and new.startswith('web/'):
                out.add(new[len('web/'):])
            i += 3
            continue
        if st[0] == 'A' and tok[i + 1].startswith('web/'):
            added.add(tok[i + 1][len('web/'):])
        elif st[0] == 'D':
            gone.add(base_name_of(tok[i + 1]))
        i += 2
    return out | {f for f in added if base_name_of(f) in gone}
