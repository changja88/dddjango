/* interaction_audit — 조작 상태 감사 순수 함수 (dddjango-web · 페이지 안 스니펫 일부).
 *
 * 이 파일은 값을 쓰지 않는 순수 함수만 담는다(설계 §범위와 소유 표: "열거·identity·
 * context·인벤토리·상태 해시·순수 함수(잔여 계산 JS판). 값은 쓰지 않는다"). DOM 열거·
 * 재생·저장은 observe_interactions.pw.js(드라이버 본체) 소관이며 이 파일이 아니다.
 * UMD: Node는 module.exports, 브라우저는 globalThis.__interactionAudit.
 *
 * 규범: workspace/design/2026-09-13-web-interaction-evidence.md K1(탐색 키·잔여 단위)·
 * K2(대상 열거 중 토글/오버레이/네이티브 select/fill 규칙)·K7(interactions.json 스키마).
 * 아래 각 함수 위 주석은 그 절의 해당 문장을 그대로 인용한다.
 *
 * entries(엔트리) 공용 모양 — stateContext/contextFor/stateHash/surfaceKey가 공유:
 *   { id,                                   // 이미 계산된 identity(12자) — stateHash가 그대로 쓴다
 *     role, name, input_type, owner,        // identity 원본 필드 — surfaceKey가 owner_items_hash
 *     dom_path,                             // 없이 재계산할 때만 쓴다(이름이 빈 대상은 dom_path도
 *                                            // 들어간다 — K1 identity 규칙). 다른 함수는 무시한다.
 *     enabled, occluded,                    // 활성 = enabled && !occluded
 *     checked, face, value_empty, surface,  // K1 "인벤토리 항목"의 관찰 값(없으면 null)
 *     live }                                // role=status/aria-live 서브트리 표식
 * target 공용 모양 — contextFor/requiredActions가 공유: { id, kind, owner, scrim,
 *   value }. `value`는 네이티브 select 옵션(kind:'option', owner의 kind가 'select')
 *   에만 있다(수정 라운드 1 컨트롤러 판정 — targets[id]에 value 문자열을 추가로 허용).
 * doc(interactions.json 문서) 공용 모양 — residual/linkedSurfaces가 공유: K7 스키마 그대로
 * (targets/initial/steps).
 *
 * 이름 규칙(K1 드라이런 결정 D-A): «자기 텍스트» 폴백은 항목형 대상(과 대상 후손이 없는
 * handler)에만 쓴다 — 컨테이너(overlay·menu/listbox/dialog 등 owner 역할 요소·대상 후손을
 * 가진 handler)는 aria-label 계열이 없으면 이름이 비고 dom_path가 identity에 들어간다.
 * 컨테이너 이름이 서브트리 텍스트면 상태마다 identity가 바뀌어 그 안의 대상이 owner
 * 연쇄로 전부 재생성되기 때문이다(A8 드라이런 1차 실측 — «관계» 트리거 38개).
 *
 * 토글형(K1 드라이런 결정 D-H): checkbox·switch, 그리고 **이름이 있고 대상 후손이 없는**
 * (D-A의 «자기 텍스트» 폴백으로 이름이 남는 leaf) handler다. checked가 없으면 surface가 그
 * 상태이며 관찰된 surface마다 click 단위가 필요하다(requiredActions·residual). 이름이 빈
 * handler(컨테이너)와 overlay는 토글형이 아니다 — A8 실측: 디자인 시스템 Checkbox가 role
 * 없는 <label> 핸들러로 렌더돼 «윤달·몰라요»가 1회 click으로 끝났다.
 * **radio는 여기 들지 않는다**: 한 번 고르면 같은 그룹 안에서 되돌릴 수 없어 «before 상태마다
 * 한 번»이 성립하지 않는다 — click 1회(CLICK_ONLY_KINDS)로 둔다.
 *
 * 가림 규칙(K2 드라이런 결정 D-B′): 클릭 지점이 브라우저 창 밖이면 hit-test가 성립하지
 * 않으므로 가림을 «미판정»으로 두고(occluded:false) 활성으로 센다 — 진짜 가림은 창 안
 * 지점으로만 판정하고, 창 밖 대상은 드라이버가 굴려서(scrollIntoView) 다시 판정한다.
 *
 * kind 어휘(고정 — 수정 라운드 1 컨트롤러 판정, Task 2 DOM 층도 이 값만 쓴다):
 * button · link · menuitem · option · tab · radio · checkbox · switch ·
 * input · textarea · select · trigger · overlay · handler · declared.
 */
(function (root, factory) {
  'use strict';
  if (typeof module === 'object' && module && module.exports) {
    module.exports = factory();
  } else {
    root.__interactionAudit = factory();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  // 고정 kind 어휘(수정 라운드 1 컨트롤러 판정 — 구속력 있음). Task 2 DOM 층도
  // 이 값만 쓴다. 아래 각 함수의 kind 버킷(CLICK_ONLY_KINDS 등)은 이 어휘의
  // 부분집합이며, 이 목록 밖 값(예: menuitemcheckbox)은 DOM 층이 이 중 하나로
  // 매핑해야 한다.
  var KINDS = [
    'button', 'link', 'menuitem', 'option', 'tab', 'radio', 'checkbox', 'switch',
    'input', 'textarea', 'select', 'trigger', 'overlay', 'handler', 'declared'
  ];

  // interactions.json의 인벤토리 항목 필드(K7 단일 출처). dom.inventory는 드라이버가
  // 쓸 런타임 값(kind·rect·dom_path)과 identity 원본 4필드(role·name·input_type·
  // owner)를 더 얹어 내므로, 문서에 쓰기 전 이 목록으로
  // 투영하는 것은 드라이버 몫이다(수정 라운드 1 컨트롤러 판정).
  var ENTRY_DOC_FIELDS = [
    'id', 'enabled', 'checked', 'face', 'value_empty', 'surface', 'occluded', 'live'
  ];

  // ---------------------------------------------------------------------
  // sha256 — 동기 순수 JS 구현(외부 의존 0, crypto import 없음). FIPS 180-4.
  // ---------------------------------------------------------------------
  var K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
  ];

  function rotr(x, n) { return (x >>> n) | (x << (32 - n)); }

  function sha256Bytes(bytes) {
    var H = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    var bitLen = bytes.length * 8;
    var withOne = bytes.concat([0x80]);
    while (withOne.length % 64 !== 56) withOne.push(0);
    var hi = Math.floor(bitLen / 0x100000000) >>> 0;
    var lo = bitLen >>> 0;
    var lenBytes = [
      (hi >>> 24) & 0xff, (hi >>> 16) & 0xff, (hi >>> 8) & 0xff, hi & 0xff,
      (lo >>> 24) & 0xff, (lo >>> 16) & 0xff, (lo >>> 8) & 0xff, lo & 0xff
    ];
    var padded = withOne.concat(lenBytes);

    for (var offset = 0; offset < padded.length; offset += 64) {
      var w = new Array(64);
      for (var i = 0; i < 16; i++) {
        w[i] = ((padded[offset + i * 4] << 24) | (padded[offset + i * 4 + 1] << 16) |
                (padded[offset + i * 4 + 2] << 8) | (padded[offset + i * 4 + 3])) >>> 0;
      }
      for (i = 16; i < 64; i++) {
        var s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >>> 3);
        var s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >>> 10);
        w[i] = (w[i - 16] + s0 + w[i - 7] + s1) >>> 0;
      }
      var a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
      for (i = 0; i < 64; i++) {
        var S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
        var ch = (e & f) ^ (~e & g);
        var temp1 = (h + S1 + ch + K[i] + w[i]) >>> 0;
        var S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
        var maj = (a & b) ^ (a & c) ^ (b & c);
        var temp2 = (S0 + maj) >>> 0;
        h = g; g = f; f = e; e = (d + temp1) >>> 0;
        d = c; c = b; b = a; a = (temp1 + temp2) >>> 0;
      }
      H[0] = (H[0] + a) >>> 0; H[1] = (H[1] + b) >>> 0; H[2] = (H[2] + c) >>> 0; H[3] = (H[3] + d) >>> 0;
      H[4] = (H[4] + e) >>> 0; H[5] = (H[5] + f) >>> 0; H[6] = (H[6] + g) >>> 0; H[7] = (H[7] + h) >>> 0;
    }
    var hex = '';
    for (var k = 0; k < 8; k++) hex += ('00000000' + (H[k] >>> 0).toString(16)).slice(-8);
    return hex;
  }

  function utf8Bytes(str) {
    var bytes = [];
    for (var i = 0; i < str.length; i++) {
      var code = str.codePointAt(i);
      if (code > 0xffff) i++; // 서로게이트 쌍 소비(codePointAt이 이미 합쳐 반환)
      if (code < 0x80) {
        bytes.push(code);
      } else if (code < 0x800) {
        bytes.push(0xc0 | (code >> 6), 0x80 | (code & 0x3f));
      } else if (code < 0x10000) {
        bytes.push(0xe0 | (code >> 12), 0x80 | ((code >> 6) & 0x3f), 0x80 | (code & 0x3f));
      } else {
        bytes.push(0xf0 | (code >> 18), 0x80 | ((code >> 12) & 0x3f), 0x80 | ((code >> 6) & 0x3f), 0x80 | (code & 0x3f));
      }
    }
    return bytes;
  }

  function toBytes(input) {
    if (typeof input === 'string') return utf8Bytes(input);
    if (Array.isArray(input)) return input;
    if (input && typeof input.length === 'number') return Array.prototype.slice.call(input);
    return utf8Bytes(String(input));
  }

  function sha256(bytesOrString) {
    return sha256Bytes(toBytes(bytesOrString));
  }

  // ---------------------------------------------------------------------
  // canonical JSON — 객체 키 정렬(배열은 순서 보존). identity·context·상태
  // 해시가 모두 "canonical JSON"을 sha256 입력으로 쓴다(K1).
  // ---------------------------------------------------------------------
  function canonicalize(value) {
    if (value === null || value === undefined) return 'null';
    var t = typeof value;
    if (t === 'number' || t === 'boolean') return JSON.stringify(value);
    if (t === 'string') return JSON.stringify(value);
    if (Array.isArray(value)) return '[' + value.map(canonicalize).join(',') + ']';
    if (t === 'object') {
      var keys = Object.keys(value).sort();
      return '{' + keys.map(function (key) { return JSON.stringify(key) + ':' + canonicalize(value[key]); }).join(',') + '}';
    }
    return JSON.stringify(String(value));
  }

  function hashOf(value) { return sha256(canonicalize(value)); }

  // ---------------------------------------------------------------------
  // normalizeName — "name은 접근성 이름(… NFC·80자)"(K1). NFC·NBSP→공백·
  // 공백 접기·trim 뒤 80자로 자른다.
  // ---------------------------------------------------------------------
  function collapseText(s) {
    var raw = s === null || s === undefined ? '' : String(s);
    return raw.normalize('NFC').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
  }

  function normalizeName(s) {
    return collapseText(s).slice(0, 80);
  }

  // ---------------------------------------------------------------------
  // identityOf — "identity = {role, name, input_type, owner, owner_items_hash}의
  // canonical sha 앞 12자 … 이름이 빈 대상만 dom_path를 identity에 넣는다.
  // 한 인벤토리에서 identity가 충돌하면 그때만 dom_path를 추가한다(순번 접미 없음)."(K1)
  // ---------------------------------------------------------------------
  function identityOf(fields, collisions) {
    fields = fields || {};
    var name = normalizeName(fields.name);
    var obj = {
      role: fields.role || '',
      name: name,
      input_type: fields.input_type || '',
      owner: fields.owner || '',
      owner_items_hash: fields.owner_items_hash || ''
    };
    if (name === '' || collisions === true) {
      obj.dom_path = fields.dom_path || '';
    }
    return hashOf(obj).slice(0, 12);
  }

  // owner_items_hash를 비운 identity(surfaceKey 전용) — 규칙은 identityOf 그대로다.
  // 이름이 빈 대상은 dom_path가 들어간다(K1): 빼면 D-A 이후 이름이 빈 컨테이너들이
  // 같은 role·owner라는 이유로 한 값으로 접혀 서로 다른 오버레이가 한 표면이 된다.
  // 문서에서 다시 계산할 때는 entries를 targets와 id로 조인해 dom_path까지 얹는다(K7).
  function reducedIdentityOf(entry, collisions) {
    return identityOf({
      role: entry.role, name: entry.name, input_type: entry.input_type,
      owner: entry.owner, dom_path: entry.dom_path
    }, collisions);
  }

  function isActive(entry) { return !!entry.enabled && !entry.occluded; }
  function hasValue(v) { return v !== null && v !== undefined; }

  // ---------------------------------------------------------------------
  // stateContext — "state context(상태의 값) = 활성 identity 정렬 목록 · 대상별
  // checked · 토글형의 surface(자기 서브트리 tag·class·텍스트 sha) · 텍스트
  // 입력별 value_empty · select/combobox 트리거별 face(표시 텍스트)."(K1)
  // live:true 항목도 ids에는 포함한다 — 해시 입력 제외는 stateHash/surfaceKey
  // 각자의 규칙이다(K1 인벤토리 항목 절 "live … 열거·실행 의무는 유지").
  // ---------------------------------------------------------------------
  function stateContext(entries) {
    var ids = [];
    var checked = {}, faces = {}, valueEmpty = {}, surfaces = {};
    (entries || []).forEach(function (e) {
      if (!isActive(e)) return;
      ids.push(e.id);
      if (hasValue(e.checked)) checked[e.id] = e.checked;
      if (hasValue(e.face)) faces[e.id] = e.face;
      if (hasValue(e.value_empty)) valueEmpty[e.id] = e.value_empty;
      if (hasValue(e.surface)) surfaces[e.id] = e.surface;
    });
    ids.sort();
    return { ids: ids, checked: checked, faces: faces, valueEmpty: valueEmpty, surfaces: surfaces };
  }

  var TRIGGER_KINDS = { trigger: true, select: true }; // "select/combobox 트리거"(K1) — 네이티브 select도 트리거로 본다
  var MENU_ITEM_KINDS = { menuitem: true, option: true };

  // ---------------------------------------------------------------------
  // contextFor — "context_T는 state context에서 face 성분을 대상 종류에 따라
  // 줄인 것이다: 대상 T가 select/combobox 트리거이면 문서 순서상 T보다 앞에
  // 있는 다른 트리거의 face만 포함(자기 face·뒤 트리거 face 제외 …); T가
  // 메뉴 항목이면 owner 트리거의 face 제외; 그 밖(버튼·입력·토글·오버레이)은
  // face 성분 전체 제외."(K1)
  // ---------------------------------------------------------------------
  function contextFor(entries, target, docOrder) {
    var ctx = stateContext(entries);
    var order = docOrder || [];
    var faces = {};
    if (TRIGGER_KINDS[target.kind]) {
      var selfIdx = order.indexOf(target.id);
      Object.keys(ctx.faces).forEach(function (id) {
        if (id === target.id) return;
        var otherIdx = order.indexOf(id);
        if (selfIdx !== -1 && otherIdx !== -1 && otherIdx < selfIdx) faces[id] = ctx.faces[id];
      });
    } else if (MENU_ITEM_KINDS[target.kind] && target.owner) {
      Object.keys(ctx.faces).forEach(function (id) {
        if (id !== target.owner) faces[id] = ctx.faces[id];
      });
    }
    // 그 밖 kind는 faces를 빈 객체로 둔다(전체 제외).
    var reduced = { ids: ctx.ids, checked: ctx.checked, faces: faces, valueEmpty: ctx.valueEmpty, surfaces: ctx.surfaces };
    return hashOf(reduced).slice(0, 16);
  }

  // ---------------------------------------------------------------------
  // stateHash — "state_hash = 루트 서브트리의 (identity, enabled, checked|surface,
  // value_empty, face) 정렬 목록 + url의 sha. live:true 항목 … 은 열거·실행
  // 의무는 유지하되 해시 … 입력에서만 제외한다."(K3)
  // ---------------------------------------------------------------------
  function stateHash(entries, url) {
    var rows = [];
    (entries || []).forEach(function (e) {
      if (e.live === true) return;
      var checkedOrSurface = hasValue(e.checked) ? e.checked : (hasValue(e.surface) ? e.surface : null);
      rows.push([e.id, !!e.enabled, checkedOrSurface, hasValue(e.value_empty) ? e.value_empty : null,
                 hasValue(e.face) ? e.face : null]);
    });
    rows.sort(function (a, b) {
      var sa = JSON.stringify(a), sb = JSON.stringify(b);
      return sa < sb ? -1 : sa > sb ? 1 : 0;
    });
    return hashOf({ rows: rows, url: url === undefined ? null : url });
  }

  // ---------------------------------------------------------------------
  // surfaceKey — "표면 키 = after 상태의 활성 identity 집합에서 face·checked·
  // value·surface·owner_items_hash를 뺀 canonical sha(같은 메뉴가 열린 상태는
  // 도별 항목이 달라도 한 표면)."(K3) 뺄 것만 뺀 identity 집합을 쓴다 —
  // role/name/input_type/owner에, 이름이 빈 대상이면 dom_path까지(K1 identity 규칙).
  // ---------------------------------------------------------------------
  function surfaceKey(entries) {
    var set = {};
    (entries || []).forEach(function (e) {
      if (!isActive(e)) return;
      if (e.live === true) return;
      set[reducedIdentityOf(e)] = true;
    });
    return hashOf(Object.keys(set).sort());
  }

  function dedupeBy(values) {
    var seen = {}, out = [];
    (values || []).forEach(function (v) {
      var key = JSON.stringify(v === undefined ? null : v);
      if (!seen[key]) { seen[key] = true; out.push(v); }
    });
    return out;
  }

  // kind → 단순 클릭 1회(K2 "핸들러 보유 = 대상"). trigger는 드롭다운/리스트박스를
  // 여는 클릭이 필요하므로 이 표에 포함한다(K1 표의 명시 목록 밖 보강). option은
  // owner kind에 따라 분기해야 하므로 이 버킷에 없다(아래 requiredActions 참고).
  var CLICK_ONLY_KINDS = {
    button: true, link: true, menuitem: true, tab: true,
    radio: true, handler: true, declared: true, trigger: true
  };
  // menuitemcheckbox는 고정 어휘 밖이다 — DOM 층은 그 역할을 'checkbox' kind로 매핑한다.
  // radio는 여기 없다: 선택 뒤 같은 그룹 안에서 되돌릴 수 없어 관찰된 상태마다 click을
  // 요구할 수 없다 — 위 CLICK_ONLY_KINDS의 click 1회가 그 대상의 필요 조작이다.
  var TOGGLE_KINDS = { checkbox: true, switch: true };
  // "토글형 = checkbox·switch, 그리고 이름이 있는(대상 후손이 없는) handler"(K1 잔여
  // 단위 · 드라이런 6차 결정 D-H). 두 조건을 다 본다: D-A로 이름이 남는 handler는 보통
  // leaf지만 aria-label을 단 컨테이너도 이름이 남는다 — 컨테이너의 surface는 서브트리
  // 텍스트라 상태마다 갈려 잔여가 불어난다(D-A가 identity에서 막은 것과 같은 병).
  function isNamedHandler(target, targets) {
    if (target.kind !== 'handler') return false;
    if (typeof target.name !== 'string' || target.name === '') return false;
    return !hasTargetDescendant(target, targets);
  }

  // "대상 후손이 없는" — dom_path가 자기 경로의 진부분 접두인 다른 대상이 없다는 뜻이다
  // (dom_path는 '/'로 이은 자식 경로라 접두 비교가 곧 후손 판정이다). dom_path를 모르는
  // 호출(kind만 주는 단위 시험 등)은 leaf로 본다.
  function hasTargetDescendant(target, targets) {
    var path = target.dom_path;
    if (typeof path !== 'string' || path === '') return false;
    var prefix = path + '/';
    var ids = Object.keys(targets || {});
    for (var i = 0; i < ids.length; i++) {
      if (ids[i] === target.id) continue;
      var other = targets[ids[i]];
      if (other && typeof other.dom_path === 'string' && other.dom_path.indexOf(prefix) === 0) return true;
    }
    return false;
  }
  var TEXT_KINDS = { input: true, textarea: true };

  // ---------------------------------------------------------------------
  // requiredActions — K1 필요 조작 표 + K2 토글/네이티브 select/오버레이 규칙.
  // "오버레이의 click:outside는 스크림형이면 스크림 자기 click과 동치다(한 번만
  // 요구)."(K1) — 수정 라운드 1 컨트롤러 판정: option은 owner의 kind로 분기
  // (owner가 select → {select, option:target.value} 1회·고정 단위; owner가
  // menu/listbox → {click, null} 1회), select 요소 자체는 옵션이 단위를 가지므로
  // 아무 단위도 요구하지 않는다(focus/blur 없음). observedStates는 checkbox·
  // switch와 이름이 있는 handler(D-H)에만 쓴다. owner kind를 알기 위해 targets
  // 맵을 세 번째 인자로 받는다.
  // ---------------------------------------------------------------------
  function requiredActions(target, observedStates, targets) {
    var kind = target.kind;
    var states = dedupeBy(observedStates);
    targets = targets || {};

    // D-H — 이름이 있는 handler는 checkbox/switch와 같은 토글 규칙을 쓴다(관찰된 상태마다
    // click 1단위 · checked가 없으면 surface가 그 상태다). CLICK_ONLY보다 먼저 본다.
    if (isNamedHandler(target, targets)) {
      return states.map(function (s) { return { action: 'click', option: s }; });
    }

    if (CLICK_ONLY_KINDS[kind]) return [{ action: 'click', option: null }];

    if (kind === 'option') {
      var owner = targets[target.owner];
      if (owner && owner.kind === 'select') {
        // 네이티브 select 옵션 — 관측 여부와 무관하게 고정 1단위(수정 라운드 1).
        return [{ action: 'select', option: hasValue(target.value) ? target.value : null }];
      }
      return [{ action: 'click', option: null }]; // owner가 menu/listbox
    }

    if (TOGGLE_KINDS[kind]) {
      return states.map(function (s) { return { action: 'click', option: s }; });
    }

    if (TEXT_KINDS[kind]) {
      return [{ action: 'focus', option: null }, { action: 'fill', option: null }, { action: 'blur', option: null }];
    }

    if (kind === 'select') {
      return []; // 옵션(kind:'option')이 단위를 가진다 — select 요소 자체는 요구 없음
    }

    if (kind === 'overlay') {
      if (target.scrim === true) {
        // click:outside ≡ 자기 click — 별도 outside 단위를 만들지 않는다.
        return [{ action: 'click', option: null }, { action: 'key', option: 'Escape' }];
      }
      return [{ action: 'click', option: 'outside' }, { action: 'key', option: 'Escape' }];
    }

    return []; // 알 수 없는 kind — 방어적 기본값(필요 조작 없음)
  }

  function unitKey(u) { return JSON.stringify([u.target, u.action, hasValue(u.option) ? u.option : null]); }

  // ---------------------------------------------------------------------
  // residual — "잔여 단위(검사기) = (identity, action, option). … 어느 state에서든
  // 활성으로 관찰된 단위는 status: executed step이 1개 이상 있어야 한다.
  // failed·unreachable·unclickable은 세지 않는다."(K1)
  // ---------------------------------------------------------------------
  function residual(doc) {
    var targets = doc.targets || {};
    var inventories = [];
    if (doc.initial && Array.isArray(doc.initial.inventory)) inventories.push(doc.initial.inventory);
    (doc.steps || []).forEach(function (step) {
      if (step.before && Array.isArray(step.before.inventory)) inventories.push(step.before.inventory);
      if (step.after && Array.isArray(step.after.inventory)) inventories.push(step.after.inventory);
    });

    var observedStates = {}; // id -> 관찰된 상태 값 배열(중복 제거 전)
    inventories.forEach(function (inv) {
      inv.forEach(function (e) {
        if (!isActive(e)) return;
        if (!observedStates[e.id]) observedStates[e.id] = [];
        var state = hasValue(e.checked) ? e.checked : (hasValue(e.surface) ? e.surface : (hasValue(e.face) ? e.face : null));
        observedStates[e.id].push(state);
      });
    });

    var required = {};
    function addRequired(id, u) {
      var unit = { target: id, action: u.action, option: hasValue(u.option) ? u.option : null };
      required[unitKey(unit)] = unit;
    }

    // 1) 인벤토리에서 활성 관찰된 대상 — 기존 경로(버튼·체크박스·커스텀 메뉴 항목 등).
    Object.keys(observedStates).forEach(function (id) {
      var target = targets[id];
      if (!target) return; // 대상 정의 없는 id는 계산 불가 — 방어적으로 건너뜀
      requiredActions(target, observedStates[id], targets).forEach(function (u) { addRequired(id, u); });
    });

    // 2) 네이티브 select 옵션 — "한 번도 인벤토리에서 활성으로 관측된 적이 없어도"
    // 요구 단위를 낸다(수정 라운드 1 컨트롤러 판정 — 네이티브 <option>은 일반 DOM
    // 서브트리 관측 대상이 아닐 수 있다). targets 정의만으로 무조건 포함한다.
    Object.keys(targets).forEach(function (id) {
      var target = targets[id];
      if (target.kind !== 'option') return;
      var owner = targets[target.owner];
      if (!owner || owner.kind !== 'select') return;
      requiredActions(target, [], targets).forEach(function (u) { addRequired(id, u); });
    });

    (doc.steps || []).forEach(function (step) {
      if (step.status !== 'executed') return; // failed·unreachable·unclickable은 세지 않는다(K1)
      var unit = { target: step.target, action: step.action, option: hasValue(step.option) ? step.option : null };
      delete required[unitKey(unit)];
    });

    return Object.keys(required).sort().map(function (k) { return required[k]; });
  }

  // ---------------------------------------------------------------------
  // linkedSurfaces — "changes.added ≠ ∅인 step이 만든 표면 키마다 … reached_by
  // … 가 있어야 한다."(K3) 이 함수는 added≠∅ step들의 after.surface_key 집합만 낸다.
  // ---------------------------------------------------------------------
  function linkedSurfaces(doc) {
    var set = new Set();
    (doc.steps || []).forEach(function (step) {
      var added = step.changes && Array.isArray(step.changes.added) ? step.changes.added : [];
      if (added.length > 0 && step.after && hasValue(step.after.surface_key)) {
        set.add(step.after.surface_key);
      }
    });
    return set;
  }

  // =====================================================================
  // dom — DOM 열거층(K2 «대상 열거» · K3 루트·outside_root 규칙). 브라우저 안에서만
  // 동작하며 드라이버(observe_interactions.pw.js)가 page.evaluate로 부르는 동기
  // 함수만 둔다. 반환값은 전부 JSON 직렬화 가능하다. 위 순수 함수는 건드리지 않는다.
  // =====================================================================

  // "의미 컨트롤(button·a[href]·input·select·textarea·summary·[tabindex>=0]·
  // role button/link/menuitem/menuitemcheckbox/menuitemradio/option/checkbox/
  // radio/switch/tab/combobox)은 핸들러와 무관하게 대상이다."(K2)
  var SEMANTIC_ROLES = {
    button: 1, link: 1, menuitem: 1, menuitemcheckbox: 1, menuitemradio: 1,
    option: 1, checkbox: 1, radio: 1, switch: 1, tab: 1, combobox: 1
  };
  // "owner는 가장 가까운 menu/listbox/dialog/alertdialog/radiogroup/select/
  // [role=combobox]/구조 오버레이(K2) 조상의 identity"(K1)
  var OWNER_ROLES = { menu: 1, listbox: 1, dialog: 1, alertdialog: 1, radiogroup: 1, combobox: 1 };
  // "오버레이: role(dialog·alertdialog·menu·listbox·aria-modal) 또는 구조(…)"(K2)
  var OVERLAY_ROLES = { dialog: 1, alertdialog: 1, menu: 1, listbox: 1 };
  var OVERLAY_COVERAGE = 0.8; // "루트 rect의 80% 이상을 덮는"(K2)
  // "CDP DOMDebugger.getEventListeners(click·mousedown·pointerdown·keydown·change·input)"(K2)
  var ACTION_LISTENER_TYPES = { click: 1, mousedown: 1, pointerdown: 1, keydown: 1, change: 1, input: 1 };
  // "발견 조작: mouseenter/mouseover 리스너나 :hover 규칙(render-audit hoverSelectors 매칭)"(K2)
  var HOVER_LISTENER_TYPES = { mouseenter: 1, mouseover: 1 };
  // "React __reactProps$*(onClick·onChange·onKeyDown·onMouseDown·onPointerDown)"(K2)
  var REACT_ACTION_PROPS = ['onClick', 'onChange', 'onKeyDown', 'onMouseDown', 'onPointerDown'];
  var REACT_HOVER_PROPS = ['onMouseEnter', 'onMouseOver'];
  // found_by 채널 표기 순서(K7) — 출력은 늘 이 순서로 정렬한다.
  var CHANNEL_ORDER = ['semantic', 'react_props', 'onclick', 'cdp_listener', 'cursor', 'structure', 'declared'];
  var HANDLER_CHANNELS = { react_props: 1, onclick: 1, cdp_listener: 1 };
  var BUTTON_INPUT_TYPES = { button: 1, submit: 1, reset: 1 };
  // "owner_items_hash는 같은 owner 안 형제 **항목** 이름 목록의 sha"(K1) — 항목 kind만
  // 센다(수정 라운드 1 컨트롤러 판정). 항목이 없는 owner(dialog·구조 오버레이 등)는
  // 빈 목록의 sha이므로, 같은 owner 아래 버튼이 늘고 주는 것이 형제 identity를 흔들지 않는다.
  var ITEM_KINDS = { menuitem: 1, option: 1, radio: 1, checkbox: 1, switch: 1, tab: 1 };
  var ZERO_OFFSET = { x: 0, y: 0 };

  // dom.inventory가 남기는 마지막 열거 상태 — clickPoint/outsidePoint/
  // hoverCandidates/scrollContainers가 이 상태를 읽는다(드라이버는 인벤토리 →
  // 지점 조회 순으로 부른다).
  var lastInventory = null;

  function styleOf(el) { return el.ownerDocument.defaultView.getComputedStyle(el); }
  function tagOf(el) { return el.tagName.toLowerCase(); }
  function attr(el, name) { return el.getAttribute(name); }

  function rectOf(el, offset) {
    var r = el.getBoundingClientRect();
    return { x: r.left + offset.x, y: r.top + offset.y, w: r.width, h: r.height };
  }
  function roundRect(r) {
    return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.w), h: Math.round(r.h) };
  }
  function roundPoint(p) {
    return { x: Math.round(p.x * 100) / 100, y: Math.round(p.y * 100) / 100 };
  }
  function inRect(p, r) {
    return p.x >= r.x && p.x <= r.x + r.w && p.y >= r.y && p.y <= r.y + r.h;
  }
  function coverageOf(r, rootRect) {
    var area = rootRect.w * rootRect.h;
    if (area <= 0) return 0;
    var w = Math.min(r.x + r.w, rootRect.x + rootRect.w) - Math.max(r.x, rootRect.x);
    var h = Math.min(r.y + r.h, rootRect.y + rootRect.h) - Math.max(r.y, rootRect.y);
    return (w > 0 && h > 0) ? (w * h) / area : 0;
  }

  function domSegment(el) {
    var parent = el.parentNode;
    var sibs = parent && parent.children ? parent.children : [];
    var n = 0;
    for (var i = 0; i < sibs.length; i++) {
      if (sibs[i].tagName === el.tagName) { n++; if (sibs[i] === el) break; }
    }
    return tagOf(el) + ':nth-of-type(' + n + ')';
  }
  function childPath(prefix, el) {
    var seg = domSegment(el);
    return prefix ? prefix + '/' + seg : seg;
  }

  function reactPropsOf(el) {
    var keys = Object.keys(el);
    for (var i = 0; i < keys.length; i++) {
      if (keys[i].indexOf('__reactProps$') === 0) return el[keys[i]];
    }
    return null;
  }
  function hasAnyProp(obj, names) {
    for (var i = 0; i < names.length; i++) {
      if (typeof obj[names[i]] === 'function') return true;
    }
    return false;
  }
  // opts.listenerIndexes는 Map 또는 평범한 객체(index → [type])다 — index는
  // markCandidates가 심은 el.__iaIndex다. 표식이 없는 요소(그 사이에 새로 그려진
  // 요소 등)는 매칭을 건너뛴다 — 드라이버는 인벤토리마다 markCandidates를 다시
  // 불러야 한다(수정 라운드 1 발견 ⑨).
  function listenerTypesOf(el, opts) {
    var map = opts && opts.listenerIndexes;
    var idx = el.__iaIndex;
    if (!map || typeof idx !== 'number') return null;
    var types = typeof map.get === 'function' ? (map.get(idx) || map.get(String(idx))) : map[idx];
    return Array.isArray(types) ? types : null;
  }
  function anyTypeIn(types, table) {
    for (var i = 0; i < types.length; i++) {
      if (table[String(types[i]).toLowerCase()]) return true;
    }
    return false;
  }

  function roleOf(el) {
    var explicit = collapseText(attr(el, 'role')).toLowerCase();
    if (explicit) return explicit.split(' ')[0];
    var tag = tagOf(el);
    if (tag === 'button' || tag === 'summary') return 'button';
    if (tag === 'a') return el.hasAttribute('href') ? 'link' : '';
    if (tag === 'select') return 'combobox';
    if (tag === 'option') return 'option';
    if (tag === 'textarea') return 'textbox';
    if (tag === 'input') {
      var type = (attr(el, 'type') || 'text').toLowerCase();
      if (type === 'checkbox') return 'checkbox';
      if (type === 'radio') return 'radio';
      if (BUTTON_INPUT_TYPES[type]) return 'button';
      return 'textbox';
    }
    return '';
  }

  function isSemantic(el, role) {
    var tag = tagOf(el);
    if (tag === 'button' || tag === 'input' || tag === 'select' || tag === 'textarea' ||
        tag === 'summary' || tag === 'option') return true;
    if (tag === 'a' && el.hasAttribute('href')) return true;
    var tabindex = attr(el, 'tabindex');
    if (tabindex !== null && /^-?\d+$/.test(tabindex.trim()) && parseInt(tabindex, 10) >= 0) return true;
    return !!SEMANTIC_ROLES[role];
  }

  // "[role=combobox]과 메뉴를 여는 버튼(aria-haspopup / aria-expanded /
  // menu·listbox를 가리키는 aria-controls)은 트리거"(K1 select/combobox 트리거).
  function isMenuTrigger(el) {
    var haspopup = collapseText(attr(el, 'aria-haspopup')).toLowerCase();
    if (haspopup && haspopup !== 'false') return true;
    if (el.hasAttribute('aria-expanded')) return true;
    var controls = attr(el, 'aria-controls');
    if (controls) {
      var target = el.ownerDocument.getElementById(controls.split(' ')[0]);
      if (target && OVERLAY_ROLES[collapseText(attr(target, 'role')).toLowerCase()]) return true;
    }
    return false;
  }

  // 고정 kind 어휘(KINDS) 밖 값을 내지 않는다.
  function kindOf(el, role, isOverlay, declaredOnly) {
    if (isOverlay) return 'overlay';
    var tag = tagOf(el);
    if (tag === 'select') return 'select';
    if (tag === 'textarea') return 'textarea';
    if (tag === 'option' || role === 'option') return 'option';
    if (role === 'menuitem' || role === 'menuitemradio') return 'menuitem';
    if (role === 'menuitemcheckbox') return 'checkbox';
    if (role === 'tab') return 'tab';
    if (role === 'switch') return 'switch';
    if (tag === 'input') {
      var type = (attr(el, 'type') || 'text').toLowerCase();
      if (type === 'radio') return 'radio';
      if (type === 'checkbox') return 'checkbox';
      if (BUTTON_INPUT_TYPES[type]) return 'button';
      return 'input';
    }
    if (role === 'radio') return 'radio';
    if (role === 'checkbox') return 'checkbox';
    if (role === 'combobox' || isMenuTrigger(el)) return 'trigger';
    if (role === 'link') return 'link';
    if (role === 'button') return 'button';
    return declaredOnly ? 'declared' : 'handler';
  }

  // "컨테이너(구조 오버레이·menu/listbox/dialog 등 owner 역할 요소·다른 대상을 후손으로
  // 가진 handler)는 aria-label/aria-labelledby가 없으면 이름이 빈다"(K1 드라이런 결정 D-A).
  // combobox·select는 여기 없다 — 자기 표시 텍스트가 이름인 항목형 트리거다.
  var CONTAINER_ROLES = { menu: 1, listbox: 1, dialog: 1, alertdialog: 1, radiogroup: 1 };
  function isContainerRec(rec) {
    if (!rec) return false;
    if (rec.kind === 'overlay') return true;
    if (CONTAINER_ROLES[rec.role]) return true;
    return rec.kind === 'handler' && rec.hasTargetDescendant === true;
  }

  // "name은 접근성 이름(aria-label → aria-labelledby → label[for] → 자기 텍스트 →
  // placeholder → title, NFC·80자)"(K1). label[for] 다음에 감싸는 label을 본다.
  // "«자기 텍스트» 폴백은 항목형 대상에만 쓴다"(K1 D-A) — rec를 주면 컨테이너에서 그
  // 폴백만 건너뛴다(placeholder·title은 그대로). 근거: 컨테이너 이름이 서브트리 텍스트면
  // 상태마다 identity가 바뀌어 그 안의 모든 대상이 owner 변동으로 재생성된다(A8 실측).
  // rec 없이 부르면(outside_root 표본) 규범의 전체 폴백 사슬을 그대로 쓴다.
  function accName(el, rec) {
    var doc = el.ownerDocument;
    var label = normalizeName(attr(el, 'aria-label'));
    if (label) return label;
    var labelledby = attr(el, 'aria-labelledby');
    if (labelledby) {
      var texts = labelledby.split(/\s+/).map(function (id) {
        var target = doc.getElementById(id);
        return target ? target.textContent : '';
      });
      var fromIds = normalizeName(texts.join(' '));
      if (fromIds) return fromIds;
    }
    if (el.id) {
      var forLabel = null;
      try { forLabel = doc.querySelector('label[for="' + cssEscape(el.id) + '"]'); } catch (e) { forLabel = null; }
      if (forLabel) {
        var fromFor = normalizeName(forLabel.textContent);
        if (fromFor) return fromFor;
      }
    }
    var wrapping = el.parentElement ? el.parentElement.closest('label') : null;
    if (wrapping) {
      var fromWrap = normalizeName(wrapping.textContent);
      if (fromWrap) return fromWrap;
    }
    if (!isContainerRec(rec)) {
      var own = normalizeName(el.textContent);
      if (own) return own;
    }
    var placeholder = normalizeName(attr(el, 'placeholder'));
    if (placeholder) return placeholder;
    return normalizeName(attr(el, 'title'));
  }
  function cssEscape(value) {
    var view = typeof globalThis !== 'undefined' ? globalThis : null;
    if (view && view.CSS && typeof view.CSS.escape === 'function') return view.CSS.escape(value);
    return String(value).replace(/["\\]/g, '\\$&');
  }

  // "role=status·aria-live 서브트리"(K3) — 열거는 하되 해시 입력에서 빠진다.
  function isLive(el) {
    var node = el;
    while (node && node.nodeType === 1) {
      if (collapseText(attr(node, 'role')).toLowerCase() === 'status') return true;
      var live = collapseText(attr(node, 'aria-live')).toLowerCase();
      if (live && live !== 'off') return true;
      node = node.parentElement;
    }
    return false;
  }

  // "disabled·aria-disabled·inert는 enabled:false로 기록만"(K2)
  function isEnabled(el) {
    if (el.disabled === true) return false;
    if (collapseText(attr(el, 'aria-disabled')).toLowerCase() === 'true') return false;
    return !el.closest('[inert]');
  }

  // ---------------------------------------------------------------------
  // 순회 — 루트 서브트리 ∪ 문서 안 오버레이, same-origin iframe은 contentDocument를
  // 같은 규칙으로 돈다(dom_path 앞에 iframe[n]/, rect는 iframe 위치만큼 이동).
  // "aria-hidden 서브트리 제외"(K2).
  // ---------------------------------------------------------------------
  function walkScope(rootEl) {
    var records = [];
    var byEl = new Map();
    var counters = { iframe: 0 };
    var limits = [];
    visitElement(rootEl, '', { doc: rootEl.ownerDocument, offset: ZERO_OFFSET },
                 records, byEl, counters, limits);
    portalOverlays(rootEl).forEach(function (el, index) {
      visitElement(el, 'overlay[' + index + ']', { doc: el.ownerDocument, offset: ZERO_OFFSET },
                   records, byEl, counters, limits);
    });
    return { records: records, byEl: byEl, limits: limits };
  }

  // 루트 밖(포털)에 붙은 role 오버레이도 열거 범위다(K2 "루트 서브트리 ∪ 문서 안 오버레이").
  function portalOverlays(rootEl) {
    var doc = rootEl.ownerDocument;
    var selector = '[role="dialog"],[role="alertdialog"],[role="menu"],[role="listbox"],[aria-modal="true"]';
    var found = doc.querySelectorAll(selector);
    var out = [];
    for (var i = 0; i < found.length; i++) {
      var el = found[i];
      if (el === rootEl || rootEl.contains(el)) continue;
      var nested = false;
      for (var j = 0; j < out.length; j++) { if (out[j].contains(el)) { nested = true; break; } }
      if (!nested) out.push(el);
    }
    return out;
  }

  // 서브트리를 통째로 끊는 조건은 둘뿐이다 — `aria-hidden="true"`(K2)와 display:none.
  // visibility:hidden·rect 0(0 크기 앵커 래퍼·display:contents 레이아웃)은 그 요소만
  // 대상에서 빼고(rendered:false) 자식은 계속 돈다(수정 라운드 1 발견 ①). 기록은
  // 남기므로 그런 요소도 owner·dom_path 계산에는 그대로 쓰인다.
  function visitElement(el, domPath, ctx, records, byEl, counters, limits) {
    if (attr(el, 'aria-hidden') === 'true') return;
    var style = styleOf(el);
    if (style.display === 'none') return;
    var rect = rectOf(el, ctx.offset);
    var rendered = style.visibility !== 'hidden' && rect.w > 0 && rect.h > 0;

    var rec = {
      el: el, doc: ctx.doc, offset: ctx.offset, domPath: domPath,
      rect: rect, style: style, rendered: rendered
    };
    records.push(rec);
    byEl.set(el, rec);

    var tag = tagOf(el);
    if (tag === 'select') {
      if (!rendered) return;
      // "native select: option은 owner=그 select·action=select인 대상"(K2). 닫힌
      // select의 option에는 rect가 없으므로 entries가 아니라 targets에만 넣는다.
      var options = el.options || [];
      for (var i = 0; i < options.length; i++) {
        var optionRec = {
          el: options[i], doc: ctx.doc, offset: ctx.offset,
          domPath: childPath(domPath, options[i]), rect: null, style: null, nativeOption: true
        };
        records.push(optionRec);
        byEl.set(options[i], optionRec);
      }
      return;
    }
    if (tag === 'iframe') {
      // 프레임 번호는 숨은 프레임도 한 자리를 차지한다 — 가시성이 바뀌어도 형제
      // 프레임의 dom_path(= 이름 없는·충돌한 대상의 identity 성분)가 흔들리지 않는다.
      var index = counters.iframe++;
      // iframe 문서는 부모의 visibility를 물려받지 않는다. 프레임이 그려지지 않으면
      // 안의 대상도 보이지 않으므로 순회하지 않는다(수정 라운드 2 발견).
      if (!rendered) return;
      var sub = null;
      try { sub = el.contentDocument; } catch (e) { sub = null; }
      if (!sub || !sub.body) {
        // cross-origin·접근 불가 프레임을 조용히 버리지 않는다 — 드라이버가
        // discovery_limits에 옮겨 적는다(K2 한계 · 수정 라운드 1 발견 ⑥).
        limits.push({ kind: 'cross-origin-iframe', dom_path: domPath });
        return;
      }
      var frameRect = el.getBoundingClientRect();
      var offset = {
        x: ctx.offset.x + frameRect.left + el.clientLeft,
        y: ctx.offset.y + frameRect.top + el.clientTop
      };
      visitElement(sub.body, 'iframe[' + index + ']', { doc: sub, offset: offset },
                   records, byEl, counters, limits);
      return;
    }
    var children = el.children;
    for (var k = 0; k < children.length; k++) {
      visitElement(children[k], childPath(domPath, children[k]), ctx, records, byEl, counters, limits);
    }
  }

  // ---------------------------------------------------------------------
  // 채널 — "핸들러 보유 = 대상(후손 대상 유무 무관)"(K2). cursor 보조는
  // "CDP가 없을 때만, 자기 computed cursor가 부모와 다른 요소에 한정"(K2).
  // ---------------------------------------------------------------------
  function channelsOf(rec, opts) {
    var el = rec.el;
    var channels = [];
    if (isSemantic(el, rec.role)) channels.push('semantic');
    var props = reactPropsOf(el);
    if (props && hasAnyProp(props, REACT_ACTION_PROPS)) channels.push('react_props');
    if (el.hasAttribute('onclick')) channels.push('onclick');
    var types = listenerTypesOf(el, opts);
    if (types && anyTypeIn(types, ACTION_LISTENER_TYPES)) channels.push('cdp_listener');
    if (opts.capabilities && opts.capabilities.cdp_listeners === false && hasOwnPointerCursor(rec)) {
      channels.push('cursor');
    }
    return channels;
  }
  function hasOwnPointerCursor(rec) {
    if (rec.style.cursor !== 'pointer') return false;
    var parent = rec.el.parentElement;
    return !parent || styleOf(parent).cursor !== 'pointer';
  }
  function hasOwnHandler(channels) {
    for (var i = 0; i < channels.length; i++) {
      if (HANDLER_CHANNELS[channels[i]]) return true;
    }
    return false;
  }
  function sortChannels(channels) {
    return CHANNEL_ORDER.filter(function (name) { return channels.indexOf(name) !== -1; });
  }

  function overlayInfoOf(rec, rootRect) {
    if (OVERLAY_ROLES[rec.role] || attr(rec.el, 'aria-modal') === 'true') {
      return { scrim: coverageOf(rec.rect, rootRect) >= OVERLAY_COVERAGE, channel: 'semantic' };
    }
    var position = rec.style.position;
    if (position !== 'absolute' && position !== 'fixed') return null;
    if (coverageOf(rec.rect, rootRect) < OVERLAY_COVERAGE) return null;
    if (!hasOwnHandler(rec.channels) && !isAboveSiblings(rec.el)) return null;
    return { scrim: true, channel: 'structure' };
  }
  function isAboveSiblings(el) {
    var own = parseInt(styleOf(el).zIndex, 10);
    if (isNaN(own)) return false;
    var sibs = el.parentElement ? el.parentElement.children : [];
    for (var i = 0; i < sibs.length; i++) {
      if (sibs[i] === el) continue;
      var other = parseInt(styleOf(sibs[i]).zIndex, 10);
      if (!isNaN(other) && other >= own) return false;
    }
    return true;
  }

  function isOwnerRec(rec) {
    return tagOf(rec.el) === 'select' || !!OWNER_ROLES[rec.role] || rec.overlay === true;
  }
  function ownerElOf(rec, byEl) {
    var node = rec.el.parentElement;
    while (node) {
      var parentRec = byEl.get(node);
      if (!parentRec) return null; // 범위 밖(루트 위 · iframe 문서 경계)
      if (isOwnerRec(parentRec)) return node;
      node = node.parentElement;
    }
    return null;
  }

  // "한 인벤토리에서 identity가 충돌하면 그때만 dom_path를 추가한다"(K1) —
  // 1차로 전부 계산하고 충돌한 대상만 2차에서 dom_path를 넣어 다시 계산한다.
  function assignIdentities(records, byEl, collisionSet) {
    var memo = new Map();
    function idFor(rec) {
      if (memo.has(rec)) return memo.get(rec);
      memo.set(rec, ''); // 순환 방어
      var ownerRec = rec.ownerEl ? byEl.get(rec.ownerEl) : null;
      var ownerId = ownerRec ? idFor(ownerRec) : '';
      var id = identityOf({
        role: rec.role, name: rec.name, input_type: rec.inputType,
        owner: ownerId, owner_items_hash: rec.itemsHash, dom_path: rec.domPath
      }, !!(collisionSet && collisionSet.has(rec)));
      memo.set(rec, id);
      rec.owner = ownerId;
      rec.id = id;
      return id;
    }
    records.forEach(idFor);
  }
  function collidingRecords(records) {
    var seen = {}, collided = new Set();
    records.forEach(function (rec) {
      if (!rec.isTarget) return;
      if (seen[rec.id]) { collided.add(seen[rec.id]); collided.add(rec); } else { seen[rec.id] = rec; }
    });
    return collided;
  }

  // "클릭 지점: 요소 rect 안에서 후손 대상 rect에 덮이지 않는 점(3×3 격자+모서리).
  // 없으면 status: unclickable"(K2) · "가림: 클릭 지점의 elementFromPoint가 자기
  // 또는 후손이 아니면 occluded:true"(K2).
  function candidatePoints(rect) {
    var fractions = [0.5, 0.25, 0.75];
    var points = [];
    for (var i = 0; i < fractions.length; i++) {
      for (var j = 0; j < fractions.length; j++) {
        points.push({ x: rect.x + rect.w * fractions[j], y: rect.y + rect.h * fractions[i] });
      }
    }
    points.push({ x: rect.x + 1, y: rect.y + 1 });
    points.push({ x: rect.x + rect.w - 1, y: rect.y + 1 });
    points.push({ x: rect.x + 1, y: rect.y + rect.h - 1 });
    points.push({ x: rect.x + rect.w - 1, y: rect.y + rect.h - 1 });
    return points;
  }
  function elementAt(rec, point) {
    return rec.doc.elementFromPoint(point.x - rec.offset.x, point.y - rec.offset.y);
  }
  function hitsSelf(rec, point) {
    var hit = elementAt(rec, point);
    return !!hit && (hit === rec.el || rec.el.contains(hit));
  }
  // 창 밖 지점은 hit-test가 성립하지 않는다(elementFromPoint가 null이다) — 가림을
  // «미판정»으로 두고 활성으로 센다(K2 드라이런 결정 D-B′). 가림은 창 안 지점으로만
  // 판정하며, 드라이버가 조작 직전에 굴려(scrollIntoView) 상태 해시가 같을 때 다시 판정한다.
  function resolveClickPoint(rec, viewport) {
    var free = candidatePoints(rec.rect).filter(function (point) {
      for (var i = 0; i < rec.descendantRects.length; i++) {
        if (inRect(point, rec.descendantRects[i])) return false;
      }
      return true;
    });
    var judged = false; // 창 안에서 실제로 hit-test를 해 본 지점이 있었는가
    for (var i = 0; i < free.length; i++) {
      if (hitsSelf(rec, free[i])) { rec.point = roundPoint(free[i]); rec.occluded = false; return; }
      if (inViewport(free[i], viewport)) judged = true;
    }
    rec.point = free.length ? roundPoint(free[0]) : null;
    rec.occluded = judged;
  }
  // 프레임 안 대상도 rect·지점이 최상위 좌표라(dom_path의 iframe[n]/ 접두와 짝) 같은 창으로 잰다.
  function inViewport(point, viewport) {
    return point.x >= 0 && point.y >= 0 && point.x < viewport.w && point.y < viewport.h;
  }

  function faceOf(rec) {
    if (rec.kind === 'select') {
      var selected = rec.el.selectedIndex >= 0 ? rec.el.options[rec.el.selectedIndex] : null;
      return selected ? normalizeName(selected.textContent) : '';
    }
    if (rec.kind === 'trigger') return normalizeName(rec.el.textContent);
    return null;
  }
  function checkedOf(rec) {
    var el = rec.el;
    if (tagOf(el) === 'input') {
      var type = (attr(el, 'type') || 'text').toLowerCase();
      if (type === 'checkbox' || type === 'radio') return !!el.checked;
    }
    var aria = collapseText(attr(el, 'aria-checked')).toLowerCase();
    if (aria === 'true') return true;
    if (aria === 'false') return false;
    if (aria === 'mixed') return 'mixed';
    return null;
  }
  // "토글: input/aria-checked가 있으면 checked, 없으면 surface를 face로 쓴다"(K2) —
  // surface는 자기와 모든 후손 요소의 [tag, class, style] 서명 목록(문서 순서) + 자기
  // 텍스트의 sha다(K1 드라이런 결정 D-J — 루트 class·텍스트만으로는 인라인 style과
  // 추가된 자식 아이콘만으로 켜짐을 그리는 토글(A8 Checkbox)을 구분하지 못했다).
  var SURFACE_SKIP_TAGS = { script: 1, style: 1, template: 1 };
  function surfaceClassNameOf(el) {
    var cls = el.className;
    return typeof cls === 'string' ? cls : (el.getAttribute('class') || '');
  }
  function collectSurfaceRows(el, rows) {
    if (SURFACE_SKIP_TAGS[tagOf(el)]) return;
    rows.push([tagOf(el), surfaceClassNameOf(el) || '', attr(el, 'style') || '']);
    var children = el.children;
    for (var i = 0; i < children.length; i++) collectSurfaceRows(children[i], rows);
  }
  function surfaceOf(rec, checked) {
    if (checked !== null) return null;
    if (rec.kind !== 'handler' && rec.kind !== 'checkbox' && rec.kind !== 'switch') return null;
    var rows = [];
    collectSurfaceRows(rec.el, rows);
    return sha256(canonicalize([rows, collapseText(rec.el.textContent)]));
  }
  function valueEmptyOf(rec) {
    if (rec.kind !== 'input' && rec.kind !== 'textarea') return null;
    return rec.el.value === '';
  }

  function matchesAny(el, selectors) {
    for (var i = 0; i < selectors.length; i++) {
      try { if (el.matches(selectors[i]) || el.closest(selectors[i])) return true; } catch (e) { /* 잘못된 선택자 무시 */ }
    }
    return false;
  }

  // "스니펫은 outside_root(루트 밖에서 대상 조건을 만족한 요소 수·이름 표본)를
  // 기록하고, excluded_regions 선언에 매칭된 요소는 count에서 빼므로 남은
  // count > 0은 선언 유무와 무관하게 결함이다."(K3)
  function scanOutsideRoot(rootEl, scopeEls, opts) {
    var doc = rootEl.ownerDocument;
    var excluded = opts.excludedRegions || [];
    var all = doc.body ? doc.body.querySelectorAll('*') : [];
    var count = 0, sample = [];
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (el === rootEl || rootEl.contains(el) || scopeEls.has(el)) continue;
      if (el.closest('[aria-hidden="true"]')) continue;
      if (excluded.length && matchesAny(el, excluded)) continue;
      var style = styleOf(el);
      if (style.display === 'none' || style.visibility === 'hidden') continue;
      var rect = el.getBoundingClientRect();
      if (rect.width <= 0 || rect.height <= 0) continue;
      var role = roleOf(el);
      if (channelsOf({ el: el, role: role, style: style }, opts).length === 0) continue;
      count++;
      if (sample.length < 5) sample.push(accName(el));
    }
    return { count: count, sample: sample };
  }

  // ---------------------------------------------------------------------
  // dom.markCandidates — 범위 안 가시 요소에 el.__iaIndex를 심는다(DOM 무변).
  // CDP 리스너 열거가 index로 결과를 돌려주면 inventory가 그 index로 짝짓는다.
  // **계약**: index는 이 호출 시점의 순회 순서라 DOM이 바뀌면 무효다. 드라이버는
  // `listenerIndexes`를 쓰는 인벤토리마다 markCandidates → CDP 열거 → inventory
  // 순으로 다시 부른다(수정 라운드 1 발견 ⑨). **부르면 옛 표식은 사라진다** —
  // 문서와 순회하는 same-origin 프레임 문서의 표식을 전부 지운 뒤 새로 심으므로,
  // 이 호출이 표식을 남긴 요소 집합 = 이번 순회의 가시 요소 집합이다(3c 수정 라운드 1 C1).
  // ---------------------------------------------------------------------
  function markCandidates(rootSelector) {
    var rootEl = document.querySelector(rootSelector);
    if (!rootEl) return 0;
    // 숨어서 이번 순회에서 빠진 요소(닫힌 메뉴·감춘 탭 패널)가 옛 번호를 들고 있으면
    // 같은 번호를 새로 받은 요소와 겹쳐, index로 짝짓는 리스너 표가 엉뚱한 요소에
    // 붙거나(유령 handler 대상) 진짜 리스너 보유 요소를 놓친다 — 부여 전에 지운다.
    clearMarks(rootEl.ownerDocument);
    var rendered = walkScope(rootEl).records.filter(function (rec) { return rec.rendered; });
    rendered.forEach(function (rec, index) { rec.el.__iaIndex = index; });
    return rendered.length;
  }

  function clearMarks(doc) {
    var all = doc.querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (typeof el.__iaIndex === 'number') delete el.__iaIndex;
      if (tagOf(el) !== 'iframe') continue;
      var sub = null;
      try { sub = el.contentDocument; } catch (e) { sub = null; }
      if (sub) clearMarks(sub);
    }
  }

  // ---------------------------------------------------------------------
  // dom.inventory — K2 대상 열거 + K3 루트·outside_root + K7 targets/entries.
  // `opts.listenerIndexes`를 주려면 **이 호출 직전에** markCandidates를 다시 불러
  // 표식을 새로 심어야 한다(위 계약). 표식 없는 요소는 매칭을 건너뛴다.
  // entries는 K7의 8필드(entry_doc_fields)에 드라이버용 런타임 값(kind·rect·
  // dom_path)과 identity 원본 4필드(role·name·input_type·owner — 파일 머리의
  // «entries 공용 모양» 계약)를 더 얹어 낸다. 문서에 쓸 때의 투영은 드라이버 몫이다.
  // ---------------------------------------------------------------------
  function inventory(rootSelector, opts) {
    opts = opts || {};
    var rootEl = document.querySelector(rootSelector);
    if (!rootEl) {
      lastInventory = null;
      return {
        root: { selector: rootSelector, found: false, fingerprint: null },
        outside_root: { count: 0, sample: [] }, entries: [], targets: {},
        overlays: [], declared_unmatched: [], limits: [],
        entry_doc_fields: ENTRY_DOC_FIELDS
      };
    }
    var rootRect = rectOf(rootEl, ZERO_OFFSET);
    var scope = walkScope(rootEl);
    var records = scope.records, byEl = scope.byEl;

    records.forEach(function (rec) {
      rec.role = roleOf(rec.el);
      rec.inputType = tagOf(rec.el) === 'input' ? (attr(rec.el, 'type') || 'text').toLowerCase() : '';
      rec.live = isLive(rec.el);
      rec.channels = rec.nativeOption ? ['semantic']
        : (rec.rendered ? channelsOf(rec, opts) : []); // 그려지지 않은 요소는 대상이 아니다
    });

    // "선언(--declared)은 대상을 늘릴 뿐 줄이지 못한다 … 어느 인벤토리에도
    // 매칭되지 않으면 declared_unmatched"(K2)
    var declaredUnmatched = [];
    (opts.declared || []).forEach(function (row) {
      var selector = row && row.selector;
      if (!selector) return;
      var found = [];
      try { found = rootEl.ownerDocument.querySelectorAll(selector); } catch (e) { found = []; }
      var matched = false;
      for (var i = 0; i < found.length; i++) {
        var rec = byEl.get(found[i]);
        if (!rec || (!rec.rendered && !rec.nativeOption)) continue;
        matched = true;
        if (rec.channels.indexOf('declared') === -1) rec.channels.push('declared');
      }
      if (!matched) declaredUnmatched.push({ selector: selector, reason: row.reason === undefined ? null : row.reason });
    });

    records.forEach(function (rec) {
      if (rec.nativeOption || !rec.rendered) return;
      var info = overlayInfoOf(rec, rootRect);
      if (!info) return;
      rec.overlay = true;
      rec.scrim = info.scrim;
      if (rec.channels.indexOf(info.channel) === -1) rec.channels.push(info.channel);
    });

    records.forEach(function (rec) {
      rec.isTarget = rec.channels.length > 0;
      if (!rec.isTarget) return;
      var declaredOnly = rec.channels.length === 1 && rec.channels[0] === 'declared';
      rec.kind = rec.nativeOption ? 'option' : kindOf(rec.el, rec.role, rec.overlay === true, declaredOnly);
    });
    records.forEach(function (rec) { rec.ownerEl = ownerElOf(rec, byEl); });

    // 이름은 kind가 정해진 뒤에 짓는다 — «자기 텍스트» 폴백이 컨테이너에서만 닫히므로
    // (K1 D-A) 그 판별에 kind와 «대상 후손 보유»가 필요하다. 표식은 각 대상에서 조상
    // 기록을 타고 올라가며 심는다(이미 심긴 조상 위는 앞선 대상이 이미 심었다).
    records.forEach(function (rec) {
      if (!rec.isTarget) return;
      var node = rec.el.parentElement;
      while (node) {
        var parentRec = byEl.get(node);
        if (!parentRec || parentRec.hasTargetDescendant) break; // 범위 밖이거나 이미 심겼다
        parentRec.hasTargetDescendant = true;
        node = node.parentElement;
      }
    });
    records.forEach(function (rec) { rec.name = accName(rec.el, rec); });

    // "owner_items_hash는 같은 owner 안 형제 항목 이름 목록의 sha"(K1) — 항목 kind만
    // 센다. 항목이 없는 owner는 빈 목록의 sha라서, 같은 owner 아래 버튼이 늘고 주는
    // 것으로 형제 identity가 흔들리지 않는다(수정 라운드 1 발견 ②).
    var itemNames = new Map();
    records.forEach(function (rec) {
      if (!rec.isTarget || !rec.ownerEl || !ITEM_KINDS[rec.kind]) return;
      var names = itemNames.get(rec.ownerEl) || [];
      names.push(rec.name);
      itemNames.set(rec.ownerEl, names);
    });
    records.forEach(function (rec) {
      if (!rec.ownerEl) { rec.itemsHash = ''; return; }
      var names = itemNames.get(rec.ownerEl) || [];
      rec.itemsHash = sha256(canonicalize(names.slice().sort()));
    });

    assignIdentities(records, byEl, null);
    var collided = collidingRecords(records);
    if (collided.size > 0) assignIdentities(records, byEl, collided);

    var view = rootEl.ownerDocument.defaultView;
    var viewport = { w: view.innerWidth, h: view.innerHeight };
    var targetRecs = records.filter(function (rec) { return rec.isTarget && !rec.nativeOption; });
    targetRecs.forEach(function (rec) {
      rec.descendantRects = targetRecs
        .filter(function (other) { return other !== rec && rec.el.contains(other.el); })
        .map(function (other) { return other.rect; });
      resolveClickPoint(rec, viewport);
    });

    var entries = [], targets = {}, overlays = [], byId = {};
    records.forEach(function (rec) {
      if (!rec.isTarget) return;
      byId[rec.id] = rec;
      var target = {
        role: rec.role, name: rec.name, input_type: rec.inputType, owner: rec.owner,
        owner_items_hash: rec.itemsHash, dom_path: rec.domPath, kind: rec.kind,
        declared: rec.channels.indexOf('declared') !== -1,
        found_by: sortChannels(rec.channels), live: rec.live
      };
      if (rec.nativeOption) {
        target.value = rec.el.value;
        targets[rec.id] = target;
        return;
      }
      if (rec.kind === 'overlay') {
        target.scrim = rec.scrim === true;
        overlays.push(rec.id);
      }
      targets[rec.id] = target;
      var checked = checkedOf(rec);
      entries.push({
        id: rec.id, enabled: isEnabled(rec.el), checked: checked, face: faceOf(rec),
        value_empty: valueEmptyOf(rec), surface: surfaceOf(rec, checked),
        occluded: rec.occluded === true, live: rec.live, kind: rec.kind,
        rect: roundRect(rec.rect), dom_path: rec.domPath,
        // identity 원본 4필드 — 파일 머리의 «entries 공용 모양» 계약이다.
        // surfaceKey의 reducedIdentityOf가 이 값으로 축약 identity를 다시 만들므로
        // 빠지면 모든 항목이 한 값으로 접혀 표면 키가 상수가 된다(수정 라운드 1 I-1).
        role: rec.role, name: rec.name, input_type: rec.inputType, owner: rec.owner
      });
    });

    var scopeEls = new Set();
    records.forEach(function (rec) { scopeEls.add(rec.el); });
    lastInventory = {
      rootEl: rootEl, rootRect: rootRect, records: records, byEl: byEl, byId: byId,
      opts: opts, hoverSelectors: opts.hoverSelectors || []
    };

    return {
      root: {
        selector: rootSelector, found: true,
        fingerprint: {
          tag: tagOf(rootEl), label: attr(rootEl, 'data-screen-label'),
          descendants: rootEl.querySelectorAll('*').length, rect: roundRect(rootRect)
        }
      },
      outside_root: scanOutsideRoot(rootEl, scopeEls, opts),
      entries: entries, targets: targets, overlays: overlays,
      declared_unmatched: declaredUnmatched, limits: scope.limits,
      entry_doc_fields: ENTRY_DOC_FIELDS
    };
  }

  function clickPoint(id) {
    var rec = lastInventory ? lastInventory.byId[id] : null;
    return rec && rec.point ? rec.point : null;
  }

  // "click:outside 지점: 스크림형은 오버레이 rect 안·후손 대상 rect 밖,
  // 비스크림형(role=menu/listbox·루트를 덮지 않음)은 루트 rect 안·오버레이 rect
  // 밖·owner 트리거 rect 밖"(K2)
  function outsidePoint(overlayId) {
    var state = lastInventory;
    var rec = state ? state.byId[overlayId] : null;
    if (!rec || rec.kind !== 'overlay') return null;
    if (rec.scrim === true) return rec.point;
    var triggerRect = triggerRectOf(rec, state);
    var root = state.rootRect, steps = 16;
    for (var row = 1; row <= steps; row++) {
      for (var col = 1; col <= steps; col++) {
        var point = { x: root.x + root.w * col / (steps + 1), y: root.y + root.h * row / (steps + 1) };
        if (inRect(point, rec.rect)) continue;
        if (triggerRect && inRect(point, triggerRect)) continue;
        var hit = elementAt(rec, point); // 오버레이가 iframe 안이면 그 문서로 hit-test
        if (!hit || rec.el.contains(hit)) continue;
        var sameDoc = rec.doc === state.rootEl.ownerDocument;
        if (sameDoc && hit !== state.rootEl && !state.rootEl.contains(hit)) continue;
        return roundPoint(point);
      }
    }
    return null;
  }
  function triggerRectOf(rec, state) {
    var id = rec.el.id;
    var owner = null;
    if (id) {
      for (var i = 0; i < state.records.length; i++) {
        var candidate = state.records[i];
        if (candidate.nativeOption) continue;
        var controls = attr(candidate.el, 'aria-controls');
        if (controls && controls.split(/\s+/).indexOf(id) !== -1) { owner = candidate; break; }
      }
    }
    if (!owner && rec.ownerEl) owner = state.byEl.get(rec.ownerEl);
    return owner ? owner.rect : null;
  }

  // "발견 조작: mouseenter/mouseover 리스너나 :hover 규칙(render-audit
  // hoverSelectors 매칭) 보유 요소에 hover 후 재인벤토리(후보는 identity당 1회이며
  // 항목형 menuitem·option·radio·checkbox·switch·tab은 제외)"(K2 드라이런 결정 D-C).
  // 항목형은 hover로 새 대상을 여는 자리가 아닌데 수가 많아, 상한 안에서 실행해야 할
  // 조작을 발견 step이 밀어낸다(A8 실측 838 step 중 hover 394·발견 0).
  function hoverCandidates() {
    var state = lastInventory;
    if (!state) return [];
    var selectors = state.hoverSelectors;
    var out = [];
    state.records.forEach(function (rec) {
      if (!rec.isTarget || rec.nativeOption || ITEM_KINDS[rec.kind]) return;
      var el = rec.el;
      var props = reactPropsOf(el);
      var hover = !!(props && hasAnyProp(props, REACT_HOVER_PROPS)) ||
        el.hasAttribute('onmouseenter') || el.hasAttribute('onmouseover');
      if (!hover) {
        var types = listenerTypesOf(el, state.opts);
        hover = !!(types && anyTypeIn(types, HOVER_LISTENER_TYPES));
      }
      if (!hover && selectors.length) hover = matchesAny(el, selectors);
      if (hover) out.push(rec.id);
    });
    return out;
  }

  // "스크롤 가능한 컨테이너는 끝까지 스크롤 후 재인벤토리"(K2) — 대상이 아닌
  // 컨테이너도 드라이버가 스크롤해야 하므로 id 없이 dom_path로 낸다.
  function scrollContainers() {
    var state = lastInventory;
    if (!state) return [];
    var out = [];
    state.records.forEach(function (rec) {
      if (rec.nativeOption || !rec.rendered) return;
      var overflowY = rec.style.overflowY, overflowX = rec.style.overflowX;
      var scrollable = overflowY === 'auto' || overflowY === 'scroll' ||
                       overflowX === 'auto' || overflowX === 'scroll';
      if (!scrollable) return;
      if (rec.el.scrollHeight <= rec.el.clientHeight) return;
      out.push({
        id: rec.isTarget ? rec.id : null, dom_path: rec.domPath,
        scrollHeight: rec.el.scrollHeight, clientHeight: rec.el.clientHeight
      });
    });
    return out;
  }

  var dom = {
    markCandidates: markCandidates,
    inventory: inventory,
    clickPoint: clickPoint,
    outsidePoint: outsidePoint,
    hoverCandidates: hoverCandidates,
    scrollContainers: scrollContainers
  };


  return {
    KINDS: KINDS,
    ENTRY_DOC_FIELDS: ENTRY_DOC_FIELDS,
    normalizeName: normalizeName,
    identityOf: identityOf,
    stateContext: stateContext,
    contextFor: contextFor,
    stateHash: stateHash,
    surfaceKey: surfaceKey,
    requiredActions: requiredActions,
    residual: residual,
    linkedSurfaces: linkedSurfaces,
    sha256: sha256,
    dom: dom
  };
});
