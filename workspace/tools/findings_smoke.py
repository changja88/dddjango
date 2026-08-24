#!/usr/bin/env python3
"""findings 스모크 — 공용 구조화 출력 모듈(findings/0)의 계약을 «내용 단언»으로 고정한다.

T0 계획 B2의 «내용 단언 하네스» 실물(동결 T0 완료 기준 «재료 재사용+내용 단언 하네스
신설»의 이행): fixture_matrix 의 exit 단언과 달리, 재저작 대표 2종을 자기 fixture 레인
red 재료의 «임시 디렉터리 사본»(원본 불변)으로 실행해 두 채널을 대조한다.

  ㉠ 라인 채널 하위 호환 — stdout 이 «개작 전 실측»(아래 SHA-256 고정)과 byte 동일하고,
     DJR_FINDINGS_JSON 유/무와 무관하게 같다(추가 채널의 stdout 오염 0 증명).
     기준 해시는 2026-08-19 개작 «직전» 검사기의 같은 fixture 실측 stdout 이다 —
     검사기·fixture 를 의도 변경하면 그 실측으로 이 상수를 재기록한다(골든 관례).
  ㉡ 구조화 레코드 내용 — schema·rule·file·symbol·severity·checker 필드를 기대값과
     대조하고, 전 레코드를 라인 채널로 역재구성해 stdout 과 1:1 대응(문면 동일)을 확인.
  ㉢ 채널 격리 — 환경변수 미지정이면 레코드 파일이 생기지 않고, green fixture 에선
     지정해도 레코드 0(파일 미생성)이다.

케이스:
  DM-red   domain_model/bad_rules × check-domain-model(규약 준수군 — rule "#N")
  CC-red   common_container/bad_rules × check-common-container(선행 계약 — rule=null+contract_ref)
  DM-green domain_model/good — exit 0 · stdout 0 · 레코드 0
  CC-green common_container/good — exit 0 · stdout 0 · 레코드 0

사용: python3 workspace/tools/findings_smoke.py
exit 0 = 전 케이스 일치 / exit 1 = 불일치 또는 재료 결손.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
SCRIPTS: Path = ROOT / "dddjango" / "scripts"
FIXTURES: Path = ROOT / "workspace" / "eval" / "fixtures"

# 개작 «직전» 실측 stdout 의 SHA-256(2026-08-19 · python3.9/3.14 동일 실측) — ㉠ 의 기준.
BASELINE_SHA: "dict[str, str]" = {
    # 2026-08-25 재실측 — #543 저널 carve-out 경계 픽스처 +2(no-op mark·일반 관용구 흉내)
    "domain_model/bad_rules": "a5569b02e7847c7d375cbe44e9d9efc83d6c4e22a093388d9e414ddad10a1f3e",
    # 계약 레인 이행(3a68fe3)의 의도 변경 열거표 등재분 반영 — `[컨테이너] {rel}/  (내용: …)`
    # → `- {rel}: 횡단 버킷이 application/ 안에 있다 (내용: …)`(계약 문법 정형화).
    "common_container/bad_rules": "5ce9427209a475032bf19b5cf8f16d356e6e976f2119afe1639159cc8afd23fc",
}

# DM-red 기대 레코드 표본(내용 단언 — 필드 그대로) · 계수 기대.
DM_EXPECT_VIOLATION: "dict[str, object]" = {
    "schema": "findings/0",
    "checker": "check-domain-model.py",
    "rule": "#264",
    "file": "application/orders/domain_layer/order/value_object/money.py:12",
    "symbol": None,
    "severity": "violation",
}
DM_EXPECT_INFO: "dict[str, object]" = {
    "schema": "findings/0",
    "checker": "check-domain-model.py",
    "rule": "#268",
    "file": "application/orders/domain_layer/order/value_object/money.py:7",
    "symbol": None,
    "severity": "info",
}
DM_COUNT_VIOLATION: int = 50  # 2026-08-25 +2 — #543 경계 픽스처
DM_COUNT_INFO: int = 13

# CC-red 기대(선행 계약 — rule=null + contract_ref).
CC_EXPECT_FILES: "set[str]" = {"application/framework", "application/common"}
CC_CONTRACT_MARK: str = "D38"
CC_COUNT: int = 2


def _run(script: str, target: Path, records: "Path | None") -> "tuple[int, str]":
    env: "dict[str, str]" = {k: v for k, v in os.environ.items() if k != "DJR_FINDINGS_JSON"}
    if records is not None:
        env["DJR_FINDINGS_JSON"] = str(records)
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), str(target)],
        capture_output=True, text=True, env=env,
    )
    return proc.returncode, proc.stdout


def _load_records(path: Path) -> "list[dict]":
    if not path.is_file():
        return []
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _matches(rec: "dict", expect: "dict[str, object]") -> bool:
    return all(rec.get(k) == v for k, v in expect.items())


def _line_of(rec: "dict") -> str:
    """레코드 → 라인 채널 문면 역재구성(규약 준수군 한정)."""
    mark: str = "ⓓ" if rec["severity"] == "info" else ""
    return f"[{mark}{rec['rule']}] {rec['file']}: {rec['message']}"


def _case_red_dm(td: Path, rows: "list[tuple[str, bool, str]]") -> None:
    fx: Path = td / "dm"
    shutil.copytree(FIXTURES / "domain_model" / "bad_rules", fx)
    rec_path: Path = td / "dm-records.jsonl"
    code_env, out_env = _run("check-domain-model.py", fx, rec_path)
    code_off, out_off = _run("check-domain-model.py", fx, None)
    sha: str = hashlib.sha256(out_env.encode("utf-8")).hexdigest()
    rows.append(("DM-red exit 2 (env 유/무)", code_env == 2 and code_off == 2, f"{code_env}/{code_off}"))
    rows.append(("DM-red stdout=개작 전 실측(㉠)", sha == BASELINE_SHA["domain_model/bad_rules"], sha[:12]))
    rows.append(("DM-red stdout env 무영향(㉠)", out_env == out_off, "byte 동일" if out_env == out_off else "오염"))
    recs: "list[dict]" = _load_records(rec_path)
    vio: "list[dict]" = [r for r in recs if r["severity"] == "violation"]
    info: "list[dict]" = [r for r in recs if r["severity"] == "info"]
    rows.append(("DM-red 레코드 계수 50+13(㉡)",
                 len(vio) == DM_COUNT_VIOLATION and len(info) == DM_COUNT_INFO,
                 f"violation {len(vio)} · info {len(info)}"))
    rows.append(("DM-red 표본 violation 레코드(㉡)", any(_matches(r, DM_EXPECT_VIOLATION) for r in vio),
                 "#264 money.py:12"))
    rows.append(("DM-red 표본 info 레코드(㉡)", any(_matches(r, DM_EXPECT_INFO) for r in info),
                 "#268 money.py:7"))
    stdout_lines: "set[str]" = {ln.strip() for ln in out_env.splitlines()}
    round_trip: bool = bool(recs) and all(_line_of(r) in stdout_lines for r in recs)
    rows.append(("DM-red 라인↔레코드 1:1 재구성(㉡)", round_trip, f"{len(recs)}건 전수"))
    ids: "set[str]" = {r["record_id"] for r in recs}
    one_run: bool = len({r["run_id"] for r in recs}) == 1 and len(ids) == len(recs)
    rows.append(("DM-red run_id 단일·record_id 유일", one_run, f"record_id {len(ids)}"))
    rows.append(("DM-red schema 전수 findings/0", all(r["schema"] == "findings/0" for r in recs), ""))


def _case_red_cc(td: Path, rows: "list[tuple[str, bool, str]]") -> None:
    fx: Path = td / "cc"
    shutil.copytree(FIXTURES / "common_container" / "bad_rules", fx)
    rec_path: Path = td / "cc-records.jsonl"
    code_env, out_env = _run("check-common-container.py", fx, rec_path)
    code_off, out_off = _run("check-common-container.py", fx, None)
    sha: str = hashlib.sha256(out_env.encode("utf-8")).hexdigest()
    rows.append(("CC-red exit 2 (env 유/무)", code_env == 2 and code_off == 2, f"{code_env}/{code_off}"))
    rows.append(("CC-red stdout=개작 전 실측(㉠)", sha == BASELINE_SHA["common_container/bad_rules"], sha[:12]))
    rows.append(("CC-red stdout env 무영향(㉠)", out_env == out_off, "byte 동일" if out_env == out_off else "오염"))
    recs: "list[dict]" = _load_records(rec_path)
    shape_ok: bool = (
        len(recs) == CC_COUNT
        and all(r["rule"] is None and r["sentinel"] is None for r in recs)
        and all(CC_CONTRACT_MARK in (r["contract_ref"] or "") for r in recs)
        and all(r["schema"] == "findings/0" and r["severity"] == "violation"
                and r["checker"] == "check-common-container.py" and r["symbol"] is None for r in recs)
        and {r["file"] for r in recs} == CC_EXPECT_FILES
    )
    rows.append(("CC-red rule=null+contract_ref 2건(㉡)", shape_ok,
                 ", ".join(sorted(r["file"] for r in recs))))


def _case_green(td: Path, name: str, script: str, fixture: str,
                rows: "list[tuple[str, bool, str]]") -> None:
    fx: Path = td / name
    shutil.copytree(FIXTURES / fixture / "good", fx)
    rec_path: Path = td / f"{name}-records.jsonl"
    code, out = _run(script, fx, rec_path)
    ok: bool = code == 0 and out == "" and not rec_path.exists()
    rows.append((f"{name} green — exit 0·stdout 0·레코드 0(㉢)", ok, f"exit {code}"))


def main() -> int:
    materials: "list[Path]" = [
        SCRIPTS / "check-domain-model.py", SCRIPTS / "check-common-container.py",
        SCRIPTS / "findings.py",
        FIXTURES / "domain_model" / "bad_rules", FIXTURES / "common_container" / "bad_rules",
        FIXTURES / "domain_model" / "good", FIXTURES / "common_container" / "good",
    ]
    missing: "list[Path]" = [p for p in materials if not p.exists()]
    if missing:
        print(f"재료 결손: {', '.join(str(p) for p in missing)}", file=sys.stderr)
        return 1

    rows: "list[tuple[str, bool, str]]" = []
    with tempfile.TemporaryDirectory() as td_s:
        td: Path = Path(td_s)
        _case_red_dm(td, rows)
        _case_red_cc(td, rows)
        _case_green(td, "dm-good", "check-domain-model.py", "domain_model", rows)
        _case_green(td, "cc-good", "check-common-container.py", "common_container", rows)

    print("| 단언 | 판정 | 비고 |")
    print("|---|---|---|")
    bad: int = 0
    for name, ok, note in rows:
        if not ok:
            bad += 1
        print(f"| {name} | {'✓' if ok else '✗ 불일치'} | {note} |")
    print(f"단언 {len(rows)} · 일치 {len(rows) - bad} · 불일치 {bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
