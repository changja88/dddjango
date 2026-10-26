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

- **목록만 줄어든 줄**(F4-99): 줄 번호 없는 줄이 앵커 줄과 문자열 목록 칸(`['a', 'b']`)만 다르고 칸마다 부분집합이며
  그 주어 파일(레코드 경로)이 앵커 · 현재 사본에서 바이트까지 같으면 잔존(L∩N)으로 센다 — 다른 파일(합집합)이
  바뀌어 목록이 준 것이지 늘린 위반이 아니다. 짝은 1:1 이고 legacy 잔존 절에 앵커 줄과 함께 찍는다.
- **사본 속 링크**(F4-97 · F4-98): 앵커 · 승인 유입 측정 사본에서 사본 밖을 가리키는 링크가 모두 숨김 경로
  (문서 입력 `.dddjango/<폴더>/{scope,design-spec}.md` 와 그 조상은 빼고)에 있으면 그 링크를 걷고 잰다. 하나라도
  그 밖이면 지금처럼 그 사본을 증거로 쓰지 않는다(fail-closed · 판정 줄에 «잴 수 없어 남긴» 수를 따로 적는다).
- **사본의 숨김 경로**: 현재 쪽 사본이 숨김 경로를 복사하지 않으므로 앵커 · 승인 유입 측정 사본도 숨김 경로(같은 문서
  입력 · 조상은 남김)를 빼고 푼다(`anchor_diff.snapshot_anchor(drop_hidden=True)`). 남은 링크가 뺀 경로를 지나면
  그 사본만 지금처럼 전체를 푼다.
- **임시 사본**: 사본은 `<기본 임시 폴더>/dddjango/` 아래 주인 표식이 붙은 폴더에 둔다. 실행을 시작할 때 주인이 죽은
  폴더(끊긴 실행이 남긴 사본)를 지우고, 지운 것이 있을 때만 stderr 에 `정리:` 한 줄을 낸다(표준 출력 · sidecar 무변).
  `--temp-report` 는 판정 없이 남은 사본 · keep 사본 · 옛 판 꼴 사본의 개수 · 크기 한 줄만 낸다(지우지 않는다).

- **앵커는 actor 가 고르지 않는다** — 라운드에선 대장의 앵커 커밋, 파이프라인에선
  Phase 2 진입 직전 기록되는 build-start 앵커(`commands/dddjango.md` 절차 소유)를
  호출자가 그대로 넘긴다. 앵커=HEAD 이고 working tree 가 clean 이면 차분이 공허하므로
  사용 오류(exit 1)다 — 「커밋 뒤 게이트」로 판정을 비우는 우회를 막는다.
- **귀속 0 ≠ 전체 clean** — legacy 잔존(L∩N)은 exit 에 안 들어가되 항상 보고한다
- **ⓓ 앵커 차분 채널**(2026-09-04 현장 보고 3 ⓔ2): `[ⓓ#N]` 후보 라인도 같은 정규화로 앵커 L′·현재 N′ 를 갈라
  «ⓓ 신규(N′∖L′)» 절(+검사기별 legacy 계수)에 인쇄하고 sidecar 에 `candidate_lines`·`candidate_records` 로
  싣는다 — exit 불산입 · `records`(위반)와 분리 · ⓓ 가 하나도 없는 저장소는 출력·sidecar byte 무변.
  (침묵 금지). BC 하나가 clean 한지는 `bc_registry_run.py`(그림자 전수)가 답한다 —
  두 도구는 같은 로스터(`checker_registry.py`)를 쓰되 묻는 것이 다르다.
- **이관 빚 채널**: `--legacy-debt-file` 의 사용자 승인 목록(줄 형식: `#<규칙> <부분문자열>`)
  에 맞는 귀속은 exit 에서 빼되 «빚» 절로 반드시 보고한다 — 빚은 기록 근거이지 legacy
  모양을 «추가로» 복사할 근거가 아니다. 번호 없는 줄 `= <검사기 파일> :: <줄>`은
  scope 렌더 전용 — 이 게이트의 차분 집합엔 맞을 줄이 없다.
- 비-git TARGET 은 fail-closed: 차분 불능이므로 현재 위반 전부를 귀속으로 본다.
- 검사기가 red 인데 위반 라인을 못 파싱하면 그 검사기 몫을 합성 귀속으로 남긴다(fail-closed).
- **승인 유입 채널(provenance 차분 · 2026-09-03)**: `--approved-merge-file` 의 발주자 승인
  «main→레인 머지» 목록(줄 형식: `<SHA> [메모]`)이 주어지면, 빚 매칭 뒤 남은 귀속 라인 ℓ
  (파일 p · 검사기 c)마다 다음을 결정적으로 증명한 것만 exit 에서 빼고 «승인 유입» 절로 보고한다:

    승인 유입(ℓ) ⟺ (W(p) ∧ (F1(p) ∨ F2(p)) ∨ G(p)) ∧ ∃M: L(ℓ, M) ∧ P(ℓ, M)
    W  worktree 의 p 가 HEAD 와 동일(porcelain 공백)
    F1 ∃M∈𝓜: blob(M^1:p) ≠ blob(M:p) ∧ blob(M:p) = blob(M^2:p) = blob(HEAD:p)
       — 승인 머지의 incoming 측에서 verbatim 전달·레인 미수정(충돌 해소분은 M≠M^2 라 탈락)
    F2 blob(HEAD:p) = blob(anchor:p) — 파일 무변 = «상호작용 서명»(검사기 환경만 바뀜)
    G  깨끗한 상대 .py 경로 · HEAD와 작업 트리에 없음 · 부모는 HEAD의 tree(부재 주어)
    L  ℓ ∈ R_c(M^2) ∖ R_c(M^1) — 검사기 c 를 M^2(incoming)·M^1(레인 측 직전)
       스냅숏에서 재실행해 «incoming 측에는 있고 레인 측 직전에는 없던» 진단임을 증명
    P  M 뒤 미승인 머지 없음 · 뒤 승인 머지의 ^2에도 있음 · 병합 결과부터 HEAD까지 사슬마다 있음
       사슬은 앞 커밋과 다른 트리 64개까지 잰다. 측정 불능·한도 초과는 귀속을 유지한다.

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
  «발주자 소유 목록 ∧ 주어 판정 ∧ R(M^2)∖R(M^1) ∧ 증명 머지 뒤 조건»이며 빚 채널과 같은 «사용자 승인 입력»
  부류다(도구는 목록의 소유를 검증하지 않는다 — 앵커·빚 목록과 같은 자리). 위 다섯 계열 공격과의
  정합: ① base 자기 선택 — 앵커도 승인 목록도 actor 밖이고, 앵커는 HEAD first-parent 사슬 위
  (도달 필수)·머지는 그 구간 안이어야 한다(역방향 합성·타 가지 머지는 형식 오류) ② 부재(#488)
  위반 — 없는 파일은 G(깨끗한 상대 .py · HEAD와 작업 트리에 없음 · 부모는 HEAD의 tree)와
  P(두 부모 차분 뒤 병합 결과·사슬 이어짐)가 서야 유입, 그 밖은 귀속 유지 ③ 출력 형식 이질 — `findings` 레코드가 단일 출처이고 대응
  레코드가 없으면 귀속 유지 ④ 빈 변경 집합 — 변경 집합을 쓰지 않고 L 이 incoming 측 존재를
  요구한다 ⑤ .gitignore 은닉 — 커밋 blob 이 없으면 F1·F2 가 성립하지 않는다. 귀속 목록을
  경로 필터(sed/grep)로 나눈 서술은 게이트 증거가 아니다 — 유입 분리는 이 채널뿐이다.
  상호작용 위반(F2)은 증명되면 유입, 아니면 `상호작용 미증명` 으로 귀속 유지다(철회할 변경이
  없으므로 처방은 STOP_FOR_USER_APPROVAL — 빚 등재·상류 해소·레인 설계 반송).
  역방향(main←lane) 머지는 HEAD=lane 이면 first-parent 사슬 밖이라 exit 1 이지만, 발주자가 합성
  머지를 레인 사슬에 올린 잔여 경로는 도구가 구별하지 못한다 — 머지 표에 `^2` 의 ref 도달성을 싣고
  `^2` 를 포함하는 ref 가 HEAD 브랜치뿐이면 «역방향/합성 머지 의심» 진단 1행을 낸다(exit 무변 ·
  custody 는 발주자 소유).

묶음 이동 채널(2.28.0 의미 묶음 · `--group-moves <산출물 폴더>`)
  `folder_group.expected_moves`(앵커 · 승인 병합 · `refactor-scope.md` 결정 · 이관 빚 목록)로 계산한 «앵커 자리 → 끝 자리»와
  실제 이동(병합 몫 `앵커 → T₀′` 과 레인 이동 `T₀′ → 지금` 을 이은 `A → C` — 같은 `actual_moves`)의 교집합이 쌍이다. 실제에만
  있는 쌍은 버리고 «계산 밖 이동» 으로 싣는다(그 파일의 옛 위반은 귀속). 정규화 · F4-99 · 빚 · 승인 유입 **뒤** 남은 귀속 줄 ℓ 마다
  해소(L∖N) 줄 ℓ′ 의 «옛 경로 → 새 경로 · 옛 점 경로 → 새 점 경로» 치환이 ℓ 과 글자로 같으면 1:1 로 짝지어 «이동 따라 옮긴
  legacy» 절로 보낸다(exit 밖 · 항상 보고 · sidecar `group_moves`). 산출물 폴더의 `build_anchor` 는 `--anchor` 와 같은 커밋 ·
  `approved-merges.txt` 는 `--approved-merge-file` 과 같은 목록이어야 한다(아니면 사용 오류). flag 가 없으면 출력 · sidecar 무변.
- **묶음 부모의 캐시만 남은 폴더**: 값 객체 · 엔티티 · 이벤트 · 예외 · 서비스 칸의 하위 폴더에 캐시만 남았으면 현재 사본에서
  뺀다(지운 묶음이 빈 폴더로 남아 거짓 위반을 내지 않게 — 설계 7.4 의 21).

사용: python3 registry_gate.py <저장소 루트> --anchor <ref> [--legacy-debt-file <path>]
      [--approved-merge-file <path>] [--introduced-json <path>] [--contract-json <path>]
      [--group-moves <산출물 폴더>]
      python3 registry_gate.py --temp-report
환경(선택): DJR_REGISTRY_WORKERS=<양의 정수> — 검사기 동시 실행 수. 없으면 빈 코어 수(CPU − 1분 부하 · 1~8)다.
      앵커·현재 두 벌이 한 한도를 나눠 쓴다. 출력·sidecar 는 워커 수와 무관하다(REGISTRY 순서 병합).
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
import stat
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from pathlib import Path

_SCRIPTS_DIR: Path = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS_DIR))
import anchor_diff  # noqa: E402  — git·앵커 스냅숏·빚 로더·빚 매칭 공용(복제 통합)
import checker_target  # noqa: E402
import standard_tree as tree  # noqa: E402
import findings  # noqa: E402  — sink 환경변수 이름·라인 재구성 문법의 단일 출처
from checker_registry import REGISTRY, checker_argv  # noqa: E402

_FINDING_RE: "re.Pattern[str]" = re.compile(r"^\s*(\[#\d+\].*)$")
_CANDIDATE_RE: "re.Pattern[str]" = re.compile(r"^\s*(\[ⓓ#\d+\].*)$")  # ⓓ 후보 — 앵커 차분만(exit 불산입)
_LINENO_RE: "re.Pattern[str]" = re.compile(r":\d+")
_IGNORE_COPY: "tuple[str, ...]" = (
    ".git", ".venv", "venv", "__pycache__", "*.pyc", "node_modules",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "staticfiles",
    # F-C: 숨김 경로는 도구·하네스 영역 — 검사 표면에서 제외한다.
    # 멱등성 검사 입력인 .dddjango/*/{scope,design-spec}.md 만 복사 뒤 별도로 보존한다.
    ".*", "site-packages", "build", "dist",
)


class _UsageParser(argparse.ArgumentParser):
    """usage 오류를 문면 계약(exit 1)으로 — argparse 기본 exit 2 는 «위반»과 겹친다
    (check-composition-root `_UsageParser` 패턴 이식)."""

    def error(self, message: str) -> None:
        print(f"사용 오류: {message}", file=sys.stderr)
        raise SystemExit(1)


def _snapshot_cache_instances(root: Path) -> set[Path]:
    """골격의 BC 내부 선택 폴더 칸만 원 작업 트리에서 수집한다."""
    omitted: set[Path] = set()
    token = re.compile(r"<([a-z_]+)>")

    def walk(directory: Path, row: tree.Row, bindings: dict[str, str]) -> None:
        if directory.is_symlink() or not directory.is_dir():
            return
        children = tree.children(row)
        fixed = {tree.concrete_name(c, bindings).rstrip("/"): c for c in children
                 if tree.is_dir(c) and c.kind in ("fixed", "reappear")}
        optional = next((c for c in children if tree.is_dir(c) and c.kind == "placeholder"
                         and "/" not in c.name.rstrip("/")), None)
        files = [tree.concrete_name(c, bindings) for c in children if not tree.is_dir(c)]
        groupable = any(c.groupable for c in children if not tree.is_dir(c))
        for child in sorted(directory.iterdir()):
            if not child.is_dir() or child.is_symlink() or child.name.startswith(".") or child.name == "__pycache__":
                continue
            if child.name in fixed:
                walk(child, fixed[child.name], bindings)
                continue
            # 파일의 승격 실현은 선택 폴더 인스턴스가 아니다. 묶음 부모의 캐시만 남은 하위 폴더(지운 묶음 · 승격)는 뺀다(7.4 의 21).
            if any(re.fullmatch(token.sub(".+", name), child.name + ".py") for name in files):
                if groupable and checker_target.cache_only_instance(child):
                    omitted.add(child.relative_to(root))
                continue
            if optional is None:
                continue
            pattern = optional.name.rstrip("/")
            if not re.fullmatch(token.sub(".+", pattern), child.name):
                continue
            if checker_target.cache_only_instance(child):
                omitted.add(child.relative_to(root))
                continue
            values = dict(bindings)
            for name in token.findall(pattern):
                values[name] = child.name.removesuffix("_adapter") if pattern.endswith("_adapter") else child.name
            walk(child, optional, values)

    ignore = shutil.ignore_patterns(*_IGNORE_COPY)
    for application in sorted(root.rglob("application")):
        if not application.is_dir() or application.is_symlink() \
                or ignore(str(root), list(application.relative_to(root).parts)):
            continue
        for bc in sorted(application.iterdir()):
            if not bc.name.startswith("."):
                walk(bc, tree.ROWS[0], {"bounded_context": bc.name})
    return omitted


def _snapshot_current(root: Path, dest: Path) -> None:
    """working tree 를 비-git 사본으로 복사한다(무거운 비-소스 디렉터리 제외)."""
    omitted = _snapshot_cache_instances(root)
    ignore = shutil.ignore_patterns(*_IGNORE_COPY)

    def ignore_current(directory: str, names: list[str]) -> set[str]:
        parent = Path(directory).relative_to(root)
        return ignore(directory, names) | {name for name in names if parent / name in omitted}

    shutil.copytree(root, dest, ignore=ignore_current)
    for name in anchor_diff.DOC_INPUTS:
        for source in sorted((root / ".dddjango").glob(f"*/{name}")):
            if source.is_file():
                target = dest / source.relative_to(root)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)


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


_STR_LIST_RE: "re.Pattern[str]" = re.compile(r"\[(?:'[^'\\\n]*'(?:, '[^'\\\n]*')*)?\]")


def _list_shrunk(new: "list[str]", gone: "list[str]") -> "dict[str, str]":
    """N∖L 줄 → 짝 L∖N 줄 — 두 줄이 문자열 목록 칸(`['a', 'b']`)만 다르고 칸마다 N 쪽이 L 쪽의 부분집합일 때(1:1)."""
    def split(line: str) -> "tuple[str, list[set[str]]]":
        found: "list[set[str]]" = [set(ast.literal_eval(m.group(0))) for m in _STR_LIST_RE.finditer(line)]
        return _STR_LIST_RE.sub("[…]", line), found
    file_level: "re.Pattern[str]" = re.compile(r"^\S+ :: \[(?:ⓓ)?#\d+\] [^:\s]+: ")
    pool: "dict[str, list[tuple[str, list[set[str]]]]]" = {}
    for line in gone:
        if not file_level.match(line):
            continue
        key, found = split(line)
        if found:
            pool.setdefault(key, []).append((line, found))
    pairs: "dict[str, str]" = {}
    for line in new:
        if not file_level.match(line):
            continue
        key, found = split(line)
        if not found:
            continue
        for index, (old, old_found) in enumerate(pool.get(key, [])):
            if len(old_found) == len(found) and all(a <= b for a, b in zip(found, old_found)):
                pairs[line] = old
                del pool[key][index]
                break
    return pairs


def _same_file(anchor: Path, current: Path, rel: "str | None") -> bool:
    """앵커 사본과 현재 사본의 `rel` 이 둘 다 링크 아닌 일반 파일이고 바이트까지 같은가 — 모르면 거짓(짝 안 지음)."""
    if not rel:
        return False
    a: Path = anchor / rel
    b: Path = current / rel
    try:
        return (a.is_file() and b.is_file() and not a.is_symlink() and not b.is_symlink()
                and a.read_bytes() == b.read_bytes())
    except OSError:
        return False


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


_WORKERS_ENV: str = "DJR_REGISTRY_WORKERS"
_MAX_AUTO_WORKERS: int = 8
_POOL_LOCK: threading.Lock = threading.Lock()
_pool: "ThreadPoolExecutor | None" = None


def _registry_workers() -> int:
    """검사기 동시 실행 수 — `DJR_REGISTRY_WORKERS`(양의 정수)가 있으면 그 값, 없으면 빈 코어 수(1~8).

    빈 코어 = CPU 수 − 1분 부하 평균이라, 한 기계에 레인이 여럿 돌아 코어가 꽉 차면 스스로 1~2개로
    줄어 다른 레인을 밀어내지 않는다. 부하를 잴 수 없는 플랫폼(`os.getloadavg` 부재 · 측정 불능)은
    부하 미상으로 보고 CPU 수 상한만 쓴다. 출력은 워커 수와 무관하다."""
    raw: str = os.environ.get(_WORKERS_ENV, "").strip()
    if raw:
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print(f"주의: {_WORKERS_ENV}={raw!r} 는 양의 정수가 아니다 — 자동 워커 수를 쓴다", file=sys.stderr)
    cpu: int = os.cpu_count() or 1
    try:
        idle: int = int(cpu - os.getloadavg()[0])
    except (OSError, AttributeError):
        idle = cpu
    return max(1, min(_MAX_AUTO_WORKERS, idle))


def _checker_pool() -> ThreadPoolExecutor:
    """검사기 자식 프로세스의 프로세스 단위 한도 — 앵커·현재 두 벌과 provenance 재실행이 한 풀을 나눠 쓴다."""
    global _pool
    with _POOL_LOCK:
        if _pool is None:
            _pool = ThreadPoolExecutor(max_workers=_registry_workers(), thread_name_prefix="registry-gate")
        return _pool


def _run_checker(script: str, target: Path, auto: bool,
                 env: "dict[str, str]") -> "subprocess.CompletedProcess[str]":
    return subprocess.run(
        checker_argv(sys.executable, script, str(target), auto),
        capture_output=True, text=True, env=env,
    )


def _merge_sink_parts(sink: Path, parts: "list[Path]") -> None:
    """작업별 sink 조각을 주어진(REGISTRY) 순서로 sink 에 이어 붙인다 — 직렬 append 와 같은 바이트.

    디코드하지 않고 바이트 그대로 잇는다: 깨진 줄 하나가 판정을 죽이지 않는다는 뒤 읽기의 계약
    (`errors="replace"` · 깨진 JSON 줄 건너뜀)을 병합 단계가 먼저 깨면 안 된다."""
    present: "list[Path]" = [part for part in parts if part.is_file()]
    if not present:
        return
    with sink.open("ab") as merged:
        for part in present:
            merged.write(part.read_bytes())
            part.unlink()


def _run_registry(target: Path,
                  sink: "Path | None" = None,
                  git_root: "Path | None" = None,
                  only: "frozenset[str] | None" = None,
                  unclassifiable: "set[str] | None" = None,
                  ) -> "tuple[dict[str, int], set[str], list[dict], set[str]]":
    """로스터 전체(또는 `only` 의 검사기만)를 돌려 (검사기별 exit, 정규화 위반 라인 집합, 구조화 레코드)를 낸다.

    `only` 는 provenance 차분의 스냅숏 재실행 전용이다(후보 라인의 검사기 집합만 — 비용 한정).
    `unclassifiable` 에는 원 출력·레코드 채널이 무효인 검사기를 기록한다(자매 분류만 금지).

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

    **병렬 실행(속도 개선 C1⑵ · 2026-10-01)**: 작업을 공용 풀(`_checker_pool`)에 모두 올리고
    **전부 끝난 뒤** REGISTRY 순서로 거둔다 — 작업 예외는 REGISTRY 순서 첫 예외로 올라오고(직렬의
    첫 실패와 같은 예외), 실행 중 작업이 호출측 임시 폴더 정리와 겹치지 않는다. 검사기마다 sink
    조각(`<sink>.<REGISTRY 인덱스>.part`)을 따로 주고 REGISTRY 순서로 바이트 병합하므로 sink·exit·
    라인 집합이 직렬 실행과 같다(검사기끼리 쓰는 파일은 sink 뿐이다).
    """
    exits: "dict[str, int]" = {}
    lines: "set[str]" = set()
    cands: "set[str]" = set()  # ⓓ 후보 라인(정규화) — N′/L′
    prefixes: "tuple[str, ...]" = (str(target) + "/", str(target))
    env: "dict[str, str]" = dict(os.environ)
    env.pop(findings.ENV_VAR, None)
    env.pop(findings.ENV_DIR, None)
    env.pop(findings.ENV_GIT_ROOT, None)
    if git_root is not None:
        env[findings.ENV_GIT_ROOT] = str(git_root)
    jobs: "list[tuple[str, bool, Path | None]]" = [
        (script, auto, sink.with_name(f"{sink.name}.{index:02d}.part") if sink is not None else None)
        for index, (script, auto) in enumerate(REGISTRY)
        if only is None or script in only
    ]
    futures: "list[Future[subprocess.CompletedProcess[str]]]" = [
        _checker_pool().submit(_run_checker, script, target, auto,
                               env if part is None else {**env, findings.ENV_VAR: str(part)})
        for script, auto, part in jobs
    ]
    wait(futures)
    procs: "list[subprocess.CompletedProcess[str]]" = [future.result() for future in futures]
    # 차분 라인·출력은 그대로 둔다. 원 출력과 검사기별 sink의 유효성만 별도 전달한다.
    if unclassifiable is not None:
        for (script, _auto, part), proc in zip(jobs, procs):
            raw_output: str = proc.stdout + "\n" + proc.stderr
            failed: bool = ("[분석]" in raw_output or "구조화 레코드 채널 비활성" in raw_output)
            numeric_records: int = 0
            if part is not None and part.is_file():
                for raw in part.read_text(encoding="utf-8", errors="replace").splitlines():
                    if not raw.strip():
                        continue
                    try:
                        rec: object = json.loads(raw)
                    except json.JSONDecodeError:
                        failed = True
                        continue
                    if not isinstance(rec, dict):
                        failed = True
                        continue
                    numeric_records += int(_FINDING_RE.match(findings.line_of_record(rec)) is not None)
            if sink is not None:
                failed |= numeric_records != sum(_FINDING_RE.match(raw) is not None
                                                  for raw in raw_output.splitlines())
            if failed:
                unclassifiable.add(script)
    if sink is not None:
        _merge_sink_parts(sink, [part for _script, _auto, part in jobs if part is not None])
    for (script, _auto, _part), proc in zip(jobs, procs):
        exits[script] = proc.returncode
        parsed: int = 0
        for raw in (proc.stdout + "\n" + proc.stderr).splitlines():
            m: "re.Match[str] | None" = _FINDING_RE.match(raw)
            if m is None:
                mc: "re.Match[str] | None" = _CANDIDATE_RE.match(raw)
                if mc is not None:
                    cands.add(f"{script} :: {_normalize(mc.group(1), prefixes)}")
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
    return exits, lines, records, cands


def _group_folder_error(root: Path, folder: Path, anchor: "str | None", approved: "Path | None") -> "str | None":
    """`--group-moves` 재료 대조 — 산출물 폴더의 `build_anchor` 가 `--anchor` 와 같은 커밋이고 `approved-merges.txt` 가
    `--approved-merge-file` 과 같은 목록(둘 다 없음 포함)이어야 한다. 어긋나면 사용 오류 문면."""
    if not folder.is_dir():
        return f"--group-moves {folder} 가 폴더가 아니다"
    marker: Path = folder / "build_anchor"
    recorded: str = marker.read_text(encoding="utf-8").strip() if marker.is_file() else ""
    if not recorded:
        return f"--group-moves {folder}/build_anchor 없음 — 묶음 이동 계산의 앵커가 없다"
    if anchor is None:
        return None  # git TARGET 의 --anchor 누락은 아래 본 자리가 낸다
    shas: "list[str]" = []
    for ref in (recorded, anchor):
        rev: "subprocess.CompletedProcess[str]" = anchor_diff.run_git(root, "rev-parse", "--verify", f"{ref}^{{commit}}")
        shas.append(rev.stdout.strip() if rev.returncode == 0 else f"(resolve 불능 {ref})")
    if shas[0] != shas[1]:
        return f"--group-moves {folder}/build_anchor({shas[0][:12]}) 와 --anchor({shas[1][:12]}) 가 다른 커밋이다"
    listed: Path = folder / "approved-merges.txt"
    mine: "bytes | None" = listed.read_bytes() if listed.is_file() else None
    given: "bytes | None" = approved.read_bytes() if approved is not None else None
    if mine != given:
        return (f"--group-moves {folder}/approved-merges.txt 와 {anchor_diff.APPROVED_MERGE_FLAG} 가 같은 목록이 아니다 — "
                "묶음 이동 계산과 승인 유입 판정이 같은 승인 병합을 써야 한다")
    return None


def _group_pairs(root: Path, folder: Path, anchor_sha: str, merges: "list[anchor_diff.ApprovedMerge]",
                 legacy: "Path | None") -> "tuple[dict[str, str], dict[str, str]]":
    """설계 9.4 — 쌍 = 실제(병합 몫 `앵커 → T₀′` 과 레인 이동 `T₀′ → 지금` 을 이은 `A → C`) ∩ 계산(`expected_moves`).
    반환 (쌍, 계산 밖 실제 쌍). 실제 이동 · T₀′ · 계산은 `folder_group` 의 한 정의다(불변식 7)."""
    import folder_group
    expected: "dict[str, str]" = folder_group.expected_moves(root, folder, legacy)
    t0: "dict[str, str]" = folder_group.tree_oids(root, anchor_sha, folder_group.git_prefix(root))
    t0p: "dict[str, str]" = folder_group.base_tree(root, anchor_sha, merges)
    now: "dict[str, str]" = {p: folder_group.blob_oid(b) for p, b in folder_group.worktree_bytes(root).items()}
    merge_share: "dict[str, str]" = folder_group.actual_moves(t0, t0p)
    lane: "dict[str, str]" = folder_group.actual_moves(t0p, now)
    pairs: "dict[str, str]" = {}
    dropped: "dict[str, str]" = {}
    for a in sorted(t0):
        b: str = merge_share.get(a, a)
        c: str = lane.get(b, b)
        if c == a or c not in now:
            continue
        if expected.get(a) == c:
            pairs[a] = c
        else:
            dropped[a] = c
    return pairs, dropped


def _follow_moves(attributed: "list[str]", resolved: "list[str]",
                  pairs: "dict[str, str]") -> "tuple[list[str], list[str], dict[str, str]]":
    """설계 9.4 줄 대응 — 귀속 줄 ℓ 마다 해소 줄 ℓ′ 의 «옛 경로 → 새 경로 · 옛 점 경로 → 새 점 경로» 치환이 ℓ 과 글자로 같으면
    1:1 로 짝짓는다. 반환 (남은 귀속, 남은 해소, {ℓ: ℓ′})."""
    if not pairs:
        return attributed, resolved, {}
    import folder_group
    subst = folder_group.string_substituter(sorted(pairs.items()))
    pool: "dict[str, list[str]]" = {}
    for old in resolved:
        new: str = subst(old)
        if new != old:
            pool.setdefault(new, []).append(old)
    rest: "list[str]" = []
    moved: "dict[str, str]" = {}
    for line in attributed:
        if pool.get(line):
            moved[line] = pool[line].pop(0)
        else:
            rest.append(line)
    taken: "set[str]" = set(moved.values())
    return rest, [line for line in resolved if line not in taken], moved


def _write_introduced(dest: Path, anchor_sha: str, attributed: "list[str]",
                      records: "list[dict]", prefixes: "tuple[str, ...]",
                      provenance: "_ProvenanceResult | None" = None,
                      candidates: "list[str] | None" = None,
                      group_moves: "dict[str, object] | None" = None) -> None:
    """귀속(N∖L) 라인에 대응하는 **현재 실행 레코드만** sidecar 로 쓴다(T2-3).

    왜 게이트가 쓰는가: 귀속은 «앵커 대비 차분»이라 게이트만 알 수 있다. 소비자가 raw
    sink 를 직접 읽으면 legacy 잔존까지 집어 «이 빌드에서 즉석 수리하지 않는다»는 규율
    (`commands/dddjango.md` — legacy 잔존 red 는 보고 채널로만)을 깨뜨린다.

    매칭은 `findings.line_of_record` 로 레코드를 라인으로 되돌린 뒤 게이트와 **같은
    정규화**를 적용해 키를 맞춘다. `candidates`(ⓓ 신규 라인 · N′∪L′≠∅ 일 때만 list)가 오면
    `candidate_lines`·`candidate_records`(severity info · 신규분만) 를 `records` 와 분리해 싣는다. 대응 레코드가 없는 귀속 라인(합성 fail-closed 귀속·
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
    if candidates is not None:  # ⓓ 채널이 있을 때(N′∪L′≠∅)만 키를 둔다 — ⓓ 0 인 저장소는 payload byte 무변(P0′)
        want_c: "set[str]" = set(candidates)
        payload["candidate_lines"] = candidates
        payload["candidate_records"] = [
            dict(rec, file=_strip_snapshot(str(rec.get("file", "")), prefixes)) for rec in records
            if rec.get("severity") == "info"
            and f"{rec.get('checker')} :: {_normalize(findings.line_of_record(rec), prefixes)}" in want_c]
    if provenance is not None:
        # flag 시에만 키 추가 — 스키마 문자열은 유지(호환 확장 · flag 없으면 payload byte 동일).
        # `attributed_lines`·`records` 는 잔여(승인 유입 제외)만이다 — 재생성 루프 입력에 유입이 섞이지 않는다.
        payload["provenance"] = provenance.as_payload()
    if group_moves is not None:  # `--group-moves` 때만 키를 둔다(flag 없으면 payload byte 무변)
        payload["group_moves"] = group_moves
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
    pruned_snapshots: "list[str]" = field(default_factory=list)          # 숨김 경로 사본 밖 링크를 뺀 스냅숏의 첫 경로

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
    """커밋 트리의 경로→blob SHA — 단일 출처는 `anchor_diff.tree_blobs`(심링크 제외)."""
    return anchor_diff.tree_blobs(root, sha)


def _tree_entries(root: Path, sha: str) -> "dict[str, str]":
    """커밋 트리의 «모든» 항목 경로 → 종류(blob·tree·commit — `git ls-tree -r -t -z` 1회)."""
    proc: "subprocess.CompletedProcess[str]" = anchor_diff.run_git(root, "ls-tree", "-r", "-t", "-z", sha)
    out: "dict[str, str]" = {}
    if proc.returncode != 0:
        return out
    for entry in proc.stdout.split("\0"):
        meta: str
        tab: str
        path: str
        meta, tab, path = entry.partition("\t")
        parts: "list[str]" = meta.split()
        if tab and len(parts) == 3:
            out[path] = parts[1]
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

    (i) 경로 (ii) 주어 판정 = `anchor_diff.PathFacts.classify`(scope 렌더와 같은 함수) — 파일·상호작용, 또는
    «없는 파일» 주어(G(p))는 부재 (iii) 후보 라인의 검사기만 커밋 스냅숏(트리 단위 캐시)에서 positional 재실행
    (iv) L 탐색 — F1 은 전달 머지 먼저·다음 first-parent 순 · L(ℓ ∈ R(M^2) ∖ R(M^1)) 이 서면
    `anchor_diff.after_merge_check`(ⓒ 뒤 미승인 머지 없음 · ⓑ 뒤 승인 머지 ^2 에도 있음 · ⓓ M 부터 HEAD 커밋까지
    사슬마다 있음)까지 통과해야 유입이다. 측정 무효는 그 머지의 증명 기회만 잃는다(∃M).
    """
    res: _ProvenanceResult = _ProvenanceResult(merges=merges, chain=chain)
    active: "list[anchor_diff.ApprovedMerge]" = sorted(
        (m for m in merges if m.participates), key=lambda m: m.position or 0)
    if not attributed:
        return res
    facts: anchor_diff.PathFacts = anchor_diff.PathFacts(root, anchor_sha, head_sha, chain, active)
    paths: "dict[str, str | None]" = _line_paths(attributed, records, prefixes)
    path_cache: "dict[str, dict[str, str]]" = {}

    def paths_of(sha: str) -> "dict[str, str]":
        if sha not in path_cache:
            path_cache[sha] = _tree_entries(root, sha)
        return path_cache[sha]

    def absent_file(p: str) -> bool:
        """G(p) — «없는 파일» 주어인가: 깨끗한 상대 경로 · .py · HEAD 에 어떤 항목도 없음 · 작업 트리에도 없음 · 부모는 HEAD 의 폴더."""
        parts: "list[str]" = p.split("/")
        if len(parts) < 2 or p.startswith("/") or any(seg in ("", ".", "..") for seg in parts) \
                or not parts[-1].endswith(".py") or re.search(r"[\s,;|<>\\\[\]:]", p):
            return False
        if p in paths_of(head_sha) or os.path.lexists(root / p):
            return False
        return paths_of(head_sha).get("/".join(parts[:-1])) == "tree"

    # (i)(ii) 후보 선별 — candidates: (line, path, checker, kind, 전달 머지)
    candidates: "list[tuple[str, str, str, str, anchor_diff.ApprovedMerge | None]]" = []
    for line in attributed:
        checker: str = line.split(" :: ", 1)[0]
        p: "str | None" = paths.get(line)
        if p is None:
            res.retained[line] = "레코드 없음"
            continue
        if p not in facts.head and absent_file(p):
            candidates.append((line, p, checker, "부재", None))
            continue
        judged: "tuple[str, anchor_diff.ApprovedMerge | None] | str" = facts.classify(p)
        if isinstance(judged, str):
            res.retained[line] = judged
            continue
        candidates.append((line, p, checker, judged[0], judged[1]))
    if not candidates:
        return res

    # (iii) 스냅숏·검사기 캐시(트리 단위) — 스냅숏 실패·사본 밖 심링크는 그 sha 의 측정을 무효로 캐시한다(traceback 0).
    tree_cache: "dict[str, str]" = {}
    snap_cache: "dict[str, Path]" = {}
    failure_cache: "dict[str, str]" = {}
    parse_fail_cache: "dict[str, set[str]]" = {}
    run_cache: "dict[tuple[str, str], tuple[bool, set[str]]]" = {}  # (tree, checker) → (유효, 라인)
    snapshot_lock: threading.Lock = threading.Lock()
    candidate_checkers: "frozenset[str]" = frozenset(row[2] for row in candidates)

    def tree_of(sha: str) -> str:
        if sha not in tree_cache:
            tree_cache[sha] = anchor_diff.tree_id(root, sha)
        return tree_cache[sha]

    def snapshot(sha: str) -> "Path | None":
        t: str = tree_of(sha)
        if t in failure_cache:
            res.snapshot_failures[sha] = failure_cache[t]
            return None
        if t not in snap_cache:
            dest: Path = td / f"snap-{t[:12]}"
            try:
                pruned: "list[str]" = anchor_diff.snapshot_anchor(root, sha, dest, drop_hidden=True)
                if pruned:
                    res.pruned_snapshots.append(pruned[0])
            except (anchor_diff.AnchorDiffUsage, OSError) as exc:  # git/tar 불능 + mkdir·디스크 오류 — traceback 0
                failure_cache[t] = f"{type(exc).__name__}: {str(exc).strip()}"
                res.snapshot_failures[sha] = failure_cache[t]
                shutil.rmtree(dest, ignore_errors=True)
                return None
            escape: "str | None" = anchor_diff.snapshot_escape(dest)
            if escape is not None:  # 사본 밖을 읽을 수 있는 스냅숏은 증거로 쓰지 않는다(fail-closed)
                failure_cache[t] = f"사본 밖을 가리키는 심링크 {escape}"
                res.snapshot_failures[sha] = failure_cache[t]
                shutil.rmtree(dest, ignore_errors=True)
                return None
            snap_cache[t] = dest
            parse_fail_cache[t] = {
                l.split(" :: ", 1)[1].split(":", 1)[0] for l in _parse_fail_findings(dest)}
            res.snapshots_run += 1
        return snap_cache[t]

    def run_batch(shas: "list[str]", checkers: "frozenset[str]") -> None:
        """한 증명 머지의 검사기별 사슬 작업을 함께 제출하고, 트리의 마지막 작업 뒤 사본을 지운다."""
        trees: "dict[str, str]" = {}
        jobs: "list[tuple[str, str, str]]" = []
        remaining: "dict[str, int]" = {}
        for sha in shas:
            trees.setdefault(tree_of(sha), sha)
        for t, sha in trees.items():
            for checker in sorted(checkers):
                if (t, checker) not in run_cache:
                    jobs.append((t, sha, checker))
                    remaining[t] = remaining.get(t, 0) + 1

        def task(job: "tuple[str, str, str]") -> None:
            t: str
            sha: str
            checker: str
            t, sha, checker = job
            try:
                with snapshot_lock:
                    snap: "Path | None" = snapshot(sha)
                if snap is None:
                    result: "tuple[bool, set[str]]" = (False, set())
                else:
                    exits: "dict[str, int]"
                    lines: "set[str]"
                    _recs: "list[dict]"
                    _cands: "set[str]"
                    exits, lines, _recs, _cands = _run_registry(snap, only=frozenset({checker}))
                    valid: bool = exits.get(checker) in (0, 2) and not any(_SYNTHETIC_MARK in l for l in lines)
                    result = (valid, lines)
                    with snapshot_lock:
                        res.checker_runs += 1
                with snapshot_lock:
                    run_cache[(t, checker)] = result
            finally:
                with snapshot_lock:
                    remaining[t] -= 1
                    if remaining[t] == 0:
                        dest: "Path | None" = snap_cache.pop(t, None)
                        if dest is not None:
                            shutil.rmtree(dest, ignore_errors=True)

        if jobs:
            with ThreadPoolExecutor(max_workers=_registry_workers(), thread_name_prefix="chain") as chain_pool:
                list(chain_pool.map(task, jobs))
        # 같은 트리의 다른 SHA도 실패 진단을 가진다. 줄 캐시는 트리·검사기 단위로 남는다.
        for sha in shas:
            t = tree_of(sha)
            if t in failure_cache:
                res.snapshot_failures[sha] = failure_cache[t]

    def run(sha: str, checker: str) -> "tuple[bool, set[str]]":
        key: "tuple[str, str]" = (tree_of(sha), checker)
        if key not in run_cache:
            run_batch([sha], candidate_checkers)
        if tree_of(sha) in failure_cache:
            res.snapshot_failures[sha] = failure_cache[tree_of(sha)]
        return run_cache[key]

    # (iv) L 탐색 + 증명 머지 뒤 조건 — ∃M: 어느 머지든 끝까지 증명하면 유입 · 아니면 귀속 유지
    for line, p, checker, kind, deliver in candidates:
        order: "list[anchor_diff.ApprovedMerge]" = (
            [deliver] + [m for m in active if m is not deliver]) if deliver is not None else list(active)

        def sample(sha: str, _checker: str = checker) -> anchor_diff.Sample:
            ok: bool
            lines: "set[str]"
            ok, lines = run(sha, _checker)
            return anchor_diff.Sample(frozenset(lines) if ok else None)

        proven: "str | None" = None
        invalid: "list[str]" = []
        after: "str | None" = None
        for m in order:
            ok1, r1 = run(m.parent1, checker)
            ok2, r2 = run(m.parent2, checker)
            if m.parent1 in res.snapshot_failures or m.parent2 in res.snapshot_failures:
                invalid.append(f"측정 무효(스냅숏 실패) — {m.sha[:12]}")
                continue
            pf1: "set[str]" = parse_fail_cache[tree_of(m.parent1)]
            pf2: "set[str]" = parse_fail_cache[tree_of(m.parent2)]
            symmetric: bool = pf1 == pf2
            if not (ok1 and ok2 and symmetric):
                sides: "list[str]" = []
                if not ok1 or (not symmetric and pf1 - pf2):
                    sides.append("M^1")
                if not ok2 or (not symmetric and pf2 - pf1):
                    sides.append("M^2")
                invalid.append(f"측정 무효({'|'.join(sides) or 'M^1|M^2'}) — {m.sha[:12]}")
                continue
            if line in r2 and line not in r1:
                # 같은 머지에서 L이 선 검사기만 사슬을 잰다. 사본은 그 트리의 필요한 검사기가
                # 모두 끝나면 바로 지운다(사슬 길이만큼 디스크에 쥐고 있지 않는다).
                proving: "frozenset[str]" = frozenset(
                    c for other, _p, c, _kind, _deliver in candidates
                    if run(m.parent1, c)[0] and run(m.parent2, c)[0]
                    and other in run(m.parent2, c)[1] and other not in run(m.parent1, c)[1])

                def prefetch(shas: "list[str]") -> None:
                    run_batch(shas, proving)

                reason: "str | None" = anchor_diff.after_merge_check(
                    key=line, m=m, active=active, chain=chain, sample=sample, tree_of=tree_of, prefetch=prefetch)
                if reason is None:
                    proven = m.sha
                    break
                after = after or reason
        if proven is not None:
            res.inflow.append((line, proven, kind))
        elif after is not None:
            res.retained[line] = after
        elif invalid:
            res.retained[line] = invalid[0]
        elif kind == "부재":
            res.retained[line] = "부재 미증명"
        elif kind == "파일":
            # 전달 머지보다 앞선 «미승인» 머지가 p 를 바꿨다면 진단은 그때 들어왔을 수 있다 — 목록 누락을
            # 표면화한다(부분 목록 실측: 이중 원인과 구별 불가 — 발주자가 목록을 보완하면 L 이 그 머지에서 선다).
            earlier_unapproved: "list[str]" = [
                c.sha for c in chain
                if c.is_merge and c.sha not in {m.sha for m in active}
                and deliver is not None and facts.position[c.sha] < facts.position.get(deliver.sha, 1 << 30)
                and facts.blobs(c.sha).get(p) != facts.blobs(c.parents[0]).get(p)]
            hint: str = (f" — 미승인 머지 {earlier_unapproved[-1][:12]} 경유 가능" if earlier_unapproved else "")
            res.retained[line] = f"유입 증명 실패(이중 원인{hint})"
        else:
            res.retained[line] = "상호작용 미증명"
    return res


_OLD_COPY_AGE_SECONDS: int = 3600
_OLD_ANCHOR_ONLY_RE: "re.Pattern[str]" = re.compile(r"anchor|tree-[0-9a-f]{12}")


def _old_copy(path: Path) -> bool:
    """뿌리 이전 판(2.24.2 이하)이 기본 임시 폴더에 남긴 사본 꼴인가 — 그 판들이 실제로 만들던 꼴만 센다.

    registry_gate `tmp*`: `current/` 와 함께 `anchor/` · `records-current.jsonl` · `records-anchor.jsonl` 가운데 하나 ·
    anchor_diff `tmp*`: `anchor/` 와 `tree-<12자>/` 뿐 · pre-gate `design-pregate-*`: `copy/`. 그리고 마지막 쓰기(그 폴더와
    바로 아래 항목)가 1시간을 넘었다. 이름이 맞지 않으면 열지 않는다."""
    name: str = path.name
    if not (name.startswith("tmp") or name.startswith("design-pregate-")):
        return False
    try:
        st: os.stat_result = os.lstat(path)
        if not stat.S_ISDIR(st.st_mode):
            return False
        children: "list[os.DirEntry[str]]" = list(os.scandir(path))
        times: "list[float]" = [st.st_mtime] + [c.stat(follow_symlinks=False).st_mtime for c in children]
    except OSError:
        return False
    dirs: "set[str]" = {c.name for c in children if c.is_dir(follow_symlinks=False)}
    names: "set[str]" = {c.name for c in children}
    if name.startswith("design-pregate-"):
        shaped: bool = "copy" in dirs
    else:
        shaped = (("current" in dirs and bool({"anchor", "records-current.jsonl", "records-anchor.jsonl"} & names))
                  or ("anchor" in dirs and all(_OLD_ANCHOR_ONLY_RE.fullmatch(n) for n in names)))
    return shaped and time.time() - max(times) > _OLD_COPY_AGE_SECONDS


def _temp_report_line() -> str:
    """`--temp-report` 의 한 줄 — 뿌리의 남은 사본(keep 아닌 것 — 다른 실행 몫) · keep 사본 · 기본 임시 폴더의 옛 판 꼴
    사본의 개수와 크기. 판정 · 지우기 없음(옛 판 꼴은 주인 표식이 없어 사용자가 지운다)."""
    base: Path = Path(tempfile.gettempdir())
    root: "Path | None" = anchor_diff.temp_root(create=False)
    left: int = 0
    left_size: int = 0
    keep: int = 0
    keep_size: int = 0
    if root is not None:
        try:
            names: "list[str]" = sorted(os.listdir(root))
        except OSError:
            names = []
        for name in names:
            entry: Path = root / name
            size: int = anchor_diff.tree_size(entry) if entry.is_dir() and not entry.is_symlink() else 0
            if anchor_diff.temp_state(entry) == "keep":
                keep, keep_size = keep + 1, keep_size + size
            else:
                left, left_size = left + 1, left_size + size
    try:
        old: "list[Path]" = [p for p in sorted(base.iterdir()) if _old_copy(p)]
    except OSError:
        old = []
    if not (left or keep or old):
        return "임시 사본: 남은 것 0"
    old_size: int = sum(anchor_diff.tree_size(p) for p in old)
    return (f"임시 사본: 남은 {left}개({left_size / 1048576:.1f} MB — 다른 실행 몫) · "
            f"keep {keep}개({keep_size / 1048576:.1f} MB) · "
            f"옛 판 꼴 {len(old)}개({old_size / 1073741824:.1f} GB — 직접 지워도 됨) · {base / anchor_diff.TEMP_ROOT}")


def main(argv: "list[str]") -> int:
    ap: _UsageParser = _UsageParser(add_help=True)
    ap.add_argument("target", nargs="?")
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
    ap.add_argument("--group-moves", default=None, metavar="산출물 폴더",
                    help="묶음 이동(2.28.0 의미 묶음)을 따라 옮긴 legacy 줄을 귀속에서 빼 «이동 따라 옮긴 legacy» 절로 "
                         "보고한다 — 쌍 = 실제 이동 ∩ folder_group 계산(설계 9.4 · git TARGET 전용 · exit 밖 · sidecar)")
    ap.add_argument("--temp-report", action="store_true",
                    help="임시 사본 한 줄 보고만 하고 끝낸다(G2 배너용 — 판정 · 지우기 없음 · TARGET 불요)")
    ns: argparse.Namespace = ap.parse_args(argv)
    if ns.temp_report:
        print(_temp_report_line())
        return 0
    if ns.target is None:
        ap.error("the following arguments are required: target")

    root: Path = Path(ns.target).resolve()
    if not root.is_dir():
        print(f"사용 오류: TARGET {root} 이 디렉터리가 아니다", file=sys.stderr)
        return 1
    bad: "str | None" = checker_target.bc_shaped_target_reason(str(root))
    if bad is not None:
        print(f"사용 오류: {bad}", file=sys.stderr)
        return 1

    source_root: Path = root
    supplied: str = os.environ.get(anchor_diff.SISTER_SOURCE_ENV, "")
    if supplied:
        try:
            candidate: Path = Path(supplied).resolve(strict=True)
            if candidate.is_dir() and os.access(candidate, os.R_OK | os.X_OK):
                source_root = candidate
        except (OSError, ValueError, RuntimeError):
            pass  # 읽을 수 없는 전달값은 원래 TARGET 판정으로 돌아간다.
    has_sister: bool = anchor_diff.sister_owned(source_root)

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
    group_folder: "Path | None" = None
    if ns.group_moves is not None:
        if not is_git:
            print("사용 오류: --group-moves 는 git 저장소 TARGET 에서만 쓸 수 있다 — 묶음 이동 재료(앵커 · 커밋 트리)가 없다",
                  file=sys.stderr)
            return 1
        group_folder = Path(ns.group_moves).resolve()
        why: "str | None" = _group_folder_error(root, group_folder, ns.anchor, approved_path)
        if why is not None:
            print(f"사용 오류: {why}", file=sys.stderr)
            return 1
    group_pairs: "dict[str, str] | None" = None
    group_dropped: "dict[str, str]" = {}

    anchor_diff.sweep_temp_root()
    with anchor_diff.owned_tempdir("registry-gate") as td:
        cur: Path = Path(td) / "current"
        _snapshot_current(root, cur)
        # L/N 을 **다른 파일**로 받는다 — 한 sink 에 누적하면 legacy 와 신규가 섞인다.
        sink_n: Path = Path(td) / "records-current.jsonl"
        sink_l: Path = Path(td) / "records-anchor.jsonl"
        cur_prefixes: "tuple[str, ...]" = (str(cur) + "/", str(cur))
        # 계약 sidecar 의 앵커 차분 재료 — 비-git 분기에서는 앵커가 없어 전량이 «신규»다.
        l_records: "list[dict]" = []
        anc_prefixes: "tuple[str, ...]" = ()
        unclassifiable_n: "set[str]" = set()
        unclassifiable_l: "set[str]" = set()
        anchor_escape: "str | None" = None
        pair_root: "Path | None" = None   # 목록 짝을 지을 앵커 사본(정상 차분일 때만)

        if not is_git:
            print("주의: 비-git TARGET — 차분 불능이라 fail-closed(현재 위반 전량 귀속)")
            exits_n, n_set, n_records, n_cands = _run_registry(
                cur, sink_n, unclassifiable=unclassifiable_n)  # 원본도 비-git — 넘길 루트 없음
            n_set |= _parse_fail_findings(cur)
            l_set: "set[str]" = set()
            l_cands: "set[str]" = set()
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
            if approved_path is None:
                hints: "list[tuple[str, str, bool]]" = anchor_diff.merge_hints(root, anchor_sha, head)
                if hints:
                    def _shown(items: "list[str]") -> str:
                        return " ".join(items[:6]) + (f" 외 {len(items) - 6}" if len(items) > 6 else "")
                    listed: "list[str]" = [f"{sha[:12]}(^2 {ref})" for sha, ref, only_head in hints if not only_head]
                    side: "list[str]" = [sha[:12] for sha, _ref, only_head in hints if only_head]
                    groups: "list[str]" = ([_shown(listed)] if listed else []) + (
                        [f"레인 곁가지 의심(^2 를 담은 ref 가 HEAD 브랜치뿐 — 등재 대상 아님): {_shown(side)}"] if side else [])
                    print(f"안내: 앵커 {anchor_sha[:12]}..HEAD first-parent 사슬에 2-부모 머지 {len(hints)}건이 있고 "
                          f"{anchor_diff.APPROVED_MERGE_FLAG} 가 없다 — {' · '.join(groups)} · 발주자가 승인한 "
                          "main→레인 머지라면 발주자가 `<산출물 폴더>/approved-merges.txt` 에 그 SHA 를 적은 뒤"
                          "(코디네이터·실행자는 이 파일을 쓰지 않는다) 그 파일을 붙여 다시 실행하면 승인 유입을 따로 가른다"
                          "(이 줄은 판정·exit 를 바꾸지 않는다)")
            if approved_path is not None:
                try:
                    merges, chain = anchor_diff.load_approved_merges(approved_path, root, anchor_sha, head)
                except anchor_diff.AnchorDiffUsage as exc:
                    print(f"사용 오류: {exc}", file=sys.stderr)
                    return 1
            if group_folder is not None:
                import folder_group
                try:
                    group_pairs, group_dropped = _group_pairs(
                        root, group_folder, anchor_sha, merges,
                        Path(ns.legacy_debt_file) if ns.legacy_debt_file is not None else None)
                except folder_group.FolderGroupError as exc:
                    print(f"사용 오류: --group-moves 묶음 이동 계산 불능 — {exc}", file=sys.stderr)
                    return 1
            anc: Path = Path(td) / "anchor"
            try:
                anchor_pruned: "list[str]" = anchor_diff.snapshot_anchor(root, anchor_sha, anc, drop_hidden=True)
            except anchor_diff.AnchorDiffUsage as exc:
                print(f"재료 결손: {exc}", file=sys.stderr)
                return 1
            if anchor_pruned:
                print(f"정보: 앵커 {anchor_sha[:12]} 사본에서 숨김 경로의 사본 밖 심링크 {len(anchor_pruned)}개를 뺐다"
                      "(사본 밖 내용을 읽지 않게 — 현재 쪽 사본은 숨김 경로를 복사하지 않는다 · 판정 무관): "
                      + anchor_pruned[0] + (f" 외 {len(anchor_pruned) - 1}" if len(anchor_pruned) > 1 else ""))
            anchor_escape = anchor_diff.snapshot_escape(anc)
            if anchor_escape is not None:
                # 앵커 사본의 심링크가 사본 밖(예: 이 작업 트리)을 가리키면 앵커 실행이 «지금» 내용을 읽는다 —
                # 그 실행은 기준선이 못 된다. 비-git 가지와 같이 현재 위반 전량을 귀속한다(fail-closed).
                print(f"주의: 앵커 {anchor_sha[:12]} 사본에 사본 밖을 가리키는 심링크 {anchor_escape} — "
                      "기준선 불능이라 fail-closed(현재 위반 전량 귀속)")
                has_sister = False  # 기준선 불능이면 자매로 가르지 않는다(«측정 실패가 먼저다»)
                exits_n, n_set, n_records, n_cands = _run_registry(
                    cur, sink_n, git_root=root, unclassifiable=unclassifiable_n)
                exits_l = {}
                l_set = set()
                l_cands = set()
                n_set |= _parse_fail_findings(cur)
            else:
                pair_root = anc
                # 앵커·현재 두 벌을 동시에 돈다 — 검사기 동시 실행 한도는 두 벌이 나눠 쓰는 공용 풀이 정한다.
                # `with` 를 나갈 때 두 벌이 모두 끝나 있으므로 한쪽 예외도 임시 폴더 정리와 겹치지 않는다.
                with ThreadPoolExecutor(max_workers=2, thread_name_prefix="registry-side") as sides:
                    anchor_run: "Future[tuple[dict[str, int], set[str], list[dict], set[str]]]" = sides.submit(
                        _run_registry, anc, sink_l, unclassifiable=unclassifiable_l)
                    current_run: "Future[tuple[dict[str, int], set[str], list[dict], set[str]]]" = sides.submit(
                        _run_registry, cur, sink_n, git_root=root, unclassifiable=unclassifiable_n)
                    exits_l, l_set, _l_records, l_cands = anchor_run.result()
                    exits_n, n_set, n_records, n_cands = current_run.result()
                l_records = _l_records
                anc_prefixes = (str(anc) + "/", str(anc))
                l_set |= _parse_fail_findings(anc)
                n_set |= _parse_fail_findings(cur)

        attributed: "list[str]" = sorted(n_set - l_set)
        resolved: "list[str]" = sorted(l_set - n_set)
        residual: "list[str]" = sorted(l_set & n_set)
        shrunk: "dict[str, str]" = {}
        cand_shrunk: "dict[str, str]" = {}
        if pair_root is not None:
            # 목록 칸만 줄어든 줄은 그 파일이 앵커와 바이트까지 같을 때만 잔존으로 센다(F4-99 — 고치지 않은 파일).
            subjects: "dict[str, str | None]" = _line_paths(attributed + sorted(n_cands - l_cands), n_records, cur_prefixes)

            def untouched(line: str, _anchor: Path = pair_root) -> bool:
                return _same_file(_anchor, cur, subjects.get(line))
            shrunk = _list_shrunk([line for line in attributed if untouched(line)], resolved)
            cand_shrunk = _list_shrunk([line for line in sorted(n_cands - l_cands) if untouched(line)],
                                       sorted(l_cands - n_cands))
        attributed = [line for line in attributed if line not in shrunk]
        resolved = [line for line in resolved if line not in set(shrunk.values())]
        residual = sorted(set(residual) | set(shrunk))
        cand_new: "list[str]" = sorted((n_cands - l_cands) - set(cand_shrunk))      # ⓓ 신규(N′∖L′) — 감수자 입력
        cand_legacy: int = len(n_cands & l_cands) + len(cand_shrunk)               # ⓓ legacy — 보고만
        cand_resolved: int = len(l_cands - n_cands) - len(cand_shrunk)

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

        moved: "dict[str, str]" = {}
        if group_pairs is not None:
            attributed, resolved, moved = _follow_moves(attributed, resolved, group_pairs)

        sister: "list[str]" = []
        if has_sister:
            invalid: "set[str]" = {checker for exits in (exits_n, exits_l)
                                   for checker, code in exits.items() if code not in (0, 2)}
            invalid.update(unclassifiable_n | unclassifiable_l)
            invalid.update(line.split(" :: ", 1)[0] for line in n_set | l_set
                           if anchor_diff.measurement_failed([line]))
            # 숫자 진단과 [분석]이 함께 나오면 라인 집합에는 숫자만 남는다.
            # 측정 표지는 레코드 채널에서도 읽어 그 검사기의 정상 판정을 막는다.
            invalid.update(str(rec.get("checker")) for rec in n_records + l_records
                           if anchor_diff.measurement_failed([findings.line_of_record(rec)]))
            paths: "dict[str, str | None]" = _line_paths(attributed, n_records, cur_prefixes)
            rest: "list[str]" = []
            for line in attributed:
                checker: str = line.split(" :: ", 1)[0]
                path: "str | None" = paths[line]
                if checker == "(pre-scan)":
                    match: "re.Match[str] | None" = re.fullmatch(
                        r"\(pre-scan\) :: \[#parse-fail\] (.+?): (.*)", line)
                    path = match.group(1) if match is not None else None
                normal: bool = (checker not in invalid and not (
                    provenance is not None and anchor_diff.unmeasured(provenance.retained.get(line, ""))))
                (sister if normal and anchor_diff.sister_path(path) else rest).append(line)
            attributed = rest
            # 계약은 숫자 차분 집합에 넣지 않는다. 신규 계약 레코드의 주어를 따로 가르고 보고한다.
            legacy_contract: "set[str]" = {_contract_key(rec, anc_prefixes)
                                            for rec in l_records if rec.get("rule") is None}
            sister_contract: "set[str]" = {_contract_key(rec, cur_prefixes) for rec in n_records
                if rec.get("rule") is None and rec.get("sentinel") is None
                and rec.get("checker") not in invalid
                and _contract_key(rec, cur_prefixes) not in legacy_contract
                and anchor_diff.sister_path(anchor_diff.subject_path(
                    _normalize(findings.line_of_record(rec), cur_prefixes)))}
            sister = sorted(set(sister) | sister_contract)

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
    if sister:
        print(f"\n== {anchor_diff.SISTER_TITLE} {len(sister)}건 ==")
        for line in sister:
            print(f"  {line}")
    by_checker: "dict[str, int]" = {}
    for line in residual:
        by_checker[line.split(" :: ", 1)[0]] = by_checker.get(line.split(" :: ", 1)[0], 0) + 1
    print(f"\n== legacy 잔존(L∩N) {len(residual)}건 · 해소(L∖N) {len(resolved)}건 ==")
    for script in sorted(by_checker):
        print(f"  {script}: {by_checker[script]}")
    if shrunk:
        print(f"  목록만 줄어 잔존으로 센 줄 {len(shrunk)}건(진단 글의 낱말 목록이 앵커 줄의 부분집합 — 늘린 위반이 아니다):")
        for line, anchor_line in sorted(shrunk.items()):
            print(f"    {line}")
            print(f"      ↳ 앵커: {anchor_line}")
    if group_pairs is not None:
        _print_group_moves(moved, group_pairs, group_dropped)
    if n_cands or l_cands:
        print(f"\n== ⓓ 신규(N′∖L′) {len(cand_new)}건 · legacy {cand_legacy}건 · 해소 {cand_resolved}건 — exit 불산입 · 감수자 입력은 신규분만(R-0284) ==")
        for line in cand_new:
            print(f"  {line}")
        legacy_by: "dict[str, int]" = {}
        for line in (n_cands & l_cands) | set(cand_shrunk):
            legacy_by[line.split(" :: ", 1)[0]] = legacy_by.get(line.split(" :: ", 1)[0], 0) + 1
        for script in sorted(legacy_by):
            print(f"  legacy {script}: {legacy_by[script]}")
        if cand_shrunk:
            print(f"  목록만 줄어 legacy 로 센 ⓓ 줄 {len(cand_shrunk)}건(진단 글의 낱말 목록이 앵커 줄의 부분집합):")
            for line, anchor_line in sorted(cand_shrunk.items()):
                print(f"    {line}")
                print(f"      ↳ 앵커: {anchor_line}")
    if provenance is not None:
        _print_provenance_diag(provenance, anchor_sha)
    if ns.introduced_json is not None:
        _write_introduced(Path(ns.introduced_json), anchor_sha, attributed,
                          n_records, cur_prefixes, provenance,
                          cand_new if (n_cands or l_cands) else None,
                          None if group_pairs is None else {
                              "pairs": group_pairs, "dropped": group_dropped,
                              "lines": [{"line": line, "anchor_line": moved[line]} for line in sorted(moved)]})
    if ns.contract_json is not None:
        sister_keys: "set[str]" = set(sister)
        server_records: "list[dict]" = [rec for rec in n_records
                                       if _contract_key(rec, cur_prefixes) not in sister_keys]
        _write_contract(Path(ns.contract_json), anchor_sha, server_records,
                        l_records, cur_prefixes, anc_prefixes)

    tail: str = f"(승인 유입 {len(provenance.inflow)}건 제외)" if provenance is not None else ""
    unmeasured: int = anchor_diff.unmeasured_count(attributed, provenance.retained) if provenance is not None else 0
    if unmeasured:
        tail = f"(승인 유입 {len(provenance.inflow)}건 제외 · 귀속 {len(attributed)}건 가운데 잴 수 없어 남긴 {unmeasured}건 — 위 provenance 진단)"
    if group_pairs is not None:
        followed: str = f"이동 따라 옮긴 legacy {len(moved)}건 제외"
        tail = f"{tail[:-1]} · {followed})" if tail else f"({followed})"
    if anchor_escape is not None:
        note: str = "기준선 불능 — 앵커 사본 밖 심링크 · 현재 위반 전량 귀속"
        tail = f"{tail[:-1]} · {note})" if tail else f"({note})"
    print(f"\n판정: 귀속 {len(attributed)}건 → {'green(신규 위반 없음)' if not attributed else 'red'}{tail}")
    return 0 if not attributed else 2


def _print_group_moves(moved: "dict[str, str]", pairs: "dict[str, str]", dropped: "dict[str, str]") -> None:
    """«이동 따라 옮긴 legacy» 절(설계 9.4) — 줄과 앵커 줄 · 쌍 · 계산 밖 이동. `--group-moves` 면 0건이어도 낸다."""
    print(f"\n== 이동 따라 옮긴 legacy(묶음 이동 쌍 — exit 제외 · 보고) {len(moved)}건 ==")
    for line in sorted(moved):
        print(f"  {line}")
        print(f"    ↳ 앵커: {moved[line]}")
    for a, c in sorted(pairs.items()):
        print(f"  쌍 {a} -> {c}")
    for a, c in sorted(dropped.items()):
        print(f"  계산 밖 이동(쌍에서 뺌 — 그 파일의 옛 위반은 귀속) {a} -> {c}")


def _print_inflow(prov: _ProvenanceResult) -> None:
    """«승인 유입» 절 — 머지 표(subject·부모·^2 ref 도달성 — 역방향 머지 오기입 가시화) + 라인별 L 증명 머지."""
    print(f"\n== 승인 유입(발주자 승인 머지 경유 · provenance 증명 — exit 제외·기록 의무) {len(prov.inflow)}건 ==")
    for m in prov.merges:
        if not m.participates:
            print(f"  [M {m.sha[:12]}] {m.subject} · 앵커 이전 — 판정 불참")
            continue
        files, inter = prov.per_merge(m.sha)
        absent: int = sum(1 for _l, s, k in prov.inflow if s == m.sha and k == "부재")
        print(f"  [M {m.sha[:12]}] {m.subject} · ^1 {m.parent1[:12]} · ^2 {m.parent2[:12]}({m.parent2_ref}) · "
              f"파일 {files} · 상호작용 {inter}" + (f" · 부재 {absent}" if absent else ""))
        if m.parent2_only_head:
            print(f"    ↳ 주의: ^2 {m.parent2[:12]} 를 포함하는 ref 가 HEAD 브랜치뿐 — 역방향/합성 머지 의심"
                  "(발주자 확인 — 등재 전 `^2` 가 main(상류) 이력에 있는지 확인 · exit 무변)")
    for line, m, kind in prov.inflow:
        print(f"  {line}")
        print(f"    ↳ 유입: {m[:12]}(L 증명) · "
              + {"파일": "파일 verbatim", "부재": "부재(상류에도 없던 파일)"}.get(kind, "상호작용"))


def _print_provenance_diag(prov: _ProvenanceResult, anchor_sha: str) -> None:
    """«provenance 진단» 절 — 사슬 통계·스냅숏 실행 수·«비머지 커밋이 첫 승인 머지보다 앞섬» 진단."""
    st: "dict[str, object]" = prov.chain_stats()
    print("\n== provenance 진단 ==")
    print(f"  first-parent 사슬 {anchor_sha[:12]}..HEAD: 커밋 {st['commits']} · 머지 {st['merges']}"
          f"(승인 {st['approved']} · 미승인 {len(st['unapproved_merges'])}) · 비머지 {st['non_merges']}")
    print(f"  스냅숏 실행 {st['snapshots_run']} · 검사기 재실행 {st['checker_runs']}")
    for sha, why in prov.snapshot_failures.items():
        print(f"  스냅숏 실패(측정 무효 — 해당 머지의 후보 라인은 귀속 유지): {sha[:12]} — {why}")
    if prov.pruned_snapshots:
        print(f"  숨김 경로의 사본 밖 심링크를 뺀 스냅숏 {len(prov.pruned_snapshots)}개(판정 무관 · 첫 경로 "
              f"{prov.pruned_snapshots[0]})")
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
