"""R8-I2 변이 가드 재실행기 — 본문 증명(#195 도메인 컬렉션 팩토리)의 조건을 하나씩 뗀 변이체가 탐침·fixture 에서 잡히는가.

탐침 트리는 임시 디렉터리에 만든다(`base_tree.json` + make_probes_i2 · make_attacks · make_impl_probes).
판형은 fixture_matrix 와 같다 — 임시 비-git 사본 · DJR_FINDINGS_JSON 제거 · `-B` · cwd = 저장소 루트.

사용: python3 run_mutants.py [--scripts DIR] [--fixtures DIR] [--check | --write]
  --scripts   검사기 디렉터리(기본: 저장소 dddjango/scripts)
  --fixtures  transaction_boundary fixture 디렉터리(기본: 저장소 workspace/eval/fixtures/transaction_boundary)
  --check     결과를 expected.md 와 대조(다르면 exit 1)   --write  expected.md 를 다시 쓴다
exit: 0 = 출력(·대조 일치) · 1 = 대조 불일치 · 변이 문자열 소실 · 검사기 오류(exit 1·stderr)
"""
from __future__ import annotations

import difflib
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
CHECKER = "check-transaction-boundary.py"

# 변이체 = (설명, [(원문, 치환)…]) — 원문은 검사기에 정확히 한 번 있어야 한다.
MUTANTS: dict[str, tuple[str, list[tuple[str, str]]]] = {
    "MUT-P1": ("인자 있는 호출의 본문 증명 요구 탈락(선언만으로 전파)", [
        ("(not (it.args or it.keywords) or collection_factories[it.func.value.id][it.func.attr])", "True")]),
    "MUT-noargproof": ("무인자 호출에도 본문 증명 요구(Ball — 운영 세션이 제외한 판)", [
        ("(not (it.args or it.keywords) or collection_factories[it.func.value.id][it.func.attr])",
         "collection_factories[it.func.value.id][it.func.attr]")]),
    "MUT-anyclscall": ("단일 팩토리 증명 대신 `cls.<아무 메서드>(..)` 를 새 원소로 인정", [
        ("(plain and _own(f)) or (isinstance(f, ast.Attribute) and _own(f.value) and f.attr in scalar)",
         "(plain and _own(f)) or (isinstance(f, ast.Attribute) and _own(f.value))")]),
    "MUT-noreadcheck": ("누적 이름의 읽기 자리 검사 탈락", [
        ("                if not _read_ok(node, seen):\n                    return False", "                pass")]),
    "MUT-noinitcheck": ("누적 이름의 결속 값 검사 탈락", [
        ("        if not all(_coll(v, seen) for v in simple[n]):\n            return False", "        pass")]),
    "MUT-raddany": ("`+` 피연산자 읽기를 상대와 무관하게 허용(리뷰 m-1 되돌림)", [
        ("            other_side = p.right if p.left is node else p.left\n"
         "            return (isinstance(other_side, ast.Name) and other_side.id == node.id) or _coll(other_side, seen)",
         "            return True")]),
    "MUT-nonestedscope": ("중첩 def·class·lambda 안 대입을 바깥 단순 대입으로 합침(리뷰 M-2 되돌림)", [
        ("        elif id(node) in nested and isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):\n"
         "            pass                            # 중첩 범위의 대입 — target 은 아래 «그 밖의 결속» 으로 센다(fail-closed)\n",
         "")]),
    "MUT-noclassscan": ("클래스 본문 결속을 최상위 문장만 셈(리뷰 M-1 되돌림 — `if` 안 def·`__new__` 대입)", [
        ("            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):\n"
         "                stack.extend(ast.iter_child_nodes(n))\n        plain",
         "        plain")]),
    "MUT-noclassimport": ("클래스 본문 import 결속을 세지 않음(리뷰 M-1 되돌림 — import 덮기)", [
        ("                     else [a.asname or a.name.split(\".\")[0] for a in n.names]\n"
         "                     if isinstance(n, (ast.Import, ast.ImportFrom))\n", "")]),
    "MUT-nodeco": ("데코레이터 정확 일치(하나뿐) 탈락", [
        ("            if isinstance(m, ast.FunctionDef) and counts.get(m.name) == 1 and len(m.decorator_list) == 1",
         "            if isinstance(m, ast.FunctionDef) and counts.get(m.name) == 1 and m.decorator_list")]),
    "MUT-nonew": ("`__new__` 가드 탈락", [
        ('        plain = "__new__" not in counts', "        plain = True")]),
    "MUT-nometa": ("metaclass 제외 탈락", [
        ('        if cdef.name in rebound or any(k.arg == "metaclass" for k in cdef.keywords):',
         "        if cdef.name in rebound:")]),
    "MUT-nofirst": ("`cls` 결속 검사 탈락", [
        ("            return arg_counts.get(first) == 1 and first not in simple and first not in aug"
         " and first not in rebinds", "            return True")]),
    "MUT-noyield": ("yield 거부 탈락", [
        ("        if isinstance(node, (ast.Yield, ast.YieldFrom, ast.Await)):\n            return False",
         "        if isinstance(node, ast.Await):\n            return False")]),
    "MUT-nonamevars": ("이름 원소 결속 검사 탈락", [
        ("            return (e.id not in seen and e.id in simple and e.id not in other and e.id not in aug\n"
         "                    and all(_elem(v, seen | {e.id}) for v in simple[e.id]))",
         "            return e.id in simple")]),
    "MUT-nobuiltin": ("내장 가림 검사 탈락", [
        ("    def _builtin(name: str) -> bool:\n        return name not in module_bound and name not in local",
         "    def _builtin(name: str) -> bool:\n        return True")]),
    "MUT-nodup": ("클래스 본문 이름 중복 검사 탈락", [
        ("            if isinstance(m, ast.FunctionDef) and counts.get(m.name) == 1 and len(m.decorator_list) == 1",
         "            if isinstance(m, ast.FunctionDef) and len(m.decorator_list) == 1")]),
    "MUT-nodecoshadow": ("모듈 범위 데코레이터 이름 가림 검사 탈락", [
        ("            and m.decorator_list[0].id not in module_bound and m.decorator_list[0].id not in counts\n",
         "            and m.decorator_list[0].id not in counts\n")]),
    "MUT-noclassdeco": ("클래스 본문 데코레이터 이름 가림 검사 탈락(구현 리뷰 M-2 되돌림)", [
        (" and m.decorator_list[0].id not in counts\n", "\n")]),
    "MUT-reversedany": ("누적 이름의 reversed 인자를 소비 자리와 무관하게 읽기로 인정(재검토 F-1 되돌림)", [
        ("            gp = parents.get(id(p))\n"
         "            return ((isinstance(gp, ast.Call) and isinstance(gp.func, ast.Name) and _builtin(gp.func.id)\n"
         "                     and gp.func.id in (\"tuple\", \"list\", \"set\", \"frozenset\", \"sorted\") and gp.args == [p])\n"
         "                    or (isinstance(gp, (ast.comprehension, ast.For)) and gp.iter is p)\n"
         "                    or (isinstance(gp, ast.Return) and id(gp) not in nested_returns))\n",
         "            return True\n")]),
    "MUT-noglobalbuiltin": ("모듈 함수 본문의 `global` 을 내장 가림으로 세지 않음(재검토 F-2 되돌림)", [
        ("            bound |= {n for g in ast.walk(node) if isinstance(g, ast.Global) for n in g.names}\n", "")]),
    "MUT-sortedany": ("sorted·reversed 의 인자가 새 컬렉션인지 보지 않음", [
        ("not isinstance(e.args[0], ast.Starred) and _coll(e.args[0], seen)\n"
         "                        and all(k.arg in ((\"key\", \"reverse\")",
         "not isinstance(e.args[0], ast.Starred)\n"
         "                        and all(k.arg in ((\"key\", \"reverse\")")]),
}
FIXTURE_GUARDS = ("select_orders", "retouch_orders", "merge_orders", "followup_orders")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# 탐침 RR1(`finally` 안 return)을 compile 할 때 나는 SyntaxWarning 은 의도한 모양이다.
warnings.filterwarnings("ignore", category=SyntaxWarning)


def _targets(tmp: Path, fixtures: Path) -> list[tuple[str, str, str, Path]]:
    base = tmp / "base"
    for rel, text in json.loads((HERE / "base_tree.json").read_text(encoding="utf-8")).items():
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    out: list[tuple[str, str, str, Path]] = []
    (tmp / "trees").mkdir()
    for grp, gen in (("i2", "make_probes_i2"), ("review", "make_attacks"), ("impl", "make_impl_probes")):
        trees = tmp / "trees" / grp
        out += [(grp, n, w, trees / n) for n, w in _load(gen).build(base, trees)]
    for side, want in (("good", "green"), ("bad_rules", "red")):
        dst = tmp / "fx" / side
        shutil.copytree(fixtures / side, dst, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        out.append(("fixture", side, want, dst))
    return out


def _variant(tmp: Path, scripts: Path, label: str, subs: list[tuple[str, str]]) -> Path:
    dst = tmp / "scripts" / label
    shutil.copytree(scripts, dst, ignore=shutil.ignore_patterns("__pycache__"))
    src = (dst / CHECKER).read_text(encoding="utf-8")
    for old, new in subs:
        n = src.count(old)
        if n != 1:
            raise SystemExit(f"[{label}] 변이 원문이 {n}번 나온다(정확히 1번이어야 한다): {old[:80]!r}")
        src = src.replace(old, new, 1)
    (dst / CHECKER).write_text(src, encoding="utf-8")
    return dst


def _run(scripts: Path, target: Path) -> tuple[int, str]:
    env = dict(os.environ)
    env.pop("DJR_FINDINGS_JSON", None)
    env["PYTHONUTF8"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    p = subprocess.run([sys.executable, "-B", str(scripts / CHECKER), str(target)],
                       cwd=str(REPO), capture_output=True, text=True, env=env)
    return p.returncode, p.stdout.replace(str(target), "<T>") + ("\n[stderr]\n" + p.stderr if p.stderr else "")


def _verdict(code: int, want: str) -> str:
    got = {0: "green", 2: "red"}.get(code, f"err{code}")
    if got == want or (want == "fc" and got == "green") or (want == "lim" and got == "red"):
        return "ok"
    return "~" if (want, got) in (("fc", "red"), ("lim", "green")) else "✗"


def report(scripts: Path, fixtures: Path) -> tuple[str, str]:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        targets = _targets(tmp, fixtures)
        variants = {"impl": _variant(tmp, scripts, "impl", [])}
        variants.update({lb: _variant(tmp, scripts, lb, subs) for lb, (_, subs) in MUTANTS.items()})
        jobs = [(lb, t) for lb in variants for t in targets]
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
            res = list(ex.map(lambda j: ((j[0], j[1][1]), _run(variants[j[0]], j[1][3])), jobs))
    raw = dict(res)
    errs = sorted(k for k, (c, o) in raw.items() if c not in (0, 2) or "[stderr]" in o)
    sha = hashlib.sha256((scripts / CHECKER).read_bytes()).hexdigest()[:16]
    lines = ["# R8-I2 변이 가드 — 기대 결과", "",
             f"대상 {len(targets)}(i2 {sum(t[0] == 'i2' for t in targets)} · review "
             f"{sum(t[0] == 'review' for t in targets)} · impl {sum(t[0] == 'impl' for t in targets)} · fixture 2)"
             f" · 변이체 {len(MUTANTS)} · 검사기 오류 {len(errs)} {errs[:3]}", "",
             "## 1. 변이 전 검사기 — 기대(ideal)와 다른 대상", "",
             "`~` = 받아들인 차이(fc = fail-closed red · lim = 문서화 한계 green) · `✗` = 기대와 다름", ""]
    counts: dict[str, int] = {}
    for grp, name, want, _ in targets:
        v = _verdict(raw[("impl", name)][0], want)
        counts[v] = counts.get(v, 0) + 1
        if v != "ok":
            lines.append(f"- {v} [{grp}] {name} (기대 {want} · exit {raw[('impl', name)][0]})")
    lines += ["", f"합계: ok {counts.get('ok', 0)} · ~ {counts.get('~', 0)} · ✗ {counts.get('✗', 0)}", "",
              "## 2. 변이체별 판정이 바뀐 대상", "",
              "| 변이체 | 뗀 조건 | 판정이 바뀐 탐침(→ exit) | bad_rules 발견 줄 수(사라진 참양성) |", "|---|---|---|---|"]
    bad_impl = raw[("impl", "bad_rules")][1]
    n_impl = sum(1 for ln in bad_impl.splitlines() if ln.startswith("  ["))
    uncaught = []
    for lb, (desc, _) in MUTANTS.items():
        flips = [f"{n}→{raw[(lb, n)][0]}" for g, n, _, _ in targets
                 if g != "fixture" and raw[(lb, n)][0] != raw[("impl", n)][0]]
        bad = raw[(lb, "bad_rules")][1]
        n_bad = sum(1 for ln in bad.splitlines() if ln.startswith("  ["))
        gone = [g for g in FIXTURE_GUARDS if f"/{g}/" in bad_impl and f"/{g}/" not in bad]
        good_flip = raw[(lb, "good")][0] != raw[("impl", "good")][0]
        if not flips and not gone and not good_flip:
            uncaught.append(lb)
        lines.append(f"| {lb} | {desc} | {', '.join(flips) or '—'} | {n_bad}/{n_impl}"
                     + (f" ({', '.join(gone)})" if gone else "") + (" · good 판정 바뀜" if good_flip else "") + " |")
    lines += ["", f"잡히지 않은 변이체: {', '.join(uncaught) or '없음'}", ""]
    return "\n".join(lines), sha


def main(argv: list[str]) -> int:
    scripts, fixtures = REPO / "dddjango/scripts", REPO / "workspace/eval/fixtures/transaction_boundary"
    mode = ""
    i = 0
    while i < len(argv):
        if argv[i] in ("--scripts", "--fixtures") and i + 1 < len(argv):
            if argv[i] == "--scripts":
                scripts = Path(argv[i + 1]).resolve()
            else:
                fixtures = Path(argv[i + 1]).resolve()
            i += 2
        elif argv[i] in ("--check", "--write"):
            mode = argv[i]
            i += 1
        else:
            print(__doc__)
            return 1
    text, sha = report(scripts, fixtures)
    print(f"[run_mutants] 검사기 {scripts / CHECKER} (sha256 앞 16 {sha})", file=sys.stderr)
    expected = HERE / "expected.md"
    if mode == "--write":
        expected.write_text(text, encoding="utf-8")
        print(f"[run_mutants] 기록: {expected}", file=sys.stderr)
        return 0
    if mode == "--check":
        want = expected.read_text(encoding="utf-8")
        if want == text:
            print("[run_mutants] expected.md 와 일치", file=sys.stderr)
            return 0
        sys.stdout.writelines(difflib.unified_diff(want.splitlines(True), text.splitlines(True),
                                                   "expected.md", "현재"))
        return 1
    print(text)
    return 1 if "검사기 오류 0 " not in text else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
