// fixtures_sdk.sh 보조 — 실제 assets/sdk_boundary.js 를 Node vm 의 DOM 대역에서 평가하고, 가로챈 gateway 호출
// `Kakao.API.request({url})` 마다 기록기의 정규 경로·승인 판정을 JSON 으로 낸다(원 SDK 함수는 부르지 않는다).
// 사용: node boundary_probe.cjs <sdk_boundary.js> <url 목록 JSON 파일>
const fs = require('fs');
const vm = require('vm');
const src = fs.readFileSync(process.argv[2], 'utf8');
const urls = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const c = { URL, ArrayBuffer, FormData, Blob, console, sent: [], opened: [], cleaned: 0, realCalls: 0 };
c.HTMLFormElement = class { submit() { c.sent.push(this.action); } requestSubmit() { c.sent.push(this.action); } };
c.HTMLInputElement = class {};
c.document = { addEventListener() {} };
c.location = { href: 'http://localhost/' };
c.navigator = { userActivation: { isActive: true } };
c.window = { open(u) { c.opened.push(u); } };
c.window.Kakao = {
  init() { this.ready = true; },
  isInitialized: () => true,
  API: { request: () => { c.realCalls += 1; }, cleanup: () => { c.cleaned += 1; } },
};
vm.createContext(c);
c.cfg = {
  global: 'Kakao', init: 'init', namespaces: ['API'], members: { API: { request: 'gateway', cleanup: 'lifecycle' } },
  gatewayPaths: { 'API.request': ['/v2/user/me'] }, apiPaths: { 'API.request': ['/v2/user/me', '/v1/user/unlink'] },
  operatorDomains: ['kakao.com', 'kakaocdn.net'],
};
vm.runInContext('(' + src + ')(cfg)', c);
const st = c.window.__dddjangoSdkBoundary;
const out = [];
for (const url of urls) {
  c.window.Kakao.API.request({ url });
  const rec = st.calls[st.calls.length - 1];
  out.push({ url, path: rec.path, pathOk: rec.pathOk });
}
c.window.Kakao.API.cleanup();
process.stdout.write(JSON.stringify({
  installed: st.installed, results: out, realCalls: c.realCalls, cleaned: c.cleaned,
  findings: st.findings().filter((f) => f.startsWith('gateway 경로가 승인 밖')).length,
}) + '\n');
