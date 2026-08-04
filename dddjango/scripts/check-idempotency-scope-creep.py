#!/usr/bin/env python3
"""dddjango 멱등성 스코프크립(C3) 결정적 백스톱 (G0=확장금지 · architecture-db §9.6 Idempotency storage 집행).

Codex 계열이 *태스크가 요청하지 않은* 멱등성(`Idempotency-Key` 필수·전용 record 테이블·
replay store)을 architect 단계에서 silent 의무화해 코드로 구현하는 회귀(DR-24 C3·DR-27
라이브 재현)를 차단한다. 이 checker의 소유는 이번 변경에서 touched된 멱등성 산출물이
G1 채택 승인 없이 accepted scope 밖에 추가되는 것을 막는 데 한정된다.

*왜 결정적 백스톱인가* — 미요청 멱등성 금지 가드는 이미 `design-architect`(§9.6 Idempotency
storage 행)에 산문으로 있으나, 첫 라이브 검증(DR-27)에서 architect 가 "risky write 라 권장"
이라 합리화하며 번복했다(가이드 단독 = 재현율 약함, DR-21). 이 백스톱은 *코드* 를 봐서 집행한다
— 백스톱은 G2 에서 도는데 그땐 멱등성 코드(전용 store·model·operation 오케스트레이션)가 이미
디스크에 있으므로, 산문 프록시(design-spec)가 아니라 산출물을 직접 본다(기존 9종과 동일 철학).
Claude 처럼 멱등성 코드를 아예 안 지으면 (2) 에서 자명 통과한다.

거짓양성 ≈ 0 — AND 합성으로만 차단:
  1) 프로젝트가 표준 레이아웃(`application/`)을 쓴다. 없으면 §1.1 존중 → exit 0.
  2) `application/<bc>/` 프로덕션(test 제외) 코드에 멱등성 *산출물* — 파일명/클래스/`db_table`
     에 `idempotency`, 또는 `Idempotency-Key` 처리 — 이 있고, (git 레포면) 이번 변경에서
     새로 추가/수정됨(brownfield 의 기존 멱등성은 존중).
  3) `.dddjango/*/scope.md` 가 멱등성을 *미요청으로 단정* 한다(안정 템플릿 "멱등성 … 이번
     요청에 명시되지 않았다 / 이번 요청 아님 / 미요청 / 범위 밖").
  4) scope·design-spec 에 G1 사용자-승인 *채택* 배너("G1 … (사용자 승인) … 멱등성 도입/채택")
     가 없다 — 정당 채택은 면제.
  2 ∧ 3 ∧ ¬4 → exit 2(blocker, 산출물 경로 출력). 아니면 exit 0.

  *왜 (3) 을 BLOCK 조건으로* — scope 가 멱등성을 *적극적으로 미요청이라 단정* 한 경우에만
  발화한다(고정밀). scope 침묵·`.dddjango/` 부재는 판정불가 → 보수적 통과(exit 0). 정당하게
  G1 에서 채택된 멱등성은 (4) 로 면제한다(거짓양성 방어).

  *한계(정직)* — 이름 회피(예: `idempotency` 대신 `RequestDeduplication`, 테이블명 위장)는
  v1 패턴이 놓칠 수 있다(고정밀·저-recall = 9종 철학). recall 갭은 discipline-reviewer 의미
  체크가 보완한다.

사용법: check-idempotency-scope-creep.py [TARGET_DIR]   (기본=현재 디렉터리)
종료코드: 0=clean(또는 표준 미적용·판정불가·정당 채택), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
TEST_DIR_NAMES = {"test", "tests"}

# (2) 멱등성 코드 산출물 신호 — 프로덕션 .py 의 파일명 또는 본문.
_IDEMP_NAME_RE = re.compile(r"idempoten", re.IGNORECASE)
_IDEMP_BODY_RES = (
    re.compile(r"class\s+\w*[Ii]dempotenc\w*"),                       # 전용 store/claim/record 클래스
    re.compile(r"""db_table\s*=\s*['"][^'"]*idempoten""", re.IGNORECASE),  # 전용 테이블
    re.compile(r"Idempotency-Key", re.IGNORECASE),                    # 헤더 처리(presentation)
)

# (3) scope.md 의 "미요청 단정" — 같은 줄에 멱등 + 미요청 표현.
_NOT_REQUESTED_RE = re.compile(
    r"멱등.*(명시되지\s*않았|이번\s*요청\s*아님|요청\s*아님|미요청|범위\s*밖|범위\s*아님|포함하지\s*않)"
)
# (4) G1 사용자-승인 *채택* 배너(면제) — 같은 줄에 멱등 + 채택동사 + 승인토큰, 단 거부토큰 없을 때만.
_ADOPT_RE = re.compile(
    r"멱등.*(도입|채택|적용).*(사용자\s*승인|G1\s*결정|G1\s*확정)"
    r"|(사용자\s*승인|G1\s*결정|G1\s*확정).*멱등.*(도입|채택|적용)"
)
_REJECT_TOKENS = ("미적용", "미도입", "범위 밖", "범위밖", "안 함", "아님", "않는다", "권장하나")


def _has_application_container(root: Path) -> bool:
    """표준 앱 컨테이너(`application/`)가 있나 — 없으면 기존 규약(§1.1)이라 적용 대상 아님."""
    for path in root.rglob("application"):
        if path.is_dir() and not (set(path.parts) & SKIP_DIRS):
            return True
    return False


def _is_test_path(path: Path) -> bool:
    parts = path.parts
    return bool(set(parts) & TEST_DIR_NAMES) or path.name.startswith("test_") or path.name == "conftest.py"


def _prod_py_under_application(root: Path) -> list[Path]:
    """application/ 하위 프로덕션 .py — test 제외(venv 제외)."""
    out: list[Path] = []
    for path in root.rglob("*.py"):
        parts = path.parts
        if set(parts) & SKIP_DIRS:
            continue
        if "application" not in parts:
            continue
        if _is_test_path(path):
            continue
        out.append(path)
    return out


def _is_new_or_modified(root: Path, file_path: Path) -> bool:
    """git 레포면 이번 변경(추가/수정)인지. git 아니면 True(가드 통과 — brownfield 가드는 git 일 때만)."""
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
            return True  # 신규(untracked) 파일.
        changed = subprocess.run(["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", str(rel)])
        return changed.returncode != 0
    except (OSError, subprocess.SubprocessError):
        return True  # git 판단 불가 → 안전하게 가드 통과(나머지 AND 가 좁힌다).


def _idempotency_artifacts(root: Path) -> list[Path]:
    """(2) 이번 변경의 멱등성 프로덕션 산출물."""
    found: list[Path] = []
    for f in _prod_py_under_application(root):
        if not _is_new_or_modified(root, f):
            continue
        if _IDEMP_NAME_RE.search(f.name):
            found.append(f)
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(r.search(text) for r in _IDEMP_BODY_RES):
            found.append(f)
    return found


def _dddjango_docs(root: Path, name: str) -> list[Path]:
    base = root / ".dddjango"
    if not base.is_dir():
        return []
    return sorted(base.glob(f"*/{name}"))


def _scope_says_not_requested(root: Path) -> bool:
    """(3) 어느 scope.md 든 멱등성을 미요청으로 단정하나."""
    for scope in _dddjango_docs(root, "scope.md"):
        try:
            for ln in scope.read_text(encoding="utf-8", errors="replace").splitlines():
                if _NOT_REQUESTED_RE.search(ln):
                    return True
        except OSError:
            continue
    return False


def _user_adopted(root: Path) -> bool:
    """(4) scope·design-spec 에 G1 사용자-승인 멱등성 채택 배너가 있나(거부토큰 없는 줄)."""
    for name in ("scope.md", "design-spec.md"):
        for doc in _dddjango_docs(root, name):
            try:
                lines = doc.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for ln in lines:
                if _ADOPT_RE.search(ln) and not any(tok in ln for tok in _REJECT_TOKENS):
                    return True
    return False


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-idempotency-scope-creep] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1
    if not _has_application_container(root):
        return 0  # 표준 레이아웃(`application/`) 미적용 → §1.1 존중, 해당 없음.

    artifacts = _idempotency_artifacts(root)
    if not artifacts:
        return 0  # 멱등성 코드 0 → 자명 통과(Claude 패턴).
    if not _scope_says_not_requested(root):
        return 0  # scope 가 미요청을 단정하지 않음(요청/침묵) → 보수적 통과.
    if _user_adopted(root):
        return 0  # G1 사용자-승인 채택 → 정당, 면제.

    print(
        "[check-idempotency-scope-creep] BLOCKER — scope 가 멱등성을 미요청이라 단정했는데 "
        "멱등성 코드를 구현함(C3 멱등성 스코프크립 · G0=확장금지 위반):"
    )
    for a in artifacts:
        print(f"  - {a.relative_to(root).as_posix()}")
    print(
        "  근거: `architecture-db` §9.6 Idempotency storage 행 · `design-architect`. 사용자가 "
        "멱등성(`Idempotency-Key`)을 요청하지 않았으면 전용 record 테이블·replay store를 silent하게 "
        "빌드하지 않는다. 이번 변경에서 touched된 미요청 멱등성 산출물은 G1 채택 승인이 없는 한 "
        "accepted scope 밖이다. 도입이 필요하면 G1에서 옵션/트레이드오프로 표면화해 사용자 채택을 "
        "받고, 불요·범위 외면 '미적용'(알려진 한계)으로 둔다. 채택할 거면 설계(G1)로 반송하라."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
