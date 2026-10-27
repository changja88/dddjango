"""folder_group 픽스처 러너 — 의미 묶음(2.28.0 · 설계 4 · 5 · 8 · 4.12)의 배치 · 이동 · 창 판정을 행동으로 고정한다.

  folder_group_fixture_run.py [--scripts <dir>] [--py39 <python>] [--require <major.minor>]
  folder_group_fixture_run.py --emit [--scripts <dir>]      # 픽스처 배치 결과를 정해진 글로(불변식 8 대조 재료)
  folder_group_fixture_run.py --mutation-test               # 변이 표를 사본에 하나씩 — 모두 red 여야 green

- 기대는 모두 리터럴이다 — `workspace/eval/fixtures/folder_group/{good,cases/*}/expect.json` 의 자리표 · 까닭 · 줄과
  이 파일의 git 시나리오 표.
- `--py39 <python>`: 그 판으로 `--emit` 을 돌려 지금 판의 `--emit` 과 바이트가 같은지 본다(불변식 8 — 3.9 · 최신 판).
- `--require 3.9`: 이 러너를 돌리는 판이 그 판이 아니면 red(3.9 다리가 다른 판으로 조용히 돌지 않게).
- 검사기 단계(단계 2 · 불변식 2): `good/` 은 온전한 BC 골격이라 등록 검사기 27종이 모두 exit 0 · 줄 0 이다.
  사례마다 검사기 #656 줄 = 도구 `lines` 이고, 도구 자리대로 옮긴 사본에서는 #654 ~ #656 줄이 0 이다.
- 임시 저장소 · 사본은 시스템 임시 폴더에 만든다(플러그인 폴더를 링크하지 않는다 — 파일을 복사한다).
- 종료: 0 green · 1 red · 2 변이 생존.
"""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
FIX: Path = ROOT / "workspace" / "eval" / "fixtures" / "folder_group"
DEFAULT_SCRIPTS: Path = ROOT / "dddjango" / "scripts"
BASE: str = "application/orbit/domain_layer/"
_GIT_ID: "list[str]" = ["-c", "user.email=fixture@dddjango", "-c", "user.name=fixture", "-c", "commit.gpgsign=false",
                        "-c", "init.defaultBranch=main", "-c", "core.autocrlf=false"]


def _load(scripts: Path):
    sys.path.insert(0, str(scripts))
    import folder_group  # noqa: E402
    return folder_group


class Run:
    def __init__(self) -> None:
        self.fails: "list[str]" = []
        self.passed: int = 0

    def eq(self, name: str, got: object, want: object) -> None:
        if got == want:
            self.passed += 1
            return
        self.fails.append(f"{name}: 기대 {_short(want)} · 실제 {_short(got)}")

    def true(self, name: str, ok: bool, detail: str = "") -> None:
        if ok:
            self.passed += 1
        else:
            self.fails.append(f"{name}: {detail or '거짓'}")


def _short(v: object) -> str:
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False, sort_keys=True)[:900]
    return repr(v)[:900]


def _diff_dict(name: str, got: dict, want: dict, run: Run) -> None:
    bad = sorted(k for k in set(got) | set(want) if got.get(k) != want.get(k))
    if not bad:
        run.passed += 1
        return
    for k in bad[:6]:
        run.fails.append(f"{name} `{k}`: 기대 {want.get(k)!r} · 실제 {got.get(k)!r}")
    if len(bad) > 6:
        run.fails.append(f"{name}: 그 밖 {len(bad) - 6}건")


# ── 낱말 목록 ──────────────────────────────────────────────────────────────────

def _literal_set(path: Path, name: str) -> "set[str]":
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return set(ast.literal_eval(node.value))
    raise SystemExit(f"{path.name} 에 {name} 없음")


def check_words(fg, scripts: Path, run: Run) -> None:
    hand = {"AMBIGUOUS": fg.AMBIGUOUS, "KIND": fg.KIND, "VERBS": fg.VERBS, "TECH_EXTRA": fg.TECH_EXTRA,
            "FORBIDDEN_EXTRA": fg.FORBIDDEN_EXTRA, "GENERAL": fg.GENERAL, "MODIFIER": fg.MODIFIER}
    names = sorted(hand)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            both = sorted(hand[a] & hand[b])
            run.true(f"손 목록 겹침 {a}∩{b}", not both, f"겹침 {both}")
    run.eq("AMBIGUOUS 20", len(fg.AMBIGUOUS), 20)
    run.eq("VERBS 30", len(fg.VERBS), 30)
    run.true("order · plan 은 동사 아님", not ({"order", "plan"} & fg.FINAL_VERBS))
    for src, name, attr in (("check-business-vocabulary.py", "CURATED_TECH", "CURATED_TECH"),
                            ("check-naming.py", "ABBREV_DENY", "ABBREV_DENY"),
                            ("check-naming.py", "DEGREE_DENY", "DEGREE_DENY"),
                            ("check-domain-model.py", "KIND_DENY", "KIND_DENY"),
                            ("check-domain-model.py", "KIND_SOFT", "KIND_SOFT")):
        original = _literal_set(scripts / src, name)
        run.eq(f"동기 {name} 복사", set(getattr(fg, attr)), original)
    run.true("CURATED_TECH ⊆ TECH", fg.CURATED_TECH <= fg.TECH)
    run.true("거절 목록 ⊆ FORBIDDEN", (fg.ABBREV_DENY | fg.DEGREE_DENY | fg.KIND_DENY | fg.KIND_SOFT) <= fg.FORBIDDEN)
    run.true("트리 이름 settings · request · event ⊆ FORBIDDEN", {"settings", "request", "event"} <= fg.FORBIDDEN)
    run.true("여러 낱말 트리 이름은 자르지 않음(work · job)", not ({"work", "job", "value", "object"} & fg.FORBIDDEN),
             str(sorted({"work", "job", "value", "object"} & fg.FORBIDDEN)))
    run.true("AMBIGUOUS ∩ (최종 GENERAL ∪ VERBS) = ∅", not (fg.AMBIGUOUS & (fg.FINAL_GENERAL | fg.FINAL_VERBS)),
             str(sorted(fg.AMBIGUOUS & (fg.FINAL_GENERAL | fg.FINAL_VERBS))))
    plural = {w + "s" for w in fg.AMBIGUOUS} - {"settings"}
    other = fg.MODIFIER | fg.FORBIDDEN | fg.TECH | fg.KIND
    run.true("AMBIGUOUS(+복수) 는 다른 종류에 없음", not ((fg.AMBIGUOUS | plural) & other),
             str(sorted((fg.AMBIGUOUS | plural) & other)))
    kinds = {w: fg.word_kind(w, frozenset()) for w in ("code", "message", "order", "plan", "reading", "match", "count",
                                                         "search", "unknown", "shared", "data", "specification",
                                                         "allowed", "new", "needs", "applies", "rag", "settings",
                                                         "work", "twelve", "7", "ganzhi")}
    run.eq("낱말 종류 대표", kinds, {
        "code": "business", "message": "business", "order": "business", "plan": "business", "reading": "business",
        "match": "verb", "count": "verb", "search": "verb", "unknown": "kind", "shared": "forbidden",
        "data": "forbidden", "specification": "forbidden", "allowed": "modifier", "new": "general",
        "needs": "verb", "applies": "verb", "rag": "tech", "settings": "forbidden", "work": "business",
        "twelve": "modifier", "7": "modifier", "ganzhi": "business"})


# ── 픽스처 배치 ────────────────────────────────────────────────────────────────

def _copy_case(src: Path, dest: Path) -> Path:
    shutil.copytree(src, dest, symlinks=False, ignore=shutil.ignore_patterns("expect.json", "__pycache__"))
    return dest


def _cases() -> "list[tuple[str, Path]]":
    out = [("good", FIX / "good")]
    out += [(p.name, p) for p in sorted((FIX / "cases").iterdir()) if p.is_dir()]
    return out


def _strip(p: str) -> str:
    return p[len(BASE):] if p.startswith(BASE) else p


def case_result(fg, root: Path) -> "tuple[dict, dict, list[str], object]":
    files, dirs = fg.scan_tree(root)
    placement = fg.place(files, dirs)
    where = {_strip(p): _strip(fp.target) for p, fp in placement.files.items()}
    why = {_strip(p): fp.reason for p, fp in placement.files.items()}
    lines = [f"[#656] {w}: {m}" for w, m in fg.lines(placement)]
    return where, why, lines, (files, dirs, placement)


def _add_cache(root: Path) -> None:
    """good 의 캐시만 남은 옛 묶음 폴더(실행 때 생기는 것 — 저장소에 두지 않는다)."""
    cache = root / BASE / "shared_value_object" / "removed" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "gone.cpython-39.pyc").write_bytes(b"\0")


def check_cases(fg, run: Run, td: Path) -> None:
    for name, src in _cases():
        expect = json.loads((src / "expect.json").read_text(encoding="utf-8"))
        root = _copy_case(src, td / f"case-{name}")
        if name == "good":
            _add_cache(root)
        where, why, lines, (files, dirs, placement) = case_result(fg, root)
        _diff_dict(f"{name} 자리", where, expect["자리"], run)
        _diff_dict(f"{name} 까닭", why, expect["까닭"], run)
        run.eq(f"{name} 줄", lines, expect["줄"])
        # 불변식 1 · 2 — 옮긴 트리를 다시 재면 모두 제자리 · 줄 0
        files2, dirs2 = fg.placed_tree(files, dirs, placement)
        again = fg.place(files2, dirs2)
        moved = sorted(_strip(p) for p, fp in again.files.items() if fp.target != p)
        run.eq(f"{name} 불변식 1(멱등) 남은 이동", moved, [])
        run.eq(f"{name} 불변식 2(줄 0)", [f"{w}: {m}" for w, m in fg.lines(again)], [])
        run.eq(f"{name} 불변식 1(자리 같음)", sorted(_strip(fp.target) for fp in again.files.values()),
               sorted(expect["자리"].values()))
        if "묶음 식구" in expect:
            for parent, want in expect["묶음 식구"].items():
                d = root / BASE / parent
                got = [_strip(p.relative_to(root).as_posix())
                       for p in fg.group_members(d, "*.py", promotable=parent == "domain_service")]
                run.eq(f"{name} group_members {parent}", got, want)
        for rel, want in sorted(expect.get("알아보기", {}).items()):
            row = 75 if rel.startswith("domain_service") else 73
            run.eq(f"{name} recognize {rel}", fg.recognize(root / BASE / rel, row), want)
    m3p = _copy_case(FIX / "cases" / "m3_promo", td / "recognize-m3p")
    run.eq("recognize 서비스 칸 승격", fg.recognize(m3p / BASE / "domain_service" / "relation", 75), "promotion")


# ── 검사기(불변식 2 · 단계 2) ─────────────────────────────────────────────────────

_RULE_LINE = re.compile(r"^\s*\[ⓓ?#\d+\]")
_GROUP_LINE = re.compile(r"^\[ⓓ?#65[456]\]")


def _checker(scripts: Path, name: str, root: Path, auto: bool = False) -> "tuple[int, list[str], str]":
    """검사기를 사본에 돌려 (exit, 규칙 줄(사본 접두를 뗀 것), stderr 끝)."""
    env: "dict[str, str]" = dict(os.environ)
    env.pop("DJR_FINDINGS_JSON", None)
    argv: "list[str]" = [sys.executable, str(scripts / name), str(root)] + (["--error-profile", "auto"] if auto else [])
    proc = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=str(ROOT))
    prefixes: "list[str]" = sorted({str(root) + "/", str(root.resolve()) + "/"}, key=len, reverse=True)
    out: "list[str]" = []
    for ln in proc.stdout.splitlines():
        if _RULE_LINE.match(ln):
            text: str = ln.strip()
            for pre in prefixes:
                text = text.replace(pre, "")
            out.append(text)
    return proc.returncode, out, (proc.stdout + proc.stderr).strip()[-300:]


def _invariant2(fg, scripts: Path, name: str, src: Path, td: Path) -> "list[tuple[str, object, object]]":
    """사례 하나 — 검사기 #656 = 도구 줄 · 도구 자리대로 옮긴 사본에서 #654 ~ #656 0. (이름, 실제, 기대) 목록."""
    root = _copy_case(src, td / f"inv2-{name}")
    if name == "good":
        _add_cache(root)
    files, dirs = fg.scan_tree(root)
    placement = fg.place(files, dirs)
    want: "list[str]" = sorted(f"[#656] {w}: {m}" for w, m in fg.lines(placement))
    code, before, tail = _checker(scripts, "check-domain-model.py", root)
    out: "list[tuple[str, object, object]]" = [
        (f"{name} 검사기 exit(옮기기 전)", code in (0, 2), True),
        (f"{name} 검사기 #656 줄 = 도구 줄", sorted(ln for ln in before if ln.startswith("[#656]")), want)]
    fg.apply_to_copy(root, fg.placement_moves(placement), fg.placement_drops(placement))
    after: "list[str]" = []
    for checker in ("check-layer-skeleton.py", "check-domain-model.py"):
        code, got, tail = _checker(scripts, checker, root)
        out.append((f"{name} {checker} exit(옮긴 뒤) — {tail[-120:]}", code in (0, 2), True))
        after += [ln for ln in got if _GROUP_LINE.match(ln)]
    out.append((f"{name} 불변식 2(옮긴 사본 · 검사기 #654~#656 0)", after, []))
    return out


def check_checkers(fg, scripts: Path, run: Run, td: Path) -> None:
    sys.path.insert(0, str(scripts))
    import checker_registry  # noqa: E402
    from concurrent.futures import ThreadPoolExecutor
    good = _copy_case(FIX / "good", td / "good-bc")
    _add_cache(good)
    registry = list(checker_registry.REGISTRY)
    run.eq("등록 검사기 27종", len(registry), 27)
    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 2)) as pool:
        got = list(pool.map(lambda item: (item[0], _checker(scripts, item[0], good, item[1])), registry))
        for checker, (code, lines, tail) in got:
            run.eq(f"good 온전한 BC — {checker} (exit · 줄)", (code, lines), (0, []))
        results = list(pool.map(lambda c: _invariant2(fg, scripts, c[0], c[1], td), _cases()))
    for rows in results:
        for label, got_v, want_v in rows:
            run.eq(label, got_v, want_v)


def emit(fg) -> str:
    """불변식 8 — 판마다 같은 글이어야 한다(경로 · 까닭 · 줄 · 멱등 결과)."""
    out: "list[str]" = []
    with tempfile.TemporaryDirectory(prefix="fg-emit-") as tmp:
        for name, src in _cases():
            root = _copy_case(src, Path(tmp) / name)
            where, why, lines, (files, dirs, placement) = case_result(fg, root)
            files2, dirs2 = fg.placed_tree(files, dirs, placement)
            again = fg.place(files2, dirs2)
            out.append(f"== {name}")
            out += [f"자리 {k} -> {where[k]} · {why[k]}" for k in sorted(where)]
            out += lines
            out += [f"다시 {_strip(p)} -> {_strip(fp.target)} · {fp.reason}" for p, fp in sorted(again.files.items())]
    return "\n".join(out) + "\n"


# ── git 시나리오(설계 5 · 8 · 4.12 의 3 · 5 · 7) ─────────────────────────────────────────

D: str = "application/orbit/domain_layer/"
SV: str = D + "shared_value_object/"
DS: str = D + "domain_service/"
PKG: str = "application.orbit.domain_layer.shared_value_object"


def _vo(stem: str, *imports: str) -> str:
    head = "".join(f"{i}\n" for i in imports)
    cls = "".join(x.capitalize() for x in stem.split("_"))
    return f'"""{stem} 값."""\nfrom dataclasses import dataclass\n{head}\n\n@dataclass(frozen=True)\nclass {cls}:\n    value: str\n'


class Repo:
    """임시 git 저장소 — `proj` 가 비어 있지 않으면 git 뿌리 아래 하위 폴더 프로젝트."""

    def __init__(self, base: Path, sub: str = "") -> None:
        self.git_root: Path = base
        self.root: Path = base / sub if sub else base
        self.root.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", *_GIT_ID, "init", "-q"], cwd=self.git_root, check=True, capture_output=True)
        self.git_root.joinpath("README").write_text("뿌리\n", encoding="utf-8")

    def git(self, *args: str, check: bool = True) -> str:
        proc = subprocess.run(["git", *_GIT_ID, *args], cwd=self.root, capture_output=True, text=True)
        if check and proc.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)}: {proc.stderr.strip()}")
        return proc.stdout.strip()

    def write(self, files: "dict[str, str]") -> None:
        for rel, text in files.items():
            f = self.root / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(text, encoding="utf-8")

    def commit(self, msg: str) -> str:
        self.git("add", "-A", str(self.git_root))
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def oid(self, rev: str, rel: str) -> str:
        return self.git("rev-parse", f"{rev}:{self.git('rev-parse', '--show-prefix')}{rel}")


def _folder(repo: Repo, name: str, anchor: str, merges: "list[str]" = (), scope: str = "") -> Path:
    folder = repo.root / ".dddjango" / name
    folder.mkdir(parents=True)
    (folder / "build_anchor").write_text(anchor + "\n", encoding="utf-8")
    (folder / "refactor-scope.md").write_text(f"실행 · G0 승인 {name}\n\n{scope}", encoding="utf-8")
    if merges:
        (folder / "approved-merges.txt").write_text("".join(f"{m} 받음\n" for m in merges), encoding="utf-8")
    return folder


def _tool(scripts: Path, *args: object) -> "tuple[int, list[str]]":
    proc = subprocess.run([sys.executable, str(scripts / "folder_group.py"), *map(str, args)],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout.splitlines() + [f"! {x}" for x in proc.stderr.splitlines()]


def _guard(scripts: Path, repo: Repo, folder: Path, *args: str) -> "tuple[int, str]":
    proc = subprocess.run([sys.executable, str(scripts / "behavior_guard.py"), *args, str(folder), "--repo",
                           str(repo.root)], capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def _starting(lines: "list[str]", head: str) -> "list[str]":
    return [ln for ln in lines if ln.startswith(head)]


def _merge_repo(td: Path, sub: str) -> "tuple[Repo, str, str]":
    """앵커 → 레인 편집 → 상류가 void 셋을 묶고 term_x 를 고침 → 레인이 받음(term_x 충돌 해소)."""
    repo = Repo(td, sub)
    repo.write({SV + "__init__.py": "", SV + "void_a.py": _vo("void_a"), SV + "void_b.py": _vo("void_b"),
                SV + "moon_phase.py": _vo("moon_phase"), SV + "term_x.py": _vo("term_x")})
    anchor = repo.commit("앵커")
    repo.git("checkout", "-q", "-b", "lane")
    repo.write({SV + "moon_phase.py": _vo("moon_phase") + "# 레인\n", SV + "term_x.py": _vo("term_x") + "# 레인\n"})
    repo.commit("레인 편집")
    repo.git("checkout", "-q", "main")
    (repo.root / SV / "void").mkdir()
    repo.git("mv", SV + "void_a.py", SV + "void/void_a.py")
    repo.git("mv", SV + "void_b.py", SV + "void/void_b.py")
    repo.write({SV + "void/__init__.py": "", SV + "void/void_c.py": _vo("void_c"),
                SV + "term_x.py": _vo("term_x") + "# 상류\n"})
    repo.commit("상류 void 묶음")
    repo.git("checkout", "-q", "lane")
    repo.git("merge", "-q", "--no-edit", "main", check=False)
    repo.write({SV + "term_x.py": _vo("term_x") + "# 레인\n# 상류\n"})
    merge = repo.commit("main 받음")
    return repo, anchor, merge


def scen_merge(fg, scripts: Path, run: Run, td: Path) -> None:
    import anchor_diff
    seen: "dict[str, dict]" = {}
    for label, sub in (("뿌리", ""), ("하위 폴더", "proj")):
        repo, anchor, merge = _merge_repo(td / f"merge-{sub or 'root'}", sub)
        folder = _folder(repo, f"m-{sub or 'root'}", anchor, [merge])
        merges = anchor_diff.load_approved_merges(folder / "approved-merges.txt", repo.root, anchor,
                                                  repo.git("rev-parse", "HEAD"))[0]
        t = fg.base_tree(repo.root, anchor, merges)
        seen[label] = t
        run.eq(f"T₀′ 경로({label}) — 병합이 지운 옛 경로 없음", sorted(p for p in t if p.startswith(SV)), [
            SV + "__init__.py", SV + "moon_phase.py", SV + "term_x.py", SV + "void/__init__.py",
            SV + "void/void_a.py", SV + "void/void_b.py", SV + "void/void_c.py"])
        run.eq(f"T₀′ 충돌 해소분은 앵커 판({label})", t.get(SV + "term_x.py"), repo.oid(anchor, SV + "term_x.py"))
        run.eq(f"T₀′ 레인만 바꾼 파일은 앵커 판({label})", t.get(SV + "moon_phase.py"),
               repo.oid(anchor, SV + "moon_phase.py"))
        run.eq(f"T₀′ 상류 유입은 M 판({label})", t.get(SV + "void/void_c.py"), repo.oid(merge, SV + "void/void_c.py"))
        run.eq(f"git 접두({label})", repo.git("rev-parse", "--show-prefix"), f"{sub}/" if sub else "")
        run.eq(f"expected_moves({label})", fg.expected_moves(repo.root, folder),
               {SV + "void_a.py": SV + "void/void_a.py", SV + "void_b.py": SV + "void/void_b.py"})
        rc, out = _tool(scripts, "draft", repo.root, "--bc", "orbit", "--run", folder)
        run.eq(f"승인 병합만 받은 실행의 이 실행 이동 0({label} · 불변식 3)",
               (rc, _starting(out, "이 실행 이동"), _starting(out, "남은 이동")), (0, [], []))
        rc, out = _tool(scripts, "verify", repo.root, "--run", folder)
        run.eq(f"verify --run green · 병합 몫({label})", (rc, _starting(out, "병합 몫"), _starting(out, "red")), (0, [
            f"병합 몫 {SV}void_a.py -> {SV}void/void_a.py", f"병합 몫 {SV}void_b.py -> {SV}void/void_b.py"], []))
    run.eq("하위 폴더 T₀′ 은 뿌리와 같은 경로(접두 밖 README 는 빠짐)", sorted(seen["하위 폴더"]),
           sorted(p for p in seen["뿌리"] if p != "README"))


HEAVY: str = "".join(f"\n\ndef helper_{i}() -> int:\n    return {i}\n" for i in range(12))


def _chain_repo(td: Path) -> "tuple[Repo, str, str]":
    """상류가 term/ 를 만들며 solar_term_x 를 머리 합류로 넣고 많이 고침 · 레인은 solar_term_y · z 를 더함."""
    repo = Repo(td)
    repo.write({SV + "__init__.py": "", SV + "moon_phase.py": _vo("moon_phase"),
                SV + "solar_term_x.py": _vo("solar_term_x"), SV + "term_a.py": _vo("term_a"),
                SV + "term_b.py": _vo("term_b"), "mypy.ini": "[mypy]\nstrict = True\n"})
    anchor = repo.commit("앵커")
    repo.git("checkout", "-q", "-b", "lane")
    repo.write({SV + "solar_term_y.py": _vo("solar_term_y"),
                SV + "solar_term_z.py": _vo("solar_term_z", "from .moon_phase import MoonPhase")})
    repo.commit("레인 새 파일")
    repo.git("checkout", "-q", "main")
    (repo.root / SV / "term").mkdir()
    for s in ("term_a", "term_b", "solar_term_x"):
        repo.git("mv", f"{SV}{s}.py", f"{SV}term/{s}.py")
    repo.write({SV + "term/__init__.py": "", SV + "term/term_c.py": _vo("term_c"),
                SV + "term/solar_term_x.py": _vo("solar_term_x") + HEAVY})
    repo.commit("상류 term 묶음")
    repo.git("checkout", "-q", "lane")
    repo.git("merge", "-q", "--no-edit", "main")
    return repo, anchor, repo.git("rev-parse", "HEAD")


def _clone(src: Repo, dest: Path) -> Repo:
    shutil.copytree(src.git_root, dest, symlinks=False)
    out = Repo.__new__(Repo)
    out.git_root = dest
    out.root = dest
    return out


def scen_chain(fg, scripts: Path, run: Run, td: Path) -> None:
    base, anchor, merge = _chain_repo(td / "chain")
    x_old, x_new = SV + "term/solar_term_x.py", SV + "solar_term/solar_term_x.py"
    # 창 안 다시 옮김 — 병합 몫(A → B)과 레인 이동(B → C)
    repo = _clone(base, td / "chain-window")
    folder = _folder(repo, "c1", anchor, [merge])
    rc, out = _tool(scripts, "draft", repo.root, "--bc", "orbit", "--run", folder)
    run.eq("다시 옮김 draft — 이 실행 이동 · 남은 이동", (rc, _starting(out, "이 실행 이동"), _starting(out, "남은 이동")), (0, [
        f"이 실행 이동 {x_old} -> {x_new}"], [
        f"남은 이동 {SV}solar_term_y.py -> {SV}solar_term/solar_term_y.py",
        f"남은 이동 {SV}solar_term_z.py -> {SV}solar_term/solar_term_z.py",
        f"남은 이동 {x_old} -> {x_new}"]))
    run.eq("다시 옮김 expected_moves(앵커 → R)", fg.expected_moves(repo.root, folder), {
        SV + "solar_term_x.py": x_new, SV + "term_a.py": SV + "term/term_a.py", SV + "term_b.py": SV + "term/term_b.py"})
    rc, text = _guard(scripts, repo, folder, "open", "--kind", "code", "--mode", "feature")
    run.true("behavior_guard open", rc == 0, text[-400:])
    rc, out = _tool(scripts, "apply", repo.root, "--run", folder, "--run-moves")
    run.eq("apply --run-moves", rc, 0)
    repo.commit("묶음 창")
    rc, text = _guard(scripts, repo, folder, "close")
    run.true("behavior_guard close green", rc == 0, text[-600:])
    rc, out = _tool(scripts, "verify", repo.root, "--run", folder, "--window", "1")
    run.eq("묶음 창 판정 green · 쌍", (rc, _starting(out, "쌍"), _starting(out, "red")), (0, [
        f"쌍 {SV}solar_term_y.py -> {SV}solar_term/solar_term_y.py",
        f"쌍 {SV}solar_term_z.py -> {SV}solar_term/solar_term_z.py", f"쌍 {x_old} -> {x_new}"], []))
    run.eq("옮긴 z 의 상대 import 는 새 깊이",
           (repo.root / SV / "solar_term/solar_term_z.py").read_text(encoding="utf-8"),
           _vo("solar_term_z", "from ..moon_phase import MoonPhase"))
    run.eq("새 묶음 빈 __init__", (repo.root / SV / "solar_term/__init__.py").read_text(encoding="utf-8"), "")
    rc, out = _tool(scripts, "verify", repo.root, "--run", folder)
    run.eq("verify --run green — 많이 고친 뒤 옮긴 파일도 병합 몫 쌍", (rc, _starting(out, "red"), _starting(out, "이동"),
                                                         _starting(out, "병합 몫")), (0, [], [
        f"이동 {x_old} -> {x_new}"], [
        f"병합 몫 {SV}solar_term_x.py -> {x_old}", f"병합 몫 {SV}term_a.py -> {SV}term/term_a.py",
        f"병합 몫 {SV}term_b.py -> {SV}term/term_b.py"]))
    # 같은 이동을 창 밖에서 손으로
    hand = _clone(base, td / "chain-hand")
    folder = _folder(hand, "c2", anchor, [merge])
    (hand.root / SV / "solar_term").mkdir()
    for s in ("term/solar_term_x", "solar_term_y", "solar_term_z"):
        hand.git("mv", f"{SV}{s}.py", f"{SV}solar_term/{s.split('/')[-1]}.py")
    hand.write({SV + "solar_term/__init__.py": ""})
    hand.commit("손으로 옮김")
    rc, out = _tool(scripts, "verify", hand.root, "--run", folder)
    run.eq("창 밖 이동 red", (rc, _starting(out, "red")), (2, [
        f"red: 창 밖 이동 `{x_old}` -> `{x_new}` — green 묶음 창의 쌍으로 이어지지 않는다(되돌리고 끝 맞춤 다시)"]))
    # 섞인 창 — 이동과 기능 편집을 한 창에서
    mixed = _clone(base, td / "chain-mixed")
    folder = _folder(mixed, "c3", anchor, [merge])
    rc, text = _guard(scripts, mixed, folder, "open", "--kind", "code", "--mode", "feature")
    _tool(scripts, "apply", mixed.root, "--run", folder, "--run-moves")
    mixed.write({SV + "moon_phase.py": _vo("moon_phase") + "# 기능 편집\n"})
    mixed.commit("섞인 창")
    _guard(scripts, mixed, folder, "close")
    rc, out = _tool(scripts, "verify", mixed.root, "--run", folder, "--window", "1")
    run.eq("섞인 창 red", (rc, _starting(out, "red")), (2, [
        f"red: 창 안 다른 변화 `{SV}moon_phase.py` — 묶음 창은 이동 · import 치환 · 빈 묶음 `__init__` · 설정 파일 경로 치환만 받는다"]))
    rc, out = _tool(scripts, "verify", mixed.root, "--run", folder)
    run.true("red 창이 있으면 verify --run red", rc == 2 and "red: red 묶음 창 w1 — 그 창을 철회하고 다시 연다" in out,
             str(out[-4:]))
    # 미커밋 비 .py 설정 파일 — 창 기록에 원문이 없어 판정 불가
    cfg = _clone(base, td / "chain-cfg")
    folder = _folder(cfg, "c4", anchor, [merge])
    cfg.write({"mypy.ini": f"[mypy]\nstrict = True\n\n[mypy-{PKG}.term.solar_term_x]\nignore_errors = True\n"})
    rc, out = _tool(scripts, "draft", cfg.root, "--bc", "orbit", "--run", folder)
    run.eq("draft --run 이 미커밋 설정 파일을 냄", _starting(out, "미커밋 설정"), ["미커밋 설정 mypy.ini"])
    _guard(scripts, cfg, folder, "open", "--kind", "code", "--mode", "feature")
    _tool(scripts, "apply", cfg.root, "--run", folder, "--run-moves")
    run.eq("설정 파일 경로 치환", (cfg.root / "mypy.ini").read_text(encoding="utf-8"),
           f"[mypy]\nstrict = True\n\n[mypy-{PKG}.solar_term.solar_term_x]\nignore_errors = True\n")
    cfg.commit("설정 창")
    _guard(scripts, cfg, folder, "close")
    rc, out = _tool(scripts, "verify", cfg.root, "--run", folder, "--window", "1")
    run.true("미커밋 비 .py 설정 → 판정 불가 red", rc == 2 and any("판정 불가 `mypy.ini`" in ln for ln in out), str(out))


JUDGE: str = (
    '"""달 판정."""\n'
    "import importlib\n"
    "from unittest import mock\n\n"
    "from ..shared_value_object.void_a import VoidA\n"
    f"from {PKG} import void_b, moon_phase\n"
    f"import {PKG}.void_c\n"
    f"import {PKG} as svo\n\n\n"
    "def judge_moon() -> int:\n"
    "    first: object = svo.void_a.VoidA\n"
    f"    second: object = {PKG}.void_c.VoidC\n"
    f'    with mock.patch("{PKG}.void_a.VoidA"):\n'
    "        pass\n"
    f'    importlib.import_module("{PKG}.void_b")\n'
    "    return len([VoidA, void_b, moon_phase, first, second])\n")
JUDGE_AFTER: str = (
    '"""달 판정."""\n'
    "import importlib\n"
    "from unittest import mock\n\n"
    "from ..shared_value_object.void.void_a import VoidA\n"
    f"from {PKG}.void import void_b\nfrom {PKG} import moon_phase\n"
    f"import {PKG}.void.void_c\n"
    f"import {PKG} as svo\n\n\n"
    "def judge_moon() -> int:\n"
    "    first: object = svo.void.void_a.VoidA\n"
    f"    second: object = {PKG}.void.void_c.VoidC\n"
    f'    with mock.patch("{PKG}.void.void_a.VoidA"):\n'
    "        pass\n"
    f'    importlib.import_module("{PKG}.void.void_b")\n'
    "    return len([VoidA, void_b, moon_phase, first, second])\n")
DEBT_LINE: str = f"[#656] {SV}__init__.py: 묶음 `void/` 을(를) 만든다"


def _debt_repo(td: Path, extra: "dict[str, str]" = ()) -> "tuple[Repo, str]":
    repo = Repo(td)
    files = {
        SV + "__init__.py": "", SV + "moon_phase.py": _vo("moon_phase"),
        SV + "void_a.py": _vo("void_a", "from .moon_phase import MoonPhase"),
        SV + "void_b.py": _vo("void_b"), SV + "void_c.py": _vo("void_c"),
        DS + "__init__.py": "", DS + "judge_moon.py": JUDGE,
        "application/stellar/domain_layer/shared_value_object/star_link.py": _vo(
            "star_link", f"from {PKG}.void_a import VoidA"),
        "application/orbit/migrations/0002_fill.py": (
            '"""정적 경로."""\nTARGET: str = "' + PKG + '.void_a.VoidA"\n'),
        "mypy.ini": f"[mypy-{PKG}.void_a]\nignore_errors = True\n",
        "setup.cfg": f"[coverage:run]\nomit = {SV}void_b.py\n",
    }
    files.update(dict(extra))
    repo.write(files)
    return repo, repo.commit("앵커")


def _scope(decision: str) -> str:
    return ("| ID | 위반 | 백스톱 | 미룰 수 있나 |\n|---|---|---|---|\n"
            f"| D1 | {DEBT_LINE} | check-domain-model | 예 |\n\n"
            f"D1 · 결정 = {decision} · 사유 = 시험 · 출처 = 본인 직접(2026-10-27T00:00)\n\n# 앞 실행\n\n"
            "D1 · 결정 = ⓐ · 사유 = 앞 실행 몫(읽지 않음)\n")


def scen_debt(fg, scripts: Path, run: Run, td: Path) -> None:
    moved = [(f"{SV}void_{x}.py", f"{SV}void/void_{x}.py") for x in "abc"]
    # 미룬 빚(ⓑ) · ⓐ′ — 이 실행의 이동 0 · R 의 줄은 앵커 줄과 같음(불변식 3 · 5)
    for decision in ("ⓑ", "ⓐ′"):
        repo, anchor = _debt_repo(td / f"debt-{'b' if decision == 'ⓑ' else 'a2'}")
        folder = _folder(repo, "d0", anchor, scope=_scope(decision))
        rc, out = _tool(scripts, "draft", repo.root, "--bc", "orbit", "--run", folder)
        run.eq(f"미룬 빚({decision}) — 빚 · 이 실행 · 예상 이동 0",
               (rc, _starting(out, "빚 이동"), _starting(out, "이 실행 이동"), _starting(out, "예상 이동")), (0, [], [], []))
        run.eq(f"미룬 빚({decision}) — 줄은 그대로", _starting(out, "줄 "), [f"줄 {DEBT_LINE}"])
    # ⓐ — 빚 창에서 apply --debt
    repo, anchor = _debt_repo(td / "debt-a")
    folder = _folder(repo, "d1", anchor, scope=_scope("ⓐ"))
    rc, out = _tool(scripts, "draft", repo.root, "--bc", "orbit", "--run", folder)
    run.eq("ⓐ 빚 — 빚 이동 셋 · 이 실행 이동 0", (_starting(out, "빚 이동"), _starting(out, "이 실행 이동")), (
        [f"빚 이동 {a} -> {b}" for a, b in moved], []))
    run.eq("ⓐ 빚 — 다른 BC import 알림", _starting(out, "다른 BC import"), [
        f"다른 BC import application/stellar/domain_layer/shared_value_object/star_link.py:3 {PKG}.void_a"])
    _guard(scripts, repo, folder, "open", "--kind", "code", "--mode", "feature")
    rc, out = _tool(scripts, "apply", repo.root, "--run", folder, "--debt")
    run.eq("apply --debt 이동", (rc, _starting(out, "이동")), (0, [f"이동 {a} -> {b}" for a, b in moved]))
    read = lambda rel: (repo.root / rel).read_text(encoding="utf-8")  # noqa: E731
    run.eq("import 치환 ⓐ ~ ⓔ(나눔 · 상대 · 속성 사슬 · 문자열)", read(DS + "judge_moon.py"), JUDGE_AFTER)
    run.eq("옮긴 파일의 상대 import 는 새 깊이", read(SV + "void/void_a.py"),
           _vo("void_a", "from ..moon_phase import MoonPhase"))
    run.eq("다른 BC 의 import 도 고침", read("application/stellar/domain_layer/shared_value_object/star_link.py"),
           _vo("star_link", f"from {PKG}.void.void_a import VoidA"))
    run.eq("마이그레이션 정적 경로 치환", read("application/orbit/migrations/0002_fill.py"),
           '"""정적 경로."""\nTARGET: str = "' + PKG + '.void.void_a.VoidA"\n')
    run.eq("mypy.ini 점 경로 치환", read("mypy.ini"), f"[mypy-{PKG}.void.void_a]\nignore_errors = True\n")
    run.eq("setup.cfg 슬래시 경로 치환", read("setup.cfg"), f"[coverage:run]\nomit = {SV}void/void_b.py\n")
    run.eq("새 묶음 빈 __init__", read(SV + "void/__init__.py"), "")
    repo.commit("빚 창")
    rc, text = _guard(scripts, repo, folder, "close")
    run.true("빚 창 behavior_guard close green", rc == 0, text[-600:])
    rc, out = _tool(scripts, "verify", repo.root, "--run", folder, "--window", "1")
    run.eq("빚 창 판정 green", (rc, _starting(out, "red")), (0, []))
    rc, out = _tool(scripts, "verify", repo.root, "--run", folder)
    run.eq("빚 창 뒤 verify --run green", (rc, _starting(out, "red")), (0, []))
    # 계산된 이름 — 기계 이동 불가면 옮기지 않음
    blocked, anchor = _debt_repo(td / "debt-blocked", {DS + "load_part.py": (
        '"""계산된 import."""\nimport importlib\n\n\ndef load_part(name: str) -> object:\n'
        f'    return importlib.import_module(f"{PKG}.{{name}}")\n')})
    folder = _folder(blocked, "d2", anchor, scope=_scope("ⓐ"))
    rc, out = _tool(scripts, "apply", blocked.root, "--run", folder, "--debt")
    run.eq("기계 이동 불가 → apply 멈춤", (rc, _starting(out, "기계 이동 불가")), (1, [
        f"기계 이동 불가 {DS}load_part.py:6 계산된 import"]))
    run.true("멈추면 옮기지 않음", (blocked.root / SV / "void_a.py").is_file())
    # G0 요약 · 설계 때(--spec) 새 파일 자리 — 미룬 빚 폴더의 새 파일은 부모(D2) · ⓐ 면 그 묶음
    plain, _anchor = _debt_repo(td / "debt-draft")
    rc, out = _tool(scripts, "draft", plain.root, "--bc", "orbit", "--summary")
    run.eq("draft --summary", (rc, _starting(out, "요약")), (0, ["요약 orbit: 묶음 빚: 폴더 1 · 파일 3 · import 줄 어림 4"]))
    spec = plain.root / "spec.md"
    spec.write_text(f"# 명세\n\n<!-- machine: file-plan -->\n```paths\nadd {SV}void_d.py  # 새 값\n```\n", encoding="utf-8")
    rc, out = _tool(scripts, "draft", plain.root, "--bc", "orbit", "--spec", spec)
    run.eq("draft --spec — 미룬 빚 폴더의 새 파일은 부모(D2)", (rc, _starting(out, "새 파일")), (0, [
        f"새 파일 {SV}void_d.py -> {SV}void_d.py"]))
    scope_dir = plain.root / ".dddjango" / "g1"
    scope_dir.mkdir(parents=True)
    (scope_dir / "refactor-scope.md").write_text("실행 · G0 승인 g1\n\n" + _scope("ⓐ"), encoding="utf-8")
    rc, out = _tool(scripts, "draft", plain.root, "--bc", "orbit", "--spec", spec, "--run", scope_dir)
    run.eq("draft --spec --run — ⓐ 빚이면 새 파일도 그 묶음", (rc, _starting(out, "새 파일"), _starting(out, "빚 이동")), (0, [
        f"새 파일 {SV}void_d.py -> {SV}void/void_d.py"], [f"빚 이동 {a} -> {b}" for a, b in moved]))
    # apply_to_copy — git 아닌 격리 사본(pre-gate)
    copy = td / "debt-copy"
    shutil.copytree(plain.root, copy, symlinks=False, ignore=shutil.ignore_patterns(".git", ".dddjango", "spec.md"))
    done = fg.apply_to_copy(copy, moved)
    run.eq("apply_to_copy 쌍", done, moved)
    run.eq("apply_to_copy import 치환", (copy / DS / "judge_moon.py").read_text(encoding="utf-8"), JUDGE_AFTER)
    run.eq("apply_to_copy 옛 파일 없음 · 새 묶음 __init__",
           (any((copy / a).exists() for a, _ in moved), (copy / SV / "void/__init__.py").read_text(encoding="utf-8")),
           (False, ""))
    # 불변식 5 — R 의 #656 줄 ⊆ 앵커 줄(미룬 실행)
    repo, anchor = _debt_repo(td / "debt-inv5")
    folder = _folder(repo, "d3", anchor, scope=_scope("ⓑ"))
    run_in = fg.load_run(repo.root, folder, None)
    plan = fg.plan_for(run_in)
    r_tree = fg.move_texts(run_in.now, plan.pairs(plan.current, plan.final))
    r_lines = set(fg.lines(fg.place(r_tree, fg.group_dirs_of(r_tree))))
    anchor_lines = set(fg.lines(fg.place(run_in.t0, fg.group_dirs_of(run_in.t0))))
    run.true("불변식 5 — R 의 줄 ⊆ 앵커 줄", r_lines <= anchor_lines and bool(r_lines), f"{r_lines} ⊄ {anchor_lines}")


def scen_legacy(fg, scripts: Path, run: Run, td: Path) -> None:
    """5절 ⓪ — 이관 빚 목록에 오른 줄은 새 파일도 지금 자리 그대로(9.3 «부모에 두고 이관 빚»)."""
    # 늦은 슬라이스의 셋째 파일이 부른 형성 — «만든다» 줄이 이관 빚이면 형성 없음 · 셋 모두 부모
    repo = Repo(td / "late-make")
    repo.write({SV + "__init__.py": "", SV + "void_a.py": _vo("void_a"), SV + "void_b.py": _vo("void_b"),
                SV + "moon_phase.py": _vo("moon_phase")})
    folder = _folder(repo, "l1", repo.commit("앵커"))
    repo.write({SV + "void_c.py": _vo("void_c")})
    repo.commit("슬라이스")
    legacy = td / "legacy-make.txt"
    legacy.write_text(f"#656 {SV}__init__.py: 묶음 `void/` 을(를) 만든다\n", encoding="utf-8")
    rc, out = _tool(scripts, "draft", repo.root, "--bc", "orbit", "--run", folder, "--legacy-debt-file", legacy)
    run.eq("⓪ «만든다» 이관 빚 — 이동 0 · 새 파일 부모 · 형성 0",
           (rc, _starting(out, "이 실행 이동"), _starting(out, "남은 이동"), _starting(out, "새 파일"),
            _starting(out, "알림 묶음")),
           (0, [], [], [f"새 파일 {SV}void_c.py -> {SV}void_c.py"],
            ["알림 묶음: 새 파일 1 · 이 실행의 이동 0(형성 0 · 해체 0 · 다시 놓기 0) · 경로 결속 0 · 다른 BC import 0"]))
    plan = fg.plan_for(fg.load_run(repo.root, folder, None), fg.legacy_entries(legacy))
    run.eq("⓪ «만든다» 이관 빚 — 이 실행의 형성 묶음 없음", plan.formed, set())
    rc, out = _tool(scripts, "verify", repo.root, "--run", folder, "--legacy-debt-file", legacy)
    run.eq("⓪ «만든다» 이관 빚 — verify --run green", (rc, _starting(out, "red")), (0, []))
    # 있는 묶음 옆에 평평하게 둔 새 파일 — 그 파일 줄이 이관 빚이면 부모 그대로
    repo = Repo(td / "late-file")
    repo.write({SV + "__init__.py": "", SV + "void/__init__.py": "", SV + "void/void_a.py": _vo("void_a"),
                SV + "void/void_b.py": _vo("void_b"), SV + "moon_phase.py": _vo("moon_phase")})
    folder = _folder(repo, "l2", repo.commit("앵커"))
    repo.write({SV + "void_c.py": _vo("void_c")})
    repo.commit("슬라이스")
    legacy = td / "legacy-file.txt"
    legacy.write_text(f"#656 {SV}void_c.py: 묶음 `void/` 에 둔다\n", encoding="utf-8")
    rc, out = _tool(scripts, "draft", repo.root, "--bc", "orbit", "--run", folder, "--legacy-debt-file", legacy)
    run.eq("⓪ 새 파일 줄 이관 빚 — 새 파일 부모 · 남은 이동 0",
           (rc, _starting(out, "새 파일"), _starting(out, "남은 이동")),
           (0, [f"새 파일 {SV}void_c.py -> {SV}void_c.py"], []))
    rc, out = _tool(scripts, "verify", repo.root, "--run", folder, "--legacy-debt-file", legacy)
    run.eq("⓪ 새 파일 줄 이관 빚 — verify --run green", (rc, _starting(out, "red")), (0, []))
    rc, out = _tool(scripts, "draft", repo.root, "--bc", "orbit", "--run", folder)
    run.eq("목록 없으면 새 파일은 있는 묶음으로", _starting(out, "새 파일"), [f"새 파일 {SV}void_c.py -> {SV}void/void_c.py"])


# ── 검토 고침(2.28.0 검토 A · B) — 메모리 ─────────────────────────────────────────

WEB: str = "web/application/orbit/domain_layer/"
MIRROR: str = "application/orbit/test/unit/domain_layer/shared_value_object/"


def _rel_lines(fg, tree: "dict[str, str]") -> "list[tuple[str, str]]":
    return fg.lines(fg.place(tree, fg.group_dirs_of(tree)))


def review_debt_undo(fg, run: Run) -> None:
    """A1 — 빚 줄은 줄마다(5절 B): «zeta/ 푼다» 만 ⓐ 면 zeta 의 파일은 부모로 · 미룬 «void/ 만든다» 는 하지 않는다."""
    t0 = {SV + "__init__.py": "", SV + "zeta/__init__.py": "", SV + "zeta/void_a.py": _vo("void_a"),
          SV + "void_b.py": _vo("void_b"), SV + "void_c.py": _vo("void_c"), SV + "moon.py": _vo("moon")}
    make, undo = (SV + "__init__.py", fg.MAKE.format("void")), (SV + "zeta/__init__.py", fg.UNDO.format("zeta"))
    run.eq("A1 앵커 줄", _rel_lines(fg, t0), [make, undo])
    plan = fg.compute_plan(t0, t0, t0, lambda c: {x for x in c if x == undo})
    run.eq("A1 «푼다» 만 ⓐ — 빚 이동은 부모로", plan.pairs(plan.base, plan.debt), [(SV + "zeta/void_a.py", SV + "void_a.py")])
    r_tree = fg.move_texts(t0, fg._expand(plan.pairs(plan.current, plan.final), t0), plan.drops)
    run.eq("A1 R 의 줄 = 미룬 «만든다» 하나(불변식 5)", _rel_lines(fg, r_tree), [make])


def review_scope(fg, run: Run) -> None:
    """A2 — 도구 범위 = 검사기 범위(서버 BC `application/<bc>/domain_layer/`). 시험 거울 · 자매 web 은 자리 · 낱말 밖."""
    for path in (MIRROR + "test_void_a.py", WEB + "ghost_gate/ghost_gate.py", "lib/orbit/domain_layer/x/value_object/a.py"):
        run.eq(f"A2 범위 밖 `{path}`", (fg._is_layer_py(path), fg.slot_of(path)), (False, None))
    base = {SV + "__init__.py": "", SV + "void_state.py": _vo("void_state")}
    now = dict(base, **{MIRROR + f"test_void_{x}.py": "def test_x() -> None:\n    pass\n" for x in "abc"})
    plan = fg.compute_plan(base, base, now, lambda c: set())
    run.eq("A2 시험 거울 파일은 옮기지 않는다", plan.pairs(plan.current, plan.final), [])
    server = {SV + "__init__.py": "", SV + "moon.py": _vo("moon"), **{SV + f"ghost_gate_{x}.py": _vo(f"ghost_gate_{x}")
                                                                     for x in "abc"}}
    web = {WEB + "ghost_gate/ghost_gate.py": "class GhostGate:\n    pass\n",
           WEB + "ghost_gate/value_object/gate_hint.py": "class GateHint:\n    pass\n"}
    targets = lambda files: {p: fp.target for p, fp in fg.place(files, fg.group_dirs_of(files)).files.items()}  # noqa
    run.eq("A2 web 의 애그리거트 구가 서버 BC 자리를 바꾸지 않는다", targets({**server, **web}), targets(server))


def review_rewrite(fg, run: Run) -> None:
    """A7 — 뜻이 다른 코드를 내지 않는다: 정확히 고치거나 «기계 이동 불가»로 멈춘다."""
    old, new = SV + "void_a.py", SV + "void/void_a.py"
    pairs = [(old, new), (SV + "void_b.py", SV + "void/void_b.py")]
    moves = fg.module_moves(pairs)
    user = SV + "user.py"

    def rw(text: str, path: str = user, to: "str | None" = None) -> str:
        return fg.rewrite_source(text, path, to or path, moves)

    cases = (
        ("역슬래시 이음 지킴", f"from {PKG}.void_a \\\n    import VoidA\n", user, None,
         f"from {PKG}.void.void_a \\\n    import VoidA\n"),
        ("`from .import` (옮긴 파일)", "from .import moon\n", old, new, "from ..import moon\n"),
        ("`from.moon` (옮긴 파일)", "from.moon import Moon\n", old, new, "from..moon import Moon\n"),
        ("`from .import void_a` 띄움", "from .import void_a\n", user, None, "from .void import void_a\n"),
        ("괄호 나눔 — 주석 지킴", "if True:\n    from . import (  # keep\n        void_a,  # a\n        moon,\n    )\n",
         user, None, "if True:\n    from .void import (  # keep\n        void_a,  # a\n    )\n"
                     "    from . import (\n        moon,\n    )\n"),
        ("괄호 나눔 — 제 줄 주석", "from . import (\n    # 앞\n    moon,\n    void_a,\n    # 끝\n)\n", user, None,
         "from . import (\n    # 앞\n    moon,\n)\nfrom .void import (\n    void_a,\n    # 끝\n)\n"),
        ("역슬래시 이음 나눔(문장 안)", "from . import void_a, \\\n    moon\n", user, None,
         "from .void import void_a\nfrom . import moon\n"),
        ("한 줄 복합문 — 나눔 없이 고침", "x = 1; from .void_a import VoidA\n", user, None,
         "x = 1; from .void.void_a import VoidA\n"))
    for label, text, path, to, want in cases:
        got = rw(text, path, to)
        run.eq(f"A7 {label}", got, want)
        try:
            compile(got, "<rewrite>", "exec")
        except SyntaxError as exc:
            run.fails.append(f"A7 {label}: 고친 글이 문법 오류 — {exc}")
    blocked = (("한 줄 복합문 나눔", "counter = bump(); from . import void_a, moon\n"),
               ("한 줄 복합문 나눔", "from . import void_a, moon; y = 1\n"),
               ("한 줄 복합문 나눔", "if True: from . import void_a, moon\n"),
               ("역슬래시 이음 나눔", "x = 1; \\\nfrom . import void_a, moon\n"))
    for reason, text in blocked:
        run.eq(f"A7 {reason} — 글 그대로", rw(text), text)
        hz = fg.hazards({user: text, old: _vo("void_a"), SV + "void_b.py": _vo("void_b")}, pairs, ["orbit"])
        line = len(text.split("from .")[0].split("\n"))
        run.eq(f"A7 {reason} → 기계 이동 불가 `{text.strip()[:30]}`", hz.blocked, [f"{user}:{line} {reason}"])


def review_clash(fg, run: Run) -> None:
    """A8 — 한 부모의 `x/tarot.py` · `tarot.py` 는 기계로 못 옮긴다(둘이 한 자리로 가지 않고 · 하나를 조용히 버리지 않는다)."""
    t = {SV + "__init__.py": "", SV + "x/__init__.py": "", SV + "x/tarot.py": _vo("tarot"), SV + "tarot.py": _vo("tarot"),
         SV + "moon.py": _vo("moon")}
    placement = fg.place(t, fg.group_dirs_of(t))
    run.eq("A8 place 는 그대로(검사기 줄은 빚으로 남음)", sorted(fp.target for fp in placement.files.values()),
           [SV + "moon.py", SV + "tarot.py", SV + "tarot.py"])
    run.eq("A8 placement_moves — 겹친 둘은 옮기지 않는다", fg.placement_moves(placement), [])
    plan = fg.compute_plan(t, t, t, lambda c: set())
    run.eq("A8 compute_plan — 이름 겹침", plan.clashes, [(SV + "tarot.py", SV + "x/tarot.py")])
    run.eq("A8 compute_plan — 겹친 키는 계획 밖(조용히 하나를 고르지 않음)",
           sorted(v for v in plan.current.values()), [SV + "moon.py"])


def review_deep(fg, run: Run) -> None:
    """S3 — 파서가 «너무 깊음»(최신 판 MemoryError · RecursionError)을 내는 글도 자리 셈을 죽이지 않는다(파싱 불능 = 글 없음)."""
    deep = "x = " + "-" * 6000 + "1\n"
    t = {SV + "__init__.py": "", SV + "void_a.py": deep, SV + "void_b.py": _vo("void_b"), SV + "void_c.py": _vo("void_c"),
         SV + "moon.py": _vo("moon")}
    run.eq("S3 깊은 식 — 자리 셈", _rel_lines(fg, t), [(SV + "__init__.py", fg.MAKE.format("void"))])
    run.eq("S3 깊은 식 — 치환 · 빈 init 판정", (fg.rewrite_source(deep, SV + "void_a.py", SV + "void/void_a.py", {}) == deep,
                                          fg.empty_init(deep)), (True, False))


def check_review_memory(fg, run: Run) -> None:
    for step in (review_debt_undo, review_scope, review_rewrite, review_clash, review_deep):
        try:
            step(fg, run)
        except Exception as exc:  # 한 갈래의 예외가 다른 갈래를 가리지 않게
            run.fails.append(f"{step.__name__} 예외: {exc!r}")


# ── 검토 고침 — git 시나리오 ───────────────────────────────────────────────────

def _lines_of(out: "list[str]", *heads: str) -> "list[str]":
    return [ln for ln in out if ln.startswith(heads)]


def scen_review_scope(fg, scripts: Path, run: Run, td: Path) -> None:
    """A2 · S4 — 시험 거울 · web 은 옮기지 않고 낱말에도 들지 않는다 · 그 import 는 apply 가 고친다(프로젝트 전체)."""
    repo = Repo(td / "scope")
    imp = f"from {PKG}.ghost_gate_a import GhostGateA\n"
    repo.write({SV + "__init__.py": "", SV + "ghost_gate_a.py": _vo("ghost_gate_a"),
                SV + "ghost_gate_b.py": _vo("ghost_gate_b"), SV + "moon.py": _vo("moon"),
                WEB + "ghost_gate/__init__.py": "", WEB + "ghost_gate/ghost_gate.py": "class GhostGate:\n    pass\n",
                WEB + "ghost_gate/value_object/gate_hint.py": "class GateHint:\n    pass\n",
                "web/application/orbit/view/ghost_view.py": imp,
                MIRROR + "__init__.py": "", MIRROR + "test_ghost.py": imp})
    folder = _folder(repo, "s1", repo.commit("앵커"))
    repo.write({SV + "ghost_gate_c.py": _vo("ghost_gate_c"),
                **{MIRROR + f"test_void_{x}.py": "def test_x() -> None:\n    pass\n" for x in "abc"}})
    repo.commit("슬라이스 — 새 값 하나 · 새 시험 셋")
    want = [f"남은 이동 {SV}ghost_gate_{x}.py -> {SV}ghost/ghost_gate_{x}.py" for x in "abc"]
    rc, out = _tool(scripts, "draft", repo.root, "--bc", "orbit", "--run", folder)
    run.eq("A2 draft --run — 서버 BC 파일만 · 검사기와 같은 묶음", (rc, _lines_of(out, "남은 이동")), (0, want))
    spec = repo.root / "spec.md"
    spec.write_text(f"<!-- machine: file-plan -->\n```paths\nadd {SV}ghost_gate_d.py\n```\n", encoding="utf-8")
    rc, out = _tool(scripts, "draft", repo.root, "--bc", "orbit", "--spec", spec, "--run", folder)
    run.eq("S4 draft --spec --run — 시험 · web 파일이 지운 것으로 보이지 않음",
           (rc, [ln for ln in out if "/test/" in ln or ln.startswith(("새 파일", "web")) or " web/" in ln]),
           (0, [f"새 파일 {SV}ghost_gate_{x}.py -> {SV}ghost/ghost_gate_{x}.py" for x in "cd"]))
    spec.unlink()
    rc, out = _tool(scripts, "apply", repo.root, "--run", folder, "--run-moves")
    run.eq("A2 apply — 서버 파일만 옮김", (rc, _lines_of(out, "이동")),
           (0, [f"이동 {SV}ghost_gate_{x}.py -> {SV}ghost/ghost_gate_{x}.py" for x in "abc"]))
    new_imp = f"from {PKG}.ghost.ghost_gate_a import GhostGateA\n"
    read = lambda rel: (repo.root / rel).read_text(encoding="utf-8")  # noqa: E731
    run.eq("A2 시험 거울 · web 의 import 는 고침 · 자리는 그대로",
           (read(MIRROR + "test_ghost.py"), read("web/application/orbit/view/ghost_view.py"),
            sorted(p.name for p in (repo.root / MIRROR).iterdir() if p.suffix == ".py")),
           (new_imp, new_imp, ["__init__.py", "test_ghost.py", "test_void_a.py", "test_void_b.py", "test_void_c.py"]))
    _code, got, _tail = _checker(scripts, "check-domain-model.py", repo.root)
    run.eq("A2 apply 뒤 검사기 #654~#656 0(도구 = 검사기)", [ln for ln in got if _GROUP_LINE.match(ln)], [])


def _window(scripts: Path, repo: Repo, folder: Path, n: int, *apply_args: str,
            edit: "object" = None) -> "tuple[int, list[str], list[str]]":
    rc, text = _guard(scripts, repo, folder, "open", "--kind", "code", "--mode", "feature")
    if rc != 0:
        return rc, [f"open 실패 {text[-300:]}"], []
    rc, out = _tool(scripts, "apply", repo.root, "--run", folder, *apply_args)
    if callable(edit):
        edit(repo)
    repo.commit(f"묶음 창 {n}")
    _guard(scripts, repo, folder, "close")
    vc, vout = _tool(scripts, "verify", repo.root, "--run", folder, "--window", str(n))
    return vc, _lines_of(vout, "red"), out


def scen_review_dissolve(fg, scripts: Path, run: Run, td: Path) -> None:
    """A3 · A4 · B10 — 빈(0바이트 · docstring · 주석뿐) 묶음 `__init__` 만 남으면 apply 가 폴더째 푼다 · 내용 있는 `__init__` 은
    남긴다 · 창 판정은 묶음 `__init__` 의 새로 · 지움만 받는다."""
    repo = Repo(td / "dissolve")
    repo.write({SV + "__init__.py": "", SV + "moon_phase.py": _vo("moon_phase"), SV + "star_dust.py": _vo("star_dust"),
                SV + "void/__init__.py": "", SV + "void/void_a.py": _vo("void_a"), SV + "void/void_b.py": _vo("void_b"),
                SV + "zeta/__init__.py": '"""zeta 묶음."""\n# 주석\n', SV + "zeta/zeta_one.py": _vo("zeta_one"),
                SV + "zeta/zeta_two.py": _vo("zeta_two"), SV + "kappa/__init__.py": "KAPPA: int = 1\n",
                SV + "kappa/kappa_one.py": _vo("kappa_one"), SV + "kappa/kappa_two.py": _vo("kappa_two")})
    folder = _folder(repo, "v1", repo.commit("앵커"))
    for rel in ("void/void_a.py", "void/void_b.py", "zeta/zeta_two.py", "kappa/kappa_two.py"):
        (repo.root / SV / rel).unlink()
    repo.commit("슬라이스 — 파일 지움")
    vc, reds, out = _window(scripts, repo, folder, 1, "--run-moves")
    run.eq("A3 · A4 apply — 남은 파일만 옮김", _lines_of(out, "이동"), [
        f"이동 {SV}kappa/kappa_one.py -> {SV}kappa_one.py", f"이동 {SV}zeta/zeta_one.py -> {SV}zeta_one.py"])
    run.eq("A3 · A4 빈 · docstring 묶음은 폴더째 지움 · 내용 있는 `__init__` 은 남김",
           ((repo.root / SV / "void").exists(), (repo.root / SV / "zeta").exists(),
            (repo.root / SV / "kappa/__init__.py").read_text(encoding="utf-8")), (False, False, "KAPPA: int = 1\n"))
    run.eq("A3 · A4 창 판정 green(빈 묶음 `__init__` 지움)", (vc, reds), (0, []))
    rc, out = _tool(scripts, "verify", repo.root, "--run", folder)
    run.eq("A3 · A4 verify --run green", (rc, _lines_of(out, "red")), (0, []))
    _code, got, _tail = _checker(scripts, "check-domain-model.py", repo.root)
    run.eq("A3 · A4 남는 #656 은 내용 있는 kappa 하나(코드를 지우지 않음)", [ln for ln in got if _GROUP_LINE.match(ln)],
           [f"[#656] {SV}kappa/__init__.py: {fg.UNDO.format('kappa')}"])
    # B10 — 묶음이 아닌 빈 `__init__.py`(마이그레이션 패키지 표지)를 지우면 red
    mig, anchor = _debt_repo(td / "b10", {"application/orbit/migrations/__init__.py": ""})
    folder = _folder(mig, "b10", anchor, scope=_scope("ⓐ"))
    vc, reds, _out = _window(scripts, mig, folder, 1, "--debt",
                             edit=lambda r: (r.root / "application/orbit/migrations/__init__.py").unlink())
    run.eq("B10 묶음 아닌 빈 `__init__` 지움은 red", (vc, reds), (2, [
        "red: 창 안 다른 변화 `application/orbit/migrations/__init__.py` — 묶음 창은 이동 · import 치환 · 빈 묶음 "
        "`__init__` · 설정 파일 경로 치환만 받는다"]))


def scen_review_clash(fg, scripts: Path, run: Run, td: Path) -> None:
    """A8 — 이름 겹침이면 draft · verify --run 이 보이고 apply 는 멈춘다."""
    repo = Repo(td / "clash")
    repo.write({SV + "__init__.py": "", SV + "x/__init__.py": "", SV + "x/tarot.py": _vo("tarot"),
                SV + "tarot.py": _vo("tarot"), SV + "moon.py": _vo("moon")})
    folder = _folder(repo, "k1", repo.commit("앵커"))
    line = f"기계 이동 불가 이름 겹침 {SV}tarot.py {SV}x/tarot.py"
    rc, out = _tool(scripts, "draft", repo.root, "--bc", "orbit", "--run", folder)
    run.eq("A8 draft 가 이름 겹침을 냄", (rc, _lines_of(out, "기계 이동 불가")), (0, [line]))
    rc, out = _tool(scripts, "apply", repo.root, "--run", folder, "--run-moves")
    run.eq("A8 apply 멈춤", (rc, _lines_of(out, "기계 이동 불가", "이동 ")), (1, [line]))
    run.true("A8 멈추면 옮기지 않음", (repo.root / SV / "x/tarot.py").is_file() and (repo.root / SV / "tarot.py").is_file())
    rc, out = _tool(scripts, "verify", repo.root, "--run", folder)
    run.eq("A8 verify --run 이 이름 겹침을 보임", (rc, _lines_of(out, "기계 이동 불가", "red")), (0, [line]))


def scen_review_encoding(fg, scripts: Path, run: Run, td: Path) -> None:
    """S1 — UTF-8 아닌 소스(인코딩 선언 latin-1)는 검사기처럼 빈 글로 센다 · 그 파일이 옮길 모듈을 부르면 apply 는 멈춘다."""
    def svc(name: str, ret: str, mod: str, latin: bool = False) -> bytes:
        head = "# -*- coding: latin-1 -*-\n# caf\xe9\n" if latin else ""
        text = head + f'"""{name}."""\nfrom {PKG}.{mod} import {ret}\n\n\ndef {name}(x: str) -> {ret}:\n    return {ret}(x)\n'
        return text.encode("latin-1" if latin else "utf-8")

    repo = Repo(td / "latin")
    repo.write({SV + "__init__.py": "", SV + "moon_phase.py": _vo("moon_phase"), SV + "relation/__init__.py": "",
                **{SV + f"relation/relation_{x}.py": _vo(f"relation_{x}") for x in "abc"}, DS + "__init__.py": ""})
    for x in "abc":
        (repo.root / DS / f"resolve_star_{x}.py").write_bytes(
            svc(f"resolve_star_{x}", f"Relation{x.upper()}", f"relation.relation_{x}", latin=x == "c"))
    (repo.root / DS / "compute_moon_phase.py").write_bytes(svc("compute_moon_phase", "MoonPhase", "moon_phase"))
    folder = _folder(repo, "e1", repo.commit("앵커"))
    rc, out = _tool(scripts, "draft", repo.root, "--bc", "orbit", "--run", folder)
    _code, got, _tail = _checker(scripts, "check-domain-model.py", repo.root)
    run.eq("S1 UTF-8 아닌 서비스 — 도구 줄 = 검사기 줄(반환을 못 읽은 것으로)",
           (rc, _lines_of(out, "줄 "), [ln for ln in got if _GROUP_LINE.match(ln)]), (0, [], []))
    repo = Repo(td / "latin-apply")
    repo.write({SV + "__init__.py": "", SV + "moon_phase.py": _vo("moon_phase"), SV + "void_a.py": _vo("void_a"),
                SV + "void_b.py": _vo("void_b")})
    user = "application/orbit/application_layer/use_void.py"
    (repo.root / user).parent.mkdir(parents=True)
    (repo.root / user).write_bytes(f"# -*- coding: latin-1 -*-\n# caf\xe9\nfrom {PKG}.void_a import VoidA\n".encode("latin-1"))
    folder = _folder(repo, "e2", repo.commit("앵커"))
    repo.write({SV + "void_c.py": _vo("void_c")})
    repo.commit("슬라이스")
    rc, out = _tool(scripts, "apply", repo.root, "--run", folder, "--run-moves")
    run.eq("S1 UTF-8 아닌 소스가 옮길 모듈을 부르면 apply 멈춤", (rc, _lines_of(out, "기계 이동 불가", "이동 ")),
           (1, [f"기계 이동 불가 {user}:1 UTF-8 아닌 소스"]))
    run.true("S1 멈추면 옮기지 않음", (repo.root / SV / "void_a.py").is_file())


def scen_review_leftover(fg, scripts: Path, run: Run, td: Path) -> None:
    """S2 — 푸는 묶음 폴더에 `.py` 아닌 파일이 남으면(지울 수 없다 — 폴더가 남아 검사기가 그 묶음을 본다) apply 는 멈춘다."""
    repo = Repo(td / "leftover")
    repo.write({SV + "__init__.py": "", SV + "moon_phase.py": _vo("moon_phase"), SV + "star_dust.py": _vo("star_dust"),
                SV + "void/__init__.py": "", SV + "void/void_a.py": _vo("void_a"), SV + "void/void_b.py": _vo("void_b"),
                SV + "void/notes.md": "메모\n"})
    folder = _folder(repo, "o1", repo.commit("앵커"))
    (repo.root / SV / "void/void_b.py").unlink()
    repo.commit("슬라이스")
    line = f"기계 이동 불가 {SV}void/notes.md:1 푸는 묶음 폴더의 .py 아닌 파일"
    rc, out = _tool(scripts, "draft", repo.root, "--bc", "orbit", "--run", folder)
    run.eq("S2 draft 가 남는 파일을 냄", (rc, _lines_of(out, "기계 이동 불가")), (0, [line]))
    rc, out = _tool(scripts, "apply", repo.root, "--run", folder, "--run-moves")
    run.eq("S2 apply 멈춤", (rc, _lines_of(out, "기계 이동 불가", "이동 ")), (1, [line]))
    run.true("S2 멈추면 옮기지 않음", (repo.root / SV / "void/void_a.py").is_file())


def scen_review_notice(fg, scripts: Path, run: Run, td: Path) -> None:
    """A9 — 알림 묶음의 형성 · 해체 · 다시 놓기는 이 실행이 옮기는 파일을 정확히 나눈다(해체 묶음에서 새 묶음으로 가는 파일은 형성)."""
    repo = Repo(td / "notice")
    repo.write({SV + "__init__.py": "", SV + "moon/__init__.py": "", SV + "moon/moon_a.py": _vo("moon_a"),
                SV + "moon/void_moon.py": _vo("void_moon"), SV + "star_dust.py": _vo("star_dust")})
    folder = _folder(repo, "n1", repo.commit("앵커"))
    repo.write({SV + "void_b.py": _vo("void_b"), SV + "void_c.py": _vo("void_c")})
    repo.commit("슬라이스")
    rc, out = _tool(scripts, "draft", repo.root, "--bc", "orbit", "--run", folder)
    run.eq("A9 알림 묶음 — 형성 1 · 해체 1 · 다시 놓기 0 (합 = 이동 2)", (rc, _lines_of(out, "알림 묶음")), (0, [
        "알림 묶음: 새 파일 2 · 이 실행의 이동 2(형성 1 · 해체 1 · 다시 놓기 0) · 경로 결속 0 · 다른 BC import 0"]))


def scen_review_windows(fg, scripts: Path, run: Run, td: Path) -> None:
    """B4 — red 창을 철회하고 다시 연 창이 green 이면 verify --run 은 그 red 창에 묶이지 않는다(dddjango.md «그 창을 철회하고
    … 다시 연다»). 철회 없이 남은 red 창의 이동은 «창 밖 이동» 이 잡는다."""
    repo = Repo(td / "withdraw")
    repo.write({SV + "__init__.py": "", SV + "moon_phase.py": _vo("moon_phase"), SV + "void_a.py": _vo("void_a"),
                SV + "void_b.py": _vo("void_b")})
    folder = _folder(repo, "w", repo.commit("앵커"))
    repo.write({SV + "void_c.py": _vo("void_c")})
    base = repo.commit("슬라이스")
    vc, reds, _out = _window(scripts, repo, folder, 1, "--run-moves",
                             edit=lambda r: r.write({SV + "moon_phase.py": _vo("moon_phase") + "# 기능 편집\n"}))
    run.eq("B4 w1 섞인 창 red", vc, 2)
    keep = td / "withdraw-records"
    shutil.copytree(repo.root / ".dddjango", keep)
    repo.git("reset", "-q", "--hard", base)
    shutil.rmtree(repo.root / ".dddjango")
    shutil.copytree(keep, repo.root / ".dddjango")
    repo.commit("w1 철회(제품 편집만)")
    rc, out = _tool(scripts, "verify", repo.root, "--run", folder)
    run.true("B4 철회만 하고 다시 열기 전 — red 창이 남음", rc == 2 and "red: red 묶음 창 w1 — 그 창을 철회하고 다시 연다" in out,
             str(out[-3:]))
    vc, reds, _out = _window(scripts, repo, folder, 2, "--run-moves")
    run.eq("B4 다시 연 w2 green", (vc, reds), (0, []))
    rc, out = _tool(scripts, "verify", repo.root, "--run", folder)
    run.eq("B4 다시 연 창이 green 이면 verify --run green", (rc, _lines_of(out, "red")), (0, []))


def scen_review_promotion(fg, scripts: Path, run: Run, td: Path) -> None:
    """B5 — 승격 폴더는 통째로 옮겨진다 — expected_moves 도 그 폴더의 모든 파일 쌍을 낸다(`_expand` 와 같이)."""
    repo = Repo(td / "promo")

    def svc(name: str, ret: str, mod: str) -> str:
        return (f'"""{name}."""\nfrom {PKG}.{mod} import {ret}\n\n\n'
                f"def {name}(x: str) -> {ret}:\n    return {ret}(x)\n")

    repo.write({SV + "__init__.py": "", SV + "relation/__init__.py": "", SV + "moon_phase.py": _vo("moon_phase"),
                **{SV + f"relation/relation_{x}.py": _vo(f"relation_{x}") for x in "abc"},
                DS + "__init__.py": "", DS + "resolve_relation_a.py": svc("resolve_relation_a", "RelationA",
                                                                           "relation.relation_a"),
                DS + "compute_moon_phase.py": svc("compute_moon_phase", "MoonPhase", "moon_phase"),
                DS + "resolve_ghost/__init__.py": "",
                DS + "resolve_ghost/resolve_ghost.py": svc("resolve_ghost", "RelationC", "relation.relation_c"),
                DS + "resolve_ghost/ghost_part.py": '"""부품."""\n\nGHOST: str = "x"\n'})
    folder = _folder(repo, "p1", repo.commit("앵커"))
    repo.write({DS + "resolve_relation_b.py": svc("resolve_relation_b", "RelationB", "relation.relation_b")})
    repo.commit("슬라이스")
    run.eq("B5 expected_moves — 승격 폴더의 모든 파일", fg.expected_moves(repo.root, folder), {
        DS + "resolve_ghost/__init__.py": DS + "relation/resolve_ghost/__init__.py",
        DS + "resolve_ghost/ghost_part.py": DS + "relation/resolve_ghost/ghost_part.py",
        DS + "resolve_ghost/resolve_ghost.py": DS + "relation/resolve_ghost/resolve_ghost.py",
        DS + "resolve_relation_a.py": DS + "relation/resolve_relation_a.py"})


def scen_review_symlink(fg, scripts: Path, run: Run, td: Path) -> None:
    """B7 — 손대지 않은 추적 심링크는 창 안 변화가 아니다(양쪽 모두 링크 글 = git blob · 링크 너머를 읽지 않는다)."""
    repo, _anchor = _debt_repo(td / "link", {"CLAUDE.md": "규칙\n"})
    (repo.root / "AGENTS.md").symlink_to("CLAUDE.md")
    folder = _folder(repo, "l", repo.commit("링크"), scope=_scope("ⓐ"))
    data = fg.worktree_bytes(repo.root).get("AGENTS.md")
    run.eq("B7 worktree_bytes — 링크 글(blob 지문 = git)", (data, fg.blob_oid(data or b"")),
           (b"CLAUDE.md", repo.git("rev-parse", "HEAD:AGENTS.md")))
    vc, reds, _out = _window(scripts, repo, folder, 1, "--debt")
    run.eq("B7 손대지 않은 심링크 — 창 판정 green", (vc, reds), (0, []))


def scen_review_subfolder(fg, scripts: Path, run: Run, td: Path) -> None:
    """B3 계약 — 하위 폴더 프로젝트 · 커밋하지 않는 실행. 창 열기 기록의 dirty 키는 git 뿌리 기준 경로 · 내용은 git 뿌리에서
    읽은 바이트다(behavior_guard 쪽 고침의 계약). 그 기록이면 folder_group 의 창 판정 · verify --run 은 green 이다."""
    import base64
    import hashlib
    repo = Repo(td / "sub-nc", "proj")
    repo.write({SV + "__init__.py": "", SV + "moon_phase.py": _vo("moon_phase"), SV + "void_a.py": _vo("void_a"),
                SV + "void_b.py": _vo("void_b")})
    folder = _folder(repo, "nc", repo.commit("앵커"))
    repo.write({SV + "void_c.py": _vo("void_c"), SV + "moon_phase.py": _vo("moon_phase") + "\nPHASES: int = 8\n"})
    rc, text = _guard(scripts, repo, folder, "open", "--kind", "code", "--mode", "feature")
    opened = next((folder / "behavior").rglob("w1-open.json"))
    record = json.loads(opened.read_text(encoding="utf-8"))
    for key in record["dirty"]:
        f = repo.git_root / key
        data = f.read_bytes() if f.is_file() else None
        record["dirty"][key] = {"sha": None} if data is None else {
            "sha": hashlib.sha256(data).hexdigest(), "b64": base64.b64encode(data).decode("ascii")}
    opened.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    _tool(scripts, "apply", repo.root, "--run", folder, "--run-moves")
    _guard(scripts, repo, folder, "close")
    vc, vout = _tool(scripts, "verify", repo.root, "--run", folder, "--window", "1")
    rc2, out2 = _tool(scripts, "verify", repo.root, "--run", folder)
    run.eq("B3 계약 — 하위 폴더 · 미커밋 창 green", (rc, vc, _lines_of(vout, "red"), rc2, _lines_of(out2, "red")),
           (0, 0, [], 0, []))


# ── 진입 ──────────────────────────────────────────────────────────────────────

def run_all(scripts: Path, fail_fast: bool = False) -> "tuple[Run, object]":
    fg = _load(scripts)
    run = Run()
    steps = (("낱말", lambda td: check_words(fg, scripts, run)), ("픽스처", lambda td: check_cases(fg, run, td)),
             ("검토 메모리", lambda td: check_review_memory(fg, run)),
             ("병합", lambda td: scen_merge(fg, scripts, run, td)), ("다시 옮김", lambda td: scen_chain(fg, scripts, run, td)),
             ("빚", lambda td: scen_debt(fg, scripts, run, td)), ("이관 빚", lambda td: scen_legacy(fg, scripts, run, td)),
             ("검토 범위", lambda td: scen_review_scope(fg, scripts, run, td)),
             ("검토 풀기", lambda td: scen_review_dissolve(fg, scripts, run, td)),
             ("검토 겹침", lambda td: scen_review_clash(fg, scripts, run, td)),
             ("검토 인코딩", lambda td: scen_review_encoding(fg, scripts, run, td)),
             ("검토 남는 파일", lambda td: scen_review_leftover(fg, scripts, run, td)),
             ("검토 알림", lambda td: scen_review_notice(fg, scripts, run, td)),
             ("검토 창", lambda td: scen_review_windows(fg, scripts, run, td)),
             ("검토 승격", lambda td: scen_review_promotion(fg, scripts, run, td)),
             ("검토 링크", lambda td: scen_review_symlink(fg, scripts, run, td)),
             ("검토 하위 폴더", lambda td: scen_review_subfolder(fg, scripts, run, td)),
             ("검사기", lambda td: check_checkers(fg, scripts, run, td)))
    with tempfile.TemporaryDirectory(prefix="fg-fixture-") as tmp:
        for name, step in steps:
            td = Path(tmp) / name
            td.mkdir()
            try:
                step(td)
            except Exception as exc:  # 시험 대상의 예외도 red 로 센다(변이가 깨뜨린 경로)
                run.fails.append(f"{name} 예외: {exc!r}")
            if fail_fast and run.fails:
                break
    return run, fg


def _py39_compare(python: str, scripts: Path, run: Run) -> None:
    me = Path(__file__).resolve()
    outs = []
    for py in (python, sys.executable):
        proc = subprocess.run([py, str(me), "--emit", "--scripts", str(scripts)], capture_output=True)
        if proc.returncode != 0:
            run.fails.append(f"불변식 8 {py} --emit 실패: {proc.stderr.decode('utf-8', 'replace')[-600:]}")
            return
        outs.append(proc.stdout)
    run.true("불변식 8 — 두 판 출력 바이트 같음", outs[0] == outs[1],
             f"{python} 과 {sys.executable} 의 --emit 이 다르다")


# (이름, 옛 글, 새 글) — 옛 글은 folder_group.py 에 정확히 한 번 있어야 한다. 계획 «단계 1 변이 회귀» + 규칙 행마다 하나.
_MUTATIONS: "tuple[tuple[str, str, str], ...]" = (
    # 셈 · 자리
    ("형성 문턱 3→2", "FORM_MIN: int = 3", "FORM_MIN: int = 2"),
    ("유지 문턱 2→1", "KEEP_MIN: int = 2", "KEEP_MIN: int = 1"),
    ("머리 자리도 후보 · 맨 자리로 셈", 'return i == 0 or kinds[i - 1] != "modifier"', "return True"),
    ("머리 자리도 형성 닻으로 셈",
     'anchored: int = sum(1 for a in got if a.anchor in ("bare", "phrase", "return"))',
     'anchored: int = sum(1 for a in got if a.anchor in ("bare", "phrase", "return", "head"))'),
    ("주인 = 가장 긴 것을 오른쪽에서", "owner, at = matches[0]",
     "owner, at = max(reversed(matches), key=lambda x: len(x[0]))"),
    ("죽을 묶음을 한 바퀴에 모두 뺌",
     "worst = min(bad, key=lambda b: (slots[b[1]].service, b[0], b[1], b[2]))\n        live[worst[1]].discard(worst[3])",
     "for worst in bad:\n            live[worst[1]].discard(worst[3])"),
    ("E3 행 지움", "if why is None and len(realized) == 1 and parent_count == 0:", "if False:"),
    ("M3 행 지움", "if why is None and slots[parent].service and g in svc_stems.get(parent, set()):", "if False:"),
    ("닻 없음 행 지움", 'elif not any(a.anchor in ("bare", "phrase", "head", "return") for a in got):', "elif False:"),
    ("자기 애그리거트 구도 단위", 'if "_" in a and not all(w in domain for w in a.split("_")))', 'if "_" in a)'),
    ("서비스 칸이 값 객체 칸 단위를 모름", "universe[parent] |= vo_side", "universe[parent] |= set()"),
    ("서비스 반환이 예외 클래스도 셈", "and not index.is_exception(*ref):", ":"),
    ("dict 반환에서 키 타입도 셈", "args = args[-1:]", "args = args"),
    ("부모에 있는 반환 값 객체를 무시", "if len(locs) == 1 and None not in locs:", "if len(locs - {None}) == 1:"),
    ("두 묶음으로 갈린 반환을 한 묶음으로", "if len(locs) == 1 and None not in locs:", "if locs and None not in locs:"),
    ("쓰는 곳에 돌려주는 서비스 자신도 셈", "continue  # 그 파일을 돌려주는 서비스 자신은 뺀다", "pass"),
    ("쓰는 곳 묶음이 죽었어도 따라감", 'if g is not None and tuple(g.split("_")) in live[m.slot.parent]:',
     "if g is not None:"),
    # 낱말 종류
    ("뜻 있는 낱말 파일도 C7 대상(E7 무시)", "elif any(k in MEANINGFUL for k in w.kinds):", "elif False:"),
    ("FORBIDDEN 도 복수 접기", "if word in NOT_PLURAL or word in FORBIDDEN:", "if word in NOT_PLURAL:"),
    ("복수 접기가 단수 확인 없이", 'and not word.endswith(("ss", "us", "is")) and word[:-1] in words:',
     'and not word.endswith(("ss", "us", "is")):'),
    ("AMBIGUOUS 를 STOPWORDS 합치기 전에 뺌", "(GENERAL | STOPWORDS) - AMBIGUOUS", "(GENERAL - AMBIGUOUS) | STOPWORDS"),
    ("order · plan 을 VERBS 에 남김", 'FINAL_VERBS: "frozenset[str]" = VERBS - AMBIGUOUS',
     'FINAL_VERBS: "frozenset[str]" = VERBS | frozenset({"order", "plan"})'),
    ("서비스 앞 동사 떼기에 따로 목록", 'if t and word_kind(t[0], ctx.domain) == "verb":',
     'if t and t[0] in (VERBS | {"order", "plan"}):'),
    ("역할 낱말 떼지 않음", "t = [w for w in t if w not in ROLE]", "t = list(t)"),
    ("조합 ⓐ(영역+업무) 허용", 'if all(k == "domain" for k in pre) and head == "business":', "if False:"),
    ("있는 묶음 홀로 일반어도 단위", 'return kinds[0] == "business"', 'return kinds[0] in ("business", "general")'),
    # 합침 없음(C6′)
    ("글자 포함 철자 합침", "return tokens[i:i + len(unit)] == unit",
     "return tokens[i:i + len(unit)] == unit or (len(unit) > 1 and tokens[i] == unit[-1])"),
    # git · 이동
    ("base_tree HEAD 조건(병합이 지운 옛 경로가 남음)", "if t1.get(p) != after and after == t2.get(p):",
     "if t1.get(p) != after and after == t2.get(p) and after is not None:"),
    ("actual_moves 가 내용 같음을 요구(git 유사도 이름 바꿈 대용)",
     "if len(olds) == 1 and len(news) == 1 and olds[0].group != news[0].group:",
     "if len(olds) == 1 and len(news) == 1 and olds[0].group != news[0].group "
     "and old[olds[0].path] == new[news[0].path]:"),
    ("T₀′ blob 읽기에서 접두를 뺌", "prefix: str = git_prefix(root)  # 하위 폴더 프로젝트 접두(검토 M5)",
     'prefix: str = ""  # 하위 폴더 프로젝트 접두(검토 M5)'),
    ("ⓐ′ 도 정리로 셈", 'if m is None or m.group(2) != "ⓐ":', 'if m is None or not m.group(2).startswith("ⓐ"):'),
    ("앞 실행 절의 결정도 읽음", 'scope_text.split("# 앞 실행", 1)[0]', "scope_text"),
    ("ⓐ 결정 줄을 읽지 않음",
     "if any(text in h for h in heads) or any(text in row and _row_id(row) in ids for row in current):", "if False:"),
    ("미룬 빚도 이 실행이 옮김(② 없음)", "final[k] = debt_m[k].path  # ② B 자리 그대로",
     "final[k] = fp.target  # ② B 자리 그대로"),
    ("창 판정 — sha 만 남은 설정 파일을 판정 불가로 보지 않음", "if p in sha_only:", "if False:"),
    ("창 판정 — 섞인 편집을 받음", 'reds.append(f"창 안 다른 변화', '(lambda *_: None)(f"창 안 다른 변화'),
    ("창 판정 — 설정 파일 경로 치환을 받지 않음", "if p in CONFIG_FILES and sub is not None and sub(before) == after:",
     "if False:"),
    ("verify --run 이 창 밖 이동을 받음", "if pos != c:", "if False:"),
    ("상대 import 깊이 하나 모자람", 'return len(n) - c + 1, ".".join(t[c:])', 'return len(n) - c, ".".join(t[c:])'),
    ("from 패키지 import 모듈 나눔 없음", "if len(groups) == 1:", "if True:"),
    ("문자열 속 점 경로 치환 없음",
     "elif (string_sub is not None and isinstance(node, ast.Constant) and isinstance(node.value, str)",
     "elif (False and isinstance(node, ast.Constant) and isinstance(node.value, str)"),
    ("계산된 import 를 막지 않음", "if hits_package(pieces):", "if False:"),
    ("새 묶음에 빈 __init__.py 를 만들지 않음(불변식 2 — #655)", 'out.setdefault(f"{d}/__init__.py", "")', "pass"),
    ("앵커에도 서는 묶음을 이 실행의 형성으로 셈(D2)", "(bset | ((g1 - g0p) - held)) - ((bset & g0p) - g1)",
     "(bset | (g1 - held)) - ((bset & g0p) - g1)"),
    ("⓪ «만든다» 이관 빚도 형성으로 셈", "(bset | ((g1 - g0p) - held)) - ((bset & g0p) - g1)",
     "(bset | (g1 - g0p)) - ((bset & g0p) - g1)"),
    ("⓪ 새 파일은 이관 빚 고정 없음", "if any(sub in ln for sub in legacy_list for ln in own_lines):",
     "if k in debt_m and any(sub in ln for sub in legacy_list for ln in own_lines):"),
    # 검토 고침(2.28.0 검토 A · B · S) — 고침을 되돌린다
    ("A1 «푼다» 만 골라도 미룬 «만든다» 자리로", "debt_pairs.append((path, fp.member.flat))",
     "debt_pairs.append((path, fp.target))"),
    ("A2 도구 범위 — domain_layer 를 아무 깊이에서 찾음(web · 시험 거울)",
     'parts: "list[str]" = path.split("/")\n    if len(parts) < 4 or parts[0] != "application" or parts[2] != LAYER:',
     'parts: "list[str]" = path.split("/")\n    if LAYER in parts[1:-1]:\n        return parts[parts.index(LAYER) - 1]\n'
     '    if len(parts) < 4 or parts[0] != "application" or parts[2] != LAYER:'),
    ("A3 drops 무시(이미 빈 묶음을 못 풂)", "init in drop_set or any(old.startswith(d + \"/\") for old in where)):",
     "any(old.startswith(d + \"/\") for old in where)):"),
    ("A3 placement_drops 없음", 'out.append(f"{parent}/{g}/__init__.py")\n    return out', "pass\n    return out"),
    ("A3 실행 계획 drops 없음", "drops=_run_drops(now, current, final, s_groups)", "drops=[]"),
    ("A4 빈 init = 0바이트만", "if rest == [init] and empty_init(out[init]) and (", 'if rest == [init] and out[init] == "" and ('),
    ("A4 창 판정 — docstring init 지움을 받지 않음", "and empty_init(before) \\", 'and before == "" \\'),
    ("B10 창 판정 — 묶음 아닌 빈 __init__ 지움도 받음", "and d in then_dirs and d not in now_dirs:", "and d not in now_dirs:"),
    ("A5 영역 낱말만으로 된 이웃 애그리거트 구도 단위", 'if "_" in a and not all(w in domain for w in a.split("_")))',
     'if "_" in a and a != slot.agg)'),
    ("A6 서비스 이름 사전 = 서비스 칸 live 전부", "hit = _match(w, names)", "hit = _match(w, live)"),
    ("A6 반환으로 서는 묶음을 이름 사전에서 뺌", 'mine: "set[Tuple[str, ...]]" = own.get(parent, set()) | {tuple(g.split("_")) for g in ret_groups}',
     'mine: "set[Tuple[str, ...]]" = own.get(parent, set())'),
    ("A6 죽음 차례 — 값 객체 칸 먼저 없음", "key=lambda b: (slots[b[1]].service, b[0], b[1], b[2])",
     "key=lambda b: (b[0], b[1], b[2])"),
    ("A7 모듈 조각 뒤 공백 · 역슬래시까지 바꿈", "lines.byte_of(toks[a_tok].start), lines.byte_of(toks[b_tok].end)",
     "lines.byte_of(toks[a_tok].start), lines.byte_of(toks[b_tok + 1].start)"),
    ("A7 `from .import` 띄움 없음", 'rep += b" "', 'rep += b""'),
    ("A7 한 줄 복합문 · 역슬래시 나눔을 막지 않음", 'why: "Optional[str]" = _split_block(toks, i, j)', 'why: "Optional[str]" = None'),
    ("A7 나눔이 주석을 버림", "if not any(t.type == tokenize.COMMENT for t in toks[i:j + 1]):", "if True:"),
    ("A7 hazards 가 못 고치는 나눔을 안 냄",
     'blocked += [f"{path}:{line} {why}" for line, why in rewrite_blocks(text, path, where.get(path, path), moves)]',
     "pass"),
    ("A8 계획이 이름 겹침을 모름",
     'clash: "set[Tuple[str, str]]" = set(_clash_keys(t0)) | set(_clash_keys(t0p)) | set(_clash_keys(now))',
     'clash: "set[Tuple[str, str]]" = set()'),
    ("A8 placement_moves 가 겹친 둘을 옮김", "if fp.target == path or _key(fp.member) in clash:\n            continue\n        unit",
     "if fp.target == path:\n            continue\n        unit"),
    ("A8 apply 가 이름 겹침에 멈추지 않음",
     'stops: "list[str]" = (hz.blocked + _disk_blocks(root, undecodable, full, drops, all_paths)\n'
     '                          + [f"이름 겹침 {a} {b}" for a, b in plan.clashes])',
     'stops: "list[str]" = (hz.blocked + _disk_blocks(root, undecodable, full, drops, all_paths))'),
    ("A9 알림 셈이 형성 · 해체를 겹쳐 셈", "        elif (k[0], _group_of(plan.debt[k])) in plan.dissolved:",
     "        if (k[0], _group_of(plan.debt[k])) in plan.dissolved:"),
    ("B4 red 창은 다시 연 green 창 뒤에도 red",
     '\n                        and not any(m > n and last[m]["verdict"] == "green" for m in last)]', "]"),
    ("B5 expected_moves 가 승격 부품을 뺌", "return dict(_expand(plan.pairs(plan.anchor, plan.final), run.anchor_paths))",
     "return dict(plan.pairs(plan.anchor, plan.final))"),
    ("B7 심링크를 건너뜀", "        if f.is_symlink():\n            out[rel] = os.fsencode", "        if False:\n            out[rel] = os.fsencode"),
    ("S1 UTF-8 아닌 소스를 바꿔 읽음", "    try:\n        return data.decode(\"utf-8\")\n    except UnicodeDecodeError:\n        return \"\"",
     "    return data.decode(\"utf-8\", \"replace\")"),
    ("S1 UTF-8 아닌 소스를 막지 않음", 'out.append(f"{p}:1 UTF-8 아닌 소스")', "pass"),
    ("S2 푸는 묶음 폴더에 남는 파일을 막지 않음", 'out.append(f"{rest[0]}:1 푸는 묶음 폴더의 .py 아닌 파일")', "pass"),
    ("S3 파서 «너무 깊음» 을 잡지 않음", "except (SyntaxError, ValueError, RecursionError, MemoryError):",
     "except (SyntaxError, ValueError):"),
)


def mutation_test(scripts: Path) -> int:
    src_path: Path = scripts / "folder_group.py"
    src: str = src_path.read_text(encoding="utf-8")
    survived: "list[str]" = [] if _MUTATIONS else ["변이 표가 비었다"]

    def one(item: "tuple[str, str, str]") -> "tuple[str, str]":
        name, old, new = item
        if src.count(old) != 1:
            return name, f"변이 지점이 정확히 한 곳이 아니다({src.count(old)}) — 변이 표를 코드에 맞춰라"
        with tempfile.TemporaryDirectory(prefix="fg-mutant-") as tmp:
            copy = Path(tmp) / "scripts"
            shutil.copytree(scripts, copy, symlinks=False, ignore=shutil.ignore_patterns("__pycache__"))
            (copy / "folder_group.py").write_text(src.replace(old, new, 1), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--scripts", str(copy),
                                   "--fail-fast"], capture_output=True, text=True)
        if proc.returncode == 0:
            return name, "변이가 살아남음(픽스처가 못 잡는다)"
        if "[folder_group] red" not in proc.stdout:
            return name, f"변이가 러너를 깨뜨림(red 판정이 아님) — {proc.stderr.strip()[-300:]}"
        return name, ""

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 2)) as pool:
        for name, why in pool.map(one, _MUTATIONS):
            if why:
                survived.append(f"{name}: {why}")
            else:
                print(f"  죽음 {name}")
    if survived:
        print(f"[mutation] 생존 변이 {len(survived)}건", file=sys.stderr)
        for s in survived:
            print(f"  {s}", file=sys.stderr)
        return 2
    print(f"[mutation] 변이 {len(_MUTATIONS)}종 모두 red — 픽스처 검출력 확인")
    return 0


def main(argv: "list[str]") -> int:
    scripts: Path = DEFAULT_SCRIPTS
    py39: "str | None" = None
    require: "str | None" = None
    mode: str = "run"
    fail_fast: bool = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--scripts":
            scripts = Path(argv[i + 1]).resolve()
            i += 2
        elif a == "--py39":
            py39 = argv[i + 1]
            i += 2
        elif a == "--require":
            require = argv[i + 1]
            i += 2
        elif a in ("--emit", "--mutation-test"):
            mode = a[2:]
            i += 1
        elif a == "--fail-fast":
            fail_fast = True
            i += 1
        else:
            print(__doc__, file=sys.stderr)
            return 1
    if mode == "emit":
        sys.stdout.write(emit(_load(scripts)))
        return 0
    if mode == "mutation-test":
        return mutation_test(scripts)
    if require is not None and f"{sys.version_info[0]}.{sys.version_info[1]}" != require:
        print(f"[folder_group] red — 이 다리는 Python {require} 이어야 한다(지금 {sys.version.split()[0]})")
        return 1
    run, _fg = run_all(scripts, fail_fast)
    if py39 is not None:
        _py39_compare(py39, scripts, run)
    if run.fails:
        print(f"[folder_group] red {len(run.fails)}건 · 통과 {run.passed} · Python {sys.version.split()[0]}")
        for f in run.fails:
            print(f"  ✖ {f}")
        return 1
    print(f"[folder_group] green — 확인 {run.passed} · Python {sys.version.split()[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
