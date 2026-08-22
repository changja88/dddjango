#!/usr/bin/env python3
"""extract_dc — Claude Design PROJECT(`.dc.html`)에서 게이트텍스트·이미지 결정론 절단 (dddjango-web).

dddart `extract_dc.dart`의 이식·간소화다. Flutter 아이콘 축(icon_map·icons[] RMW 주입)은
web에 존재하지 않아 **전체 미이식**이다 — `--tokens`는 실행 순서 계약(MF-3: extract_design
--from-ds-manifest 선행) 확인용으로 **존재 검사만** 한다(내용 수정 없음).

**대상은 앱 콘텐츠(`.screen` 서브트리)만**이다 — `.stage`/`.phone`/`.decor`/`.statusbar`는
폰 목업 device-chrome이라 그 안의 `<img>`·텍스트는 출력에 절대 나오지 않는다.
`.screen`이 `<div>` 짝맞춤으로 추출되므로 그 밖의 크롬은 자동 제외된다.

산출:
  - `--meta <screen-meta.json>`: {title, subtitle, cards[]} — `.title`/`.subtitle`/카드
    `.rtitle`의 직속 텍스트. 확인 게이트(MF-1)가 *이 파일만* 인용한다(손추출 금지의 단일 출처).
  - `--asset-manifest <asset-manifest.json>`: `.screen` 안 `<img>` 전수의
    {images:[{src, alt, local_path, token, status}]}. 원격 src는 다운로드(타임아웃)·
    로컬 상대경로는 `--asset-base`(design-ref) 기준 해소 복사 →
    `--assets-root` 기준 `web/static/images/`에 착지.

사용:
  python extract_dc.py <screen.dc.html> --tokens <design-tokens.json> \\
    --asset-manifest <asset-manifest.json> --assets-root <프로젝트 루트> \\
    --asset-base <design-ref 디렉터리> --meta <screen-meta.json>

종료: 0=성공(이미지 부분 실패는 status·[warn] stderr로 표면화) /
      1=사용법·`.dc.html` 부재·`.screen` 부재·tokens 부재(실행 순서 위반).
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


# ---- 앱 콘텐츠: `.screen` 서브트리 절단 ----


def find_screen_start(html: str) -> int:
    """class 토큰에 `screen`을 가진 첫 `<div>`의 `<` 위치. 없으면 -1."""
    lower = html.lower()
    i = 0
    while True:
        lt = lower.find("<div", i)
        if lt < 0:
            return -1
        if word_char_at(html, lt + 4):  # `<divider` 등 — 태그명 경계 아님
            i = lt + 4
            continue
        gt = tag_end(html, lt)
        if gt < 0:
            return -1
        raw = html[lt + 1:gt]  # div class="screen" ...
        sp = WS_RE.search(raw)
        if sp is not None:
            attrs = parse_attrs(raw[sp.start() + 1:])
            if has_class(attrs.get("class", ""), "screen"):
                return lt
        i = gt + 1


def div_subtree(html: str, start_lt: int) -> Optional[str]:
    """start_lt의 `<div ...>`부터 짝 맞는 `</div>`까지 — `<div>`/`</div>` 깊이추적.
    비-div 태그는 깊이에 무관하고 tag_end로 건너뛴다. 균형 실패면 None."""
    lower = html.lower()
    depth = 0
    i = start_lt
    while i < len(html):
        lt = lower.find("<", i)
        if lt < 0:
            break
        if lower.startswith("</div", lt) and not word_char_at(html, lt + 5):
            gt = tag_end(html, lt)
            if gt < 0:
                break
            depth -= 1
            if depth == 0:
                return html[start_lt:gt + 1]
            i = gt + 1
        elif lower.startswith("<div", lt) and not word_char_at(html, lt + 4):
            gt = tag_end(html, lt)
            if gt < 0:
                break
            depth += 1
            i = gt + 1
        else:
            gt = tag_end(html, lt)
            if gt < 0:
                break
            i = gt + 1
    return None


def app_content(html: str) -> Optional[str]:
    start = find_screen_start(html)
    if start < 0:
        return None
    return div_subtree(html, start)


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
    """한 `<img>`의 src를 스킴별로 처리하고 manifest 엔트리를 만든다(dart `_fetchOne` 이식).
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
        status = "skipped"  # 상대경로·file: 등(해소 기준 없음) — 표면화(조용한 폴백 금지)

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


def collect_images(app: str, doc_slug: str, asset_base: str, images_dir: str) -> List[Dict[str, str]]:
    """앱 콘텐츠(`.screen`)의 모든 `<img src>` 전수 처리 — 같은 src는 1회만(엔트리·다운로드 dedupe)."""
    images: List[Dict[str, str]] = []
    seen_srcs: set = set()
    used_tokens: set = set()
    resolve_base = os.path.abspath(asset_base)
    lower = app.lower()
    n = 0
    i = 0
    while True:
        lt = lower.find("<img", i)
        if lt < 0:
            break
        if word_char_at(app, lt + 4):  # `<image` 등 — 태그명 경계 아님
            i = lt + 4
            continue
        gt = tag_end(app, lt)
        if gt < 0:
            break
        raw = app[lt + 1:gt]  # img src="…" alt="…"
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
    return images


# ---- 진입점 ----


def main(argv: List[str]) -> None:
    dc_html: Optional[str] = None
    tokens_path: Optional[str] = None
    manifest_path: Optional[str] = None
    assets_root: Optional[str] = None
    asset_base: Optional[str] = None
    meta_path: Optional[str] = None
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

    with open(dc_html, encoding="utf-8", errors="replace") as f:
        html = f.read()

    app = app_content(html)
    if app is None:
        die(f"`.screen` 서브트리 없음: {dc_html} — 앱 콘텐츠 미검출(동결 누락 또는 "
            "device-chrome만). 동결본을 확인하라.")

    screen_name = os.path.basename(dc_html)
    doc_slug = re.sub(r"[^a-z0-9]+", "_",
                      re.sub(r"\.dc\.html?$|\.html?$", "", screen_name, flags=re.IGNORECASE).lower()
                      ).strip("_") or "screen"

    images_dir = os.path.join(assets_root, IMAGES_SUBDIR)
    images = collect_images(app, doc_slug, asset_base, images_dir)
    meta = gate_text(app)

    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"images": images}, indent=2, ensure_ascii=False) + "\n")
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
