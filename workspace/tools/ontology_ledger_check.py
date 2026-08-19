#!/usr/bin/env python3
"""원장(LEDGER.tsv) 부식 방지 검사 (T1-5 — stdlib 전용).

원장 규약: 한 (doc_key, section_key)에 행이 여럿이면 **마지막 행이 유효**(재기준선 append).
검사(owner=prose 미이관 절 한정 — graph 절은 렌더 동기 검증기 소관):
1. 원장 절 키가 현재 기계 분할에 존재하는가(절 구조 변경 검출)
2. 현재 기계 분할의 절이 전부 원장에 등재됐는가(신규 절 무단 등장 검출)
3. 미이관 절의 현재 raw SHA-256 == 유효 기준선 (다르면 exit 2 — 정당 개정이면
   재기준선 append(새 해시+사유+커밋)로 해소·무단 부식이면 되돌림)

사용: python3 workspace/tools/ontology_ledger_check.py [--repo-root .] [--self-test]
exit: 0 정합 / 2 위반(fail-closed)
"""

import argparse
import csv
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ontology_census import parse_sections  # noqa: E402  (stdlib 도구 — 절 분할 규약 단일 출처)

MANIFEST = "workspace/design/2026-08-19-ontology-t1-census/corpus-manifest.tsv"


def load_ledger(path: Path):
    """키별 유효(마지막) 행. (rows 순서 보존 — append-only 원장)"""
    effective = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            effective[(r["doc_key"], r["section_key"])] = r
    return effective


def current_sections(repo: Path):
    cur = {}
    with open(repo / MANIFEST, encoding="utf-8") as f:
        for m in csv.DictReader(f, delimiter="\t"):
            data = (repo / m["path"]).read_bytes()
            for s in parse_sections(data):
                cur[(m["doc_key"], s["section_key"])] = hashlib.sha256(s["span"]).hexdigest()
    return cur


def check(repo: Path) -> list[str]:
    ledger_path = repo / "ontology" / "LEDGER.tsv"
    if not ledger_path.is_file():
        return ["ontology/LEDGER.tsv 부재 — 게이트 1(센서스 동결) 이후 필수"]
    ledger = load_ledger(ledger_path)
    cur = current_sections(repo)
    errors = []
    for key, row in ledger.items():
        if row["owner"] not in ("prose", "graph"):
            # L-H #14: owner 값 공간 폐쇄 — 오타는 부식 검사 우회가 아니라 위반
            errors.append(f"{key[0]}/{key[1]}: 원장 owner 값 위반 {row['owner']!r} (prose|graph 만 허용)")
            continue
        if key not in cur:
            errors.append(f"{key[0]}/{key[1]}: 원장 절이 현재 분할에 없음 — 절 구조 변경(재기준선·원장 개정 필요)")
            continue
        if row["owner"] == "prose" and cur[key] != row["baseline_sha256"]:
            errors.append(f"{key[0]}/{key[1]}: 미이관 절 부식 — 현재 해시 ≠ 기준선(정당 개정이면 재기준선 append)")
    for key in cur:
        if key not in ledger:
            errors.append(f"{key[0]}/{key[1]}: 원장 미등재 신규 절 — 원장 append 필요(다음 미사용 서수 규약 §14)")
    return errors


def self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        (repo / "ontology").mkdir()
        doc_dir = repo / "d"
        doc_dir.mkdir()
        (doc_dir / "x.md").write_text("# 1. A\nbody\n", encoding="utf-8")
        man = repo / MANIFEST
        man.parent.mkdir(parents=True)
        man.write_text("doc_key\tpath\texpected_lines\tp0_group\nx\td/x.md\t2\tE01\n", encoding="utf-8")
        h = hashlib.sha256((doc_dir / "x.md").read_bytes()).hexdigest()
        led = repo / "ontology" / "LEDGER.tsv"
        header = "doc_key\tsection_key\tbaseline_sha256\towner\tmigrated_sha256\tblock_total\tblock_norm\tcommit\tnote\n"
        led.write_text(header + f"x\ts001-1\t{h}\tprose\t-\t-\t-\t-\tt\n", encoding="utf-8")
        assert check(repo) == [], check(repo)
        (doc_dir / "x.md").write_text("# 1. A\nbody CHANGED\n", encoding="utf-8")
        errs = check(repo)
        assert any("부식" in e for e in errs), errs
        h2 = hashlib.sha256((doc_dir / "x.md").read_bytes()).hexdigest()
        with open(led, "a", encoding="utf-8") as f:
            f.write(f"x\ts001-1\t{h2}\tprose\t-\t-\t-\t-\trebaseline:test\n")
        assert check(repo) == [], check(repo)  # append 재기준선으로 해소
    print("self-test OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    errors = check(Path(args.repo_root))
    for e in errors:
        print(f"[ledger-check] {e}", file=sys.stderr)
    print(f"[ledger-check] {'정합 — 위반 0' if not errors else f'위반 {len(errors)}건'}")
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
