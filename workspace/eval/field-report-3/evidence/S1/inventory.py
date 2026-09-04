#!/usr/bin/env python3
"""S-1 인벤토리 — application/** 전수(테스트 포함)에서 django-stubs 제네릭 기저 상속 클래스를
①맨몸 ②`# type: ignore[type-arg]` 헤더 ③TYPE_CHECKING 별칭 ④직접 subscript 로 분류.

proto_646 의 해소기를 재사용한다. 출력: jsonl(클래스 1행) + 표(stdout · BC별 · 파일별).
사용법: inventory.py --label NAME --jsonl OUT REPO_ROOT
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "proto"))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # evidence 사본: proto_646.py 가 같은 폴더
import proto_646 as p  # noqa: E402

TYPE_ARG_RE = re.compile(r"#\s*type:\s*ignore\[[^\]]*\btype-arg\b[^\]]*\]")
MISC_RE = re.compile(r"#\s*type:\s*ignore\[[^\]]*\bmisc\b[^\]]*\]")


def classify_class(node: ast.ClassDef, b: p.Bindings, lines: list[str], ignores: dict[int, set[str]]):
    paths = dict(p.ADMIN_FORM_PATHS)
    paths.update(p.CBV_PATHS)
    names = p.ADMIN_FORM_NAMES | p.CBV_NAMES
    families = {n: "admin_form" for n in p.ADMIN_FORM_NAMES}
    families.update({n: "cbv" for n in p.CBV_NAMES})
    matches = [m for m in (p.classify_base(x, b, paths, names, families) for x in node.bases) if m]
    canon = [m for m in matches if m.canonical]
    if not canon:
        return None, matches
    hs, he = p.header_range(node, lines)
    hdr: set[str] = set()
    for ln in range(hs, he + 1):
        hdr |= ignores.get(ln, set())
    shapes = {m.shape for m in canon}
    if "type-arg" in hdr:
        cat = "②ignore"
    elif shapes <= {"subscript"}:
        cat = "④direct(TC)" if node.name in b.tc_classes else "④direct"
    elif shapes <= {"alias-subscript", "subscript"} and all(m.alias in b.tc_alias for m in canon if m.alias):
        cat = "③alias"
    elif shapes & {"bare", "alias-bare"}:
        cat = "①bare"
    else:
        cat = "?" + ",".join(sorted(shapes))
    attr_ignore_lines = []
    for st in node.body:
        if isinstance(st, (ast.AnnAssign, ast.Assign)):
            for ln in range(st.lineno, (st.end_lineno or st.lineno) + 1):
                if "type-arg" in ignores.get(ln, set()):
                    attr_ignore_lines.append(ln)
    return {
        "cat": cat, "family": canon[0].family, "bases": [m.canonical for m in canon],
        "shapes": sorted(shapes), "aliases": sorted({m.alias for m in canon if m.alias}),
        "header": [hs, he], "hdr_codes": sorted(hdr), "attr_ignore_lines": attr_ignore_lines,
    }, matches


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--label", required=True)
    ap.add_argument("--jsonl", required=True)
    ap.add_argument("--subdir", default="application")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    base = root / a.subdir
    rows = []
    file_stats = {}
    for f in sorted(base.rglob("*.py")):
        if set(f.parts) & p.SKIP_DIRS or "migrations" in f.parts:
            continue
        rel = f.relative_to(root)
        src = f.read_text(encoding="utf-8")
        try:
            mod = ast.parse(src)
        except SyntaxError:
            continue
        lines = src.splitlines()
        n_type_arg = sum(1 for l in lines if TYPE_ARG_RE.search(l))
        n_misc = sum(1 for l in lines if MISC_RE.search(l))
        if n_type_arg or n_misc:
            file_stats[str(rel)] = {"type_arg_lines": n_type_arg, "misc_lines": n_misc,
                                    "misc_ctx": [l.strip()[:120] for l in lines if MISC_RE.search(l)]}
        ignores = p.ignore_codes_by_line(lines)
        b = p.module_bindings(mod)
        is_test = not p.is_target_file(f)
        for node in ast.walk(mod):
            if not isinstance(node, ast.ClassDef):
                continue
            info, matches = classify_class(node, b, lines, ignores)
            if info is None:
                if matches:
                    rows.append({"label": a.label, "file": str(rel), "bc": p.bc_of(rel), "cls": node.name,
                                 "line": node.lineno, "cat": "lenient-only", "family": None,
                                 "bases": [m.lenient for m in matches], "is_test": is_test,
                                 "header_src": lines[node.lineno - 1].strip()[:140]})
                continue
            rows.append({"label": a.label, "file": str(rel), "bc": p.bc_of(rel), "cls": node.name,
                         "line": node.lineno, "is_test": is_test, **info,
                         "header_src": lines[node.lineno - 1].strip()[:140]})
    with open(a.jsonl, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ── 표 ──
    print(f"## {a.label} — root={root} subdir={a.subdir}")
    for fam in ("admin_form", "cbv"):
        fam_rows = [r for r in rows if r.get("family") == fam]
        print(f"\n### family={fam} 클래스 {len(fam_rows)} (테스트 파일 {sum(1 for r in fam_rows if r['is_test'])})")
        by_bc: dict[str, Counter] = defaultdict(Counter)
        for r in fam_rows:
            by_bc[r["bc"] or "-"][r["cat"]] += 1
        cats = ["①bare", "②ignore", "③alias", "④direct", "④direct(TC)"]
        print("| BC | " + " | ".join(cats) + " | 기타 | 합 |")
        print("|---|" + "---|" * (len(cats) + 2))
        tot = Counter()
        for bc in sorted(by_bc):
            c = by_bc[bc]
            other = sum(v for k, v in c.items() if k not in cats)
            print(f"| {bc} | " + " | ".join(str(c.get(k, 0)) for k in cats) + f" | {other} | {sum(c.values())} |")
            tot.update(c)
        other = sum(v for k, v in tot.items() if k not in cats)
        print(f"| **합** | " + " | ".join(str(tot.get(k, 0)) for k in cats) + f" | {other} | {sum(tot.values())} |")
        # 파일별
        print("\n파일별:")
        by_file: dict[str, Counter] = defaultdict(Counter)
        for r in fam_rows:
            by_file[r["file"]][r["cat"]] += 1
        for fpath in sorted(by_file):
            c = by_file[fpath]
            print(f"- {fpath}: " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
        attr_lines = [(r["file"], ln) for r in fam_rows for ln in r.get("attr_ignore_lines", [])]
        print(f"\n속성 줄 `type: ignore[type-arg]`: {len(attr_lines)} {attr_lines}")
        base_counter = Counter(bn for r in fam_rows for bn in r["bases"])
        print(f"기저별: {dict(base_counter)}")
    lenient = [r for r in rows if r["cat"] == "lenient-only"]
    print(f"\n### lenient-only(attr 이름만 일치 · 정본 경로 아님): {len(lenient)}")
    for r in lenient:
        print(f"- {r['file']}:{r['line']} {r['cls']} bases={r['bases']} :: {r['header_src']}")
    print(f"\n### 파일 전체 `type: ignore[type-arg]` 줄 합: {sum(v['type_arg_lines'] for v in file_stats.values())}")
    for k, v in sorted(file_stats.items()):
        if v["type_arg_lines"]:
            print(f"- {k}: {v['type_arg_lines']}")
    print(f"\n### `type: ignore[misc]` 줄 합: {sum(v['misc_lines'] for v in file_stats.values())}")
    for k, v in sorted(file_stats.items()):
        for ctx in v["misc_ctx"]:
            print(f"- {k}: {ctx}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
