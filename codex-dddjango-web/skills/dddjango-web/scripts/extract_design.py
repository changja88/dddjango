#!/usr/bin/env python3
"""extract_design — 동결 디자인 출처를 design-tokens.json으로 결정론 절단 (dddjango-web).

dddart `extract_design.dart`의 이식·간소화다. Flutter 아이콘 축(icon_map·icons[]·
unmappedIcons)은 web에 존재하지 않아 **전체 미이식**이다.

두 입력 모드(둘 다 LLM 추출을 제거하고 architect는 산출물만 소비):
  1) --from-ds-manifest <_ds_manifest.json>: Claude Design manifest의 tokens[]
     {name,value,kind}를 kind 버킷으로 분류한다 — color→colors · font→typography ·
     spacing→spacing · radius→borderRadius · shadow→shadows · other→drop(버림).
     `var(--x)` 자기참조는 같은 tokens[]에서 리터럴로 해소한다(최대 깊이 10·순환은 원본 유지).
  2) 위치 인자 <design-ref 경로>(디렉터리 또는 단일 .html): 참조 HTML 모드 —
     인라인 style·`<style>` 블록·tailwind config 류에서 색(#hex·rgb/rgba·hsl/hsla)·
     font-size·spacing(margin/padding/gap)·border-radius·box-shadow 값을 수집하고
     **빈도 정렬로 토큰 후보화**한다(color-1·font-size-1·space-1·radius-1·shadow-1 …).
     tailwind-config 블록이 파싱되면 그 명명 토큰을 우선 채택하고, 빈도 후보는
     미중복 값만 뒤에 잇는다. Tailwind 임의값 클래스(`p-[13px]` 류)는 arbitraryValues로.

사용:
  python extract_design.py --from-ds-manifest <_ds_manifest.json> --out <design-tokens.json>
  python extract_design.py <design-ref 디렉터리|참조.html> --out <design-tokens.json>

산출 스키마(정렬 2-space JSON — 결정론):
  {colors, typography, spacing, borderRadius, shadows, arbitraryValues}

종료코드: 0=성공 / 1=사용법·소스 부재·파싱 실패·토큰 0(fail-loud — 빈 토큰으로
충실도 게이트가 헛발동하지 않게 한다). 경고는 [warn]으로 stderr에 표면화한다.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from typing import Dict, List, Optional, Tuple

VAR_RE = re.compile(r"var\((--[^)]+)\)")
MAX_VAR_DEPTH = 10

# ---- 공통: 출력(결정론) ----


def write_tokens(
    out_file: str,
    colors: Dict[str, str],
    typography: Dict[str, Dict[str, str]],
    spacing: Dict[str, str],
    border_radius: Dict[str, str],
    shadows: Dict[str, str],
    arbitrary_values: List[str],
) -> None:
    """버킷 6종을 고정 키 순서·2-space 들여쓰기로 기록한다(타임스탬프 없음 — 결정론)."""
    out: Dict[str, object] = {
        "colors": colors,
        "typography": typography,
        "spacing": spacing,
        "borderRadius": border_radius,
        "shadows": shadows,
        "arbitraryValues": arbitrary_values,
    }
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")


def sorted_map(m: Dict[str, str]) -> Dict[str, str]:
    return {k: m[k] for k in sorted(m)}


def sorted_nested(m: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    return {k: {ik: m[k][ik] for ik in sorted(m[k])} for k in sorted(m)}


def warn(msg: str) -> None:
    print(f"[warn] {msg}", file=sys.stderr)


def die(msg: str) -> None:
    print(f"[extract-design] {msg}", file=sys.stderr)
    sys.exit(1)


# ---- 모드 1: --from-ds-manifest (Claude Design _ds_manifest.json) ----


def run_ds_manifest_mode(manifest_file: str, out_file: str) -> None:
    if not os.path.isfile(manifest_file):
        die(f"ds-manifest 파일 없음: {manifest_file}")
    try:
        with open(manifest_file, encoding="utf-8") as f:
            doc = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        die(f"ds-manifest JSON 파싱 실패: {e} — 동결본을 확인하라.")

    tokens_list = doc.get("tokens") if isinstance(doc, dict) else None
    if not isinstance(tokens_list, list):
        die("ds-manifest: tokens 배열 없음 또는 형태 오류.")

    # 1단계: name→value 원시 맵 — var(--x) 해소용 사전(리터럴 값 먼저 등록).
    raw_values: Dict[str, str] = {}
    for t in tokens_list:
        if not isinstance(t, dict):
            continue
        name, value = t.get("name"), t.get("value")
        if isinstance(name, str) and isinstance(value, str):
            raw_values[name] = value

    def resolve(value: str) -> str:
        """var(--x) 자기참조 해소 — 순환·미해소는 원본 그대로 유지(최대 깊이 10)."""
        v = value
        depth = 0
        while VAR_RE.search(v) and depth < MAX_VAR_DEPTH:
            v = VAR_RE.sub(lambda m: raw_values.get(m.group(1), m.group(0)), v)
            depth += 1
        return v

    # 2단계: kind 버킷 분류(kind='other'는 명시적 무수집).
    colors: Dict[str, str] = {}
    typography: Dict[str, Dict[str, str]] = {}
    spacing: Dict[str, str] = {}
    border_radius: Dict[str, str] = {}
    shadows: Dict[str, str] = {}

    for t in tokens_list:
        if not isinstance(t, dict):
            continue
        name, value, kind = t.get("name"), t.get("value"), t.get("kind")
        if not (isinstance(name, str) and isinstance(value, str) and isinstance(kind, str)):
            continue
        resolved = resolve(value)
        if kind == "color":
            colors[name] = resolved
        elif kind == "font":
            typography[name] = {"size": resolved}
        elif kind == "spacing":
            spacing[name] = resolved
        elif kind == "radius":
            border_radius[name] = resolved
        elif kind == "shadow":
            shadows[name] = resolved
        # 'other' → 수집하지 않음

    # fail-loud: 핵심 토큰군이 모두 비면 manifest가 비정상.
    if not colors and not typography and not spacing:
        die("ds-manifest tokens[]에서 색·타이포·간격 토큰 0 — manifest가 비었거나 형태가 다르다.")

    write_tokens(out_file, sorted_map(colors), sorted_nested(typography),
                 sorted_map(spacing), sorted_map(border_radius), sorted_map(shadows), [])
    print(f"[extract-design] dsManifest → 색 {len(colors)} · 간격 {len(spacing)} · "
          f"모서리 {len(border_radius)} · 그림자 {len(shadows)} · 타이포 {len(typography)} → {out_file}")
    sys.exit(0)


# ---- 모드 2: 참조 HTML — tailwind-config 파서(dart _jsToJson/_balanced 이식) ----


def balanced(s: str, brace_start: int) -> Optional[str]:
    """brace_start의 `{`부터 짝 맞는 `}`까지 부분 문자열(따옴표 안 중괄호는 무시)."""
    depth = 0
    quote: Optional[str] = None
    i = brace_start
    while i < len(s):
        c = s[i]
        if quote is not None:
            if c == "\\":
                i += 1  # 이스케이프 다음 문자 건너뜀
            elif c == quote:
                quote = None
        elif c in ('"', "'"):
            quote = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[brace_start:i + 1]
        i += 1
    return None


_UNQUOTED_KEY_RE = re.compile(r"([{,]\s*)([A-Za-z_$][A-Za-z0-9_$]*)\s*:")
_TRAILING_COMMA_RE = re.compile(r",(\s*[}\]])")


def js_to_json(src: str) -> str:
    """JS 객체 리터럴 → JSON. 문자열 리터럴 안은 보존하고 그 밖에서만 무인용 키 인용 +
    trailing comma 제거(따옴표·이스케이프 추적). 단일따옴표 문자열은 보존돼 json.loads가 fail-loud."""
    out: List[str] = []
    seg: List[str] = []

    def flush_seg() -> None:
        if not seg:
            return
        text = "".join(seg)
        text = _UNQUOTED_KEY_RE.sub(lambda m: f'{m.group(1)}"{m.group(2)}":', text)
        text = _TRAILING_COMMA_RE.sub(lambda m: m.group(1), text)
        out.append(text)
        seg.clear()

    quote: Optional[str] = None
    i = 0
    while i < len(src):
        c = src[i]
        if quote is not None:
            out.append(c)
            if c == "\\" and i + 1 < len(src):
                out.append(src[i + 1])
                i += 1
            elif c == quote:
                quote = None
        elif c in ('"', "'"):
            flush_seg()
            quote = c
            out.append(c)
        else:
            seg.append(c)
        i += 1
    flush_seg()
    return "".join(out)


def parse_tw_config(block: str) -> Optional[Dict[str, object]]:
    """`tailwind.config = { ... }` 객체 리터럴을 JS→JSON 정규화 후 디코드."""
    eq = block.find("=")
    brace_start = block.find("{", 0 if eq < 0 else eq)
    if brace_start < 0:
        return None
    obj_text = balanced(block, brace_start)
    if obj_text is None:
        return None
    try:
        decoded = json.loads(js_to_json(obj_text))
    except json.JSONDecodeError:
        return None
    return decoded if isinstance(decoded, dict) else None


def tw_extend(config: Dict[str, object]) -> Dict[str, object]:
    theme = config.get("theme")
    if isinstance(theme, dict):
        extend = theme.get("extend")
        if isinstance(extend, dict):
            return extend
        return theme
    return config


def flatten_str_map(src: object, prefix: str = "") -> Dict[str, str]:
    """tailwind 중첩 맵({primary:{50:"#..."}} 류)을 `이름-하위키`로 평탄화(문자열 값만)."""
    out: Dict[str, str] = {}
    if not isinstance(src, dict):
        return out
    for k, v in src.items():
        name = f"{prefix}-{k}" if prefix else str(k)
        if isinstance(v, str):
            out[name] = v
        elif isinstance(v, dict):
            out.update(flatten_str_map(v, name))
    return out


def merge_first_wins(into: Dict[str, str], src: Dict[str, str], screen: str, bucket: str) -> None:
    for name, v in src.items():
        prev = into.get(name)
        if prev is not None and prev != v:
            warn(f"{screen}: {bucket}.{name} 값 불일치({prev} → {v}) — 화면 간 디자인시스템 차이, 첫 값 유지")
            continue
        into[name] = v


def merge_typography(into: Dict[str, Dict[str, str]], font_family: object, font_size: object) -> None:
    """tailwind extend의 fontFamily/fontSize를 typography 버킷 모양으로(dart _mergeTypography 이식)."""
    if isinstance(font_family, dict):
        for k, v in font_family.items():
            fam = v[0] if isinstance(v, list) and v else (v if isinstance(v, str) else None)
            if fam is not None:
                into.setdefault(str(k), {})["family"] = str(fam)
    if isinstance(font_size, dict):
        for k, v in font_size.items():
            m = into.setdefault(str(k), {})
            if isinstance(v, list) and v:
                m["size"] = str(v[0])
                if len(v) > 1 and isinstance(v[1], dict):
                    for attr in ("lineHeight", "fontWeight", "letterSpacing"):
                        if v[1].get(attr) is not None:
                            m[attr] = str(v[1][attr])
            elif isinstance(v, str):
                m["size"] = v


# ---- 모드 2: 참조 HTML — 스타일 값 수집(빈도 후보) ----

STYLE_ATTR_RE = re.compile(r"""style\s*=\s*("([^"]*)"|'([^']*)')""", re.IGNORECASE)
STYLE_BLOCK_RE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
SCRIPT_BLOCK_RE = re.compile(r"<script\b[^>]*>(.*?)</script>", re.IGNORECASE | re.DOTALL)
TW_CONFIG_MARKER_RE = re.compile(r'id\s*=\s*["\']tailwind-config["\']', re.IGNORECASE)

COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]+\)|hsla?\([^)]+\)")
DECL_RE = re.compile(r"([-a-zA-Z]+)\s*:\s*([^;{}]+)")
LENGTH_RE = re.compile(r"-?\d*\.?\d+(?:px|rem|em|vh|vw|%)\b")
CLASS_ATTR_RE = re.compile(r"""class\s*=\s*("([^"]*)"|'([^']*)')""", re.IGNORECASE)
ARBITRARY_RE = re.compile(r"^[a-zA-Z][\w-]*-\[[^\]]+\]$")
WS_RE = re.compile(r"\s+")

SPACING_PROPS = frozenset({
    "margin", "margin-top", "margin-right", "margin-bottom", "margin-left",
    "padding", "padding-top", "padding-right", "padding-bottom", "padding-left",
    "gap", "row-gap", "column-gap",
})
SHADOW_PROPS = frozenset({"box-shadow", "text-shadow"})


def norm_value(v: str) -> str:
    return WS_RE.sub(" ", v).strip()


def collect_style_values(
    style_texts: List[str],
    color_freq: "Counter[str]",
    font_size_freq: "Counter[str]",
    spacing_freq: "Counter[str]",
    radius_freq: "Counter[str]",
    shadow_freq: "Counter[str]",
) -> None:
    """style 텍스트(인라인·<style> 블록)에서 색·font-size·spacing·radius·shadow 값을 빈도 수집."""
    for text in style_texts:
        for m in COLOR_RE.finditer(text):
            color_freq[norm_value(m.group(0)).lower()] += 1
        for m in DECL_RE.finditer(text):
            prop = m.group(1).lower()
            value = norm_value(m.group(2))
            if not value:
                continue
            if prop == "font-size":
                font_size_freq[value] += 1
            elif prop in SPACING_PROPS:
                for lm in LENGTH_RE.finditer(value):
                    spacing_freq[lm.group(0)] += 1
            elif prop.startswith("border") and prop.endswith("radius"):
                radius_freq[value] += 1
            elif prop in SHADOW_PROPS:
                shadow_freq[value.lower()] += 1


def rank_candidates(freq: "Counter[str]", prefix: str, taken_values: set) -> Dict[str, str]:
    """빈도 내림차순(동률은 값 사전순 — 결정론)으로 `<prefix>-N` 후보 명명. 기존 값과 중복은 제외."""
    out: Dict[str, str] = {}
    n = 0
    for value, _count in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0])):
        if value in taken_values:
            continue
        n += 1
        out[f"{prefix}-{n}"] = value
    return out


def collect_arbitrary_classes(html: str, into: set) -> None:
    """Tailwind 임의값 클래스(`p-[13px]` 류) 수집 — hover:/md: 변형 접두는 제거."""
    for m in CLASS_ATTR_RE.finditer(html):
        cls = m.group(2) if m.group(2) is not None else (m.group(3) or "")
        for tok in cls.split():
            bare = tok.rsplit(":", 1)[-1]
            if ARBITRARY_RE.match(bare):
                into.add(bare)


def run_html_mode(ref_path: str, out_file: str) -> None:
    if os.path.isdir(ref_path):
        html_files = sorted(
            os.path.join(ref_path, name)
            for name in os.listdir(ref_path)
            if name.lower().endswith((".html", ".htm"))
            and os.path.isfile(os.path.join(ref_path, name))
        )
        if not html_files:
            die(f"동결 HTML 없음: {ref_path}/*.html — 참조 HTML 동결이 누락됐다(Phase 0 위반).")
    elif os.path.isfile(ref_path):
        html_files = [ref_path]
    else:
        die(f"design-ref 경로 없음: {ref_path}")

    # 명명 토큰(tailwind-config 파싱분·first-wins) + 빈도 후보(인라인 style·<style> 블록).
    named_colors: Dict[str, str] = {}
    named_spacing: Dict[str, str] = {}
    named_radius: Dict[str, str] = {}
    named_shadows: Dict[str, str] = {}
    typography: Dict[str, Dict[str, str]] = {}
    color_freq: "Counter[str]" = Counter()
    font_size_freq: "Counter[str]" = Counter()
    spacing_freq: "Counter[str]" = Counter()
    radius_freq: "Counter[str]" = Counter()
    shadow_freq: "Counter[str]" = Counter()
    arbitrary: set = set()

    for path in html_files:
        name = os.path.basename(path)
        with open(path, encoding="utf-8", errors="replace") as f:
            html = f.read()

        style_texts: List[str] = [
            m.group(2) if m.group(2) is not None else (m.group(3) or "")
            for m in STYLE_ATTR_RE.finditer(html)
        ]
        style_texts.extend(m.group(1) for m in STYLE_BLOCK_RE.finditer(html))

        # tailwind config 류: id="tailwind-config" 또는 `tailwind.config` 포함 스크립트.
        for m in SCRIPT_BLOCK_RE.finditer(html):
            open_tag_end = html.index(">", m.start())
            open_tag = html[m.start():open_tag_end]
            body = m.group(1)
            if not (TW_CONFIG_MARKER_RE.search(open_tag) or "tailwind.config" in body):
                continue
            config = parse_tw_config(body)
            if config is None:
                # 파싱 실패는 조용히 버리지 않는다 — 값 수집 풀로 강등하고 표면화.
                warn(f"{name}: tailwind-config 파싱 실패 — 명명 토큰 없이 값 빈도 수집으로 강등")
                style_texts.append(body)
                continue
            extend = tw_extend(config)
            merge_first_wins(named_colors, flatten_str_map(extend.get("colors")), name, "colors")
            merge_first_wins(named_spacing, flatten_str_map(extend.get("spacing")), name, "spacing")
            merge_first_wins(named_radius, flatten_str_map(extend.get("borderRadius")), name, "borderRadius")
            merge_first_wins(named_shadows, flatten_str_map(extend.get("boxShadow")), name, "shadows")
            merge_typography(typography, extend.get("fontFamily"), extend.get("fontSize"))

        collect_style_values(style_texts, color_freq, font_size_freq,
                             spacing_freq, radius_freq, shadow_freq)
        collect_arbitrary_classes(html, arbitrary)

    # 버킷 합성: 명명 토큰(이름 정렬) 먼저, 빈도 후보(순위 순·미중복 값)를 뒤에.
    def compose(named: Dict[str, str], freq: "Counter[str]", prefix: str) -> Dict[str, str]:
        out = sorted_map(named)
        taken = {v.lower() for v in named.values()}
        out.update(rank_candidates(freq, prefix, taken))
        return out

    colors = compose(named_colors, color_freq, "color")
    spacing = compose(named_spacing, spacing_freq, "space")
    border_radius = compose(named_radius, radius_freq, "radius")
    shadows = compose(named_shadows, shadow_freq, "shadow")

    typo_out = sorted_nested(typography)
    taken_sizes = {m.get("size", "").lower() for m in typography.values()}
    for tname, size in rank_candidates(font_size_freq, "font-size", taken_sizes).items():
        typo_out[tname] = {"size": size}

    # fail-loud: 핵심 토큰군이 모두 비면 시안 색·간격·타이포를 기계 추출하지 못한 것 — exit 1
    # (빈 토큰으로 충실도 게이트가 헛발동하지 않게 한다).
    if not colors and not typo_out and not spacing:
        die("참조 HTML에서 색·타이포·간격 토큰 0 — 인라인 style·<style>·tailwind config가 없거나 비었다. "
            "기계 추출 불가(토큰 없이 진행·충실도는 인간 오라클 보조).")

    write_tokens(out_file, colors, typo_out, spacing, border_radius, shadows, sorted(arbitrary))
    print(f"[extract-design] 참조 HTML {len(html_files)} → 색 {len(colors)} · 간격 {len(spacing)} · "
          f"모서리 {len(border_radius)} · 그림자 {len(shadows)} · 타이포 {len(typo_out)} · "
          f"임의값 {len(arbitrary)} → {out_file}")
    sys.exit(0)


# ---- 진입점 ----


def parse_args(argv: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    ref_path: Optional[str] = None
    out_file: Optional[str] = None
    manifest_file: Optional[str] = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--out":
            i += 1
            out_file = argv[i] if i < len(argv) else None
        elif arg == "--from-ds-manifest":
            i += 1
            manifest_file = argv[i] if i < len(argv) else None
        else:
            ref_path = arg
        i += 1
    return ref_path, out_file, manifest_file


def main(argv: List[str]) -> None:
    ref_path, out_file, manifest_file = parse_args(argv)
    if out_file is None or (ref_path is None and manifest_file is None):
        print("사용(dsManifest): python extract_design.py --from-ds-manifest <_ds_manifest.json> --out <design-tokens.json>",
              file=sys.stderr)
        print("사용(참조 HTML): python extract_design.py <design-ref 디렉터리|참조.html> --out <design-tokens.json>",
              file=sys.stderr)
        sys.exit(1)
    if manifest_file is not None:
        run_ds_manifest_mode(manifest_file, out_file)
    else:
        assert ref_path is not None
        run_html_mode(ref_path, out_file)


if __name__ == "__main__":
    main(sys.argv[1:])
