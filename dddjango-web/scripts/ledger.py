#!/usr/bin/env python3
r"""ledger — 미검증 원장 (dddjango-web).

게이트는 **막는 장치가 아니라 비용을 기록하는 장치**다. 사용자가 사실을 알고 진행을 지시하면
길이 있어야 하고, 게이트의 역할은 «무엇이 미검증인지» 를 지우지 못하게 남기는 것이다.

원장은 `check_design_evidence.validate_inputs` 가 발견을 확정하는 **한 자리**에서 조회된다
(`if issues: raise Defects(issues)` 직전). 그 자리를 고른 이유:

  · `main()` 의 `except Defects` 에 두면 **`backstop.py` 가 안 지난다** — backstop 은
    `validate_inputs` 를 인프로세스로 직접 부르고 자기 `except Defects` 를 갖는다.
    게이트의 절반(G2 직전·마무리)이 원장을 모른 채 같은 발견으로 막는다.
  · 거기서 exit 0 을 내면 `run()` 이 중단된 뒤라 **두 digest 를 못 내고**(→ `visual-evidence.json`
    을 쓸 수 없어 G2 가 영구 차단된다) **`validate_visual` 이 통째로 건너뛰어진다**(→ 시각 검증
    전량 무검증 통과).
  · `issues` 묶음에만 붙으므로 **조기 `raise Defects([...])` 5곳은 구조적으로 원장 밖이다**
    (design-input.json 판독·최상위 필드·web 디렉터리·심링크 2종). 그 한 줄을 등재하면 다른
    모든 검사가 단락되는 «한 줄짜리 마스터키» 가 성립하지 않는다. 열거식 거부 목록이 필요 없다.

천장(원장이 받지 않는 발견):
  · `interaction evidence required (version N with interactions)` — 관찰 자체를 안 했다.
    열면 «드라이버를 안 잇는 것» 이 가장 싼 길이 된다.
  · `coverage_review: … does not match` — 검토 문서 재생성으로 **항상** 닫힌다.

사용:
  python ledger.py add  --build <빌드> --project-root <루트> --phase <prepare|inputs|visual> \
                        --index <발견 번호> --quote "<사용자 승인 원문>" --scope-ref "<경로>#<앵커>"
  python ledger.py list --build <빌드>
  python ledger.py drop --build <빌드> --key <키>

`add` 는 스스로 검사기를 돌려 발견 목록을 만들고 `--index` 가 가리키는 발견만 등재한다
(에이전트가 문자열을 지어낼 자리가 없다). 등재 직후 **다시 돌려 그 발견이 실제로 사라졌는지
확인** 하고, 사라지지 않으면 행을 철회한다 — `--index` 는 두 실행 사이의 서수이므로 자기 검증이
붙어야 «사용자의 인용이 다른 발견에 붙는» 사고를 막는다.

exit: 0=성공 / 1=사용법·입력 오류 / 2=거부(천장·앵커·자기 검증 실패)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

LEDGER_NAME = "evidence-ledger.json"
SCOPE_DOCUMENT = "scope.md"
VERSION = 1
SCRIPTS = Path(__file__).resolve().parent

QUOTED_RE = re.compile(r"'[^']*'")
COUNT_RE = re.compile(r"(\d+)\s*(건|행|개)")
TUPLES_RE = re.compile(r"\((?:…|None|True|False|[,\s])*\)(?:[,\s]*\((?:…|None|True|False|[,\s])*\))*")
SPACE_RE = re.compile(r"\s+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
EXPLICIT_RE = re.compile(r"\{#([^}\s]+)\}\s*$")
DEFECT_RE = re.compile(r"^\[design-evidence\] defect(?:\[(\w+)\])?: (.*)$")

# 원장은 **허용 목록**이다 — 거부 목록이 아니다.
#
# 거부 목록이면 «열거되지 않은 것이 기본 개방» 이라 단락 경로 하나가 마스터키가 된다:
# `design-input.json` 의 `cases` 를 `[]` 로 바꾸면 발견이 1건이고, 그 1건을 등재하면 계산조차 안 된
# 부분트리 전체가 열린다(실측: 발견 13→0 · digest_items 49→25). `validate_inputs` 안에만 그런
# 단락 경로가 25곳이라 전부 열거하는 것은 불가능하다.
#
# 그리고 **문자열 매칭으로 판정을 식별하면 안 된다.** 검사기 메시지에는 에이전트가 정하는 문자열
# (포인터 경로·case id·표면 이름)이 그대로 박히므로 사용자 데이터가 판정을 사칭할 수 있다
# (실측: 관찰 경로를 `captures/잔여 1건 — none.json` 으로 두니 «관찰 미실시» 발견이 «잔여» 로
# 승격돼 §3 천장이 뚫렸다). 그래서 `check_design_evidence` 가 **발견을 내는 그 자리에서**
# 판정 종류를 실어 보내고(`verdict()`), 원장은 그 종류만 받는다.
KINDS = ('residual', 'exclusion_cap', 'surface', 'partial')
#   판정 종류마다 키를 만들 때 지울 부분이 다르다 — `residual` 은 튜플 목록을 접어야 키가 안정되고,
#   `surface` 는 표면 이름을 **남겨야** 승인 1건이 그 문서의 모든 표면을 열지 않는다.
FOLD = {'residual': ('quoted', 'count', 'tuples'), 'exclusion_cap': ('count',),
        'surface': ('count',), 'partial': ('count',)}

def slug(title: str) -> str:
    """앵커 슬러그는 검사기가 정본이다 — 규칙이 갈리면 승인이 조용히 빗나간다.

    지연 import 다: `check_design_evidence` 가 이 모듈을 최상위에서 부르므로 여기서
    최상위 import 를 하면 순환이 된다(호출 시점에는 이미 적재돼 있다)."""
    from check_design_evidence import _slug
    return _slug(title)


def normalize(message: str, kind: str | None = None) -> str:
    """규모와 열거를 지운 뒤에도 **발견의 정체는 남는** 형태로 접는다.

    `cases[N]` 인덱스는 어느 경우에도 보존한다(지우면 승인 1건이 12건을 연다)."""
    text = message
    for step in FOLD.get(kind or "", ("quoted", "count", "tuples")):
        if step == "quoted":
            text = QUOTED_RE.sub("…", text)
        elif step == "count":
            text = COUNT_RE.sub(lambda m: f"#{m.group(2)}", text)
        elif step == "tuples":
            text = TUPLES_RE.sub("(…)", text)
    return SPACE_RE.sub(" ", text).strip()


def key_of(message: str, kind: str | None = None) -> str:
    return hashlib.sha256(f"{kind}\x1f{normalize(message, kind)}".encode("utf-8")).hexdigest()[:16]


def magnitude_of(message: str) -> int | None:
    """계수 단위(건·행·개) 앞 **첫** 정수. 없으면 None.

    모든 정수를 쓰면 hex target id 파편이 섞이고, 둘째 정수(«활성 대상 M개»)는 커질수록
    유리한 값이라 개선에도 재승인을 강요한다."""
    match = COUNT_RE.search(QUOTED_RE.sub("…", message))
    return int(match.group(1)) if match else None


def refusal(message: str, kind: str | None) -> str | None:
    """종류가 없으면 여는 대상이 아니다(기본 폐쇄)."""
    if kind in KINDS:
        return None
    if "interaction evidence required" in message:
        return ("관찰 자체를 안 한 발견이다 — 원장으로 열면 드라이버 미연결이 가장 싼 길이 된다. "
                "부분 관찰이라도 먼저 한다")
    return ("원장이 받는 것은 검사기가 끝까지 계산한 뒤 내리는 판정(잔여·예외 상한·새 표면·partial)뿐이다. "
            "이 발견은 구조가 깨졌거나 계산이 안 됐다는 뜻이라 여는 대상이 아니다")


def section_of(text: str, anchor: str) -> tuple[str, int] | None:
    """앵커가 가리키는 절의 본문과 제목 수준. 제목 앵커가 아니면 None."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        heading = HEADING_RE.match(line)
        if not heading:
            continue
        level, title = len(heading.group(1)), heading.group(2)
        explicit = EXPLICIT_RE.search(title)
        names = {explicit.group(1)} if explicit else set()
        names.add(slug(title[:explicit.start()] if explicit else title))
        if anchor not in names:
            continue
        body: list[str] = []
        for following in lines[index + 1:]:
            next_heading = HEADING_RE.match(following)
            if next_heading and len(next_heading.group(1)) <= level:
                break
            body.append(following)
        return "\n".join(body), level
    return None


def observation_fingerprint(build: Path) -> str:
    """cases[*].source_observation 하위의 모든 sha256 을 모아 하나로 접는다.

    규모만 보면 «잔여 38건 승인» 뒤에 전혀 다른 30건이 조용히 열린다 — 규모는 작아졌는데
    구성이 바뀐 경우다. 관찰이 바뀌면 승인은 무효이고 재승인이 필요하다(fail-closed)."""
    def walk(node, out):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "sha256" and isinstance(value, str):
                    out.append(value)
                else:
                    walk(value, out)
        elif isinstance(node, list):
            for item in node:
                walk(item, out)
    try:
        data = json.loads((build / "design-input.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    shas: list[str] = []
    for case in (data.get("cases") if isinstance(data, dict) else None) or []:
        if isinstance(case, dict):
            walk(case.get("source_observation"), shas)
    return hashlib.sha256("\n".join(sorted(shas)).encode("utf-8")).hexdigest()


def load(build: Path) -> dict:
    path = build / LEDGER_NAME
    if not path.is_file():
        return {"version": VERSION, "entries": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"version": VERSION, "entries": []}
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        return {"version": VERSION, "entries": []}
    return data


def save(build: Path, data: dict) -> None:
    (build / LEDGER_NAME).write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def valid_entries(build: Path) -> tuple[list[dict], list[str]]:
    """살아 있는 행과, 무효가 된 행의 사유.

    **fail-closed 다** — 승인 근거 필드가 하나라도 없거나 어긋나면 그 행은 없는 것이다.
    «있으면 검사» 로 두면 손으로 쓴 `{"key": "<16hex>"}` 한 줄이 승인 근거 0으로 유효 행이 되고
    허용 목록·천장·앵커·관찰 지문을 전부 우회한다(실측). 규범(«`ledger.py` 만 쓴다»)은 기제가
    아니다 — 조회에서 다시 본다."""
    alive, dead = [], []
    fingerprint = observation_fingerprint(build)
    for entry in load(build).get("entries", []):
        if not isinstance(entry, dict):
            dead.append("행이 객체가 아니다")
            continue
        key, label, kind = entry.get("key"), entry.get("label"), entry.get("kind")
        quote, reference = entry.get("quote"), entry.get("scope_ref")
        anchor_hash, observed = entry.get("anchor_sha256"), entry.get("observation_sha256")
        where = key if isinstance(key, str) else "<키 없음>"
        if not all(isinstance(value, str) and value
                   for value in (key, label, kind, quote, reference, anchor_hash, observed)):
            dead.append(f"{where}: 승인 근거 필드가 빠졌다 — 손으로 쓴 행은 통행권이 아니다")
            continue
        if kind not in KINDS:
            dead.append(f"{where}: 알 수 없는 판정 종류 ({kind})")
            continue
        if key_of(label, kind) != key:
            dead.append(f"{where}: 키가 label·kind 와 맞지 않는다")
            continue
        document, _, anchor = reference.partition("#")
        if document != SCOPE_DOCUMENT or not anchor:
            dead.append(f"{where}: 승인 원문은 {SCOPE_DOCUMENT} 의 앵커 절에만 산다 ({reference})")
            continue
        try:
            text = (build / document).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            dead.append(f"{where}: 승인 문서를 읽을 수 없다 ({reference})")
            continue
        found = section_of(text, anchor)
        if found is None or found[1] < 2:
            dead.append(f"{where}: H2 이상 제목 앵커가 아니다(또는 사라졌다) ({reference})")
            continue
        body, _level = found
        if hashlib.sha256(body.encode("utf-8")).hexdigest() != anchor_hash:
            dead.append(f"{where}: 승인 절이 바뀌었다 — 재승인이 필요하다 ({reference})")
            continue
        if SPACE_RE.sub(" ", quote).strip() not in SPACE_RE.sub(" ", body):
            dead.append(f"{where}: 승인 원문이 그 절 본문 안에 없다 ({reference})")
            continue
        if observed != fingerprint:
            dead.append(f"{where}: 관찰이 바뀌었다 — 규모가 같아도 구성이 다를 수 있다. 재승인이 필요하다")
            continue
        alive.append(entry)
    return alive, dead


def filter_issues(build: Path, issues: list[str],
                  verdicts: dict[str, str] | None = None) -> tuple[list[str], list[str], list[str]]:
    """(남은 발견, 원장이 연 발견, 고지) — check_design_evidence 가 부른다.

    `verdicts` 는 검사기가 발견을 내며 실어 보낸 «판정 종류» 다. 거기 없는 메시지는 어떤 원장 행이
    있어도 열리지 않는다 — 사용자 데이터가 판정을 사칭할 수 없다."""
    verdicts = verdicts or {}
    alive, dead = valid_entries(build)
    by_key = {entry["key"]: entry for entry in alive}
    remaining, opened = [], []
    for message in issues:
        kind = verdicts.get(message)
        entry = by_key.get(key_of(message, kind)) if kind in KINDS else None
        if entry is None or entry.get("kind") != kind:
            remaining.append(message)
            continue
        approved, current = entry.get("magnitude"), magnitude_of(message)
        if isinstance(approved, int) and isinstance(current, int) and current > approved:
            remaining.append(f"{message} [원장 승인 규모 {approved} 초과 — 재승인이 필요하다]")
            continue
        opened.append(message)
    return remaining, opened, dead


def run_checker(build: Path, project: Path, phase: str) -> tuple[int, list[str]]:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "check_design_evidence.py"), "--build", str(build),
         "--project-root", str(project), "--phase", phase],
        capture_output=True, text=True)
    found = [(m.group(2), m.group(1)) for line in result.stderr.splitlines()
             if (m := DEFECT_RE.match(line.strip()))]
    return result.returncode, found


def cmd_add(args) -> int:
    build, project = args.build.resolve(), args.project_root.resolve()
    code, found = run_checker(build, project, args.phase)
    if code == 0:
        print("[ledger] 발견이 없다 — 등재할 것이 없다")
        return 1
    if code != 2:
        print(f"[ledger] 검사기가 미실행이다(exit {code}) — 원인을 먼저 고친다", file=sys.stderr)
        return 1
    if not 1 <= args.index <= len(found):
        print(f"[ledger] --index 는 1..{len(found)} 이다. 현재 발견:", file=sys.stderr)
        for number, (message, kind) in enumerate(found, 1):
            print(f"  {number}. [{kind or '—'}] {message}", file=sys.stderr)
        return 1
    message, kind = found[args.index - 1]
    reason = refusal(message, kind)
    if reason is not None:
        print(f"[ledger] 원장이 받지 않는 발견이다 — {reason}\n  {message}", file=sys.stderr)
        return 2

    document, _, anchor = args.scope_ref.partition("#")
    if not document or not anchor:
        print('[ledger] --scope-ref 는 "<경로>#<앵커>" 형식이다', file=sys.stderr)
        return 1
    if document != SCOPE_DOCUMENT:
        print(f"[ledger] 승인 원문은 {SCOPE_DOCUMENT} 에만 산다 — 에이전트가 쓰는 문서의 앵커로는"
              f" 승인이 성립하지 않는다 ({document})", file=sys.stderr)
        return 2
    try:
        text = (build / document).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"[ledger] 승인 문서를 읽을 수 없다: {error}", file=sys.stderr)
        return 1
    found_section = section_of(text, anchor)
    if found_section is None:
        print(f"[ledger] 제목 앵커가 아니다(또는 없다): {args.scope_ref}", file=sys.stderr)
        return 2
    body, level = found_section
    if level < 2:
        print(f"[ledger] 앵커는 H2 이상 깊이여야 한다 — H1 절은 파일 전체라 승인 범위가 되지 않는다"
              f" (현재 H{level})", file=sys.stderr)
        return 2
    quote = SPACE_RE.sub(" ", args.quote).strip()
    if len(quote) < 10:
        print(f"[ledger] 승인 원문은 10자 이상이어야 한다 ({quote!r})", file=sys.stderr)
        return 2
    if quote not in SPACE_RE.sub(" ", body):
        print(f"[ledger] 승인 원문이 그 절 본문 안에 없다 — {args.scope_ref}", file=sys.stderr)
        return 2

    entry = {"key": key_of(message, kind), "label": message, "kind": kind,
             "magnitude": magnitude_of(message),
             "phase": args.phase, "quote": quote, "scope_ref": args.scope_ref,
             "anchor_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
             "observation_sha256": observation_fingerprint(build),
             "approved_at": args.now}
    data = load(build)
    data["version"] = VERSION
    data["entries"] = [row for row in data.get("entries", [])
                       if not (isinstance(row, dict) and row.get("key") == entry["key"])]
    data["entries"].append(entry)
    save(build, data)

    after_code, after = run_checker(build, project, args.phase)
    if message in [text for text, _kind in after]:
        data["entries"] = [row for row in data["entries"] if row.get("key") != entry["key"]]
        save(build, data)
        print(f"[ledger] 자기 검증 실패 — 등재해도 그 발견이 그대로 남는다(행 철회). exit {after_code}",
              file=sys.stderr)
        return 2
    print(f"[ledger] 등재했다: {entry['key']} · 판정 {kind} · 규모 {entry['magnitude']} · {message}")
    print(f"[ledger] 남은 발견 {len(after)}건 (검사기 exit {after_code})")
    return 0


def cmd_list(args) -> int:
    build = args.build.resolve()
    alive, dead = valid_entries(build)
    for issue in dead:
        print(f"[ledger] 무효: {issue}")
    for entry in alive:
        print(f"{entry['key']}  {entry.get('kind')}  규모 {entry.get('magnitude')}  "
              f"{entry.get('scope_ref')}  {entry.get('label')}")
    print(f"[ledger] 유효 {len(alive)}행 · 무효 {len(dead)}행")
    return 0


def cmd_drop(args) -> int:
    build = args.build.resolve()
    data = load(build)
    before = len(data.get("entries", []))
    data["entries"] = [row for row in data.get("entries", []) if row.get("key") != args.key]
    save(build, data)
    removed = before - len(data["entries"])
    print(f"[ledger] {removed}행 제거 — 그 발견은 다시 막는다")
    return 0 if removed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="미검증 원장")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add")
    add.add_argument("--build", required=True, type=Path)
    add.add_argument("--project-root", required=True, type=Path)
    add.add_argument("--phase", required=True, choices=("prepare", "inputs", "visual"))
    add.add_argument("--index", required=True, type=int)
    add.add_argument("--quote", required=True)
    add.add_argument("--scope-ref", required=True)
    add.add_argument("--now", default=None)
    add.set_defaults(handler=cmd_add)
    show = sub.add_parser("list")
    show.add_argument("--build", required=True, type=Path)
    show.set_defaults(handler=cmd_list)
    drop = sub.add_parser("drop")
    drop.add_argument("--build", required=True, type=Path)
    drop.add_argument("--key", required=True)
    drop.set_defaults(handler=cmd_drop)
    args = parser.parse_args(argv)
    if getattr(args, "now", None) is None and args.command == "add":
        from datetime import datetime
        args.now = datetime.now().astimezone().isoformat(timespec="seconds")
    try:
        return args.handler(args)
    except (OSError, ValueError) as error:
        print(f"[ledger] 오류: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
