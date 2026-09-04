#!/usr/bin/env python3
"""교차 fixture 스캔 — 검사기 간 «요구/금지 충돌»의 상류 드리프트 감지기 (메인테이너/빌드타임).

원리: 각 fixture 레인의 good/ 은 그 검사기 기준 «정본 모양»이다. 이것을 27종 «전부»에
돌리면, 검사기 개정이 확립 exemplar 를 새로 거부하는 순간(#210↔#95 부류 — 한 검사기가
요구한 모양을 다른 검사기가 금지)이 census 차이로 드러난다. eval v5 FROZEN 무접촉 —
fixture 는 임시 사본으로만 실행하고(hermetic·fixture_matrix 전례) good/ 내용을 바꾸지 않는다.

판정은 EXPECTED census 와의 «양방향 동등» 대조다(계획 2026-08-14-s2p5-copy-hygiene.md §6 G2·G3):
  - 기대 밖 (레인×검사기) red / 기대한 red 의 소멸 / exit·규칙ID·건수 변화 — 전부 발화(exit 2).
  - 계수 열 분리(T2-1 보강 1단계 — §4-1): 충돌·규칙 계수는 violation(`[#N]`)만,
    info(`[ⓓ#N]`)는 별도 관찰 열(ⓓ 후보 채널 소실 감지) — 둘 다 변화 시 발화하되
    메시지로 구분한다. EXPECTED 재생성 시 `--emit-expected` 가 구 판과의 차이 원인
    분해(«info 분리»뿐인지)를 stderr 로 요약한다.
  - EXPECTED 행의 사유는 닫힌 enum 이다: 가드-red(#74 조용한-무동작 금지가 최소 fixture 에
    정당 발화) · 골격-부재(#486~#490 — fixture 최소성으로 타 칸이 없음) · 최소성(그 외 —
    fixture 가 자기 검사기 슬라이스만 갖춰 이웃 규칙 재료가 없음) · 모순-이월(실재 긴장 —
    사유·이월 기록 필수. 현재 0건).
  - EXPECTED diff 는 릴리즈 보고에 전수 표면화한다 — 무단 갱신은 차분 세탁이다.

한계(정직 기록): 같은 (레인×검사기×규칙ID×건수) 안에서 «의미»만 바뀌는 개정은 못 본다 —
그 층은 fixture red→green 실증과 정독 스윕이 소유한다.

exit: 0=EXPECTED 와 동등 · 2=차이(신규 red·소멸·변화) · 1=재료 결손/usage
사용:
  python3 workspace/tools/checker_cross_matrix.py                  # 대조
  python3 workspace/tools/checker_cross_matrix.py --emit-expected  # 현재 census 를 소스 스플라이스용으로 출력
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
S: Path = ROOT / "dddjango" / "scripts"
F: Path = ROOT / "workspace" / "eval" / "fixtures"

sys.path.insert(0, str(S))
sys.path.insert(0, str(ROOT / "workspace" / "tools"))
from checker_registry import REGISTRY  # noqa: E402
import fixture_matrix as FM  # noqa: E402

# 구 FIND_ID(`\[ⓓ?#(\d+)\]`) 분리(T2-1 보강 1단계 — 포매터 계약 §4-1): 충돌·규칙 계수는
# violation 만 세고, info(ⓓ 후보)는 별도 «관찰 열»로 EXPECTED 에 병기한다(소실 감지용 —
# 개정이 후보 채널을 조용히 죽이면 여기서 드러난다).
VIOLATION_ID = re.compile(r"\[#(\d+)\]")
INFO_ID = re.compile(r"\[ⓓ#(\d+)\]")

CATEGORIES = ("가드-red", "골격-부재", "최소성", "모순-이월")
_SKELETON_IDS = frozenset({486, 487, 488, 489, 490})


def lanes() -> "list[tuple[str, Path, str]]":
    """(레인 이름, good 경로, 자기 검사기)"""
    out = [("skeleton", F / "skeleton" / "good_bc", "check-layer-skeleton.py")]
    for script, fx in FM.PLAIN_PAIRS + FM.AUTO_PAIRS + FM.EXTRA_LANES:
        out.append((fx, F / fx / "good", script))
    return out


def census() -> "dict[tuple[str, str], tuple[int, tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]]":
    """(레인, 검사기) → (exit, ((violation ID, 건수), …), ((info ID, 건수), …)) — 비-0 exit 만."""
    result: "dict[tuple[str, str], tuple[int, tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]]" = {}
    for lane, src, own in lanes():
        if not src.is_dir():
            print(f"재료 결손: {src}", file=sys.stderr)
            sys.exit(1)
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "fixture"
            shutil.copytree(src, tmp)
            # 사용자 환경의 DJR_FINDINGS_JSON 을 상속하면 이 하네스가 사용자의 실제
            # 레코드 파일에 테스트 레코드를 append 한다(T2-1 적대 검증 레인 S 7번 —
            # checker_baseline_matrix 판형). 라인 채널만 세는 도구이므로 sink 를 끊는다.
            env = dict(os.environ)
            env.pop("DJR_FINDINGS_JSON", None)
            for script, auto in REGISTRY:
                cmd = [sys.executable, str(S / script), str(tmp)]
                if auto:
                    cmd += ["--error-profile", "auto"]
                r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, env=env)
                if script == own:
                    if r.returncode != 0:
                        print(f"재료 결손: 자기 검사기 비-0 — {lane} × {script} exit {r.returncode}", file=sys.stderr)
                        sys.exit(1)
                    continue
                if r.returncode == 0:
                    continue
                vio: "dict[int, int]" = {}
                info: "dict[int, int]" = {}
                for m in VIOLATION_ID.finditer(r.stdout):
                    n = int(m.group(1))
                    vio[n] = vio.get(n, 0) + 1
                for m in INFO_ID.finditer(r.stdout):
                    n = int(m.group(1))
                    info[n] = info.get(n, 0) + 1
                result[(lane, script)] = (
                    r.returncode, tuple(sorted(vio.items())), tuple(sorted(info.items()))
                )
    return result


def _merge(vio: "tuple[tuple[int, int], ...]", info: "tuple[tuple[int, int], ...]",
           ) -> "tuple[tuple[int, int], ...]":
    """violation+info 합산 계수 — 구 FIND_ID(혼합 계수)와의 동등 비교용."""
    counts: "dict[int, int]" = {}
    for n, c in (*vio, *info):
        counts[n] = counts.get(n, 0) + c
    return tuple(sorted(counts.items()))


def _category(exit_code: int, vio: "tuple[tuple[int, int], ...]",
              info: "tuple[tuple[int, int], ...]") -> str:
    # 사유 분류는 구 판(혼합 계수) 의미 보존을 위해 violation+info 합산으로 판정한다 —
    # info 분리는 «계수 열»의 개정이지 사유 enum 의 재분류 사유가 아니다.
    ids = _merge(vio, info)
    if not ids:
        return "가드-red"
    if all(n in _SKELETON_IDS for n, _ in ids):
        return "골격-부재"
    return "최소성"


def _emit_diff_summary(cur) -> None:
    """emit-expected 재생성분 ↔ 현행 EXPECTED 의 차이 원인 분해(stderr) — «info 분리»
    개정의 통제 장치: 구 판(3튜플·혼합 계수)과 대조할 땐 violation+info 합산이 구 계수와
    같으면 원인이 info 분리뿐임이 실증된다. 그 외 차이는 전건 표면화한다."""
    same = info_sep = 0
    beyond: "list[str]" = []
    for key in sorted(set(cur) | set(EXPECTED)):
        new = cur.get(key)
        old = EXPECTED.get(key)
        if new is None or old is None:
            beyond.append(f"{key}: {'행 소멸' if new is None else '행 신규'}")
            continue
        code, vio, info = new
        if len(old) == 3:  # 구 판: (exit, 혼합 ids, 사유)
            o_code, o_ids, _cat = old
            if (code, _merge(vio, info)) == (o_code, o_ids):
                if info:
                    info_sep += 1
                else:
                    same += 1
            else:
                beyond.append(f"{key}: exit {o_code}→{code} · 합산 ids {o_ids}→{_merge(vio, info)}")
        else:  # 신 판: (exit, violation ids, info ids, 사유)
            o_code, o_vio, o_info, _cat = old
            if (code, vio, info) == (o_code, o_vio, o_info):
                same += 1
            else:
                beyond.append(f"{key}: ({o_code}, {o_vio}, {o_info}) → ({code}, {vio}, {info})")
    print(f"# emit-expected 차이 요약: 총 {len(set(cur) | set(EXPECTED))}행 — 무변 {same} · "
          f"info 분리(계수 동등·열만 분할) {info_sep} · 그 외 {len(beyond)}", file=sys.stderr)
    for row in beyond:
        print(f"#   그 외 차이: {row}", file=sys.stderr)


def emit_expected() -> None:
    cur = census()
    print("EXPECTED: \"dict[tuple[str, str], tuple[int, tuple[tuple[int, int], ...], "
          "tuple[tuple[int, int], ...], str]]\" = {")
    for (lane, script), (code, vio, info) in sorted(cur.items()):
        cat = _category(code, vio, info)
        print(f"    ({lane!r}, {script!r}): ({code}, {vio!r}, {info!r}, {cat!r}),")
    print("}")
    print(f"# 총 {len(cur)} 행", file=sys.stderr)
    _emit_diff_summary(cur)


def main(argv: "list[str]") -> int:
    if argv == ["--emit-expected"]:
        emit_expected()
        return 0
    if argv:
        print(__doc__, file=sys.stderr)
        return 1
    cur = census()
    findings: "list[str]" = []
    for key, (code, vio, info) in sorted(cur.items()):
        if key not in EXPECTED:
            findings.append(f"신규 교차 red: {key[0]} × {key[1]} exit {code} vio={vio} info={info} — "
                            f"모순 후보(삼분 처분 필요)")
            continue
        e_code, e_vio, e_info, _cat = EXPECTED[key]
        if (code, vio) != (e_code, e_vio):
            findings.append(
                f"교차 red 변화: {key[0]} × {key[1]} exit {e_code}→{code} vio {e_vio}→{vio} — 검사기 개정 영향 확인 필요"
            )
        elif info != e_info:
            # violation 무변·info 만 변화 — 후보 채널 소실/증감 감지(관찰 열의 존재 이유).
            findings.append(
                f"info 관찰 변화(소실 감지): {key[0]} × {key[1]} info {e_info}→{info} — ⓓ 후보 채널 개정 확인 필요"
            )
    for key, (e_code, e_vio, e_info, cat) in sorted(EXPECTED.items()):
        if key not in cur:
            findings.append(f"기대 red 소멸: {key[0]} × {key[1]} ({cat}) — EXPECTED 갱신 필요(--emit-expected)")
    for key, (_c, _v, _i, cat) in EXPECTED.items():
        if cat not in CATEGORIES:
            findings.append(f"EXPECTED 사유 이탈: {key} «{cat}» — 닫힌 enum {CATEGORIES} 만 허용")
    print(f"census {len(cur)} 행 · EXPECTED {len(EXPECTED)} 행")
    if findings:
        for f in findings:
            print(" ", f)
        print(f"차이 {len(findings)}건")
        return 2
    print("차이 0건")
    return 0


# ── EXPECTED census — --emit-expected 산출물을 삼분 처분해 스플라이스한다(무단 갱신 금지·diff 는 릴리즈 보고에 표면화) ──
EXPECTED: "dict[tuple[str, str], tuple[int, tuple[tuple[int, int], ...], tuple[tuple[int, int], ...], str]]" = {
    ('api_error_controller', 'check-context-isolation.py'): (2, ((110, 2),), (), '최소성'),
    ('api_error_controller', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('api_error_controller', 'check-domain-model.py'): (2, ((256, 2), (299, 2)), (), '최소성'),
    ('api_error_controller', 'check-layer-skeleton.py'): (2, ((488, 36),), (), '골격-부재'),
    ('api_error_controller', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('api_error_controller', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('api_error_controller', 'check-public-surface-annotation.py'): (2, ((493, 4),), ((647, 1),), '최소성'),
    ('api_error_controller', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('api_error_controller', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('api_error_controller', 'check-usecase-dto-placement.py'): (2, ((193, 1), (569, 2), (570, 2), (635, 1)), (), '최소성'),
    ('app_container', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('app_container', 'check-domain-model.py'): (2, (), (), '가드-red'),
    ('app_container', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('app_container', 'check-event-publish.py'): (2, (), (), '가드-red'),
    ('app_container', 'check-layer-skeleton.py'): (2, ((488, 12),), (), '골격-부재'),
    ('app_container', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('app_container', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('app_container', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('app_container', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('app_container', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('app_container', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('app_container', 'check-transaction-boundary.py'): (2, (), (), '가드-red'),
    ('app_container', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('broker_contract', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('broker_contract', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('broker_contract', 'check-domain-model.py'): (2, ((299, 1),), ((257, 1),), '최소성'),
    ('broker_contract', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('broker_contract', 'check-event-publish.py'): (2, (), (), '가드-red'),
    ('broker_contract', 'check-layer-skeleton.py'): (2, ((488, 20),), (), '골격-부재'),
    ('broker_contract', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('broker_contract', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('broker_contract', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('broker_contract', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('broker_contract', 'check-port-adapter-pairing.py'): (2, (), (), '가드-red'),
    ('broker_contract', 'check-public-surface-annotation.py'): (2, ((493, 1),), (), '최소성'),
    ('broker_contract', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('broker_contract', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('broker_contract', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('broker_contract', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('business_vocabulary', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('business_vocabulary', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('business_vocabulary', 'check-domain-model.py'): (2, ((299, 1),), ((257, 1),), '최소성'),
    ('business_vocabulary', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('business_vocabulary', 'check-event-publish.py'): (2, (), (), '가드-red'),
    ('business_vocabulary', 'check-layer-skeleton.py'): (2, ((488, 19),), (), '골격-부재'),
    ('business_vocabulary', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('business_vocabulary', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('business_vocabulary', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('business_vocabulary', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('business_vocabulary', 'check-port-adapter-pairing.py'): (2, (), (), '가드-red'),
    ('business_vocabulary', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('business_vocabulary', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('business_vocabulary', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('business_vocabulary', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('choices_literal', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('choices_literal', 'check-domain-model.py'): (2, (), (), '가드-red'),
    ('choices_literal', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('choices_literal', 'check-event-publish.py'): (2, (), (), '가드-red'),
    ('choices_literal', 'check-layer-skeleton.py'): (2, ((488, 19),), (), '골격-부재'),
    ('choices_literal', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('choices_literal', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('choices_literal', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('choices_literal', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('choices_literal', 'check-port-adapter-pairing.py'): (2, ((351, 1), (477, 1), (552, 1)), (), '최소성'),
    ('choices_literal', 'check-public-surface-annotation.py'): (2, ((493, 1),), (), '최소성'),
    ('choices_literal', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('choices_literal', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('choices_literal', 'check-transaction-boundary.py'): (2, (), (), '가드-red'),
    ('choices_literal', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('common_container', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('common_container', 'check-business-vocabulary.py'): (2, ((561, 1),), (), '최소성'),
    ('common_container', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('common_container', 'check-domain-model.py'): (2, ((299, 1),), (), '최소성'),
    ('common_container', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('common_container', 'check-event-publish.py'): (2, (), (), '가드-red'),
    ('common_container', 'check-layer-skeleton.py'): (2, ((488, 17),), (), '골격-부재'),
    ('common_container', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('common_container', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('common_container', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('common_container', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('common_container', 'check-port-adapter-pairing.py'): (2, (), (), '가드-red'),
    ('common_container', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('common_container', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('common_container', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('common_container', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('composition_root', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('composition_root', 'check-layer-skeleton.py'): (2, ((488, 40),), (), '골격-부재'),
    ('composition_root', 'check-port-adapter-pairing.py'): (2, ((225, 1),), (), '최소성'),
    ('composition_root', 'check-public-surface-annotation.py'): (2, ((493, 1),), (), '최소성'),
    ('composition_root', 'check-usecase-dto-placement.py'): (2, ((188, 1), (569, 2), (570, 1)), ((68, 1),), '최소성'),
    ('context_isolation', 'check-business-vocabulary.py'): (2, ((396, 1),), (), '최소성'),
    ('context_isolation', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('context_isolation', 'check-domain-model.py'): (2, ((299, 2),), ((268, 1),), '최소성'),
    ('context_isolation', 'check-error-centralization.py'): (2, ((114, 1),), (), '최소성'),
    ('context_isolation', 'check-layer-skeleton.py'): (2, ((488, 64), (643, 1)), (), '최소성'),
    ('context_isolation', 'check-port-adapter-pairing.py'): (2, ((225, 4),), ((485, 2),), '최소성'),
    ('context_isolation', 'check-public-surface-annotation.py'): (2, ((493, 5),), (), '최소성'),
    ('context_isolation', 'check-usecase-dto-placement.py'): (2, ((569, 2), (570, 1)), (), '최소성'),
    ('db_table', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('db_table', 'check-domain-model.py'): (2, (), (), '가드-red'),
    ('db_table', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('db_table', 'check-event-publish.py'): (2, (), (), '가드-red'),
    ('db_table', 'check-layer-skeleton.py'): (2, ((488, 9),), (), '골격-부재'),
    ('db_table', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('db_table', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('db_table', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('db_table', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('db_table', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('db_table', 'check-transaction-boundary.py'): (2, (), (), '가드-red'),
    ('db_table', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('db_table_choices', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('db_table_choices', 'check-domain-model.py'): (2, (), (), '가드-red'),
    ('db_table_choices', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('db_table_choices', 'check-event-publish.py'): (2, (), (), '가드-red'),
    ('db_table_choices', 'check-layer-skeleton.py'): (2, ((488, 9),), (), '골격-부재'),
    ('db_table_choices', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('db_table_choices', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('db_table_choices', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('db_table_choices', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('db_table_choices', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('db_table_choices', 'check-transaction-boundary.py'): (2, (), (), '가드-red'),
    ('db_table_choices', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('domain_model', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('domain_model', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('domain_model', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('domain_model', 'check-layer-skeleton.py'): (2, ((488, 29),), (), '골격-부재'),
    ('domain_model', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('domain_model', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('domain_model', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('domain_model', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('domain_model', 'check-public-surface-annotation.py'): (2, ((493, 1),), (), '최소성'),
    ('domain_model', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('domain_model', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('domain_model', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('domain_model', 'check-usecase-dto-placement.py'): (2, ((569, 2), (570, 1), (635, 1)), (), '최소성'),
    ('error_centralization', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('error_centralization', 'check-domain-model.py'): (2, (), (), '가드-red'),
    ('error_centralization', 'check-layer-skeleton.py'): (2, ((488, 13),), (), '골격-부재'),
    ('error_centralization', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('error_centralization', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('error_centralization', 'check-port-adapter-pairing.py'): (2, (), (), '가드-red'),
    ('error_centralization', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('error_centralization', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('error_centralization', 'check-transaction-boundary.py'): (2, (), (), '가드-red'),
    ('error_centralization', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('event_publish', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('event_publish', 'check-domain-model.py'): (2, ((299, 2),), ((257, 2),), '최소성'),
    ('event_publish', 'check-layer-skeleton.py'): (2, ((488, 37),), (), '골격-부재'),
    ('event_publish', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('event_publish', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('event_publish', 'check-public-surface-annotation.py'): (2, ((493, 2),), (), '최소성'),
    ('event_publish', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('event_publish', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('event_publish', 'check-usecase-dto-placement.py'): (2, ((569, 2), (570, 1)), (), '최소성'),
    ('event_publish_leaf', 'check-api-error-controller-contract.py'): (2, ((123, 1),), (), '최소성'),
    ('event_publish_leaf', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('event_publish_leaf', 'check-domain-model.py'): (2, ((299, 2),), ((257, 2),), '최소성'),
    ('event_publish_leaf', 'check-error-centralization.py'): (2, ((114, 1),), (), '최소성'),
    ('event_publish_leaf', 'check-layer-skeleton.py'): (2, ((488, 47),), (), '골격-부재'),
    ('event_publish_leaf', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('event_publish_leaf', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('event_publish_leaf', 'check-public-surface-annotation.py'): (2, ((493, 2),), (), '최소성'),
    ('event_publish_leaf', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('event_publish_leaf', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('event_publish_leaf', 'check-usecase-dto-placement.py'): (2, ((569, 2), (570, 1)), ((140, 1),), '최소성'),
    ('idempotency_scope_creep', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('idempotency_scope_creep', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('idempotency_scope_creep', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('idempotency_scope_creep', 'check-layer-skeleton.py'): (2, ((488, 11),), (), '골격-부재'),
    ('idempotency_scope_creep', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('idempotency_scope_creep', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('idempotency_scope_creep', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('idempotency_scope_creep', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('idempotency_scope_creep', 'check-public-surface-annotation.py'): (2, ((493, 2),), (), '최소성'),
    ('idempotency_scope_creep', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('idempotency_scope_creep', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('idempotency_scope_creep', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('idempotency_scope_creep', 'check-usecase-dto-placement.py'): (2, ((569, 2), (570, 1)), (), '최소성'),
    ('mechanism_ownership', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('mechanism_ownership', 'check-domain-model.py'): (2, (), (), '가드-red'),
    ('mechanism_ownership', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('mechanism_ownership', 'check-event-publish.py'): (2, (), (), '가드-red'),
    ('mechanism_ownership', 'check-layer-skeleton.py'): (2, ((429, 1), (488, 14)), (), '최소성'),
    ('mechanism_ownership', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('mechanism_ownership', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('mechanism_ownership', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('mechanism_ownership', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('mechanism_ownership', 'check-transaction-boundary.py'): (2, (), (), '가드-red'),
    ('mechanism_ownership', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('missable_entrance', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('missable_entrance', 'check-domain-model.py'): (2, ((299, 1),), ((257, 1),), '최소성'),
    ('missable_entrance', 'check-layer-skeleton.py'): (2, ((488, 24), (490, 1)), (), '골격-부재'),
    ('missable_entrance', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('missable_entrance', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('missable_entrance', 'check-public-surface-annotation.py'): (2, ((493, 3),), (), '최소성'),
    ('missable_entrance', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('missable_entrance', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('missable_entrance', 'check-usecase-dto-placement.py'): (2, ((569, 4), (570, 2), (635, 2)), (), '최소성'),
    ('naming', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('naming', 'check-domain-model.py'): (2, ((299, 1),), ((257, 1), (268, 1)), '최소성'),
    ('naming', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('naming', 'check-layer-skeleton.py'): (2, ((488, 32),), (), '골격-부재'),
    ('naming', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('naming', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('naming', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('naming', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('naming', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('naming', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('naming', 'check-usecase-dto-placement.py'): (2, ((193, 1), (569, 1), (570, 1)), (), '최소성'),
    ('ninja_boundary_middleware', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('ninja_boundary_middleware', 'check-domain-model.py'): (2, (), (), '가드-red'),
    ('ninja_boundary_middleware', 'check-error-centralization.py'): (2, ((114, 1),), (), '최소성'),
    ('ninja_boundary_middleware', 'check-layer-skeleton.py'): (2, ((429, 1), (488, 16)), (), '최소성'),
    ('ninja_boundary_middleware', 'check-port-adapter-pairing.py'): (2, (), (), '가드-red'),
    ('ninja_boundary_middleware', 'check-public-surface-annotation.py'): (2, ((493, 1),), (), '최소성'),
    ('ninja_boundary_middleware', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('ninja_boundary_middleware', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('ninja_boundary_middleware', 'check-transaction-boundary.py'): (2, (), (), '가드-red'),
    ('ninja_boundary_middleware', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('openapi_error_declaration', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('openapi_error_declaration', 'check-domain-model.py'): (2, (), (), '가드-red'),
    ('openapi_error_declaration', 'check-error-centralization.py'): (2, ((114, 1),), (), '최소성'),
    ('openapi_error_declaration', 'check-layer-skeleton.py'): (2, ((488, 16),), (), '골격-부재'),
    ('openapi_error_declaration', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('openapi_error_declaration', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('openapi_error_declaration', 'check-port-adapter-pairing.py'): (2, (), (), '가드-red'),
    ('openapi_error_declaration', 'check-public-surface-annotation.py'): (2, ((493, 6),), (), '최소성'),
    ('openapi_error_declaration', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('openapi_error_declaration', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('openapi_error_declaration', 'check-transaction-boundary.py'): (2, (), (), '가드-red'),
    ('openapi_error_declaration', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('port_adapter_pairing', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('port_adapter_pairing', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('port_adapter_pairing', 'check-layer-skeleton.py'): (2, ((488, 61),), (), '골격-부재'),
    ('port_adapter_pairing', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('port_adapter_pairing', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('port_adapter_pairing', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('port_adapter_pairing', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('port_adapter_pairing', 'check-public-surface-annotation.py'): (2, ((493, 1),), ((647, 12),), '최소성'),
    ('port_adapter_pairing', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('port_adapter_pairing', 'check-transaction-boundary.py'): (2, ((355, 6),), (), '최소성'),
    ('public_surface', 'check-layer-skeleton.py'): (2, ((488, 26),), (), '골격-부재'),
    ('public_surface', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('public_surface', 'check-port-adapter-pairing.py'): (2, ((359, 4),), (), '최소성'),
    ('public_surface', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('public_surface', 'check-usecase-dto-placement.py'): (2, ((569, 2), (570, 1), (635, 1)), ((68, 1),), '최소성'),
    ('response_schema_bypass', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('response_schema_bypass', 'check-domain-model.py'): (2, (), (), '가드-red'),
    ('response_schema_bypass', 'check-error-centralization.py'): (2, ((114, 1),), (), '최소성'),
    ('response_schema_bypass', 'check-layer-skeleton.py'): (2, ((488, 15),), (), '골격-부재'),
    ('response_schema_bypass', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('response_schema_bypass', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('response_schema_bypass', 'check-port-adapter-pairing.py'): (2, (), (), '가드-red'),
    ('response_schema_bypass', 'check-public-surface-annotation.py'): (2, ((493, 3),), (), '최소성'),
    ('response_schema_bypass', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('response_schema_bypass', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('response_schema_bypass', 'check-transaction-boundary.py'): (2, (), (), '가드-red'),
    ('response_schema_bypass', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('skeleton', 'check-composition-root.py'): (2, ((107, 1),), (), '최소성'),
    ('skeleton', 'check-db-table.py'): (2, ((329, 1),), (), '최소성'),
    ('synthetic_infra_exc', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('synthetic_infra_exc', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('synthetic_infra_exc', 'check-domain-model.py'): (2, (), (), '가드-red'),
    ('synthetic_infra_exc', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('synthetic_infra_exc', 'check-event-publish.py'): (2, (), (), '가드-red'),
    ('synthetic_infra_exc', 'check-layer-skeleton.py'): (2, ((488, 15),), (), '골격-부재'),
    ('synthetic_infra_exc', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('synthetic_infra_exc', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('synthetic_infra_exc', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('synthetic_infra_exc', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('synthetic_infra_exc', 'check-port-adapter-pairing.py'): (2, ((351, 1), (552, 1)), (), '최소성'),
    ('synthetic_infra_exc', 'check-public-surface-annotation.py'): (2, ((493, 2),), (), '최소성'),
    ('synthetic_infra_exc', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('synthetic_infra_exc', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('synthetic_infra_exc', 'check-transaction-boundary.py'): (2, (), (), '가드-red'),
    ('synthetic_infra_exc', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('test_config', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('test_config', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('test_config', 'check-domain-model.py'): (2, ((299, 1),), (), '최소성'),
    ('test_config', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('test_config', 'check-event-publish.py'): (2, (), (), '가드-red'),
    ('test_config', 'check-layer-skeleton.py'): (2, ((488, 22), (490, 1)), (), '골격-부재'),
    ('test_config', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('test_config', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('test_config', 'check-port-adapter-pairing.py'): (2, (), (), '가드-red'),
    ('test_config', 'check-public-surface-annotation.py'): (2, ((493, 1),), (), '최소성'),
    ('test_config', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('test_config', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('test_config', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('test_config_entrance', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('test_config_entrance', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('test_config_entrance', 'check-domain-model.py'): (2, ((299, 1),), (), '최소성'),
    ('test_config_entrance', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('test_config_entrance', 'check-event-publish.py'): (2, (), (), '가드-red'),
    ('test_config_entrance', 'check-layer-skeleton.py'): (2, ((488, 22), (490, 1)), (), '골격-부재'),
    ('test_config_entrance', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('test_config_entrance', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('test_config_entrance', 'check-port-adapter-pairing.py'): (2, (), (), '가드-red'),
    ('test_config_entrance', 'check-public-surface-annotation.py'): (2, ((493, 1),), (), '최소성'),
    ('test_config_entrance', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('test_config_entrance', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('test_config_entrance', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('transaction_boundary', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('transaction_boundary', 'check-db-table.py'): (2, ((318, 1),), (), '최소성'),
    ('transaction_boundary', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('transaction_boundary', 'check-layer-skeleton.py'): (2, ((488, 30), (490, 1)), (), '골격-부재'),
    ('transaction_boundary', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('transaction_boundary', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('transaction_boundary', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('transaction_boundary', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('transaction_boundary', 'check-public-surface-annotation.py'): (2, ((493, 4),), ((647, 2),), '최소성'),
    ('transaction_boundary', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('transaction_boundary', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('transaction_boundary', 'check-usecase-dto-placement.py'): (2, ((569, 8), (570, 4), (635, 1)), (), '최소성'),
    ('transient_overmapping', 'check-api-error-controller-contract.py'): (2, (), (), '가드-red'),
    ('transient_overmapping', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('transient_overmapping', 'check-domain-model.py'): (2, ((299, 1),), (), '최소성'),
    ('transient_overmapping', 'check-error-centralization.py'): (2, (), (), '가드-red'),
    ('transient_overmapping', 'check-event-publish.py'): (2, (), (), '가드-red'),
    ('transient_overmapping', 'check-layer-skeleton.py'): (2, ((488, 14),), (), '골격-부재'),
    ('transient_overmapping', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('transient_overmapping', 'check-missable-entrance.py'): (2, (), (), '가드-red'),
    ('transient_overmapping', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('transient_overmapping', 'check-openapi-error-declaration.py'): (2, (), (), '가드-red'),
    ('transient_overmapping', 'check-port-adapter-pairing.py'): (2, (), (), '가드-red'),
    ('transient_overmapping', 'check-public-surface-annotation.py'): (2, ((493, 3),), (), '최소성'),
    ('transient_overmapping', 'check-response-schema-bypass.py'): (2, (), (), '가드-red'),
    ('transient_overmapping', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('transient_overmapping', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('transient_overmapping', 'check-usecase-dto-placement.py'): (2, (), (), '가드-red'),
    ('usecase_dto', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('usecase_dto', 'check-domain-model.py'): (2, ((299, 1), (543, 1)), (), '최소성'),
    ('usecase_dto', 'check-error-centralization.py'): (2, ((114, 1),), (), '최소성'),
    ('usecase_dto', 'check-layer-skeleton.py'): (2, ((488, 23),), (), '골격-부재'),
    ('usecase_dto', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('usecase_dto', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('usecase_dto', 'check-public-surface-annotation.py'): (2, ((493, 2),), (), '최소성'),
    ('usecase_dto', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('usecase_dto', 'check-test-config.py'): (2, (), (), '가드-red'),
    ('usecase_dto_domain_exception', 'check-db-table.py'): (2, (), (), '가드-red'),
    ('usecase_dto_domain_exception', 'check-domain-model.py'): (2, ((299, 1), (543, 1)), (), '최소성'),
    ('usecase_dto_domain_exception', 'check-error-centralization.py'): (2, ((114, 1),), (), '최소성'),
    ('usecase_dto_domain_exception', 'check-layer-skeleton.py'): (2, ((488, 23),), (), '골격-부재'),
    ('usecase_dto_domain_exception', 'check-mechanism-ownership.py'): (2, (), (), '가드-red'),
    ('usecase_dto_domain_exception', 'check-ninja-boundary-middleware.py'): (2, (), (), '가드-red'),
    ('usecase_dto_domain_exception', 'check-public-surface-annotation.py'): (2, ((493, 2),), (), '최소성'),
    ('usecase_dto_domain_exception', 'check-synthetic-infra-exc.py'): (2, (), (), '가드-red'),
    ('usecase_dto_domain_exception', 'check-test-config.py'): (2, (), (), '가드-red'),
}





if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
