# WN — 명명 8종 (값 정본: discipline-web-houserules §4 명명 규약 총괄표의 기계 판별 가능 행).
# 게이트: added 파일. 대응 존재 검사(WN6)는 파일시스템 기준 — 같은 슬라이스 동시 생성 합법.
#
# *왜 결정적 백스톱인가*: 종류 폴더↔접미사↔접두의 일치는 문자열 비교로 환원된다.
# 접미사 판별은 긴 것 우선(§4-2 — `_view_model.py`는 view_model이지 view가 아니다).
# (판형: dddart check_naming)

import re
from typing import Dict, List, Optional, Set

from .common import (
    KIND_PY_SUFFIX, MARKER_FILES, BackstopContext, Finding, base_name_of,
    segs_of, stem_of, tokens_contain,
)

_SNAKE_RE = re.compile(r'^[a-z0-9_]+(\.[a-z0-9]+)+$')


def run_naming(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    added: List[str] = [f for f in ctx.files if ctx.is_added(f)]

    # 화면 개념 이름 수집 (파일시스템 기준 — WN3 view 이름 금지 대조용)
    area_views: Dict[str, Set[str]] = {}
    all_views: Set[str] = set()
    for d in ctx.dirs:
        s: List[str] = segs_of(d)
        if len(s) == 2 and s[0] in ctx.areas and s[1] != 'widget':
            area_views.setdefault(s[0], set()).add(s[1])
            all_views.add(s[1])

    for f in added:
        s = segs_of(f)
        base: str = base_name_of(f)
        if base in MARKER_FILES:
            continue

        # ---- WN8: 파일명 snake_case (§4 공통원칙 1 — vendored htmx는 원명 그대로 예외)
        if not _SNAKE_RE.fullmatch(base) and not base.startswith('htmx'):
            out.append(Finding('WN8', f, None,
                '파일명 `%s` — snake_case 위반(소문자·숫자·언더스코어)' % base,
                'snake_case로 개명한다 — 템플릿·CSS는 파일명 자체가 계약이다.', '§4'))

        in_concept_kind: bool = (len(s) == 4 and s[0] in ctx.areas
                                 and s[1] != 'widget' and s[2] in KIND_PY_SUFFIX)
        view_name: str = s[1] if len(s) >= 2 else ''

        # ---- WN1: 종류 폴더 ↔ 파일 접미사 (§4 총괄표)
        if in_concept_kind:
            kind: str = s[2]
            suffix: str = KIND_PY_SUFFIX[kind]
            if kind == 'view' and base.endswith('.html'):
                pass  # 페이지 템플릿 — 이름은 WN4가 본다
            elif not base.endswith(suffix):
                out.append(Finding('WN1', f, None,
                    '%s/ 폴더의 파일 `%s` — 접미사 `%s` 위반(축약·타 종류 접미사 금지)'
                    % (kind, base, suffix),
                    '`%s%s`로 개명한다 — 종류는 폴더가 결정하고 접미사가 재확인한다.'
                    % (view_name, suffix), '§4'))
        elif len(s) == 4 and s[0] in ctx.areas and s[1] != 'widget' and s[2] == 'section':
            if not base.endswith('.html'):
                out.append(Finding('WN1', f, None,
                    'section/ 폴더의 비템플릿 파일 `%s` — section은 .html 조각 전용' % base,
                    '코드는 종류 폴더(view/·view_model/·state/·form/)로, 조각만 section/에 둔다.',
                    '§4'))
        elif len(s) == 3 and s[0] in ctx.areas and s[1] == 'widget':
            if not base.endswith('.html'):
                out.append(Finding('WN1', f, None,
                    'widget/ 폴더의 비템플릿 파일 `%s` — widget은 .html 조각 전용' % base,
                    '코드는 화면 개념 폴더의 종류 폴더로 옮긴다.', '§4'))
        elif len(s) == 3 and s[0] == 'client':
            if not (base.endswith('_client.py') or base == 'exception.py'):
                out.append(Finding('WN1', f, None,
                    'client BC 직속 파일 `%s` — 허용은 `<capability>_client.py`·exception.py뿐' % base,
                    '계약 클라이언트면 `_client.py` 접미사로, 응답 모델이면 response/로.', '§4'))
        elif len(s) == 4 and s[0] == 'client' and s[2] == 'response':
            if not base.endswith('_response.py'):
                out.append(Finding('WN1', f, None,
                    'response/ 폴더의 파일 `%s` — 접미사 `_response.py` 위반' % base,
                    '`<response>_response.py`로 개명한다.', '§4'))
        elif (len(s) == 4 and s[0] == 'design_system' and s[1] == 'component'
              and not base.endswith('.html')):
            out.append(Finding('WN1', f, None,
                'component 부품군의 비템플릿 파일 `%s` — component는 .html 부품 전용' % base,
                '시각 값은 foundation/tokens.css로, 부품 조각만 component/<부품군>/에 둔다.', '§4'))

        # ---- WN2: section 접두 — 소속 view 접두 실재 대조 (§4-4)
        if (len(s) == 4 and s[0] in ctx.areas and s[1] != 'widget'
                and s[2] == 'section' and base.endswith('.html')):
            stem: str = stem_of(f)
            if not (stem.startswith(view_name + '_') and len(stem) > len(view_name) + 1):
                out.append(Finding('WN2', f, None,
                    'section `%s` — 소속 view 접두 필수(`%s_<section>.html`)' % (base, view_name),
                    '화면 전속 조각은 `%s_` 접두로 개명한다 — 접두 없는 재사용 조각이면 '
                    'widget/ 또는 design_system 승격을 판별한다.' % view_name, '§4'))

        # ---- WN3: widget·component 이름에 view 이름 금지 (§4-4)
        if len(s) == 3 and s[0] in ctx.areas and s[1] == 'widget' and base.endswith('.html'):
            hit: Optional[str] = _view_hit(stem_of(f), area_views.get(s[0], set()))
            if hit:
                out.append(Finding('WN3', f, None,
                    'widget `%s` — 이름에 view 이름 `%s` 포함(화면 전속 신호)' % (base, hit),
                    '화면 전속이면 그 화면 section/으로 옮기고 접두를 달거나, '
                    '재사용 부품이면 화면 무관 어휘로 개명한다.', '§4'))
        if (len(s) == 4 and s[0] == 'design_system' and s[1] == 'component'
                and base.endswith('.html')):
            hit = _view_hit(stem_of(f), all_views)
            if hit:
                out.append(Finding('WN3', f, None,
                    'component `%s` — 이름에 view 이름 `%s` 포함(BC·화면 어휘 금지)' % (base, hit),
                    '순수 시각 부품 어휘로 개명한다 — 화면 어휘가 필요하면 component 실격, '
                    '그 화면 section/·영역 widget/으로 내린다.', '§4'))

        # ---- WN4: 페이지 템플릿 = 화면명 (§4 — `<view>/view/<view>.html`)
        if (len(s) == 4 and s[0] in ctx.areas and s[1] != 'widget'
                and s[2] == 'view' and base.endswith('.html')):
            if base != view_name + '.html':
                out.append(Finding('WN4', f, None,
                    '페이지 템플릿 `%s` — 소속 화면명과 불일치(`%s.html`이어야 한다)' % (base, view_name),
                    '같은 개념은 위치가 달라도 같은 철자다 — `%s.html`로 개명하거나 '
                    '다른 화면이면 새 `<화면>/` 폴더로 분리한다.' % view_name, '§4'))

        # ---- WN5: component 부품군 접미사 (§4 — button/ 안은 *_button.html)
        if (len(s) == 4 and s[0] == 'design_system' and s[1] == 'component'
                and base.endswith('.html')):
            group: str = s[2]
            stem = stem_of(f)
            if stem != group and not stem.endswith('_' + group):
                out.append(Finding('WN5', f, None,
                    'component `%s` — 부품군 `%s/`의 접미사 `_%s` 위반' % (base, group, group),
                    '`<수식>_%s.html`로 개명하거나 맞는 부품군 폴더로 옮긴다.' % group, '§4'))

        # ---- WN6·WN7: 삼총사 접두 (§4-3 — 접두=view stem에서 `_view`를 뗀 것, VM 기준 대응)
        if in_concept_kind:
            suffix = KIND_PY_SUFFIX[s[2]]
            if base.endswith(suffix):
                prefix: str = base[:-len(suffix)]
                if prefix.endswith('_view'):
                    out.append(Finding('WN7', f, None,
                        '접두 `%s` — 접두에 `_view`를 끼운 형태(`…_view%s` 류) 금지' % (prefix, suffix),
                        '접두는 view 파일 stem에서 `_view`를 뗀 것이다 — `%s%s`로 개명한다.'
                        % (view_name, suffix), '§4'))
                elif prefix != view_name:
                    out.append(Finding('WN6', f, None,
                        '접두 `%s` — 소속 화면 개념 `%s`와 불일치(1:1:1:1 대응·어순 포함 동일 철자)'
                        % (prefix, view_name),
                        '`%s%s`로 개명하거나, 다른 화면 개념이면 새 `<화면>/` 폴더로 분리한다.'
                        % (view_name, suffix), '§4'))

        # ---- WN6: VM 기준 대응 — VM이 존재하면 view·state·페이지 템플릿 대응 (§4-3)
        if (in_concept_kind and s[2] == 'view_model'
                and base == view_name + '_view_model.py'):
            missing: List[str] = []
            root: str = s[0] + '/' + s[1]
            for req in ('view/%s_view.py' % view_name, 'state/%s_state.py' % view_name,
                        'view/%s.html' % view_name):
                if (root + '/' + req) not in ctx.files_set:
                    missing.append(req)
            if missing:
                out.append(Finding('WN6', f, None,
                    'VM `%s` 대응 미완 — 같은 접두의 %s 부재' % (base, ', '.join(missing)),
                    '삼총사+페이지 템플릿은 1:1:1:1이다 — 누락 파일을 같은 접두로 생성한다'
                    '(정적 화면이면 VM 없이 view+템플릿만).', '§4'))

    return out


def _view_hit(stem: str, views: Set[str]) -> Optional[str]:
    for v in sorted(views, key=len, reverse=True):
        if tokens_contain(stem, v):
            return v
    return None
