#!/usr/bin/env python3
"""B0 영구 픽스처 러너 — 지원 확인 · 증거 실행 엔진(`behavior_support.run` · `g0_keep`)을 장난감 저장소 510 칸에 대어
판정 · 사유 · 사유 수를 기대 표와 대조한다(RD 설계 v15.2 §4-7 · §8 B0 · 계획 T11 · T10 E1).

사례 = `workspace/eval/fixtures/behavior_probe/cases.py`(R 원형 재현 412 · N 이름별 48 · C 빈 범주 50) ·
기대 표 = 같은 폴더 `expected.json`. 장난감은 `tempfile` 안 새 폴더(`git init` 만 — `after_commit` 사례만 픽스처 커밋 1)이고, 장난감 pytest 는
저장소 루트의 고정 판 픽스처 환경 `.venv-probe` 로 돈다(없으면 «make probe-env 필요»).

엔진:
  --engine impl              (기본) 구현판 `dddjango/scripts/behavior_support.py`(k0 §4-5 서명) — 510 칸.
  --engine impl=<scripts 폴더>  같은 서명의 다른 판(대역 시험용).
  --engine proto=<원형 폴더>   원형 `support_v152.run`(T11 원형 대비 전용) — 상한 14 칸은 원형에 상수가 없어 건너뛴다.
칸 판정: 사유가 없으면 «통과», 있으면 collect · G0 · support 칸은 «정지», run · G2 · suite 칸은 «red».
정규화(k0 v2 §5 — 경로만 · compare_v152 방식): 픽스처 인터프리터 경로 `<PY>` · 장난감 경로 `<TOY>` · 탐침 출력 자리
`<PROBE_OUT>` · 러너 공유 자리(저장소 밖 설치 도구 흉내 · 플러그인 폴더) `<SHARED>` · 인터프리터 환경의 site-packages 경로
`<SITE>/`. 트리 지문 값 · 시간 · pid · 판정 · 규칙 이름 · 걸린 파일:줄 · 사유 수는 정규화하지 않는다.
편차(기대 표 그 칸의 `deviation` — 표시가 없는 칸에는 쓰지 않는다):
  «지문 값» 엔진마다 계산식이 달라 정말로 다른 값 — 그 엔진에서만 정규식 첫 묶음 안 12 자리 값을 처음 나온 차례대로 ‹A› ‹B› … 로
            바꿔 같음 · 다름 꼴만 대조한다. 그 칸의 나머지 글자는 그대로 본다.
  «환경»    돌린 환경이 정하는 값 — 기대 표의 표지(`<PARSER_VERSION>`)를 엔진을 돌린 인터프리터의 판으로 채워 정확히 대조한다.
  «구현판 더함» 원형에 없는 관측 칸 때문에 구현판만 내는 사유 — 그 엔진에서만 기대 사유에 적힌 줄을 더해(사유 수도) 정확히 대조한다.
상한: 일반 사례는 두 제품 상수를 COMMAND_CAP_SECONDS로 잠시 낮춘다(러너 안전 상한) ·
상한 사례는 명령 진입 함수 `cmd_support` · `cmd_suite`(support --collect · suite)를 장난감 안 실행 폴더로 거치고, 상수만
TIMEOUT_CASE_SECONDS 로 바꿔 혼자(병렬 밖) 돈다 — exit · 기록 판정 · 마지막 `요약:` 줄까지 본다. 신호는 러너가 띄운 표지
프로세스에만 보낸다. 분리 사례는 수집 10초 · suite 40초로 차례 실행한다(기계가 바쁠 때도 서게 넉넉히 — 수집은 보통 1초 안). T3는 지원 안 함 뒤 G1을 만들지 않고 run 엔진만 대조한다.
exit 0 = 전 칸 기대 일치 · 1 = 불일치 · 실행 실패 · 실행 불능.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
import hashlib
import importlib
import importlib.util
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path
from types import ModuleType

sys.dont_write_bytecode = True   # 구현판 · 사례 모듈을 들여도 저장소에 __pycache__ 를 남기지 않는다

ROOT: Path = Path(__file__).resolve().parents[2]
FIXTURES: Path = ROOT / "workspace" / "eval" / "fixtures" / "behavior_probe"
EXPECTED: Path = FIXTURES / "expected.json"
PROBE_PY: Path = ROOT / ".venv-probe" / "bin" / "python"
IMPL_DIR: Path = ROOT / "dddjango" / "scripts"
PRODUCT_TIMEOUT_SECONDS: int = 600      # 정오 2 — 제품 고정값(구현판 상수가 이 값인지 먼저 본다)
PRODUCT_SUITE_TIMEOUT_SECONDS: int = 3600
MAX_JOBS: int = 8
COMMAND_CAP_SECONDS: int = 180
TIMEOUT_CASE_SECONDS: int = 5
LIMIT_COLLECT_SECONDS: int = 10         # 바쁜 기계에서 장난감 수집이 2초를 넘은 실측(2026-10-07) — 넉넉히
LIMIT_SUITE_SECONDS: int = 40
TIMEOUT_FOLDER: str = ".dddjango/f1-refactor-timeout"          # 상한 사례의 실행 폴더(장난감 안 · `.dddjango/` 는 범위 밖)
TIMEOUT_SCOPE: str = "# 범위\n\n실행 · G0 승인 20261004T100000Z · 운영 전 픽스처\n"
TIMEOUT_G1_AT: str = "2026-10-04T10:00:00Z"
GONE_WAIT_SECONDS: float = 5.0
BASE_ENV_DROP_PREFIX: "tuple[str, ...]" = ("PYTEST_", "DJANGO_", "DDDJANGO_")
BASE_ENV_DROP: "tuple[str, ...]" = ("R8_SKIP_BAD", "R8_SETUPONLY", "QUICK", "NO_BODY", "FAST", "PYTHONOPTIMIZE", "PYTHONPATH")
CELLS: "dict[str, tuple[str, str]]" = {"pair": ("collect", "run"), "env": ("G0", "G2"), "timeout": ("support", "suite"),
                                       "limits": ("support", "suite")}
STOP_LABEL: "dict[str, str]" = {"collect": "정지", "G0": "정지", "support": "정지", "run": "red", "G2": "red", "suite": "red"}
SITE_RE: "re.Pattern[str]" = re.compile(r"(?:/[^\s:()'\"]*)?/lib/python3\.\d+/site-packages/")
HEX12_RE: "re.Pattern[str]" = re.compile(r"\b[0-9a-f]{12}\b")
# 엔진은 러너 프로세스 안에서 돈다 — 정적 규칙의 파서 판 = 이 인터프리터의 판(설계 «파서 판을 사유에 적는다»)
ENV_TOKENS: "dict[str, str]" = {"<PARSER_VERSION>": ".".join(map(str, sys.version_info[:3]))}
GIT_FIXTURE_ENV: "dict[str, str]" = {"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                                     "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
                                     "GIT_AUTHOR_DATE": "2026-01-01T00:00:00+0000", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00+0000"}


def load_cases() -> ModuleType:
    spec = importlib.util.spec_from_file_location("behavior_probe_cases", FIXTURES / "cases.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class Engine:
    """원형 · 구현판 엔진의 같은 꼴 — run(repo, definition, mode, inherited) · g0_keep(g0, g2, repo)."""

    def __init__(self, label: str, mod: ModuleType, proto: bool) -> None:
        self.label: str = label
        self.mod: ModuleType = mod
        self.proto: bool = proto
        self.frozen: "tuple[str, ...]" = tuple(mod.FROZEN)

    def definition(self, argvs: "list[list[str]]", frozen: "dict[str, str] | None") -> dict:
        env = {k: (frozen or {}).get(k) for k in self.frozen}
        if self.proto:
            return {"argvs": argvs, "env": env}
        return {"version": 1, "argvs": argvs, "env": env, "sources": [], "frozen_at": ""}

    def run(self, repo: Path, definition: dict, mode: str, inherited: "dict[str, str]", *, drop_worker: bool,
            probe_out_root: Path) -> "tuple[list[str], dict]":
        if self.proto:
            return self.mod.run(repo, definition, mode, inherited, drop_worker=drop_worker, timeout=COMMAND_CAP_SECONDS)
        return self.mod.run(repo, definition, mode, inherited, probe_out_root=probe_out_root, drop_worker=drop_worker,
                            stop_on_fail=(mode == "run"))

    def g0_keep(self, g0: dict, g2: dict, repo: Path) -> "list[str]":
        return self.mod.g0_keep(g0, g2, repo)


def load_engine(spec: str) -> "tuple[Engine | None, str]":
    kind, _, where = spec.partition("=")
    if kind == "proto":
        if not where:
            return None, "--engine proto=<원형 폴더> 에 폴더가 없다"
        d = Path(where).resolve()
        if not (d / "support_v152.py").is_file():
            return None, f"원형 support_v152.py 없음: {d}"
        (d / "probe_out").mkdir(exist_ok=True)       # 원형 run 이 탐침 출력을 자기 폴더 probe_out/ 아래에 만든다
        sys.path.insert(0, str(d))
        return Engine(f"proto({d})", importlib.import_module("support_v152"), proto=True), ""
    if kind == "impl":
        d = Path(where).resolve() if where else IMPL_DIR
        if not (d / "behavior_support.py").is_file():
            return None, f"구현판 behavior_support.py 없음: {d}"
        sys.path.insert(0, str(d))
        return Engine(f"impl({d})", importlib.import_module("behavior_support"), proto=False), ""
    return None, f"모르는 엔진: {spec}"


def base_env() -> "dict[str, str]":
    return {k: v for k, v in os.environ.items() if not k.startswith(BASE_ENV_DROP_PREFIX) and k not in BASE_ENV_DROP}


class Toolbox:
    """실행 한 번의 공유 자리 — 설치 도구 흉내 폴더(저장소 · 장난감 밖)와 표지 치환."""

    def __init__(self, cases: ModuleType, shared: Path) -> None:
        self.cases: ModuleType = cases
        self.shared: Path = shared
        self.tokens: "dict[str, str]" = {}
        for token, body, sub, name in ((cases.COV_TRACE, cases.COV_TRACE_SITECUSTOMIZE, "cov_trace", "sitecustomize.py"),
                                       (cases.COV_MON, cases.COV_MON_SITECUSTOMIZE, "cov_mon", "sitecustomize.py"),
                                       (cases.EXT_PLUGIN, cases.EXT_PLUGIN_SOURCE, "ext_plugin", "extplug.py")):
            d = shared / sub
            d.mkdir()
            (d / name).write_text(body, encoding="utf-8")
            self.tokens[token] = str(d)

    def env(self, env: "dict[str, str]") -> "dict[str, str]":
        out = {}
        for k, v in env.items():
            if v == self.cases.GREENLET_SITE:
                continue                                   # greenlet 은 .venv-probe site-packages 에 있다(k0 §6)
            out[k] = self.tokens.get(v, v)
        return out

    def argvs(self, argvs: "list[list[str]] | None") -> "list[list[str]]":
        return [[str(PROBE_PY) if a == self.cases.PY else a for a in argv] for argv in (argvs or [[self.cases.PY, "-m", "pytest"]])]


def build_toy(cases: ModuleType, case, at: Path) -> Path:
    at.mkdir()
    for rel, body in cases.toy_files(case).items():
        p = at / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(body, bytes):
            p.write_bytes(body)
        else:
            p.write_text(body, encoding="utf-8")
    for rel, target in (case.symlinks or {}).items():
        link = at / rel
        link.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(target, link)
    subprocess.run(["git", "-c", "init.defaultBranch=main", "init", "-q", str(at)], check=True, capture_output=True)
    if case.after_commit is not None:                      # tempfile 안 픽스처 커밋 1 뒤 작업 트리 편집(지운 추적 파일 등)
        git = ["git", "-C", str(at), "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false"]
        env = {**os.environ, **GIT_FIXTURE_ENV}
        subprocess.run([*git, "add", "-A"], check=True, capture_output=True, env=env)
        subprocess.run([*git, "commit", "-q", "-m", "fixture base"], check=True, capture_output=True, env=env)
        for rel, body in case.after_commit.items():
            if body is None:
                (at / rel).unlink()
            else:
                (at / rel).write_text(body, encoding="utf-8")
    return at


def normalize(text: str, places: "list[tuple[Path, str]]") -> str:
    pairs = [(str(PROBE_PY), "<PY>")]
    for path, token in places:
        pairs += [(str(path.resolve()), token), (str(path), token)]
    for path, token in sorted(pairs, key=lambda x: -len(x[0])):
        text = text.replace(path, token)
    return SITE_RE.sub("<SITE>/", text)


def _obs(info: dict) -> "list[int]":
    return [len(info["obs_hits_M"]), info["obs_files_M"], len(info["obs_hits_union"]), info["obs_files_union"]]


def cell(label: str, reasons: "list[str]", extras: dict, box: "Toolbox", *places: "tuple[Path, str]") -> dict:
    norm = [normalize(r, [*places, (box.shared, "<SHARED>")]) for r in reasons]
    return {"verdict": STOP_LABEL[label] if norm else "통과", "count": len(norm), "reasons": norm, "extras": extras}


def run_pair(engine: Engine, box: Toolbox, case, work: Path) -> dict:
    out = {}
    for n, mode in enumerate(CELLS["pair"]):
        toy = build_toy(box.cases, case, work / f"toy{n}")
        probe = work / f"probe{n}"
        probe.mkdir()
        d = engine.definition(box.argvs(case.argvs), case.frozen)
        reasons, info = engine.run(toy, d, mode, {**base_env(), **box.env(case.env)}, drop_worker=case.drop_worker, probe_out_root=probe)
        out[mode] = cell(mode, reasons, {"selected": info["selected"], "M": info["M"], "outputs": info["outputs"], "obs": _obs(info)},
                         box, (toy, "<TOY>"), (probe, "<PROBE_OUT>"))
    return out


def run_env(engine: Engine, box: Toolbox, case, work: Path) -> dict:
    toy = build_toy(box.cases, case, work / "toy")
    probe0, probe2, probe2b = work / "probe0", work / "probe2", work / "probe2b"
    for place in (probe0, probe2, probe2b):
        place.mkdir()                                      # 실행마다 빈 새 자리(구현판은 비어 있지 않은 자리를 거부한다)
    d = engine.definition(box.argvs(None), None)
    g2env = box.env(case.env)
    g0env = {**base_env(), **({"PYTHONPATH": g2env["PYTHONPATH"]} if "PYTHONPATH" in g2env else {})}
    r0, i0 = engine.run(toy, d, "collect", g0env, drop_worker=False, probe_out_root=probe0)
    r2, i2 = engine.run(toy, d, "run", {**base_env(), **g2env}, drop_worker=False, probe_out_root=probe2)
    if case.after:
        for rel, body in case.after.items():
            (toy / rel).write_text(body, encoding="utf-8")
        probe2 = probe2b
        r2, i2 = engine.run(toy, d, "run", {**base_env(), **g2env}, drop_worker=False, probe_out_root=probe2)
    lost = engine.g0_keep(i0, i2, toy) if "keys" in i0 and "keys" in i2 else ["구조 키 없음"]
    verdict = list(r2) + ([f"G0 유지 위반 {lost}"] if lost else [])
    return {"G0": cell("G0", r0, {"selected": i0["selected"]}, box, (toy, "<TOY>"), (probe0, "<PROBE_OUT>")),
            "G2": cell("G2", verdict, {"selected": i2["selected"], "obs": _obs(i2)}, box, (toy, "<TOY>"), (probe2, "<PROBE_OUT>"))}


def _gone(pid: int) -> bool:
    """pid 가 없거나 좀비면 끝난 것 — ps 로만 본다(신호를 보내지 않는다)."""
    deadline = time.monotonic() + GONE_WAIT_SECONDS
    while True:
        p = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True)
        stat = p.stdout.strip()
        if p.returncode != 0 or not stat or stat.startswith("Z"):
            return True
        if time.monotonic() > deadline:
            return False
        time.sleep(0.2)


def _killed(pid_file: Path) -> bool:
    return pid_file.is_file() and _gone(int(pid_file.read_text(encoding="utf-8")))


def _command(fn, folder: Path, repo: Path) -> "tuple[int, str]":
    """명령 진입 함수 하나 — (exit, 출력). 병렬 밖에서만 부른다(표준 출력을 잠시 가로챈다)."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = fn(folder, repo)
    return code, said.getvalue()


def _summary(said: str) -> str:
    """마지막 줄의 `요약: …` 머리(첫 « · » 앞) — 마지막 줄이 요약이 아니면 그렇다고 적는다."""
    lines = said.strip().splitlines()
    last = lines[-1] if lines else ""
    return last.split(" · ")[0] if last.startswith("요약:") else f"마지막 줄이 요약 아님: {last[:80]}"


def _timeout_folder(engine: Engine, box: Toolbox, case, at: Path) -> "tuple[Path, Path, Path]":
    """장난감 + 실행 폴더(refactor-scope.md 실행 줄) + 새 지원 확인 기록 자리의 test-commands.md(k0 §4-3 판형)."""
    toy = build_toy(box.cases, case, at)
    folder = toy / TIMEOUT_FOLDER
    folder.mkdir(parents=True)
    (folder / "refactor-scope.md").write_text(TIMEOUT_SCOPE, encoding="utf-8")
    rec = engine.mod.support_root(folder) / time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    rec.mkdir(parents=True)
    (rec / "test-commands.md").write_text("".join(f"시험 명령 {n}: {shlex.join(argv)}\n출처: 픽스처(behavior_probe {case.id})\n"
                                                for n, argv in enumerate(box.argvs(case.argvs), 1)), encoding="utf-8")
    return toy, folder, rec


def _bind_g1(folder: Path, rec: Path) -> None:
    """G1 결속 자료 — 후보 스냅숏(그 지원 기록 · 실행 정의 digest) + 이번 실행 몫의 `## G1 변경 결정 <시각> · 후보 digest <c>`
    절 머리(밖 동작 V 0 이라 결정 줄 없음) + 그 뒤 `G1 변경판 확정 <시각> · digest <d> · 후보 <c>` 줄(k0 §4-4 · §1 G1 순서)."""
    g0 = json.loads((rec / "g0-collect.json").read_text(encoding="utf-8"))
    snap = {"version": 1, "support_record": rec.name, "run_definition_digest": g0["run_definition_digest"]}
    digest = hashlib.sha256(json.dumps(snap, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:12]
    (folder / "g1").mkdir()
    (folder / "g1" / f"{rec.name}-candidate.json").write_text(json.dumps(snap, ensure_ascii=False), encoding="utf-8")
    with (folder / "refactor-scope.md").open("a", encoding="utf-8") as fh:
        fh.write(f"\n## G1 변경 결정 {TIMEOUT_G1_AT} · 후보 digest {digest}\n\n"
                 f"G1 변경판 확정 {TIMEOUT_G1_AT} · digest {digest} · 후보 {digest}\n")


def run_timeout(engine: Engine, box: Toolbox, case, work: Path) -> dict:
    """상한 상수만 짧게 바꿔 명령 진입 함수 support(cmd_support) · suite(cmd_suite) 를 돈다 — 그 명령의 프로세스 묶음(자식 포함)은
    끝나고, 러너가 묶음 밖에 띄운 표지 프로세스는 산다. 명령은 상속 환경(os.environ)을 쓰므로 병렬 밖에서 기본 환경으로 잠시
    바꿔 돌린다. suite 칸은 같은 장난감이 멈추지 않을 때 지원 확인(«지원») → G1 결속 → 멈추게 하는 변수를 준 suite 차례다.
    표지는 끝에 러너가 자기 것만 정리한다."""
    marker = subprocess.Popen([str(PROBE_PY), "-c", "import time; time.sleep(300)"], start_new_session=True,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    saved_const = (engine.mod.COMMAND_TIMEOUT_SECONDS, engine.mod.SUITE_COMMAND_TIMEOUT_SECONDS)
    saved_env = dict(os.environ)

    def hang(fn, folder: Path, toy: Path, pid_file: Path) -> "tuple[int, str]":
        os.environ["F_CHILD_PID_FILE"] = str(pid_file)
        engine.mod.COMMAND_TIMEOUT_SECONDS = TIMEOUT_CASE_SECONDS
        engine.mod.SUITE_COMMAND_TIMEOUT_SECONDS = TIMEOUT_CASE_SECONDS
        try:
            return _command(fn, folder, toy)
        finally:
            engine.mod.COMMAND_TIMEOUT_SECONDS, engine.mod.SUITE_COMMAND_TIMEOUT_SECONDS = saved_const
            os.environ.pop("F_CHILD_PID_FILE", None)

    out = {}
    try:
        os.environ.clear()
        os.environ.update(base_env())
        toy, folder, rec = _timeout_folder(engine, box, case, work / "toy0")
        code, said = hang(engine.mod.cmd_support, folder, toy, work / "child0.pid")
        g0 = json.loads((rec / "g0-collect.json").read_text(encoding="utf-8"))
        out["support"] = cell("support", g0["reasons"], {"exit": code, "summary": _summary(said), "record_verdict": g0["verdict"],
                                                         "group_killed": _killed(work / "child0.pid"), "marker_alive": marker.poll() is None},
                              box, (toy, "<TOY>"))
        toy, folder, rec = _timeout_folder(engine, box, case, work / "toy1")
        code, said = _command(engine.mod.cmd_support, folder, toy)
        if code != 0:
            raise RuntimeError(f"suite 칸 준비 — 앞선 지원 확인이 «지원»이 아님(exit {code}): {said.strip().splitlines()[-1:]}")
        _bind_g1(folder, rec)
        code, said = hang(engine.mod.cmd_suite, folder, toy, work / "child1.pid")
        suite = engine.mod.latest_suite_record(folder)
        if suite is None:
            raise RuntimeError(f"suite 기록 없음(exit {code}): {said.strip().splitlines()[-1:]}")
        keep = [normalize(k, [(toy, "<TOY>"), (box.shared, "<SHARED>")]) for k in suite["g0_keep"]]
        out["suite"] = cell("suite", suite["reasons"], {"exit": code, "summary": _summary(said), "record_verdict": suite["verdict"],
                                                        "g0_keep": keep, "group_killed": _killed(work / "child1.pid"),
                                                        "marker_alive": marker.poll() is None}, box, (toy, "<TOY>"))
    finally:
        os.environ.clear()
        os.environ.update(saved_env)
        if marker.poll() is None:
            os.killpg(marker.pid, 15)                      # 러너가 띄운 표지(자기 세션) 하나에만
        marker.wait(timeout=10)
    return out


def run_limits(engine: Engine, box: Toolbox, case, work: Path) -> dict:
    """서로 다른 상한을 명령 진입 함수에 적용한다. T3의 지원 안 함 뒤에는 결속 없이 run 엔진만 대조한다."""
    saved = (engine.mod.COMMAND_TIMEOUT_SECONDS, engine.mod.SUITE_COMMAND_TIMEOUT_SECONDS)
    saved_env, saved_keep = dict(os.environ), engine.mod.g0_keep
    inherited = base_env()
    marker = None
    out = {}
    try:
        os.environ.clear()
        os.environ.update(inherited)
        engine.mod.COMMAND_TIMEOUT_SECONDS = LIMIT_COLLECT_SECONDS
        engine.mod.SUITE_COMMAND_TIMEOUT_SECONDS = LIMIT_SUITE_SECONDS
        toy, folder, rec = _timeout_folder(engine, box, case, work / "toy")
        code, said = _command(engine.mod.cmd_support, folder, toy)
        g0 = json.loads((rec / "g0-collect.json").read_text(encoding="utf-8"))
        out["support"] = cell("support", g0["reasons"], {"exit": code, "summary": _summary(said),
                                                        "record_verdict": g0["verdict"]}, box, (toy, "<TOY>"))
        if case.id == "C-limit-T3":
            reasons, info = engine.run(toy, engine.definition(box.argvs(case.argvs), case.frozen), "run", dict(os.environ),
                                       drop_worker=False, probe_out_root=work / "probe")
            out["suite"] = cell("suite", reasons, {"command_exits": [c["exit"] for c in info["commands"]],
                                                  "outputs": info["outputs"], "proof": [info["counts"]["proof_ok"],
                                                                                       info["counts"]["proof_total"]]}, box,
                                (toy, "<TOY>"), (work / "probe", "<PROBE_OUT>"))
            return out
        if code != 0:
            raise RuntimeError(f"분리 사례의 지원 확인이 «지원»이 아님: {said}")
        _bind_g1(folder, rec)
        if case.id in ("C-limit-T2a", "C-limit-T2b"):
            marker = subprocess.Popen([str(PROBE_PY), "-c", "import time; time.sleep(300)"], start_new_session=True,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.environ["F_CHILD_PID_FILE"] = str(work / "child.pid")

            def unexpected_keep(*args, **kwargs):
                raise AssertionError("시간 초과 suite가 g0_keep 대조를 호출함")

            engine.mod.g0_keep = unexpected_keep
        code, said = _command(engine.mod.cmd_suite, folder, toy)
        suite = engine.mod.latest_suite_record(folder)
        if suite is None:
            raise RuntimeError(f"분리 사례의 suite 기록 없음: {said}")
        extras = {"exit": code, "summary": _summary(said), "record_verdict": suite["verdict"], "g0_keep": suite["g0_keep"],
                  "command_exits": [c["exit"] for c in suite["commands"]], "outputs": sum(c["outputs"] for c in suite["commands"]),
                  "proof": [suite["counts"]["proof_ok"], suite["counts"]["proof_total"]]}
        if marker is not None:
            extras.update({"group_killed": _killed(work / "child.pid"), "marker_alive": marker.poll() is None,
                           "next_not_run": not (work / "child.pid.next").exists()})
        if case.id in ("C-limit-T1", "C-limit-T4"):
            seconds = [c["seconds"] for c in suite["commands"]]
            extras.update({"collect_below_cap": all(c["seconds"] < LIMIT_COLLECT_SECONDS for c in g0["commands"]),
                           "each_between_caps": all(LIMIT_COLLECT_SECONDS < s < LIMIT_SUITE_SECONDS for s in seconds),
                           "sum_above_suite_cap": sum(seconds) > LIMIT_SUITE_SECONDS})
        out["suite"] = cell("suite", suite["reasons"], extras, box, (toy, "<TOY>"))
    finally:
        engine.mod.COMMAND_TIMEOUT_SECONDS, engine.mod.SUITE_COMMAND_TIMEOUT_SECONDS = saved
        engine.mod.g0_keep = saved_keep
        os.environ.clear()
        os.environ.update(saved_env)
        if marker is not None:
            if marker.poll() is None:
                os.killpg(marker.pid, 15)
            marker.wait(timeout=10)
    return out


RUNNERS = {"pair": run_pair, "env": run_env, "timeout": run_timeout, "limits": run_limits}


def run_case(engine: Engine, box: Toolbox, case) -> "tuple[dict | None, str, float]":
    t0 = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix="bp-case-") as td:
            got = RUNNERS[case.kind](engine, box, case, Path(td))
        return got, "", time.monotonic() - t0
    except Exception:                                      # noqa: BLE001 — 사례 하나의 실패를 기록하고 나머지를 돈다
        return None, traceback.format_exc(), time.monotonic() - t0


def mask(reasons: "list[str]", regex: str) -> "list[str]":
    """편차 범위(정규식 첫 묶음) 안 12 자리 값만 처음 나온 차례대로 ‹A› ‹B› … 로 — 범위 밖 글자와 같음 · 다름 꼴은 남긴다."""
    rx = re.compile(regex)

    def inner(m: "re.Match[str]") -> str:
        seen: "dict[str, str]" = {}
        body = HEX12_RE.sub(lambda h: seen.setdefault(h.group(0), f"‹{chr(65 + len(seen))}›"), m.group(1))
        whole = m.group(0)
        return whole[:m.start(1) - m.start()] + body + whole[m.end(1) - m.start():]

    return [rx.sub(inner, r) for r in reasons]


def compare(case, want: "dict | None", got: dict, engine: Engine) -> "tuple[list[str], int, int, int]":
    """(다름 줄, 지문 값 편차 범위를 뺀 칸 수, 환경 값을 채운 칸 수, 구현판 사유를 더한 칸 수)."""
    if want is None:
        return [f"{case.id} — 기대 표에 사례 없음"], 0, 0, 0
    if want.get("name") != case.name:
        return [f"{case.id} — 기대 표 사례 이름 다름: {want.get('name')!r}"], 0, 0, 0
    diffs, deviated, filled, added = [], 0, 0, 0
    for label in CELLS[case.kind]:
        w, g = want["cells"].get(label), got.get(label)
        if w is None or g is None:
            diffs.append(f"{case.id} {label} — 칸 없음(기대 {w is not None} · 실제 {g is not None})")
            continue
        wr, gr, wcount = w["reasons"], g["reasons"], w["count"]
        dev = w.get("deviation")
        this_engine = "proto" if engine.proto else "impl"
        if dev and dev["kind"] == "환경":
            wr = [r.replace(dev["token"], ENV_TOKENS[dev["token"]]) for r in wr]
            filled += 1
        elif dev and dev["kind"] == "지문 값" and this_engine in dev["engines"]:
            wr, gr = mask(wr, dev["regex"]), mask(gr, dev["regex"])
            deviated += 1
        elif dev and dev["kind"] == "구현판 더함" and this_engine in dev["engines"]:
            wr, wcount = [*wr, *dev["reasons"]], wcount + len(dev["reasons"])
            added += 1
        parts = []
        if w["verdict"] != g["verdict"]:
            parts.append(f"판정 기대 {w['verdict']} · 실제 {g['verdict']}")
        if wcount != g["count"]:
            parts.append(f"사유 수 기대 {wcount} · 실제 {g['count']}")
        if sorted(wr) != sorted(gr):
            only_w = sorted(set(wr) - set(gr))
            only_g = sorted(set(gr) - set(wr))
            parts.append(f"사유 다름 — 기대에만 {only_w} · 실제에만 {only_g}")
        if w["extras"] != g["extras"]:
            parts.append(f"부가 관측 기대 {w['extras']} · 실제 {g['extras']}")
        if parts:
            diffs.append(f"{case.id} {label} [{case.name}] — " + " / ".join(parts))
    return diffs, deviated, filled, added


def main() -> int:
    ap = argparse.ArgumentParser(description="B0 영구 픽스처 러너(behavior_support)")
    ap.add_argument("--engine", default="impl", help="impl(기본) · impl=<scripts 폴더> · proto=<원형 폴더>")
    ap.add_argument("--only", action="append", default=[], help="사례 id 접두 · 갈래(R|N|C) · 묶음 이름 — 여러 번 줄 수 있다")
    ap.add_argument("--jobs", type=int, default=MAX_JOBS, help=f"병렬 사례 수(1 ~ {MAX_JOBS})")
    ap.add_argument("--dump", type=Path, help="실제 결과(정규화 뒤)를 이 JSON 파일로 쓴다")
    args = ap.parse_args()
    if not PROBE_PY.exists():
        print(f"요약: 실행 불능 — 픽스처 환경 없음 {PROBE_PY} · make probe-env 필요")
        return 1
    engine, why = load_engine(args.engine)
    if engine is None:
        print(f"요약: 실행 불능 — {why}")
        return 1
    cases = load_cases()
    want_all = json.loads(EXPECTED.read_text(encoding="utf-8"))["cases"] if EXPECTED.is_file() else {}
    selected = [c for c in cases.ALL_CASES
                if not args.only or any(c.id.startswith(o) or c.group == o or c.bundle == o for o in args.only)]
    skipped = [c for c in selected if c.kind in ("timeout", "limits") and engine.proto]
    pooled = [c for c in selected if c.kind not in ("timeout", "limits")]
    serial = [c for c in selected if c.kind in ("timeout", "limits") and not engine.proto]
    jobs = max(1, min(MAX_JOBS, args.jobs))
    problems: "list[str]" = []
    if not engine.proto and engine.mod.COMMAND_TIMEOUT_SECONDS != PRODUCT_TIMEOUT_SECONDS:
        problems.append(f"구현판 COMMAND_TIMEOUT_SECONDS = {engine.mod.COMMAND_TIMEOUT_SECONDS} ≠ {PRODUCT_TIMEOUT_SECONDS}(정오 2)")
    if not engine.proto and engine.mod.SUITE_COMMAND_TIMEOUT_SECONDS != PRODUCT_SUITE_TIMEOUT_SECONDS:
        problems.append(f"구현판 SUITE_COMMAND_TIMEOUT_SECONDS = {engine.mod.SUITE_COMMAND_TIMEOUT_SECONDS} ≠ {PRODUCT_SUITE_TIMEOUT_SECONDS}(F-B1R-6)")
    print(f"B0 영구 픽스처 — 엔진 {engine.label} · 사례 {len(pooled) + len(serial)} · 칸 {2 * (len(pooled) + len(serial))} · 병렬 {jobs}",
          flush=True)
    results: "dict[str, tuple[dict | None, str, float]]" = {}
    t0 = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="bp-shared-") as shared:
        box = Toolbox(cases, Path(shared))
        saved = None if engine.proto else (engine.mod.COMMAND_TIMEOUT_SECONDS, engine.mod.SUITE_COMMAND_TIMEOUT_SECONDS)
        if saved is not None:
            engine.mod.COMMAND_TIMEOUT_SECONDS = COMMAND_CAP_SECONDS
            engine.mod.SUITE_COMMAND_TIMEOUT_SECONDS = COMMAND_CAP_SECONDS
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
                futs = {pool.submit(run_case, engine, box, c): c for c in pooled}
                for f in concurrent.futures.as_completed(futs):
                    results[futs[f].id] = f.result()
        finally:
            if saved is not None:
                engine.mod.COMMAND_TIMEOUT_SECONDS, engine.mod.SUITE_COMMAND_TIMEOUT_SECONDS = saved
        for c in serial:
            results[c.id] = run_case(engine, box, c)
    wall = time.monotonic() - t0
    mismatches, failures, tracebacks, deviated, filled, added = [], 0, 0, 0, 0, 0
    ok_cells = {"R": 0, "N": 0, "C": 0}
    dump = {}
    for c in [*pooled, *serial]:
        got, tb, secs = results[c.id]
        if got is None:
            failures += 1
            tracebacks += tb.count("Traceback")
            mismatches.append(f"{c.id} — 실행 실패\n    " + tb.strip().replace("\n", "\n    "))
            continue
        dump[c.id] = {"name": c.name, "group": c.group, "bundle": c.bundle, "kind": c.kind, "seconds": round(secs, 2), "cells": got}
        diffs, dev, env_filled, impl_added = compare(c, want_all.get(c.id), got, engine)
        mismatches += diffs
        deviated += dev
        filled += env_filled
        added += impl_added
        if not diffs:
            ok_cells[c.group] += 2
    if args.dump:
        args.dump.write_text(json.dumps({"engine": engine.label, "cases": dump}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for line in problems + mismatches:
        print("  ✗ " + line)
    total = 2 * (len(pooled) + len(serial))
    matched = sum(ok_cells.values())
    slow = sorted(((results[c.id][2], c.id) for c in [*pooled, *serial]), reverse=True)[:3]
    print(f"{'PASS' if matched == total and not problems else 'FAIL'} — 가장 느린 사례 " + " · ".join(f"{i} {s:.1f}초" for s, i in slow))
    skip_note = f"건너뜀 {2 * len(skipped)}(원형에 상한 상수 없음) · " if skipped else ""
    print(f"요약: 칸 {matched}/{total} 일치 · 다름 {len(mismatches)} · 실행 실패 {failures} · traceback {tracebacks} · "
          f"{skip_note}편차 범위 뺀 칸 {deviated} · 환경 값 채운 칸 {filled} · 구현판 사유 더한 칸 {added} · R {ok_cells['R']} · N {ok_cells['N']} · C {ok_cells['C']} · {wall:.1f}초 · 병렬 {jobs}")
    return 0 if matched == total and not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
