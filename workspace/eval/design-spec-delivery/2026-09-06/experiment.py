"""고정 명세의 무손실 전달·조회·제한된 출력 채점. 배포하지 않는 실험 코드."""

import ast
import hashlib
import math
import re
from collections import Counter, defaultdict


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_utf8(text: str, limit: int) -> list[str]:
    if limit < 1:
        raise ValueError("positive byte limit required")
    chunks: list[str] = []
    current: list[str] = []
    size = 0
    for char in text:
        width = len(char.encode("utf-8"))
        if width > limit:
            raise ValueError("one codepoint exceeds byte limit")
        if size + width > limit:
            chunks.append("".join(current))
            current, size = [], 0
        current.append(char)
        size += width
    if current:
        chunks.append("".join(current))
    return chunks


def make_units(text: str) -> list[dict]:
    units: list[dict] = []
    heading = ""
    fence = ""
    occurrences: Counter = Counter()
    for line_number, line in enumerate(text.splitlines(keepends=True), 1):
        stripped = line.lstrip()
        marker = re.match(r"(`{3,}|~{3,})", stripped)
        if marker:
            token = marker.group(1)
            if not fence:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = ""
        elif not fence:
            match = re.match(r"#{1,6}\s+(.+)", stripped)
            if match:
                heading = match.group(1).strip()
        if line.strip():
            key = digest(line)[:20]
            occurrences[key] += 1
            units.append({"id": f"u-{key}-{occurrences[key]}", "line": line_number,
                          "text": line, "heading": heading})
    return units


def words(text: str) -> list[str]:
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    tokens = re.findall(r"[a-z0-9]+|[가-힣]+", text.lower())
    return [piece for word in tokens for piece in
            ([word] + ([word[i:i + 2] for i in range(len(word) - 1)]
                       if re.fullmatch(r"[가-힣]{3,}", word) else []))]


def rank_units(units: list[dict], query: str, contextual: bool = False) -> list[str]:
    if not units:
        return []
    terms = set(words(query))
    bags = [Counter(words(u["text"] + (" " + u["heading"] if contextual else ""))) for u in units]
    lengths = [sum(b.values()) for b in bags]
    average = sum(lengths) / len(lengths) or 1
    frequency = Counter(t for bag in bags for t in bag)
    scores: list[tuple[float, int, str]] = []
    for unit, bag, length in zip(units, bags, lengths):
        score = 0.0
        for term in terms & bag.keys():
            inverse = math.log(1 + (len(units) - frequency[term] + 0.5) / (frequency[term] + 0.5))
            count = bag[term]
            score += inverse * count * 2.2 / (count + 1.2 * (0.25 + 0.75 * length / average))
        if score > 0:
            scores.append((-score, unit["line"], unit["id"]))
    return [key for _, _, key in sorted(scores)]


def select_budget(units: list[dict], ranked: list[str], budget: int) -> list[dict]:
    by_id = {u["id"]: u for u in units}
    selected: list[dict] = []
    seen: set[str] = set()
    used = 0
    for key in ranked:
        if key in seen:
            continue
        seen.add(key)
        unit = by_id[key]
        size = len(unit["text"].encode())
        if used + size <= budget:
            selected.append(unit)
            used += size
    return selected


def closure(seeds: list[str], edges: list[tuple[str, str]]) -> list[str]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for source, target in edges:
        adjacency[source].add(target)
    seen: set[str] = set()
    pending = list(seeds)
    while pending:
        key = pending.pop()
        if key not in seen:
            seen.add(key)
            pending.extend(adjacency[key] - seen)
    return sorted(seen)


def explicit_edges(units: list[dict]) -> list[tuple[str, str]]:
    """명세의 § 참조만 연결한다. 의미상 빠진 참조를 추정하지 않는다."""
    section_units: dict[str, list[str]] = defaultdict(list)
    for unit in units:
        match = re.match(r"(\d+(?:\.\d+)*)(?:[.\s]|$)", unit["heading"])
        if match:
            section_units[match.group(1)].append(unit["id"])
    edges: set[tuple[str, str]] = set()
    for unit in units:
        for section in re.findall(r"§\s*(\d+(?:\.\d+)*)", unit["text"]):
            for target in section_units.get(section, []):
                if target != unit["id"]:
                    edges.add((unit["id"], target))
    return sorted(edges)


def check_index(digest: str, current: str, nodes: list[str], edges: list[tuple[str, str]]) -> None:
    if digest != current:
        raise ValueError("stale source digest")
    known = set(nodes)
    if any(a not in known or b not in known for a, b in edges):
        raise ValueError("dangling reference")


def coverage(units: list[dict], obligations: list[dict]) -> dict:
    lines = {u["line"] for u in units}
    passed, missing = [], []
    for obligation in obligations:
        matched = any(set(group) <= lines for group in obligation["supports"])
        (passed if matched else missing).append(obligation["id"])
    return {"passed": passed, "missing": missing, "all_pass": not missing}


class InvalidSpeechSituation(Exception):
    """실험용 독립 예외 — 원 프로젝트 모듈·환경에는 접근하지 않는다."""


def _guard_function(code: str, *, allow_replace: bool = False):
    """부작용 없는 직선 분기 함수만 허용한다. 일반 Python sandbox는 아니다."""
    if not isinstance(code, str) or len(code) > 16000:
        raise ValueError("missing or oversized code")
    tree = ast.parse(code)
    permitted = (ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.If,
                 ast.Compare, ast.Name, ast.Load, ast.Store, ast.Constant,
                 ast.Raise, ast.Call, ast.Attribute, ast.Subscript, ast.Assign,
                 ast.AnnAssign, ast.Return, ast.In, ast.NotIn, ast.Is, ast.IsNot,
                 ast.Eq, ast.NotEq, ast.UnaryOp, ast.Not, ast.BoolOp, ast.Or,
                 ast.And, ast.IfExp, ast.keyword, ast.Expr, ast.Dict, ast.List,
                 ast.Tuple, ast.BinOp, ast.BitOr, ast.JoinedStr, ast.FormattedValue)
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise ValueError("one function required")
    function = tree.body[0]
    if function.name != "render_situation" or function.decorator_list:
        raise ValueError("unexpected function or decorators")
    if [a.arg for a in function.args.args] != ["templates", "situation", "subject"]:
        raise ValueError("wrong function arguments")
    if function.args.defaults or function.args.kw_defaults or function.args.vararg or function.args.kwarg:
        raise ValueError("defaults or variadics forbidden")
    for node in ast.walk(tree):
        if not isinstance(node, permitted):
            raise ValueError(f"unsupported AST: {type(node).__name__}")
        if isinstance(node, ast.FunctionDef) and node is not function:
            raise ValueError("nested functions forbidden")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise ValueError("private introspection forbidden")
        if isinstance(node, ast.Attribute) and node.attr not in {"strip", "format", "get"} and not (allow_replace and node.attr == "replace"):
            raise ValueError("unexpected attribute")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id not in {"InvalidSpeechSituation", "str"}:
                raise ValueError("unexpected call")
            if not isinstance(node.func, (ast.Name, ast.Attribute)):
                raise ValueError("indirect call forbidden")
    # 어노테이션은 실행하지 않는다. 함수의 동작만 제한된 값으로 검사한다.
    function.returns = None
    for arg in function.args.args + function.args.kwonlyargs:
        arg.annotation = None
    namespace = {"__builtins__": {}, "InvalidSpeechSituation": InvalidSpeechSituation, "str": str}
    exec(compile(tree, "<isolated-guard-probe>", "exec"), namespace)
    return namespace["render_situation"]


def grade_guard(code: str, *, allow_replace: bool = False) -> dict:
    templates = {"PROFILE_INPUT_REQUEST": "정보 중 {subject} 필요", "NO_CHARACTER": "없음",
                 "REQUEST_CANCELLED": "취소", "NEW_PLACEHOLDER": "추가 {subject}"}
    cases = [("none", "PROFILE_INPUT_REQUEST", None, None),
             ("empty", "PROFILE_INPUT_REQUEST", "", None),
             ("spaces", "PROFILE_INPUT_REQUEST", " \t ", None),
             ("valid", "PROFILE_INPUT_REQUEST", "생년월일시", "정보 중 생년월일시 필요"),
             ("preserve_whitespace", "PROFILE_INPUT_REQUEST", " 이름 ", "정보 중  이름  필요"),
             ("no_placeholder_none", "NO_CHARACTER", None, "없음"),
             ("no_placeholder_blank", "REQUEST_CANCELLED", "  ", "취소"),
             ("outside_table", "OUTSIDE", "정상", None),
             ("new_placeholder", "NEW_PLACEHOLDER", None, None),
             ("new_placeholder_valid", "NEW_PLACEHOLDER", "값", "추가 값")]
    try:
        function = _guard_function(code, allow_replace=allow_replace)
    except (SyntaxError, ValueError, TypeError) as error:
        return {"passed": [], "missing": ["safe_executable_function"], "all_pass": False, "error": str(error)}
    passed, missing = [], []
    for name, situation, subject, expected in cases:
        try:
            value = function(dict(templates), situation, subject)
            ok = expected is not None and value == expected
        except InvalidSpeechSituation:
            ok = expected is None
        except Exception:
            ok = False
        (passed if ok else missing).append(name)
    return {"passed": passed, "missing": missing, "all_pass": not missing}


def grade_constructor(answer: dict) -> dict:
    expected = {"request_required": True, "request_nullable": True,
                "loader_argument": "request=request", "callers_first": True,
                "new_test_cases_required": False, "new_assertions_required": False,
                "prepared_file_count": 6, "prepared_constructor_calls": 7,
                "remaining_production_change": "remove_default_only"}
    passed, missing = [], []
    for key, value in expected.items():
        observed = answer.get(key)
        ok = type(observed) is type(value) and observed == value
        if key == "loader_argument" and isinstance(observed, str):
            try:
                expected_ast = ast.dump(ast.parse("load(request=request)", mode="eval"))
                observed_ast = ast.dump(ast.parse("load(" + observed + ")", mode="eval"))
                ok = observed_ast == expected_ast
            except SyntaxError:
                ok = False
        (passed if ok else missing).append(key)
    return {"passed": passed, "missing": missing, "all_pass": not missing}
