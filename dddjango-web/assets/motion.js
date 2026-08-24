/* dddjango-web vendored motion runner — 플러그인 판형(수정·확장 금지 — 백스톱이 해시 대조).
 * 단일 기능: [data-motion] 요소가 뷰포트에 들어오면 .motion-in 부여(one-shot).
 * 은닉·전환·감속 선호는 CSS 소유 — html.motion-ready 하위 셀렉터 +
 * prefers-reduced-motion 가드 안에서만 쓴다(implementation-ui §7). */
(function () {
  'use strict';
  if (!('IntersectionObserver' in window) || !('MutationObserver' in window)) { return; }
  document.documentElement.classList.add('motion-ready');
  var io = new IntersectionObserver(function (entries) {
    for (var i = 0; i < entries.length; i++) {
      if (entries[i].isIntersecting) {
        entries[i].target.classList.add('motion-in');
        io.unobserve(entries[i].target);
      }
    }
  }, { threshold: 0.15 });
  function observe(root) {
    if (root.nodeType !== 1 && root.nodeType !== 9) { return; }
    if (root.nodeType === 1 && root.hasAttribute('data-motion') && !root.classList.contains('motion-in')) {
      io.observe(root);
    }
    var els = root.querySelectorAll('[data-motion]:not(.motion-in)');
    for (var i = 0; i < els.length; i++) { io.observe(els[i]); }
  }
  observe(document);
  new MutationObserver(function (muts) {
    for (var i = 0; i < muts.length; i++) {
      var added = muts[i].addedNodes;
      for (var j = 0; j < added.length; j++) { observe(added[j]); }
    }
  }).observe(document.body, { childList: true, subtree: true });
})();
