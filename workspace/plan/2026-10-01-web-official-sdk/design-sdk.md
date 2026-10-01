결론(v3.3 동결 · 2026-10-01): 설계를 v3.3 으로 동결한다. 검토 열두 건(v1 적대 검토 둘 · v2·v3·v3.1·v3.2 닫힘 확인 각 둘 · v3.3 최종 확인 둘)을 모두 받았고, 최종 확인은 두 검토 모두 설계 막힘 없음(blocker·major 0)이다. 남은 minor·nit 여섯 건은 구현자가 반드시 처리할 목록으로 §16 에 옮겼다. 반박한 지적은 없고, 사용자에게 물을 쟁점도 없다. v3.1·v3.2 닫힘 확인은 두 검토 모두 «닫힘»(새 blocker·major 0)이었고, v3.2·v3.3 은 남은 minor·nit 을 반영했다. **① 승인 범위**: 승인은 이름공간 묶음 단위로 묻는다(사용자 결정 «G1 에서 한 줄로 다시 묻기»). v3.2 는 목록에 함수 분류표를 두고 승인에 묶는다. 묶음은 호출형·수명 함수만 덮는다. 사용자 자료를 운영자 저장소로 보내는 함수(`uploadImage` 류 — 카카오가 100일 보관)는 이름을 적어 G1 에서 따로 묻는다. 경로를 인자로 받는 범용 함수(`Kakao.API.request` — 친구 메시지 발송·업로드·연결 끊기를 포함한 경로 30개)는 다섯째 종류 `gateway` 로 두어, 경로마다 이름을 적고 묻는다(6-3-13 은 `Share` 만 써서 영향이 없다). SDK 가 그리는 단추는 WV9 가 늘 막는다. G2 스니펫은 `cleanup` 같은 수명 함수를 그대로 두어 «호출 1회» 판정이 흔들리지 않게 했다. 표에 없는 함수와 파일 인자도 대조한다(실제 카카오 2.8.3 으로 확인). **② 발송 누출**: 운영자 호스트는 컨텍스트 단위로 막고(팝업 포함), 운영자 폼·`window.open` 은 기록만 한다. 실제 Chromium 에서 운영자 요청 0 · 팝업 0 이다. **③ 늘 검사**: 등재 id 디렉터리·그 참조·표지만 늘 본다. 목록에 없는 벤더 사본은 지금 바이트가 «목록 시대»에 처음 생겼는지로 가른다(생겼으면 WV13 · 아니면 이관 빚 WV12). v3.2 는 이 판정을 git 한 번 걸음으로 바꾸고, 목록 이력이 없으면 걸음 자체를 건너뛴다(미등재 파일 200개: 11.5 s → 0.13 s). 목록에서 빠진 등재 바이트의 사본은 어디에 있든 WV13 이다. 얕은 이력에서는 판정하지 않고 멈춘다(미실행 exit 1). 목록 이전 사본 가지를 rebase·squash 로 합치면 WV13 이 되므로, merge 로 착륙하라고 알린다. **④ 외부 코드·주소**: WV8 은 리터럴마다 이스케이프를 푼 뒤 본다. 같은 출처 웹소켓 조립·`startsWith('https://')`·CSS 선택자·점 찍은 키 오탐을 없앴고, `createElementNS(…, 'script')`·`srcdoc` 대입·`document.write` 싱크를 더했다. 정적 덫이 못 잡는 몫은 모든 레인에서 discipline-reviewer-web 이 맡는다. SDK 레인에서는 G2 «프로젝트 JS 가 시작한 외부 요청 0»(CDP 시작 스택으로 귀속)이 더해진다. spring_dream 전수(main·가지 머리 8·워크트리 8)에서 WV8 적중은 기존 `createElement("script")` 2줄뿐이고 WP3 는 0 이다. **⑤ 승인 출처**: 대리 원문은 HEAD 조상 커밋에 있어야 하고, `web/`·`.dddjango-web/` 밖이어야 하며, 그 행의 원바이트 해시로 묶인다. NFC 는 공용 함수 없이 자리마다 정규화한다. 경로는 원문으로 기록하고 조회만 NFC 로 한다. **⑥ 6-3-13** 의 품질 기본값은 «릴리즈 뒤 등재 경로로만»이다. 처분은 §14·§15 에 있다.

> **사용자 결정(2026-10-01 14시대 · §13)**: «G1 에서 한 줄로 다시 묻기 (권장)» — 승인된 SDK 의 `use_scope` 밖 기능을 다음 레인이 쓰면 G1 에서 한 줄로 다시 승인받는다(파일은 재사용). (발주 기록 · 원문 그대로)


# dddjango-web 공식 플랫폼 SDK 개방 · 프로젝트 1회 등록 — 설계 (v3.3 동결 · 2026-10-01)

- 입력
  - 현장 보고 F4-38(`workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md` 131–147 · 읽기만)
  - 사용자 결정(구속):
    - «공식 SDK 개방 + 처음 한 번 등록» · «공식 SDK 만» · 프레임워크·일반 라이브러리 금지
    - «설계는 지금 병행» — 구현은 web 1순위 속도 커밋 뒤, 릴리즈는 속도 배치와 함께
    - «퀄리티는 양보할 수 없다»
  - 적대 검토 v1: scratch `review-sdk-tool/review.md`(탐침 `wv_proto.py` · `run_probes*.py` · `kakao_probe.js` · `probes*.out`) · `review-sdk-rules/review.md`(`anchors.py`). 처분은 §14 다.
  - v2 실측: scratch `design-sdk/probe/intercept_probe.js` · `intercept_probe.out`(실제 카카오 2.8.3 · node shim · 네트워크 0) · `design-sdk/facts.md`
  - 닫힘 확인 v2: scratch `review-sdk-rules/closure-v2.md`(`anchors_v2.py`) · `review-sdk-tool/closure-v2.md`(`v2_probes.py`·`kakao_probe2.js`). 처분은 §15 다.
  - v3 실측(scratch 전용 · 저장소 무변): `design-sdk/probe/kakao_probe3.js`·`kakao_probe3.out`(검토 `kakao_probe2.js` + v3 폼 래퍼) · `design-sdk/browser/`(`page.html`·`feature.js`·`sdk_boundary.js` 시제품·`run.js`·`run.out` — 실제 Chromium headless shell 1234 · playwright-core 1.64 · 로컬 http 서버 · 운영자 호스트는 모든 경우 `context.route` 에서 abort)
  - 닫힘 확인 v3: scratch `review-sdk-rules/closure-v3.md` · `review-sdk-tool/closure-v3.md`(`v3_probes.py`). 처분은 §15-3·§15-4 다. v3.1 실측은 `design-sdk/v31/`·`design-sdk/wp3/`·`design-sdk/browser/run2·run3` 이다.
  - 닫힘 확인 v3.1(두 검토 모두 «닫힘» · 새 blocker·major 0 · 남은 minor·nit): scratch `review-sdk-rules/closure-v31.md`(`wv8/scan.py`) · `review-sdk-tool/closure-v31.md`(`v31_probes.*`·`sd_scan*.out`·`wp3_v31_mine.out`·`wv8_v31_mine.out`·`browser-v31/`). 처분은 §15-5 다.
  - v3.2 실측(scratch 전용 · 저장소 무변): `design-sdk/v32/` — `v32_probes.py`·`.out`(검토자 `v31_probes.py` 시나리오를 v3.2 판정으로) · `wv8_v32.py`·`.out`(WV8 표본 27 · spring_dream 가지 머리 9 · 워크트리 8 · WP3 같은 범위) · `wv8_rules_scan_main.out`(규범 검토자 `wv8/scan.py` 그대로) · `browser/run4.*`(함수 분류 · 실제 카카오 2.8.3) · `browser/run5.*`(외부 요청 귀속 · CDP initiator)
  - 닫힘 확인 v3.2(두 검토 모두 «닫힘» · 새 minor 2 · nit): scratch `review-sdk-rules/closure-v32.md` · `review-sdk-tool/closure-v32.md`(`v32_probes.*` · `wv8_v32_mine.*` · `ns_script_check.*` · `sink_check.*`). 처분은 §15-6 이다.
  - 최종 확인 v3.3(두 검토 모두 «설계 막힘 없음»): scratch `review-sdk-rules/closure-v33.md` · `review-sdk-tool/closure-v33.md`(`v33_probes.*` · `wv8_v33_mine.*`). 남은 항목은 §16 구현 단계 메모다.
  - v3.3 실측(scratch 전용 · 저장소 무변): `design-sdk/v33/` — `v33_probes.py`·`.out`(검토자 `v32_probes.py` 시나리오를 v3.3 판정으로) · `wv8_v33.py`·`.out`(WV8 표본 47 · spring_dream 전수) · `floors.py`·`.out`(이름·경로 바닥 · 실제 카카오 2.8.3) · `browser/run5.*`(같은 출처 script 귀속 추가) · `browser/run6.*`(gateway 경로 대조)
  - NFC 판형: `workspace/plan/2026-09-26-refactor-path-repair/diag-R8f-nfc.md`(«쓰기는 NFC · 비교는 정규화 뒤 · 옛 기록 이관 없음»)
- 기준: HEAD `86fc3c24`(미릴리즈 · 현장 1.1.25).
  - 1순위 web W1~W4(`design-tier1.md` v3 · 묶음 W8e)와 W6m(`design-W5-7.md` v3)이 같은 Coordinator 문단을 먼저 고친다. `design-W8.md`(v1 → v2 개정 중 · 이 설계는 고치지 않는다)는 3-1 과 `CL:222` 를 고친다.
  - 편집은 **인용한 문장(앵커)** 으로 찾는다. A1~A26 은 HEAD 의 CL·CX 와 W8e 워크트리(`.claude/worktrees/agent-afbf6bda4bd10a725`)의 CL·CX, 네 파일 모두에 정확히 1회씩 있다 [실측 · 검토 `anchors.py`·`anchors_v2.py`].
- 표기
  - `CL` = `dddjango-web/commands/dddjango-web.md` · `CX` = `codex-dddjango-web/skills/dddjango-web/SKILL.md`
  - `HR` = discipline-web-houserules `references/final.md` · `IU` = implementation-ui `references/final.md` · `IJ` = implementation-javascript `references/final.md` · `AW` = architecture-web `references/final.md`
  - **[실측]** = 이번에 파일·git·네트워크·실행으로 확인 · **[추정]** = 실측의 해석
  - 앵커 id 는 **A1~A26**(v1 의 K1~K20 → A1~A20 · 새 A21~A26), 픽스처 id 는 **K·D·R**(검토 문서의 K19~K39·D36~D38 번호 그대로)

## 0. 쉬운 말 요약 — 지금 → 바꾸면 → 품질 안전장치

| 무엇 | 지금 | 바꾸면 | 품질 안전장치 |
|---|---|---|---|
| 카카오 같은 플랫폼의 공식 도구 | 어디에 두어도 검사가 막는다 | 그 회사가 직접 배포하고 자기 서비스를 부르는 도구만, 처음 한 번 사용자가 승인하면 들인다 | 회사 공식 문서 쪽을 도구가 직접 내려받아, 거기 적힌 주소·지문과 맞는 파일만 받는다. 라이브러리 배포용 공용 주소(cdnjs·jsdelivr·구글 라이브러리 경로 등)는 회사 주소여도 받지 않는다. 그 파일이 실제로 회사 서비스 주소를 부르는지도(주석 말고 코드에서) 본다 |
| 승인 기록 | 없다 | 프로젝트 안 목록 파일에 도구가 적는다. 승인은 그 항목 전체(판·지문·주소·쓰는 기능·키 이름…)에 묶인다 | 한 글자라도 바뀌면 승인이 저절로 무효다. 목록을 손으로 고쳐도, 같은 이름을 두 번 적어도, 글자 꼴(NFC/NFD)이 달라도 검사가 막는다 |
| 누가 승인하나 | — | 사용자가 G1 에서 직접 답하거나, 사용자가 판(또는 승인 화면의 표지)을 담아 남긴 글 | 옛 결정 줄·버린 가지의 글·화면 코드 폴더 안 글은 출처가 아니다. 판을 올릴 때는 새 판을 적은 새 글이 필요하다 |
| 다음 작업들 | 매번 막힌다 | 승인된 도구·승인된 기능 묶음(예: 공유)은 묻지 않고 쓴다. 새 기능 묶음(예: 로그인)은 G1 에서 한 줄로 다시 묻는다. 요청에 이미 «카카오 로그인»이라고 썼으면 그 글을 승인으로 받고 묻지 않는다 | 매 실행마다 등록된 파일·목록·그 파일을 부르는 화면 참조를 기계가 다시 확인한다 |
| 등록된 도구가 어긋나면 | — | 모든 작업의 완성 단계가 멈춘다 | 승인 없이 되돌릴 수 있는 것(원본 바이트 복원·아무도 안 쓰는 파일 정리)은 어느 작업이든 언제든 고치고, 아니면 정해진 입구로 안내한다 |
| 목록을 지우거나 항목을 빼거나 폴더 이름을 바꿔서 검사를 피하려 하면 | — | 막는다 | 목록이 한 번이라도 생긴 뒤에 새로 생긴 도구 파일 내용이 등록 밖에 있으면, 목록이 지워졌어도·폴더 이름이 바뀌었어도 늘 검사한다(목록이 생기기 전부터 있던 사본만 «등록 전»으로 본다) |
| 목록이 생기기 전부터 있던 등록 안 된 도구 파일(6-3-13 임시 사본 · 평면 `vendor/kakao.min.js` 포함) | — | 그 파일·폴더만 «등록 전»으로 다룬다(그 가지를 merge 로 합칠 때 — rebase·squash 로 합치면 «목록이 생긴 뒤 새로 생긴 것»이 되어 늘 막힌다). 등록된 다른 도구가 있어도 그것 때문에 모두가 막히지는 않는다. 새 파일·새 로드 줄은 막고, 모든 작업의 첫 화면에 «등록 입구» 한 줄을 띄운다 | **단 그 사본이 main 에 들어오면, main 을 받는 작업들은 등록이 끝날 때까지 완성 단계가 막힌다**(받은 파일을 «이번에 들인 것»으로 보기 때문). 그래서 6-3-13 은 이 판 릴리즈 뒤 정식 등록 경로로만 시작하는 것을 기본으로 한다 |
| 같은 기능 묶음 안의 «사용자 자료 올리기» | — | 공유 묶음을 승인해도 사용자 사진을 카카오 서버에 올리는 기능은 들지 않는다. 쓰려면 그 기능 이름으로 G1 에서 한 줄 다시 묻는다(카카오가 보관한다는 사실을 함께 보인다). 주소(경로)를 받아 카카오의 아무 기능이나 부르는 범용 함수(`API.request`)는 경로마다 따로 묻는다. 한 요청이 여럿을 들이면 한 번에 묻는다. SDK 가 그리는 단추는 어떤 승인으로도 쓰지 않는다 | 목록에 함수마다 종류(호출·수명·자료 올리기·SDK 단추)를 적고 승인에 묶는다. 이름으로 올리기·단추 함수를 기계가 먼저 가른다. 완성 확인 때 실제 함수 목록과 파일 인자로 다시 맞춰 본다 |
| 화면에서 부르는 곳 · 키 | — | 기능 JS 한 곳에서만, 키는 서버 설정 값에서만 | 템플릿의 `javascript:` 링크(조각으로 이어 붙인 것 포함)·`srcdoc`·SVG 애니메이션 링크, 기능 JS 안의 외부 주소 문자열·외부 스크립트 끌어오기도 이제 검사가 막는다 |
| 완성 확인(G2) | — | 실제로 보내지 않는다. 도구가 보낼 내용을 가로채 명세와 맞춰 본다 | 카카오 쪽 주소만 막고 우리 그림 주소(CDN)는 그대로 둔다. 새 창(팝업)·숨은 폼까지 막고 기록한다(실제 브라우저로 확인). 막을 장치가 없으면 «미검증»으로 적는다. 우리 기능 JS 가 프로젝트 밖으로 낸 스크립트·자료 요청은 발견으로 센다(템플릿 태그·다른 회사 스크립트·사용자가 누른 링크는 기록만) |

## 1. 전제 — 확인한 사실

1. **막힘의 자리** [실측 HEAD]
   - 규범: `HR:163`·`HR:168`.
   - WP1 은 added 파일만 본다(`check_purity.py:154`). WP2 는 바뀐 태그 줄만 본다(`:216-220`). WS6 은 added 파일·디렉터리만 본다(`check_structure.py:101-130`).
   - 시안 증거 검사(`backstop.py:281-312`)는 `--only` 와 무관하게 돈다.
2. **diff 게이트와 설치 시점** [실측 검토 P13·P14·K9]
   - Phase 2 진입 ②″ 의 설치 커밋은 ⑥ `git_snapshot` 보다 앞이다. 그래서 설치한 레인의 G2 에서도 벤더 파일은 added 가 아니다.
   - 벤더 불변식을 diff 게이트 검사(WS6·WP1·WP2)로 지키면 비등재·변조 사본이 G2 를 green 으로 통과한다.
3. **git 이 저장하는 바이트 ≠ 작업 트리 바이트** [실측 검토 P1~P6]: 심볼릭 링크(파일·디렉터리), `text=auto`·`eol=crlf`, clean 필터, 대소문자 무시 FS 에서 작업 트리 해시는 통과하지만 clone·배포 바이트는 다르다.
4. **카카오 2.8.3** [실측]
   - 87,110 B · sha256 `b2ff7b30deff3757ee5836c3a64016d6cd815b80d9b7ebffb2c4338d6bc5f7e0`.
   - 공개 sha384 `oroumrnF…kHDS5CR7tu20eGiOU6GkTpy` 는 다운로드 문서 원문(서버 렌더 HTML)에 원본 경로와 함께 실재한다.
   - Apache-2.0 이다.
   - init 이 만드는 이름공간은 `API·Auth·Cert·Channel·Navi·Picker·Share` 다(`this.<X>=` 정적 추출). API 경로에는 `/v2/user/me`·`/v1/api/talk/friends/message/default/send`·`/v2/api/talk/message/image/upload` 등 28개가 있다. https 호스트는 16개이고(카카오 12 · 그 밖 `github.com`·`itunes.apple.com`·`openjsf.org`·`www.apache.org`), 액세스 토큰은 `sessionStorage` 에 둔다.
   - 로드 직후 `Kakao` 키는 `VERSION,cleanup,init,isInAppBrowser,isInitialized` 다. **`Share` 는 `init` 안에서 대입**된다. 로드·init 은 네트워크 요청 0 이다. 두 번째 `init` 은 «Already initialized» 를 던진다.
   - 잘못된 인자는 `KakaoError` 로 동기에 던진다(`Missing required keys: content`).
   - 데스크톱 경로의 실물 `sendDefault` 는 `window.open("https://sharer.kakao.com/picker/link")` 뒤 폼을 제출한다.
   - 출처: `facts.md` · `intercept_probe.out` · 검토 `kakao_probe.js`.
5. **spring_dream** [실측 · 읽기만]
   - 발주서 개정 2c 가 «이번 요청만 임시 허용»을 말한다. 카카오 SDK 결정 줄은 `b6f0ef25b` 기준 `:74`(2026-09-28 21:59:32 «가»)다. `:75` 는 «공유 그림 = 서버» 줄이다.
   - `KAKAO_JAVASCRIPT_KEY` 는 `env/.env.sample:55` 에만 있고 settings 에는 없다.
   - `local.py`·`dev.py`·`prod.py` 가 `STORAGES = _base.s3_storages()` 라 **web 그림은 로컬에서도 CloudFront 주소**로 나간다(`base.py:183-188`).
   - CSP 는 0 이다. 진행 중 레인은 7개다(규범 검토 B1).
6. **1.1.25 에서 임시 허용의 실제**(규범 검토 M8 [실측 설치본]): 사본을 어디에 두어도 G2 백스톱은 exit 2 다. 1.1.25 Coordinator 에는 «승인된 편차»를 받는 장치가 없다. main 병합 뒤 그 main 을 받는 다른 레인의 G2 에도 WP1(+WS6)·WP2 가 뜬다.
7. **W8**(`design-W8.md` v1): 커밋 ②가 3-1(`CL:218-219`)·새 3-2·`CL:222`(G2 배너 — 한 물리 줄 · verify-web 문단 byte 대조)를 고친다. `asset_digests.js` 로 그림 바이트 지문을 잰다. 릴리즈는 커밋 ②·③ 뒤에 각각 한다.
8. **릴리즈 배선** [실측 검토 m11]: `make release-web` 의 `_release` 는 `make verify` 만 돈다. `verify-web` 은 자동 경로 밖이다. `manifest_seal.py` 는 web 스크립트가 아니라 Makefile 을 봉인한다.
9. **카카오 발송 경로 — 실제 브라우저** [실측 v3 `design-sdk/browser/run.out` · Chromium headless shell 1234]
   - E0: SDK 를 막은 첫 화면과 불러온 첫 화면이 같다(노드 10 · 스타일시트 0 · iframe 0). 로드·활성화 init 의 요청은 0 이다.
   - E1(가로채기 없음 · 클릭): 실물 `sendDefault` 가 팝업 1개를 열고, `POST https://sharer.kakao.com/picker/link` 가 **내비게이션 요청**으로 나간다. 같은 페이지에 건 `page.route` 기록은 0 이고, `context.route` 기록이 1 이다(거기서 abort — 실제로 나가지 않음). 그래서 `page.route` 만 쓰면 이 요청이 새어 나간다(검토 규범 N1 · 검사기 N4 확인).
   - E2(v3 스니펫 · 클릭): 기록기 1회 · `userActivation` 참 · 팝업 0 · 운영자 요청 0.
   - E3(v3 스니펫 · 기록된 인자로 실물 1회 = 인자 검증): 예외 0(«real ok») · `window.open(sharer, "sharer")` 기록 1 · 폼 제출 기록 1(`action=https://sharer.kakao.com/picker/link` · `target=sharer` · `method=post` · 필드 `app_key·ka·validation_action·validation_params`) · 팝업 0 · 운영자 요청 0.
   - E4(제품이 옛 참조를 쥔 경우 · v3 스니펫): 기록기 0(case 실패로 드러남) · 폼·`window.open` 기록 1 · 운영자 요청 0.
   - node 확인: 검토 `kakao_probe2.js` 에 폼 래퍼만 더한 `kakao_probe3.out` — A·B 기록기 1, CAP·VERIFY 는 폼 기록 1 · 실제 제출 0.
10. **v2 경계의 구멍** [실측 검토 `v2_probes.out`]
    - 병합 경합: 깨끗한 레인의 `install` 과 미등재 사본 레인이 충돌 없이 병합되면 v2 늘 검사(WV5·WV6)가 main 전체를 막는다.
    - 강등: 한 커밋으로 목록을 지우고 사본을 바꾸면 v2 는 «등재 전»으로 판정해 늘 검사를 건너뛴다(빌드 기록 없는 편집이면 WV10 도 notice).
    - `.DS_Store`(전역 무시)가 WV5·`install` 전제를 막는다. `check_design_evidence.py:25` 는 이미 이 파일을 뺀다.
11. **spring_dream 6-3-13**: `lane/6-3-13` 브랜치는 아직 없다(규범 닫힘 확인 [실측 `git branch -a`]). 그래서 «릴리즈 뒤 등재 경로로 시작»을 지금 고를 수 있다.
12. **v3.1 실측**(규범·검사기 v3 닫힘 확인 대응 · 모두 scratch)
    - WP3 ③: spring_dream main 의 URL 속성 216개(검토자 `url_attrs.txt`)에서 v3 문면은 오탐 4(전부 `{% url 'ns:name' %}`) · v3.1 «태그 밖 · 스킴 위치» 규칙은 0. 사례 13(차단 5 · 통과 8) 일치 · 검토자 WP3 표본 7(엔티티 콜론 2 · `?t=10:00` 포함) 놓침 0 · 오탐 0(`design-sdk/wp3/wp3_scheme.out` · `design-sdk/v31/v31_probes.out`).
    - 검토자 `v3_probes.py` 시나리오를 v3.1 판정(직속 파일 늘 제외 · «목록 시대» 내용 판정 · `--full-history`)으로 다시 돌렸다(검토자 폴더는 읽기만 · 작업 폴더는 `design-sdk/v31/work`): rebase 0/0/1 · 목록·항목 삭제 1/1 · 정상 remove·재채택 0/0/0 · **개명 우회 1(V3-3)** · **병합 해소 탈락 1(V3-2)** · **평면 사본 경합 늘 0 · WV12(V3-1)** · **같은 이름 등재 전 사본 WV12(nit 2)** — 모두 기대값이다.
    - WV8 v3.1 표본 9(조립 우회 2 · 스킴만 든 리터럴 짝 포함) 놓침 0 · 오탐 0. spring_dream main `web/static/js` 24개에 적용하면 발견 2 — `conversation.js` 의 `createElement("script")`(비실행 JSON 담기 · 기존 줄)뿐이고 스킴 비교 `["http:", "https:"]` 는 통과한다(`design-sdk/v31/wv8_springdream.out`). 기존 줄은 빚 스캔에서 미룰 수 있는 키다.
    - 실브라우저(`design-sdk/browser/run2.out`·`run3.out`): 늦은 초기화 init 감싸기 경로 · 라우트 해제 뒤 다음 case 정상 · 이름공간 단위 기록기.
13. **v3.2 실측**(v3.1 닫힘 확인 대응 · 모두 scratch `design-sdk/v32/`)
    - **WV12/WV13**: 검토자 `v31_probes.py` 시나리오를 v3.2 판정(단락 · `-m` 한 번 걸음 · 얕은 이력 판정 불가 · 이력상 등재 바이트 규칙)으로 다시 돌렸다(`v32_probes.out` · 검토자 폴더는 읽기만). 결과는 모두 기대값이다.
      - merge·평면 merge 는 WV12, rebase·squash·cherry-pick 은 WV13 이다(고지대로 — K50c).
      - 같은 바이트 복사는 WV12, 변조는 WV13 이다.
      - **기존 등록 SDK 의 개명(바이트 그대로)은 WV13** 이다(v3.1 은 WV12). 변조도 WV13 이다.
      - V3-3·V3-2 재현은 WV13 이다. 병합 해소에서만 생긴 내용도 `-m` 덕에 탄생이 보인다.
      - 얕은 클론 depth 1~3 은 «판정 불가», 전체 이력은 WV12 다.
      - K50 현장 꼴(목록 이전 임시 사본 = 나중 등재 바이트 · merge)은 평면·디렉터리 모두 WV12 다.
    - **비용**: 미등재 파일 200개에서 목록 이력이 없으면 0.05 s(단락 · 걸음 0), 있으면 0.13 s(한 번 걸음)다. v3.1 문면(파일마다 `--find-object`)은 같은 저장소에서 8.3 s · 11.5 s 였다. spring_dream main(커밋 5,357)에서 한 번 걸음(`git log --full-history -m --raw -- web/static/`)은 0.06 s, 목록 이력 조회는 0.055 s 다(검토자 실측: 파일 1개 `--find-object` 0.17 s).
    - **WV8**: v3.2 판정(이스케이프 해제 · 스킴만·`스킴://`·`스킴://${…}` 허용 · 도메인 강약 규칙 · 선택자 첫 라벨)으로 표본 27(검토자 13 · v3.1 9 · 새 짝·덫 5)이 어긋남 0 이다. 정적 놓침 1(조각 템플릿 `` `${'ht'}tps://…` `` fetch)은 G2 실행 확인의 몫이다(`wv8_v32.out`).
    - **spring_dream 전수**(읽기만): main·`b6f0ef25b`·레인 가지 머리 7(`git show`)과 레인 워크트리 8(미커밋 포함)에서 WV8 적중은 어디서나 `conversation.js` 의 `createElement("script")` 두 줄뿐이고 WP3 는 0 이다. 규범 검토자 `wv8/scan.py` 를 main 에 그대로 돌려도 같은 2건이다(`wv8_rules_scan_main.out`). 기능 JS 의 `fetch` 7곳은 모두 `sameOrigin(…)`·`credentials: "same-origin"` 으로 같은 출처만 부른다.
    - **함수 분류**(실제 카카오 2.8.3 · `browser/run4.out`)
      - `Share` 함수 10개 가운데 `cleanup` 은 원본 그대로 두었다(기록기 9).
      - 클릭 뒤 호출형 기록은 1이고, 제품이 `Share.cleanup()` 을 불러도 그대로다.
      - `uploadImage({file: FileList})` 는 data_out 으로 기록되고 파일 인자 표지가 참이다. `createDefaultButton` 은 sdk_ui 로 기록된다(발견).
      - 표에서 `scrapImage` 를 빼고 설치하면 «표에 없는 함수 Share.scrapImage»(발견)다. 운영자 요청 0 · 팝업 0.
      - 사본에는 세 저장 경로(`/v2/api/talk/message/image/upload`·`scrap`·`delete`)가 있다.
    - **외부 요청 귀속**(`browser/run5.out` — CDP `Network.requestWillBeSent`·`webSocketCreated` 의 initiator · 비동기 스택 없이)
      - 기능 JS 가 낸 외부 요청 8건은 시작 스택에 기능 JS 가 있다: fetch(이스케이프 주소 포함) · 조립 script · JS 가 만든 iframe · WebSocket · sendBeacon · 타이머 안 XHR · 프라미스 안 fetch · `debugger;` 뒤 fetch.
      - `setTimeout(fetch, 0, url)`·`.then(fetch)`·EventSource 3건은 시작 스택이 없다(initiator `other`).
      - 템플릿 태그(`parser`)·제3자 스크립트가 낸 요청·사용자가 누른 최상위 이동·팝업 2개는 기능 JS 몫이 아니다. 프로젝트 미디어 CDN 그림과 같은 출처 요청은 셈 밖이다.
      - `Debugger` 도메인(비동기 스택)을 켜면 기능 JS 의 `debugger;` 문에서 페이지가 멈췄다(클릭 30 s 시간 초과). 그래서 쓰지 않는다.
14. **v3.3 실측**(v3.2 닫힘 확인 대응 · 모두 scratch `design-sdk/v33/`)
    - **`Kakao.API`**: 사본의 정의는 `Or=Object.freeze({__proto__:null,request:xr})` 하나다. 실행 열거로는 `API` = {`cleanup`, `request`} 다. 사본의 API 경로 리터럴은 30개이고, 경로 바닥(§3-2)으로 data_out 16 · read 14 로 갈린다(`floors.out`). data_out 쪽에는 친구 메시지 발송 3 · 나에게 보내기 3 · 그림 올리기·지우기·긁어 오기 · 연결 끊기 · 가입 · 로그아웃 · 프로필 갱신 · 동의 철회 2 가 있다. 검토자 실측으로 `API.request` 가 닿는 경로는 28 이다.
    - **gateway 기록기**(`browser/run6.out` — 실제 카카오 2.8.3): `API.request({url: '/v2/user/me'})` 는 허용 경로라 `pathOk` 가 참이고, `'/v1/api/talk/friends/message/default/send'` 는 거짓(발견)이다. 운영자 요청은 0 이다. 분류표에 `API.cleanup` 을 적지 않고 설치하면 «표에 없는 함수»가 된다 — 완전성 대조가 함께 돈다.
    - **이름 바닥(camelCase 토큰)**: `Share` 10 함수는 v3.2 와 같게 갈린다. `request` 는 gateway 다. `restoreSession`·`inputValue`·`outputText`·`createLink` 는 `call`, `putObject`·`storeToken` 은 `data_out` 이다(`floors.out`). 부분 문자열 대조였다면 앞의 셋이 `data_out` 으로 올라갔을 것이다.
    - **WV8 싱크**(검토자 실측 `ns_script_check.out` · `sink_check.out`): `createElementNS(XHTML·SVG, 'script')`, iframe `srcdoc` 대입, 로드 뒤 `document.write` 가 실제 Chromium 에서 모두 실행된다. v3.3 판정(③ 를 `createElementNS` 둘째 인자에도 · ④ 에 `srcdoc` 대입·`document.write`·`writeln` · ② 약한 최상위는 URL 문맥에서만 · 문자열 이어 붙이기 접기 · 8진 이스케이프 · 템플릿 `${…}` 안 리터럴)으로 표본 47(v3.2 27 · 검토자 v3.2 추가 7 · 새 싱크·짝 13)이 어긋남 0 이다. 정적 놓침 1(조각 템플릿 fetch)은 R5 몫이고, 문면 한계 3(단독 약한 최상위 호스트 `'i.cdn.io'`·`'myapi.dev'`·`'cdn.socket.io'`)은 적었다(`wv8_v33.out`).
    - **spring_dream 전수**(읽기만): main·`b6f0ef25b`·레인 가지 머리 6·레인 워크트리 7(6-3-15 는 가지·워크트리가 사라졌다)에서 WV8 적중은 여전히 `conversation.js` `createElement("script")` 두 줄뿐이다. 새 싱크 적중은 0, WP3 는 0 이다(`wv8_v33.out`).
    - **같은 출처 script**(`browser/run5.out` b15): 기능 JS 가 `createElementNS(XHTML, 'script')` 로 미등재 vendor 사본(같은 출처)을 부르면, 시작 스택에 기능 JS 가 있는 `Script` 요청이 된다. 그래서 v3.3 실행 확인은 이것을 출처와 무관하게 발견으로 센다. `srcdoc` 안에서 파서가 부른 script 는 실행 확인에 보이지 않는다(b16). 그 몫은 정적 ④ 가 맡는다.
    - **WV12/WV13**(`v33_probes.out` — 검토자 `v32_probes.py` 시나리오 · 검토자 독립 구현 판정을 v3.3 판정으로 바꿔 끼움): 결과는 모두 기대값이다.
      - 받는 방식: merge·평면 WV12 · rebase/squash/pick WV13 · K50d 는 디렉터리·평면 모두 WV12
      - 같은 바이트: 복사 WV12 · 변조 WV13 · K48b WV13
      - **옛 임시 자리로 되돌려 개명 WV13**(v3.2 는 WV12)
      - 병합: 병합 안 변조 WV13 · 목록 이전 충돌 해소 사본 WV12 · 개명+변조 WV13
      - 얕은 클론 depth 1·3 «판정 불가(exit 1)» · full WV12
      - K51: 목록 없음 0.04 s(git 2회) · 있음 0.15 s(git 6회)
      - 마지막 `remove` 뒤 새 사본 WV13(의도 — §5-1)


## 2. «공식 SDK» 판정 기준

### 2-1. 자격 — 모두 만족해야 후보다

| id | 기준 | 기계 신호(도구·WV) | 사람 판단 |
|---|---|---|---|
| O1 | 배포자 = 그 서비스의 운영자 | — | 운영자 문서가 자기 SDK 로 소개하는가 |
| O2 | 원본 주소가 운영자 공식 도메인의 https 다. 공용 라이브러리 CDN 은 운영자 소유여도 안 된다 | `urlsplit` 호스트가 `operator_domains` 의 점 경계 하위 · userinfo/port/대문자/끝점/비ASCII 거절 · 리다이렉트 최종 URL 도 같은 조건 · **라이브러리 CDN 차단 목록**(아래)에 걸리면 거절(WV4) | 그 도메인이 정말 운영자 것인가 |
| O3 | **운영자 자기 문서 쪽이 그 원본을 인용**한다 | 도구가 `docs_url` 을 직접 내려받아 `docs.html`·sha256 을 남긴다. 원문에 원본 경로가 실재해야 한다(`evidence.cites_source=true` 필수). 같은 문서에 sha384 문자열이 실재할 때만 `upstream_integrity` 를 채운다(`integrity_from_docs`) | 인용 맥락이 «공식 배포»인가 |
| O4 | 라이선스·약관 | 칸 존재 · `license-header.txt` 보존 | 내용 수용 |
| O5 | 필요성: 서버·평범한 링크·native 로는 그 결과가 안 됨을 운영자 문서가 말한다 | `evidence.md` 인용이 저장한 문서 원문에 grep 으로 실재하는지(리뷰어) | 근거 판단 |
| O6 | 원본 그대로 한 파일 · 실행 중 다른 코드를 받지 않는다 | sha256·운영자 sha384 · 로더 표지 계수 · G2 외부 요청 기록 | — |
| O7 | 운영자 **자기 서비스 API** 의 클라이언트다 | `mask_js` 로 주석을 지운 **코드** 안의 https 호스트 가운데, `host(source_url)`·`host(docs_url)` 와 다른 운영자 호스트가 1개 이상 있다(WV4 · `origins.operator_in_code`) — 머리 주석·오류 문구의 홈페이지 주소는 세지 않는다 | 일반 라이브러리가 아닌가 |

- **라이브러리 CDN 차단 목록**(WV4 · 하드 거절):
  - 호스트: `cdnjs.cloudflare.com`·`cdn.jsdelivr.net`·`unpkg.com`·`code.jquery.com`·`cdn.skypack.dev`·`esm.sh`·`ga.jspm.io`·`cdn.statically.io`·`raw.githubusercontent.com`·`rawcdn.githack.com`·`*.github.io`
  - 경로: `/ajax/libs/` 를 포함한 경로
  - 공용 호스팅 접미사: `cloudfront.net`·`amazonaws.com`·`vercel.app`·`pages.dev`·`netlify.app`·`azureedge.net` 단독 `operator_domains`
- 이번 판의 범위 밖: SDK 가 우리 DOM 에 UI 를 그리는 기능 · ESM 전용 · 여러 파일 · SDK CSS(필요해지면 그때 개정).

### 2-2. 제외 범주

- UI 프레임워크·컴포넌트, 상태 계층, 일반 유틸리티, 화면 캡처·렌더(html2canvas·dom-to-image·html-to-image·modern-screenshot 류), 차트·시각화, 애니메이션, 폴리필·로더, htmx 와 그 확장, 비공식 래퍼.
- 운영자가 냈더라도 자기 서비스를 부르지 않으면 제외다.
- WV4 의 낱말 덫은 «영숫자 밖 문자로 자른 정확 토큰» + «구분자를 지운 결합형»(`html2canvas`·`domtoimage`·`htmltoimage`·`modernscreenshot`)으로 대조한다. 덫일 뿐 보증이 아니다. 부분열 대조는 `split→lit`·`d3` 해시·`revue→vue` 오탐 때문에 쓰지 않는다 [실측 P12].

### 2-3. 기계와 사람의 몫 — 순환을 끊는 법

- `operator_domains` 는 사람이 적는다. 그래서 «원본 ∈ operator_domains» 만으로는 순환이다(규범 M3).
- v2 는 세 가지 **운영자 쪽 증거**를 기계로 묶어 순환을 끊는다.
  - ① 운영자 문서를 도구가 직접 받는다.
  - ② 그 원문에 원본 경로가 실재한다(필수).
  - ③ 사본의 **주석 밖 코드**가 배포·문서 호스트와 다른 운영자 호스트를 부른다(O7 · 카카오는 12개 모두 코드 문자열 안 [실측 규범 닫힘 확인]).
- 여기에 라이브러리 CDN 하드 거절을 더한다. 그래서 `ajax.googleapis.com/ajax/libs/three.js` 류는 경로 차단과 O7 둘 다에서 떨어진다.
- 남는 것은 «그 도메인이 운영자 것인가»·O1·O5 의 사람 판단이다. 게이트 위임 실행에서는 이 승인 자체가 위임되지 않는다(§3-4).

## 3. 프로젝트 등재 목록(레지스트리)

### 3-1. 위치·형식 — `web/sdk_registry.json` · 정규 JSON

- 위치 근거
  - 다스리는 사본과 같은 트리·같은 커밋이라 병합·리베이스·soft-reset 을 내용으로 견딘다.
  - `static/` 밖이라 공개 서빙되지 않는다.
  - 백스톱·빚 우주 안이다.
  - `.dddjango-web/` 은 ignore 될 수 있고 dirty·subst 대조 밖이라 기각했다.
- **정규 바이트**: 파일 바이트는 `json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True, separators=(',', ': ')) + '\n'` 의 UTF-8(NFC) 바이트와 같아야 한다(WV1). 그래서 다음이 한 번에 드러난다.
  - 손 편집·숨은 칸·병합 잔재
  - 중복 키(`object_pairs_hook` 거절)
  - `NaN`·`Infinity`(`parse_constant` 거절)
  - `true` 를 int 로 쓴 값(`type(x) is int`)
  - 실측 P5: `json.loads` 는 둘째 중복 항목을 쓰는데, 사람은 첫째를 본다.

### 3-2. 필드 — 스키마 `dddjango-web-sdk-registry/2`

```json
{
  "schema": "dddjango-web-sdk-registry/2",
  "sdks": {
    "<sdk_id>": {
      "name": "…", "operator": "…", "operator_domains": ["…"],
      "service_api": "<이 프로젝트가 쓰려는 목적>",
      "use_scope": ["<전역>.<핵심 함수>", "<전역>.<이름공간>.*", "<전역>.<이름공간>.<data_out 함수>", "<전역>.<이름공간>.<gateway 함수>:<경로>", "…"],
      "namespace_words": {"<이름공간 | 이름공간.data_out 함수>": ["<사람이 쓰는 낱말>", "…"]},
      "namespace_members": {"<이름공간>": {"<함수>": "call | lifecycle | data_out | gateway | sdk_ui"}},
      "gateway_paths": {"<이름공간>.<gateway 함수>": {"<경로>": "read | data_out"}},
      "features_in_file": ["<init 이 여는 이름공간>", "…"],
      "lifecycle": {"global": "<전역 이름>", "init": "<초기화 함수>", "created_by_init": ["<이름공간>"]},
      "version": "…", "file": "static/vendor/<sdk_id>/<파일>", "size": 0,
      "sha256": "<64 hex>", "upstream_integrity": "sha384-… | null",
      "source_url": "https://…", "final_url": "https://…", "docs_url": "https://…",
      "evidence": {"docs_sha256": "<64 hex>", "cites_source": true, "integrity_from_docs": true, "fetched_from": "network | file"},
      "license": "<SPDX id | LicenseRef-…>", "terms_url": "https://…",
      "origins": {"operator": ["<호스트>"], "operator_in_code": ["<호스트>"], "other": ["<호스트>"]},
      "public_config": [{"setting": "<SETTINGS_NAME>", "attr": "data-<kebab>", "call": "<전역>.<init>"}],
      "approval": {
        "decision": "approved", "gate": "G1 | G1' | G1(리팩토링)",
        "at": "YYYY-MM-DD HH:MM +ZZZZ",
        "source": "<이 판·이 파일의 승인 출처>",
        "namespace_sources": {"(core)": "<출처>", "<이름공간>": "<출처>", "<이름공간>.<data_out 함수>": "<출처>", "<이름공간>.<gateway 함수>:<경로>": "<출처>"},
        "source_line_sha256": {"<출처 문자열>": "<64 hex>"},
        "candidate_token": "<sdk_id>@<판>#<sha256 앞 12>",
        "build": ".dddjango-web/<폴더>/",
        "binds": {"entry_sha256": "<approval 을 뺀 항목의 정규 JSON sha256>"}
      }
    }
  }
}
```

| 칸 | 쓰는 쪽 | 뜻·검사 |
|---|---|---|
| `size`·`sha256`·`upstream_integrity`·`final_url`·`evidence`·`origins`·`features_in_file` | **도구만**(`candidate`) | 바이트·문서의 결정 함수 — WV2 가 바이트에서 `size`·`sha256`·sha384·`origins` 를 다시 계산해 대조한다 |
| `version`·`source_url`·`docs_url`·`file` | 도구 인자 → `candidate.json` | `file` 디렉터리 = id(WV1) · 두 항목이 같은 `file` 이면 WV1 · 확장자 없는 원본은 `<id>.js` |
| `name`·`operator`·`operator_domains`·`service_api`·`use_scope`·`namespace_words`·`lifecycle`·`license`·`terms_url`·`public_config` | Coordinator 판단 → `entry-draft.json` | `operator_domains` 는 2라벨 이상 · 공용 접미사 아님. `public_config.setting` 은 `^[A-Z][A-Z0-9_]*$` 이면서 `SECRET`·`PASSWORD`·`PRIVATE`·`TOKEN`·`ADMIN`·`CLIENT_SECRET` 낱말이 없어야 한다(WV1 — 공개 흐름으로 HTML 에 나가기 때문이다 · 카카오 Admin 키는 비밀이다). `namespace_words` 는 `features_in_file` 의 이름공간마다 운영자 문서의 기능 이름에서 뽑는다(첫 승인 배너에 보인다 · 결속 안 · WV1 품질 규칙과 운영자 문서 등장 수 배너 — v3.1) |
| `namespace_members` | 함수 **이름**은 도구(열거 파일 — 없으면 Coordinator 가 문서에서 · 이름마다 사본 바이트 실재 대조) · **분류**는 Coordinator(운영자 문서) — 도구가 이름 바닥을 강제 | 아래 «함수 분류» · WV1 · 결속 안 |
| `gateway_paths` | 경로 **목록**은 도구(`api-paths.txt` — 사본 바이트의 경로 리터럴 전수) · **분류**(`read`·`data_out`)는 Coordinator(운영자 문서) — 도구가 경로 바닥을 강제 | 아래 «gateway» · WV1 · 결속 안 · `use_scope` 의 gateway 함수가 있을 때만 |
| `approval` | 도구(`install` 인자) | §3-4 · `candidate_token` 은 도구가 만든다 |

- `origins` 는 사본 안 https 호스트 **전수**다. 운영자 도메인 하위면 `operator`, 아니면 `other` 로 나눈다(실측 16 = 12 + 4). `operator_in_code` 는 `mask_js` 로 주석을 지운 코드 안에 있는 운영자 호스트다(O7).
- `use_scope` 의 원소는 네 꼴이다(v3.2 · 규범 v3.1 m-2 · v3.3 경로 지정 gateway — 규범 v3.2 n1).
  - **핵심 함수**: `Kakao.init`·`Kakao.isInitialized` — 이름공간 밖 · 묶음 `(core)`
  - **이름공간 묶음**: `Kakao.Share.*` — 그 이름공간의 `call`·`lifecycle` 함수만 덮는다
  - **이름 지정 함수**: `Kakao.Share.uploadImage` — 그 이름공간의 `data_out` 함수만 이 꼴로 적는다
  - **경로 지정 gateway**(v3.3 · 규범 v3.2 n1): `Kakao.API.request:/v2/user/me` — `gateway` 함수는 경로마다 이 꼴로만 적는다. 묶음·이름만으로는 덮이지 않는다
  - 승인과 다시 묻기의 단위는 이름공간 · 이름 지정 함수 · gateway 경로다(사용자 결정 «G1 에서 한 줄로 다시 묻기» · 규범 닫힘 확인 §6 다듬기).
- **함수 분류 `namespace_members`**(v3.2 · 규범 v3.1 m-2 · v3.3 다섯째 종류): `use_scope` 에 원소가 있는 이름공간마다, 그 안의 함수 전부를 다섯으로 나눈다.
  - `call` — 호출형이다(`sendDefault`·`sendCustom`·`sendScrap`). 묶음이 덮는다.
  - `lifecycle` — 수명 함수다(`cleanup`). 묶음이 덮고, G2 기록기는 이 함수를 바꾸지 않는다(§7-6).
  - `data_out` — **사용자 자료·계정 상태를 운영자 쪽에 보내거나 바꾸거나 지우는 함수**다(`uploadImage`·`scrapImage`·`deleteImage` — 카카오는 올린 그림을 100일 보관한다 · 운영자 문서 [실측 `facts.md`]). 묶음이 덮지 **않는다**. `use_scope` 에 이름을 적어야 쓸 수 있고, 그 이름이 다시 묻기의 단위다.
  - `gateway` — **운영자 API 경로를 인자로 받아 어느 기능이든 부르는 범용 함수**다(`Kakao.API.request({url})` — 사본의 경로 리터럴 30개 가운데 친구 메시지 발송·그림 올리기·연결 끊기가 있다 [실측]). 묶음도 이름도 덮지 않는다. `use_scope` 에 경로마다 `<함수>:<경로>` 로 적어야 그 경로를 쓸 수 있다(v3.3 · 규범 v3.2 n1).
    - 경로 분류 `gateway_paths`: 도구가 사본의 경로 리터럴 전수(`api-paths.txt`)를 목록으로 내고, Coordinator 가 운영자 문서로 `read`(조회)·`data_out`(사용자 자료·계정 상태를 보내거나 바꾸거나 지움)으로 나눈다. **경로 바닥**: 경로 조각(`/`·`_` 로 가름)에 `send`·`upload`·`delete`·`unlink`·`revoke`·`scrap`·`update`·`logout`·`signup`·`set`·`save`·`store`·`write` 가 있으면 적어도 `data_out` 이다. 카카오 2.8.3 은 data_out 16 · read 14 다 [실측 `floors.out`].
    - `read` 경로도 경로마다 승인한다. 사용자 정보를 읽는 경로(`/v2/user/me`·친구 목록)도 데이터 흐름을 바꾸기 때문이다. `data_out` 경로는 m-2 와 같은 규칙(이름 명시 + G1 한 줄 + 1급 행에 운영자 쪽 효과)이다.
  - `sdk_ui` — SDK 가 우리 DOM 에 UI 를 그리는 함수다(`createDefaultButton` 류). 어떤 승인으로도 쓰지 않는다(houserules §9 제외 · WV9 가 늘 거절).
  - **이름의 출처**: Coordinator 가 브라우저 도구로 사본을 더미 키로 init 해 이름공간마다 함수 이름을 센 열거 파일을 `candidate --members-file` 로 넘긴다. 아직 승인 전의 바이트이므로 열거하는 동안에는 **로컬(사본을 내는 임시 출처) 밖 요청을 모두 막고**, 막힌 요청 수를 열거 파일에 남긴다 — 도구가 `candidate.json` 에 옮긴다(v3.3 · 규범 v3.2 n3). 브라우저가 없으면 운영자 문서의 API 참조에서 옮기고, 배너에 «함수 표 출처: 문서» 1급 표시를 남긴다. 도구는 이름마다 사본 바이트(주석을 지운 코드)에 그 식별자가 실재하는지 본다. 어느 쪽이든 G2 스니펫이 실제 함수 목록과 다시 대조한다 — 표에 없는 함수는 발견이다(§7-6 · 실측 `run4.out`).
  - **분류의 출처**: Coordinator 가 운영자 문서로 정한다. 도구는 **이름 바닥**을 강제하고, 바닥보다 느슨한 분류는 WV1 이 거절한다. 엄격 순서는 `sdk_ui` > `gateway` > `data_out` > `call`·`lifecycle` 이다.
    - 이름은 **camelCase·`_` 토큰**으로 나눠 대조한다(v3.3 · 규범 v3.2 n2 — 부분 문자열 대조는 `inputValue`·`outputText`·`restoreSession` 을 잘못 올린다 [실측 `floors.out`]).
    - 마지막 토큰이 `button`·`widget` 이거나 첫 토큰이 `render`·`mount`·`draw` 이면 적어도 `sdk_ui` 다(`createDefaultButton` · `createLink` 는 아니다).
    - 이름 전체가 `request`·`invoke`·`fetch`·`call`·`ajax` 이면 적어도 `gateway` 다.
    - 토큰에 `upload`·`delete`·`remove`·`store`·`save`·`put`·`unlink`·`revoke` 가 있거나 마지막 토큰이 `image`·`file`·`files`·`photo` 이면 적어도 `data_out` 이다.
    - `cleanup`·`destroy`·`dispose`·`teardown` 은 위 바닥이 없을 때 `lifecycle` 이다.
  - 이름 바닥은 덫이다. 실제 판정은 운영자 문서(design-review-web 12 가 대조)와 G2 실행 짝(파일·바이너리 인자를 받은 함수가 `data_out` 이 아니면 발견 · gateway 의 실제 `url` 인자가 승인 경로 밖이면 발견)이 받친다. 압축 코드에서 «함수 → 운영자 API 경로» 대응을 도구가 기계로 확정할 수는 없다. 그래서 일반 함수에 대해서는 `api-paths.txt` 의 저장 경로를 배너에 함께 보이는 사실로만 쓰고, 경로를 인자로 받는 gateway 함수만 경로 단위로 승인한다.
  - 분류표는 결속 안에 있다. 그래서 «무엇이 묶음에 드는가»를 첫 승인 뒤에 바꿀 수 없다.
- `features_in_file` 은 사용자에게 «파일 전체가 무엇을 담는가»를 보이는 칸이다.

### 3-3. 쓰는 사람·쓰는 때

1. Phase 1 에서 명세가 «새 채택» 후보를 내면 Coordinator 가 `sdk_vendor.py candidate` 를 돈다. 결과는 `sdk-candidates/<id>/` 에 쌓이고 목록은 바꾸지 않는다. 도구가 `candidate_token`(`<id>@<판>#<sha12>`)을 만든다.
2. G1 승인 뒤 Phase 2 진입 ②″ 에서 `sdk_vendor.py install` → `sdk_vendor.py verify` exit 0 → **격리 커밋** `chore(web-sdk): <id> <판> 설치 — <gate> <시각>`(목록·`static/vendor/<id>/`·`static/vendor/.gitattributes` 만)을 만든다. 해시를 build-state `sdk_commits` 에 적는다.
3. 목록은 «승인된 항목»만 담는다. 승인 전 기록은 후보 파일이 맡는다.
4. **미등재 형제 단위**(v3 · 검사기 닫힘 확인 N1 · v3.1 V3-1): `static/vendor/` 에 등재되지 않은 id 디렉터리나 직속 파일이 있어도 `install` 은 거절하지 않는다. 목록 시대 전의 단위는 등재 프로젝트에서도 «등재 전» 의미론(WV12 · diff 게이트 · G0 알림)을 따른다(§5-1). G1 배너에는 «미등재 벤더 단위 n개 — 이관 항목(입구 …)» 1행을 낸다. 목록 시대에 생긴 미등재 내용(WV13)이 있으면 `install` 의 자가 `verify` 가 실패해 되돌린다 — 그 상태는 이미 모든 레인의 늘 red 이므로 먼저 고친다. v2 의 «목록 생성 전제(거절)»는 워크트리 단위라 병합 경합을 막지 못했고, 무관한 임시 사본이 정당한 채택 레인을 세웠기 때문에 걷었다. 그 일은 늘 검사 범위 축소와 «목록 시대» 판정이 맡는다.
5. 판 올림·기존 등록·범위 넓힘·제거·복원도 같은 `chore(web-sdk):` 격리 커밋이다. 코더·설계자는 쓰지 않는다.

### 3-4. 승인 기록 — 무엇에 묶이고, 누가 줄 수 있나

- **결속**: `binds.entry_sha256` = approval 을 뺀 항목의 정규 JSON(§3-1 직렬화 · 키 정렬 · **NFC 로 바꾼 뒤**) sha256 이다. WV3 이 매번 다시 계산한다.
  - 판·지문·주소·문서 증거·쓰는 기능 묶음·낱말 표·키 이름·호스트·라이선스 어느 칸이 바뀌어도 승인은 무효다(검토 M2·m5 · K28).
- **출처** — 둘만 받는다. 도구가 꼴과 내용을 검사한다.
  - `본인 직접(<YYYY-MM-DD HH:MM:SS +ZZZZ>)` — 이 실행에서 사용자가 직접 답했거나 직접 입력한 요청문에 적었다. G1 질문문에는 판·`candidate_token`·`use_scope`·`features_in_file` 이 들어 있었다. 결정 줄은 `g1_decisions` 에 판·지문 앞 12·이름공간 묶음을 담는다.
  - `사용자 원문 <저장소 상대 경로>@<커밋 12>:<행>(<시각>)` — 도구는 `git show <커밋>:<NFC 로 바꾼 경로>` 의 그 행을 읽고 다음을 확인한다. 경로는 출처 문자열에 **원문 그대로** 기록하고, 조회·대조에만 NFC 꼴을 쓴다 — git 트리 경로는 NFC 다(`core.precomposeunicode` · R8f §2 · 규범 v3.1 nit-6).
    - ① 커밋이 `git merge-base --is-ancestor <커밋> HEAD` 를 만족한다(버린 가지 금지 · 규범 R3)
    - ② 경로가 `web/`·`.dddjango-web/` 밖이다(화면 코드·빌드 기록 안 문장 금지 · 규범 R3)
    - ③ `<시각>` 문자열이 그 행에 실재한다
    - ④ **도구가 만든 필수 낱말**이 실재한다(승인 종류마다 다르다 · v3.1 — 규범 m-a). Coordinator 의 `--source-tokens` 는 덧붙이기만 한다(규범 R3 · 검사기 지적 «Coordinator 가 고른 토큰» 제거).
      - **채택·판 올림·기존 등록**: `operator`·`name` 의 낱말 1개(도구가 항목에서 뽑는다) + **`version` 문자열 또는 `candidate_token`**. 판 올림은 새 판(새 표지)이어야 한다.
      - **범위 넓힘**: `operator`·`name` 의 낱말 1개 + **그 단위(이름공간 또는 이름 지정 `data_out` 함수)의 `namespace_words` 낱말 1개**. gateway 경로 단위는 낱말 표가 없으므로 **그 경로 문자열 그대로**(예: `/v2/user/me`)를 담아야 한다(v3.3). 판·표지는 요구하지 않는다 — 바이트가 그대로이고, 그 판의 사실은 이미 승인됐다. 예: «카카오 로그인 붙여 주세요» 는 통과한다(`카카오` + `카카오 로그인`).
    - ⑤ 낱말 대조는 양쪽을 NFC 로 바꾼 뒤 한다. 이름공간 낱말이 운영자 낱말을 품는 경우(«카카오 로그인» ⊃ «카카오»)도 두 조건을 각각 센다.
    - ⑥ `--replace` 는 직전 `approval.source` 와 같은 출처를 거절한다(M1(b)).
    - 시각 하한(`<시각>` ≥ `fetched_at`)은 **보조**다. 어기면 배너에 «원문이 후보 수집보다 이르다» 1행을 남기고, 거절하지는 않는다 — 판이나 표지를 담은 문장은 이미 사실을 지목했기 때문이다.
    
    통과하면 그 출처의 `source_line_sha256` 을 남긴다. 이 값은 **git blob 에서 읽은 그 행의 원바이트**(줄바꿈 제외)의 sha256 이다. 낱말·시각 대조만 NFC 로 바꾼 뒤 한다(규범 nit-c · R8f 판형 — 기록은 원바이트, 비교는 정규화 뒤). 저장소 밖 파일·절대 경로는 거절한다(n2). 행 번호는 마지막 `:<숫자>(` 에 앵커한다.
    - **조상 조건을 실제로 지키는 길**(규범 nit-b): 레인이 `lane/*` 가지에서 돌면, 레인 시작 뒤 main 에 커밋된 원문은 레인 HEAD 의 조상이 아니다. 그래서 발주자는 사용자 원문 줄을 **레인 가지의 최상위 `docs/…`**(예: `docs/superpowers/orders/lane/…`)에 커밋한다 — 8e 치환 확인은 최상위 `docs/` 를 문서로 대조 밖에 둔다. 또는 그 줄이 든 main 을 승인 병합으로 받은 뒤 출처로 쓴다.
- **위임 불가**: 발주 고정·대리 답·게이트 위임·Coordinator 추론은 출처가 아니다. 게이트 답을 대리에게 맡긴 실행은 SDK 채택·판 올림·범위 넓힘·기존 등록 승인을 **사용자 원문**으로만 받는다. 원문이 없으면 기록하고 그 지점에서 정지한다(`CL:276` 위임 목록 · A23).
- **`gate`·`at`**: `G1′`(U+2032)도 받되 `G1'` 로 정규화해 저장한다(n1). `at` 은 `date '+%Y-%m-%d %H:%M %z'` 꼴로 시간대를 포함한다(nit 5).
- **6-3-13 의 09-28 줄(`:74`)**: 판도 표지도 없다. 그래서 첫 채택 출처로도 쓸 수 없다 — 사실을 보기 전의 방향 결정이다. G1 에서 본인 직접으로 받거나, 사용자가 판(또는 표지)을 담아 남긴 새 줄이 필요하다(§9).
- **남는 위험**: 규칙을 어긴 Coordinator 가 «본인 직접»을 지어내는 경우다. ⓑ 와 같은 신뢰 경계이고, G2 배너 SDK 행이 사후에 보인다.

### 3-5. 판 올림 · 범위 넓힘 · 바이트 변경

- **판 올림**: `candidate` → G1/G1′ «SDK 판 올림: <id> <옛 판> → <새 판> · 변경 기록 URL · 표지 <새 candidate_token>» → `install --replace` 순서다.
  - 운영자 파일 이름이 바뀌면 도구가 옛 사본을 지워 `vendor/<id>/` 에 등재 파일 하나만 남긴다(검토 B1 교정 · K16).
  - 템플릿 경로가 바뀌면 그 로드 줄 치환은 coder 몫이다.
  - 이름공간 출처(`namespace_sources`)는 그대로 넘어간다. 판 승인 출처(`source`)만 새로 받는다.
- **범위 넓힘 — 이름공간 단위**(사용자 결정 «G1 에서 한 줄로 다시 묻기» · 규범 닫힘 확인 §6 다듬기)
  - **같은 이름공간 안 변형**(`Kakao.Share.sendCustom`·`sendScrap` 등 분류 `call` — `Kakao.Share.*` 가 이미 `use_scope` 에 있음): 묻지 않는다. 항목이 바뀌지 않으므로 결속도 그대로다. G1 배너에 정보 줄 «같은 묶음 안 기능: Share.sendScrap»만 낸다.
  - **새 이름공간**(`Auth`·`API`·`Channel`·`Navi`·`Cert`·`Picker`): G1/G1′ 에서 **1문항**을 묻는다 — «카카오 로그인(Auth)을 이 프로젝트에서 쓸까요? 로그인은 사용자 정보·토큰을 다룹니다 …». 승인이면 `install --scope-add Kakao.Auth.*` 가 `use_scope`·`namespace_sources` 를 바꾸고 결속을 새로 묶는다.
  - **이름공간 안의 `data_out` 함수**(v3.2 · 규범 v3.1 m-2): 묶음이 있어도 덮이지 않는다. 새 이름공간과 같은 1문항으로 묻는다 — «카카오톡 공유에 사용자가 고른 사진을 카카오 서버에 올리는 기능(Share.uploadImage)을 쓸까요? 올린 사진은 카카오가 보관합니다(운영자 문서: 100일).» 승인이면 `install --scope-add Kakao.Share.uploadImage` 가 이름 지정 원소와 `namespace_sources["Share.uploadImage"]` 를 더하고 결속을 새로 묶는다. 낱말 표 키는 `Share.uploadImage`(예: «사진 올리기»·«이미지 업로드»)다. 아래 «자명하면 묻지 않는다»도 같이 적용하되, 그때도 G1 배너 1급 행에 운영자 보관 사실을 함께 적는다.
  - **gateway 경로**(v3.3 · 규범 v3.2 n1): 경로마다 범위 넓힘이다. 1문항 예: «카카오 사용자 정보 읽기(API.request · /v2/user/me)를 쓸까요?» · data_out 경로면 «…친구에게 메시지 보내기(/v1/api/talk/friends/message/default/send)를 쓸까요? 사용자 이름으로 친구에게 메시지가 갑니다.» 승인이면 `install --scope-add Kakao.API.request:<경로>` 다. gateway 경로에는 «자명하면 묻지 않는다»를 쓰지 않는다 — 그 규칙은 첫 승인 배너에 보이고 결속된 낱말 표가 전제인데, 경로 30개의 낱말을 첫 승인에 미리 정해 두지 않았기 때문이다(그때 Coordinator 가 요청문에 맞춰 낱말을 고르면 순환이 된다). 대리 실행은 경로 문자열을 담은 사용자 원문이 필요하다(§3-4 ④).
  - **묶어 묻기**(v3.3 · 규범 v3.2 n2): 한 명세가 같은 이름공간에서 새로 들이는 `data_out` 이름·gateway 경로는 **1문항 · 1결정 줄**로 묶는다(예: «사진 올리기·지우기(uploadImage·deleteImage)를 쓸까요?»). 결정 줄에 단위를 모두 적고, `namespace_sources` 에는 단위마다 같은 출처를 남긴다.
  - **`sdk_ui` 함수**: 어떤 승인으로도 범위에 넣지 않는다. 명세가 필요로 하면 호출형 API 로 다시 설계한다.
  - **6-3-13 영향 없음**: 6-3-13 은 `Kakao.Share.sendDefault` 만 쓴다. `Share` 의 함수 10개에는 gateway 가 없다 [실측 `run4.out`·`floors.out`]. 그래서 질문은 채택 1문항 그대로다. gateway 는 로그인·사용자 정보처럼 `API` 를 쓰는 레인부터 해당한다.
  - **자명하면 묻지 않는다**: 이번 요청의 사용자 원문 — 사용자가 직접 입력한 요청문(본인 직접) 또는 커밋된 사용자 원문(§3-4 ①~③ 조건 · ④ «범위 넓힘» 필수 낱말 = 운영자 낱말 + 이름공간 낱말 · 판 불요) — 이 그 이름공간의 `namespace_words` 낱말(예: «카카오 로그인»)을 이미 담았으면, 그 줄을 출처로 받고 질문 대신 G1 배너 **1급 행** «범위 넓힘: Auth(로그인) · 출처 <줄>»을 둔다.
  - 첫 승인 질문의 약속 «다른 기능은 쓰려면 다시 묻습니다»를 그대로 지킨다. 낱말 표는 첫 승인 배너에 보이고 결속 안에 있다. 그래서 «무엇이 같은 묶음인가»를 나중에 바꿀 수 없다.
- **같은 판 · 다른 바이트**: WV2 발견이다. `source_url` 에서 다시 받은 바이트가 등재 지문과 같으면 승인 불요 복원(§6-8)이고, 다르면 «판 올림 / 제거 / 정지»다.

### 3-6. 제거

- 기능 레인은 자동으로 제거하지 않는다(규범 m2 ①②).
- 사용처 0 은 다음 G0 빚 스캔의 WV11 키가 되고, 사용자가 ⓐ/ⓑ 로 정한다.
- ⓐ 이면 `sdk_vendor.py remove` 를 격리 커밋으로 한다. 이때 참조 확인은 **저장소 전체 템플릿**(`git grep` · `*.html`) 기준이다(m2 ③).
- `remove` 는 항목과 **`vendor/<id>/` 디렉터리를 함께** 지운다. 그래서 등재 시대 강등 금지(WV13)에 걸리지 않는다. 마지막 항목이면 `sdk_registry.json`·`static/vendor/`(+ `.gitattributes`)도 지운다.
- 다시 쓰려면 새 채택이다(사용자가 제거를 골랐으니 «처음 한 번»과 어긋나지 않는다).

### 3-7. 동시 채택·병합

- 텍스트 충돌은 보이는 실패다.
- 병합 결과는 정규 바이트·결속·등재 id 디렉터리 정확성·등재 시대 강등 금지(WV1~WV6·WV13)를 다시 통과해야 한다. **병합하는 쪽이 `sdk_vendor.py verify` exit 0 을 확인한 뒤 main 에 올린다**(규범 R2 — REQUEST_GUIDE §7 에도 한 줄).
- 미등재 사본을 가진 가지와 등재 가지가 만나도 늘 검사는 등재 id 만 보므로 main 이 막히지 않는다(§5-1). 다만 그 사본이 main 에 들어오는 순간부터 main 을 받는 레인의 diff 게이트가 그것을 «들인 것»으로 본다(§5-1 표).

## 4. 사본 자리 · 로드 · 키

### 4-1. 사본 자리 — `web/static/vendor/<sdk_id>/<파일>` + `web/static/vendor/.gitattributes`

| 후보 | 판정 | 이유 |
|---|---|---|
| **`static/vendor/<sdk_id>/<파일>`**(새 조건부 칸 · fonts/·files/ 와 같은 «필요할 때만») | **채택** | 제3자 원본임이 경로로 보인다. 기능 JS 칸(`js/` = 수기 코드 · 평면 · WP1 `.min.js` 금지)의 규칙을 흐리지 않는다. 리팩토링·감사 제외를 경로 하나로 정할 수 있다 |
| `static/js/<이름>.min.js` | 기각 | `js/` 는 «기능당 한 파일 · 우리 코드»다. 섞이면 감사·motion 역스윕·리팩토링이 벤더 바이트를 우리 코드로 읽는다 |
| `static/files/` | 기각 | 다운로드용 파일 칸이다. 실행 코드를 두지 않는다 |
| `static/vendor/<id>/<판>/<파일>`(판 디렉터리) | 기각 | 판 올림마다 템플릿 경로가 바뀐다. 격리 커밋과 템플릿 편집 사이에 깨진 중간 상태가 생긴다. 캐시는 모든 JS 에 같은 프로젝트 정책(해시 이름 저장소·캐시 헤더)이 다룬다 |

- **바이트 안정 표지**: `install` 이 `web/static/vendor/.gitattributes` 를 고정 바이트 `* -text -diff -filter -ident -eol -working-tree-encoding\n` 으로 둔다.
  - 디렉터리 단위 `.gitattributes` 는 상위 규칙보다 우선한다.
  - collectstatic 기본 무시 패턴(`.*`)에 걸려 공개되지 않는다.
  - 저장소 루트 파일이 아니라 web/ 안이므로 격리 커밋·subst 대조와 충돌하지 않는다(규범 m6 · 검토 M1 ④).
  - `.git/info/attributes` 같은 로컬 우선 규칙은 WV2 의 `check-attr` 가 효과값으로 잡는다.
- WS6·WV5 의 트리 규칙: 등재 id 디렉터리 안에는 등재 파일 하나만, `static/vendor/.gitattributes` 는 고정 바이트다. `vendor/` 직속의 다른 파일과 미등재 id 디렉터리는 미등재 단위다 — 목록 시대 전 내용이면 WV12(등재 전), 목록 시대에 생긴 내용이면 WV13(늘)이다(§5-1).
- **OS 잡파일**: 고정 목록(`.DS_Store`·`Thumbs.db`·`desktop.ini`·`._*`·`Icon\r`)에 들고 미추적이거나 무시된 파일은 WV5·WV12·WV13·`install`·`verify` 가 모두 뺀다(검사기 N3). `check_design_evidence.py:25` 의 `EXCLUDED_FILES` 와 같은 결이다. 추적됐거나 템플릿이 가리키면 빼지 않는다.

### 4-2. 로드 규칙

- 외부 `{% static 'web/vendor/<id>/<파일>' %}` 로 한 번 로드한다. 속성은 `src`·`defer` 만 쓴다(프로젝트 CSP 가 nonce 를 쓰면 `nonce` 도). `async`·`type`·`nomodule`·`integrity`·그 밖은 금지한다(nit 4).
- **페이지는 `{% block scripts %}` 안에만**, 그 SDK 를 부르는 기능 JS 태그보다 앞에 둔다. 다른 block 에 두면 원문 순서와 렌더 순서가 갈린다(검토 minor 5). base 에 둘 때는 `{% block scripts %}` 여는 줄보다 앞이다.
- base·페이지 중복 금지 · fragment 금지 · standard prefix 만.
- 순서 규칙은 같은 파일 원문 기준이다. 교차 파일(base 의 벤더 ↔ 페이지 블록)은 base 색인으로 함께 대조한다(K35).

### 4-3. 공개 키 흐름

- `env`(사용자 값) → settings 이름(SDK 공개 설정 배선 — G1 승인 하 Coordinator) → VM → state → 템플릿 `public_config[].attr` 의 escape 된 data 속성(값은 순수 `{{ … }}` — WV7 템플릿 분기) 또는 `json_script` → 기능 JS.
- **SDK 공개 설정 배선**: G0 배선 6종과 다른, SDK 채택 때만 생기는 호스트 배선이다. 등재 `public_config[].setting` 이름이 settings 에 없으면 G1 배너에 «추가»로 보이고, Phase 2 진입 준비 ③ 에서 Coordinator 가 한 줄 더한다.
  - 기본은 프로젝트의 **선택형** 꼴(빈 문자열 = 미설정)이다. 근거는 셋이다.
    - 필수형은 그 값이 아직 없는 다른 워크트리와 dev 의 기동을 멈춘다(spring_dream 발주서 §2-5 실측 위험).
    - 화면 기능 하나가 백엔드 전체를 세우면 안 된다.
    - 빈 키는 명세 «설정 실패» 행과 G2 확인 case 로 보이게 만든다.
  - 프로젝트에 선택형 꼴이 아예 없을 때만 필수형을 쓰고, 배너에 «기동 영향»을 적는다.
  - 값은 쓰지 않는다. web/ 밖 편집이므로 G1 승인 뒤 적용하고 «배선 적용» 기록을 남긴다(Phase 2 진입 준비 안에서 적용하면 `git_snapshot` 전이라 끝 green ④ 범위 밖이고, 설계 반송 뒤 적용이면 `--except`).
- 명세는 두 실패를 나눈다(규범 m3).
  - **설정 실패**(키 빈 값 — «다시 시도» 없이 안내)
  - **일시 실패**(SDK 로드 실패 등 — 다시 시도)
- G2 배너·완료 보고에 «운영 env 필요: <이름>» 1행을 둔다. G1 배너에는 «JavaScript 키만 — Admin 키 금지»를 적는다.
- 금지: 키 리터럴(JS·템플릿), 전역 상수, web 코드의 `os.environ`, 새 context processor, 템플릿의 settings 직접 접근.

## 5. 검사기

### 5-1. 무엇이 «늘» 검사되나 — 대상별 의미론(v3 · v3.2 보강)

v2 의 «체제(프로젝트 단위)» 판정은 병합 경합(검사기 N1)과 강등(검사기 N2)에 뚫렸다. v3 는 판정 단위를 **디렉터리와 이력**으로 내린다.

| 대상 | 늘 도는 검사(diff 게이트 무관 · «미룰 수 없음») | diff 게이트 | 빚 스캔 | 다른 레인 영향 |
|---|---|---|---|---|
| **목록 파일**(`web/sdk_registry.json` 이 있다) | WV1(형식·정규 바이트) · WV3(결속·출처) · WV4(공식성) | WV7·WV9 | WV1·WV3·WV4 키(`undeferrable`) | 어긋나면 모든 레인의 G2 red(의도) |
| **등재 id 디렉터리**(`vendor/<목록에 있는 id>/`)와 그 참조 · `vendor/.gitattributes` | WV2(git 저장 바이트) · WV5(그 디렉터리의 정확성과 표지 바이트 — OS 잡파일 제외) · WV6(그 디렉터리를 가리키는 모든 템플릿 참조) | WS6/WP1/WP2 벤더 분기(덫) | 같은 키(`undeferrable`) | 같다. 들어오는 길은 변조·플러그인 밖 편차·충돌 해소 실수뿐이다. G0 빚 스캔이 먼저 드러내고, ⓡ1~ⓡ4 는 언제든 고친다(§6-8) |
| **목록 시대에 생긴 미등재 단위**(`vendor/<x>/` 디렉터리 또는 `vendor/` 직속 파일 가운데 목록에 없는 것 — 그 안의 지금 내용 하나라도 «목록 시대»에 처음 생겼다 · v3.1 · 또는 이력상 등재 바이트를 다른 자리로 옮겼다 · v3.2) | **WV13 «등재 시대 강등 금지»** — 목록이 없어도 돈다 | — | 같은 키(`undeferrable`) | 같다. 목록 삭제·항목 삭제·rebase·병합 해소 탈락·**디렉터리 개명**·빌드 기록 없는 편집으로 늘 검사를 피하는 길을 막는다(검사기 N2 · V3-2 · V3-3). 정상 `remove` 는 디렉터리를 함께 지우므로 걸리지 않는다 |
| **목록 시대 전의 미등재 단위**(그 안의 지금 내용이 모두 목록이 생기기 전에 이미 있던 것 — 목록이 생기기 전에 갈라진 가지의 사본 · 평면 `vendor/kakao.min.js` 포함 · **그 가지를 merge 로 받았을 때만** — rebase·squash·cherry-pick 으로 받으면 같은 바이트의 탄생 커밋이 시대 안에 새로 생겨 WV13 이다 · 검사기 v3.1 minor 1 · K50c) | 없음(규범 B1 · 검사기 N1 · V3-1) | WS6/WP1(새 파일) · WP2(그 사본을 부르는 새·바뀐 줄) · WV8 | **WV12 «미등재 벤더 단위»**(단위마다 키 · 이관 항목 · 보통 빚 규칙) + WS6/WP1/WP2 키 · **모든 G0 배너에 입구 알림 1행** | **늘 검사로는 없다.** 그러나 그 사본(과 로드 줄)이 레인 도중 main 에서 들어오면, diff 게이트가 «이번에 들인 것»으로 보아 그 레인의 G2 가 WS6/WP1/WP2 로 red 가 된다(`git diff <git_snapshot>` 작업 트리 대비 [실측 규범 R1]). G0 동결 뒤라 ⓐ/ⓑ 로 다룰 수 없고, **등록이 main 에 착륙할 때까지 출구가 없다.** 그래서 6-3-13 은 «릴리즈 뒤 등재 경로로만»이 품질 기본값이다(§9) |
| **무관**(목록·벤더·이력 모두 없음) | 없음 | 오늘과 같음 + WP3 확장 · WV8 | 오늘과 같음 | 없음 |

- **왜 등재 id 에만 «늘»인가**
  - 등재 id 는 사용자 승인을 거쳐 도구로만 생긴다. 그 디렉터리의 어긋남은 «승인된 상태의 파손»이라 지금 실행되는 미승인 바이트다(검사기 B1).
  - 목록 시대 전의 미등재 단위는 승인이 한 번도 없던 제3자 JS 다. 오늘의 html2canvas 와 같은 빚이고, 범위 기반 빚 의미론이 맞는다. 여기에 «늘»을 걸면 사본 하나·병합 하나가 무관한 레인 전부를 막는다(규범 B1 · 검사기 N1 실측).
- **경계는 «목록 시대»로 고정한다**(v3.1 · 검사기 V3-3 · nit 2)
  - **목록 시대** = 저장소 이력(HEAD 에서 닿는 모든 커밋 · `--full-history`)에서 `web/sdk_registry.json` 을 들인 커밋 가운데 하나라도 조상(또는 자신)인 커밋들이다. 미커밋 내용은 HEAD 가 시대 안이거나 작업 트리에 목록이 있으면 시대 안이다.
  - 미등재 단위의 각 파일에 대해 **지금 내용(blob)이 나타난 커밋들**을 찾는다. 그 커밋들이 **모두** 시대 안이면 «목록 시대에 생긴 내용»이다. 단위 안에 그런 파일이 하나라도 있으면 WV13, 없으면 WV12 다.
  - v3.2 는 이것을 파일마다 묻지 않고 **한 번 걸어** 표로 만든다(검사기 v3.1 minor 3 · nit 2). `git log --full-history -m --raw --no-abbrev --format=%x00%H HEAD -- web/static/` 의 각 행에서 새 쪽 blob(상태 A·M·R·C·T)을 (커밋, 경로)로 모은다. `-m` 은 병합 커밋이 부모마다 보인 차이를 넣는다. 그래서 병합 해소에서만 생긴 내용도 탄생이 보인다. 목록 이전의 충돌 해소가 만든 사본이 «HEAD 시대» 대체 규칙으로 WV13 이 되던 오분류도 사라진다.
  - 그래서 개명·복사·변조로 새로 생긴 내용은 이름과 무관하게 WV13 이다. 목록 이전부터 있던 바이트를 그대로 가진 사본(K40·K50·같은 이름의 등재 전 사본)은 WV12 다. v3 의 «id 이름 이력» 판정은 개명(V3-3)을 놓치고 같은 이름 사본을 거짓 발견(nit 2)했기 때문에 이 규칙으로 바꿨다.
  - **같은 바이트는 미룰 수 있다**(규범 v3.1 nit-5): 목록 이전부터 있던 (등재된 적 없는) 바이트를 시대 안에 새 미등재 디렉터리로 복사하면 WV12(미룰 수 있음)다. 새로 실행되는 바이트가 없기 때문이다. 한 바이트라도 바꾸면 새 blob 이라 WV13 이다.
  - **이력상 등재 바이트 규칙**(v3.2 · 검사기 v3.1 nit 1 · v3.3 좁힘 — 검사기 v3.2 nit): 미등재 단위의 파일 바이트가 저장소 이력의 어느 목록 판에 등재된 `sha256` 과 같을 수 있다.
    - 그 sha256 이 **지금 목록에 없으면**(등재됐다가 빠짐) 어디에 있든 WV13 이다.
    - 지금 목록에도 있으면, 그 바이트가 **목록 시대 전에 지금과 같은 경로**에서 생긴 경우만 WV12 이고 그 밖은 WV13 이다. 앞의 경우는 등재 전 임시 사본이 병합으로 들어온 것이다(K40·K50·K50d).
    - 그래서 «기존 등록»한 SDK 를 항목 삭제 + 개명(바이트 그대로)으로 등재 밖에 두면 WV13 이다. «등재에서 빠지는 길은 `remove` 뿐»이 이 경로에서도 참이 된다(K48b). 옛 임시 자리(같은 경로)로 되돌려 개명해도 WV13 이다 — «같은 경로 예외»는 지금도 등재된 바이트에만 쓴다(K48c · v3.2 는 WV12 [실측 `v33_probes.out`]).
    - 등재 밖으로 나간 SDK 는 WV9 범위 검사도 받지 않으니, 이 길을 열어 두면 승인 범위를 벗어날 수 있었다.
    - 목록 판은 `git log --full-history -m --format=%H HEAD -- web/sdk_registry.json` 의 판마다 `git show` 로 읽는다(판 수는 작다).
    - 검토자의 다른 대안 «등재 바이트면 무조건 시대 내용»은 쓰지 않는다. 6-3-13 꼴(임시 사본 = 나중에 등재한 바이트)이 다시 늘 red 가 되기 때문이다(실측 K50d 는 WV12 유지).
  - **목록 시대는 끝나지 않는다**(의도 · 검사기 v3.2 nit): 마지막 `remove` 로 목록·vendor 를 모두 지워도, 목록을 들인 커밋은 이력에 남는다. 그래서 그 뒤 새로 생긴 미등재 사본도 WV13 이다(실측 K48c).
    - 까닭: 이 프로젝트는 «처음 한 번 등록» 체제에 들어섰다. 그 뒤 새 벤더 바이트는 등록(G1)으로만 들어와야 한다. 등록 없이 사본을 다시 들이는 길을 열면 제거 결정과 승인 절차를 함께 우회한다.
    - 같은 까닭으로, 제거한 SDK 의 목록 이전 임시 사본이 옛 가지 병합으로 되돌아오면 WV13 이다(지금 목록에 없는 등재 바이트 [추정 — 규칙에서]). 아무 템플릿도 부르지 않으면 ⓡ4(승인 불요 제거)로 끝난다.
  - **비용과 단락**(v3.2 · 검사기 v3.1 minor 3)
    - ① 미등재 단위가 없으면 git 을 부르지 않는다(os.walk 만).
    - ② 얕은 저장소가 아니고, 목록을 들인 커밋이 이력에 없고, 작업 트리에 목록도 없으면 걸음 없이 모두 WV12 다(목록 시대가 없으면 답은 늘 WV12).
    - ③ 그 밖은 한 번 걸음 표 하나와 시대 집합(`git rev-list --ancestry-path <시작>..HEAD` ∪ 시작)으로 판정한다. blob id 는 프로세스 안에서 `sha1("blob <크기>\0" + 바이트)`(= `hash-object --no-filters`)로 셈한다.
    - 실측: 미등재 파일 200개에서 0.05 s / 0.13 s(v3.1 문면 8.3 s / 11.5 s) · spring_dream 한 번 걸음 0.06 s(§1-13 · K51).
  - **얕은 저장소**(v3.2 · 검사기 v3.1 nit 4): 미등재 단위가 있고 `git rev-parse --is-shallow-repository` 가 참이면 분류하지 않는다.
    - WV13 은 «판정 불가 — 얕은 이력(`git fetch --unshallow` 뒤 다시)»으로 **exit 1** 을 낸다. 백스톱 계약에서 1 은 사용·내부 오류(미실행 — 통과가 아니다)이고 2 는 blocker 다(v3.3 · 검사기 v3.2 nit — v3.2 의 exit 2 는 계약과 어긋났다). 거짓 통과도 거짓 발견도 내지 않는다.
    - v3.1 의 «보수적 WV13»은 정상 WV12 단위를 미룰 수 없음으로 바꾸는 의도된 거짓 발견이었다(depth 1 실측). notice 만 내면 강등을 놓친다.
    - 레인 워크트리는 전체 이력이라 실해는 작다.
  - 남는 비용(검사기 V3-3 (가) 고지): 목록이 생긴 프로젝트에서 이 판 이전 설치본(1.1.25)으로 도는 레인이 새 미등재 사본을 들이면 그 사본은 늘 red 다. 이 판 이후의 레인은 diff 게이트가 먼저 막는다.
  - 남는 비용 둘째(검사기 v3.1 minor 1 고지): 목록 이전에 갈라진 가지의 사본도 rebase·squash·cherry-pick 으로 받으면 WV13 으로 굳는다. 원래 커밋이 HEAD 에서 닿지 않으니 내용으로 되돌릴 근거가 없다.
    - 그래서 G0 알림(§5-4)과 REQUEST_GUIDE §7 에 «미등재 사본을 가진 가지는 merge 로 착륙»을 적는다(K50c).
    - spring_dream 은 no-ff merge 로 착륙한다(main 첫 부모 사슬 09-01 이후 병합 217 — 검토자 실측). 다른 프로젝트·GitHub squash 착륙에서는 고지가 막는다.
  - 미등재 단위가 등재 id 가 되는 길은 `install --register-existing`(G1 승인)뿐이다.
- **병합**
  - 깨끗한 `install` 가지와 미등재 사본 가지가 충돌 없이 합쳐져도 늘 검사는 등재 id 만 본다. 그래서 main 이 막히지 않는다(K40). 미등재 사본은 WV12·G0 알림으로 남는다.
  - 등재 SDK 를 가져온 병합은 받는 레인의 diff 게이트를 red 로 만들지 않는다. WS6/WP1/WP2 벤더 분기가 WV2 를 통과한 등재 파일을 받기 때문이다. 내용은 늘 검사가 검증한다.

### 5-2. WV — 공식 SDK 등재 13종(v3.2 갱신)

| id | 무엇을 보나 | 실행 |
|---|---|---|
| **WV1** 목록 형식 | 엄격 파싱(중복 키·NaN·bool-as-int 거절) · **NFC 로 바꾼 값의 정규 직렬화 바이트 = 원문 바이트**(NFD 원문 · 손 편집이 드러난다 · R8f 판형 «쓰기는 NFC · 비교는 정규화 뒤») · 스키마 · 필수 칸·타입 · 모르는 칸 · id·`file` 꼴(`file` 디렉터리 = id · 유일) · https · `urlsplit` 점 경계 호스트 ∈ `operator_domains`(source·final·docs) · `operator_domains` 2라벨 이상·공용 접미사 아님 · sha 꼴 · `public_config` 꼴·비밀 낱말 · `use_scope` 원소가 «핵심 함수» · «`<global>.<이름공간>.*`» · «`<global>.<이름공간>.<data_out 함수>`» · «`<global>.<이름공간>.<gateway 함수>:<경로>`»이고 그 이름공간 ∈ `features_in_file` · `namespace_words` 가 `features_in_file` 을 모두 덮음 · **`namespace_words` 품질(v3.1 · 규범 m-b)**: 낱말마다 NFC 2글자 이상 · 운영자·`name` 토큰과 같거나 그 부분 문자열인 낱말 거절 · 운영자·제품 토큰(`SDK`·`JavaScript` 류 포함)을 지우면 빈 낱말 거절 · 두 단위에 같은 낱말 거절 · **`namespace_members`(v3.2 · 규범 v3.1 m-2)**: `use_scope` 에 묶음이 있는 이름공간마다 표가 있다 · 분류 값은 `call`·`lifecycle`·`data_out`·`sdk_ui` · 이름 바닥(§3-2)보다 느슨하지 않다 · 이름 지정 원소의 함수는 그 표에서 `data_out` 이다 · `sdk_ui` 함수는 `use_scope` 에 없다 · `namespace_words` 키는 이름공간 또는 이름 지정 단위(`Share.uploadImage`)다 · **gateway(v3.3)**: `gateway` 함수는 묶음·이름 원소로 덮이지 않고 `<함수>:<경로>` 원소로만 적는다 · 그 경로는 `gateway_paths` 에 있고 분류가 경로 바닥보다 느슨하지 않다 · 이름 바닥은 camelCase 토큰 대조다 · `evidence.cites_source=true` | 늘(목록) |
| **WV2** 사본 바이트 | ① os.walk 정확 이름(대소문자) ② web/ 에서 파일까지 모든 성분 `os.lstat` 심볼릭 링크 0 ③ `git check-ignore -q --no-index` 거짓 ④ 인덱스 항목이 있으면 모드 `100644` · 인덱스 blob = `git hash-object --no-filters` ⑤ `git check-attr text eol filter ident working-tree-encoding` 이 unset/unspecified ⑥ 크기·sha256·(있으면)sha384·`origins` 를 바이트에서 재계산해 일치. git 호출은 `ls-files -s`·`check-attr --stdin` 일괄 | 늘(등재 id) |
| **WV3** 승인 결속 | approval 꼴(§3-4) · `entry_sha256` 재계산 일치 · `gate`·`at` 꼴 · `use_scope` 의 묶음마다 `namespace_sources` 출처가 있다 · 각 `사용자 원문` 출처는 커밋이 **HEAD 의 조상**(아니면 발견 · 얕은 이력이면 notice)이고 경로가 `web/`·`.dddjango-web/` 밖이며 그 행 sha256 = `source_line_sha256` | 늘(목록) |
| **WV4** 공식성 차단 | 라이브러리 CDN 하드 거절(source·final) · 낱말 덫(토큰·결합형) · **O7**: `origins.operator_in_code` 가운데 `host(source_url)`·`host(docs_url)` 가 아닌 호스트 ≥ 1(주석을 지운 코드 기준 — 규범 N2) | 늘(목록) |
| **WV5** 등재 디렉터리 정확성 | `vendor/<등재 id>/**`(os.walk · 링크 포함)는 등재 `file` 하나뿐이다(하위 디렉터리·다른 파일은 발견). `vendor/.gitattributes` 가 있으면 고정 바이트다. **`vendor/` 직속의 다른 파일은 WV5 가 보지 않는다**(v3.1 · 검사기 V3-1 — 등재 파일은 언제나 `vendor/<id>/` 안이므로 직속 파일은 정의상 미등재 단위다 → WV12/WV13). **OS 잡파일 제외**: 고정 목록(`.DS_Store`·`Thumbs.db`·`desktop.ini`·`._*`(AppleDouble)·`Icon\r`)에 들고 **미추적이거나 무시된** 파일만 뺀다. 추적된 잡파일은 발견이다(검사기 N3) | 늘(등재 id) |
| **WV6** 등재 참조 | **모든** web 템플릿(WP2 와 같은 opener 파서 · 주석·verbatim 마스킹)에서 `{% static %}` 인자나 원문 `/static/web/vendor/` 가 **등재 id 디렉터리**를 가리키면, 그것은 standard prefix 의 등재 `file` 이고 WV2 를 통과해야 한다. 무시된 파일을 가리켜도 발견이다(K44). 미등재 단위를 가리키는 참조는 diff 게이트 WP2 가 본다 | 늘(등재 id) |
| **WV7** 공개 키 리터럴 | ① `static/js/*.js` added 줄(`mask_js`): `<global>\s*(\?\.)?\s*(\.\s*<init>|\[\s*["']<init>["']\s*\])\s*(\?\.)?\s*\(\s*["'\`]` ② 템플릿 added 줄: `public_config[].attr` 속성 값이 순수 `{{ … }}` 가 아니면 발견. 간접 상수는 리뷰어 몫(덫) | added 줄(목록) |
| **WV8** 기능 JS 외부 코드·주소 | `static/js/*.js` added 줄(`mask_js` — 주석만 지움). 판정은 **리터럴 단위**다(v3.2 · 검사기 v3.1 minor 2): 문자열·템플릿 리터럴마다 `\xNN`·`\uNNNN`·`\u{…}`·8진 `\NNN` 이스케이프를 풀고, 템플릿의 `${…}` 는 자리표시 한 글자로 두되 그 안의 리터럴도 따로 본다. 문자열 리터럴끼리의 `+` 이어 붙이기는 접어서 한 값으로도 본다(v3.3). ① **외부 주소 리터럴**: 스킴(`http`·`https`·`ws`·`wss`) 뒤에 무엇이든 더 붙은 리터럴과 `//<호스트>` 로 시작하는 리터럴은 발견이다. 허용은 셋뿐이다 — 스킴만(`"https:"` — `url.protocol` 비교) · `스킴://` 만(`'wss://' + location.host` · `startsWith('https://')`) · `스킴://${…}`(주인 자리가 실행 값 — `` `wss://${location.host}/ws` ``). `https:/${'/'}…` 처럼 `//` 를 쪼갠 꼴은 발견이다. 예외는 고정 목록의 XML 이름공간 URI(`http://www.w3.org/2000/svg`·`/1999/xlink`·`/1999/xhtml`·`/1998/Math/MathML`·`/XML/1998/namespace`·`/2000/xmlns/`)뿐이다 ② **도메인 꼴 리터럴**: 최상위가 `com·net·org·kr·jp·cn` 이면 라벨 둘 이상에서 발견이다. `io·dev·app·co·me·xyz·cloud` 이면 **URL 문맥**(앞이 `//`·`@` 이거나 뒤가 `/`·`:`·`?`·`#`)일 때만 발견이다(v3.3 · 검사기 v3.2 nit — 점 찍은 키 `'auth.user.me'` 오탐을 없앴다). `'t1.kakaocdn.net'`·`'kakaocdn.net'`·`'help@x.co.kr'`(문구 속 주소)·`'//i.cdn.io/x.js'`·`'cdn.socket.io/x.js'` 는 잡고, `'li.me'`·`'div.app'`·`'socket.io'`·`'li.msg.me'`·`'auth.user.me'`·`t('nav.about.me')` 는 넘긴다. 이어 붙이기를 접으므로 `'https://' + 'myapi.dev' + '/v1'`·`'https://' + 'i.cdn.io' + '/x'` 는 ① 이 잡는다. **문면 한계**: 단독 약한 최상위 호스트(`'i.cdn.io'`·`'myapi.dev'`·`'cdn.socket.io'` 를 배열 `join`·템플릿으로 주소로 만드는 경우)는 놓친다 — SDK 레인은 R5, 모든 레인은 리뷰어 읽기가 맡는다 ③ **`createElement` 첫 인자는 단일 문자열 리터럴만**(이어 붙이기·변수·템플릿 리터럴은 발견) · 이스케이프를 푼 값이 `script` 면 type 과 무관하게 발견(비실행 JSON 은 서버가 `json_script` 로 렌더한다) · **`createElementNS` 는 둘째 인자에 같은 규칙**(v3.3 · 검사기 v3.2 minor — XHTML·SVG 이름공간의 `script` 도 실행된다 [검토자 실측 `ns_script_check.out`]) ④ `createContextualFragment` · `insertAdjacentHTML`·`innerHTML`·`outerHTML` 에 `<script` 리터럴 · **`.srcdoc` 대입과 `setAttribute('srcdoc', …)`, `document`·`contentDocument`·`ownerDocument` 의 `write`·`writeln` 호출은 값과 무관하게 발견**(v3.3 — 둘 다 같은 출처로 실행된다 [검토자 실측 `sink_check.out`]. 값 조건(`<script` 리터럴)을 두면 이어 붙이기로 빠지므로 싱크 자체를 막는다. 템플릿의 `srcdoc` 을 WP3 ② 가 값과 무관하게 막는 것과 같은 판형이다) ⑤ `import\s*\(` · `importScripts\(` ⑥ `\beval\b`·`\bFunction\b` 의 호출·전달 ⑦ `setTimeout/setInterval(\s*["'\`]`. 표본 47 어긋남 0(v3.3) · spring_dream 전수(main·가지 머리 7·워크트리 7) 적중은 기존 2줄뿐이고 새 싱크 적중은 0 이다(§1-14). **덫의 남는 몫과 짝**(규범 v3.1 m-1): 조각 템플릿(`` `${'ht'}tps://…` ``)·문자 코드·`atob`·계산된 속성·서버가 준 문자열로 만든 주소는 정적으로 다 잡을 수 없다(실행 등가 판정은 결정 불가). 남는 몫을 받는 짝은 레인마다 다르다 — **모든 레인**: discipline-reviewer-web 이 houserules §5⑤(외부 스크립트·외부 주소 리터럴·외부 네트워크 요청 금지 — §7-1 v3.2 문안)로 기능 JS 를 읽는다. **SDK 레인**(명세 SDK 사용 표에 행이 있음): 리뷰어 10 과 G2 실행 확인 «프로젝트 JS 가 시작한 외부 요청 0»(§7-6)이 더해진다. SDK 가 없는 레인에는 실행 짝이 없고, 정적 덫 밖 몫은 리뷰어 읽기가 맡는다 | added 줄(**모든 경우** — 기존 틈) |
| **WV9** 사용 범위 | 기능 JS added 줄의 `<global>.<이름공간>.<함수>(`(`?.`·`["<함수>"]` 꼴 포함)를 `namespace_members` 분류로 본다(v3.2 · 규범 v3.1 m-2): `call`·`lifecycle` 은 `<global>.<이름공간>.*` 가, `data_out` 은 **이름 지정 원소** `<global>.<이름공간>.<함수>` 가 `use_scope` 에 있어야 한다 · `sdk_ui` 는 늘 발견(SDK 가 그리는 UI 금지) · 표에 없는 함수는 발견(«표에 없는 함수 — 표를 고치려면 재승인») · **`gateway`**(v3.3 · 규범 v3.2 n1)는 첫 인자의 `url` 이 문자열 리터럴이고 그 경로가 `use_scope` 의 `<함수>:<경로>` 에 있어야 한다(비리터럴 `url` 은 발견 — 경로는 운영자 API 상수라 state 로 받을 까닭이 없다). `<global>.<함수>(` 는 그 핵심 함수가 있어야 한다. 교정은 범위 넓힘(§3-5)이나 호출형 API 로의 재설계 | added 줄(목록) |
| **WV10** SDK 변경 격리 | 아래 별도 정의 | gated(빌드 기록이 있을 때) |
| **WV11** 미사용 SDK | 어느 템플릿도 그 `file` 을 로드하지 않는다(WV6 과 같은 파서) | 빚 스캔만 · 미룰 수 있음 |
| **WV12** 미등재 벤더 단위(목록 시대 전) | 목록에 없는 `vendor/<x>/`(OS 잡파일 제외 후 비어 있지 않음)와 `.gitattributes` 밖 `vendor/` 직속 파일 가운데, 지금 내용이 모두 목록 시대 전부터 있던 단위마다 키 `WV12|static/vendor/<x>/` · `WV12|static/vendor/<파일>` | 빚 스캔만 · 이관 항목 · 미룰 수 있음 · G0 알림 |
| **WV13** 등재 시대 강등 금지 | 미등재 단위(목록에 없는 `vendor/<x>/` · `.gitattributes` 밖 직속 파일) 가운데 지금 내용 하나라도 **목록 시대에 처음 생긴** 단위는 발견 «목록 시대에 생긴 미등재 벤더 내용 — `sdk_vendor.py remove`(디렉터리째) · 재등록(G1) · 되돌림만». 시대 시작 = `git log --full-history -m --diff-filter=A --format=%H HEAD -- web/sdk_registry.json` · 내용의 탄생 = 한 번 걸음 표(`git log --full-history -m --raw --no-abbrev HEAD -- web/static/` — 모두 시대 안이면 시대 내용) · 이력상 등재 바이트 규칙 · 미커밋 내용은 HEAD 가 시대 안이면 시대 내용 · 단락(목록 이력·작업 트리 목록 모두 없으면 걸음 없이 WV12) · 얕은 저장소면 «판정 불가» exit 1(미실행 · §5-1 «경계» · v3.3) | 늘(목록 유무 무관) |

**WV10 정의**(검사기 M4 · 규범 m4 · v3 (c) 수정):

- 빌드 폴더는 `--design-build`, 아니면 `current_nondesign_scope` 와 같은 «`git_snapshot` 일치» 규칙으로 찾는다. 못 찾으면 «WV10 생략 — 빌드 기록 없음» notice 를 내고 G2 배너에 올린다. 그래도 강등 경로는 WV13 이 늘 막는다.
- 범위는 `git_snapshot..HEAD` 첫 부모 사슬이다(`subst.py` 의 `_chain` 재사용).
  - (a) 이 빌드가 기록한 커밋(`slices[].commits` ∪ `sdk_commits`) 가운데 목록·`static/vendor/**` 를 바꾼 커밋은 `sdk_commits` 에 있어야 한다. 그 커밋은 그 두 경로만 바꾸고 제목이 `chore(web-sdk):` 로 시작해야 한다.
  - (b) `sdk_commits` 의 커밋이 그 밖 경로를 바꾸면 발견이다.
  - (c) 사슬 위 병합이 가져온 상류 몫의 목록·벤더 변경은 **둘째 부모가 기준 가지(main) 이력에 있을 때만 notice** 다(`git merge-base --is-ancestor <둘째 부모> <main 참조>` — 참조는 `main`, 없으면 `origin/main` · 8e 판형 · 규범 m-c). `approved-merges.txt` 에 적힌 병합도 notice 다. 그 밖 병합(레인이 만든 곁가지 재유입)의 목록·벤더 몫은 발견이다. 기준 가지 참조를 찾지 못하면 «기준 가지 없음 — 승인 목록만 대조» notice 를 내고, 목록 밖 병합의 몫은 발견으로 둔다. 내용은 늘 검사 WV1~WV6·WV13 이 따로 검증한다. 이렇게 해도 main 받기마다 레인이 멈추던 문제(규범 R1)는 다시 생기지 않는다. 병합 커밋 **자신의 몫**(두 부모 어느 쪽과도 다른 목록·벤더 내용 — evil merge)은 발견이다.
  - (d) 기록 밖 비병합 커밋(rebase·ff 로 들어온 main 커밋)은 notice 만 낸다(실측 P9 오탐 제거).
  - (e) 목록·벤더의 미커밋 변경은 발견이다. Phase 0 step 1 이 목록·벤더 dirty 시작을 받지 않으므로(A24) 남의 잔재가 아니다.
  - (f) 목록을 지우는 변경도 (a)~(e) 그대로다(K9).
- 모든 경우에 돈다. 목록이 없어도 범위가 벤더를 바꿨으면 본다.

- **`undeferrable` 표지**: 빚 스캔 JSON 의 발견 행에 `undeferrable: true`(WV1~WV6 · WV13)를 싣는다. Coordinator step 4′ 는 판정 물음 없이 «미룰 수 없음»으로 둔다(A21 · 규범 M5 · 검사기 minor 1).
- `backstop.py`: 패밀리 `wv` · `TOTAL_CHECKS` 26 → **39** · 사용법·머리 주석 «검사 39종». WP3 확장은 WP3 안이다.

### 5-3. 기존 검사 변경

| 검사 | 바꾸는 것 | 그대로 |
|---|---|---|
| **WS1** | `web/` 직속 허용에 `sdk_registry.json` | 그 밖 |
| **WS6** | `STATIC_DIRS` 에 `vendor`(조건부). added 경로에 «vendor/ 직속은 `.gitattributes` 만 · 등재 id 밖 디렉터리 · id 안 하위 디렉터리 · 등재 밖 파일». **보증이 아니라 덫이다** — 보증은 WV5(검사기 B1) | 기존 칸 규칙 |
| **WP1** | 등재 `file`(대소문자 정확)이면 WP1 없음. `static/vendor/` 안 비등재 `.js` 는 «등재되지 않은 벤더 JS». 확장자 대조를 소문자로 한다(nit 4 · `x.JS`) | 기능 JS 꼴 · core 규칙 |
| **WP2** | `_script_path_allowed` 는 **WV2 를 통과한 등재 파일 집합**(ctx 캐시)만 받는다. 그래서 `--only wp` 에서도 문면이 참이다(nit 1). 벤더 태그 사유: ① `src`·`defer`(·CSP nonce) 밖 속성 ② 페이지에서 `{% block scripts %}` 밖 ③ 같은 파일 기능 JS 태그보다 뒤 ④ base 에서 block 여는 줄보다 뒤 ⑤ base·페이지 중복. ③~⑤ 는 벤더 태그나 기능 태그 어느 쪽이 added 여도 낸다(교차 파일 색인) | CDN·inline·fragment·ghost·async |
| **WP3** | ① URL 속성(`href·src·action·formaction·xlink:href·data·poster·background·srcset·ping·cite`) 값이 HTML 엔티티 해제·공백/제어문자 제거·소문자화 뒤 `javascript:`·`vbscript:`·`data:text/html` 로 시작 ② `srcdoc` 속성 자체(값 무관) ③ **스킴 조립 금지(v3.1)**: 값에서 HTML 엔티티를 풀고, `{{…}}`·`{%…%}` 를 **자리표시 한 글자**로 바꾸고, 공백·제어문자를 지운다. 그다음 **태그 밖** 첫 `:` 를 찾는다. 그 앞부분이 스킴 자리(`[A-Za-z0-9+.\-]` 와 자리표시만 — `/`·`?`·`#` 없음)이고 자리표시를 담으면 발견이다. 잡는 예는 `java{{ '' }}script:` · `{% if %}javascript{% endif %}:` · `{{ 'javascript' }}:` · `{{ scheme }}://…` 다. 통과하는 예는 `{% url 'auth:login' %}`(콜론이 태그 안) · `{% url 'x' %}?t=12:30` · `{{ base }}/a:b` · `mailto:{{ email }}` · `https://{{ host }}/x` 다. spring_dream main 의 URL 속성 216개에서 v3 문면은 오탐 4(전부 이름공간 `{% url 'ns:name' %}`)였고, v3.1 은 0 이다. 템플릿 주석(`{# #}`·`{% comment %}`)은 ①③ 전에 `mask_html` 이 공백으로 지운다 — 그래서 `java{# c #}script:` 는 ③ 이 아니라 ① «공백 제거 뒤 `javascript:`» 가 잡는다(규범 v3.1 nit-4 · K45b). 태그 출력 바로 뒤의 `:`(`{% url 'a' %}:{{ x }}`)와 `{{ host }}:{{ port }}/x` 도 스킴 자리로 보아 발견이다 — 드문 꼴이고 스킴 조립과 구별할 수 없으니 감수한다(검사기 v3.1 nit 3 · 교정은 주소 조립을 서버로). v3.2 재측정: spring_dream main·가지 머리 8·워크트리 8 의 URL 속성 전수에서 WP3 적중 0(§1-13). 사례 13개(차단 5 · 통과 8)는 모두 기대대로다 [실측 scratch `design-sdk/wp3/wp3_scheme.py`·`wp3_scheme.out` · 규범 M-1] ④ SVG `<set>`·`<animate>` 계열에서 `attributeName` 이 `href`·`xlink:href` 이면 금지. added 줄. 모든 경우 — 기존 틈(검사기 M5·m1 · P8·P15) | on*·hx-on·js:·조건식 |
| `mask_of` | `.js` 는 새 `mask_js`(`//`·`/* */` 주석만 마스킹 · 문자열·템플릿 리터럴 보존) | `.py`·`.css`·`.html` |
| WN8·WI·WP4~WP6·WS2~WS5·WS7·WS8 | 변경 없음 | — |

공용 상수·모듈:

- `common.py`: `VENDOR_DIR` · `SDK_REGISTRY` · `VENDOR_ATTRS_BYTES` · `LIB_CDN_HOSTS` · `LIB_CDN_PATHS` · `HOSTING_SUFFIXES` · `TRAP_TOKENS` · `SECRET_WORDS` · `BackstopContext.sdk`(지연 적재 · WV2 통과 집합 캐시)
- 새 `src/sdk_registry.py`(적재·정규화·결속·도메인·덫) · 새 `src/check_vendor.py`(WV1~WV13)

### 5-4. 빚 스캔 · 잔존 · 리팩토링

- **`debt.py`**
  - `scan` 은 대상별(§5-1)로 돈다 — 목록이 있으면 WV1·WV3·WV4·WV7·WV9·WV11, 등재 id 마다 WV2·WV5·WV6, 늘 WV13·WV8, 목록 시대 전의 미등재 단위마다 WV12. WV10 은 생략 notice 다.
  - **벤더 트리는 `debt_universe`(ls-files)가 아니라 os.walk 로 본다.** 디렉터리 심볼릭 링크 사본은 ls-files 우주에 파일로 없기 때문이다(P2 · D36). OS 잡파일 제외(§4-1)는 같은 규칙이다.
  - `debt-g0.json` 에 `scanner`(플러그인 판 · 검사 집합 해시)를 싣는다. `--debt-residual` 은 판이 다르면 exit 1 «판 경계 — G0 재스캔 필요»를 낸다. 옛 키 `WS6|static/vendor/` 가 새 판에서 사라져 «해소»로 세는 오판을 막는다(검사기 minor 9 · D38).
- **G0 배너 알림**(목록 시대 전의 미등재 벤더 단위가 있으면 · 목록 유무 무관): 빚 행 다음에 `미등재 벤더 단위: <id·파일 들>(WV12) — 입구: /dddjango-web:refactor web/static/vendor (또는 이 요청이 그 단위·그 사본을 부르는 화면에 닿으면 슬라이스 0 «기존 등록») · main 을 받는 레인의 diff 게이트 red 는 등록 착륙까지 남는다 · 이 사본이 든 가지는 merge 로 착륙(rebase·squash 면 늘 red)` 1행을 낸다(A25 앵커 · v3.2 끝 구절 — 검사기 v3.1 minor 1). 질문이 아니라 알림이다. 스캔 단위에 들면 보통 빚 질문이다.
- **기준점 뒤에 들어온 늘 red**(규범 R4): G0 동결 뒤(Phase 2 중 main 받기 등) 늘 검사가 red 가 되면, ⓡ1~ⓡ4 로 고칠 수 있는 것은 Coordinator 가 **언제든** 격리 커밋으로 고친다(승인 불요 · `sdk_commits`). 그 밖은 정지하고 입구를 안내한다(A20 근처 문장).
- **`refactor_audit.py`**
  - ① R0 대상 `web/static/vendor` 를 **«SDK 등재 정리 전용» 단위**로 받는다(규범 M9 — §6-8).
  - ② 영역 «영역 전속 정적»·«경계 교차» 판정에서 `static/vendor/**` 를 뺀다.
  - ③ 컨테이너 단위 범위에서 `sdk_registry.json` 을 뺀다(벤더 단위가 소유한다). `unit_of("sdk_registry.json")` 은 `static/vendor` 를 돌려준다(특례 — 빚 키 `WV1|sdk_registry.json` 류도 벤더 단위로 센다 · Coordinator step 4′ 단위 문구 A5 와 같은 뜻).
  - ④ `REF_PATHSPEC` 에 `:(exclude)web/static/vendor` 를 더한다(87 KB 한 줄 사본이 6a 참조 grep 에 들어가는 것 — 검사기 minor 10).
  - ⑤ 벤더 단위 plan 은 렌즈×조각 0(벤더 바이트는 의미 점검 대상이 아니다)이고 `check`·`check-verdict` 가 0 행으로 exit 0.
  - ⑥ 벤더 단위 R1: 등록할 항목의 `public_config.setting` 이 settings 에 없으면 그 항목은 `ⓐ 재상정` «기능 요청 — 공개 설정 배선»이다. 리팩토링은 배선을 하지 않는데, 이름 없이 등록하면 화면이 «설정 실패» 행으로 바뀌어 동작이 달라지기 때문이다(규범 N4).
  - `--self-test` 에 여섯 경우를 더한다.
- **`subst.py`**: 무관하다. WV10 이 `_chain`·`_approved_merges`·`_records` 를 import 해 재사용한다.
- **감사 범위**(규범 m8): W6m «touched» 와 슬라이스 감사는 목록·벤더에 대해 **격리만**(WV10 결과) 본다. discipline-reviewer-web 은 벤더 바이트를 읽지 않는다.

### 5-5. 도구 `scripts/sdk_vendor.py` · 자산 `assets/sdk_boundary.js`

```
python sdk_vendor.py candidate <루트> --id <id> --version <판> --source-url <https> --docs-url <https>
        [--from-file <로컬 사본>] [--docs-file <브라우저 저장 문서>] [--members-file <함수 열거 JSON>] --out <산출물 폴더>/sdk-candidates/<id>/
python sdk_vendor.py install <루트> <candidate.json> --entry <entry-draft.json> --approval-source "<꼴>"
        [--source-tokens "<덧붙일 낱말>"] --approved-at "<YYYY-MM-DD HH:MM +ZZZZ>" --gate "G1|G1'|G1(리팩토링)"
        --build <산출물 폴더> [--replace | --scope-add <global>.<이름공간>.* | <global>.<이름공간>.<data_out 함수> … | <global>.<이름공간>.<gateway 함수>:<경로> … | --register-existing <지금 경로>] [--dry-run]
python sdk_vendor.py verify <루트>          # WV1~WV6 · WV13 인프로세스 · 시안 증거 검사 없음 (검사기 B2) · 얕은 이력+미등재 단위면 exit 1 «판정 불가»(미실행)
python sdk_vendor.py restore <루트> <id>    # 승인 불요 복원: 다시 받은 바이트 = 등재 지문일 때만
python sdk_vendor.py remove <루트> <id>     # 항목 + vendor/<id>/ 디렉터리째
```

- **`candidate`**
  - 원본을 받는다(리다이렉트 추적 → `final_url` 호스트 ∈ 운영자 도메인 · 라이브러리 CDN 아님 — 아니면 exit 2).
  - HTML·빈 응답이면 exit 2 다.
  - **`docs_url` 을 직접 받아** `docs.html` 과 sha256 을 남긴다. `cites_source`(원문에 원본 경로가 있는가 · 아니면 exit 2)와 `integrity_from_docs` 를 판정한다. 문서의 SRI 는 sha384/256/512 다중을 받고, 원본 경로와 같은 문서에 같은 값이 있을 때만 `upstream_integrity` 를 채운다(규범 M4).
  - `--docs-file` 은 네트워크 불가·JS 렌더 문서일 때만 쓰고 `fetched_from=file` 표지를 남긴다(배너 1급).
  - `--from-file` 이면 `source_url` 을 다시 받아 byte 대조를 시도한다. 받지 못했고 문서 integrity 도 없으면 «출처 검증 없음(사용자 제공 파일)»을 1급 표지로 남기고, `install` 은 이 표지가 있으면 G1 배너 확인 문구를 요구한다(minor 8).
  - **함수 열거**(v3.2 · 규범 v3.1 m-2): `--members-file` 은 브라우저 도구가 사본을 더미 키로 init 해 센 이름공간별 함수 이름 JSON 이다. 열거하는 동안 로컬 밖 요청은 모두 막고, 막힌 요청 수를 그 파일에 남긴다 — 도구가 `candidate.json` 에 옮긴다(v3.3 · 규범 v3.2 n3). `api-paths.txt` 는 `gateway_paths` 의 경로 목록이 된다. 도구는 이름마다 사본 바이트(`mask_js` 로 주석을 지운 코드)에 그 식별자가 실재하는지 보고, 없으면 exit 2 다. 파일이 없으면 Coordinator 가 운영자 문서 API 참조에서 옮긴 표를 draft 에 넣고, 도구는 같은 실재 대조를 한 뒤 «함수 표 출처: 문서» 1급 표지를 남긴다. 분류의 이름 바닥(§3-2)은 `install` 이 강제한다.
  - **낱말 표 닻**(규범 m-b): `install --dry-run` 이 `namespace_words` 낱말마다 저장한 `docs.html`(과 Coordinator 가 `--docs-file` 로 함께 남긴 기능별 운영자 문서)에서 등장 수를 세어 G1 배너에 보이고, 0회 낱말은 1급 표시한다(«운영자 문서에 없는 낱말»). 거절은 WV1 의 꼴 규칙이 맡고, 등장 수는 사람이 보는 닻이다.
  - 산출: `license-header.txt` · `origins`(전수 · operator/operator_in_code/other — `mask_js` 로 주석을 지운 코드 기준) · `features_in_file`(`this.<X>=` 정적 추정 · 그 밖은 evidence 수동) · API 경로 목록(`api-paths.txt`) · 로더 표지 수 · `fetched_at` · **`candidate_token`**(`<id>@<판>#<sha12>` — G1 배너·질문문에 그대로 보인다).
- **`install`**
  - 해시·크기·origins·증거·표지는 `candidate.json` 에서만 가져온다. 사람 칸은 draft 에서만 가져오고, 모르는 칸은 거절한다. 두 입력 파일도 같은 엄격 파서(중복 키·NaN 거절 · NFC)로 읽는다(검사기 nit 1).
  - 출처 검사(§3-4 — 필수 낱말은 도구가 만든다)를 한다. 미등재 형제 디렉터리는 거절하지 않고 배너 줄로 남긴다(§3-3 4). 정규 바이트로 쓴다. `.gitattributes` 를 둔다.
  - `--replace` 는 옛 사본을 정리한다. `--scope-add` 는 새 이름공간 묶음 · `data_out` 함수 이름 · gateway 경로 단위(`Kakao.API.request:<경로>`)를 받는다. 한 번에 여럿을 받으면 1결정 줄로 묶는다(같은 이름공간 안 `call`·`lifecycle` 함수는 이미 덮인다 · `sdk_ui` 는 거절 · gateway 경로는 `gateway_paths` 에 있어야 한다). `--register-existing` 은 지금 경로 바이트 = 후보 바이트일 때만 받는다(벤더 칸으로 옮기는 복사 — 옛 경로 삭제·태그 치환은 coder 슬라이스 0).
  - 쓴 뒤 `verify` 를 하고, 실패하면 되돌린 뒤 exit 2 다. 재실행은 멱등이다.
- **`verify`**: §5-2 의 늘 검사(WV1~WV6·WV13)만 돌고, 시안 증거(`check_design_evidence`)를 부르지 않는다. 과거 빌드가 있어도 exit 0 이 가능하다(검사기 B2 · K37). 인덱스 항목이 없으면(설치 직후·커밋 전) WV2 ④ 는 건너뛴다. 커밋 여부는 G2 의 WV10 (e)가 본다(minor m1). 병합하는 쪽의 확인 명령이기도 하다(§3-7).
- **`restore`**: `source_url` 바이트가 등재 sha256·sha384 와 같을 때만 사본을 되쓴다. 승인 불요다(승인된 상태로의 복원). 목록 재정규화(ⓡ2 — NFC 포함)도 한다.
- **`remove`**: 저장소 전체 템플릿에 참조가 남았으면 exit 2 다. 항목과 `vendor/<id>/` 를 함께 지운다.
- **`assets/sdk_boundary.js`**(새 · byte 미러): G2 가로채기 스니펫이다(§7-6). 승인 이름공간의 함수를 분류표대로 다루고(v3.2 — `lifecycle` 은 원본 그대로 · 그 밖은 기록기 · 표에 없는 함수·`sdk_ui` 호출·파일 인자 표지 · v3.3 — gateway 의 실제 `url` 을 승인 경로와 대조), 운영자 대상 `window.open`·폼 제출(`HTMLFormElement.prototype.submit`·`requestSubmit`·`submit` 이벤트) 기록 전용 래퍼를 포함한다. 제품 코드가 아니고 web/ 에 들어가지 않는다. 시제품은 scratch `design-sdk/v33/browser/sdk_boundary_v33.js` 다(v3.1 판의 실브라우저 E2~E4 · L1 · RT · sendScrap, v3.2 판의 분류 실측 `run4.out` 위에 gateway 실측 `run6.out`).

### 5-6. 픽스처

`fixtures_sdk.sh`(새):

| id | 경우 | 기대 |
|---|---|---|
| K1 | 정상 등재 + `.gitattributes` + 페이지 블록 안 SDK 태그(기능 JS 앞) + 키 `{{ }}` | exit 0 · `verify` 0 |
| K2 | 사본 1바이트 수정(기준점 이전 · gated) / 운영자 sha384 불일치 | WV2 1 / 1 — gated 에서도 |
| K3 | 결속 뒤 `service_api` 만 수정 / `source`=«발주 고정 ⓐ …» / `at` 시간대 없음 | WV3 ×3 |
| K4 | `http` 원본 · 원본 호스트가 운영자 밖 · sha 꼴 · `file` 이 `static/js/` · 모르는 칸 `waiver` | WV1 ×5 |
| K5 | id `html2canvas` / 짝 `kakao_js_sdk` | WV4 1 / 0 |
| K6 | 목록 있음(`kakao_js_sdk` 등재) + 이번 실행에 `static/vendor/html2canvas/html2canvas.min.js`(미등재 디렉터리) · `static/vendor/readme.txt`(직속) · `static/vendor/kakao_js_sdk/2.8.3/x.js`(등재 id 안 하위) 추가 | WV5 1(등재 id 안) + **WV13 ×2**(목록 시대에 생긴 미등재 단위 — v3.1) + WS6 ×3 + WP1 ×2 |
| K7 | `web/sdk_registry.json` / `web/vendor.json` | WS1 0 / 1 |
| K8 | 벤더 태그가 기능 JS 뒤 · base block 뒤 · `async` · `type=module` · `nomodule` · base+page 중복(페이지 파일에 1) | WP2 ×6 / 짝 0 |
| K9 | 이번 실행이 목록을 지움(사본·태그는 기준점 이전) — 슬라이스 커밋 / 미커밋 | WV13 1 + WV10 1 / WV13 1 + WV10 1 |
| K10 | `Kakao.init("abc")` added / dataset / 기준점 이전 리터럴 | WV7 1 / 0 / 0 |
| K11 | 슬라이스 커밋이 목록+템플릿 · 기록된 `sdk_commits` 격리 · 슬라이스에 기록된 목록 단독 커밋 · 승인 병합의 목록 변경 · 승인 밖 병합의 목록 변경(v3 — 상류 몫 notice) | WV10 1 · 0 · 1 · 0 · notice 0 |
| K12 | `.gitignore` 의 `*.min.js` | `install` exit 2 · WV2 |
| K13 | 무관 체제 + `static/js/html2canvas.min.js` + CDN 태그(회귀) | 오늘과 같은 WP1·WP2 |
| K14 | `candidate --from-file` 문서 integrity 일치 / 불일치 / `http` 원본 | 0 / 2 / 1 |
| K15 | `install --dry-run` 쓰기 0 · 정규 바이트 · 멱등 · 출처 «대리 답» | 0 · 0 · 동일 · exit 1 |
| K16 | `--replace` 에 직전과 같은 출처 / 새 판을 담은 새 원문 / 파일 이름 바뀜 / 원문에 판·표지 없음(시각만 늦음) / HEAD 조상이 아닌 커밋의 원문 / `web/` 안 원문 / 필수 낱말을 Coordinator 토큰으로만 채움 | exit 1 / 0 / 옛 사본 제거 / 1 / 1 / 1 / 1 |
| K17 | 저장소 템플릿 참조가 남은 `remove` / 참조 제거 뒤 / 마지막 항목 | 2 / 0 / 목록·vendor 제거 |
| K18 | 문서 원문에 원본 경로·integrity 있음 / 원본 경로 없음 / `--docs-file` | integrity 채움 / exit 2 / `fetched_from=file` |
| K19 | 벤더 파일 심볼릭 링크(바이트 동일 외부 파일) | WV2(링크·모드 120000) |
| K20 | `vendor/<id>` 디렉터리 심볼릭 링크 · 태그 무변 레인 | WV2·WV5 — gated 에서도 |
| K21 | 상위 `.gitattributes` 가 `text=auto`·`eol=crlf`·`filter=` 를 걸고 vendor 표지가 지워짐 | `install` exit 2 · WV2 ×3 |
| K22 | 디스크 `Kakao.min.js` · 등재 `kakao.min.js`(대소문자 무시 FS) | WV2·WV5 |
| K23 | 중복 키(항목·칸) · 비정규 바이트 · `size: true` · `NaN` | WV1 ×4 |
| K24 | 등재 `file` 을 새 파일로 돌리고 옛 파일 변조·잔존·참조(P13) | WV5 1 + WV6 1 |
| K25a | **목록 없음** + 기준점 이전 벤더 사본·태그(P14) · 무관 레인 | gated 0 · 빚 WV12+WS6+WP1+WP2(미룰 수 있음) · G0 알림 1행 |
| K25b | 같은 사본(목록 시대 전 바이트) + 다른 SDK 가 등재된 목록(병합 유입) | **늘 0**(v3.1 — 목록 시대 전의 미등재 단위는 등재 전 의미론) · 빚 WV12 + G0 알림 |
| K25c | K25a 상태에서 다른 SDK `install` | exit 0 · 배너 줄 «미등재 벤더 디렉터리 1» |
| K26 | `file` 디렉터리 ≠ id · 두 항목이 같은 `file` | WV1 ×2 |
| K27 | `evilkakaocdn.net` · `kakao.com@evil` · `:8443` · 대문자 · 끝점 · 단일 라벨 `com` · jsdelivr 원본 · `/ajax/libs/` 원본 | WV1/WV4 ×8 |
| K28 | 승인 뒤 `public_config`·`source_url` 만 바뀜 | WV3 |
| K29 | `setting` = `SECRET_KEY` / `KAKAO_ADMIN_KEY` | WV1 ×2 |
| K30 | `href="javascript:…"` · `&#106;avascript:` · `xlink:href="javascript:…"` · `srcdoc="&lt;script&gt;…"` | WP3 ×4 |
| K31 | `data-kakao-javascript-key="리터럴"` / `{{ state.kakao_javascript_key }}` | WV7 1 / 0 |
| K32 | 기능 JS `createElement('script')`+src · `import('https://…')` · 운영자 호스트 리터럴 · `setTimeout("…")` | WV8 ×4 — 무관 체제에서도 |
| K33 | `Kakao?.init('k')` · `Kakao.init( "k")` · `Kakao["init"]("k")` / 주석 `// Kakao.init("YOUR_KEY")` | WV7 ×3 / 0 |
| K34 | 벤더 태그가 section 조각 · `{% static 'vendor/…' %}` · 하드코딩 `/static/web/vendor/…` · 페이지 block 밖 | WP2·WV6 ×4 |
| K35 | 기능 JS 태그만 added 인데 기준점 이전 벤더 태그보다 앞 · base 만 added 인 base+page 중복 | WP2 ×2 |
| K36 | rebase/ff 로 받은 main 혼합 커밋 · evil merge 의 목록 변경 · 다른 빌드의 `chore(web-sdk):` 커밋 | notice · WV10 1 · notice |
| K37 | `sdk_vendor.py verify` + 과거 시안 빌드 존재 | exit 0 |
| K38 | `candidate`: 리다이렉트로 운영자 밖 · `--from-file` 무증거 · HTML 응답 · 빈 응답 · 확장자 없는 원본 | 2 · 표지 · 2 · 2 · `<id>.js` |
| K39 | `use_scope`=`Kakao.Share.*` 에서 `Kakao.Auth.login(` added / `Kakao.Share.sendScrap(`(같은 이름공간) · `--scope-add Kakao.Auth.*` 출처 줄에 «카카오 로그인» 있음(판 없음) / 없음 / «로그인»만 있고 운영자 낱말 없음 | WV9 1 / 0 · exit 0 / 1 / 1 |
| K40 | 깨끗한 vendor 에서 레인 X `install` + 미등재 사본 레인 Y(목록 시대 전에 갈라짐) · 충돌 없는 병합(검사기 N1) | 늘 0 · 빚 WV12 + G0 알림 |
| K41 | 등재 id 안 바꿔치기(P13) — N1 교정 뒤 회귀 보호 | WV5 1 + WV6 1 |
| K42 | 빌드 기록 없음(트리비얼 · `--diff-base <편집 직전 HEAD>`)에서 목록 삭제 + 사본 변조 / 항목만 삭제 + 사본 변조 / 삭제 커밋을 rebase 로 받은 레인 / 정상 `remove`(디렉터리째) / 재채택 | WV13 2(남은 두 단위) / 1 / 1 / 0 / 0 |
| K48 | 빌드 기록 없음: 항목 삭제 + `vendor/<id>/` 개명 + 변조 + 로드 줄 치환(검사기 V3-3) | WV13 1(개명된 단위) |
| K48b | `--register-existing` 으로 등록한(바이트가 목록 이전부터 있던) SDK 의 항목 삭제 + 디렉터리 개명(바이트 그대로) / + 변조(검사기 v3.1 nit 1) | WV13 1 / 1 — v3.1 은 앞쪽이 WV12 [실측 `design-sdk/v32/v32_probes.out`] |
| K49 | main 병합 해소가 목록 항목만 떨어뜨리고 디렉터리를 남겨 변조(빌드 기록 없음 · 검사기 V3-2) | WV13 1(`--full-history`) |
| K50 | K40 변형 — 목록 시대 전 갈라진 레인의 평면 사본 `vendor/kakao.min.js` + 다른 레인의 설치 · 충돌 없는 병합(검사기 V3-1) | 늘 0 · WV12 + G0 알림 |
| K50b | 같은 이름의 등재 전 사본이 제거 뒤 병합으로 들어옴(검사기 nit 2) | 늘 0 · WV12 |
| K50c | K40 의 미등재 사본 가지(목록 이전 분기)를 squash / rebase / cherry-pick 으로 착륙 · G0 알림 문구(검사기 v3.1 minor 1) | WV13 1 ×3(고지대로) · 알림 끝 구절 «merge 로 착륙» [실측 `v32_probes.out`] |
| K50d | K50 현장 꼴 — 목록 이전 평면·디렉터리 임시 사본 = 나중에 main 이 등재한 바이트 · merge | 늘 0 · WV12 ×1 씩(같은 경로의 목록 이전 탄생 — 이력상 등재 바이트 규칙의 예외) [실측 `v32_probes.out`] |
| K50e | 목록 이전 레인 Y 의 임시 사본 `vendor/kakao_tmp/kakao.min.js` + 로드 줄 · 그사이 main 이 같은 바이트를 등록하고 판 올림 · Y 를 merge / §6-8 #6b 치환 정리 뒤 | WV13 1(참조 중 — ⓡ4 불가) / 0 [검토자 실측 `review-sdk-tool/v33_probes.out` — «판 올림 뒤 옛 임시 사본 merge=WV13»] |
| K51 | 미등재 파일 200개 단위 · 목록 이력 없음 / 있음 / 얕은 클론(검사기 v3.1 minor 3 · nit 4) | WV12 · git 걸음 0 · 1 s 미만 / WV12 · 걸음 1 · 1 s 미만 / exit 1 «판정 불가»(미실행) [실측 0.05 s / 0.13 s · v3.3 재실행 0.04 s / 0.15 s] |
| K43 | 등재 + `vendor/.DS_Store`·`vendor/<id>/.DS_Store`(무시) / 목록 없음 + `.DS_Store` 만에서 `install` / 추적된 `.DS_Store` | 0 / exit 0(배너 줄 0) / WV5 1 |
| K44 | 등재 id 안 무시된 파일을 템플릿이 가리킴 | WV6 1(+ 잡파일 목록 밖이면 WV5 1) |
| K45 | `href="java{{ '' }}script:…"` · `href="{% if 1 %}javascript{% endif %}:…"` · `href="{{ 'javascript' }}:x"` · `href="{{ scheme }}://…"` · SVG `<set attributeName="href" to="javascript:…">` / 짝 `href="{% url 'x' %}"` · `href="{{ state.url }}"` · **`action="{% url 'auth:login' %}"`(태그 안 이름공간 `:`)** · `href="{% url 'x' %}?t=12:30"` · `href="{{ base }}/a:b"` | WP3 ×5 / 0 |
| K45+ | `href="{{ 'javascript' }}&#58;K.init('k')"` · `href="java{{ '' }}script&colon;x"` / 짝 `href="{% url 'x' %}?t=10:00"` | WP3 ×2 / 0 [실측 — 검토자 `v3_probes.py` 의 WP3 표본 7개를 v3.1 ③ 으로 다시 돌려 놓침 0 · 오탐 0 · `design-sdk/v31/v31_probes.out`] |
| K46 | 기능 JS `createElement("SCRIPT")` · `` createElement(`script`) `` · `createElement(t)` · `createContextualFragment('<script …>')` · `.then(eval)` · 목록 없는 프로젝트의 `'https://t1.kakaocdn.net/…'` 리터럴 / 짝 `createElementNS("http://www.w3.org/2000/svg", "path")` | WV8 ×6 / 0 |
| K46+ | `createElement('scr'+'ipt')` + `['https:','','t1.kakaocdn.net','x.js'].join('/')` · `` `https:/${'/'}${h}.net/kakao.min.js` `` · `createElement("script")` 로 JSON 담기 / 짝 `["http:", "https:"].includes(url.protocol)` · `createElement('li')` | WV8 ×3 / 0 [실측 `design-sdk/v31/v31_probes.out` — 표본 9: 놓침 0 · 오탐 0] |
| K47 | 레지스트리 문자열 NFD(같은 내용 NFC 와 다른 바이트) / `restore` 뒤 | WV1 1 / 0 |
| K45b | `href="{% url 'a' %}:{{ x }}"` · `href="{{ host }}:{{ port }}/x"`(감수하는 발견) / `href="java{# c #}script:x"`(주석 마스킹 뒤 ①) | WP3 ×2 / 1 |
| K46b | v3.2 짝 `'wss://' + location.host` · `` `wss://${location.host}/ws` `` · `startsWith('https://')` · `querySelector('li.me')`·`'div.app'`·`'li.msg.me'` · `'socket.io'` · `'https://' + location.host + path` / 덫 `fetch('\x68ttps://kapi.kakao.com/…')` · `f.src='\x68ttps://evil.example/'` · `createElement('\x73cript')` · `'help@spring.co.kr'` · `'https://' + 'kapi.kakao.com'` | WV8 0 / ×5 [실측 `design-sdk/v32/wv8_v32.out` — 표본 27 어긋남 0 · v3.3 부터 단독 `'cdn.socket.io'` 는 문면 한계(K46c)] |
| K52 | `use_scope`=`Kakao.Share.*` 에서 added `Kakao.Share.uploadImage(` / 같은 줄 + 이름 지정 원소 `Kakao.Share.uploadImage` / `Kakao.Share.createDefaultButton(`(묶음 있음) / `Kakao.Share.cleanup(` / `Kakao.Share.fooBar(`(표에 없음) | WV9 1 / 0 / 1 / 0 / 1 |
| K46c | v3.3 싱크·② 정리: `createElementNS('http://www.w3.org/1999/xhtml', 'script')` · `createElementNS('http://www.w3.org/2000/svg', 'script')` · `createElementNS(NS, tag)` · `f.srcdoc = '<scr' + 'ipt …'` · `f.setAttribute('srcdoc', html)` · `document.write('<script …')` · `frame.contentDocument.writeln(html)` · `fetch('https://' + 'myapi.dev' + '/v1')` · `fetch('https://' + 'i.cdn.io' + '/x')` · `'//i.cdn.io/x.js'` · `'cdn.socket.io/x.js'` · `fetch('\150ttps://kapi.kakao.com/v2')` · `` fetch(`https://${'kapi.kakao.com'}/v2/user/me`) `` / 짝 `createElementNS(SVG_NS, 'path')` · `navigator.clipboard.write([item])` · `f.srcdoc === ''` · `'auth.user.me'` · `t('nav.about.me')` / 문면 한계 단독 `'i.cdn.io'`·`'myapi.dev'`·`'cdn.socket.io'` | WV8 ×13 / 0 / 0 [실측 `design-sdk/v33/wv8_v33.out` — 표본 47 어긋남 0] |
| K48c | 등록 SDK 바이트를 목록 이전 임시 자리(같은 경로)로 되돌려 개명 + 항목 삭제 / 마지막 `remove` 뒤 새 미등재 사본(검사기 v3.2 nit 둘) | WV13 1(v3.2 는 WV12) / WV13 1(의도 — 목록 시대는 끝나지 않는다) [실측 `design-sdk/v33/v33_probes.out`] |
| K52b | `use_scope` 에 `Kakao.API.request:/v2/user/me` 만: added `Kakao.API.request({url: '/v2/user/me'})` / `{url: '/v1/api/talk/friends/message/default/send'}` / `{url: path}`(비리터럴) / `use_scope` 에 `Kakao.API.*` 묶음 · `Kakao.API.request` 이름 원소 | WV9 0 / 1 / 1 / WV1 ×2(gateway 는 경로 원소로만) |
| K53b | 바닥: `request: "call"` / 경로 `/v1/user/unlink: "read"` / 토큰 짝 `restoreSession: "call"`·`outputText: "call"`·`inputValue: "call"` / `putObject: "call"` | WV1 1 / 1 / 0 / 1 [바닥 실측 `design-sdk/v33/floors.out`] |
| K53 | 분류표에서 `uploadImage: "call"`(바닥 아래) / `use_scope` 에 `Kakao.Share.createDefaultButton` / 이름 지정 원소가 `call` 함수(`Kakao.Share.sendDefault`) / 묶음 이름공간의 분류표 없음 / 낱말 표 키 `Share.uploadImage` 의 낱말이 «카카오»(운영자 토큰) | WV1 ×5 |

`fixtures_debt.sh`:

| id | 경우 | 기대 |
|---|---|---|
| D30 | 정상 등재 | WV 키 0 |
| D31 | 사용처 0 | `WV11|…`(미룰 수 있음) |
| D32 | 지문 불일치 | `WV2|…` · `undeferrable` · exit 2 |
| D33 | 빚 스캔 | «WV10 빚 모드 생략» notice |
| D34 | `--debt-residual` 에서 ⓐ WV2 복원 | 잔존 0 |
| D35 | `--refactor` | D31·D32 와 같은 키 |
| D36 | 디렉터리 심볼릭 링크 벤더(ls-files 우주에 없음) | `WV2`·`WV5` 키 · `undeferrable` |
| D37 | 목록 없는 벤더 사본 | `WV12|static/vendor/` + WS6/WP1(미룰 수 있음) · notice |
| D38 | `--debt-residual` · `debt-g0.json` `scanner` 판이 다름 | exit 1 «판 경계» |

`refactor_audit.py --self-test`(R+):

- R0 `web/static/vendor` 수용(등재 정리 전용)
- 벤더 단위 plan 렌즈×조각 0 · `check`/`check-verdict` 0 행 exit 0
- 영역 plan 이 벤더를 «영역 전속 정적»에서 뺌
- 컨테이너 plan 이 목록을 뺌
- `REF_PATHSPEC` 벤더 제외
- 벤더 단위 R1: `public_config.setting` 이 settings 에 없는 등록 항목은 `ⓐ 재상정` «기능 요청 — 공개 설정 배선»

리허설 고정 항목(R — 실제 브라우저 · scratch · §11-2 ③):

| id | 경우 | 기대 |
|---|---|---|
| **R4** | 실물 `sendDefault`(가로채기 없음)의 팝업 폼 POST · v3 스니펫 클릭 · 기록 인자로 실물 1회(인자 검증) · 옛 참조 우회 | `page.route` 기록 0 · `context.route` 가 운영자 요청을 받아 abort / 기록기 1 · `userActivation` 참 / 예외 0 · `window.open`·폼 기록 각 1 / 기록기 0 · 폼 기록 1 — 모든 경우 운영자 실제 요청 0 · 팝업 0(스니펫이 있을 때) [v3 실측 `design-sdk/browser/run.out` E1~E4] |
| **R4++** | 분류표 설치(실제 카카오 2.8.3) — 클릭 · 제품의 `Share.cleanup()` · `uploadImage({file: FileList})` · `createDefaultButton` · 표에서 함수 하나를 뺀 설치 | `cleanup` 원본 그대로(기록기 9) · 호출형 기록 1 불변 / data_out 기록 · 파일 인자 참 / sdk_ui 기록(발견) / «표에 없는 함수 Share.scrapImage»(발견) · 운영자 요청 0 · 팝업 0 [v3.2 실측 `design-sdk/v32/browser/run4.out`] |
| **R5** | 외부 요청 귀속 — 템플릿 외부 script·iframe · 제3자 스크립트의 fetch·script · 기능 JS 의 외부 fetch(이스케이프)·조립 script·iframe·WebSocket·sendBeacon·EventSource·XHR·타이머·프라미스 · 사용자 링크 이동·팝업 · 프로젝트 CDN 그림 · 같은 출처 | 기능 JS 몫 11건 발견(시작 스택에 기능 JS 8 · 시작 스택 없음 3) · 템플릿·제3자·사용자 이동 5건과 팝업 2 는 기록만 · 셈 밖 2 [v3.2 실측 `design-sdk/v32/browser/run5.out`] |
| **R6** | gateway 기록기 — `API.request({url: '/v2/user/me'})`(허용) · `{url: '/v1/api/talk/friends/message/default/send'}`(허용 밖) · 분류표에 `API.cleanup` 을 빼고 설치 / 같은 출처 미등재 vendor 를 `createElementNS(XHTML,'script')` 로 부름 | `pathOk` 참 / 거짓(발견) / «표에 없는 함수»(발견) · 운영자 요청 0 [v3.3 실측 `design-sdk/v33/browser/run6.out`] / 시작 스택에 기능 JS 가 있는 `Script` → 발견(같은 출처) [`design-sdk/v33/browser/run5.out` b15] |
| **R4+** | 늦은 초기화(클릭 때 init) 페이지 — init 감싸기 경로 · 같은 이름공간의 다른 함수(`Share.sendScrap`) · «SDK 만 막기» case 뒤 라우트 해제·새로고침한 다음 case | `path=[init-wrapped, patched:…]` · `thisOk=[true]` · 기록기 1 · `userActivation` 참 / 기록기에 `Share.sendScrap` · 운영자 요청 0 / 다음 case 에서 SDK 로드됨 · 래퍼는 새로고침으로 사라져 다시 설치 [v3.1 실측 `design-sdk/browser/run2.out`·`run3.out`] |

변이 검사(§11-2): WV5·WV6 비활성 · WV2 ②④⑤ 각각 제거 · 중복 키 허용 · `entry_sha256` 무시 · WV10 (b) 제거 · 대상 판정을 «목록이 있으면 vendor 전부 늘»로 넓힘(K40·K25b·K50 가 red 여야 한다) · 미등재 단위에 시대 판정 없이 늘을 걺(K25a·K50b) · **직속 파일을 WV5 늘로 되돌림(K50 red)** · **WV13 을 v3 의 «id 이름 이력»으로 되돌림(K48 red · K50b 오탐)** · **`--full-history` 제거(K49 red)** · OS 잡파일 제외 제거(K43 red) · NFC 정규화 제거(K47 red) · 대리 출처 필수 낱말을 Coordinator 토큰으로 되돌림(K16 red) · **WP3 ③ 의 태그 밖 판정 제거(K45 짝 red)** · 컨텍스트 경로를 page 경로로 되돌림 · 폼 래퍼 제거(R4 red) · **스니펫을 함수 목록 기록으로 되돌림(R4+ red)** · **case 사이 라우트 해제 생략(R4+ red)** · **`-m` 제거(목록 이전 병합 해소 사본 오분류)** · **이력상 등재 바이트 규칙 제거(K48b red)** · **단락 제거(K51 시간 상한 red)** · **얕은 이력 «판정 불가» 대신 보수적 WV13(K51 red)** · **`data_out` 이름 바닥 제거(K53 red)** · **WV9 의 분류 대조 제거(K52 red)** · **수명 함수를 기록기로(R4++ red)** · **시작 스택 없는 요청을 기록만으로(R5 red)** · **WV8 이스케이프 해제 제거(K46b red)** · **gateway 를 묶음으로 덮음(K52b red)** · **camelCase 토큰 대신 부분 문자열 바닥(K53b 짝 red)** · **③ 에서 `createElementNS` 제외 · ④ 에서 `srcdoc`·`document.write` 제외 · 이어 붙이기 접기 제거(K46c red)** · **약한 최상위의 URL 문맥 조건 제거(K46c 짝 `'auth.user.me'` red)** · **지금 목록 sha 구분 제거(K48c red)** · **같은 출처 script 를 셈 밖으로(R6 red)**. 각 변이에서 해당 픽스처가 red 인지 본다.

## 6. Coordinator 흐름

### 6-1. 언제

| 시점 | 할 수 있는 일 |
|---|---|
| G0 | 채택하지 않는다. step 1 host 상태에 «승인된 SDK(id·판·`use_scope` 묶음)·CSP 유무·프로젝트 정적/미디어 CDN 출처»를 적는다. 목록·벤더에 미커밋 변경이 있으면 «그대로 진행»을 받지 않는다(A24). 미등재 벤더 디렉터리가 있으면 G0 알림 1행(A25)을 낸다. 플랫폼 결과가 예견되면 scope 에 «SDK 필요 가능»만 적는다 |
| Phase 1 | **유일한 새 채택·판 올림·이름공간 범위 넓힘 자리**다. 후보 사실은 architect 호출과 병렬로 모을 수 있다 |
| Phase 2 | 코더가 «SDK 필요»를 보고하면 설계 반송 → G1′. 설치는 격리 커밋(WV10 이 `sdk_commits` 로 받는다). 기준점 뒤에 들어온 늘 red 는 ⓡ 로 언제든 고치거나 정지·입구(§5-4) |
| 리팩토링 | 새 채택·범위 넓힘 없음. 벤더 단위 대상이면 «기존 등록»·복원·미사용 제거(§6-8). 대상과 무관한 늘 red 는 ⓡ 로 고치거나 정지 |
| 트리비얼 | 채택 없음. **늘 red 를 만나면 수정 모드로 승격**한다(A16 · 규범 R4) |

### 6-2. 후보 사실 수집

- `candidate` → `sdk-candidates/<id>/`(`candidate.json`·`docs.html`·`license-header.txt`·`api-paths.txt`·임시 사본) 이 생긴다. 도구가 `candidate_token` 을 만든다.
- Coordinator 는 인용·URL 을 `evidence.md` 에 쓴다. 리뷰어는 인용이 `docs.html` 에 실재하는지 grep 으로 대조한다(규범 M4).
- 사람 판단 칸은 `entry-draft.json` 이다. `use_scope` 는 명세 SDK 사용 표의 «쓰는 SDK 기능 묶음»(핵심 함수 + `<이름공간>.*`)과 같다. `namespace_words` 는 운영자 문서의 기능 이름에서 이름공간마다 뽑는다(카카오: `Share`=공유·카카오톡 공유 · `Auth`=로그인·카카오 로그인 · `API`=사용자 정보·메시지·친구 · `Channel`=채널 · `Navi`=내비 · `Cert`=인증·전자서명 · `Picker`=친구 고르기·친구 선택 — 규범 N3 대응표). `lifecycle` 은 문서·정적 추출·필요하면 빈 페이지 탐침으로 정한다(«호출 대상이 언제 생기나» — 검사기 M7).

### 6-3. SDK 채택 확인 · G1 배너 줄 · 질문

**SDK 채택 확인**(A8 새 문단 — verify-web 대조 표지는 이 문단 머리 `**SDK 채택 확인(G1 배너 직전` 뿐이다 · n3). 다음을 모두 확인해야 G1 배너를 낸다.

- ① `install --dry-run` exit 0
- ② 임시 사본 재해시 일치
- ③ design-review-web 항목 12 blocker 0
- ④ 스캔 단위에 `web/static/vendor/`·컨테이너
- ⑤ 공개 설정 이름의 settings 존재 여부와 배선 계획
- ⑥ host CSP 가 있으면 등재 호스트로 필요한 지시문(`connect-src`·`form-action`·`frame-src`)을 대조한다(규범 m9)

**배너 줄**(사실만 · 무결성 출처 명시):

```
새 SDK 채택: kakao_js_sdk 2.8.3 · 표지 kakao_js_sdk@2.8.3#b2ff7b30deff · 운영자 Kakao Corp.(kakao.com·kakaocdn.net)
  · 원본 https://t1.kakaocdn.net/kakao_js_sdk/2.8.3/kakao.min.js · 운영자 문서 인용 확인(docs.html sha256 <앞 12>)
  · 무결성: 운영자 문서 공개 sha384 와 일치 · 지문 sha256 b2ff7b30deff · 87,110 B · Apache-2.0 · 약관 <URL>
  · 낱말 표(범위 넓힘 출처 대조용 · 운영자 문서 등장 수): Share=공유·카카오톡 공유 · Auth=로그인·카카오 로그인 · API=사용자 정보·메시지·친구 · …(0회 낱말 없음)
  · 쓰는 기능 묶음(승인 범위): 핵심(Kakao.init · Kakao.isInitialized) · Share(카카오톡 공유 — 묶음이 덮는 함수 sendDefault·sendCustom·sendScrap · 수명 cleanup) — 이번에 부르는 함수 Share.sendDefault
  · 같은 묶음 안 범위 밖 함수: 사용자 자료를 카카오 저장소로 보냄 uploadImage·scrapImage·deleteImage(올린 그림 100일 보관 · 저장 경로 /v2/api/talk/message/image/upload·scrap·delete — 쓰려면 이름마다 다시 묻는다)
      · SDK 가 그리는 단추 createDefaultButton·createCustomButton·createScrapButton(쓰지 않음) · 함수 표 출처: 실행 열거(운영자 호스트 차단)
  · 파일이 함께 담은 기능 묶음(승인 범위 밖 — 쓰려면 묶음마다 다시 묻는다): Auth(로그인) · API(사용자 정보·메시지) · Channel(채널) · Navi(내비) · Cert(인증) · Picker(친구 고르기)
      · API 는 경로를 인자로 받는 범용 함수 request 하나다 — 경로 30(data_out 16: 친구 메시지 발송 · 그림 올리기 · 연결 끊기 … / read 14: 사용자 정보 /v2/user/me … — api-paths.txt) · 쓰려면 경로마다 묻는다
  · 접속 호스트 16: 카카오 12(accounts·apps·cert-sign-fe·developers·friend-picker·kakaonavi·kapi·kauth·ocert·pf·sharer·talk-apps · 모두 코드 안)
      · 그 밖 4(github.com·itunes.apple.com·openjsf.org·www.apache.org — 머리 주석·번들 라이브러리 링크)
  · 필요한 까닭: 카카오톡 카드 공유는 JS SDK 로만(REST 미지원 — <URL>)
  · 공개 설정 KAKAO_JAVASCRIPT_KEY(settings 에 없음 → 선택형 추가 · JavaScript 키만 — Admin 키 금지 · 운영 env 필요)
  · 미등재 벤더 디렉터리: 없음 | <id 들>(이관 항목 — 입구 …) · CSP: 없음 · 후보 <산출물 폴더>/sdk-candidates/kakao_js_sdk/
```

- 무결성이 문서에서 오지 않았으면 «무결성: 운영자 공개 값 없음/문서 인용 미확인 — 다시 받은 바이트와 대조함|대조 못 함»으로 적고, «일치»라는 말을 쓰지 않는다(규범 M4).
- `fetched_from=file`·«출처 검증 없음»은 1급 표시다.

**질문**(명세 승인과 따로 · 쉬운 말):

> 카카오가 직접 배포하는 도구(2.8.3 · 표지 `kakao_js_sdk@2.8.3#b2ff7b30deff`)를 들일까요? 이번에는 카카오톡 카드 공유에만 씁니다. 이 파일에는 카카오 로그인·사용자 정보·친구에게 메시지·채널·인증 기능도 들어 있지만, 그 기능은 승인 범위가 아니라서 쓰려면 다시 묻습니다. 공유 기능 안에 있는 «사용자 사진을 카카오 서버에 올리는 기능»도 승인 범위가 아니라서 쓰려면 다시 묻습니다. 승인하면 우리 서버에 사본을 두고, 이 프로젝트의 다음 작업들은 같은 범위(공유) 안에서 다시 묻지 않고 씁니다. 판을 올릴 때는 다시 묻습니다.
> 선택지: **승인** / **기각 — 이 도구 없이 다시 설계** (+ 기타)

- 출처·위임은 §3-4 다. 결정 줄은 `SDK 채택 승인: kakao_js_sdk 2.8.3 b2ff7b30deff · 묶음 (core),Share · 출처 = …` 꼴이다.
- SDK 기각이면 같은 배너의 명세 승인 답은 무효다.
- **범위 넓힘 줄**(이후 레인 · §3-5): 새 이름공간이면 1문항 «카카오 로그인(Auth)을 이 프로젝트에서 쓸까요? 로그인은 사용자 정보·토큰을 다룹니다. 승인하면 다음 작업들도 로그인 기능은 다시 묻지 않습니다.» — 요청 원문이 대응 낱말로 이미 말했으면 질문 대신 1급 행 «범위 넓힘: Auth(로그인) · 출처 <줄>». 같은 이름공간 안 변형(`call`)은 정보 줄 «같은 묶음 안 기능: Share.sendScrap». `data_out` 함수는 «카카오톡 공유에 사용자가 고른 사진을 카카오 서버에 올리는 기능(Share.uploadImage)을 쓸까요? 올린 사진은 카카오가 보관합니다(운영자 문서: 100일).» 1문항이다 — 요청 원문이 대응 낱말로 이미 말했으면 1급 행에 보관 사실을 함께 적는다(v3.2). gateway 경로는 경로마다 1문항이고 «자명하면» 건너뛰기가 없다. 한 명세가 같은 이름공간에서 함께 들이는 data_out 이름·gateway 경로는 1문항 · 1결정 줄로 묶는다(v3.3).

### 6-4. 기각

- 목록·사본은 그대로다(아직 아무것도 설치하지 않았다). 임시 사본을 지운다. `candidate.json`·`docs.html` 은 기각 기록으로 남는다.
- `g1_decisions` 에 `SDK 채택 기각: <id> · 출처 = …` 를 적는다.
- architect 를 G1 override «SDK 기각: <id>» 로 다시 부른다. 명세는 그 SDK 없이 같은 결과를 내는 설계(서버가 만드는 길·평범한 링크·native)로 바꾸거나, 그 요구를 «이 SDK 없이는 불가»로 표시한다.
- 불가 표시면 Coordinator 가 «범위에서 빼고 진행 / 요청 종료»를 묻는다(비위반 이동 STOP 꼴). 답은 scope.md «범위 아님»에 한 줄로 적는다(scope 바이트 변경 절차).
- 기각은 그 요청에만 묶인다. 목록은 승인 항목만 담으므로 다음 요청이 같은 SDK 를 다시 제안할 수 있다.

### 6-5. 설치 — Phase 2 진입 준비 ②″ · ③ · ⑤

- **②″**
  1. `install …`
  2. **`sdk_vendor.py verify <루트>` exit 0**(검사기 B2 — `backstop.py --only wv` 가 아니다)
  3. 격리 커밋(목록·`vendor/<id>/`·`vendor/.gitattributes` 만) → `sdk_commits`·`last_commit`
  - 재개 때 결정 줄은 있는데 목록에 항목이 없으면 다시 돈다.
- **③**: G1 승인 SDK 공개 설정 배선 — 프로젝트 선택형 꼴의 한 줄. «배선 적용» 줄을 남긴다.
- **⑤**: `candidate.json`·`docs.html`·`license-header.txt`·`api-paths.txt`·`evidence.md`·`entry-draft.json` 을 산출물 커밋에 넣는다(임시 사본 제외).
- 슬라이스 도출에서 벤더·목록은 계수 밖이다. SDK 로드 태그는 그 페이지 슬라이스에 간다.

### 6-6. 이후 레인

- host 상태의 승인 SDK·`use_scope` 묶음을 «기존 승인»으로 쓴다. G1 배너는 정보 줄이다. 같은 이름공간 안의 다른 호출형 함수도 묻지 않는다(정보 줄).
- 새 이름공간이나 이름 지정 `data_out` 함수(사용자 자료를 운영자 저장소로 보내는 함수)나 gateway 경로(v3.3 — 경로마다 묻는다)가 필요하면 «범위 넓힘»이다(§3-5 · 사용자 결정 «G1 에서 한 줄로 다시 묻기» · 요청 원문이 대응 낱말로 이미 말했으면 그 줄이 출처). `sdk_ui` 함수는 범위 넓힘 대상이 아니다. WV9 가 기능 JS 에서 덫으로 잡는다.

### 6-7. 수정 · 트리비얼 · 재개 · 엣지

- 수정 모드는 SDK 행이 생기면 G1′ 을 생략하지 않는다(A15). SDK 설치·판 올림·범위 넓힘·등록·제거는 트리비얼이 아니고, 트리비얼이 늘 red 를 만나면 수정 모드로 승격한다(A16).
- 기준점 뒤에 들어온 늘 red 는 ⓡ1~ⓡ4 로 고칠 수 있으면 Coordinator 가 언제든 격리 커밋으로 고치고, 아니면 정지·입구다(A20 근처 문장 · 규범 R4).
- 재개는 `sdk_commits`·`g1_decisions` 로 복원한다(A26 «세션 사멸 후 재개» 항목에 한 구).
- 엣지 «코더 SDK 필요 → 설계 반송»(A17). 반송 (가)에 SDK 공개 설정을 포함한다(A12).

### 6-8. 경우별 처리 — 모든 모드

**승인 불요 복원**(어느 모드의 슬라이스 0 이든 Coordinator 격리 커밋으로 할 수 있다):

- ⓡ1 `restore` — 다시 받은 바이트 = 등재 지문
- ⓡ2 목록 재정규화 — 파싱한 내용이 같고 바이트 꼴만 다를 때
- ⓡ3 `.gitattributes` 재기록
- ⓡ4 **아무 템플릿도 부르지 않는** 비등재 벤더 파일 제거(실행되지 않는 바이트라 동작 불변)

그 밖(등록·재승인·범위 넓힘·참조 중인 비등재 사본)은 G1 승인이 필요하거나 동작 변경이다. ⓡ 는 G0 의 슬라이스 0 뿐 아니라 **기준점 뒤에 들어온 늘 red 에도 언제든** 쓴다(규범 R4).

| # | 경우 | 처리 |
|---|---|---|
| 1 | 등재 id · 정상 | 아무 일 없음 |
| 2 | 등재 id · 사본 변조·링크·속성 | 모든 레인 G2 red. G0 `undeferrable` → 슬라이스 0 ⓡ1·ⓡ3(또는 기준점 뒤면 언제든). 원본이 그 바이트를 더 내지 않으면 «판 올림(G1) / 제거(동작 변경 — 별도 요청) / 정지» |
| 3 | 등재 id 디렉터리 안 비등재 파일 · 미참조 | ⓡ4 |
| 4 | 등재 id 디렉터리 안 비등재 파일을 템플릿이 참조(P13·K24·K41) | 등재 파일로 참조를 되돌리는 것은 coder 슬라이스 0(동작 불변이면) — 아니면 정지·입구 |
| 5 | 목록 · 결속 불일치(누가 칸을 바꿈) | G1 재승인(새 출처) 또는 ⓡ — 승인 기록과 맞는 판으로 되돌림(같은 항목 바이트일 때) |
| 6 | 목록 시대에 생긴 미등재 단위(목록 삭제·항목 삭제·개명·병합 해소 탈락 — WV13 · K42·K48·K49) | 모든 레인 G2 red. 목록 판을 되돌리거나(ⓡ — 이력의 마지막 승인 판과 바이트·결속이 같을 때) 재등록(G1) 또는 `remove`(참조가 없을 때 · 있으면 별도 요청) |
| 6b | 판 올림 뒤 옛 판 바이트의 «목록 이전 임시 사본»(과 그 로드 줄)이 merge 로 돌아와 WV13 — 참조 중이라 ⓡ4 를 쓸 수 없음(K50e · 검사기 최종 메모 2) | 출구는 **사본·로드 줄을 지금 등재 파일로 치환하는 슬라이스 0**이다(coder: 로드 줄을 등재 `{% static %}` 경로로 치환 · Coordinator: 임시 사본 삭제를 격리 커밋). 바뀌는 동작은 판 차이뿐이고 그 판은 이미 G1(판 올림)에서 승인됐으므로 질문이 아니라 G1 정보 줄 «옛 판 임시 사본 → 등재 판 치환»이다. G0 뒤에 들어왔으면 정지하고 이 치환을 다음 레인의 슬라이스 0 이나 `/dddjango-web:refactor web/static/vendor` 로 안내한다. 그래서 임시 사본 가지는 판 올림 전에 merge 하거나 폐기한다 |
| 7 | 목록 시대 전 미등재 단위 · 그것을 건드리지 않고 main 도 받지 않는 레인 | 막히지 않는다. G0 알림 1행 |
| 8 | 목록 시대 전 미등재 단위 · **그 사본이 레인 도중 main 에서 들어옴** | 그 레인의 diff 게이트(WS6/WP1/WP2)가 red 다. G0 동결 뒤라 ⓐ/ⓑ 가 없고, 출구는 등록 착륙 뒤 main 을 다시 받는 것뿐이다(규범 R1). 그래서 그런 사본을 main 에 들이지 않는 것이 기본값이다(§9 (가)) |
| 8b | 목록 시대 전 미등재 사본을 가진 가지를 rebase·squash·cherry-pick 으로 착륙(검사기 v3.1 minor 1) | 그 사본은 WV13(늘 red)이 된다. 출구는 #6 과 같다(되돌림 · 재등록 G1 · `remove`). 그래서 G0 알림과 가이드가 «merge 로 착륙»을 요구한다(K50c) |
| 9 | 목록 시대 전 미등재 단위 · 요청이 그 디렉터리나 그 사본을 부르는 화면에 닿음 | 스캔 단위 → 보통 빚 질문. ⓐ = 슬라이스 0 «기존 등록»(G1 · `--register-existing`) |
| 9b | 9 의 ⓐ(기존 등록)를 골랐는데 G1 에서 등록이 기각되거나, 대리 실행에 판을 담은 원문이 없음(규범 v3.1 nit-8) | 그 단위는 `ⓐ 재상정` «등록 거절 — 제거(동작 변경 · 별도 요청) / 출처 있는 ⓑ / 중단» 이다. 본인 직접 실행이면 사용자가 셋 중 고른다. 대리 실행이면 기록하고 정지한다(§3-4 위임 불가) |
| 10 | 목록 시대 전 미등재 단위가 있는 프로젝트에서 새 SDK 채택 | 막지 않는다(v3). G1 배너에 미등재 줄 1행. 새 SDK 는 자기 id 만 등재된다. 목록 시대에 생긴 미등재 내용이 있으면 `install` 자가 `verify` 가 실패한다(#6 을 먼저 고친다) |
| 11 | 리팩토링 · 대상 무관 · 등재 파손(규범 M5) | 리팩토링 G0 «범위 밖 미룰 수 없음» 행 → **ⓡ 로 고칠 수 있으면 슬라이스 0 에 포함**(대상 무관 · Coordinator 격리 커밋). 아니면 G0 정지 «선행: `/dddjango-web:refactor web/static/vendor`(등록) 또는 기능 요청(판 올림)» |
| 12 | 리팩토링 · 대상 `web/static/vendor`(규범 M9) | 아래 «벤더 단위» |
| 13 | 트리비얼 · 늘 red | 수정 모드로 승격(A16) |
| 14 | 병합이 목록·벤더를 바꿈 | 상류 몫은 notice(내용은 늘 검사가 본다) · 병합 커밋 자신의 몫(evil merge)은 WV10 발견 → 되돌림 |

**리팩토링 «벤더 단위»** — `/dddjango-web:refactor web/static/vendor` 는 등재 전·등재 체제 모두의 정의된 입구다.

- R0 는 이 단위를 **SDK 등재 정리 전용**으로 받는다(새 채택·판 올림·범위 넓힘은 받지 않는다 — 기능 요청 안내).
- R1 은 `--debt-scan --refactor` 를 돈다. 키는 WV12·WS6·WP1·WV1~WV6·WV11·WV13 과, 그 사본을 부르는 템플릿 줄의 WP2/WV6 이다. 템플릿 줄은 기존 «범위 밖 줄 편집 (가) 로드 줄»로 옮길 수 있다. 등록할 항목의 `public_config.setting` 이 settings 에 없으면 그 항목은 `ⓐ 재상정` «기능 요청 — 공개 설정 배선»이다(규범 N4).
- R2 의미 점검 조각은 0 이다. R3 판정은 0 행이다.
- G0 의 ⓐ 후보: 기존 등록(공식 원본 증명 필수) · ⓡ1~ⓡ4 · 미사용 제거(WV11). 공식이 아닌 사본은 등록할 수 없으므로 `ⓐ 재상정` «별도 요청 — 동작 변경(라이브러리 제거)»이다.
- G1(리팩토링)은 «기존 SDK 등록» 줄만 가진다. Phase 2 ②″ 는 등록·복원·제거만 한다. coder 슬라이스 0 은 옛 경로 삭제·태그 치환을 한다(참조 완전성 ③ 그대로).
- R0 문구와 §6-8 을 같은 말로 맞춘다(A19).

### 6-9. G2

- 백스톱은 그대로다(WV 는 러너 안 · 등재 id·목록·이력 대상은 늘).
- 3-1 에 «공식 SDK 경계 확인»(A13 · §7-6)을 둔다.
- 배너 ③′ SDK 행(A14):

```
SDK: kakao_js_sdk 2.8.3(새 채택 · 범위 3) · 격리 커밋 <약칭> · 출처 <꼴> · 운영 env 필요 KAKAO_JAVASCRIPT_KEY
  · 차단 장치 <context.route(팝업 포함)|CDP auto-attach+Fetch|없음> · 운영자 호스트 요청 통과 0 · 차단 <n>건 · 운영자 window.open·폼 제출 기록 <n>건(보내지 않음) · 프로젝트 JS 외부 요청 <n>(발견 · 시작 스택 없음 <k> 포함) · 그 밖 외부 요청 <호스트별 수>(기록만)
  · 가로채기 설치 <init-wrap|direct> · 기록 case k 일치 k/k · 사용자 동작 안 호출 예 · 함수 표 일치(표에 없는 함수 0 · sdk_ui 0 · 파일 인자 분류 일치)
  · SDK 인자 검증(실물 1회 · 차단 하) <통과|미검증(사유)> · 실패 행(SDK 차단 · 키 빈 값) <결과>
  · CSP <없음|대조 결과> · 판 올림이면 «G2 시각 증거 재관찰(implementation_digest 변경)» · 실제 왕복 <미검증(등록 도메인 · 사용자)|확인 <시각>>
```

### 6-10. 앵커 — W8e·W6m 뒤, W8 과의 순차 착륙

`CL`·`CX` 같은 문장이다(CX 는 치환 둘). HEAD 줄 번호 / W8e 워크트리 줄 번호.

| A | 자리 | 앵커 | 바꿈 |
|---|---|---|---|
| A1 | 머리 직접 쓰기(`CL:8`) | «직접 쓰기의 명시 예외)**» | 뒤에 « · **공식 SDK 설치·복원·제거(`sdk_vendor.py` — G1 승인된 운영자 원본 byte 복사·등재 목록·SDK 공개 설정 배선 — 격리 커밋)**» |
| A2 | 산출물 위치(`CL:41`) | «- 빌드 상태 → …» | 앞에 «- SDK 후보 → `<산출물 폴더>/sdk-candidates/<id>/`(candidate.json·docs.html·license-header.txt·api-paths.txt·evidence.md·entry-draft.json — 임시 사본은 지운다)» |
| A3 | build-state | «"g2_visual":» | 키 `sdk_commits` · 갱신 시점 «SDK 격리 커밋마다» |
| A4 | step 1 host(`CL:138`) | «기존 base의 공통 scripts block…host 상태로 기록해» | «·승인된 SDK(id·판·use_scope)·CSP 유무·프로젝트 정적/미디어 CDN 출처» |
| A5 | step 4′ 단위(`CL:149`) | «web 컨테이너 파일(`web/*.py`)» | «(`web/*.py` — 목록은 `web/static/vendor/` 단위)» |
| A6 | Phase 1 입력(`CL:188`·`189`) | «**host 상태**(…classic/module 방식)» | «·승인된 SDK» · «(후보가 있으면) `sdk-candidates/<id>/`» |
| A7 | 스캔 단위 확인(`CL:194`) | «(motion.js 채택이면 `web/static/js/` 포함)» | «· SDK 새 채택·판 올림·범위 넓힘·등록·복원이면 `web/static/vendor/` 포함» |
| A8 | 계약 인용 0 확인 뒤(`CL:196`) | «**계약 인용 0 확인(G1 배너 직전 · openapi 동결본이 있을 때)**» | 다음 문단 «**SDK 채택 확인(G1 배너 직전** …»(§6-3) — verify-web 대조 목록에 이 표지 |
| A9 | G1 배너(`CL:198`) | «Z는 옵션으로 보인다.» | SDK 줄·따로 묻기·출처·기각 |
| A10 | Phase 2 진입(`CL:203`) | «러너 채택 0이면 설치하지 않는다(…없다).» | ②″(`verify`) · ③ · ⑤ |
| A11 | 슬라이스 도출(`CL:209`) | «**잔여 범주 귀속**» | 벤더·목록 계수 밖 |
| A12 | 반송 (가)(`CL:217`) | «(Phase 0 검사 6종의 미비 — 승인 하 직접 적용» | «… 6종 · G1 승인 SDK 공개 설정의 미비 — …» |
| A13 | 3-1(`CL:218` / W8e `CL:226`) | «쓰지 않는 자원을 검증 의무로 추가하지 않는다.» | 앞에 «공식 SDK 경계 확인»(§7-6) |
| A14 | G2 배너(`CL:222` / W8e `CL:231` · `CX:245` / W8e `CX:254` · verify-web 대조) | «④ **합치기 고지 1줄**» | 앞에 «③′ **SDK 행**» |
| A15 | 수정 모드 3(`CL:243`) | «**G0 ⓐ가 있으면 G1'을 생략하지 않는다**» | SDK 문장 |
| A16 | 트리비얼(`CL:250`) | «신규 파일 0 + 비구조 diff(…)일 때 후보가 된다.» | «SDK 설치·판 올림·범위 넓힘·등록·제거는 트리비얼이 아니다 · 트리비얼이 늘 WV red 를 만나면 수정 모드로 승격한다» |
| A17 | 엣지(`CL:262`) | «- **행위 항목 구현 불가**:» | 뒤에 «코더 SDK 필요» |
| A18 | 경계(`CL:274`) | «유일 예외는 G0 승인 하의 web 배선 6종이다» | «… 6종과 G1 승인 하의 SDK 공개 설정 배선이다» |
| A19 | R0(`CL:282`) | «없음 · 2개 이상 · 단위 안쪽 경로 ·» | 앞에 «`web/static/vendor` 는 SDK 등재 정리 전용(새 채택·판 올림·범위 넓힘은 기능 요청) ·» |
| A20 | 리팩토링 배선(`CL:302`) | «Phase 2 진입 준비 ②·②′·③ 이 없고» | «(②″ 는 등록·복원·제거만)» + 대상 무관 ⓡ 슬라이스 0 문장 + «기준점 뒤에 들어온 늘 WV red 는 모든 모드에서 ⓡ1~ⓡ4 로 언제든 격리 커밋 · 아니면 정지·입구» |
| **A21** | step 4′ 판정(`CL:149` / CX `:171`) | «각 키에 판정 물음» | 앞에 «러너가 `undeferrable` 로 표시한 키(WV 늘 검사 — houserules §9)는 판정 물음 없이 «미룰 수 없음»이다. » |
| **A22** | 경계 직접 쓰기 목록(`CL:270` / W8e `:279`) | «첫 실행 최소 골격에 한정)**뿐이다» | 앞에 A1 과 같은 항목 |
| **A23** | 위임(`CL:276` / W8e `:285`) | «위임되는 것은 승인 입력뿐이다» | 뒤 목록에 «SDK 채택·판 올림·범위 넓힘·기존 등록 승인(사용자 원문 없으면 비위임 — houserules §9)» |
| **A24** | step 1 dirty(`CL:138`) | «`.dddjango-web/` 기록 폴더는 판정 밖) "커밋/스태시 후 진행 vs 그대로 진행(중단 복구 불가 고지)"» | 뒤에 «`web/sdk_registry.json`·`web/static/vendor/` 의 미커밋 변경은 «그대로 진행»을 받지 않는다(WV10)» |
| **A25** | G0 배너(`CL:180`) | «+ **빚 1행**(» | 빚 행 뒤에 «+ (미등재 벤더 디렉터리가 있으면) 이관 알림 1행(§5-4 — 입구와 «main 받기 red 는 등록 착륙까지»)» |
| **A26** | 재개 엣지(`CL:266` / W8e `:275`) | «**세션 사멸 후 재개**: 위 기존 화면 재개 입구로» | 끝에 «SDK 결정 줄이 있고 목록에 없으면 ②″ 를 다시 돈다(`sdk_commits`)» |

- 손대지 않는 자리: `CL:212`·`CL:214`(문단 대조 문구) · `CL:220`·`CL:244`(W6m·W8) · `CL:166`·`CL:179`·`CL:211`(W2·W3).
- **같은 물리 줄 `CL:222`·`CX:245`**(규범 m10): A14 와 W8 커밋 ②가 같은 줄을 고친다. 이 줄은 문단 하나가 든 한 줄이라 «다른 문장»이어도 git 에서는 같은 줄 충돌이다. 그래서 **병렬 가지 금지 · 순차 착륙**이다.
  - 순서: W8e → W6m → **SDK S4(A14)** → 속도 배치 릴리즈 → **W8 커밋 ②**(S4 가 바꾼 줄 위에 자기 행을 얹는다).
  - W8 ②가 먼저 착륙하면 S4 가 그 위에 얹는다. 어느 쪽이든 rebase 로 남의 편집을 다시 쓰지 않고, 착륙 뒤 `make verify-web` 문단 대조를 확인한다.
- **W8 설계에 넘길 글**(규범 M6·m8·m10 · 검사기 M7 — W8 문서에 그대로 옮긴다):
  > ① **SDK 레인 측정 조건**: 등재 SDK 를 부르는 화면의 구현측 census·`asset_digests.js` 는 **운영자 호스트만**(등재 `operator_domains` 하위 ∪ `origins.operator`) **브라우저 컨텍스트 경로**(`page.context().route` — 팝업 포함 · CDP 는 auto-attach + 타깃별 Fetch)에서 막은 상태로 잰다. 프로젝트 정적·미디어 CDN(예: spring_dream CloudFront)은 막지 않는다. SDK 로드·init 은 운영자 호스트 요청 0 이라 [실측 카카오 2.8.3] 첫 화면 측정값이 바뀌지 않는다. 시안측은 SDK 를 싣지 않으므로 대칭 문제가 없다.
  > ② **§2-6 (c) «바뀐 JS·HTMX 동작 파일을 쓰는 case»** 에 `web/static/vendor/**`·`web/sdk_registry.json` 변경(판 올림·등록·복원)을 넣는다 — 그 SDK 를 로드하는 case 전부다. 판 올림은 `implementation_digest` 를 바꾸므로 G2 시각 증거를 다시 뜬다.
  > ③ **3-1 앵커 보존**: W8 이 3-1(`CL:218-219`)을 고칠 때 SDK 문장의 앵커 «쓰지 않는 자원을 검증 의무로 추가하지 않는다.»와 그 앞 «공식 SDK 경계 확인» 문장을 보존한다.
  > ④ **`CL:222`·`CX:245` 순차 착륙**(위 순서 · W8 v2 에도 이 제약을 적는다 — 이 설계는 W8 문서를 고치지 않는다).
  > ⑤ **감사 범위**: 목록·벤더 변경은 W6m «touched» 감사에서 «격리만»(WV10 결과) 본다.

### 6-11. REQUEST_GUIDE 문안

발주자용 문안이다. `REQUEST_GUIDE.md` 와 Codex 는 byte 미러다.

- §3 «알려 주면 좋은 제품 정보» 새 항목:
  > - 외부 플랫폼으로 보내기: “카카오톡으로 공유하면 친구 채팅방에 시안의 카드(그림·제목·설명·단추 둘)가 보여야 합니다.”처럼 받는 쪽에서 보이는 결과를 적습니다. 그 플랫폼이 공식으로 배포하는 도구가 필요하면 플러그인이 조사해 설계 승인 단계에서 «새 SDK 채택»으로 한 번 묻고, 승인한 도구는 이 프로젝트의 다음 요청에서 같은 기능 묶음(예: 공유)이라면 다시 묻지 않고 씁니다. 같은 도구의 다른 기능 묶음(예: 카카오 로그인)은 한 번 더 묻습니다. 같은 묶음 안이라도 사용자 사진·파일을 플랫폼 서버에 올리는 기능은 한 번 더 묻습니다. 요청에 «카카오 로그인을 붙여 주세요»처럼 그 기능을 이미 적었으면 그 글을 승인으로 받고 묻지 않습니다. 요청마다 도구 이름을 적거나 허용할 필요는 없습니다. 플랫폼 공식 도구가 아닌 일반 JavaScript 라이브러리(화면 캡처·차트·화면 프레임워크 등)는 쓰지 않습니다.
- §5 «있으면 함께 주기» 새 항목:
  > - 외부 플랫폼 준비 상태: 개발자 앱·사이트 도메인 등록 여부와 공개 키를 담을 서버 설정 이름(예: `KAKAO_JAVASCRIPT_KEY`). 키 값은 요청에 적지 않습니다. 운영 서버 env 에도 키를 넣어야 합니다. 실제 보내기 확인은 등록된 주소에서 사용자가 합니다.
- §7 «다른 세션에 맡겨 요청할 때» 새 항목:
  > - «새 SDK 채택»·«SDK 판 올림»·«기존 SDK 등록» 승인은 사용자가 그 도구의 판(또는 승인 화면에 나온 표지 `<id>@<판>#<지문>`)을 담아 남긴 원문이 저장소의 화면 코드·작업 기록 폴더 밖에 커밋돼 있고 지금 작업 가지의 이력에 있을 때만 대신 전할 수 있습니다. 작업 가지에서 도는 요청이면 그 원문 줄을 작업 가지의 `docs/…` 에 커밋하세요(main 에만 있으면 받기 전에는 쓸 수 없습니다). 판을 올릴 때는 새 판을 적은 새 원문이 필요합니다. «사용 범위 넓힘»은 운영자 이름과 그 기능 이름을 담은 원문(예: «카카오 로그인 붙여 주세요»)이면 되고, 판은 없어도 됩니다. 없으면 플러그인이 멈추니 사용자에게 올립니다.
  > - 등록된 도구(목록 `web/sdk_registry.json` 이나 `web/static/vendor/`)를 바꾼 가지를 main 에 합칠 때는 합친 결과에서 `sdk_vendor.py verify` 가 통과하는지 먼저 확인합니다. 등록 안 된 도구 사본을 main 에 들이지 마세요 — main 을 받는 다른 작업들이 등록이 끝날 때까지 완성 단계에서 막힙니다. 이미 그런 사본이 든 가지를 합쳐야 하면 rebase·squash 가 아니라 merge 로 합칩니다(rebase·squash 로 합치면 그 사본이 «등록 뒤 새로 생긴 것»으로 보여 모든 작업이 막힙니다).
- §4 «사용할 라이브러리»(적지 않을 것)는 그대로다. 위 §3 항목이 «라이브러리 이름이 아니라 결과를 적는다»를 보강한다.

## 7. 규범 문안

### 7-1. houserules(`HR` · byte 미러)

- **§1 트리**
  - `static/` 블록에 «`vendor/  # 승인된 공식 SDK 사본 — .gitattributes(고정 표지) + <sdk_id>/<파일> · 필요할 때만(§9)`»
  - `web/` 직속에 «`sdk_registry.json  # 공식 SDK 등재 목록 — SDK 가 있을 때만(§9)`»
  - 읽는 법의 조건 생성 문장에 `static/vendor/`·`sdk_registry.json` 을 더한다.
- **§3** 둘째 항목 끝: «`static/vendor/`·`sdk_registry.json` 은 승인된 공식 SDK 가 있을 때만 생긴다(골격 아님 — §9)».
- **§4 총괄표** 세 행:
  - `| web/ 직속 | 고정 | sdk_registry.json | 공식 SDK 등재 목록 — Coordinator 가 도구로만 쓴다(§9) |`
  - `| static/vendor/ | 고정 | .gitattributes | 바이트 안정 표지 — 도구가 쓰는 고정 내용(§9) |`
  - `| static/vendor/<sdk_id>/ | 운영자 원본 | <운영자 파일 이름>(WN8 꼴 · 확장자 없으면 <sdk_id>.js) | kakao_js_sdk/kakao.min.js — 등재된 한 파일·byte 그대로·수정 금지(§9) |`
- **§5⑤**
  - 첫 문단의 «새 JS 프레임워크/라이브러리는 금지다» 뒤에 «(승인·등재된 공식 플랫폼 SDK 는 §9 의 예외 — 그 밖 제3자 JS 는 등재와 무관하게 금지)»
  - «CDN 실행 태그·inline 실행 JS…» 문장 뒤에 «(템플릿 URL 속성의 `javascript:` 류·템플릿 태그로 이어 붙인 스킴·`srcdoc`·SVG `set/animate` 의 href 포함). 공식 SDK 도 CDN 이 아니라 등재 사본을 로드한다(§9). 기능 JS 는 외부 스크립트를 끌어오지 않고(`createElement('script')`·`createElementNS(…, 'script')`·`srcdoc` 대입·`document.write`·`import()`·문자열 실행), 외부 절대 URL 문자열을 담지 않는다(W3C 이름공간 URI 만 예외 — 외부 주소는 서버가 state 로 넘긴다). 기능 JS 의 네트워크 요청(fetch·XHR·WebSocket·EventSource·sendBeacon)과 JS 가 만드는 iframe 은 프로젝트 출처(레인 서버 · settings 의 정적·미디어·저장소 출처)로만 간다 — 외부 서비스는 서버나 등재 SDK 가 부른다»(v3.2 · 규범 v3.1 m-1 · 검사기 v3.1 minor 2 — 플러그인 정의 «web 은 내부의 외부 클라이언트»와 현장 관행 `sameOrigin` 에서 나온다)
- **새 §9 «공식 플랫폼 SDK — 등재·사본·로드»**(목차 추가):
  > 플랫폼 운영자가 자기 서비스 API 를 부르라고 직접 배포하는 브라우저 SDK 는 사용자가 G1 에서 한 번 승인하고 `web/sdk_registry.json` 에 등재한 것만 `static/vendor/<sdk_id>/<파일>` 에 운영자 원본 그대로 둔다.
  >
  > **자격**(모두):
  > ① 배포자 = 그 서비스의 운영자
  > ② 원본·문서 주소가 운영자 공식 도메인의 https(리다이렉트 최종 주소 포함). 공용 라이브러리 CDN(cdnjs·jsdelivr·unpkg·code.jquery.com·skypack·esm.sh·`/ajax/libs/` 경로 …)은 운영자 소유여도 아니다
  > ③ 운영자 자기 문서 쪽이 그 원본 주소를 인용(도구가 직접 받은 원문으로 확인)
  > ④ 라이선스·약관 확인
  > ⑤ 승인된 요구의 결과가 서버·평범한 링크·native 로는 안 됨을 운영자 문서로 보임
  > ⑥ 원본 그대로 한 파일이고 실행 중 다른 코드를 받아 실행하지 않음
  > ⑦ 운영자 자기 서비스 API 의 클라이언트(사본의 주석 밖 코드가 배포·문서 호스트와 다른 운영자 서비스 호스트를 부른다)
  >
  > **제외**: UI 프레임워크·컴포넌트 라이브러리, 상태 계층, 일반 유틸리티, 화면 캡처·렌더, 차트·시각화, 애니메이션, 폴리필·로더, htmx 와 그 확장, 비공식 래퍼. 운영자가 냈더라도 자기 서비스를 부르지 않으면 제외다. SDK 가 우리 DOM 에 UI 를 그리는 기능·ESM 전용·여러 파일·SDK CSS 는 받지 않는다.
  >
  > **목록**: 스키마 `dddjango-web-sdk-registry/2` · 정규 JSON 바이트(키 정렬 · 2칸 · NFC)다. 해시·크기·최종 주소·문서 증거·접속 호스트·파일이 담은 기능은 도구만 쓴다. `use_scope` 는 이 승인이 덮는 SDK 함수다. 공개 설정 이름에는 `SECRET`·`PASSWORD`·`PRIVATE`·`TOKEN`·`ADMIN` 낱말을 쓰지 않는다(공개 흐름으로 HTML 에 나간다 — JavaScript 키만).
  >
  > **늘 검사의 대상**(v3.3):
  > - 목록이 있으면 목록 자체(형식·결속·공식성)와 **등재 id 디렉터리**·그것을 가리키는 모든 템플릿 참조·`vendor/.gitattributes` 가 게이트와 무관하게 늘 검사되고, 발견은 «미룰 수 없음»이다.
  > - 목록에 없는 벤더 단위(`vendor/` 아래 디렉터리 또는 직속 파일)는 지금 내용이 처음 생긴 때로 가른다. 목록이 저장소에 들어온 뒤(«목록 시대» — 목록을 들인 커밋의 자손)에 처음 생긴 내용이 하나라도 있으면 늘 발견이다(강등 금지 — 목록 삭제·항목 삭제·개명·병합 해소 탈락 모두). 등재에서 빠지는 길은 디렉터리째 지우는 `remove` 뿐이다. 목록에서 빠진 등재 바이트의 사본은 어디에 있든 늘 발견이다. 지금도 등재된 바이트의 다른 자리 사본은 목록 이전에 그 자리에 있던 것만 «등재 전»이다. 목록 시대는 마지막 SDK 를 지워도 끝나지 않는다. 얕은 이력에서는 판정하지 않고 멈춘다.
  > - 목록이 생기기 전부터 있던 내용만 담은 미등재 단위는 «등재 전»이다. 새 벤더 파일·새 로드 줄만 diff 게이트가 막고, 빚 스캔은 이관 항목 WV12 를 내며, G0 배너에 입구를 알린다. 그 사본이 main 에 들어오면 main 을 받는 레인의 diff 게이트가 등록 착륙까지 red 이므로, 미등재 사본을 main 에 들이지 않는다. 그런 사본이 든 가지는 merge 로 합친다(rebase·squash 로 합치면 «목록 시대에 생긴 내용»이 된다).
  > - OS 잡파일(고정 목록 · 미추적이거나 무시된 것)은 세지 않는다.
  >
  > **승인**: 승인은 approval 을 뺀 항목 전체의 정규 JSON sha256(NFC)에 묶인다. 한 칸이라도 바뀌면 다시 승인한다. 출처는 «본인 직접(<시각>)» 또는 «사용자 원문 <저장소 상대 경로>@<커밋>:<행>(<시각>)» 뿐이고, 대리할 수 없다. 원문은 다음을 모두 지켜야 한다.
  > - 커밋이 지금 HEAD 의 조상이고, 경로가 `web/`·`.dddjango-web/` 밖이다.
  > - 그 줄에 시각과, 도구가 항목에서 뽑은 운영자·제품 낱말과, 판(또는 도구가 만든 표지 `<id>@<판>#<지문 앞 12>`)이 있다. 시각이 후보 수집보다 이르면 배너에 알린다.
  > - 판 올림은 새 판(새 표지)을 담은 새 원문이고, 범위 넓힘은 그 이름공간의 낱말(예: «카카오 로그인»)을 담은 원문이다.
  >
  > **범위**: 승인은 `use_scope` 의 원소 — 핵심 함수 · `<이름공간>.*` 묶음 · 이름 지정 함수 — 만 덮는다. 묶음은 그 이름공간의 호출형·수명 함수만 덮는다. 사용자 자료·계정 상태를 운영자 쪽에 보내거나 바꾸거나 지우는 함수(업로드·저장류)는 묶음에 들지 않고, 이름을 적어 따로 승인한다. 운영자 API 경로를 인자로 받는 범용 함수는 경로마다 적어 따로 승인한다. 한 요청이 함께 들이는 것은 한 번에 묻는다. SDK 가 우리 DOM 에 UI 를 그리는 함수는 어떤 승인으로도 쓰지 않는다. 함수 분류는 목록의 `namespace_members` 에 있고 승인에 묶인다. 같은 이름공간 안 호출형 함수는 다시 묻지 않는다(정보 줄). 새 이름공간·이름 지정 함수·범용 함수 경로는 G1 에서 한 줄로 다시 묻고, 요청 원문이 대응 낱말로 이미 말했으면 그 줄이 출처다(범용 함수 경로는 예외 없이 묻는다). 파일이 담은 다른 기능은 이렇게 다시 승인하기 전에는 쓰지 않는다.
  >
  > **바이트**: 사본은 심볼릭 링크·변환 속성 없이 git 에 일반 파일로 저장된 운영자 원본이다(`static/vendor/.gitattributes` 고정 표지).
  >
  > **쓰는 쪽**: 목록·사본은 Coordinator 가 `sdk_vendor.py` 로만, 그 둘만 담은 `chore(web-sdk):` 커밋으로 바꾼다. 설계자·코더는 읽기만 한다.
  >
  > **복원**: 다시 받은 원본이 등재 지문과 같을 때의 복원, 목록 재정규화(NFC 포함), 표지 재기록, 아무도 부르지 않는 비등재 사본 제거는 승인 없이 어느 작업에서든 언제든 한다(G0 뒤에 들어온 파손 포함).
  >
  > **로드**: 그 SDK 를 쓰는 페이지의 `{% block scripts %}` 안(모든 페이지가 쓰면 base 의 `{% block scripts %}` 앞)에 외부 `{% static 'web/vendor/<id>/<파일>' %}` 로 한 번 둔다. 속성은 `src`·`defer` 만이고, 그 SDK 를 부르는 기능 JS 태그보다 앞이다. base·페이지 중복 로드는 금지다.
  >
  > **호출·키**: SDK 호출은 UI 동작 계약이 지정한 기능 JS 안에서, `use_scope` 묶음의 함수만, 부르는 순간 전역 경로로 한다. 공개 키는 settings 값만 출처다 — VM 이 state 에 담고 템플릿이 escape 된 data 속성·`json_script` 로 넘긴다. 키 리터럴·`os.environ` 직접 읽기·새 context processor 는 금지다.
  >
  > **정리 단위**: 벤더 칸은 리팩토링에서 «SDK 등재 정리 전용» 단위다(등록·복원·미사용 제거만).
- **§7**
  - 검사 패밀리 «4종» → «5종 … · WV(공식 SDK 등재 — §9)»
  - 게이트 의미론 문장 끝에 «WV 늘 검사는 §9 «늘 검사의 대상»을 따른다»
  - 빚 모드 문장에 «빚 스캔은 늘 검사 키에 `undeferrable` 을 표시하고, `debt-g0.json` 의 `scanner` 판이 다르면 잔존 판정은 불가다»
  - 반송 백링크에 «WV → §9»
- **§8 교정 사전** 한 행: `| CDN 실행 태그로 플랫폼 SDK 로드 · static/js/ 에 SDK 사본 | 등재 사본 `static/vendor/<id>/` + 로컬 defer 태그(§9) — 공식이 아니면 제거(별도 요청) |`.

### 7-2. architecture-web(`AW` §1 · byte 미러)

- «기술 책임»: «JavaScript 는 승인된 UI 동작 계약의 브라우저 임시 상호작용만 담당한다» 뒤에 «승인·등재된 공식 플랫폼 SDK 는 그 상호작용 안에서 운영자 서비스를 부르는 도구로만, 승인 범위의 기능만 쓴다(등재·로드 사실은 houserules §9)».
- UI 동작 계약 «담당 기술»에 `SDK:<sdk_id>` 값을 허용한다. 예시 표에 일반 행 하나를 더한다:

  `| 플랫폼 공유 | 승인 요구의 공유 단추 | HTML + UI JS + SDK:<sdk_id> | static/js/<기능>.js | [data-<root>] 안 단추·공유 자료 JSON | 공유 자료는 서버 렌더·HTMX 로 클릭 전에 준비 · SDK 호출은 우리 서버 요청 없음 | 없음(문서 수명 SDK 초기화 1회) | 키 빈 값 = 설정 실패 · SDK 없음 = 일시 실패 · 결과를 알 수 없으면 성공 표시 없음 | 호출 경계 기록 대조·사용자 동작 안 호출·두 실패 행 |`

### 7-3. implementation-ui(`IU` · byte 미러)

- §5 scripts block 예시 뒤:

  > 승인된 공식 SDK(houserules §9)는 그 SDK 를 쓰는 페이지의 `{% block scripts %}` **안에서**, 그 SDK 를 부르는 기능 JS 보다 **앞에** 한 번 로드한다. 속성은 `src`·`defer` 만 쓴다(모든 페이지가 쓸 때만 base 의 `{% block scripts %}` 앞).
  > ```html
  > {% block scripts %}
  >   <script src="{% static 'web/vendor/<sdk_id>/<파일>' %}" defer></script>
  >   <script src="{% static 'web/js/<기능>.js' %}" defer></script>
  > {% endblock scripts %}
  > ```
  > 공개 키는 VM 이 settings 에서 읽어 state 에 담고, root 의 escape 된 `data-*` 속성(값은 `{{ … }}` 만)이나 `json_script` 로 넘긴다.

- §7 «이미지·파일» 문단 끝: «공식 SDK 사본은 Coordinator 가 `sdk_vendor.py` 로 `web/static/vendor/` 에 설치한다 — 코더는 내려받기·복사·수정하지 않는다».

### 7-4. implementation-javascript(`IJ` · byte 미러 — verify-web 대조 추가)

- 새 **§8. 공식 SDK 소비**:
  > 등재된 공식 SDK(houserules §9)를 부르는 기능 JS 의 표기다. 채택·등재는 이 스킬 밖이다.
  > - **불러진 뒤에만**: SDK 전역(`window.Kakao` 류)이 없으면(차단·로드 실패) UI 동작 계약의 «일시 실패» 행대로 처리한다. 있다고 가정해 예외로 죽지 않는다.
  > - **초기화는 문서 수명 1회**: 키가 있으면 문서 활성화(DOMContentLoaded·`htmx:load`) 때 운영자 SDK 의 초기화 여부 API(`Kakao.isInitialized()` 류)로 멱등하게 초기화한다. 클릭 처리 안에서 늦게 초기화해도 된다(초기화는 동기다). 키가 비면 초기화하지 않고 «설정 실패» 행(다시 시도 없음)으로 간다.
  > - **부르는 순간 찾기**: 호출 함수는 `window.Kakao.Share.sendDefault(…)` 처럼 부르는 순간 전역 경로로 찾는다. 미리 꺼내 둔 참조를 쓰지 않는다 — 운영자 SDK 는 초기화 때 이름공간을 새로 대입한다(카카오 `this.Share=`).
  > - **사용자 동작 안에서 동기 호출**: 앱 전환·팝업을 여는 호출은 클릭 처리 함수 안에서 `await` 없이 부른다. 필요한 서버 자료(공유 링크·그림 주소)는 클릭 **전**에 서버 렌더·HTMX 교체로 root 에 와 있어야 한다. 클릭 뒤 비동기 대기를 거치면 브라우저가 팝업·앱 전환을 막는다.
  > - **범위**: 명세 «쓰는 SDK 기능»(`use_scope` — 핵심 함수 · `<이름공간>.*` · 이름 지정 함수) 밖 함수를 부르지 않는다. 묶음은 호출형·수명 함수만 덮는다 — 사용자 자료를 운영자에 올리는 함수(`uploadImage` 류)는 이름이 `use_scope` 에 있을 때만 부른다. 경로를 인자로 받는 범용 함수(`Kakao.API.request` 류)는 `use_scope` 에 적힌 경로만, 경로를 문자열 리터럴로 적어 부른다.
  > - **결과를 모르면 성공을 말하지 않는다**: 결과를 돌려주지 않는 호출 뒤에 «보냈어요» 류 성공 표시를 만들지 않는다.
  > - **보내는 값은 서버가 정한 값**: SDK 인자의 문구·주소·그림은 state 가 준 값을 그대로 쓴다. JS 에서 업무 문구를 조립하거나 가림 여부를 판정하지 않는다.
  > - **SDK 가 그리는 UI 금지**: 우리 DOM 에 단추·위젯을 그리는 API(`create…Button` 류) 대신 호출형 API 를 쓴다.
  > - **외부 코드·주소 금지**: script 요소를 만들지 않는다(`createElementNS` 포함 · 비실행 JSON 도 서버가 `json_script` 로 렌더한다). `createElement`·`createElementNS` 의 태그 인자에는 단일 문자열 리터럴만 넘긴다. `srcdoc` 을 대입하지 않고 `document.write` 를 쓰지 않는다. `import()`·문자열 실행(`eval`·`new Function`·문자열 `setTimeout`)을 쓰지 않는다. 기능 JS 에 외부 주소 리터럴(스킴이 붙은 문자열·도메인 꼴 문자열)을 적지 않는다 — 외부 주소(공유 링크·그림)는 서버가 state 로 넘긴다(W3C 이름공간 URI · 스킴만 든 `"https:"` 비교 · `'wss://' + location.host` 같은 `스킴://` 만 든 조각만 예외 · WV8). 네트워크 요청은 프로젝트 출처로만 한다. 정상 모양: 같은 출처 웹소켓은 `` `wss://${location.host}/…` `` 또는 `new URL(path, location.href)` 뒤 `protocol` 교체 · 바깥 링크 판정은 `new URL(href, location.href).origin !== location.origin` · 화면 문구 속 주소·이메일은 서버 state(규범 v3.1 nit-3).
  > - **검사용 코드 금지**: 테스트 전역·스텁 분기를 기능 JS 에 넣지 않는다. 검증은 브라우저 도구가 호출 경계에서 대체한다(§7).
- §7 표 한 행: `| 공식 SDK 호출 | assets/sdk_boundary.js 로 init 감싸기·직접 교체 가로채기(분류표대로 — 수명 함수는 그대로)와 운영자 window.open·폼 제출 기록 전용 래퍼 → 인자·호출 순간 사용자 동작 상태를 기록해 명세와 대조 · 컨텍스트 단위 운영자 호스트 차단 하 실물 1회 인자 검증 · SDK 차단(일시 실패)·키 빈 값(설정 실패) 행 · 운영자 호스트만 막은 첫 화면 동일 |`.

### 7-5. 역할 의무(Claude agents · Codex 역할 SKILL 의미 미러)

- **design-architect-web** — «UI 동작 계약» 항목 다음 새 항목:
  > - **SDK 사용 표**(«담당 기술»에 `SDK:<id>` 가 있으면): 헤더 byte 고정 `| SDK id | 상태 | 요구 근거 | 쓰는 SDK 기능 | 필요 근거 | 부르는 기능 JS | 로드 위치 | 공개 설정 이름 | 실패 동작 | 검증 행위 |`.
  > - 상태는 `기존 승인`(host 상태의 등재 목록 · `use_scope` 안 — 묻지 않고 쓴다)·`새 채택`·`판 올림`·`범위 넓힘`·`기존 등록`·`제거` 다.
  > - «쓰는 SDK 기능»은 묶음(핵심 함수 + `<이름공간>.*`)과, 필요하면 이름 지정 함수(사용자 자료를 운영자에 올리는 `data_out` 함수 — 묶음이 덮지 않는다)와 gateway 경로(`Kakao.API.request:<경로>`)로 적고 그대로 `use_scope` 가 된다. 이번에 실제로 부르는 함수는 같은 칸에 괄호로 적는다. 요구에 필요한 최소 묶음만 적는다. 기존 승인에 없는 이름공간·이름 지정 함수면 상태를 `범위 넓힘` 으로 둔다.
  > - `새 채택` 은 houserules §9 자격을 모두 만족할 때만 둔다. 필요 근거와 `lifecycle`(호출 대상이 생기는 때)은 Coordinator 후보 사실(`sdk-candidates/<id>/evidence.md`·`docs.html`)에서 인용한다. 사실을 지어내지 않는다 — 아직 없으면 «후보 사실 대기»로 적는다.
  > - 일반 라이브러리는 후보로 두지 않는다. 그런 결과는 서버가 만드는 설계나 범위 조정으로 간다.
  > - SDK 호출은 그 행의 기능 JS 하나에서만 하고, SDK 가 그리는 UI 는 쓰지 않는다.
  > - 공개 키 흐름(settings 이름 → VM → state → data 속성/`json_script`)을 파일 목록·행위 목록에 연결한다. 실패 동작은 «설정 실패(키 빈 값 · 다시 시도 없음)»와 «일시 실패(SDK 없음·예외)»로 나누고, G2 검증 행위(호출 경계 기록 대조·사용자 동작 안 호출·두 실패 행)를 적는다.
  > - 벤더 사본·등재 목록은 명세 파일 목록에 넣지 않는다(Coordinator 설치).
- **design-review-web** — 새 점검 항목 12:
  > 12. **공식 SDK**(명세에 SDK 사용 표가 있으면): 새 채택·판 올림·범위 넓힘·기존 등록 행마다 후보 사실과 houserules §9 자격을 대조한다.
  >     - 배포자가 그 서비스의 운영자인가
  >     - SDK 가 운영자 자기 서비스 API 의 클라이언트인가(운영자가 낸 일반 라이브러리가 아닌가 · `origins.operator` 가 비지 않았나)
  >     - 원본이 공용 라이브러리 CDN 이 아닌가
  >     - `evidence.md` 의 인용이 `docs.html` 원문에 grep 으로 실재하는가 · 무결성이 문서에서 왔는가(`integrity_from_docs`)
  >     - 필요 근거가 «서버·링크·native 대안 없음»을 문서로 보이는가
  >     - 라이선스·약관이 적혔는가
  >     - 제외 범주가 아닌가
  >     - «쓰는 SDK 기능 묶음»이 요구에 필요한 최소인가 · 새 이름공간이면 `범위 넓힘` 으로 표시됐는가
  >     - `namespace_members` 분류가 운영자 문서와 맞는가(사용자 자료를 운영자에 올리거나 지우는 함수가 `data_out` 인가 · SDK UI 함수가 `sdk_ui` 인가 · 수명 함수만 `lifecycle` 인가 · 경로를 받는 범용 함수가 `gateway` 이고 `gateway_paths` 의 `data_out` 경로가 운영자 쪽 효과(발송·올리기·끊기·철회)를 빠짐없이 덮는가)
  >     - 판 올림·범위 넓힘의 출처가 새 원문인가
  >
  >     하나라도 어긋나면 blocker 다. SDK 호출이 기능 JS 한 곳인지, 키 흐름이 settings → state → data 속성인지, 보내는 값이 서버가 정한 값인지(가림 판정을 JS 로 옮기지 않았는지), 두 실패 동작·검증 행위가 있는지도 본다. 기존 승인 행은 등재 목록 존재와 `use_scope` 안인지만 대조한다.
- **discipline-reviewer-web** — 새 점검 항목 10:
  > 10. **공식 SDK 소비**(감사 범위에 SDK 를 부르는 기능 JS 가 있으면): 아래 가운데 하나라도 어기면 blocker 다.
  >     - SDK 호출이 UI 동작 계약이 지정한 기능 JS 에만 있다
  >     - `use_scope` 밖 호출(로그인·사용자 API·위젯 렌더러 류 · 이름이 적히지 않은 업로드 함수 · 승인 경로 밖이거나 비리터럴 경로의 범용 요청)이 없다 — WV9 는 덫이다
  >     - 호출 함수를 부르는 순간 전역 경로로 찾는다
  >     - 초기화가 문서 수명 1회 멱등이다
  >     - 키가 data 속성·`json_script` 에서 온다(리터럴·전역 상수·환경 읽기 없음 — WV7 은 직접 리터럴만 잡는다)
  >     - 업무 판정·문구 조립·가림 판정이 JS 에 없다
  >     - 사용자 동작 안에서 `await` 없이 부른다
  >     - 결과를 모르면서 성공 표시를 하지 않는다
  >     - 외부 스크립트 끌어오기·외부 절대 URL 문자열이 없다 — WV8 은 덫이다
  >     - 검사용 분기·전역 훅이 없다
  >     - 벤더 사본·등재 목록은 «격리만» 본다(WV10 결과 — 벤더 바이트는 읽지 않는다)
- **coder-web** — «경계»에 새 항목:
  > - **공식 SDK**: 등재 SDK 는 명세 SDK 사용 표가 지정한 기능 JS 안에서, 승인 범위의 함수만, 부르는 순간 전역 경로로 부른다. `web/static/vendor/**`·`web/sdk_registry.json` 은 읽기만 한다 — 내려받기·복사·수정·개명·등재는 Coordinator 소관이고, 네 변경에 섞이면 백스톱 WV10 이 막는다. 명세에 없는 SDK·라이브러리·SDK 기능이 필요해 보이면 우회(파일 복사·CDN·동적 로드·다른 패키지)하지 말고 설계로 반송한다. 공개 키는 state 가 준 data 속성·`json_script` 에서만 읽고, 검증용 스텁·전역 훅을 기능 JS 에 넣지 않는다.

### 7-6. G2 결정성 — 가로채기 · 차단 · 더미 키(A13 문장)

> **공식 SDK 경계 확인**(명세 SDK 사용 표에 행이 있으면):
> - **차단 장치 — 브라우저 컨텍스트 단위**: 운영자 SDK 는 팝업(새 최상위 창)으로 요청을 낸다. 그래서 페이지 단위 가로채기로는 막을 수 없고, **컨텍스트 단위**로 막는다. Claude 는 Playwright MCP `browser_run_code_unsafe` 의 `page.context().route(…)`(팝업 포함)를 쓴다 — 도구 권한은 사용자 실행 경계를 따른다. CDP 채널은 `Target.setAutoAttach{autoAttach:true, waitForDebuggerOnStart:true, flatten:true}` 로 새 타깃마다 붙어 `Fetch.enable` 을 건다. 차단 대상은 **운영자 호스트만**이다(등재 `operator_domains` 의 점 경계 하위 ∪ `origins.operator`). 프로젝트 정적·미디어 CDN 은 막지 않고, 그 밖 외부 요청은 호스트별로 기록만 한다. 컨텍스트 단위 차단 장치가 없으면 기록기 case 만 하고(아래 ③ 래퍼가 1차로 막는다) «SDK 인자 검증·SDK 차단 실패 행: 미검증 — 차단 장치 없음»으로 적는다.
> - **가로채기**(`${CLAUDE_PLUGIN_ROOT}/assets/sdk_boundary.js` · 인자 = 등재 `lifecycle` + 운영자 도메인 + 승인 이름공간(`use_scope` 의 `<이름공간>.*`)과 그 `namespace_members` 분류표 + 이름 지정 함수 + 핵심 함수): 페이지 로드 뒤 스니펫이 다음을 설치한다.
>   - ① `Kakao.init` 류 초기화 함수를 감싸, 원 init 이 끝난 직후 **승인 이름공간의 함수를 분류표대로** 바꾼다(v3.2 · 규범 v3.1 m-2 · 검사기 v3.1 nit 4). `lifecycle`(`cleanup`)은 원본 그대로 둔다. 그 밖(`call`·`data_out`·`sdk_ui`·표에 없는 함수)은 모두 기록기로 바꾼다(`this.Share.*` — 명세가 부르는 함수만이 아니다 · 검사기 v3 nit 1). 실제 함수 목록에 표에 없는 함수가 있으면 그 case 는 발견이다. 감싼 init 이 `this === 전역`으로 불렸는지도 표지에 남긴다(검사기 nit 2). 실브라우저 늦은 초기화 페이지에서 이 경로가 발동했다(`thisOk=[true]` · 기록기 1 · 규범 nit-a · `run2.out` L1).
>   - ② 이미 초기화됐으면 그 함수를 바로 기록기로 바꾼다.
>   - ③ **운영자 대상 바깥 출구를 기록 전용으로 감싼다**: `window.open`(운영자 URL 이면 열지 않고 기록) · `HTMLFormElement.prototype.submit`·`requestSubmit` · 캡처 단계 `submit` 이벤트(action 이 운영자 호스트인 폼은 보내지 않고 action·target·method·필드 이름을 기록). 실물 `sendDefault` 의 숨은 폼 POST(`target="sharer"` · `app_key`·`validation_params` 등)가 여기서 멈춘다(규범 N1 · 검사기 N4).
>   - 클릭 **전에** `window.__dddjangoSdkBoundary.installed === true` 와 경로 표지(`init-wrapped`·`patched:<함수>`)를 확인한다. 실패하면 그 case 는 누르지 않고 미검증이다.
>   - 기록기는 함수 이름·분류·인자(JSON 사본 — 파일·바이너리는 표지로)·**파일 인자 표지**(인자 안에 File·Blob·FileList·FormData·바이너리·파일 입력이 있나)와 호출 순간 `navigator.userActivation.isActive` 를 남긴다. 다음은 발견이다 — `sdk_ui` 기록 · 이름 지정 원소 없는 `data_out` 기록 · 파일 인자 표지가 참인데 분류가 `data_out` 이 아닌 기록(분류표 오류 — 재승인) · 표에 없는 함수 · `gateway` 기록의 `url` 이 `use_scope` 의 경로 밖(v3.3 · 실측 `run6.out`). 클릭 뒤 **호출형 기록 1회 · 운영자 window.open·폼 기록 0 · 컨텍스트 경로의 운영자 요청 0 · 팝업 0** 을 확인하고, 기록을 `captures/sdk-<id>-<case>.json` 에 둔다. 기록기 0 인데 폼 기록이 있으면(제품이 옛 참조를 쥠) case 실패다 — 요청은 ③·차단에서 멈췄다.
> - **인자 검증**: 컨텍스트 차단 장치가 있을 때 데스크톱 viewport 에서 판형(가림 켬·끔)마다 1회, 기록된 인자로 **원래 함수**를 부른다. 기대는 셋이다 — 예외 0(`KakaoError` 는 동기로 던진다 [실측]) · 운영자 `window.open`·폼 제출 **기록** 각 ≥1(보내지 않음) · 컨텍스트 경로의 운영자 요청 0. 실제 발송은 0 이다.
> - **«실제 발송 0»의 정의**: ① 운영자 호스트로 가는 요청이 컨텍스트 경로(팝업 포함)에서 통과 0 이고 ② 운영자 대상 `window.open`·폼 제출은 기록만 됐다. 둘 다 배너 SDK 행에 수로 적는다.
> - **키**: 레인 서버 env 에 공개 키가 없으면 Coordinator 가 자기가 띄운 로컬 서버 프로세스 env 에만 비밀이 아닌 32 hex 더미 키를 준다(저장소·settings·env 파일 무변 · init 은 네트워크 0 [실측]). 사용자 서버면 키 유무를 묻거나 성공 case 를 미검증으로 둔다. `visual-check.md` 에 기록한다.
> - **무간섭**: 운영자 호스트를 막은 상태에서 SDK 파일을 막은 첫 화면과 불러온 첫 화면의 DOM 노드 수·스타일시트 수가 같다.
> - **실패 행**: SDK 파일 경로 하나만 막은 case(SDK 없음 = 일시 실패)와 키 빈 값 case(설정 실패)를 실제로 발동한다.
> - **라우트·래퍼의 수명**(규범 m-d): 운영자 호스트 차단 라우트는 G2 브라우저 세션의 시작부터 끝까지 컨텍스트에 둔다(W8 측정도 이 상태 — 넘길 글 ①). case 전용 라우트(«SDK 파일만 막기» 등)는 그 case 직전에 걸고 **case 가 끝나면 `context.unroute(<url>, <handler>)` 로 푼다**. 세션 끝에는 `unrouteAll({behavior:'wait'})` 다. 래퍼는 페이지 JS 라 새로고침·이동으로 사라지므로, **case 마다 새로 불러온 뒤 스니펫을 다시 설치**하고 설치 표지를 확인한다. W8 census·무간섭 비교는 스니펫 설치 **전**, 운영자 차단만 걸린 표준 라우트 집합에서 잰다. 캡처 기록(`captures/sdk-<id>-<case>.json`)에 그 case 의 라우트 집합(`["operator-hosts"]` · `["operator-hosts","sdk-file"]`)을 남긴다. 실측: «SDK 만 막기» case 뒤 해제·새로고침한 다음 case 에서 SDK 가 로드되고 래퍼가 사라져 재설치가 필요했다(`run2.out` RT).
> - **프로젝트 JS 가 시작한 외부 요청 0**(WV8 정적 덫의 SDK 레인 실행 짝 · v3.2 · 규범 v3.1 m-1 · 검사기 v3.1 minor 2): case 동안 페이지의 CDP `Network.requestWillBeSent`·`Network.webSocketCreated` 를 듣는다(Claude 는 `page.context().newCDPSession(page)` · Codex 는 같은 CDP 채널).
>   - **프로젝트 출처** = 레인 서버 출처 ∪ host 상태의 settings 정적·미디어·저장소 출처(`STATIC_URL`·`MEDIA_URL` 의 절대 출처 · 저장소 사용자 도메인). **프로젝트 JS** = 프로젝트 정적 출처의 `web/js/` 아래 기능 JS 와 등재 SDK 사본.
>   - **셈 대상**: 프로젝트 출처·운영자 호스트 밖으로 가는 `Script`·`Fetch`·`XHR`·`WebSocket`·`EventSource`·`Ping`(sendBeacon) 요청과 **하위 프레임** 문서 요청.
>   - **판정**: 시작(initiator)이 `script` 이고 시작 스택(부모 포함)에 프로젝트 JS 가 있으면 발견이다. 시작 스택이 없으면(`other` — `setTimeout(fetch, 0, url)`·`.then(fetch)`·EventSource [실측]) 보수적으로 발견이다. 시작이 `parser`(템플릿 태그 — WP2·빚의 몫)이거나 시작 스택이 제3자 스크립트뿐이면 기록만이다.
>   - **같은 출처 script**(v3.3 · 검사기 v3.2 minor): 시작 스택에 프로젝트 기능 JS 가 있거나 시작 스택이 없는 `Script` 요청은 **출처와 무관하게** 발견이다. 기능 JS 는 script 를 부르지 않으므로(WV8 ③④), 같은 출처의 미등재 vendor 사본 동적 로드도 여기서 드러난다(실측 `run5.out` b15). `srcdoc` 안에서 파서가 부른 script 는 시작이 `parser` 라 보이지 않는다(b16) — 정적 ④ 가 맡는다.
>   - **기록만**: 최상위 문서 이동과 팝업(사용자 조작이든 스크립트든 — 우리 출처에 코드를 들이지 않는다 · 운영자 대상은 ③ 래퍼와 차단이 따로 막는다) · 그림·글꼴·스타일·미디어. 운영자 호스트 요청은 abort 되고 따로 센다.
>   - CDP 비동기 스택(`Debugger` 도메인)은 켜지 않는다 — 기능 JS 의 `debugger;` 문에서 페이지가 멈춘다 [실측]. CDP 채널이 없으면 «외부 요청 판정: 미검증 — CDP 없음»으로 적는다.
>   - 남는 몫: 제3자 템플릿 스크립트가 시작 스택 없이 낸 요청은 거짓 발견이 될 수 있다(드물다 · 그런 태그는 이미 WP2 빚이다).
> - **실제 왕복**: 등록 도메인에서 사용자가 한다. 그 전에는 미검증이다.

- **실측 근거**
  - node(`probe/intercept_probe.out` · `probe/kakao_probe3.out` — 검토 `kakao_probe2.js` + 폼 래퍼): init 전 감싸기·init 뒤 교체 모두 기록기 1 · 네트워크 0. 옛 init 참조(CAP)·인자 검증(VERIFY)은 폼 기록 1 · **실제 제출 0**. 재초기화는 «Already initialized» 로 던지고 기록기를 유지한다. 잘못된 인자는 `KakaoError` 동기다.
  - **실제 Chromium**(`browser/run.out` · §1-9): 가로채기 없는 실물 클릭의 POST 는 팝업 내비게이션이라 `page.route` 0 · `context.route` 1(E1). v3 스니펫 아래에서 클릭(E2) · 인자 검증(E3) · 옛 참조(E4) 모두 운영자 요청 0 · 팝업 0. 인자 검증은 «real ok» 이고 폼 기록에 `app_key·ka·validation_action·validation_params` 가 있다. 무간섭은 노드 10 = 10 이다(E0).
  - v3.1 실측: 늦은 초기화 페이지의 init 감싸기 경로 발동(`run2.out` L1) · «SDK 만 막기» 뒤 해제·새로고침 다음 case 의 SDK 로드(`run2.out` RT) · 이름공간 단위 기록기의 `Share.sendScrap` 기록(`run3.out` — 함수 10개 기록기 · 운영자 요청 0 · 팝업 0).
  - v3.2 실측: 분류표 스니펫(`design-sdk/v32/browser/run4.out` — `cleanup` 통과 · 호출형 기록 1 불변 · data_out 파일 인자 · sdk_ui·표 누락 발견) · 외부 요청 귀속(`design-sdk/v32/browser/run5.out` — 기능 JS 몫 11 발견 · 템플릿·제3자·사용자 이동 기록만 · 프로젝트 CDN 셈 밖).
  - v3.3 실측: gateway 기록기(`design-sdk/v33/browser/run6.out` — 허용 경로 `pathOk` 참 · 친구 메시지 발송 거짓 · 운영자 요청 0) · 같은 출처 script 귀속(`design-sdk/v33/browser/run5.out` b15 발견 · b16 `srcdoc` 파서 script 는 보이지 않음).
  - 리허설 R4·R4+·R4++·R5·R6(§5-6)로 고정한다. 구현된 `sdk_boundary.js` 로 레인 scratch 복제본에서 다시 돈다.
- **결정성의 근거**
  - 운영자 호스트 요청이 0 이라 렌더·실측(W8 차단 게이트 포함)이 운영자 네트워크와 무관하다. 프로젝트 CDN 은 그대로라 그림·지문이 같다.
  - 기록기·래퍼는 브라우저 도구가 설치하므로 제품 코드에 «테스트용 분기»가 생기지 않는다.
  - SDK 가 그리는 UI 를 금지했으니 시각 비교 대상에 SDK 산출물이 없다. 무간섭 확인이 그 가정을 매번 검증한다.
- 이 기록은 `visual-check.md` ③ 의 «요소·배치·동작 대조» 칸과 captures 에 둔다. `visual-evidence.json` 스키마·`check_design_evidence.py` 는 바꾸지 않는다.

## 8. Codex 미러 · `make verify-web`

| 정본 | Codex | 미러 방식 | verify-web |
|---|---|---|---|
| `dddjango-web/scripts/**`(새 `sdk_vendor.py`·`src/sdk_registry.py`·`src/check_vendor.py`·`test/fixtures_sdk.sh` 포함) | `codex-dddjango-web/skills/dddjango-web/scripts/**` | byte | `diff -rq` 기존 |
| `dddjango-web/assets/sdk_boundary.js`(새) | `codex-dddjango-web/skills/dddjango-web/assets/` | byte | `diff -rq` assets 기존 |
| `HR` · `IU` · `AW` | 같은 상대 경로 | byte | `cmp` 기존 |
| `IJ` | `codex-dddjango-web/skills/implementation-javascript/references/final.md` | byte(지금도 동일 [실측]) | **`cmp` 줄 새로 추가** |
| `REQUEST_GUIDE.md` | `codex-dddjango-web/REQUEST_GUIDE.md` | byte | `cmp` 기존 + `request_guide_contract.py` |
| `CL` | `CX` | 의미 미러 · 단 대조 문단은 치환 뒤 byte | G2 배너 문단(A14)은 기존 대조 대상. **표지 `'**SDK 채택 확인(G1 배너 직전'` 을 대조 목록(`for p in …`)에 추가** — 이 표지는 A8 문단 머리에만 둔다(G1 배너 줄 문면에 같은 굵은 문자열을 쓰지 않는다 · n3) |
| agents 4 | `dddjango-web-<역할>/SKILL.md` 4 | 의미 미러 | 문면 리뷰 |
| houserules·IU·IJ·AW 의 `SKILL.md` 라우팅 표(§9·§8 행) | Codex `SKILL.md` | 의미 미러 | 문면 리뷰 |

- Codex Coordinator 는 질문 도구가 없다. G1 SDK 질문은 같은 문안을 평문으로 내고 그 턴을 끝내 답을 기다린다(빚 질문 판형).
- 명령 경로는 `${SKILL_DIR}/scripts/sdk_vendor.py`·`${SKILL_DIR}/assets/sdk_boundary.js` 다.
- 차단 장치는 Codex 쪽 가용 브라우저 채널의 요청 가로채기를 쓰고, 없으면 «미검증 — 차단 장치 없음»이다.
- 저장소 밖 문서
  - `AGENTS.md` 의 «검사 26종» → «39종 · 공식 SDK 등재 도구 `sdk_vendor.py`»
  - `docs/file_tree_web.html` 정적 자산 칸 설명에 `vendor/`·`sdk_registry.json`
- **봉인**: `workspace/tools/manifest_seal.py` 는 web 스크립트가 아니라 **Makefile** 을 봉인한다. S2·S4 의 Makefile 변경(IJ `cmp` · 문단 대조 표지)이 봉인 재발행 사유다(v1 의 «새 스크립트 글롭» 사유는 틀렸다 — 검사기 minor 11).

## 9. 사례 — spring_dream 6-3-13

**등재 항목**(해시·크기·호스트·기능은 [실측] · 승인 칸은 그 레인 값):

```json
{
  "schema": "dddjango-web-sdk-registry/2",
  "sdks": {
    "kakao_js_sdk": {
      "approval": {
        "at": "2026-10-0X HH:MM +0900",
        "binds": {"entry_sha256": "<도구 계산>"},
        "build": ".dddjango-web/<그 레인 폴더>/",
        "candidate_token": "kakao_js_sdk@2.8.3#b2ff7b30deff",
        "decision": "approved",
        "gate": "G1",
        "namespace_sources": {"(core)": "본인 직접(2026-10-0X HH:MM:SS +0900)", "Share": "본인 직접(2026-10-0X HH:MM:SS +0900)"},
        "source": "본인 직접(2026-10-0X HH:MM:SS +0900)",
        "source_line_sha256": {}
      },
      "docs_url": "https://developers.kakao.com/docs/en/javascript/download",
      "evidence": {"cites_source": true, "docs_sha256": "<도구 계산>", "fetched_from": "network", "integrity_from_docs": true},
      "features_in_file": ["API", "Auth", "Cert", "Channel", "Navi", "Picker", "Share"],
      "file": "static/vendor/kakao_js_sdk/kakao.min.js",
      "final_url": "https://t1.kakaocdn.net/kakao_js_sdk/2.8.3/kakao.min.js",
      "license": "Apache-2.0",
      "lifecycle": {"created_by_init": ["API", "Auth", "Cert", "Channel", "Navi", "Picker", "Share"], "global": "Kakao", "init": "init"},
      "name": "Kakao SDK for JavaScript",
      "namespace_members": {"Share": {"cleanup": "lifecycle", "createCustomButton": "sdk_ui", "createDefaultButton": "sdk_ui", "createScrapButton": "sdk_ui",
                                      "deleteImage": "data_out", "scrapImage": "data_out", "sendCustom": "call", "sendDefault": "call",
                                      "sendScrap": "call", "uploadImage": "data_out"}},
      "namespace_words": {"API": ["사용자 정보", "메시지", "친구"], "Auth": ["로그인", "카카오 로그인"], "Cert": ["인증", "전자서명"],
                          "Channel": ["채널"], "Navi": ["내비"], "Picker": ["친구 고르기", "친구 선택"], "Share": ["공유", "카카오톡 공유"]},
      "operator": "Kakao Corp.",
      "operator_domains": ["kakao.com", "kakaocdn.net"],
      "origins": {"operator": ["accounts.kakao.com", "apps.kakao.com", "cert-sign-fe.kakao.com", "developers.kakao.com",
                               "friend-picker.kakao.com", "kakaonavi.kakao.com", "kapi.kakao.com", "kauth.kakao.com",
                               "ocert.kakao.com", "pf.kakao.com", "sharer.kakao.com", "talk-apps.kakao.com"],
                  "operator_in_code": ["<위 12개 — 블록 주석을 지운 코드에서도 12개 [실측]>"],
                  "other": ["github.com", "itunes.apple.com", "openjsf.org", "www.apache.org"]},
      "public_config": [{"attr": "data-kakao-javascript-key", "call": "Kakao.init", "setting": "KAKAO_JAVASCRIPT_KEY"}],
      "service_api": "카카오톡 카드 공유 — 피드 템플릿 · REST 미지원",
      "sha256": "b2ff7b30deff3757ee5836c3a64016d6cd815b80d9b7ebffb2c4338d6bc5f7e0",
      "size": 87110,
      "source_url": "https://t1.kakaocdn.net/kakao_js_sdk/2.8.3/kakao.min.js",
      "terms_url": "https://developers.kakao.com/terms/latest/en/site-terms",
      "upstream_integrity": "sha384-oroumrnFVE0xtgqyDZJARgERibXg2C28380uaUZz2kHDS5CR7tu20eGiOU6GkTpy",
      "use_scope": ["Kakao.Share.*", "Kakao.init", "Kakao.isInitialized"],
      "version": "2.8.3"
    }
  }
}
```

- **출처**: 레인 G1 에서 사용자가 직접 답하면 `본인 직접` 이다. 발주자가 대신 답하려면 사용자가 배너 사실을 본 뒤 남긴 줄이 필요하다. 그 줄은 판 `2.8.3` 또는 표지 `kakao_js_sdk@2.8.3#b2ff7b30deff` 와 운영자·제품 낱말(도구가 뽑음 — `카카오`/`Kakao`·`SDK`)을 담는다. 발주서처럼 `web/`·`.dddjango-web/` 밖 파일에 커밋돼 있고 레인 HEAD 의 조상이어야 한다. 꼴은 `사용자 원문 docs/superpowers/orders/<발주서>.md@<커밋>:<행>(<시각>)` 이다.
- 09-28 결정 줄(`:74` · 2026-09-28 21:59:32 «가»)은 판도 표지도 없다. 그래서 **출처로 쓸 수 없다**(v1 의 `:75` 인용은 틀렸다).
- 다음 레인이 «카카오 로그인»을 붙이는 요청이면 Auth 묶음은 새 이름공간이다. 요청문(본인 직접)이나 커밋된 사용자 원문에 «카카오 로그인»이 있으면 그 줄이 출처이고 질문은 없다(G1 1급 행만). 없으면 G1 에서 한 줄로 묻는다.

**파일·경로**

| 파일 | 쓰는 쪽 | 내용 |
|---|---|---|
| `web/sdk_registry.json` | Coordinator(`install`) | 위 항목 |
| `web/static/vendor/.gitattributes` | Coordinator(`install`) | 고정 표지 |
| `web/static/vendor/kakao_js_sdk/kakao.min.js` | Coordinator(`install`) | 87,110 B · 운영자 원본 그대로 |
| `spring_dream_server/settings/base.py` | Coordinator(SDK 공개 설정 배선 · G1 승인 하 · Phase 2 진입 준비 ③) | `KAKAO_JAVASCRIPT_KEY: str = os.getenv("KAKAO_JAVASCRIPT_KEY", "")  # 카카오 공유 JavaScript 공개 키 — 빈 문자열이면 미설정(설정 실패 행) · Admin 키 금지` — 같은 파일 `:328` 의 선택형 꼴을 따른다 |
| `env/.env.base`(primary · 비추적) · 운영 env | 사용자·발주자 | 값. 플러그인은 쓰지 않는다. `env/.env.sample` 4절에 이름이 이미 있다 [실측] |
| `web/chart/chart/view_model/chart_view_model.py` | coder-web | `from django.conf import settings` → `kakao_javascript_key=settings.KAKAO_JAVASCRIPT_KEY` 를 state 에 |
| `web/chart/chart/state/chart_state.py` | coder-web | `kakao_javascript_key: str` · `kakao_share_card: …`(제목·설명·그림 절대 주소·공유 화면 절대 주소·단추 둘 — 서버 응답 `sharer_name`·`kakao_card_image_path`·`share_token` 에서 VM 이 조립) |
| `web/chart/chart/section/chart_share_sheet.html`(예시 이름) | coder-web | root·키·카드 자료 |
| `web/chart/chart/view/chart.html` | coder-web | `{% block scripts %}` 안에서 SDK 태그를 기능 JS 들보다 앞에 · `defer` 만 |
| `web/static/js/chart_kakao_share.js`(예시 이름) | coder-web | 기능 JS |

**템플릿**:

```html
{# view/chart.html — {% block scripts %} 안: SDK 먼저(속성 defer 만), 그 SDK 를 부르는 기능 JS 뒤 #}
{% block scripts %}
  <script defer src="{% static 'web/vendor/kakao_js_sdk/kakao.min.js' %}"></script>
  …(기존 기능 JS 들)…
  <script defer src="{% static 'web/js/chart_kakao_share.js' %}"></script>
{% endblock scripts %}

{# section/chart_share_sheet.html — 공유가 만들어진 뒤 HTMX 교체로 오는 조각 · 실행 script 0 #}
<div data-chart-kakao-share data-kakao-javascript-key="{{ state.kakao_javascript_key }}">
  {{ state.kakao_share_card|json_script:"chart-kakao-share-card" }}
  <button type="button" data-chart-kakao-share-button>카카오톡</button>
</div>
```

- `json_script` 는 필터 출력이라 WP2 가 보는 템플릿 원문에 `<script` 가 없다. data 속성 값은 순수 `{{ … }}` 다(WV7).
- 공유 만들기(`POST /api/decisive-fortune/chart-shares` · 1,077~1,244 ms [발주서 §2-7])는 클릭 **전**에 끝나 있어야 한다. 예를 들어 시트에서 가림을 고를 때 HTMX 로 만들고, 교체된 조각이 카드 자료를 싣는다. 그래야 «카카오톡» 클릭 안에서 SDK 를 동기로 부를 수 있다(발주서 §2-3).

**기능 JS 스케치**(v2 — 활성화 때 초기화 · 부르는 순간 찾기 · 두 실패):

```javascript
(() => {
  const ROOT = "[data-chart-kakao-share]";
  function initialize(root) {                              // 활성화 때 · 멱등 · 동기
    if (!window.Kakao) return "transient";                 // SDK 차단·로드 실패 → 일시 실패 행
    if (window.Kakao.isInitialized()) return "ready";
    const key = root.dataset.kakaoJavascriptKey;           // settings → VM → state → data 속성
    if (!key) return "config";                             // 키 빈 값 → 설정 실패 행(다시 시도 없음)
    window.Kakao.init(key);                                // 운영자 SDK 가 여기서 Share 를 만든다
    return "ready";
  }
  function activate(scope) {
    const roots = scope instanceof Element && scope.matches(ROOT) ? [scope] : [];
    for (const root of [...roots, ...scope.querySelectorAll(ROOT)]) initialize(root);
  }
  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const button = event.target.closest("[data-chart-kakao-share-button]");
    const root = button?.closest(ROOT);
    if (!root) return;
    const node = root.querySelector("#chart-kakao-share-card");
    const data = node ? JSON.parse(node.textContent) : null; // 서버가 정한 값 그대로
    const state = initialize(root);                         // 늦은 초기화도 같은 함수
    if (!data || state !== "ready") { /* 명세의 설정 실패 / 일시 실패 행 */ return; }
    window.Kakao.Share.sendDefault({                        // 부르는 순간 전역 경로로 · 클릭 안 · await 없음
      objectType: "feed",
      content: { title: data.title, description: data.description, imageUrl: data.image_url,
                 link: { mobileWebUrl: data.share_url, webUrl: data.share_url } },
      buttons: data.buttons.map((b) => ({ title: b.title, link: { mobileWebUrl: b.url, webUrl: b.url } })),
    });                                                     // 결과를 알 수 없음 → 성공 표시 없음(사용자 22:22:31 «가»)
  });
  document.addEventListener("htmx:load", (event) => activate(event.detail.elt));
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => activate(document), { once: true });
  } else { activate(document); }
})();
```

- 이 스케치에서 `use_scope` = `Kakao.init`·`Kakao.isInitialized`·`Kakao.Share.*` 다(WV9 대조 대상 · 부르는 함수는 `Share.sendDefault`). 외부 절대 URL 은 없다 — 공유·그림 주소는 서버 state 의 JSON 에서 온다(WV8).
- G2 가로채기는 두 경로를 다 덮는다(활성화 때 init 이 이미 돌았으면 직접 교체, 아직이면 init 감싸기).

**G2 확인**(§7-6):

- 운영자 호스트(`*.kakao.com`·`*.kakaocdn.net`)만 **브라우저 컨텍스트 단위**(팝업 포함)로 차단하고, 스니펫의 운영자 `window.open`·폼 제출 기록 전용 래퍼를 함께 건다. CloudFront 그림은 그대로다.
- 무간섭을 확인한다.
- 가림 켬·끔 × 시 있음·모름 × 양력·음력 case 마다 기록기 인자를 대조한다. `title` = 가린 모양 `sharer_name`, `imageUrl` = 같은 출처 200 PNG 800×400, 링크 = 공유 화면 절대 주소, 단추 = 둘, `userActivation` 참을 본다.
- 판형별 인자 검증을 1회 한다.
- 두 실패 행을 발동한다(SDK 경로 차단 · 더미 없는 빈 키 서버).
- 실제 왕복은 dev(등록 도메인)에서 사용자 계정·친구로만 한다(발주서 §4).

**6-3-13 의 길 — 품질 기본값은 (가) «이 판 릴리즈 뒤 등재 경로로만 시작»**(규범 M8 · B1 잔여 R1)

- **(가) 기본값**: 6-3-13 은 이 판이 릴리즈된 뒤 새 흐름으로 시작한다. `lane/6-3-13` 은 아직 없다 [실측]. 그래서 지금 고를 수 있다. G1 «새 SDK 채택» · 공개 설정 배선 · 등록이 한 레인에서 끝난다. 미등재 사본이 main 에 들어오지 않으므로 다른 레인의 main 받기에 red 가 번지지 않는다. 등재 SDK 를 가져온 병합은 diff 게이트 벤더 분기가 받는다(§5-1).
- **임시 사본 경로(개정 2c «이번 요청만 임시 허용»)는 폐기 권고**다. 사용자 결정(11:17:04)을 뒤집지 않는다 — 비용을 사실대로 적고 발주자가 판단한다.
  - **1.1.25 에서 레인은 사본 자리와 무관하게 막힌다.** 벤더 자리는 WS6+WP1+WP2, `static/js/` 자리는 WP1+WP2 다. 1.1.25 Coordinator 에는 «승인된 편차»를 받는 장치가 없다. exit 2 는 coder/architect 반송이고, 시안 빌드 Phase 3 는 실제 exit 0 을 요구한다. coder 가 «고치려고» 사본을 옮기거나 지울 수 있다. 이 플러그인 판으로는 임시 허용을 집행할 수 없다. 발주서가 하는 일은 플러그인 밖 운영이다.
  - **settings 이름이 없다**: `KAKAO_JAVASCRIPT_KEY` 는 env 견본에만 있다. 1.1.25 레인에는 settings 에 한 줄을 더할 정식 경로가 없다(G0 배선 6종 · coder 는 web/ 밖 금지 → 반송 (나) «/dddjango 발주»에서 멈춘다).
  - **병합 뒤 전파 — 출구 없음**: 임시 사본이 main 에 착륙하면, 그 main 을 레인 도중에 받는 다른 레인의 G2 에 WP1(+WS6)·WP2 가 뜬다. 백스톱 added 는 `git diff <git_snapshot>`(작업 트리 대비)이기 때문이다. G0 동결 뒤라 그 레인의 ⓐ/ⓑ 로 다룰 수 없고, 등록이 main 에 착륙할 때까지 출구가 없다. 1.1.25 에서도, 이 판에서도 같다(v3 의 늘 검사 축소는 «늘» red 만 없앤다 · diff 게이트 red 는 남는다).
- **이미 임시 사본이 main 에 있다면(복구 경로 — 권고가 아니다 · 이 판 릴리즈 뒤에만)**
  - 그 디렉터리는 «미등재»다. 늘 검사로는 막지 않고 WV12·G0 알림이 남는다.
  - 등록 입구는 `/dddjango-web:refactor web/static/vendor` 또는 그 칸을 쓰는 다음 web 요청의 슬라이스 0 이다. 바이트가 운영자 2.8.3 원본과 같아야 등록된다(`--register-existing` 이 다시 받아 대조한다). 태그가 §4-2 를 어겼으면 슬라이스 0 이 고친다.
  - 리팩토링 등록은 공개 설정 배선을 못 한다. settings 에 `KAKAO_JAVASCRIPT_KEY` 가 없으면 `ⓐ 재상정` «기능 요청 — 공개 설정 배선»이다(규범 N4). 그래서 실제로는 기능 요청 쪽 입구가 맞다.
  - 등록이 main 에 착륙할 때까지 다른 레인은 main 받기를 미루는 것이 diff 게이트 red 를 피하는 유일한 길이다.

## 10. 위험과 안전장치

| 위험 | 안전장치 | 남는 것 |
|---|---|---|
| 공급망 — 받는 길에서 변조 | https 원본만 · 리다이렉트 최종 주소도 운영자 도메인 · 운영자 문서 원문의 공개 무결성과 대조 · sha256 고정 · 등재 id 는 매 실행 재확인(WV2) · 자동 갱신 없음 | 운영자가 무결성을 공개하지 않는 SDK 는 «공개 값 없음»으로 배너에 보이고 사용자가 판단한다 |
| 공급망 — 정식 판 자체가 악성(운영자·CDN 탈취) | 판 고정 · 판 올림마다 변경 기록 URL 과 새 원문 재승인 · 로더 표지 계수 · G2 외부 요청 기록 · SDK 를 쓰는 페이지에만 로드 | 운영자 신뢰는 사용자 승인의 몫이다 |
| 벤더 불변식이 diff 게이트 안(검사기 B1) | 등재 id 디렉터리·목록·목록 시대 미등재 단위 대상의 늘 검사 WV1~WV6·WV13(정확성 · 그 디렉터리를 가리키는 모든 참조 · git 저장 바이트) | — |
| 작업 트리 ≠ git 저장 바이트(링크·필터·eol·대소문자) | WV2 ①~⑥ · vendor `.gitattributes` 고정 표지 · `.gitignore` 걸림은 `install` 거절·WV2 | `.git/info/attributes`(로컬)는 WV2 효과값으로만 잡는다 |
| 목록 손 편집·중복 키·병합 잔재 | 정규 바이트 · 엄격 파싱 | — |
| 결속 밖 칸의 몰래 변경 | `entry_sha256`(approval 밖 전 칸) | — |
| 옛 원문으로 승인·재승인 | 판 또는 도구 표지 필수(시각은 보조) · 도구가 만든 필수 낱말 · HEAD 조상 커밋 · `web/`·`.dddjango-web/` 밖 · 판 올림 새 판 · 직전 출처 거절 · 줄 sha256 | — |
| 레인의 자가 승인 | 두 출처 꼴만(도구 거절) · 대리 답 불가 · WV3 결속 · WV10 격리 · 명세 파일 목록 제외 · G2 배너 SDK 행 | 규칙을 어긴 Coordinator 의 허위 «본인 직접»(ⓑ 와 같은 신뢰 경계) |
| 승인이 파일 전체 기능으로 번짐(로그인·친구 메시지·인증) · 같은 묶음 안 사용자 자료 반출(업로드)·SDK UI · 경로를 받는 범용 함수(`API.request`) | `use_scope` · 함수 분류표(`data_out` 은 이름 지정 · `gateway` 는 경로 지정 · `sdk_ui` 금지 · camelCase 이름 바닥·경로 바닥 · 결속 안) · 배너의 기능·API 경로·호스트 전수 · WV9 · 범위 넓힘 승인 · G2 분류 대조(표에 없는 함수 · 파일 인자) | 간접 호출은 리뷰어 몫 · 분류의 최종 근거는 운영자 문서와 design-review-web 12 |
| 일반 라이브러리를 «SDK»로 이름 붙임 · 운영자 소유 라이브러리 CDN | 라이브러리 CDN 하드 거절 · 문서 직접 수집·원본 인용 필수 · O7 신호 · WV4 토큰 덫 · design-review-web 12 blocker · G1 배너 | 목록 밖 신규 CDN 은 사람 판단 |
| 무결성 출처 혼동 | 문서 원문에서만 `upstream_integrity` · 배너 문구 분리 · `fetched_from=file` 1급 표시 | — |
| 라이선스 | `license`·`license-header.txt` 보존 · byte 동일 사본이라 Apache-2.0 고지가 그대로 · `LicenseRef-…`(독점)는 배너 표시·사용자 수용 | 법률 검토는 범위 밖 |
| 약관(ToS) | `terms_url` 기록 · 카카오 주의 문구(사칭·판매 금지)와 다운로드 제공 실측 · 판 올림 때 재확인 | 운영자가 약관을 바꾸면 다음 판 올림까지 모른다 |
| 판 지원 종료 | `docs_url` 로 판 올림 요청 · 일시 실패 행이 사용자에게 보인다 | 감지는 현장 몫 |
| CSP | host 상태에 CSP 유무 · G1·G2 배너에 필요한 지시문 대조 1행 · CSP 편집은 web 배선이 아니라 «/dddjango 발주»나 사용자 몫(spring_dream 은 CSP 0 [실측]) | — |
| 키 하드코딩·Admin 키 노출 | settings 단일 출처 · 비밀 낱말 덫(WV1) · WV7(JS·템플릿) · 리뷰어 10 · «JavaScript 키만» 배너 | 간접 상수는 리뷰어 몫 · 꼴로 Admin 키를 구별할 수 없다 |
| 운영 env 누락 | 선택형 기본 + «설정 실패» 행 · G2·완료 보고 «운영 env 필요» 1행 | 배포 env 동기화는 발주자 |
| 기능 JS 의 외부 스크립트 끌어오기·외부 주소 리터럴·외부 네트워크 요청 · 템플릿 `javascript:`(조립·엔티티 콜론 포함)/`srcdoc`/SVG `set` | WV8 v3.3(리터럴 단위 · 이스케이프 해제 · 이어 붙이기 접기 · 스킴만·`스킴://` 허용 · 도메인 강약 규칙(약한 최상위는 URL 문맥) · `createElement`·`createElementNS` 리터럴만 · `script` 요소 금지 · `srcdoc` 대입·`document.write` 금지 · 표본 47 어긋남 0 · spring_dream 전수 기존 2줄뿐) · WP3 ③ v3.1(태그 밖·스킴 위치만 — 현장 오탐 0) · houserules §5⑤ «네트워크 요청은 프로젝트 출처로만» · **SDK 레인 G2 «프로젝트 JS 가 시작한 외부 요청 0»(같은 출처 script 포함)** | 정적 덫의 남는 몫은 모든 레인에서 discipline-reviewer-web 의 §5⑤ 읽기가, SDK 레인에서 리뷰어 10 과 G2 실행 확인이 맡는다. SDK 가 없는 레인에는 실행 짝이 없다 |
| 사용자 동작 상실(팝업·앱 전환 막힘) | IJ §8 동기 호출 · 자료 사전 준비 · G2 `userActivation` 기록 | 실기기 차이는 실제 왕복에서 |
| 결과 모르는 성공 표시 | IJ §8 · 발주서 토스트 제거(22:22:31) | — |
| 개인정보 | 사용자 동작 때만 전송 · 인자 = 서버가 정한 값(가림) · 페이지 단위 로드 · 범위 밖 기능(사용자 정보·토큰) 금지 · 리뷰어 대조 | — |
| 기록기 대체 불능(초기화 때 이름공간 재대입) | init 감싸기 + 직접 교체(실측) · 설치 표지 확인 전 클릭 금지 · 차단 하 인자 검증 1회 | 차단 장치 없는 채널은 미검증 |
| **실물 SDK 의 팝업·숨은 폼 POST 누출**(규범 N1 · 검사기 N4) | 컨텍스트 단위 차단(팝업 포함 · CDP auto-attach) · 운영자 `window.open`·폼 제출 기록 전용 래퍼 · «발송 0» 을 «통과 0 + 기록만»으로 정의 · 실브라우저 E1~E4 · R4 | 컨텍스트 차단 장치가 없는 채널은 래퍼만으로 막고 인자 검증은 미검증 |
| 목록 삭제·항목 삭제·개명(바이트 그대로 포함)·병합 해소 탈락으로 늘 검사를 피함(검사기 N2 · V3-2 · V3-3 · v3.1 nit 1) | WV13 «목록 시대» 판정(한 번 걸음 탄생 표 · `--full-history -m` · 이력상 등재 바이트 규칙 · 목록 유무 무관) · `remove` 는 디렉터리째 | 얕은 저장소는 «판정 불가» exit 1(미실행 · unshallow 뒤 다시) · rebase·squash 로 받은 목록 이전 사본은 WV13(고지 · merge 착륙 안내) |
| 늘 검사 비용(미등재 벤더가 많은 브라운필드 · 속도 배치와 충돌) | 단락(미등재 단위 없음 → git 0 · 목록 이력 없음 → 걸음 0) · 한 번 걸음 표 · 프로세스 안 blob 해시(200 파일 0.05 s / 0.13 s) | — |
| 깨끗한 설치와 미등재 사본(디렉터리·평면 파일)의 병합 경합(검사기 N1 · V3-1) | 늘 검사를 등재 id 디렉터리와 표지로 축소 · 목록 시대 전 미등재 단위는 WV12 · `verify` 를 병합 쪽 의무로 | 이 판 이전 설치본으로 목록 시대에 새 미등재 사본을 들이면 늘 red(§5-1 «경계») |
| OS 잡파일(`.DS_Store`)이 늘 검사·설치를 막음(검사기 N3) | 고정 목록 · 미추적/무시일 때만 제외 | — |
| G2 차단이 프로젝트 CDN 그림을 막음 | 운영자 호스트만 차단 · W8 넘길 글 ① | — |
| 미등재 사본이 무관 레인을 막음(규범 B1 · R1) | 늘 검사 대상에서 제외 · G0 알림 · 벤더 단위 입구 · 6-3-13 기본값 (가) | **그 사본이 main 에 들어오면 main 을 받는 레인의 diff 게이트 red 는 등록 착륙까지 남는다**(출구 없음 — 사실 고지) |
| 같은 settings 파일을 다른 레인도 고친다 | 한 줄 추가 · «배선 적용» 기록 · 병합 충돌은 보이는 실패 | spring_dream `base.py` 는 admin-1·8-C-0 도 고친다(발주서 §3) |
| 동시 채택 병합 | 보이는 충돌 · 병합 결과 `verify` | — |
| 판 올림 뒤 브라우저 캐시 | 모든 JS 와 같은 프로젝트 정적 캐시 정책 · 판 올림 레인 G2 배너에 «배포 캐시 정책 확인» | 정책이 없는 프로젝트는 모든 JS 변경이 같은 위험 |
| SDK 가 DOM·스타일을 주입해 화면이 흔들림 | SDK UI 금지 · G2 무간섭 확인 | — |
| 리팩토링이 벤더 바이트를 «정리» | 벤더 단위는 등재 정리 전용(등록·복원·미사용 제거) · 영역 범위·참조 grep 제외 · WV2 | — |
| 판 경계에서 빚 키 오판 | `debt-g0.json` `scanner` 판 대조 | — |
| `CL:222` 동시 편집 | 순차 착륙 | — |
| 6-3-13 임시 사본 | 기본값 (가) «릴리즈 뒤 등재 경로로만» · 임시 사본 경로 폐기 권고 · 이미 착륙했으면 복구 경로(§9) | 1.1.25 에서는 막힘·전파가 그대로다(사실 고지) |

## 11. 구현 계획

### 11-1. 파일

| 묶음 | 파일 | 내용 |
|---|---|---|
| **S1 검사기·도구** | `scripts/src/sdk_registry.py`(새) | 엄격 적재 · 정규 바이트 · 스키마 · 도메인 대조 · 결속 · 출처 꼴·원문 검사 · 덫·차단 목록 · `namespace_members` camelCase 이름 바닥 · `gateway_paths` 경로 바닥 · NFC 는 자리마다 `unicodedata.normalize` |
| | `scripts/src/check_vendor.py`(새) | WV1~WV13 · 대상 판정(등재 id·미등재 단위·목록 시대 — 단락 · `-m` 한 번 걸음 · 이력상 등재 바이트 · 얕은 이력 판정 불가) · WV8 리터럴 단위(v3.3 싱크) · WV9 분류·gateway 경로 대조 · OS 잡파일 제외 |
| | `scripts/src/common.py` | `STATIC_DIRS`+vendor · `WEB_TOP_FILES`+sdk_registry.json · 상수 · `mask_js` · `BackstopContext.sdk`(WV2 통과 집합 캐시) |
| | `scripts/src/check_structure.py` | WS1 · WS6(덫) |
| | `scripts/src/check_purity.py` | WP1 · WP2(통과 집합·속성·block·순서·교차 파일) · **WP3 확장** |
| | `scripts/backstop.py` | `wv` 패밀리 · `TOTAL_CHECKS=39` · 사용법 |
| | `scripts/src/debt.py` | 대상 판정 · 벤더 os.walk · OS 잡파일 · `undeferrable`(WV1~WV6·WV13) · WV11·WV12(단위마다) · WV13 목록 시대 판정 · `scanner` · 잔존 판 경계 |
| | `scripts/refactor_audit.py` | 벤더 단위(R0 수용 · 렌즈 0) · 영역·컨테이너 제외 · `REF_PATHSPEC` · self-test |
| | `scripts/sdk_vendor.py`(새) | candidate · install · verify · restore · remove |
| | `assets/sdk_boundary.js`(새) | G2 가로채기 스니펫(init 감싸기·직접 교체·운영자 `window.open`·폼 제출 기록 전용 래퍼 · 분류표(수명 함수 통과·표에 없는 함수·파일 인자·gateway 경로) · 시제품 scratch `design-sdk/v33/browser/sdk_boundary_v33.js`) |
| | `scripts/test/fixtures_sdk.sh`(새) · `fixtures_debt.sh` | K1~K53(K45+·K45b·K46+·K46b·K46c·K48b·K48c·K50b~K50e·K52b·K53b 포함) · D30~D38 |
| | Codex `scripts/**`·`assets/**` | byte 복사 |
| **S2 규범** | `HR`(§1·§3·§4·§5⑤·§7·§8·새 §9 · 목차) · `IU`(§5·§7) · `IJ`(§7 행·새 §8) · `AW`(§1) · 각 `SKILL.md` 라우팅 행 | §7-1~§7-4 · byte·의미 미러 |
| | `Makefile` | verify-web 에 `IJ` cmp |
| **S3 역할** | `agents/design-architect-web.md`·`design-review-web.md`·`coder-web.md`·`discipline-reviewer-web.md` + Codex 역할 `SKILL.md` 4 | §7-5 |
| **S4 Coordinator·가이드** | `CL`(A1~A26) · `CX`(같은 앵커) · `REQUEST_GUIDE.md` + Codex · `Makefile` 문단 대조 표지 · `AGENTS.md` · `docs/file_tree_web.html` | §6 · §6-11 |
| 봉인 | `manifest_seal.py --write`(Makefile 변경) | chore |

### 11-2. 검증

1. S1: `run_fixtures.sh`(기존 무변 green + 새 픽스처 K1~K53 · D30~D38) · 두 `refactor_audit.py --self-test` · 변이 검사(§5-6).
2. S2~S4: `make verify-web` · `claude plugin validate dddjango-web --strict` · 문면 리뷰.
3. 리허설(scratch 복제본만 · 저장소에 파일을 만들지 않는다 — 브라우저 도구의 작업 폴더도 scratch 로 지정한다)
   - ① 실제 카카오 2.8.3 `candidate`(네트워크 · 문서 직접 수집) → `install` → `verify` → gated 백스톱 → 빚 스캔 · P13·P14 재현이 red 인지 · 병합 경합(K40·K50)·강등(K42·K48·K49)·`.DS_Store`(K43) 재현 — 설계 단계 판정 규칙 시제품으로 검토자 시나리오를 이미 다시 돌렸다 [실측 `design-sdk/v31/v31_probes.out` · v3.2 `design-sdk/v32/v32_probes.out`(K48b·K50c·K50d·K51 포함) · v3.3 `design-sdk/v33/v33_probes.out`(K48c)]
   - ② html2canvas · `ajax.googleapis.com/ajax/libs/` 원본 시도 → WV4·exit 2
   - ③ **R4·R4+ — 실제 브라우저**: runserver 에서 구현된 `sdk_boundary.js` 로 가로채기(init 전·후 두 경로 · 늦은 초기화 페이지 포함) · 승인 이름공간 함수를 분류표대로 기록(수명 함수는 그대로) · `page.context().route` 운영자 호스트 차단(팝업 포함) · 운영자 `window.open`·폼 기록 · 인자 검증 1회 · 옛 참조 우회 · 무간섭 · 두 실패 행 · case 사이 라우트 해제·새로고침 · 분류표(수명 함수 통과·data_out·sdk_ui·표 누락) · 프로젝트 JS 가 시작한 외부 요청 0(CDP 귀속). 기대는 §5-6 R4·R4+·R4++·R5·R6 다. 설계 단계 시제품으로 이미 통과했다 [실측 `design-sdk/browser/run.out` E0~E4 · `run2.out`(늦은 초기화 · 라우트 수명) · `run3.out`(sendScrap) · v3.2 `design-sdk/v32/browser/run4.out`·`run5.out` · v3.3 `design-sdk/v33/browser/run5.out`·`run6.out` · 저장소에 `.playwright-mcp/` 등 파일 생성 0 확인]
   - ④ 미등재 단위(목록 없는 사본)에서 무관 레인 G2 0 · G0 알림 · `install` 허용 + 배너 줄 · 그 사본을 레인 도중 main 에서 받은 레인의 diff 게이트 red(사실 확인)
4. 설계 동결(v3.3 최종 확인 — 막힘 없음) → 구현(§16 여섯 건 포함) → 구현 검토(§16 대조) → 승인 후 커밋.

## 12. 의존 · 순서 · 릴리즈 배선

| 차례 | 묶음 | 조건 |
|---|---|---|
| 1 | W8e | 구현 중 |
| 2 | W6m | W8e 뒤 |
| 3 | S1 | 독립(Coordinator 문단 무관) — 병행 가능 · 무관 경우 동작 무변(K13) · 단 WP3 확장·WV8(외부 절대 URL 금지 포함)은 무관 경우에도 새 발견을 낸다(added 줄 · 빚 스캔에서는 기존 줄도 새 키 — 미룰 수 있음) — 릴리즈 노트 |
| 4 | S2 → S3 → S4 | S4 는 W8e·W6m 뒤 · **W8 커밋 ② 보다 앞**(`CL:222` 순차) |
| 5 | `make verify-web` → 봉인 chore(Makefile) → `make verify` → **`make release-web`** 한 번(W8e + W6m + S1~S4) | **`make release-web` 은 `verify-web` 을 돌지 않는다**(`_release` 는 `make verify` 만 · verify-web 은 2026-09-16 자동 경로에서 빠졌다). 그래서 릴리즈 직전 `make verify-web` green 을 사람이 확인한다 |
| 6 | W8 커밋 ②·③ | S4 위에 얹는다 · W8 자체 릴리즈. **W8 착수 조건**: `design-W8.md` v2 가 §6-10 넘길 글 ①~⑤ 를 옮겼다(이 설계는 W8 문서를 고치지 않는다 · 규범 닫힘 확인 N9) |

- **R8f(NFD/NFC) 와의 관계**: 등재 목록은 새 기록이라 이관 문제가 없다. 도구는 처음부터 NFC 로 쓰고, 검사는 NFC 로 바꾼 뒤 비교한다. 이는 `diag-R8f-nfc.md` 의 판형(«쓰기는 NFC · 비교는 정규화 뒤 · 옛 기록 고쳐 쓰기 없음»)과 같다. **공용 정규화 함수는 두지 않는다**(R8f §6 «공용 헬퍼로 묶을 필요는 없다(파일마다 몇 줄)» · 규범 v3.1 nit-6 ①). `src/sdk_registry.py`·`sdk_vendor.py` 는 비교하는 자리에서 `unicodedata.normalize('NFC', …)` 를 직접 부른다.
  - 원문 경로는 기록은 원문 그대로, `git show` 조회와 대조는 NFC 로 바꾼 꼴로 한다(git 트리 경로는 NFC — R8f §2 · nit-6 ②).
  - R8f 문서의 이 설계 인용(v1/v2 줄 번호 · «경로·문구 NFC 대조»)은 v3 부터 «낱말·시각만 NFC · 경로는 조회만 NFC»로 바뀌었다. 그 문서의 갱신은 R8f 개정의 몫이다(이 설계는 R8f 문서를 고치지 않는다).

## 13. 쟁점 — 사용자 결정 반영

- **결정됨(2026-10-01 14시대 · 문서 머리 발주 기록)**: «G1 에서 한 줄로 다시 묻기». 규범 닫힘 확인 §6 의 다듬기로 적용했다(§3-5 · §6-3 · §6-6).
  - 다시 묻는 단위는 **이름공간**(과 v3.2 의 이름 지정 `data_out` 함수)이다. `Share` 안의 호출형 함수를 더하는 것은 정보 줄이고, 새 이름공간(`Auth`·`API`·`Channel`·`Navi`·`Cert`·`Picker`)은 1문항이다.
  - **자명하면 묻지 않는다**: 요청 원문(본인 직접 요청문 또는 커밋된 사용자 원문)이 `namespace_words` 낱말(예: «카카오 로그인»)로 그 기능을 이미 말했으면, 그 줄이 출처이고 G1 1급 행만 둔다.
  - 첫 질문의 약속 «다른 기능은 쓰려면 다시 묻습니다»를 지킨다. 낱말 표는 첫 승인 배너에 보이고 결속 안에 있다.
  - **사용자 자료 반출 함수**(v3.2 — 같은 결정의 적용 · 규범 v3.1 m-2): 같은 이름공간 안이라도 사용자 자료를 운영자 저장소로 보내거나 지우는 함수는 묶음에 들지 않는다. 이름을 적어 G1 에서 한 줄로 다시 묻는다. SDK 가 그리는 UI 함수는 어떤 승인으로도 쓰지 않는다.
  - **경로를 받는 범용 함수**(v3.3 — 같은 결정의 적용 · 규범 v3.2 n1): gateway 경로마다 G1 에서 한 줄로 묻는다. 한 명세가 함께 들이는 data_out 이름·gateway 경로는 1문항으로 묶는다. 6-3-13 은 영향이 없다.
- **남은 사용자 쟁점: 없다.** 아래는 목적·기존 결정·플러그인 정의에서 나온 설계 판단이고, 알리기만 한다.
  - 늘 검사는 등재 id·목록·이력 대상에만 건다.
  - 승인 불요 복원 ⓡ1~ⓡ4 는 언제든 한다.
  - 09-28 줄은 출처가 될 수 없다.
  - 선택형 키가 기본이다.
  - 제거는 사용자가 빚 질문으로 정한다.
  - 6-3-13 은 (가)가 기본값이다(발주자 판단 · 임시 허용 결정은 뒤집지 않고 비용만 적었다).
  - WV10 (c) 상류 몫은 notice 로 둔다.
  - 얕은 이력에서는 WV13 을 판정하지 않고 멈춘다(거짓 발견도 거짓 통과도 내지 않는다).
  - 기능 JS 의 네트워크 요청은 프로젝트 출처로만 한다(houserules §5⑤ 보강 — 플러그인 정의 «web 은 내부의 외부 클라이언트»와 현장 관행에서 나온다).
  - 목록 이전 사본 가지는 merge 로 착륙하도록 알린다(규칙은 바꾸지 않는다 — 내용 기준으로는 rebase·squash 를 되돌릴 근거가 없다).

## 14. 처분 표 v1 → v2

### 14-1. 검사기·도구 검토(`review-sdk-tool/review.md` · 조건부 반려)

| 항목 | 처분 | 반영 |
|---|---|---|
| B1 벤더 불변식 diff 게이트 · P13·P14·K9 | **받음(일부 바꿔 받음)** — (a) 트리 정확성 → WV5 · (b) 모든 템플릿 참조 → WV6 · `install --replace`·`remove` 정리 · K9 기대 정정 · P13·P14 픽스처. **(c) «목록 없음 + vendor 있음 = 늘 발견»은 바꿔 받음**: 규범 B1 실측(진행 레인 7개 · 사본 하나가 무관 레인 전부를 막음)을 근거로, 목록이 있을 때만 늘(미룰 수 없음)로 하고, 목록이 없으면 이관 항목 WV12 + diff 게이트 + G0 알림 + `install` 전제로 정의된 경로를 준다. 미승인 실행 바이트라는 우려는 «목록은 비등재 사본이 없을 때만 생긴다»와 «새 파일·새 로드 줄 차단»으로 번짐을 끊어 받는다 | §5-1 · §5-2 · §3-3 · K24·K25a~c · D37 |
| B2 `--only wv` exit 0 불가 · 추적 조건 | 받음 — `sdk_vendor.py verify` · 추적 = check-ignore 거짓 + 인덱스 있으면 모드·blob · 커밋 여부는 WV10 (e) | §5-5 · §6-5 · K37 |
| M1 git 저장 바이트 | 받음 — WV2 ①~⑥ · 일괄 git 호출 · vendor `.gitattributes` | §5-2 · §4-1 · K19~K22 · D36 |
| M2 결속 범위 | 받음 — `entry_sha256` · `size`·`origins` 재계산 | §3-4 · K28 |
| M3 파서 | 받음 — 엄격 파싱 · 정규 바이트 | §3-1 · K23 |
| M4 WV6 범위 모델 | 받음 — WV10 = 빌드 기록·첫 부모·승인 병합·evil merge · 미커밋은 dirty 시작 금지와 짝 | §5-2 · A24(앵커) · K11·K36 |
| M5 템플릿 인라인 채널 · 키 리터럴 | 받음 — WP3 확장 · WV7 템플릿 분기 | §5-3 · K30·K31 |
| M6 동적 로드 | 받음 — WV8(모든 체제) | §5-2 · K32 |
| M7 기록기·차단 | 받음 — init 감싸기+직접 교체(실측 확인) · 표지 확인 전 클릭 금지 · 차단 장치 명시 · 더미 키 · 인자 검증 | §7-6 · §5-5 · `probe/` |
| minor 1 늘↔ⓑ | 받음 — `undeferrable` · A21 앵커 | §5-2 |
| minor 2 도메인 대조 | 받음 — urlsplit·점 경계·거절 목록·공용 접미사 | §2-1 · K27 |
| minor 3 WV4 대조 | 받음 — 토큰·결합형·목록 보강 | §2-2 |
| minor 4 WV5 정규식 | 받음 — `mask_js`·`?.`·대괄호 · 한계 명시 | WV7 · K33 |
| minor 5 순서 렌더 | 받음 — 페이지는 block scripts 안 | §4-2 · K34 |
| minor 6 비밀 덫 | 받음 | §3-2 · K29 |
| minor 7 origins | 받음 — 전수 + operator/other · 재계산 | §3-2 · §9 |
| minor 8 candidate 출처 | 받음 — final_url · 무증거 표지 · 재다운로드 대조 · 확장자 없는 원본 · SRI 다중 | §5-5 · K38 |
| minor 9 판 경계 | 받음 — `scanner` | §5-4 · D38 |
| minor 10 refactor grep | 받음 | §5-4 |
| minor 11 미러·릴리즈 배선 | 받음 — verify-web 수동 확인 명시 · 봉인 사유 정정 | §8 · §12 |
| minor 12 픽스처 기대값 | 받음 — K6·K8·K11 확정 | §5-6 |
| nit 1 문면 정확성 | 받음 — WP2 는 WV2 통과 집합 | §5-3 |
| nit 2 출처 경로·NFC | 받음 | §3-4 |
| nit 3 WV7(미사용) 파서 | 받음 — WV11 이 WV6 파서를 쓴다 | §5-2 |
| nit 4 확장자 대소문자·nomodule | 받음 | §5-3 · §4-2 |
| nit 5 시간대 | 받음 | §3-4 |
| 결정성·성능 · digest 재관찰 | 받음 — 배너 1행 · W8 넘길 말 ② | §6-9 · §6-10 |
| 빠진 음성 픽스처 · 변이 | 받음(WV 번호는 v2 체계로 다시 매김 · K25 는 체제 셋으로 나눔) | §5-6 |

### 14-2. 규범·보안 검토(`review-sdk-rules/review.md` · 수정 후 승인)

| 항목 | 처분 | 반영 |
|---|---|---|
| B1 WV1 «늘»과 §9 권고 | 받음 — 늘 검사는 목록이 있을 때만 · 목록 없는 벤더 칸은 diff 게이트+빚(미룰 수 있음). 이에 더해 이관 항목 WV12·G0 알림·`install` 전제를 둬 «정의된 경로»를 만든다(검사기 B1 과 화해) · 권고는 릴리즈 뒤로 한정 | §5-1 · §9 · K25a · D37 |
| M1 원문이 판·시각에 안 묶임 · `:75`→`:74` | 받음 — 시각 하한 또는 판 · 판 올림 새 판·새 원문 · 직전 출처 거절 · 저장소 상대 경로@커밋:행 + 줄 sha256 · 09-28 줄은 출처 불가 | §3-4 · §9 · K16 |
| M2 기능 범위 고지 | 받음(더 엄격하게) — 배너에 기능·API·호스트 전수 + `use_scope` 로 승인 범위를 묶음 · 범위 넓힘은 다시 묻는 것을 권장 기본으로 둠 · 이 선택은 §13 사용자 확인 | §3-2 · §6-3 · §13 · K39 |
| M3 공식 판정 순환 | 받음 — 라이브러리 CDN 하드 거절 · 토큰 덫 · O7 신호 · 호스트 전수 배너 | §2 · K27 |
| M4 무결성 출처 | 받음 — 도구가 문서 직접 수집 · `integrity_from_docs` 일 때만 «일치» · `--docs-file` 표지 · 리뷰어 grep | §2-1 · §5-5 · §6-3 |
| M5 «늘» 키 미룸 · 리팩토링 red | 받음 — `undeferrable` · A21 · 리팩토링 대상 무관 ⓡ 슬라이스 0 · 아니면 G0 정지+입구 | §5-2 · §6-8 #9 |
| M6 G2 차단이 CDN 그림 막음 · W8 | 받음 — 운영자 호스트만 차단 · host 상태에 CDN 출처 · «발송 0» 재정의 · W8 넘길 글 ① | §7-6 · §6-10 |
| M7 기록기 실행 불능 | 받음 — 검사기 M7 과 같은 판형 · 더미 키 · 인자 검증 1회 또는 미검증 표기 | §7-6 |
| M8 6-3-13 임시 권고 | 받음 — 1.1.25 막힘·전파·settings 부재를 사실로 쓰고, 권고는 «릴리즈 뒤에만»으로 한정 | §9 |
| M9 기존 등록 진입 | 받음 — R0 가 `web/static/vendor` 를 «등재 정리 전용»으로 받음 · R0·§6-8 문구 통일 | §6-8 · §5-4 · A19 |
| m1 설치 자가 검사 순서 | 받음 — 검사기 B2 와 같은 처리 | §5-5 |
| m2 승인 없는 제거 | 받음 — 기능 레인 자동 제거 없음 · WV11 빚 질문 · 저장소 전체 참조 | §3-6 |
| m3 선택형 키 | 받음 — 두 실패 · 운영 env 1행 · Admin 키 금지 · 비밀 덫 | §4-3 · §3-2 |
| m4 WV6 병합 우회 | 받음 — WV10 (c) | §5-2 |
| m5 결속 범위 | 받음 — `entry_sha256` | §3-4 |
| m6 바이트 안정성 | 받음 — vendor `.gitattributes`(루트 아님 — 격리·subst 충돌 회피) · 훅이 벤더를 덮으면 G1 배너 경고 · WV2 | §4-1 |
| m7 앵커 누락 | 받음 — A21·A22·A23(+A24·A25·A26) | §6-10 |
| m8 감사 범위 | 받음 — 격리만 · W8 (c) | §5-4 · §6-10 |
| m9 CSP | 받음 — G1·G2 배너 대조 1행 | §6-3 · §6-9 |
| m10 같은 물리 줄 · 3-1 보존 | 받음 — 순차 착륙 · W8 넘길 글 ③④ | §6-10 |
| n1 `G1′` 표기 | 받음 — 둘 다 받고 ASCII 로 저장 | §3-4 |
| n2 절대 경로 | 받음 | §3-4 |
| n3 대조 표지 | 받음 — A8 문단 머리에만 | §6-3 · §8 |
| n4 실측 재확인 | 확인(변경 없음) | — |

## 15. 처분 표 v2 → v3 · v3 → v3.1 · v3.1 → v3.2 · v3.2 → v3.3(닫힘 확인 여덟)

### 15-1. 규범·보안 닫힘 확인(`review-sdk-rules/closure-v2.md` · 수정 후 승인 유지 · blocker 0)

| 항목 | 처분 | 반영 |
|---|---|---|
| R1 B1 잔여 — main 받기 전파 · §5-1/§10 «영향 없음» 문면 · WV10 (c) 승인 줄 정지 | 받음 — §5-1 표·§10·§0 를 «main 을 받으면 등록 착륙까지 diff 게이트 red · 출구 없음»으로 고침 · 6-3-13 기본값 (가) · 임시 사본 경로 폐기 권고(사용자 결정은 뒤집지 않고 비용 고지) · WV10 (c) 상류 몫은 notice(내용은 늘 검사가 검증 — «모든 레인이 승인 줄 하나 때문에 멈춤» 해소) · evil merge 는 발견 유지 | §0 · §5-1 · §5-2 WV10 · §9 · §10 |
| R2 `install` 전제가 워크트리 단위 | 받음(검사기 N1 과 같은 근원 · 더 강하게) — 전제 대신 늘 검사를 등재 id 로 축소 · `verify` 를 병합 쪽 의무로(§3-7 · REQUEST_GUIDE §7) | §3-3 · §3-7 · §5-1 · §6-11 · K40 |
| R3 첫 채택 원문 조건 약함 | 받음 — 판 또는 도구 표지 필수 · 시각은 보조 · 필수 낱말은 도구가 생성(Coordinator 토큰은 덧붙이기만) · HEAD 조상 커밋 · `web/`·`.dddjango-web/` 밖 | §3-4 · WV3 · K16 |
| R4 G0 뒤 늘 red · 트리비얼 | 받음 — ⓡ 는 기준점 뒤에도 언제든(A20 근처) · 트리비얼 늘 red → 수정 모드 승격(A16) | §5-4 · §6-1 · §6-7 · §6-8 #13 |
| N1 인자 검증의 팝업 누출 | 받음 — 컨텍스트 단위 차단(CDP auto-attach) · 폼 제출·`window.open` 기록 전용 래퍼 · 기대 «폼 기록 ≥1 · 운영자 요청 0» · 실브라우저 E1~E4 실측 · R4 고정 | §7-6 · §5-5 · §1-9 · R4 |
| N2 O7 조임 | 받음 — 주석을 지운 코드 + 배포·문서 호스트 밖 운영자 호스트 ≥1 | §2-1 · WV4 |
| N3 범위 넓힘 원문 조건이 사람 말과 맞지 않음 | 받음 — 이름공간↔낱말 대응표(`namespace_words` · 결속 안) · 원문은 대응 낱말로 충분 | §3-2 · §3-4 ⑤ · §3-5 |
| N4 리팩토링 등록과 공개 설정 | 받음 — 벤더 단위 R1 에서 settings 이름이 없으면 `ⓐ 재상정` «기능 요청 — 공개 설정 배선» | §5-4 ⑥ · §6-8 · §9 |
| N5 처분표·본문 일관성 | 받음 — §0 «main 을 받지 않는 한» 취지로 정정 | §0 |
| N9 W8 문서 반영 | 받음 — W8 v2 가 ①~⑤ 를 옮기는 것을 W8 착수 조건으로 §12 에 적음(W8 문서는 고치지 않는다) | §12 · §6-10 |
| §6 사용자 쟁점 의견(이름공간 단위 · 자명하면 묻지 않음) | 받음 — 사용자 결정 «G1 에서 한 줄로 다시 묻기»에 그대로 적용 | §13 · §3-5 · §6-3 |
| 앵커 A1~A26 재검사 | 확인 — 같은 물리 줄(A21·A5 · A24·A4)은 S4 한 묶음에서 고친다 | §6-10 |

### 15-2. 검사기·도구 닫힘 확인(`review-sdk-tool/closure-v2.md` · 부분 닫힘)

| 항목 | 처분 | 반영 |
|---|---|---|
| N1 체제 전환 가드가 지역 검사 · 병합 경합 · K25b 가 굳힘 | 받음 — 늘 검사를 등재 id 디렉터리와 그 참조로 축소 · 미등재 디렉터리는 목록이 있어도 «등재 전» 의미론(WV12 · diff 게이트 · G0 알림) · `install` 전제 걷음 · K25b·K25c 기대 정정 · K40 | §5-1 · §5-2 WV5/WV6/WV12 · §3-3 · §5-6 |
| N2 목록 삭제 강등 | 받음 — 이력 판정 WV13(HEAD 에서 닿는 모든 목록 판의 id ∪ 작업 트리·인덱스·HEAD·기준점) · 항목만 삭제도 포함 · 목록 유무 무관 · `remove` 는 디렉터리째 · K42 · 얕은 저장소 notice | §5-1 · §5-2 WV13 · §3-6 |
| N3 `.DS_Store` | 받음 — 고정 목록(`.DS_Store`·`Thumbs.db`·`desktop.ini`·`._*`·`Icon\r`) · 미추적/무시일 때만 제외 · 추적되거나 참조되면 발견 · K43·K44 | §4-1 · §5-2 · §5-4 |
| N4 실물 `sendDefault` 의 숨은 폼 POST · `page.route` 의 팝업 사각 | 받음 — 규범 N1 과 같은 처리 · 검토 `kakao_probe2.js` 에 폼 래퍼를 더한 `kakao_probe3.out`(실제 제출 0) · 실제 Chromium E1(팝업 POST 는 `context.route` 에만 보임)·E2~E4(운영자 요청 0) | §7-6 · §1-9 · R4 |
| m1 WP3 조립 스킴 · SVG `set` | 받음 — 원문 `:` 앞 `{{`·`{%` 금지 · `set/animate` 의 href 금지 · K45 | §5-3 |
| m2 WV8 변형 7/7 · 등재 전 kakaocdn 리터럴 | 받음 — **외부 절대 URL 문자열 리터럴 전면 금지**를 평가해 채택했다. 근거: 기능 JS 의 외부 주소는 서버 state 로 오는 것이 규범(§5④ «URL 리터럴의 거처» · IJ §5)이고, 정당한 예외는 SVG 등 W3C 이름공간 URI 뿐이라 고정 목록으로 둔다. 거기에 `createElement` 대소문자·백틱·변수 · `createContextualFragment` · `eval`/`Function` 전달 · 문자열 타이머를 더했다 · K46 | §5-2 WV8 · §7-1 · §7-4 |
| nit 1(e) NFC 뒤 정규 바이트 · 입력 파일 엄격 파서 | 받음 — NFC 로 바꾼 값의 직렬화 = 원문 · `candidate.json`·`entry-draft.json` 도 엄격 파서 · R8f 판형과 같음(§12) · K47 | §3-1 · §3-4 · §5-2 WV1 · §5-5 |
| nit 2(g) `this` 없는 init 호출 | 받음 — 감싼 init 의 `this === 전역` 여부를 표지에 남김 | §7-6 |
| (b) P13 · (c) verify · (d) M1 하드닝 · (e) 결속 | 확인(닫힘) — K41 로 P13 회귀 보호 | §5-6 |
| 빠진 음성 K40~K47 · R4 · 변이 넷 | 받음 — 모두 §5-6 에 넣고 변이 목록을 넓힘 | §5-6 |
| 한계 «실제 브라우저 미실행» | 해소 — scratch 에서 playwright-core + 로컬 Chromium 으로 실측(저장소 파일 생성 0 확인) | §1-9 · §11-2 ③ |

### 15-3. v3 → v3.1 — 규범 닫힘 확인 v3(`review-sdk-rules/closure-v3.md` · 이전 지적 전부 닫힘 · 새 major 1)

| 항목 | 처분 | 반영 |
|---|---|---|
| **M-1** WP3 ③ 이 이름공간 `{% url 'ns:name' %}` 를 오탐(현장 4/216 · 전부 오탐) | 받음 — 엔티티를 풀고 태그를 자리표시로 바꾼 뒤 **태그 밖 첫 `:`** 를 찾고, 그 앞이 **스킴 자리**(`/`·`?`·`#` 없음)이면서 자리표시를 담을 때만 발견. 216개 재적용 오탐 0 · 기존 차단 사례 유지 · K45 짝에 «태그 안 이름공간 `:`»·«`?t=12:30`»·«`{{ base }}/a:b`» · 변이 «태그 밖 판정 제거» | §5-3 · §1-12 · K45·K45+ · §5-6 변이 |
| **m-a** 범위 넓힘 원문 조건과 가이드 문면이 어긋남 | 받음 — 필수 낱말을 승인 종류별로 나눔: 범위 넓힘 = 운영자·제품 낱말 + 그 이름공간 낱말(판 불요) · 채택·판 올림·등록 = 운영자 낱말 + 판/표지 · 가이드 §7 같은 말 · K39 에 «판 없는 "카카오 로그인" 줄 → 통과»와 «운영자 낱말 없는 "로그인" 줄 → 거절» | §3-4 ④⑤ · §3-5 · §6-11 · K39 |
| **m-b** `namespace_words` 품질을 기계가 안 봄 | 받음 — WV1 이 2글자 미만 · 운영자·`name` 토큰과 같거나 그 부분 · 토큰을 지우면 빈 낱말 · 이름공간 사이 겹침을 거절 · `install --dry-run` 이 운영자 문서 등장 수를 세어 G1 배너에(0회는 1급 표시) | §5-2 WV1 · §5-5 · §6-3 |
| **m-c** WV10 (c) 완화가 곁가지 재유입을 엶 | 받음 — 둘째 부모가 기준 가지(main · 없으면 origin/main) 이력이거나 승인 병합일 때만 notice · 그 밖 곁가지 몫은 발견 · 기준 가지 없으면 notice + 승인 목록만 | §5-2 WV10 (c) |
| **m-d** 컨텍스트 라우트·래퍼 수명 | 받음 — 운영자 차단은 세션 내내 · case 전용 라우트는 case 끝에 `unroute` · 세션 끝 `unrouteAll` · case 마다 새로고침 뒤 스니펫 재설치 · W8 측정은 설치 전 표준 라우트 집합 · 캡처에 라우트 집합 기록 · 실측 `run2.out` RT | §7-6 · R4+ |
| **nit-a** 실브라우저 init 감싸기 경로 미발동 | 받음 — 늦은 초기화 페이지로 실브라우저 발동 확인(`thisOk=[true]` · 기록기 1) · R4+ | §7-6 · R4+ |
| **nit-b** HEAD 조상 조건의 실제 경로 | 받음 — 발주자는 원문 줄을 레인 가지의 최상위 `docs/…` 에 커밋(8e 치환 확인의 문서 제외) · 또는 그 줄이 든 main 을 승인 병합으로 받은 뒤 · 가이드 §7 에도 | §3-4 · §6-11 |
| N9 W8 반영 «조건으로 닫힘» | 유지 — W8 착수 조건(`design-W8.md` v2 가 ①~⑤를 옮김)은 실제로 지킬 조건이다. 이 설계는 `design-W8.md` 를 고치지 않는다 | §12 차례 6 |
| **nit-c** `source_line_sha256` 의 대상 | 받음 — git blob 의 그 행 원바이트(줄바꿈 제외)를 해시 · 낱말·시각 대조는 NFC 뒤(R8f 판형) | §3-4 |

### 15-4. v3 → v3.1 — 검사기 닫힘 확인 v3(`review-sdk-tool/closure-v3.md` · 닫히지 않음(부분))

| 항목 | 처분 | 반영 |
|---|---|---|
| **V3-1** 평면 `vendor/kakao.min.js` 사본이 WV5 직속 규칙으로 병합 경합 red | 받음 — WV5 의 늘 범위를 등재 id 디렉터리와 `.gitattributes` 바이트로 줄임 · 직속 파일은 미등재 단위(목록 시대 전 → WV12 · 시대 안 → WV13) · K50 · 변이 | §5-1 · §5-2 WV5/WV12 · §4-1 |
| **V3-2** WV13 의 `git log -- 목록` 기본 단순화가 곁가지를 버림 | 받음 — 모든 이력 명령을 `--full-history` 로 고정(시대 시작 · 내용 탄생) · K49 · 변이 | §5-2 WV13 |
| **V3-3** 항목 삭제 + id 디렉터리 개명 + 변조로 강등 | 받음 — 검토자 권고 (가)의 «처음 들인 커밋에 목록이 있었나»를 더 단순·강하게 바꿨다: **미등재 단위의 지금 내용이 처음 나타난 커밋이 모두 «목록 시대»(목록을 들인 커밋의 자손) 안이면 WV13**. 근거: (가)의 «가장 오래된 추가 커밋»은 같은 초 커밋 순서·이름 재사용에 흔들려 같은 이름 사본(nit 2)을 거짓 발견했다(v3.1 첫 시제품 실측). 내용(blob) 기준은 개명·복사·변조에 강하고 이름과 무관하다. 목록 이전부터 있던 바이트만 WV12 다. 남는 비용(이 판 이전 설치본이 시대 안에 새 사본을 들이면 늘 red)을 고지한다 · K48 · 변이 | §5-1 «경계» · §5-2 WV13 |
| nit 2 같은 이름의 등재 전 사본이 WV13 | 받음 — 위 내용 기준으로 함께 해소(WV12) · K50b | §5-1 · K50b |
| m1 WP3 ③ 엔티티 콜론 놓침 · `?t=10:00` 오탐 | 받음 — 규범 M-1 과 같은 규칙(엔티티 해제 뒤 · 태그 밖 · 스킴 자리만)으로 둘 다 해소 · K45+ | §5-3 |
| m2 WV8 조립 우회 2/4 | 받음 — 스킴 붙은 리터럴(스킴만 든 `"https:"` 비교는 허용) · 도메인 꼴 리터럴 · `createElement` 비리터럴 인자 · `script` 요소 생성 금지(type 무관 — 현장 기존 2줄은 미룰 수 있는 빚) · 남는 한계(문자 코드·`atob`·계산된 속성)는 리뷰어 10 과 **G2 «외부 스크립트 요청 0» 실행 확인**으로 넘김 · 근거: 실행 등가를 정적으로 다 판정할 수 없고, 실제 로드는 실행에서 반드시 요청으로 드러난다 · K46+ | §5-2 WV8 · §7-6 · §10 |
| nit 1 스니펫이 함수 목록만 기록(`sendScrap` 기록기 0) | 받음 — 승인 이름공간의 함수 전부를 기록기로 · 실브라우저 `sendScrap` 기록(`run3.out`) · R4+ | §7-6 · §5-5 · R4+ |
| 보탤 픽스처 K48·K49·K50·K45+·K46+·R4+ · 변이 둘 | 받음 — 모두 §5-6 · 변이에 «`--full-history` 제거»·«직속 파일 늘 복귀»·«이름 이력 판정 복귀» | §5-6 |
| 재실행 결과 요구 | 이행 — 검토자 `v3_probes.py` 시나리오를 v3.1 판정으로 다시 돌린 결과가 major 3(V3-1·V3-2·V3-3)과 M-1 모두 기대값이다(§1-12 · `design-sdk/v31/v31_probes.out`) | §1-12 |

### 15-5. v3.1 → v3.2 — 닫힘 확인 v3.1 둘(`review-sdk-rules/closure-v31.md` · `review-sdk-tool/closure-v31.md` · 둘 다 «닫힘» · 새 blocker·major 0)

| 항목 | 처분 | 반영 |
|---|---|---|
| **규범 m-2** `Share.*` 승인이 `uploadImage`(사용자 파일 → 카카오 저장소 · 100일 보관)를 묻지 않고 덮는다 · `create*Button` 이 WV9 를 통과한다 · `cleanup` 이 기록기로 바뀌어 «호출 1회»가 흔들린다 | 받음 — 목록에 함수 분류표 `namespace_members`(`call`·`lifecycle`·`data_out`·`sdk_ui`)를 두고 승인에 묶는다. 묶음 `<이름공간>.*` 는 `call`·`lifecycle` 만 덮는다. `data_out` 은 `use_scope` 에 이름을 적어야 쓰고, 그 이름이 G1 1문항의 단위다(운영자 보관 사실을 질문과 1급 행에 적는다). `sdk_ui` 는 WV9 가 늘 거절한다. 도구는 이름 바닥(`upload·delete·…`·`create…Button`)을 강제하고 이름마다 사본 바이트 실재를 대조한다. G2 스니펫은 `lifecycle` 을 원본 그대로 두고, 표에 없는 함수·파일 인자를 대조한다. 검토자 제안 «`api-paths.txt` 로 함수 → 경로 대응»은 압축 코드에서 기계로 확정할 수 없어 배너의 사실로만 쓰고, 판정은 문서·이름 바닥·실행 대조로 한다. 실측 `run4.out` | §3-2 · §3-5 · §5-2 WV1/WV9 · §5-5 · §6-3 · §7-1 §9 · §7-4 · §7-5 · §7-6 · §13 · K52·K53·R4++ |
| **규범 m-1** ① WV8 의 짝이 SDK 레인 전용이다 ② «프로젝트 출처» 정의가 없다(CDN) ③ 사용자 조작의 최상위 이동을 센다 | 받음 — ① 문면을 정직하게 고쳤다. 모든 레인은 discipline-reviewer-web 의 houserules §5⑤ 읽기가 짝이고, SDK 레인은 리뷰어 10 + G2 실행 확인이 더해진다. 검토자 대안 «모든 레인 수동 청취»는 택하지 않았다 — W8 이 다시 짜는 3-1 문단에 모든 레인 규칙을 더하게 되고, 이 판에서는 리뷰어 읽기로 짝이 선다 ② 프로젝트 출처 = 레인 서버 ∪ settings 정적·미디어·저장소 출처 ③ 최상위 이동·팝업은 사용자·스크립트 모두 기록만이고, 운영자 요청은 따로 센다. 아울러 판정을 CDP 시작 스택으로 귀속해(프로젝트 JS 가 시작한 것 · 시작 스택이 없으면 보수적으로 발견) 템플릿·제3자 스크립트 요청의 거짓 발견을 없앴다. 실측 `run5.out` | §5-2 WV8 · §7-1 §5⑤ · §7-6 · §6-9 · §10 · R5 |
| **규범 nit-6 ①** 공용 정규화 함수 계획이 R8f §6 과 반대 | 받음 — 공용 함수를 두지 않고 자리마다 `unicodedata.normalize('NFC', …)` | §12 · §11-1 |
| **규범 nit-6 ②** 사용자 원문 경로의 NFC | 받음 — 기록은 원문 그대로, `git show` 조회·대조는 NFC 경로. R8f 문서의 교차 인용 갱신은 R8f 개정의 몫(이 설계는 고치지 않는다) | §3-4 · §12 |
| **규범 nit-3** `wss://`·문구 속 도메인의 교정 모양 | 받음 — `'wss://' + location.host`·`` `wss://${…}` `` 는 v3.2 에서 통과한다(검사기 minor 2). 문구 속 주소는 여전히 발견이고 교정은 서버 state 다. IJ §8 에 정상 모양 한 줄 | §7-4 · §5-2 WV8 |
| **규범 nit-4** `java{# c #}script:` | 받음 — 주석 마스킹 뒤 ① 이 잡는다는 사실을 WP3 행과 K45b 에 적었다 | §5-3 · K45b |
| **규범 nit-5** «같은 바이트» 예외 | 받음 — «목록 이전의 (등재된 적 없는) 같은 바이트 사본은 시대 안 복사도 WV12(미룰 수 있음)»를 문면에 적었다. 등재된 적 있는 바이트는 이력상 등재 바이트 규칙으로 WV13 이다 | §5-1 |
| **규범 nit-7** §11-1 픽스처 범위 «K1~K39» | 받음 — K1~K53(파생 id 포함) | §11-1 · §11-2 |
| **규범 nit-8** G0 ⓐ 뒤 G1 등록 거절 | 받음 — `ⓐ 재상정` «등록 거절 — 제거(별도 요청) / 출처 있는 ⓑ / 중단». 대리 실행은 기록하고 정지 | §6-8 #9b |
| **검사기 minor 1** 목록 이전 가지의 사본도 rebase·squash·cherry-pick 이면 WV13 으로 굳는다 | 받음(고지) — §5-1 표·«경계»에 적고, G0 알림 끝 구절과 REQUEST_GUIDE §7 에 «merge 로 착륙»을 더했다. §6-8 #8b · K50c. 원래 커밋이 HEAD 에서 닿지 않아 내용 기준으로는 되돌릴 근거가 없으므로 규칙은 바꾸지 않는다 | §5-1 · §5-4 · §6-8 · §6-11 · §7-1 · K50c |
| **검사기 minor 2** WV8 오탐 넷(`'wss://'+location.host` · `startsWith('https://')` · `li.me`/`div.app` · `socket.io`) · 놓침(`\x68ttps` · 외부 fetch·XHR) | 받음 — 스킴만·`스킴://`·`스킴://${…}` 허용 · 도메인 강약 규칙 + 선택자 첫 라벨 · 이스케이프 해제(③ 의 `createElement('\x73cript')` 포함) · G2 셈 종류를 script·fetch·XHR·WebSocket·EventSource·ping·하위 프레임으로 넓힘 · houserules §5⑤ 에 «네트워크 요청은 프로젝트 출처로만». 표본 27 어긋남 0. 조각 템플릿 fetch 1건은 정적으로 놓치고 R5 가 잡는다 | §5-2 WV8 · §7-1 · §7-6 · K46b · R5 |
| **검사기 minor 3** `--find-object` 가 파일당 0.17 s · 단락 없음 | 받음 — 단락 둘(미등재 단위 없음 → git 0 · 목록 이력과 작업 트리 목록 모두 없음 → 걸음 0) · 한 번 걸음 표 · 프로세스 안 blob 해시. 200 파일 0.05 s / 0.13 s(v3.1 문면 8.3 s / 11.5 s) · spring_dream 한 번 걸음 0.06 s | §5-1 · §5-2 WV13 · §10 · K51 |
| **검사기 nit 1** 기존 등록 SDK 를 바이트 그대로 개명하면 WV12 | 받음(규칙으로) — 검토자 대안 둘 가운데 «이력상 등재 바이트도 시대 내용»을 택했다. 다만 목록 이전에 **같은 경로**에서 생긴 바이트(K40·K50 임시 사본의 병합)는 WV12 로 남긴다. 무조건 시대 내용으로 보면 6-3-13 꼴(임시 사본 = 나중 등재 바이트)이 다시 늘 red 가 되기 때문이다(실측 K50d 는 WV12 유지). 개명은 WV13 이다(실측). 등재 밖으로 나간 SDK 는 WV9 범위 검사도 받지 않으므로, 실행 위험이 없어도 범위 이탈 길이라 막는다 | §5-1 · §7-1 §9 · K48b · K50d |
| **검사기 nit 2** `--find-object` 에 `-m` | 받음 — 한 번 걸음과 시대 시작 조회 모두 `-m` | §5-1 · §5-2 WV13 |
| **검사기 nit 3** WP3 `{% url 'a' %}:{{ x }}` 발견 | 받음(감수) — «태그 출력 바로 뒤 `:` 도 스킴 자리로 본다» 문장과 K45b | §5-3 · K45b |
| **검사기 nit 4** 스니펫이 `Share.cleanup` 을 기록한다 · 얕은 클론의 보수적 WV13 | 받음 — `lifecycle` 은 원본 그대로 둔다(실측: 기록 수 불변). 얕은 이력은 «판정 불가» exit 2(v3.3 에서 계약대로 exit 1 로 바로잡음 — §15-6) + `git fetch --unshallow` 안내다. 검토자 권고 «판정 불가 notice» 보다 한 걸음 더 갔다 — notice 만이면 강등을 놓치기 때문이다 | §7-6 · §5-1 · K51 · R4++ |
| 검토자 픽스처 K50c · K46 짝+ · K46+ · K51 · R4++ | 받음 — K50c · K46b(짝과 이스케이프 덫을 한 행으로) · K51 · 검토자 R4++(기능 JS 외부 fetch → G2 발견)는 이 설계의 R5 다. 이 설계의 R4++ 는 분류 실측이다 | §5-6 |
| 재실행 요구(검토자 탐침 · spring_dream 전수) | 이행 — 검토자 `v31_probes.py` 시나리오를 v3.2 판정으로 다시 돌렸다(`design-sdk/v32/v32_probes.out`): merge·평면 merge WV12 · rebase·squash·cherry-pick WV13(고지대로) · 같은 바이트 복사 WV12 · 변조 WV13 · 기존 등록 개명 WV13 · V3-3·V3-2 WV13 · 얕은 클론 depth 1~3 판정 불가(full WV12) · K50 현장 꼴 WV12 · K51 단락/한 번 걸음 — 모두 기대값. 규범 검토자 `wv8/scan.py`(main 2건)와 v3.2 WV8·WP3 판정을 spring_dream main·`b6f0ef25b`·레인 가지 머리 7·레인 워크트리 8 에 전수 적용 — WV8 적중은 어디서나 `conversation.js` `createElement("script")` 2줄 · WP3 0(`wv8_v32.out`) | §1-13 |

### 15-6. v3.2 → v3.3 — 닫힘 확인 v3.2 둘(`review-sdk-rules/closure-v32.md` · `review-sdk-tool/closure-v32.md` · 둘 다 «닫힘» · 새 minor 2 · nit)

| 항목 | 처분 | 반영 |
|---|---|---|
| **규범 n1(minor)** `Kakao.API.request` 가 이름 바닥상 `call` 이라 `API.*` 승인 한 번으로 친구 메시지 발송·업로드·연결 끊기 등이 묻지 않고 열린다 | 받음 — 다섯째 종류 `gateway` 를 두었다. gateway 함수는 묶음·이름으로 덮이지 않고 `use_scope` 에 `<함수>:<경로>` 로 경로마다 적는다. 경로 목록은 도구(`api-paths.txt` · 30)가, 분류(`read`·`data_out`)는 Coordinator 가 운영자 문서로 정하고 도구가 경로 바닥(`send`·`upload`·`unlink`·`revoke` …)을 강제한다(카카오 data_out 16 · read 14). `data_out` 경로는 m-2 와 같은 규칙(이름 명시 + G1 한 줄 + 1급 행)이고, `read` 경로도 경로마다 승인한다. gateway 경로에는 «자명하면 묻지 않는다»를 쓰지 않는다 — 결속된 낱말 표가 전제인데 경로 낱말을 미리 정하지 않았다. WV9 는 리터럴 `url` 을 대조하고(비리터럴은 발견), G2 기록기는 실제 `url` 을 승인 경로와 대조한다(실측 `run6.out` — 허용 경로 참 · 친구 메시지 발송 거짓). **6-3-13 영향 없음**: `Share` 함수 10개에 gateway 가 없고, 질문은 채택 1문항 그대로다 | §3-2 · §3-4 · §3-5 · §5-2 WV1/WV9 · §5-5 · §6-3 · §7-1 §9 · §7-4 · §7-5 · §7-6 · §13 · K52b·K53b·R6 |
| **검사기 minor** WV8 ③④ 의 실행 싱크 빈칸 — `createElementNS(XHTML·SVG, 'script')` · iframe `srcdoc` 대입 · `document.write` 가 실제로 실행되어, 같은 출처의 미등재 vendor 사본 동적 로드가 그물을 모두 비켜 간다 | 받음 — ③ 을 `createElementNS` 둘째 인자에도 적용한다(리터럴 `script`·비리터럴 발견). ④ 에 `.srcdoc` 대입·`setAttribute('srcdoc', …)` 와 `document`·`contentDocument`·`ownerDocument` 의 `write`·`writeln` 을 더하되 **값과 무관하게** 막는다(값 조건은 이어 붙이기로 빠진다). 실행 짝도 넓혔다: 시작 스택에 기능 JS 가 있는 `Script` 요청은 같은 출처여도 발견이다(실측 `run5.out` b15). `srcdoc` 안 파서가 부른 script 는 실행 확인에 보이지 않아(b16) 정적 ④ 가 맡는다. spring_dream 전수(main·가지 머리 7·워크트리 7)에서 새 싱크 적중 0 · 기존 2줄 그대로 | §5-2 WV8 · §7-1 §5⑤ · §7-4 · §7-6 · §10 · K46c · R6 |
| **검사기 nit** 얕은 클론 «판정 불가»의 exit 코드 | 받음 — 백스톱 계약대로 미실행 **exit 1**. 발견 키를 새로 정의하지 않는다(판정하지 않았기 때문이다) | §5-1 · §5-2 WV13 · §5-5 · §10 · K51 |
| **검사기 nit** WV8 ② `'https://'+'myapi.dev'`·`'i.cdn.io'` 놓침 · `'auth.user.me'` 오탐 | 받음 — 문자열 이어 붙이기를 접어서 보므로 `'https://' + 'myapi.dev' + '/v1'`·`'https://' + 'i.cdn.io' + '/x'` 는 ① 이 잡는다. 약한 최상위(`io·dev·app·co·me·xyz·cloud`)는 URL 문맥에서만 보므로 `'auth.user.me'`·`t('nav.about.me')` 는 넘긴다. 대가로 단독 약한 최상위 호스트(`'i.cdn.io'`·`'myapi.dev'`·`'cdn.socket.io'` 를 `join`·템플릿으로 주소로 만드는 꼴)는 문면 한계로 적었다 — 오탐은 레인을 막고, 놓침은 R5·리뷰어가 받치기 때문이다. 8진 이스케이프·템플릿 `${…}` 안 리터럴도 본다. 검토자 v3.2 추가 표본 7 포함 47 어긋남 0 | §5-2 WV8 · K46b · K46c |
| **검사기 nit** 마지막 `remove` 뒤에도 목록 시대가 이어져 새 사본이 WV13 | 의도다 — §5-1 «경계»에 «목록 시대는 끝나지 않는다»와 까닭(«처음 한 번 등록» 체제에 들어선 뒤 새 벤더 바이트는 등록으로만)을 적었다. 실측 K48c | §5-1 · §7-1 §9 · K48c |
| **검사기 nit** 등록 SDK 바이트를 옛 임시 자리(같은 경로)로 되돌려 개명하면 WV12 | 받음(규칙으로 — 한계로 두지 않음) — 이력상 등재 바이트 규칙을 좁혔다: 그 sha256 이 **지금 목록에 없으면** 어디에 있든 WV13, 지금도 등재돼 있을 때만 «같은 경로 예외»를 쓴다. 되돌려 개명은 WV13 이 되고(실측), K50d(임시 사본 = 지금 등재된 바이트)는 WV12 그대로다(실측). 제거한 SDK 의 옛 임시 사본이 병합으로 돌아오는 경우도 WV13 이 되며, 미참조면 ⓡ4 로 끝난다 | §5-1 · §7-1 §9 · K48c |
| **규범 n2(nit)** ① 같은 명세의 `data_out` 여러 개가 여러 문항 ② 이름 바닥이 부분 문자열(`put`·`store`…) | 받음 — ① 한 명세가 같은 이름공간에서 새로 들이는 `data_out` 이름·gateway 경로는 1문항 · 1결정 줄로 묶는다(`--scope-add` 여럿). ② 이름은 camelCase·`_` 토큰으로 나눠 대조한다 — `restoreSession`·`inputValue`·`outputText`·`createLink` 는 `call`, `putObject`·`storeToken` 은 `data_out`(실측 `floors.out`). sdk_ui 바닥도 토큰으로(마지막 `button`·`widget` · 첫 `render`·`mount`·`draw`) 좁혀 `createLink` 같은 호출형을 막지 않는다 | §3-2 · §3-5 · §5-5 · §13 · K53b |
| **규범 n3(nit)** 승인 전 함수 열거가 운영자 호스트만 막는다 | 받음 — 열거하는 동안 로컬(사본을 내는 임시 출처) 밖 요청을 모두 막고, 막힌 요청 수를 열거 파일 → `candidate.json` 에 남긴다 | §3-2 · §5-5 |
| 재실행 요구 | 이행 — 검토자 `v32_probes.py` 시나리오를 그 독립 판정 대신 v3.3 판정으로 돌렸다(`design-sdk/v33/v33_probes.out`): 받는 방식 merge·평면 WV12 · rebase/squash/pick WV13 · K50d WV12·WV12 · 같은 바이트 복사 WV12 · 변조 WV13 · K48b WV13 · **되돌려 개명 WV13**(v3.2 WV12) · 병합 WV13·WV12·WV13 · 얕은 클론 판정 불가(exit 1) · K51 0.04 s / 0.15 s · 마지막 remove 뒤 새 사본 WV13(의도). WV8 v3.3 은 표본 47 어긋남 0, spring_dream 전수 적중은 기존 2줄 · 새 싱크 0 · WP3 0(`wv8_v33.out`). gateway·같은 출처 script 는 실제 Chromium(`run6.out`·`run5.out`) | §1-14 |

## 16. 구현 단계 메모 — 구현자가 반드시 처리할 목록(v3.3 최종 확인 · 설계 막힘 없음)

v3.3 최종 확인(`review-sdk-rules/closure-v33.md` · `review-sdk-tool/closure-v33.md`)은 두 검토 모두 blocker·major 0 이다. 아래 여섯 건은 설계를 바꾸지 않고 구현에서 처리한다. 구현 리뷰는 이 목록을 하나씩 대조한다.

| # | 할 일 | 근거 | 확인 |
|---|---|---|---|
| ① | 시제품이 `API.cleanup` 을 기록기로 바꿔 «수명 함수는 그대로»(§7-6)와 어긋난다. 실제 `sdk_boundary.js` 는 모든 이름공간(gateway 이름공간 포함)의 `lifecycle` 함수를 원본 그대로 둔다 | 규범 최종 메모 1 · `design-sdk/v33/browser/run6.out`(`patched:API.cleanup`) | R6 에 «`API.cleanup` 통과»를 고정 |
| ② | gateway `url` 은 WV9(리터럴)와 G2 기록기(실제 인자)가 **같은 정규형**으로 대조한다 — 절대·상대 주소 · 쿼리 · 끝 `/` · 퍼센트 인코딩 · 대소문자. 정규형은 «운영자 호스트 점 경계 확인 → 경로만 · 쿼리 제거 · 끝 `/` 제거»이고, 정규화한 뒤 `api-paths` 밖 경로는 발견이다 | 규범 최종 메모 2 | K52b 에 절대 주소·쿼리·끝 `/` 짝 추가 · R6 같은 짝 |
| ③ | 판 올림 때 gateway 경로표를 다시 뽑는다. 새 판의 `api-paths` 와 승인된 `request:<경로>` 를 대조해 사라진 경로·새 경로를 G1 배너에 보인다. 새 경로는 승인 밖이다 | 규범 최종 메모 3 | `install --replace --dry-run` 픽스처(사라진 경로 1 · 새 경로 1) |
| ④ | REQUEST_GUIDE §7 에 «대리 실행은 경로 문자열 원문이 없으면 정지»를 한 줄 안내한다 — 문안: «사용자 정보·메시지처럼 카카오 API 를 쓰는 기능은 그 경로 이름(예: `/v2/user/me`)을 원문에 적거나 G1 에서 사용자가 직접 답합니다. «카카오 로그인 붙여 주세요» 같은 말만으로는 경로 승인이 되지 않아 대리 실행이 멈춥니다.» | 규범 최종 메모 4 · §3-4 ④ | `REQUEST_GUIDE.md`·Codex byte 미러 |
| ⑤ | WV8 싱크의 별칭·괄호·호출 우회 8꼴을 **토큰 규칙**으로 막는다: `f['srcdoc']` · `Object.assign(f, {srcdoc})` · `setAttributeNS(null, 'srcdoc', …)` · `d = f.contentDocument; d.write(…)` · `document['write'](…)` · `Document.prototype.createElement.call(…)` · `document.createElement.bind(…)` · `document['createElement'](…)`. 규칙: 기능 JS 의 `srcdoc` 토큰(식별자·문자열 모두) → 발견(템플릿 WP3 ② 와 같은 판형) · `createElement`/`createElementNS` 토큰 뒤가 «`(` + 단일 문자열 리터럴»이 아니면 발견(`.call`·`.bind`·`['createElement']` 포함) · `write`/`writeln` 은 `document`·`contentDocument`·`ownerDocument` 와 그것을 받은 지역 이름에 붙은 호출·괄호 접근을 발견. 이 경로로 넣은 parser script 는 R5 실행 확인에도 보이지 않으므로(§1-14 b16) 정적 덫만이 그물이다. spring_dream main 신규 적중은 0 이다 | 검사기 최종 메모 1(표본 49 = 문면 41 + 우회 8) | K46c 에 8꼴 추가 · spring_dream 전수 재확인 |
| ⑥ | K50e — 판 올림 뒤 옛 판 바이트의 «목록 이전 임시 사본»이 merge 로 돌아와 참조 중인 경우의 출구(§6-8 #6b)를 구현·픽스처로 고정한다 | 검사기 최종 메모 2 · 검토자 실측 `review-sdk-tool/v33_probes.out` | K50e(§5-6) |
