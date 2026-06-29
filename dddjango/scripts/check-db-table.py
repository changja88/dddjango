#!/usr/bin/env python3
"""dddjango ORM 테이블명 *작성 강제* 결정적 백스톱 (houserules §4 — 신규 모델 db_table).

표준 레이아웃(`infra_layer/django_<app>/models/`)에서 *이번 작업이 새로 추가한* concrete·
managed ORM 모델이 `Meta.db_table` 을 **명시했는지(존재)** 만 검사한다. **값의 형태**
(`<app_label>_<entity_snake>` 일치 — `Model` 접미 제거·snake·app 접두)는 이 백스톱이 보지
않는다 — 그건 §4 규약 본문 + `makemigrations --check` + discipline-reviewer 의미 점검 몫이다.

*왜 존재만 보나(presence-only)* — 값 형태 검증은 클래스명·app_label 에서 '기대 테이블명'을
도출해 대조해야 하는데, 그 도출에 실패 모드(약어 snake, `AppConfig.label`≠디렉터리명, 이주
보존명≠규약)가 있어 거짓 양성을 낳는다. 결정적 게이트의 존재 근거는 'FP≈0'이므로, 모호성
0인 *누락*만 결정적으로 잡고 값 정확성은 의미 레인에 위임한다.

*왜 필요한가* — 클래스 명명 규약이 `<Name>Model`(houserules §0 불변식 6)이라 db_table 을
명시 안 하면 Django 기본값이 `<app>_<name>model` 이 돼 코드측 `Model` 접미가 테이블명에
샌다(`catalog_productmodel`). db_table 미선언은 테스트로 안 잡혀 TDD Red 로 못 막는다 —
이 스크립트가 그 절반(작성 강제)을 결정적으로 메운다.

거짓 양성 회피 — AND 합성으로만 차단:
  1) 표준 레이아웃을 쓴다 = `infra_layer/django_*/` 가 레포에 있다. 없으면 §1.1 기존
     규약이라 적용 대상이 아니다 → exit 0.
  2) git 레포다. 신규 한정 규약이라 git 없이는 '신규'를 식별할 수 없다 → exit 0(보수적).
  3) 그 모델 파일이 이번 변경에서 *새로 추가*(untracked `??`/staged `A`)됐다. 기존 파일
     *수정*(`M`)은 제외(수정 파일 내 신규 모델은 reviewer 사각). 이주(§10.4)는 파일이
     신규로 떨어져도 보존 db_table 을 *명시*하므로 존재 검사를 통과한다(값은 안 보므로
     보존명이 규약과 달라도 무방).
  4) 모델이 concrete·managed 이고 옵션이 정적으로 확정된다 — `abstract=True`·`proxy=True`
     (자체 테이블 없음)·`managed=False`(외부 소유 테이블) 면제. Meta 가 다른 Meta 를
     상속하거나 abstract/proxy/managed 가 비-리터럴(정적 미확정)이면 통째 스킵(보수적).
  위 넷이 참인 모델에서 db_table 대입이 *전혀 없으면*(리터럴이든 동적 식이든 하나도 없음)
  → blocker. db_table 이 무엇이든 대입돼 있으면(값 불문) 통과.

사용법: check-db-table.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean(또는 표준 레이아웃 미적용·non-git), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
TEST_DIR_NAMES = {"test", "tests"}
DJANGO_PREFIX = "django_"
MODEL_SUFFIX = "Model"
# 모델 base 로 보지 않는 이름(같은 디렉터리에 섞일 수 있는 비-ORM base — 거짓 양성 회피).
NON_MODEL_BASES = {"BaseModel"}  # pydantic 등.


def _find_django_app_dirs(root: Path) -> list[Path]:
    """`infra_layer/django_<app>/` 디렉터리들(모델 파일 탐색 스코프)."""
    out: list[Path] = []
    for p in root.rglob(f"{DJANGO_PREFIX}*"):
        if not p.is_dir():
            continue
        if set(p.parts) & SKIP_DIRS:
            continue
        if p.parent.name != "infra_layer":
            continue
        out.append(p)
    return out


def _model_files_for(app_dir: Path) -> list[Path]:
    """`django_<app>/models/**/*.py` + `django_<app>/models.py`. test 경로 제외."""
    files: list[Path] = []
    models_pkg = app_dir / "models"
    if models_pkg.is_dir():
        for f in sorted(models_pkg.rglob("*.py")):
            rel_parts = set(f.relative_to(app_dir).parts)
            if rel_parts & SKIP_DIRS or rel_parts & TEST_DIR_NAMES:
                continue
            files.append(f)
    models_mod = app_dir / "models.py"
    if models_mod.is_file():
        files.append(models_mod)
    return files


def _is_new_file(root: Path, path: Path) -> bool:
    """git porcelain 으로 이 파일이 *새로 추가*(untracked `??`/staged `A`)됐는가.
    수정(`M`)·미변경은 False(신규 한정 규약)."""
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--", str(rel)],
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    if res.returncode != 0 or not res.stdout.strip():
        return False
    code = res.stdout[:2]  # porcelain XY 상태코드.
    return "A" in code or "?" in code


def _is_model_base(base: ast.expr) -> bool:
    """base 가 `models.Model` 또는 `...Model` 로 끝나는 이름인가(NON_MODEL_BASES 제외)."""
    if isinstance(base, ast.Attribute):
        name = base.attr
    elif isinstance(base, ast.Name):
        name = base.id
    else:
        return False
    if name in NON_MODEL_BASES:
        return False
    return name == MODEL_SUFFIX or name.endswith(MODEL_SUFFIX)


def _const_bool(value: ast.expr) -> bool | None:
    if isinstance(value, ast.Constant) and isinstance(value.value, bool):
        return value.value
    return None


def _meta_info(model_node: ast.ClassDef) -> dict | None:
    """모델의 `class Meta` 에서 면제 플래그 + db_table 존재 여부 추출.
    반환 None = 통째 스킵(보수적): Meta 가 다른 Meta 를 상속(`class Meta(Base.Meta)`)하거나
    abstract/proxy/managed 가 비-리터럴이라 옵션을 정적으로 확정할 수 없는 경우.
    Meta 가 아예 없으면 concrete·managed·db_table 미선언으로 본다."""
    flags: dict = {"abstract": False, "proxy": False, "managed": True, "has_db_table": False}
    meta = next(
        (
            item
            for item in model_node.body
            if isinstance(item, ast.ClassDef) and item.name == "Meta"
        ),
        None,
    )
    if meta is None:
        return flags
    if meta.bases:  # 상속 Meta → 정적 판정 불가.
        return None
    for stmt in meta.body:
        if isinstance(stmt, ast.Assign):
            names = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
            value = stmt.value
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            if stmt.value is None:
                continue
            names = [stmt.target.id]
            value = stmt.value
        else:
            continue
        for name in names:
            if name == "db_table":
                flags["has_db_table"] = True  # 값 불문(리터럴·동적 모두 '명시'로 인정).
            elif name in ("abstract", "proxy"):
                b = _const_bool(value)
                if b is None:
                    return None  # 비-리터럴 면제 플래그 → 정적 미확정, 보수적 스킵.
                flags[name] = b
            elif name == "managed":
                b = _const_bool(value)
                if b is None:
                    return None
                flags["managed"] = b
    return flags


def _file_issues(path: Path, root: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return []
    rel = path.relative_to(root)
    issues: list[str] = []
    for node in tree.body:  # 모듈 최상위 클래스만(중첩 helper 제외).
        if not isinstance(node, ast.ClassDef):
            continue
        if not any(_is_model_base(b) for b in node.bases):
            continue
        meta = _meta_info(node)
        if meta is None:
            continue  # 상속 Meta·비-리터럴 면제 플래그 → 판정 불가.
        if meta["abstract"] or meta["proxy"] or not meta["managed"]:
            continue
        if not meta["has_db_table"]:
            issues.append(f"  - {rel}: {node.name} — Meta.db_table 미선언")
    return issues


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-db-table] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    app_dirs = _find_django_app_dirs(root)
    if not app_dirs:
        return 0  # 표준 레이아웃(`infra_layer/django_<app>/`) 미적용 → 해당 없음.
    if not (root / ".git").exists():
        return 0  # 신규 한정 규약 — git 없이는 신규 식별 불가 → 스킵(보수적).

    findings: list[str] = []
    for app_dir in app_dirs:
        for f in _model_files_for(app_dir):
            if not _is_new_file(root, f):
                continue
            findings.extend(_file_issues(f, root))

    if findings:
        print(
            "[check-db-table] BLOCKER — 신규 ORM 모델이 `Meta.db_table` 을 명시하지 않았다"
            "(houserules §4):"
        )
        for x in findings:
            print(x)
        print(
            "  근거: discipline-houserules §4 — 신규 ORM 모델은 `Meta.db_table` 을 명시한다"
            "(미선언 시 Django 기본값 `<app>_<name>model` 이 돼 코드측 `Model` 접미가 "
            "테이블명에 샌다). 값은 `<app_label>_<entity_snake>`(클래스 `<Name>Model` 에서 "
            "`Model` 제거·snake; `ProductModel`→`<app>_product`)로 쓴다 — 단 이 백스톱은 "
            "*존재*만 보고 값 형태는 `makemigrations --check`·discipline-reviewer 가 본다. "
            "`abstract`/`proxy`/`managed=False` 모델은 db_table 을 두지 않는다. 기존 적용 "
            "모델의 이주는 보존 db_table 을 명시하면 통과한다(`implementation-django` §10.4)."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
