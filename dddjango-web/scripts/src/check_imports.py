# IM — import 방향 27종 (IM1~IM27). 게이트: touched 파일의 added 줄.
#
# *왜 결정적 백스톱인가*: 계층·컨테이너의 의존 방향(제1 규약 §3.7 매트릭스·§9-3
# 4채널·§3.6 root 규칙)은 정규화된 참조 경로 하나로 판별된다 — 의미 해석 0.
# 참조 = Python import(절대 `web.`·상대는 web/ 루트 클램핑 · 함수 안 import 포함) + 템플릿 `{% extends %}`·
# `{% include %}`·`{% static %}`(TEMPLATES DIRS = web/ 뿌리) + CSS `@import`·`url()`. 조각 CSS
# (`static/application/…`·`static/root/…`)는 소유자의 presentation 자리로 센다(houserules §5).
# 거짓양성 게이트 = added 줄 한정(레거시 파일의 기존 위반 참조에 불발화) + 표준 트리 밖 옛 배치 파일은 층 판정 불가
# 레거시라 층 무관 IM(IM24·IM25·IM27)만 건다
# + 주석·문자열 마스킹(교정 주석의 토큰이 재차 blocker가 되는 루프 차단).
# (판형: dddart check_imports.dart — IM1~IM23 번호 그대로 · IM24~IM27 = web 새 검사)

from __future__ import annotations

import re
from typing import List, Optional, Set

from .common import (
    API_CLIENT, BACKEND_TOP_PKGS, ENTRY_FILES, JSON_FIELD, ROOT_VIEW_TEMPLATE, STDLIB, BackstopContext, Finding,
    base_name_of, bc_of, ext_of, has_seg, is_bc_root_path, is_standard_path, parent_dir_of, ref_path, scan_tokens,
    segs_of,
)

# 층과 상관없는 IM — 표준 트리 밖 옛 배치 파일(층 판정 불가 레거시)에도 건다. 나머지 IM 은 전부 층(경로 마디)
# 의존이라 옛 배치 파일에는 걸지 않는다(houserules §7·§8 — 레거시 불발화 · 이동 요구 없음).
LAYER_FREE_IM: Set[str] = {'IM24', 'IM25', 'IM27'}
_COMPONENT_PREFIX: str = 'design_system/component/'
_HTTP_SURFACE: Set[str] = {'requests', 'httpx', 'aiohttp', 'urllib.request', 'http.client', 'django.test'}
_API_LITERAL_RE = re.compile(r'''["'`]\s*/api/''')


def _http_surface(module: str, names: List[str]) -> Optional[str]:
    for s in sorted(_HTTP_SURFACE):
        if module == s or module.startswith(s + '.'):
            return s
        head, _, tail = s.rpartition('.')
        if head and module == head and tail in names:
            return s
    return None


def run_imports(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    backend: Set[str] = BACKEND_TOP_PKGS | ctx.project_pkgs
    for f in ctx.files:
        if not ctx.is_touched(f):
            continue
        ext: str = ext_of(f)
        if ext not in ('.py', '.html', '.css'):
            continue
        fv: str = ref_path(f)  # 조각 CSS 는 소유자의 presentation 자리로 센다
        segs: List[str] = segs_of(fv)
        bc: Optional[str] = bc_of(fv, ctx.areas)
        base: str = base_name_of(fv)
        parent: str = parent_dir_of(fv)
        in_domain: bool = has_seg(fv, 'domain_layer')
        in_app: bool = has_seg(fv, 'application_layer')
        in_infra: bool = has_seg(fv, 'infra_layer')
        in_pres: bool = has_seg(fv, 'presentation_layer')
        is_bc_root_file: bool = is_bc_root_path(fv, ctx.areas)
        is_navigator: bool = is_bc_root_file and base == '%s_navigator.py' % bc
        is_bc_router: bool = is_bc_root_file and base == '%s_router.py' % bc
        is_entry: bool = f in ENTRY_FILES  # main.dart 자리(web/apps.py·web/urls.py)
        in_root: bool = segs[0] == 'root'
        is_page: bool = in_pres and parent == 'view' and ext == '.html'
        is_root_gate_page: bool = (fv.startswith('root/scaffold/view/') and base.startswith('root_')
                                   and base.endswith('_view.html') and base != 'root_view.html')
        is_fragment_tpl: bool = ext == '.html' and (
            (in_pres and parent in ('section', 'widget')) or fv.startswith(_COMPONENT_PREFIX))
        in_network: bool = fv.startswith('common/network/')
        legacy: bool = not is_standard_path(f)  # 표준 트리 밖 옛 배치 — 층 판정 불가

        def add(cid: str, line: int, msg: str, rule: str, fix: str) -> None:
            if legacy and cid not in LAYER_FREE_IM:
                return
            if ctx.line_is_added(f, line):
                out.append(Finding(cid, f, line, msg, rule, fix))

        for e in ctx.edges_of(f):
            t: str = ref_path(e.target or '')
            internal: bool = e.internal and bool(t)
            py_ext: bool = e.kind == 'py' and not e.internal
            mod: str = e.module or ''

            # ---- IM1: domain → django 금지
            if in_domain:
                if py_ext and e.top == 'django':
                    add('IM1', e.line, 'domain_layer에서 `%s` import — 순수 Python 계층' % mod,
                        '제1 규약 §3.2',
                        'UI 매핑(CSS 클래스·아이콘·라벨)은 presentation의 ui_extension/으로 — 도메인은 표준 라이브러리만.')
                # ---- IM19: domain → 비domain 내부 경로 금지 (직파싱 단일 출처 json_field 하나 예외 —
                #      dddart 모델이 json_serializable 외부 패키지를 쓰던 자리)
                if internal and not has_seg(t, 'domain_layer') and t != JSON_FIELD:
                    add('IM19', e.line, 'domain_layer에서 `%s` 참조 — domain은 domain만 본다(common 포함 금지)' % t,
                        '제1 규약 §3.7', '도메인 이유로만 바뀌는 코드만 남기고, 변환·조율은 UseCase/VM으로 올린다.')

            # ---- IM2: root 참조는 apps.py·urls.py만 (root 내부 상호 참조 · 페이지의 root_view extends 제외)
            if internal and t.startswith('root/') and not in_root and not is_entry:
                if not (e.kind == 'extends' and t == ROOT_VIEW_TEMPLATE and is_page):
                    add('IM2', e.line, 'root/ 참조 `%s` — root를 아는 곳은 apps.py·urls.py뿐'
                        '(페이지 템플릿의 root_view.html extends 1건 예외 · BC가 root를 알면 격리 붕괴)' % t,
                        '제1 규약 §3.6',
                        '필요한 것이 전역 인스턴스면 common으로, 전 BC 배선이면 root handler가 *이쪽을* 호출하는 방향으로 뒤집는다.')

            # ---- IM3·IM4: common·design_system → application·root 금지
            if segs[0] == 'common' and internal and (t.startswith('application/') or t.startswith('root/')):
                add('IM3', e.line, 'common에서 `%s` 참조 — common은 모두가 아는 곳, 아무도 모르면 안 된다' % t,
                    '제1 규약 §6', 'BC 어휘가 필요하면 그 코드는 common 실격 — 해당 BC로 옮기고, BC 일이 필요하면 콜백 주입으로 뒤집는다.')
            if segs[0] == 'design_system' and internal and (t.startswith('application/') or t.startswith('root/')):
                add('IM4', e.line, 'design_system에서 `%s` 참조 — 시각 요소는 BC 어휘를 모른다' % t,
                    '제1 규약 §6', '도메인 의존 부품은 그 BC presentation의 widget으로 내린다.')

            # ---- IM5: 교차 BC 4채널
            if bc is not None and internal:
                tbc: Optional[str] = bc_of(t, ctx.areas)
                if tbc is not None and tbc != bc:
                    ts: List[str] = segs_of(t)
                    in_t_domain: bool = has_seg(t, 'domain_layer')
                    domain_type: bool = in_t_domain and (
                        has_seg(t, 'entity') or has_seg(t, 'value_object') or has_seg(t, 'enum')
                        or (len(ts) >= 3 and ts[-3] == 'domain_layer' and ts[-1] == '%s.py' % ts[-2])
                        or base_name_of(t) == 'exception.py')
                    ok: bool = (domain_type or has_seg(t, 'use_case')
                                or (is_bc_root_path(t, ctx.areas) and base_name_of(t) == '%s_navigator.py' % tbc)
                                or (has_seg(t, 'presentation_layer') and has_seg(t, 'view')))
                    if not ok:
                        reason: str = ('domain_service·specification은 도메인 로직 — 채널①은 타입(엔티티·VO·enum)만, 행위는 UseCase 관문'
                                       if in_t_domain else
                                       'infra·VM·SharedState·state·section·widget·ui_extension은 채널 밖')
                        add('IM5', e.line, '타 BC `%s`의 `%s` 참조 — 교차 BC는 4채널만(%s)' % (tbc, t, reason),
                            '제1 규약 §9-3',
                            '데이터·행위는 그 BC UseCase 호출, 표시는 view 임베드, 이동은 navigator, 타입은 entity/value_object/enum만.')

            # ---- IM6: root → BC infra 금지
            if in_root and internal and has_seg(t, 'infra_layer'):
                add('IM6', e.line, 'root에서 BC infra `%s` 참조 — root도 Model 규율(UseCase만) 적용' % t,
                    '제1 규약 §3.6', '그 BC UseCase를 호출한다.')

            # ---- IM7: VM·SharedState·Service → infra·api_client 금지
            if in_app and parent in ('view_model', 'shared_state', 'service') and internal:
                if has_seg(t, 'infra_layer') or t == API_CLIENT:
                    add('IM7', e.line, 'ViewModel 변종에서 `%s` 참조 — Model 방향은 UseCase만' % t,
                        '제1 규약 §3.3', '위임 한 줄짜리라도 UseCase를 거친다 — 관문의 일관성이 지름길의 근거가 되지 않는다.')

            # ---- IM8: section·widget·ui_extension → application_layer 금지(VM·상태 계층을 모른다)
            if in_pres and parent in ('section', 'widget', 'ui_extension') and internal and has_seg(t, 'application_layer'):
                add('IM8', e.line, '%s에서 application_layer `%s` 참조 — dumb 표현 조각은 VM·상태의 존재를 모른다' % (parent, t),
                    '제1 규약 §3.5', '값은 include 인자·필터 인자로 받는다. 상태가 필요해진 것은 승격 신호 — view+vm 쌍(삼총사)으로 승격한다.')

            # ---- IM9: widget → 화면 전속 조각(section·view) 금지
            if in_pres and parent == 'widget' and internal and has_seg(t, 'presentation_layer') \
                    and (has_seg(t, 'section') or has_seg(t, 'view')):
                add('IM9', e.line, 'widget에서 화면 전속 조각 `%s` 참조 — 재사용 부품은 화면을 모른다' % t,
                    '제1 규약 §3.5', '엔티티·원시값·href 를 include 인자로 받는다. 화면 전속이면 section으로.')

            # ---- IM10·IM21: navigator의 금지 방향
            if is_navigator and internal:
                if has_seg(t, 'presentation_layer'):
                    add('IM10', e.line, 'navigator에서 presentation `%s` 참조 — URL name만 참조' % t,
                        '제1 규약 §3.1', '`<Bc>Routes` 상수(reverse)만 쓴다 — view 참조는 순환(VM→navigator→view→VM)을 만든다.')
                elif has_seg(t, 'domain_layer') or has_seg(t, 'application_layer') or has_seg(t, 'infra_layer'):
                    add('IM21', e.line, 'navigator에서 계층 코드 `%s` 참조 — navigator는 정적 href 헬퍼일 뿐' % t,
                        '제1 규약 §3.7', 'navigator의 합법 참조는 자기 router(URL name 상수)·common·django.urls뿐.')

            # ---- IM11: application → presentation 금지
            if in_app and internal and has_seg(t, 'presentation_layer'):
                add('IM11', e.line, 'application_layer에서 presentation `%s` 참조 — 역류' % t,
                    '제1 규약 §3.7', 'UI가 필요한 결정은 State로 노출하고 view가 응답(redirect·조각)으로 소비한다.')

            # ---- IM12(import 절반): application → django 전면 금지(django.utils 예외)
            if in_app and py_ext and e.top == 'django' and not (mod == 'django.utils' or mod.startswith('django.utils.')):
                add('IM12', e.line, 'application_layer에서 `%s` import — 요청·응답·템플릿 호출 금지' % mod,
                    '제1 규약 §3.3·§3.7',
                    '요청·응답은 view로, href 는 navigator로, 표시 매핑은 ui_extension으로. django.utils(비UI 유틸)만 허용.')

            # ---- IM13: design_system 참조 화이트리스트
            if internal and t.startswith('design_system/'):
                if not (in_pres or fv.startswith('root/scaffold/') or segs[0] == 'design_system'):
                    add('IM13', e.line, '`%s` 참조 — design_system은 presentation·root scaffold·design_system 내부만' % t,
                        '제1 규약 §3.7', '시각 토큰이 필요한 로직은 ui_extension(도메인→UI 매핑의 유일한 자리)으로 옮긴다.')

            # ---- IM14(import 절반): app service → navigator 금지
            if in_app and parent == 'service' and internal and base_name_of(t).endswith('_navigator.py'):
                add('IM14', e.line, 'application service에서 navigator 참조 — 내비는 VM만',
                    '제1 규약 §3.7·§3.6', '비화면 이벤트발 화면 이동은 root_destination_handler 소유 — 진입 URL로 정규화해 디스패치한다.')

            # ---- IM15: apps.py·urls.py 역참조 금지
            if internal and t in ENTRY_FILES and segs[0] in ('application', 'common', 'design_system'):
                add('IM15', e.line, '`web/%s` 참조 — 엔트리포인트를 역참조' % t,
                    '제1 규약 §3.6', '필요한 전역 인스턴스(logger 등)는 common 소속으로 옮긴다.')

            # ---- IM16: apps.py·urls.py import 화이트리스트
            if is_entry and e.kind == 'py':
                ok_ext: bool = py_ext and (e.top in STDLIB or e.top == 'django')
                ok_int: bool = internal and t.startswith('root/')
                if not (ok_ext or ok_int):
                    add('IM16', e.line, '`web/%s` 화이트리스트 외 import `%s` — 엔트리포인트 최소형' % (f, e.uri),
                        '제1 규약 §3.6',
                        '시동은 root_initializer, 라우팅은 root_router 한 줄 — 그 외는 apps.py·urls.py의 일이 아니다.')

            # ---- IM17: presentation → infra 금지
            if in_pres and internal and has_seg(t, 'infra_layer'):
                add('IM17', e.line, 'presentation에서 infra `%s` 참조 — view→Repo 직행' % t,
                    '제1 규약 §3.7', '데이터는 VM이 UseCase로 가져와 State로 노출한다.')

            # ---- IM18: infra → application·presentation 금지
            if in_infra and internal and (has_seg(t, 'application_layer') or has_seg(t, 'presentation_layer')):
                add('IM18', e.line, 'infra에서 상위 계층 `%s` 참조 — 역류' % t,
                    '제1 규약 §3.7', 'infra는 호출당하는 쪽 — 필요한 값은 인자로 받는다.')

            # ---- IM20: use_case·state·shared_state → navigator 금지
            if in_app and parent in ('use_case', 'state', 'shared_state') and internal \
                    and base_name_of(t).endswith('_navigator.py'):
                add('IM20', e.line, '%s에서 navigator 참조 — BC 루트 호출은 VM만' % parent,
                    '제1 규약 §3.7', '화면 전환은 VM의 일 — UseCase는 Either만 반환하고 결정은 VM이 한다.')

            # ---- IM22: router 허용 목록
            if is_bc_router and internal:
                tbc = bc_of(t, ctx.areas)
                ok = t.startswith('common/') or (tbc == bc and (
                    (has_seg(t, 'presentation_layer') and has_seg(t, 'view')) or is_bc_root_path(t, ctx.areas)))
                if not ok:
                    add('IM22', e.line, 'router에서 `%s` 참조 — router는 자기 BC view(path 대상 함수)·BC 루트·common만' % t,
                        '제1 규약 §3.7·§3.1', 'section·widget은 view가 조립하고, 게이트 상태 확인은 root 쪽(UseCase 직접 생성)의 일.')

            # ---- IM23(import 절반): router·navigator → datetime 직접 import 금지(날짜 직렬화 보유 금지)
            if (is_bc_router or is_navigator) and py_ext and e.top == 'datetime':
                add('IM23', e.line, 'BC 루트(%s)에서 `%s` import — 날짜 직렬화 보유 금지' % ('router' if is_bc_router else 'navigator', mod),
                    'architecture-ddd §3.72·architecture-ui §6',
                    '날짜→path 변환은 도메인 VO 메서드(우선)·VM 변환에 단일 거주하고, router·navigator는 결과 str을 전달만 한다.')

            # ---- IM24: 상대 import 금지
            if e.kind == 'py' and e.relative:
                add('IM24', e.line, '상대 import `from %s import …` — web/ 의 import 는 `web.` 절대 경로만' % e.uri,
                    '제1 규약 §2', '`from web.<경로> import …` 로 바꾼다 — 경로 한 줄로 계층·BC가 식별되는 설계.')

            # ---- IM25: 백엔드 내부 import 금지
            if py_ext and e.top in backend:
                add('IM25', e.line, 'web에서 백엔드 내부 `%s` import — web 과 백엔드의 계약은 API(URL+JSON)뿐' % mod,
                    '제1 규약 §3.7',
                    'import를 지우고 DataSource가 api_client로 API를 부른다 — 필요한 API가 없으면 가정 계약으로 짓고 '
                    '실제 API는 /dddjango 로 요청한다.')

            # ---- IM26: extends 대상 — 페이지 템플릿은 root_view.html 만 · 조각 템플릿(section·widget·component)은
            #      design_system component 만(부품이 내놓은 block 채우기 = 위젯 slot 인자 자리) · 그 밖은 root_view.html 만
            if e.kind == 'extends':
                if is_fragment_tpl and not (is_page or is_root_gate_page):
                    ok26: bool = t.startswith(_COMPONENT_PREFIX) and t.endswith('.html')
                    want: str = 'design_system/component/**/*.html(부품의 block 채우기)'
                else:
                    ok26 = t == ROOT_VIEW_TEMPLATE
                    want = 'root_view.html 하나'
                if not ok26:
                    add('IM26', e.line, '`{%% extends %%}` 대상 `%s` — %s의 상속 대상은 %s' % (
                        t, '조각 템플릿' if is_fragment_tpl else '페이지(그 밖) 템플릿', want),
                        '제1 규약 §3.6·§5',
                        '페이지는 root_view.html 을 extends 하고, 조각은 값은 include … only 로·마크업 자리는 '
                        'design_system component 를 extends 해 block 만 채운다.')

            # ---- IM27(import 절반): HTTP 호출 표면은 common/network 전속
            if py_ext and not in_network:
                surf: Optional[str] = _http_surface(mod, e.names)
                if surf:
                    add('IM27', e.line, 'common/network 밖 HTTP 호출 표면 `%s` import' % surf,
                        '제1 규약 §3.4·§6',
                        'API 호출은 common/network/api_client.py·safe_api_call.py 하나로 — DataSource는 그것을 부른다.')

        # ================= 토큰 검사 (마스킹 본문, added 줄 게이트) =================
        if ext == '.py':
            ms = ctx.mask_of(f)
            import_lines: Set[int] = {e.line for e in ctx.edges_of(f)}

            def add_token(cid: str, line: int, msg: str, rule: str, fix: str) -> None:
                if line not in import_lines:
                    add(cid, line, msg, rule, fix)
            # IM12: 요청·응답 객체 토큰 (BuildContext 자리)
            if in_app:
                for line, _ in scan_tokens(ms, re.compile(
                        r'\bHttpRequest\b|\bHttpResponse\w*\b|\brequest\.(?:GET|POST|session|META|COOKIES|headers|user)\b')):
                    add_token('IM12', line, 'application_layer에서 요청·응답 객체 보유', '제1 규약 §3.3·§9-7',
                        'view가 요청에서 원시값을 꺼내 VM에 넘긴다 — 화면 전환은 navigator href, 에러는 State 노출.')
            # IM14: service의 내비 호출 토큰
            if in_app and parent == 'service':
                for line, _ in scan_tokens(ms, re.compile(r'\b(?:reverse|reverse_lazy|redirect)\s*\(')):
                    add_token('IM14', line, 'application service에서 내비 호출(`reverse(`·`redirect(`)', '제1 규약 §3.6',
                        '비화면 이벤트의 화면 이동은 root_destination_handler가 진입 URL로 디스패치한다.')
            # IM23(토큰 절반): router·navigator의 날짜 직렬화 토큰
            if is_bc_router or is_navigator:
                for line, _ in scan_tokens(ms, re.compile(r'\.strftime\s*\(|\.isoformat\s*\(\s*\)')):
                    add_token('IM23', line, 'BC 루트(%s)에서 날짜 직렬화(`strftime`/`isoformat`) 보유 — BC 루트는 변환을 모른다'
                        % ('router' if is_bc_router else 'navigator'),
                        'architecture-ddd §3.72·architecture-ui §6', '날짜→path 변환은 도메인 VO·VM 단일 거주, router·navigator는 str 전달만.')
        # IM27(리터럴 절반): API URL 리터럴은 DataSource·common/network 전속
        if ext != '.css' and not in_network and not (in_infra and parent == 'data_source'):
            ms = ctx.mask_of(f)
            for line, _ in scan_tokens(ms, _API_LITERAL_RE, view='no_comments'):
                add('IM27', line, 'DataSource 밖 API URL 리터럴 `/api/…`', '제1 규약 §3.4',
                    'API path 는 그 BC infra_layer/data_source/<개념>_data_source.py 에만 둔다.')
    return out
