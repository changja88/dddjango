#!/usr/bin/env python3
"""dddjango 배포 코퍼스 문면 위생 lint — S2.5 (메인테이너/빌드타임 — 런타임 게이트 아님).

배경: 코퍼스는 사람이 아니라 AI 파이프라인 에이전트가 읽는다. 라운드 2~3 의 STOP·오독은
코드가 아니라 문면(모순·죽은 참조·번호 공간 혼동)이 원인이었다 — 이 lint 는 그 부류의
드리프트를 결정적으로 탐지한다. spec_lint·corpus_mirror_sync 와 같은 부류라 registry 밖이다.

여섯 검사 (계획 workspace/plan/2026-08-14-s2p5-copy-hygiene.md §5.5·§6):
  ① 죽은 저장소 경로  배포 md 코퍼스 안 `workspace/…` 경로 — 설치본에서 해석 불가
  ② 끊긴 번호       무접두 #N=명세 규칙(생존 집합) · «registry #N»=1..27 ·
                    «의사결정 #N»=그 파일 안 `[의사결정 #N]` 선언 집합 · D N=생존 카드.
                    한계(정직 기록): 무접두 registry 순번이 생존 규칙 번호와 겹치면 기계로
                    못 가른다 — commands 머리의 번호 공간 규약 문장이 사람 판별의 근거다.
  ③ 별칭 혼용       걷어낸 어휘 재등장 — md 는 «위치 기반 allowlist»(파일·앵커·기대 건수 —
                    문맥 휴리스틱 금지: «→» 류는 준-와일드카드다) · 스크립트는 문자열 상수
                    ≥20자만(검출 튜플 보존 — 주석·검출-자리 옛 이름 인용은 checker_lint 계약)
  ④ 재량 낱말       규범 4부류(houserules final.md·SKILL.md 전부·agents·commands) 한정 —
                    고정 토큰 «트립와이어»다(재량-위임 부류 검출기가 아니다 — 부류는 정독 스윕 소유)
  ⑤ 같은-문서 중복   펜스 제외·정규화 동일(≥40자) — allowlist 는 (파일·지문·기대 건수)
  ⑥ 트리-밖 예시 경로 final.md 의 `application/…` 경로꼴 ↔ standard_tree 자리표시자 대조.
                    한계(정직 기록): 자리표시자-형태와 우연히 일치하는 의미 오류는 못 잡는다.

self-test 가 매 호출에 선행한다 — 합성 red/green 케이스(수정-목록-밖 변형 포함)로 각 검사의
검출력을 실증한 뒤 실제 코퍼스를 검사한다(«검사를 좁혀서 green» 순환 차단 — 계획 §6 G6).

fail-CLOSED: 파일 부재·파싱 실패·self-test 실패는 exit 3.

exit: 0=clean · 2=위반 · 3=구조 전제 깨짐 · 1=usage
사용: python3 workspace/tools/corpus_lint.py [--root <저장소>]
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
import tempfile
from pathlib import Path

EXIT_CLEAN = 0
EXIT_USAGE = 1
EXIT_VIOLATION = 2
EXIT_STRUCTURE = 3

SPEC_REL = "workspace/design/2026-08-08-tree-revision-spec.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import spec_lint  # noqa: E402  — load_rules(텍스트)·LIVE_CARDS 재사용(경로 무의존)


class StructureError(Exception):
    """구조 전제 위반 → fail-closed(exit 3)."""


# ──────────────────────────────────────────────────────────── 대상 수집

def collect_docs(root: Path) -> "list[Path]":
    skills = root / "dddjango" / "skills"
    docs = (
        sorted(skills.glob("*/references/final.md"))
        + sorted(skills.glob("*/SKILL.md"))
        + sorted((root / "dddjango" / "agents").glob("*.md"))
    )
    cmd = root / "dddjango" / "commands" / "dddjango.md"
    if cmd.is_file():
        docs.append(cmd)
    if not docs:
        raise StructureError(f"배포 md 코퍼스 0건: {skills}")
    return docs


def collect_scripts(root: Path) -> "list[Path]":
    return sorted((root / "dddjango" / "scripts").glob("*.py"))


def is_normative(root: Path, p: Path) -> bool:
    """④ 의 «규범 4부류» — houserules final.md · SKILL.md 전부 · agents · commands."""
    rel = p.relative_to(root).as_posix()
    return (
        rel.endswith("discipline-houserules/references/final.md")
        or rel.endswith("SKILL.md")
        or "/agents/" in rel
        or rel.endswith("commands/dddjango.md")
    )


def _rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix()


# ──────────────────────────────────────────────────────────── ① 죽은 저장소 경로

WORKSPACE_PATH = re.compile(r"workspace/[\w\-./]+")


def check_dead_repo_paths(root: Path, docs: "list[Path]") -> "list[str]":
    out = []
    for p in docs:
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for m in WORKSPACE_PATH.finditer(line):
                out.append(f"① 죽은 저장소 경로: {_rel(root, p)}:{i} «{m.group(0)[:60]}»")
    return out


# ──────────────────────────────────────────────────────────── ② 끊긴 번호

REF_NUM = re.compile(r"#(\d{1,3})\b")
DECISION_DECL = re.compile(r"\[의사결정\s*#(\d+)\]|\*\*의사결정\s*#(\d+)\*\*")  # 대괄호형(ddd)·볼드형(python)
DECISION_REF = re.compile(r"의사결정\s*#(\d+)")
CARD_REF = re.compile(r"\bD(\d{1,2})\b")
REGISTRY_MAX = 27


def _load_live_rules(root: Path) -> "set[int]":
    spec = root / SPEC_REL
    if not spec.is_file():
        raise StructureError(f"명세 부재: {spec}")
    return {r.num for r in spec_lint.load_rules(spec.read_text(encoding="utf-8"))}


def check_broken_numbers(root: Path, docs: "list[Path]", scripts: "list[Path]") -> "list[str]":
    live = _load_live_rules(root)
    out = []
    for p in docs + scripts:
        text = p.read_text(encoding="utf-8")
        declared = {int(a or b) for a, b in DECISION_DECL.findall(text)}
        for i, line in enumerate(text.splitlines(), 1):
            # «registry #2·#15·#6» — registry 접두 뒤 ·/, 로 이어진 리스트 전체가 순번 공간이다(번호 공간 규약)
            ordinal_spans = [m.span() for m in re.finditer(r"registry\s*#\d+(?:\s*[·,]\s*#\d+)*", line, re.I)]
            for m in REF_NUM.finditer(line):
                n = int(m.group(1))
                before = line[: m.start()]
                if before.endswith("]("):  # markdown 앵커 링크 `](#6-…)`
                    continue
                if any(a <= m.start() < b for a, b in ordinal_spans):
                    if not (1 <= n <= REGISTRY_MAX):
                        out.append(f"② 없는 registry 순번: {_rel(root, p)}:{i} registry #{n}")
                    continue
                if re.search(r"의사결정\s*$", before):
                    if n not in declared:
                        out.append(f"② 선언 없는 의사결정 번호: {_rel(root, p)}:{i} 의사결정 #{n}")
                    continue
                if re.search(r"(이슈|issue|PR)\s*$", before, re.I):
                    continue
                if n not in live:
                    out.append(f"② 끊긴 규칙 번호: {_rel(root, p)}:{i} #{n} :: {line.strip()[:70]}")
            for m in CARD_REF.finditer(line):
                n = int(m.group(1))
                if n < 60 and n not in spec_lint.LIVE_CARDS:
                    out.append(f"② 없는 결정 카드: {_rel(root, p)}:{i} D{n}")
    return out


# ──────────────────────────────────────────────────────────── ③ 별칭 혼용

# 위치 기반 allowlist — (파일 suffix, 그 줄의 앵커 문면, 기대 건수 상한).
# 문맥 휴리스틱(«→» 등) 금지 — 계획 §6 G4. 새 정당 인용이 생기면 여기 «사유와 함께» 행을 더한다.
AliasAllow = "tuple[str, str, int]"
ALIAS_TOKENS: "dict[str, tuple[tuple[str, str, int], ...]]" = {
    # 걷어낸 옛 층·칸 이름 — 정당 인용은 이관 기록·금지 규칙 문면뿐
    r"presentation_layer": (
        ("discipline-houserules/references/final.md", "옛 판(4계층", 1),
        ("discipline-houserules/references/final.md", "쓰지 않는다", 1),
        ("discipline-houserules/references/final.md", "옛 이름(", 1),
        ("discipline-houserules/SKILL.md", "옛 이름이 새 코드에", 1),
    ),
    r"infra_layer": (
        ("discipline-houserules/references/final.md", "옛 판(4계층", 1),
        ("discipline-houserules/references/final.md", "옛 이름(", 1),
        ("discipline-houserules/SKILL.md", "옛 이름이 새 코드에", 1),
        ("check-db-table.py", "층 이름 위장", 1),
    ),
    r"published[_ ]service": (
        ("discipline-houserules/references/final.md", "옛 이름(", 1),
        ("discipline-houserules/SKILL.md", "옛 이름이 새 코드에", 1),
        ("check-context-isolation.py", "published_service 금지", 1),
        ("check-context-isolation.py", "타 BC 입구는", 1),
    ),
    r"dto_(?:in|out)": (),
    r"(?<![\w])ErrorOut": (),
    r"(?<![\w])error_out\b": (),
    r"query_repository": (),
    r"(?<![\w/])reference/final\.md": (),  # 단수 오기 — 정본 디렉터리는 references/
}
SCRIPT_STRING_MIN = 20  # 이 미만은 검출 튜플·짧은 키로 보고 보존한다(계획 §6 G9)


def _alias_allowed(pat: str, rel: str, line: str, allows: "tuple[tuple[str, str, int], ...]",
                   used: "dict[tuple[str, str, str], int]") -> bool:
    for suffix, anchor, cap in allows:
        if rel.endswith(suffix) and anchor in line:
            key = (pat, suffix, anchor)  # 토큰별 독립 카운트 — 같은 줄의 다른 토큰이 서로를 소진하면 안 된다
            used[key] = used.get(key, 0) + 1
            return used[key] <= cap
    return False


def check_aliases(root: Path, docs: "list[Path]", scripts: "list[Path]") -> "list[str]":
    out = []
    used: "dict[tuple[str, str, str], int]" = {}
    for p in docs:
        rel = _rel(root, p)
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for pat, allows in ALIAS_TOKENS.items():
                if re.search(pat, line) and not _alias_allowed(pat, rel, line, allows, used):
                    out.append(f"③ 별칭 혼용: {rel}:{i} «{pat}» :: {line.strip()[:70]}")
    for p in scripts:
        rel = _rel(root, p)
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError as e:  # fail-closed — 침묵 스킵 금지(F-A 교훈)
            raise StructureError(f"스크립트 파싱 실패: {rel} — {e}")
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value) >= SCRIPT_STRING_MIN:
                for pat, allows in ALIAS_TOKENS.items():
                    if re.search(pat, node.value) and not _alias_allowed(pat, rel, node.value, allows, used):
                        out.append(
                            f"③ 별칭 혼용(스크립트 문자열): {rel}:{node.lineno} «{pat}» :: {node.value.strip()[:70]}"
                        )
    return out


# ──────────────────────────────────────────────────────────── ④ 재량 낱말

DISCRETION = re.compile(r"적절히|필요시|필요에 따라|상황에 따라|알아서|유연하게|알맞게|적당히|재량껏")


def check_discretion(root: Path, docs: "list[Path]") -> "list[str]":
    out = []
    for p in docs:
        if not is_normative(root, p):
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            m = DISCRETION.search(line)
            if m:
                out.append(f"④ 재량 낱말: {_rel(root, p)}:{i} «{m.group(0)}» :: {line.strip()[:70]}")
    return out


# ──────────────────────────────────────────────────────────── ⑤ 같은-문서 중복

# (파일 suffix, 정규화 지문 앞 40자, 기대 건수) — 의도 반복은 사유와 함께만 등재한다.
DUP_ALLOW: "tuple[tuple[str, str, int], ...]" = (
    # ninja wire 계약 문장 — 앵커가 축자 반복을 요구하는 계약 문면(라운드 2 앵커 재료)이라 의도 반복
    ("implementation-django-ninja/references/final.md", "populated BC-base `ErrorSchema`, 필요하면 주입된 응답용", 2),
)


def check_same_doc_dup(root: Path, docs: "list[Path]") -> "list[str]":
    out = []
    for p in docs:
        rel = _rel(root, p)
        seen: "dict[str, list[int]]" = {}
        fence = False
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip().startswith("```"):
                fence = not fence
                continue
            if fence:
                continue
            key = re.sub(r"\s+", " ", line.strip().replace("**", ""))
            if len(key) < 40 or key.startswith(("|--", "| --", "<!--")) or re.match(r"^\|?[\s\-|:]+$", key):
                continue
            seen.setdefault(key, []).append(i)
        for key, lines in seen.items():
            if len(lines) < 2:
                continue
            cap = 1
            for suffix, fp, allowed in DUP_ALLOW:
                if rel.endswith(suffix) and key.startswith(fp):
                    cap = allowed
                    break
            if len(lines) > cap:
                out.append(f"⑤ 같은-문서 중복: {rel} 행 {lines} (기대 {cap}) :: {key[:60]}")
    return out


# ──────────────────────────────────────────────────────────── ⑥ 트리-밖 예시 경로

# 의도적 반례(문서가 «나쁜 예»로 트리-밖 경로를 보여주는 자리) — 사유와 함께만 등재한다.
TREE_PATH_ALLOW: "tuple[tuple[str, str], ...]" = (
    # (파일 suffix, 경로 그대로)
)

APP_PATH = re.compile(r"application/[A-Za-z0-9_<>./*]+")
APP_IMPORT = re.compile(r"from\s+(application\.[\w.]+)\s+import")


def _load_tree(root: Path):
    """루트별 standard_tree 를 명시 경로로 로드한다(캐시·reload 함정 회피)."""
    import importlib.util

    path = root / "dddjango" / "scripts" / "standard_tree.py"
    if not path.is_file():
        raise StructureError(f"standard_tree 부재: {path}")
    name = f"_corpus_lint_tree_{abs(hash(str(path)))}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise StructureError(f"standard_tree 로드 실패: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # dataclass 가 cls.__module__ 를 sys.modules 에서 찾는다
    spec.loader.exec_module(mod)
    return mod


def _seg_matches(row_name: str, seg: str, is_last: bool, seg_is_file: bool) -> bool:
    row_is_dir = row_name.endswith("/")
    name = row_name.rstrip("/")
    if "/" in name:  # 복합 이름(admin·templates 계열) — 첫 성분만 대조
        name = name.split("/")[0]
    if seg_is_file and is_last and row_is_dir:
        return False
    if (not seg_is_file) and (not row_is_dir) and is_last:
        return False
    if "<" in seg:  # 문서 쪽 자리표시자 — 그 깊이의 아무 행과나 대응
        return True
    if "<" in name:  # 트리 쪽 자리표시자 — 리터럴 이스케이프 후 <x> 를 스네이크 토큰으로
        esc = ""
        rest = name
        while "<" in rest:
            pre, _, tail = rest.partition("<")
            _ph, _, rest = tail.partition(">")
            esc += re.escape(pre) + r"[a-z0-9_]+"
        esc += re.escape(rest)
        return re.fullmatch(esc, seg) is not None
    return name == seg


def _walk_tree(rows_children, node, segs) -> bool:
    """segs 를 트리 아래로 소진할 수 있으면 True. 리프로 닫힌 폴더 아래는 재량(#490)."""
    if not segs:
        return True
    kids = rows_children(node)
    if node is not None and not kids and node.name.endswith("/"):
        return True  # 리프 폴더 안 추가 모듈은 재량
    seg = segs[0]
    is_last = len(segs) == 1
    seg_is_file = "." in seg and not seg.endswith("/")
    for k in kids:
        if _seg_matches(k.name, seg.rstrip("/"), is_last, seg_is_file):
            if is_last:
                return True
            if k.name.endswith("/"):
                if _walk_tree(rows_children, k, segs[1:]):
                    return True
    return False


def check_offtree_paths(root: Path, docs: "list[Path]") -> "list[str]":
    st = _load_tree(root)
    bc_row = st.ROWS[0]  # application/<bounded_context>/
    out = []
    finals = [p for p in docs if p.name == "final.md"]
    for p in finals:
        rel = _rel(root, p)
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            paths: "list[tuple[str, bool]]" = []  # (경로, import 꼴 여부)
            for m in APP_IMPORT.finditer(line):
                paths.append((m.group(1).replace(".", "/"), True))
            for m in APP_PATH.finditer(line):
                paths.append((m.group(0), False))
            for raw, from_import in paths:
                path = raw.rstrip(".·,;:)»]}'\"")
                if any(rel.endswith(sfx) and path == allowed for sfx, allowed in TREE_PATH_ALLOW):
                    continue
                segs = [s for s in path.split("/") if s]
                if len(segs) < 3 or segs[0] != "application":
                    continue
                if "*" in path:  # 와일드카드 서술(`**` 등)은 형태 서술이라 대상 밖
                    continue
                # 산문 슬래시 열거(«application/service/usecase 계층» 류) 오탐 차단 —
                # 검사 대상은 «트리 경로 주장»뿐: import 꼴이거나, 층·칸 낱말을 지나거나, .py 로 끝나는 것.
                CELL_TOKENS = ("driving_layer", "driven_layer", "domain_layer", "application_layer",
                               "composition_root", "published_event", "framework", "test")
                if not from_import and not path.endswith(".py") and not any(t in segs for t in CELL_TOKENS):
                    continue
                if any(not re.fullmatch(r"[a-z0-9_.<>]+", s) for s in segs[1:]):
                    continue  # 대문자 성분 등 — 경로 주장 아님
                body = segs[2:]  # application/<bc>/ 이후
                ok = _walk_tree(st.children, bc_row, body)
                if not ok and from_import:
                    # import 꼴은 파일(.py 생략)일 수도 패키지일 수도 있다 — 둘 중 하나면 통과
                    ok = _walk_tree(st.children, bc_row, body[:-1] + [body[-1] + ".py"])
                if not ok:
                    out.append(f"⑥ 트리-밖 예시 경로: {rel}:{i} «{path[:80]}»")
    return out


# ──────────────────────────────────────────────────────────── self-test

_MINI_SPEC = """\
| # | 규칙 | 자리 | 판정 | 근거 | 메모 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 1 | 미니 규칙 하나 | 트리 1행 | path | d |  | blocker |
| 95 | 미니 규칙 둘 | 트리 22행 | ast | d |  | blocker |
"""

_BAD_FINAL = """\
# 미니 코퍼스 (bad)

죽은 경로 고전형은 `workspace/reference/implementation-python/reference/final.md` 를 참조한다.
죽은 경로 변형은 `workspace/plan/2026-01-01-foo.md` 를 참조한다.
끊긴 규칙은 #999 를 가리킨다. 없는 순번은 registry #99 다. 선언 없는 의사결정 #9 도 있다. 죽은 카드는 D19 다.
옛 층 이름 `presentation_layer/` 를 규범 문장에 쓴다.
화살표 세탁 시도: `error_out` 모듈에 둔다(→ §5 참조).
단수 오기는 그 `reference/final.md` 를 참조한다.
이 문장은 마흔 자를 넘기는 같은-문서 중복 실증용 규범 문장이다 — 반복 하나.
이 문장은 마흔 자를 넘기는 같은-문서 중복 실증용 규범 문장이다 — 반복 하나.
이 문장은 마흔 자를 넘기는 같은-문서 중복 실증용 규범 문장이다 — 반복 하나.

```python
from application.order.driven_layer.acl.product_stock_adapter import X
```
"""

_GOOD_FINAL = """\
# 미니 코퍼스 (good)

[의사결정 #1] 스킬 이름 참조는 `implementation-python` §26 을 따른다. 규칙 #1 과 #95 는 생존이다.
의사결정 #1 재인용과 registry #2 와 D50 은 전부 정합이다.

```python
from application.order.driven_layer.adapter.persistence.repository.order_repository import X
```
"""

_BAD_SKILL = "# t\n\n작업은 상황에 맞게 적절히 진행하고 알맞게 마무리한다.\n"
_GOOD_SKILL = "# t\n\n작업 판정은 명시된 물음으로만 한다.\n"

_BAD_SCRIPT = 'MSG = "common ErrorOut의 project import는 runtime proof 필요"\nT = ("ErrorOut", "ErrorSchema")\n'
_GOOD_SCRIPT = 'MSG = "common FrameworkErrorSchema의 project import는 proof 필요"\nT = ("ErrorOut", "ErrorSchema")\n'


def _build_mini_root(base: Path, bad: bool) -> Path:
    root = base / ("bad" if bad else "good")
    (root / "workspace" / "design").mkdir(parents=True)
    (root / SPEC_REL).write_text(_MINI_SPEC, encoding="utf-8")
    sk = root / "dddjango" / "skills" / "testskill"
    (sk / "references").mkdir(parents=True)
    (sk / "references" / "final.md").write_text(_BAD_FINAL if bad else _GOOD_FINAL, encoding="utf-8")
    (sk / "SKILL.md").write_text(_BAD_SKILL if bad else _GOOD_SKILL, encoding="utf-8")
    (root / "dddjango" / "agents").mkdir(parents=True)
    sc = root / "dddjango" / "scripts"
    sc.mkdir(parents=True)
    (sc / "check-mini.py").write_text(_BAD_SCRIPT if bad else _GOOD_SCRIPT, encoding="utf-8")
    # standard_tree 는 실물 사본을 쓴다(⑥ 의 판정 재료 — 트리 값 자체가 검사 대상이 아니라 잣대)
    real = Path(__file__).resolve().parents[2] / "dddjango" / "scripts" / "standard_tree.py"
    (sc / "standard_tree.py").write_text(real.read_text(encoding="utf-8"), encoding="utf-8")
    return root


def run_checks(root: Path) -> "list[str]":
    docs = collect_docs(root)
    scripts = [p for p in collect_scripts(root) if p.name != "standard_tree.py"]
    findings: "list[str]" = []
    findings += check_dead_repo_paths(root, docs)
    findings += check_broken_numbers(root, docs, scripts)
    findings += check_aliases(root, docs, scripts)
    findings += check_discretion(root, docs)
    findings += check_same_doc_dup(root, docs)
    findings += check_offtree_paths(root, docs)
    return findings


def self_test() -> None:
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        bad = _build_mini_root(base, bad=True)
        good = _build_mini_root(base, bad=False)
        bad_f = run_checks(bad)
        good_f = run_checks(good)
        kinds = {f[0] for f in bad_f}
        need = {"①", "②", "③", "④", "⑤", "⑥"}
        missing = need - kinds
        if missing:
            raise StructureError(f"self-test 실패 — bad 케이스에서 미발화: {sorted(missing)} (발화 {sorted(kinds)})")
        # 목록-밖 변형 검출 실증(G6): 비-reference 죽은 경로 · 단수 오기 · 화살표-줄 별칭
        for token in ("workspace/plan/2026-01-01-foo.md", "reference/final\\.md", "error_out"):
            if not any(token in f for f in bad_f):
                raise StructureError(f"self-test 실패 — 목록-밖 변형 미검출: «{token}»")
        if good_f:
            raise StructureError(f"self-test 실패 — good 케이스 오발화 {len(good_f)}건: {good_f[:3]}")


# ──────────────────────────────────────────────────────────── main

def main(argv: "list[str]") -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="저장소 루트")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        self_test()
        findings = run_checks(root)
    except StructureError as e:
        print(f"구조 전제 깨짐: {e}", file=sys.stderr)
        return EXIT_STRUCTURE
    docs_n = len(collect_docs(root))
    print(f"self-test ✓ · md {docs_n} · 스크립트 {len(collect_scripts(root))}")
    if findings:
        for f in findings:
            print(" ", f)
        print(f"위반 {len(findings)}건")
        return EXIT_VIOLATION
    print("위반 0건")
    return EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
