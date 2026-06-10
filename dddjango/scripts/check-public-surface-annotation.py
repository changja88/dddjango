#!/usr/bin/env python3
"""dddjango 공개 표면 어노테이션 가드 결정적 백스톱 (discipline-houserules §4·§4.1).

모듈 레벨 변수와 (일반) 클래스 변수 — 다른 코드가 import 하고 독자가 계약으로 읽는 *공개 표면* —
의 첫 단순대입(`name = expr`)에 타입 어노테이션이 없는 경우를 적출한다. **함수 지역 변수는 보지
않는다**(§4: 지역 변수는 권장이지 필수가 아니다 — mypy 가 추론하고 노이즈가 크다).

*왜 결정적 백스톱인가* — §4 는 공개 표면 어노테이션을 필수로 박지만 mypy strict 의
`disallow_untyped_defs` 는 *시그니처만* 강제하고 변수 어노테이션 전용 옵션은 없다. 공개 표면(모듈/
클래스 본문 *직계*)은 좁아서 "bare 대입이면 거의 확실히 누락"이라 결정적으로 막을 수 있다(거짓양성
≈0). 함수 지역 변수(넓고 추론 자명)는 보지 않으므로 noise 폭증을 피한다(§4.1 — 실익은 버그예방이
아니라 공개 표면의 생성 결정성·계약 가독성).

거짓양성 ≈ 0 — 다음은 위반이 아니라 전부 통과(면제):
  - 함수 본문 안 지역 변수(스코프가 함수면 본문 통째 검사 안 함).
  - 모듈/클래스 본문 *직계* 가 아닌 곳(`if`/`try`/`with`/`for` 블록 내부 — TYPE_CHECKING 별칭·조건부
    상수 포함). 직계만 보므로 조건부 대입의 위양성을 구조적으로 회피한다.
  - 어노테이션 문법이 없는 바인딩: 언패킹(`a, b = …`)·다중 대입(`a = b = …`)·증강 대입(AugAssign)·
    Subscript/Attribute 타깃(`d[k]=`·`self.x=`)·import·for/with/except 타깃·walrus.
  - 재대입(같은 본문에서 이미 바인딩된 이름의 후속 대입 — 첫 바인딩만 본다).
  - 던더(`__all__`·`__version__` 등)·`urlpatterns`(Django URLconf 매직 이름), 그리고 RHS 가 리터럴·
    컬렉션 상수가 *아닌* 경우 — 호출식(`router = Router()`·`api = NinjaAPI()`), 타입 별칭(`= Union[...]`),
    이름 참조·재export(`router = make_router`), 표현식. 타입이 RHS·원본에서 자명하거나 관용
    무어노테이션이라 면제. 검출 대상은 리터럴·컬렉션 상수(`= 3`·`= "..."`·`= [...]`·`= {...}`)뿐이다.
  - 선언적 프레임워크 클래스 본문(base 가 `Model`/`Enum`/`*Choices`/`Form`/`Serializer`/`Schema`/
    `BaseModel`/`TypedDict`/`NamedTuple` 또는 `@dataclass`, 클래스명 `Meta`/`Config`) — 필드/멤버
    선언이 관용이라 통째 면제. pydantic/ninja `Schema`·`dataclass` 필드는 정상이면 이미 `x: T`
    (AnnAssign)라 매치되지 않고, bare 면 필드가 안 되는 버그지만 그 의미 판정은 reviewer 몫이다.
  - *알려진 한계(위양성 방향·현 코퍼스 0건)*: 선언적 클래스 면제는 *직계* base 이름 매칭이라, 프로젝트-로컬
    추상 base 2단 상속(`class X(BaseSchema)`)·별칭 import base(`Model as M`)·`Exception` 서브클래스의
    리터럴 클래스 상수는 면제가 못 미쳐 검출될 수 있다 — 막다른길은 아니고(어노테이트로 통과)
    discipline-reviewer 의미 점검이 '선언적 클래스 손자/별칭'을 면제로 보완한다.
  - production 만(`test`/`tests`/`migrations`/`settings` 디렉터리·`settings.py`/`urls.py`/`manage.py`/
    `asgi.py`/`wsgi.py`/`conftest.py` 제외), 이번 작업 신규/수정분만(git untracked/modified, 판정
    불가면 스킵 — brownfield 레거시 거짓양성 회피).

사용법: check-public-surface-annotation.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean(또는 판정불가), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {
    ".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__",
    "build", "dist", ".tox", ".mypy_cache", ".pytest_cache", ".eggs",
}
# 검사 제외 디렉터리(테스트·자동생성·설정 관용 — 대량 bare 대입이 정상).
SKIP_PATH_DIRS = {"test", "tests", "migrations", "settings"}
# 검사 제외 파일(Django 진입·설정 파일 — `urlpatterns = [...]`·`DEBUG = True` 류 관용).
SKIP_FILE_NAMES = {
    "settings.py", "urls.py", "manage.py", "asgi.py", "wsgi.py", "conftest.py",
}

# 선언적 프레임워크 클래스 — 본문 대입이 "필드/멤버/옵션 선언" 관용이라 본문 통째 면제.
DECLARATIVE_BASE_NAMES = {
    "Model", "Enum", "IntEnum", "StrEnum", "Flag", "IntFlag",
    "Choices", "TextChoices", "IntegerChoices",
    "Form", "ModelForm", "Serializer", "ModelSerializer",
    "HyperlinkedModelSerializer", "Schema", "BaseModel",
    "TypedDict", "NamedTuple",
    # Django 설정·등록 선언 클래스(`default_auto_field`·`name`·`list_display` 등은 관용 무어노테이션).
    "AppConfig", "ModelAdmin", "TabularInline", "StackedInline", "AdminSite",
}
DECLARATIVE_CLASS_NAMES = {"Meta", "Config"}
DECLARATIVE_DECORATORS = {"dataclass", "define", "frozen", "attrs"}

# Django 매직 모듈 변수 — 프레임워크가 특정 이름을 특정 위치에서 찾는 관용(어노테이션 비관용).
EXEMPT_NAMES = {"urlpatterns"}

# 검출 대상 RHS — 리터럴·컬렉션 상수만(계약 명시 효용 있는 진짜 상수). 그 외(호출·별칭·표현식)는 면제.
LITERAL_RHS = (ast.Constant, ast.List, ast.Dict, ast.Set, ast.Tuple)


def _callee_name(node: ast.AST) -> str | None:
    """호출식의 callee 이름(`f(...)`→`f`, `a.b.c(...)`→`c`)."""
    if isinstance(node, ast.Call):
        f = node.func
        if isinstance(f, ast.Name):
            return f.id
        if isinstance(f, ast.Attribute):
            return f.attr
    return None


def _base_names(cls: ast.ClassDef) -> set[str]:
    names: set[str] = set()
    for b in cls.bases:
        if isinstance(b, ast.Name):
            names.add(b.id)
        elif isinstance(b, ast.Attribute):
            names.add(b.attr)
    return names


def _decorator_names(node: ast.ClassDef) -> set[str]:
    names: set[str] = set()
    for d in node.decorator_list:
        if isinstance(d, ast.Name):
            names.add(d.id)
        elif isinstance(d, ast.Attribute):
            names.add(d.attr)
        else:
            n = _callee_name(d)
            if n:
                names.add(n)
    return names


def _is_declarative_class(cls: ast.ClassDef) -> bool:
    """필드/멤버 선언이 관용이라 클래스 변수 규칙에서 면제할 클래스인가."""
    if cls.name in DECLARATIVE_CLASS_NAMES:
        return True
    if _base_names(cls) & DECLARATIVE_BASE_NAMES:
        return True
    if _decorator_names(cls) & DECLARATIVE_DECORATORS:
        return True
    return False


def _rhs_exempt(value: ast.AST) -> bool:
    """검출 대상은 리터럴·컬렉션 상수(`= 3`·`= "..."`·`= [...]`·`= {...}`)뿐 — 계약 명시 효용이 있는
    진짜 상수다. 그 외는 면제: 호출식(`Router()`·`NinjaAPI()`·`getLogger()`·`models.CharField()` — 타입이
    RHS 에서 자명·관용 무어노테이션), 타입 별칭(`Union[...]`), 이름 참조·재export(`router = make_router`),
    표현식(`A + B`). 거짓양성≈0 — 면제 쪽으로 기운다."""
    return not isinstance(value, LITERAL_RHS)


def _is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def _record_bindings(node: ast.AST, bound: set[str]) -> None:
    """node 하위에서 바인딩되는 모든 이름을 기록(직계 첫 바인딩 판정의 면제 기반)."""
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            bound.add(n.id)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                bound.add((a.asname or a.name).split(".")[0])


def _scan_body(body: list[ast.stmt], in_class: bool, findings: list[str]) -> None:
    """모듈/클래스 본문 *직계* 의 첫 단순대입 어노테이션 누락을 모은다(스코프별 재귀)."""
    bound: set[str] = set()
    for stmt in body:
        if isinstance(stmt, ast.ClassDef):
            bound.add(stmt.name)
            if not _is_declarative_class(stmt):
                _scan_body(stmt.body, True, findings)  # 일반 클래스 본문만 재귀
            continue
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            bound.add(stmt.name)
            continue  # 함수 본문 = 지역 변수, 검사 안 함
        if isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Name):
                bound.add(stmt.target.id)  # 이미 어노테이트됨
            continue
        if isinstance(stmt, ast.Assign):
            if len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                name = stmt.targets[0].id
                if name in bound:
                    continue  # 재대입(첫 바인딩만 본다)
                bound.add(name)
                if _is_dunder(name) or name in EXEMPT_NAMES or _rhs_exempt(stmt.value):
                    continue
                scope = "클래스 변수" if in_class else "모듈 변수"
                findings.append(f"{name} ({scope}, line {stmt.lineno})")
            else:
                _record_bindings(stmt, bound)  # 언패킹·다중·비-Name 타깃
            continue
        _record_bindings(stmt, bound)  # If/Try/With/For/AugAssign/Import 등 — 기록만


def _scan_file(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return []
    findings: list[str] = []
    _scan_body(tree.body, False, findings)
    return findings


def _git_available(root: Path) -> bool:
    return (root / ".git").exists()


def _porcelain(root: Path, relpath: str) -> str | None:
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--", relpath],
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if res.returncode != 0:
        return None
    return res.stdout


def _is_new_or_modified(root: Path, file: Path) -> bool | None:
    """이번 작업이 이 파일을 새로 만들거나 수정했나. 판정 불가면 None(→ 스킵)."""
    if not _git_available(root):
        return None
    rel = file.relative_to(root).as_posix()
    out = _porcelain(root, rel)
    if out is None:
        return None
    return bool(out.strip())


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-public-surface-annotation] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    findings: list[str] = []
    for path in root.rglob("*.py"):
        if set(path.parts) & SKIP_DIRS:
            continue
        if set(path.parts) & SKIP_PATH_DIRS:
            continue
        if path.name in SKIP_FILE_NAMES:
            continue
        hits = _scan_file(path)
        if not hits:
            continue
        if _is_new_or_modified(root, path) is not True:
            continue  # 미변경·비-git → 스킵(거짓양성 회피)
        rel = path.relative_to(root).as_posix()
        for h in hits:
            findings.append(f"  - {rel}: {h}")

    if findings:
        print(
            "[check-public-surface-annotation] BLOCKER — 공개 표면(모듈/클래스 변수)의 첫 "
            "단순대입에 타입 어노테이션이 없다(discipline-houserules §4):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: `discipline-houserules` §4·§4.1. 모듈 상수·클래스 변수는 다른 코드가 import 하고 "
            "독자가 계약으로 읽는 공개 표면이라 `name: T = expr` 로 타입을 명시한다. 함수 지역 변수는 "
            "권장(필수 아님)이라 보지 않는다. 합법 경로(누락이 위반 아님): 함수 지역 변수, 어노테이션 "
            "문법이 없는 곳(`for`/`with`/`except`/언패킹/다중·증강 대입), 재대입, `self.x=`(타입은 클래스 "
            "본문 `x: T` 선언으로), Django 모델 필드·`Meta`/`Config`·enum 멤버, RHS 가 리터럴 상수가 "
            "아닌 경우(`router = Router()` 호출식·`= Union[...]` 타입 별칭·이름 참조). pydantic/ninja "
            "`Schema`·`dataclass` 필드는 오히려 `x: T` 가 필수다."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
