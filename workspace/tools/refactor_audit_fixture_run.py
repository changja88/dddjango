#!/usr/bin/env python3
"""refactor_audit.py 픽스처 러너 — 도구 자체의 단위 시험(로드맵 5 · 설계 v5 §10 · 계획 v2 §2-3 · RD 설계 v15.2 §8).

리팩토링 대상 프로젝트의 테스트가 아니라 플러그인 도구의 시험이다. 합성 git 저장소(BC `demo`)에
리뷰어 표·판정 표·명세를 써 넣고 `plan`·`outline`·`check`·`sections`·`check-verdict`·`resolution`·`changes`·
`deps`·`residual`·`--self-test` 의 exit 와 요약을 대조한다. 결속·판정 사례의 코퍼스는 작업 트리
설치본(`dddjango/`·`codex-dddjango/`)과 그 규칙 팩이고, 인용·R-ID 는 실제 규범이다(Override 번호는
도구의 역할 표 상수에서 끌어 쓴다 — 번호 글자를 박지 않는다).
exit 0 = 전건 기대 일치 · 1 = 불일치.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
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
# 설계 §7 `Row.fixable` · §3-2 — R2 6번 칸 «동작 불변 정리 가능» → «바뀌는 것»(닫힌 값 다섯).
HEADER: str = ("| 행# | 규칙 | 반대 방향 규칙 | 파일:행 | 위반 요지 | 바뀌는 것 | C<n> 과 같음 |\n"
               "|---|---|---|---|---|---|---|\n")
P_LOC: str = "application/demo/domain_layer/policy.py:5"
C_LOC: str = "application/demo/driving_layer/api/thing/thing_controller.py:7"
M_LOC: str = "application/demo/driven_layer/django_demo/models/thing_model.py:4"
STAGE: str = "본인 직접(0255)"                                   # R0′ 운영 단계 출처(plan --stage)


def cite(doc: str, sec: str, quote: str) -> str:
    return f"{doc} §{sec} «{quote}»"


def _nov() -> "tuple[str, str, str]":
    """(적용 범위 규범 R-ID, 그 절 제목, 블록 안 인용 한 줄)."""
    corpus = ra.Corpus("claude")
    nov, _t = corpus.override_norms()[ra.SCOPE_ROLE]                 # 설계 §6-2 — scope_norm → override_norms(역할 표)
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


def row(n: int, rule: str, where: str = P_LOC, opposite: str = "—", fixable: str = "없음", same_c: str = "") -> str:
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
        # 설계 §6-2 · §7 `plan --stage` — check-verdict 는 plan.md `운영 단계: 운영 전` 줄이 없으면 실행 불능이다.
        code, out = run(self.repo, "plan", "demo", "--out", str(self.base / "plan0"), "--stage", STAGE)
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
    # R-0183 문면이 설계 §2 #20(리뷰 A #5 · N T6)으로 «→리팩토링 슬라이스(…)» 가 됐다 — 인용만 새 문면으로(기대 무변)
    a = aud.make([row(1, V_B9)], ["M1 | ddd-01#1 | 제외 | R-0183 «이동 권한은 G0 빚 결정→리팩토링 슬라이스» | "])
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
    # 설계 §7 `VERDICTS`·`_separate` · §3-2 — «별도 요청» → «다른 BC 몫»: 리뷰어 칸 `다른 BC 파일` ∧ 근거 `타 BC` 하나.
    a = aud.make([row(1, V_B9, where=C_LOC)], ["M1 | ddd-01#1 | 다른 BC 몫 | 타 BC application/other/domain_layer/x.py:1 | "])
    expect(fails, "리뷰어 «바뀌는 것»에 `다른 BC 파일` 없는 다른 BC 몫 → 채택 재분류", cv(a), 0,
           "재분류: M1 다른 BC 몫 → 채택", "채택 1")
    a = aud.make([row(1, V_B9, where=M_LOC, fixable="다른 BC 파일 — 마이그레이션")], ["M1 | ddd-01#1 | 다른 BC 몫 | 모델 필드 | "])
    expect(fails, "모델 필드 근거 다른 BC 몫(근거 유형은 `타 BC` 하나) → 채택 재분류", cv(a), 0,
           "재분류: M1 다른 BC 몫 → 채택(근거 유형", "채택 1")
    a = aud.make([row(1, V_B9, where=C_LOC, fixable="다른 BC 파일 — 사유: 타 BC")],
                 ["M1 | ddd-01#1 | 다른 BC 몫 | 타 BC application/other/domain_layer/x.py:1 | "])
    expect(fails, "정당한 다른 BC 몫(리뷰어 `다른 BC 파일` + 타 BC 근거 실재 · 허용 갈래 밖) → 유지", cv(a), 0, "다른 BC 몫 1")
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
    code, out = run(repo, "plan", "demo", "--out", str(audit), "--stage", STAGE)          # 설계 §6-2 · §7 plan --stage
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


def residual_ground_fp_cases(fails: "list[str]", td: Path) -> None:
    """해소 지문 = 원 발견 경로 ∪ 해소로 받은 근거 경로(web 2.1.0 K′ 와 같은 고침). 원 발견 a.py(thing_controller.py) · 해소 근거
    b.py(새 파일 helper.py) → 확정 → b.py 를 안 바꾸면 이월(대조 짝) · b.py 만 바꾸면 이월하지 않고 다시 묶는다."""
    repo: Path = _project(td / "gfp")
    folder, anchor = _res_folder(repo, [row(1, V_B9, where=P_LOC), row(2, V_B9, where=C_LOC)],
                                 ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 채택 | | "])
    (folder / "refactor-scope.md").write_text(
        f"실행 · G0 승인 20260927-0300 · 모드 리팩토링 · audit 20260927-0250 · build_anchor {anchor}\n\n"
        "- M1, M2 · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(0300)\n", encoding="utf-8")
    thing: Path = repo / "application/demo/driving_layer/api/thing/thing_controller.py"
    thing.write_text(thing.read_text(encoding="utf-8") + "\n# 정리\n", encoding="utf-8")
    helper: Path = repo / "application/demo/domain_layer/helper.py"
    helper.write_text("def to_error(code: int) -> str:\n    return str(code)\n", encoding="utf-8")
    rdir: Path = _fresh_stamp(repo, folder, clear=True)
    (rdir / "result-ddd.md").write_text("| M | 판정 | 근거 |\n|---|---|---|\n"
                                        "| M2 | 해소 | application/demo/domain_layer/helper.py:1 — 매핑을 helper 로 옮겼다 |\n",
                                        encoding="utf-8")
    expect(fails, "RD-FP1 원 발견 thing_controller.py · 해소 근거 helper.py(새 파일 · 바뀐 파일) → 해소 확정",
           run(repo, "residual", str(folder), "--finalize", rdir.name), 2, "해소 1")
    expect(fails, "RD-FP2 확정 뒤 근거 파일(helper.py) 무변 → 이월(해소 유지 · 다시 묶지 않음)", run(repo, "residual", str(folder)), 2,
           "해소 유지 1", "리뷰어 확인 대상 0")
    helper.write_text(helper.read_text(encoding="utf-8") + "\n\ndef unused() -> None:\n    return None\n", encoding="utf-8")
    expect(fails, "RD-FP3 확정 뒤 근거 파일(helper.py)만 바뀜 → 이월하지 않고 M2 를 다시 묶는다(해소 지문에 근거 경로)",
           run(repo, "residual", str(folder)), 0, "리뷰어 확인 대상 1(ddd)", "M_m 미정")


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
    expect(fails, "O2 묶음 머리에 build_anchor 이후 변경 파일·원 발견·대응 경로의 실재 위치 조건",
           (0 if "` — ` 앞에는 `build_anchor` 이후 바뀐 파일(산출물 폴더 제외) 또는 이 항목의 원 발견 · 대응 경로에 속하는 "
            "지금 있는 `파일:행[-행]`만 적는다. 지워서 푼 항목도 같은 조건을 따르며, 삭제 사실과 허용 집합 밖 주변 위치는 "
            "` — ` 뒤에 적는다." in bundle else 9, bundle), 0)
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
    # 설계 §7 해소 판정 · §3-3 — 불가 범주 7 → 6(외부 관찰 동작 · 테스트 본문 동반 · 테스트 새 판정 걷음 → V 로)
    "M2b": f"| M2 | 2 | 긴 위치 인자 목록 | 불가 | 편집 범위 밖 | {X_LOC} — 호출 쪽 BC 밖 파일 인자 형태가 바뀐다 | — | — |\n",
    "M3": f"| M3 | 1 | 판정이 어댑터에 | 불가 | 반대 방향 규칙 | {C_LOC} — 404 응답이 도메인 예외로 바뀐다 | — | — |\n",
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
    # 리뷰 B #5 · 설계 :249 · :253 — M3 의 `반대 방향 규칙` 불가는 원 행이 인용한 반대 방향 규칙(OPP_SIBLING)으로 선다.
    folder, anchor = _res_folder(repo, [row(1, V_B9, where=P_LOC), row(2, V_B9, where=C_LOC),
                                        row(3, V_B9, where=C_LOC, opposite=OPP_SIBLING), row(4, V_B9, where=P_LOC)],
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
    spec({**RES_ROWS, "M3": RES_ROWS["M3"].replace("반대 방향 규칙", "기존 보호 부족")})
    expect(fails, "resolution 불가 범주가 닫힌 목록 밖(«기존 보호 부족» 포함) → red", rs(), 2, "`기존 보호 부족`", "닫힌 목록")
    spec({**RES_ROWS, "M3": RES_ROWS["M3"].replace(C_LOC, "application/demo/driving_layer/api/thing/thing_controller.py:999")})
    expect(fails, "resolution 막는 것 파일:행 부재 → red", rs(), 2, "대상 프로젝트에 없다")
    spec({**RES_ROWS, "M1": RES_ROWS["M1"].replace("M1 — 규칙 함수 이름 통일", "명세에 없는 처방 문장")})
    expect(fails, "resolution 처방 앵커 원문이 표 밖 본문에 없음 → red", rs(), 2, "M1 #1 처방 앵커")
    spec({**RES_ROWS, "M2a": RES_ROWS["M2a"].replace("뺀 요지의 처방은 인자 형태만 바꾼다", "—")})
    expect(fails, "resolution 부분 항목 해소 행의 되돌리지 않는 이유 공란 → red", rs(), 2, "되돌리지 않는 이유")
    spec({**RES_ROWS, "M4": "| M4 | 1 | 병합 항목 | 해소 | — | — | M1 — 규칙 함수 이름 통일 | — |\n",
          "M1": RES_ROWS["M1"].replace("| 해소 |", "| 부분 |")})
    expect(fails, "resolution 병합 항목 행(범위 밖)·요지 판정 값 밖 → red(설계 §7 — 판정 값 해소 · 변경 · 불가)", rs(), 2, "M4 범위 밖",
           "`부분` 이 `해소` · `변경` · `불가` 밖")
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
    spec({**RES_ROWS, "M1": RES_ROWS["M1"].replace("| 해소 | — |", "| 해소 | 편집 범위 밖 |")})
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
    expect(fails, "M-1a R8-R 실물 모양 전체 제외 줄 + 표의 해소 요지 → red(설계 §7 «정리» = 해소 ∪ 변경)", rs("--gate"), 2,
           "M2 전체 제외 항목의 판정 표에 정리(해소·변경) 요지가 남아 있다")
    scope(RES_RECON + WHOLE_M2)
    expect(fails, "M-1b 요지 축소 뒤 G2 전체 철회 줄 · 표 무수정 → red(설계 §7 «정리»)", rs("--gate"), 2,
           "M2 전체 제외 항목의 판정 표에 정리(해소·변경) 요지가 남아 있다")
    whole_no: int = next(i for i, ln in enumerate(scope_path.read_text(encoding="utf-8").split("\n"), 1)
                         if ln.startswith("- M2 · 결정 = 별도 요청"))
    fixed: str = (f"| M2 | 1 | 예외 매핑 흩어짐 | 불가 | 재상정 제외 | {scope_rel}:{whole_no} — G2 잔존 철회로 항목 전체를 뺐다 "
                  "| — | — |\n")
    spec({**RES_ROWS, "M2a": fixed})
    expect(fails, "M-1c 표를 전체 불가(해소이던 요지 = 재상정 제외 · 막는 것 = 결정 줄)로 고침 → green", rs("--gate"), 0,
           "red 0 · gate")
    scope()
    spec({**RES_ROWS, "M3": RES_ROWS["M3"].replace("반대 방향 규칙", "재상정 제외")})
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
    folder, anchor = _res_folder(repo, [row(1, V_B9, where=P_LOC), row(2, V_B9, where=C_LOC),   # M3 반대 방향 근거 — 리뷰 B #5
                                        row(3, V_B9, where=C_LOC, opposite=OPP_SIBLING), row(4, V_B9, where=P_LOC)],
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
    """R8d ① — `--final` 재분류(새 번호 · 번호 중복 · 병합→채택 · 원 행 두 번 · 통과 아닌 원 행)와 다른 BC 몫 재분류를
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
    # F7 다른 BC 몫 → 채택 재분류(--final 없이 exit 0) — 확정 표에 채택으로 남는다(설계 §7 «별도 요청» → «다른 BC 몫»)
    rp, fd, cv = lane("f7", [row(1, V_B9, where=M_LOC)], ["M1 | ddd-01#1 | 다른 BC 몫 | 모델 필드 | "], "M1", ["M1"],
                      final=False)
    vf: Path = fd / "audit" / "20260927-0250" / "verdict-final.md"
    expect(fails, "F7 다른 BC 몫 → 채택 재분류(exit 0) → verdict-final.md 에 채택 · verdict.md 원문 보존",
           (int(cv.split("/")[0]), (vf.read_text(encoding="utf-8") if vf.is_file() else "")
            + (fd / "audit" / "20260927-0250" / "verdict.md").read_text(encoding="utf-8")), 0,
           "| M1 | ddd-01#1 | 채택 |", "| M1 | ddd-01#1 | 다른 BC 몫 |")
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
STD_SPEC: str = ("# 설계 명세 — demo\n\n**M2 — 예외 매핑 정리 처방** 매핑 표 한 곳.\n\n## 5. 슬라이스 0 해소 판정\n\n" + RES_HEAD
                 + f"| M1 | 1 | 판정 흩어짐 | 불가 | 편집 범위 밖 | {X_LOC} — BC 밖 파일을 고친다 | — | — |\n"
                 + "| M2 | 1 | 예외 매핑 | 해소 | — | — | M2 — 예외 매핑 정리 처방 | 뺀 요지 처방은 인자만 바꾼다 |\n"
                 + f"| M2 | 2 | 인자 목록 | 불가 | 편집 범위 밖 | {X_LOC} — BC 밖 호출 자리가 바뀐다 | — | — |\n\n## 6. 끝\n")
STD_G0: str = ("실행 · G0 승인 20260929-0300 · 모드 리팩토링 · audit 20260927-0250 · build_anchor {anchor}\n\n"
               "- M1, M2 · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(0300)\n")
STD_USER: str = ("\n## ⓐ 재상정 20260929-0500 — G1 재상정\n\n"
                 "- M1 · 결정 = 별도 요청 · 사유 = 불가(편집 범위 밖) · 출처 = 본인 직접(0500)\n"
                 "- M2 · 결정 = 요지 축소 · 남긴 요지 = #1 · 뺀 요지 = #2 → 별도 요청 · 남김 근거 = 해소 판정 표 · "
                 "출처 = 본인 직접(0500)\n")


def standing_cases(fails: "list[str]", td: Path) -> None:
    """㉯ 상시 답 걷기 — 설계 §7 «상시 답» · §3-4: 흐름 · `--gate` · `residual` 에서 걷고 인식 블록만 web 수리 때까지 둔다.
    옛 `출처 = 상시 답` 줄이 이번 실행 몫(«앞 실행» 절 밖)이면 실행 불능 · «앞 실행» 절 안이면 기록일 뿐(옛 S1~S15 대체)."""
    repo: Path = _project(td / "std")
    folder, anchor = _res_folder(repo, [row(1, V_B9, where=C_LOC), row(2, V_B9, where=C_LOC)],
                                 ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 채택 | | "])
    (folder / "design-spec.md").write_text(STD_SPEC, encoding="utf-8")
    scope_path: Path = folder / "refactor-scope.md"
    std: Path = repo / STD_FILE
    rs = lambda *extra: run(repo, "resolution", str(folder), *extra)  # noqa: E731
    std.parent.mkdir(parents=True, exist_ok=True)
    std.write_text(STD_BODY, encoding="utf-8")
    _git(repo, "add", STD_FILE)
    _git(repo, "commit", "-qm", "standing")
    c: str = _git(repo, "rev-parse", "HEAD").strip()[:12]
    old: str = f"- M1 · 결정 = 별도 요청 · 사유 = 불가 · 출처 = 상시 답 {STD_FILE}:3@{c}\n"
    scope_path.write_text(STD_G0.format(anchor=anchor) + STD_USER, encoding="utf-8")
    got = rs()
    expect(fails, "S′1 인식되는 상시 답 파일이 있어도 resolution 출력에 상시 답 행 · 요약 꼬리 없음(흐름에서 걷음)",
           (got[0] if "상시 답" not in got[1] else 9, got[1]), 0, "해소 판정: 해소 0 · 부분 1 · 불가 1")
    expect(fails, "S′2 사용자 직접 답만의 재상정 → resolution --gate green", rs("--gate"), 0, "red 0 · gate")
    scope_path.write_text(STD_G0.format(anchor=anchor) + STD_USER.replace(
        "- M1 · 결정 = 별도 요청 · 사유 = 불가(편집 범위 밖) · 출처 = 본인 직접(0500)\n", old), encoding="utf-8")
    expect(fails, "S′3 이번 실행 몫의 옛 `출처 = 상시 답` 결정 줄 → resolution --gate 실행 불능", rs("--gate"), 1,
           "옛 `출처 = 상시 답` 줄", "상시 답은 걷혔다")
    expect(fails, "S′4 같은 줄 → residual 실행 불능", run(repo, "residual", str(folder)), 1, "옛 `출처 = 상시 답` 줄")
    expect(fails, "S′5 같은 줄 — `--gate` 없는 resolution 은 실행 불능이 아니다(설계 :1355 — 흐름 · --gate · residual)",
           rs(), 0, "red 0")
    scope_path.write_text(STD_G0.format(anchor=anchor) + "- M2 · 사용자 판단 = 위반 · 출처 = `상시 답` x\n" + STD_USER,
                          encoding="utf-8")
    expect(fails, "S′6 결정 줄이 아닌 줄의 상시 답 출처(백틱 변형)도 이번 실행 몫이면 실행 불능", rs("--gate"), 1,
           "옛 `출처 = 상시 답` 줄")
    scope_path.write_text(STD_G0.format(anchor=anchor) + STD_USER + "\n# 앞 실행\n\n실행 · G0 승인 20260920-0100 · "
                          "모드 리팩토링 · audit 20260919-0000 · G2 승인 20260921-0000\n\n## ⓐ 재상정 20260920-0300 — "
                          "상시 답 적용 1건\n\n" + old, encoding="utf-8")
    expect(fails, "S′7 «앞 실행» 절 안의 옛 상시 답 줄은 기록일 뿐 → resolution --gate green", rs("--gate"), 0, "red 0 · gate")


# ── RD(설계 v15.2 §8 «refactor_audit_fixture_run.py +약 32») ───────────────────────────────────────────

def _block_quote(rid: str, platform: str = "claude") -> "tuple[str, str, str]":
    """(문서 키, 그 블록을 담은 절 제목, 블록 안 인용 한 줄 40자) — 규범 블록에서 바로 뽑는다(번호 무관)."""
    corpus = ra.Corpus(platform)
    meta: dict = corpus.works[rid]
    key: str = corpus.key_of(meta["document"])
    i, j = corpus.block_spans(key)[meta["block"]][0]
    index = corpus.doc(key)
    heading: str = next(t for line, _lv, t, _a in reversed(index.headings) if line <= i)
    first: str = next(ln for ln in index.lines[i:j] if ln.strip())
    body: str = first.replace("*", "").replace("`", "").strip().lstrip("-> ").strip()
    body = re.sub(r"^\d+[.)]\s*", "", body)
    return key, heading, body[:40]


def _evidence_norm(rids: "list[str]", bound: bool) -> "tuple[str, str]":
    """(R-ID, 인용) — 후보 가운데 블록 첫 줄 인용이 20~40자이고 «» 가 없으며(`bound` 면 그 규범 블록에 결속까지) 첫 규범."""
    corpus = ra.Corpus("claude")
    for rid in rids:
        meta: dict = corpus.works[rid]
        key: str = corpus.key_of(meta["document"])
        if meta["block"] not in corpus.block_spans(key):
            continue
        quote: str = _block_quote(rid)[2].strip()
        if not 20 <= len(quote) <= 60 or "«" in quote or "»" in quote or "|" in quote:
            continue
        if bound:
            bid, _why = corpus.bind(key, quote)
            if bid is None or rid not in corpus.blocks[bid]["works"]:
                continue
        return rid, quote
    raise RuntimeError("증거 칸 픽스처에 쓸 규범을 찾지 못했다")


def _opsafe_target() -> str:
    """운영 전 예외 대상 가운데 적용 범위 대상이 아닌 것 하나(R-ID 순)."""
    roles = ra.Corpus("claude").override_norms()
    return sorted(roles[ra.OPSAFE_ROLE][1] - roles[ra.SCOPE_ROLE][1])[0]


def stage_cases(fails: "list[str]", td: Path) -> None:
    """설계 §7 `plan --stage` · §6-2 — plan.md `운영 단계:` 줄 · check-verdict 결속."""
    repo: Path = _project(td / "stage")
    got = run(repo, "plan", "demo", "--out", str(td / "st1"), "--stage", "운영 전 — 본인 직접(1903)")
    text: str = (td / "st1" / "plan.md").read_text(encoding="utf-8") if (td / "st1" / "plan.md").is_file() else ""
    expect(fails, "RD-P1 plan --stage → plan.md `운영 단계: 운영 전 본인 직접(1903)` 줄(앞 «운영 전 —» 는 뗀다)",
           (got[0], got[1] + text), 0, "- 운영 단계: 운영 전 본인 직접(1903)", "· 운영 단계 운영 전")
    expect(fails, "RD-P2 plan --stage 대리 출처 → 실행 불능(운영 단계는 대리 불가)",
           run(repo, "plan", "demo", "--out", str(td / "st2"), "--stage", "대리 답 ⓐ x.md:1"), 1, "대리 답을 받지 않는다")
    expect(fails, "RD-P3 plan --stage 운영 중 → 실행 불능(G0 정지 몫)",
           run(repo, "plan", "demo", "--out", str(td / "st3"), "--stage", "운영 중 — 본인 직접(1900)"), 1, "운영 중")
    run(repo, "plan", "demo", "--out", str(td / "st4"))
    audit: Path = td / "st4"
    for name, _l, _c in ra.Plan(audit).dispatch:
        (audit / name).write_text(HEADER + (row(1, V_B9) if name.startswith("ddd-") else ""), encoding="utf-8")
    Audit.verdict(audit, ["M1 | ddd-01#1 | 채택 | | "])
    expect(fails, "RD-P4 plan.md 에 운영 단계 줄이 없으면 check-verdict 실행 불능(운영 전 예외 결속)",
           run(repo, "check-verdict", str(audit)), 1, "운영 단계: 운영 전 <출처>")


def override_cases(fails: "list[str]", aud: Audit, td: Path) -> None:
    """설계 §6-2 · §7 `override_norms` — 역할 표 · 두 Override 의 대상 · 조건부 대상은 제외 · 반대 방향 근거 금지."""
    cv = lambda audit, *extra: run(aud.repo, "check-verdict", str(audit), *extra)  # noqa: E731
    opsafe_id: str = ra.OVERRIDE_ROLES[ra.OPSAFE_ROLE]
    target: str = _opsafe_target()
    tkey, thead, tquote = _block_quote(target)
    a = aud.make([row(1, V_B9)], [f"M1 | ddd-01#1 | 제외 | {target} «{tquote}» | "])
    expect(fails, f"RD-O1 운영 전 예외 대상({target})을 제외 근거 → red ③", cv(a), 2, f"③ 운영 전 예외 대상 규범 {target}")
    okey, ohead, oquote = _block_quote(opsafe_id)
    a = aud.make([row(1, V_B9)], [f"M1 | ddd-01#1 | 제외 | {opsafe_id} «{oquote}» | "])
    expect(fails, "RD-O2 운영 전 예외 규범 자신을 제외 근거 → red ③", cv(a), 2, f"③ 운영 전 예외 규범 {opsafe_id}")
    a = aud.make([row(1, V_B9, opposite=cite(tkey, thead, tquote))], ["M1 | ddd-01#1 | 사용자 판단 | 규칙 충돌 | "])
    expect(fails, "RD-O3 운영 전 예외 대상을 반대 방향 규칙으로 사용자 판단 → red", cv(a), 2, f"운영 전 예외 대상 규범 {target}")
    a = aud.make([row(1, V_B9, opposite=cite(okey, ohead, oquote))], ["M1 | ddd-01#1 | 사용자 판단 | 규칙 충돌 | "])
    expect(fails, "RD-O4 운영 전 예외 규범 자신을 반대 방향 규칙으로 → red", cv(a), 2, f"운영 전 예외 규범 {opsafe_id}")
    a = aud.make([row(1, V_B9)])
    got = run(aud.repo, "sections", str(a))
    text: str = (a / "sections.md").read_text(encoding="utf-8") if (a / "sections.md").is_file() else ""
    expect(fails, "RD-O5 sections 가 Override 둘(원문 · 대상 목록)을 싣는다", (got[0], got[1] + text), 0,
           "## 적용 범위 규범", "## 운영 전 예외 규범", f"〔{opsafe_id} · Override", f"| {target} |",
           f"운영 전 예외 규범 {opsafe_id} · 대상")
    pack = json.loads((TOOL.parent / "rulepack.json").read_text(encoding="utf-8"))
    pack["works"][opsafe_id]["overrides"] = []
    bad: Path = td / "pack-no-opsafe.json"
    bad.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")
    expect(fails, "RD-O6 팩의 대상 있는 Override 집합 ≠ 역할 표 → sections 실행 불능",
           run(aud.repo, "--rulepack", str(bad), "sections", str(a)), 1, "대상 있는 Override 집합 ≠ 역할 표")
    expect(fails, "RD-O7 같은 팩 → check-verdict 실행 불능", run(aud.repo, "--rulepack", str(bad), "check-verdict", str(a)),
           1, "대상 있는 Override 집합 ≠ 역할 표")


def change_column_cases(fails: "list[str]", aud: Audit) -> None:
    """설계 §7 `Row.fixable` · `check-verdict 요약:` — «바뀌는 것» 닫힌 값 · 형식 밖 경고 · 동반 수."""
    rows: "list[str]" = [row(1, V_B9, fixable="내부 약속 + DB 구조 — 저장 형태"), row(2, V_B9, fixable="밖 동작"),
                         row(3, V_B9, fixable="예"), row(4, V_B9, fixable="없음 + 밖 동작"), row(5, V_B9)]
    a = aud.make(rows, ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 병합 → M1 | | ", "M3 | ddd-01#3 | 채택 | | ",
                        "M4 | ddd-01#4 | 채택 | | ", "M5 | ddd-01#5 | 채택 | | "])
    got = run(aud.repo, "check", str(a))
    expect(fails, "RD-K1 check — «바뀌는 것» 형식 밖(옛 «예» · `없음` 겹침) 경고 2 · 판정은 막지 않는다(exit 0)", got, 0,
           "경고: ddd-01#3 «바뀌는 것» 칸 `예`", "경고: ddd-01#4", "바뀌는 것 형식 밖 2(경고)")
    expect(fails, "RD-K2 check-verdict 요약 `바뀌는 것 동반 안 · 밖 · DB · 다른 BC`(병합 행은 대상 항목으로) · 경고 꼬리",
           run(aud.repo, "check-verdict", str(a)), 0, "다른 BC 몫 0", "바뀌는 것 동반 안 1 · 밖 1 · DB 1 · 다른 BC 0",
           "바뀌는 것 형식 밖 2(경고) · red 0")


ACL_REL: str = "application/other/driven_layer/adapter/anticorruption_layer/demo/demo_adapter.py"
REGISTRAR_REL: str = "application/demo/driving_layer/api/api_router.py"
REGISTRAR: str = ("from ninja_extra import NinjaExtraAPI\n\n"
                  "from application.demo.driving_layer.api.thing.thing_controller import ThingController\n\n\n"
                  "def register_demo_api(api: NinjaExtraAPI) -> None:\n    api.register_controllers(ThingController)\n")
URLS_PY: str = ("from django.urls import path\n\nfrom application.demo.driving_layer.api.api_router import register_demo_api\n"
                "from config.api import api\n\nregister_demo_api(api)\n\nurlpatterns = [path(\"api/\", api.urls)]\n")
DEPS_FILES: "dict[str, str]" = {
    **FILES,
    ACL_REL: "from application.demo.driving_layer.open_host_service.thing.thing_service import get\n\n\nX = get\n",
    "application/demo/driving_layer/open_host_service/__init__.py": "",
    "application/demo/driving_layer/open_host_service/thing/thing_service.py": "def get() -> int:\n    return 1\n",
    "application/demo/domain_layer/uses_base.py": (
        "from application.base.driving_layer.open_host_service.base_service import f\n\n\nY = f\n"),
    "application/base/driving_layer/open_host_service/base_service.py": "def f() -> int:\n    return 2\n",
    "application/other/test/test_demo_adapter.py": (
        "from application.other.driven_layer.adapter.anticorruption_layer.demo.demo_adapter import X\n\n\n"
        "def test_x() -> None:\n    assert X\n"),
    "application/third/domain_layer/y.py": "from application.demo.domain_layer.policy import rule_0\n\n\nZ = rule_0\n",
    "web/home/client.py": "URL: str = \"/api/thing/1\"\n",
    "web/home/tests/test_client.py": "from web.home.client import URL\n\n\ndef test_url() -> None:\n    assert URL\n",
    "scripts/tool.py": "import application.demo.domain_layer.policy\n",
    # 구현 지식 implementation-django-ninja 의 «프로젝트 소유 API · BC 소유 registrar · URLconf 소유 합성» 꼴 — HTTP 소비 판정은
    # 이 마운트를 결속하지 않는다(r3 처분 · api_controller 접두 조각 일치 상위 집합)
    "config/settings.py": "ROOT_URLCONF: str = \"config.urls\"\n",
    "config/api.py": "from ninja_extra import NinjaExtraAPI\n\napi = NinjaExtraAPI()\n",
    REGISTRAR_REL: REGISTRAR,
    "config/urls.py": URLS_PY,
}


def other_bc_lane_case(fails: "list[str]", td: Path) -> None:
    """설계 §3-2 · §5-2 — 다른 BC 몫 근거가 이 레인이 고치는 갈래(받는 쪽 어댑터)면 채택 재분류."""
    aud = Audit.__new__(Audit)
    aud.repo = _project(td / "obc", DEPS_FILES)
    aud.base = td / "obc-audits"
    run(aud.repo, "plan", "demo", "--out", str(aud.base / "plan0"), "--stage", STAGE)
    aud.plan = (aud.base / "plan0" / "plan.md").read_text(encoding="utf-8")
    aud.n = 0
    a = aud.make([row(1, V_B9, where=C_LOC, fixable="다른 BC 파일 — 받는 쪽")],
                 [f"M1 | ddd-01#1 | 다른 BC 몫 | 타 BC {ACL_REL}:1 | "])
    expect(fails, "RD-B1 다른 BC 몫 근거가 받는 쪽 어댑터(이 레인 몫) → 채택 재분류", run(aud.repo, "check-verdict", str(a)), 0,
           "재분류: M1 다른 BC 몫 → 채택(근거", "받는 쪽 어댑터", "채택 1")
    a = aud.make([row(1, V_B9, where=C_LOC, fixable="다른 BC 파일 — x")],
                 ["M1 | ddd-01#1 | 다른 BC 몫 | 타 BC application/other/domain_layer/x.py:9 | "])
    expect(fails, "RD-B2 타 BC 근거 행 범위 밖(실재 안 함) → 채택 재분류", run(aud.repo, "check-verdict", str(a)), 0,
           "재분류: M1 다른 BC 몫 → 채택(타 BC 근거")


V_SPEC_ROWS: str = (
    "| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |\n"
    "|---|---|---|---|---|---|\n"
    "| 규칙 함수 반환 기대 | 규칙 계약 | 규칙 오류 | test_policy | update | coder `application/demo/test/test_policy.py::test_rule` |\n"
    "| 컨트롤러 404 응답 | HTTP 계약 | 매핑 오류 | 없음 | add | acceptance-tester `application/demo/test/test_thing_api.py::test_gone` |\n"
    "| 정책 시험 파일 재조직(이동) | 같은 기대 그대로 | — | test_policy | retain | coder `application/demo/test/unit/test_policy.py` |\n"
    "| 큰 함수 시험 그대로 | — | — | — | retain | coder `application/demo/test/test_big.py` |\n")
V1_TEXT: str = ("- V1 · 내부 약속 · 근거 M1 #1 · 슬라이스 S1\n"
                "  - 전 → 후: rule_0 이 x → x + 1\n"
                "  - 시험: 규칙 함수 반환 기대 update(coder) application/demo/test/test_policy.py::test_rule\n"
                "    - 바뀌는 기대: «assert True»\n")
V2_TEXT: str = ("- V2 · 밖 동작 + DB 구조 · 근거 M2 #1 · 슬라이스 S2\n"
                "  - 전 → 후: 없는 thing 404 → 410\n"
                "  - 시험: 컨트롤러 404 응답 add(acceptance-tester) application/demo/test/test_thing_api.py::test_gone\n"
                "    - 바뀌는 기대: 기대 추가 1\n"
                "  - 연산: demo · migrations.AddField(model_name=\"thingmodel\", name=\"gone\", "
                "field=models.BooleanField(default=False))\n"
                "  - 데이터: 보존 안 함 — 위반 행이 있으면 적용 실패\n"
                "  - 영향: 받는 쪽 0 · HTTP 소비 0\n")
EDIT_LINE: str = f"- {ACL_REL} · 받는 쪽 어댑터 · V2\n"
CH_ROW_M1: str = "| M1 | 1 | 규칙 이름 흩어짐 | 변경 | — | V1 | M1 — 규칙 함수 이름 통일 | — |\n"
CH_ROW_M2: str = "| M2 | 1 | 예외 매핑 흩어짐 | 변경 | — | V2 | M2 — 컨트롤러 예외 매핑 정리 | — |\n"


class ChangesLane:
    """changes 픽스처 — 합성 저장소 · G0 ⓐ M1 · M2 · 명세(V · 입장 표 · 다른 BC 편집 · 해소 표) · 지원 기록."""

    def __init__(self, td: Path, name: str) -> None:
        self.repo: Path = _project(td / name, DEPS_FILES)
        self.folder, self.anchor = _res_folder(self.repo, [row(1, V_B9, where=P_LOC), row(2, V_B9, where=C_LOC)],
                                               ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 채택 | | "])
        self.scope_base: str = (f"실행 · G0 승인 20261004-1900 · 모드 리팩토링 · audit 20260927-0250 · build_anchor "
                                f"{self.anchor}\n\n- M1, M2 · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(1900)\n")
        (self.folder / "refactor-scope.md").write_text(self.scope_base, encoding="utf-8")
        self.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2)

    def spec(self, vs: str, edits: str, res_rows: str, adm: str = V_SPEC_ROWS) -> None:
        (self.folder / "design-spec.md").write_text(
            RES_BODY + "## 5. 슬라이스 0 해소 판정\n\n" + RES_HEAD + res_rows + "\n## 6. 영구 테스트 입장 표\n\n" + adm
            + "\n## 7. 바뀌는 것 목록\n\n" + vs + "\n## 8. 다른 BC 편집 목록\n\n" + edits + "\n## 9. 끝\n", encoding="utf-8")

    def support(self, stamp: str = "20261004T100000Z", verdict: str = "지원", argv: str = "pytest") -> None:
        d: Path = self.folder / "behavior" / "support" / stamp
        d.mkdir(parents=True, exist_ok=True)
        (d / "run-definition.json").write_text(json.dumps({"version": 1, "argvs": [[argv]], "env": {"PYTEST_ADDOPTS": None},
                                                           "sources": ["Makefile:1"], "frozen_at": stamp}), encoding="utf-8")
        (d / "g0-collect.json").write_text(json.dumps({"version": 1, "verdict": verdict}), encoding="utf-8")

    def ch(self, *extra: str) -> "tuple[int, str]":
        return run(self.repo, "changes", str(self.folder), *extra)


def changes_cases(fails: "list[str]", td: Path) -> None:
    """설계 §3-3 · §3-4 · §7 새 `changes` — 기본 · --candidate · --applied · --gate · --baseline · 공개 함수."""
    lane = ChangesLane(td, "chg")
    f = lane.folder
    expect(fails, "RD-C1 changes 기본 — V 형식 · 입장 행 · owner ↔ 종류 · 허용 연산 · 다른 BC 편집 ⊆ deps · 바뀌는 기대 실재 → green",
           lane.ch(), 0, "V 2(내부 약속 1 · 밖 동작 1 · DB 구조 1)", "연산 1 · 다른 BC 편집 1 · retain 재조직 1", "red 0")
    for label, vs, needle in (
            ("RD-C2 V 종류 닫힌 값 밖 → red", V1_TEXT.replace("내부 약속", "속 약속") + V2_TEXT, "종류 `속 약속`"),
            ("RD-C3 `전 → 후:` 없음 → red", V1_TEXT.replace("  - 전 → 후: rule_0 이 x → x + 1\n", "") + V2_TEXT, "`전 → 후:`"),
            ("RD-C4 시험 줄 입장 행이 입장 표에 없음 → red", V1_TEXT.replace("규칙 함수 반환 기대 update", "없는 입장 행 update")
             + V2_TEXT, "입장 표에 없다"),
            ("RD-C5 owner ↔ 종류 — 내부 약속 V 에 acceptance-tester → red",
             V1_TEXT.replace("update(coder)", "update(acceptance-tester)") + V2_TEXT, "밖 동작 V 에만"),
            ("RD-C6 연산 RunPython → red", V1_TEXT + V2_TEXT.replace("migrations.AddField(model_name=\"thingmodel\", name=\"gone\", "
                                                                     "field=models.BooleanField(default=False))",
                                                                     "migrations.RunPython(forwards)"), "RunPython"),
            ("RD-C7 연산 호출식 파싱 불가 → red", V1_TEXT + V2_TEXT.replace("default=False))", "default=False)"), "파싱되지 않는다"),
            ("RD-C8 바뀌는 기대 원문이 지금 시험 케이스에 없음 → red", V1_TEXT.replace("«assert True»", "«assert False»") + V2_TEXT,
             "원문이 기준 판 케이스에 없다"),
            ("RD-C9 DB 구조 V 에 연산 없음 → red", V1_TEXT + "\n".join(ln for ln in V2_TEXT.split("\n")
                                                                       if "연산:" not in ln), "연산:` 줄이 없다"),
            ("RD-C10 밖 동작 V 에 영향 줄 없음 → red", V1_TEXT + V2_TEXT.replace("  - 영향: 받는 쪽 0 · HTTP 소비 0\n", ""),
             "`영향:` 줄이 없다")):
        lane.spec(vs, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2)
        expect(fails, label, lane.ch(), 2, needle)
    lane.spec(V1_TEXT + V2_TEXT, "- application/other/domain_layer/x.py · 받는 쪽 어댑터 · V2\n", CH_ROW_M1 + CH_ROW_M2)
    expect(fails, "RD-C11 다른 BC 편집 줄이 deps 출력과 다름(받는 쪽 어댑터 아님) → red", lane.ch(), 2, "deps 출력과 다르다")
    lane.spec(V1_TEXT + V2_TEXT, "- application/demo/domain_layer/policy.py · 공유 표면 · V2\n", CH_ROW_M1 + CH_ROW_M2)
    expect(fails, "RD-C12 다른 BC 편집 경로가 대상 BC 안 → red", lane.ch(), 2, "대상 BC(demo) 안")
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2)
    expect(fails, "RD-C13 --candidate 지원 기록 없음 → 실행 불능", lane.ch("--candidate"), 1, "지원 확인 기록")
    lane.support("20261004T090000Z", argv="pytest -x")
    lane.support("20261004T100000Z", verdict="지원 안 함")
    got = lane.ch("--candidate")
    cand_files = sorted((f / "g1").glob("*-candidate.json"))
    snap: dict = json.loads(cand_files[-1].read_text(encoding="utf-8")) if cand_files else {}
    digest: str = ra.snapshot_digest(snap) if snap else ""
    expect(fails, "RD-C14 --candidate → g1/<UTC>-candidate.json + 후보 digest(지원 안 함 기록은 건너뜀 · 실행 정의 결속)",
           (got[0] if snap.get("support_record") == "20261004T090000Z" and digest and f"후보 digest {digest}" in got[1]
            else 9, got[1] + json.dumps(snap, ensure_ascii=False)[:400]), 0, "red 0 · candidate")
    # B1R 수리(설계 v3.1 §1-5 6): 후보 digest 는 결속 칸 `resolution_rows_digest` 를 담은 후보 파일 전체로 검증하고, 지금 스냅숏과의
    # 동일성 대조에서만 그 한 칸을 뺀다 · 지금 · 최종 digest 는 `snapshot_digest(changes_snapshot(…))` 로 따로 센다.
    bare: dict = {k: v for k, v in snap.items() if k != "resolution_rows_digest"}
    now_digest: str = ra.snapshot_digest(ra.changes_snapshot(f, lane.repo)) if snap else ""
    side_rows: object = (json.loads(cand_files[-1].with_name(cand_files[-1].name[:-len(".json")] + "-resolution.json")
                                    .read_text(encoding="utf-8")).get("rows") if cand_files else None)
    rows_bind: str = hashlib.sha256(json.dumps(side_rows, ensure_ascii=False, sort_keys=True,
                                               separators=(",", ":")).encode("utf-8")).hexdigest()
    same: bool = (bool(snap) and ra.changes_snapshot(f, lane.repo) == bare and ra.load_candidate(f, digest) == snap
                  and now_digest == ra.snapshot_digest(bare) and snap.get("resolution_rows_digest") == rows_bind
                  and len(rows_bind) == 64 and isinstance(side_rows, list) and len(side_rows) == 2)
    k0_run: str = hashlib.sha256(json.dumps({"argvs": [["pytest -x"]], "env": {"PYTEST_ADDOPTS": None}}, ensure_ascii=False,
                                            sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:12]
    k0_snap: str = hashlib.sha256(json.dumps(snap, ensure_ascii=False, sort_keys=True,
                                             separators=(",", ":")).encode("utf-8")).hexdigest()[:12]
    expect(fails, "RD-C15 공개 함수 — changes_snapshot = 후보 파일 − 결속 칸 · load_candidate(digest) = 후보 · k0 판형 칸 · k0 digest 규칙 · "
           "결속 칸 = 곁 자료 rows 정규 JSON sha256",
           (0 if same and snap.get("run_definition_digest") == k0_run and digest == k0_snap
            and sorted(snap) == ["V", "linked_rows", "other_bc_edits", "remove_rows", "resolution_rows_digest", "retain_rows",
                                 "run_definition_digest", "support_record", "update_rows", "version"]
            and snap["V"][0]["tests"][0]["expect_old"] == ["assert True"] and snap["V"][1]["ops"][0]["op"] == "AddField"
            and snap["V"][1]["ops"][0]["key"].startswith("demo · Call(") and snap["retain_rows"] == [
                {"path": "application/demo/test/unit/test_policy.py", "case": None, "why": "같은 기대 그대로"}]
            and snap["other_bc_edits"] == [{"path": ACL_REL, "kind": "받는 쪽 어댑터", "ref": "V2"}]
            and len(snap["linked_rows"]) == 2 else 9, json.dumps(snap, ensure_ascii=False)[:600]), 0)
    try:
        ra.load_candidate(f, "0" * 12)
        missing: int = 9
    except RuntimeError:
        missing = 0
    expect(fails, "RD-C16 load_candidate 없는 digest → RuntimeError 계열", (missing, ""), 0)
    scope: Path = f / "refactor-scope.md"
    head: str = f"\n## G1 변경 결정 20261004-1930 · 후보 digest {digest}\n\n"
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 바꾼다 · 출처 = 본인 직접(1930)\n", encoding="utf-8")
    expect(fails, "RD-C17 --applied 고른 V 전부 바꾼다 · 승인판 무변 → green", lane.ch("--applied", str(cand_files[-1])), 0,
           "red 0 · applied", f"후보 {digest} → 지금 {now_digest}")
    got = lane.ch("--gate")
    final: str = got[1].split("최종 digest ", 1)[1].split()[0] if "최종 digest " in got[1] else ""
    expect(fails, "RD-C18 --gate 결정 줄 · V 표 · 해소 표 정합 → green + 최종 digest(= 지금 스냅숏 digest)",
           (got[0] if final == now_digest and final else 9, got[1]),
           0, "red 0 · gate")
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 바꾼다 · 출처 = 대리 답 ⓐ x.md:1\n", encoding="utf-8")
    expect(fails, "RD-C19 --gate 밖 동작 V 결정 출처가 대리 → red", lane.ch("--gate"), 2, "대리 불가")
    scope.write_text(lane.scope_base + head, encoding="utf-8")
    expect(fails, "RD-C20 --gate 밖 동작 V 에 결정 줄 없음 → red", lane.ch("--gate"), 2, "V2 밖 동작 V 에 G1 결정 `바꾼다` 줄이 없다")
    scope.write_text(lane.scope_base, encoding="utf-8")
    expect(fails, "RD-C21 --gate G1 변경 결정 절 없음 → red", lane.ch("--gate"), 2, "G1 변경 결정 <시각>")
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 바꾼다 · 출처 = 본인 직접(1930)\n", encoding="utf-8")
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2.replace("| V2 |", "| V1 |"))
    expect(fails, "RD-C22 --gate V2 근거 요지가 V2 를 가리키는 변경 행이 아님 → red", lane.ch("--gate"), 2,
           "V2 근거 M2 #1 가 이 V 를 가리키는")
    lane.spec(V1_TEXT + V2_TEXT.replace("전 → 후: 없는 thing 404 → 410", "전 → 후: 없는 thing 404 → 451"), EDIT_LINE,
              CH_ROW_M1 + CH_ROW_M2)
    expect(fails, "RD-C23 --applied 후보 뒤 V 문면이 바뀜(한 글자) → red", lane.ch("--applied", str(cand_files[-1])), 2,
           "반영 대조 다름 — `V`")
    # 안 바꾼 밖 동작 V — architect 반영(그 V · 딸린 입장 행 · 다른 BC 편집 줄 삭제 · 요지 → 불가 · 변경 미승인)
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 안 바꾼다 · 출처 = 사용자 원문 /x/answers.md:3(1931)\n",
                     encoding="utf-8")
    line_no: int = len((lane.scope_base + head).split("\n"))
    unapproved: str = f"| M2 | 1 | 예외 매핑 흩어짐 | 불가 | 변경 미승인 | refactor-scope.md:{line_no} — G1 결정 안 바꾼다 | — | — |\n"
    adm_v1: str = "".join(ln for ln in V_SPEC_ROWS.splitlines(keepends=True) if "컨트롤러 404 응답" not in ln)  # 리뷰 B #1
    lane.spec(V1_TEXT, "없음\n", CH_ROW_M1 + unapproved, adm=adm_v1)
    expect(fails, "RD-C24 --applied 안 바꾼 V 를 지운 승인판 = 후보 − 그 V 몫(입장 행 포함) · 바뀐 행 = 변경 미승인 → green",
           lane.ch("--applied", str(cand_files[-1])), 0, "red 0 · applied")
    expect(fails, "RD-C25 --gate 안 바꾼 V 는 목록에 없고 요지 = 불가 · 변경 미승인 → green", lane.ch("--gate"), 0, "red 0 · gate")
    lane.spec(V1_TEXT, "없음\n", CH_ROW_M1.replace("| — |\n", "| 되돌리지 않는다 |\n") + unapproved, adm=adm_v1)
    expect(fails, "RD-C26 --applied 해소 판정 표의 다른 행도 바뀜 → red", lane.ch("--applied", str(cand_files[-1])), 2,
           "M1 #1 가 후보 뒤 바뀌었다")
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + unapproved)
    expect(fails, "RD-C27 --gate 안 바꾼 V 가 목록에 남음 → red", lane.ch("--gate"), 2, "V2 는 G1 결정 `안 바꾼다` 인데 바뀌는 것 목록에 남아")
    scope.write_text(scope.read_text(encoding="utf-8") + "- M1 · 사용자 판단 = 위반 · 출처 = 상시 답 x\n", encoding="utf-8")
    expect(fails, "RD-C28 --gate 이번 실행 몫의 옛 상시 답 줄 → 실행 불능(설계 :1355)", lane.ch("--gate"), 1, "상시 답은 걷혔다")
    # g1_confirmed — 이번 실행 몫의 마지막 확정 줄 · 앞 실행 절은 보지 않는다
    scope.write_text(lane.scope_base + f"\n## G1 변경 결정 20261004-1930 · 후보 digest {digest}\n\n"   # 리뷰 B #7 — 결정 절과 결속
                     f"- G1 변경판 확정 20261004-1940 · digest aaaaaaaaaaaa · 후보 {digest}\n"
                     f"- G1 변경판 확정 20261004-1950 · digest bbbbbbbbbbbb · 후보 {digest}\n\n# 앞 실행\n\n"
                     f"- G1 변경판 확정 20261001-0000 · digest cccccccccccc · 후보 {digest}\n", encoding="utf-8")
    got_c = ra.g1_confirmed(f)
    scope.write_text(lane.scope_base + "\n# 앞 실행\n\n- G1 변경판 확정 20261001-0000 · digest cccccccccccc · 후보 dddddddddddd\n",
                     encoding="utf-8")
    expect(fails, "RD-C29 g1_confirmed — 이번 실행 몫 마지막 줄 (시각, digest, 후보) · 앞 실행 절만 있으면 None",
           (0 if got_c == ("20261004-1950", "bbbbbbbbbbbb", digest) and ra.g1_confirmed(f) is None else 9, str(got_c)), 0)
    # --baseline — 창 기준선(head + dirty0 b64)에서 «바뀌는 기대» 실재를 본다
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2)
    head_sha: str = _git(lane.repo, "rev-parse", "HEAD").strip()
    test_file: Path = lane.repo / "application/demo/test/test_policy.py"
    test_file.write_text("def test_rule() -> None:\n    assert 1 == 1\n", encoding="utf-8")
    opened: Path = td / "w3-open.json"
    opened.write_text(json.dumps({"window": 3, "kind": "change", "head": head_sha, "dirty": {}}), encoding="utf-8")
    expect(fails, "RD-C30 지금 시험에서 바뀐 기대 → 기본 changes red", lane.ch(), 2, "원문이 기준 판 케이스에 없다")
    expect(fails, "RD-C31 --baseline 창 open 기록 — 기준선(head 블롭)에 옛 원소 실재 → green", lane.ch("--baseline", str(opened)),
           0, "기준선 창 open 기록 · red 0")
    opened.write_text(json.dumps({"window": 3, "kind": "change", "head": head_sha, "dirty": {
        "application/demo/test/test_policy.py": {"sha": "x", "b64": base64.b64encode(
            b"def test_rule() -> None:\n    assert 2 == 2\n").decode("ascii")}}}), encoding="utf-8")
    expect(fails, "RD-C32 --baseline dirty0(b64)가 head 블롭보다 먼저 → 그 판에 없으면 red", lane.ch("--baseline", str(opened)), 2,
           "원문이 기준 판 케이스에 없다")
    try:
        lane.spec(V1_TEXT.replace("내부 약속", "속 약속"), "없음\n", CH_ROW_M1)
        ra.changes_snapshot(f, lane.repo)
        raised: int = 9
    except RuntimeError:
        raised = 0
    expect(fails, "RD-C33 changes_snapshot 형식 red 명세 → RuntimeError 계열(fail-closed)", (raised, ""), 0)


ADM_HEAD: str = "".join(V_SPEC_ROWS.splitlines(keepends=True)[:2])
ADM_V1_ROW: str = V_SPEC_ROWS.splitlines(keepends=True)[2]
ADM_REST: str = "".join(V_SPEC_ROWS.splitlines(keepends=True)[3:])
BIG_TEST: str = "application/demo/test/test_big.py"
FREE_ROW: str = (f"| 큰 함수 기대 고침 | 정책 계약 | 기대 오류 | test_big | update | coder `{BIG_TEST}::TestBig::test_big` · "
                 f"`{BIG_TEST}::test_other` |\n")
FILE_ROW: str = "| 정책 시험 표지 갱신 | 표지 | — | test_policy | update | coder `application/demo/test/test_policy.py` [markers: slow] |\n"
OUT_ROW: str = ("| 컨트롤러 응답 기대 | HTTP 계약 | 매핑 오류 | test_policy | update | acceptance-tester "
                "`application/demo/test/test_policy.py::test_rule` |\n")
V2_UPDATE: str = V2_TEXT.replace(
    "  - 연산: demo", "  - 시험: 컨트롤러 응답 기대 update(acceptance-tester) application/demo/test/test_policy.py::test_rule\n"
                     "    - 바뀌는 기대: «assert True»\n  - 연산: demo")


def update_rows_cases(fails: "list[str]", td: Path) -> None:
    """k0 v5 §4-4 `update_rows`(운영자 결정 10-04 · 설계 정오 4 — :583 «ⓐ 항목이 그 기대를 고치는 것»의 기계 자료) —
    입장 표 decision `update` 행 전부 · `v` = 딸린 V 또는 null · digest 결속 · `--applied` 는 안 바꾼 V 에만 딸린 행만 빠진다."""
    lane = ChangesLane(td, "upd")
    lane.support()
    f = lane.folder
    v1_item: dict = {"case": "application/demo/test/test_policy.py::test_rule", "owner": "coder", "row": ADM_V1_ROW.strip(),
                     "v": "V1"}

    def rows() -> "list[dict]":
        return ra.changes_snapshot(f, lane.repo)["update_rows"]

    def digest() -> str:
        return ra.snapshot_digest(ra.changes_snapshot(f, lane.repo))

    lane.spec(V2_TEXT, EDIT_LINE, RES_ROWS["M1"] + CH_ROW_M2, adm=ADM_HEAD + ADM_REST)
    got: "list[dict]" = rows()
    expect(fails, "RD-U1 입장 표에 update 행 0 → `update_rows` 빈 목록", (0 if got == [] else 9, str(got)), 0)
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2)
    got, d0 = rows(), digest()
    expect(fails, "RD-U2 V 의 시험 줄에 딸린 update 행 → `v` = 그 V · case = owner/path 의 `경로::케이스` · row = 표 행 전체",
           (0 if got == [v1_item] else 9, str(got)), 0)
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + FREE_ROW)
    got, d_add = rows(), digest()
    free: "list[dict]" = [{"case": f"{BIG_TEST}::TestBig::test_big", "owner": "coder", "row": FREE_ROW.strip(), "v": None},
                          {"case": f"{BIG_TEST}::test_other", "owner": "coder", "row": FREE_ROW.strip(), "v": None}]
    expect(fails, "RD-U3 V 에 딸리지 않은 update 행 → `v` null · 한 행의 케이스 둘 → 항목 둘(표 차례 · `Class::method` 글자 그대로)",
           (0 if got == [v1_item] + free else 9, str(got)), 0)
    expect(fails, "RD-U4 요약 `update 케이스 3(V 밖 2)`", lane.ch(), 0, "update 케이스 3(V 밖 2)", "red 0")
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + FREE_ROW.replace("정책 계약", "정책 계약."))
    d_edit: str = digest()
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2)
    d_del: str = digest()
    expect(fails, "RD-U5 스냅숏 digest 가 update 행 추가 · 글자 변경 · 삭제에 바뀐다(삭제하면 처음 digest 로)",
           (0 if len({d0, d_add, d_edit}) == 3 and d_del == d0 else 9, f"{d0} {d_add} {d_edit} {d_del}"), 0)
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + FILE_ROW)
    got = rows()
    expect(fails, "RD-U6 케이스 주소 없는 update 행(파일만) → case = 파일 경로 한 항목 · v null(케이스 글자 일치에 안 걸린다)",
           (0 if got == [v1_item, {"case": "application/demo/test/test_policy.py", "owner": "coder", "row": FILE_ROW.strip(),
                                   "v": None}] else 9, str(got)), 0)
    # --applied — V 밖 update 행은 한 글자도 같아야 한다 · 안 바꾼 V 에만 딸린 update 행만 빠진다
    scope: Path = f / "refactor-scope.md"
    adm_out: str = V_SPEC_ROWS + OUT_ROW + FREE_ROW
    lane.spec(V1_TEXT + V2_UPDATE, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=adm_out)
    cand_run = lane.ch("--candidate")
    cand_path: Path = sorted((f / "g1").glob("*-candidate.json"))[-1]
    cand: dict = json.loads(cand_path.read_text(encoding="utf-8"))
    cd: str = ra.snapshot_digest(cand)
    expect(fails, "RD-U7 후보 스냅숏에 update_rows(V1 행 · V2 에 딸린 행 · V 밖 행 둘) · digest 에 든다",
           (cand_run[0] if [u["v"] for u in cand["update_rows"]] == ["V1", "V2", None, None] and f"후보 digest {cd}" in cand_run[1]
            else 9, cand_run[1] + str(cand.get("update_rows"))), 0)
    head: str = f"\n## G1 변경 결정 20261004-2150 · 후보 digest {cd}\n\n"
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 바꾼다 · 출처 = 본인 직접(2150)\n", encoding="utf-8")
    expect(fails, "RD-U8 --applied 승인판 무변 → green", lane.ch("--applied", str(cand_path)), 0, "red 0 · applied")
    lane.spec(V1_TEXT + V2_UPDATE, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + OUT_ROW + FREE_ROW.replace("기대 오류", "기대 오류!"))
    expect(fails, "RD-U9 --applied V 밖 update 행 글자 변경 → 반송(red)", lane.ch("--applied", str(cand_path)), 2,
           "반영 대조 다름 — `update_rows`")
    lane.spec(V1_TEXT + V2_UPDATE, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + OUT_ROW)
    expect(fails, "RD-U10 --applied V 밖 update 행 삭제 → 반송(red)", lane.ch("--applied", str(cand_path)), 2,
           "반영 대조 다름 — `update_rows`")
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 안 바꾼다 · 출처 = 본인 직접(2151)\n", encoding="utf-8")
    line_no: int = len((lane.scope_base + head).split("\n"))
    unapproved: str = f"| M2 | 1 | 예외 매핑 흩어짐 | 불가 | 변경 미승인 | refactor-scope.md:{line_no} — G1 결정 안 바꾼다 | — | — |\n"
    kept_adm: str = ADM_HEAD + ADM_V1_ROW + "".join(ADM_REST.splitlines(keepends=True)[1:]) + FREE_ROW
    lane.spec(V1_TEXT, "없음\n", CH_ROW_M1 + unapproved, adm=kept_adm)
    expect(fails, "RD-U11 --applied 안 바꾼 V 에만 딸린 update 행(과 add 행)이 빠진 승인판 → green",
           lane.ch("--applied", str(cand_path)), 0, "red 0 · applied", "update 케이스 3(V 밖 2)")
    lane.spec(V1_TEXT, "없음\n", CH_ROW_M1 + unapproved, adm=ADM_HEAD + ADM_V1_ROW + OUT_ROW
              + "".join(ADM_REST.splitlines(keepends=True)[1:]) + FREE_ROW)
    expect(fails, "RD-U12 --applied 안 바꾼 V 의 update 행을 남김(V 밖 행이 됨) → 반송(red)",
           lane.ch("--applied", str(cand_path)), 2, "반영 대조 다름 — `update_rows`")


CW_RULE: str = "application/demo/test/test_policy.py::test_rule"
CW_GONE: str = "application/demo/test/test_thing_api.py::test_gone"
CW_OLD_CASE: str = "application/demo/test/test_policy.py::test_gone_old"
CW_POLICY: str = "application/demo/test/test_policy.py"
CW_API: str = "application/demo/test/test_thing_api.py"


def _cw_guard():  # noqa: ANN202
    """behavior_guard(창 허용 표 `allow_table`) — 러너가 창 open 기록을 장치와 같은 꼴로 만들 때만 쓴다."""
    import behavior_guard  # noqa: PLC0415
    return behavior_guard


class CwLane:
    """F-B1R-5 창 픽스처 — ChangesLane + G1 확정 기록(후보 · 확정 줄) + behavior 실행 폴더의 창 open · close 기록(장치 판형 칸)."""

    def __init__(self, td: Path, name: str, v_text: str = "", adm: str = "") -> None:
        self.lane = ChangesLane(td, name)
        self.lane.support()
        self.f: Path = self.lane.folder
        self.repo: Path = self.lane.repo
        if v_text:
            self.lane.spec(v_text, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=adm or V_SPEC_ROWS)
        self.run_dir: Path = self.f / "behavior" / "20261004-1900"
        self.run_dir.mkdir(parents=True)
        self.confirm()

    def confirm(self) -> None:
        """지금 명세로 후보 → G1 변경 결정(V2 바꾼다) → G1 변경판 확정 — 창 open 의 `g1_digest` · `allow` 재료."""
        before: "set[Path]" = set((self.f / "g1").glob("*-candidate.json"))
        got = self.lane.ch("--candidate")
        new: "list[Path]" = sorted(set((self.f / "g1").glob("*-candidate.json")) - before)   # 같은 초의 `-2` 이름도 바르게
        if got[0] != 0 or len(new) != 1:
            raise RuntimeError(f"후보 준비 실패(새 후보 파일 {len(new)}): {got[1][-600:]}")
        cand: Path = new[0]
        c: str = ra.snapshot_digest(json.loads(cand.read_text(encoding="utf-8")))
        snap: dict = ra.changes_snapshot(self.f, self.repo)
        self.d: str = ra.snapshot_digest(snap)
        self.allow: dict = _cw_guard().allow_table(snap)
        (self.f / "refactor-scope.md").write_text(
            self.lane.scope_base + f"\n## G1 변경 결정 2026-10-06 09:50 · 후보 digest {c}\n\n"
            "- V2 · 결정 = 바꾼다 · 출처 = 본인 직접(0950)\n"
            f"- G1 변경판 확정 2026-10-06 09:55 · digest {self.d} · 후보 {c}\n", encoding="utf-8")

    def head(self) -> str:
        return _git(self.repo, "rev-parse", "HEAD").strip()

    def commit(self, files: "dict[str, str]", msg: str) -> str:
        for rel, body in files.items():
            (self.repo / rel).write_text(body, encoding="utf-8")
        _git(self.repo, "add", "-A", "application")
        _git(self.repo, "commit", "-qm", msg)
        return self.head()

    def window(self, n: int, head: str, closes: "list[dict] | None" = None, dirty: "dict | None" = None,
               allow: "dict | None" = None, rebinds: "list[dict] | None" = None) -> Path:
        opened: dict = {"window": n, "kind": "change", "run": "20261004-1900", "anchor": "x", "head": head,
                        "opened": "2026-10-06T10:00:00Z", "dirty": dirty or {}, "cases": {}, "pytest": {}, "mode": "refactor",
                        "g1_digest": self.d, "allow": allow if allow is not None else self.allow, "rebinds": rebinds or []}
        (self.run_dir / f"w{n}-open.json").write_text(json.dumps(opened, ensure_ascii=False), encoding="utf-8")
        if closes is not None:
            (self.run_dir / f"w{n}-close.json").write_text(json.dumps(closes, ensure_ascii=False), encoding="utf-8")
        return self.run_dir / f"w{n}-open.json"

    def ch(self, *extra: str) -> "tuple[int, str]":
        return self.lane.ch(*extra)


def _cw_close(verdict: str = "audit", hits: "dict | None" = None, added: "list[str] | None" = None,
              removed: "list[str] | None" = None, at: str = "2026-10-06T11:00:00Z") -> dict:
    return {"closed": at, "verdict": verdict, "approved_hits": hits or {}, "cases_added": added or [],
            "cases_removed": removed or []}


def closed_window_cases(fails: "list[str]", td: Path) -> None:
    """F-B1R-5(설계 `design-B1R5-repair.md` v2 §3 · 사례 1 ~ 15) — 닫힌 변경 창에서 집행이 결속된 원소는 그 창 기준선에서 확인
    (그 창 `g1_digest` 의 확정 줄 → 후보 → `_expected_applied` 로 V 별 원소를 되살리고 `allow_table` 이 open allow 와 같을 때만) ·
    집행된 원소 보존 · 과거 기준선 «읽지 못함»과 쓰려던 기록 손상 = 실행 불능. 단언은 원인 줄(red 한 줄의 V id · 문구) 직접."""
    def red_line(got: "tuple[int, str]", *parts: str) -> bool:
        return any(all(p in ln for p in parts) for ln in got[1].splitlines() if ln.strip().startswith(("red:", "실행 불능")))

    def check(label: str, got: "tuple[int, str]", code: int, must: "tuple[str, ...]" = (),
              lines: "tuple[tuple[str, ...], ...]" = (), not_lines: "tuple[tuple[str, ...], ...]" = ()) -> None:
        bad: "list[tuple[str, ...]]" = [g for g in lines if not red_line(got, *g)] + [g for g in not_lines if red_line(got, *g)]
        expect(fails, label, (got[0] if not bad else 9, got[1] + (f"\n줄 단언 어긋남: {bad}" if bad else "")), code, *must)
    s1_files: "dict[str, str]" = {CW_POLICY: "def test_rule() -> None:\n    assert 1 == 1\n",
                                  CW_API: "def test_gone() -> None:\n    assert 410\n"}
    s1_hits: dict = {CW_RULE: {"old": ["assert True"], "add": 0}}
    v1_red = (f"V1 시험 {CW_RULE} 바뀌는 기대 «assert True» 원문이 기준 판 케이스에 없다",)
    v2_red = (f"V2 시험 {CW_GONE} add 케이스가 기준 판에 이미 있다",)
    kept_v1 = ("닫힌 창 w5 에서 집행된 V1 원소", CW_RULE, "«assert True»", "지금 명세에 없다")

    def s1(name: str, closes: "list[dict] | None" = None, open_next: bool = True, **kw: object) -> "tuple[CwLane, Path | None]":
        """S1(V1 «assert True» → «assert 1 == 1» · V2 test_gone 추가)을 w5 에서 집행 · 커밋 · close → (w6 open)."""
        cw = CwLane(td, name)
        head_a: str = cw.head()
        head_b: str = cw.commit(s1_files, "S1")
        cw.window(5, head_a, closes if closes is not None else [_cw_close(hits=s1_hits, added=[CW_GONE])], **kw)
        return cw, (cw.window(6, head_b) if open_next else None)
    # 1 재현
    cw, w6 = s1("cw1")
    check("RD-W1 S1 닫힘 · S2 열림 · G1′ `changes --baseline w6` → 집행된 V1 · V2 원소는 닫힌 창 w5 기준선 → green · 요약 꼬리",
          cw.ch("--baseline", str(w6)), 0, ("red 0", "닫힌 창 기준선 2(w5)"))
    # 2 집행된 V1 옛 원문을 지금 글로 다시 씀 → 보존 red
    cw.lane.spec(V1_TEXT.replace("«assert True»", "«assert 1 == 1»") + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2)
    check("RD-W2 G1′ 이 집행된 V1 옛 원문을 지금 글(«assert 1 == 1»)로 다시 씀 → red(보존 줄 · V1)", cw.ch("--baseline", str(w6)), 2,
          lines=(kept_v1,), not_lines=(v2_red,))
    # 3 새 V9 가 같은 케이스의 소비된 o 를 적음 → V9 원소 red(⑤)
    v9: str = ("- V9 · 내부 약속 · 근거 M1 #1 · 슬라이스 S2\n  - 전 → 후: rule_0 이 다시 바뀐다\n"
               "  - 시험: 규칙 함수 반환 기대 update(coder) application/demo/test/test_policy.py::test_rule\n"
               "    - 바뀌는 기대: «assert True»\n")
    cw.lane.spec(V1_TEXT + V2_TEXT + v9, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2)
    check("RD-W3 G1′ 새 V9 가 닫힌 창에서 소비된 «assert True» 를 다시 적음 → red(V9 원소 · 열린 창 기준선) · V1 보존은 섬",
          cw.ch("--baseline", str(w6)), 2, lines=((f"V9 시험 {CW_RULE} 바뀌는 기대 «assert True» 원문이 기준 판 케이스에 없다",),),
          not_lines=(kept_v1, v1_red, v2_red))
    # 4 V1 → V7 번호 다시 매김 → 보존 red(V1)
    cw.lane.spec(V1_TEXT.replace("- V1 · ", "- V7 · ") + V2_TEXT, EDIT_LINE, CH_ROW_M1.replace("| V1 |", "| V7 |") + CH_ROW_M2)
    check("RD-W4 집행된 V1 을 G1′ 에서 V7 로 다시 매김 → red(보존 줄 · V1)", cw.ch("--baseline", str(w6)), 2, lines=(kept_v1,))
    # 5 창 사이 G1′
    cw, _w = s1("cw5", open_next=False)
    check("RD-W5 창 사이 G1′(S1 닫힘 · 다음 창 안 엶 · --baseline 없음) → 닫힌 창 w5 기준선 → green", cw.ch(), 0,
          ("red 0", "닫힌 창 기준선 2(w5)"))
    # 6a 정상 흐름 — S1 열린 채
    cw = CwLane(td, "cw6a")
    w5 = cw.window(5, cw.head())
    check("RD-W6a S1 창 열린 채 `--baseline w5` → 과거 창 안 씀 → green(꼬리 없음)", cw.ch("--baseline", str(w5)), 0, ("red 0",))
    # 6b 손으로 만든 불일치 — w5 마지막 close red 인데 w6 기록 있음
    cw, w6 = s1("cw6b", closes=[_cw_close(verdict="red", hits=s1_hits, added=[CW_GONE])])
    check("RD-W6b w5 마지막 close red(닫힌 창 아님) · w6 기록 있음 → red(⑤ · V1 · V2 줄)", cw.ch("--baseline", str(w6)), 2,
          lines=(v1_red, v2_red))
    # 7 remove 케이스 짝
    v2_rm: str = V2_TEXT.replace("  - 연산: demo", "  - 시험: 낡은 404 시험 지움 remove(acceptance-tester) "
                                                 "application/demo/test/test_policy.py::test_gone_old\n"
                                                 "    - 바뀌는 기대: «assert True»\n  - 연산: demo")
    cw = CwLane(td, "cw7")
    head_a = cw.commit({CW_POLICY: "def test_rule() -> None:\n    assert True\n\n\ndef test_gone_old() -> None:\n    assert True\n"},
                       "base")
    cw.lane.spec(V1_TEXT + v2_rm, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + REMOVE_V2)
    cw.confirm()
    head_b = cw.commit({CW_POLICY: "def test_rule() -> None:\n    assert 1 == 1\n",
                        CW_API: "def test_gone() -> None:\n    assert 410\n"}, "S1")
    cw.window(5, head_a, [_cw_close(hits={CW_RULE: {"old": ["assert True"], "add": 0},
                                          CW_OLD_CASE: {"old": ["assert True"], "add": 0}},
                                    added=[CW_GONE], removed=[CW_OLD_CASE])])
    w6 = cw.window(6, head_b)
    check("RD-W7 닫힌 창 w5 에서 지운 remove 케이스 · 더한 add 케이스 · 바꾼 옛 원문 → w5 기준선 → green", cw.ch("--baseline", str(w6)), 0,
          ("red 0", "닫힌 창 기준선 4(w5)"))
    # 8 닫힌 창 기준선이 dirty b64 원문
    cw = CwLane(td, "cw8")
    head_a = cw.commit({CW_POLICY: "def test_rule() -> None:\n    assert 0 == 0\n"}, "base")
    head_b = cw.commit(s1_files, "S1")
    dirty: dict = {CW_POLICY: {"sha": "x", "b64": base64.b64encode(b"def test_rule() -> None:\n    assert True\n").decode("ascii")}}
    cw.window(5, head_a, [_cw_close(hits=s1_hits, added=[CW_GONE])], dirty=dirty)
    w6 = cw.window(6, head_b)
    check("RD-W8 닫힌 창 w5 기준선의 dirty b64(head 블롭엔 없음)에서 «assert True» 를 읽는다 → green", cw.ch("--baseline", str(w6)), 0,
          ("red 0", "닫힌 창 기준선 2(w5)"))
    # 9 같은 케이스 두 V(V1 «assert True» · V3 «assert 0 == 0») · V1 만 소비 · G1′ 이 V3 기대를 «assert True» 로
    v3: str = ("- V3 · 내부 약속 · 근거 M1 #1 · 슬라이스 S2\n  - 전 → 후: rule_0 이 한 번 더 바뀐다\n"
               "  - 시험: 규칙 함수 반환 기대 update(coder) application/demo/test/test_policy.py::test_rule\n"
               "    - 바뀌는 기대: «assert 0 == 0»\n")
    cw = CwLane(td, "cw9")
    head_a = cw.commit({CW_POLICY: "def test_rule() -> None:\n    assert True\n    assert 0 == 0\n"}, "base")
    cw.lane.spec(V1_TEXT + V2_TEXT + v3, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2)
    cw.confirm()
    head_b = cw.commit({CW_POLICY: "def test_rule() -> None:\n    assert 1 == 1\n    assert 0 == 0\n",
                        CW_API: "def test_gone() -> None:\n    assert 410\n"}, "S1")
    cw.window(5, head_a, [_cw_close(hits=s1_hits, added=[CW_GONE])])
    w6 = cw.window(6, head_b)
    check("RD-W9a 같은 케이스 두 V · V1 만 소비 · 명세 무변 → green(V1 · V2 는 w5 · V3 는 열린 창)", cw.ch("--baseline", str(w6)), 0,
          ("red 0", "닫힌 창 기준선 2(w5)"))
    cw.lane.spec(V1_TEXT + V2_TEXT + v3.replace("«assert 0 == 0»", "«assert True»"), EDIT_LINE, CH_ROW_M1 + CH_ROW_M2)
    check("RD-W9 G1′ 이 아직 집행 안 된 V3 의 기대를 V1 이 소비한 «assert True» 로 → red(V3 원소)", cw.ch("--baseline", str(w6)), 2,
          lines=((f"V3 시험 {CW_RULE} 바뀌는 기대 «assert True» 원문이 기준 판 케이스에 없다",),), not_lines=(kept_v1, v1_red))
    # 10 close 뒤 rebind(close.closed ≤ rebind.at) · 그 뒤 close 없음 → 그 창 증거 안 씀
    cw, w6 = s1("cw10", closes=[_cw_close(hits=s1_hits, added=[CW_GONE], at="2026-10-06T11:00:00Z")],
                rebinds=[{"at": "2026-10-06T11:00:00Z", "from": "a", "to": "b"}])
    check("RD-W10 w5 마지막 close 가 마지막 rebind 보다 엄격히 뒤가 아님 → 그 창 증거 안 씀 → red(⑤ · V1 · V2)",
          cw.ch("--baseline", str(w6)), 2, lines=(v1_red, v2_red))
    # 11 마지막 close 차례
    cw, w6 = s1("cw11a", closes=[_cw_close(verdict="red", at="2026-10-06T10:30:00Z"), _cw_close(hits=s1_hits, added=[CW_GONE])])
    check("RD-W11a w5 close red → audit(마지막 audit) → 씀 → green", cw.ch("--baseline", str(w6)), 0, ("red 0", "닫힌 창 기준선 2(w5)"))
    cw, w6 = s1("cw11b", closes=[_cw_close(hits=s1_hits, added=[CW_GONE], at="2026-10-06T10:30:00Z"), _cw_close(verdict="red")])
    check("RD-W11b w5 close audit → red(마지막 red) → 안 씀 → red(⑤)", cw.ch("--baseline", str(w6)), 2, lines=(v1_red, v2_red))
    # 12 창 번호 w2 · w10 정수 차례 — 같은 원소를 둘 다 집행했다고 적고 w2 기준선에는 원문이 없다
    cw = CwLane(td, "cw12")
    head_a = cw.head()
    head_x = cw.commit({CW_POLICY: "def test_rule() -> None:\n    assert 0 == 0\n"}, "x")
    head_b = cw.commit(s1_files, "S1")
    cw.window(2, head_x, [_cw_close(hits=s1_hits, added=[CW_GONE], at="2026-10-06T10:20:00Z")])
    cw.window(10, head_a, [_cw_close(hits=s1_hits, added=[CW_GONE])])
    w11 = cw.window(11, head_b)
    check("RD-W12 w2 · w10 둘 다 집행 기록 → 번호가 큰 w10(정수 차례) 기준선 → green · 꼬리 w10", cw.ch("--baseline", str(w11)), 0,
          ("red 0", "닫힌 창 기준선 2(w10)"))
    # 13 update 의 기대 추가만 집행 · 뒤에서 그 케이스가 지워짐 → ④ 그 창 기준선에 케이스 있음
    v1_add: str = V1_TEXT.replace("«assert True»", "기대 추가 1")
    cw = CwLane(td, "cw13", v_text=v1_add + V2_TEXT)
    head_a = cw.head()
    head_b = cw.commit({CW_POLICY: "X: int = 1\n", CW_API: "def test_gone() -> None:\n    assert 410\n"}, "S1+삭제")
    cw.window(5, head_a, [_cw_close(hits={CW_RULE: {"old": [], "add": 1}}, added=[CW_GONE])])
    w6 = cw.window(6, head_b)
    check("RD-W13 V1 기대 추가만 w5 에서 집행 · 그 뒤 케이스 지워짐 → ④ w5 기준선에 케이스 있음 → green", cw.ch("--baseline", str(w6)), 0,
          ("red 0", "닫힌 창 기준선 2(w5)"))
    # 14 쓰려던 기록 손상 · dirty b64 누락 → 실행 불능
    cw, w6 = s1("cw14a")
    (cw.run_dir / "w5-close.json").write_text("{깨진", encoding="utf-8")
    check("RD-W14a 쓰려던 w5 close 가 JSON 아님 → 실행 불능(exit 1 · 파일)", cw.ch("--baseline", str(w6)), 1, ("w5-close.json",))
    cw, w6 = s1("cw14b", dirty={CW_POLICY: {"sha": "x"}})
    check("RD-W14b 쓰려던 w5 기준선 dirty 항목에 b64 없음 → 실행 불능(exit 1 · 파일 · 칸)", cw.ch("--baseline", str(w6)), 1,
          ("w5-open.json", "b64"))
    # 15 open allow 를 손으로 고침 → 되살린 판과 다름 → 그 창 증거 안 씀
    cw = CwLane(td, "cw15")
    head_a = cw.head()
    head_b = cw.commit(s1_files, "S1")
    tampered: dict = json.loads(json.dumps(cw.allow))
    tampered["approved_cases"][CW_RULE]["expect_old"] = ["assert True", "assert 2 == 2"]
    cw.window(5, head_a, [_cw_close(hits=s1_hits, added=[CW_GONE])], allow=tampered)
    w6 = cw.window(6, head_b)
    check("RD-W15 w5 open allow 를 손으로 고침(되살린 판의 allow_table 과 다름) → 그 창 증거 안 씀 → red(⑤ · V1 · V2)",
          cw.ch("--baseline", str(w6)), 2, lines=(v1_red, v2_red))


GP_ADM_KEPT: str = "".join(ln for ln in V_SPEC_ROWS.splitlines(keepends=True) if "컨트롤러 404 응답" not in ln)
GP_V3: str = ("- V3 · 내부 약속 · 근거 M2 #2 · 슬라이스 S3\n"
              "  - 전 → 후: 예외 번역 함수 이름 x → y\n"
              "  - 시험: 규칙 함수 반환 기대 update(coder) application/demo/test/test_policy.py::test_rule\n"
              "    - 바뀌는 기대: «assert True»\n")
GP_M1: str = "| M1 | 1 | 규칙 이름 흩어짐 | 변경 | — | V1 | M1 — 규칙 함수 이름 통일 | — |\n"
GP_M1_PART1: str = "| M1 | 1 | 규칙 이름 흩어짐 | 변경 | — | V1 | M1 — 규칙 함수 이름 통일 | 남긴 정리는 이름만 바꾼다 |\n"
GP_M1_PART2: str = f"| M1 | 2 | 받는 쪽 이름 흩어짐 | 불가 | 편집 범위 밖 | {ACL_REL}:1 — 받는 쪽 어댑터 이름이 바뀐다 | — | — |\n"
GP_M2_1: str = "| M2 | 1 | 예외 매핑 흩어짐 | 변경 | — | V1 · V2 | M2 — 컨트롤러 예외 매핑 정리 | — |\n"
GP_M2_2: str = "| M2 | 2 | 예외 번역 이름 | 변경 | — | V3 | 예외를 매핑 표 한 곳에서 번역한다 | — |\n"
GP_M2_SOLO: str = "| M2 | 1 | 예외 매핑 흩어짐 | 변경 | — | V2 | M2 — 컨트롤러 예외 매핑 정리 | — |\n"
GP_M2_BOTH2: str = "| M2 | 2 | 예외 번역 이름 | 변경 | — | V2 | 예외를 매핑 표 한 곳에서 번역한다 | — |\n"
GP_M2_3: str = "| M2 | 3 | 예외 문서 흩어짐 | 해소 | — | — | M2 — 컨트롤러 예외 매핑 정리 | — |\n"
GP_WHY: str = "남긴 정리(V3)는 뺀 요지 #1 과 엮이지 않는다"
GP_RECON_PART: str = ("- M2 · 결정 = 요지 축소 · 남긴 요지 = #2 · 뺀 요지 = #1 → ⓑ · 남김 근거 = 사용자 선택 · "
                      "출처 = 본인 직접(0100)\n")
GP_RECON_WHOLE: str = "- M2 · 결정 = ⓑ · 사유 = G1 안 바꾼다 · 출처 = 본인 직접(0100)\n"
GP_G0_RECON_M1: str = ("\n## ⓐ 재상정 20261005-2300 — STOP_FOR_USER_APPROVAL(부분·불가)\n\n"
                       "- M1 · 결정 = 요지 축소 · 남긴 요지 = #1 · 뺀 요지 = #2 → 별도 요청 · 남김 근거 = 해소 판정 표 · "
                       "출처 = 본인 직접(2300)\n")
GP_A: str = "바뀔 수 있는 행은 안 바꾼 V 요지의 `불가 · 변경 미승인` 뿐"
GP_FILL_ONLY: str = "빈 칸을 채우는 것만 받는다"
GP_REASON: str = "부분 항목의 변경 행에 «되돌리지 않는 이유»가 없다"


def g1_partial_cases(fails: "list[str]", td: Path) -> None:
    """B1R 수리(설계 v3.1 §1-1 · §1-5 · §3-1) — G1 이 «부분»으로 만든 항목의 남은 정리 행 «되돌리지 않는 이유»(⑤ `changes --applied`
    가 받는 변경 하나 · ⑥ `resolution --gate` 무변) · 곁 자료 결속. 기본 꼴: M1 #1 `변경 · V1` · M2 #1 `변경 · V1 · V2` · M2 #2
    `변경 · V3` 에서 V2 안 바꾼다 → 반영(M2 #1 `불가 · 변경 미승인` · 막는 것 = G1 결정 줄). 단언은 줄 단위(그 행 · 문구).
    고치기 전 판 실측은 설계 §3-1 얼린 표(`I/q/b1r3-probe*.log` · `br-pre-probe.log`)."""
    def unapproved_row(no: int, gist: str, line_no: int) -> str:
        return f"| M2 | {no} | {gist} | 불가 | 변경 미승인 | refactor-scope.md:{line_no} — G1 결정 안 바꾼다 | — | — |\n"

    def add_body(lane: ChangesLane, extra: str) -> None:
        if extra:
            sp: Path = lane.folder / "design-spec.md"
            sp.write_text(sp.read_text(encoding="utf-8").replace("## 5. 슬라이스 0 해소 판정", extra + "## 5. 슬라이스 0 해소 판정", 1),
                          encoding="utf-8")

    def make(name: str, vs: str, rows: str, recon: str, g0: str = "", body: str = "") -> "tuple[ChangesLane, Path, int]":
        """후보 시점 명세 → --candidate(후보 스냅숏 + 곁 자료) → refactor-scope 에 G1 결정 절(V2 안 바꾼다) + ⓐ 재상정 절."""
        lane = ChangesLane(td, name)
        lane.support()
        (lane.folder / "refactor-scope.md").write_text(lane.scope_base + g0, encoding="utf-8")
        lane.spec(vs, EDIT_LINE, rows)
        add_body(lane, body)
        got = lane.ch("--candidate")
        if got[0] != 0:
            raise RuntimeError(f"후보 준비 실패: {got[1][-600:]}")
        cand: Path = sorted((lane.folder / "g1").glob("*-candidate.json"))[-1]
        digest: str = ra.snapshot_digest(json.loads(cand.read_text(encoding="utf-8")))
        pre: str = lane.scope_base + g0 + f"\n## G1 변경 결정 2026-10-06 01:00 · 후보 digest {digest}\n\n"
        (lane.folder / "refactor-scope.md").write_text(
            pre + "- V2 · 결정 = 안 바꾼다 · 출처 = 본인 직접(0100)\n\n## ⓐ 재상정 20261006-0100 — G1 안 바꾼다\n\n" + recon,
            encoding="utf-8")
        return lane, cand, len(pre.split("\n"))

    def reflect(lane: ChangesLane, rows: str, vs: str = V1_TEXT + GP_V3, body: str = "") -> None:
        lane.spec(vs, "없음\n", rows, adm=GP_ADM_KEPT)
        add_body(lane, body)

    def check(label: str, got: "tuple[int, str]", code: int, must: "tuple[str, ...]" = (),
              must_not: "tuple[str, ...]" = (), lines: "tuple[tuple[str, ...], ...]" = ()) -> None:
        """`lines` = 조각 묶음마다 그 조각이 모두 **같은 red 한 줄** 안에 있어야 한다(출력 전체에서 따로 찾지 않는다)."""
        bad: "list[str]" = [n for n in must_not if n in got[1]]
        reds: "list[str]" = [ln.strip() for ln in got[1].splitlines() if ln.strip().startswith("red:")]
        unbound: "list[tuple[str, ...]]" = [g for g in lines if not any(all(p in ln for p in g) for ln in reds)]
        note: str = (f"\n금지 문구: {bad}" if bad else "") + (f"\n한 줄에 묶이지 않음: {unbound}" if unbound else "")
        expect(fails, label, (got[0] if not bad and not unbound else 9, got[1] + note), code, *must)

    def five(lane: ChangesLane, cand: Path) -> "tuple[int, str]":
        return lane.ch("--applied", str(cand))

    def six(lane: ChangesLane) -> "tuple[int, str]":
        return run(lane.repo, "resolution", str(lane.folder), "--gate")
    vs3: str = V1_TEXT + V2_TEXT + GP_V3
    filled2: str = GP_M2_2.replace("| — |\n", f"| {GP_WHY} |\n")
    # 1 · 2 · 3 · 7
    lane, cand, ln = make("gp1", vs3, GP_M1 + GP_M2_1 + GP_M2_2, GP_RECON_PART)
    blocked1: str = unapproved_row(1, "예외 매핑 흩어짐", ln)
    reflect(lane, GP_M1 + blocked1 + GP_M2_2)
    check("RD-G1 ⑤ G1 이 부분으로 만든 항목 · 남은 행 이유 `—` → green(이유 의무는 ⑥ 몫) · 요약 `G1 이 부분으로 만든 항목 1`",
          five(lane, cand), 0, ("red 0 · applied", "G1 이 부분으로 만든 항목 1"))
    check("RD-G1b ⑥ 같은 꼴 → red(M2 #2 이유 없음 · ⑥ 무변)", six(lane), 2, (f"M2 #2 {GP_REASON}",))
    reflect(lane, GP_M1 + blocked1 + filled2)
    check("RD-G2 ⑤ 남은 정리 행(M2 #2) 이유 칸 빈 칸 → 채움 → green(예외 — 조건 넷 성립)", five(lane, cand), 0,
          ("red 0 · applied", "G1 이 부분으로 만든 항목 1"))
    check("RD-G2b ⑥ 같은 꼴 → green", six(lane), 0, ("red 0 · gate",))
    reflect(lane, GP_M1 + blocked1 + filled2.replace("| 예외를 매핑 표 한 곳에서 번역한다 |", "| 컨트롤러 예외 매핑 정리 |"))
    check("RD-G3 ⑤ 이유 채움 + 처방 앵커 바꿈 → red(그 행 · 이유 칸만 받는다는 문구)", five(lane, cand), 2,
          ("해소 판정 표 M2 #2 가 후보 뒤 바뀌었다 — G1 이 «부분»으로 만든 항목의 남은 정리 행은 «되돌리지 않는 이유» 칸만 빈 칸에서 "
           "채울 수 있다",))
    check("RD-G3b ⑥ 같은 꼴 → green(앵커 글은 본문에 있음)", six(lane), 0, ("red 0 · gate",))
    reflect(lane, GP_M1 + blocked1.replace("| — | — |\n", f"| — | {GP_WHY} |\n") + filled2)
    check("RD-G7 ⑤ 영향 행(M2 #1 불가)의 이유 칸 채움 → red(그 행만 — M2 #2 이유 채움은 받음)", five(lane, cand), 2,
          ("안 바꾼 V 의 요지 M2 #1 — 처방 앵커 · 되돌리지 않는 이유는 `—` 로 둔다",), ("해소 판정 표 M2 #2",))
    check("RD-G7b ⑥ 같은 꼴 → red(M2 #1 불가 행 · 무변)", six(lane), 2, ("M2 #1 불가 행의 처방 앵커·되돌리지 않는 이유는 `—` 로 둔다",))
    # 4 — 후보 때 이미 부분인 M1 의 이유 고쳐 씀(조건 1 실패)
    lane, cand, ln = make("gp4", V1_TEXT + V2_TEXT, GP_M1_PART1 + GP_M1_PART2 + GP_M2_SOLO, GP_RECON_WHOLE, g0=GP_G0_RECON_M1)
    reflect(lane, GP_M1_PART1.replace("이름만 바꾼다", "이름만 바꾼다(G1 뒤 고쳐 씀)") + GP_M1_PART2
            + unapproved_row(1, "예외 매핑 흩어짐", ln), vs=V1_TEXT)
    check("RD-G4 ⑤ 후보 때 이미 부분인 M1 #1 이유 고쳐 씀 → red(그 행 · 지금 문구 + 빈 칸 채움만 받는다) · 부분으로 만든 항목 0",
          five(lane, cand), 2, ("G1 이 부분으로 만든 항목 0",),
          lines=((f"해소 판정 표 M1 #1 가 후보 뒤 바뀌었다 — {GP_A} — «되돌리지 않는 이유»는", GP_FILL_ONLY),))
    check("RD-G4b ⑥ 같은 꼴 → green", six(lane), 0, ("red 0 · gate",))
    # 5 — 해소 그대로인 M1 의 이유 채움(조건 2 실패)
    lane, cand, ln = make("gp5", V1_TEXT + V2_TEXT, GP_M1 + GP_M2_SOLO, GP_RECON_WHOLE)
    reflect(lane, GP_M1.replace("| — |\n", f"| {GP_WHY} |\n") + unapproved_row(1, "예외 매핑 흩어짐", ln), vs=V1_TEXT)
    check("RD-G5 ⑤ 해소 그대로인 M1 #1 이유 채움 → red(그 행 · 빈 칸 채움만 받는다)", five(lane, cand), 2,
          lines=(("해소 판정 표 M1 #1 가 후보 뒤 바뀌었다", GP_A, GP_FILL_ONLY),))
    check("RD-G5b ⑥ 같은 꼴 → green", six(lane), 0, ("red 0 · gate",))
    # 6 — 요지 모두 V2 → 항목 불가
    lane, cand, ln = make("gp6", V1_TEXT + V2_TEXT, GP_M1 + GP_M2_SOLO + GP_M2_BOTH2, GP_RECON_WHOLE)
    reflect(lane, GP_M1 + unapproved_row(1, "예외 매핑 흩어짐", ln) + unapproved_row(2, "예외 번역 이름", ln), vs=V1_TEXT)
    check("RD-G6 ⑤ 요지 모두 안 바꾼 V → 항목 불가 · 이유 `—` → green · 부분으로 만든 항목 0", five(lane, cand), 0,
          ("red 0 · applied", "G1 이 부분으로 만든 항목 0"))
    check("RD-G6b ⑥ 같은 꼴 → green", six(lane), 0, ("red 0 · gate",))
    # 8′(갑) — V3 몫 문장이 V2 처방과 한 문단 → 문단째 지움 → V3 몫 문장만 되살림 + 이유 채움
    v3_sentence: str = "예외 번역 함수 이름을 y 로 바꾼다"
    row2a: str = GP_M2_2.replace("예외를 매핑 표 한 곳에서 번역한다", v3_sentence)
    lane, cand, ln = make("gp8a", vs3, GP_M1 + GP_M2_1 + row2a, GP_RECON_PART,
                          body=f"**M2 처방** 없는 thing 은 404 대신 410 을 돌려준다. {v3_sentence}.\n\n")
    reflect(lane, GP_M1 + unapproved_row(1, "예외 매핑 흩어짐", ln) + row2a)
    check("RD-G8a ⑤ (갑) 문단째 지움 · 이유 `—` → green", five(lane, cand), 0, ("red 0 · applied",))
    check("RD-G8a2 ⑥ 같은 꼴 → red(앵커 원문 없음 + 이유 없음)", six(lane), 2,
          (f"M2 #2 처방 앵커 원문이 표 밖 명세 본문에 없다: «{v3_sentence}»", f"M2 #2 {GP_REASON}"))
    check("RD-G8a3 changes --gate 같은 꼴 → green", lane.ch("--gate"), 0, ("red 0 · gate",))
    reflect(lane, GP_M1 + unapproved_row(1, "예외 매핑 흩어짐", ln) + row2a.replace("| — |\n", f"| {GP_WHY} |\n"),
            body=f"**M2 #2 처방** {v3_sentence}.\n\n")
    check("RD-G8b ⑤ (갑) V3 몫 문장만 되살림 + 이유 채움 → green", five(lane, cand), 0, ("red 0 · applied",))
    check("RD-G8b2 ⑥ 같은 꼴 → green", six(lane), 0, ("red 0 · gate",))
    check("RD-G8b3 changes --gate 같은 꼴 → green", lane.ch("--gate"), 0, ("red 0 · gate",))
    # 8″(을) — 앵커가 거절한 V2 의 처방 글 그 자체 → 반영으로 사라짐(되살리지 않음) → ⑥ 멈춤
    v2_sentence: str = "없는 thing 은 404 대신 410 을 돌려준다"
    row2b: str = GP_M2_2.replace("예외를 매핑 표 한 곳에서 번역한다", v2_sentence)
    lane, cand, ln = make("gp8c", vs3, GP_M1 + GP_M2_1 + row2b, GP_RECON_PART, body=f"**M2 처방** {v2_sentence}.\n\n")
    reflect(lane, GP_M1 + unapproved_row(1, "예외 매핑 흩어짐", ln) + row2b.replace("| — |\n", f"| {GP_WHY} |\n"))
    check("RD-G8c ⑤ (을) 이유 채움은 받음 → green", five(lane, cand), 0, ("red 0 · applied",))
    check("RD-G8c2 ⑥ (을) 앵커가 거절한 V2 처방 글 → red(멈춤 · G1′)", six(lane), 2,
          (f"M2 #2 처방 앵커 원문이 표 밖 명세 본문에 없다: «{v2_sentence}»",))
    # 9 — 후보 때 이미 찬 이유를 G1 뒤 고쳐 씀(조건 3 실패)
    pre_why: str = "후보 때 미리 쓴 이유"
    row2c: str = GP_M2_2.replace("| — |\n", f"| {pre_why} |\n")
    lane, cand, ln = make("gp9", vs3, GP_M1 + GP_M2_1 + row2c, GP_RECON_PART)
    reflect(lane, GP_M1 + unapproved_row(1, "예외 매핑 흩어짐", ln) + row2c.replace(pre_why, GP_WHY))
    check("RD-G9 ⑤ 후보 때 찬 이유를 고쳐 씀 → red(그 행 · 빈 칸 채움만 받는다)", five(lane, cand), 2,
          lines=(("해소 판정 표 M2 #2 가 후보 뒤 바뀌었다", GP_A, GP_FILL_ONLY),))
    check("RD-G9b ⑥ 같은 꼴 → green", six(lane), 0, ("red 0 · gate",))
    # 12 — 사례 9 의 지금 표 그대로 · 곁 자료의 후보 이유만 `—` 로 바꿈(결속 다름 → 실행 불능)
    side: Path = cand.with_name(cand.name[:-len(".json")] + "-resolution.json")
    data: dict = json.loads(side.read_text(encoding="utf-8"))
    data["rows"] = [r[:7] + ["—"] if r[:2] == ["M2", "2"] else r for r in data["rows"]]
    side.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    check("RD-G12 ⑤ 곁 자료 해소 표를 후보 뒤 고침(후보 이유 → `—`) → 실행 불능(결속 다름 · 새 후보로 재상정)", five(lane, cand), 1,
          ("후보 곁 자료의 해소 판정 표가 후보 결속", "새 후보로 재상정한다"))
    # 10a · 10b · 10c — 조건 4 실패 · 중복
    lane, cand, ln = make("gp10a", vs3, GP_M1 + GP_M2_1 + GP_M2_2 + GP_M2_3,
                          GP_RECON_PART.replace("남긴 요지 = #2 · 뺀 요지 = #1", "남긴 요지 = #2 · 뺀 요지 = #1 · #3"))
    reflect(lane, GP_M1 + unapproved_row(1, "예외 매핑 흩어짐", ln) + filled2
            + f"| M2 | 3 | 예외 문서 흩어짐 | 불가 | 편집 범위 밖 | {ACL_REL}:1 — 받는 쪽 어댑터 문서가 바뀐다 | — | — |\n")
    check("RD-G10a ⑤ 영향 행 밖 M2 #3 이 불가로 바뀜 + M2 #2 이유 채움 → red 두 행 각각(예외 안 섬)", five(lane, cand), 2,
          lines=((f"해소 판정 표 M2 #3 가 후보 뒤 바뀌었다 — {GP_A}",),
                 ("해소 판정 표 M2 #2 가 후보 뒤 바뀌었다", GP_A, GP_FILL_ONLY)))
    check("RD-G10a2 ⑥ 같은 꼴 → green", six(lane), 0, ("red 0 · gate",))
    lane, cand, ln = make("gp10b", vs3, GP_M1 + GP_M2_1 + GP_M2_2,
                          GP_RECON_PART.replace("남긴 요지 = #2", "남긴 요지 = #2 · #3"))
    reflect(lane, GP_M1 + unapproved_row(1, "예외 매핑 흩어짐", ln) + filled2 + GP_M2_3.replace("| — |\n", f"| {GP_WHY} |\n"))
    check("RD-G10b ⑤ 그 항목에 새 행 M2 #3 추가 + M2 #2 이유 채움 → red 두 행 각각(행이 늘었다 · 예외 안 섬)", five(lane, cand), 2,
          lines=(("해소 판정 표 M2 #3 가 후보 뒤 바뀌었다 — 후보에 없던 행이 생겼다", GP_A),
                 ("해소 판정 표 M2 #2 가 후보 뒤 바뀌었다", GP_A, GP_FILL_ONLY)))
    lane, cand, ln = make("gp10b2", vs3, GP_M1 + GP_M2_1 + GP_M2_2 + GP_M2_3, GP_RECON_PART)
    reflect(lane, GP_M1 + unapproved_row(1, "예외 매핑 흩어짐", ln) + filled2)
    check("RD-G10b2 ⑤ 후보의 M2 #3 을 지움 + M2 #2 이유 채움 → red 두 행 각각(행이 줄었다 · 예외 안 섬)", five(lane, cand), 2,
          lines=(("해소 판정 표 M2 #3 가 후보 뒤 바뀌었다 — 후보에 있던 행이 빠졌다", GP_A),
                 ("해소 판정 표 M2 #2 가 후보 뒤 바뀌었다", GP_A, GP_FILL_ONLY)))
    lane, cand, ln = make("gp10c", vs3, GP_M1 + GP_M2_1 + GP_M2_2, GP_RECON_PART)
    reflect(lane, GP_M1 + unapproved_row(1, "예외 매핑 흩어짐", ln) + filled2 + filled2)
    check("RD-G10c ⑤ 지금 표에 같은 키 M2 #2 두 행 → red(중복 · 반영 대조 불가)", five(lane, cand), 2,
          ("지금 해소 판정 표 M2 #2 가 둘 이상이다 — 반영 대조를 할 수 없다",))
    check("RD-G10c2 ⑥ 같은 꼴 → red(요지# 겹침 · 무변)", six(lane), 2, ("M2 요지# 가 1 이상 정수가 아니거나 항목 안에서 겹친다",))
    lane, cand, ln = make("gp10d", vs3, GP_M1 + GP_M2_1 + GP_M2_2 + GP_M2_2, GP_RECON_PART)
    reflect(lane, GP_M1 + unapproved_row(1, "예외 매핑 흩어짐", ln) + filled2)
    check("RD-G10d ⑤ 후보 곁 자료 표에 같은 키 M2 #2 두 행 → red(중복 · 새 후보로 재상정)", five(lane, cand), 2,
          ("후보 곁 자료 해소 판정 표 M2 #2 가 둘 이상이다 — 반영 대조를 할 수 없다 — 새 후보로 재상정한다",))
    # 11 — 남은 정리 행이 `해소`
    row2h: str = "| M2 | 2 | 예외 번역 이름 | 해소 | — | — | 예외를 매핑 표 한 곳에서 번역한다 | — |\n"
    lane, cand, ln = make("gp11", V1_TEXT + V2_TEXT, GP_M1 + GP_M2_1 + row2h, GP_RECON_PART)
    reflect(lane, GP_M1 + unapproved_row(1, "예외 매핑 흩어짐", ln) + row2h.replace("| — |\n", f"| {GP_WHY} |\n"), vs=V1_TEXT)
    check("RD-G11 ⑤ 남은 정리 행이 해소 · 이유 채움 → green", five(lane, cand), 0, ("red 0 · applied", "G1 이 부분으로 만든 항목 1"))
    check("RD-G11b ⑥ 같은 꼴 → green", six(lane), 0, ("red 0 · gate",))
    # 13 · 14 — 결속 같음 / 옛 후보(결속 칸 없음)
    lane, cand, ln = make("gp13", vs3, GP_M1 + GP_M2_1 + GP_M2_2, GP_RECON_PART)
    snap13: dict = json.loads(cand.read_text(encoding="utf-8"))
    side13: dict = json.loads(cand.with_name(cand.name[:-len(".json")] + "-resolution.json").read_text(encoding="utf-8"))
    reflect(lane, GP_M1 + unapproved_row(1, "예외 매핑 흩어짐", ln) + filled2)
    bound13: bool = snap13.get("resolution_rows_digest") == hashlib.sha256(json.dumps(
        side13.get("rows"), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    got = five(lane, cand)
    check("RD-G13 ⑤ 후보 결속 칸 = 곁 자료 rows sha256 · 곁 자료 무변 → green(예외 성립)",
          (got[0] if bound13 else 9, got[1]), 0, ("red 0 · applied", "G1 이 부분으로 만든 항목 1"))
    lane, cand, _ln = make("gp14", vs3, GP_M1 + GP_M2_1 + GP_M2_2, GP_RECON_PART)
    snap14: dict = json.loads(cand.read_text(encoding="utf-8"))
    snap14.pop("resolution_rows_digest", None)                     # 옛 도구가 만든 후보 꼴 — 결속 칸 없음
    cand.write_text(json.dumps(snap14, ensure_ascii=False, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    old_digest: str = ra.snapshot_digest(snap14)
    side14: Path = cand.with_name(cand.name[:-len(".json")] + "-resolution.json")
    data = json.loads(side14.read_text(encoding="utf-8"))
    data["candidate"] = old_digest
    side14.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    scope14: Path = lane.folder / "refactor-scope.md"
    text14: str = scope14.read_text(encoding="utf-8")
    scope14.write_text(re.sub(r"후보 digest [0-9a-f]{12}", f"후보 digest {old_digest}", text14), encoding="utf-8")
    ln14: int = next(i for i, s in enumerate(scope14.read_text(encoding="utf-8").split("\n"), 1) if s.startswith("- V2 · 결정"))
    reflect(lane, GP_M1 + unapproved_row(1, "예외 매핑 흩어짐", ln14) + filled2)
    check("RD-G14 ⑤ 옛 후보(결속 칸 없음) → 예외 끔 · red(그 행 끝 «옛 후보 — 재상정») · 부분으로 만든 항목 0", five(lane, cand), 2,
          (f"해소 판정 표 M2 #2 가 후보 뒤 바뀌었다 — {GP_A} — 이 후보에는 곁 자료 결속이 없다(옛 후보): 새 후보로 재상정한다",
           "G1 이 부분으로 만든 항목 0"))


def g1_time_cases(fails: "list[str]", td: Path) -> None:
    """T12 통합 발견 A2 — G1 기록의 `<시각>` 은 ` · ` 앞까지(공백 든 `2026-10-04 19:30` 도 읽는다) · 시각 없는 줄은 못 읽는다."""
    lane = ChangesLane(td, "g1t")
    lane.support()
    f = lane.folder
    scope: Path = f / "refactor-scope.md"
    lane.ch("--candidate")
    digest: str = ra.snapshot_digest(json.loads(sorted((f / "g1").glob("*-candidate.json"))[-1].read_text(encoding="utf-8")))
    scope.write_text(lane.scope_base + f"\n## G1 변경 결정 2026-10-04 19:30 · 후보 digest {digest}\n\n"
                     "- V2 · 결정 = 바꾼다 · 출처 = 본인 직접(2026-10-04 19:30)\n", encoding="utf-8")
    final_now: str = ra.snapshot_digest(ra.changes_snapshot(f, lane.repo))     # 최종 digest = 지금 스냅숏(결속 칸 없음)
    expect(fails, "RD-T1 G1 변경 결정 절 머리 시각에 공백(`2026-10-04 19:30`) → 읽힘 · --gate green", lane.ch("--gate"), 0,
           "red 0 · gate", f"최종 digest {final_now}")
    scope.write_text(lane.scope_base + f"\n## G1 변경 결정 · 후보 digest {digest}\n\n"
                     "- V2 · 결정 = 바꾼다 · 출처 = 본인 직접(2026-10-04 19:30)\n", encoding="utf-8")
    # 리뷰 B #7 — 최신 결정 절 머리가 판형 밖(시각 없음)이면 못 읽음이 아니라 실행 불능(앞 절로 내려가지 않는다)
    expect(fails, "RD-T2 G1 변경 결정 절 머리에 시각 없음 → 판형 밖 실행 불능", lane.ch("--gate"), 1,
           "최신 `G1 변경 결정` 절 머리가 판형")
    head: str = f"\n## G1 변경 결정 2026-10-04 19:30 · 후보 digest {digest}\n\n"
    scope.write_text(lane.scope_base + head + f"- G1 변경판 확정 2026-10-04 19:50 · digest {digest} · 후보 {digest}\n",
                     encoding="utf-8")
    spaced = ra.g1_confirmed(f)
    scope.write_text(lane.scope_base + head + f"- G1 변경판 확정 · digest {digest} · 후보 {digest}\n", encoding="utf-8")
    try:
        ra.g1_confirmed(f)
        bare: str = "읽힘"
    except RuntimeError as exc:
        bare = f"실행 불능 {exc}"
    expect(fails, "RD-T3 g1_confirmed — 공백 든 시각 → (\"2026-10-04 19:50\", d, c) · 시각 없는 최신 확정 줄 → 실행 불능(RuntimeError)",
           (0 if spaced == ("2026-10-04 19:50", digest, digest) and "판형" in bare else 9, f"{spaced} · {bare}"), 0)


def support_rule_cases(fails: "list[str]", td: Path) -> None:
    """T12 통합 발견 B3 — `_support_binding` = behavior_support.latest_support 규칙(판형 `%Y%m%dT%H%M%SZ` 만 · 가장 새 «지원»의
    실행 정의가 없거나 깨지면 내려가지 않고 실행 불능 · surrogateescape 로 읽음)."""
    lane = ChangesLane(td, "sup")
    lane.support("20261004T090000Z")
    lane.support("zz-manual")
    lane.support("20261004T0930Z")
    got = lane.ch("--candidate")
    snap: dict = json.loads(sorted((lane.folder / "g1").glob("*-candidate.json"))[-1].read_text(encoding="utf-8")) \
        if got[0] == 0 else {}
    expect(fails, "RD-W1 시각 판형 밖 이름(`zz-manual` · `20261004T0930Z`)의 «지원» 폴더는 무시 → 판형 안 기록을 고른다",
           (got[0] if snap.get("support_record") == "20261004T090000Z" else 9, got[1]), 0, "red 0 · candidate")
    broken: Path = lane.folder / "behavior" / "support" / "20261004T100000Z"
    lane.support(broken.name)
    (broken / "run-definition.json").write_text("{broken", encoding="utf-8")
    expect(fails, "RD-W2 가장 새 «지원» 기록의 run-definition.json 깨짐 → 더 오래된 기록으로 내려가지 않고 실행 불능",
           lane.ch("--candidate"), 1, f"가장 새 지원 기록 {broken.name} 의 run-definition.json 을 읽지 못한다")
    (broken / "run-definition.json").unlink()
    expect(fails, "RD-W3 가장 새 «지원» 기록에 run-definition.json 없음 → 실행 불능(그 폴더 이름)", lane.ch("--candidate"), 1,
           f"가장 새 지원 기록 {broken.name}")
    (broken / "run-definition.json").write_text(json.dumps({"version": 1, "argvs": [["pytest"]]}), encoding="utf-8")
    expect(fails, "RD-W4 가장 새 «지원» 기록의 실행 정의에 env 칸 없음 → 실행 불능", lane.ch("--candidate"), 1, "(KeyError)")
    odd: dict = {"version": 1, "argvs": [["pytest"]], "env": {"DJANGO_SETTINGS_MODULE": "s\udcff"}}
    (broken / "run-definition.json").write_bytes(json.dumps(odd, ensure_ascii=False).encode("utf-8", "surrogateescape"))
    want: str = hashlib.sha256(json.dumps({"argvs": odd["argvs"], "env": odd["env"]}, ensure_ascii=False, sort_keys=True,
                                          separators=(",", ":")).encode("utf-8", "surrogateescape")).hexdigest()[:12]
    got_name, got_digest = ra._support_binding(lane.folder)
    expect(fails, "RD-W5 UTF-8 아닌 바이트가 든 실행 정의 → surrogateescape 로 읽고 같은 바이트로 digest",
           (0 if (got_name, got_digest) == (broken.name, want) else 9, f"{got_name} {got_digest} 기대 {want}"), 0)


def retain_notice_cases(fails: "list[str]", td: Path) -> None:
    """T12 통합 발견 A6 — retain 행이 있는데 candidate 칸에 재조직 표지가 하나도 없으면 알림 한 줄(red 아님 · exit · 요약 무변)."""
    lane = ChangesLane(td, "ret")
    plain: str = V_SPEC_ROWS.replace("정책 시험 파일 재조직(이동)", "정책 시험 파일 이동(move)")   # 리뷰 B #9 — 옛 표지는 재조직 아님
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=plain)
    got = lane.ch()
    expect(fails, "RD-N1 retain 행 2 · 재조직 표지 0 → 알림 한 줄 · exit 0 · 요약 `retain 재조직 0`", got, 0,
           "  알림: retain 행 2 가운데 재조직 표지 0 — 0F 허용 파일 없음(candidate 칸에 재조직 낱말이 있어야 재조직 행이다)",
           "retain 재조직 0", "red 0")
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2)
    got = lane.ch()
    expect(fails, "RD-N2 재조직 표지가 있는 retain 행이 하나라도 있으면 알림 없음",
           (got[0] if "알림: retain" not in got[1] else 9, got[1]), 0, "retain 재조직 1")


SLICE_PLAN: str = ("\n## 슬라이스 계획\n\n| 슬라이스 | 목적 | 인수 행 | 내부 행 | 완료 조건 |\n|---|---|---|---|---|\n"
                   "| S1 | 규칙 V1 | — | 규칙 함수 반환 기대 | test_policy |\n"
                   "| S2 | 응답 V2 | 컨트롤러 404 응답 · 공유 응답 기대 | — | test_thing_api |\n")
SHARED_ROW: str = ("| 공유 응답 기대 | HTTP 계약 | 매핑 오류 | test_policy | update | coder "
                   "`application/demo/test/test_policy.py::test_rule` |\n")


class ReviewLane(ChangesLane):
    """리뷰 B 사례 — 명세에 슬라이스 계획을 덧붙일 수 있는 changes 레인."""

    def spec_plan(self, vs: str, edits: str, res_rows: str, adm: str = V_SPEC_ROWS, plan: str = "") -> None:
        self.spec(vs + plan, edits, res_rows, adm=adm)

    def candidate(self) -> "tuple[Path, str]":
        """--candidate 한 번 → 새로 생긴 후보 파일(생성 전후 파일 집합 차이 — 같은 초의 `-2` 이름도 바르게 고른다)과 digest."""
        before: "set[Path]" = set((self.folder / "g1").glob("*-candidate.json"))
        got = self.ch("--candidate")
        new: "list[Path]" = sorted(set((self.folder / "g1").glob("*-candidate.json")) - before)
        if got[0] != 0 or len(new) != 1:
            raise RuntimeError(f"후보 준비 실패(새 후보 파일 {len(new)}): {got[1][-400:]}")
        return new[0], ra.snapshot_digest(json.loads(new[0].read_text(encoding="utf-8")))


def review_b_cases(fails: "list[str]", td: Path) -> None:
    """T13 독립 리뷰 B(Codex r1) 지적 1 ~ 9 — 지적마다 음성(리뷰가 적은 반례 꼴) · «더 멈추는 쪽» 처분."""
    lane = ReviewLane(td, "rvb")
    lane.support()
    f = lane.folder
    scope: Path = f / "refactor-scope.md"
    v2_shared: str = V2_TEXT.replace("  - 연산: demo", "  - 시험: 공유 응답 기대 update(coder) application/demo/test/test_policy.py::test_rule\n"
                                                    "    - 바뀌는 기대: «assert True»\n  - 연산: demo")
    v1_shared: str = V1_TEXT + ("  - 시험: 공유 응답 기대 update(coder) application/demo/test/test_policy.py::test_rule\n"
                                "    - 바뀌는 기대: «assert True»\n")
    adm_all: str = V_SPEC_ROWS + SHARED_ROW
    lane.spec_plan(v1_shared + v2_shared, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=adm_all, plan=SLICE_PLAN)
    cand_path, cd = lane.candidate()
    side: Path = cand_path.with_name(cand_path.name[:-len(".json")] + "-resolution.json")
    side_data: dict = json.loads(side.read_text(encoding="utf-8")) if side.is_file() else {}
    first_bytes: "tuple[bytes, bytes]" = (cand_path.read_bytes(), side.read_bytes() if side.is_file() else b"")
    expect(fails, "RD-B3a 곁 자료 = 후보 파일과 1:1(`<후보 줄기>-resolution.json`) · 해소 표 · 입장 표 · 슬라이스 계획 · 후보 digest",
           (0 if side_data.get("candidate") == cd and side_data.get("candidate_file") == cand_path.name
            and len(side_data.get("admission", [])) == 5 and [s[0] for s in side_data.get("slices", [])] == ["S1", "S2"]
            else 9, str(side_data)[:300]), 0)
    head: str = f"\n## G1 변경 결정 2026-10-05 00:50 · 후보 digest {cd}\n\n"
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 안 바꾼다 · 출처 = 본인 직접(2026-10-05 00:50)\n", encoding="utf-8")
    line_no: int = len((lane.scope_base + head).split("\n"))
    unapproved: str = (f"| M2 | 1 | 예외 매핑 흩어짐 | 불가 | 변경 미승인 | refactor-scope.md:{line_no} — G1 결정 안 바꾼다 "
                       f"| — | — |\n")
    adm_kept: str = "".join(ln for ln in adm_all.splitlines(keepends=True) if "컨트롤러 404 응답" not in ln)
    plan_kept: str = SLICE_PLAN.replace("| S2 | 응답 V2 | 컨트롤러 404 응답 · 공유 응답 기대 | — | test_thing_api |\n", "")
    ap = lambda: lane.ch("--applied", str(cand_path))  # noqa: E731
    lane.spec_plan(v1_shared, "없음\n", CH_ROW_M1 + unapproved, adm=adm_kept, plan=plan_kept)
    expect(fails, "RD-B1a --applied 안 바꾼 V2 에만 딸린 입장 행 · 슬라이스가 빠지고 공유 행(V1 · V2)은 남음 → green", ap(), 0,
           "red 0 · applied")
    lane.spec_plan(v1_shared, "없음\n", CH_ROW_M1 + unapproved, adm=adm_all, plan=plan_kept)
    expect(fails, "RD-B1b --applied 안 바꾼 V2 에만 딸린 `add` 입장 행이 표에 남음 → red(리뷰 B #1 반례)", ap(), 2,
           "반영 대조 다름 — 입장 표", "컨트롤러 404 응답")
    lane.spec_plan(v1_shared, "없음\n", CH_ROW_M1 + unapproved,
                   adm="".join(ln for ln in adm_kept.splitlines(keepends=True) if "공유 응답 기대" not in ln), plan=plan_kept)
    expect(fails, "RD-B1c --applied 공유 입장 행(V1 도 가리킴)까지 지움 → red", ap(), 2, "반영 대조 다름 — 입장 표", "빠진 행 공유 응답 기대")
    lane.spec_plan(v1_shared, "없음\n", CH_ROW_M1 + unapproved, adm=adm_kept, plan=SLICE_PLAN)
    expect(fails, "RD-B1d --applied 안 바꾼 V2 에만 딸린 슬라이스 S2 가 계획에 남음 → red", ap(), 2,
           "반영 대조 다름 — 슬라이스 계획(후보 − 안 바꾼 V 에만 딸린 슬라이스 ['S2'])")
    lane.spec_plan(v1_shared, "없음\n", CH_ROW_M1 + unapproved, adm=adm_kept,
                   plan=plan_kept.replace("| S1 | 규칙 V1 |", "| S1 | 규칙 V1 고침 |"))
    expect(fails, "RD-B1e --applied 남은 슬라이스 S1 의 칸이 바뀜 → red · 안내(글자 그대로 · 안 바꾼 V 이름도 지우지 않음 — X12 N2)", ap(), 2,
           "남은 슬라이스의 칸이 다르다", "— 남은 슬라이스 행은 글자 그대로 둔다(목적 칸의 안 바꾼 V 이름도 지우지 않는다 — ④)")
    for label, row, needle in (
            ("RD-B2a --applied 안 바꾼 V 요지의 요지 원문을 바꿈 → red(리뷰 B #2 반례)",
             unapproved.replace("예외 매핑 흩어짐", "예외 매핑 일부"), "항목 · 요지 번호 · 요지 원문이 후보와 다르다"),
            ("RD-B2b --applied 막는 것이 그 G1 결정 줄이 아님 → red",
             unapproved.replace(f"refactor-scope.md:{line_no}", "refactor-scope.md:1"), "막는 것이 그 G1 변경 결정 줄"),
            ("RD-B2c --applied 막는 것에 한 구 없음 → red", unapproved.replace(" — G1 결정 안 바꾼다", ""), "막는 것이 그 G1 변경 결정 줄"),
            ("RD-B2d --applied 범주가 변경 미승인이 아님 → red", unapproved.replace("변경 미승인", "편집 범위 밖"),
             "판정 · 범주가 `불가 · 변경 미승인` 가 아니다")):
        lane.spec_plan(v1_shared, "없음\n", CH_ROW_M1 + row, adm=adm_kept, plan=plan_kept)
        expect(fails, label, ap(), 2, needle)
    # 리뷰 B #3 — 곁 자료는 후보 파일마다(덮어쓰지 않음) · --applied 는 그 후보의 곁 자료만
    lane.spec_plan(v1_shared + v2_shared, EDIT_LINE, CH_ROW_M1.replace("| — |\n", "| 다른 해소 표 |\n") + CH_ROW_M2, adm=adm_all,
                   plan=SLICE_PLAN)
    cand2, cd2 = lane.candidate()
    side2: Path = cand2.with_name(cand2.name[:-len(".json")] + "-resolution.json")
    kept2: bool = (cand_path.read_bytes(), side.read_bytes()) == first_bytes        # 둘째 후보 뒤 첫 후보 · 첫 곁 자료 바이트 그대로
    lane.spec_plan(v1_shared, "없음\n", CH_ROW_M1 + unapproved, adm=adm_kept, plan=plan_kept)
    # B1R 수리(설계 v3.1 §1-5 · lead 결정 02:3x): 옛 전제 `cd2 == cd` 는 결속 앞 판 — 결속 칸 `resolution_rows_digest` 가 해소 표를
    # 후보 digest 에 넣으므로 해소 표가 다른 둘째 후보는 digest 도 다르다(`cd2 != cd`). 나머지 단언은 그대로.
    expect(fails, "RD-B3b 해소 표가 다른 둘째 후보는 후보 digest 도 다르다(결속) · 첫 후보 --applied 는 제 곁 자료로 → green",
           (ap()[0] if cd2 != cd and side2 != side and side.is_file() and side2.is_file() else 9, f"{cd} {cd2} {side2.name}"), 0)
    # 옛 전제가 지키던 성질(같은 digest 의 후보 둘이 곁 자료를 덮어쓰지 않음) — 같은 명세로 후보를 한 번 더 만든다
    lane.spec_plan(v1_shared + v2_shared, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=adm_all, plan=SLICE_PLAN)
    cand3, cd3 = lane.candidate()                                                     # 생성 전후 파일 집합 차이로 고름
    side3: Path = cand3.with_name(cand3.name[:-len(".json")] + "-resolution.json")
    kept3: bool = (cand_path.read_bytes(), side.read_bytes()) == first_bytes        # 셋째(같은 digest) 뒤에도 바이트 그대로
    own_names: bool = all(json.loads(sp.read_text(encoding="utf-8")).get("candidate_file") == cp.name
                          for cp, sp in ((cand_path, side), (cand2, side2), (cand3, side3)))
    same_side: bool = (side.is_file() and side3.is_file() and json.loads(side.read_text(encoding="utf-8")).get("rows")
                       == json.loads(side3.read_text(encoding="utf-8")).get("rows"))
    lane.spec_plan(v1_shared, "없음\n", CH_ROW_M1 + unapproved, adm=adm_kept, plan=plan_kept)
    got3 = ap()
    expect(fails, "RD-B3b2 같은 명세로 다시 만든 후보 = 같은 digest · 곁 자료 파일 따로(해소 표 같음) · 둘째 · 셋째 뒤 첫 후보 · 첫 곁 자료 "
           "바이트 그대로 · 곁 자료마다 `candidate_file` = 자기 후보 · 첫 후보 --applied → green",
           (got3[0] if cd3 == cd and cand3 != cand_path and side3 != side and same_side and kept2 and kept3 and own_names else 9,
            f"{got3[1]}\n{cd} {cd3} {side3.name} 보존 {kept2}/{kept3} 이름 {own_names}"), 0, "red 0 · applied")
    side.rename(side.with_name(side.name + ".bak"))
    expect(fails, "RD-B3c 후보의 곁 자료 없음 → 실행 불능(다른 후보 곁 자료로 대신하지 않는다)", ap(), 1, "파일 없음")
    side.with_name(side.name + ".bak").rename(side)
    # 리뷰 B #4 — --gate 양방향
    lane.spec_plan(v1_shared, "없음\n", CH_ROW_M1 + unapproved, adm=adm_kept, plan=plan_kept)
    expect(fails, "RD-B4a --gate 정상(안 바꾼 V2 · 목록 없음 · 변경 미승인) → green", lane.ch("--gate"), 0, "red 0 · gate")
    scope.write_text(lane.scope_base + head, encoding="utf-8")
    expect(fails, "RD-B4b --gate 후보의 밖 동작 V2 에 결정 줄 없음(지금 목록에서도 사라짐) → red(리뷰 B #4 반례)", lane.ch("--gate"), 2,
           "후보의 밖 동작 V2 에 G1 결정 줄이 없다")
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 안 바꾼다 · 출처 = 본인 직접(0050)\n"
                     "- V9 · 결정 = 바꾼다 · 출처 = 본인 직접(0050)\n", encoding="utf-8")
    expect(fails, "RD-B4c --gate 후보의 밖 동작 V 가 아닌 결정 줄(V9) → red", lane.ch("--gate"), 2, "G1 결정 줄 V9 이 후보의 밖 동작 V 가 아니다")
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 바꾼다 · 출처 = 본인 직접(0050)\n", encoding="utf-8")
    expect(fails, "RD-B4d --gate `바꾼다` V2 가 지금 목록에 없음 → red", lane.ch("--gate"), 2, "V2 는 G1 결정 `바꾼다` 인데 바뀌는 것 목록에 없다")
    # 리뷰 B #7 — 실제 기록 줄 · 절만 · 최신 불완전 → 실행 불능 · 확정 줄 ↔ 결정 절 결속
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 안 바꾼다 · 출처 = 본인 직접(0050)\n\n## G1 변경 결정 2026-10-05 01:00\n",
                     encoding="utf-8")
    expect(fails, "RD-B7a 유효한 결정 절 뒤 최신 결정 절 머리가 불완전 → 앞 절로 내려가지 않고 실행 불능(리뷰 B #7 반례)",
           lane.ch("--gate"), 1, "최신 `G1 변경 결정` 절 머리가 판형")
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 안 바꾼다 · 출처 = 본인 직접(0050)\n\n예시:\n```\n"
                     "## G1 변경 결정 2026-10-05 01:00 · 후보 digest 000000000000\n"
                     "G1 변경판 확정 2026-10-05 01:01 · digest 000000000000 · 후보 000000000000\n```\n", encoding="utf-8")
    expect(fails, "RD-B7b 코드 펜스 안 G1 기록(예시)은 읽지 않는다 → 앞의 실제 절로 green · 확정 없음(None)",
           (lane.ch("--gate")[0] if ra.g1_confirmed(f) is None else 9, "fenced"), 0)
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 안 바꾼다 · 출처 = 본인 직접(0050)\n"
                     f"- G1 변경판 확정 2026-10-05 00:55 · digest {cd} · 후보 aaaaaaaaaaaa\n", encoding="utf-8")
    try:
        ra.g1_confirmed(f)
        mism: str = "읽힘"
    except RuntimeError as exc:
        mism = str(exc)
    expect(fails, "RD-B7c 확정 줄의 후보 ≠ 그 앞 결정 절의 후보 digest → 실행 불능(옛 확정을 결속으로 받지 않음)",
           (0 if "후보 aaaaaaaaaaaa ≠" in mism else 9, mism), 0)
    scope.write_text(lane.scope_base + "\n이 실행의 G1 변경판 확정 2026-10-05 00:55 · digest " + cd + " · 후보 " + cd + " 줄을 쓴다\n",
                     encoding="utf-8")
    expect(fails, "RD-B7d 문장 중간의 `G1 변경판 확정` 언급은 기록이 아니다 → None", (0 if ra.g1_confirmed(f) is None else 9, ""), 0)
    # 리뷰 B r2 #1 — CommonMark 펜스(종류 · 여는 길이 이상 · 뒤 공백만이 닫힘) · 판독 지원 밖 꼴에 G1 기록이 걸리면 실행 불능
    fake: str = ("## G1 변경 결정 2026-10-05 01:00 · 후보 digest 000000000000\n"
                 "G1 변경판 확정 2026-10-05 01:01 · digest 000000000000 · 후보 000000000000\n")
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 안 바꾼다 · 출처 = 본인 직접(0050)\n\n문서 예시:\n````md\n```\n"
                     + fake + "```\n~~~\n" + fake + "````\n", encoding="utf-8")
    expect(fails, "RD-B7e 긴 펜스(````) 안 짧은 펜스(```) · 다른 종류(~~~) 안 G1 기록 → 기록 아님 → 앞의 실제 절로 green · 확정 없음"
           "(리뷰 B r2 #1 반례)", (lane.ch("--gate")[0] if ra.g1_confirmed(f) is None else 9, "long fence"), 0)
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 안 바꾼다 · 출처 = 본인 직접(0050)\n\n```\n예시\n``` 끝\n"
                     f"- G1 변경판 확정 2026-10-05 00:55 · digest {cd} · 후보 {cd}\n", encoding="utf-8")
    try:
        ra.g1_confirmed(f)
        unclosed: str = "읽힘"
    except RuntimeError as exc:
        unclosed = str(exc)
    expect(fails, "RD-B7f 닫히지 않은 펜스(``` 끝 은 정보 문자열 — 닫힘 아님) 뒤의 G1 확정 줄 → 실행 불능(gate 도 실행 불능)",
           (lane.ch("--gate")[0] if "닫히지 않았는데" in unclosed else 9, unclosed), 1)
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 안 바꾼다 · 출처 = 본인 직접(0050)\n\n"
                     f"    G1 변경판 확정 2026-10-05 00:55 · digest {cd} · 후보 {cd}\n", encoding="utf-8")
    expect(fails, "RD-B7g 4칸 들여 쓴 G1 확정 줄(들여쓴 코드 블록 · 목록 안 — 판독 지원 밖) → 실행 불능", lane.ch("--gate"), 1,
           "4칸 이상 들여 쓰여 있다")
    # X12 N4 — 문면 ⑥ «같은 절에»: 확정 줄이 가장 최근 결정 절 밖(다음 `#` / `##` 머리 뒤)이면 실행 불능 · `###` 이하는 절 안
    conf_line: str = f"- G1 변경판 확정 2026-10-05 00:55 · digest {cd} · 후보 {cd}\n"
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 안 바꾼다 · 출처 = 본인 직접(0050)\n\n## 메모\n\n" + conf_line,
                     encoding="utf-8")
    try:
        ra.g1_confirmed(f)
        outside: str = "읽힘"
    except RuntimeError as exc:
        outside = str(exc)
    expect(fails, "RD-B7h `## 메모` 밑 확정 줄(결정 절 밖) → 실행 불능(X12 N4)", (0 if "절" in outside and "밖이다" in outside else 9, outside), 0)
    scope.write_text(lane.scope_base + head + "- V2 · 결정 = 안 바꾼다 · 출처 = 본인 직접(0050)\n\n### 메모\n\n" + conf_line,
                     encoding="utf-8")
    expect(fails, "RD-B7i `### 메모` 밑 확정 줄은 절 안 → 읽힘", (0 if ra.g1_confirmed(f) == ("2026-10-05 00:55", cd, cd) else 9, ""), 0)
    # 리뷰 B #5 — 반대 방향 규칙: 원 행 인용이 없으면 인용 밖 증거 칸 필수
    rlane = ReviewLane(td, "rvb5")
    rlane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1
               + f"| M2 | 1 | 예외 매핑 흩어짐 | 불가 | 반대 방향 규칙 | {C_LOC} — 매핑 자리가 바뀐다 | — | — |\n")
    expect(fails, "RD-B5 `반대 방향 규칙` 불가 행 · 원 행 · verdict 에 반대 방향 인용 없음 · 증거 칸 없음 → red(설계 :249 · :253)",
           run(rlane.repo, "resolution", str(rlane.folder)), 2, "원 행 · verdict 가 인용한 반대 방향 규칙이 없다")


def review_b4_cases(fails: "list[str]", td: Path) -> None:
    """리뷰 B r4 #1 ~ #3(계약 = json.loads 값 · 소스 = 원문 + `\\/` 푼 줄 · 관찰 못 함 = 표면마다 · 소비 파일 읽기 실패) +
    X12 N1(다른 BC 편집 줄 — 표지 없어도 · 판형 밖 red)."""
    scope_line: str = "실행 · G0 승인 20261005-0230 · 모드 리팩토링 · audit 20261005-0220\n"
    own_name: str = "20261005-0230-refactor-demo"
    ctrl: str = FILES["application/demo/driving_layer/api/thing/thing_controller.py"]

    def proj(name: str, extra: "dict[str, str]") -> Path:
        r: Path = _project(td / name, {**DEPS_FILES, **extra})
        (r / ".dddjango" / own_name).mkdir(parents=True)
        (r / ".dddjango" / own_name / "refactor-scope.md").write_text(scope_line, encoding="utf-8")
        return r

    def dp(r: Path, n: str) -> "tuple[int, str]":
        return run(r, "deps", "demo", "--out", str(r / ".dddjango" / own_name / "deps" / n))

    def zeta_run(r: Path) -> None:
        z: Path = r / ".dddjango" / "20261005-0210-refactor-zeta"
        (z / "audit" / "20261005-0211").mkdir(parents=True)
        (z / "refactor-scope.md").write_text("실행 · G0 승인 20261005-0210 · 모드 리팩토링 · audit 20261005-0211\n", encoding="utf-8")
        (z / "audit" / "20261005-0211" / "plan.md").write_text("# p\n\n- BC: `zeta`\n", encoding="utf-8")

    def hits(r: Path, rel: str) -> "set[str]":
        return {h["provider"] for h in ra.DepsScan(r).http if h["file"] == rel}

    def dpw(r: Path, n: str) -> "tuple[int, str]":
        """deps 를 돌리고 출력 뒤에 deps.json 의 표면별 사유(`http_blind_why`)를 붙인다."""
        code, text = dp(r, n)
        dj: Path = r / ".dddjango" / own_name / "deps" / n / "deps.json"
        whys: "list[str]" = json.loads(dj.read_text(encoding="utf-8")).get("http_blind_why", []) if dj.is_file() else []
        return code, text + "\n사유: " + " | ".join(whys)
    sub: str = ctrl.replace('@api_controller("/thing")', '@api_controller("/thing/sub")')
    contract_rel: str = ".dddjango-web/20261005-0200-other/server-contract.json"
    esc: Path = proj("h1", {"application/demo/driving_layer/api/thing/thing_controller.py": sub,
                            "web/home/client.py": "URL: str = \"/api/thing/sub/1\"\n",
                            contract_rel: '{"paths": {"/api/thing\\/sub/1": {}, "/v2/thing\\u002fsub/{id}": {}}}\n',
                            "web/home/static/app.js": 'fetch("\\/api\\/thing\\/sub\\/2");\n'})
    scan = ra.DepsScan(esc)
    contract_hits: "list[str]" = [str(h["line"]) for h in scan.http if h["file"] == contract_rel]
    expect(fails, "RD-H1 이스케이프 계약(`\\/` · `\\u002f`) · 복수 조각 접두 `/thing/sub` → 계약 소비로 셈 · JS 원문 `\\/` 도 셈(리뷰 B r4 #1)",
           (0 if contract_hits and "web/home/static/app.js" in {h["file"] for h in scan.http} else 9,
            str([(h["file"], h["line"]) for h in scan.http])), 0)
    web: Path = esc / ".dddjango-web" / "20261005-0200-other"
    (web / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": True,
                                                      "slices": [{"files": ["web/other/views.py"]}]}), encoding="utf-8")
    (web / "server-contract.json").write_text('{"paths": {"/v9/thing\\u002fsub/{id}": {}}}\n', encoding="utf-8")
    expect(fails, "RD-H1b 활성 web 실행 계약의 `\\u002f` 경로(json.loads 값) → 계획된 소비 → 겹침", dp(esc, "h1"), 2,
           "계획된 소비 server-contract.json /v9/thing/sub/{id}")
    # #2 표면마다
    mixed: Path = proj("h3", {"application/demo/driving_layer/api/legacy/legacy_api.py":
                              "from ninja import Router\n\nrouter = Router()\n\n\n@router.get(\"/x\")\ndef x() -> int:\n    return 1\n"})
    expect(fails, "RD-H3 혼합 표면(접두 `/thing` 컨트롤러 + 함수형 Router) → 관찰 못 함(접두가 있어도 · 리뷰 B r4 #2)", dp(mixed, "m1"), 0,
           "HTTP 소비 web/home · HTTP 소비 관찰 못 함", "보류 0")
    zeta_run(mixed)
    expect(fails, "RD-H3b 그 + 다른 활성 실행 → 보류(사유 = 표면별)", dp(mixed, "m2"), 2, "Router() — api_controller 밖 API 표면", "보류 1")
    broken: Path = proj("h4", {"application/demo/driving_layer/api/thing/schema/schema_out.py": "class Out(:\n    pass\n"})
    expect(fails, "RD-H4 API 표면 파일 파싱 실패(원문에 api_controller 없음) → 관찰 못 함", dpw(broken, "p1"), 0,
           "HTTP 소비 관찰 못 함", "파싱 실패")
    area: Path = proj("h4b", {"application/demo/driving_layer/api/report/schema/schema_out.py": "X: int = 1\n"})
    expect(fails, "RD-H4b 컨트롤러 없는 API 영역(`api/report/`) → 관찰 못 함(같은 BC 다른 영역에 컨트롤러가 있어도)", dpw(area, "a1"), 0,
           "HTTP 소비 관찰 못 함", "컨트롤러 없는 API 영역")
    # #3 소비 파일 읽기 실패
    unread: Path = proj("h5", {"web/home/static/locked.js": "fetch(\"/api/thing/9\");\n"})
    locked: Path = unread / "web/home/static/locked.js"
    (unread / "web/home/templates").mkdir(parents=True)
    (unread / "web/home/templates/latin.html").write_bytes(b"<a href='/api/thing/8'>\xe9</a>\n")
    locked.chmod(0)
    try:
        got = dp(unread, "u1")
        expect(fails, "RD-H5 소비 파일 읽기 실패(chmod 000 · 비 UTF-8) → 관찰 못 함 · 활성 실행 없으면 요약만(실행 불능 아님 · 리뷰 B r4 #3)",
               got, 0, "HTTP 소비 관찰 못 함", "보류 0")
        ujson: Path = unread / ".dddjango" / own_name / "deps" / "u1" / "deps.json"
        unread_list: "list[str]" = json.loads(ujson.read_text(encoding="utf-8")).get("http_unread", []) if ujson.is_file() else []
        expect(fails, "RD-H5b 읽지 못한 소비 파일 둘을 `http_unread` · 사유 «소비 파일 읽기 실패 2»에",
               (0 if sorted(unread_list) == ["web/home/static/locked.js", "web/home/templates/latin.html"] else 9, str(unread_list)), 0)
        zeta_run(unread)
        expect(fails, "RD-H5c 그 + 다른 활성 실행 → 보류", dp(unread, "u2"), 2, "소비 파일 읽기 실패 2(", "보류 1")
    finally:
        locked.chmod(0o644)
    # 빈 문자열 접두 · `<…>` 경로 변수 · 한 줄 여러 BC · JS/HTML
    empty: Path = proj("h6", {"application/demo/driving_layer/api/thing/thing_controller.py":
                              ctrl.replace('@api_controller("/thing")', '@api_controller("")')})
    expect(fails, "RD-H6 빈 문자열 접두 → 관찰 못 함", dpw(empty, "e1"), 0, "HTTP 소비 관찰 못 함", "비었거나 `/` 뿐")
    angle: Path = proj("h7", {"application/demo/driving_layer/api/thing/thing_controller.py":
                              ctrl.replace('@api_controller("/thing")', '@api_controller("/thing/<int:tid>/sub")'),
                              "web/home/client.py": "URL: str = \"/api/thing/3/sub\"\n"})
    got = dp(angle, "g1")
    expect(fails, "RD-H7 `<…>` 경로 변수 → 앞 고정 조각 `/thing` 으로 셈", (got[0] if "관찰 못 함" not in got[1] else 9, got[1]), 0,
           "HTTP 소비 web/home")
    multi: Path = proj("h8", {
        "application/zeta/__init__.py": "", "application/zeta/driving_layer/__init__.py": "",
        "application/zeta/driving_layer/api/__init__.py": "", "application/zeta/driving_layer/api/z/__init__.py": "",
        "application/zeta/driving_layer/api/z/z_controller.py": ctrl.replace('@api_controller("/thing")', '@api_controller("/zeta")')
                                                                    .replace("ThingController", "ZetaController"),
        "web/home/static/both.js": 'const A = "/api/thing/1", B = "/api/zeta/2";\n',
        "web/home/templates/page.html": '<div hx-get="/api/thing/4"></div>\n'})
    expect(fails, "RD-H8 한 줄에 두 BC 접두 → 두 BC 모두 소비 · HTML 속성 문자열도 셈",
           (0 if hits(multi, "web/home/static/both.js") == {"demo", "zeta"} and hits(multi, "web/home/templates/page.html") == {"demo"}
            else 9, f"{hits(multi, 'web/home/static/both.js')} {hits(multi, 'web/home/templates/page.html')}"), 0)
    # X12 N1 — 다른 BC 편집 줄(표지 없어도 · 판형 밖 red · 산문 · 펜스 무시)
    lane = ChangesLane(td, "n1e")
    lane.support()
    base = lane.ch()
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE[2:], CH_ROW_M1 + CH_ROW_M2)
    expect(fails, "RD-X1a 표지 없는 `<경로> · <갈래> · V2` 줄도 읽는다 → 표지 있는 꼴과 같은 결과(X12 N1)",
           (lane.ch()[0] if lane.ch()[1].replace(str(lane.folder), "") == base[1].replace(str(lane.folder), "") else 9, lane.ch()[1]), 0,
           "다른 BC 편집 1", "red 0")
    lane.spec(V1_TEXT + V2_TEXT, "아래 줄은 G1 뒤 고친다\n\n```\nx/y.py · 받는 쪽 어댑터 · V9\n```\n" + EDIT_LINE,
              CH_ROW_M1 + CH_ROW_M2)
    expect(fails, "RD-X1b ` · ` 없는 산문 줄 · 펜스 안 줄은 무시 → green", lane.ch(), 0, "다른 BC 편집 1", "red 0")
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE + f"{ACL_REL} · V2\n", CH_ROW_M1 + CH_ROW_M2)
    for label, extra in (("기본", ()), ("--candidate", ("--candidate",)), ("--gate", ("--gate",))):
        got = lane.ch(*extra)
        expect(fails, f"RD-X1c ` · ` 를 품었는데 판형 밖인 줄 → red({label} — changes 모든 꼴)", got, 2, "다른 BC 편집 줄 판형 밖 —")


def surface_area_cases(fails: "list[str]", td: Path) -> None:
    """이어서 7(현장 사전 대조) — «컨트롤러 없는 API 영역»은 코드 있는 `.py` 가 있는 영역만. 반대 입력(관찰 못 함 유지)을 먼저 못 박고,
    그다음 통과 쪽(빈 `__init__.py` 뿐인 영역 — 정본 트리의 빈 `webhook/` 패키지 표지 — 은 사유 없음)."""
    own_name: str = "20261005-0250-refactor-demo"
    api: str = "application/demo/driving_layer/api/"

    def proj(name: str, extra: "dict[str, str]") -> Path:
        r: Path = _project(td / name, {**DEPS_FILES, **extra})
        (r / ".dddjango" / own_name).mkdir(parents=True)
        (r / ".dddjango" / own_name / "refactor-scope.md").write_text(
            "실행 · G0 승인 20261005-0250 · 모드 리팩토링 · audit 20261005-0240\n", encoding="utf-8")
        return r

    def dpw(r: Path, n: str, bc: str = "demo") -> "tuple[int, str]":
        code, text = run(r, "deps", bc, "--out", str(r / ".dddjango" / own_name / "deps" / n))
        dj: Path = r / ".dddjango" / own_name / "deps" / n / "deps.json"
        whys: "list[str]" = json.loads(dj.read_text(encoding="utf-8")).get("http_blind_why", []) if dj.is_file() else []
        return code, text + "\n사유: " + (" | ".join(whys) or "(없음)")

    def zeta_run(r: Path) -> None:
        z: Path = r / ".dddjango" / "20261005-0210-refactor-zeta"
        (z / "audit" / "20261005-0211").mkdir(parents=True)
        (z / "refactor-scope.md").write_text("실행 · G0 승인 20261005-0210 · 모드 리팩토링 · audit 20261005-0211\n", encoding="utf-8")
        (z / "audit" / "20261005-0211" / "plan.md").write_text("# p\n\n- BC: `zeta`\n", encoding="utf-8")
    handler: str = "def handle() -> int:\n    return 1\n"
    # 반대 입력 먼저 — 관찰 못 함이 그대로여야 한다
    for tag, label, extra, needle in (
            ("sa", "ⓐ 영역에 import 한 줄 든 `__init__.py` 만 · 컨트롤러 없음",
             {api + "report/__init__.py": "from application.demo.domain_layer.policy import rule_0\n"}, "report/ — 컨트롤러 없는 API 영역"),
            ("sb", "ⓑ 빈 `__init__.py` + `handler.py`(컨트롤러 없음)",
             {api + "report/__init__.py": "", api + "report/handler.py": handler}, "report/ — 컨트롤러 없는 API 영역"),
            ("sc", "ⓒ `webhook/<공급자>/handler.py`(api_controller 없음)",
             {api + "webhook/__init__.py": "", api + "webhook/pay/handler.py": handler}, "webhook/pay/ — 컨트롤러 없는 API 영역"),
            ("sd", "ⓓ 빈 `__init__.py` + 0바이트 `views.py`",
             {api + "report/__init__.py": "", api + "report/views.py": ""}, "report/ — 컨트롤러 없는 API 영역"),
            ("se", "ⓔ `__init__.py` 파싱 실패", {api + "report/__init__.py": "def (:\n"}, "report/__init__.py API 표면 파일 파싱 실패")):
        expect(fails, f"RD-A1{tag[1]} 반대 입력 {label} → 관찰 못 함 유지", dpw(proj(tag, extra), "d"), 0,
               "HTTP 소비 관찰 못 함", needle)
    # 통과 쪽 — 사유 없음
    for tag, label, extra in (
            ("sf", "ⓕ 0바이트 `webhook/__init__.py`", {api + "webhook/__init__.py": ""}),
            ("sg", "ⓖ 공백 · 주석만인 `webhook/__init__.py`", {api + "webhook/__init__.py": "\n# 웹훅 패키지\n   \n"}),
            ("sh", "ⓗ docstring 만인 `webhook/__init__.py`", {api + "webhook/__init__.py": '"""웹훅 패키지."""\n'}),
            ("si", "ⓘ 0바이트 `webhook/<공급자>/__init__.py` 만",
             {api + "webhook/__init__.py": "", api + "webhook/pay/__init__.py": ""})):
        got = dpw(proj(tag, extra), "d")
        expect(fails, f"RD-A2{tag[1]} 통과 {label} → 관찰 못 함 아님 · 사유 없음",
               (got[0] if "관찰 못 함" not in got[1] and "사유: (없음)" in got[1] else 9, got[1]), 0, "HTTP 소비 web/home")
    canon: Path = proj("sj", {api + "bc_error_schema.py": "class DemoErrorSchema:\n    code: str = \"\"\n",
                              api + "webhook/__init__.py": "", api + "thing/schema/__init__.py": "",
                              api + "thing/schema/schema_out.py": "class ThingOut:\n    id: int = 0\n"})
    got = dpw(canon, "d1")
    expect(fails, "RD-A2j 정본 트리 꼴 전체(registrar · bc_error_schema · 컨트롤러 영역 + schema · 빈 webhook) → 관찰 못 함 0",
           (got[0] if "관찰 못 함" not in got[1] and "사유: (없음)" in got[1] else 9, got[1]), 0, "HTTP 소비 web/home")
    zeta_run(canon)
    got = dpw(canon, "d2")
    expect(fails, "RD-A2j2 그 + 다른 활성 실행(이웃 아님) → 보류 0",
           (got[0] if "사유: (없음)" in got[1] else 9, got[1]), 0, "레인 겹침 없음", "보류 0")
    # 이어서 8(X12 r3) — 컨트롤러가 하나도 없는 BC 의 정본 뼈대(`api/` 바로 밑 `api_router.py` · `bc_error_schema.py`)는 표면이 아니다.
    # 반대 입력 먼저(관찰 못 함 유지) → 통과 쪽(사유 없음). 대상 BC = bare(컨트롤러 없음).
    bare: str = "application/bare/driving_layer/api/"
    pkgs: "dict[str, str]" = {"application/bare/__init__.py": "", "application/bare/driving_layer/__init__.py": "",
                              bare + "__init__.py": ""}
    reg_out: str = ("from ninja_extra import NinjaExtraAPI\n\n"
                    "from application.demo.driving_layer.api.thing.thing_controller import ThingController\n\n\n"
                    "def register_bare_api(api: NinjaExtraAPI) -> None:\n    api.register_controllers(ThingController)\n")
    for tag, label, extra, needle in (
            ("ba", "ⓐ `api_router.py` 가 밖에서 import 한 컨트롤러를 `register_controllers(X)`", {bare + "api_router.py": reg_out},
             "registrar 가 등록하는 컨트롤러의 접두를 이 BC 에서 못 찾음"),
            ("bb", "ⓑ `api/` 바로 밑 0바이트 `views.py`", {bare + "api_router.py": "", bare + "views.py": ""},
             "api_controller 없는 API 표면"),
            ("bc", "ⓒ `api_router.py` 안 `Router(` · `add_router`",
             {bare + "api_router.py": "from ninja import Router\n\nrouter = Router()\n\n\ndef register_bare_api(api) -> None:\n"
                                      "    api.add_router(\"/bare\", router)\n"}, "api_router.py 의 Router() — api_controller 밖 API 표면"),
            ("bd", "ⓓ `bc_error_schema.py` 안 함수형 경로 데코레이터",
             {bare + "bc_error_schema.py": "from config.api import api\n\n\n@api.get(\"/err\")\ndef err() -> int:\n    return 1\n"},
             "함수형 경로 데코레이터 — api_controller 밖 API 표면"),
            ("be", "ⓔ `api_router.py` 파싱 실패", {bare + "api_router.py": "def register_bare_api(:\n"},
             "api_router.py API 표면 파일 파싱 실패")):
        expect(fails, f"RD-A4{tag[1]} 반대 입력 {label}(컨트롤러 없는 BC) → 관찰 못 함 유지", dpw(proj(tag, {**pkgs, **extra}), "d", "bare"), 0,
               "HTTP 소비 관찰 못 함", needle)
    site_like: "dict[str, str]" = {**pkgs, bare + "api_router.py": "", bare + "bc_error_schema.py": "", bare + "webhook/__init__.py": ""}
    toy_like: "dict[str, str]" = {**pkgs, bare + "api_router.py": "def register_bare_api(api: object) -> None:\n    return None\n",
                                  bare + "bc_error_schema.py": "class BareErrorSchema:\n    code: str = \"\"\n"}
    for tag, label, extra in (("bf", "ⓕ 두 뼈대 파일 0바이트 + 빈 `__init__.py` + 빈 `webhook/__init__.py`(현장 꼴)", site_like),
                              ("bg", "ⓖ 등록 호출 없는 registrar def + 오류 스키마 클래스(X12 장난감 꼴)", toy_like)):
        got = dpw(proj(tag, extra), "d", "bare")
        expect(fails, f"RD-A5{tag[1]} 통과 {label} → 관찰 못 함 아님 · 사유 없음",
               (got[0] if "관찰 못 함" not in got[1] and "사유: (없음)" in got[1] else 9, got[1]), 0, "HTTP 소비 없음")
    held: Path = proj("bh", site_like)
    zeta_run(held)
    got = dpw(held, "d", "bare")
    expect(fails, "RD-A5h ⓕ + 다른 활성 실행(이웃 아님) → 보류 0",
           (got[0] if "사유: (없음)" in got[1] else 9, got[1]), 0, "레인 겹침 없음", "보류 0")
    # r5 가 «직접 사례로는 확인 못 함»이라 적은 넷
    nested: Path = proj("sk", {".dddjango-web/20261005-0200-other/server-contract.json":
                               '{"servers": [{"meta": {"url": "/api\\u002fthing/1"}}]}\n'})
    seen: "list[int]" = [h["line"] for h in ra.DepsScan(nested).http if h["file"].endswith("server-contract.json")]
    expect(fails, "RD-A3a 계약의 중첩 문자열 값(배열 속 객체의 값 · `\\u002f`) → json.loads 값에서 소비로 셈(원문 줄에는 없음 → 행 0)",
           (0 if seen == [0] else 9, str(seen)), 0)
    broken: Path = proj("sl", {api + "thing/schema/schema_out.py": "class Out(:\n    pass\n"})
    zeta_run(broken)
    expect(fails, "RD-A3b API 표면 파일 파싱 실패 + 다른 활성 실행 → 보류", dpw(broken, "d"), 2,
           "보류(이 BC 의 HTTP 소비 관찰 못 함 — ", "API 표면 파일 파싱 실패", "보류 1")
    text: str = (f"## 8. 다른 BC 편집 목록\n\n* {ACL_REL} · 받는 쪽 어댑터 · 0C\n* application/other/test/test_demo_adapter.py · "
                 "받는 쪽 시험 · 0F\n")
    edits, reds = ra._other_edits(text, set())
    expect(fails, "RD-A3c 다른 BC 편집 줄 `* ` 표지 · 연결 `0C` · `0F` → 읽힘 · red 0",
           (0 if [e["ref"] for e in edits] == ["0C", "0F"] and not reds else 9, f"{edits} {reds}"), 0)
    lane = ChangesLane(td, "s3d")
    lane.support()
    lane.ch("--candidate")
    cand: Path = sorted((lane.folder / "g1").glob("*-candidate.json"))[-1]
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE + f"{ACL_REL} · V2\n", CH_ROW_M1 + CH_ROW_M2)
    expect(fails, "RD-A3d `--applied` 에서도 판형 밖 다른 BC 편집 줄 → red", lane.ch("--applied", str(cand)), 2,
           "다른 BC 편집 줄 판형 밖 —")
    digest: str = ra.snapshot_digest(json.loads(cand.read_text(encoding="utf-8")))
    (lane.folder / "refactor-scope.md").write_text(
        lane.scope_base + f"\n## G1 변경 결정 2026-10-05 02:50 · 후보 digest {digest}\n\n- V2 · 결정 = 바꾼다 · 출처 = 본인 직접(0250)\n\n"
        f"# 다른 장\n\n- G1 변경판 확정 2026-10-05 02:55 · digest {digest} · 후보 {digest}\n", encoding="utf-8")
    try:
        ra.g1_confirmed(lane.folder)
        level1: str = "읽힘"
    except RuntimeError as exc:
        level1 = str(exc)
    expect(fails, "RD-A3e `#`(수준 1) 머리 뒤 확정 줄(결정 절 밖) → 실행 불능", (0 if "밖이다" in level1 else 9, level1), 0)


def review_b_deps_cases(fails: "list[str]", td: Path) -> None:
    """리뷰 B #6 · #8(→ r3 처분) — 활성 web 실행 계약 부재 · 읽기 실패는 G1 승인과 무관하게 보류 · HTTP 소비는 마운트를 결속하지 않는
    상위 집합(api_controller 접두 조각 일치 — 앞에 어떤 마운트가 와도 셈) · «관찰 못 함»은 api_controller 밖 API 표면 · 빈 · `/` 뿐 ·
    못 읽는 접두 · 소비 파일 읽기 실패 — 그 + 다른 활성 실행이면 보류(편차 8)."""
    repo: Path = _project(td / "rbd", DEPS_FILES)
    own: Path = repo / ".dddjango" / "20261005-0050-refactor-demo"
    own.mkdir(parents=True)
    (own / "refactor-scope.md").write_text("실행 · G0 승인 20261005-0050 · 모드 리팩토링 · audit 20261005-0040\n", encoding="utf-8")
    dp = lambda r, n: run(r, "deps", "demo", "--out", str(r / ".dddjango" / own.name / "deps" / n))  # noqa: E731
    web: Path = repo / ".dddjango-web" / "20261005-0000-home"
    web.mkdir(parents=True)
    (web / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": True,
                                                      "slices": [{"files": ["web/other/views.py"]}]}), encoding="utf-8")
    expect(fails, "RD-B6a G1 승인 뒤 web 실행에 server-contract.json 없음 → 보류(리뷰 B #6 반례)", dp(repo, "w1"), 2,
           "보류(server-contract.json 이 없다(계약 모름))")
    (web / "server-contract.json").write_bytes(b"\xff\xfe{broken")
    expect(fails, "RD-B6b web 계약을 읽지 못함(깨진 바이트) → 보류(빈 글로 바꾸지 않는다)", dp(repo, "w2"), 2,
           "보류(server-contract.json 을 읽지 못한다(계약 모름))")
    (web / "server-contract.json").write_text(json.dumps({"paths": {"/api/other/{id}": {}}}), encoding="utf-8")
    expect(fails, "RD-B6c 계약을 읽었고 이 BC 소비 없음 · 단위 다름 → 겹침 · 보류 없음", dp(repo, "w3"), 0, "레인 겹침 없음", "보류 0")
    shutil.rmtree(repo / ".dddjango-web")
    # #8 → r3 처분(lead 01:59 · 계획 끝 편차 8): HTTP 소비는 마운트를 결속하지 않는 상위 집합 — 대상 BC 의 `api_controller("<접두>")`
    # 마다 경로 조각 경계에서 `/<접두>` 로 시작하는 조각을 품은 URL 문자열(앞에 어떤 마운트가 와도)을 센다. «관찰 못 함»은 설계 :1275
    # 그대로(api_controller 밖 API 표면) + 접두가 비었거나 `/` 뿐 · 못 읽는 컨트롤러. 앞 RD-B8a ~ h 의 기대는 이 처분으로 바뀌었다.
    def mounted(name: str, extra: "dict[str, str]", drop: "tuple[str, ...]" = ()) -> Path:
        r: Path = _project(td / name, {**{k: v for k, v in DEPS_FILES.items() if not k.startswith(drop)}, **extra})
        (r / ".dddjango" / own.name).mkdir(parents=True)
        (r / ".dddjango" / own.name / "refactor-scope.md").write_text((own / "refactor-scope.md").read_text(encoding="utf-8"),
                                                                       encoding="utf-8")
        return r

    def zeta_run(r: Path) -> None:
        zeta: Path = r / ".dddjango" / "20261005-0010-refactor-zeta"
        (zeta / "audit" / "20261005-0011").mkdir(parents=True)
        (zeta / "refactor-scope.md").write_text("실행 · G0 승인 20261005-0010 · 모드 리팩토링 · audit 20261005-0011\n",
                                                encoding="utf-8")
        (zeta / "audit" / "20261005-0011" / "plan.md").write_text("# p\n\n- BC: `zeta`\n", encoding="utf-8")

    def lines_of(r: Path, rel: str) -> "list[int]":
        return sorted(h["line"] for h in ra.DepsScan(r).http if h["file"] == rel and h["provider"] == "demo")
    ctrl: str = FILES["application/demo/driving_layer/api/thing/thing_controller.py"]
    # 까닭: 앞 판은 마운트 재료(config/)가 없으면 관찰 못 함 — 이제 마운트를 몰라도 `/api/thing/1` 을 소비로 센다
    r2: Path = mounted("rbm", {}, drop=("config/",))
    expect(fails, "RD-B8a 마운트 재료(설정 · urls) 없음 → 마운트를 몰라도 `/api/thing/1` 을 소비로 셈(관찰 못 함 아님)", dp(r2, "m1"), 0,
           "HTTP 소비 web/home", "보류 0")
    # 까닭: 관찰 못 함의 사례를 빈 접두(`/` 뿐) 컨트롤러로 — 그 + 다른 활성 실행 = 보류(편차 8 그대로)
    blank: Path = mounted("rbb", {"application/demo/driving_layer/api/thing/thing_controller.py":
                                  ctrl.replace('@api_controller("/thing")', '@api_controller("/")')})
    expect(fails, "RD-B8b 접두가 `/` 뿐인 컨트롤러 → HTTP 소비 관찰 못 함(조각 일치가 무의미) · 활성 실행 없으면 요약만", dp(blank, "b1"), 0,
           "HTTP 소비 없음 · HTTP 소비 관찰 못 함", "보류 0")
    zeta_run(blank)
    expect(fails, "RD-B8b2 그 + 다른 활성 실행(이웃 아님) → 보류(관찰 못 한 충돌 후보 · 편차 8)", dp(blank, "b2"), 2,
           "보류(이 BC 의 HTTP 소비 관찰 못 함 — ", "비었거나 `/` 뿐", "보류 1")
    r3: Path = mounted("rbv", {"config/urls.py": URLS_PY.replace('path(\"api/\"', 'path(\"v2/\"'),
                               "web/home/client.py": "URL: str = \"/v2/thing/1\"\n"})
    got = dp(r3, "v1")
    expect(fails, "RD-B8c 다른 마운트(`v2/`)의 `/v2/thing/1` 도 소비로 셈(관찰 못 함 아님)",
           (got[0] if "관찰 못 함" not in got[1] else 9, got[1]), 0, "HTTP 소비 web/home")
    inner: str = URLS_PY
    nested: Path = mounted("rbn", {
        "config/urls.py": "from django.urls import include, path\n\nurlpatterns = [path(\"svc/\", include(\"config.api_urls\"))]\n",
        "config/api_urls.py": inner, "web/home/client.py": "URL: str = \"/svc/api/thing/1\"\nOLD: str = \"/api/thing/2\"\n"})
    got = dp(nested, "n1")
    seen: "list[int]" = lines_of(nested, "web/home/client.py")
    # 까닭: 앞 판은 결속한 전체 경로 `/svc/api/thing` 만 셌다 — 이제 마운트를 결속하지 않아 옛 `/api/thing/2` 도 센다(넘쳐 세기 — 상위 집합)
    expect(fails, "RD-B8d 마운트 `svc/api/` 여도 `/svc/api/thing/1` 을 셈 · 다른 접두의 `/api/thing/2` 도 셈(상위 집합)",
           (got[0] if seen == [1, 2] and "관찰 못 함" not in got[1] else 9, got[1] + str(seen)), 0, "HTTP 소비 web/home")
    dyn: Path = mounted("rbd2", {
        "config/urls.py": "from django.urls import include, path\n\nPREFIX: str = \"svc/\"\n\n"
                          "urlpatterns = [path(PREFIX, include(\"config.api_urls\"))]\n",
        "config/api_urls.py": inner, "web/home/client.py": "URL: str = \"/svc/api/thing/1\"\n"})
    # 까닭: 앞 판은 include 접두를 못 읽으면 관찰 못 함 — 이제 마운트 판독을 판정에 쓰지 않는다
    expect(fails, "RD-B8e include 접두가 변수여도 `/svc/api/thing/1` 을 셈(마운트 판독을 판정에 안 씀)", dp(dyn, "e1"), 0,
           "HTTP 소비 web/home", "보류 0")
    other_api: Path = mounted("rbo", {
        "config/api.py": "from ninja_extra import NinjaExtraAPI\n\napi = NinjaExtraAPI()\npublic = NinjaExtraAPI()\n",
        "config/urls.py": URLS_PY.replace("from config.api import api", "from config.api import api, public")
                                 .replace('path(\"api/\", api.urls)', 'path(\"api/\", public.urls)')})
    # 까닭: 앞 판은 다른 API 객체만 마운트되면 관찰 못 함 — 이제 결속을 보지 않고 `/api/thing/1` 을 셈
    expect(fails, "RD-B8f 다른 API 객체만 마운트돼도 `/api/thing/1` 을 셈(결속 안 함)", dp(other_api, "o1"), 0, "HTTP 소비 web/home")
    zeta_run(other_api)
    # 까닭: 관찰 못 함이 아니므로 편차 8 보류 대상이 아니다 — 이웃 아닌 활성 실행은 겹침도 보류도 아님
    expect(fails, "RD-B8g 그 + 다른 활성 실행(이웃 아님) → 관찰 못 함 아님 → 보류 0 · 겹침 0", dp(other_api, "o2"), 0,
           "레인 겹침 없음", "보류 0")
    unreg: Path = mounted("rbu", {"config/urls.py": URLS_PY.replace("register_demo_api(api)\n\n", "")})
    # 까닭: 앞 판은 registrar 를 안 부르면 관찰 못 함 — 이제 등록을 보지 않는다
    expect(fails, "RD-B8h registrar 를 부르지 않아도 `/api/thing/1` 을 셈(등록 안 봄)", dp(unreg, "u1"), 0, "HTTP 소비 web/home")
    edge: Path = mounted("rbe", {"web/home/client.py": (
        "A: str = \"/api/thingx/1\"\nB: str = \"/thing\"\nC: str = \"/v9/thing?x=1\"\nD: str = \"/a/thing#f\"\n"
        "E: str = \"/thing.json\"\nF: str = f\"{BASE}/thing/{tid}\"\nG: str = \"https://h.example/svc/thing\"\n")})
    seen = lines_of(edge, "web/home/client.py")
    expect(fails, "RD-B8i 조각 경계 — `/thingx` · `/thing.json` 은 아님 · `/thing` 끝 · `?` · `#` · `/` 뒤 · 앞 마운트 아무것이나 → 셈",
           (0 if seen == [2, 3, 4, 6, 7] else 9, str(seen)), 0)
    unread: Path = mounted("rbr", {"application/demo/driving_layer/api/thing/thing_controller.py":
                                   ctrl.replace('@api_controller("/thing")', 'PREFIX: str = "/thing"\n\n\n@api_controller(PREFIX)')})
    expect(fails, "RD-B8j 접두가 상수 글이 아님(`api_controller(PREFIX)`) → 관찰 못 함", dp(unread, "r1"), 0,
           "HTTP 소비 관찰 못 함")
    bare: Path = mounted("rbz", {"application/demo/driving_layer/api/thing/thing_controller.py":
                                 ctrl.replace('@api_controller("/thing")', '@api_controller')})
    expect(fails, "RD-B8k 맨 데코레이터 `@api_controller`(기본 빈 접두) → 관찰 못 함", dp(bare, "z1"), 0, "HTTP 소비 관찰 못 함")
    var: Path = mounted("rbx", {"application/demo/driving_layer/api/thing/thing_controller.py":
                                ctrl.replace('@api_controller("/thing")', '@api_controller("/thing/{tid}/sub")'),
                                "web/home/client.py": "URL: str = \"/api/thing/7/sub\"\n"})
    got = dp(var, "x1")
    expect(fails, "RD-B8l 접두에 경로 변수(`/thing/{tid}/sub`) → 변수 앞 고정 조각 `/thing` 으로 셈(상위 집합)",
           (got[0] if "관찰 못 함" not in got[1] else 9, got[1]), 0, "HTTP 소비 web/home")


REMOVE_FREE: str = ("| 낡은 경로 시험 지움 | 종료 근거 | — | test_big | remove | coder `application/demo/test/test_big.py::test_old` |\n")
REMOVE_V2: str = ("| 낡은 404 시험 지움 | 종료 근거 | — | test_thing_api | remove | acceptance-tester "
                  "`application/demo/test/test_policy.py::test_gone_old` |\n")


def remove_rows_cases(fails: "list[str]", td: Path) -> None:
    """k0 v6 §4-4 `remove_rows`(리뷰 C #3 · 0T 자료를 G1 확정 스냅숏에 결속) — 판형 = `update_rows` · digest 결속 ·
    `--applied` 는 안 바꾼 V 에만 딸린 행만 빠진다."""
    lane = ChangesLane(td, "rmv")
    lane.support()
    f = lane.folder
    rows = lambda: ra.changes_snapshot(f, lane.repo)["remove_rows"]  # noqa: E731
    dig = lambda: ra.snapshot_digest(ra.changes_snapshot(f, lane.repo))  # noqa: E731
    got: "list[dict]" = rows()
    d0: str = dig()
    expect(fails, "RD-Y1 입장 표에 remove 행 0 → `remove_rows` 빈 목록", (0 if got == [] else 9, str(got)), 0)
    v2_rm: str = V2_TEXT.replace("  - 연산: demo", "  - 시험: 낡은 404 시험 지움 remove(acceptance-tester) "
                                                 "application/demo/test/test_policy.py::test_gone_old\n"
                                                 "    - 바뀌는 기대: «assert True»\n  - 연산: demo")
    (lane.repo / "application/demo/test/test_policy.py").write_text(
        "def test_rule() -> None:\n    assert True\n\n\ndef test_gone_old() -> None:\n    assert True\n", encoding="utf-8")
    lane.spec(V1_TEXT + v2_rm, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + REMOVE_V2 + REMOVE_FREE)
    got, d1 = rows(), dig()
    want: "list[dict]" = [
        {"case": "application/demo/test/test_policy.py::test_gone_old", "owner": "acceptance-tester", "row": REMOVE_V2.strip(),
         "v": "V2"},
        {"case": "application/demo/test/test_big.py::test_old", "owner": "coder", "row": REMOVE_FREE.strip(), "v": None}]
    expect(fails, "RD-Y2 V 에 딸린 remove 행 → `v` = 그 V · 딸리지 않은 remove 행 → `v` null(표 차례 · 케이스 글자 그대로)",
           (0 if got == want else 9, str(got)), 0)
    expect(fails, "RD-Y3 요약 `remove 케이스 2(V 밖 1)`", lane.ch(), 0, "remove 케이스 2(V 밖 1)", "red 0")
    lane.spec(V1_TEXT + v2_rm, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2,
              adm=V_SPEC_ROWS + REMOVE_V2 + REMOVE_FREE.replace("종료 근거", "종료 근거."))
    d2: str = dig()
    expect(fails, "RD-Y4 스냅숏 digest 가 remove 행 추가 · 글자 변경에 바뀐다", (0 if len({d0, d1, d2}) == 3 else 9, f"{d0} {d1} {d2}"), 0)
    lane.spec(V1_TEXT + v2_rm, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + REMOVE_V2 + REMOVE_FREE)
    lane.ch("--candidate")
    cand_path: Path = sorted((f / "g1").glob("*-candidate.json"))[-1]
    cd: str = ra.snapshot_digest(json.loads(cand_path.read_text(encoding="utf-8")))
    head: str = f"\n## G1 변경 결정 2026-10-05 01:00 · 후보 digest {cd}\n\n"
    (f / "refactor-scope.md").write_text(lane.scope_base + head + "- V2 · 결정 = 안 바꾼다 · 출처 = 본인 직접(0100)\n", encoding="utf-8")
    line_no: int = len((lane.scope_base + head).split("\n"))
    unapproved: str = f"| M2 | 1 | 예외 매핑 흩어짐 | 불가 | 변경 미승인 | refactor-scope.md:{line_no} — G1 결정 안 바꾼다 | — | — |\n"
    kept: str = "".join(ln for ln in V_SPEC_ROWS.splitlines(keepends=True) if "컨트롤러 404 응답" not in ln)
    lane.spec(V1_TEXT, "없음\n", CH_ROW_M1 + unapproved, adm=kept + REMOVE_FREE)
    expect(fails, "RD-Y5 --applied 안 바꾼 V2 에만 딸린 remove 행이 빠진 승인판 → green", lane.ch("--applied", str(cand_path)), 0,
           "red 0 · applied", "remove 케이스 1(V 밖 1)")
    lane.spec(V1_TEXT, "없음\n", CH_ROW_M1 + unapproved, adm=kept + REMOVE_FREE.replace("test_old", "test_older"))
    expect(fails, "RD-Y6 --applied V 밖 remove 행 글자 변경 → 반송(red)", lane.ch("--applied", str(cand_path)), 2,
           "반영 대조 다름 — `remove_rows`")
    lane.spec(V1_TEXT, "없음\n", CH_ROW_M1 + unapproved, adm=kept + REMOVE_V2 + REMOVE_FREE)
    expect(fails, "RD-Y7 --applied 안 바꾼 V2 에만 딸린 remove 행을 승인판에 남김 → red(리뷰 B r2 «remove 행 잔존 직접 음성»)",
           lane.ch("--applied", str(cand_path)), 2, "반영 대조 다름 — 입장 표", "낡은 404 시험 지움", "반영 대조 다름 — `remove_rows`")


def resolution_change_cases(fails: "list[str]", td: Path) -> None:
    """설계 §3-3 · §7 해소 판정 — 판정 값 `변경` · 범주 6(`지원 안 함` · `변경 미승인`) · «정리»."""
    lane = ChangesLane(td, "rch")
    rs = lambda *extra: run(lane.repo, "resolution", str(lane.folder), *extra)  # noqa: E731
    expect(fails, "RD-R1 변경 행(처방 앵커 · 막는 것 = V<n> · 범주 —) 항목 둘 → 항목 해소 2(«정리» = 해소 ∪ 변경) · 변경 요지 2", rs(), 0,
           "해소 판정: 해소 2 · 부분 0 · 불가 0", "변경 요지 2 · 인용 밖 반대 규칙 0 · red 0")
    for label, m2, needle in (
            ("RD-R2 변경 행 처방 앵커 없음 → red", CH_ROW_M2.replace("M2 — 컨트롤러 예외 매핑 정리", "—"), "변경 행에 처방 앵커가 없다"),
            ("RD-R3 변경 행에 불가 범주 → red", CH_ROW_M2.replace("| 변경 | — |", "| 변경 | 지원 안 함 |"), "변경 행의 불가 범주"),
            ("RD-R4 변경 행 V 가 목록에 없음 → red", CH_ROW_M2.replace("| V2 |", "| V9 |"), "V9 이 `바뀌는 것 목록` 에 없다"),
            ("RD-R5 변경 행 막는 것이 V 목록 아님 → red", CH_ROW_M2.replace("| V2 |", f"| {C_LOC} — x |"), "`V<n>[ · V<m>]` 가 아니다"),
            ("RD-R6 옛 범주 `외부 관찰 동작` → 닫힌 목록 밖 red(범주 7 → 6)",
             f"| M2 | 1 | 예외 매핑 흩어짐 | 불가 | 외부 관찰 동작 | {C_LOC} — 응답이 바뀐다 | — | — |\n", "`외부 관찰 동작` 가 닫힌 목록"),
            ("RD-R7 `지원 안 함`(막는 것 = 기존 마이그레이션 파일) → 불가 항목 green",
             f"| M2 | 1 | 예외 매핑 흩어짐 | 불가 | 지원 안 함 | {M_LOC} — 기존 마이그레이션 수정이 필요 | — | — |\n", "불가 1"),
            ("RD-R8 부분 항목의 변경 행에 «되돌리지 않는 이유» 없음 → red",
             CH_ROW_M2 + f"| M2 | 2 | 긴 인자 | 불가 | 편집 범위 밖 | {X_LOC} — BC 밖 | — | — |\n", "부분 항목의 변경 행에")):
        lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + m2)
        expect(fails, label, rs(), 0 if "green" in label else 2, needle)
    # 반대 방향 규칙 — 인용 밖 규칙 증거 칸(설계 §3-3 1-1 · §8 더하는 것 넷)
    corpus = ra.Corpus("claude")
    roles, blocked = corpus.blocked_norms()
    good_rid, good_q = _evidence_norm(sorted(r for r in corpus.works if r not in blocked), bound=True)
    scope_t, scope_q = _evidence_norm(sorted(roles[ra.SCOPE_ROLE][1] - roles[ra.OPSAFE_ROLE][1]), bound=False)
    op_t, op_q = _evidence_norm(sorted(roles[ra.OPSAFE_ROLE][1] - roles[ra.SCOPE_ROLE][1]), bound=False)

    def opp(rid: str, quote: str, tail: str = " · 함께 지킬 배치 없음 — 두 자리가 같은 파일을 요구한다", cat: str = "반대 방향 규칙") -> str:
        return (f"| M2 | 1 | 예외 매핑 흩어짐 | 불가 | {cat} | {C_LOC} — 매핑 자리 · 반대 규칙 {rid} «{quote}»"
                f" · 검사기 check-context-isolation red{tail} | — | — |\n")
    for label, m2, code, needle in (
            ("RD-R9 인용 밖 반대 규칙 R-ID 가 팩에 없음 → red", opp("R-9999", good_q), 2, "반대 규칙 R-9999 가 팩에 없다"),
            ("RD-R10 인용 원문이 그 규범 블록에 없음 → red", opp(good_rid, "이 문장은 어느 규범 블록에도 없는 날조 인용"), 2,
             f"반대 규칙 {good_rid} 인용"),
            ("RD-R11 반대 규칙이 운영 전 예외 대상 → red", opp(op_t, op_q), 2, f"반대 규칙 {op_t} 가 운영 전 예외 Override"),
            ("RD-R12 반대 규칙이 적용 범위 대상 → red", opp(scope_t, scope_q), 2, f"반대 규칙 {scope_t} 가 적용 범위 Override"),
            ("RD-R13 증거 칸이 다 있으면 green · `인용 밖 반대 규칙 1`", opp(good_rid, good_q), 0, "인용 밖 반대 규칙 1 · red 0"),
            ("RD-R14 `함께 지킬 배치 없음` 칸 없음 → red", opp(good_rid, good_q, tail=""), 2, "함께 지킬 배치 없음 — <한 구>"),
            ("RD-R15 인용 20자 미만 → red", opp(good_rid, "애그리거트"), 2, "원문 인용이 5자다"),
            ("RD-R16 증거 칸을 다른 범주에 씀 → red", opp(good_rid, good_q, cat="편집 범위 밖"), 2, "범주 `반대 방향 규칙` 에만")):
        lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + m2)
        expect(fails, label, rs(), code, needle)


def deps_cases(fails: "list[str]", td: Path) -> None:
    """설계 §5 새 `deps` — SCC · 받는 쪽 · HTTP 간선 · 공유 표면 · 공급자 정리 상태 · 경로 단위 겹침 · 보류 · 다른 작업 트리."""
    repo: Path = _project(td / "dep", DEPS_FILES)
    own: Path = repo / ".dddjango" / "20261004-1900-refactor-demo"
    own.mkdir(parents=True)
    (own / "refactor-scope.md").write_text("실행 · G0 승인 20261004-1900 · 모드 리팩토링 · audit 20261004-1850\n", encoding="utf-8")
    dp = lambda n: run(repo, "deps", "demo", "--out", str(own / "deps" / n))  # noqa: E731

    def edit_paths(n: str) -> dict:
        p: Path = own / "deps" / n / "deps.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
    got = dp("d1")
    data: dict = edit_paths("d1")
    kinds: dict = data.get("edit_paths", {})
    expect(fails, "RD-D1 deps — 받는 쪽 어댑터 · 받는 쪽 시험 · 직접 import 자리 · HTTP 소비자(호출 자리 · 그 시험) · 공유 표면 · "
           "내주는 쪽 미정리 · 자기 폴더 제외 → exit 0",
           (got[0] if kinds.get(ACL_REL) == "받는 쪽 어댑터" and kinds.get("application/other/test/test_demo_adapter.py") == "받는 쪽 시험"
            and kinds.get("application/third/domain_layer/y.py") == "직접 import 자리"
            and kinds.get("web/home/client.py") == "HTTP 소비자" and kinds.get("scripts/tool.py") == "공유 표면"
            and kinds.get("web/home/tests/test_client.py") == "HTTP 소비자" else 9,
            got[1] + json.dumps(kinds, ensure_ascii=False)), 0,
           "순환 성분 단독", "내주는 쪽 base(미정리)", "미정리 공급자 1", "받는 쪽 other", "HTTP 소비 web/home", "레인 겹침 없음", "보류 0")
    sup: Path = repo / ".dddjango" / "20260901-refactor-base"
    sup.mkdir(parents=True)
    (sup / "refactor-scope.md").write_text("실행 · G0 승인 20260901-0000 · 모드 리팩토링 · audit 20260901-0001 · "
                                           "build_anchor abc · G2 승인 20260902-0000\n", encoding="utf-8")
    expect(fails, "RD-D2 내주는 쪽에 G2 승인 리팩토링 실행 → 정리", dp("d2"), 0, "내주는 쪽 base(정리(재상정 0))", "미정리 공급자 0")
    x: Path = repo / ".dddjango" / "20261003-0900-home-screen"
    x.mkdir(parents=True)
    (x / "refactor-scope.md").write_text("실행 · G0 승인 20261003-0900\n", encoding="utf-8")
    expect(fails, "RD-D3 명세 없는 활성 실행(대상 BC 모름) → 보류 정지 · 재개 조건 기록", dp("d3"), 2, "보류(대상 BC 를 모른다",
           "재개 조건: 그 레인이 G1 명세를 내거나 G2 로 끝난 뒤 다시 시작", "보류 1")
    (x / "design-spec.md").write_text("# x\n\n<!-- machine: file-plan -->\n```paths\nupdate web/home/client.py  # S1\n```\n",
                                      encoding="utf-8")
    expect(fails, "RD-D4 X 레인 file-plan 이 이 BC 를 URL 로 부르는 client 를 고침 → 겹침 정지", dp("d4"), 2,
           "겹침: 이 작업 트리 .dddjango/20261003-0900-home-screen — 경로 web/home/client.py", "레인 겹침 1")
    (x / "design-spec.md").write_text("# x\n\n<!-- machine: file-plan -->\n```paths\nupdate scripts/tool.py\n```\n",
                                      encoding="utf-8")
    expect(fails, "RD-D5 공유 표면 경로 겹침 → 겹침 정지", dp("d5"), 2, "경로 scripts/tool.py")
    (x / "design-spec.md").write_text("# x\n\n<!-- machine: file-plan -->\n```paths\nupdate application/zeta/a.py\n```\n\n"
                                      "<!-- machine: boundary-imports -->\n```imports\napplication/zeta/a.py  "
                                      "from application.demo.driving_layer.open_host_service.thing.thing_service import get\n```\n",
                                      encoding="utf-8")
    expect(fails, "RD-D6 다른 실행의 계획된 소비(boundary-imports 가 이 BC 를 가리킴) → 겹침 정지", dp("d6"), 2, "계획된 소비",
           "계획된 소비 1")
    (x / "refactor-scope.md").write_text("실행 · G0 승인 20261003-0900 · build_anchor abc · G2 승인 20261003-2000\n",
                                         encoding="utf-8")
    expect(fails, "RD-D7 G2 승인으로 끝난 실행은 보지 않는다 → exit 0", dp("d7"), 0, "레인 겹침 없음", "보류 0")
    web: Path = repo / ".dddjango-web" / "20261004-0800-home"
    web.mkdir(parents=True)
    (web / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": False, "slices": []}),
                                          encoding="utf-8")
    expect(fails, "RD-D8 G1 전 web 실행(단위 · 계약 모름) → 보류", dp("d8"), 2, "보류(server-contract.json 이 없다")
    (web / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": True,
                                                      "slices": [{"files": ["web/home/views.py"]}]}), encoding="utf-8")
    (web / "server-contract.json").write_text(json.dumps({"paths": {"/api/thing/{id}": {}}}), encoding="utf-8")
    expect(fails, "RD-D9 web 실행 계약이 이 BC 접두 operation 을 소비 · 같은 web 단위 → 겹침", dp("d9"), 2, "web 단위 web/home",
           "server-contract.json /api/thing")
    shutil.rmtree(web)
    # 순환 묶음 — a → b → c → a(운영 import)
    cyc: "dict[str, str]" = {**FILES, "application/a/domain_layer/m.py": "from application.b.domain_layer.m import B\nA = B\n",
                             "application/b/domain_layer/m.py": "from application.c.domain_layer.m import C\nB = C\n",
                             "application/c/domain_layer/m.py": "from application.a.domain_layer.m import A\nC = 1\n"}
    crepo: Path = _project(td / "cyc", cyc)
    expect(fails, "RD-D10 운영 순환 a → b → c → a → 지원 안 함(G0 정지)",
           run(crepo, "deps", "a", "--out", str(crepo / ".dddjango" / "r" / "deps" / "1")), 2, "순환 성분 크기 3",
           "지원 안 함: 순환 묶음 a · b · c")
    # HTTP 소비 간선도 운영 그래프에 든다 — demo → base(import) · base 운영 파일이 demo API 를 URL 로 부름 → 순환 2
    hrepo: Path = _project(td / "http", {**DEPS_FILES, "application/base/application_layer/thing_client.py":
                                         "THING_URL: str = \"/api/thing/9\"\n"})
    got = run(hrepo, "deps", "demo", "--out", str(hrepo / ".dddjango" / "r" / "deps" / "1"))
    hdata: Path = hrepo / ".dddjango" / "r" / "deps" / "1" / "deps.json"
    hkinds: dict = json.loads(hdata.read_text(encoding="utf-8")).get("edit_paths", {}) if hdata.is_file() else {}
    expect(fails, "RD-D10b HTTP 소비 주인 간선(BC base → demo) + demo → base import → 순환 성분 크기 2 · 주인 = BC",
           (got[0] if hkinds.get("application/base/application_layer/thing_client.py") == "HTTP 소비자" else 9, got[1]), 2,
           "순환 성분 크기 2", "HTTP 소비 base · web/home")
    # HTTP 관찰 못 함 — 접두를 api_controller 로 못 찾는 API 표면(urls.py path())
    (repo / "application/demo/urls.py").write_text("from django.urls import path\nurlpatterns = [path(\"x/\", None)]\n",
                                                   encoding="utf-8")
    expect(fails, "RD-D11 urls.py path() 만 있는 API 표면 → HTTP 소비 관찰 못 함", dp("d11"), 0, "HTTP 소비 관찰 못 함")
    (repo / "application/demo/urls.py").unlink()
    # 다른 작업 트리 — 그 트리의 활성 리팩토링 실행(이웃 BC third) · 커밋 차분 · git status 를 돌리지 않음(index 무변)
    wt: Path = td / "dep-wt"
    _git(repo, "worktree", "add", "-q", "-b", "side", str(wt))
    (wt / "application/third/domain_layer/y.py").write_text("Z = 0\n", encoding="utf-8")
    _git(wt, "commit", "-qam", "side")
    run_dir: Path = wt / ".dddjango" / "20261004-1000-refactor-third"
    (run_dir / "audit" / "20261004-1001").mkdir(parents=True)
    (run_dir / "refactor-scope.md").write_text("실행 · G0 승인 20261004-1000 · 모드 리팩토링 · audit 20261004-1001\n",
                                               encoding="utf-8")
    (run_dir / "audit" / "20261004-1001" / "plan.md").write_text("# p\n\n- BC: `third`\n", encoding="utf-8")
    gitdir: Path = Path(_git(wt, "rev-parse", "--git-dir").strip())
    index: Path = (gitdir if gitdir.is_absolute() else wt / gitdir) / "index"
    before: int = index.stat().st_mtime_ns
    got = dp("d12")
    expect(fails, "RD-D12 다른 작업 트리의 활성 실행(이웃 BC third) → 겹침 · 그 트리 index 무변(git status 0)",
           (got[0] if index.stat().st_mtime_ns == before else 9, got[1]), 2, "작업 트리", "BC third", "본 범위: 작업 트리 2")
    copy: Path = wt / ".dddjango" / own.name
    copy.mkdir(parents=True)
    (copy / "refactor-scope.md").write_text((own / "refactor-scope.md").read_text(encoding="utf-8"), encoding="utf-8")
    got = dp("d13")
    expect(fails, "RD-D13 다른 작업 트리에 든 이 실행의 사본(같은 폴더 · 같은 실행 줄)은 다른 실행으로 세지 않는다",
           (got[0] if f"{own.name} —" not in got[1] else 9, got[1]), 2, "레인 겹침 1")
    (copy / "refactor-scope.md").write_text("실행 · G0 승인 20261004-2100 · 모드 리팩토링 · audit 20261004-2050\n", encoding="utf-8")
    expect(fails, "RD-D14 같은 폴더 이름이라도 실행 줄이 다르면 다른 실행 — 같은 BC 겹침", dp("d14"), 2,
           f"{own.name} — BC demo", "레인 겹침 2")


def map_items_case(fails: "list[str]", td: Path) -> None:
    """설계 §7 `_map_items` — follow · change 창 대응표도 싣는다(test 창은 아니다) · 창 차례는 번호(w2 < w10)."""
    folder: Path = td / "mapf"
    run_dir: Path = folder / "behavior" / "20261004-1900"
    run_dir.mkdir(parents=True)
    for n, kind, old, new in ((1, "test", "t_old.py", "t_new.py"), (2, "code", "a.py", "b.py"), (3, "follow", "c.py", "d.py"),
                              (4, "change", "e.py", "f.py"), (10, "change", "a.py", "z.py")):
        (run_dir / f"w{n}-open.json").write_text(json.dumps({"kind": kind}), encoding="utf-8")
        (run_dir / f"w{n}-close.json").write_text(json.dumps([{"map_items": {"pairs": {old: new}}}]), encoding="utf-8")
    got: dict = ra._map_items(folder, "20261004-1900")
    expect(fails, "RD-M1 _map_items — code · follow · change 대응(test 제외) · w10 이 w2 뒤",
           (0 if got == {"a.py": "z.py", "c.py": "d.py", "e.py": "f.py"} else 9, str(got)), 0)


def self_test_opsafe_cases(fails: "list[str]") -> None:
    """설계 §6-2 `--self-test` ①~④ 의 이빨 — 팩 · 블록 · 역할 표를 하나씩 어긋내면 red."""
    import contextlib
    import copy
    import io
    base = ra.Corpus("claude")
    opsafe_id: str = ra.OVERRIDE_ROLES[ra.OPSAFE_ROLE]

    def self_test(corpus: "ra.Corpus") -> "tuple[int, str]":
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code: int = ra.cmd_self_test(corpus)
        return code, buf.getvalue()

    c = copy.deepcopy(base)
    c.works[opsafe_id]["overrides"] = sorted(c.works[opsafe_id]["overrides"])[1:]
    expect(fails, "RD-S1 self-test ① 팩 overrides 가 블록 본문 대상 ∪ 조건부보다 하나 적음 → red", self_test(c), 2, "① 블록 본문")
    c = copy.deepcopy(base)
    roles = base.override_norms()
    retained: "list[str]" = sorted(ra._opsafe_lists("\n".join(
        base.doc(base.key_of(base.works[opsafe_id]["document"])).lines[slice(
            *base.block_spans(base.key_of(base.works[opsafe_id]["document"]))[base.works[opsafe_id]["block"]][0])]))["유지"])
    c.works[opsafe_id]["overrides"] = sorted(roles[ra.OPSAFE_ROLE][1] | {retained[0]})
    expect(fails, "RD-S2 self-test ② 유지 R-ID 가 overrides 에 들어감 → red", self_test(c), 2, "② 유지 R-ID 가 overrides 와 겹친다")
    c = copy.deepcopy(base)
    c.blocks[c.works[opsafe_id]["block"]]["h"] = "0" * 16
    c._spans = {}
    expect(fails, "RD-S3 self-test ③ 렌더 md 블록이 팩 해시와 결속 안 됨 → red", self_test(c), 2, "③ 운영 전 예외 규범")
    saved = dict(ra.OVERRIDE_ROLES)
    ra.OVERRIDE_ROLES[ra.OPSAFE_ROLE] = "R-0001"
    try:
        got = self_test(copy.deepcopy(base))
    finally:
        ra.OVERRIDE_ROLES.clear()
        ra.OVERRIDE_ROLES.update(saved)
    expect(fails, "RD-S4 self-test ④ 역할 표 ≠ 팩 «대상 있는 Override» 집합 → red", got, 2, "④ 대상 있는 Override 집합 ≠ 역할 표")
    expect(fails, "RD-S5 self-test ①~④ 정상 → red 0 · 운영 전 예외 대상 · 조건부 · 유지 수", self_test(copy.deepcopy(base)), 0,
           "운영 전 예외 대상", "red 0")


def self_test_negative_case(fails: "list[str]") -> None:
    """`--self-test` 의 불가 범주·재상정 어휘 대조에 이빨이 있는가 — 상수를 하나 빼면 red."""
    import contextlib
    import io
    corpus = ra.Corpus("claude")
    # 설계 §7 상시 답 걷기 — STANDING_CATEGORIES 는 Coordinator 문면 대조에서 빠졌다(인식 블록 상수는 web cmp 몫으로 남음).
    for name in ("RESOLUTION_CATEGORIES", "RECONSIDER_TOKENS"):
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
        residual_ground_fp_cases(fails, td)
        resolution_cases(fails, td)
        e2_cases(fails, td)
        final_cases(fails, td)
        standing_cases(fails, td)
        stage_cases(fails, td)
        override_cases(fails, aud, td)
        change_column_cases(fails, aud)
        other_bc_lane_case(fails, td)
        changes_cases(fails, td)
        update_rows_cases(fails, td)
        g1_time_cases(fails, td)
        support_rule_cases(fails, td)
        retain_notice_cases(fails, td)
        review_b_cases(fails, td)
        review_b_deps_cases(fails, td)
        review_b4_cases(fails, td)
        surface_area_cases(fails, td)
        remove_rows_cases(fails, td)
        g1_partial_cases(fails, td)
        closed_window_cases(fails, td)
        resolution_change_cases(fails, td)
        deps_cases(fails, td)
        map_items_case(fails, td)
    corpus_cases(fails, nov[0])
    self_test_negative_case(fails)
    self_test_opsafe_cases(fails)
    if fails:
        print("\nFAIL — refactor_audit 픽스처 기대 불일치:")
        for f in fails:
            print("  - " + f.replace("\n", "\n    "))
        return 1
    print("\nPASS — refactor_audit 픽스처 기대 일치")
    return 0


if __name__ == "__main__":
    sys.exit(main())
