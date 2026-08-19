#!/usr/bin/env python3
"""ISSUED 대장↔rules/ Work 양방향 전수 대조 (T1-5 — stdlib 전용, T0 명시 이월 이행).

검사:
1. 행 형식 `R-NNNN<TAB>YYYY-MM-DD<TAB>경로`(authoring §5) · 시작 R-0001 · 연속 증가(결번·중복 금지)
2. 대장→정본: 각 행의 경로 파일 실재 + 그 파일에 Work IRI(`…djr#R-NNNN>`) 등장
3. 정본→대장: rules/·wiring/ 전 파일에 등장하는 Work IRI 전부가 대장에 등재
   (Expression IRI `R-NNNN@…`는 Work 등장으로 세지 않되, 그 번호도 대장 등재 의무)

정본 파일은 canon/1 결정 직렬형이므로 텍스트 스캔으로 충분하다(게이트가 형식을 강제).
사용: python3 workspace/tools/ontology_issued_check.py [--root ontology] [--self-test]
exit: 0 정합 / 2 위반(fail-closed)
"""

import argparse
import re
import sys
import tempfile
from pathlib import Path

ROW_RE = re.compile(r"^(R-\d{4})\t(\d{4}-\d{2}-\d{2})\t(\S.*)$")
# canon 직렬형의 두 표기(djr 네임스페이스 한정 — L-H #16): 접두 축약 djr:R-NNNN ·
# 전체 IRI <https://numchida.com/ns/djr#R-NNNN[@날짜]>. 리터럴 안 문자열은 계수 밖.
WORK_RE = re.compile(r"(?:djr:|<https://numchida\.com/ns/djr#)(R-\d{4})(?=[^\w@-]|$)", re.MULTILINE)
EXPR_RE = re.compile(r"(?:djr:|<https://numchida\.com/ns/djr#)(R-\d{4})@")
STRING_LITERAL_RE = re.compile(r'"(?:[^"\\]|\\.)*"')


def strip_literals(text: str) -> str:
    """canon 직렬형의 문자열 리터럴 내용을 제거 — 리터럴 안 R-NNNN 오계수 차단(L-H #16)."""
    return STRING_LITERAL_RE.sub('""', text)


def check(root: Path) -> list[str]:
    errors = []
    issued_path = root / "ISSUED"
    rows = []
    if issued_path.is_file():
        for i, line in enumerate(issued_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line:
                continue
            m = ROW_RE.match(line)
            if not m:
                errors.append(f"ISSUED:{i}: 행 형식 위반(TAB 3필드 R-NNNN/날짜/경로): {line!r}")
                continue
            # L-H #17: 날짜 실검증 + 경로는 rules/ 정본 한정(authoring §5 경로 필드 규약)
            import datetime as _dt
            try:
                _dt.date.fromisoformat(m.group(2))
            except ValueError:
                errors.append(f"ISSUED:{i}: 무효 날짜 {m.group(2)}")
            if not m.group(3).startswith("rules/") or not m.group(3).endswith(".ttl"):
                errors.append(f"ISSUED:{i}: 경로 필드가 rules/<문서 키>.ttl 형식이 아님: {m.group(3)}")
            rows.append((i, m.group(1), m.group(3)))

    nums = [int(r[1][2:]) for r in rows]
    for idx, n in enumerate(nums, 1):
        if n != idx:
            errors.append(f"ISSUED: 번호 불연속 — {idx}번째 행이 R-{n:04d}(기대 R-{idx:04d}, 결번·중복 금지)")
            break

    corpus: dict[str, set[str]] = {}
    for sub in ("rules", "wiring"):
        d = root / sub
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.ttl")):
            text = strip_literals(f.read_text(encoding="utf-8"))
            corpus[f"{sub}/{f.name}"] = set(WORK_RE.findall(text)) | set(EXPR_RE.findall(text))

    all_in_files: set[str] = set()
    for s in corpus.values():
        all_in_files |= s
    issued_ids = {r[1] for r in rows}

    for i, rid, path_field in rows:
        target = root / path_field
        if not target.is_file():
            errors.append(f"ISSUED:{i}: {rid} 경로 필드 파일 없음 — {path_field}")
            continue
        if rid not in WORK_RE.findall(strip_literals(target.read_text(encoding="utf-8"))):
            errors.append(f"ISSUED:{i}: {rid} 가 {path_field} 에 Work IRI 로 등장하지 않음")

    for fname, ids in sorted(corpus.items()):
        for rid in sorted(ids - issued_ids):
            errors.append(f"{fname}: {rid} 등장하나 ISSUED 미등재(대장 경유 채번 위반)")
    return errors


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "rules").mkdir()
        (root / "ISSUED").write_text(
            "R-0001\t2026-08-19\trules/x.ttl\n", encoding="utf-8")
        (root / "rules" / "x.ttl").write_text(
            "<https://numchida.com/ns/djr#R-0001> <https://numchida.com/ns/djr#kind> <https://numchida.com/ns/djr#kind-norm> .\n",
            encoding="utf-8")
        assert check(root) == [], check(root)
        (root / "rules" / "x.ttl").write_text(
            "<https://numchida.com/ns/djr#R-0002> <https://numchida.com/ns/djr#kind> <https://numchida.com/ns/djr#kind-norm> .\n",
            encoding="utf-8")
        errs = check(root)
        assert any("미등재" in e for e in errs) and any("등장하지 않음" in e for e in errs), errs
        (root / "ISSUED").write_text("R-0002\t2026-08-19\trules/x.ttl\n", encoding="utf-8")
        assert any("불연속" in e for e in check(root)), check(root)
    print("self-test OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2] / "ontology"))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    errors = check(Path(args.root))
    for e in errors:
        print(f"[issued-check] {e}", file=sys.stderr)
    n = len(errors)
    print(f"[issued-check] {'정합 — 위반 0' if not n else f'위반 {n}건'}")
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
