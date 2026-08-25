/* render_audit — 렌더 실측 스니펫 (dddjango-web · 사용자 브라우저 콘솔용 관찰 도구).
 *
 * 대상 페이지(목표 원본 또는 runserver 구현)의 DevTools 콘솔에 전문을 붙여넣어
 * 실행한다 — 산출물 코드가 아니다: web/ 트리에 반입 금지(D12v2), 산출 JSON은
 * 산출물 폴더에 동결한다(render-audit.json / render-audit-impl.json).
 * 첫 붙여넣기에 브라우저가 "allow pasting" 타이핑을 요구할 수 있다.
 *
 * 수집: 뷰포트 · 앱 컬럼 후보 · 텍스트 리프 실측(크기/웨이트/행간/정렬/색/rect)
 *      · 고정(pinned) 요소 — 내부 2점(1/3·2/3) 스크롤 샘플링으로 rect 불변 판별
 *      · 모션 인벤토리(v2) — computed transition·CSSOM 규칙(@keyframes·transition·
 *        :hover/:focus·@import 1단 하강)·시트 접근/측정 밖 엔진 자기 신고.
 *        전부 동기·결정적(정적 페이지 기준 — 스크롤 샘플링이 lazy-load·리스너를
 *        발화시키는 동적 페이지는 실행이 상태를 바꿀 수 있다) — 런타임 애니메이션
 *        표본(getAnimations 류)은 채택하지 않는다(비결정·IO 리빌은 동기 실행 중
 *        발화 전이라 관찰 불가 — 계획 2026-08-25 §3).
 * 출력: JSON을 클립보드(copy)·console.log·window.__renderAudit 세 곳으로 —
 *      대행 실행(세션 도구)은 실행 후 JSON.stringify(window.__renderAudit)를
 *      도구의 평가 채널로 회수한다. 대조는 scripts/compare_render_audit.py가
 *      결정론 수행한다(스키마 audit_version 2 · v1 하위 호환은 대조기 소관).
 */
(() => {
  'use strict';
  const AUDIT_VERSION = 2;
  const TEXT_CAP = 200;
  const PINNED_CAP = 20;
  const MOTION_CAPS = { transitions: 100, transitionRules: 100, animationRules: 50,
                        keyframes: 50, hoverSelectors: 100, focusSelectors: 100 };

  const norm = (s) =>
    s.normalize('NFC').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
  // 조인 키: 콤마 제거 + 숫자 런 → '#' 접기 (실시간 카운터 «2,380명» 류의 변동 흡수)
  const keyOf = (s) =>
    norm(s).replace(/(\d),(?=\d)/g, '$1').replace(/\d+/g, '#').slice(0, 40);

  const rectOf = (el) => {
    const r = el.getBoundingClientRect();
    return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) };
  };
  const visible = (el, r) =>
    r.w >= 1 && r.h >= 1 && getComputedStyle(el).visibility !== 'hidden';

  // 유효 웨이트: 웨이트 내장 패밀리(_700·_700Bold 류 — RN-web 관례) 우선, 아니면 computed
  const effWeight = (family, weight) => {
    const m = /_([1-9]00)(?![0-9])/.exec(family);
    if (m) return parseInt(m[1], 10);
    const w = parseInt(weight, 10);
    return Number.isNaN(w) ? String(weight) : w;
  };
  const firstFamily = (family) => family.split(',')[0].trim().replace(/^["']|["']$/g, '');

  const out = {
    audit_version: AUDIT_VERSION,
    url: location.origin + location.pathname,
    viewport: { w: innerWidth, h: innerHeight },
    column: null,
    scroll: { mode: 'none', height: 0 },
    texts: [],
    textsTruncated: false,
    pinned: [],
    pinnedTruncated: false,
    partial: false,
    // 골격 선대입 — 모션 블록 이전 단계에서 예외(partial)여도 v2 스키마가 성립한다
    motion: { transitions: [], transitionRules: [], keyframes: [], animationRules: [],
              hoverSelectors: [], focusSelectors: [],
              sheets: { total: 0, readable: 0, blocked: [] },
              blind_spots: [], caps_hit: [] },
  };

  const all = [...document.querySelectorAll('body *')];

  // 앱 컬럼 후보: 중앙 정렬·뷰포트보다 좁고 세로로 긴 컨테이너 중 최소 폭
  {
    let best = null;
    for (const el of all) {
      const r = el.getBoundingClientRect();
      if (r.width < 280 || r.width > innerWidth * 0.9) continue;
      if (r.height < innerHeight * 0.7) continue;
      if (Math.abs(r.x + r.width / 2 - innerWidth / 2) > 8) continue;
      if (!best || r.width < best.width) best = { width: Math.round(r.width), x: Math.round(r.x) };
    }
    out.column = best || { width: innerWidth, x: 0 };
  }

  // 스크롤 컨텍스트 판정 (문서 우선 → 자격 있는 내부 스크롤러)
  const doc = document.scrollingElement || document.documentElement;
  const docMax = doc.scrollHeight - innerHeight;
  let scroller = null; // null = 문서 스크롤
  let maxScroll = docMax;
  if (docMax <= 100) {
    // 자격 있는 내부 스크롤러: 가시 + overflow-y auto|scroll + 실스크롤 여지 최대
    let bestDelta = 200;
    for (const el of all) {
      const cs = getComputedStyle(el);
      if (cs.overflowY !== 'auto' && cs.overflowY !== 'scroll') continue;
      const delta = el.scrollHeight - el.clientHeight;
      const r = el.getBoundingClientRect();
      if (delta > bestDelta && visible(el, rectOf(el)) && r.height > 100) {
        bestDelta = delta; scroller = el; maxScroll = delta;
      }
    }
  }
  out.scroll = {
    mode: docMax > 100 ? 'document' : scroller ? 'inner' : 'none',
    height: Math.round(docMax > 100 ? doc.scrollHeight : scroller ? scroller.scrollHeight : doc.scrollHeight),
  };

  // 스크롤 접근자 — 주체(문서/내부 스크롤러) 공용
  const getTop = () => (scroller ? scroller.scrollTop : (window.scrollY || doc.scrollTop));
  const setTop = (v) => {
    // behavior:'instant' — CSS scroll-behavior:smooth를 무시하고 동기 이동
    if (scroller) scroller.scrollTo({ top: v, behavior: 'instant' });
    else window.scrollTo({ top: v, left: 0, behavior: 'instant' });
  };

  // 실측 전체를 스크롤 원점 기준으로 수행하고 종료 시 복원한다 —
  // 목표/구현 두 실측의 rect 좌표계 통일(실행 시점의 스크롤 위치 무관).
  const scrollable = out.scroll.mode !== 'none';
  const prevTop = scrollable ? getTop() : 0;
  try {
    if (scrollable) setTop(0);

    // 텍스트 리프 실측
    {
      const texts = [];
      for (const el of all) {
        if (el.children.length !== 0) continue;
        const raw = el.textContent || '';
        const t = norm(raw);
        if (t.length < 2) continue;
        const r = rectOf(el);
        if (!visible(el, r)) continue;
        const cs = getComputedStyle(el);
        texts.push({
          key: keyOf(raw),
          text: t.slice(0, 60),
          fontSize: cs.fontSize,
          weight: effWeight(cs.fontFamily, cs.fontWeight),
          lineHeight: cs.lineHeight,
          textAlign: cs.textAlign,
          color: cs.color,
          fontFamily: firstFamily(cs.fontFamily),
          rect: r,
        });
      }
      texts.sort((a, b) =>
        a.key < b.key ? -1 : a.key > b.key ? 1 : a.rect.y - b.rect.y || a.rect.x - b.rect.x);
      if (texts.length > TEXT_CAP) { out.textsTruncated = true; texts.length = TEXT_CAP; }
      out.texts = texts;
    }

    // 모션 인벤토리(v2) — 텍스트 실측과 같은 top-0 단계에서 동기 수집(골격은 선대입됨)
    {
      const m = out.motion;
      const push = (name, item) => {
        if (m[name].length < MOTION_CAPS[name]) m[name].push(item);
        else if (!m.caps_hit.includes(name)) m.caps_hit.push(name);
      };
      // 요소 key: 텍스트 리프면 텍스트 키, 비텍스트는 태그.classList(정렬·최대 3) 시그니처
      const elKey = (el) => {
        const t = norm(el.textContent || '');
        if (el.children.length === 0 && t.length >= 2) return keyOf(el.textContent || '');
        const cls = [...el.classList].sort().slice(0, 3).join('.');
        return el.tagName.toLowerCase() + (cls ? '.' + cls : '');
      };
      // 판별 술어는 duration/delay다 — transition-property의 초기값이 'all'이라 property로는 전 요소가 매치된다
      const hasRealTime = (v) => String(v || '').split(',').some((s) => parseFloat(s) > 0);
      for (const el of all) {
        const r = rectOf(el);
        if (!visible(el, r)) continue;
        const cs = getComputedStyle(el);
        if (hasRealTime(cs.transitionDuration) || hasRealTime(cs.transitionDelay)) {
          push('transitions', { key: elKey(el), property: cs.transitionProperty.slice(0, 120),
                                duration: cs.transitionDuration, easing: cs.transitionTimingFunction.slice(0, 120) });
        }
      }
      // CSSOM 순회 — @keyframes 우선 판별 → @import 1단 하강(실패는 blocked 신고 —
      // curl 동결 경로의 «@import 1단 재귀»와 같은 판형) → 그룹 규칙(@media·@supports·중첩) 재귀
      const walkRules = (rules) => {
        for (const rule of rules) {
          if (rule.type === 7) { push('keyframes', String(rule.name)); continue; } // CSSKeyframesRule
          if (rule.type === 3) { // CSSImportRule — document.styleSheets에 안 담긴다
            try { if (rule.styleSheet) walkRules(rule.styleSheet.cssRules); }
            catch (err) { m.sheets.blocked.push(String(rule.href || '(import)')); }
            continue;
          }
          if (rule.selectorText && rule.style) {
            const st = rule.style;
            const sel = rule.selectorText.slice(0, 120);
            // 실시간 규칙만 — «all 0s» 리셋류가 인벤토리·계수 게이트를 부풀리지 않게
            if (hasRealTime(st.transitionDuration) || hasRealTime(st.transitionDelay))
              push('transitionRules', { selector: sel,
                transition: String(st.transition || [st.transitionProperty, st.transitionDuration, st.transitionTimingFunction].filter(Boolean).join(' ')).slice(0, 120) });
            if (st.animationName && st.animationName !== 'none')
              push('animationRules', { selector: sel,
                animation: String(st.animation || [st.animationName, st.animationDuration].filter(Boolean).join(' ')).slice(0, 120) });
            if (rule.selectorText.includes(':hover')) push('hoverSelectors', sel);
            if (rule.selectorText.includes(':focus')) push('focusSelectors', sel);
          }
          if (rule.cssRules && rule.cssRules.length) walkRules(rule.cssRules);
        }
      };
      const sheets = [...document.styleSheets, ...(document.adoptedStyleSheets || [])];
      m.sheets.total = sheets.length;
      for (const sh of sheets) {
        try { walkRules(sh.cssRules); m.sheets.readable += 1; }
        catch (err) { m.sheets.blocked.push(String((sh && sh.href) || '(inline/adopted)')); }
      }
      // 측정 밖 모션 엔진 자기 신고 — 전역 시그니처 + DOM 흔적(전역 미노출 번들 보완)
      for (const g of ['gsap', 'anime', 'AOS', 'ScrollReveal', 'ScrollMagic', 'Velocity', 'lottie'])
        if (window[g]) m.blind_spots.push('global:' + g);
      for (const sel of ['[data-aos]', '.aos-init', '[data-scroll]', '[data-sr-id]'])
        if (document.querySelector(sel)) m.blind_spots.push('dom:' + sel);
      if (all.some((el) => el.shadowRoot)) m.blind_spots.push('dom:shadow-root'); // shadow 내부는 순회 밖
    }

    // 고정(pinned) 요소 — 2점 스크롤 샘플링
    if (scrollable) {
      const box = scroller
        ? scroller.getBoundingClientRect()
        : { x: 0, y: 0, width: innerWidth, height: innerHeight };
      const overlaps = (r) =>
        r.x < box.x + box.width && r.x + r.w > box.x && r.y < box.y + box.height && r.y + r.h > box.y;
      const isScrollerOrAncestor = (el) => {
        if (!scroller) return el === document.documentElement || el === document.body;
        let p = scroller;
        while (p) { if (p === el) return true; p = p.parentElement; }
        return false;
      };
      // 표본은 내부 2점(1/3·2/3) — 0점 기준이면 중간 진입 sticky-top이 미검출된다.
      // 측정은 scrollTo 직후 같은 task에서 동기 수행 — IO·lazy-load 콜백 개입 차단.
      setTop(maxScroll / 3);
      const s1 = new Map();
      for (const el of all) {
        if (isScrollerOrAncestor(el)) continue;
        const r = rectOf(el);
        if (r.w < 80 || r.h < 24 || !visible(el, r) || !overlaps(r)) continue;
        s1.set(el, r);
      }
      setTop((maxScroll * 2) / 3);
      const pinnedEls = [];
      for (const [el, r1] of s1) {
        const r2 = rectOf(el);
        if (Math.abs(r1.x - r2.x) <= 1 && Math.abs(r1.y - r2.y) <= 1 &&
            Math.abs(r1.w - r2.w) <= 1 && Math.abs(r1.h - r2.h) <= 1 &&
            visible(el, r2)) pinnedEls.push(el);
      }
      // 중첩은 최외곽만 — pinned 조상이 있는 요소는 제외
      const set = new Set(pinnedEls);
      const pinned = [];
      for (const el of pinnedEls) {
        let p = el.parentElement, nested = false;
        while (p) { if (set.has(p)) { nested = true; break; } p = p.parentElement; }
        if (nested) continue;
        const cs = getComputedStyle(el);
        pinned.push({ position: cs.position, rect: s1.get(el), key: keyOf(el.textContent || ''), text: norm(el.textContent || '').slice(0, 60) });
      }
      pinned.sort((a, b) => a.rect.y - b.rect.y || a.rect.x - b.rect.x || (a.key < b.key ? -1 : a.key > b.key ? 1 : 0));
      if (pinned.length > PINNED_CAP) { out.pinnedTruncated = true; pinned.length = PINNED_CAP; }
      out.pinned = pinned;
    }
  } catch (e) {
    out.partial = true;
    out.error = String(e);
  } finally {
    if (scrollable) setTop(prevTop); // 스크롤 복원 (best-effort)
  }

  const json = JSON.stringify(out);
  window.__renderAudit = out; // 대행 실행의 회수 채널 — JSON.stringify(window.__renderAudit)
  try { if (typeof copy === 'function') copy(json); } catch (e) { /* copy는 DevTools 전용 */ }
  console.log(json);
  const mo = out.motion || {};
  return `[render-audit] texts ${out.texts.length}건 · pinned ${out.pinned.length}건 · scroll=${out.scroll.mode}` +
    ` · motion tr ${(mo.transitions || []).length}/kf ${(mo.keyframes || []).length}/hover ${(mo.hoverSelectors || []).length}` +
    ((mo.sheets && mo.sheets.blocked && mo.sheets.blocked.length) ? ` · 차단 시트 ${mo.sheets.blocked.length}` : '') +
    ((mo.blind_spots || []).length ? ` · 측정 밖 엔진 ${mo.blind_spots.length}` : '') +
    (out.partial ? ' · PARTIAL(오류 발생 — error 필드 확인)' : '') +
    ' — JSON은 클립보드(copy)와 위 로그에 있습니다. 파일로 저장해 산출물 폴더에 동결하세요.';
})();
