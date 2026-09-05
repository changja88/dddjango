# WS — 구조·골격 8종 (값 정본: discipline-web-houserules §1 트리 v3.1·§2 성장·§3 골격).
# 게이트: added 파일·added 디렉터리, WS5(골격 완비)만 신규 단위.
#
# *왜 결정적 백스톱인가*: 트리의 형태(어떤 폴더·어떤 직속 파일이 합법인가)는
# houserules §1~§3이 전수 화이트리스트로 정의한다 — LLM 판단이 0인 영역이며,
# 위반은 항상 "규약 밖 경로의 존재"라는 기계적 사실이다. (판형: dddart check_structure)

from typing import List, Optional, Set

from .common import (
    HTMX_ALLOWED, JUNK_GROUPS, KIND_DIRS, MARKER_FILES, PY_KIND_DIRS,
    RESERVED_NAMES, STATIC_DIRS, WEB_TOP_FILES, BackstopContext, Finding,
    base_name_of, segs_of,
)


def run_structure(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    added_files: List[str] = [f for f in ctx.files if ctx.is_added(f)]
    added_dirs: List[str] = sorted(d for d in ctx.dirs if ctx.is_added_dir(d))

    # ---- WS1: web/ 직속 화이트리스트 (§1 — urls.py·apps.py·마커만)
    for f in added_files:
        if '/' not in f and f not in WEB_TOP_FILES and f not in MARKER_FILES:
            out.append(Finding('WS1', f, None,
                'web/ 직속 허용 외 파일 — 허용: urls.py·apps.py(마커 파일 예외)',
                '내용의 정체대로 재배치한다 — 화면 코드는 <영역>/<화면>/ 종류 폴더로, '
                '계약 소비는 client/<bc>/로, 시각 자산은 design_system/·static/으로.', '§1'))

    # ---- WS2: 영역 직속 — urls.py·widget/·화면 개념 폴더만 (§1)
    for f in added_files:
        s: List[str] = segs_of(f)
        if len(s) == 2 and s[0] in ctx.areas and s[1] != 'urls.py' and s[1] not in MARKER_FILES:
            out.append(Finding('WS2', f, None,
                '영역 `%s/` 직속 허용 외 파일 — 직속은 urls.py뿐(마커 파일 예외)' % s[0],
                '화면 파일이면 화면 개념 폴더 `%s/<화면>/` 종류 폴더 안으로, '
                '재사용 조각이면 widget/으로 옮긴다.' % s[0], '§1'))

    # ---- WS3: 화면 개념 — 종류 폴더(view·view_model·state·form·section) 밖 금지 (§1·§2)
    for d in added_dirs:
        s = segs_of(d)
        if len(s) == 3 and s[0] in ctx.areas and s[1] != 'widget' and s[2] not in KIND_DIRS:
            out.append(Finding('WS3', d + '/', None,
                '화면 개념 `%s/` 하위 허용 외 디렉터리 `%s/` — 종류 5폴더'
                '(view·view_model·state·form·section)만' % (s[1], s[2]),
                '종류 폴더 표기로 교정하거나, 다른 화면 개념이면 새 `<화면>/` 폴더로 분리한다.', '§1'))
        if len(s) == 4 and s[0] in ctx.areas and s[1] != 'widget' and s[2] in KIND_DIRS:
            out.append(Finding('WS3', d + '/', None,
                '종류 폴더 `%s/` 내부 디렉터리 `%s/` — 종류 폴더는 평면이다' % (s[2], s[3]),
                '하위 폴더 없이 종류 폴더 직속 파일로 둔다 — 개념이 갈리면 새 `<화면>/` 폴더다.', '§1'))
    for f in added_files:
        s = segs_of(f)
        if (len(s) == 3 and s[0] in ctx.areas and s[1] != 'widget'
                and s[2] not in MARKER_FILES and (s[0] + '/' + s[1]) in ctx.dirs):
            out.append(Finding('WS3', f, None,
                '화면 개념 `%s/` 직속 파일 — 파일은 종류 폴더 안에만 둔다(마커 파일 예외)' % s[1],
                'view/·view_model/·state/·form/·section/ 중 정체에 맞는 폴더로 옮긴다.', '§1'))

    # ---- WS4: design_system 2칸 — foundation/·component/<부품군>/·직속 파일 금지 (§1·§3)
    for f in added_files:
        s = segs_of(f)
        if s[0] != 'design_system':
            continue
        if len(s) == 2 and s[1] not in MARKER_FILES:
            out.append(Finding('WS4', f, None,
                'design_system/ 직속 파일 금지 — foundation·component 2칸만',
                '토큰이면 foundation/tokens.css로, 부품이면 component/<부품군>/으로.', '§1'))
        if (len(s) == 3 and s[1] == 'foundation'
                and s[2] not in ('tokens.css', 'motion.css') and s[2] not in MARKER_FILES):
            out.append(Finding('WS4', f, None,
                'foundation 표준은 tokens.css·motion.css 두 파일 — 시각 값·공용 모션의 단일 출처 보호',
                '새 토큰은 tokens.css의 커스텀 프로퍼티로, 공용 keyframes·모션 유틸은 motion.css로 '
                '합친다(파일 증설은 규약 개정이 먼저).', '§4'))
        if len(s) == 3 and s[1] == 'component' and s[2] not in MARKER_FILES:
            out.append(Finding('WS4', f, None,
                'component/ 직속 파일 금지 — 부품군 1차',
                '부품군 폴더(button/·card/ 류)를 만들어 그 안으로 옮긴다.', '§1'))
    for d in added_dirs:
        s = segs_of(d)
        if s[0] != 'design_system':
            continue
        if len(s) == 2 and s[1] not in ('foundation', 'component'):
            out.append(Finding('WS4', d + '/', None,
                'design_system 직속 허용 외 디렉터리 `%s/` — foundation·component 2칸 시작'
                '(theme/·util/은 만들지 않는 칸)' % s[1],
                '실수요 전 증설 금지 — 토큰은 foundation/, 부품은 component/<부품군>/으로.', '§3'))
        if len(s) == 3 and s[1] == 'component' and s[2] in JUNK_GROUPS:
            out.append(Finding('WS4', d + '/', None,
                'component/ 정크드로어 군 `%s/` 금지' % s[2],
                '분류 안 되는 부품은 정크드로어가 아니라 새 부품군 폴더를 만든다.', '§4'))
        if len(s) == 3 and s[1] == 'foundation':
            out.append(Finding('WS4', d + '/', None,
                'foundation/ 하위 디렉터리 `%s/` — foundation은 평면(tokens.css·motion.css)' % s[2],
                '토큰은 tokens.css 하나로 합친다.', '§1'))
        if len(s) == 4 and s[1] == 'component':
            out.append(Finding('WS4', d + '/', None,
                '부품군 `%s/` 내부 디렉터리 `%s/` — 부품군은 평면이다' % (s[2], s[3]),
                '변형은 파일명 수식으로(`primary_button.html` 류) — 하위 폴더를 파지 않는다.', '§1'))

    # ---- WS6: static/ 직속은 css/·js/·images/와 조건부 fonts/·files/ (§1·§3)
    for f in added_files:
        s = segs_of(f)
        if len(s) == 2 and s[0] == 'static' and s[1] not in MARKER_FILES:
            out.append(Finding('WS6', f, None,
                'static/ 직속 파일 금지 — css/·js/·images/·fonts/·files/만(무네임스페이스 경로 금지)',
                '정체에 맞는 칸(css/·js/·images/·fonts/·files/)으로 옮긴다.', '§1'))
    for d in added_dirs:
        s = segs_of(d)
        if len(s) == 2 and s[0] == 'static' and s[1] not in STATIC_DIRS:
            out.append(Finding('WS6', d + '/', None,
                'static/ 직속 허용 외 디렉터리 `%s/` — css/·js/·images/·fonts/·files/만' % s[1],
                '폰트는 fonts/, 다운로드 파일은 files/에 필요할 때만 둔다 — 임의 칸을 신설하지 않는다.', '§1'))

    # ---- WS7: 영역·화면 이름 deny — 컨테이너명·종류명 금지 (§1)
    for d in added_dirs:
        s = segs_of(d)
        if len(s) == 1 and s[0] in ctx.areas and s[0] in RESERVED_NAMES:
            out.append(Finding('WS7', d + '/', None,
                '영역 이름 `%s/` — 컨테이너명·종류명은 영역 이름으로 금지(경로 판별 오염)' % s[0],
                '내비게이션 어휘로 개명한다 — 컨테이너·종류명은 트리의 예약어다.', '§1'))
        if (len(s) == 2 and s[0] in ctx.areas and s[1] != 'widget'
                and s[1] in RESERVED_NAMES):
            out.append(Finding('WS7', d + '/', None,
                '화면 개념 이름 `%s/` — 컨테이너명·종류명은 화면 이름으로 금지' % s[1],
                '화면 어휘(`order_list` 류)로 개명한다.', '§1'))

    # ---- WS8: client 컨테이너 형태 — BC 1차·<bc> 직속 dirs=response/만 (§1·§2)
    for f in added_files:
        s = segs_of(f)
        if len(s) == 2 and s[0] == 'client' and s[1] not in MARKER_FILES:
            out.append(Finding('WS8', f, None,
                'client/ 직속 파일 금지 — BC 1차(client/<bounded_context>/)',
                '계약을 제공하는 백엔드 BC 폴더를 만들어 그 안의 `<capability>_client.py`로.', '§1'))
    for d in added_dirs:
        s = segs_of(d)
        if len(s) == 3 and s[0] == 'client' and s[2] != 'response':
            out.append(Finding('WS8', d + '/', None,
                'client BC `%s/` 직속 허용 외 디렉터리 `%s/` — 허용은 response/뿐' % (s[1], s[2]),
                'capability가 늘면 폴더가 아니라 `<capability>_client.py` 파일이 는다.', '§2'))
        if len(s) == 4 and s[0] == 'client' and s[2] == 'response':
            out.append(Finding('WS8', d + '/', None,
                'response/ 내부 디렉터리 `%s/` — response는 평면이다' % s[3],
                '응답 모델은 response/ 직속 `<response>_response.py`로만 둔다.', '§1'))

    # ---- WS5: 신규 단위 골격 완비 (§3 — 영역·화면 개념·client BC·web 컨테이너 최초)
    if not ctx.can_detect_new_units:
        ctx.notices.append('[info] WS5(골격 완비) 생략 — git 기준점 없음(신규 단위 판별 불가, houserules §7)')
    else:
        out.extend(_skeleton(ctx))

    return out


# ---------------------------------------------------------------- WS5 구현


def _skeleton(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []

    def dir_empty(d: str) -> bool:
        prefix: str = d + '/'
        return not any(f.startswith(prefix) for f in ctx.files_set)

    def need_dir(d: str, missing: List[str], label: str) -> None:
        """폴더 존재 + 비면 마커(__init__.py/.gitkeep) — «폴더는 무조건, 코드는 필요할 때만»."""
        if d not in ctx.dirs:
            missing.append(label + '/')
            return
        base: str = base_name_of(d)
        marker: str = '__init__.py' if base in PY_KIND_DIRS or base == 'response' else '.gitkeep'
        if dir_empty(d):
            missing.append('%s/%s (빈 폴더 유지)' % (label, marker))

    def report(unit_path: str, unit_desc: str, missing: List[str], section: str) -> None:
        if missing:
            out.append(Finding('WS5', unit_path, None,
                '%s 골격 미완비 — 누락: %s' % (unit_desc, ', '.join(missing)),
                '비어 있어도 표준 폴더 전부+마커 파일을 생성한다 — 폴더는 무조건, 코드는 필요할 때만.',
                section))

    # web/ 컨테이너 최초 (§3 표 1행)
    if ctx.is_added_dir(''):
        missing: List[str] = []
        for rf in ('urls.py', 'apps.py', 'base/base.html', 'design_system/foundation/tokens.css',
                   'design_system/foundation/motion.css'):
            if rf not in ctx.files_set:
                missing.append(rf)
        need_dir('design_system/component', missing, 'design_system/component')
        for sd in ('static/css', 'static/images'):
            need_dir(sd, missing, sd)
        if 'static/js' not in ctx.dirs:
            missing.append('static/js/')
        elif not any(f in ctx.files_set for f in HTMX_ALLOWED):
            missing.append('static/js/htmx.min.js (vendored htmx)')
        report('', '신규 web/ 컨테이너', missing, '§3')

    # 신규 영역 (§3 표 2행 — urls.py + widget/)
    for a in sorted(ctx.areas):
        if not ctx.is_added_dir(a):
            continue
        missing = []
        if (a + '/urls.py') not in ctx.files_set:
            missing.append('urls.py')
        need_dir(a + '/widget', missing, 'widget')
        report(a + '/', '신규 영역 `%s`' % a, missing, '§3')

    # 신규 화면 개념 (§3 표 3행 — 종류 4폴더, form은 조건 생성이라 비대상)
    for d in sorted(ctx.dirs):
        s: List[str] = segs_of(d)
        if len(s) != 2 or s[0] not in ctx.areas or s[1] == 'widget':
            continue
        if s[1] in KIND_DIRS or not ctx.is_added_dir(d):
            continue
        missing = []
        for k in ('view', 'view_model', 'state', 'section'):
            need_dir(d + '/' + k, missing, k)
        report(d + '/', '신규 화면 개념 `%s`' % s[1], missing, '§3')

    # 신규 client BC (§3 표 4행 — <capability>_client.py + response/, exception.py 비대상)
    for d in sorted(ctx.dirs):
        s = segs_of(d)
        if len(s) != 2 or s[0] != 'client' or not ctx.is_added_dir(d):
            continue
        missing = []
        prefix: str = d + '/'
        if not any(f.startswith(prefix) and f.count('/') == 2 and f.endswith('_client.py')
                   for f in ctx.files_set):
            missing.append('<capability>_client.py')
        need_dir(d + '/response', missing, 'response')
        report(d + '/', '신규 client BC `%s`' % s[1], missing, '§3')

    return out
