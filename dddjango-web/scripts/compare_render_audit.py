#!/usr/bin/env python3
"""compare_render_audit — 렌더 실측 JSON 2건의 결정론 대조 (dddjango-web).

목표 실측(render-audit.json)과 구현 실측(render-audit-impl.json)을 정규화
텍스트 키로 조인해 축별 diff를 낸다 — G2 시각 대조의 결정적 증적이다(수행
품질과 무관·회귀 재사용 가능). 시각 정합 «전체»의 판정이 아니다: 커버 축은
글자 크기·유효 웨이트·행간·정렬·색·상대 위치·고정(pinned) 인벤토리·앱 컬럼
폭뿐이고, 블록 유무·비텍스트 구성은 육안+시안 대조 소관이다.

입력 JSON은 assets/render_audit.js(콘솔 스니펫)의 산출(audit_version 1)만
받는다 — 스키마 불일치는 fail-loud(exit 1)로, 필드가 바뀐 스니펫과 수제
JSON이 조용히 통과하지 못하게 한다.

사용:
  python compare_render_audit.py <target.json> <impl.json>
  python compare_render_audit.py --validate <audit.json>   # 동결 직후 스키마 검사

축·관용치:
  font-size  : float 파싱 후 ε 0.05px (직렬화 흔들림만 흡수 — rem 유래 소수 차는 실결함)
  weight     : 정확 일치 (유효 웨이트 — 스니펫이 _700 류 패밀리를 해소해 옴)
  line-height: 양쪽 normal=일치 · 한쪽만 normal=diff · 둘 다 px면 ±1px
  text-align : start→left·end→right 정규화 후 일치
  color      : rgb()/rgba() → #rrggbbaa 정규화 · 그 외 직렬화는 [warn]+문자열 비교
  상대 위치  : 앱 컬럼 정규화 center-x 차 > 5% → diff · 조인 쌍 수직 순서 역전 → diff
  pinned     : 인벤토리 대조 — 구현 pinned 0개면 전체 소실, 아니면 키 차집합(목표
               pinned 키가 구현 pinned에 없으면 개별 발화). 세부 rect는 비교 안 함
  중복 키    : 숫자 접기로 같은 키가 된 그룹은 축 값 분포(다중집합)로 그룹 단위 비교
  뷰포트     : 폭 불일치는 [warn] (같은 창폭 실측이 전제 — 전 축 신뢰 불가 경고)

exit: 0=diff 0 / 1=사용법·파싱·스키마(미실행 취급 — 통과가 아니다) / 2=diff ≥1
"""
from __future__ import annotations

import json
import re
import sys

AUDIT_VERSION = 1
FONT_EPS = 0.05
LINE_EPS = 1.0
CENTER_X_TOL = 0.05
ORDER_Y_TOL = 8
UNJOINED_LIST_CAP = 20

RGB_RE = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([0-9.]+)\s*)?\)")
PX_RE = re.compile(r"^(-?[0-9.]+)px$")


def die(msg: str) -> None:
    print(f"[compare-audit] {msg}", file=sys.stderr)
    sys.exit(1)


def load_audit(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        die(f"읽기 실패: {path} ({e})")
    except json.JSONDecodeError as e:
        die(f"JSON 파싱 실패: {path} ({e})")
    if not isinstance(data, dict) or data.get("audit_version") != AUDIT_VERSION:
        die(f"audit_version {AUDIT_VERSION} 아님: {path} — render_audit.js 산출만 받는다")
    for field in ("viewport", "column", "scroll", "texts", "pinned"):
        if field not in data:
            die(f"필수 필드 없음: {field} ({path})")
    for i, t in enumerate(data["texts"]):
        for field in ("key", "text", "fontSize", "weight", "lineHeight", "textAlign", "color", "rect"):
            if field not in t:
                die(f"texts[{i}]에 필드 없음: {field} ({path})")
    if data.get("partial"):
        print(f"[warn] {path}: partial 실측(스니펫 오류 중단) — 결과가 불완전할 수 있다")
    return data


def px(v: str) -> float | None:
    m = PX_RE.match(str(v).strip())
    return float(m.group(1)) if m else None


def norm_align(v: str) -> str:
    return {"start": "left", "end": "right"}.get(str(v), str(v))


def norm_color(v: str) -> tuple[bool, str]:
    """(정규화 성공 여부, 값). rgb/rgba → #rrggbbaa. 그 외 직렬화는 원문."""
    m = RGB_RE.match(str(v).strip())
    if not m:
        return False, str(v).strip()
    r, g, b = (int(m.group(i)) for i in (1, 2, 3))
    a = round(float(m.group(4)) * 255) if m.group(4) is not None else 255
    return True, f"#{r:02x}{g:02x}{b:02x}{a:02x}"


def center_x_ratio(t: dict, column: dict) -> float | None:
    w = column.get("width") or 0
    if w <= 0:
        return None
    r = t["rect"]
    return (r["x"] + r["w"] / 2 - column.get("x", 0)) / w


def axis_sig(t: dict) -> tuple:
    """중복 키 그룹의 분포 비교용 축 서명(rect 제외 — 위치는 그룹 비교 밖)."""
    ok, color = norm_color(t["color"])
    return (str(t["fontSize"]), str(t["weight"]), norm_align(t["textAlign"]), str(t["lineHeight"]), color)


def compare_pair(key: str, a: dict, b: dict, col_a: dict, col_b: dict, diffs: list, warns: list) -> None:
    label = f"«{key}»"
    fa, fb = px(a["fontSize"]), px(b["fontSize"])
    if fa is None or fb is None:
        if str(a["fontSize"]) != str(b["fontSize"]):
            diffs.append(f"{label} font-size {a['fontSize']} ↔ {b['fontSize']}")
    elif abs(fa - fb) > FONT_EPS:
        diffs.append(f"{label} font-size {a['fontSize']} ↔ {b['fontSize']}")
    if str(a["weight"]) != str(b["weight"]):
        diffs.append(f"{label} weight {a['weight']} ↔ {b['weight']}")
    la, lb = str(a["lineHeight"]), str(b["lineHeight"])
    if (la == "normal") != (lb == "normal"):
        diffs.append(f"{label} line-height {la} ↔ {lb}")
    elif la != "normal":
        pa, pb = px(la), px(lb)
        if pa is not None and pb is not None and abs(pa - pb) > LINE_EPS:
            diffs.append(f"{label} line-height {la} ↔ {lb}")
    if norm_align(a["textAlign"]) != norm_align(b["textAlign"]):
        diffs.append(f"{label} text-align {a['textAlign']} ↔ {b['textAlign']}")
    oka, ca = norm_color(a["color"])
    okb, cb = norm_color(b["color"])
    if not (oka and okb):
        if ca != cb:
            warns.append(f"{label} color 비표준 직렬화 — 문자열 비교")
            diffs.append(f"{label} color {ca} ↔ {cb}")
    elif ca != cb:
        diffs.append(f"{label} color {ca} ↔ {cb}")
    ra, rb = center_x_ratio(a, col_a), center_x_ratio(b, col_b)
    if ra is not None and rb is not None and abs(ra - rb) > CENTER_X_TOL:
        diffs.append(f"{label} 상대 위치 center-x {ra:.2f} ↔ {rb:.2f} (컬럼 폭 대비)")


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--validate":
        data = load_audit(argv[2])
        print(f"[compare-audit] validate OK: texts {len(data['texts'])}건 · pinned {len(data['pinned'])}건 · scroll={data['scroll'].get('mode')}")
        return 0
    if len(argv) != 3:
        die("사용: compare_render_audit.py <target.json> <impl.json> | --validate <audit.json>")

    target, impl = load_audit(argv[1]), load_audit(argv[2])
    diffs: list[str] = []
    warns: list[str] = []

    tv, iv = target["viewport"], impl["viewport"]
    if tv.get("w") != iv.get("w"):
        warns.append(f"뷰포트 폭 불일치 target={tv.get('w')} impl={iv.get('w')} — 같은 창폭으로 재실측 권장(전 축 신뢰 불가)")

    tcol, icol = target["column"], impl["column"]
    if abs((tcol.get("width") or 0) - (icol.get("width") or 0)) > 8:
        diffs.append(f"앱 컬럼 폭 {tcol.get('width')} ↔ {icol.get('width')}")

    tmap: dict[str, list] = {}
    imap: dict[str, list] = {}
    for t in target["texts"]:
        tmap.setdefault(t["key"], []).append(t)
    for t in impl["texts"]:
        imap.setdefault(t["key"], []).append(t)

    joined_pairs: list[tuple[dict, dict]] = []
    for key in sorted(set(tmap) & set(imap)):
        ta, tb = tmap[key], imap[key]
        if len(ta) == 1 and len(tb) == 1:
            compare_pair(key, ta[0], tb[0], tcol, icol, diffs, warns)
            joined_pairs.append((ta[0], tb[0]))
        else:
            siga = sorted(axis_sig(t) for t in ta)
            sigb = sorted(axis_sig(t) for t in tb)
            if siga != sigb:
                diffs.append(f"그룹 «{key}» ({len(ta)}↔{len(tb)}건) 축 분포 불일치")

    # 조인 쌍 수직 순서 역전 — 목표 y 순으로 정렬했을 때 구현 y가 역행하면 배치 어긋남
    joined_pairs.sort(key=lambda p: (p[0]["rect"]["y"], p[0]["rect"]["x"], p[0]["key"]))
    for (a1, b1), (a2, b2) in zip(joined_pairs, joined_pairs[1:]):
        if a2["rect"]["y"] - a1["rect"]["y"] > ORDER_Y_TOL and b1["rect"]["y"] - b2["rect"]["y"] > ORDER_Y_TOL:
            diffs.append(f"수직 순서 역전 «{a1['key']}» ↔ «{a2['key']}»")

    if target["pinned"] and not impl["pinned"]:
        keys = " · ".join(p.get("key", "?") for p in target["pinned"][:5])
        diffs.append(f"고정 요소 소실: 목표 pinned {len(target['pinned'])}개({keys}) ↔ 구현 0개")
    elif target["pinned"]:
        # 부분 소실 — 키 차집합(목표 pinned 키가 구현 pinned에 없으면 개별 발화)
        impl_pinned_keys = {p.get("key", "") for p in impl["pinned"]}
        for p in target["pinned"]:
            if p.get("key", "") not in impl_pinned_keys:
                diffs.append(f"고정 요소 소실: 목표 pinned «{p.get('key', '?')}» 가 구현 pinned에 없음")

    only_t = sorted(set(tmap) - set(imap))
    only_i = sorted(set(imap) - set(tmap))

    for w in warns:
        print(f"[warn] {w}")
    for i, d in enumerate(diffs, 1):
        print(f"DIFF {i}) {d}")
    for label, keys in (("목표에만", only_t), ("구현에만", only_i)):
        if keys:
            shown = " · ".join(keys[:UNJOINED_LIST_CAP])
            more = f" 외 {len(keys) - UNJOINED_LIST_CAP}건" if len(keys) > UNJOINED_LIST_CAP else ""
            print(f"INFO 미조인({label} {len(keys)}건): {shown}{more}")
    print(f"[compare-audit] diff {len(diffs)}건 · 조인 {len(joined_pairs) + len([k for k in set(tmap) & set(imap) if len(tmap[k]) > 1 or len(imap[k]) > 1])}키 · 미조인 target {len(only_t)}/impl {len(only_i)}")
    return 2 if diffs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
