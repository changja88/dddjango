/* style_census — W8 v4 report (dddjango-web).
 * DOM-agnostic visual census of one rendered case: glyph runs, painted boxes, icons/media, pseudo icons.
 * Synchronous, no waits, no DOM or scroll mutation. Called as
 *   page.evaluate(SRC, {root: '<css selector>' | null, page: 0, pageSize: 4000})
 * Returns {meta, records[...]} for the requested page (pagination replaces the old 200 cap).
 */
(arg) => {
  'use strict';
  const t0 = performance.now();
  const opt = Object.assign({ root: null, page: 0, pageSize: 100000, placeholders: [], exclude: [], budgetMs: 5000, routeSet: null, sdkGlobals: [] }, typeof arg === 'string' ? { root: arg } : (arg || {}));
  const rootHits = opt.root ? document.querySelectorAll(opt.root).length : 0;
  if (opt.root && rootHits !== 1) return { meta: { census_version: 4, root: opt.root, root_matched: rootHits, partial: false, records_total: 0 }, records: [] };
  const root = opt.root ? document.querySelector(opt.root) : document.body;   // no selector = whole body (recorded as root_matched:'body')
  const rr = root.getBoundingClientRect();
  const norm = (s) => (s || '').normalize('NFC').replace(/ /g, ' ').replace(/\s+/g, ' ').trim();
  const r2 = (v) => Math.round(v * 100) / 100;
  const TRANSPARENT = 'rgba(0, 0, 0, 0)';
  // ── element walk (shadow roots included) ──
  const all = [];
  const walk = (r) => { for (const n of r.querySelectorAll('*')) { all.push(n); if (n.shadowRoot) walk(n.shadowRoot); } };
  all.push(root); walk(root);
  // cumulative opacity / visibility with memo
  const opMemo = new Map();
  const cumOp = (n) => {
    if (!n || n.nodeType !== 1) return 1;
    if (opMemo.has(n)) return opMemo.get(n);
    const s = getComputedStyle(n);
    let v;
    if (s.display === 'none') v = 0;
    else v = parseFloat(s.opacity) * (n === root ? 1 : cumOp(n.parentElement || (n.getRootNode && n.getRootNode().host)));
    opMemo.set(n, v);
    return v;
  };
  // scroll origin: measure every scroller at its own origin is impossible without moving;
  // we record document-space coords by adding the scrollTop/Left of all scrolling ancestors.
  const scrollers = [];
  for (const n of all) {
    const s = getComputedStyle(n);
    if ((/(auto|scroll)/.test(s.overflowY) && n.scrollHeight > n.clientHeight + 1) ||
        (/(auto|scroll)/.test(s.overflowX) && n.scrollWidth > n.clientWidth + 1)) scrollers.push(n);
  }
  const scrollOff = (n) => { let dx = 0, dy = 0; for (const sc of scrollers) if (sc !== n && sc.contains(n)) { dx += sc.scrollLeft; dy += sc.scrollTop; } return [dx, dy]; };
  const rectOf = (n, r) => { const [dx, dy] = scrollOff(n); return [r2(r.left - rr.left + dx), r2(r.top - rr.top + dy), r2(r.width), r2(r.height)]; };
  // design placeholder components (e.g. image-slot): host = 2, inside = 1 (crosses shadow roots)
  const phSel = (opt.placeholders || []).join(',');
  const phOf = (n) => {
    if (!phSel) return 0;
    if (n.matches && n.matches(phSel)) return 2;
    for (let p = n.parentElement || (n.getRootNode && n.getRootNode().host); p; p = p.parentElement || (p.getRootNode && p.getRootNode().host)) {
      if (p.matches && p.matches(phSel)) return 1;
    }
    return 0;
  };
  const exSel = (opt.exclude || []).join(',');
  const exOf = (n) => { if (!exSel) return 0; for (let p = n; p; p = p.parentElement || (p.getRootNode && p.getRootNode().host)) if (p.matches && p.matches(exSel)) return 1; return 0; };
  const sig = (n) => { const c = (typeof n.className === 'string' ? n.className : (n.className && n.className.baseVal) || '').trim(); return n.tagName.toLowerCase() + (c ? '.' + c.split(/\s+/).slice(0, 3).join('.') : ''); };
  const alphaOf = (c) => { const m = /rgba?\(([^)]*)\)/.exec(c); if (m) { const v = m[1].split(',').map(parseFloat); return v.length > 3 ? v[3] : 1; }
                           const q = /color\(srgb [^/)]*(?:\/\s*([\d.]+))?\)/.exec(c); return q ? (q[1] === undefined ? 1 : parseFloat(q[1])) : 0; };
  // a border/outline whose colour is fully transparent paints nothing (its width is layout, measured as geometry)
  const painted = (s) => alphaOf(s.backgroundColor) > 0 || s.backgroundImage !== 'none' || s.boxShadow !== 'none' ||
    (s.backdropFilter && s.backdropFilter !== 'none') ||
    ['Top', 'Right', 'Bottom', 'Left'].some((k) => s['border' + k + 'Style'] !== 'none' && parseFloat(s['border' + k + 'Width']) > 0 && alphaOf(s['border' + k + 'Color']) > 0) ||
    (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0 && alphaOf(s.outlineColor) > 0);
  const isBackdrop = (r) => r.width >= rr.width * 0.95 && r.height >= rr.height * 0.6; // page/frame backgrounds — still recorded, never a container
  const sides = (s, p) => ['Top', 'Right', 'Bottom', 'Left'].map((k) => s[p + k + (p === 'border' ? 'Width' : '')]);
  const borderOf = (s) => ['Top', 'Right', 'Bottom', 'Left'].map((k) =>
    (s['border' + k + 'Style'] === 'none' || parseFloat(s['border' + k + 'Width']) === 0) ? '0' : s['border' + k + 'Width'] + ' ' + s['border' + k + 'Style'] + ' ' + s['border' + k + 'Color']).join(' | ');
  const radiusOf = (s) => [s.borderTopLeftRadius, s.borderTopRightRadius, s.borderBottomRightRadius, s.borderBottomLeftRadius].join(' ');
  const boxStyle = (s) => ({
    bg: s.backgroundColor, bgi: s.backgroundImage === 'none' ? 'none' : s.backgroundImage.replace(/url\("?[^")]*\/([^/")]+)"?\)/g, 'url($1)').slice(0, 300),
    bd: borderOf(s), rad: radiusOf(s), sh: s.boxShadow, ol: (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) ? s.outlineWidth + ' ' + s.outlineStyle + ' ' + s.outlineColor : 'none',
    bf: s.backdropFilter || 'none', fil: s.filter, tr: s.transform, mbm: s.mixBlendMode, clip: s.clipPath,
    pad: sides(s, 'padding').join(' '), gap: s.rowGap + ' ' + s.columnGap,
    minw: s.minWidth, maxw: s.maxWidth, minh: s.minHeight, maxh: s.maxHeight, pos: (s.position === 'fixed' || s.position === 'sticky') ? s.position : 'flow',
  });
  // ── sections: headings in document order ──
  // section = last heading met in document order (single pass — O(N))
  const heads = [];
  const secMap = new Map();
  { let cur = -1; for (const n of all) { if (/^H[1-6]$/.test(n.tagName) || n.getAttribute('role') === 'heading') { heads.push(n); cur = heads.length - 1; } secMap.set(n, cur); } }
  const secOf = (n) => (secMap.has(n) ? secMap.get(n) : -1);
  // ── records ──
  const recs = [];
  const recOf = new Map(); // element -> box record index (painted boxes only, used as containers)
  let visibleCount = 0, excludedCount = 0;
  let partial = false;
  for (const n of all) {
    if (performance.now() - t0 > opt.budgetMs) { partial = true; break; }
    const op = cumOp(n);
    if (op <= 0.001) continue;
    const s = getComputedStyle(n);
    if (s.visibility === 'hidden' || s.visibility === 'collapse') continue;
    if (n.closest && n.closest('[hidden]')) continue;
    const r = n.getBoundingClientRect();
    if (r.width === 0 && r.height === 0 && s.display !== 'contents') continue;
    // off-canvas (drawers translated out of the frame) is not visible
    if (n !== root && (r.right <= rr.left + 0.5 || r.left >= rr.right - 0.5)) continue;
    visibleCount++;
    if (exOf(n)) { excludedCount++; continue; }
    const base = { el: n, sec: secOf(n), sig: sig(n), r: rectOf(n, r), op: r2(op), label: norm(n.innerText || n.textContent).slice(0, 40), ph: phOf(n), abs: (s.position === 'absolute' || s.position === 'fixed') ? 1 : 0 };
    if (n !== root && painted(s)) {
      const rec = Object.assign({ k: 'box', backdrop: isBackdrop(r) }, base, { s: boxStyle(s) });
      recOf.set(n, recs.length); recs.push(rec);
    } else if (n !== root && (s.minHeight !== '0px' && s.minHeight !== 'auto' || s.maxHeight !== 'none') && r.height > 0) {
      // unpainted but height-constrained boxes (min/max sizing — e.g. media frames)
      recs.push(Object.assign({ k: 'frame' }, base, { s: { minh: s.minHeight, maxh: s.maxHeight, minw: s.minWidth, maxw: s.maxWidth } }));
    }
    // glyph runs (own text nodes)
    const tn = [...n.childNodes].filter((c) => c.nodeType === 3 && c.textContent.trim());
    if (tn.length) {
      let L = 1e9, T = 1e9, R = -1e9, B = -1e9; const ys = new Set();
      for (const t of tn) { const rg = document.createRange(); rg.selectNodeContents(t); for (const q of rg.getClientRects()) { if (q.width < 0.5) continue; L = Math.min(L, q.left); T = Math.min(T, q.top); R = Math.max(R, q.right); B = Math.max(B, q.bottom); ys.add(Math.round(q.top)); } }
      if (L < 1e9) {
        const fam = s.fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, '');
        // effective decoration: text-decoration propagates from inline ancestors and the first block container
        const decos = new Set();
        for (let p = n; p && p !== root.parentElement; p = p.parentElement) {
          const ps = p === n ? s : getComputedStyle(p);
          if (ps.textDecorationLine && ps.textDecorationLine !== 'none') ps.textDecorationLine.split(' ').forEach((d) => decos.add(d));
          if (p !== n && ps.display !== 'inline') break;
        }
        recs.push(Object.assign({ k: 'text' }, base, {
          r: rectOf(n, { left: L, top: T, width: R - L, height: B - T }),
          t: norm(tn.map((c) => c.textContent).join(' ')).slice(0, 60),
          trunc: (n.scrollWidth > n.clientWidth + 1 && /(hidden|clip)/.test(s.overflowX)) ? 1 : 0,
          s: { ff: fam, fs: s.fontSize, fw: s.fontWeight, lh: s.lineHeight, ls: s.letterSpacing, fst: s.fontStyle, ta: s.textAlign,
               tt: s.textTransform, td: [...decos].sort().join(' ') || 'none', ws: s.whiteSpace, to: s.textOverflow, c: s.color, tfc: s.webkitTextFillColor, lines: ys.size },
        }));
      }
    }
    // media / icons
    if (base.ph === 2) recs.push(Object.assign({ k: 'media' }, base, { tag: 'slot', s: {} }));
    else if (n.tagName === 'IMG' || n.tagName === 'VIDEO' || n.tagName === 'CANVAS' || n.tagName === 'svg' || n.tagName === 'SVG') {
      const src = n.tagName === 'IMG' ? (n.currentSrc || n.src || '').split('/').pop().split('?')[0].slice(0, 60) : '';
      recs.push(Object.assign({ k: 'media' }, base, { tag: n.tagName.toLowerCase(), s: { src, fit: s.objectFit, fil: s.filter, fill: s.fill, stroke: s.stroke, sw: s.strokeWidth, c: s.color } }));
    }
    for (const pn of ['::before', '::after']) {
      const p = getComputedStyle(n, pn);
      if (p.content && p.content !== 'none' && p.content !== 'normal' && p.display !== 'none') {
        const pw = parseFloat(p.width) || 0, ph = parseFloat(p.height) || 0;
        let pr = null;
        if (p.position === 'absolute' || p.position === 'fixed') {
          const L = parseFloat(p.left), T = parseFloat(p.top), Wd = parseFloat(p.width), Hd = parseFloat(p.height);
          if (!Number.isNaN(L) && !Number.isNaN(T) && !Number.isNaN(Wd) && !Number.isNaN(Hd)) {
            const bl = parseFloat(s.borderLeftWidth) || 0, bt = parseFloat(s.borderTopWidth) || 0;
            const ro = rectOf(n, r); pr = [r2(ro[0] + bl + L), r2(ro[1] + bt + T), r2(Wd), r2(Hd)];
          }
        }
        recs.push(Object.assign({ k: 'pseudo' }, base, { pn, pr, s: { content: p.content.slice(0, 16), ff: p.fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, ''), fs: p.fontSize, w: p.width, h: p.height, c: p.color,
          bg: p.backgroundColor, bgi: p.backgroundImage === 'none' ? 'none' : p.backgroundImage.replace(/url\("?[^")]*\/([^/")]+)"?\)/g, 'url($1)').slice(0, 160),
          bd: borderOf(p), rad: radiusOf(p), sh: p.boxShadow, op: p.opacity, tr: p.transform, pos: p.position, mask: (p.webkitMaskImage || p.maskImage || 'none').slice(0, 80) }, pwh: [r2(pw), r2(ph)] }));
      }
    }
  }
  // container = nearest painted, non-backdrop ancestor box record
  // (text/media/pseudo: the own element counts — a painted button is its label's container;
  //  box/frame: start from the parent)
  for (const rec of recs) {
    let c = -1; const anc = [];
    const start = (rec.k === 'box' || rec.k === 'frame') ? rec.el.parentElement : rec.el;
    for (let p = start; p && p !== root; p = p.parentElement || (p.getRootNode && p.getRootNode().host)) {
      const idx = recOf.get(p);
      if (idx !== undefined && recs[idx] !== rec) { anc.push(idx); if (c < 0 && !recs[idx].backdrop) c = idx; }
    }
    rec.c = c; rec.anc = anc;
  }
  // occlusion: in-viewport primitives whose sample points are all covered by unrelated elements (sheets, dialogs)
  const related = (a, b) => { // a contains b or b contains a (shadow-aware)
    const up = (x) => x.parentElement || (x.getRootNode && x.getRootNode().host) || null;
    for (let p = b; p; p = up(p)) if (p === a) return true;
    for (let p = a; p; p = up(p)) if (p === b) return true;
    return false;
  };
  // only an opaque layer hides what is under it — translucent scrims / blurred glass still show it.
  // A translucent layer with a backdrop blur at least as large as the element makes it «blur-covered»:
  // still visible as a smear, so its differences go to the human-check list, never block.
  const blurOf = (st) => { const m = /blur\(([\d.]+)px\)/.exec(st.backdropFilter || ''); return m ? parseFloat(m[1]) : 0; };
  const blurCover = (hit, el, minSide) => {
    const up = (x) => x.parentElement || (x.getRootNode && x.getRootNode().host) || null;
    for (let p = hit; p && !related(p, el); p = up(p)) { if (blurOf(getComputedStyle(p)) * 2 >= minSide) return true; }
    return false;
  };
  const opaqueCover = (hit, el) => {
    const up = (x) => x.parentElement || (x.getRootNode && x.getRootNode().host) || null;
    for (let p = hit; p && !related(p, el); p = up(p)) {
      const st = getComputedStyle(p);
      if (alphaOf(st.backgroundColor) >= 0.98 && cumOp(p) >= 0.98 && (!st.backdropFilter || st.backdropFilter === 'none')) return true;
    }
    return false;
  };
  let occTests = 0;
  for (const rec of recs) {
    const el = rec.el;
    const vr = rec.k === 'text' ? null : el.getBoundingClientRect();
    const box = rec.k === 'text' ? { left: rec.r[0] + rr.left - scrollOff(el)[0], top: rec.r[1] + rr.top - scrollOff(el)[1], width: rec.r[2], height: rec.r[3] } : vr;
    const pts = [[box.left + box.width / 2, box.top + box.height / 2]];
    if (rec.k === 'box' && box.width > 8 && box.height > 8) pts.push([box.left + 3, box.top + 3], [box.left + box.width - 3, box.top + box.height - 3]);
    const inView = pts.filter(([x, y]) => x >= 0 && y >= 0 && x < innerWidth && y < innerHeight);
    if (!inView.length) continue;
    let covered = 0, blurred = 0;
    for (const [x, y] of inView) {
      occTests++;
      const hit = document.elementFromPoint(x, y);
      if (hit && !related(hit, el) && opaqueCover(hit, el)) covered++;
      else if (hit && !related(hit, el) && blurCover(hit, el, Math.min(box.width, box.height))) blurred++;
      if (performance.now() - t0 > opt.budgetMs) { partial = true; break; }
    }
    if (partial) break;
    if (covered === inView.length) rec.occ = 1;
    else if (covered + blurred === inView.length && blurred > 0) rec.blurocc = 1;
  }
  // fonts actually used by the recorded text: a family whose faces failed, or that cannot render now, is a fallback
  const usedFamilies = [...new Set(recs.filter((r) => r.k === 'text' || (r.k === 'pseudo' && r.s.content && r.s.content !== '""')).map((r) => r.s.ff).filter(Boolean))];
  const fontsFailed = [];
  if (document.fonts) {
    const faces = [...document.fonts];
    for (const fam of usedFamilies) {
      const mine = faces.filter((f) => f.family.replace(/^["']|["']$/g, '') === fam);
      if (!mine.length) continue;                         // system / local family — nothing to load
      const ok = mine.some((f) => f.status === 'loaded');
      const err = mine.length > 0 && mine.every((f) => f.status === 'error');
      if (err || !ok) fontsFailed.push(fam + (err ? ':error' : ':' + mine.map((f) => f.status).join('/')));
    }
    // a face the page asked for and could not get (status error) — even when nothing recorded uses it any more
    // (a failed icon font collapses the icon to 0×0, so the element itself disappears from the census)
    for (const f of faces) if (f.status === 'error') { const n = f.family.replace(/^["']|["']$/g, '') + ':error'; if (!fontsFailed.includes(n)) fontsFailed.push(n); }
  }
  // a stylesheet that never arrived (blocked CDN) leaves no FontFace behind — check the <link> itself
  for (const l of document.querySelectorAll('link[rel~="stylesheet"]')) if (!l.sheet && !l.disabled) fontsFailed.push('stylesheet:' + String(l.href).split('?')[0].slice(0, 80));
  for (const sh of document.styleSheets) {        // @import that never arrived (readable sheets only)
    let rules = null; try { rules = sh.cssRules; } catch (e) { continue; }
    for (const ru of rules) {
      if (ru.type !== 3) continue;
      let ok = false; try { ok = !!(ru.styleSheet && ru.styleSheet.cssRules); } catch (e) { ok = !!ru.styleSheet; } // cross-origin but loaded → ok
      if (!ok) fontsFailed.push('import:' + String(ru.href).split('?')[0].slice(0, 80));
    }
  }
  // elements animated forever (spinners, shimmer): their animated properties are not comparable values
  const infTargets = new Set();
  if (document.getAnimations) for (const a of document.getAnimations()) {
    if (a.playState === 'running' && a.effect && a.effect.getComputedTiming().iterations === Infinity && a.effect.target) infTargets.add(a.effect.target);
  }
  for (const rec of recs) if (infTargets.has(rec.el)) rec.inf = 1;
  const vocab = { tags: new Set(), classes: new Set(), ids: new Set(), attrs: new Set() };
  for (const n of all) { vocab.tags.add(n.localName); if (n.id) vocab.ids.add(n.id); for (const c of n.classList || []) vocab.classes.add(c); for (const a of n.attributes || []) if (a.name !== 'class' && a.name !== 'id' && a.name !== 'style') vocab.attrs.add(a.name); }
  const meta = {
    census_version: 4, root_matched: opt.root ? 1 : 'body', route_set: opt.routeSet || null,
    // V5: what the page actually loaded from the vendor area, and which SDK globals exist — cross-checked against route_set
    vendor: (performance.getEntriesByType ? performance.getEntriesByType('resource') : []).filter((e) => /\/static\/vendor\//.test(e.name)).map((e) => ({ path: new URL(e.name).pathname, status: e.responseStatus === undefined ? null : e.responseStatus })),
    sdk_globals: Object.fromEntries((opt.sdkGlobals || []).map((g) => [g, typeof window[g] !== 'undefined'])),
    vocab: { tags: [...vocab.tags].sort(), classes: [...vocab.classes].sort(), ids: [...vocab.ids].sort(), attrs: [...vocab.attrs].sort() }, partial, budget_ms: opt.budgetMs, fonts_used: usedFamilies, fonts_failed: fontsFailed, url: location.origin + location.pathname, viewport: [innerWidth, innerHeight], dpr: devicePixelRatio,
    root: opt.root, root_rect: [r2(rr.left), r2(rr.top), r2(rr.width), r2(rr.height)],
    sections: heads.map((h) => norm(h.textContent).slice(0, 40)),
    fonts: document.fonts ? document.fonts.status : 'n/a',
    running_animations: (document.getAnimations ? document.getAnimations().filter((a) => a.playState === 'running' && a.effect && a.effect.getComputedTiming().iterations !== Infinity).length : -1),
    infinite_animations: (document.getAnimations ? document.getAnimations().filter((a) => a.playState === 'running' && a.effect && a.effect.getComputedTiming().iterations === Infinity).length : -1),
    elements_total: all.length, elements_visible: visibleCount, records_total: recs.length, occluded: recs.filter((r) => r.occ).length, excluded_elements: excludedCount, exclude: opt.exclude, occlusion_tests: occTests,
    page: opt.page, page_size: opt.pageSize, pages: Math.max(1, Math.ceil(recs.length / opt.pageSize)),
  };
  const slice = recs.slice(opt.page * opt.pageSize, (opt.page + 1) * opt.pageSize).map((rec, j) => {
    const o = Object.assign({}, rec); delete o.el; o.i = opt.page * opt.pageSize + j; return o;
  });
  meta.elapsed_ms = Math.round(performance.now() - t0);
  return { meta, records: slice };
}
