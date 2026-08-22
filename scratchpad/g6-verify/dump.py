#!/usr/bin/env python3
"""후보표 각 항목의 사본 블록·정본 블록 실물 텍스트를 덤프한다."""
import json
import os
import re
import sys

ROOT = "/Users/hyun/Desktop/dddjango"
SPECS = os.path.join(ROOT, "workspace/eval/t3/specs")

_spec_cache: dict[str, dict] = {}
_file_cache: dict[str, list[str]] = {}


def load_spec(doc_key: str) -> dict:
    if doc_key not in _spec_cache:
        _spec_cache[doc_key] = json.load(open(os.path.join(SPECS, doc_key + ".spec.json")))
    return _spec_cache[doc_key]


BASE_REV = "fe1057c~1"


def load_file(path: str) -> list[str]:
    if path not in _file_cache:
        import subprocess
        out = subprocess.run(
            ["git", "-C", ROOT, "show", f"{BASE_REV}:{path}"],
            capture_output=True, text=True, check=True,
        ).stdout
        _file_cache[path] = out.splitlines()
    return _file_cache[path]


def get_block(doc_key: str, section_key: str, block_no: int):
    spec = load_spec(doc_key)
    for sec in spec["sections"]:
        if sec["section_key"] == section_key:
            blocks = sec["blocks"]
            if block_no < 1 or block_no > len(blocks):
                return None, len(blocks), None
            blk = blocks[block_no - 1]
            lines = load_file(spec["path"])
            lo, hi = blk["lines"]
            text = "\n".join(f"L{n}: {lines[n-1]}" for n in range(lo, min(hi, len(lines)) + 1))
            return blk, len(blocks), text
    return None, -1, None


def main():
    cands = json.load(open(sys.argv[1]))
    sel = None
    if len(sys.argv) > 2:
        sel = set(int(x) for x in sys.argv[2].split(","))
    for i, c in enumerate(cands):
        if sel is not None and i not in sel:
            continue
        print("=" * 100)
        print(f"[{i}] {c['verdict'].upper()}  {c['copy_doc']}/{c['copy_section']}/b{c['copy_block']}  ->  {c['target']}")
        blk, nblocks, text = get_block(c["copy_doc"], c["copy_section"], c["copy_block"])
        if blk is None:
            print(f"  !! COPY BLOCK NOT FOUND (section has {nblocks} blocks)" if nblocks >= 0 else "  !! COPY SECTION NOT FOUND")
        else:
            print(f"  COPY  [{blk['kind']}] lines {blk['lines']}  (section blocks={nblocks})")
            print("  " + text.replace("\n", "\n  "))
        m = re.match(r"^([a-z0-9-]+)/(s[\w.-]+)/b(\d+)$", c["target"])
        if not m:
            print(f"  TARGET (non-doc): {c['target']}")
            continue
        tdoc, tsec, tb = m.group(1), m.group(2), int(m.group(3))
        blk, nblocks, text = get_block(tdoc, tsec, tb)
        if blk is None:
            print(f"  !! TARGET BLOCK NOT FOUND (section has {nblocks} blocks)" if nblocks >= 0 else "  !! TARGET SECTION NOT FOUND")
        else:
            print(f"  TARGET [{blk['kind']}] lines {blk['lines']}  (section blocks={nblocks})")
            t = text if len(text) < 2500 else text[:2500] + "\n  ...[truncated]"
            print("  " + t.replace("\n", "\n  "))


if __name__ == "__main__":
    main()
