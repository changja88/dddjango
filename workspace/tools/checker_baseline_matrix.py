#!/usr/bin/env python3
"""검사기 27종 출력 기준선 실측표 — {parsed·unparsed·synthetic} × 자기 red fixture.

T2-1 선행 장치(t2-plan v1.1 §2 — 적대 리뷰 L-10 처분): «규약 밖 11종은 일괄
미파싱 1건» 전제가 거짓(파싱 가능·불가능 라인 혼합)임이 실측됐으므로, 개작
«전» 각 검사기의 라인 채널 실태를 registry_gate 와 동일한 눈으로 세어 고정한다.
개작 커밋의 registry_gate 앵커 diff 기대는 이 표가 기준이다.

계수 정의(registry_gate 와 동일 코퍼스·동일 정규식 — import 로 단일 출처):
- parsed    = stdout+stderr 에서 `_FINDING_RE`(`[#N]` 앵커) 매치 라인 수
- unparsed  = 비어 있지 않은 비매치 라인 수(ⓓ candidate·rule=null 선행 계약·헤더 등)
- synthetic = registry_gate 합성 귀속 조건(exit≠0 and parsed==0) 충족 여부

EXPECTED 갱신 규율(기대표 관례): 개작 커밋에서 수치가 바뀌면 같은 커밋에서
`--emit-expected` 로 갱신하되 커밋 메시지에 검사기별 사유(어떤 라인이 왜
늘고 줄었는지)를 전건 기록한다 — 무사유 일괄 갱신 금지.

사용: python3 workspace/tools/checker_baseline_matrix.py [--emit <md 경로>] [--emit-expected]
exit 0 = EXPECTED 전수 일치 / exit 2 = 불일치 존재 / exit 1 = 재료 결손.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

CHECKER_TIMEOUT_S: int = 300  # 무기한 verify 정지 방지(적대 검증 레인 S 9번)

ROOT: Path = Path(__file__).resolve().parents[2]
S: Path = ROOT / "dddjango" / "scripts"
F: Path = ROOT / "workspace" / "eval" / "fixtures"

# 로스터·픽스처 쌍·게이트 정규식을 전부 import — 재구현 금지(단일 출처).
sys.path.insert(0, str(S))
sys.path.insert(0, str(ROOT / "workspace" / "tools"))
from checker_registry import REGISTRY, checker_argv  # noqa: E402
from fixture_matrix import AUTO_PAIRS, PLAIN_PAIRS  # noqa: E402  (import 시점 로스터 assert 동승)
from registry_gate import _FINDING_RE  # noqa: E402

_RED_SUB: "dict[str, str]" = {"check-layer-skeleton.py": "skeleton/bad_legacy_flat"}
_RED_SUB.update({s: f"{fx}/bad_rules" for s, fx in PLAIN_PAIRS})
_RED_SUB.update({s: f"{fx}/bad_rules" for s, fx in AUTO_PAIRS})

# 기준선(2026-08-19 개작 전 실측 — --emit-expected 재생성): script -> (exit, parsed, unparsed, synthetic)
# 실측 검증: domain_model parsed=48 = findings_smoke DM_COUNT_VIOLATION · common_container
# synthetic = rule=null 선행 계약 라인(비[#N]) 실증. synthetic 군은 7종(«11종» 아님 — L-10 확정).
EXPECTED: "dict[str, tuple[int, int, int, bool]]" = {
    "check-mechanism-ownership.py": (2, 6, 1, False),
    "check-error-centralization.py": (2, 5, 1, False),
    "check-response-schema-bypass.py": (2, 0, 3, True),
    "check-layer-skeleton.py": (2, 10, 1, False),
    "check-openapi-error-declaration.py": (2, 3, 1, False),
    "check-context-isolation.py": (2, 58, 6, False),
    "check-app-container.py": (2, 0, 4, True),
    "check-ninja-boundary-middleware.py": (2, 0, 4, True),
    "check-common-container.py": (2, 0, 4, True),
    "check-idempotency-scope-creep.py": (2, 0, 3, True),
    "check-public-surface-annotation.py": (2, 10, 4, False),
    "check-test-config.py": (2, 13, 2, False),
    "check-transient-overmapping.py": (2, 0, 3, True),
    "check-synthetic-infra-exc.py": (2, 1, 2, False),
    "check-api-error-controller-contract.py": (2, 9, 3, False),
    "check-composition-root.py": (2, 18, 4, False),
    "check-db-table.py": (2, 26, 2, False),
    "check-choices-literal-consumption.py": (2, 0, 6, True),
    "check-usecase-dto-placement.py": (2, 35, 7, False),
    "check-transaction-boundary.py": (2, 13, 3, False),
    "check-domain-model.py": (2, 48, 14, False),
    "check-port-adapter-pairing.py": (2, 79, 10, False),
    "check-event-publish.py": (2, 20, 5, False),
    "check-broker-contract.py": (2, 22, 6, False),
    "check-missable-entrance.py": (2, 17, 5, False),
    "check-naming.py": (2, 29, 6, False),
    "check-business-vocabulary.py": (2, 48, 7, False),
}


def measure() -> "dict[str, tuple[int, int, int, bool]]":
    got: "dict[str, tuple[int, int, int, bool]]" = {}
    for script, auto in REGISTRY:
        fx = F / _RED_SUB[script]
        if not fx.is_dir():
            print(f"재료 결손: fixture {_RED_SUB[script]} 없음", file=sys.stderr)
            raise SystemExit(1)
        # fixture 는 git 밖 «임시 사본»으로 실행(hermetic) — fixture_matrix 와 같은 사유:
        # 저장소 안 원본 직접 실행은 git/touched 인식이 커밋 상태에 따라 결과를 바꾼다.
        with tempfile.TemporaryDirectory() as td:
            tmp_fx = Path(td) / "fixture"
            shutil.copytree(fx, tmp_fx)
            # 사용자 환경의 DJR_FINDINGS_JSON 을 상속하면 이 하네스가 사용자의 실제
            # 레코드 파일에 테스트 레코드를 append 한다(T2-1 적대 검증 레인 S 7번 — 544행 오염
            # 실증). 라인 채널만 재는 도구이므로 레코드 sink 를 아예 끊는다.
            env = dict(os.environ)
            env.pop("DJR_FINDINGS_JSON", None)
            proc = subprocess.run(
                checker_argv(sys.executable, script, str(tmp_fx), auto),
                capture_output=True, text=True, cwd=str(ROOT), env=env,
                timeout=CHECKER_TIMEOUT_S,
            )
        parsed = unparsed = 0
        for raw in (proc.stdout + "\n" + proc.stderr).splitlines():
            if not raw.strip():
                continue
            if _FINDING_RE.match(raw):
                parsed += 1
            else:
                unparsed += 1
        synthetic = proc.returncode != 0 and parsed == 0
        got[script] = (proc.returncode, parsed, unparsed, synthetic)
    return got


def main(argv: "list[str]") -> int:
    emit: "Path | None" = None
    emit_expected = "--emit-expected" in argv
    if "--emit" in argv:
        i = argv.index("--emit")
        if len(argv) < i + 2:
            print("사용: checker_baseline_matrix.py [--emit <md 경로>] [--emit-expected]", file=sys.stderr)
            return 1
        emit = Path(argv[i + 1])

    # 로스터↔기대표 키 집합 양방향 검사(적대 검증 레인 S 10번) — assert 가 아니라 런타임 검사다
    # (PYTHONOPTIMIZE=1 이면 assert 가 사라져 «26/26 일치»로 세탁된다).
    roster = {script for script, _ in REGISTRY}
    if len(roster) != 27:
        print(f"재료 결손: REGISTRY 로스터 27종 가정 위반({len(roster)})", file=sys.stderr)
        return 1
    if not emit_expected and roster != set(EXPECTED):
        print(f"재료 결손: 로스터↔EXPECTED 키 불일치 — 로스터만: {sorted(roster - set(EXPECTED))} · "
              f"기대표만: {sorted(set(EXPECTED) - roster)}", file=sys.stderr)
        return 1

    got = measure()

    if emit_expected:
        # 실패 상태를 «새 정답»으로 세탁하는 것을 막는다(적대 검증 레인 S 1번): red 픽스처는
        # exit 2 여야 하고, 라인 앵커가 전멸한 검사기를 조용히 동결하지 않는다.
        bad = [s for s, (e, _p, _u, _syn) in got.items() if e != 2]
        if bad:
            print(f"거부: red 픽스처 exit 2 가 아닌 검사기 — {sorted(bad)}. 개작 결함을 "
                  f"기대표로 세탁할 수 없다(사유와 함께 코드를 먼저 고쳐라)", file=sys.stderr)
            return 1
        print('EXPECTED: "dict[str, tuple[int, int, int, bool]]" = {')
        for script, _ in REGISTRY:
            e, p, u, syn = got[script]
            print(f'    "{script}": ({e}, {p}, {u}, {syn}),')
        print("}")
        return 0

    lines: "list[str]" = [
        "| 검사기 | exit | parsed | unparsed | synthetic | 판정 |",
        "|---|---|---|---|---|---|",
    ]
    mismatch = 0
    for script, _ in REGISTRY:
        cur = got[script]
        want = EXPECTED.get(script)
        ok = cur == want
        if not ok:
            mismatch += 1
        e, p, u, syn = cur
        mark = "✓" if ok else f"✗ 기대 {want}"
        lines.append(f"| `{script}` | {e} | {p} | {u} | {'1건' if syn else '—'} | {mark} |")
    summary = f"검사기 {len(got)} · 일치 {len(got) - mismatch} · 불일치 {mismatch}"
    table = "\n".join(lines)
    print(table)
    print(summary)
    if emit is not None:
        emit.write_text(
            "# T2 검사기 출력 기준선 — 27종 × 자기 red fixture\n\n"
            f"생성: {date.today().isoformat()} · `workspace/tools/checker_baseline_matrix.py --emit` 산출물"
            "(손으로 고치지 않는다 — 재실행으로 재생성).\n\n"
            "T2-1 개작(공용 findings 모듈 편입)의 anchor diff 기대 기준선 — 계수 정의·갱신 규율은 도구 docstring.\n\n"
            f"{table}\n\n{summary}\n",
            encoding="utf-8",
        )
        print(f"실측표 기록: {emit}")
    return 0 if mismatch == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
