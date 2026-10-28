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
import importlib.util
import itertools
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
_SCRIPTS: "str | None" = sys.argv[sys.argv.index("--scripts") + 1] if "--scripts" in sys.argv[1:-1] else None
TOOL: Path = (Path(_SCRIPTS).resolve() if _SCRIPTS else ROOT / "dddjango" / "scripts") / "refactor_audit.py"
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
    if args and args[0] == "deps" and tool == TOOL and "--at" not in args:
        args = (*args, "--at", _deps_at(args))
    return _raw_run(repo, *args, tool=tool)


def _raw_run(repo: Path, *args: str, tool: Path = TOOL) -> "tuple[int, str]":
    """인자를 그대로 넘긴다(`--at` 빠짐 사례 · 옛 판)."""
    proc = subprocess.run([sys.executable, str(tool), *args], cwd=repo, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def _deps_at(args: "tuple[str, ...]") -> str:
    """`--at` 을 적지 않은 기존 deps 사례의 판정 시점 값(설계 A0) — 이 실행 폴더에 끝나지 않은 실행 줄과 G1 확정이 있으면 `dispatch`
    (2.28.0 의 파견 직전 판정) · 그 밖은 `new`(2.28.0 의 G0 판정과 같은 셈). 새 사례는 값을 손으로 적는다."""
    out: Path = Path(args[args.index("--out") + 1]).resolve()
    own: "Path | None" = next((p for p in [out, *out.parents] if p.parent.name == ".dddjango"), None)
    line: "str | None" = ra._scope_run_line(own) if own is not None else None
    if own is None or line is None or ra._line_ended(line):
        return "new"
    try:
        return "dispatch" if ra.g1_confirmed(own) is not None else "new"
    except RuntimeError:                                     # G1 기록 판형 밖 — 도구가 같은 실행 불능을 내게
        return "dispatch"


PR_OLD_SHA: str = "af66e8d71e0ea3865a9999bb91eb3bc2b4ef8b9d"   # dddjango 2.28.0 배포 커밋(태그 dddjango--v2.28.0) — 옛 판 대조는 HEAD 아닌 이 판


def _pr_old_tool(td: Path) -> Path:
    """2.28.0 배포판 refactor_audit.py 사본(한 번만 꺼낸다 · deps 는 다른 모듈을 부르지 않는다)."""
    tool: Path = td / "pr-old" / "refactor_audit.py"
    if not tool.is_file():
        tool.parent.mkdir(parents=True, exist_ok=True)
        tool.write_text(_git(ROOT, "show", f"{PR_OLD_SHA}:dddjango/scripts/refactor_audit.py"), encoding="utf-8")
    return tool


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

    def __init__(self, td: Path, name: str, files: "dict[str, str] | None" = None) -> None:
        self.repo: Path = _project(td / name, files or DEPS_FILES)
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


CC_POLICY: str = "application/demo/test/test_policy.py"
CC_BIG: str = "application/demo/test/test_big.py"
CC_SKIP: str = "application/demo/test/test_skip.py"
CC_WEB: str = "web/home/tests/test_client.py"
CC_OUT: str = "확인 필요: 실행 정의 밖이거나 skip 인 편집 시험: "
CC_NEW: str = "확인 필요: 수집 꼴 밖 새 시험 파일: "


def _collect_support(lane: "ChangesLane", files: "list[str]", stamp: str = "20261004T110000Z") -> None:
    """수집 키를 담은 «지원» 기록(behavior_support 판형 — `keys` 노드 → [파일, …]) · 가장 새 기록이라 G1 관문이 이것에 결속한다."""
    d: Path = lane.folder / "behavior" / "support" / stamp
    d.mkdir(parents=True, exist_ok=True)
    (d / "run-definition.json").write_text(json.dumps({"version": 1, "argvs": [["pytest"]], "env": {"PYTEST_ADDOPTS": None},
                                                       "sources": ["Makefile:1"], "frozen_at": stamp}), encoding="utf-8")
    (d / "g0-collect.json").write_text(json.dumps({"version": 1, "verdict": "지원", "keys": {
        f"{f}::test_x": [f, "", "test_x"] for f in files}}), encoding="utf-8")


def changes_collect_cases(fails: "list[str]", td: Path) -> None:
    """설계 A5(S) — G1 관문(`--candidate` · `--gate`)이 결속한 지원 기록의 수집 파일(g0-collect `keys`)과 이 실행이 고칠 시험 모듈(명세
    file-plan · 다른 BC 편집 · 입장 표 owner/path 가운데 이미 있고 · `python_files` 에 맞고 · 정적 케이스가 있는 것)을 견준다 — 빠진
    모듈 · 수집 꼴 밖 `add` 새 파일은 «확인 필요» 줄(관문 red 아님 · exit 무변)."""
    lane = ChangesLane(td, "cc")
    repo: Path = lane.repo
    (repo / CC_BIG).write_text("def test_big() -> None:\n    assert True\n", encoding="utf-8")
    (repo / CC_SKIP).write_text("import pytest\n\npytest.importorskip(\"nope\")\n\n\ndef test_s() -> None:\n    assert True\n",
                                encoding="utf-8")
    for rel, body in (("application/demo/test/conftest.py", "import pytest\n\n\n@pytest.fixture\ndef x() -> int:\n    return 1\n"),
                      ("application/demo/test/factories.py", "def make() -> int:\n    return 1\n"),
                      ("application/demo/test/data/case.json", "{}\n")):
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(body, encoding="utf-8")
    skip_row: str = ("| 선택 의존 시험 기대 | 규칙 계약 | 규칙 오류 | test_skip | update | coder "
                     f"`{CC_SKIP}::test_s` |\n")
    plan: str = ("\n<!-- machine: file-plan -->\n```paths\nupdate application/demo/domain_layer/policy.py\n"
                 "update application/demo/test/conftest.py\nupdate application/demo/test/factories.py\n"
                 "update application/demo/test/data/case.json\n```\n")

    def spec(extra_rows: str = "") -> None:
        lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + skip_row + extra_rows)
        sp: Path = lane.folder / "design-spec.md"
        sp.write_text(sp.read_text(encoding="utf-8") + plan, encoding="utf-8")
    spec()
    _collect_support(lane, [CC_BIG, CC_SKIP])
    got = lane.ch("--candidate")
    expect(fails, "RD-CC1 편집 시험 모듈이 수집 밖(실행 정의가 `--ignore` 로 뺌) → 확인 필요 줄 · 관문 red 아님(exit 0)", got, 0,
           f"  {CC_OUT}{CC_POLICY}", "확인 필요 1 · red 0 · candidate")
    expect(fails, "RD-CC1b conftest · 팩토리 · JSON 자료 편집 · 고치지 않는 HTTP 소비 시험 → 견줄 대상 밖(줄 없음)",
           (got[0] if not any(x in got[1] for x in ("conftest.py", "factories.py", "case.json", CC_WEB)) else 9, got[1]), 0)
    _collect_support(lane, [CC_POLICY, CC_SKIP])
    expect(fails, "RD-CC2 retain 행 `경로.py`(케이스 없는 주소)가 수집 밖 → 확인 필요 줄", lane.ch("--candidate"), 0,
           f"  {CC_OUT}{CC_BIG}", "확인 필요 1 ·")
    _collect_support(lane, [CC_POLICY, CC_BIG])
    expect(fails, "RD-CC3 편집 모듈이 importorskip(정의 안이나 모듈 skip — 수집 키 없음) → 확인 필요 줄(red 아님 · 3회 I-3)",
           lane.ch("--candidate"), 0, f"  {CC_OUT}{CC_SKIP}", "red 0 · candidate")
    _collect_support(lane, [CC_POLICY, CC_BIG, CC_SKIP])
    got = lane.ch("--candidate")
    expect(fails, "RD-CC4 두 타깃 정의(고칠 모듈 모두 수집) → 줄 없음",
           (got[0] if "확인 필요" not in got[1] else 9, got[1]), 0, "red 0 · candidate")
    spec(f"| 새 점검 시험 | 규칙 계약 | 규칙 오류 | 없음 | add | coder `application/demo/test/check_new.py::test_c` |\n"
         f"| 새 하위 폴더 시험 | 규칙 계약 | 규칙 오류 | 없음 | add | coder `application/demo/test/sub/test_new.py::test_n` |\n")
    got = lane.ch("--candidate")
    expect(fails, "RD-CC5 `add` 새 파일 `check_new.py`(python_files 밖) → 수집 꼴 밖 줄 · 새 하위 폴더 `test_new.py` → 줄 없음",
           (got[0] if "sub/test_new.py" not in got[1] else 9, got[1]), 0, f"  {CC_NEW}application/demo/test/check_new.py",
           "확인 필요 1 ·")
    digest: str = got[1].split("후보 digest ", 1)[1].split()[0] if "후보 digest " in got[1] else ""
    (lane.folder / "refactor-scope.md").write_text(lane.scope_base + f"\n## G1 변경 결정 20261004-1930 · 후보 digest {digest}\n\n"
                                                   "- V2 · 결정 = 바꾼다 · 출처 = 본인 직접(1930)\n", encoding="utf-8")
    expect(fails, "RD-CC6 --gate 도 같은 확인 필요 줄 · 관문 green 그대로", lane.ch("--gate"), 0,
           f"  {CC_NEW}application/demo/test/check_new.py", "확인 필요 1 · red 0 · gate")
    got = lane.ch()
    expect(fails, "RD-CC7 기본 changes(관문 아님) → 확인 필요 줄 없음", (got[0] if "확인 필요" not in got[1] else 9, got[1]), 0)
    (repo / "pytest.ini").write_text("[pytest]\npython_files = check_*.py\n", encoding="utf-8")
    got = lane.ch("--candidate")
    expect(fails, "RD-CC8 프로젝트 `python_files = check_*.py` → check_new.py 는 수집 꼴 안 · 있는 test_*.py 는 시험 모듈 아님 · "
           "`add` 새 test_*.py 는 수집 꼴 밖 줄", (got[0] if "check_new.py" not in got[1] and CC_OUT not in got[1] else 9, got[1]), 0,
           f"  {CC_NEW}application/demo/test/test_thing_api.py", f"  {CC_NEW}application/demo/test/sub/test_new.py",
           "확인 필요 2 · red 0 · candidate")
    (repo / "pytest.ini").unlink()
    # 고칠 시험 모듈의 세 조건(이미 있음 · python_files 맞음 · 정적 케이스 있음)과 출처(file-plan · 다른 BC 편집 목록) — 구현 검토 변이
    helper_only: str = "application/demo/test/test_helpers.py"      # python_files 맞음 · 정적 케이스 없음
    not_named: str = "application/demo/test/checks.py"              # 정적 케이스 있음 · python_files 밖
    plan_only: str = "application/demo/test/test_plan_only.py"      # file-plan 에만 있는 시험 모듈
    edit_only: str = "application/other/test/test_demo_adapter.py"  # 다른 BC 편집 목록에만 있는 시험 모듈(받는 쪽 시험 · DEPS_FILES)
    for rel, body in ((helper_only, "def make() -> int:\n    return 1\n"),
                      (not_named, "def test_like() -> None:\n    assert True\n"),
                      (plan_only, "def test_p() -> None:\n    assert True\n")):
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(body, encoding="utf-8")
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE + f"- {edit_only} · 받는 쪽 시험 · V2\n", CH_ROW_M1 + CH_ROW_M2,
              adm=V_SPEC_ROWS + skip_row)
    sp: Path = lane.folder / "design-spec.md"
    sp.write_text(sp.read_text(encoding="utf-8") + plan.replace("update application/demo/test/conftest.py\n",
                                                                f"update {helper_only}\nupdate {not_named}\nupdate {plan_only}\n"),
                  encoding="utf-8")
    got = lane.ch("--candidate")
    expect(fails, "RD-CC9 file-plan 에만 있는 편집 시험 모듈이 수집 밖 → 확인 필요 줄(출처 file-plan)", got, 0, f"  {CC_OUT}{plan_only}")
    expect(fails, "RD-CC10 다른 BC 편집 목록에만 있는 편집 시험 모듈이 수집 밖 → 확인 필요 줄(출처 다른 BC 편집 목록)", got, 0,
           f"  {CC_OUT}{edit_only}")
    expect(fails, "RD-CC11 python_files 에 맞지만 정적 케이스 없는 모듈 · 정적 케이스 있지만 python_files 밖 모듈 → 줄 없음(시험 모듈 아님)",
           (got[0] if helper_only not in got[1] and not_named not in got[1] else 9, got[1]), 0, "확인 필요 2 · red 0 · candidate")
    (repo / "pytest.ini").write_text("[pytest]\ntestpaths = application/demo/test\n", encoding="utf-8")
    spec("| 밖 자리 새 시험 | 규칙 계약 | 규칙 오류 | 없음 | add | coder `application/demo/checks/test_far.py::test_f` |\n")
    got = lane.ch("--candidate")
    expect(fails, "RD-CC12 `add` 새 파일 이름은 python_files 안이나 testpaths 밖 → 수집 꼴 밖 줄(`_collectible` — 이름만 보지 않는다)",
           got, 0, f"  {CC_NEW}application/demo/checks/test_far.py")
    (repo / "pytest.ini").unlink()


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


GRP_SV: str = "application/demo/domain_layer/shared_value_object/"
GRP_PKG: str = "application.demo.domain_layer.shared_value_object"


def _grp_vo(stem: str) -> str:
    cls: str = "".join(x.capitalize() for x in stem.split("_"))
    return f'"""{stem} 값."""\nfrom dataclasses import dataclass\n\n\n@dataclass(frozen=True)\nclass {cls}:\n    value: str\n'


# 묶음 부모(값 객체 칸)에 `void_*` 셋 — C1(#656 만든다) ⓐ 면 셋이 `void/` 로 간다 · 다른 BC(third)가 void_b 를 부른다
GRP_FILES: "dict[str, str]" = {
    GRP_SV + "__init__.py": "", **{f"{GRP_SV}{s}.py": _grp_vo(s) for s in ("void_a", "void_b", "void_c", "moon_phase")},
    "application/demo/domain_layer/void_use.py": f"from {GRP_PKG}.void_a import VoidA\n\n\nUSE = VoidA\n",
    "application/third/domain_layer/void_user.py": f"from {GRP_PKG}.void_b import VoidB\n\n\nUSER = VoidB\n",
}
GRP_C1: str = f"| C1 | [#656] {GRP_SV}__init__.py: 묶음 `void/` 을(를) 만든다 | check-domain-model | 예 |\n"
GRP_C2: str = f"| C2 | [#459] {GRP_SV}void_a.py:6: 값 객체 칸 이름 픽스처 위반 | check-domain-model | 예 |\n"
GRP_C3: str = f"| C3 | [#459] {GRP_SV}moon_phase.py:6: 값 객체 칸 이름 픽스처 위반 | check-domain-model | 예 |\n"
GRP_TABLE: str = "| ID | 위반 | 백스톱 | 미룰 수 있나 |\n|---|---|---|---|\n"
GRP_PAIRS: "dict[str, str]" = {f"{GRP_SV}{s}.py": f"{GRP_SV}void/{s}.py" for s in ("void_a", "void_b", "void_c")}


def _grp_apply(repo: Path, folder: Path) -> None:
    """묶음 창 대역 — folder_group `apply --debt`(이동 + import 치환) 뒤 커밋."""
    proc = subprocess.run([sys.executable, str(TOOL.parent / "folder_group.py"), "apply", str(repo), "--run", str(folder), "--debt"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"folder_group apply 실패: {proc.stdout}{proc.stderr}")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "group window")


def _grp_sidecar(path: Path, pairs: "dict[str, str] | None" = None, lines: "tuple[str, ...]" = ()) -> Path:
    """게이트 `--introduced-json` sidecar 대역(`--group-moves` 로 돈 판 — `group_moves` 키)."""
    moved: "list[dict]" = [{"line": f"check-domain-model :: {ln}", "anchor_line": "(앵커 줄)"} for ln in lines]
    path.write_text(json.dumps({"anchor": "0" * 40, "records": [], "group_moves": {
        "pairs": GRP_PAIRS if pairs is None else pairs, "dropped": {}, "lines": moved}}, ensure_ascii=False), encoding="utf-8")
    return path


def group_move_cases(fails: "list[str]", td: Path) -> None:
    """2.28.0 의미 묶음 — `changes` 의 갈래 `묶음 import 치환` ⊆ draft 다른 BC import · `residual --gate-json` 의 쌍(M_c · M_m)."""
    lane = ChangesLane(td, "chg-grp", files={**DEPS_FILES, **GRP_FILES})
    scope: str = lane.scope_base.replace("- M1, M2 · 결정", GRP_TABLE + GRP_C1 + "\n- C1, M1, M2 · 결정")
    (lane.folder / "refactor-scope.md").write_text(scope, encoding="utf-8")
    user: str = "application/third/domain_layer/void_user.py"
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE + f"- {user} · 묶음 import 치환 · 0C\n", CH_ROW_M1 + CH_ROW_M2)
    expect(fails, "FG-C1 changes 갈래 `묶음 import 치환` 줄이 draft 다른 BC import 안 → green", lane.ch(), 0, "red 0")
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE + "- application/third/domain_layer/y.py · 묶음 import 치환 · 0C\n",
              CH_ROW_M1 + CH_ROW_M2)
    expect(fails, "FG-C2 changes 갈래 `묶음 import 치환` 줄이 draft 다른 BC import 밖 → red", lane.ch(), 2,
           "다른 BC 편집 `application/third/domain_layer/y.py · 묶음 import 치환` 가 draft 다른 BC import 밖")
    for ref in ("0F", "V1"):   # 검토 B9 — 이 갈래는 0C 묶음 창에서만(설계 10절 :478)
        lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE + f"- {user} · 묶음 import 치환 · {ref}\n", CH_ROW_M1 + CH_ROW_M2)
        expect(fails, f"FG-C5 changes 갈래 `묶음 import 치환` 줄의 연결이 {ref}(0C 아님) → red", lane.ch(), 2,
               f"다른 BC 편집 갈래 `묶음 import 치환` 의 연결 `{ref}` 가 0C 가 아니다")
    (lane.folder / "refactor-scope.md").write_text(lane.scope_base, encoding="utf-8")
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE + f"- {user} · 묶음 import 치환 · 0C\n", CH_ROW_M1 + CH_ROW_M2)
    expect(fails, "FG-C3 C1 이 ⓐ 가 아니면(묶음 이동 없음) 같은 줄도 draft 다른 BC import 밖 → red", lane.ch(), 2,
           f"다른 BC 편집 `{user} · 묶음 import 치환` 가 draft 다른 BC import 밖")
    (lane.folder / "refactor-scope.md").write_text(scope, encoding="utf-8")
    _grp_apply(lane.repo, lane.folder)
    expect(fails, "FG-C4 묶음 창이 이미 옮기고 import 를 고친 뒤 다시 돈 changes → green(앵커 판의 다른 BC import)", lane.ch(), 0,
           "red 0")
    # residual — C<n> ⓐ 만(M 없음): 이동 따라 옮긴 legacy 가 C2 면 M_c 1 → red
    repo: Path = _project(td / "grp-res", {**FILES, **GRP_FILES})
    folder, anchor = _res_folder(repo, [row(1, V_B9, where=f"{GRP_SV}void_c.py:6"),
                                        row(2, V_B9, where="application/demo/domain_layer/void_use.py:1"),
                                        row(3, V_B9, where=f"{GRP_SV}void_b.py:6")],
                                 ["M1 | ddd-01#1 | 채택 | | ", "M2 | ddd-01#2 | 채택 | | ", "M3 | ddd-01#3 | 채택 | | "])
    head: str = f"실행 · G0 승인 20260927-0300 · 모드 리팩토링 · audit 20260927-0250 · build_anchor {anchor}\n\n"
    scope_path: Path = folder / "refactor-scope.md"
    scope_path.write_text(head + GRP_TABLE + GRP_C1 + GRP_C2 + GRP_C3
                          + "\n- C1, C2, C3 · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(0300)\n", encoding="utf-8")
    _grp_apply(repo, folder)
    moved_c2: str = f"[#459] {GRP_SV}void/void_a.py:N: 값 객체 칸 이름 픽스처 위반"
    side: Path = _grp_sidecar(td / "grp-side.json", lines=(moved_c2,))
    expect(fails, "FG-R1 residual --gate-json · 이동 따라 옮긴 legacy 가 ⓐ C2 → M_c 이동 잔존 1 → red",
           run(repo, "residual", str(folder), "--gate-json", str(side)), 2, "M_c 이동 잔존 1(C2)", "M_m=0")
    expect(fails, "FG-R2 residual --gate-json 없음 → 지금과 같음(M_c 줄 없음 · green)", run(repo, "residual", str(folder)), 0,
           "M_m=0")
    other: Path = _grp_sidecar(td / "grp-side-c3.json",
                               lines=(f"[#459] {GRP_SV}void/moon_phase.py:N: 값 객체 칸 이름 픽스처 위반",))
    expect(fails, "FG-R3 쌍에 없는 경로의 줄은 C<n> 과 맞추지 않는다 → M_c 0 → green",
           run(repo, "residual", str(folder), "--gate-json", str(other)), 0, "M_c 이동 잔존 0")
    bare: Path = td / "grp-side-bare.json"
    bare.write_text(json.dumps({"anchor": "0" * 40, "records": []}), encoding="utf-8")
    expect(fails, "FG-R4 residual --gate-json sidecar 에 group_moves 없음 → 실행 불능",
           run(repo, "residual", str(folder), "--gate-json", str(bare)), 1, "group_moves")
    # 검토 SB2 — 이동 따라 옮긴 legacy 줄은 C 행의 위반 칸과 글자로 같아야 한다(줄이 그 칸의 앞부분일 뿐인 다른 위반 · 칸 밖
    # 글은 맞지 않는다)
    c4: str = f"| C4 | [#459] {GRP_SV}void_a.py:9: 값 객체 칸 이름 픽스처 위반 둘째 | check-domain-model | 예 |\n"
    scope_path.write_text(head + GRP_TABLE + GRP_C1 + GRP_C2 + GRP_C3 + c4
                          + "\n- C1, C2, C3, C4 · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(0300)\n", encoding="utf-8")
    expect(fails, "FG-R8 이동 따라 옮긴 legacy 줄이 다른 C 행 위반의 앞부분일 뿐 → 그 행은 M_c 아님(C2 만)",
           run(repo, "residual", str(folder), "--gate-json", str(side)), 2, "M_c 이동 잔존 1(C2)")
    # M_m — 이름 바꿈 + import 치환뿐인 항목 파일은 «안 바뀜»(결정적 잔존) · 그 밖은 리뷰어
    scope_path.write_text(head + GRP_TABLE + GRP_C1 + GRP_C2 + GRP_C3
                          + "\n- C1, C2, C3, M1, M2, M3 · 결정 = ⓐ · 사유 = 픽스처 · 출처 = 본인 직접(0300)\n", encoding="utf-8")
    moved_c: Path = repo / GRP_SV / "void" / "void_c.py"
    moved_c.write_text(moved_c.read_text(encoding="utf-8") + "\n\nEXTRA: int = 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "edit moved")
    expect(fails, "FG-R5 residual --gate-json · 옮기기만 한 파일(M3) · import 만 고친 파일(M2) → 결정적 잔존 · 옮긴 뒤 고친 파일(M1) → 리뷰어",
           run(repo, "residual", str(folder), "--gate-json", str(side)), 0, "결정적 잔존 2", "리뷰어 확인 대상 1(ddd)",
           "M_c 이동 잔존 1(C2)")
    bottom: str = max((folder / "residual").glob("*/bottom.md"), key=lambda q: q.stat().st_mtime).read_text(encoding="utf-8")
    expect(fails, "FG-R6 bottom.md 사유 = 이름 바꿈 + import 치환뿐", (0 if bottom.count("이름 바꿈 + import 치환뿐") == 2 else 9, bottom),
           0)
    expect(fails, "FG-R7 residual --gate-json 없음 → 지금과 같음(옮긴 파일은 바뀐 파일 · 셋 다 리뷰어)",
           run(repo, "residual", str(folder)), 0, "결정적 잔존 0", "리뷰어 확인 대상 3(ddd)")


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


POLICY_TEST: str = "application/demo/test/test_policy.py"


def _rn_row(cand: str, path: str = POLICY_TEST, why: str = "기대 의미 그대로 — 이름만") -> str:
    return f"| {cand} | {why} | 없음(재조직) | 그 케이스 자신 | retain | coder `{path}` |\n"


def rename_row_cases(fails: "list[str]", td: Path) -> None:
    """설계 3.1 §D2(F4-116) — 입장 표 `retain` 행 candidate `재조직 — 개명 <경로>::[<클래스>::]<옛> → <새>` · `재조직 — 개명
    <경로>::<케이스>[<옛 id>] → [<새 id>]` 를 G1 스냅숏 `retain_rows[].renames` 로(키는 개명 행에만 — 없는 명세는 digest 무변) · 한 행에
    하나 · 꼴 밖 · owner/path 파일 ≠ 개명 경로 → red · `.py::` 가 뒤따르지 않는 «재조직 — 개명» 글은 보통 재조직 행."""
    lane = ChangesLane(td, "rn")
    lane.support()
    f = lane.folder

    def retained() -> "list[dict]":
        return ra.changes_snapshot(f, lane.repo)["retain_rows"]

    d0: str = ra.snapshot_digest(ra.changes_snapshot(f, lane.repo))
    plain: "list[dict]" = retained()
    rows: str = (_rn_row(f"재조직 — 개명 {POLICY_TEST}::test_rule → test_rule_adds_one")
                 + _rn_row(f"재조직 — 개명 `{POLICY_TEST}::TestBox::test_m` → `test_box_m`")
                 + _rn_row(f"재조직 — 개명 {POLICY_TEST}::test_choose[choose_card] → [choose_tarot_card]",
                          path=f"{POLICY_TEST}::test_choose"))
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + rows)
    got: "list[dict]" = retained()
    want: "list[dict]" = plain + [
        {"path": POLICY_TEST, "case": None, "why": "기대 의미 그대로 — 이름만",
         "renames": [{"kind": "케이스", "path": POLICY_TEST, "class": None, "old": "test_rule", "new": "test_rule_adds_one"}]},
        {"path": POLICY_TEST, "case": None, "why": "기대 의미 그대로 — 이름만",
         "renames": [{"kind": "케이스", "path": POLICY_TEST, "class": "TestBox", "old": "test_m", "new": "test_box_m"}]},
        {"path": POLICY_TEST, "case": "test_choose", "why": "기대 의미 그대로 — 이름만",
         "renames": [{"kind": "ids", "path": POLICY_TEST, "case": "test_choose", "old": "choose_card", "new": "choose_tarot_card"}]}]
    expect(fails, "RD-RN1 개명 행 셋(케이스 · 클래스 메서드 · ids 원소 id) → `retain_rows[].renames` · 개명 아닌 retain 행은 키 없음",
           (0 if got == want and all("renames" not in r for r in plain) else 9, json.dumps(got, ensure_ascii=False)), 0)
    expect(fails, "RD-RN2 요약 `retain 재조직 4(개명 3)` · red 0", lane.ch(), 0, "retain 재조직 4(개명 3)", "red 0")
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2)
    expect(fails, "RD-RN3 개명 행을 지우면 처음 digest 로(개명 행 없는 명세는 digest 무변)",
           (0 if ra.snapshot_digest(ra.changes_snapshot(f, lane.repo)) == d0 else 9, ""), 0)
    for label, row, needle in (
            ("RD-RN4 새 이름 없음 → red(개명 행 꼴 밖)", _rn_row(f"재조직 — 개명 {POLICY_TEST}::test_rule →"), "개명 행 꼴 밖"),
            ("RD-RN5 한 행에 개명 둘 → red(한 행에 하나)",
             _rn_row(f"재조직 — 개명 {POLICY_TEST}::test_a → test_b · {POLICY_TEST}::test_c → test_d"), "개명 행 꼴 밖"),
            ("RD-RN6 옛 = 새 → red", _rn_row(f"재조직 — 개명 {POLICY_TEST}::test_rule → test_rule"), "옛 = 새"),
            ("RD-RN7 owner/path 파일 ≠ 개명 경로 → red",
             _rn_row(f"재조직 — 개명 {POLICY_TEST}::test_rule → test_rule_adds_one", path="application/demo/test/test_big.py"),
             "개명 행 owner/path 파일 `application/demo/test/test_big.py` ≠ 개명 경로")):
        lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + row)
        expect(fails, label, lane.ch(), 2, needle)
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2,
              adm=V_SPEC_ROWS + _rn_row("재조직 — 개명 card_b 변수를 summary_confirm_card 로(M47 #3)"))
    got = retained()
    expect(fails, "RD-RN8 «재조직 — 개명» 뒤에 `.py::` 주소가 없는 글 → 보통 재조직 행(renames 키 없음 · red 0)",
           (lane.ch()[0] if len(got) == 2 and all("renames" not in r for r in got) else 9, json.dumps(got, ensure_ascii=False)),
           0)
    one: str = _rn_row(f"재조직 — 개명 {POLICY_TEST}::test_rule → test_rule_adds_one")
    for label, rows, needle in (
            ("RD-RN9 같은 개명 행 두 번 → red", one + one, "같은 개명 행이 두 번"),
            ("RD-RN10 한 옛 이름에 개명 행 둘 → red", one + _rn_row(f"재조직 — 개명 {POLICY_TEST}::test_rule → test_rule_other"),
             "한 옛 이름에 개명 행 둘"),
            ("RD-RN11 ids 한 옛 id 에 개명 행 둘 → red",
             _rn_row(f"재조직 — 개명 {POLICY_TEST}::test_choose[a] → [b]") + _rn_row(f"재조직 — 개명 {POLICY_TEST}::test_choose[a] → [c]"),
             "한 옛 이름에 개명 행 둘")):
        lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + rows)
        expect(fails, label, lane.ch(), 2, needle)
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2,
              adm=V_SPEC_ROWS + _rn_row(f"정책 시험 재조직 — 개명 {POLICY_TEST}::test_rule → test_rule_adds_one"))
    got = retained()
    expect(fails, "RD-RN12 «재조직 — 개명» 이 candidate 맨 앞이 아니면 보통 재조직 행(renames 키 없음)",
           (lane.ch()[0] if len(got) == 2 and all("renames" not in r for r in got) else 9, json.dumps(got, ensure_ascii=False)),
           0)
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2,
              adm=V_SPEC_ROWS + _rn_row(f"재조직 — 개명 ./{POLICY_TEST}::test_rule → test_rule_adds_one"))
    got = retained()
    expect(fails, "RD-RN13 `./` 접두 경로 → 정규화(개명 경로 = owner/path 파일) · red 0",
           (lane.ch()[0] if got[-1].get("renames") == [{"kind": "케이스", "path": POLICY_TEST, "class": None, "old": "test_rule",
                                                         "new": "test_rule_adds_one"}] else 9, json.dumps(got, ensure_ascii=False)), 0)
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2,
              adm=V_SPEC_ROWS + _rn_row(f"재조직 — 개명 ../{POLICY_TEST}::test_rule → test_rule_adds_one"))
    expect(fails, "RD-RN14 저장소 밖 경로(`../`) → red", lane.ch(), 2, "개명 행 꼴 밖")
    upd_row: str = (f"| 규칙 함수 반환 기대 | 규칙 계약 | 규칙 오류 | test_policy | update | coder "
                    f"`{POLICY_TEST}::test_rule_adds_one` |\n")
    rm_row: str = f"| 옛 규칙 시험 | — | — | test_policy | remove | coder `{POLICY_TEST}::test_rule_adds_one` |\n"
    for label, extra, needle in (
            ("RD-RN15 개명 새 이름 = 입장 표 remove 행 케이스 → red(그 행이 개명된 케이스에 걸린다)", rm_row, "remove 행 케이스와 같다"),
            ("RD-RN16 개명 새 이름 = 입장 표 update 행 케이스 → red", upd_row, "update 행 케이스와 같다")):
        lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + one + extra)
        expect(fails, label, lane.ch(), 2, "개명 행 꼴 밖 — 개명 새 이름", needle)


CARD_SRC: str = "application/demo/domain_layer/card.py"


def _rf_item(path: str = POLICY_TEST, new: str = "card_key") -> dict:
    return {"kind": "칸", "path": path, "source": CARD_SRC, "class": "Card", "old": "card_id", "new": new}


def field_rename_row_cases(fails: "list[str]", td: Path) -> None:
    """설계 A 4판 A6(F4-116 남은 것) — 개명 항목 세 번째 꼴 «칸» `재조직 — 칸 개명 <운영 경로>::<클래스>.<옛> → <새>` · owner/path =
    그 칸을 쓰는 시험 파일 하나 → G1 스냅숏 `retain_rows[].renames` 원소 {kind 칸, path 시험 파일, source 운영 경로, class, old, new}
    (behavior_guard 0F 가 받는 꼴). 꼴 · 경로만 본다(운영 칸이 옛 → 새 로 바뀌었는지 · 밖 계약 클래스는 behavior_guard)."""
    lane = ChangesLane(td, "rf")
    lane.support()
    f = lane.folder

    def retained() -> "list[dict]":
        return ra.changes_snapshot(f, lane.repo)["retain_rows"]

    d0: str = ra.snapshot_digest(ra.changes_snapshot(f, lane.repo))
    plain: "list[dict]" = retained()
    field: str = f"재조직 — 칸 개명 {CARD_SRC}::Card.card_id → card_key"
    rows: str = _rn_row(field) + _rn_row(f"재조직 — 칸 개명 `{CARD_SRC}::Card.card_id` → `card_key`", path=BIG_TEST)
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + rows)
    got: "list[dict]" = retained()
    want: "list[dict]" = plain + [{"path": p, "case": None, "why": "기대 의미 그대로 — 이름만", "renames": [_rf_item(p)]}
                                  for p in (POLICY_TEST, BIG_TEST)]
    expect(fails, "RD-RF9 칸 개명 행(시험 파일마다 한 행 · 같은 칸 두 시험 파일) → `renames` 칸 항목 둘 · 요약 `retain 재조직 3(개명 2)`",
           (lane.ch()[0] if got == want else 9, json.dumps(got, ensure_ascii=False)), 0)
    expect(fails, "RD-RF9 요약 · red 0", lane.ch(), 0, "retain 재조직 3(개명 2)", "red 0")
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2)
    expect(fails, "RD-RF9 칸 개명 행을 지우면 처음 digest 로(칸 행 없는 명세는 digest 무변)",
           (0 if ra.snapshot_digest(ra.changes_snapshot(f, lane.repo)) == d0 else 9, ""), 0)
    for label, row, needle in (
            ("RD-RF10 클래스 없음(`<운영 경로>::<옛> → <새>`) → red(칸 개명 행 꼴 밖)",
             _rn_row(f"재조직 — 칸 개명 {CARD_SRC}::card_id → card_key"), "칸 개명 행 꼴 밖"),
            ("RD-RF10 중첩 클래스(`Outer.Card.<옛>`) → red(꼴 밖 — 클래스 하나)",
             _rn_row(f"재조직 — 칸 개명 {CARD_SRC}::Outer.Card.card_id → card_key"), "칸 개명 행 꼴 밖"),
            ("RD-RF10 한 행에 칸 개명 둘 → red", _rn_row(f"{field} · {CARD_SRC}::Card.kind → sort"), "칸 개명 행 꼴 밖"),
            ("RD-RF10 옛 = 새 → red", _rn_row(f"재조직 — 칸 개명 {CARD_SRC}::Card.card_id → card_id"), "옛 = 새"),
            ("RD-RF10 owner/path 가 시험 파일이 아님(운영 파일) → red", _rn_row(field, path=CARD_SRC),
             f"칸 개명 행 owner/path 파일 `{CARD_SRC}` 가 시험 파일이 아니다"),
            ("RD-RF10 운영 경로가 저장소 밖(`../`) → red", _rn_row(f"재조직 — 칸 개명 ../{CARD_SRC}::Card.card_id → card_key"),
             "저장소 상대 경로가 아니다"),
            ("RD-RF10 owner/path 가 저장소 밖(`../`) → red", _rn_row(field, path=f"../{POLICY_TEST}"), "저장소 상대 경로가 아니다")):
        lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + row)
        expect(fails, label, lane.ch(), 2, needle)
    for label, rows, needle in (
            ("RD-RF11 같은 칸 개명 행 두 번(같은 시험 파일) → red", _rn_row(field) + _rn_row(field), "같은 개명 행이 두 번"),
            ("RD-RF11 한 칸(운영 경로 · 클래스 · 옛)에 다른 새 이름 둘(다른 시험 파일) → red",
             _rn_row(field) + _rn_row(f"재조직 — 칸 개명 {CARD_SRC}::Card.card_id → card_ref", path=BIG_TEST), "한 옛 이름에 개명 행 둘")):
        lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + rows)
        expect(fails, label, lane.ch(), 2, needle)
    upd_row: str = (f"| 규칙 함수 반환 기대 | 규칙 계약 | 규칙 오류 | test_policy | update | coder "
                    f"`{POLICY_TEST}::Card::card_key` |\n")
    lane.spec(V1_TEXT + V2_TEXT, EDIT_LINE, CH_ROW_M1 + CH_ROW_M2, adm=V_SPEC_ROWS + _rn_row(field) + upd_row)
    got = retained()
    expect(fails, "RD-RF11 칸 개명은 케이스 키가 그대로 — 새 이름 꼴의 update 행 케이스와 겹침 대조 밖(red 0)",
           (lane.ch()[0] if got[-1].get("renames") == [_rf_item()] else 9, json.dumps(got, ensure_ascii=False)), 0)
    expect(fails, "RD-RF11 겹침 대조 밖 · red 0", lane.ch(), 0, "red 0")


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
    # 까닭(10-24 조정자 결정): G0 deps 의 web HTTP 소비로만 선 겹침은 «예보 겹침»이다. 앞 기대: exit 2 겹침.
    expect(fails, "RD-H1b 활성 web 실행 계약의 `\\u002f` 경로(json.loads 값) → 계획된 소비 → G0 예보 겹침", dp(esc, "h1"), 0,
           "예보 겹침: 이 작업 트리 .dddjango-web/20261005-0200-other — 계획된 소비 server-contract.json /v9/thing/sub/{id}")
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
    # 까닭(설계 3판 §A3 · 사용자 결정 «가.» 10-24): 계약 부재 · 읽기 실패는 G1 승인과 무관하게 web HTTP 소비 보류 그대로지만,
    # G0 deps(이 실행에 `G1 변경판 확정` 줄 없음)에서는 정지가 아니라 «예보 보류»다. 앞 기대: exit 2 보류.
    expect(fails, "RD-B6a G1 승인 뒤 web 실행에 server-contract.json 없음 → G0 예보 보류(리뷰 B #6 반례 · exit 0)", dp(repo, "w1"), 0,
           "예보 보류: 이 작업 트리 .dddjango-web/20261005-0000-home — 보류(server-contract.json 이 없다(계약 모름))")
    (web / "server-contract.json").write_bytes(b"\xff\xfe{broken")
    expect(fails, "RD-B6b web 계약을 읽지 못함(깨진 바이트) → G0 예보 보류(빈 글로 바꾸지 않는다 · exit 0)", dp(repo, "w2"), 0,
           "예보 보류: 이 작업 트리 .dddjango-web/20261005-0000-home — 보류(server-contract.json 을 읽지 못한다(계약 모름))")
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
    # 까닭(설계 3판 §A3 · 사용자 결정 «가.» 10-24): G0 deps 의 web HTTP 소비 보류는 정지가 아니라 «예보 보류»다 — 정지 판정은
    # 첫 파견 직전 deps(G1 확정판 밖 동작 V 수)와 조정자(G0 배너 직전 check-verdict «밖 b»)가 한다. 앞 기대: exit 2 보류.
    expect(fails, "RD-D8 G0 · G1 전 web 실행(단위 · 계약 모름) → 예보 보류(exit 0)", dp("d8"), 0,
           "예보 보류: 이 작업 트리 .dddjango-web/20261004-0800-home — 보류(server-contract.json 이 없다", "보류 0 ")
    (web / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": True,
                                                      "slices": [{"files": ["web/home/views.py"]}]}), encoding="utf-8")
    (web / "server-contract.json").write_text(json.dumps({"paths": {"/api/thing/{id}": {}}}), encoding="utf-8")
    # 까닭(10-24 조정자 결정 — 사용자 결정 «가.» 의 대상은 web 실행의 HTTP 소비로만 선 겹침 · 보류 한 갈래): G0 deps 에서는 V 를 아직
    # 모르므로 이 겹침도 정지가 아니라 «예보 겹침»이다(첫 파견 직전 V 로 판정). 앞 기대: exit 2 겹침.
    expect(fails, "RD-D9 G0 · web 실행 계약이 이 BC 접두 operation 을 소비 · 같은 web 단위(HTTP 소비로만 선 겹침) → 예보 겹침(exit 0)",
           dp("d9"), 0, "예보 겹침: 이 작업 트리 .dddjango-web/20261004-0800-home — web 단위 web/home",
           "server-contract.json /api/thing", "레인 겹침 없음", "예보 겹침 1")
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


# 설계 3판 §A1 · §A4(core 리팩토링 모드 막힘 묶음 10-24) — 끝 판정은 표식만 · 바뀐 것은 «어느 판의 기록을 읽나»뿐.
TREE_FILES: "dict[str, str]" = {
    "application/demo/__init__.py": "", "application/demo/domain_layer/__init__.py": "",
    "application/demo/domain_layer/m.py": "X: int = 1\n",
    "application/other/__init__.py": "", "application/other/domain_layer/__init__.py": "",
    "application/other/domain_layer/m.py": "from application.demo.domain_layer.m import X\n",
    "application/zeta/__init__.py": "", "application/zeta/domain_layer/__init__.py": "",
    "application/zeta/domain_layer/m.py": "Z: int = 1\n"}
TREE_OWN: str = "20261024-0300-refactor-demo"
TREE_OWN_LINE: str = "실행 · G0 승인 20261024-0300 · 모드 리팩토링 · audit 20261024-0301\n"
TREE_DONE: str = " · build_anchor a · G2 승인 20261001-0900"


class TreeLanes:
    """deps 작업 트리 사례 — 합성 저장소(주 작업 트리 = `main` 가지 · BC demo · other(demo 를 import) · zeta(독립)) + 레인 트리."""

    def __init__(self, td: Path, name: str, files: "dict[str, str] | None" = None) -> None:
        self.root: Path = td / name
        self.main: Path = _project(self.root, files or TREE_FILES)

    def tree(self, name: str, branch: str, start: str = "HEAD") -> Path:
        path: Path = self.root / name
        _git(self.main, "worktree", "add", "-q", "-b", branch, str(path), start)
        return path

    @staticmethod
    def write(tree: Path, files: "dict[str, str | bytes]") -> None:
        for rel, body in files.items():
            p: Path = tree / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(body, bytes):
                p.write_bytes(body)
            else:
                p.write_text(body, encoding="utf-8")

    @staticmethod
    def commit(tree: Path, msg: str, files: "dict[str, str | bytes] | None" = None) -> None:
        TreeLanes.write(tree, files or {})
        _git(tree, "add", "-A", "--", ".", f":(exclude).dddjango/{TREE_OWN}")
        _git(tree, "commit", "-qm", msg)

    @staticmethod
    def own(tree: Path, line: str = TREE_OWN_LINE) -> Path:
        folder: Path = tree / ".dddjango" / TREE_OWN
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "refactor-scope.md").write_text(line, encoding="utf-8")
        return folder

    @staticmethod
    def dp(tree: Path, n: str) -> "tuple[int, str]":
        return run(tree, "deps", "demo", "--out", str(tree / ".dddjango" / TREE_OWN / "deps" / n))


def _feat(name: str, bc: str, end: str = "") -> "dict[str, str]":
    """기능 실행 기록(실행 줄 + 대상 BC 경로 필터) — `end` 가 끝 표식(`· build_anchor … · G2 승인 …`)."""
    return {f".dddjango/{name}/refactor-scope.md": f"실행 · G0 승인 {name[:13]}{end}\n\n- 대상 BC 경로 필터: application/{bc}/\n"}


def deps_tree_cases(fails: "list[str]", td: Path) -> None:
    """설계 3판 §A1(F4-110 · F4-108 ㉡) — 자기 변경 사본은 그 사본 · MH 에 없는 폴더는 «이 트리가 만든 폴더»면 그 사본 · 아니면 뺌 ·
    그 밖은 주 작업 트리 HEAD(MH) 판 기록으로 판정(표식만 — 착륙 근거 없음) · 덧씌우기 · (종류, 폴더)로 묶기. 사례 S* · M* · W1 · R1 · H1 ·
    E1 은 재검토 합성(`review-deps/v2/mk2.sh` · `sc/`)과 같은 꼴."""
    L = TreeLanes
    # ── 센다 ──
    s1 = TreeLanes(td, "ts1")                               # S1 main 직접 실행(G1 대기 · 커밋) 뒤 레인 — 같은 실행 두 트리
    L.commit(s1.main, "main 직접 실행 G0 기록", _feat("20261024-0100-stopped-feature", "demo"))
    x = s1.tree("wt-x", "lane-x")
    L.own(x)
    got = L.dp(x, "s1")
    expect(fails, "RD-L1 S1 main 직접 실행(커밋 · 미종료) 뒤 레인 → 겹침 · 두 트리 사본은 한 번(묶기)", got, 2,
           ".dddjango/20261024-0100-stopped-feature — BC demo", "레인 겹침 1 ", "활성 실행 1(사본 2 · 트리 2)")
    s1c = TreeLanes(td, "ts1c")                             # S1c 작업 트리 하나 · 같은 트리 앞 실행
    L.commit(s1c.main, "기능 실행 G0 기록", _feat("20261024-0100-stopped-feature", "demo"))
    L.own(s1c.main)
    expect(fails, "RD-L2 S1c 작업 트리 하나 · 커밋된 앞 실행 → 겹침", L.dp(s1c.main, "s1c"), 2, "레인 겹침 1 ")
    s2 = TreeLanes(td, "ts2")                               # S2 레인이 main 을 받음(머지)
    y = s2.tree("wt-y", "lane-y")
    L.commit(y, "레인 Y 자기 커밋", {"application/zeta/domain_layer/y.py": "Y: int = 1\n"})
    L.commit(s2.main, "main 직접 실행 G0 기록", _feat("20261024-0100-stopped-feature", "demo"))
    _git(y, "merge", "-q", "--no-edit", "main")
    L.own(y)
    expect(fails, "RD-L3 S2 레인이 main 을 받음 → main 직접 실행 한 번 겹침", L.dp(y, "s2"), 2, "레인 겹침 1 ")
    s3 = TreeLanes(td, "ts3")                               # S3 main 직접 실행(zeta) + 레인이 만든 뒤 demo 코드 커밋 → 덧씌우기
    L.commit(s3.main, "main 직접 실행 G0 기록(BC zeta)", _feat("20261024-0100-direct-run", "zeta"))
    x = s3.tree("wt-x", "lane-x")
    L.own(x)
    L.commit(s3.main, "main 직접 실행 Phase 2 코드(demo)", {"application/demo/domain_layer/m.py": "X: int = 9\n"})
    expect(fails, "RD-L4 S3 main 직접 실행의 main 직접 코드 커밋 경로를 덧씌움 → 경로 겹침", L.dp(x, "s3"), 2,
           "경로 application/demo/domain_layer/m.py", "레인 겹침 1 ")
    s4 = TreeLanes(td, "ts4")                               # S4 쌓인 레인(Z 가 Y 위)
    y = s4.tree("wt-y", "lane-y")
    L.commit(y, "Y G0 기록", _feat("20261024-0200-feature-demo", "demo"))
    z = s4.tree("wt-z", "lane-z", "lane-y")
    L.own(z)
    expect(fails, "RD-L5 S4 쌓인 레인 → Y 실행 한 번 겹침", L.dp(z, "s4"), 2, "레인 겹침 1 ", "(사본 2 · 트리 3)")
    s5 = TreeLanes(td, "ts5")                               # S5 착륙했지만 MH 판에 표식 없음(지금과 같음 — 센다)
    y = s5.tree("wt-y", "lane-y")
    L.commit(y, "Y 실행 · 코드(끝 표식 빠짐)", {**_feat("20261024-0200-feature-demo", "demo"),
                                               "application/demo/domain_layer/m.py": "X: int = 2\n"})
    _git(s5.main, "merge", "-q", "--no-ff", "lane-y", "-m", "Merge lane-y")
    x = s5.tree("wt-x", "lane-x")
    L.own(x)
    expect(fails, "RD-L6 S5 착륙했지만 MH 판에 끝 표식 없는 실행 → 센다(한 번)", L.dp(x, "s5"), 2, "레인 겹침 1 ")
    for tag, after in (("m1", "code"), ("m1b", ""), ("m1c", "dirty")):   # M1 · M1b · M1c 중간 착륙 뒤 같은 레인에서 계속
        m = TreeLanes(td, f"t{tag}")
        y = m.tree("wt-y", "lane-y")
        L.commit(y, "Y G0 기록 + S1 코드", {**_feat("20261024-0200-feature-demo", "demo"),
                                           "application/demo/domain_layer/m.py": "X: int = 2\n"})
        _git(m.main, "merge", "-q", "--no-ff", "lane-y", "-m", "Merge lane-y — 첫 착륙(뒤 착륙은 같은 레인에서)")
        if after == "code":
            L.commit(y, "Y S2 코드", {"application/demo/domain_layer/s2.py": "Y2: int = 3\n"})
        elif after == "dirty":
            L.write(y, {"application/demo/domain_layer/s3.py": "Y3: int = 4\n"})
        x = m.tree("wt-x", "lane-x")
        L.own(x)
        expect(fails, f"RD-L7 {tag.upper()} 중간 착륙 뒤 계속하는 실행(표식 없음) → 센다(착륙 근거로 빼지 않는다)", L.dp(x, tag), 2,
               ".dddjango/20261024-0200-feature-demo", "레인 겹침 1 ")
    w1 = TreeLanes(td, "tw1")                               # W1 web 중간 착륙
    w = w1.tree("wt-w", "lane-w")
    L.commit(w, "W 기록 + S1", {
        ".dddjango-web/20261024-0100-web-demo/build-state.json": json.dumps(
            {"phase": "implement", "mode": "modify", "g2_approved": False,
             "slices": [{"name": "s1", "files": ["web/application/demo/a.py", "application/demo/domain_layer/w.py"]}]}),
        ".dddjango-web/20261024-0100-web-demo/server-contract.json": '{"paths": {}}\n'})
    _git(w1.main, "merge", "-q", "--no-ff", "lane-w", "-m", "Merge lane-w — 첫 착륙")
    L.commit(w, "W S2 코드", {"application/demo/domain_layer/w2.py": "W2: int = 1\n"})
    x = w1.tree("wt-x", "lane-x")
    L.own(x)
    expect(fails, "RD-L8 W1 web 중간 착륙(g2_approved false) → 센다", L.dp(x, "w1"), 2,
           ".dddjango-web/20261024-0100-web-demo", "경로 application/demo/domain_layer/w.py", "레인 겹침 1 ")
    r1 = TreeLanes(td, "tr1")                               # R1 착륙 머지를 main 이 되돌린 뒤 레인이 고침 — 이 트리가 만든 폴더
    y = r1.tree("wt-y", "lane-y")
    L.commit(y, "Y G0 기록 + S1 코드", {**_feat("20261024-0200-feature-demo", "demo"),
                                       "application/demo/domain_layer/m.py": "X: int = 2\n"})
    _git(r1.main, "merge", "-q", "--no-ff", "lane-y", "-m", "Merge lane-y")
    _git(r1.main, "revert", "-m", "1", "--no-edit", "HEAD")
    L.commit(y, "Y 고침(다시 착륙 준비)", {"application/demo/domain_layer/m.py": "X: int = 5\n"})
    x = r1.tree("wt-x", "lane-x")
    L.own(x)
    expect(fails, "RD-L9 R1 착륙 머지 revert 뒤 레인이 고침(MH 에 없음 · 이 트리가 만든 폴더) → 센다", L.dp(x, "r1"), 2,
           ".dddjango/20261024-0200-feature-demo", "레인 겹침 1 ", "MH 에서 지워져 뺌 0")
    for tag, dirty in (("r1b", False), ("r1c", True)):      # R1b · R1c — revert 직후 고침 커밋 전 · 미커밋으로 고치는 중(미착륙 커밋 없음)
        r = TreeLanes(td, f"t{tag}")
        y = r.tree("wt-y", "lane-y")
        L.commit(y, "Y G0 기록 + S1 코드", {**_feat("20261024-0200-feature-demo", "demo"),
                                           "application/demo/domain_layer/m.py": "X: int = 2\n"})
        _git(r.main, "merge", "-q", "--no-ff", "lane-y", "-m", "Merge lane-y")
        _git(r.main, "revert", "-m", "1", "--no-edit", "HEAD")
        if dirty:
            L.write(y, {"application/demo/domain_layer/m.py": "X: int = 7\n"})
        x = r.tree("wt-x", "lane-x")
        L.own(x)
        expect(fails, f"RD-L9{tag[-1]} {tag.upper()} 착륙 머지 revert 뒤 레인 고침 커밋 전{'(미커밋으로 고치는 중)' if dirty else ''} — "
               f"미착륙 커밋 없어도 이 트리가 만든 폴더 → 센다", L.dp(x, tag), 2, ".dddjango/20261024-0200-feature-demo",
               "레인 겹침 1 ", "MH 에서 지워져 뺌 0")
    h1 = TreeLanes(td, "th1")                               # H1 주 작업 트리가 main 이 아님(lane-a 가 lane-b 를 받음)
    b = h1.tree("wt-b", "lane-b")
    L.commit(b, "B G0 기록", _feat("20261024-0200-feature-demo", "demo"))
    x = h1.tree("wt-x", "lane-x")
    L.own(x)
    _git(h1.main, "checkout", "-q", "-b", "lane-a")
    _git(h1.main, "merge", "-q", "--no-ff", "lane-b", "-m", "lane-a 가 lane-b 를 받음")
    expect(fails, "RD-L10 H1 주 작업 트리 HEAD 가 main 이 아님 → 센다(한 번)", L.dp(x, "h1"), 2, "레인 겹침 1 ")
    e1 = TreeLanes(td, "te1")                               # E1 다른 트리 빈 web 폴더(보류) · 다른 트리 미커밋 실행 폴더(센다)
    y = e1.tree("wt-y", "lane-y")
    (y / ".dddjango-web" / "20261024-0000-empty").mkdir(parents=True)
    x = e1.tree("wt-x", "lane-x")
    L.own(x)
    expect(fails, "RD-L11 E1 다른 트리 빈 web 폴더 → 보류(build-state.json 을 못 읽는다 · G0 에도 예보 아님)", L.dp(x, "e1"), 2,
           "보류(build-state.json 을 못 읽는다", "보류 1 ")
    L.write(y, _feat("20261024-0100-feature-other", "other"))
    expect(fails, "RD-L12 다른 트리 미커밋 실행 폴더(BC other) → 겹침", L.dp(x, "e1b"), 2,
           ".dddjango/20261024-0100-feature-other — BC other", "레인 겹침 1 ")
    # ── 안 센다 ──
    o1 = TreeLanes(td, "to1")                               # MH 판에 표식 있는 실행의 옛 사본(표식 없음 · 깨진 바이트)
    L.commit(o1.main, "옛 기록(표식 빠짐 · 깨진 글자)", {
        **_feat("20261001-0100-feature-demo", "demo"),
        ".dddjango/20261001-0200-broken-demo/refactor-scope.md":
            "실행 · G0 승인 20261001-0200\n\n- 대상 BC 경로 필터: application/demo/\n".encode("utf-8") + b"\xed\xa0\n"})
    old = o1.tree("wt-old", "old")
    L.commit(o1.main, "기록 바로잡기(표식)", {**_feat("20261001-0100-feature-demo", "demo", TREE_DONE),
                                           **_feat("20261001-0200-broken-demo", "demo", TREE_DONE)})
    x = o1.tree("wt-x", "lane-x")
    L.own(x)
    got = L.dp(x, "o1")
    expect(fails, "RD-L13 MH 판에 끝 표식 있는 실행의 옛 사본(표식 없음 · 깨진 바이트 — 다른 트리 · 옛 main 커밋) → 안 셈",
           got, 0, "레인 겹침 없음", "보류 0 ", "MH 판으로 판정 2")
    L.own(old)
    expect(fails, "RD-L14 그 옛 사본 트리가 이 트리(THIS)여도 MH 판 기록으로 → 안 셈", L.dp(old, "o1t"), 0, "레인 겹침 없음",
           "보류 0 ")
    o2 = TreeLanes(td, "to2")                               # ㉣ MH 에서 지운 실행의 옛 사본(THIS 포함)
    L.commit(o2.main, "폐기할 실행 기록", _feat("20261001-0100-dropped-demo", "demo"))
    x = o2.tree("wt-x", "lane-x")
    y = o2.tree("wt-y", "lane-y")
    _git(o2.main, "rm", "-r", "-q", ".dddjango/20261001-0100-dropped-demo")
    _git(o2.main, "commit", "-qm", "폐기한 실행 기록 지움")
    L.commit(y, "레인 Y 자기 커밋(그 폴더는 건드리지 않음)", {"application/zeta/domain_layer/y.py": "Y: int = 1\n"})
    L.own(x)
    expect(fails, "RD-L15 ㉣ MH 에서 지운 실행의 옛 사본(이 트리 · 미착륙 커밋 있는 다른 트리 — 그 트리가 만든 폴더 아님) → 뺌(THIS 몫 "
           "절 없음)", L.dp(x, "o2"), 0, "레인 겹침 없음", "MH 에서 지워져 뺌 2")
    for tag, record in (("s6", True), ("s8", False), ("rebase", False)):   # S6 · S8 · rebase — main 직접 커밋은 그 레인 몫이 아니다
        s = TreeLanes(td, f"t{tag}")
        x = s.tree("wt-x", "lane-x")
        L.own(x)
        y = s.tree("wt-y", "lane-y") if tag == "rebase" else None
        L.commit(s.main, "main 직접 커밋(demo 코드)", {"application/demo/domain_layer/direct.py": "D: int = 1\n",
                                                   **(_feat("20261001-0100-old-direct", "demo", TREE_DONE) if record else {})})
        y = y or s.tree("wt-y", "lane-y")
        L.commit(y, "Y zeta 실행", {".dddjango/20261024-0200-refactor-zeta/refactor-scope.md":
                                   "실행 · G0 승인 20261024-0200 · 모드 리팩토링 · audit 20261024-0201\n"})
        if tag == "rebase":                                 # main 직접 커밋 앞에서 갈라진 레인이 main 위로 rebase
            _git(y, "rebase", "-q", "main")
        expect(fails, f"RD-L16 {tag.upper()} 나중에 갈라진(또는 rebase 한) 레인(zeta)에 main 직접 커밋 경로를 덧씌우지 않는다 → 겹침 없음",
               L.dp(x, tag), 0, "레인 겹침 없음")
    k1 = TreeLanes(td, "tk1")                               # 링크 · 끊긴 링크 · 한글 경로 · 무시 파일만 다른 폴더(옛 사본 · 안 셈)
    L.commit(k1.main, "옛 기록", {
        **_feat("20261001-0300-한글-실행", "demo"),
        ".dddjango/20261001-0400-dangling/refactor-scope.md": "실행 · G0 승인 20261001-0400\n\n- 대상 BC 경로 필터: application/demo/\n",
        ".dddjango/20261001-0500-ignored/refactor-scope.md": "실행 · G0 승인 20261001-0500\n\n- 대상 BC 경로 필터: application/demo/\n",
        "notes/linked.md": "실행 · G0 승인 20261001-0600\n\n- 대상 BC 경로 필터: application/demo/\n",
        ".gitignore": ".dddjango/**/.runs/\n.dddjango/**/*.png\n"})
    (k1.main / ".dddjango" / "20261001-0600-linked").mkdir(parents=True)
    (k1.main / ".dddjango" / "20261001-0600-linked" / "refactor-scope.md").symlink_to("../../notes/linked.md")
    (k1.main / ".dddjango" / "20261001-0400-dangling" / "design-spec.md").symlink_to("nowhere.md")
    L.commit(k1.main, "링크 기록")
    old = k1.tree("wt-old", "old")
    TreeLanes.write(old, {".dddjango/20261001-0500-ignored/.runs/r.txt": "x\n", ".dddjango/20261001-0500-ignored/shot.png": "png"})
    (k1.main / ".dddjango" / "20261001-0600-linked" / "refactor-scope.md").unlink()
    L.commit(k1.main, "기록 바로잡기(표식)", {
        **_feat("20261001-0300-한글-실행", "demo", TREE_DONE), **_feat("20261001-0400-dangling", "demo", TREE_DONE),
        **_feat("20261001-0500-ignored", "demo", TREE_DONE), **_feat("20261001-0600-linked", "demo", TREE_DONE)})
    x = k1.tree("wt-x", "lane-x")
    L.own(x)
    expect(fails, "RD-L17 링크(링크 글자로 견줌) · 끊긴 링크(실패 아님) · 한글 경로 · 무시 파일만 다른 옛 사본 → MH 판 기록 → 안 셈",
           L.dp(x, "k1"), 0, "레인 겹침 없음", "보류 0 ", "MH 판으로 판정 4")
    z1 = TreeLanes(td, "tz1")                               # 크기 같고 바이트 다른 기록(미커밋) → 자기 변경 → 그 사본
    L.commit(z1.main, "끝난 실행", _feat("20261001-0100-feature-demo", "demo", " · G2 승인 20261001-0900"))
    y = z1.tree("wt-y", "lane-y")
    scope: Path = y / ".dddjango" / "20261001-0100-feature-demo" / "refactor-scope.md"
    before: bytes = scope.read_bytes()
    scope.write_text(before.decode("utf-8").replace("G2 승인", "XX 확인"), encoding="utf-8")
    x = z1.tree("wt-x", "lane-x")
    L.own(x)
    got = L.dp(x, "z1")
    expect(fails, "RD-L18 크기 같고 바이트 다른 기록(미커밋 — 표식 지움) → 자기 변경 → 그 사본 → 센다",
           (got[0] if len(scope.read_bytes()) == len(before) else 9, got[1]), 2, "레인 겹침 1 ")
    g1 = TreeLanes(td, "tg1")                               # 자기 변경 — 미착륙 커밋 경로(디스크 = 그 트리 커밋본이어도)
    L.commit(g1.main, "끝난 실행", _feat("20261001-0100-feature-demo", "demo", TREE_DONE))
    y = g1.tree("wt-y", "lane-y")
    L.commit(y, "같은 폴더로 새 요청(G0 기록)", _feat("20261001-0100-feature-demo", "demo"))
    x = g1.tree("wt-x", "lane-x")
    L.own(x)
    expect(fails, "RD-L19 MH 에서 끝난 폴더를 레인이 새 요청으로 다시 씀(커밋 · 미착륙) → 미착륙 경로 = 자기 변경 → 그 사본 → 센다",
           L.dp(x, "g1"), 2, ".dddjango/20261001-0100-feature-demo — BC demo", "레인 겹침 1 ")
    for tag, landed in (("g4", False), ("g4b", True)):       # 덧씌우기 — 자기 변경 사본 · MH 판 판정 사본 모두
        g = TreeLanes(td, f"t{tag}")
        y = g.tree("wt-y", "lane-y")
        L.commit(y, "Y G0 기록(zeta)", _feat("20261024-0200-feature-zeta", "zeta"))
        if landed:
            _git(g.main, "merge", "-q", "--no-ff", "lane-y", "-m", "Merge lane-y — 첫 착륙")
        L.commit(y, "Y 코드가 demo 를 고침", {"application/demo/domain_layer/m.py": "X: int = 3\n"})
        x = g.tree("wt-x", "lane-x")
        L.own(x)
        expect(fails, f"RD-L20{'b' if landed else ''} {tag.upper()} 레인 실행(zeta · {'중간 착륙 — MH 판 판정' if landed else '미착륙 — 자기 변경'})에 "
               f"그 트리 `T ^MH ^THIS` 경로(demo 코드)를 덧씌움 → 경로 겹침", L.dp(x, tag), 2,
               "경로 application/demo/domain_layer/m.py", "레인 겹침 1 ")
    g6 = TreeLanes(td, "tg6")                               # 표식 밖 기록(design-spec.md)만 미커밋 — 자기 변경
    y = g6.tree("wt-y", "lane-y")
    L.commit(y, "Y G0 기록(zeta)", _feat("20261024-0200-feature-zeta", "zeta"))
    _git(g6.main, "merge", "-q", "--no-ff", "lane-y", "-m", "Merge lane-y — 첫 착륙")
    L.write(y, {".dddjango/20261024-0200-feature-zeta/design-spec.md":
                "# 명세\n\n<!-- machine: file-plan -->\n```paths\nedit application/demo/domain_layer/m.py\n```\n"})
    x = g6.tree("wt-x", "lane-x")
    L.own(x)
    expect(fails, "RD-L22 표식 그대로 · design-spec.md 만 미커밋(file-plan 이 demo) → 기록 파일 다름 = 자기 변경 → 그 사본 → 경로 겹침",
           L.dp(x, "g6"), 2, "경로 application/demo/domain_layer/m.py", "레인 겹침 1 ")
    sp = TreeLanes(td, "tsup", {**TREE_FILES, "application/base/__init__.py": "", "application/base/domain_layer/__init__.py": "",
                                "application/base/domain_layer/m.py": "B: int = 1\n",
                                "application/demo/domain_layer/use.py": "from application.base.domain_layer.m import B\n"})
    L.commit(sp.main, "base 리팩토링 기록(깨진 바이트)", {".dddjango/20260901-refactor-base/refactor-scope.md":
                                                     "실행 · G0 승인 20260901-0100 · 모드 리팩토링 · audit 20260901-0101\n\n깨진 ".encode()
                                                     + b"\xff\xfe" + " 글자\n".encode()})
    x = sp.tree("wt-x", "lane-x")
    L.own(x)
    L.commit(sp.main, "기록 바로잡기", {".dddjango/20260901-refactor-base/refactor-scope.md": "# 옛 기록(실행 줄 없음)\n"})
    expect(fails, "RD-L23 내주는 쪽 기록도 A1 과 같은 판 — 이 트리 옛 사본(깨진 바이트)이 아니라 MH 판으로 읽음 → 미정리 · 미정리 공급자 1",
           L.dp(x, "sup"), 0, "내주는 쪽 base(미정리)", "미정리 공급자 1")
    em = TreeLanes(td, "tem")                               # 끝 표식 판정 캐시는 (종류, blob) — 빈 refactor-scope(끝) ≠ 빈 build-state(보류)
    L.commit(em.main, "빈 기록 둘", {".dddjango/20261001-0100-x/refactor-scope.md": "",
                                    ".dddjango-web/20261001-0100-w/build-state.json": ""})
    x = em.tree("wt-x", "lane-x")
    L.own(x)
    shutil.rmtree(em.main / ".dddjango-web" / "20261001-0100-w")
    expect(fails, "RD-L24 같은 빈 blob — dddjango 표식(끝)과 web 표식(못 읽음 — 보류)을 섞지 않는다 → 보류", L.dp(x, "em"), 2,
           ".dddjango-web/20261001-0100-w — 보류(build-state.json 을 못 읽는다", "보류 1 ")
    lk = TreeLanes(td, "tlk")                               # MH 판 기록이 링크 — MH 트리 안에서 풀면 그 대상(MH 판) · 못 풀면 그 사본(디스크)
    active: str = "실행 · G0 승인 {g}\n\n- 대상 BC 경로 필터: application/demo/\n"
    (lk.root / "outside-run.md").write_text(active.format(g="20261001-0700"), encoding="utf-8")   # 저장소 밖(MH 트리에서 못 풂)
    L.commit(lk.main, "링크 대상(활성)", {"notes/linked.md": active.format(g="20261001-0600")})
    for name, target in (("20261001-0600-linked", "../../notes/linked.md"), ("20261001-0700-outside", "../../../outside-run.md")):
        (lk.main / ".dddjango" / name).mkdir(parents=True)
        (lk.main / ".dddjango" / name / "refactor-scope.md").symlink_to(target)
    L.commit(lk.main, "링크 기록")
    x = lk.tree("wt-x", "lane-x")
    L.own(x)
    for name in ("20261001-0600-linked", "20261001-0700-outside"):    # 주 작업 트리 사본은 없다(미커밋으로 지움)
        shutil.rmtree(lk.main / ".dddjango" / name)
    expect(fails, "RD-L25 MH 판 표식이 링크 — MH 트리 안에서 풀림 → MH 판 대상으로(활성 · 센다) · 저장소 밖이라 못 풂 → 그 사본(디스크 꼬리표)",
           L.dp(x, "lk"), 2, "이 작업 트리(main 판) .dddjango/20261001-0600-linked — BC demo",
           "이 작업 트리(디스크) .dddjango/20261001-0700-outside — BC demo", "레인 겹침 2 ")
    (lk.main / "notes" / "linked.md").write_text(active.format(g="20261001-0600 · build_anchor a · G2 승인 20261002-0100"),
                                                  encoding="utf-8")
    _git(lk.main, "add", "notes/linked.md")
    _git(lk.main, "commit", "-qm", "끝 표식(링크 대상)")
    got = L.dp(x, "lk1")
    expect(fails, "RD-L25a MH 판 링크 대상이 끝(G2) · 이 트리 옛 사본은 같은 링크 글자 · 대상 활성 → MH 판으로 → 안 셈(그 사본을 다시 세지 않음)",
           (got[0] if "20261001-0600-linked" not in got[1] else 9, got[1]), 2, "레인 겹침 1 ")
    (lk.root / "outside-run.md").unlink()
    expect(fails, "RD-L25b 못 푸는 링크가 디스크에서도 끊김 → 보류(끝으로 읽지 않는다 · 디스크 꼬리표)", L.dp(x, "lk2"), 2,
           "이 작업 트리(디스크) .dddjango/20261001-0700-outside — 보류(", "보류 1 ")


def _dispatch_own(repo: Path, own: Path, vs: str) -> None:
    """이 실행을 첫 파견 직전 꼴로 — 명세 «바뀌는 것 목록»(`vs`) · 지원 기록 · `G1 변경 결정` 절과 `G1 변경판 확정` 줄(digest = 지금 스냅숏)."""
    (own / "design-spec.md").write_text("# 설계 명세 — demo\n\n## 바뀌는 것 목록\n\n" + vs + "\n## 다른 BC 편집 목록\n\n없음\n",
                                        encoding="utf-8")
    sup: Path = own / "behavior" / "support" / "20261024T000000Z"
    sup.mkdir(parents=True, exist_ok=True)
    (sup / "run-definition.json").write_text(json.dumps({"version": 1, "argvs": [["pytest"]], "env": {}}), encoding="utf-8")
    (sup / "g0-collect.json").write_text(json.dumps({"version": 1, "verdict": "지원"}), encoding="utf-8")
    digest: str = ra.snapshot_digest(ra.changes_snapshot(own, repo))
    line: str = (own / "refactor-scope.md").read_text(encoding="utf-8").split("\n## G1 변경 결정")[0].rstrip("\n")
    (own / "refactor-scope.md").write_text(line + f"\n\n## G1 변경 결정 2026-10-24 09:50 · 후보 digest {'c' * 12}\n\n"
                                           f"- G1 변경판 확정 2026-10-24 09:55 · digest {digest} · 후보 {'c' * 12}\n", encoding="utf-8")
    _stale_bases(repo, own)


def _stale_bases(repo: Path, own: Path, head: "str | None" = None) -> None:
    """파견 직전 낡음(설계 A4)의 두 기준 — 이 실행 audit `plan.md` 의 `- HEAD` 와 `pregate-report.md` 예보 절의 기준선 SHA 를 `head`
    (없으면 지금 HEAD)로 쓴다(낡음 0 의 바탕 — 기존 파견 직전 사례의 기대 exit 를 바꾸지 않는다)."""
    sha: str = head or _git(repo, "rev-parse", "HEAD").strip()
    am = re.search(r"모드 리팩토링 · audit (\S+)", (own / "refactor-scope.md").read_text(encoding="utf-8"))
    bm = re.search(r"(?:^|-)refactor-([a-z0-9-]+)$", own.name)
    if am:
        (own / "audit" / am.group(1)).mkdir(parents=True, exist_ok=True)
        (own / "audit" / am.group(1) / "plan.md").write_text(
            f"# refactor_audit plan\n\n- BC: `{bm.group(1).replace('-', '_') if bm else 'demo'}`\n- HEAD {sha}\n"
            "- BC 미커밋 변경 0\n", encoding="utf-8")
    (own / "pregate-report.md").write_text(f"## pre-gate 예보 — 2026-10-24T09:40:00Z · design-spec.md\n\n- 기준선 SHA: `{sha}` "
                                           "(--base HEAD)\n- 판정: green\n", encoding="utf-8")


def deps_stage_cases(fails: "list[str]", td: Path) -> None:
    """설계 3판 §A3(F4-117 · 사용자 결정 «가.») · §A2(F4-108) — 도구는 G0 / 파견 직전을 `G1 변경판 확정` 줄 유무로 가른다 ·
    파견 직전 G1 확정판 밖 동작 V(« + » 포함) 0 이면 web 실행의 HTTP 소비로만 선 겹침 · 보류를 세지 않는다(경로 · BC 겹침은 센다) ·
    G0 의 같은 보류는 «예보 보류»(exit 에 넣지 않음) · 앵커 없는 리팩토링 실행 맞물림 · 기록 해독 실패는 경로를 단 보류."""
    repo: Path = _project(td / "dst", DEPS_FILES)
    own: Path = repo / ".dddjango" / TREE_OWN
    own.mkdir(parents=True)
    (own / "refactor-scope.md").write_text(TREE_OWN_LINE, encoding="utf-8")
    dp = lambda n: run(repo, "deps", "demo", "--out", str(own / "deps" / n))  # noqa: E731
    web: Path = repo / ".dddjango-web" / "20261024-0800-home"
    web.mkdir(parents=True)
    (web / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": False, "slices": []}), encoding="utf-8")
    expect(fails, "RD-E1 G0 deps · G1 전 web 실행(계약 · 단위 모름) → 예보 보류(정지 아님 · exit 0)", dp("a1"), 0,
           "예보 보류: 이 작업 트리 .dddjango-web/20261024-0800-home — 보류(server-contract.json 이 없다", "보류 0 ",
           "판정 시점 G0 · 예보 보류 1")
    _dispatch_own(repo, own, V1_TEXT)
    expect(fails, "RD-E2 파견 직전 · G1 확정판 밖 동작 V 0 · G1 전 web 실행 → 세지 않음(exit 0 · 뺌 줄)", dp("a2"), 0,
           "뺌: 이 작업 트리 .dddjango-web/20261024-0800-home", "보류 0 ", "밖 동작 V 0", "web HTTP 소비로만 선 겹침 · 보류 뺌 1")
    _dispatch_own(repo, own, V1_TEXT + V2_TEXT)
    expect(fails, "RD-E3 파견 직전 · 밖 동작 V 1(복합 « + ») · G1 전 web 실행 → 보류(exit 2)", dp("a3"), 2,
           "보류: 이 작업 트리 .dddjango-web/20261024-0800-home — 보류(server-contract.json 이 없다", "밖 동작 V 1")
    (web / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": True,
                                                      "slices": [{"files": ["web/home/views.py"]}]}), encoding="utf-8")
    (web / "server-contract.json").write_text(json.dumps({"paths": {"/api/thing/{id}": {}}}), encoding="utf-8")
    (own / "refactor-scope.md").write_text(TREE_OWN_LINE, encoding="utf-8")
    expect(fails, "RD-E1b G0 · web 실행이 이 BC API 를 소비 · 같은 web 단위(HTTP 소비로만 선 겹침) → 예보 겹침(exit 0)", dp("a1b"), 0,
           "예보 겹침: 이 작업 트리 .dddjango-web/20261024-0800-home — web 단위 web/home", "레인 겹침 없음",
           "판정 시점 G0 · 예보 보류 0 · 예보 겹침 1")
    (web / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": True,
                                                      "slices": [{"files": ["web/home/client.py"]}]}), encoding="utf-8")
    expect(fails, "RD-E1c G0 · web 단위 겹침이 경로 겹침과 함께(HTTP 소비로만 선 겹침 아님) → 겹침(exit 2)", dp("a1c"), 2,
           "겹침: 이 작업 트리 .dddjango-web/20261024-0800-home — 경로 web/home/client.py · web 단위 web/home", "예보 겹침 0")
    (web / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": True,
                                                      "slices": [{"files": ["web/home/views.py"]}]}), encoding="utf-8")
    _dispatch_own(repo, own, V1_TEXT)
    expect(fails, "RD-E4 파견 직전 · V 0 · web 실행이 이 BC API 를 소비 · 같은 web 단위(HTTP 소비로만 선 겹침) → 세지 않음", dp("a4"), 0,
           "레인 겹침 없음", "뺌: 이 작업 트리 .dddjango-web/20261024-0800-home — web 단위 web/home")
    _dispatch_own(repo, own, V1_TEXT + V2_TEXT)
    expect(fails, "RD-E4b 파견 직전 · 밖 동작 V 1 · 같은 HTTP 소비로만 선 겹침 → 겹침(exit 2)", dp("a4b"), 2,
           "겹침: 이 작업 트리 .dddjango-web/20261024-0800-home — web 단위 web/home", "밖 동작 V 1")
    spec: Path = own / "design-spec.md"
    spec.write_text(spec.read_text(encoding="utf-8").replace(V2_TEXT, ""), encoding="utf-8")
    expect(fails, "RD-E4c 파견 직전 · 확정 뒤 명세에서 밖 동작 V 를 지움(지금 스냅숏 ≠ G1 확정 digest — V 모름) → 그대로 셈",
           dp("a4c"), 2, "겹침: 이 작업 트리 .dddjango-web/20261024-0800-home — web 단위 web/home", "밖 동작 V 모름")
    spec.unlink()
    expect(fails, "RD-E4d 파견 직전 · 명세를 못 읽음(스냅숏 실행 불능 — V 모름) → 그대로 셈", dp("a4d"), 2,
           "겹침: 이 작업 트리 .dddjango-web/20261024-0800-home — web 단위 web/home", "밖 동작 V 모름")
    _dispatch_own(repo, own, V1_TEXT)
    (web / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": True,
                                                      "slices": [{"files": ["web/home/views.py",
                                                                            "application/demo/domain_layer/big.py"]}]}),
                                          encoding="utf-8")
    expect(fails, "RD-E5 파견 직전 · V 0 · web 실행이 대상 BC 경로를 고침 → 경로 겹침은 센다", dp("a5"), 2,
           "경로 application/demo/domain_layer/big.py", "레인 겹침 1 ")
    (web / "build-state.json").write_text("{broken", encoding="utf-8")
    expect(fails, "RD-E6 파견 직전 · V 0 · web build-state 를 못 읽음(활성 여부 모름 — HTTP 소비 보류 아님) → 보류", dp("a6"), 2,
           "보류(build-state.json 을 못 읽는다")
    (web / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": True,
                                                      "slices": [{"files": ["web/other/views.py"]}]}), encoding="utf-8")
    (web / "server-contract.json").write_text(json.dumps({"paths": {}}), encoding="utf-8")
    urls: Path = repo / "application/demo/urls.py"
    urls.write_text("from django.urls import path\nurlpatterns = [path(\"x/\", None)]\n", encoding="utf-8")
    expect(fails, "RD-E6b 파견 직전 · V 0 · 이 BC 의 HTTP 소비 관찰 못 함 + web 실행 → 그 보류도 web HTTP 소비 보류라 세지 않음",
           dp("a6b"), 0, "뺌: 이 작업 트리 .dddjango-web/20261024-0800-home — 보류(이 BC 의 HTTP 소비 관찰 못 함", "보류 0 ")
    (own / "refactor-scope.md").write_text(TREE_OWN_LINE, encoding="utf-8")
    expect(fails, "RD-E6c G0 · 이 BC 의 HTTP 소비 관찰 못 함 + web 실행 → 예보 보류", dp("a6c"), 0,
           "예보 보류: 이 작업 트리 .dddjango-web/20261024-0800-home — 보류(이 BC 의 HTTP 소비 관찰 못 함", "보류 0 ")
    urls.unlink()
    _dispatch_own(repo, own, V1_TEXT)
    shutil.rmtree(web)
    # 맞물림 — 앵커 없는 두 리팩토링 실행: 먼저 G0 승인한 쪽이 나아간다(G0 승인 값 · 같으면 폴더 이름 사전순)
    other: Path = repo / ".dddjango" / "20261024-0400-refactor-other"
    other.mkdir(parents=True)
    other_line: str = "실행 · G0 승인 20261024-0400 · 모드 리팩토링 · audit 20261024-0401\n\n- 대상 BC 경로 필터: application/other/\n"
    (other / "refactor-scope.md").write_text(other_line, encoding="utf-8")
    expect(fails, "RD-E7 맞물림 — 이른 쪽(파견 직전): 늦게 G0 승인한 앵커 없는 리팩토링 실행의 겹침 · «file-plan 이 아직 없다» 보류 안 셈",
           dp("a7"), 0, "레인 겹침 없음", "보류 0 ", "늦게 G0 승인한 리팩토링 실행 뺌 1")
    expect(fails, "RD-E8 맞물림 — 늦은 쪽: 이른 실행은 센다(exit 2)",
           run(repo, "deps", "other", "--out", str(other / "deps" / "a8")), 2, f".dddjango/{TREE_OWN} — BC demo")
    (other / "refactor-scope.md").write_text(other_line.replace("audit 20261024-0401", "audit 20261024-0401 · build_anchor abc"),
                                             encoding="utf-8")
    expect(fails, "RD-E9 맞물림 — 앵커 있는 상대는 늦게 G0 승인했어도 센다", dp("a9"), 2, "20261024-0400-refactor-other — BC ")
    (other / "refactor-scope.md").write_text(other_line.replace("G0 승인 20261024-0400", "G0 승인 20261024-0200")
                                             + "\n## 재개 G0 20261024-0500\n", encoding="utf-8")
    expect(fails, "RD-E10 맞물림 — 비교 값은 실행 줄 G0 승인(잇기 재개 G0 가 더 늦어도) → 이른 상대 → 센다", dp("a10"), 2,
           "20261024-0400-refactor-other — BC ")
    shutil.rmtree(other)
    same: Path = repo / ".dddjango" / "20261024-0300-refactor-alpha"
    same.mkdir(parents=True)
    (same / "refactor-scope.md").write_text(other_line.replace("G0 승인 20261024-0400", "G0 승인 20261024-0300"), encoding="utf-8")
    expect(fails, "RD-E11 맞물림 — G0 승인 값이 같으면 폴더 이름 사전순(-alpha 가 먼저) → 센다", dp("a11"), 2,
           "20261024-0300-refactor-alpha — BC ")
    shutil.rmtree(same)
    after: Path = repo / ".dddjango" / "20261024-0300-refactor-zzz"
    after.mkdir(parents=True)
    (after / "refactor-scope.md").write_text(other_line.replace("G0 승인 20261024-0400", "G0 승인 20261024-0300"), encoding="utf-8")
    expect(fails, "RD-E11b 맞물림 — G0 승인 값이 같고 상대 폴더 이름이 사전순 뒤(-zzz) → 늦은 쪽 → 안 셈", dp("a11b"), 0,
           "레인 겹침 없음", "늦게 G0 승인한 리팩토링 실행 뺌 1")
    shutil.rmtree(after)
    twin: Path = td / "dst-twin"                            # G0 승인 값도 폴더 이름도 같은 다른 실행(실행 줄 다름) — 늦은 쪽 아님 → 센다
    _git(repo, "worktree", "add", "-q", "-b", "twin", str(twin))
    (twin / ".dddjango" / TREE_OWN).mkdir(parents=True)
    (twin / ".dddjango" / TREE_OWN / "refactor-scope.md").write_text(
        TREE_OWN_LINE.replace("audit 20261024-0301", "audit 20261024-0399"), encoding="utf-8")
    expect(fails, "RD-E11c 맞물림 — G0 승인 값 · 폴더 이름이 모두 같은 다른 실행(실행 줄 다름) → 늦은 쪽 아님 → 센다", dp("a11c"), 2,
           f".dddjango/{TREE_OWN} — BC demo")
    _git(repo, "worktree", "remove", "--force", str(twin))
    # 기록 해독 실패(F4-108) — 경로를 단 보류 · exit 2(실행 불능 아님)
    bad: Path = repo / ".dddjango" / "20261024-0100-feature-x"
    (bad / "audit" / "20261024-0101").mkdir(parents=True)
    (bad / "refactor-scope.md").write_bytes("실행 · G0 승인 20261024-0100\n".encode("utf-8") + b"\xff\xfe\n")
    expect(fails, "RD-E12 다른 실행 refactor-scope.md 깨진 바이트 → 보류(경로 · 바이트 위치) · exit 2", dp("a12"), 2,
           "20261024-0100-feature-x/refactor-scope.md 를 UTF-8 로 못 읽는다(바이트 ", "재개 조건: 그 기록을 UTF-8 로 고친 뒤 다시 시작")
    (bad / "refactor-scope.md").write_text("실행 · G0 승인 20261024-0100 · 모드 리팩토링 · audit 20261024-0101\n\n"
                                           "- 대상 BC 경로 필터: application/zeta/\n", encoding="utf-8")
    (bad / "audit" / "20261024-0101" / "plan.md").write_bytes(b"# p\n\n- BC: `zeta`\xc3\n")
    expect(fails, "RD-E13 다른 실행 audit plan.md 깨진 바이트 → 보류(이웃 아닌 BC 여도) · exit 2", dp("a13"), 2,
           "audit/20261024-0101/plan.md 를 UTF-8 로 못 읽는다(바이트 ")
    (bad / "audit" / "20261024-0101" / "plan.md").write_text("# p\n\n- BC: `zeta`\n", encoding="utf-8")
    (bad / "design-spec.md").write_bytes(b"# spec \x80\n")
    expect(fails, "RD-E14 다른 실행 design-spec.md 깨진 바이트 → 보류 · exit 2", dp("a14"), 2,
           "20261024-0100-feature-x/design-spec.md 를 UTF-8 로 못 읽는다(바이트 7)")
    shutil.rmtree(bad)
    wbad: Path = repo / ".dddjango-web" / "20261024-0000-home"
    wbad.mkdir(parents=True)
    (wbad / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": True,
                                                       "slices": [{"files": ["web/other/views.py"]}]}), encoding="utf-8")
    (wbad / "server-contract.json").write_text(json.dumps({"paths": {}}), encoding="utf-8")
    (wbad / "design-spec.md").write_bytes(b"# web spec \xe9\n")
    expect(fails, "RD-E15 web 실행 design-spec.md 깨진 바이트(S9) → 보류(HTTP 소비 보류 아님 — G0 에도) · exit 2", dp("a15"), 2,
           ".dddjango-web/20261024-0000-home/design-spec.md 를 UTF-8 로 못 읽는다")
    shutil.rmtree(wbad)
    sup: Path = repo / ".dddjango" / "20260901-refactor-base"
    sup.mkdir(parents=True)
    (sup / "refactor-scope.md").write_bytes(b"\xff refactor-scope\n")
    expect(fails, "RD-E16 내주는 쪽 기록 깨진 바이트 → 내주는 쪽 «못 읽음(<경로>)»(실행 불능 아님 · 미정리 공급자 수에 듦) · 그 실행 폴더도 해독 보류",
           dp("a16"), 2, "내주는 쪽 base(못 읽음(", "미정리 공급자 1 ", "20260901-refactor-base/refactor-scope.md 를 UTF-8 로 못 읽는다(바이트 0)")
    shutil.rmtree(sup)
    web.mkdir(parents=True)
    (web / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": False, "slices": []}), encoding="utf-8")
    expect(fails, "RD-E17 이 실행 폴더가 없음(--out 이 .dddjango 밖) → 판정 시점 모름 — web HTTP 소비 보류도 그대로 셈",
           run(repo, "deps", "demo", "--out", str(td / "dst-ownless")), 2,
           "\n  보류: 이 작업 트리 .dddjango-web/20261024-0800-home — 보류(server-contract.json 이 없다", "판정 시점 모름")


# 설계 F4-118 2판 + 좁은 확인 N1(dddjango 2.26.1) — deps 레인 겹침을 «실제로 만나는 자리»로 좁힘: 공급 BC(대상이 쓰기만 하는 BC)는
# BC 가 아니라 공급 면(창구 · 계약 · 이벤트 전부 + 대상 파일이 가리키는 파일 · 이름 사슬 · 대상 운영 코드의 HTTP 호출)과 만날 때만 센다 ·
# 공급 BC 기능 실행의 고침 목록은 build_anchor + 이번 실행 명세(pregate-report 마지막 실행 경계 뒤 예보 절)일 때만 믿는다 · web 단위는
# dddjango-web 단위 규칙. 사례 이름(C · B · X · Y · F · W · S5)은 설계 2판 §2 · §6 과 좁은 확인의 이름 그대로다(접두 `RD-F118`).
FACE_OWN: str = "20261025-0000-refactor-demo"
FACE_OWN_LINE: str = "실행 · G0 승인 20261025-0000 · 모드 리팩토링 · audit 20261025-0001\n"
FACE_SUP: str = "20261025-0100-base-feature"
FACE_OHS: str = "application/base/driving_layer/open_host_service"
FACE_CONTROLLER: str = ("from ninja_extra import api_controller, route\n\n\n@api_controller(\"{prefix}\")\nclass {name}:\n"
                        "    @route.get(\"/\")\n    def get(self) -> dict:\n        return {{}}\n")
FACE_FILES: "dict[str, str]" = {
    "application/__init__.py": "",
    "application/demo/__init__.py": "",
    "application/demo/domain_layer/__init__.py": "",
    "application/demo/domain_layer/policy.py": "def rule(x: int) -> int:\n    return x\n",
    "application/demo/driven_layer/__init__.py": "",
    "application/demo/driven_layer/adapter/anticorruption_layer/base/base_adapter.py": (
        f"from {FACE_OHS.replace('/', '.')}.base_service import f\n\n\nY = f\n"),
    "application/demo/driving_layer/api/thing/thing_controller.py": FACE_CONTROLLER.format(prefix="/thing", name="ThingController"),
    "application/base/__init__.py": "",
    f"{FACE_OHS}/base_service.py": "from application.base.domain_layer.inner import g\n\n\ndef f() -> int:\n    return g()\n",
    f"{FACE_OHS}/other_service.py": "def h() -> int:\n    return 4\n",
    f"{FACE_OHS}/contract/thing_contract.py": "class ThingDto:\n    pass\n",
    "application/base/domain_layer/inner.py": "def g() -> int:\n    return 2\n",
    "application/base/domain_layer/unrelated.py": "Z: int = 3\n",
    "application/base/composition_root/wiring.py": "W: int = 1\n",
    "application/other/__init__.py": "",
    "application/other/domain_layer/uses_demo.py": "from application.demo.domain_layer.policy import rule\n\n\nR = rule\n",
    "application/other/domain_layer/x.py": "X: int = 1\n",
    "web/__init__.py": "",
    "web/application/__init__.py": "",
    "web/application/admin/__init__.py": "",
    "web/application/admin/op_a/infra_layer/data_source/a_data_source.py": "URL: str = \"/api/thing/1\"\n",
    "web/application/admin/op_a/presentation_layer/view/a_view.py": "V: int = 1\n",
    "web/application/client/ad_page/presentation_layer/view/ad_view.py": "V: int = 2\n",
}
FACE_V_OUT: str = "- V1 · 밖 동작 · 근거 M1 #1 · 슬라이스 S1\n  - 전 → 후: 없는 thing 200 → 404\n  - 영향: HTTP 소비 1\n"
FACE_SECTION: str = "## pre-gate 예보 — 2026-10-25T01:00:00Z · design-spec.md\n\n- 기준선 SHA: `new`\n\n"
FACE_OLD_SECTION: str = "## pre-gate 예보 — 2026-10-20T01:00:00Z · design-spec.md\n\n- 기준선 SHA: `old`\n\n"
FACE_OLD_BASE: str = "- pre-gate 기준선 — aaaaaaaa · 2026-10-20T02:00:00Z\n"
FACE_NEW_BASE: str = "- pre-gate 기준선 — bbbbbbbb · 2026-10-25T02:00:00Z\n"
FACE_TRUST: "dict[str, object]" = {"anchor": True, "report": FACE_SECTION}
FACE_DROP: str = "· 공급 면과 만남 0 — 세지 않는다(서는 장치: 그 실행의 G2 전체 suite 가 지금 대상 시험을 돈다"
FACE_MODIFY_PREV: str = ("\n## 앞 실행\n\n- 실행 · G0 승인 20261020-1000 · build_anchor abc · G2 승인 20261021-1000\n")


class FaceLane:
    """공급 면 사례 — 합성 저장소(대상 demo · 공급 base · 받는 쪽 other · web area admin/op_a(소비) · client/ad_page) + 이 실행 폴더."""

    def __init__(self, td: Path, name: str, extra: "dict[str, str] | None" = None) -> None:
        self.repo: Path = _project(td / name, {**FACE_FILES, **(extra or {})})
        self.own: Path = self.repo / ".dddjango" / FACE_OWN
        self.own.mkdir(parents=True)
        self.to_g0()

    def to_g0(self) -> None:
        (self.own / "refactor-scope.md").write_text(FACE_OWN_LINE, encoding="utf-8")

    def dispatch(self) -> None:
        """이 실행을 첫 파견 직전 꼴로(G1 확정 줄 · 밖 동작 V 1)."""
        self.to_g0()
        _dispatch_own(self.repo, self.own, FACE_V_OUT)

    def sup(self, plan: "list[str] | None", *, anchor: bool = False, report: "str | bytes | None" = None,
            g0: str = "20261025-0100", name: str = FACE_SUP, bc: str = "base", prev: str = "", line: "str | None" = None) -> Path:
        """다른 실행 기록(실행 줄 · 대상 BC 경로 필터 · 명세 file-plan · pregate-report.md) — None 이면 그 파일을 지운다."""
        folder: Path = self.repo / ".dddjango" / name
        folder.mkdir(parents=True, exist_ok=True)
        head: str = line or (f"실행 · G0 승인 {g0}" + (" · build_anchor abc123" if anchor else ""))
        (folder / "refactor-scope.md").write_text(f"{head}\n\n- 대상 BC 경로 필터: application/{bc}/\n{prev}", encoding="utf-8")
        spec: Path = folder / "design-spec.md"
        if plan is None:
            spec.unlink(missing_ok=True)
        else:
            spec.write_text("# s\n\n<!-- machine: file-plan -->\n```paths\n" + "".join(f"update {p}\n" for p in plan) + "```\n",
                            encoding="utf-8")
        rep: Path = folder / "pregate-report.md"
        if report is None:
            rep.unlink(missing_ok=True)
        elif isinstance(report, bytes):
            rep.write_bytes(report)
        else:
            rep.write_text(report, encoding="utf-8")
        return folder

    def web(self, files: "list[str]", contract: "dict | None" = None, name: str = "20261025-0200-web-x") -> Path:
        folder: Path = self.repo / ".dddjango-web" / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "build-state.json").write_text(json.dumps({"g2_approved": False, "g1_approved": True,
                                                            "slices": [{"files": files}]}), encoding="utf-8")
        (folder / "server-contract.json").write_text(json.dumps(contract if contract is not None else {"paths": {}}),
                                                     encoding="utf-8")
        return folder

    def dp(self, tag: str) -> "tuple[int, str]":
        return run(self.repo, "deps", "demo", "--out", str(self.own / "deps" / tag))

    def data(self, tag: str) -> dict:
        p: Path = self.own / "deps" / tag / "deps.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def deps_face_cases(fails: "list[str]", td: Path) -> None:
    """설계 2판 §4-2 공급 면 ①~⑤ · §4-4 판정 — 반례 C1 ~ C4 · 1판 목록 F1 ~ F15 · S5 · 면 넓힘(이름 사슬 상한 · 못 읽은 파일)."""
    sup_ex: str = f"이 작업 트리 .dddjango/{FACE_SUP}"
    # ── 공급 BC 창구 · 계약 · 대상이 가리키는 파일 ──
    lane = FaceLane(td, "f-c1")
    lane.sup([f"{FACE_OHS}/other_service.py"])
    expect(fails, "RD-F118 C1 공급 BC 의 다른 창구만 고치는 기능 실행 초안(앵커 없음) · G0 → 예보 보류(첫 파견 전 · 면 파일 만남 꼬리) · exit 0",
           lane.dp("c1"), 0, f"예보 보류: {sup_ex} — 보류(공급 BC base 를 고치는 기능 실행 — 고침 목록 모름: 첫 파견 전 — "
           "명세가 아직 G1 승인본이 아니다 · 지금 명세 file-plan 이 면 파일 1 과 만남) · 첫 파견 직전 deps 가 다시 본다(",
           "판정 시점 G0 · 예보 보류 1 · 예보 겹침 0 · 예보 보류 가운데 공급 BC 고침 목록 모름 1", "보류 0 ")
    lane.sup([f"{FACE_OHS}/other_service.py"], **FACE_TRUST)
    expect(fails, "RD-F118 C1t 같은 · 이번 실행 승인 명세(앵커 + 이번 실행 pre-gate 절) · G0 → 공급 면 겹침(창구 전부 — B2)", lane.dp("c1t"),
           2, f"겹침: {sup_ex} — 공급 면 {FACE_OHS}/other_service.py → 순서: 그 레인 착륙 뒤")
    lane.dispatch()
    expect(fails, "RD-F118 C1d 같은 · 파견 직전 → 공급 면 겹침", lane.dp("c1d"), 2, f"— 공급 면 {FACE_OHS}/other_service.py")
    lane.sup(["application/base/domain_layer/unrelated.py"], **FACE_TRUST)
    expect(fails, "RD-F118 F1 · B1c 승인 명세가 공급 면 밖만 고침 · 파견 직전 → 세지 않음(뺌 줄 · 면 밖 뺌 1) · exit 0", lane.dp("f1"), 0,
           f"뺌: {sup_ex} — 공급 BC base · 고침 1 파일 {FACE_DROP}", "면 밖 뺌 1", "레인 겹침 없음")
    got: dict = lane.data("f1")
    expect(fails, "RD-F118 F1b deps.json face_free 1 · supplier_faces(창구 · 계약 전부) · our_bcs 에 공급 BC 없음",
           (0 if got.get("face_free") == 1 and f"{FACE_OHS}/contract/thing_contract.py" in got.get("supplier_faces", {}).get("base", [])
            and "base" not in got.get("our_bcs", []) and "other" in got.get("our_bcs", []) else 9, json.dumps(got, ensure_ascii=False)),
           0)
    lane.sup([f"{FACE_OHS}/base_service.py"], **FACE_TRUST)
    expect(fails, "RD-F118 F2 · B1d 승인 명세가 대상이 import 하는 창구 파일을 고침 → 공급 면 겹침", lane.dp("f2"), 2,
           f"공급 면 {FACE_OHS}/base_service.py")
    lane.sup([f"{FACE_OHS}/contract/thing_contract.py"], **FACE_TRUST)
    expect(fails, "RD-F118 F3 대상은 창구 서비스만 import · 실행이 창구 계약 모듈을 고침 → 공급 면 겹침", lane.dp("f3"), 2,
           f"공급 면 {FACE_OHS}/contract/thing_contract.py")
    lane.sup(["application/base/domain_layer/inner.py", "application/base/composition_root/wiring.py"], **FACE_TRUST)
    # 까닭(설계 2판 §1 (나) · §8-1 — 받아들인 갈래): 창구 뒤 도메인 · 합성만 고친 실행은 세지 않는다 — 서는 장치는 그 실행의 G2 전체
    # suite(지금 대상 시험)뿐이고 안 센 실행은 뺌 줄로 남는다.
    expect(fails, "RD-F118 F4 창구 뒤 도메인 · 합성 파일만 고침(받아들인 갈래) → 세지 않음(뺌 줄)", lane.dp("f4"), 0,
           f"뺌: {sup_ex} — 공급 BC base · 고침 2 파일 {FACE_DROP}")
    lane.sup(["application/other/domain_layer/x.py"], bc="other", name="20261025-0110-other-feature", **FACE_TRUST)
    expect(fails, "RD-F118 F8 받는 쪽 BC(other — demo 를 import) 기능 실행이 무관 파일만 → BC 겹침(그대로)", lane.dp("f8"), 2,
           ".dddjango/20261025-0110-other-feature — BC other")
    shutil.rmtree(lane.repo / ".dddjango" / "20261025-0110-other-feature")
    lane.sup(None, line="실행 · G0 승인 20261025-0100 · 모드 리팩토링 · audit 20261025-0101 · build_anchor abc",
             name="20261025-0100-refactor-base")
    (lane.repo / ".dddjango" / "20261025-0100-refactor-base" / "audit" / "20261025-0101").mkdir(parents=True)
    (lane.repo / ".dddjango" / "20261025-0100-refactor-base" / "audit" / "20261025-0101" / "plan.md").write_text(
        "# p\n\n- BC: `base`\n", encoding="utf-8")
    expect(fails, "RD-F118 F7 공급 BC 리팩토링 실행(앵커 있음) → BC 겹침(엮인 BC 는 동시에 돌리지 않는다)", lane.dp("f7"), 2,
           ".dddjango/20261025-0100-refactor-base — BC base (리팩토링 실행 — 엮인 BC)")
    shutil.rmtree(lane.repo / ".dddjango" / "20261025-0100-refactor-base")
    lane.sup([f"{FACE_OHS}/other_service.py"], **FACE_TRUST)
    # ── 다시 내보내기 · 이름 사슬(I2 · 좁은 확인 사소 1) ──
    re_export: "dict[str, str]" = {
        "application/demo/domain_layer/uses_thing.py": "from application.base.domain_layer.facade import Thing\n\n\nT = Thing\n",
        "application/base/domain_layer/impl.py": "class Thing:\n    pass\n"}
    for tag, facade, label in (
            ("c2t", "from application.base.domain_layer.impl import Thing\n", "이름 사슬(facade → impl.Thing)"),
            ("y1", "try:\n    from application.base.domain_layer.impl import Thing\nexcept ImportError:  # pragma: no cover\n"
                   "    Thing = None\n", "try 블록 안 다시 내보내기"),
            ("y2", "from application.base.domain_layer import impl\n\nThing = impl.Thing\n", "대입 다시 내보내기(Thing = impl.Thing)")):
        ln = FaceLane(td, f"f-{tag}", {**re_export, "application/base/domain_layer/facade.py": facade})
        ln.sup(["application/base/domain_layer/impl.py"], **FACE_TRUST)
        ln.dispatch()
        expect(fails, f"RD-F118 {tag.upper()} {label} · 실행이 정의 모듈 impl.py(승인 명세) · 파견 직전 → 공급 면 겹침", ln.dp(tag), 2,
               "공급 면 application/base/domain_layer/impl.py")
    ln = FaceLane(td, "f-c2bt", {"application/demo/domain_layer/uses_thing.py":
                                 "from application.base.domain_layer import facade\n\n\nT = facade\n",
                                 "application/base/domain_layer/facade.py": "from application.base.domain_layer.impl import Thing\n",
                                 "application/base/domain_layer/impl.py": "class Thing:\n    pass\n"})
    ln.sup(["application/base/domain_layer/impl.py"], **FACE_TRUST)
    expect(fails, "RD-F118 C2bt 모듈째 import 한 파사드(import 만으로 된 파일) · 실행이 impl.py → 공급 면 겹침", ln.dp("c2bt"), 2,
           "공급 면 application/base/domain_layer/impl.py")
    scan = ra.DepsScan(ln.repo)
    saved_cap: int = ra.FACE_CHAIN_CAP
    try:
        ra.FACE_CHAIN_CAP = 0
        cap_faces, cap_why = ra._supplier_faces(ra.DepsScan(lane.repo), "demo", {"base"})
    finally:
        ra.FACE_CHAIN_CAP = saved_cap
    expect(fails, "RD-F118 S-cap 이름 사슬 상한에 닿으면 조용히 멈추지 않고 그 BC 전체를 면으로(까닭 기록)",
           (0 if cap_faces.get("base") == {"application/base/"} and "이름 사슬 상한 0 걸음" in cap_why.get("base", "") else 9,
            f"{cap_faces} {cap_why}"), 0)
    faces, why = ra._supplier_faces(scan, "demo", {"base"})
    expect(fails, "RD-F118 S-cap2 상한 안이면 넓히지 않는다(파사드 · 정의 모듈만)",
           (0 if not why and "application/base/domain_layer/impl.py" in faces["base"]
            and "application/base/domain_layer/unrelated.py" not in faces["base"] else 9, f"{faces} {why}"), 0)
    import contextlib
    import io
    buf = io.StringIO()
    ln2 = FaceLane(td, "f-cap", {**re_export, "application/base/domain_layer/facade.py":
                                 "from application.base.domain_layer.impl import Thing\n"})
    ln2.sup(["application/base/domain_layer/unrelated.py"], **FACE_TRUST)
    try:
        ra.FACE_CHAIN_CAP = 1
        with contextlib.redirect_stdout(buf):
            cap_out: Path = ln2.own / "deps" / "cap"
            code: int = ra.cmd_deps(ln2.repo, "demo", cap_out, _deps_at(("deps", "demo", "--out", str(cap_out))))
    finally:
        ra.FACE_CHAIN_CAP = saved_cap
    expect(fails, "RD-F118 S-cap3 상한에 닿은 실행 — 출력에 «면 넓힘:» 한 줄 · 그 BC 의 면 밖 파일을 고친 실행도 공급 면 겹침(안전 쪽)",
           (code, buf.getvalue()), 2, "  면 넓힘: 공급 BC base — 이름 사슬 상한 1 걸음에 닿음 — 그 BC 전체를 공급 면으로 센다",
           "공급 면 application/base/domain_layer/unrelated.py")
    # ── 합성 경로(I1) · 마이그레이션 의존 ──
    apps: str = ("from django.apps import AppConfig\n\n\nclass BaseConfig(AppConfig):\n    name = \"application.base\"\n"
                 "    label = \"base\"\n")
    ln = FaceLane(td, "f-c3", {"application/base/apps.py": apps, "application/base/models.py": "class ThingModel:\n    pass\n",
                               "application/base/migrations/__init__.py": "",
                               "application/base/migrations/0001_x.py": "X: int = 1\n",
                               "application/base/driven_layer/__init__.py": "", "application/base/driven_layer/repo.py": "R: int = 1\n",
                               "application/demo/driven_layer/django_demo/models.py": "FK: str = \"base.ThingModel\"\n",
                               "application/demo/driven_layer/django_demo/migrations/0001_initial.py":
                                   "dependencies = [(\"base\", \"0001_x\")]\n"})
    ln.sup(["application/base/models.py"], **FACE_TRUST)
    expect(fails, "RD-F118 C3t 브라운필드 모델(application/base/models.py) · 대상 \"base.ThingModel\" → label 선언 apps.py 폴더의 models · "
           "공급 면 겹침", ln.dp("c3t"), 2, "공급 면 application/base/models.py")
    ln.sup(["application/base/migrations/0001_x.py"], **FACE_TRUST)
    expect(fails, "RD-F118 C3m 브라운필드 마이그레이션 의존(\"base\", \"0001_x\") · 실행이 그 마이그레이션을 고침 → 공급 면 겹침", ln.dp("c3m"),
           2, "공급 면 application/base/migrations/0001_x.py")
    ln.sup(["application/base/migrations/0002_y.py", "application/base/driven_layer/repo.py"], **FACE_TRUST)
    expect(fails, "RD-F118 C3n 브라운필드 — 새 마이그레이션 더하기 · driven_layer 안쪽만 → 세지 않음(뺌 줄)", ln.dp("c3n"), 0,
           f"뺌: {sup_ex} — 공급 BC base · 고침 2 파일 {FACE_DROP}")
    std: "dict[str, str]" = {
        "application/base/apps.py": apps.replace("application.base", "application.base.driven_layer.django_base"),
        "application/base/driven_layer/django_base/models/thing_model.py": "class ThingModel:\n    pass\n",
        "application/base/driven_layer/django_base/migrations/0001_x.py": "X: int = 1\n",
        "application/base/test/factories.py": "def make() -> int:\n    return 1\n",
        "application/demo/driven_layer/django_demo/models/fk.py": "FK: str = \"base.ThingModel\"\n",
        "application/demo/driven_layer/django_demo/migrations/0001_initial.py": "dependencies = [(\"base\", \"0001_x\")]\n",
        "application/demo/test/test_make.py": "from application.base.test.factories import make\n\n\ndef test_make() -> None:\n"
                                              "    assert make()\n"}
    ln = FaceLane(td, "f-std", std)
    ln.sup(["application/base/driven_layer/django_base/models/thing_model.py"], **FACE_TRUST)
    expect(fails, "RD-F118 F11 모델 라벨 — 대상이 \"base.ThingModel\" · 실행이 base models 고침 → 공급 면 겹침", ln.dp("f11"), 2,
           "공급 면 application/base/driven_layer/django_base/models/thing_model.py")
    ln.sup(["application/base/driven_layer/django_base/migrations/0002_y.py"], **FACE_TRUST)
    expect(fails, "RD-F118 F12 마이그레이션 의존 (\"base\", \"0001_x\") · 실행이 base 0002 를 더함 → 세지 않음", ln.dp("f12"), 0,
           f"뺌: {sup_ex} — 공급 BC base · 고침 1 파일 {FACE_DROP}")
    ln.sup(["application/base/driven_layer/django_base/migrations/0001_x.py"], **FACE_TRUST)
    expect(fails, "RD-F118 F12b 같은 · 실행이 의존한 0001_x 를 고침 → 공급 면 겹침", ln.dp("f12b"), 2,
           "공급 면 application/base/driven_layer/django_base/migrations/0001_x.py")
    ln.sup(["application/base/test/factories.py"], **FACE_TRUST)
    expect(fails, "RD-F118 F13 대상 시험이 base 재료(factory)를 import · 실행이 그 파일 고침 → 공급 면 겹침", ln.dp("f13"), 2,
           "공급 면 application/base/test/factories.py")
    (ln.repo / "application/demo/domain_layer/gone.py").write_text("PATH: str = \"application.base.gone_module.thing\"\n",
                                                                    encoding="utf-8")
    ln.sup(["application/base/domain_layer/unrelated.py"], **FACE_TRUST)
    expect(fails, "RD-F118 F15 대상이 가리키는 점 경로 문자열의 모듈이 없음 → 그 BC 전체가 면(모르면 넓게) → 공급 면 겹침", ln.dp("f15"), 2,
           "공급 면 application/base/domain_layer/unrelated.py")
    ln = FaceLane(td, "f-auth", {"config/settings.py": "AUTH_USER_MODEL: str = \"base.User\"\n",
                                 "application/base/apps.py": apps.replace("application.base",
                                                                          "application.base.driven_layer.django_base"),
                                 "application/base/driven_layer/django_base/models/user.py": "class User:\n    pass\n",
                                 "application/demo/domain_layer/owner.py": "from django.conf import settings\n\n\n"
                                                                            "OWNER = settings.AUTH_USER_MODEL\n"})
    ln.sup(["application/base/driven_layer/django_base/models/user.py"], **FACE_TRUST)
    expect(fails, "RD-F118 F11b AUTH_USER_MODEL — 대상이 settings.AUTH_USER_MODEL(base) · 실행이 base models 고침 → 공급 면 겹침",
           ln.dp("f11b"), 2, "공급 면 application/base/driven_layer/django_base/models/user.py")
    # ── 패키지 · 같은 이름 파일과 폴더(S5) ──
    ln = FaceLane(td, "f-pkg", {"application/base/domain_layer/pkg/__init__.py": "P: int = 1\n",
                                "application/base/domain_layer/dual.py": "class Thing:\n    pass\n",
                                "application/base/domain_layer/dual/helper.py": "H: int = 1\n",
                                "application/demo/domain_layer/uses_pkg.py": "import application.base.domain_layer.pkg\n",
                                "application/demo/domain_layer/uses_dual.py":
                                    "from application.base.domain_layer.dual import Thing\n\n\nT = Thing\n"})
    ln.sup(["application/base/domain_layer/pkg/new_module.py"], **FACE_TRUST)
    expect(fails, "RD-F118 F5 패키지 import(pkg/__init__.py) · 실행이 pkg/ 아래 새 파일을 더함 → 공급 면 겹침(폴더 접두)", ln.dp("f5"), 2,
           "공급 면 application/base/domain_layer/pkg/new_module.py")
    ln.sup(["application/base/domain_layer/dual/helper.py"], **FACE_TRUST)
    expect(fails, "RD-F118 S5 같은 이름의 dual.py 와 dual/ 가 함께 있음 → 둘 다 면 · 실행이 dual/helper.py → 공급 면 겹침", ln.dp("s5"), 2,
           "공급 면 application/base/domain_layer/dual/helper.py")
    ln.sup(["application/base/domain_layer/dual.py"], **FACE_TRUST)
    expect(fails, "RD-F118 S5b 같은 · 실행이 dual.py → 공급 면 겹침", ln.dp("s5b"), 2, "공급 면 application/base/domain_layer/dual.py")
    # ── HTTP(I3 · D2 · ⑤) ──
    http: "dict[str, str]" = {
        "application/base/driving_layer/web_api/thing_controller.py":
            FACE_CONTROLLER.format(prefix="/basething", name="BaseThingController"),
        "application/demo/driven_layer/adapter/http_client.py": "URL: str = \"/api/basething/1\"\n"}
    ln = FaceLane(td, "f-c4", http)
    ln.sup(["application/base/driving_layer/web_api/thing_controller.py"], **FACE_TRUST)
    expect(fails, "RD-F118 C4t 공급 BC API 가 driving_layer/api/ 밖(접두 선언 파일) · 대상 운영 코드가 부름 → 공급 면 겹침", ln.dp("c4t"), 2,
           "공급 면 application/base/driving_layer/web_api/thing_controller.py")
    ln = FaceLane(td, "f-f14", {"application/base/driving_layer/api/thing/base_controller.py":
                                FACE_CONTROLLER.format(prefix="/basething", name="BaseThingController"),
                                "application/demo/driven_layer/adapter/http_client.py": "URL: str = \"/api/basething/1\"\n"})
    ln.sup(["application/base/driving_layer/api/thing/base_controller.py"], **FACE_TRUST)
    expect(fails, "RD-F118 F14 대상 운영 코드가 base API 를 URL 문자열로 부름 · 실행이 base driving_layer/api/ 고침 → 공급 면 겹침",
           ln.dp("f14"), 2, "공급 면 application/base/driving_layer/api/thing/base_controller.py")
    client: Path = ln.repo / "application/demo/driven_layer/adapter/http_client.py"
    client.write_text("\"\"\"GET /api/basething/1 을 부른다(문서).\"\"\"\nURL: str = \"\"\n", encoding="utf-8")
    expect(fails, "RD-F118 F14b 같은 URL 이 대상 운영 코드의 문서 문자열에만 → 세지 않음", ln.dp("f14b"), 0, f"뺌: {sup_ex}")
    client.unlink()
    (ln.repo / "application/demo/test/test_http.py").parent.mkdir(parents=True, exist_ok=True)
    (ln.repo / "application/demo/test/test_http.py").write_text("URL: str = \"/api/basething/1\"\n", encoding="utf-8")
    expect(fails, "RD-F118 F14c 같은 URL 이 대상 시험에만(준비용 HTTP 호출 — D2 면 밖) → 세지 않음", ln.dp("f14c"), 0, f"뺌: {sup_ex}")
    (ln.repo / "application/base/urls.py").write_text("from django.urls import path\nurlpatterns = [path(\"x/\", None)]\n",
                                                       encoding="utf-8")
    ln.sup(["application/base/domain_layer/unrelated.py"], **FACE_TRUST)
    expect(fails, "RD-F118 C4b 공급 BC 에 HTTP 표면 관찰 못 함 사유 → 그 BC 전체가 면(면 넓힘 줄) → 공급 면 겹침", ln.dp("c4b"), 2,
           "공급 면 application/base/domain_layer/unrelated.py", "면 넓힘: 공급 BC base — HTTP 표면 관찰 못 함(")
    # ── 못 읽은 파일 — 그 파일이 속한 BC 만(좁은 확인 사소 3) ──
    ln = FaceLane(td, "f-bad", {"application/zeta/__init__.py": "", "application/zeta/domain_layer/bad.py": "def (:\n"})
    ln.sup(["application/base/domain_layer/unrelated.py"], **FACE_TRUST)
    expect(fails, "RD-F118 U1 공급 BC 밖(zeta) 파싱 못 한 파일 → 공급 면을 넓히지 않음(뺌 줄 · 면 넓힘 없음)", ln.dp("u1"), 0,
           f"뺌: {sup_ex}")
    (ln.repo / "web/application/admin/op_a/presentation_layer/view/broken.js").write_bytes(b"var x = '\xff';\n")
    ln.dp("u2")
    got = ln.data("u2")
    expect(fails, "RD-F118 U2 web 의 UTF-8 아닌 파일(소비 파일 읽기 실패) → 공급 BC 의 면은 넓히지 않는다(face_widened 없음)",
           (0 if not got.get("face_widened") and "application/base/" not in got.get("supplier_faces", {}).get("base", [])
            and got.get("http_unread") else 9, json.dumps(got.get("supplier_faces"), ensure_ascii=False)), 0)
    (ln.repo / "web/application/admin/op_a/presentation_layer/view/broken.js").unlink()
    (ln.repo / "application/base/domain_layer/bad.py").write_text("def (:\n", encoding="utf-8")
    expect(fails, "RD-F118 U3 공급 BC 안 파싱 못 한 파일 → 그 BC 전체가 면(면 넓힘 줄) → 공급 면 겹침", ln.dp("u3"), 2,
           "공급 면 application/base/domain_layer/unrelated.py",
           "면 넓힘: 공급 BC base — application/base/domain_layer/bad.py 를 읽거나 파싱하지 못함")
    (ln.repo / "application/base/domain_layer/bad.py").unlink()
    (ln.repo / "application/demo/domain_layer/bad.py").write_text("def (:\n", encoding="utf-8")
    expect(fails, "RD-F118 U4 대상 BC 안 파싱 못 한 파일 → 대상이 가리키는 곳을 몰라 모든 공급 BC 전체가 면 → 공급 면 겹침", ln.dp("u4"), 2,
           "면 넓힘: 공급 BC base — 대상 파일 application/demo/domain_layer/bad.py 를 읽거나 파싱하지 못함")


def deps_trust_cases(fails: "list[str]", td: Path) -> None:
    """설계 2판 §4-3 고침 목록 신뢰(B1) · §4-4 4 공급 BC 기능 실행 고침 목록 모름(D1 = 나) · 좁은 확인 N1(경계 행 꼴 · 빠짐) · 덧씌움
    (F9 · F10) · 실행 기록 사본 가르기(RD-F16 — pregate-report.md 도 같은 판)."""
    sup_ex: str = f"이 작업 트리 .dddjango/{FACE_SUP}"
    resume: str = "재개 조건: 그 레인이 이번 실행 명세로 첫 파견(G1 승인 뒤)하거나 G2 로 끝난 뒤 다시 시작"
    lane = FaceLane(td, "t-b1")
    lane.sup(["application/base/domain_layer/unrelated.py"])
    expect(fails, "RD-F118 B1a 공급 기능 실행 초안(앵커 없음) · 면 밖 계획 · G0 → 예보 보류(exit 0)", lane.dp("b1a"), 0,
           f"예보 보류: {sup_ex} — 보류(공급 BC base 를 고치는 기능 실행 — 고침 목록 모름: 첫 파견 전 — 명세가 아직 G1 승인본이 아니다)",
           "예보 보류 가운데 공급 BC 고침 목록 모름 1")
    lane.web([], name="20261025-0200-home")
    (lane.repo / ".dddjango-web" / "20261025-0200-home" / "server-contract.json").unlink()
    expect(fails, "RD-F118 B1a2 G0 · web HTTP 소비 예보 보류 + 공급 예보 보류 → 요약에 공급 수 h 가 따로(조정자 G0 정지 셈 = f + g − h)",
           lane.dp("b1a2"), 0, "판정 시점 G0 · 예보 보류 2 · 예보 겹침 0 · 예보 보류 가운데 공급 BC 고침 목록 모름 1")
    shutil.rmtree(lane.repo / ".dddjango-web")
    lane.dispatch()
    expect(fails, "RD-F118 B1b 같은 · 파견 직전 → 보류(파견 정지 · 확인할 자료 · 재개 조건)", lane.dp("b1b"), 2,
           f"보류: {sup_ex} — 보류(공급 BC base 를 고치는 기능 실행 — 고침 목록 모름: 첫 파견 전", "실행 줄(build_anchor) · "
           "pregate-report.md · 명세 file-plan", resume)
    lane.sup(None, anchor=True)
    expect(fails, "RD-F118 B1e 명세 없음 · 파견 직전 → 보류(명세 file-plan 없음)", lane.dp("b1e"), 2,
           "고침 목록 모름: 명세 file-plan 없음", resume)
    lane.to_g0()
    expect(fails, "RD-F118 B2a 명세 없음 · G0 → 예보 보류(exit 0)", lane.dp("b2a"), 0, "예보 보류: ", "고침 목록 모름: 명세 file-plan 없음")
    lane.dispatch()
    lane.sup(["application/base/domain_layer/unrelated.py"], anchor=True, report=b"## pre-gate \xff\n")
    got = lane.dp("b1u")
    expect(fails, "RD-F118 B1u UTF-8 아닌 pregate-report.md → 해독 보류를 새로 만들지 않고 «고침 목록 모름»(파견 직전 보류)",
           (got[0] if "그 기록을 UTF-8 로 고친 뒤" not in got[1] else 9, got[1]), 2,
           "고침 목록 모름: pregate-report.md 를 UTF-8 로 못 읽는다 — 이번 실행 명세인지 모른다")
    # ── 수정 모드 새 실행 · 실행 경계(C5 · N1) ──
    c5 = FaceLane(td, "t-c5")
    old: str = "20261020-1000-base-feature"
    c5.sup(["application/base/domain_layer/unrelated.py"], g0="20261025-0300", name=old, prev=FACE_MODIFY_PREV)
    expect(fails, "RD-F118 C5 수정 모드 새 실행(앵커 없음) · 앞 실행 file-plan · G0 → 예보 보류(첫 파견 전)", c5.dp("c5"), 0,
           f"예보 보류: 이 작업 트리 .dddjango/{old} — 보류(공급 BC base 를 고치는 기능 실행 — 고침 목록 모름: 첫 파견 전")
    cases: "list[tuple[str, str, int, str]]" = [
        ("c5g", FACE_OLD_SECTION + FACE_OLD_BASE + "- 실행 경계 — 20261025-0300 · 2026-10-25T00:00:00Z\n" + FACE_NEW_BASE, 2,
         "이번 실행 pre-gate 예보가 없다 — 명세가 앞 실행 것일 수 있다"),
        ("c5ok", FACE_OLD_SECTION + FACE_OLD_BASE + "- 실행 경계 — 20261025-0300 · 2026-10-25T00:00:00Z\n" + FACE_SECTION
         + FACE_NEW_BASE, 0, f"뺌: 이 작업 트리 .dddjango/{old} — 공급 BC base · 고침 1 파일 {FACE_DROP}"),
        ("c5mm", FACE_OLD_SECTION + "- 실행 경계 — 20261020-1000 · 2026-10-20T00:00:00Z\n" + FACE_SECTION, 2,
         "pregate-report.md 마지막 실행 경계 값(20261020-1000)이 이 실행 G0 승인 값(20261025-0300)이 아니다"),
        ("x1", FACE_OLD_SECTION + FACE_OLD_BASE + FACE_NEW_BASE, 2,
         "pregate-report.md 에 실행 경계 행이 없는데 pre-gate 기준선 행이 2 — 명세가 앞 실행 것일 수 있다"),
        ("x2", FACE_OLD_SECTION + FACE_OLD_BASE + "- 실행 경계 — 20261025-0300 (2026-10-25T00:00:00Z)\n" + FACE_NEW_BASE, 2,
         "이번 실행 pre-gate 예보가 없다"),
        ("x2b", FACE_OLD_SECTION + FACE_OLD_BASE + "- 실행 경계 — 20261025-0300\n" + FACE_NEW_BASE, 2, "이번 실행 pre-gate 예보가 없다"),
        ("x2ok", FACE_OLD_SECTION + FACE_OLD_BASE + "- 실행 경계 — 20261025-0300 (2026-10-25T00:00:00Z)\n" + FACE_SECTION, 0,
         f"뺌: 이 작업 트리 .dddjango/{old}"),
        ("x3", FACE_OLD_SECTION + "- 실행 경계 —\n" + FACE_SECTION, 2, "마지막 실행 경계 값(못 읽음)"),
        ("x4", FACE_OLD_SECTION + "- 실행 경계 — 20261025-0300 · 2026-10-25T00:00:00Z\n## pre-gate 예보 (손으로 쓴 제목)\n", 2,
         "이번 실행 pre-gate 예보가 없다")]
    labels: "dict[str, str]" = {
        "c5g": "C5gd 첫 파견 뒤(앵커) · G1′ 생략(실행 경계 뒤 예보 절 없음) · 파견 직전 → 보류",
        "c5ok": "C5ok 실행 경계 뒤 이번 실행 예보 절 있음 · 파견 직전 → 믿음 · 면 밖 → 뺌",
        "c5mm": "C5mm 마지막 실행 경계 값이 앞 실행 G0 값 · 파견 직전 → 보류",
        "x1": "X1 경계 행 빠뜨림 · 기준선 행 둘(앞 · 이번) · 앞 실행 예보 절 → 처음부터로 읽지 않음 → 보류(N1)",
        "x2": "X2 경계 행 꼴 흔들림(`(UTC)` 꼬리) — check-report 와 같은 머리로 경계를 찾음 · 그 뒤 예보 절 없음 → 보류(N1)",
        "x2b": "X2b 경계 행에 UTC 칸 없음 · 그 뒤 예보 절 없음 → 보류(N1)",
        "x2ok": "X2ok `(UTC)` 꼬리 경계 · 값 = 이 실행 G0 · 그 뒤 예보 절 있음 → 믿음 → 뺌",
        "x3": "X3 경계 행 값 없음(못 읽음) → 보류(fail-closed)",
        "x4": "X4 경계 뒤 예보 절 앵커(`## pre-gate 예보 — <UTC> · `) 아닌 손 제목 → 절로 세지 않음 → 보류"}
    c5.dispatch()
    for tag, report, code, needle in cases:
        c5.sup(["application/base/domain_layer/unrelated.py"], g0="20261025-0300", name=old, prev=FACE_MODIFY_PREV, anchor=True,
               report=report)
        expect(fails, f"RD-F118 {labels[tag]}", c5.dp(tag), code, needle)
    c5.to_g0()
    c5.sup(["application/base/domain_layer/unrelated.py"], g0="20261025-0300", name=old, prev=FACE_MODIFY_PREV, anchor=True,
           report=cases[0][1])
    expect(fails, "RD-F118 C5g 같은 G1′ 생략 실행 · G0 → 예보 보류(정지 아님)", c5.dp("c5g0"), 0,
           f"예보 보류: 이 작업 트리 .dddjango/{old} — 보류(공급 BC base 를 고치는 기능 실행 — 고침 목록 모름: 이번 실행 pre-gate 예보가 없다")
    c5.sup(["application/base/domain_layer/unrelated.py"], g0="20261025-0300", name=old, prev=FACE_MODIFY_PREV, anchor=True,
           report=FACE_SECTION + FACE_NEW_BASE)
    expect(fails, "RD-F118 B1c2 경계 행 없음 · 기준선 행 하나 · 예보 절 있음(이 실행이 리포트를 처음 만듦) → 믿음 → 뺌", c5.dp("b1c2"), 0,
           f"뺌: 이 작업 트리 .dddjango/{old}")
    # ── 덧씌움(그 트리 미착륙 커밋 경로는 언제나 믿는 고침) ──
    for tag, path, code, needle in (
            ("f9", f"{FACE_OHS}/base_service.py", 2, f"공급 면 {FACE_OHS}/base_service.py"),
            ("f10", "application/base/domain_layer/inner.py", 0, "공급 면과 만남 0")):
        ov = FaceLane(td, f"t-{tag}")
        y: Path = td / f"t-{tag}-wt"
        _git(ov.repo, "worktree", "add", "-q", "-b", "lane-y", str(y))
        TreeLanes.write(y, {f".dddjango/{FACE_SUP}/refactor-scope.md":
                            "실행 · G0 승인 20261025-0100 · build_anchor abc123\n\n- 대상 BC 경로 필터: application/base/\n",
                            f".dddjango/{FACE_SUP}/design-spec.md":
                                "# s\n\n<!-- machine: file-plan -->\n```paths\nupdate application/base/domain_layer/unrelated.py\n```\n",
                            f".dddjango/{FACE_SUP}/pregate-report.md": FACE_SECTION,
                            path: "# 레인이 고침\n"})
        _git(y, "add", "-A")
        _git(y, "commit", "-qm", "레인 Y 공급 실행 + 코드")
        expect(fails, f"RD-F118 {tag.upper()} 다른 작업 트리 미착륙 커밋(덧씌움)이 {'공급 면 파일' if code else '면 밖'}을 고침 · file-plan 은 면 밖"
               f" → {'공급 면 겹침' if code else '세지 않음(뺌)'}", ov.dp(tag), code, needle)
    # ── 사본 가르기(RD-F16) — pregate-report.md 도 RUN_RECORDS 라 자기 변경 · MH 판 판정이 같은 판으로 읽는다 ──
    sp = TreeLanes(td, "t-f16", FACE_FILES)
    untrusted: "dict[str, str]" = {
        f".dddjango/{FACE_SUP}/refactor-scope.md": "실행 · G0 승인 20261025-0100 · build_anchor abc123\n\n"
                                                   "- 대상 BC 경로 필터: application/base/\n",
        f".dddjango/{FACE_SUP}/design-spec.md":
            "# s\n\n<!-- machine: file-plan -->\n```paths\nupdate application/base/domain_layer/unrelated.py\n```\n",
        f".dddjango/{FACE_SUP}/pregate-report.md": FACE_OLD_SECTION + "- 실행 경계 — 20261025-0100 · 2026-10-25T00:00:00Z\n"}
    L = TreeLanes
    L.commit(sp.main, "공급 실행 기록(이번 실행 예보 절 없음)", untrusted)
    y = sp.tree("wt-y", "lane-y")
    x = sp.tree("wt-x", "lane-x")
    for tree in (sp.main, x):                               # 주 작업 트리 · 이 트리 사본은 없다(미커밋으로 지움)
        shutil.rmtree(tree / ".dddjango" / FACE_SUP)
    L.own(x)
    expect(fails, "RD-F118 F16a 다른 트리 사본 = 커밋본(옛 사본) → MH 판 기록(pregate-report 포함)으로 → 고침 목록 모름 → G0 예보 보류",
           L.dp(x, "f16a"), 0, f".dddjango/{FACE_SUP} — 보류(공급 BC base 를 고치는 기능 실행 — 고침 목록 모름: 이번 실행 pre-gate 예보가 없다")
    (y / ".dddjango" / FACE_SUP / "pregate-report.md").write_text(
        untrusted[f".dddjango/{FACE_SUP}/pregate-report.md"] + FACE_SECTION, encoding="utf-8")
    expect(fails, "RD-F118 F16b 그 트리에서 pregate-report.md 만 디스크가 커밋본과 다름 → 자기 변경 사본으로 판정 → 믿음 → 뺌",
           L.dp(x, "f16b"), 0, f".dddjango/{FACE_SUP} — 공급 BC base · 고침 1 파일 {FACE_DROP}")
    sp2 = TreeLanes(td, "t-f16c", FACE_FILES)
    L.commit(sp2.main, "공급 실행 기록(이번 실행 예보 절 없음)", untrusted)
    y = sp2.tree("wt-y", "lane-y")
    L.commit(sp2.main, "공급 실행 이번 실행 예보 절(main 에서)", {f".dddjango/{FACE_SUP}/pregate-report.md":
                                                            untrusted[f".dddjango/{FACE_SUP}/pregate-report.md"] + FACE_SECTION})
    x = sp2.tree("wt-x", "lane-x")
    L.own(x)
    expect(fails, "RD-F118 F16c 다른 트리의 옛 사본(예보 절 없음)은 MH 판 pregate-report(예보 절 있음)로 읽는다 → 믿음 → 뺌",
           L.dp(x, "f16c"), 0, f".dddjango/{FACE_SUP} — 공급 BC base · 고침 1 파일 {FACE_DROP}", "MH 판으로 판정 1")


def deps_web_unit_cases(fails: "list[str]", td: Path) -> None:
    """설계 2판 §4-5 web 단위(dddjango-web 단위 규칙) — W0 core = web 규칙 · W1 ~ W5 · C6(단위 밖 web 파일만 고치는 web 실행 S1)."""
    probe: str = (
        "import importlib.util, json, sys\n"
        "def load(name, path):\n"
        "    spec = importlib.util.spec_from_file_location(name, path)\n"
        "    mod = importlib.util.module_from_spec(spec)\n"
        "    sys.modules[name] = mod\n"
        "    spec.loader.exec_module(mod)\n"
        "    return mod\n"
        "core = load('core_ra', sys.argv[1])\n"
        "web = load('web_ra', sys.argv[2])\n"
        "paths = json.loads(sys.argv[3])\n"
        "ca = core._web_areas(['web/' + p for p in paths])\n"
        "wa = web.areas_of(paths)\n"
        "out = {'areas': [sorted(ca), sorted(wa)], 'diff': []}\n"
        "for p in paths:\n"
        "    c = core._web_unit('web/' + p, ca)\n"
        "    w = web.unit_of(p, wa)\n"
        "    if c != ('web/' + w if w else ''):\n"
        "        out['diff'].append([p, c, w])\n"
        "print(json.dumps(out, ensure_ascii=False))\n")
    paths: "list[str]" = [
        "application/admin/op_a/infra_layer/data_source/a.py", "application/admin/op_a/presentation_layer/view/v.html",
        "application/admin/op_b/domain_layer/m.py", "application/client/ad_page/presentation_layer/view/v.py",
        "application/flat_bc/domain_layer/m.py", "application/flat_bc/presentation_layer/view/v.html",
        "application/mixed/x.py", "application/mixed/inner/domain_layer/m.py", "application/__init__.py",
        "application/admin/__init__.py", "static/application/admin/op_a/a.css", "static/application/flat_bc/b.css",
        "static/root/root.css", "static/css/base.css", "static/js/app.js", "static/vendor/htmx.min.js", "static/x.css",
        "root/views.py", "common/util.py", "design_system/button.html", "home/views.py", "web_test/test_x.py"]
    got = subprocess.run([sys.executable, "-c", probe, str(TOOL), str(ROOT / "dddjango-web" / "scripts" / "refactor_audit.py"),
                          json.dumps(paths)], capture_output=True, text=True)
    res: dict = json.loads(got.stdout) if got.returncode == 0 and got.stdout.strip() else {}
    expect(fails, f"RD-F118 W0 core _web_unit · _web_areas = dddjango-web unit_of · areas_of(경로 {len(paths)} · web 바로 밑 파일 뺌)",
           (0 if res and not res["diff"] and res["areas"][0] == res["areas"][1] == ["admin", "client"] else 9,
            got.stdout + got.stderr), 0)
    lane = FaceLane(td, "w-units", {"web/application/client/ad_page/infra_layer/x.py": "X: int = 1\n",
                                    "web/static/application/admin/op_a/a.css": ".a {}\n",
                                    "web/static/vendor/htmx.min.js": "/*x*/\n"})
    lane.dp("w5")
    md: str = (lane.own / "deps" / "w5" / "deps.md").read_text(encoding="utf-8") if (lane.own / "deps" / "w5" / "deps.md").is_file() \
        else ""
    expect(fails, "RD-F118 W5 deps.md «HTTP 소비» · deps.json our_units 의 web 주인이 정밀 단위(web/application/admin/op_a)",
           (0 if "- HTTP 소비: web/application/admin/op_a" in md and lane.data("w5").get("our_units") == ["web/application/admin/op_a"]
            else 9, md), 0)
    expect(fails, "RD-F118 W4 area 아님(web/application/<x>/ 직속 코드 파일) → 단위 web/application/<x>",
           (0 if ra._web_unit("web/application/client/ad_page/a.py", ra._web_areas(["web/application/client/x.py",
                                                                                  "web/application/client/ad_page/domain_layer/m.py"]))
            == "web/application/client" else 9, "단위 값"), 0)
    lane.web(["web/application/client/ad_page/presentation_layer/view/ad_view.py"])
    lane.dispatch()
    expect(fails, "RD-F118 W1 web 실행이 소비 단위 밖(client/ad_page)만 · 파견 직전 V 1 → 안 셈", lane.dp("w1"), 0, "레인 겹침 없음",
           "보류 0 ")
    lane.web(["web/application/admin/op_a/presentation_layer/view/a_view.py"])
    expect(fails, "RD-F118 W2 같은 소비 단위(admin/op_a)의 다른 파일 · V 1 → 겹침(web 단위)", lane.dp("w2"), 2,
           "— web 단위 web/application/admin/op_a")
    lane.to_g0()
    expect(fails, "RD-F118 W2b 같은 · G0 → 예보 겹침", lane.dp("w2b"), 0, "예보 겹침: 이 작업 트리 .dddjango-web/20261025-0200-web-x — web 단위 "
           "web/application/admin/op_a")
    lane.web(["web/static/application/admin/op_a/a.css"])
    lane.dispatch()
    expect(fails, "RD-F118 W3 BC 미러 CSS(web/static/application/admin/op_a/…) · V 1 → 같은 단위 겹침", lane.dp("w3"), 2,
           "web 단위 web/application/admin/op_a")
    lane.web(["web/static/vendor/htmx.min.js"], {"paths": {"/api/ads/{id}": {}}})
    expect(fails, "RD-F118 C6d web 실행이 web/static/vendor/ 만 고침(단위 밖) · 파견 직전 V 1 → 보류 아님 · 안 셈(S1)", lane.dp("c6d"), 0,
           "레인 겹침 없음", "보류 0 ")
    lane.to_g0()
    got2 = lane.dp("c6")
    expect(fails, "RD-F118 C6 같은 · G0 → 예보 보류 아님(S1)", (got2[0] if "web 단위를 모른다" not in got2[1] else 9, got2[1]), 0,
           "예보 보류 0")


def deps_face_review_cases(fails: "list[str]", td: Path) -> None:
    """구현 검토(F4-118) 중요 I-1 · I-2 — 이름 사슬은 폴더 면(그 `__init__.py`) · 점 경로 문자열(가장 긴 모듈 뒤 첫 성분) · BC 뿌리
    패키지(`from .. import X`)에서도 정의 모듈까지 · 모델 이름도 · 합성 경로는 지어낸 `django_<BC>` 가 아니라 그 label 의 앱 폴더."""
    impl: str = "application/base/application_layer/thing_impl.py"
    app_layer: "dict[str, str]" = {"application/base/application_layer/__init__.py": "",
                                   impl: "class ThingService:\n    pass\n\n\nclass Thing:\n    pass\n"}
    ohs_dot: str = FACE_OHS.replace("/", ".")
    uses_svc: str = f"from {ohs_dot} import ThingService\n\n\nS = ThingService\n"
    for tag, init, label in (
            ("ce1", "import logging\n\nfrom application.base.application_layer.thing_impl import ThingService\n\n"
                    "logger = logging.getLogger(__name__)\n", "창구 패키지 __init__ 이 다른 층에서 다시 내보냄(파사드 아님 — 대입 있음)"),
            ("ce1b", "from application.base.application_layer.thing_impl import ThingService\n",
             "대조 — 창구 패키지 __init__ 이 import 만(파사드)")):
        ln = FaceLane(td, f"r-{tag}", {**app_layer, f"{FACE_OHS}/__init__.py": init,
                                       "application/demo/domain_layer/uses_svc.py": uses_svc})
        ln.sup([impl], **FACE_TRUST)
        ln.dispatch()
        expect(fails, f"RD-F118 {tag.upper()} 대상이 창구 «패키지»에서 이름을 들임 · {label} · 실행이 정의 모듈만 고침 → 공급 면 겹침(이름 사슬은 "
               f"폴더 면의 __init__.py 에서 시작)", ln.dp(tag), 2, f"공급 면 {impl}")
    ln = FaceLane(td, "r-ce1c", {**app_layer, "application/base/domain_layer/__init__.py":
                                 "from application.base.application_layer.thing_impl import Thing\n\nVERSION = 1\n",
                                 "application/demo/domain_layer/uses_thing.py":
                                     "from application.base.domain_layer import Thing\n\n\nT = Thing\n"})
    ln.sup([impl], **FACE_TRUST)
    ln.dispatch()
    expect(fails, "RD-F118 CE1C 대상이 domain_layer 패키지에서 이름을 들임 · __init__ 이 다른 층에서 다시 내보냄 → 공급 면 겹침", ln.dp("ce1c"),
           2, f"공급 면 {impl}")
    ln = FaceLane(td, "r-ce1d", {**app_layer, "application/base/__init__.py":
                                 "from application.base.application_layer.thing_impl import Thing\n",
                                 "application/base/domain_layer/__init__.py": "",
                                 "application/base/domain_layer/facade.py": "from .. import Thing\n\nX = 1\n",
                                 "application/demo/domain_layer/uses.py":
                                     "from application.base.domain_layer.facade import Thing\n\n\nT = Thing\n"})
    ln.sup([impl], **FACE_TRUST)
    ln.dispatch()
    expect(fails, "RD-F118 CE1D `from .. import Thing`(BC 뿌리 패키지 application.base 가 다시 내보냄) → 사슬이 그 __init__.py 로 이어짐 → "
           "공급 면 겹침", ln.dp("ce1d"), 2, f"공급 면 {impl}")
    window: "dict[str, str]" = {**app_layer, f"{FACE_OHS}/svc_window.py":
                                "from application.base.application_layer.thing_impl import ThingService\n\nX = 1\n"}
    for tag, wiring, label in (
            ("ce6", f"SERVICE: str = \"{ohs_dot}.svc_window.ThingService\"\n", "점 경로 문자열(import_string 류)"),
            ("ce6b", f"from {ohs_dot}.svc_window import ThingService\n\n\nSERVICE = ThingService\n", "대조 — 같은 것을 from-import ")):
        ln = FaceLane(td, f"r-{tag}", {**window, "application/demo/composition_root/wiring.py": wiring})
        ln.sup([impl], **FACE_TRUST)
        ln.dispatch()
        expect(fails, f"RD-F118 {tag.upper()} 대상 합성 루트가 {label}로 창구 모듈의 이름을 가리킴 · 그 모듈이 다른 층에서 다시 내보냄 → "
               f"공급 면 겹침(가장 긴 모듈 뒤 첫 성분이 이름)", ln.dp(tag), 2, f"공급 면 {impl}")
    apps: str = "from django.apps import AppConfig\n\n\nclass C(AppConfig):\n    name = \"{name}\"\n    label = \"{label}\"\n"
    drv: str = "application/base/driven_layer"
    two_apps: "dict[str, str]" = {
        f"{drv}/django_base/__init__.py": "",
        f"{drv}/django_base/apps.py": apps.format(name=f"{drv.replace('/', '.')}.django_base", label="base"),
        f"{drv}/django_base/models.py": "class ThingModel:\n    pass\n",
        f"{drv}/django_base/migrations/0001_initial.py": "X: int = 1\n",
        f"{drv}/django_base_audit/__init__.py": "",
        f"{drv}/django_base_audit/apps.py": apps.format(name=f"{drv.replace('/', '.')}.django_base_audit", label="base_audit"),
        f"{drv}/django_base_audit/models.py": "class AuditModel:\n    pass\n",
        f"{drv}/django_base_audit/migrations/0001_initial.py": "Y: int = 1\n"}
    ln = FaceLane(td, "r-ce2", {**two_apps, "application/demo/driven_layer/django_demo/models.py": "FK: str = \"base_audit.AuditModel\"\n"})
    ln.sup([f"{drv}/django_base_audit/models.py"], **FACE_TRUST)
    ln.dispatch()
    expect(fails, "RD-F118 CE2 한 BC 에 Django 앱 둘(label base · base_audit) · 대상이 \"base_audit.AuditModel\" · 실행이 그 앱 모델만 고침 → "
           "그 label 의 앱 폴더 · 공급 면 겹침", ln.dp("ce2"), 2, f"공급 면 {drv}/django_base_audit/models.py")
    ln.sup([f"{drv}/django_base/models.py"], **FACE_TRUST)
    expect(fails, "RD-F118 CE2n 같은 · 실행이 다른 앱(label base) 모델만 고침 → 면 밖(지어낸 django_<BC> 경로를 면으로 세지 않음) → 뺌",
           ln.dp("ce2n"), 0, f"뺌: 이 작업 트리 .dddjango/{FACE_SUP} — 공급 BC base · 고침 1 파일 {FACE_DROP}")
    ln = FaceLane(td, "r-ce2b", {**two_apps, "application/demo/driven_layer/django_demo/migrations/0001_initial.py":
                                 "dependencies = [(\"base_audit\", \"0001_initial\")]\n"})
    ln.sup([f"{drv}/django_base_audit/migrations/0001_initial.py"], **FACE_TRUST)
    ln.dispatch()
    expect(fails, "RD-F118 CE2B 대상 마이그레이션이 (\"base_audit\", \"0001_initial\") 에 의존 · 두 앱 다 0001_initial · 실행이 그 앱 것을 고침 → "
           "공급 면 겹침", ln.dp("ce2b"), 2, f"공급 면 {drv}/django_base_audit/migrations/0001_initial.py")
    ln.sup([f"{drv}/django_base/migrations/0001_initial.py"], **FACE_TRUST)
    expect(fails, "RD-F118 CE2Bn 같은 · 실행이 다른 앱의 같은 이름 마이그레이션만 고침 → 면 밖 → 뺌", ln.dp("ce2bn"), 0,
           f"뺌: 이 작업 트리 .dddjango/{FACE_SUP}")
    model_split: "dict[str, str]" = {
        f"{drv}/django_base/__init__.py": "",
        f"{drv}/django_base/apps.py": apps.format(name=f"{drv.replace('/', '.')}.django_base", label="base"),
        f"{drv}/django_base/models.py": "from .thing_model import ThingModel\n\nALL_MODELS = [ThingModel]\n",
        f"{drv}/django_base/thing_model.py": "class ThingModel:\n    pass\n"}
    for tag, src, label in (
            ("m1", {"application/demo/driven_layer/django_demo/models.py": "FK: str = \"base.ThingModel\"\n"},
             "대상이 \"base.ThingModel\""),
            ("m2", {"application/demo/driven_layer/django_demo/migrations/0002_fk.py": "TO: str = \"base.thingmodel\"\n"},
             "대상 마이그레이션이 소문자 \"base.thingmodel\"(모델 이름 대소문자 무시)")):
        ln = FaceLane(td, f"r-{tag}", {**model_split, **src})
        ln.sup([f"{drv}/django_base/thing_model.py"], **FACE_TRUST)
        ln.dispatch()
        expect(fails, f"RD-F118 {tag.upper()} {label} · models.py 가 다른 모듈에서 모델을 다시 내보냄(파사드 아님) · 실행이 정의 모듈만 고침 → "
               f"모델 이름 사슬 · 공급 면 겹침", ln.dp(tag), 2, f"공급 면 {drv}/django_base/thing_model.py")
    # 재확인 N-1 — label 앱 폴더에 models · migrations 가 없으면 앱 폴더 전체로 좁히지 않고 예전 대체(지어낸 경로 → BC 의 apps.py 폴더
    # 몫 → 그 BC 전체)로 내려간다
    one_app: "dict[str, str]" = {f"{drv}/django_base/__init__.py": "",
                                 f"{drv}/django_base/apps.py": apps.format(name=f"{drv.replace('/', '.')}.django_base", label="base")}
    for tag, extra, plan, label in (
            ("r1", {f"{drv}/orm/__init__.py": "", f"{drv}/orm/thing.py":
                    "class ThingModel:\n    class Meta:\n        app_label = \"base\"\n",
                    "application/demo/driven_layer/django_demo/models.py": "FK: str = \"base.ThingModel\"\n"},
             f"{drv}/orm/thing.py", "모델이 label 앱 폴더 밖(`Meta.app_label`) · 대상이 \"base.ThingModel\""),
            ("r2", {f"{drv}/django_base/models.py": "class ThingModel:\n    pass\n",
                    f"{drv}/schema_migrations/__init__.py": "", f"{drv}/schema_migrations/0001_x.py": "X: int = 1\n",
                    "config/settings.py": "MIGRATION_MODULES = {\"base\": \"application.base.driven_layer.schema_migrations\"}\n",
                    "application/demo/driven_layer/django_demo/migrations/0001_initial.py": "dependencies = [(\"base\", \"0001_x\")]\n"},
             f"{drv}/schema_migrations/0001_x.py", "`MIGRATION_MODULES` 로 옮긴 마이그레이션 · 대상 마이그레이션이 (\"base\", \"0001_x\") 에 의존")):
        ln = FaceLane(td, f"r-{tag}", {**one_app, **extra})
        ln.sup([plan], **FACE_TRUST)
        ln.dispatch()
        expect(fails, f"RD-F118 {tag.upper()} {label} · 실행이 그 파일을 고침 → label 앱 폴더에 없으니 예전 대체(그 BC 전체) → 공급 면 겹침",
               ln.dp(tag), 2, f"공급 면 {plan}")
    # 재확인 N-2 — 모델 이름 씨앗(대소문자 무시)은 그 이름을 정의하거나 들인 import 만 따라간다 · 지운 모델 이름은 BC 를 걷지 않는다
    mdl: str = f"{drv}/django_base/models"
    walk: "dict[str, str]" = {
        **one_app,
        f"{mdl}/__init__.py": "from .thing import ThingModel\nfrom .order import OrderModel\n",
        f"{mdl}/thing.py": "from application.base.domain_layer.thing import Thing\n\n\nclass ThingModel:\n    pass\n",
        f"{mdl}/order.py": "from application.base.domain_layer.order import Order\n\n\nclass OrderModel:\n    pass\n",
        "application/base/domain_layer/__init__.py": "",
        "application/base/domain_layer/thing.py": "from application.base.domain_layer.policy import p\n\n\nclass Thing:\n    pass\n",
        "application/base/domain_layer/order.py": "from application.base.application_layer.pricing import price\n\n\nclass Order:\n    pass\n",
        "application/base/domain_layer/policy.py": "def p() -> int:\n    return 1\n",
        "application/base/application_layer/__init__.py": "",
        "application/base/application_layer/pricing.py": "def price() -> int:\n    return 1\n",
        "application/demo/driven_layer/django_demo/migrations/0003_x.py":
            "from django.apps import apps\n\nOPS = [\"base.thingmodel\"]\nOLD = apps.get_model(\"base\", \"RemovedModel\")\n"}
    ln = FaceLane(td, "r-ce4", walk)
    ln.sup(["application/base/application_layer/pricing.py"], **FACE_TRUST)
    ln.dispatch()
    expect(fails, "RD-F118 CE4 대상 마이그레이션이 지운 모델 apps.get_model(\"base\", \"RemovedModel\") · 실행이 창구 뒤 다른 파일만 고침 → 모델 "
           "이름 사슬이 «import 모두» 로 번지지 않음 → 뺌", ln.dp("ce4"), 0, f"뺌: 이 작업 트리 .dddjango/{FACE_SUP}")
    got = ln.data("ce4").get("supplier_faces", {}).get("base", [])
    expect(fails, "RD-F118 CE4b 같은 · 면에 모델 자리(models/ · 정의 모듈 thing.py)는 남고 도메인 · 응용 층은 없음",
           (0 if f"{mdl}/" in got and f"{mdl}/thing.py" in got and not any("domain_layer" in g or "application_layer" in g for g in got)
            else 9, json.dumps(got, ensure_ascii=False)), 0)
    # 재확인 3 r3 — 두 앱 BC · 대상 label(base_audit)의 앱 폴더를 아는데 거기 models 가 없음(모델은 Meta.app_label 로 다른 폴더) ·
    # 다른 앱의 지어낸 경로 django_base/models.py 는 있음 → 다른 앱 자리로 떨어지지 않고 그 BC 전체
    r3: "dict[str, str]" = {k: v for k, v in two_apps.items() if not k.endswith("django_base_audit/models.py")}
    ln = FaceLane(td, "r-r3", {**r3, f"{drv}/audit_orm/__init__.py": "",
                               f"{drv}/audit_orm/audit.py": "class AuditModel:\n    class Meta:\n        app_label = \"base_audit\"\n",
                               "application/demo/driven_layer/django_demo/models.py": "FK: str = \"base_audit.AuditModel\"\n"})
    ln.sup([f"{drv}/audit_orm/audit.py"], **FACE_TRUST)
    ln.dispatch()
    expect(fails, "RD-F118 R3 두 앱 BC · 대상 label(base_audit) 앱 폴더에 models 없음 · 다른 앱 django_base/models.py 는 있음 · 실행이 "
           "Meta.app_label 모델 파일을 고침 → 다른 앱 자리로 떨어지지 않고 그 BC 전체 → 공급 면 겹침", ln.dp("r3"), 2,
           f"공급 면 {drv}/audit_orm/audit.py")


F121_OLD_SHA: str = "55ab56e52371d3f8f264f4c77792dc56da1a0673"   # dddjango 2.26.1 배포 커밋 — 옛 판 대조는 HEAD 가 아니라 이 판에
F121_URL: str = "/api/other-api/1"
F121_SCHEMA: str = "application/demo/driving_layer/api/thing/schema/schema_out.py"
F121_PAGE: str = "application/demo/driven_layer/django_demo/templates/admin/demo/page.html"
F121_JS: str = "application/demo/driven_layer/django_demo/static/demo/page.js"
F121_OWN: str = "20261026-0100-refactor-demo"
F121_FILES: "dict[str, str]" = {      # DEPS_FILES + other 의 API(`/other-api`) — other → demo 실제 변(받는 쪽 어댑터)은 이미 있다
    **DEPS_FILES,
    "application/other/driving_layer/api/o/o_controller.py": FACE_CONTROLLER.format(prefix="/other-api", name="OtherController"),
}


def _f121_schema(doc: str = "결과지 칸.", head: str = "", tail: str = "") -> str:
    return f'{head}class ThingOut:\n    """{doc}"""\n\n    key: str = "k"\n{tail}'


def deps_http_text_cases(fails: "list[str]", td: Path) -> None:
    """F4-121 — HTTP 소비 셈은 부를 수 있는 글만: `.py` 문서 문자열 · 주석 밖 문자열 · 바이트 상수(+ doctest docstring) · `.html` 은
    HTML · Django 주석 밖(태그 · 날 글 요소 · 템플릿 태그 안 `<!--` 는 주석 아님 · verbatim 안 Django 주석은 글자 · Django 낱말은 한 줄 안 ·
    이름 붙은 verbatim 은 이름까지 같은 endverbatim 까지 · `--!>` 도 주석 끝 · 날 글 요소는 이름 뒤가 공백 · `/` · `>` 인 끝 태그에서만
    끝남 · 짝 없는 여는 글이 많은 긴 줄도 선형 시간 · 그 바꾸기는 낱말을 바꾸지 않음) · `.js` · 계약 · 파싱 못 한 `.py` 는 원문 줄(JS 주석은
    받아들인 한계로 지금처럼 셈).
    대상 demo 의 한 자리에 other API 주소를 꼴만 바꿔 넣는다
    (other → demo 실제 변이 있어 demo → other 변이 서면 순환 묶음). 옛 판 = F121_OLD_SHA(HEAD 아님)."""
    old_tool: Path = td / "f121-old" / "refactor_audit.py"
    old_tool.parent.mkdir(parents=True)
    old_tool.write_text(_git(ROOT, "show", f"{F121_OLD_SHA}:dddjango/scripts/refactor_audit.py"), encoding="utf-8")
    repo: Path = _project(td / "f121", F121_FILES)
    own: Path = repo / ".dddjango" / F121_OWN
    own.mkdir(parents=True)
    (own / "refactor-scope.md").write_text("실행 · G0 승인 20261026-0100 · 모드 리팩토링 · audit 20261026-0050\n", encoding="utf-8")
    single: str = "순환 성분 단독"
    cycle: str = "지원 안 함: 순환 묶음 demo · other"

    def dp(tag: str, files: "dict[str, str]", tool: Path = TOOL) -> "tuple[int, str]":
        """그 파일들을 미추적으로 써 deps demo 를 돌리고 지운다(같은 저장소를 사례마다 다시 쓴다)."""
        for rel, body in files.items():
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (repo / rel).write_text(body, encoding="utf-8")
        try:
            return run(repo, "deps", "demo", "--out", str(own / "deps" / tag), tool=tool)
        finally:
            for rel in files:
                (repo / rel).unlink()
    doc_line: str = f"key = 카드 묶음 창구 `GET {F121_URL}` 를 부를 열쇠"
    # ── 세지 않을 글(새 판 단독) ──
    t1: "dict[str, str]" = {F121_SCHEMA: _f121_schema(doc_line)}
    expect(fails, "RD-F121 T1 클래스 docstring 의 다른 BC 주소 → HTTP 소비 아님 · 순환 성분 단독 · exit 0", dp("t1", t1), 0, single)
    expect(fails, "RD-F121 T1o 같은 · 옛 판(2.26.1 배포 커밋) → 순환 묶음 exit 2(이 판이 고친 것)", dp("t1o", t1, old_tool), 2, cycle)
    for tag, label, files in (
            ("t2", "모듈 docstring", {F121_SCHEMA: _f121_schema(head=f'"""{doc_line}"""\n')}),
            ("t3", "함수 docstring", {F121_SCHEMA: _f121_schema(tail=f'\n\ndef key_of(r: ThingOut) -> str:\n    """{doc_line}"""\n'
                                                                    "    return r.key\n")}),
            ("t4", "`#` 주석 줄", {F121_SCHEMA: _f121_schema(tail=f"\n\n# GET {F121_URL}\n")}),
            ("t5", "코드 줄 끝 `#` 주석", {F121_SCHEMA: _f121_schema(tail=f"\n\nKEY_MAX: int = 40  # GET {F121_URL}\n")}),
            ("t6", "함수 몸 가운데 문자열 식 문장", {F121_SCHEMA: _f121_schema(
                tail=f'\n\ndef key_of(r: ThingOut) -> str:\n    x: str = r.key\n    "{doc_line}"\n    return x\n')}),
            ("t7", "BC 템플릿 `<!-- -->`", {F121_PAGE: f"<p>카드</p>\n<!-- GET {F121_URL} -->\n"}),
            ("t8", "BC 템플릿 `{# #}`", {F121_PAGE: f"<p>카드</p> {{# GET {F121_URL} #}}\n"}),
            ("t9", "BC 템플릿 `{% comment %}` 여러 줄", {F121_PAGE: f"{{% comment %}}\nGET {F121_URL}\n{{% endcomment %}}\n<p>카드</p>\n"}),
            ("t10", "HTML 주석 · `\\r` 줄 끝 · 조건부 주석", {F121_PAGE: f"<p>a</p>\r<!-- {F121_URL} -->\r"
                                                                     f"<!--[if IE]><script src=\"{F121_URL}\"></script><![endif]-->\r"}),
            ("t11", "짝 없는 `{%`(Django 는 글자) 뒤 다른 줄 HTML 주석", {F121_PAGE: f"<p>50{{% off</p>\n<!-- GET {F121_URL} -->\n"}),
            ("t12", "`--!>` 로 닫힌 HTML 주석", {F121_PAGE: f"<p>카드</p>\n<!-- GET {F121_URL} --!>\n"}),
            ("t13", "이름 붙은 verbatim 이 이름까지 같은 endverbatim 으로 닫힌 뒤 `{# #}`",
             {F121_PAGE: "{% verbatim blk %}{# a #}{% endverbatim blk %}" + f"{{# GET {F121_URL} #}}\n"}),
            ("t14", "`{% comment %}` 안 verbatim 속 `{% endcomment %}`(글자) — 주석은 뒤 endcomment 까지",
             {F121_PAGE: "{% comment %}{% verbatim %}{% endcomment %}{% endverbatim %}" + f"GET {F121_URL}" + "{% endcomment %}\n"})):
        expect(fails, f"RD-F121 {tag.upper()} {label} → HTTP 소비 아님 · 순환 성분 단독 · exit 0", dp(tag, files), 0, single)
    # ── 그대로 셀 글(새 판 순환 묶음) ──
    lit: "dict[str, str]" = {F121_SCHEMA: _f121_schema(tail=f'\n\nDECK_URL: str = "{F121_URL}"\n')}
    expect(fails, "RD-F121 C1 문자열 리터럴 → HTTP 소비 · 순환 묶음 exit 2", dp("c1", lit), 2, cycle)
    expect(fails, "RD-F121 C1o 같은 · 옛 판 → 순환 묶음 exit 2(리터럴은 두 판 같음)", dp("c1o", lit, old_tool), 2, cycle)
    for tag, label, files in (
            ("c2", "f-string 조각", {F121_SCHEMA: _f121_schema(tail='\n\ndef url(k: str) -> str:\n    return f"/api/other-api/{k}/deck"\n')}),
            ("c3", "같은 줄 리터럴 + `#` 주석", {F121_SCHEMA: _f121_schema(tail=f'\n\nU: str = "{F121_URL}"  # 손님 화면용\n')}),
            ("c4", "한 파일 docstring + 리터럴", {F121_SCHEMA: _f121_schema(doc_line, tail=f'\n\nU: str = "{F121_URL}"\n')}),
            ("c5", "`hx-get` 속성", {F121_PAGE: f'<a hx-get="{F121_URL}">카드</a>\n'}),
            ("c6", "같은 줄 속성 + `<!-- -->`", {F121_PAGE: f'<a hx-get="{F121_URL}">카드</a> <!-- 카드 그림 -->\n'}),
            ("c7", "JS `fetch` + 같은 줄 `//`", {F121_JS: f'fetch("{F121_URL}"); // 카드 그림\n'}),
            ("c8", "바이트 리터럴", {F121_SCHEMA: _f121_schema(tail=f'\n\nRAW: bytes = b"{F121_URL}"\n')}),
            ("c9", "doctest docstring(`>>>` — 실행되는 글)", {F121_SCHEMA: _f121_schema(
                tail=f'\n\ndef load() -> None:\n    """\n    >>> client.get("{F121_URL}")\n    """\n')}),
            ("j1", "JS `//` 주석 줄(받아들인 한계 — 원문 줄)", {F121_JS: f"// GET {F121_URL}\nconst n = 1;\n"}),
            ("j2", "JS 여러 줄 `/* */`(받아들인 한계)", {F121_JS: f"/*\n * GET {F121_URL}\n */\nconst n = 1;\n"}),
            ("j3", "JS 코드 줄 끝 `//`(받아들인 한계)", {F121_JS: f"const n = 1; // GET {F121_URL}\n"}),
            ("f1", "파싱 못 한 `.py` 의 `#` 주석(원문 줄)", {F121_SCHEMA: _f121_schema(tail=f"\n\ndef broken(:\n    pass  # GET {F121_URL}\n")}),
            ("f3", "닫히지 않은 `<!--` 뒤 속성(모를 때 원문)", {F121_PAGE: f'<!-- 메모\n<a hx-get="{F121_URL}">카드</a>\n'}),
            ("f6", "`<script>` 안 옛 숨김 `<!--` · 그 안 `fetch`", {F121_PAGE: f'<script>\n<!--\nfetch("{F121_URL}");\n//-->\n</script>\n'}),
            ("f7", "`<script>` 문자열 속 `<!--` 뒤 다른 줄 속성 · 뒤 주석", {F121_PAGE: f'<script>const s = "<!--";</script>\n'
                                                                             f'<div hx-get="{F121_URL}"></div>\n<!-- 메모 -->\n'}),
            ("f8", "속성 값 속 `<!--`(placeholder) 뒤 속성", {F121_PAGE: f'<input placeholder="<!--">\n<div hx-get="{F121_URL}"></div>\n'
                                                                    "<p>--></p>\n"}),
            ("f9", "`{% verbatim %}` 안 `{# #}`(글자로 나감)", {F121_PAGE: f'{{% verbatim %}}{{# <div hx-get="{F121_URL}"></div> #}}'
                                                                     "{% endverbatim %}\n"}),
            ("f10", "템플릿 태그 문자열 속 `<!--` 뒤 속성 · 뒤 주석", {F121_PAGE: '{% include "x.html" with a="<!--" %}\n'
                                                                       f'<div hx-get="{F121_URL}"></div>\n<!-- 메모 -->\n'}),
            ("f11", "짝 없는 `{%` 가 여러 줄 뒤 `<script>` 문자열 `%}` 와 맞물리지 않음 · 옛 숨김 `<!--` 안 `fetch`",
             {F121_PAGE: '<p>100{% off</p>\n<script>\nvar s = "%}";\n<!--\n' + f'fetch("{F121_URL}");\n//-->\n</script>\n'}),
            ("f12", "이름 붙은 verbatim 안 이름 없는 endverbatim 뒤 `{# #}`(글자로 나감)",
             {F121_PAGE: "{% verbatim blk %}{% endverbatim %}" + f'{{# <div hx-get="{F121_URL}"></div> #}}' + "{% endverbatim blk %}\n"}),
            ("f13", "`--!>` 로 닫힌 주석 뒤 속성 · 뒤 주석", {F121_PAGE: f'<!-- 메모 --!>\n<div hx-get="{F121_URL}"></div>\n<!-- 끝 -->\n'}),
            ("f14", "날 글 요소(xmp) 안 닫히지 않은 `<!--` 뒤 속성 · 뒤 주석",
             {F121_PAGE: f'<xmp><!-- 예시</xmp>\n<div hx-get="{F121_URL}"></div>\n<!-- 메모 -->\n'}),
            ("f15", "Django 변수 문자열 속 `{#` 뒤 속성", {F121_PAGE: '{{ "{#" }}' + f'<div hx-get="{F121_URL}"></div>' + '{{ "#}" }}\n'}),
            ("f16", "`<script>` 안 `</script` 뒤가 `'`(끝 태그 아님) · 뒤 옛 숨김 `<!--` 안 `fetch`",
             {F121_PAGE: "<script>\ndocument.write('<script src=\"a.js\"></script' + '>');\n// <!-- loader\n"
                         f'fetch("{F121_URL}");\n// -->\n</script>\n'}),
            ("f17", "같은 · 옛 숨김이 `--!>` 로 닫힘",
             {F121_PAGE: "<script>\ndocument.write('<script src=\"a.js\"></script' + '>');\n// <!-- loader\n"
                         f'fetch("{F121_URL}");\n// --!>\n</script>\n'})):
        got = dp(tag, files)
        expect(fails, f"RD-F121 {tag.upper()} {label} → HTTP 소비 · 순환 묶음 exit 2", got, 2, cycle,
               *(("파싱 못 한 파일 1",) if tag == "f1" else ()))
    c10: "dict[str, str]" = {F121_SCHEMA: _f121_schema(tail='\n\nU: str = "/api/" "other-api/1"\n')}
    expect(fails, "RD-F121 C10 이어 쓴 리터럴(값 = 주소) → 새 판은 셈 · 순환 묶음", dp("c10", c10), 2, cycle)
    expect(fails, "RD-F121 C10o 같은 · 옛 판은 줄 글자에 주소가 없어 못 봄 → 단독(새로 세는 꼴 — 릴리즈 노트)", dp("c10o", c10, old_tool), 0,
           single)
    # ── 쓰는 곳마다 같은 셈(대상 = 소비되는 쪽 · web 단위 · 시험 포함 그래프 · 공급 면 ④ · 계약) ──
    side: Path = _project(td / "f121-side", {
        **F121_FILES,
        F121_SCHEMA: _f121_schema(doc_line),                               # docstring 만 — 호출 아님
        "application/demo/test/test_schema.py": ("from application.demo.driving_layer.api.thing.schema.schema_out import ThingOut\n\n\n"
                                                 "def test_key() -> None:\n    assert ThingOut.key\n"),
        "application/zeta/__init__.py": "",
        "application/zeta/domain_layer/z.py": "Z: int = 1\n",
        "application/zeta/test/test_z.py": '"""시험 설명 — 손님 화면은 GET /api/thing/1 을 부른다."""\n\n\ndef test_z() -> None:\n    assert True\n',
        "web/away/templates/away.html": "<p>x</p>\n<!-- /api/thing/1 -->\n",
        "web/far/static/far.js": "// GET /api/thing/1\nconst n = 1;\n",
        ".dddjango-web/20261026-0300-x/server-contract.json": '{"paths": {}, "info": {"description": "see /api/thing/1"}}\n',
    })

    def side_deps(tag: str, bc: str, tool: Path = TOOL) -> dict:
        out: Path = td / "f121-side-out" / tag
        run(side, "deps", bc, "--out", str(out), tool=tool)
        p: Path = out / "deps.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
    test_rel: str = "application/demo/test/test_schema.py"
    for tag, tool, want in (("e1", TOOL, False), ("e1o", old_tool, True)):
        got = side_deps(tag, "other", tool)
        kinds: dict = got.get("edit_kinds", {})
        seen: "set[bool]" = {F121_SCHEMA in kinds, test_rel in kinds, "demo" in got.get("http_owners", [])}
        expect(fails, f"RD-F121 {tag.upper()} deps other — docstring 만 가진 demo 파일 · 그 모듈을 import 하는 시험 → «HTTP 소비자» 갈래 · "
               f"http_owners {'에 있음(옛 판)' if want else '에 없음'}", (0 if seen == {want} else 9, json.dumps(got, ensure_ascii=False)), 0)
    for tag, tool, want in (("e3", TOOL, False), ("e3o", old_tool, True)):
        got = side_deps(tag, "demo", tool)
        owners: "list[str]" = got.get("http_owners", [])
        ok: bool = (("web/away" in owners) == want and ("zeta" in got.get("our_bcs", [])) == want and "web/far" in owners
                    and ".dddjango-web/20261026-0300-x" in owners)
        expect(fails, f"RD-F121 {tag.upper()} deps demo — web 단위 HTML 주석만 · 시험 docstring 만(시험 포함 그래프) → 소비 주인 · our_bcs "
               f"{'에 있음(옛 판)' if want else '에 없음'} · JS 주석 web 단위 · 계약 description 은 두 판 모두 셈",
               (0 if ok else 9, json.dumps({k: got.get(k) for k in ("http_owners", "our_bcs")}, ensure_ascii=False)), 0)
    face: Path = _project(td / "f121-face", {
        **F121_FILES,
        "application/base/driving_layer/api/a/a_controller.py": FACE_CONTROLLER.format(prefix="/base-a", name="AController"),
        "application/base/driving_layer/api/b/b_controller.py": FACE_CONTROLLER.format(prefix="/base-b", name="BController"),
        F121_PAGE: "".join(f'<a hx-get="/api/base-a/items/{i}">{i}</a> <!-- 옛 /api/base-b/{i} -->\n' for i in range(300)),
    })
    for tag, tool, want in (("e2", TOOL, False), ("e2o", old_tool, True)):
        out = td / "f121-face-out" / tag
        run(face, "deps", "demo", "--out", str(out), tool=tool)
        faces: "list[str]" = (json.loads((out / "deps.json").read_text(encoding="utf-8")).get("supplier_faces", {}).get("base", [])
                              if (out / "deps.json").is_file() else [])
        ok = ("application/base/driving_layer/api/a/a_controller.py" in faces
              and ("application/base/driving_layer/api/b/b_controller.py" in faces) == want)
        expect(fails, f"RD-F121 {tag.upper()} 공급 면 ④ — 대상 BC 템플릿이 /base-a 를 부르고 주석에만 /base-b → 면에 b 선언 파일 "
               f"{'있음(옛 판)' if want else '없음'}", (0 if ok else 9, str(faces)), 0)
    calls: "list[str]" = []
    real_mask = ra._mask_html

    def counting(text: str) -> str:
        calls.append(text[:20])
        return real_mask(text)
    ra._mask_html = counting
    try:
        scan = ra.DepsScan(face)
        ra._supplier_faces(scan, "demo", {"base"})
    finally:
        ra._mask_html = real_mask
    expect(fails, "RD-F121 P1 대상 BC 템플릿 hit 300 줄 → 주석 지우기는 파일당 한 번(소비 셈 · 공급 면 ④ 가 같은 결과를 씀)",
           (0 if len(calls) == 1 else 9, f"_mask_html 호출 {len(calls)}"), 0)
    lines: str = ("a /api/thing/1 b /api/other-api/2\x0c\\/api\\/thing\\/3\x85x /api/things/4 /api/other-api "
                  "\x1c/api/thing/5\x1d\x1e/api/other-api/6\x0bend \\/v2\\/deck\\/7\r\n/api/thing/8\r/v2/deck\n")
    rnd = random.Random(1026)
    pieces: "list[str]" = ["/api/thing/1", "/api/thing", "/api/things", "/api/other-api/2", "\\/api\\/other-api", "\\\\/api/thing",
                           "\\/v2\\/deck", "/v2/deck", "\\/v2/deck",
                           "\n", "\r\n", "\x0c", "\x85", " ", " ", "x", '"', "/", "-", "%"]
    big: Path = _project(td / "f121-big", {
        **F121_FILES,
        "web/big/client.py": "".join(f'U{i}: str = "/api/thing/{i}"\n' for i in range(3000))
                             + 'PAIR: tuple[str, str] = ("/api/thing/a", "/api/thing/b")\n',
        "application/third/driving_layer/api/t/t_controller.py": FACE_CONTROLLER.format(prefix="/v2/deck", name="ThirdController"),
        "web/big/lines.js": lines,
        "web/big/lines.html": lines,
        "web/big/rand.js": "".join(rnd.choice(pieces) for _ in range(6000)),
    })
    old_spec = importlib.util.spec_from_file_location("ra_f121_old", old_tool)
    old_mod = importlib.util.module_from_spec(old_spec)
    old_spec.loader.exec_module(old_mod)                                   # type: ignore[union-attr]
    new_hits: "set[tuple[str, int, str]]" = {(h["file"], h["line"], h["provider"]) for h in ra.DepsScan(big).http
                                             if h["file"] == "web/big/client.py"}
    old_hits: "set[tuple[str, int, str]]" = {(h["file"], h["line"], h["provider"]) for h in old_mod.DepsScan(big).http
                                             if h["file"] == "web/big/client.py"}
    expect(fails, "RD-F121 I1 리터럴 3002 조각(한 줄에 둘) 파일 → (줄, 공급 BC) 한 번씩 · 옛 판과 같은 3001 줄",
           (0 if new_hits == old_hits and len(new_hits) == 3001 else 9, f"새 {len(new_hits)} · 옛 {len(old_hits)}"), 0)
    raw: "tuple[str, ...]" = ("web/big/lines.js", "web/big/lines.html", "web/big/rand.js")
    new_raw: "set[tuple[str, int, str]]" = {(h["file"], h["line"], h["provider"]) for h in ra.DepsScan(big).http if h["file"] in raw}
    old_raw: "set[tuple[str, int, str]]" = {(h["file"], h["line"], h["provider"]) for h in old_mod.DepsScan(big).http
                                            if h["file"] in raw}
    expect(fails, "RD-F121 I2 원문 계열(.js · 주석 없는 .html) 글 전체 훑기 — 여러 줄 끝 글자(\\x0c · \\x85 · U+2028 · U+2029 · \\x1c ~ \\x1e · "
           "\\x0b · \\r) · 한 줄 두 공급 BC · `\\/` · 조각 경계 · 무작위 글 6천 조각 → (파일, 줄, 공급 BC) 가 옛 판(줄마다 셈)과 같다",
           (0 if new_raw == old_raw and len({h for h in new_raw if h[0] != "web/big/rand.js"}) == 18 and len(new_raw) > 200 else 9,
            f"새 {len(new_raw)} · 옛 {len(old_raw)} · 다름 {sorted(new_raw ^ old_raw)[:6]}"), 0)
    for tag, text, want in (
            ("u1", "<p>a</p>\r<!-- x -->\u2028<a hx-get=\"/x\"></a>\x85<!-- y -->\n", "\r\u2028\x85\n"),
            ("u2", '<TITLE><!--</Title><a hx-get="/x"></a>-->\n', None),
            ("u3", '<!--><a hx-get="/x"></a><!-- y -->\n', None)):
        masked: str = ra._mask_html(text)
        kept: bool = len(masked) == len(text) and len(masked.splitlines()) == len(text.splitlines())
        if want is not None:
            kept = kept and "".join(c for c in masked if c in ra._LINE_ENDS) == want and 'hx-get="/x"' in masked
        else:
            kept = kept and 'hx-get="/x"' in masked
        expect(fails, f"RD-F121 {tag.upper()} _mask_html — 줄 끝 글자 · 글자 자리 그대로 · 날 글 요소 닫는 태그(대소문자) · `<!-->` 빈 주석",
               (0 if kept else 9, repr(masked)), 0)
    for tag, label, text, want in (
            ("u4", "짝 없는 `{{` 가 `<script>` 문자열 `}}` 와 맞물리지 않음",
             '<p>{{ </p>\n<script>\nvar s = "}}";\n<!--\nfetch("/x");\n//-->\n</script>\n', True),
            ("u5", "Django 변수 문자열 속 `{% comment %}`", '{{ "{% comment %}" }}<a hx-get="/x"></a>{% comment %}c{% endcomment %}\n', True),
            *((f"u6-{el}", f"날 글 요소 {el} 안 닫히지 않은 `<!--`", f'<{el}><!-- 예시</{el}>\n<a hx-get="/x"></a>\n<!-- 메모 -->\n', True)
              for el in ("iframe", "noembed", "noframes", "noscript")),
            ("u7", "`--!` 뒤가 `>` 가 아니면 닫히지 않음", '<!-- a --!-- <a hx-get="/x"></a> -->\n', False)):
        masked = ra._mask_html(text)
        ok: bool = (len(masked) == len(text) and len(masked.splitlines()) == len(text.splitlines())
                    and ('"/x"' in masked) == want)
        expect(fails, f"RD-F121 {tag.upper()} _mask_html — {label} → 주소 {'남음' if want else '지움'}", (0 if ok else 9, repr(masked)), 0)
    a_url: str = '<a hx-get="/x"></a>'
    for tag, label, text in (
            ("u8a", "한 줄 짝 없는 `{{` 1만 2천", "{# c #}<!-- a -->" + "<p>{{ a </p>" * 12000 + a_url + "<!-- b -->"),
            ("u8b", "한 줄 짝 없는 `{%` 1만 2천", "{# c #}<!-- a -->" + "<p>{% a </p>" * 12000 + a_url + "<!-- b -->"),
            ("u8c", "한 줄 CSS `{#` 1만 2천", "<style>" + "".join("@media(x){#a%d{b:c}}" % i for i in range(12000)) + "</style><!-- x -->"
             + a_url)):
        began: float = time.perf_counter()
        masked = ra._mask_html(text)
        took: float = time.perf_counter() - began
        expect(fails, f"RD-F121 {tag.upper()} _mask_html — {label} → 선형 시간(2 초 안 · 제곱이면 열 초 넘음) · 주소 남음",
               (0 if took < 2.0 and '"/x"' in masked and len(masked) == len(text) else 9, f"{took:.2f} 초"), 0)
    # 짝 없는 여는 글 바꾸기(`_lone_openers_blanked`)는 낱말을 바꾸지 않는다 — 줄 끝 거리 문턱을 0 으로 낮춰 모든 여는 글에서 돌리고,
    # 글자 `{}%#\n\x0cx` 로 만든 길이 6 이하 모든 글(13만 7256 개)의 Django · HTML 낱말(자리 · 종류)을 원문과 사본에서 견준다.
    real_opener: str = ra._LONE_OPENER
    ra._LONE_OPENER = r"\{(?=[{%#])"
    try:
        django_tag: "re.Pattern[str]" = re.compile(ra._DJANGO_TAG)
        html_token: "re.Pattern[str]" = re.compile(ra._HTML_TOKEN, re.S | re.I)
        seen: int = 0
        differ: "list[str]" = []
        for size in range(1, 7):
            for chars in itertools.product("{}%#\n\x0cx", repeat=size):
                text = "".join(chars)
                copy: str = ra._lone_openers_blanked(text)
                seen += 1
                if ([m.span() for m in django_tag.finditer(text)] != [m.span() for m in django_tag.finditer(copy)]
                        or [(m.span(), m.lastgroup) for m in html_token.finditer(text)]
                        != [(m.span(), m.lastgroup) for m in html_token.finditer(copy)]):
                    differ.append(text)
    finally:
        ra._LONE_OPENER = real_opener
    expect(fails, "RD-F121 U9 짝 없는 여는 글 바꾸기 — 문턱 0 · 길이 6 이하 모든 글 13만 7256 개에서 Django · HTML 낱말(자리 · 종류)이 원문과 같다",
           (0 if seen == 137256 and not differ else 9, f"글 {seen} · 다름 {len(differ)} · 예 {differ[:3]!r}"), 0)
    named: str = ("{% verbatim {{ %} }}<p>a</p>{% endverbatim {{ %}" + '{# <a hx-get="/x"></a> #}' + " " * 300 + "\n")
    masked = ra._mask_html(named)
    expect(fails, "RD-F121 U10 긴 줄 · verbatim 이름에 여는 글(`{% verbatim {{ %}` … `{% endverbatim {{ %}`) → 이름까지 같은 끝에서 닫히고 뒤 `{# #}` 지움"
           "(태그 내용은 원문에서 읽는다)", (0 if '"/x"' not in masked and len(masked) == len(named) else 9, repr(masked[:80])), 0)


AT_OWN: str = "20261020-0900-refactor-demo"
AT_LINE: str = "실행 · G0 승인 20261020-1000 · 모드 리팩토링 · audit 20261020-0901\n"
AT_LATE: str = "20261028-1000-refactor-other"
AT_LATE_LINE: str = "실행 · G0 승인 20261028-1100 · 모드 리팩토링 · audit 20261028-1001\n"


def _deps_json(folder: Path, tag: str) -> dict:
    p: Path = folder / "deps" / tag / "deps.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def deps_at_cases(fails: "list[str]", td: Path) -> None:
    """설계 A0 — deps 판정 시점은 조정자가 `--at new|continue|dispatch` 로 밝힌다(필수 · 빠지면 실행 불능). `continue` 는 끝나지 않은
    실행 줄 · `dispatch` 는 그 + G1 확정이 있어야 하고 · 이 폴더 refactor-scope.md 를 UTF-8 로 못 읽으면 실행 불능 · `continue` 의 맞물림은
    G1 확정과 무관하게 실행 줄 G0 승인 값으로(검토 2회 a0 재현 — 옛 판 2 · 2 맞기다림) · `new` 도 다른 트리의 이 실행 사본은 뺀다(2회 s1)."""
    old: Path = _pr_old_tool(td)
    repo: Path = _project(td / "at", DEPS_FILES)
    own: Path = repo / ".dddjango" / AT_OWN
    own.mkdir(parents=True)
    scope: Path = own / "refactor-scope.md"
    out = lambda tag: str(own / "deps" / tag)                 # noqa: E731
    scope.write_text(AT_LINE, encoding="utf-8")
    expect(fails, "RD-AT1 `--at` 빠짐 → 실행 불능(exit 1)", _raw_run(repo, "deps", "demo", "--out", out("m")), 1,
           "요약: refactor_audit 실행 불능 — 인자 오류")
    expect(fails, "RD-AT1b `--at` 값이 닫힌 셋 밖 → 실행 불능", _raw_run(repo, "deps", "demo", "--out", out("m2"), "--at", "g0"), 1,
           "인자 오류")
    scope.write_text(AT_LINE.rstrip("\n") + " · build_anchor a · G2 승인 20261021-1000\n", encoding="utf-8")
    expect(fails, "RD-AT2 `continue` 인데 이 폴더 실행 줄이 끝남(G2) → 실행 불능", run(repo, "deps", "demo", "--out", out("c1"), "--at",
           "continue"), 1, "끝나지 않은 실행 줄이 없다")
    scope.unlink()
    expect(fails, "RD-AT2b `continue` 인데 refactor-scope.md 없음 → 실행 불능", run(repo, "deps", "demo", "--out", out("c2"), "--at",
           "continue"), 1, "끝나지 않은 실행 줄이 없다")
    expect(fails, "RD-AT2c `dispatch` 인데 refactor-scope.md 없음 → 실행 불능", run(repo, "deps", "demo", "--out", out("c3"), "--at",
           "dispatch"), 1, "끝나지 않은 실행 줄이 없다")
    scope.write_text(AT_LINE, encoding="utf-8")
    expect(fails, "RD-AT3 `dispatch` 인데 G1 확정 없음 → 실행 불능", run(repo, "deps", "demo", "--out", out("d1"), "--at", "dispatch"), 1,
           "`G1 변경판 확정` 줄이 없다")
    _dispatch_own(repo, own, V1_TEXT)
    scope.write_bytes(scope.read_bytes() + b"\n- \xff\n")
    for at in ("dispatch", "new"):
        expect(fails, f"RD-AT4 이 폴더 refactor-scope.md 를 UTF-8 로 못 읽음 + `{at}` → 실행 불능(삼키지 않는 읽기)",
               run(repo, "deps", "demo", "--out", out(f"u-{at}"), "--at", at), 1, "UTF-8 로 못 읽는다")
    # 잇기(G1 전 · Phase 1 중 끊김 · G0 정지 재개) vs 늦게 G0 승인한 이웃(파견 직전) — 검토 2회 a0 재현 꼴
    scope.write_text(AT_LINE + "\n## G0 정지 20261029-0910\n\n- 모드 리팩토링 · audit 20261020-0901 · 사유: 새 빚 질문 답 없음\n",
                     encoding="utf-8")
    shutil.rmtree(own / "behavior")
    (own / "design-spec.md").unlink()
    late: Path = repo / ".dddjango" / AT_LATE
    late.mkdir(parents=True)
    (late / "refactor-scope.md").write_text(AT_LATE_LINE, encoding="utf-8")
    _dispatch_own(repo, late, V1_TEXT)
    expect(fails, "RD-AT5 잇기(G1 전) `continue` vs 늦게 G0 승인한 이웃 → 우리는 그 실행을 뺀다(맞물림 — G1 유무 무관) · exit 0",
           run(repo, "deps", "demo", "--out", out("s1"), "--at", "continue"), 0, "판정 시점 G0", "늦게 G0 승인한 리팩토링 실행 뺌 1",
           f"뺌: 이 작업 트리 .dddjango/{AT_LATE} — 앵커 없는 리팩토링 실행 · G0 승인 20261028-1100")
    expect(fails, "RD-AT5b 같은 · 이웃(파견 직전 `dispatch`)은 먼저 G0 승인한 우리를 센다 → exit 2(맞기다림 풀림 — 0 · 2)",
           run(repo, "deps", "other", "--out", str(late / "deps" / "s1"), "--at", "dispatch"), 2, f".dddjango/{AT_OWN} — BC demo")
    expect(fails, "RD-AT5o 같은 · 옛 판(2.28.0 배포 커밋) 우리 쪽은 G0 이라 맞물림 없이 이웃을 센다 → exit 2(옛 판 2 · 2 맞기다림)",
           _raw_run(repo, "deps", "demo", "--out", out("s1o"), tool=old), 2, f"겹침: 이 작업 트리 .dddjango/{AT_LATE}")
    shutil.rmtree(late)
    # `new` — 버린 앞 실행(커밋됨)의 사본이 다른 작업 트리에 있어도 그 사본(같은 폴더 · 같은 실행 줄)은 뺀다
    scope.write_text(AT_LINE, encoding="utf-8")
    _dispatch_own(repo, own, V1_TEXT)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "앞 실행 기록(버림)")
    _git(repo, "worktree", "add", "-q", "-b", "at-copy", str(td / "at-copy"))
    expect(fails, "RD-AT6 `new` + 다른 작업 트리에 버린 앞 실행 사본(같은 폴더 · 같은 실행 줄) → 그 사본은 빼고 G0 판정 · exit 0",
           run(repo, "deps", "demo", "--out", out("n1"), "--at", "new"), 0, "판정 시점 G0", "레인 겹침 없음", "활성 실행 0")
    got: dict = _deps_json(own, "n1")
    expect(fails, "RD-AT6b deps.json `at` = new · stage G0", (0 if got.get("at") == "new" and got.get("stage") == "G0" else 9,
                                                              json.dumps({k: got.get(k) for k in ("at", "stage")})), 0)
    _git(repo, "worktree", "remove", "--force", str(td / "at-copy"))


OC_NEW_LINE: str = "실행 · G0 승인 20261029-1000 · 모드 리팩토링 · audit 20261020-0901\n"   # 같은 폴더 새 실행(실행 줄 바뀜)
OC_OTHER_LINE: str = "실행 · G0 승인 20261021-0900 · 모드 리팩토링 · audit 20261021-0850\n"  # 다른 트리가 같은 이름 폴더로 먼저 G0 승인


def deps_own_copy_cases(fails: "list[str]", td: Path) -> None:
    """구현 검토 결함 1 — 다른 작업 트리의 이 폴더 옛 사본(그 트리의 자기 변경 아님 · MH 판으로 판정)은 이 실행 자신이거나 버린 앞 실행
    기록이라 활성 실행에서 뺀다(`요약:` `이 폴더 옛 사본 뺌 n`) — 실행 줄이 바뀐 뒤 파견 직전 deps 가 자기와 겹치지 않는다. 같은 이름
    폴더가 그 트리의 자기 변경으로 돌면 지금처럼 디스크로 판정한다(실행 줄이 다르면 겹침)."""
    old: Path = _pr_old_tool(td)

    def dp(repo: Path, own: Path, tag: str, tool: "Path | None" = None) -> "tuple[int, str]":
        if tool is not None:
            return _raw_run(repo, "deps", "demo", "--out", str(own / "deps" / tag), tool=tool)
        return run(repo, "deps", "demo", "--out", str(own / "deps" / tag), "--at", "dispatch")

    def lane(name: str) -> "tuple[Path, Path]":
        repo: Path = _project(td / name, DEPS_FILES)
        own: Path = repo / ".dddjango" / AT_OWN
        own.mkdir(parents=True)
        (own / "refactor-scope.md").write_text(AT_LINE, encoding="utf-8")
        return repo, own
    # 재현 1 — 버린 앞 실행 기록(커밋됨)의 사본이 다른 트리에 · 같은 폴더 새 실행 G0 승인(실행 줄 바뀜) 뒤 첫 파견 직전
    repo, own = lane("oc1")
    _dispatch_own(repo, own, V1_TEXT)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "앞 실행 기록(버림)")
    copy: Path = td / "oc1-copy"
    _git(repo, "worktree", "add", "-q", "-b", "oc1-copy", str(copy))
    (own / "refactor-scope.md").write_text(OC_NEW_LINE, encoding="utf-8")
    _dispatch_own(repo, own, V1_TEXT)
    expect(fails, "RD-OC1 다른 트리에 버린 앞 실행 사본(그 트리 변경 아님) · 새 실행 첫 파견 직전 → 이 폴더 옛 사본 뺌 1 · 겹침 없음(exit 0)",
           dp(repo, own, "c1"), 0, "레인 겹침 없음", "활성 실행 0", "이 폴더 옛 사본 뺌 1")
    # 지킴 — 같은 이름 폴더가 다른 트리에서 그 트리의 자기 변경(다른 실행 줄 · 먼저 G0 승인)으로 돎 → 디스크 판정 · 겹침
    (copy / ".dddjango" / AT_OWN / "refactor-scope.md").write_text(OC_OTHER_LINE, encoding="utf-8")
    got = dp(repo, own, "c4")
    expect(fails, "RD-OC4 같은 이름 폴더가 다른 트리의 자기 변경으로 돎(실행 줄 다름) → 그대로 디스크 판정 · 겹침(exit 2)",
           (got[0] if "(main 판)" not in got[1] else 9, got[1]), 2, f".dddjango/{AT_OWN} — BC demo", "레인 겹침 1 ",
           "이 폴더 옛 사본 뺌 0")
    # 재현 2 — 이 실행 기록을 주 작업 트리(= 이 레인)에 커밋 · 그 전에 갈라진 레인에 옛 사본(MH 판 = 이 실행 자신)
    repo, own = lane("oc2")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "앞 실행 G0 기록")
    _git(repo, "worktree", "add", "-q", "-b", "oc2-lane", str(td / "oc2-lane"))
    (own / "refactor-scope.md").write_text(OC_NEW_LINE, encoding="utf-8")
    _dispatch_own(repo, own, V1_TEXT)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "이 실행 기록 커밋(새 실행 · G1)")
    _stale_bases(repo, own)
    expect(fails, "RD-OC2 이 실행 기록 커밋됨 · 다른 레인에 옛 사본(MH 판 = 이 실행) → 이 폴더 옛 사본 뺌 1 · 겹침 없음(exit 0)",
           dp(repo, own, "c2"), 0, "레인 겹침 없음", "이 폴더 옛 사본 뺌 1")
    expect(fails, "RD-OC2o 같은 · 옛 판(2.28.0 배포 커밋) → 자기와 겹침(exit 2 — 회귀 아님 · 이 판이 고친 것)",
           dp(repo, own, "c2o", tool=old), 2, f"(main 판) .dddjango/{AT_OWN} — BC demo")
    # 재현 3 — 실행 하나뿐 · 기록 커밋 → 다른 레인 생김 → 앵커 커밋 → G1′ 승인 직후 파견 직전
    repo, own = lane("oc3")
    _dispatch_own(repo, own, V1_TEXT)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "이 실행 G1 기록")
    _git(repo, "worktree", "add", "-q", "-b", "oc3-lane", str(td / "oc3-lane"))
    scope: Path = own / "refactor-scope.md"
    anchor: str = _git(repo, "rev-parse", "HEAD").strip()
    scope.write_text(scope.read_text(encoding="utf-8").replace(AT_LINE.rstrip("\n"), AT_LINE.rstrip("\n") + f" · build_anchor {anchor}",
                                                               1), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "앵커 기록")
    expect(fails, "RD-OC3 실행 하나뿐 · 앵커 커밋 뒤 G1′ 직후 파견 직전 · 다른 레인에 앵커 전 사본 → 이 폴더 옛 사본 뺌 1(exit 0)",
           dp(repo, own, "c3"), 0, "레인 겹침 없음", "이 폴더 옛 사본 뺌 1")
    # 지킴 — 주 작업 트리의 이 실행 사본(디스크 판정)은 지금처럼 같은 실행 줄로만 뺀다(이 폴더 옛 사본 빼기 밖)
    repo, own = lane("oc5")
    _dispatch_own(repo, own, V1_TEXT)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "이 실행 기록")
    wt: Path = td / "oc5-lane"
    _git(repo, "worktree", "add", "-q", "-b", "oc5-lane", str(wt))
    wown: Path = wt / ".dddjango" / AT_OWN
    expect(fails, "RD-OC5 레인에서 R1 `new` · 주 작업 트리에 이 실행 사본(같은 실행 줄) → 실행 줄 같음으로 뺌 · 옛 사본 뺌 0(exit 0)",
           run(wt, "deps", "demo", "--out", str(wown / "deps" / "c5"), "--at", "new"), 0, "레인 겹침 없음", "활성 실행 0",
           "이 폴더 옛 사본 뺌 0")


def deps_rerun_cases(fails: "list[str]", td: Path) -> None:
    """설계 A2(②) — 같은 폴더를 다시 쓰는 새 실행의 R1 은 `--at new` 로 앞 실행 기록(G1 확정 · 명세 다른 BC 편집 목록 · 앞 실행 G0
    승인 값)을 끊는다 — 옛 판은 앞 실행 G1 확정을 집어 «파견 직전» · 앞 G0 값으로 늦은 이웃을 뺐다(fail-open) · 판형 밖 G1 기록이면
    실행 불능이었다. 잇기(`dispatch`)는 지금과 같다."""
    old: Path = _pr_old_tool(td)
    repo: Path = _project(td / "pr2", DEPS_FILES)
    own: Path = repo / ".dddjango" / AT_OWN
    own.mkdir(parents=True)
    scope: Path = own / "refactor-scope.md"
    out = lambda tag: str(own / "deps" / tag)                 # noqa: E731
    late: Path = repo / ".dddjango" / AT_LATE
    late.mkdir(parents=True)
    (late / "refactor-scope.md").write_text(AT_LATE_LINE, encoding="utf-8")
    _dispatch_own(repo, late, V1_TEXT)
    ended: str = AT_LINE.rstrip("\n") + " · build_anchor a1 · G2 승인 20261021-1000\n"
    scope.write_text(ended, encoding="utf-8")
    _dispatch_own(repo, own, V1_TEXT)                         # 앞 실행(G2 끝)의 G1 확정 · 명세가 남음
    seen: str = f"겹침: 이 작업 트리 .dddjango/{AT_LATE}"
    gone: str = f"뺌: 이 작업 트리 .dddjango/{AT_LATE}"
    expect(fails, "RD-PR2 A 앞 실행 G2 끝 · 새 실행 R1 `new` · 늦은 이웃 → G0 판정 · 그 이웃을 센다(exit 2)",
           run(repo, "deps", "demo", "--out", out("a"), "--at", "new"), 2, "판정 시점 G0", seen)
    expect(fails, "RD-PR2 Ao 같은 · 옛 판(2.28.0 배포 커밋) → 앞 실행 G1 확정으로 «파견 직전» · 앞 G0 값으로 이웃을 뺀다(exit 0 · fail-open)",
           _raw_run(repo, "deps", "demo", "--out", out("ao"), tool=old), 0, "판정 시점 파견 직전", gone)
    scope.write_text(AT_LINE, encoding="utf-8")
    _dispatch_own(repo, own, V1_TEXT)                         # 버린 앞 실행(G2 없음 · G1 확정 남음)
    expect(fails, "RD-PR2 B 폐기 뒤 새 실행 R1 `new` → G0 판정 · 늦은 이웃을 센다(exit 2)",
           run(repo, "deps", "demo", "--out", out("b"), "--at", "new"), 2, "판정 시점 G0", seen)
    expect(fails, "RD-PR2 Bo 같은 · 옛 판 → 파견 직전 · 이웃 뺌(exit 0)", _raw_run(repo, "deps", "demo", "--out", out("bo"), tool=old), 0,
           "판정 시점 파견 직전", gone)
    expect(fails, "RD-PR2 E 잇기 `dispatch` → 지금과 같음(파견 직전 · 늦은 이웃 뺌 · exit 0)",
           run(repo, "deps", "demo", "--out", out("e"), "--at", "dispatch"), 0, "판정 시점 파견 직전",
           "늦게 G0 승인한 리팩토링 실행 뺌 1", gone)
    shutil.rmtree(late)
    shutil.rmtree(own)
    own.mkdir(parents=True)
    scope.write_text(ended + "\n## G1 변경 결정 판형 밖 머리\n\n- G1 변경판 확정 2026-10-24 09:55 · digest 0\n", encoding="utf-8")
    expect(fails, "RD-PR2 F 앞 실행 G1 기록이 판형 밖 + `new` → 읽지 않는다(실행 불능 아님 · G0 · exit 0)",
           run(repo, "deps", "demo", "--out", out("f"), "--at", "new"), 0, "판정 시점 G0")
    expect(fails, "RD-PR2 Fo 같은 · 옛 판 → 앞 실행 G1 기록 판형 밖으로 실행 불능(exit 1)",
           _raw_run(repo, "deps", "demo", "--out", out("fo"), tool=old), 1, "판형")
    scope.write_text(ended, encoding="utf-8")
    (own / "design-spec.md").write_text("# 설계 명세 — demo\n\n## 다른 BC 편집 목록\n\n- application/zeta/a.py · 받는 쪽 어댑터 · V1\n",
                                        encoding="utf-8")
    x: Path = repo / ".dddjango" / "20261027-0900-zeta-screen"
    x.mkdir(parents=True)
    (x / "refactor-scope.md").write_text("실행 · G0 승인 20261027-0900\n", encoding="utf-8")
    (x / "design-spec.md").write_text("# x\n\n<!-- machine: file-plan -->\n```paths\nupdate application/zeta/a.py\n```\n",
                                      encoding="utf-8")
    expect(fails, "RD-PR2 G 앞 실행 명세 다른 BC 편집 경로를 고치는 무관 실행 + `new` → 우리 경로 아님 · 겹침 없음(exit 0)",
           run(repo, "deps", "demo", "--out", out("g"), "--at", "new"), 0, "판정 시점 G0", "레인 겹침 없음")
    expect(fails, "RD-PR2 Go 같은 · 옛 판 → 앞 실행 다른 BC 편집 경로로 겹침(exit 2)",
           _raw_run(repo, "deps", "demo", "--out", out("go"), tool=old), 2, "경로 application/zeta/a.py")


ST_PLAN: str = "application/demo/domain_layer/policy.py"            # 명세 file-plan(대상 BC 안)
ST_EXTRA: str = "application/demo/domain_layer/extra.py"            # 대상 BC 안 · 설계 범위 밖
ST_FACE: str = "application/base/driving_layer/open_host_service/base_service.py"   # 좁은 공급 면
ST_SPEC: str = ("# 설계 명세 — demo\n\n## 바뀌는 것 목록\n\n" + V1_TEXT + "\n## 다른 BC 편집 목록\n\n"
                f"- {ACL_REL} · 받는 쪽 어댑터 · V1\n\n<!-- machine: file-plan -->\n```paths\nupdate {ST_PLAN}  # S1\n```\n")
ST_TARGET: str = "→ 처분: main 받기 → 폐기 → 새 실행"
ST_G1P: str = "→ 처분: 수정 모드 2번(G1′)"


class StaleLane:
    """파견 직전 낡음(설계 A4) 픽스처 — 주 작업 트리(`main` · MH) + 레인 작업 트리(`lane`) · 이 실행(레인 · 앵커 없는 리팩토링 ·
    G1 확정 · audit `- HEAD` 와 예보 기준선 = 레인 HEAD). `sub` 를 주면 프로젝트 뿌리가 저장소의 하위 폴더다."""

    def __init__(self, td: Path, name: str, files: "dict[str, str] | None" = None, sub: str = "",
                 line: str = AT_LINE) -> None:
        self.git_main: Path = td / name / "main"
        self.git_main.mkdir(parents=True)
        _git(self.git_main, "init", "-q", "-b", "main")
        _git(self.git_main, "config", "user.email", "t@t")
        _git(self.git_main, "config", "user.name", "t")
        self.main: Path = self.git_main / sub if sub else self.git_main
        for rel, body in (files or DEPS_FILES).items():
            (self.main / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.main / rel).write_text(body, encoding="utf-8")
        _git(self.git_main, "add", "-A")
        _git(self.git_main, "commit", "-qm", "base")
        self.git_lane: Path = td / name / "lane"
        _git(self.git_main, "worktree", "add", "-q", "-b", "lane", str(self.git_lane))
        self.lane: Path = self.git_lane / sub if sub else self.git_lane
        self.own: Path = self.lane / ".dddjango" / AT_OWN
        self.own.mkdir(parents=True)
        (self.own / "refactor-scope.md").write_text(line, encoding="utf-8")
        self.confirm()

    def confirm(self, spec: str = ST_SPEC) -> None:
        """G1 확정(명세 `spec` 의 digest) · 두 기준 = 지금 레인 HEAD."""
        _dispatch_own(self.lane, self.own, V1_TEXT)
        (self.own / "design-spec.md").write_text(spec, encoding="utf-8")
        digest: str = ra.snapshot_digest(ra.changes_snapshot(self.own, self.lane))
        scope: Path = self.own / "refactor-scope.md"
        scope.write_text(re.sub(r"· digest \w+ · 후보", f"· digest {digest} · 후보", scope.read_text(encoding="utf-8")),
                         encoding="utf-8")

    @staticmethod
    def commit(tree: Path, rel: str, body: "str | None", msg: str) -> str:
        p: Path = tree / rel
        if body is None:
            p.unlink()
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, encoding="utf-8")
        _git(tree, "add", "-A", "--", rel)
        _git(tree, "commit", "-qm", msg)
        return _git(tree, "rev-parse", "HEAD").strip()

    def dp(self, tag: str, at: str = "dispatch", tool: "Path | None" = None) -> "tuple[int, str]":
        if tool is not None:
            return _raw_run(self.lane, "deps", "demo", "--out", str(self.own / "deps" / tag), tool=tool)
        return run(self.lane, "deps", "demo", "--out", str(self.own / "deps" / tag), "--at", at)

    def data(self, tag: str) -> dict:
        return _deps_json(self.own, tag)


def _order(text: str, *heads: str) -> bool:
    """출력 줄머리가 이 차례로 나오는가(모두 있어야 한다)."""
    at: "list[int]" = [text.find(h) for h in heads]
    return all(i >= 0 for i in at) and at == sorted(at)


def deps_stale_cases(fails: "list[str]", td: Path) -> None:
    """설계 A4(④) — `--at dispatch` · 앵커 없는 실행만: 대상 낡음(audit `- HEAD` 뒤 `application/<bc>/` 커밋 차분) · 설계 낡음(마지막
    실행 경계 뒤 마지막 예보 절 기준선 SHA 뒤 file-plan ∪ 다른 BC 편집 ∪ 공급 면 커밋 차분) · 커밋 차분 = `<기준>..HEAD` ∪ (MH ≠ HEAD 면)
    `<기준>...<MH>` 가운데 기준 대 MH 내용이 다른 것 · pathspec · `--no-renames` · 넓힌 공급 면만이면 보고만 · 기준 모름 처분 · 차례."""
    old: Path = _pr_old_tool(td)
    s = StaleLane(td, "t1")
    expect(fails, "RD-ST0 바탕 — 두 기준 = 레인 HEAD · 바뀜 없음 → 낡음 0(exit 0)", s.dp("t0"), 0, "판정 시점 파견 직전", "낡음 대상 0 · 설계 0")
    s.commit(s.main, ST_EXTRA, "E: int = 1\n", "다른 레인 착륙(대상 BC)")
    expect(fails, "RD-ST1 대상 낡음 — main 에만 대상 BC 착륙(레인 미수령) → exit 2 · 처분 main 받기 → 폐기 → 새 실행",
           s.dp("t1"), 2, f"  대상 낡음: {ST_EXTRA}", ST_TARGET, "낡음 대상 1 · 설계 0")
    expect(fails, "RD-ST1o 같은 · 옛 판(2.28.0 배포 커밋) → 낡음을 재지 않는다(exit 0)", s.dp("t1o", tool=old), 0, "레인 겹침 없음")
    _git(s.git_lane, "merge", "-q", "--no-edit", "main")
    expect(fails, "RD-ST2a main 받기만(audit 다시 안 함) → audit 기준 뒤 레인 HEAD 가 대상 BC 를 바꿈 → 대상 낡음(exit 2)",
           s.dp("t2a"), 2, f"  대상 낡음: {ST_EXTRA}")
    _stale_bases(s.lane, s.own)
    expect(fails, "RD-ST2 main 받은 뒤 새 audit(기준 = 받은 HEAD) → 0", s.dp("t2"), 0, "낡음 대상 0 · 설계 0")
    (s.lane / ST_EXTRA).write_text("E: int = 3  # 사용자 작업 중\n", encoding="utf-8")
    (s.lane / "application/demo/domain_layer/draft.py").write_text("D: int = 1\n", encoding="utf-8")
    expect(fails, "RD-ST3 audit 뒤 대상 BC 사용자 미커밋 · 미추적 → 보지 않는다(exit 0 — 폐기 순환 없음 · 옛 판과 같음)", s.dp("t3"), 0,
           "낡음 대상 0 · 설계 0")
    _git(s.git_lane, "checkout", "-q", "--", ".")
    (s.lane / "application/demo/domain_layer/draft.py").unlink()
    plan: Path = s.own / "audit" / "20261020-0901" / "plan.md"
    plan.write_text(plan.read_text(encoding="utf-8").replace("- BC 미커밋 변경 0", "- BC 미커밋 변경 2"), encoding="utf-8")
    expect(fails, "RD-ST4 audit `BC 미커밋 변경 2` → 0(커밋 차분만 본다)", s.dp("t4"), 0, "낡음 대상 0 · 설계 0")
    plan.write_text(re.sub(r"- HEAD \w+", "- HEAD " + "d" * 40, plan.read_text(encoding="utf-8")), encoding="utf-8")
    expect(fails, "RD-ST5 audit `- HEAD` 못 풂 → 대상 기준 모름(exit 2 · 대상 낡음과 같은 처분)", s.dp("t5"), 2,
           "  대상 기준 모름: ", ST_TARGET)
    plan.unlink()
    expect(fails, "RD-ST5b audit plan.md 없음 → 대상 기준 모름(exit 2)", s.dp("t5b"), 2, "  대상 기준 모름: ", "plan.md")
    # 체리픽 — 레인이 main 착륙분을 체리픽으로 받은 뒤 audit(조상 관계 없음 · 내용 같음)
    c = StaleLane(td, "t6")
    landed: str = c.commit(c.main, ST_EXTRA, "E: int = 1\n", "다른 레인 착륙(대상 BC)")
    acl: str = c.commit(c.main, ACL_REL, DEPS_FILES[ACL_REL] + "\nW: int = 1\n", "다른 레인 착륙(받는 쪽 어댑터)")
    _git(c.git_lane, "cherry-pick", "-x", landed, acl)
    c.confirm()
    expect(fails, "RD-ST6 체리픽으로 받은 착륙(내용 같음) 뒤 audit · 예보 → 대상 · 설계 낡음 0(exit 0)", c.dp("t6"), 0,
           "낡음 대상 0 · 설계 0")
    # 설계 낡음
    d = StaleLane(td, "d1")
    d.commit(d.lane, ACL_REL, DEPS_FILES[ACL_REL] + "\nW: int = 1\n", "레인에서 다른 BC 편집 파일 커밋")
    expect(fails, "RD-SD1 설계 낡음 — 다른 BC 편집 파일 커밋(레인) → exit 2 · 처분 G1′", d.dp("d1"), 2, f"  설계 낡음: {ACL_REL}",
           ST_G1P, "낡음 대상 0 · 설계 1")
    d = StaleLane(td, "d2")
    d.commit(d.main, ACL_REL, DEPS_FILES[ACL_REL] + "\nW: int = 1\n", "다른 레인 착륙(받는 쪽 어댑터)")
    expect(fails, "RD-SD2 설계 낡음 — main 착륙 미수령(다른 BC 편집 파일) → exit 2", d.dp("d2"), 2, f"  설계 낡음: {ACL_REL}", ST_G1P)
    _git(d.git_lane, "merge", "-q", "--no-edit", "main")
    expect(fails, "RD-SD2b main 받기만(G1′ 전) → 레인 HEAD 가 설계 기준 뒤 바꿈 → 설계 낡음 그대로(exit 2)", d.dp("d2b"), 2,
           f"  설계 낡음: {ACL_REL}")
    report: Path = d.own / "pregate-report.md"
    head: str = _git(d.lane, "rev-parse", "HEAD").strip()
    report.write_text(report.read_text(encoding="utf-8") + f"\n## pre-gate 예보 — 2026-10-25T09:40:00Z · design-spec.md\n\n"
                      f"- 기준선 SHA: `{head}` (--base HEAD)\n- 판정: green\n", encoding="utf-8")
    expect(fails, "RD-SU4 G1′ 새 예보 절(기준선 = 받은 HEAD) 뒤 → 0", d.dp("u4"), 0, "낡음 대상 0 · 설계 0")
    d = StaleLane(td, "d3")
    d.commit(d.main, ST_FACE, DEPS_FILES[ST_FACE] + "\nV: int = 1\n", "다른 레인 착륙(공급 면)")
    expect(fails, "RD-SD3 설계 낡음 — 좁은 공급 면 파일 착륙 → exit 2", d.dp("d3"), 2, f"  설계 낡음: {ST_FACE}", ST_G1P)
    d.commit(d.main, "application/third/domain_layer/y.py", DEPS_FILES["application/third/domain_layer/y.py"] + "\nQ: int = 1\n",
             "범위 밖")
    _git(d.git_lane, "merge", "-q", "--no-edit", "main")
    d.confirm()
    d.commit(d.main, "application/third/domain_layer/y.py", DEPS_FILES["application/third/domain_layer/y.py"] + "\nQ: int = 2\n",
             "범위 밖(직접 import 자리 · E 밖)")
    expect(fails, "RD-SD6 E 밖(레인 경로지만 file-plan · 다른 BC 편집 · 공급 면 아님) 착륙 → 0", d.dp("d6"), 0, "낡음 대상 0 · 설계 0")
    (d.lane / ACL_REL).write_text(DEPS_FILES[ACL_REL] + "\nU: int = 1\n", encoding="utf-8")
    (d.lane / "application/base/driving_layer/open_host_service/new_face.py").write_text("N: int = 1\n", encoding="utf-8")
    expect(fails, "RD-SD5 설계 범위 미커밋 · 미추적만 → 0(커밋 차분만 — G1 전 미커밋 되풀이 막음)", d.dp("d5"), 0,
           "낡음 대상 0 · 설계 0")
    w = StaleLane(td, "d4", {**DEPS_FILES, "application/base/urls.py":
                             "from django.urls import path\nurlpatterns = [path(\"x/\", None)]\n"})
    w.commit(w.main, "application/base/domain_layer/unrelated.py", "U: int = 1\n", "다른 레인 착륙(넓힌 공급 면만)")
    expect(fails, "RD-SD4 넓힌 공급 면만 바뀜 → 보고만(exit 0 · coder 입력 · G2 배너)", w.dp("d4"), 0,
           "  설계 낡음(넓힌 공급 면 — 보고만): application/base/domain_layer/unrelated.py",
           "→ coder 파견 입력 · G2 배너에 싣는다", "낡음 대상 0 · 설계 0 · 보고만 1")
    w.commit(w.main, ACL_REL, DEPS_FILES[ACL_REL] + "\nW: int = 1\n", "다른 레인 착륙(받는 쪽 어댑터)")
    expect(fails, "RD-SD4b 넓힌 공급 면 + 다른 BC 편집 파일 함께 → 설계 낡음(exit 2)", w.dp("d4b"), 2, f"  설계 낡음: {ACL_REL}", ST_G1P)
    # 판정 밖
    x = StaleLane(td, "x1", line=AT_LINE.rstrip("\n") + " · build_anchor abc\n")
    x.commit(x.main, ST_EXTRA, "E: int = 1\n", "다른 레인 착륙(대상 BC)")
    got = x.dp("x1")
    expect(fails, "RD-SX1 `build_anchor` 있음 → 낡음 판정 밖(exit 0 · 대상 낡음 줄 없음)",
           (got[0] if "대상 낡음:" not in got[1] else 9, got[1]), 0, "낡음 판정 밖(앵커 뒤)")
    x = StaleLane(td, "x2")
    x.commit(x.main, ST_EXTRA, "E: int = 1\n", "다른 레인 착륙(대상 BC)")
    got = x.dp("x2", at="continue")
    expect(fails, "RD-SX2 `--at continue`(G1 확정 있음) → 낡음 판정 밖(exit 0 · 대상 낡음 줄 없음)",
           (got[0] if "대상 낡음:" not in got[1] else 9, got[1]), 0, "판정 시점 파견 직전", "--at continue")
    # 설계 기준선 모름 — 출력 `설계 기준선 모름(<갈래>): <까닭> → 처분: …` · 갈래 다섯(경계 값 다름 → 폐기 · 그 밖 G1′)
    u = StaleLane(td, "u1")
    rep: Path = u.own / "pregate-report.md"
    rep.write_text("# pre-gate 리포트\n", encoding="utf-8")
    expect(fails, "RD-SU1 예보 절 없음 → 설계 기준선 모름(예보 절 없음) · 처분 G1′(exit 2)", u.dp("u1"), 2,
           "  설계 기준선 모름(예보 절 없음): ", ST_G1P)
    rep.unlink()
    expect(fails, "RD-SU1b pregate-report.md 없음 → 설계 기준선 모름(예보 절 없음) · G1′(exit 2)", u.dp("u1b"), 2,
           "  설계 기준선 모름(예보 절 없음): ", ST_G1P)
    rep.write_text(f"## pre-gate 예보 — 2026-10-24T09:40:00Z · design-spec.md\n\n- 기준선 SHA: `{'d' * 40}` (--base HEAD)\n"
                   "- 판정: green\n", encoding="utf-8")
    expect(fails, "RD-SU2 기준선 SHA 못 풂 → 설계 기준선 모름(기준선 SHA 못 풂) · G1′(exit 2)", u.dp("u2"), 2,
           "  설계 기준선 모름(기준선 SHA 못 풂): ", ST_G1P)
    rep.write_text("## pre-gate 예보 — 2026-10-24T09:40:00Z · design-spec.md\n\n- 판정: green\n", encoding="utf-8")
    expect(fails, "RD-SU2b 예보 절에 기준선 SHA 줄 없음 → 설계 기준선 모름(기준선 SHA 못 풂) · G1′(exit 2)", u.dp("u2b"), 2,
           "  설계 기준선 모름(기준선 SHA 못 풂): ", ST_G1P)
    head = _git(u.lane, "rev-parse", "HEAD").strip()
    sec: str = (f"## pre-gate 예보 — 2026-10-24T09:40:00Z · design-spec.md\n\n- 기준선 SHA: `{head}` (--base HEAD)\n"
                "- 판정: green\n")
    rep.write_text("- 실행 경계 — 20261019-0000 · 앞 실행 끝\n\n" + sec, encoding="utf-8")
    expect(fails, "RD-SU3 마지막 실행 경계 값 ≠ 이 실행 G0 승인 값 → 설계 기준선 모름(경계 값 다름) · 처분 폐기(exit 2)", u.dp("u3"), 2,
           "  설계 기준선 모름(경계 값 다름): ", "→ 처분: 폐기")
    rep.write_text("- pre-gate 기준선 — a\n- pre-gate 기준선 — b\n\n" + sec, encoding="utf-8")
    expect(fails, "RD-SU3c 경계 행 없이 pre-gate 기준선 행 둘(앞 실행 흔적) → 설계 기준선 모름(경계 값 다름) · 폐기(exit 2)", u.dp("u3c"),
           2, "  설계 기준선 모름(경계 값 다름): ", "→ 처분: 폐기")
    rep.write_text("- 실행 경계 — 20261020-1000 · 이 실행\n\n" + sec, encoding="utf-8")
    expect(fails, "RD-SU3b 마지막 실행 경계 값 = 이 실행 G0 승인 값 · 그 뒤 예보 절 → 0", u.dp("u3b"), 0, "낡음 대상 0 · 설계 0")
    rep.write_text(sec + "\n- 실행 경계 — 20261020-1000 · 이 실행\n", encoding="utf-8")
    expect(fails, "RD-SU6 마지막 실행 경계(이 실행 값) 앞에만 예보 절 · 뒤에 없음 → 설계 기준선 모름(예보 절 없음) · G1′(exit 2 — 경계 앞 절을 "
           "기준으로 쓰지 않는다)", u.dp("u6"), 2, "  설계 기준선 모름(예보 절 없음): ", ST_G1P)
    rep.write_bytes(b"\xff\n" + sec.encode())
    expect(fails, "RD-SU5 pregate-report.md 를 UTF-8 로 못 읽음 → 실행 불능(exit 1 — G1′ 로도 안 풀림)", u.dp("u5"), 1,
           "UTF-8 로 못 읽는다")
    rep.write_text(sec, encoding="utf-8")
    spec_path: Path = u.own / "design-spec.md"
    spec_text: str = spec_path.read_text(encoding="utf-8")
    spec_path.unlink()
    expect(fails, "RD-SU7 이 실행 명세 없음 → 설계 기준선 모름(명세 없음) · G1′(exit 2)", u.dp("u7"), 2,
           "  설계 기준선 모름(명세 없음): ", ST_G1P)
    spec_path.write_text(spec_text, encoding="utf-8")
    u.commit(u.main, "README.md", "main 만\n", "main 이 앞섬(설계 · 대상 범위 밖 — MH ≠ HEAD)")
    orphan: str = _git(u.lane, "commit-tree", "HEAD^{tree}", "-m", "공통 조상 없는 커밋").strip()
    rep.write_text(sec.replace(head, orphan), encoding="utf-8")
    expect(fails, "RD-SU8 예보 기준선이 MH 와 공통 조상 없음(세 점 차분 실패) → 설계 기준선 모름(차분 못 잼) · G1′(exit 2)", u.dp("u8"), 2,
           "  설계 기준선 모름(차분 못 잼): ", ST_G1P)
    # 차례 · 경계
    o = StaleLane(td, "o1")
    o.commit(o.main, ST_PLAN, DEPS_FILES[ST_PLAN] + "\nZ: int = 1\n", "다른 레인 착륙(file-plan · 대상 BC)")
    got = o.dp("o1")
    expect(fails, "RD-SO1 대상 · 설계 낡음 동시 → 두 줄 · 대상 먼저(exit 2)",
           (got[0] if _order(got[1], "  대상 낡음: ", "  설계 낡음: ") else 9, got[1]), 2, "낡음 대상 1 · 설계 1")
    xr: Path = o.lane / ".dddjango" / "20261003-0900-tool-screen"
    xr.mkdir(parents=True)
    (xr / "refactor-scope.md").write_text("실행 · G0 승인 20261003-0900\n", encoding="utf-8")
    (xr / "design-spec.md").write_text("# x\n\n<!-- machine: file-plan -->\n```paths\nupdate scripts/tool.py\n```\n", encoding="utf-8")
    got = o.dp("o2")
    expect(fails, "RD-SO2 겹침과 낡음 동시 → 겹침 줄이 먼저(파견 정지가 먼저 · exit 2)",
           (got[0] if _order(got[1], "  겹침: ", "  대상 낡음: ", "  설계 낡음: ") else 9, got[1]), 2)
    shutil.rmtree(xr)
    r = StaleLane(td, "o3")
    _git(r.main, "mv", ST_PLAN, "application/demo/domain_layer/rules.py")
    _git(r.main, "commit", "-qm", "다른 레인 착륙(대상 BC 개명)")
    expect(fails, "RD-SO3 개명 착륙 → 옛 · 새 경로 모두(--no-renames)", r.dp("o3"), 2, ST_PLAN, "application/demo/domain_layer/rules.py")
    expect(fails, "RD-SO3b 같은 · 대상 범위(대상 BC) 안 개명은 대상 낡음 줄에 옛 · 새 경로 둘(변경 2 — 개명 감지면 새 경로 하나)", r.dp("o3b"),
           2, f"  대상 낡음: {ST_PLAN} · application/demo/domain_layer/rules.py — ", "대상 BC 커밋 변경 2(")
    sb = StaleLane(td, "o4", sub="srv")
    sb.commit(sb.git_main, "application/demo/outside.py", "O: int = 1\n", "저장소 뿌리(프로젝트 밖)의 같은 이름 경로")
    expect(fails, "RD-SO4b 하위 폴더 프로젝트 · 프로젝트 밖 같은 꼴 경로 착륙 → 0(pathspec 은 프로젝트 기준)", sb.dp("o4b"), 0,
           "낡음 대상 0 · 설계 0")
    sb.commit(sb.main, ST_EXTRA, "E: int = 1\n", "다른 레인 착륙(대상 BC)")
    expect(fails, "RD-SO4 하위 폴더 프로젝트 · 대상 BC 착륙 → 대상 낡음(프로젝트 상대 경로 · exit 2)", sb.dp("o4"), 2,
           f"  대상 낡음: {ST_EXTRA}", ST_TARGET)
    got = sb.data("o4")
    expect(fails, "RD-SO4c deps.json stale 칸 — at dispatch · stale_target 1 · stale_design 0",
           (0 if got.get("at") == "dispatch" and len(got.get("stale_target", [])) == 1 and not got.get("stale_design") else 9,
            json.dumps({k: got.get(k) for k in ("at", "stale_target", "stale_design")}, ensure_ascii=False)), 0)


SUP_DONE: str = "실행 · G0 승인 20261028-0900 · 모드 리팩토링 · audit x · build_anchor abc · G2 승인 20261028-0930\n"
SUP_RUN: str = "실행 · G0 승인 20261028-1400 · 모드 리팩토링 · audit y\n"
SUP_DIR: str = "20261028-0900-refactor-base"


def deps_supplier_cases(fails: "list[str]", td: Path) -> None:
    """설계 A3(③) — 공급자 상태를 `_active_runs` 결과(모든 작업 트리 · MH 판 · 끝 표식)에서 고른다: 공급자를 대상 BC 로 하는(audit
    plan.md BC ∪ 폴더 이름) 리팩토링 실행이 겹침 셈에 들면 `미정리(도는 실행 <폴더>)` · 맞물림으로 뺐으면 `도는 실행(맞물림 — 이 실행
    뒤) <폴더>`(미정리 셈 밖) · 없으면 지금 규칙(앞 실행 절의 G2 를 정리로 읽던 것 포함)."""
    old: Path = _pr_old_tool(td)
    repo: Path = _project(td / "pr3", DEPS_FILES)
    own: Path = repo / ".dddjango" / "20261028-1000-refactor-demo"
    own.mkdir(parents=True)
    bf: Path = repo / ".dddjango" / SUP_DIR
    bf.mkdir(parents=True)
    out = lambda tag: str(own / "deps" / tag)                 # noqa: E731
    running: str = f"내주는 쪽 base(미정리(도는 실행 .dddjango/{SUP_DIR}))"
    (bf / "refactor-scope.md").write_text(SUP_DONE, encoding="utf-8")
    expect(fails, "RD-PR3 S6 공급자 앞 실행 G2 끝(도는 실행 없음) → 정리(exit 0)", run(repo, "deps", "demo", "--out", out("s6"), "--at", "new"),
           0, "내주는 쪽 base(정리(재상정 0))", "미정리 공급자 0")
    (bf / "refactor-scope.md").write_text(SUP_DONE + "\n## ⓐ 재상정 20261028-0920 — G1 재상정\n\n- M3 · 결정 = 별도 요청\n",
                                          encoding="utf-8")
    expect(fails, "RD-PR3 S6b 끝난 실행 몫의 ⓐ 재상정 절(M3) → 정리(재상정 1)", run(repo, "deps", "demo", "--out", out("s6b"), "--at", "new"),
           0, "내주는 쪽 base(정리(재상정 1))")
    (bf / "refactor-scope.md").write_text(SUP_RUN, encoding="utf-8")
    expect(fails, "RD-PR3 S7 공급자 새 실행 도는 중 → 미정리(도는 실행 <폴더>) · 미정리 공급자 1 · 겹침(exit 2)",
           run(repo, "deps", "demo", "--out", out("s7"), "--at", "new"), 2, running, "미정리 공급자 1")
    (bf / "refactor-scope.md").write_text(SUP_RUN + "\n# 앞 실행\n\n" + SUP_DONE, encoding="utf-8")
    expect(fails, "RD-PR3 S8 새 실행 도는 중 + `# 앞 실행` 절에 G2 줄 → 미정리(도는 실행) · 미정리 공급자 1",
           run(repo, "deps", "demo", "--out", out("s8"), "--at", "new"), 2, running, "미정리 공급자 1")
    expect(fails, "RD-PR3 S8o 같은 · 옛 판(2.28.0 배포 커밋) → 앞 실행 G2 줄로 정리 · 미정리 공급자 0",
           _raw_run(repo, "deps", "demo", "--out", out("s8o"), tool=old), 2, "내주는 쪽 base(정리(재상정 0))", "미정리 공급자 0")
    (bf / "refactor-scope.md").write_text(SUP_DONE + "\n## 재상정 메모\n", encoding="utf-8")
    expect(fails, "RD-PR3 S9 공급자 새 실행 R0′~G0 승인 전(앞 실행 판 · 새 줄 없음) → 정리 그대로(exit 0)",
           run(repo, "deps", "demo", "--out", out("s9"), "--at", "new"), 0, "내주는 쪽 base(정리(재상정 0))")
    # I(= 진단 S10) — 우리 파견 직전(G0 1200 먼저) · 공급자 늦게 G0 승인(1400) → 맞물림으로 뺌 · 표기만 · 미정리 셈 밖
    (own / "refactor-scope.md").write_text("실행 · G0 승인 20261028-1200 · 모드 리팩토링 · audit 20261028-1001\n", encoding="utf-8")
    _dispatch_own(repo, own, V1_TEXT)
    (bf / "refactor-scope.md").write_text(SUP_RUN + "\n# 앞 실행\n\n" + SUP_DONE, encoding="utf-8")
    expect(fails, "RD-PR3 I 맞물림으로 뺀 늦은 공급자 실행 → `도는 실행(맞물림 — 이 실행 뒤) <폴더>` · 미정리 공급자 0 · exit 0",
           run(repo, "deps", "demo", "--out", out("i"), "--at", "dispatch"), 0,
           f"내주는 쪽 base(도는 실행(맞물림 — 이 실행 뒤) .dddjango/{SUP_DIR})", "미정리 공급자 0",
           f"뺌: 이 작업 트리 .dddjango/{SUP_DIR} — 앵커 없는 리팩토링 실행")
    got: dict = _deps_json(own, "i")
    expect(fails, "RD-PR3 Ib deps.json suppliers 칸도 같은 표기", (0 if got.get("suppliers", {}).get("base", "").startswith(
        "도는 실행(맞물림 — 이 실행 뒤)") else 9, json.dumps(got.get("suppliers"), ensure_ascii=False)), 0)
    # S11(②+③) — 우리 폴더 재사용(앞 실행 G2 끝 · G1 확정 남음) · 새 실행 R1 `new` · 공급자 도는 중(늦은 G0)
    scope: Path = own / "refactor-scope.md"
    scope.write_text(scope.read_text(encoding="utf-8").replace("audit 20261028-1001", "audit 20261028-1001 · build_anchor abc · "
                                                               "G2 승인 20261028-1300", 1), encoding="utf-8")
    expect(fails, "RD-PR3 S11 재사용 폴더 새 실행 R1 `new` · 공급자 도는 중 → G0 · 겹침 exit 2 · 미정리(도는 실행) · 미정리 공급자 1",
           run(repo, "deps", "demo", "--out", out("s11"), "--at", "new"), 2, "판정 시점 G0", running, "미정리 공급자 1")
    expect(fails, "RD-PR3 S11o 같은 · 옛 판 → 파견 직전으로 읽어 공급자 실행을 빼고 정리(exit 0 · 질문 0)",
           _raw_run(repo, "deps", "demo", "--out", out("s11o"), tool=old), 0, "내주는 쪽 base(정리(재상정 0))", "미정리 공급자 0")
    shutil.rmtree(own)
    own.mkdir(parents=True)
    # 여러 폴더 — 옛 폴더 G2 끝 + 새 폴더 도는 실행
    (bf / "refactor-scope.md").write_text(SUP_RUN, encoding="utf-8")
    older: Path = repo / ".dddjango" / "20261001-0900-refactor-base"
    older.mkdir(parents=True)
    (older / "refactor-scope.md").write_text(SUP_DONE, encoding="utf-8")
    expect(fails, "RD-PR3 M 여러 폴더(옛 폴더 G2 끝 + 새 폴더 도는 실행) → 미정리(도는 실행 새 폴더)",
           run(repo, "deps", "demo", "--out", out("m"), "--at", "new"), 2, running, "미정리 공급자 1")
    expect(fails, "RD-PR3 Mo 같은 · 옛 판 → 사전순 첫 G2 폴더로 정리", _raw_run(repo, "deps", "demo", "--out", out("mo"), tool=old), 2,
           "내주는 쪽 base(정리(재상정 0))")
    # W — 공급자 실행이 다른 작업 트리에서 돎(이 트리 사본은 앞 실행 G2 끝)
    wr: Path = _project(td / "pr3w", DEPS_FILES)
    wbf: Path = wr / ".dddjango" / "refactor-base"
    wbf.mkdir(parents=True)
    (wbf / "refactor-scope.md").write_text(SUP_DONE, encoding="utf-8")
    _git(wr, "add", "-A")
    _git(wr, "commit", "-qm", "base 앞 실행 G2 끝")
    lane: Path = td / "pr3w-lane"
    _git(wr, "worktree", "add", "-q", "-b", "lane-base", str(lane))
    (lane / ".dddjango" / "refactor-base" / "refactor-scope.md").write_text(SUP_RUN, encoding="utf-8")
    _git(lane, "add", "-A")
    _git(lane, "commit", "-qm", "base 새 실행 G0")
    wown: Path = wr / ".dddjango" / "refactor-demo"
    wown.mkdir(parents=True)
    expect(fails, "RD-PR3 W 공급자 새 실행이 다른 작업 트리에서 돎 · 겹침 → 미정리(도는 실행 .dddjango/refactor-base)",
           run(wr, "deps", "demo", "--out", str(wown / "deps" / "w"), "--at", "new"), 2,
           "내주는 쪽 base(미정리(도는 실행 .dddjango/refactor-base))", "미정리 공급자 1")
    expect(fails, "RD-PR3 Wo 같은 · 옛 판 → 이 트리 사본(앞 실행 G2)으로 정리",
           _raw_run(wr, "deps", "demo", "--out", str(wown / "deps" / "wo"), tool=old), 2, "내주는 쪽 base(정리(재상정 0))")
    # B — 공급자 실행의 대상 BC 를 audit plan.md 로만 안다(폴더 이름 BC 는 다른 이름)
    br: Path = _project(td / "pr3b", DEPS_FILES)
    misc: str = "20261028-0900-refactor-misc"
    mf: Path = br / ".dddjango" / misc
    (mf / "audit" / "y").mkdir(parents=True)
    (mf / "refactor-scope.md").write_text(SUP_RUN, encoding="utf-8")
    (mf / "audit" / "y" / "plan.md").write_text("# refactor_audit plan\n\n- BC: `base`\n", encoding="utf-8")
    bown: Path = br / ".dddjango" / "refactor-demo"
    bown.mkdir(parents=True)
    expect(fails, "RD-PR3 B 공급자 실행의 대상 BC 가 plan.md 에만(폴더 이름 BC 다름) → 미정리(도는 실행 그 폴더) · 미정리 공급자 1",
           run(br, "deps", "demo", "--out", str(bown / "deps" / "b"), "--at", "new"), 2,
           f"내주는 쪽 base(미정리(도는 실행 .dddjango/{misc}))", "미정리 공급자 1")
    # 받아들인 한계 고정(3회 a3n) — 다른 트리 G2 끝 · 미착륙은 안 보임 · 착륙 뒤 폴더 정리 · squash · 그 가지에서 갈라진 레인 → 겹침 0
    xd: str = ".dddjango/20261027-0900-refactor-third"
    done2: str = "실행 · G0 승인 20261027-0900 · 모드 리팩토링 · audit a1 · build_anchor abc · G2 승인 20261027-1500\n"

    def finished(w: Path) -> None:
        (w / xd).mkdir(parents=True, exist_ok=True)
        (w / xd / "refactor-scope.md").write_text(done2, encoding="utf-8")
        y: Path = w / "application/third/domain_layer/y.py"
        y.write_text(y.read_text(encoding="utf-8") + "\nW: int = 1\n", encoding="utf-8")
        _git(w, "add", "-A")
        _git(w, "commit", "-qm", "third 레인 G2 승인")

    def ours(tree: Path) -> Path:
        o: Path = tree / ".dddjango" / TREE_OWN
        o.mkdir(parents=True, exist_ok=True)
        (o / "refactor-scope.md").write_text(TREE_OWN_LINE, encoding="utf-8")
        _dispatch_own(tree, o, V1_TEXT)
        return o

    for name in ("P1", "P3", "P4", "P6"):
        r: Path = _project(td / f"pr3-{name}", DEPS_FILES)
        w: Path = td / f"pr3-{name}-w"
        _git(r, "worktree", "add", "-q", "-b", "w", str(w))
        finished(w)
        tree: Path = r
        if name == "P3":                                    # merge 착륙 → main 이 옛 실행 폴더 정리
            _git(r, "merge", "-q", "--no-ff", "--no-edit", "w")
            _git(r, "rm", "-rq", xd)
            _git(r, "commit", "-qm", "끝난 실행 폴더 정리")
        elif name == "P4":                                  # squash 착륙 → main 이 옛 실행 폴더 정리
            _git(r, "merge", "-q", "--squash", "w")
            _git(r, "commit", "-qm", "third 착륙(squash)")
            _git(r, "rm", "-rq", xd)
            _git(r, "commit", "-qm", "끝난 실행 폴더 정리")
        elif name == "P6":                                  # 우리 레인이 그 레인 가지에서 갈라짐
            tree = td / f"pr3-{name}-l2"
            _git(r, "worktree", "add", "-q", "-b", "l2", str(tree), "w")
            shutil.rmtree(tree / xd)
            _git(tree, "add", "-A")
            _git(tree, "commit", "-qm", "l2 기록 정리")
        o = ours(tree)
        expect(fails, f"RD-PR3 한계 {name} 다른 트리 G2 끝 실행(미착륙 · 착륙 뒤 폴더 정리 · squash · 갈라진 레인) → 겹침 0(exit 0)",
               run(tree, "deps", "demo", "--out", str(o / "deps" / "p"), "--at", "dispatch"), 0, "레인 겹침 없음")
        if name == "P1":
            expect(fails, "RD-PR3 한계 P1o 같은 · 옛 판도 겹침 0(받아들인 한계 — 옛 판과 같음)",
                   _raw_run(tree, "deps", "demo", "--out", str(o / "deps" / "po"), tool=old), 0, "레인 겹침 없음")


DK_CTRL: str = "application/demo/driving_layer/api/thing/thing_controller.py"
DK_HEAD: str = "from ninja import Field, Schema\nfrom ninja_extra import api_controller, route\n\n\n"


def _dk_ctrl(kw: str, tail: str = "", pre: str = "") -> str:
    """대상 demo 컨트롤러 — 라우트 데코레이터 키워드 `kw` 한 자리만 바꾼다."""
    return (DK_HEAD + pre + "@api_controller(\"/thing\")\nclass ThingController:\n"
            f"    @route.get(\"/\", response={{200: dict}}, {kw})\n    def get(self) -> dict:\n        return {{}}\n" + tail)


def deps_doc_kwarg_cases(fails: "list[str]", td: Path) -> None:
    """설계 A1(①) — 설명 글 키워드 인자(`description=` · `summary=`) 값 아래 상수는 HTTP 소비 글이 아니다(f-string 조각 · `_()` 포함) ·
    호출 인자 · 경로 상수 · `url=` · dict 값(이름이 description 인 dict 키 · `openapi_extra` 안 description 키 포함) · 모듈 상수를
    `description=` 에 넘긴 꼴 · `title=` 은 그대로 센다. 대상 demo 의 한 자리에 other API 주소(other → demo 실제 변이 있어 demo → other
    변이 서면 순환 묶음)."""
    old: Path = _pr_old_tool(td)
    repo: Path = _project(td / "pr1", F121_FILES)
    own: Path = repo / ".dddjango" / F121_OWN
    own.mkdir(parents=True)
    (own / "refactor-scope.md").write_text("실행 · G0 승인 20261026-0100 · 모드 리팩토링 · audit 20261026-0050\n", encoding="utf-8")
    single: str = "순환 성분 단독"
    cycle: str = "지원 안 함: 순환 묶음 demo · other"

    def dp(tag: str, files: "dict[str, str]", tool: "Path | None" = None) -> "tuple[int, str]":
        """그 파일들을 써 deps demo 를 돌리고 원래대로 되돌린다."""
        saved: "dict[str, str | None]" = {rel: (repo / rel).read_text(encoding="utf-8") if (repo / rel).is_file() else None
                                          for rel in files}
        for rel, body in files.items():
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (repo / rel).write_text(body, encoding="utf-8")
        try:
            if tool is not None:
                return _raw_run(repo, "deps", "demo", "--out", str(own / "deps" / tag), tool=tool)
            return run(repo, "deps", "demo", "--out", str(own / "deps" / tag), "--at", "continue")
        finally:
            for rel, body in saved.items():
                if body is None:
                    (repo / rel).unlink()
                else:
                    (repo / rel).write_text(body, encoding="utf-8")
    n1: "dict[str, str]" = {DK_CTRL: _dk_ctrl('description="내 세션 확인(GET /api/other-api/sessions/current) 뒤 부른다"')}
    for tag, label, files in (
            ("n1", "라우트 description= 산문 속 다른 BC 주소", n1),
            ("n2", "라우트 summary=", {DK_CTRL: _dk_ctrl('summary="GET /api/other-api/sessions/current 와 짝"')}),
            ("n3", "Schema Field(description=)", {F121_SCHEMA: DK_HEAD + "class ThingOut(Schema):\n    key: str = Field(..., "
                                                  "description=\"/api/other-api/1 의 열쇠\")\n"}),
            ("n4", "description= 이어 쓴 글 · f-string 조각", {DK_CTRL: _dk_ctrl('description=("첫 줄\\n" f"GET /api/other-api/{1}/x 확인")')}),
            ("n5", "description=_(…) 번역 감싸기", {DK_CTRL: "from django.utils.translation import gettext_lazy as _\n"
                                                + _dk_ctrl('description=_("GET /api/other-api/1")')}),
            ("n6", "description= 바이트 글(바이트 · doctest 갈래)", {DK_CTRL: _dk_ctrl('description=b"GET /api/other-api/1"')})):
        expect(fails, f"RD-PR1 {tag.upper()} {label} → HTTP 소비 아님 · 순환 성분 단독 · exit 0", dp(tag, files), 0, single)
    expect(fails, "RD-PR1 N1o 같은 · 옛 판(2.28.0 배포 커밋) → 순환 묶음 exit 2(이 판이 고친 것)", dp("n1o", n1, old), 2, cycle)
    for tag, label, files in (
            ("k1", "같은 파일 실제 호출(client.get 인자)", {DK_CTRL: _dk_ctrl('description="설명"', "\n\ndef call(client) -> None:\n"
                                                                       "    client.get(\"/api/other-api/1\")\n")}),
            ("k2", "경로 상수", {DK_CTRL: _dk_ctrl('description="설명"', "\n\nOTHER_URL: str = \"/api/other-api/1\"\n")}),
            ("k3", "다른 이름 키워드(url=)", {DK_CTRL: _dk_ctrl('description="설명"', "\n\ndef call(c) -> None:\n"
                                                                         "    c.request(method=\"GET\", url=\"/api/other-api/1\")\n")}),
            ("k4", "description 이름의 dict 키(요청 몸)", {DK_CTRL: _dk_ctrl('description="설명"', "\n\ndef call(c) -> None:\n"
                                                                            "    c.post(\"/x\", json={\"description\": \"/api/other-api/1\"})\n")}),
            ("k5", "openapi_extra 안 description 키", {DK_CTRL: _dk_ctrl('openapi_extra={"description": "/api/other-api/1"}')}),
            ("k6", "모듈 상수를 description= 에 넘김", {DK_CTRL: _dk_ctrl("description=DOC", pre="DOC: str = \"GET /api/other-api/1\"\n\n\n")}),
            ("k7", "title=", {DK_CTRL: _dk_ctrl('title="GET /api/other-api/1"')})):
        expect(fails, f"RD-PR1 {tag.upper()} {label} → 그대로 HTTP 소비 · 순환 묶음 exit 2(범위 고정)", dp(tag, files), 2, cycle)
    # 받는 쪽에서 본 같은 셈 · 공급 면 ④
    side: Path = _project(td / "pr1-side", {**F121_FILES, DK_CTRL: _dk_ctrl(
        'description="내 세션 확인(GET /api/other-api/sessions/current)"')})
    for tag, tool, want in (("e1", None, False), ("e1o", old, True)):
        out: Path = td / "pr1-side-out" / tag
        if tool is None:
            run(side, "deps", "other", "--out", str(out), "--at", "new")
        else:
            _raw_run(side, "deps", "other", "--out", str(out), tool=tool)
        got: dict = json.loads((out / "deps.json").read_text(encoding="utf-8")) if (out / "deps.json").is_file() else {}
        seen: "set[bool]" = {DK_CTRL in got.get("edit_kinds", {}), "demo" in got.get("http_owners", [])}
        expect(fails, f"RD-PR1 {tag.upper()} deps other — 설명 글만 가진 demo 컨트롤러 → «HTTP 소비자» 갈래 · http_owners "
               f"{'에 있음(옛 판)' if want else '에 없음'}", (0 if seen == {want} else 9, json.dumps(
                   {k: got.get(k) for k in ("http_owners", "scc")}, ensure_ascii=False)), 0)
    face: Path = _project(td / "pr1-face", {
        **F121_FILES,
        "application/base/driving_layer/api/a/a_controller.py": FACE_CONTROLLER.format(prefix="/base-a", name="AController"),
        "application/base/driving_layer/api/b/b_controller.py": FACE_CONTROLLER.format(prefix="/base-b", name="BController"),
        "application/demo/driven_layer/adapter/base_client.py": "URL: str = \"/api/base-a/items/1\"\n",
        DK_CTRL: _dk_ctrl('description="옛 창구 /api/base-b/1 대신"'),
    })
    for tag, tool, want in (("e2", None, False), ("e2o", old, True)):
        out = td / "pr1-face-out" / tag
        if tool is None:
            run(face, "deps", "demo", "--out", str(out), "--at", "new")
        else:
            _raw_run(face, "deps", "demo", "--out", str(out), tool=tool)
        faces: "list[str]" = (json.loads((out / "deps.json").read_text(encoding="utf-8")).get("supplier_faces", {}).get("base", [])
                              if (out / "deps.json").is_file() else [])
        ok: bool = ("application/base/driving_layer/api/a/a_controller.py" in faces
                    and ("application/base/driving_layer/api/b/b_controller.py" in faces) == want)
        expect(fails, f"RD-PR1 {tag.upper()} 공급 면 ④ — 대상 운영 코드가 /base-a 를 부르고 description= 에만 /base-b → 면에 b 선언 "
               f"파일 {'있음(옛 판)' if want else '없음'}", (0 if ok else 9, str(faces)), 0)


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


def _only(names: "list[str]") -> int:
    """이름 댄 `(fails, td)` 사례 함수만 돈다(고치기 전 붉음 · 고친 뒤 초록 확인)."""
    fails: "list[str]" = []
    with tempfile.TemporaryDirectory(prefix="ra-fo-") as tmp:
        for name in names:
            globals()[name](fails, Path(tmp) / name)
    if fails:
        print("\nFAIL — refactor_audit 고른 사례 기대 불일치:")
        for f in fails:
            print("  - " + f.replace("\n", "\n    "))
        return 1
    print("\nPASS — refactor_audit 고른 사례 기대 일치")
    return 0


def _only_group() -> int:
    """묶음 사례만(`group_move_cases`) — 변이 시험이 scripts 사본에 대고 돈다."""
    fails: "list[str]" = []
    with tempfile.TemporaryDirectory(prefix="ra-fg-") as tmp:
        group_move_cases(fails, Path(tmp))
    if fails:
        print("\nFAIL — refactor_audit 묶음 사례 기대 불일치:")
        for f in fails:
            print("  - " + f.replace("\n", "\n    "))
        return 1
    print("\nPASS — refactor_audit 묶음 사례 기대 일치")
    return 0


# 변이(묶음 사례가 잡아야 한다) — (이름, ((옛 글, 새 글), …)) · refactor_audit.py 사본에 하나씩
_MUTATIONS: "tuple[tuple[str, tuple[tuple[str, str], ...]], ...]" = (
    ("changes 의 ⊆ 대조 지움", (("        elif e[\"kind\"] == GROUP_IMPORT_KIND and e[\"path\"] not in group_import:",
                                "        elif False:"),)),
    ("residual 이 쌍을 안 따름(M_c)", (("    sub = fg.string_substituter(sorted(pairs.items())) if pairs else None",
                                       "    sub = None"),)),
    ("residual 이 쌍을 안 따름(M_m 바닥)", (("                if f in pairs or f in changed:\n                    same = _rename_only(",
                                           "                if False:\n                    same = _rename_only("),)),
    ("묶음 import 치환 줄의 연결 대조 지움(검토 B9)", (('        elif kind == GROUP_IMPORT_KIND and ref != "0C":',
                                             "        elif False:"),)),
    ("M_c 를 칸 끝 없이 부분 글로 맞춤(검토 SB2)", (("        if any(line and re.search(re.escape(line) + end, text) for line in moved):",
                                            "        if any(line and line in text for line in moved):"),)),
)


def _mutation_test() -> int:
    """변이를 scripts 사본에 하나씩 넣고 묶음 사례(`--only-group`)를 돈다 — 모두 붉어야 green."""
    src: str = TOOL.read_text(encoding="utf-8")
    survived: "list[str]" = []
    for name, edits in _MUTATIONS:
        text: str = src
        bad: str = ""
        for old, new in edits:
            if text.count(old) != 1:
                bad = f"변이 지점이 정확히 한 곳이 아니다({text.count(old)}) — 변이 표를 코드에 맞춰라"
                break
            text = text.replace(old, new, 1)
        if not bad:
            with tempfile.TemporaryDirectory(prefix="ra-mutant-") as tmp:   # 설치본째(코퍼스 · 플랫폼 판별은 scripts 의 부모)
                plugin: Path = Path(tmp) / TOOL.parent.parent.name
                shutil.copytree(TOOL.parent.parent, plugin, symlinks=False, ignore=shutil.ignore_patterns("__pycache__"))
                (plugin / "scripts" / TOOL.name).write_text(text, encoding="utf-8")
                proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--scripts", str(plugin / "scripts"),
                                       "--only-group"], capture_output=True, text=True)
            out: str = proc.stdout + proc.stderr
            if proc.returncode == 0:
                bad = "변이가 살아남음(시험이 못 잡는다)"
            elif "FAIL — refactor_audit 묶음 사례" not in out:
                bad = f"변이가 러너를 깨뜨림(시험 실패가 아님) — {out.strip()[-300:]}"
        if bad:
            survived.append(f"{name}: {bad}")
        else:
            print(f"  죽음 {name}")
    if survived:
        print(f"[mutation] 생존 변이 {len(survived)}건", file=sys.stderr)
        for line in survived:
            print(f"  {line}", file=sys.stderr)
        return 2
    print(f"[mutation] refactor_audit 변이 {len(_MUTATIONS)}종 모두 red")
    return 0


def main() -> int:
    if "--mutation-test" in sys.argv[1:]:
        return _mutation_test()
    if "--only-group" in sys.argv[1:]:
        return _only_group()
    if "--only" in sys.argv[1:-1]:
        return _only(sys.argv[sys.argv.index("--only") + 1].split(","))
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
        changes_collect_cases(fails, td)
        group_move_cases(fails, td)
        update_rows_cases(fails, td)
        g1_time_cases(fails, td)
        support_rule_cases(fails, td)
        retain_notice_cases(fails, td)
        rename_row_cases(fails, td)
        field_rename_row_cases(fails, td)
        review_b_cases(fails, td)
        review_b_deps_cases(fails, td)
        review_b4_cases(fails, td)
        surface_area_cases(fails, td)
        remove_rows_cases(fails, td)
        g1_partial_cases(fails, td)
        closed_window_cases(fails, td)
        resolution_change_cases(fails, td)
        deps_cases(fails, td)
        deps_tree_cases(fails, td)
        deps_stage_cases(fails, td)
        deps_face_cases(fails, td)
        deps_trust_cases(fails, td)
        deps_web_unit_cases(fails, td)
        deps_face_review_cases(fails, td)
        deps_http_text_cases(fails, td)
        deps_at_cases(fails, td)
        deps_rerun_cases(fails, td)
        deps_stale_cases(fails, td)
        deps_supplier_cases(fails, td)
        deps_doc_kwarg_cases(fails, td)
        deps_own_copy_cases(fails, td)
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
