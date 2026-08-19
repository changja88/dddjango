"""재생성 루프 시제품 — 그래프 미경유 (T0 B3, 블루프린트 §6 B암 부품).

입력: findings/0 JSON lines(검사기가 DJR_FINDINGS_JSON 채널로 방출한 위반 레코드)
조인: rule-owner-map T0 스냅숏(B1 — 동결 사본)에서 rule «#N» → 담당(ⓒ 검사기·ⓓ 에이전트)
조립: «위반된 제약+핵심 맥락만» 주입 프롬프트 — 재료는 **번호+검사기 산출 발췌**(레코드의
      rule·file·message)뿐이다. 규범 본문 정본(final.md 등) 발췌는 동결 E8이 금지한다.
      owner-map 유래 값(담당 검사기·에이전트)은 **조인·재검사 라우팅 내부 전용**이며 주입
      문자열에 넣지 않는다(T2 적대 리뷰 L-1 정정 — E8 «검사기 산출 발췌» 한정의 회복.
      필드 집합은 --self-test 골든으로 고정).
선행 계약 검사기 레코드(rule=null+contract_ref)는 조인 공백으로 별도 보고한다(조인은
check-domain-model 류 «#N» 레코드에서만 성립 — T0 계획 §3 B3).

기본은 dry-run: 조립된 프롬프트를 출력하고 끝난다(재생성 호출·자동화 배선은 T2 몫).
python3.9 호환 · 표준 라이브러리만.

사용: python3 workspace/tools/regen_loop_prototype.py --records <jsonl>
        [--filter-file 부분문자열] [--severity violation] [--out 경로]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = REPO_ROOT / "workspace" / "eval" / "ab" / "T0-rule-owner-map-snapshot.md"

ROW = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")


def load_snapshot(path: Path) -> "dict[str, dict]":
    """스냅숏 markdown 표 → {"#N": {판정, 검사기, 에이전트}}."""
    owners: "dict[str, dict]" = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if not m:
            continue
        num, verdict, checker, agent = m.groups()
        owners["#" + num] = {
            "판정": verdict,
            "검사기": checker if checker != "—" else None,
            "에이전트": agent if agent != "—" else None,
        }
    return owners


def load_records(path: Path) -> "list[dict]":
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def assemble_prompt(joined: "list[tuple[dict, dict]]") -> str:
    lines = [
        "다음은 결정적 검사기가 잡은 규칙 위반 목록이다. 각 항목의 검사기 산출 발췌(번호·위치·사유)만이",
        "수정 기준이다 — 규범 본문은 재주입하지 않는다. 위반이 난 파일만 수정하고, 무관한 코드는 건드리지 않는다.",
        "",
    ]
    for rec, _owner in joined:
        # _owner(owner-map 유래)는 조인 성립 확인·재검사 라우팅 전용 — 주입 필드는
        # 검사기 산출 발췌(rule·file·message)로 닫는다(E8 — L-1 정정).
        lines.append(f"- [{rec['rule']}] {rec['file']} — {rec['message']}")
    lines += ["", "수정 후 같은 검사기를 재실행해 위 항목이 0이 되는지 확인한다."]
    return "\n".join(lines)


_SELF_TEST_GOLDEN = (
    "다음은 결정적 검사기가 잡은 규칙 위반 목록이다. 각 항목의 검사기 산출 발췌(번호·위치·사유)만이\n"
    "수정 기준이다 — 규범 본문은 재주입하지 않는다. 위반이 난 파일만 수정하고, 무관한 코드는 건드리지 않는다.\n"
    "\n"
    "- [#302] application/orders/domain_layer/x.py — 판정이 서비스로 새어 나갔다\n"
    "- [#310] application/orders/domain_layer/y.py — 불변식 검사가 어댑터에 있다\n"
    "\n"
    "수정 후 같은 검사기를 재실행해 위 항목이 0이 되는지 확인한다."
)


def self_test() -> int:
    """주입 필드 집합 골든 — owner-map 값이 프롬프트에 새면 red(E8·L-1 회귀 방지)."""
    owner = {"판정": "ast", "검사기": "scripts/check-domain-model.py", "에이전트": None}
    joined = [
        ({"rule": "#302", "file": "application/orders/domain_layer/x.py",
          "message": "판정이 서비스로 새어 나갔다", "checker": "check-domain-model.py"}, owner),
        ({"rule": "#310", "file": "application/orders/domain_layer/y.py",
          "message": "불변식 검사가 어댑터에 있다", "checker": "check-domain-model.py"}, owner),
    ]
    prompt = assemble_prompt(joined)
    if prompt != _SELF_TEST_GOLDEN:
        print("[self-test] 프롬프트가 골든과 다르다 — 주입 필드 집합 변경은 골든 갱신+사유 필수", file=sys.stderr)
        return 2
    for leak in ("담당", owner["검사기"], "check-domain-model.py"):
        if leak in prompt:
            print(f"[self-test] owner-map/검사기명 유출: {leak!r}", file=sys.stderr)
            return 2
    print("[self-test] 주입 필드 골든 일치 · owner-map 유출 0")
    return 0


def main() -> int:
    if sys.argv[1:2] == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser(description="재생성 루프 시제품(그래프 미경유·dry-run)")
    ap.add_argument("--records", required=True)
    ap.add_argument("--snapshot", default=str(SNAPSHOT))
    ap.add_argument("--filter-file", default="", help="file 필드 부분 일치로 범위 한정")
    # severity 봉인(중재 채택 — L-V 미착지 «choices=violation»): 주입 대상은 위반뿐이다.
    # info(ⓓ 후보)는 discipline-reviewer 의 물음 채널이지 재생성 주입 재료가 아니다.
    ap.add_argument("--severity", default="violation", choices=("violation",),
                    help="주입 대상 심각도(violation 고정 — 후보 주입 오용 차단)")
    ap.add_argument("--out", default="", help="프롬프트 저장 경로(생략 시 stdout)")
    args = ap.parse_args()

    owners = load_snapshot(Path(args.snapshot))
    records = load_records(Path(args.records))

    scoped = [
        r
        for r in records
        if r["severity"] == args.severity and (not args.filter_file or args.filter_file in r["file"])
    ]
    joined, join_gap, unknown = [], [], []
    for rec in scoped:
        if rec.get("rule") is None:
            join_gap.append(rec)
        elif rec["rule"] in owners:
            joined.append((rec, owners[rec["rule"]]))
        else:
            unknown.append(rec)

    print(f"[regen-loop] 레코드 {len(records)} → 범위 {len(scoped)} — 조인 {len(joined)} · "
          f"조인 공백(선행 계약) {len(join_gap)} · 스냅숏 밖 {len(unknown)}", file=sys.stderr)
    for rec in join_gap:
        print(f"[regen-loop]   조인 공백: {rec['checker']} contract_ref={rec.get('contract_ref')} "
              f"{rec['file']} — rule=null(rule-owner-map 규칙 0건 · T2 이월: docstring IRI 재저작이 "
              f"선행 계약 7종에서 가리킬 대상 결정)", file=sys.stderr)
    for rec in unknown:
        print(f"[regen-loop]   스냅숏 밖 rule: {rec['rule']} ({rec['checker']})", file=sys.stderr)

    if not joined:
        print("[regen-loop] 조인된 위반 없음 — 프롬프트 미조립", file=sys.stderr)
        return 1

    prompt = assemble_prompt(joined)
    if args.out:
        Path(args.out).write_text(prompt, encoding="utf-8")
        print(f"[regen-loop] 프롬프트 {len(joined)}건 → {args.out}", file=sys.stderr)
    else:
        print(prompt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
