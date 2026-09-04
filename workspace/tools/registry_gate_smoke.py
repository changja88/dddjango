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
from pathlib import Path

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
    for rec in payload.get("records", []):
        for key in ("ts", "run_id", "record_id", "file_raw", "experiment_run_id"):
            rec.pop(key, None)
    return payload


def _pre_repair_gate(td: Path) -> "Path | None":
    """수리 전 «게이트»(`_PRE_REPAIR_COMMIT` 의 registry_gate.py)를 **현행 검사기 트리** 위에 덮어쓴 사본.

    측정 대상은 게이트 불변(귀속·정규화·출력 판형)뿐이다 — 검사기 트리는 현행을 쓴다(검사기 규칙이
    바뀌면(예: 2026-09-04 #219/#635 의 골격 파일 건너뜀) 옛 검사기의 발화가 diff 를 오염시키므로).
    옛 게이트의 import 계약(findings·anchor_diff)이 현행 모듈과 맞아야 한다 — 어긋나면 스모크가 그 사실로 red 다."""
    dest: Path = td / "pre-repair"
    shutil.copytree(GATE.parent, dest / "dddjango" / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    old_gate: "subprocess.CompletedProcess[bytes]" = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{_PRE_REPAIR_COMMIT}:dddjango/scripts/registry_gate.py"],
        capture_output=True)
    if old_gate.returncode != 0:
        return None
    gate: Path = dest / "dddjango" / "scripts" / "registry_gate.py"
    gate.write_bytes(old_gate.stdout)
    return gate


def main() -> int:
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
        rows.append(("P0′ 수리 전 사본 byte 동일", 2, code0p,
                     _mask(out0) == _mask(out0p) and _mask_sidecar(side0) == _mask_sidecar(side0p),
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
