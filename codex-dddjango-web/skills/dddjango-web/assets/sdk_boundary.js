// dddjango-web 공식 SDK 경계 가로채기 스니펫 — G2 «공식 SDK 경계 확인» 전용(제품 코드가 아니다 · web/ 에 두지 않는다).
// 브라우저 도구가 페이지를 불러온 뒤 `(<이 파일 본문>)(cfg)` 로 평가한다. case 마다 새로 불러온 뒤 다시 설치하고,
// 클릭 전에 window.__dddjangoSdkBoundary.installed === true 와 path 표지(init-wrapped · patched:<함수>)를 확인한다.
// cfg = { global, init, namespaces: [승인 이름공간], members: {이름공간: {함수: call|lifecycle|data_out|gateway|sdk_ui}},
//         named: ['<이름공간>.<data_out 함수>'…], gatewayPaths: {'<이름공간>.<함수>': [승인 경로…]},
//         apiPaths: {'<이름공간>.<함수>': [api-paths 전부…]}(선택), operatorDomains: [운영자 도메인…] }
// 승인 이름공간의 함수를 분류표대로 바꾼다 — 수명 함수(lifecycle · 표에 없어도 이름이 수명 꼴이면)는 원본 그대로, 그 밖은
// 기록기(원 함수를 부르지 않는다). 운영자 대상 window.open·폼 제출은 보내지 않고 기록만 한다. gateway url 은 백스톱 WV9 와
// 같은 정규형(아래 normPath — 운영자 https 호스트 점 경계 → 경로만 · 쿼리·조각 제거 · 비예약 퍼센트 해제 · 끝 `/` 제거 ·
// 공백·역슬래시·빈 조각·점 조각 거절 · 소문자)으로 대조한다.
(cfg) => {
  const LIFE = ['cleanup', 'destroy', 'dispose', 'teardown'];
  const st = window.__dddjangoSdkBoundary = {
    installed: false, path: [], calls: [], opens: [], forms: [], thisOk: [], members: {}, unlisted: [], real: {},
  };
  const underOp = (host) => cfg.operatorDomains.some((d) => host === d || host.endsWith('.' + d));
  const isOp = (u) => {
    try { return underOp(new URL(String(u), location.href).hostname.toLowerCase()); } catch (e) { return false; }
  };
  // gateway url 정규형 — 백스톱 normalize_gateway_url 과 글자 단위로 같은 규칙(URL 파서의 해석 차이에 기대지 않는다):
  // 출력 가능한 ASCII·역슬래시 없음 → 스킴/`//` 면 `https://<운영자 호스트>` 만 · 아니면 `/` 로 시작 → 쿼리·조각 제거 →
  // `%XX` 는 비예약 문자로 풀리는 것만 → 끝 `/` 제거 · 빈 조각·`.`·`..` 거절 → 소문자. 거절은 null(승인 밖).
  const normPath = (u) => {
    if (typeof u !== 'string' || !u) return null;
    for (const c of u) { if (c < '!' || c > '~' || c === '\\') return null; }
    let rest = u;
    if (/^[A-Za-z][A-Za-z0-9+.\-]*:/.test(u) || u.startsWith('//')) {
      if (u.slice(0, 8).toLowerCase() !== 'https://') return null;
      const after = u.slice(8);
      let cut = after.length;
      for (const ch of '/?#') { const k = after.indexOf(ch); if (k >= 0) cut = Math.min(cut, k); }
      const host = after.slice(0, cut).toLowerCase();
      if (!/^[a-z0-9.\-]+$/.test(host) || !underOp(host)) return null;
      rest = after.slice(cut);
      if (!rest.startsWith('/')) rest = '/' + rest;
    } else if (!u.startsWith('/')) return null;
    let p = rest.split(/[?#]/, 1)[0];
    if (/%(?![0-9A-Fa-f]{2})/.test(p)) return null;
    let bad = false;
    p = p.replace(/%([0-9A-Fa-f]{2})/g, (m, h) => {
      const c = String.fromCharCode(parseInt(h, 16));
      if (!/^[A-Za-z0-9\-._~]$/.test(c)) bad = true;
      return c;
    });
    if (bad) return null;
    p = p.replace(/\/+$/, '');
    if (p.split('/').slice(1).some((s) => s === '' || s === '.' || s === '..')) return null;
    return (p || '/').toLowerCase();
  };
  // 운영자 대상 바깥 출구 — 기록 전용
  const open0 = window.open;
  window.open = function (u, n, f) {
    if (isOp(u)) { st.opens.push([String(u), n]); return null; }
    return open0.apply(this, arguments);
  };
  const P = HTMLFormElement.prototype;
  const sub0 = P.submit;
  const req0 = P.requestSubmit;
  const rec = (form) => {
    st.forms.push({ action: form.action, target: form.target, method: form.method,
      fields: [...form.elements].map((e) => e.name) });
  };
  P.submit = function () { if (isOp(this.action)) { rec(this); return; } return sub0.apply(this, arguments); };
  P.requestSubmit = function () { if (isOp(this.action)) { rec(this); return; } return req0.apply(this, arguments); };
  document.addEventListener('submit', (e) => { if (isOp(e.target.action)) { rec(e.target); e.preventDefault(); } }, true);
  const g = window[cfg.global];
  if (!g) { st.reason = 'global 없음'; return { installed: false, path: st.path, reason: st.reason }; }
  // 사용자 파일·바이너리 인자(깊이 4) — data_out 분류의 실행 짝
  const fileLike = (v, d) => {
    if (v == null || d > 4) return false;
    if ((typeof File !== 'undefined' && v instanceof File) || (typeof Blob !== 'undefined' && v instanceof Blob)
        || (typeof FileList !== 'undefined' && v instanceof FileList)
        || (typeof FormData !== 'undefined' && v instanceof FormData)
        || v instanceof ArrayBuffer || ArrayBuffer.isView(v) || (v instanceof HTMLInputElement && v.type === 'file')) return true;
    if (typeof v === 'object') { for (const k of Object.keys(v)) { if (fileLike(v[k], d + 1)) return true; } }
    return false;
  };
  const safe = (a) => {
    try { return JSON.parse(JSON.stringify(a, (k, v) => (fileLike(v, 4) ? '[file-like]' : v))); } catch (e) { return '[unserializable]'; }
  };
  const recorder = (name, cls) => function () {
    const args = [...arguments];
    const url = cls === 'gateway' && args[0] && typeof args[0].url === 'string' ? args[0].url : null;
    const path = cls === 'gateway' ? normPath(url) : null;
    const allowed = ((cfg.gatewayPaths && cfg.gatewayPaths[name]) || []).map(normPath);
    const known = cfg.apiPaths && cfg.apiPaths[name] ? cfg.apiPaths[name].map(normPath) : null;
    st.calls.push({ call: name, cls, arg: safe(args[0]), fileArg: args.some((a) => fileLike(a, 0)),
      url, path, pathOk: cls === 'gateway' ? (path !== null && allowed.includes(path)) : null,
      pathKnown: cls === 'gateway' && known ? known.includes(path) : null,
      active: !!(navigator.userActivation && navigator.userActivation.isActive) });
  };
  const patch = (obj) => {
    for (const ns of cfg.namespaces) {
      if (!obj || !obj[ns]) continue;
      const table = (cfg.members && cfg.members[ns]) || {};
      st.members[ns] = Object.keys(obj[ns]).filter((k) => typeof obj[ns][k] === 'function').sort();
      for (const fn of st.members[ns]) {
        const c = ns + '.' + fn;
        const cls = table[fn];
        if (!cls && !st.unlisted.includes(c)) st.unlisted.push(c);           // 표에 없는 함수 — 발견
        if (cls === 'lifecycle' || (!cls && LIFE.includes(fn))) {             // 수명 함수 — 원본 그대로(모든 이름공간)
          if (!st.path.includes('pass:' + c)) st.path.push('pass:' + c);
          continue;
        }
        if (st.real[c] && obj[ns][fn].__dddjangoRecorder) continue;
        st.real[c] = obj[ns][fn];
        const r = recorder(c, cls || 'unlisted');
        r.__dddjangoRecorder = true;
        obj[ns][fn] = r;
        if (!st.path.includes('patched:' + c)) st.path.push('patched:' + c);
      }
    }
  };
  const init0 = g[cfg.init];
  g[cfg.init] = function () { st.thisOk.push(this === g); const r = init0.apply(this, arguments); patch(this); return r; };
  st.path.push('init-wrapped');
  if (typeof g.isInitialized === 'function' && g.isInitialized()) patch(g);
  // 기록에서 발견을 센다(Coordinator 가 captures/sdk-<id>-<case>.json 에 그대로 둔다)
  st.findings = () => {
    const out = st.unlisted.map((c) => '표에 없는 함수 ' + c);
    for (const c of st.calls) {
      if (c.cls === 'sdk_ui') out.push('SDK 가 그리는 UI 호출 ' + c.call);
      if (c.cls === 'data_out' && !(cfg.named || []).includes(c.call)) out.push('이름 지정 원소 없는 data_out 호출 ' + c.call);
      if (c.fileArg && c.cls !== 'data_out') out.push('파일 인자인데 분류가 data_out 이 아니다 ' + c.call);
      if (c.cls === 'gateway' && !c.pathOk) out.push('gateway 경로가 승인 밖 ' + c.call + ' ' + c.url);
      if (c.cls === 'unlisted') out.push('표에 없는 함수 호출 ' + c.call);
    }
    return out;
  };
  st.installed = true;
  return { installed: st.installed, path: st.path };
}
