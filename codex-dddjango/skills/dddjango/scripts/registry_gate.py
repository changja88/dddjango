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
- **승인 유입 채널(provenance 차분 · 2026-09-03)**: `--approved-merge-file` 의 발주자 승인
  «main→레인 머지» 목록(줄 형식: `<SHA> [메모]`)이 주어지면, 빚 매칭 뒤 남은 귀속 라인 ℓ
  (파일 p · 검사기 c)마다 다음을 결정적으로 증명한 것만 exit 에서 빼고 «승인 유입» 절로 보고한다:

    승인 유입(ℓ) ⟺ W(p) ∧ (F1(p) ∨ F2(p)) ∧ L(ℓ)
    W  worktree 의 p 가 HEAD 와 동일(porcelain 공백)
    F1 ∃M∈𝓜: blob(M^1:p) ≠ blob(M:p) ∧ blob(M:p) = blob(M^2:p) = blob(HEAD:p)
       — 승인 머지의 incoming 측에서 verbatim 전달·레인 미수정(충돌 해소분은 M≠M^2 라 탈락)
    F2 blob(HEAD:p) = blob(anchor:p) — 파일 무변 = «상호작용 서명»(검사기 환경만 바뀜)
    L  ∃M∈𝓜: ℓ ∈ R_c(M^2) ∖ R_c(M^1) — 검사기 c 를 M^2(incoming)·M^1(레인 측 직전)
       스냅숏에서 재실행해 «incoming 측에는 있고 레인 측 직전에는 없던» 진단임을 증명

  판정 불능(레코드 없음·비-blob 경로·worktree 수정·측정 무효·스냅숏 실패)은 전부 귀속 유지(fail-closed)다.
  L 은 **∃M 의미론**이다 — 승인 머지 하나에서라도 증명되면 유입이고, 전 승인 머지가 무효(측정 무효·
  스냅숏 실패)이거나 미증명이면 귀속 유지다(사유는 첫 무효 머지 기준 — 무효는 그 머지의 증명 기회를 잃을 뿐
  다른 머지의 증명을 막지 않는다). 스냅숏 실패(`git archive` 불능 등)는 traceback 이 아니라 그 머지의
  후보 라인 사유 `측정 무효(스냅숏 실패) — <M>` 로 귀속 유지되고 진단 절에 git 오류를 싣는다(출력 소실 0).
  L 없는 blob-only 설계는 기각됐다 — 레인이 BC `promotion` 을 신설하고 승인 머지가 리터럴
  "promotion" 을 가진 파일을 verbatim 들여오면 F1 은 통과하나 원인은 레인의 BC 다(이중 원인);
  R(M) 이 아니라 R(M^2) 를 쓰는 이유가 이 반례다(R(M) 은 레인 측 산출물을 포함한다).

provenance 차분 — 귀속의 분할이지 재정의가 아니다
  귀속 산식 N∖L 은 그대로다. 새 채널은 «감산»이 아니라 «분할»이다 — N∖L = 빚 ⊔ 승인 유입 ⊔
  귀속(잔여)이고 어떤 라인도 인쇄되지 않는 채널로 가지 않는다. exit 에서 빠지는 유일한 새 경로는
  «발주자 소유 목록 ∧ blob 3중 일치 ∧ R(M^2)∖R(M^1) 증명»이며 빚 채널과 같은 «사용자 승인 입력»
  부류다(도구는 목록의 소유를 검증하지 않는다 — 앵커·빚 목록과 같은 자리). 위 다섯 계열 공격과의
  정합: ① base 자기 선택 — 앵커도 승인 목록도 actor 밖이고, 앵커는 HEAD first-parent 사슬 위
  (도달 필수)·머지는 그 구간 안이어야 한다(역방향 합성·타 가지 머지는 형식 오류) ② 부재(#488)
  위반 — blob 없는 경로는 귀속 유지 ③ 출력 형식 이질 — `findings` 레코드가 단일 출처이고 대응
  레코드가 없으면 귀속 유지 ④ 빈 변경 집합 — 변경 집합을 쓰지 않고 L 이 incoming 측 존재를
  요구한다 ⑤ .gitignore 은닉 — 커밋 blob 이 없으면 F1·F2 가 성립하지 않는다. 귀속 목록을
  경로 필터(sed/grep)로 나눈 서술은 게이트 증거가 아니다 — 유입 분리는 이 채널뿐이다.
  상호작용 위반(F2)은 증명되면 유입, 아니면 `상호작용 미증명` 으로 귀속 유지다(철회할 변경이
  없으므로 처방은 STOP_FOR_USER_APPROVAL — 빚 등재·상류 해소·레인 설계 반송).
  역방향(main←lane) 머지는 HEAD=lane 이면 first-parent 사슬 밖이라 exit 1 이지만, 발주자가 합성
  머지를 레인 사슬에 올린 잔여 경로는 도구가 구별하지 못한다 — 머지 표에 `^2` 의 ref 도달성을 싣고
  `^2` 를 포함하는 ref 가 HEAD 브랜치뿐이면 «역방향/합성 머지 의심» 진단 1행을 낸다(exit 무변 ·
  custody 는 발주자 소유).

사용: python3 registry_gate.py <저장소 루트> --anchor <ref> [--legacy-debt-file <path>]
      [--approved-merge-file <path>] [--introduced-json <path>] [--contract-json <path>]
exit 0 = 귀속 0 / exit 2 = 귀속 존재 / exit 1 = 사용 오류·재료 결손·공허 차분·승인 목록 형식/사슬 오류.
flag 가 없으면 출력·sidecar 는 이 채널 도입 전과 byte 동일하다(상시 진단 «앵커가 HEAD 의 조상이
아니다» 1행만 병리 시 추가 — exit 무변).
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

_SCRIPTS_DIR: Path = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS_DIR))
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


def plugin_version() -> str:
    """플러그인 버전 probe — 설치 레이아웃 2경로(Claude `<plugin>/.claude-plugin/plugin.json` ·
    Codex `<plugin>/skills/dddjango/scripts` 기준 `parents[2]/.codex-plugin/plugin.json`).
    실패는 `(unknown)` — 판정 영향 0(헤더 «툴체인» 행 전용). design_pregate.py 도 같은 probe 를
    각자 보유한다(두 스크립트는 독립 파일 — 러너 유닛이 동치를 가드한다)."""
    candidates: "list[Path]" = [_SCRIPTS_DIR.parent / ".claude-plugin" / "plugin.json"]
    if len(_SCRIPTS_DIR.parents) > 2:
        candidates.append(_SCRIPTS_DIR.parents[2] / ".codex-plugin" / "plugin.json")
    for manifest in candidates:
        try:
            version: object = json.loads(manifest.read_text(encoding="utf-8")).get("version")
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(version, str) and version:
            return version
    return "(unknown)"


def _tree_digest() -> "tuple[str, int]":
    """실행 트리 digest — 같은 폴더의 `*.py`·`*.json` 전량(`__pycache__` 제외) 파일별 sha256 을
    이름 순으로 결합한 sha256[:16] 과 파일 수. 판정 입력(검사기·로스터·트리 데이터·rulepack)이 전부
    이 폴더에 살므로 «같은 버전·같은 digest = 같은 측정»이 성립한다(exact command 기록은 경로 pin 계약이 아니다)."""
    files: "list[Path]" = sorted(
        p for p in list(_SCRIPTS_DIR.glob("*.py")) + list(_SCRIPTS_DIR.glob("*.json")) if p.is_file())
    manifest: str = "".join(f"{f.name}\0{hashlib.sha256(f.read_bytes()).hexdigest()}\n" for f in files)
    return hashlib.sha256(manifest.encode("utf-8")).hexdigest()[:16], len(files)


def _toolchain_line() -> str:
    """헤더 «툴체인» 행 — 판정 도구의 정체(플러그인 버전·인터프리터·실행 트리 digest·경로)를 stdout 증거에
    싣는다(R-0365 수집 의무로 자연히 G2 증거가 된다). 출력 전용 — 판정 무접촉."""
    digest, count = _tree_digest()
    return (f"툴체인: dddjango v{plugin_version()} · py{sys.version_info[0]}.{sys.version_info[1]} · "
            f"실행 트리 digest {digest}({count}파일) · 경로 {_SCRIPTS_DIR}")


def _run_registry(target: Path,
                  sink: "Path | None" = None,
                  git_root: "Path | None" = None,
                  only: "frozenset[str] | None" = None,
                  ) -> "tuple[dict[str, int], set[str], list[dict]]":
    """로스터 전체(또는 `only` 의 검사기만)를 돌려 (검사기별 exit, 정규화 위반 라인 집합, 구조화 레코드)를 낸다.

    `only` 는 provenance 차분의 스냅숏 재실행 전용이다(후보 라인의 검사기 집합만 — 비용 한정).

    **sink 격리(T2-3)**: 검사기 서브프로세스는 부모 환경을 상속하므로, 격리하지 않으면
    앵커 실행과 현재 실행의 레코드가 **같은 파일에 뒤섞여** 소비자가 legacy 와 신규를
    구분할 수 없다(`anchor_diff._run_lines` 가 T2-1 에서 같은 이유로 받은 수리를 이 게이트만
    못 받고 있었다 — 적대 리뷰 AM#3·AN#3). 여기서는 두 채널(`DJR_FINDINGS_JSON`·
    `DJR_VIOLATIONS_DIR`)을 **둘 다** 제거하고, 요청받은 sink 만 명시 지정한다.

    **git 루트 전달(BK1 수리 2026-08-21)**: 스냅숏 사본은 .git 을 잃으므로 touched 판정이
    필요한 검사기(check-app-container)가 fail-closed 로 붕괴해 무관 legacy 를 귀속시켰다
    (세 런 공통 G2 red 의 근원). «현재» 스냅숏 실행에만 원본 루트를 넘긴다 — 스냅숏은
    working tree 의 사본이라 원본 porcelain 이 그대로 참이다. 앵커 스냅숏은 커밋된
    기준선이므로 넘기지 않는다(anchor 측 fail-closed 는 L 에만 실려 귀속을 만들지 않는다).
    """
    exits: "dict[str, int]" = {}
    lines: "set[str]" = set()
    prefixes: "tuple[str, ...]" = (str(target) + "/", str(target))
    env: "dict[str, str]" = dict(os.environ)
    env.pop(findings.ENV_VAR, None)
    env.pop(findings.ENV_DIR, None)
    env.pop(findings.ENV_GIT_ROOT, None)
    if sink is not None:
        env[findings.ENV_VAR] = str(sink)
    if git_root is not None:
        env[findings.ENV_GIT_ROOT] = str(git_root)
    for script, auto in REGISTRY:
        if only is not None and script not in only:
            continue
        proc: "subprocess.CompletedProcess[str]" = subprocess.run(
            checker_argv(sys.executable, script, str(target), auto),
            capture_output=True, text=True, env=env,
        )
        exits[script] = proc.returncode
        parsed: int = 0
        for raw in (proc.stdout + "\n" + proc.stderr).splitlines():
            m: "re.Match[str] | None" = _FINDING_RE.match(raw)
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
                      records: "list[dict]", prefixes: "tuple[str, ...]",
                      provenance: "_ProvenanceResult | None" = None) -> None:
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
        "experiment_run_id": _experiment_run_id(picked),
        "attributed_lines": attributed,
        "records": picked,
        "unmatched_lines": sorted(want - matched),
    }
    if provenance is not None:
        # flag 시에만 키 추가 — 스키마 문자열은 유지(호환 확장 · flag 없으면 payload byte 동일).
        # `attributed_lines`·`records` 는 잔여(승인 유입 제외)만이다 — 재생성 루프 입력에 유입이 섞이지 않는다.
        payload["provenance"] = provenance.as_payload()
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n귀속 레코드 sidecar → {dest} "
          f"(레코드 {len(picked)} · 대응 없는 귀속 라인 {len(want - matched)})")


def _experiment_run_id(picked: "list[dict]") -> "str | None":
    """실런 식별자를 고른다 — 레코드 우선, 없으면 **환경**.

    왜 환경 폴백이 필요한가(BK1 실측 2026-08-21): 앞선 판은 `picked` 안의 레코드에서만
    id 를 꺼냈다. 그래서 **귀속 레코드가 0건인 런은 `introduced.json` 의 id 가 `null`** 이
    된다 — 그런데 «귀속 0» 은 노출 게이트가 판정해야 할 바로 그 경우다. 실측에서 R03 의
    `introduced.json` 이 `null` 로 나왔고 `contract.json` 만 id 를 실었다(그쪽은 레코드가
    1건이었다). 사슬이 «끊기면 안 되는 지점에서 정확히 끊기는» 형태였다.

    검사기는 레코드마다 같은 환경변수로 id 를 박으므로 두 경로의 값은 일치한다. 레코드가
    있으면 그것을 쓰고(관측된 값이 정본), 없을 때만 환경을 읽는다.
    """
    from_records: "str | None" = next(
        (r.get("experiment_run_id") for r in picked if r.get("experiment_run_id")), None)
    if from_records:
        return str(from_records)
    return os.environ.get(findings.ENV_EXPERIMENT) or None


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
        "experiment_run_id": _experiment_run_id(picked),
        "records": [{k: r.get(k) for k in
                     ("checker", "contract_ref", "sentinel", "file", "message",
                      "severity", "record_id", "experiment_run_id")} for r in picked],
    }
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"계약 레코드 companion sidecar → {dest} "
          f"(신규 rule=null {len(picked)}건 · legacy 잔존 {residual}건 · "
          f"검사기 {len(by_checker)}종 — 주입 대상 아님·계수 전용)")


# ── provenance 차분(승인 유입 채널 · 2026-09-03) ────────────────────────────────────────
# 판정식·공격 정합은 모듈 docstring 「승인 유입 채널」·「provenance 차분」 절이 정본이다.

_TRAILING_LINENO_RE: "re.Pattern[str]" = re.compile(r"(:\d+)+$")
_SYNTHETIC_MARK: str = "[진단 미파싱"


@dataclass
class _ProvenanceResult:
    """분할 결과 — inflow(승인 유입)·retained(귀속 유지 사유)·chain(사슬 통계)."""

    merges: "list[anchor_diff.ApprovedMerge]"
    chain: "list[anchor_diff.ChainCommit]"
    inflow: "list[tuple[str, str, str]]" = field(default_factory=list)   # (line, L 증명 머지 sha, 파일|상호작용)
    retained: "dict[str, str]" = field(default_factory=dict)             # line → 사유
    snapshot_failures: "dict[str, str]" = field(default_factory=dict)    # sha → git 오류(진단 절 — 출력 소실 0)
    snapshots_run: int = 0
    checker_runs: int = 0

    @property
    def inflow_lines(self) -> "set[str]":
        return {line for line, _m, _k in self.inflow}

    def per_merge(self, sha: str) -> "tuple[int, int]":
        files: int = sum(1 for _l, m, k in self.inflow if m == sha and k == "파일")
        inter: int = sum(1 for _l, m, k in self.inflow if m == sha and k == "상호작용")
        return files, inter

    def chain_stats(self) -> "dict[str, object]":
        approved: "set[str]" = {m.sha for m in self.merges if m.participates}
        merges_in_chain: "list[anchor_diff.ChainCommit]" = [c for c in self.chain if c.is_merge]
        non_merges: "list[anchor_diff.ChainCommit]" = [c for c in self.chain if not c.is_merge]
        first_approved: "int | None" = next(
            (i for i, c in enumerate(self.chain) if c.sha in approved), None)
        before: "list[str]" = [c.sha for i, c in enumerate(self.chain)
                               if not c.is_merge and (first_approved is None or i < first_approved)]
        return {
            "commits": len(self.chain),
            "merges": len(merges_in_chain),
            "approved": len(approved & {c.sha for c in merges_in_chain}),
            "unapproved_merges": [c.sha for c in merges_in_chain if c.sha not in approved],
            "non_merges": len(non_merges),
            "non_merges_before_first_approved": before,
            "not_participating": [m.sha for m in self.merges if not m.participates],
            "snapshots_run": self.snapshots_run,
            "checker_runs": self.checker_runs,
            "snapshot_failures": dict(sorted(self.snapshot_failures.items())),
        }

    def as_payload(self) -> "dict[str, object]":
        return {
            "approved_merges": [
                {"sha": m.sha, "parent1": m.parent1, "parent2": m.parent2, "parent2_ref": m.parent2_ref,
                 "parent2_only_head": m.parent2_only_head,
                 "subject": m.subject, "position": m.position, "memo": m.memo}
                for m in self.merges],
            "inflow_lines": [{"line": line, "merge": m, "kind": k} for line, m, k in self.inflow],
            "retained_reasons": dict(sorted(self.retained.items())),
            "chain": self.chain_stats(),
        }


def _tree_blobs(root: Path, sha: str) -> "dict[str, str]":
    """커밋 트리의 경로→blob SHA 사전(`git ls-tree -r -z` 1회) — 디렉터리·서브모듈은 들어가지 않는다."""
    proc: "subprocess.CompletedProcess[str]" = anchor_diff.run_git(root, "ls-tree", "-r", "-z", sha)
    out: "dict[str, str]" = {}
    if proc.returncode != 0:
        return out
    for entry in proc.stdout.split("\0"):
        if not entry:
            continue
        meta, _, path = entry.partition("\t")
        parts: "list[str]" = meta.split()
        if len(parts) == 3 and parts[1] == "blob":
            out[path] = parts[2]
    return out


def _line_paths(attributed: "list[str]", records: "list[dict]",
                prefixes: "tuple[str, ...]") -> "dict[str, str | None]":
    """귀속 라인 → 대상 상대 경로. 매칭 키는 `_write_introduced` 와 같다(`findings.line_of_record` → `_normalize`).

    대응 레코드가 없으면 None(합성 fail-closed 귀속·레코드 채널 밖 진단 — 귀속 유지). `file` 의
    스냅숏 절대 경로 접두·후행 `:행[:열]` 을 걷어 경로만 남긴다 — blob 존재 여부는 호출측이 본다.
    """
    want: "set[str]" = set(attributed)
    out: "dict[str, str | None]" = {line: None for line in attributed}
    for rec in records:
        key: str = _contract_key(rec, prefixes)
        if key not in want or out.get(key) is not None:
            continue
        rel: str = _strip_snapshot(str(rec.get("file", "")), prefixes)
        rel = _TRAILING_LINENO_RE.sub("", rel).strip()
        if rel.startswith("./"):
            rel = rel[2:]
        out[key] = rel or None
    return out


def _provenance_split(root: Path, anchor_sha: str, head_sha: str,
                      merges: "list[anchor_diff.ApprovedMerge]",
                      chain: "list[anchor_diff.ChainCommit]",
                      attributed: "list[str]", records: "list[dict]",
                      prefixes: "tuple[str, ...]", td: Path) -> _ProvenanceResult:
    """빚 매칭 뒤 남은 귀속을 «승인 유입 ⊔ 귀속(잔여)» 로 분할한다 — 어떤 라인도 버려지지 않는다.

    (i) 경로 (ii) W·F1·F2 blob 판정 (iii) 후보 라인의 검사기만 M^1·M^2 스냅숏(`anchor_diff.snapshot_anchor`
    · `git_root=None` — 스냅숏은 커밋 트리라 원본 porcelain 이 참이 아니다)에서 재실행해 R_c 캐시
    (iv) L 탐색 — F1 은 전달 머지 먼저·다음 first-parent 순, F2 는 first-parent 순 · 첫 적중 중단
    (v) 후보 0 이면 스냅숏 0. 측정 무효(exit∉{0,2} ∨ 미파싱 합성행 ∨ M^1/M^2 parse-fail 집합 비대칭 ∨ 스냅숏
    실패)는 **그 머지에서의** 증명 기회만 잃는다 — L 은 ∃M 의미론이라 다른 승인 머지가 증명하면 유입이고,
    전 승인 머지가 무효/미증명이면 귀속 유지(사유 = 첫 무효 머지 · `측정 무효(M^1|M^2) — <M>` 또는
    `측정 무효(스냅숏 실패) — <M>` · R-0372 «미파싱=측정 실패» 정합). 스냅숏 실패는 `AnchorDiffUsage` 를 여기서
    포착해 진단 절에 git 오류를 싣는다 — traceback 으로 출력 전체를 잃지 않는다.
    """
    res: _ProvenanceResult = _ProvenanceResult(merges=merges, chain=chain)
    active: "list[anchor_diff.ApprovedMerge]" = sorted(
        (m for m in merges if m.participates), key=lambda m: m.position or 0)
    if not attributed:
        return res
    dirty_proc: "subprocess.CompletedProcess[str]" = anchor_diff.run_git(
        root, "status", "--porcelain", "--untracked-files=all", "-z")
    dirty: "set[str]" = set()
    for entry in dirty_proc.stdout.split("\0"):
        if len(entry) > 3:
            dirty.add(entry[3:])
    blob_cache: "dict[str, dict[str, str]]" = {}

    def blobs(sha: str) -> "dict[str, str]":
        if sha not in blob_cache:
            blob_cache[sha] = _tree_blobs(root, sha)
        return blob_cache[sha]

    head_blobs: "dict[str, str]" = blobs(head_sha)
    anchor_blobs: "dict[str, str]" = blobs(anchor_sha)
    chain_by_sha: "dict[str, int]" = {c.sha: i for i, c in enumerate(chain)}
    paths: "dict[str, str | None]" = _line_paths(attributed, records, prefixes)

    def last_toucher(p: str) -> "anchor_diff.ChainCommit | None":
        for c in reversed(chain):  # 최신 → 오래된 순
            parent_blobs: "dict[str, str]" = blobs(c.parents[0]) if c.parents else {}
            if blobs(c.sha).get(p) != parent_blobs.get(p):
                return c
        return None

    def retained_reason(p: str) -> str:
        last: "anchor_diff.ChainCommit | None" = last_toucher(p)
        if last is None:
            return "유입 증명 실패(경로 추적 불능)"
        approved: "dict[str, anchor_diff.ApprovedMerge]" = {m.sha: m for m in active}
        if last.is_merge and last.sha in approved:
            return f"충돌 해소분(M≠M^2) — {last.sha[:12]}"
        if last.is_merge:
            return f"미승인 머지 경유 {last.sha[:12]}"
        delivered_before: "anchor_diff.ApprovedMerge | None" = next(
            (m for m in active if chain_by_sha.get(m.sha, 1 << 30) < chain_by_sha[last.sha]
             and blobs(m.sha).get(p) != blobs(m.parent1).get(p)), None)
        if delivered_before is not None:
            return f"레인 커밋 수정 {last.sha[:12]}(승인 머지 {delivered_before.sha[:12]} 이후)"
        return f"비머지 커밋 경유 {last.sha[:12]}"

    # (i)(ii) 후보 선별 — candidates: line → (path, checker, kind, 전달 머지)
    candidates: "list[tuple[str, str, str, str, anchor_diff.ApprovedMerge | None]]" = []
    for line in attributed:
        checker: str = line.split(" :: ", 1)[0]
        p: "str | None" = paths.get(line)
        if p is None:
            res.retained[line] = "레코드 없음"
            continue
        if p not in head_blobs:
            res.retained[line] = "비-blob 경로"
            continue
        if p in dirty:
            res.retained[line] = "worktree 수정 중"
            continue
        deliver: "anchor_diff.ApprovedMerge | None" = next(
            (m for m in active
             if blobs(m.parent1).get(p) != blobs(m.sha).get(p)
             and blobs(m.sha).get(p) == blobs(m.parent2).get(p) == head_blobs[p]), None)
        if deliver is not None:
            candidates.append((line, p, checker, "파일", deliver))
        elif head_blobs[p] == anchor_blobs.get(p):
            candidates.append((line, p, checker, "상호작용", None))
        else:
            res.retained[line] = retained_reason(p)
    if not candidates:
        return res

    # (iii) 스냅숏·검사기 캐시 — 스냅숏 실패(git archive 불능 등)는 그 sha 의 측정을 무효로 캐시한다(재시도 0 ·
    # traceback 0 — 후보 라인은 `측정 무효(스냅숏 실패) — <M>` 로 귀속 유지, git 오류는 진단 절에).
    snap_cache: "dict[str, Path]" = {}
    parse_fail_cache: "dict[str, set[str]]" = {}
    run_cache: "dict[tuple[str, str], tuple[bool, set[str]]]" = {}  # (sha, checker) → (유효, 라인)

    def snapshot(sha: str) -> "Path | None":
        if sha in res.snapshot_failures:
            return None
        if sha not in snap_cache:
            dest: Path = td / f"snap-{sha[:12]}"
            try:
                anchor_diff.snapshot_anchor(root, sha, dest)
            except (anchor_diff.AnchorDiffUsage, OSError) as exc:  # git/tar 불능 + mkdir·디스크 오류 — traceback 0
                res.snapshot_failures[sha] = f"{type(exc).__name__}: {str(exc).strip()}"
                return None
            snap_cache[sha] = dest
            parse_fail_cache[sha] = {
                l.split(" :: ", 1)[1].split(":", 1)[0] for l in _parse_fail_findings(dest)}
            res.snapshots_run += 1
        return snap_cache[sha]

    def run(sha: str, checker: str) -> "tuple[bool, set[str]]":
        key: "tuple[str, str]" = (sha, checker)
        if key not in run_cache:
            snap: "Path | None" = snapshot(sha)
            if snap is None:
                run_cache[key] = (False, set())
            else:
                exits, lines, _recs = _run_registry(snap, only=frozenset({checker}))
                res.checker_runs += 1
                valid: bool = exits.get(checker) in (0, 2) and not any(_SYNTHETIC_MARK in l for l in lines)
                run_cache[key] = (valid, lines)
        return run_cache[key]

    # (iv) L 탐색 — ∃M: 어느 머지든 증명하면 유입 · 전건 무효/미증명이면 귀속 유지
    for line, p, checker, kind, deliver in candidates:
        order: "list[anchor_diff.ApprovedMerge]" = (
            [deliver] + [m for m in active if m is not deliver]) if deliver is not None else list(active)
        proven: "str | None" = None
        invalid: "list[str]" = []
        for m in order:
            ok1, r1 = run(m.parent1, checker)
            ok2, r2 = run(m.parent2, checker)
            if m.parent1 in res.snapshot_failures or m.parent2 in res.snapshot_failures:
                invalid.append(f"측정 무효(스냅숏 실패) — {m.sha[:12]}")
                continue
            symmetric: bool = parse_fail_cache[m.parent1] == parse_fail_cache[m.parent2]
            if not (ok1 and ok2 and symmetric):
                sides: "list[str]" = []
                if not ok1 or (not symmetric and parse_fail_cache[m.parent1] - parse_fail_cache[m.parent2]):
                    sides.append("M^1")
                if not ok2 or (not symmetric and parse_fail_cache[m.parent2] - parse_fail_cache[m.parent1]):
                    sides.append("M^2")
                invalid.append(f"측정 무효({'|'.join(sides) or 'M^1|M^2'}) — {m.sha[:12]}")
                continue
            if line in r2 and line not in r1:
                proven = m.sha
                break
        if proven is not None:
            res.inflow.append((line, proven, kind))
        elif invalid:
            res.retained[line] = invalid[0]
        elif kind == "파일":
            # 전달 머지보다 앞선 «미승인» 머지가 p 를 바꿨다면 진단은 그때 들어왔을 수 있다 — 목록 누락을
            # 표면화한다(부분 목록 실측: 이중 원인과 구별 불가 — 발주자가 목록을 보완하면 L 이 그 머지에서 선다).
            earlier_unapproved: "list[str]" = [
                c.sha for c in chain
                if c.is_merge and c.sha not in {m.sha for m in active}
                and deliver is not None and chain_by_sha[c.sha] < chain_by_sha.get(deliver.sha, 1 << 30)
                and blobs(c.sha).get(p) != blobs(c.parents[0]).get(p)]
            hint: str = (f" — 미승인 머지 {earlier_unapproved[-1][:12]} 경유 가능" if earlier_unapproved else "")
            res.retained[line] = f"유입 증명 실패(이중 원인{hint})"
        else:
            res.retained[line] = "상호작용 미증명"
    return res


def main(argv: "list[str]") -> int:
    ap: _UsageParser = _UsageParser(add_help=True)
    ap.add_argument("target")
    ap.add_argument("--anchor", required=False, default=None,
                    help="차분 기준(대장 앵커 또는 build-start 앵커) — actor 가 임의로 고르지 않는다")
    ap.add_argument("--legacy-debt-file", default=None)
    ap.add_argument(anchor_diff.APPROVED_MERGE_FLAG, dest="approved_merge_file", default=None,
                    help="발주자 승인 «main→레인 머지» 목록(`<SHA> [메모]`) — provenance 차분으로 증명된 "
                         "승인 유입을 exit 에서 빼되 «승인 유입» 절로 반드시 보고한다(git TARGET 전용)")
    ap.add_argument("--introduced-json", default=None,
                    help="귀속(N∖L) 위반의 구조화 레코드를 이 경로에 sidecar 로 쓴다 — "
                         "재생성 루프의 유일한 입력(legacy 잔존은 구조적으로 배제된다)")
    ap.add_argument("--contract-json", default=None,
                    help="`rule=null`(선행 계약·센티널) 레코드의 계수를 companion sidecar 로 "
                         "쓴다 — 주입 대상이 아니라 «계수 후 유효 유지»(개정 9)의 원자료")
    ns: argparse.Namespace = ap.parse_args(argv)

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

    approved_path: "Path | None" = None
    if ns.approved_merge_file is not None:
        approved_path = Path(ns.approved_merge_file)
        if not approved_path.is_file():
            print(f"재료 결손: 승인 머지 목록 {approved_path} 없음", file=sys.stderr)
            return 1

    is_git: bool = anchor_diff.is_git_worktree(root)
    if approved_path is not None and not is_git:
        print(f"사용 오류: {anchor_diff.APPROVED_MERGE_FLAG} 은 git 저장소 TARGET 에서만 쓸 수 있다 — "
              "provenance 재료(커밋 blob·first-parent 사슬)가 없다", file=sys.stderr)
        return 1
    merges: "list[anchor_diff.ApprovedMerge]" = []
    chain: "list[anchor_diff.ChainCommit]" = []
    provenance: "_ProvenanceResult | None" = None

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
            exits_n, n_set, n_records = _run_registry(cur, sink_n)  # 원본도 비-git — 넘길 루트 없음
            n_set |= _parse_fail_findings(cur)
            l_set: "set[str]" = set()
            exits_l: "dict[str, int]" = {}
            anchor_sha: str = "(비-git)"
        else:
            if ns.anchor is None:
                print("사용 오류: git 저장소에는 --anchor <ref> 가 필수다 — 라운드=대장 앵커 · "
                      "파이프라인=Phase 2 진입 직전 기록된 build-start 앵커", file=sys.stderr)
                return 1
            rev: "subprocess.CompletedProcess[str]" = anchor_diff.run_git(
                root, "rev-parse", "--verify", f"{ns.anchor}^{{commit}}")
            if rev.returncode != 0:
                print(f"사용 오류: 앵커 {ns.anchor!r} resolve 불능 — {rev.stderr.strip()}", file=sys.stderr)
                return 1
            anchor_sha = rev.stdout.strip()
            head: str = anchor_diff.run_git(root, "rev-parse", "HEAD").stdout.strip()
            dirty: bool = bool(anchor_diff.run_git(root, "status", "--porcelain").stdout.strip())
            if anchor_sha == head and not dirty:
                print("사용 오류: 앵커=HEAD 이고 working tree 가 clean — 차분이 공허하다. "
                      "게이트는 구현 커밋 «전»에 돌리거나, 런 시작점 앵커를 지정하라(공허 green 차단).",
                      file=sys.stderr)
                return 1
            if anchor_diff.run_git(root, "merge-base", "--is-ancestor", anchor_sha, head).returncode != 0:
                # 상시 진단(병리 시만 발화 · exit 무변) — 앵커가 이 가지의 과거가 아니면 차분은
                # «이번 런»이 아니라 두 가지의 차이를 잰다. 승격은 별도 결정 게이트.
                print(f"주의: 앵커 {anchor_sha[:12]} 는 HEAD {head[:12]} 의 조상이 아니다 — "
                      "차분이 «이번 런의 변경»을 재지 않을 수 있다(앵커 재료를 확인하라 · exit 무변)")
            if approved_path is not None:
                try:
                    merges, chain = anchor_diff.load_approved_merges(approved_path, root, anchor_sha, head)
                except anchor_diff.AnchorDiffUsage as exc:
                    print(f"사용 오류: {exc}", file=sys.stderr)
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
            exits_n, n_set, n_records = _run_registry(cur, sink_n, git_root=root)
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

        if approved_path is not None:
            # 순서: attributed → 빚 분리 → provenance 분리(빚 우선) → 잔여 = exit 근거.
            provenance = _provenance_split(root, anchor_sha, head, merges, chain,
                                           attributed, n_records, cur_prefixes, Path(td))
            inflow_lines: "set[str]" = provenance.inflow_lines
            attributed = [line for line in attributed if line not in inflow_lines]

    print(f"# registry_gate — 판정 차분 · {root.name} · 앵커 {anchor_sha[:12]}")
    print(_toolchain_line())
    print("**귀속 0 ≠ 전체 clean** — 이 게이트는 «이번 런이 위반을 늘렸나»만 판정한다(legacy 격리).")
    print("| 검사기 | anchor | current |")
    print("|---|---|---|")
    for script, _auto in REGISTRY:
        print(f"| `{script}` | {exits_l.get(script, '—')} | {exits_n.get(script, '—')} |")
    print(f"\n== 귀속(N∖L) {len(attributed)}건 ==")
    for line in attributed:
        print(f"  {line}")
        if provenance is not None:
            print(f"    ↳ 귀속 유지: {provenance.retained.get(line, '판정 미도달')}")
    if debt:
        print(f"\n== 이관 빚(승인 목록 매칭 — exit 제외·기록 의무) {len(debt)}건 ==")
        for line in debt:
            print(f"  {line}")
    if provenance is not None:
        _print_inflow(provenance)
    by_checker: "dict[str, int]" = {}
    for line in residual:
        by_checker[line.split(" :: ", 1)[0]] = by_checker.get(line.split(" :: ", 1)[0], 0) + 1
    print(f"\n== legacy 잔존(L∩N) {len(residual)}건 · 해소(L∖N) {len(resolved)}건 ==")
    for script in sorted(by_checker):
        print(f"  {script}: {by_checker[script]}")
    if provenance is not None:
        _print_provenance_diag(provenance, anchor_sha)
    if ns.introduced_json is not None:
        _write_introduced(Path(ns.introduced_json), anchor_sha, attributed,
                          n_records, cur_prefixes, provenance)
    if ns.contract_json is not None:
        _write_contract(Path(ns.contract_json), anchor_sha, n_records,
                        l_records, cur_prefixes, anc_prefixes)

    tail: str = f"(승인 유입 {len(provenance.inflow)}건 제외)" if provenance is not None else ""
    print(f"\n판정: 귀속 {len(attributed)}건 → {'green(신규 위반 없음)' if not attributed else 'red'}{tail}")
    return 0 if not attributed else 2


def _print_inflow(prov: _ProvenanceResult) -> None:
    """«승인 유입» 절 — 머지 표(subject·부모·^2 ref 도달성 — 역방향 머지 오기입 가시화) + 라인별 L 증명 머지."""
    print(f"\n== 승인 유입(발주자 승인 머지 경유 · provenance 증명 — exit 제외·기록 의무) {len(prov.inflow)}건 ==")
    for m in prov.merges:
        if not m.participates:
            print(f"  [M {m.sha[:12]}] {m.subject} · 앵커 이전 — 판정 불참")
            continue
        files, inter = prov.per_merge(m.sha)
        print(f"  [M {m.sha[:12]}] {m.subject} · ^1 {m.parent1[:12]} · ^2 {m.parent2[:12]}({m.parent2_ref}) · "
              f"파일 {files} · 상호작용 {inter}")
        if m.parent2_only_head:
            print(f"    ↳ 주의: ^2 {m.parent2[:12]} 를 포함하는 ref 가 HEAD 브랜치뿐 — 역방향/합성 머지 의심"
                  "(발주자 확인 — 등재 전 `^2` 가 main(상류) 이력에 있는지 확인 · exit 무변)")
    for line, m, kind in prov.inflow:
        print(f"  {line}")
        print(f"    ↳ 유입: {m[:12]}(L 증명) · {'파일 verbatim' if kind == '파일' else '상호작용'}")


def _print_provenance_diag(prov: _ProvenanceResult, anchor_sha: str) -> None:
    """«provenance 진단» 절 — 사슬 통계·스냅숏 실행 수·«비머지 커밋이 첫 승인 머지보다 앞섬» 진단."""
    st: "dict[str, object]" = prov.chain_stats()
    print("\n== provenance 진단 ==")
    print(f"  first-parent 사슬 {anchor_sha[:12]}..HEAD: 커밋 {st['commits']} · 머지 {st['merges']}"
          f"(승인 {st['approved']} · 미승인 {len(st['unapproved_merges'])}) · 비머지 {st['non_merges']}")
    print(f"  스냅숏 실행 {st['snapshots_run']} · 검사기 재실행 {st['checker_runs']}")
    for sha, why in prov.snapshot_failures.items():
        print(f"  스냅숏 실패(측정 무효 — 해당 머지의 후보 라인은 귀속 유지): {sha[:12]} — {why}")
    unapproved: "list[str]" = list(st["unapproved_merges"])  # type: ignore[arg-type]
    if unapproved:
        print(f"  미승인 머지: {' '.join(sha[:12] for sha in unapproved)}")
    not_participating: "list[str]" = list(st["not_participating"])  # type: ignore[arg-type]
    if not_participating:
        print(f"  앵커 이전 목록(판정 불참): {' '.join(sha[:12] for sha in not_participating)}")
    before: "list[str]" = list(st["non_merges_before_first_approved"])  # type: ignore[arg-type]
    if before and st["approved"]:
        shown: str = " ".join(sha[:12] for sha in before[:6]) + (f" 외 {len(before) - 6}" if len(before) > 6 else "")
        print(f"  진단: 비머지 커밋 {len(before)}건({shown})이 첫 승인 머지보다 앞선다 — 레인 자신의 커밋이면 정상이고 "
              "main 직접 커밋이면 앵커가 레인 분기점보다 앞선 것이다(도구는 둘을 구별하지 않는다 · "
              "epoch 재앵커는 발주자 결정 · 도구는 재앵커하지 않는다)")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
