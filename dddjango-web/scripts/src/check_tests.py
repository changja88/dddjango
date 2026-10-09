# TG — 3종: TG1 신규 BC 시험 존재 · TG2 변경 영구 시험 재현성 · TG3 비채택 이미지 비교.
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

import ast
import configparser
import difflib
import io
import tokenize
from dataclasses import dataclass
import fnmatch
import json
import re
import shlex
import subprocess
from pathlib import Path
from typing import List, Set

from .common import BackstopContext, Finding, base_name_of, segs_of

_RULE_TG: str = 'discipline-test — coder 행위검증 테스트 산출(green=pytest web_test)'


@dataclass
class TestChange:
    path: str
    before: str
    source: str
    added: set[int]
    deleted: set[int]
    old_to_new: dict[int, int]


def _commit_oid(root, ref):
    if not isinstance(ref, str) or not ref or ref.startswith('-'):
        raise ValueError('commit 기준점 없음')
    r = subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', ref + '^{commit}'], capture_output=True)
    if r.returncode:
        raise ValueError('commit 기준점 해소 실패: ' + ref)
    return r.stdout.decode().strip()


def _line_delta(before, source):
    # old/new hunk의 실제 대응만 사용한다. 같은 숫자 행끼리 비교하지 않는다.
    added, deleted, mapping = set(), set(), {}
    for tag, a, b, c, d in difflib.SequenceMatcher(None, before.splitlines(), source.splitlines(), autojunk=False).get_opcodes():
        if tag == 'equal':
            mapping.update((a + i + 1, c + i + 1) for i in range(b - a))
        else:
            deleted.update(range(a + 1, b + 1))
            added.update(range(c + 1, d + 1))
    return added, deleted, mapping


def _changed_tests(ctx: BackstopContext) -> List[TestChange]:
    """기준 commit→현재 트리의 새쪽 hunk와 old/new 대응을 수집한다(staged·unstaged·커밋 포함).
    rename은 명시 -M50%와 D/A 동일 blob 대응으로 확인한다. 시험→시험 순수 이동은 새 줄 0,
    copy·시험 밖에서 편입·기준판에 없는 미추적은 전 줄 새 줄이다. 기준판 파일의 미추적은 비교한다.
    관례·pytest 설정의 시험/지원 파일과 같은 commit OID의 G0 명시 경로만 수집한다.
    기준점·대응 해석 실패는 범위 미확정·미실행으로 고지하며 ctx.files나 파일 전체로 퇴화하지 않는다.
    """
    if not ctx.can_detect_new_units:
        ctx.notices.append('[info] TG2·TG3 미실행 — git 기준점 없음 · 변경 시험 범위 미확정')
        return []
    roots = ['web_test', 'test', 'tests']
    patterns = ['test_*.py', '*_test.py', 'tests.py']
    explicit = []
    try:
        base = _commit_oid(ctx.root, ctx.diff_base)
        for name, section in [('pytest.ini', 'pytest'), ('tox.ini', 'pytest'), ('setup.cfg', 'tool:pytest')]:
            path = ctx.root / name
            if not path.is_file():
                continue
            cfg = configparser.ConfigParser(interpolation=None)
            cfg.read(path, encoding='utf-8')
            if cfg.has_section(section):
                roots += shlex.split(cfg.get(section, 'testpaths', fallback=''))
                value = cfg.get(section, 'python_files', fallback='')
                if value:
                    patterns = shlex.split(value)
        path = ctx.root / 'pyproject.toml'
        if path.is_file():
            import tomllib
            options = tomllib.loads(path.read_text(encoding='utf-8')).get('tool', {}).get('pytest', {}).get('ini_options', {})
            def words(value):
                return shlex.split(value) if isinstance(value, str) else value
            roots += words(options.get('testpaths', []))
            if options.get('python_files'):
                patterns = words(options['python_files'])
        for path in sorted((ctx.root / '.dddjango-web').glob('*/build-state.json')):
            try:
                state = json.loads(path.read_text(encoding='utf-8'))
                snapshot = _commit_oid(ctx.root, state.get('git_snapshot'))
                command = state.get('test_command', '')
                if not isinstance(command, str):
                    continue
                words = shlex.split(command)
            except (OSError, ValueError, TypeError, AttributeError):
                # 읽기·JSON·기준점·명령 필드/quoting 실패는 해당 기록만 건너뛴다.
                continue
            if snapshot != base:
                continue
            for word in words:
                candidate_path = word.split('::')[0]
                if not word.startswith('-') and (ctx.root / candidate_path).exists():
                    explicit.append(candidate_path.rstrip('/'))
        def git(*args):
            r = subprocess.run(['git', '-C', str(ctx.root), *args], capture_output=True)
            if r.returncode:
                raise ValueError('root diff/대응 수집 실패')
            return r.stdout.decode('utf-8', 'surrogateescape')
        old_paths = set(git('ls-tree', '-rz', '--name-only', base, '--', '.').split('\0')) - {''}
        tokens = git('-c', 'diff.renames=true', 'diff', '--no-ext-diff', '--no-textconv',
                     '--find-renames=50%', '-l0', '--name-status', '-z', '--relative', base, '--', '.').split('\0')
        untracked = set(git('ls-files', '--others', '--exclude-standard', '-z', '--', '.').split('\0')) - {''}
        pairs, changed = {}, set(untracked)
        i = 0
        while i < len(tokens) and tokens[i]:
            status, old = tokens[i], tokens[i + 1]
            if status.startswith(('R', 'C')):
                new = tokens[i + 2]
                if status.startswith('R'):
                    pairs[new] = old
                changed.add(new)
                i += 3
            else:
                # index에서 빠져도 현물이 있는 기준판 파일은 기존 파일로 비교한다.
                if not status.startswith('D') or (ctx.root / old).is_file():
                    changed.add(old)
                i += 2
        def under(rel, folder):
            return rel == folder or rel.startswith(folder.rstrip('/') + '/')
        def candidate(rel):
            if not rel.endswith('.py'):
                return False
            parts = Path(rel).parts
            name = parts[-1]
            conventional = any(p in ('web_test', 'test', 'tests') for p in parts[:-1])
            support = name == 'conftest.py' or name.endswith('_support.py') or name in ('support.py', 'helpers.py') or any(p in ('support', '_support', 'helpers') for p in parts[:-1])
            collected = any(fnmatch.fnmatch(name, pat) for pat in patterns)
            return conventional or name == 'conftest.py' or any(under(rel, p) for p in explicit) or (
                (collected or support) and (collected or any(under(rel, p) for p in roots)))
        contents = {}
        def old_source(rel):
            if rel not in contents:
                contents[rel] = git('show', base + ':' + rel)
            return contents[rel]
        gone = {p for p in old_paths if not (ctx.root / p).exists()} - set(pairs.values())
        out = []
        for rel in sorted(changed):
            if not candidate(rel) or not (ctx.root / rel).is_file():
                continue
            source = (ctx.root / rel).read_text(encoding='utf-8')
            old = pairs.get(rel, rel if rel in old_paths else None)
            if old is None:
                # ls-files의 미추적은 git diff rename 입력 밖이다. 동일 blob D/A도 명시 대응한다.
                matches = [p for p in sorted(gone) if old_source(p) == source]
                if len(matches) > 1:
                    ctx.notices.append('[info] TG2·TG3 미실행 — %s 이동 대응 모호 · 변경 시험 범위 미확정' % rel)
                    continue
                if matches:
                    old = matches[0]
                    gone.remove(old)
            before = old_source(old) if old is not None and candidate(old) else ''
            added, deleted, mapping = _line_delta(before, source)
            out.append(TestChange(rel, before, source, added, deleted, mapping))
        return out
    except (OSError, ValueError, IndexError, TypeError, configparser.Error, ImportError) as error:
        ctx.notices.append('[info] TG2·TG3 미실행 — 기준점·설정·대응 해석 실패 · 변경 시험 범위 미확정: %s' % error)
        return []


@dataclass(frozen=True)
class Static:
    value: str | None = None
    places: frozenset[int] = frozenset()
    chars: tuple[int, ...] = ()
    runner: bool = False
    anchors: frozenset[int] = frozenset()


@dataclass(frozen=True)
class Screen:
    origin: tuple[int, int] | None = None
    places: frozenset[int] = frozenset()


@dataclass(frozen=True)
class Probe:
    check_id: str
    position: tuple[int, int]
    places: frozenset[int]
    active: bool
    slot: int = 0
    anchors: frozenset[int] = frozenset()


def _places(node):
    if node is None or not hasattr(node, 'lineno'):
        return frozenset()
    return frozenset(range(node.lineno, node.end_lineno + 1))


def _literal_chars(node, source):
    """각 디코드 문자를 원래 Python 행으로 대응한다(escape·삼중·암시적 결합 포함)."""
    segment = ast.get_source_segment(source, node)
    rows = []
    for token in tokenize.generate_tokens(io.StringIO(segment).readline):
        if token.type != tokenize.STRING:
            continue
        text = token.string
        m = re.match(r"(?i)[rub]*(?=['\"])", text)
        if m is None:
            raise ValueError('Python 문자열 위치 대응 실패')
        prefix = m.group()
        quote = text[m.end()]
        if text.startswith(quote * 3, m.end()):
            quote *= 3
        body = text[m.end() + len(quote):-len(quote)]
        line = node.lineno + token.start[0] - 1
        i = 0
        while i < len(body):
            if body[i] != '\\' or 'r' in prefix.lower():
                rows.append(line)
                line += body[i] == '\n'
                i += 1
                continue
            end = i + 2
            if end > len(body):
                raise ValueError('Python escape 위치 대응 실패')
            c = body[i + 1]
            if c in 'xuU':
                end = i + 2 + {'x': 2, 'u': 4, 'U': 8}[c]
            elif c == 'N' and body[i + 2:i + 3] == '{':
                end = body.index('}', i + 3) + 1
            elif c in '01234567':
                end = i + 1
                while end < min(len(body), i + 4) and body[end] in '01234567':
                    end += 1
            escape = body[i:end]
            decoded = ast.literal_eval('\"' + escape.replace('\"', '\\\"') + '\"') if c != '\"' else '\"'
            rows.extend([line] * len(decoded))
            line += escape.count('\n')
            i = end
    if len(rows) != len(node.value):
        raise ValueError('Python 디코드 위치 대응 길이 불일치')
    return tuple(rows)

def _value(node, env):
    """닫힌 정적 값: 문자열·지역 이름·+ 연결·Path / 결합·Path/joinpath·str/fspath.
    Path.home()는 ~ 표식으로 보존한다. 도구 탐색(which 등)·동적 호출은 추론하지 않는다.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return env.get(node.id)
    if isinstance(node, ast.Attribute) and node.attr == 'parent':
        value = _value(node.value, env)
        return str(Path(value).parent) if value is not None else None
    if (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute)
            and node.value.attr == 'parents' and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, int)):
        value = _value(node.value.value, env)
        if value is not None and 0 <= node.slice.value < len(Path(value).parents):
            return str(Path(value).parents[node.slice.value])
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Div)):
        a, b = _value(node.left, env), _value(node.right, env)
        if a is not None and b is not None:
            return a + b if isinstance(node.op, ast.Add) else str(Path(a) / b)
    if isinstance(node, ast.Call):
        name = _call_name(node.func)
        if name in ('Path.home', 'pathlib.Path.home') and not node.args:
            return '~'
        if name in ('Path', 'pathlib.Path', 'str', 'os.fspath') and node.args:
            values = [_value(a, env) for a in node.args]
            if all(v is not None for v in values):
                return str(Path(*values)) if name in ('Path', 'pathlib.Path') else values[0]
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'joinpath':
            values = [_value(node.func.value, env)] + [_value(a, env) for a in node.args]
            if all(v is not None for v in values):
                return str(Path(*values))
        if isinstance(node.func, ast.Attribute) and node.func.attr in ('resolve', 'absolute') and not node.args:
            return _value(node.func.value, env)
    return None


def _call_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _call_name(node.value) + '.' + node.attr
    return ''


_JS_RUNNERS = {'node', 'nodejs', 'node.exe'}


def _node_eval(vals):
    """Node 옵션 구간만 해석한다. --·첫 entry point 이후는 스크립트 argv다.
    반환값은 코드 인덱스·실제 argv·값을 받는 옵션의 인덱스다(실행기 확정은 호출자가 맡는다).
    """
    code, option_values = None, []
    i = 1
    while i < len(vals):
        word = vals[i].value
        if word is None:
            if code is None:
                return None
            break
        if word == '--':
            i += 1
            break
        if word == '-' or not word.startswith('-'):
            break
        if word in ('-e', '--eval', '-p', '--print'):
            if i + 1 == len(vals):
                return None
            code = i + 1
            i += 2
        elif word in ('-r', '--require', '--import', '--loader', '--experimental-loader',
                      '--inspect-port', '--title', '-C', '--conditions', '--icu-data-dir'):
            if i + 1 == len(vals):
                return None
            option_values.append(i + 1)
            i += 2
        else:
            i += 1
    return (code, vals[i:], option_values) if code is not None else None


def _static(node, env, source):
    if node is None:
        return Static()
    places = _places(node)
    anchors = frozenset({node.lineno}) if hasattr(node, 'lineno') else frozenset()
    for n in ast.walk(node):
        if hasattr(n, 'lineno'):
            anchors |= {n.lineno}
        if isinstance(n, ast.Name):
            places |= env.get(n.id, Static()).places
            anchors |= env.get(n.id, Static()).anchors
    if isinstance(node, ast.Name):
        old = env.get(node.id, Static())
        return Static(old.value, places, old.chars, old.runner, anchors)
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return Static(node.value, places, _literal_chars(node, source), anchors=anchors)
    chars = ()
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = _static(node.left, env, source), _static(node.right, env, source)
        chars = a.chars + b.chars
    if isinstance(node, ast.Call) and _call_name(node.func) in ('str', 'os.fspath') and node.args:
        chars = _static(node.args[0], env, source).chars
    if isinstance(node, ast.Call) and _call_name(node.func) == 'shutil.which' and len(node.args) == 1:
        name = _value(node.args[0], {k: v.value for k, v in env.items()})
        return Static(None, places, runner=name in _JS_RUNNERS, anchors=anchors)
    value = _value(node, {k: v.value for k, v in env.items()})
    return Static(value, places, chars, anchors=anchors)


def _forbidden(value, root):
    if value is None or re.match(r'^[a-zA-Z][\w+.-]*://', value):
        return False
    path = Path(value)
    if '.dddjango-web' in path.parts or value == '~' or value.startswith('~/'):
        return True
    if path.is_absolute():
        return not path.resolve().is_relative_to(root.resolve())
    return False


_PROCESS = {'subprocess.run', 'subprocess.Popen', 'subprocess.call', 'subprocess.check_call', 'subprocess.check_output'}
_PATH_METHODS = {'open', 'read_text', 'read_bytes', 'write_text', 'write_bytes', 'mkdir', 'unlink', 'iterdir', 'glob', 'rglob'}
_FILE_FUNCTIONS = {'open', 'io.open', 'os.open', 'os.mkdir', 'os.makedirs', 'os.remove', 'os.unlink',
                   'shutil.copy', 'shutil.copy2', 'shutil.copyfile', 'shutil.copytree', 'shutil.move', 'shutil.rmtree'}
_SCREEN_ASSERTIONS = {'to_have_screenshot', 'toHaveScreenshot'}
_SERVER_FUNCTIONS = {'fixture_server', 'start_server', 'run_server'}



def _js_tokens(source):
    """JS 코드 토큰만 판별한다. 주석·문자열·정규식은 코드가 아니며 문자열은 TG2 인자에만 쓴다."""
    pattern = re.compile(r'(?P<space>\s+)|(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)|'
                         r'(?P<string>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`)|'
                         r'(?P<word>[A-Za-z_$][\w$]*)|(?P<op>=>|&&|\|\||\?\?|===|!==|==|!=|\+\+|--)|(?P<other>.)')
    tokens = []
    pos = 0
    previous = ''
    while pos < len(source):
        # 식 시작은 정규식이다. )·} 뒤의 모호한 slash 구간도 코드로 단정하지 않는다.
        # 확정된 피연산자 뒤의 나눗셈은 코드 토큰으로 남긴다.
        expression_start = previous in ('', '=', '(', ',', ':', '[', 'return', 'throw', 'case', 'yield', 'await',
                                        'typeof', 'void', 'delete',
                                        ';', '{', '!', '&&', '||', '=>', '?', '??', '&', '|', '^', '~',
                                        '==', '!=', '===', '!==', '+', '-', '*', '/', '%', '<', '>', 'in', 'instanceof')
        if source[pos] == '/' and not source.startswith(('//', '/*'), pos) and (expression_start or previous in (')', '}')):
            regex = re.match(r'/(?:\\.|\[(?:\\.|[^\]\\])*\]|[^/\n\\])+/[a-z]*', source[pos:])
            if regex:
                pos += len(regex.group())
                previous = 'literal'
                continue
            if expression_start:
                raise ValueError('JS 정규식 구간 해석 실패')
        m = pattern.match(source, pos)
        if m is None:
            break
        pos = m.end()
        if m.lastgroup in ('space', 'comment'):
            continue
        value = m.group()
        kind = m.lastgroup
        tokens.append((kind, value, source.count('\n', 0, m.start()), m.start()))
        previous = 'literal' if kind == 'string' else value
    return tokens


def _js_checks(source, root, argv=None):
    """TG2: 확정된 JS 실행기의 정적 코드에서 fs.readFile[Sync]/writeFile[Sync]/appendFile[Sync]/mkdir[Sync]/unlink[Sync],
    문자열·const/let 지역 변수·+ 연결·path.join/resolve·정적 argv의 process.argv.slice(1) 배열 분해·process.argv[정수]를 지원한다.
    TG3: 같은 블록의 서로 다른 screenshot 생성 출처 두 개의 .equals/Buffer.compare,
    to_have_screenshot/toHaveScreenshot 호출, screenshot 수신값의 toMatchSnapshot을 지원한다.
    생성·중간 대입·I/O·비교의 문자 위치와 실제 사용 argv의 Python 출처를 따로 보존한다.
    대입 RHS는 중첩 괄호를 보존하고 세미콜론·블록 끝·ASI 줄 경계·다음 선언 키워드에서 끝낸다.
    screenshot 이름 별칭·재대입 screenshot·다른 블록·파일 재읽기·해시·자유 하니스 추론은 지원하지 않는다.
    주석·문자열·정규식의 가짜 호출과 자기 비교는 제외한다.
    """
    toks = _js_tokens(source)
    initial = {}
    pieces = [t[1] if t[0] != 'string' else '""' for t in toks]
    code = ' '.join(pieces)
    starts, offset = [], 0
    for piece in pieces:
        starts.append(offset)
        offset += len(piece) + 1
    for m in re.finditer(r'\b(?:const|let)\s*\[([\w$,\s]+)\]\s*=\s*process\s*\.\s*argv\s*\.\s*slice\s*\(\s*1\s*\)', code):
        origin = frozenset(t[3] for t, start in zip(toks, starts) if m.start() <= start < m.end())
        for name, val in zip(m.group(1).split(','), argv or []):
            initial[name.strip()] = Static(val.value, origin, anchors=val.places)
    frames = [(initial, {}, {})]  # 정적 값 · screenshot 출처 · 대입 위치
    out = []
    def places(ts):
        return frozenset(t[3] for t in ts)
    def arguments(ts, opening):
        args, start, depth = [], opening + 1, 0
        for j in range(start, len(ts)):
            v = ts[j][1] if ts[j][0] != 'string' else 'literal'
            if v in ('(', '[', '{'):
                depth += 1
            elif v in (')', ']', '}'):
                if depth == 0:
                    if j > start:
                        args.append(ts[start:j])
                    return args, j
                depth -= 1
            elif v == ',' and depth == 0:
                args.append(ts[start:j]); start = j + 1
        return [], opening
    def value(ts, env):
        ps = places(ts)
        if len(ts) >= 6 and [t[1] for t in ts[:4]] == ['process', '.', 'argv', '['] and ts[-1][1] == ']':
            index = ''.join(t[1] for t in ts[4:-1])
            if index.isdigit() and 1 <= int(index) <= len(argv or []):
                val = argv[int(index) - 1]
                return Static(val.value, ps, anchors=val.places)
        if len(ts) == 1:
            t = ts[0]
            if t[0] == 'string':
                return Static(t[1][1:-1] if '${' not in t[1] else None, ps)
            old = env.get(t[1], Static())
            return Static(old.value, old.places | ps, anchors=old.anchors)
        chunks, start = [], 0
        for j, t in enumerate(ts):
            if t[1] == '+':
                chunks.append(value(ts[start:j], env)); start = j + 1
        if chunks:
            chunks.append(value(ts[start:], env))
            ps |= frozenset().union(*(c.places for c in chunks))
            val = ''.join(c.value for c in chunks) if all(c.value is not None for c in chunks) else next((c.value for c in chunks if _forbidden(c.value, root)), None)
            return Static(val, ps, anchors=frozenset().union(*(c.anchors for c in chunks)))
        if [t[1] for t in ts[:4]] in (['path', '.', 'join', '('], ['path', '.', 'resolve', '(']):
            vals = [value(arg, env) for arg in arguments(ts, 3)[0]]
            ps |= frozenset().union(*(v.places for v in vals))
            return Static(str(Path(*(v.value for v in vals))) if vals and all(v.value is not None for v in vals) else None,
                          ps, anchors=frozenset().union(*(v.anchors for v in vals)))
        return Static(None, ps)
    def screen_expr(ts, screens):
        ps = places(ts)
        if ts and ts[0][1] == 'await':
            ts = ts[1:]
        if len(ts) == 1:
            old = screens.get(ts[0][1], Screen())
            return Screen(old.origin, old.places | ps)
        if not ts or ts[0][0] != 'word':
            return Screen(None, ps)
        index, last = 1, ts[0][1]
        while index < len(ts):
            if ts[index][1] == '.' and index + 1 < len(ts) and ts[index + 1][0] == 'word':
                last = ts[index + 1][1]; index += 2
            elif ts[index][1] == '(':
                _, end = arguments(ts, index)
                if end == index:
                    return Screen(None, ps)
                index = end + 1
                if index == len(ts):
                    return Screen((ts[0][3], 0) if last == 'screenshot' else None, ps)
            else:
                return Screen(None, ps)
        return Screen(None, ps)
    def record(cid, token, ps, active, anchors=frozenset()):
        out.append(Probe(cid, (token[3], 0), ps | {token[3]}, active, anchors=anchors))
    def pair(token, left, right, screens, ps):
        a, b = screen_expr(left, screens), screen_expr(right, screens)
        record('TG3', token, ps | a.places | b.places,
               a.origin is not None and b.origin is not None and a.origin != b.origin)
    for i, token in enumerate(toks):
        kind, word, line, offset = token
        env, screens, assigned = frames[-1]
        if kind == 'string':
            continue
        if word == '{':
            frames.append((dict(env), {}, {})); continue
        if word == '}':
            if len(frames) > 1:
                frames.pop()
            continue
        if kind == 'word' and i + 1 < len(toks) and toks[i + 1][1] == '=':
            end, depth = i + 2, 0
            while end < len(toks):
                punctuation = toks[end][1] if toks[end][0] != 'string' else 'literal'
                if depth == 0 and punctuation in (';', '}'):
                    break
                if depth == 0 and end > i + 2:
                    previous = toks[end - 1]
                    can_end = (previous[0] == 'string' or previous[1] in (')', ']', '}', '++', '--') or
                               previous[1].isdigit() or previous[0] == 'word' and previous[1] not in
                               ('await', 'yield', 'new', 'typeof', 'void', 'delete', 'in', 'instanceof'))
                    continues = punctuation in ('(', '[', '.', '+', '-', '*', '/', '%', '**', '&&', '||', '??',
                                                '?', ':', '=', '==', '!=', '===', '!==', '<', '>', '&', '|', '^',
                                                'in', 'instanceof', ',')
                    if punctuation in ('const', 'let', 'var') or (toks[end][2] > previous[2] and can_end and not continues):
                        break
                if punctuation in ('(', '[', '{'):
                    depth += 1
                elif punctuation in (')', ']', '}'):
                    depth -= 1
                end += 1
            rhs = toks[i + 2:end]
            ps = places(toks[i:end])
            val = value(rhs, env)
            env[word] = Static(val.value, val.places | ps, anchors=val.anchors)
            screen = screen_expr(rhs, screens)
            # screenshot 이름 별칭과 재대입은 생성 출처로 인정하지 않는다.
            if word in assigned or len(rhs) == 1:
                screens[word] = Screen(None, ps | assigned.get(word, frozenset()) | screen.places)
            else:
                screens[word] = Screen(screen.origin, screen.places | ps)
            assigned[word] = assigned.get(word, frozenset()) | ps
        if i + 1 >= len(toks) or toks[i + 1][1] != '(':
            continue
        args, end = arguments(toks, i + 1)
        ps = places(toks[max(0, i - 2):end + 1])
        if word in _SCREEN_ASSERTIONS:
            record('TG3', token, ps, True)
        if word == 'toMatchSnapshot' and i >= 2 and toks[i - 1][1] == '.':
            j = i - 2
            if toks[j][1] == ')':
                depth = 1; j -= 1
                while j >= 0 and depth:
                    if toks[j][1] == ')': depth += 1
                    if toks[j][1] == '(': depth -= 1
                    j -= 1
                if j >= 0 and toks[j][1] == 'expect':
                    screen = screen_expr(toks[j + 2:i - 2], screens)
                    record('TG3', token, ps | screen.places, screen.origin is not None)
        if word == 'equals' and i >= 2 and toks[i - 1][1] == '.' and len(args) == 1:
            pair(token, toks[i - 2:i - 1], args[0], screens, ps)
        if word == 'compare' and i >= 2 and toks[i - 2][1] == 'Buffer' and len(args) == 2:
            pair(token, args[0], args[1], screens, ps)
        if word in {'readFile', 'readFileSync', 'writeFile', 'writeFileSync', 'appendFile', 'appendFileSync', 'mkdir', 'mkdirSync', 'unlink', 'unlinkSync'} and i >= 2 and toks[i - 2][1] == 'fs' and args:
            val = value(args[0], env)
            record('TG2', token, places(toks[i - 2:i + 1]) | val.places, _forbidden(val.value, root), val.anchors)
    return out


def _own_nodes(node):
    """실행 영역 하나만 순회한다. 자식 실행 블록·함수 몸통은 scope가 맡는다."""
    yield node
    if isinstance(node, ast.Lambda):
        return
    for field, value in ast.iter_fields(node):
        if field in ('body', 'orelse', 'finalbody', 'handlers', 'cases') and isinstance(value, list):
            continue
        for child in value if isinstance(value, list) else [value]:
            if isinstance(child, ast.AST):
                yield from _own_nodes(child)


def _bound_names(node):
    """지원하지 않는 재바인딩에서도 기존 값·출처를 무효화한다."""
    names = set()
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {node.name}
    if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
        names.add(node.id)
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        names.update(a.asname or a.name.split('.')[0] for a in node.names)
    if isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
        names.add(node.name)
    if isinstance(node, ast.MatchMapping) and node.rest:
        names.add(node.rest)
    if isinstance(node, ast.ExceptHandler) and node.name:
        names.add(node.name)
    for child in ast.iter_child_nodes(node):
        names.update(_bound_names(child))
    return names


def _analyze(source, root, rel):
    tree = ast.parse(source)
    source_tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    out, unsupported = [], set()
    def scope(body, inherited, in_function=False, inherited_screens=None, assignments=None):
        env = dict(inherited)
        screens = dict(inherited_screens or {})
        if assignments is None:
            assignments = {}
            def stores(node):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                    return
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    assignments[node.id] = assignments.get(node.id, []) + [node.lineno]
                for child in ast.iter_child_nodes(node):
                    stores(child)
            for statement in body:
                stores(statement)
        def invalidate(names, places):
            for name in names:
                env[name] = Static(None, places)
                screens[name] = Screen(None, places)
        def shadow(names, places):
            branch, branch_screens = dict(env), dict(screens)
            for name in names:
                branch[name] = Static(None, places)
                branch_screens[name] = Screen(None, places)
            return branch, branch_screens
        def rebound(body):
            names, places = set(), frozenset()
            for statement in body:
                names |= _bound_names(statement)
                for node in ast.walk(statement):
                    if isinstance(node, (ast.Assign, ast.AnnAssign, ast.Import, ast.ImportFrom, ast.NamedExpr)):
                        places |= {node.lineno}
            return names, places
        def screen(node):
            if isinstance(node, ast.Await):
                return screen(node.value)
            if isinstance(node, ast.Name):
                old = screens.get(node.id, Screen())
                return Screen(old.origin, old.places | _places(node))
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'screenshot':
                    return Screen((node.lineno, node.col_offset), _places(node))
                if _call_name(node.func) == 'expect' and node.args:
                    old = screen(node.args[0])
                    return Screen(old.origin, old.places | _places(node))
            return Screen(None, _places(node))
        def record(cid, node, ps, active, slot=0):
            sink_places = _places(node.func) if isinstance(node, ast.Call) else frozenset()
            out.append(Probe(cid, (node.lineno, node.col_offset), ps | sink_places, active, slot))
        def compare(node, left, right, slot=0):
            a, b = screen(left), screen(right)
            operator_places = frozenset(t.start[0] for t in source_tokens if t.type == tokenize.OP and
                                        t.string in ('==', '!=') and
                                        (left.end_lineno, left.end_col_offset) <= t.start < (right.lineno, right.col_offset)) if isinstance(node, ast.Compare) else frozenset()
            record('TG3', node, a.places | b.places | operator_places,
                   a.origin is not None and b.origin is not None and a.origin != b.origin, slot)
        def path_values(node):
            if isinstance(node, (ast.List, ast.Tuple)):
                for child in node.elts:
                    yield from path_values(child)
            else:
                yield _static(node, env, source)
        def inspect(statement):
            for n in _own_nodes(statement):
                if in_function and isinstance(n, ast.Compare):
                    operands = [n.left] + n.comparators
                    for slot, (op, left, right) in enumerate(zip(n.ops, operands, operands[1:])):
                        if isinstance(op, (ast.Eq, ast.NotEq)):
                            compare(n, left, right, slot)
                if not isinstance(n, ast.Call):
                    continue
                name = _call_name(n.func)
                method = n.func.attr if isinstance(n.func, ast.Attribute) else ''
                if method in _SCREEN_ASSERTIONS:
                    record('TG3', n, frozenset().union(*(_places(a) for a in n.args)), True)
                if method == 'toMatchSnapshot':
                    val = screen(n.func.value)
                    record('TG3', n, val.places, val.origin is not None)
                if in_function and method in ('assertEqual', 'assertNotEqual') and len(n.args) >= 2:
                    compare(n, n.args[0], n.args[1])
                inputs = []
                command = None
                command_values = []
                execution_js = None
                if name in _FILE_FUNCTIONS:
                    inputs = n.args[:2] if name.startswith('shutil.') else n.args[:1]
                    inputs += [k.value for k in n.keywords if k.arg in ('file', 'path', 'src', 'dst')]
                elif method in _PATH_METHODS:
                    inputs = [n.func.value]
                elif name in _PROCESS:
                    inputs = list(n.args) + [k.value for k in n.keywords if k.arg in ('args', 'cwd')]
                    command = n.args[0] if n.args else next((k.value for k in n.keywords if k.arg == 'args'), None)
                    if isinstance(command, (ast.List, ast.Tuple)) and command.elts:
                        command_values = [_static(a, env, source) for a in command.elts]
                        executable = command_values[0]
                        runner = executable.runner or (executable.value is not None and Path(executable.value).name in _JS_RUNNERS)
                        execution_js = _node_eval(command_values) if runner else None
                        if execution_js is not None:
                            # eval 코드·옵션 표지·미사용 argv를 Python 경로로 중복 판정하지 않는다.
                            inputs = [command.elts[0]] + [command.elts[i] for i in execution_js[2]]
                            inputs += [k.value for k in n.keywords if k.arg == 'cwd']
                elif name in _SERVER_FUNCTIONS:
                    inputs = list(n.args) + [k.value for k in n.keywords if k.arg in ('source', 'root', 'path')]
                if inputs:
                    vals = [v for arg in inputs for v in path_values(arg)]
                    # 입력 자리별 기준판 사슬도 보존한다(이미 금지인 다른 입력과 섞지 않는다).
                    for slot, val in enumerate(vals):
                        record('TG2', n, val.places, _forbidden(val.value, root), slot)
                    if any(v.value is None and not v.runner for v in vals):
                        unsupported.add(n.lineno)
                if execution_js is not None:
                    code, argv, _ = execution_js
                    js = command_values[code]
                    if js.value is None:
                        unsupported.add(n.lineno)
                        continue
                    if len(js.chars) != len(js.value):
                        raise ValueError('실행 JS의 Python 원본 위치 대응 실패')
                    # 함수 이름·실행기·eval 표지·코드 전달과 JS의 실제 사슬만 연결한다.
                    execution = _places(n.func) | command_values[0].places | command_values[code - 1].places | js.anchors
                    for probe in _js_checks(js.value, root, argv):
                        ps = frozenset(js.chars[pos] for pos in probe.places) | execution | probe.anchors
                        offset = probe.position[0]
                        column = offset - js.value.rfind('\n', 0, offset) - 1
                        out.append(Probe(probe.check_id, (js.chars[offset], column), ps, probe.active, probe.slot))
        for statement in body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                local = dict(env)
                for arg in statement.args.posonlyargs + statement.args.args + statement.args.kwonlyargs + [statement.args.vararg, statement.args.kwarg]:
                    if arg is not None:
                        local[arg.arg] = Static()
                scope(statement.body, local, True)
                invalidate({statement.name}, frozenset({statement.lineno}))
                continue
            if isinstance(statement, ast.ClassDef):
                scope(statement.body, env)
                invalidate({statement.name}, frozenset({statement.lineno}))
                continue
            if isinstance(statement, (ast.With, ast.AsyncWith)):
                outer_env, outer_screens = env, screens
                env, screens = dict(env), dict(screens)
                for item in statement.items:
                    inspect(item.context_expr)
                    if item.optional_vars:
                        invalidate(_bound_names(item.optional_vars), _places(item.optional_vars))
                scope(statement.body, env, in_function, screens, assignments)
                env, screens = outer_env, outer_screens
            else:
                inspect(statement)
            if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
                val = _static(statement.value, env, source)
                captured = screen(statement.value)
                for target in targets:
                    if isinstance(target, ast.Name):
                        env[target.id] = Static(val.value, val.places | _places(target), val.chars, val.runner, val.anchors | _places(target))
                        writes = assignments.get(target.id, [])
                        if len(writes) == 1 and not isinstance(statement.value, ast.Name):
                            screens[target.id] = Screen(captured.origin, captured.places | _places(target))
                        else:
                            screens[target.id] = Screen(None, captured.places | _places(target) | frozenset(writes))
                    else:
                        invalidate(_bound_names(target), _places(target))
                continue
            if isinstance(statement, (ast.For, ast.AsyncFor)):
                ps = _places(statement.target)
                branch, branch_screens = shadow(_bound_names(statement.target), ps)
                scope(statement.body, branch, in_function, branch_screens, assignments)
                scope(statement.orelse, branch, in_function, branch_screens, assignments)
            elif isinstance(statement, (ast.With, ast.AsyncWith)):
                pass  # 항목별 검사·바인딩·몸통을 위에서 이미 실행했다.
            elif isinstance(statement, (ast.Try, ast.TryStar)):
                scope(statement.body, env, in_function, screens, assignments)
                branch, branch_screens = shadow(*rebound(statement.body))
                for handler in statement.handlers:
                    handler_env, handler_screens = dict(branch), dict(branch_screens)
                    if handler.name:
                        handler_env[handler.name] = Static(None, frozenset({handler.lineno}))
                        handler_screens[handler.name] = Screen(None, frozenset({handler.lineno}))
                    scope(handler.body, handler_env, in_function, handler_screens, assignments)
                scope(statement.orelse, branch, in_function, branch_screens, assignments)
                prior_body = statement.body + statement.orelse + [s for h in statement.handlers for s in h.body]
                final_env, final_screens = shadow(*rebound(prior_body))
                scope(statement.finalbody, final_env, in_function, final_screens, assignments)
            elif isinstance(statement, ast.Match):
                for case in statement.cases:
                    branch, branch_screens = shadow(_bound_names(case.pattern), _places(case.pattern))
                    scope(case.body, branch, in_function, branch_screens, assignments)
            else:
                for field in ('body', 'orelse'):
                    nested = getattr(statement, field, None)
                    if isinstance(nested, list):
                        scope(nested, env, in_function, screens, assignments)
            names = _bound_names(statement)
            if any(isinstance(n, ast.ImportFrom) and any(a.name == '*' for a in n.names) for n in ast.walk(statement)):
                names |= set(env)
            # 부모의 사슬에 블록 전체 행을 넣지 않고 실제 바인딩 자리만 넣는다.
            for name in names:
                ps = frozenset(n.lineno for n in ast.walk(statement) if hasattr(n, 'lineno') and
                               (name in _bound_names(n) or isinstance(n, ast.ImportFrom) and any(a.name == '*' for a in n.names)) and
                               not isinstance(n, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.TryStar, ast.Match)))
                invalidate({name}, ps)
    scope(tree.body, {'__file__': Static(str(root / rel))})
    return out, unsupported


def _content_tests(ctx: BackstopContext) -> List[Finding]:
    """TG2 지원: .dddjango-web 경로·루트 밖 절대 경로·Path.home()/~/ 경로를
    문자열 연결·Path 결합·__file__/parent/parents[n]·모듈 상수→함수 및 지역 대입에서 I/O·실행 인자로 추적한다.
    파일 I/O는 open/io.open/os.open·Path의 open/read_text/read_bytes/write_text/write_bytes/mkdir/unlink/iterdir/glob/rglob,
    os의 mkdir/makedirs/remove/unlink·shutil의 copy/copy2/copyfile/copytree/move/rmtree를 지원한다.
    서버는 fixture_server/start_server/run_server, 프로세스는 subprocess의 run/Popen/call/check_call/check_output이다.
    IfExp의 조건·각 가지, BoolOp, with 항목·호출 인자 안의 직접 sink 호출도 순회한다.
    with/async with는 각 항목의 표현식 검사 뒤 그 항목의 바인딩을 무효화하고 다음 항목을 검사한다.
    분기 뒤 이름 무효화는 문장 수준 재바인딩에 적용하며 조건식 결과의 값 합류는 추론하지 않는다.
    Python 안 JS는 list/tuple 명령의 node/nodejs/node.exe 정적 이름 또는 shutil.which 출처가 확정된 실행기의
    -- 옵션 종료·스크립트 entry point 앞의 -e/--eval/-p/--print 정적 문자열만 실행 코드로 추출한다.
    확정된 eval 명령은 실행기·값을 받는 옵션·cwd만 일반 Python 경로 검사에 남기며,
    코드·옵션 표지·미사용 argv는 일반 경로로 다시 판정하지 않는다. JS I/O에 실제 사용한
    process.argv.slice(1) 배열 분해·process.argv[정수]만 argv 출처를 연결한다.
    디코드 문자→Python 원본 행과 정의·중간 대입·실행 인자를 보존한다.
    TG3 지원: to_have_screenshot·toHaveScreenshot, screenshot 수신값의 toMatchSnapshot,
    같은 함수의 서로 다른 sync/async screenshot 생성 출처 두 개의 인접 ==/!=·assertEqual/assertNotEqual,
    실행 JS의 같은 블록 .equals/Buffer.compare 비교(세미콜론 없는 ASI 대입 포함).
    단언 API에는 두 생성 출처 조건을 적용하지 않는다.
    게이트: 기준 commit→작업 트리(staged·unstaged·커밋 포함)의 새쪽 추가 줄과 실제 사슬 위치의 교집합,
    또는 기준판의 안전 대입·출처 무효화 삭제로 같은 sink에 새 금지 사슬이 닿았음이 확인된 경우만 발화한다.
    TG2 사슬 위치는 정의·대입의 값 식·해당 입력 식·호출 함수 이름으로 한정한다.
    TG3 비교 사슬은 비교 두 입력·두 screenshot 생성 출처·호출 함수 이름(==/!=는 연산자) 위치로 한정한다.
    호출·함수·블록 전체와 다른 인자·키워드·JS 미사용 argv의 줄은 사슬에 넣지 않는다.
    순수 시험 rename·무관한 줄 이동은 제외한다. copy·시험 밖 편입·기준판에 없는 미추적은 전 줄 새 줄이다.
    G0 기록의 읽기·JSON·snapshot·test_command 형상/quoting 실패는 그 기록만 건너뛴다.
    기준점·old/new 대응·Python/JS 위치 해석 실패는 범위 미확정·미실행을 고지하며 파일 전체로 퇴화하지 않는다.
    제외: 주석·docstring·URL·I/O에 쓰이지 않는 검증 대상 경로·도구 탐색 자체·알 수 없는 명령의 eval 인자,
    갈무리 자체·자기 비교·일반 bytes/텍스트 snapshot·screenshot 이름 별칭·재대입 screenshot·다른 스코프·문자열/정규식의 가짜 호출.
    typeof/void/delete/in/instanceof/return/throw/case/yield/await 뒤 정규식도 코드에서 제외한다.
    동적 경로·shell 명령 문자열·함수 인자/반환/타 파일 전달·파일 저장 후 재읽기·해시·자유 하니스·환경 변수 단언은 자동 판정 밖이다.
    shutil.which 도구 탐색 결과는 경로 금지에서 제외하지만 하드코딩된 루트 밖 실행 파일 절대 경로는 TG2 대상이다.
    미지원 흐름은 무관함의 증명이 아니며 discipline 감수와 G2 표준 실행이 확인한다.
    """
    out: List[Finding] = []
    for change in _changed_tests(ctx):
        try:
            probes, unsupported = _analyze(change.source, ctx.root, change.path)
            old_probes, _ = _analyze(change.before, ctx.root, change.path)
            previous = {}
            for old in old_probes:
                mapped = change.old_to_new.get(old.position[0])
                if mapped is not None:
                    key = (old.check_id, mapped, old.position[1], old.slot)
                    previous.setdefault(key, []).append(old)
            found = set()
            for probe in probes:
                if not probe.active:
                    continue
                added = bool(probe.places & change.added)
                prior = previous.get((probe.check_id, *probe.position, probe.slot), [])
                # 같은 sink의 기준판 안전/무효화 사슬에 실제 삭제가 있을 때만 삭제 인과를 인정한다.
                deletion = prior and not any(p.active for p in prior) and any(p.places & change.deleted for p in prior)
                if added or deletion:
                    found.add((probe.check_id, probe.position[0]))
            if unsupported:
                ctx.notices.append('[info] TG2 일부 흐름 자동 판정 밖 — %s:%s 동적/미지원 입력은 무관함의 증명이 아니며 discipline 감수 대상' %
                                   (change.path, ','.join(map(str, sorted(unsupported)))))
        except (SyntaxError, ValueError, IndexError, tokenize.TokenError) as error:
            ctx.notices.append('[info] TG2·TG3 미실행 — %s 기준판/현재판·위치 해석 실패 · 변경 시험 범위 미확정: %s' % (change.path, error))
            continue
        for cid, line in sorted(found, key=lambda item: (item[1], item[0])):
            out.append(Finding(cid, change.path, line,
                '영구 시험이 기록 폴더·머신 고정 경로를 I/O·실행에 사용한다' if cid == 'TG2' else '영구 시험이 비채택 스크린샷 이미지 비교를 사용한다',
                'implementation-test §4·§7 / discipline-test' if cid == 'TG2' else 'implementation-test §8 / discipline-test §4',
                '고정물은 시험 트리, 실행 기록은 tmp_path에 둔다. 레인 변수 재현성은 표준 실행으로 확인한다.' if cid == 'TG2' else '명세 행위·관찰값을 단언한다. 사람 눈 확인용 갈무리는 유지한다.', root_rel=True))
    return out


def run_tests(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = _content_tests(ctx)
    out.extend(_test_presence(ctx))
    return out


def _test_presence(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    if not ctx.can_detect_new_units:
        ctx.notices.append('[info] TG1(행위테스트) 생략 — git 기준점 없음(신규 BC 판별 불가)')
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
