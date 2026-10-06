# dddjango-web 치환 확인 (값 정본: 커맨드 «슬라이스 0 호출» 끝 green ④ · houserules §8).
# (바탕: dddjango-web v1.3.1 src/subst.py — 트리와 무관한 git 대조라 그대로 · 테스트 판정은 debt.is_test_path[web_test 포함])
#
# --subst-check <기준> <대상> [--names <design-spec.md>] [--except <경로>]…: 기준..대상 사이의 web/ 밖
#   변경이 테스트 파일의 옛 경로·옛 이름 → 새 경로·새 이름 치환뿐인지 본다. 쌍은 web/ 개명(git diff -M
#   — 누적 1회와 구간 안 커밋별 개명 사슬) · 옛 폴더 전체 이동 · 명세 `## 슬라이스 0` 절의 `이름:` 행에서
#   만든다. 사슬 쌍은 옛 경로가 기준에만 · 새 경로가 대상에만 있을 때만 쓰고, 구간 안에서 새로 생긴
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

import ast
import difflib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .debt import DebtError, is_test_path, module_of, parse_spec_pairs, tail_of

_IDENT: str = 'A-Za-z0-9_'


class _Pairs:
    """대상(새) → 기준(옛) 역치환 쌍."""

    def __init__(self) -> None:
        self.full: Dict[str, str] = {}      # 점 경로 전체(이름 쌍)
        self.prefix: Dict[str, str] = {}    # 모듈·패키지 점 경로 접두(점 성분 경계)
        self.bare: Dict[str, str] = {}      # 맨 이름(끝 성분이 바뀐 이름 쌍)
        self.text: Dict[str, str] = {}      # 꼬리 문자열(경로)
        self.renames: List[Tuple[str, str]] = []  # web/ 개명 쌍(옛, 새 — web-상대) · 미러 테스트 이동 판정 입력
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


def build_pairs(root: Path, base: str, target: str, names_file: Optional[str]) -> _Pairs:
    pairs: _Pairs = _Pairs()
    base_files: Set[str] = _tree_files(root, base)
    target_files: Set[str] = _tree_files(root, target)
    renames: List[Tuple[str, str]] = _history_renames(root, base, target, base_files, target_files)
    pairs.renames = renames
    for old, new in renames:
        old_tail, new_tail = tail_of(old), tail_of(new)
        pairs.text[new_tail[0]] = old_tail[0]
        old_mod, new_mod = module_of(old), module_of(new)
        if old_mod and new_mod:
            pairs.prefix[new_mod] = old_mod
    for folder, dest in _folder_pairs(renames, base_files, target_files):
        pairs.text[_strip_static(dest) + '/'] = _strip_static(folder) + '/'
        pairs.prefix['web.' + dest.replace('/', '.')] = 'web.' + folder.replace('/', '.')
    if names_file is not None:
        try:
            text: str = Path(names_file).read_text(encoding='utf-8')
        except OSError as error:
            raise DebtError('--names 파일을 읽을 수 없다 — %s' % error)
        for old, new in parse_spec_pairs(text, require=True)[1]:
            pairs.full[new] = old
            if new.rsplit('.', 1)[1] != old.rsplit('.', 1)[1]:
                pairs.bare[new.rsplit('.', 1)[1]] = old.rsplit('.', 1)[1]
    return pairs


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


def _segments(tree: ast.Module, pairs: Optional[_Pairs]) -> Dict[Tuple, Tuple[int, Counter]]:
    """블록·위치별 연속 import 구간 → (첫 행, 바인딩 다중집합). 위치 = 그 블록에서 구간 앞 비-import 문 수."""
    out: Dict[Tuple, Tuple[int, Counter]] = {}

    def walk(stmts: List[ast.stmt], path: Tuple) -> None:
        pos: int = 0
        for st in stmts:
            if isinstance(st, (ast.Import, ast.ImportFrom)):
                key: Tuple = path + (pos,)
                line, bag = out.setdefault(key, (st.lineno, Counter()))
                for dotted, alias in _bindings(st):
                    if pairs is not None:
                        dotted = pairs.binding(dotted, alias)
                    bag[(dotted, alias)] += 1
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


def _compare_py(path: str, base_src: str, target_src: str, pairs: _Pairs) -> List[str]:
    try:
        base_tree: ast.Module = ast.parse(base_src)
        target_tree: ast.Module = ast.parse(target_src)
    except SyntaxError as error:
        raise DebtError('%s 파싱 실패 — %s' % (path, error))
    problems: List[str] = []
    base_segs = _segments(base_tree, None)
    target_segs = _segments(target_tree, pairs)
    for key in sorted(set(base_segs) | set(target_segs), key=repr):
        b_line, b_bag = base_segs.get(key, (0, Counter()))
        t_line, t_bag = target_segs.get(key, (0, Counter()))
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
# (커밋, 종류 S|F|U|M, 전, 후, 상류 경로인가, 상류 판 항목) — S = 슬라이스 0 대조 · F = 기능 슬라이스 커밋 ·
# U = 승인 병합이 들여온 그대로 · M = 승인 병합 안 레인 몫


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
             feature: Dict[str, str]) -> Tuple[Dict[str, List[Step]], Dict[str, str], List[str]]:
    """첫 부모 사슬의 경로별 걸음 · 상류 판(경로 → 상류가 그 경로를 바꾼 마지막 승인 병합의 둘째 부모) · 알림."""
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
        for path, (before, after) in _raw(root, parents[0] if parents else empty, sha, outside).items():
            steps.setdefault(path, []).append((sha, kind, before, after, False, None))
    return steps, inflow, notes


def _status(before: Entry, after: Entry) -> str:
    # 실행 비트만 다르면 M(git 과 같다) — 종류(일반 · 심볼릭 링크 · 하위 모듈)가 바뀔 때만 T
    return 'A' if before is None else 'D' if after is None else 'T' if before[0][:2] != after[0][:2] else 'M'


def _contrast(root: Path, path: str, before: Entry, after: Entry, pairs: _Pairs) -> List[str]:
    """테스트 파일 한 구간(전 → 후)이 치환뿐인가 — 어긋남 줄 목록."""
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
    compare = _compare_py if path.endswith('.py') else _compare_lines
    return compare(path, base_src, target_src, pairs)


def _clean(root: Path, path: str, before: Entry, after: Entry, pairs: _Pairs) -> bool:
    try:
        return not _contrast(root, path, before, after, pairs)
    except DebtError:
        return False


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
        approved, approved_notes = _approved_merges(root, folder, base_sha, chain)
        steps, inflow, history_notes = _history(root, chain, outside, approved, feature)
        notes += approved_notes + history_notes
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
                    for line in _contrast(root, path, tree(base_sha).get(moves[path]), end, pairs))
                continue
            if not history and tree(base_sha).get(path) != end:
                # 기준이 첫 부모 사슬 밖(곁가지 커밋 · rebase)이면 기준 쪽에서만 바뀐 경로는 사슬에 걸음이 없다 — 기준 판 대비
                files += 1
                problems.extend('%s — 기준 판 대비(첫 부모 사슬에 이 경로의 걸음 없음 — 기준이 사슬 밖)' % line
                                for line in _contrast(root, path, tree(base_sha).get(path), end, pairs))
                continue
            # 테스트 파일 — 슬라이스 0 대조 구간마다 치환만 · 기능 슬라이스와 그 뒤 승인 병합 안 몫은 목록
            others: List[Tuple[str, str]] = []
            run: List[Tuple[str, str, Entry, Entry]] = []
            checked: bool = False
            seen_feature: bool = False

            def flush() -> None:
                nonlocal checked
                if run and run[0][2] != run[-1][3]:
                    checked = True
                    found: List[str] = _contrast(root, path, run[0][2], run[-1][3], pairs)
                    problems.extend('%s — 슬라이스 0 대조 커밋 %s' % (line, tags([(r[0], r[1]) for r in run]))
                                    for line in found)
                run.clear()

            for index, (sha, kind, before, after, up, upstream_entry) in enumerate(history):
                if index == 0:      # 첫 걸음의 전 판은 기준 판이다(무관 이력 · 기준이 첫 부모 사슬 밖이어도)
                    before = tree(base_sha).get(path)
                if kind == 'M' and up and _clean(root, path, upstream_entry, after, pairs):
                    kind = 'U'      # 상류 판 위에 레인의 치환만 얹힌 병합(겹침)
                if kind == 'M' and not seen_feature:
                    # 앞선 기능 편집을 잇지 않는 승인 병합 안 몫 — 슬라이스 0 대조 구간을 연다(상류 경로면 상류 판부터)
                    flush()
                    run.append((sha, 'M', upstream_entry if up else before, after))
                    continue
                if kind == 'S':
                    run.append((sha, 'S', before, after))
                    continue
                flush()
                seen_feature = seen_feature or kind == 'F'
                if kind in ('F', 'M'):
                    others.append((sha, kind))
            flush()
            files += checked
            if start == end:
                upstream_only += path in inflow and not checked and not others
                continue
            if others:
                listed.append('%s(%s)%s — 커밋 %s' % (path, _status(start, end),
                                                     '' if path.endswith('.py') else '[비 .py]', tags(others)))
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
