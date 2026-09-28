# dddjango-web 치환 확인 (값 정본: 커맨드 «슬라이스 0 호출» 끝 green ④ · houserules §7).
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

import ast
import difflib
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


def cli_subst_check(root: Path, base: str, target: str, names_file: Optional[str],
                    excepts: List[str]) -> int:
    try:
        base_sha: str = _commit(root, base)
        target_sha: str = _commit(root, target)
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
        entries: List[str] = _status_entries(
            root, ['diff', '--name-status', '--no-renames', '-z', base_sha, target_sha, '--', *outside])
        problems: List[str] = []
        files: int = 0
        for status, path in zip(entries[0::2], entries[1::2]):
            files += 1
            if not is_test_path(path):
                problems.append('%s 테스트 밖 web/ 밖 파일 변경(%s)' % (path, status))
                continue
            if status != 'M':
                problems.append('%s 치환이 아닌 변경(%s — 새 파일·삭제·개명·타입 변경)' % (path, status))
                continue
            before: bytes = _git(root, ['show', '%s:%s' % (base_sha, path)])
            after: bytes = _git(root, ['show', '%s:%s' % (target_sha, path)])
            try:
                if b'\0' in before or b'\0' in after:
                    raise UnicodeDecodeError('utf-8', b'', 0, 1, 'binary')
                base_src, target_src = before.decode('utf-8'), after.decode('utf-8')
            except UnicodeDecodeError:
                problems.append('%s 이진 파일 변경 — 치환으로 설명할 수 없다' % path)
                continue
            compare = _compare_py if path.endswith('.py') else _compare_lines
            problems.extend(compare(path, base_src, target_src, pairs))
    except (DebtError, OSError) as error:
        print('[backstop] 치환 확인 실행 불능 — %s' % error)
        return 1
    for problem in problems:
        print('[subst] %s' % problem)
    excluded: str = (' — %s' % ', '.join(cleaned)) if cleaned else ''
    if problems:
        print('[backstop] 치환 확인 — 어긋남 %d · web/ 밖 변경 파일 %d · 쌍 %d · 제외 %d%s'
              % (len(problems), files, pairs.count(), len(cleaned), excluded))
        return 2
    print('[backstop] 치환 확인 — web/ 밖 변경 파일 %d · 쌍 %d · 제외 %d%s'
          % (files, pairs.count(), len(cleaned), excluded))
    return 0
