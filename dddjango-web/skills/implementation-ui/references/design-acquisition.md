# Claude Design 원본 수집과 브라우저 관찰

Claude Design URL은 원본을 찾을 주소다. Coordinator가 원본 파일과 실제 렌더를
확보한다. 원본 캡처가 필요하다는 조건은 사용자에게 캡처 작업을 배정한다는 뜻이 아니다.

## 1. 현재 원본 확보

`BUILD`는 산출물 폴더, `PROJECT`는 타깃 프로젝트 루트다. **`TARGET`은 평시에는 `BUILD`이고 재동결 중에는
그 빌드의 staging(`BUILD/_refreeze-<ts>`)이다** — 폐기·교체 대상 산출물을 쓰거나 읽는 인자는 `TARGET`을
가리킨다(§2 «재동결»). `--assets-root`는 언제나 `PROJECT`다.

- URL의 프로젝트·파일을 확인하고 가용한 DesignSync 읽기 도구로 파일 목록과 원본을
  수집한다. 링크 자체의 인증/접근 실패와 로컬 정적 분석기의 한계를 구별한다.
- 사용자가 제공한 동일 프로젝트 export는 정상 원본 수집 경로다. 폴더 전체를 같은
  상대 트리로 보관한다. 목록에서 고른 JSX 몇 개나 HTML만으로 export 전체를 대체하지 않는다.
  URL에서 일부 파일만 수집했다면 실제 수집 범위와 미확보 파일을 명시한다.
- 토큰 CSS, 컴포넌트, 런타임, 폰트·이미지 파일을 보존한다. 같은 시점의 파일 묶음인지
  확인한다. 다른 버전의 파일을 조용히 합치거나 런타임을 직접 만들어 원본으로 삼지 않는다.
- 프로젝트가 제공한 렌더 이미지도 목록에서 확인한다. 파일 이름·썸네일·한 장의 부분
  스크린샷만으로 전체 화면과 모든 상태의 렌더라고 판정하지 않는다.

## 2. 정적 수집과 원본 보관 선택

일반 HTML의 정적 의존성 수집은 `freeze_design.py`와 기존 `source_ready=true` 검사를
사용한다. `.dc.html`/JSX처럼 원본 엔진이 동적 컴포넌트를 조립하는 입력은 원본 보관과
브라우저 관찰을 사용한다. 확장자가 게이트 면제 사유이거나 렌더 불가의 증거는 아니다.

허용된 staging 폴더에 원본 수집을 마친 뒤, 실제 경로로 실행한다:

```bash
python PLUGIN/scripts/archive_design.py EXPORT/screen.dc.html --source-root EXPORT --out TARGET/design-ref --manifest TARGET/source-manifest.json
```

`EXPORT`와 `TARGET/design-ref`는 겹치지 않는 폴더다. manifest는 `design-ref` 밖의 형제
파일이다. 충돌이 있으면 새 staging을 사용한다. 이 명령은 `.DS_Store`를 제외한 전체
파일을 바이트 그대로 보관하며 `collection=archive`, `archive_ready=true`,
`source_ready=false`를 기록한다. manifest의 `dependencies`는 선택한 원본부터 따라간
참조 목록이다(`source_document`·`source`·`kind`·`local_path`·`status`·`reason`).
`ok`는 로컬 파일 존재, `missing`은 로컬 참조 누락/경계 이탈, `inline`은 내장 자원,
`external`은 외부 URL, `runtime`은 동적 해석이 필요한 참조다. 컴포넌트 안 자원의
상대경로는 참조 종류에 따라 컴포넌트 파일 또는 원본 HTML을 기준으로 해소한다.
`missing`이 있으면 바이트와 진단 목록을 보존하고 **exit 1**로 끝난다. 누락된 원본을
같은 버전에서 확보한 뒤 새 보관 경로로 다시 실행한다. `archive_ready`는 복사 완료이며 진행 승인이 아니다.
외부/동적 참조는 다음 원본 관찰에서 확인한다. **정적 의존성 완전 수집이나 렌더 성공을 주장하지 않는다.**
기존 실패 manifest의 필드를 손으로 바꿔 archive로 승격하지 않는다. 수집 진단 실패
내역은 보존해 관찰 검토에 전달한다. 실제 파일을 못 읽거나 보관하지 못한 실패는 해결한다.

### 재동결

재동결은 **기존 동결물을 전량 폐기하고 처음부터 다시 동결하는 것**이다. 차이를 대조하지 않는다.
사용자가 요청했을 때만 실행하며(자동 staleness 감지는 없다), **요청이 있으면 항상 전량 재실행한다** —
직전 결과를 재사용하거나 «이번 세션에 이미 했다»는 판단으로 생략하지 않는다.

파괴적 구간은 `refreeze.py`가 집행한다. live 빌드 폴더는 교체 순간까지 손대지 않는다.

```bash
python PLUGIN/scripts/refreeze.py begin --build BUILD --project-root PROJECT --quote "<재동결 요청 원문>"
# 재수집 — step 5-4·5-5를 그대로 다시 하되 경로는 TARGET(= BUILD/_refreeze-<ts>)이다
python PLUGIN/scripts/refreeze.py check  --build BUILD [--render-audit-skipped "<enum 사유>"]
python PLUGIN/scripts/check_design_evidence.py --build TARGET --project-root PROJECT --phase prepare
# 독립 검토 → --phase inputs exit 0 까지 staging 에서 통과시킨다
python PLUGIN/scripts/refreeze.py commit --build BUILD
```

`begin`은 staging을 만들고 입력(`scope.md`·`<screen>-declared.json`·`--excluded-regions` 입력)을
복사하며 `journal.json`에 **폐기 집합·고아·이미지 목록·기존 예외 행·기존 부채 결정**을 확정하고
`build-state.json.evidence_debt`를 `observe`로 기록한다.

**폐기 집합은 포인터로만 정한다** — `design-input.json`의 case에서 `reference_capture`·
`source_observation`, 그 관찰 문서의 `capture`·`trace`·`interactions`, 그 interactions 문서의
`initial.capture`·`steps[].after.capture`까지 3겹으로 순회하고, 여기에 `design-ref/**`·
`source-manifest.json`·`design-tokens.json`·`asset-manifest.json`·`screen-meta.json`·
`render-audit.json`·`design-input.json`·`coverage-review.md`·`scope.md`·`<screen>-declared.json`을
더한다. `visual-evidence.json`이 가리키는 구현 캡처는 재동결이 만들지 않으므로 **보존**한다.
`motion-notes.md`·`build-state.json`·`visual-check.md`·`design-spec.md`도 보존이다.

**고아**(`captures/` 중 어느 포인터에도 없는 파일 — 스모크 캡처·실패 회차 잔재·`captures/external/*`
같은 재수집 불가 수동 입력)는 **지우지 않는다**. `journal.json`에 기록되고 배너에 건수로 보고된다.

`check`(exit 0 완전·3 미완·1 오류)는 `--phase prepare`가 보지 않는 축까지 본다 — staging의
`design-ref/`·`source-manifest.json`·`design-tokens.json`·`asset-manifest.json`·`screen-meta.json`·
`design-input.json`·(`journal`의 `has_render_audit`이면) `render-audit.json` 실재, 3겹 포인터 해소,
archive 원본이면 case마다 v2 관찰 실재, 그리고 **폐기 집합이 3겹 포인터를 모두 덮는가**.
재측정이 렌더 실측 생략 enum 사유로 불가능하면 `--render-audit-skipped <사유>`가 journal 값을
내리는 유일한 경로다.

**`prepare` exit 2는 실패가 아니라 보완 루프 진입이다** — live가 무손상이므로 staging에서 몇 번이든
반복한다. 재수집 중 **live `scope.md`에 쓰지 않는다**: 실행 경계·렌더 실측 생략 사유·새 승인 원문은
staging 사본에만 적고 `commit`이 그것을 live로 옮긴다(live가 바뀌었으면 `commit`이 exit 1로 멈춘다).
독립 검토는 `scope.md` 최종 확정 뒤에 받는다.

`commit`은 **`check` 를 통과한 staging 에서만** 시작한다(통과 기록이 없으면 전량 폐기 전에 거부한다).
파일 단위 트랜잭션이며 `planned → discarded → installed → verified → done` 순으로 진행하고
`_prev-<ts>/swap-plan.json`에 단계를 적는다. 중단되면 `commit --resume`이 그 단계에서 이어간다.
**되감기는 단계 기록에 의존하지 않는다** — `abort`는 `_prev`에 실제로 들어 있는 것을 전부 되돌리므로
단계 «도중» 죽어도 원본이 사라지지 않는다. **디렉터리 이동은 하지 않는다**(`captures/`에 보존 대상이
섞여 있다). `installed`는 staging 쪽이 있으면 대상 존재와 무관하게 덮어쓴다. `verified`가 실패하면
되감고 이미지·부채까지 원상 복구한 뒤 exit 3이다.

`abort`는 staging을 지우기 전에 **`_discarded-<ts>/`로 한 세대 복사**한다. staging은 백업이
아니라 **재동결 산출물이 쌓이는 자리**이기 때문이다 — `begin`이 넣는 것은 `INPUT_GLOBS`뿐이고
`REQUIRED_STAGING`·`design-ref/`·관찰 문서는 거기서 새로 만들어진다. `_prev`가 있는 되감기도
설치분을 staging으로 되돌린 뒤 지우므로 같은 보존을 받는다. 복사는 **차단 사유가 아니다**(실패하면
경고만 내고 정리를 계속한다). 남은 `_discarded-*`는 다음 재동결을 막지 않고 게이트의 «untracked 0»
예외이며, 확인한 뒤 직접 지운다.

재동결은 `web/static/images/`에 **실제로 쓴다**(`--assets-root`는 언제나 프로젝트 루트다). 같은
이미지는 멱등이지만 인라인 이미지는 토큰이 밀려 새 파일명으로 떨어질 수 있다. 그래서 **실패 시
`abort`는 선택이 아니라 의무**이며, `journal.images_before` 차집합만 되돌린다 — 그 때문에 재동결 중
같은 프로젝트의 **병행 실행을 금지한다**.

결과는 «변화 0/차이 있음»이 아니라 **«무엇을 다시 동결했는가» 목록과 exit**로만 보고한다.
완료 빌드를 재동결하면 `implementation_visual`이 `pending`으로 내려가 G2 재대조 전까지 마무리
backstop이 막힌다. 승인된 `interaction_exclusions`가 있었으면 새 관찰의 target id 기준으로 행을
다시 짓는다(승인 원문·앵커는 staging `scope.md`에서 재사용 · 10% 상한은 새 분모로 재검증 ·
대응 단위를 못 찾은 행은 버리지 않고 배너에 올린다).

## 3. 에이전트가 원본 관찰

1. 원본 엔진을 가용한 브라우저로 열거나, 동결 export의 원본 런타임을 그대로 서빙한다.
   기존 서버를 쓰거나 사용자 실행 경계 안에서 loopback 서버를 시작한다. 자신이 시작한
   서버만 정리한다. 정적 스캔 실패를 이유로 브라우저 시도를 생략하지 않는다.
2. 실제 URL·원본 entrypoint·동결 버전이 대응하는지 확인한다. 인증 화면, 오류 페이지,
   비어 있는 런타임, 다른 상태의 화면은 원본 렌더가 아니다. 원본의 HTML/CSS/JS를 고쳐
   렌더를 꾸미지 않는다. 필요한 런타임/권한/파일을 구체적으로 복구한다.
3. 사용자 범위의 화면·단계·상태를 원본 컨트롤로 재현한다. 변경된 체크 상태·disabled·
   오류·완료와 기존에 재현되지 않았던 요소도 포함한다. 원본 데이터/상태를 임의 주입해
   자연스럽게 도달한 상태처럼 기록하지 않는다. 재개도 이전 실패 구현이 아닌 원본과 비교한다.
4. 창폭과 앱 콘텐츠 경계/크롭을 명시하고 상태별 원본 캡처를 에이전트가 저장한다.
   원본 캔버스에 여러 화면이 있으면 창 크기와 각 콘텐츠 크롭을 구별한다. 크롭에 맞추려고
   원본 치수·배치·스타일을 바꾸지 않는다. 원본과 구현의 비교 조건을 맞춘다.
5. 캡처와 함께 실제 브라우저 관찰 원문을 저장한다: URL·창 크기·콘텐츠 경계·상태 도달
   행동과 결과, 실제 DOM/스타일, 이미지 currentSrc·로드 크기, 폰트 로드/적용, 필요한
   네트워크 응답과 실패. CSS 배경·가상 요소·자식 장식도 확인한다. 접근 가능한 원본은
   기존 render_audit.js 전체를 실행해 치수·색·타이포 비교 자료를 확보한다.
6. 조작 상태 수집: entrypoint·viewport마다 드라이버를 실행해 실제로 조작해 본 기록을
   `interactions.json`으로 동결한다(필드는 design-evidence.md 「`interactions.json`
   version 1」이 단일 출처). Node 경로는

   ```bash
   node PLUGIN/scripts/observe_interactions.mjs --url URL --root '[data-screen-label="LABEL"]' \
     --viewport 560x1040 --crop-root --entrypoint-sha SHA --archive-sha SHA \
     --out TARGET/captures/<screen>-interactions.json --captures-dir TARGET/captures \
     [--declared DECLARED.json] [--excluded-regions EXCLUDED.json] [--hover-selectors HOVER.json] \
     [--playwright-module DIR] [--browser-channel chrome | --cdp WS] \
     [--max-steps N --max-depth N --max-minutes N] [--resume]
   ```

   로 부른다(모듈 경로·채널·CDP는 각각 env `DDDJANGO_WEB_PLAYWRIGHT_MODULE`·
   `DDDJANGO_WEB_BROWSER_CHANNEL`·`DDDJANGO_WEB_BROWSER_CDP`로도 줄 수 있다 — 둘 다
   없으면 exit 1 + 안내). exit 0은 완료, 3은 상한(`--max-minutes`/`--max-steps`/
   `--max-depth`)에 걸린 partial(문서는 이미 작성돼 있다), 1은 환경 오류(모듈·브라우저
   부재, 원격 URL 거부 등 — 문서 미작성)이거나 드라이버 예외다. Coordinator의 Bash
   도구 상한(≤600초) 때문에 드라이버는 백그라운드로 실행하고 호출 1회에
   `--max-minutes 8`을 주며, exit 3이면 같은 `--out`에 `--resume`을 더해 이어서
   실행한다(총 예산 90분 — 다 써도 archive/served sha가 그대로면 이어진다). 소스
   검토로 찾은 비의미 대상은 `--declared`(행마다 `selector`·`reason`, 선택
   `value` — 있으면 채움 표본보다 그 값을 우선한다)로 준다: 대상을 늘릴 뿐 줄이지
   못한다. `--excluded-regions`는 `{selector, reason}` 행 배열이다 — 선언에 매칭된
   요소는 스니펫이 `outside_root.count`에서 빼므로, 문서에 남은 `count>0`은 선언
   유무와 무관하게 결함이다(선언을 더 정확히 고쳐 다시 돌린다). MCP 경로에서는
   `browser_run_code_unsafe`의 `code`에

   ```js
   async (page) => (await import('<abs>/observe_interactions.pw.js')).default(page, {...})
   ```

   한 줄(같은 파일을 부르는 트램폴린 — opts가 없어 `filename`을 따로 지정하지
   않는다)만 넘긴다. `--cdp`로 붙었을 때는 그 브라우저가 이미 연 컨텍스트 안에서만
   관찰하며(인증 세션 유지), 모션 환원은 적용되지 않는다 — 실행 경계에 그대로 적는다.
   산출은 대상·잔여 근사·caps_hit를 담은 1행 JSON 요약과
   `captures/<screen>-interactions.json`·상태 캡처 PNG다. 같은 `--out`은 `--resume`이
   아니면 문서·PNG를 덮어쓰므로, 한 화면을 viewport마다 실행할 때는
   `--out captures/<screen>-<w>x<h>-interactions.json`으로 파일을 나눈다(상태 캡처
   PNG도 그 접두 `<screen>-<w>x<h>-`로 저장되므로 `--captures-dir`는 같은 `captures/`
   여도 겹치지 않는다) — 각 case의 `source_observation.interactions`가 자기 viewport의
   그 파일을 가리킨다(검사기는 case가 가리키는 경로로 읽는다). 잔여·`outside_root`·
   `declared_unmatched`·연결되지 않은 표면이 남으면 재실행이 아니라 실제로 보완한다:
   먼저 선언(`--declared`/`--excluded-regions`)을 늘려 다시 돌리고, 그래도 남으면
   case를 추가해 표면을 잇거나, 마지막으로 scope.md 사용자 승인을 받아
   `interaction_exclusions` 예외 행을 단다 — 사유 없이 잔여를 지우지 않는다.
7. 동적 URL과 폰트 fallback은 **그 상태에서 실제 표시된 결과**로 확인한다. 404를 전부
   무시하거나 `document.fonts.ready`만으로 정상이라고 판정하지 않는다. 실제 사용된
   폰트·이미지·컴포넌트와 해소되지 않은 실패를 구분하고, 구현에 필요한 추가 외부 파일은
   실제 응답에서 바이트를 확보해 출처와 함께 보관한다. placeholder·영상 자체 제작으로
   실제 API 자산 요구를 충족했다고 보고하지 않는다.

브라우저 관찰/자동 수집을 실제로 시도했는데 인증·도구 가용성·원본 파일 문제로
진행할 수 없을 때만, 시도한 명령/결과와 정확히 필요한 도움을 요청한다. 공유 접근
복구나 원본 export처럼 부족한 조건을 해소하는 최소 요청을 우선한다. 스크린샷 여러 장을
기본 과제로 넘기거나, 불편을 이유로 이전 게이트 없는 파이프라인을 권하지 않는다.

## 4. 원본과 관찰을 묶어 입력 검증

`design-input.json`의 case.entrypoint는 archive 안 원본 HTML/JSX를 유지하고,
reference_capture는 실제 원본 캡처를 가리킨다. source_observation에는
design-evidence.md의 archive 버전·case·캡처·브라우저 원문 연결을 작성한다.
PNG만 남겨 원본 소스의 버전 연결을 잃지 않는다. 여러 화면도 전체 트리의 archive manifest 하나를
공유하며, 각 case는 그 안의 해당 원본 HTML/JSX를 가리킨다.

source_observation은 **version 2**를 쓴다 — 위 6번에서 동결한
`interactions.json`을 가리키는 `interactions` 포인터가 늘어난 형태다(정확한 필드는
design-evidence.md 「`interactions.json` version 1」). case에는 그 문서 안 도달
지점을 가리키는 `reached_by`도 함께 적는다. version 1(포인터 없이)은 새로 관찰하는
어떤 case에도 쓸 수 없다 — `backstop.py`가 발견한 build가 git으로 완전히 추적되고
`--diff-base`(없으면 HEAD) 대비 무변경일 때만 그 build 자체가 legacy로 통과할 뿐이며,
이 조건은 `check_design_evidence.py`를 직접 호출할 때도 같은 legacy 플래그 없이는
적용되지 않는다.

```bash
python PLUGIN/scripts/check_design_evidence.py --build TARGET --project-root PROJECT --phase prepare
```

이 명령은 독립 리뷰 **전**의 파일·관찰 연결을 검사하고 `review_digest`를 반환한다.
`coverage_review`는 이때 null이어도 된다. prepare 성공은 G0/구현 허가가 아니다.
독립 입력범위 리뷰어에게 이 digest와 실제 원본·전체 archive·case·원본 캡처·관찰 원문·
수집 실패 내역을 준다. 리뷰어는 전체 사용자 범위와 실제 원본을 확인한 뒤
`reviewed-input: <digest>`와 `review-result: pass|fail`을 자기 반환 원문에 적는다.
Coordinator가 원문을 coverage-review.md로 보존하고 포인터를 연결한 뒤 현재 `inputs`를
실행한다. 실패는 해당 수집·관찰·검토 단계에서 해결한다. 사용자 승인으로 검사 결과를
대체하지 않는다. 소스·case·관찰 변경 시 prepare와 독립 리뷰를 다시 수행한다.
prepare/inputs는 각 case의 원본에서 로컬 의존성을 다시 탐색한다. 보관 목록에서 누락
파일의 행까지 함께 지웠거나 구형 manifest에 `dependencies`가 없어도 누락은 실패한다.

## 5. 외형과 내부 구조

원본 소스와 렌더가 외형을 정하고, 플러그인은 Django 책임·파일 분해·데이터 흐름을
정한다. 원본의 DOM 관계와 CSS 선언/값/효과 조합은 보존할 근거다. 템플릿·토큰·CSS
소유 위치로 옮기는 것은 허용하며, 그 과정에서 색·크기·간격·레이어를 근사하지 않는다.
원본 엔진/React 런타임 전체를 앱에 넣거나 업무 상태를 그 런타임에 맡기지 않는다.
최종 판정은 구현 화면의 실제 대조와 구조 검사 양쪽이 통과해야 한다.
