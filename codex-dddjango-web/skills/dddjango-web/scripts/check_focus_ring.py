#!/usr/bin/env python3
r"""check_focus_ring — 포커스 링 중첩 정적 검사 (dddjango-web).

전역 포커스 링(`:focus-visible { box-shadow: … }`)을 둔 프로젝트에서 부품이 래퍼에
`:focus-within` 링을 또 얹으면 **링이 두 겹으로 그려진다**. 안쪽 요소가 `border-radius` 를
갖지 않으면 그 겹은 **직각**이라 둥근 바깥 링 안에 각진 테두리가 비친다 — A8 관계인 편집기에서
실제로 났다(`.select-field__control:focus-within` 둥근 링 + native `<select>` 가 받는 전역
직각 링. Chrome 실측: 마우스 클릭만으로 `<select>` 가 `:focus-visible` 을 매치한다).

시안 대조로는 안 잡힌다 — `render_audit.js` 는 `:focus` **셀렉터 이름만** 모으고
`compare_render_audit.py` 는 그것을 문자열 목록으로만 비교한다. 이름이 같으면 통과한다.

**브라우저를 쓰지 않는다.** CSS 와 템플릿 텍스트만 읽는다. CSS 파서·템플릿 조인은
`check_clip_clearance` 를 import 해 쓴다(중복 구현 금지). 셀렉터 분류만 자체 보유한다 —
`last_compound` 는 `re.split(r"[>+~]|\s+")` 라 **괄호를 모르고**,
`:where(a, button, input):focus-visible` 이 `input)` 으로 잘린다(실측).

정본: workspace/design/2026-09-15-web-gate-hardwall.md §5 ·
규칙 선검증: workspace/eval/web-gate-hardwall/ring-overlap-prevalidation.md

사용:
  python check_focus_ring.py <web 루트>

7단계:
  ① 셀렉터 분류(괄호 인식) — global(타입·클래스·ID 없음) / types(`:is`·`:where` 타입 나열 포함) /
     narrow(클래스로 좁힘). `:not()` 인자의 클래스는 **면제**로 수확하고, 조상 스코프가 붙은
     전역 규칙은 «스코프 있음» 을 발견 줄에 적는다(범위 밖 요소는 그 링을 못 받는다).
  ② 래퍼 링 — `:focus-within` 이면서 바깥 box-shadow 를 얹는 규칙의 대상 클래스 K
     (K 는 **마지막 compound 의 클래스**다 — 조상 스코프의 클래스가 아니다).
  ③ 면제 — ⓐ `:focus*` 규칙의 `box-shadow: none` ⓑ sr-only 은닉(clip·clip-path·opacity:0·1px×1px)
     ⓒ `:not()` 예외. 은닉 요소는 링을 그릴 수 없으므로 이중이 아니다.
  ④ 명시 선언 — 자손이 자기 `:focus` 그림자를 **선언**했으면 전역 링을 «추가» 가 아니라
     «교체» 한다. 발견이 아니라 **인벤토리**로 낸다(누락이 아니라 결정이다).
  ⑤ 조인 — K 를 선언한 템플릿과 include/extends 로 이어진 텍스트에서 포커스 가능 요소를 찾는다.
     타입 링만 있으면 그 태그의 요소만 대상이다.
  ⑥ 중복 제거 — (K, 템플릿) 한 자리. **면제 판정 뒤에** 한다 — 앞에 두면 억제된 요소가
     자리를 차지해 진짜 발견이 통째로 사라진다(원형에서 실제로 밟았다).
  ⑦ radius 비교 — 안쪽이 0 이면 «직각 링», 다르면 «모서리 불일치». 발견 줄 부속 정보다.

**전역·타입 링이 0건이면 exit 0 이되 «판정을 수행하지 않았다» 를 명시 출력한다** —
무증상 통과는 미탐 통로다(발견 0 과 판정 안 함은 다르다).

판정 한계(출력에 항상 고지):
  · 타입 한정 전역 규칙(`a:focus-visible` 같은)은 전역으로 보지 않는다.
  · `@media` 블록은 평탄화돼 조건부 규칙이 무조건 규칙으로 보인다.
  · 조인은 include/extends 만 따라가고 템플릿당 첫 일치만 본다.
  · 특이도·선언 순서를 보지 않는다.

지위는 check_clip_clearance 와 동급 — **판단 자료(비차단)·배너 1급 의무 표기**.
exit: 0=발견 0(판정 수행 여부는 출력이 말한다) / 1=사용법 오류(미실행 취급) / 2=발견 ≥1
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_clip_clearance as clip  # noqa: E402

RADIUS_RE = re.compile(r"(?<![-\w])border-radius\s*:\s*([^;]+)")
SHADOW_DECL_RE = re.compile(r"(?<![-\w])box-shadow\s*:\s*([^;]+)")
HIDDEN_RE = (re.compile(r"(?<![-\w])clip\s*:\s*rect\(\s*0"),
             re.compile(r"(?<![-\w])clip-path\s*:"),
             re.compile(r"(?<![-\w])opacity\s*:\s*0(?![.\d])"))
WIDTH_1_RE = re.compile(r"(?<![-\w])width\s*:\s*1px")
HEIGHT_1_RE = re.compile(r"(?<![-\w])height\s*:\s*1px")
GROUP_RE = re.compile(r":(?:is|where|matches|any)\(([^()]*(?:\([^()]*\)[^()]*)*)\)")
NOT_RE = re.compile(r":not\(([^()]*(?:\([^()]*\)[^()]*)*)\)")
PSEUDO_RE = re.compile(r"::?[a-zA-Z-]+(?:\([^()]*(?:\([^()]*\)[^()]*)*\))?")
TYPE_RE = re.compile(r"^[A-Za-z][\w-]*$")
TAG_RE = re.compile(r"<([a-zA-Z]+)")
CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')


def fail(message: str) -> int:
    print(f"[focus-ring] {message}", file=sys.stderr)
    return 1


def split_compounds(member: str) -> list[str]:
    """괄호 깊이를 지키며 후손·자식·형제 결합자로 자른다."""
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    for char in member:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if depth == 0 and (char.isspace() or char in ">+~"):
            if current:
                parts.append("".join(current))
                current = []
            continue
        current.append(char)
    if current:
        parts.append("".join(current))
    return parts


def classify(member: str) -> tuple[str, set[str] | None, set[str], bool]:
    """(kind, 태그 집합, :not 면제 클래스, 조상 스코프 유무)."""
    compounds = split_compounds(member)
    if not compounds:
        return "narrow", None, set(), False
    subject, scoped = compounds[-1], len(compounds) > 1
    excluded = {name for m in NOT_RE.finditer(subject)
                for name in re.findall(r"\.([A-Za-z_][\w-]*)", m.group(1))}
    body = NOT_RE.sub("", subject)
    grouped = [part.strip() for m in GROUP_RE.finditer(body)
               for part in m.group(1).split(",") if part.strip()]
    rest = PSEUDO_RE.sub("", GROUP_RE.sub("", body)).strip()
    atoms = ([rest] if rest else []) + grouped
    if not atoms or all(atom == "*" for atom in atoms):
        return "global", None, excluded, scoped
    bare = [stripped for stripped in (PSEUDO_RE.sub("", atom).strip() for atom in atoms) if stripped]
    if bare and all(TYPE_RE.match(name) for name in bare):
        return "types", {name.lower() for name in bare}, excluded, scoped
    return "narrow", None, excluded, scoped


def hidden(body: str) -> bool:
    """sr-only 판형 — 링이 보일 수 없는 요소다."""
    return (any(pattern.search(body) for pattern in HIDDEN_RE)
            or bool(WIDTH_1_RE.search(body) and HEIGHT_1_RE.search(body)))


def outer_shadow(body: str, root_vars: dict[str, str]) -> bool:
    match = SHADOW_DECL_RE.search(body)
    if not match:
        return False
    return any(clip.shadow_extent(part)
               for part in clip.split_top(clip.resolve(match.group(1), root_vars))
               if "inset" not in part)


def read_rules(web_root: Path) -> list[tuple[str, str, Path]]:
    """CSS 를 읽되 규칙 0건에도 죽지 않는다 — «판정 안 함» 은 «미실행» 이 아니다."""
    rules: list[tuple[str, str, Path]] = []
    for path in sorted(web_root.rglob("*.css")):
        try:
            text = clip.CSS_COMMENT_RE.sub("", path.read_text(encoding="utf-8", errors="replace"))
        except OSError as error:
            print(f"[focus-ring] CSS 읽기 실패(건너뜀): {path} ({error})")
            continue
        for match in clip.RULE_RE.finditer(text):
            rules.append((" ".join(match.group(1).split()), match.group(2), path))
    return rules


def element_classes(tag: str) -> set[str]:
    """Django 템플릿 문법이 섞인 class 속성에서 리터럴 클래스만 건진다."""
    names: set[str] = set()
    for value in CLASS_ATTR_RE.findall(tag):
        names |= {word for word in value.split() if "{" not in word and "}" not in word}
    return names


def whole_tag(text: str, end: int) -> str:
    """여는 태그 전체를 잘라온다 — `{% … %}` 안의 `>` 에 속지 않는다."""
    start = text.rfind("<", 0, end)
    if start < 0:
        return ""
    stop = text.find(">", start)
    while stop != -1 and text.count("{%", start, stop) != text.count("%}", start, stop):
        stop = text.find(">", stop + 1)
    return text[start:stop + 1] if stop != -1 else text[start:start + 160]


def harvest(rules, root_vars):
    """규칙을 한 번 훑어 링·면제·radius 를 모은다."""
    globals_, types_, wrappers = [], [], []
    exempt, declared, radius = set(), set(), {}
    for selector, body, path in rules:
        radius_match = RADIUS_RE.search(body)
        if radius_match:
            value = clip.resolve(radius_match.group(1), root_vars).strip()
            for member in clip.members(selector):
                for name in clip.CLASS_RE.findall(clip.last_compound(member)):
                    radius.setdefault(name, value)
        if hidden(body):
            for member in clip.members(selector):
                exempt |= set(clip.CLASS_RE.findall(clip.last_compound(member)))
        shadow_match = SHADOW_DECL_RE.search(body)
        if shadow_match and ":focus" in selector:
            value = clip.resolve(shadow_match.group(1), root_vars).strip()
            target = exempt if value == "none" else declared
            for member in clip.members(selector):
                target |= set(clip.CLASS_RE.findall(member))
        if not (clip.RING_TRIGGER_RE.search(selector) and outer_shadow(body, root_vars)):
            continue
        for member in clip.members(selector):
            if not clip.RING_TRIGGER_RE.search(member):
                continue
            kind, tags, excluded, scoped = classify(member)
            exempt |= excluded
            if kind == "global":
                globals_.append((path.name, member, scoped))
            elif kind == "types":
                types_.append((path.name, member, tags, scoped))
            elif ":focus-within" in member:
                for name in clip.CLASS_RE.findall(clip.last_compound(member)):
                    wrappers.append((path.name, member, name))
    return globals_, types_, wrappers, exempt, declared, radius


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        return fail("사용: check_focus_ring.py <web 루트>")
    web_root = Path(argv[0]).resolve()
    if not web_root.is_dir():
        return fail(f"web 루트가 디렉터리가 아니다: {web_root}")
    rules = read_rules(web_root)
    root_vars = clip.root_variables(rules)
    globals_, types_, wrappers, exempt, declared, radius = harvest(rules, root_vars)
    wrapper_names = {name for _, _, name in wrappers}
    print(f"[focus-ring] 전역 링 {len(globals_)} · 타입 링 {len(types_)} · 래퍼 링 {len(wrapper_names)} "
          f"· 면제 {len(exempt)} · 자기 선언 {len(declared - exempt)}")
    for name, member, scoped in globals_:
        scope_note = " (조상 스코프 있음 — 범위 밖 요소는 이 링을 받지 않는다)" if scoped else ""
        print(f"[inventory] 전역 링 {name} :: {member}{scope_note}")
    for name, member, tags, _scoped in types_:
        print(f"[inventory] 타입 링 {name} :: {member} → {', '.join(sorted(tags))}")
    if not globals_ and not types_:
        print("[focus-ring] 전역·타입 링 규칙이 없다 — 이 프로젝트에서는 이중 링 판정을 수행하지 않았다"
              "(발견 0 이 아니라 판정 안 함이다)")
        return 0
    texts, includes, extends = clip.template_graph(web_root)
    typed = set().union(*(tags for _, _, tags, _ in types_)) if types_ else set()
    findings: list[tuple[tuple[str, str], str]] = []
    notes: list[str] = []
    seen: dict[tuple[str, str], int] = {}
    for css_name, _member, name in sorted(set(wrappers), key=lambda row: (row[2], row[0])):
        for template, text in sorted(texts.items()):
            span = clip.element_span(text, name)
            if span is None:
                continue
            blob = clip.expand(span, template, texts, includes, extends)
            for match in clip.FOCUSABLE_RE.finditer(blob):
                tag = whole_tag(blob, match.end())
                tag_name = TAG_RE.match(tag).group(1).lower() if TAG_RE.match(tag) else ""
                if not globals_ and tag_name not in typed:
                    continue
                classes = element_classes(tag)
                if classes & exempt:
                    continue
                if classes & declared:
                    notes.append(f"[inventory] .{name} 안 <{tag_name}> ({', '.join(sorted(classes & declared))})"
                                 " — 자기 :focus 그림자를 선언했다(교체이지 누락이 아니다 · 이중 여부는 육안)")
                    continue
                key = (name, template.name)
                if key in seen:
                    seen[key] += 1
                    continue
                seen[key] = 1
                outer = radius.get(name, "0")
                inner = next((radius[c] for c in sorted(classes) if c in radius),
                             "0" if classes else None)
                note = ""
                if inner is None:
                    note = " · 안쪽 radius 미상(리터럴 클래스 없음 — 모서리는 육안)"
                elif inner != outer:
                    shape = "직각 링" if inner in ("0", "0px") else "모서리 불일치"
                    note = f" · 안쪽 radius {inner} vs 바깥 {outer} — {shape}"
                shown = f'<{tag_name} class="{" ".join(sorted(classes))}">' if classes else f"<{tag_name}>"
                findings.append((key, f"[FINDING] {css_name} :: .{name} 안의 면제 없는 포커스 대상"
                                      f"{{extra}} — {template.name} {shown}{note}"))
    for note in dict.fromkeys(notes):
        print(note)
    for key, line in findings:
        more = seen.get(key, 1) - 1
        print(line.format(extra=f" 외 {more}건" if more else ""))
    print("[focus-ring] 판정 한계 — 타입 한정 전역 규칙·@media 조건·특이도/선언 순서는 보지 않고, "
          "조인은 include/extends 만 따라가며 템플릿당 첫 일치만 본다")
    print(f"[focus-ring] 발견 {len(findings)}건 · 인벤토리 {len(globals_) + len(types_) + len(set(notes))}건")
    return 2 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
