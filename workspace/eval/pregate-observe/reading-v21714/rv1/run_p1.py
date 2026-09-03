"""스크래치 실험 러너 — design_pregate 를 수정하지 않고 monkeypatch 로 P1(update 병합) 변종을 실행한다.
사용: run_p1.py <dedupe|naive> <spec> <repo> --base <sha> --python <bin> --report <path>
"""
import sys, dataclasses
from pathlib import Path
sys.path.insert(0, "/Users/hyun/Desktop/dddjango/dddjango/scripts")
import design_pregate as dp

MODE = sys.argv[1]
argv = sys.argv[2:]

def patched_parse_symbols(rows, plan, errors):
    for raw in rows:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = dp._SYM_LINE_RE.match(line)
        if m is None:
            errors.append(f"symbols 행 파싱 불가: `{line}`"); continue
        path = m.group(1)
        parsed = dp._parse_symbol_rest(m.group(2), errors, path)
        if parsed is None:
            continue
        entry = plan.entries.get(path)
        if entry is None:
            plan.notes.append(f"symbols 고아 행(file-plan 미등재 — 미반영): {path}::{m.group(2).strip()}"); continue
        declared_name = parsed.name.split(".", 1)[0]
        if declared_name not in entry.declared:
            entry.declared.append(declared_name)
        if entry.tag not in ("add", "update"):
            plan.notes.append(f"symbols 미반영(비-add/update `{entry.tag}` 칸): {path}"); continue
        if isinstance(parsed, dp.Method):
            cls_name = parsed.name.split(".", 1)[0]
            owner = next((s for s in entry.symbols if s.kind == "class" and s.name == cls_name), None)
            if owner is None:
                errors.append(f"symbols 메서드 행의 선행 클래스 부재: {path}::{parsed.name}"); continue
            owner.methods.append(dp.Method(name=parsed.name.split(".", 1)[1], params=parsed.params, ret=parsed.ret))
        else:
            entry.symbols.append(parsed)
dp._parse_symbols = patched_parse_symbols

orig_materialize = dp.materialize
def patched_materialize(copy, plan, *, realized=frozenset(), base_short=""):
    report = orig_materialize(copy, plan, realized=realized, base_short=base_short)
    for entry in plan.entries.values():
        if entry.tag != "update" or not entry.symbols:
            continue
        target = copy / entry.path
        if not entry.path.endswith(".py") or not target.is_file():
            report["unsimulated"].append(f"[P1] update 병합 불가(비-py 또는 부재): {entry.path}"); continue
        existing = dp._top_level_names(target)
        if existing is None:
            report["unsimulated"].append(f"[P1] update 병합 불가(기존 파싱 불능): {entry.path}"); continue
        names, _open = existing
        syms = list(entry.symbols) if MODE == "naive" else [s for s in entry.symbols if s.name not in names]
        if not syms:
            report["unsimulated"].append(f"[P1] update 병합 생략(선언 전부 기실존 — dedupe): {entry.path}"); continue
        tmp = dataclasses.replace(entry, symbols=syms)
        stub = dp.render_stub(tmp)
        body = [ln for ln in stub.splitlines() if not ln.startswith('"""pre-gate') and not ln.startswith("from __future__")]
        old = target.read_text(encoding="utf-8")
        merged = old.rstrip("\n") + ("\n\n\n" if old.strip() else "") + "# pre-gate 팬텀 스텁 — update 병합(P1 실험)\n" + "\n".join(body).strip("\n") + "\n"
        try:
            compile(merged, entry.path, "exec")
        except (SyntaxError, ValueError) as exc:
            report["unsimulated"].append(f"[P1] update 병합 불가(병합 후 컴파일 실패 {exc}): {entry.path}"); continue
        target.write_text(merged, encoding="utf-8")
        report["materialized"].append(f"[P1-{MODE}] update 병합 append {[s.name for s in syms]}: {entry.path}")
    return report
dp.materialize = patched_materialize

sys.exit(dp.main(argv))
