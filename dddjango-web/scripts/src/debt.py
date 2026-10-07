# dddjango-web 빚 스캔·잔존 판정 (값 정본: discipline-houserules §8 · 커맨드 Phase 0 step 4′·G2).
# (바탕: dddjango-web v1.3.1 src/debt.py — 2.0.0 새 트리 · 새 검사 번호에 맞춤)
#
# --debt-scan: web/ 전체(git 추적 + 미추적·비무시, 작업 트리 실재 파일)를 «모두 added» 로 보고
#   ST · MD · IM · NM · PU · WV 패밀리를 돌린다(CY 순환은 베이스라인 래칫 · TG 는 테스트 추가라 동작 불변
#   정리 밖 · PJ 는 늘 검사라 빚 모드에 넣지 않는다). 게이트의 ST 폴더 발견(표준 트리 밖 옛 배치 최상위 폴더 ST0 ·
#   허용 밖 디렉터리 ST3·ST5~ST8·ST10~ST12)은 그 아래 파일마다의 키로 펼친다 — «빚 정리 = 손대는 파일 + 부르는
#   곳»이 파일 단위로 고르고 G2 잔존도 범위가 옮긴 파일만큼 줄게(ST4 골격 미비 · static/vendor/ 벤더 단위는 폴더
#   키 그대로). 펼친 행에는 `folder`(원 폴더)를 싣는다 — 잔존 판정이 같은 폴더의 범위 밖 남은 키를 보고만 한다.
#   옛 배치 파일은 층 판정 불가 레거시라 층 의존 IM 이 걸리지 않는다 — 슬라이스 0 이 새 배치로 옮긴다.
#   브라운필드 허용 규범은 빚이 아니다(_exempt). 키 = (검사, 경로).
# --debt-residual: 같은 의미론으로 다시 스캔해 refactor-scope.md 의 마지막 `## G0` 절과 그 뒤
#   재승인 절들의 ⓐ·요구 키(재상정 뺌)가 사라졌는지 센다(키 대조 — 개명 추적 없음.
#   개명·이동의 새 경로 발견은 --diff-base 게이트 몫). ⓐ·요구 키와 같은 폴더 발견에서 펼친 다른 키가 남으면
#   «범위 밖 남은 빚»으로 보고만 한다(잔존 아님).
# --debt-scan --refactor: 리팩토링 입구의 스캔 — 기존 단위의 골격 미비(ST4)도 빚이고, legacy core
#   면제는 그 root_view 로드 태그 면제가 없을 때만 걷는다(커맨드 «리팩토링 모드» · houserules §8).
#   debt-g0.json 의 mode 가 --debt-residual 의 의미론을 정한다.
# 공식 SDK 등재(WV — src/check_vendor.py `run_vendor(ctx, debt=True)`): 늘 검사 키(check_vendor.UNDEFERRABLE)는
#   발견 행에 `undeferrable: true` 를 싣는다(판정 물음 없이 미룰 수 없음).
#   debt-g0.json 의 `scanner` 검사 집합 해시·키 의미론이 지금과 다르면 판 경계라 잔존 판정 불가다(exit 1).
#   플러그인 판 글자만 다르면 알림 한 줄을 내고 잔존 판정을 잇는다.

import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .check_imports import run_imports
from .check_models import run_models
from .check_naming import run_naming
from .check_project import _is_htmx_core
from .check_purity import run_purity
from .check_structure import _skeleton, run_structure
from .check_vendor import UNDEFERRABLE, VENDOR_CHECK_IDS, VendorUndecidable, run_vendor
from .common import CORE_CHECK_IDS, ROOT_VIEW_TEMPLATE, BackstopContext, Finding
from .sdk_registry import VENDOR_DIR

SCHEMA: str = 'dddjango-web-debt/1'

# refactor-scope.md 절 머리 — 커맨드 Phase 0 기록 정형과 같은 문자열이다.
SECTION_G0: str = 'G0'
SECTION_REAPPROVAL: str = 'G0 재승인'
SECTION_STOP: str = 'G0 정지'
SECTION_RESUBMIT: str = 'ⓐ 재상정'
ROW_A: str = 'ⓐ 키'
ROW_REQUIRED: str = '요구 키'
ROW_RESUBMIT: str = '재상정 키'
ROW_M_A: str = '의미 ⓐ 키'
ROW_M_RESUBMIT: str = '의미 재상정 키'
ROW_M_AUDIT: str = '의미 audit'
MODE_FEATURE: str = 'feature'
MODE_REFACTOR: str = 'refactor'
# 명세(design-spec.md)의 슬라이스 0 절 머리와 정형 행 — design-architect-web 문면과 같은 문자열이다.
SPEC_SLICE0_HEAD: str = '## 슬라이스 0'
SPEC_ROW_PATH: str = '경로'
SPEC_ROW_NAME: str = '이름'
# 6a 참조 완전성 grep 의 pathspec — 커맨드 문면의 명령과 같은 문자열이다(refactor_audit --self-test).
REF_PATHSPEC: Tuple[str, ...] = ('web', 'web_test', '*.py', '*.html', '*.css', '*.js', ':(exclude).dddjango-web',
                                  ':(exclude)web/static/vendor', ':(exclude)web/sdk_registry.json')
# 빚 스캔이 도는 패밀리와 그 검사 집합 — 검사 집합이 다른 동결본으로는 잔존을 판정하지 않는다(scanner 지문).
DEBT_FAMILIES: Tuple[str, ...] = ('st', 'md', 'im', 'nm', 'pu')
CHECK_IDS: Tuple[str, ...] = tuple([c for c in CORE_CHECK_IDS if c[:2].lower() in DEBT_FAMILIES]
                                   + list(VENDOR_CHECK_IDS))
# 빚 키 의미론 — 폴더 발견을 파일 키로 펼친 판(이 값이 다른 동결본은 판 경계)
# 빚 키의 꼴(검사 ID·경로 표현)을 바꾸는 고침은 이 값을 올린다 — 플러그인 판 글자는 경계가 아니다
KEY_SCHEME: str = 'st-folder-to-file'
# 브라운필드 legacy htmx core(기존 설치 그대로 소비) — 신규 이름으로는 금지(PU1)
HTMX_LEGACY: Tuple[str, ...] = ('static/js/htmx.min.js', 'static/js/htmx.js')
# PU2 의 실행 순서 사유(check_purity 문면 머리) — 문면이 바뀌면 fixtures_debt.sh D3·D25 가 깨진다
PU2_ORDER_REASONS: Tuple[str, ...] = ('async 실행 금지', 'classic 외부 스크립트는 defer가 필요하다')

_HEAD_RE = re.compile(r'^## (G0 재승인|G0 정지|G0|ⓐ 재상정) '
                      r'(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?(?:[+-]\d{2}:?\d{2}|Z)?)\s*$')
_ROW_RE = re.compile(r'^(?:- )?(의미 ⓐ 키|의미 재상정 키|의미 audit|ⓐ 키|요구 키|재상정 키):'
                     r'[ \t]*(.*?)\s*$')
_ID_RE = re.compile(r'^C[1-9]\d*$')
_M_ID_RE = re.compile(r'^M[1-9]\d*$')
_AUDIT_RE = re.compile(r'^\d{8}-\d{6}$')
_SPEC_HEAD_RE = re.compile(r'^## 슬라이스 0(?:\s|$)')
_SPEC_ROW_START_RE = re.compile(r'^\s*(?:[-*] )?(경로|이름):')
_SPEC_ROW_RE = re.compile(r'^\s*(?:[-*] )?(경로|이름):\s*`?([^`\s]+)`?\s*→\s*`?([^`\s]+)`?\s*$')
_DOTTED_RE = re.compile(r'^web(\.[A-Za-z_][A-Za-z0-9_]*)+$')
_WHEN_RE = re.compile(r'^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::\d{2})?'
                      r'(Z|[+-]\d{2}:?\d{2})?$')
_FENCE_RE = re.compile(r'^\s*(```|~~~)')
_ST4_NO_BASE: str = '[info] ST4(골격 완비) 생략 — git 기준점 없음'
FIRST_RUN_NOTICE: str = '[info] web/ 없음 — 첫 실행(기존 web 코드 없음 = 빚 0)'


class DebtError(Exception):
    """실행 불능·판정 불가 — exit 1(통과가 아니다)."""


def _plugin_version() -> str:
    here: Path = Path(__file__).resolve()
    for parent in list(here.parents)[:6]:
        for manifest in (parent / '.claude-plugin' / 'plugin.json', parent / '.codex-plugin' / 'plugin.json'):
            if manifest.is_file():
                try:
                    return str(json.loads(manifest.read_text(encoding='utf-8')).get('version', 'unknown'))
                except (OSError, ValueError):
                    return 'unknown'
    return 'unknown'


def scanner_stamp() -> dict:
    """빚 스캔 판 — 플러그인 판 · 검사 집합 해시 · 키 의미론.
    경계는 검사 집합 해시·키 의미론 — 플러그인 판은 기록·알림용."""
    return {'plugin': _plugin_version(),
            'checks': hashlib.sha256(','.join(CHECK_IDS).encode('ascii')).hexdigest()[:16],
            'keys': KEY_SCHEME}


# ------------------------------------------------------------------ 스캔


def _bytecode(rel: str) -> bool:
    return '__pycache__' in rel.split('/') or rel.endswith('.pyc')


def debt_universe(root: Path) -> List[str]:
    """web/ 파일 우주(web-상대) — 무시 파일·인덱스 전용 삭제·gitlink·바이트코드 제외.
    git 이 web/ 을 못 보면(심볼릭 링크 · 비git · git 밖·무시된 폴더) 판정 불가다 — «빚 0» 이 아니다.
    web/ 이 없으면 첫 실행이다(빈 우주 — 기존 코드가 없어 빚 0). git 보다 먼저 본다 — 비git 첫 실행도 빚 0
    (G0 의 비git 진행은 web/ 없는 첫 실행에서만 성립한다 — 커맨드 Phase 0 step 1)."""
    web: Path = root / 'web'
    if web.is_symlink():
        raise DebtError('web/ 가 심볼릭 링크 — git 우주로 스캔할 수 없다(%s)' % web)
    if not web.exists():
        return []
    result = subprocess.run(['git', '-C', str(root), 'ls-files', '-co', '--exclude-standard',
                             '-z', '--', 'web/'], capture_output=True)
    if result.returncode != 0:
        raise DebtError('git ls-files 실패(git 저장소 아님?) — %s' %
                        result.stderr.decode('utf-8', 'replace').strip())
    if not web.is_dir():
        raise DebtError('web 이 폴더가 아니다 — %s' % web)
    names: Set[str] = set()
    for raw in result.stdout.decode('utf-8').split('\0'):
        if not raw.startswith('web/'):
            continue
        rel: str = raw[len('web/'):]
        if not rel or _bytecode(rel):
            continue
        if (web / rel).is_file():
            names.add(rel)
    if not names and any(p.is_file() and not _bytecode(p.relative_to(web).as_posix())
                         for p in web.rglob('*')):
        raise DebtError('git 우주가 비었는데 web/ 에 파일이 있다 — web/ 가 git 밖이거나 무시됨')
    return sorted(names)


def _legacy_tag(f: Finding) -> bool:
    """root_view 의 legacy core 로드 태그 실행 순서(async · defer) 발견인가."""
    return (f.check_id == 'PU2' and f.path == ROOT_VIEW_TEMPLATE and f.message.startswith(PU2_ORDER_REASONS)
            and f.message.rsplit(' — ', 1)[-1] in HTMX_LEGACY)


LEGACY_MESSAGE: str = '표준 트리 밖 옛 배치 파일 — 층 판정 불가 레거시(슬라이스 0 이 새 배치로 옮긴다)'


def _folder_files(findings: List[Finding], files: List[str]) -> Tuple[List[Finding], Dict[str, str]]:
    """게이트의 ST 폴더 발견(옛 배치 최상위 폴더 ST0 · 허용 밖 디렉터리)을 그 아래 파일마다의 키로 펼친다(빚 모드
    전용) — (발견, {키: 폴더}). 빚 범위(손대는 파일 + 부르는 곳)가 파일 단위로 고르고 G2 잔존도 범위가 옮긴 파일만큼
    줄게 한다(범위 밖 파일이 같은 폴더에 남아도 범위 몫의 잔존이 아니다). 펼치지 않는 것: ST4 골격 미비(생성이라
    폴더가 단위다) · static/vendor/ 의 벤더 단위(등재·제거가 폴더째 — Coordinator 소관)."""
    out: List[Finding] = []
    folder_of: Dict[str, str] = {}
    file_set: Set[str] = set(files)
    for f in findings:
        members: List[str] = []
        if f.check_id.startswith('ST') and f.check_id != 'ST4' and not (
                f.path + '/').startswith(VENDOR_DIR + '/') and f.path not in file_set:
            members = [x for x in files if x.startswith(f.path + '/')]
        if not members:
            out.append(f)
            continue
        message: str = LEGACY_MESSAGE if f.check_id == 'ST0' else '%s — 폴더 `%s/` 의 파일' % (f.message, f.path)
        for x in members:
            out.append(Finding(f.check_id, x, None, message, f.rule, f.fix))
            folder_of['%s|%s' % (f.check_id, x)] = f.path
    return out, folder_of


def _exempt(findings: List[Finding], files: List[str], refactor: bool = False) -> List[Finding]:
    """브라운필드 허용 규범은 빚이 아니다(houserules «그대로 소비» — 기존 htmx core 설치 1개).
    - PU1: 기존 legacy htmx core 설치(`static/js/htmx.min.js`·`htmx.js`) — core 설치가 하나뿐일 때만.
      리팩토링 스캔은 그 core 를 가리키는 root_view 로드 태그 면제(PU2)가 없을 때 면제를 걷는다 — 있으면
      core 를 옮긴 태그가 defer 를 요구해 동작 불변 정리가 아니므로 PU1·PU2 한 쌍을 그대로 둔다.
    - PU2: 그 core 의 root_view 로드 태그 실행 순서(async·defer) — 같은 조건. defer 를 붙이면 실행 순서가
      바뀌어 동작 불변 교정이 아니다."""
    duplicate: bool = sum(1 for f in files if _is_htmx_core(f)) > 1
    tagged: Set[str] = {f.message.rsplit(' — ', 1)[1] for f in findings if _legacy_tag(f)}
    kept: List[Finding] = []
    for f in findings:
        if (not duplicate and f.check_id == 'PU1' and f.path in HTMX_LEGACY
                and (not refactor or f.path in tagged)):
            continue
        if not duplicate and _legacy_tag(f):
            continue
        kept.append(f)
    return kept


def _is_git(root: Path) -> bool:
    return _git_out(root, ['rev-parse', '--is-inside-work-tree']) is not None


def _git_out(root: Path, args: List[str]) -> Optional[str]:
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
    return result.stdout.decode('utf-8', 'replace') if result.returncode == 0 else None


def scan(root: Path, refactor: bool = False) -> Tuple[dict, List[str]]:
    """web/ 전체 빚 스캔 — (JSON 사전, notice 목록). refactor 면 기존 단위 골격 미비도 빚이다."""
    files: List[str] = debt_universe(root)
    raw: List[Finding] = []
    notices: List[str] = []
    if not (root / 'web').exists():
        notices.append(FIRST_RUN_NOTICE)
    else:
        ctx: BackstopContext = BackstopContext.from_files(root, files)
        raw.extend(run_structure(ctx))
        if refactor:
            raw.extend(_skeleton(ctx))
        raw.extend(run_models(ctx))
        raw.extend(run_imports(ctx))
        raw.extend(run_naming(ctx))
        raw.extend(run_purity(ctx))
        try:
            raw.extend(run_vendor(ctx, debt=True))
        except VendorUndecidable as error:
            raise DebtError(str(error))
        # 빚 모드에는 기준점이 없는 것이 정상이다 — ST4 생략 사유를 빚 모드 말로 바꿔 싣는다
        # (리팩토링 스캔은 ST4 를 직접 돌렸으므로 생략 notice 를 떨군다).
        for n in ctx.notices:
            if not n.startswith(_ST4_NO_BASE):
                notices.append(n)
            elif not refactor:
                notices.append('[info] ST4(골격 완비) 빚 모드 제외 — 기존 단위의 골격 미비는 빚이 아니다'
                               '(브라운필드 허용 · 새 단위 골격은 G2 diff 게이트가 본다)')
    expanded, folder_of = _folder_files(raw, files)
    kept: List[Finding] = sorted(_exempt(expanded, files, refactor),
                                 key=lambda f: (f.check_id, f.path, f.line or 0, f.message))
    counts: Dict[str, int] = {}
    rows: List[dict] = []
    for f in kept:
        key: str = '%s|%s' % (f.check_id, f.path)
        counts[key] = counts.get(key, 0) + 1
        row: dict = {'key': key, 'check': f.check_id, 'path': f.path, 'line': f.line, 'message': f.message}
        if f.check_id in UNDEFERRABLE:
            row['undeferrable'] = True
        if key in folder_of:
            row['folder'] = folder_of[key]
        rows.append(row)
    ids: Dict[str, str] = {'C%d' % (n + 1): key for n, key in enumerate(sorted(counts))}
    head: Optional[str] = None
    status: Optional[str] = ''
    if _is_git(root):
        head = _git_out(root, ['rev-parse', '--verify', '-q', 'HEAD'])
        status = _git_out(root, ['status', '--porcelain', '-z', '--untracked-files=all',
                                 '--', '.', ':(exclude).dddjango-web'])
        if status is None:
            raise DebtError('git status 실패 — %s' % root)
    else:  # debt_universe 가 비git 을 web/ 없는 첫 실행에서만 통과시킨다
        notices.append('[info] git 저장소 아님 — web/ 없는 첫 실행이라 빚 0(head 없음 · dirty 판정 밖)')
    data: dict = {
        'schema': SCHEMA,
        'mode': MODE_REFACTOR if refactor else MODE_FEATURE,
        'scanner': scanner_stamp(),
        'head': head.strip() if head else None,
        'dirty': bool(status.strip('\0')),
        'scanned_at': datetime.now().astimezone().isoformat(timespec='seconds'),
        'files': files,
        'ids': ids,
        'findings': rows,
        'counts': counts,
    }
    return data, notices


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                    encoding='utf-8')


def _id_of(data: dict) -> Dict[str, str]:
    return {key: cid for cid, key in data['ids'].items()}


def cli_scan(root: Path, json_path: Optional[str], refactor: bool = False) -> int:
    try:
        data, notices = scan(root, refactor)
        if json_path is not None:
            write_json(Path(json_path), data)
    except (DebtError, OSError) as error:
        print('[backstop] 빚 스캔 실행 불능 — %s' % error)
        return 1
    for n in notices:
        print(n)
    by_key: Dict[str, str] = _id_of(data)
    for row in data['findings']:
        loc: str = 'web/' + row['path'] + ('' if row['line'] is None else ':%d' % row['line'])
        mark: str = ' (미룰 수 없음)' if row.get('undeferrable') else ''
        print('%s [%s]%s %s %s' % (by_key[row['key']], row['check'], mark, loc, row['message']))
    print('[backstop] 빚 스캔%s — 키 %d · 발견 %d · 스캔 파일 %d'
          % (' (리팩토링)' if refactor else '', len(data['counts']), len(data['findings']),
             len(data['files'])))
    return 2 if data['findings'] else 0


# ------------------------------------------------------------------ 잔존


def _ids_of(value: str, where: str) -> Set[str]:
    if value == '-':
        return set()
    tokens: List[str] = value.split()
    if not tokens or any(not _ID_RE.match(t) for t in tokens):
        raise DebtError('정형 행 값은 `C<n>` 공백 구분 또는 `-` 다 — %s: %r' % (where, value))
    return set(tokens)


def parse_scope(text: str) -> List[Tuple[str, str, Dict[str, List[str]]]]:
    """refactor-scope.md 의 G0 계열 절 — [(절 종류, 시각, {정형 행: [값…]})]."""
    sections: List[Tuple[str, str, Dict[str, List[str]]]] = []
    current: Optional[Dict[str, List[str]]] = None
    fenced: bool = False
    for number, line in enumerate(text.splitlines(), 1):
        if _FENCE_RE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.startswith('## '):
            current = None
            head = _HEAD_RE.match(line)
            if head:
                current = {}
                sections.append((head.group(1), head.group(2), current))
            elif line.startswith('## G0') or line.startswith('## ⓐ'):
                raise DebtError('알 수 없는 절 머리 %d행 — %r' % (number, line))
            continue
        if current is None:
            continue
        row = _ROW_RE.match(line)
        if row:
            current.setdefault(row.group(1), []).append(row.group(2))
    return sections


def _one_row(kind: str, when: str, rows: Dict[str, List[str]], name: str) -> Set[str]:
    values: List[str] = rows.get(name, [])
    if len(values) != 1:
        raise DebtError('`## %s %s` 절에 `%s:` 행이 정확히 한 번 있어야 한다(%d번)'
                        % (kind, when, name, len(values)))
    return _ids_of(values[0], '%s %s %s' % (kind, when, name))


def residual_sets(text: str) -> Tuple[str, Set[str], Set[str], Set[str]]:
    """(마지막 `## G0` 시각, ⓐ 키, 요구 키, 재상정 키) — 마지막 `## G0` 절부터 순서대로 접는다.
    G0·G0 재승인 절은 ⓐ·요구 키를 더하고(재승인 절이 앞 키를 다시 적지 않아도 빠지지 않는다),
    ⓐ 재상정 절은 뺀다(그 뒤 재승인 절이 다시 적으면 되살아난다). G0 정지 절은 판정 입력이 아니다."""
    sections = parse_scope(text)
    starts: List[int] = [i for i, (kind, _w, _r) in enumerate(sections) if kind == SECTION_G0]
    if not starts:
        raise DebtError('refactor-scope.md 에 `## G0 <시각>` 절 없음')
    first_when: str = sections[starts[-1]][1]
    a_keys: Set[str] = set()
    required: Set[str] = set()
    resubmitted: Set[str] = set()
    for kind, when, rows in sections[starts[-1]:]:
        if kind in (SECTION_G0, SECTION_REAPPROVAL):
            added_a: Set[str] = _one_row(kind, when, rows, ROW_A)
            added_r: Set[str] = _one_row(kind, when, rows, ROW_REQUIRED)
            a_keys |= added_a
            required |= added_r
            resubmitted -= added_a | added_r
        elif kind == SECTION_RESUBMIT:
            resubmitted |= _one_row(kind, when, rows, ROW_RESUBMIT)
    return first_when, a_keys, required, resubmitted


def _m_ids_of(value: str, where: str) -> Set[str]:
    if value == '-':
        return set()
    tokens: List[str] = value.split()
    if not tokens or any(not _M_ID_RE.match(t) for t in tokens):
        raise DebtError('의미 정형 행 값은 `M<n>` 공백 구분 또는 `-` 다 — %s: %r' % (where, value))
    return set(tokens)


def _at_most_one(kind: str, when: str, rows: Dict[str, List[str]], name: str) -> Set[str]:
    values: List[str] = rows.get(name, [])
    if len(values) > 1:
        raise DebtError('`## %s %s` 절에 `%s:` 행이 두 번 이상 있다' % (kind, when, name))
    return _m_ids_of(values[0], '%s %s %s' % (kind, when, name)) if values else set()


def residual_m_sets(text: str) -> Tuple[str, str, Set[str], Set[str]]:
    """(마지막 `## G0` 시각, 의미 audit, 의미 ⓐ 키, 의미 재상정 키) — 리팩토링 모드의 M 항목 접기.
    C 접기(residual_sets)와 같은 순서다. 마지막 `## G0` 절에는 `의미 ⓐ 키:`·`의미 audit:` 가 정확히
    1행씩 있어야 한다(의미 행이 없다고 M 0 으로 읽지 않는다). 재승인 절의 `의미 ⓐ 키:` 는 0·1행,
    재상정 절의 `의미 재상정 키:` 도 0·1행이다. 값 검사는 접는 절에서만 한다."""
    sections = parse_scope(text)
    starts: List[int] = [i for i, (kind, _w, _r) in enumerate(sections) if kind == SECTION_G0]
    if not starts:
        raise DebtError('refactor-scope.md 에 `## G0 <시각>` 절 없음')
    kind0, when0, rows0 = sections[starts[-1]]
    audits: List[str] = rows0.get(ROW_M_AUDIT, [])
    if len(audits) != 1 or not _AUDIT_RE.match(audits[0]):
        raise DebtError('`## G0 %s` 절에 `%s: <YYYYMMDD-HHMMSS>` 행이 정확히 한 번 있어야 한다(%r)'
                        % (when0, ROW_M_AUDIT, audits))
    if len(rows0.get(ROW_M_A, [])) != 1:
        raise DebtError('`## G0 %s` 절에 `%s:` 행이 정확히 한 번 있어야 한다' % (when0, ROW_M_A))
    m_keys: Set[str] = set()
    resubmitted: Set[str] = set()
    for kind, when, rows in sections[starts[-1]:]:
        if kind in (SECTION_G0, SECTION_REAPPROVAL):
            added: Set[str] = _at_most_one(kind, when, rows, ROW_M_A)
            m_keys |= added
            resubmitted -= added
        elif kind == SECTION_RESUBMIT:
            resubmitted |= _at_most_one(kind, when, rows, ROW_M_RESUBMIT)
    return when0, audits[0], m_keys, resubmitted


def _local_minute(when: str) -> datetime:
    """절 머리·scanned_at 시각 → 분 단위 로컬 시각(오프셋이 있으면 로컬로 바꾼다)."""
    m = _WHEN_RE.match(when)
    if not m:
        raise DebtError('시각 형식 오류 — %r' % when)
    stamp: datetime = datetime(*(int(g) for g in m.groups()[:5]))
    offset: Optional[str] = m.group(6)
    if offset:
        spec: str = '+0000' if offset == 'Z' else offset.replace(':', '')
        stamp = datetime.strptime(stamp.strftime('%Y-%m-%d %H:%M') + spec,
                                  '%Y-%m-%d %H:%M%z').astimezone().replace(tzinfo=None)
    return stamp


def cli_residual(root: Path, folder_arg: str) -> int:
    folder: Path = Path(folder_arg).resolve()
    records: Path = (root / '.dddjango-web').resolve()
    if not folder.is_relative_to(records) or folder == records or not folder.is_dir():
        print('[backstop] 빚 잔존 판정 불가 — 폴더는 %s/ 아래의 실재 폴더여야 한다: %s'
              % (records, folder_arg))
        return 1
    scope_md: Path = folder / 'refactor-scope.md'
    g0_json: Path = folder / 'debt-g0.json'
    if not scope_md.exists() and not g0_json.exists():
        print('[info] 잔존 판정 해당 없음(규칙 이전 G0) — refactor-scope.md·debt-g0.json 둘 다 없음')
        print('[backstop] 빚 잔존 — 해당 없음')
        return 0
    try:
        if not scope_md.is_file():
            raise DebtError('debt-g0.json 은 있는데 refactor-scope.md 가 없음(G0 절 기록 누락)')
        if not g0_json.is_file():
            raise DebtError('refactor-scope.md 는 있는데 debt-g0.json 이 없음')
        try:
            g0: dict = json.loads(g0_json.read_text(encoding='utf-8'))
            ids: Dict[str, str] = dict(g0['ids'])
            g0_keys: Set[str] = set(g0['counts'])
            mode: str = g0.get('mode', MODE_FEATURE)
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            raise DebtError('debt-g0.json 파싱 실패 — %s' % error)
        if mode not in (MODE_FEATURE, MODE_REFACTOR):
            raise DebtError('debt-g0.json mode 값 오류 — %r' % mode)
        scanner = g0.get('scanner')
        stamp: dict = scanner_stamp()
        if (not isinstance(scanner, dict) or scanner.get('checks') != stamp['checks']
                or scanner.get('keys') != stamp['keys']):
            raise DebtError('판 경계 — G0 재스캔 필요(debt-g0.json 스캔 판 %r ≠ 지금 %r)'
                            % (scanner, stamp))
        notice: str = ''
        if scanner.get('plugin') != stamp['plugin']:
            notice = ('[info] 플러그인 판 바뀜 — G0 스캔 %s → 지금 %s'
                      '(검사 집합·키 의미론이 같아 잔존 판정을 잇는다)'
                      % (scanner.get('plugin', 'unknown'), stamp['plugin']))
        g0_when, a_ids, required_ids, resubmit_ids = residual_sets(
            scope_md.read_text(encoding='utf-8'))
        scanned: str = str(g0.get('scanned_at', ''))
        if _local_minute(g0_when) < _local_minute(scanned):
            raise DebtError('마지막 `## G0 %s` 절이 debt-g0.json 스캔(%s)보다 이르다 — '
                            '이번 요청의 G0 절 없음' % (g0_when, scanned))
        unknown: List[str] = sorted((a_ids | required_ids | resubmit_ids) - set(ids),
                                    key=lambda c: int(c[1:]))
        if unknown:
            raise DebtError('debt-g0.json ids 에 없는 ID — %s' % ' '.join(unknown))
        if not (a_ids | required_ids) - resubmit_ids and not _is_git(root):
            # 비git 첫 실행(G0 빚 0)의 G2 — 판정할 키가 없고 비git 이라 재스캔할 우주가 없다
            if notice:
                print(notice)
            print('[info] git 저장소 아님 — 판정할 ⓐ·요구 키 0 이라 재스캔 생략(G0 첫 실행 · 새 키 보고 없음)')
            print('[backstop] 빚 잔존 — ⓐ 잔존 0 · 요구 잔존 0 · 재상정 제외 %d · G0 에 없던 키 판정 밖(비git)'
                  % len((a_ids | required_ids) & resubmit_ids))
            return 0
        g2, _notices = scan(root, mode == MODE_REFACTOR)
        write_json(folder / 'debt-g2.json', g2)
    except (DebtError, OSError) as error:
        print('[backstop] 빚 잔존 판정 불가 — %s' % error)
        return 1
    counts: Dict[str, int] = g2['counts']
    a_live: List[str] = sorted(a_ids - resubmit_ids, key=lambda c: int(c[1:]))
    r_live: List[str] = sorted(required_ids - a_ids - resubmit_ids, key=lambda c: int(c[1:]))
    excluded: int = len((a_ids | required_ids) & resubmit_ids)
    remaining_a: List[str] = [c for c in a_live if counts.get(ids[c], 0) > 0]
    remaining_r: List[str] = [c for c in r_live if counts.get(ids[c], 0) > 0]
    new_keys: List[str] = sorted(set(counts) - g0_keys)
    outside: Dict[str, List[str]] = _outside_left(g0, g2, {ids[c] for c in a_live + r_live})
    if notice:
        print(notice)
    for label, rows in (('ⓐ', remaining_a), ('요구', remaining_r)):
        for cid in rows:
            print('잔존 %s %s %s — 발견 %d' % (label, cid, ids[cid], counts[ids[cid]]))
    for key in new_keys:
        print('[info] G0 에 없던 키 %s — 발견 %d(보고만)' % (key, counts[key]))
    for folder, keys in sorted(outside.items()):
        print('[info] 범위 밖 남은 빚 — 폴더 `%s/` 키 %d(이번 ⓐ·요구 키와 같은 폴더 발견 · 범위 밖 파일 — 보고만): %s%s'
              % (folder, len(keys), ' '.join(keys[:5]), ' 외 %d' % (len(keys) - 5) if len(keys) > 5 else ''))
    print('[backstop] 빚 잔존 — ⓐ 잔존 %d · 요구 잔존 %d · 재상정 제외 %d · G0 에 없던 키 %d · 범위 밖 남은 빚 %d'
          % (len(remaining_a), len(remaining_r), excluded, len(new_keys), sum(len(k) for k in outside.values())))
    return 0 if not remaining_a and not remaining_r else 2


def _outside_left(g0: dict, g2: dict, judged: Set[str]) -> Dict[str, List[str]]:
    """판정 키(ⓐ·요구)와 같은 폴더 발견에서 펼친 G0 키 가운데 판정 밖인데 G2 에 남은 것 — {폴더: [키…]}.
    폴더 발견의 범위 밖 파일 몫이다(잔존이 아니다 — 보고만)."""
    folder_of: Dict[str, str] = {r['key']: r['folder'] for r in g0.get('findings', [])
                                 if isinstance(r, dict) and r.get('folder') and r.get('key')}
    folders: Set[str] = {folder_of[k] for k in judged if k in folder_of}
    left: Dict[str, List[str]] = {}
    for key in sorted(set(g2['counts']) & set(folder_of)):
        if key not in judged and folder_of[key] in folders:
            left.setdefault(folder_of[key], []).append(key)
    return left


# ------------------------------------------------------------------ 명세 정형 행 · 참조 grep


def parse_spec_pairs(text: str, require: bool = False) -> Tuple[List[Tuple[str, str]],
                                                                 List[Tuple[str, str]]]:
    """design-spec.md 의 `## 슬라이스 0` 절 안 정형 행 — (경로 쌍, 이름 쌍).
    경로: `<옛> → <새>`(web 기준 상대 · 폴더면 `/` 로 끝) · 이름: `<옛 모듈>.<옛 이름> → <새 …>`
    (`web.` 으로 시작하는 전체 점 경로). 절 밖 줄과 코드 울타리 안 줄은 읽지 않는다.
    절 안 형식 어긋남 · 절 머리 2개 이상 · (require 일 때) 절 머리 0개는 판정 불가다."""
    heads: int = 0
    inside: bool = False
    fenced: bool = False
    paths: List[Tuple[str, str]] = []
    names: List[Tuple[str, str]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if _FENCE_RE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.startswith('#') and not line.startswith('###'):
            inside = bool(_SPEC_HEAD_RE.match(line))
            heads += inside
            continue
        if not inside or not _SPEC_ROW_START_RE.match(line):
            continue
        row = _SPEC_ROW_RE.match(line)
        if not row:
            raise DebtError('슬라이스 0 절 정형 행 형식 오류 %d행 — %r' % (number, line))
        kind, old, new = row.groups()
        if kind == SPEC_ROW_NAME:
            if not (_DOTTED_RE.match(old) and _DOTTED_RE.match(new)):
                raise DebtError('`이름:` 은 web. 으로 시작하는 전체 점 경로 쌍이다 %d행 — %r'
                                % (number, line))
            names.append((old, new))
        else:
            for value in (old, new):
                if value.startswith(('/', 'web/')) or '..' in value.split('/'):
                    raise DebtError('`경로:` 는 web 기준 상대 경로다 %d행 — %r' % (number, line))
            if old.endswith('/') != new.endswith('/'):
                raise DebtError('`경로:` 쌍의 폴더·파일 모양이 다르다 %d행 — %r' % (number, line))
            paths.append((old, new))
    if heads > 1:
        raise DebtError('`%s` 절 머리가 %d개다' % (SPEC_SLICE0_HEAD, heads))
    if require and heads == 0:
        raise DebtError('명세에 `%s` 절이 없다' % SPEC_SLICE0_HEAD)
    return paths, names


def module_of(rel: str) -> Optional[str]:
    """web 기준 상대 .py 경로 → `web.` 으로 시작하는 전체 모듈 점 경로(패키지는 __init__ 을 뗀다)."""
    if not rel.endswith('.py'):
        return None
    dotted: str = 'web.' + rel[:-3].replace('/', '.')
    return dotted[:-len('.__init__')] if dotted.endswith('.__init__') else dotted


def tail_of(rel: str) -> List[str]:
    """6a 참조 완전성 꼬리 — web 기준 상대 경로에서 `static/` 접두를 뗀 것(+ .py 면 전체 점 경로)."""
    tail: str = rel[len('static/'):] if rel.startswith('static/') else rel
    dotted: Optional[str] = module_of(rel)
    return [tail] + ([dotted] if dotted else [])


def reference_lines(root: Path, needles: List[str], word: bool = False,
                    paths: Optional[List[str]] = None) -> List[Tuple[str, int, str]]:
    """6a 참조 완전성 grep 적중 — [(저장소 상대 경로, 행, 줄)]. 미추적·비무시 파일도 본다.
    word 면 `-w`(점 경로의 성분 경계 — `web.a.q` 가 `web.a.q2` 를 잡지 않는다)."""
    if not needles:
        return []
    cmd: List[str] = ['git', '-C', str(root), '-c', 'core.quotePath=false', 'grep', '--untracked', '-I',
                      '-n', '-F']
    if word:
        cmd.append('-w')
    for needle in needles:
        cmd += ['-e', needle]
    cmd += ['--', *(paths if paths is not None else REF_PATHSPEC)]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode == 1:
        return []
    if result.returncode != 0:
        raise DebtError('git grep 실패 — %s' % result.stderr.decode('utf-8', 'replace').strip())
    hits: List[Tuple[str, int, str]] = []
    for raw in result.stdout.decode('utf-8', 'replace').splitlines():
        path, line, text = raw.split(':', 2)
        hits.append((path, int(line), text))
    return hits


def is_test_path(path: str) -> bool:
    """테스트 파일 판정(경로 성분 test·tests·web_test · test_*.py · *_test.py · conftest.py — dddjango
    behavior_guard 의 판별과 다르다) — 저장소 상대 경로. web_test/ 는 2.0.0 영구 테스트 뿌리(web/ 미러)다."""
    parts: List[str] = path.split('/')
    name: str = parts[-1]
    return (any(p in ('test', 'tests', 'web_test') for p in parts[:-1]) or name == 'conftest.py'
            or (name.endswith('.py') and (name.startswith('test_') or name.endswith('_test.py'))))
