# 구현 리뷰 — W8 작은 판(`design/w8-v5` · `78a731bd..676127ba`)

- 대상 커밋: `21e70dfb`(도구·결정성) · `cab38019`(정확값 시트) · `676127ba`(감사·G2 연결)
- 내가 한 일: 이 scratch 의 `git clone --shared` 사본(`review-w8-small/repo`, HEAD `676127ba`, `.venv` 는 main 심링크)에서 읽기·실행만 했다. 플러그인·워크트리·main·spring_dream 은 읽기만 했다(spring_dream 은 `tokens.css` 를 시트 입력으로 읽음). Serena·Graphify·서브에이전트·서버·DB·네트워크는 쓰지 않았다. 로컬 헤드리스 Chromium 은 모든 요청을 abort/fulfill 한 채로만 썼다.

## 1. 판정

**수정 후 승인** — 보고 도구(수집기·대조기·CLI)와 문면 연결은 범위·판정 보존·결정성·미러가 모두 맞다. 다만 새로 만든 **정확값 시트**가 목적 사례(R11·R17·R18·R19 류)에서 «있는 토큰»을 «신규 등록 필요»로 잘못 적고(major 1), 레인당 1MB 안팎의 잡음 파일이라 참고 자료로 쓰기 어렵다(major 2). 시트는 막지 않는 참고물이라 blocker 는 아니지만, «새 결함은 배포 전에 고친다»에 따라 배포 전에 고쳐야 한다.

## 2. 발견

### major

**M1. 정확값 시트가 이미 있는 토큰을 «신규 등록 필요»로 적는다 — `color(srgb …)` 값·`color-mix` 토큰·hex alpha·서체 스택**
- 파일:줄: `dddjango-web/scripts/style_value_sheet.py:103-130`(`color()` — `Fraction(p) * 255` 를 그대로 비교) · `:145-150`(`color-mix(...)` 를 함수 튜플로 두어 어떤 관측값과도 같지 않음) · `:166-169`(`ff` 는 토큰 값 전체 문자열과 비교) · `:289`(일치 0 이면 무조건 `신규 등록 필요`) · 시험 `scripts/test/test_style_census.py:252-256`(`#01020380` 을 «일치 아님»으로 고정).
- 근거(재현)
  - Chrome 의 직렬화(로컬 헤드리스, 요청 전부 abort · `review-w8-small/color_probe.py`):
    `color-mix(in srgb,#1F1C18 6%,transparent)` → `color(srgb 0.121569 0.109804 0.0941176 / 0.06)` · `#01020380` → `rgba(1, 2, 3, 0.5)`(= `rgba(1,2,3,.5)` 와 같은 문자열). 채널은 유효숫자 6자리라 `0.992157×255 = 253.000035` 처럼 정수가 되지 않는다.
  - 함수 단위:
    ```
    cd review-w8-small/repo && python3 -B -c "
    import sys; sys.path.insert(0,'dddjango-web/scripts'); import style_value_sheet as s
    tv=s.token_values(':root{--glass-tint-strong: rgba(255,253,249,.52);}')
    print(s.canonical('color(srgb 1 0.992157 0.976471 / 0.52)','bg')==s.canonical(tv['--glass-tint-strong'],'bg'))"   # False
    ```
  - 실데이터: P1 시안 census(보관본 v3 → **측정 전용**으로 `census_version`만 4 로 올린 사본 `sheet/p1-design-bumped.json`)와 spring_dream 의 실제 `web/design_system/foundation/tokens.css` 로 시트를 만들면 `color(srgb …)` 값 행 **282개 중 토큰 후보 0개**(P2 135/0). 예:
    - `bg color(srgb 1 0.992157 0.976471 / 0.52)` → `신규 등록 필요` · 그런데 `tokens.css:40 --glass-tint-strong: rgba(255,253,249,.52)` 이 같은 색이다.
    - `sh color(srgb … / 0.07) 0px 2px 6px 0px, color(srgb … / 0.1) 0px 10px 28px 0px` → `신규 등록 필요` · `tokens.css:196 --shadow-2` 가 정확히 그 값이다(R11 의 shadow-2↔3 이 시트의 겨냥 사례였다).
    - `bg color(srgb 0.309804 0.541176 0.423529 / 0.14)`(jade 14%) · `bg …/ 0.06`(ink 6%) → `신규 등록 필요` · `tokens.css:77 --success-soft`, `:1279 --surface-muted` 가 있다. R18·R19 의 원인이 바로 «토큰 부재 → sunken 대체»였다(`exp-fidelity-p1-report.md:83-84`).
    - `ff Pretendard Variable`(67행)·`Gowun Batang`(30행) → `신규 등록 필요` · `--font-sans`·`--font-serif` 가 그 서체로 시작한다(v4 `ff` 는 첫 서체만 관측).
  - 영향: 규범 `architecture-web/references/final.md:141` «풀 밖 원본 값은 … 새 토큰으로 등록한다»와 겹치면, 시트의 거짓 «신규 등록 필요»가 **같은 값의 중복 토큰 등록**이나 «토큰 없음 → 대체»(R18·R19 형) 판단을 부추긴다. 시트가 겨냥한 사례(검토 §3 «무엇» 2의 R10·R11·R13·R15~R19)에서 색·그림자 쪽은 대부분 잡지 못한다(spring_dream 토큰의 `color-mix` 100곳).
- 권고(근접 일치가 아니라 **표현 정규화**로 푼다)
  1. `color(srgb …)` 는 Chrome 직렬화 정밀도(유효숫자 6자리)의 역변환으로 8bit 채널을 복원해 비교한다. 또는 토큰 색을 같은 규칙으로 `color(srgb …)` 문자열로 만들어 문자열 비교한다.
  2. 가장 흔한 `color-mix(in srgb, <색> p%, transparent)` 는 정확히 계산한다(채널 그대로·alpha×p). 그 밖의 `color-mix`·`rem`·`calc`·다중 선언처럼 **해석 못 한 토큰이 있을 수 있는 행**은 `신규 등록 필요` 대신 `수동 확인 — 해석 못 한 토큰 N개`로 적는다.
  3. hex alpha 는 관측 문자열이 8bit 반올림 뒤 값이므로 같은 반올림으로 비교하고, `test_alpha_is_not_rounded_to_eight_bits` 를 그에 맞게 고친다.
  4. `ff` 는 «첫 서체가 같은 토큰»을 `첫 서체 일치(스택 확인)`으로 표시하고 `신규 등록 필요`로 쓰지 않는다.
  5. 회귀 시험: 실제 Chrome 문자열(`color(srgb 0.121569 0.109804 0.0941176 / 0.06)` 등)과 `color-mix` 토큰으로 «일치»를, 0.11 대 0.1 같은 근접값으로 «불일치»를 함께 고정한다.
  - (대안) G0 브라우저에서 빈 문서에 `tokens.css` 를 넣고 토큰마다 계산값을 읽어 비교하면 브라우저 의미 그대로가 된다. 다만 설계가 바뀌므로 1~4 가 더 작다.

**M2. 시트가 레인당 0.8~1.1MB · 행 절반 이상이 기본값/키워드 · 후보가 범주 무관 — 참고 자료로 쓰기 어렵고 문맥 비용 위험(M4 재발)**
- 파일:줄: `style_value_sheet.py:243-245`(묶음 키에 `s` 전체·`op`·`pwh`) · `:265-277`(구성원·부모/조상·자식 목록 전부 나열) · `:278-290`(모든 관측 속성 행 출력 · 기본값 제외 없음 · 후보는 속성 범주와 무관하게 값만 비교) · 실행 `:282-283`(행×토큰 전수 비교).
- 근거(재현 — 위 측정 사본, 토큰은 spring_dream 실물)
  ```
  python3 -B repo/dddjango-web/scripts/style_value_sheet.py --census sheet/p1-design-bumped.json \
    --tokens /Users/hyun/Desktop/spring_dream_server/web/design_system/foundation/tokens.css --out sheet/p1-design.md
  ```
  - P1 시안: **1,108,053B · 7,739줄 · 묶음 233 · 46.6초**. P2 시안: 790,258B · 37.1초. P1 구현 v4 census(`run/p1-plant-base7`, 원래 v4): 1,210,691B · 52.3초.
  - P1 표 행 5,401개 중 3,004개(56%)가 `none`·`auto`·`normal`·`0`·`rgba(0, 0, 0, 0)` 같은 기본값/키워드다. 그중 753행은 `신규 등록 필요`(예: `minh auto`, `gap normal`), 2,163행은 엉뚱한 토큰이 붙는다 — `op 1` → `--settings-toast-z`·`--user-info-card-z`(z-index), `bf none`·`maxh none` → `--shadow-0`, `pad 0px` → `--ls-caption`(자간)·`--employee-choice-source-opacity-hidden`, `lh 13px` → `--fs-caption`, `bd.top.width 1px` → `--chat-review-stars-tracking`. 후보 5개 이상인 행 1,802개.
  - 4면 합성 행 `bd 0 | 0 | 0 | 0` 은 CSS 값이 아닌 census 표기라 늘 `신규 등록 필요`다.
  - 이 파일 경로가 architect·coder 입력에 붙는다(`agents/design-architect-web.md:14`, `agents/coder-web.md:16`). 읽으면 Read 한 번에 2,000줄(≈28만 B)이 들어가고, 안 읽으면 효과가 없다. 검토 M4(문맥 비대 = 속도 손해)를 다시 만든다.
- 권고
  1. 기본값/키워드(`none`·`auto`·`normal`·`0`·`transparent`·`visible`·`static`·`flow` 등)와 census 합성 표기(`bd` 4면 합성)는 행에서 뺀다.
  2. 후보를 속성 범주에 맞는 토큰으로 좁힌다. 최소한 색 속성 ↔ 색 토큰, 길이 속성 ↔ 길이 토큰, 단위 없는 수는 `fw` 등 해당 속성만 허용한다. 하우스룰의 `--color-*`·`--space-*` 같은 이름 규칙(`discipline-web-houserules/references/final.md:142`)을 보조로 쓸 수 있다.
  3. 구성원·부모·자식 목록은 개수와 앞의 몇 개만 남긴다. 맨 앞에 «속성 범주 · 값 → 정확 일치 토큰 · 등장 묶음 수» 색인 표를 두면 architect 가 그것만 읽어도 된다.
  4. 토큰을 속성별 정규형으로 미리 색인해 행×토큰 전수 비교를 없앤다(수십 초 → 1초 안팎).
  5. 실제 크기의 census 로 «시트 ≤ ~100KB» 같은 크기 상한 시험을 둔다.

### minor

- **m1. 입력 오류 exit 1 뒤 이전 `style-report.json` 이 그대로 남는다**(`compare_style_census.py:870-889`, `:919-922`). 재현: 유효한 보고를 `cli/stale.json` 에 쓴 뒤 `--mapping` 에 없는 case 를 넣고 같은 `--out` 으로 다시 돌리면 `W8 미실행: mapped case missing …` · exit 1 이고 파일은 이전 내용 그대로다(`cmp` 동일). 반대로 «일부 case 미실행»의 exit 1 은 새 보고를 쓴다. 문면(`design-evidence.md` «실패한 실행에서 이전 report 파일을 새 결과로 읽지 않는다»)만으로는 둘을 가르기 어렵다. 권고: 시작할 때 `--out` 을 지우거나 임시 파일에 쓰고 성공 때만 바꿔 넣는다. 그리고 «exit 1 + 새 보고 = 일부 case 미실행, 나머지는 유효»를 한 줄 적는다.
- **m2. 두 CLI 가 `KeyError`·`TypeError`·`AttributeError`·`IndexError` 까지 잡아 «미실행»으로 바꾼다**(`compare_style_census.py:920`, `style_value_sheet.py:311`). 도구 결함(예: 키 오타)도 `W8 미실행: 'ord'` 한 줄이 되고 traceback 이 사라진다. 잡지 않아도 Python 은 exit 1 로 끝나므로 얻는 것이 없다. 권고: 파일·JSON·검증 단계의 `OSError`/`ValueError` 만 잡는다.
- **m3. 시트는 G0 시점의 `tokens.css` 로 고정된다**(Coordinator `dddjango-web.md:173`). G1·Phase 2 에서 토큰을 새로 등록하면 «신규 등록 필요»가 낡는다. 그런데 다시 만들 지점이 없다. 권고: Phase 2 진입(또는 3-2) 때 한 번 다시 만든다는 한 구절을 넣는다.
- **m4. 빌드 폴더는 기본 커밋 대상**인데(`dddjango-web.md` «`.gitignore`에 넣지 않는다»), census 원자료는 한쪽에 1.2~2.3MB(보관 P1/P2 실측)이고 시트는 ~1MB 다. 회차 보존까지 더하면 레인당 수 MB 가 대상 저장소에 쌓인다. 권고: `observations/` 원자료를 커밋할지 무시할지 `design-evidence.md` §W8 에 한 줄로 정한다.

### nit

- n1. Coordinator 의 «네가 직접 쓰는 것» 목록(`dddjango-web.md:8`, `:288`)은 `observations/style-*.json`·`style-values.md` 만 적는다. 3-1 비교용 데이터 하네스(코드)의 작성 주체와 자리(빌드 폴더 `observations/` 또는 «전용 모듈»)는 `design-evidence.md` 에만 있다.
- n2. 스니펫 머리 주석의 예시 `pageSize: 4000` 과 실제 기본값 `100000` 이 다르다(`assets/style_census.js:4,10` — v4 원본부터 있던 것).
- n3. `make verify-web` 은 JS 스니펫을 실행하지 않는다(브라우저 합성 `style_census_browser.py` 는 수동). 이번에는 내가 직접 돌려 통과를 확인했다(§3).

### 확인했지만 문제 없음

- **범위 정합**: 검토 §3 «무엇» 1~4 와 맞다. 대조기는 v4 대비 `ord` 버킷·정렬·입력 검증·CLI 만 바뀌었다(`diff -u frozen-v4-src/compare_census_v4.py …` 136줄). 차단·입력 결속·재렌더·exit 2/3·영향 case·freshness·재관찰 축소·발주자 축소는 없다. 기존 검사기·백스톱은 바뀌지 않았다(변경은 새 파일 + md 뿐). 후보가 있어도 exit 0 이다 — 시험 `test_candidates_are_reported_without_blocking_exit`, 그리고 실제 v4 census(`p1-plant-base7` 대 `plantA`)로 CLI 를 돌린 결과 `후보 119 · exit=0`.
- **D 회귀 방지**: «시안 예시 값으로 고치지 않는다 + 인과 근거»가 Coordinator 3-2(`dddjango-web.md:235`), `design-evidence.md` §W8 처분 표, coder(`coder-web.md:16`), 감사 반환(`discipline-reviewer-web.md:63`)에 다 있다. 비교용 데이터 자리는 v4.1 §2-4 문면 그대로다(하네스·전용 모듈뿐 · 기존 fixture·factory·시드 무변경). Coordinator 3-1 에도 «기존 시험 fixture는 유지»가 있다.
- **역할 경계**: 실행·전달 = Coordinator, 해석 = architect(«값·행 id 결속 블록이나 새 G1 검사를 만들지 않는다»), 수리 = coder, 처분 = 기존 `discipline-reviewer-web` 시각 감사(별도 회차·파일 없음).
- **Coordinator 크기**: Claude +2,115B(204,526 → 206,641) · Codex +2,088B. 짧은 접속 문면 9곳이고 계약은 reference 에 있다.
- **SDK 없음·시안 없음**: 추가 문면은 전부 «(있으면)»·«원본 census가 있으면» 조건부다. G2 배너만 «W8 보고: 미수행 — 사유» 한 줄이 늘어난다. backstop 의 빌드 탐지는 표식 파일 기준이라 새 `observations/` 와 충돌하지 않는다(`backstop.py:74-104`).

## 3. 미러 · 검증 · 재현

### 미러
- byte: 새 파일 6개(`assets/style_census.js` · `scripts/compare_style_census.py` · `scripts/style_value_sheet.py` · `scripts/test/{fixtures_style_census.sh, test_style_census.py, style_census_browser.py}`)와 `implementation-ui/references/design-evidence.md` 를 Codex 쪽과 `cmp` 해 전부 동일. `diff -rq` scripts·assets 디렉터리 동일. `Makefile` verify-web 은 scripts·assets 를 디렉터리째 `diff -rq` 하고 `design-evidence.md` 를 `cmp` 하므로 Makefile 수정이 없어도 새 파일이 다 대조된다.
- 의미: Coordinator 추가 9곳을 `${CLAUDE_PLUGIN_ROOT}`→`${SKILL_DIR}` 로 바꾼 뒤 Codex 추가분과 비교해 9/9 동일, 삭제 0. 세 역할의 추가 문장은 Claude·Codex 문자 그대로 같다. architect 1·4번 호출과 coder 호출 입력의 같은 자리에 들어갔다.

### 검증(사본 `review-w8-small/repo`, `PYTHONDONTWRITEBYTECODE=1`)
| 명령 | 결과 |
|---|---|
| `make verify-web` | **exit 0** · 픽스처 20파일 실패 0 · `fixtures_style_census.sh` 19 tests OK · refactor_audit self-test red 0 · scripts/assets/references/REQUEST_GUIDE 미러 통과(`verify-web.log`) |
| `make verify` | **exit 0** · 5/5 green(249초 · `/tmp/djr-verify.25A0os`) — 봉인 드리프트도 red 아님 |
| `claude plugin validate dddjango-web --strict` | **exit 0** · Validation passed |
| `style_census_browser.py --chromium <로컬 headless>` (scratch venv p2) | **exit 0** · «v4 SDK six scenarios + root zero/multiple PASS (network intercepted)» |
| `W8_TEST_SOURCE=<frozen v4> python3 -m unittest …test_group_and_samples_are_hash_seed_independent` | **FAILED** — v4 의 비결정성이 시험에서 재현됨(제품판은 통과) |

### 결정성·판정 재현(내 스크립트 `review-w8-small/my_replay.py` · 출력 `replay-out/` · 로그 `replay.log`)
- 보관 P1/P2 6회차를 **제품 대조기와 동결 v4 대조기를 같은 프로세스에서 각각** 돌렸다(보관 schema 3 이라 API 재생 설정 `DECLARED={'ALL'}`·`ALLOW_LEGACY=True`·`SDK_SCOPE=None` — 구현자와 같은 조건). `PYTHONHASHSEED` 는 0·1·2·3.
- 6회차 × 4시드 모두 `examples` 를 뺀 묶음(id·값·구성원·차단 후보 구성원)이 **v4 실시간 실행과 같고 저장 JSON 과도 같다**. 묶음/후보/후보 구성원은 P1 122/84/346 · 91/49/216 · 60/31/114, P2 104/56/110 · 67/28/46 · 63/24/42 이다.
- **P1 G2#1 독립 라벨 T 35/35 가 모두 후보**다.
- 제품 출력은 4시드에서 **파일 byte 가 같다**. SHA-256 앞 16자리 `f400faf33805e3d6`·`2264fc165a21b30e`·`395fbf2a8ebebf82`·`951e5621cb5d1f2d`·`f979ce89c0b4d98f`·`868aec09ed4e5159` 는 구현자 `replay-seed-*.log` 와 일치한다. v4 는 같은 입력에서 묶음 순서 해시가 시드마다 달라졌다(P2 r2: `430877c6…`/`050a4e5f…`/`a46a7ea7…`/`42c14a8d…`).
- 제품 CLI(엄격 v4 경로)를 실제 v4 census 짝으로 돌리면 시드 0·5 에서 보고가 byte 동일하고 exit 0 이다.

### 실행 흔적 고지
- 쓰기는 이 scratch 폴더 아래에만 했다(`repo/`·`replay-out/`·`sheet/`·`cli/`·로그·스크립트). 예외는 `make verify` 가 스스로 만드는 `/tmp/djr-verify.25A0os` 다.
- 한 번 상대 경로 실수로 `/Users/hyun/Desktop/cmp-diff.txt`(대조기 diff 출력)를 만들었다가 곧바로 지웠다. 저장소·워크트리 안에는 쓰지 않았다.

REPORT-DONE
