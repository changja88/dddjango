#!/usr/bin/env python3
"""Land statically referenced design images in web/static/images with evidence.

Usage: fetch_images.py <design-ref> --assets-root <project root>
       [--asset-base <local source root>] [--source-manifest <path>] --out <asset-manifest.json>

Reads HTML, CSS and JSX recursively, including CSS url() and literal component
images. Each document resolves relative references against its own directory;
source-manifest.json in design-ref or its parent (or --source-manifest) maps
original URLs to already frozen files. With this manifest, kind selects even
extensionless documents and only verified frozen paths can supply bytes; origin
identifiers are resolved separately from the confined file-read root.
Source identities are deduplicated, basename collisions receive stable suffixes.
Output filenames include a content digest so refreshing an asset never overwrites
a previous file; templates consume local_path from the current manifest.
Data/HTTP/local bytes must pass container checks before status ok/inline.

Output: {images:[{src,alt,local_path,token,status,sha256,size_bytes,reason,
source_document,resolved_source}],source_ready,unresolved}. Dynamic/failed entries are loud
and cannot make source_ready true. Exit 0 preserves the partial acquisition
contract; callers must inspect the manifest before passing the source gate.
Container checks do not replace browser decode/render verification.
"""
from __future__ import annotations

import hashlib
import json
import os
import posixpath
import re
import sys
import urllib.parse
from typing import Dict, List, Optional

IMAGES_SUBDIR = os.path.join("web", "static", "images")
IMAGES_PREFIX = "web/static/images"  # local_path 표기(assets-root 기준·posix)

ATTR_RE = re.compile(r"""([\w:-]+)\s*=\s*("([^"]*)"|'([^']*)'|(\S+))""")


def warn(msg: str) -> None:
    print(f"[warn] {msg}", file=sys.stderr)


# ---- HTML 토크나이저(dart `_tagEnd`·`_parseAttrs` 동형 이식 — extract_dc.py와 국소 복제 짝) ----


def parse_attrs(s: str) -> Dict[str, str]:
    """속성 파서 — 쌍·단·무따옴표 3종."""
    attrs: Dict[str, str] = {}
    for m in ATTR_RE.finditer(s):
        attrs[m.group(1).lower()] = m.group(3) or m.group(4) or m.group(5) or ""
    return attrs


# ---- 파일명 토큰: 소스명 기반 결정론(slug·충돌 시 해시 접미) ----


def slug_of_source(src: str) -> Optional[str]:
    """src의 파일명 stem을 소문자 케밥으로 — 파일명 토큰의 결정론 기반(소스명 기반)."""
    if src.startswith("data:"):
        return None
    path = urllib.parse.urlparse(src).path if "://" in src else src
    name = posixpath.basename(path.replace("\\", "/"))
    stem = name.rsplit(".", 1)[0] if "." in name else name
    s = re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
    return s or None


def assign_token(src: str, doc_slug: str, n: int, used: set) -> str:
    """소스명 slug 토큰. 소스명 없음(data: 등)은 `<문서slug>_<n>`. 충돌 시 src 해시 접미(결정론)."""
    base = slug_of_source(src) or f"{doc_slug}_{n}"
    token = base
    if token in used:
        token = f"{base}_{hashlib.sha1(src.encode('utf-8')).hexdigest()[:8]}"
    while token in used:  # 해시 접미까지 충돌(동일 src 재등장은 호출 전에 dedupe됨) — 길이 연장
        token += "x"
    used.add(token)
    return token


# ---- 이미지 바이트 처리(dart `_fetchOne` 이식 — extract_dc.py와 국소 복제 짝) ----


def fetch_one(src: str, alt: str, token: str, images_dir: str,
              resolve_base: Optional[str], resolved_source: Optional[str] = None,
              expected_sha256: Optional[str] = None) -> Dict[str, object]:
    """Acquire and validate complete image bytes before writing a success entry."""
    from pathlib import Path
    from asset_io import digest_fields, image_extension, read_resource, write_verified

    entry: Dict[str, object] = {"src": src, "alt": alt, "local_path": "", "token": token,
                                "status": "failed", "sha256": "", "size_bytes": 0, "reason": ""}
    source = resolved_source or src
    if src.startswith("{") or (resolve_base is None and not source.startswith(("data:", "http://", "https://"))):
        entry.update(status="skipped", reason="dynamic source or missing asset base")
    else:
        try:
            data, _mime = read_resource(source, resolve_base)
            ext = image_extension(data)
            if expected_sha256 and hashlib.sha256(data).hexdigest() != expected_sha256:
                raise ValueError("frozen image changed since source manifest")
            root = Path(images_dir).resolve()
            if not root.is_relative_to(Path(images_dir).parents[2].resolve()):
                raise ValueError("images directory escapes application root")
            filename = f"{token}_{hashlib.sha256(data).hexdigest()[:12]}.{ext}"
            destination = Path(images_dir) / filename
            if not destination.resolve().is_relative_to(root):
                raise ValueError("destination escapes images directory")
            write_verified(destination, data)
            entry.update(status="inline" if src.startswith("data:") else "ok",
                         local_path=f"{IMAGES_PREFIX}/{filename}", **digest_fields(data))
        except Exception as error:  # Network/file/format failures are manifest data, not silent fallbacks.
            entry["reason"] = f"{type(error).__name__}: {error}"
    if entry["status"] in ("failed", "skipped"):
        warn(f"이미지 {entry['status']}: {src} ({entry['reason']})")
    return entry


# ---- 진입점 ----


def main(argv: List[str]) -> None:
    ref_dir: Optional[str] = None
    assets_root: Optional[str] = None
    out_file: Optional[str] = None
    asset_base: Optional[str] = None
    source_manifest_arg: Optional[str] = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--assets-root":
            i += 1
            assets_root = argv[i] if i < len(argv) else None
        elif arg == "--out":
            i += 1
            out_file = argv[i] if i < len(argv) else None
        elif arg == "--asset-base":
            i += 1
            asset_base = argv[i] if i < len(argv) else None
        elif arg == "--source-manifest":
            i += 1
            source_manifest_arg = argv[i] if i < len(argv) else None
        else:
            ref_dir = arg
        i += 1

    if ref_dir is None or assets_root is None or out_file is None:
        print("사용: python fetch_images.py <design-ref 디렉터리> --assets-root <프로젝트 루트> "
              "[--asset-base <design-ref 디렉터리>] --out <asset-manifest.json>", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(ref_dir):
        print(f"[fetch-images] design-ref 디렉터리 없음: {ref_dir}", file=sys.stderr)
        sys.exit(1)

    from pathlib import Path
    from design_sources import dependencies, resource_kind
    from freeze_design import resolve_source

    ref_root = Path(ref_dir).resolve()
    resolve_base = Path(asset_base).resolve() if asset_base is not None else ref_root
    from asset_io import frozen_resource, load_source_manifest, read_resource, source_identity_root, source_index
    try:
        source_manifest = load_source_manifest(ref_root, source_manifest_arg)
    except (OSError, ValueError) as error:
        print(f"[fetch-images] invalid source manifest: {error}", file=sys.stderr)
        sys.exit(1)
    file_rows = source_manifest.get("files", []) if source_manifest else []
    by_source = source_index(source_manifest)
    identity_root = source_identity_root(source_manifest, resolve_base)
    by_local = {row["local_path"]: row for row in file_rows if row.get("local_path")}
    if source_manifest:
        documents = sorted(ref_root / row["local_path"] for row in file_rows
                           if row.get("status") == "ok" and row.get("local_path")
                           and row.get("kind") in ("html", "css", "component"))
    else:
        documents = sorted(path for path in ref_root.rglob("*")
                           if path.is_file() and path.suffix.lower() in (".html", ".htm", ".css", ".jsx", ".tsx"))
    unresolved = []
    images: List[Dict[str, object]] = []
    seen_sources: set = set()
    used_tokens: set = set()
    images_dir = os.path.join(assets_root, IMAGES_SUBDIR)

    for path in documents:
        relative = path.relative_to(ref_root).as_posix()
        source_row = by_local.get(relative, {})
        origin = source_row.get("source", str(resolve_base / relative))
        doc_slug = re.sub(r"[^a-z0-9]+", "_", path.stem.lower()).strip("_") or "ref"
        document_kind = source_row.get("kind", resource_kind(str(path), "html"))
        try:
            if source_manifest:
                frozen_path, expected_hash = frozen_resource(origin, by_source, ref_root)
                payload, _mime = read_resource(frozen_path, str(ref_root))
                if hashlib.sha256(payload).hexdigest() != expected_hash:
                    raise ValueError("frozen document changed since source manifest")
            else:
                payload, _mime = read_resource(str(path), str(ref_root))
            html = payload.decode("utf-8-sig")
        except (OSError, ValueError) as error:
            unresolved.append({"source": origin, "reason": str(error)})
            continue
        # Alt text is metadata only; all static image references include CSS and imported JSX.
        alts = {}
        for match in re.finditer(r"<img\b[^>]*>", html, flags=re.I):
            attrs = parse_attrs(match[0])
            alts[attrs.get("src", "")] = attrs.get("alt", "")
        for src, kind, base_kind in dependencies(html, document_kind):
            if kind != "image":
                continue
            try:
                document_origin = by_local.get(source_manifest.get("entrypoint", ""), {}).get("source", str(resolve_base / "index.html")) if source_manifest else str(resolve_base / "index.html")
                base_source = document_origin if document_kind == "component" and base_kind == "document" else origin
                resolved = resolve_source(src, base_source, identity_root)
            except ValueError as error:
                if source_manifest:
                    unresolved.append({"source": src, "source_document": relative, "reason": str(error)})
                    continue
                resolved = src
            if resolved in seen_sources:
                continue
            seen_sources.add(resolved)
            token = assign_token(resolved, doc_slug, len(images) + 1, used_tokens)
            if source_manifest:
                try:
                    acquired, expected_hash = frozen_resource(resolved, by_source, ref_root)
                except ValueError as error:
                    unresolved.append({"source": src, "source_document": relative, "reason": str(error)})
                    continue
            else:
                acquired, expected_hash = resolved, None
            item = fetch_one(src, alts.get(src, ""), token, images_dir,
                             str(ref_root if source_manifest else resolve_base), acquired, expected_hash)
            item.update(source_document=relative, resolved_source=resolved)
            images.append(item)

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(json.dumps({"images": images, "source_ready": not unresolved and source_manifest.get("source_ready", True) and all(e["status"] in ("ok", "inline") for e in images), "unresolved": unresolved}, indent=2, ensure_ascii=False) + "\n")

    def count(s: str) -> int:
        return sum(1 for e in images if e["status"] == s)

    print(f"[fetch-images] 이미지 {len(images)} "
          f"(ok {count('ok')}·failed {count('failed')}·inline {count('inline')}·skipped {count('skipped')}) → {out_file}")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
