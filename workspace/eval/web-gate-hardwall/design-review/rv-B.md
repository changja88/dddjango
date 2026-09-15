# 적대 검토 B — 이 설계로도 남는 «불가» (2026-09-15)

검토 대상: `workspace/design/2026-09-15-web-gate-hardwall.md`
판정 기준(사용자 지시): «재동결하라고 하고 차이점이 있으면 수정하게 하면 된다. 이게 어떤 이유로든
불가능해지는 것 자체가 말이 안 된다.»
BLOCKER = 설계를 그대로 구현해도 이 기준이 충족되지 않는 상태.

## 하드월 전수 표

«실질 하드월» = 사용자가 사실을 알고 진행을 지시해도 열리지 않거나, 우회로가 규범에 명시돼 있지 않은 것.

| # | 위치(파일:줄) | 조건 | 우회로 | 규범에 명시? | 실질 하드월? |
|---|---|---|---|---|---|
| 1 | `check_design_evidence.py:895-897` | 예외 행수 ×10 > 활성 대상 | 없음 | — | 예(설계 H1 대상) |
| 2 | `check_design_evidence.py:1048-1051` | archive case에 v2 관찰 없음 | 재수집뿐 | 재수집만·불가 시 경로 없음 | 예 |
| 3 | `check_design_evidence.py:1006-1010` | 수집기 sha ≠ 설치본 assets | 재수집뿐 | «무조건 결함»만 명시 | 예 |
| 4 | `check_design_evidence.py:668-673` | `outside_root.count > 0` | `--excluded-regions` 고쳐 재수집 | 예(design-acquisition) | 조건부(재수집 불가 환경) |
| 5 | `check_design_evidence.py:654-655` | `root.found ≠ true` | 루트 선언 고쳐 재수집 | 예(K2) | 조건부 |
| 6 | `check_design_evidence.py:963-975` | 잔여 ≠ 0 | `interaction_exclusions` 승인 행 | 예 | 아니오(단 #1과 곱해짐) |
| 7 | `check_design_evidence.py:947-960` | 표면 미연결 | case `reached_by` 또는 표면 예외 | 예 | 아니오 |
| 8 | `check_design_evidence.py:995-997` | `environment_error ≠ null` | 문서 교체(재수집) | 「exit 1」만 명시 | 조건부→예(backstop에선 #16) |
| 9 | `check_design_evidence.py:1084-1085` | design-input 최상위 미지 필드 | 설치본/저장소 판형 일치 | 없음 | 예(설계가 키를 늘린다) |
| 10 | `check_design_evidence.py:1122-1123·1170-1172` | archive manifest 2개 이상·인벤토리 불일치 | 재동결·파일 정리 | 예 | 아니오 |
| 11 | `check_design_evidence.py:1260-1263` | 프로젝트에 `web/` 없음 | `web/` 생성 | 없음(비시안 실행엔 미기재) | 예 |
| 12 | `check_design_evidence.py:1328-1329` | case `result ≠ pass` | 승인된 이탈도 `pass`로 적음 | 없음 | 아니오(과허용) |
| 13 | `archive_design.py:35-36` | 원본 트리 4096 파일 초과 | 없음 | 없음 | 예 |
| 14 | `backstop.py:281-282` | config에 design_source 有 · 빌드 폴더 0 | config.json 수동 편집 | 없음 | 예 |
| 15 | `backstop.py:286-293` | 어느 폴더든 `_refreeze-*`/`_prev-*` 잔존 | `commit --resume`/`abort` | 예 | 조건부(#24와 결합 시 예) |
| 16 | `backstop.py:299-310` | `validate_inputs`가 ValueError → `except Exception` | 없음(문서 교체뿐) | 없음 | 예 |
| 17 | `backstop.py:95-123·299` | legacy v1 허용이 backstop 런 속성 | CLI엔 없음 | 예(design-evidence:183-192) | 아니오(설계상 의도) |
| 18 | `refreeze.py:346-351` | 증거 문서 1건이라도 못 읽음 → `begin` exit 1 | 없음 | 없음 | 예 |
| 19 | `refreeze.py:422-429` | staging에 `screen-meta.json`·`design-tokens.json`·`asset-manifest.json`·`design-ref/` 없음 | 없음(dc 경로 외엔 생산 주체 부재) | 요구만 명시 | 예 |
| 20 | `refreeze.py:49·442-446` | `has_render_audit=false` + enum 밖 사유 | 없음(거짓 사유뿐) | enum 닫힘 명시 | 예 |
| 21 | `refreeze.py:477-479` | staging case에 v2 관찰 없음 | 재수집뿐 | 예 | 예(#2와 동일 축) |
| 22 | `refreeze.py:509-511` | `check` 미통과 상태의 `commit` | `check` 통과 | 예 | 아니오 |
| 23 | `refreeze.py:556-561` | 교체 후 live inputs ≠ 0 → 되감기·exit 3 | inputs 통과 | 예 | 조건부 |
| 24 | `refreeze.py:503-506·526` | `journal.json`/`swap-plan.json` 손상·부재 조합 | 수동 `rm` | 없음 | 예 |
| 25 | `commands/dddjango-web.md:147·152` | inputs exit 0 없이는 ready·Phase 1 진입 불가 | 없음(«미검증 수락은 검사 성공이 아니다») | 예(명시적 문 없음) | 예 |
| 26 | `commands/dddjango-web.md:179` · `agents/coder-web.md:44-45` | 모든 coder 호출 직전 inputs exit 0 | 없음 | 예 | 예 |
| 27 | `commands/dddjango-web.md:130` | 부채 defer 상태의 구현 재진입 | ⓐ observe(전량 재관찰)뿐 | 예 | 예 |
| 28 | `commands/dddjango-web.md:191` | 마무리 backstop 전체 exit 0 | 발견 해소 | 예 | 아니오 |
| 29 | `commands/dddjango-web.md:138` | 완료 빌드 재동결 → `implementation_visual=pending` | G2 재대조 | 예 | 아니오 |
| 30 | `assets/observe_interactions.pw.js:650-654` | `max_steps`는 문서 전체 기준(resume 무효) | `--max-steps` 상향 | 예(design-acquisition:139) | 아니오 |

**행 30 · 실질 하드월 «예» 17 · 조건부 4 · 아니오 9.**
30행 중 설계(H1+H2)가 실제로 여는 것은 **#1 하나**이고, #6은 #1과의 곱이 풀리면서 함께 완화된다.
나머지 15개의 «예»는 설계 후에도 그대로 남는다.

---

### [BLOCKER] H1은 «관찰됐으나 잔여가 많다» 축만 연다 — «관찰 자체가 불가능» 축에는 여전히 문이 없다

**막히는 시나리오**
1. A8 빌드(`collection=archive`)에서 사용자가 «드롭다운 4개를 시안대로 고쳐라»를 지시한다.
2. 구현 재진입이므로 `commands:130`의 래칫이 ⓐ observe를 요구한다.
3. 그 시점에 브라우저 채널이 없다(`--browser-channel`/`--cdp` 부재) 또는 Playwright 모듈이 없다
   → 드라이버 exit 1, **문서가 아예 쓰이지 않는다**(`observe_interactions.pw.js:74`는 EnvironmentError에서
   `writeDocument`를 타지 않는다).
4. `--phase inputs`는 `check_design_evidence.py:1048` «interaction evidence required (version 2 with
   interactions)»로 exit 2.
5. 사용자가 «관찰 못 한 건 안다, 그대로 진행해라»라고 말해도 `evidence_scope`는 이 발견을 건드리지 않는다
   — 설계의 문은 `_check_exclusions`의 상한 위에만 났다.
6. `commands:152`는 «승인 자체·실패 공개·미검증 수락은 검사 성공이 아니»라고 못 박고,
   `agents/coder-web.md:45`는 exit 2에서 «코드 변경 없이 반환»을 강제한다. 행동 0.

**근거**
- 설계 §3: «H3 증거 부채 래칫 완화 — 하지 않는다. H1이 «불가»를 이미 제거하므로 래칫은 더 이상 막다른 길을
  만들지 않는다». 이 전제가 틀렸다. H1이 제거하는 «불가»는 *관찰이 성립한 뒤*의 잔여 상한 하나뿐이다.
  관찰이 성립하지 않으면 H1의 `evidence_scope`는 게이트에 닿지도 않는다(`_check_exclusions`는
  `interaction_exclusions`가 있을 때만 도는 함수이고, v2 부재 발견은 `_source_observation` 안에서 난다).
- 즉 설계 §3의 «하지 않는다»의 근거 문장이 사실과 어긋난다.

**필요한 조치**
`evidence_scope.level`을 `full|partial` 2종이 아니라 **«관찰 없음(unobserved)»을 포함한 3종**으로 두고,
`_source_observation`의 v2 필수 발견도 같은 문을 지나게 한다. 또는 H3를 채택해 defer 상태에서도
«미관찰 명시 + 영구 기록» 조건으로 구현 재진입을 허용한다. 둘 중 하나가 없으면 사용자 지시는 미충족이다.

---

### [BLOCKER] H2가 수집기 바이트를 바꾸는 순간, 기존 모든 v2 증거가 무효가 된다

**막히는 시나리오**
1. 이 설계가 릴리즈된다. §4 표대로 `assets/observe_interactions.pw.js`·`assets/interaction_audit.js`가
   `data_variant`/`data_variant_folded` 때문에 바뀐다.
2. 그 이전에 동결된 모든 빌드의 `interactions.json`이 가진 `collector.snippet_sha256`·`driver_sha256`는
   설치본 assets의 sha와 달라진다.
3. `check_design_evidence.py:1006-1010`이 «이 플러그인의 수집기 바이트가 아니다»로 exit 2.
   `design-evidence.md:272-274`는 «a mismatch is a defect **no matter what the rest of the document says**».
4. 그 빌드는 이제 coder 호출도(#26), 마무리 backstop도(#28) 통과하지 못한다. 유일한 문은 전량 재수집인데,
   원본이 사라졌거나(디자인 프로젝트 삭제 — `commands:135` ⓑ) 브라우저가 없으면 영구히 닫힌다.
5. 사용자가 «수집기가 바뀐 것뿐이고 관찰 내용은 그대로다, 진행해라»라고 해도 여는 장치가 없다.

**근거**
- `COLLECTOR_ASSETS`(`check_design_evidence.py:237`)는 **현재 바이트 1쌍**만 인정한다. 과거 sha 허용 목록도,
  판형 버전 필드도, 승인 우회도 없다.
- 설계 §4는 이 두 파일을 «변경» 대상으로 명시하면서 소급 무효화를 언급하지 않는다.
- 이 벽은 이번 수리에만 해당하는 일회성이 아니다 — 수집기를 고칠 때마다 반복된다.

**필요한 조치**
① 수집기에 판형 버전을 도입하고 검사기가 **허용 sha 집합**(현재 + 알려진 과거 판형)을 갖거나,
② sha 불일치를 «발견»이 아니라 `evidence_scope`와 같은 «지위 강등 + 영구 기록»으로 내리거나,
③ 최소한 이 릴리즈의 마이그레이션 절차(기존 빌드 전수 재수집 혹은 sha grandfather)를 설계에 넣어야 한다.

---

### [BLOCKER] 재동결이 `.dc.html` 경로 전용이다 — 다른 출처의 빌드는 «재동결하라»가 영구 불가

**막히는 시나리오**
1. 참조 HTML/URL로 동결한 빌드(`commands:141` 경로)에서 사용자가 «재동결해라»라고 한다.
2. `refreeze.py begin` 성공 → staging에 재수집 수행.
3. `refreeze.py check`가 `REQUIRED_STAGING`(`refreeze.py:39-40`)에서 **`screen-meta.json` 부재**로 exit 3.
4. `screen-meta.json`을 만드는 도구는 저장소 전체에서 `extract_dc.py`뿐이다(`--meta` 인자는 그 파일에만 있다).
   참조 HTML 경로의 추출 순서(`commands:141`)는 `extract_design.py`만 부르고 `--meta`가 없다.
5. `commit`은 `refreeze.py:510-511`에서 «check 를 통과하지 않았다»로 거부. `abort` 외에 취할 행동이 없다.
6. 이미지 단독·자체 설계 빌드는 `design-ref/` 실재 요구(`refreeze.py:422-424`)에서 같은 방식으로 막힌다.

**근거**
- 규범은 재동결을 출처별로 한정하지 않는다 — `design-acquisition.md:50-52` «사용자가 요청했을 때만 실행하며,
  **요청이 있으면 항상 전량 재실행한다**». `commands:130`은 폴더 재사용 질문에서 출처 종류와 무관하게
  재동결을 선택지로 연다.
- 반면 `check`의 요구 목록은 dc 경로의 산출물 집합을 그대로 못박았다. 규범과 집행의 정면 충돌이다.
- 검사기 본체는 `screen-meta.json`을 **선택**으로 취급한다(`check_design_evidence.py:758-768` —
  `meta.is_file()`일 때만 보고, `design-evidence.md:274-278`은 «any other entrypoint … records its `--root`
  as a declared input instead»). 즉 `refreeze.py`만 혼자 필수로 요구한다.

**필요한 조치**
`REQUIRED_STAGING`을 **live 빌드에 실제로 있던 산출물 집합**(= `journal.discard_set`에 포함된 것)으로
동적으로 정하거나, 출처 종류별 필수 집합을 분기한다. 설계 §4 표에 `refreeze.py`가 없으므로 이 수정은
현재 계획에 들어 있지 않다.

---

### [BLOCKER] 렌더 실측 생략 enum에 «측정할 DOM이 없음»이 없어, 이미지·자체 설계 빌드의 재동결이 영구 exit 3

**막히는 시나리오**
1. `build-state.json` 스키마(`commands:70`)는 «측정할 DOM이 없는 이미지 단독·자체 설계 경로면
   `has_render_audit=false`»를 **정상 상태**로 정의한다.
2. 그 빌드에서 재동결을 지시한다. `refreeze.py:442-446`이 «렌더 실측이 이 빌드에서 꺼져 있는데 사유 기록이
   없다»로 exit 3.
3. 사유를 대려면 `SKIP_REASONS`(`refreeze.py:49`) = «원본 열람 불가 · 필요한 인증 상태 접근 불가 ·
   브라우저 채널 부재» 중에서 골라야 한다. 셋 다 사실이 아니다.
4. `commands`는 «그 외 사유는 생략으로 받지 말고 배너에서 재질문한다»로 enum을 닫아 놨다.
   → 참을 적으면 exit 3, 거짓을 적으면 증거 위조. 행동 0.

**근거** `refreeze.py:442-446`의 주석은 «상속된 false 를 그대로 통과시키면 … 사유 없이 영구 침묵한다»이지만,
이 빌드의 false는 «상속»이 아니라 **구조적 해당 없음**이다. 두 상태를 구분하는 값이 없다.

**필요한 조치** enum에 «측정 대상 DOM 없음»을 추가하거나, `journal.has_render_audit`가 애초에 false였고
그 사유가 `build-state`에 있으면 재질문 없이 통과시킨다.

---

### [BLOCKER] `refreeze begin`이 «증거가 깨졌다»는 이유로 재동결을 거부한다 — 재동결이 고칠 대상이 재동결을 막는다

**막히는 시나리오**
1. 어떤 이유로 `captures/<screen>-interactions.json`이 사라지거나 `design-input.json`이 깨진다
   (중단된 정리, 수동 삭제, 판형 변경 실패).
2. 사용자가 정확히 그래서 «재동결해라»라고 한다.
3. `cmd_begin`이 `discard_set(build, errors)`를 부르고, `evidence_pointers` → `_walk_observation` →
   `_read_document`가 «파일이 없다»/«JSONDecodeError»를 `errors`에 넣는다(`refreeze.py:91-105·132-154`).
4. `refreeze.py:346-351`이 exit 1. **staging도 만들어지지 않는다.**
5. 재동결은 폐기 집합을 «지울 대상»으로만 쓴다 — 없는 파일은 지울 것도 없다. 그런데도 시작이 막힌다.

**근거** `design-input.json`은 `FIXED_DISCARD_FILES`에 들어 있어 재동결이 **어차피 통째로 새로 만든다**
(`refreeze.py:32-36`). 그 파일이 깨졌다는 사실은 재동결의 **입력 오류가 아니라 재동결의 사유**다.

**필요한 조치** 못 읽는 포인터는 exit 1이 아니라 `journal`에 «해소 불가 포인터» 목록으로 기록하고 진행한다
(고아 처리와 같은 등급). 설계는 `refreeze.py`를 아예 다루지 않으므로 현재 계획에 없다.

---

### [BLOCKER] H1이 상한만 열고 `_check_residual`을 열지 않는다 — 설계가 주장하는 exit 0이 설계대로는 성립하지 않는다

**막히는 시나리오**
1. A8: 시·군 153 옵션이 잔여로 남는다.
2. 설계대로 `evidence_scope {level: partial, unverified: 153, active: 190, …}`를 적는다.
3. 그래도 `_check_residual`(`check_design_evidence.py:963-975`)이 «잔여 153건»을 그대로 낸다 —
   `evidence_scope`는 이 함수가 보지 않는 값이다. exit 2.
4. exit 0에 도달하려면 여전히 **잔여 단위마다 `interaction_exclusions` 행 1개**(153행)를 손으로 써야 한다.
   각 행은 opaque한 collector target id·action·option을 정확히 재현해야 한다(`_unit_key` 일치).
5. 그리고 `_notices`(`:1017-1027`)가 그 153행을 전부 stderr로 내고, `design-evidence.md:325-329`와
   `commands:144`가 그것을 **G0 배너 1급 항목**으로 올리라고 요구한다. 배너가 153줄이 된다.

**근거**
- 설계 §1의 «exit 의미: 상한 초과 + `evidence_scope` 적법 = exit 0(부분 검증)»은 «상한 초과» 외의 발견이
  없다고 가정한다. 상한은 정의상 예외 행이 이미 153개 있을 때만 걸리므로, 그 153행의 작성 비용은
  설계가 없앤 것이 아니라 **전제로 깔았다**.
- 행 생성 도구는 저장소에 없다(`scripts/` 전수 확인). Coordinator가 직접 쓰는 산출물이다(`commands:9`).

**필요한 조치**
`evidence_scope`를 «상한 해제»가 아니라 **포괄 예외**로 정의한다 — `scope_ref`·`approval_quote` 1건으로
지정된 잔여 집합(예: 특정 target의 전 option)을 통째로 닫고, 개별 행을 요구하지 않는다. 그렇지 않으면
행 생성 보조 도구와 배너 요약 규칙(«예외 N행 — 전문은 design-input.json»)을 함께 설계해야 한다.

---

### [MAJOR] 설계 §4 배선 표에 `refreeze.py`가 없다 — `evidence_scope`가 재동결에서 소실된다

**막히는 시나리오** 부분 검증으로 통과한 빌드를 나중에 재동결한다. `cmd_begin`은 `journal`에
`interaction_exclusions`만 보관한다(`refreeze.py:363-367·383`). `design-input.json`은 폐기되고 staging에서
새로 쓰이므로 `evidence_scope`와 그 `approval_quote`는 사라진다. 재동결 후 staging 게이트에서 다시 상한에
걸리고, 사용자 승인 원문도 journal에 없어 Coordinator가 «무엇이 승인됐었는지»를 복원할 근거가 없다.

**근거** `design-acquisition.md:105-109`는 예외 행의 이월만 규정한다(«새 관찰의 target id 기준으로 다시
짓는다 · 10% 상한은 새 분모로 재검증»). `evidence_scope`는 그 규정의 사각이다.

**필요한 조치** `journal`에 `evidence_scope`를 이월 대상으로 추가하고, `design-acquisition.md`의 이월 문장에
합류시킨다. 설계 §4 표에 `scripts/refreeze.py` 행을 추가한다.

---

### [MAJOR] `evidence_scope`는 최상위 신규 키다 — 설치본/저장소 판형 스큐에서 양방향 즉사

**막히는 시나리오** 사용자의 `/plugin` 설치본이 구판이고 저장소가 신판이거나 그 반대일 때
(메모리 기록상 «설치본 갱신»이 반복 미완 항목이다):
- 신판이 만든 `design-input.json`을 구판 검사기가 읽으면 `check_design_evidence.py:1084-1085`의
  `set(spec) - allowed`가 걸려 **`raise Defects(['design-input.json: invalid top-level fields'])`** —
  다른 발견은 하나도 출력되지 않고 exit 2. 원인 진단이 «최상위 필드가 잘못됐다» 한 줄뿐이다.
- 구판이 만든 빌드는 신판에서도 통과한다(키가 없으면 상한이 그냥 발견이 된다) — 즉 한쪽만 깨진다.

**필요한 조치** 키 추가와 함께 `design-input.json`의 `version`을 2로 올리고, 미지 최상위 키 메시지에
«설치본 판형이 낮을 수 있다»는 진단을 붙인다. 릴리즈 노트에 설치본 갱신 선행을 명시한다.

---

### [MAJOR] 수치 부트스트랩 경로가 없다 — 상한을 넘은 빌드는 `prepare`도 exit 2라 독립 검토를 붙일 수 없다

**막히는 시나리오**
1. `evidence_scope.unverified`·`active`를 쓰려면 검사기가 센 값을 알아야 한다.
2. 그런데 `_check_exclusions`는 `validate_inputs` 안에 있고, `--phase prepare`도 같은 `validate_inputs`를
   지난다(`check_design_evidence.py:1403`). 상한 초과면 `prepare`가 exit 2 → **`review_digest`가 출력되지
   않는다** → `coverage-review.md`의 `reviewed-input`을 만들 수 없다 → `inputs`의 독립 검토 검사(:1245-1254)도
   통과 못 한다.
3. 설계는 `unverified`의 정의(잔여 단위 수인가, 예외 행 수인가, 표면 포함인가)를 적지 않았다.
   정의를 틀리면 «수치 불일치» 발견만 반복된다.

**필요한 조치** ① 상한 초과 메시지에 `unverified`·`active`를 기계 판독 가능한 형태로 싣고,
② `unverified`의 정의를 규범에 한 줄로 고정하며, ③ `prepare`는 `evidence_scope` 부재를 발견으로 내되
`review_digest`는 출력하도록 예외를 둔다(아니면 부트스트랩 순환이 남는다).

---

### [MAJOR] backstop이 `ValueError`를 «내부 오류 exit 1»로 삼킨다 — 발견도 아니고 미실행도 아닌 상태

**막히는 시나리오** `interactions.json`에 `environment_error`가 실린 문서(수동 편집·과거 판형·MCP 경로)가
있으면 `validate_interactions`가 `ValueError`를 던진다(`check_design_evidence.py:995-997`).
`backstop.py:300`의 호출은 `except Defects`만 잡고, 바깥 `except Exception`(`:308-310`)이 받아
«[backstop] design evidence 내부 오류» + **return 1**. `commands:186·191`은 exit 1을 «미실행»으로 규정하므로
마무리는 영구히 완료 보고를 낼 수 없고, 화면에는 traceback만 남는다.
같은 경로에서 `refreeze commit`의 `verified` 단계는 exit 1을 «실패»로 읽어 되감기(`:556-561`)까지 한다.

**필요한 조치** `validate_inputs`의 `ValueError`를 backstop에서 «미실행 사유 1줄»로 분류해 잡는다.

---

### [MAJOR] `design_source is configured but no design build was found` — 빌드 폴더를 지운 프로젝트는 backstop 영구 BLOCKER

**막히는 시나리오** 사용자가 완료된 `.dddjango-web/<빌드>/`를 정리하고 커밋한다. `config.json`의
`design_source`(type=PROJECT)는 남는다. 이후 어떤 실행이든 `backstop.py:281-282`가
«--design-build required» BLOCKER를 낸다. `--design-build`를 줘도 `:294-296`에서 «design build
디렉터리/증거가 없음»으로 같은 BLOCKER다. 문은 `config.json`을 손으로 고치는 것뿐인데, 그 파일은
«Coordinator만 읽고 쓴다»(`commands:44`)이고 이 상황의 편집 절차는 어디에도 없다.

**필요한 조치** 빌드 0개 + config 有 상태를 BLOCKER가 아니라 notice로 내리거나, 해소 절차를 규범에 적는다.

---

### [MAJOR] 재수집 외에 문이 없는 발견들이 그대로 남는다 — 설계가 다루지 않는다

`outside_root.count>0`(#4) · `root.found≠true`(#5) · 수집기 sha(#3) · v2 부재(#2)는 모두
«다시 관찰해라»가 유일한 응답이다. 브라우저·원본이 있는 동안에는 문이지만, 없어지는 순간 벽이 된다.
설계는 이 네 발견 중 어느 것도 `evidence_scope`의 관할에 넣지 않는다.
최소한 «관찰 불가 사유 + 사용자 승인»으로 이 축 전체를 부분 검증으로 강등하는 단일 규칙이 필요하다.

---

### [MAJOR] 부채 defer 래칫이 CSS 한 줄 수정까지 ≤90분 전량 재관찰로 묶는다

`commands:130`: «구현 재진입 = Phase 1 진입·수정 모드 편집·**트리비얼 편집**·coder 호출 — 이때는 ⓐ가
선행돼야 하며 입력 게이트 exit 2가 그대로 막는다». 즉 토큰 값 하나를 고치는 패스트트랙(`commands:220`)도
전체 조작 상태 재수집을 요구한다. 설계 §3은 이 래칫을 명시적으로 건드리지 않기로 했고, 그 근거는
위 첫 BLOCKER에서 보였듯 성립하지 않는다.

**필요한 조치** 부분 상환(변경 영향 화면만 재관찰) 또는 «비화면 변경은 래칫 밖»의 경계를 규범에 둔다.

---

### [MAJOR] 예외 153행이 G0 배너 1급 줄 153개가 된다 — 게이트가 결정 자료로서 무너진다

`_notices`(`check_design_evidence.py:1017-1027`)는 예외 **전 행**을 stderr로 내고,
`design-evidence.md:325-329`·`commands:144`가 그것을 배너 1급 항목으로 요구한다.
H1이 상한을 열면 이 출력이 수백 줄까지 자란다. 설계 §1-3의 «G 배너 1급 줄»은 `evidence_level` 한 줄만
가정하고 있으나, 기존 규칙과 합치면 «1급 항목»의 의미가 사라진다.
배너 요약 규칙(«예외 N행 · 부분 검증 unverified/active · 전문은 파일 참조»)을 같은 수리에서 함께 바꿔야 한다.

---

### [MINOR] `journal`/`swap-plan` 손상 조합에서 `refreeze` 네 서브커맨드가 모두 exit 1

`_prev-*`는 있는데 `swap-plan.json`이 없고 staging도 사라진 상태에서 `commit --resume`은
`load_json(prev/PLAN)` OSError로 exit 1, `abort`는 `_rewind`가 같은 파일을 읽어 exit 1, `begin`은
«진행 중인 재동결이 있다»로 exit 2. 그동안 `backstop.py:286-293`이 프로젝트 전역 BLOCKER를 낸다.
문은 수동 `rm`뿐이고 규범에 없다. `abort`가 PLAN 부재를 허용하도록 고치면 닫힌다.

### [MINOR] `archive_files`의 4096 파일 상한에 승인 문이 없다

`archive_design.py:35-36`. 큰 디자인 export를 가진 프로젝트는 시작 자체가 불가하고, 사용자가 사실을 알아도
여는 값이 없다. 상한을 인자로 빼거나 초과분을 «미수집 선언»으로 기록할 길이 필요하다.

### [MINOR] `implementation_digest`의 `web/` 필수가 비시안 실행에서 BLOCKER가 된다

`check_design_evidence.py:1260-1263`. 설계 단계 빌드만 있는 프로젝트에서 `--design-build` 없이 backstop을
돌리면(비시안 트리비얼 등) `web/` 부재로 BLOCKER. `current_nondesign_scope`의 생략 조건은 모든 빌드가
완료 상태일 것을 요구하므로 여기서는 발동하지 않는다.

### [MINOR] `visual-evidence.json`에 «승인된 이탈»을 적을 칸이 없다

`check_design_evidence.py:1328-1329`는 `result: "pass"`만 받는다. `commands:187`은 «명세가 의도한 이탈·데이터
콘텐츠 차이는 사용자가 수락할 수 있다»고 하는데, 그 수락을 증거 JSON이 표현하지 못해 `pass`로 눌러 적게 된다.
이번 설계의 «비용을 기록하는 장치» 원칙과 같은 결의 결함이다.

### [MINOR] 진행 중 설계 빌드가 같은 프로젝트의 다른 실행을 막는다

`backstop.py:294`에서 `--design-build` 없이 돌면 `builds = discovered` 전량이 visual 검사를 받는다.
아직 `visual-evidence.json`이 없는 설계 단계 빌드가 하나라도 있으면 BLOCKER다.

### [MINOR] `_active_targets` 분모가 검사 진행 상태에 의존한다 — `evidence_scope.active`가 흔들린다

`_active_targets`(`:840-846`)는 그 실행에서 실제로 수집된 `digest_items`만 센다. case의 포인터가 하나라도
해소되지 않으면 그 문서의 identity가 분모에서 빠진다. 즉 **실패 라운드와 성공 라운드의 `active`가 다르다.**
설계의 «수치 일치» 요구는 이 값을 고정값처럼 다루는데, 실제로는 다른 발견을 고칠 때마다 바뀐다.
분모를 `design-input.json`이 선언한 문서 집합으로 고정하지 않으면 수치 맞추기가 반복 왕복이 된다.

---

## 요약 판정

설계는 진단이 지목한 벽(#1) 하나를 정확히 겨눴고 그 지점의 처방(지위 강등 + 사용자 원문 + 영구 기록)은 옳다.
그러나 «어떤 이유로든 불가능해지면 안 된다»를 기준으로 하면 **17개의 실질 하드월 중 1개만 열린다.**
남는 것 중 6개는 사용자 지시 문장(«재동결하라», «고치게 하라») 그 자체를 불가능하게 만드는 경로이며,
그중 셋(`refreeze` REQUIRED_STAGING · render-audit enum · `begin`의 증거 읽기)은 설계가 다루기로 한
파일 목록(§4)에 `refreeze.py`가 아예 없어 이번 수리로는 손도 닿지 않는다.

<!-- 도구 사용: 워크트리 루트에 `.serena/project.yml`·`graphify-out/graph.json`이 없어 Serena·Graphify 미사용(기본 검색·읽기 도구로 전수 확인). -->
