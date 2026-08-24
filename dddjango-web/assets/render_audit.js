/* render_audit — 렌더 실측 스니펫 (dddjango-web · 사용자 브라우저 콘솔용 관찰 도구).
 *
 * 대상 페이지(목표 원본 또는 runserver 구현)의 DevTools 콘솔에 전문을 붙여넣어
 * 실행한다 — 산출물 코드가 아니다: web/ 트리에 반입 금지(D12v2), 산출 JSON은
 * 산출물 폴더에 동결한다(render-audit.json / render-audit-impl.json).
 * 첫 붙여넣기에 브라우저가 "allow pasting" 타이핑을 요구할 수 있다.
 *
 * 수집: 뷰포트 · 앱 컬럼 후보 · 텍스트 리프 실측(크기/웨이트/행간/정렬/색/rect)
 *      · 고정(pinned) 요소 — 내부 2점(1/3·2/3) 스크롤 샘플링으로 rect 불변 판별.
 * 출력: JSON을 클립보드(copy)와 console.log 양쪽으로 — 대조는
 *      scripts/compare_render_audit.py가 결정론 수행한다(스키마 audit_version 1).
 */
(() => {
  'use strict';
  const AUDIT_VERSION = 1;
  const TEXT_CAP = 200;
  const PINNED_CAP = 20;

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
      pinned.sort((a, b) => a.rect.y - b.rect.y || a.rect.x - b.rect.x || (a.key < b.key ? -1 : 1));
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
  try { if (typeof copy === 'function') copy(json); } catch (e) { /* copy는 DevTools 전용 */ }
  console.log(json);
  return `[render-audit] texts ${out.texts.length}건 · pinned ${out.pinned.length}건 · scroll=${out.scroll.mode}` +
    (out.partial ? ' · PARTIAL(오류 발생 — error 필드 확인)' : '') +
    ' — JSON은 클립보드(copy)와 위 로그에 있습니다. 파일로 저장해 산출물 폴더에 동결하세요.';
})();
