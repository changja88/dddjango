#!/usr/bin/env python3
"""registry 27종 «판정 차분» 게이트 — 이번 런이 위반을 «늘렸는가»만 판정한다.

왜 차분인가(2026-08-12 라운드 1′ P3′ · 적대 리뷰 Goodhart 렌즈): brownfield 에선
legacy 위반이 상존해 「루트 registry 전체 green」이 문자 그대로는 영원히 불가능하고,
그 모순이 세션의 자체 귀속 발명을 낳았다(라운드 1′ 실측). 경로 매칭식 귀속(변경 집합
대조)은 다섯 계열 공격에 뚫린다 — base 자기 선택·부재(#488) 위반의 경로 부재·검사기
출력 형식 이질·빈 변경 집합 역이용·.gitignore 은닉(전부 재현 실측). 판정 차분은 그
전부를 한 설계로 닫는다:

  앵커 상태에서 registry 실행 → 위반 라인 집합 L
  현재 상태에서 registry 실행 → 위반 라인 집합 N
  귀속 = N ∖ L  (라인번호·스냅숏 경로만 정규화 — 경로 «파싱»을 하지 않는다)

- **앵커는 actor 가 고르지 않는다** — 라운드에선 대장의 앵커 커밋, 파이프라인에선
  Phase 2 진입 직전 기록되는 build-start 앵커(`commands/dddjango.md` 절차 소유)를
  호출자가 그대로 넘긴다. 앵커=HEAD 이고 working tree 가 clean 이면 차분이 공허하므로
  사용 오류(exit 1)다 — 「커밋 뒤 게이트」로 판정을 비우는 우회를 막는다.
- **귀속 0 ≠ 전체 clean** — legacy 잔존(L∩N)은 exit 에 안 들어가되 항상 보고한다
  (침묵 금지). BC 하나가 clean 한지는 `bc_registry_run.py`(그림자 전수)가 답한다 —
  두 도구는 같은 로스터(`checker_registry.py`)를 쓰되 묻는 것이 다르다.
- **이관 빚 채널**: `--legacy-debt-file` 의 사용자 승인 목록(줄 형식: `#<규칙> <부분문자열>`)
  에 맞는 귀속은 exit 에서 빼되 «빚» 절로 반드시 보고한다 — 빚은 기록 근거이지 legacy
  모양을 «추가로» 복사할 근거가 아니다.
- 비-git TARGET 은 fail-closed: 차분 불능이므로 현재 위반 전부를 귀속으로 본다.
- 검사기가 red 인데 위반 라인을 못 파싱하면 그 검사기 몫을 합성 귀속으로 남긴다(fail-closed).

사용: python3 registry_gate.py <저장소 루트> --anchor <ref> [--legacy-debt-file <path>]
exit 0 = 귀속 0 / exit 2 = 귀속 존재 / exit 1 = 사용 오류·재료 결손·공허 차분.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anchor_diff  # noqa: E402  — git·앵커 스냅숏·빚 로더·빚 매칭 공용(복제 통합)
import checker_target  # noqa: E402
import findings  # noqa: E402  — sink 환경변수 이름·라인 재구성 문법의 단일 출처
from checker_registry import REGISTRY, checker_argv  # noqa: E402

_FINDING_RE: "re.Pattern[str]" = re.compile(r"^\s*(\[#\d+\].*)$")
_LINENO_RE: "re.Pattern[str]" = re.compile(r":\d+")
_IGNORE_COPY: "tuple[str, ...]" = (
    ".git", ".venv", "venv", "__pycache__", "*.pyc", "node_modules",
    "graphify-out", ".mypy_cache", ".pytest_cache", ".ruff_cache", "staticfiles",
    # F-C(2026-08-14): 숨김 디렉터리 전부 = 도구·하네스 영역(`.codex/`·`.dddjango/` 등) —
    # 검사 표면이 아니다(라운드 3 실측: `.codex/cleanroom-guard.py` #493×4 오탐 귀속).
    ".*", "site-packages", "build", "dist",
)


class _UsageParser(argparse.ArgumentParser):
    """usage 오류를 문면 계약(exit 1)으로 — argparse 기본 exit 2 는 «위반»과 겹친다
    (check-composition-root `_UsageParser` 패턴 이식)."""

    def error(self, message: str) -> None:
        print(f"사용 오류: {message}", file=sys.stderr)
        raise SystemExit(1)


def _snapshot_current(root: Path, dest: Path) -> None:
    """working tree 를 비-git 사본으로 복사한다(무거운 비-소스 디렉터리 제외)."""
    shutil.copytree(root, dest, ignore=shutil.ignore_patterns(*_IGNORE_COPY))


def _parse_fail_findings(target: Path) -> "set[str]":
    """이 인터프리터로 파싱 불가한 검사 대상 — fail-open(침묵 스킵) 방지 합성 귀속(F-A 2026-08-14).

    앵커·현재 «양쪽» 스냅숏에 같은 스캔을 걸어 차분 원리를 태운다 — 앵커에도 있던
    깨진 파일은 legacy(L∩N), 새로 생긴 것만 귀속(N∖L). 고의 투입으로 red 를
    «판정 불능(exit 1)»으로 바꾸는 우회(적대 리뷰 A1)가 성립하지 않는다.
    """
    out: "set[str]" = set()
    for p in sorted(target.rglob("*.py")):
        if any(seg.startswith(".") for seg in p.relative_to(target).parts[:-1]):
            continue  # 숨김 디렉터리 = 도구·하네스 영역(F-C)
        try:
            ast.parse(p.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            out.add(f"(pre-scan) :: [#parse-fail] {p.relative_to(target)}: 이 인터프리터"
                    f"({sys.version_info[0]}.{sys.version_info[1]})로 파싱 불가 — 검사기가 침묵 스킵하는 파일")
    return out


def _strip_snapshot(text: str, prefixes: "tuple[str, ...]") -> str:
    """스냅숏 절대 경로 echo 제거(A3) — 라인번호는 건드리지 않는다."""
    for p in prefixes:
        text = text.replace(p, "")
    return text


def _normalize(line: str, prefixes: "tuple[str, ...]") -> str:
    """차분 키용 정규화 — 경로 제거 + 라인번호 정규화(상하 이동 오탐 방지)."""
    return _LINENO_RE.sub(":N", _strip_snapshot(line, prefixes))


def _run_registry(target: Path,
                  sink: "Path | None" = None) -> "tuple[dict[str, int], set[str], list[dict]]":
    """로스터 전체를 돌려 (검사기별 exit, 정규화 위반 라인 집합, 구조화 레코드)를 낸다.

    **sink 격리(T2-3)**: 검사기 서브프로세스는 부모 환경을 상속하므로, 격리하지 않으면
    앵커 실행과 현재 실행의 레코드가 **같은 파일에 뒤섞여** 소비자가 legacy 와 신규를
    구분할 수 없다(`anchor_diff._run_lines` 가 T2-1 에서 같은 이유로 받은 수리를 이 게이트만
    못 받고 있었다 — 적대 리뷰 AM#3·AN#3). 여기서는 두 채널(`DJR_FINDINGS_JSON`·
    `DJR_VIOLATIONS_DIR`)을 **둘 다** 제거하고, 요청받은 sink 만 명시 지정한다.
    """
    exits: "dict[str, int]" = {}
    lines: "set[str]" = set()
    prefixes: "tuple[str, ...]" = (str(target) + "/", str(target))
    env: "dict[str, str]" = dict(os.environ)
    env.pop(findings.ENV_VAR, None)
    env.pop(findings.ENV_DIR, None)
    if sink is not None:
        env[findings.ENV_VAR] = str(sink)
    for script, auto in REGISTRY:
        proc = subprocess.run(
            checker_argv(sys.executable, script, str(target), auto),
            capture_output=True, text=True, env=env,
        )
        exits[script] = proc.returncode
        parsed: int = 0
        for raw in (proc.stdout + "\n" + proc.stderr).splitlines():
            m = _FINDING_RE.match(raw)
            if m is None:
                continue
            lines.add(f"{script} :: {_normalize(m.group(1), prefixes)}")
            parsed += 1
        if proc.returncode != 0 and parsed == 0:
            lines.add(f"{script} :: [진단 미파싱 · exit {proc.returncode}] fail-closed 귀속")
    records: "list[dict]" = []
    if sink is not None and sink.is_file():
        for raw in sink.read_text(encoding="utf-8", errors="replace").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                records.append(json.loads(raw))
            except json.JSONDecodeError:
                continue  # 레코드는 «추가» 채널 — 깨진 줄이 판정을 죽이지 않는다
    return exits, lines, records


def _write_introduced(dest: Path, anchor_sha: str, attributed: "list[str]",
                      records: "list[dict]", prefixes: "tuple[str, ...]") -> None:
    """귀속(N∖L) 라인에 대응하는 **현재 실행 레코드만** sidecar 로 쓴다(T2-3).

    왜 게이트가 쓰는가: 귀속은 «앵커 대비 차분»이라 게이트만 알 수 있다. 소비자가 raw
    sink 를 직접 읽으면 legacy 잔존까지 집어 «이 빌드에서 즉석 수리하지 않는다»는 규율
    (`commands/dddjango.md` — legacy 잔존 red 는 보고 채널로만)을 깨뜨린다.

    매칭은 `findings.line_of_record` 로 레코드를 라인으로 되돌린 뒤 게이트와 **같은
    정규화**를 적용해 키를 맞춘다. 대응 레코드가 없는 귀속 라인(합성 fail-closed 귀속·
    레코드 채널 밖 진단)은 버리지 않고 `unmatched` 로 남긴다 — fail-closed.
    """
    want: "set[str]" = set(attributed)
    picked: "list[dict]" = []
    matched: "set[str]" = set()
    for rec in records:
        key: str = f"{rec.get('checker')} :: {_normalize(findings.line_of_record(rec), prefixes)}"
        if key not in want:
            continue
        # 게이트는 **임시 스냅숏 사본**에서 검사기를 돌리므로 레코드의 file 은 그 사본의
        # 절대 경로다. 그대로 넘기면 소비자(재생성 루프)가 존재하지 않는 경로를 주입한다 —
        # 대상 상대 경로로 되돌리고 원본은 file_raw 로 보존한다(라인번호는 유지).
        raw: str = str(rec.get("file", ""))
        rel: str = _strip_snapshot(raw, prefixes)
        picked.append(dict(rec, file=rel, file_raw=raw) if rel != raw else dict(rec))
        matched.add(key)
    payload: "dict[str, object]" = {
        "schema": "gate-introduced/0",
        "anchor": anchor_sha,
        # 실런 식별자를 sidecar 가 **운반한다**(반증 레인 AT 과제 2): 이게 없으면 재생성 루프가
        # 남기는 용량 로그에 실런을 적을 경로가 없어 「전 사슬」이 게이트에서 끊긴다.
        "experiment_run_id": next((r.get("experiment_run_id") for r in picked
                                   if r.get("experiment_run_id")), None),
        "attributed_lines": attributed,
        "records": picked,
        "unmatched_lines": sorted(want - matched),
    }
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n귀속 레코드 sidecar → {dest} "
          f"(레코드 {len(picked)} · 대응 없는 귀속 라인 {len(want - matched)})")


def _contract_key(rec: "dict", prefixes: "tuple[str, ...]") -> str:
    return f"{rec.get('checker')} :: {_normalize(findings.line_of_record(rec), prefixes)}"


def _write_contract(dest: Path, anchor_sha: str, records: "list[dict]",
                    anchor_records: "list[dict]", prefixes: "tuple[str, ...]",
                    anchor_prefixes: "tuple[str, ...]") -> None:
    """`rule=null` 레코드(선행 계약·센티널)를 **계수 전용** companion sidecar 로 쓴다.

    왜 별도인가(동결 개정 9 · 사후 리뷰 AS-03): 이 레코드들은 `[#N]` 라인을 내지 않아
    귀속 정규식에 걸리지 않고, selector 도 `rule is None` 이면 버린다. 그래서 **주입에는
    쓰이지 않지만 존재는 셈해야** 한다 — 사용자 결정 «계수 후 유효 유지»는 「이런 런을
    통계에서 빼지 않되 비율은 기록한다」이므로, 셀 원자료가 여기서 만들어져야 한다.

    이 sidecar 는 재생성 루프의 **입력이 아니다**. 계수·리포트 전용이다.

    **앵커 차분을 적용한다**(반증 레인 AT 4-1): 앞선 판은 current 실행의 `rule=null` 을 통째로
    셌다 — 그러면 `uninjectable_n` 이 「이번 빌드 신규」인지 「legacy 포함 총량」인지 알 수 없다.
    귀속과 **같은 정규화·같은 N∖L 규칙**으로 신규분만 세고, legacy 는 따로 보고한다.
    """
    legacy: "set[str]" = {_contract_key(r, anchor_prefixes)
                          for r in anchor_records if r.get("rule") is None}
    picked: "list[dict]" = [r for r in records if r.get("rule") is None
                            and _contract_key(r, prefixes) not in legacy]
    residual: int = sum(1 for r in records if r.get("rule") is None
                        and _contract_key(r, prefixes) in legacy)
    by_checker: "dict[str, int]" = {}
    for rec in picked:
        name: str = str(rec.get("checker"))
        by_checker[name] = by_checker.get(name, 0) + 1
    payload: "dict[str, object]" = {
        "schema": "gate-contract/0",
        "anchor": anchor_sha,
        "total": len(picked),                 # 신규(N∖L)만
        "legacy_residual": residual,          # 앵커에도 있던 것 — 보고만
        "by_checker": dict(sorted(by_checker.items())),
        "experiment_run_id": next((r.get("experiment_run_id") for r in picked
                                   if r.get("experiment_run_id")), None),
        "records": [{k: r.get(k) for k in
                     ("checker", "contract_ref", "sentinel", "file", "message",
                      "severity", "record_id", "experiment_run_id")} for r in picked],
    }
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"계약 레코드 companion sidecar → {dest} "
          f"(신규 rule=null {len(picked)}건 · legacy 잔존 {residual}건 · "
          f"검사기 {len(by_checker)}종 — 주입 대상 아님·계수 전용)")


def main(argv: "list[str]") -> int:
    ap = _UsageParser(add_help=True)
    ap.add_argument("target")
    ap.add_argument("--anchor", required=False, default=None,
                    help="차분 기준(대장 앵커 또는 build-start 앵커) — actor 가 임의로 고르지 않는다")
    ap.add_argument("--legacy-debt-file", default=None)
    ap.add_argument("--introduced-json", default=None,
                    help="귀속(N∖L) 위반의 구조화 레코드를 이 경로에 sidecar 로 쓴다 — "
                         "재생성 루프의 유일한 입력(legacy 잔존은 구조적으로 배제된다)")
    ap.add_argument("--contract-json", default=None,
                    help="`rule=null`(선행 계약·센티널) 레코드의 계수를 companion sidecar 로 "
                         "쓴다 — 주입 대상이 아니라 «계수 후 유효 유지»(개정 9)의 원자료")
    ns = ap.parse_args(argv)

    root: Path = Path(ns.target).resolve()
    if not root.is_dir():
        print(f"사용 오류: TARGET {root} 이 디렉터리가 아니다", file=sys.stderr)
        return 1
    bad: "str | None" = checker_target.bc_shaped_target_reason(str(root))
    if bad is not None:
        print(f"사용 오류: {bad}", file=sys.stderr)
        return 1

    debt_rules: "list[tuple[str, str]]" = []
    if ns.legacy_debt_file is not None:
        debt_path: Path = Path(ns.legacy_debt_file)
        if not debt_path.is_file():
            print(f"재료 결손: 빚 목록 {debt_path} 없음", file=sys.stderr)
            return 1
        try:
            debt_rules = anchor_diff.load_debt(debt_path)
        except anchor_diff.AnchorDiffUsage as exc:  # 형식 오류 — traceback 아닌 사용 오류로
            print(f"사용 오류: {exc}", file=sys.stderr)
            return 1

    is_git: bool = anchor_diff.is_git_worktree(root)

    with tempfile.TemporaryDirectory() as td:
        cur: Path = Path(td) / "current"
        _snapshot_current(root, cur)
        # L/N 을 **다른 파일**로 받는다 — 한 sink 에 누적하면 legacy 와 신규가 섞인다.
        sink_n: Path = Path(td) / "records-current.jsonl"
        sink_l: Path = Path(td) / "records-anchor.jsonl"
        cur_prefixes: "tuple[str, ...]" = (str(cur) + "/", str(cur))
        # 계약 sidecar 의 앵커 차분 재료 — 비-git 분기에서는 앵커가 없어 전량이 «신규»다.
        l_records: "list[dict]" = []
        anc_prefixes: "tuple[str, ...]" = ()

        if not is_git:
            print("주의: 비-git TARGET — 차분 불능이라 fail-closed(현재 위반 전량 귀속)")
            exits_n, n_set, n_records = _run_registry(cur, sink_n)
            n_set |= _parse_fail_findings(cur)
            l_set: "set[str]" = set()
            exits_l: "dict[str, int]" = {}
            anchor_sha: str = "(비-git)"
        else:
            if ns.anchor is None:
                print("사용 오류: git 저장소에는 --anchor <ref> 가 필수다 — 라운드=대장 앵커 · "
                      "파이프라인=Phase 2 진입 직전 기록된 build-start 앵커", file=sys.stderr)
                return 1
            rev = anchor_diff.run_git(root, "rev-parse", "--verify", f"{ns.anchor}^{{commit}}")
            if rev.returncode != 0:
                print(f"사용 오류: 앵커 {ns.anchor!r} resolve 불능 — {rev.stderr.strip()}", file=sys.stderr)
                return 1
            anchor_sha = rev.stdout.strip()
            head = anchor_diff.run_git(root, "rev-parse", "HEAD").stdout.strip()
            dirty: bool = bool(anchor_diff.run_git(root, "status", "--porcelain").stdout.strip())
            if anchor_sha == head and not dirty:
                print("사용 오류: 앵커=HEAD 이고 working tree 가 clean — 차분이 공허하다. "
                      "게이트는 구현 커밋 «전»에 돌리거나, 런 시작점 앵커를 지정하라(공허 green 차단).",
                      file=sys.stderr)
                return 1
            anc: Path = Path(td) / "anchor"
            try:
                anchor_diff.snapshot_anchor(root, anchor_sha, anc)
            except anchor_diff.AnchorDiffUsage as exc:
                print(f"재료 결손: {exc}", file=sys.stderr)
                return 1
            exits_l, l_set, _l_records = _run_registry(anc, sink_l)
            l_records = _l_records
            anc_prefixes = (str(anc) + "/", str(anc))
            l_set |= _parse_fail_findings(anc)
            exits_n, n_set, n_records = _run_registry(cur, sink_n)
            n_set |= _parse_fail_findings(cur)

    attributed: "list[str]" = sorted(n_set - l_set)
    resolved: "list[str]" = sorted(l_set - n_set)
    residual: "list[str]" = sorted(l_set & n_set)

    debt: "list[str]" = []
    if debt_rules:
        rest: "list[str]" = []
        for line in attributed:  # 라인은 이미 정규화돼 있다 — debt_match 코퍼스 그대로.
            hit: bool = anchor_diff.debt_match(line, debt_rules)
            (debt if hit else rest).append(line)
        attributed = rest

    print(f"# registry_gate — 판정 차분 · {root.name} · 앵커 {anchor_sha[:12]}")
    print("**귀속 0 ≠ 전체 clean** — 이 게이트는 «이번 런이 위반을 늘렸나»만 판정한다(legacy 격리).")
    print("| 검사기 | anchor | current |")
    print("|---|---|---|")
    for script, _auto in REGISTRY:
        print(f"| `{script}` | {exits_l.get(script, '—')} | {exits_n.get(script, '—')} |")
    print(f"\n== 귀속(N∖L) {len(attributed)}건 ==")
    for line in attributed:
        print(f"  {line}")
    if debt:
        print(f"\n== 이관 빚(승인 목록 매칭 — exit 제외·기록 의무) {len(debt)}건 ==")
        for line in debt:
            print(f"  {line}")
    by_checker: "dict[str, int]" = {}
    for line in residual:
        by_checker[line.split(" :: ", 1)[0]] = by_checker.get(line.split(" :: ", 1)[0], 0) + 1
    print(f"\n== legacy 잔존(L∩N) {len(residual)}건 · 해소(L∖N) {len(resolved)}건 ==")
    for script in sorted(by_checker):
        print(f"  {script}: {by_checker[script]}")
    if ns.introduced_json is not None:
        _write_introduced(Path(ns.introduced_json), anchor_sha, attributed,
                          n_records, cur_prefixes)
    if ns.contract_json is not None:
        _write_contract(Path(ns.contract_json), anchor_sha, n_records,
                        l_records, cur_prefixes, anc_prefixes)

    print(f"\n판정: 귀속 {len(attributed)}건 → {'green(신규 위반 없음)' if not attributed else 'red'}")
    return 0 if not attributed else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
