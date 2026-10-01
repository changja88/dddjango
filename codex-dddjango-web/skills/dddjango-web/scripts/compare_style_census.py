"""W8 v4 report comparator — paint-region model (DOM-agnostic).

Visual primitives per side:
  region  a cluster of paint layers (painted boxes + absolutely positioned paint pseudos) sharing a rect (±2.5px)
          -> one visual surface; its signature is the union of its layers (bg colours, bg images, borders,
             shadow layers, backdrop, filter, radius, opacity, binding min/max sizes)
  text    glyph run (own text nodes of one element)
  media   img / video / canvas / svg
  icon    content pseudo (icon font glyph / mask) without a region of its own
Pairing: regions by whitespace-stripped label, then position relative to the paired parent region;
         texts by exact text, digit-folded text, then position inside the paired parent region.
Findings: prop (visual property), geom (size / inset in parent region), missing, extra.
Non-visual computed differences are normalised away (see NORMALISE notes inline).
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

PX_TOL = 0.5
GEOM_TOL = 1.0
COLOR_TOL = 2.0        # premultiplied channel delta (0..255)
ALPHA_TOL = 3
OP_TOL = 0.02
REGION_EPS = 2.5
PLACEHOLDER_EPS = 3.0
PARITY_FLOOR = 0.85   # share of design text runs present in the implementation; below → «미대조(데이터)» case
# 보고 API의 보관 입력 재생 설정. 제품 CLI는 legacy 우회를 제공하지 않는다.
DECLARED = set()
STANDARD_ROUTES = (None, ["operator-hosts"])
ALLOW_LEGACY = False
SDK_SCOPE = None
LABEL_NEAR = 80.0

COLOR_RE = re.compile(r"color\(srgb ([\d.e-]+) ([\d.e-]+) ([\d.e-]+)(?: / ([\d.e-]+%?))?\)|rgba?\((\d+(?:\.\d+)?), (\d+(?:\.\d+)?), (\d+(?:\.\d+)?)(?:, ([\d.]+))?\)")
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?(?:e-?\d+)?")


def _c(m: re.Match) -> str:
    if m.group(1) is not None:
        r, g, b = (round(float(m.group(i)) * 255) for i in (1, 2, 3))
        a = m.group(4)
        av = 1.0 if a is None else (float(a[:-1]) / 100 if a.endswith("%") else float(a))
    else:
        r, g, b = (round(float(m.group(i))) for i in (5, 6, 7))
        av = 1.0 if m.group(8) is None else float(m.group(8))
    return f"#{r:02x}{g:02x}{b:02x}{round(av * 255):02x}"


def norm(v) -> str:
    s = str(v)
    s = COLOR_RE.sub(_c, s)
    s = re.sub(r"url\(\"?([^\")]*)\"?\)", lambda m: "url(" + m.group(1).split("/")[-1] + ")", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def norm_gradient(s: str) -> str:
    """NORMALISE: implied first/last stop positions (0% / 100%) are made explicit."""
    def fix(m):
        name, body = m.group(1), m.group(2)
        parts = [p.strip() for p in re.split(r",(?![^(]*\))", body)]
        head = []
        if parts and not parts[0].startswith("#"):
            head, parts = [parts[0]], parts[1:]
        if parts:
            if re.fullmatch(r"#[0-9a-f]{8}", parts[0]):
                parts[0] += " 0%"
            if re.fullmatch(r"#[0-9a-f]{8}", parts[-1]):
                parts[-1] += " 100%"
        if head and head[0] in ("180deg", "to bottom"):
            head = []
        return f"{name}(" + ", ".join(head + parts) + ")"
    return re.sub(r"((?:repeating-)?(?:linear|radial|conic)-gradient)\(((?:[^()]|\([^()]*\))*)\)", fix, s)


def split_top(s: str) -> list:
    return [p.strip() for p in re.split(r",(?![^(]*\))", s) if p.strip()]


def tokens(s: str) -> list:
    return [t for t in re.split(r"(#[0-9a-f]{8}|-?\d+(?:\.\d+)?(?:e-?\d+)?%?|[ ,()/|])", s) if t and t != " "]


def col_eq(x: str, y: str) -> bool:
    ca = [int(x[i:i + 2], 16) for i in (1, 3, 5, 7)]
    cb = [int(y[i:i + 2], 16) for i in (1, 3, 5, 7)]
    if ca[3] == 0 and cb[3] == 0:
        return True
    if abs(ca[3] - cb[3]) > ALPHA_TOL:
        return False
    # NORMALISE: premultiplied comparison — a 3/255 rgb delta at 38% alpha is invisible
    return max(abs(ca[i] * ca[3] / 255 - cb[i] * cb[3] / 255) for i in range(3)) <= COLOR_TOL


def tok_equal(a: str, b: str, tol: float = PX_TOL) -> bool:
    if a == b:
        return True
    ta, tb = tokens(a), tokens(b)
    if len(ta) != len(tb):
        return False
    for x, y in zip(ta, tb):
        if x == y:
            continue
        if x.startswith("#") and y.startswith("#") and len(x) == 9 and len(y) == 9:
            if not col_eq(x, y):
                return False
            continue
        if NUM_RE.fullmatch(x.rstrip("%")) and NUM_RE.fullmatch(y.rstrip("%")) and x.endswith("%") == y.endswith("%"):
            if abs(float(x.rstrip("%")) - float(y.rstrip("%"))) > tol:
                return False
            continue
        return False
    return True


def set_equal(la: list, lb: list) -> bool:
    if len(la) != len(lb):
        return False
    used = set()
    for x in la:
        hit = next((j for j, y in enumerate(lb) if j not in used and tok_equal(x, y)), None)
        if hit is None:
            return False
        used.add(hit)
    return True


def px(v):
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)px", str(v).strip())
    return float(m.group(1)) if m else None


def eff_radius(rad: str, r) -> str:
    """NORMALISE: '999px' and '50%' are the same pill once they exceed half the short side."""
    w, h = r[2], r[3]
    half = min(w, h) / 2
    out = []
    for part in str(rad).split(" "):
        if part.endswith("%"):
            v = float(part[:-1]) / 100 * min(w, h)
        else:
            v = px(part)
            if v is None:
                out.append(part)
                continue
        out.append("pill" if v > 0.5 and v >= half - 0.5 else f"{round(v, 1)}px")   # a square corner is never a pill
    return " ".join(out)


def binding(v, size):
    """NORMALISE: min-* 'auto' == '0px' (no floor); max-* 'none' == no ceiling. Only positive floors /
    finite ceilings are visual constraints."""
    p = px(v)
    if v in ("auto", "none", None) or p is None:
        return None
    if p <= 0:
        return None
    return round(p, 1)


def lin_transform(v: str) -> str:
    """NORMALISE: translation is position (covered by geometry); scale/rotate/skew stays visual."""
    m = re.fullmatch(r"matrix\(([^)]*)\)", v or "")
    if not m:
        return v
    a, b, c, d = (round(float(x), 3) for x in m.group(1).split(",")[:4])
    return "none" if (a, b, c, d) == (1, 0, 0, 1) else f"matrix({a}, {b}, {c}, {d})"


def strip_label(s: str) -> str:
    return re.sub(r"\s+", "", s or "")


def contains(outer, inner, eps=1.0):
    return (inner[0] >= outer[0] - eps and inner[1] >= outer[1] - eps and
            inner[0] + inner[2] <= outer[0] + outer[2] + eps and inner[1] + inner[3] <= outer[1] + outer[3] + eps)


def near(a, b, eps):
    return all(abs(a[i] - b[i]) <= eps for i in range(4))


# ── primitive extraction ──
def asset_norm(v: str, assets: dict) -> str:
    """NORMALISE: an image is identified by its bytes (sha256 prefix), not by its file name."""
    if not assets:
        return v
    def one(m):
        u = m.group(1)
        base = u.split("/")[-1].split("?")[0]
        d = assets.get(u) or next((v2 for k2, v2 in assets.items() if k2.endswith("/" + u.lstrip("./"))), None) or assets.get(base)
        if d is None:
            return "url(#" + base + ")"
        if str(d).startswith("unreadable"):
            return "url(#unreadable-" + hashlib.sha1(u.encode()).hexdigest()[:8] + ")"   # N9: two unreadable images are not «the same image»
        return "url(#" + d + ")"
    return re.sub(r"url\(\"?([^\")]*)\"?\)", one, v)


def build(census: dict) -> dict:
    assets = census["meta"].get("assets") or {}
    recs = []
    for r in census["records"]:
        if r.get("ph", 0) == 1 or r.get("occ"):
            continue
        if assets and r.get("s", {}).get("bgi", "none") != "none":
            r = dict(r); r["s"] = dict(r["s"]); r["s"]["bgi"] = asset_norm(r["s"]["bgi"], assets)
        recs.append(r)
    layers = []
    for r in recs:
        if r["k"] == "box":
            layers.append({"r": r["r"], "s": r["s"], "op": r["op"], "label": r["label"], "sig": r["sig"], "src": r, "backdrop": r.get("backdrop")})
        elif r["k"] == "pseudo" and r.get("pr") and (r["s"].get("bg") not in (None, "rgba(0, 0, 0, 0)") or r["s"].get("bgi", "none") != "none"
                                                      or r["s"].get("sh", "none") != "none" or r["s"].get("bd", "0 | 0 | 0 | 0") != "0 | 0 | 0 | 0"):
            s = dict(r["s"]); s.setdefault("bf", "none"); s.setdefault("fil", "none")
            layers.append({"r": r["pr"], "s": s, "op": r["op"] * float(r["s"].get("op") or 1), "label": "", "sig": r["sig"] + r["pn"], "src": r, "pseudo": True})
    # cluster layers into regions (largest first)
    layers.sort(key=lambda L: -(L["r"][2] * L["r"][3]))
    regions = []
    grid = collections.defaultdict(list)   # top-left cell index → regions (clustering in O(n))
    cell = lambda r: (int(r[0] // 5), int(r[1] // 5))
    for L in layers:
        if L.get("backdrop"):
            continue
        cx, cy = cell(L["r"])
        hit = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for g in grid[(cx + dx, cy + dy)]:
                    if near(g["r"], L["r"], REGION_EPS) and (hit is None or g["ord"] < hit["ord"]):
                        hit = g
        if hit:
            hit["layers"].append(L)
        else:
            g = {"r": L["r"], "layers": [L], "label": L["label"], "sig": L["sig"], "ord": len(regions)}
            regions.append(g); grid[(cx, cy)].append(g)
    for g in regions:
        g["label"] = max((L["label"] for L in g["layers"]), key=len)
        g["key"] = strip_label(g["label"])[:40]
        sig = {"bg": [], "bgi": [], "bd": [], "sh": [], "bf": [], "fil": [], "rad": None, "op": None, "minh": None, "maxh": None, "minw": None, "maxw": None, "tr": "none", "pos": "flow"}
        for L in g["layers"]:
            s = L["s"]
            bg = norm(s.get("bg", ""))
            if bg and not bg.endswith("00"):
                sig["bg"].append(bg)
            bgi = norm_gradient(norm(s.get("bgi", "none")))
            if bgi != "none":
                sig["bgi"].append(bgi)
            bd = norm(s.get("bd", "0 | 0 | 0 | 0"))
            # NORMALISE: a fully transparent border paints nothing (its width is layout — compared as geometry)
            bd = " | ".join("0" if re.search(r"#[0-9a-f]{6}00$", side.strip()) else side.strip() for side in bd.split("|"))
            if bd != "0 | 0 | 0 | 0":
                sig["bd"].append(bd)
            sh = norm(s.get("sh", "none"))
            if sh != "none":
                sig["sh"] += split_top(sh)
            for k in ("bf", "fil"):
                v = norm(s.get(k, "none"))
                if v != "none":
                    sig[k].append(v)
            tr = lin_transform(s.get("tr", "none"))
            if tr != "none":
                sig["tr"] = tr
            if s.get("pos") in ("fixed", "sticky"):
                sig["pos"] = s["pos"]
        outer = g["layers"][0]
        sig["rad"] = eff_radius(outer["s"].get("rad", "0px 0px 0px 0px"), outer["r"])
        sig["op"] = round(min(L["op"] for L in g["layers"]), 3)
        for k in ("minh", "maxh"):
            vals = [binding(L["s"].get(k), L["r"][3]) for L in g["layers"]]
            vals = [v for v in vals if v is not None]
            sig[k] = max(vals) if vals else None
        for k in ("minw", "maxw"):
            vals = [binding(L["s"].get(k), L["r"][2]) for L in g["layers"]]
            vals = [v for v in vals if v is not None]
            sig[k] = max(vals) if vals else None
        g["paint"] = sig
    texts = [{"r": r["r"], "t": r["t"], "s": r["s"], "op": r["op"], "sig": r["sig"], "trunc": r.get("trunc", 0), "src": r} for r in recs if r["k"] == "text"]
    media = [{"r": r["r"], "s": r["s"], "op": r["op"], "sig": r["sig"], "tag": r.get("tag"), "src": r} for r in recs if r["k"] == "media"]
    def glyph_rect(r):
        """NORMALISE: an icon-font glyph is a font-size square centred in its owner, whatever the owner box is
        (a 52px badge circle and a bare 24px <i> holding the same 24px glyph are the same icon)."""
        f = px(r["s"].get("fs")) or 0
        if r.get("pr") or not f:
            return r.get("pr") or r["r"]
        cx, cy = r["r"][0] + r["r"][2] / 2, r["r"][1] + r["r"][3] / 2
        return [round(cx - f / 2, 2), round(cy - f / 2, 2), f, f]
    icons = [{"r": glyph_rect(r), "s": r["s"], "op": r["op"] * float(r["s"].get("op") or 1), "sig": r["sig"], "pn": r["pn"], "wh": r.get("pwh"), "src": r}
             for r in recs if r["k"] == "pseudo" and r["s"].get("content") not in ('""', "''") and not r.get("pr")]
    frames = [{"r": r["r"], "s": r["s"], "sig": r["sig"], "label": r["label"], "src": r} for r in recs if r["k"] == "frame"]
    # parent region of every primitive: smallest region containing it (DOM-agnostic)
    # parent = smallest region that contains the primitive AND paints one of its DOM ancestors
    # (decorative glows that merely overlap are not containers)
    for g in regions:
        g["idx"] = {L["src"]["i"] for L in g["layers"]}
    by_idx = {}
    for g in regions:
        for k in g["idx"]:
            by_idx[k] = g
    def parent(rect, exclude=None, anc=None):
        if anc is not None:   # candidates = regions painting a DOM ancestor (O(depth))
            cands = {id(by_idx[k]): by_idx[k] for k in anc if k in by_idx}.values()
        else:
            cands = regions
        best = None
        for g in cands:
            if g is exclude or not contains(g["r"], rect):
                continue
            if exclude is not None and near(g["r"], rect, REGION_EPS):
                continue
            if best is None or g["r"][2] * g["r"][3] < best["r"][2] * best["r"][3]:
                best = g
        return best
    for g in regions:
        anc = set()
        for L in g["layers"]:
            anc |= set(L["src"].get("anc", []))
        g["parent"] = parent(g["r"], exclude=g, anc=anc if any("anc" in L["src"] for L in g["layers"]) else None)
    for coll in (texts, media, icons, frames):
        for x in coll:
            src = x.get("src")
            anc = set(src.get("anc", [])) | {src["i"]} if src is not None and "anc" in src else None
            x["parent"] = parent(x["r"], anc=anc)
    return {"regions": regions, "texts": texts, "media": media, "icons": icons, "frames": frames, "meta": census["meta"]}


def rel(x, parent):
    if parent is None:
        return (x["r"][0], x["r"][1])
    return (x["r"][0] - parent["r"][0], x["r"][1] - parent["r"][1])


def near_pairs(da, ia, keyf, eps=6.0):
    """Same spot on screen (|dx|+|dy|+…≤eps) = same primitive whatever wraps it. O(n log n) sweep on y."""
    import bisect
    ib = sorted(ia, key=lambda e: e["r"][1]); ys = [e["r"][1] for e in ib]
    used, pairs, ud = set(), [], []
    for a in da:
        lo = bisect.bisect_left(ys, a["r"][1] - eps); hi = bisect.bisect_right(ys, a["r"][1] + eps)
        best, bc = None, None
        for j in range(lo, hi):
            if j in used or keyf(ib[j]) != keyf(a):
                continue
            b = ib[j]
            c = abs(a["r"][0] - b["r"][0]) + abs(a["r"][1] - b["r"][1]) + 0.5 * abs(a["r"][2] - b["r"][2]) + 0.1 * abs(a["r"][3] - b["r"][3])
            if c <= eps and (bc is None or c < bc):
                best, bc = j, c
        if best is None:
            ud.append(a)
        else:
            used.add(best); pairs.append((a, ib[best]))
    return pairs, ud, [e for j, e in enumerate(ib) if j not in used]


def greedy(da, ia, keyf, costf, maxcost=None, dbucket=None, ibucket=None):
    """Greedy min-cost pairing within key groups. With buckets, candidates are only generated inside the same
    bucket (e.g. children of the paired parent) — same result for finite costs, linear-ish on large pages."""
    if dbucket is not None:
        kf = keyf
        keyf_d = lambda e: (kf(e), dbucket(e))
        keyf_i = lambda e: (kf(e), ibucket(e))
    else:
        keyf_d = keyf_i = keyf
    dg, ig = collections.defaultdict(list), collections.defaultdict(list)
    for e in da:
        dg[keyf_d(e)].append(e)
    for e in ia:
        ig[keyf_i(e)].append(e)
    pairs, ud, ui = [], [], []
    for k in sorted(set(dg) | set(ig), key=str):
        a, b = list(dg.get(k, [])), list(ig.get(k, []))
        if len(a) * len(b) > 250_000:
            # large groups of identical keys (a label repeated hundreds of times): candidates within ±1000px only
            import bisect
            order = sorted(range(len(b)), key=lambda j: b[j]["r"][1]); ys = [b[j]["r"][1] for j in order]
            cand = []
            for i, x in enumerate(a):
                lo, hi = bisect.bisect_left(ys, x["r"][1] - 1000), bisect.bisect_right(ys, x["r"][1] + 1000)
                cand.extend((costf(x, b[order[q]]), i, order[q]) for q in range(lo, hi))
            cand.sort()
        else:
            cand = sorted((costf(x, y), i, j) for i, x in enumerate(a) for j, y in enumerate(b))
        ui_, uj_ = set(), set()
        for c, i, j in cand:
            if i in ui_ or j in uj_ or (maxcost is not None and c > maxcost):
                continue
            ui_.add(i); uj_.add(j)
            pairs.append((a[i], b[j]))
        ud += [x for i, x in enumerate(a) if i not in ui_]
        ui += [y for j, y in enumerate(b) if j not in uj_]
    return pairs, ud, ui


def compare_case(Dc: dict, Ic: dict, case: str) -> dict:
    findings, info = [], collections.Counter()
    def unrun(prop, d, i, note):
        return {"findings": [{"case": case, "kind": "unrun", "blocking": False, "variant": True, "why": "unrun", "prop": prop, "design": d, "impl": i,
                              "d_sig": "", "i_sig": "", "label": "", "note": note, "d_r": None, "i_r": None}],
                "info": {prop: 1}, "pairs": {}, "regions": [0, 0], "unpaired_text": {"design": [], "impl": []}}
    for side, C in (("design", Dc), ("impl", Ic)):
        m = C["meta"]
        if not ALLOW_LEGACY and ((m.get("census_version") or 0) < 4 or "root_matched" not in m or "route_set" not in m):
            return unrun("schema-" + side, m.get("census_version"), sorted(k for k in ("root_matched", "route_set") if k not in m), "census_version >= 4 with root_matched / route_set required (V5)")
    if SDK_SCOPE is not None:
        m = Ic["meta"]; exp = SDK_SCOPE.get(case)
        vend = {v.get("path"): v.get("status") for v in (m.get("vendor") or [])}
        if exp:
            bad = [f for f in exp.get("files", []) if vend.get(f) not in (200, 304)] + [g for g in exp.get("globals", []) if not (m.get("sdk_globals") or {}).get(g)]
            if m.get("route_set") != ["operator-hosts"] or bad:
                return unrun("sdk-state", exp, [m.get("route_set"), bad], "SDK screen: operator-host route only, SDK files loaded, globals present (V5 cross-check)")
        elif m.get("route_set") is not None or vend:
            return unrun("sdk-state", None, [m.get("route_set"), sorted(vend)], "no SDK expected for this case, but a route set / vendor file was seen (V5)")
    for side, C in (("design", Dc), ("impl", Ic)):
        m = C["meta"]
        if m.get("root_matched", 1) not in (1, "body") or (m.get("root_matched") == "body" and m.get("root")):
            return {"findings": [{"case": case, "kind": "unrun", "blocking": False, "variant": True, "why": "unrun", "prop": "root-selector-" + side, "design": m.get("root"), "impl": m.get("root_matched"), "d_sig": "", "i_sig": "",
                                  "label": "", "note": "root selector must match exactly one element (N7)", "d_r": None, "i_r": None}],
                    "info": {"root selector": 1}, "pairs": {}, "regions": [0, 0], "unpaired_text": {"design": [], "impl": []}}
        if side == "impl" and m.get("route_set", None) not in STANDARD_ROUTES:
            return {"findings": [{"case": case, "kind": "unrun", "blocking": False, "variant": True, "why": "unrun", "prop": "route-set", "design": None, "impl": m.get("route_set"), "d_sig": "", "i_sig": "",
                                  "label": "", "note": "census only under the standard route set (SDK v3.1 §7-6)", "d_r": None, "i_r": None}],
                    "info": {"route set": 1}, "pairs": {}, "regions": [0, 0], "unpaired_text": {"design": [], "impl": []}}
    rd, ri = Dc["meta"]["root_rect"], Ic["meta"]["root_rect"]
    if abs(rd[2] - ri[2]) > 2 or abs(rd[3] - ri[3]) > 2:
        # the two captures are not the same visual frame — comparing would only produce noise
        return {"findings": [{"case": case, "kind": "unrun", "blocking": False, "variant": True, "why": "unrun", "prop": "root-mismatch", "design": rd[2:], "impl": ri[2:], "d_sig": "", "i_sig": "",
                              "label": "", "note": "recapture with the same frame", "d_r": rd, "i_r": ri}],
                "info": {"root mismatch": 1}, "pairs": {}, "regions": [0, 0], "unpaired_text": {"design": [], "impl": []}}
    for side, C in (("design", Dc), ("impl", Ic)):
        m = C["meta"]
        # unrun: fonts not settled / a used family fell back / finite animation running / snippet over budget
        if (m.get("fonts") not in ("loaded", "n/a") or (m.get("running_animations") or 0) > 0
                or m.get("fonts_failed") or m.get("partial")):
            return {"findings": [{"case": case, "kind": "unrun", "blocking": False, "variant": True, "why": "unrun", "prop": "unsettled-" + side, "design": [m.get("fonts"), m.get("fonts_failed"), m.get("partial")], "impl": m.get("running_animations"),
                                  "d_sig": "", "i_sig": "", "label": "", "note": "recapture after fonts.ready / animations finished", "d_r": None, "i_r": None}],
                    "info": {"unsettled": 1}, "pairs": {}, "regions": [0, 0], "unpaired_text": {"design": [], "impl": []}}
    D, I = build(Dc), build(Ic)
    _dsec = [strip_label(x) for x in (Dc["meta"].get("sections") or [])]
    _isec = [strip_label(x) for x in (Ic["meta"].get("sections") or [])]
    _common = set(_dsec) & set(_isec)
    def _tag(B, secs):
        for coll in ("regions", "texts", "media", "icons", "frames"):
            for x in B.get(coll, []):
                src = x.get("src") or (x["layers"][0]["src"] if x.get("layers") else None)
                k = (src or {}).get("sec")
                n = secs[k] if isinstance(k, int) and 0 <= k < len(secs) else None
                x["secn"] = n if n in _common else None
    _tag(D, _dsec); _tag(I, _isec)
    D_text = strip_label(" ".join(t["t"] for t in D["texts"]))
    I_text = strip_label(" ".join(t["t"] for t in I["texts"]))
    pmap = {}  # id(design region) -> impl region
    rpmap = {}  # id(impl region) -> design region

    def content_of(x):
        return strip_label(x.get("t") or x.get("label") or "")
    def parent_variant(x, side):
        """True when the nearest container of x holds different content on the two sides (another data row)."""
        p = x.get("parent")
        while p is not None:
            if side == "d":
                q = pmap.get(id(p))
                if q is not None:
                    return content_of(p) != content_of(q)
            else:
                q = rpmap.get(id(p))
                if q is not None:
                    return content_of(p) != content_of(q)
                lbl = content_of(p)
                return bool(lbl) and lbl not in D_text
            p = p.get("parent")
        return False
    def srcs(x):
        if x is None:
            return []
        if x.get("layers"):
            return [L["src"] for L in x["layers"]]
        return [x["src"]] if x.get("src") else []
    def flag(x, k):
        return any(sr.get(k) for sr in srcs(x))
    def add(kind, prop, d, i, dv, iv, note=""):
        x = d or i
        if d is not None and i is not None:
            own = content_of(d) != content_of(i)
            pv = parent_variant(d, "d")
        else:
            lbl = content_of(x)
            other = I_text if d is not None else D_text
            own = bool(lbl) and lbl not in other
            pv = parent_variant(x, "d" if d is not None else "i")
        variant = own or pv
        # BLOCKING rule: a style property of a paired primitive blocks unless its container holds other data;
        # geometry and missing/extra block unless the primitive itself or its container holds other data.
        if kind == "prop":
            blocking = True                        # FAIL-CLOSED: a style difference blocks even inside another data row
            #   (data-dependent styles are resolved by fixture/state parity at G0 or a data-parity disposition)
        elif kind == "geom" and ("gap-top" in prop or "inset-top" in prop):
            blocking = True                        # vertical spacing is a layout constant, not data
        elif kind == "geom" and "gap-left" in prop:
            try:
                blocking = (not variant) or (abs(float(dv)) <= 40 and abs(float(iv)) <= 40)  # adjacent items: constant gap
            except (TypeError, ValueError):
                blocking = not variant
        elif kind in ("geom", "missing", "extra"):
            blocking = not variant                 # sizes / presence follow the data shown
        else:
            blocking = False
        why = ""
        if blocking and (flag(d, "blurocc") or flag(i, "blurocc")):
            blocking, why = False, "blur-covered"   # seen only through a blurred glass layer → human check
        if blocking and (flag(d, "inf") or flag(i, "inf")) and (kind == "geom" or prop in ("paint.transform", "paint.opacity", "text.opacity")):
            blocking, why = False, "infinite-animation"
        if blocking and kind == "prop" and "#unreadable-" in (str(dv) + str(iv)):
            blocking, why = False, "asset-unreadable"   # N9: the image bytes could not be read — a person compares it
        member = hashlib.sha1(json.dumps([case, kind, prop, str(dv), str(iv), content_of(x)[:30],
                                          [round(v / 4) for v in (x["r"] if x else [0, 0, 0, 0])], (d or {}).get("sig", ""), (i or {}).get("sig", "")],
                                         ensure_ascii=False).encode()).hexdigest()[:12]
        findings.append({"case": case, "kind": kind, "prop": prop, "design": dv, "impl": iv, "variant": variant, "blocking": blocking, "why": why, "member": member,
                         "d_sig": d["sig"] if d else "", "i_sig": i["sig"] if i else "",
                         "label": (x.get("t") or x.get("label") or "")[:30], "note": note,
                         "d_r": d["r"] if d else None, "i_r": i["r"] if i else None})

    def cost_abs(a, b):
        # anchor (top-left) and width matter; height follows content length, so it weighs little
        # v4: never pair across two different sections that exist on both sides
        if a.get("secn") and b.get("secn") and a["secn"] != b["secn"]:
            return 1e9
        return abs(a["r"][0] - b["r"][0]) + abs(a["r"][1] - b["r"][1]) + 0.5 * abs(a["r"][2] - b["r"][2]) + 0.1 * abs(a["r"][3] - b["r"][3])

    def dbk(x):
        p = x.get("parent")
        if p is None:
            return "top"
        q = pmap.get(id(p))
        return q["ord"] if q is not None else "orphan"
    def ibk(x):
        p = x.get("parent")
        return "top" if p is None else (p["ord"] if id(p) in rpmap else "orphan")
    def cost_rel(a, b):
        pa, pb = a.get("parent"), b.get("parent")
        if pa is not None and pb is not None and pmap.get(id(pa)) is pb:
            ra, rb = rel(a, pa), rel(b, pb)
            return abs(ra[0] - rb[0]) + abs(ra[1] - rb[1]) + 0.5 * abs(a["r"][2] - b["r"][2]) + 0.1 * abs(a["r"][3] - b["r"][3])
        if pa is None and pb is None:
            return cost_abs(a, b)
        c = cost_abs(a, b)
        return c if c <= 6 else c + 50  # same spot on screen = same primitive, whatever wraps it

    # media placeholders: design regions/texts/icons inside a design area where the implementation shows media
    impl_media_rects = [m["r"] for m in I["media"] if m["tag"] in ("img", "video", "canvas") and m["r"][2] > 40 and m["r"][3] > 40]

    def is_placeholder(x):
        return False  # placeholders are marked by the census (ph) from the design system's placeholder components

    dreg = [g for g in D["regions"] if not is_placeholder(g)]
    info["design placeholder regions"] += len(D["regions"]) - len(dreg)
    # regions: pass 1 by label (big first, so parents pair before children), pass 2 positional within paired parent
    dreg.sort(key=lambda g: -(g["r"][2] * g["r"][3]))
    ireg = sorted(I["regions"], key=lambda g: -(g["r"][2] * g["r"][3]))
    # label pairing only when the two are near each other; far label matches are usually sample-data
    # differences (the same title in another slot) — those slots are paired by position instead
    def cost_label(a, b):
        c = cost_abs(a, b)
        if c <= LABEL_NEAR or abs(a["r"][0] - b["r"][0]) <= 40:
            return c
        return 1e9
    rp, rud, rui = greedy([g for g in dreg if g["key"]], [g for g in ireg if g["key"]], lambda g: g["key"][:24], cost_label, maxcost=1e8)
    for a, b in rp:
        pmap[id(a)] = b; rpmap[id(b)] = a
    rest_d = rud + [g for g in dreg if not g["key"]]
    rest_i = rui + [g for g in ireg if not g["key"]]
    for _ in range(3):  # iterate: children become pairable once parents are paired
        rp2, rest_d, rest_i = greedy(rest_d, rest_i, lambda g: 0, cost_rel, maxcost=40, dbucket=dbk, ibucket=ibk)
        rp3, rest_d, rest_i = near_pairs(rest_d, rest_i, lambda g: 0)
        rp2 += rp3
        for a, b in rp2:
            pmap[id(a)] = b; rpmap[id(b)] = a
        rp += rp2
        if not rp2:
            break
    for a, b in rp:
        A, B = a["paint"], b["paint"]
        for k in ("bg", "bgi", "bd", "sh", "bf", "fil"):
            if not set_equal(A[k], B[k]):
                add("prop", "paint." + k, a, b, " ; ".join(sorted(A[k])) or "none", " ; ".join(sorted(B[k])) or "none")
        if not tok_equal(A["rad"], B["rad"]):
            add("prop", "paint.radius", a, b, A["rad"], B["rad"])
        if A["tr"] != B["tr"]:
            add("prop", "paint.transform", a, b, A["tr"], B["tr"])
        if A["pos"] != B["pos"]:
            add("prop", "position", a, b, A["pos"], B["pos"])
        if abs(A["op"] - B["op"]) > OP_TOL:
            add("prop", "paint.opacity", a, b, A["op"], B["op"])
        for k in ("minh", "maxh", "minw", "maxw"):
            if (A[k] is None) != (B[k] is None) or (A[k] is not None and abs(A[k] - B[k]) > PX_TOL):
                idx = 3 if k.endswith("h") else 2
                # latent: the floor/ceiling differs but does not change the rendered size in this case
                kind = "latent" if abs(a["r"][idx] - b["r"][idx]) <= GEOM_TOL else "prop"
                add(kind, "size." + k, a, b, A[k], B[k])
        same_label = a["key"] == b["key"]
        for idx, nm in ((2, "w"), (3, "h")):
            if same_label and abs(a["r"][idx] - b["r"][idx]) > GEOM_TOL:
                add("geom", "region." + nm, a, b, a["r"][idx], b["r"][idx])
    def paint_key(g):
        P = g["paint"]
        return (round(g["r"][2]), round(g["r"][3] / 4), "|".join(sorted(P["bg"])), "|".join(sorted(P["bgi"])), "|".join(sorted(P["bd"])), "|".join(sorted(P["sh"])), P["rad"])
    twins, rest_d, rest_i = greedy(rest_d, rest_i, paint_key, cost_abs, maxcost=1e8)
    info["content-variant twin regions"] += len(twins)
    for a, b in twins:
        pmap[id(a)] = b; rpmap[id(b)] = a
    rp_twins = twins
    for g in rest_d:
        add("missing", "region", g, None, g["label"] or "(무명)", "", note=f"{g['r']} {'; '.join(g['paint']['bg'] + g['paint']['bgi'] + g['paint']['sh'][:1])[:80]}")
    for g in rest_i:
        if any(contains(m["r"], g["r"], PLACEHOLDER_EPS) for m in I["media"]) and False:
            continue
        add("extra", "region", None, g, "", g["label"] or "(무명)", note=f"{g['r']} {'; '.join(g['paint']['bg'] + g['paint']['bgi'] + g['paint']['sh'][:1])[:80]}")
    # texts
    dtx = [t for t in D["texts"] if not is_placeholder(t)]
    info["design placeholder texts"] += len(D["texts"]) - len(dtx)
    def cost_text(a, b):
        pa, pb = a.get("parent"), b.get("parent")
        if pa is not None and pb is not None and pmap.get(id(pa)) is pb:
            return cost_rel(a, b)
        if pa is None and pb is None:
            return cost_label(a, b)
        c = cost_abs(a, b)
        return c if c <= 6 else 1e9  # a glyph run never pairs across unrelated containers (single hanja repeat everywhere)
    tp, tud, tui = greedy(dtx, I["texts"], lambda t: t["t"], cost_text, maxcost=1e8, dbucket=dbk, ibucket=ibk)
    tp2, tud, tui = greedy(tud, tui, lambda t: re.sub(r"\d+", "#", t["t"]), cost_text, maxcost=1e8, dbucket=dbk, ibucket=ibk)
    tp3, tud, tui = greedy(tud, tui, lambda t: (t["s"]["fs"], t["s"]["fw"]), cost_rel, maxcost=24, dbucket=dbk, ibucket=ibk)
    tp4, tud, tui = near_pairs(tud, tui, lambda t: 0)
    tp3 += tp4
    for a, b in tp + tp2 + tp3:
        same = a["t"] == b["t"]
        info["content-different text pair"] += (not same)
        for p in ("ff", "fs", "fw", "lh", "ls", "fst", "tt", "td", "c"):
            va, vb = norm(a["s"].get(p)), norm(b["s"].get(p))
            if p == "ff":
                if va.lower() != vb.lower():
                    add("prop", "text." + p, a, b, va, vb)
            elif p == "lh":
                # line-height is layout-level: sub-pixel deltas do not move glyphs visibly
                if not tok_equal(va, vb, tol=GEOM_TOL):
                    add("prop", "text." + p, a, b, va, vb)
            elif p == "ls":
                # NORMALISE: letter-spacing is visible as its accumulation over the run
                la, lb = px(va.replace("normal", "0px")), px(vb.replace("normal", "0px"))
                if la is None or lb is None or abs(la - lb) * max(1, len(a["t"])) > GEOM_TOL:
                    add("prop", "text." + p, a, b, va, vb)
            elif not tok_equal(va, vb):
                add("prop", "text." + p, a, b, va, vb)
        # latent typography: invisible with this content, visible with another (i18n · longer data) — listed, not blocking
        for p in ("ta", "ws", "to"):
            va, vb = a["s"].get(p), b["s"].get(p)
            if p == "ta":
                va = {"start": "left", "end": "right", "-webkit-left": "left"}.get(va, va); vb = {"start": "left", "end": "right", "-webkit-left": "left"}.get(vb, vb)
            if va is not None and vb is not None and va != vb:
                add("latent", "text." + p, a, b, va, vb)
        if same and a["s"].get("lines") != b["s"].get("lines"):
            add("prop", "text.lines", a, b, a["s"].get("lines"), b["s"].get("lines"))
        if a.get("trunc", 0) != b.get("trunc", 0):
            add("prop", "text.truncated", a, b, a.get("trunc", 0), b.get("trunc", 0))
        if abs(a["op"] - b["op"]) > OP_TOL:
            add("prop", "text.opacity", a, b, a["op"], b["op"])
        if same:
            for idx, nm in ((2, "w"), (3, "h")):
                if abs(a["r"][idx] - b["r"][idx]) > GEOM_TOL:
                    add("geom", "text." + nm, a, b, a["r"][idx], b["r"][idx])
    info["text unpaired design"] += len(tud)
    info["text unpaired impl"] += len(tui)
    dts = [t["t"] for t in D["texts"]]
    its = set(t["t"] for t in I["texts"])
    parity = round(sum(1 for t in dts if t in its) / len(dts), 3) if dts else 1.0
    info["text parity"] = parity
    # media and icons
    dmd = [m for m in D["media"] if not is_placeholder(m)]
    mp, mud, mui = greedy(dmd, I["media"], lambda m: "m", cost_rel, maxcost=30, dbucket=dbk, ibucket=ibk)
    for a, b in mp:
        for idx, nm in ((2, "w"), (3, "h")):
            if abs(a["r"][idx] - b["r"][idx]) > GEOM_TOL:
                add("geom", "media." + nm, a, b, a["r"][idx], b["r"][idx])
        for p in ("fit", "fil"):
            if a["tag"] in ("img", "video") and b["tag"] in ("img", "video") and norm(a["s"].get(p)) != norm(b["s"].get(p)):  # slot hosts: size only
                add("prop", "media." + p, a, b, a["s"].get(p), b["s"].get(p))
    icp, icd, ici = greedy(D["icons"], I["icons"], lambda x: x["pn"], cost_rel, maxcost=24, dbucket=dbk, ibucket=ibk)
    # NORMALISE: an svg icon and an icon-font pseudo are the same visual primitive
    icp2, icd, ici = near_pairs(icd, ici, lambda x: x["pn"])
    icp += icp2
    mp2, mud, mui = near_pairs(mud, mui, lambda x: 0)
    mp += mp2
    x_pairs, mud, ici = greedy(mud, ici, lambda x: 0, cost_rel, maxcost=16, dbucket=dbk, ibucket=ibk)
    y_pairs, icd, mui = greedy(icd, mui, lambda x: 0, cost_rel, maxcost=16, dbucket=dbk, ibucket=ibk)
    xp2, mud, ici = near_pairs(mud, ici, lambda x: 0)
    yp2, icd, mui = near_pairs(icd, mui, lambda x: 0)
    x_pairs += xp2; y_pairs += yp2
    for a, b in icp:
        fa, fb = px(a["s"].get("fs")), px(b["s"].get("fs"))
        if fa is not None and fb is not None and abs(fa - fb) > PX_TOL:
            add("prop", "icon.size", a, b, a["s"].get("fs"), b["s"].get("fs"))
        if not tok_equal(norm(a["s"].get("c")), norm(b["s"].get("c"))):
            add("prop", "icon.color", a, b, norm(a["s"].get("c")), norm(b["s"].get("c")))
    for a, b in x_pairs + y_pairs:
        wa = a["r"][2] if a.get("tag") else px(a["s"].get("fs"))
        wb = b["r"][2] if b.get("tag") else px(b["s"].get("fs"))
        if wa is not None and wb is not None and abs(wa - wb) > GEOM_TOL:
            add("geom", "icon.size", a, b, wa, wb)
    for x in mud + icd:
        add("missing", "icon/media", x, None, x.get("tag") or x["sig"], "", note=str(x["r"]))
    for x in mui + ici:
        add("extra", "icon/media", None, x, "", x.get("tag") or x["sig"], note=str(x["r"]))
    # ── local layout: gap to the previous sibling (same parent region), else inset in the parent ──
    # (localises a spacing change to the first primitive after it — no cascade through later siblings)
    allp = [(a, b, "region", a["key"] == b["key"]) for a, b in rp] + [(a, b, "text", a["t"] == b["t"]) for a, b in tp + tp2 + tp3] + \
           [(a, b, "media", True) for a, b in mp] + [(a, b, "icon", True) for a, b in icp + x_pairs + y_pairs]
    pair_of = {id(a): b for a, b, _, _ in allp}
    def prims(S, regs):
        return list(regs) + S["texts"] + S["media"] + S["icons"]
    dprims = prims(D, dreg)
    iprims = prims(I, I["regions"])
    def sib_index(ps):
        ix = collections.defaultdict(list)
        for x in ps:
            ix[id(x.get("parent"))].append(x)
        return ix
    dsib, isib = sib_index(dprims), sib_index(iprims)
    def is_abs(x):
        src = x.get("src") or (x.get("layers") or [{}])[0].get("src") or {}
        return bool(src.get("abs"))
    import bisect
    def sorted_index(ix):
        """per parent: flow siblings sorted by bottom (for prev_v) and by right edge (for prev_h)."""
        out = {}
        for k, lst in ix.items():
            flow = [y for y in lst if not is_abs(y)]
            byb = sorted(flow, key=lambda y: y["r"][1] + y["r"][3])
            byr = sorted(flow, key=lambda y: y["r"][0] + y["r"][2])
            out[k] = (byb, [y["r"][1] + y["r"][3] for y in byb], byr, [y["r"][0] + y["r"][2] for y in byr])
        return out
    dsorted, isorted = sorted_index(dsib), sorted_index(isib)
    def prev_v(x, ix):
        if is_abs(x):
            return None
        byb, bots, _, _ = (dsorted if ix is dsib else isorted).get(id(x.get("parent")), ([], [], [], []))
        j = bisect.bisect_right(bots, x["r"][1] + 0.5) - 1
        while j >= 0:   # nearest bottom above that overlaps horizontally (usually the first or second)
            y = byb[j]
            if y is not x and y["r"][0] < x["r"][0] + x["r"][2] and x["r"][0] < y["r"][0] + y["r"][2]:
                return y
            j -= 1
            if j >= 0 and bots[j] < x["r"][1] - 2000:
                break
        return None
    def prev_h(x, ix):
        if is_abs(x):
            return None
        _, _, byr, rights = (dsorted if ix is dsib else isorted).get(id(x.get("parent")), ([], [], [], []))
        j = bisect.bisect_right(rights, x["r"][0] + 0.5) - 1
        best = None
        while j >= 0:
            y = byr[j]
            if y is not x:
                ov = min(x["r"][1] + x["r"][3], y["r"][1] + y["r"][3]) - max(x["r"][1], y["r"][1])
                if ov > 0.5 * min(x["r"][3], y["r"][3]):
                    return y
            j -= 1
            if j >= 0 and rights[j] < x["r"][0] - 400:
                break
        return best
    def parents_ok(a, b):
        pa, pb = a.get("parent"), b.get("parent")
        return (pa is None and pb is None) or (pa is not None and pb is not None and pmap.get(id(pa)) is pb)
    for a, b, kind, same in allp:
        if not parents_ok(a, b):
            continue
        for axis, prevf, gname, iname, ax in ((1, prev_v, "gap-top", "inset-top", 1), (0, prev_h, "gap-left", "inset-left", 0)):
            if axis == 0 and kind == "text" and not same:
                continue  # NORMALISE: horizontal place of a different-length text follows its content
            sa, sb = prevf(a, dsib), prevf(b, isib)
            if sa is not None and sb is not None:
                if pair_of.get(id(sa)) is not sb:
                    continue  # neighbours differ — reported as missing/extra, not as spacing
                ga = a["r"][ax] - (sa["r"][ax] + sa["r"][ax + 2])
                gb = b["r"][ax] - (sb["r"][ax] + sb["r"][ax + 2])
                if abs(ga - gb) > GEOM_TOL:
                    add("geom", f"{kind}.{gname}", a, b, round(ga, 2), round(gb, 2), note=f"after «{(sa.get('t') or sa.get('label') or sa['sig'])[:16]}»")
            elif sa is None and sb is None:
                if a.get("parent") is None and (is_abs(a) or is_abs(b)):
                    continue
                # no anchor → no position: a primitive sitting inside an unpaired painted box (another data slot)
                # has nothing to be measured against; the root is not an anchor for it
                if a.get("parent") is None and (any(contains(g["r"], a["r"]) for g in rest_d) or any(contains(g["r"], b["r"]) for g in rest_i)):
                    continue
                ra, rb = rel(a, a.get("parent")), rel(b, b.get("parent"))
                if abs(ra[ax] - rb[ax]) > GEOM_TOL:
                    add("geom", f"{kind}.{iname}", a, b, round(ra[ax], 2), round(rb[ax], 2))
    # frames (unpainted size-constrained boxes): only binding min/max floors/ceilings
    fp, _, _ = greedy(D["frames"], I["frames"], lambda f: strip_label(f["label"])[:40], cost_abs, maxcost=40)
    for a, b in fp:
        for k in ("minh", "maxh", "minw", "maxw"):
            va, vb = binding(a["s"].get(k), 0), binding(b["s"].get(k), 0)
            if (va is None) != (vb is None) or (va is not None and abs(va - vb) > PX_TOL):
                idx = 3 if k.endswith("h") else 2
                kind = "latent" if abs(a["r"][idx] - b["r"][idx]) <= GEOM_TOL else "prop"
                add(kind, "size." + k, a, b, va, vb)
    if parity < PARITY_FLOOR and not ("ALL" in DECLARED or case in DECLARED):
        # N1: an undeclared case whose fixture stopped showing the mockup sample is not «uncompared» — it is UNRUN
        return {"findings": [{"case": case, "kind": "unrun", "blocking": False, "variant": True, "why": "unrun", "prop": "parity-below-floor", "design": PARITY_FLOOR, "impl": parity, "d_sig": "", "i_sig": "",
                              "label": "", "note": "restore the comparison fixture (G0 sample parity) or declare the case at G0", "d_r": None, "i_r": None}],
                "info": {"text parity": parity}, "pairs": {}, "regions": [0, 0], "unpaired_text": {"design": [], "impl": []}}
    if parity < PARITY_FLOOR:
        # G0-declared «uncompared (data)» case: pairing and geometry are unreliable, so sizes / presence / spacing go to
        # a person — but a STYLE PROPERTY of a paired primitive still blocks (N1 · fail-closed regardless of parity)
        for f in findings:
            if f["blocking"] and f["kind"] != "prop":
                f["blocking"], f["why"] = False, "uncompared-data"
        findings.append({"case": case, "kind": "uncompared", "prop": "text-parity", "design": PARITY_FLOOR, "impl": parity, "variant": True,
                         "blocking": False, "why": "uncompared-data", "member": "parity-" + case, "d_sig": "", "i_sig": "", "label": "",
                         "note": "comparison fixture must reproduce the mockup sample (G0)", "d_r": None, "i_r": None})
    return {"findings": findings, "info": dict(info),
            "pairs": {"region": len(rp), "text": len(tp) + len(tp2) + len(tp3), "media": len(mp), "icon": len(icp) + len(x_pairs) + len(y_pairs)},
            "regions": [len(D["regions"]), len(I["regions"])],
            "unpaired_text": {"design": [t["t"] for t in tud][:40], "impl": [t["t"] for t in tui][:40]}}


def first_class(sig: str) -> str:
    parts = sig.split(".")
    return parts[1] if len(parts) > 1 else parts[0]


def group(results: dict) -> list:
    agg = collections.defaultdict(list)
    for case, res in results.items():
        for f in res["findings"]:
            f.setdefault("member", f"{f['kind']}-{f['case']}-{f['prop']}")   # unrun / uncompared rows are case-level
            sig = first_class(f["i_sig"] or f["d_sig"])
            def rv(v):
                try:
                    return str(round(float(v) * 2) / 2)
                except (TypeError, ValueError):
                    return str(v)
            if f["kind"] == "prop":
                vals = (str(f["design"]), str(f["impl"]))
            elif f["kind"] in ("geom", "latent"):
                vals = (rv(f["design"]), rv(f["impl"]))
            else:   # missing / extra: what is missing, and how big it is
                r = f["d_r"] or f["i_r"] or [0, 0, 0, 0]
                vals = (strip_label(str(f["design"]))[:24], strip_label(str(f["impl"]))[:24] + f"@{round(r[2])}x{round(r[3])}")
            key = (f["kind"], f["prop"], vals[0], vals[1], sig)
            agg[key].append(f)
    rows = []
    for key, fs in agg.items():
        fs.sort(key=lambda f: (f["case"], f["member"], json.dumps(f, ensure_ascii=False, sort_keys=True)))
        gid = hashlib.sha256(json.dumps(key, ensure_ascii=False).encode()).hexdigest()[:10]
        rows.append({"id": gid, "kind": key[0], "prop": key[1], "design": key[2], "impl": key[3], "sig": key[4], "n": len(fs),
                     "variant": all(f.get("variant") for f in fs), "blocking": any(f.get("blocking") for f in fs),
                     "members": sorted({f["member"] for f in fs}), "blocking_members": sorted({f["member"] for f in fs if f.get("blocking")}),
                     "why": sorted({f.get("why", "") for f in fs} - {""}),
                     "cases": sorted({f["case"] for f in fs}),
                     "examples": [(f["case"], f["label"], f["design"], f["impl"], f["note"], f["d_r"], f["i_r"]) for f in fs[:4]]})
    rows.sort(key=lambda r: (r["kind"], r["sig"], r["prop"], r["design"], r["impl"], r["id"]))
    return rows


def run(dpath: str, ipath: str, mapping: dict, out: str) -> dict:
    D = json.loads(Path(dpath).read_text())
    I = json.loads(Path(ipath).read_text())
    results = {}
    if not isinstance(mapping, dict) or not mapping or not all(isinstance(k, str) and isinstance(v, str) for k, v in mapping.items()):
        raise ValueError("mapping must be a nonempty object of case names")
    if len(set(mapping.values())) != len(mapping):
        raise ValueError("mapping repeats an implementation case")
    for dk, ik in sorted(mapping.items()):
        if dk not in D or ik not in I:
            raise ValueError(f"mapped case missing: {dk} -> {ik}")
        for c in (D[dk], I[ik]):
            total = c["meta"].get("records_total", len(c["records"]))
            if total != len(c["records"]):
                raise ValueError(f"incomplete census pages: {dk} -> {ik}")
        results[ik] = compare_case(D[dk], I[ik], ik)
    rows = group(results)
    Path(out).write_text(json.dumps({"cases": {k: {"pairs": v["pairs"], "regions": v["regions"], "info": v["info"], "n_findings": len(v["findings"]),
                                                   "unpaired_text": v["unpaired_text"]} for k, v in results.items()},
                                     "groups": rows}, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    return {"groups": rows, "results": results}


class ReportParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(1, f"W8: {message}\n")


def main(argv=None):
    global DECLARED, SDK_SCOPE, ALLOW_LEGACY
    parser = ReportParser(description="W8 v4 비차단 보고: 후보가 있어도 exit 0, 미실행/입력 오류 exit 1")
    for name in ("design", "impl", "mapping", "sdk-scope", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--declared-data-case", action="append", default=[], metavar="CASE")
    args = parser.parse_args(argv)
    try:
        mapping = json.loads(args.mapping.read_text())
        SDK_SCOPE = json.loads(args.sdk_scope.read_text())
        if not isinstance(SDK_SCOPE, dict) or not all(
            isinstance(v, dict) and all(isinstance(v.get(k, []), list) and
            all(isinstance(x, str) for x in v.get(k, [])) for k in ("files", "globals"))
            for v in SDK_SCOPE.values()
        ):
            raise ValueError("sdk-scope must map case names to files/globals lists")
        DECLARED = set(args.declared_data_case)
        if "ALL" in DECLARED or not DECLARED.issubset(set(mapping.values())):
            raise ValueError("declare mapped implementation cases individually")
        ALLOW_LEGACY = False
        result = run(args.design, args.impl, mapping, args.out)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, IndexError) as exc:
        print(f"W8 미실행: {exc}", file=sys.stderr)
        return 1
    groups = result["groups"]
    candidates = [g for g in groups if g["blocking"]]
    unrun = [k for k, v in result["results"].items() if any(f["kind"] == "unrun" for f in v["findings"])]
    uncompared = [k for k, v in result["results"].items() if any(f["kind"] in ("unrun", "uncompared") for f in v["findings"])]
    print(f"W8 보고: 묶음 {len(groups)} · 후보 {len(candidates)} · 후보 구성원 {sum(len(g['blocking_members']) for g in candidates)} · 미대조 case {len(uncompared)} · 미실행 case {len(unrun)}")
    return 1 if unrun else 0


if __name__ == "__main__":
    raise SystemExit(main())
