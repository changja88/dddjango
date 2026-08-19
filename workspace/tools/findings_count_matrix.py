#!/usr/bin/env python3
"""findings/0 계수 골든 — 편입 검사기 × red/green fixture × {계수·violation_id 집합}.

T2-1 채점 하네스(D11 — t2-plan v1.1: «27종 전수 arm-blind red/green 계수 골든»)의
레코드 채널 축: 공용 findings 모듈로 편입된 검사기마다 red fixture 에서
{exit · severity별 레코드 수 · rule/sentinel 분포 · violation_id 집합 해시}를,
green fixture 에서 {exit 0 · 레코드 0}을 고정한다. byte 골든(findings_smoke·대표군)과
달리 stdout 문면이 아니라 **계수 의미**를 고정한다 — 개작이 계수를 바꾸면 여기서 red.

violation_id = (rule|sentinel|contract_ref, file, symbol) — 동결 §6 계수 규약의
«Work×대상 파일×심볼» 동일성의 레코드 층 대응(Work 조인 전이므로 rule 표기 사용).
file 은 hermetic 사본 절대 경로를 <FX> 로 정규화해 결정화한다.

EXPECTED 갱신 규율: 개작·픽스처 변경으로 수치가 바뀌면 같은 커밋에서
`--emit-expected` 로 갱신하되 검사기별 사유를 커밋 메시지에 전건 기록한다.

사용: python3 workspace/tools/findings_count_matrix.py [--emit-expected]
exit 0 = 전수 일치 / exit 2 = 불일치 / exit 1 = 재료 결손.
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
S: Path = ROOT / "dddjango" / "scripts"
F: Path = ROOT / "workspace" / "eval" / "fixtures"

sys.path.insert(0, str(S))
sys.path.insert(0, str(ROOT / "workspace" / "tools"))
from checker_registry import REGISTRY, checker_argv  # noqa: E402
from fixture_matrix import AUTO_PAIRS, PLAIN_PAIRS  # noqa: E402

_LANE: "dict[str, tuple[str, str]]" = {"check-layer-skeleton.py": ("skeleton/bad_legacy_flat", "skeleton/good_bc")}
_LANE.update({s: (f"{fx}/bad_rules", f"{fx}/good") for s, fx in PLAIN_PAIRS})
_LANE.update({s: (f"{fx}/bad_rules", f"{fx}/good") for s, fx in AUTO_PAIRS})

# 공용 findings 모듈 편입 완료 로스터 — 개작 진행에 따라 이 목록과 EXPECTED 를 함께 확장.
# 27/27 도달 시 REGISTRY 전체와의 동일성 assert 로 승격한다(T2-1 완료 기준).
CONVERTED: "tuple[str, ...]" = (
    "check-app-container.py",
    "check-broker-contract.py",
    "check-business-vocabulary.py",
    "check-choices-literal-consumption.py",
    "check-common-container.py",
    "check-context-isolation.py",
    "check-db-table.py",
    "check-domain-model.py",
    "check-event-publish.py",
    "check-idempotency-scope-creep.py",
    "check-layer-skeleton.py",
    "check-mechanism-ownership.py",
    "check-missable-entrance.py",
    "check-naming.py",
    "check-ninja-boundary-middleware.py",
    "check-port-adapter-pairing.py",
    "check-public-surface-annotation.py",
    "check-synthetic-infra-exc.py",
    "check-test-config.py",
    "check-transaction-boundary.py",
    "check-transient-overmapping.py",
    "check-usecase-dto-placement.py",
)

# script -> (red_exit, violation수, info수, rule/sentinel 분포 요약, violation_id 집합 sha16)
EXPECTED: "dict[str, tuple[int, int, int, str, str]]" = {
    "check-app-container.py": (2, 1, 0, "contract:선행 규약(표준 트리 전신 — application/ 컨테이너 위치) 소유×1", "31240e8fe5840470"),
    "check-broker-contract.py": (2, 22, 5, "#442×2,#443×2,#444×1,#518×1,#520×3,#521×1,#523×1,#524×2,#525×1,#527×1,#528×1,#529×1,#531×1,#532×1,#533×2,#534×1,#603×5", "11deccf9f90c6592"),
    "check-business-vocabulary.py": (2, 48, 5, "#119×1,#19×1,#294×1,#35×1,#39×1,#393×1,#395×1,#396×1,#398×1,#402×1,#407×2,#408×1,#412×1,#414×1,#415×1,#416×1,#417×1,#420×1,#423×1,#425×1,#426×1,#428×1,#434×1,#448×1,#46×2,#47×1,#52×1,#53×1,#560×1,#561×1,#562×2,#584×1,#585×2,#587×1,#606×2,#607×1,#615×2,#617×1,#618×1,#619×2,#620×1,#621×1,#622×1,#623×1,#624×2", "5d54270ca9386cdf"),
    "check-choices-literal-consumption.py": (2, 3, 0, "contract:선행 계약(2026-07-06 상수 승격) 소유×3", "6253365c1e25da21"),
    "check-common-container.py": (2, 2, 0, "contract:선행 규약(D38 승격/강등 — 루트 framework/ 배치) 소유×2", "7ddb14624648702f"),
    "check-context-isolation.py": (2, 58, 4, "#102×1,#11×1,#110×1,#117×1,#13×1,#14×1,#146×1,#150×1,#151×1,#153×4,#154×1,#155×1,#157×1,#164×2,#166×1,#167×2,#168×1,#170×1,#185×1,#186×1,#2×2,#251×1,#288×1,#291×1,#292×1,#295×1,#312×1,#328×1,#347×1,#361×1,#363×1,#364×2,#431×2,#433×2,#450×2,#453×1,#455×1,#472×1,#473×2,#482×1,#483×2,#484×1,#51×1,#633×1,#634×1,#9×1,#93×1,#94×1,#95×1,#98×1", "1417df159b14cac7"),
    "check-db-table.py": (2, 26, 0, "#318×1,#324×2,#325×1,#326×2,#329×1,#330×2,#331×2,#332×1,#334×1,#335×2,#467×1,#535×1,#536×1,#537×1,#538×2,#630×2,#631×2,#632×1", "5b85011e45235434"),
    "check-domain-model.py": (2, 48, 13, "#17×2,#249×1,#252×1,#253×1,#256×1,#257×2,#258×1,#259×1,#260×2,#261×1,#262×1,#263×1,#264×1,#266×1,#267×1,#268×2,#269×2,#270×1,#272×1,#275×1,#276×1,#289×1,#290×1,#298×1,#299×2,#300×1,#301×4,#302×1,#303×1,#304×1,#305×1,#307×1,#308×1,#310×1,#311×1,#315×1,#459×1,#505×1,#506×1,#542×1,#543×3,#546×1,#547×2,#548×2,#549×1,#550×1,#565×1,#8×1", "085ac733a6aa5b35"),
    "check-event-publish.py": (2, 20, 4, "#271×3,#279×1,#280×2,#502×1,#503×2,#504×1,#507×1,#508×1,#509×1,#564×2,#600×1,#601×1,#627×2,#7×2,#96×3", "06594a2b1253f981"),
    "check-idempotency-scope-creep.py": (2, 1, 0, "contract:선행 계약(architecture-api §13 멱등 스코프) 소유×1", "46b04bd6bcc4b9e5"),
    "check-layer-skeleton.py": (2, 10, 0, "#488×7,#490×2,#81×1", "650a62bfa578c75d"),
    "check-mechanism-ownership.py": (2, 6, 0, "#336×1,#337×1,#338×1,#593×3", "667832904ba25a08"),
    "check-missable-entrance.py": (2, 17, 4, "#172×1,#173×1,#174×2,#175×1,#179×2,#180×1,#181×2,#451×1,#512×2,#514×1,#515×2,#516×2,#517×2,#629×1", "2b604f3883227873"),
    "check-naming.py": (2, 29, 5, "#118×1,#148×1,#169×1,#247×2,#28×2,#30×1,#309×1,#33×1,#34×1,#340×1,#341×1,#342×1,#343×1,#344×2,#345×1,#348×2,#36×3,#382×1,#41×1,#43×1,#44×1,#481×1,#588×1,#589×1,#590×2,#87×1,#97×1", "67c3b8f630ac2347"),
    "check-ninja-boundary-middleware.py": (2, 2, 0, "contract:선행 계약(08-04 API-error) 소유×2", "bcca745399dc645e"),
    "check-port-adapter-pairing.py": (2, 79, 9, "#134×1,#212×2,#214×1,#215×1,#216×2,#218×1,#219×1,#220×2,#225×1,#227×1,#228×2,#231×1,#232×1,#233×2,#234×1,#235×1,#236×1,#238×1,#239×1,#240×1,#241×1,#242×1,#244×1,#245×1,#246×1,#313×1,#351×2,#352×1,#354×1,#356×1,#359×1,#367×1,#368×1,#369×1,#370×2,#373×1,#374×1,#376×1,#457×1,#460×1,#462×2,#464×1,#465×1,#476×2,#477×2,#480×1,#485×5,#545×2,#551×1,#552×4,#553×1,#554×1,#555×1,#556×1,#557×1,#566×1,#573×1,#574×1,#575×1,#576×1,#577×1,#578×1,#579×1,#580×1,#581×1,#582×1,#583×1,#594×2,#64×1", "1714fece63e1a322"),
    "check-public-surface-annotation.py": (2, 10, 2, "#358×2,#456×1,#493×7,#69×2", "fa502276528518f0"),
    "check-synthetic-infra-exc.py": (2, 2, 0, "#129×1,sentinel:합성×1", "639e715f10dcde56"),
    "check-test-config.py": (2, 14, 0, "#384×2,#385×1,#387×1,#388×1,#389×1,#390×2,#391×1,#392×1,#445×1,#446×1,#447×1,sentinel:바인딩×1", "3df1f227a35f1c83"),
    "check-transaction-boundary.py": (2, 13, 2, "#195×1,#197×1,#200×1,#282×1,#283×1,#285×1,#287×2,#355×2,#4×1,#597×1,#599×3", "4a583ba210af44e8"),
    "check-transient-overmapping.py": (2, 1, 0, "contract:선행 계약(08-04 API-error) 소유×1", "e4f6a367f28dd0d1"),
    "check-usecase-dto-placement.py": (2, 35, 5, "#139×1,#140×1,#142×1,#144×2,#182×1,#183×1,#188×2,#189×1,#190×1,#191×1,#192×1,#193×1,#194×1,#196×1,#201×1,#202×2,#205×1,#208×1,#210×1,#211×1,#539×1,#540×1,#541×1,#567×1,#569×3,#570×2,#571×2,#635×3,#67×1,#68×2", "378ab736baa677df"),
}


def _measure_one(script: str, auto: bool, lane_rel: str, want_records: bool):
    with tempfile.TemporaryDirectory() as td:
        fx = Path(td) / "fixture"
        shutil.copytree(F / lane_rel, fx)
        rec_path = Path(td) / "rec.jsonl"
        env = dict(os.environ)
        env["DJR_FINDINGS_JSON"] = str(rec_path)
        proc = subprocess.run(
            checker_argv(sys.executable, script, str(fx), auto),
            capture_output=True, text=True, cwd=str(ROOT), env=env,
        )
        records: "list[dict]" = []
        if rec_path.exists():
            for line in rec_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    obj = json.loads(line)
                    if obj["schema"] != "findings/0":
                        print(f"재료 결손: {script} 미지 schema {obj['schema']}", file=sys.stderr)
                        raise SystemExit(1)
                    obj["file"] = str(obj["file"]).replace(str(fx), "<FX>")
                    records.append(obj)
    return proc.returncode, records


def _summarize(returncode: int, records: "list[dict]"):
    vio = [r for r in records if r["severity"] == "violation"]
    info = [r for r in records if r["severity"] == "info"]
    dist: "dict[str, int]" = {}
    for r in records:
        key = r["rule"] or (f"sentinel:{r['sentinel']}" if r["sentinel"] else f"contract:{r['contract_ref']}")
        dist[key] = dist.get(key, 0) + 1
    dist_s = ",".join(f"{k}×{v}" for k, v in sorted(dist.items()))
    ids = sorted(
        (r["rule"] or r["sentinel"] or r["contract_ref"] or "", r["file"], r["symbol"] or "")
        for r in vio
    )
    ids_sha = hashlib.sha256(json.dumps(ids, ensure_ascii=False).encode()).hexdigest()[:16]
    return returncode, len(vio), len(info), dist_s, ids_sha


def main(argv: "list[str]") -> int:
    emit_expected = "--emit-expected" in argv
    roster = dict(REGISTRY)
    got: "dict[str, tuple]" = {}
    for script in CONVERTED:
        if script not in roster:
            print(f"재료 결손: {script} 가 REGISTRY 에 없음", file=sys.stderr)
            return 1
        red_lane, green_lane = _LANE[script]
        got[script] = _summarize(*_measure_one(script, roster[script], red_lane, True))
        g_exit, g_records = _measure_one(script, roster[script], green_lane, False)
        if g_exit != 0 or g_records:
            print(f"✗ {script} green: exit {g_exit} · 레코드 {len(g_records)} (기대 0·0)")
            return 2

    if emit_expected:
        print('EXPECTED: "dict[str, tuple[int, int, int, str, str]]" = {')
        for script in CONVERTED:
            e, v, i, dist, sha = got[script]
            print(f'    "{script}": ({e}, {v}, {i}, "{dist}", "{sha}"),')
        print("}")
        return 0

    mismatch = 0
    for script in CONVERTED:
        cur, want = got[script], EXPECTED.get(script)
        ok = cur == want
        if not ok:
            mismatch += 1
        e, v, i, dist, sha = cur
        mark = "✓" if ok else f"✗ 기대 {want}"
        print(f"| `{script}` | exit {e} | violation {v} | info {i} | {sha} | {mark} |")
    print(f"편입 {len(CONVERTED)} · 일치 {len(CONVERTED) - mismatch} · 불일치 {mismatch} (green 전수 0레코드 확인)")
    return 0 if mismatch == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
