#!/usr/bin/env python3
"""check_clip_clearance — 클리핑 컨테이너의 링 여유 정적 검사 (dddjango-web).

포커스 링(바깥 box-shadow)은 스크롤·클리핑 컨테이너의 패딩 박스에서 잘린다. 컨테이너에
링 확장만큼의 패딩이 없으면 링이 통째로 사라진다 — A8 관계인 편집기에서 실제로 났다
(`.rpe-scroll{overflow-y:auto}` 패딩 0 · 링 3px → 좌우 절단).

**브라우저를 쓰지 않는다.** 이 결함의 컨테이너는 다이얼로그 안이라 초기 페이지 렌더 실측이
도달하지 못한다(실측 JSON 은 목록 페이지 한 장뿐이다). CSS 와 템플릿 텍스트만 읽는다.
정본: workspace/design/2026-09-15-web-clip-fidelity.md · 계획 …-plan.md T2.

사용:
  python check_clip_clearance.py <web 루트>

4단계:
  ① 링 규칙 수확 — `:focus*`·`:checked` 규칙의 바깥 box-shadow.
     **판정 확장 = spread + |offset| — blur 는 제외한다.** 실측(Chrome 픽셀): `0 0 20px 0` 의
     페인트 확장은 29px 로 `spread+blur/2`(10)도 `spread+blur`(20)도 아니다 — blur 그림자는
     «어디까지가 잘린 것인가»가 연속적이라 결정 판정에 부적합하다. blur>0 은 인벤토리로만 낸다.
  ② 클리핑 규칙 수확 — overflow(-x|-y): auto|scroll|hidden|clip.
     **축 전파**: 한 축이 visible 이 아니면 다른 축도 auto 로 계산된다(CSS 규칙) → 양축을 본다.
     이 전파가 이 결함의 기전이다 — `overflow-y:auto` 만 준 컨테이너가 가로로도 자른다.
  ③ 템플릿 조인 — 그 클래스를 선언한 템플릿과 include/extends 로 이어진 템플릿에서
     링을 지는 요소를 찾는다. 없으면 인벤토리(아바타·말줄임·sr-only 입력이 여기로 빠진다).
     조인 자체가 실패하면 «조인 실패» 로 명시한다 — 조용한 강등은 미탐 통로다.
  ④ 여유 판정 — 그 컨테이너에 실제로 적용되는 링의 확장과 패딩을 축별로 비교한다.
     **전역 최대 확장 금지** — 장식 고도 그림자가 임계를 지배하면 동결 시안을 정확히 구현한
     코드까지 반송된다.
     심각도: 여유 0 = «확정» · 0 < 여유 < 확장 = «경미».

지위는 compare_render_audit·check_motion_spec 과 동급 — **판단 자료(비차단)·배너 1급 의무 표기**.
exit: 0=발견 0 / 1=사용법·읽기 실패(미실행 취급 — 통과가 아니다) / 2=발견 ≥1
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
OVERFLOW_RE = re.compile(r"(?<![-\w])overflow(-[xy])?\s*:\s*([a-z-]+)")
BOX_SHADOW_RE = re.compile(r"(?<![-\w])box-shadow\s*:\s*([^;]+)")
PADDING_RE = re.compile(
    r"(?<![-\w])padding(-(?:top|right|bottom|left|inline|block|inline-start|inline-end"
    r"|block-start|block-end))?\s*:\s*([^;]+)")
LOGICAL = {"inline": ("left", "right"), "block": ("top", "bottom"),
           "inline-start": ("left",), "inline-end": ("right",),
           "block-start": ("top",), "block-end": ("bottom",)}
UNKNOWN = float("nan")  # 선언은 있는데 해석 불가(calc·미해소 var) — 0 으로 보면 오탐이다
VAR_DECL_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;]+)")
VAR_USE_RE = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,([^()]*))?\)")
CLASS_RE = re.compile(r"\.([A-Za-z_][\w-]*)")
LEN_RE = re.compile(r"(-?[0-9.]+)(px|rem|em)?")
COLORFN_RE = re.compile(r"[a-z-]+\([^()]*(?:\([^()]*\)[^()]*)*\)", re.I)
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}")
INCLUDE_RE = re.compile(r"\{%\s*include\s+[\"']([^\"']+)[\"']")
EXTENDS_RE = re.compile(r"\{%\s*extends\s+[\"']([^\"']+)[\"']")
BLOCK_RE = re.compile(r"\{%\s*block\s+\w+")
# Django 주석 — 산문 안의 리터럴 `<button>`·`<select>` 를 실제 요소로 오인하면 오탐이고,
# 그 오탐은 소스를 도구에 맞춰 훼손하게 만든다(실제로 났다: 부품 docstring 의 `<a>`·`<button>`
# 이 발견으로 잡혀 `a`·`button` 으로 고쳐졌다). 줄 수는 보존한다.
DJANGO_COMMENT_RE = re.compile(r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}|\{#.*?#\}", re.S)
RING_TRIGGER_RE = re.compile(r":focus(-visible|-within)?\b|:checked\b")
FOCUSABLE_RE = re.compile(r"<(input|button|select|textarea)\b|<a\s[^>]*href=|tabindex\s*=", re.I)
CLIPPING = ("auto", "scroll", "hidden", "clip")
SIDES = ("top", "right", "bottom", "left")
REM_BASE = 16.0
MAX_VAR_DEPTH = 6


def die(msg: str) -> None:
    print(f"[clip-clearance] {msg}", file=sys.stderr)
    sys.exit(1)


def px(value: str) -> float | None:
    m = LEN_RE.fullmatch(value.strip())
    if not m:
        return None
    n = float(m.group(1))
    return n * REM_BASE if m.group(2) in ("rem", "em") else n


def resolve(value: str, root_vars: dict[str, str], depth: int = 0) -> str:
    if depth > MAX_VAR_DEPTH or "var(" not in value:
        return value
    def sub(m: re.Match[str]) -> str:
        return (root_vars.get(m.group(1)) or (m.group(2) or "")).strip()
    return resolve(VAR_USE_RE.sub(sub, value), root_vars, depth + 1)


def split_top(text: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return [s.strip() for s in out if s.strip()]


def shadow_extent(shadow: str) -> tuple[dict[str, float], float] | None:
    """한 그림자의 바깥 확장(축별)과 blur 를 돌려준다. inset·안쪽이면 None.

    확장 = spread + |offset| (blur 제외 — 모듈 docstring 의 실측 근거)."""
    s = shadow.strip()
    if s.startswith("inset"):
        return None
    bare = HEX_RE.sub(" ", COLORFN_RE.sub(" ", s))
    nums = [px(m.group(0)) for m in LEN_RE.finditer(bare) if px(m.group(0)) is not None]
    if not nums:
        return None
    ox, oy, blur, spread = (list(nums) + [0.0, 0.0, 0.0, 0.0])[:4]
    ext = {"left": spread - ox, "right": spread + ox, "top": spread - oy, "bottom": spread + oy}
    ext = {k: max(v, 0.0) for k, v in ext.items()}
    return ext, blur  # 판정 확장이 0(순수 blur)이어도 blur 고지를 위해 돌려준다


def last_compound(selector: str) -> str:
    """후손·형제 조합자 뒤의 마지막 compound — 링을 실제로 지는 요소다.

    `.checkbox__input:checked + .checkbox__box` 의 링 보유자는 `.checkbox__box` 다."""
    part = re.split(r"[>+~]|\s+", selector.strip())
    return part[-1] if part else selector.strip()


def read_css(web_root: Path) -> list[tuple[str, str, Path]]:
    rules: list[tuple[str, str, Path]] = []
    for path in sorted(web_root.rglob("*.css")):
        try:
            text = CSS_COMMENT_RE.sub("", path.read_text(encoding="utf-8", errors="replace"))
        except OSError as e:
            die(f"CSS 읽기 실패: {path} ({e})")
        for m in RULE_RE.finditer(text):
            rules.append((" ".join(m.group(1).split()), m.group(2), path))
    if not rules:
        die(f"CSS 규칙이 없다: {web_root}")
    return rules


def root_variables(rules: list[tuple[str, str, Path]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for selector, body, _ in rules:
        if ":root" not in selector and selector.strip() != "html":
            continue
        for name, value in VAR_DECL_RE.findall(body):
            out.setdefault(name, value.strip())
    return out


def padding_of(body: str, root_vars: dict[str, str], into: dict[str, float | None]) -> None:
    """규칙 본문의 패딩 선언을 `into` 에 병합한다(캐스케이드 — 나중 선언이 이긴다).

    선언이 없으면 None(=0 이 맞다), 선언은 있는데 해석 불가면 UNKNOWN 이다."""
    for side, raw in PADDING_RE.findall(body):
        value = resolve(raw.strip(), root_vars).replace("!important", "").strip()
        if side:
            key = side[1:]
            got = px(value)
            for s in (LOGICAL.get(key) or (key,)):
                into[s] = UNKNOWN if got is None else got
            continue
        parts = value.split()
        vals = [px(p) for p in parts]
        if not vals or len(vals) > 4:
            continue
        if any(v is None for v in vals):
            for s in SIDES:
                into[s] = UNKNOWN
            continue
        if len(vals) == 1:
            vals = vals * 4
        elif len(vals) == 2:
            vals = [vals[0], vals[1], vals[0], vals[1]]
        elif len(vals) == 3:
            vals = [vals[0], vals[1], vals[2], vals[1]]
        for i, s in enumerate(SIDES):
            into[s] = vals[i]


def members(selector: str) -> list[str]:
    """콤마 목록은 각각이 독립 셀렉터다 — 마지막 하나만 보면 앞 멤버를 통째로 놓친다."""
    return [m.strip() for m in split_top(selector) if m.strip()]


def strip_comments(text: str) -> str:
    """Django 주석을 지우되 줄 수는 유지한다 — 주석 속 리터럴 태그는 요소가 아니다."""
    return DJANGO_COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def template_graph(web_root: Path) -> tuple[dict[Path, str], dict[Path, set[Path]], dict[Path, set[Path]]]:
    """템플릿 본문과 방향 있는 두 그래프 — include(내려감)와 extends 역방향(블록을 채워줌)."""
    texts: dict[Path, str] = {}
    for path in sorted(web_root.rglob("*.html")):
        try:
            texts[path] = strip_comments(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    by_name: dict[str, list[Path]] = {}
    for path in texts:
        by_name.setdefault(path.name, []).append(path)

    def resolve_ref(ref: str) -> list[Path]:
        return [c for c in by_name.get(Path(ref).name, []) if str(c).endswith(ref)] \
            or by_name.get(Path(ref).name, [])

    includes: dict[Path, set[Path]] = {p: set() for p in texts}
    fills: dict[Path, set[Path]] = {p: set() for p in texts}  # 이 파일의 block 을 채우는 자식들
    for path, text in texts.items():
        for ref in INCLUDE_RE.findall(text):
            includes[path].update(resolve_ref(ref))
        for ref in EXTENDS_RE.findall(text):
            for parent in resolve_ref(ref):
                fills[parent].add(path)
    return texts, includes, fills


def element_span(text: str, klass: str) -> str | None:
    """`class="… klass …"` 를 가진 첫 요소의 **자손 범위**(자기 자신 제외)를 돌려준다.

    자기 자신을 빼는 게 중요하다 — 요소의 overflow 는 자기 box-shadow 를 자르지 않는다.
    (`.conversation-composer__textarea{overflow:auto}` 는 자신이 링 보유자지 피해자가 아니다.)"""
    pattern = re.compile(r'class\s*=\s*"[^"]*(?<![\w-])' + re.escape(klass) + r'(?![\w-])[^"]*"')
    m = pattern.search(text)
    if m is None:
        return None
    start = text.rfind("<", 0, m.start())
    if start < 0:
        return None
    tag_m = re.match(r"<([A-Za-z][\w-]*)", text[start:])
    if tag_m is None:
        return None
    tag = tag_m.group(1)
    open_end = text.find(">", m.end())
    if open_end < 0:
        return None
    if text[open_end - 1] == "/" or tag.lower() in ("input", "img", "br", "hr", "meta", "link"):
        return ""  # 빈 요소 — 자손 없음
    depth, i = 1, open_end + 1
    open_re = re.compile(r"<" + tag + r"\b", re.I)
    close_re = re.compile(r"</" + tag + r"\s*>", re.I)
    while i < len(text) and depth > 0:
        o = open_re.search(text, i)
        c = close_re.search(text, i)
        if c is None:
            return text[open_end + 1:]  # 닫는 태그 없음 — 남은 전부(보수적)
        if o is not None and o.start() < c.start():
            depth += 1
            i = o.end()
            continue
        depth -= 1
        if depth == 0:
            return text[open_end + 1:c.start()]
        i = c.end()
    return text[open_end + 1:]


def expand(span: str, owner: Path, texts: dict[Path, str],
           includes: dict[Path, set[Path]], fills: dict[Path, set[Path]],
           depth: int = 0) -> str:
    """자손 범위 + 그 안의 include 본문 + (block 이 있으면) 그 block 을 채우는 자식 템플릿."""
    if depth > 4:
        return span
    parts = [span]
    by_name: dict[str, Path] = {p.name: p for p in texts}
    for ref in INCLUDE_RE.findall(span):
        target = by_name.get(Path(ref).name)
        if target is not None and target in texts:
            parts.append(expand(texts[target], target, texts, includes, fills, depth + 1))
    if BLOCK_RE.search(span):
        for child in sorted(fills.get(owner, ())):
            parts.append(expand(texts[child], child, texts, includes, fills, depth + 1))
    return "\n".join(parts)


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        die("사용: check_clip_clearance.py <web 루트>")
    web_root = Path(argv[0])
    if not web_root.is_dir():
        die(f"web 루트가 디렉터리가 아니다: {web_root}")

    rules = read_css(web_root)
    root_vars = root_variables(rules)

    # ① 링 규칙
    rings: list[tuple[str, dict[str, float], float, Path]] = []
    blurred: list[str] = []
    for selector, body, path in rules:
        if not RING_TRIGGER_RE.search(selector):
            continue
        m = BOX_SHADOW_RE.search(body)
        if not m:
            continue
        best: dict[str, float] | None = None
        worst_blur = 0.0
        for piece in split_top(resolve(m.group(1), root_vars)):
            got = shadow_extent(piece)
            if got is None:
                continue
            ext, blur = got
            worst_blur = max(worst_blur, blur)
            best = ext if best is None else {k: max(best[k], ext[k]) for k in SIDES}
        if best is None:
            continue
        if worst_blur > 0:
            blurred.append(f"{path.name} :: {selector}")
            continue  # blur>0 은 페인트 범위가 연속적이라 결정 판정에서 뺀다(고지만)
        if not any(v > 0 for v in best.values()):
            continue
        for member in members(selector):
            rings.append((member, best, worst_blur, path))

    # 셀렉터별 패딩 캐스케이드 — 패딩이 overflow 와 다른 규칙에 선언될 수 있다(@media 포함).
    pad_by_selector: dict[str, dict[str, float | None]] = {}
    for selector, body, _ in rules:
        for member in members(selector):
            padding_of(body, root_vars, pad_by_selector.setdefault(member, {s: None for s in SIDES}))

    # ② 클리핑 규칙 (축 전파 — 한 축이라도 비-visible 이면 양축)
    clips: list[tuple[str, str, Path, dict[str, float | None]]] = []
    for selector, body, path in rules:
        kinds = {value for _, value in OVERFLOW_RE.findall(body) if value in CLIPPING}
        if not kinds:
            continue
        for member in members(selector):
            clips.append((member, "/".join(sorted(kinds)), path,
                          pad_by_selector.get(member, {s: None for s in SIDES})))

    texts, includes, fills = template_graph(web_root)
    ring_classes = {c for selector, _, _, _ in rings for c in CLASS_RE.findall(last_compound(selector))}
    global_ring = max(
        (ext for selector, ext, _, _ in rings if not CLASS_RE.search(last_compound(selector))),
        key=lambda e: max(e.values()), default=None)

    findings: list[str] = []
    inventory: list[str] = []
    for selector, kinds, path, pad in clips:
        classes = CLASS_RE.findall(last_compound(selector))
        if not classes:
            inventory.append(f"{path.name} :: {selector} — 클래스 없는 셀렉터(조인 불가)")
            continue
        target = classes[0]
        spans = [expand(span, tpl, texts, includes, fills)
                 for tpl, text in sorted(texts.items())
                 if (span := element_span(text, target)) is not None]
        if not spans:
            inventory.append(f"{path.name} :: {selector} — 조인 실패(템플릿에서 «{target}» 을 못 찾음)")
            continue
        blob = "\n".join(spans)
        def present(cls: str) -> bool:
            return re.search(r'class\s*=\s*"[^"]*(?<![\w-])' + re.escape(cls) + r'(?![\w-])',
                             blob) is not None
        applicable = [ext for sel, ext, _, _ in rings
                      if any(present(c) for c in CLASS_RE.findall(last_compound(sel)))]
        if global_ring is not None and FOCUSABLE_RE.search(blob):
            applicable.append(global_ring)
        if not applicable:
            inventory.append(f"{path.name} :: {selector} — 링 보유 요소 없음(자손 범위)")
            continue
        need = {s: max(e[s] for e in applicable) for s in SIDES}
        short, unknown = [], []
        for s in SIDES:
            have = pad.get(s)
            if have is not None and math.isnan(have):
                unknown.append(s)
                continue
            have = 0.0 if have is None else have
            if have < need[s]:
                grade = "확정" if have == 0 else "경미"
                short.append(f"{s} 여유 {have:g}px < 확장 {need[s]:g}px [{grade}]")
        if unknown:
            inventory.append(f"{path.name} :: {selector} — 패딩 미해석({'·'.join(unknown)}) "
                             f"— calc()·미해소 var 는 0 으로 보지 않는다")
            if not short:
                continue
        if short:
            findings.append(f"{path.name} :: {selector} (overflow {kinds}) — " + " · ".join(short))

    print(f"[clip-clearance] 링 규칙 {len(rings)} · 클리핑 규칙 {len(clips)} · "
          f"템플릿 {len(texts)} · 링 클래스 {len(ring_classes)}")
    if blurred:
        print(f"[clip-clearance] blur>0 그림자 {len(blurred)}건은 판정 제외(인벤토리): "
              + " · ".join(sorted(blurred)[:5]) + (" …" if len(blurred) > 5 else ""))
    for line in sorted(inventory):
        print(f"[inventory] {line}")
    for line in sorted(findings):
        print(f"[FINDING] {line}")
    print("[clip-clearance] 조인 한계 — include/extends 만 따라간다(동적 클래스 부착은 못 본다)")
    print(f"[clip-clearance] 발견 {len(findings)}건 · 인벤토리 {len(inventory)}건")
    return 2 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
