#!/usr/bin/env python3
"""재생성 루프 상태기계 하네스 (T2-3 · 규약 R1′ 의 «픽스처 하네스» 이행).

루프의 **종료 사유와 회전 전이**를 결정적 픽스처로 고정한다. 과금·비결정성이 없도록
재생성 호출은 `--dry-regen`(no-op) 또는 `--fake-regen`(결정적 명령)으로 대체한다.

왜 `--fake-regen` 이 필요한가(반증 레인 AO 과제 2): dry 는 아무것도 고치지 않아 두 회전
만에 위반 집합이 굳는다. 그러면 «`no_progress` 뒤에도 계속 돌아 세 번째 회전에서 수렴한다»는
규율을 **영원히 검증하지 못한다** — 구현이 `no_progress` 를 종료로 잘못 다뤄도 하네스가
통과해 버린다. 그래서 `{X}→{X}→{X}→∅` 를 결정적으로 재현하는 케이스를 둔다.

케이스:
  T1 no_progress 비종료 — dry 3회전 → `budget` · no_progress 2회 발생하되 종료 안 함
  T2 2→3 전이 후 수렴  — fake 가 3회전째에 위반 제거 → `zero`
  T3 범위 밖 편집       — fake 가 scope 밖 파일 생성 → `scope_violation` · exit 3
  T4 귀속 0            — 위반 없음 → 1회전에 `zero`

exit 0 = 전건 일치 / 2 = 불일치 / 1 = 재료 결손.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
LOOP: Path = ROOT / "workspace" / "tools" / "regen_loop_prototype.py"
SCOPE: str = "application/orders"
VIOLATION_REL: str = "application/orders/domain_layer/fresh_svc.py"
VIOLATION_SRC: str = "NEWCACHE = {}\n"

sys.path.insert(0, str(ROOT / "workspace" / "tools"))
import registry_gate_smoke as G  # noqa: E402  — good_bc git repo 만들기·env 스크럽 재사용


def _run(repo: Path, anchor: str, log: Path, extra: "list[str]") -> "tuple[int, str]":
    proc = subprocess.run(
        [sys.executable, str(LOOP), "--run", "--target", str(repo), "--anchor", anchor,
         "--scope", SCOPE, "--max-turns", "3", "--turn-log", str(log), *extra],
        capture_output=True, text=True, env=G._scrubbed_env())
    return proc.returncode, proc.stdout + proc.stderr


def _turns(log: Path) -> "list[dict]":
    if not log.is_file():
        return []
    return [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines() if x.strip()]


def _seed_violation(repo: Path) -> None:
    p: Path = repo / VIOLATION_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(VIOLATION_SRC, encoding="utf-8")


def main() -> int:
    if not LOOP.is_file() or not G.BASE_FIXTURE.is_dir():
        print("재료 결손: regen_loop_prototype.py 또는 good_bc fixture 없음", file=sys.stderr)
        return 1
    rows: "list[tuple[str, str, str, bool, str]]" = []

    with tempfile.TemporaryDirectory() as td_s:
        td: Path = Path(td_s)

        # T1 — dry 3회전: no_progress 가 나도 예산까지 돈다
        repo, anchor = G._make_repo(td, "t1")
        _seed_violation(repo)
        log = td / "t1.jsonl"
        code, _out = _run(repo, anchor, log, ["--dry-regen"])
        t = _turns(log)
        ok = (len(t) == 3 and t[-1]["stop_reason"] == "budget"
              and sum(1 for x in t if x.get("no_progress")) == 2 and code == 0)
        rows.append(("T1 no_progress 비종료", "budget/3회전",
                     f"{t[-1]['stop_reason'] if t else '—'}/{len(t)}회전", ok,
                     "no_progress 2회 발생하되 종료 안 함"))

        # T2 — fake 가 3회전째에 위반 제거: {X}→{X}→{X}→∅
        # 위반을 **커밋해 둔다**: 3회전째에 지워도 working tree 는 dirty(deleted)라 게이트가
        # «앵커=HEAD·clean = 공허 차분»(exit 1)으로 거절하지 않는다. 앵커는 위반 이전 커밋이라
        # 위반은 그대로 귀속(N∖L)이다. 대안으로 «무해한 파일 하나 남기기»를 썼더니 트리 규약
        # 검사기가 그 파일을 #490 으로 잡았다 — `.txt` 도 검사 표면이다(하네스가 적발).
        repo, anchor = G._make_repo(td, "t2")
        _seed_violation(repo)
        G._git(repo, "add", "-A")
        G._git(repo, "commit", "-q", "-m", "위반 포함 커밋(앵커 이후)")
        counter: Path = td / "t2.count"          # 저장소 **밖**(범위 밖 편집으로 세지 않게)
        fake: str = (
            f'C=$(cat "{counter}" 2>/dev/null || echo 0); C=$((C+1)); echo $C > "{counter}"; '
            f'if [ "$C" -ge 3 ]; then rm -f "{VIOLATION_REL}"; fi'
        )
        log = td / "t2.jsonl"
        code, _out = _run(repo, anchor, log, ["--fake-regen", fake])
        t = _turns(log)
        ok = (len(t) == 3 and t[-1]["stop_reason"] == "zero"
              and sum(1 for x in t if x.get("no_progress")) >= 1 and code == 0)
        rows.append(("T2 2→3 전이 후 수렴", "zero/3회전",
                     f"{t[-1]['stop_reason'] if t else '—'}/{len(t)}회전", ok,
                     "2회전 no_progress 뒤에도 3회전을 돌아 수렴"))

        # T3 — fake 가 범위 밖 파일을 만든다: 관측치가 아니라 기술 실패
        repo, anchor = G._make_repo(td, "t3")
        _seed_violation(repo)
        log = td / "t3.jsonl"
        code, _out = _run(repo, anchor, log, ["--fake-regen", "echo x > framework_oops.py"])
        t = _turns(log)
        ok = (bool(t) and t[-1]["stop_reason"] == "scope_violation"
              and t[-1]["changed_outside_scope"] and code == 3)
        rows.append(("T3 범위 밖 편집", "scope_violation/exit 3",
                     f"{t[-1]['stop_reason'] if t else '—'}/exit {code}", ok,
                     "위반 delta 가 아니라 편집 자체로 잡는다"))

        # T4 — 귀속 0: 무해 변경만 있는 저장소
        repo, anchor = G._make_repo(td, "t4")
        (repo / "docs_note.md").write_text("harmless\n", encoding="utf-8")
        log = td / "t4.jsonl"
        code, _out = _run(repo, anchor, log, ["--dry-regen"])
        t = _turns(log)
        ok = (len(t) == 1 and t[-1]["stop_reason"] == "zero" and code == 0)
        rows.append(("T4 귀속 0", "zero/1회전",
                     f"{t[-1]['stop_reason'] if t else '—'}/{len(t)}회전", ok,
                     "고칠 것이 없으면 즉시 수렴"))

        # T5 — C암 배선(`--selector sparql`): 같은 저장소·같은 앵커에서 B와 **프롬프트가 달라야**
        # 한다. 여기까지 와야 「팩이 존재한다」가 아니라 「루프가 팩을 탄다」가 증명된다
        # (적대 리뷰 AQ-04 — regen_core 단위 시험만으로는 배선 공백을 못 잡는다).
        repo, anchor = G._make_repo(td, "t5")
        _seed_violation(repo)
        log_b = td / "t5b.jsonl"
        code_b, _ = _run(repo, anchor, log_b, ["--dry-regen"])
        tb = _turns(log_b)
        repo2, anchor2 = G._make_repo(td, "t5c")
        _seed_violation(repo2)
        log_c = td / "t5c.jsonl"
        code_c, out_c = _run(repo2, anchor2, log_c, ["--dry-regen", "--selector", "sparql"])
        tc = _turns(log_c)
        ok = (bool(tb) and bool(tc) and code_b == 0 and code_c == 0
              and tb[0]["prompt_sha256"] != tc[0]["prompt_sha256"]
              and tc[0].get("rules_n", 0) > 0
              and tc[0].get("hit_ratio") is not None
              and tb[0].get("rules_n", 0) == 0)
        rows.append(("T5 C암 배선 발화", "프롬프트 상이·rules>0",
                     f"b≠c {bool(tb) and bool(tc) and tb[0]['prompt_sha256'] != tc[0]['prompt_sha256']}"
                     f" · rules {tc[0].get('rules_n') if tc else '—'}", ok,
                     "루프가 실제로 팩을 탄다(단위 시험 아님)"))

    print("| 케이스 | 기대 | 실측 | 일치 | 비고 |")
    print("|---|---|---|---|---|")
    bad: int = 0
    for name, want, got, ok, note in rows:
        bad += 0 if ok else 1
        print(f"| {name} | {want} | {got} | {'✓' if ok else '✗'} | {note} |")
    print(f"케이스 {len(rows)} · 일치 {len(rows) - bad} · 불일치 {bad}")
    return 0 if not bad else 2


if __name__ == "__main__":
    sys.exit(main())
