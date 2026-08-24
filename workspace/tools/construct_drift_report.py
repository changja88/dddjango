#!/usr/bin/env python3
"""D11 construct drift — 대표 8종 byte 골든 + 구판(이행 직전) 대비 문면 diff 리포트.

두 역할(V18·T9 — 귀속 매핑표 v2 A-6·중재 W7):
1. **게이트(기본)**: 대표 8종의 기본 red 레인 stdout sha256 을 EXPECTED_SHA 로
   고정한다 — T2-2+(docstring IRI 재저작)·T3 구간에서 stdout 이 «몰래» 바뀌면
   여기서 red. A/B 실런의 검사기(신판)와 검증 생산자(개작 중 검사기)의 construct
   drift(T9)를 byte 층에서 차단하는 골든이다.
2. **리포트(--emit-report)**: 각 검사기의 «이행 직전» 봉인 커밋(SEALED — 검사기별
   stdout 변경 커밋의 부모)에서 구판 스크립트 일체를 추출·실행해 신판과의
   unified diff 를 `workspace/eval/ab/T2-construct-drift.md` 로 전수 기록한다 —
   의도 변경 열거표의 기계 실측 대응물(사람 저작 표 ↔ 기계 diff 상호 검증).

8종 = domain-model·common-container(T0 기존 byte 골든 2) + api-error·EC·
composition·openapi(#N 승격 4) + response-schema(계약) + context-isolation
(다규칙 대형) — 중재 V18 확정. 실행은 hermetic 임시 비-git 사본(fixture_matrix
쌍의 red 축·checker_registry argv — 단일 출처 import).

EXPECTED_SHA 갱신 규율: stdout 변경 커밋에서 `--emit-expected` 로 갱신하되
검사기별 사유를 커밋 메시지에 전건 기록한다(무사유 일괄 갱신 금지).

사용: python3 workspace/tools/construct_drift_report.py
        [--emit-expected] [--emit-report]
exit 0 = 8종 전수 일치 / exit 2 = 불일치 / exit 1 = 재료 결손.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
S: Path = ROOT / "dddjango" / "scripts"
F: Path = ROOT / "workspace" / "eval" / "fixtures"
REPORT: Path = ROOT / "workspace" / "eval" / "ab" / "T2-construct-drift.md"

sys.path.insert(0, str(S))
sys.path.insert(0, str(ROOT / "workspace" / "tools"))
from checker_registry import REGISTRY, checker_argv  # noqa: E402
from fixture_matrix import AUTO_PAIRS, PLAIN_PAIRS  # noqa: E402

_RED: "dict[str, str]" = {"check-layer-skeleton.py": "skeleton/bad_legacy_flat"}
_RED.update({s: f"{fx}/bad_rules" for s, fx in PLAIN_PAIRS})
_RED.update({s: f"{fx}/bad_rules" for s, fx in AUTO_PAIRS})
_AUTO: "dict[str, bool]" = dict(REGISTRY)

# 대표 8종 → 이행 직전 봉인 커밋(그 검사기의 T2-1 보강 stdout 변경 커밋의 부모 —
# 문면 무변인 domain-model 은 3단계 개시 직전 = 2단계 완료 커밋으로 봉인).
SEALED: "dict[str, str]" = {
    "check-domain-model.py": "f164dd9",           # 문면 무변 — 3단계 개시 직전
    "check-common-container.py": "e245b1e",       # 계약 레인(3a68fe3) 직전
    "check-api-error-controller-contract.py": "77691d8",  # ⑤(c13d08e) 직전
    "check-error-centralization.py": "1e887e3",   # ②(5fbe8dd) 직전
    "check-composition-root.py": "faea9d3",       # ④(77691d8) 직전 — Y#5 오봉인 교정
    "check-openapi-error-declaration.py": "ee62c5c",      # ③(36bd09c) 직전 — Y#5 오봉인 교정
    "check-response-schema-bypass.py": "f164dd9",  # ①(ee62c5c) 직전
    "check-context-isolation.py": "36bd09c",      # #117 보강(1e887e3) 직전
}

# 신판 기본 red 레인 stdout sha256 (--emit-expected 재생성). domain-model·
# common-container 는 findings_smoke.BASELINE_SHA 와 동일값(교차 골든 — 2026-08-20 실측).
EXPECTED_SHA: "dict[str, str]" = {
    # 2026-08-25 재실측 — #543 저널 carve-out 경계 픽스처 +2(findings_smoke 와 동일 사유)
    "check-domain-model.py": "a5569b02e7847c7d375cbe44e9d9efc83d6c4e22a093388d9e414ddad10a1f3e",
    "check-common-container.py": "5ce9427209a475032bf19b5cf8f16d356e6e976f2119afe1639159cc8afd23fc",
    "check-api-error-controller-contract.py": "b883cb584e61d5b18ab527aebf9d4536a15b5519d49ece049e0f273298dcf1df",
    "check-error-centralization.py": "5d21b130e5a23bc5c5610ad3ebe29e880e526cd2338ff2377f00cb36294ff191",
    "check-composition-root.py": "650cdb87ee229acfe53415f5ef92da02995cec8bb865a0fb42d2a986a1f0bceb",
    "check-openapi-error-declaration.py": "eef4b45829694c5e65eb0cd3c5efacddf58e3f3669e0c291d2730190111c3e34",
    "check-response-schema-bypass.py": "b1a77bebb4272f9eb817feb63f31b6715d52da9d0ad312a2f02d744717428793",
    "check-context-isolation.py": "4906139cf24a4bcd1c037e3a53f331c7d80afab78adf5475f16b425b0173202d",
}

CHECKER_TIMEOUT_S: int = 300


def _run(scripts_dir: Path, script: str, fixture: Path) -> "tuple[int, str]":
    with tempfile.TemporaryDirectory() as td:
        fx = Path(td) / "fixture"
        shutil.copytree(fixture, fx)
        env = dict(os.environ)
        env.pop("DJR_FINDINGS_JSON", None)  # 사용자 레코드 파일 오염 방지(S#7)
        if scripts_dir == S:
            argv = checker_argv(sys.executable, script, str(fx), _AUTO[script])
        else:
            argv = [sys.executable, str(scripts_dir / script), str(fx)]
            if _AUTO[script]:
                argv += ["--error-profile", "auto"]
        proc = subprocess.run(argv, capture_output=True, text=True, cwd=str(ROOT),
                              env=env, timeout=CHECKER_TIMEOUT_S)
        return proc.returncode, proc.stdout


def _extract_old(commit: str, dest: Path) -> Path:
    """봉인 커밋의 dddjango/scripts 전체를 추출(구판 검사기는 구판 공용 모듈에 의존)."""
    out = dest / commit
    out.mkdir(parents=True)
    proc = subprocess.run(["git", "-C", str(ROOT), "archive", commit, "dddjango/scripts"],
                          capture_output=True)
    if proc.returncode != 0:
        print(f"재료 결손: git archive {commit} 실패 — {proc.stderr.decode()[:200]}",
              file=sys.stderr)
        raise SystemExit(1)
    subprocess.run(["tar", "-x", "-C", str(out)], input=proc.stdout, check=True)
    return out / "dddjango" / "scripts"


def _validate_sealed() -> None:
    """오봉인 방지(혼성 패널 Y#5 — 변경 커밋의 자손으로 봉인하면 자기 비교가 된다):
    봉인 커밋의 스크립트 blob 이 HEAD 와 동일하면 그 diff 는 무의미 — 즉사."""
    for script, commit in SEALED.items():
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "diff", "--quiet", commit, "HEAD", "--",
             f"dddjango/scripts/{script}"], capture_output=True)
        if proc.returncode == 0:
            print(f"재료 결손: SEALED[{script}]={commit} 오봉인 — 봉인 시점과 HEAD 의 "
                  f"스크립트가 동일(자기 비교). 변경 커밋의 부모로 재봉인하라", file=sys.stderr)
            raise SystemExit(1)


def measure() -> "dict[str, tuple[int, str, str]]":
    _validate_sealed()
    got: "dict[str, tuple[int, str, str]]" = {}
    for script in SEALED:
        fixture = F / _RED[script]
        if not fixture.is_dir():
            print(f"재료 결손: fixture {fixture} 없음", file=sys.stderr)
            raise SystemExit(1)
        code, out = _run(S, script, fixture)
        got[script] = (code, hashlib.sha256(out.encode("utf-8")).hexdigest(), out)
    return got


def emit_report(got: "dict[str, tuple[int, str, str]]") -> None:
    import difflib
    lines: "list[str]" = [
        "# T2 construct drift 리포트 — 대표 8종 구판(이행 직전) ↔ 신판 stdout (D11·T9)",
        "",
        "> 생성: `python3 workspace/tools/construct_drift_report.py --emit-report`(수기 편집 금지 — 재생성으로만 갱신).",
        "> 구판 = 검사기별 «이행 직전» 봉인 커밋(아래 표)·신판 = 생성 시점 워킹트리. 기본 red 레인 한정",
        "> (위험 레인 diff 는 각 이행 커밋 메시지가 소유). 의도 변경 열거표(포매터 계약 v2 §2)의 기계 실측 대응물.",
        "",
        "## 이관 고지 — 설치본 빚 목록(--legacy-debt-file)",
        "",
        "debt 매칭은 `[#N]` 태그 + 부분문자열이다(`anchor_diff.debt_match`). B형 콜론 정형화로",
        "`…:{lineno} {msg}` → `…:{lineno}: {msg}` 가 된 라인에 대해, **부분문자열이 lineno-msg 경계를",
        "가로지르는 빚 엔트리만** 매치가 깨진다(msg 내부·경로 내부 부분문자열은 무사). 설치본",
        "프로젝트의 빚 파일은 해당 엔트리에 콜론을 삽입해 개정한다. 저장소 내 실물 빚 파일 0건·",
        "테스트 자산(스모크 합성 빚)은 신판 기준 상시 green(2026-08-20 실측).",
        "",
        "## 검사기별 diff",
        "",
    ]
    with tempfile.TemporaryDirectory() as td:
        cache: "dict[str, Path]" = {}
        for script in sorted(SEALED):
            commit = SEALED[script]
            if commit not in cache:
                cache[commit] = _extract_old(commit, Path(td))
            old_code, old_out = _run(cache[commit], script, F / _RED[script])
            new_code, _sha, new_out = got[script]
            diff = list(difflib.unified_diff(
                old_out.splitlines(), new_out.splitlines(),
                fromfile=f"{script}@{commit}", tofile=f"{script}@신판", lineterm="", n=0))
            lines.append(f"### {script} — 구판 `{commit}` (exit {old_code}→{new_code})")
            lines.append("")
            if not diff:
                lines.append("stdout **byte 무변**.")
            else:
                changed = sum(1 for d in diff if d[:1] in "+-" and d[:3] not in ("+++", "---"))
                lines.append(f"변경 {changed}행:")
                lines.append("")
                lines.append("```diff")
                lines.extend(diff)
                lines.append("```")
            lines.append("")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"리포트 생성: {REPORT.relative_to(ROOT)}")


def main(argv: "list[str]") -> int:
    got = measure()
    bad_exit = [s for s, (code, _h, _o) in got.items() if code != 2]
    if bad_exit:
        print(f"거부: red 레인 exit 2 아님 — {sorted(bad_exit)} (결함을 골든으로 세탁할 수 없다)",
              file=sys.stderr)
        return 1
    if "--emit-expected" in argv:
        print('EXPECTED_SHA: "dict[str, str]" = {')
        for script in SEALED:
            print(f'    "{script}": "{got[script][1]}",')
        print("}")
        return 0
    if "--emit-report" in argv:
        emit_report(got)
        return 0
    mismatch = 0
    for script in SEALED:
        code, sha, _out = got[script]
        ok = sha == EXPECTED_SHA[script]
        if not ok:
            mismatch += 1
        print(f"| `{script}` | exit {code} | {sha[:16]} | {'✓' if ok else '✗ 기대 ' + EXPECTED_SHA[script][:16]} |")
    print(f"대표 8종 byte 골든 · 일치 {8 - mismatch} · 불일치 {mismatch}")
    return 0 if mismatch == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
