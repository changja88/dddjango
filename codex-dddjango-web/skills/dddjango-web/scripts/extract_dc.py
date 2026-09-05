#!/usr/bin/env python3
"""Extract one explicit Claude Design screen and its static image dependencies.

Supports legacy `.screen` and `data-screen-label` on arbitrary HTML elements.
Multiple candidates require --screen-label <exact label> or --screen-index <0-based>;
a single candidate is automatic. Nested device decoration is never a screen.

Usage: extract_dc.py <screen.dc.html> --tokens <design-tokens.json>
       --asset-manifest <asset-manifest.json> --assets-root <project root>
       --asset-base <design-ref> --meta <screen-meta.json>
       [--screen-label <label> | --screen-index <index>] [--source-manifest <path>]

--tokens verifies the upstream extraction exists; it does not mutate tokens.
Meta contains source text fields, selected screen_label, source_sha256, and
explicit_frames (only root/direct-child fixed px sizes; no inferred viewport or
chrome classification). Source rendering is still required to confirm boundaries.
Image output adds source_ready, unresolved dependencies and per-image digest/size/
reason. Status ok/inline means validated bytes landed in web/static/images, not
that a browser rendered them. Existing source-manifest URL mappings are reused.
Exit 1: input/selection failure; exit 0: extraction ran, even with failed images.
The caller must inspect source_ready and resolve failures before a design gate.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from typing import Dict, List, Optional

IMAGES_SUBDIR = os.path.join("web", "static", "images")

WORD_RE = re.compile(r"[A-Za-z0-9]")
WS_RE = re.compile(r"\s")
WS_COLLAPSE_RE = re.compile(r"\s+")
ATTR_RE = re.compile(r"""([\w:-]+)\s*=\s*("([^"]*)"|'([^']*)'|(\S+))""")


def warn(msg: str) -> None:
    print(f"[warn] {msg}", file=sys.stderr)


def die(msg: str) -> None:
    print(f"[extract-dc] {msg}", file=sys.stderr)
    sys.exit(1)


# ---- HTML 토크나이저(dart `_tagEnd`·`_parseAttrs` 동형 이식) ----


def tag_end(s: str, lt: int) -> int:
    """`<` 위치(lt)부터 짝 맞는 `>`까지 — 따옴표 안 `>`는 무시(attr 값 안전)."""
    quote: Optional[str] = None
    for i in range(lt + 1, len(s)):
        c = s[i]
        if quote is not None:
            if c == quote:
                quote = None
        elif c in ('"', "'"):
            quote = c
        elif c == ">":
            return i
    return -1


def parse_attrs(s: str) -> Dict[str, str]:
    """속성 파서 — 쌍·단·무따옴표 3종."""
    attrs: Dict[str, str] = {}
    for m in ATTR_RE.finditer(s):
        attrs[m.group(1).lower()] = m.group(3) or m.group(4) or m.group(5) or ""
    return attrs


def word_char_at(s: str, pos: int) -> bool:
    return pos < len(s) and bool(WORD_RE.match(s[pos]))


def has_class(cls: str, token: str) -> bool:
    """class 속성에 주어진 토큰이 공백 구분 단어로 들어있는가(`fullscreen` 부분일치 아님)."""
    return token in cls.split()


# ---- Explicitly identify a screen; source frames are evidence, never inferred chrome. ----
from html.parser import HTMLParser


class ScreenParser(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.lines = [0]
        for match in re.finditer("\n", source):
            self.lines.append(match.end())
        self.stack = []
        self.screens = []
        self.frames = []

    def source_position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        style = attributes.get("style") or ""
        width = re.search(r"(?:^|;)\s*width\s*:\s*(\d+(?:\.\d+)?)px\s*(?:;|$)", style)
        height = re.search(r"(?:^|;)\s*height\s*:\s*(\d+(?:\.\d+)?)px\s*(?:;|$)", style)
        if width and height and len(self.stack) <= 1:
            self.frames.append({"width_px": float(width[1]), "height_px": float(height[1])})
        candidate = "data-screen-label" in attributes or has_class(attributes.get("class") or "", "screen")
        record = {"tag": tag, "start": self.source_position(), "label": attributes.get("data-screen-label"), "end": None} if candidate else None
        if record:
            self.screens.append(record)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append((tag, record))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                for _, record in self.stack[index:]:
                    if record and record["tag"] == tag:
                        record["end"] = self.source.find(">", self.source_position()) + 1
                del self.stack[index:]
                break


def select_screen(html: str, label: Optional[str] = None, index: Optional[int] = None):
    parser = ScreenParser(html)
    parser.feed(html)
    candidates = [row for row in parser.screens if row["label"] is not None] or parser.screens
    if label is not None:
        candidates = [row for row in candidates if row["label"] == label]
    if index is not None:
        candidates = candidates[index:index + 1] if index >= 0 else []
    if len(candidates) != 1:
        raise ValueError(f".screen/data-screen-label candidate count {len(candidates)}; use --screen-label or --screen-index for explicit selection")
    selected = candidates[0]
    if not selected["end"]:
        raise ValueError("selected screen subtree is incomplete")
    return html[selected["start"]:selected["end"]], selected["label"] or ""


# ---- 게이트 텍스트: .title·.subtitle·카드 .rtitle ----


def all_text_by_class(html: str, cls: str) -> List[str]:
    """class 토큰이 일치하는 모든 요소의 직속 텍스트(여는 태그 다음~다음 `<`)를 공백 정규화 수집.
    `.title`/`.subtitle`/`.rtitle`은 리프 텍스트 노드라 이 단순 절단으로 충분하다."""
    out: List[str] = []
    lower = html.lower()
    i = 0
    while True:
        lt = lower.find("<", i)
        if lt < 0:
            break
        gt = tag_end(html, lt)
        if gt < 0:
            break
        raw = html[lt + 1:gt]
        sp = WS_RE.search(raw)  # 닫는 태그·속성 없는 태그는 공백 없음 → 건너뜀
        if sp is not None:
            attrs = parse_attrs(raw[sp.start() + 1:])
            if has_class(attrs.get("class", ""), cls):
                next_lt = html.find("<", gt + 1)
                text = html[gt + 1:next_lt if next_lt >= 0 else len(html)]
                clean = WS_COLLAPSE_RE.sub(" ", text).strip()
                if clean:
                    out.append(clean)
        i = gt + 1
    return out


def gate_text(app: str) -> Dict[str, object]:
    titles = all_text_by_class(app, "title")
    subtitles = all_text_by_class(app, "subtitle")
    return {
        "title": titles[0] if titles else "",
        "subtitle": subtitles[0] if subtitles else "",
        "cards": all_text_by_class(app, "rtitle"),
    }


# ---- 이미지: `<img>` 전수 → web/static/images/ + manifest ----


from fetch_images import assign_token, fetch_one


def collect_images(app: str, doc_slug: str, asset_base: str, images_dir: str, document: str, source_manifest_arg: Optional[str]):
    """Collect selected screen images, CSS URLs, and statically imported components."""
    from pathlib import Path
    from asset_io import frozen_resource, load_source_manifest, read_resource, source_identity_root, source_index
    from design_sources import dependencies
    from freeze_design import resolve_source

    root = Path(asset_base).resolve()
    frozen_manifest = load_source_manifest(root, source_manifest_arg)
    files = frozen_manifest.get("files", [])
    by_source = source_index(frozen_manifest)
    identity_root = source_identity_root(frozen_manifest, root)
    by_local = {row["local_path"]: row for row in files if row.get("local_path")}
    document_path = Path(document).resolve()
    relative = document_path.relative_to(root).as_posix() if document_path.is_relative_to(root) else ""
    origin = by_local.get(relative, {}).get("source", str(document_path))
    pending = [(app, "html", origin)]
    images = []
    unresolved = []
    seen_sources = set()
    used_tokens = set()
    while pending:
        content, kind, parent = pending.pop(0)
        alts = {}
        for match in re.finditer(r"<img\b[^>]*>", content, flags=re.I):
            attrs = parse_attrs(match[0])
            alts[attrs.get("src", "")] = attrs.get("alt", "")
        for src, dep_kind, base_kind in dependencies(content, kind):
            if dep_kind not in ("image", "component", "css", "script"):
                continue
            try:
                base_source = origin if kind in ("component", "script") and base_kind == "document" else parent
                resolved = resolve_source(src, base_source, identity_root)
                if resolved in seen_sources:
                    continue
                seen_sources.add(resolved)
                if frozen_manifest:
                    acquired, expected_hash = frozen_resource(resolved, by_source, root)
                else:
                    acquired, expected_hash = resolved, None
                if dep_kind == "image":
                    token = assign_token(resolved, doc_slug, len(images) + 1, used_tokens)
                    item = fetch_one(src, alts.get(src, ""), token, images_dir, str(root), acquired, expected_hash)
                    item.update(source_document=parent, resolved_source=resolved)
                    images.append(item)
                else:
                    data, _mime = read_resource(acquired, str(root))
                    if expected_hash and hashlib.sha256(data).hexdigest() != expected_hash:
                        raise ValueError("frozen dependency changed since source manifest")
                    pending.append((data.decode("utf-8-sig"), dep_kind, resolved))
            except Exception as error:
                unresolved.append({"source": src, "source_document": parent, "reason": f"{type(error).__name__}: {error}"})
                warn(f"dependency unresolved: {src}: {error}")
    return images, unresolved


# ---- 진입점 ----


def main(argv: List[str]) -> None:
    dc_html: Optional[str] = None
    tokens_path: Optional[str] = None
    manifest_path: Optional[str] = None
    assets_root: Optional[str] = None
    asset_base: Optional[str] = None
    meta_path: Optional[str] = None
    screen_label: Optional[str] = None
    source_manifest_arg: Optional[str] = None
    screen_index: Optional[int] = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--tokens":
            i += 1
            tokens_path = argv[i] if i < len(argv) else None
        elif arg == "--asset-manifest":
            i += 1
            manifest_path = argv[i] if i < len(argv) else None
        elif arg == "--assets-root":
            i += 1
            assets_root = argv[i] if i < len(argv) else None
        elif arg == "--asset-base":
            i += 1
            asset_base = argv[i] if i < len(argv) else None
        elif arg == "--meta":
            i += 1
            meta_path = argv[i] if i < len(argv) else None
        elif arg == "--source-manifest":
            i += 1
            source_manifest_arg = argv[i] if i < len(argv) else None
        elif arg == "--screen-label":
            i += 1
            screen_label = argv[i] if i < len(argv) else None
        elif arg == "--screen-index":
            i += 1
            try:
                screen_index = int(argv[i])
            except (IndexError, ValueError):
                die("--screen-index requires a non-negative integer")
        else:
            dc_html = arg
        i += 1

    if None in (dc_html, tokens_path, manifest_path, assets_root, asset_base, meta_path):
        print("사용: python extract_dc.py <screen.dc.html> --tokens <design-tokens.json> "
              "--asset-manifest <asset-manifest.json> --assets-root <프로젝트 루트> "
              "--asset-base <design-ref 디렉터리> --meta <screen-meta.json>", file=sys.stderr)
        sys.exit(1)
    assert dc_html and tokens_path and manifest_path and assets_root and asset_base and meta_path

    if not os.path.isfile(dc_html):
        die(f".dc.html 부재: {dc_html} — Phase 0 동결 누락(시안 미반영).")

    # 실행 순서 계약(MF-3): extract_design --from-ds-manifest 선행이 design-tokens.json을 만든다.
    # 부재면 fail-loud. web엔 아이콘 축이 없어 내용 주입(RMW)은 없다 — 존재 검사만.
    if not os.path.isfile(tokens_path):
        die(f"design-tokens.json 부재: {tokens_path} — extract_design --from-ds-manifest 선행이 "
            "누락됐다(실행 순서 위반·MF-3). extract_dc는 통째 생성하지 않는다.")

    with open(dc_html, "rb") as f:
        source_bytes = f.read()
    try:
        html = source_bytes.decode("utf-8-sig")
    except UnicodeError as error:
        die(f"source is not complete UTF-8: {error}")

    try:
        app, selected_label = select_screen(html, screen_label, screen_index)
    except ValueError as error:
        die(str(error))

    screen_name = os.path.basename(dc_html)
    doc_slug = re.sub(r"[^a-z0-9]+", "_",
                      re.sub(r"\.dc\.html?$|\.html?$", "", screen_name, flags=re.IGNORECASE).lower()
                      ).strip("_") or "screen"

    images_dir = os.path.join(assets_root, IMAGES_SUBDIR)
    try:
        images, unresolved = collect_images(app, doc_slug, asset_base, images_dir, dc_html, source_manifest_arg)
    except (OSError, ValueError) as error:
        die(f"invalid source manifest: {error}")
    meta = gate_text(app)
    selected_parser = ScreenParser(app)
    selected_parser.feed(app)
    meta.update(screen_label=selected_label, explicit_frames=selected_parser.frames,
                source_sha256=hashlib.sha256(source_bytes).hexdigest())

    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"images": images, "source_ready": not unresolved and all(e["status"] in ("ok", "inline") for e in images), "unresolved": unresolved}, indent=2, ensure_ascii=False) + "\n")
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

    def count(s: str) -> int:
        return sum(1 for e in images if e["status"] == s)

    cards = meta["cards"]
    assert isinstance(cards, list)
    print(f"[extract-dc] {screen_name} · 이미지 {len(images)}"
          f"(ok {count('ok')}·failed {count('failed')}·inline {count('inline')}·skipped {count('skipped')}) · "
          f"카드 {len(cards)} → {manifest_path}·{meta_path}")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
