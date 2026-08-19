#!/usr/bin/env python3
"""dddjango 선언된 choices 값의 *리터럴 소비* 결정적 백스톱 (cleancode §2.14 소비 규율).

Enum/choices 를 **선언해 놓고** 소비처가 원시 문자열 리터럴을 쓰는 직접형 두 가지만 잡는다:
  (a) 같은 필드 호출 안에서 `choices=` 가 심볼 출처(Name/Attribute/컴프리헨션)인데
      `default="리터럴"` 을 쓴 경우 — 같은 호출 노드라 모호성 0.
  (b) 심볼-choices 필드가 확인된 모델의 직접 호출형
      `<Model>.objects.filter/exclude(<field>="리터럴")`(`<field>__in=[리터럴…]` 포함).

**보지 않는 것(의미 레인 = discipline-reviewer 몫)**: 변수 우회, 간접 queryset(`qs.filter`),
비교식(`x.status == "…"`), 닫힌 집합의 *미승격*, 계층 역참조, 테스트의 상수 역수입. 범용
magic-string 검사는 오탐으로 생태계에서 기각된 부류라 시도하지 않는다(TSLint 기각·ruff str
기본 면제) — 이 게이트는 '선언된 심볼의 존재'에 앵커된 부분집합만 결정적으로 강제한다.

거짓 양성 회피 — AND 합성으로만 차단:
  1) git 레포면 이번 변경에서 touched(신규 `??`/`A` 또는 수정 `M`)인 파일만 본다.
     수정 파일은 **추가된 라인**(git diff -U0)에 위반 라인이 있을 때만 잡는다 — 기존
     리터럴은 grandfather. **git 이 아니면 «전 파일을 touched 로 간주»하고 그 사실을
     출력한다**(fail-closed · 명세 조각 ⓐ — 비-git 스킵은 검사가 꺼진 것이지 깨끗한
     것이 아니다).
  3) `migrations/`·테스트 경로(`test`/`tests` 디렉터리·`test_*.py`·`conftest.py`)는 면제 —
     마이그레이션은 historical value 동결(`implementation-django` §10.4)이 오히려 규율이고,
     테스트 기댓값 리터럴은 `implementation-test` §15.4 가 허용·강제한다.
  4) `choices=` 가 리터럴 목록(인라인 List/Tuple/Dict)이면 참조할 심볼이 없으므로 비대상.
  5) `default=OrderStatus.PENDING.value`(Attribute) 등 비-Constant 는 정상(.value 평탄화 —
     `implementation-django` §2.5)이라 잡지 않는다.

사용법: check-choices-literal-consumption.py [TARGET_DIR]   (기본=현재 디렉터리)
종료코드: 0=clean(또는 해당 없음), 2=blocker(발견 출력), 1=사용 오류.
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys

import checker_target
from findings import ContractFindings
from pathlib import Path

# rule-owner-map 규칙 0건 — 선행 계약 소유(reverse_coverage PRIOR_CONTRACT_SCRIPTS 등재).
CONTRACT_REF = "선행 계약(2026-07-06 상수 승격) 소유"

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango"}
EXEMPT_DIR_NAMES = {"test", "tests", "migrations"}
MODEL_SUFFIX = "Model"
NON_MODEL_BASES = {"BaseModel"}  # pydantic 등 — ORM 모델로 오인 금지.
HUNK_RE = re.compile(r"^@@ [^+]*\+(\d+)(?:,(\d+))? @@")


def _is_exempt_path(rel: Path) -> bool:
    parts = set(rel.parts)
    if parts & SKIP_DIRS or parts & EXEMPT_DIR_NAMES:
        return True
    name = rel.name
    return name.startswith("test_") or name == "conftest.py"


def _git_touched(root: Path) -> dict[Path, str] | None:
    """touched .py 파일 → porcelain XY. git 아님/실패면 None(fail-open)."""
    if not (root / ".git").exists():
        return None
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if res.returncode != 0:
        return None
    out: dict[Path, str] = {}
    for line in res.stdout.splitlines():
        if len(line) < 4:
            continue
        code, rel_str = line[:2], line[3:].strip().strip('"')
        if " -> " in rel_str:  # rename: 새 경로만.
            rel_str = rel_str.split(" -> ", 1)[1]
        rel = Path(rel_str)
        if rel.suffix == ".py":
            out[rel] = code
    return out


def _added_lines(root: Path, rel: Path, code: str) -> set[int] | None:
    """이번 변경에서 *추가된* 라인 번호 집합. None=전체 라인(신규 파일)."""
    if "?" in code or "A" in code:
        return None  # 신규 파일 — 전 라인이 추가분.
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "diff", "HEAD", "--unified=0", "--no-color", "--", str(rel)],
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return set()
    if res.returncode != 0:
        return set()
    lines: set[int] = set()
    for ln in res.stdout.splitlines():
        m = HUNK_RE.match(ln)
        if m:
            start = int(m.group(1))
            count = int(m.group(2)) if m.group(2) is not None else 1
            lines.update(range(start, start + count))
    return lines


def _is_model_base(base: ast.expr) -> bool:
    if isinstance(base, ast.Attribute):
        name = base.attr
    elif isinstance(base, ast.Name):
        name = base.id
    else:
        return False
    if name in NON_MODEL_BASES:
        return False
    return name == MODEL_SUFFIX or name.endswith(MODEL_SUFFIX)


def _is_symbol_choices(value: ast.expr) -> bool:
    """choices= 값이 심볼 출처인가 — Name/Attribute/컴프리헨션. 리터럴 컬렉션·호출식은 제외."""
    return isinstance(value, (ast.Name, ast.Attribute, ast.ListComp, ast.GeneratorExp))


def _field_call_kwargs(stmt: ast.stmt) -> tuple[str, ast.Call] | None:
    """클래스 본문의 `name = <Call>(...)` 필드 대입 → (필드명, 호출 노드)."""
    if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
        target, value = stmt.targets[0].id, stmt.value
    elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.value is not None:
        target, value = stmt.target.id, stmt.value
    else:
        return None
    if not isinstance(value, ast.Call):
        return None
    return target, value


def _scan_models(tree: ast.Module) -> tuple[dict[str, set[str]], list[tuple[int, str, str]]]:
    """모듈의 모델들에서 (심볼-choices 필드 레지스트리, (a)형 위반 목록) 추출.
    위반 항목: (라인, 모델명, 필드명)."""
    registry: dict[str, set[str]] = {}
    violations: list[tuple[int, str, str]] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if not any(_is_model_base(b) for b in node.bases):
            continue
        for stmt in node.body:
            parsed = _field_call_kwargs(stmt)
            if parsed is None:
                continue
            field_name, call = parsed
            choices_kw = next((k for k in call.keywords if k.arg == "choices"), None)
            if choices_kw is None or not _is_symbol_choices(choices_kw.value):
                continue
            registry.setdefault(node.name, set()).add(field_name)
            default_kw = next((k for k in call.keywords if k.arg == "default"), None)
            if (
                default_kw is not None
                and isinstance(default_kw.value, ast.Constant)
                and isinstance(default_kw.value.value, str)
            ):
                violations.append((default_kw.value.lineno, node.name, field_name))
    return registry, violations


def _objects_call_model(call: ast.Call) -> str | None:
    """`<Name>.objects.filter/exclude(...)` 직접 호출형이면 모델명 반환."""
    f = call.func
    if not (isinstance(f, ast.Attribute) and f.attr in ("filter", "exclude")):
        return None
    obj = f.value
    if not (isinstance(obj, ast.Attribute) and obj.attr == "objects" and isinstance(obj.value, ast.Name)):
        return None
    return obj.value.id


def _scan_filter_literals(
    tree: ast.Module, registry: dict[str, set[str]]
) -> list[tuple[int, str, str]]:
    """(b)형: 레지스트리 모델의 직접 filter/exclude 에서 str 리터럴(또는 __in 리터럴 목록) kwarg."""
    violations: list[tuple[int, str, str]] = []
    for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
        model = _objects_call_model(call)
        if model is None or model not in registry:
            continue
        fields = registry[model]
        for kw in call.keywords:
            if kw.arg is None:
                continue
            base, _, lookup = kw.arg.partition("__")
            if base not in fields:
                continue
            if lookup == "" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                violations.append((kw.value.lineno, model, kw.arg))
            elif lookup == "in" and isinstance(kw.value, (ast.List, ast.Tuple, ast.Set)):
                elts = kw.value.elts
                if elts and all(
                    isinstance(e, ast.Constant) and isinstance(e.value, str) for e in elts
                ):
                    violations.append((kw.value.lineno, model, kw.arg))
    return violations


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    bad_target_reason = checker_target.bc_shaped_target_reason(root)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not root.is_dir():
        print(f"[check-choices-literal-consumption] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    touched = _git_touched(root)

    # 레지스트리는 레포 전체(면제 경로 제외)에서 구축 — 필터 위반은 touched 파일이지만
    # 모델 선언은 기존(untouched) 파일에 있을 수 있다.
    registry: dict[str, set[str]] = {}
    trees: dict[Path, ast.Module] = {}
    for f in sorted(root.rglob("*.py")):
        rel = f.relative_to(root)
        if _is_exempt_path(rel):
            continue
        try:
            mod_tree = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue  # 파싱 불가 파일은 판정 유보.
        trees[rel] = mod_tree
        file_registry, _ = _scan_models(mod_tree)
        for model, fields in file_registry.items():
            registry.setdefault(model, set()).update(fields)

    if touched is None:
        # git 이 아니면 touched 식별이 불가하다 — «전 파일을 신규(touched)로 간주»한다(fail-closed).
        print("주의: git 저장소가 아니다 — touched 식별이 불가해 «전 파일»을 검사한다(fail-closed)")
        candidates = {rel: "??" for rel in trees}
    else:
        candidates = {rel: code for rel, code in touched.items() if not _is_exempt_path(rel)}
    if not candidates:
        return 0  # touched 공집합은 «정상»이다(중간 커밋 후 재실행 등 — 조각 ⓐ §3)

    findings = ContractFindings(CONTRACT_REF)
    for rel, code in sorted(candidates.items()):
        tree = trees.get(rel)
        if tree is None:
            continue
        added = _added_lines(root, rel, code)
        _, default_violations = _scan_models(tree)
        filter_violations = _scan_filter_literals(tree, registry)
        for lineno, model, field in default_violations:
            if added is None or lineno in added:
                findings.add(
                    f"  - {rel}:{lineno}: {model}.{field} — 심볼 choices 선언 필드의 `default=\"리터럴\"`",
                    where=f"{rel}:{lineno}",
                    msg=f"{model}.{field} — 심볼 choices 선언 필드의 `default=\"리터럴\"`",
                    symbol=f"{model}.{field}",
                )
        for lineno, model, field in filter_violations:
            if added is None or lineno in added:
                findings.add(
                    f"  - {rel}:{lineno}: {model}.objects.filter/exclude({field}=리터럴) — 선언된 심볼 미사용",
                    where=f"{rel}:{lineno}",
                    msg=f"{model}.objects.filter/exclude({field}=리터럴) — 선언된 심볼 미사용",
                    symbol=f"{model}.{field}",
                )

    if findings:
        print(
            "[check-choices-literal-consumption] BLOCKER — 선언된 choices 값을 원시 리터럴로 "
            "소비했다(discipline-cleancode §2.14 소비 규율):"
        )
        for x in findings:
            print(x)
        print(
            "  근거: Enum/choices 가 선언된 값의 비교·분기·필터·대입·기본값은 그 심볼로만 "
            "참조한다 — 리터럴 오타는 조용한 항상-False 로 잠복하고 심볼 오타는 즉사한다. "
            "`default=` 는 `.value` 평탄화(`default=OrderStatus.PENDING.value` — "
            "`implementation-django` §2.5), 필터는 `.filter(status=OrderStatus.PENDING)`. "
            "마이그레이션 historical value·테스트 assert 기댓값의 리터럴은 면제 경로라 이 "
            "게이트가 보지 않는다(§10.4·implementation-test §15.4)."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
