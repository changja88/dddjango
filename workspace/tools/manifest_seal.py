#!/usr/bin/env python3
"""T2-0b **구현 동결 게이트** — manifest 저작·봉인·대조 (비가역).

봉인 이후 여기 등재된 것이 하나라도 바뀌면 **이미 돈 실런은 전부 무효**다(t2-plan §2 T2-0b).
그래서 이 도구의 유일한 설계 목표는 «바뀐 것을 놓치지 않는다»이며, 그 반대편 실패
(«안 바뀐 것을 바뀌었다고 한다»)는 비용이 훨씬 싸다. 판단이 갈리면 red 로 붙인다.

**놓치기 쉬운 세 구멍을 명시적으로 막는다**:

1. **파일 추가**. 해시 목록만 대조하면 28번째 검사기를 몰래 더해도 green 이다. 그래서 그룹마다
   `globs` 를 함께 봉인하고, 대조 때 글롭을 **다시 펴서 집합이 정확히 같은지** 본다.
2. **manifest 자체의 손편집**. 봉인본을 고치면 무엇이든 통과한다. `self_sha256`(자기 필드를 뺀
   canonical JSON 의 해시)으로 봉인본을 tamper-evident 하게 만든다.
3. **외부 재료의 조용한 공백**. 설치 cache·발주 타깃처럼 저장소 밖에 있는 항목은 «측정 못 했다»가
   «문제 없다»로 읽히기 쉽다. `external` 로 분리하고 **`PENDING` 이 하나라도 있으면 `--check`
   실패**로 만든다(엄격 모드가 기본 — 실런 게이트가 이 모드를 쓴다).

또 한 가지, 봉인 값을 **손으로 적지 않는다**. allocation 표는 seed 에서 재계산하고, B암 재료
본문 해시는 스냅숏에서 다시 추출한다(L-M #14 — 구 sed 문면이 빈 입력 해시를 내던 결함의 정본
대체). 손으로 적은 값은 대조가 자기 자신을 확인하는 함정이 된다.

사용:
    python3 workspace/tools/manifest_seal.py --emit          # 실측 → manifest 저작(stdout)
    python3 workspace/tools/manifest_seal.py --write         # 실측 → 봉인 파일 기록
    python3 workspace/tools/manifest_seal.py --check         # 봉인본 ↔ 실측 대조(엄격)
    python3 workspace/tools/manifest_seal.py --check --draft # PENDING 허용(봉인 전 개발 중에만)
    python3 workspace/tools/manifest_seal.py --allocation    # 18런 배정표 인쇄

exit 0 = 일치 / 2 = 드리프트·PENDING(=실런 금지) / 1 = 재료 결손
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
MANIFEST: Path = ROOT / "workspace" / "eval" / "ab" / "T2-0b-manifest.json"
SCHEMA: str = "t2-0b-manifest/1"

PENDING: str = "PENDING"

# ─────────────────────────────────────────────────────────────────────────────
# 봉인 그룹 — 각 그룹은 «왜 이것이 바뀌면 실런이 무효인가»를 함께 등재한다.
# 글롭은 저장소 루트 기준. `**` 는 하위 전체.
# ─────────────────────────────────────────────────────────────────────────────
GROUPS: "dict[str, dict]" = {
    "scorer": {
        "why": "판정 스칼라(결정적 검사기 위반 수)를 만드는 전부. 발주·암 산출물을 "
               "보기 전에 동결한다 — 산출물을 본 뒤 채점기를 만지면 판정 교락(L-M #4).",
        "globs": [
            "dddjango/scripts/check-*.py",
            "dddjango/scripts/findings.py",
            "dddjango/scripts/checker_registry.py",
            "dddjango/scripts/checker_target.py",
            "dddjango/scripts/business_vocab.py",
            "dddjango/scripts/anchor_diff.py",
            "dddjango/scripts/standard_tree.py",
            "workspace/eval/rubric/*.md",
            "workspace/eval/tools/FC-GOLDEN.md",
            # **계수 규약의 실행체**. 검사기 파일만 동결하고 «어떻게 부르는가»를 두면, 재는 법이
            # 산출물을 본 뒤에 정해진다(레인 AV 발견 1). 사람이 손으로 세는 판정 스칼라는
            # arm-blind 가 아니다.
            "workspace/tools/ab_score.py",
        ],
    },
    "pipeline": {
        "why": "3암이 공유하는 실행 경로. 암 사이 차이는 스위치 둘뿐이어야 하고, 그 «둘뿐»을 "
               "성립시키는 것이 이 파일들의 동일성이다.",
        "globs": [
            "dddjango/scripts/regen_core.py",
            "dddjango/scripts/rulepack.py",
            "dddjango/scripts/registry_gate.py",
            # pre-gate 실행기 — 차단 승격(2026-09-03)으로 G1/G1′·G2 배너의 근거를 내는 실행 경로가 됐다(설계 §9-6).
            "dddjango/scripts/design_pregate.py",
            "dddjango/commands/dddjango.md",
            "codex-dddjango/skills/dddjango/SKILL.md",
        ],
    },
    "plugin_payload": {
        "why": "절차서가 **부르는 것들**. 서브에이전트 정의와 규범 산문(`references/final.md`)이 "
               "여기 있다 — 그중 ninja §6.1·§6.2 와 ddd §3.2 는 파일럿 이관 대상 클러스터 그 "
               "자체다. 절차서만 동결하고 이것들을 두면 봉투만 봉인하고 내용물을 열어 둔 것이다. "
               "산문이 런 사이에 바뀌면 세 암이 같은 규범을 상대한 것이 아니게 되고, "
               "`coder.md` 한 줄이 바뀌면 처치와 무관하게 산출물이 달라진다.",
        "globs": [
            "dddjango/agents/*.md",
            "dddjango/skills/**/*.md",
            "dddjango/.claude-plugin/plugin.json",
            "codex-dddjango/skills/**/*.md",
            "codex-dddjango/skills/**/*.yaml",
            "codex-dddjango/.codex-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            ".agents/plugins/marketplace.json",
        ],
    },
    "packs": {
        "why": "C암 규칙 팩과 B암 재료. 팩이 바뀌면 처치 자체가 바뀐다.",
        "globs": [
            "dddjango/scripts/rulepack.json",
            # architect 가 symbols 채널에 쓰는 Base 종류 닫힌 목록(검사기 소스 기계 추출 소성물 — 팩과 같은 이유로 동결).
            "dddjango/scripts/pregate_symbol_kinds.json",
            "workspace/eval/ab/T0-rule-owner-map-snapshot.md",
        ],
    },
    "graph": {
        "why": "C암 선별의 원천. 그래프가 바뀌면 팩 재생성이 필요하고, 재생성 없이 바뀌면 "
               "팩과 그래프가 어긋난 채 실런이 돈다.",
        # `ontology/**` 은 3.13 미만에서 디렉터리만 내놓는다 — 그러면 그래프가 **0파일로 봉인**되고
        # 대조는 영원히 green 이다. `**/*` 는 두 판형 모두에서 파일을 낸다.
        "globs": ["ontology/**/*"],
    },
    "queries": {
        "why": "팩을 굽는 질의. 질의가 바뀌면 팩의 의미가 바뀐다.",
        "globs": [
            "workspace/tools/queries/*.rq",
            "workspace/tools/ontology_rulepack.py",
            "workspace/tools/derive_path_globs.py",
            "workspace/tools/section-path-map.tsv",
            # 질의의 **정답지**. 질의 파일만 동결하고 골든을 두면 «무엇이 옳은가»가 열려 있다.
            "workspace/eval/fixtures/rulepack/**/*",
        ],
    },
    "orders": {
        "why": "발주문·고정 게이트 답·허용 도구·인수 테스트. 세 암이 **같은 발주**를 받았다는 "
               "주장의 근거가 이 파일들이다 — 문면이 흔들리면 비교가 성립하지 않는다.",
        "globs": ["workspace/eval/ab/orders/*.md",
                  # **외부 인수 스위트** — 산출물이 쓴 테스트에 인수를 맡기면 인수 통과가
                  # 처치와 상관된 선택 변수가 된다(레인 AU 발견 6).
                  "workspace/eval/ab/acceptance/**/*"],
    },
    "protocol": {
        "why": "**전이 의존** — 발주문이 «그대로 따르라»고 가리키는 판형과, 인수 판정이 부르는 "
               "도구와, 게이트를 배선하는 Makefile. 이 중 하나만 바뀌어도 모델이 받는 요청문·"
               "허용 범위·STOP 규약·shape 합격 여부·실런 진입 조건이 바뀐다. 그런데 대조는 "
               "글롭에 든 것만 재전개하므로, 봉인 밖이면 그 변경은 드리프트가 아니었다"
               "(레인 AU 발견 4).",
        "globs": [
            "Makefile",
            "workspace/plan/2026-08-12-bc-rebuild-protocol.md",
            "workspace/plan/templates/request-template.md",
            "workspace/tools/openapi_shape.py",
            "workspace/tools/plugin_loop_probe.py",
            # 판단표도 여기 둔다 — 운영자가 이 문서를 읽고 «무엇이 봉인됐나»를 판단한다.
            "workspace/design/2026-08-20-ontology-t2-0b-design.md",
        ],
    },
    "preregistration": {
        "why": "분석 계획. 결과를 본 뒤 산식을 바꾸지 못하게 하는 **유일한** 장치다. "
               "원래 t2-plan 안에 있었으나 그 파일은 진행 기록이 append 되는 살아 있는 문서라 "
               "«수정 금지»가 성립하지 않았다 — 그래서 떼어내 여기서 동결한다.",
        "globs": ["workspace/eval/ab/T2-0a-preregistration.md"],
    },
    "harness": {
        "why": "측정기. 실런 중 측정기가 바뀌면 앞뒤 런의 수치가 같은 자를 안 쓴 것이 된다(D11).",
        "globs": [
            # 봉인 도구 자신도 봉인 대상이다 — 자를 바꾸면 잰 값의 뜻이 바뀐다.
            # (봉인본 JSON 은 여기 넣지 않는다. 자기 자신을 해시할 수 없고, 그 무결성은
            #  `self_sha256` 이 따로 본다.)
            "workspace/tools/manifest_seal.py",
            "workspace/tools/findings_count_matrix.py",
            "workspace/tools/construct_drift_report.py",
            "workspace/tools/rulepack_smoke.py",
            "workspace/tools/firing_probe.py",
            "workspace/tools/query_golden_check.py",
            "workspace/tools/session_bounce_counter.py",
            "workspace/tools/collect_violations.py",
            "workspace/tools/violation_adapter.py",
            "workspace/eval/ab/T2-construct-drift.md",
            # B암 프롬프트 골든이 이 두 파일 안에 상수로 산다(`_SELF_TEST_GOLDEN`).
            "workspace/tools/regen_loop_prototype.py",
            "workspace/tools/regen_loop_smoke.py",
            # 반송 계수기 픽스처 — 계수 규약의 정답지(T2-3 fragment 요구 항목).
            "workspace/eval/fixtures/bounce_counter/**/*",
            # 도구 lockfile — t2-plan §2 T2-0b 명시 항목. 그래프 도구 사슬과 runtime 계약 pin.
            "workspace/tools/ontology-requirements.txt",
            "workspace/eval/fixtures/api_error_contract/requirements.txt",
        ],
    },
}

# 두 런타임이 byte 동일해야 하는 미러 쌍(디렉터리).
MIRROR: "tuple[str, str]" = ("dddjango/scripts", "codex-dddjango/skills/dddjango/scripts")

# 3암 정의 — 차등은 환경 스위치 둘뿐이다. 값 공간까지 봉인한다.
ARMS: "dict[str, dict]" = {
    "A": {"label": "개작판 루프 off(대조군 = 현행 파이프라인)",
          "env": {"DJR_LOOP_ENABLED": "off"}},
    "B": {"label": "루프만(위반 레코드 주입 · <rules> 없음)",
          "env": {"DJR_LOOP_ENABLED": "on", "DJR_LOOP_SELECTOR": "snapshot"}},
    # 라벨을 실물에 맞춘다(레인 AV 발견 13). 「번호·명칭」만 적으면 estimand 명명이 실물보다
    # 좁아지고, C−B 를 그 이름으로 리포트하면 실제로는 조인 표지와 억제 지시문의 효과까지
    # 그 이름으로 부르게 된다.
    "C": {"label": "루프+그래프(SPARQL 선별 · <rules> = 번호·명칭 + 조인 표지 join + "
                   "후보 오적용 억제 문장) · 중복 제거·재정렬 동반",
          "env": {"DJR_LOOP_ENABLED": "on", "DJR_LOOP_SELECTOR": "sparql"}},
}
SWITCH_SPACE: "dict[str, list]" = {
    "DJR_LOOP_ENABLED": ["on", "off"],
    "DJR_LOOP_SELECTOR": ["snapshot", "sparql"],
    "DJR_EXPERIMENT_RUN_ID": ["<run_id — 런마다 다름·격리 네임스페이스>"],
}

# 맹검의 **실제 범위** — 부풀리지 않는다. 여기 적힌 것보다 더 가려진다고 리포트가 주장하면
# 그 리포트가 틀린 것이다.
BLINDING: "dict[str, str]" = {
    "scorer": "성립 — 채점 하네스는 arm 을 입력으로 받지 않는다(D11 arm-blind 계수 골든). "
              "같은 산출물이면 어느 암에서 나왔든 같은 수를 낸다.",
    "false_positive_review": "성립 — 오탐 심의는 arm·순서를 지우고 `blind_label` 만 남긴 "
                             "레코드를 codex 독립 레인에 넘긴다(규약 R4).",
    "author": "**불성립(자인)** — 배정표가 저장소에 공개되고 실행자가 곧 저자다. 저자 맹검을 "
              "주장하지 않는다. 이 구멍을 메우는 것은 맹검이 아니라 ⓐ 채점기 사전 동결 "
              "(발주·산출물 관측 전) ⓑ 산식 사전 등록 ⓒ 독립 심의 레인 셋이다.",
    "report_wording": "A/B 리포트는 «맹검 실험»이라고 쓰지 않는다. «채점기·심의 맹검, 실행자 "
                      "비맹검»으로 쓴다.",
}

ORDERS: "list[str]" = ["O-7", "O-4", "O-5"]
REPEATS: int = 2
ALLOCATION_SEED: str = "dddjango-t2-ab-allocation-2026-08-20"

# **반복 = 레인**. 사전 등록(t2-plan §2 T2-0a · L-M #9)이 «각 암을 두 레인에 균형 배정»을
# 요구한다. 반복을 레인으로 두면 각 암이 각 런타임에서 정확히 3번(발주 3 × 1) 돌아 완전
# 균형이고, 암 대비가 런타임과 교락되지 않는다. 대가는 `V̄` 의 «반복»이 런타임을 가로지르는
# 평균이 된다는 것 — 분산은 커지되 편향은 없다(리포트 한계 문구 대상).
LANES: "dict[int, str]" = {1: "claude", 2: "codex"}

# **라틴 방진 2벌** — 사전 등록의 «라틴 방진» 이행. 행=발주 · 열=블록 안 위치 · 칸=암.
# 무작위 배치는 계통 불균형을 만든다(구판 실측: 위치 1 에 A 가 **한 번도** 오지 않았다).
# 방진은 그 불균형을 구조적으로 배제한다: 각 암이 발주마다 한 번·위치마다 한 번.
# 두 방진을 합치면 위치별로 각 암이 정확히 2회.
LATIN: "dict[int, dict]" = {
    1: {"O-7": ["A", "B", "C"], "O-4": ["B", "C", "A"], "O-5": ["C", "A", "B"]},
    2: {"O-7": ["C", "B", "A"], "O-4": ["A", "C", "B"], "O-5": ["B", "A", "C"]},
}


# ─────────────────────────────────────────────────────────────────────────────
# 해시 유틸
# ─────────────────────────────────────────────────────────────────────────────
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """내용 + **실행 비트**. 모드를 빼면 `chmod +x` 가 봉인을 통과한다(레인 AU 발견 11).

    실행 비트는 검사기·게이트가 어떻게 기동되는지를 바꿀 수 있는 값이고, 내용만 해시하면
    그 변경이 봉인에 안 잡힌다. 그룹·미러·cache 대조가 모두 이 함수를 지나므로 한 곳만 고친다.
    """
    mode = "x" if path.stat().st_mode & 0o111 else "-"
    return sha256_bytes(path.read_bytes() + b"\0mode:" + mode.encode("ascii"))


def tree_hash(files: "dict[str, str]") -> str:
    """파일 목록 자체를 해시에 넣는다 — 파일이 하나 사라져도 값이 바뀌게."""
    h = hashlib.sha256()
    for rel in sorted(files):
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(files[rel].encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def _expand(globs: "list[str]") -> "list[Path]":
    """글롭을 편다. `__pycache__` 와 디렉터리는 제외."""
    hits: "set[Path]" = set()
    for pattern in globs:
        for p in ROOT.glob(pattern):
            if p.is_file() and "__pycache__" not in p.parts:
                hits.add(p)
    return sorted(hits)


def group_files(globs: "list[str]") -> "dict[str, str]":
    return {str(p.relative_to(ROOT)): sha256_file(p) for p in _expand(globs)}


# ─────────────────────────────────────────────────────────────────────────────
# B암 재료 본문 추출 (L-M #14 — awk 절차의 프로그램 정본)
# ─────────────────────────────────────────────────────────────────────────────
def snapshot_body_sha(path: Path) -> "dict[str, str]":
    """스냅숏의 **본문**(메타 주석 종료 행 다음 줄부터 EOF)을 다시 뽑아 해시한다.

    스냅숏 메타가 스스로 적어 둔 절차(`awk 'f; /-->$/{f=1}'`)의 프로그램 대응물이다.
    메타에 **선언된** 해시와 **다시 뽑은** 해시를 함께 내고, 대조는 둘이 같은지를 본다 —
    선언값만 옮겨 적으면 그 대조는 아무것도 증명하지 못한다.
    """
    raw = path.read_bytes()
    lines = raw.split(b"\n")
    idx = next((i for i, ln in enumerate(lines) if ln.endswith(b"-->")), None)
    if idx is None:
        return {"declared": PENDING, "extracted": PENDING, "error": "메타 종료 행 미발견"}
    body = b"\n".join(lines[idx + 1:])
    declared = PENDING
    for ln in lines[: idx + 1]:
        text = ln.decode("utf-8", "replace")
        if "사본 SHA-256" in text and ":" in text:
            declared = text.split(":", 1)[1].strip()
            break
    return {"declared": declared, "extracted": sha256_bytes(body),
            "body_bytes": str(len(body))}


# ─────────────────────────────────────────────────────────────────────────────
# 18런 allocation — seed 에서 재계산한다(손으로 적은 표는 대조가 불가능하다)
# ─────────────────────────────────────────────────────────────────────────────
def allocation() -> "list[dict]":
    """블록 = (발주 × 반복). 블록 안에서 3암 순서를 seed 로 섞고, 블록 순서도 섞는다.

    왜 블록인가: 1블록 계측 게이트(L-M #15)가 «발주 1×3암» 단위로 열리고, triplet 재실행
    (기술 실패 처분)도 같은 단위다. 암을 블록 밖으로 흩으면 그 두 규약이 성립하지 않는다.

    **첫 블록만 O-7 로 고정**한다. 계측 게이트는 첫 블록에서 P50/P90 을 다시 잡는 자리인데,
    비교할 기준선이 있는 판형은 O-7 뿐이다(N≥5 반복 실증 이력·판형 동결). 최소형 O-4 가 먼저
    오면 가장 싼 블록으로 전체 예산을 외삽하게 되어 재산정이 낙관 쪽으로 치우친다.
    나머지 5블록 순서는 seed 무작위 — 환경 드리프트와 발주의 교락을 줄인다.

    암 순서를 블록 안에서 섞는 이유도 같다: 세 암은 같은 baseline 에서 클린룸으로 각각 돌지만
    시간축(모델 부하·환경)은 공유하므로, 암이 늘 같은 자리에 오면 그 축과 붙는다.

    맹검 라벨은 seed 로 정한 18개 라벨의 순열이다. **이 라벨이 저자를 가려 주지는 않는다** —
    배정표가 저장소에 공개되므로 표를 본 사람은 누구든 되돌릴 수 있다. 라벨의 용도는 codex
    독립 심의 레인에 넘기는 재료에서 암을 지우는 것뿐이다(규약 R4·`blinding` 절 자인).
    """
    rng = random.Random(ALLOCATION_SEED)
    blocks: "list[dict]" = [{"order": o, "repeat": r, "arms": LATIN[r][o]}
                            for o in ORDERS for r in sorted(LANES)]
    # 블록 **순서**만 무작위다. 블록 안 배치는 방진이 정한다 — 무작위로 두면 방진의 균형이 깨진다.
    rng.shuffle(blocks)
    first = next(i for i, b in enumerate(blocks) if b["order"] == "O-7" and b["repeat"] == 1)
    blocks.insert(0, blocks.pop(first))

    labels = [f"S{i:02d}" for i in range(1, len(blocks) * len(ARMS) + 1)]
    rng.shuffle(labels)

    rows: "list[dict]" = []
    for bi, blk in enumerate(blocks, start=1):
        for pos, arm in enumerate(blk["arms"], start=1):
            n = len(rows) + 1
            rows.append({
                "run_id": f"R{n:02d}",
                "block": f"BK{bi}",
                "order": blk["order"],
                "repeat": blk["repeat"],
                "lane": LANES[blk["repeat"]],
                "position": pos,
                "arm": arm,
                "blind_label": labels[n - 1],
                "experiment_run_id": f"t2ab-R{n:02d}",
            })
    return rows


def allocation_balance() -> "dict":
    """배정표의 균형을 **재계산해서 단언 재료로 낸다**. 「방진이니까 균형이다」는 주장이지
    확인이 아니다 — 표를 다시 세어 본다."""
    rows = allocation()
    from collections import Counter
    return {
        "n_runs": len(rows),
        "by_arm": dict(Counter(r["arm"] for r in rows)),
        "by_lane_arm": {f"{ln}:{a}": sum(1 for r in rows if r["lane"] == ln and r["arm"] == a)
                        for ln in sorted(LANES.values()) for a in sorted(ARMS)},
        "by_position_arm": {f"p{p}:{a}": sum(1 for r in rows
                                             if r["position"] == p and r["arm"] == a)
                            for p in (1, 2, 3) for a in sorted(ARMS)},
        "by_order_arm": {f"{o}:{a}": sum(1 for r in rows if r["order"] == o and r["arm"] == a)
                         for o in ORDERS for a in sorted(ARMS)},
        "first_block": rows[0]["block"] if rows else None,
        "first_order": rows[0]["order"] if rows else None,
        "first_lane": rows[0]["lane"] if rows else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 외부(저장소 밖) 재료 — 측정된 값만 싣고, 못 실은 것은 PENDING 으로 남긴다
# ─────────────────────────────────────────────────────────────────────────────
def claude_install() -> "dict":
    """Claude 설치본의 **정본**은 `installed_plugins.json` 이다 — glob 이 아니라.

    앞선 판은 `sorted(glob)[-1]` 로 골랐다(레인 AV 발견 14). 문자열 정렬이라
    `sorted(['2.11.0','2.13.0','2.9.0'])[-1] == '2.9.0'` 이다 — 지금 맞는 것은 우연이고,
    2.9.x 캐시가 하나만 생기면 도구는 **런타임이 로드하지 않는 트리**를 해시하며 green 을 낸다.
    계획서가 «plugin 은 설치 캐시에서 로드»를 hard blocker 로 올려놓고 «어느 캐시인가»의
    정본을 안 읽는 것은 앞뒤가 안 맞는다.
    """
    p = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    if not p.is_file():
        return {"source": "missing", "install_path": PENDING, "version": PENDING,
                "git_commit_sha": PENDING}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return {"source": "unparsable", "install_path": PENDING, "version": PENDING,
                "git_commit_sha": PENDING}
    for key, entries in (data.get("plugins") or {}).items():
        if not key.startswith("dddjango@"):
            continue
        for e in entries or []:
            return {"source": "installed_plugins.json", "key": key,
                    "install_path": e.get("installPath", PENDING),
                    "version": e.get("version", PENDING),
                    "git_commit_sha": e.get("gitCommitSha", PENDING)}
    return {"source": "not-installed", "install_path": PENDING, "version": PENDING,
            "git_commit_sha": PENDING}


def _codex_root(codex_home: Path) -> "tuple":
    """Codex 는 설치 대장이 없어 glob 뿐이다. 그래서 **후보가 둘 이상이면 실패로 낸다** —
    사전식 최댓값으로 아무거나 고르면 틀린 트리를 봉인하고도 green 이 난다."""
    hits = sorted(codex_home.glob("plugins/cache/*/dddjango/*"))
    hits = [h for h in hits if h.is_dir()]
    if len(hits) == 1:
        return hits[0], None
    if not hits:
        return None, "codex 설치 cache 미발견"
    return None, f"codex 설치 cache 후보 {len(hits)}개 — 어느 것이 로드되는지 결정 불가: " \
                 f"{[h.name for h in hits]}"


def install_trees(claude_home: Path, codex_home: Path) -> "dict[str, str]":
    """설치 cache 두 트리의 scripts tree hash. 실런이 **실제로 로드하는 곳**이다."""
    out: "dict[str, str]" = {}
    ci = claude_install()
    ip = ci.get("install_path")
    scripts = Path(ip) / "scripts" if ip and ip != PENDING else None
    if scripts and scripts.is_dir():
        out["cache-claude"] = tree_hash(_dir_files(scripts))
        out["cache-claude_path"] = str(scripts)
    else:
        out["cache-claude"] = PENDING

    root, err = _codex_root(codex_home)
    cs = (root / "skills" / "dddjango" / "scripts") if root else None
    if cs and cs.is_dir():
        out["cache-codex"] = tree_hash(_dir_files(cs))
        out["cache-codex_path"] = str(cs)
    else:
        out["cache-codex"] = PENDING
        if err:
            out["cache-codex_error"] = err
    return out


def cache_parity(codex_home: Path) -> "dict":
    """**봉인한 파일이 설치본에도 같은 내용으로 있는가**를 파일 단위로 확인한다.

    `install_trees` 는 `scripts/` 만 본다. 그런데 봉인 대상에는 절차 정본(`commands/dddjango.md`·
    `skills/dddjango/SKILL.md`)과 서브에이전트·규범 산문이 있고, **그것들의 cache 사본은
    대조되지 않았다**(레인 AV 발견 14 후단). 실런이 로드하는 것은 cache 다.
    """
    ci = claude_install()
    ip = ci.get("install_path")
    croot = Path(ip) if ip and ip != PENDING else None
    xroot, _ = _codex_root(codex_home)

    pairs = [("claude", "dddjango/", croot), ("codex", "codex-dddjango/", xroot)]
    out: "dict" = {}
    for name, prefix, root in pairs:
        if root is None or not root.is_dir():
            out[name] = {"status": PENDING}
            continue
        missing: "list" = []
        mismatch: "list" = []
        checked = 0
        for spec in GROUPS.values():
            for p in _expand(spec["globs"]):
                rel = str(p.relative_to(ROOT))
                if not rel.startswith(prefix):
                    continue
                target = root / rel[len(prefix):]
                checked += 1
                if not target.is_file():
                    missing.append(rel)
                elif sha256_file(target) != sha256_file(p):
                    mismatch.append(rel)
        out[name] = {"status": "ok" if not (missing or mismatch) else "drift",
                     "root": str(root), "checked": checked,
                     "missing": sorted(set(missing)), "mismatch": sorted(set(mismatch))}
    return out


def _dir_files(d: Path) -> "dict[str, str]":
    """디렉터리를 상대 경로 키로 해시한다. `p.name` 을 키로 쓰면 하위 폴더의 동명 파일이
    서로를 덮어 «바뀌었는데 같은 해시»가 난다."""
    return {str(p.relative_to(d)): sha256_file(p) for p in sorted(d.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


def source_script_tree() -> "dict[str, str]":
    return {name: tree_hash(_dir_files(ROOT / rel))
            for name, rel in (("source-claude", MIRROR[0]), ("source-codex", MIRROR[1]))}


def mirror_parity() -> "dict[str, object]":
    fa = _dir_files(ROOT / MIRROR[0])
    fb = _dir_files(ROOT / MIRROR[1])
    diff = sorted(set(fa) ^ set(fb)) + sorted(k for k in set(fa) & set(fb) if fa[k] != fb[k])
    return {"identical": not diff, "n_files": len(fa), "diff": diff}


def plugin_versions() -> "dict[str, str]":
    out: "dict[str, str]" = {}
    for key, rel in (("claude", "dddjango/.claude-plugin/plugin.json"),
                     ("codex", "codex-dddjango/.codex-plugin/plugin.json")):
        try:
            out[key] = json.loads((ROOT / rel).read_text(encoding="utf-8")).get("version", PENDING)
        except Exception:
            out[key] = PENDING
    return out


_SCHEMA_SOURCES: "tuple" = (
    ("findings", "dddjango/scripts/findings.py"),
    ("gate_introduced", "dddjango/scripts/registry_gate.py"),
    ("gate_contract", "dddjango/scripts/registry_gate.py"),
    ("regen_prompt", "dddjango/scripts/regen_core.py"),
    ("injection_capacity", "dddjango/scripts/regen_core.py"),
    ("rulepack", "dddjango/scripts/rulepack.py"),
)


def schemas() -> "dict[str, list]":
    """레코드·sidecar·프롬프트·팩의 **스키마 문자열**을 파일에서 뽑아 싣는다.

    해시가 이미 어떤 변경이든 잡는다. 그런데 «`gate-contract/0` → `/1`» 같은 버전 올림은
    해시 한 줄로만 보이면 **무엇이 바뀌었는지 안 보인다**. 이름을 함께 봉인하면 red 의 뜻이
    읽힌다. 값을 손으로 적지 않고 **실물에서 뽑는다**.

    **정정**(레인 AU 발견 7): 앞선 문면은 `injection-capacity/2` 를 T2-3 의
    «turn-log schema/version» 이행이라고 적었는데, 그건 사실이 아니었다 — 그 로그는 selector 와
    용량만 실었고 `loop-turn/1` 은 비인과 Shell A prototype 에만 있었다. 지금은
    `injection-capacity/3` 이 회전 서수·환경 스위치·실행 코어 해시를 함께 싣는다.
    **여전히 이 로그가 소유하지 않는 것**: 모델 ID·권한 모드·타임아웃 — 스크립트 안에서 알 수
    없는 값이라 **암 영수증**(`arm-receipt/0`)과 부속서 `runtime` 이 소유한다.
    """
    import re
    pat = re.compile(r'"([a-z][a-z-]*/[0-9]+)"')
    out: "dict[str, list]" = {}
    for name, rel in _SCHEMA_SOURCES:
        p = ROOT / rel
        found = sorted(set(pat.findall(p.read_text(encoding="utf-8")))) if p.is_file() else []
        out.setdefault(rel, [])
        out[rel] = found
    return out


def c_arm_material() -> "dict":
    """C암이 실제로 더 싣는 것 — B암에 `b_arm_material` 이 있듯 C암에도 대응물을 둔다.

    앞선 판에는 이 항목이 없었다(레인 AV 발견 13). 그래서 「C는 번호·명칭을 더 싣는다」는
    문면만 있고, 실물이 그보다 넓다는 사실(조인 표지 `join` · 후보 오적용 억제 문장 3줄)이
    봉인 어디에도 안 남았다. 값은 실물에서 **뽑는다**.
    """
    # **정규식으로 문자열 리터럴을 파싱하지 않는다.** 첫 시도는 `[^"]*` 로 긁었는데,
    # 문면 안에 `\"exact\"` 가 있어 84 byte 에서 잘렸다 — 그 잘린 값도 «해시»처럼 보였다.
    # AST 로 실제 리터럴을 평가한다.
    import ast
    src = (ROOT / "dddjango" / "scripts" / "regen_core.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    consts: "dict" = {}
    for node in tree.body:
        target = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target = node.target.id
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
        if target in ("_RULES_NOTE", "RULE_FIELDS") and node.value is not None:
            try:
                consts[target] = ast.literal_eval(node.value)
            except ValueError:
                pass
    note_text = consts.get("_RULES_NOTE", "")
    return {
        "rule_fields": list(consts.get("RULE_FIELDS", [])),
        "rules_note_sha256": sha256_bytes(note_text.encode("utf-8")) if note_text else PENDING,
        "rules_note_bytes": len(note_text.encode("utf-8")),
        "note": "C는 <rules> 블록에 번호·명칭 **과 함께** 조인 표지와 억제 지시문을 싣는다. "
                "estimand 명명은 이 폭에 맞춘다.",
    }


def git_head(repo: Path = ROOT) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return PENDING


def tracked_tree_hash(repo: Path) -> str:
    """추적 경로의 **워킹트리 실물**(내용+모드)을 해시한다 — O-5 리셋 동등성의 자.

    앞선 판은 `git ls-files -s` 였다(레인 AU 발견 3). 그건 **인덱스**를 읽는다 — 실측으로
    `Makefile` 이 수정돼 있는데도 인덱스 blob 만 보고 정상값을 냈다. 리셋 실증은 「디스크에
    무엇이 있는가」를 물어야 하는데 인덱스는 그 질문에 답하지 않는다.
    """
    try:
        ls = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"],
                            capture_output=True, check=True).stdout
    except Exception:
        return PENDING
    h = hashlib.sha256()
    for raw in ls.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8", "surrogateescape")
        p = repo / rel
        h.update(raw)
        h.update(b"\0")
        h.update((sha256_file(p) if p.is_file() else "ABSENT").encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def worktree_state(repo: Path) -> "dict":
    """리셋이 정말 클린룸을 만들었는지의 **전수 상태**.

    미추적만 보면 안 된다(레인 AU 발견 3): ⓐ 수정된 추적 파일(`git diff`)과 ⓑ 스테이징된
    변경(`--cached`)과 ⓒ **ignored 오염**(`__pycache__`·`.dddjango/`·`.env.local` — 전부
    `.gitignore` 에 있어 `??` 에 안 나온다)이 각각 다른 경로로 남는다. O-5 가 지목한 위험은
    정확히 ⓒ 다.
    """
    def _run(args: "list[str]") -> "tuple":
        try:
            p = subprocess.run(["git", "-C", str(repo), *args],
                               capture_output=True, text=True, check=False)
            return p.returncode, p.stdout
        except Exception:
            return 1, ""

    rc_dirty, _ = _run(["diff", "--quiet"])
    rc_staged, _ = _run(["diff", "--cached", "--quiet"])
    _, porcelain = _run(["status", "--porcelain", "--untracked-files=all"])
    _, ignored = _run(["status", "--porcelain", "--ignored=matching",
                       "--untracked-files=all"])
    un = sorted(ln[3:] for ln in porcelain.splitlines() if ln.startswith("?? "))
    ig = sorted(ln[3:] for ln in ignored.splitlines() if ln.startswith("!! "))
    return {
        "modified_tracked": rc_dirty != 0,
        "staged": rc_staged != 0,
        "untracked_n": len(un), "untracked": un[:80],
        "ignored_n": len(ig), "ignored": ig[:80],
        "clean": rc_dirty == 0 and rc_staged == 0 and not un and not ig,
    }


def untracked(repo: Path) -> "list[str]":
    return worktree_state(repo)["untracked"]


def measure_annex(targets: "dict") -> "dict":
    """타깃 접근이 있을 때 **한 번** 돌려 외부 부속서를 채운다.

    비싼 실측(`make test` 수 따위)은 여기서 돌리지 않는다 — 그건 앵커 preflight ⑹ 가 이미
    기록한 값이므로 `targets` 로 받아 그대로 싣는다. 이 도구가 다시 재는 것은 **경로가 실재하고
    커밋이 고정됐는가**뿐이다. 남의 저장소에서 무거운 명령을 자동으로 돌리지 않는다.
    """
    # 키 자체가 없으면 `PENDING` 스캔이 아무것도 못 찾아 **없는 값이 통과**한다. 기본 키를
    # 먼저 깔고 그 위에 실측을 덮는다.
    runtime = {"claude_model_id": PENDING, "codex_model_id": PENDING,
               "permission_mode": PENDING, "thinking": PENDING,
               "codex_reasoning_effort": PENDING,
               # 발주 봉인 항목 «허용 도구»(t2-plan §2 T2-0a L-M #10). 「파이프라인 기본값
               # 그대로」는 봉인이 아니다 — 그 기본값이 무엇인지가 어디에도 안 적혀 있으면
               # 세션 설정이 바뀔 때 조용히 달라진다.
               "allowed_tools": PENDING,
               "hard_stop": {"O-7": "기계 4h · 과금 10M", "O-4": "기계 4h · 과금 10M",
                             "O-5": "기계 8h · 과금 20M"}}
    runtime.update(targets.get("runtime") or {})
    out: "dict" = {"why": (
        "저장소 밖 재료 — 타깃 저장소·클린룸 앵커·실런 런타임. 측정에는 타깃 접근이 필요하다."),
        "runtime": runtime, "orders": {}}
    for order in ORDERS:
        spec = (targets.get("orders") or {}).get(order) or {}
        repo_s = spec.get("target_repo")
        repo = Path(repo_s).expanduser() if repo_s else None
        row: "dict" = {
            "target_repo": str(repo) if repo else PENDING,
            "reachable": bool(repo and repo.is_dir()),
            "baseline_commit": git_head(repo) if repo and repo.is_dir() else PENDING,
            "tracked_tree_sha256": tracked_tree_hash(repo) if repo and repo.is_dir() else PENDING,
            "baseline_tests": spec.get("baseline_tests") or PENDING,
            "artifacts": {},
        }
        for rel in spec.get("artifacts") or []:
            p = (repo / rel) if repo else None
            row["artifacts"][rel] = sha256_file(p) if p and p.is_file() else PENDING
        if order == "O-5":
            row["stub_induced_red"] = spec.get("stub_induced_red") or PENDING
        # **리셋 앵커는 세 발주 전부의 요구 항목이다**(레인 AV 발견 10). 앞선 판은 O-5 에만
        # 뒀는데, O-4 도 워크트리 판형이라 미추적 `.dddjango/` 가 git 리셋에 똑같이 살아남고
        # 6런을 돈다. O-5 §4 의 논거(「추적 파일만 같고 미추적 오염이 남으면 클린룸이 아니다」)는
        # O-4 에 그대로 적용된다. O-7 은 폴더 삭제 후 재클론이라 명령만 다르다.
        anchor = spec.get("reset_anchor") or {}
        row["reset_anchor"] = {
            "baseline_commit": anchor.get("baseline_commit", PENDING),
            "reset_command": anchor.get("reset_command", PENDING),
            "post_reset_tree_sha256": anchor.get("post_reset_tree_sha256", PENDING),
            "post_reset_untracked": anchor.get("post_reset_untracked", PENDING),
            # ignored 오염(`__pycache__`·`.dddjango/`·`.env.local`)은 `??` 에 안 나온다 —
            # O-5 가 지목한 위험이 정확히 이것이라 별도 칸으로 요구한다(레인 AU 발견 3).
            "post_reset_ignored": anchor.get("post_reset_ignored", PENDING),
            "demonstrated_at": anchor.get("demonstrated_at", PENDING),
        }
        out["orders"][order] = row

    # O-5 는 D10 이 «실증 1회»를 재판정의 조건으로 걸어 둔 발주라 별칭을 남긴다(추적 편의).
    out["o5_cleanroom_anchor"] = out["orders"]["O-5"]["reset_anchor"]
    out["initial_memory"] = memory_state(targets.get("memory_projects") or [])
    # 상태를 스스로 «측정됨»이라 부르지 않는다. `PENDING` 문자열 유무만 보던 판이
    # 빈 값·잘못된 타입·빈 목록을 전부 통과시켰으므로(레인 AU 발견 2), **스키마 검증**을 건다.
    problems = _walk_pending(out) + validate_annex(out)
    out["status"] = "measured" if not problems else PENDING
    out["validation"] = {"ok": not problems, "problems": problems[:40]}
    return out


def memory_state(project_keys: "list[str]") -> "dict":
    """실런 세션이 로드할 **에이전트 메모리**의 시작 상태.

    이것이 왜 부속서 1급 항목인가: `~/.claude/projects/-Users-hyun-Desktop-broccoli-server/memory/`
    에는 이미 «어느 검사기가 어느 검사기와 부딪히는가·게이트를 어떻게 통과시키는가»를 정리한
    파일이 10개 있다(실측 2026-08-20). broccoli-server 는 O-4·O-5 의 타깃이고, 저것은 **C암
    처치가 주려는 바로 그 종류의 지식**이다. 그대로 두면 ⓐ 세 암이 시작부터 무장해 천장 효과가
    나고 ⓑ 메모리가 런 중에 자라 뒤 런이 유리해지며 ⓒ 클린룸 원칙(옛 구현 열람 금지)이
    결론 형태로 새어 든다.

    **처분은 대피지 삭제가 아니다** — 실행자가 런 전에 디렉터리 이름을 바꾸고 18런 뒤 되돌린다.
    여기서는 그 전/후 상태를 기록만 한다.
    """
    home = Path.home() / ".claude" / "projects"
    rows: "dict" = {}
    for key in project_keys:
        d = home / key / "memory"
        if not d.is_dir():
            rows[key] = {"exists": False, "n_files": 0, "tree_sha256": tree_hash({})}
            continue
        files = {str(p.relative_to(d)): sha256_file(p) for p in sorted(d.rglob("*"))
                 if p.is_file()}
        rows[key] = {"exists": True, "n_files": len(files),
                     "files": sorted(files), "tree_sha256": tree_hash(files)}
    return {"policy": ("런 전 대피(이름 변경)·18런 뒤 복구. 삭제 금지. 런마다 사전 확인."),
            "projects": rows or PENDING}


# ─────────────────────────────────────────────────────────────────────────────
# manifest 저작
# ─────────────────────────────────────────────────────────────────────────────
def canonical(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build(claude_home: Path, codex_home: Path, prior: "dict | None" = None) -> "dict":
    """실측으로 manifest 를 짓는다. `prior` 가 있으면 **외부 부속서만** 물려받는다.

    물려받는 범위를 외부 부속서로 좁히는 이유: 저장소 안 값은 언제든 다시 잴 수 있으므로
    물려받을 이유가 없고, 물려받으면 «옛 값이 새 실측을 덮는» 사고가 난다.
    """
    groups: "dict[str, dict]" = {}
    for name, spec in GROUPS.items():
        files = group_files(spec["globs"])
        groups[name] = {
            "why": spec["why"],
            "globs": spec["globs"],
            "n_files": len(files),
            "files": files,
            "tree_sha256": tree_hash(files),
        }

    # 물려받을 때 **새 필수 키를 보충**한다. 앞선 판은 옛 부속서를 그대로 승계해,
    # 뒤에 신설된 `initial_memory`·`allowed_tools`·발주별 `reset_anchor` 가 통째로
    # 빠진 채 남았다(레인 AU 발견 2 후단).
    fresh = measure_annex({})
    annex = (prior or {}).get("external_annex") or {}
    annex = _merge_defaults(fresh, annex)
    annex["status"] = "measured" if not (_walk_pending(annex) + validate_annex(annex)) \
        else PENDING

    manifest: "dict" = {
        "schema": SCHEMA,
        "status": "draft",
        "sealed_commit": git_head(),
        "groups": groups,
        "mirror_parity": mirror_parity(),
        "script_trees": {**source_script_tree(), **install_trees(claude_home, codex_home)},
        "claude_install": claude_install(),
        "cache_parity": cache_parity(codex_home),
        "plugin_versions": plugin_versions(),
        "arms": ARMS,
        "switch_space": SWITCH_SPACE,
        "b_arm_material": snapshot_body_sha(
            ROOT / "workspace" / "eval" / "ab" / "T0-rule-owner-map-snapshot.md"),
        "c_arm_material": c_arm_material(),
        "initial_state": initial_state(),
        "allocation": {"seed": ALLOCATION_SEED, "orders": ORDERS, "repeats": REPEATS,
                       "lanes": LANES, "latin_squares": LATIN,
                       "n_runs": len(ORDERS) * REPEATS * len(ARMS), "rows": allocation(),
                       "balance": allocation_balance()},
        "blinding": BLINDING,
        "schemas": schemas(),
        "external_annex": annex,
    }
    manifest["self_sha256"] = sha256_bytes(canonical(manifest).encode("utf-8"))
    return manifest


def initial_state() -> "dict":
    """실런 시작 시점의 상태 — «비어 있음»도 봉인해야 하는 값이다.

    위반 이력이 비어 있다는 것은 run namespace 격리의 출발점이고, 나중에 «원래 있었다»는
    변명이 불가능해진다.
    """
    vio = ROOT / "workspace" / "eval" / "violations"
    files = sorted(str(p.relative_to(ROOT)) for p in vio.rglob("*") if p.is_file()) \
        if vio.is_dir() else []
    graph = group_files(["ontology/**/*"])   # `**` 단독은 3.13 미만에서 디렉터리만 낸다
    return {
        "violation_history": {
            "dir": "workspace/eval/violations",
            # **이것은 목적지이지 원천이 아니다**(레인 AV 발견 10). 실제 생산자는 타깃 안의
            # `<TARGET>/.dddjango/violations/` 이고, 그 폴더는 **미추적**이라 git 기반 리셋에
            # 살아남는다. 저장소 측 목적지가 비어 있다는 사실은 런 사이 오염을 조금도
            # 배제하지 못한다 — 원천 측 처분은 부속서 `orders[*].reset_anchor` 소관이다.
            "role": "목적지(수집 대상) — 원천은 <TARGET>/.dddjango/violations/",
            "exists": vio.is_dir(), "n_files": len(files), "files": files},
        "knowledge_graph_tree_sha256": tree_hash(graph),
        "ledger_sha256": sha256_file(ROOT / "ontology" / "LEDGER.tsv"),
        "issued_sha256": sha256_file(ROOT / "ontology" / "ISSUED"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 대조
# ─────────────────────────────────────────────────────────────────────────────
_HEX64 = "0123456789abcdef"


def _is_sha(v: object) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in _HEX64 for c in v)


def _nonempty_str(v: object) -> bool:
    return isinstance(v, str) and bool(v.strip()) and v != PENDING


def validate_annex(annex: "dict") -> "list[str]":
    """부속서를 **스키마로** 검증한다 — `PENDING` 문자열 찾기가 아니라.

    앞선 판은 값의 형식을 안 봤다(레인 AU 발견 2·9). 실측 재현에서 `""`·`{}`·`0`·`[]` 를
    넣자 `status=measured` 가 나오고 엄격 대조가 exit 0 이었다. 「값이 있다」가 아니라
    「문자열이 정확히 PENDING 은 아니다」만 증명하고 있었던 것이다. 그 구멍으로는
    모델 ID 도, baseline 수도, 스텁 기인 red 목록도, 메모리 격리도 전부 빈 값으로 통과한다.
    """
    bad: "list[str]" = []
    if not isinstance(annex, dict):
        return ["external_annex 가 객체가 아니다"]

    rt = annex.get("runtime")
    if not isinstance(rt, dict):
        bad.append("runtime 이 객체가 아니다")
    else:
        for k in ("claude_model_id", "codex_model_id", "permission_mode", "thinking",
                  "codex_reasoning_effort", "allowed_tools"):
            if not _nonempty_str(rt.get(k)):
                bad.append(f"runtime.{k}: 비어 있거나 문자열이 아니다 ({rt.get(k)!r})")
        if not isinstance(rt.get("hard_stop"), dict) or len(rt.get("hard_stop") or {}) < 3:
            bad.append("runtime.hard_stop: 발주 3건 상한이 없다")

    orders = annex.get("orders")
    if not isinstance(orders, dict) or set(orders) != set(ORDERS):
        bad.append(f"orders 키가 {ORDERS} 와 다르다")
        orders = orders if isinstance(orders, dict) else {}
    for name in ORDERS:
        row = orders.get(name)
        if not isinstance(row, dict):
            bad.append(f"orders.{name}: 객체가 아니다")
            continue
        if not _nonempty_str(row.get("target_repo")):
            bad.append(f"orders.{name}.target_repo 비어 있음")
        if row.get("reachable") is not True:
            bad.append(f"orders.{name}: 타깃에 도달하지 못했다(reachable != true)")
        if not _nonempty_str(row.get("baseline_commit")):
            bad.append(f"orders.{name}.baseline_commit 비어 있음")
        if not _is_sha(row.get("tracked_tree_sha256")):
            bad.append(f"orders.{name}.tracked_tree_sha256 이 sha256 이 아니다")
        bt = row.get("baseline_tests")
        if not isinstance(bt, dict) or not all(isinstance(bt.get(k), int)
                                               for k in ("green", "red")):
            bad.append(f"orders.{name}.baseline_tests: {{green:int, red:int}} 가 아니다")
        arts = row.get("artifacts")
        if not isinstance(arts, dict) or not arts:
            bad.append(f"orders.{name}.artifacts 가 비어 있다 — 발주 재료 해시가 없다")
        else:
            for rel, sha in arts.items():
                if not _is_sha(sha):
                    bad.append(f"orders.{name}.artifacts[{rel}] 이 sha256 이 아니다")
        anc = row.get("reset_anchor")
        if not isinstance(anc, dict):
            bad.append(f"orders.{name}.reset_anchor 가 없다")
        else:
            if not _nonempty_str(anc.get("baseline_commit")):
                bad.append(f"orders.{name}.reset_anchor.baseline_commit 비어 있음")
            if not _nonempty_str(anc.get("reset_command")):
                bad.append(f"orders.{name}.reset_anchor.reset_command 비어 있음")
            if not _is_sha(anc.get("post_reset_tree_sha256")):
                bad.append(f"orders.{name}.reset_anchor.post_reset_tree_sha256 이 sha256 이 아니다")
            # 리셋 후 잔여물은 **없어야** 한다 — 「목록이 있다」가 아니라 「비었다」가 조건이다.
            for key in ("post_reset_untracked", "post_reset_ignored"):
                v = anc.get(key)
                if not isinstance(v, list):
                    bad.append(f"orders.{name}.reset_anchor.{key} 가 목록이 아니다")
                elif v:
                    bad.append(f"orders.{name}.reset_anchor.{key}: 리셋 후 잔여 {len(v)}건 — "
                               f"클린룸이 아니다 {v[:3]}")
            if not _nonempty_str(anc.get("demonstrated_at")):
                bad.append(f"orders.{name}.reset_anchor.demonstrated_at 비어 있음")
        if name == "O-5":
            sr = row.get("stub_induced_red")
            if not isinstance(sr, list):
                bad.append("orders.O-5.stub_induced_red 가 **목록**이 아니다 — 임의 문자열은 "
                           "증거가 아니다(처치가 만든 red 를 사후에 baseline 으로 재분류할 수 있다)")

    mem = annex.get("initial_memory")
    if not isinstance(mem, dict) or not isinstance(mem.get("projects"), dict) \
            or not mem.get("projects"):
        bad.append("initial_memory.projects 가 비어 있다 — 대피 대상을 열거하지 않았다")
    else:
        for key, row in mem["projects"].items():
            if row.get("exists"):
                bad.append(f"initial_memory[{key}]: 메모리가 **대피되지 않았다**"
                           f"(n_files={row.get('n_files')})")
    return bad


def _merge_defaults(default: object, have: object) -> object:
    """기본 뼈대에 기존 값을 얹는다 — **키는 기본 뼈대가 정한다**."""
    if not isinstance(default, dict):
        return have if have is not None else default
    if not isinstance(have, dict):
        return default
    merged = {k: (_merge_defaults(v, have[k]) if k in have else v)
              for k, v in default.items()}
    merged.update({k: v for k, v in have.items() if k not in default})
    return merged


def _walk_pending(node: object, path: str = "") -> "list[str]":
    hits: "list[str]" = []
    if isinstance(node, dict):
        for k, v in node.items():
            hits += _walk_pending(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            hits += _walk_pending(v, f"{path}[{i}]")
    elif node == PENDING:
        hits.append(path)
    return hits


def check(claude_home: Path, codex_home: Path, draft_ok: bool,
          manifest: "Path | None" = None) -> int:
    path = manifest or MANIFEST
    if not path.is_file():
        print(f"[manifest] 봉인본 부재: {path} — `--write` 미실행", file=sys.stderr)
        return 1
    sealed = json.loads(path.read_text(encoding="utf-8"))
    fails: "list[str]" = []

    if sealed.get("schema") != SCHEMA:
        fails.append(f"schema 불일치: {sealed.get('schema')} ≠ {SCHEMA}")

    # ① manifest 자체의 무결성 — 손편집 탐지
    declared = sealed.pop("self_sha256", None)
    recomputed = sha256_bytes(canonical(sealed).encode("utf-8"))
    sealed["self_sha256"] = declared
    if declared != recomputed:
        fails.append(f"self_sha256 불일치(손편집 의심): 선언 {str(declared)[:16]} ≠ "
                     f"실측 {recomputed[:16]}")

    # ② 그룹 — 글롭 재전개로 «추가/삭제»까지 잡는다
    for name, spec in GROUPS.items():
        s = sealed.get("groups", {}).get(name)
        if not s:
            fails.append(f"그룹 미등재: {name}")
            continue
        if s.get("globs") != spec["globs"]:
            fails.append(f"{name}: 글롭 정의가 봉인본과 다르다(도구 개정 — 재봉인 필요)")
            continue
        now = group_files(spec["globs"])
        was = s.get("files", {})
        added = sorted(set(now) - set(was))
        removed = sorted(set(was) - set(now))
        changed = sorted(k for k in set(now) & set(was) if now[k] != was[k])
        for k in added:
            fails.append(f"{name}: 봉인 후 추가 — {k}")
        for k in removed:
            fails.append(f"{name}: 봉인 후 삭제 — {k}")
        for k in changed:
            fails.append(f"{name}: 봉인 후 변경 — {k}")
        if tree_hash(now) != s.get("tree_sha256"):
            fails.append(f"{name}: tree_sha256 드리프트")

    # ③ 미러 동일성 — 봉인 시점에 참이었다면 지금도 참이어야 한다
    mp = mirror_parity()
    if not mp["identical"]:
        fails.append(f"미러 파손: {mp['diff'][:5]}")

    # ④ 스크립트 트리(설치 cache 포함) — 실런이 로드하는 곳
    # 설치 cache 축은 **엄격 모드에서만** 본다. 개발 중에는 source 를 고치고 나서 설치본을
    # 갱신하기 전까지 반드시 어긋나며, 그 어긋남으로 상시 검증을 red 로 만들면 아무도 verify 를
    # 못 돌린다. cache 가 낡은 동안 막아야 하는 것은 **C 실런**이지 일반 검증이 아니다
    # (firing probe 와 같은 배치 — T2-4 AT 4-2 정정).
    now_trees = {**source_script_tree(), **install_trees(claude_home, codex_home)}
    for k, v in (sealed.get("script_trees") or {}).items():
        if k.endswith("_path") or k.endswith("_error"):
            continue
        if draft_ok and k.startswith("cache-"):
            continue
        if now_trees.get(k) != v:
            fails.append(f"script_trees[{k}] 드리프트: 봉인 {str(v)[:16]} ≠ "
                         f"실측 {str(now_trees.get(k))[:16]}")
    scope_keys = [k for k in now_trees
                  if not k.endswith(("_path", "_error"))
                  and not (draft_ok and k.startswith("cache-"))]
    live = {k: now_trees[k] for k in scope_keys if now_trees[k] != PENDING}
    if len(set(live.values())) > 1:
        fails.append(f"트리 해시 불일치: {sorted(set(live))}")

    # ⑤ B암 재료 — 선언값이 아니라 **다시 뽑은 본문**과 대조한다
    b = snapshot_body_sha(ROOT / "workspace" / "eval" / "ab" / "T0-rule-owner-map-snapshot.md")
    if b.get("declared") != b.get("extracted"):
        fails.append(f"B암 재료: 메타 선언 {str(b.get('declared'))[:16]} ≠ "
                     f"재추출 {str(b.get('extracted'))[:16]}")
    if sealed.get("b_arm_material", {}).get("extracted") != b.get("extracted"):
        fails.append("B암 재료: 봉인본과 재추출 본문 해시 불일치")

    # ⑥ allocation — seed 재계산과 일치해야 하고, 균형은 **다시 세어** 확인한다
    if sealed.get("allocation", {}).get("rows") != allocation():
        fails.append("allocation: seed 재계산과 불일치(표를 손으로 고쳤거나 seed 가 바뀌었다)")
    bal = allocation_balance()
    if sealed.get("allocation", {}).get("balance") != bal:
        fails.append("allocation.balance: 재계산과 불일치")
    if sorted(bal["by_arm"].values()) != [6, 6, 6]:
        fails.append(f"allocation: 암별 런 수 불균형 {bal['by_arm']}")
    if set(bal["by_lane_arm"].values()) != {3}:
        fails.append(f"allocation: 레인×암 불균형 {bal['by_lane_arm']}")
    if set(bal["by_position_arm"].values()) != {2}:
        fails.append(f"allocation: 위치×암 불균형(라틴 방진 파손) {bal['by_position_arm']}")
    if set(bal["by_order_arm"].values()) != {2}:
        fails.append(f"allocation: 발주×암 불균형 {bal['by_order_arm']}")
    if (bal["first_order"], bal["first_lane"]) != ("O-7", "claude"):
        fails.append(f"allocation: 첫 블록이 O-7·claude 가 아니다 — {bal['first_order']}·"
                     f"{bal['first_lane']}(계측 게이트 기준선 상실)")

    # ⑨ 스키마 이름 — 해시가 잡는 변경의 «뜻»을 읽히게 한다
    if sealed.get("schemas") != schemas():
        fails.append("schemas: 스키마 문자열 드리프트(버전 올림 의심)")

    # ⑦ 초기 스냅숏
    if sealed.get("initial_state") != initial_state():
        fails.append("initial_state 드리프트(위반 이력·그래프·LEDGER·ISSUED)")

    # ⑧′ 출처 복원 가능성 — 봉인 파일이 `sealed_commit` 에 **실재**해야 한다(레인 AV 발견 11).
    # 미추적 파일만 해시하면 봉인은 자기참조로 닫힌다: 해시는 manifest 에 있고 manifest 도
    # 커밋 밖이면, «그때 그 문면이었다»를 제3자가 확인할 경로가 없다. `git clean`·새 클론·
    # 워크트리 전환 어느 것도 그 파일을 되살리지 못한다.
    # 개발 중(`--draft`)에는 걸지 않는다 — 편집→검증→커밋 순서를 막지 않기 위해서다.
    if not draft_ok:
        commit = sealed.get("sealed_commit")
        if not commit or commit == PENDING:
            fails.append("sealed_commit 미지정 — 출처를 커밋에 고정하지 않았다")
        else:
            absent: "list[str]" = []
            differ: "list[str]" = []
            for gname, g in (sealed.get("groups") or {}).items():
                for rel, want in g.get("files", {}).items():
                    r = subprocess.run(["git", "-C", str(ROOT), "cat-file", "blob",
                                        f"{commit}:{rel}"], capture_output=True)
                    if r.returncode != 0:
                        absent.append(f"{gname}/{rel}")
                        continue
                    # 존재만 보면 «커밋에 있긴 한데 내용이 다른» 경우를 놓친다. 실행 비트는
                    # blob 으로 알 수 없으므로 내용만 대조하고, 모드는 워킹트리 대조가 본다.
                    if sha256_bytes(r.stdout + b"\0mode:-") != want and \
                       sha256_bytes(r.stdout + b"\0mode:x") != want:
                        differ.append(f"{gname}/{rel}")
            for a in absent[:8]:
                fails.append(f"sealed_commit 에 부재 — {a}")
            if len(absent) > 8:
                fails.append(f"… sealed_commit 부재 {len(absent) - 8}건 더")
            for d in differ[:8]:
                fails.append(f"sealed_commit 의 내용이 봉인값과 다르다 — {d}")
            if len(differ) > 8:
                fails.append(f"… sealed_commit 내용 불일치 {len(differ) - 8}건 더")

    # ⑧″ 설치본 대조 — 실런이 로드하는 것이 봉인한 것과 같은가
    if not draft_ok:
        for name, row in cache_parity(codex_home).items():
            if row.get("status") != "ok":
                fails.append(f"cache_parity[{name}]: {row.get('status')} — "
                             f"부재 {len(row.get('missing') or [])} · "
                             f"불일치 {len(row.get('mismatch') or [])}")

    # ⑧ PENDING — 엄격 모드에서는 이것만으로 실런 금지
    pend = _walk_pending(sealed)
    if pend and not draft_ok:
        for p in pend[:12]:
            fails.append(f"PENDING 잔존: {p}")
        if len(pend) > 12:
            fails.append(f"… PENDING {len(pend) - 12}건 더")
    if sealed.get("status") != "sealed" and not draft_ok:
        fails.append(f"status={sealed.get('status')} — 아직 봉인되지 않았다")
    # 저장된 `status` 를 믿지 않는다 — 부속서를 **여기서 다시 검증**한다(레인 AU 발견 2).
    if not draft_ok:
        for msg in validate_annex(sealed.get("external_annex") or {})[:12]:
            fails.append(f"external_annex: {msg}")

    if fails:
        print(f"[manifest] **RED — 실런 금지** · 지적 {len(fails)}건")
        for f in fails:
            print(f"  ✗ {f}")
        return 2
    n = sum(g["n_files"] for g in sealed["groups"].values())
    print(f"[manifest] green · 그룹 {len(GROUPS)} · 봉인 파일 {n} · "
          f"배정 {len(sealed['allocation']['rows'])}런 · 상태 {sealed.get('status')}")
    return 0


def self_test() -> int:
    """대조가 **실제로 무는지** 변이로 확인한다.

    이 도구의 위험은 «항상 green» 이다. 그래서 봉인본 사본에 다섯 가지 변이를 넣고 각각이
    red 로 잡히는지 본다. 변이는 사본에만 넣고 **정답은 저장소 실물**에서 나온다 — 같은
    함수로 양쪽을 만들면 무엇도 증명하지 못한다(AT 4-2 교훈).

    자기 해시를 다시 맞춰 주는 변이(M1~M3·M5)와 안 맞춰 주는 변이(M4)를 나눠, 각 탐지기가
    **자기 몫으로** 잡는지 확인한다. 안 그러면 self_sha256 하나가 전부를 가려 다른 탐지기가
    죽어 있어도 green 이 안 뜬다.
    """
    import copy
    import tempfile

    if not MANIFEST.is_file():
        print("[self-test] 봉인본 부재 — `--write` 선행 필요", file=sys.stderr)
        return 1
    base = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def reseal(m: "dict") -> "dict":
        m.pop("self_sha256", None)
        m["self_sha256"] = sha256_bytes(canonical(m).encode("utf-8"))
        return m

    def mutate_hash(m: "dict") -> "dict":
        g = m["groups"]["pipeline"]["files"]
        k = sorted(g)[0]
        g[k] = "0" * 64
        m["groups"]["pipeline"]["tree_sha256"] = tree_hash(g)
        return reseal(m)

    def mutate_drop(m: "dict") -> "dict":
        g = m["groups"]["scorer"]["files"]
        g.pop(sorted(g)[0])
        m["groups"]["scorer"]["n_files"] = len(g)
        m["groups"]["scorer"]["tree_sha256"] = tree_hash(g)
        return reseal(m)

    def mutate_ghost(m: "dict") -> "dict":
        g = m["groups"]["harness"]["files"]
        g["workspace/tools/does-not-exist.py"] = "f" * 64
        m["groups"]["harness"]["n_files"] = len(g)
        m["groups"]["harness"]["tree_sha256"] = tree_hash(g)
        return reseal(m)

    def mutate_handedit(m: "dict") -> "dict":
        m["groups"]["graph"]["tree_sha256"] = "e" * 64   # self_sha256 은 그대로 둔다
        return m

    def mutate_alloc(m: "dict") -> "dict":
        # 값을 **바꾸는** 변이여야 한다. 앞선 판은 `arm = "A"` 로 고정했는데 R01 의 암이 마침
        # A 라 변이가 무효였고, 하네스가 그 사실을 «놓침»으로 정직하게 드러냈다.
        row = m["allocation"]["rows"][0]
        row["arm"] = "B" if row["arm"] != "B" else "C"
        return reseal(m)

    def mutate_balance(m: "dict") -> "dict":
        m["allocation"]["balance"]["by_arm"] = {"A": 7, "B": 6, "C": 5}
        return reseal(m)

    def mutate_schema(m: "dict") -> "dict":
        key = sorted(m["schemas"])[0]
        m["schemas"][key] = ["bogus/9"]
        return reseal(m)

    cases = [
        ("M1 봉인 파일 내용 변조", mutate_hash, "봉인 후 변경"),
        ("M2 봉인 목록에서 파일 누락", mutate_drop, "봉인 후 추가"),
        ("M3 실재하지 않는 파일 등재", mutate_ghost, "봉인 후 삭제"),
        ("M4 manifest 손편집(자기 해시 미갱신)", mutate_handedit, "self_sha256 불일치"),
        ("M5 배정표 손질", mutate_alloc, "allocation"),
        ("M6 균형 표 손질", mutate_balance, "allocation.balance"),
        ("M7 스키마 버전 올림", mutate_schema, "schemas"),
    ]
    print("| 변이 | 기대 탐지 | 판정 |")
    print("|---|---|---|")
    failed = 0
    with tempfile.TemporaryDirectory() as td:
        for name, fn, expect in cases:
            p = Path(td) / "m.json"
            p.write_text(json.dumps(fn(copy.deepcopy(base)), ensure_ascii=False), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--check", "--draft",
                 "--manifest", str(p)],
                capture_output=True, text=True,
                env={"PYTHONUTF8": "1", "PATH": "/usr/bin:/bin"})
            hit = proc.returncode == 2 and expect in proc.stdout
            if not hit:
                failed += 1
            print(f"| {name} | `{expect}` | {'✓ red' if hit else '✗ **놓침**'} |")

    # M8 — 레인 AU 발견 2 의 재현. 빈 값·잘못된 타입·빈 목록·대피 안 된 메모리를 넣었을 때
    # 부속서가 `measured` 로 통과하면 안 된다. **레인이 실제로 통과시켰던 입력**을 그대로 쓴다.
    degenerate = measure_annex({
        "runtime": {"claude_model_id": "", "codex_model_id": None, "permission_mode": {},
                    "thinking": 0, "codex_reasoning_effort": [], "allowed_tools": ""},
        "orders": {o: {"target_repo": "/tmp", "artifacts": [],
                       "baseline_tests": "0 green / 0 red",
                       "stub_induced_red": "none",
                       "reset_anchor": {"baseline_commit": "x", "reset_command": "x",
                                        "post_reset_tree_sha256": "0" * 64,
                                        "post_reset_untracked": ["ignored-junk"],
                                        "post_reset_ignored": ["__pycache__"],
                                        "demonstrated_at": "now"}} for o in ORDERS},
    })
    m8 = degenerate.get("status") != "measured"
    if not m8:
        failed += 1
    print(f"| M8 빈 값·잘못된 타입 부속서 | `status != measured` | "
          f"{'✓ red' if m8 else '✗ **놓침**'} |")

    rc = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--check", "--draft"],
        capture_output=True, text=True,
        env={"PYTHONUTF8": "1", "PATH": "/usr/bin:/bin"}).returncode
    ok = rc == 0
    if not ok:
        failed += 1
    print(f"| M0 무변이(대조) | exit 0 | {'✓ green' if ok else '✗ **위양성**'} |")
    print(f"\n변이 {len(cases) + 2} · 실패 {failed}")   # cases + M8(부속서) + M0(대조)
    return 2 if failed else 0


DESIGN_DOC: Path = ROOT / "workspace" / "design" / "2026-08-20-ontology-t2-0b-design.md"
FACTS_BEGIN: str = "<!-- MANIFEST-FACTS (기계 렌더 — 손으로 고치지 않는다) -->"
FACTS_END: str = "<!-- /MANIFEST-FACTS -->"


def sync_design_facts(m: "dict") -> bool:
    """판단표의 수치를 **기계에서 렌더**한다 — 손기입을 없앤다(레인 AU 발견 10).

    실측으로 판단표가 이미 기계 정본과 어긋나 있었다(«101파일·7그룹» ↔ 실물 190·9 · «다섯
    변이» ↔ 실물 8). 문서를 고쳐도 봉인이 드리프트를 안 내면 그 문서는 정본이 아니라 소문이다.
    이제 판단표는 `protocol` 그룹으로 동결되고, 이 블록은 `--write` 마다 다시 렌더된다.
    """
    if not DESIGN_DOC.is_file():
        return False
    # **자기 참조 값을 렌더하지 않는다.** 이 문서가 `protocol` 그룹 안에 있으므로, tree hash 나
    # `self_sha256` 을 여기 적으면 렌더 → 해시 변경 → 다시 렌더 로 수렴하지 않는다.
    # 파일 **수**는 문서 내용이 바뀌어도 안 변하므로 안전하다. 해시의 정본은 manifest 다.
    rows = ["| 그룹 | 파일 |", "|---|---|"]
    for g in sorted(m["groups"]):
        rows.append(f"| `{g}` | {m['groups'][g]['n_files']} |")
    total = sum(v["n_files"] for v in m["groups"].values())
    schemas_flat = sorted({s for v in m["schemas"].values() for s in v})
    body = "\n".join([
        FACTS_BEGIN, "",
        f"**봉인 실측**(기계 렌더 — 해시 정본은 `T2-0b-manifest.json`): "
        f"그룹 **{len(m['groups'])}** · 파일 **{total}** · 배정 {m['allocation']['n_runs']}런",
        "", *rows, "",
        f"**스키마**: {' · '.join('`' + s + '`' for s in schemas_flat)}",
        "",
        f"**미러**: {m['mirror_parity']['n_files']}파일 "
        f"{'동일' if m['mirror_parity']['identical'] else '**파손**'} · "
        f"**설치본**: {m['plugin_versions']} · "
        f"cache_parity claude={m['cache_parity'].get('claude', {}).get('status')} "
        f"codex={m['cache_parity'].get('codex', {}).get('status')}",
        "", FACTS_END,
    ])
    text = DESIGN_DOC.read_text(encoding="utf-8")
    if FACTS_BEGIN in text and FACTS_END in text:
        head, rest = text.split(FACTS_BEGIN, 1)
        _, tail = rest.split(FACTS_END, 1)
        new = head + body + tail
    else:
        new = text.rstrip("\n") + "\n\n" + body + "\n"
    if new != text:
        DESIGN_DOC.write_text(new, encoding="utf-8")
        return True
    return False


def runready_receipt(out: Path, claude_home: Path, codex_home: Path) -> int:
    """실런 진입 영수증 — 엄격 대조가 green 일 때만 발행된다.

    왜 필요한가(레인 AU 발견 5): `verify-runready` 는 실행자가 자발적으로 부르는 진단 명령일
    뿐 hard gate 가 아니었다. 실런 세션은 사용자가 `claude`/`codex` 를 직접 기동하므로
    (프로토콜 §2 ④ — 하네스 세션의 재귀 기동은 권한 분류기에 차단된다), 기동 시점에 기계를
    끼워 넣을 자리가 없다. 그래서 **채점 경계**에 건다: 영수증이 없거나 `self_sha256` 이
    다르면 `ab_score` 가 채점을 거절한다. 기동을 못 막으면 **점수를 못 받게** 한다.
    """
    rc = check(claude_home, codex_home, draft_ok=False)
    if rc != 0:
        print("[runready] 엄격 대조 red — 영수증을 발행하지 않는다", file=sys.stderr)
        return rc
    sealed = json.loads(MANIFEST.read_text(encoding="utf-8"))
    row = {"schema": "runready-receipt/0",
           "manifest_self_sha256": sealed.get("self_sha256"),
           "sealed_commit": sealed.get("sealed_commit"),
           "allocation_seed": ALLOCATION_SEED,
           "repo_head": git_head()}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(row, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"[runready] 영수증 발행 {out}")
    return 0


def print_allocation() -> None:
    rows = allocation()
    print(f"seed = {ALLOCATION_SEED}\n")
    print("| run | block | 발주 | 레인 | 위치 | 암 | 맹검 라벨 | experiment_run_id |")
    print("|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['run_id']} | {r['block']} | {r['order']} | {r['lane']} | {r['position']} | "
              f"{r['arm']} | {r['blind_label']} | `{r['experiment_run_id']}` |")
    bal = allocation_balance()
    print(f"\n균형 재계산: 암별 {bal['by_arm']} · 레인×암 {bal['by_lane_arm']}")
    print(f"위치×암 {bal['by_position_arm']}")


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description="T2-0b 구현 동결 게이트 manifest")
    ap.add_argument("--emit", action="store_true", help="실측 manifest 를 stdout 으로")
    ap.add_argument("--write", action="store_true", help="봉인 파일에 기록")
    ap.add_argument("--check", action="store_true", help="봉인본 ↔ 실측 대조")
    ap.add_argument("--draft", action="store_true", help="PENDING 허용(봉인 전에만)")
    ap.add_argument("--seal", action="store_true", help="status 를 sealed 로 올린다")
    ap.add_argument("--allocation", action="store_true", help="배정표만 인쇄")
    ap.add_argument("--measure-annex", metavar="TARGETS_JSON",
                    help="타깃 접근이 있을 때 외부 부속서를 실측한다(--write 와 함께 쓰면 병합)")
    ap.add_argument("--tree-hash", metavar="REPO",
                    help="그 저장소의 추적 파일 트리 해시 + 미추적 목록(O-5 리셋 동등성)")
    ap.add_argument("--self-test", action="store_true", help="변이로 탐지력을 확인한다")
    ap.add_argument("--runready-receipt", metavar="PATH",
                    help="엄격 대조가 green 이면 실런 진입 영수증을 발행한다(ab_score 가 요구)")
    ap.add_argument("--manifest", help="대조할 봉인본 경로(자기 시험용 — 기본은 정본)")
    ap.add_argument("--claude-home", default=str(Path.home() / ".claude"))
    ap.add_argument("--codex-home", default=str(Path.home() / ".codex"))
    args = ap.parse_args(argv)

    ch, co = Path(args.claude_home), Path(args.codex_home)

    if args.allocation:
        print_allocation()
        return 0
    if args.tree_hash:
        repo = Path(args.tree_hash).expanduser()
        if not repo.is_dir():
            print(f"[manifest] 경로 부재: {repo}", file=sys.stderr)
            return 1
        state = worktree_state(repo)
        print(json.dumps({"repo": str(repo), "head": git_head(repo),
                          "tracked_tree_sha256": tracked_tree_hash(repo),
                          **state}, ensure_ascii=False, indent=2))
        # 클린룸이 아니면 **exit 로 알린다** — 사람이 JSON 을 눈으로 읽고 판단하게 두지 않는다.
        return 0 if state["clean"] else 2
    if args.measure_annex:
        targets = json.loads(Path(args.measure_annex).expanduser().read_text(encoding="utf-8"))
        annex = measure_annex(targets)
        if args.write:
            if not MANIFEST.is_file():
                print("[manifest] 봉인본 부재 — 먼저 `--write` 로 저작하라", file=sys.stderr)
                return 1
            m = json.loads(MANIFEST.read_text(encoding="utf-8"))
            m["external_annex"] = annex
            m.pop("self_sha256", None)
            m["self_sha256"] = sha256_bytes(canonical(m).encode("utf-8"))
            MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                                encoding="utf-8")
            print(f"[manifest] 부속서 병합 · status={annex['status']}")
        else:
            print(json.dumps(annex, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.self_test:
        return self_test()
    if args.runready_receipt:
        return runready_receipt(Path(args.runready_receipt).expanduser(), ch, co)
    if args.check:
        return check(ch, co, draft_ok=args.draft,
                     manifest=Path(args.manifest) if args.manifest else None)
    if args.emit or args.write or args.seal:
        prior = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else None
        # 2패스: 판단표의 기계 렌더 블록을 먼저 갱신하고 **그 뒤에** 해시를 잰다.
        # 판단표가 `protocol` 그룹 안에 있으므로 순서를 뒤집으면 쓰자마자 드리프트가 난다.
        m = build(ch, co, prior)
        if (args.write or args.seal) and sync_design_facts(m):
            m = build(ch, co, prior)
            sync_design_facts(m)
            m = build(ch, co, prior)
        if args.seal:
            m["status"] = "sealed"
            m.pop("self_sha256")
            m["self_sha256"] = sha256_bytes(canonical(m).encode("utf-8"))
        text = json.dumps(m, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.write or args.seal:
            MANIFEST.parent.mkdir(parents=True, exist_ok=True)
            MANIFEST.write_text(text, encoding="utf-8")
            print(f"[manifest] 기록 {MANIFEST.relative_to(ROOT)} · status={m['status']}")
        else:
            sys.stdout.write(text)
        return 0
    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
