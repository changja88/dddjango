# 2.1.0 짓기 기록 — dddjango-web 2.1.0 (빚 정리 · 외부 JS 승인 절차 · 리팩토링 입구)

- 시작 12:58:50 (`date` · 10-06 KST) · 운영자 지시(1차 2.0.0 배포 12:56 · R main `168b014e` · 사용자 «아니야 2차는 1차하고해»)
- 바탕: R main `168b014e` 를 `git archive` 로 `<S>/web-new2/` 에 풂 — Claude 판 56 파일 908,724 B · Codex 판 54 파일 867,649 B · web-new 얼린 판과 같음(매니페스트만 2.0.0)
- 옮길 원본: v1.3.1(`<S>/web-new/head/` = `0cdb10f5`)
- 결정 · 소유: `web-new2/plan-2.1.0.md`
- 2.0.0 의 기록은 `web-new/build-log.md`(R 에는 `workspace/plan/2026-10-06-web-dddart/build-log.md`)

## 일꾼 배치(13:00 기동)
| | 일 | 일꾼 |
|---|---|---|
| X1 | 빚 정리 | ④ |
| X2 | 외부 JS 승인 절차 | ③ |
| X3 | 리팩토링 입구 | ① |
| C | Codex 판 | ⑤(X1~X3 뒤) |
| R | 깨끗한 사본 `<S>/web-rel2` · 문서 · 검증 · 커밋 | ⑥(13:0x 준비 · 얼림 뒤 넣기) |

## 진행
- 13:0x 결정(plan-2.1.0.md «결정 덧»): 검사 84종(72 − PJ3 + WV13) · 단위 목록(v1.3.1 1:1 — BC · root · common · design_system · static 칸 · web/*.py · 옛 배치 최상위 폴더) · debt.py 9 이름 · debt JSON 스키마 v1.3.1 그대로 · 개명 · 이동 묶음.
- 13:05:41 ⑥ 준비 끝: `<S>/web-rel2` HEAD `168b014e` · 2.0.0 기준선 make verify green 5/5 250초 · verify-web green 10초 · 저장소 쪽 초안(makefile · readme · agents-md · development-md diff · release-notes-2.1.0 뼈대). 짚은 것: core `refactor_audit.py:161~195` «상시 답 인식 블록» 은 core · web byte 동일(verify-web 대조) → X3 에 전함 · Codex defaultPrompt 는 `$dddjango-web-refactor` 만으로는 이름을 부른 것으로 안 셈(하이픈 경계) → ⑤ 에 전할 것 · 스펙 이름 `plan-2.1.0.md` · `build-log-2.1.0.md`(2.0.0 build-log 와 겹치지 않게).
- 13:29:16 X3(①) 끝: `commands/refactor.md` 705 B · `scripts/refactor_audit.py` 125,458 B(2,312줄) · `scripts/test/fixtures_refactor_audit.sh` 72,845 B → PASS=213 FAIL=0 · 상시 답 인식 블록 core `168b014e` 와 byte 같음 · 표지 `리팩토링 모드(입구 /dddjango-web:refactor) · 대상: ` · validate 통과 · 검사 ID 변화 없음.
  - Coordinator: 맨 뒤 새 절 «리팩토링 모드»(R0 · R0′ · R1 · R2 · R2′/R3 · 적용 범위 · G0 · Phase 1~2 · 상시 답 · G2) · 모드 사분류 · `mode: refactor` · `g2_approved` · `요청 원문: $ARGUMENTS` 줄. 에이전트 7 은 맨 뒤 «리팩토링 모드» 절.
  - UNIT_AUDIT = 리뷰어 다섯(ddd · ui · state · data + discipline) 모두 — dddart G1 «4축 전부 병렬» 원칙(렌즈 필요 여부는 기계로 못 가림 · 빼면 사각). 슬라이스 0 의 G1 리뷰는 수정 모드 G1′ 처럼 닿는 층 렌즈 + ddd 항상.
  - **2.0.0 과 달라진 곳 — Coordinator frontmatter 의 `disable-model-invocation: true` 지움**: 이 줄이 있으면 `refactor.md` 가 Skill 도구로 Coordinator 에 넘기는 길이 막힌다(v1.3.1 web · core dddjango 도 이 줄 없음). 대가: 모델이 자연어 요청에 Coordinator 를 스스로 부를 수 있다(v1.3.1 과 같은 상태). dddart 에는 리팩토링 입구가 없어 이 줄을 둘 수 있었다.
  - 단위 vendor 는 단위 아님(X2 절차 몫) · 개명 · 이동 묶음 · 편집 줄 키(IM · PU) · debt 이름 10(9 + `is_test_path`) X1 과 합의.
- 13:29:54 X7(⑤) 끝: Claude 판 Coordinator 에 «Claude Design 에서 내려받은 시안 폴더» 갈래 — 디자인 출처 문단 12곳(16 · 38 · 127 · 129 · 131 · 132 · 137 · 138 · 139 · 147 · 148 · 258줄) · Bash `ls` · `cp` · config `source:"local",path` · 같은 동결 · 추출 · 화면 확인 게이트. Codex 판 전용 문장(세션 도구 목록 · 이미지 판독 보조 · 렌더 경로 제시)은 넣지 않음. 묶인 픽스처 · 검사 없음. Codex 판 경계 규율(step 10)에 «내려받은 시안 폴더의 같은 파일 포함» 은 Codex 옮길 때.
- 13:32:35 X1(④) 끝: `backstop.py` 12,248 B(러너 모드 `--debt-scan [--refactor]` · `--debt-residual` · `--subst-check` · `--design-build` 되살림 · 모드 배타) · `src/common.py`(`CORE_FAMILIES` · `CORE_CHECK_IDS` 71 · `from_files`) · `src/debt.py` 29,871 B · `src/subst.py` 43,187 B · `fixtures_debt.sh` PASS=91 · `fixtures_subst.sh` PASS=133 · run_fixtures PASS 113 · 검사 **84종**(ST13 · IM27 · NM19 · CY1 · TG1 · MD2 · PJ2 · PU6 · WV13). 빚 스캔 패밀리 ST · MD · IM · NM · PU · WV(CY · TG · PJ 빼 — 래칫 · 테스트 추가 · 늘 검사). 같이 쓰는 md: Coordinator step 4′ · G0 빚 1행 · Phase 1 슬라이스 0 · 스캔 단위 확인 · Phase 2 기존 테스트 기준선(`test_command` + 호스트 기존 테스트) · 슬라이스 0 끝 green ①~⑤ · `--debt-residual` · G2 빚 1행 · 수정 · 트리비얼 ⓪ · 엣지 · 경계 / coder-web · design-architect-web(`## 슬라이스 0`) · discipline-reviewer-web(9 슬라이스 0 대조) / houserules SKILL · §7 · §8.

### X1 — 옛 배치 이동 크기(spring_dream_server · 읽기만 · `git archive` 사본에서 빚 스캔)
- 추적 web 파일 414 중 **표준 트리 밖 옛 배치 317(76.6%)** · 최상위 폴더 10(client 80 · consultation 62 · auth 36 · related_persons 34 · chart 29 · preferences 26 · intake 19 · employee_choice 17 · home 13 · base 1) · 표준 컨테이너 안 97(static 54 · design_system 40 · 직속 3). 화면 개념 12 · 페이지 템플릿 11(전부 `base/base.html` extends).
- 전체 빚 스캔: 키 426 · 발견 628(ST0 317 · NM13 34 · IM27 26 · NM3 25 · ST12 10 · PU2 8 · ST10 2 · PU7 2 · PU8 1 · WV8 1).
- **W4 일감(chart AppBar)에 «손대는 파일 + 부르는 곳»**: 규칙 그대로면 옮김 2 파일(`chart_app_bar.html` + 부르는 `chart_screen.html`) · 키 3. 그러나 새 트리 게이트가 연쇄를 부른다 [추정] — 옮긴 section 은 같은 BC 의 view 가 있어야 하고(NM5) · 옮긴 페이지는 root_view.html 만 extends(IM26) → base.html → root_view.html 와 나머지 페이지 10 의 extends 줄 치환 · 테스트 치환 3 · 새 골격 chart BC 약 25 · root 약 10. **합계 [추정]: 옮김 5 · 참조 줄 편집 약 12 · 테스트 치환 3 · 골격 생성 약 35 파일.** 번진 몫은 G1 «스캔 단위 확인» 재승인 질문으로 올라온다. dddart 에는 없는 동작(옛 배치 파일마다 ST0 키 — 10-05 «손대는 파일 + 부르는 곳» 이 파일 단위로 고르고 G2 잔존도 옮긴 만큼만 줄어야 해서).
- 알려진 한계: 슬라이스 0 은 web_test 파일을 옮기지 않고 치환만(`--subst-check` 가 테스트 파일 개명을 치환으로 보지 않음) → SUT 를 옮기면 web_test 미러가 어긋난 채 남는다.
- 13:35:19 X2(③) 끝: `scripts/sdk_vendor.py` 45,920 B · `src/sdk_registry.py` 50,071 B(등재 상수를 common 에서 이 모듈로 · `sdk_state(ctx)`) · `src/check_vendor.py` 54,248 B(`VENDOR_CHECK_IDS` WV1~WV13 · `UNDEFERRABLE` · `VendorUndecidable` · `run_vendor`) · `assets/sdk_boundary.js` 8,346 B(v1.3.1 byte 같음) · `test/sdk_fixture.py` · `test/boundary_probe.cjs` · `test/fixtures_sdk.sh` PASS 239(v1.3.1 K · F 전부 + 빚 모드 WV D30~D38) · ST12 벤더 분기 · PJ3 비움 · PU1 · PU2 넓힘(미등재 벤더 JS · 등재 사본만 로드 · root_view.html 자리) · run_fixtures F1 의 vendor 줄 맞춤(lead 허락).
  - 같이 쓰는 md: Coordinator(SDK 후보 · `sdk_commits` · G0 미커밋 vendor 거절 · G1 SDK 행 · 별도 1문항 · SDK 채택 확인 · Phase 2 SDK 격리 커밋 · 슬라이스 계수 밖 · 공식 SDK 경계 확인 · G2 SDK 행 · 수정 · 트리비얼 · 엣지 둘 · 경계) · 에이전트(architect SDK 표 · **design-review-data-web 에 공식 SDK 점검**(v1.3.1 design-review-web 12 자리 — 운영자 API 와 오가는 바깥 데이터 교환이라 data 렌즈) · discipline-reviewer-web 10 · coder-web) · 스킬(houserules 트리 · §9 신설 · implementation-javascript §8 «공식 SDK 소비» · implementation-django §11 «공식 SDK 사본 — static/vendor» · implementation-htmx PU1 · PU2 행).
  - **2.0.0 과 달라진 곳**: 2.0.0 의 «coder 가 외부 JS 를 `vendor/<라이브러리>/<버전>/` 에 고정해 들임» 길이 등재 절차로 바뀜 → **2.0.0 으로 지은 프로젝트에 남은 그 꼴 사본은 WV12 빚이 된다**(덫 낱말에 걸리면 등록 불가 · ⓐ 재상정 — 배포 노트에 적을 것) · 공개 키 흐름 = settings → `common/` 설정 읽기 → VM → state → data 속성(IM12) · PU8 과 WV8 이 기능 JS 의 eval 류 한 줄에 함께 난다(둘 다 둠 — 2.0.0 검사와 v1.3.1 번호).
  - 13:36:22 lead: Coordinator 리팩토링 절의 «외부 JS 고정 사본 `web/static/vendor` 는 단위가 아니다» → «공식 SDK 사본 `web/static/vendor` · `web/sdk_registry.json` 은 단위가 아니다 — 등재 · 복원 · 제거는 공식 SDK 승인 절차가 맡는다»(2.0.0 낱말이 남아 있던 곳) · `run_fixtures.sh` 끝에 fixtures_debt · fixtures_subst · fixtures_sdk · fixtures_refactor_audit 이어 부르기.
- 13:4x X6 빠짐(사용자 결정 — plan «변경» 절): ⑦ 13:40:45 멈춤 · 초안 `web-new2/later/X6-draft/REQUEST_GUIDE.md`(394줄 · 34,792 B)로 옮김 · Codex 사본 지움 · 두 매니페스트 homepage · websiteURL 을 2.0.0 값으로 되돌림(168b014e 와 byte 같음 · 13:41:04).

## Claude 판 검증(13:36:29 ~ 13:42:44 · lead)
- `claude plugin validate dddjango-web --strict` → `✔ Validation passed`
- py_compile 26 파일 ok
- `run_fixtures.sh` → exit 0(5분 50초): `결과: PASS 113 / FAIL 0` · `fixtures_extract: PASS 31 · FAIL 0` · `PASS=13 FAIL=0` · `fixtures_debt: PASS=91 FAIL=0` · `fixtures_subst: PASS=133 FAIL=0` · `fixtures_sdk: PASS=239 FAIL=0` · `fixtures_refactor_audit: PASS=213 FAIL=0`
- `backstop.py --help` → 사용 오류 exit 1 · `--only typo` → 사용 오류(패밀리 st,md,im,nm,cy,tg,pj,pu,wv)
- frontmatter 21(커맨드 2 · 에이전트 7 · 스킬 12) 파싱 · bad 0 · 교차 참조 깨진 것 0 · python 예시 블록 124 문법 오류 0
- 13:42:44 discipline-reviewer-web 의 «검사 72종» → «검사 84종 … 공식 SDK» (남은 72종 표기 0)
- 크기: Claude 판 70 파일 1,705,888 B(2.0.0 56 파일 908,724 B · v1.3.1 84 파일 2,027,085 B)

## Codex 판(⑤ · 13:54:21 끝 · lead 13:55:06 확인)
- Coordinator `skills/dddjango-web/SKILL.md` 151,978 B(새로 복사 · 규칙 재적용 · 표지 `리팩토링 모드(입구 $dddjango-web-refactor) · 대상: ` · 빚 질문 등 선택지 = 평문 번호 목록 · R2 파견 = spawn_agent · SDK 경계 확인 = 가용 브라우저 채널 · X7 경계 규율 포함) · 역할 7 다시 옮김 · 새 `skills/dddjango-web-refactor/SKILL.md` + `agents/openai.yaml`(`allow_implicit_invocation: false`) · 지식 12(SKILL.md 접두 · references byte) · scripts 24(test/ 제외) · `assets/sdk_boundary.js` · plugin.json defaultPrompt 넷째 «dddjango-web으로 … $dddjango-web-refactor web/application/order»(하이픈 경계라 이름을 따로 부름) · README(리팩토링 입구 · assets · `${SKILL_DIR}` · 가이드 줄 없음).
- 검증: SKILL.md 21 frontmatter 파싱(bad 0) · references 13 · scripts 24 · assets 가 Claude 판과 byte 같음 · defaultPrompt 4 개 모두 이름 부름 · Codex 자리 refactor_audit self-test red 0 · 리팩토링 입구 표지 OK · 매니페스트 homepage · websiteURL = 저장소 루트(2.0.0 값) · REQUEST_GUIDE 없음.
- codex-dddart 와 달라진 곳 덧: 경로 표기 `${SKILL_DIR}`(v1.3.1 Codex · Makefile 문단 대조 sed 와 맞춤) · «Bash로 실행» → «네이티브 셸로 실행» 단순 치환 · 문단 앵커 7 의 낱말은 Claude 판 그대로 · 새 스킬 `dddjango-web-refactor` · `assets/` · scripts 6 더 실음.
- ⑥ 에 넘길 것: Makefile 문단 대조 — `**SDK 채택 확인(G1 배너 직전` 문단은 sed 에 `-e 's/dddjango-web:/dddjango-web-/g'` 를 더해야 양판이 같고 · `6. **G2 배너**` 앵커는 Claude 판에 없어 뺀다.
- 크기: Claude 판 70 파일 1,705,900 B · Codex 판 63 파일 1,379,248 B · `__pycache__` 0.
- 13:5x 운영자: 기준 커밋(2.0.1)은 가이드 초안 → 사용자 확인 → 배포 뒤라 시각 미정 · 운영자가 web-new2 대상 Codex 검토 r1 을 돌리는 중(13:56~ · `web-new2/review/review-web21-codex-r1.md`) → 검토 끝까지 web-new2 플러그인 트리 고치지 않음.
- 13:59:08 ⑥: 저장소 쪽 diff 넷을 13:55 판에 맞춰 확정(84종 · 문단 앵커 8 · sed 에 `dddjango-web:`→`dddjango-web-` · README 리팩토링 예시 · 가이드 관련 줄 0) · scratch 두 판에 verify-web 새 줄 미리 돌려 전부 통과(상시 답 블록 == core · 표지 · 미러 · self-test) · release-notes-2.1.0.md 4,347 B. 기준 커밋을 받으면: 사본을 그 커밋으로 · 기준선 · diff 다시 얹기 · 매니페스트는 기준 커밋 판 위에 2.1.0 이 바꾼 필드만(Codex defaultPrompt 넷째 · longDescription — version 은 기준 값 그대로 · DRY minor).
- 검토 고침 묶음에 넣을 것(lead): Claude `plugin.json` description 에 리팩토링 입구 한 마디(Codex longDescription 과 맞춤 · v1.3.1 처럼).

## 검토 r1 고침(14:13 ~ · 운영자 Codex 검토 반려 — blocker 4 · important 6 · minor 1)
- 검토 `web-new2/review/review-web21-codex-r1.md` · 계획 `web-new2/review/fix-plan-r1.md`(14:1x). 11건 모두 고침 · 다시 검토하지 않음 · blocker 는 재현 픽스처 red → green.
- 일꾼: X1 ④ #1 · #2 · #10 / X2 ③ #3 · #4 · #6 · #7 · #8 · #9 · #11 / X3 ① #5 / 뒤에 ⑤ Codex 판.
- Coordinator 의 «서버 계약 출처 해소» 절 · `$api_url` 줄은 손대지 않음(2.0.1 이 바꿈 — 얹을 때 합침).
- 14:19:37 #5(①) 끝: `refactor_audit.py:1876` · `:1896-1901` · `:1922-1929`(확정 지문 = 원 발견 경로 + 개명 대응 ∪ 채택한 해소 근거 `grounds`) · 픽스처 K′(`fixtures_refactor_audit.sh:709-741`) 고치기 전 `FAIL K′1b` · `FAIL K′3`(PASS=215 FAIL=2) → 고친 뒤 PASS=217 FAIL=0 · self-test red 0 · 상시 답 블록 core 와 byte 같음. **1.3.1 에도 있던 결함(web `:1854` · `:1892`) · core dddjango 에도 같은 꼴(`168b014e:dddjango/scripts/refactor_audit.py:1980` · `:2018` · `:1900`) — core 는 고치지 않음 · 운영자에 알림(14:19).**
- 14:39:03 #1 · #2 · #10(④) 끝 — fixtures_debt PASS=97 · fixtures_subst PASS=136 · run_fixtures 백스톱 113 · sdk 258 · refactor_audit 217 · extract 31 · contract 13.
  - #1: `debt.py` 가 `web/` 부재를 git 앞에서 봄(첫 실행 = 빚 0 · 비git 이어도) · `_is_git` · 비git 첫 실행의 잔존 판정은 다시 스캔 없이 exit 0 · `web/` 있는 비git 은 그대로 exit 1. Coordinator :119(git init 거부의 대가가 `web/` 유무로 갈림) · :151 · :204. 픽스처 D33a(고치기 전 `빚 스캔 실행 불능 — git ls-files 실패`) · D33b(고치기 전 `빚 잔존 판정 불가`) red → green · D33c 대조. **1.3.1 에 없던 결함** — 1.3.1 은 비git 을 모두 막아 일관됐고, 2.0.0 의 «전체 검사로 퇴화» 문장과 합치며 생긴 어긋남.
  - #2: `subst.py` `_mirror` · `_dir_shifts` · `_test_moves` — 슬라이스 0 커밋만 닿은 `web_test/` 파일이 SUT 이동과 같은 경로 대응으로 옮겨지면 한 걸음으로 비교(단언 바뀜 · 엉뚱한 자리 · 새 테스트는 그대로 red). 문면 «테스트는 옮기되 단언은 그대로»(architect `테스트 이동: <옛> → <새>` 줄 · coder `git mv` · discipline 9 · Coordinator 끝 green ④ · houserules TG1 문장). 픽스처 S20a red → green · S20b · S20c 대조. **덧(lead 받음)**: `check_tests.py` — 새 BC 의 행위 파일이 모두 기준점에서 옮겨 온 것이면 TG1 은 새 테스트를 요구하지 않고 알림만(옛 배치는 web_test 가 없고 슬라이스 0 은 테스트를 더할 수 없어 막히던 길 — 사용자 원칙 «리팩토링은 기존 테스트 충분 가정»). 픽스처 D34a · D34c red → green · D34b(새 파일이 더해진 BC) 대조 red 유지. **1.3.1 에 없던 결함**(web_test 미러는 2.0.0 부터). 남은 한계: SUT 의 새 경로 짝은 1.3.1 처럼 git 개명 감지에 기댐.
  - #10: Coordinator :228 — 이번 G0 에 빚 ⓐ 가 있으면 G1′ 생략 안 함(승인 명세의 `## 슬라이스 0` 을 이번 ⓐ 목록으로 제자리 다시 쓰고 G1′) · ⓐ 가 없으면 남은 절로 슬라이스 0 을 돌리지 않음 · architect :47. **1.3.1 에 있던 규칙을 옮기며 빠뜨린 것**(1.3.1 수정 모드 3).
- 14:42:19 #3 · #4 · #6 · #7 · #8 · #9 · #11(③) 끝 — fixtures_sdk 고치기 전 249/9 → PASS 258 / FAIL 0 · run_fixtures 전수 green.
  - #3 `sdk_vendor.py:368` — `web/` 조건을 실제 설치에만 · Coordinator :180 ①. 픽스처 R3a(고치기 전 `install --dry-run … [web/ 없음]=1`) red → green · R3b 대조(실제 설치는 `web/` 필요). **1.3.1 에도 있던 결함**(`sdk_vendor.py:342-343`).
  - #4 **계획과 다른 길(lead 받음)**: 도구가 템플릿 로드 줄까지 고치면 WV10(격리 커밋이 목록 · 벤더 밖을 바꿈 / 슬라이스 커밋이 목록 · 벤더를 바꿈)에 걸리고 템플릿 편집은 coder 몫 → 이관 세 걸음 ① 옛 폴더와 **다른 id** 로 등록(격리 커밋 — 옛 사본은 미등재 단위라 WV12 빚일 뿐) ② coder 슬라이스 0 이 로드 줄을 등재 파일로 치환 ③ 참조 0 인 옛 단위를 `sdk_vendor.py remove`(격리 커밋 · #7 로 가능) — 걸음마다 늘 검사 통과를 픽스처로 확인 · 같은 id 등록은 G1 dry-run 에서 «다른 id» 안내로 거절. `sdk_vendor.py:351` `_existing_place` · Coordinator :184 · houserules §9 :373. 픽스처 R4a~R4g. **1.3.1 에는 부분**(판 폴더 꼴은 2.0.0 부터 · 같은 id 다른 자리 등록의 되돌림 구조는 잠재).
  - #6 `sdk_registry.py:251 · 254 · 268`(배포 · 문서 자원 경로 밖을 부르면 서비스 호출로 셈) · `sdk_vendor.py:563` · `check_vendor.py:827`. R6a red → green · R6b 대조. **1.3.1 에도 있던 결함.**
  - #7 `sdk_vendor.py:762 · 775 · 796`(미등재 단위의 참조 0 제거 · 목록 그대로) · WV13 안내 `check_vendor.py:900` · houserules :372 · Coordinator :250. R4d~R4g. **1.3.1 에도 있던 결함.**
  - #8 `assets/sdk_boundary.js:119`(이미 있는 승인 이름공간을 바로 가로챔 · `isInitialized` 의존 없음) · `boundary_probe.cjs` noinit. R8 red(`{"path":["init-wrapped"],…,"realCalls":1}`) → green. core dddjango 에는 같은 파일 없음(R 전체 find 0). **1.3.1 에도 있던 결함.**
  - #9 Coordinator :207 ③ — 명세 SDK 사용 표 «검증 행위» 칸에 적힌 전송 방식(팝업 · 폼 제출 · Fetch/XHR)만 각 ≥1 · 비면 «미검증» · architect :54 · design-review-data-web :43. **1.3.1 에도 있던 결함.**
  - #11 `sdk_registry.py:499` «WN8 꼴» → «houserules §4 파일명 snake_case». 1.3.1 에서는 WN8 이 실제 검사 ID 였음(옮기며 남은 흔적).
  - 남긴 것: 등재 id 디렉터리 안의 비등재 파일만 지우는 전용 도구 동작은 없음(1.3.1 과 같음 · 이번 지적 밖).
- 14:4x lead: Claude `plugin.json` description 에 «/dddjango-web:refactor로 대상 단위 하나의 기존 web 코드를 동작 그대로 표준 정리한다» (Codex longDescription 과 맞춤 · v1.3.1 처럼) · ⑤ 에 Codex 판 옮김 지시.
- 14:46:42 ⑤ Codex 판 반영 끝: Coordinator 바뀐 9줄 · 역할 4 · references 13 · scripts 24 · assets byte · self-test(Codex 자리) red 0 · 표지 · 앵커 8 OK · Codex 판 63 파일 1,399,039 B.

### 검토 r1 고침 검증(14:43:08 ~ 14:49:35 · lead)
- `claude plugin validate dddjango-web --strict` → `✔ Validation passed` · py_compile 26 ok
- `run_fixtures.sh` → exit 0: `결과: PASS 113 / FAIL 0` · `fixtures_extract: PASS 31 · FAIL 0` · `PASS=13 FAIL=0` · `fixtures_debt: PASS=97 FAIL=0` · `fixtures_subst: PASS=136 FAIL=0` · `fixtures_sdk: PASS=258 FAIL=0` · `fixtures_refactor_audit: PASS=217 FAIL=0`(앞 판 대비 debt +6 · subst +3 · sdk +19 · refactor_audit +4)
- frontmatter Claude 21 · Codex 21 bad 0 · 교차 참조 · 예시 124 오류 0 · references 13 · scripts 24 · assets 가 두 판 byte 같음 · `__pycache__` 0
- 크기: Claude 판 70 파일 1,741,018 B · Codex 판 63 파일 1,399,039 B
- 고친 수 11/11 · 새 재현 픽스처: blocker 4(#1 D33a·b · #2 S20a + D34a·c · #3 R3a · #4 R4a~g) + #5 K′ · #6 R6a · #8 R8 (대조 짝 D33c · S20b·c · D34b · R3b · R6b 포함)

## 2.0.1 위로 얹기(14:5x ~)
- 운영자: web 2.0.1 배포 끝(14:51:01 · 태그 dddjango-web--v2.0.1) · **기준 커밋 R main `6cfb83e4`**. 2.0.1 이 바꾼 것 15 파일(가이드 양판 · Coordinator/Codex SKILL «서버 계약 출처 해소» 절 · `$api_url` 줄 · argument-hint · architecture-data references 한 줄 · openai.yaml defaultPrompt · 매니페스트 homepage/websiteURL · 버전 2.0.1 · README · codex README · AGENTS.md · DEVELOPMENT.md · request_guide_contract.py · build-log.md 한 줄).
- ⑥: `<S>/web-rel2` 를 6cfb83e4 로 · 2.1.0 을 얹되 겹치는 곳은 2.0.1 내용을 지키며 합침(가이드 rsync 삭제 금지 · Coordinator 의 2.0.1 절 그대로 옮김 · 매니페스트는 2.0.1 바탕 + 2.1.0 필드) · verify · 커밋 A · B · DRY minor.
- ⑦: 2.0.1 가이드 위에 2.1.0 셋(G0 빚 질문 · 리팩토링 입구 요청 꼴 · G1 외부 JS 승인 질문) · «2.1.0 기준» · 3절 ③ Claude Code 도 내려받은 폴더 → `web-new2/guide-2.1.0/REQUEST_GUIDE.md` → ⑥ 이 양판에 넣음.
- 14:54:16 ⑦ 가이드 2.1.0: `web-new2/guide-2.1.0/REQUEST_GUIDE.md` 241줄 · 19,769 B(2.0.1 가이드 201줄 · 15,431 B + 40줄 · 2.0.1 문장은 5줄 «2.1.0 기준» 하나만 바뀜). 더한 것: 6절 «기존 코드 정리(G0)»(빚 한 줄 · 먼저 정리(권장) · 이유를 적고 미룸 · 리팩토링 입구로 따로 · 화면 동작을 바꾸지 않는 첫 조각 · 기존 테스트 앞뒤) · G2 줄 · 작은 수정 줄 · 4절 «정리를 미루거나 건너뛰라고 적지 않음» · 7절 끝 «기존 코드만 정리하기 — 리팩토링 입구»(`/dddjango-web:refactor web/application/order …` · Codex `$dddjango-web-refactor` · 단위 예) · 6절 «외부 JavaScript 승인(G1)» · 3절 선택 줄 · 2절 ③ «Claude Code 도 내려받은 시안 폴더»(2.0.1 의 디자인 출처는 2절 ③ 이라 그 자리) · 8절 두 줄(정리 미룸 · 외부 도구 승인은 사용자 원문 · 리팩토링 모드 표지 줄). 가이드 검사 authority · link PASS · 내부 id 0.
- 15:17:38 ⑥ 끝(사본 `<S>/web-rel2` · 기준 `6cfb83e4` · push 막힘): 커밋 A `28710820f46a5f361341f8e48fce3c085738abc9`(feat(web): dddjango-web 2.1.0 — 빚 정리 · 외부 JS 승인 절차 · 리팩토링 입구를 새 구조로 · 77 파일) · B `08663efa`(chore: manifest 봉인 재발행 · sealed_commit = A) · 6cfb83e4 → HEAD 78 파일 +19,616 −366. 기준선 verify 5/5 250초 · verify-web 11초. 마지막(B 뒤 15:08:21 → 15:17:31): verify green 5/5 233초 · verify-web green 316초(백스톱 113 · extract 31 · contract 13 · debt 97 · subst 136 · sdk 258 · refactor_audit 217 · self-test 두 자리 red 0 · 표지 · 문단 8 · 미러 같음) · validate --strict ✔ · request_guide_contract self-test 157/157 · `make release-web DRY=1` v2.0.1 → v2.1.0. 가이드 양판 sha256 `8d4ecd282d4fcc177b9368aa658ec097a03d78b59edba21b8649ea0067c0aa16`. 겹친 곳: Coordinator · Codex SKILL · Codex README 를 2.0.0 · 2.0.1 · 2.1.0 3-way 합침(충돌 줄 셋은 2.1.0 삽입만이라 2.0.1 줄 뒤에 넣음 · 2.0.1 «서버 계약 출처 해소» · `$api_url` · argument-hint 그대로) · architecture-data references 2.0.1 판 · openai.yaml 2.0.1 값 · 매니페스트 2.0.1 바탕 + 2.1.0 필드 · README · AGENTS · DEVELOPMENT 3-way(2.0.1 가이드 표 · 링크 그대로). R main 은 15:18 에도 `6cfb83e4` — A · B 는 fast-forward 로 얹힘.

## X4 시험 중 병렬 일(15:52 ~ · web-rel2 · web-new2 코드는 잠금)
- 15:56:06 ⑥ 일 1: `release-prep/release-notes-2.1.0.md` 빈칸 채움(«2.0.0 이후 바뀌지 않은 것» 표 · «호스트에 새로 생기는 것» · X7 항목 · `<채움 — X4 결과>` 남김 · 외부 JS 설명을 houserules 그대로 «플랫폼 운영자의 공식 SDK 만» 으로 바로잡음).
- 16:18:02 ⑧ 일 2: `S/web-diagrams/` 에 그림 초안 — `work_flow_web.html`(archify architecture 형 · 노드 14 · validate 9/9) · `.spec.json` · `.delivery.json` · `work_flow_web_guide.html` · `file_tree_web.html`(생성기 `_gen/build_tree.py`). 브라우저 렌더 확인은 X4 뒤.
- 16:32:52 ④ **F-X4-1 고침**(사본 `S/web-fix1` — web-rel2 `08663efa` 에서 clone · 커밋 `556c188c13a4329da16bd6825bd0d4cb752e9fb2` · push 없음): 빚 모드에서 폴더 발견(ST3 · ST5~ST8 · ST10~ST12)을 파일 키로 펼침(`ST12|static/css` → `ST12|static/css/<파일>` — ST0 옛 배치 펼침을 넓힘 · ST4 골격과 `static/vendor/` 단위는 폴더 키 그대로) · 잔존 판정은 범위가 소유한 파일 기준 · 같은 폴더의 남은 파일은 «범위 밖 남은 빚» 으로 보고만(exit 영향 없음) · G0 표시도 같은 기준 · debt JSON 에 선택 필드 `folder`(스키마 그대로 · refactor_audit 영향 없음). 픽스처 D35(소유 1 · 남 10): 고치기 전 D35a `{"C1": "ST12|static/css"}` · D35c exit 2 `ⓐ 잔존 1` → 고친 뒤 exit 0 `ⓐ 잔존 0 … 범위 밖 남은 빚 10` · D35b 대조. `make verify-web`(사본) exit 0 — 백스톱 113 · debt 100 · subst 136 · sdk 258 · refactor_audit 217 · extract 31 · contract 13. Claude ↔ Codex scripts diff 0 · houserules byte 같음. **주의: 스캐너 지문이 바뀌어 지금 후보가 얼린 `debt-g0.json`(X4 것 포함)은 `--debt-residual` 에서 «판 경계» → G0 다시 스캔 필요(일부러 — 옛 폴더 키가 조용히 해소로 읽히지 않게).** 봉인 매니페스트는 다시 만들지 않음(web-rel2 에 얹을 때 B 다시).
- 16:33 lead: 배포 노트의 낡은 줄(«슬라이스 0 은 테스트 파일을 옮기지 않고») → r1 #2 대로 «코드와 함께 테스트 파일도 같은 자리 대응으로 옮김 · 옮겨 온 파일만인 새 묶음엔 새 테스트 요구 없음» + 한계 «새 자리 짝 찾기는 git 개명 감지».
- 17:13:15 ④ **F-X4-2 고침**(`S/web-fix1` 커밋 `a2bc336b27689ffd23e5818654256070a9d81e15` · 556c188c 위 · push 없음): 빚 질문의 답은 G0 승인이 아니다 — 답을 받으면(Codex 는 다음 턴) step 5 G0 배너로 가고 배너의 빚 1행에 답을 싣는다 · «빚 답 받음 · G0 배너 전» 상태는 `## G0` 절을 쓰지 않고 phase 는 scope 그대로 · `## G0` 절과 phase=design 은 step 5 배너 승인 뒤에만 · 세션 사멸 재개는 phase=scope 면 step 4′ 스캔 · 빚 질문부터 다시 · Codex «게이트 = 평문 질문» 에 «선택지 질문의 답은 게이트 승인이 아니다 — 다음 턴은 그 질문 다음 단계부터». 고친 곳 Claude `commands/dddjango-web.md` :69 · :160 · :165 · :169 · :171 / Codex `SKILL.md` :80 · :113 · :180 · :185 · :189 · :191. 러너(`debt.py` `_HEAD_RE` · `residual_sets` · `refactor_audit.py` `_scope_decisions`)가 읽는 `## G0` 꼴은 그대로(쓰는 때만 늦춤) · 새 검사기 · 픽스처 변경 없음. `make verify-web` exit 0(백스톱 113 · debt 100 · subst 136 · sdk 258 · refactor_audit 217 · extract 31 · contract 13). 노트 :24 한 줄.
- 17:14 운영자: 새 후보 `S/web-rel3`(web-rel2 clone · A 위 F-X4-1 · F-X4-2 · build-log docs · 봉인 B 다시) → ⑥.
- 17:23 운영자: **F-A2-1**(사용자 실레인 admin-2 · 설치본 2.0.1 · 내려받은 Claude Design 폴더의 새 `<x-dc>` 꼴에서 `extract_dc.py` «화면 후보 0개») → ④ · 2.0.1 바탕 새 사본 `S/web-202`.
- 17:24:52 운영자: 사용자 결정 «추천방향으로해줘» — **F-A2-1 은 2.0.2 로 먼저 따로 냄**(배포 승인 포함) · web-202 가 임계 경로 1순위 · 2.1.0 은 2.0.2 배포 뒤 새 main 위로 다시 얹음(web-rel3 6cfb83e4 판은 겹침 확인용) · 그때 2.1.0 노트에 «2.0.2 의 x-dc 시안 수리 포함».
- 17:29 ④ F-A2-1(2.0.2 판) 끝 — `S/web-202` 커밋 `d06c69e3`(extract_dc 가 `<x-dc>` 루트 하나를 화면으로 · 게이트 글은 보이는 글에서 · fixtures_extract 32/8 → 41/0 · 사용자 폴더 사본 Login · v5 exit 0) · web-rel3 위 cherry-pick 깨끗.
- 17:28 ⑥ web-rel3(6cfb83e4 판 · 겹침 확인용) HEAD `d56306d3` · verify 5/5 · verify-web green · DRY v2.0.1 → v2.1.0.
- 17:36 운영자: X4 끝(17:31:17) → F-X4-1 확인 2 · 그림 화면 확인(⑧) · F-X4-3(③ — `.ruff_cache` 등 도구 캐시 폴더를 구조 검사가 잡던 것 · `S/web-fix1` 위 커밋).
- 17:37:38 lead F-X4-1 확인 2: X4 최종 트리(d415a8fa1 clone)에 고친 판 `--debt-residual` → exit 0 · `ⓐ 잔존 0 · 요구 잔존 0 · 재상정 제외 0 · G0 에 없던 키 0 · 범위 밖 남은 빚 30`(static/css 10 + 옛 chart 폴더 범위 밖 20) · 기록 `S/web-fix1-check/result.md`.
- 17:39 운영자: 사용자가 2.1.0 도 배포까지 자동으로 맡김 · 2.0.2 를 `S/web-cl3` 에서 배포 중(R main 2c32c89e) → 2.0.2 release 커밋 위로 `S/web-rel4`(A · F-X4-1 · F-X4-2 · F-X4-3 · build-log docs · **그림 docs 커밋**(정정 — visual-check 산출물 포함 · 초안 표지 지움 · master.html 안 건드림) · 봉인 B 마지막) · 노트는 운영자가 채움(f93646cb8a14) + F-X4-3 한 줄(③). ⑥ 준비시킴.
- 17:42:07 ⑧ 그림 화면 확인: archify visual-check exit 0 · pass(1440 · 1600 · 1920 · 2048 넘침 0 · 최소 글자 8.02px · 빛/어둠 스크린샷 눈 확인) · 트리 · 안내 headless(1440 · 2048 · 390 × 빛/어둠 · 가로 넘침 0 · 탭 · 행 선택 · 말풍선 · 2장 → 1장 동작) · 고친 것 둘(390px 트리 메모가 핀 칸 덮음 → 트리 상자 가로 스크롤 · 2장 긴 코드 줄 → 줄바꿈) · 초안 표지 지움 · delivery.json visual 칸 · 최종 11 파일(R docs 같은 이름).
- 17:49:17 운영자: **2.0.2 배포 끝** — release `41959a7236c82c9512ee356e61321832ff89d03d`(태그 dddjango-web--v2.0.2 · R main ff) → web-rel4 시작(⑥).
- 17:50:22 ③ **F-X4-3 고침**(`S/web-fix1` 커밋 `22d4073759c6db4585a8ea41b1ef453889a467f0` · a2bc336b 위): `src/common.py:72` `TOOL_CACHE_DIRS = {'__pycache__', '.ruff_cache', '.pytest_cache', '.mypy_cache'}` · :646 수집(os.walk)에서 건너뜀(같은 수집을 쓰는 모든 패밀리에 적용 · 빚 스캔은 `ls-files -co --exclude-standard` 라 이미 같은 뜻) · 양판 byte 미러(sha 앞 12 `1bc9d7f309af`) · 픽스처 F17(`run_fixtures.sh`): 고치기 전 `FAIL F17a … [ST3] BLOCKER — web/application/order/.mypy_cache · .pytest_cache · .ruff_cache · [ST8] BLOCKER — web/root/.ruff_cache` → 고친 뒤 PASS F17a · F17b(일반 이름 비표준 폴더 ST3 대조) · F17c(root 직속 ST8 대조) · 백스톱 116/0. 노트 한 줄(sha 앞 12 `cddfb83ce393`).
