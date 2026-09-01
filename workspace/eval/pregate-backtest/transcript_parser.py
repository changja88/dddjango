#!/usr/bin/env python3
"""맹검 전사본 파서 — transcript-b5392f0.md → PlanFile 목록."""
from __future__ import annotations

import re
from pathlib import Path

from pregate_proto import PlanFile


def _split_top(s: str) -> list[str]:
    out, depth, cur = [], 0, []
    for ch in s:
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur).strip())
    return [x for x in out if x]


_TYPE_OK = re.compile(r"^[A-Za-z_][\w.\[\], |\"']*$")
_NAME = re.compile(r"^[A-Za-z_]\w*$")


def parse_fields(spec: str, enum: bool) -> list[tuple[str, str]]:
    """{...} → [(렌더 종류, 코드 라인)]. 파싱 불가 항목은 name: object."""
    items = _split_top(spec.strip().strip("{}"))
    lines: list[tuple[str, str]] = []
    for it in items:
        m = re.match(r"^([A-Za-z_]\w*)\s*:\s*(.+)$", it)
        a = re.match(r"^([A-Za-z_]\w*)\s*=\s*(.+)$", it)
        if enum and m:
            lines.append(("member", f"{m.group(1)} = {m.group(2).strip()}"))
        elif m:
            name, rest = m.group(1), m.group(2).strip()
            dm = re.match(r"^(.*?)\s*=\s*(.+)$", rest)
            ann, default = (dm.group(1).strip(), dm.group(2).strip()) if dm else (rest, None)
            if not _TYPE_OK.match(ann.replace("(non-empty)", "").strip()):
                ann, default = "object", None
            line = f"{name}: {ann}" + (f" = {default}" if default else "")
            lines.append(("field", line))
        elif a:
            lines.append(("assign", f"{a.group(1)} = {a.group(2).strip()}"))
        else:
            nm = re.match(r"^([A-Za-z_]\w*)", it)
            if nm:
                lines.append(("field", f"{nm.group(1)}: object"))
    return lines


def parse(transcript: Path) -> tuple[list[PlanFile], list[str]]:
    text = transcript.read_text(encoding="utf-8")
    notes: list[str] = []
    files: dict[str, PlanFile] = {}

    # 블록 1 — file-plan
    fence = re.search(r"```paths\n(.*?)```", text, re.S)
    for line in fence.group(1).splitlines():
        m = re.match(r"^(add|update|remove|empty)\t(\S+)\t?", line)
        if m:
            tag, p = m.group(1), m.group(2)
            if p in files and files[p].tag != tag:
                pri = {"add": 3, "remove": 2, "empty": 1, "update": 0}
                notes.append(f"태그 이중 서술: {p} {files[p].tag}↔{tag} → {'add' if pri[tag] < pri[files[p].tag] else tag} 우선")
                if pri[tag] <= pri[files[p].tag]:
                    continue
            files[p] = PlanFile(path=p, tag=tag)

    def resolve(pathish: str) -> str | None:
        p = pathish.lstrip("…/").lstrip("…")
        cands = [k for k in files if k.endswith(p)]
        if len(cands) == 1:
            return cands[0]
        notes.append(f"경로 해소 실패({len(cands)}): {pathish}")
        return None

    # 블록 2 — symbols ([A]/[B]/[C]만 — «파일 미명시»는 부재)
    blk2 = text.split("## 블록 2")[1].split("### 파일 미명시")[0]
    entries = re.split(r"\n- ", blk2)
    for ent in entries[1:]:
        m = re.match(r"`([^`]+?)::([A-Za-z_]\w*)(?:\(([^)]*)\))?`", ent)
        if not m:
            continue
        pathish, sym, base = m.group(1), m.group(2), (m.group(3) or "").strip()
        if "[L3 제거 대상" in ent:
            continue
        rp = resolve(pathish)
        if rp is None or files[rp].tag not in ("add",):
            if rp and files[rp].tag != "add":
                notes.append(f"심볼 스킵(비-add {files[rp].tag}): {rp}::{sym}")
            continue
        fm = re.search(r"(\{.*?\})\s*\n", ent, re.S) or re.search(r"(\{.*\})", ent, re.S)
        fields = parse_fields(fm.group(1), enum=base in ("StrEnum", "IntEnum", "Enum")) if fm else []
        methods: list[dict] = []
        for mm in re.finditer(r"`([a-z_]\w*)\(([^)`]*)\)(?:\s*->\s*([A-Za-z_][\w.\[\], ]*))?`", ent):
            name, params, ret = mm.group(1), mm.group(2).strip(), (mm.group(3) or "").strip()
            if "/" in params or "::" in params:
                continue
            params = re.sub(r"\.\.\.|…", "", params)
            if params and not re.match(r"^[\w:,=\[\]\"' .|()-]*$", params):
                params = ""
            clean = []
            for piece in [p.strip() for p in params.split(",") if p.strip()]:
                pm2 = re.match(r"^([A-Za-z_]\w*)(\s*:\s*[A-Za-z_][\w.\[\], |]*)?", piece)
                if pm2:
                    clean.append(pm2.group(1) + (pm2.group(2) or ": object"))
            methods.append({"name": name, "params": ", ".join(clean),
                            "ret": ret if re.match(r"^[A-Za-z_][\w.\[\], |]*$", ret or "") else ""})
        files[rp].symbols.append({"name": sym, "base": base, "fieldlines": fields, "methods": methods, "kind": "class"})

    # 블록 3 — boundary-imports (구체 경로 행만)
    blk3 = text.split("## 블록 3")[1].split("## 블록 4")[0]
    for row in re.finditer(r"^\| `([^`]+)`[^|]*\| ([^|]+)\|", blk3, re.M):
        consumer_raw, target = row.group(1), row.group(2)
        if "미명시" in target:
            continue
        rp = resolve(consumer_raw)
        if rp is None:
            continue
        if files[rp].tag != "add":
            notes.append(f"import 스킵(비-add): {rp}")
            continue
        tm = re.search(r"`([\w/]+\.py)`", target)
        names = re.findall(r"\(공통 `(\w+)`", target) or re.findall(r"`(\w+)` Protocol", target)
        if tm:
            mod = tm.group(1)[:-3].replace("/", ".")
            stmt = f"from {mod} import {names[0]}" if names else f"import {mod}"
            files[rp].imports.append(stmt)
    # pydantic 행(계약 칸 수준) — s229 문면의 두 파일에 적용
    if "서드파티 `pydantic`" in blk3:
        for suffix in ("contract/response/allowed_evidence.py", "contract/response/cited_answer.py"):
            rp = resolve(suffix)
            if rp:
                files[rp].imports.append("import pydantic")

    # 블록 4 — physical-signals: 전건 부재 → 반영 없음(파일 존재는 file-plan에 있어야)
    blk4 = text.split("## 블록 4")[1].split("## 블록 5")[0]
    for row in re.finditer(r"^\| T\d+ \| ([^|]+) \|", blk4, re.M):
        for pm in re.finditer(r"`([\w/.]+\.py)`", row.group(1)):
            p = pm.group(1)
            if p not in files:
                files[p] = PlanFile(path=p, tag="add")
                notes.append(f"file-plan 밖 테스트 경로 추가(add): {p}")

    # 블록 5 — 5a 소유는 symbols와 중복(s889 [A]에 반영됨). 5b raise 합성은 파일 결합 부기라 fail-closed 미합성.
    notes.append("exception-map 5b raise 합성: 파일 결합이 명명일치 부기뿐이라 미합성(fail-closed)")
    return list(files.values()), notes


if __name__ == "__main__":
    fs, ns = parse(Path(__file__).parent.parent / "transcript-b5392f0.md")
    from collections import Counter
    print(Counter(f.tag for f in fs))
    print("심볼 보유 파일:", sum(1 for f in fs if f.symbols), "/ import 보유:", sum(1 for f in fs if f.imports))
    for n in ns:
        print("NOTE:", n)
