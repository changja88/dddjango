#!/usr/bin/env python3
"""fetch_images — 동결 design-ref HTML의 모든 `<img>`를 빌드타임 동결 → web/static/images + asset-manifest.json.

dddart `fetch_images.dart`의 이식·간소화다(JSX 스캔 축은 web에 불요해 미이식 —
참조 HTML 카피 시나리오는 *.html만 동결된다). extract_design이 *토큰*(색·간격·타이포)을
절단하듯, 이 도구는 시안의 *이미지 바이트*를 `--assets-root` 기준 `web/static/images/`로
동결하고 src→local_path→token 매핑을 `asset-manifest.json`(단일 SSOT)으로 절단한다.
**모든 `<img>` 전수** — 카드 썸네일·리스트 아바타 등 중첩 이미지 포함(같은 src는 1회만 기록).

src 처리: 원격 URL=바이트 다운로드(타임아웃) / data:=인라인 디코드 /
로컬 상대경로=`--asset-base` 기준 해소 복사 / 동적 `src={expr}`·해소 불가=skipped.
파일명 토큰은 소스명 기반 결정론(slug·다른 src와 충돌 시 src 해시 접미).

사용:
  python fetch_images.py <design-ref 디렉터리> --assets-root <프로젝트 루트> \\
    [--asset-base <design-ref 디렉터리>] --out <asset-manifest.json>

산출: {images:[{src, alt, local_path, token, status}]} — status ok/inline/failed/skipped.
종료: 0=성공(**부분 실패 fail-loud — status·[warn] stderr로 표면화하되 exit 0 유지**) /
      1=사용법·design-ref 부재.
"""
from __future__ import annotations

import hashlib
import json
import os
import posixpath
import re
import sys
import urllib.parse
import urllib.request
from typing import Dict, List, Optional

FETCH_TIMEOUT_SEC = 20
IMAGES_SUBDIR = os.path.join("web", "static", "images")
IMAGES_PREFIX = "web/static/images"  # local_path 표기(assets-root 기준·posix)

WORD_RE = re.compile(r"[A-Za-z0-9]")
WS_RE = re.compile(r"\s")
ATTR_RE = re.compile(r"""([\w:-]+)\s*=\s*("([^"]*)"|'([^']*)'|(\S+))""")


def warn(msg: str) -> None:
    print(f"[warn] {msg}", file=sys.stderr)


# ---- HTML 토크나이저(dart `_tagEnd`·`_parseAttrs` 동형 이식 — extract_dc.py와 국소 복제 짝) ----


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


def ext_from_mime(mime: Optional[str]) -> Optional[str]:
    if not mime:
        return None
    m = mime.lower()
    if "png" in m:
        return "png"
    if "jpeg" in m or "jpg" in m:
        return "jpg"
    if "gif" in m:
        return "gif"
    if "webp" in m:
        return "webp"
    if "svg" in m:
        return "svg"
    return None


def ext_from_magic(b: bytes) -> Optional[str]:
    if len(b) >= 4 and b[:4] == b"\x89PNG":
        return "png"
    if len(b) >= 3 and b[:3] == b"\xff\xd8\xff":
        return "jpg"
    if len(b) >= 3 and b[:3] == b"GIF":
        return "gif"
    if len(b) >= 12 and b[8:12] == b"WEBP":
        return "webp"
    return None


def fetch_one(src: str, alt: str, token: str, images_dir: str,
              resolve_base: Optional[str]) -> Dict[str, str]:
    """한 `<img>`의 src를 스킴별로 처리하고 manifest 엔트리를 만든다.
    http(s)=다운로드(타임아웃) / data:=인라인 디코드 / resolve_base 있음=로컬 상대경로 복사
    / 그 외=skipped. 실패·스킵은 status + [warn] stderr로 표면화(조용한 폴백 금지)."""
    status = "failed"
    ext = "png"
    data: Optional[bytes] = None

    if src.startswith("data:"):
        comma = src.find(",")
        if comma > 0:
            meta = src[5:comma]  # 예: image/png;base64
            data_part = src[comma + 1:]
            try:
                if "base64" in meta:
                    import base64 as _b64
                    data = _b64.b64decode(re.sub(r"\s", "", data_part), validate=False)
                else:
                    data = urllib.parse.unquote(data_part).encode("utf-8")
                ext = ext_from_mime(meta) or ext_from_magic(data) or "png"
                status = "inline"
            except (ValueError, UnicodeError):
                status = "failed"
        else:
            status = "failed"
    elif src.startswith(("http://", "https://")):
        try:
            req = urllib.request.Request(src, headers={"User-Agent": "dddjango-web-fetch/1"})
            with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SEC) as res:
                if res.status == 200:
                    data = res.read()
                    ext = ext_from_mime(res.headers.get_content_type()) or ext_from_magic(data) or "png"
                    status = "ok"
                else:
                    status = "failed"
        except Exception:  # 타임아웃·네트워크·HTTP 오류 — 전부 status로 표면화
            status = "failed"
            data = None
    elif resolve_base is not None:
        if src.startswith("{"):
            status = "skipped"  # 동적 표현식 src={expr}: 정적 해소 불가 → fail-loud(skipped)
        else:
            try:
                rel = urllib.parse.unquote(src.split("?", 1)[0].split("#", 1)[0])
                resolved = os.path.normpath(os.path.join(resolve_base, rel))
                if os.path.isfile(resolved):
                    with open(resolved, "rb") as f:
                        data = f.read()
                    suffix = os.path.splitext(resolved)[1].lstrip(".").lower()
                    ext = ext_from_magic(data) or (suffix if suffix else "png")
                    status = "ok"
                else:
                    status = "failed"  # 파일 없음 → fail-loud
            except OSError:
                status = "failed"
                data = None
    else:
        status = "skipped"  # 상대경로·file: 등(--asset-base 없음) — 표면화(조용한 폴백 금지)

    local_path = ""
    if data is not None and status in ("ok", "inline"):
        fname = f"{token}.{ext}"
        os.makedirs(images_dir, exist_ok=True)
        with open(os.path.join(images_dir, fname), "wb") as f:
            f.write(data)
        local_path = f"{IMAGES_PREFIX}/{fname}"

    if status in ("failed", "skipped"):
        warn(f"이미지 {status}: {src}")

    return {"src": src, "alt": alt, "local_path": local_path, "token": token, "status": status}


# ---- 진입점 ----


def main(argv: List[str]) -> None:
    ref_dir: Optional[str] = None
    assets_root: Optional[str] = None
    out_file: Optional[str] = None
    asset_base: Optional[str] = None
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

    # design-ref/*.html을 파일명 정렬(결정론) — 같은 입력 → 같은 파일명·token.
    html_files = sorted(
        os.path.join(ref_dir, name)
        for name in os.listdir(ref_dir)
        if name.lower().endswith((".html", ".htm")) and os.path.isfile(os.path.join(ref_dir, name))
    )

    images: List[Dict[str, str]] = []
    seen_srcs: set = set()
    used_tokens: set = set()
    images_dir = os.path.join(assets_root, IMAGES_SUBDIR)
    resolve_base = os.path.abspath(asset_base) if asset_base is not None else None

    for path in html_files:
        doc_slug = re.sub(r"[^a-z0-9]+", "_",
                          re.sub(r"\.html?$", "", os.path.basename(path), flags=re.IGNORECASE).lower()
                          ).strip("_") or "ref"
        with open(path, encoding="utf-8", errors="replace") as f:
            html = f.read()
        lower = html.lower()
        n = 0
        i = 0
        while True:
            lt = lower.find("<img", i)
            if lt < 0:
                break
            if word_char_at(html, lt + 4):  # `<image` 등 — 태그명 경계 아님
                i = lt + 4
                continue
            gt = tag_end(html, lt)
            if gt < 0:
                break
            raw = html[lt + 1:gt]  # img src="…" alt="…"
            sp = WS_RE.search(raw)
            attrs = parse_attrs(raw[sp.start() + 1:]) if sp is not None else {}
            i = gt + 1
            src = attrs.get("src", "")
            if not src or src in seen_srcs:
                continue
            seen_srcs.add(src)
            n += 1
            token = assign_token(src, doc_slug, n, used_tokens)
            images.append(fetch_one(src, attrs.get("alt", ""), token, images_dir, resolve_base))

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(json.dumps({"images": images}, indent=2, ensure_ascii=False) + "\n")

    def count(s: str) -> int:
        return sum(1 for e in images if e["status"] == s)

    print(f"[fetch-images] 이미지 {len(images)} "
          f"(ok {count('ok')}·failed {count('failed')}·inline {count('inline')}·skipped {count('skipped')}) → {out_file}")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
