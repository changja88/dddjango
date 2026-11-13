#!/usr/bin/env python3
"""경로 앞 응답 정본의 한 출처 — 참조 글 코드 블록 = 검사기 정본 자산(F4-173 · 2026-11-13).

#63(check-openapi-error-declaration)은 프로젝트의 `framework/ninja/pre_route_responses.py` 를 검사기 옆
자산 `dddjango/scripts/pre_route_responses_canonical.py` 와 AST 로 대조하고, coder 는 그 파일을
implementation-django-ninja 참조 글의 정본 코드 블록에서 글자 그대로 옮긴다. 둘이 어긋나면 글대로 짠
프로젝트가 검사기에 막힌다. 이 시험이 지킨다.

  ① 자산 ↔ Codex byte 미러 · 픽스처(`workspace/eval/fixtures/openapi_*`)의 정본 사본도 byte 동일.
  ② 참조 글(Claude · Codex)에서 `def add_pre_route_responses(` 를 담은 ```python 블록이 정확히 하나이고,
     그 블록 글(펜스 사이 줄 + 끝 줄바꿈)이 자산과 byte 동일.
  ③ 루트 API 클래스 꼴(3.2) — #63 · #437 두 검사기와 pre-gate(`design_pregate.py` — 루트 API 클래스 스텁을 이 글로
     렌더한다)의 `DOCUMENTED_API_METHOD` 글이 같고, 참조 글에
     `def get_openapi_schema(` 를 담은 ```python 블록이 있으며 그 클래스 메서드가 그 글과 AST 동일.

검출력 self-test(빠진 블록 · 한 글자 다른 블록 · 블록 둘 · 다른 메서드 · 검사기 상수 어긋남)가 늘 먼저 돈다.

exit 0 = 일치 · 2 = 어긋남 · 1 = 재료 결손.
사용: python3 workspace/tools/pre_route_canonical_check.py
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
ASSET: Path = ROOT / "dddjango" / "scripts" / "pre_route_responses_canonical.py"
ASSET_MIRROR: Path = ROOT / "codex-dddjango" / "skills" / "dddjango" / "scripts" / "pre_route_responses_canonical.py"
REFERENCES: tuple[Path, ...] = (
    ROOT / "dddjango" / "skills" / "implementation-django-ninja" / "references" / "final.md",
    ROOT / "codex-dddjango" / "skills" / "implementation-django-ninja" / "references" / "final.md",
)
CHECKERS: tuple[Path, ...] = (
    ROOT / "dddjango" / "scripts" / "check-openapi-error-declaration.py",
    ROOT / "dddjango" / "scripts" / "check-composition-root.py",
    ROOT / "dddjango" / "scripts" / "design_pregate.py",
)
FIXTURE_COPIES: str = "workspace/eval/fixtures/openapi_*/**/framework/ninja/pre_route_responses.py"
CANONICAL_MARK: str = "def add_pre_route_responses("
METHOD_MARK: str = "def get_openapi_schema("
FENCE_RE: re.Pattern[str] = re.compile(r"^```python[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
METHOD_CONSTANTS: tuple[str, ...] = ("DOCUMENTED_API_METHOD", "_DOCUMENTED_API_METHOD")


def python_blocks(text: str) -> list[str]:
    return [match.group(1) for match in FENCE_RE.finditer(text)]


def method_constant(source: str) -> str | None:
    """검사기 소스에서 3.2 메서드 글 상수(괄호로 이은 글자 조각들)를 읽는다."""
    tree = ast.parse(source)
    for statement in tree.body:
        targets = statement.targets if isinstance(statement, ast.Assign) else (
            [statement.target] if isinstance(statement, ast.AnnAssign) and statement.value is not None else []
        )
        if any(isinstance(t, ast.Name) and t.id in METHOD_CONSTANTS for t in targets):
            value = ast.literal_eval(statement.value)  # type: ignore[arg-type]
            return value if isinstance(value, str) else None
    return None


def documented_method_dump(block: str) -> str | None:
    """블록 안 루트 API 클래스의 `get_openapi_schema` 메서드 AST(없으면 None)."""
    try:
        tree = ast.parse(block)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for member in node.body:
                if isinstance(member, ast.FunctionDef) and member.name == "get_openapi_schema":
                    return ast.dump(member, include_attributes=False)
    return None


def problems_for(asset: str, references: dict[str, str], methods: dict[str, str | None]) -> list[str]:
    problems: list[str] = []
    method_texts = set(methods.values())
    if None in method_texts or len(method_texts) != 1:
        problems.append(f"③ 3.2 메서드 글 상수가 검사기마다 다르거나 없다: {sorted(name for name, v in methods.items() if v is None)}")
        expected_method: str | None = None
    else:
        expected_method = ast.dump(ast.parse(next(iter(method_texts)) or "").body[0], include_attributes=False)
    for name, text in references.items():
        blocks = python_blocks(text)
        canonical = [block for block in blocks if CANONICAL_MARK in block]
        if len(canonical) != 1:
            problems.append(f"② {name}: `{CANONICAL_MARK}` 를 담은 python 블록이 {len(canonical)}개다(정확히 하나여야 한다)")
        elif canonical[0] != asset:
            got = canonical[0].splitlines()
            want = asset.splitlines()
            line = next((i + 1 for i, (a, b) in enumerate(zip(got, want)) if a != b), min(len(got), len(want)) + 1)
            problems.append(f"② {name}: 정본 코드 블록이 자산 `{ASSET.name}` 과 다르다(블록 {line}번째 줄부터)")
        if expected_method is not None:
            dumps = [documented_method_dump(block) for block in blocks if METHOD_MARK in block and CANONICAL_MARK not in block]
            if not dumps:
                problems.append(f"③ {name}: `{METHOD_MARK}` 를 담은 루트 API 클래스 python 블록이 없다")
            elif expected_method not in dumps:
                problems.append(f"③ {name}: 루트 API 클래스 블록의 메서드가 검사기의 정해진 꼴과 AST 가 다르다")
    return problems


def self_test(asset: str, method: str) -> list[str]:
    """빠진 블록 · 한 글자 다른 블록 · 다른 메서드가 붉은지(검출력) — 맞는 글은 초록인지."""
    good_class = (
        "class DocumentedAPI(NinjaExtraAPI):\n"
        + "".join(f"    {line}\n" if line else "\n" for line in method.splitlines())
    )
    good = f"```python\n{asset}```\n\n```python\n{good_class}```\n"
    methods = {"a": method, "b": method}
    cases = {
        "맞는 글": (good, True),
        "정본 블록 없음": (f"```python\n{good_class}```\n", False),
        "정본 한 글자 다름": (good.replace("def _add(", "def _add_(", 1), False),
        "정본 블록 둘": (good + f"```python\n{asset}```\n", False),
        "3.2 메서드 다름": (good.replace("path_prefix=path_prefix,", "path_prefix=None,"), False),
    }
    failures: list[str] = []
    for label, (text, ok) in cases.items():
        found = problems_for(asset, {"t": text}, methods)
        if bool(found) == ok:
            failures.append(f"self-test «{label}»: 기대 {'초록' if ok else '붉음'} · 실제 {found or '초록'}")
    if not problems_for(asset, {"t": good}, {"a": method, "b": method + "#"}):
        failures.append("self-test «검사기 상수 어긋남»: 붉어야 한다")
    return failures


def main(argv: list[str]) -> int:
    try:
        asset = ASSET.read_text(encoding="utf-8")
        mirror = ASSET_MIRROR.read_bytes()
        references = {str(path.relative_to(ROOT)): path.read_text(encoding="utf-8") for path in REFERENCES}
        methods = {str(path.relative_to(ROOT)): method_constant(path.read_text(encoding="utf-8")) for path in CHECKERS}
    except (OSError, UnicodeError, SyntaxError, ValueError) as exc:
        print(f"재료 결손: {exc}", file=sys.stderr)
        return 1
    problems: list[str] = []
    if mirror != asset.encode("utf-8"):
        problems.append(f"① 자산 Codex 미러가 byte 동일이 아니다: {ASSET_MIRROR.relative_to(ROOT)}")
    copies = sorted(ROOT.glob(FIXTURE_COPIES))
    if not copies:
        problems.append(f"① 픽스처 정본 사본이 하나도 없다: {FIXTURE_COPIES}")
    for copy in copies:
        if copy.read_bytes() != asset.encode("utf-8"):
            problems.append(f"① 픽스처 정본 사본이 자산과 byte 동일이 아니다: {copy.relative_to(ROOT)}")
    method = next((value for value in methods.values() if value), "")
    problems.extend(self_test(asset, method))  # 검출력 — 늘 돈다
    problems.extend(problems_for(asset, references, methods))
    for problem in problems:
        print(problem)
    if problems:
        print(f"pre-route canonical check: 어긋남 {len(problems)}")
        return 2
    print("pre-route canonical check: 참조 글 정본 블록 = 자산 · 3.2 메서드 글 일치")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
