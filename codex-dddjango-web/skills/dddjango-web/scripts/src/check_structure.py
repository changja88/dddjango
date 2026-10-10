# ST — 구조·경로 13종 (ST0~ST12). 게이트: added 파일·added 디렉터리, ST4만 신규 단위.
# 국소 ruff.toml(BC 루트·common·root·design_system)·.gitkeep 등 비코드 파일은 직속 검사가 막지 않는다(ST1 area 직속 제외).
#
# *왜 결정적 백스톱인가*: 트리의 형태(어떤 폴더·어떤 직속 파일이 합법인가)는 제1 규약
# §2·§5가 전수 화이트리스트로 정의한다 — LLM 판단이 0인 영역이며, 위반은 항상
# "규약 밖 경로의 존재"라는 기계적 사실이다. 거짓양성 게이트 = added 한정(레거시 면책).
# (판형: dddart check_structure.dart — ST0~ST11 번호 그대로 · ST12 = web/static/ 트리 · ST12 vendor 분기 =
#  v1.3.1 WS6 vendor 분기 — 등재 공식 SDK 사본 자리(discipline-houserules §9))
# 제품 분기(2.3.0 · web 새 분기 — dddart 대응 없음 · src/products.py): 제품 선언(web/product_registry.json)이 있으면
#   ST10 은 제품 뿌리(`design_system/` · `design_system/<id>/`)를 뗀 상대 경로에 같은 규칙을 걸고, 뿌리 직속 디렉터리를
#   허용 목록으로 본다(평면 = 네 종류 + 선언된 own 뿌리 · own = 네 종류만 — 조용한 무검사를 만들지 않는다).
#   ST4 는 선언된 own 제품의 뿌리 골격(네 폴더 + 표준 7 파일)과 셸을 신설 여부와 무관하게 본다(슬라이스 끝에서는 미룸).
#   선언이 없으면 뿌리는 평면 하나라 2.2.x 와 같다. Finding 경로는 실제 물리 경로다.

from __future__ import annotations

from typing import Dict, List, Set

from .common import (
    APP_KINDS, COMMON_DIRS, DOMAIN_KINDS, DS_DIRS, FOUNDATION_FILES, FOUNDATION_TOKENS, HTMX_CORE,
    INFRA_KINDS, LAYER_NAMES, LOCAL_LINT, PRES_KINDS, ROOT_DIRS, SCAFFOLD_DIRS, STATIC_DIRS,
    WEB_TOP_DIRS, WEB_TOP_FILES, BackstopContext, Finding, base_name_of, bc_index, ext_of,
    is_marker, is_python_path, segs_of,
)
from .products import Products, products_state
from .sdk_registry import VENDOR_DIR, is_os_junk_name, sdk_state

_RULE2: str = '제1 규약 §2 표준 트리'
_RULE5: str = '제1 규약 §5 골격 완비'


def run_structure(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    added_files: List[str] = [f for f in ctx.files if ctx.is_added(f) and not is_marker(f)]
    added_dirs: List[str] = sorted(d for d in ctx.dirs if ctx.is_added_dir(d))
    # ruff.toml·.gitkeep 등 비코드 파일은 ST0~ST11 직속 검사 대상이 아니다(dddart 의 비dart 파일과 같음).

    # ---- ST0: web/ 직속 화이트리스트
    for f in added_files:
        if '/' not in f and f not in WEB_TOP_FILES:
            out.append(Finding('ST0', f, None,
                'web/ 직속 허용 외 파일 — 허용: __init__.py·apps.py·urls.py(Django 고정 자리)·'
                '5컨테이너(root/application/common/design_system/static)',
                _RULE2,
                '내용의 정체대로 재배치한다 — BC 코드면 application/<bc>/, 조립이면 root/, 횡단이면 common/, '
                '시각이면 design_system/, 정적 자산이면 static/.'))
    for d in added_dirs:
        if '/' not in d and d not in WEB_TOP_DIRS:
            out.append(Finding('ST0', d, None,
                'web/ 직속 허용 외 디렉터리 `%s/` — 5컨테이너 외 최상위 폴더 금지(templates/·migrations/ 포함)' % d,
                _RULE2, '기능 코드는 application/<bc>/ 4계층으로, 공용은 common/·design_system/으로, '
                '템플릿은 TEMPLATES DIRS = web/ 뿌리라 제 계층 폴더에 둔다.'))

    # ---- ST1: application/ 직속·area 직속 파일 금지 (`__init__.py` 표지 외 — ruff.toml·.gitkeep 포함)
    # area 직속 *코드* 파일은 별도 불요 — 있으면 area로 판별되지 않아(보수 폴백) 그 폴더는 BC 취급 → ST2/ST4가 발화한다.
    for f in ctx.all_files:
        s: List[str] = segs_of(f)
        if s[0] != 'application' or s[-1] == '__init__.py' or not ctx.is_added(f):
            continue
        if len(s) == 2:
            out.append(Finding('ST1', f, None,
                'application/ 직속 파일 — 직속은 BC(또는 area) 디렉터리만', _RULE2,
                '소속 BC를 정해 application/<bc>/ 안으로 옮긴다(라우터·내비게이터면 그 BC 직속).'))
        elif len(s) == 3 and s[1] in ctx.areas:
            out.append(Finding('ST1', f, None,
                'area `%s/` 직속 파일 — area 직속은 BC 폴더만(`__init__.py` 외 파일·ruff.toml·.gitkeep 금지)' % s[1],
                _RULE2, 'area는 순수 시각 네임스페이스 — 파일은 그 아래 BC 안 제자리로, 국소 lint는 BC 루트에 둔다.'))

    # ---- ST2: BC 직속 파일 2종 + <bc> 바인딩 (area 하위 BC 포함)
    for f in added_files:
        s = segs_of(f)
        if s[0] != 'application':
            continue
        bi: int = bc_index(s, ctx.areas)
        if len(s) == bi + 2:
            bc: str = s[bi]
            name: str = s[-1]
            if name not in ('%s_router.py' % bc, '%s_navigator.py' % bc):
                out.append(Finding('ST2', f, None,
                    'BC 직속 허용 외 파일 — 허용은 `%s_router.py`·`%s_navigator.py` 2종(접두=BC 폴더명)뿐' % (bc, bc),
                    '제1 규약 §3.1', '계층 폴더 안 제자리로 옮기거나, 라우팅 짝이면 BC명 접두로 개명한다.'))

    # ---- ST3: BC 1뎁스 = 4계층 화이트리스트 (area 하위 BC 포함)
    for d in added_dirs:
        s = segs_of(d)
        if s[0] != 'application':
            continue
        bi = bc_index(s, ctx.areas)
        if len(s) == bi + 2 and s[-1] not in LAYER_NAMES:
            out.append(Finding('ST3', d, None,
                'BC 직속 허용 외 디렉터리 `%s/` — 4계층 고정 표기만(domain_layer·application_layer·'
                'infra_layer·presentation_layer)%s' % (s[-1], _typo_hint(s[-1], LAYER_NAMES)),
                _RULE2, '4계층 중 정체에 맞는 폴더로 옮기고 오타면 표기를 교정한다.'))

    # ---- ST5: domain_layer 직속·애그리거트 폴더 내부
    for f in added_files:
        s = segs_of(f)
        if s[0] != 'application' or 'domain_layer' not in s:
            continue
        di: int = s.index('domain_layer')
        if di == len(s) - 2:
            out.append(Finding('ST5', f, None,
                'domain_layer 직속 파일 — 직속은 `<aggregate>/` 디렉터리만', '제1 규약 §3.2',
                '애그리거트 폴더(기본값: BC 동명)를 만들어 그 안으로.'))
        elif di == len(s) - 3:
            agg: str = s[di + 1]
            if s[-1] not in ('%s.py' % agg, 'exception.py'):
                out.append(Finding('ST5', f, None,
                    '애그리거트 폴더 직속 허용 외 파일 — 허용은 `%s.py`(루트)·`exception.py`뿐' % agg,
                    '제1 규약 §3.2', '5종 폴더(entity·value_object·enum·domain_service·specification) 중 제자리로.'))
    for d in added_dirs:
        s = segs_of(d)
        if s[0] != 'application' or 'domain_layer' not in s:
            continue
        di = s.index('domain_layer')
        if di == len(s) - 3 and s[-1] not in DOMAIN_KINDS:
            out.append(Finding('ST5', d, None,
                '애그리거트 하위 허용 외 디렉터리 `%s/` — 5종 폴더만%s' % (s[-1], _typo_hint(s[-1], DOMAIN_KINDS)),
                '제1 규약 §3.2', 'entity·value_object·enum·domain_service·specification 중 정체에 맞게.'))

    # ---- ST6: 계층/개념 폴더 직속 종류 화이트리스트 (+infra 평면, area 하위 BC 포함)
    for d in added_dirs:
        s = segs_of(d)
        if s[0] != 'application':
            continue
        bi = bc_index(s, ctx.areas)
        if len(s) < bi + 3:
            continue
        layer: str = s[bi + 1]
        name = s[-1]
        if layer in ('application_layer', 'presentation_layer'):
            kinds: Set[str] = APP_KINDS if layer == 'application_layer' else PRES_KINDS
            if len(s) == bi + 3:
                continue  # 계층 직속 비종류 디렉터리 = 개념 폴더(합법, §4)
            if len(s) == bi + 4 and name not in kinds:
                out.append(Finding('ST6', d, None,
                    '개념 폴더 하위 허용 외 디렉터리 `%s/` — %s만%s' % (
                        name, 'app 5종' if layer == 'application_layer' else 'pres 4종', _typo_hint(name, kinds)),
                    '제1 규약 §4·§5', '종류 폴더 표기로 교정하거나 제자리로 옮긴다.'))
        elif layer == 'infra_layer':
            if len(s) == bi + 3 and name not in INFRA_KINDS:
                out.append(Finding('ST6', d, None,
                    'infra_layer 직속 허용 외 디렉터리 `%s/` — infra는 평면 유지(개념 폴더 금지), '
                    '3종(data_source·repository·service)만%s' % (name, _typo_hint(name, INFRA_KINDS)),
                    '제1 규약 §4', '종류 3폴더로 정리한다.'))
            elif len(s) == bi + 4 and s[bi + 2] == 'data_source':
                out.append(Finding('ST6', d, None,
                    'data_source 하위 디렉터리 `%s/` — data_source는 평면(로컬 저장 하위층 없음)' % name,
                    '제1 규약 §4', 'API 접근 DataSource 파일을 data_source/ 직속에 둔다.'))

    # ---- ST7: 구명칭 디렉터리 deny + BC·area 이름 deny(계층·컨테이너명)
    bc_deny: Set[str] = {'app', 'bridge', 'block', 'viewmodel', 'repo', 'container'}
    name_deny: Set[str] = LAYER_NAMES | {'root', 'application', 'common', 'design_system', 'static'}
    for d in added_dirs:
        s = segs_of(d)
        if s[0] == 'application' and len(s) > 2 and s[-1] in bc_deny:
            out.append(Finding('ST7', d, None, '구명칭 디렉터리 `%s/`' % s[-1], '제1 규약 §8·§9-8',
                'app→use_case, bridge→shared_state, block→section, viewmodel→view_model, repo→repository, '
                'container→view/section/widget 정리.'))
        if (s[0] == 'application' and (len(s) == 2 or (len(s) == 3 and s[1] in ctx.areas))
                and s[-1] in name_deny):
            out.append(Finding('ST7', d, None,
                'BC·area 이름 `%s/` — 계층명·컨테이너명은 BC·area 이름으로 금지(경로 판별 오염)' % s[-1],
                '제1 규약 §2', '기능 어휘로 개명한다 — 계층·컨테이너명은 트리의 예약어다.'))

    # ---- ST8: root 직속·scaffold 직속
    for f in added_files:
        s = segs_of(f)
        if len(s) == 2 and s[0] == 'root':
            out.append(Finding('ST8', f, None, 'root/ 직속 파일 — 직속은 역할 4폴더만', '제1 규약 §3.6',
                'router/·scaffold/·handler/·initializer/ 중 역할에 맞는 폴더로.'))
    for d in added_dirs:
        s = segs_of(d)
        if len(s) == 2 and s[0] == 'root' and s[1] not in ROOT_DIRS:
            out.append(Finding('ST8', d, None,
                'root/ 직속 허용 외 디렉터리 `%s/` — 역할 4폴더만%s' % (s[1], _typo_hint(s[1], ROOT_DIRS)),
                '제1 규약 §3.6', 'router/·scaffold/·handler/·initializer/로 정리.'))
        if len(s) == 3 and s[0] == 'root' and s[1] == 'scaffold' and s[2] not in SCAFFOLD_DIRS:
            out.append(Finding('ST8', d, None,
                'scaffold/ 직속 허용 외 디렉터리 `%s/` — view·view_model·state 3종만' % s[2], '제1 규약 §3.6',
                '삼총사 종류 폴더로 정리한다.'))

    # ---- ST9: root_ 접두
    for f in added_files:
        if segs_of(f)[0] == 'root' and not base_name_of(f).startswith('root_'):
            out.append(Finding('ST9', f, None, 'root/ 이하 파일명 `root_` 접두 위반', '제1 규약 §3.6',
                'root_<이름>으로 개명 — BC 코드의 `web.root…`·`root/…` 참조 한 줄로 위반이 식별되는 설계.'))

    # ---- ST10: design_system — 제품 뿌리 안 상대 경로(r)에 같은 규칙(선언이 없으면 뿌리는 평면 하나)
    products: Products = products_state(ctx)
    for f in added_files:
        s = segs_of(f)
        if s[0] != 'design_system':
            continue
        r: List[str] = products.ds_rel(f)
        if len(r) == 2 and r[0] == 'foundation' and r[1] not in FOUNDATION_FILES:
            out.append(Finding('ST10', f, None,
                'foundation 표준 7파일 외 — 새 토큰 종류는 규약 개정이 먼저(시각 값 단일 출처 보호)',
                '제1 규약 §6', '기존 7파일(app_color.css … app_asset.css) 중 해당 토큰으로 합치거나 규약 개정을 제안한다.'))
        if len(r) == 2 and r[0] == 'theme' and r[1] != 'app_theme.css':
            out.append(Finding('ST10', f, None, 'theme/ 직속은 app_theme.css만', '제1 규약 §6',
                '문서 전역 기본값 조립은 app_theme.css 하나로 — light/dark도 그 안의 확장점.'))
        if len(r) == 2 and r[0] == 'component':
            out.append(Finding('ST10', f, None, 'component/ 직속 파일 금지 — 부품군 1차', '제1 규약 §6',
                '부품군 폴더(button/·dialog/ 등)를 만들어 그 안으로.'))
        if ext_of(f) == '.py':
            out.append(Finding('ST10', f, None, 'design_system 안 Python 파일 — 시각 자리는 템플릿·CSS만',
                '제1 규약 §6', '도메인→UI 매핑은 BC presentation의 ui_extension/으로, 빈 폴더 표지는 .gitkeep으로.'))
    for d in added_dirs:
        split = products.ds_split(d)
        if split is None:
            continue
        pid, r = split
        if len(r) == 2 and r[0] == 'component' and r[1] in {'widget', 'etc', 'common', 'misc'}:
            out.append(Finding('ST10', d, None, 'component/ 정크드로어 군 `%s/` 금지' % r[1], '제1 규약 §6',
                '분류 안 되는 부품은 정크드로어가 아니라 새 부품군 폴더를 만든다.'))
        if products.declared and len(r) == 1 and r[0] not in DS_DIRS:  # 뿌리 직속 허용 목록(선언이 있을 때만)
            if pid in products.own:
                where: str = '제품 `%s` 뿌리(design_system/%s/) 직속 허용 외 디렉터리 `%s/` — 네 종류 폴더만' % (pid, pid, r[0])
            else:
                where = ('design_system/ 직속 허용 외 디렉터리 `%s/` — 제품 선언이 있으면 평면 뿌리 직속은 네 종류 폴더와 '
                         '선언된 제품 뿌리(%s)만' % (r[0], ' · '.join(products.own) or '없음'))
            out.append(Finding('ST10', d, None, '%s(foundation·theme·component·util)%s' % (
                where, _typo_hint(r[0], DS_DIRS | set(products.own) if pid not in products.own else DS_DIRS)),
                '제1 규약 §6', '그 제품 뿌리의 네 종류 폴더 안 제자리로 옮긴다 — 새 제품의 뿌리면 사용자 결정으로 '
                'web/product_registry.json 에 먼저 선언한다(선언은 Coordinator·호스트가 쓴다).'))

    # ---- ST11: common 직속 4종
    for f in added_files:
        s = segs_of(f)
        if len(s) == 2 and s[0] == 'common':
            out.append(Finding('ST11', f, None, 'common/ 직속 파일 금지 — 4종 폴더만', '제1 규약 §6',
                'enum·network·service·util 중 정체에 맞는 폴더로.'))
    for d in added_dirs:
        s = segs_of(d)
        if len(s) == 2 and s[0] == 'common' and s[1] not in COMMON_DIRS:
            out.append(Finding('ST11', d, None,
                'common/ 직속 허용 외 디렉터리 `%s/` — 4종만%s' % (s[1], _typo_hint(s[1], COMMON_DIRS)),
                '제1 규약 §6·§9-11', '입장 판별(§6)대로 — BC 어휘면 그 BC로, 조립이면 root/로, 그 외 4종 중 하나로.'))

    # ---- ST12: web/static/ 트리 — 직속 7칸 · js/·htmx/·root/ 평면 · application/ 은 BC 미러 CSS 만 · vendor/ 는 등재 id
    out.extend(_static_tree(ctx))

    # ---- ST4: 신규 단위 골격 완비 · 선언된 own 제품의 뿌리 골격과 셸(신설 여부 · 기준점과 무관)
    if not ctx.can_detect_new_units:
        ctx.notices.append('[info] ST4(골격 완비) 생략 — git 기준점 없음(신규 단위 판별 불가)')
    else:
        out.extend(_skeleton(ctx))
    out.extend(_product_skeleton(ctx, products))
    return out


# ---------------------------------------------------------------- ST12 구현


def _static_tree(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    rule: str = '제1 규약 §2 web/static/'
    for f in ctx.all_files:
        s: List[str] = segs_of(f)
        if s[0] != 'static' or not ctx.is_added(f) or base_name_of(f) == '.gitkeep':
            continue
        if len(s) == 2:
            out.append(Finding('ST12', f, None,
                'static/ 직속 파일 금지 — application/·root/·js/·htmx/·vendor/·images/·fonts/만', rule,
                '정체에 맞는 칸으로 옮긴다(조각 CSS는 application/<bc>/, 기능 JS는 js/).'))
        elif s[1] == 'root' and (len(s) != 3 or ext_of(f) != '.css'):
            out.append(Finding('ST12', f, None,
                'static/root/ 는 root scaffold 조각 CSS 자리 — 평면 `<조각 stem>.css` 만', rule,
                'static/root/<조각 stem>.css 로 둔다(root scaffold 템플릿과 같은 stem).'))
        elif s[1] == 'htmx' and f != HTMX_CORE:
            out.append(Finding('ST12', f, None,
                'static/htmx/ 는 htmx core `htmx.min.js` 한 파일 자리', rule,
                'core는 htmx.min.js 하나로 두고 기능 JS는 static/js/<기능>.js로 옮긴다.'))
        elif s[1] == 'application':
            bc_dir: str = '/'.join(s[1:-1])
            if ext_of(f) != '.css':
                out.append(Finding('ST12', f, None,
                    'static/application/ 은 presentation 조각 CSS 자리 — `.css`만', rule,
                    '이미지는 static/images/, 기능 JS는 static/js/로 옮긴다.'))
            elif bc_dir not in ctx.dirs or segs_of(bc_dir)[-1] in LAYER_NAMES or not _is_bc_dir(ctx, bc_dir):
                out.append(Finding('ST12', f, None,
                    'static/application/ 경로 `%s/` 가 web/ 의 BC 디렉터리와 1:1 대응하지 않는다'
                    '(BC 직속 평면 — 계층 폴더 없음)' % bc_dir, rule,
                    'static/application/[<area>/]<bc>/<조각 stem>.css 로 둔다.'))
    for d in sorted(ctx.dirs):
        s = segs_of(d)
        if s[0] != 'static' or not ctx.is_added_dir(d):
            continue
        if len(s) == 2 and s[1] not in STATIC_DIRS:
            out.append(Finding('ST12', d, None,
                'static/ 직속 허용 외 디렉터리 `%s/` — application/·root/·js/·htmx/·vendor/·images/·fonts/만%s'
                % (s[1], _typo_hint(s[1], STATIC_DIRS)), rule,
                '임의 칸을 신설하지 않는다 — 시안 이미지는 images/, 웹폰트는 fonts/, 승인·등재된 공식 SDK 사본은 vendor/.'))
        if len(s) == 3 and s[1] in ('js', 'htmx', 'root'):
            out.append(Finding('ST12', d, None,
                'static/%s/ 내부 디렉터리 `%s/` — 평면이다' % (s[1], s[2]), rule,
                '기능당 파일 하나를 static/%s/ 직속에 둔다.' % s[1]))
    out.extend(_vendor_tree(ctx))
    return out


def _vendor_tree(ctx: BackstopContext) -> List[Finding]:
    """ST12 vendor 분기(덫 — 보증은 늘 검사 WV5·WV13): vendor/ 직속은 고정 표지 .gitattributes 만 · 등재 id 밖
    디렉터리 · 등재 id 안 하위 디렉터리 · 등재 id 안 등재 밖 파일 (discipline-houserules §9 · 바탕: v1.3.1 WS6 vendor 분기)."""
    out: List[Finding] = []
    rule: str = 'discipline-houserules §9 공식 SDK'
    prefix: str = VENDOR_DIR + '/'
    added_files: List[str] = [f for f in ctx.all_files if f.startswith(prefix) and ctx.is_added(f)
                              and base_name_of(f) != '.gitkeep' and not is_os_junk_name(base_name_of(f))]
    added_dirs: List[str] = sorted(d for d in ctx.dirs if d.startswith(prefix) and ctx.is_added_dir(d))
    if not added_files and not added_dirs:
        return out
    registered: Dict[str, str] = sdk_state(ctx).files()
    for f in added_files:
        s: List[str] = segs_of(f)
        if len(s) == 3 and s[2] != '.gitattributes':
            out.append(Finding('ST12', f, None,
                'static/vendor/ 직속 파일 — 직속은 고정 표지 .gitattributes 만(사본은 vendor/<sdk_id>/ 안)', rule,
                '공식 SDK 면 G1 승인 뒤 sdk_vendor.py 로 등재하고, 아니면 제3자 JS 를 들이지 않는다.'))
        elif len(s) == 4 and s[2] in registered and f != registered[s[2]]:
            out.append(Finding('ST12', f, None,
                '등재 id 디렉터리 `%s/` 안 등재 밖 파일 — 등재 파일 하나만 둔다' % s[2], rule,
                '사본·목록은 Coordinator 가 sdk_vendor.py 로만 바꾼다.'))
    for d in added_dirs:
        s = segs_of(d)
        if len(s) == 3 and s[2] not in registered:
            out.append(Finding('ST12', d, None,
                'static/vendor/ 의 등재 id 밖 디렉터리 `%s/` — 등재되지 않은 벤더 단위' % s[2], rule,
                '공식 SDK 면 G1 승인 뒤 sdk_vendor.py 로 등재하고, 아니면 들이지 않는다.'))
        elif len(s) == 4 and s[2] in registered:
            out.append(Finding('ST12', d, None,
                '등재 id 디렉터리 `%s/` 안 하위 디렉터리 `%s/` — id 디렉터리는 등재 파일 하나다' % (s[2], s[3]), rule,
                '판 디렉터리를 두지 않는다 — 판 올림은 sdk_vendor.py install --replace.'))
    return out


def _is_bc_dir(ctx: BackstopContext, d: str) -> bool:
    s: List[str] = segs_of(d)
    return len(s) == bc_index(s, ctx.areas) + 1


# ---------------------------------------------------------------- ST4 구현


def _unit_missing(ctx: BackstopContext, unit_dir: str, layer_kinds: Dict[str, Set[str]],
                  required_files: List[str]) -> List[str]:
    """한 단위의 골격 누락 목록 — 종류 폴더 존재 + 표지 + 필수 파일."""
    missing: List[str] = []

    def kind_ok(path: str, label: str) -> None:
        """폴더 존재 + 표지 — Python 경로는 `__init__.py`(패키지 표지 겸), 그 밖은 비면 `.gitkeep`."""
        if path not in ctx.dirs:
            missing.append(label + '/')
        elif is_python_path(path):
            if path + '/__init__.py' not in ctx.files_set:
                missing.append(label + '/__init__.py (빈 폴더 표지 겸 패키지 표지)')
        elif not any(f.startswith(path + '/') for f in ctx.all_files):
            missing.append(label + '/.gitkeep (빈 폴더 유지)')

    for layer, kinds in layer_kinds.items():
        layer_path: str = unit_dir if not layer else unit_dir + '/' + layer
        pre: str = layer + '/' if layer else ''
        if layer_path not in ctx.dirs:
            missing.append(pre + ' (계층/단위 폴더 없음)')
            continue
        for k in sorted(kinds):
            kind_ok(layer_path + '/' + k, pre + k)
    for rf in required_files:
        if unit_dir + '/' + rf not in ctx.files_set:
            missing.append(rf)
    return missing


def _product_skeleton(ctx: BackstopContext, products: Products) -> List[Finding]:
    """ST4 제품 분기 — 선언된 own 제품마다 design_system 뿌리 골격(네 폴더 + 표준 7 파일)과 문서 셸이 있어야 한다.
    선언이 약속한 자리라 신설 여부 · 기준점과 무관하게 본다(G2 직전 실행 · 빚 스캔 — 슬라이스 끝에서는 ST4 째 미룬다)."""
    out: List[Finding] = []
    for pid in products.own:
        root: str = products.ds_root(pid)
        missing: List[str] = (['뿌리 폴더 `web/%s/` 째' % root] if root not in ctx.dirs else _unit_missing(
            ctx, root, {'': DS_DIRS}, ['foundation/app_%s.css' % t for t in FOUNDATION_TOKENS]))
        if missing:
            out.append(Finding('ST4', root, None,
                '선언된 제품 `%s` 의 design_system 뿌리 골격 미완비 — 누락: %s' % (pid, ', '.join(missing)), _RULE5,
                '선언한 제품 뿌리는 비어 있어도 네 종류 폴더(foundation·theme·component·util — 빈 폴더는 .gitkeep)와 '
                '표준 7 파일을 갖춘다.'))
        shell: str = products.shell_of(pid)
        if shell not in ctx.files_set:
            out.append(Finding('ST4', shell, None,
                '선언된 제품 `%s` 의 문서 셸 없음 — own 제품의 셸은 `web/%s`' % (pid, shell), _RULE5,
                '그 제품의 독립 문서 셸을 이 자리에 둔다(다른 제품 셸을 extends 하지 않는다 · state·view_model 짝은 요구하지 않는다).'))
    return out


def _skeleton(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []

    def require_unit(unit_dir: str, unit_desc: str, layer_kinds: Dict[str, Set[str]],
                     required_files: List[str]) -> None:
        missing: List[str] = _unit_missing(ctx, unit_dir, layer_kinds, required_files)
        if missing:
            out.append(Finding('ST4', unit_dir, None,
                '%s 골격 미완비 — 누락: %s' % (unit_desc, ', '.join(missing)), _RULE5,
                '비어 있어도 표준 종류 폴더 전부+표지(Python 경로 __init__.py · design_system .gitkeep)를 생성한다 — '
                '폴더는 무조건, 코드는 필요할 때만.'))

    def direct_kinds(layer_path: str, kinds: Set[str]) -> Set[str]:
        """app·pres 계층 직속에 요구할 종류 — 직속 디렉터리가 있고 종류 이름이 하나도 없을 때만 요구하지 않는다.
        개념 폴더 안 완비(houserules §2·§3)는 아래 «신규 개념 폴더»가 본다."""
        children: Set[str] = {segs_of(x)[-1] for x in ctx.dirs
                              if x.startswith(layer_path + '/') and x.count('/') == layer_path.count('/') + 1}
        split: bool = bool(children) and not (children & kinds)
        return set() if split else kinds

    # 신규 BC (area 하위 포함 — `application/<bc>` 또는 `application/<area>/<bc>`)
    for d in sorted(ctx.dirs):
        s: List[str] = segs_of(d)
        is_bc: bool = s[0] == 'application' and (
            (len(s) == 2 and s[1] not in ctx.areas) or (len(s) == 3 and s[1] in ctx.areas))
        if not (is_bc and ctx.is_added_dir(d)):
            continue
        bc_name: str = s[-1]
        require_unit(d, '신규 BC `%s`' % bc_name, {
            'application_layer': direct_kinds(d + '/application_layer', APP_KINDS),
            'infra_layer': INFRA_KINDS,
            'presentation_layer': direct_kinds(d + '/presentation_layer', PRES_KINDS),
            'domain_layer': set(),
        }, [LOCAL_LINT])  # 타입 명시 국소 lint(houserules §3)
        dom: str = d + '/domain_layer'
        if dom in ctx.dirs and not any(x.startswith(dom + '/') and x.count('/') == dom.count('/') + 1
                                       for x in ctx.dirs):
            out.append(Finding('ST4', dom, None,
                '신규 BC `%s` domain_layer에 애그리거트 폴더 없음 — 기본값은 BC 동명 애그리거트' % bc_name,
                _RULE5, '`domain_layer/%s/` + `%s.py` + 5종 폴더를 생성한다.' % (bc_name, bc_name)))
    # 신규 애그리거트 (domain_layer 상대 판별이라 area 깊이 무관)
    for d in sorted(ctx.dirs):
        s = segs_of(d)
        if s[0] == 'application' and 'domain_layer' in s and s.index('domain_layer') == len(s) - 2 \
                and ctx.is_added_dir(d):
            require_unit(d, '신규 애그리거트 `%s`' % s[-1], {'': DOMAIN_KINDS}, ['%s.py' % s[-1]])
    # 신규 개념 폴더 (app·pres — area 하위 BC 포함)
    for d in sorted(ctx.dirs):
        s = segs_of(d)
        if s[0] != 'application' or not ctx.is_added_dir(d):
            continue
        bi: int = bc_index(s, ctx.areas)
        if len(s) == bi + 3:
            if s[bi + 1] == 'application_layer' and s[-1] not in APP_KINDS:
                require_unit(d, '신규 개념 폴더 `%s`(application)' % s[-1], {'': APP_KINDS}, [])
            if s[bi + 1] == 'presentation_layer' and s[-1] not in PRES_KINDS:
                require_unit(d, '신규 개념 폴더 `%s`(presentation)' % s[-1], {'': PRES_KINDS}, [])
    # root 신설
    if 'root' in ctx.dirs and ctx.is_added_dir('root'):
        require_unit('root', '신규 합성 루트', {'': ROOT_DIRS, 'scaffold': SCAFFOLD_DIRS}, [LOCAL_LINT])
    # design_system 신설 (Python 없음 — 국소 lint 비대상)
    if 'design_system' in ctx.dirs and ctx.is_added_dir('design_system'):
        require_unit('design_system', '신규 design_system', {'': DS_DIRS},
                     ['foundation/app_%s.css' % t for t in FOUNDATION_TOKENS])
    return out


def _typo_hint(name: str, candidates: Set[str]) -> str:
    """종류 폴더 오타 보조 진단 — 편집거리 1 이내면 메시지에 힌트 병기."""
    for c in sorted(candidates):
        if _edit_distance1(name, c):
            return ' — `%s/` 오타 의심' % c
    return ''


def _edit_distance1(a: str, b: str) -> bool:
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    i: int = 0
    j: int = 0
    edits: int = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1
            j += 1
            continue
        edits += 1
        if edits > 1:
            return False
        if len(a) > len(b):
            i += 1
        elif len(a) < len(b):
            j += 1
        else:
            i += 1
            j += 1
    return edits + (len(a) - i) + (len(b) - j) <= 1
