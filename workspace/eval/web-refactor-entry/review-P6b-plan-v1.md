판정: 수정 후 승인 — blocker 0 · major 7 · minor 16 — 설계는 빠짐없이 옮겨졌고 러너 계획은 실물에서 선다(원형 55/55·현장 키 무증가). 다만 진입 준비 번호 충돌로 산출물 커밋이 빠졌고, 리팩토링 build-state 에 디자인 플래그가 없어 현장 G2 백스톱이 막힌다(합성 실측). 「명세 슬라이스 0 절 파일」·plan 재계산 대조는 수단이 정의되지 않았고, 결정 출처 문장이 빠졌으며, Codex 플랫폼 자동 판별이 설치본 경로에서 틀리고, ④ 는 미커밋 변경을 보지 못한다

# 계획 리뷰 P6b — 로드맵 6b «dddjango-web 리팩토링 입구» 구현 계획 v1 (2026-09-27)

- 대상: `plan-v1.md`(이하 `P:행`) · 설계 정본 `design-v5.md`(이하 `D5:행`) · 앞 검토 X1~X4.
- 실물(HEAD `c9fcadff`): `dddjango-web/commands/dddjango-web.md`(`W:행`) · Codex `codex-dddjango-web/skills/dddjango-web/SKILL.md`(`CX:행`) · `scripts/backstop.py`(`BS:행`) · `scripts/src/debt.py`(`DB:행`) · `common.py`(`CM:행`) · `check_structure.py`(`ST:행`) · `check_purity.py`(`PU:행`) · `check_design_evidence.py` · 에이전트 4 · dddjango 선례(`dddjango/commands/dddjango.md` · `refactor.md` · `scripts/refactor_audit.py` · `codex-dddjango/skills/dddjango-refactor/`).
- Serena·Graphify 는 쓰지 않았다. 모델 하네스도 부르지 않았고 현장 테스트 suite 도 돌리지 않았다.

## §0 확인 실행 기록

scratch 는 `…/scratchpad/6b-review-P/` 하나만 썼다. 현장 원본에는 읽기(`git rev-parse`·`sed`·`git grep`)와 `git clone --shared` 만 했다.

| # | 실행 | 결과 |
|---|---|---|
| 0 | 리뷰 전 `git status --short` | 시작 스냅숏과 같다. M 5(`docs/master.html` · 조감도 · field-report-4 · progress · synthesis-v2) · ?? 2(`workspace/eval/web-refactor-entry/` · refactor-campaign) |
| 1 | `bash dddjango-web/scripts/test/fixtures_debt.sh`(저장소 원본) | `PASS=55 FAIL=0` [실측] |
| 2 | 원형 `proto/scripts`(저장소 scripts 복사본). 계획 §4 를 그대로 넣었다: `_ROW_RE` 여섯 이름 · `scan(root, refactor)` 가 `_skeleton(ctx)` 발견 추가 · `_WS5_NO_BASE` notice 떨굼 · JSON `mode` · `_exempt` WP1 조건부(«메시지 `<WP2 사유> — p` 인 WP2 발견이 없으면 WP1 면제 안 함») · `cli_residual` 이 `mode` 추종. 이 상태로 `fixtures_debt.sh` 실행 | `PASS=55 FAIL=0` — M 행 확장과 `mode` 필드가 6a 55 를 깨지 않는다 [실측] |
| 3 | 합성 `e2`: legacy core `static/js/htmx.min.js` + defer 없는 base 태그 + 골격 미비 단위 3개. 원형 `scan(refactor=True)` 실행 | 키 `WS5|`(누락에 `static/htmx/` 포함) · `WS5|home/` · `WS5|home/home/` · `WS5|client/orders/` · notice 0 · WP1·WP2 쌍 면제 유지. 태그에 `defer` 를 붙이면 `WP1|static/js/htmx.min.js` 가 더해진다. feature 스캔은 WN6 1키로 무변 [실측]. `from_files` 는 `gated=False` 라 `is_added_dir` 가 늘 참이다(`CM:352-355`) |
| 4 | 현장 `--shared` 사본 `sds`(`3dd440224`)에서 원형 feature·refactor 스캔 | 둘 다 `WN8|static/images/{chunmong-logo-v2,cloud-ornament,gold-blossom}.png` 3키 — 해제로 늘어나는 키 0(설계 §4-1 주장 성립) [실측] |
| 5 | 사본 `sds` 에서 6a 참조 완전성 pathspec 으로 이미지 3 꼬리를 grep | `tests/test_settings_profiles.py:131·148` · `login.html:18·23·25` · `special_button.html:12·14` — W6-T0 기대와 같다 [실측] |
| 6 | 합성 `e3` 에서 `git grep -n -w -F -e web.a.q -- web '*.py' …`(git 2.54) | `web.a.q2` 만 있는 줄은 빠진다. 같은 줄 뒤쪽의 `web.a.q` 는 잡힌다. pathspec 이 `tests/*.py` 도 잡는다 [실측] |
| 7 | 합성 `e1`: 과거 시안 빌드 1 + `config.json` `design_source.type=PROJECT` + 리팩토링 build-state(`mode: refactor` · `git_snapshot`) + 슬라이스 0 커밋 1. 이어서 `backstop.py . --diff-base <snap>` | build-state 에 디자인 플래그 없음 = `[DESIGN] BLOCKER … design-input.json: invalid top-level fields` · blocker 1. `has_design_screen: false` 를 더하면 «git_snapshot이 일치하는 현재 비시안 작업 — 과거 시안 빌드 1개의 visual 검사 생략» · blocker 0 [실측] |
| 8 | 같은 `e1` 리팩토링 폴더에서 `check_design_evidence.py --phase identity` | `{"component_identity": "ok"}` exit 0 — 재개 입구 step 4 는 리팩토링 폴더에서 무해하다 [실측] |
| 9 | `ls ~/.codex/plugins/cache/changja88-dddjango/dddjango-web/` 와 `find` | Codex 설치본 = `…/dddjango-web/1.1.25/skills/dddjango-web/scripts/backstop.py` — 경로에 `codex-dddjango-web` 성분이 없다 [실측] |
| 10 | 현장 읽기: `.dddjango-web/` 목록 · `config.json` · `Makefile:48-50` · `tests/web/intake/test_user_info_employee_gate.py:85-105` · `web/` 상대 import 수 | 빌드 폴더 17 · `design_source` PROJECT · `testp` = `-rF … --maxfail=1` 두 단계 · `:97` `reverse` 뒤 `:98` 지역 import · 상대 import 0 / `from web.` 254 [실측] |
| 11 | 리뷰 뒤 `git status --short` | 이 파일 1개만 새로 생겼다. 새 파일은 이미 미추적인 `workspace/eval/web-refactor-entry/` 안에 있어 목록 모양은 0번과 같다. 무시된 `dddjango-web/scripts/__pycache__/` 는 원래 있던 것이다 |

## §1 커버리지 표 (설계 v5 → 계획 v1)

| 설계 항목 | 계획 위치 | 판정 |
|---|---|---|
| §1-1 disable 제거 · `refactor.md` · `요청 원문:` 1행 · 문면 작성 규칙 | §1(P:21-27) | 옮김 |
| §1-1 양끝 짝 따옴표 제거 | §2-2(P:40) | 옮김 |
| §1-1 **결정 출처와의 관계**(`D5:43`) | — | **누락 → M5** |
| §1-1 호출 정책 기록(W6-T12 관찰만) | §11-10 | 옮김 |
| §1-2 Codex 얇은 스킬 · openai.yaml · 요청 첫 줄 판별 | §1 Codex(P:28-31) | 옮김 |
| §2-1 판별 입력 둘 · 표지 손상 · 단조성 · 따르지 않는 지시 · `<대상>` 표기 | §2-2 · §2-3 · §3-1 | 옮김. 단조성 문장의 뒤 절반이 빠짐 → m8 |
| §2-2 흐름 · step 3·5 생략 · 배선 미적용 · `:212` (가) 없음 · 수정 전 렌더 | §3-1 · §3-14 · §3-16 | 옮김. step 5 생략이 build-state 에 주는 결과가 없음 → **M2** |
| §2-3 R0 · R0′ · 초기화 8필드 · 끝남 · 잇기 · 끊김 · 표지 없는 잇기 | §3-2 · §3-3 | 옮김(초기화에 디자인 플래그 없음 → M2) |
| §2-3 G0 정지 재개 조건 1~4 · 재사용 거부 | §3-4 · §10 | 조건 4 를 결정적으로 볼 수단이 없음 → **M4** |
| §3-1 범위 파일 · 판정 순서 · 이중 범위 · 이름 전속 없음 | §3-5 · §5 plan | 옮김 |
| §3-2 키 소속 1~4 · 키 전체 편입 | §3-5 · §5 plan | 옮김 |
| §3-3 경계 교차 소비자 · (가)(나)(다) · `plan --names` · DR 대조 1항 | §3-6 · §5 · §6 DR | 옮김. 입력 파일이 미정 → **M3**. web/ 아래 필터 명시 → m2 |
| §3-4 스캔 단위 · `:193` 리팩토링 판 · 범위 밖 미룰 수 없음 1행 | §3-7 | 옮김. 설계 반송 재진입 → m11 |
| §4-1 `--refactor`(WS5 · WP1 조건부 · WP2·WP5 유지) · `mode` · 배타 · residual 추종 · 스캔 기록 | §4 · §3-8 · §10 D24~27 | 옮김. 원형 실측 55/55(§0-2·3) |
| §4-2 렌즈 2 · 점검 절 · 조각 · 파견 입력 · 산출 표 8열 · 에이전트 절 | §3-9 · §5 상수 · §6 | 옮김 |
| §4-3 R2′ 재인용 · R3 판정 모드 · architect 경계 예외 · 판정 범주 | §3-10 · §5 · §6 | 옮김 |
| §4-4 별도 요청 4유형 · 기계 근거 · import 줄 불성립 | §3-11 · §5 | 옮김 |
| §5-1 · §5-2 도구 갈래(B) · 하위 명령 · 공통 · 식별자 · self-test 자리 | §5 | 옮김. 플랫폼 판별 → **M6** · self-test 범위 → m7 |
| §5-3 출구 5 · 긍정 술어 · 부정형 · 무효 접미 `면` · 제외 ⑤ 괄호 예외 · 대리 축소 | §5 · §7 | 옮김 |
| §6 M 행 3 · 6a 행 항상 · 파서 한 곳 · residual 필수 조건 · 배너 · 정리 0 정지 | §3-13 · §4 M 행 · §10 D28 | 옮김. 값 검사 시점 → m5 |
| §7-1 Phase 1 흐름 · 명세 정형 행 `경로:`·`이름:` | §3-15 · §6 architect | 옮김 |
| §7-1 진입 준비 기준선(«6a ①~⑥ · ②②′③ 없음») | §2-7 · §3-16 | **번호 충돌 · 산출물 커밋 ⑤ 누락 → M1** |
| §7-1 끝 green ①~⑤ · ⑤ 실행 규칙 · 재확인 · 6a 재기준선 · G2 직전 ④ · `--except` | §2-8~§2-12 · §3-16 | 옮김. ④ 가 작업 트리를 보지 않음 → **M7** · 도구 시간 제한 → m10 |
| §7-2 coder 예외 · 테스트 판정 · CLI · 경로·폴더·이름 쌍 · 바인딩 대조 · 줄 다중집합 | §4 · §6 coder · §10 subst | 옮김. 파일 상태 → m3 · 위치 키 → m4 · 점 경로 → m2 |
| §7-3 a~e · 잠복 모순 정정 메모 | §2-4 · §2-6 · §2-8~§2-10 · §6 · §8 | 옮김 |
| §7-4 결정 17 번복 · 사용자 보고 1줄 | §8 REQUEST_GUIDE | 부분 — 보고 단계 없음 → m13 |
| §8 M_c · M_m · 재개봉 · 재상정 · G2 배너 | §2-11 · §3-17 · §5 residual | 옮김 |
| §9 Override ⑴⑵ · 끝 문장 · 어구 목록 · `:191` · 에이전트 1행 · 전수 분류 | §3-12 · §6 · §7 | 옮김. 사본 전수 grep 빠짐 → m13 |
| §10 문면 갱신 표 1~12 · + 행 | §2 · §6 · §8 · §9 | 옮김. 5행(houserules `:15`·`:217` 무변 확인) 빠짐 → m13 |
| §11 W6-T0~T14 · W6-C · 비용 | §10 · §11 | 옮김. T10 비용 · T13 좁힘 · G2 실하네스 0 → m12 |
| **부록 D X4 M1** 6a 재개봉 재기준선 | §2-8(재기준선 파일) · §2-11 · §11(T14) | 옮김 |
| **X4 M2** (나) 옛 모듈 적중 파일 한정 · `-w` · 호출 줄 치환 · `plan --names` · `경로:` 정형 행 | §3-6 · §5 `--names` · §6 architect `:55` · §10 · §11-4 | 옮김(입력 파일 미정 → M3) |
| **X4 m1** 원문 `-r` 떼고 `-rfE` 끝 | §2-8 | 옮김 |
| **X4 m2** 기준선 통과 0 = 판정 불가 | §2-8 | 옮김 |
| **X4 m3** 비용(1회 약 19분 · 최소 38분) | §11(6분 × 가지) | 부분 — 사용자 보고 문장 없음 → m13 |
| **X4 m4** `:212` (가) × ④ · `--except` | §2-9 · §2-10 · §3-14 · §4 · §10 subst | 옮김 |
| **X4 m5** 조건절 `면` · cleancode 서술문 5개 적용 여부 | §5 무효 접미 · §7 | 옮김 |
| **X4 m6** 속성 이름 = 키 불성립 | §5 check-verdict | 옮김 |
| **X4 m7** 접두 쌍 성분 경계 | §4 · §10 subst | 옮김 |
| X4 (덧) `의 예외` 항 중복 정리 · render 지역 이름 | §5(설계 참조) · 무변 | 옮김 |

부록 A 대응표는 대체로 맞다. 두 곳만 고친다: §7-1 행에 §3-15(Phase 1)가 빠졌다. §1 행에는 §1-1 결정 출처 문장이 갈 계획 위치가 없다(M5 로 새 행).

## §2 지적

### major

**M1. Phase 2 진입 준비의 새 단계가 기존 «⑤ 산출물 커밋»과 번호가 겹친다. 그래서 리팩토링 모드 목록에서 커밋이 빠졌다.** [실측 문면]
- 근거
  - `W:200` 진입 준비의 ⑤ 는 `.dddjango-web/` 산출물 커밋이고 ⑥ 은 `git_snapshot` 이다. `W:156`(`CX:178`)은 «Coordinator 기록물의 커밋 시점은 Phase 2 진입 준비 ⑤뿐»이라고 이 번호를 가리킨다.
  - 계획 2-7(P:45)은 ④ 직후에 «**⑤** 기존 테스트 기준선 캡처»를 넣는다. 이러면 한 목록에 ⑤ 가 둘이 된다.
  - 계획 §3-16(P:74)은 리팩토링 진입 준비를 «① · ④ · ⑤ 기준선 · ⑥» 으로 적어 커밋 ⑤ 가 없다.
  - 설계 §7-1(`D5:282`)은 «6a ① ~ ⑥ · 리팩토링 모드는 ②·②′·③ 없음»이라 리팩토링에도 커밋 ⑤ 가 있다. 계획이 설계를 잘못 옮긴 것이다.
  - 커밋 ⑤ 의 add 목록과 «네가 직접 쓰는 것»(2-13)에 `test-baseline*.txt`(두 모드)와 `audit/`·`plan-names.md`(리팩토링)가 없다.
- 영향: 끝 절대로 구현하면 리팩토링 실행이 산출물을 커밋하지 않고 `git_snapshot` 을 잡는다. `refactor-scope.md`·`debt-g0.json`·audit 이 미추적으로 남고, `:156` 의 «⑤» 가 무엇을 가리키는지 모호해진다.
- 고칠 곳과 고칠 말
  - 2-7(P:45): «④ 직후 **④′ 기존 테스트 기준선**(슬라이스 0 이 있을 때 — ②′ 판형 번호)».
  - §3-16(P:74): «진입 준비 ① · ④ · ④′ · ⑤(산출물 커밋) · ⑥».
  - 2-13(P:51)과 `W:200` ⑤ 의 add 목록에 «`test-baseline*.txt`(두 모드) · 리팩토링은 `audit/` · `plan-names.md`» 1구.
  - 끝 green 의 ①~⑤ 는 문면에서 «끝 green ⑤»처럼 한정어를 붙여 진입 준비 번호와 구별한다.

**M2. 리팩토링 build-state 에 디자인 플래그를 쓰는 지점이 없다. 그러면 G2 백스톱이 과거 시안 빌드를 판정 입력으로 삼아 현장에서 막힌다.** [실측 합성 §0-7 · 현장 설정 §0-10]
- 근거
  - `BS:239-255` 는 `--design-build` 없이 돌면 `current_nondesign_scope`(`BS:102-127`)가 참일 때만 과거 빌드를 뺀다. 그 조건은 현재 폴더 build-state 의 `has_design_screen is False`(명시적 false)다.
  - 디자인 플래그는 «디자인 해소 후»(`W:86`), 곧 step 5 뒤에 쓴다. 리팩토링은 step 5 를 생략한다(`D5:71`).
  - 계획 §3-3 의 새 점검 초기화 8필드(P:61)에도 디자인 플래그가 없다.
  - `implementation_digest` 는 `web/` 전체 바이트의 digest 다(`check_design_evidence.py:430-449`). 그래서 슬라이스 0 이 web/ 을 바꾸면 과거 빌드의 visual 증거가 곧바로 낡는다.
  - 현장에는 `design_source.type=PROJECT` 와 빌드 폴더 17개가 있다.
  - 합성 `e1` 실측: 플래그가 없으면 `[DESIGN] BLOCKER` exit 2 이고, `has_design_screen: false` 를 두면 «비시안 작업 — 생략» blocker 0 이다.
- 영향: 리팩토링 G2 의 결정적 백스톱이 늘 blocker 가 되어 반송이 되풀이된다. 계획의 행동 시험 중 리팩토링 모드로 G2 까지 가는 실하네스가 없어서(m12) 착륙 전에 드러나지 않는다.
- 고칠 곳과 고칠 말
  - §3-3(P:61): «R0′ 에서 build-state 를 만들거나 새 점검으로 초기화할 때 `mode: refactor` 와 함께 `has_design_screen: false` · `has_design_tokens: false` · `has_design_images: false` · `has_motion_notes: false` · `has_render_audit: false` · `design_status: none` 을 쓴다(step 5 생략 — G2 백스톱의 비시안 식별 입력)».
  - 2-1(P:39) 갱신 시점에 «리팩토링은 생성 시 디자인 플래그 false» 1구.
  - 러너는 무변이다(기존 계약을 쓴다). 확인은 m12 (d) 의 G2 실하네스 1회로 한다.

**M3. «명세 슬라이스 0 절 파일»이 무엇인지, 누가 만드는지 정의되지 않았다. 이것이 ④ `--subst-check --names` 와 `plan --names` 의 입력이다.** [실측 문면]
- 근거
  - 계획 2-8(P:46)·§3-7·§5(P:114 «`--names <명세 파일>`»)과 설계 `D5:141·226·288` 이 모두 이 말만 쓴다.
  - 명세는 `design-spec.md` 한 파일이다(`W:37`). architect 의 슬라이스 0 절에는 고정된 머리가 없다(`design-architect-web.md:55` «**슬라이스 0 절**»).
  - `parse_spec_pairs` 는 «형식 어긋남은 `DebtError`»다(P:94).
  - 현장 명세는 1,400행대 자유 서술이다(`20260925-1759-room-open-signal/design-spec.md`).
- 영향: 명세 전체를 넘기면 슬라이스 0 밖 줄의 `경로:`·`이름:` 모양을 쌍으로 잘못 읽거나, 형식 어긋남 exit 1 로 끝 green ④ 가 영영 서지 않는다. Coordinator 가 발췌 파일을 만들면 «직접 쓰는 것» 밖의 새 산출물이 되고, 발췌에서 빠진 쌍이 (나) 계산을 조용히 줄인다.
- 고칠 곳과 고칠 말
  - §4(P:94)와 §5(P:114): «`--names <design-spec.md>` — 파서는 머리 `## 슬라이스 0` 절 안의 정형 행만 읽는다. 절 밖은 무시한다. 절 안의 형식 어긋남 · 머리 0개(쌍을 요구할 때)·2개 이상은 `DebtError`». 머리 문자열은 `debt.py` 상수로 둔다.
  - §6 architect `:55`(P:139): «슬라이스 0 절은 머리 `## 슬라이스 0` 로 쓴다» 1구.
  - `--self-test` 에 이 머리 문자열과 architect 문면의 대조를 더한다.
  - 픽스처는 두 명령 공통 3건이다: 절 밖 `이름:` 무시 · 절 안 어긋남 exit 1 · 머리 중복 exit 1.

**M4. G0 정지 재개의 조건 4(«`plan` 을 다시 돌린 결과 = 그 audit `plan.md`», `D5:89`)를 결정적으로 볼 수단이 계획에 없다.** [실측 코드 · 추정 결과]
- 근거
  - §3-4(P:62)와 §10(P:174 «네 갈래의 `plan` 재계산 대조»)는 대조를 전제한다. 그런데 §5 `plan` 계약(P:113)에는 `--out <audit>` 뿐이고 대조 출구가 없다.
  - 계획은 «모양은 dddjango 를 따른다»(P:110)고 한다. dddjango `cmd_plan` 은 `plan.md` 를 그대로 덮어쓴다(`dddjango/scripts/refactor_audit.py:612`).
- 영향
  - 같은 `--out` 으로 다시 돌리면 비교 대상이 지워져 조건 4 가 늘 참이 된다. 낡은 verdict 가 재사용되는 fail-open 이다.
  - 새 폴더로 돌려 파일째 비교하면 이번에는 반대로 샌다. `plan.md` 에는 `HEAD`·`범위 미커밋 변경 N` 이 들어 있어서, 조건 2 가 허용한 HEAD 차이에서도 불일치가 난다.
- 고칠 곳과 고칠 말(§5 P:113 에 1항, 새 장치 없이 기존 하위 명령의 플래그로)
  - «`plan <단위> --debt <json> --against <그 audit>/plan.md`: 계산만 하고 쓰지 않는다. 설계 §2-3 조건 4 의 여섯 목록만 대조한다. exit 0 같음 · 2 다름(다른 목록 이름 출력) · 1 실행 불능.»
  - «`--out` 에 `plan.md` 가 이미 있으면 exit 1(덮지 않는다).»
  - §3-4 문면은 «`plan --against` exit 0» 으로 쓴다. 네 갈래 픽스처도 이 출구로 한다.

**M5. 설계 §1-1 «결정 출처와의 관계» 문장이 계획 어디에도 없다.** [실측 문면]
- 근거
  - `D5:43` 은 «D1 뒤에는 모델이 조립한 args 도 `요청 원문:` 줄에 보인다. 이 줄은 «결정 출처 — 본인 직접»의 근거가 아니다(`:152` 와 맞춤)»라고 쓴다.
  - 계획에서 «결정 출처|본인 직접|:152» 를 grep 하면 P:62(재사용 거부) 1건뿐이다.
  - 현행 `W:152`(`CX:174`)는 «대화형 세션에서 사용자가 직접 입력한 요청문에 적은 미룸 포함»을 본인 직접으로 받는다.
- 영향: D1(`W:5` 제거)로 모델이 Coordinator 를 스스로 부를 수 있게 된다. 그 args 에 적힌 미룸이 두 모드 모두에서 출처 없는 ⓑ 인데도 «본인 직접»으로 읽힐 수 있다. 계획이 스스로 여는 구멍을 설계가 닫아 둔 문장이다.
- 고칠 곳과 고칠 말
  - §2 표에 새 행 «2-14 | `:152`(Codex `:174`) 결정 출처 | «본인 직접» 괄호 끝에 «— `요청 원문:` 줄(Codex 는 요청 첫 줄)은 모델이 조립한 args 도 담으므로 그 줄만으로는 본인 직접이 아니다(이 실행의 대화에서 사용자가 직접 입력한 문장만)» 1구».
  - 부록 A 에 §1-1 → 2-14 행을 둔다.

**M6. `refactor_audit.py` 의 Codex 자동 판별 규칙 «`…/codex-dddjango-web/…` 아래면 codex»(P:111)가 설치본에서 틀린다.** [실측 §0-9]
- 근거
  - Codex 설치본 경로는 `~/.codex/plugins/cache/changja88-dddjango/dddjango-web/1.1.25/skills/dddjango-web/scripts/` 이다. W6-C 의 사본 경로(`.agents/skills/…`)에도 `codex-dddjango-web` 성분은 없다.
  - 두 Coordinator 는 `--platform` 을 넘기지 않는다(dddjango `dddjango.md:233-247` · Codex `:249-263` 판형).
  - Makefile self-test 2행(P:161)은 `--platform` 을 명시한다. 그래서 자동 판별 경로는 `verify-web` 에서 한 번도 돌지 않는다.
- 영향: Codex 실행의 `plan`·`check` 가 Claude 경로 사상으로 문서를 찾는다. 인용이 전부 불일치가 되거나 실행 불능이 된다. W6-C 합격선(R2 파견 또는 G0)은 `check` 앞일 수 있어 이 결함을 놓칠 수 있다.
- 고칠 곳과 고칠 말
  - §5 공통(P:111): «기본 판별은 구조로 한다(dddjango `refactor_audit.py:310-319` 판형). `scripts/../commands/dddjango-web.md` 가 있으면 claude, `scripts/../SKILL.md` 가 있으면 codex. 루트는 경로 사상 표에 맞춘다. 둘 다 없으면 exit 1».
  - §9(P:161): `--platform` 없는 self-test 를 트리마다 1행 더하거나, self-test 가 «자동 판별 = 주어진 플랫폼»을 red 조건으로 본다.

**M7. ④ `--subst-check` 가 커밋 범위(`git diff --name-only <base>..<target>` · `git show <rev>:<path>`, P:98·P:100)만 본다. 미커밋 web/ 밖 편집은 보지 못하는데, ⑤ 는 작업 트리에서 돈다.** [실측 코드 · 추정 경로]
- 근거
  - 슬라이스 커밋에 어떤 경로를 넣는지는 Coordinator 문면에 없다(`W:209` «green으로 끝날 때마다 커밋»).
  - 기존 `--diff-base` 는 작업 트리의 미커밋 추적 변경과 미추적 파일을 본다(`CM:432-477`).
  - 설계는 ④ 의 몫을 «테스트를 «고쳐서» ⑤ 를 통과시키는 단언 변경을 잡는다»로 둔다(`D5:303`).
- 실패 모양: 명세 목록 밖 테스트 파일의 단언을 고친 편집이 경로 명시 커밋에서 빠져 작업 트리에 남는다. 그러면 ④ 는 그 파일을 못 봐서 exit 0 이고, ⑤ 는 고친 단언으로 통과한다. Phase 3 soft-reset 이 그 편집을 사용자 스테이징에 섞는다.
- 고칠 곳과 고칠 말
  - §4 `--subst-check`(P:98 뒤): «web/ 밖(`.dddjango-web/` 제외)에 미커밋 변경(추적 파일 수정 · 미추적 비무시 파일)이 있으면 exit 1 «미커밋 web/ 밖 변경 — 커밋 뒤 다시»(경로 출력)».
  - 2-8(P:46) ④ 문면: «슬라이스 0 커밋 뒤».
  - §10 subst 픽스처: «미커밋 테스트 단언 변경 → exit 1».
  - ⑤ 실행 산출물이 무시되지 않는 프로젝트라면 exit 1 로 멈추고 경로를 보고한다(fail-closed).
  - 대안은 «대상 `HEAD` 는 작업 트리까지 본다»(`--diff-base` 와 같은 의미론)다. 다만 exit 1 가드가 더 작다.

### minor

- **m1. 행 번호** [실측]
  - `debt.py:138-140`(P:84)은 key·rows 조립이다. 6a WS5 notice 재작성은 `DB:129-132` 다.
  - build-state `mode` 는 `W:62` 이다(`:61` 은 `phase`). Codex 는 `CX:115` 다.
- **m2. 점 경로와 (나) 필터**
  - `tail_of` 의 `.py` 점 경로를 `web.` 을 붙인 전체 모듈 경로로 정한다. 바인딩 역치환은 «`N` 과 같거나 `N.` 으로 시작»(P:100)이라, web 상대(`home.x`)로 두면 `web.home.x` 바인딩이 걸리지 않아 거짓 red 가 난다.
  - `plan --names` 의 (나) 결과는 **web/ 아래 줄만**이라고 §5(P:114)에 적는다. 참조 완전성 pathspec 은 저장소 전체 `.py` 를 잡는다(§0-6 `tests/…` 적중).
- **m3. `--subst-check` 의 파일 상태**
  - A(새 테스트 파일) · D(삭제) · R(테스트 파일 개명) · 타입 변경은 치환이 아니므로 exit 2 로 가른다.
  - `--name-only` 에 한쪽 `git show` 가 실패하는 경우를 «커밋 부재 exit 1»로 떨어뜨리지 않는다. `--name-status --no-renames` 로 상태를 본다.
  - 이진 파일(테스트 fixture 이미지 등)은 byte 가 같을 때만 green 이다.
  - 픽스처 3건을 더한다.
- **m4. import 구간 키에 위치를 넣는다**(블록 안에서 그 구간 앞에 있는 비-import 문 수). 블록별 합집합으로 구현하면 같은 함수 안에서 문장을 건너 옮긴 import 가 green 이다. 현장 `test_user_info_employee_gate.py:97-98`(`reverse` 뒤 지역 import — 순서에 뜻이 있다)이 바로 그 모양이다. 픽스처 «같은 블록 안 문장 건너 이동 red»를 더한다. [추정 — 계획 문면 «블록별 연속 import 구간 바인딩 다중집합»(P:100)이 두 구현을 다 허용한다]
- **m5. M 행 값 검사는 접는 절(마지막 `## G0` 부터)에서만 한다.** 6a 는 옛 절을 판정 입력으로 쓰지 않는다. `parse_scope` 가 즉시 검사하면 재사용 폴더의 옛 절 모양이 새 요청을 막는다. 또 `## G0 재승인` 절의 `의미 ⓐ 키:` 는 0행 또는 1행(없으면 새 M 0)이라고 `residual_m_sets`(P:92) 계약에 적는다. 원형으로 55/55 는 확인했다(§0-2).
- **m6.** D27(P:171)에 `--refactor --debt-residual` → exit 1 을 1사례 더한다. «모드는 `debt-g0.json` 이 정한다»는 계약의 짝이다.
- **m7. self-test 대조 범위를 정리한다.**
  - 계획의 길이 관리(P:77)는 술어 목록을 문면에 두지 않는다. 그런데 설계 드리프트 문장(`D5:370`)은 «어구·술어·부정형 상수 = 규범 문면»이다.
  - 문면에 싣는 것은 어구 목록뿐이다. 그러니 §5 self-test(P:118)를 «어구 상수 ↔ 끝 절 «…» · 술어·부정형은 극성 표본»으로 적는다.
  - 같은 자리에서 참조 완전성 pathspec 상수와 Coordinator 문면을 대조한다(P:95 «같은 문자열 상수»의 기계 확인).
- **m8. 단조성 문면**
  - 2-2(P:40)에 설계 §2-1 문장의 뒤 절반을 싣는다: «G0 의무를 전부 수행하고 R2·R3 를 더한다» · «정하지 않은 사항은 앞 절 그대로».
  - §3-1(P:59) «끝 절이 앞 절을 바꾸는 곳»은 닫힌 목록으로 읽히지 않게 «대표적으로»를 붙인다. ⓐ′ · 폴더 후보 · G0/G2 배너 · 정리 0 정지 · step 3·5 · 진입 준비 ②②′③ · `:191` 도 끝 절이 바꾼다.
  - `W:206` «잔여 범주 귀속(…슬라이스 0이 아니다)»과 슬라이스 도출 임계는 리팩토링 모드에 쓰지 않는다는 1구를 둔다. 대상이 `web/base`·`web/design_system`·컨테이너면 이 문면과 부딪힌다.
- **m9. WS5 컨테이너 키와 legacy 쌍 유지가 겹친다**(§0-3 실측 · 현장 0).
  - 쌍을 유지할 때 `WS5|` 누락 목록에 `static/htmx/` 가 든다. 표준 core 를 설치하면 core 중복(WP1)이 되고, core 이동은 쌍 규칙이 막는다.
  - 그래서 같은 키에 묶인 나머지 누락(`static/css/` 등)까지 재상정으로 간다(fail-closed).
  - D24/D25 에 이 조합 1사례를 두고 기대를 «`WS5|` 키 있음 · G0 에서 동작 불변 불가 사유 표시»로 고정한다. 새 장치는 없다.
- **m10. ⑤ 실행 규칙에 도구 시간 제한 1구**(2-8 P:46). 현장 postgres 단계는 788초다(X4 실측). Claude Bash 도구의 최대 제한은 600초다. «단계 명령은 백그라운드로 돌려 완료를 기다리고, 시간 제한으로 끊긴 단계는 판정 불가» — Codex 셸도 같은 문장이다.
- **m11.** §3-7(P:65)에 1구: `W:261` 설계 반송 재진입과 ⑤ 새 실패로 가는 architect 반송(`D5:298`)에서 명세 쌍이 바뀌면 `plan --names` 재실행 · 범위 밖 편집 대조 · (나) 새 키 재승인을 다시 한다.
- **m12. 행동 시험**(§11 P:179-193)
  - (a) W6-T10 비용이 상한 계산에 없다. «새 점검» 두 갈래는 R2 전 판정 지점에서 멈추게 적는다.
  - (b) W6-T13 은 가지 약 9 × 6분이다. 설계 §11 의 «가지가 많으면 대상 모듈만 좁혀»를 옮긴다.
  - (c) W6-T13 «G2 배너 HEAD 기준 표기»는 책상 재생으로 볼 수 없다. 확인 방법을 적는다.
  - (d) 리팩토링 모드가 실하네스로 Phase 2·G2 를 지나는 시험이 0 이다. M2·M7·m10 이 모두 거기서 드러난다. W6-T0(`web/static/images` · C 3 · R2 조각 작음)을 G2 까지 1회 이어 가는 행을 권한다(⑤ 2회 약 38분 포함 · 기존 테스트 실행은 보강이 아니다).
- **m13. 문서 몫**
  - (a) 결정 17 번복과 비용을 사용자에게 알리는 보고(설계 §13)가 계획 단계에 없다. 승인 브리프에 1줄을 둔다.
  - (b) 설계 §9·§10 5행이 요구한 «리팩터링 대상 = 백스톱 위반» 사본의 전수 grep(houserules SKILL `:15` · final `:217` 무변 확인)이 §7 에 없다.
  - (c) AGENTS `:25` «검사 24종»은 러너 `TOTAL_CHECKS = 26`(`BS:38`)과 다르다. 같은 줄을 고치므로 함께 정정한다.
  - (d) 부록 A 는 §1 끝의 두 곳을 고친다.
- **m14.** Codex 의미 미러 표기 목록(P:35)에 `spawn_agent` 와 역할 스킬 이름(`dddjango-web-design-review-web` 등 — dddjango Codex `:249` 판형)을 더한다. R2 다발 · R3 · 잔존 확인의 파견 문면이 이 표기를 쓴다.
- **m15.** 끝 절 R2 문단(§3-9 P:67)에 R2 시각 형식 `date +%Y%m%d-%H%M%S` 를 명시한다(파서는 `\d{8}-\d{6}` 만 받는다 · `D5:269`). `## G0` 머리 시각(`date '+%Y-%m-%d %H:%M'`, `W:155`)과 형식이 달라 섞이기 쉽다.
- **m16.**(참고) `refactor_audit.py` 800행(P:110)은 낙관적이다.
  - dddjango 판 1,521행에서 빠지는 것은 rulepack · outline · sections(약 250행)뿐이다.
  - web 판은 문서 색인(절·문장·문단)을 새로 쓰고, 소유 판정 · 교차 단위 줄 · `--names` · render 호출 ast · API 리터럴 결속을 더한다.
  - 1,100~1,400행이 현실적이다. 작업량 추정(5~6일)에는 영향이 작다.

## §3 행 번호 대조 결과 요약

| 계획이 가리킨 곳 | 실물 | 판정 |
|---|---|---|
| Coordinator `:5` disable · `:15` `빌드할 화면: $feature` · `:17-19` 인자 | 같음 | ✓ |
| `:61` 스키마 | `:61` = phase · **`:62` = mode** | ✗ → m1 |
| `:86` 갱신 시점 · `:120` 삼분류 · `:128` 정리 요청 · `:148` 단위 · `:150` 묶음 · `:151` ⓐ′ · `:153` 충돌 | 같음 | ✓ |
| `:193` 스캔 단위 확인 · `:200` 진입 준비 · `:211` 슬라이스 0 호출 · `:212` 반송 (가) | 같음 | ✓ |
| `:216` 감사 리듬 · `:217` 백스톱 + 잔존 · `:218` G2 배너(빚 3행) · `:222` Phase 3 · `:237` 수정 전 근거 · `:264` 경계 · `:9`·`:266` 직접 쓰는 것 | 같음 | ✓ |
| Codex `:114`~ | mode `:115` | ≈ |
| Codex `:142` · `:150` · `:172` · `:173` · `:216` · `:288` | 같음 | ✓ |
| Codex 대응(계획에 번호 없음) | 진입 준비 `:223` · 슬라이스 0 `:234` · 반송 `:235` · 감사 `:239` · 백스톱 `:240` · G2 배너 `:241` · Phase 3 `:245` · 결정 출처 `:174` · 첫 문단 `:8` · 경계 목록 `:290` | 참고 |
| 에이전트 DRW `:27`·`:59` · DR `:49`·`:51` · architect `:55`·`:86` · coder `:38`·`:57`·`:75` | 같음 | ✓ |
| `backstop.py:6-16` 머리 · `:40-43` `_USAGE` · `:141-176` 인자 루프 · `:188-196` 배타 | 머리 `:5-19` · 루프 `:141-179` · 배타 `:189-196` | ✓(범위 근사) |
| `check_structure.py:163-167` WS5 게이트 | 같음 | ✓ |
| `debt.py:138-140` WS5 notice | **`:129-132`** | ✗ → m1 |
| houserules `final.md:197-207` | 명령 판형 `:197-199` · 빚 모드 `:207` | ✓ |
| REQUEST_GUIDE `:205-207` · README `:108-109`·`:318` · AGENTS `:24-25` | 같음 | ✓(AGENTS «24종» 드리프트 → m13) |
| `dddjango/commands/dddjango.md:222-247` 끝 절 | 머리 `:222` · 문단 12(`:225-247`) | ✓(계획 «문단 13»은 근사) |
