// 설계 §2 판정 규칙 프로토타입 — 포커스를 주지 않고 링 절단을 판정한다.
(() => {
  'use strict';
  const FOCUSABLE = 'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"]), [contenteditable]';
  const rootCS = getComputedStyle(document.documentElement);

  // var() 해소 (깊이 제한)
  const resolveVars = (v, d = 0) => {
    if (d > 6 || !v.includes('var(')) return v;
    return resolveVars(v.replace(/var\(\s*(--[\w-]+)\s*(?:,([^()]*))?\)/g,
      (_, name, fb) => (rootCS.getPropertyValue(name) || fb || '').trim()), d + 1);
  };
  // 괄호 깊이를 고려한 콤마 분리
  const splitTop = (s) => {
    const out = []; let d = 0, cur = '';
    for (const ch of s) {
      if (ch === '(') d++; else if (ch === ')') d--;
      if (ch === ',' && d === 0) { out.push(cur); cur = ''; } else cur += ch;
    }
    if (cur.trim()) out.push(cur);
    return out.map((x) => x.trim()).filter(Boolean);
  };
  // 한 그림자의 바깥 확장 (inset 은 null)
  const outerExtent = (sh) => {
    if (/^inset\b/.test(sh)) return null;
    // 색 함수(rgba/rgb/hsl/color-mix…)와 #hex 를 먼저 제거해야 그 안의 숫자가 길이로 오인되지 않는다.
    const bare = sh.replace(/[a-z-]+\([^()]*(?:\([^()]*\)[^()]*)*\)/gi, ' ').replace(/#[0-9a-f]{3,8}/gi, ' ');
    // 길이는 순서대로 offset-x offset-y [blur] [spread] — 단위 없는 0 도 길이다.
    const lens = [...bare.matchAll(/(-?[\d.]+)(px|rem|em)?/g)]
      .map((m) => (m[2] === 'rem' || m[2] === 'em') ? parseFloat(m[1]) * 16 : parseFloat(m[1]))
      .filter((n) => !Number.isNaN(n));
    const [ox = 0, oy = 0, blur = 0, spread = 0] = lens;
    const e = { l: blur + spread - ox, r: blur + spread + ox, t: blur + spread - oy, b: blur + spread + oy };
    return (e.l > 0 || e.r > 0 || e.t > 0 || e.b > 0) ? e : null;
  };
  const maxExtent = (a, b) => a ? { l: Math.max(a.l, b.l), r: Math.max(a.r, b.r), t: Math.max(a.t, b.t), b: Math.max(a.b, b.b) } : b;

  // ── 1. CSSOM 에서 «바깥 box-shadow 를 붙이는 포커스 규칙» 수확
  const rules = [];
  const blind = [];
  const walk = (sheet) => {
    let list; try { list = sheet.cssRules; } catch (e) { blind.push(sheet.href || '(inline)'); return; }
    for (const r of list) {
      // CSS Nesting 이후 CSSStyleRule 도 cssRules 를 갖는다(길이 0) — selectorText 를 먼저 본다.
      if (r.selectorText === undefined) { if (r.cssRules) walk(r); continue; }
      if (r.cssRules && r.cssRules.length) walk(r);
      if (!/:focus/.test(r.selectorText)) continue;
      const bs = r.style && r.style.getPropertyValue('box-shadow');
      if (!bs) continue;
      let ext = null;
      for (const sh of splitTop(resolveVars(bs))) { const e = outerExtent(sh); if (e) ext = maxExtent(ext, e); }
      if (ext) rules.push({ selector: r.selectorText, raw: bs.trim(), ext });
    }
  };
  for (const s of document.styleSheets) walk(s);

  // ── 2. 기반 셀렉터 → 링을 지는 후보 요소
  // 전역 규칙(`:focus-visible` 단독)은 기반 셀렉터가 빈 문자열이 된다 — 버리면 후보 0 이 되므로 남긴다.
  const stripFocus = (sel) => sel.split(',').map((s) => s.trim()
    .replace(/:focus-within|:focus-visible|:focus/g, '')).map((s) => s.trim());
  const cand = new Map(); // el -> {ext, via[]}
  for (const r of rules) {
    for (const base of stripFocus(r.selector)) {
      let els;
      const isGlobal = base === '' || base === '*';
      try { els = isGlobal ? document.querySelectorAll(FOCUSABLE) : document.querySelectorAll(base); }
      catch (e) { blind.push('bad-selector:' + base); continue; }
      for (const el of els) {
        const prev = cand.get(el);
        cand.set(el, { ext: prev ? maxExtent(prev.ext, r.ext) : r.ext, via: (prev ? prev.via : []).concat(r.selector) });
      }
    }
  }

  // ── 3. 기하 판정
  const pathOf = (el) => { const p = []; for (let e = el; e && e.tagName !== 'HTML'; e = e.parentElement) { p.unshift(e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).join('.') : '')); } return p.slice(-3).join(' > '); };
  const findings = [];
  let checked = 0;
  for (const [el, info] of cand) {
    const er = el.getBoundingClientRect();
    if (er.width < 1 && er.height < 1) continue;
    let anc = null;
    for (let a = el.parentElement; a; a = a.parentElement) {
      const cs = getComputedStyle(a);
      if (cs.overflowX !== 'visible' || cs.overflowY !== 'visible') { anc = { el: a, cs }; break; }
    }
    if (!anc) continue;
    checked++;
    const { el: A, cs } = anc, ar = A.getBoundingClientRect();
    const pb = { l: ar.left + parseFloat(cs.borderLeftWidth), r: ar.right - parseFloat(cs.borderRightWidth),
                 t: ar.top + parseFloat(cs.borderTopWidth),  b: ar.bottom - parseFloat(cs.borderBottomWidth) };
    const hardX = A.scrollWidth <= A.clientWidth + 1;
    const hardY = A.scrollHeight <= A.clientHeight + 1;
    const clear = { l: er.left - pb.l, r: pb.r - er.right, t: er.top - pb.t, b: pb.b - er.bottom };
    const bad = [];
    if (hardX) { if (clear.l < info.ext.l) bad.push(['left', clear.l, info.ext.l]); if (clear.r < info.ext.r) bad.push(['right', clear.r, info.ext.r]); }
    if (hardY) { if (clear.t < info.ext.t) bad.push(['top', clear.t, info.ext.t]); if (clear.b < info.ext.b) bad.push(['bottom', clear.b, info.ext.b]); }
    if (bad.length) findings.push({ el: pathOf(el), ancestor: pathOf(A), hardX, hardY,
        sides: bad.map(([s, c, e]) => `${s} 여유 ${c.toFixed(1)}px < 확장 ${e}px`), via: info.via[0] });
  }
  return { rules: rules.map((r) => r.selector + ' → ' + JSON.stringify(r.ext)), candidates: cand.size,
           withClippingAncestor: checked, findings, blind };
})()
