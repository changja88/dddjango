#!/usr/bin/env python3
"""refactor_audit.py 픽스처 러너 — 도구 자체의 단위 시험(로드맵 5 · 설계 v5 §10 · 계획 v2 §2-3).

리팩토링 대상 프로젝트의 테스트가 아니라 플러그인 도구의 시험이다. 합성 git 저장소(BC `demo`)에
리뷰어 표·판정 표를 써 넣고 `plan`·`outline`·`check`·`check-verdict`·`residual`·`--self-test` 의
exit 와 요약을 대조한다. 결속·판정 사례의 코퍼스는 작업 트리 설치본(`dddjango/`·`codex-dddjango/`)과
그 규칙 팩이고, 인용·R-ID 는 실제 규범이다.
exit 0 = 전건 기대 일치 · 1 = 불일치.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
TOOL: Path = ROOT / "dddjango" / "scripts" / "refactor_audit.py"
CODEX_SKILLS: Path = ROOT / "codex-dddjango" / "skills"
sys.path.insert(0, str(TOOL.parent))
import refactor_audit as ra  # noqa: E402

DDD: str = "skills/architecture-ddd/references/final.md"
NINJA: str = "skills/implementation-django-ninja/references/final.md"
DJANGO: str = "skills/implementation-django/references/final.md"
DR: str = "agents/discipline-reviewer.md"
DR_SEC: str = "Phase 2 점검 항목 (클린코드·TDD 규율만)"
COORD: str = "commands/dddjango.md"
CLEAN: str = "skills/discipline-cleancode/references/final.md"
PHASE0: str = "Phase 0 — 요구·스코프 (G0)"

POLICY: str = "".join(f"def rule_{i}(x: int) -> int:\n    return x + {i}\n\n\n" for i in range(12))
FILES: "dict[str, str]" = {
    "application/demo/__init__.py": "",
    "application/demo/domain_layer/__init__.py": "",
    "application/demo/domain_layer/policy.py": POLICY,
    "application/demo/domain_layer/big.py": "def big() -> int:\n    return 1\n",
    "application/demo/driving_layer/__init__.py": "",
    "application/demo/driving_layer/api/__init__.py": "",
    "application/demo/driving_layer/api/thing/__init__.py": "",
    "application/demo/driving_layer/api/thing/thing_controller.py": (
        "from ninja_extra import api_controller, route\nfrom ninja.errors import HttpError\n\n\n"
        "@api_controller(\"/thing\")\nclass ThingController:\n    @route.get(\"/\", response={200: dict})\n"
        "    def get(self) -> dict:\n        raise HttpError(404, \"없음\")\n"),
    "application/demo/driven_layer/__init__.py": "",
    "application/demo/driven_layer/django_demo/models/thing_model.py": (
        "from django.db import models\n\n\nclass ThingModel(models.Model):\n    name = models.CharField(max_length=10)\n"),
    "application/demo/test/__init__.py": "",
    "application/demo/test/test_policy.py": "def test_rule() -> None:\n    assert True\n",
    "application/other/domain_layer/x.py": "X = 1\nY = 2\n",
}
HEADER: str = ("| 행# | 규칙 | 반대 방향 규칙 | 파일:행 | 위반 요지 | 동작 불변 정리 가능 | C<n> 과 같음 |\n"
               "|---|---|---|---|---|---|---|\n")
P_LOC: str = "application/demo/domain_layer/policy.py:5"
C_LOC: str = "application/demo/driving_layer/api/thing/thing_controller.py:7"
M_LOC: str = "application/demo/driven_layer/django_demo/models/thing_model.py:4"


def cite(doc: str, sec: str, quote: str) -> str:
    return f"{doc} §{sec} «{quote}»"


def _nov() -> "tuple[str, str, str]":
    """(적용 범위 규범 R-ID, 그 절 제목, 블록 안 인용 한 줄)."""
    corpus = ra.Corpus("claude")
    nov, _t = corpus.scope_norm()
    spans = corpus.block_spans(COORD)[corpus.works[nov]["block"]]
    index = corpus.doc(COORD)
    i, j = spans[0]
    heading: str = next(t for line, _lv, t, _a in reversed(index.headings) if line <= i)
    first: str = next(ln for ln in index.lines[i:j] if ln.strip())      # 창이 빈 줄로 시작할 수 있다
    body: str = first.replace("*", "").replace("`", "").strip().lstrip("-> ").strip()
    return nov, heading, body[:40]


V_B9: str = cite(DDD, "3.2", "domain_layer의 애그리거트로 존재해야 한다")
V_DR13: str = cite(DR, DR_SEC, "원시 리터럴로 산재하면")
V_NINJA: str = cite(NINJA, "2.2", "신규 표준 presentation 표면은 §2.3의 ninja-extra 클래스 컨트롤러다")
V_IMPL8_OVER: str = cite(DJANGO, "8", "greenfield endpoint 구현의 기본 경로를 Django Ninja Router/Schema로 두며, 이 문서의 DRF 내용은")
V_IMPL8: str = cite(DJANGO, "8", "신규 REST API의 리소스 계약, HTTP 상태 코드")
OPP_TARGET: str = cite(NINJA, "2.2", "기존 함수형 Router는 확립된 표면을 유지할 때 보존한다")
OPP_SIBLING: str = cite(NINJA, "2.2", "오류 응답 때문에 클래스 컨트롤러를 함수형 Router로 바꾸지 않는다")
EXCL_OK: str = "R-1230 «이미 DRF를 표준으로 채택한 프로젝트 안에서만 적용한다»"


def row(n: int, rule: str, where: str = P_LOC, opposite: str = "—", fixable: str = "예", same_c: str = "") -> str:
    return f"| {n} | {rule} | {opposite} | {where} | 픽스처 위반 | {fixable} | {same_c} |\n"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def _project(td: Path, files: "dict[str, str] | None" = None) -> Path:
    repo: Path = td / "proj"
    repo.mkdir(parents=True)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    for rel, body in (files or FILES).items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(body, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    return repo


def run(repo: Path, *args: str, tool: Path = TOOL) -> "tuple[int, str]":
    proc = subprocess.run([sys.executable, str(tool), *args], cwd=repo, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


class Audit:
    """합성 프로젝트 1개 + plan 1회 — 시나리오마다 audit 폴더를 새로 만든다."""

    def __init__(self, td: Path) -> None:
        self.repo: Path = _project(td)
        self.base: Path = td / "audits"
        code, out = run(self.repo, "plan", "demo", "--out", str(self.base / "plan0"))
        if code != 0:
            raise RuntimeError(f"plan 실패: {out}")
        self.plan: str = (self.base / "plan0" / "plan.md").read_text(encoding="utf-8")
        self.n: int = 0

    def make(self, rows: "list[str]", verdicts: "list[str] | None" = None) -> Path:
        self.n += 1
        audit: Path = self.base / f"a{self.n}"
        audit.mkdir(parents=True)
        (audit / "plan.md").write_text(self.plan, encoding="utf-8")
        for name, _lens, _cid in ra.Plan(audit).dispatch:
            body: str = HEADER + ("".join(rows) if name.startswith("ddd-") else "")
            (audit / name).write_text(body, encoding="utf-8")
        if verdicts is not None:
            self.verdict(audit, verdicts)
        return audit

    @staticmethod
    def verdict(audit: Path, verdicts: "list[str]") -> None:
        (audit / "verdict.md").write_text("| M | 원 행 | 판정 | 근거 | 파일:행 |\n|---|---|---|---|---|\n"
                                          + "".join(f"| {v} |\n" for v in verdicts), encoding="utf-8")


def expect(fails: "list[str]", label: str, got: "tuple[int, str]", code: int, *needles: str) -> None:
    ok: bool = got[0] == code and all(n in got[1] for n in needles)
    print(("  ✓ " if ok else "  ✗ ") + label)
    if not ok:
        fails.append(f"{label}: exit {got[0]} (기대 {code} · {needles})\n{got[1][-1500:]}")


def plan_cases(fails: "list[str]", td: Path) -> None:
    repo: Path = _project(td / "p")
    a, b = run(repo, "plan", "demo", "--out", str(td / "p1")), run(repo, "plan", "demo", "--out", str(td / "p2"))
    same: bool = (td / "p1" / "plan.md").read_text() == (td / "p2" / "plan.md").read_text()
    text: str = (td / "p1" / "plan.md").read_text(encoding="utf-8")
    expect(fails, "plan 결정성(같은 입력 → 같은 plan.md) · db 켜짐 → db+보안 · audit 앵커 HEAD 줄",
           (0 if same and b[0] == 0 else 9, a[1] + text), 0, "db+보안", "api", "- HEAD ", "- BC 미커밋 변경 0")
    stray: Path = repo / "application/demo/domain_layer/stray.py"
    stray.write_text("X = 1\n", encoding="utf-8")
    dirty_run = run(repo, "plan", "demo", "--out", str(td / "p3"))
    expect(fails, "plan 이 R2 시점 BC 미커밋 변경을 적는다(G0 정지 재개의 재사용 조건)",
           (dirty_run[0], (td / "p3" / "plan.md").read_text(encoding="utf-8")), 0, "- BC 미커밋 변경 1")
    stray.unlink()
    nomodel: "dict[str, str]" = {k: v for k, v in FILES.items() if "models" not in k}
    repo2: Path = _project(td / "q", nomodel)
    expect(fails, "plan 보안 대행 — 모델 없음 → api+보안", run(repo2, "plan", "demo", "--out", str(td / "q1")), 0,
           "api+보안")
    bare: "dict[str, str]" = {k: v for k, v in nomodel.items() if "driving_layer/api" not in k}
    repo3: Path = _project(td / "r", bare)
    expect(fails, "plan 보안 대행 — 모델·어댑터 없음 → discipline+보안",
           run(repo3, "plan", "demo", "--out", str(td / "r1")), 0, "discipline+보안")
    expect(fails, "plan 대상 BC 부재 → 실행 불능", run(repo, "plan", "nope", "--out", str(td / "p9")), 1, "대상 BC 없음")
    flat: "dict[str, str]" = {**FILES, "application/demo/legacy/a.py": "x = 1\n" * 3000,
                              "application/demo/legacy/b.py": "y = 2\n" * 3000}
    repo4: Path = _project(td / "s", flat)
    got4 = run(repo4, "plan", "demo", "--out", str(td / "s1"))
    table: str = (td / "s1" / "plan.md").read_text(encoding="utf-8") if (td / "s1" / "plan.md").is_file() else ""
    expect(fails, "plan 트리 밖 파일도 5,000행 문턱으로 조각을 쌓는다(평면 레거시 BC)",
           (got4[0] if table.count(f"| {ra.OUTSIDE} |") == 2 else 9, got4[1] + table[:400]), 0, "조각 3")
    got = run(repo, "outline", "demo", "--out", str(td / "p1"))
    text = (td / "p1" / "outline.md").read_text(encoding="utf-8") if (td / "p1" / "outline.md").is_file() else ""
    expect(fails, "outline 파일 산출(정의·행)", (got[0], got[1] + text), 0, "class ThingController", "def rule_0")


def check_cases(fails: "list[str]", aud: Audit) -> None:
    rows: "list[str]" = [
        row(1, V_B9),
        row(2, cite(DDD, "3.2", "이 문장은 규범에 없는 날조 인용이다 아무 데도")),
        row(3, cite(DDD, "2.5", "domain_layer의 애그리거트로 존재해야 한다")),
        row(4, V_B9, where="application/other/domain_layer/x.py:1"),
        row(5, V_B9, where="application/demo/domain_layer/policy.py:999"),
        row(6, cite(DDD, "3.2", "**판정 소유→구조 이주 — 판정을 `소유`하면**")),
        row(7, OPP_SIBLING),
        row(8, cite(DR, DR_SEC, "이중 계상 금지")),
        row(9, "근거 없음(불편 #1)"),
        row(10, V_B9, where="application/demo/../other/domain_layer/x.py:1"),
        row(11, cite(DDD, "99.9", "domain_layer의 애그리거트로 존재해야 한다")),
        f"| 12 | {V_B9} | — |\n",
    ]
    audit: Path = aud.make(rows)
    got = run(aud.repo, "check", str(audit))
    text: str = (audit / "check.md").read_text(encoding="utf-8") if (audit / "check.md").is_file() else ""
    status: "dict[str, str]" = {c[0]: c[1] for c in ra._table_rows(text) if c and c[0].startswith("ddd-")}
    want: "dict[str, str]" = {"#1": "통과", "#2": "인용 불일치", "#3": "인용 불일치", "#4": "인용 불일치",
                              "#5": "인용 불일치", "#6": "통과", "#7": "통과", "#8": "통과", "#9": "불편",
                              "#10": "인용 불일치", "#11": "인용 불일치", "#12": "인용 불일치"}
    bad: "list[str]" = [f"{k} {status.get('ddd-01' + k)}≠{v}" for k, v in want.items() if status.get("ddd-01" + k) != v]
    expect(fails, "check 날조·틀린 절·BC 밖·행 범위 밖·`..` 탈출·없는 절 토큰·칸 부족 번호 행 → 인용 불일치 · "
           "마크업·줄바꿈 인용 통과 · 불편 행",
           (got[0] if not bad else 9, got[1] + "\n" + "; ".join(bad)), 2, "인용 불일치 7", "규칙 근거 없는 불편 1")
    reasons: "dict[str, str]" = {c[0]: c[-1] for c in ra._table_rows(text) if c and c[0].startswith("ddd-")}
    expect(fails, "check 없는 절 = «절 없음»(문서 전체로 대체 금지) · 칸 부족 = «칸 부족»(무언 삭제 금지)",
           (0 if "절 없음" in reasons.get("ddd-01#11", "") and "칸 부족" in reasons.get("ddd-01#12", "") else 9,
            str(reasons)), 0)
    two = [c for c in ra._table_rows(text) if c and c[0] == "ddd-01#8"]
    expect(fails, "check 서로 다른 두 블록 적중 인용 → 결속 실패(규범 없음)",
           (0 if two and two[0][2] == "—" and "서로 다른 블록" in two[0][6] else 9, text[-800:]), 0)


def sections_case(fails: "list[str]", aud: Audit, nov_id: str) -> None:
    audit: Path = aud.make([row(1, V_B9, opposite=OPP_SIBLING), row(2, cite(DDD, "2.5", "없는 인용 문구 아무것")),
                            row(3, V_B9, opposite=cite(DDD, "99.9", "아무 인용"))])
    got = run(aud.repo, "sections", str(audit))
    text: str = (audit / "sections.md").read_text(encoding="utf-8") if (audit / "sections.md").is_file() else ""
    expect(fails, "sections: 인용 절·반대 방향 절 원문 + 블록 `R-ID · 종류 · 라벨` + 적용 범위 규범 원문·대상 목록(인용 불일치 행 절 제외)",
           (got[0] if f"## {DDD} §2.5" not in text and "§99.9" not in text else 9, got[1] + text), 0,
           f"〔{nov_id} · Override", "| R-0674 | Permission |", "〔블록 s017-3.2/b9 — R-0115 · Obligation",
           f"## {DDD} §3.2", f"## {NINJA} §2.2", "절 2")


def verdict_cases(fails: "list[str]", aud: Audit, nov: "tuple[str, str, str]") -> None:
    nov_id, nov_head, nov_quote = nov
    nov_cite: str = cite(COORD, nov_head, nov_quote)
    cv = lambda audit, *extra: run(aud.repo, "check-verdict", str(audit), *extra)  # noqa: E731

    a = aud.make([row(1, V_B9)], ["M1 | ddd-01#1 | 제외 | R-0116 «항-(1) 판정·불변식을 소유하면 도메인 컨텍스트 → 표준 구조로 이주한다» | "])
    expect(fails, "의무를 제외 근거 → red(②)", cv(a), 2, "② R-0116")
    a = aud.make([row(1, V_NINJA), row(2, V_DR13), row(3, V_DR13), row(4, V_B9)],
                 ["M1 | ddd-01#1 | 제외 | R-0674 «기존 함수형 Router는 확립된 표면을 유지할 때 보존한다» | ",
                  "M2 | ddd-01#2 | 제외 | R-0965 «이번 작업이 touched한 코드만 본다» | ",
                  "M3 | ddd-01#3 | 제외 | R-0982 «이번 diff에 새로 들어온 변경만 본다» | ",
                  "M4 | ddd-01#4 | 제외 | R-0125 «이 이주는 판정이 새로 얹히는 그 코드에 한정한다» | "])
    expect(fails, "대상 목록 규범(R-0674·R-0965·R-0982·R-0125)을 제외 근거 → red(③)", cv(a), 2,
           "③ 대상 목록 규범 R-0674", "R-0965", "R-0982", "R-0125", "red 4")
    a = aud.make([row(1, V_B9)], [f"M1 | ddd-01#1 | 제외 | {nov_id} «{nov_quote}» | "])
    expect(fails, "적용 범위 규범을 제외 근거(근거 R-ID) → red", cv(a), 2, f"③ 적용 범위 규범 {nov_id}")
    a = aud.make([row(1, V_B9, opposite=nov_cite)], [f"M1 | ddd-01#1 | 제외 | {nov_id} «{nov_quote}» | "])
    expect(fails, "적용 범위 규범을 제외 근거(반대 방향 열 경로) → red", cv(a), 2, f"③ 적용 범위 규범 {nov_id}")
    a = aud.make([row(1, V_B9, opposite=nov_cite)], ["M1 | ddd-01#1 | 사용자 판단 | 규칙 충돌 | "])
    expect(fails, "적용 범위 규범을 반대 방향 규칙으로 사용자 판단 → red", cv(a), 2, f"적용 범위 규범 {nov_id}")
    a = aud.make([row(1, V_B9)], ["M1 | ddd-01#1 | 제외 | R-0117 «기존 코드를 표준으로 일괄 강제하지 않는다» | "])
    expect(fails, "R-0125 문장의 부분 인용 + 형제 예외 R-0117 → red(문장 단위 어구)", cv(a), 2, "③ 인용이 든 문장에 적용 한정 어구")
    a = aud.make([row(1, V_B9)], ["M1 | ddd-01#1 | 제외 | R-0183 «이동 권한은 G0 빚 결정→슬라이스 0 뿐» | "])
    expect(fails, "R-0183 «이동 권한은 G0 …» 제외 → red(옛 C 목록 통로)", cv(a), 2, "③ 인용이 든 문장에 적용 한정 어구")
    a = aud.make([row(1, V_B9)], ["M1 | ddd-01#1 | 제외 | R-0983 «프로덕션 경로에 배선되지 않은 테스트 격리 전용 설정은 통과» | "])
    expect(fails, "R-0983 + 같은 문장 부분 인용 → red(공백 든 어구 대칭 정규화)", cv(a), 2, "③ 인용이 든 문장에 적용 한정 어구")
    a = aud.make([row(1, V_DR13)], ["M1 | ddd-01#1 | 오탐 | «이번 작업이 touched한 코드만 본다» | "])
    expect(fails, "touched 인용 오탐 → red", cv(a), 2, "오탐 인용이 든 문장에 적용 한정 어구")
    a = aud.make([row(1, V_B9)], ["M1 | ddd-01#1 | 오탐 | «원시 리터럴로 산재하면» | "])
    expect(fails, "다른 문장(다른 블록) 인용 오탐 → red", cv(a), 2, "그 블록에 없다")
    a = aud.make([row(1, cite(DR, DR_SEC, "이중 계상 금지"))], ["M1 | ddd-01#1 | 오탐 | «이중 계상 금지» | "])
    expect(fails, "결속 실패 행의 오탐 → red(제외·오탐 근거 불가)", cv(a), 2, "결속되지 않아")
    a = aud.make([row(1, V_IMPL8_OVER)], ["M1 | ddd-01#1 | 제외 | R-1230 «이 문서의 DRF 내용은 기존 DRF 코드 유지보수» | "])
    expect(fails, "혼합 블록 겹침 인용 제외 → red(④)", cv(a), 2, "④ 혼합 블록")
    a = aud.make([row(1, V_IMPL8)], [f"M1 | ddd-01#1 | 제외 | {EXCL_OK} | "])
    expect(fails, "정당한 제외(범위 밖 블록 예외 · 겹침 없음) → green · 혼합 블록 표시", cv(a), 0, "제외 1", "혼합 블록 제외 1")
    a = aud.make([row(1, V_B9, where=M_LOC)], ["M1 | ddd-01#1 | 별도 요청 | 모델 필드 | "])
    expect(fails, "리뷰어 «아니오» 없는 별도 요청 → 채택 재분류", cv(a), 0, "재분류: M1 별도 요청 → 채택", "채택 1")
    a = aud.make([row(1, V_B9, where=M_LOC, fixable="아니오 — 사유: 마이그레이션")], ["M1 | ddd-01#1 | 별도 요청 | 모델 필드 | "])
    expect(fails, "정당한 별도 요청(리뷰어 «아니오» + 모델 필드) → 유지", cv(a), 0, "별도 요청 1")
    a = aud.make([row(1, V_B9, where=C_LOC, fixable="아니오 — 사유: 타 BC")],
                 ["M1 | ddd-01#1 | 별도 요청 | 타 BC application/other/domain_layer/x.py:1 | "])
    expect(fails, "정당한 별도 요청(타 BC 근거 실재) → 유지", cv(a), 0, "별도 요청 1")
    a = aud.make([row(1, V_B9, where=C_LOC), row(2, V_B9, where=C_LOC, same_c="C1")],
                 ["M1 | ddd-01#1 | 병합 → C1 | 같은 파일 | ", "M2 | ddd-01#2 | 병합 → C1 | 리뷰어 표시 | "])
    expect(fails, "리뷰어 표시 없는 M→C 병합(같은 파일이어도) → red · 표시 있으면 통과", cv(a), 2, "M1 병합", "red 1")
    a = aud.make([row(1, V_B9), row(2, V_B9), row(3, V_IMPL8), row(4, V_B9)],
                 ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 병합 → M1 | | ",
                  f"M3 | ddd-01#3 | 제외 | {EXCL_OK} | ", "M4 | ddd-01#4 | 병합 → M3 | | "])
    expect(fails, "M→M 병합은 채택 대상만(제외 항목으로 사슬 병합 → red)", cv(a), 2, "M4 병합", "red 1")
    a = aud.make([row(1, V_NINJA, opposite=OPP_TARGET)], ["M1 | ddd-01#1 | 사용자 판단 | 규칙 충돌 | "])
    expect(fails, "사용자 판단: 대상 문장을 반대 방향 규칙으로 → red", cv(a), 2, "결정 18 이 가른 충돌")
    a = aud.make([row(1, V_NINJA, opposite=OPP_SIBLING)], ["M1 | ddd-01#1 | 사용자 판단 | 규칙 충돌 | "])
    expect(fails, "사용자 판단: 범위 블록의 대상 아닌 형제 문장 → 통과", cv(a), 0, "사용자 판단 1")
    stack_opp: str = cite(COORD, PHASE0, "기존 프로젝트에 확립된 API 스택이 있으면 그 정체(어느 프레임워크인가)를 "
                                         "architect가 식별하고, 신규 표면의 스택 확정은")
    a = aud.make([row(1, V_NINJA, opposite=stack_opp)],
                 ["M1 | ddd-01#1 | 제외 | R-0180 «lens는 관심사(계약·데이터의 유무)만 제안한다» | "])
    expect(fails, "반대 방향 경로로만 서는 제외 — 리뷰어 반대 방향 인용 문장에 한정 어구(R-0180 형) → red",
           cv(a), 2, "② 반대 방향 규칙 인용이 든 문장에 적용 한정 어구")
    a = aud.make([row(1, cite(CLEAN, "2.14", "같은 지식의 철자를 서로 다른 파일 2곳 이상이 공유하면 명명 상수로"),
                      opposite=cite(CLEAN, "2.14", "우연히 값이 같을 뿐 다른 지식이면 합치지 않는다"))],
                 ["M1 | ddd-01#1 | 제외 | R-1395 «우연히 값이 같을 뿐 다른 지식이면 합치지 않는다» | "])
    expect(fails, "반대 방향 경로의 정당한 제외(5B R-1395 금지 형 · 범위 밖 블록) → 통과", cv(a), 0, "제외 1")
    a = aud.make([row(1, V_B9)], ["M1 | ddd-01#1 | 병합 | 대상 없음 | "])
    expect(fails, "대상 없는 병합 → 범주 밖 red(역추적 exit 1 아님)", cv(a), 2, "판정 범주 밖")
    a = aud.make([row(1, V_B9), row(2, V_B9)], ["M1 | ddd-01#1 | 채택 | | "])
    expect(fails, "판정 없는 통과 행 → red", cv(a), 2, "판정이 없다")
    a = aud.make([row(1, V_B9), row(2, V_B9), row(3, V_B9)],
                 ["M1 | ddd-01#1 | 제외 | R-0116 «항-(1) 판정·불변식을 소유하면 도메인 컨텍스트 → 표준 구조로 이주한다» | ",
                  "M2 | ddd-01#2 | 병합 | 대상 없음 | "])
    got = cv(a, "--final")
    log: str = (a / "verdict-log.md").read_text(encoding="utf-8") if (a / "verdict-log.md").is_file() else ""
    expect(fails, "--final: 남은 red 행·범주 밖·판정 없는 통과 행 → 채택(새 번호)으로 기록 · exit 0 · 로그 표 재분류",
           (got[0], got[1] + log), 0, "→ 채택", "채택 3", "판정 없는 통과 행 ddd-01#3 → 채택", "| M3 | ddd-01#3 | 채택 |",
           "- 재분류:")
    # 대리 출처 축소 · M 번호 유지(같은 audit 에서 R3 재실행)
    a = aud.make([row(1, V_IMPL8)], ["M1 | ddd-01#1 | 채택 | | "])
    first = cv(a)
    Audit.verdict(a, [f"M1 | ddd-01#1 | 제외 | {EXCL_OK} | "])
    fb: Path = a / "feedback.md"
    fb.write_text("출처 = 대리 답 ⓐ <record.md:1>(0300)\n판정 근거 오류 지적\n", encoding="utf-8")
    expect(fails, "대리 출처 피드백으로 채택 축소(채택 → 제외) → red",
           (cv(a, "--feedback", str(fb))[0] if first[0] == 0 else 9, cv(a, "--feedback", str(fb))[1]), 2, "대리 출처")
    fb.write_text("출처 = 대리 답 ⓐ <record.md:1>(0305) — 사용자 원문 없음\n", encoding="utf-8")
    expect(fails, "출처 값 머리가 대리인데 «사용자 원문» 부분 문자열 → 여전히 대리(축소 red)",
           cv(a, "--feedback", str(fb)), 2, "대리 출처")
    fb.write_text("출처 = 상시 답 .dddjango/standing-answer.md:3@0123456789ab\n", encoding="utf-8")
    expect(fails, "S13 상시 답 출처 피드백의 채택 축소 → 대리(red — R3 로 새지 않는다)",
           cv(a, "--feedback", str(fb)), 2, "대리 출처")
    expect(fails, "앞 확정 판이 있는데 --feedback 없이 재실행해 채택 축소 → red", cv(a), 2, "출처 없는 재실행")
    fb.write_text("출처 = 본인 직접(0310)\n", encoding="utf-8")
    expect(fails, "본인 직접 출처 피드백은 축소 가능 → green", cv(a, "--feedback", str(fb)), 0, "제외 1")
    Audit.verdict(a, [f"M2 | ddd-01#1 | 제외 | {EXCL_OK} | "])
    expect(fails, "R3 재실행이 기존 M 번호를 바꿈 → red", cv(a), 2, "번호를 M1 → M2")


def _res_folder(repo: Path, rows: "list[str]", verdicts: "list[str]",
                disc: "list[str] | None" = None, confirm: bool = True) -> "tuple[Path, str]":
    """리팩토링 실행 산출물 폴더(G0 ⓐ 뒤 · 앵커 기록) — (폴더, 앵커). `disc` = discipline 렌즈 표 행.
    `confirm` = check-verdict exit 0 으로 확정 표(verdict-final.md)까지 만든다(아니면 호출자가 확정한다)."""
    anchor: str = _git(repo, "rev-parse", "HEAD").strip()
    folder: Path = repo / ".dddjango" / "refactor-demo"
    audit: Path = folder / "audit" / "20260927-0250"
    code, out = run(repo, "plan", "demo", "--out", str(audit))
    if code != 0:
        raise RuntimeError(f"residual 준비 plan 실패: {out}")
    for name, _l, _c in ra.Plan(audit).dispatch:
        body: str = "".join(rows) if name.startswith("ddd-") else "".join(disc or []) if name.startswith("discipline-") else ""
        (audit / name).write_text(HEADER + body, encoding="utf-8")
    Audit.verdict(audit, verdicts)
    if confirm:
        code, out = run(repo, "check-verdict", str(audit))
        if code != 0:
            raise RuntimeError(f"residual 준비 check-verdict exit {code}: {out}")
    (folder / "build_anchor").write_text(anchor + "\n", encoding="utf-8")
    return folder, anchor


def _fresh_stamp(repo: Path, folder: Path, clear: bool = False) -> Path:
    """residual 시각을 새로 연다(`clear` = 앞 시각 폴더를 지워 이월 없이) — 그 시각 폴더."""
    if clear:
        shutil.rmtree(folder / "residual", ignore_errors=True)
    got = run(repo, "residual", str(folder))
    if "--finalize " not in got[1]:                  # 열리지 않음 — residual 밖 자리표시(뒤 --finalize 가 실행 불능 exit 1)
        placeholder: Path = folder / "(열리지 않음)"
        placeholder.mkdir(parents=True, exist_ok=True)
        return placeholder
    return folder / "residual" / got[1].split("--finalize ", 1)[1].split()[0]


def residual_moved_case(fails: "list[str]", td: Path) -> None:
    """커밋된 `git mv` 는 옛 경로도 «바뀜»이다(--no-renames) — 결정적 잔존이 아니라 리뷰어 묶음."""
    repo: Path = _project(td / "mv")
    folder, anchor = _res_folder(repo, [row(1, V_B9, where=P_LOC)], ["M1 | ddd-01#1 | 채택 | | "])
    (folder / "refactor-scope.md").write_text(
        f"실행 · G0 승인 20260927-0300 · 모드 리팩토링 · audit 20260927-0250 · build_anchor {anchor}\n\n"
        "- M1 · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(0300)\n", encoding="utf-8")
    (repo / "application/demo/domain_layer/rules").mkdir()
    _git(repo, "mv", "application/demo/domain_layer/policy.py", "application/demo/domain_layer/rules/policy.py")
    _git(repo, "commit", "-qm", "move")
    expect(fails, "residual 커밋된 git mv 항목 → 결정적 잔존 아님(리뷰어 묶음)", run(repo, "residual", str(folder)), 0,
           "결정적 잔존 0", "리뷰어 확인 대상 1(ddd)", "M_m 미정")


def residual_cases(fails: "list[str]", td: Path) -> None:
    repo: Path = _project(td / "res")
    rows: "list[str]" = [row(1, V_B9, where=P_LOC), row(2, V_B9, where=C_LOC), row(3, V_B9, where=P_LOC),
                         row(4, V_B9, where="application/demo/domain_layer/big.py:1").replace("픽스처 위반", "[ⓓ#644] 후보 겹침"),
                         row(5, V_B9, where="application/demo/domain_layer/policy.py:9")]
    folder, anchor = _res_folder(repo, rows, ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 채택 | | ",
                                              "M3 | ddd-01#3 | 채택 | | ", "M4 | ddd-01#4 | 채택 | | ",
                                              "M5 | ddd-01#5 | 병합 → M2 | | "])
    (folder / "refactor-scope.md").write_text(
        f"실행 · G0 승인 20260927-0300 · 모드 리팩토링 · audit 20260927-0250 · build_anchor {anchor}\n\n"
        "- C1, M1, M2, M3 · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(0300)\n\n"
        "## ⓐ 재상정 20260927-0400\n\n- M3 · 결정 = 별도 요청 · 사유 = 픽스처 · 출처 = 본인 직접(0400)\n"
        "- M1 · 결정 = · 사유 = (답 대기 — 빈 자리표시는 결정이 아니다) · 출처 = —\n",
        encoding="utf-8")
    thing: Path = repo / "application/demo/driving_layer/api/thing/thing_controller.py"
    thing.write_text(thing.read_text(encoding="utf-8") + "\n# 정리\n", encoding="utf-8")
    first = run(repo, "residual", str(folder))
    expect(fails, "residual 무변 파일 → 결정적 잔존(리뷰어 0회) · 바뀐 파일만 리뷰어 · 재상정 항목 제외", first, 0,
           "결정적 잔존 1", "리뷰어 확인 대상 1(ddd)")
    stamp: str = first[1].split("--finalize ", 1)[1].split(")", 1)[0].split()[0] if "--finalize " in first[1] else ""
    rdir: Path = folder / "residual" / stamp
    bundle: str = (rdir / "review-ddd.md").read_text(encoding="utf-8") if (rdir / "review-ddd.md").is_file() else ""
    expect(fails, "residual 잔존 확인 묶음에 병합 행(원 행 전부)과 «(병합 M<k>)» 표시",
           (0 if "- 원 행 ddd-01#2:" in bundle and "- 원 행 ddd-01#5 (병합 M5):" in bundle else 9, bundle), 0)
    (rdir / "result-ddd.md").write_text("| M | 판정 | 근거 |\n|---|---|---|\n| M2 | 해소 | 고쳤다 |\n", encoding="utf-8")
    expect(fails, "residual 근거 칸 머리가 위치가 아닌 해소 → 근거 판형 아님(잔존 아님 · 재기재 안내)",
           run(repo, "residual", str(folder), "--finalize", stamp), 2, "M_m=2", "리뷰어 잔존 0 · 근거 판형 아님 1",
           "근거 판형 아님: M2(ddd: `고쳤다`)")
    # 같은 시각 재확정은 판형 아님 행만 다시 본다(동결) — 사례마다 시각을 새로 연다.
    rdir = _fresh_stamp(repo, folder, clear=True)
    (rdir / "result-ddd.md").write_text(
        "| M | 판정 | 근거 |\n|---|---|---|\n| M2 | 해소 | application/demo/test/test_policy.py:1 |\n", encoding="utf-8")
    expect(fails, "residual 해소 근거가 앵커 이후 안 바뀐 파일(대응 경로도 아님) → 잔존",
           run(repo, "residual", str(folder), "--finalize", rdir.name), 2, "M_m=2", "리뷰어 잔존 1")
    rdir = _fresh_stamp(repo, folder, clear=True)
    (rdir / "result-ddd.md").write_text(
        f"| M | 판정 | 근거 |\n|---|---|---|\n| M2 | 해소 | {C_LOC} |\n", encoding="utf-8")
    expect(fails, "residual 새 파일:행 근거가 있는 해소 → 해소", run(repo, "residual", str(folder), "--finalize", rdir.name), 2,
           "M_m=1", "해소 1")
    scope: Path = folder / "refactor-scope.md"
    scope.write_text(scope.read_text(encoding="utf-8").replace("C1, M1, M2, M3", "C1, M1, M2, M3, M4"), encoding="utf-8")
    (repo / "application/demo/domain_layer/big").mkdir()
    (repo / "application/demo/domain_layer/big.py").rename(repo / "application/demo/domain_layer/big/big.py")
    run_dir: Path = folder / "behavior" / "20260927-0300"
    run_dir.mkdir(parents=True)
    (run_dir / "w1-open.json").write_text(json.dumps({"kind": "code"}), encoding="utf-8")
    (run_dir / "w1-close.json").write_text(json.dumps([{"verdict": "green", "map_items": {
        "pairs": {"application/demo/domain_layer/big.py": "application/demo/domain_layer/big/big.py"},
        "dirs": {}, "fm": {"application/demo/domain_layer/big.py": "application/demo/domain_layer/big/big.py"}}}]),
        encoding="utf-8")
    expect(fails, "residual ⓓ 겹침 항목에 --candidates 없음 → 실행 불능", run(repo, "residual", str(folder)), 1, "--candidates")
    cand: Path = td / "cand.txt"
    cand.write_text("[ⓓ#644] application/demo/domain_layer/big/big.py: 행위 칸 200행 초과 — 물음: 분할?\n", encoding="utf-8")
    expect(fails, "residual 대응표로 옮긴 경로에 같은 ⓓ 가 남음 → 결정적 잔존 · 직전 해소(M2) 무변 → 이월(묶지 않음)",
           run(repo, "residual", str(folder), "--candidates", str(cand)), 2, "결정적 잔존 2", "해소 유지 1",
           "리뷰어 확인 대상 0")
    thing.write_text(thing.read_text(encoding="utf-8") + "# 반송 편집\n", encoding="utf-8")
    expect(fails, "residual 직전 해소 항목의 파일을 반송이 건드림 → 이월 없이 다시 묶는다",
           run(repo, "residual", str(folder), "--candidates", str(cand)), 0, "리뷰어 확인 대상 1(ddd)", "M_m 미정")


def residual_ground_cases(fails: "list[str]", td: Path) -> None:
    """E1 — 해소 근거 칸 판형(머리 = 첫 `—` 앞 위치만) · 근거 판형 아님 · 같은 시각 동결 · 렌즈 완전성 · 산출물 폴더 ·
    판정 칸 정확 일치(설계 R8c §2.1 · §4.1 · §7). M1 = 무변 파일(결정적 잔존 1 고정) · M2 = 바뀐 파일(ddd 리뷰어 확인)."""
    repo: Path = _project(td / "grd")
    folder, anchor = _res_folder(repo, [row(1, V_B9, where=P_LOC), row(2, V_B9, where=C_LOC), row(3, V_B9, where=C_LOC)],
                                 ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 채택 | | ",
                                  "M3 | ddd-01#3 · discipline-01#1 | 채택 | | "], disc=[row(1, V_DR13, where=C_LOC)])
    scope_path: Path = folder / "refactor-scope.md"

    def scope(keys: str) -> None:
        scope_path.write_text(f"실행 · G0 승인 20260927-0300 · 모드 리팩토링 · audit 20260927-0250 · build_anchor {anchor}\n\n"
                              f"- {keys} · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(0300)\n", encoding="utf-8")

    def fin(rdir: Path, ddd: str, disc: "str | None" = None) -> "tuple[int, str]":
        head: str = "| M | 판정 | 근거 |\n|---|---|---|\n"
        (rdir / "result-ddd.md").write_text(head + ddd, encoding="utf-8")
        if disc is not None:
            (rdir / "result-discipline.md").write_text(head + disc, encoding="utf-8")
        got = run(repo, "residual", str(folder), "--finalize", rdir.name)
        result: Path = rdir / "result.md"
        return got[0], got[1] + (result.read_text(encoding="utf-8") if result.is_file() else "")

    thing: Path = repo / "application/demo/driving_layer/api/thing/thing_controller.py"
    thing.write_text(thing.read_text(encoding="utf-8") + "\n# 정리\n", encoding="utf-8")
    scope("M1, M2")
    rdir: Path = _fresh_stamp(repo, folder, clear=True)
    bundle: str = (rdir / "review-ddd.md").read_text(encoding="utf-8") if (rdir / "review-ddd.md").is_file() else ""
    expect(fails, "O2 묶음 머리에 근거 칸 판형(` — ` 앞 위치만 · 줄임 없이 · 구분 ` · `)과 예시",
           (0 if "` — ` 앞에는 저장소 루트 기준 새 위치만" in bundle and "`:16`·`15·16` 줄임 없이" in bundle
            and "예: `M3 | 해소 | application/<bc>/domain_layer/x/x.py:12-18 · " in bundle else 9, bundle), 0)
    got = fin(rdir, f"| M2 | 해소 | 이 파일의 리터럴은 {C_LOC}의 정의 한 곳 |\n")
    expect(fails, "G1 머리에 조사(WR2 M11 모양) → 근거 판형 아님 1 · 리뷰어 잔존 0 · exit 2", got, 2,
           "M_m=2(결정적 잔존 1 · 리뷰어 잔존 0 · 근거 판형 아님 1 · 판단 불가 0)", "| M2 | 근거 판형 아님(ddd) |")
    expect(fails, "O1 `요약:` 뒤 재기재 안내 — 항목·렌즈·불량 토큰 · 같은 시각 --finalize", got, 2,
           "  근거 판형 아님: M2(ddd: `이`) — 그 행만 같은 렌즈 리뷰어에게", f"--finalize {rdir.name} 한 번 더")
    got = fin(rdir, f"| M2 | 해소 | {C_LOC} — 리터럴은 {C_LOC}의 정의 한 곳 |\n")
    expect(fails, "N6b 판형 아님 행을 같은 시각에 판형대로 고쳐 재확정 → 해소", got, 2, "근거 판형 아님 0", "해소 1",
           "| M2 | 해소 |")
    cases: "list[tuple[str, str, tuple[str, ...]]]" = [
        ("G2 조사가 꼬리", f"{C_LOC} — 리터럴은 {C_LOC}의 정의 한 곳", ("근거 판형 아님 0", "해소 1")),
        ("G3 괄호·설계 근거 위치가 꼬리(WR2 M10 모양)",
         f"{C_LOC} — 남은 두 return(:46 · :49)은 표기 반복(design-spec.md:103에 이유)", ("리뷰어 잔존 0", "해소 1")),
        ("G4 맥락·제외 위치가 꼬리(R2 M18·M1 모양)",
         f"{C_LOC} — 남은 리터럴 thing_controller.py:3·5 는 처음부터 제외한 범주 · policy.py:9 문구는 뺀 요지 몫",
         ("리뷰어 잔존 0", "해소 1")),
        ("N1 꼬리에만 위치 → 판형 아님(해소 아님)", f"— 남은 리터럴 {C_LOC} 는 제외 범주", ("근거 판형 아님 1", "해소 0")),
        ("N2 허용 밖(안 바뀐 파일) 머리 → 리뷰어 잔존(판형 아님 아님)", f"{T_LOC} — 테스트에서 확인",
         ("리뷰어 잔존 1 · 근거 판형 아님 0",)),
        ("N3 머리에 바뀐 파일·안 바뀐 파일 섞임 → 잔존", f"{C_LOC} · {T_LOC} — 둘 다 고쳤다", ("리뷰어 잔존 1",)),
        ("N4a 실재 안 함(맨 파일 이름) → 판형 아님", "thing_controller.py:7 — 고쳤다", ("근거 판형 아님 1", "`thing_controller.py:7`")),
        ("N4b 행 범위 밖 → 판형 아님", "application/demo/driving_layer/api/thing/thing_controller.py:999 — 고쳤다",
         ("근거 판형 아님 1",)),
        ("N5 머리에 산문 → 판형 아님", f"{C_LOC} 에서 고침 — 매핑 한 곳", ("근거 판형 아님 1", "`에서`")),
        ("대시 변형(en dash) 은 구분자가 아니다 → 판형 아님", f"{C_LOC} – 고쳤다", ("근거 판형 아님 1", "해소 0")),
        ("m2 절대 경로 머리(실재 · 바뀐 파일) → 판형 아님", f"{repo}/{C_LOC} — 고쳤다", ("근거 판형 아님 1", "해소 0")),
        ("m2 `..` 경로 머리(실재 · 바뀐 파일) → 판형 아님", f"../proj/{C_LOC} — 고쳤다", ("근거 판형 아님 1", "해소 0")),
        ("M2 산출물 폴더 파일(미추적 = 바뀐 파일) 머리 → 잔존(해소 아님)",
         ".dddjango/refactor-demo/refactor-scope.md:1 — 명세에 적었다", ("리뷰어 잔존 1", "해소 0")),
    ]
    for label, cell, needles in cases:
        rdir = _fresh_stamp(repo, folder, clear=True)
        expect(fails, label, fin(rdir, f"| M2 | 해소 | {cell} |\n"), 2, *needles)
    rdir = _fresh_stamp(repo, folder, clear=True)
    expect(fails, "m1 판정 칸 «해소 안 됨» → 판단 불가(접두어로 해소 아님)", fin(rdir, f"| M2 | 해소 안 됨 | {C_LOC} — 남아 있다 |\n"),
           2, "판단 불가 1", "해소 0")
    rdir = _fresh_stamp(repo, folder, clear=True)
    expect(fails, "m1 판정 칸 강조·백틱(`**해소**`)은 벗겨 읽는다 → 해소", fin(rdir, f"| M2 | **`해소`** | {C_LOC} — 고쳤다 |\n"),
           2, "판단 불가 0", "해소 1")
    rdir = _fresh_stamp(repo, folder, clear=True)
    expect(fails, "N7 같은 M 두 행 잔존 + 판형 아님 해소 → 리뷰어 잔존 1 · 판형 아님 0",
           fin(rdir, "| M2 | 잔존 | 남았다 |\n| M2 | 해소 | 고쳤다 |\n"), 2, "리뷰어 잔존 1 · 근거 판형 아님 0")
    rdir = _fresh_stamp(repo, folder, clear=True)
    fin(rdir, f"| M2 | 해소 | — 남은 리터럴 {C_LOC} 는 제외 범주 |\n")
    got = fin(rdir, f"| M2 | 해소 | — 남은 리터럴 {C_LOC} 는 제외 범주 |\n")
    expect(fails, "N6 같은 시각 재확정에도 판형 아님 → 잔존(근거 판형 아님 반복)", got, 2,
           "리뷰어 잔존 1 · 근거 판형 아님 0", "| M2 | 잔존(근거 판형 아님 반복) |")
    expect(fails, "N6 세 번째 재확정(판형대로 고침)도 잔존 유지(동결)", fin(rdir, f"| M2 | 해소 | {C_LOC} — 고쳤다 |\n"), 2,
           "리뷰어 잔존 1", "해소 0")
    rdir = _fresh_stamp(repo, folder, clear=True)
    fin(rdir, "| M2 | 잔존 | 남았다 |\n")
    expect(fails, "M1 같은 시각 재확정으로 잔존 행을 해소로 뒤집기 → 잔존 유지(동결)",
           fin(rdir, f"| M2 | 해소 | {C_LOC} — 다시 보니 해소 |\n"), 2, "리뷰어 잔존 1", "해소 0")
    rdir = _fresh_stamp(repo, folder, clear=True)
    fin(rdir, f"| M2 | 해소 | {C_LOC} — 고쳤다 |\n")
    expect(fails, "MJ1 같은 시각 재확정에서 앞 판 해소를 리뷰어가 잔존으로 고쳐 씀 → 잔존(나빠지는 쪽은 막지 않는다)",
           fin(rdir, "| M2 | 잔존 | 다시 보니 남았다 |\n"), 2, "리뷰어 잔존 1", "해소 0")
    rdir = _fresh_stamp(repo, folder, clear=True)
    fin(rdir, f"| M2 | 해소 | {C_LOC} — 고쳤다 |\n")
    expect(fails, "MJ1 짝 — 같은 시각 재확정에 M2 행 없음 → 앞 판 해소 유지", fin(rdir, ""), 2, "리뷰어 잔존 0", "해소 1",
           "| M2 | 해소 |")
    # §9.7 강등 일반화 — 앞 판 해소의 강등은 모두 받고, 해소 아닌 확정은 해소·다시 판정 쪽으로 가지 않는다
    rdir = _fresh_stamp(repo, folder, clear=True)
    fin(rdir, f"| M2 | 해소 | {C_LOC} — 고쳤다 |\n")
    expect(fails, "§9.7 앞 판 해소 → 이번 판단 불가 → 판단 불가(exit 2)", fin(rdir, "| M2 | 판단 불가 | 다시 보니 모르겠다 |\n"), 2,
           "판단 불가 1", "해소 0")
    rdir = _fresh_stamp(repo, folder, clear=True)
    fin(rdir, f"| M2 | 해소 | {C_LOC} — 고쳤다 |\n")
    expect(fails, "§9.7 앞 판 해소 → 이번 판형 아님 행 → 판형 아님(exit 2 · 재기재 안내)", fin(rdir, "| M2 | 해소 | 고쳤다 |\n"), 2,
           "근거 판형 아님 1", "해소 0", "근거 판형 아님: M2(ddd: `고쳤다`)")
    rdir = _fresh_stamp(repo, folder, clear=True)
    fin(rdir, "| M2 | 판단 불가 | 모르겠다 |\n")
    expect(fails, "§9.7 앞 판 판단 불가 → 이번 해소 → 판단 불가 유지", fin(rdir, f"| M2 | 해소 | {C_LOC} — 고쳤다 |\n"), 2,
           "판단 불가 1", "해소 0")
    rdir = _fresh_stamp(repo, folder, clear=True)
    fin(rdir, "| M2 | 잔존 | 남았다 |\n")
    expect(fails, "§9.7 앞 판 잔존 → 이번 판형 아님 행 → 잔존 유지(판형 아님 경유 우회 봉쇄)",
           fin(rdir, "| M2 | 해소 | 고쳤다 |\n"), 2, "리뷰어 잔존 1 · 근거 판형 아님 0", "해소 0")
    # mi3 — 같은 시각 재확정의 해소 유지는 앞 판 지문을 쓴다(그 사이 편집이 이월을 통과하지 못한다)
    rdir = _fresh_stamp(repo, folder, clear=True)
    fin(rdir, f"| M2 | 해소 | {C_LOC} — 고쳤다 |\n")
    thing.write_text(thing.read_text(encoding="utf-8") + "# 재확정 사이 편집\n", encoding="utf-8")
    fin(rdir, f"| M2 | 해소 | {C_LOC} — 고쳤다 |\n")
    expect(fails, "mi3 1차 해소 → 파일 편집 → 같은 시각 2차(앞 판 지문 유지) → 새 시각은 이월 없이 M2 를 다시 묶는다",
           run(repo, "residual", str(folder)), 0, "리뷰어 확인 대상 1(ddd) · M_m 미정")
    # mi2 — 판형 아님 이력은 행 삭제(답 없음)로 끊기지 않는다(리뷰 x2 순서)
    rdir = _fresh_stamp(repo, folder, clear=True)
    fin(rdir, "| M2 | 해소 | 고쳤다 |\n")
    fin(rdir, "")
    got = fin(rdir, "| M2 | 해소 | 고쳤다 |\n")
    expect(fails, "mi2 판형 아님 → 행 삭제(답 없음) → 판형 아님 → 잔존(근거 판형 아님 반복)", got, 2,
           "리뷰어 잔존 1 · 근거 판형 아님 0", "| M2 | 잔존(근거 판형 아님 반복) |")
    expect(fails, "mi2 뒤이어 판형대로 고쳐도 잔존 유지(동결)", fin(rdir, f"| M2 | 해소 | {C_LOC} — 고쳤다 |\n"), 2,
           "리뷰어 잔존 1", "해소 0")
    # n1 — 다른 플러그인 산출물 폴더(.dddjango-web/…)도 해소 근거가 아니다
    other: Path = repo / ".dddjango-web" / "20260930-home" / "design-spec.md"
    other.parent.mkdir(parents=True)
    other.write_text("a\nb\n", encoding="utf-8")
    rdir = _fresh_stamp(repo, folder, clear=True)
    expect(fails, "n1 web 산출물 폴더 파일(미추적) 머리 → 잔존(해소 아님)",
           fin(rdir, "| M2 | 해소 | .dddjango-web/20260930-home/design-spec.md:1 — 명세에 적었다 |\n"), 2, "리뷰어 잔존 1", "해소 0")
    shutil.rmtree(repo / ".dddjango-web")
    # n2 — 같은 시각 result.json 모양이 틀리면 실행 불능(트레이스백 아님)
    rdir = _fresh_stamp(repo, folder, clear=True)
    (rdir / "result.json").write_text(json.dumps({"stamp": rdir.name, "solved": {}, "states": ["M2"]}), encoding="utf-8")
    expect(fails, "n2 result.json states 가 dict 아님 → 실행 불능(exit 1)", fin(rdir, f"| M2 | 해소 | {C_LOC} — 고쳤다 |\n"), 1,
           "실행 불능", "result.json", "states·redo·solved")
    scope("M3")
    rdir = _fresh_stamp(repo, folder, clear=True)
    expect(fails, "M3 렌즈 완전성 — 두 렌즈 항목에 ddd 만 해소 → 판단 불가(discipline 답 없음)",
           fin(rdir, f"| M3 | 해소 | {C_LOC} — 고쳤다 |\n"), 2, "M_m=1(결정적 잔존 0 · 리뷰어 잔존 0 · 근거 판형 아님 0 · 판단 불가 1)")
    expect(fails, "M3 렌즈 완전성 — 같은 시각에 빠진 렌즈 답을 채워 재확정 → 해소(답 없음은 다시 판정)",
           fin(rdir, f"| M3 | 해소 | {C_LOC} — 고쳤다 |\n", f"| M3 | 해소 | {C_LOC} — 리터럴 한 곳 |\n"), 0, "M_m=0", "해소 1")
    # n4 — `잔존(일부)` 는 잔존(접두어)이라 판형 아님보다 앞서고 동결된다(리뷰 x9)
    rdir = _fresh_stamp(repo, folder, clear=True)
    expect(fails, "n4 ddd «잔존(일부)» + discipline 판형 아님 → 잔존(판단 불가·판형 아님 아님)",
           fin(rdir, f"| M3 | 잔존(일부) | {C_LOC} 에 남음 |\n", "| M3 | 해소 | 고쳤다 |\n"), 2,
           "리뷰어 잔존 1 · 근거 판형 아님 0 · 판단 불가 0")
    expect(fails, "n4 같은 시각 2차에 두 렌즈 모두 해소로 고쳐 써도 잔존 유지(동결)",
           fin(rdir, f"| M3 | 해소 | {C_LOC} — x |\n", f"| M3 | 해소 | {C_LOC} — x |\n"), 2, "리뷰어 잔존 1", "해소 0")
    # mi-A — 잔존 → (한 렌즈 행 삭제 = 답 없음) → 해소 로 빠져나가지 못한다
    rdir = _fresh_stamp(repo, folder, clear=True)
    fin(rdir, "| M3 | 잔존 | 남음 |\n", f"| M3 | 해소 | {C_LOC} — x |\n")
    expect(fails, "mi-A 1차 ddd 잔존 · discipline 해소 → 2차 ddd 행 삭제(답 없음) → 잔존 유지",
           fin(rdir, "", f"| M3 | 해소 | {C_LOC} — x |\n"), 2, "리뷰어 잔존 1 · 근거 판형 아님 0 · 판단 불가 0")
    expect(fails, "mi-A 3차 두 렌즈 해소 → 잔존 유지(답 없음 경유 이탈 없음)",
           fin(rdir, f"| M3 | 해소 | {C_LOC} — x |\n", f"| M3 | 해소 | {C_LOC} — x |\n"), 2, "리뷰어 잔존 1", "해소 0")


RES_HEAD: str = ("| M | 요지# | 요지(원 행 발췌) | 판정 | 불가 범주 | 막는 것(파일:행) | 처방 앵커 | 되돌리지 않는 이유 |\n"
                 "|---|---|---|---|---|---|---|---|\n")
RES_BODY: str = ("# 설계 명세 — demo\n\n## 4. 슬라이스 0 처방\n\n**M1 — 규칙 함수 이름 통일** policy.py 의 규칙 함수를 한 이름 규약으로.\n\n"
                 "**M2 — 컨트롤러 예외 매핑 정리** 예외를 매핑 표 한 곳에서 번역한다.\n\n")
T_LOC: str = "application/demo/test/test_policy.py:1"
X_LOC: str = "application/other/domain_layer/x.py:1"
RES_ROWS: "dict[str, str]" = {
    "M1": "| M1(+M4) | 1 | 규칙 이름 흩어짐 | 해소 | — | — | M1 — 규칙 함수 이름 통일 | — |\n",
    "M2a": "| M2 | 1 | 예외 매핑 흩어짐 | 해소 | — | — | M2 — 컨트롤러 예외 매핑 정리 | 뺀 요지의 처방은 인자 형태만 바꾼다 |\n",
    "M2b": f"| M2 | 2 | 긴 위치 인자 목록 | 불가 | 테스트 본문 동반 | {T_LOC} — 호출문 인자 형태가 바뀐다 | — | — |\n",
    "M3": f"| M3 | 1 | 판정이 어댑터에 | 불가 | 외부 관찰 동작 | {C_LOC} — 404 응답이 도메인 예외로 바뀐다 | — | — |\n",
}
RES_SCOPE: str = ("실행 · G0 승인 20260929-0300 · 모드 리팩토링 · audit 20260927-0250 · build_anchor {anchor}\n\n"
                  "- M1, M2, M3 · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(0300)\n")
RES_RECON: str = ("\n## ⓐ 재상정 20260929-0400 — STOP_FOR_USER_APPROVAL(부분·불가)\n\n"
                  "- M2 · 결정 = 요지 축소 · 남긴 요지 = #1 · 뺀 요지 = #2 → 별도 요청 · 남김 근거 = 해소 판정 표 · 출처 = 본인 직접(0400)\n"
                  "- M3 · 결정 = 별도 요청 · 사유 = 픽스처 · 출처 = 본인 직접(0400)\n")
RED_M2: str = "- M2 · 결정 = 요지 축소 · 남긴 요지 = #1 · 뺀 요지 = #2 → 별도 요청"
WHOLE_M2: str = "\n## ⓐ 재상정 20260929-0600 — G2 잔존\n\n- M2 · 결정 = 별도 요청 · 사유 = 잔존 · 출처 = 본인 직접(0600)\n"


def resolution_cases(fails: "list[str]", td: Path) -> None:
    """`resolution [--gate]` 판정 표 검사와 재상정 닫힌 어휘·요지 축소(F1 봉쇄) — 설계 R8-I1 v2 §8 · §11."""
    repo: Path = _project(td / "rsl")
    folder, anchor = _res_folder(repo, [row(1, V_B9, where=P_LOC), row(2, V_B9, where=C_LOC),
                                        row(3, V_B9, where=C_LOC), row(4, V_B9, where=P_LOC)],
                                 ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 채택 | | ", "M3 | ddd-01#3 | 채택 | | ",
                                  "M4 | ddd-01#4 | 병합 → M1 | | "])
    scope_path: Path = folder / "refactor-scope.md"
    spec_path: Path = folder / "design-spec.md"
    scope_rel: str = scope_path.relative_to(repo).as_posix()

    def spec(rows: "dict[str, str]", body: str = RES_BODY, heading: str = "## 5. 슬라이스 0 해소 판정") -> None:
        spec_path.write_text(body + f"{heading}\n\n" + RES_HEAD + "".join(rows.values()) + "\n## 6. 끝\n", encoding="utf-8")

    def scope(recon: str = "") -> None:
        scope_path.write_text(RES_SCOPE.format(anchor=anchor) + recon, encoding="utf-8")

    rs = lambda *extra: run(repo, "resolution", str(folder), *extra)  # noqa: E731
    scope()
    spec(RES_ROWS)
    expect(fails, "resolution 정상 표(해소·부분·불가 · `M1(+M4)` 병합 표기) → green · 해소 판정 1행 · 렌즈별 M(병합 원 행 포함)", rs(), 0,
           "해소 판정: 해소 1 · 부분 1 · 불가 1", "렌즈 ddd: M1 · M2 · M3", "red 0")
    spec({k: v for k, v in RES_ROWS.items() if k != "M3"})
    expect(fails, "resolution 범위 안 ⓐ 항목에 판정 행 없음 → red", rs(), 2, "M3 판정 없음")
    spec({**RES_ROWS, "M3": RES_ROWS["M3"].replace("외부 관찰 동작", "기존 보호 부족")})
    expect(fails, "resolution 불가 범주가 닫힌 목록 밖(«기존 보호 부족» 포함) → red", rs(), 2, "`기존 보호 부족`", "닫힌 목록")
    spec({**RES_ROWS, "M3": RES_ROWS["M3"].replace(C_LOC, "application/demo/driving_layer/api/thing/thing_controller.py:999")})
    expect(fails, "resolution 막는 것 파일:행 부재 → red", rs(), 2, "대상 프로젝트에 없다")
    spec({**RES_ROWS, "M1": RES_ROWS["M1"].replace("M1 — 규칙 함수 이름 통일", "명세에 없는 처방 문장")})
    expect(fails, "resolution 처방 앵커 원문이 표 밖 본문에 없음 → red", rs(), 2, "M1 #1 처방 앵커")
    spec({**RES_ROWS, "M2a": RES_ROWS["M2a"].replace("뺀 요지의 처방은 인자 형태만 바꾼다", "—")})
    expect(fails, "resolution 부분 항목 해소 행의 되돌리지 않는 이유 공란 → red", rs(), 2, "되돌리지 않는 이유")
    spec({**RES_ROWS, "M4": "| M4 | 1 | 병합 항목 | 해소 | — | — | M1 — 규칙 함수 이름 통일 | — |\n",
          "M1": RES_ROWS["M1"].replace("| 해소 |", "| 부분 |")})
    expect(fails, "resolution 병합 항목 행(범위 밖)·요지 판정 값 밖 → red", rs(), 2, "M4 범위 밖", "`부분` 이 `해소`·`불가` 밖")
    spec(RES_ROWS, heading="## 5. 해소 여부")
    expect(fails, "resolution 판정 표 제목 없음 → red(기대 형태 표시)", rs(), 2, "제목이 없다", "기대 형태")
    spec({})
    expect(fails, "m-6 제목은 있는데 표 행 0 → red «표에 행이 없다»", rs(), 2, "표에 행이 없다")
    # §11 M-2 · n-1 · n-2 · n-5 · m-2 · m-6(표 형식)
    spec({**RES_ROWS, "M3": RES_ROWS["M3"].replace(" — 404 응답이 도메인 예외로 바뀐다", "")})
    expect(fails, "M-2 불가 행 막는 것에 «— 한 구» 없음 → red", rs(), 2, "M3 #1 막는 것에 «— 무엇이 바뀌어야")
    spec({**RES_ROWS, "M3": RES_ROWS["M3"].replace("404 응답이 도메인 예외로 바뀐다", "응답: 404 → 500")})
    expect(fails, "M-2 한 구 안의 `:` 는 위치로 읽지 않는다 → green", rs(), 0, "red 0")
    spec({**RES_ROWS, "M1": RES_ROWS["M1"].replace("| M1 — 규칙 함수 이름 통일 |", "| M1 — 규칙 |")})
    expect(fails, "n-1 처방 앵커 정규화 8자 미만 → red", rs(), 2, "M1 #1 처방 앵커가 너무 짧다")
    spec({**RES_ROWS, "M1": RES_ROWS["M1"].replace("| 해소 | — |", "| 해소 | 외부 관찰 동작 |")})
    expect(fails, "n-2 해소 행에 불가 범주 → red", rs(), 2, "M1 #1 해소 행의 불가 범주·막는 것은")
    spec({**RES_ROWS, "M3": RES_ROWS["M3"].replace("| — | — |\n", "| M1 — 규칙 함수 이름 통일 | — |\n")})
    expect(fails, "n-2 불가 행에 처방 앵커 → red", rs(), 2, "M3 #1 불가 행의 처방 앵커")
    spec(RES_ROWS, heading="## 5. **슬라이스 0 해소 판정**")
    expect(fails, "n-5 제목 강조 표기 → 인식 green", rs(), 0, "red 0")
    spec({**RES_ROWS, "M2a": RES_ROWS["M2a"].replace("예외 매핑 흩어짐", "`str \\| None` 반환이 흩어짐")})
    expect(fails, "m-2 칸 속 `\\|` 이스케이프 → green", rs(), 0, "red 0")
    spec({**RES_ROWS, "M2a": RES_ROWS["M2a"].replace("예외 매핑 흩어짐", "str | None 반환")})
    expect(fails, "m-2 이스케이프 안 된 칸 속 `|` → 칸 밀림 red(fail-closed)", rs(), 2, "판정 `None 반환`")
    spec({**RES_ROWS, "M2b": RES_ROWS["M2b"].replace("| M2 | 2 |", "| M2 | 1 |")})
    expect(fails, "m-6 요지# 중복 → red", rs(), 2, "M2 요지# 가 1 이상 정수가 아니거나 항목 안에서 겹친다")
    spec_path.write_text(RES_BODY + "## 5. 슬라이스 0 해소 판정\n\n" + RES_HEAD + "".join(RES_ROWS.values())
                         + "\n## 7. 슬라이스 0 해소 판정\n\n" + RES_HEAD + "\n## 8. 끝\n", encoding="utf-8")
    expect(fails, "m-6 판정 표 제목 둘 → red", rs(), 2, "제목이 2개다")
    spec({**RES_ROWS, "M3b": "| M3 | 2 | 짧은 행 |\n"})
    expect(fails, "m-6 칸 부족 행 → red", rs(), 2, "칸 부족(3 < 8)")
    spec(RES_ROWS)
    expect(fails, "resolution --gate 부분·불가 항목에 재상정 결정 줄 없음 → red", rs("--gate"), 2,
           "M2 부분 항목에 재상정 결정 줄", "M3 불가 항목에 재상정 결정 줄이 없다")
    scope(RES_RECON)
    expect(fails, "resolution --gate 부분 = 요지 축소(번호 = 표) · 불가 = 별도 요청 → green", rs("--gate"), 0, "red 0 · gate")
    scope(RES_RECON.replace("\n\n- M2", "\n\n### 처분\n\n- M2"))
    expect(fails, "n-3 재상정 절 안 하위 제목은 절을 끊지 않는다 → green", rs("--gate"), 0, "red 0 · gate")
    scope(RES_RECON.replace("남긴 요지 = #1 · 뺀 요지 = #2", "남긴 요지 = #2 · 뺀 요지 = #1"))
    expect(fails, "resolution --gate 요지 축소 줄 번호 ≠ 표 → red", rs("--gate"), 2, "번호가 표와 다르다")
    scope(RES_RECON.replace("뺀 요지 = #2", "뺀 요지 = #3"))
    expect(fails, "m-6 뺀 번호만 어긋남 → red", rs("--gate"), 2, "줄 남긴 [1] · 뺀 [3]")
    scope(RES_RECON.replace("남긴 요지 = #1", "남긴 요지 = #3"))
    expect(fails, "m-6 남긴 번호만 어긋남 → red", rs("--gate"), 2, "줄 남긴 [3] · 뺀 [2]")
    scope(RES_RECON + "- M1 · 결정 = 요지 축소 · 남긴 요지 = #1 · 뺀 요지 = #2 → 플러그인 결함 · 남김 근거 = 사용자 선택 · "
                      "출처 = 본인 직접(0500)\n")
    expect(fails, "resolution --gate 표가 해소인데 요지 축소 줄 → red(표 갱신 G1′)", rs("--gate"), 2, "M1 표가 해소인데")
    scope(RES_RECON + RED_M2.replace("M2", "M4") + " · 남김 근거 = 해소 판정 표 · 출처 = 본인 직접(0400)\n")
    expect(fails, "m-6 판정 표 밖 항목의 요지 축소 줄 → red", rs("--gate"), 2, "M4 요지 축소 줄 항목이 판정 표에 없다")
    scope(RES_RECON.replace("- M3 · 결정 = 별도 요청 · 사유 = 픽스처", RED_M2.replace("M2", "M3") + " · 남김 근거 = 해소 판정 표"))
    expect(fails, "m-6 불가 항목에 요지 축소 줄 → red", rs("--gate"), 2, "M3 불가 항목에 요지 축소 줄이 걸렸다")
    # §11 M-1 — 전체 제외 줄이 표의 해소 요지를 덮지 못하게
    scope("\n## ⓐ 재상정 20260929-0400 — 오탐 STOP\n\n- M2 카탈로그 부분 · 결정 = 플러그인 결함 — 슬라이스 0 에서 빼고 진행"
          "(예외 매핑 정리는 유지) · 출처 = 본인 직접(0400)\n- M3 · 결정 = 별도 요청 · 사유 = 픽스처 · 출처 = 본인 직접(0400)\n")
    expect(fails, "M-1a R8-R 실물 모양 전체 제외 줄 + 표의 해소 요지 → red", rs("--gate"), 2,
           "M2 전체 제외 항목의 판정 표에 해소 요지가 남아 있다")
    scope(RES_RECON + WHOLE_M2)
    expect(fails, "M-1b 요지 축소 뒤 G2 전체 철회 줄 · 표 무수정 → red", rs("--gate"), 2,
           "M2 전체 제외 항목의 판정 표에 해소 요지가 남아 있다")
    whole_no: int = next(i for i, ln in enumerate(scope_path.read_text(encoding="utf-8").split("\n"), 1)
                         if ln.startswith("- M2 · 결정 = 별도 요청"))
    fixed: str = (f"| M2 | 1 | 예외 매핑 흩어짐 | 불가 | 재상정 제외 | {scope_rel}:{whole_no} — G2 잔존 철회로 항목 전체를 뺐다 "
                  "| — | — |\n")
    spec({**RES_ROWS, "M2a": fixed})
    expect(fails, "M-1c 표를 전체 불가(해소이던 요지 = 재상정 제외 · 막는 것 = 결정 줄)로 고침 → green", rs("--gate"), 0,
           "red 0 · gate")
    scope()
    spec({**RES_ROWS, "M3": RES_ROWS["M3"].replace("외부 관찰 동작", "재상정 제외")})
    expect(fails, "M-1d 전체 제외 줄 없이 범주 `재상정 제외` → red", rs(), 2, "M3 #1 범주 `재상정 제외` 인데")
    spec(RES_ROWS)
    for label, recon in (("요지 축소 → 전체 제외", RES_RECON + WHOLE_M2),
                         ("전체 제외 → 요지 축소", WHOLE_M2 + RES_RECON.replace("20260929-0400", "20260929-0700"))):
        scope(recon)
        _ts, adopted, removed, reductions, _lines = ra._scope(folder)
        expect(fails, f"m-6 같은 항목에 요지 축소 줄과 전체 제외 줄({label}) → 전체 제외가 이긴다",
               (0 if "M2" in removed and "M2" not in adopted - removed and "M2" in reductions else 9,
                f"removed={sorted(removed)} reductions={sorted(reductions)}"), 0)
    # 재상정 줄 어휘·정형(fail-closed)
    scope(RES_RECON.replace("- M3 · 결정 = 별도 요청", "- M3 · 결정 = 부분 정리"))
    expect(fails, "재상정 결정 칸 첫 낱말 어휘 밖 → resolution 실행 불능(fail-closed)", rs(), 1, "닫힌 어휘")
    expect(fails, "재상정 결정 칸 첫 낱말 어휘 밖 → residual 실행 불능(F1 fail-open 봉쇄)",
           run(repo, "residual", str(folder)), 1, "닫힌 어휘")
    scope(RES_RECON.replace(" · 남김 근거 = 해소 판정 표", ""))
    expect(fails, "요지 축소 줄 정형 불비(남김 근거 없음) → 실행 불능", rs(), 1, "정형이 아니다", "남김 근거")
    scope(RES_RECON.replace("→ 별도 요청", "→ 요지 축소"))
    expect(fails, "요지 축소 줄 뺀 요지 처분이 어휘 밖(요지) → 실행 불능", rs(), 1, "뺀 요지 처분")
    scope(RES_RECON.replace("뺀 요지 = #2", "뺀 요지 = #1·#2"))
    expect(fails, "m-6 요지 축소 줄 남긴·뺀 번호 겹침 → 실행 불능", rs(), 1, "번호 겹침")
    scope(RES_RECON.replace("- M2 · 결정 = 요지 축소", "- M2 · M3 · 결정 = 요지 축소"))
    expect(fails, "m-6 요지 축소 줄에 항목 둘 → 실행 불능", rs(), 1, "항목 하나")
    # residual — 요지 축소 항목은 빼지 않고 남긴 요지로 묶는다(F1 봉쇄) · 전체 제외 줄은 종전대로 뺀다(F7)
    scope(RES_RECON)
    thing: Path = repo / "application/demo/driving_layer/api/thing/thing_controller.py"
    thing.write_text(thing.read_text(encoding="utf-8") + "\n# 정리\n", encoding="utf-8")
    first = run(repo, "residual", str(folder))
    expect(fails, "residual 요지 축소 항목(M2)은 남고 전체 제외(M3)만 빠짐 · 요약 «요지 축소 1»", first, 0,
           "결정적 잔존 1", "리뷰어 확인 대상 1(ddd)", "요지 축소 1")
    stamp: str = first[1].split("--finalize ", 1)[1].split(")", 1)[0].split()[0] if "--finalize " in first[1] else ""
    bundle_path: Path = folder / "residual" / stamp / "review-ddd.md"
    bundle: str = bundle_path.read_text(encoding="utf-8") if bundle_path.is_file() else ""
    expect(fails, "residual 묶음에 요지 축소 줄(남긴·뺀 요지 원문 — 명세 표) · 머리 지시 1줄",
           (0 if "- 요지 축소(재상정 20260929-0400): 남긴 요지 #1 «예외 매핑 흩어짐» — 이 요지만 확인한다" in bundle
            and "뺀 요지 #2 «긴 위치 인자 목록» → 별도 요청" in bundle and "요지 축소 항목은 남긴 요지만 본다" in bundle
            and "### M3" not in bundle else 9, bundle), 0)
    (folder / "residual" / stamp / "result-ddd.md").write_text(
        f"| M | 판정 | 근거 |\n|---|---|---|\n| M2 | 해소 | {C_LOC} |\n", encoding="utf-8")
    fin = run(repo, "residual", str(folder), "--finalize", stamp)
    result: str = (folder / "residual" / stamp / "result.md").read_text(encoding="utf-8") if fin[0] != 1 else ""
    expect(fails, "residual --finalize 요지 축소 항목 해소 표시 · 요약 «요지 축소 1»", (fin[0], fin[1] + result), 2,
           "M_m=1", "요지 축소 1", "| M2 | 해소(요지 축소 — 남긴 요지) |")
    scope(RES_RECON.replace("남긴 요지 = #1", "남긴 요지 = #1·#7"))
    expect(fails, "residual 요지 축소 번호가 명세 표에 없음 → 실행 불능", run(repo, "residual", str(folder)), 1,
           "명세 해소 판정 표에 없다")


E2_SCOPE: str = ("실행 · G0 승인 20260929-0300 · 모드 리팩토링 · audit 20260927-0250 · build_anchor {anchor}\n\n"
                 "- {keys} · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(0300)\n")


def e2_cases(fails: "list[str]", td: Path) -> None:
    """E2 — `_scope` 가 G0 확정 판정(verdict-final.md)의 병합 항목을 ⓐ 키에서 뺀다(결정 줄 표기와 무관) ·
    확정 표가 없으면 실행 불능 · `--final` 재분류(병합 → 채택)는 따른다(설계 R8c §2.2 · §4.1 E2 · §7 B1·m5 · R8d §1.2)."""
    repo: Path = _project(td / "e2r")
    folder, anchor = _res_folder(repo, [row(1, V_B9, where=P_LOC), row(2, V_B9, where=C_LOC),
                                        row(3, V_B9, where=C_LOC), row(4, V_B9, where=P_LOC)],
                                 ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 채택 | | ", "M3 | ddd-01#3 | 채택 | | ",
                                  "M4 | ddd-01#4 | 병합 → M1 | | "], confirm=False)
    audit: Path = folder / "audit" / "20260927-0250"
    spec_path: Path = folder / "design-spec.md"

    def spec(rows: "dict[str, str]") -> None:
        spec_path.write_text(RES_BODY + "## 5. 슬라이스 0 해소 판정\n\n" + RES_HEAD + "".join(rows.values()) + "\n## 6. 끝\n",
                             encoding="utf-8")

    def scope(keys: str) -> None:
        (folder / "refactor-scope.md").write_text(E2_SCOPE.format(anchor=anchor, keys=keys), encoding="utf-8")

    rs = lambda: run(repo, "resolution", str(folder))  # noqa: E731
    spec(RES_ROWS)
    scope("M1(+M4), M2, M3")
    expect(fails, "E2-0 verdict-final.md 없음(check-verdict exit 0 판 없음) → 실행 불능(fail-closed)", rs(), 1,
           "verdict-final.md 이 없다", "check-verdict")
    expect(fails, "E2 준비 — check-verdict 가 병합→M 을 확정(exit 0 · verdict-final.md)", run(repo, "check-verdict", str(audit)), 0,
           "병합→M 1", "red 0")
    expect(fails, "E2-1 `M1(+M4)` 병합 표기 결정 줄 → 병합 항목은 ⓐ 판정 대상이 아니다 · red 0", rs(), 0, "red 0")
    scope("M1, M2, M3, M4")
    expect(fails, "E2-2 병합 키를 명시한 결정 줄 → red 0(표기와 무관)", rs(), 0, "red 0")
    scope("M1(+M4), M2, M3")
    spec({**RES_ROWS, "M4": "| M4 | 1 | 병합 항목 | 해소 | — | — | M1 — 규칙 함수 이름 통일 | — |\n"})
    expect(fails, "E2-3 역방향 — 병합 항목의 판정 표 행 → «M4 범위 밖» red", rs(), 2, "M4 범위 밖")
    scope("M1, M2(M3 는 사용자 판단 뒤 ⓐ)")
    spec({k: v for k, v in RES_ROWS.items() if k != "M3"})
    expect(fails, "E2-4 괄호 안에 적힌 진짜 ⓐ 키는 지우지 않는다 → «M3 판정 없음» red", rs(), 2, "M3 판정 없음")
    # residual — 병합 키가 독립 항목으로 묶이지 않는다(R8-R2 M9·M27·M28 모양)
    repo2: Path = _project(td / "e2s")
    folder2, anchor2 = _res_folder(repo2, [row(1, V_B9, where=P_LOC), row(2, V_B9, where=C_LOC), row(3, V_B9, where=P_LOC),
                                           row(5, V_B9, where="application/demo/domain_layer/policy.py:9")],
                                   ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 채택 | | ", "M3 | ddd-01#3 | 채택 | | ",
                                    "M5 | ddd-01#5 | 병합 → M2 | | "], confirm=False)
    prep = run(repo2, "check-verdict", str(folder2 / "audit" / "20260927-0250"))
    (folder2 / "refactor-scope.md").write_text(
        E2_SCOPE.format(anchor=anchor2, keys="C1, M1, M2(+M5), M3")
        + "\n## ⓐ 재상정 20260927-0400\n\n- M3 · 결정 = 별도 요청 · 사유 = 픽스처 · 출처 = 본인 직접(0400)\n", encoding="utf-8")
    thing: Path = repo2 / "application/demo/driving_layer/api/thing/thing_controller.py"
    thing.write_text(thing.read_text(encoding="utf-8") + "\n# 정리\n", encoding="utf-8")
    got = run(repo2, "residual", str(folder2))
    stamp: str = got[1].split("--finalize ", 1)[1].split()[0] if "--finalize " in got[1] else ""
    bundle_path: Path = folder2 / "residual" / stamp / "review-ddd.md"
    bundle: str = bundle_path.read_text(encoding="utf-8") if bundle_path.is_file() else ""
    expect(fails, "E2-5 residual `M2(+M5)` → 결정적 잔존 1(M1) · 묶음에 `### M5` 없음 · M2 아래 «(병합 M5)»",
           (got[0] if prep[0] == 0 and "### M5" not in bundle and "- 원 행 ddd-01#5 (병합 M5):" in bundle else 9,
            prep[1] + got[1] + bundle), 0, "결정적 잔존 1", "리뷰어 확인 대상 1(ddd)")
    # 재상정·--final 재분류 — verdict: M2 병합→M1 · M3 제외 · M4 병합→M3(사슬 red → --final 이 채택으로 기록)
    repo3: Path = _project(td / "e2f")
    folder3, anchor3 = _res_folder(repo3, [row(1, V_B9, where=C_LOC), row(2, V_B9, where=P_LOC), row(3, V_IMPL8, where=C_LOC),
                                           row(4, V_B9, where=P_LOC)],
                                   ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 병합 → M1 | | ",
                                    f"M3 | ddd-01#3 | 제외 | {EXCL_OK} | ", "M4 | ddd-01#4 | 병합 → M3 | | "], confirm=False)
    audit3: Path = folder3 / "audit" / "20260927-0250"
    first = run(repo3, "check-verdict", str(audit3))
    final = run(repo3, "check-verdict", str(audit3), "--final")
    log: str = (audit3 / "verdict-log.md").read_text(encoding="utf-8") if (audit3 / "verdict-log.md").is_file() else ""
    expect(fails, "E2 준비 — 사슬 병합 red → --final 이 M4 를 채택으로 재분류(verdict.md 는 원문 · 로그·확정 표에 남는다)",
           (final[0] if first[0] == 2 else 9, final[1] + log), 0, "| M4 | ddd-01#4 | 채택 |", "| M2 | ddd-01#2 | 병합→M |")
    (folder3 / "refactor-scope.md").write_text(
        E2_SCOPE.format(anchor=anchor3, keys="M1(+M2)")
        + "\n## ⓐ 재상정 20260927-0400\n\n- M1 · 결정 = 별도 요청 · 사유 = 픽스처 · 출처 = 본인 직접(0400)\n", encoding="utf-8")
    expect(fails, "E2-6 `M1(+M2)` 뒤 재상정 `M1 · 별도 요청` → 병합 항목 M2 도 함께 빠진다(결정적 잔존 0 · 확인 대상 0)",
           run(repo3, "residual", str(folder3)), 0, "M_m=0(결정적 잔존 0)", "리뷰어 확인 대상 0")
    shutil.rmtree(folder3 / "residual", ignore_errors=True)
    (folder3 / "refactor-scope.md").write_text(E2_SCOPE.format(anchor=anchor3, keys="M1, M4"), encoding="utf-8")
    expect(fails, "E2-7 --final 로 채택된 M4(verdict.md 는 병합) 는 ⓐ 에 남는다 → residual 결정적 잔존 2",
           run(repo3, "residual", str(folder3)), 2, "M_m=2(결정적 잔존 2)")
    (folder3 / "design-spec.md").write_text(
        RES_BODY + "## 5. 슬라이스 0 해소 판정\n\n" + RES_HEAD
        + "| M1 | 1 | 규칙 이름 흩어짐 | 해소 | — | — | M1 — 규칙 함수 이름 통일 | — |\n\n## 6. 끝\n", encoding="utf-8")
    expect(fails, "E2-7 --final 로 채택된 M4 → resolution «M4 판정 없음» red(조용히 빠지지 않는다)",
           run(repo3, "resolution", str(folder3)), 2, "M4 판정 없음")
    # mi1 — 차감 = 확정 표(verdict-final.md) 병합 ∩ (대상 M 이 ⓐ 키 | 대상 C 가 ⓐ 줄) · 코드 무변(M1 = 바뀐 파일만)
    def g0(name: str, rows: "list[str]", verdicts: "list[str]", keys: str) -> "tuple[Path, Path, tuple[int, str]]":
        rp: Path = _project(td / name)
        fd, an = _res_folder(rp, rows, verdicts, confirm=False)
        cv = run(rp, "check-verdict", str(fd / "audit" / "20260927-0250"))
        (fd / "refactor-scope.md").write_text(E2_SCOPE.format(anchor=an, keys=keys), encoding="utf-8")
        tc: Path = rp / "application/demo/driving_layer/api/thing/thing_controller.py"
        tc.write_text(tc.read_text(encoding="utf-8") + "\n# 정리\n", encoding="utf-8")
        return rp, fd, cv

    two: "list[str]" = [row(1, V_B9, where=C_LOC), row(2, V_B9, where=P_LOC)]
    rp, fd, cv = g0("x3", two, ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 병합 → M1 | | "], "M1, M2")
    Audit.verdict(fd / "audit" / "20260927-0250", ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 채택 | | "])
    got = run(rp, "residual", str(fd))
    x3_stamp: str = got[1].split("--finalize ", 1)[1].split()[0] if "--finalize " in got[1] else ""
    x3_bundle: Path = fd / "residual" / x3_stamp / "review-ddd.md"
    x3_text: str = x3_bundle.read_text(encoding="utf-8") if x3_stamp and x3_bundle.is_file() else ""
    expect(fails, "x3 확정 뒤 verdict.md 만 채택으로 고침(재실행 없음) → 확정 표대로 M2 는 M1 에 병합(묶음 «(병합 M2)» · 바닥 0)",
           (got[0] if cv[0] == 0 and "(병합 M2)" in x3_text and "### M2" not in x3_text else 9, cv[1] + got[1] + x3_text),
           0, "결정적 잔존 0", "리뷰어 확인 대상 1(ddd)")
    rp, fd, cv = g0("x4", two, ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 병합 → M1 | | "], "M2")
    got = run(rp, "residual", str(fd))
    expect(fails, "mi1 x4 고아 병합 M — 결정 줄에 M2 만(대상 M1 은 ⓐ 아님) → M2 를 빼지 않는다(M_m=1)",
           (got[0] if cv[0] == 0 else 9, cv[1] + got[1]), 2, "M_m=1(결정적 잔존 1)")
    four: "list[str]" = [row(1, V_B9, where=C_LOC), row(2, V_B9, where=P_LOC), row(3, V_B9, where=P_LOC),
                         row(4, V_B9, where=P_LOC, same_c="C1")]
    four_v: "list[str]" = ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 채택 | | ", "M3 | ddd-01#3 | 채택 | | ",
                           "M4 | ddd-01#4 | 병합 → C1 | 리뷰어 표시 | "]
    rp, fd, cv = g0("x5", four, four_v, "M1, M4")
    got = run(rp, "residual", str(fd))
    expect(fails, "mi1 x5 고아 병합 C — 결정 줄 `M1, M4`(C1 은 ⓐ 아님) → M4 를 빼지 않는다(결정적 잔존 1)",
           (got[0] if cv[0] == 0 else 9, cv[1] + got[1]), 0, "결정적 잔존 1", "리뷰어 확인 대상 1(ddd)")
    (fd / "refactor-scope.md").write_text(
        (fd / "refactor-scope.md").read_text(encoding="utf-8").replace("- M1, M4 ·", "- C1, M1, M4 ·"), encoding="utf-8")
    expect(fails, "mi1 x5 짝 — 결정 줄에 C1 이 있으면 병합→C1 인 M4 는 C1 을 따른다(결정적 잔존 0)",
           run(rp, "residual", str(fd)), 0, "결정적 잔존 0", "리뷰어 확인 대상 1(ddd)")
    (fd / "refactor-scope.md").write_text((fd / "refactor-scope.md").read_text(encoding="utf-8").replace(
        "- C1, M1, M4 ·", "- M1, M4(C1 은 ⓑ 로 미룸) ·"), encoding="utf-8")
    expect(fails, "mi-B 괄호 안 C1(ⓐ 아님) → 병합→C1 인 M4 를 빼지 않는다(결정적 잔존 1 · HEAD 와 같음)",
           run(rp, "residual", str(fd)), 0, "결정적 잔존 1", "리뷰어 확인 대상 1(ddd)")


def final_cases(fails: "list[str]", td: Path) -> None:
    """R8d ① — `--final` 재분류(새 번호 · 번호 중복 · 병합→채택 · 원 행 두 번 · 통과 아닌 원 행)와 별도 요청 재분류를
    resolution·residual 이 확정 표(verdict-final.md)로 따른다 · 확정 표 없는 옛 폴더는 실행 불능(진단 R8d-1 §2)."""
    bad: str = cite(DDD, "3.2", "이 문장은 규범에 없다 진단용")
    pf: str = P_LOC.split(":")[0]

    def lane(name: str, rows: "list[str]", verdicts: "list[str]", keys: str, spec_m: "list[str]",
             final: bool = True) -> "tuple[Path, Path, str]":
        rp: Path = _project(td / name)
        fd, an = _res_folder(rp, rows, verdicts, confirm=False)
        audit: Path = fd / "audit" / "20260927-0250"
        first = run(rp, "check-verdict", str(audit))
        last = run(rp, "check-verdict", str(audit), "--final") if final else first
        (fd / "refactor-scope.md").write_text(E2_SCOPE.format(anchor=an, keys=keys), encoding="utf-8")
        (fd / "design-spec.md").write_text(RES_BODY + "## 5. 슬라이스 0 해소 판정\n\n" + RES_HEAD + "".join(
            f"| {m} | 1 | 규칙 이름 흩어짐 | 해소 | — | — | M1 — 규칙 함수 이름 통일 | — |\n" for m in spec_m)
            + "\n## 6. 끝\n", encoding="utf-8")
        tc: Path = rp / "application/demo/driving_layer/api/thing/thing_controller.py"
        tc.write_text(tc.read_text(encoding="utf-8") + "\n# 정리\n", encoding="utf-8")
        return rp, fd, f"{first[0]}/{last[0]}"

    def bundle(fd: Path, out: str) -> str:
        st: str = out.split("--finalize ", 1)[1].split()[0] if "--finalize " in out else ""
        b: Path = fd / "residual" / st / "review-ddd.md"
        return b.read_text(encoding="utf-8") if st and b.is_file() else ""

    # F1 새 번호(판정 없는 통과 행 → M2) 를 ⓐ — HEAD: resolution·residual «M2 이 verdict.md 에 없다» exit 1
    rp, fd, cv = lane("f1", [row(1, V_B9, where=P_LOC), row(2, V_B9, where=C_LOC)], ["M1 | ddd-01#1 | 채택 | | "],
                      "M1, M2", ["M1", "M2"])
    expect(fails, "F1 --final 새 번호 M2 를 ⓐ → resolution 정상(red 0 · 렌즈 ddd: M1 · M2)",
           run(rp, "resolution", str(fd)), 0, "red 0", "렌즈 ddd: M1 · M2")
    got = run(rp, "residual", str(fd))
    expect(fails, "F1 residual 정상 — M1(P 무변) 결정적 잔존 · M2 리뷰어", (got[0] if cv == "2/0" else 9, got[1]), 0,
           "결정적 잔존 1", "리뷰어 확인 대상 1(ddd)")
    # F2 번호 중복(M1 두 행 → 뒤 행 새 번호 M2) · M1 ⓐ · M2 ⓑ — HEAD: 뒤 행이 M1 을 덮어 M_m=0(fail-open)
    rp, fd, cv = lane("f2", [row(1, V_B9, where=P_LOC), row(2, V_B9, where=C_LOC)],
                      ["M1 | ddd-01#1 | 채택 | | ", "M1 | ddd-01#2 | 채택 | | "], "M1", ["M1"])
    got = run(rp, "residual", str(fd))
    expect(fails, "F2 --final 번호 중복 → M1 = 로그와 같은 앞 행(P 무변) → 결정적 잔존 1 · exit 2",
           (got[0] if cv == "2/0" else 9, got[1]), 2, "M_m=1(결정적 잔존 1)")
    # F3 렌즈 — M1 두 행(ddd·discipline) → discipline 행이 M2 로 · resolution 렌즈 ddd: M1
    rp3: Path = _project(td / "f3")
    fd3, an3 = _res_folder(rp3, [row(1, V_B9, where=P_LOC)], ["M1 | ddd-01#1 | 채택 | | ", "M1 | discipline-01#1 | 채택 | | "],
                           disc=[row(1, V_B9, where=C_LOC)], confirm=False)
    a3: Path = fd3 / "audit" / "20260927-0250"
    run(rp3, "check-verdict", str(a3))
    fin3 = run(rp3, "check-verdict", str(a3), "--final")
    (fd3 / "refactor-scope.md").write_text(E2_SCOPE.format(anchor=an3, keys="M1"), encoding="utf-8")
    (fd3 / "design-spec.md").write_text(RES_BODY + "## 5. 슬라이스 0 해소 판정\n\n" + RES_HEAD
                                         + "| M1 | 1 | 규칙 이름 흩어짐 | 해소 | — | — | M1 — 규칙 함수 이름 통일 | — |\n"
                                         + "\n## 6. 끝\n", encoding="utf-8")
    got = run(rp3, "resolution", str(fd3))
    expect(fails, "F3 번호 중복의 렌즈 — resolution 렌즈 ddd: M1(discipline 아님)",
           (got[0] if fin3[0] == 0 and "렌즈 discipline" not in got[1] else 9, fin3[1] + got[1]), 0, "렌즈 ddd: M1")
    # F4 병합→채택 재분류(대상 M3 제외 red → 채택 · M4 병합 → M3 는 --final 로 채택) · M3 ⓐ · M4 ⓑ
    rp, fd, cv = lane("f4", [row(3, V_B9, where=P_LOC), row(4, V_B9, where=C_LOC)],
                      ["M3 | ddd-01#3 | 제외 | 근거 형식 아님 | ", "M4 | ddd-01#4 | 병합 → M3 | | "], "M3", ["M3"])
    got = run(rp, "residual", str(fd))
    expect(fails, "F4 --final 병합→채택 재분류 → M3 묶음에 M4 행 없음 · M3(P 무변) 결정적 잔존 1",
           (got[0] if cv == "2/0" else 9, got[1]), 2, "M_m=1(결정적 잔존 1)")
    # F5 원 행 두 번 판정(M2 가 #1·#2) → --final 이 M2 에서 #1 을 뺀다 · M1(C)·M2(P) ⓐ
    rp, fd, cv = lane("f5", [row(1, V_B9, where=C_LOC), row(2, V_B9, where=P_LOC)],
                      ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#1 · ddd-01#2 | 채택 | | "], "M1, M2", ["M1", "M2"])
    got = run(rp, "residual", str(fd))
    b5: str = bundle(fd, got[1])
    expect(fails, "F5 --final 원 행 두 번 → M2 는 #2(P 무변)만 · 결정적 잔존 1 · M1 리뷰어",
           (got[0] if cv == "2/0" and "### M2" not in b5 else 9, got[1] + b5), 0, "결정적 잔존 1", "리뷰어 확인 대상 1(ddd)")
    # F6 통과 아닌 원 행(인용 불일치 #2) → --final 이 뺀다 · M1 ⓐ
    rp, fd, cv = lane("f6", [row(1, V_B9, where=P_LOC), row(2, bad, where=C_LOC)],
                      ["M1 | ddd-01#1 · ddd-01#2 | 채택 | | "], "M1", ["M1"])
    got = run(rp, "residual", str(fd))
    expect(fails, "F6 --final 통과 아닌 원 행 제거 → M1 묶음에 #2 없음 · 결정적 잔존 1",
           (got[0] if cv == "2/0" else 9, got[1]), 2, "M_m=1(결정적 잔존 1)")
    # F7 별도 요청 → 채택 재분류(--final 없이 exit 0) — 확정 표에 채택으로 남는다
    rp, fd, cv = lane("f7", [row(1, V_B9, where=M_LOC)], ["M1 | ddd-01#1 | 별도 요청 | 모델 필드 | "], "M1", ["M1"],
                      final=False)
    vf: Path = fd / "audit" / "20260927-0250" / "verdict-final.md"
    expect(fails, "F7 별도 요청 → 채택 재분류(exit 0) → verdict-final.md 에 채택 · verdict.md 원문 보존",
           (int(cv.split("/")[0]), (vf.read_text(encoding="utf-8") if vf.is_file() else "")
            + (fd / "audit" / "20260927-0250" / "verdict.md").read_text(encoding="utf-8")), 0,
           "| M1 | ddd-01#1 | 채택 |", "| M1 | ddd-01#1 | 별도 요청 |")
    # F8 red(exit 2) 재실행은 앞 확정 표를 지우거나 바꾸지 않는다
    before: str = vf.read_text(encoding="utf-8") if vf.is_file() else ""
    Audit.verdict(fd / "audit" / "20260927-0250", ["M1 | ddd-01#1 | 병합 | 대상 없음 | "])
    red = run(rp, "check-verdict", str(fd / "audit" / "20260927-0250"))
    expect(fails, "F8 exit 2 재실행 → verdict-final.md 그대로(마지막 exit 0 판 = G0 목록 출처)",
           (red[0] if vf.is_file() and vf.read_text(encoding="utf-8") == before else 9, red[1]), 2, "판정 범주 밖")
    # F9 옛 폴더(수리 전 도구 산출 — verdict-log exit 0 판만 있고 verdict-final.md 없음) → 실행 불능 · 안내 → check-verdict 재실행으로 회복
    rp, fd, cv = lane("f9", [row(1, V_B9, where=P_LOC)], ["M1 | ddd-01#1 | 채택 | | "], "M1", ["M1"], final=False)
    (fd / "audit" / "20260927-0250" / "verdict-final.md").unlink(missing_ok=True)
    expect(fails, "F9 옛 폴더(verdict-final.md 없음) → residual 실행 불능 · check-verdict 재실행 안내",
           run(rp, "residual", str(fd)), 1, "verdict-final.md 이 없다", "check-verdict")
    _git(rp, "checkout", "--", "application/demo/driving_layer/api/thing/thing_controller.py")   # 안내의 조건 — BC 무변
    run(rp, "check-verdict", str(fd / "audit" / "20260927-0250"))
    expect(fails, "F9 짝 — BC 무변에서 check-verdict 재실행(exit 0) 뒤 residual 정상", run(rp, "residual", str(fd)), 2,
           "M_m=1(결정적 잔존 1)")
    # F9′ 옛 폴더 + Phase 2 코드 변경(원 행 파일 축소) → 안내가 재실행하지 말고 멈추라고 한다(재실행은 원 행을 다시 검사해 확정 표를 바꾼다)
    rp, fd, cv = lane("f9b", [row(1, V_B9, where=P_LOC), row(2, V_B9, where=C_LOC), row(3, V_B9, where=C_LOC)],
                      ["M1 | ddd-01#1 · ddd-01#2 | 채택 | | "], "M1, M2", ["M1", "M2"])
    (fd / "audit" / "20260927-0250" / "verdict-final.md").unlink(missing_ok=True)
    (rp / P_LOC.split(":")[0]).write_text("def rule(x: int, i: int) -> int:\n    return x + i\n", encoding="utf-8")
    expect(fails, "F9′ 옛 폴더 + BC 변경 → residual 실행 불능 · 안내 «바뀌었으면 다시 돌리지 않고 멈춘다»",
           run(rp, "residual", str(fd)), 1, "verdict-final.md 이 없다", "바뀌었으면 다시 돌리지 않고 멈춘다")
    # F10 고아 병합 — 대상 M3 의 원 행이 통과 행이 아니어서 --final 이 M3 를 빼면 M4(병합 → M3)는 채택으로 확정
    rp, fd, cv = lane("f10", [row(1, V_B9, where=C_LOC), row(3, bad, where=C_LOC), row(4, V_B9, where=P_LOC)],
                      ["M1 | ddd-01#1 | 채택 | | ", "M3 | ddd-01#3 | 채택 | | ", "M4 | ddd-01#4 | 병합 → M3 | | "], "M1", ["M1"])
    a10: Path = fd / "audit" / "20260927-0250"
    vf10: str = (a10 / "verdict-final.md").read_text(encoding="utf-8") if (a10 / "verdict-final.md").is_file() else ""
    log10: str = (a10 / "verdict-log.md").read_text(encoding="utf-8") if (a10 / "verdict-log.md").is_file() else ""
    expect(fails, "F10 --final 이 병합 대상 M3 을 빼면 M4 는 채택(확정 표·로그 · 병합 → M3 없음)",
           (0 if cv == "2/0" and "| M4 | ddd-01#4 | 채택 |" in vf10 and "병합 → M3" not in vf10 else 9, vf10 + log10), 0,
           "| M4 | ddd-01#4 | 채택 |", "재분류: M4 병합 대상 M3 이 확정 기록의 채택 항목이 아니다 → 채택")
    # F10b 고아 병합 교정은 대상 M 만 — 정당한 병합 → C1 은 --final 뒤에도 확정 표에 그대로
    rp, fd, cv = lane("f10b", [row(1, V_B9, where=C_LOC), row(2, V_B9, where=P_LOC, same_c="C1"), row(3, bad, where=C_LOC)],
                      ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 병합 → C1 | 리뷰어 표시 | ", "M3 | ddd-01#3 | 채택 | | "], "M1", ["M1"])
    a10b: Path = fd / "audit" / "20260927-0250"
    vf10b: str = (a10b / "verdict-final.md").read_text(encoding="utf-8") if (a10b / "verdict-final.md").is_file() else ""
    expect(fails, "F10b --final 고아 병합 교정은 대상 M 만 — 병합 → C1 은 확정 표에 그대로",
           (0 if cv == "2/0" else 9, vf10b), 0, "| M2 | ddd-01#2 | 병합 → C1 |")
    # F12 번호 중복으로 병합 대상 M1 이 제외(비채택)로 남으면 M3(병합 → M1)은 채택 — 제외 항목에 붙지 않는다
    rp, fd, cv = lane("f12", [row(1, V_IMPL8, where=C_LOC), row(2, V_B9, where=P_LOC), row(3, V_B9, where=C_LOC)],
                      [f"M1 | ddd-01#1 | 제외 | {EXCL_OK} | ", "M1 | ddd-01#2 | 채택 | | ", "M3 | ddd-01#3 | 병합 → M1 | | "],
                      "M3", ["M3"])
    a12: Path = fd / "audit" / "20260927-0250"
    vf12: str = (a12 / "verdict-final.md").read_text(encoding="utf-8") if (a12 / "verdict-final.md").is_file() else ""
    log12: str = (a12 / "verdict-log.md").read_text(encoding="utf-8") if (a12 / "verdict-log.md").is_file() else ""
    expect(fails, "F12 번호 중복으로 병합 대상 M1 이 제외로 남으면 M3 은 채택(확정 표 · 병합 → M1 없음 · M1 은 제외 그대로)",
           (0 if cv == "2/0" and "| M3 | ddd-01#3 | 채택 |" in vf12 and "병합 → M1" not in vf12 else 9, vf12 + log12), 0,
           "| M1 | ddd-01#1 | 제외 |", "재분류: M3 병합 대상 M1 이 확정 기록의 채택 항목이 아니다 → 채택")
    # F11 확정 표 칸 이스케이프 — 근거 칸 `\|` · 파일:행 칸 ⓓ 표식 → exit 0 확정 뒤 residual 이 --candidates 없이 실행 불능(ⓓ 가드 유지)
    rp, fd, cv = lane("f11", [row(1, V_B9, where=P_LOC)], [f"M1 | ddd-01#1 | 채택 | 근거 a \\| b | {P_LOC} [ⓓ#644] "], "M1",
                      ["M1"], final=False)
    pol: Path = rp / P_LOC.split(":")[0]
    pol.write_text(pol.read_text(encoding="utf-8") + "\n# 정리\n", encoding="utf-8")
    expect(fails, "F11 확정 표 `\\|` 칸 이스케이프 → ⓓ 표식이 파일:행 칸에 남아 residual 이 --candidates 요구(실행 불능)",
           (lambda g: (g[0] if cv.startswith("0") else 9, cv + g[1]))(run(rp, "residual", str(fd))), 1, "ⓓ 겹침 항목")


STD_FILE: str = ".dddjango/standing-answer.md"
STD_BODY: str = "# 상시 답\n\n«동작 변경이나 테스트 수정이 필요해 이번에 못 끝내는 항목은 별도 요청으로».\n"
STD_SPEC: str = ("# 설계 명세 — demo\n\n**M2 — 예외 매핑 정리 처방** 매핑 표 한 곳.\n\n**M4 — 규칙 이름 통일 처방** 한 규약.\n\n"
                 "**M6 — 판정 소유 이동 처방** 도메인으로.\n\n## 5. 슬라이스 0 해소 판정\n\n" + RES_HEAD
                 + f"| M1 | 1 | 판정 흩어짐 | 불가 | 외부 관찰 동작 | {C_LOC} — 상태 코드가 바뀐다 | — | — |\n"
                 + "| M2 | 1 | 예외 매핑 | 해소 | — | — | M2 — 예외 매핑 정리 처방 | 뺀 요지 처방은 인자만 바꾼다 |\n"
                 + f"| M2 | 2 | 인자 목록 | 불가 | 테스트 본문 동반 | {T_LOC} — 호출문이 바뀐다 | — | — |\n"
                 + f"| M3 | 1 | 공용 기저 | 불가 | 편집 범위 밖 | {X_LOC} — BC 밖 파일을 고친다 | — | — |\n"
                 + "| M4 | 1 | 이름 | 해소 | — | — | M4 — 규칙 이름 통일 처방 | 뺀 요지 처방은 호출 자리만 바꾼다 |\n"
                 + f"| M4 | 2 | 호출문 | 불가 | 테스트 본문 동반 | {T_LOC} — 호출문이 바뀐다 | — | — |\n"
                 + f"| M4 | 3 | 공용 | 불가 | 편집 범위 밖 | {X_LOC} — BC 밖 파일을 고친다 | — | — |\n"
                 + f"| M5 | 1 | 상태 코드 | 불가 | 외부 관찰 동작 | {C_LOC} — 응답이 바뀐다 | — | — |\n"
                 + f"| M5 | 2 | 규칙 충돌 | 불가 | 반대 방향 규칙 | {P_LOC} — 조회 조율 자리가 바뀐다 | — | — |\n"
                 + "| M6 | 1 | 판정 소유 | 해소 | — | — | M6 — 판정 소유 이동 처방 | — |\n\n## 6. 끝\n")
STD_G0: str = ("실행 · G0 승인 20260929-0300 · 모드 리팩토링 · audit 20260927-0250 · build_anchor {anchor}\n\n"
               "- M1, M2, M3, M4, M5, M6 · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(0300)\n")
STD_SECTION: str = ("\n## ⓐ 재상정 20260929-0500 — G1 재상정 · 상시 답 적용 2건\n\n"
                    "- M1 · 결정 = 별도 요청 · 사유 = 불가(외부 관찰 동작 — 해소 판정 표) · 출처 = 상시 답 {src}\n"
                    "- M2 · 결정 = 요지 축소 · 남긴 요지 = #1 · 뺀 요지 = #2 → 별도 요청 · 남김 근거 = 해소 판정 표 · 출처 = 상시 답 {src}\n"
                    "- M3 · 결정 = ⓑ · 사유 = 픽스처 · 출처 = 본인 직접(0500)\n"
                    "- M4 · 결정 = 요지 축소 · 남긴 요지 = #1 · 뺀 요지 = #2·#3 → 별도 요청 · 남김 근거 = 해소 판정 표 · "
                    "출처 = 본인 직접(0500)\n"
                    "- M5 · 결정 = 별도 요청 · 사유 = 픽스처 · 출처 = 본인 직접(0500)\n")


def standing_cases(fails: "list[str]", td: Path) -> None:
    """㉯ 상시 답 — 인식 · 적용 예정/묻는 항목 · `--gate` 네 검사(커밋·행 · 처분 모양 · 표 조건 · 자리) — 설계 §12-4 S1~S15."""
    repo: Path = _project(td / "std")
    folder, anchor = _res_folder(repo, [row(k, V_B9, where=w) for k, w in
                                        enumerate((C_LOC, C_LOC, P_LOC, P_LOC, C_LOC, P_LOC, C_LOC), 1)],
                                 [f"M{k} | ddd-01#{k} | 채택 | | " for k in range(1, 7)] + ["M7 | ddd-01#7 | 병합 → M1 | | "])
    (folder / "design-spec.md").write_text(STD_SPEC, encoding="utf-8")
    scope_path: Path = folder / "refactor-scope.md"
    std: Path = repo / STD_FILE
    rs = lambda *extra: run(repo, "resolution", str(folder), *extra)  # noqa: E731

    def commit(body: "str | None", msg: str) -> str:
        if body is None:
            _git(repo, "rm", "-q", STD_FILE)
        else:
            std.write_text(body, encoding="utf-8")
            _git(repo, "add", STD_FILE)
        _git(repo, "commit", "-qm", msg)
        return _git(repo, "rev-parse", "HEAD").strip()[:12]

    def scope(extra: str = "", src: str = "") -> None:
        scope_path.write_text(STD_G0.format(anchor=anchor) + extra.replace("{src}", src), encoding="utf-8")

    scope()
    got = rs()
    expect(fails, "S1 파일 없음 → 출력에 상시 답 행 없음(I1 그대로)", (got[0] if "상시 답" not in got[1] else 9, got[1]), 0,
           "해소 판정: 해소 1 · 부분 2 · 불가 3")
    std.parent.mkdir(parents=True, exist_ok=True)
    std.write_text(STD_BODY, encoding="utf-8")
    expect(fails, "S3 미추적 → 인식 안 함 · 기대 문장 · exit 0", rs(), 0, "상시 답: 인식 안 함(미추적) — 적용 0",
           "기대 문장: 동작 변경이나 테스트 수정이")
    _git(repo, "add", STD_FILE)
    expect(fails, "S3 커밋되지 않은 수정(스테이지만) → 인식 안 함", rs(), 0, "인식 안 함(커밋되지 않은 수정)")
    commit(STD_BODY + "- 동작 변경이나 테스트 수정이 필요해 이번에 못 끝내는 항목은 별도 요청으로\n", "two")
    expect(fails, "S3 인식 줄 2개 → 인식 안 함", rs(), 0, "인식 안 함(인식 줄 2개)")
    commit("동작 변경·테스트 수정이 필요해 이번에 못 끝내는 항목은 별도 요청으로\n", "draft")
    expect(fails, "S3′ 리뷰 초안 문장(«동작 변경·테스트 수정이») → 인식 안 함(문장 없음)", rs(), 0, "인식 안 함(문장 없음)")
    commit("메모\n- 동작 변경이나 테스트 수정이 필요해 이번에 못 끝내는 항목은 별도 요청으로\n", "list")
    expect(fails, "S3′ 목록 머리 줄 → 인식(2행)", rs(), 0, "상시 답 출처: 상시 답 .dddjango/standing-answer.md:2@")
    c: str = commit(STD_BODY, "standing")
    src: str = f"{STD_FILE}:3@{c}"
    got = rs()
    order_ok: bool = got[1].find("요약:") < got[1].find("  상시 답:")
    expect(fails, "S2 «…» 감쌈 + 끝 마침표 인식 · 적용 예정 M1·M2(S14·S15: M3·M4·M5 는 묻는다) · 출처 값 · `요약:` 뒤",
           (got[0] if order_ok else 9, got[1]), 0, "상시 답: 적용 예정 M1 · M2 · 묻는 재상정 M3 · M4 · M5",
           f"상시 답 출처: 상시 답 {src}", "red 0 · 상시 답 2")
    std.write_text(STD_BODY + "추가\n", encoding="utf-8")
    expect(fails, "S3 커밋된 파일의 미커밋 수정 → 인식 안 함", rs(), 0, "인식 안 함(커밋되지 않은 수정)")
    _git(repo, "checkout", "--", STD_FILE)
    scope(STD_SECTION, src)
    expect(fails, "S4 --gate 정상(상시 답 2 · 사용자 답 3) → green", rs("--gate"), 0, "red 0 · gate")
    expect(fails, "implB 결정 줄을 적은 항목은 적용 예정·묻는 목록에서 빠진다(G1′ 재실행)", rs(), 0,
           "상시 답: 적용 예정 없음 · 묻는 재상정 없음")
    scope(STD_SECTION.replace("- M1 · 결정 = 별도 요청", "- M1(+M7) · 결정 = 별도 요청"), src)
    expect(fails, "MA-1 병합 표기 머리 `M1(+M7)` 상시 답 줄 → 괄호 안 키는 줄의 키가 아니다 · green", rs("--gate"), 0,
           "red 0 · gate")
    scope(STD_SECTION, src)
    m1_no: int = next(i for i, ln in enumerate(scope_path.read_text(encoding="utf-8").split("\n"), 1)
                      if ln.startswith("- M1 · 결정 = 별도 요청"))
    spec_path: Path = folder / "design-spec.md"
    spec_path.write_text(STD_SPEC.replace(
        f"| M1 | 1 | 판정 흩어짐 | 불가 | 외부 관찰 동작 | {C_LOC} — 상태 코드가 바뀐다 | — | — |",
        f"| M1 | 1 | 판정 흩어짐 | 불가 | 재상정 제외 | refactor-scope.md:{m1_no} — override 로 풀리게 됐으나 결정대로 뺐다 | — | — |"),
        encoding="utf-8")
    expect(fails, "MA-2·mi-4 상시 답으로 뺀 항목을 `재상정 제외`(막는 것 = 맨 `refactor-scope.md:<행>`)로 고침 → green",
           rs("--gate"), 0, "red 0 · gate")
    spec_path.write_text(STD_SPEC, encoding="utf-8")
    scope(STD_SECTION.replace("- M2 · 결정 = 요지 축소 · 남긴 요지 = #1 · 뺀 요지 = #2 → 별도 요청 · 남김 근거 = 해소 판정 표",
                              "- M2 · 결정 = 별도 요청 · 사유 = 불가"), src)
    expect(fails, "implB 부분 항목에 전체 제외 모양 상시 답 줄 → red ②(제자리 교정 대상)", rs("--gate"), 2,
           "M2 상시 답 줄", "② 처분이")
    scope_path.write_text(STD_G0.format(anchor=anchor) + "- M6 · 결정 = ⓐ · 사유 = x · 출처 = `상시 답 " + src + "`\n"
                          + STD_SECTION.replace("{src}", src), encoding="utf-8")
    expect(fails, "mi-3 백틱으로 감싼 상시 답 출처(G0 줄)도 탐지 → red ④", rs("--gate"), 2, "M6 상시 답 줄", "④ 머리에")
    scope(STD_SECTION.replace("· 출처 = 상시 답 {src}\n- M2", "· 출처 = **상시 답** {src}\n- M2"), src)
    expect(fails, "mi-3 강조 표기 상시 답 출처 → 탐지 · red ①(정형 아님)", rs("--gate"), 2, "M1 상시 답 줄", "① 출처 값이")
    scope_path.write_text(STD_G0.format(anchor=anchor) + "- M6 · 사용자 판단 = 위반 · 출처 = 상시 답 " + src + "\n"
                          + STD_SECTION.replace("{src}", src), encoding="utf-8")
    expect(fails, "mi-3 사용자 판단 줄의 상시 답 출처 → red ④", rs("--gate"), 2, "M6 상시 답 줄", "결정 줄(`· 결정 =`)이 아닌 줄")
    scope(STD_SECTION + "- M6 · 사용자 판단 = 위반 · 출처 = 상시 답 {src}\n", src)
    expect(fails, "mi-3 `상시 답 적용` 절 안이라도 결정 줄이 아닌 상시 답 줄 → red ④", rs("--gate"), 2, "M6 상시 답 줄",
           "결정 줄(`· 결정 =`)이 아닌 줄")
    scope(STD_SECTION.replace("- M1 · 결정 = 별도 요청", "- M1 · 결정 = ⓑ")
          + "\n## 메모\n\n- M1 · 결정 = 별도 요청 · 사유 = x · 출처 = 본인 직접(0700)\n", src)
    expect(fails, "implB 재상정 절 밖의 뒤 줄은 대체하지 않는다 → red ② 유지", rs("--gate"), 2, "M1 상시 답 줄", "② 처분이")
    scope(STD_SECTION.replace("- M1 · 결정 = 별도 요청", "- M1 · 결정 = ⓑ")
          + "\n## ⓐ 재상정 20260929-0700 — 상시 답 적용 1건\n\n- M1 · 사용자 판단 = 위반 · 출처 = 상시 답 {src}\n", src)
    expect(fails, "implB 결정 줄이 아닌 뒤 줄은 대체하지 않는다 → red ② 유지(+ 그 줄 ④)", rs("--gate"), 2, "② 처분이",
           "결정 줄(`· 결정 =`)이 아닌 줄")
    g2: str = "\n## ⓐ 재상정 20260929-0900 — G2 잔존\n\n- M6 · 결정 = 별도 요청 · 사유 = 잔존 · 출처 = 상시 답 {src}\n"
    scope(STD_SECTION + g2, src)
    expect(fails, "mi-2 G2 잔존 절의 상시 답 줄 → residual 실행 불능", run(repo, "residual", str(folder)), 1,
           "상시 답 출처 줄이 `상시 답 적용` 재상정 절의 결정 줄이 아니다")
    scope(STD_SECTION + g2 + "\n## ⓐ 재상정 20260929-0910 — 재질문\n\n- M6 · 결정 = 별도 요청 · 사유 = 잔존 · "
                             "출처 = 본인 직접(0910)\n", src)
    expect(fails, "mi-2 뒤 사용자 답이 대체한 G2 상시 답 줄 → residual 진행(결정적 잔존)", run(repo, "residual", str(folder)), 2,
           "결정적 잔존", "요지 축소 2")
    scope_path.write_text(STD_G0.format(anchor=anchor) + "- M1 · 결정 = ⓐ · 사유 = 사용자 판단 위반 · 출처 = 사용자 원문 "
                          "/x/answers.md:1(0300)\n" + STD_SECTION.replace("{src}", src), encoding="utf-8")
    expect(fails, "S9′ G0 의 사용자 원문 ⓐ 줄은 ④ 순서 검사에 세지 않는다 → green", rs("--gate"), 0, "red 0 · gate")
    scope(STD_SECTION.replace("- M3 · 결정 = ⓑ · 사유 = 픽스처 · 출처 = 본인 직접(0500)",
                              "- M3 · 결정 = 별도 요청 · 사유 = 불가 · 출처 = 상시 답 {src}"), src)
    expect(fails, "S5 `편집 범위 밖` 항목에 상시 답 → red ③", rs("--gate"), 2, "M3 상시 답 줄", "③ M3 은 판정 표에서 상시 답이")
    scope(STD_SECTION, f"{STD_FILE}:4@{c}")
    expect(fails, "S6 행 번호 어긋남 → red ①", rs("--gate"), 2, f"① 커밋 {c} 판의 4행이 유일한 인식 줄이 아니다")
    scope(STD_SECTION, f"{STD_FILE}:3@0123456789ab")
    expect(fails, "S6 없는 커밋 → red ①", rs("--gate"), 2, "① 커밋 0123456789ab 이 없다")
    scope(STD_SECTION, f".dddjango/other.md:3@{c}")
    expect(fails, "S6 경로 다름 → red ①", rs("--gate"), 2, "① 경로 `.dddjango/other.md`")
    _git(repo, "checkout", "-q", "-b", "side")
    side: str = commit(STD_BODY + "곁가지\n", "side")
    _git(repo, "checkout", "-q", "main")
    scope(STD_SECTION, f"{STD_FILE}:3@{side}")
    expect(fails, "S6 HEAD 의 조상이 아닌 커밋 → red ①", rs("--gate"), 2, f"① 커밋 {side} 이 HEAD 의 조상이 아니다")
    scope(STD_SECTION.replace("- M1 · 결정 = 별도 요청", "- M1 · 결정 = ⓑ"), src)
    expect(fails, "S7 상시 답으로 ⓑ → red ②", rs("--gate"), 2, "M1 상시 답 줄", "② 처분이")
    scope(STD_SECTION.replace("#2 → 별도 요청 · 남김 근거 = 해소 판정 표 · 출처 = 상시 답", "#2 → ⓑ · 남김 근거 = 해소 판정 표 · 출처 = 상시 답"), src)
    expect(fails, "S7 요지 축소 `→ ⓑ` 에 상시 답 → red ②", rs("--gate"), 2, "M2 상시 답 줄", "② 처분이")
    scope(STD_SECTION.replace("#2 → 별도 요청 · 남김 근거 = 해소 판정 표 · 출처 = 상시 답", "#2 → 별도 요청 · 남김 근거 = 사용자 선택 · 출처 = 상시 답"), src)
    expect(fails, "S7 `남김 근거 = 사용자 선택` 에 상시 답 → red ②", rs("--gate"), 2, "M2 상시 답 줄", "② 처분이")
    scope(STD_SECTION.replace(" · 상시 답 적용 2건", ""), src)
    expect(fails, "S8 `상시 답 적용` 표지 없는 재상정 절 → red ④", rs("--gate"), 2, "④ 머리에 `상시 답 적용`")
    scope_path.write_text(STD_G0.format(anchor=anchor) + "- M6 · 결정 = ⓐ · 사유 = x · 출처 = 상시 답 " + src + "\n"
                          + STD_SECTION.replace("{src}", src), encoding="utf-8")
    expect(fails, "S8 재상정 절 밖(G0 줄)의 상시 답 → red ④", rs("--gate"), 2, "M6 상시 답 줄", "④ 머리에")
    scope(STD_SECTION + "- C3 · 결정 = 별도 요청 · 사유 = x · 출처 = 상시 답 {src}\n", src)
    expect(fails, "S8 `C<n>` 상시 답 줄 → red ③", rs("--gate"), 2, "C3 상시 답 줄", "③ `C<n>`")
    scope("\n## ⓐ 재상정 20260929-0400 — 앞선 STOP\n\n- M1 · 결정 = 별도 요청 · 사유 = x · 출처 = 본인 직접(0400)\n"
          + STD_SECTION, src)
    expect(fails, "S9 앞선 재상정 사용자 답 줄 뒤 같은 항목 상시 답 → red ④", rs("--gate"), 2,
           "④ M1 의 앞선 재상정 사용자 답 줄보다 뒤다")
    scope(STD_SECTION + "- M6 · 결정 = 별도 요청 · 사유 = x · 출처 = 상시 답 {src}\n", src)
    expect(fails, "S10 표에서 해소인 항목에 상시 답(승인 뒤 override) → red ③ · architect 반송", rs("--gate"), 2,
           "③ M6 은 판정 표에서 상시 답이 덮는 항목이 아니다", "architect 반송")
    later_user: str = ("\n## ⓐ 재상정 20260929-0600 — 상시 답 red 뒤 재질문\n\n"
                       "- M1 · 결정 = 별도 요청 · 사유 = 재질문 · 출처 = 본인 직접(0600)\n")
    scope(STD_SECTION.replace("- M1 · 결정 = 별도 요청", "- M1 · 결정 = ⓑ") + later_user, src)
    expect(fails, "K3 red 인 상시 답 줄 뒤 같은 항목의 사용자 답(새 재상정 절) → 대체 · green", rs("--gate"), 0, "red 0 · gate")
    fixed_std: str = ("\n## ⓐ 재상정 20260929-0610 — 상시 답 적용 2건(고침)\n\n"
                      "- M1 · 결정 = 별도 요청 · 사유 = 불가(외부 관찰 동작 — 해소 판정 표) · 출처 = 상시 답 {fix}\n"
                      "- M2 · 결정 = 요지 축소 · 남긴 요지 = #1 · 뺀 요지 = #2 → 별도 요청 · 남김 근거 = 해소 판정 표 · "
                      "출처 = 상시 답 {fix}\n")
    scope(STD_SECTION + fixed_std.replace("{fix}", src), f"{STD_FILE}:4@{c}")
    expect(fails, "K3 행 어긋난 상시 답 줄 뒤 고친 상시 답 줄 → 대체 · green", rs("--gate"), 0, "red 0 · gate")
    scope(STD_SECTION + fixed_std.replace("{fix}", f"{STD_FILE}:5@{c}"), f"{STD_FILE}:4@{c}")
    expect(fails, "K3 고친 상시 답 줄도 어긋나면 그 줄(뒤 줄)은 검사한다 → red ①", rs("--gate"), 2,
           f"① 커밋 {c} 판의 5행이 유일한 인식 줄이 아니다")
    scope(STD_SECTION.replace("- M1 · 결정 = 별도 요청 · 사유 = 불가", "- M1 · M5 · 결정 = 별도 요청 · 사유 = 불가"), src)
    expect(fails, "K3 여러 키 상시 답 줄에서 뒤 사용자 답이 대체한 키(M5)만 빼고 검사 → green", rs("--gate"), 0,
           "red 0 · gate")
    scope(STD_SECTION, src)
    commit(None, "remove standing")
    got = rs("--gate")
    expect(fails, "S11 적용 커밋 뒤 파일 삭제 커밋 → 기록 유효(exit 0) · 상시 답 행 없음",
           (got[0] if "상시 답:" not in got[1] else 9, got[1]), 0, "red 0 · gate")


def self_test_negative_case(fails: "list[str]") -> None:
    """`--self-test` 의 불가 범주·재상정 어휘·상시 답 범주 대조에 이빨이 있는가 — 상수를 하나 빼면 red."""
    import contextlib
    import io
    corpus = ra.Corpus("claude")
    for name in ("RESOLUTION_CATEGORIES", "RECONSIDER_TOKENS", "STANDING_CATEGORIES"):
        saved = getattr(ra, name)
        setattr(ra, name, saved[:-1])
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                code: int = ra.cmd_self_test(corpus)
        finally:
            setattr(ra, name, saved)
        expect(fails, f"self-test {name} 상수 ≠ 규범 문면 → red", (code, buf.getvalue()), 2, "상수 ≠ 규범 문면")


def corpus_cases(fails: "list[str]", nov_id: str) -> None:
    corpus = ra.Corpus("claude")
    total: int = len(corpus.blocks)
    bound: int = sum(len(corpus.block_spans(corpus.key_of(d))) for d in {b.rsplit("/", 2)[0] for b in corpus.blocks})
    expect(fails, f"블록 결속 Claude 전건({bound}/{total})", (0 if bound == total else 9, f"{bound}/{total}"), 0)
    codex = ra.Corpus("codex", CODEX_SKILLS, CODEX_SKILLS / "dddjango" / "scripts" / "rulepack.json")
    cbound: int = sum(len(codex.block_spans(codex.key_of(d))) for d in {b.rsplit("/", 2)[0] for b in codex.blocks})
    print(f"  · 기록: Codex 블록 결속 {cbound}/{len(codex.blocks)}({cbound * 100 // max(1, len(codex.blocks))}%)"
          " — 의미 미러 결속 실패 블록은 제외·오탐 근거가 될 수 없다(fail-closed)")
    coord: Path = CODEX_SKILLS / "dddjango" / "SKILL.md"
    if "## 리팩토링 모드" in coord.read_text(encoding="utf-8"):
        block: str = codex.works[nov_id]["block"]
        ok: bool = block in codex.block_spans(COORD)
        expect(fails, f"적용 범위 규범 {nov_id} 블록 Codex 결속(sections·self-test 전제)", (0 if ok else 9, block), 0)
        expect(fails, "self-test(Codex)", run(ROOT, "--self-test", tool=CODEX_SKILLS / "dddjango" / "scripts" / "refactor_audit.py"),
               0, "self-test codex", "red 0")
    else:
        print("  · 보류: Codex Coordinator 에 «리팩토링 모드» 절이 아직 없다 — N-OV Codex 결속·Codex self-test 는 반영 뒤 단언")
    expect(fails, "self-test(Claude — 점검 절 실재 · 경로 사상 · 어구 상수 = 규범 문면)", run(ROOT, "--self-test"), 0, "red 0")


def main() -> int:
    fails: "list[str]" = []
    try:
        nov = _nov()
    except ra.ToolError as exc:
        print(f"FAIL — 적용 범위 규범을 팩에서 찾지 못했다: {exc}")
        return 1
    with tempfile.TemporaryDirectory(prefix="ra-fx-") as tmp:
        td: Path = Path(tmp)
        plan_cases(fails, td)
        aud: Audit = Audit(td / "main")
        check_cases(fails, aud)
        sections_case(fails, aud, nov[0])
        verdict_cases(fails, aud, nov)
        residual_cases(fails, td)
        residual_moved_case(fails, td)
        residual_ground_cases(fails, td)
        resolution_cases(fails, td)
        e2_cases(fails, td)
        final_cases(fails, td)
        standing_cases(fails, td)
    corpus_cases(fails, nov[0])
    self_test_negative_case(fails)
    if fails:
        print("\nFAIL — refactor_audit 픽스처 기대 불일치:")
        for f in fails:
            print("  - " + f.replace("\n", "\n    "))
        return 1
    print("\nPASS — refactor_audit 픽스처 기대 일치")
    return 0


if __name__ == "__main__":
    sys.exit(main())
