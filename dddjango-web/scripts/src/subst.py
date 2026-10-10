# dddjango-web 치환 확인 (값 정본: 커맨드 «슬라이스 0 호출» 끝 green ④ · houserules §8).
# (바탕: dddjango-web v1.3.1 src/subst.py — 트리와 무관한 git 대조라 그대로 · 테스트 판정은 debt.is_test_path[web_test 포함])
#
# --subst-check <기준> <대상> [--names <design-spec.md>] [--except <경로>]…: 기준..대상 사이의 web/ 밖
#   변경이 테스트 파일의 옛 경로·옛 이름 → 새 경로·새 이름 치환뿐인지 본다. 쌍은 web/ 개명(git diff -M
#   — 누적 1회와 구간 안 커밋별 개명 사슬) · 옛 폴더 전체 이동 · 명세 `## 슬라이스 0` 절의 `이름:` 행에서
#   만든다. static 접두(`web/static/` — 정적 식별자로는 `web/…`)를 건너는 이동(`static/…` ↔ `design_system/…` 등)은 꼬리
#   하나로 못 받으므로 쌍을 둘로 가른다 — static 식별자 쌍(`{% static %}`·`static(...)` 인자와 `/static/…` URL 의 꼴)과
#   저장소 파일 경로 쌍(`web/…` 로 시작하는 문자열의 꼴). 같은 쪽 안 이동은 꼬리 쌍 하나 그대로다.
#   사슬 쌍은 옛 경로가 기준에만 · 새 경로가 대상에만 있을 때만 쓰고, 구간 안에서 새로 생긴
#   경로(A · 뿌리 커밋이 들인 경로 포함)는 계보를 끊는다. 사슬은 첫 부모 줄기만 본다. 쌍이 없는(fail-closed)
#   한계 셋: 곁가지 안에서 개명과 대폭 교체를 함께 한 뒤 머지 · 한 커밋 안에서 개명과 대폭 교정을 함께 함 ·
#   개명된 경로를 한 커밋이 지우고 뒤 커밋이 다시 만듦(트리는 개명+제자리 교체와 같아도). .py 의 import 는 원문을
#   바인딩으로 펼친 뒤 대상 쪽에 쌍을 거꾸로 적용해 블록·위치별 다중집합으로 대조하고, import 밖은
#   대상 원문을 거꾸로 치환해 ast 로 대조한다. 그 밖 파일은 바뀐 줄의 다중집합으로 대조한다.
#   대조 대상은 기준..대상 첫 부모 사슬의 레인 편집이다(--build <산출물 폴더> 가 재료를 준다).
#   · 승인 병합: 산출물 폴더 `approved-merges.txt`(발주자 소유 · `<SHA> [메모]` · `//` 주석 — dddjango
#     approved-merges 와 같은 뜻)에 적힌 첫 부모 사슬 위 두 부모 병합만 상류다. 상류가 바꾼 경로의 기준은 마지막
#     그 병합의 둘째 부모 판(상류 판)이고, 병합이 상류 판과 다르게 만든 몫(끼운 편집 · 충돌 해소 · 상류 변경 버림)은
#     레인 편집이다. 목록 밖 병합은 들여온 변경 전부가 레인 편집이고, 병합마다 한 줄(등재 먼저 — 되돌려도 남는다)과
#     들인 비테스트의 «승인 목록 밖 병합 유입» 줄을 낸다. 얕은 이력 · 공통 조상 없는 승인 병합 · --build 인데 기준이
#     첫 부모 사슬 밖이면 판정 불가.
#   · 커밋 가름: build-state.json 슬라이스의 `commit`·`commits`(7~40 hex · 기준..대상 첫 부모 사슬 위 비병합
#     커밋만 받는다). slices[0] · `slice-0` 이름 기록과 기록 없는 커밋 · 목록 밖 병합은 슬라이스 0 으로 대조하고,
#     나머지 슬라이스 기록만 기능 슬라이스 커밋이다(`mode: refactor` 면 모든 기록이 슬라이스 0). 양쪽 기록은 어긋남 ·
#     slices[0] 기록이 없으면 판정 불가.
#   · web_test/ 미러 테스트 이동: SUT 개명과 같은 경로 대응(미러 경로 쌍 · 같은 디렉터리 이동)으로 옮긴 테스트는
#     옛 경로 판 → 새 경로 판을 한 구간으로 대조한다(내용은 참조 치환뿐 · 두 경로 걸음이 슬라이스 0 대조 커밋뿐일 때).
#   · 테스트 파일: 슬라이스 0 대조 걸음이 잇단 구간마다 치환만 허용한다(앞선 기능 편집을 잇지 않는 승인 병합 안
#     몫도 이 구간을 연다). 기능 슬라이스 커밋과 그 뒤 승인 병합 안 몫이 바꾼 테스트 파일은 목록으로 낸다(G2 배너).
#     (--build 없이) 기준이 첫 부모 사슬 밖이라 사슬에 걸음이 없는 경로는 기준 판 → 대상 판 한 구간으로 대조한다.
#   · 비테스트 파일은 상류 판 대비 바뀌면 누가 바꿨든 어긋남이다. 최상위 docs/ · .dddjango/ · 저장소 루트의
#     `.md` 문서만 대조하지 않는다(루트 CLAUDE.md · AGENTS.md 는 대조). 어긋남마다 그 경로를 바꾼 커밋 약칭과
#     출처 표지를 붙인다.
#   · 메서드 이동(명세 `## 슬라이스 0` 절 `메서드 이동:` 행 — 꼴이 어긋난 줄은 읽지 않는다): 행이 적은 시험 함수 안의
#     그 메서드 자리만 양쪽 판에서 같은 표지로 바꾼 뒤 지금처럼 대조한다(자리 = `R(...).m(...)` · `R.m` · 검증된 patch API 의
#     대상 + 이름 인자 · patch API 대상 인자의 문자열 경로 · 한 번 대입된 지역 이름). 같은 AST 위치의 옛 자리 → 새 자리만
#     대응하고, 수신자의 이름 부분만 표지로 바꾼다(인자 · 대체값 · 옵션은 그대로). 제품 쪽은 기준 판의 옛 def · 대상 판의
#     새 def · 대상 판에 옛 def 없음을 본다. 대응 충돌 · 표지 이름이 원문에 있음은 판정 불가.
#   · 0T 시험 전환(build-state slices[0].test_switch 기록이 있을 때만): 0T 커밋 걸음은 슬라이스 0 대조 구간을 끊고
#     명세 `시험 전환:` 행의 시험 함수마다 행위 문장 하나만 옛 대상 → 새 대상으로 바뀌었는지 대조한다(단언 · patch ·
#     행 밖 내용 그대로 · 더한 것은 행위 앞 import · 단순 대입). 뒤 구간은 0T 끝 판에서 시작한다. 0T 커밋은 web/ 무변 ·
#     행에 적힌 시험 파일만 · 첫 0C 커밋보다 앞이고, 검증(verified) 전 0C 커밋은 어긋남이다. 취소(cancelled)는 0T 와
#     취소 커밋의 합이 무변일 때 둘 다 대조에서 뺀다.

import ast
import difflib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Dict, Iterator, List, NamedTuple, Optional, Sequence, Set, Tuple, Union

from .debt import _FENCE_RE, _SPEC_HEAD_RE, DebtError, is_test_path, module_of, parse_spec_pairs

_IDENT: str = 'A-Za-z0-9_'
Func = Union[ast.FunctionDef, ast.AsyncFunctionDef]


class _Pairs:
    """대상(새) → 기준(옛) 역치환 쌍."""

    def __init__(self) -> None:
        self.full: Dict[str, str] = {}      # 점 경로 전체(이름 쌍)
        self.prefix: Dict[str, str] = {}    # 모듈·패키지 점 경로 접두(점 성분 경계)
        self.bare: Dict[str, str] = {}      # 맨 이름(끝 성분이 바뀐 이름 쌍)
        self.text: Dict[str, str] = {}      # 꼬리 문자열(경로)
        self.renames: List[Tuple[str, str]] = []  # web/ 개명 쌍(옛, 새 — web-상대) · 미러 테스트 이동 판정 입력
        self.moves: List['_MethodMove'] = []      # 승인된 메서드 이동(명세 `메서드 이동:` 행)
        self.switches: List['_TestSwitch'] = []   # 승인된 시험 전환(명세 `시험 전환:` 행)
        self.resolver: Optional['_Resolver'] = None
        self.infos: List[str] = []                # 메서드 이동 정규화 알림(대조 중 쌓임)
        self._regex: Optional['re.Pattern[str]'] = None

    def count(self) -> int:
        return len(self.full) + len(self.prefix) + len(self.bare) + len(self.text)

    def binding(self, dotted: str, alias: Optional[str]) -> str:
        if dotted in self.full:
            return self.full[dotted]
        for new in sorted(self.prefix, key=len, reverse=True):
            if dotted == new or dotted.startswith(new + '.'):
                dotted = self.prefix[new] + dotted[len(new):]
                break
        if alias is None and '.' in dotted:
            head, last = dotted.rsplit('.', 1)
            if last in self.bare:
                dotted = head + '.' + self.bare[last]
        return dotted

    def substitute(self, text: str) -> str:
        """모든 쌍을 긴 것부터 동시에 거꾸로 치환한다(단어·점 성분 경계)."""
        table: Dict[str, str] = {}
        parts: List[Tuple[int, str]] = []
        for new, old in self.text.items():
            table[new] = old
            tail: str = '' if new.endswith('/') else '(?![%s])' % _IDENT
            parts.append((len(new), '(?<![%s])%s%s' % (_IDENT, re.escape(new), tail)))
        for source, before in ((self.full, _IDENT + '.'), (self.prefix, _IDENT + '.'),
                               (self.bare, _IDENT)):
            # 점 경로는 앞에 점이 오면 다른 경로의 일부다. 맨 이름은 속성 참조(`vm.<이름>`)도 바꾼다.
            for new, old in source.items():
                table[new] = old
                parts.append((len(new), '(?<![%s])%s(?![%s])' % (before, re.escape(new), _IDENT)))
        if not parts:
            return text
        if self._regex is None:
            self._regex = re.compile('|'.join(p for _n, p in sorted(parts, key=lambda x: -x[0])))
        return self._regex.sub(lambda m: table[m.group(0)], text)


def _git(root: Path, args: List[str]) -> bytes:
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
    if result.returncode != 0:
        raise DebtError('git %s 실패 — %s' % (' '.join(args[:2]),
                                             result.stderr.decode('utf-8', 'replace').strip()))
    return result.stdout


def _commit(root: Path, rev: str) -> str:
    return _git(root, ['rev-parse', '--verify', '-q', rev + '^{commit}']).decode().strip()


def _blob(root: Path, rev: str, rel: str) -> bool:
    result = subprocess.run(['git', '-C', str(root), 'cat-file', '-t', '%s:%s' % (rev, rel)],
                            capture_output=True)
    return result.returncode == 0 and result.stdout.strip() == b'blob'


def _tree_files(root: Path, rev: str) -> Set[str]:
    out: bytes = _git(root, ['ls-tree', '-r', '--name-only', '-z', rev, '--', 'web/'])
    return {p[len('web/'):] for p in out.decode('utf-8').split('\0') if p.startswith('web/')}


def _web_changes(root: Path, base: str, target: str) -> Tuple[List[Tuple[str, str]], Set[str]]:
    """기준..대상의 web/ 개명 쌍(옛·새 모두 web/)과 새로 생긴 web/ 경로(A · web/ 밖에서 들어온 것 포함)."""
    out: List[str] = _git(root, ['diff', '-M', '--name-status', '-z', base, target,
                                 '--', 'web/']).decode('utf-8').split('\0')
    pairs: List[Tuple[str, str]] = []
    added: Set[str] = set()
    i: int = 0
    while i < len(out) and out[i]:
        status: str = out[i]
        if status[0] in 'RC':
            old, new = out[i + 1], out[i + 2]
            if status[0] == 'R' and old.startswith('web/') and new.startswith('web/'):
                pairs.append((old[len('web/'):], new[len('web/'):]))
            elif new.startswith('web/'):
                added.add(new[len('web/'):])
            i += 3
        else:
            if status[0] == 'A' and out[i + 1].startswith('web/'):
                added.add(out[i + 1][len('web/'):])
            i += 2
    return pairs, added


def _history_renames(root: Path, base: str, target: str, base_files: Set[str],
                     target_files: Set[str]) -> List[Tuple[str, str]]:
    """누적 개명 ∪ 커밋별 개명 사슬. 사슬 쌍은 누적 개명과 같은 트리 조건(옛 경로는 기준에만 ·
    새 경로는 대상에만 있다)을 채울 때만 더한다 — 슬라이스 0 이 개명한 파일을 뒤 커밋이 고쳐 쓰면
    누적 diff 는 D+A 로 본다. 구간 안에서 새로 생긴 경로는 계보가 없다(비운 옛 이름에 다시 만든
    파일을 기준 파일의 후계로 잡지 않는다)."""
    found: Dict[str, str] = {new: old for old, new in _web_changes(root, base, target)[0]}
    origin: Dict[str, Optional[str]] = {}
    lines: List[str] = _git(root, ['rev-list', '--reverse', '--first-parent', '--parents',
                                   '%s..%s' % (base, target)]).decode().splitlines()
    for line in lines:
        ids: List[str] = line.split()
        # 뿌리 커밋은 빈 트리와 비교한다 — 뿌리가 들인 경로도 구간 안에서 새로 생긴 경로다.
        parent: str = ids[1] if len(ids) > 1 else _git(
            root, ['hash-object', '-t', 'tree', '/dev/null']).decode().strip()
        renames, added = _web_changes(root, parent, ids[0])
        for old, new in renames:
            origin[new] = origin.pop(old, old)
        for path in added:
            origin[path] = None
    for new, source in origin.items():
        if (source is not None and source in base_files and source not in target_files
                and new in target_files and new not in base_files):
            found.setdefault(new, source)
    return sorted((old, new) for new, old in found.items())


def _folder_pairs(renames: List[Tuple[str, str]], base_files: Set[str],
                  target_files: Set[str]) -> List[Tuple[str, str]]:
    """옛 폴더 아래 기준 파일이 전부 같은 접두 변환으로 개명됐고 대상 트리에 옛 폴더가 없을 때만."""
    moved: Dict[str, str] = dict(renames)
    found: Set[Tuple[str, str]] = set()
    for old, new in renames:
        segs: List[str] = old.split('/')
        for k in range(1, len(segs)):
            folder: str = '/'.join(segs[:k])
            rest: str = '/'.join(segs[k:])
            if not new.endswith('/' + rest):
                continue
            dest: str = new[:-len(rest) - 1]
            if dest == folder:
                continue
            members: List[str] = [f for f in base_files if f.startswith(folder + '/')]
            if all(moved.get(f) == dest + f[len(folder):] for f in members) and not any(
                    f.startswith(folder + '/') for f in target_files):
                found.add((folder, dest))
    return sorted(found)


def _strip_static(rel: str) -> str:
    return rel[len('static/'):] if rel.startswith('static/') else rel


def _in_static(rel: str) -> bool:
    return rel == 'static' or rel.startswith('static/')


def _static_id(rel: str) -> str:
    """web 기준 상대 경로 → static 식별자(`{% static %}`·`static(...)` 인자 · `/static/` 뒤 URL 꼬리).
    STATICFILES_DIRS 접두 둘: `static/<x>` → `web/<x>` · `design_system/<x>` → 그대로(common.static_target 의 거꾸로)."""
    return 'web' + rel[len('static'):] if _in_static(rel) else rel


def _text_pairs(old: str, new: str, tail: str = '') -> List[Tuple[str, str]]:
    """경로 이동 한 쌍(파일이면 tail = '' · 폴더면 '/')의 거꾸로 치환 꼬리 쌍 [(새, 옛)].
    같은 쪽(둘 다 static 안 · 둘 다 밖) 이동은 `static/` 을 뗀 꼬리 하나가 식별자와 저장소 경로 문자열을 함께 받는다.
    static 접두를 건너는 이동은 한 꼬리로 두 꼴을 받을 수 없어 둘로 가른다 — static 식별자 쌍
    (`design_system/guest/theme/app_theme.css` ↔ `web/css/base.css`)과 저장소 파일 경로 쌍
    (`web/design_system/guest/theme/app_theme.css` ↔ `web/static/css/base.css`). 긴 쌍이 먼저 맞는다(_Pairs.substitute)."""
    if _in_static(old) == _in_static(new):
        return [(_strip_static(new) + tail, _strip_static(old) + tail)]
    return [(_static_id(new) + tail, _static_id(old) + tail), ('web/' + new + tail, 'web/' + old + tail)]


def build_pairs(root: Path, base: str, target: str, names_file: Optional[str]) -> _Pairs:
    pairs: _Pairs = _Pairs()
    base_files: Set[str] = _tree_files(root, base)
    target_files: Set[str] = _tree_files(root, target)
    renames: List[Tuple[str, str]] = _history_renames(root, base, target, base_files, target_files)
    pairs.renames = renames
    for old, new in renames:
        pairs.text.update(_text_pairs(old, new))
        old_mod, new_mod = module_of(old), module_of(new)
        if old_mod and new_mod:
            pairs.prefix[new_mod] = old_mod
    for folder, dest in _folder_pairs(renames, base_files, target_files):
        pairs.text.update(_text_pairs(folder, dest, '/'))
        pairs.prefix['web.' + dest.replace('/', '.')] = 'web.' + folder.replace('/', '.')
    if names_file is not None:
        try:
            text: str = Path(names_file).read_text(encoding='utf-8')
        except OSError as error:
            raise DebtError('--names 파일을 읽을 수 없다 — %s' % error)
        names: List[Tuple[str, str]] = parse_spec_pairs(text, require=True)[1]
        for old, new in names:
            pairs.full[new] = old
            if new.rsplit('.', 1)[1] != old.rsplit('.', 1)[1]:
                pairs.bare[new.rsplit('.', 1)[1]] = old.rsplit('.', 1)[1]
        pairs.moves, pairs.switches = parse_spec_approvals(text)
        _check_approvals(pairs.moves, pairs.switches, names)
    pairs.resolver = _Resolver(root)
    return pairs


# ------------------------------------------------------------------ 승인 행(메서드 이동 · 시험 전환)

_MOVE_PATH: str = r'web(?:\.[a-z_][a-z0-9_]*)+\.[A-Z][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*'
_TEST_REF: str = r'[^\s`:]+\.py::[A-Za-z_][A-Za-z0-9_]*'
_TARGET_PATH: str = r'web(?:\.[A-Za-z_][A-Za-z0-9_]*)+'
_MOVE_ROW_RE = re.compile(r'^\s*(?:[-*] )?메서드 이동:\s*`?(%s)`?\s*→\s*`?(%s)`?\s*·\s*시험((?:\s+`?%s`?)+)\s*$'
                          % (_MOVE_PATH, _MOVE_PATH, _TEST_REF))
_SWITCH_ROW_RE = re.compile(r'^\s*(?:[-*] )?시험 전환:\s*`?([^\s`:]+\.py)::([A-Za-z_][A-Za-z0-9_]*)`?\s*·\s*'
                            r'행위\s+`?(%s)`?\s*→\s*`?(%s)`?\s*·\s*보호 분기\s+\S.*?\s*·\s*반례\s+\S.*$'
                            % (_TARGET_PATH, _TARGET_PATH))
_MARKER_RE = re.compile(r'__dddjango_m\d+__')


class _MethodMove:
    """승인된 메서드 이동 한 행 — 옛 · 새 `<모듈>.<클래스>.<메서드>` 와 승인 범위(시험 파일 → 최상위 함수 이름)."""

    def __init__(self, index: int, old: str, new: str, tests: List[Tuple[str, str]]) -> None:
        self.old: str = old
        self.new: str = new
        self.old_class, self.old_method = old.rsplit('.', 1)
        self.new_class, self.new_method = new.rsplit('.', 1)
        self.marker: str = '__dddjango_m%d__' % index
        self.tests: Dict[str, Set[str]] = {}
        for path, func in tests:
            self.tests.setdefault(path, set()).add(func)

    def label(self) -> str:
        return '%s → %s' % (self.old, self.new)

    def functions(self) -> int:
        return sum(len(funcs) for funcs in self.tests.values())


class _TestSwitch(NamedTuple):
    path: str       # 시험 파일(저장소 상대)
    func: str       # 최상위 시험 함수 이름
    old: str        # 옛 행위 대상(web. 점 경로)
    new: str        # 새 행위 대상


def _is_test_file(path: str) -> bool:
    return (path.endswith('.py') and not path.startswith('/') and '..' not in path.split('/')
            and is_test_path(path))


def parse_spec_approvals(text: str) -> Tuple[List[_MethodMove], List[_TestSwitch]]:
    """design-spec.md `## 슬라이스 0` 절 안 승인 행 — (메서드 이동, 시험 전환). 절 밖 줄 · 코드 울타리 안 줄은 읽지 않고,
    꼴이 어긋난 줄은 승인으로 읽지 않는다(알림 없음 — 그 시험은 지금처럼 대조된다). 절 머리 수와 `경로:` · `이름:`
    행 형식은 parse_spec_pairs 가 먼저 본다."""
    inside: bool = False
    fenced: bool = False
    moves: List[_MethodMove] = []
    switches: List[_TestSwitch] = []
    for line in text.splitlines():
        if _FENCE_RE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.startswith('#') and not line.startswith('###'):
            inside = bool(_SPEC_HEAD_RE.match(line))
            continue
        if not inside:
            continue
        move = _MOVE_ROW_RE.match(line)
        if move:
            tests: List[Tuple[str, str]] = [tuple(ref.split('::')) for ref in re.findall(_TEST_REF, move.group(3))]
            if all(_is_test_file(path) for path, _func in tests):
                moves.append(_MethodMove(len(moves), move.group(1), move.group(2), tests))
            continue
        switch = _SWITCH_ROW_RE.match(line)
        if switch and _is_test_file(switch.group(1)):
            switches.append(_TestSwitch(*switch.group(1, 2, 3, 4)))
    return moves, switches


def _check_approvals(moves: List[_MethodMove], switches: List[_TestSwitch], names: List[Tuple[str, str]]) -> None:
    """대응 충돌은 판정 불가 — 같은 옛 메서드 두 행 · 여러 옛 → 한 새 · 역방향 · 사슬 · `이름:` 행과 같은 클래스 경로 ·
    같은 시험 함수의 시험 전환 두 행 · 옛 대상 = 새 대상."""
    olds: Counter = Counter(m.old for m in moves)
    news: Counter = Counter(m.new for m in moves)
    named: Set[str] = {end for pair in names for end in pair}
    for move in moves:
        if olds[move.old] > 1:
            raise DebtError('메서드 이동 대응 충돌 — 같은 옛 메서드 %s 가 두 행에 있다' % move.old)
        if news[move.new] > 1:
            raise DebtError('메서드 이동 대응 충돌 — 여러 옛 메서드가 한 새 메서드 %s 로 간다' % move.new)
        if move.old in news or move.new in olds:
            raise DebtError('메서드 이동 대응 충돌 — 역방향 · 사슬 대응(%s)' % move.label())
        overlap: Set[str] = named & {move.old, move.new, move.old_class, move.new_class}
        if overlap:
            raise DebtError('메서드 이동 대응 충돌 — `이름:` 행과 같은 경로를 겹쳐 쓴다(%s)' % ', '.join(sorted(overlap)))
    seen: Set[Tuple[str, str]] = set()
    for switch in switches:
        if (switch.path, switch.func) in seen:
            raise DebtError('시험 전환 행 충돌 — 같은 시험 함수 %s::%s 가 두 행에 있다' % (switch.path, switch.func))
        seen.add((switch.path, switch.func))
        if switch.old == switch.new:
            raise DebtError('시험 전환 행 충돌 — 옛 대상과 새 대상이 같다(%s)' % switch.old)


# ------------------------------------------------------------------ 판(rev)마다 web 모듈 해석


class _Resolver:
    """판(rev)별 web 모듈 해석 — 모듈 파일 · 최상위 정의 · 최상위 `from X import Y [as Z]` 재수출 건넘(최대 HOPS 칸 —
    순환 · 초과는 해석 불가)."""

    HOPS: int = 4

    def __init__(self, root: Path) -> None:
        self.root: Path = root
        self._files: Dict[str, Set[str]] = {}
        self._sources: Dict[Tuple[str, str], Optional[str]] = {}

    def module_file(self, rev: str, dotted: str) -> Optional[str]:
        if dotted != 'web' and not dotted.startswith('web.'):
            return None
        if rev not in self._files:
            self._files[rev] = _tree_files(self.root, rev)
        rel: str = dotted[len('web.'):].replace('.', '/') if dotted != 'web' else ''
        for candidate in ([rel + '.py', rel + '/__init__.py'] if rel else ['__init__.py']):
            if candidate in self._files[rev]:
                return 'web/' + candidate
        return None

    def source(self, rev: str, dotted: str) -> Optional[str]:
        if (rev, dotted) not in self._sources:
            path: Optional[str] = self.module_file(rev, dotted)
            text: Optional[str] = None
            if path is not None:
                try:
                    text = _git(self.root, ['cat-file', 'blob', '%s:%s' % (rev, path)]).decode('utf-8')
                except (DebtError, UnicodeDecodeError):
                    text = None
            self._sources[(rev, dotted)] = text
        return self._sources[(rev, dotted)]

    def module_ast(self, rev: str, dotted: str) -> Optional[ast.Module]:
        text: Optional[str] = self.source(rev, dotted)
        if text is None:
            return None
        try:
            return ast.parse(text)
        except SyntaxError:
            return None

    def _top_binding(self, rev: str, module: str, name: str) -> Tuple[str, Optional[str]]:
        """모듈 최상위에서 name 의 바인딩 — ('def', None) · ('import', 전체 경로) · ('none', None)(없음 · 여럿)."""
        tree: Optional[ast.Module] = self.module_ast(rev, module)
        if tree is None:
            return 'none', None
        package: List[str] = module.split('.')
        if not str(self.module_file(rev, module)).endswith('__init__.py'):
            package = package[:-1]
        hits: List[Tuple[str, Optional[str]]] = []
        for st in tree.body:
            if isinstance(st, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == name:
                hits.append(('def', None))
            elif isinstance(st, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in st.targets):
                hits.append(('def', None))
            elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and st.target.id == name:
                hits.append(('def', None))
            elif isinstance(st, ast.Import):
                # `import X [as Z]` 바인딩은 건너지 않는다(재수출은 `from X import Y [as Z]` 만) — 있으면 해석 불가
                hits.extend(('none', None) for alias in st.names if (alias.asname or alias.name.split('.')[0]) == name)
            elif isinstance(st, ast.ImportFrom):
                for alias in st.names:
                    if (alias.asname or alias.name) != name:
                        continue
                    if st.level == 0:
                        hits.append(('import', '%s.%s' % (st.module, alias.name)))
                    elif st.level - 1 < len(package):
                        parts: List[str] = package[:len(package) - (st.level - 1)] + ([st.module] if st.module else [])
                        hits.append(('import', '.'.join(parts + [alias.name])))
                    else:
                        hits.append(('none', None))
        return hits[0] if len(hits) == 1 else ('none', None)

    def canonical(self, rev: str, dotted: str) -> Optional[str]:
        """점 경로 → 그 판에서 정의된 자리의 전체 경로(web 밖이면 그대로) · 해석 불가면 None."""
        seen: Set[str] = {dotted}
        for _hop in range(self.HOPS + 1):
            if dotted != 'web' and not dotted.startswith('web.'):
                return dotted
            parts: List[str] = dotted.split('.')
            k: int = len(parts)
            while k > 0 and self.module_file(rev, '.'.join(parts[:k])) is None:
                k -= 1
            if k == 0:
                return None
            if k == len(parts):
                return dotted
            kind, value = self._top_binding(rev, '.'.join(parts[:k]), parts[k])
            if kind == 'def':
                return dotted
            if kind != 'import' or value is None:
                return None
            dotted = '.'.join([value] + parts[k + 1:])
            if dotted in seen:
                return None
            seen.add(dotted)
        return None

    def methods(self, rev: str, class_path: str, method: str) -> List[Func]:
        """그 판 클래스 본문의 method def(최상위 클래스 하나일 때만)."""
        module, name = class_path.rsplit('.', 1)
        tree: Optional[ast.Module] = self.module_ast(rev, module)
        if tree is None:
            return []
        classes: List[ast.ClassDef] = [st for st in tree.body if isinstance(st, ast.ClassDef) and st.name == name]
        if len(classes) != 1:
            return []
        return [st for st in classes[0].body
                if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == method]


def _mirror(rel: str) -> Optional[str]:
    """web/ 의 .py SUT → web_test/ 미러 테스트 경로(`web_test/<같은 경로>/<sut>_test.py`)."""
    if not rel.endswith('.py'):
        return None
    head, _, name = rel.rpartition('/')
    return 'web_test/' + (head + '/' if head else '') + name[:-3] + '_test.py'


def _dir_shifts(renames: List[Tuple[str, str]]) -> Set[Tuple[str, str]]:
    """SUT 개명이 보여 준 디렉터리 이동 — 같은 꼬리(파일명 포함)를 남기고 앞부분만 바뀐 (옛 접두, 새 접두)."""
    found: Set[Tuple[str, str]] = set()
    for old, new in renames:
        o, n = old.split('/'), new.split('/')
        common: int = 0
        while common < min(len(o), len(n)) - 1 and o[-1 - common] == n[-1 - common]:
            common += 1
        for j in range(1, common + 1):
            fo, fn = '/'.join(o[:-j]), '/'.join(n[:-j])
            if fo and fn and fo != fn:
                found.add((fo, fn))
    return found


def _test_moves(base_paths: Set[str], target_paths: Set[str], renames: List[Tuple[str, str]]) -> Dict[str, str]:
    """기준에만 있는 web_test/ 경로와 대상에만 있는 web_test/ 경로를 SUT 이동과 같은 경로 대응으로 짝짓는다 —
    {새 경로: 옛 경로}(저장소 상대). 대응 = 그 SUT 의 미러 경로 쌍이거나, SUT 개명이 보여 준 디렉터리 이동을 그대로
    따른 것(`_support.py` 류). git 개명 탐지(유사도)에 기대지 않는다 — 내용 대조는 호출 쪽이 한다."""
    files: Dict[str, str] = {}
    for old, new in renames:
        mo, mn = _mirror(old), _mirror(new)
        if mo and mn:
            files[mo] = mn
    shifts: List[Tuple[str, str]] = sorted(_dir_shifts(renames), key=lambda p: -len(p[0]))
    gone: List[str] = sorted(p for p in base_paths - target_paths if p.startswith('web_test/'))
    born: Set[str] = {p for p in target_paths - base_paths if p.startswith('web_test/')}
    moves: Dict[str, str] = {}
    for old in gone:
        cands: List[str] = [files[old]] if old in files else []
        cands += ['web_test/%s/%s' % (fn, old[len('web_test/%s/' % fo):])
                  for fo, fn in shifts if old.startswith('web_test/%s/' % fo)]
        for cand in cands:
            if cand in born and cand not in moves:
                moves[cand] = old
                break
    return moves


# ------------------------------------------------------------------ .py 대조


def _bindings(node: ast.stmt) -> List[Tuple[str, Optional[str]]]:
    if isinstance(node, ast.Import):
        return [(a.name, a.asname) for a in node.names]
    assert isinstance(node, ast.ImportFrom)
    mod: str = '.' * node.level + (node.module or '')
    sep: str = '.' if node.module else ''
    return [(mod + sep + a.name, a.asname) for a in node.names]


def _import_blocks(tree: ast.Module) -> List[Tuple[Tuple, ast.stmt]]:
    """블록·위치별 연속 import 구간의 import 문(원문 차례) — [(위치 키, 문)]. 위치 = 그 블록에서 구간 앞 비-import 문 수."""
    out: List[Tuple[Tuple, ast.stmt]] = []

    def walk(stmts: List[ast.stmt], path: Tuple) -> None:
        pos: int = 0
        for st in stmts:
            if isinstance(st, (ast.Import, ast.ImportFrom)):
                out.append((path + (pos,), st))
                continue
            for field, value in ast.iter_fields(st):
                if isinstance(value, list) and value and isinstance(value[0], ast.stmt):
                    walk(value, path + (pos, field))
                elif isinstance(value, list):
                    for j, item in enumerate(value):
                        body = getattr(item, 'body', None)
                        if isinstance(body, list) and body and isinstance(body[0], ast.stmt):
                            walk(body, path + (pos, field, j))
            pos += 1

    walk(tree.body, ())
    return out


def _segments(tree: ast.Module, pairs: Optional[_Pairs]) -> Dict[Tuple, Tuple[int, Counter]]:
    """블록·위치별 연속 import 구간 → (첫 행, 바인딩 다중집합)."""
    out: Dict[Tuple, Tuple[int, Counter]] = {}
    for key, st in _import_blocks(tree):
        line, bag = out.setdefault(key, (st.lineno, Counter()))
        for dotted, alias in _bindings(st):
            if pairs is not None:
                dotted = pairs.binding(dotted, alias)
            bag[(dotted, alias)] += 1
    return out


class _DropImports(ast.NodeTransformer):
    def generic_visit(self, node: ast.AST) -> ast.AST:
        for field, value in ast.iter_fields(node):
            if isinstance(value, list) and value and isinstance(value[0], ast.stmt):
                setattr(node, field, [s for s in value
                                      if not isinstance(s, (ast.Import, ast.ImportFrom))])
        return super().generic_visit(node)


def _first_diff(base: ast.Module, target: ast.Module) -> int:
    for b, t in zip(base.body, target.body):
        if ast.dump(b) != ast.dump(t):
            return getattr(t, 'lineno', 1)
    extra: List[ast.stmt] = target.body[len(base.body):]
    return getattr(extra[0], 'lineno', 1) if extra else 1


# ------------------------------------------------------------------ 시험 파일 이름 해석 · 메서드 이동 자리

_NESTED_SCOPES: Tuple[type, ...] = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)
_MATCH_NAMES: Tuple[type, ...] = tuple(getattr(ast, n) for n in ('MatchAs', 'MatchStar') if hasattr(ast, n))
_FIXTURES: Tuple[str, ...] = ('monkeypatch', 'mocker')          # pytest · pytest-mock fixture 인자 이름
_BUILTIN_APIS: Tuple[str, ...] = ('setattr', 'getattr', 'hasattr', 'delattr')
_NAME_ARG_APIS: Set[str] = {'unittest.mock.patch.object', 'fixture:mocker.patch.object', 'fixture:monkeypatch.setattr',
                            'fixture:monkeypatch.delattr', 'fixture:mocker.spy', 'builtins.setattr', 'builtins.getattr',
                            'builtins.hasattr', 'builtins.delattr'}
_STRING_TARGET_APIS: Set[str] = {'unittest.mock.patch', 'fixture:mocker.patch', 'fixture:monkeypatch.setattr'}
_IMPORT_MODULE: str = 'importlib.import_module'
Binding = Tuple[str, object]           # (종류 import|module_call|param|other, 값)
Edit = Tuple[int, int, int, int, str]  # (행, 열, 끝 행, 끝 열 — 열은 utf-8 바이트, 바꿀 글)


def _dotted(node: ast.AST) -> Optional[str]:
    """Name · Attribute 사슬 → 점 경로(그 밖은 None)."""
    parts: List[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return '.'.join(reversed(parts))


def _module_call(value: Optional[ast.expr]) -> Optional[Tuple[ast.expr, str]]:
    """`<호출>("<글자>")` 꼴(인자 하나 · 글자) → (호출 식, 글자)."""
    if (isinstance(value, ast.Call) and len(value.args) == 1 and not value.keywords
            and isinstance(value.args[0], ast.Constant) and isinstance(value.args[0].value, str)
            and _dotted(value.func) is not None):
        return value.func, value.args[0].value
    return None


def _scope_bindings(body: List[ast.stmt], params: Sequence[str] = ()) -> Dict[str, List[Binding]]:
    """한 범위(모듈 · 함수 본문)의 이름 바인딩 — 이름 → [(종류, 값)]. 중첩 함수 · 클래스 · lambda 본문은 들어가지 않는다."""
    found: Dict[str, List[Binding]] = {}

    def add(name: str, kind: str, value: object = None) -> None:
        found.setdefault(name, []).append((kind, value))

    def visit(node: ast.AST) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            add(node.name, 'other')
            return
        if isinstance(node, ast.Lambda):
            return
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound: str = alias.asname or alias.name.split('.')[0]
                add(bound, 'import', alias.name if alias.asname else bound)
            return
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == '*' or node.level:
                    add(alias.asname or alias.name, 'other')
                else:
                    add(alias.asname or alias.name, 'import', '%s.%s' % (node.module, alias.name))
            return
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            target: Optional[ast.expr] = (node.targets[0] if isinstance(node, ast.Assign) and len(node.targets) == 1
                                          else node.target if isinstance(node, ast.AnnAssign) else None)
            call = _module_call(node.value) if isinstance(target, ast.Name) else None
            if call is not None and isinstance(target, ast.Name):
                add(target.id, 'module_call', call)
                visit(node.value)
                return
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            add(node.id, 'other')
        elif isinstance(node, ast.ExceptHandler) and node.name:
            add(node.name, 'other')
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            for name in node.names:
                add(name, 'other')
        elif _MATCH_NAMES and isinstance(node, _MATCH_NAMES) and getattr(node, 'name', None):
            add(node.name, 'other')
        elif hasattr(ast, 'MatchMapping') and isinstance(node, ast.MatchMapping) and node.rest:
            add(node.rest, 'other')
        for child in ast.iter_child_nodes(node):
            visit(child)

    for name in params:
        add(name, 'param')
    for st in body:
        visit(st)
    return found


class _TestNames:
    """시험 파일 한 판의 이름 해석 — 함수 범위 · 모듈 범위 바인딩(모듈 머리 · 함수 안 import · 별칭 · 한 번 대입된
    `import_module("<글자>")`)을 전체 경로로 · web 경로는 그 판 web 모듈로 재수출을 건넌다. 두 번 이상 바인딩된 이름 ·
    함수 인자(fixture monkeypatch · mocker 밖) · 그 밖 대입은 해석하지 않는다."""

    def __init__(self, tree: ast.Module, resolver: _Resolver, rev: str) -> None:
        self.resolver: _Resolver = resolver
        self.rev: str = rev
        self.module: Dict[str, List[Binding]] = _scope_bindings(tree.body)
        self._scopes: Dict[int, Dict[str, List[Binding]]] = {}
        self._active: Set[Tuple[int, str]] = set()

    def scope(self, func: Func) -> Dict[str, List[Binding]]:
        if id(func) not in self._scopes:
            args: ast.arguments = func.args
            params: List[str] = [a.arg for a in args.posonlyargs + args.args + args.kwonlyargs]
            params += [a.arg for a in (args.vararg, args.kwarg) if a is not None]
            self._scopes[id(func)] = _scope_bindings(func.body, params)
        return self._scopes[id(func)]

    def name(self, func: Optional[Func], name: str) -> Optional[str]:
        local: Optional[List[Binding]] = self.scope(func).get(name) if func is not None else None
        entries: Optional[List[Binding]] = local if local is not None else self.module.get(name)
        if entries is None:
            return 'builtins.' + name if name in _BUILTIN_APIS and '*' not in self.module else None
        if len(entries) != 1:
            return None
        kind, value = entries[0]
        if kind == 'import':
            return str(value)
        if kind == 'param':     # fixture 인자 — 이 모듈이 같은 이름을 따로 정의 · import 했으면 그 fixture 가 아닐 수 있다
            return 'fixture:' + name if name in _FIXTURES and name not in self.module else None
        key: Tuple[int, str] = (id(func), name)
        if kind == 'module_call' and key not in self._active:
            self._active.add(key)
            try:
                api: Optional[str] = self.expr(func if local is not None else None, value[0])
            finally:
                self._active.discard(key)
            return value[1] if api == _IMPORT_MODULE else None
        return None

    def expr(self, func: Optional[Func], node: ast.AST) -> Optional[str]:
        dotted: Optional[str] = _dotted(node)
        if dotted is None:
            return None
        head, _, rest = dotted.partition('.')
        base: Optional[str] = self.name(func, head)
        if base is None:
            return None
        path: str = base + ('.' + rest if rest else '')
        if path == 'web' or path.startswith('web.'):
            return self.resolver.canonical(self.rev, path)
        return path


def _top_function(tree: ast.Module, name: str) -> Optional[Func]:
    found: List[Func] = [st for st in tree.body
                         if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == name]
    return found[0] if len(found) == 1 else None


def _walk_func(func: Func) -> List[Tuple[ast.AST, Tuple]]:
    """함수 본문의 노드와 위치 경로((필드, 순번) 사슬) — 중첩 함수 · 클래스 · lambda 본문은 들어가지 않는다."""
    out: List[Tuple[ast.AST, Tuple]] = []

    def walk(node: ast.AST, path: Tuple) -> None:
        if isinstance(node, _NESTED_SCOPES):
            return
        for field, value in ast.iter_fields(node):
            for index, item in (enumerate(value) if isinstance(value, list) else [(-1, value)]):
                if isinstance(item, ast.AST) and not isinstance(item, ast.expr_context):
                    here: Tuple = path + ((field, index),)
                    out.append((item, here))
                    walk(item, here)

    for index, st in enumerate(func.body):
        out.append((st, (('body', index),)))
        walk(st, (('body', index),))
    return out


def _binding_count(func: Func, name: str) -> int:
    """함수 안(중첩 범위 포함)에서 name 을 바인딩하는 자리 수 — 대입 · 인자 · except · import · def · global 등."""
    count: int = 0
    for node in ast.walk(func):
        if isinstance(node, ast.Name):
            count += node.id == name and isinstance(node.ctx, (ast.Store, ast.Del))
        elif isinstance(node, ast.arg):
            count += node.arg == name
        elif isinstance(node, ast.ExceptHandler):
            count += node.name == name
        elif isinstance(node, ast.Import):
            count += sum((a.asname or a.name.split('.')[0]) == name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            count += sum((a.asname or a.name) == name for a in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node is not func:
            count += node.name == name
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            count += name in node.names
        elif _MATCH_NAMES and isinstance(node, _MATCH_NAMES):
            count += getattr(node, 'name', None) == name
        elif hasattr(ast, 'MatchMapping') and isinstance(node, ast.MatchMapping):
            count += node.rest == name
    return count


def _local_uses(func: Func, nodes: List[Tuple[ast.AST, Tuple]], name: str,
                method: str) -> Optional[List[Tuple[Tuple, ast.Attribute]]]:
    """(e) 지역 이름 — 함수 안 바인딩이 그 대입 하나이고 모든 쓰임이 `name.method` 일 때 쓰임 자리들(아니면 None)."""
    if _binding_count(func, name) != 1:
        return None
    parent_of: Dict[int, ast.AST] = {id(child): parent for parent in ast.walk(func) for child in ast.iter_child_nodes(parent)}
    path_of: Dict[int, Tuple] = {id(node): path for node, path in nodes}
    uses: List[Tuple[Tuple, ast.Attribute]] = []
    for node in ast.walk(func):
        if isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, ast.Load):
            parent: Optional[ast.AST] = parent_of.get(id(node))
            if not (isinstance(parent, ast.Attribute) and parent.value is node and parent.attr == method
                    and id(parent) in path_of):
                return None
            uses.append((path_of[id(parent)], parent))
    return uses or None


def _span(node: ast.AST, text: str) -> Edit:
    return (node.lineno, node.col_offset, node.end_lineno, node.end_col_offset, text)


def _attr_span(node: ast.Attribute, text: str) -> Edit:
    """속성 이름 글자 구간 — Attribute 끝의 이름(끝 열에서 이름 바이트 길이만큼)."""
    width: int = len(node.attr.encode('utf-8'))
    return (node.end_lineno, node.end_col_offset - width, node.end_lineno, node.end_col_offset, text)


def _string_target(call: ast.Call, api: Optional[str]) -> Optional[ast.Constant]:
    """검증된 patch API 의 대상 인자 자리의 글자 상수(첫 위치 인자 · patch 의 `target=`)."""
    if api not in _STRING_TARGET_APIS:
        return None
    node: Optional[ast.expr] = call.args[0] if call.args else next(
        (k.value for k in call.keywords if k.arg == 'target' and api != 'fixture:monkeypatch.setattr'), None)
    return node if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _move_sites(names: _TestNames, func: Func, move: _MethodMove, old_side: bool) -> Dict[Tuple, List[Edit]]:
    """승인된 함수 안 그 메서드 자리 → 표시 편집. 키 = (꼴, 위치 경로[, 쓰임 경로]) — 옛 · 새 판의 같은 키만 대응한다.
    수신자의 이름 부분만 표지로 · 메서드 이름은 옛 이름으로(호출 인자 · patch 대체값 · 옵션은 그대로)."""
    cls: str = move.old_class if old_side else move.new_class
    method: str = move.old_method if old_side else move.new_method
    nodes: List[Tuple[ast.AST, Tuple]] = _walk_func(func)
    sites: Dict[Tuple, List[Edit]] = {}

    def is_class(node: ast.AST) -> bool:
        return _dotted(node) is not None and names.expr(func, node) == cls

    for node, path in nodes:
        if isinstance(node, ast.Call):
            callee: ast.expr = node.func
            if (isinstance(callee, ast.Attribute) and callee.attr == method and isinstance(callee.value, ast.Call)
                    and is_class(callee.value.func)):
                sites[('a', path)] = [_span(callee.value.func, move.marker), _attr_span(callee, move.old_method)]
            api: Optional[str] = names.expr(func, callee) if _dotted(callee) is not None else None
            if (api in _NAME_ARG_APIS and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant)
                    and node.args[1].value == method and is_class(node.args[0])):
                sites[('c', path)] = [_span(node.args[0], move.marker), _span(node.args[1], repr(move.old_method))]
            target: Optional[ast.Constant] = _string_target(node, api)
            if target is not None and re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+', target.value):
                prefix, last = target.value.rsplit('.', 1)
                if last == method and names.resolver.canonical(names.rev, prefix) == cls:
                    sites[('d', path)] = [_span(target, repr('%s.%s' % (move.marker, move.old_method)))]
        elif isinstance(node, ast.Attribute) and node.attr == method and is_class(node.value):
            sites[('b', path)] = [_span(node.value, move.marker), _attr_span(node, move.old_method)]
        elif (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
              and isinstance(node.value, ast.Call) and is_class(node.value.func)):
            uses = _local_uses(func, nodes, node.targets[0].id, method)
            if uses:
                sites[('e', path, tuple(p for p, _n in uses))] = (
                    [_span(node.value.func, move.marker)] + [_attr_span(n, move.old_method) for _p, n in uses])
    return sites


def _apply_edits(src: str, edits: List[Edit]) -> str:
    data: bytes = src.encode('utf-8')
    starts: List[int] = [0]
    pos: int = data.find(b'\n')
    while pos != -1:
        starts.append(pos + 1)
        pos = data.find(b'\n', pos + 1)
    spans = sorted({(starts[a - 1] + b, starts[c - 1] + d, text) for a, b, c, d, text in edits}, reverse=True)
    limit: int = len(data)
    for start, end, text in spans:
        if end > limit:
            raise DebtError('메서드 이동 자리가 서로 겹친다 — 판정 불가')
        data = data[:start] + text.encode('utf-8') + data[end:]
        limit = start
    return data.decode('utf-8')


def _loads(tree: ast.Module, owner: Optional[str], name: str) -> bool:
    scopes: List[ast.AST] = ([st for st in tree.body if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef))
                              and st.name == owner] if owner else [tree])
    return any(isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, ast.Load)
               for scope in scopes for n in ast.walk(scope))


def _site_only_imports(tree: ast.Module, marked: ast.Module, names: _TestNames, classes: Set[str],
                       pairs: Optional[_Pairs]) -> Dict[Tuple, Counter]:
    """자리 전용 바인딩 — 표시 뒤 Load 가 남지 않고 K(또는 그 모듈)로 풀리는 import 바인딩 → 위치 키별 다중집합
    (대상 쪽은 쌍 적용 뒤 바인딩 꼴)."""
    modules: Set[str] = {c.rsplit('.', 1)[0] for c in classes}
    owners: Dict[int, str] = {id(node): st.name for st in tree.body
                              if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef))
                              for node in ast.walk(st) if isinstance(node, (ast.Import, ast.ImportFrom))}
    out: Dict[Tuple, Counter] = {}
    for key, st in _import_blocks(tree):
        if isinstance(st, ast.ImportFrom) and st.level:
            continue
        for alias, (dotted, asname) in zip(st.names, _bindings(st)):
            if alias.name == '*':
                continue
            if isinstance(st, ast.Import):
                bound, full = alias.asname or alias.name.split('.')[0], alias.name
            else:
                bound, full = alias.asname or alias.name, '%s.%s' % (st.module, alias.name)
            resolved: Optional[str] = names.resolver.canonical(names.rev, full) if full.startswith('web.') else full
            owner: Optional[str] = owners.get(id(st))
            if (resolved not in classes and full not in modules) or not _loads(tree, owner, bound) or _loads(marked, owner, bound):
                continue    # K 가 아니거나 · 자리가 쓰지 않던 바인딩이거나 · 표시 뒤에도 읽힌다
            entry: Tuple[str, Optional[str]] = (pairs.binding(dotted, asname) if pairs is not None else dotted, asname)
            out.setdefault(key, Counter())[entry] += 1
    return out


def _mark_moves(path: str, base_src: str, target_src: str, base_tree: ast.Module, target_tree: ast.Module,
                pairs: _Pairs, revs: Optional[Tuple[str, str]]) -> Optional[Tuple[str, str, ast.Module, Dict, Dict]]:
    """승인된 메서드 이동 자리를 양쪽 판에서 같은 표지로 바꾼다 → (옛 원문, 새 원문, 옛 AST, 옛 자리 전용 import,
    새 자리 전용 import). 이 파일에 승인 자리가 없으면 None(지금 경로 그대로)."""
    rows: List[_MethodMove] = [m for m in pairs.moves if path in m.tests]
    if not rows or revs is None or pairs.resolver is None:
        return None
    if _MARKER_RE.search(base_src) or _MARKER_RE.search(target_src):
        raise DebtError('메서드 이동 대응 충돌 — 표지 이름(__dddjango_m…__)이 원문에 이미 있다 — %s' % path)
    if '\r' in base_src.replace('\r\n', '') or '\r' in target_src.replace('\r\n', ''):
        return None     # 줄 끝 판독이 AST 행과 어긋날 수 있다 — 정규화하지 않는다(fail-closed)
    sides: Tuple[_TestNames, _TestNames] = (_TestNames(base_tree, pairs.resolver, revs[0]),
                                            _TestNames(target_tree, pairs.resolver, revs[1]))
    edits: Tuple[List[Edit], List[Edit]] = ([], [])
    count: int = 0
    for move in rows:
        for name in sorted(move.tests[path]):
            old_func, new_func = _top_function(base_tree, name), _top_function(target_tree, name)
            if old_func is None or new_func is None:
                continue
            old_sites = _move_sites(sides[0], old_func, move, True)
            new_sites = _move_sites(sides[1], new_func, move, False)
            for key in sorted(set(old_sites) & set(new_sites), key=repr):
                edits[0].extend(old_sites[key])
                edits[1].extend(new_sites[key])
                count += 1
    if not count:
        return None
    marked: Tuple[str, str] = (_apply_edits(base_src, edits[0]), _apply_edits(target_src, edits[1]))
    try:
        marked_trees: Tuple[ast.Module, ast.Module] = (ast.parse(marked[0]), ast.parse(marked[1]))
    except SyntaxError as error:
        raise DebtError('%s 메서드 이동 표시 뒤 파싱 실패 — %s' % (path, error))
    pairs.infos.append('메서드 이동 자리 정규화 %s — %d곳' % (path, count))
    drop_old = _site_only_imports(base_tree, marked_trees[0], sides[0], {m.old_class for m in rows}, None)
    drop_new = _site_only_imports(target_tree, marked_trees[1], sides[1], {m.new_class for m in rows}, pairs)
    return marked[0], marked[1], marked_trees[0], drop_old, drop_new


def _drop_site_imports(path: str, line: int, base_bag: Counter, target_bag: Counter, drop_old: Optional[Counter],
                       drop_new: Optional[Counter], infos: List[str]) -> Tuple[Counter, Counter]:
    """자리 전용 바인딩은 더함(새 쪽) · 뺌(옛 쪽) 방향으로만 다중집합에서 뺀다 — 뺀 바인딩은 알림 한 줄."""
    added: Counter = (drop_new or Counter()) & (target_bag - base_bag)
    removed: Counter = (drop_old or Counter()) & (base_bag - target_bag)
    if not added and not removed:
        return base_bag, target_bag

    def label(bag: Counter) -> object:
        return sorted('%s%s' % (d, ' as ' + a if a else '') for (d, a) in bag) or '-'

    infos.append('메서드 이동 자리 전용 import 대조 밖 — %s:%d 더함 %s · 뺌 %s' % (path, line, label(added), label(removed)))
    return base_bag - removed, target_bag - added


def _compare_py(path: str, base_src: str, target_src: str, pairs: _Pairs,
                revs: Optional[Tuple[str, str]] = None) -> List[str]:
    try:
        base_tree: ast.Module = ast.parse(base_src)
        target_tree: ast.Module = ast.parse(target_src)
    except SyntaxError as error:
        raise DebtError('%s 파싱 실패 — %s' % (path, error))
    problems: List[str] = []
    base_segs = _segments(base_tree, None)
    target_segs = _segments(target_tree, pairs)
    marked = _mark_moves(path, base_src, target_src, base_tree, target_tree, pairs, revs)
    if marked is not None:
        base_src, target_src, base_tree = marked[0], marked[1], marked[2]
    for key in sorted(set(base_segs) | set(target_segs), key=repr):
        b_line, b_bag = base_segs.get(key, (0, Counter()))
        t_line, t_bag = target_segs.get(key, (0, Counter()))
        if marked is not None:
            b_bag, t_bag = _drop_site_imports(path, t_line or b_line, b_bag, t_bag, marked[3].get(key),
                                              marked[4].get(key), pairs.infos)
        if b_bag != t_bag:
            extra = sorted('%s%s' % (d, ' as ' + a if a else '') for (d, a) in (t_bag - b_bag))
            missing = sorted('%s%s' % (d, ' as ' + a if a else '') for (d, a) in (b_bag - t_bag))
            problems.append('%s:%d import 구간이 치환만으로 설명되지 않는다 — 더함 %s · 뺌 %s'
                            % (path, t_line or b_line, extra or '-', missing or '-'))
    try:
        rewritten: ast.Module = ast.parse(pairs.substitute(target_src))
    except SyntaxError:
        return problems + ['%s:1 역치환 뒤 파싱 불가 — 치환만의 변경이 아니다' % path]
    base_body: ast.Module = _DropImports().visit(base_tree)
    target_body: ast.Module = _DropImports().visit(rewritten)
    if ast.dump(base_body) != ast.dump(target_body):
        problems.append('%s:%d import 밖 본문이 치환만으로 설명되지 않는다(단언·호출 변경 포함)'
                        % (path, _first_diff(base_body, target_body)))
    return problems


def _compare_lines(path: str, base_src: str, target_src: str, pairs: _Pairs) -> List[str]:
    base_lines: List[str] = base_src.splitlines()
    target_lines: List[str] = target_src.splitlines()
    removed: List[str] = []
    added: List[Tuple[int, str]] = []
    matcher = difflib.SequenceMatcher(None, base_lines, target_lines, autojunk=False)
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op in ('replace', 'delete'):
            removed.extend(base_lines[i1:i2])
        if op in ('replace', 'insert'):
            added.extend((j + 1, target_lines[j]) for j in range(j1, j2))
    if Counter(removed) == Counter(pairs.substitute(line) for _n, line in added):
        return []
    return ['%s:%d 바뀐 줄이 치환만으로 설명되지 않는다' % (path, added[0][0] if added else 1)]


# ------------------------------------------------------------------ CLI


def _status_entries(root: Path, args: List[str]) -> List[str]:
    return [e for e in _git(root, args).decode('utf-8', 'replace').split('\0') if e]


def _is_ancestor(root: Path, older: str, newer: str) -> bool:
    result = subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', older, newer],
                            capture_output=True)
    if result.returncode not in (0, 1):
        raise DebtError('git merge-base --is-ancestor 실패 — %s'
                        % result.stderr.decode('utf-8', 'replace').strip())
    return result.returncode == 0


def _names(root: Path, a: str, b: str, pathspec: List[str]) -> Set[str]:
    out: bytes = _git(root, ['diff', '--no-renames', '--name-only', '-z', a, b, '--', *pathspec])
    return {p for p in out.decode('utf-8', 'surrogateescape').split('\0') if p}


Entry = Optional[Tuple[str, str]]      # (모드, blob) — 없음이면 None
Step = Tuple[str, str, Entry, Entry, bool, Entry]
# (커밋, 종류 S|F|U|M|T|X, 전, 후, 상류 경로인가, 상류 판 항목) — S = 슬라이스 0 대조 · F = 기능 슬라이스 커밋 ·
# U = 승인 병합이 들여온 그대로 · M = 승인 병합 안 레인 몫 · T = 0T 시험 전환 커밋 · X = 0T 취소 커밋(둘은 test_switch 기록이 있을 때만)


def _raw(root: Path, a: str, b: str, pathspec: List[str]) -> Dict[str, Tuple[Entry, Entry]]:
    """a → b 에서 바뀐 경로 → (a 판 항목, b 판 항목)."""
    out: List[str] = _git(root, ['diff', '--raw', '-z', '--no-renames', '--no-abbrev', a, b, '--',
                                 *pathspec]).decode('utf-8', 'surrogateescape').split('\0')
    found: Dict[str, Tuple[Entry, Entry]] = {}
    i: int = 0
    while i + 1 < len(out):
        meta: str = out[i]
        if not meta.startswith(':'):
            i += 1
            continue
        m1, m2, s1, s2 = meta[1:].split()[:4]
        found[out[i + 1]] = (None if set(m1) == {'0'} else (m1, s1), None if set(m2) == {'0'} else (m2, s2))
        i += 2
    return found


def _tree(root: Path, rev: str) -> Dict[str, Tuple[str, str]]:
    """판의 파일 → (모드, blob) — 저장소 최상위 기준 경로(diff 출력과 같은 표기)."""
    out: str = _git(root, ['ls-tree', '-r', '-z', '--full-name', rev, '--', '.']).decode('utf-8', 'surrogateescape')
    found: Dict[str, Tuple[str, str]] = {}
    for rec in out.split('\0'):
        if rec and '\t' in rec:
            meta, name = rec.split('\t', 1)
            mode, _kind, sha = meta.split()
            found[name] = (mode, sha)
    return found


def _chain(root: Path, base: str, target: str) -> List[Tuple[str, List[str]]]:
    """기준..대상 첫 부모 사슬(오래된 순) — (커밋, 부모 목록)."""
    lines: List[str] = _git(root, ['rev-list', '--reverse', '--first-parent', '--parents',
                                   '%s..%s' % (base, target)]).decode().splitlines()
    return [(ids[0], ids[1:]) for ids in (line.split() for line in lines)]


def _approved_merges(root: Path, folder: Optional[Path], base: str,
                     chain: List[Tuple[str, List[str]]]) -> Tuple[Dict[str, str], List[str]]:
    """발주자 승인 병합(`<산출물 폴더>/approved-merges.txt`) → {병합: 둘째 부모} · 알림.

    dddjango approved-merges 와 같은 뜻: 줄 `<SHA> [메모]`(빈 줄 · `//` 주석) · 두 부모 병합만 · 기준 이전 병합은
    판정 불참 · 기준..대상 첫 부모 사슬 밖이면 실행 불능 · `^2` 를 담은 ref 가 HEAD 가지(와 그 remote-tracking ·
    태그)뿐이면 역방향/합성 병합 의심 알림(exit 무변). 등재 병합이 있으면 얕은 이력이 아니어야 한다(기준이 대상의
    첫 부모 사슬 위인지는 --build 에서 호출 쪽이 먼저 본다)."""
    if folder is None:
        return {}, []
    listed: Path = folder / 'approved-merges.txt'
    if not listed.is_file():
        return {}, []
    in_range: Set[str] = {sha for sha, _parents in chain}
    head_ref: str = subprocess.run(['git', '-C', str(root), 'symbolic-ref', '-q', 'HEAD'],
                                   capture_output=True).stdout.decode().strip()
    head_branch: str = head_ref[len('refs/heads/'):] if head_ref.startswith('refs/heads/') else ''
    try:
        lines: List[str] = listed.read_text(encoding='utf-8').splitlines()
    except (OSError, UnicodeError) as error:
        raise DebtError('approved-merges.txt 를 읽을 수 없다 — %s' % error)
    approved: Dict[str, str] = {}
    notes: List[str] = []
    for raw in lines:
        line: str = raw.strip()
        if not line or line.startswith('//'):
            continue
        token: str = line.split(' ', 1)[0]
        if re.fullmatch(r'[0-9a-fA-F]{7,40}', token) is None:
            raise DebtError('approved-merges.txt 줄 형식 오류 %r — `<SHA> [메모]`(SHA 7~40 hex)' % raw)
        found = subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', '-q', token + '^{commit}'],
                               capture_output=True)
        if found.returncode != 0:
            raise DebtError('approved-merges.txt 의 %s 를 커밋으로 풀 수 없다' % token)
        sha: str = found.stdout.decode().strip()
        parents: List[str] = _git(root, ['rev-list', '--parents', '-n', '1', sha]).decode().split()[1:]
        if len(parents) != 2:
            raise DebtError('승인 병합 %s 의 부모가 %d개 — 두 부모 병합만 등재한다' % (sha[:12], len(parents)))
        if _is_ancestor(root, sha, base):
            notes.append('승인 병합 %s 는 기준 이전 — 판정 불참' % sha[:12])
            continue
        if sha not in in_range:
            raise DebtError('승인 병합 %s 가 기준..대상 첫 부모 사슬 밖 — 레인이 받은 병합이 아니다' % sha[:12])
        refs: List[str] = _git(root, ['for-each-ref', '--contains', parents[1],
                                      '--format=%(refname)']).decode().split()
        others: List[str] = [r for r in refs if r != head_ref and not r.startswith('refs/tags/')
                             and not (head_branch and r.startswith('refs/remotes/')
                                      and r[len('refs/remotes/'):].partition('/')[2] == head_branch)]
        if not others:
            notes.append('승인 병합 %s 의 ^2 %s 를 담은 ref 가 HEAD 가지뿐 — 역방향/합성 병합 의심(발주자 확인)'
                         % (sha[:12], parents[1][:12]))
        approved[sha] = parents[1]
    if approved and _git(root, ['rev-parse', '--is-shallow-repository']).decode().strip() == 'true':
        raise DebtError('얕은 이력 — 승인 병합 판정 불가(git fetch --unshallow 뒤 다시)')
    return approved, notes


def _records(root: Path, folder: Optional[Path], chain: List[Tuple[str, List[str]]]
             ) -> Tuple[Set[str], Dict[str, str], List[str], List[str]]:
    """build-state.json 슬라이스 기록 → (슬라이스 0 커밋 · 기능 커밋 → 슬라이스 이름 · 알림 · 어긋남).

    받는 값: 7~40 hex 이고 기준..대상 첫 부모 사슬 위 비병합 커밋으로 풀리는 것뿐(그 밖은 알리고 버린다 — 버린
    커밋은 슬라이스 0 대조). slices[0] 과 `slice-0` 이름 슬라이스가 슬라이스 0 이고, `mode: refactor`(리팩토링
    입구 — 동작 불변)이면 모든 기록이 슬라이스 0 이다. 양쪽 기록은 어긋남이고, 슬라이스 0 기록이 없거나 기능
    기록이 가장 이른 슬라이스 0 기록보다 앞이면 그 몫을 슬라이스 0 으로 본다."""
    if folder is None:
        return set(), {}, ['--build 없음 — 모든 커밋을 슬라이스 0 으로 · 모든 병합을 미승인으로 대조'], []
    path: Path = folder / 'build-state.json'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError) as error:
        raise DebtError('build-state.json 을 읽을 수 없다 — %s' % error)
    slices = data.get('slices') if isinstance(data, dict) else None
    if not isinstance(slices, list) or not all(isinstance(x, dict) for x in slices):
        raise DebtError('build-state.json 의 slices 가 객체 목록이 아니다')
    refactor: bool = data.get('mode') == 'refactor'
    order: Dict[str, int] = {sha: i for i, (sha, _parents) in enumerate(chain)}
    merges: Set[str] = {sha for sha, parents in chain if len(parents) >= 2}
    zero: Set[str] = set()
    feature: Dict[str, str] = {}
    notes: List[str] = []
    for index, item in enumerate(slices):
        name: str = item.get('name') if isinstance(item.get('name'), str) else 'slices[%d]' % index
        listed = item.get('commits', [])
        values: List[object] = [item.get('commit')] + (listed if isinstance(listed, list) else [listed])
        for value in values:
            if value is None or value == '':
                continue
            text: str = value.strip() if isinstance(value, str) else repr(value)
            if not isinstance(value, str) or re.fullmatch(r'[0-9a-fA-F]{7,40}', text) is None:
                notes.append('build-state %s 기록 %r 거부 — 커밋 해시(7~40 hex)만 받는다' % (name, text[:40]))
                continue
            found = subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', '-q', text + '^{commit}'],
                                   capture_output=True)
            sha: str = found.stdout.decode().strip()
            if found.returncode != 0:
                notes.append('build-state %s 기록 %s 를 풀 수 없다 — 버림' % (name, text[:12]))
            elif sha not in order:
                notes.append('build-state %s 기록 %s 가 기준..대상 첫 부모 사슬 밖 — 버림' % (name, sha[:12]))
            elif sha in merges:
                notes.append('build-state %s 기록 %s 는 병합 — 버림(병합은 승인 목록으로만 가른다)' % (name, sha[:12]))
            elif index == 0 or name.startswith('slice-0') or refactor:
                if index != 0 and not name.startswith('slice-0'):
                    notes.append('build-state mode=refactor — %s 기록 %s 를 슬라이스 0 으로 대조' % (name, sha[:12]))
                zero.add(sha)
            else:
                feature.setdefault(sha, name)
    problems: List[str] = []
    for sha in sorted(set(feature) & zero, key=order.get):
        problems.append('build-state 기록 모순 — %s 가 slices[0] 과 %s 양쪽에 있다(슬라이스 0 으로 대조 · 한쪽을 '
                        '지운 뒤 다시)' % (sha[:12], feature.pop(sha)))
    if not zero:
        raise DebtError('build-state slices[0] 에 기준..대상 첫 부모 사슬 위 슬라이스 0 커밋 기록이 없다 — 적은 뒤 다시%s'
                        % ('' if not notes else '(' + ' · '.join(notes) + ')'))
    first: int = min(order[sha] for sha in zero)
    for sha in [s for s in feature if order[s] < first]:
        notes.append('build-state %s 기록 %s 가 첫 슬라이스 0 커밋보다 앞 — 슬라이스 0 으로 대조' % (feature.pop(sha), sha[:12]))
    return zero, feature, notes, problems


def _history(root: Path, chain: List[Tuple[str, List[str]]], outside: List[str], approved: Dict[str, str],
             feature: Dict[str, str], switch: Optional[Dict[str, str]] = None
             ) -> Tuple[Dict[str, List[Step]], Dict[str, str], List[str]]:
    """첫 부모 사슬의 경로별 걸음 · 상류 판(경로 → 상류가 그 경로를 바꾼 마지막 승인 병합의 둘째 부모) · 알림.
    switch(커밋 → 'T' 0T · 'X' 취소)에 든 비병합 커밋의 걸음은 그 종류다."""
    empty: str = _git(root, ['hash-object', '-t', 'tree', '/dev/null']).decode().strip()
    steps: Dict[str, List[Step]] = {}
    inflow: Dict[str, str] = {}
    notes: List[str] = []
    for sha, parents in chain:
        if sha in approved:
            p1, p2 = parents
            found = subprocess.run(['git', '-C', str(root), 'merge-base', p1, p2], capture_output=True)
            if found.returncode != 0:
                raise DebtError('승인 병합 %s 의 공통 조상을 찾지 못함 — 판정 불가(얕은 이력이면 git fetch '
                                '--unshallow 뒤 다시)' % sha[:12])
            changed = _raw(root, p1, sha, outside)
            upstream: Set[str] = _names(root, found.stdout.decode().strip(), p2, outside)
            versus = _raw(root, p2, sha, outside)
            lane: int = 0
            for path in upstream:
                inflow[path] = p2
            for path, (before, after) in changed.items():
                up: bool = path in upstream
                kind: str = 'U' if up and path not in versus else 'M'
                lane += kind == 'M'
                steps.setdefault(path, []).append((sha, kind, before, after, up,
                                                   versus[path][0] if up and path in versus else None))
            for path in (upstream & set(versus)) - set(changed):
                # 병합이 상류 변경을 버리고 레인 판을 지킴 — 상류 판 대비 레인 몫
                lane += 1
                kept: Entry = versus[path][1]
                steps.setdefault(path, []).append((sha, 'M', kept, kept, True, versus[path][0]))
            notes.append('승인 병합 %s(^2 %s) — 상류 변경 %d경로 · 병합 안 레인 몫 %d경로'
                         % (sha[:12], p2[:12], len(upstream), lane))
            continue
        if len(parents) >= 2:
            notes.append('병합 %s 승인 목록 밖 — 들여온 변경을 슬라이스 0 으로 대조(main 받기면 발주자가 '
                         'approved-merges.txt 에 적은 뒤 다시)' % sha[:12])
        kind = 'F' if len(parents) == 1 and sha in feature else 'S'
        if switch and sha in switch:
            kind = switch[sha]
        for path, (before, after) in _raw(root, parents[0] if parents else empty, sha, outside).items():
            steps.setdefault(path, []).append((sha, kind, before, after, False, None))
    return steps, inflow, notes


def _status(before: Entry, after: Entry) -> str:
    # 실행 비트만 다르면 M(git 과 같다) — 종류(일반 · 심볼릭 링크 · 하위 모듈)가 바뀔 때만 T
    return 'A' if before is None else 'D' if after is None else 'T' if before[0][:2] != after[0][:2] else 'M'


def _contrast(root: Path, path: str, before: Entry, after: Entry, pairs: _Pairs,
              revs: Optional[Tuple[str, str]] = None) -> List[str]:
    """테스트 파일 한 구간(전 → 후 · revs = 두 판의 커밋)이 치환뿐인가 — 어긋남 줄 목록."""
    if before == after:
        return []
    status: str = _status(before, after)
    if status != 'M':
        return ['%s 치환이 아닌 변경(%s — 새 파일·삭제·개명·타입 변경)' % (path, status)]
    assert before is not None and after is not None
    if before[1] == after[1]:
        return []           # 실행 비트만 바뀜
    old: bytes = _git(root, ['cat-file', 'blob', before[1]])
    new: bytes = _git(root, ['cat-file', 'blob', after[1]])
    try:
        if b'\0' in old or b'\0' in new:
            raise UnicodeDecodeError('utf-8', b'', 0, 1, 'binary')
        base_src, target_src = old.decode('utf-8'), new.decode('utf-8')
    except UnicodeDecodeError:
        return ['%s 이진 파일 변경 — 치환으로 설명할 수 없다' % path]
    if path.endswith('.py'):
        return _compare_py(path, base_src, target_src, pairs, revs)
    return _compare_lines(path, base_src, target_src, pairs)


def _clean(root: Path, path: str, before: Entry, after: Entry, pairs: _Pairs,
           revs: Optional[Tuple[str, str]] = None) -> bool:
    try:
        return not _contrast(root, path, before, after, pairs, revs)
    except DebtError:
        return False


# ------------------------------------------------------------------ 메서드 이동 제품 쪽 확인


def _forward(pairs: _Pairs, module: str) -> Set[str]:
    """옛 모듈 점 경로 → 대상 판에서 그 모듈이 있을 자리들(그대로 · 개명 쌍 · `이름:` 쌍을 정방향으로)."""
    found: Set[str] = {module}
    for table in (pairs.prefix, pairs.full):
        for new, old in table.items():
            if module == old or module.startswith(old + '.'):
                found.add(new + module[len(old):])
    return found


def _def_dump(source: Optional[str], node: Func, pairs: Optional[_Pairs]) -> Optional[str]:
    """메서드 def(decorator · 시그니처 · 본문)의 AST 덤프 — 이름은 지운다 · pairs 가 있으면 승인 대응을 거꾸로 적용한 뒤."""
    if source is None:
        return None
    lines: List[str] = source.split('\n')
    first: int = min([node.lineno] + [d.lineno for d in node.decorator_list])
    text: str = 'class _:\n' + '\n'.join(lines[first - 1:node.end_lineno])
    if pairs is not None:
        text = pairs.substitute(text)
    try:
        method = ast.parse(text).body[0].body[0]
    except (SyntaxError, IndexError, AttributeError):
        return None
    method.name = '_'
    return ast.dump(method)


def _check_moves(pairs: _Pairs, base: str, target: str) -> Tuple[List[str], List[str]]:
    """메서드 이동 행마다 제품 쪽 확인(git blob) — (어긋남, 알림). 기준 판의 옛 def · 대상 판의 새 def · 대상 판에
    옛 def 없음. 옮긴 본문(승인 대응 뒤)이 다르면 알림만."""
    problems: List[str] = []
    notes: List[str] = []
    resolver: Optional[_Resolver] = pairs.resolver
    if resolver is None:
        return problems, notes
    for move in pairs.moves:
        label: str = move.label()
        notes.append('메서드 이동 %s — 승인 시험 함수 %d' % (label, move.functions()))
        old_defs: List[Func] = resolver.methods(base, move.old_class, move.old_method)
        new_defs: List[Func] = resolver.methods(target, move.new_class, move.new_method)
        if not old_defs:
            problems.append('메서드 이동 %s — 기준 판 %s 에 옛 메서드 def 가 없다' % (label, base[:12]))
        if not new_defs:
            problems.append('메서드 이동 %s — 대상 판 %s 에 새 메서드 def 가 없다' % (label, target[:12]))
        module, name = move.old_class.rsplit('.', 1)
        if any(resolver.methods(target, '%s.%s' % (m, name), move.old_method) for m in sorted(_forward(pairs, module))):
            problems.append('메서드 이동 %s — 대상 판 %s 에 옛 메서드 def 가 남아 있다(이동이 아니다)' % (label, target[:12]))
        if old_defs and new_defs:
            before = _def_dump(resolver.source(base, module), old_defs[-1], None)
            after = _def_dump(resolver.source(target, move.new_class.rsplit('.', 1)[0]), new_defs[-1], pairs)
            if before is None or before != after:
                notes.append('메서드 이동 %s — 옮긴 본문 다름(동작 불변 근거는 명세 · 감수)' % label)
    return problems, notes


# ------------------------------------------------------------------ 0T 시험 전환

_SWITCH_STATES: Tuple[str, ...] = ('prepared', 'verifying', 'verified', 'cancelled')
_PATCH_WORDS: Set[str] = {'mock', 'patch', 'monkeypatch', 'mocker', 'setattr', 'delattr', 'setitem', 'delitem', 'setenv',
                          'delenv', 'spy', 'stub', 'MagicMock', 'Mock', 'AsyncMock', 'NonCallableMock', 'PropertyMock',
                          'create_autospec', 'mock_open', '__setattr__', '__delattr__', '__dict__'}


def _switch_record(root: Path, folder: Optional[Path], chain: List[Tuple[str, List[str]]], zero: Set[str],
                   feature: Dict[str, str], switches: List[_TestSwitch]) -> Tuple[Dict[str, str], Optional[str], List[str]]:
    """build-state slices[0].test_switch → (커밋 → 'T' 0T · 'X' 취소, 상태, 어긋남). 기록이 없으면 ({}, None, [])."""
    if folder is None:
        return {}, None, []
    data = json.loads((folder / 'build-state.json').read_text(encoding='utf-8'))
    record = data['slices'][0].get('test_switch')
    if record is None:
        return {}, None, []
    if not isinstance(record, dict):
        raise DebtError('build-state slices[0].test_switch 가 객체가 아니다')
    state = record.get('state')
    if state not in _SWITCH_STATES:
        raise DebtError('build-state slices[0].test_switch.state 는 %s 가운데 하나다 — %r' % (' · '.join(_SWITCH_STATES), state))
    order: Dict[str, int] = {sha: i for i, (sha, _parents) in enumerate(chain)}
    parents_of: Dict[str, List[str]] = dict(chain)
    problems: List[str] = []

    def commits(field: str) -> List[str]:
        values = record.get(field, [])
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            raise DebtError('build-state slices[0].test_switch.%s 가 커밋 해시 목록이 아니다' % field)
        found: List[str] = []
        for value in values:
            text: str = value.strip()
            sha: str = ''
            if re.fullmatch(r'[0-9a-fA-F]{7,40}', text):
                result = subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', '-q', text + '^{commit}'],
                                        capture_output=True)
                sha = result.stdout.decode().strip() if result.returncode == 0 else ''
            if not sha:
                problems.append('build-state test_switch.%s 기록 %s 를 커밋으로 풀 수 없다' % (field, text[:40]))
            elif sha not in order:
                problems.append('build-state test_switch.%s 기록 %s 가 기준..대상 첫 부모 사슬 밖' % (field, sha[:12]))
            elif len(parents_of[sha]) != 1:
                problems.append('build-state test_switch.%s 기록 %s 는 병합이다 — 0T · 취소는 비병합 커밋' % (field, sha[:12]))
            else:
                found.append(sha)
        return found

    tees: List[str] = commits('commits')
    cancels: List[str] = commits('cancel_commits')
    kinds: Dict[str, str] = {sha: 'T' for sha in tees}
    for sha in tees:
        if sha not in zero:
            problems.append('0T 커밋 %s 가 slices[0] commits 에 없다 — 0T 는 슬라이스 0 커밋이다' % sha[:12])
        if sha in feature:
            problems.append('build-state 기록 모순 — 0T 커밋 %s 가 기능 슬라이스 %s 에도 있다' % (sha[:12], feature[sha]))
    codes: List[str] = sorted((sha for sha in zero if sha not in kinds and sha not in cancels), key=order.get)
    for sha in tees:
        if codes and order[sha] > order[codes[0]]:
            problems.append('0T 커밋 %s 가 첫 0C 커밋 %s 뒤 — 0T 는 첫 코드 커밋 앞에서 한 번' % (sha[:12], codes[0][:12]))
    if state in ('prepared', 'verifying') and codes:
        problems.append('0T 검증 전(state=%s)인데 0C 커밋 %s 가 있다 — 0C 는 검증(verified) 뒤' % (state, codes[0][:12]))
    # 기록 없는 커밋도 슬라이스 0 으로 대조한다 — 0T 보다 앞선 레인 커밋(비병합)이 제품을 바꿨으면 0T 가 기준 판 제품 위가 아니다
    last: int = max((order[sha] for sha in tees), default=0) if state != 'cancelled' else 0
    for sha, parents in chain[:last]:
        if sha in kinds or sha in zero or len(parents) != 1:
            continue        # 0T 자신 · 기록된 0C(위 «첫 0C 뒤» 로 잡힌다) · 병합은 여기서 보지 않는다
        early: List[str] = sorted(_names(root, parents[0], sha, ['web/']))
        if early:
            problems.append('0T 앞 커밋 %s 가 web/ 을 바꿨다(%s%s) — 0T 는 첫 코드 커밋 앞에서 한 번'
                            % (sha[:12], early[0], ' 외 %d' % (len(early) - 1) if len(early) > 1 else ''))
    allowed: Set[str] = {switch.path for switch in switches}
    touched: Set[str] = set()
    for sha in tees:
        parent: str = parents_of[sha][0]
        web: List[str] = sorted(_names(root, parent, sha, ['web/']))
        if web:
            problems.append('0T 커밋 %s 가 web/ 을 바꿨다(%s%s) — 0T 는 제품을 고정한다'
                            % (sha[:12], web[0], ' 외 %d' % (len(web) - 1) if len(web) > 1 else ''))
        changed: Set[str] = _names(root, parent, sha, ['.', ':(exclude)web', ':(exclude).dddjango-web'])
        touched |= changed | set(web)
        outside: List[str] = sorted(changed - allowed)
        if outside and state != 'cancelled':
            problems.append('0T 커밋 %s 가 시험 전환 행 밖 파일을 바꿨다(%s%s) — 명세 `시험 전환:` 행의 시험 파일만'
                            % (sha[:12], outside[0], ' 외 %d' % (len(outside) - 1) if len(outside) > 1 else ''))
    if state != 'cancelled':
        if cancels:
            problems.append('build-state 기록 모순 — 취소 커밋 %s 가 있는데 state=%s' % (cancels[0][:12], state))
        return kinds, state, problems
    if not cancels:
        problems.append('0T 취소(state=cancelled)인데 취소 커밋이 없다(cancel_commits)')
    for sha in cancels:
        if sha in kinds:
            problems.append('build-state 기록 모순 — %s 가 0T 커밋이자 취소 커밋이다' % sha[:12])
            continue
        if any(order[sha] < order[t] for t in tees):
            problems.append('취소 커밋 %s 가 0T 커밋보다 앞' % sha[:12])
        extra: List[str] = sorted(_names(root, parents_of[sha][0], sha, ['.', ':(exclude).dddjango-web']) - touched)
        if extra:
            problems.append('취소 커밋 %s 가 0T 가 바꾸지 않은 경로를 바꿨다(%s) — 취소는 0T 의 정확한 역 커밋' % (sha[:12], extra[0]))
        kinds[sha] = 'X'
    return kinds, state, problems


def _drop_cancelled(path: str, history: List[Step], base_entry: Entry) -> Tuple[List[Step], List[str]]:
    """취소된 0T — 0T · 취소 걸음이 잇달고 합이 무변이면 둘 다 대조에서 뺀다(아니면 슬라이스 0 대조 걸음으로 남긴다)."""
    marks: List[int] = [i for i, step in enumerate(history) if step[1] in ('T', 'X')]
    if not marks:
        return history, []
    first, last = marks[0], marks[-1]
    start: Entry = base_entry if first == 0 else history[first][2]
    if all(history[i][1] in ('T', 'X') for i in range(first, last + 1)) and start == history[last][3]:
        return history[:first] + history[last + 1:], []
    shas: str = ' '.join(dict.fromkeys(history[i][0][:12] for i in marks))
    return ([(step[0], 'S') + step[2:] if step[1] in ('T', 'X') else step for step in history],
            ['%s 0T 취소가 시험 파일을 되돌리지 않았다(0T · 취소 커밋 %s) — 둘의 합이 무변일 때만 대조에서 뺀다' % (path, shas)])


def _statements(st: ast.stmt) -> Iterator[ast.stmt]:
    """문과 그 안의 문(차례대로) — 중첩 함수 · 클래스 본문은 들어가지 않는다."""
    yield st
    if isinstance(st, _NESTED_SCOPES):
        return
    for _field, value in ast.iter_fields(st):
        for item in (value if isinstance(value, list) else [value]):
            if isinstance(item, ast.stmt):
                yield from _statements(item)
            elif isinstance(item, ast.AST) and isinstance(getattr(item, 'body', None), list):
                for sub in item.body:
                    if isinstance(sub, ast.stmt):
                        yield from _statements(sub)


def _assertions(names: _TestNames, func: Func) -> List[Tuple[int, ast.stmt]]:
    """단언 문장(`assert` · `with pytest.raises/warns` · `.assert_*()`) — [(그 문이 든 최상위 문 순번, 문)]."""
    out: List[Tuple[int, ast.stmt]] = []
    for index, top in enumerate(func.body):
        for st in _statements(top):
            if isinstance(st, ast.Assert):
                out.append((index, st))
            elif isinstance(st, (ast.With, ast.AsyncWith)) and any(
                    isinstance(item.context_expr, ast.Call) and _dotted(item.context_expr.func) is not None
                    and names.expr(func, item.context_expr.func) in ('pytest.raises', 'pytest.warns') for item in st.items):
                out.append((index, st))
            elif (isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) and isinstance(st.value.func, ast.Attribute)
                  and st.value.func.attr.startswith('assert_')):
                out.append((index, st))
    return out


def _behaviors(names: _TestNames, func: Func, target: str) -> Tuple[List[Tuple[int, ast.stmt]], int]:
    """행위 문장(최상위 `<이름>[: T] = <대상>(…)`)과 함수 안 그 대상 호출 수."""
    calls: int = sum(1 for node, _path in _walk_func(func) if isinstance(node, ast.Call)
                     and _dotted(node.func) is not None and names.expr(func, node.func) == target)
    hits: List[Tuple[int, ast.stmt]] = []
    for index, st in enumerate(func.body):
        name: Optional[ast.expr] = (st.targets[0] if isinstance(st, ast.Assign) and len(st.targets) == 1
                                    else st.target if isinstance(st, ast.AnnAssign) else None)
        value: Optional[ast.expr] = st.value if isinstance(st, (ast.Assign, ast.AnnAssign)) else None
        if (isinstance(name, ast.Name) and isinstance(value, ast.Call) and _dotted(value.func) is not None
                and names.expr(func, value.func) == target):
            hits.append((index, st))
    return hits, calls


def _result_of(st: ast.stmt) -> Tuple[str, Optional[str]]:
    if isinstance(st, ast.AnnAssign):
        return st.target.id, ast.dump(st.annotation)
    return st.targets[0].id, None


def _leaves(node: ast.AST) -> List[str]:
    """값 잎 — 글자 상수 · 이름 · 점 경로(호출은 인자 · 키워드 값만 — 부르는 대상은 빼고)."""
    if isinstance(node, ast.Constant):
        return [repr(node.value)]
    dotted: Optional[str] = _dotted(node)
    if dotted is not None:
        return [dotted]
    if isinstance(node, ast.Call):
        children: List[ast.AST] = list(node.args) + [k.value for k in node.keywords]
    else:
        children = [c for c in ast.iter_child_nodes(node) if isinstance(c, ast.expr)]
        children += [c.value for c in ast.iter_child_nodes(node) if isinstance(c, ast.keyword)]
    return [leaf for child in children for leaf in _leaves(child)]


def _target_root(target: ast.expr) -> Optional[ast.Name]:
    while isinstance(target, (ast.Attribute, ast.Subscript)):
        target = target.value
    return target if isinstance(target, ast.Name) else None


def _simple_assign(st: ast.stmt) -> bool:
    """단순 대입 — 대상 하나(이름 · 이름에서 시작하는 속성 · 첨자)."""
    if isinstance(st, ast.Assign) and len(st.targets) == 1:
        target: ast.expr = st.targets[0]
    elif isinstance(st, ast.AnnAssign) and st.value is not None:
        target = st.target
    else:
        return False
    return isinstance(target, ast.Name) or (isinstance(target, (ast.Attribute, ast.Subscript))
                                            and _target_root(target) is not None)


def _is_patch(names: _TestNames, func: Func, st: ast.stmt) -> bool:
    """patch · mock 문장 — mock · patch 이름을 (부르지 않고 읽기만 해도) 담거나, 함수 지역 대입이 아닌 객체(import ·
    인자 · 모듈 이름)의 속성 · 첨자를 바꾸거나, return_value · side_effect 를 바꾼다."""
    for node in ast.walk(st):
        if isinstance(node, ast.Attribute) and node.attr in _PATCH_WORDS:
            return True
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            resolved: str = names.name(func, node.id) or ''
            if node.id in _PATCH_WORDS or resolved.startswith(('unittest.mock', 'pytest_mock', 'mock.', 'fixture:')):
                return True
    targets: List[ast.expr] = (st.targets if isinstance(st, ast.Assign)
                               else [st.target] if isinstance(st, (ast.AnnAssign, ast.AugAssign)) else [])
    local: Dict[str, List[Binding]] = names.scope(func)
    for target in targets:
        if isinstance(target, ast.Attribute) and target.attr in ('return_value', 'side_effect'):
            return True
        root: Optional[ast.Name] = _target_root(target)
        if not isinstance(target, (ast.Attribute, ast.Subscript)):
            continue
        # 함수 안에서 대입으로 만든 객체만 고쳐도 된다 — 인자 · import · import_module 로 얻은 모듈은 바깥 객체다
        assigned: bool = root is not None and bool(local.get(root.id)) and all(
            kind in ('other', 'module_call') for kind, _value in local[root.id])
        if root is None or not assigned or names.name(func, root.id) is not None:
            return True
    return False


def _bound_names(st: ast.stmt) -> Set[str]:
    if isinstance(st, ast.Import):
        return {a.asname or a.name.split('.')[0] for a in st.names}
    if isinstance(st, ast.ImportFrom):
        return {a.asname or a.name for a in st.names}
    targets: List[ast.expr] = st.targets if isinstance(st, ast.Assign) else [st.target] if isinstance(st, ast.AnnAssign) else []
    return {t.id for t in targets if isinstance(t, ast.Name)}


def _used(names: _TestNames, func: Func, name: str) -> bool:
    """함수 안에서 name 을 읽는가 — Load · `typing.cast("<…>")` 의 형식 글자 · 글자 형식 표기."""
    word = re.compile(r'(?<![\w.])%s(?!\w)' % re.escape(name))
    for node in ast.walk(func):
        if isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, ast.Load):
            return True
        if (isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str) and _dotted(node.func) is not None
                and names.expr(func, node.func) in ('typing.cast', 'typing_extensions.cast')
                and word.search(node.args[0].value)):
            return True
        if (isinstance(node, ast.AnnAssign) and isinstance(node.annotation, ast.Constant)
                and isinstance(node.annotation.value, str) and word.search(node.annotation.value)):
            return True
    return False


def _only_in(func: Func, st: ast.stmt, behavior: ast.stmt) -> bool:
    """import 문의 바인딩이 모두 행위 문장 안에서만 읽힌다."""
    for name in _bound_names(st):
        total: int = sum(1 for n in ast.walk(func) if isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, ast.Load))
        inside: int = sum(1 for n in ast.walk(behavior)
                          if isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, ast.Load))
        if inside == 0 or inside != total:
            return False
    return True


def _switch_reasons(funcs: Tuple[Func, Func], names: Tuple[_TestNames, _TestNames],
                    row: _TestSwitch) -> List[Tuple[int, str]]:
    """시험 함수 하나의 0T 대조 — [(행, 사유)]. 규칙: 함수 머리 같음 · 단언 차례까지 같음 · patch · mock 문장 차례와
    위치(행위 앞 · 뒤) 같음 · 행위 문장 양쪽 하나씩(새 행위는 첫 단언 앞) · 대응 밖 문장은 순서 · 제어 구조까지 같음 ·
    뺀 문장 = 옛 행위와 그것만 쓰던 함수 안 import · 더한 문장 = 새 행위 앞 import · 단순 대입(patch 아님 · 단언이 읽는
    이름을 새로 바인딩하지 않음 · 더한 import 는 쓰임) · 옛 행위 인자의 값 잎 ⊆ 더한 문장 · 새 행위의 값 잎."""
    old_func, new_func = funcs
    reasons: List[Tuple[int, str]] = []

    def head(func: Func) -> Tuple:
        return (type(func).__name__, ast.dump(func.args), [ast.dump(d) for d in func.decorator_list],
                ast.dump(func.returns) if func.returns else None,
                [ast.dump(t) for t in getattr(func, 'type_params', [])])

    if head(old_func) != head(new_func):
        reasons.append((new_func.lineno, '함수 머리(decorator · 인자 · 반환 표기)가 다르다'))
    old_target: str = names[0].resolver.canonical(names[0].rev, row.old) or row.old
    new_target: str = names[1].resolver.canonical(names[1].rev, row.new) or row.new
    old_hits, old_calls = _behaviors(names[0], old_func, old_target)
    new_hits, new_calls = _behaviors(names[1], new_func, new_target)
    stray: int = _behaviors(names[1], new_func, names[1].resolver.canonical(names[1].rev, row.old) or row.old)[1]
    if len(old_hits) != 1 or old_calls != 1:
        reasons.append((new_func.lineno, '옛 판의 옛 행위 문장(`<이름> = %s(…)`)이 하나가 아니다(문장 %d · 호출 %d)'
                        % (row.old, len(old_hits), old_calls)))
    if len(new_hits) != 1 or new_calls != 1:
        reasons.append((new_func.lineno, '새 행위 문장(`<이름> = %s(…)`)이 하나가 아니다(문장 %d · 호출 %d)'
                        % (row.new, len(new_hits), new_calls)))
    if stray:
        reasons.append((new_func.lineno, '새 판이 옛 대상 %s 를 아직 부른다' % row.old))
    if len(old_hits) != 1 or len(new_hits) != 1 or old_calls != 1 or new_calls != 1 or stray:
        return reasons
    (i_old, b_old), (i_new, b_new) = old_hits[0], new_hits[0]
    if _result_of(b_old) != _result_of(b_new):
        reasons.append((b_new.lineno, '행위 결과 이름 · 표기가 다르다'))
    asserts = (_assertions(names[0], old_func), _assertions(names[1], new_func))
    old_dumps: List[str] = [ast.dump(st) for _i, st in asserts[0]]
    new_dumps: List[str] = [ast.dump(st) for _i, st in asserts[1]]
    if old_dumps != new_dumps:
        k: int = next((k for k, (a, b) in enumerate(zip(old_dumps, new_dumps)) if a != b), min(len(old_dumps), len(new_dumps)))
        line: int = asserts[1][k][1].lineno if k < len(asserts[1]) else new_func.lineno
        reasons.append((line, '단언 문장이 다르다(차례 포함)'))
    if asserts[1] and i_new > asserts[1][0][0]:
        reasons.append((b_new.lineno, '새 행위가 첫 단언 뒤에 있다'))
    old_body: List[ast.stmt] = old_func.body
    new_body: List[ast.stmt] = new_func.body
    removed: List[int] = []
    added: List[int] = []
    matched: List[Tuple[int, int]] = []
    matcher = difflib.SequenceMatcher(None, [ast.dump(s) for s in old_body], [ast.dump(s) for s in new_body], autojunk=False)
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == 'equal':
            matched.extend(zip(range(i1, i2), range(j1, j2)))
        else:
            removed.extend(range(i1, i2))
            added.extend(range(j1, j2))
    for i in removed:
        st: ast.stmt = old_body[i]
        if i != i_old and not (isinstance(st, (ast.Import, ast.ImportFrom)) and _only_in(old_func, st, b_old)):
            reasons.append((new_func.lineno, '뺀 문장(옛 판 %d행)이 옛 행위 · 그것만 쓰던 함수 안 import 가 아니다' % st.lineno))
    result_name: str = _result_of(b_new)[0]
    read: Set[str] = {n.id for _i, st in asserts[1] for n in ast.walk(st)
                      if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)} - {result_name}
    new_leaves: Counter = Counter(_leaves(b_new.value))
    # 속성 · 첨자 대입으로 고쳐도 되는 객체 — 더한 문장이 새로 만든 이름과 새 행위에 넘기는 이름뿐(단언이 읽는 객체는 아님)
    prepared: Set[str] = {leaf.split('.')[0] for leaf in new_leaves} | {
        name for j in added if j != i_new for name in _bound_names(new_body[j])}
    # 더한 문장이 바인딩해도 되는 이름 — 옛 판 모듈 · 함수에 없고 옛 함수가 읽지도 않던 새 이름뿐(남은 문장의 뜻을 바꾸지 않게)
    taken: Set[str] = set(names[0].module) | set(names[0].scope(old_func)) | {
        n.id for n in ast.walk(old_func) if isinstance(n, ast.Name)}
    for j in added:
        st = new_body[j]
        if j == i_new:
            continue
        if j > i_new:
            reasons.append((st.lineno, '더한 문장이 새 행위 뒤에 있다'))
        is_import: bool = isinstance(st, (ast.Import, ast.ImportFrom))
        if not is_import and not _simple_assign(st):
            reasons.append((st.lineno, '더한 문장이 import · 단순 대입이 아니다'))
            continue
        if _is_patch(names[1], new_func, st):
            reasons.append((st.lineno, '더한 문장이 patch · mock 이다'))
        rebound: Set[str] = _bound_names(st) & read
        if rebound:
            reasons.append((st.lineno, '더한 문장이 단언이 읽는 이름 %s 를 새로 바인딩한다' % ', '.join(sorted(rebound))))
        reused: Set[str] = (_bound_names(st) & taken) - rebound
        if reused:
            reasons.append((st.lineno, '더한 문장이 이미 있는 이름 %s 를 다시 바인딩한다' % ', '.join(sorted(reused))))
        if is_import:
            unused: List[str] = sorted(n for n in _bound_names(st) if not _used(names[1], new_func, n))
            if unused:
                reasons.append((st.lineno, '더한 import %s 가 쓰이지 않는다' % ', '.join(unused)))
            continue
        target: ast.expr = st.targets[0] if isinstance(st, ast.Assign) else st.target
        root: Optional[ast.Name] = _target_root(target)
        if not isinstance(target, ast.Name) and root is not None and (root.id in read or root.id not in prepared):
            reasons.append((st.lineno, '더한 문장이 새 준비 · 새 행위 입력이 아닌 객체 %s 를 고친다' % root.id))
        new_leaves.update(_leaves(st.value))
    for i, j in matched:
        if _is_patch(names[0], old_func, old_body[i]) and (i < i_old) != (j < i_new):
            reasons.append((new_body[j].lineno, 'patch · mock 문장의 위치(행위 앞 · 뒤)가 바뀌었다'))
    missing: Counter = Counter(_leaves(b_old.value)) - new_leaves
    if missing:
        reasons.append((b_new.lineno, '옛 행위 입력 값 %s 이 새 준비 · 행위에 없다' % ', '.join(sorted(missing))))
    return reasons


def _contrast_switch(root: Path, path: str, before: Entry, after: Entry, pairs: _Pairs,
                     revs: Tuple[str, str]) -> List[str]:
    """0T 걸음 한 구간(전 → 후) — 명세 `시험 전환:` 행의 시험 함수마다 _switch_reasons · 행 밖 모듈 내용 같음."""
    if before == after:
        return []
    status: str = _status(before, after)
    if status != 'M':
        return ['%s 0T 시험 전환 — 시험 파일 수정이 아닌 변경(%s)' % (path, status)]
    assert before is not None and after is not None
    if before[1] == after[1]:
        return []
    if not path.endswith('.py'):
        return ['%s 0T 시험 전환 — .py 시험 파일만 전환한다' % path]
    try:
        trees: Tuple[ast.Module, ...] = tuple(ast.parse(_git(root, ['cat-file', 'blob', entry[1]]).decode('utf-8'))
                                              for entry in (before, after))
    except (SyntaxError, UnicodeDecodeError, ValueError) as error:
        raise DebtError('%s 파싱 실패 — %s' % (path, error))
    rows: Dict[str, _TestSwitch] = {switch.func: switch for switch in pairs.switches if switch.path == path}
    if not rows or pairs.resolver is None:
        return ['%s:1 0T 시험 전환 — 명세 `시험 전환:` 행에 없는 시험 파일이다' % path]
    problems: List[str] = []
    outlines: List[List[object]] = [[('행', st.name) if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef))
                                     and st.name in rows else ast.dump(st) for st in tree.body] for tree in trees]
    if outlines[0] != outlines[1]:
        k: int = next((k for k, (a, b) in enumerate(zip(*outlines)) if a != b), min(map(len, outlines)))
        line: int = trees[1].body[k].lineno if k < len(trees[1].body) else 1
        problems.append('%s:%d 0T 시험 전환 — 행에 적힌 함수 밖 모듈 내용이 다르다' % (path, line))
    names: Tuple[_TestNames, _TestNames] = (_TestNames(trees[0], pairs.resolver, revs[0]),
                                            _TestNames(trees[1], pairs.resolver, revs[1]))
    for func_name in sorted(rows):
        funcs = (_top_function(trees[0], func_name), _top_function(trees[1], func_name))
        if funcs[0] is None or funcs[1] is None:
            problems.append('%s:1 0T 시험 전환 %s — 최상위 함수가 양쪽 판에 하나씩 있어야 한다' % (path, func_name))
            continue
        problems.extend('%s:%d 0T 시험 전환 %s — %s' % (path, line, func_name, reason)
                        for line, reason in dict.fromkeys(_switch_reasons(funcs, names, rows[func_name])))
    return problems


def _is_doc(path: str) -> bool:
    """대조하지 않는 비테스트 `.md` — 발주·보고 문서 자리(최상위 docs/ · .dddjango/ · 저장소 루트). 루트의
    에이전트 지침(CLAUDE.md · AGENTS.md — 대소문자 무시)은 문서 자리가 아니다."""
    return path.lower().endswith('.md') and (path.startswith(('docs/', '.dddjango/')) or (
        '/' not in path and path.upper() not in ('CLAUDE.MD', 'AGENTS.MD')))


def cli_subst_check(root: Path, base: str, target: str, names_file: Optional[str],
                    excepts: List[str], build: Optional[str] = None) -> int:
    try:
        base_sha: str = _commit(root, base)
        target_sha: str = _commit(root, target)
        folder: Optional[Path] = None
        if build is not None:
            folder = Path(build)
            if not folder.is_dir():
                raise DebtError('--build 산출물 폴더가 없다 — %s' % build)
        cleaned: List[str] = []
        for raw in excepts:
            rel: str = raw[2:] if raw.startswith('./') else raw
            if rel in ('web', '') or rel.startswith(('web/', '/', '.dddjango-web')) or is_test_path(rel):
                raise DebtError('--except 는 web/ 밖 비테스트 파일만 받는다 — %s' % raw)
            # 폴더·글롭은 받지 않는다 — 기준·대상 트리 어느 한쪽에 있는 파일 경로 하나씩만(테스트가 새어 빠지지 않게).
            if not any(_blob(root, sha, rel) for sha in (base_sha, target_sha)):
                raise DebtError('--except 는 기준·대상 트리에 있는 파일 경로만 받는다(폴더·글롭 불가) — %s' % raw)
            cleaned.append(rel)
        outside: List[str] = ['.', ':(exclude)web', ':(exclude).dddjango-web',
                              *(':(exclude,literal)' + e for e in cleaned)]
        if target_sha == _commit(root, 'HEAD'):
            dirty: List[str] = [e for e in _status_entries(
                root, ['status', '--porcelain', '-z', '--untracked-files=all', '--', *outside])
                if len(e) > 3 and e[2] == ' ']
            if dirty:
                raise DebtError('미커밋 web/ 밖 변경 — 커밋 뒤 다시(%s)'
                                % ', '.join(e[3:] for e in dirty))
        pairs: _Pairs = build_pairs(root, base_sha, target_sha, names_file)
        chain: List[Tuple[str, List[str]]] = _chain(root, base_sha, target_sha)
        if folder is not None and chain and chain[0][1][:1] != [base_sha]:
            raise DebtError('기준 %s 가 대상의 첫 부모 사슬 밖 — 레인 편집 판정 불가(--build)' % base_sha[:12])
        zero, feature, notes, problems = _records(root, folder, chain)
        switch, switch_state, switch_problems = _switch_record(root, folder, chain, zero, feature, pairs.switches)
        approved, approved_notes = _approved_merges(root, folder, base_sha, chain)
        steps, inflow, history_notes = _history(root, chain, outside, approved, feature, switch)
        notes += approved_notes + history_notes
        move_problems, move_notes = _check_moves(pairs, base_sha, target_sha)
        notes += move_notes
        problems += switch_problems + move_problems
        parents_of: Dict[str, List[str]] = dict(chain)
        trees: Dict[str, Dict[str, Tuple[str, str]]] = {}

        def tree(rev: str) -> Dict[str, Tuple[str, str]]:
            if rev not in trees:
                trees[rev] = _tree(root, rev)
            return trees[rev]

        def tag(sha: str, kind: str) -> str:
            if kind == 'F':
                source: str = feature[sha]
            elif kind == 'M':
                source = '승인 병합 안'
            elif len(parents_of.get(sha, [])) >= 2:
                source = '미승인 병합'
            elif not parents_of.get(sha):
                source = '뿌리'     # 무관 이력의 뿌리 커밋 — 등재 대상이 아니다
            else:
                source = 'slices[0]' if sha in zero else '기록 없음'
            return '%s(%s)' % (sha[:12], source)

        def tags(items: List[Tuple[str, str]]) -> str:
            return ' '.join(dict.fromkeys(tag(sha, kind) for sha, kind in items)) or '-'

        # 승인 목록 밖 병합이 들인 경로는 복원 대상이 아니다(등재 먼저) — 되돌려도 남게 병합마다 한 줄을 낸다.
        unlisted: Set[str] = {sha for sha, parents in chain
                              if folder is not None and len(parents) >= 2 and sha not in approved}
        for sha in [s for s, _parents in chain if s in unlisted]:
            brought: List[str] = sorted(p for p, hs in steps.items() if not _is_doc(p)
                                        and any(h[0] == sha for h in hs))
            if brought:
                problems.append('병합 %s(미승인 병합) 승인 목록 밖 병합이 %d경로를 들였다(%s%s) — 등재 먼저 · '
                                '되돌려도 이 줄은 남는다' % (sha[:12], len(brought), brought[0],
                                                          ' 외' if len(brought) > 1 else ''))

        candidates: Set[str] = _names(root, base_sha, target_sha, outside) | set(steps)
        # 슬라이스 0 이 SUT 를 옮기며 함께 옮긴 web_test/ 미러 테스트 — 옛 경로 판 → 새 경로 판을 한 구간으로 대조한다
        # (내용은 참조 치환뿐이어야 한다). 두 경로의 걸음이 슬라이스 0 대조 커밋뿐일 때만 — 그 밖은 아래 일반 대조(red).
        moves: Dict[str, str] = {new: old for new, old in _test_moves(set(tree(base_sha)), set(tree(target_sha)),
                                                                                pairs.renames).items()
                                 if all(h[1] == 'S' for h in steps.get(new, []) + steps.get(old, []))}
        moved_old: Set[str] = set(moves.values())
        listed: List[str] = []
        files: int = 0
        docs: List[str] = []
        upstream_only: int = 0
        for path in sorted(candidates):
            ref: str = inflow.get(path, base_sha)
            start: Entry = tree(ref).get(path)
            end: Entry = tree(target_sha).get(path)
            history: List[Step] = steps.get(path, [])
            if not is_test_path(path):
                if start == end:
                    upstream_only += path in inflow
                    continue
                if _is_doc(path):
                    docs.append(path)
                    continue
                files += 1
                lane: List[Tuple[str, str]] = [(h[0], h[1]) for h in history if h[1] != 'U']
                if any(sha in unlisted for sha, _kind in lane):
                    problems.append('%s 승인 목록 밖 병합 유입(%s) — 레인 커밋 %s — 등재 먼저(복원하지 않는다)' % (
                        path, _status(start, end), tags(lane)))
                    continue
                problems.append('%s 테스트 밖 web/ 밖 파일 변경(%s) — 레인 커밋 %s%s' % (
                    path, _status(start, end), tags(lane), ' · 기준 = 상류 판 %s' % ref[:12] if ref != base_sha else ''))
                continue
            if path in moved_old:
                continue        # 옮긴 미러 테스트의 옛 경로 — 새 경로 쪽에서 한 번에 대조한다
            if path in moves:
                files += 1
                problems.extend('%s — 미러 테스트 이동 %s → %s · 슬라이스 0 대조 커밋 %s' % (
                    line, moves[path], path, tags([(h[0], h[1]) for h in history]))
                    for line in _contrast(root, path, tree(base_sha).get(moves[path]), end, pairs, (base_sha, target_sha)))
                continue
            if not history and tree(base_sha).get(path) != end:
                # 기준이 첫 부모 사슬 밖(곁가지 커밋 · rebase)이면 기준 쪽에서만 바뀐 경로는 사슬에 걸음이 없다 — 기준 판 대비
                files += 1
                problems.extend('%s — 기준 판 대비(첫 부모 사슬에 이 경로의 걸음 없음 — 기준이 사슬 밖)' % line
                                for line in _contrast(root, path, tree(base_sha).get(path), end, pairs,
                                                      (base_sha, target_sha)))
                continue
            if switch_state == 'cancelled':
                history, unreverted = _drop_cancelled(path, history, tree(base_sha).get(path))
                problems.extend(unreverted)
            # 테스트 파일 — 슬라이스 0 대조 구간마다 치환만 · 기능 슬라이스와 그 뒤 승인 병합 안 몫은 목록 ·
            # 0T 걸음(test_switch 기록)은 구간을 끊고 시험 전환 규칙으로 대조한다
            others: List[Tuple[str, str]] = []
            run: List[Tuple[str, str, Entry, Entry, str]] = []      # (커밋, 종류, 전, 후, 전 판의 커밋)
            switched: List[Tuple[str, Entry, Entry, str]] = []      # 잇단 0T 걸음 — (커밋, 전, 후, 전 판의 커밋)
            checked: bool = False
            seen_feature: bool = False

            def flush() -> None:
                nonlocal checked
                if run and run[0][2] != run[-1][3]:
                    checked = True
                    found: List[str] = _contrast(root, path, run[0][2], run[-1][3], pairs, (run[0][4], run[-1][0]))
                    problems.extend('%s — 슬라이스 0 대조 커밋 %s' % (line, tags([(r[0], r[1]) for r in run]))
                                    for line in found)
                run.clear()

            def flush_switch() -> None:
                nonlocal checked
                if switched and switched[0][1] != switched[-1][2]:
                    checked = True
                    found: List[str] = _contrast_switch(root, path, switched[0][1], switched[-1][2], pairs,
                                                        (switched[0][3], switched[-1][0]))
                    shas: str = ' '.join(dict.fromkeys(s[0][:12] for s in switched))
                    problems.extend('%s — 0T 커밋 %s' % (line, shas) for line in found)
                switched.clear()

            for index, (sha, kind, before, after, up, upstream_entry) in enumerate(history):
                if index == 0:      # 첫 걸음의 전 판은 기준 판이다(무관 이력 · 기준이 첫 부모 사슬 밖이어도)
                    before = tree(base_sha).get(path)
                first_parent: List[str] = parents_of.get(sha, [])[:1]
                before_rev: str = base_sha if index == 0 or not first_parent else first_parent[0]
                if kind == 'M' and up and _clean(root, path, upstream_entry, after, pairs, (parents_of[sha][1], sha)):
                    kind = 'U'      # 상류 판 위에 레인의 치환만 얹힌 병합(겹침)
                if kind == 'M' and not seen_feature:
                    # 앞선 기능 편집을 잇지 않는 승인 병합 안 몫 — 슬라이스 0 대조 구간을 연다(상류 경로면 상류 판부터)
                    flush_switch()
                    flush()
                    run.append((sha, 'M', upstream_entry if up else before, after,
                                parents_of[sha][1] if up else before_rev))
                    continue
                if kind == 'S':
                    flush_switch()
                    run.append((sha, 'S', before, after, before_rev))
                    continue
                if kind == 'T':
                    flush()
                    switched.append((sha, before, after, before_rev))
                    continue
                flush_switch()
                flush()
                seen_feature = seen_feature or kind == 'F'
                if kind in ('F', 'M'):
                    others.append((sha, kind))
            flush_switch()
            flush()
            files += checked
            if start == end:
                upstream_only += path in inflow and not checked and not others
                continue
            if others:
                listed.append('%s(%s)%s — 커밋 %s' % (path, _status(start, end),
                                                     '' if path.endswith('.py') else '[비 .py]', tags(others)))
        notes += list(dict.fromkeys(pairs.infos))
    except (DebtError, OSError) as error:
        print('[backstop] 치환 확인 실행 불능 — %s' % error)
        return 1
    for note in notes:
        print('[info] %s' % note)
    if docs:
        print('[info] 문서 제외(docs/ · .dddjango/ · 루트 .md) %d: %s%s' % (
            len(docs), ', '.join(docs[:10]), ' 외 %d' % (len(docs) - 10) if len(docs) > 10 else ''))
    for item in listed:
        print('[info] 기능 슬라이스·병합 테스트 편집 %s' % item)
    for problem in problems:
        print('[subst] %s' % problem)
    excluded: str = (' — %s' % ', '.join(cleaned)) if cleaned else ''
    tally: str = '쌍 %d · 병합 유입 제외 %d · 기능 테스트 편집 %d · 문서 제외 %d · 제외 %d%s' % (
        pairs.count(), upstream_only, len(listed), len(docs), len(cleaned), excluded)
    if problems:
        print('[backstop] 치환 확인 — 어긋남 %d · web/ 밖 변경 파일 %d · %s' % (len(problems), files, tally))
        return 2
    print('[backstop] 치환 확인 — web/ 밖 변경 파일 %d · %s' % (files, tally))
    return 0
