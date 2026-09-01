#!/usr/bin/env python3
"""pre-gate 프로토타입 (④ 백테스트 전용 — 배포물 아님).

설계 v2 D1/D2의 최소 구현: archive+init 격리 사본 → 팬텀 스텁 실체화 →
registry_gate --anchor HEAD → 귀속 목록 파싱.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

PLUGIN_SCRIPTS = Path.home() / "Desktop/dddjango/dddjango/scripts"
FORBIDDEN_SEGMENTS = {"build", "dist", "staticfiles", "node_modules", "site-packages", "venv", ".dddjango"}

# 베이스 토큰 → import 문 합성 (②상수-배선형 화이트리스트의 일부)
BASE_IMPORTS: dict[str, str] = {
    "ABC": "from abc import ABC, abstractmethod",
    "TestCase": "from django.test import TestCase",
    "TransactionTestCase": "from django.test import TransactionTestCase",
    "StrEnum": "from enum import StrEnum",
    "IntEnum": "from enum import IntEnum",
    "Enum": "from enum import Enum",
    "Schema": "from ninja import Schema",
    "BaseModel": "from pydantic import BaseModel",
    "Exception": "",
    "AppConfig": "from django.apps import AppConfig",
}


@dataclass
class PlanFile:
    path: str
    tag: str  # add|update|remove|empty
    symbols: list[dict] = field(default_factory=list)  # {name, base, fields, kind}
    imports: list[str] = field(default_factory=list)
    signals: dict | None = None  # {markers, base, client}
    raises: list[str] = field(default_factory=list)  # 예외 번역표 합성


def _class_stub(sym: dict) -> str:
    name = sym["name"]
    base = sym.get("base") or ""
    head = f"class {name}({base}):" if base else f"class {name}:"
    lines = [head, '    """계획 스텁."""']
    body: list[str] = []
    for fname, ftype in (sym.get("fields") or {}).items():
        body.append(f"    {fname}: {ftype}")
    for _kind, code in (sym.get("fieldlines") or []):
        body.append(f"    {code}")
    for meth in (sym.get("methods") or []):
        params = meth.get("params", "")
        ret = meth.get("ret") or "object"
        sig = f"self, {params}" if params else "self"
        body.append(f"    def {meth['name']}({sig}) -> {ret}:")
        body.append("        raise NotImplementedError")
    lines.extend(body if body else ["    ..."])
    return "\n".join(lines)


def render_stub(pf: PlanFile) -> str:
    lines: list[str] = ['"""pre-gate 팬텀 스텁."""', "from __future__ import annotations", ""]
    bases_seen: set[str] = set()
    for sym in pf.symbols:
        b = (sym.get("base") or "").split(".")[-1].split("[")[0]
        if b and b in BASE_IMPORTS and BASE_IMPORTS[b] and b not in bases_seen:
            lines.append(BASE_IMPORTS[b])
            bases_seen.add(b)
    for mod in pf.imports:
        lines.append(mod if mod.startswith(("from ", "import ")) else f"import {mod}")
    sig = pf.signals or {}
    if sig.get("markers"):
        lines.append("import pytest")
    lines.append("")
    if sig.get("markers"):
        marks = ", ".join(f"pytest.mark.{m}" for m in sig["markers"])
        lines.append(f"pytestmark: list = [{marks}]")
        lines.append("")
    for sym in pf.symbols:
        if sym.get("kind") == "function":
            lines.append(f"def {sym['name']}() -> None:")
            lines.append('    """계획 스텁."""')
            lines.append("    raise NotImplementedError")
        else:
            lines.append(_class_stub(sym))
        lines.append("")
    for exc in pf.raises:
        lines.append(f"def _pregate_raise_{exc.lower()}() -> None:")
        lines.append('    """예외 번역표 합성(§D2 — #456 진탐 보존)."""')
        lines.append(f"    raise {exc}()")
        lines.append("")
    if sig.get("client") or "/test/e2e/" in pf.path:
        lines.append("def test_planned_client_flow(client) -> None:")
        lines.append('    """계획 스텁 — 입구 통과 규약 상수."""')
        lines.append('    client.get("/")')
        lines.append("    raise NotImplementedError")
        lines.append("")
    if not pf.symbols and not pf.raises and not sig:
        lines.append("")
    return "\n".join(lines) + "\n"


def validate_paths(files: list[PlanFile]) -> list[str]:
    errs = []
    for pf in files:
        parts = Path(pf.path).parts
        if any(p in FORBIDDEN_SEGMENTS or p.startswith(".") for p in parts):
            errs.append(f"경로 거절: {pf.path}")
        if pf.tag not in ("add", "update", "remove", "empty"):
            errs.append(f"태그 불명: {pf.path} {pf.tag}")
    return errs


sys.path.insert(0, str(PLUGIN_SCRIPTS))
import standard_tree as tree  # noqa: E402


def materialize_skeleton(copy: Path, bc_name: str) -> None:
    """신규 BC의 fixed/reappear 골격 전량 실체화 (D2 ②상수-배선형 — #488 대응)."""
    bc_dir = copy / "application" / bc_name
    if not bc_dir.exists():
        return
    (bc_dir / "__init__.py").touch()

    def walk(row: "tree.Row", dirpath: Path, bindings: dict) -> None:
        kids = tree.children(row)
        fixed_claimed: set[str] = set()
        for c in kids:
            if c.kind in ("fixed", "reappear"):
                name = tree.concrete_name(c, bindings)
                if "<" in name:
                    continue  # 미해소 재등장 — 이 수준에서 바인딩 없음
                name = name.rstrip("/")
                fixed_claimed.add(name)
                tgt = dirpath / name
                if tree.is_dir(c):
                    tgt.mkdir(parents=True, exist_ok=True)
                    (tgt / "__init__.py").touch()
                    walk(c, tgt, bindings)
                elif not tgt.exists():
                    if name == "apps.py" and dirpath.name.startswith("django_"):
                        bc = bindings.get("bounded_context", "")
                        cls = "".join(w.title() for w in bc.split("_")) + "Config"
                        tgt.write_text(
                            "from django.apps import AppConfig\n\n\n"
                            f"class {cls}(AppConfig):\n"
                            '    """pre-gate 팬텀 정형 골격."""\n\n'
                            f'    name = "application.{bc}.driven_layer.{dirpath.name}"\n'
                            f'    label = "{bc}"\n',
                            encoding="utf-8",
                        )
                    else:
                        tgt.touch()
        for c in kids:
            if c.kind == "placeholder" and tree.is_dir(c) and dirpath.exists():
                token = c.name.rstrip("/").strip("<>")
                for p in sorted(dirpath.iterdir()):
                    if p.is_dir() and p.name not in fixed_claimed and p.name != "__pycache__":
                        b2 = dict(bindings)
                        b2[token] = p.name
                        walk(c, p, b2)

    walk(tree.bc_root(), bc_dir, {"bounded_context": bc_name})


def run(src_repo: Path, base_sha: str, files: list[PlanFile], workdir: Path,
        python_bin: str, keep: bool = False, reconcile: bool = False) -> dict:
    if workdir.exists():
        shutil.rmtree(workdir)
    copy = workdir / "copy"
    copy.mkdir(parents=True)
    errs = validate_paths(files)
    if errs:
        return {"status": "red-form", "errors": errs}
    # 1) archive → 사본 (훅 억제)
    tar = subprocess.run(["git", "-C", str(src_repo), "-c", "core.hooksPath=", "archive", base_sha],
                         capture_output=True, check=True)
    subprocess.run(["tar", "-x", "-C", str(copy)], input=tar.stdout, check=True)
    # 2) init + 전량 커밋 (= 앵커)
    def g(*args: str) -> None:
        subprocess.run(["git", "-C", str(copy), "-c", "core.hooksPath=",
                        "-c", "user.email=pregate@local", "-c", "user.name=pregate"]
                       + list(args), check=True, capture_output=True)
    g("init", "-q")
    g("add", "-A")
    g("commit", "-q", "-m", "pregate-anchor")
    # 3) 팬텀 실체화 (태그 의미론)
    report: dict = {"unsimulated": [], "materialized": []}
    for pf in files:
        if pf.path.endswith("/apps.py") and "django_" in pf.path:
            for sym in pf.symbols:
                if not sym.get("base"):
                    sym["base"] = "AppConfig"
    for pf in files:
        target = copy / pf.path
        if pf.tag == "add":
            if target.exists():
                if reconcile:
                    report.setdefault("already_built", []).append(pf.path)
                    continue
                return {"status": "red-form", "errors": [f"add 충돌(실존): {pf.path}"]}
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render_stub(pf), encoding="utf-8")
            report["materialized"].append(pf.path)
        elif pf.tag == "empty":
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text("", encoding="utf-8")
            report["materialized"].append(pf.path)
        elif pf.tag == "remove":
            if target.exists():
                target.unlink()
                report["materialized"].append(f"removed {pf.path}")
            else:
                report["unsimulated"].append(f"remove(실존 없음): {pf.path}")
        elif pf.tag == "update":
            report["unsimulated"].append(f"update: {pf.path}")
    # 신규 BC 골격 전량 (archive에 없던 BC만)
    new_bcs: set[str] = set()
    for pf in files:
        parts = Path(pf.path).parts
        if len(parts) >= 2 and parts[0] == "application":
            new_bcs.add(parts[1])
    for bc in sorted(new_bcs):
        marker = subprocess.run(["git", "-C", str(copy), "ls-tree", "HEAD", f"application/{bc}"],
                                capture_output=True, text=True)
        if not marker.stdout.strip():
            materialize_skeleton(copy, bc)
    # __init__.py 체인 보강 (골격 최소 — 패키지 인식)
    for pf in files:
        if pf.tag in ("add", "empty"):
            p = Path(pf.path).parent
            while len(p.parts) >= 1 and str(p) != ".":
                initf = copy / p / "__init__.py"
                if not initf.exists() and (copy / p).exists():
                    initf.write_text("", encoding="utf-8")
                p = p.parent
    # 4) registry_gate
    env = dict(os.environ)
    env["DJR_FINDINGS_JSON"] = str(workdir / "findings.jsonl")
    proc = subprocess.run([python_bin, str(PLUGIN_SCRIPTS / "registry_gate.py"),
                           str(copy), "--anchor", "HEAD",
                           "--introduced-json", str(workdir / "introduced.json")],
                          capture_output=True, text=True, env=env)
    report["exit"] = proc.returncode
    report["stdout_tail"] = proc.stdout[-4000:]
    report["stderr_tail"] = proc.stderr[-2000:]
    intro = workdir / "introduced.json"
    if intro.exists():
        report["introduced"] = json.loads(intro.read_text())
    report["status"] = "done"
    if not keep:
        shutil.rmtree(copy, ignore_errors=True)
    return report


if __name__ == "__main__":
    # 스모크: 팬텀 1파일 (레이어 밖 경로 → 귀속 발화 기대)
    src = Path.home() / ".herdr/worktrees/spring_dream_server/feat-fortune-reading"
    wd = Path(__file__).parent / "smoke"
    pf = PlanFile(path="application/fortune_reading/helpers/util.py", tag="add",
                  symbols=[{"name": "Util", "base": "", "fields": {}}])
    rep = run(src, "b5392f0", [pf], wd, sys.executable, keep=False)
    print(json.dumps({k: v for k, v in rep.items() if k != "stdout_tail"}, ensure_ascii=False, indent=1)[:2000])
    print("STDOUT TAIL:\n", rep.get("stdout_tail", "")[-1500:])
