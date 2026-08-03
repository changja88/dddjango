#!/usr/bin/env python3
"""dddjango 컨텍스트 격리 결정적 백스톱 (SD-7 — 컨텍스트 간 통신).

`check-layer-skeleton.py`(구조 골격)의 *의존 방향* 짝이다. 세 슬라이스를 잡는다:

  S1  cross-BC 내부 결합 — ACL/OHS 경로 *밖*에서 한 바운디드 컨텍스트(BC)가 다른 BC 의
      `domain_layer`/`infra_layer` 를 직접 import 하는 것(architecture-ddd §2.5·§3.2(3):
      컨텍스트 간 접근은 ACL 또는 `published_service`(OHS)로만 — 다른 컨텍스트의 내부
      계층을 직접 import 하지 않는다).
  S2  OHS contract 무의존 위반 — `published_service/*/contract/` 모듈이 (자기 BC 포함
      어느 BC 든) `domain_layer`/`application_layer`/`infra_layer` 를 import 하는 것
      (houserules `references/final.md` §2 OHS 내부 구조: contract 는 표준 라이브러리·
      같은 서비스 contract 만 — 소비 BC 의 계약 import 가 무거운 그래프(Django 앱 로딩)를
      끌고 오지 않게 하는 격리이자 도메인 enum 노출 차단).
  S3  published 계약 관통 — 자기 BC 의 `domain_layer`/`application_layer`/`infra_layer`
      프로덕션 파일이 *자기* BC 의 `published_service` 를 import 하는 것(houserules §2
      OHS 시그니처 계약: published 계약 타입을 application_layer 안으로 관통시키지 않는다
      — 응용은 domain 에만 의존, OHS 가 필드 단위로 언랩·재조립한다. *타* BC 의
      published_service 소비는 표준 경로라 대상이 아니고, presentation 의 자기 published
      import 도 대상 밖이다. `infra_layer/acl/` 도 3계층이므로 자기 published 역-import 는
      S3 대상이다 — ACL 면제는 S1(업스트림 번역) 한정).

*왜 결정적 백스톱인가* — 세 슬라이스 모두 **AST import 노드** 직격의 FP≈0 직접형이고
(`ast.parse` — 문자열·주석 안의 import 유사 텍스트에 오발화하지 않는다; `import x`·
`from x import y`·콤마 다중·별칭 전 형태, 함수 내부 지연 import 포함), 어느 것도 컴파일·
테스트를 깨지 않는다(green). discipline-reviewer 의미 게이트 한 점에만 의존하면 LLM 이
프로즈 규칙을 회피하는 표면이 된다 — 이 스크립트가 직접형을 결정적으로 메우고, 의미 변종
(변수 우회·간접 재수출·상대 import(`from ..domain_layer import x`)·문자열 동적 import)은
reviewer 몫이다(고정밀·저-recall, 거짓 양성 ≈0). 파싱 불가 파일은 fail-open(스킵)한다.

**ACL 면제(미스캘리브 차단)** — `infra_layer/acl/`(인접 경로 한정 — `repository/acl/` 류
은닉 배치는 면제 아님) 의 미이주 ACL 이 업스트림(타 BC) 모델·예외를 import·번역하는 건
표준 §2(houserules `references/final.md` §2 컨텍스트 간 통신: "OHS 미이주·행잠금 불가피 시
ACL로 명시 — 구현(업스트림 모델·예외 번역)은 `infra_layer/acl/` 에 가둔다") **명시 허용**이라
차단하지 않는다. 진짜 위반은 ACL *밖*(도메인/응용/presentation)이 타 BC 내부를 직접
import(예: 예외 번역이 ACL 에 안 갇혀 presentation·application 으로 누수)다. ACL 자신이
OHS 미경유(OHS 존재 시)·도메인 누수(포트 ABC 미준수)인지는 의미 변종이라 discipline-reviewer
의미 체크 몫이다. [근거: smoke4-claude(catalog 결합이 ACL 격리 → PASS) ↔ p1a-v3-claude
(catalog 예외가 presentation·application 으로 누수 → FAIL)를 결정적으로 가르는 축.]

거짓 양성 회피 — AND 합성으로만 차단:
  1) 프로젝트가 표준 레이아웃(`application/` 컨테이너)을 쓴다. 없으면 기존 확립 규약(§1.1)이라
     적용 대상 아님 → exit 0. **경로 판정은 전부 TARGET_DIR 기준 상대 경로다** — 체크아웃
     조상 디렉터리명(`…/application/…`·`…/venv/…` 등)에 오염되지 않는다(TARGET_DIR 는
     프로젝트 루트를 전제한다 — `application/` 컨테이너 자체를 넘기면 대상 없음 exit 0).
  2) `application/<bc>/` 하위 프로덕션 파일(test 디렉터리·`test_*.py`·`conftest.py` 제외 —
     프로덕션 파일명에 `test_` 접두를 쓰지 않는 표준 명명을 전제한다)이 슬라이스 패턴에
     걸린다. 컨테이너 직하 비-BC 파일(`application/glue.py`)의 BC 내부 import 는 보수적으로
     S1 로 본다(BC 밖에서의 내부 접근).
  3) (git 레포면) 그 파일이 이번 변경에서 새로 추가/수정됨 — 기존 커밋 코드는 존중(brownfield).
     구 read/write 평면 OHS·이주 호환 심은 §2 이주 조문상 허용이라 어느 슬라이스에도 안 걸린다.
  `application_layer` 의 cross-BC 직접 import 는 보수적으로 불-차단(루브릭 SD-7=domain/infra;
  거짓양성↓) — 의미 레인 몫. presentation·application 이 타 BC 의 *예외*(domain_layer 하위)를
  직접 import 하는 건 S1 로 포착된다.

레거시 API 순도 lane은 positional/auto/preserve 실행에서 기존 application_layer HTTP 직접
신호와 touched grandfathering을 그대로 보존한다. 명시 code-profile의 filtered full-tree
검사는 후속 slice가 소유하며, auto는 Error response G2 증거가 아니다.

사용법: check-context-isolation.py [TARGET_DIR] [--error-profile PROFILE ...]
종료코드: 0=clean(또는 표준 레이아웃 미적용), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
TEST_DIR_NAMES = {"test", "tests"}
LAYER_DIR_NAMES = {"domain_layer", "application_layer", "infra_layer"}

# S1: 타 BC 내부 계층. domain/infra 만(루브릭 SD-7) — application_layer 는 의미 레인.
CROSS_BC_RE = re.compile(r"^application\.([A-Za-z_]\w*)\.(?:domain_layer|infra_layer)(?:\.|$)")
# S2: contract 모듈의 계층 import — BC 불문 3계층 전부(무의존 규칙이라 application_layer 포함).
LAYER_ANY_RE = re.compile(
    r"^application\.[A-Za-z_]\w*\.(?:domain_layer|application_layer|infra_layer)(?:\.|$)"
)
# S3: 자기 BC published_service 역-import(관통).
PUBLISHED_RE = re.compile(r"^application\.([A-Za-z_]\w*)\.published_service(?:\.|$)")

# 구 check-error-centralization.py의 raw application-layer HTTP 신호. positional/auto/preserve
# lane에서 collector·순서·label·touched 의미를 바꾸지 않는다.
LEGACY_RESPONSE_CALL_RE = re.compile(
    r"\b(?:JsonResponse|HttpResponse|HttpResponseBadRequest|HttpResponseForbidden"
    r"|HttpResponseNotFound|HttpResponseNotAllowed|HttpResponseServerError)\s*\("
)
LEGACY_ERROR_STATUS_RE = re.compile(r"\bstatus(?:_code)?\s*=\s*[45]\d\d\b")
LEGACY_HTTP_ERROR_RE = re.compile(r"\bHttpError\s*\(\s*[45]\d\d\b")
LEGACY_NINJA_IMPORT_RE = re.compile(
    r"^\s*(?:from\s+ninja(?:_extra)?(?:\.\w+)*\s+import|import\s+ninja(?:_extra)?)\b",
    re.MULTILINE,
)
LEGACY_SIGNAL_CHECKS = (
    (LEGACY_RESPONSE_CALL_RE, "수제 HTTP 응답 객체 생성(JsonResponse/HttpResponse)"),
    (LEGACY_ERROR_STATUS_RE, "오류 status code 직접 선택(status[_code]=4xx/5xx)"),
    (LEGACY_HTTP_ERROR_RE, "ninja HttpError 를 status 와 함께 raise"),
    (LEGACY_NINJA_IMPORT_RE, "ninja(web 프레임워크) import — application 은 web 을 모른다"),
)

ERROR_PROFILES = {"auto", "dddjango-code-json", "preserve-established"}
BC_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


class UsageError(Exception):
    """CLI/selector analysis error normalized to exit 1."""


class _UsageParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UsageError(message)


@dataclass(frozen=True)
class Config:
    root: Path
    profile: str | None
    scope: str | None
    api_module: str | None
    controller_modules: tuple[str, ...]
    scope_bcs: tuple[str, ...]
    error_bcs: tuple[str, ...]


def _argument_parser() -> _UsageParser:
    parser = _UsageParser(add_help=True)
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--error-profile", action="append")
    parser.add_argument("--scope", action="append")
    parser.add_argument("--api-module", action="append")
    parser.add_argument("--controller-module", action="append", default=[])
    parser.add_argument("--scope-bc", action="append", default=[])
    parser.add_argument("--error-bc", action="append", default=[])
    return parser


def _one(
    option: str,
    values: list[str] | None,
    *,
    required: bool,
    issues: list[str],
) -> str | None:
    actual = values or []
    if required and not actual:
        issues.append(f"필수 인자 누락: {option}")
        return None
    if len(actual) > 1:
        issues.append(f"단일 인자 중복: {option}")
    return actual[0] if actual else None


def _unique(option: str, values: list[str], issues: list[str]) -> tuple[str, ...]:
    if len(values) != len(set(values)):
        issues.append(f"반복 인자 중복: {option}")
    return tuple(values)


def _selected_source(root: Path, option: str, raw: str, issues: list[str]) -> Path | None:
    rel = Path(raw)
    if (
        rel.is_absolute()
        or ".." in rel.parts
        or rel.as_posix() != raw
        or "/" not in raw
        or rel.suffix != ".py"
    ):
        issues.append(f"잘못된 source path: {option}={raw}")
        return None
    try:
        resolved = (root / rel).resolve()
    except (OSError, RuntimeError) as exc:
        issues.append(f"source path resolve 불능: {option}={raw} ({exc})")
        return None
    try:
        resolved.relative_to(root)
    except ValueError:
        issues.append(f"root/symlink 탈출: {option}={raw}")
        return None
    if not resolved.is_file():
        issues.append(f"선택 source 없음: {option}={raw}")
        return None
    try:
        source = resolved.read_text(encoding="utf-8")
        ast.parse(source, filename=raw)
    except (OSError, UnicodeError, SyntaxError) as exc:
        issues.append(f"선택 source 분석 불능: {option}={raw} ({exc})")
        return None
    return resolved


def _parse_config(argv: list[str]) -> Config:
    namespace = _argument_parser().parse_args(argv)
    try:
        root = Path(namespace.target).resolve()
        root_is_dir = root.is_dir()
    except (OSError, RuntimeError) as exc:
        raise UsageError(f"TARGET_DIR resolve 불능: {namespace.target} ({exc})") from exc
    if not root_is_dir:
        raise UsageError(f"디렉터리 아님 {root}")

    issues: list[str] = []
    profile = _one(
        "--error-profile",
        namespace.error_profile,
        required=False,
        issues=issues,
    )
    selectors_present = any(
        (
            namespace.scope,
            namespace.api_module,
            namespace.controller_module,
            namespace.scope_bc,
            namespace.error_bc,
        )
    )
    if profile is None and selectors_present:
        issues.append("selector 사용 시 --error-profile 필수")
    if profile is not None and profile not in ERROR_PROFILES:
        issues.append(f"지원하지 않는 --error-profile: {profile}")
    if profile == "auto" and selectors_present:
        issues.append("auto profile에는 scope/source/BC selector를 전달하지 않음")

    explicit = profile in {"dddjango-code-json", "preserve-established"}
    scope = _one("--scope", namespace.scope, required=explicit, issues=issues)
    api_module = _one(
        "--api-module",
        namespace.api_module,
        required=explicit,
        issues=issues,
    )
    controller_modules = _unique(
        "--controller-module", namespace.controller_module, issues
    )
    scope_bcs = _unique("--scope-bc", namespace.scope_bc, issues)
    error_bcs = _unique("--error-bc", namespace.error_bc, issues)
    if explicit and not controller_modules:
        issues.append("필수 인자 누락: --controller-module")
    if explicit and not scope_bcs:
        issues.append("필수 인자 누락: --scope-bc")
    if scope is not None and not scope.strip():
        issues.append("--scope는 빈 문자열일 수 없음")
    for option, names in (("--scope-bc", scope_bcs), ("--error-bc", error_bcs)):
        for name in names:
            if not BC_NAME_RE.fullmatch(name):
                issues.append(f"잘못된 BC 이름: {option}={name}")
    if not set(error_bcs).issubset(scope_bcs):
        issues.append("--error-bc는 --scope-bc의 부분집합이어야 함")

    resolved_by_role: dict[str, list[Path]] = {"api": [], "controller": []}
    if api_module is not None:
        path = _selected_source(root, "--api-module", api_module, issues)
        if path is not None:
            resolved_by_role["api"].append(path)
    for raw in controller_modules:
        path = _selected_source(root, "--controller-module", raw, issues)
        if path is not None:
            resolved_by_role["controller"].append(path)
    if set(resolved_by_role["api"]) & set(resolved_by_role["controller"]):
        issues.append("--api-module과 --controller-module 역할 overlap")
    all_selected = resolved_by_role["api"] + resolved_by_role["controller"]
    if len(all_selected) != len(set(all_selected)):
        issues.append("선택 source가 같은 resolved path를 중복 지정함")

    if issues:
        raise UsageError("; ".join(issues))
    return Config(
        root=root,
        profile=profile,
        scope=scope,
        api_module=api_module,
        controller_modules=controller_modules,
        scope_bcs=scope_bcs,
        error_bcs=error_bcs,
    )


def _legacy_application_layer_files(root: Path) -> list[Path]:
    """구 checker의 application_layer raw-signal 후보를 순서까지 그대로 수집한다."""
    out: list[Path] = []
    for path in root.rglob("*.py"):
        parts = set(path.parts)
        if parts & SKIP_DIRS:
            continue
        if "application_layer" not in parts:
            continue
        if parts & TEST_DIR_NAMES or path.name.startswith("test_") or path.name == "conftest.py":
            continue
        out.append(path)
    return out


def _legacy_is_new_or_modified(root: Path, file_path: Path) -> bool:
    """구 checker의 touched/untracked/Git-불능 보수 판정을 그대로 보존한다."""
    if not (root / ".git").exists():
        return True
    try:
        rel = file_path.relative_to(root)
    except ValueError:
        return True
    try:
        tracked = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--error-unmatch", str(rel)],
            capture_output=True,
        )
        if tracked.returncode != 0:
            return True
        changed = subprocess.run(
            ["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", str(rel)],
        )
        return changed.returncode != 0
    except (OSError, subprocess.SubprocessError):
        return True


def _legacy_http_findings(root: Path) -> list[str]:
    findings: list[str] = []
    for app_file in _legacy_application_layer_files(root):
        try:
            body = app_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        signals = [label for regex, label in LEGACY_SIGNAL_CHECKS if regex.search(body)]
        if not signals or not _legacy_is_new_or_modified(root, app_file):
            continue
        findings.append(f"  - {app_file.relative_to(root)}: {'; '.join(signals)}")
    return findings


def _print_legacy_http(findings: list[str]) -> None:
    print(
        "[check-context-isolation] BLOCKER — legacy touched application_layer가 "
        "HTTP 오류 응답을 직접 생성/의존함(presentation 경계 밖):"
    )
    for finding in findings:
        print(finding)
    print(
        "  근거: 오류→HTTP status/response 선택은 presentation 경계 소유다. "
        "positional/auto/preserve lane은 구 check-error-centralization의 raw signal과 "
        "grandfathering을 그대로 보존한다."
    )


def _has_application_container(root: Path) -> bool:
    """표준 앱 컨테이너(`application/`)가 있나 — 없으면 기존 규약이라 적용 대상 아님."""
    for path in root.rglob("application"):
        if not path.is_dir():
            continue
        if set(path.relative_to(root).parts) & SKIP_DIRS:
            continue
        return True
    return False


def _own_bc(rel_parts: tuple[str, ...]) -> str | None:
    """`application/<bc>/...` 의 <bc> (TARGET_DIR 기준 상대 경로에서)."""
    if "application" in rel_parts:
        i = rel_parts.index("application")
        if i + 1 < len(rel_parts):
            return rel_parts[i + 1]
    return None


def _prod_py_files(root: Path) -> list[tuple[Path, tuple[str, ...]]]:
    """application/ 하위 프로덕션 .py 와 그 상대 parts — test 제외. ACL 면제는 S1 판정에서만."""
    out: list[tuple[Path, tuple[str, ...]]] = []
    for path in root.rglob("*.py"):
        rel_parts = path.relative_to(root).parts
        if set(rel_parts) & SKIP_DIRS:
            continue
        if "application" not in rel_parts:
            continue
        if set(rel_parts) & TEST_DIR_NAMES or path.name.startswith("test_") or path.name == "conftest.py":
            continue
        out.append((path, rel_parts))
    return out


def _is_contract_file(rel_parts: tuple[str, ...]) -> bool:
    """`published_service/…/contract/…` 하위인가(S2 대상)."""
    return (
        "published_service" in rel_parts
        and "contract" in rel_parts
        and rel_parts.index("published_service") < rel_parts.index("contract")
    )


def _is_acl_file(rel_parts: tuple[str, ...]) -> bool:
    """`infra_layer/acl/` 직하 계열인가(S1 면제 — 인접 경로 한정, `repository/acl/` 은닉은 비면제)."""
    return any(
        rel_parts[i] == "infra_layer" and rel_parts[i + 1] == "acl"
        for i in range(len(rel_parts) - 1)
    )


def _imported_paths(tree: ast.AST) -> Iterator[tuple[int, str]]:
    """모든 import 노드의 (lineno, 점경로) — 절대 import 만(상대 import 는 reviewer 몫)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # 상대 import — 저-recall 설계(docstring), 의미 레인 몫.
                continue
            if node.module:
                yield node.lineno, node.module
                for alias in node.names:  # `from application.x import domain_layer` 형태 포착
                    if alias.name != "*":
                        yield node.lineno, f"{node.module}.{alias.name}"


def _is_new_or_modified(root: Path, file_path: Path) -> bool:
    """git 레포면 이번 변경(추가/수정)인지. git 아니면 True(가드 통과)."""
    if not (root / ".git").exists():
        return True
    try:
        rel = file_path.relative_to(root)
    except ValueError:
        return True
    try:
        tracked = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--error-unmatch", str(rel)],
            capture_output=True,
        )
        if tracked.returncode != 0:
            return True  # 신규 파일.
        changed = subprocess.run(
            ["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", str(rel)],
            capture_output=True,  # 커밋 0개 레포의 'bad revision' stderr 누출 방지.
        )
        return changed.returncode != 0
    except (OSError, subprocess.SubprocessError):
        return True  # git 판단 불가 → 안전하게 가드 통과(나머지 AND 가 좁힌다).


def main(argv: list[str]) -> int:
    try:
        config = _parse_config(argv[1:])
    except UsageError as exc:
        print(f"[check-context-isolation] 사용 오류: {exc}", file=sys.stderr)
        return 1
    except SystemExit as exc:  # argparse --help
        return int(exc.code)

    root = config.root
    legacy_http_findings = (
        _legacy_http_findings(root)
        if config.profile in {None, "auto", "preserve-established"}
        else []
    )
    if not _has_application_container(root):
        if legacy_http_findings:
            _print_legacy_http(legacy_http_findings)
            return 2
        return 0  # S1~S3 표준 레이아웃 미적용. legacy HTTP lane은 위에서 먼저 실행.

    s1_findings: list[str] = []  # cross-BC 내부 결합
    s2_findings: list[str] = []  # contract 무의존 위반
    s3_findings: list[str] = []  # published 계약 관통
    for f, rel_parts in _prod_py_files(root):
        if not _is_new_or_modified(root, f):
            continue
        own = _own_bc(rel_parts)
        try:
            source = f.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)
        except (OSError, SyntaxError):
            continue  # 파싱 불가 → fail-open(스킵) — green 전제라 실코드는 파싱된다.
        src_lines = source.splitlines()
        is_contract = _is_contract_file(rel_parts)
        is_acl = _is_acl_file(rel_parts)
        in_layer = bool(set(rel_parts) & LAYER_DIR_NAMES)
        rel = f.relative_to(root)
        seen: set[tuple[int, str]] = set()  # (lineno, slice) — 한 import 문 1발화
        for lineno, dotted in _imported_paths(tree):
            shown = src_lines[lineno - 1].strip() if 0 < lineno <= len(src_lines) else dotted
            if is_contract:
                # S2 — contract 는 어느 계층도 import 하지 않는다(자기 BC 포함).
                if LAYER_ANY_RE.match(dotted) and (lineno, "s2") not in seen:
                    seen.add((lineno, "s2"))
                    s2_findings.append(f"  - {rel}:{lineno}  {shown}")
                continue  # contract 파일은 S2 전담(중복 계상 방지).
            m = CROSS_BC_RE.match(dotted)
            if m and m.group(1) != own and not is_acl and (lineno, "s1") not in seen:
                seen.add((lineno, "s1"))  # S1 — 타 BC 내부 계층(ACL 면제)
                s1_findings.append(f"  - {rel}:{lineno}  {shown}")
            p = PUBLISHED_RE.match(dotted)
            if p and p.group(1) == own and in_layer and (lineno, "s3") not in seen:
                seen.add((lineno, "s3"))  # S3 — 자기 published 역-import(관통)
                s3_findings.append(f"  - {rel}:{lineno}  {shown}")

    if not (legacy_http_findings or s1_findings or s2_findings or s3_findings):
        return 0

    if legacy_http_findings:
        _print_legacy_http(legacy_http_findings)
    if s1_findings:
        print(
            "[check-context-isolation] BLOCKER — ACL 밖(도메인/응용/presentation)에서 타 BC 의 "
            "domain_layer/infra_layer 를 직접 import 함(컨텍스트 간 결합 누수):"
        )
        for line in s1_findings:
            print(line)
        print(
            "  근거: architecture-ddd §2.5·§3.2(3)·discipline-houserules §2. 컨텍스트 간 접근은 "
            "ACL 또는 published_service(OHS)로만 한다 — 다른 BC 의 내부 계층(예외 포함)을 직접 "
            "import 하지 않는다. ACL 이 업스트림 모델·예외를 번역해 격리하거나(infra_layer/acl/), "
            "OHS 를 경유하라. 접을 실질 사유가 있으면 코드에서 흘리지 말고 설계(G1)로 반송하라."
        )
    if s2_findings:
        print(
            "[check-context-isolation] BLOCKER — OHS contract 모듈이 계층"
            "(domain/application/infra)을 import 함(contract 무의존 위반):"
        )
        for line in s2_findings:
            print(line)
        print(
            "  근거: discipline-houserules `references/final.md` §2 OHS 내부 구조(contract 무의존). "
            "contract 는 표준 라이브러리·같은 서비스 contract 만 import 한다 — 계약 타입은 wire 형"
            "(str·Literal)으로 선언하고, 도메인 enum·모델을 계약 필드로 노출하지 않는다."
        )
    if s3_findings:
        print(
            "[check-context-isolation] BLOCKER — 자기 BC 의 계층(domain/application/infra)이 "
            "자기 published_service 를 import 함(published 계약 관통):"
        )
        for line in s3_findings:
            print(line)
        print(
            "  근거: discipline-houserules `references/final.md` §2 OHS 시그니처 계약. published "
            "계약 타입을 application_layer 안으로 관통시키지 않는다 — 응용은 자기 DTO"
            "(`<feature>/dto/<usecase>_request.py`·`<usecase>_result.py`)를 소유하고, OHS 가 "
            "계약↔응용 DTO 를 필드 단위로 언랩·재조립한다(타 BC 의 published_service 소비는 정상)."
        )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
