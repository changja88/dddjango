#!/usr/bin/env python3
"""registry_gate 스모크 — 판정 차분 게이트의 계약을 «공격 재현»으로 고정한다.

fixture_matrix 밖에 두는 이유: 그 레인의 hermetic 원칙은 «비-git 임시 사본»인데
이 게이트는 git(앵커)이 재료라 원칙이 상반된다 — 한 도구에 두 원칙을 섞지 않는다.
release 게이트 [2/7] 검증 세트에 등록되어 함께 돈다(Makefile).

케이스(2026-08-12 적대 리뷰 Goodhart·회귀 렌즈 재현 실측의 고정):
  V  공허 차분(앵커=HEAD·clean)          → exit 1 (커밋-후-게이트 우회 차단)
  A  귀속 red(working 신규 위반)          → exit 2 + 그 위반이 귀속 절에
  B  legacy-only(앵커에 이미 있던 위반)    → exit 0 + 잔존 보고(침묵 금지)
  C  A1 공격(위반을 «선커밋»하고 무해 변경) → exit 2 (경로-매칭 게이트가 뚫리던 자리)
  D  A2 공격(골격 칸 «삭제» — 부재 위반)   → exit 2 (부재는 변경 집합에 경로가 없다)
  E  빚 채널(승인 목록 매칭)              → exit 0 + «이관 빚» 절 보고
  U  usage 오류(알 수 없는 flag)          → exit 1 (F3 — 문면 계약 1=usage·2=위반,
                                            argparse 기본 exit 2 로 새지 않는다)

provenance 차분(승인 유입 채널 · 수리 배치 2 Part 2 · 2026-09-03) — 골격 «A(앵커) → lane 커밋 →
main 위반 커밋 → lane 에서 `git merge --no-ff main`(M) → 판정». 고정 GIT_*_DATE(결정적 SHA).
  P0   flag 없음 → 현행 판형(귀속 3·exit 2) + 새 절 제목 3종 부재 + flag 유/무의 legacy·해소 절
       동일·(귀속∪승인 유입) 집합 동일. P0′ 수리 전 사본(Part 1 tip `34c74a6` 의 scripts 트리)과
       정규화(툴체인 행 전체·sidecar ts/run_id/record_id/file_raw 마스킹) 출력·sidecar byte 동일
  P1   목록={M}                            → 유입 3(파일)·귀속 0·exit 0·sidecar attributed_lines=[]
  P2   머지 뒤 lane 이 위반 파일 수정(커밋) → 귀속 3·`레인 커밋 수정`·exit 2 / P2w 미커밋 → `worktree 수정 중`
  P2′  양쪽 수정 → 충돌 해소 M             → 귀속 유지·`충돌 해소분(M≠M^2)`
  P3   ⓐ 빈 목록 → `미승인 머지 경유 M`·exit 2 ⓑ 비머지 SHA → exit 1 ⓒ 사슬 밖 → exit 1
       ⓓ 앵커 이전 머지 → «판정 불참»·귀속 3
  P4   앵커 `framework/redis/redis_cache.py`(`"promotion"` 리터럴) + main 이 `application/promotion/`
       (orders BC 사본 — 완전 BC 캘리브레이션) → M   → `#416` = 승인 유입(상호작용)·귀속 0·exit 0
  P4′  P4 에서 목록 비움                    → 귀속·`상호작용 미증명`·exit 2
  P5   kkebi 형 — main 직접 커밋 X 뒤 lane 분기·M → 귀속 3·`비머지 커밋 경유 X`·진단 «비머지 1건»·exit 2
  P6   이중 원인 — lane 이 promotion BC 신설·main 이 리터럴 파일 → M 승인 → F1 통과·L 실패 →
       `유입 증명 실패(이중 원인)`·exit 2
  P7   빚+유입 공존(P1 + `#95 schema_smoke`)  → #95 빚 절·나머지 2 유입(빚 우선)·exit 0
  P8   앵커 비조상(무관 가지)                → «주의: 앵커 … 조상이 아니다» 1행·exit 현행(2)
  P9   역방향 합성 머지(main←lane) 등재      → exit 1 «사슬 밖» — **HEAD=lane 한정**(main←lane 머지는 lane 의
       first-parent 사슬에 없다) / P9′ 앵커가 ^2 경유 → exit 1 «first-parent 사슬 밖». 발주자가 합성 머지를 레인
       사슬에 올린 잔여 경로는 exit 1 이 아니라 P12 진단+custody 다.
  P10  M^1 에 SyntaxError                   → `측정 무효(M^1)` 귀속 유지·exit 2
  P11  M^1 스냅숏 실패(git archive 불능 — PATH shim) → `측정 무효(스냅숏 실패) — M` 귀속 3·exit 2·traceback 0·
       판정 행 보존·진단 절에 git 오류(5단계 리뷰 P2 M-2)
  P12  합성 머지 — lane 이 임시 가지를 머지하고 그 가지를 지움(^2 를 포함하는 ref 가 HEAD 브랜치뿐) → 머지 표에
       «역방향/합성 머지 의심» 진단 1행·exit 무변(유입 3·exit 0)(P2 M-1) / P12r 같은 상태에 remote-tracking
       `refs/remotes/origin/lane`·태그를 얹어도 진단 1행(HEAD 브랜치 자신으로 계수 — 6단계 재검 MAJOR-2)

병렬 실행(속도 개선 C1⑵ · 2026-10-01) — 옛 직렬 게이트(`86fc3c24` 의 registry_gate.py 를 현행 검사기 트리에
덮어쓴 사본)와 새 게이트를 같은 픽스처에서 돌려 exit·stdout(툴체인 행 마스킹)·stderr·introduced·contract
(휘발 필드 마스킹)를 대조한다. 새 게이트 실행마다 `$TMPDIR` 를 빈 전용 폴더로 줘 임시 폴더 누수를 센다.
  R1   레코드 수백 건 저장소(good_bc + bad_rules 15종 — 절반 앵커·절반 작업 트리) · 워커 1·3·8·기본 → 옛과 동일·누수 0
  R2   REGISTRY 0번 검사기 지연 주입(완료 순서 뒤집힘) · 워커 8 → 옛과 동일(병합은 REGISTRY 순서)
  R3   검사기가 sink 에 깨진 바이트 줄 → 옛·새 exit 2 · 동일(조각은 바이트로 잇는다)
  R4   검사기 stdout 비-UTF-8(게이트 작업 예외) → 옛·새 traceback 1 · 같은 예외 줄 · exit 1 · 누수 0
  R5   검사기 실행 시 예외(crash) → 옛·새 exit 2 · 합성 fail-closed 귀속 동일
  R6   `DJR_REGISTRY_WORKERS=0`(양의 정수 아님) → stderr 주의 1행 · 자동 워커 · 나머지 옛과 동일
  (게이트에는 검사기별 timeout 이 없다 — 옛·새 같다. «느린 검사기»는 R2 지연 주입이 덮는다.)
  유지 규칙: 게이트 출력 판형(절·진단 행)을 바꾸는 개정은 같은 변경을 직렬 판형 사본(`_SERIAL_GATE_COMMIT` 게이트 +
  그 변경)에도 적용해 이 대조를 유지하거나, R 을 `DJR_REGISTRY_WORKERS=1` 대조로 낮추는 결정을 커밋 메시지에 적는다
  (기준을 병렬 이후 커밋으로 올리면 «직렬 대조»라는 뜻이 사라진다).

사용: python3 registry_gate_smoke.py
exit 0 = 전 케이스 일치 / exit 2 = 불일치 / exit 1 = 재료 결손.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import contextlib
import io
from unittest.mock import patch
from pathlib import Path
from types import ModuleType
from typing import Callable
from anchor_diff_smoke import ApprovedInflowRepo

ROOT: Path = Path(__file__).resolve().parents[2]
GATE: Path = ROOT / "dddjango" / "scripts" / "registry_gate.py"
BASE_FIXTURE: Path = ROOT / "workspace" / "eval" / "fixtures" / "skeleton" / "good_bc"

_GIT_ID: "list[str]" = ["-c", "user.email=smoke@dddjango", "-c", "user.name=smoke"]
# 결정적 SHA — 모든 커밋의 저자·커미터 시각 고정(provenance 케이스의 사슬·머지 SHA 가 런마다 같다).
_GIT_DATE: str = "2026-09-03T00:00:00+0900"
# P0′ 수리 전 사본 — 수리 배치 2 Part 1 tip(provenance 채널 도입 직전 실행기 트리).
_PRE_REPAIR_COMMIT: str = "34c74a6"

# 위반 재료: driving 잎이 애그리거트를 import(#96 계열 — 앵커 이후 «신규»로 심는다)
_VIOLATION_REL: str = "application/orders/driving_layer/api/order/schema/schema_smoke.py"
_VIOLATION_SRC: str = "from application.orders.domain_layer.order.order import Order\n\n_N: str = Order.__name__\n"



def _scrubbed_env() -> "dict[str, str]":
    """검사기 하위 실행 env — 사용자 DJR_FINDINGS_JSON 오염 차단(T2-1 적대 검증 레인 S 7번 잔여)."""
    env: "dict[str, str]" = dict(os.environ)
    env.pop("DJR_FINDINGS_JSON", None)
    return env

def _git(repo: Path, *args: str) -> "subprocess.CompletedProcess[str]":
    env: "dict[str, str]" = dict(os.environ, GIT_AUTHOR_DATE=_GIT_DATE, GIT_COMMITTER_DATE=_GIT_DATE)
    return subprocess.run(["git", "-C", str(repo), *_GIT_ID, *args], capture_output=True, text=True, env=env)


def _make_repo(td: Path, name: str) -> "tuple[Path, str]":
    """good_bc 사본으로 git repo 를 만들고 앵커 커밋 해시를 돌려준다."""
    repo: Path = td / name
    shutil.copytree(BASE_FIXTURE, repo)
    for step in (("init", "-q"), ("add", "-A"), ("commit", "-q", "-m", "anchor")):
        proc: "subprocess.CompletedProcess[str]" = _git(repo, *step)
        if proc.returncode != 0:
            raise RuntimeError(f"git {step[0]} 실패: {proc.stderr.strip()}")
    return repo, _git(repo, "rev-parse", "HEAD").stdout.strip()


def _gate(repo: Path, anchor: str, extra: "list[str] | None" = None,
          gate: "Path | None" = None) -> "tuple[int, str]":
    proc: "subprocess.CompletedProcess[str]" = subprocess.run(
        [sys.executable, str(gate or GATE), str(repo), "--anchor", anchor] + (extra or []),
        capture_output=True, text=True, env=_scrubbed_env(),
    )
    return proc.returncode, proc.stdout + proc.stderr


# ── provenance 케이스 재료 ─────────────────────────────────────────────────────────

def _head(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _commit_all(repo: Path, msg: str) -> str:
    _git(repo, "add", "-A")
    proc: "subprocess.CompletedProcess[str]" = _git(repo, "commit", "-q", "--allow-empty", "-m", msg)
    if proc.returncode != 0:
        raise RuntimeError(f"git commit 실패: {proc.stderr.strip()}")
    return _head(repo)


def _write(repo: Path, rel: str, text: str) -> None:
    (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / rel).write_text(text, encoding="utf-8")


def _plant_violation(repo: Path) -> None:
    _write(repo, _VIOLATION_REL, _VIOLATION_SRC)


def _make_promotion_bc(repo: Path) -> None:
    """orders BC 사본 → `application/promotion/`(완전 BC 캘리브레이션 — good_bc 와 같은 잔존 수준).

    이름 치환: orders→promotion · order→coupon(애그리거트). 사본이 내는 진단은 orders 가 이미 내는
    legacy 4건(#107·#329·#219·#635 — 빈 파일 골격)의 경로 복사본뿐이다(P4 캘리브레이션 실측).
    """
    src: Path = repo / "application" / "orders"
    dst: Path = repo / "application" / "promotion"
    shutil.copytree(src, dst)
    subs: "list[tuple[str, str]]" = [("orders", "promotion"), ("Orders", "Promotion"),
                                     ("order", "coupon"), ("Order", "Coupon")]
    for path in sorted(dst.rglob("*"), key=lambda x: -len(str(x))):
        if path.is_file():
            text: str = path.read_text(encoding="utf-8")
            for a, b in subs:
                text = text.replace(a, b)
            path.write_text(text, encoding="utf-8")
    for path in sorted(dst.rglob("*"), key=lambda x: -len(str(x))):
        name: str = path.name
        for a, b in subs:
            name = name.replace(a, b)
        if name != path.name:
            path.rename(path.with_name(name))


_REDIS_REL: str = "framework/redis/redis_cache.py"
_REDIS_SRC: str = 'import redis\n\nactivation_type: str = "promotion"\n_R: str = redis.__name__\n'


def _plant_redis(repo: Path, src: str = _REDIS_SRC) -> None:
    _write(repo, "framework/__init__.py", "")
    _write(repo, "framework/redis/__init__.py", "")
    _write(repo, _REDIS_REL, src)


def _lane_merge_repo(td: Path, name: str, main_step, lane_step=None,
                     anchor_step=None) -> "tuple[Path, str, str]":
    """골격 «A(앵커) → lane 커밋 → main 변경 커밋 → lane 에서 `git merge --no-ff main`(M)».

    반환 (repo, 앵커 SHA, M SHA). HEAD = lane(M). anchor_step 은 앵커 커밋 «안»에 넣을 재료.
    """
    repo, anchor = _make_repo(td, name)
    if anchor_step is not None:
        anchor_step(repo)
        anchor = _commit_all(repo, "anchor+")
    _git(repo, "checkout", "-q", "-b", "lane")
    if lane_step is None:
        _write(repo, "lane_note.md", "lane work\n")
    else:
        lane_step(repo)
    _commit_all(repo, "lane work")
    _git(repo, "checkout", "-q", "main")
    main_step(repo)
    _commit_all(repo, "main change")
    _git(repo, "checkout", "-q", "lane")
    proc: "subprocess.CompletedProcess[str]" = _git(repo, "merge", "-q", "--no-ff", "-m", "M merge main", "main")
    if proc.returncode != 0:
        raise RuntimeError(f"git merge 실패: {proc.stderr.strip()} {proc.stdout.strip()}")
    return repo, anchor, _head(repo)


def _approved(td: Path, name: str, *shas: str) -> Path:
    path: Path = td / f"{name}-approved.txt"
    path.write_text("// 발주자 승인 머지 목록(스모크)\n" + "".join(f"{sha} 승인 메모\n" for sha in shas),
                    encoding="utf-8")
    return path


def _section(out: str, title: str) -> str:
    """`== <title> …` 절 본문(다음 `==` 절 전까지)."""
    m: "re.Match[str] | None" = re.search(
        rf"^== {re.escape(title)}.*?$\n(.*?)(?=^== |^판정:|^귀속 레코드|\Z)", out, re.S | re.M)
    return m.group(1) if m else ""


def _lines_of(out: str, title: str) -> "set[str]":
    return {l.strip() for l in _section(out, title).splitlines()
            if l.startswith("  ") and " :: " in l and not l.strip().startswith("[M ")}


def _mask(out: str) -> str:
    """P0 정규화 — 툴체인 행 전체(digest·경로)와 sidecar 경로 행(tempdir)만 마스킹한다."""
    masked: "list[str]" = []
    for l in out.splitlines():
        if l.startswith("툴체인:"):
            masked.append("툴체인: <masked>")
        elif l.startswith("귀속 레코드 sidecar → "):
            masked.append("귀속 레코드 sidecar → <masked>" + l.split(" (", 1)[-1])
        else:
            masked.append(l)
    return "\n".join(masked)


def _mask_sidecar(path: Path) -> "dict | None":
    if not path.is_file():
        return None
    payload: dict = json.loads(path.read_text(encoding="utf-8"))
    for key in ("experiment_run_id",):
        payload.pop(key, None)
    for rec in payload.get("records", []) + (payload.get("candidate_records") or []):
        for key in ("ts", "run_id", "record_id", "file_raw", "experiment_run_id"):
            rec.pop(key, None)
    return payload


def _gate_copy(td: Path, name: str, commit: "str | None" = None) -> "Path | None":
    """**현행 검사기 트리** 사본의 registry_gate.py — `commit` 이 있으면 게이트만 그 커밋 판으로 덮는다.

    측정 대상은 게이트 불변(귀속·정규화·출력 판형)뿐이다 — 검사기 트리는 현행을 쓴다(검사기 규칙이
    바뀌면(예: 2026-09-04 #219/#635 의 골격 파일 건너뜀) 옛 검사기의 발화가 diff 를 오염시키므로).
    옛 게이트의 import 계약(findings·anchor_diff)이 현행 모듈과 맞아야 한다 — 어긋나면 스모크가 그 사실로 red 다.
    사본은 결함 주입(`_inject`)의 재료이기도 하다 — 원본 scripts 트리는 건드리지 않는다."""
    dest: Path = td / name
    shutil.copytree(GATE.parent, dest / "dddjango" / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    gate: Path = dest / "dddjango" / "scripts" / "registry_gate.py"
    if commit is not None:
        old_gate: "subprocess.CompletedProcess[bytes]" = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"{commit}:dddjango/scripts/registry_gate.py"],
            capture_output=True)
        if old_gate.returncode != 0:
            return None
        gate.write_bytes(old_gate.stdout)
    return gate


def _pre_repair_gate(td: Path) -> "Path | None":
    """수리 전 «게이트»(`_PRE_REPAIR_COMMIT` 의 registry_gate.py)를 현행 검사기 트리 위에 덮어쓴 사본(P0′)."""
    return _gate_copy(td, "pre-repair", _PRE_REPAIR_COMMIT)


# ── R — 병렬 실행(속도 개선 C1⑵) 옛 게이트 직접 대조 ─────────────────────────────────────
# 옛(직렬) 게이트 = `_SERIAL_GATE_COMMIT` 의 registry_gate.py 를 현행 검사기 트리에 덮어쓴 사본(P0′ 판형).
# 새 게이트 자기 설정끼리(워커 1 vs 기본)만 대조하면 병합 결함이 양쪽에 같이 숨는다 — 옛 코드와 직접 잰다.

_SERIAL_GATE_COMMIT: str = "86fc3c24"
# F4-89 바로 앞 배포판(dddjango 2.21.2) — U2 «옛 출력과 같음» 대조의 옛 게이트. HEAD 로 잡으면 커밋 뒤 새 판 자신이 된다.
_RELEASED_2212_COMMIT: str = "c4e40615"
_FIXTURES: Path = ROOT / "workspace" / "eval" / "fixtures"
# 레코드가 여러 검사기에서 수백 건 나도록 겹치는 bad_rules — 앞 절반은 앵커에 커밋(legacy), 뒤 절반은 작업 트리.
_MANY_BADS: "tuple[str, ...]" = (
    "domain_model", "naming", "business_vocabulary", "context_isolation", "port_adapter_pairing",
    "transaction_boundary", "db_table", "event_publish", "mechanism_ownership", "usecase_dto",
    "public_surface", "response_schema_bypass", "choices_literal", "broker_contract", "missable_entrance",
)


def _add_bad_rules(repo: Path, bad: str) -> None:
    """재료 하나를 `fx_<재료>/` 에 두고 그 BC 는 뿌리 `application/<재료>_<bc>` 로 옮긴다 — BC 마다 도는 검사기는 뿌리
    `application/` 만 BC 로 고른다(저장소 전체를 훑는 검사기 몫은 `fx_<재료>/` 그대로)."""
    shutil.copytree(_FIXTURES / bad / "bad_rules", repo / f"fx_{bad}")
    for bc in sorted((repo / f"fx_{bad}" / "application").iterdir()):
        if bc.is_dir():
            shutil.move(str(bc), str(repo / "application" / f"{bad}_{bc.name}"))


def _many_records_repo(td: Path, name: str) -> "tuple[Path, str]":
    repo, _good = _make_repo(td, name)
    split: int = len(_MANY_BADS) // 2
    for bad in _MANY_BADS[:split]:
        _add_bad_rules(repo, bad)
    anchor: str = _commit_all(repo, "anchor + legacy half")
    for bad in _MANY_BADS[split:]:
        _add_bad_rules(repo, bad)
    _plant_violation(repo)
    return repo, anchor


def _inject(gate: Path, checker: str, body: str) -> None:
    """사본의 검사기 `__main__` 블록 첫머리에 결함 코드를 심는다(옛·새 사본에 같은 주입)."""
    path: Path = gate.parent / checker
    text: str = path.read_text(encoding="utf-8")
    anchor: str = '\nif __name__ == "__main__":\n'
    if text.count(anchor) != 1:
        raise RuntimeError(f"주입 앵커 없음: {checker}")
    path.write_text(text.replace(anchor, anchor + "".join(f"    {line}\n" for line in body.splitlines())),
                    encoding="utf-8")


def _leaked(tmp: Path) -> "list[str]":
    """임시 폴더 누수 — `$TMPDIR` 바로 아래 항목(옛 판 꼴) + 임시 사본 뿌리 `dddjango/` 안 항목(뿌리 자체는 남는다)."""
    out: "list[str]" = sorted(p.name for p in tmp.iterdir() if p.name != "dddjango")
    root: Path = tmp / "dddjango"
    if root.is_dir() and not root.is_symlink():
        out += sorted("dddjango/" + p.name for p in root.iterdir())
    return out


def _par_run(gate: Path, repo: Path, anchor: str, td: Path, workers: "str | None",
             seed: "Callable[[Path], None] | None" = None) -> "dict[str, object]":
    """게이트 1회 — 사이드카는 고정 경로(출력의 경로 행이 런마다 같다) · `$TMPDIR` 는 빈 전용 폴더(누수 계수).
    `seed` 는 실행 전에 그 폴더를 채운다(끊긴 실행이 남긴 사본 흉내)."""
    tmp: Path = td / "par-tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir()
    if seed is not None:
        seed(tmp)
    intro: Path = td / "par-introduced.json"
    contract: Path = td / "par-contract.json"
    intro.unlink(missing_ok=True)
    contract.unlink(missing_ok=True)
    env: "dict[str, str]" = _scrubbed_env()
    env.pop("DJR_REGISTRY_WORKERS", None)
    if workers is not None:
        env["DJR_REGISTRY_WORKERS"] = workers
    env["TMPDIR"] = str(tmp)
    proc: "subprocess.CompletedProcess[str]" = subprocess.run(
        [sys.executable, str(gate), str(repo), "--anchor", anchor,
         "--introduced-json", str(intro), "--contract-json", str(contract)],
        capture_output=True, text=True, env=env)
    return {"exit": proc.returncode, "stdout": _mask(proc.stdout), "stderr": proc.stderr,
            "introduced": _mask_sidecar(intro), "contract": _mask_sidecar(contract),
            "leaked": _leaked(tmp)}


def _same_output(a: "dict[str, object]", b: "dict[str, object]") -> bool:
    return all(a[key] == b[key] for key in ("exit", "stdout", "stderr", "introduced", "contract"))


def _last_line(text: object) -> str:
    """traceback 의 마지막 줄(예외 종류·메시지) — 프레임 경로는 옛·새가 달라 이 줄만 대조한다."""
    lines: "list[str]" = [line for line in str(text).splitlines() if line.strip()]
    return lines[-1] if lines else ""


def _parallel_rows(td: Path) -> "list[tuple[str, int, int, bool, str]]":
    """R1~R6 — 병렬 게이트가 옛 직렬 게이트와 byte 같은가(정상·완료 순서 뒤집힘·결함 주입 셋·워커 값 오류)."""
    rows: "list[tuple[str, int, int, bool, str]]" = []
    serial: "Path | None" = _gate_copy(td, "serial-gate", _SERIAL_GATE_COMMIT)
    if serial is None:
        raise RuntimeError(f"직렬 게이트 사본({_SERIAL_GATE_COMMIT}) 추출 실패")

    # R1 — 레코드 수백 건 저장소: 옛 1회 vs 새 워커 1 · 3 · 8 · 기본(빈 코어). 누수 0.
    repo, anchor = _many_records_repo(td, "par-many")
    ref: "dict[str, object]" = _par_run(serial, repo, anchor, td, None)
    n_records: int = len((ref["introduced"] or {}).get("records", []))  # type: ignore[union-attr]
    for workers in ("1", "3", "8", None):
        got: "dict[str, object]" = _par_run(GATE, repo, anchor, td, workers)
        rows.append((f"R1 옛 직렬 대조 · 워커 {workers or '기본'}", 2, int(got["exit"]),  # type: ignore[arg-type]
                     ref["exit"] == 2 and n_records >= 300 and _same_output(ref, got) and not got["leaked"],
                     f"stdout·stderr·introduced·contract 동일(레코드 {n_records}) · 임시 폴더 누수 0"))

    # R2 — 완료 순서 뒤집힘: REGISTRY 0번 검사기를 늦춰(지연 주입) 첫 작업이 늦게 끝나도 병합은 REGISTRY 순서.
    slow: "Path | None" = _gate_copy(td, "par-slow")
    assert slow is not None
    _inject(slow, "check-mechanism-ownership.py", "import time as _t\n_t.sleep(2)")
    got = _par_run(slow, repo, anchor, td, "8")
    rows.append(("R2 완료 순서 뒤집힘(첫 검사기 지연)", 2, int(got["exit"]),  # type: ignore[arg-type]
                 _same_output(ref, got), "지연 주입 사본 · 워커 8 — 옛 직렬과 byte 동일"))

    # 결함 주입 — 옛·새 사본에 같은 주입. R3·R5 는 작은 저장소(good_bc + 위반 1)로 충분하고, R4 는 예외가 올라올 때
    # 형제 작업이 아직 돌고 있어야 «정리와 경합»을 볼 수 있으므로 레코드 수백 건 저장소에서 돈다.
    small, small_anchor = _make_repo(td, "par-small")
    _plant_violation(small)
    injections: "list[tuple[str, str, str, int, bool, str]]" = [
        ("R3 깨진 sink 줄(바이트 병합)", "check-naming.py",
         "import os as _o\n_p = _o.environ.get('DJR_FINDINGS_JSON')\nif _p:\n"
         "    open(_p, 'ab').write(b'{\"schema\": \"findings/0\", \"bad\": \"\\xff\\xfe\"}\\n')",
         2, False, "옛·새 exit 2 · 판정·사이드카 동일(깨진 줄은 읽기에서 건너뜀)"),
        ("R4 작업 예외(stdout 비-UTF-8)", "check-mechanism-ownership.py",
         "import sys as _s\n_s.stdout.buffer.write(b'\\xff\\xfe broken\\n')\n_s.stdout.flush()",
         1, True, "옛·새 traceback 1 · 같은 예외 · exit 1 · 임시 폴더 누수 0"),
        ("R5 검사기 crash(실행 시 예외)", "check-naming.py", "raise RuntimeError('injected crash')",
         2, False, "옛·새 exit 2 · 합성 fail-closed 귀속 동일"),
    ]
    for name, checker, body, want, on_many, note in injections:
        tag: str = name.split()[0].lower()
        old_gate: "Path | None" = _gate_copy(td, f"{tag}-old", _SERIAL_GATE_COMMIT)
        new_gate: "Path | None" = _gate_copy(td, f"{tag}-new")
        assert old_gate is not None and new_gate is not None
        _inject(old_gate, checker, body)
        _inject(new_gate, checker, body)
        target, target_anchor = (repo, anchor) if on_many else (small, small_anchor)
        old_run: "dict[str, object]" = _par_run(old_gate, target, target_anchor, td, None)
        new_run: "dict[str, object]" = _par_run(new_gate, target, target_anchor, td, "8")
        if want == 1:
            ok: bool = (old_run["exit"] == 1 and str(old_run["stderr"]).count("Traceback") == 1
                        and str(new_run["stderr"]).count("Traceback") == 1
                        and "Directory not empty" not in str(new_run["stderr"])
                        and _last_line(old_run["stderr"]) == _last_line(new_run["stderr"])
                        and _last_line(new_run["stderr"]).startswith("UnicodeDecodeError")
                        and not old_run["leaked"] and not new_run["leaked"])
        else:
            ok = old_run["exit"] == want and _same_output(old_run, new_run) and not new_run["leaked"]
        rows.append((name, want, int(new_run["exit"]), ok, note))  # type: ignore[arg-type]

    # R6 — 워커 값 오류(`0`): 주의 1행 뒤 자동 워커로 같은 판정(옛 직렬과 stdout·사이드카 동일).
    small_ref: "dict[str, object]" = _par_run(serial, small, small_anchor, td, None)
    got = _par_run(GATE, small, small_anchor, td, "0")
    rows.append(("R6 워커 값 오류 → 자동", 2, int(got["exit"]),  # type: ignore[arg-type]
                 all(small_ref[k] == got[k] for k in ("exit", "stdout", "introduced", "contract"))
                 and "DJR_REGISTRY_WORKERS='0' 는 양의 정수가 아니다" in str(got["stderr"]),
                 "stderr 주의 1행 · 나머지 옛 직렬과 동일"))
    return rows



class IdempotencySnapshotRegression(unittest.TestCase):
    artifact = "application/orders/domain_layer/order/idempotency_record.py"
    scope = "멱등성 처리는 이번 요청에 명시되지 않았다.\n"
    approval = "G1 사용자 승인: 멱등성 도입 채택\n"
    checker = "check-idempotency-scope-creep.py"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="idempotency-snapshot-")
        self.addCleanup(self.temp.cleanup)
        self.td = Path(self.temp.name)
        self.repo, self.anchor = _make_repo(self.td, "repo")

    def direct(self):
        return subprocess.run([sys.executable, str(GATE.parent / self.checker), str(self.repo)],
                              capture_output=True, text=True, env=_scrubbed_env()).returncode

    def test_unrequested_untracked_artifact_fires_in_direct_checker_and_gate(self):
        _write(self.repo, ".dddjango/orders/scope.md", self.scope)
        self.anchor = _commit_all(self.repo, "scope")
        _write(self.repo, self.artifact, "")
        self.assertEqual(self.direct(), 2)
        code, out = _gate(self.repo, self.anchor)
        self.assertEqual(code, 2, out)
        self.assertRegex(out, rf"\| `{re.escape(self.checker)}` \| 0 \| 2 \|")

    def test_untracked_scope_and_approval_inputs_preserve_checker_decision(self):
        _write(self.repo, ".dddjango/orders/scope.md", self.scope)
        _write(self.repo, self.artifact, "")
        code, out = _gate(self.repo, self.anchor)
        self.assertEqual(code, 2, out)
        self.assertRegex(out, rf"\| `{re.escape(self.checker)}` \| 0 \| 2 \|")
        other_rows = [line for line in out.splitlines() if line.startswith("| `")
                      and self.checker not in line]
        for document in ("scope.md", "design-spec.md"):
            with self.subTest(document=document):
                _write(self.repo, ".dddjango/orders/" + document, self.scope + self.approval)
                self.assertEqual(self.direct(), 0)
                code, out = _gate(self.repo, self.anchor)
                self.assertRegex(out, rf"\| `{re.escape(self.checker)}` \| 0 \| 0 \|")
                self.assertNotIn(self.checker + " ::", out)
                self.assertEqual([line for line in out.splitlines() if line.startswith("| `")
                                  and self.checker not in line], other_rows)
                _write(self.repo, ".dddjango/orders/" + document, self.scope)

    def test_snapshot_copies_only_checker_documents_with_current_bytes(self):
        from pregate_fixture_run import _load_module
        sys.path.insert(0, str(GATE.parent))
        gate = _load_module(GATE, "idempotency_snapshot_gate")
        documents = {".dddjango/orders/scope.md": self.scope,
                     ".dddjango/orders/design-spec.md": self.approval,
                     ".dddjango/another/scope.md": "다른 범위\n"}
        for relative, content in documents.items():
            _write(self.repo, relative, content)
        for relative in (".codex/guard.py", ".env", ".dddjango/guard.py",
                         ".dddjango/orders/guard.py", ".dddjango/orders/nested/scope.md",
                         "src/.dddjango/orders/scope.md"):
            _write(self.repo, relative, "hidden\n")
        snapshot = self.td / "snapshot"
        gate._snapshot_current(self.repo, snapshot)
        hidden = {str(p.relative_to(snapshot)): p.read_text(encoding="utf-8")
                  for p in snapshot.rglob("*") if p.is_file()
                  and any(part.startswith(".") for part in p.relative_to(snapshot).parts)}
        self.assertEqual(hidden, documents)

    def test_pregate_planned_artifact_fires_with_archived_and_overlaid_scope(self):
        for tracked in (False, True):
            with self.subTest(tracked=tracked):
                _write(self.repo, ".dddjango/orders/scope.md", self.scope)
                if tracked:
                    _commit_all(self.repo, "scope")
                spec = self.td / "design-spec.md"
                spec.write_text("<!-- machine: file-plan -->\n```paths\nadd " + self.artifact
                                + "\n```\n<!-- machine: symbols -->\n```symbols\n```\n"
                                "<!-- machine: boundary-imports -->\n```imports\n```\n", encoding="utf-8")
                proc = subprocess.run([sys.executable, str(GATE.parent / "design_pregate.py"),
                                       str(spec), str(self.repo)], capture_output=True, text=True,
                                      env=_scrubbed_env())
                out = proc.stdout + proc.stderr
                self.assertEqual(proc.returncode, 2, out)
                self.assertRegex(out, rf"\| `{re.escape(self.checker)}` \| 0 \| 2 \|")


class CacheSnapshotRegression(unittest.TestCase):
    def test_snapshot_gate_skips_only_optional_cache_and_preserves_original_bytes(self):
        from pregate_fixture_run import _load_module
        sys.path.insert(0, str(GATE.parent))
        gate = _load_module(GATE, "cache_snapshot_gate")
        slots = (
            "domain_layer/vanished",
            "application_layer/order/vanished",
            "driving_layer/open_host_service/vanished",
            "application_layer/port/vanished",
            "driven_layer/adapter/email_sender/vanished_adapter",
        )
        with tempfile.TemporaryDirectory(prefix="cache-snapshot-") as temp:
            td = Path(temp)
            repo, anchor = _make_repo(td, "repo")
            for relative in slots:
                _write(repo, "application/orders/" + relative + "/deep/__pycache__/old.pyc", "cache bytes")
            _write(repo, "harmless.txt", "working change")
            before = {str(p.relative_to(repo)): p.read_bytes() for p in repo.rglob("*")
                      if p.is_file() and ".git" not in p.relative_to(repo).parts}
            snapshot = td / "snapshot"
            gate._snapshot_current(repo, snapshot)
            code, out = _gate(repo, anchor)
            self.assertEqual(code, 0, out)
            self.assertNotIn("vanished", out)
            for relative in slots:
                self.assertFalse((snapshot / "application/orders" / relative).exists(), relative)
            for relative in slots:
                _write(repo, "application/orders/" + relative + "/__init__.py", "")
            code, out = _gate(repo, anchor)
            self.assertEqual(code, 2, out)
            for rule in ("#299", "#256", "#193", "#570", "#569", "#152", "#218", "#225"):
                self.assertTrue(any(rule in line and "vanished" in line for line in out.splitlines()), (rule, out))
            for relative in slots:
                (repo / "application/orders" / relative / "__init__.py").unlink()
            after = {str(p.relative_to(repo)): p.read_bytes() for p in repo.rglob("*")
                     if p.is_file() and ".git" not in p.relative_to(repo).parts
                     and ".dddjango" not in p.relative_to(repo).parts}
            self.assertEqual(after, before)

    def test_snapshot_keeps_fixed_parents_hidden_files_empty_instances_and_other_parents(self):
        from pregate_fixture_run import _load_module
        sys.path.insert(0, str(GATE.parent))
        gate = _load_module(GATE, "cache_boundary_gate")
        with tempfile.TemporaryDirectory(prefix="cache-boundary-") as temp:
            td = Path(temp)
            repo = td / "repo"
            shutil.copytree(BASE_FIXTURE, repo)
            fixed = repo / "application/orders/application_layer/port/unit_of_work"
            shutil.rmtree(fixed)
            _write(repo, str(fixed.relative_to(repo)) + "/__pycache__/old.pyc", "cache")
            _write(repo, "other/domain_layer/vanished/__pycache__/old.pyc", "cache")
            _write(repo, "application/orders/driving_layer/api/order/order_controller/__pycache__/old.pyc", "cache")
            _write(repo, "application/orders/domain_layer/hidden/__pycache__/old.pyc", "cache")
            _write(repo, "application/orders/domain_layer/hidden/.real", "hidden source")
            (repo / "application/orders/domain_layer/empty").mkdir()
            _write(repo, "application/cache_bc/domain_layer/__pycache__/old.pyc", "cache")
            snapshot = td / "snapshot"
            gate._snapshot_current(repo, snapshot)
            for relative in (str(fixed.relative_to(repo)), "other/domain_layer/vanished",
                             "application/orders/domain_layer/hidden", "application/orders/domain_layer/empty",
                             "application/cache_bc/domain_layer",
                             "application/orders/driving_layer/api/order/order_controller"):
                self.assertTrue((snapshot / relative).is_dir(), relative)
            proc = subprocess.run([sys.executable, "-B", str(GATE.parent / "check-layer-skeleton.py"),
                                   str(snapshot)], capture_output=True, text=True, env=_scrubbed_env())
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertTrue(any("#488" in line and "unit_of_work" in line for line in proc.stdout.splitlines()))

    def test_nested_application_container_uses_same_optional_slots_as_direct_checker(self):
        from pregate_fixture_run import _load_module
        sys.path.insert(0, str(GATE.parent))
        gate = _load_module(GATE, "nested_cache_gate")
        with tempfile.TemporaryDirectory(prefix="nested-cache-") as temp:
            td = Path(temp)
            root = td / "repo"
            shutil.copytree(BASE_FIXTURE, root / "src")
            relative = "src/application/orders/domain_layer/vanished"
            _write(root, relative + "/__pycache__/old.pyc", "cache")
            snapshot = td / "snapshot"
            gate._snapshot_current(root, snapshot)
            self.assertFalse((snapshot / relative).exists())

class SisterGateRegression(unittest.TestCase):
    """자매 주어 분할이 서버 진단 또는 측정 실패를 숨기는 변경을 잡는다."""
    checker = "check-context-isolation.py"
    sister_title = "자매 플러그인 영역(dddjango-web 소유 — 서버 판정 밖 · 보고만)"

    def setUp(self):
        from pregate_fixture_run import _load_module
        sys.path.insert(0, str(GATE.parent))
        self.gate = _load_module(GATE, "sister_registry_gate")
        self.temp = tempfile.TemporaryDirectory(prefix="sister-gate-")
        self.addCleanup(self.temp.cleanup)
        self.td = Path(self.temp.name)
        self.repo, _ = _make_repo(self.td, "repo")
        _write(self.repo, "manage.py", 'import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")\n')
        _write(self.repo, "config/settings.py", "")
        _write(self.repo, ".gitignore", ".dddjango-web/\n")
        (self.repo / ".dddjango-web").mkdir()
        self.anchor = _commit_all(self.repo, "server project")
        _write(self.repo, "note.md", "dirty\n")

    def measure(self, subjects, *, current_exit=2, anchor_exit=0,
                synthetic=False, no_records=False, retained=None, extra=None):
        # 검사기 실행 경계만 대역. 실제 archive·주어 매칭·분할·출력·sidecar를 실행한다.
        records = []
        def run(target, sink=None, git_root=None, only=None, unclassifiable=None):
            current = target.name == "current"
            lines = set()
            recs = []
            if current:
                for rule, subject, message in subjects:
                    rec = {"checker": self.checker, "rule": rule, "file": subject,
                           "message": message, "kind": "violation", "severity": "error"}
                    if rule is None:
                        rec["contract_ref"] = "선행 계약 시험"
                    else:
                        lines.add(self.gate._normalize(f"{self.checker} :: [{rule}] {subject}: {message}", ()))
                    if not no_records:
                        recs.append(rec)
                records[:] = recs
            if synthetic:
                lines.add(f"{self.checker} :: [진단 미파싱 · exit 2] fail-closed 귀속")
            return {self.checker: current_exit if current else anchor_exit}, lines, recs, set()
        args = [str(self.repo), "--anchor", self.anchor,
                "--introduced-json", str(self.td / "introduced.json"),
                "--contract-json", str(self.td / "contract.json"), *(extra or [])]
        out = io.StringIO()
        with patch.object(self.gate, "_run_registry", side_effect=run), contextlib.redirect_stdout(out):
            if retained is None:
                code = self.gate.main(args)
            else:
                prov = self.gate._ProvenanceResult(merges=[], chain=[])
                prov.retained = {f"{self.checker} :: [{r}] {p}: {m}": retained for r, p, m in subjects}
                with patch.object(self.gate, "_provenance_split", return_value=prov):
                    code = self.gate.main(args)
        return code, out.getvalue(), json.loads((self.td / "introduced.json").read_text()), records

    def test_sister_only_report_and_empty_sidecars(self):
        code, out, payload, _ = self.measure([("#95", "web/application/shop/a.py:7", "위반")])
        self.assertEqual(code, 0, out)
        self.assertIn(f"== {self.sister_title} 1건 ==", out)
        self.assertEqual(_lines_of(out, "귀속(N∖L)"), set())
        self.assertEqual(_lines_of(out, self.sister_title),
                         {self.checker + " :: [#95] web/application/shop/a.py:N: 위반"})
        self.assertEqual(payload["records"], [])
        self.assertEqual(payload["attributed_lines"], [])

    def test_null_rule_sister_contract_excluded_and_server_contract_preserved(self):
        subjects = [("#95", "web/a.py", "숫자 위반"),
                    (None, "web/contract.py:9", "자매 계약"),
                    (None, "application/orders/contract.py:8", "서버 계약")]
        code, out, payload, _ = self.measure(subjects)
        self.assertEqual(code, 0, out)
        self.assertEqual(payload["records"], [])
        contract = json.loads((self.td / "contract.json").read_text())
        self.assertEqual(contract["total"], 1, contract)
        self.assertEqual([(r["file"], r["message"], r["contract_ref"]) for r in contract["records"]],
                         [("application/orders/contract.py:8", "서버 계약", "선행 계약 시험")])
        self.assertEqual(_lines_of(out, self.sister_title),
                         {self.checker + " :: [#95] web/a.py: 숫자 위반",
                          self.checker + " :: - web/contract.py:N: 자매 계약"})
        code, out, _, _ = self.measure(subjects, current_exit=1)
        self.assertEqual(code, 2, out)
        self.assertNotIn(self.sister_title, out)
        contract = json.loads((self.td / "contract.json").read_text())
        self.assertEqual({r["message"] for r in contract["records"]}, {"자매 계약", "서버 계약"})

    def test_keyword_settings_update_keeps_server_diagnostic_and_record(self):
        manage = self.repo / "manage.py"
        manage.write_text(manage.read_text() + 'os.environ.update(DJANGO_SETTINGS_MODULE="web.settings.dev")\n')
        _write(self.repo, "web/settings/dev.py", "")
        code, out, payload, records = self.measure([("#446", "web/settings/dev.py", "서버 설정 위반")])
        self.assertEqual(code, 2, out)
        self.assertNotIn(self.sister_title, out)
        self.assertEqual(payload["records"], records)
        self.assertEqual(_lines_of(out, "귀속(N∖L)"),
                         {self.checker + " :: [#446] web/settings/dev.py: 서버 설정 위반"})

    def test_mixed_preserves_each_server_rule_record_and_message_path(self):
        server = [("#95", "application/orders/a.py", "의존 web/application/shop/a.py"),
                  ("#450", "application/orders", "폴더 위반"),
                  ("#488", "application/orders/missing.py", "없는 locator")]
        web = [("#95", "web_test/shop/a.py", "위반"), ("#488", ".dddjango-web/missing.py", "위반")]
        code, out, payload, records = self.measure(server + web)
        self.assertEqual(code, 2, out)
        self.assertEqual(payload["records"], records[:3])
        self.assertEqual(set(payload["attributed_lines"]),
                         {f"{self.checker} :: [{r}] {p}: {m}" for r, p, m in server})
        self.assertEqual(_lines_of(out, self.sister_title),
                         {f"{self.checker} :: [{r}] {p}: {m}" for r, p, m in web})

    def test_ambiguous_unmatched_and_outside_subjects_stay(self):
        subjects = ["(target)", "../web/a.py", "/web/a.py", "web/../application/a.py",
                    "web/a.py, application/a.py", "web/a.py | web/b.py", "application/web/a.py"]
        code, out, payload, _ = self.measure([("#74", p, "위반") for p in subjects])
        self.assertEqual(code, 2, out)
        self.assertEqual(len(payload["records"]), len(subjects))
        self.assertNotIn(self.sister_title, out)
        code, out, payload, _ = self.measure([("#95", "web/a.py", "위반")], no_records=True)
        self.assertEqual(code, 2, out)
        self.assertEqual(payload["unmatched_lines"], [self.checker + " :: [#95] web/a.py: 위반"])
        self.assertNotIn(self.sister_title, out)

    def test_uncertain_ownership_keeps_web_attributed(self):
        manage = self.repo / "manage.py"
        original = manage.read_text()
        cases = [None, 'import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", choose())\n',
                 original + 'os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")\n',
                 'import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")\n']
        _write(self.repo, "web/settings.py", "")
        for source in cases:
            with self.subTest(manage=source):
                if source is None:
                    manage.unlink()
                else:
                    manage.write_text(source)
                code, out, payload, _ = self.measure([("#95", "web/a.py", "위반")])
                self.assertEqual(code, 2, out)
                self.assertEqual(payload["records"][0]["file"], "web/a.py")
                self.assertNotIn(self.sister_title, out)
        manage.write_text(original)
        for name in (".dddjango-web", "web", "web_test"):
            with self.subTest(link=name):
                path = self.repo / name
                if path.exists():
                    shutil.rmtree(path)
                path.symlink_to(self.repo / "config", target_is_directory=True)
                code, out, _, _ = self.measure([("#95", "web/a.py", "위반")])
                self.assertEqual(code, 2, out)
                self.assertNotIn(self.sister_title, out)
                path.unlink()
                path.mkdir()
        (self.repo / ".dddjango-web").rmdir()
        code, out, _, _ = self.measure([("#95", "web/a.py", "위반")])
        self.assertEqual(code, 2, out)
        self.assertNotIn(self.sister_title, out)

    def test_project_realpath_alias_and_subtarget_do_not_split(self):
        shutil.rmtree(self.repo / "config")
        _write(self.repo, "web/settings.py", "")
        (self.repo / "config").symlink_to(self.repo / "web", target_is_directory=True)
        code, out, _, _ = self.measure([("#446", "web/settings.py", "서버 설정")])
        self.assertEqual(code, 2, out)
        self.assertNotIn(self.sister_title, out)
        self.repo = self.repo / "web"
        (self.repo / "application").mkdir()
        self.anchor = _head(self.repo)
        code, out, _, _ = self.measure([("#95", "web/a.py", "하위 TARGET")])
        self.assertEqual(code, 2, out)
        self.assertNotIn(self.sister_title, out)

    def test_abnormal_exit_and_identical_unparsed_block_sister_split(self):
        for kwargs in ({"current_exit": 1}, {"anchor_exit": 3}, {"synthetic": True}):
            with self.subTest(kwargs=kwargs):
                code, out, payload, _ = self.measure([("#95", "web/a.py", "위반")], **kwargs)
                self.assertEqual(code, 2, out)
                self.assertEqual(payload["records"][0]["file"], "web/a.py")
                self.assertNotIn(self.sister_title, out)

    def test_numbered_diagnostic_then_process_exit_3_stays_attributed(self):
        gate = _gate_copy(self.td, "crashed-checker")
        path = gate.parent / self.checker
        path.write_text("import sys\nfrom pathlib import Path\nfrom findings import Findings, emit_all\n"
                        "if Path(sys.argv[1]).name == 'anchor': raise SystemExit(0)\n"
                        "out = Findings(defer=True)\nout.add('#95', Path('web/a.py'), 'partial diagnostic')\n"
                        "emit_all(out, printer=print)\nraise SystemExit(3)\n")
        source = gate.read_text()
        gate.write_text(source.replace("from checker_registry import REGISTRY, checker_argv",
                "from checker_registry import checker_argv\nREGISTRY = [('check-context-isolation.py', False)]"))
        code, out = _gate(self.repo, self.anchor, gate=gate)
        self.assertEqual(code, 2, out)
        self.assertIn("| `check-context-isolation.py` | 0 | 3 |", out)
        self.assertEqual(_lines_of(out, "귀속(N∖L)"),
                         {self.checker + " :: [#95] web/a.py: partial diagnostic"})
        self.assertNotIn(self.sister_title, out)

    def test_numbered_diagnostic_with_analysis_record_stays_attributed(self):
        gate = _gate_copy(self.td, "analysis-checker")
        (gate.parent / self.checker).write_text(
            "import sys\nfrom pathlib import Path\nfrom findings import Findings, emit_all\n"
            "if Path(sys.argv[1]).name == 'anchor': raise SystemExit(0)\n"
            "out = Findings(defer=True)\nout.add('#95', Path('web/a.py'), 'numeric')\n"
            "out.add('분석', Path('web/a.py'), 'parse failure')\n"
            "emit_all(out, printer=print)\nraise SystemExit(2)\n")
        source = gate.read_text()
        gate.write_text(source.replace("from checker_registry import REGISTRY, checker_argv",
                "from checker_registry import checker_argv\nREGISTRY = [('check-context-isolation.py', False)]"))
        code, out = _gate(self.repo, self.anchor, gate=gate)
        self.assertEqual(code, 2, out)
        self.assertEqual(_lines_of(out, "귀속(N∖L)"), {self.checker + " :: [#95] web/a.py: numeric"})
        self.assertNotIn(self.sister_title, out)

    def test_raw_analysis_or_record_channel_failure_blocks_sister_split(self):
        gate = _gate_copy(self.td, "lost-analysis-checker")
        source = gate.read_text()
        gate.write_text(source.replace("from checker_registry import REGISTRY, checker_argv",
                "from checker_registry import checker_argv\nREGISTRY = [('check-context-isolation.py', False)]"))
        failures = {
            "lost analysis stdout": "print('[분석] web/a.py: lost analysis record')\n",
            "lost analysis stderr": "print('[분석] web/a.py: lost analysis record', file=sys.stderr)\n",
            "record write warning": "print('주의: 구조화 레코드 채널 비활성 — DJR_FINDINGS_JSON 경로에 쓸 수 없다', file=sys.stderr)\n",
            "broken json": "with open(os.environ['DJR_FINDINGS_JSON'], 'a') as f: f.write('{broken\\n')\n",
            "missing numeric record": "print('[#96] web/b.py: lost numeric record')\n",
            "extra numeric record": "extra = Findings(defer=True)\nextra.add('#96', Path('web/b.py'), 'record without line')\nemit_all(extra)\n",
        }
        for side in ("current", "anchor"):
            for label, failure in failures.items():
                with self.subTest(side=side, failure=label):
                    (gate.parent / self.checker).write_text(
                        "import os, sys\nfrom pathlib import Path\nfrom findings import Findings, emit_all\n"
                        "side = Path(sys.argv[1]).name\n"
                        "if side == 'anchor':\n"
                        "    if " + repr(side) + " != 'anchor': raise SystemExit(0)\n"
                        "out = Findings(defer=True)\n"
                        "out.add('#95', Path('web/a.py'), 'numeric' if side == 'current' else 'legacy')\n"
                        "emit_all(out, printer=print)\n"
                        "if side == " + repr(side) + ":\n" +
                        "".join("    " + line + "\n" for line in failure.splitlines()) +
                        "raise SystemExit(2)\n")
                    introduced = self.td / "introduced.json"
                    code, out = _gate(self.repo, self.anchor, gate=gate,
                                      extra=["--introduced-json", str(introduced)])
                    self.assertEqual(code, 2, out)
                    self.assertNotIn(self.sister_title, out)
                    self.assertIn(self.checker + " :: [#95] web/a.py: numeric",
                                  _lines_of(out, "귀속(N∖L)"))
                    payload = json.loads(introduced.read_text())
                    self.assertEqual([(r["rule"], r["file"], r["message"]) for r in payload["records"]],
                                     [("#95", "web/a.py", "numeric")])

    def test_case_alias_missing_package_and_unreadable_source_fallback(self):
        _write(self.repo, "web/settings.py", "")
        manage = self.repo / "manage.py"
        for module in ("missing.settings", "Web.settings"):
            with self.subTest(module=module):
                manage.write_text('import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "' + module + '")\n')
                code, out, _, _ = self.measure([("#446", "web/settings.py", "설정 위반")])
                self.assertEqual(code, 2, out)
                self.assertNotIn(self.sister_title, out)
        manage.write_text('import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")\n')
        with patch.dict(os.environ, {"DJR_SISTER_SOURCE_ROOT": str(self.td / "unreadable-missing")}):
            code, out, payload, _ = self.measure([("#95", "web/a.py", "위반")])
        self.assertEqual(code, 0, out)
        self.assertEqual(payload["records"], [])
        self.assertIn(self.sister_title, out)

    def test_provenance_measurement_invalid_stays_with_reason(self):
        approved = self.td / "approved.txt"
        approved.write_text("")
        code, out, payload, _ = self.measure([("#95", "web/a.py", "위반")],
            retained="측정 무효(스냅숏 실패) — abcdef123456",
            extra=["--approved-merge-file", str(approved)])
        self.assertEqual(code, 2, out)
        self.assertIn("↳ 귀속 유지: 측정 무효(스냅숏 실패)", out)
        self.assertEqual(payload["records"][0]["file"], "web/a.py")
        self.assertNotIn(self.sister_title, out)

    def test_parse_fail_web_reports_server_stays(self):
        _write(self.repo, "web/broken.py", "def broken(:\n")
        _write(self.repo, "application/orders/broken.py", "def broken(:\n")
        code, out, payload, _ = self.measure([])
        self.assertEqual(code, 2, out)
        self.assertEqual(len(payload["attributed_lines"]), 1)
        self.assertIn("[#parse-fail] application/orders/broken.py:", payload["attributed_lines"][0])
        self.assertIn("[#parse-fail] web/broken.py:", _section(out, self.sister_title))
        (self.repo / "application/orders/broken.py").unlink()
        code, out, payload, _ = self.measure([])
        self.assertEqual(code, 0, out)
        self.assertEqual(payload["attributed_lines"], [])
        self.assertIn(f"{self.sister_title} 1건", out)

    def test_pregate_original_root_reaches_copy_without_marker(self):
        from pregate_fixture_run import _load_module
        pregate = _load_module(GATE.parent / "design_pregate.py", "sister_design_pregate")
        copy = self.td / "copy"
        shutil.copytree(self.repo, copy, ignore=shutil.ignore_patterns(".dddjango-web"))
        self.assertFalse((copy / ".dddjango-web").exists())
        _write(copy, "web/broken.py", "def broken(:\n")
        scratch = self.td / "scratch"
        scratch.mkdir()
        result = pregate.run_gate(copy, scratch, sys.executable, source_root=self.repo)
        self.assertIn("[#parse-fail] web/broken.py:", _section(result["raw_stdout"], self.sister_title))
        self.assertFalse(any("[#parse-fail] web/" in line for line in result["attributed_lines"]))

    def test_no_split_output_matches_head_2191(self):
        old_gate = _gate_copy(self.td, "head-scripts", "HEAD")
        for filename in ("anchor_diff.py", "design_pregate.py"):
            proc = _git(ROOT, "show", "HEAD:dddjango/scripts/" + filename)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            (old_gate.parent / filename).write_text(proc.stdout)
        for marker in (False, True):
            with self.subTest(marker=marker):
                if not marker:
                    (self.repo / ".dddjango-web").rmdir()
                    _write(self.repo, "web/server.py", "from application.orders.domain_layer.order.order import Order\n")
                    _write(self.repo, "web/settings.py", "")
                    _write(self.repo, "manage.py", 'import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")\n')
                else:
                    (self.repo / ".dddjango-web").mkdir()
                    shutil.rmtree(self.repo / "web")
                    _write(self.repo, "manage.py", 'import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")\n')
                    _plant_violation(self.repo)
                old_code, old = _gate(self.repo, self.anchor, gate=old_gate)
                code, out = _gate(self.repo, self.anchor)
                self.assertEqual(code, old_code)
                self.assertEqual(_mask(out), _mask(old))

    def test_actual_server_bc_import_and_web_model_choices_records_survive(self):
        server = _VIOLATION_REL
        _write(self.repo, server, "from web.application.shop.domain_layer.item.item import Item\n"
               "from web.model import ShopModel\nShopModel.objects.filter(status='open')\n")
        _write(self.repo, "web/model.py", "from django.db import models\nclass ShopModel(models.Model):\n"
               "    status = models.CharField(choices=Status.choices)\n")
        _write(self.repo, "web/application/shop/domain_layer/item/item.py", "class Item: ...\n")
        web = "web/application/shop/driving_layer/api/item/schema/invalid.py"
        # web 파일의 서버 도메인 import 는 BC 마다 도는 #6 이 더는 안 잰다(뿌리 `application/` 만 BC). 자매 절까지 가는 실제 출력은
        # 저장소 전체를 훑는 public-surface 검사기의 타입 없는 함수 줄로 지킨다.
        _write(self.repo, web, "from application.orders.domain_layer.order.order import Order\n\n\n"
               "def peek(order):\n    return Order\n")
        out = io.StringIO()
        surface = "check-public-surface-annotation.py"
        selected = [(self.checker, False), ("check-choices-literal-consumption.py", False), (surface, False)]
        with patch.object(self.gate, "REGISTRY", selected), contextlib.redirect_stdout(out):
            code = self.gate.main([str(self.repo), "--anchor", self.anchor,
                "--introduced-json", str(self.td / "introduced.json"),
                "--contract-json", str(self.td / "contract.json")])
        self.assertEqual(code, 2, out.getvalue())
        payload = json.loads((self.td / "introduced.json").read_text())
        matched = [r for r in payload["records"] if r["file"] == server and r["rule"] == "#12"]
        self.assertEqual(len(matched), 1, payload)
        self.assertIn("web.application.shop.domain_layer", matched[0]["message"])
        self.assertTrue(any("[#12] " + server in l for l in payload["attributed_lines"]))
        self.assertEqual(_lines_of(out.getvalue(), self.sister_title),
            {surface + " :: [#493] " + web + ":N: `peek()` 매개변수 `order` 에 타입이 없다",
             surface + " :: [#493] " + web + ":N: `peek()` 반환 타입이 없다"})
        self.assertFalse(any(r["file"].startswith("web/") for r in payload["records"]), payload)
        contract = json.loads((self.td / "contract.json").read_text())
        self.assertEqual(contract["total"], 1, contract)
        rec = contract["records"][0]
        self.assertEqual(rec["contract_ref"], "선행 계약(2026-07-06 상수 승격) 소유")
        self.assertEqual(rec["file"], server + ":3")
        self.assertIn("ShopModel.objects.filter/exclude(status=리터럴)", rec["message"])


class ApprovedInflowGateRegression(unittest.TestCase):
    """설계 v3 §7-1의 부재·공통 P·사본·안내 줄 계약."""

    def setUp(self) -> None:
        from anchor_diff_smoke import ApprovedInflowRepo
        sys.path.insert(0, str(GATE.parent))
        self.repo_type: type[ApprovedInflowRepo] = ApprovedInflowRepo
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="approved-gate-")
        self.addCleanup(self.temp.cleanup)
        self.td: Path = Path(self.temp.name)

    def verdict(self, r, anchor: str, merges: tuple[str, ...], code: int, reason: str) -> str:
        actual: int
        out: str
        actual, out = _gate(r.root, anchor, ["--approved-merge-file", str(r.approved(*merges))])
        self.assertEqual(actual, code, out)
        self.assertIn(reason, out)
        return out

    def absent(self, name: str, *, drop_parent: bool = False):
        r: ApprovedInflowRepo = self.repo_type(self.td, name)
        r.project("orders", "xbc")
        anchor: str = r.commit("A")
        r.checkout(anchor, "lane"); r.write("lane.txt", "lane"); r.commit("L0")
        r.checkout("main"); r.rm(r.fixed); r.commit("upstream deletion")
        r.checkout("lane"); r.merge(pending=drop_parent)
        if drop_parent:
            r.rm("application/xbc/composition_root"); r.commit("merge deletes parent")
        return r, anchor, r.git("rev-parse", "HEAD")

    def test_P13_P14_P14b_upstream_absence_and_parent_gap(self) -> None:
        r: ApprovedInflowRepo
        anchor: str
        merge: str
        for mode in ("inflow", "merge-gap", "chain-gap"):
            with self.subTest(mode=mode):
                r, anchor, merge = self.absent(mode, drop_parent=mode == "merge-gap")
                if mode != "inflow":
                    saved: dict[str, str] = {p.name: p.read_text() for p in (r.root / "application/xbc/composition_root").glob("*") if p.is_file()}
                    if mode == "chain-gap":
                        r.rm("application/xbc/composition_root"); gap: str = r.commit("remove parent")
                    if not saved:
                        saved = {"__init__.py": "", "dependency_wiring.py": "", "dependency_wiring_test.py": ""}
                    for name, source in saved.items():
                        r.write("application/xbc/composition_root/" + name, source)
                    r.commit("restore parent without file")
                    reason: str = f"유입 증명 실패(승인 머지 {merge[:12]} " + ("결과에 없음)" if mode == "merge-gap" else f"뒤 사슬 {gap[:12]} 에 없음)")
                    self.verdict(r, anchor, (merge,), 2, reason)
                else:
                    out: str = self.verdict(r, anchor, (merge,), 0, "부재(상류에도 없던 파일)")
                    self.assertIn(" · 부재 1", out)

    def test_P14c_P14d_P14e_restore_delete_resolution_and_later_proof(self) -> None:
        r: ApprovedInflowRepo
        anchor: str
        merge: str
        for mode in ("lane-delete", "resolution-delete", "later-delete"):
            with self.subTest(mode=mode):
                r, anchor, merge = self.absent(mode)
                r.checkout("main"); r.write(r.fixed); r.commit("upstream restores")
                r.checkout("lane"); m2: str = r.merge(pending=mode == "resolution-delete")
                if mode == "resolution-delete":
                    r.rm(r.fixed); m2 = r.commit("merge keeps deletion")
                else:
                    r.rm(r.fixed); r.commit("lane deletes")
                merges: tuple[str, ...] = (merge, m2)
                if mode == "later-delete":
                    r.write(r.fixed); r.commit("lane restores before upstream deletion")
                    r.checkout("main"); r.rm(r.fixed); r.commit("upstream deletes again")
                    r.checkout("lane"); m3: str = r.merge(); merges += (m3,)
                    self.verdict(r, anchor, merges, 0, f"유입: {m3[:12]}(L 증명) · 부재")
                else:
                    self.verdict(r, anchor, merges, 2, f"유입 증명 실패(뒤 승인 머지 {m2[:12]} 의 ^2 에 없음)")

    def test_P14f_P14g_P15_P15prime_lane_created_absence(self) -> None:
        r: ApprovedInflowRepo
        anchor: str
        merge: str
        for mode in ("bc-recreate", "side-merge", "lane-delete", "new-bc"):
            with self.subTest(mode=mode):
                r, anchor, merge = self.absent(mode)
                if mode == "bc-recreate":
                    r.checkout("main"); r.rm("application/xbc"); r.commit("upstream removes BC")
                    r.checkout("lane"); m2: str = r.merge()
                    r.bc("xbc"); r.rm(r.fixed); r.commit("lane creates BC")
                    self.verdict(r, anchor, (merge, m2), 2, f"뒤 승인 머지 {m2[:12]} 의 ^2 에 없음)")
                elif mode == "side-merge":
                    r.checkout(anchor, "side"); r.write("side.txt", "s"); r.commit("side")
                    r.checkout("lane"); m2 = r.merge("side")
                    self.verdict(r, anchor, (merge,), 2, f"뒤 미승인 머지 {m2[:12]})")
                else:
                    # P15: 승인 머지는 무관한 변경만 들였고 누락은 레인이 만든다.
                    r.checkout(anchor, "own"); r.write("own.txt", "o"); r.commit("own")
                    r.checkout("main"); r.write(r.fixed); r.commit("restore before unrelated merge")
                    r.checkout("own"); m2 = r.merge()
                    if mode == "new-bc":
                        r.bc("lane_bc"); r.rm("application/lane_bc/composition_root/wiring_material.py")
                    else:
                        r.rm(r.fixed)
                    r.commit("lane omission")
                    self.verdict(r, anchor, (m2,), 2, "부재 미증명")

    def test_P16_to_P20_existing_channels_share_chain_proof(self) -> None:
        anchor: str
        merge: str
        for mode in ("later-fix", "merge-gap", "octopus", "over", "invalid"):
            with self.subTest(mode=mode):
                r: ApprovedInflowRepo = self.repo_type(self.td, mode)
                anchor, merge = r.cause_merge(drop_in_merge=mode == "merge-gap")
                merges: tuple[str, ...] = (merge,)
                if mode == "later-fix":
                    r.checkout("main"); r.rm("application/billing"); r.commit("upstream fixes")
                    r.checkout("lane"); m2: str = r.merge(); merges += (m2,)
                    r.bc("billing"); r.commit("own cause")
                    reason: str = f"뒤 승인 머지 {m2[:12]} 의 ^2 에 없음)"
                elif mode == "merge-gap":
                    r.bc("zulu"); r.commit("own cause")
                    reason = f"유입 증명 실패(승인 머지 {merge[:12]} 결과에 없음)"
                elif mode == "over":
                    for index in range(64):
                        r.write("lane.txt", str(index)); r.commit(str(index))
                    reason = f"측정 생략(사슬 커밋 65 > 한도 64) — {merge[:12]}"
                elif mode == "invalid":
                    r.write("pyproject.toml", '[project]\nrequires-python = ">=3.99"\n'); gap: str = r.commit("invalid interpreter")
                    r.rm("pyproject.toml"); r.commit("fixed")
                    reason = f"측정 무효(사슬 {gap[:12]}) — {merge[:12]}"
                else:
                    for branch in ("s1", "s2"):
                        r.checkout(merge, branch); r.write(branch + ".txt", branch); r.commit(branch); r.checkout("lane")
                    r.git("merge", "-q", "--no-ff", "-m", "octopus", "s1", "s2")
                    reason = f"뒤 미승인 머지 {r.git('rev-parse', 'HEAD')[:12]})"
                out: str = self.verdict(r, anchor, merges, 2, reason)
                if mode == "later-fix":
                    retained: str = _section(out, "귀속(N∖L)")
                    self.assertIn("[#364]", retained)
                    self.assertIn("[#329]", retained)
                    self.assertEqual(retained.count(reason), 2)

    def test_G1_subject_guards_and_P21_P22_P23_links(self) -> None:
        r: ApprovedInflowRepo
        anchor: str
        merge: str
        merges: list[anchor_diff.ApprovedMerge]
        chain: list[anchor_diff.ChainCommit]
        import anchor_diff
        gate_module: ModuleType = __import__("registry_gate")
        r, anchor, merge = self.absent("guards")
        head: str = r.git("rev-parse", "HEAD")
        merges, chain = anchor_diff.load_approved_merges(r.approved(merge), r.root, anchor, head)
        for mode in ("absolute", "dotdot", "punctuation", "not-py", "directory", "ignored-live"):
            with self.subTest(mode=mode):
                p: str = {"absolute": "/abs/a.py", "dotdot": "application/../a.py", "punctuation": "application/a:b.py", "not-py": "application/xbc/composition_root/no.txt"}.get(mode, r.fixed)
                if mode == "directory":
                    (r.root / p).mkdir()
                elif mode == "ignored-live":
                    r.write(".gitignore", p + "\n"); r.write(p)
                line: str = "check-layer-skeleton.py :: [#488] " + p + ": 고정 파일 부재"
                result: gate_module._ProvenanceResult = gate_module._provenance_split(r.root, anchor, head, merges, chain, [line], [{"file": p, "rule": "#488", "checker": "check-layer-skeleton.py", "message": "고정 파일 부재"}], (), self.td / mode)
                self.assertEqual(result.inflow, [])
                self.assertEqual(result.retained[line], "비-blob 경로")
                def render(snapshot: Path, *args, **kwargs):
                    current: bool = snapshot.name == "current"
                    return ({"check-layer-skeleton.py": 2 if current else 0}, {line} if current else set(),
                            [{"file": p, "rule": "#488", "checker": "check-layer-skeleton.py", "message": "고정 파일 부재"}] if current else [], set())
                output: io.StringIO = io.StringIO()
                # 주어 가드만 겨냥한 합성 레코드다. 코드 파스 선점은 이 가드의 측정 재료가 아니다.
                with patch.object(gate_module, "_run_registry", side_effect=render), \
                        patch.object(gate_module, "_parse_fail_findings", return_value=set()), contextlib.redirect_stdout(output):
                    code: int = gate_module.main([str(r.root), "--anchor", anchor, "--approved-merge-file", str(r.approved(merge))])
                self.assertEqual(code, 2, output.getvalue())
                self.assertIn("↳ 귀속 유지: 비-blob 경로", output.getvalue())
                if mode in ("directory", "ignored-live"):
                    r.rm(p)
        for folder in (False, True):
            r = self.repo_type(self.td, "link-" + str(folder))
            r.project("orders"); anchor = r.commit("A")
            r.checkout(anchor, "lane"); r.write("lane.txt", "l"); r.commit("L0")
            r.checkout("main")
            rel: str = "application/orders/domain_layer/bad.py"
            r.write(rel, "from django.db import models\n")
            outside: Path = self.td / ("outside-" + str(folder)); outside.mkdir()
            if folder:
                r.write("external/__init__.py"); r.rm("external"); (r.root / "external").symlink_to(outside, target_is_directory=True)
            else:
                (outside / "target.py").write_text("from django.db import models\n", encoding="utf-8")
                (r.root / "extra.py").symlink_to(outside / "target.py")
            r.commit("upstream symlink"); r.checkout("lane"); merge = r.merge()
            out: str = self.verdict(r, anchor, (merge,), 2, f"측정 무효(스냅숏 실패) — {merge[:12]}")
            self.assertIn("사본 밖을 가리키는 심링크", out)
        r = self.repo_type(self.td, "subject-link"); r.project("orders"); anchor = r.commit("A")
        r.checkout(anchor, "lane"); r.write("lane.txt", "l"); r.commit("L0")
        r.checkout("main"); r.write("payload.txt", "from django.db import models\n")
        for index in range(4):
            (r.root / f"application/orders/domain_layer/link{index}.py").symlink_to("../../../payload.txt")
        r.commit("upstream subject links"); r.checkout("lane"); merge = r.merge()
        out = self.verdict(r, anchor, (merge,), 2, "비-blob 경로")
        self.assertGreaterEqual(out.count("↳ 귀속 유지: 비-blob 경로"), 4)

    def test_U2a_U2b_U2c_U2d_exact_hint_and_old_outputs(self) -> None:
        actual: int
        out: str
        old_code: int
        old_out: str
        code: int
        text: str
        r: ApprovedInflowRepo = self.repo_type(self.td, "hint"); r.project("orders"); anchor: str = r.commit("A")
        r.checkout(anchor, "lane"); r.write("lane.txt", "l"); r.commit("L0")
        r.checkout("main"); r.write("up.txt", "u"); r.commit("U")
        r.checkout("lane"); merge: str = r.merge()
        old: "Path | None" = _gate_copy(self.td, "hint-old", _RELEASED_2212_COMMIT)
        assert old is not None, f"2.21.2 게이트 사본({_RELEASED_2212_COMMIT}) 추출 실패"
        actual, out = _gate(r.root, anchor)
        old_code, old_out = _gate(r.root, anchor, gate=old)
        self.assertEqual(actual, old_code, out)
        expected: str = (f"안내: 앵커 {anchor[:12]}..HEAD first-parent 사슬에 2-부모 머지 1건이 있고 --approved-merge-file 가 없다 — {merge[:12]}(^2 main) · 발주자가 승인한 main→레인 머지라면 발주자가 `<산출물 폴더>/approved-merges.txt` 에 그 SHA 를 적은 뒤(코디네이터·실행자는 이 파일을 쓰지 않는다) 그 파일을 붙여 다시 실행하면 승인 유입을 따로 가른다(이 줄은 판정·exit 를 바꾸지 않는다)")
        self.assertEqual([l for l in out.splitlines() if l.startswith("안내:")], [expected])
        self.assertEqual(_mask("\n".join(l for l in out.splitlines() if not l.startswith("안내:"))), _mask(old_out))
        new_run: dict[str, object] = _par_run(GATE, r.root, anchor, self.td, "4")
        old_run: dict[str, object] = _par_run(old, r.root, anchor, self.td, "4")
        new_run["stdout"] = "\n".join(l for l in str(new_run["stdout"]).splitlines() if not l.startswith("안내:"))
        self.assertTrue(_same_output(new_run, old_run))
        self.assertEqual(new_run["leaked"], [])
        for ref, flag in ((anchor, True), (merge, False)):
            extra: list[str] = ["--approved-merge-file", str(r.approved(merge))] if flag else []
            r.write("working.txt", "w")
            code, text = _gate(r.root, ref, extra)
            self.assertIn("판정:", text)
            self.assertNotIn("안내:", text)
            self.assertEqual(code, 0, text)
        r.checkout("lane", "feature-x"); r.write("side.txt", "s"); r.commit("side")
        r.checkout("lane"); side: str = r.merge("feature-x")
        code, out = _gate(r.root, anchor)
        self.assertEqual(code, 0, out); self.assertIn(f"{side[:12]}(^2 feature-x)", out)
        r.git("branch", "-D", "feature-x")
        code, out = _gate(r.root, anchor)
        self.assertEqual(code, 0, out)
        self.assertIn("레인 곁가지 의심(^2 를 담은 ref 가 HEAD 브랜치뿐 — 등재 대상 아님): " + side[:12], out)

    def test_U2b_no_merge_octopus_only_and_nonancestor(self) -> None:
        code: int
        out: str
        r: ApprovedInflowRepo = self.repo_type(self.td, "no-hints"); r.project("orders"); anchor: str = r.commit("A")
        r.checkout(anchor, "lane"); r.write("lane.txt", "l"); r.commit("L")
        code, out = _gate(r.root, anchor)
        self.assertEqual(code, 0, out); self.assertIn("판정:", out); self.assertNotIn("안내:", out)
        for branch in ("s1", "s2"):
            r.checkout(anchor, branch); r.write(branch + ".txt", branch); r.commit(branch); r.checkout("lane")
        r.git("merge", "-q", "--no-ff", "-m", "octopus", "s1", "s2")
        code, out = _gate(r.root, anchor)
        self.assertEqual(code, 0, out); self.assertIn("판정:", out); self.assertNotIn("안내:", out)
        r.checkout(anchor, "unrelated"); r.write("unrelated.txt", "u"); other: str = r.commit("other")
        r.checkout("lane")
        code, out = _gate(r.root, other)
        self.assertEqual(code, 0, out); self.assertIn("조상이 아니다", out); self.assertNotIn("안내:", out)


_PREGATE_MINI: Path = ROOT / "workspace" / "eval" / "fixtures" / "pregate" / "mini_repo"
_LINK_DIR: str = ".dddjango-web/20261012-0717-x/return1/browser-basetemp-2"
_PURE_REL: str = "framework/pure/json_value.py"
_PURE_SRC: str = ('from typing import Mapping as Glossary, Sequence as Roster, Union\n\n'
                  'TallyScalar = Union[str, int, float, bool, None]\n'
                  'TallyValue = Union[TallyScalar, Roster["TallyValue"], Glossary[str, "TallyValue"]]\n')


def _gate_module() -> ModuleType:
    import importlib.util
    sys.path.insert(0, str(GATE.parent))
    name: str = "registry_gate_smoke_gate"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, GATE)
        module: ModuleType = importlib.util.module_from_spec(spec)
        sys.modules[name] = module  # dataclass 가 모듈 이름으로 자기 모듈을 찾는다(3.14)
        spec.loader.exec_module(module)
    return sys.modules[name]


class SnapshotLinkRegression(unittest.TestCase):
    """F4-97 · F4-98(2.23.1) — 사본 밖 링크가 모두 숨김 경로(문서 입력 제외)에 있으면 걷고 재고, 그 밖이면 fail-closed ·
    판정 줄에 «잴 수 없어 남긴» 수를 따로 적는다."""

    def setUp(self) -> None:
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="gate-link-")
        self.addCleanup(self.temp.cleanup)
        self.td: Path = Path(self.temp.name)
        (self.td / "outside").mkdir()

    def chain(self, name: str, link_dir: str) -> "tuple[Path, str, str, Path]":
        """앵커 → 레인 커밋 → main X1(위반 + 링크) → 승인 머지 M1 → main X2(링크 걷기) → 승인 머지 M2."""
        repo: Path
        anchor: str
        repo, anchor = _make_repo(self.td, name)
        base: str = _git(repo, "branch", "--show-current").stdout.strip()
        _git(repo, "checkout", "-q", "-b", "lane"); _write(repo, "lane_note.md", "lane\n"); _commit_all(repo, "lane")
        _git(repo, "checkout", "-q", base)
        _write(repo, _VIOLATION_REL, _VIOLATION_SRC)
        (repo / link_dir).mkdir(parents=True)
        os.symlink(str(self.td / "gone" / "x1"), repo / link_dir / "test_xcurrent")
        _commit_all(repo, "X1 main: violation + record link")
        _git(repo, "checkout", "-q", "lane"); _git(repo, "merge", "-q", "--no-ff", "-m", "M1", base)
        m1: str = _head(repo)
        _git(repo, "checkout", "-q", base); _git(repo, "rm", "-q", f"{link_dir}/test_xcurrent"); _commit_all(repo, "X2 main: link removed")
        _git(repo, "checkout", "-q", "lane"); _git(repo, "merge", "-q", "--no-ff", "-m", "M2", base)
        m2: str = _head(repo)
        approved: Path = self.td / f"{name}-approved.txt"
        approved.write_text(f"{m1} M1\n{m2} M2\n", encoding="utf-8")
        return repo, anchor, m1, approved

    def test_L3_history_record_link_no_longer_voids_inflow_proof(self) -> None:
        repo, anchor, _m1, approved = self.chain("l3", _LINK_DIR)
        code, out = _gate(repo, anchor, ["--approved-merge-file", str(approved)])
        self.assertEqual(code, 0, out)
        self.assertNotIn("측정 무효(스냅숏 실패)", out)
        # 출처 스냅숏은 숨김 경로를 빼고 풀어 기록 링크가 들어오지 않는다(걷을 링크 0 — 알림 없음)
        self.assertNotIn("숨김 경로의 사본 밖 심링크를 뺀 스냅숏", out)

    def test_L3b_anchor_inside_the_link_window_is_a_normal_baseline(self) -> None:
        repo, _anchor, m1, approved = self.chain("l3b", _LINK_DIR)
        code, out = _gate(repo, m1, ["--approved-merge-file", str(approved)])
        self.assertEqual(code, 0, out)
        # 앵커 사본도 숨김 경로를 빼고 풀어 기록 링크가 들어오지 않는다(걷을 링크 0 — 알림 없음)
        self.assertNotIn(f"정보: 앵커 {m1[:12]} 사본에서 숨김 경로의 사본 밖 심링크", out)
        self.assertNotIn("기준선 불능", out)

    def test_L6_surface_link_stays_unmeasured_and_is_counted_on_the_verdict(self) -> None:
        repo, anchor, _m1, approved = self.chain("l6", "records/x")
        code, out = _gate(repo, anchor, ["--approved-merge-file", str(approved)])
        self.assertEqual(code, 2, out)
        self.assertIn("측정 무효(스냅숏 실패)", out)
        self.assertRegex(out, r"판정: 귀속 (\d+)건 → red\(승인 유입 0건 제외 · 귀속 \1건 가운데 잴 수 없어 남긴 \d+건 — 위 provenance 진단\)")

    def test_L8_surface_link_escaping_through_a_hidden_link_is_named_without_traceback(self) -> None:
        repo, _anchor = _make_repo(self.td, "l8")
        (self.td / "outside" / "y.py").write_text("X = 1\n", encoding="utf-8")
        os.symlink(str(self.td / "outside"), repo / ".x")
        os.symlink("../../.x/y.py", repo / "application" / "orders" / "y.py")
        anchor: str = _commit_all(repo, "anchor with links")
        _write(repo, "lane_note.md", "lane\n"); _commit_all(repo, "lane")
        code, out = _gate(repo, anchor)
        self.assertEqual(code, 2, out)
        self.assertNotIn("Traceback", out)
        self.assertIn(f"주의: 앵커 {anchor[:12]} 사본에 사본 밖을 가리키는 심링크 application/orders/y.py", out)
        self.assertIn("(기준선 불능 — 앵커 사본 밖 심링크 · 현재 위반 전량 귀속)", out)

    def test_L10_document_inputs_and_case_variants_stay_fail_closed(self) -> None:
        approval: Path = self.td / "outside" / "approval.md"
        approval.write_text("# 설계\n- 멱등성 채택 — G1 결정(사용자 승인)\n", encoding="utf-8")
        for index, rel in enumerate((".dddjango/run/design-spec.md", ".DDDJANGO/run/design-spec.md",
                                     ".dddjango/run/DESIGN-SPEC.MD", ".DDDJANGO/run/SCOPE.MD", ".dddjango")):
            with self.subTest(rel=rel):
                repo, _pre = _make_repo(self.td, f"l10-{index}")
                _write(repo, "application/orders/domain_layer/order/idempotency_record.py", 'class IdempotencyRecord:\n    """x."""\n')
                link: Path = repo / rel
                link.parent.mkdir(parents=True, exist_ok=True)
                os.symlink(str(approval if rel != ".dddjango" else self.td / "outside"), link)
                anchor: str = _commit_all(repo, "anchor with document link")
                link.unlink()
                _write(repo, rel if rel != ".dddjango" else ".dddjango/run/scope.md", "# 승인 없음\n")
                _commit_all(repo, "lane: approval removed")
                code, out = _gate(repo, anchor)
                self.assertEqual(code, 2, out)
                self.assertIn("(기준선 불능 — 앵커 사본 밖 심링크 · 현재 위반 전량 귀속)", out)


class ListShrinkRegression(unittest.TestCase):
    """F4-99(2.23.1) — 줄 번호 없는 줄의 문자열 목록 칸만 줄었고 그 파일이 앵커와 바이트까지 같으면 잔존이다."""

    def setUp(self) -> None:
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="gate-list-")
        self.addCleanup(self.temp.cleanup)
        self.td: Path = Path(self.temp.name)

    def repo(self, name: str, extra: str = "") -> Path:
        repo: Path = self.td / name
        shutil.copytree(_PREGATE_MINI, repo)
        _write(repo, "application/orders/domain_layer/order_roster/__init__.py", "")
        _write(repo, "application/orders/domain_layer/order_roster/order_roster.py",
               "class OrderRoster:\n    def next_tally_scalar(self) -> int:\n        return 1\n")
        for rel in ("application/library/__init__.py", "application/library/domain_layer/__init__.py",
                    "application/library/domain_layer/search_term_glossary/__init__.py",
                    "framework/__init__.py", "framework/pure/__init__.py"):
            _write(repo, rel, "")
        _write(repo, "application/library/domain_layer/search_term_glossary/search_term_glossary.py",
               "class SearchTermGlossary:\n    pass\n")
        _write(repo, _PURE_REL, _PURE_SRC + extra)
        _git(repo, "init", "-q")
        _commit_all(repo, "anchor")
        return repo

    def test_V1_deleting_a_bc_only_shrinks_the_untouched_pure_list(self) -> None:
        repo: Path = self.repo("v1")
        shutil.rmtree(repo / "application" / "library")
        code, out = _gate(repo, "HEAD")
        self.assertEqual(code, 0, out)
        self.assertIn("목록만 줄어 잔존으로 센 줄 1건", out)
        self.assertIn("↳ 앵커: check-business-vocabulary.py :: [#562] framework/pure/json_value.py: pure/ 에 업무 어휘 "
                      "['glossary', 'roster', 'scalar', 'tally']", out)
        self.assertIn("== ⓓ 신규(N′∖L′) 0건 · legacy 1건 · 해소 0건", out)
        self.assertIn("  legacy check-business-vocabulary.py: 1", out)
        self.assertIn("  목록만 줄어 legacy 로 센 ⓓ 줄 1건", out)
        self.assertIn("↳ 앵커: check-business-vocabulary.py :: [ⓓ#448] framework/pure/json_value.py: framework 파일에 업무 어휘 "
                      "['glossary', 'roster', 'scalar', 'tally']", out)

    def test_V3_lists_longer_than_five_words_are_not_cut(self) -> None:
        repo: Path = self.repo("v3", '\n\nclass NextOrderSearchTerm:\n    """x."""\n')
        shutil.rmtree(repo / "application" / "library")
        code, out = _gate(repo, "HEAD")
        self.assertEqual(code, 0, out)
        self.assertIn("['glossary', 'next', 'order', 'roster', 'scalar', 'search', 'tally', 'term']", out)

    def test_V4_V5_A1_C3_growth_swap_and_edited_file_stay_attributed(self) -> None:
        def edit(repo: Path, replace: "tuple[str, str] | None", append: str, delete_bc: bool) -> None:
            path: Path = repo / _PURE_REL
            text: str = path.read_text(encoding="utf-8")
            if replace is not None:
                text = text.replace(*replace)
            path.write_text(text + append, encoding="utf-8")
            if delete_bc:
                shutil.rmtree(repo / "application" / "library")
        variants = {
            "v4-growth": (None, "\n\nclass TallyTerm:\n    pass\n", False),
            "v5-swap": (None, "\n\nclass TallyOrder:\n    pass\n", True),
            "a1-edited-same-words": (None, "\n\nclass TallyScalarRoster:\n    pass\n", True),
            "c3-edited-shrunk": (("Glossary[str, \"TallyValue\"]", "dict[str, \"TallyValue\"]"),
                                 "\n\ndef tally_scalar_roster(value: TallyScalar) -> Roster[TallyScalar]:\n    return [value]\n", False),
        }
        for name, (replace, append, delete_bc) in variants.items():
            with self.subTest(name=name):
                repo: Path = self.repo(name)
                edit(repo, replace, append, delete_bc)
                code, out = _gate(repo, "HEAD")
                self.assertEqual(code, 2, out)
                self.assertIn("[#562] framework/pure/json_value.py", _section(out, "귀속(N∖L)"))
                self.assertNotIn("목록만 줄어", out)

    def test_list_shrunk_pairs_one_to_one_only_for_file_level_string_lists(self) -> None:
        gate: ModuleType = _gate_module()
        old: str = "c.py :: [#562] f/x.py: 업무 어휘 ['a', 'b', 'c'] — 끝"
        self.assertEqual(gate._list_shrunk(["c.py :: [#562] f/x.py: 업무 어휘 ['a', 'c'] — 끝",
                                            "c.py :: [#562] f/x.py: 업무 어휘 ['b'] — 끝"], [old]),
                         {"c.py :: [#562] f/x.py: 업무 어휘 ['a', 'c'] — 끝": old})
        self.assertEqual(gate._list_shrunk(["c.py :: [#616] f/x.py:N: 애그리거트 ['A'] — 끝"],
                                           ["c.py :: [#616] f/x.py:N: 애그리거트 ['A', 'B'] — 끝"]), {})
        self.assertEqual(gate._list_shrunk(["c.py :: [#562] f/x.py: 업무 어휘 ['a', 'd'] — 끝"], [old]), {})
        self.assertEqual(gate._list_shrunk(["c.py :: [#562] f/x.py: 수 [1] — 끝"], ["c.py :: [#562] f/x.py: 수 [1, 2] — 끝"]), {})


# 숨김 뺀 앵커 · 임시 사본 뿌리 바로 앞 배포판(dddjango 2.24.2) — «판정이 옛 판과 같음» 대조의 옛 판(HEAD 금지).
_RELEASED_2242_COMMIT: str = "2119e502"


def _released_gate(td: Path, commit: str) -> Path:
    """배포 커밋의 scripts 트리 사본의 registry_gate.py — 게이트와 공용 모듈(anchor_diff) 모두 그 판이다."""
    dest: Path = td / f"released-{commit}"
    if not dest.exists():
        dest.mkdir()
        archive: "subprocess.CompletedProcess[bytes]" = subprocess.run(
            ["git", "-C", str(ROOT), "archive", commit, "dddjango/scripts"], capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)
    return dest / "dddjango" / "scripts" / "registry_gate.py"


def _anchor_module() -> ModuleType:
    """시험 대상 scripts 트리의 anchor_diff(게이트가 import 하는 그 모듈)."""
    _gate_module()
    import anchor_diff  # noqa: PLC0415 — `_gate_module` 이 scripts 폴더를 sys.path 에 넣은 뒤
    return anchor_diff


class HiddenAnchorGateRegression(unittest.TestCase):
    """앵커 · 출처 스냅숏이 숨김 경로(실행 기록)를 뺀다 — 지금 쪽 사본과 같은 표면. 숨김 기록이 판정에 닿지 않는 저장소와
    남길 링크가 뺀 경로를 지나는 저장소(되돌림)에서 exit · 출력 · sidecar 가 2.24.2 와 같다."""

    def setUp(self) -> None:
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="gate-hidden-")
        self.addCleanup(self.temp.cleanup)
        self.td: Path = Path(self.temp.name)
        self.old: Path = _released_gate(self.td, _RELEASED_2242_COMMIT)

    def same_as_released(self, repo: Path, anchor: str, extra: "list[str] | None" = None) -> str:
        new_side: Path = self.td / "new-introduced.json"
        old_side: Path = self.td / "old-introduced.json"
        code: int
        out: str
        old_code: int
        old_out: str
        code, out = _gate(repo, anchor, [*(extra or []), "--introduced-json", str(new_side)])
        old_code, old_out = _gate(repo, anchor, [*(extra or []), "--introduced-json", str(old_side)], gate=self.old)
        self.assertNotIn("Traceback", out)
        self.assertEqual((code, _mask(out)), (old_code, _mask(old_out)))
        self.assertEqual(_mask_sidecar(new_side), _mask_sidecar(old_side))
        return out

    @staticmethod
    def records(repo: Path) -> None:
        """커밋된 실행 기록 꼴 — 숨김 폴더(문서 입력 · 그 밖 기록 · CI 설정) + 숨김 항목만 든 숨김 아닌 폴더 셋
        (`<project>/logs/.gitkeep` · 비계만 만든 BC · 숨김 폴더만 든 폴더 — 지금 쪽 사본에는 빈 폴더로 있다)."""
        for rel, src in {".dddjango/20261020-run/scope.md": "# 범위\n", ".dddjango/20261020-run/design-spec.md": "# 설계\n",
                         ".dddjango/20261020-run/notes/log.txt": "log\n",
                         ".dddjango-web/20261016-run/captures/result.txt": "captured\n",
                         ".dddjango-web/20261016-run/design-ref/page.html": "<p>ref</p>\n",
                         ".github/workflows/ci.yml": "on: push\n", "config/logs/.gitkeep": "",
                         "application/payments/.gitkeep": "", "application/orders/notes/.cache/f": "cache\n"}.items():
            _write(repo, rel, src)

    def test_A1_committed_records_leave_the_verdict_and_sidecar_unchanged(self) -> None:
        repo: Path
        repo, _pre = _make_repo(self.td, "a1")
        self.records(repo)
        anchor: str = _commit_all(repo, "anchor with records")
        _plant_violation(repo)
        out: str = self.same_as_released(repo, anchor)
        self.assertIn("schema_smoke", _section(out, "귀속(N∖L)"))

    def test_A1_provenance_snapshots_with_records_prove_the_same_inflow(self) -> None:
        def main_step(r: Path) -> None:
            _plant_violation(r)
            self.records(r)
        repo: Path
        anchor: str
        merge: str
        repo, anchor, merge = _lane_merge_repo(self.td, "a1p", main_step, anchor_step=self.records)
        out: str = self.same_as_released(repo, anchor, ["--approved-merge-file", str(_approved(self.td, "a1p", merge))])
        self.assertIn("귀속(N∖L) 0건", out)

    def test_A6_a_kept_link_through_a_dropped_path_extracts_everything_like_released(self) -> None:
        repo: Path
        repo, _pre = _make_repo(self.td, "a6")
        _write(repo, ".h/shared_constants.py", "LIMIT: int = 3\n")
        os.symlink("../../.h/shared_constants.py", repo / "application" / "orders" / "shared_constants.py")
        anchor: str = _commit_all(repo, "anchor with a link into a hidden folder")
        _plant_violation(repo)
        self.same_as_released(repo, anchor)


class TempRootRegression(unittest.TestCase):
    """임시 사본 뿌리 `<TMPDIR>/dddjango/` — 시작 때 쓸기(주인 · keep · 이름 판정) · 뿌리 확인 · pre-gate `--keep` ·
    `--temp-report`. 모두 시험 전용 TMPDIR 에서 돈다(실제 임시 폴더의 사본을 건드리지 않는다)."""

    def setUp(self) -> None:
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="gate-temp-root-")
        self.addCleanup(self.temp.cleanup)
        self.td: Path = Path(self.temp.name)
        self.tmp: Path = self.td / "tmp"
        self.tmp.mkdir()
        self.root: Path = self.tmp / "dddjango"
        self.repo: Path
        self.anchor: str
        self.repo, self.anchor = _make_repo(self.td, "repo")
        _plant_violation(self.repo)
        self.ad: ModuleType = _anchor_module()

    def env(self) -> "dict[str, str]":
        return dict(_scrubbed_env(), TMPDIR=str(self.tmp))

    def gate(self, *args: str) -> "subprocess.CompletedProcess[str]":
        return subprocess.run([sys.executable, str(GATE), *args], capture_output=True, text=True, env=self.env())

    @staticmethod
    def dead_pid() -> int:
        proc: "subprocess.Popen[bytes]" = subprocess.Popen([sys.executable, "-c", "pass"])
        proc.wait()
        return proc.pid

    def make_root(self, mode: int = 0o700) -> None:
        self.root.mkdir()
        self.root.chmod(mode)

    @staticmethod
    def folder(where: Path, name: str, owner: "dict[str, object] | None", size: int = 1024) -> Path:
        path: Path = where / name
        (path / "current").mkdir(parents=True)
        (path / "current" / "blob").write_bytes(b"x" * size)
        if owner is not None:
            (path / "owner.json").write_text(json.dumps(owner), encoding="utf-8")
        return path

    def test_B1_to_B6_start_sweep_removes_only_folders_whose_owner_is_gone(self) -> None:
        dead: int = self.dead_pid()
        self.assertTrue(self.ad._pid_dead(dead))
        live: int = os.getpid()
        self.make_root()
        gone: "list[Path]" = [
            self.folder(self.root, f"registry-gate-{live}-b1aaaaaa", {"pid": dead, "tool": "registry-gate"}),  # B1 표식 pid 죽음
            self.folder(self.root, f"anchor-diff-{dead}-b4aaaaaa", None),                                      # B4 표식 없음 · 이름 pid 죽음
            self.folder(self.root, f"design-pregate-{live}-b6aaaaaa-sweeping-{dead}", None),                    # B6 쓸던 실행이 죽음
            self.folder(self.root, f"registry-gate-1-b6bbbbbb-sweeping-{live}-sweeping-{dead}", None),          # B6 이름에 둘 — 마지막 pid
        ]
        stay: "list[Path]" = [
            self.folder(self.root, f"registry-gate-{dead}-b2aaaaaa", {"pid": live}),                             # B2 산 주인(표식이 이름보다 먼저)
            self.folder(self.root, f"design-pregate-{dead}-b3aaaaaa", {"pid": dead, "keep": True}),              # B3 keep
            self.folder(self.root, "notes", None),                                                              # B5 이름 해석 불가
            self.folder(self.root, f"other-tool-{dead}-b5aaaaaa", None),                                        # B5 모르는 도구
            self.folder(self.root, f"registry-gate-{dead}-b5bbbbbb", None),                                     # (표식 깨짐 → 아래)
            self.folder(self.root, f"registry-gate-{dead}-b6cccccc-sweeping-{live}", None),                     # B6 쓰는 중(산 pid)
        ]
        (stay[4] / "owner.json").write_text("{깨진 표식", encoding="utf-8")                                     # B5 읽기 실패
        locked: Path = gone[0] / "current" / "locked"                                                             # 읽기 전용 하위 폴더도 지운다
        locked.mkdir()
        (locked / "x").write_bytes(b"x" * 2048)
        locked.chmod(0o500)
        (self.root / "stray.txt").write_text("x", encoding="utf-8")
        run: "subprocess.CompletedProcess[str]" = self.gate(str(self.repo), "--anchor", self.anchor)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertEqual([p.name for p in gone if os.path.lexists(p)], [])
        self.assertEqual([p.name for p in stay if not p.is_dir()], [])
        self.assertTrue((self.root / "stray.txt").is_file())
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), sorted([p.name for p in stay] + ["stray.txt"]))
        notes: "list[str]" = [line for line in run.stderr.splitlines() if line.startswith("정리:")]
        self.assertEqual(len(notes), 1, run.stderr)
        self.assertRegex(notes[0], rf"^정리: 끊긴 실행이 남긴 임시 사본 4개\([0-9.]+ MB\)를 지웠다 — {re.escape(str(self.root))}$")
        self.assertNotIn("정리:", run.stdout)
        # 차지할 때 이름은 «첫 `-sweeping-` 앞 원래 이름 + `-sweeping-<내 pid>`» — 다시 차지해도 길어지지 않는다
        self.assertEqual(self.ad._claim_name("registry-gate-1-abcdefgh", 77), "registry-gate-1-abcdefgh-sweeping-77")
        self.assertEqual(self.ad._claim_name("registry-gate-1-abcdefgh-sweeping-5-sweeping-6", 77),
                         "registry-gate-1-abcdefgh-sweeping-77")

    def test_B7_a_root_that_is_a_link_not_0700_or_not_mine_is_not_used(self) -> None:
        dead: int = self.dead_pid()
        elsewhere: Path = self.td / "elsewhere"
        elsewhere.mkdir(mode=0o700)
        planted: Path = self.folder(elsewhere, f"registry-gate-{dead}-b7aaaaaa", {"pid": dead})
        self.root.symlink_to(elsewhere)
        run: "subprocess.CompletedProcess[str]" = self.gate(str(self.repo), "--anchor", self.anchor)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertTrue(planted.is_dir())
        self.assertNotIn("정리:", run.stderr)
        self.assertEqual(sorted(p.name for p in elsewhere.iterdir()), [planted.name])
        self.root.unlink()
        self.make_root(0o755)
        planted = self.folder(self.root, f"registry-gate-{dead}-b7bbbbbb", {"pid": dead})
        run = self.gate(str(self.repo), "--anchor", self.anchor)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertTrue(planted.is_dir())
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), [planted.name])
        self.root.chmod(0o700)
        with patch.object(tempfile, "tempdir", str(self.tmp)):
            self.assertEqual(self.ad.temp_root(), self.root)
            with patch.object(os, "getuid", return_value=os.getuid() + 1):
                self.assertIsNone(self.ad.temp_root())
                with self.ad.owned_tempdir("registry-gate") as fallback:
                    self.assertEqual(Path(fallback).parent, self.tmp)
                    self.assertFalse((Path(fallback) / "owner.json").exists())
            with self.ad.owned_tempdir("registry-gate") as owned:
                self.assertEqual(Path(owned).parent, self.root)
                self.assertRegex(Path(owned).name, rf"^registry-gate-{os.getpid()}-")
                self.assertEqual(json.loads((Path(owned) / "owner.json").read_text(encoding="utf-8"))["pid"], os.getpid())

    def test_B9_pregate_keep_copy_survives_the_next_sweep(self) -> None:
        from pregate_fixture_run import _make_repo as _pregate_repo  # noqa: PLC0415
        repo: Path = _pregate_repo(self.td, "pregate")
        spec: Path = ROOT / "workspace" / "eval" / "fixtures" / "pregate" / "green-spec.md"
        pregate: "list[str]" = [sys.executable, str(GATE.parent / "design_pregate.py"), str(spec), str(repo)]
        run: "subprocess.CompletedProcess[str]" = subprocess.run(pregate, capture_output=True, text=True, env=self.env())
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(list(self.root.iterdir()), [])
        run = subprocess.run(pregate + ["--keep"], capture_output=True, text=True, env=self.env())
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        kept: Path = Path(re.search(r"\(--keep\) 격리 사본 보존: (\S+)", run.stdout).group(1))  # type: ignore[union-attr]
        self.addCleanup(shutil.rmtree, kept, True)
        self.assertEqual(kept.parent, self.root)
        self.assertRegex(kept.name, r"^design-pregate-\d+-")
        self.assertIs(json.loads((kept / "owner.json").read_text(encoding="utf-8"))["keep"], True)
        self.assertEqual(self.gate(str(self.repo), "--anchor", self.anchor).returncode, 2)
        self.assertTrue((kept / "copy").is_dir())

    def test_B10_temp_report_counts_without_target_and_deletes_nothing(self) -> None:
        run: "subprocess.CompletedProcess[str]" = self.gate("--temp-report")
        self.assertEqual((run.returncode, run.stdout, run.stderr), (0, "임시 사본: 남은 것 0\n", ""))
        self.assertFalse(os.path.lexists(self.root))
        dead: int = self.dead_pid()
        self.make_root()
        mib: int = 1024 * 1024
        planted: "list[Path]" = [
            self.folder(self.root, f"registry-gate-{os.getpid()}-b10aaaaa", {"pid": os.getpid()}, 2 * mib),
            self.folder(self.root, f"registry-gate-{dead}-b10bbbbb", {"pid": dead}, mib),
            self.folder(self.root, f"design-pregate-{dead}-b10ccccc", {"pid": dead, "keep": True}, mib),
        ]
        # 2.24.2 가 남기던 꼴 — registry_gate(`current/` + `anchor/` 또는 `records-*.jsonl`) · anchor_diff(`anchor/` · `tree-*`
        # 뿐) · pre-gate(`design-pregate-*/copy/`). 흔한 이름 하나(`current/` 만 · `copy/` 없는 pre-gate 이름)는 세지 않는다.
        old_gate: Path = self.folder(self.tmp, "tmpb10old1", None, 3 * mib)
        (old_gate / "anchor").mkdir()
        old_records: Path = self.folder(self.tmp, "tmpb10old2", None)
        (old_records / "records-current.jsonl").write_bytes(b"{}\n" * 10)
        old_anchor: Path = self.tmp / "tmpb10old3"
        (old_anchor / "anchor").mkdir(parents=True)
        (old_anchor / "tree-0123456789ab").mkdir()
        old_pregate: Path = self.tmp / "design-pregate-b10old4"
        (old_pregate / "copy").mkdir(parents=True)
        recent: Path = self.folder(self.tmp, "tmpb10recent", None)
        (recent / "anchor").mkdir()
        unrelated: Path = self.folder(self.tmp, "tmpb10other", None)
        (unrelated / "current").rename(unrelated / "something")
        current_only: Path = self.folder(self.tmp, "tmpb10current", None)
        pregate_no_copy: Path = self.tmp / "design-pregate-b10nocopy"
        pregate_no_copy.mkdir()
        two_hours_ago: float = time.time() - 7200
        for folder in (old_gate, old_records, old_anchor, old_pregate, unrelated, current_only, pregate_no_copy):
            for path in [folder, *folder.iterdir()]:
                os.utime(path, (two_hours_ago, two_hours_ago), follow_symlinks=False)
        run = self.gate("--temp-report")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(run.stderr, "")
        self.assertRegex(run.stdout, rf"^임시 사본: 남은 2개\(3\.0 MB — 다른 실행 몫\) · keep 1개\(1\.0 MB\) · "
                                     rf"옛 판 꼴 4개\(0\.0 GB — 직접 지워도 됨\) · {re.escape(str(self.root))}\n$")
        for path in [*planted, old_gate, old_records, old_anchor, old_pregate, recent, unrelated, current_only,
                     pregate_no_copy]:
            self.assertTrue(path.is_dir(), path)

    def test_B11_stdout_and_sidecars_match_the_released_gate_and_the_note_goes_to_stderr_only(self) -> None:
        dead: int = self.dead_pid()
        old: Path = _released_gate(self.td, _RELEASED_2242_COMMIT)

        def leftover(tmp: Path) -> None:
            root: Path = tmp / "dddjango"
            root.mkdir(mode=0o700)
            root.chmod(0o700)
            self.folder(root, f"registry-gate-{dead}-b11aaaaa", {"pid": dead})

        ref: "dict[str, object]" = _par_run(old, self.repo, self.anchor, self.td, None)
        swept: "dict[str, object]" = _par_run(GATE, self.repo, self.anchor, self.td, None, seed=leftover)
        clean: "dict[str, object]" = _par_run(GATE, self.repo, self.anchor, self.td, None)
        for got in (swept, clean):
            self.assertEqual([got[k] for k in ("exit", "stdout", "introduced", "contract")],
                             [ref[k] for k in ("exit", "stdout", "introduced", "contract")])
            self.assertEqual(got["leaked"], [])
        self.assertEqual(clean["stderr"], ref["stderr"])
        extra: "list[str]" = [line for line in str(swept["stderr"]).splitlines()
                              if line not in str(ref["stderr"]).splitlines()]
        self.assertEqual(len(extra), 1, swept["stderr"])
        self.assertTrue(extra[0].startswith("정리: 끊긴 실행이 남긴 임시 사본 1개("), extra[0])


def _unnumbered_debt_rows(td: Path, repo: Path, anchor: str, debt: Path,
                          e_out: str) -> "list[tuple[str, int, int, bool, str]]":
    """E3 · E4 — 번호 없는 줄 빚(`= <검사기 파일> :: <줄>`)을 섞은 목록: 새 게이트와 옛 직렬 게이트 사본
    (`_SERIAL_GATE_COMMIT` — 현행 anchor_diff 를 import)이 E 와 같은 판정 · 같은 출력, 맞을 수 없는 줄은 exit 1."""
    code: int
    out: str
    old_code: int
    old_out: str
    mixed: Path = td / "debt-mixed.txt"
    mixed.write_text(debt.read_text(encoding="utf-8")
                     + "= check-error-centralization.py :: - application/orders/x.py:1: 줄 전체 일치 항목\n",
                     encoding="utf-8")
    rows: "list[tuple[str, int, int, bool, str]]" = []
    code, out = _gate(repo, anchor, ["--legacy-debt-file", str(mixed)])
    rows.append(("E3 번호 없는 줄 섞은 빚 목록", 0, code, _mask(out) == _mask(e_out), "E 와 같은 출력(게이트 차분 집합엔 번호 없는 줄이 없다)"))
    old: "Path | None" = _gate_copy(td, "e3-serial-gate", _SERIAL_GATE_COMMIT)
    assert old is not None
    old_code, old_out = _gate(repo, anchor, ["--legacy-debt-file", str(mixed)], gate=old)
    rows.append(("E3′ 옛 게이트 사본 + 현행 anchor_diff", 0, old_code, _mask(old_out) == _mask(e_out),
                 "load_debt 반환 꼴 호환(옛 사본은 debt_match 에 그대로 넘긴다)"))
    bad: Path = td / "debt-bad.txt"
    bad.write_text("= check-naming.py :: - application/orders/x.py:1: m\n", encoding="utf-8")
    code, out = _gate(repo, anchor, ["--legacy-debt-file", str(bad)])
    rows.append(("E4 맞을 수 없는 번호 없는 줄", 1, code,
                 "사용 오류: 빚 목록 줄 형식 오류: '= check-naming.py :: - application/orders/x.py:1: m' — 번호 없는 줄의 검사기는" in out,
                 "fail-closed 사용 오류"))
    return rows


def main() -> int:
    """스모크 전체를 이 실행 전용 임시 폴더(TMPDIR)에서 돈다 — 게이트의 시작 때 쓸기가 실제 임시 폴더의 다른 실행 사본을
    건드리거나 그 알림 줄이 옛 판 대조 출력에 섞이지 않게."""
    private: str = tempfile.mkdtemp(prefix="gate-smoke-tmp-")
    saved: "str | None" = os.environ.get("TMPDIR")
    os.environ["TMPDIR"] = private
    tempfile.tempdir = private
    try:
        return _main()
    finally:
        tempfile.tempdir = None
        if saved is None:
            os.environ.pop("TMPDIR", None)
        else:
            os.environ["TMPDIR"] = saved
        shutil.rmtree(private, ignore_errors=True)


def _main() -> int:
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(case)
                               for case in (CacheSnapshotRegression, IdempotencySnapshotRegression, SisterGateRegression,
                                            ApprovedInflowGateRegression, SnapshotLinkRegression, ListShrinkRegression,
                                            HiddenAnchorGateRegression, TempRootRegression))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 2
    if not GATE.is_file() or not BASE_FIXTURE.is_dir():
        print("재료 결손: registry_gate.py 또는 skeleton/good_bc fixture 없음", file=sys.stderr)
        return 1
    rows: "list[tuple[str, int, int, bool, str]]" = []  # (케이스, 기대, 실측, 내용검사, 비고)

    with tempfile.TemporaryDirectory() as td_s:
        td: Path = Path(td_s)

        # V — 공허 차분: 앵커=HEAD·clean → exit 1
        repo, anchor = _make_repo(td, "vacuous")
        code, out = _gate(repo, anchor)
        rows.append(("V 공허 차분", 1, code, "공허" in out, "앵커=HEAD·clean"))

        # A — working tree 신규 위반 → 귀속 red
        repo, anchor = _make_repo(td, "attributed")
        (repo / _VIOLATION_REL).parent.mkdir(parents=True, exist_ok=True)
        (repo / _VIOLATION_REL).write_text(_VIOLATION_SRC, encoding="utf-8")
        code, out = _gate(repo, anchor)
        rows.append(("A 귀속 red", 2, code, "schema_smoke" in out.split("legacy 잔존")[0], "신규 위반이 귀속 절에"))

        # B — 앵커에 이미 있던 위반 + 무해 변경 → green + 잔존 보고
        repo, _pre = _make_repo(td, "legacy")
        (repo / _VIOLATION_REL).parent.mkdir(parents=True, exist_ok=True)
        (repo / _VIOLATION_REL).write_text(_VIOLATION_SRC, encoding="utf-8")
        _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "legacy 포함 앵커")
        anchor = _git(repo, "rev-parse", "HEAD").stdout.strip()
        (repo / "docs_note.md").write_text("harmless\n", encoding="utf-8")
        code, out = _gate(repo, anchor)
        rows.append(("B legacy-only green", 0, code, "잔존" in out and "귀속 0건" in out.replace("(N∖L) 0건", "귀속 0건"), "잔존 보고·귀속 0"))

        # Q — ⓓ 앵커 차분(현장 보고 3 ⓔ2): 앵커에 있던 ⓓ 는 legacy(계수만) · working 의 새 ⓓ 는 «ⓓ 신규» 절에
        # 인쇄 · exit 무변(ⓓ 는 exit 불산입). 재료 = `#69` 프로덕션 assert(그 자리는 27종 위반 0 · ⓓ#69 만).
        repo, _pre = _make_repo(td, "cand_anchor")
        _write(repo, "application/orders/domain_layer/order/value_object/legacy_probe.py",
               "_N: int = 1\nassert _N == 1\n")
        _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "legacy ⓓ 포함 앵커")
        anchor = _git(repo, "rev-parse", "HEAD").stdout.strip()
        _write(repo, "application/orders/domain_layer/order/value_object/fresh_probe.py",
               "_M: int = 2\nassert _M == 2\n")
        side_q: Path = td / "introduced_q.json"
        code, out = _gate(repo, anchor, ["--introduced-json", str(side_q)])
        payload_q: dict = json.loads(side_q.read_text(encoding="utf-8")) if side_q.is_file() else {}
        cand_section: str = out.split("== ⓓ 신규", 1)[1] if "== ⓓ 신규" in out else ""
        q_ok: bool = (
            "== ⓓ 신규(N′∖L′) 1건 · legacy 1건" in out
            and "fresh_probe" in cand_section and "legacy_probe" not in cand_section
            and payload_q.get("candidate_lines") and all("fresh_probe" in l for l in payload_q["candidate_lines"])
            and payload_q.get("candidate_records")
            and all(r.get("severity") == "info" and r.get("rule") == "#69" and "fresh_probe.py" in str(r.get("file", ""))
                    for r in payload_q["candidate_records"])  # file 은 `<경로>:<줄>` 형(레코드 계약)
            and payload_q.get("records") == []  # ⓓ 는 records(위반)와 분리
        )
        rows.append(("Q ⓓ 앵커 차분", 0, code, q_ok, "ⓓ 신규 1·legacy 1 · sidecar 분리 키(info #69 · records []) · exit 무변"))
        # Q′ — 같은 재료에 위반을 함께 심으면 exit 2(ⓓ 절은 그대로 · records 는 위반만 · candidate_lines 는 ⓓ 만).
        _plant_violation(repo)
        side_q2: Path = td / "introduced_q2.json"
        code, out = _gate(repo, anchor, ["--introduced-json", str(side_q2)])
        payload_q2: dict = json.loads(side_q2.read_text(encoding="utf-8")) if side_q2.is_file() else {}
        q2_ok: bool = (
            "== ⓓ 신규(N′∖L′) 1건" in out and "schema_smoke" in out
            and payload_q2.get("records") and all("schema_smoke" in str(r.get("file", "")) for r in payload_q2["records"])
            and payload_q2.get("candidate_lines") and all("fresh_probe" in l for l in payload_q2["candidate_lines"])
            and payload_q2.get("candidate_records") and all(r.get("rule") == "#69" for r in payload_q2["candidate_records"])
        )
        rows.append(("Q′ ⓓ + 위반 동반", 2, code, q2_ok, "ⓓ 절 유지 · records 는 위반만 · candidate_lines 는 ⓓ 만"))

        # S — sidecar(T2-3): 귀속 레코드만 담고 legacy 는 구조적으로 배제되는가.
        # 왜 필요한가: 소비자(재생성 루프)가 raw sink 를 직접 읽으면 앵커 실행 레코드까지
        # 섞여 «legacy 잔존은 이 빌드에서 즉석 수리하지 않는다» 규율을 깨뜨린다(적대 리뷰
        # AM#3·AN#3). 게이트가 L/N 을 다른 sink 로 받고 N∖L 에 해당하는 레코드만 낸다.
        repo, _pre = _make_repo(td, "sidecar")
        (repo / _VIOLATION_REL).parent.mkdir(parents=True, exist_ok=True)
        (repo / _VIOLATION_REL).write_text(_VIOLATION_SRC, encoding="utf-8")
        _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "legacy 포함 앵커")
        anchor = _git(repo, "rev-parse", "HEAD").stdout.strip()
        fresh: Path = repo / "application" / "orders" / "domain_layer" / "fresh_svc.py"
        fresh.parent.mkdir(parents=True, exist_ok=True)
        fresh.write_text("NEWCACHE = {}\n", encoding="utf-8")
        side: Path = td / "introduced.json"
        code, out = _gate(repo, anchor, ["--introduced-json", str(side)])
        payload: dict = json.loads(side.read_text(encoding="utf-8")) if side.is_file() else {}
        recs: "list[dict]" = payload.get("records", [])
        side_ok: bool = (
            bool(recs)
            and all("fresh_svc" in str(r.get("file", "")) for r in recs)      # 신규만
            and not any("schema_smoke" in str(r.get("file", "")) for r in recs)  # legacy 배제
            and not any(str(r.get("file", "")).startswith("/") for r in recs)    # 경로 정규화
            and not payload.get("unmatched_lines")                            # 전건 매칭
        )
        rows.append(("S sidecar 귀속만", 2, code, side_ok,
                     "legacy 배제·스냅숏 경로 정규화·대응없는 귀속 0"))

        # C — A1 공격: 위반을 «선커밋»(앵커 이후) 후 무해 파일만 working 에
        repo, anchor = _make_repo(td, "precommit")
        (repo / _VIOLATION_REL).parent.mkdir(parents=True, exist_ok=True)
        (repo / _VIOLATION_REL).write_text(_VIOLATION_SRC, encoding="utf-8")
        _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "위반 선커밋")
        (repo / "docs_note.md").write_text("harmless\n", encoding="utf-8")
        code, out = _gate(repo, anchor)
        rows.append(("C 선커밋 공격", 2, code, "schema_smoke" in out, "HEAD 안 위반도 앵커 차분에 잡힘"))

        # D — A2 공격: 골격 고정 칸 삭제(부재 위반 — 경로가 존재하지 않음)
        repo, anchor = _make_repo(td, "absence")
        shutil.rmtree(repo / "application" / "orders" / "composition_root")
        code, out = _gate(repo, anchor)
        rows.append(("D 골격 접힘 공격", 2, code, "composition_root" in out, "부재 위반 귀속"))

        # E — 빚 채널: A 케이스 위반을 승인 목록으로 → green + 빚 절
        repo, anchor = _make_repo(td, "debt")
        (repo / _VIOLATION_REL).parent.mkdir(parents=True, exist_ok=True)
        (repo / _VIOLATION_REL).write_text(_VIOLATION_SRC, encoding="utf-8")
        debt: Path = td / "debt.txt"
        debt.write_text(
            "// 승인: 스모크 빚 — 같은 파일에 발화하는 태그 셋 전부(#95 격리·#96 잎·#490 트리 밖 파일)\n"
            "#95 schema_smoke\n#96 schema_smoke\n#490 schema_smoke\n",
            encoding="utf-8",
        )
        code, out = _gate(repo, anchor, ["--legacy-debt-file", str(debt)])
        rows.append(("E 빚 채널", 0, code, "이관 빚" in out and "schema_smoke" in out, "exit 제외·보고 필수"))
        rows.extend(_unnumbered_debt_rows(td, repo, anchor, debt, out))

        # U — usage 오류: 알 수 없는 flag → 문면 계약 exit 1(F3 — argparse 기본 2 봉합).
        proc: "subprocess.CompletedProcess[str]" = subprocess.run(
            [sys.executable, str(GATE), str(repo), "--nope"],
            capture_output=True, text=True, env=_scrubbed_env(),
        )
        rows.append((
            "U usage exit 1", 1, proc.returncode,
            "사용 오류" in (proc.stdout + proc.stderr),
            "usage 오류는 exit 1(F3)",
        ))

        # ── provenance 차분(승인 유입 채널) ──────────────────────────────────────────
        inflow_title: str = "승인 유입"
        titles_new: "tuple[str, ...]" = ("== 승인 유입", "== provenance 진단", "↳ 귀속 유지")

        # P0 — flag 없음: 현행 판형 + 새 절 부재 + flag 유/무 불변식 3종 + 수리 전 사본과 정규화 byte 동일.
        repo, anchor, m_sha = _lane_merge_repo(td, "p0", _plant_violation)
        side0: Path = td / "p0-introduced.json"
        code0, out0 = _gate(repo, anchor, ["--introduced-json", str(side0)])
        side0f: Path = td / "p0f-introduced.json"
        code0f, out0f = _gate(repo, anchor, ["--approved-merge-file", str(_approved(td, "p0", m_sha)),
                                             "--introduced-json", str(side0f)])
        attributed0: "set[str]" = _lines_of(out0, "귀속(N∖L)")
        union_f: "set[str]" = _lines_of(out0f, "귀속(N∖L)") | _lines_of(out0f, inflow_title)
        invariants: bool = (
            not any(t in out0 for t in titles_new)
            and _section(out0, "legacy 잔존") == _section(out0f, "legacy 잔존")
            and re.search(r"legacy 잔존\(L∩N\) \d+건 · 해소\(L∖N\) \d+건", out0).group(0)  # type: ignore[union-attr]
            == re.search(r"legacy 잔존\(L∩N\) \d+건 · 해소\(L∖N\) \d+건", out0f).group(0)  # type: ignore[union-attr]
            and attributed0 == union_f and len(attributed0) == 3 and code0f == 0
        )
        rows.append(("P0 flag 없음 현행", 2, code0, "귀속(N∖L) 3건" in out0 and invariants,
                     "새 절 부재·legacy/해소 동일·(귀속∪유입) 동일"))
        pre_gate: "Path | None" = _pre_repair_gate(td)
        if pre_gate is None:
            print(f"재료 결손: 수리 전 사본({_PRE_REPAIR_COMMIT}) archive 실패", file=sys.stderr)
            return 1
        side0p: Path = td / "p0p-introduced.json"
        code0p, out0p = _gate(repo, anchor, ["--introduced-json", str(side0p)], gate=pre_gate)
        rows.append(("P0′ 수리 전 사본 byte 동일 + 안내", 2, code0p,
                     len([l for l in out0.splitlines() if l.startswith("안내:")]) == 1
                     and _mask("\n".join(l for l in out0.splitlines() if not l.startswith("안내:"))) == _mask(out0p)
                     and _mask_sidecar(side0) == _mask_sidecar(side0p),
                     f"툴체인 행·sidecar 식별자 마스킹 후 diff 0(사본 {_PRE_REPAIR_COMMIT})"))

        # P1 — 목록={M} → 유입 3(파일)·귀속 0·exit 0·sidecar attributed_lines=[]
        side1: Path = td / "p1-introduced.json"
        code, out = _gate(repo, anchor, ["--approved-merge-file", str(_approved(td, "p1", m_sha)),
                                         "--introduced-json", str(side1)])
        payload1: dict = json.loads(side1.read_text(encoding="utf-8")) if side1.is_file() else {}
        rows.append(("P1 승인 유입", 0, code,
                     f"{inflow_title}(" in out and "3건 ==" in out.split("== 승인 유입")[1].split("\n")[0]
                     and out.count("↳ 유입: " + m_sha[:12] + "(L 증명) · 파일 verbatim") == 3
                     and "귀속(N∖L) 0건" in out and payload1.get("attributed_lines") == []
                     and len(payload1.get("provenance", {}).get("inflow_lines", [])) == 3,
                     "파일 verbatim 3·귀속 0·sidecar 잔여 0"))

        # P7 — 빚+유입 공존: #95 는 빚 절(빚 우선), 나머지 2 는 유입.
        debt7: Path = td / "p7-debt.txt"
        debt7.write_text("#95 schema_smoke\n", encoding="utf-8")
        code, out = _gate(repo, anchor, ["--approved-merge-file", str(_approved(td, "p7", m_sha)),
                                         "--legacy-debt-file", str(debt7)])
        rows.append(("P7 빚+유입 공존", 0, code,
                     "이관 빚(승인 목록 매칭 — exit 제외·기록 의무) 1건" in out
                     and "[#95]" in _section(out, "이관 빚") and "[#95]" not in _section(out, inflow_title)
                     and out.count("↳ 유입:") == 2 and "귀속(N∖L) 0건" in out,
                     "빚 1(#95)·유입 2·귀속 0"))

        # P3ⓐ — 빈 목록: 마지막 접촉 커밋 = M(미승인) → 누락 SHA 표면화 · 귀속 3
        code, out = _gate(repo, anchor, ["--approved-merge-file", str(_approved(td, "p3a"))])
        rows.append(("P3ⓐ 빈 목록", 2, code,
                     out.count(f"↳ 귀속 유지: 미승인 머지 경유 {m_sha[:12]}") == 3
                     and f"미승인 머지: {m_sha[:12]}" in out, "누락 SHA 표면화"))

        # P2 — 머지 뒤 lane 이 위반 파일을 «커밋»으로 수정 → 레인 커밋 수정 / P2w 미커밋 → worktree 수정 중
        _write(repo, _VIOLATION_REL, _VIOLATION_SRC + "_M: int = 1\n")
        lane_fix: str = _commit_all(repo, "lane edits violation file")
        code, out = _gate(repo, anchor, ["--approved-merge-file", str(_approved(td, "p2", m_sha))])
        rows.append(("P2 레인 커밋 수정", 2, code,
                     out.count(f"↳ 귀속 유지: 레인 커밋 수정 {lane_fix[:12]}(승인 머지 {m_sha[:12]} 이후)") == 3
                     and "귀속(N∖L) 3건" in out, "F1 탈락(HEAD blob ≠ M blob)"))
        _write(repo, _VIOLATION_REL, _VIOLATION_SRC + "_M: int = 2\n")
        code, out = _gate(repo, anchor, ["--approved-merge-file", str(_approved(td, "p2w", m_sha))])
        rows.append(("P2w worktree 수정 중", 2, code,
                     out.count("↳ 귀속 유지: worktree 수정 중") == 3, "W 탈락"))
        _git(repo, "checkout", "-q", "--", _VIOLATION_REL)

        # P2′ — 양쪽 수정 → 충돌 해소 M(blob(M) ≠ blob(M^2)) → 충돌 해소분
        def _anchor_base(r: Path) -> None:
            _write(r, _VIOLATION_REL, "_BASE: int = 0\n")

        def _lane_edit(r: Path) -> None:
            _write(r, _VIOLATION_REL, "_BASE: int = 1  # lane\n")

        def _main_edit(r: Path) -> None:
            _write(r, _VIOLATION_REL, _VIOLATION_SRC)

        repo2, anchor2 = _make_repo(td, "p2c")
        _anchor_base(repo2)
        anchor2 = _commit_all(repo2, "anchor+")
        _git(repo2, "checkout", "-q", "-b", "lane")
        _lane_edit(repo2)
        _commit_all(repo2, "lane edit")
        _git(repo2, "checkout", "-q", "main")
        _main_edit(repo2)
        _commit_all(repo2, "main violation")
        _git(repo2, "checkout", "-q", "lane")
        conflict: "subprocess.CompletedProcess[str]" = _git(repo2, "merge", "--no-ff", "-m", "M resolved", "main")
        _write(repo2, _VIOLATION_REL, _VIOLATION_SRC + "_BASE: int = 1  # lane\n")  # 해소분 = 양쪽 합성
        m2c: str = _commit_all(repo2, "M resolved")
        parents2: "list[str]" = _git(repo2, "show", "-s", "--format=%P", m2c).stdout.split()
        code, out = _gate(repo2, anchor2, ["--approved-merge-file", str(_approved(td, "p2c", m2c))])
        rows.append(("P2′ 충돌 해소분", 2, code,
                     conflict.returncode != 0 and len(parents2) == 2 and "귀속(N∖L) 2건" in out
                     and out.count(f"↳ 귀속 유지: 충돌 해소분(M≠M^2) — {m2c[:12]}") == 2,
                     "blob(M)≠blob(M^2) → 귀속 유지(#490 은 앵커 기존분 — 신규 2)"))

        # P3 — ⓑ 비머지 SHA ⓒ 사슬 밖 ⓓ 앵커 이전 머지 (ⓐ 빈 목록은 P2 앞에서 — 레인 후속 커밋 전 상태)
        code, out = _gate(repo, anchor, ["--approved-merge-file", str(_approved(td, "p3b", lane_fix))])
        rows.append(("P3ⓑ 비머지 SHA", 1, code, "부모가 1개" in out, "형식 오류 exit 1"))
        # ⓒ 사슬 밖: main 이 다른 가지를 머지한 커밋(lane 이 받지 않음)
        _git(repo, "checkout", "-q", "main")
        _git(repo, "checkout", "-q", "-b", "other")
        _write(repo, "other_note.md", "other\n")
        _commit_all(repo, "other work")
        _git(repo, "checkout", "-q", "main")
        _git(repo, "merge", "-q", "--no-ff", "-m", "main merges other", "other")
        m_other: str = _head(repo)
        _git(repo, "checkout", "-q", "lane")
        code, out = _gate(repo, anchor, ["--approved-merge-file", str(_approved(td, "p3c", m_other))])
        rows.append(("P3ⓒ 사슬 밖", 1, code, "사슬 밖" in out, "레인이 받지 않은 머지"))
        # ⓓ 앵커 이전 머지 → 판정 불참(목록 유효) · M 미승인 → 귀속 3
        def _anchor_with_prior_merge(r: Path) -> None:
            _git(r, "checkout", "-q", "-b", "x")
            _write(r, "x_note.md", "x\n")
            _commit_all(r, "x work")
            _git(r, "checkout", "-q", "main")
            _git(r, "merge", "-q", "--no-ff", "-m", "M0 prior merge", "x")
            _write(r, "anchor_note.md", "anchor\n")

        repo3, anchor3, m3 = _lane_merge_repo(td, "p3d", _plant_violation, anchor_step=_anchor_with_prior_merge)
        m0: str = _git(repo3, "rev-parse", f"{anchor3}^").stdout.strip()
        code, out = _gate(repo3, anchor3, ["--approved-merge-file", str(_approved(td, "p3d", m0))])
        rows.append(("P3ⓓ 앵커 이전 머지", 2, code,
                     f"[M {m0[:12]}]" in out and "앵커 이전 — 판정 불참" in out
                     and out.count(f"↳ 귀속 유지: 미승인 머지 경유 {m3[:12]}") == 3, "판정 불참·귀속 3"))

        # P4 — 상호작용: 앵커에 framework/redis(리터럴 "promotion") · main 이 promotion BC → M
        repo4, anchor4, m4 = _lane_merge_repo(td, "p4", _make_promotion_bc, anchor_step=_plant_redis)
        code, out = _gate(repo4, anchor4, ["--approved-merge-file", str(_approved(td, "p4", m4))])
        sec4: str = _section(out, inflow_title)
        rows.append(("P4 상호작용 승인 유입", 0, code,
                     "귀속(N∖L) 0건" in out and "[#416]" in sec4
                     and re.search(r"\[#416\][^\n]*\n\s+↳ 유입: " + m4[:12] + r"\(L 증명\) · 상호작용", out) is not None
                     and re.search(r"\[M " + m4[:12] + r"\][^\n]*· 상호작용 1$", out, re.M) is not None,
                     "#416 = 상호작용(파일 무변·L 증명)·귀속 0"))
        code, out = _gate(repo4, anchor4, ["--approved-merge-file", str(_approved(td, "p4p"))])
        rows.append(("P4′ 상호작용 미증명", 2, code,
                     re.search(r"\[#416\][^\n]*\n\s+↳ 귀속 유지: 상호작용 미증명", out) is not None,
                     "목록 비움 → 귀속 유지"))

        # P5 — kkebi 형: main 직접 커밋 X(위반) 뒤 lane 분기 · main 무해 커밋 · lane 머지 M
        repo5, anchor5 = _make_repo(td, "p5")
        _plant_violation(repo5)
        x_sha: str = _commit_all(repo5, "X direct violation on main")
        _git(repo5, "checkout", "-q", "-b", "lane")
        _git(repo5, "checkout", "-q", "main")
        _write(repo5, "harmless.md", "h\n")
        _commit_all(repo5, "main harmless")
        _git(repo5, "checkout", "-q", "lane")
        _git(repo5, "merge", "-q", "--no-ff", "-m", "M merge main", "main")
        m5: str = _head(repo5)
        code, out = _gate(repo5, anchor5, ["--approved-merge-file", str(_approved(td, "p5", m5))])
        rows.append(("P5 kkebi 형 직접 커밋", 2, code,
                     out.count(f"↳ 귀속 유지: 비머지 커밋 경유 {x_sha[:12]}") == 3
                     and f"진단: 비머지 커밋 1건({x_sha[:12]})이 첫 승인 머지보다 앞선다" in out,
                     "비머지 경유·진단 1행"))

        # P6 — 이중 원인: lane 이 promotion BC 신설 · main 이 redis 파일에 리터럴 추가 → M 승인
        def _redis_plain(r: Path) -> None:
            _plant_redis(r, "import redis\n\n_R: str = redis.__name__\n")

        repo6, anchor6, m6 = _lane_merge_repo(td, "p6", _plant_redis, lane_step=_make_promotion_bc,
                                              anchor_step=_redis_plain)
        code, out = _gate(repo6, anchor6, ["--approved-merge-file", str(_approved(td, "p6", m6))])
        rows.append(("P6 이중 원인(L 필요성)", 2, code,
                     re.search(r"\[#416\][^\n]*\n\s+↳ 귀속 유지: 유입 증명 실패\(이중 원인\)", out) is not None
                     and "[#416]" not in _section(out, inflow_title),
                     "F1 통과·L 실패 → 귀속 유지"))

        # P8 — 앵커 비조상(무관 가지): 주의 1행 · exit 현행(2)
        repo8, _anchor8 = _make_repo(td, "p8")
        _git(repo8, "checkout", "-q", "-b", "side")
        _write(repo8, "side_note.md", "side\n")
        side_sha: str = _commit_all(repo8, "side work")
        _git(repo8, "checkout", "-q", "main")
        _plant_violation(repo8)
        _commit_all(repo8, "main violation")
        code, out = _gate(repo8, side_sha)
        rows.append(("P8 앵커 비조상", 2, code,
                     f"주의: 앵커 {side_sha[:12]} 는 HEAD" in out and "조상이 아니다" in out
                     and not any(t in out for t in titles_new), "진단 1행·exit 무변"))

        # P9 — 역방향 합성 머지(main←lane) 등재 → exit 1 / P9′ 앵커가 ^2 경유 → exit 1
        repo9, anchor9, _m9 = _lane_merge_repo(td, "p9", _plant_violation)
        _git(repo9, "checkout", "-q", "main")
        _git(repo9, "merge", "-q", "--no-ff", "-m", "reverse: main merges lane", "lane")
        m_rev: str = _head(repo9)
        _git(repo9, "checkout", "-q", "lane")
        code, out = _gate(repo9, anchor9, ["--approved-merge-file", str(_approved(td, "p9", m_rev))])
        rows.append(("P9 역방향 합성 머지", 1, code, "사슬 밖" in out, "main←lane 머지는 등재 대상 아님"))
        repo9b, _anchor9b = _make_repo(td, "p9b")
        _git(repo9b, "checkout", "-q", "-b", "side")
        _write(repo9b, "side_note.md", "side\n")
        side9: str = _commit_all(repo9b, "side work")
        _git(repo9b, "checkout", "-q", "main")
        _git(repo9b, "merge", "-q", "--no-ff", "-m", "main merges side", "side")
        _plant_violation(repo9b)
        _commit_all(repo9b, "violation after")
        code, out = _gate(repo9b, side9, ["--approved-merge-file", str(_approved(td, "p9b"))])
        rows.append(("P9′ 앵커 사슬 밖", 1, code, "first-parent 사슬 밖" in out, "조상이지만 ^2 경유"))

        # P10 — M^1 에 SyntaxError → 측정 무효(M^1) 귀속 유지
        def _lane_broken(r: Path) -> None:
            _write(r, "application/orders/broken_lane.py", "def (:\n")

        repo10, anchor10, m10 = _lane_merge_repo(td, "p10", _plant_violation, lane_step=_lane_broken)
        code, out = _gate(repo10, anchor10, ["--approved-merge-file", str(_approved(td, "p10", m10))])
        rows.append(("P10 M^1 SyntaxError 측정 무효", 2, code,
                     out.count(f"↳ 귀속 유지: 측정 무효(M^1) — {m10[:12]}") == 3
                     and "[#parse-fail]" in _section(out, "귀속(N∖L)"),
                     "parse-fail 비대칭 → L 불성립"))

        # P11 — M^1 스냅숏 실패(PATH shim 이 그 sha 의 `git archive` 만 거절) → 측정 무효(스냅숏 실패)·출력 보존
        repo11, anchor11, m11 = _lane_merge_repo(td, "p11", _plant_violation)
        p11_parent1: str = _git(repo11, "rev-parse", f"{m11}^1").stdout.strip()
        shim: Path = td / "git-shim"
        shim.mkdir()
        (shim / "git").write_text(
            '#!/bin/bash\nif [ "$3" = "archive" ] && [ "$4" = "$DJR_SMOKE_DENY_ARCHIVE" ]; then '
            'echo "fatal: simulated: object $4 unavailable" >&2; exit 128; fi\nexec /usr/bin/git "$@"\n',
            encoding="utf-8")
        (shim / "git").chmod(0o755)
        env11: "dict[str, str]" = dict(_scrubbed_env(), PATH=f"{shim}:{os.environ.get('PATH', '')}",
                                       DJR_SMOKE_DENY_ARCHIVE=p11_parent1)
        proc11: "subprocess.CompletedProcess[str]" = subprocess.run(
            [sys.executable, str(GATE), str(repo11), "--anchor", anchor11,
             "--approved-merge-file", str(_approved(td, "p11", m11))],
            capture_output=True, text=True, env=env11)
        out11: str = proc11.stdout + proc11.stderr
        rows.append(("P11 스냅숏 실패 측정 무효", 2, proc11.returncode,
                     "Traceback" not in out11 and "판정: 귀속 3건" in out11
                     and out11.count(f"↳ 귀속 유지: 측정 무효(스냅숏 실패) — {m11[:12]}") == 3
                     and f"스냅숏 실패(측정 무효 — 해당 머지의 후보 라인은 귀속 유지): {p11_parent1[:12]}" in out11,
                     "AnchorDiffUsage 포착 → custody·출력 보존"))

        # P12 — 합성 머지: lane 이 임시 가지 tmp 를 머지하고 tmp 를 지움 → ^2 를 포함하는 ref 가 lane(HEAD)뿐 → 진단 1행
        repo12, anchor12 = _make_repo(td, "p12")
        _git(repo12, "checkout", "-q", "-b", "lane")
        _write(repo12, "lane_note.md", "lane work\n")
        _commit_all(repo12, "lane work")
        _git(repo12, "checkout", "-q", "-b", "tmp", "main")
        _plant_violation(repo12)
        _commit_all(repo12, "tmp change")
        _git(repo12, "checkout", "-q", "lane")
        _git(repo12, "merge", "-q", "--no-ff", "-m", "M merge tmp", "tmp")
        m12: str = _head(repo12)
        _git(repo12, "branch", "-D", "tmp")
        code, out = _gate(repo12, anchor12, ["--approved-merge-file", str(_approved(td, "p12", m12))])
        rows.append(("P12 합성 머지 ^2 ref 진단", 0, code,
                     "↳ 주의: ^2" in out and "HEAD 브랜치뿐 — 역방향/합성 머지 의심" in out
                     and out.count("↳ 유입:") == 3,
                     "진단 1행·exit 무변(유입 3)"))
        # P12r — remote-tracking(`refs/remotes/origin/lane`)·태그가 ^2 를 포함해도 HEAD 브랜치 자신으로 세어 진단 유지.
        _git(repo12, "update-ref", "refs/remotes/origin/lane", m12)
        _git(repo12, "tag", "lane-wip", m12)
        code, out = _gate(repo12, anchor12, ["--approved-merge-file", str(_approved(td, "p12r", m12))])
        rows.append(("P12r remote-tracking·태그 진단 유지", 0, code,
                     out.count("역방향/합성 머지 의심") == 1 and out.count("↳ 유입:") == 3,
                     "origin/lane·태그는 HEAD 브랜치 자신 — 진단 침묵 사각 폐쇄"))
        # 대조 — 정상 머지(P1 골격)에는 진단이 없다.
        code, out = _gate(repo, anchor, ["--approved-merge-file", str(_approved(td, "p12n", m_sha))])
        rows.append(("P12′ 정상 머지 진단 부재", 2, code, "역방향/합성 머지 의심" not in out,
                     "^2 가 main 에 도달 → 진단 0(레인 후속 커밋 뒤 상태라 exit 2)"))

        # ── R — 병렬 실행(C1⑵) 옛 직렬 게이트 직접 대조 ─────────────────────────────────
        try:
            rows.extend(_parallel_rows(td))
        except RuntimeError as exc:
            print(f"재료 결손: {exc}", file=sys.stderr)
            return 1

    print("| 케이스 | 기대 exit | 실측 | 내용 | 판정 |")
    print("|---|---|---|---|---|")
    bad: int = 0
    for name, want, got, content_ok, note in rows:
        ok: bool = want == got and content_ok
        if not ok:
            bad += 1
        print(f"| {name} | {want} | {got} | {'✓' if content_ok else '✗'} | {'✓' if ok else '✗ 불일치'} | {note}")
    print(f"케이스 {len(rows)} · 일치 {len(rows) - bad} · 불일치 {bad}")
    return 0 if bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
