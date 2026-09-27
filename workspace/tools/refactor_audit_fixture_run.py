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
    expect(fails, "앞 확정 판이 있는데 --feedback 없이 재실행해 채택 축소 → red", cv(a), 2, "출처 없는 재실행")
    fb.write_text("출처 = 본인 직접(0310)\n", encoding="utf-8")
    expect(fails, "본인 직접 출처 피드백은 축소 가능 → green", cv(a, "--feedback", str(fb)), 0, "제외 1")
    Audit.verdict(a, [f"M2 | ddd-01#1 | 제외 | {EXCL_OK} | "])
    expect(fails, "R3 재실행이 기존 M 번호를 바꿈 → red", cv(a), 2, "번호를 M1 → M2")


def _res_folder(repo: Path, rows: "list[str]", verdicts: "list[str]") -> "tuple[Path, str]":
    """리팩토링 실행 산출물 폴더(G0 ⓐ 뒤 · 앵커 기록) — (폴더, 앵커)."""
    anchor: str = _git(repo, "rev-parse", "HEAD").strip()
    folder: Path = repo / ".dddjango" / "refactor-demo"
    audit: Path = folder / "audit" / "20260927-0250"
    code, out = run(repo, "plan", "demo", "--out", str(audit))
    if code != 0:
        raise RuntimeError(f"residual 준비 plan 실패: {out}")
    for name, _l, _c in ra.Plan(audit).dispatch:
        (audit / name).write_text(HEADER + ("".join(rows) if name.startswith("ddd-") else ""), encoding="utf-8")
    Audit.verdict(audit, verdicts)
    (folder / "build_anchor").write_text(anchor + "\n", encoding="utf-8")
    return folder, anchor


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
    expect(fails, "residual 근거 없는 해소 → 잔존", run(repo, "residual", str(folder), "--finalize", stamp), 2,
           "M_m=2", "리뷰어 잔존 1")
    (rdir / "result-ddd.md").write_text(
        "| M | 판정 | 근거 |\n|---|---|---|\n| M2 | 해소 | application/demo/test/test_policy.py:1 |\n", encoding="utf-8")
    expect(fails, "residual 해소 근거가 앵커 이후 안 바뀐 파일(대응 경로도 아님) → 잔존",
           run(repo, "residual", str(folder), "--finalize", stamp), 2, "M_m=2", "리뷰어 잔존 1")
    (rdir / "result-ddd.md").write_text(
        f"| M | 판정 | 근거 |\n|---|---|---|\n| M2 | 해소 | {C_LOC} |\n", encoding="utf-8")
    expect(fails, "residual 새 파일:행 근거가 있는 해소 → 해소", run(repo, "residual", str(folder), "--finalize", stamp), 2,
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
    corpus_cases(fails, nov[0])
    if fails:
        print("\nFAIL — refactor_audit 픽스처 기대 불일치:")
        for f in fails:
            print("  - " + f.replace("\n", "\n    "))
        return 1
    print("\nPASS — refactor_audit 픽스처 기대 일치")
    return 0


if __name__ == "__main__":
    sys.exit(main())
