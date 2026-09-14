// observe_interactions.mjs — 조작 상태 수집 드라이버의 Node 래퍼 (dddjango-web).
//
// 인자 파싱 · 선언 파일 검증 · Playwright 모듈 해소 · 브라우저 기동(channel 또는
// --cdp) 뒤 형제 assets/observe_interactions.pw.js의 observe(page, opts)를 부른다(K5).
// 아무것도 설치하지 않으며 저장소에 node_modules를 만들지 않는다.
//
// 사용:
//   node observe_interactions.mjs --url U --root SEL --viewport 560x1040 --crop-root \
//     --entrypoint-sha S --archive-sha S --out F [--captures-dir D] [--declared F] \
//     [--excluded-regions F] [--hover-selectors F] [--playwright-module DIR] \
//     [--browser-channel chrome | --cdp WS] [--max-steps N --max-depth N --max-minutes N] [--resume]
//
// env 폴백: DDDJANGO_WEB_PLAYWRIGHT_MODULE · DDDJANGO_WEB_BROWSER_CHANNEL · DDDJANGO_WEB_BROWSER_CDP
// stdout = 1행 JSON 요약. exit 0 완료 / 3 partial / 1 환경 오류·드라이버 오류.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import observe from '../assets/observe_interactions.pw.js';

const MODULE_GUIDE = '--playwright-module <dir> 또는 DDDJANGO_WEB_PLAYWRIGHT_MODULE 필요';
const VALUE_ARGS = {
  '--url': 'url', '--root': 'root', '--viewport': 'viewport',
  '--entrypoint-sha': 'entrypointSha', '--archive-sha': 'archiveSha', '--out': 'out',
  '--captures-dir': 'capturesDir', '--declared': 'declaredFile',
  '--excluded-regions': 'excludedRegionsFile', '--hover-selectors': 'hoverSelectorsFile',
  '--playwright-module': 'playwrightModule', '--browser-channel': 'browserChannel', '--cdp': 'cdp',
  '--max-steps': 'maxSteps', '--max-depth': 'maxDepth', '--max-minutes': 'maxMinutes',
};
const FLAG_ARGS = { '--crop-root': 'cropToRoot', '--resume': 'resume' };
const REQUIRED = [
  ['url', '--url'], ['root', '--root'], ['viewport', '--viewport'],
  ['entrypointSha', '--entrypoint-sha'], ['archiveSha', '--archive-sha'], ['out', '--out'],
];

// 사용자 입력·환경 때문에 수집을 시작할 수 없는 조건. 드라이버의 EnvironmentError와
// 같은 등급(exit 1 + environmentError)이며, 프로그래머 오류와는 구별한다.
class CliError extends Error {}

function parseArgs(argv) {
  const args = { cropToRoot: false, resume: false };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (FLAG_ARGS[token]) {
      args[FLAG_ARGS[token]] = true;
    } else if (VALUE_ARGS[token]) {
      i += 1;
      if (i >= argv.length) throw new CliError(`${token} 값이 없다`);
      args[VALUE_ARGS[token]] = argv[i];
    } else {
      throw new CliError(`알 수 없는 인자: ${token}`);
    }
  }
  for (const [key, flag] of REQUIRED) {
    if (!args[key]) throw new CliError(`${flag} 필수`);
  }
  return args;
}

function parseViewport(raw) {
  const match = /^(\d+)x(\d+)$/.exec(raw);
  if (!match) throw new CliError(`--viewport 형식은 WxH여야 한다: ${raw}`);
  return [Number(match[1]), Number(match[2])];
}

function readJsonArray(file, flag) {
  if (!file) return [];
  try {
    const parsed = JSON.parse(fs.readFileSync(file, 'utf8'));
    if (!Array.isArray(parsed)) throw new Error('최상위가 배열이 아니다');
    return parsed;
  } catch (err) {
    throw new CliError(`${flag} 파일을 읽을 수 없다: ${file}(${err.message})`);
  }
}

// K3는 excluded_regions를 «selector·사유» 선언으로 규정한다 — 문자열 배열을 주면
// 제외가 조용히 무효가 되므로 행 모양을 여기서 막는다(수정 라운드 1 M8).
function readExcludedRegions(file) {
  const rows = readJsonArray(file, '--excluded-regions');
  for (const row of rows) {
    if (!row || typeof row.selector !== 'string' || typeof row.reason !== 'string') {
      throw new CliError(`excluded_regions 행 모양은 {selector, reason}이어야 한다: ${JSON.stringify(row)}`);
    }
  }
  return rows;
}

function loadChromium(moduleDir) {
  if (!moduleDir) throw new CliError(MODULE_GUIDE);
  try {
    const requireFromModule = createRequire(path.join(moduleDir, 'package.json'));
    return requireFromModule(moduleDir).chromium;
  } catch (err) {
    throw new CliError(`${MODULE_GUIDE}(${moduleDir}: ${err.message})`);
  }
}

// "드라이버는 loopback이 아닌 URL을 거부하되 --cdp로 붙은 브라우저의 현재 origin은
// 허용한다"(K2) — 허용 근거와 관찰 주체가 같아야 하므로 우리가 쓸 컨텍스트에서 읽는다.
function connectedOrigin(context) {
  for (const page of context.pages()) {
    try {
      const url = new URL(page.url());
      if (url.protocol === 'http:' || url.protocol === 'https:') return url.origin;
    } catch (err) { /* about:blank 등은 origin이 없다 */ }
  }
  return null;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const [width, height] = parseViewport(args.viewport);
  // 파일 읽기·검증은 기동 앞이다 — 실패해도 정리할 브라우저가 없다(수정 라운드 1 M3).
  const declared = readJsonArray(args.declaredFile, '--declared');
  const excludedRegions = readExcludedRegions(args.excludedRegionsFile);
  const hoverSelectors = readJsonArray(args.hoverSelectorsFile, '--hover-selectors');

  const cdp = args.cdp || process.env.DDDJANGO_WEB_BROWSER_CDP || '';
  const channel = args.browserChannel || process.env.DDDJANGO_WEB_BROWSER_CHANNEL || 'chrome';
  const chromium = loadChromium(args.playwrightModule || process.env.DDDJANGO_WEB_PLAYWRIGHT_MODULE || '');

  let browser = null;
  let context = null;
  let ownsContext = false; // 우리가 만든 컨텍스트만 우리가 닫는다
  let page = null;
  try {
    let allowOrigin = null;
    if (cdp) {
      // 인증 필요 원본을 여는 유일한 경로다(K2) — 새 컨텍스트를 만들면 사용자
      // 프로필의 쿠키·스토리지를 잃으므로 기존 컨텍스트 안에 page만 연다. 기존 컨텍스트가
      // 없을 때만 만들고, 그것은 사용자 것이 아니므로 끝에 닫는다(3a 재리뷰 이월).
      browser = await connect(chromium, cdp);
      context = browser.contexts()[0] || null;
      if (!context) {
        context = await browser.newContext();
        ownsContext = true;
      }
      allowOrigin = connectedOrigin(context);
      page = await context.newPage();
      await page.setViewportSize({ width, height });
    } else {
      browser = await launch(chromium, channel);
      context = await browser.newContext({ viewport: { width, height }, reducedMotion: 'reduce' });
      ownsContext = true;
      page = await context.newPage();
    }

    const summary = await observe(page, {
      url: args.url,
      rootSelector: args.root,
      browserViewport: [width, height],
      cropToRoot: args.cropToRoot,
      entrypointSha: args.entrypointSha,
      archiveSha: args.archiveSha,
      out: args.out,
      capturesDir: args.capturesDir,
      declared,
      excludedRegions,
      hoverSelectors,
      maxSteps: args.maxSteps,
      maxDepth: args.maxDepth,
      maxMinutes: args.maxMinutes,
      resume: args.resume,
      path: 'node',
      listeners: 'cdp',
      allowOrigin,
    });
    if (summary.environmentError) return { payload: summary, code: 1, stderr: summary.environmentError };
    return { payload: summary, code: summary.partial ? 3 : 0, stderr: null };
  } finally {
    // --cdp로 붙은 브라우저와 그 기존 컨텍스트는 사용자 것이다 — 우리가 연 page와 우리가 만든
    // 컨텍스트만 닫는다.
    if (page) await page.close().catch(() => {});
    if (ownsContext && context) await context.close().catch(() => {});
    if (!cdp && browser) await browser.close().catch(() => {});
  }
}

async function launch(chromium, channel) {
  try {
    return await chromium.launch({ channel, headless: true });
  } catch (err) {
    throw new CliError(`브라우저 기동 실패: channel ${channel}(${err.message})`);
  }
}

async function connect(chromium, endpoint) {
  try {
    return await chromium.connectOverCDP(endpoint);
  } catch (err) {
    throw new CliError(`브라우저 기동 실패: --cdp ${endpoint}(${err.message})`);
  }
}

function finish(payload, code, stderrLine) {
  if (stderrLine) process.stderr.write(`${stderrLine}\n`);
  process.exitCode = code;
  process.stdout.write(`${JSON.stringify(payload)}\n`, () => process.exit(code));
}

try {
  const result = await main();
  finish(result.payload, result.code, result.stderr);
} catch (err) {
  if (err instanceof CliError) {
    finish({
      targets: 0, executed: 0, residual: [], surfaces: 0, partial: false, capsHit: [],
      environmentError: err.message,
    }, 1, err.message);
  } else {
    // 프로그래머 오류를 «환경 blocked»로 둔갑시키지 않는다(수정 라운드 1 M4).
    process.stderr.write(`드라이버 오류: ${err.stack}\n`);
    finish({ driver_error: err.message }, 1, null);
  }
}
