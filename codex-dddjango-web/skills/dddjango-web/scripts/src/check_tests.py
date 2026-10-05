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

from pathlib import Path
from typing import List

from .common import BackstopContext, Finding, segs_of

_RULE_TG: str = 'discipline-test — coder 행위검증 테스트 산출(green=pytest web_test)'


def run_tests(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    if not ctx.can_detect_new_units:
        ctx.notices.append('[info] TG(행위테스트) 생략 — git 기준점 없음(신규 BC 판별 불가)')
        return out
    test_root: Path = ctx.root / 'web_test'
    for d in sorted(ctx.dirs):
        s: List[str] = segs_of(d)
        # BC = `application/<bc>` 또는 `application/<area>/<bc>` — web_test/는 web/ 1:1 미러라 area 경로를 그대로 따른다.
        is_bc: bool = s[0] == 'application' and (
            (len(s) == 2 and s[1] not in ctx.areas) or (len(s) == 3 and s[1] in ctx.areas))
        if not (is_bc and ctx.is_added_dir(d)):
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
