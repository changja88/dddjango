# 계획 축소 재검토 (2026-09-15)

대상: `workspace/plan/2026-09-15-web-refreeze-full-rebuild.md`(v2)
기준: `design-review/plan-review.md`(직전 리뷰) · `workspace/design/2026-09-15-web-refreeze-full-rebuild.md`(v5)
범위: 폐쇄 확인 하나. 새 감사 축·설계 결정 재감사는 열지 않았다.
도구: Serena·Graphify 모두 워크트리 opt-in 표식 부재(`.serena/project.yml`·`graphify-out/graph.json` 없음) — 기본 검색·읽기 도구로 수행.

## 판정

**실행 진입 불가 (미폐쇄 BLOCKER 0 · MAJOR 0 · MINOR 0 · 신규 충돌 2 — BLOCKER급 1 · MINOR급 1)**

직전 리뷰의 BLOCKER 3 · MAJOR 10 · MINOR 8 · 커버리지 △✗ 14항은 **전건 닫힘**이다.
다만 v2가 폐쇄를 위해 새로 붙인 두 문장이 서로를 부정한다 — m-1을 닫은 «`scripts/` 안의
`carried_from` 잔존 0»(plan:136)과 BL-2를 닫은 «거부 픽스처를 **수정**해 남긴다»(plan:133)가
같은 Task 안에서 충돌하고, 그 파급으로 plan:165의 «B 전건 green»도 성립하지 않는다.
직전 BLOCKER와 같은 «Task가 자기 힘으로 만들 수 없는 green» 부류라 같은 등급으로 둔다.
필요한 수정은 **범위 규칙 한 줄**이다(계획은 고치지 않았다).

## 폐쇄 대조

### 직전 BLOCKER·MAJOR·MINOR

| id | 계획 v2 근거(행) | 판정 |
|---|---|---|
| BL-1 계약 검사가 Task 경계를 가로지름 | plan:22(Global «중간 Task 합격 = 자기 Files 잔존 0 · 전건 green은 T7 S6») · plan:109(T3 합격) · plan:136(T5 합격) · plan:149·152(T6 S6·합격) · plan:165(T7 S6) | **닫힘** |
| BL-2 `test_interaction_evidence.py` 누락 | plan:36(파일표) · plan:128(T5 Files «+미러 4») · plan:133(T5 S4 명시 지시 + 근거) | **닫힘** |
| BL-3 설계 §4.4 미매핑 | plan:64(T1 S1 — 실재 7종·조건부 render-audit·3겹 해소·v2 관찰·폐기 집합 자기 검사) · plan:74(T1 S3 «§4.1~4.6») | **닫힘** |
| M-1 §5 병행 실행 금지 | plan:145(T6 S2 열거에 «§5(병행 실행 금지)») | **닫힘** |
| M-2 R6 이월 절차 | plan:145(«R6(`interaction_exclusions` 행 재작성·10% 재검증·미대응 행 배너)») | **닫힘** |
| M-3 `test_refreeze.py` 미배선 | plan:30(파일표 `fixtures_refreeze.sh`) · plan:60(Files «+미러 3») · plan:75(S4) · plan:78(합격 «run_fixtures.sh가 새 픽스처를 실제로 실행») | **닫힘** |
| M-4 §4.6-1·-5·§3-4 지시 부재 | plan:67(planned live `scope.md` sha 대조 → exit 1) · plan:70(`done` 4단 순서) | **닫힘** |
| M-5 R9 `_prev-*` 누락 | plan:104(T3 S1 «`_refreeze-*` 또는 `_prev-*`») · plan:117(T4 S1 동일) | **닫힘** |
| M-6 `commands:70` 미지목 · T6이 B를 뺌 | plan:37(파일표 `:70`) · plan:92(T2 red 목록 포함 요건) · plan:146(T6 S3 «`:70` build-state `refreeze` 키 제거») · plan:149(T6 S6이 «A·D1~D4» 열거를 버리고 «red 목록에 commands 항목 0»으로 전환) | **닫힘** |
| M-7 `release-web` 클린 트리 충돌 | plan:3(«릴리즈 직전의 보관·복원 절차는 Task 8 Step 11» 명시 예외) · plan:184-190(보관→커밋→`git checkout --`→봉인 chore→release→복원) | **닫힘** |
| M-8 릴리즈 권한 자가당착 | plan:3(«릴리즈는 사용자 승인 뒤 이 계획의 마지막 단계이며 권한 안이다. 권한 밖은 A8 앱 수정뿐이다.») | **닫힘** |
| M-9 B3·B4 주입 수단 부재 | plan:28·72(`--stop-after <phase>` 신설) · plan:176(B3 `commit --stop-after discarded` → `--resume`) · plan:177(B4 «폐기 집합 밖 live `captures/`에 동명 파일 심기») | **닫힘**(신규 충돌 ② 참조) |
| M-10 B1·B2 주체·전제 부재 | plan:174(B1 실행 주체 = 별도 `claude -p /dddjango-web:dddjango-web` 세션 · `--plugin-dir` · 비용) · plan:49(사본이 Django 루트로 성립) · plan:51(브라우저 env 확인) · plan:175(B2 «case마다 별도 프로세스라 호출 사이 치환») | **닫힘** |
| m-1 T5 합격 범위 무정의 | plan:136(«**`dddjango-web/scripts/` 안의**» + «규범 쪽은 Task 6·7 소관») | **닫힘**(신규 충돌 ① 참조) |
| m-2 `DEVELOPMENT.md` 갱신 빈약 | plan:15(Global «§1·§4») · plan:166(T7 S7 — §1 지도 2행 + §4 한 문단, 선례 판형 지명) | **닫힘** |
| m-3 `REQUEST_GUIDE` 절차 | plan:163(T7 S4 «`docs/DEVELOPMENT.md:69-77` 절차 전체» 5단 인용 — 실측 :69-77과 문면 일치) | **닫힘** |
| m-4 Codex 역할 SKILL «같은 턴» | plan:17(Global «정본과 미러를 같은 Task 같은 턴에서») · plan:162(T7 S3 «Codex 역할 SKILL에 같은 턴 반영(의미 미러·기계 대조 없음)») | **닫힘** |
| m-5 `commands:171` ⑤ 미지명 | plan:37(파일표 `:171`⑤) · plan:146(T6 S3 «`:171` ⑤에 «커밋 전 `_refreeze-*`·`_prev-*` 잔존 없음 확인» 추가») | **닫힘** |
| m-6 G0 배너 고아 k건 1줄 | plan:145(«§2.2(고아 배너·종료 보고 «미참조 k건 지우지 않음» 1줄 포함)») | **닫힘** |
| m-7 `verify-web-browser` 전제 | plan:189(«선행 `verify-web-browser` ≈19분» — `Makefile:302`·`docs/DEVELOPMENT.md:147`과 일치) | **닫힘** |
| m-8 조감도 HTML | plan:15(Global 범위) · plan:42(파일표) · plan:181(T8 S8 «조감도 `ontology-adoption-map.html` 갱신(사용자 상시 지침)») | **닫힘** |

### 직전 커버리지 표의 △·✗ 항목

| 설계 규정 | 계획 v2 근거(행) | 판정 |
|---|---|---|
| §2.1 고정 폐기·교체 목록(design:57-60) | plan:63(T1 S1 «**고정 폐기 목록(설계 §2.1)**») · plan:74 | **닫힘** |
| §2.2 G0 배너·종료 보고 1줄(design:69) | plan:145 | **닫힘** |
| §3-1 begin이 scope 복사·sha 기록(design:85) | plan:63(journal «설계 §4.2 전 필드» → `scope_sha256_at_begin`) · plan:66(«`begin`이 `copied_inputs`를 staging에 복사») | **닫힘** |
| §3-4 commit의 live scope sha 대조(design:91-92) | plan:67 | **닫힘** |
| §4.1 `check --render-audit-skipped` 유일 주체(design:112-113) | plan:65(«journal 값을 내리는 **유일 주체**») | **닫힘** |
| §4.3 begin의 staging 복사 입력(design:159-161) | plan:66 | **닫힘** |
| §4.4 `check`의 검사 내용(design:163-169) | plan:64 | **닫힘** |
| §4.6-1 planned·sha 대조(design:183-184) | plan:67 | **닫힘** |
| §4.6-5 done 순서(design:195-197) | plan:70(4단 순서 명시) | **닫힘** |
| §5 병행 실행 금지(design:207) | plan:145 | **닫힘** |
| R6 `interaction_exclusions` 이월(design:211-215) | plan:145 | **닫힘** |
| R9 `_prev-*` 감지(design:246-247) | plan:104 · plan:117 | **닫힘** |
| §7 제거 대상 표 10행(design:255-266) | archive plan:130 · test_design_archive plan:131 · check_design_evidence plan:132 · test_interaction_evidence plan:133 · commands(+Codex) plan:144-148 · design-acquisition plan:160 · design-evidence plan:161 · agents(+Codex 역할) plan:162 · REQUEST_GUIDE plan:162 · test_evidence_debt{,_hook} plan:107 | **닫힘**(10/10) |
| §10 B1~B10(design:302-315) | B1 plan:174 · B2 plan:175 · B3 plan:176 · B4 plan:177 · B5·B7 plan:178 · B6·B10 plan:179 · B8·B9 plan:180 | **닫힘**(10/10) |

## 미폐쇄·신규 충돌 상세

### ① [BLOCKER급 · 신규] Task 5 Step 4가 남기는 `carried_from` 리터럴이 plan:136·plan:165와 충돌

- plan:133(T5 S4)은 `test_manifest_row_accepts_carried_from_only`를 «제거»가 아니라
  «기대 exit를 2로 **수정**»하라고 지시한다 → 리터럴이 그대로 남는다.
  실측 잔존 4곳: `dddjango-web/scripts/test/test_interaction_evidence.py:626`(테스트 이름)·
  `:627`(`('carried_from', '4'*64)`·`('carried_from','not-a-sha')`)·`:632`·`:641`
  (+ byte 미러 `codex-dddjango-web/skills/dddjango-web/scripts/test/test_interaction_evidence.py` 동일).
- plan:136(T5 합격)은 «**`dddjango-web/scripts/` 안의** `--compare-build`·`carried_from` 잔존 0
  (규범 쪽은 Task 6·7 소관)»이다. 괄호의 예외는 «규범»뿐이고 시험 파일은 그 범위 안이다.
  → **같은 Task의 Step과 합격이 서로를 부정한다.** m-1을 닫으려고 붙인 디렉터리 범위와
  BL-2를 닫으려고 붙인 «수정해서 남긴다»가 v2에서 처음 만났다.
- 파급: 설계 §8-B(design:276)도 «`carried_from` 잔존 0»이고, plan:72(T2 S1)는 «설계 §8의
  A·B·C·D1~D4»를 그대로 구현하라고만 한다(범위 규칙 없음). 따라서 검사 B는 이 파일에서
  **영구 red**가 되고 plan:165(T7 S6) «A·B·C·D1~D4 전건 green»도 성립하지 않는다.
  T7 S6은 이번 판형에서 유일한 전건 green 지점이므로 그물 전체가 그 자리에서 멈춘다.
- 범위 자체는 샌 곳이 없다 — 세 토큰의 실측 잔존 파일 전수가 Task Files로 덮인다
  (`archive_design.py`·`check_design_evidence.py`·`test_design_archive.py`·
  `test_interaction_evidence.py` = T5 · `commands`·Codex `SKILL.md` = T6 ·
  `design-acquisition.md`·`design-evidence.md` = T7). **비어 있는 것은 거부 픽스처 1곳의
  범위 규칙뿐이다** — 검사 B의 허용 목록 또는 «수용 경로 잔존 0»으로의 한정 한 줄.

### ② [MINOR급 · 신규] `--stop-after`가 설계 §4.1 인자·exit 표 밖이고 중단 exit가 미정의

- plan:28·72가 신설한 `--stop-after <phase>`는 설계 §4.1의 `commit` 인자
  (design:106 — `--build [--staging] [--resume]`)에 없다.
- 그런데 plan:18(Global)은 «`refreeze.py`는 설계 §4.1 표대로 0/1/2/3», plan:11은
  «충돌 시 설계 v5가 우선한다»고 못박는다. 문면 그대로면 신설 인자가 설계에 밀려 M-9가 다시 열린다.
- exit도 미정의다 — §4.1의 commit exit는 «0 완료 · 3 중단·되감김 · 1 오류»뿐인데
  `--stop-after` 중단은 «완료»도 «되감김»도 아니다. plan:176(B3)은 그 뒤 `commit --resume`
  완주를 요구하므로 되감기가 **아니어야** 한다.
- M-9의 폐쇄 자체는 유효하다(B3·B4가 재현 가능해졌다). 필요한 것은 exit 값 한 줄이다.

## 확인했으나 정합 (보고 대상 아님)

- **Task 8 Step 11 ↔ Global Constraints** — 충돌 없음. plan:3이 «작업 중에는 커밋·스태시·
  브랜치 전환으로 … 수용하지 않는다**(릴리즈 직전의 보관·복원 절차는 Task 8 Step 11)**»로
  명시 예외를 뒀고, plan:184-190의 6단이 실물과 일치한다:
  `Makefile:328-331`(비-DRY에서 dirty면 `die`) · `Makefile:302`(`release-web: verify-web-browser _release`) ·
  `Makefile:323-326`(main 전용) · `docs/DEVELOPMENT.md:145·147·149`.
  봉인 순서도 `docs/DEVELOPMENT.md:149`(«봉인 대상을 바꾼 커밋 **뒤에** 별도 chore 커밋»)와 일치하고,
  plan:164가 고치는 `Makefile`은 봉인 protocol 군(`workspace/tools/manifest_seal.py:143`)이라
  Step 11-4의 재발행이 실제로 필요하다. 보관·복원 대상 `docs/master.html`·`…lanes.md`는
  봉인 글롭 밖이므로(`manifest_seal.py:51-187`에 `docs/` 항목 0) 릴리즈 뒤 복원이 `sealed_commit`을 깨지 않는다.
- **계획의 규범 행 인용 전수 실측 일치** — `commands/dddjango-web.md` `:22`(«## 산출물 위치») ·
  `:70`(build-state `refreeze` 키) · `:129`(«ⓑ defer가 허용하는 것 = 재동결·조회·보고» **와**
  «scope 바이트가 바뀌면 … review digest가 어긋난다»가 같은 줄) · `:137` · `:144`(«재기준 승인
  직후에도 blocked를 유지하며» + 실패 회차 이력 보존) · `:146`(입력 게이트 `--build <산출물 폴더>`) ·
  `:171`(Phase 2 진입 준비) · `:227`(«ⓐ 재동결») · `REQUEST_GUIDE.md:116` ·
  Codex `SKILL.md:123`·`:151` · `design-acquisition.md:27`·`:116` ·
  `agents/design-review-web.md:25`(+Codex 역할 `SKILL.md:28`).
- **plan:164(T7 S5)의 «`--self-test` + 본 검사» 배선**이 선례와 같다(`Makefile:108-109`의 `web_hooks_contract.py`).
- **미러 수** — T1 «미러 3»(refreeze/test/fixtures) · T3 «미러 4» · T4 «미러 2» · T5 «미러 4» 모두 Files 열거와 일치.

## 미확인

- **`make verify` / `make verify-web` / 계약 검사 실제 실행** — 읽기 전용 재검토라 돌리지 않았다.
  신규 충돌 ①은 시험 소스 실측 4곳과 설계 §8-B·plan:136 문면의 정적 대조로 판정했다.
- **A8 워크트리 실물** — 읽기 전용 지시에 따라 접근하지 않았다. plan:49가 요구하는
  `manage.py`·`config/`·`web/`·표적 빌드 폴더의 실재는 미확인이다.
- **`web_refreeze_contract.py`의 red 목록 입도** — 도구가 아직 없다. plan:92-94·149·160이
  «파일:행» 단위 red 목록을 전제하는데 plan:86(T2 S1)은 그 입도를 지시하지 않는다.
  ①의 «B가 파일 단위로 red를 낸다»는 판단도 이 전제 위에 있다.
- **plan:189의 `printf '1\ny\n'`** — `_release`가 실제로 그 입력을 받는지는 실행 없이 확인 불가다.
  선택지 `0) current`·`1) patch`의 실재만 확인했다(`Makefile:343-344`).
