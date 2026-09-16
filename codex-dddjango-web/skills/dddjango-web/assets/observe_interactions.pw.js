/* observe_interactions.pw.js — 조작 상태 수집 드라이버 본체 (dddjango-web).
 *
 * `export default async function observe(page, opts)` 하나가 Node 래퍼
 * (scripts/observe_interactions.mjs)와 MCP 트램폴린의 공용 진입점이다(K5).
 * 페이지 안 열거·identity·해시는 형제 파일 interaction_audit.js(스니펫)가 소유하고,
 * 이 파일은 값을 만들지 않는다 — 주입·기동·응답 바이트·크롭 캡처·문서 조립만 한다.
 *
 * 규범: workspace/design/2026-09-13-web-interaction-evidence.md
 *   K3(served 바이트·루트 규칙·viewport/crop·state_hash·수집기 sha)
 *   K5(실행 환경·모듈 해소·원격 URL 거부·exit 계약)
 *   K7(interactions.json version 1 — 문서 필드의 단일 출처)
 *
 * 실행 순서: prepare(+--resume 대조) → 응답 훅 → open → 스니펫 주입 → CDP 리스너 세션 →
 *            로드 실패 확인 → 루트 확인 → 안정 대기 → markCandidates + CDP 리스너 열거 +
 *            inventory → 로드 창 닫고 재확인 → served 대조 → initial(투영·해시·캡처) →
 *            exploreQueue(발견 조작·탐색·재생·조작·캡처) → 문서 쓰기 → 요약 반환.
 */
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const DRIVER_FILE = fileURLToPath(import.meta.url);
const DRIVER_NAME = 'observe_interactions.pw.js';
const SNIPPET_FILE = path.join(path.dirname(DRIVER_FILE), 'interaction_audit.js');
const LOOPBACK_HOSTS = ['127.0.0.1', 'localhost', '[::1]'];
const DEFAULT_LIMITS = { maxSteps: 8000, maxDepth: 24, maxMinutes: 90 };
const OPERATION_TIMEOUT_MS = 5000;
const NAVIGATION_TIMEOUT_MS = 15000;
// 워치독 유예 — 상한을 넘긴 뒤 정상 종료 경로가 끝날 시간을 준다. 이 안에도 못 끝나면
// 루프가 어딘가에 갇힌 것이므로 프로세스를 끝낸다(문서는 쓰지 않는다 · 아래 armWatchdog).
const WATCHDOG_GRACE_MS = 60000;

// 환경 오류 = 수집을 시작조차 못 한 조건(K5 exit 1). partial(exit 3)과 구별해야 하므로
// 별도 타입으로 던지고 observe가 잡아 요약에만 남긴다 — 문서는 쓰지 않는다.
class EnvironmentError extends Error {}

// `--max-steps`·`--max-minutes` 는 **항목 사이에서만** 재므로(capHit 호출 지점 넷 전부),
// 한 `await` 가 안 풀리면 상한이 영영 발화하지 않는다. `page.setDefaultTimeout` 이 그걸
// 막아 주지만 Playwright 의 `evaluate` 계열과 `CDPSession.send` 에는 **타임아웃 인자가
// 없다** — 그 22곳이 실제로 프로세스를 8시간 52분 세웠다(A8 실측 · CPU 0.0%).
//
// 막힐 수 있는 자리를 열거해 고치지 않는다. 열거는 다음 편집 한 줄로 다시 열린다
// (거부 목록이 완전할 수 없다는 v1.1.17 의 교훈과 같은 모양). 대신 그 계열을 **전부**
// 이 한 지점으로 통과시키고, 통과하지 않은 호출이 남으면 픽스처가 red 로 잡는다.
//
// 초과는 새 의미가 아니다 — 조작 예외와 같은 경로로 그 step 이 failed 가 되고 탐색은
// 계속된다(파일 머리의 타임아웃 주석이 이미 규정한 동작).
function withDeadline(promise, label, ms = OPERATION_TIMEOUT_MS) {
  let timer = null;
  const deadline = new Promise((_resolve, reject) => {
    timer = setTimeout(() => reject(new Error(`${label}: ${ms}ms 안에 반환하지 않았다`)), ms);
  });
  return Promise.race([promise, deadline]).finally(() => clearTimeout(timer));
}

// 종료 보증 — ① 이 놓친 자리가 생겨도 프로세스가 상한을 넘겨 살아남지 못한다.
//
// **문서는 쓰지 않는다.** 워치독이 도는 시점에 다른 async 작업이 `run.steps` 를 덧붙이거나
// 캡처 PNG 를 flush 하는 중일 수 있고, 그 상태로 쓰면 sha 가 실물과 어긋난 문서가 나온다.
// 그건 «막힌 것» 보다 나쁘다 — 막힘은 보이지만 어긋난 문서는 조용히 통과한다. `exit 1` 은
// 계약상 이미 «미실행» 이라 백스톱이 통과로 세지 않는다.
function armWatchdog(limits) {
  const budget = limits.maxMinutes * 60000 + WATCHDOG_GRACE_MS;
  const timer = setTimeout(() => {
    process.stderr.write(
      `[observe] 워치독: ${limits.maxMinutes}분 상한 + 유예 ${WATCHDOG_GRACE_MS / 1000}초를 넘겨도 `
      + '끝나지 않았다 — 루프가 반환하지 않는 await 에 갇혔다. 문서를 쓰지 않고 종료한다(미실행).\n');
    process.exit(1);
  }, budget);
  timer.unref?.();
  return () => clearTimeout(timer);
}

export default async function observe(page, opts) {
  let ctx = null;
  let disarm = null;
  try {
    // 조작·이동 타임아웃 — 상한(--max-steps/--max-minutes)은 항목 사이에서만 재므로,
    // 한 조작이 기본 30s를 끌면 도구 상한(600초) 분할 실행이 무너진다. 초과는 조작
    // 예외와 같은 경로로 그 step failed(재생 중이면 unreachable)가 되고 탐색은 계속된다.
    page.setDefaultTimeout(OPERATION_TIMEOUT_MS);
    page.setDefaultNavigationTimeout(NAVIGATION_TIMEOUT_MS);
    ctx = prepare(page, opts);
    disarm = armWatchdog(ctx.limits);
    watchResponses(ctx);
    watchLoadFailures(ctx);
    await open(ctx);
    await injectSnippet(ctx);
    await attachListenerSession(ctx);

    assertLoaded(ctx);
    await assertRootPresent(ctx);

    await waitStable(ctx);
    const snapshot = await inventorySnapshot(ctx);
    // pageerror 수집 창은 goto 시작부터 초기 인벤토리 완료까지다 — load 이벤트 뒤에
    // 터지는 렌더 예외(비동기 import·JSX 런타임)도 환경 오류로 잡기 위해서다.
    ctx.loadWindowOpen = false;
    assertLoaded(ctx);

    // 재개 대조는 initial 캡처 앞이다 — sha가 어긋난 실행이 동결된 initial PNG를
    // 덮어쓰면 안 된다(수정 라운드 1 m1).
    await Promise.all(ctx.servedPending);
    assertResumeServed(ctx);

    const initial = await recordInitial(ctx, snapshot);
    const explored = await exploreQueue(ctx, snapshot);

    await Promise.all(ctx.servedPending);
    const doc = buildDocument(ctx, initial, explored);
    writeDocument(ctx, doc);
    return summarize(ctx, doc, explored.steps, explored.partial, explored.capsHit, null);
  } catch (err) {
    if (err instanceof EnvironmentError) return summarize(null, null, [], false, [], err.message);
    throw err;
  } finally {
    if (disarm) disarm();   // 정상 종료 경로에서는 워치독이 프로세스를 잡고 있으면 안 된다
    // 예외로 빠져도 CDP 세션은 닫는다(수정 라운드 1 M7).
    if (ctx) await detachListenerSession(ctx);
  }
}

// ---------------------------------------------------------------------
// prepare — opts 해석·원격 URL 거부·수집기 바이트 sha·출력 경로.
// ---------------------------------------------------------------------
function prepare(page, opts) {
  const url = parseUrl(opts.url);
  const allowOrigin = opts.allowOrigin || null;
  if (!LOOPBACK_HOSTS.includes(url.hostname) && allowOrigin !== url.origin) {
    throw new EnvironmentError(`원격 URL 거부: ${url.origin}(loopback 아님 · --cdp origin과도 다름)`);
  }
  if (!opts.rootSelector) throw new EnvironmentError('루트 selector(--root)가 없다');
  if (!opts.out) throw new EnvironmentError('출력 경로(--out)가 없다');

  // 수집기 sha는 «지금 실행 중인 이 파일과 그 형제 스니펫»의 바이트다(K3 신뢰 경계) —
  // 해시 대상을 호출자가 바꾸는 손잡이는 두지 않는다(최종 리뷰 Minor 4).
  if (!fs.existsSync(SNIPPET_FILE)) throw new EnvironmentError(`스니펫을 찾을 수 없다: ${SNIPPET_FILE}`);

  const out = path.resolve(opts.out);
  const capturesDir = opts.capturesDir ? path.resolve(opts.capturesDir) : path.dirname(out);
  // browser_viewport는 실측값이다 — CLI 주장값(opts)은 viewportSize()가 없는
  // 컨텍스트(viewport: null)에서만 쓰는 폴백이다(수정 라운드 1 M9).
  const viewport = viewportOf(page) || opts.browserViewport;
  if (!viewport) throw new EnvironmentError('browser_viewport를 알 수 없다(--viewport 필요)');

  const ctx = {
    page,
    url,
    rootSelector: opts.rootSelector,
    snippetPath: SNIPPET_FILE,
    snippetSha: sha256File(SNIPPET_FILE),
    driverSha: sha256File(DRIVER_FILE),
    pure: createRequire(import.meta.url)(SNIPPET_FILE),
    out,
    capturesDir,
    buildDir: path.dirname(capturesDir),
    screen: screenNameOf(out),
    cropToRoot: opts.cropToRoot === true,
    viewport,
    entrypointSha: opts.entrypointSha || '',
    archiveSha: opts.archiveSha || '',
    declared: opts.declared || [],
    excludedRegions: opts.excludedRegions || [],
    hoverSelectors: opts.hoverSelectors || [],
    collectorPath: opts.path || 'node',
    listeners: opts.listeners || 'cdp',
    capabilities: { react_props: true, cdp_listeners: false },
    cdp: null,
    discoveryLimits: [],
    limitKeys: new Set(),
    sweepNotes: new Map(), // dom_path → {states, reason} — 훑기 한계 행 1개를 갱신한다(B2)
    limits: {
      maxSteps: numberOr(opts.maxSteps, DEFAULT_LIMITS.maxSteps),
      maxDepth: numberOr(opts.maxDepth, DEFAULT_LIMITS.maxDepth),
      maxMinutes: numberOr(opts.maxMinutes, DEFAULT_LIMITS.maxMinutes),
    },
    resume: opts.resume === true,
    entryDir: path.posix.dirname(url.pathname),
    served: {},
    servedPending: [],
    targets: {},
    prior: null,
    loadWindowOpen: false,
    loadError: null,
    crop: null,
  };
  ctx.prior = loadPrior(ctx);
  if (ctx.prior) {
    Object.assign(ctx.targets, ctx.prior.targets);
    // 앞선 실행이 적은 한계는 그대로 잇는다 — 이번 실행에서 같은 한계를 다시 만나도
    // 행이 겹치지 않는다(같은 kind·dom_path는 한 번만).
    for (const row of ctx.prior.limits) noteLimit(ctx, row.kind, row.dom_path, row.reason);
  }
  return ctx;
}

// ---------------------------------------------------------------------
// --resume — "같은 --out의 큐·steps를 이어서 실행한다(archive/served sha가 같을
// 때만)"(K1). 문서를 쓰지 않는 환경 오류(exit 1)로 막아야 기존 문서가 남는다.
// ---------------------------------------------------------------------
function loadPrior(ctx) {
  if (!ctx.resume || !fs.existsSync(ctx.out)) return null;
  let doc;
  try {
    doc = JSON.parse(fs.readFileSync(ctx.out, 'utf8'));
  } catch (err) {
    throw new EnvironmentError(`재개 대조 실패: 기존 문서를 읽을 수 없다(${err.message})`);
  }
  if (doc.archive_sha256 !== ctx.archiveSha) {
    throw new EnvironmentError(`재개 대조 실패: archive sha 불일치(${doc.archive_sha256} ≠ ${ctx.archiveSha})`);
  }
  const priorEntrypoint = doc.entrypoint ? doc.entrypoint.sha256 : '';
  if (priorEntrypoint !== ctx.entrypointSha) {
    throw new EnvironmentError(`재개 대조 실패: entrypoint sha 불일치(${priorEntrypoint} ≠ ${ctx.entrypointSha})`);
  }
  const steps = Array.isArray(doc.steps) ? doc.steps : [];
  return {
    steps,
    targets: doc.targets || {},
    served: doc.served || {},
    limits: Array.isArray(doc.discovery_limits) ? doc.discovery_limits : [],
    initialHash: doc.initial ? doc.initial.state_hash : null,
    lastStep: steps.reduce((last, step) => Math.max(last, step.n || 0), 0),
  };
}

// served는 페이지를 연 뒤에야 채워진다 — 같은 경로의 바이트가 달라졌으면 이어
// 달릴 수 없다(다른 화면의 step을 한 문서에 섞는 셈이다).
function assertResumeServed(ctx) {
  if (!ctx.prior) return;
  for (const [local, sha] of Object.entries(ctx.prior.served)) {
    const now = ctx.served[local];
    if (now !== undefined && now !== sha) {
      throw new EnvironmentError(`재개 대조 실패: served sha 불일치(${local})`);
    }
  }
}

function parseUrl(raw) {
  try {
    return new URL(raw);
  } catch (err) {
    throw new EnvironmentError(`URL을 해석할 수 없다: ${raw}`);
  }
}

function viewportOf(page) {
  const size = page.viewportSize();
  return size ? [size.width, size.height] : null;
}

// `<screen>-interactions.json` → `<screen>`. 캡처 파일 이름의 접두사가 된다.
function screenNameOf(out) {
  return path.basename(out).replace(/-interactions\.json$/, '').replace(/\.json$/, '');
}

function numberOr(value, fallback) {
  const n = Number(value);
  return Number.isFinite(n) && n > 0 ? n : fallback;
}

// ---------------------------------------------------------------------
// served — "드라이버가 entrypoint 응답과 same-origin 2xx 자원의
// served: {local_path: sha256}를 기록한다"(K3). local_path는 entrypoint
// 디렉터리 기준 상대 경로를 percent-decode한 값이다.
// ---------------------------------------------------------------------
function watchResponses(ctx) {
  ctx.page.on('response', (response) => {
    const status = response.status();
    // 204·205는 본문이 없는 2xx다 — 빈 바이트 sha를 남기면 manifest와 매칭될 수 없는
    // 위양성 행이 된다(수정 라운드 1 M1).
    if (status < 200 || status >= 300 || status === 204 || status === 205) return;
    let resourceUrl;
    try {
      resourceUrl = new URL(response.url());
    } catch (err) {
      return;
    }
    if (resourceUrl.origin !== ctx.url.origin) return;
    ctx.servedPending.push(
      response
        .body()
        .then((body) => {
          ctx.served[localPathOf(ctx, resourceUrl)] = sha256Buffer(body);
        })
        // 본문을 돌려주지 않는 응답(중단·캐시 전용)은 대조 밖이다 — 검사기가
        // entrypoint·manifest 대조에서 누락을 잡는다.
        .catch(() => {}),
    );
  });
}

function localPathOf(ctx, resourceUrl) {
  return decodeURIComponent(path.posix.relative(ctx.entryDir, resourceUrl.pathname));
}

// "외부 스크립트(unpkg 런타임 등) 로드 실패는 environment_error로 기록하고
// 검사기는 partial과 구별해 exit 1(미실행)로 낸다"(K2). 전송 실패(requestfailed)와
// HTTP 오류(4xx·5xx)는 다른 이벤트로 오므로 둘 다 본다 — 404로 번들이 안 오는 것이
// 가장 흔한 실패 모드인데 requestfailed만 보면 그물 밖이다(수정 라운드 1 I-2).
function watchLoadFailures(ctx) {
  ctx.page.on('response', (response) => {
    if (response.request().resourceType() !== 'script' || response.status() < 400) return;
    recordLoadError(ctx, `스크립트 로드 실패: ${response.url()} ${response.status()}`);
  });
  ctx.page.on('requestfailed', (request) => {
    if (request.resourceType() !== 'script') return;
    const failure = request.failure();
    recordLoadError(ctx, `스크립트 로드 실패: ${request.url()} ${failure ? failure.errorText : '사유 불명'}`);
  });
  ctx.page.on('pageerror', (error) => {
    if (!ctx.loadWindowOpen) return;
    recordLoadError(ctx, `로드 중 페이지 오류: ${error.message}`);
  });
}

function recordLoadError(ctx, message) {
  if (!ctx.loadError) ctx.loadError = message;
}

function assertLoaded(ctx) {
  if (ctx.loadError) throw new EnvironmentError(ctx.loadError);
}

async function open(ctx) {
  ctx.loadWindowOpen = true;
  try {
    await ctx.page.goto(ctx.url.href, { waitUntil: 'load' });
  } catch (err) {
    throw new EnvironmentError(`페이지 열기 실패: ${ctx.url.href}(${err.message})`);
  }
}

// 루트 확인은 인벤토리보다 앞이다 — 로드 실패를 «루트 미발견»으로 오진하지 않도록
// assertLoaded 뒤에 두고, dom.inventory와 같은 querySelector로 본다(K3 루트 규칙).
async function assertRootPresent(ctx) {
  const found = await withDeadline(ctx.page.evaluate(
    (selector) => document.querySelector(selector) !== null, ctx.rootSelector,
  ), 'ctx.page.evaluate');
  if (!found) throw new EnvironmentError(`루트 selector를 찾지 못했다: ${ctx.rootSelector}`);
}

async function injectSnippet(ctx) {
  try {
    await ctx.page.addScriptTag({ path: ctx.snippetPath });
  } catch (err) {
    throw new EnvironmentError(`스니펫 주입 실패: ${ctx.snippetPath}(${err.message})`);
  }
}

// ---------------------------------------------------------------------
// CDP 리스너 열거 — "감지: … CDP DOMDebugger.getEventListeners(click·mousedown·
// pointerdown·keydown·change·input)"(K2). `dom.markCandidates`가 심은
// `el.__iaIndex`를 키로 `index → [type]` 표를 만들어 `dom.inventory`에 넘긴다.
// 표식은 인벤토리마다 다시 심기므로(스니펫 계약) 매핑도 인벤토리마다 다시 한다.
//
// 열거는 «표식 배열 한 번 + 대상마다 getEventListeners»다. 브리프가 적은
// DOM.getDocument → querySelectorAll → resolveNode → callFunctionOn 경로는 같은 표를
// 만들지만 픽스처 실측으로 56~82ms(노드 95)이고 이 경로는 16~18ms(대상 72)다. 노드마다
// 왕복 3회가 1회로 줄고, 루트 밖 포털 오버레이와 same-origin iframe 문서의 표식까지
// markCandidates와 **같은 집합**으로 덮는다(보고서 §CDP 매핑 비용).
// ---------------------------------------------------------------------
const MARKED_ELEMENTS = ['(function(){var out=[];function walk(doc){',
  "var all=doc.querySelectorAll('*');for(var i=0;i<all.length;i++){var el=all[i];",
  "if(typeof el.__iaIndex==='number')out[el.__iaIndex]=el;",
  "if(el.tagName==='IFRAME'){var sub=null;try{sub=el.contentDocument}catch(e){}if(sub)walk(sub);}}}",
  'walk(document);return out})()'].join('');
const INDEX_KEY = /^\d+$/;
const LISTENER_OBJECT_GROUP = 'dddjango-web-interaction-listeners';

async function attachListenerSession(ctx) {
  if (ctx.listeners !== 'cdp') return;
  try {
    ctx.cdp = await ctx.page.context().newCDPSession(ctx.page);
    ctx.capabilities.cdp_listeners = true;
  } catch (err) {
    dropListenerSession(ctx, err);
  }
}

// "CDP가 없을 때만" cursor 보조가 켜진다(K2) — 스니펫이 `capabilities`를 보고 채널을
// 바꾸므로, 여기서 내려 두면 열거 규칙도 같이 바뀐다.
function dropListenerSession(ctx, err) {
  const session = ctx.cdp;
  ctx.cdp = null;
  ctx.listeners = 'none';
  ctx.capabilities.cdp_listeners = false;
  // 세션이 살아 있을 수도 있다(도메인만 막힌 경우) — detach를 시도한 뒤 버린다.
  // 여기서 ctx.cdp를 비우므로 observe의 finally(detachListenerSession)는 닿지 못한다(3c 재리뷰 Minor).
  if (session) session.detach().catch(() => {});
  process.stderr.write(`CDP 리스너 열거를 쓸 수 없다(${err.message}) — cursor 보조로 내려간다\n`);
}

async function detachListenerSession(ctx) {
  if (!ctx.cdp) return;
  const session = ctx.cdp;
  ctx.cdp = null;
  await session.detach().catch(() => {});
}

async function listenerIndexesOf(ctx) {
  if (!ctx.cdp) return null;
  try {
    const evaluated = await withDeadline(ctx.cdp.send('Runtime.evaluate', {
      expression: MARKED_ELEMENTS, objectGroup: LISTENER_OBJECT_GROUP,
    }), 'ctx.cdp.send');
    const arrayId = evaluated.result ? evaluated.result.objectId : null;
    if (!arrayId) return null;
    const props = await withDeadline(ctx.cdp.send('Runtime.getProperties', { objectId: arrayId, ownProperties: true }), 'ctx.cdp.send');
    const table = {};
    for (const prop of props.result) {
      if (!INDEX_KEY.test(prop.name) || !prop.value || !prop.value.objectId) continue;
      const listed = await withDeadline(ctx.cdp.send('DOMDebugger.getEventListeners', { objectId: prop.value.objectId }), 'ctx.cdp.send');
      if (listed.listeners.length > 0) table[prop.name] = listed.listeners.map((row) => row.type);
    }
    return table;
  } catch (err) {
    // 세션이 끊겼거나(page 종료·원격 제한) 도메인이 막혔다 — 남은 실행은 cursor 보조로 간다.
    dropListenerSession(ctx, err);
    return null;
  } finally {
    // 배열과 원소 핸들이 한 그룹에 들어가므로 한 번에 놓아준다 — 인벤토리마다 쌓이는
    // 원격 핸들을 남기지 않는다(수정 라운드 1 M5 · 해제 뒤 원소 사용 불가를 실측).
    if (ctx.cdp) {
      await withDeadline(ctx.cdp.send('Runtime.releaseObjectGroup', { objectGroup: LISTENER_OBJECT_GROUP }), 'ctx.cdp.send').catch(() => {});
    }
  }
}

// ---------------------------------------------------------------------
// inventorySnapshot — markCandidates → CDP 리스너 열거 → inventory.
// state_hash·surface_key는 스니펫의 순수 함수가 **페이지 안에서** 생 엔트리로
// 계산한다(엔트리가 identity 원본 4필드를 갖는 것은 스니펫의 계약이다).
// ---------------------------------------------------------------------
async function inventorySnapshot(ctx) {
  await withDeadline(ctx.page.evaluate(
    (rootSelector) => globalThis.__interactionAudit.dom.markCandidates(rootSelector),
    ctx.rootSelector,
  ), 'ctx.page.evaluate');
  const listenerIndexes = await listenerIndexesOf(ctx);
  const snapshot = await withDeadline(ctx.page.evaluate(
    ([rootSelector, invOpts, url]) => {
      const audit = globalThis.__interactionAudit;
      const inv = audit.dom.inventory(rootSelector, invOpts);
      return {
        inventory: inv,
        state_hash: audit.stateHash(inv.entries, url),
        surface_key: audit.surfaceKey(inv.entries),
      };
    },
    [ctx.rootSelector, inventoryOptions(ctx, listenerIndexes), ctx.url.href],
  ), 'ctx.page.evaluate');
  noteLimits(ctx, snapshot.inventory.limits);
  return snapshot;
}

// declared·excludedRegions는 둘 다 {selector, reason} 행이다(K3 "excluded_regions
// (selector·사유) 선언"). 스니펫의 outside_root 스캔은 selector만 쓰므로 여기서 벗긴다.
function inventoryOptions(ctx, listenerIndexes) {
  return {
    declared: ctx.declared,
    excludedRegions: ctx.excludedRegions.map((row) => row.selector),
    hoverSelectors: ctx.hoverSelectors,
    listenerIndexes: listenerIndexes || null,
    capabilities: ctx.capabilities,
  };
}

// ---------------------------------------------------------------------
// discovery_limits — "cross-origin iframe·가상화 목록의 DOM 밖 항목은 수집 완료가
// 아니며 discovery_limits가 비어 있지 않으면 리뷰어 항목이다"(K2). 스니펫이 낸 한계
// (접근 불가 프레임)와 드라이버가 스크롤한 overflow 컨테이너를 같은 행 모양
// {kind, dom_path, reason}으로 모은다 — 같은 kind·dom_path는 한 번만 적는다.
// ---------------------------------------------------------------------
const LIMIT_REASONS = {
  'cross-origin-iframe': '접근할 수 없는 프레임 — 안쪽 대상을 열거하지 못했다',
};

// 스니펫 dom_path는 루트 자식 경로라 루트 자신은 ''이다(루트가 overflow 컨테이너인 긴 모바일
// 화면) — 문서 행에는 '.'(루트 자체)로 적는다. 검사기는 kind·dom_path·reason 전부 nonempty를
// 요구하므로 ''는 거짓 결함(exit 2)이 된다(최종 리뷰 검사기 I1). 스크롤 손잡이(scrollByDomPath)는
// 스니펫 값 ''를 그대로 쓴다 — 여기서는 문서 행의 키·값만 바꾼다.
function limitPathOf(domPath) {
  return domPath === '' ? '.' : domPath;
}

function noteLimit(ctx, kind, domPath, reason) {
  const rowPath = limitPathOf(domPath);
  const key = `${kind}\n${rowPath}`;
  if (ctx.limitKeys.has(key)) return;
  ctx.limitKeys.add(key);
  ctx.discoveryLimits.push({ kind, dom_path: rowPath, reason });
}

// 갱신 경로 — 앞 슬라이스가 상한에 걸려 적은 «미실행» 행은 `--resume`이 그대로 이어싣는데
// (loadPrior), 이번 슬라이스가 그 발견을 실제로 열면 거짓이 된다(3c 재리뷰 N-3). 그래서
// 여는 자리에서 같은 kind+dom_path 행을 지운다 — 스크롤은 곧바로 성공·실패 사유를 다시
// 적고(dedup이 풀렸으므로 기록된다), hover는 discovery step 자체가 증거다.
function dropLimit(ctx, kind, domPath) {
  const rowPath = limitPathOf(domPath);
  if (!ctx.limitKeys.delete(`${kind}\n${rowPath}`)) return;
  const at = ctx.discoveryLimits.findIndex((row) => row.kind === kind && row.dom_path === rowPath);
  if (at !== -1) ctx.discoveryLimits.splice(at, 1);
}

function noteLimits(ctx, rows) {
  for (const row of rows || []) {
    noteLimit(ctx, row.kind, row.dom_path, LIMIT_REASONS[row.kind] || '수집 한계');
  }
}

// 훑기 한계 행 — 같은 컨테이너를 여러 상태에서 훑어도(드라이런 6차 결정 B2) 행은
// dom_path당 하나이고 사유에 훑은 상태 수가 누적된다. 사유는 **«중단»이 이긴다**: 어느
// 상태에서든 한 번 잘렸으면(상한·드리프트·페이지 상한) 그 사실이 리뷰어가 볼 것이고,
// 다른 상태를 완주했다는 말이 그것을 덮어서는 안 된다. 같은 등급이면 첫 사유를 지킨다.
function noteSweep(ctx, domPath, reason, stopped) {
  const note = ctx.sweepNotes.get(domPath) || { states: 0, reason: null, stopped: false };
  note.states += 1;
  if (note.reason === null || (stopped && !note.stopped)) {
    note.reason = reason;
    note.stopped = stopped === true;
  }
  ctx.sweepNotes.set(domPath, note);
  dropLimit(ctx, 'scroll-container', domPath);
  noteLimit(ctx, 'scroll-container', domPath, `${note.reason}(훑은 상태 ${note.states})`);
}

// ---------------------------------------------------------------------
// initial — 인벤토리 투영·해시·루트 크롭 캡처. content_crop은 --crop-root면
// 루트 rect, 아니면 브라우저 viewport 전체다(K3 "viewport와 crop을 따로 기록").
// ---------------------------------------------------------------------
async function recordInitial(ctx, snapshot) {
  const inv = snapshot.inventory;
  ctx.crop = ctx.cropToRoot
    ? Object.assign({}, inv.root.fingerprint.rect)
    : { x: 0, y: 0, w: ctx.viewport[0], h: ctx.viewport[1] };
  mergeTargets(ctx, inv.targets, 0);
  return {
    root: inv.root,
    outside_root: inv.outside_root,
    declared_unmatched: inv.declared_unmatched,
    block: {
      inventory: projectEntries(inv.entries, inv.entry_doc_fields),
      state_hash: snapshot.state_hash,
      surface_key: snapshot.surface_key,
      capture: await capture(ctx, 'initial'),
    },
  };
}

// clip은 캡처 시점마다 다시 잰다 — 스크롤 잠금·레이아웃 변화로 루트가 움직여도
// 그 상태를 실제로 담기 위해서다. 루트가 뷰포트 안에 들어가면 뷰포트 좌표로 찍고
// (position:fixed 오버레이가 제자리에 남는다), 넘칠 때만 fullPage + 문서 좌표를 쓴다
// (clip만으로는 뷰포트 폭에서 잘림을 실측 — 수정 라운드 1 I-4).
async function captureClipOf(ctx) {
  const view = await withDeadline(ctx.page.evaluate(
    (selector) => {
      const el = selector ? document.querySelector(selector) : null;
      const rect = el ? el.getBoundingClientRect() : null;
      return {
        scrollX: window.scrollX,
        scrollY: window.scrollY,
        rect: rect
          ? { x: Math.round(rect.left), y: Math.round(rect.top), w: Math.round(rect.width), h: Math.round(rect.height) }
          : null,
      };
    },
    ctx.cropToRoot ? ctx.rootSelector : null,
  ), 'ctx.page.evaluate');
  const rect = view.rect || { x: 0, y: 0, w: ctx.viewport[0], h: ctx.viewport[1] };
  const fits = rect.w <= ctx.viewport[0] && rect.h <= ctx.viewport[1];
  return {
    fullPage: !fits,
    clip: {
      x: fits ? rect.x : rect.x + view.scrollX,
      y: fits ? rect.y : rect.y + view.scrollY,
      width: rect.w,
      height: rect.h,
    },
  };
}

async function capture(ctx, name) {
  fs.mkdirSync(ctx.capturesDir, { recursive: true });
  const file = path.join(ctx.capturesDir, `${ctx.screen}-${name}.png`);
  const shot = await captureClipOf(ctx);
  const bytes = await ctx.page.screenshot({ fullPage: shot.fullPage, clip: shot.clip });
  fs.writeFileSync(file, bytes);
  return { path: relativePosix(ctx.buildDir, file), sha256: sha256Buffer(bytes) };
}

// ---------------------------------------------------------------------
// 문서 투영 — "인벤토리 항목은 위 8필드로 고정하며 스니펫이 런타임에 쓰는
// kind·rect·dom_path는 드라이버가 문서에 쓰기 전에 제거한다"(K7).
// ---------------------------------------------------------------------
function projectEntries(entries, fields) {
  return entries.map((entry) => {
    const row = {};
    for (const field of fields) row[field] = entry[field];
    return row;
  });
}

// targets는 실행 전체에 걸쳐 누적되고 first_seen_step은 처음 본 step 번호다
// (initial에서 본 대상은 0). 이미 있는 id는 덮어쓰지 않는다.
function mergeTargets(ctx, invTargets, stepNumber) {
  for (const [id, target] of Object.entries(invTargets)) {
    if (ctx.targets[id]) continue;
    ctx.targets[id] = projectTarget(target, stepNumber);
  }
}

function projectTarget(target, firstSeenStep) {
  const row = {
    role: target.role, name: target.name, input_type: target.input_type, owner: target.owner,
    owner_items_hash: target.owner_items_hash, dom_path: target.dom_path, kind: target.kind,
    first_seen_step: firstSeenStep, declared: target.declared, found_by: target.found_by,
    live: target.live,
  };
  // "종류별 선택 필드는 둘뿐이다: native select 옵션 target의 value,
  // overlay target의 scrim"(K7).
  if (target.value !== undefined) row.value = target.value;
  if (target.scrim !== undefined) row.scrim = target.scrim;
  return row;
}

// ---------------------------------------------------------------------
// exploreQueue — "큐(실행) 키 = (identity, action, option, context_T)"(K1).
// 항목은 자기가 발견된 상태의 해시(prefixHash)와 거기까지의 재생 경로(ops)를 든다.
//
// 꺼내는 순서: ① 아직 한 번도 executed된 적 없는 단위 ② 그중 재생이 필요 없는 것
// ③ 그 밖에는 가장 최근에 들어온 것. 잔여(검사기 판정)를 가장 빨리 0으로 만드는
// 순서다 — 상태 차원이 곱해지는 화면에서 큐는 상한 전에 마르지 않으므로, 무엇을
// 먼저 실행하는가가 곧 «상한 안에서 무엇을 증명하는가»다.
// ---------------------------------------------------------------------
async function exploreQueue(ctx, snapshot) {
  const run = {
    queue: [],
    seen: new Set(),            // 큐 키 — 같은 키는 한 번만 실행한다
    executedUnits: new Set(),   // (identity, action, option) — 잔여가 세는 단위
    steps: ctx.prior ? ctx.prior.steps.slice() : [],
    stepNo: ctx.prior ? ctx.prior.lastStep : 0,
    capsHit: [],
    depthBlocked: new Set(), // 깊이 상한에 막혀 넣지 못한 큐 키 — 더 얕은 경로로 들어오면 뺀다
    discovered: new Set(),   // 이미 연 발견 후보(hover는 identity, 스크롤은 dom_path)
    // D-F 우선순위 카운터 — 전부 steps에서 재구성할 수 있다(restoreVisited).
    executedFaces: new Map(),   // identity → 실행된 «직전 트리거 face» 집합(② D-F′)
    fillRuns: new Map(),        // identity → executed fill step 수(②b 상한 — D-K)
    executedByState: new Map(),  // 접두 상태 해시 → 그 상태에서 실행된 step 수(④ 공정성)
    sameStateRun: 0,             // 같은 접두 상태에서 연속으로 꺼낸 수(③ 소진 방지)
    lastPrefixHash: null,
    startedAt: Date.now(),
    current: snapshot,          // 페이지가 지금 놓인 상태(null이면 모른다 → 재생)
    currentPath: [],            // 그 상태에 이른 대상 id 계보(D-G) — null이면 모른다
    pageClosed: false,          // D-I — 페이지가 사라져 멈췄다(큐가 비어도 완주가 아니다)
  };
  if (ctx.prior) restoreVisited(ctx, run, ctx.prior.steps);
  enqueueFrom(ctx, run, snapshot.inventory.entries, snapshot.inventory.targets, snapshot.state_hash, []);
  if (ctx.prior) restoreStates(ctx, run);
  run.current = await unlessClosed(ctx, run, () => discover(ctx, run, snapshot, []));
  if (!run.current) run.currentPath = null;

  while (run.queue.length > 0) {
    // D-I — 페이지가 사라진 뒤로는 아무것도 관찰할 수 없다. 남은 큐를 «갈 수 없는 곳»으로
    // 비우면 문서가 partial:false로 완주처럼 보이고(6차 실측: 브라우저가 죽은 뒤 2470건이
    // 1초 만에 unreachable로 쌓이고 exit 0) `--resume`도 그 키를 이미 본 것으로 여겨 영영
    // 건너뛴다. 큐를 그대로 둔 채 멈추면 partial:true가 되고 재개가 이어 간다.
    // 여기서 보므로 발견 조작 중에 닫힌 경우도 한 자리에서 잡힌다.
    if (pageGone(ctx, run)) break;
    const cap = capHit(ctx, run);
    if (cap) {
      noteCap(run, cap);
      break;
    }
    await unlessClosed(ctx, run, () => runItem(ctx, run, takeNext(ctx, run)));
  }
  if (run.depthBlocked.size > 0) noteCap(run, 'max_depth');
  return {
    steps: run.steps,
    capsHit: run.capsHit,
    // 큐가 남았거나, 깊이 상한에 막혀 끝내 넣지 못한 키가 있거나, 어떤 상한이든 한
    // 번이라도 걸렸으면 완주가 아니다(K3 반례 "partial:false인데 caps_hit≠[]"와 짝이
    // 맞아야 한다 — 발견 조작이 상한에 잘린 실행이 여기에 해당한다). 페이지가 사라져 멈춘
    // 실행도 완주가 아니다 — 닫는 조작이 큐의 마지막 항목이면 큐가 비어 루프가 정상 종료하지만
    // 그 step 뒤의 발견 조작은 열어 보지 못했다(4d 재리뷰 Minor 1).
    partial: run.pageClosed || run.queue.length > 0 || run.depthBlocked.size > 0 || run.capsHit.length > 0,
  };
}

// "--max-minutes(기본 90)·--max-steps(기본 8000)·--max-depth(기본 24). 도달하면
// partial:true·caps_hit"(K1). max_steps는 문서 전체 step 수 기준이라 --resume이
// 같은 상한을 다시 만나지 않는다.
function capHit(ctx, run) {
  if (run.steps.length >= ctx.limits.maxSteps) return 'max_steps';
  if (Date.now() - run.startedAt >= ctx.limits.maxMinutes * 60000) return 'max_minutes';
  return null;
}

// D-I — 페이지가 사라진 뒤의 실패는 «조작이 안 됐다»가 아니라 «관찰이 끊겼다»다. 판정은
// Playwright 메시지 파싱이 아니라 `isClosed()`로 하고(문구 의존 금지), 사유는 원문을 달고
// 다시 적는다. `--resume`이 이 접두로 «한 번은 다시 시도할 단위»를 가른다(restoreVisited).
const PAGE_CLOSED_PREFIX = '페이지가 닫혔다: ';

// 페이지가 사라졌는가 — 참이면 이 실행은 그 자리에서 끝나고 완주가 아니다(`run.pageClosed`).
// 닫힘 step을 적는 자리(stepError)·루프·발견 조작 예외가 모두 이 하나로 판정한다.
function pageGone(ctx, run) {
  if (!ctx.page.isClosed()) return false;
  run.pageClosed = true;
  return true;
}

function stepError(ctx, run, message) {
  return pageGone(ctx, run) ? `${PAGE_CLOSED_PREFIX}${message}` : message;
}

// 발견 조작(스크롤 훑기·hover)·조작 직전 확인·재생은 step 밖에서 page.evaluate를 부른다 — 그 사이에
// 페이지가 사라지면 Playwright 예외가 observe 밖으로 새어 문서가 아예 쓰이지 않는다(4d 재리뷰 범위
// 밖 2). 닫힌 페이지의 예외만 삼키고(루프는 pageGone으로 멈춘다) 다른 예외는 그대로 낸다.
async function unlessClosed(ctx, run, work) {
  try {
    return await work();
  } catch (err) {
    if (pageGone(ctx, run)) return null;
    throw err;
  }
}

// 같은 상한을 두 번 적지 않는다 — 탐색 루프와 발견 조작이 같은 cap을 함께 만난다.
function noteCap(run, cap) {
  if (!run.capsHit.includes(cap)) run.capsHit.push(cap);
}

// 우선순위(드라이런 4차 결정 D-F — 위에서부터 첫 차이로 결정한다):
// ① 아직 executed된 적 없는 단위(잔여를 먼저 0으로 만든다)
// ② 트리거(select/combobox)의 **한 번도 실행되지 않은 context_T** — cascade 발견의 자리다.
//    4차 실측: «시·도=X 뒤의 시·군» 키 16개가 끝내 미실행이었다. 그 항목은 단위로는
//    이미 실행돼 ①에서 밀리고, 얕은 폼 재실행이 ③⑤⑥를 계속 이겨 큐에서 굶는다.
// ②b 빈 입력(value_empty=true)의 fill — **진행 조건**이다(6차 결정 O1). 6차 실측:
//    다른 화면에서 같은 identity의 이름 fill이 이미 실행돼 ①을 잃은 탓에, 등록 흐름의
//    빈 이름이 «다음» 재실행에 계속 밀려 단계 2에 이르지 못했다. 채우지 않으면 그 흐름의
//    뒤 상태는 아예 열리지 않으므로 ③(재생 비용)보다 앞에 둔다. 단 **identity당 executed
//    fill 수가 EMPTY_FILL_PRIORITY_CAP(2) 미만일 때만**이다(8차 결정 D-K — 빈 «메모» fill이
//    새 상태마다 최우선으로 179회 재실행돼 슬라이스의 80%를 먹었다).
// ③ 재생이 필요 없는 항목(같은 상태에서 이어 하는 조작 — 재생 비용 0). 단 같은 접두
//    상태에서 연속 NO_REPLAY_STREAK개를 꺼냈으면 이 우선권을 잃는다(한 상태 안 소진 방지).
// ④ 접두 상태별 공정성 — 그 상태에서 실행된 step이 가장 적은 항목(상태를 고루 돈다).
//    «단위 총 실행 수 오름차순»(8차 결정 D-K ④a)은 두지 않는다 — 9차 실측: «다음»·«이전»처럼
//    정당하게 실행 수가 커지는 진행 버튼이 뒤로 밀려 폼 3단계 이후가 열리지 않았다(D-K′).
// ⑤ 경로가 짧은 항목(재생 비용이 작다) ⑥ 늦게 들어온 항목(막 발견한 cascade 자식).
// 같은 입력이면 같은 순서다(결정적) — 카운터는 `--resume`이 steps에서 재구성한다.
const NO_REPLAY_STREAK = 5;
const TRIGGER_KINDS = { trigger: 1, select: 1 };
// ②b — "빈 입력(value_empty === true)의 fill"(O1). select 가지는 두지 않는다(컨트롤러
// 판정): select 단위는 언제나 kind `option` 대상에 붙으므로 «kind가 select인 select 항목»은
// 구조적으로 없고, value_empty도 텍스트 입력에만 있다.
const EMPTY_INPUT_KINDS = { input: 1, textarea: 1 };

function takeNext(ctx, run) {
  const currentHash = run.current ? run.current.state_hash : null;
  const streakOver = run.sameStateRun >= NO_REPLAY_STREAK;
  const rankOf = (item) => [
    run.executedUnits.has(item.unitKey) ? 1 : 0,
    newTriggerFace(ctx, run, item) ? 0 : 1,
    emptyInputPriority(ctx, run, item) ? 0 : 1,
    !streakOver && freeToRun(run, item, currentHash) ? 0 : 1,
    run.executedByState.get(item.prefixHash) || 0,
    item.ops.length,
  ];
  let best = 0;
  let bestRank = rankOf(run.queue[0]);
  for (let i = 1; i < run.queue.length; i += 1) {
    const rank = rankOf(run.queue[i]);
    if (compareRanks(rank, bestRank) <= 0) { // 같으면 나중에 들어온 항목이 이긴다(⑥)
      best = i;
      bestRank = rank;
    }
  }
  const item = run.queue.splice(best, 1)[0];
  run.sameStateRun = item.prefixHash === run.lastPrefixHash ? run.sameStateRun + 1 : 1;
  run.lastPrefixHash = item.prefixHash;
  return item;
}

function compareRanks(rank, top) {
  for (let i = 0; i < rank.length; i += 1) {
    if (rank[i] !== top[i]) return rank[i] - top[i];
  }
  return 0;
}

// ③ «재생이 필요 없다»는 D-G 이후 «해시 일치 ∧ 계보 일치»다(리뷰 I-1) — 해시만 보면 계보가 달라
// 어차피 재생될 항목이 진짜 무료 항목을 ⑤(짧은 경로)에서 이겨, 같은 순간에 재생이 체계적으로
// 먼저 꺼내진다. 두 값 모두 pop 시점에 이미 손에 있다(`run.currentPath`는 `run.current`와 같은
// 라이브 상태라 결정성·재개 요건도 같다).
function freeToRun(run, item, currentHash) {
  return item.prefixHash === currentHash && samePath(run.currentPath, item.ops);
}

// ②는 «대상 T 바로 앞(문서 순서) 트리거의 face가 T에서 처음 보는 값»일 때만이다
// (D-F′ — 4b 리뷰 I3 Ruling). cascade는 직전 트리거에 의존한다는 근사다: 모든 새 context_T를
// ②로 올리면 트리거의 face·활성 집합 조합만큼 공급이 불어나 ②가 큐를 지배한다(A8 이론
// 조합 8×12×17 = 1,632). 직전 트리거 face로 좁히면 같은 화면에서 17개로 줄고, 그 밖의 새
// context 항목은 ③④로 내려간다(K1 큐 키·잔여 정의는 그대로다).
function newTriggerFace(ctx, run, item) {
  const target = ctx.targets[item.target];
  if (!target || !TRIGGER_KINDS[target.kind]) return false;
  const seen = run.executedFaces.get(item.target);
  return !seen || !seen.has(item.priorFace);
}

// D-F·D-K 카운터 갱신 — executed step 하나가 «그 대상의 직전 트리거 face»(②)·«그 접두 상태의
// 실행 수»(④)·«그 identity의 fill 실행 수»(②b 상한)를 함께 늘린다. `unit`은 큐 항목(라이브)이거나
// step에서 재구성한 같은 모양({target, action, priorFace})이다. 발견(hover) step은 필요 조작이
// 아니므로 세지 않는다(4b 리뷰 I1). `restoreVisited`가 앞선 슬라이스의 steps로 같은 값을 되살린다.
function noteExecuted(run, unit, prefixHash) {
  const faces = run.executedFaces.get(unit.target) || new Set();
  faces.add(unit.priorFace === undefined ? null : unit.priorFace);
  run.executedFaces.set(unit.target, faces);
  if (prefixHash) run.executedByState.set(prefixHash, (run.executedByState.get(prefixHash) || 0) + 1);
  if (unit.action === 'fill') run.fillRuns.set(unit.target, (run.fillRuns.get(unit.target) || 0) + 1);
}

// "대상 T 바로 앞(문서 순서) 트리거의 face"(D-F′) — 엔트리는 문서 순서다. 라이브(enqueueFrom)와
// 재개 복원(restoreVisited)이 같은 규칙으로 구한다.
function priorFaceOf(ctx, entries, targetId) {
  let face = null;
  for (const entry of entries) {
    if (entry.id === targetId) return face;
    const target = ctx.targets[entry.id];
    if (target && TRIGGER_KINDS[target.kind] && entry.enabled && !entry.occluded
        && entry.face !== null && entry.face !== undefined) {
      face = entry.face; // 활성 트리거만(리뷰 Minor 7) — 라이브 적재와 같은 규칙
    }
  }
  return face;
}

// ②b는 «그 항목이 들어온 상태에서 대상이 빈 입력이었는가»다(O1) — 값은 pushUnit이 그때의
// 인벤토리 엔트리에서 받아 든다. 재개는 문서의 인벤토리(K7 value_empty)로 같은 값을 되살린다.
// 우선권은 identity당 executed fill이 상한 미만일 때만이다(D-K) — 진행 조건은 두 번이면 충분히
// 열리고, 그 뒤의 빈 입력은 다른 단위와 같은 저울(③④⑤⑥)로 잰다.
const EMPTY_FILL_PRIORITY_CAP = 2;

function emptyInputPriority(ctx, run, item) {
  const target = ctx.targets[item.target];
  if (!target || !EMPTY_INPUT_KINDS[target.kind] || item.action !== 'fill') return false;
  return item.valueEmpty === true && (run.fillRuns.get(item.target) || 0) < EMPTY_FILL_PRIORITY_CAP;
}

// D-G — 재생 생략은 «해시 일치 ∧ 계보 일치»일 때만이다(5차 실측: 숨은 데이터를 해시가
// 구분하지 못해 다른 계보의 상태가 이어 붙었다).
function samePath(path, ops) {
  if (!path || path.length !== ops.length) return false;
  for (let i = 0; i < ops.length; i += 1) {
    if (path[i] !== ops[i].target) return false;
  }
  return true;
}

// ---------------------------------------------------------------------
// 큐 확장 — 한 상태에서 관찰한 활성 대상의 필요 조작을 전부 넣는다. 문서에 남는
// 인벤토리는 예외 없이 여기를 거친다(그러지 않으면 잔여가 요구하는 단위인데
// 큐에 없는 «영구 잔여»가 생긴다).
// ---------------------------------------------------------------------
function enqueueFrom(ctx, run, entries, invTargets, stateHash, ops) {
  const docOrder = entries.map((entry) => entry.id);
  const contexts = new Map();
  const contextOf = (id, target) => {
    const bucket = contextBucket(id, target);
    if (!contexts.has(bucket)) {
      contexts.set(bucket, ctx.pure.contextFor(entries, unitTarget(id, target), docOrder));
    }
    return contexts.get(bucket);
  };

  // "대상 바로 앞(문서 순서) 트리거의 face"(D-F′ ②) — 엔트리를 문서 순서로 한 번 훑으며 모은다.
  const priorFaces = new Map();
  let runningFace = null;
  for (const entry of entries) {
    priorFaces.set(entry.id, runningFace);
    const seen = ctx.targets[entry.id];
    // 활성 트리거의 face만 센다 — 큐 키의 context_T(stateContext)와 같은 규칙이다(리뷰 Minor 7).
    if (seen && TRIGGER_KINDS[seen.kind] && entry.enabled && !entry.occluded
        && entry.face !== null && entry.face !== undefined) {
      runningFace = entry.face;
    }
  }

  const active = new Set();
  for (const entry of entries) {
    if (!entry.enabled || entry.occluded) continue; // 활성 = enabled && !occluded(K1)
    active.add(entry.id);
    const target = ctx.targets[entry.id];
    if (!target) continue;
    const observed = [observedStateOf(entry)];
    for (const unit of ctx.pure.requiredActions(unitTarget(entry.id, target), observed, ctx.targets)) {
      pushUnit(ctx, run, entry.id, unit, contextOf(entry.id, target), stateHash, ops,
               priorFaces.get(entry.id), entry.value_empty === true);
    }
  }
  // "native select: option은 owner=그 select·action=select인 대상"(K2) — 닫힌 select의
  // option은 entries 밖이라 targets에서 따로 돈다. **이 상태의 인벤토리가 낸 targets**만
  // 본다(누적 ctx.targets를 돌면 부모 값이 바뀌어 사라진 옛 옵션까지 큐에 들어간다 —
  // 수정 라운드 1 I-5). 문서 복원(resume)에는 상태별 targets가 없어 빈 맵이 온다.
  for (const [id, target] of Object.entries(invTargets)) {
    if (target.kind !== 'option' || !active.has(target.owner)) continue;
    const owner = ctx.targets[target.owner];
    if (!owner || owner.kind !== 'select') continue;
    for (const unit of ctx.pure.requiredActions(unitTarget(id, target), [], ctx.targets)) {
      // 네이티브 옵션은 트리거가 아니라 ②에 해당하지 않는다(priorFace는 쓰이지 않는다).
      // 닫힌 select의 옵션은 entries 밖이라 value_empty도 없다(②b도 해당하지 않는다).
      pushUnit(ctx, run, id, unit, contextOf(id, target), stateHash, ops, null, false);
    }
  }
}

// residual이 세는 관찰 상태와 같은 규칙(checked → surface → face)이다.
function observedStateOf(entry) {
  if (entry.checked !== null && entry.checked !== undefined) return entry.checked;
  if (entry.surface !== null && entry.surface !== undefined) return entry.surface;
  return entry.face === undefined ? null : entry.face;
}

// requiredActions가 보는 대상 모양 — `name`·`dom_path`는 «이름이 있고 대상 후손이 없는
// handler = 토글형»(D-H) 판정 입력이다(이름이 빈 handler와 컨테이너는 토글형이 아니다).
function unitTarget(id, target) {
  return {
    id, kind: target.kind, name: target.name, dom_path: target.dom_path, owner: target.owner,
    scrim: target.scrim, value: target.value,
  };
}

// context_T는 대상 종류로만 갈린다 — 트리거는 자기 문서 순서, 메뉴 항목은 owner,
// 그 밖은 face 성분을 전부 빼므로 한 값이다(K1). 상태마다 대상 수만큼 해시를 다시
// 계산하면 큰 화면에서 탐색이 서므로 이 세 갈래로만 계산한다(값은 정의와 같다).
function contextBucket(id, target) {
  if (target.kind === 'trigger' || target.kind === 'select') return `trigger:${id}`;
  if ((target.kind === 'menuitem' || target.kind === 'option') && target.owner) return `item:${target.owner}`;
  return 'plain';
}

function pushUnit(ctx, run, targetId, unit, context, prefixHash, ops, priorFace, valueEmpty) {
  const option = unit.option === undefined ? null : unit.option;
  const key = JSON.stringify([targetId, unit.action, option, context]);
  if (run.seen.has(key)) return;
  if (ops.length + 1 > ctx.limits.maxDepth) {
    // 같은 키가 나중에 더 얕은 경로로 들어오면 아래에서 집합에서 빠진다 —
    // 한 번 막혔다는 이유로 partial을 영구히 참으로 두지 않는다(수정 라운드 1 m8).
    run.depthBlocked.add(key);
    return;
  }
  run.depthBlocked.delete(key);
  run.seen.add(key);
  run.queue.push({
    key,
    unitKey: JSON.stringify([targetId, unit.action, option]),
    target: targetId,
    action: unit.action,
    option,
    context,
    prefixHash,
    ops,
    priorFace: priorFace === undefined ? null : priorFace, // ② D-F′ 입력
    valueEmpty: valueEmpty === true,                       // ②b O1 입력(빈 입력인가)
  });
}

// 새로 관찰한 상태를 받아들인다 — 대상 누적과 큐 확장은 늘 같이 일어난다.
// `ops`는 **그 상태에 이른 부모 경로**(지금 조작하려는 대상은 빠진다 — 드라이런 6차 결정
// B1)다. 사본으로 넘긴다: 재생(`reachState`)은 op를 하나씩 덧붙이는 **같은 배열**을
// replayOperation에 넘기므로, 그 배열을 큐 항목이 그대로 물면 복구 재인벤토리로 드러난
// 항목의 계보에 바로 뒤에 재생될 형제 조작이 끼어든다(6차 실측 [… 시·군, 보성군, 고흥군]).
function acceptState(ctx, run, snapshot, stepNumber, ops) {
  mergeTargets(ctx, snapshot.inventory.targets, stepNumber);
  enqueueFrom(ctx, run, snapshot.inventory.entries, snapshot.inventory.targets, snapshot.state_hash, ops.slice());
}

// ---------------------------------------------------------------------
// --resume — "out 문서의 steps/큐를 잇는다"(K1). 큐는 문서에 없으므로 기록된
// 상태(step의 after 인벤토리)와 그 step의 path에서 다시 만든다. 이미 소비한 큐
// 키는 step의 (target, action, option, context)가 그대로다.
// ---------------------------------------------------------------------
// «재생을 지나 그 상태에 **선 채 스냅샷을 들고**» 난 unreachable 사유 — 그때만 step의
// before가 곧 항목의 prefixHash다. ensureOperable·performStep·applyOperation이 내는
// 문구가 단일 출처다. 스냅샷을 잃은 두 갈래(«가림을 푸는 사이에 상태가 달라졌다» ·
// «뷰포트 밖 대상을 굴리는 사이에 상태가 달라졌다» — before가 null이다)는 여기 없다.
const REACHED_STATE_ERRORS = /^(현재 상태에 없음|조작 직전 대상이 비활성이다|조작 뒤 루트를 찾지 못했다|owner select를 찾지 못했다)/;

function restoreVisited(ctx, run, steps) {
  // D-I — 페이지가 사라져 끊긴 단위는 새 브라우저에서 **한 번은** 다시 시도한다(그러지
  // 않으면 미실행 단위가 영구 잔여가 된다). 같은 키가 두 번째로 그렇게 끊겼으면 조작
  // 자체가 페이지를 닫는 대상이므로 그때부터 다시 넣지 않는다(무한 재시도 방지).
  const closedOnce = new Set();
  // 항목의 prefixHash는 문서에 없다 — executed·unclickable은 before가 곧 그 값이고,
  // 재생이 종점에서 어긋난 unreachable은 **부모 경로의 after**가 그 값이다(4b 리뷰 I2).
  // 부모를 찾지 못하면(앞선 슬라이스에 그 step이 없으면) before로 대신한다 — 보고서 한계.
  const afterByPath = new Map([[JSON.stringify([]), ctx.prior ? ctx.prior.initialHash : null]]);
  for (const step of steps) {
    const seenKey = JSON.stringify([step.target, step.action, step.option, step.context]);
    const closed = (step.error || '').startsWith(PAGE_CLOSED_PREFIX);
    if (!closed || closedOnce.has(seenKey)) {
      run.seen.add(seenKey);
    } else {
      closedOnce.add(seenKey);
    }
    // 분류는 접두를 뗀 원문 사유로 한다 — 접두가 `REACHED_STATE_ERRORS`의 `^` 앵커를 깨면 ①(before)
    // 갈래가 ②(부모 after)로 샌다(4d 재리뷰 Minor 2).
    const reason = closed ? step.error.slice(PAGE_CLOSED_PREFIX.length) : (step.error || '');
    const before = step.before ? step.before.state_hash : null;
    const parent = afterByPath.get(JSON.stringify(step.path.slice(0, -1)));
    // unreachable은 두 갈래다. ① 재생이 성공해 «도달하려던 상태»에 선 뒤 실패한 갈래는
    // before가 곧 항목의 prefixHash다. ② 그 상태에 서 보지도 못한 갈래(재생 실패·재생 종점
    // 불일치·페이지를 다시 열지 못함·굴리는 사이 상태가 달라짐)는 before가 그 상태가
    // 아니므로 부모 경로의 after로 대신한다(리뷰 Minor 4). 문서 스키마로는 갈리지 않아
    // 사유로 가르되 **①을 목록으로** 둔다 — 재생 쪽 사유가 늘어도(«페이지를 다시 열지
    // 못했다» — 4c 재리뷰 이월 2) ①로 잘못 새지 않는다.
    const reached = step.status !== 'unreachable' || REACHED_STATE_ERRORS.test(reason);
    const prefixHash = reached || parent === undefined ? before : parent;
    if (step.status === 'executed' && step.discovery !== true) {
      run.executedUnits.add(JSON.stringify([step.target, step.action, step.option]));
      // D-F·D-K 카운터도 같은 자리에서 되살린다 — 이어 단 슬라이스가 첫 슬라이스와 같은 순서로
      // 꺼내려면 «직전 트리거 face»·«접두 상태별 실행 수»·«identity별 fill 실행 수»가 복원돼야 한다.
      const entries = step.before ? step.before.inventory : [];
      noteExecuted(run, {
        target: step.target, action: step.action, priorFace: priorFaceOf(ctx, entries, step.target),
      }, prefixHash);
    }
    if (step.after && step.after.state_hash) afterByPath.set(JSON.stringify(step.path), step.after.state_hash);
    // 발견은 실행당 한 번이다 — 앞선 슬라이스의 hover step을 다시 만들지 않는다(그 뒤 상태는
    // restoreStates가 되살린다). 스크롤은 step이 아니라 상태 정규화라 다시 걸어도 문서가 늘지
    // 않으므로 되살리지 않는다. 연속 카운터보다 앞이다 — 아래 `continue` 뒤에 두면 닿지 않는다
    // (4d 재리뷰 범위 밖 1: 슬라이스마다 같은 hover가 되풀이됐다).
    if (step.discovery === true) run.discovered.add(`${step.action}:${step.target}`);
    // 연속 카운터는 꼬리에서 다시 센다 — 마지막으로 «꺼낸» 항목들의 접두 상태가 같았는가.
    // 발견(hover) step은 큐를 거치지 않으므로(discoverHover가 performStep을 직접 부른다) 라이브
    // `takeNext`가 세지 않는다 — 복원도 세지 않아야 슬라이스 경계에서 순서가 갈리지 않는다(리뷰 I-3).
    if (step.discovery === true) continue;
    run.sameStateRun = prefixHash && prefixHash === run.lastPrefixHash ? run.sameStateRun + 1 : 1;
    run.lastPrefixHash = prefixHash;
  }
}

function restoreStates(ctx, run) {
  // path(대상 id 목록)는 같은 대상의 focus/fill/blur를 구별하지 못한다 — 부모는
  // «path 접두가 같은 후보» 중 자기 after 해시가 이 step의 before 해시와 같은 것이다
  // (수정 라운드 1 I-2). 그래서 후보 목록으로 들고 해시로 확정한다.
  const byPath = new Map([[JSON.stringify([]), [{ ops: [], afterHash: ctx.prior.initialHash }]]]);
  const push = (path, candidate) => {
    const key = JSON.stringify(path);
    if (!byPath.has(key)) byPath.set(key, []);
    byPath.get(key).push(candidate);
  };

  for (const step of ctx.prior.steps) {
    const before = step.before || {};
    if (!before.state_hash) {
      process.stderr.write(`재개: step ${step.n}에 before 상태가 없어 복원 출처에서 뺀다\n`);
      continue;
    }
    const candidates = byPath.get(JSON.stringify(step.path.slice(0, -1))) || [];
    const parent = candidates.find((row) => row.afterHash === before.state_hash);
    if (!parent) {
      process.stderr.write(`재개: step ${step.n}의 부모 상태를 찾지 못해 복원 출처에서 뺀다\n`);
      continue;
    }
    const ops = parent.ops.concat([{ target: step.target, action: step.action, option: step.option }]);
    const hasAfter = !!step.after && Array.isArray(step.after.inventory);
    // step n의 first_seen_step이 n인 네이티브 옵션은 그 step의 after 상태 것이다 — after가
    // 없는 step(unreachable·failed)에서만 before가 대신 받는다(수정 라운드 1 m3).
    const options = optionsFirstSeenAt(ctx, step.n);
    // 3b 불변식: 문서에 남는 인벤토리는 예외 없이 큐 확장 출처다. 라이브에서는 조작 직전
    // 복구 재인벤토리(ensureOperable · D-E)가 이 step의 before로 남으며 acceptState를 거치므로,
    // 재개도 executed를 가리지 않고 **모든** step의 before를 먼저 넣는다(라이브와 같은 순서 —
    // 복구 재인벤토리 → 조작 → after). 경로는 자기 대상을 뺀 부모 경로다(B1). 종전에는 after가
    // 있는 step의 before를 버려 거기서만 활성이던 대상이 재개 뒤 영구 잔여가 됐다(최종 리뷰 I1).
    // run.seen이 중복을 거른다.
    if (Array.isArray(before.inventory)) {
      enqueueFrom(ctx, run, rejoinEntries(ctx, before.inventory),
                  hasAfter ? {} : options, before.state_hash, parent.ops);
    }
    if (hasAfter) {
      push(step.path, { ops, afterHash: step.after.state_hash });
      enqueueFrom(ctx, run, rejoinEntries(ctx, step.after.inventory), options, step.after.state_hash, ops);
    }
  }
}

// 네이티브 select 옵션은 인벤토리 entries에 없어 문서만으로는 어느 상태의 것인지
// 알 수 없다 — 다만 target의 first_seen_step이 «처음 관찰된 상태»를 가리킨다. 그
// step의 상태에서만 그 옵션을 다시 넣으면 재개가 cascade 자식 옵션을 잃지 않으면서
// stale 옵션도 들어오지 않는다(수정 라운드 2 N-1). first_seen_step 0은 initial이라
// 살아 있는 초기 스냅샷이 이미 넣는다.
function optionsFirstSeenAt(ctx, stepNumber) {
  const found = {};
  for (const [id, target] of Object.entries(ctx.targets)) {
    if (target.kind === 'option' && target.first_seen_step === stepNumber) found[id] = target;
  }
  return found;
}

// 재개가 문서의 엔트리(K7 8필드)에 identity 원본 4필드를 되살리는 조인이다 — 소비처는
// `restoreStates` → `enqueueFrom`(→ `contextFor`/`stateContext`)뿐이고 그들은 dom_path를
// 읽지 않는다. 표면 키를 문서로 재계산하는 조인은 이름이 빈 대상의 `dom_path`까지 얹어야
// 한다(K7 · 수정 라운드 2) — 그 조인은 여기가 아니라 검사기·테스트 쪽에 있다(재리뷰 M6).
function rejoinEntries(ctx, entries) {
  return entries.map((entry) => {
    const target = ctx.targets[entry.id];
    if (!target) return entry;
    return Object.assign({}, entry, {
      role: target.role, name: target.name, input_type: target.input_type, owner: target.owner,
    });
  });
}

// ---------------------------------------------------------------------
// 항목 하나 실행 — 재생 → 조작 가능 확인 → 조작 → step 기록 → 발견 조작.
// ---------------------------------------------------------------------
async function runItem(ctx, run, item) {
  const n = run.stepNo + 1;
  const reached = await reachState(ctx, run, item, n);
  if (!reached.ok) {
    recordStep(run, item, n, {
      status: 'unreachable', error: stepError(ctx, run, reached.error),
      before: blockOf(reached.snapshot), after: null,
    });
    run.current = null;
    run.currentPath = null;
    return;
  }

  const operable = await ensureOperable(ctx, run, item, reached.snapshot);
  if (!operable.ok) {
    recordStep(run, item, n, {
      status: operable.status, error: stepError(ctx, run, operable.error),
      before: blockOf(operable.snapshot), after: null,
    });
    run.current = operable.snapshot; // 조작을 시도하지 않았으므로 상태는 그대로다
    if (!run.current) run.currentPath = null;
    return;
  }

  const done = await performStep(ctx, run, item, n, operable.snapshot);
  run.current = done.ops ? await discover(ctx, run, done.snapshot, done.ops) : done.snapshot;
  if (!run.current) run.currentPath = null;
}

// 조작 직전 확인 — 큐에 든 것은 «그 상태에서 활성»이던 대상이지만, 스크롤 위치는
// state_hash 입력이 아니라서(K3) 같은 해시의 상태를 다시 열면 스크롤 컨테이너가
// 처음으로 돌아가 대상이 다시 가려진다. 가려진 채로 클릭하면 엉뚱한 요소를 눌러 놓고
// K3 반례(«가림 대상의 executed»)를 만든다.
async function ensureOperable(ctx, run, item, snapshot) {
  const entry = snapshot.inventory.entries.find((row) => row.id === item.target);
  // 네이티브 select 옵션은 entries 밖이지만 그 상태의 targets에는 있다 — 거기에도
  // 없으면 «이 상태에 없는 대상»이라 조작을 시도하지 않는다(수정 라운드 1 M3).
  if (!entry && !snapshot.inventory.targets[item.target]) {
    return { ok: false, snapshot, status: 'unreachable', error: `현재 상태에 없음: ${item.target}` };
  }
  if (entry && !entry.enabled) {
    return { ok: false, snapshot, status: 'unreachable', error: `조작 직전 대상이 비활성이다: ${item.target}` };
  }
  let ready = snapshot;
  if (entry && entry.occluded) {
    const recovered = await recoverOccluded(ctx, snapshot, item.target);
    if (!recovered.ok) {
      if (!recovered.snapshot) {
        return { ok: false, snapshot: null, status: 'unreachable', error: '가림을 푸는 사이에 상태가 달라졌다' };
      }
      // 굴려도 가려져 있던 그 인벤토리도 문서에 before로 남는다 — 확장 출처로 삼지 않으면
      // 거기서만 활성인 대상이 «잔여인데 큐에 없는» 상태가 된다(3b 불변식 · 재리뷰 M5).
      if (recovered.snapshot !== snapshot) acceptState(ctx, run, recovered.snapshot, run.stepNo, item.ops);
      return { ok: false, snapshot: recovered.snapshot, status: 'unclickable', error: recovered.reason };
    }
    // 복구 재인벤토리도 문서에 남는 인벤토리다 — 예외 없이 큐 확장 출처로 삼는다
    // (3b 불변식 · 드라이런 2차 결정 D-E). 거기서만 활성인 대상이 영구 잔여가 되지 않는다.
    acceptState(ctx, run, recovered.snapshot, run.stepNo, item.ops);
    ready = recovered.snapshot;
  }
  // 굴린 뒤의 인벤토리가 이 step의 before가 되도록 조작 전에 판정한다(D-B).
  const rolled = await recoverOffscreen(ctx, ready, item);
  if (!rolled.snapshot) return { ok: false, snapshot: null, status: 'unreachable', error: rolled.reason };
  if (rolled.snapshot !== ready) acceptState(ctx, run, rolled.snapshot, run.stepNo, item.ops); // D-E
  if (occludedNow(rolled.snapshot, item.target)) {
    // 굴린 자리에서 새로 가려졌다(고정 막대 뒤 등) — 굴리기 전 판정으로는 못 잡는다.
    // 다시 recoverOccluded를 걸어도 같은 자리로 굴릴 뿐이라 그대로 unclickable로 적는다.
    // 실행하면 before에 occluded:true인 executed step이 남아 K3 반례가 된다(수정 라운드 4 Ruling).
    return { ok: false, snapshot: rolled.snapshot, status: 'unclickable', error: '굴린 자리에서 대상이 가려져 있다' };
  }
  return { ok: true, snapshot: rolled.snapshot };
}

// 그 상태의 인벤토리에서 대상이 가려져 있는가(엔트리가 없는 네이티브 옵션 등은 판정 밖).
function occludedNow(snapshot, targetId) {
  const entry = snapshot.inventory.entries.find((row) => row.id === targetId);
  return !!entry && entry.occluded === true;
}

// 가림 풀기 — 대상을 보이는 자리로 굴리고 한 번만 다시 본다. 스크롤은 state_hash
// 입력이 아니므로(K3) 이 조작은 상태를 바꾸지 않는다(바뀌면 실패로 다룬다). 발견
// 조작이 연 «컨테이너 끝» 상태를 재생 뒤에 되살리는 것도 이 경로다.
// 실패 사유는 호출부가 step `error`에 그대로 적는다 — «굴려도 가려져 있다»와
// «굴려 보지도 못했다»는 리뷰어에게 다른 사실이다(수정 라운드 1 I1).
async function recoverOccluded(ctx, snapshot, targetId) {
  const target = ctx.targets[targetId];
  if (!target) return { ok: false, snapshot, reason: `대상 정의가 없다: ${targetId}` };
  if (!(await scrollIntoViewOf(ctx, target.dom_path))) {
    // `iframe[n]/`·`overlay[n]/` 접두 등 루트 자식 경로가 아닌 대상 — 되짚지 못한
    // 영역이 있다는 사실을 한계로 남긴다(K2 «수집 완료가 아니다»).
    noteLimit(ctx, 'occlusion-recovery', target.dom_path,
      '경로를 되짚지 못해 가림을 풀지 못했다 — 이 영역의 가려진 대상은 실행되지 않는다');
    return { ok: false, snapshot, reason: `경로 되짚기 실패: ${target.dom_path}` };
  }
  await waitStable(ctx);
  const retaken = await inventorySnapshot(ctx);
  if (!retaken.inventory.root.found || retaken.state_hash !== snapshot.state_hash) {
    return { ok: false, snapshot: null, reason: '가림을 푸는 사이에 상태가 달라졌다' };
  }
  const entry = retaken.inventory.entries.find((row) => row.id === targetId);
  const ok = !!entry && entry.enabled && !entry.occluded;
  return { ok, snapshot: retaken, reason: ok ? null : '스크롤로 굴려도 대상이 가려져 있다' };
}

// 뷰포트 밖 풀기 — "클릭 지점이 브라우저 뷰포트 밖이면 대상을 scrollIntoView로 굴려
// 상태 해시가 그대로일 때만 재판정하고, 여전히 밖이면 unclickable"(K2 드라이런 결정 D-B).
// 루트가 브라우저 창보다 긴 화면(A8의 긴 메뉴·다이얼로그)에서는 창 밖에 놓인 지점이
// 조작 실패의 유일한 사유가 된다(드라이런 1차 실측 unclickable 10건이 전부 이 사유).
// 굴려도 밖이면 여기서 판정하지 않는다 — applyOperation이 기존 문구로 unclickable을 낸다.
// 반환 `snapshot`이 null이면 굴리는 사이에 상태가 달라진 것이다(호출부가 unreachable).
async function recoverOffscreen(ctx, snapshot, op) {
  const pointTarget = pointTargetOf(ctx, op);
  if (op.action === 'key' || !pointTarget) return { snapshot, reason: null }; // 지점을 쓰지 않는다
  const target = ctx.targets[pointTarget];
  if (!target) return { snapshot, reason: null };
  const point = await pointOf(ctx, op, pointTarget);
  if (!point || !outsideViewport(ctx, point)) return { snapshot, reason: null };
  if (!(await scrollIntoViewOf(ctx, target.dom_path))) {
    // `iframe[n]/`·`overlay[n]/` 접두 등 루트 자식 경로가 아닌 대상 — 굴려 보지도
    // 못했다는 사실을 한계로 남긴다(K2 «수집 완료가 아니다»).
    noteLimit(ctx, 'offscreen-recovery', target.dom_path,
      '경로를 되짚지 못해 뷰포트 안으로 굴리지 못했다 — 이 영역의 창 밖 대상은 실행되지 않는다');
    return { snapshot, reason: null };
  }
  await waitStable(ctx);
  const retaken = await inventorySnapshot(ctx);
  if (!retaken.inventory.root.found || retaken.state_hash !== snapshot.state_hash) {
    return { snapshot: null, reason: '뷰포트 밖 대상을 굴리는 사이에 상태가 달라졌다' };
  }
  return { snapshot: retaken, reason: null };
}

// 조작 → 안정 대기 → 이탈/루트 확인 → 인벤토리 → step 기록. 통상 항목과 발견 조작이
// 같은 경로를 쓴다(발견 step도 K7 step 14필드 그대로다 — `discovery`만 참이다).
// 반환은 «조작 뒤 우리가 아는 상태»(모르면 null)와 거기까지의 재생 경로다.
async function performStep(ctx, run, item, n, before) {
  ctx.loadError = null; // 이 조작 동안 생긴 로드 오류만 이 step의 것이다
  const outcome = await applyOperation(ctx, item);
  if (outcome.status !== 'executed') {
    recordStep(run, item, n, {
      status: outcome.status, error: stepError(ctx, run, outcome.error),
      before: blockOf(before), after: null, value: outcome.value,
    });
    // unclickable·unreachable은 조작을 시도하지 않았으므로 상태가 그대로지만(계보도 그대로),
    // failed는 조작 도중에 끊긴 것이라 지금 상태도 계보도 알 수 없다.
    if (outcome.status === 'failed') run.currentPath = null;
    return { snapshot: outcome.status === 'failed' ? null : before, ops: null };
  }

  await settle(ctx);
  // D-I — 조작이 페이지를 없앴다(외부 종료도 같은 관찰면이다). 이탈(navigated)도 성공도
  // 아니다: after를 관찰할 수 없으므로 실패로 적는다. 여기서 잡지 않으면 `navigatedUrl`이
  // 살아 있지 않은 page의 url을 «이탈»로 읽어 executed 터미널 step을 남기고(6차 실측
  // step 575 판형), 그 뒤 `inventorySnapshot`이 닫힌 page에서 깨진다.
  if (pageGone(ctx, run)) {
    recordStep(run, item, n, {
      status: 'failed', error: stepError(ctx, run, '조작 뒤 상태를 관찰하지 못했다'),
      before: blockOf(before), after: null, value: outcome.value,
    });
    run.currentPath = null;
    return { snapshot: null, ops: null };
  }

  const loadError = ctx.loadError;
  if (loadError) {
    // 로드 오류가 난 조작은 관찰이 성립하지 않는다. K3가 "executed인데 error≠null"을
    // 반례로 두므로 executed로 남기지 않고 failed로 적어 단위를 잔여에 남긴다.
    recordStep(run, item, n, {
      status: 'failed', error: stepError(ctx, run, loadError), before: blockOf(before), after: null,
    });
    run.currentPath = null;
    return { snapshot: null, ops: null };
  }

  const url = await navigatedUrl(ctx);
  if (url) {
    // "조작 뒤 document/URL이 바뀌면 navigated: <url>·after: null인 터미널 step,
    // 큐에 넣지 않는다"(K2). 캡처는 하지 않는다 — "드라이버는 initial과 added≠∅
    // step에만 PNG를 저장한다(navigated는 루트 크롭이 성립하지 않는다)"(K3).
    // 조작이 만든 값 변화는 after가 없어도 사실대로 남긴다(수정 라운드 1 I-1).
    recordStep(run, item, n, {
      status: 'executed', error: null, before: blockOf(before), after: null, navigated: url,
      value: outcome.value, changes: { added: [], removed: [], values: outcome.values || [] },
    });
    run.currentPath = null; // 이탈했다 — 이 문서의 계보 밖이다
    return { snapshot: null, ops: null };
  }

  const after = await inventorySnapshot(ctx);
  if (!after.inventory.root.found) {
    recordStep(run, item, n, {
      status: 'unreachable', error: stepError(ctx, run, `조작 뒤 루트를 찾지 못했다: ${ctx.rootSelector}`),
      before: blockOf(before), after: null, value: outcome.value,
    });
    run.currentPath = null; // 루트를 잃었다 — 지금 상태도 계보도 모른다
    return { snapshot: null, ops: null };
  }

  const changes = changesOf(before, after, outcome.values || []);
  // "after.capture는 initial과 changes.added ≠ ∅·navigated step에만 있다"(K7).
  const shot = changes.added.length > 0 ? await capture(ctx, `step-${n}`) : null;
  recordStep(run, item, n, {
    status: 'executed', error: null, before: blockOf(before), after: afterBlockOf(after, shot),
    changes, value: outcome.value,
  });
  const ops = item.ops.concat([{ target: item.target, action: item.action, option: item.option }]);
  run.currentPath = ops.map((op) => op.target); // 이 조작이 지금 상태의 계보다(D-G)
  acceptState(ctx, run, after, n, ops);
  return { snapshot: after, ops };
}

// ---------------------------------------------------------------------
// 발견 조작 — "mouseenter/mouseover 리스너나 :hover 규칙(render-audit hoverSelectors
// 매칭) 보유 요소에 hover 후 재인벤토리, 스크롤 가능한 컨테이너는 끝까지 스크롤 후
// 재인벤토리(discovery_limits에 overflow 컨테이너·자식 수 급증 기록). 새 대상은 K1
// 규칙으로 큐에 들어간다."(K2) 필요 조작이 아니므로 잔여 단위를 만들지 않는다.
//
// hover 후보는 한 실행에서 **대상 identity당 한 번씩만** 연다 — 상태마다 다시 열면 상태
// 차원이 후보 수만큼 곱해져 상한 안에서 아무것도 증명하지 못한다(보고서 §발견 범위).
// 스크롤 훑기는 **(상태 해시, dom_path)당 한 번씩**이다(드라이런 6차 결정 B2): 컨테이너
// 안 목록은 상태마다 통째로 갈리므로 dom_path 전역 한 번은 뒤 상태를 통째로 잃는다.
// ---------------------------------------------------------------------
async function discover(ctx, run, snapshot, ops) {
  if (!snapshot) return null;
  const scrolled = await discoverScroll(ctx, run, snapshot, ops);
  if (!scrolled) return null;
  return discoverHover(ctx, run, scrolled, ops);
}

// 스크롤은 step이 아니다: state_hash 입력이 아니고(K3), 컨테이너는 대상이 아닐 수 있어
// (스니펫 `scrollContainers`의 `id`가 null) K7 step의 `target`을 채울 identity가 없으며,
// K3가 "path가 가리키는 step 미존재"를 반례로 두므로 재생 경로에도 넣을 수 없다.
// 대신 «컨테이너를 끝까지 연 상태»를 상태 정규화로 두고 discovery_limits에 적는다.
async function discoverScroll(ctx, run, snapshot, ops) {
  const containers = await withDeadline(ctx.page.evaluate(() => globalThis.__interactionAudit.dom.scrollContainers()), 'ctx.page.evaluate');
  let current = snapshot;
  for (const container of containers) {
    // 훑음 판정은 **(현재 상태 해시, dom_path)**다(드라이런 6차 결정 B2). dom_path 전역으로
    // 한 번만 훑으면, 같은 자리의 컨테이너가 상태마다 다른 목록을 갖는 화면(A8 시·도→시·군)
    // 에서 뒤 상태의 항목이 가려진 채 어느 인벤토리에도 활성으로 나오지 않아 큐에 못 든다
    // (6차 실측 시·군 145/153 · 충북 7~11번 항목).
    const key = `scroll:${current.state_hash}:${container.dom_path}`;
    if (run.discovered.has(key)) continue;
    const cap = capHit(ctx, run);
    if (cap) {
      // 상한에 잘린 발견은 문서에 남아야 한다 — 안 그러면 «열어 보지도 못한 영역»이
      // 있는 실행이 partial:false로 완주처럼 보인다(수정 라운드 1 I2).
      noteCap(run, cap);
      noteLimit(ctx, 'scroll-container', container.dom_path, `상한(${cap})으로 미실행`);
      continue;
    }
    run.discovered.add(key);
    // 앞 슬라이스의 «미실행» 행(N-3)은 이 실행이 처음 훑을 때만 지운다 — 뒤 상태의 훑기가
    // 이 실행의 첫 사유까지 지우면 noteSweep이 유지하는 «첫 훑기의 사실»이 사라진다.
    if (!ctx.sweepNotes.has(container.dom_path)) dropLimit(ctx, 'scroll-container', container.dom_path);
    const swept = await sweepContainer(ctx, run, current, container, ops);
    if (!swept) return null; // 훑는 사이 루트를 잃었다
    current = swept;
  }
  return current;
}

// "컨테이너마다 scrollTop=0부터 clientHeight씩(가로는 clientWidth) 끝까지 진행하며 위치마다
// 재인벤토리하고 acceptState한다"(K2 발견 조작 · 드라이런 2차 결정 D-D). 상태마다 다시
// 훑는다(6차 결정 B2 — 목록이 상태마다 갈린다). 끝으로만 굴리면
// 중간 페이지의 항목은 어느 인벤토리에도 활성으로 나오지 않아 큐에 들지 못한다
// (A8 2차 실측: 시·도 메뉴 17항목 중 처음 6·끝 3만 실행). 컨테이너는 마지막 위치(끝)에 남는다.
//
// **first_seen_step 규칙**: 스크롤로 드러난 대상의 first_seen_step은 «이 정규화가 붙은
// 상태를 만든 step n»이다(initial 상태면 0). 스크롤은 step이 아니라 그 상태의 일부이므로
// `optionsFirstSeenAt`(재개가 옵션을 되넣는 자리)과도 정합한다 — 그 step의 after 상태에서
// 다시 훑으면 같은 대상이 다시 드러난다.
const SWEEP_PAGES = 50; // 페이지 수 상한(K2 D-D)

async function sweepContainer(ctx, run, snapshot, container, ops) {
  const had = activeIds(snapshot);
  const gained = new Set();
  let current = snapshot;
  let visited = 0;
  let stopped = null;
  let offset = 0;
  let span = 0;
  let limit = 0;

  for (let page = 0; page <= SWEEP_PAGES; page += 1) {
    // 위치마다 상한을 본다 — 훑기는 step을 늘리지 않아 max_steps에 걸리지 않고 max_minutes도
    // 항목 사이에서만 재므로, 컨테이너 하나가 «50 위치 × (안정 대기 + 인벤토리)»를 상한 밖에서
    // 먹을 수 있다(재리뷰 M4 — 도구 600초 상한과 인접하다).
    const cap = capHit(ctx, run);
    if (cap) {
      noteCap(run, cap);
      stopped = `${visited} 위치까지 훑고 상한(${cap})으로 멈췄다`;
      break;
    }
    const at = await scrollContainerTo(ctx, container.dom_path, offset);
    if (!at) {
      noteLimit(ctx, 'scroll-container', container.dom_path,
        '컨테이너를 dom_path로 되짚지 못해 훑지 못했다 — 컨테이너 안 항목은 열거되지 않았다');
      return current;
    }
    // 세로로 굴릴 자리가 있으면 세로, 아니면 가로로 훑는다(한 축만 — 스니펫이 내는
    // 컨테이너는 세로로 넘치는 것뿐이다).
    span = at.vertical ? at.page.h : at.page.w;
    limit = at.vertical ? at.max.top : at.max.left;
    await waitStable(ctx);
    const after = await inventorySnapshot(ctx);
    if (!after.inventory.root.found) return null;
    if (after.state_hash !== snapshot.state_hash) {
      // 훑다가 상태가 달라졌다(지연 로딩 등) — 훑기는 여기서 끝내되 **지금 상태**는 이
      // after다. 옛 스냅샷을 current로 올리면 다음 컨테이너 훑기·발견 step의 before·
      // «접두 해시가 같으면 재생 생략» 최적화가 전부 실제와 어긋난다(재리뷰 I2).
      // 문서에 before로 남을 수 있는 인벤토리이므로 3b 불변식대로 확장 출처로도 삼는다.
      stopped = `${visited} 위치까지 훑다가 상태가 달라져 중단했다`;
      acceptState(ctx, run, after, run.stepNo, ops);
      current = after;
      break;
    }
    visited += 1;
    for (const id of activeIds(after)) { if (!had.has(id)) gained.add(id); }
    acceptState(ctx, run, after, run.stepNo, ops);
    current = after;
    if (at.at >= limit) break; // 끝에 닿았다
    if (page === SWEEP_PAGES) {
      stopped = `페이지 상한(${SWEEP_PAGES})에서 멈췄다 — 컨테이너 끝까지 훑지 못했다`;
      break;
    }
    offset = Math.min(offset + (span > 0 ? span : limit), limit);
  }

  noteSweep(ctx, container.dom_path, stopped
    ? `${stopped}(활성이 된 대상 ${gained.size}) — 컨테이너 안 항목 열거는 완전하지 않을 수 있다`
    : `${visited} 위치를 훑어 재인벤토리했다(활성이 된 대상 ${gained.size}) — 컨테이너 안 항목 열거는 완전하지 않을 수 있다`,
    stopped !== null);
  return current;
}

// hover는 DOM을 바꾸므로(메뉴가 열린다) 재생 가능한 op여야 한다 — `discovery:true`인
// step으로 적고, 거기서 드러난 대상의 재생 경로에 `{action:'hover'}`가 들어간다.
async function discoverHover(ctx, run, snapshot, ops) {
  const candidates = await withDeadline(ctx.page.evaluate(() => globalThis.__interactionAudit.dom.hoverCandidates()), 'ctx.page.evaluate');
  let current = snapshot;
  let currentOps = ops;
  for (const id of candidates) {
    const key = `hover:${id}`;
    const target = ctx.targets[id];
    if (run.discovered.has(key) || !target) continue;
    // 비활성 후보는 열지 않는다 — hover는 ensureOperable을 거치지 않는 유일한 조작 경로라 여기서
    // 거르지 않으면 disabled 대상(툴팁용 mouseenter를 단 비활성 버튼)의 executed 발견 step이 남아
    // K3 반례(«비활성·가림 대상의 executed»)가 된다(최종 리뷰 검사기 I2). 후보 키는 소비하지
    // 않는다 — 뒤 상태에서 활성이 되면 그때 연다(발견은 identity당 한 번 — 활성으로 열린 한 번).
    // 지금 인벤토리에 엔트리가 없으면 활성을 확인할 수 없으므로 같은 이유로 열지 않는다.
    const entry = current.inventory.entries.find((row) => row.id === id);
    if (!entry || entry.enabled !== true) continue;
    const cap = capHit(ctx, run);
    if (cap) {
      // 상한을 넘겨 step을 늘리지 않되, 열어 보지 못한 후보는 반드시 남긴다 —
      // 큐가 마른 마지막 슬라이스에서 «거짓 완주»가 되는 자리다(수정 라운드 1 I2).
      noteCap(run, cap);
      noteLimit(ctx, 'hover-candidate', target.dom_path, `상한(${cap})으로 미실행`);
      continue;
    }
    run.discovered.add(key);
    // 후보가 창 밖에 있으면 굴려서 연다 — hover는 ensureOperable을 거치지 않는 유일한
    // 조작 경로라, 여기서 풀지 않으면 그대로 unclickable이 된다(D-B · 수정 라운드 1 Ruling).
    // A8 1차 실측(D-C 이전): 뷰포트 밖 unclickable 10건이 전부 이 hover 발견 경로였다.
    const rolled = await recoverOffscreen(ctx, current, { target: id, action: 'hover', option: null });
    if (!rolled.snapshot) {
      // 굴리는 사이 상태가 달라져 이 후보는 끝내 열지 못했다 — 후보 키는 이미 소비했으므로
      // 사유를 바꿔 다시 적는다(앞 슬라이스의 «상한으로 미실행» 행을 그 자리에서 대신한다).
      dropLimit(ctx, 'hover-candidate', target.dom_path);
      noteLimit(ctx, 'hover-candidate', target.dom_path,
        '창 밖 후보를 굴리는 사이에 상태가 달라져 열지 못했다 — 이 후보가 열 대상은 열거되지 않았다');
      return null;
    }
    if (rolled.snapshot !== current) acceptState(ctx, run, rolled.snapshot, run.stepNo, currentOps); // D-E
    current = rolled.snapshot;
    if (occludedNow(current, id)) {
      // 굴린 자리에서 후보가 가려졌다 — hover하면 엉뚱한 요소를 짚고 발견 step의 before가
      // 가림 상태로 남는다(K3 반례). 열지 못한 사실만 남긴다(수정 라운드 4 Ruling).
      dropLimit(ctx, 'hover-candidate', target.dom_path);
      noteLimit(ctx, 'hover-candidate', target.dom_path,
        '굴린 자리에서 후보가 가려져 열지 못했다 — 이 후보가 열 대상은 열거되지 않았다');
      continue;
    }
    const item = hoverItem(ctx, current, id, target, currentOps);
    const done = await performStep(ctx, run, item, run.stepNo + 1, current);
    // step이 실제로 기록된 뒤에야 앞 슬라이스의 «상한으로 미실행» 행이 거짓이 된다(N-3 ·
    // 리뷰 Important #2). performStep은 어느 갈래로도 step을 정확히 하나 남긴다.
    dropLimit(ctx, 'hover-candidate', target.dom_path);
    if (!done.snapshot) return null;
    current = done.snapshot;
    if (done.ops) currentOps = done.ops;
  }
  return current;
}

// 발견 step은 큐 항목이 아니라 «상태를 여는 절차»다 — 큐 키는 만들지 않고, K7 step이
// 요구하는 값(target·action·option·context·재생 경로)만 통상 항목과 같은 모양으로 든다.
function hoverItem(ctx, snapshot, id, target, ops) {
  const entries = snapshot.inventory.entries;
  return {
    unitKey: JSON.stringify([id, 'hover', null]),
    target: id,
    action: 'hover',
    option: null,
    context: ctx.pure.contextFor(entries, unitTarget(id, target), entries.map((entry) => entry.id)),
    prefixHash: snapshot.state_hash,
    ops,
    discovery: true,
  };
}

// 스니펫이 낸 dom_path(‹tag:nth-of-type(n)›을 '/'로 이은 자식 경로)를 루트에서 되짚어
// 그 요소를 스크롤한다('end' = 컨테이너를 끝까지 · 'view' = 대상을 보이는 자리로).
// 스크롤 컨테이너는 대상이 아닐 수 있어(스니펫 `scrollContainers`의 `id`가 null)
// identity도 clickPoint도 없으므로 경로가 유일한 손잡이다(보고서 §우려).
function scrollByDomPath(ctx, domPath, mode) {
  return withDeadline(ctx.page.evaluate(([rootSelector, path, how]) => {
    const root = document.querySelector(rootSelector);
    if (!root) return false;
    let el = root;
    for (const segment of (path ? path.split('/') : [])) {
      const parsed = /^([a-z0-9-]+):nth-of-type\((\d+)\)$/.exec(segment);
      if (!parsed) return false; // iframe[n]·overlay[n] 접두는 루트 자식 경로가 아니다
      let seen = 0;
      let found = null;
      for (const child of el.children) {
        if (child.tagName.toLowerCase() !== parsed[1]) continue;
        seen += 1;
        if (seen === Number(parsed[2])) { found = child; break; }
      }
      if (!found) return false;
      el = found;
    }
    if (how === 'view') {
      el.scrollIntoView({ block: 'center', inline: 'center' });
      return true;
    }
    // 숫자 자리 — 그 자리로 굴리고 실제로 닿은 자리와 한 «페이지» 크기를 돌려준다(D-D).
    const vertical = el.scrollHeight > el.clientHeight;
    if (vertical) el.scrollTop = how; else el.scrollLeft = how;
    return {
      vertical,
      at: vertical ? el.scrollTop : el.scrollLeft,
      page: { h: el.clientHeight, w: el.clientWidth },
      max: { top: el.scrollHeight - el.clientHeight, left: el.scrollWidth - el.clientWidth },
    };
  }, [ctx.rootSelector, domPath, mode]), 'ctx.page.evaluate');
}

const scrollIntoViewOf = (ctx, domPath) => scrollByDomPath(ctx, domPath, 'view');
const scrollContainerTo = (ctx, domPath, offset) => scrollByDomPath(ctx, domPath, offset);

// "자식 수 급증 기록"(K2) — 훑는 동안 새로 **활성**이 된 대상을 세는 입력이다
// (가상화 목록은 여기가 커진다).
function activeIds(snapshot) {
  return new Set(
    snapshot.inventory.entries.filter((entry) => entry.enabled && !entry.occluded).map((entry) => entry.id),
  );
}

// "접두 상태 해시가 현재 상태 해시와 같으면 새로고침·재생을 생략한다"(K1). 아니면
// 다시 열고 경로를 재생한다 — "각 대상을 현재 인벤토리에서 identity로 찾아 실제
// 조작·종점 before.state_hash 대조·불일치 unreachable".
async function reachState(ctx, run, item, n) {
  // "해시 일치 ∧ 계보 일치"일 때만 생략한다(D-G) — 해시는 숨은 데이터(편집 중인 사람 등)를
  // 구분하지 못해, 같은 해시의 **다른 계보** 상태를 이어 붙이면 그 뒤 step의 before가 남의
  // 데이터가 된다(5차 실측: 같은 경로 재생 50건이 «대상이 비활성»으로 unreachable).
  // 조건은 순위 ③이 쓰는 `freeToRun`과 **같은 지식**이다 — 여기서 따로 쓰면 둘이 갈린다
  // (4c 재리뷰 이월 1).
  if (run.current && freeToRun(run, item, run.current.state_hash)) {
    return { ok: true, snapshot: run.current };
  }
  run.currentPath = null; // 여기서부터 계보는 실제로 밟은 것뿐이다
  let snapshot;
  try {
    snapshot = await reload(ctx);
  } catch (err) {
    return { ok: false, snapshot: null, error: `페이지를 다시 열지 못했다: ${err.message}` };
  }
  run.currentPath = []; // 새로 연 페이지 = 초기 상태
  const applied = [];
  for (const op of item.ops) {
    const replay = await replayOperation(ctx, run, op, snapshot, applied);
    if (!replay.ok) {
      // 여기서 멈춘 상태도 before로 문서에 남는다 — 불변식대로 큐 확장 출처로 삼는다
      // (수정 라운드 1 m2).
      acceptState(ctx, run, snapshot, n, applied);
      return { ok: false, snapshot, error: replay.error };
    }
    snapshot = replay.snapshot;
    applied.push(op);
    run.currentPath = applied.map((row) => row.target);
  }
  if (snapshot.state_hash !== item.prefixHash) {
    // 종점이 다르면 그 상태도 우리가 실제로 본 상태다 — 문서에 남을 인벤토리이므로
    // 큐 확장 출처로도 삼는다.
    acceptState(ctx, run, snapshot, n, applied);
    return {
      ok: false, snapshot,
      error: `재생 종점 상태 불일치: 기대 ${item.prefixHash} 실제 ${snapshot.state_hash}`,
    };
  }
  return { ok: true, snapshot };
}

async function reload(ctx) {
  await ctx.page.goto(ctx.url.href, { waitUntil: 'load' });
  await injectSnippet(ctx);
  await waitStable(ctx);
  return inventorySnapshot(ctx);
}

async function replayOperation(ctx, run, op, snapshot, ops) {
  const entry = snapshot.inventory.entries.find((row) => row.id === op.target);
  const known = entry || snapshot.inventory.targets[op.target];
  if (!known) return { ok: false, error: `재생 중 대상을 찾지 못했다: ${op.target}` };
  if (entry && !entry.enabled) return { ok: false, error: `재생 중 대상이 비활성이다: ${op.target}` };
  if (entry && entry.occluded) {
    // 새로 연 페이지는 스크롤 컨테이너가 처음으로 돌아가 있다 — 발견 조작이 열었던
    // 자리로 다시 굴려 본다(스크롤은 state_hash를 바꾸지 않는다 — K3).
    const recovered = await recoverOccluded(ctx, snapshot, op.target);
    if (!recovered.ok) return { ok: false, error: `재생 중 가림을 풀지 못했다(${op.target}): ${recovered.reason}` };
    acceptState(ctx, run, recovered.snapshot, run.stepNo, ops); // 복구 재인벤토리도 확장 출처(D-E)
    // 가림을 푼 뒤의 인벤토리가 이 조작의 «지금 상태»다 — 갱신하지 않으면 아래 창 밖 판정과
    // occludedNow가 복구 **전** 인벤토리를 읽어, 복구에 성공한 재생을 unreachable로 뒤집는다
    // (재리뷰 C1 실측: 한 화면에서 18건 → 0건). ensureOperable의 `ready` 갱신과 같은 순서다.
    snapshot = recovered.snapshot;
  }
  // 새로 연 페이지는 문서 스크롤도 처음으로 돌아간다 — 창 밖에 놓인 지점을 굴려서 다시
  // 잰다(D-B). 굴리는 사이 상태가 달라졌으면 재생 실패이므로 호출부가 unreachable로 적는다.
  const rolled = await recoverOffscreen(ctx, snapshot, op);
  if (!rolled.snapshot) return { ok: false, error: `재생 중 ${rolled.reason}(${op.target})` };
  if (rolled.snapshot !== snapshot) acceptState(ctx, run, rolled.snapshot, run.stepNo, ops); // D-E
  if (occludedNow(rolled.snapshot, op.target)) {
    // 굴린 자리에서 새로 가려졌다 — 재생 중이므로 호출부가 unreachable로 적는다(라운드 4 Ruling).
    return { ok: false, error: `재생 중 굴린 자리에서 대상이 가려져 있다: ${op.target}` };
  }

  const outcome = await applyOperation(ctx, op);
  if (outcome.status !== 'executed') return { ok: false, error: `재생 실패(${op.action}): ${outcome.error}` };
  await settle(ctx);
  if (await navigatedUrl(ctx)) return { ok: false, error: '재생 중 이탈했다' };
  const next = await inventorySnapshot(ctx);
  if (!next.inventory.root.found) return { ok: false, error: '재생 중 루트를 잃었다' };
  return { ok: true, snapshot: next };
}

// ---------------------------------------------------------------------
// 조작 — "page.mouse.click(x,y)(clickPoint/outsidePoint 없으면 unclickable)·
// fill(K2 표본 규칙·--declared value 우선)·focus/blur·press('Escape')·selectOption".
// 지점은 스니펫이 고르고(K2 클릭 지점·바깥 지점 규칙) 요소는 그 지점에서 잡는다.
// ---------------------------------------------------------------------
async function applyOperation(ctx, op) {
  if (op.action === 'key') {
    try {
      await ctx.page.keyboard.press(op.option);
    } catch (err) {
      return { status: 'failed', error: `키 입력 실패: ${err.message}` };
    }
    return { status: 'executed', error: null };
  }

  const pointTarget = pointTargetOf(ctx, op);
  if (!pointTarget) return { status: 'unreachable', error: `owner select를 찾지 못했다: ${op.target}` };
  const point = await pointOf(ctx, op, pointTarget);
  if (!point) return { status: 'unclickable', error: '클릭 지점이 없다' };
  // 여기 닿았다는 것은 D-B 복구(recoverOffscreen)로도 창 안으로 들어오지 못했다는 뜻이다.
  if (outsideViewport(ctx, point)) {
    return { status: 'unclickable', error: `클릭 지점이 브라우저 뷰포트 밖이다(${point.x}, ${point.y})` };
  }

  if (op.action === 'click') {
    try {
      await ctx.page.mouse.click(point.x, point.y);
    } catch (err) {
      return { status: 'failed', error: `클릭 실패: ${err.message}` };
    }
    return { status: 'executed', error: null };
  }

  // 발견 조작 hover — 지점은 클릭과 같은 규칙으로 스니펫이 고른다(K2). 마우스는
  // 그 자리에 남으므로 이어지는 조작은 «메뉴가 열린 상태»에서 일어난다.
  if (op.action === 'hover') {
    try {
      await ctx.page.mouse.move(point.x, point.y);
    } catch (err) {
      return { status: 'failed', error: `hover 실패: ${err.message}` };
    }
    return { status: 'executed', error: null };
  }

  const handle = await elementAt(ctx, point);
  if (!handle) return { status: 'unclickable', error: '클릭 지점에서 요소를 찾지 못했다' };
  try {
    return await applyElementOperation(ctx, op, pointTarget, handle);
  } catch (err) {
    return { status: 'failed', error: `${op.action} 실패: ${err.message}` };
  } finally {
    await handle.dispose();
  }
}

async function applyElementOperation(ctx, op, pointTarget, handle) {
  if (op.action === 'focus') {
    await handle.focus();
    return { status: 'executed', error: null };
  }
  if (op.action === 'blur') {
    // blur 핸들러는 focus를 거친 요소에서만 돈다 — 한 조작 안에서 둘 다 일으킨다.
    await withDeadline(handle.evaluate((el) => { el.focus(); el.blur(); }), 'handle.evaluate');
    return { status: 'executed', error: null };
  }
  if (op.action === 'fill') {
    const info = await withDeadline(handle.evaluate((el, declared) => ({
      value: typeof el.value === 'string' ? el.value : '',
      placeholder: el.getAttribute('placeholder') || '',
      inputmode: el.getAttribute('inputmode') || '',
      pattern: el.getAttribute('pattern') || '',
      declared: (declared || [])
        .filter((row) => { try { return el.matches(row.selector); } catch (err) { return false; } })
        .map((row) => row.value)[0],
    }), ctx.declared.filter((row) => row && typeof row.value === 'string')), 'handle.evaluate');
    const value = fillSample(info);
    await handle.fill(value);
    // "값이 걸러져 비어도 executed로 세되 changes.values에 사실대로 남는다"(K2).
    const after = await withDeadline(handle.evaluate((el) => (typeof el.value === 'string' ? el.value : '')), 'handle.evaluate');
    return { status: 'executed', error: null, value, values: [{ target: op.target, before: info.value, after }] };
  }
  if (op.action === 'select') {
    const before = await withDeadline(handle.evaluate((el) => (typeof el.value === 'string' ? el.value : '')), 'handle.evaluate');
    await handle.selectOption({ value: op.option === null ? '' : op.option });
    const after = await withDeadline(handle.evaluate((el) => (typeof el.value === 'string' ? el.value : '')), 'handle.evaluate');
    return { status: 'executed', error: null, values: [{ target: pointTarget, before, after }] };
  }
  return { status: 'failed', error: `알 수 없는 조작: ${op.action}` };
}

function ownerSelectOf(ctx, optionId) {
  const target = ctx.targets[optionId];
  return target && target.owner ? target.owner : null;
}

// 지점을 재는 대상 — 네이티브 select 옵션만 owner select의 자리를 쓴다(K2).
function pointTargetOf(ctx, op) {
  return op.action === 'select' ? ownerSelectOf(ctx, op.target) : op.target;
}

function outsideViewport(ctx, point) {
  return point.x < 0 || point.y < 0 || point.x >= ctx.viewport[0] || point.y >= ctx.viewport[1];
}

function pointOf(ctx, op, pointTarget) {
  if (op.action === 'click' && op.option === 'outside') {
    return withDeadline(ctx.page.evaluate((id) => globalThis.__interactionAudit.dom.outsidePoint(id), op.target), 'ctx.page.evaluate');
  }
  return withDeadline(ctx.page.evaluate((id) => globalThis.__interactionAudit.dom.clickPoint(id), pointTarget), 'ctx.page.evaluate');
}

// 지점의 요소를 잡는다. 스니펫의 rect·클릭 지점은 프레임 오프셋을 이미 더한 최상위
// 문서 좌표이므로(dom_path의 `iframe[n]/` 접두와 짝) `mouse.click`은 그대로 쓰지만,
// 요소 핸들은 프레임 문서 좌표로 바꿔 그 프레임에서 다시 hit-test해야 잡힌다 —
// 최상위에서 보면 iframe 요소가 잡히고 fill/select가 그 자리에서 실패한다.
const MAX_FRAME_DEPTH = 4;

async function elementAt(ctx, point) {
  let frame = ctx.page.mainFrame();
  let x = point.x;
  let y = point.y;
  for (let depth = 0; depth <= MAX_FRAME_DEPTH; depth += 1) {
    const handle = await withDeadline(frame.evaluateHandle(([px, py]) => document.elementFromPoint(px, py), [x, y]), 'frame.evaluateHandle');
    const element = handle.asElement();
    if (!element) {
      await handle.dispose();
      return null;
    }
    const inner = await element.contentFrame(); // iframe이 아니면 null이다
    if (!inner) return element;
    const box = await element.boundingBox(); // 최상위 프레임 기준 좌표
    const border = await withDeadline(element.evaluate((el) => [el.clientLeft, el.clientTop]), 'element.evaluate');
    await element.dispose();
    if (!box) return null;
    frame = inner;
    x = point.x - box.x - border[0];
    y = point.y - box.y - border[1];
  }
  return null;
}

// "fill 표본: inputmode=numeric|decimal|tel·pattern이면 placeholder의 숫자열(없으면
// 12345678), placeholder가 형식처럼 보이면 placeholder 원문, 그 외 «검증 입력».
// --declared가 대상별 value를 줄 수 있다."(K2)
const NUMERIC_MODES = ['numeric', 'decimal', 'tel'];
const FORMAT_LIKE = /^[0-9A-Za-z@._:/\- ]+$/; // 낱말·문장이 아닌 «형식» 문자열
const FORMAT_SEPARATOR = /[-._:/@ ]/;

function fillSample(info) {
  if (typeof info.declared === 'string') return info.declared;
  if (NUMERIC_MODES.includes(info.inputmode.toLowerCase()) || info.pattern) {
    return info.placeholder.replace(/\D+/g, '') || '12345678';
  }
  if (info.placeholder && FORMAT_LIKE.test(info.placeholder) && FORMAT_SEPARATOR.test(info.placeholder)) {
    return info.placeholder;
  }
  return '검증 입력';
}

// ---------------------------------------------------------------------
// step 기록 — K7 step 블록 그대로(필드 순서 포함).
// ---------------------------------------------------------------------
function recordStep(run, item, n, outcome) {
  run.steps.push({
    n,
    path: item.ops.map((op) => op.target).concat(item.target),
    target: item.target,
    action: item.action,
    option: item.option,
    value: outcome.value === undefined ? null : outcome.value,
    context: item.context,
    status: outcome.status,
    error: outcome.error === undefined ? null : outcome.error,
    before: outcome.before,
    after: outcome.after,
    changes: outcome.changes || { added: [], removed: [], values: [] },
    navigated: outcome.navigated === undefined ? null : outcome.navigated,
    discovery: item.discovery === true, // 발견 조작(hover)만 참이다(K2 «필요 조작 아님»)
  });
  run.stepNo = n;
  // 발견(hover) step은 «필요 조작»이 아니다 — 단위로도 우선순위 카운터로도 세지 않는다(4b 리뷰 I1).
  if (outcome.status === 'executed' && item.discovery !== true) {
    run.executedUnits.add(item.unitKey);
    noteExecuted(run, item, item.prefixHash); // D-F·D-K(②·②b·④) — 라이브는 항목의 prefixHash
  }
}

function blockOf(snapshot) {
  if (!snapshot) return { inventory: [], state_hash: null };
  return {
    inventory: projectEntries(snapshot.inventory.entries, snapshot.inventory.entry_doc_fields),
    state_hash: snapshot.state_hash,
  };
}

function afterBlockOf(snapshot, shot) {
  const block = blockOf(snapshot);
  block.surface_key = snapshot.surface_key;
  if (shot) block.capture = shot;
  return block;
}

function changesOf(before, after, values) {
  const beforeIds = new Set(before.inventory.entries.map((entry) => entry.id));
  const afterIds = new Set(after.inventory.entries.map((entry) => entry.id));
  return {
    added: after.inventory.entries.filter((entry) => !beforeIds.has(entry.id)).map((entry) => entry.id),
    removed: before.inventory.entries.filter((entry) => !afterIds.has(entry.id)).map((entry) => entry.id),
    values,
  };
}

// ---------------------------------------------------------------------
// 안정 대기 — 조작 뒤 DOM이 멈출 때까지 기다린다(MutationObserver 250ms 정적·
// 최대 3s). 초기 인벤토리 앞에도 건다 — 늦게 그려지는 화면에서 content_crop과
// 초기 캡처가 어긋나는 창을 닫는다(3a 수정 라운드 1 M10).
// ---------------------------------------------------------------------
const STABLE_QUIET_MS = 250;
const STABLE_MAX_MS = 3000;

// 조작 뒤 안정화 — DOM이 멈출 때까지 기다리고, 이탈이 시작됐으면 새 문서의 load까지
// 기다린다(URL 갱신이 클릭보다 늦게 오는 경합을 없앤다).
async function settle(ctx) {
  await waitStable(ctx);
  try {
    await ctx.page.waitForLoadState('load', { timeout: STABLE_MAX_MS });
  } catch (err) {
    // 이탈이 늦거나 끊겨도 판정은 아래 navigatedUrl이 한다.
  }
}

// "조작 뒤 document/URL이 바뀌면"(K2) — 주입한 스니펫 전역이 사라진 것도 document
// 교체다(같은 URL로 다시 그려진 경우까지 잡는다).
async function navigatedUrl(ctx) {
  let alive = false;
  try {
    alive = await withDeadline(ctx.page.evaluate(() => !!globalThis.__interactionAudit), 'ctx.page.evaluate');
  } catch (err) {
    alive = false;
  }
  const url = ctx.page.url();
  return alive && url === ctx.url.href ? null : url;
}

async function waitStable(ctx) {
  try {
    await withDeadline(ctx.page.evaluate(([quiet, max]) => new Promise((resolve) => {
      let quietTimer = null;
      const finish = () => {
        clearTimeout(quietTimer);
        clearTimeout(capTimer);
        observer.disconnect();
        resolve(null);
      };
      const observer = new MutationObserver(() => {
        clearTimeout(quietTimer);
        quietTimer = setTimeout(finish, quiet);
      });
      const capTimer = setTimeout(finish, max);
      quietTimer = setTimeout(finish, quiet);
      observer.observe(document.documentElement, {
        subtree: true, childList: true, attributes: true, characterData: true,
      });
    }), [STABLE_QUIET_MS, STABLE_MAX_MS]), 'ctx.page.evaluate');
  } catch (err) {
    // 조작이 이탈을 일으키면 실행 컨텍스트가 사라진다 — 이탈 판정은 호출자 몫이다.
  }
}

// ---------------------------------------------------------------------
// buildDocument — K7 블록 그대로(필드 순서 포함). 여기가 문서의 유일한 조립 지점이다.
// ---------------------------------------------------------------------
function buildDocument(ctx, initial, explored) {
  return {
    version: 1,
    collector: {
      name: 'interaction_audit',
      snippet_sha256: ctx.snippetSha,
      driver: DRIVER_NAME,
      driver_sha256: ctx.driverSha,
      path: ctx.collectorPath,
      capabilities: ctx.capabilities,
    },
    archive_sha256: ctx.archiveSha,
    entrypoint: { path: entrypointPathOf(ctx), sha256: ctx.entrypointSha },
    url: ctx.url.href,
    browser_viewport: [ctx.viewport[0], ctx.viewport[1]],
    content_crop: ctx.crop,
    root: initial.root,
    outside_root: initial.outside_root,
    excluded_regions: ctx.excludedRegions,
    served: sortedKeys(ctx.served),
    declared: ctx.declared,
    declared_unmatched: initial.declared_unmatched,
    observed_at: new Date().toISOString().replace(/\.\d+Z$/, 'Z'),
    targets: ctx.targets,
    initial: initial.block,
    steps: explored.steps,
    discovery_limits: ctx.discoveryLimits,
    partial: explored.partial,
    caps_hit: explored.capsHit,
    environment_error: null,
  };
}

// "percent-decode한 url basename = entrypoint basename을 요구한다"(K3).
function entrypointPathOf(ctx) {
  return decodeURIComponent(path.posix.basename(ctx.url.pathname));
}

function writeDocument(ctx, doc) {
  fs.mkdirSync(path.dirname(ctx.out), { recursive: true });
  fs.writeFileSync(ctx.out, `${JSON.stringify(doc, null, 2)}\n`);
}

function summarize(ctx, doc, steps, partial, capsHit, environmentError) {
  if (!doc) {
    return { targets: 0, executed: 0, residual: [], surfaces: 0, partial, capsHit, environmentError };
  }
  const surfaces = new Set([doc.initial.surface_key]);
  for (const step of steps) {
    if (step.after && step.after.surface_key) surfaces.add(step.after.surface_key);
  }
  return {
    targets: Object.keys(doc.targets).length,
    executed: steps.filter((step) => step.status === 'executed').length,
    residual: ctx.pure.residual(doc),
    surfaces: surfaces.size,
    partial,
    capsHit,
    environmentError,
  };
}

// 테스트 전용 내보내기 — 꺼내는 순서(D-F·D-F′·D-G)와 카운터 규칙은 브라우저 없이 고정해야
// 판별력이 있다(리뷰 I-1·I-2). 진입점은 default export 하나 그대로이며(K5), 이 객체는
// 드라이버 동작에 관여하지 않는다.
export const _internals = {
  takeNext, recordStep, restoreVisited, noteExecuted, acceptState, samePath, NO_REPLAY_STREAK,
};

// ---------------------------------------------------------------------
// 작은 도구
// ---------------------------------------------------------------------
function sha256Buffer(bytes) {
  return crypto.createHash('sha256').update(bytes).digest('hex');
}

function sha256File(file) {
  return sha256Buffer(fs.readFileSync(file));
}

function relativePosix(from, to) {
  return path.relative(from, to).split(path.sep).join('/');
}

function sortedKeys(record) {
  const out = {};
  for (const key of Object.keys(record).sort()) out[key] = record[key];
  return out;
}
