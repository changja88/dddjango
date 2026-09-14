// interaction_audit.js(dddjango-web · dom) 브라우저 회귀 테스트 — node:test + Playwright.
// 실행: DDDJANGO_WEB_PLAYWRIGHT_MODULE=<playwright 디렉터리> DDDJANGO_WEB_BROWSER_CHANNEL=chrome \
//         node --test dddjango-web/scripts/test/test_observe_interactions.mjs
// 대상 규범: workspace/design/2026-09-13-web-interaction-evidence.md K1·K2·K3·K5·K7.
// SKIP 의미론은 이 파일이 소유한다(K5 «모듈 env가 있을 때 실행하고 없으면 SKIP + 사유»):
//   모듈 env 미설정 → `SKIP: …` 1줄 + exit 0, 단 DDDJANGO_WEB_REQUIRE_BROWSER=1이면 ERROR: 접두 + exit 1.
// 그룹은 describe 단위로 덧붙인다(현재 inventory·skeleton·explore·discovery).
import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import http from 'node:http';
import fs from 'node:fs';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import observe, { _internals } from '../../assets/observe_interactions.pw.js';

const SKIP_LINE = 'SKIP: DDDJANGO_WEB_PLAYWRIGHT_MODULE 미설정';
const moduleDir = process.env.DDDJANGO_WEB_PLAYWRIGHT_MODULE;
if (!moduleDir) {
  if (process.env.DDDJANGO_WEB_REQUIRE_BROWSER === '1') {
    console.error(`ERROR: ${SKIP_LINE}`);
    process.exit(1);
  }
  console.log(SKIP_LINE);
  process.exit(0);
}

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURE_DIR = path.join(__dirname, 'fixtures', 'interaction');
const SNIPPET = path.join(__dirname, '..', '..', 'assets', 'interaction_audit.js');
const ROOT_SELECTOR = '[data-screen-label="fixture"]';
const WRAPPER = path.join(__dirname, '..', 'observe_interactions.mjs');

const requirePlaywright = createRequire(path.join(moduleDir, 'package.json'));
const { chromium } = requirePlaywright(moduleDir);
const pure = createRequire(import.meta.url)('../../assets/interaction_audit.js');

// broken.html — 파일 없이 라우트로만 서빙한다(외부 스크립트 로드 실패 전용 페이지).
// 루트는 있고 <script src="missing.js">만 404라서, 드라이버가 «루트 미발견»으로
// 오진하는지 «스크립트 로드 실패»로 바로 잡는지를 가른다.
const BROKEN_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>broken</title></head>',
  '<body><div data-screen-label="broken"><button type="button">확인</button></div>',
  '<script src="missing.js"></script></body></html>',
].join('');

// small.html — 상한·재개 전용 최소 화면(라우트로만 서빙한다). 조작해도 상태가 바뀌지
// 않는 버튼 6개라 큐가 6 항목에서 끝난다 — fixture.html은 상태 차원이 곱해져 큐가
// 현실적으로 마르지 않으므로 «완주(exit 0)»를 고정할 수 있는 화면이 따로 필요하다.
const SMALL_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>small</title></head>',
  '<body><div data-screen-label="small">',
  ['하나', '둘', '셋', '넷', '다섯', '여섯']
    .map((label) => `<button type="button" onclick="void 0">${label}</button>`).join(''),
  '</div></body></html>',
].join('');

// cover.html — 자기 rect가 후손 대상 rect에 완전히 덮인 요소 전용 화면(라우트 서빙).
// 클릭 지점이 없어 unclickable이고 K2가 "실행 아님·잔여"로 못 박으므로, 잔여 0을
// 요구하는 fixture.html에 둘 수 없다.
const COVER_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>cover</title>',
  '<style>#cover{display:inline-flex}#cover button{margin:0}</style></head>',
  '<body><div data-screen-label="cover">',
  '<span id="cover" aria-label="덮개" onclick="void 0"><button type="button" onclick="void 0">덮개 안 버튼</button></span>',
  '</div></body></html>',
].join('');

// wizard.html — «같은 identity·다른 context» 전용 화면(라우트 서빙). 단계마다 다른
// 대상이 하나씩 있어 «다음»의 context_T가 3갈래로 갈리고, 상태가 3개뿐이라 큐가 마른다.
const WIZARD_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>wizard</title></head><body>',
  '<div data-screen-label="wizard">',
  '<div id="w1"><button type="button" onclick="go(2)">다음</button></div>',
  '<div id="w2" hidden><button type="button" onclick="go(1)">이전</button>',
  '<button type="button" onclick="go(3)">다음</button></div>',
  '<div id="w3" hidden><button type="button" onclick="go(1)">처음으로</button>',
  '<button type="button" onclick="go(1)">다음</button></div>',
  '</div>',
  '<script>function go(n){for(var i=1;i<=3;i++){document.getElementById("w"+i).hidden=(i!==n);}}<\/script>',
  '</body></html>',
].join('');

// drop.html — 조작이 루트를 통째로 없애는 화면(라우트 서빙). 이탈이 아닌데 루트가
// 사라지는 경로를 K7 안에서 처리하는지(=드라이버 예외로 새지 않는지) 고정한다.
const DROP_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>drop</title></head><body>',
  '<div id="root" data-screen-label="drop">',
  '<button type="button" onclick="document.getElementById(\'root\').remove()">루트 제거</button>',
  '</div></body></html>',
].join('');

// deep.html — 깊이 ≥ 2 + 같은 path의 focus/fill/blur가 공존하는 화면(라우트 서빙).
// resume이 부모 step을 path만으로 고르면 서로 덮어써 엉뚱한 조작을 재생한다.
const DEEP_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>deep</title></head><body>',
  '<div data-screen-label="deep">',
  '<button type="button" onclick="openForm()">열기</button>',
  '<div id="form" hidden><label for="name">이름</label><input id="name" oninput="sync()">',
  '<button type="button" id="save" hidden onclick="show(\'done\')">저장</button>',
  '<div id="done" hidden><button type="button" onclick="hide(\'done\')">확인</button></div>',
  '<div id="extra" hidden><button type="button" onclick="hide(\'extra\')">덧보기</button></div>',
  '<button type="button" onclick="hide(\'form\')">닫기</button></div>',
  '</div>',
  '<script>',
  'function show(id){document.getElementById(id).hidden=false;}',
  'function hide(id){document.getElementById(id).hidden=true;}',
  'function sync(){document.getElementById("save").hidden=document.getElementById("name").value==="";}',
  // 이름이 채워진 상태에서 «열기»를 다시 누를 때만 «덧보기»가 드러난다 — 그 step은
  // 이미 실행한 단위(우선순위 ③)라 focus/blur가 기록된 뒤에야 돌아온다.
  'function openForm(){show("form");if(document.getElementById("name").value!==""){show("extra");}}',
  '<\/script></body></html>',
].join('');

// cascade-select.html — 부모 native select 값에 따라 자식 select의 option 목록이 갈리는
// 화면(라우트 서빙). 누적 targets로 확장하면 부모가 «나»일 때 «가»의 옵션을 고르려 든다.
const CASCADE_SELECT_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>cascade</title></head><body>',
  '<div data-screen-label="cascade">',
  '<label for="parent">부모</label>',
  '<select id="parent" onchange="fillChild()"><option value="">선택</option>',
  '<option value="a">가</option><option value="b">나</option></select>',
  '<label for="child">자식</label><select id="child"><option value="">선택</option></select>',
  '</div>',
  '<script>function fillChild(){',
  'var value=document.getElementById("parent").value;',
  'var child=document.getElementById("child");',
  'var items=value==="a"?["a1","a2","a3"]:value==="b"?["b1","b2"]:[];',
  'child.textContent="";',
  'var head=document.createElement("option");head.value="";head.textContent="선택";child.appendChild(head);',
  'items.forEach(function(v){var o=document.createElement("option");o.value=v;o.textContent=v;child.appendChild(o);});',
  '}<\/script></body></html>',
].join('');

// cascade-flat.html — 자식 옵션 이름이 전부 같아 자식 select의 face가 변하지 않는
// cascade(라우트 서빙). 그러면 부모 옵션 단위의 context_T(= 자기 face를 뺀 나머지
// face들)가 고정이라 한 번 실행한 부모 옵션은 다시 큐에 들지 않는다 — 자식 옵션이
// 관찰된 상태로 돌아갈 다른 이유가 없으므로, 재개가 first_seen_step 상태에서 그
// 옵션을 되넣지 않으면 영구 잔여가 된다. 부모 이름은 서로 달라 상태 해시는 갈린다.
const CASCADE_FLAT_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>flat</title></head><body>',
  '<div data-screen-label="flat">',
  '<label for="parent">부모</label>',
  '<select id="parent" onchange="fillChild()"><option value="">선택</option>',
  '<option value="a">가</option><option value="b">나</option></select>',
  '<label for="child">자식</label><select id="child"><option value="">값</option></select>',
  '</div>',
  '<script>function fillChild(){',
  'var value=document.getElementById("parent").value;',
  'var child=document.getElementById("child");',
  'var items=value==="a"?["a1","a2","a3"]:value==="b"?["b1","b2"]:[];',
  'child.textContent="";',
  'var head=document.createElement("option");head.value="";head.textContent="값";child.appendChild(head);',
  'items.forEach(function(v){var o=document.createElement("option");o.value=v;o.textContent="값";child.appendChild(o);});',
  '}<\/script></body></html>',
].join('');

// late-break.html — 조작이 404 스크립트를 뒤늦게 끌어오는 화면(라우트 서빙).
// 로드 창 밖 로드 오류의 처분(step failed·문서 보존)을 고정한다.
const LATE_BREAK_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>late</title></head><body>',
  '<div data-screen-label="late">',
  '<button type="button" onclick="var s=document.createElement(\'script\');s.src=\'missing2.js\';document.body.appendChild(s);">불러오기</button>',
  '</div></body></html>',
].join('');

// discovery.html — 발견 채널 전용 화면(라우트 서빙). 세 갈래를 한 화면에 모은다:
//   ① addEventListener 전용 요소(#ael) — CDP 리스너 열거가 없으면 대상이 아니다.
//   ② mouseenter 리스너로만 열리는 메뉴(#more → #menu) — hover 발견 없이는 항목을 못 본다.
//   ③ overflow 컨테이너(#list) 끝의 버튼 2개 — 스크롤 발견 없이는 가려진 채로 남는다.
//      뒤 버튼이 상태를 바꾸므로 앞 버튼은 «패널 열기»를 거친 경로의 재생(새로고침)에서도
//      실행돼야 한다 — 스크롤이 처음으로 돌아간 것을 풀지 않으면 그 대상은 가려진 채라
//      재생이 서거나(«비활성») 엉뚱한 요소를 눌러 K3 반례(«가림 대상의 executed»)가 된다.
const DISCOVERY_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>discovery</title><style>',
  '#list{height:56px;width:220px;overflow-y:auto;border:1px solid #ccc}#list p{margin:4px}',
  '#menu{width:140px;border:1px solid #999}',
  '</style></head><body><div data-screen-label="discovery">',
  '<div id="ael">리스너만</div>',
  '<button type="button" id="more">더보기</button>',
  '<div id="menu" role="menu" aria-label="더보기 메뉴" hidden>',
  '<button type="button" role="menuitem" onclick="closeMenu()">복제</button></div>',
  '<div id="list"><p>항목 1</p><p>항목 2</p><p>항목 3</p>',
  '<button type="button" id="bottom" onclick="void 0">아래 버튼</button>',
  '<button type="button" id="opener" onclick="openPanel()">패널 열기</button></div>',
  '<div id="panel" hidden><button type="button" onclick="closePanel()">닫기</button></div>',
  '</div><script>',
  'function closeMenu(){document.getElementById("menu").hidden=true;}',
  'function openPanel(){document.getElementById("panel").hidden=false;}',
  'function closePanel(){document.getElementById("panel").hidden=true;}',
  'document.getElementById("ael").addEventListener("click",function(){',
  'document.body.dataset.clicks=String((Number(document.body.dataset.clicks)||0)+1);});',
  'document.getElementById("more").addEventListener("mouseenter",function(){',
  'document.getElementById("menu").hidden=false;});',
  '<\/script></body></html>',
].join('');

// tall.html — 루트가 브라우저 창보다 길어 아래쪽 대상의 클릭 지점이 창 밖에 놓이는
// 화면(라우트 서빙). hover 발견 후보(#more)가 창 아래 y>400에 있어, 굴려 보지 않으면 그
// 조작이 «클릭 지점이 브라우저 뷰포트 밖»으로 unclickable이 되고 메뉴 항목은 열거조차
// 되지 않는다(A8 드라이런 1차 실측 unclickable 10건 — 드라이런 결정 D-B).
const TALL_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>tall</title>',
  '<style>#pad{height:700px;background:#eee}#menu{width:140px;border:1px solid #999}</style>',
  '</head><body><div data-screen-label="tall">',
  '<button type="button" id="head" onclick="void 0">머리 버튼</button>',
  '<div id="pad">여백</div>',
  '<button type="button" id="more">더보기</button>',
  '<div id="menu" role="menu" aria-label="더보기 메뉴" hidden>',
  '<button type="button" role="menuitem" onclick="closeMenu()">복제</button></div>',
  '<button type="button" id="bottom" onclick="void 0">아래 버튼</button>',
  '</div><script>',
  'function closeMenu(){document.getElementById("menu").hidden=true;}',
  'document.getElementById("more").addEventListener("mouseenter",function(){',
  'document.getElementById("menu").hidden=false;});',
  '<\/script></body></html>',
].join('');

// resume-cap.html — 발견 대상(overflow 컨테이너·hover 후보)이 **첫 step 뒤에** 드러나는
// 화면(라우트 서빙). --max-steps 1로 끊으면 패널을 연 직후 상한에 걸려 둘 다 «상한으로
// 미실행» 행만 남는다. --resume이 실제로 열면 그 행은 거짓이 되므로 사라져야 한다(3c N-3).
const RESUME_CAP_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>resume cap</title><style>',
  '#list{height:56px;width:220px;overflow-y:auto;border:1px solid #ccc}#list p{margin:4px}',
  '#menu{width:140px;border:1px solid #999}</style></head>',
  '<body><div data-screen-label="resume-cap">',
  '<button type="button" id="open" onclick="openPanel()">열기</button>',
  '<div id="panel" hidden>',
  '<div id="list"><p>항목 1</p><p>항목 2</p><p>항목 3</p>',
  '<button type="button" id="bottom" onclick="void 0">아래 버튼</button></div>',
  '<button type="button" id="more">더보기</button>',
  '<div id="menu" role="menu" aria-label="더보기 메뉴" hidden>',
  '<button type="button" role="menuitem" onclick="closeMenu()">복제</button></div>',
  '</div></div><script>',
  'function openPanel(){document.getElementById("panel").hidden=false;}',
  'function closeMenu(){document.getElementById("menu").hidden=true;}',
  'document.getElementById("more").addEventListener("mouseenter",function(){',
  'document.getElementById("menu").hidden=false;});',
  '<\/script></body></html>',
].join('');

// scroll-sweep.html — 항목 20개짜리 스크롤 컨테이너(높이 = 항목 5개분). 끝으로만 굴리면
// 처음 5·끝 5만 활성이라 중간 10개는 어떤 인벤토리에도 활성으로 나오지 않아 큐에 못 든다
// (A8 드라이런 2차 실측: 시·도 메뉴 17항목 중 처음 6·끝 3만 실행 — 드라이런 결정 D-D).
// 컨테이너 밖으로 밀린 항목이 창 «안»에 남아야 가림으로 빠진다(창 밖이면 D-B′로 활성이라
// 이 결함이 가려진다) — 그래서 여백으로 컨테이너를 창 한가운데에 두고 큰 창에서 본다.
const SWEEP_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>sweep</title><style>',
  '#spacer{height:320px;background:#f6f6f6}',
  '#list{height:100px;width:200px;overflow-y:auto;border:1px solid #ccc}',
  '#list button{display:block;box-sizing:border-box;margin:0;width:100%;height:20px;padding:0;font:12px/1 system-ui}',
  '</style></head><body><div data-screen-label="sweep"><div id="spacer">여백</div><div id="list">',
  Array.from({ length: 20 }, (v, i) => `<button type="button" onclick="void 0">항목 ${i + 1}</button>`).join(''),
  '</div></div></body></html>',
].join('');

// hidden-state.html — 상태 해시가 구분하지 못하는 «숨은 데이터»(편집 중인 사람) 화면(라우트 서빙).
// 두 사람의 단계 1은 대상·값이 똑같아 해시도 context도 같고(그래서 큐 키가 하나로 합쳐진다),
// 차이는 단계 2에서 도시 트리거의 활성 여부로만 드러난다. 해시만 보고 재생을 생략하면 한 계보의
// 항목이 다른 계보의 페이지에서 실행돼 그 step의 after가 남의 데이터가 되고, 그 상태에서 넣은
// 항목은 나중에 «재생 종점 상태 불일치»로 죽는다(A8 5차 실측 50건 — 드라이런 결정 D-G).
// 단계 1은 «다음»을 먼저 두어 입력 9단위가 연속 상한(D-F ③)을 넘기게 한다 — 그때 다른 사람 행이
// 꺼내져 페이지가 옮겨 간 채로 «다음»이 남는 것이 오염이 일어나는 자리다.
const HIDDEN_STATE_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>hidden</title>',
  '<style>#city-menu{width:120px;border:1px solid #999}</style></head>',
  '<body><div data-screen-label="hidden">',
  '<div id="list">',
  '<button type="button" onclick="edit(\'A\')">김가 수정</button>',
  '<button type="button" onclick="edit(\'B\')">이나 수정</button></div>',
  '<div id="form" hidden>',
  '<div id="s1"><button type="button" id="next" onclick="go2()">다음</button>',
  '<label for="who">이름</label><input id="who" value="이름">',
  '<label for="tel">전화</label><input id="tel" value="010">',
  '<label for="note">비고</label><input id="note" value="비고"></div>',
  '<div id="s2" hidden>',
  '<label for="memo">메모</label><input id="memo">',
  '<button type="button" id="city" aria-haspopup="menu" aria-expanded="false"',
  ' aria-controls="city-menu" onclick="openCity()">도시 선택</button>',
  '<div id="city-menu" role="menu" aria-label="도시 메뉴" hidden>',
  '<button type="button" role="menuitem" onclick="pickCity()">진주시</button></div>',
  '<button type="button" id="back" onclick="back()">닫기</button></div></div>',
  '</div><script>',
  'var who=null;',
  'function edit(p){who=p;document.getElementById("list").hidden=true;',
  'document.getElementById("form").hidden=false;',
  'document.getElementById("s1").hidden=false;document.getElementById("s2").hidden=true;}',
  'function go2(){document.getElementById("s1").hidden=true;',
  'document.getElementById("s2").hidden=false;',
  'document.getElementById("city").disabled=(who==="A");}',
  'function openCity(){var m=document.getElementById("city-menu");m.hidden=!m.hidden;',
  'document.getElementById("city").setAttribute("aria-expanded",String(!m.hidden));}',
  'function pickCity(){document.getElementById("city").textContent="진주시";openCity();}',
  'function back(){document.getElementById("form").hidden=true;',
  'document.getElementById("list").hidden=false;',
  'document.getElementById("city").textContent="도시 선택";',
  'document.getElementById("city").disabled=false;}',
  '<\/script></body></html>',
].join('');

// cascade-starve.html — A8 «시·도 → 시·군» 판형(라우트 서빙). 부모·자식이 커스텀 트리거+메뉴이고
// 부모를 고르면 자식 메뉴는 **닫힌 채** 다시 만들어지므로, 자식 항목은 «그 부모 값 상태에서 자식
// 트리거를 다시 누르는» 조작으로만 드러난다. 그 조작은 단위로는 이미 실행돼 ①에서 밀리고, 얕은
// 폼 재실행(메모·라디오)이 ③⑤⑥을 계속 이겨 큐에서 굶는다(드라이런 4차 실측 — 결정 D-F ②).
const CASCADE_STARVE_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>starve</title>',
  '<style>#parent-menu,#child-menu{width:120px;border:1px solid #999}</style></head>',
  '<body><div data-screen-label="starve">',
  '<button type="button" id="parent" aria-haspopup="menu" aria-expanded="false"',
  ' aria-controls="parent-menu" onclick="toggle(\'parent-menu\')">부모 선택</button>',
  '<div id="parent-menu" role="menu" aria-label="부모 메뉴" hidden>',
  ['가', '나', '다'].map((v) => `<button type="button" role="menuitem" onclick="pick('${v}')">${v}</button>`).join(''),
  '</div>',
  '<button type="button" id="child" aria-haspopup="menu" aria-expanded="false"',
  ' aria-controls="child-menu" onclick="toggle(\'child-menu\')">자식 선택</button>',
  '<div id="child-menu" role="menu" aria-label="자식 메뉴" hidden></div>',
  '<label for="memo">메모</label><input id="memo">',
  '<label><input type="radio" name="sex" value="m">남</label>',
  '<label><input type="radio" name="sex" value="f">여</label>',
  '</div><script>',
  'function toggle(id){var m=document.getElementById(id);m.hidden=!m.hidden;',
  'document.querySelector(\'[aria-controls="\'+id+\'"]\').setAttribute("aria-expanded",String(!m.hidden));}',
  'function pick(v){document.getElementById("parent").textContent=v;',
  'var items=v==="가"?["a1","a2","a3","a4"]:v==="나"?["b1","b2","b3"]:["c1","c2"];',
  'var m=document.getElementById("child-menu");m.textContent="";',
  'items.forEach(function(x){var b=document.createElement("button");b.type="button";',
  'b.setAttribute("role","menuitem");b.textContent=x;b.addEventListener("click",function(){',
  'document.getElementById("child").textContent=x;toggle("child-menu");});m.appendChild(b);});',
  'm.hidden=true;document.getElementById("child").setAttribute("aria-expanded","false");',
  'toggle("parent-menu");}',
  '<\/script></body></html>',
].join('');

// replay-occluded.html — 재생 접두(prefix op)가 **스크롤 컨테이너 안 가려진 항목**인 화면
// (라우트 서빙). 새로 연 페이지는 컨테이너가 처음으로 돌아가 그 항목이 가려져 있으므로,
// 재생이 가림 복구를 거친다. 복구 뒤 인벤토리로 판정하지 않으면 복구에 성공한 재생이 전부
// unreachable이 된다(재리뷰 C1 — A8의 «시·도 항목을 누른 뒤 시·군» cascade와 같은 판형).
const REPLAY_OCCLUDED_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>replay</title><style>',
  '#list{height:60px;width:200px;overflow-y:auto;border:1px solid #ccc}',
  '#list button{display:block;box-sizing:border-box;margin:0;width:100%;height:20px;padding:0;font:12px/1 system-ui}',
  '</style></head><body><div data-screen-label="replay"><div id="list">',
  [1, 2, 3, 4, 5, 6, 7].map((n) => `<button type="button" onclick="void 0">항목 ${n}</button>`).join(''),
  '<button type="button" id="open" onclick="openExtra()">여는 항목</button>',
  [9, 10].map((n) => `<button type="button" onclick="void 0">항목 ${n}</button>`).join(''),
  '</div>',
  '<div id="extra" hidden><button type="button" onclick="void 0">덧보기</button>',
  '<button type="button" onclick="closeExtra()">닫기</button></div>',
  '</div><script>',
  'function openExtra(){document.getElementById("extra").hidden=false;}',
  'function closeExtra(){document.getElementById("extra").hidden=true;}',
  '<\/script></body></html>',
].join('');

// sweep-drift.html — 첫 컨테이너를 훑는 «도중»에 상태가 달라지는 화면(라우트 서빙).
// 스크롤 리스너가 #extra를 드러내 해시가 바뀌므로 훑기가 그 자리에서 중단된다. 그때 옛
// 스냅샷을 지금 상태로 올리면 **둘째 컨테이너**가 첫 위치에서 곧바로 «상태가 달라졌다»로
// 떨어져 통째로 미훑기가 된다(재리뷰 I2).
const SWEEP_DRIFT_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>drift</title><style>',
  '.box{height:40px;width:200px;overflow-y:auto;border:1px solid #ccc;margin-bottom:6px}',
  '.box button{display:block;box-sizing:border-box;margin:0;width:100%;height:20px;padding:0;font:12px/1 system-ui}',
  '</style></head><body><div data-screen-label="drift">',
  '<div id="a" class="box">',
  [1, 2, 3, 4, 5, 6].map((n) => `<button type="button" onclick="void 0">가 ${n}</button>`).join(''),
  '</div><div id="b" class="box">',
  [1, 2, 3, 4, 5, 6].map((n) => `<button type="button" onclick="void 0">나 ${n}</button>`).join(''),
  '</div>',
  '<div id="extra" hidden><button type="button" onclick="void 0">덧보기</button></div>',
  '</div><script>',
  'document.getElementById("a").addEventListener("scroll",function(){',
  'document.getElementById("extra").hidden=false;},{once:true});',
  '<\/script></body></html>',
].join('');

// sweep-late-drift.html — 컨테이너를 **먼저 완주로 훑고 나중 상태에서 중단**하는 화면
// (라우트 서빙). «리스너 달기»가 표식을 드러내 상태를 가르고, 그때 붙는 scroll 리스너가
// 다음 훑기 도중 #extra를 드러내 훑기를 중단시킨다. 한계 행 사유가 «완주»로 남으면
// 리뷰어는 잘린 영역이 있다는 사실을 잃는다(리뷰 Minor 1 — 중단 사유가 이겨야 한다).
// 컨테이너 안은 대상이 아닌 <p> 3개(2 위치)다 — 항목이 대상이면 상태 × 항목 재실행이 곱해져
// 시험 하나가 30초를 넘겼다(4d 재리뷰 Minor 4). 단언은 «완주 1회 + 중단 1회»면 충분하다.
const SWEEP_LATE_DRIFT_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>late drift</title><style>',
  'body{margin:0}#list{height:40px;width:200px;overflow-y:auto;border:1px solid #ccc}',
  '#list p{display:block;box-sizing:border-box;margin:0;height:20px;font:12px/1 system-ui}',
  '</style></head><body><div data-screen-label="late-drift">',
  '<button type="button" id="arm" onclick="arm()">리스너 달기</button>',
  '<button type="button" id="mark" hidden onclick="void 0">표식</button>',
  '<div id="list"><p>항목 1</p><p>항목 2</p><p>항목 3</p></div>',
  '<div id="extra" hidden><button type="button" onclick="void 0">덧보기</button></div>',
  '</div><script>',
  'function arm(){document.getElementById("mark").hidden=false;',
  'document.getElementById("list").addEventListener("scroll",function(){',
  'document.getElementById("extra").hidden=false;},{once:true});}',
  '<\/script></body></html>',
].join('');

// barred.html — 창 밖 대상을 굴린 «자리»에서 새로 가려지는 화면(라우트 서빙). 문서가 짧아
// scrollIntoView({block:'center'})가 끝까지만 굴리고, 그 자리에서 #deep이 창 아래 고정 막대
// 뒤로 들어간다. 굴리기 전 인벤토리로만 가림을 판정하면 그대로 눌러 K3 반례
// «가림 대상의 executed»가 된다(수정 라운드 3 실측 → 라운드 4 Ruling).
const BARRED_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>barred</title><style>',
  '#pad{height:700px;background:#eee}',
  '#bar{position:fixed;left:0;right:0;bottom:0;height:120px;background:#fff;z-index:5}',
  '</style></head><body><div data-screen-label="barred">',
  '<button type="button" id="head" onclick="void 0">머리 버튼</button>',
  '<div id="pad">여백</div>',
  '<button type="button" id="deep" onclick="void 0">아래 버튼</button>',
  '<div id="bar"></div>',
  '</div></body></html>',
].join('');

// revive.html — «복구 재인벤토리에서만 활성»인 대상 전용 화면(라우트 서빙). #hidden은 창
// 아래에 고정된 막대에 덮여 초기에는 가림(비활성)이고, 창 밖 #deep을 굴려 잡는 복구
// 재인벤토리에서만 활성이 된다 — #deep의 클릭이 스크롤을 되돌리므로 after에서는 다시
// 가려진다. 그 인벤토리를 큐 확장 출처로 삼지 않으면 영구 잔여가 된다(드라이런 결정 D-E).
const REVIVE_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>revive</title><style>',
  '#screen{position:relative}#pad{height:700px;background:#eee}#tail{height:400px}',
  '#hidden{position:absolute;top:350px;left:8px}',
  '#bar{position:fixed;left:0;right:0;bottom:0;height:120px;background:#fff;z-index:5}',
  '</style></head><body><div id="screen" data-screen-label="revive">',
  '<button type="button" id="head" onclick="void 0">머리 버튼</button>',
  '<button type="button" id="hidden" onclick="void 0">가림 버튼</button>',
  '<div id="pad">여백</div>',
  '<button type="button" id="deep" onclick="window.scrollTo(0,0)">아래 버튼</button>',
  // 꼬리 여백 — 문서가 충분히 길어야 #deep을 창 한가운데로 굴릴 수 있다(끝까지 굴려도
  // 모자라면 #deep이 고정 막대 뒤로 들어가 버린다 — 보고서 R3 우려 ②).
  '<div id="tail"></div>',
  '<div id="bar"></div>',
  '</div></body></html>',
].join('');

// hover-drift.html — 창 밖 hover 후보를 굴리는 «사이»에 상태가 달라지는 화면(라우트 서빙).
// scrollIntoView가 일으킨 스크롤이 새 대상을 드러내 상태 해시가 바뀌므로 복구가 중단된다.
// 후보 키는 이미 소비돼 재시도가 없으니, 그 사실이 discovery_limits에 남아야 한다(리뷰 I#2).
const HOVER_DRIFT_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>hover drift</title>',
  '<style>#pad{height:700px;background:#eee}#menu{width:140px;border:1px solid #999}</style>',
  '</head><body><div data-screen-label="hover-drift">',
  '<button type="button" id="head" onclick="void 0">머리 버튼</button>',
  '<div id="pad">여백</div>',
  '<button type="button" id="more">더보기</button>',
  '<div id="menu" role="menu" aria-label="더보기 메뉴" hidden>',
  '<button type="button" role="menuitem" onclick="void 0">복제</button></div>',
  '<div id="extra" hidden><button type="button" onclick="void 0">스크롤로 드러남</button></div>',
  '</div><script>',
  'window.addEventListener("scroll",function(){document.getElementById("extra").hidden=false;},{once:true});',
  'document.getElementById("more").addEventListener("mouseenter",function(){',
  'document.getElementById("menu").hidden=false;});',
  '<\/script></body></html>',
].join('');

// frame-host.html — same-origin iframe 안 대상 전용 화면(라우트 서빙). 클릭은 최상위
// 좌표로 닿지만 fill/focus/blur는 프레임 문서로 내려가 요소를 잡아야 한다.
const FRAME_HOST_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>frame host</title>',
  '<style>#frame{width:220px;height:56px;border:0}</style></head>',
  '<body><div data-screen-label="frame-host">',
  '<iframe id="frame" src="frame-input.html" title="프레임"></iframe>',
  '</div></body></html>',
].join('');

const FRAME_INPUT_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>frame input</title>',
  '<style>body{margin:4px;overflow:hidden;font:14px/1.4 system-ui,-apple-system,sans-serif}</style></head>',
  '<body><label for="fi">프레임 입력</label><input id="fi"></body></html>',
].join('');

// tabs.html — 상호배타 토글(탭)로 «숨은 옛 표식»을 만드는 화면(라우트 서빙).
// 두 패널의 요소 수·모양이 같아 state A(p2)에서 매긴 표식과 state B(p1)에서 매긴 표식이
// 같은 번호를 쓴다. 옛 표식이 남으면 문서 순서상 뒤(p2)가 그 번호를 차지해 ⑴ 리스너를
// 가진 p2 요소의 결과가 p1의 무리스너 <span>에 붙고(유령 handler 대상) ⑵ 진짜
// addEventListener 요소는 표에서 빠진다(K2 «핸들러 보유 = 대상» 위반).
const TABS_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>tabs</title></head><body>',
  '<div data-screen-label="tabs">',
  '<button type="button" id="t1" onclick="show(1)">1단계</button>',
  '<button type="button" id="t2" onclick="show(2)">2단계</button>',
  '<div id="p1" hidden><div id="live">진짜 리스너</div><span id="plain">그냥 글</span></div>',
  '<div id="p2"><span id="s2">보조 글</span><button type="button" id="save" onclick="bump()">저장</button></div>',
  '</div><script>',
  'function show(n){document.getElementById("p1").hidden=(n!==1);document.getElementById("p2").hidden=(n!==2);}',
  'function bump(){document.body.dataset.clicks=String((Number(document.body.dataset.clicks)||0)+1);}',
  'document.getElementById("live").addEventListener("click",bump);',
  '<\/script></body></html>',
].join('');

// sweep-state.html — **같은 dom_path 컨테이너가 상태마다 다른 항목 목록을 갖는** 화면
// (라우트 서빙 · A8 «시·도 → 시·군» 판형). 자식 메뉴는 부모 값에 따라 다시 채워지므로
// 부모 «가» 상태의 a1~a6와 부모 «나» 상태의 b1~b6가 같은 요소 자리를 쓴다. 훑기를
// dom_path 전역으로 한 번만 하면 뒤 상태의 목록은 컨테이너에 가려진 채 어느 인벤토리에도
// 활성으로 나오지 않아 큐에 들지 못한다(드라이런 6차 실측 시·군 145/153 — 결정 B2).
// 항목 클릭은 메뉴만 닫아 상태 차원이 곱해지지 않게 한다(부모 값 3 × 메뉴 2 × 2).
const SWEEP_STATE_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>sweep state</title><style>',
  'body{margin:0}#cm{height:60px;width:160px;overflow-y:auto;border:1px solid #999}',
  '#cm button{display:block;box-sizing:border-box;margin:0;width:100%;height:20px;padding:0;font:12px/1 system-ui}',
  '</style></head><body><div data-screen-label="sweepstate">',
  ['가', '나'].map((v) => `<button type="button" onclick="pick('${v}')">${v}</button>`).join(''),
  '<button type="button" id="chosen" hidden onclick="void 0">고른 값</button>',
  '<button type="button" id="c" aria-haspopup="menu" aria-expanded="false"',
  ' aria-controls="cm" onclick="toggle()">자식 선택</button>',
  '<div id="cm" role="menu" aria-label="자식 메뉴" hidden></div>',
  '</div><script>',
  'function toggle(){var m=document.getElementById("cm");m.hidden=!m.hidden;',
  'document.getElementById("c").setAttribute("aria-expanded",String(!m.hidden));}',
  'function closeChild(){var m=document.getElementById("cm");m.hidden=true;',
  'document.getElementById("c").setAttribute("aria-expanded","false");}',
  // 고른 값이 화면에 남아 두 부모 상태가 갈린다(A8의 시·도 face 자리). 자식 메뉴는
  // **닫힌 채** 다시 만들어지므로 다시 열면 컨테이너가 처음 자리로 돌아간다.
  'function pick(v){var chosen=document.getElementById("chosen");',
  'chosen.hidden=false;chosen.textContent=v;',
  'var items=v==="가"?["a1","a2","a3","a4","a5","a6"]:["b1","b2","b3","b4","b5","b6"];',
  'var m=document.getElementById("cm");m.textContent="";',
  'items.forEach(function(x){var b=document.createElement("button");b.type="button";',
  'b.setAttribute("role","menuitem");b.textContent=x;',
  'b.addEventListener("click",closeChild);m.appendChild(b);});closeChild();}',
  '<\/script></body></html>',
].join('');

// register.html — «같은 identity의 입력이 다른 화면에서 이미 채워진» 등록 흐름(라우트 서빙).
// 수정 흐름이 먼저 탐색되면서 «이름» fill·«다음» click 단위가 executed가 되므로, 등록
// 흐름에서는 둘 다 ①(미실행)을 잃고 ⑥(늦게 들어온 항목)만 남아 «다음» 재실행이 빈 이름
// fill을 이긴다 — 그러면 등록 흐름은 단계를 넘지 못한다(드라이런 6차 실측 — 결정 O1).
const REGISTER_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>register</title></head><body>',
  '<div data-screen-label="register">',
  '<div id="list"><button type="button" onclick="open_(\'new\')">등록</button>',
  '<button type="button" onclick="open_(\'edit\')">수정</button></div>',
  // 흐름마다 표식 대상이 하나씩 있어야 두 화면의 상태가 갈린다 — 상태 해시는 값이 아니라
  // value_empty만 보므로, 표식이 없으면 이름을 채운 등록 화면이 수정 화면과 한 상태가 된다.
  '<div id="new" hidden><button type="button" onclick="void 0">새 관계인</button>',
  '<label for="nn">이름</label><input id="nn">',
  '<button type="button" onclick="go()">다음</button></div>',
  '<div id="edit" hidden><button type="button" onclick="void 0">기존 관계인</button>',
  '<label for="en">이름</label><input id="en" value="김가">',
  '<button type="button" onclick="void 0">다음</button></div>',
  '<div id="stage2" hidden><button type="button" onclick="void 0">완료</button></div>',
  '</div><script>',
  'function open_(id){document.getElementById("list").hidden=true;',
  'document.getElementById(id).hidden=false;}',
  // 이름이 비어 있으면 넘어가지 않는다 — 진행 조건이 곧 빈 입력 fill이다.
  'function go(){if(document.getElementById("nn").value===""){return;}',
  'document.getElementById("new").hidden=true;document.getElementById("stage2").hidden=false;}',
  '<\/script></body></html>',
].join('');

// leap-toggle.html — role 없는 <label> 핸들러 체크박스(라우트 서빙). 클릭마다 자기
// class가 바뀌어 surface(자기 tag·class·텍스트 sha)가 갈린다. 이름이 있는 handler를
// 토글형으로 보지 않으면 click 1회로 끝나 «켜진 상태»가 관찰되지 않는다(결정 D-H —
// A8의 «윤달·몰라요·못려요»가 전부 이 판형이다).
const LEAP_TOGGLE_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>leap</title>',
  '<style>#leap{display:inline-block;border:1px solid #333;padding:2px}',
  '#leap.on{background:#333;color:#fff}</style></head>',
  '<body><div data-screen-label="leap">',
  '<label id="leap" onclick="this.classList.toggle(\'on\')">윤달</label>',
  '</div></body></html>',
].join('');

// inline-toggle.html — A8 Checkbox 판형(라우트 서빙): 켜짐이 root class가 아니라 자식
// span의 인라인 style(background)과 추가된 <i class="icon-check"> 아이콘으로만 그려진다
// (class는 어디도 바뀌지 않는다) — 결정 D-J. 둘째 label «인라인만»은 자식 추가 없이
// style만 바뀌는 대조군이다.
const INLINE_TOGGLE_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>inline toggle</title></head>',
  '<body><div data-screen-label="inline">',
  '<label id="leap" onclick="toggle()">',
  '<span id="box" style="background:#ddd;border:1px solid #999"></span>',
  '<span>윤달에 태어났어요</span>',
  '</label>',
  '<label id="onlyInline" onclick="toggleInlineOnly()">',
  '<span id="box2" style="background:#ddd"></span>',
  '<span>인라인만</span>',
  '</label>',
  '</div>',
  '<script>',
  // setAttribute로 style 전체를 다시 쓴다(.style.background= 는 브라우저가 CSSOM으로
  // 나머지 선언까지 재직렬화해 최초 HTML 리터럴과 문자열이 달라진다 — 실측: on/off를
  // 오가도 의미상 같은 꺼짐 상태의 raw style 문자열이 갈려 surface가 3갈래로 샜다).
  'var leapOn=false;',
  'function toggle(){',
  'var box=document.getElementById("box");leapOn=!leapOn;',
  'box.setAttribute("style", leapOn ? "background:#c33;border:1px solid #999" : "background:#ddd;border:1px solid #999");',
  'if(leapOn){var icon=document.createElement("i");icon.className="icon-check";',
  'icon.setAttribute("aria-hidden","true");box.appendChild(icon);}',
  'else{var icon=box.querySelector("i.icon-check");if(icon){icon.parentNode.removeChild(icon);}}',
  '}',
  'var onlyOn=false;',
  'function toggleInlineOnly(){',
  'var box2=document.getElementById("box2");onlyOn=!onlyOn;',
  'box2.setAttribute("style", onlyOn ? "background:#c33" : "background:#ddd");',
  '}',
  '<\/script>',
  '</body></html>',
].join('');

// svg-toggle.html — 켜짐이 자식 `<svg>`의 class로만 그려지는 handler(라우트 서빙). SVG 요소의
// `className`은 문자열이 아니라 SVGAnimatedString이라 스니펫 `surfaceClassNameOf`가
// `getAttribute('class')`로 내려가야 두 상태의 surface가 갈린다(4f 리뷰 Minor — 그 분기를
// 실제로 지나는 브라우저 시험이 없었다). 루트 label의 class·style·텍스트는 두 상태에서 같다.
const SVG_TOGGLE_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>svg toggle</title></head>',
  '<body><div data-screen-label="svg">',
  '<label id="star" onclick="toggleStar()">',
  '<svg class="ico" width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M6 1l5 10H1z"></path></svg>',
  '<span>즐겨찾기</span>',
  '</label>',
  '</div>',
  '<script>',
  'function toggleStar(){var ico=document.querySelector("#star svg");',
  'ico.setAttribute("class", ico.getAttribute("class")==="ico" ? "ico on" : "ico");}',
  '<\/script>',
  '</body></html>',
].join('');

// closer.html — 조작이 **페이지 자체를 없애는** 화면(라우트 서빙). «창 닫기»는 테스트가
// 미리 걸어 둔 바인딩(window.__closeMe)을 불러 page를 닫는다 — window.close()는 Chromium이
// history 2항목(newPage의 about:blank + goto)이라 막으므로 쓰지 않는다(컨트롤러 실측).
// 관찰면은 외부 종료(브라우저 kill)와 같다: click은 성공하고 곧 page.isClosed()가 참이 되며
// 이후 evaluate/goto가 «Target page, context or browser has been closed»로 깨진다.
// 6차 실측: 그 순간부터 남은 큐 2470건이 1초 안에 unreachable로 비워지고 문서가
// partial:false·exit 0(«완주»)으로 쓰였다 — 드라이런 결정 D-I가 막는 자리다.
const CLOSER_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>closer</title></head><body>',
  '<div data-screen-label="closer">',
  '<button type="button" id="a" onclick="void 0">가</button>',
  '<button type="button" id="b" onclick="void 0">나</button>',
  '<button type="button" id="x" onclick="window.__closeMe && window.__closeMe()">창 닫기</button>',
  '</div></body></html>',
].join('');

// closer-last.html — «창 닫기»가 **큐의 마지막 항목**인 화면(라우트 서빙). 닫는 조작 뒤 큐가
// 비어 루프가 정상 종료하므로 pop 앞 `isClosed()` 검사로는 잡히지 않는다 — 그 step 뒤의
// 발견 조작(스크롤·hover)이 통째로 생략됐는데 문서가 partial:false로 «완주»라고 말하는
// 자리다(4d 재리뷰 Minor 1).
const CLOSER_LAST_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>closer last</title></head><body>',
  '<div data-screen-label="closer-last">',
  '<button type="button" id="x" onclick="window.__closeMe && window.__closeMe()">창 닫기</button>',
  '</div></body></html>',
].join('');

// closer-scroll.html — **발견 조작(스크롤 훑기) 중에** 페이지가 사라지는 화면(라우트 서빙).
// 컨테이너의 첫 scroll 이벤트가 page를 닫는다. 훑기의 evaluate가 닫힌 page에서 던지면 그
// 예외가 observe 밖으로 새어 문서가 아예 쓰이지 않던 자리다(4d 재리뷰 범위 밖 2).
const CLOSER_SCROLL_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>closer scroll</title><style>',
  'body{margin:0}#list{height:40px;width:200px;overflow-y:auto;border:1px solid #ccc}',
  '#list button{display:block;box-sizing:border-box;margin:0;width:100%;height:20px;padding:0;font:12px/1 system-ui}',
  '</style></head><body><div data-screen-label="closer-scroll">',
  '<div id="list">',
  [1, 2, 3, 4].map((n) => `<button type="button" onclick="void 0">항목 ${n}</button>`).join(''),
  '</div></div><script>',
  'document.getElementById("list").addEventListener("scroll",function(){',
  'if(window.__closeMe){window.__closeMe();}},{once:true});',
  '<\/script></body></html>',
].join('');

// hover-cap.html — hover 후보가 둘인 화면(라우트 서빙). --max-steps 1로 끊으면 첫 후보만
// 열리고 둘째는 열어 보지도 못한다 — 그 사실이 caps_hit·discovery_limits에 남아야 한다.
const HOVER_CAP_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>hover cap</title></head><body>',
  '<div data-screen-label="hover-cap">',
  '<button type="button" id="h1">하나</button>',
  '<div id="m1" role="menu" aria-label="하나 메뉴" hidden><button type="button" role="menuitem">항목 1</button></div>',
  '<button type="button" id="h2">둘</button>',
  '<div id="m2" role="menu" aria-label="둘 메뉴" hidden><button type="button" role="menuitem">항목 2</button></div>',
  '</div><script>',
  'document.getElementById("h1").addEventListener("mouseenter",function(){document.getElementById("m1").hidden=false;});',
  'document.getElementById("h2").addEventListener("mouseenter",function(){document.getElementById("m2").hidden=false;});',
  '<\/script></body></html>',
].join('');

// root-scroll.html — **루트 자체**가 스크롤 컨테이너인 화면(라우트 서빙 — 긴 모바일 화면의 흔한
// 배치). 스니펫 `scrollContainers`는 루트 record(domPath '')도 내므로 드라이버가 그 행을
// dom_path ''로 적으면 검사기(nonempty 요구)가 exit 2로 거짓 결함을 낸다(최종 리뷰 검사기 I1).
const ROOT_SCROLL_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>root scroll</title><style>',
  '#screen{height:300px;overflow-y:auto;border:1px solid #ccc}#pad{height:1700px;background:#f6f6f6}',
  '</style></head><body><div id="screen" data-screen-label="root-scroll">',
  '<button type="button" onclick="void 0">머리 버튼</button>',
  '<div id="pad">여백</div>',
  '<button type="button" onclick="void 0">아래 버튼</button>',
  '</div></body></html>',
].join('');

// hover-disabled.html — hover 신호(onmouseenter)를 가진 **disabled** 버튼과 정상 hover 트리거가
// 함께 있는 화면(라우트 서빙). hover 발견은 ensureOperable을 거치지 않으므로 비활성 후보를
// 거르지 않으면 «비활성 대상의 executed» 발견 step이 남아 검사기 exit 2다(최종 리뷰 검사기 I2).
const HOVER_DISABLED_HTML = [
  '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>hover disabled</title></head><body>',
  '<div data-screen-label="hover-disabled">',
  '<button type="button" id="off" disabled onmouseenter="void 0">비활성 도움말</button>',
  '<button type="button" id="more" onmouseenter="document.getElementById(\'menu\').hidden=false">더보기</button>',
  '<div id="menu" role="menu" aria-label="더보기 메뉴" hidden><button type="button" role="menuitem" onclick="void 0">복제</button></div>',
  '<button type="button" onclick="void 0">정상 버튼</button>',
  '</div></body></html>',
].join('');

const ctx = { server: null, browser: null, base: '', requests: [], smallHtml: SMALL_HTML };

before(async () => {
  ctx.server = http.createServer((req, res) => {
    const rel = decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname).replace(/^\/+/, '');
    ctx.requests.push({ path: rel, cookie: req.headers.cookie || '' });
    if (rel === 'favicon.ico') { // 브라우저 자동 요청 — 404 잡음을 만들지 않는다
      res.writeHead(204);
      res.end();
      return;
    }
    if (rel === 'broken.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(BROKEN_HTML);
      return;
    }
    if (rel === 'small.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(ctx.smallHtml);
      return;
    }
    if (rel === 'cover.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(COVER_HTML);
      return;
    }
    if (rel === 'wizard.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(WIZARD_HTML);
      return;
    }
    if (rel === 'drop.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(DROP_HTML);
      return;
    }
    if (rel === 'deep.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(DEEP_HTML);
      return;
    }
    if (rel === 'cascade-select.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(CASCADE_SELECT_HTML);
      return;
    }
    if (rel === 'cascade-flat.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(CASCADE_FLAT_HTML);
      return;
    }
    if (rel === 'late-break.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(LATE_BREAK_HTML);
      return;
    }
    if (rel === 'discovery.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(DISCOVERY_HTML);
      return;
    }
    if (rel === 'tabs.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(TABS_HTML);
      return;
    }
    if (rel === 'hover-cap.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(HOVER_CAP_HTML);
      return;
    }
    if (rel === 'tall.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(TALL_HTML);
      return;
    }
    if (rel === 'resume-cap.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(RESUME_CAP_HTML);
      return;
    }
    if (rel === 'scroll-sweep.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(SWEEP_HTML);
      return;
    }
    if (rel === 'closer.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(CLOSER_HTML);
      return;
    }
    if (rel === 'closer-last.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(CLOSER_LAST_HTML);
      return;
    }
    if (rel === 'closer-scroll.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(CLOSER_SCROLL_HTML);
      return;
    }
    if (rel === 'svg-toggle.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(SVG_TOGGLE_HTML);
      return;
    }
    if (rel === 'sweep-state.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(SWEEP_STATE_HTML);
      return;
    }
    if (rel === 'register.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(REGISTER_HTML);
      return;
    }
    if (rel === 'leap-toggle.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(LEAP_TOGGLE_HTML);
      return;
    }
    if (rel === 'inline-toggle.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(INLINE_TOGGLE_HTML);
      return;
    }
    if (rel === 'hidden-state.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(HIDDEN_STATE_HTML);
      return;
    }
    if (rel === 'cascade-starve.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(CASCADE_STARVE_HTML);
      return;
    }
    if (rel === 'replay-occluded.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(REPLAY_OCCLUDED_HTML);
      return;
    }
    if (rel === 'sweep-late-drift.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(SWEEP_LATE_DRIFT_HTML);
      return;
    }
    if (rel === 'sweep-drift.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(SWEEP_DRIFT_HTML);
      return;
    }
    if (rel === 'barred.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(BARRED_HTML);
      return;
    }
    if (rel === 'revive.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(REVIVE_HTML);
      return;
    }
    if (rel === 'root-scroll.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(ROOT_SCROLL_HTML);
      return;
    }
    if (rel === 'hover-disabled.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(HOVER_DISABLED_HTML);
      return;
    }
    if (rel === 'hover-drift.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(HOVER_DRIFT_HTML);
      return;
    }
    if (rel === 'frame-host.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(FRAME_HOST_HTML);
      return;
    }
    if (rel === 'frame-input.html') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(FRAME_INPUT_HTML);
      return;
    }
    const file = path.join(FIXTURE_DIR, rel);
    if (!file.startsWith(FIXTURE_DIR) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
      res.end('not found');
      return;
    }
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end(fs.readFileSync(file));
  });
  await new Promise((resolve) => ctx.server.listen(0, '127.0.0.1', resolve));
  ctx.base = `http://127.0.0.1:${ctx.server.address().port}`;
  ctx.browser = process.env.DDDJANGO_WEB_BROWSER_CDP
    ? await chromium.connectOverCDP(process.env.DDDJANGO_WEB_BROWSER_CDP)
    : await chromium.launch({ channel: process.env.DDDJANGO_WEB_BROWSER_CHANNEL || 'chrome', headless: true });
});

after(async () => {
  if (ctx.browser) await ctx.browser.close();
  if (ctx.server) await new Promise((resolve) => ctx.server.close(resolve));
});

// ---- 공용 헬퍼 ------------------------------------------------------------
async function openFixture(t) {
  const page = await ctx.browser.newPage({ viewport: { width: 1000, height: 1400 } });
  const noise = [];
  page.on('console', (m) => noise.push(`[${m.type()}] ${m.text()}`));
  page.on('pageerror', (e) => noise.push(`[pageerror] ${e.message}`));
  t.after(async () => {
    await page.close();
    assert.deepEqual(noise, [], '픽스처 페이지가 콘솔 잡음을 냈다');
  });
  await page.goto(`${ctx.base}/fixture.html`, { waitUntil: 'load' });
  await page.addScriptTag({ path: SNIPPET });
  return page;
}

const inventory = (page, opts = {}) =>
  page.evaluate(
    ([selector, o]) => globalThis.__interactionAudit.dom.inventory(selector, o),
    [ROOT_SELECTOR, { capabilities: { cdp_listeners: false }, excludedRegions: ['#knobs'], ...opts }],
  );

const rectOf = (page, selector) =>
  page.evaluate((s) => {
    const r = document.querySelector(s).getBoundingClientRect();
    return { x: r.left, y: r.top, w: r.width, h: r.height };
  }, selector);

const sha256File = (file) => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const sha256Text = (text) => crypto.createHash('sha256').update(text).digest('hex');
const fixtureSha = () => sha256File(path.join(FIXTURE_DIR, 'fixture.html'));
const nameIn = (doc, id) => (doc.targets[id] || {}).name;

// 임시 build 디렉터리 — 저장소에 산출물을 남기지 않는다(K5 "임시 캡처는 os.tmpdir()").
function tempBuild(t, screen = 'fixture') {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ia-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return { dir, capturesDir: path.join(dir, 'captures'), out: path.join(dir, 'captures', `${screen}-interactions.json`) };
}

// 픽스처 서버는 이 프로세스가 돌린다 — 래퍼를 동기로 띄우면 이벤트 루프가 막혀
// 자식의 요청에 응답하지 못한다. 그래서 비동기 spawn으로만 부른다.
function runWrapper(args, env = process.env) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, args, { env });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('close', (status) => resolve({ status, stdout, stderr }));
  });
}

const pngSize = (file) => {
  const bytes = fs.readFileSync(file);
  assert.equal(bytes.subarray(0, 8).toString('hex'), '89504e470d0a1a0a', `PNG가 아니다: ${file}`);
  return { w: bytes.readUInt32BE(16), h: bytes.readUInt32BE(20) };
};

// K7 문서 블록이 단일 출처다 — 순서까지 고정해 필드 누락·잉여를 둘 다 잡는다.
const DOC_KEYS = [
  'version', 'collector', 'archive_sha256', 'entrypoint', 'url', 'browser_viewport', 'content_crop',
  'root', 'outside_root', 'excluded_regions', 'served', 'declared', 'declared_unmatched',
  'observed_at', 'targets', 'initial', 'steps', 'discovery_limits', 'partial', 'caps_hit',
  'environment_error',
];

const named = (inv, name) => Object.entries(inv.targets).filter(([, t]) => t.name === name);
const kinded = (inv, kind) => Object.entries(inv.targets).filter(([, t]) => t.kind === kind);
const entryOf = (inv, id) => inv.entries.find((e) => e.id === id);
const outside = (pt, r) => pt.x < r.x || pt.x > r.x + r.w || pt.y < r.y || pt.y > r.y + r.h;

// =====================================================================
// inventory — dom.markCandidates/inventory/clickPoint/outsidePoint/
//             hoverCandidates/scrollContainers (K2 대상 열거 · K3 루트 규칙)
// =====================================================================
describe('inventory', () => {
  test('초기 인벤토리 — 루트·행 4·«다음» 1·트리거 2·disabled·토스트·iframe·select', async (t) => {
    const page = await openFixture(t);
    const inv = await inventory(page);

    assert.equal(inv.root.selector, ROOT_SELECTOR);
    assert.equal(inv.root.found, true);
    assert.equal(inv.root.fingerprint.tag, 'div');
    assert.equal(inv.root.fingerprint.label, 'fixture');
    assert.ok(inv.root.fingerprint.descendants > 20, `descendants=${inv.root.fingerprint.descendants}`);
    assert.ok(inv.root.fingerprint.rect.w > 0 && inv.root.fingerprint.rect.h > 0);
    assert.deepEqual(inv.outside_root, { count: 0, sample: [] }); // #knobs 제외 선언

    // 행 4 — 이름이 같아 identity가 충돌하므로 dom_path로 갈라져야 한다(K1).
    const rows = named(inv, '삭제');
    assert.equal(rows.length, 4);
    assert.equal(new Set(rows.map(([id]) => id)).size, 4);
    for (const [id, target] of rows) {
      assert.equal(target.kind, 'button');
      assert.deepEqual(target.found_by, ['semantic', 'onclick']); // CHANNEL_ORDER 순서
      assert.equal(entryOf(inv, id).enabled, true);
      assert.equal(entryOf(inv, id).occluded, false);
    }

    // 같은 이름 «다음» 위저드 — 보이는 1단계만 열거된다.
    assert.equal(named(inv, '다음').length, 1);

    // cascade 트리거 2(role=combobox·aria-haspopup 두 경로) — face는 표시 텍스트.
    const triggers = kinded(inv, 'trigger');
    assert.deepEqual(triggers.map(([, t]) => t.name).sort(), ['시·군', '시·도']);
    for (const [id] of triggers) assert.equal(entryOf(inv, id).face, '선택');

    // disabled 버튼 — 열거하되 enabled:false.
    const save = named(inv, '저장');
    assert.equal(save.length, 1);
    assert.equal(entryOf(inv, save[0][0]).enabled, false);

    // role=status 안 액션 버튼 — live:true로 열거된다.
    const undo = named(inv, '실행 취소');
    assert.equal(undo.length, 1);
    assert.equal(undo[0][1].live, true);
    assert.equal(entryOf(inv, undo[0][0]).live, true);

    // same-origin iframe — dom_path 앞에 iframe[0]/.
    const frameBtn = named(inv, '프레임 버튼');
    assert.equal(frameBtn.length, 1);
    assert.ok(frameBtn[0][1].dom_path.startsWith('iframe[0]/'), frameBtn[0][1].dom_path);
    assert.ok(entryOf(inv, frameBtn[0][0]).rect.x > 0);

    // native select — 옵션 3은 owner=select·value 보유 대상(entries 밖).
    const selects = kinded(inv, 'select');
    assert.equal(selects.length, 1);
    assert.equal(selects[0][1].name, '관계');
    assert.equal(entryOf(inv, selects[0][0]).face, '선택');
    const options = kinded(inv, 'option');
    assert.equal(options.length, 3);
    assert.deepEqual(options.map(([, t]) => t.value), ['', 'spouse', 'child']);
    for (const [id, target] of options) {
      assert.equal(target.owner, selects[0][0]);
      assert.equal(entryOf(inv, id), undefined);
    }

    // 이탈 링크 · label 토글(surface) · onclick 채널 · addEventListener 전용 누락.
    assert.equal(named(inv, '이탈')[0][1].kind, 'link');
    const agree = named(inv, '동의합니다');
    assert.equal(agree.length, 1);
    assert.equal(agree[0][1].kind, 'handler');
    assert.equal(entryOf(inv, agree[0][0]).checked, null);
    assert.match(entryOf(inv, agree[0][0]).surface, /^[0-9a-f]{64}$/);
    assert.ok(named(inv, '직접 클릭')[0][1].found_by.includes('onclick'));
    assert.equal(named(inv, '리스너만').length, 0); // CDP 리스너 경로(Task 3c)가 잡는다

    // entries ↔ targets: 네이티브 옵션을 뺀 모든 대상이 엔트리 1개씩.
    assert.equal(inv.entries.length, Object.keys(inv.targets).length - options.length);
    for (const e of inv.entries) assert.ok(inv.targets[e.id], `entry ${e.id}에 대응하는 target 없음`);
    assert.deepEqual(inv.overlays, []);
    assert.deepEqual(inv.declared_unmatched, []);

    // display:contents 래퍼는 자기만 빠지고 자식은 계속 열거된다(발견 ①).
    const wrapped = named(inv, '래퍼 안 버튼');
    assert.equal(wrapped.length, 1);
    assert.ok(wrapped[0][1].dom_path.includes('div:nth-of-type'), wrapped[0][1].dom_path);
    assert.equal(entryOf(inv, wrapped[0][0]).occluded, false);

    // entry 필드 = K7 8필드 ∪ 드라이버용 런타임 값(kind·rect·dom_path)
    // ∪ 스니펫 헤더가 «entries 공용 모양»으로 못 박은 identity 원본 4필드(발견 ③).
    // 그 4필드가 없으면 surfaceKey의 reducedIdentityOf가 전부 한 값으로 접힌다.
    assert.deepEqual(inv.entry_doc_fields, pure.ENTRY_DOC_FIELDS);
    const IDENTITY_FIELDS = ['role', 'name', 'input_type', 'owner'];
    const wanted = [...pure.ENTRY_DOC_FIELDS, 'kind', 'rect', 'dom_path', ...IDENTITY_FIELDS].sort();
    for (const entry of inv.entries) {
      assert.deepEqual(Object.keys(entry).sort(), wanted);
      const target = inv.targets[entry.id];
      for (const field of IDENTITY_FIELDS) {
        assert.equal(entry[field], target[field], `${entry.id}.${field}`);
      }
    }

    // 접근 불가 프레임 한계는 조용히 버리지 않고 배열로 돌려준다(발견 ⑥).
    assert.ok(Array.isArray(inv.limits));
    assert.deepEqual(inv.limits, []);

    // kind 어휘는 고정이다 — DOM 층은 KINDS 밖 값을 내지 않는다.
    const kinds = await page.evaluate(() => globalThis.__interactionAudit.KINDS);
    for (const [, target] of Object.entries(inv.targets)) {
      assert.ok(kinds.includes(target.kind), `고정 어휘 밖 kind: ${target.kind}`);
    }
  });

  test('outside_root — 제외 선언이 없으면 루트 밖 대상을 센다', async (t) => {
    const page = await openFixture(t);
    const inv = await inventory(page, { excludedRegions: [] });
    assert.ok(inv.outside_root.count > 0, JSON.stringify(inv.outside_root));
    assert.ok(inv.outside_root.sample.includes('노브'), JSON.stringify(inv.outside_root.sample));
    assert.ok(inv.outside_root.sample.length <= 5);
  });

  test('markCandidates — __iaIndex 표식과 cdp_listener 채널', async (t) => {
    const page = await openFixture(t);
    const count = await page.evaluate(
      (s) => globalThis.__interactionAudit.dom.markCandidates(s), ROOT_SELECTOR);
    assert.ok(count > 20, `count=${count}`);
    const index = await page.evaluate(() => document.getElementById('ael-only').__iaIndex);
    assert.equal(typeof index, 'number');

    // CDP 리스너 열거가 있으면 addEventListener 전용 요소도 대상이 된다.
    const inv = await inventory(page, {
      capabilities: { cdp_listeners: true },
      listenerIndexes: { [index]: ['click'] },
    });
    const found = named(inv, '리스너만');
    assert.equal(found.length, 1);
    assert.deepEqual(found[0][1].found_by, ['cdp_listener']);
    assert.equal(found[0][1].kind, 'handler');
  });

  test('markCandidates — 다시 부르면 옛 표식은 사라진다', async (t) => {
    const page = await openFixture(t);
    // 표식은 이 호출의 순회 순서다 — 숨어서 순회에서 빠진 요소가 옛 번호를 들고 있으면
    // 같은 번호를 새로 받은 요소와 겹쳐 CDP 리스너 표가 엉뚱한 요소에 붙는다(K2).
    const probe = await page.evaluate((selector) => {
      const audit = globalThis.__interactionAudit;
      const marksOf = (root) => {
        const found = [];
        for (const el of root.querySelectorAll('*')) {
          if (typeof el.__iaIndex === 'number') found.push(el.__iaIndex);
          if (el.tagName === 'IFRAME' && el.contentDocument) found.push(...marksOf(el.contentDocument));
        }
        return found;
      };
      audit.dom.markCandidates(selector);
      const rows = document.getElementById('rows');
      const marked = rows.querySelector('button').__iaIndex; // 숨기기 전에는 표식이 있다
      rows.hidden = true; // display:none → 다음 순회에서 통째로 빠진다
      audit.dom.markCandidates(selector);
      const stale = [...rows.querySelectorAll('*')].filter((el) => typeof el.__iaIndex === 'number').length;
      const all = marksOf(document);
      return { marked, stale, total: all.length, unique: new Set(all).size };
    }, ROOT_SELECTOR);

    assert.equal(typeof probe.marked, 'number', '숨기기 전 표식이 없어 시험이 헛돈다');
    assert.equal(probe.stale, 0, `숨은 서브트리에 옛 표식 ${probe.stale}개가 남았다`);
    assert.equal(probe.unique, probe.total, `표식 번호가 겹친다(${probe.total} → ${probe.unique})`);
  });

  test('스크림 오버레이 — 행 4 가림·clickPoint는 패널 밖', async (t) => {
    const page = await openFixture(t);
    await page.evaluate(() => openDialog());
    const inv = await inventory(page);

    // 스크림(구조)과 패널(role=dialog) 둘 다 오버레이다.
    assert.equal(inv.overlays.length, 2);
    const scrims = inv.overlays.filter((id) => inv.targets[id].scrim === true);
    assert.equal(scrims.length, 1);
    const scrimId = scrims[0];
    assert.equal(inv.targets[scrimId].kind, 'overlay');
    assert.ok(inv.targets[scrimId].found_by.includes('structure'));
    const dialogId = inv.overlays.find((id) => inv.targets[id].role === 'dialog');
    assert.ok(dialogId);
    assert.equal(inv.targets[dialogId].scrim, false);

    for (const [id] of named(inv, '삭제')) {
      assert.equal(entryOf(inv, id).occluded, true, `삭제 ${id}가 가려지지 않았다`);
    }
    for (const name of ['확인', '취소']) {
      const hit = named(inv, name);
      assert.equal(hit.length, 1);
      assert.equal(entryOf(inv, hit[0][0]).occluded, false);
    }
    assert.equal(entryOf(inv, scrimId).occluded, false);

    const point = await page.evaluate((id) => globalThis.__interactionAudit.dom.clickPoint(id), scrimId);
    const panel = await rectOf(page, '#panel');
    assert.ok(point, 'scrim clickPoint 없음');
    assert.ok(outside(point, panel), JSON.stringify({ point, panel }));
  });

  test('메뉴형 오버레이 — outsidePoint는 루트 안·메뉴 밖·트리거 밖', async (t) => {
    const page = await openFixture(t);
    await page.evaluate(() => toggleMenu('menu-do'));
    const inv = await inventory(page);

    assert.equal(inv.overlays.length, 1);
    const menuId = inv.overlays[0];
    assert.equal(inv.targets[menuId].scrim, false);
    const items = kinded(inv, 'menuitem');
    assert.deepEqual(items.map(([, t]) => t.name).sort(), ['부산', '서울']);
    for (const [, target] of items) assert.equal(target.owner, menuId);

    const point = await page.evaluate((id) => globalThis.__interactionAudit.dom.outsidePoint(id), menuId);
    const [menu, trigger, root] = await Promise.all([
      rectOf(page, '#menu-do'), rectOf(page, '#trg-do'), rectOf(page, ROOT_SELECTOR),
    ]);
    assert.ok(point, 'outsidePoint 없음');
    assert.ok(!outside(point, root), JSON.stringify({ point, root }));
    assert.ok(outside(point, menu), JSON.stringify({ point, menu }));
    assert.ok(outside(point, trigger), JSON.stringify({ point, trigger }));
  });

  test('hover 후보와 스크롤 컨테이너', async (t) => {
    const page = await openFixture(t);
    const inv = await inventory(page);

    const hovers = await page.evaluate(() => globalThis.__interactionAudit.dom.hoverCandidates());
    assert.equal(hovers.length, 1);
    assert.equal(inv.targets[hovers[0]].name, '더보기');

    await inventory(page, { hoverSelectors: ['#rows button'] });
    const withSelectors = await page.evaluate(() => globalThis.__interactionAudit.dom.hoverCandidates());
    assert.equal(withSelectors.length, 5);

    const containers = await page.evaluate(() => globalThis.__interactionAudit.dom.scrollContainers());
    assert.equal(containers.length, 1, JSON.stringify(containers));
    assert.equal(containers[0].id, null); // #scroll-box 자체는 대상이 아니다
    assert.ok(containers[0].dom_path.length > 0);
    assert.ok(containers[0].scrollHeight > containers[0].clientHeight);
  });

  test('이름 규칙 — 컨테이너 오버레이는 서브트리 텍스트를 이름으로 쓰지 않는다', async (t) => {
    const page = await openFixture(t);
    await page.evaluate(() => { toggleMenu('menu-do'); openDialog(); });
    const inv = await inventory(page);

    // "컨테이너(구조 오버레이·menu/listbox/dialog 등 owner 역할 요소 …)는 aria-label/
    // aria-labelledby가 없으면 이름이 비어 dom_path가 identity에 들어간다"(K1 D-A).
    const menuId = inv.overlays.find((id) => inv.targets[id].role === 'menu');
    assert.ok(menuId, '메뉴 오버레이가 없다');
    assert.equal(inv.targets[menuId].name, '');
    // aria-label이 있는 다이얼로그는 그 이름을 그대로 쓴다(폴백 경로만 닫혔다).
    const dialogId = inv.overlays.find((id) => inv.targets[id].role === 'dialog');
    assert.ok(dialogId, '다이얼로그 오버레이가 없다');
    assert.equal(inv.targets[dialogId].name, '확인 대화상자');
    // 구조 오버레이(스크림)는 원래도 이름이 없다.
    const scrimId = inv.overlays.find((id) => inv.targets[id].scrim === true);
    assert.ok(scrimId, '스크림 오버레이가 없다');
    assert.equal(inv.targets[scrimId].name, '');
    // 항목형 대상은 자기 텍스트를 그대로 이름으로 쓴다.
    assert.deepEqual(kinded(inv, 'menuitem').map(([, target]) => target.name).sort(), ['부산', '서울']);
  });

  test('이름 규칙 — 대상 후손을 가진 handler만 빈 이름이고 identity가 안 흔들린다', async (t) => {
    const page = await openFixture(t);
    // #rows(행 4개를 품은 컨테이너)와 #ael-only(후손 없는 요소)에 리스너를 심어 둘 다
    // handler 대상으로 만든다 — 표식은 인벤토리 직전에 다시 심어야 한다(스니펫 계약).
    const marksOf = () => page.evaluate((selector) => {
      globalThis.__interactionAudit.dom.markCandidates(selector);
      const map = {};
      map[document.getElementById('rows').__iaIndex] = ['click'];
      map[document.getElementById('ael-only').__iaIndex] = ['click'];
      return map;
    }, ROOT_SELECTOR);
    const readInventory = async () =>
      inventory(page, { capabilities: { cdp_listeners: true }, listenerIndexes: await marksOf() });

    const before = await readInventory();
    const containers = Object.entries(before.targets)
      .filter(([, target]) => target.kind === 'handler' && target.name === '');
    assert.equal(containers.length, 1, JSON.stringify(containers.map(([, t2]) => t2.dom_path)));
    const [rowsId, rows] = containers[0];
    for (const [, row] of named(before, '삭제')) {
      assert.ok(row.dom_path.startsWith(`${rows.dom_path}/`), row.dom_path);
    }
    // 대상 후손이 없는 handler는 자기 텍스트를 그대로 쓴다.
    const listener = named(before, '리스너만');
    assert.equal(listener.length, 1);
    assert.equal(listener[0][1].kind, 'handler');

    // D-A의 근거 — 컨테이너 이름이 서브트리 텍스트면 행 하나만 지워도 identity가 바뀌고
    // owner 연쇄로 그 안의 대상이 전부 재생성된다(A8 실측 «관계» 트리거 38개).
    await page.evaluate(() => removeRow(document.querySelector('#rows .row button')));
    const after = await readInventory();
    assert.equal(named(after, '삭제').length, 3);
    assert.ok(after.targets[rowsId], '행 컨테이너 identity가 바뀌었다');
    assert.equal(after.targets[rowsId].dom_path, rows.dom_path);
  });

  test('hover 후보 — 항목형 대상은 발견 후보에서 뺀다', async (t) => {
    const page = await openFixture(t);
    await page.evaluate(() => toggleMenu('menu-do'));
    // :hover 규칙이 메뉴 항목과 트리거를 함께 가리켜도 항목형은 후보가 아니다(K2 D-C).
    const inv = await inventory(page, { hoverSelectors: ['#menu-do button', '#trg-do'] });
    const candidates = await page.evaluate(() => globalThis.__interactionAudit.dom.hoverCandidates());

    assert.equal(kinded(inv, 'menuitem').length, 2); // 후보에서 빠질 뿐 대상이다
    assert.deepEqual(candidates.filter((id) => inv.targets[id].kind === 'menuitem'), []);
    const trigger = named(inv, '시·도');
    assert.equal(trigger.length, 1);
    assert.ok(candidates.includes(trigger[0][0]), '항목형이 아닌 후보까지 사라졌다');
  });

  test('뷰포트 밖 지점 — 가림으로 판정하지 않고 활성으로 센다', async (t) => {
    const page = await openFixture(t);
    // 창을 줄여 루트 아래쪽을 창 밖으로 민다 — 그 지점은 hit-test가 성립하지 않는다
    // (elementFromPoint가 null이다). 가림은 창 «안» 지점으로만 판정한다(K2 D-B′).
    await page.setViewportSize({ width: 1000, height: 300 });
    const inv = await inventory(page);
    const open = named(inv, '열기');
    assert.equal(open.length, 1);
    const entry = entryOf(inv, open[0][0]);
    assert.ok(entry.rect.y >= 300, `창 안이라 시험이 헛돈다: ${JSON.stringify(entry.rect)}`);
    assert.equal(entry.occluded, false, '창 밖 지점을 가림으로 판정했다');
    assert.equal(entry.enabled, true);
    // 지점은 그대로 그 자리를 준다 — 드라이버가 굴려서(D-B) 다시 판정한다.
    const point = await page.evaluate((id) => globalThis.__interactionAudit.dom.clickPoint(id), open[0][0]);
    assert.ok(point && point.y >= 300, JSON.stringify(point));

    // 대조군 — 창 «안»에서 오버레이 뒤에 놓인 대상은 여전히 가림이다.
    await page.setViewportSize({ width: 1000, height: 1400 });
    await page.evaluate(() => openDialog());
    const covered = await inventory(page);
    for (const [id] of named(covered, '삭제')) {
      assert.equal(entryOf(covered, id).occluded, true, `삭제 ${id}가 가려지지 않았다`);
    }
  });

  test('owner_items_hash — 다이얼로그 안 무관 버튼 identity는 행 삭제 뒤에도 같다', async (t) => {
    const page = await openFixture(t);
    await page.evaluate(() => openDialog());
    const before = await inventory(page);

    const dialogId = before.overlays.find((id) => before.targets[id].role === 'dialog');
    assert.ok(dialogId);
    const confirmBefore = named(before, '확인');
    assert.equal(confirmBefore.length, 1);
    assert.equal(confirmBefore[0][1].owner, dialogId);
    // 다이얼로그 아래에는 항목 kind가 없다 → owner_items_hash는 빈 목록의 sha.
    assert.equal(confirmBefore[0][1].owner_items_hash, pure.sha256('[]'));

    await page.evaluate(() => {
      closeDialog();
      removeRow(document.querySelector('#rows .row button'));
      openDialog();
    });
    const after = await inventory(page);
    assert.equal(named(after, '삭제').length, 3); // 다이얼로그 안 칩도 4→3으로 준다
    const confirmAfter = named(after, '확인');
    assert.equal(confirmAfter.length, 1);
    assert.equal(confirmAfter[0][0], confirmBefore[0][0]);
    assert.equal(confirmAfter[0][1].owner, dialogId);
  });

  test('숨긴 iframe — 그려지지 않은 프레임 내부는 열거하지 않는다', async (t) => {
    const page = await openFixture(t);
    const inv = await inventory(page);

    const inFrames = Object.entries(inv.targets).filter(([, x]) => x.dom_path.startsWith('iframe['));
    assert.equal(inFrames.length, 1, JSON.stringify(inFrames.map(([, x]) => x.dom_path)));
    assert.ok(inFrames[0][1].dom_path.startsWith('iframe[0]/'));
    assert.equal(named(inv, '프레임 버튼').length, 1);

    // 대조군 — 같은 프레임을 보이게 하면 내부 버튼이 열거된다(프레임 자체는 멀쩡하다).
    await page.evaluate(() => { document.getElementById('frame-hidden').style.visibility = 'visible'; });
    const shown = await inventory(page);
    assert.equal(named(shown, '프레임 버튼').length, 2);
  });

  test('declared — 대상을 늘리고 미매칭은 declared_unmatched로 남는다', async (t) => {
    const page = await openFixture(t);
    const inv = await inventory(page, {
      declared: [
        { selector: '#ael-only', reason: '리스너 전용' },
        { selector: '#nope', reason: '없는 선택자' },
      ],
    });
    const declared = named(inv, '리스너만');
    assert.equal(declared.length, 1);
    assert.equal(declared[0][1].kind, 'declared');
    assert.equal(declared[0][1].declared, true);
    assert.deepEqual(declared[0][1].found_by, ['declared']);
    assert.deepEqual(inv.declared_unmatched, [{ selector: '#nope', reason: '없는 선택자' }]);
  });
});

// =====================================================================
// skeleton — 드라이버 골격(K5 래퍼·기동 · K3 served·루트·crop · K7 문서 필드)
// =====================================================================
describe('skeleton', () => {
  const DRIVER = path.join(__dirname, '..', '..', 'assets', 'observe_interactions.pw.js');
  const MODULE_GUIDE = /--playwright-module <dir> 또는 DDDJANGO_WEB_PLAYWRIGHT_MODULE 필요/;
  const COLLECTOR_KEYS = ['name', 'snippet_sha256', 'driver', 'driver_sha256', 'path', 'capabilities'];
  const TARGET_KEYS = [
    'role', 'name', 'input_type', 'owner', 'owner_items_hash', 'dom_path', 'kind',
    'first_seen_step', 'declared', 'found_by', 'live',
  ];

  // "문서에서 표면 키를 재계산할 때는 entries를 targets와 id로 조인한다"(K7) — 이름이 빈
  // 대상은 dom_path가 identity에 들어가므로(K1) 조인에 dom_path도 얹는다.
  const identityOf = (target) => ({
    role: target.role, name: target.name, input_type: target.input_type, owner: target.owner,
    dom_path: target.dom_path,
  });

  // skeleton이 보는 것은 골격(기동·served·crop·문서 판형)이다 — 탐색은 1 step으로
  // 묶는다. fixture.html은 상태 차원이 곱해져 큐가 마르지 않으므로(Task 3b 실측)
  // 상한을 주는 실행이 정상이고, 그래서 완주 exit 0이 아니라 partial exit 3이다.
  function wrapperArgs(build, over = {}, { cropRoot = true } = {}) {
    const named = {
      '--url': `${ctx.base}/fixture.html`, '--root': ROOT_SELECTOR, '--viewport': '560x1040',
      '--entrypoint-sha': fixtureSha(), '--archive-sha': 'a'.repeat(64), '--out': build.out,
      '--max-steps': '1',
      ...over,
    };
    const args = [WRAPPER, ...Object.entries(named).flat()];
    return cropRoot ? [...args, '--crop-root'] : args;
  }

  const freePort = () => new Promise((resolve) => {
    const probe = net.createServer();
    probe.listen(0, '127.0.0.1', () => {
      const { port } = probe.address();
      probe.close(() => resolve(port));
    });
  });

  test('모듈 없는 경로 — exit 1 + --playwright-module 안내', async (t) => {
    const build = tempBuild(t);
    const env = { ...process.env };
    delete env.DDDJANGO_WEB_PLAYWRIGHT_MODULE;

    const unset = await runWrapper(wrapperArgs(build), env);
    assert.equal(unset.status, 1, unset.stderr);
    assert.match(unset.stderr, MODULE_GUIDE);

    const missing = await runWrapper([...wrapperArgs(build), '--playwright-module', path.join(build.dir, 'none')], env);
    assert.equal(missing.status, 1, missing.stderr);
    assert.match(missing.stderr, MODULE_GUIDE);
    assert.equal(fs.existsSync(build.out), false, '환경 오류에서는 문서를 쓰지 않는다');
  });

  test('원격 URL — loopback도 --cdp origin도 아니면 거부하고 exit 1', async (t) => {
    const build = tempBuild(t);
    const run = await runWrapper(wrapperArgs(build, { '--url': 'http://example.invalid/screen.html' }));
    assert.equal(run.status, 1, run.stderr);
    assert.match(run.stderr, /원격 URL 거부/);
    assert.match(JSON.parse(run.stdout).environmentError, /원격 URL 거부/);
    assert.equal(fs.existsSync(build.out), false);
  });

  test('루트 selector 미발견 — exit 1', async (t) => {
    const build = tempBuild(t);
    const run = await runWrapper(wrapperArgs(build, { '--root': '[data-screen-label="없음"]' }));
    assert.equal(run.status, 1, run.stderr);
    assert.match(run.stderr, /루트 selector/);
    assert.match(JSON.parse(run.stdout).environmentError, /루트 selector/);
    assert.equal(fs.existsSync(build.out), false);
  });

  test('정상 실행 — served·수집기 sha·crop·캡처·K7 문서 필드', async (t) => {
    const build = tempBuild(t);
    const page = await ctx.browser.newPage({ viewport: { width: 560, height: 1040 }, reducedMotion: 'reduce' });
    const noise = [];
    page.on('console', (m) => noise.push(`[${m.type()}] ${m.text()}`));
    page.on('pageerror', (e) => noise.push(`[pageerror] ${e.message}`));
    t.after(async () => {
      await page.close();
      assert.deepEqual(noise, [], '드라이버가 콘솔 잡음을 냈다');
    });

    const url = `${ctx.base}/fixture.html`;
    const entrypointSha = fixtureSha();
    const excludedRegions = [{ selector: '#knobs', reason: '픽스처 노브' }];
    const summary = await observe(page, {
      url, rootSelector: ROOT_SELECTOR, browserViewport: [560, 1040], cropToRoot: true,
      entrypointSha, archiveSha: 'a'.repeat(64), out: build.out, capturesDir: build.capturesDir,
      declared: [], excludedRegions, hoverSelectors: [], path: 'node', maxSteps: 1,
    });

    assert.equal(summary.environmentError, null);
    assert.equal(summary.partial, true); // --max-steps 1에서 끊었다
    assert.deepEqual(summary.capsHit, ['max_steps']);
    assert.equal(summary.executed, 1);
    assert.ok(summary.surfaces >= 1);
    assert.ok(summary.residual.length > 0, '1 step으로 잔여가 0이 될 수는 없다');

    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    assert.deepEqual(Object.keys(doc), DOC_KEYS);
    assert.equal(doc.version, 1);
    assert.equal(summary.targets, Object.keys(doc.targets).length);

    // 수집기 — 실제 파일 바이트의 sha(K3 byte 대조 대상).
    assert.deepEqual(Object.keys(doc.collector), COLLECTOR_KEYS);
    assert.equal(doc.collector.name, 'interaction_audit');
    assert.equal(doc.collector.driver, 'observe_interactions.pw.js');
    assert.equal(doc.collector.snippet_sha256, sha256File(SNIPPET));
    assert.equal(doc.collector.driver_sha256, sha256File(DRIVER));
    assert.equal(doc.collector.path, 'node');
    // Chromium 경로는 CDP 리스너 열거가 산다 — 없으면 스니펫이 cursor 보조로 내려간다(K2).
    assert.deepEqual(doc.collector.capabilities, { react_props: true, cdp_listeners: true });

    assert.equal(doc.archive_sha256, 'a'.repeat(64));
    assert.deepEqual(doc.entrypoint, { path: 'fixture.html', sha256: entrypointSha });
    assert.equal(doc.url, url);
    assert.deepEqual(doc.browser_viewport, [560, 1040]);
    assert.match(doc.observed_at, /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/);

    // 루트·crop — content_crop은 루트 rect, browser_viewport와 별개로 기록한다(K3).
    // 실행은 마지막 step의 상태(발견 조작이 연 메뉴 등)로 페이지를 남기므로, 초기 상태의
    // 루트를 독립으로 재보려면 다시 열고 잰다.
    await page.goto(url, { waitUntil: 'load' });
    const rect = await rectOf(page, ROOT_SELECTOR);
    const rounded = {
      x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.w), h: Math.round(rect.h),
    };
    assert.deepEqual(doc.content_crop, rounded);
    assert.notDeepEqual([doc.content_crop.w, doc.content_crop.h], doc.browser_viewport);
    assert.equal(doc.root.selector, ROOT_SELECTOR);
    assert.equal(doc.root.found, true);
    assert.deepEqual(doc.root.fingerprint.rect, rounded);
    assert.deepEqual(doc.outside_root, { count: 0, sample: [] });
    assert.deepEqual(doc.excluded_regions, excludedRegions);
    assert.deepEqual(doc.declared, []);
    assert.deepEqual(doc.declared_unmatched, []);

    // served — same-origin 2xx 응답 바이트의 sha(테스트가 파일에서 독립 계산).
    assert.deepEqual(Object.keys(doc.served).sort(), ['fixture.html', 'frame.html']);
    assert.equal(doc.served['fixture.html'], entrypointSha);
    assert.equal(doc.served['frame.html'], sha256File(path.join(FIXTURE_DIR, 'frame.html')));

    // targets — K7 필드 고정. 선택 필드는 네이티브 옵션 value·오버레이 scrim 둘뿐이고
    // 스니펫 런타임 값(rect·rendered 등)은 문서에 남지 않는다.
    let optionCount = 0;
    for (const [id, target] of Object.entries(doc.targets)) {
      const keys = Object.keys(target);
      assert.deepEqual(keys.filter((k) => TARGET_KEYS.includes(k)), TARGET_KEYS, id);
      const optional = keys.filter((k) => !TARGET_KEYS.includes(k));
      if (target.kind === 'option') { assert.deepEqual(optional, ['value'], id); optionCount += 1; }
      else if (target.kind === 'overlay') assert.deepEqual(optional, ['scrim'], id);
      else assert.deepEqual(optional, [], `${id}(${target.kind})`);
      assert.ok(target.first_seen_step <= doc.steps.length, `${id}(${target.first_seen_step})`);
    }
    assert.equal(optionCount, 3);

    // initial — 인벤토리는 K7 8필드 고정(스니펫이 엔트리에 얹는 런타임 필드는 투영에서 빠진다).
    assert.deepEqual(Object.keys(doc.initial), ['inventory', 'state_hash', 'surface_key', 'capture']);
    assert.ok(doc.initial.inventory.length > 0);
    for (const entry of doc.initial.inventory) {
      assert.deepEqual(Object.keys(entry), pure.ENTRY_DOC_FIELDS);
    }
    // 기대 해시는 문서만으로 다시 만든다 — 8필드 엔트리를 targets와 id로 조인하는
    // 검사기(Task 5)와 같은 방식이라, 드라이버의 합침 코드를 복제하지 않는다.
    const rejoined = doc.initial.inventory.map((entry) => ({ ...entry, ...identityOf(doc.targets[entry.id]) }));
    assert.equal(doc.initial.state_hash, pure.stateHash(rejoined, url));
    assert.equal(doc.initial.surface_key, pure.surfaceKey(rejoined));

    // 캡처 — build 기준 상대 경로 · 루트 rect 크기 PNG · 기록된 sha가 바이트와 일치.
    assert.equal(doc.initial.capture.path, 'captures/fixture-initial.png');
    const png = path.join(build.dir, doc.initial.capture.path);
    assert.ok(fs.existsSync(png), png);
    assert.deepEqual(pngSize(png), { w: rounded.w, h: rounded.h });
    assert.equal(doc.initial.capture.sha256, sha256File(png));

    // 상한에서 끊긴 실행 — step 1개, partial과 caps_hit이 짝이 맞는다(K3 반례).
    assert.equal(doc.steps.length, 1);
    assert.equal(doc.discovery_limits.length, 1, JSON.stringify(doc.discovery_limits));
    assert.equal(doc.discovery_limits[0].kind, 'scroll-container');
    assert.equal(doc.partial, true);
    assert.deepEqual(doc.caps_hit, ['max_steps']);
    assert.equal(doc.environment_error, null);
  });

  test('외부 스크립트 로드 실패 — 루트 미발견으로 오진하지 않는다', async (t) => {
    const build = tempBuild(t);
    const run = await runWrapper(wrapperArgs(build, {
      '--url': `${ctx.base}/broken.html`, '--root': '[data-screen-label="broken"]',
    }));

    assert.equal(run.status, 1, run.stderr);
    assert.match(run.stderr, /스크립트 로드 실패/);
    assert.match(run.stderr, /missing\.js/);
    // 루트는 실제로 있다 — 원인이 아니라 증상을 보고하면 K5 배너 사유가 잘못 분류된다.
    assert.doesNotMatch(run.stderr, /루트 selector/);
    assert.match(JSON.parse(run.stdout).environmentError, /스크립트 로드 실패/);
    assert.equal(fs.existsSync(build.out), false);
  });

  test('래퍼 전 구간 — 상한 exit 3 · 요약 1행 JSON · 문서와 캡처 생성', async (t) => {
    const build = tempBuild(t);
    const run = await runWrapper(wrapperArgs(build));

    assert.equal(run.status, 3, run.stderr); // --max-steps 1 → partial
    assert.equal(run.stderr, '');
    const summary = JSON.parse(run.stdout);
    assert.equal(summary.environmentError, null);
    assert.equal(summary.partial, true);
    assert.equal(summary.executed, 1);
    assert.deepEqual(summary.capsHit, ['max_steps']);
    assert.ok(summary.targets > 0);
    assert.ok(summary.residual.length > 0);

    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    assert.deepEqual(Object.keys(doc), DOC_KEYS);
    assert.equal(doc.collector.path, 'node');
    assert.ok(fs.existsSync(path.join(build.dir, doc.initial.capture.path)));
  });

  test('--crop-root 미지정 — content_crop은 브라우저 뷰포트 전체', async (t) => {
    const build = tempBuild(t);
    const run = await runWrapper(wrapperArgs(build, {}, { cropRoot: false }));

    assert.equal(run.status, 3, run.stderr);
    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    assert.deepEqual(doc.browser_viewport, [560, 1040]);
    assert.deepEqual(doc.content_crop, { x: 0, y: 0, w: 560, h: 1040 });
    assert.deepEqual(pngSize(path.join(build.dir, doc.initial.capture.path)), { w: 560, h: 1040 });
  });

  test('--excluded-regions — {selector, reason} 행이 아니면 exit 1', async (t) => {
    const build = tempBuild(t);
    const file = path.join(build.dir, 'excluded.json');
    fs.writeFileSync(file, JSON.stringify(['#knobs']));
    const run = await runWrapper([...wrapperArgs(build), '--excluded-regions', file]);

    assert.equal(run.status, 1, run.stderr);
    assert.match(run.stderr, /excluded_regions 행 모양/);
    assert.equal(fs.existsSync(build.out), false);
  });

  test('--cdp — 사용자 세션 컨텍스트에서 관찰하고 우리 page만 정리한다', async (t) => {
    const build = tempBuild(t);
    const port = await freePort();
    const hosted = await chromium.launch({
      channel: process.env.DDDJANGO_WEB_BROWSER_CHANNEL || 'chrome',
      headless: true,
      args: [`--remote-debugging-port=${port}`],
    });
    const probe = await chromium.connectOverCDP(`http://127.0.0.1:${port}`);
    t.after(async () => {
      await probe.close();
      await hosted.close();
    });

    const session = probe.contexts()[0];
    assert.ok(session, 'CDP 연결에 기존 컨텍스트가 없다');
    await session.addCookies([{ name: 'ia_probe', value: '1', url: ctx.base }]);
    const pagesBefore = session.pages().length;
    const mark = ctx.requests.length;

    const run = await runWrapper(wrapperArgs(build, { '--cdp': `http://127.0.0.1:${port}` }));
    assert.equal(run.status, 3, run.stderr);

    // 인증 필요 원본을 여는 유일한 경로라, 관찰은 사용자 세션 안에서 일어나야 한다.
    const served = ctx.requests.slice(mark).find((row) => row.path === 'fixture.html');
    assert.ok(served, '픽스처 요청이 기록되지 않았다');
    assert.match(served.cookie, /ia_probe=1/);
    // 사용자 컨텍스트·브라우저는 남기고 우리가 연 page만 닫는다.
    assert.equal(session.pages().length, pagesBefore);
    assert.ok(fs.existsSync(build.out));
    assert.deepEqual(JSON.parse(fs.readFileSync(build.out, 'utf8')).browser_viewport, [560, 1040]);
  });

  // 실제 Chrome은 기본 컨텍스트를 늘 갖고 있어 `contexts()[0]`이 비는 CDP 경로를 실물로 만들
  // 수 없다 — Playwright 모듈 자리에 스텁을 끼워 정리 순서만 고정한다(3a 재리뷰 이월 · 4e #8).
  // 관찰은 원격 URL 거부(환경 오류 exit 1)로 바로 끝나므로 브라우저 API는 기동·정리 표면만 있으면 된다.
  const PW_STUB = [
    "const fs = require('node:fs');",
    "const note = (what) => fs.appendFileSync(process.env.IA_STUB_LOG, what + '\\n');",
    'const page = { setDefaultTimeout() {}, setDefaultNavigationTimeout() {}, async setViewportSize() {},',
    "  url() { return 'about:blank'; }, isClosed() { return false; }, async close() { note('page.close'); } };",
    "const context = { pages: () => [], async newPage() { return page; }, async close() { note('context.close'); } };",
    'const browser = {',
    "  contexts: () => (process.env.IA_STUB_CONTEXTS === '0' ? [] : [context]),",
    "  async newContext() { note('newContext'); return context; },",
    "  async close() { note('browser.close'); },",
    '};',
    'module.exports = { chromium: { async connectOverCDP() { return browser; }, async launch() { return browser; } } };',
  ].join('\n');

  test('--cdp — 기존 컨텍스트가 없어 우리가 만든 컨텍스트는 닫고, 있으면 page만 닫는다', async (t) => {
    const build = tempBuild(t);
    const stubDir = path.join(build.dir, 'pw-stub');
    fs.mkdirSync(stubDir);
    fs.writeFileSync(path.join(stubDir, 'package.json'), '{"name":"pw-stub","main":"index.js"}');
    fs.writeFileSync(path.join(stubDir, 'index.js'), PW_STUB);
    const cleanupOf = async (contexts) => {
      const log = path.join(build.dir, `stub-${contexts}.log`);
      const env = { ...process.env, IA_STUB_LOG: log, IA_STUB_CONTEXTS: String(contexts) };
      const result = await runWrapper(wrapperArgs(build, {
        '--cdp': 'http://127.0.0.1:1', '--url': 'http://example.invalid/x.html', '--playwright-module': stubDir,
      }), env);
      assert.equal(result.status, 1, result.stderr);
      assert.match(result.stderr, /원격 URL 거부/);
      return fs.readFileSync(log, 'utf8').trim().split('\n');
    };
    // 사용자 컨텍스트가 있으면 그 안에 page만 열고 page만 닫는다(브라우저·컨텍스트는 사용자 것).
    assert.deepEqual(await cleanupOf(1), ['page.close']);
    // 없어서 우리가 만든 컨텍스트는 우리가 닫는다 — 사용자 브라우저에 빈 컨텍스트를 남기지 않는다.
    assert.deepEqual(await cleanupOf(0), ['newContext', 'page.close', 'context.close']);
  });
});

// =====================================================================
// explore — 탐색 큐·재생·조작·안정 대기·캡처·resume
//   K1 큐 키(identity, action, option, context_T)·잔여 단위·상한
//   K2 조작 규칙(클릭 지점·fill 표본·네이티브 select·오버레이·이탈)
//   K7 step 기록(필드·before/after·changes·capture)
// =====================================================================
describe('explore', () => {
  const STEP_KEYS = [
    'n', 'path', 'target', 'action', 'option', 'value', 'context', 'status', 'error',
    'before', 'after', 'changes', 'navigated', 'discovery',
  ];
  // 탐색은 «관찰한 상태 × 대상»을 도는 일이라 상태 차원이 곱해지는 화면에서는 큐가
  // 마르지 않는다(보고서 §실측). 이 픽스처는 잔여가 67 step에서 0이 되므로(실측)
  // 여유를 두고 120에서 끊는다 — 상한에 걸린 실행이 정상 판형이다(partial:true).
  const MAX_STEPS = 120;
  const DECLARED = [
    { selector: '#ael-only', reason: '리스너 전용 요소' },
    { selector: '#nick', reason: '별명은 값을 고정한다', value: '홍길동' },
    { selector: '#nope', reason: '없는 선택자' },
  ];
  const EXCLUDED = [{ selector: '#knobs', reason: '픽스처 노브' }];

  const run = { doc: null, summary: null, build: null, noise: [] };

  before(async () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ia-explore-'));
    run.build = { dir, capturesDir: path.join(dir, 'captures'), out: path.join(dir, 'captures', 'fixture-interactions.json') };
    const page = await ctx.browser.newPage({ viewport: { width: 560, height: 1040 }, reducedMotion: 'reduce' });
    page.on('console', (m) => run.noise.push(`[${m.type()}] ${m.text()}`));
    page.on('pageerror', (e) => run.noise.push(`[pageerror] ${e.message}`));
    run.summary = await observe(page, {
      url: `${ctx.base}/fixture.html`, rootSelector: ROOT_SELECTOR, browserViewport: [560, 1040],
      cropToRoot: true, entrypointSha: fixtureSha(), archiveSha: 'a'.repeat(64),
      out: run.build.out, capturesDir: run.build.capturesDir,
      declared: DECLARED, excludedRegions: EXCLUDED, hoverSelectors: [], path: 'node',
      maxSteps: MAX_STEPS,
    });
    await page.close();
    run.doc = JSON.parse(fs.readFileSync(run.build.out, 'utf8'));
  });

  after(() => { if (run.build) fs.rmSync(run.build.dir, { recursive: true, force: true }); });

  const targetsNamed = (name) => Object.entries(run.doc.targets).filter(([, t]) => t.name === name);
  const idNamed = (name) => {
    const hits = targetsNamed(name);
    assert.equal(hits.length, 1, `대상 «${name}» ${hits.length}개`);
    return hits[0][0];
  };
  const stepsOf = (id) => run.doc.steps.filter((s) => s.target === id);
  const executedOf = (id, action) =>
    stepsOf(id).filter((s) => s.status === 'executed' && (action === undefined || s.action === action));
  const rowIds = () => targetsNamed('삭제').map(([id]) => id);

  test('잔여 0 — 발견한 모든 단위가 executed step을 가진다', () => {
    assert.deepEqual(run.noise, [], '탐색이 콘솔 잡음을 냈다');
    assert.equal(run.summary.environmentError, null);
    assert.ok(run.doc.steps.length > 0, 'step이 하나도 없다');
    assert.deepEqual(run.summary.residual, []);
    // 문서만으로 다시 계산해도 0이어야 한다(검사기 Task 5와 같은 입력).
    assert.deepEqual(pure.residual(run.doc), []);
    assert.equal(run.summary.executed, run.doc.steps.filter((s) => s.status === 'executed').length);
    assert.ok(run.summary.surfaces > 1, `표면 ${run.summary.surfaces}`);
  });

  test('step 판형 — K7 필드·n 연속·executed는 error null·path 끝이 자기 대상', () => {
    const seen = new Set();
    run.doc.steps.forEach((step, index) => {
      assert.deepEqual(Object.keys(step), STEP_KEYS, `step ${step.n}`);
      assert.equal(step.n, index + 1);
      assert.equal(seen.has(step.n), false);
      seen.add(step.n);
      assert.equal(typeof step.discovery, 'boolean'); // 발견 조작(hover)만 참이다(K2)
      assert.match(step.context, /^[0-9a-f]{16}$/);
      assert.equal(step.path[step.path.length - 1], step.target);
      assert.deepEqual(Object.keys(step.before), ['inventory', 'state_hash']);
      for (const entry of step.before.inventory) assert.deepEqual(Object.keys(entry), pure.ENTRY_DOC_FIELDS);
      if (step.status === 'executed') assert.equal(step.error, null, `step ${step.n}`);
      else assert.equal(step.after, null, `step ${step.n}(${step.status})`);
      if (step.after) {
        const keys = Object.keys(step.after);
        assert.deepEqual(keys.slice(0, 3), ['inventory', 'state_hash', 'surface_key'], `step ${step.n}`);
        assert.deepEqual(keys.slice(3), step.changes.added.length > 0 ? ['capture'] : [], `step ${step.n}`);
        for (const entry of step.after.inventory) assert.deepEqual(Object.keys(entry), pure.ENTRY_DOC_FIELDS);
      }
      assert.deepEqual(Object.keys(step.changes), ['added', 'removed', 'values']);
    });
    // 상한에 걸린 실행은 partial과 caps_hit이 같이 말한다(K3 반례: partial:false ∧ caps_hit≠[]).
    assert.equal(run.doc.partial, run.doc.caps_hit.length > 0);
    assert.deepEqual(run.doc.caps_hit, ['max_steps']);
    assert.equal(run.doc.steps.length, MAX_STEPS);
  });

  test('«다음» 위저드 — 같은 identity가 3단계 context에서 각각 executed', async (t) => {
    const build = tempBuild(t, 'wizard');
    const page = await ctx.browser.newPage({ viewport: { width: 560, height: 400 }, reducedMotion: 'reduce' });
    t.after(() => page.close());
    const summary = await observe(page, {
      url: `${ctx.base}/wizard.html`, rootSelector: '[data-screen-label="wizard"]',
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(WIZARD_HTML),
      archiveSha: 'd'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node',
    });
    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    const one = (name) => {
      const hits = Object.entries(doc.targets).filter(([, t2]) => t2.name === name);
      assert.equal(hits.length, 1, `${name}: ${hits.length}`);
      return hits[0][0];
    };
    const next = one('다음');
    const prev = one('이전');
    const first = one('처음으로');
    const steps = doc.steps.filter((s) => s.target === next && s.status === 'executed');
    const stageOf = (step) => {
      const ids = new Set(step.before.inventory.map((e) => e.id));
      return ids.has(prev) ? 2 : ids.has(first) ? 3 : 1;
    };
    // 같은 identity가 세 단계에서 각각 실행됐고 큐 키를 가른 것은 context_T다(K1).
    assert.deepEqual([...new Set(steps.map(stageOf))].sort(), [1, 2, 3]);
    assert.equal(new Set(steps.map((s) => s.context)).size, 3);
    assert.deepEqual(summary.residual, []);
    assert.equal(doc.partial, false);
    assert.deepEqual(doc.caps_hit, []);
  });

  test('cascade — 부모 pick 뒤 나타난 시·군 항목 5종이 전부 executed', () => {
    for (const name of ['강남구', '종로구', '마포구', '해운대구', '수영구']) {
      assert.ok(executedOf(idNamed(name)).length >= 1, name);
    }
    for (const name of ['서울', '부산']) assert.ok(executedOf(idNamed(name)).length >= 1, name);
  });

  test('토글 — 두 상태가 각각 executed이고 option은 before surface다', () => {
    const star = idNamed('즐겨찾기');
    const steps = executedOf(star, 'click');
    const options = new Set(steps.map((s) => s.option));
    assert.equal(options.size, 2, `상태 ${[...options].length}`);
    for (const step of steps) {
      assert.match(step.option, /^[0-9a-f]{64}$/);
      const entry = step.before.inventory.find((e) => e.id === star);
      assert.equal(step.option, entry.surface, `step ${step.n}`);
    }
  });

  test('오버레이 — 스크림은 자기 click ≡ click:outside, 메뉴·패널은 바깥 지점·Escape', () => {
    const overlays = Object.entries(run.doc.targets).filter(([, t]) => t.kind === 'overlay');
    const scrim = overlays.find(([, t]) => t.scrim === true);
    assert.ok(scrim, '스크림 오버레이가 없다');
    assert.ok(executedOf(scrim[0], 'click').some((s) => s.option === null));
    assert.ok(executedOf(scrim[0], 'key').some((s) => s.option === 'Escape'));

    const panel = overlays.find(([, t]) => t.role === 'dialog');
    assert.ok(panel, '다이얼로그 오버레이가 없다');
    assert.ok(executedOf(panel[0], 'click').some((s) => s.option === 'outside'));
    assert.ok(executedOf(panel[0], 'key').some((s) => s.option === 'Escape'));
  });

  test('네이티브 select — 옵션 3이 전부 action select로 executed', () => {
    const options = Object.entries(run.doc.targets).filter(([, t]) => t.kind === 'option');
    assert.equal(options.length, 3);
    assert.deepEqual(options.map(([, t]) => t.value).sort(), ['', 'child', 'spouse']);
    const selectId = idNamed('관계');
    for (const [id, target] of options) {
      const steps = executedOf(id, 'select');
      assert.ok(steps.length >= 1, target.name);
      assert.equal(steps[0].option, target.value);
      assert.deepEqual(steps[0].changes.values.map((v) => v.target), [selectId]);
      assert.equal(steps[0].changes.values[0].after, target.value);
    }
  });

  test('live 대상 — 토스트 액션 버튼도 실행 의무가 있다', () => {
    const undo = idNamed('실행 취소');
    assert.equal(run.doc.targets[undo].live, true);
    assert.ok(executedOf(undo).length >= 1);
  });

  test('가림 — 오버레이 context에서는 행을 실행하지 않고 목록 context에서 실행한다', () => {
    // 행 버튼은 이름이 같아 dom_path로 갈린다 — 행을 지우면 뒤 행의 dom_path가 밀려
    // 새 identity가 생기므로 4개로 고정되지 않는다(K1 충돌 규칙의 관찰 결과).
    const rows = rowIds();
    assert.ok(rows.length >= 4, `행 대상 ${rows.length}`);
    for (const id of rows) assert.ok(executedOf(id).length >= 1, id);
    const occluded = run.doc.steps.some((s) =>
      s.before.inventory.some((e) => rows.includes(e.id) && e.occluded === true));
    assert.ok(occluded, '행이 가려진 상태를 관찰하지 못했다');
    for (const step of run.doc.steps.filter((s) => s.status === 'executed')) {
      const entry = step.before.inventory.find((e) => e.id === step.target);
      if (!entry) continue; // 네이티브 옵션은 entries 밖이다
      assert.equal(entry.occluded, false, `step ${step.n}`);
      assert.equal(entry.enabled, true, `step ${step.n}`);
    }
  });

  test('이탈 — navigated 터미널 step이고 큐에 잇지 않는다', () => {
    const leave = idNamed('이탈');
    const steps = stepsOf(leave);
    assert.ok(steps.length >= 1);
    for (const step of steps) {
      assert.equal(step.status, 'executed');
      assert.equal(step.navigated, 'about:blank');
      assert.equal(step.after, null);
      assert.deepEqual(step.changes, { added: [], removed: [], values: [] });
    }
    for (const step of run.doc.steps) {
      const index = step.path.indexOf(leave);
      assert.ok(index === -1 || index === step.path.length - 1, `step ${step.n} path에 이탈이 중간에 있다`);
    }
  });

  test('빈 목록 — 행 대상이 0인 after 인벤토리를 가진 executed step이 있다', () => {
    const rows = rowIds();
    const empty = run.doc.steps.find((s) =>
      s.status === 'executed' && s.after && !s.after.inventory.some((e) => rows.includes(e.id)));
    assert.ok(empty, '빈 목록 상태에 도달한 step이 없다');
    assert.ok(empty.changes.removed.length > 0);
  });

  test('fill 표본 — numeric은 placeholder 숫자열·형식 placeholder는 원문·선언 value 우선', () => {
    const fillOf = (name) => {
      const steps = executedOf(idNamed(name), 'fill');
      assert.ok(steps.length >= 1, `${name} fill 없음`);
      return steps[0];
    };
    assert.equal(fillOf('생년월일').value, '19920704'); // inputmode=numeric + placeholder 1992.07.04
    assert.equal(fillOf('전화').value, '010-0000-0000'); // 형식처럼 보이는 placeholder 원문
    assert.equal(fillOf('메모').value, '검증 입력'); // placeholder 없음
    assert.equal(fillOf('별명').value, '홍길동'); // --declared value 우선

    const birth = idNamed('생년월일');
    assert.deepEqual(fillOf('생년월일').changes.values, [{ target: birth, before: '', after: '19920704' }]);
    for (const name of ['생년월일', '전화', '별명', '메모']) {
      const id = idNamed(name);
      assert.ok(executedOf(id, 'focus').length >= 1, `${name} focus`);
      assert.ok(executedOf(id, 'blur').length >= 1, `${name} blur`);
    }
  });

  test('캡처 — initial 1 + added≠∅ step 수(이탈 step은 PNG를 남기지 않는다)', () => {
    const added = run.doc.steps.filter((s) => s.changes.added.length > 0);
    const navigated = run.doc.steps.filter((s) => s.navigated !== null);
    const files = fs.readdirSync(run.build.capturesDir).filter((f) => f.endsWith('.png'));
    assert.equal(files.length, 1 + added.length, files.join(','));
    assert.ok(added.length > 0 && navigated.length > 0);

    assert.equal(run.doc.initial.capture.path, 'captures/fixture-initial.png');
    for (const step of added) {
      assert.equal(step.after.capture.path, `captures/fixture-step-${step.n}.png`);
      const file = path.join(run.build.dir, step.after.capture.path);
      assert.equal(step.after.capture.sha256, sha256File(file));
      // clip은 캡처 시점마다 다시 잰다(3a 수정 라운드 1 I-4) — 행이 지워지거나
      // 메뉴가 열리면 루트 높이가 그 상태의 것으로 바뀐다. 폭은 루트 폭 그대로다.
      const size = pngSize(file);
      assert.equal(size.w, run.doc.content_crop.w, `step ${step.n} 폭`);
      assert.ok(size.h > 0, `step ${step.n} 높이 ${size.h}`);
    }
    // 이탈 step은 루트 크롭이 성립하지 않으므로 PNG 자체를 남기지 않는다(K3).
    for (const step of navigated) {
      assert.equal(fs.existsSync(path.join(run.build.capturesDir, `fixture-step-${step.n}.png`)), false,
        `이탈 step ${step.n}의 PNG가 남았다`);
    }
  });

  test('선언 — 매칭된 대상은 declared:true, 미매칭은 declared_unmatched(잔여 밖)', () => {
    assert.deepEqual(run.doc.declared, DECLARED);
    assert.deepEqual(run.doc.declared_unmatched, [{ selector: '#nope', reason: '없는 선택자' }]);
    const listener = idNamed('리스너만');
    assert.equal(run.doc.targets[listener].declared, true);
    assert.deepEqual(run.doc.targets[listener].found_by, ['cdp_listener', 'declared']);
    assert.ok(executedOf(listener).length >= 1);
    assert.equal(run.doc.targets[idNamed('별명')].declared, true);
    // 미매칭 선언은 대상이 아니므로 잔여 계산에 들어가지 않는다.
    assert.deepEqual(run.summary.residual, []);
  });

  test('unclickable — 후손 대상에 완전히 덮인 요소는 실행하지 않고 잔여로 남는다', async (t) => {
    const build = tempBuild(t, 'cover');
    const page = await ctx.browser.newPage({ viewport: { width: 560, height: 400 }, reducedMotion: 'reduce' });
    t.after(() => page.close());
    const summary = await observe(page, {
      url: `${ctx.base}/cover.html`, rootSelector: '[data-screen-label="cover"]',
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(COVER_HTML),
      archiveSha: 'c'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node',
    });
    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    const cover = Object.entries(doc.targets).find(([, t2]) => t2.name === '덮개');
    assert.ok(cover, '덮개 대상이 없다');
    const steps = doc.steps.filter((s) => s.target === cover[0]);
    assert.equal(steps.length, 1);
    assert.equal(steps[0].status, 'unclickable');
    assert.equal(steps[0].after, null);
    assert.match(steps[0].error, /클릭 지점/);
    // 안쪽 버튼은 정상 실행된다.
    const inner = Object.entries(doc.targets).find(([, t2]) => t2.name === '덮개 안 버튼');
    assert.equal(doc.steps.filter((s) => s.target === inner[0] && s.status === 'executed').length, 1);
    // "unclickable은 세지 않는다"(K1) — 잔여에 그대로 남는다.
    assert.deepEqual(summary.residual, [{ target: cover[0], action: 'click', option: null }]);
    assert.equal(doc.partial, false);
  });

  test('뷰포트 밖 지점 — 굴려서 다시 재고 unclickable을 남기지 않는다', async (t) => {
    const { summary, doc } = await observeRoute(t, 'tall', 'tall', TALL_HTML);
    const executedNamed = (name) => doc.steps.filter((s) =>
      s.status === 'executed' && doc.targets[s.target].name === name);

    // "클릭 지점이 브라우저 뷰포트 밖이면 대상을 scrollIntoView로 굴려 … 재판정"(K2 D-B).
    assert.deepEqual(doc.steps.filter((s) => s.status === 'unclickable').map((s) => [s.n, s.error]), []);
    const discovery = doc.steps.filter((s) => s.discovery === true);
    assert.equal(discovery.length, 1, JSON.stringify(discovery.map((s) => [s.n, s.status])));
    assert.equal(discovery[0].status, 'executed');
    assert.equal(doc.targets[discovery[0].target].name, '더보기');
    // 굴려서 연 메뉴 항목과, 창 아래에 있던 버튼이 전부 실행된다.
    assert.ok(executedNamed('복제').length >= 1, 'hover로 드러난 항목이 실행되지 않았다');
    assert.ok(executedNamed('아래 버튼').length >= 1, '창 아래 버튼이 실행되지 않았다');
    // 창 밖은 가림이 아니므로(D-B′) 그 버튼은 초기 상태에서 이미 활성이고 큐에 든다.
    const bottom = Object.entries(doc.targets).find(([, t2]) => t2.name === '아래 버튼');
    const initial = doc.initial.inventory.find((e) => e.id === bottom[0]);
    assert.ok(initial, '창 아래 버튼이 초기 인벤토리에 없다');
    assert.deepEqual([initial.enabled, initial.occluded], [true, false]);
    assert.deepEqual(summary.residual, []);
    assert.equal(doc.partial, false);
    assert.deepEqual(doc.caps_hit, []);
  });

  test('스크롤 훑기 — 위치마다 재인벤토리해 컨테이너 안 항목을 전부 실행한다', async (t) => {
    const build = tempBuild(t, 'scroll-sweep');
    // 이 화면만 큰 창에서 본다 — 컨테이너 밖으로 밀린 항목이 창 안에 남아야 가림이 된다.
    const page = await ctx.browser.newPage({ viewport: { width: 560, height: 1040 }, reducedMotion: 'reduce' });
    t.after(() => page.close());
    const summary = await observe(page, {
      url: `${ctx.base}/scroll-sweep.html`, rootSelector: '[data-screen-label="sweep"]',
      browserViewport: [560, 1040], cropToRoot: true, entrypointSha: sha256Text(SWEEP_HTML),
      archiveSha: '2'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node',
    });
    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    const executedNames = new Set(doc.steps
      .filter((s) => s.status === 'executed').map((s) => doc.targets[s.target].name));

    // "컨테이너마다 scrollTop=0부터 clientHeight씩 끝까지 진행하며 위치마다 재인벤토리하고
    // acceptState한다"(K2 D-D) — 끝으로만 굴리면 중간 페이지 항목이 큐에 들지 못한다.
    for (let i = 1; i <= 20; i += 1) {
      assert.ok(executedNames.has(`항목 ${i}`), `항목 ${i} 미실행(${executedNames.size}건 실행)`);
    }
    assert.equal(Object.keys(doc.targets).length, 20);
    assert.deepEqual(summary.residual, []);
    assert.deepEqual(pure.residual(doc), []);
    assert.equal(doc.partial, false);
    assert.deepEqual(doc.caps_hit, []);

    // 컨테이너 하나 = 한계 행 하나. 사유에 훑은 위치 수와 활성이 된 대상 수가 들어간다.
    const rows = doc.discovery_limits.filter((row) => row.kind === 'scroll-container');
    assert.equal(rows.length, 1, JSON.stringify(doc.discovery_limits));
    assert.deepEqual(Object.keys(rows[0]), ['kind', 'dom_path', 'reason']);
    assert.match(rows[0].reason, /4 위치를 훑어 재인벤토리했다\(활성이 된 대상 \d+\)/);
  });

  test('숨은 상태 — 해시가 같아도 다른 계보의 페이지에서 실행하지 않는다', async (t) => {
    const { summary, doc } = await observeRoute(t, 'hidden-state', 'hidden', HIDDEN_STATE_HTML,
      { maxSteps: 80 });
    const idOf = (name) => (Object.entries(doc.targets).find(([, t2]) => t2.name === name) || [])[0];
    const rowA = idOf('김가 수정');
    const rowB = idOf('이나 수정');
    const city = idOf('도시 선택');
    assert.ok(rowA && rowB && city, '행·도시 트리거가 열거되지 않았다');

    // 김가(A)는 도시 트리거가 비활성, 이나(B)는 활성이다 — 단계 1의 해시·context는 같다.
    const cityIn = (block) => (block ? block.inventory.find((e) => e.id === city) : undefined);
    let sawA = false;
    let sawB = false;
    for (const step of doc.steps) {
      const lineage = step.path[0];
      if (lineage !== rowA && lineage !== rowB) continue;
      for (const block of [step.before, step.after]) {
        const entry = cityIn(block);
        if (!entry) continue;
        if (lineage === rowA) {
          assert.equal(entry.enabled, false, `A 계보 step ${step.n}에 B 데이터(활성 트리거)가 있다`);
          sawA = true;
        } else {
          assert.equal(entry.enabled, true, `B 계보 step ${step.n}에 A 데이터(비활성 트리거)가 있다`);
          sawB = true;
        }
      }
    }
    assert.ok(sawB, '단계 2에 이른 B 계보 step이 없어 시험이 헛돈다');
    // A 방향 단언은 이 화면에서 «방어»다(리뷰 Minor 8의 답): 단계 1이 두 사람에게 완전히 같아
    // 큐 키가 하나로 합쳐지므로 A 계보의 «다음»은 아예 존재하지 않는다 — 그래서 A 계보 step은
    // 단계 1에 머문다. 실측: sawA = false. 판별력은 B 방향(위 RED)이 갖는다.
    assert.equal(sawA, false, 'A 계보가 단계 2에 이르렀다 — 화면 전제가 달라졌으니 단언을 다시 본다');

    // 오염된 상태에서 넣은 항목은 나중에 «재생 종점 상태 불일치»로 죽는다(5차 실측 50건).
    assert.deepEqual(doc.steps.filter((s) => s.status === 'unreachable').map((s) => [s.n, s.error]), []);
    // 도시 트리거는 B 계보에서만 실행된다(A에서는 비활성이라 큐에 들지 않는다).
    assert.ok(doc.steps.some((s) => s.target === city && s.status === 'executed' && s.path[0] === rowB));
    assert.deepEqual(doc.steps.filter((s) => s.target === city && s.status === 'executed'
      && s.path[0] === rowA), []);
    assert.deepEqual(summary.residual, []);
  });

  test('cascade 기아 — 트리거의 새 context가 얕은 재실행에 밀리지 않는다', async (t) => {
    // 얕은 폼(메모·라디오 2)이 계속 새 context를 만들어 큐를 채우는 동안, 자식 트리거의
    // «부모 값이 정해진 상태» context가 굶으면 그 메뉴 항목은 열거조차 되지 않는다(D-F ②).
    const { summary, doc } = await observeRoute(t, 'cascade-starve', 'starve', CASCADE_STARVE_HTML,
      { maxSteps: 90 });
    const executedNames = new Set(doc.steps
      .filter((s) => s.status === 'executed').map((s) => doc.targets[s.target].name));

    for (const name of ['a1', 'a2', 'a3', 'a4', 'b1', 'b2', 'b3', 'c1', 'c2']) {
      assert.ok(executedNames.has(name), `${name} 미실행(${[...executedNames].join(',')})`);
    }
    assert.deepEqual(doc.steps.filter((s) => s.status === 'unreachable').map((s) => [s.n, s.error]), []);
    // 트리거의 «새 context»가 실제로 먼저 꺼내진다 — 부모를 고른 뒤 자식 트리거 클릭이
    // 그 뒤 얕은 재실행보다 앞선다(순서 자체가 이 Task의 결과물이다).
    const pickAt = doc.steps.findIndex((s) => s.status === 'executed' && doc.targets[s.target].name === '가');
    const childAfterPick = doc.steps.findIndex((s, i) => i > pickAt
      && s.status === 'executed' && doc.targets[s.target].name === '자식 선택');
    assert.ok(pickAt !== -1 && childAfterPick !== -1, '부모 선택·자식 트리거 step이 없다');
    assert.ok(childAfterPick - pickAt <= 5, `부모를 고른 뒤 자식 트리거까지 ${childAfterPick - pickAt} step`);
    // 자식 항목 9종은 잔여로 남지 않는다 — 상한에서 끊긴 실행이라 다른 단위는 남을 수 있다.
    const childUnits = pure.residual(doc)
      .filter((unit) => /^[abc]\d$/.test((doc.targets[unit.target] || {}).name || ''));
    assert.deepEqual(childUnits, []);
  });

  test('재생 중 가림 복구 — 복구 뒤 인벤토리로 판정해 재생을 살린다', async (t) => {
    const { summary, doc } = await observeRoute(t, 'replay-occluded', 'replay', REPLAY_OCCLUDED_HTML);
    const named2 = (name) => Object.entries(doc.targets).find(([, t2]) => t2.name === name);
    const executedOf2 = (name) => doc.steps.filter((s) =>
      s.status === 'executed' && s.target === (named2(name) || [])[0]);

    // 재생 접두가 «컨테이너 안 가려진 항목»인 화면 — 복구 **전** 인벤토리로 판정하면
    // 복구에 성공한 재생이 전부 unreachable이 된다(재리뷰 C1).
    const unreachable = doc.steps.filter((s) => s.status === 'unreachable');
    assert.deepEqual(unreachable.map((s) => [s.n, s.error]), []);
    // 시험이 헛돌지 않으려면 그 항목이 실제로 재생 경로에 있어야 한다(깊이 2 이상 step 존재).
    assert.ok(doc.steps.some((s) => s.path.length >= 2), '재생 경로가 없어 시험이 헛돈다');
    for (const name of ['여는 항목', '덧보기', '닫기']) {
      assert.ok(executedOf2(name).length >= 1, `${name} 미실행`);
    }
    assert.deepEqual(summary.residual, []);
    assert.equal(doc.partial, false);
  });

  test('훑기 드리프트 — 다음 컨테이너가 옛 상태와 대조하지 않는다', async (t) => {
    const { summary, doc } = await observeRoute(t, 'sweep-drift', 'drift', SWEEP_DRIFT_HTML);
    const rows = doc.discovery_limits.filter((row) => row.kind === 'scroll-container');
    assert.equal(rows.length, 2, JSON.stringify(doc.discovery_limits));

    // 첫 컨테이너는 훑는 중 상태가 달라져 중단한다.
    const drifted = rows.filter((row) => /위치까지 훑다가 상태가 달라져 중단했다/.test(row.reason));
    assert.equal(drifted.length, 1, JSON.stringify(rows));
    // 둘째 컨테이너는 **지금 상태**와 대조하므로 정상으로 훑는다(옛 해시면 0 위치에서 떨어진다).
    const swept = rows.filter((row) => /위치를 훑어 재인벤토리했다/.test(row.reason));
    assert.equal(swept.length, 1, JSON.stringify(rows));
    assert.ok(Number(/^(\d+) 위치를/.exec(swept[0].reason)[1]) >= 2, swept[0].reason);
    // 드리프트한 상태도 확장 출처다 — 거기서 드러난 대상이 실행된다.
    const extra = Object.entries(doc.targets).find(([, t2]) => t2.name === '덧보기');
    assert.ok(extra, '덧보기가 열거되지 않았다');
    assert.ok(doc.steps.some((s) => s.target === extra[0] && s.status === 'executed'), '덧보기 미실행');
    // 훑기 위치는 문서에 남지 않아 재생으로 되돌아갈 수 없다 — 드리프트 뒤 상태에서만 관찰된
    // 단위는 꺼내는 순서에 따라 잔여로 남을 수 있다(보고서 R5 우려 ① · D-F로 드러났다).
    // 조용히 사라지지는 않는다는 것을 고정한다: 잔여로 남았다면 그 사유가 문서에 있어야 한다.
    // 사유는 재생 쪽 실패면 어느 갈래든 된다 — B2(상태별 훑기)로 같은 단위가 «종점 불일치»
    // 대신 «재생 중 대상을 찾지 못했다»로 끊기기도 한다(잔여 수는 4로 그대로다 — 4d 실측).
    for (const unit of summary.residual) {
      const failed = doc.steps.filter((s) => s.target === unit.target && s.status !== 'executed'
        && s.action === unit.action && (s.option === undefined ? null : s.option) === unit.option);
      assert.ok(failed.some((s) => /^재생 /.test(s.error || '')),
        `사유 없는 잔여: ${JSON.stringify(unit)}`);
    }
  });

  test('훑기 한계 사유 — 나중 상태의 중단이 앞선 상태의 완주를 이긴다', async (t) => {
    const { doc } = await observeRoute(t, 'sweep-late-drift', 'late-drift', SWEEP_LATE_DRIFT_HTML);
    const rows = doc.discovery_limits.filter((row) => row.kind === 'scroll-container');
    assert.equal(rows.length, 1, JSON.stringify(doc.discovery_limits));
    // 초기 상태는 완주로 훑었고(리스너 없음) «리스너 달기» 뒤 상태에서 중단했다 —
    // 행 하나가 남는 이상 남아야 할 사실은 «잘렸다»는 쪽이다(리뷰 Minor 1).
    assert.match(rows[0].reason, /위치까지 훑다가 상태가 달라져 중단했다/);
    assert.match(rows[0].reason, /\(훑은 상태 [2-9][0-9]*\)$/);
  });

  test('굴린 자리의 가림 — 실행하지 않고 unclickable로 적는다', async (t) => {
    const { summary, doc } = await observeRoute(t, 'barred', 'barred', BARRED_HTML);
    const deep = Object.entries(doc.targets).find(([, t2]) => t2.name === '아래 버튼');
    assert.ok(deep, '아래 버튼이 열거되지 않았다');
    // 시험이 헛돌지 않으려면 그 대상이 초기에 활성(창 밖)이라 큐에 들어야 한다(D-B′).
    const initial = doc.initial.inventory.find((e) => e.id === deep[0]);
    assert.deepEqual([initial.enabled, initial.occluded], [true, false]);

    const steps = doc.steps.filter((s) => s.target === deep[0]);
    assert.equal(steps.filter((s) => s.status === 'executed').length, 0, '굴린 자리에서 가려진 대상을 눌렀다');
    assert.equal(steps.length, 1, JSON.stringify(steps.map((s) => [s.n, s.status, s.error])));
    assert.equal(steps[0].status, 'unclickable');
    assert.match(steps[0].error, /굴린 자리에서/);
    assert.equal(steps[0].after, null);
    // "비활성/가림 대상의 executed"는 K3 반례다 — 어느 step도 그래서는 안 된다.
    for (const step of doc.steps.filter((s) => s.status === 'executed')) {
      const entry = step.before.inventory.find((e) => e.id === step.target);
      if (!entry) continue;
      assert.deepEqual([entry.enabled, entry.occluded], [true, false], `step ${step.n}`);
    }
    // "unclickable은 세지 않는다"(K1) — 그 단위는 잔여에 남는다.
    assert.deepEqual(summary.residual, [{ target: deep[0], action: 'click', option: null }]);
    assert.equal(doc.partial, false);
  });

  test('복구 재인벤토리 — 거기서만 활성인 대상도 큐에 들어 실행된다', async (t) => {
    const { summary, doc } = await observeRoute(t, 'revive', 'revive', REVIVE_HTML);
    const hidden = Object.entries(doc.targets).find(([, t2]) => t2.name === '가림 버튼');
    assert.ok(hidden, '가림 버튼이 열거되지 않았다');

    // 초기·after 인벤토리에서는 가려져 있고(비활성), 복구 재인벤토리(step의 before)에서만
    // 활성으로 관찰된다 — 시험이 헛돌지 않으려면 그 비대칭이 실제로 있어야 한다.
    const activeIn = (inv) => inv.some((e) => e.id === hidden[0] && e.enabled && !e.occluded);
    assert.equal(activeIn(doc.initial.inventory), false, '초기부터 활성이라 시험이 헛돈다');
    const befores = doc.steps.filter((s) => s.before && activeIn(s.before.inventory));
    assert.ok(befores.length >= 1, '복구 재인벤토리에서도 활성이 아니라 시험이 헛돈다');

    // "문서에 남는 인벤토리는 예외 없이 큐 확장 출처"(3b 불변식 · D-E) — 아니면 영구 잔여다.
    assert.ok(doc.steps.some((s) => s.target === hidden[0] && s.status === 'executed'), '가림 버튼 미실행');
    assert.deepEqual(summary.residual, []);
    assert.deepEqual(pure.residual(doc), []);
    assert.equal(doc.partial, false);
    // 실행된 step의 before에서는 가려져 있지 않다(K3 반례 방어).
    for (const step of doc.steps.filter((s) => s.status === 'executed')) {
      const entry = step.before.inventory.find((e) => e.id === step.target);
      if (!entry) continue;
      assert.deepEqual([entry.enabled, entry.occluded], [true, false], `step ${step.n}`);
    }
  });

  test('복구 재인벤토리 재개 — 앞 슬라이스 step의 before에서만 활성이던 대상도 이어 달려 실행된다', async (t) => {
    const build = tempBuild(t, 'revive');
    const opts = {
      url: `${ctx.base}/revive.html`, rootSelector: '[data-screen-label="revive"]',
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(REVIVE_HTML),
      archiveSha: 'f'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node',
    };
    const newPage = async () => {
      const page = await ctx.browser.newPage({ viewport: { width: 560, height: 400 }, reducedMotion: 'reduce' });
      t.after(() => page.close());
      return page;
    };
    const activeIn = (inv, id) => inv.some((e) => e.id === id && e.enabled && !e.occluded);

    // 슬라이스 1 — «아래 버튼» 1 step에서 상한. 그 step의 before(복구 재인벤토리)에서만
    // «가림 버튼»이 활성이고 initial·after에서는 가려져 있다(시험이 헛돌지 않을 비대칭).
    await observe(await newPage(), { ...opts, maxSteps: 1 });
    const first = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    const hidden = Object.entries(first.targets).find(([, t2]) => t2.name === '가림 버튼');
    assert.ok(hidden, '가림 버튼이 열거되지 않았다');
    assert.equal(first.partial, true);
    assert.deepEqual(first.steps.map((s) => [nameIn(first, s.target), s.status]), [['아래 버튼', 'executed']]);
    assert.equal(activeIn(first.initial.inventory, hidden[0]), false, '초기부터 활성이라 시험이 헛돈다');
    assert.equal(activeIn(first.steps[0].before.inventory, hidden[0]), true, '복구 재인벤토리에서 활성이 아니라 시험이 헛돈다');
    assert.equal(activeIn(first.steps[0].after.inventory, hidden[0]), false, 'after에서도 활성이라 시험이 헛돈다');

    // 슬라이스 2 — "문서에 남는 인벤토리는 예외 없이 큐 확장 출처"(3b 불변식 · D-E)는 재개
    // 복원에도 같다: executed step의 before 인벤토리도 확장 출처다. 종전에는 after가 있는
    // step의 before를 버려 «가림 버튼»이 큐에 없는 채 partial:false로 끝났다(최종 리뷰 I1).
    const summary = await observe(await newPage(), { ...opts, resume: true });
    const done = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    assert.deepEqual(done.steps[0], first.steps[0]); // 앞선 step은 그대로 잇는다
    assert.ok(done.steps.some((s) => s.target === hidden[0] && s.status === 'executed'),
      `가림 버튼 미실행 — ${JSON.stringify(done.steps.map((s) => [nameIn(done, s.target), s.status]))}`);
    assert.deepEqual(summary.residual, []);
    assert.deepEqual(pure.residual(done), []);
    assert.equal(done.partial, false);
    assert.deepEqual(done.caps_hit, []);
    for (const step of done.steps.filter((s) => s.status === 'executed')) {
      const entry = step.before.inventory.find((e) => e.id === step.target);
      if (!entry) continue;
      assert.deepEqual([entry.enabled, entry.occluded], [true, false], `step ${step.n}`);
    }
  });

  test('상태별 훑기 — 같은 dom_path 컨테이너의 두 목록이 전부 executed(B2)', async (t) => {
    const { doc } = await observeRoute(t, 'sweep-state', 'sweepstate', SWEEP_STATE_HTML, { maxSteps: 200 });
    const executedNames = new Set(doc.steps
      .filter((s) => s.status === 'executed').map((s) => doc.targets[s.target].name));

    // "훑기는 (상태 해시, dom_path)별로 — 전역 dom_path 중복 제거 금지"(결정 B2).
    for (const name of ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6']) {
      assert.ok(executedNames.has(name), `${name} 미실행(${[...executedNames].sort().join(',')})`);
    }
    // 한계 행은 dom_path당 하나를 유지하고 사유에 훑은 상태 수를 누적한다(B2).
    const rows = doc.discovery_limits.filter((row) => row.kind === 'scroll-container');
    assert.equal(rows.length, 1, JSON.stringify(doc.discovery_limits));
    assert.deepEqual(Object.keys(rows[0]), ['kind', 'dom_path', 'reason']);
    const states = Number((/훑은 상태 (\d+)/.exec(rows[0].reason) || [])[1]);
    assert.ok(states >= 2, rows[0].reason);

    // 복구 재인벤토리로 드러난 항목은 «다른 항목 click 뒤»가 아니라 메뉴가 열린 상태의
    // 계보를 든다(결정 B1) — 형제 항목이 바로 위 부모로 끼면 재생이 서고 unreachable이
    // 된다(6차 실측 [… 시·군, 보성군, 고흥군] 5건). 이 단언은 **판별이 아니라 가드**다:
    // 항목 클릭이 메뉴를 닫는 이 화면에서는 형제가 부모로 낄 자리가 애초에 없다. B1의
    // 판별 RED는 `order` describe의 `_internals.acceptState` 시험이 갖는다.
    for (const step of doc.steps) {
      const owner = doc.targets[step.target].owner;
      const parent = doc.targets[step.path[step.path.length - 2]];
      if (!owner || !parent) continue;
      assert.notEqual(parent.owner, owner, `step ${step.n} 부모 경로 끝이 형제 항목이다`);
    }
    assert.deepEqual(doc.steps.filter((s) => s.status === 'unreachable').map((s) => [s.n, s.error]), []);
  });

  test('빈 입력 우선 — 등록 흐름에서 fill이 «다음» 재실행보다 먼저 꺼내진다(O1)', async (t) => {
    const { doc } = await observeRoute(t, 'register', 'register', REGISTER_HTML, { maxSteps: 60 });
    const one = (name) => {
      const hits = Object.entries(doc.targets).filter(([, t2]) => t2.name === name);
      assert.equal(hits.length, 1, `대상 «${name}» ${hits.length}개`);
      return hits[0][0];
    };
    const enter = one('등록');
    const edit = one('수정');
    const name = one('이름'); // 두 흐름이 같은 identity를 쓴다(시험 전제)
    const next = one('다음');

    // 전제 — 수정 흐름이 먼저 돌아 «이름» fill·«다음» click 단위를 이미 소비했다.
    const before = doc.steps.filter((s) => s.status === 'executed' && s.path[0] === edit);
    assert.ok(before.some((s) => s.target === name && s.action === 'fill'), '수정 흐름의 이름 fill이 없다');
    assert.ok(before.some((s) => s.target === next && s.action === 'click'), '수정 흐름의 다음 click이 없다');

    // "②b: 빈 입력(value_empty=true) fill/select를 ② 뒤·③ 앞에"(결정 O1) — 등록 흐름에서
    // 처음 꺼내지는 것이 그 fill이다. 아니면 ⑥(늦게 들어온 항목)이 «다음» 재실행을 택한다.
    const flow = doc.steps.filter((s) => s.status === 'executed' && s.path[0] === enter && s.path.length > 1);
    assert.ok(flow.length > 0, '등록 흐름 step이 없다');
    assert.deepEqual([flow[0].target, flow[0].action], [name, 'fill'],
      `등록 흐름 첫 조작이 ${doc.targets[flow[0].target].name}:${flow[0].action}이다`);

    // 그 fill이 진행 조건이라 단계 2에 도달한다.
    const done = Object.entries(doc.targets).find(([, t2]) => t2.name === '완료');
    assert.ok(done, '단계 2가 열거되지 않았다');
    assert.ok(doc.steps.some((s) => s.target === done[0] && s.status === 'executed'), '단계 2에 이르지 못했다');
  });

  test('이름 있는 handler 토글 — 두 surface가 각각 executed이고 잔여 0(D-H)', async (t) => {
    const { summary, doc } = await observeRoute(t, 'leap-toggle', 'leap', LEAP_TOGGLE_HTML);
    const leap = Object.entries(doc.targets).find(([, t2]) => t2.name === '윤달');
    assert.ok(leap, '«윤달» 대상이 열거되지 않았다');
    assert.equal(leap[1].kind, 'handler');
    assert.equal(leap[1].role, ''); // role 없는 <label> 핸들러(A8 판형)

    const steps = doc.steps.filter((s) => s.target === leap[0] && s.status === 'executed');
    assert.equal(steps.length, 2, `click ${steps.length}회 — 관찰된 surface마다 1회여야 한다`);
    assert.equal(new Set(steps.map((s) => s.option)).size, 2);
    for (const step of steps) {
      assert.match(step.option, /^[0-9a-f]{64}$/);
      const entry = step.before.inventory.find((e) => e.id === leap[0]);
      assert.equal(step.option, entry.surface, `step ${step.n} option이 before surface가 아니다`);
    }
    assert.deepEqual(summary.residual, []);
    assert.deepEqual(pure.residual(doc), []);
    assert.equal(doc.partial, false);
    assert.deepEqual(doc.caps_hit, []);
  });

  test('인라인 style·자식 아이콘으로만 켜지는 토글 — 서브트리 서명이 두 상태를 가른다(D-J)', async (t) => {
    const { summary, doc } = await observeRoute(t, 'inline-toggle', 'inline', INLINE_TOGGLE_HTML);

    const leap = Object.entries(doc.targets).find(([, t2]) => t2.name === '윤달에 태어났어요');
    assert.ok(leap, '«윤달에 태어났어요» 대상이 열거되지 않았다');
    assert.equal(leap[1].kind, 'handler');
    assert.equal(leap[1].role, '');

    const onlyInline = Object.entries(doc.targets).find(([, t2]) => t2.name === '인라인만');
    assert.ok(onlyInline, '«인라인만» 대상이 열거되지 않았다');
    assert.equal(onlyInline[1].kind, 'handler');
    assert.equal(onlyInline[1].role, '');

    // 두 label이 같은 페이지의 독립 토글이라 결합 상태 공간(2×2)을 BFS가 온전히
    // 훑는다 — 실측: 각 대상 4 executed step(옵션마다 서로 다른 두 전임 상태에서 한
    // 번씩, 양방향)·잔여 0. «관찰된 surface마다 1회 이상»(D-H)은 지키되 leap-toggle.html
    // (페이지에 토글이 하나뿐)처럼 정확히 2회로 못 박지 않는다 — 이 페이지엔 «인라인만»
    // 이라는 둘째 독립 토글이 있어 상태 결합이 그 최소치를 넘는다(«클릭 2회»는 실측과
    // 다르다 — 스펙 검토 이력 «드라이런 7차/8차 · D-J 반영(구현 Task 4f)» 실측).
    for (const [id, targetLabel] of [[leap[0], '윤달에 태어났어요'], [onlyInline[0], '인라인만']]) {
      const steps = doc.steps.filter((s) => s.target === id && s.status === 'executed');
      assert.ok(steps.length >= 2, `${targetLabel}: click ${steps.length}회 — 관찰된 surface마다 1회 이상이어야 한다`);
      assert.equal(new Set(steps.map((s) => s.option)).size, 2, `${targetLabel}: 두 surface가 서로 달라야 한다`);
      for (const step of steps) {
        assert.match(step.option, /^[0-9a-f]{64}$/);
        const entry = step.before.inventory.find((e) => e.id === id);
        assert.equal(step.option, entry.surface, `${targetLabel} step ${step.n} option이 before surface가 아니다`);
      }
    }

    assert.deepEqual(summary.residual, []);
    assert.deepEqual(pure.residual(doc), []);
    assert.equal(doc.partial, false);
    assert.deepEqual(doc.caps_hit, []);
  });

  test('자식 SVG의 class로만 켜지는 토글 — className 폴백이 두 surface를 가른다(D-J)', async (t) => {
    const { summary, doc } = await observeRoute(t, 'svg-toggle', 'svg', SVG_TOGGLE_HTML);
    const star = Object.entries(doc.targets).find(([, t2]) => t2.name === '즐겨찾기');
    assert.ok(star, '«즐겨찾기» 대상이 열거되지 않았다');
    assert.equal(star[1].kind, 'handler');
    assert.equal(star[1].role, '');

    // 두 상태의 차이는 <svg class> 하나뿐이다 — SVG의 className은 SVGAnimatedString이라
    // `getAttribute('class')` 폴백이 없으면 surface가 같아져 click 1회로 끝난다.
    const steps = doc.steps.filter((s) => s.target === star[0] && s.status === 'executed');
    assert.equal(steps.length, 2, `click ${steps.length}회 — 관찰된 surface마다 1회여야 한다`);
    assert.equal(new Set(steps.map((s) => s.option)).size, 2, 'svg class 차이가 surface에 반영되지 않았다');
    for (const step of steps) {
      assert.match(step.option, /^[0-9a-f]{64}$/);
      const entry = step.before.inventory.find((e) => e.id === star[0]);
      assert.equal(step.option, entry.surface, `step ${step.n} option이 before surface가 아니다`);
    }
    assert.deepEqual(summary.residual, []);
    assert.deepEqual(pure.residual(doc), []);
    assert.equal(doc.partial, false);
    assert.deepEqual(doc.caps_hit, []);
  });

  // 라우트 전용 화면을 한 번 관찰하고 문서를 돌려주는 공용 절차.
  async function observeRoute(t, page_name, label, html, over = {}) {
    const build = tempBuild(t, page_name);
    const page = await ctx.browser.newPage({ viewport: { width: 560, height: 400 }, reducedMotion: 'reduce' });
    t.after(() => page.close());
    const summary = await observe(page, {
      url: `${ctx.base}/${page_name}.html`, rootSelector: `[data-screen-label="${label}"]`,
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(html),
      archiveSha: 'f'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node', ...over,
    });
    return { summary, build, doc: JSON.parse(fs.readFileSync(build.out, 'utf8')) };
  }

  test('cascade select — 부모 값이 바뀌어 사라진 옵션을 다시 큐에 넣지 않는다', async (t) => {
    const { summary, doc } = await observeRoute(t, 'cascade-select', 'cascade', CASCADE_SELECT_HTML);

    // 사라진 옵션을 고르려 들면 selectOption이 실패해 failed step이 남는다.
    assert.deepEqual(doc.steps.filter((s) => s.status === 'failed').map((s) => s.error), []);
    const executedNames = doc.steps
      .filter((s) => s.status === 'executed' && s.action === 'select')
      .map((s) => doc.targets[s.target].name);
    for (const name of ['가', '나', 'a1', 'a2', 'a3', 'b1', 'b2']) {
      assert.ok(executedNames.includes(name), `${name} 미실행(${executedNames.join(',')})`);
    }
    assert.deepEqual(summary.residual, []);
    assert.equal(doc.partial, false);
    assert.deepEqual(doc.caps_hit, []);
  });

  test('cascade select 재개 — 부모 값을 골라야 나타나는 자식 옵션도 이어 달려 닫는다', async (t) => {
    const build = tempBuild(t, 'cascade-select');
    const args = (extra) => [
      WRAPPER, '--url', `${ctx.base}/cascade-select.html`, '--root', '[data-screen-label="cascade"]',
      '--viewport', '560x400', '--entrypoint-sha', sha256Text(CASCADE_SELECT_HTML),
      '--archive-sha', 'f'.repeat(64), '--out', build.out, '--crop-root', ...extra,
    ];

    // 5에서 끊으면 부모 «나»의 b1과 «가»의 a1·a2가 발견만 되고 실행되지 않는다 —
    // 옵션은 인벤토리 entries에 없어, 재개가 first_seen_step 상태에서 되넣지 않으면
    // 영구 잔여가 된다.
    const first = await runWrapper(args(['--max-steps', '5']));
    assert.equal(first.status, 3, first.stderr);
    const partial = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    const executedIn = (doc) => new Set(doc.steps
      .filter((s) => s.status === 'executed' && s.action === 'select')
      .map((s) => doc.targets[s.target].name));
    const cut = executedIn(partial);
    assert.ok(['a1', 'a2', 'b1'].some((name) => !cut.has(name)), `끊긴 지점이 너무 늦다: ${[...cut]}`);

    const second = await runWrapper(args(['--resume']));
    assert.equal(second.status, 0, second.stderr);
    const done = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    const names = executedIn(done);
    for (const name of ['가', '나', 'a1', 'a2', 'a3', 'b1', 'b2']) {
      assert.ok(names.has(name), `${name} 미실행(${[...names].join(',')})`);
    }
    assert.deepEqual(done.steps.filter((s) => s.status === 'unreachable').map((s) => s.error), []);
    assert.deepEqual(JSON.parse(second.stdout).residual, []);
    assert.equal(done.partial, false);
    assert.deepEqual(done.caps_hit, []);
  });

  test('cascade 재개 — 돌아갈 다른 이유가 없는 자식 옵션도 first_seen 상태에서 되살린다', async (t) => {
    const build = tempBuild(t, 'cascade-flat');
    const args = (extra) => [
      WRAPPER, '--url', `${ctx.base}/cascade-flat.html`, '--root', '[data-screen-label="flat"]',
      '--viewport', '560x400', '--entrypoint-sha', sha256Text(CASCADE_FLAT_HTML),
      '--archive-sha', 'a'.repeat(64), '--out', build.out, '--crop-root', ...extra,
    ];
    const optionValues = (doc) => new Set(doc.steps
      .filter((s) => s.status === 'executed' && s.action === 'select')
      .map((s) => s.option));

    // 2에서 끊으면 부모 «나»가 막 드러낸 자식 옵션(b1·b2)이 큐에만 남는다. 자식 이름이
    // 모두 같아 부모 옵션의 context_T가 고정이므로 그 상태로 돌아갈 다른 단위가 없다.
    const first = await runWrapper(args(['--max-steps', '2']));
    assert.equal(first.status, 3, first.stderr);
    const cut = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    assert.equal(cut.steps.length, 2);
    assert.equal(optionValues(cut).has('b1'), false);

    const second = await runWrapper(args(['--resume']));
    assert.equal(second.status, 0, second.stderr);
    const done = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    const values = optionValues(done);
    for (const value of ['', 'a', 'b', 'a1', 'a2', 'a3', 'b1', 'b2']) {
      assert.ok(values.has(value), `${value || '(빈 값)'} 미실행(${[...values].join(',')})`);
    }
    assert.deepEqual(done.steps.filter((s) => s.status === 'unreachable').map((s) => s.error), []);
    assert.deepEqual(JSON.parse(second.stdout).residual, []);
    assert.equal(done.partial, false);
  });

  test('로드 오류 — 조작이 부른 404 스크립트는 그 step을 failed로 남기고 계속 간다', async (t) => {
    const { summary, doc } = await observeRoute(t, 'late-break', 'late', LATE_BREAK_HTML);

    assert.equal(summary.environmentError, null); // 초기 로드는 멀쩡했다
    assert.equal(doc.environment_error, null);
    assert.equal(doc.steps.length, 1);
    assert.equal(doc.steps[0].status, 'failed');
    assert.match(doc.steps[0].error, /스크립트 로드 실패/);
    assert.match(doc.steps[0].error, /missing2\.js/);
    assert.equal(doc.steps[0].after, null);
    // "failed는 세지 않는다"(K1) — 그 단위는 잔여에 남는다.
    assert.deepEqual(summary.residual, [{ target: doc.steps[0].target, action: 'click', option: null }]);
  });

  test('재개 — 같은 path의 focus/fill/blur가 섞인 깊은 화면도 이어 달린다', async (t) => {
    const build = tempBuild(t, 'deep');
    const args = (extra) => [
      WRAPPER, '--url', `${ctx.base}/deep.html`, '--root', '[data-screen-label="deep"]',
      '--viewport', '560x400', '--entrypoint-sha', sha256Text(DEEP_HTML),
      '--archive-sha', 'd'.repeat(64), '--out', build.out, '--crop-root', ...extra,
    ];

    // 13에서 끊으면 «이름이 채워진 채 열기»가 막 드러낸 깊은 단위(덧보기)가 큐에만
    // 남는다 — 그 앞에 같은 path의 focus가 fill 뒤로 기록돼 있어, 부모를 path만으로
    // 고르면 그 단위는 이름이 빈 상태로 재생돼 대상을 찾지 못한다.
    const first = await runWrapper(args(['--max-steps', '13']));
    assert.equal(first.status, 3, first.stderr);
    const partial = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    assert.equal(partial.steps.length, 13);
    // 시험이 헛돌지 않으려면 «같은 path·다른 after 상태» 짝이 앞선 실행에 실제로 있어야
    // 한다 — path만으로 부모를 고르면 그중 아무거나 집어 다른 상태로 재생한다.
    const byPath = new Map();
    for (const step of partial.steps.filter((s) => s.after)) {
      const key = JSON.stringify(step.path);
      if (!byPath.has(key)) byPath.set(key, new Set());
      byPath.get(key).add(step.after.state_hash);
    }
    assert.ok([...byPath.values()].some((hashes) => hashes.size > 1), '같은 path·다른 after 짝이 없다');

    const second = await runWrapper(args(['--resume']));
    assert.equal(second.status, 0, second.stderr);
    const done = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    assert.deepEqual(done.steps.map((s) => s.n), done.steps.map((s, i) => i + 1));
    assert.deepEqual(done.steps.slice(0, 13), partial.steps); // 앞선 step은 그대로 잇는다
    assert.deepEqual(done.steps.filter((s) => s.status === 'unreachable').map((s) => s.error), []);
    // 이어 단 부분에 그 모호한 path를 부모로 삼는 깊이 3 step이 있어야 판별력이 있다.
    assert.ok(done.steps.some((s) => s.n > 13 && s.path.length >= 4), '재개분에 깊은 step이 없다');
    assert.equal(done.partial, false);
    assert.deepEqual(done.caps_hit, []);
    assert.deepEqual(JSON.parse(second.stdout).residual, []);
  });

  test('루트 소실 — 이탈이 아닌 루트 소실은 unreachable step이고 문서는 남는다', async (t) => {
    const build = tempBuild(t, 'drop');
    const page = await ctx.browser.newPage({ viewport: { width: 560, height: 400 }, reducedMotion: 'reduce' });
    t.after(() => page.close());
    const summary = await observe(page, {
      url: `${ctx.base}/drop.html`, rootSelector: '[data-screen-label="drop"]',
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(DROP_HTML),
      archiveSha: 'e'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node',
    });
    assert.equal(summary.environmentError, null); // 드라이버 예외로 새지 않는다
    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    assert.equal(doc.steps.length, 1);
    assert.equal(doc.steps[0].status, 'unreachable');
    assert.match(doc.steps[0].error, /루트를 찾지 못했다/);
    assert.equal(doc.steps[0].after, null);
    assert.equal(doc.steps[0].navigated, null);
    // 실행으로 세지 않으므로 그 단위는 잔여에 남는다(K1).
    assert.deepEqual(summary.residual, [{ target: doc.steps[0].target, action: 'click', option: null }]);
  });

  test('상한·재개 — --max-steps에서 끊고 --resume이 이어 달려 완주한다', async (t) => {
    const build = tempBuild(t, 'small');
    const args = (extra) => [
      WRAPPER, '--url', `${ctx.base}/small.html`, '--root', '[data-screen-label="small"]',
      '--viewport', '560x1040', '--entrypoint-sha', sha256Text(ctx.smallHtml),
      '--archive-sha', 'b'.repeat(64), '--out', build.out, '--crop-root', ...extra,
    ];

    const first = await runWrapper(args(['--max-steps', '5']));
    assert.equal(first.status, 3, first.stderr);
    const partial = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    assert.equal(partial.partial, true);
    assert.deepEqual(partial.caps_hit, ['max_steps']);
    assert.equal(partial.steps.length, 5);
    assert.ok(JSON.parse(first.stdout).residual.length > 0);

    const second = await runWrapper(args(['--resume']));
    assert.equal(second.status, 0, second.stderr);
    const done = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    assert.equal(done.partial, false);
    assert.deepEqual(done.caps_hit, []);
    assert.equal(done.steps.length, 6);
    assert.deepEqual(done.steps.map((s) => s.n), [1, 2, 3, 4, 5, 6]);
    assert.deepEqual(done.steps.slice(0, 5), partial.steps); // 앞선 step은 그대로 잇는다
    assert.deepEqual(JSON.parse(second.stdout).residual, []);
  });

  test('재개 대조 — entrypoint·served sha가 다르면 exit 1이고 문서를 덮어쓰지 않는다', async (t) => {
    const build = tempBuild(t, 'small');
    const originalSha = sha256Text(ctx.smallHtml);
    const args = (extra, sha = originalSha) => [
      WRAPPER, '--url', `${ctx.base}/small.html`, '--root', '[data-screen-label="small"]',
      '--viewport', '560x1040', '--entrypoint-sha', sha, '--archive-sha', 'b'.repeat(64),
      '--out', build.out, '--crop-root', ...extra,
    ];
    const first = await runWrapper(args(['--max-steps', '2']));
    assert.equal(first.status, 3, first.stderr);

    t.after(() => { ctx.smallHtml = SMALL_HTML; });
    ctx.smallHtml = `${SMALL_HTML} `; // 1바이트 변경

    const changed = await runWrapper(args(['--resume'], sha256Text(ctx.smallHtml)));
    assert.equal(changed.status, 1, changed.stderr);
    assert.match(changed.stderr, /재개/);
    assert.match(JSON.parse(changed.stdout).environmentError, /entrypoint/);

    const staleSha = await runWrapper(args(['--resume'])); // 옛 sha를 그대로 주면 served가 잡는다
    assert.equal(staleSha.status, 1, staleSha.stderr);
    assert.match(JSON.parse(staleSha.stdout).environmentError, /served/);

    assert.equal(JSON.parse(fs.readFileSync(build.out, 'utf8')).steps.length, 2);
  });
});

// =====================================================================
// discovery — CDP 리스너 매핑 · 발견 조작(hover·스크롤) · same-origin iframe 조작
//   K2 발견 채널(CDP 리스너·hover·스크롤·iframe 한계)
//   K7 collector.capabilities · step.discovery · discovery_limits
// =====================================================================
describe('discovery', () => {
  const LIMIT_KEYS = ['kind', 'dom_path', 'reason'];
  const run = { doc: null, summary: null, build: null, noise: [] };

  before(async () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ia-discovery-'));
    run.build = {
      dir, capturesDir: path.join(dir, 'captures'),
      out: path.join(dir, 'captures', 'discovery-interactions.json'),
    };
    const page = await ctx.browser.newPage({ viewport: { width: 560, height: 400 }, reducedMotion: 'reduce' });
    page.on('console', (m) => run.noise.push(`[${m.type()}] ${m.text()}`));
    page.on('pageerror', (e) => run.noise.push(`[pageerror] ${e.message}`));
    run.summary = await observe(page, {
      url: `${ctx.base}/discovery.html`, rootSelector: '[data-screen-label="discovery"]',
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(DISCOVERY_HTML),
      archiveSha: '9'.repeat(64), out: run.build.out, capturesDir: run.build.capturesDir,
      path: 'node',
    });
    await page.close();
    run.doc = JSON.parse(fs.readFileSync(run.build.out, 'utf8'));
  });

  after(() => {
    // 정리가 단언보다 앞이다 — 잡음 단언이 실패해도 temp를 남기지 않는다(3c 재리뷰 Minor).
    try {
      if (run.build) fs.rmSync(run.build.dir, { recursive: true, force: true });
    } finally {
      // 잡음 0은 그룹 전체의 계약이다 — 한 테스트 안에 두면 --test-name-pattern으로
      // 다른 건만 돌릴 때 검사가 빠진다(수정 라운드 1 M10). 그룹의 모든 page가 여기에 싣는다.
      assert.deepEqual(run.noise, [], '발견 실행이 콘솔 잡음을 냈다');
    }
  });

  // 그룹의 다른 테스트가 직접 여는 page도 같은 잡음 계약 아래 둔다(3c 재리뷰 Minor).
  async function openGroupPage(t, viewport) {
    const page = await ctx.browser.newPage({ viewport, reducedMotion: 'reduce' });
    page.on('console', (m) => run.noise.push(`[${m.type()}] ${m.text()}`));
    page.on('pageerror', (e) => run.noise.push(`[pageerror] ${e.message}`));
    t.after(() => page.close());
    return page;
  }

  const idNamed = (name) => {
    const hits = Object.entries(run.doc.targets).filter(([, t]) => t.name === name);
    assert.equal(hits.length, 1, `대상 «${name}» ${hits.length}개`);
    return hits[0][0];
  };
  const executedOf = (id, action) => run.doc.steps.filter(
    (s) => s.target === id && s.status === 'executed' && (action === undefined || s.action === action));

  test('CDP 리스너 — capabilities와 addEventListener 전용 대상', () => {
    assert.equal(run.summary.environmentError, null);
    // "사용 채널은 collector.capabilities에 기록한다"(K2) — Chromium 경로는 CDP가 산다.
    assert.deepEqual(run.doc.collector.capabilities, { react_props: true, cdp_listeners: true });

    // 의미도 onclick도 cursor도 아닌 요소 — CDP 리스너 열거만이 잡는다.
    const listener = idNamed('리스너만');
    assert.deepEqual(run.doc.targets[listener].found_by, ['cdp_listener']);
    assert.equal(run.doc.targets[listener].kind, 'handler');
    assert.ok(executedOf(listener, 'click').length >= 1, 'CDP로 잡은 대상이 실행되지 않았다');
  });

  test('hover 발견 — discovery step이 hover 전용 메뉴를 열고 항목이 executed', () => {
    const more = idNamed('더보기');
    const hovers = run.doc.steps.filter((s) => s.discovery === true && s.action === 'hover');
    assert.equal(hovers.length, 1, `hover 발견 step ${hovers.length}건`);
    const hover = hovers[0];
    assert.equal(hover.target, more);
    assert.equal(hover.status, 'executed');
    assert.equal(hover.option, null);
    assert.equal(hover.path[hover.path.length - 1], more);

    // 메뉴는 mouseenter로만 열린다 — hover 발견이 없으면 항목 자체가 열거되지 않는다.
    const clone = idNamed('복제');
    assert.ok(hover.changes.added.includes(clone), 'hover step이 메뉴 항목을 드러내지 않았다');
    assert.equal(run.doc.targets[clone].kind, 'menuitem');
    assert.ok(executedOf(clone, 'click').length >= 1, 'hover로 드러난 항목이 실행되지 않았다');
    // 발견 step도 added≠∅면 PNG를 남긴다(K3 — 표면 연결 대상).
    assert.equal(hover.after.capture.path, `captures/discovery-step-${hover.n}.png`);
    assert.equal(hover.after.capture.sha256, sha256File(path.join(run.build.dir, hover.after.capture.path)));
  });

  test('스크롤 발견 — 컨테이너 끝 대상이 executed이고 discovery_limits에 남는다', () => {
    for (const name of ['아래 버튼', '패널 열기']) {
      assert.ok(executedOf(idNamed(name), 'click').length >= 1, `${name} 미실행`);
    }
    // 스크롤로 드러난 버튼이 연 상태의 대상도 실행된다(발견이 큐로 이어진다).
    assert.ok(executedOf(idNamed('닫기'), 'click').length >= 1, '패널 안 대상 미실행');

    // "discovery_limits에 overflow 컨테이너 … 기록"(K2) — 컨테이너 1개 = 행 1개.
    assert.equal(run.doc.discovery_limits.length, 1, JSON.stringify(run.doc.discovery_limits));
    const limit = run.doc.discovery_limits[0];
    assert.deepEqual(Object.keys(limit), LIMIT_KEYS);
    assert.equal(limit.kind, 'scroll-container');
    assert.ok(limit.dom_path.length > 0, JSON.stringify(limit));
    assert.ok(limit.reason.length > 0, JSON.stringify(limit));
  });

  test('same-origin iframe — 프레임 안 입력이 focus·fill·blur로 executed', async (t) => {
    const build = tempBuild(t, 'frame-host');
    const page = await ctx.browser.newPage({ viewport: { width: 560, height: 400 }, reducedMotion: 'reduce' });
    const noise = [];
    page.on('console', (m) => noise.push(`[${m.type()}] ${m.text()}`));
    page.on('pageerror', (e) => noise.push(`[pageerror] ${e.message}`));
    t.after(async () => {
      await page.close();
      assert.deepEqual(noise, [], '프레임 관찰이 콘솔 잡음을 냈다');
    });
    const summary = await observe(page, {
      url: `${ctx.base}/frame-host.html`, rootSelector: '[data-screen-label="frame-host"]',
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(FRAME_HOST_HTML),
      archiveSha: '8'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node',
    });
    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));

    // 프레임 문서의 대상은 dom_path 앞에 iframe[n]/이 붙고 rect·클릭 지점은 프레임
    // 오프셋을 더한 최상위 좌표다 — 요소 핸들만 프레임 문서 좌표로 다시 잡아야 한다.
    const hits = Object.entries(doc.targets).filter(([, t2]) => t2.name === '프레임 입력');
    assert.equal(hits.length, 1, JSON.stringify(Object.values(doc.targets).map((t2) => t2.name)));
    const [input, target] = hits[0];
    assert.ok(target.dom_path.startsWith('iframe[0]/'), target.dom_path);
    assert.equal(target.kind, 'input');

    const executed = (action) => doc.steps.filter(
      (s) => s.target === input && s.action === action && s.status === 'executed');
    for (const action of ['focus', 'blur']) {
      assert.ok(executed(action).length >= 1, `프레임 입력 ${action} 미실행`);
    }
    const fills = executed('fill');
    assert.ok(fills.length >= 1, '프레임 입력 fill 미실행');
    assert.equal(fills[0].value, '검증 입력');
    assert.deepEqual(fills[0].changes.values, [{ target: input, before: '', after: '검증 입력' }]);
    assert.deepEqual(summary.residual, []);
    assert.equal(doc.partial, false);
    assert.deepEqual(doc.discovery_limits, []); // 보이는 same-origin 프레임은 한계가 아니다
  });

  test('루트 스크롤 컨테이너 — 한계 행의 dom_path는 \'.\'(루트 자체)이고 비어 있지 않다', async (t) => {
    const build = tempBuild(t, 'root-scroll');
    const page = await openGroupPage(t, { width: 560, height: 400 });
    const summary = await observe(page, {
      url: `${ctx.base}/root-scroll.html`, rootSelector: '[data-screen-label="root-scroll"]',
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(ROOT_SCROLL_HTML),
      archiveSha: '5'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node',
    });
    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    const rows = doc.discovery_limits.filter((row) => row.kind === 'scroll-container');
    assert.equal(rows.length, 1, JSON.stringify(doc.discovery_limits));
    // 스니펫 dom_path는 루트 자식 경로라 루트 자신은 ''이다 — 문서 행은 '.'로 적는다(검사기는
    // kind·dom_path·reason 전부 nonempty를 요구한다). 훑기 자체는 루트를 굴려 완주한다.
    assert.equal(rows[0].dom_path, '.');
    assert.match(rows[0].reason, /위치를 훑어 재인벤토리했다/);
    for (const row of doc.discovery_limits) {
      for (const key of LIMIT_KEYS) assert.ok(typeof row[key] === 'string' && row[key] !== '', `${key} 비어 있음`);
    }
    for (const name of ['머리 버튼', '아래 버튼']) {
      assert.ok(doc.steps.some((s) => nameIn(doc, s.target) === name && s.status === 'executed'), `${name} 미실행`);
    }
    assert.deepEqual(summary.residual, []);
    assert.equal(doc.partial, false);
  });

  test('hover 발견 — 비활성 후보는 열지 않는다(활성 = enabled ∧ !occluded)', async (t) => {
    const build = tempBuild(t, 'hover-disabled');
    const page = await openGroupPage(t, { width: 560, height: 400 });
    const summary = await observe(page, {
      url: `${ctx.base}/hover-disabled.html`, rootSelector: '[data-screen-label="hover-disabled"]',
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(HOVER_DISABLED_HTML),
      archiveSha: '6'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node',
    });
    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    const off = Object.entries(doc.targets).find(([, t2]) => t2.name === '비활성 도움말');
    assert.ok(off, '비활성 버튼이 열거되지 않았다');
    const initial = doc.initial.inventory.find((e) => e.id === off[0]);
    assert.equal(initial.enabled, false, '초기부터 활성이라 시험이 헛돈다');

    // 비활성 대상은 발견 후보여도 열지 않는다 — hover 발견은 ensureOperable을 거치지 않는
    // 유일한 조작 경로라 여기서 걸러야 «비활성 대상의 executed»(K3 반례)가 남지 않는다.
    assert.deepEqual(doc.steps.filter((s) => s.target === off[0]).map((s) => [s.action, s.status]), []);
    for (const step of doc.steps.filter((s) => s.status === 'executed')) {
      const entry = step.before.inventory.find((e) => e.id === step.target);
      if (!entry) continue;
      assert.deepEqual([entry.enabled, entry.occluded], [true, false], `step ${step.n}`);
    }
    // 활성 후보의 hover 발견은 그대로다 — 메뉴가 열리고 항목이 실행된다.
    const hovers = doc.steps.filter((s) => s.discovery === true && s.action === 'hover');
    assert.deepEqual(hovers.map((s) => [nameIn(doc, s.target), s.status]), [['더보기', 'executed']]);
    assert.ok(doc.steps.some((s) => nameIn(doc, s.target) === '복제' && s.status === 'executed'), '복제 미실행');
    assert.deepEqual(summary.residual, []);
    assert.equal(doc.partial, false);
    assert.deepEqual(doc.discovery_limits, []);
  });

  test('탭 전환 — 옛 표식이 리스너 채널을 오염시키지 않는다', async (t) => {
    const build = tempBuild(t, 'tabs');
    const page = await openGroupPage(t, { width: 560, height: 400 });
    const summary = await observe(page, {
      url: `${ctx.base}/tabs.html`, rootSelector: '[data-screen-label="tabs"]',
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(TABS_HTML),
      archiveSha: '7'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node',
    });
    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    const named = (name) => Object.entries(doc.targets).filter(([, t2]) => t2.name === name);

    // ① 유령 대상 — 리스너가 없는 <span>이 숨은 옛 패널의 버튼 표식을 물려받으면 안 된다.
    assert.deepEqual(named('그냥 글'), [], '리스너 없는 요소가 handler 대상이 됐다');
    assert.deepEqual(named('보조 글'), [], '리스너 없는 요소가 handler 대상이 됐다');

    // ② 미탐지 — 진짜 addEventListener 요소는 대상이고 실행돼야 한다.
    const live = named('진짜 리스너');
    assert.equal(live.length, 1, '리스너 보유 요소가 대상에서 빠졌다');
    assert.deepEqual(live[0][1].found_by, ['cdp_listener']);
    assert.equal(live[0][1].kind, 'handler');
    assert.ok(doc.steps.some((s2) => s2.target === live[0][0] && s2.status === 'executed'), '리스너 보유 요소 미실행');

    assert.deepEqual(summary.residual, []);
    assert.equal(doc.partial, false);
  });

  test('발견 상한 — 못 연 hover 후보가 caps_hit·discovery_limits에 남는다', async (t) => {
    const build = tempBuild(t, 'hover-cap');
    const page = await openGroupPage(t, { width: 560, height: 400 });
    await observe(page, {
      url: `${ctx.base}/hover-cap.html`, rootSelector: '[data-screen-label="hover-cap"]',
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(HOVER_CAP_HTML),
      archiveSha: '6'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node',
      maxSteps: 1, // 첫 hover 발견 뒤 바로 상한 — 둘째 후보는 열어 보지도 못한다
    });
    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));

    const hovers = doc.steps.filter((s2) => s2.discovery === true);
    assert.equal(hovers.length, 1, `발견 step ${hovers.length}건`);
    assert.equal(doc.targets[hovers[0].target].name, '하나');
    // 열어 보지 못한 후보가 문서에 남지 않으면 «거짓 완주»가 된다(K1 상한·K2 한계).
    assert.equal(doc.partial, true);
    assert.deepEqual(doc.caps_hit, ['max_steps']); // 같은 cap을 두 번 적지 않는다
    const skipped = doc.discovery_limits.filter((row) => row.kind === 'hover-candidate');
    assert.equal(skipped.length, 1, JSON.stringify(doc.discovery_limits));
    assert.deepEqual(Object.keys(skipped[0]), ['kind', 'dom_path', 'reason']);
    assert.ok(skipped[0].dom_path.length > 0, JSON.stringify(skipped[0]));
    assert.match(skipped[0].reason, /상한/);
  });

  test('재개 — 앞선 슬라이스가 연 hover 후보를 다시 열지 않는다', async (t) => {
    const build = tempBuild(t, 'hover-resume');
    const opts = {
      url: `${ctx.base}/hover-cap.html`, rootSelector: '[data-screen-label="hover-cap"]',
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(HOVER_CAP_HTML),
      archiveSha: '7'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node',
    };
    // 슬라이스 1 — 첫 hover 발견(«하나») 직후 상한.
    await observe(await openGroupPage(t, { width: 560, height: 400 }), { ...opts, maxSteps: 1 });
    const first = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    assert.deepEqual(first.steps.map((s) => [nameIn(first, s.target), s.discovery]), [['하나', true]]);

    // 슬라이스 2 — 발견은 실행당 한 번이다: «하나»는 앞선 step에서 이미 열었으므로 다시 만들지
    // 않고(그 뒤 상태는 재개 복원이 되살린다), 못 연 «둘»만 연다. 종전에는 복원이 `continue`
    // 뒤에 있어 슬라이스마다 같은 hover가 되풀이됐다(4d 재리뷰 범위 밖 1).
    const summary = await observe(await openGroupPage(t, { width: 560, height: 400 }), { ...opts, resume: true });
    const done = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    const hovers = done.steps.filter((s) => s.discovery === true).map((s) => nameIn(done, s.target));
    assert.deepEqual(hovers.sort(), ['둘', '하나'], `발견 step ${JSON.stringify(hovers)}`);
    // 되살린 상태에서 열린 «항목 1»도 hover 재생으로 닿아 실행된다 — 발견을 생략해도 그 뒤가 사라지지 않는다.
    for (const name of ['항목 1', '항목 2']) {
      assert.ok(done.steps.some((s) => nameIn(done, s.target) === name && s.status === 'executed'), `${name} 미실행`);
    }
    assert.deepEqual(summary.residual, []);
    assert.equal(done.partial, false);
    assert.deepEqual(done.caps_hit, []);
    assert.deepEqual(done.discovery_limits.filter((row) => row.kind === 'hover-candidate'), []);
  });

  test('재개 — 상한으로 남은 «미실행» 발견 행은 실제로 열면 사라진다', async (t) => {
    const build = tempBuild(t, 'resume-cap');
    const args = (extra) => [
      WRAPPER, '--url', `${ctx.base}/resume-cap.html`, '--root', '[data-screen-label="resume-cap"]',
      '--viewport', '560x400', '--entrypoint-sha', sha256Text(RESUME_CAP_HTML),
      '--archive-sha', '4'.repeat(64), '--out', build.out, '--crop-root', ...extra,
    ];
    const capped = (doc) => doc.discovery_limits.filter((row) => /상한/.test(row.reason));

    // 패널을 연 step 바로 뒤에 상한이 걸려 스크롤·hover 둘 다 열어 보지 못한다.
    const first = await runWrapper(args(['--max-steps', '1']));
    assert.equal(first.status, 3, first.stderr);
    const cut = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    assert.equal(cut.steps.length, 1);
    assert.deepEqual(capped(cut).map((row) => row.kind).sort(), ['hover-candidate', 'scroll-container']);

    // 이어 단 슬라이스가 실제로 열면 그 행은 거짓이 된다 — 지우고(hover) 성공 행이
    // 그 자리를 대신한다(스크롤).
    const second = await runWrapper(args(['--resume']));
    assert.equal(second.status, 0, second.stderr);
    const done = JSON.parse(fs.readFileSync(build.out, 'utf8'));
    assert.deepEqual(capped(done), []);
    assert.deepEqual(done.discovery_limits.filter((row) => row.kind === 'hover-candidate'), []);
    const scrolled = done.discovery_limits.filter((row) => row.kind === 'scroll-container');
    assert.equal(scrolled.length, 1, JSON.stringify(done.discovery_limits));
    assert.match(scrolled[0].reason, /위치를 훑어 재인벤토리했다/); // D-D로 사유 문구가 바뀌었다
    assert.ok(done.steps.some((s) => s.discovery === true && s.status === 'executed'), '발견 step이 없다');
    assert.deepEqual(JSON.parse(second.stdout).residual, []);
    assert.equal(done.partial, false);
    assert.deepEqual(done.caps_hit, []);
  });

  test('복구 중단 — 끝내 열지 못한 hover 후보는 사유가 바뀐 한계 행으로 남는다', async (t) => {
    const build = tempBuild(t, 'hover-drift');
    const page = await openGroupPage(t, { width: 560, height: 400 });
    await observe(page, {
      url: `${ctx.base}/hover-drift.html`, rootSelector: '[data-screen-label="hover-drift"]',
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(HOVER_DRIFT_HTML),
      archiveSha: '3'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node',
    });
    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));

    // 굴리는 사이 상태가 달라져 hover를 시도하지 못했다 — step이 없으므로 한계 행이 유일한 흔적이다.
    assert.deepEqual(doc.steps.filter((s) => s.discovery === true).map((s) => s.n), []);
    const rows = doc.discovery_limits.filter((row) => row.kind === 'hover-candidate');
    assert.equal(rows.length, 1, JSON.stringify(doc.discovery_limits));
    assert.deepEqual(Object.keys(rows[0]), ['kind', 'dom_path', 'reason']);
    assert.match(rows[0].reason, /굴리는 사이에 상태가 달라져/);
    // 열지 못한 메뉴 항목은 애초에 열거되지 않는다(«복제»는 대상이 아니다).
    assert.deepEqual(Object.values(doc.targets).filter((t2) => t2.name === '복제'), []);
  });

  test('CDP 불가 — capabilities false로 적고 cursor 보조로 내려간다', async (t) => {
    const build = tempBuild(t, 'fixture');
    const page = await openGroupPage(t, { width: 560, height: 1040 });
    const summary = await observe(page, {
      url: `${ctx.base}/fixture.html`, rootSelector: ROOT_SELECTOR, browserViewport: [560, 1040],
      cropToRoot: true, entrypointSha: fixtureSha(), archiveSha: '5'.repeat(64),
      out: build.out, capturesDir: build.capturesDir, excludedRegions: [{ selector: '#knobs', reason: '픽스처 노브' }],
      path: 'node', maxSteps: 1, listeners: 'none', // CDP 세션을 아예 열지 않는 경로
    });
    const doc = JSON.parse(fs.readFileSync(build.out, 'utf8'));

    assert.equal(summary.environmentError, null);
    assert.deepEqual(Object.keys(doc), DOC_KEYS); // K7 판형은 그대로다
    assert.deepEqual(doc.collector.capabilities, { react_props: true, cdp_listeners: false });
    // "cursor:pointer는 CDP가 없을 때만 보조로"(K2) — 그 채널이 실제로 켜진다.
    const byName = (name) => Object.values(doc.targets).filter((t2) => t2.name === name);
    assert.ok(byName('직접 클릭')[0].found_by.includes('cursor'), JSON.stringify(byName('직접 클릭')));
    // 선언도 CDP도 없으면 addEventListener 전용 요소는 대상이 아니다(K2 채널 목록).
    assert.deepEqual(byName('리스너만'), []);
  });

  test('발견 판형 — 잔여 0 · discovery는 boolean · 가려진 대상은 실행하지 않는다', () => {
    assert.deepEqual(run.summary.residual, []);
    assert.deepEqual(pure.residual(run.doc), []);
    assert.equal(run.doc.partial, false);
    assert.deepEqual(run.doc.caps_hit, []);

    for (const step of run.doc.steps) {
      assert.deepEqual(Object.keys(step), [
        'n', 'path', 'target', 'action', 'option', 'value', 'context', 'status', 'error',
        'before', 'after', 'changes', 'navigated', 'discovery',
      ], `step ${step.n}`);
      assert.equal(typeof step.discovery, 'boolean', `step ${step.n}`);
      assert.match(step.context, /^[0-9a-f]{16}$/);
      if (step.status !== 'executed') continue;
      // "비활성/가림 대상의 executed"는 K3 반례다 — 스크롤을 되돌린 재생에서도 지켜야 한다.
      const entry = step.before.inventory.find((e) => e.id === step.target);
      if (!entry) continue;
      assert.equal(entry.occluded, false, `step ${step.n}(${step.action})`);
      assert.equal(entry.enabled, true, `step ${step.n}(${step.action})`);
    }
  });
});

// =====================================================================
// closing — 페이지 소실(드라이런 6차 결정 D-I). 조작이 페이지를 없애면 그 자리에서
//   멈춰야 한다: 남은 큐를 «갈 수 없는 곳»으로 비우면 문서가 partial:false로 완주처럼
//   보이고(6차 실측 2470건), --resume도 그 키를 이미 본 것으로 여겨 영원히 건너뛴다.
// =====================================================================
describe('closing', () => {
  const run = { dir: null, out: null, capturesDir: null, noise: [] };

  before(() => {
    run.dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ia-closer-'));
    run.capturesDir = path.join(run.dir, 'captures');
    run.out = path.join(run.capturesDir, 'closer-interactions.json');
  });
  after(() => { if (run.dir) fs.rmSync(run.dir, { recursive: true, force: true }); });

  // 슬라이스마다 새 page에 같은 바인딩을 건다(같은 브라우저). 바인딩은 init script라
  // goto 뒤에도 살아 있다.
  async function slice(resume) {
    const page = await ctx.browser.newPage({ viewport: { width: 560, height: 400 }, reducedMotion: 'reduce' });
    page.on('console', (m) => run.noise.push(`[${m.type()}] ${m.text()}`));
    page.on('pageerror', (e) => run.noise.push(`[pageerror] ${e.message}`));
    await page.exposeFunction('__closeMe', () => {
      setTimeout(() => page.close().catch(() => {}), 0);
      return true;
    });
    const summary = await observe(page, {
      url: `${ctx.base}/closer.html`, rootSelector: '[data-screen-label="closer"]',
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(CLOSER_HTML),
      archiveSha: '9'.repeat(64), out: run.out, capturesDir: run.capturesDir, path: 'node', resume,
    });
    if (!page.isClosed()) await page.close();
    return { summary, doc: JSON.parse(fs.readFileSync(run.out, 'utf8')) };
  }

  const closedSteps = (doc) => doc.steps.filter((s) => /^페이지가 닫혔다: /.test(s.error || ''));
  const idNamed = (doc, name) => {
    const hits = Object.entries(doc.targets).filter(([, t2]) => t2.name === name);
    assert.equal(hits.length, 1, `대상 «${name}» ${hits.length}개`);
    return hits[0][0];
  };

  test('페이지 소실 — 그 자리에서 멈추고 남은 큐를 비우지 않는다', async () => {
    const { summary, doc } = await slice(false);
    const closer = idNamed(doc, '창 닫기');
    const last = doc.steps[doc.steps.length - 1];

    // 페이지를 없앤 조작이 **마지막 step**이다 — 그 뒤로는 아무것도 관찰할 수 없다.
    assert.equal(last.target, closer,
      `마지막 step이 «창 닫기»가 아니다: ${JSON.stringify(doc.steps.map((s) => [s.n, doc.targets[s.target].name, s.status]))}`);
    assert.match(last.error || '', /^페이지가 닫혔다: /);
    assert.equal(closedSteps(doc).length, 1, '닫힌 뒤에도 step이 쌓였다');
    // 큐를 비우지 않았으므로 완주가 아니다. 상한이 아니므로 caps_hit은 그대로고,
    // 수집이 시작된 뒤의 실패라 environment_error도 아니다(K5 exit 1이 아니다).
    assert.equal(doc.partial, true);
    assert.deepEqual(doc.caps_hit, []);
    assert.equal(doc.environment_error, null);
    assert.equal(summary.environmentError, null);
    assert.equal(summary.partial, true);
  });

  test('재개 — 페이지가 닫힌 단위는 새 브라우저에서 한 번 다시 시도한다', async () => {
    const { doc } = await slice(true);
    const closed = closedSteps(doc);
    assert.equal(closed.length, 2, '재개가 그 단위를 다시 시도하지 않았다(영구 잔여가 된다)');
    assert.equal(new Set(closed.map((s) => s.target)).size, 1);
    assert.equal(closed[1].n, doc.steps[doc.steps.length - 1].n, '재시도 뒤에도 step이 쌓였다');
    assert.equal(doc.partial, true);
  });

  test('재개 — 두 번째 «페이지가 닫혔다» 뒤에는 꺼내지 않고 완주한다', async () => {
    const { summary, doc } = await slice(true);
    const closer = idNamed(doc, '창 닫기');
    assert.equal(closedSteps(doc).length, 2, '조작 자체가 페이지를 닫는 대상을 또 시도했다');

    const executed = new Set(doc.steps.filter((s) => s.status === 'executed')
      .map((s) => doc.targets[s.target].name));
    assert.ok(executed.has('가') && executed.has('나'), `남은 단위 미실행: ${[...executed].join(',')}`);
    assert.equal(doc.partial, false);
    assert.deepEqual(doc.caps_hit, []);
    // 끝내 실행하지 못한 단위는 잔여다(K3) — 작성자 면제 없이 interaction_exclusions로 닫는다.
    assert.deepEqual(summary.residual, [{ target: closer, action: 'click', option: null }]);
    assert.deepEqual(run.noise, [], '페이지가 콘솔 잡음을 냈다');
  });

  // 라우트 전용 닫힘 화면 — 자기 build·자기 page(같은 __closeMe 바인딩)로 한 슬라이스만 본다.
  async function observeClosing(t, screen, label, html) {
    const build = tempBuild(t, screen);
    const page = await ctx.browser.newPage({ viewport: { width: 560, height: 400 }, reducedMotion: 'reduce' });
    const noise = [];
    page.on('console', (m) => noise.push(`[${m.type()}] ${m.text()}`));
    page.on('pageerror', (e) => noise.push(`[pageerror] ${e.message}`));
    await page.exposeFunction('__closeMe', () => {
      setTimeout(() => page.close().catch(() => {}), 0);
      return true;
    });
    t.after(async () => { if (!page.isClosed()) await page.close(); });
    const summary = await observe(page, {
      url: `${ctx.base}/${screen}.html`, rootSelector: `[data-screen-label="${label}"]`,
      browserViewport: [560, 400], cropToRoot: true, entrypointSha: sha256Text(html),
      archiveSha: '8'.repeat(64), out: build.out, capturesDir: build.capturesDir, path: 'node',
    });
    assert.deepEqual(noise, [], '페이지가 콘솔 잡음을 냈다');
    return { summary, doc: JSON.parse(fs.readFileSync(build.out, 'utf8')) };
  }

  test('페이지 소실 — 닫는 조작이 큐의 마지막 항목이어도 완주가 아니다', async (t) => {
    const { summary, doc } = await observeClosing(t, 'closer-last', 'closer-last', CLOSER_LAST_HTML);
    const closer = idNamed(doc, '창 닫기');
    assert.deepEqual(doc.steps.map((s) => [s.target, s.status]), [[closer, 'failed']]);
    assert.match(doc.steps[0].error || '', /^페이지가 닫혔다: /);
    // 큐는 비었지만 그 step 뒤의 발견 조작을 열어 보지 못했다 — «완주»로 읽히면 D-I가 막으려던
    // 오독이 그대로 남는다(4d 재리뷰 Minor 1). 상한도 환경 오류도 아니다.
    assert.equal(doc.partial, true);
    assert.equal(summary.partial, true);
    assert.deepEqual(doc.caps_hit, []);
    assert.equal(doc.environment_error, null);
    assert.deepEqual(summary.residual, [{ target: closer, action: 'click', option: null }]);
  });

  test('페이지 소실 — 발견 조작(스크롤 훑기) 중에 닫혀도 문서는 쓰이고 partial이다', async (t) => {
    // 첫 scroll 이벤트가 page를 닫는다 — 훑기의 evaluate가 닫힌 page에서 던지는 자리다.
    const { summary, doc } = await observeClosing(t, 'closer-scroll', 'closer-scroll', CLOSER_SCROLL_HTML);
    assert.equal(summary.environmentError, null);
    assert.equal(doc.environment_error, null);
    assert.deepEqual(doc.steps, []); // 조작 하나 못 했지만 문서는 정상 판형이다
    assert.equal(doc.partial, true);
    assert.equal(summary.partial, true);
    assert.deepEqual(doc.caps_hit, []);
    assert.ok(Object.values(doc.targets).some((t2) => t2.name === '항목 1'), '초기 인벤토리가 없다');
    assert.ok(summary.residual.length >= 1, '큐를 비워 잔여를 지웠다');
  });
});

// =====================================================================
// order — 꺼내는 순서와 우선순위 카운터(D-F·D-F′·D-G). 브라우저 없이 `_internals`로
//   직접 고정한다: 실화면 순서 단언은 ①(미실행 단위)이 먼저 걸려 ②③④를 가리기 쉽다.
// =====================================================================
describe('order', () => {
  const { takeNext, recordStep, restoreVisited, noteExecuted, acceptState } = _internals;

  const queueItem = (over) => ({
    key: JSON.stringify([over.target, over.action || 'click', null, over.context || 'c']),
    unitKey: JSON.stringify([over.target, over.action || 'click', null]),
    target: over.target, action: over.action || 'click', option: null, context: over.context || 'c',
    prefixHash: over.prefixHash, ops: over.ops || [], priorFace: over.priorFace === undefined ? null : over.priorFace,
    valueEmpty: over.valueEmpty === undefined ? null : over.valueEmpty,
  });
  const newRun = (over = {}) => ({
    queue: [], seen: new Set(), executedUnits: new Set(), steps: [], stepNo: 0, capsHit: [],
    depthBlocked: new Set(), discovered: new Set(), executedFaces: new Map(), executedByState: new Map(),
    fillRuns: new Map(),
    sameStateRun: 0, lastPrefixHash: null, startedAt: Date.now(),
    current: { state_hash: 'S' }, currentPath: [], ...over,
  });
  const unitKeyOf = (target, action = 'click', option = null) => JSON.stringify([target, action, option]);
  const ctxWith = (targets) => ({ targets });

  // D-E 확장 경로는 «그 상태에 이른 부모 경로»다(결정 B1). reachState는 재생하면서 같은
  // 배열에 op를 덧붙이므로, 그 배열을 그대로 큐 항목에 물리면 복구 재인벤토리로 드러난
  // 항목의 계보에 **바로 뒤에 재생될 형제 조작**이 끼어든다(6차 실측 [… 시·군, 보성군,
  // 고흥군] 5건이 «재생 종점 상태 불일치»로 죽었다).
  test('B1 확장 경로 — 재생 중 늘어나는 배열을 큐 항목이 붙들지 않는다', () => {
    const ctx = { pure, targets: {}, limits: { maxSteps: 100, maxDepth: 24, maxMinutes: 90 } };
    const run = newRun();
    const target = {
      role: '', name: '고흥군', input_type: '', owner: 'menu', owner_items_hash: '',
      dom_path: 'div:nth-of-type(1)', kind: 'menuitem', declared: false, found_by: ['semantic'], live: false,
    };
    const snapshot = {
      state_hash: 'H',
      inventory: {
        entries: [{
          id: 'goheung', role: '', name: '고흥군', input_type: '', owner: 'menu', enabled: true,
          occluded: false, checked: null, face: null, value_empty: null, surface: null, live: false,
        }],
        targets: { goheung: target },
      },
    };
    // reachState가 재생에 쓰는 배열 — replayOperation이 돌아온 뒤 그 op가 덧붙는다.
    const applied = [{ target: 'sigungu', action: 'click', option: null }];
    acceptState(ctx, run, snapshot, 1, applied);
    applied.push({ target: 'boseong', action: 'click', option: null });

    assert.equal(run.queue.length, 1);
    assert.deepEqual(run.queue[0].ops.map((op) => op.target), ['sigungu'],
      '복구 재인벤토리로 드러난 항목이 형제 항목 click 뒤 경로를 들었다');
  });

  // O1 — "②b: 대상 kind input·textarea·select이고 항목 context의 value_empty === true인
  // fill/select 항목을 ②(트리거 새 context) 뒤·③ 앞에"(진행 조건 우선).
  test('②b 빈 입력 fill — 이미 실행된 단위끼리는 진행 조건이 먼저다(O1)', () => {
    const ctx = ctxWith({ name: { kind: 'input' }, next: { kind: 'button' } });
    const run = newRun();
    run.executedUnits.add(JSON.stringify(['name', 'fill', null]));
    run.executedUnits.add(JSON.stringify(['next', 'click', null]));
    // 문서 순서상 «다음»이 뒤에 들어와 ⑥(늦게 들어온 항목)을 쥔다 — ②b가 없으면 그쪽이 이긴다.
    run.queue.push(queueItem({ target: 'name', action: 'fill', prefixHash: 'S', context: 'r', valueEmpty: true }),
      queueItem({ target: 'next', prefixHash: 'S', context: 'r' }));
    assert.equal(takeNext(ctx, run).target, 'name', '빈 입력 fill이 얕은 재실행에 밀렸다');

    // 대조군 — 값이 이미 차 있으면(value_empty=false) ②b가 없고 ⑥이 그대로 이긴다.
    const filled = newRun();
    filled.executedUnits.add(JSON.stringify(['name', 'fill', null]));
    filled.executedUnits.add(JSON.stringify(['next', 'click', null]));
    filled.queue.push(queueItem({ target: 'name', action: 'fill', prefixHash: 'S', context: 'r', valueEmpty: false }),
      queueItem({ target: 'next', prefixHash: 'S', context: 'r' }));
    assert.equal(takeNext(ctx, filled).target, 'next');

    // ②(트리거의 새 context)는 ②b보다 앞이다 — 순위 칸이 ②와 ③ 사이에 들어갔는지 고정한다.
    const both = newRun();
    both.executedUnits.add(JSON.stringify(['name', 'fill', null]));
    both.executedUnits.add(JSON.stringify(['trg', 'click', null]));
    both.queue.push(queueItem({ target: 'name', action: 'fill', prefixHash: 'S', context: 'r', valueEmpty: true }),
      queueItem({ target: 'trg', prefixHash: 'S', context: 'r', priorFace: '가' }));
    assert.equal(takeNext(ctxWith({ name: { kind: 'input' }, trg: { kind: 'trigger' } }), both).target, 'trg');
  });

  test('③ 재생 불필요 — 계보가 다르면 «무료»가 아니다(D-G 정합)', () => {
    // 같은 접두 해시를 요구하는 두 항목: 얕지만 계보가 달라 어차피 재생될 항목 vs
    // 깊지만 지금 페이지 그대로인 항목. 해시만 보면 ⑤(짧은 경로)가 재생 쪽을 택한다(리뷰 I-1).
    const ctx = ctxWith({ shallow: { kind: 'button' }, deep: { kind: 'button' } });
    const run = newRun({ currentPath: ['a', 'b'] });
    const replayItem = queueItem({ target: 'shallow', prefixHash: 'S', ops: [{ target: 'z' }] });
    const freeItem = queueItem({ target: 'deep', prefixHash: 'S', ops: [{ target: 'a' }, { target: 'b' }] });
    run.queue.push(replayItem, freeItem);

    assert.equal(takeNext(ctx, run).target, 'deep', '재생될 항목이 무료 항목을 이겼다');
    assert.equal(run.sameStateRun, 1);
    assert.deepEqual(run.lastPrefixHash, 'S');
  });

  test('② 트리거의 새 priorFace — 발견(hover) step은 그 카운터를 올리지 않는다(4b-I1)', () => {
    const ctx = ctxWith({ trg: { kind: 'trigger' }, plain: { kind: 'button' } });
    const run = newRun();
    run.executedUnits.add(JSON.stringify(['trg', 'click', null]));
    run.executedUnits.add(JSON.stringify(['plain', 'click', null]));

    // hover 발견 step이 실행됐다 — 필요 조작이 아니므로 ②(face)·④(상태별 실행 수)에 들어가면 안 된다.
    const hoverItem = { ...queueItem({ target: 'trg', prefixHash: 'S', priorFace: '가' }), action: 'hover', discovery: true };
    recordStep(run, hoverItem, 1, { status: 'executed', error: null, before: { inventory: [], state_hash: 'S' }, after: null });
    assert.equal(run.executedFaces.has('trg'), false, 'hover가 ② 카운터를 올렸다');
    assert.equal(run.executedByState.get('S'), undefined, 'hover가 ④ 카운터를 올렸다');

    // 그래서 같은 face의 트리거 클릭은 ②를 그대로 갖고, 얕고 무료인 항목보다 먼저 꺼내진다.
    const triggerItem = queueItem({ target: 'trg', prefixHash: 'S', ops: [{ target: 'a' }], priorFace: '가', context: 'c2' });
    const plainItem = queueItem({ target: 'plain', prefixHash: 'S', ops: [], context: 'c3' });
    run.currentPath = [];
    run.queue.push(triggerItem, plainItem);
    assert.equal(takeNext(ctx, run).target, 'trg', '트리거의 새 priorFace가 ②를 잃었다');

    // 대조군 — 그 face가 실제 실행으로 기록되면 ②를 잃고 얕은 항목이 이긴다.
    const after = newRun();
    after.executedUnits.add(JSON.stringify(['trg', 'click', null]));
    after.executedUnits.add(JSON.stringify(['plain', 'click', null]));
    noteExecuted(after, { target: 'trg', action: 'click', priorFace: '가' }, 'S');
    after.queue.push(queueItem({ target: 'trg', prefixHash: 'S', ops: [{ target: 'a' }], priorFace: '가', context: 'c2' }),
      queueItem({ target: 'plain', prefixHash: 'S', ops: [], context: 'c3' }));
    assert.equal(takeNext(ctx, after).target, 'plain');
  });

  test('③ 연속 카운터 — 재개 복원도 발견 step을 세지 않는다(리뷰 I-3)', () => {
    const ctx = ctxWith({ a: { kind: 'button' }, b: { kind: 'button' } });
    const live = newRun();
    // 라이브: 큐에서 꺼낸 항목만 센다(hover는 takeNext를 거치지 않는다).
    for (const target of ['a', 'b']) {
      live.queue.push(queueItem({ target, prefixHash: 'S', context: target }));
      takeNext(ctx, live);
    }
    const restored = newRun();
    restoreVisited({ ...ctx, prior: { initialHash: 'S' } }, restored, [
      { target: 'a', action: 'click', option: null, context: 'a', status: 'executed', discovery: false,
        path: ['a'], before: { inventory: [], state_hash: 'S' }, after: { inventory: [], state_hash: 'S' } },
      { target: 'h', action: 'hover', option: null, context: 'h', status: 'executed', discovery: true,
        path: ['h'], before: { inventory: [], state_hash: 'S' }, after: { inventory: [], state_hash: 'S' } },
      { target: 'b', action: 'click', option: null, context: 'b', status: 'executed', discovery: false,
        path: ['b'], before: { inventory: [], state_hash: 'S' }, after: { inventory: [], state_hash: 'S' } },
    ]);
    assert.equal(restored.sameStateRun, live.sameStateRun, '재개 복원이 hover step까지 세어 라이브와 어긋난다');
    assert.equal(restored.lastPrefixHash, live.lastPrefixHash);
    // 발견 step은 단위·② 카운터에도 들어가지 않는다.
    assert.equal(restored.executedUnits.has(JSON.stringify(['h', 'hover', null])), false);
    assert.equal(restored.executedFaces.has('h'), false);
  });

  test('재개 복원 — «페이지가 닫혔다» 접두를 뗀 사유로 ①(before) 갈래를 가른다(4d 재리뷰 Minor 2)', () => {
    const ctx = ctxWith({ a: { kind: 'button' } });
    // 목록 안 사유(«현재 상태에 없음»)가 닫힌 페이지와 함께 나면 접두가 붙는다 — 그래도 재생을 지나
    // 그 상태에 선 채 난 실패이므로 항목의 prefixHash는 부모 after(S)가 아니라 before(B)다.
    const step = (error) => ({
      target: 'a', action: 'click', option: null, context: 'a', status: 'unreachable', discovery: false,
      error, path: ['a'], before: { inventory: [], state_hash: 'B' }, after: null,
    });
    const closed = newRun();
    restoreVisited({ ...ctx, prior: { initialHash: 'S' } }, closed, [step('페이지가 닫혔다: 현재 상태에 없음: a')]);
    const plain = newRun();
    restoreVisited({ ...ctx, prior: { initialHash: 'S' } }, plain, [step('현재 상태에 없음: a')]);
    assert.equal(plain.lastPrefixHash, 'B');
    assert.equal(closed.lastPrefixHash, plain.lastPrefixHash, '접두 때문에 ②(부모 after) 갈래로 샜다');
    // 닫힌 단위는 한 번 다시 시도한다 — 그 계약은 그대로다.
    assert.equal(closed.seen.size, 0);
    assert.equal(plain.seen.size, 1);
  });

  test('②b 빈 입력 우선 — identity의 fill 실행 수가 2부터는 적용되지 않는다(D-K)', () => {
    const ctx = ctxWith({ name: { kind: 'input' }, next: { kind: 'button' } });
    for (const [fills, expected] of [[0, 'name'], [1, 'name'], [2, 'next'], [3, 'next']]) {
      const run = newRun();
      run.executedUnits.add(unitKeyOf('name', 'fill'));
      run.executedUnits.add(unitKeyOf('next'));
      run.fillRuns.set('name', fills);
      // ③④⑤는 동률이다 — ②b가 가르지 않으면 ⑥으로 «다음»(나중 항목)이 이긴다.
      run.queue.push(queueItem({ target: 'name', action: 'fill', prefixHash: 'S', context: 'r', valueEmpty: true }),
        queueItem({ target: 'next', prefixHash: 'S', context: 'r' }));
      assert.equal(takeNext(ctx, run).target, expected, `fill ${fills}회 뒤`);
    }
  });

  test('재개 복원 — D-K 카운터(identity별 fill 실행 수)를 steps에서 되살린다', () => {
    const ctx = ctxWith({ name: { kind: 'input' }, a: { kind: 'button' }, h: { kind: 'button' } });
    const executed = (target, action, discovery = false) => ({
      target, action, option: null, context: target, status: 'executed', discovery,
      path: [target], before: { inventory: [], state_hash: 'S' }, after: { inventory: [], state_hash: 'S' },
    });
    const restored = newRun();
    restoreVisited({ ...ctx, prior: { initialHash: 'S' } }, restored, [
      executed('name', 'fill'), executed('a', 'click'), executed('name', 'fill'),
      executed('h', 'hover', true), // 발견 step은 세지 않는다
      { ...executed('a', 'click'), status: 'failed' }, // executed가 아니면 세지 않는다
    ]);
    assert.equal(restored.fillRuns.get('name'), 2);
    assert.equal(restored.fillRuns.has('a'), false);
    assert.equal(restored.fillRuns.has('h'), false);

    // 라이브 recordStep과 같은 값이다 — 슬라이스 경계에서 ②b 상한이 갈리지 않는다.
    const live = newRun();
    const item = (target, action) => ({ ...queueItem({ target, action, prefixHash: 'S', context: target }) });
    for (const [target, action] of [['name', 'fill'], ['a', 'click'], ['name', 'fill']]) {
      recordStep(live, item(target, action), live.stepNo + 1,
        { status: 'executed', error: null, before: { inventory: [], state_hash: 'S' }, after: { inventory: [], state_hash: 'S' } });
    }
    assert.deepEqual([...live.fillRuns], [...restored.fillRuns]);
  });
});
