// interaction_audit.js(dddjango-web · pure) 자기 회귀 테스트 — node:test + node:assert/strict.
// 실행: `node --test dddjango-web/scripts/test/test_interaction_audit.mjs`
//      또는 직접: `node dddjango-web/scripts/test/test_interaction_audit.mjs`
// 대상 규범: workspace/design/2026-09-13-web-interaction-evidence.md K1·K2·K7.
// 5개 fixture(expected/doc-{register,edit,cascade,handler-toggle,mixed}.json)의 residual·
// linkedSurfaces 기대값은 이 파일 안에 하드코딩한다(계산해서 비교하지 않는다 — 태스크 결정).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const require = createRequire(import.meta.url);
const pure = require('../../assets/interaction_audit.js');

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fixtureDir = path.join(__dirname, 'fixtures', 'interaction', 'expected');
const loadFixture = (name) => JSON.parse(readFileSync(path.join(fixtureDir, name), 'utf8'));

// ---- 테스트 헬퍼 — entries 공용 모양 기본값(파일 헤더 JSDoc과 동일) ----
function entry(id, overrides) {
  return Object.assign({
    id, role: '', name: id, input_type: '', owner: '',
    enabled: true, occluded: false,
    checked: null, face: null, value_empty: null, surface: null,
    live: false,
  }, overrides || {});
}

// =====================================================================
// sha256 — node:crypto 대조(하드코딩 hex 없이 실제 구현으로 상호 검증)
// =====================================================================
test('sha256_matches_node_crypto_for_various_inputs', () => {
  const samples = ['', 'abc', 'hello world', '한글 이름 검증', 'x'.repeat(200)];
  for (const s of samples) {
    const want = createHash('sha256').update(s, 'utf8').digest('hex');
    assert.equal(pure.sha256(s), want, `mismatch for ${JSON.stringify(s)}`);
  }
});

// =====================================================================
// normalizeName
// =====================================================================
test('normalize_name_nfc_nbsp_collapse_trim_80', () => {
  const withNbsp = ' 확인  버튼  ';
  assert.equal(pure.normalizeName(withNbsp), '확인 버튼');
  assert.equal(pure.normalizeName('  a   b  '), 'a b');
  assert.equal(pure.normalizeName('x'.repeat(90)).length, 80);
  assert.equal(pure.normalizeName(null), '');
});

// =====================================================================
// identityOf
// =====================================================================
test('identity_ignores_value_and_face', () => {
  const base = { role: 'button', name: '다음', input_type: '', owner: '', owner_items_hash: '' };
  const id1 = pure.identityOf(Object.assign({}, base, { face: 'A', checked: true, value: 'x' }), false);
  const id2 = pure.identityOf(Object.assign({}, base, { face: 'B', checked: false, value: 'y' }), false);
  assert.equal(id1, id2, 'identity는 face/checked/value 같은 관찰 값을 반영하지 않아야 한다');
  assert.equal(id1.length, 12);
});

test('identity_dom_path_only_on_empty_name_or_collision', () => {
  const namedFields = (domPath) => ({
    role: 'menuitem', name: '배우자', input_type: '', owner: 'owner1', owner_items_hash: 'h1', dom_path: domPath,
  });
  // 이름이 있고 충돌 없음 — dom_path 무시
  assert.equal(
    pure.identityOf(namedFields('path/a'), false),
    pure.identityOf(namedFields('path/b'), false),
  );
  // 이름이 있어도 충돌이면 dom_path 반영
  assert.notEqual(
    pure.identityOf(namedFields('path/a'), true),
    pure.identityOf(namedFields('path/b'), true),
  );
  // 이름이 빈 대상은 충돌 플래그 없이도 dom_path 반영
  const emptyNameFields = (domPath) => ({
    role: 'button', name: '', input_type: '', owner: '', owner_items_hash: '', dom_path: domPath,
  });
  assert.notEqual(
    pure.identityOf(emptyNameFields('path/a'), false),
    pure.identityOf(emptyNameFields('path/b'), false),
  );
});

// =====================================================================
// contextFor — K1 context_T 축약 규칙
// =====================================================================
test('context_trigger_prior_face_only', () => {
  const docOrder = ['t1', 't2', 't3'];
  const target = { id: 't2', kind: 'trigger' };
  const base = [entry('t1', { face: 'A' }), entry('t2', { face: 'X' }), entry('t3', { face: 'B' })];
  const changedSelfFace = [entry('t1', { face: 'A' }), entry('t2', { face: 'Y' }), entry('t3', { face: 'B' })];
  const changedAfterFace = [entry('t1', { face: 'A' }), entry('t2', { face: 'X' }), entry('t3', { face: 'C' })];
  const changedBeforeFace = [entry('t1', { face: 'Z' }), entry('t2', { face: 'X' }), entry('t3', { face: 'B' })];

  const h0 = pure.contextFor(base, target, docOrder);
  assert.equal(h0.length, 16);
  assert.equal(pure.contextFor(changedSelfFace, target, docOrder), h0, '자기 face는 제외되어야 한다');
  assert.equal(pure.contextFor(changedAfterFace, target, docOrder), h0, '뒤 트리거 face는 제외되어야 한다');
  assert.notEqual(pure.contextFor(changedBeforeFace, target, docOrder), h0, '앞 트리거 face는 포함되어야 한다');
});

test('context_menu_item_excludes_owner_face', () => {
  const target = { id: 'item1', kind: 'menuitem', owner: 'ownerTrigger' };
  const docOrder = ['ownerTrigger', 'otherTrigger', 'item1'];
  const base = [entry('ownerTrigger', { kind: 'trigger', face: 'OWNER' }), entry('otherTrigger', { face: 'OTHER' }), entry('item1')];
  const changedOwnerFace = [entry('ownerTrigger', { face: 'OWNER-2' }), entry('otherTrigger', { face: 'OTHER' }), entry('item1')];
  const changedOtherFace = [entry('ownerTrigger', { face: 'OWNER' }), entry('otherTrigger', { face: 'OTHER-2' }), entry('item1')];

  const h0 = pure.contextFor(base, target, docOrder);
  assert.equal(pure.contextFor(changedOwnerFace, target, docOrder), h0, 'owner 트리거 face는 제외되어야 한다');
  assert.notEqual(pure.contextFor(changedOtherFace, target, docOrder), h0, '다른 트리거 face는 포함되어야 한다');
});

test('context_button_excludes_all_faces', () => {
  const target = { id: 'btn1', kind: 'button' };
  const docOrder = ['trigger1', 'btn1'];
  const base = [entry('trigger1', { face: 'A' }), entry('btn1')];
  const changedFace = [entry('trigger1', { face: 'B' }), entry('btn1')];
  const changedChecked = [entry('trigger1', { face: 'A' }), entry('btn1', { checked: true })];

  const h0 = pure.contextFor(base, target, docOrder);
  assert.equal(pure.contextFor(changedFace, target, docOrder), h0, '버튼은 face 성분 전체가 제외되어야 한다');
  assert.notEqual(pure.contextFor(changedChecked, target, docOrder), h0, 'checked 같은 다른 성분은 그대로 반영되어야 한다');
});

// =====================================================================
// stateHash
// =====================================================================
test('state_hash_excludes_live_entries', () => {
  const withoutLive = [entry('e1', { checked: true })];
  const withLiveDefault = [entry('e1', { checked: true }), entry('e2', { live: true, face: 'anything' })];
  const withLiveChanged = [entry('e1', { checked: true }), entry('e2', { live: true, face: 'changed', checked: false })];
  const withLiveFalse = [entry('e1', { checked: true }), entry('e2', { live: false, face: 'x' })];

  const h0 = pure.stateHash(withoutLive, 'http://x/');
  assert.equal(pure.stateHash(withLiveDefault, 'http://x/'), h0, 'live:true 항목은 해시 입력에서 제외되어야 한다');
  assert.equal(pure.stateHash(withLiveChanged, 'http://x/'), h0, 'live 항목 값이 바뀌어도 해시는 불변이어야 한다');
  assert.notEqual(pure.stateHash(withLiveFalse, 'http://x/'), h0, 'live:false면 다시 포함되어야 한다');
  assert.notEqual(pure.stateHash(withoutLive, 'http://y/'), h0, 'url이 다르면 해시도 달라야 한다');
});

// =====================================================================
// surfaceKey
// =====================================================================
test('surface_key_collapses_menu_items_across_owner_hash', () => {
  const itemsWithHashA = [
    entry('i1', { role: 'menuitem', name: 'X', owner: 'm', owner_items_hash: 'H1' }),
    entry('i2', { role: 'menuitem', name: 'Y', owner: 'm', owner_items_hash: 'H1' }),
  ];
  const itemsWithHashB = [
    entry('i1', { role: 'menuitem', name: 'X', owner: 'm', owner_items_hash: 'H2-DIFFERENT' }),
    entry('i2', { role: 'menuitem', name: 'Y', owner: 'm', owner_items_hash: 'H2-DIFFERENT' }),
  ];
  const itemsWithDifferentOwner = [
    entry('i1', { role: 'menuitem', name: 'X', owner: 'm-other', owner_items_hash: 'H1' }),
    entry('i2', { role: 'menuitem', name: 'Y', owner: 'm-other', owner_items_hash: 'H1' }),
  ];

  const k0 = pure.surfaceKey(itemsWithHashA);
  assert.equal(pure.surfaceKey(itemsWithHashB), k0, 'owner_items_hash 차이는 surfaceKey에 반영되지 않아야 한다');
  assert.notEqual(pure.surfaceKey(itemsWithDifferentOwner), k0, 'owner 자체가 다르면 surfaceKey도 달라야 한다');
});

test('surface_key_separates_empty_name_containers_by_dom_path', () => {
  // D-A 이후 컨테이너 이름은 대개 빈다 — 축약 identity가 dom_path를 빼면 role·owner가 같은
  // 두 오버레이가 한 값으로 접혀 서로 다른 표면이 한 표면이 된다(K1 "이름이 빈 대상만
  // dom_path를 identity에 넣는다" · K3는 그 identity에서 owner_items_hash 등만 뺀다).
  const menuA = [entry('o1', { role: 'menu', name: '', dom_path: 'div:nth-of-type(5)' })];
  const menuB = [entry('o2', { role: 'menu', name: '', dom_path: 'div:nth-of-type(6)' })];
  assert.notEqual(pure.surfaceKey(menuA), pure.surfaceKey(menuB),
    '이름이 빈 두 컨테이너가 한 표면으로 접혔다');
  // 같은 자리면 같은 표면이다 — id 자체는 표면 키 입력이 아니다.
  const sameSpot = [entry('o3', { role: 'menu', name: '', dom_path: 'div:nth-of-type(5)' })];
  assert.equal(pure.surfaceKey(sameSpot), pure.surfaceKey(menuA));
  // 이름이 있으면 dom_path는 들어가지 않는다(K1) — 자리가 달라도 한 표면이다.
  const named1 = [entry('n1', { role: 'menu', name: '메뉴', dom_path: 'div:nth-of-type(5)' })];
  const named2 = [entry('n2', { role: 'menu', name: '메뉴', dom_path: 'div:nth-of-type(9)' })];
  assert.equal(pure.surfaceKey(named1), pure.surfaceKey(named2));
});

test('surface_key_excludes_inactive_and_live', () => {
  const active = [entry('i1')];
  const withInactive = [entry('i1'), entry('i2', { enabled: false })];
  const withOccluded = [entry('i1'), entry('i2', { occluded: true })];
  const withLive = [entry('i1'), entry('i2', { live: true })];

  const k0 = pure.surfaceKey(active);
  assert.equal(pure.surfaceKey(withInactive), k0);
  assert.equal(pure.surfaceKey(withOccluded), k0);
  assert.equal(pure.surfaceKey(withLive), k0);
});

// =====================================================================
// requiredActions
// =====================================================================
test('required_actions_click_only_kinds', () => {
  for (const kind of ['button', 'link', 'menuitem', 'option', 'tab', 'radio', 'handler', 'declared']) {
    assert.deepEqual(pure.requiredActions({ kind }, []), [{ action: 'click', option: null }], kind);
  }
});

test('required_actions_toggle_two_states', () => {
  const units = pure.requiredActions({ kind: 'checkbox' }, [false, true, true, false]);
  assert.deepEqual(units, [
    { action: 'click', option: false },
    { action: 'click', option: true },
  ]);
});

// 드라이런 6차 결정 D-H — "토글형 = checkbox·switch·radio, 그리고 이름이 있는(대상 후손이
// 없는) handler … checked가 없으면 surface가 상태이며 관찰된 surface마다 click 단위가
// 필요하다"(K1 잔여 단위). A8의 «윤달·몰라요»가 role 없는 <label> 핸들러라 1회 click으로
// 끝나던 자리다. 이름이 빈 handler(컨테이너 — D-A)와 overlay는 토글형이 아니다.
test('required_actions_named_handler_is_a_surface_toggle', () => {
  const surfaceA = 'a'.repeat(64);
  const surfaceB = 'b'.repeat(64);
  assert.deepEqual(pure.requiredActions({ kind: 'handler', name: '윤달' }, [surfaceA, surfaceB, surfaceA]), [
    { action: 'click', option: surfaceA },
    { action: 'click', option: surfaceB },
  ]);
  // checked가 있는 handler(aria-checked 등)는 checkbox와 같은 규칙으로 checked가 상태다.
  assert.deepEqual(pure.requiredActions({ kind: 'handler', name: '몰라요' }, [false, true]), [
    { action: 'click', option: false },
    { action: 'click', option: true },
  ]);
  // 이름이 빈 handler는 컨테이너다 — surface가 관찰돼도 click 1회다.
  assert.deepEqual(pure.requiredActions({ kind: 'handler', name: '' }, [surfaceA, surfaceB]),
    [{ action: 'click', option: null }]);
  // 이름 필드가 아예 없는 호출(kind만 주는 옛 호출부)도 click 1회다.
  assert.deepEqual(pure.requiredActions({ kind: 'handler' }, [surfaceA, surfaceB]),
    [{ action: 'click', option: null }]);
  // aria-label을 달아 이름이 남은 **컨테이너** handler(대상 후손이 있다)도 토글형이 아니다 —
  // 컨테이너의 surface는 서브트리 텍스트라 상태마다 갈린다(D-A가 identity에서 막은 병).
  const nested = {
    cover: { kind: 'handler', name: '덮개', dom_path: 'span:nth-of-type(1)' },
    inner: { kind: 'button', name: '덮개 안 버튼', dom_path: 'span:nth-of-type(1)/button:nth-of-type(1)' },
  };
  assert.deepEqual(
    pure.requiredActions(Object.assign({ id: 'cover' }, nested.cover), [surfaceA, surfaceB], nested),
    [{ action: 'click', option: null }],
  );
  // 형제(같은 접두를 쓰지 않는 대상)는 후손이 아니다 — 접두 비교가 '/' 경계를 지킨다.
  const sibling = {
    leap: { kind: 'handler', name: '윤달', dom_path: 'div:nth-of-type(1)' },
    other: { kind: 'button', name: '저장', dom_path: 'div:nth-of-type(11)/button:nth-of-type(1)' },
  };
  assert.deepEqual(
    pure.requiredActions(Object.assign({ id: 'leap' }, sibling.leap), [surfaceA, surfaceB], sibling),
    [{ action: 'click', option: surfaceA }, { action: 'click', option: surfaceB }],
  );
});

test('required_actions_text_inputs_focus_fill_blur', () => {
  for (const kind of ['input', 'textarea']) {
    assert.deepEqual(pure.requiredActions({ kind }, []), [
      { action: 'focus', option: null },
      { action: 'fill', option: null },
      { action: 'blur', option: null },
    ]);
  }
});

test('required_actions_native_select_option_is_select_with_value', () => {
  // 수정 라운드 1 컨트롤러 판정: 옵션은 owner kind로 분기한다. owner가 select(native)이면
  // {select, option:target.value} 고정 1단위, select 요소 자체는 단위를 요구하지 않는다.
  const targets = {
    sel1: { kind: 'select' },
    optA: { kind: 'option', owner: 'sel1', value: 'A' },
    optB: { kind: 'option', owner: 'sel1', value: 'B' },
    optC: { kind: 'option', owner: 'sel1', value: 'C' },
  };
  assert.deepEqual(pure.requiredActions(targets.optA, [], targets), [{ action: 'select', option: 'A' }]);
  assert.deepEqual(pure.requiredActions(targets.optB, [], targets), [{ action: 'select', option: 'B' }]);
  assert.deepEqual(pure.requiredActions(targets.optC, [], targets), [{ action: 'select', option: 'C' }]);
  assert.deepEqual(pure.requiredActions(targets.sel1, [], targets), [], 'select 요소 자체는 아무 단위도 요구하지 않는다');
});

test('required_actions_option_under_listbox_owner_is_plain_click', () => {
  const targets = {
    menu1: { kind: 'menu' }, // select가 아닌 owner(menu/listbox) — click 1회
    optZ: { kind: 'option', owner: 'menu1' },
  };
  assert.deepEqual(pure.requiredActions(targets.optZ, [], targets), [{ action: 'click', option: null }]);
});

test('required_overlay_needs_escape_and_outside', () => {
  const units = pure.requiredActions({ kind: 'overlay' }, []);
  assert.deepEqual(units, [
    { action: 'click', option: 'outside' },
    { action: 'key', option: 'Escape' },
  ]);
});

test('required_scrim_outside_equals_click', () => {
  const units = pure.requiredActions({ kind: 'overlay', scrim: true }, []);
  assert.deepEqual(units, [
    { action: 'click', option: null },
    { action: 'key', option: 'Escape' },
  ]);
  assert.ok(!units.some((u) => u.option === 'outside'), 'outside 단위가 자기 click과 중복 계수되면 안 된다');
});

// =====================================================================
// residual / linkedSurfaces — 소단위 문서
// =====================================================================
function docWith(targets, initialInventory, steps) {
  return {
    version: 1, targets, initial: { inventory: initialInventory, state_hash: 's0', surface_key: 'sf0' },
    steps: steps || [],
  };
}

test('residual_counts_executed_only', () => {
  const targets = { btn1: { role: 'button', name: '확인', input_type: '', owner: '', owner_items_hash: '', kind: 'button' } };
  const inv = [entry('btn1')];

  const notExecuted = docWith(targets, inv, [
    { n: 1, target: 'btn1', action: 'click', option: null, status: 'failed' },
    { n: 2, target: 'btn1', action: 'click', option: null, status: 'unreachable' },
    { n: 3, target: 'btn1', action: 'click', option: null, status: 'unclickable' },
  ]);
  assert.deepEqual(pure.residual(notExecuted), [{ target: 'btn1', action: 'click', option: null }]);

  const executed = docWith(targets, inv, [
    { n: 1, target: 'btn1', action: 'click', option: null, status: 'failed' },
    { n: 2, target: 'btn1', action: 'click', option: null, status: 'executed' },
  ]);
  assert.deepEqual(pure.residual(executed), []);
});

test('residual_covers_targets_seen_only_in_step_inventories', () => {
  const targets = {
    trg: { role: 'button', name: '열기', input_type: '', owner: '', owner_items_hash: '', kind: 'trigger' },
    itm: { role: 'menuitem', name: '항목', input_type: '', owner: 'trg', owner_items_hash: 'h', kind: 'menuitem' },
  };
  const initialInv = [entry('trg')];
  const steps = [
    {
      n: 1, target: 'trg', action: 'click', option: null, status: 'executed',
      before: { inventory: initialInv, state_hash: 's0' },
      after: { inventory: [entry('trg'), entry('itm')], state_hash: 's1', surface_key: 'sf1' },
      changes: { added: ['itm'], removed: [] },
    },
  ];
  const doc = docWith(targets, initialInv, steps);
  assert.deepEqual(pure.residual(doc), [{ target: 'itm', action: 'click', option: null }]);
});

test('residual_reports_unselected_native_option', () => {
  // 수정 라운드 1 컨트롤러 판정: 네이티브 select 옵션은 인벤토리에 한 번도
  // 활성으로 나타나지 않아도(native <option>은 일반 DOM 서브트리 관측 대상이
  // 아닐 수 있다) 자기 target 정의만으로 잔여 단위를 낸다.
  const targets = {
    sel1: { role: 'listbox', name: '지역', input_type: 'select', owner: '', owner_items_hash: '', kind: 'select' },
    optA: { role: 'option', name: '서울', input_type: '', owner: 'sel1', owner_items_hash: 'h', kind: 'option', value: 'seoul' },
    optB: { role: 'option', name: '부산', input_type: '', owner: 'sel1', owner_items_hash: 'h', kind: 'option', value: 'busan' },
    optC: { role: 'option', name: '대구', input_type: '', owner: 'sel1', owner_items_hash: 'h', kind: 'option', value: 'daegu' },
  };
  // optA/optB/optC는 어느 inventory에도 등장하지 않는다 — sel1만 관측된다.
  const initialInv = [entry('sel1', { kind: 'select' })];
  const doc = docWith(targets, initialInv, [
    { n: 1, target: 'optA', action: 'select', option: 'seoul', status: 'executed' },
  ]);
  const result = pure.residual(doc).sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)));
  assert.deepEqual(result, [
    { target: 'optB', action: 'select', option: 'busan' },
    { target: 'optC', action: 'select', option: 'daegu' },
  ]);
});

test('linked_surfaces_from_added_steps', () => {
  const doc = {
    version: 1,
    steps: [
      { changes: { added: ['x'], removed: [] }, after: { surface_key: 'S1' } },
      { changes: { added: [], removed: ['y'] }, after: { surface_key: 'S2' } },
      { changes: { added: ['z'], removed: [] }, after: { surface_key: 'S3' } },
      { changes: { added: [], removed: [] }, after: { surface_key: 'S4' }, navigated: 'http://x/next' },
    ],
  };
  const result = pure.linkedSurfaces(doc);
  assert.ok(result instanceof Set);
  assert.deepEqual([...result].sort(), ['S1', 'S3']);
});

// =====================================================================
// fixture 문서 3종 — K7 최소 interactions.json, residual/surface 기대값 하드코딩
// =====================================================================
test('fixture_doc_register_residual_and_surfaces', () => {
  const doc = loadFixture('doc-register.json');
  assert.deepEqual(pure.residual(doc), [], 'register 픽스처는 완전 실행되어 잔여가 없어야 한다');
  assert.deepEqual([...pure.linkedSurfaces(doc)].sort(), []);
});

test('fixture_doc_edit_residual_and_surfaces', () => {
  const doc = loadFixture('doc-edit.json');
  // region-select에 네이티브 옵션 3개(서울·부산·대구) 중 서울만 executed(step 7) —
  // 나머지 둘은 인벤토리 관측 여부와 무관하게 잔여로 남는다(수정 라운드 1 판정).
  const expectedResidual = [
    { target: 'region-busan', action: 'select', option: 'busan' },
    { target: 'region-daegu', action: 'select', option: 'daegu' },
  ].sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)));
  const actualResidual = pure.residual(doc).sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)));
  assert.deepEqual(actualResidual, expectedResidual);
  assert.deepEqual([...pure.linkedSurfaces(doc)].sort(), []);
  // edit은 value_empty=false로 시작 — register와 같은 식별자라도 «다음» context_T가 달라야 한다
  const registerDoc = loadFixture('doc-register.json');
  const nextId = 'next-button';
  const ctxEdit = pure.contextFor(
    doc.initial.inventory.map((e) => Object.assign({}, e, doc.targets[e.id])),
    Object.assign({ id: nextId }, doc.targets[nextId]),
    Object.keys(doc.targets),
  );
  const ctxRegister = pure.contextFor(
    registerDoc.initial.inventory.map((e) => Object.assign({}, e, registerDoc.targets[e.id])),
    Object.assign({ id: nextId }, registerDoc.targets[nextId]),
    Object.keys(registerDoc.targets),
  );
  assert.notEqual(ctxEdit, ctxRegister, 'value_empty 차이가 다음 버튼 context_T에 반영되어야 한다');
});

test('fixture_doc_handler_toggle_residual_keeps_the_unclicked_surface', () => {
  const doc = loadFixture('doc-handler-toggle.json');
  // D-H — 이름이 있는 **leaf** handler «윤달»은 surface 토글형이다. surface A는 step 1이
  // 눌렀고 surface B(그 결과 상태)는 아무 step도 누르지 않았으므로 잔여로 남는다.
  // 토글형이 **아닌** 두 갈래도 이 fixture가 함께 고정한다: 이름이 빈 컨테이너 handler
  // (card-wrap)와, aria-label로 이름이 남았지만 대상 후손이 있는 컨테이너(cover-label) —
  // 둘 다 click 1회면 잔여가 없다(step 2·4가 닫는다). 후손 가지를 빼면 cover-label의
  // surface 단위가 잔여에 하나 더 생기므로 이 기대값이 그 가지를 지킨다(두 구현 동일성).
  assert.deepEqual(pure.residual(doc), [
    { target: 'leap-label', action: 'click', option: 'b'.repeat(64) },
  ]);
  assert.deepEqual([...pure.linkedSurfaces(doc)].sort(), []);
});

// aria-checked="mixed"(3상태 «전체 선택» 헤더) — checkedOf가 'mixed'를 내고 잔여는 그 값을 하나의
// 관찰 상태로 센다(토글형 = 관찰된 상태마다 click 1단위). step 1이 mixed에서, step 2가 true에서
// 눌렀으므로 헤더는 false 상태의 click만 남고, 행 2는 두 상태 다 남는다(검사기 포트와 같은 답).
test('fixture_doc_mixed_residual_counts_mixed_as_an_observed_state', () => {
  const doc = loadFixture('doc-mixed.json');
  assert.deepEqual(pure.requiredActions({ kind: 'checkbox' }, ['mixed', true, false, 'mixed']), [
    { action: 'click', option: 'mixed' },
    { action: 'click', option: true },
    { action: 'click', option: false },
  ]);
  assert.deepEqual(pure.residual(doc), [
    { target: 'row-1', action: 'click', option: false },
    { target: 'row-2', action: 'click', option: false },
    { target: 'row-2', action: 'click', option: true },
    { target: 'select-all', action: 'click', option: false },
  ]);
  assert.deepEqual([...pure.linkedSurfaces(doc)].sort(), []);
});

test('fixture_doc_cascade_residual_non_empty', () => {
  const doc = loadFixture('doc-cascade.json');
  const expectedResidual = [
    { target: 'item-a-busan', action: 'click', option: null },
    { target: 'item-b-jongno-seoul', action: 'click', option: null },
  ].sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)));
  const actual = [...pure.residual(doc)].sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)));
  assert.deepEqual(actual, expectedResidual);
  assert.deepEqual(
    [...pure.linkedSurfaces(doc)].sort(),
    ['surface-menu-a-open', 'surface-menu-b-seoul-open'].sort(),
  );
});
