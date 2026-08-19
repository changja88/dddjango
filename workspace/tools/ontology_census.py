#!/usr/bin/env python3
"""T1-1 절 유형 센서스 — 기계 절 추출기 (stdlib 전용).

manifest(30문서 목록 정본 TSV)를 입력으로 각 문서를 fence-aware로 절 분할하고
절 목록 TSV를 출력한다. 기계 추출 절이 정본 절 키다(T1 계획 §2 T1-1).

절 분할 규약 (게이트 1 동결 대상):
- 절 경계 = fence 밖·frontmatter 밖의 ATX 헤딩(h1~h6, `#{1,6} ` 시작 라인). setext 헤딩 비인정.
- 문서 선두~첫 헤딩 직전 = «(전문)» 절(첫 라인이 헤딩이면 없음). YAML frontmatter는 (전문)에 포함.
- 코드 펜스 = 들여쓰기 0~3의 백틱/틸드 3+ 라인(CommonMark 근사). 펜스 안 `#`은 헤딩이 아니다.
- 절 스팬 = 헤딩 라인부터 다음 헤딩 직전까지의 원문 바이트 그대로(개행 포함) — 전 절 연결 == 원문(무손실).
- 절 키 = `s<서수 3자리>`(+ 헤딩 앵커 있으면 `-<앵커>`). 서수 = 문서 내 등장 순 1부터.
- 앵커 = 헤딩 텍스트 선두의 번호 토큰(`§` 허용, 숫자 시작, `.`/`-` 연결) — 예: «## 6.2 오류» → 6.2.
- doc_hash = 절 스팬 raw SHA-256 (원장 LEDGER.tsv 기준선).

exit: 0 정상 / 2 검증 실패(행수 재현·무손실 분할·manifest 불일치 — fail-closed).
"""

import argparse
import hashlib
import re
import sys
import unicodedata
from pathlib import Path

FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
ANCHOR_RE = re.compile(r"^§?([0-9]+(?:[.\-][0-9A-Za-z]+)*)[.)]?(?=\s|$)")


def split_lines_with_spans(data: bytes):
    """(1-indexed 라인 텍스트 목록, 라인별 [start,end) 바이트 스팬, 개행 기준 행수) 반환."""
    parts = data.split(b"\n")
    ends_with_nl = data.endswith(b"\n")
    if ends_with_nl:
        parts = parts[:-1]
    lines = []
    spans = []
    off = 0
    for i, p in enumerate(parts):
        nl = 1 if (i < len(parts) - 1 or ends_with_nl) else 0
        spans.append((off, off + len(p) + nl))
        lines.append(p)
        off += len(p) + nl
    return lines, spans, len(parts) if ends_with_nl else len(parts)


def parse_sections(data: bytes):
    """절 목록 [{ordinal, level, anchor, heading, line_start, line_end, span}] 반환."""
    lines, spans, _ = split_lines_with_spans(data)
    n = len(lines)
    if n == 0 or data == b"":
        return []  # 빈 파일 = 0절 (유령 (전문) 절 금지 — L-H #8)
    fm_end = 0
    if lines[0] == b"---":
        for i in range(1, n):
            if lines[i] in (b"---", b"..."):
                fm_end = i + 1  # 1-indexed 종료 라인
                break
        else:
            # 미폐쇄 frontmatter = 구조 훼손 — fail-open 금지 (L-H #7)
            raise ValueError("미폐쇄 frontmatter(첫 줄 '---'의 닫는 구분자 없음)")

    heading_lines = []  # (line_no 1-indexed, level, text)
    fence_char = None
    fence_len = 0
    for i in range(n):
        line_no = i + 1
        if line_no <= fm_end:
            continue
        try:
            text = lines[i].decode("utf-8")
        except UnicodeDecodeError:
            continue
        m = FENCE_RE.match(text)
        if m:
            marker = m.group(1)
            if fence_char is None:
                fence_char, fence_len = marker[0], len(marker)
                continue
            if marker[0] == fence_char and len(marker) >= fence_len and text.strip() == marker:
                fence_char, fence_len = None, 0
                continue
        if fence_char is not None:
            continue
        hm = HEADING_RE.match(text)
        if hm:
            heading_lines.append((line_no, len(hm.group(1)), hm.group(2).rstrip()))

    sections = []
    boundaries = [h[0] for h in heading_lines]
    if not boundaries or boundaries[0] > 1:
        first_end = (boundaries[0] - 1) if boundaries else n
        sections.append({"level": 0, "anchor": "", "heading": "(전문)",
                         "line_start": 1, "line_end": first_end})
    for idx, (line_no, level, text) in enumerate(heading_lines):
        end = boundaries[idx + 1] - 1 if idx + 1 < len(boundaries) else n
        am = ANCHOR_RE.match(text)
        sections.append({"level": level, "anchor": am.group(1) if am else "",
                         "heading": text, "line_start": line_no, "line_end": end})
    for ordinal, s in enumerate(sections, 1):
        s["ordinal"] = ordinal
        key = f"s{ordinal:03d}"
        if s["anchor"]:
            key += f"-{s['anchor']}"
        s["section_key"] = key
        start_off = spans[s["line_start"] - 1][0] if n else 0
        end_off = spans[s["line_end"] - 1][1] if n else 0
        s["span"] = data[start_off:end_off]
    return sections


def hygiene(span: bytes):
    nfc = "Y"
    try:
        t = span.decode("utf-8")
        if unicodedata.normalize("NFC", t) != t:
            nfc = "N"
    except UnicodeDecodeError:
        nfc = "?"
    return nfc, "Y" if b"\t" in span else "N", "Y" if b"\r" in span else "N"


def self_test() -> int:
    doc = (b"---\ntitle: x\n---\npreamble\n# 1. One\nbody\n```py\n# not a heading\n```\n"
           b"## 1.1 Sub\ntail\n")
    secs = parse_sections(doc)
    keys = [s["section_key"] for s in secs]
    assert keys == ["s001", "s002-1", "s003-1.1"], keys
    assert secs[0]["heading"] == "(전문)" and secs[0]["line_end"] == 4
    assert secs[1]["line_start"] == 5 and secs[1]["line_end"] == 9  # 펜스 안 # 무시
    assert b"".join(s["span"] for s in secs) == doc  # 무손실
    no_pre = b"# A\nx\n"
    secs2 = parse_sections(no_pre)
    assert [s["section_key"] for s in secs2] == ["s001"]
    assert b"".join(s["span"] for s in secs2) == no_pre
    print("self-test OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--manifest",
                    default="workspace/design/2026-08-19-ontology-t1-census/corpus-manifest.tsv")
    ap.add_argument("--out",
                    default="workspace/design/2026-08-19-ontology-t1-census/sections.tsv")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    root = Path(args.repo_root)
    manifest_path = root / args.manifest
    rows = []
    with open(manifest_path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        if header != ["doc_key", "path", "expected_lines", "p0_group"]:
            print(f"FAIL: manifest 헤더 불일치: {header}", file=sys.stderr)
            return 2
        for ln in f:
            if not ln.strip():
                continue
            doc_key, path, expected_lines, p0_group = ln.rstrip("\n").split("\t")
            rows.append((doc_key, path, int(expected_lines), p0_group))

    failures = []
    out_lines = ["\t".join(["doc_key", "p0_group", "section_key", "ordinal", "level",
                            "anchor", "heading", "line_start", "line_end", "line_count",
                            "sha256", "nfc", "has_tab", "has_crlf"])]
    total_lines = 0
    total_sections = 0
    per_doc = []
    for doc_key, path, expected, p0_group in rows:
        p = root / path
        if not p.is_file():
            failures.append(f"{doc_key}: 파일 없음 {path}")
            continue
        data = p.read_bytes()
        wc = data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)
        if wc != expected:
            failures.append(f"{doc_key}: 행수 {wc} ≠ manifest {expected}")
        total_lines += wc
        try:
            sections = parse_sections(data)
        except ValueError as exc:
            failures.append(f"{doc_key}: 구조 훼손 — {exc}")
            continue
        if b"".join(s["span"] for s in sections) != data:
            failures.append(f"{doc_key}: 무손실 분할 실패")
        total_sections += len(sections)
        per_doc.append((doc_key, p0_group, len(sections), wc))
        for s in sections:
            nfc, tab, crlf = hygiene(s["span"])
            heading = s["heading"].replace("\t", "\\t")
            out_lines.append("\t".join([
                doc_key, p0_group, s["section_key"], str(s["ordinal"]), str(s["level"]),
                s["anchor"], heading, str(s["line_start"]), str(s["line_end"]),
                str(s["line_end"] - s["line_start"] + 1),
                hashlib.sha256(s["span"]).hexdigest(), nfc, tab, crlf]))

    if total_lines != 17398:
        failures.append(f"코퍼스 총 행수 {total_lines} ≠ 17398 (P0 재현 검증)")

    if failures:
        # fail-closed: 검증 실패 시 동결 산출물(sections.tsv)을 덮어쓰지 않는다 (L-H #5)
        for f_ in failures:
            print(f"FAIL: {f_}", file=sys.stderr)
        print("[census] 검증 실패 — sections.tsv 미기록(동결본 보존)")
        return 2

    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    for doc_key, p0_group, n_sec, wc in per_doc:
        print(f"{p0_group}\t{doc_key}\t{n_sec}절\t{wc}행")
    print(f"합계\t{len(per_doc)}문서\t{total_sections}절\t{total_lines}행")
    print(f"OK → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
