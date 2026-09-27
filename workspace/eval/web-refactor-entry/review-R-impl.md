판정: 수정 후 승인 — blocker 1 · major 4 · minor 12 — 입구·러너·도구·문면·미러는 설계 v5·계획 v2대로 섰고 verify-web·validate도 green이다. 다만 재사용 폴더의 새 점검에서 G2 `residual`이 앞 실행의 해소 기록을 M 번호로 이어받아 미해소 항목을 «해소 유지»로 닫는다(fail-open). 이것과 `--final` 확정 표 미기록, `--except` 폴더·글롭 누수, 리뷰어 짧은 행의 무언 삭제, 참조 치환 줄 위 의미 항목의 편집 종류 공백을 고친 뒤 승인한다

# 로드맵 6b 구현 독립 리뷰 R (2026-09-27)

- **대상**: HEAD `c9fcadff` 위 미커밋 변경 중 6b 몫이다.
  - `dddjango-web/**`: 입구 `commands/refactor.md` · Coordinator · 에이전트 4 · `scripts/{backstop.py, refactor_audit.py, src/debt.py, src/subst.py, src/check_structure.py}` · 픽스처 3 · houserules `final.md` · REQUEST_GUIDE · plugin.json.
  - `codex-dddjango-web/**`: 같은 파일의 미러와 새 `skills/dddjango-web-refactor/`.
  - `Makefile` · `AGENTS.md` · `README.md`.
  - 사용자 파일(`docs/master.html` · `workspace/eval/field-report-4/…` · `workspace/plan/2026-09-26-refactor-campaign/` · `…/request-guide-audit/synthesis-v2.md`)은 읽지도 쓰지도 않았다.
- **근거**: `design-v5.md` · `plan-v2.md` · `impl-log.md`(§2 편차 1~8) · `phrase-classification.md`(§7 F1~F9) · `behavior-tests.md` · `review-X4-design-v4.md` · `review-P6b-plan-v1.md` · 6a 판형 `web-g0-debt/review-Q-impl.md` · `AGENTS.md` · `docs/DEVELOPMENT.md`.
- **행동 시험 원 기록**: scratch `6b-impl/`(`bt/*.jsonl` · `t13/` · `t14/` · `t9/` · `t5/`)를 읽기만 했다. W6-T0b는 진행 중이라(`bt/W6-T0b3.jsonl` 갱신 중) 판정하지 않았다.
- **실험 위치**: scratch `review-R/`
  - `exp/e1`~`e6`: 합성 프로젝트. 픽스처 `fixtures_refactor_audit.sh` 준비부를 `exp/setup.sh`로 떠서 썼다.
  - `sds/`: 현장 `git clone --shared` · HEAD `49b9b2182`. 테스트는 돌리지 않아 `uv sync`도 하지 않았다. 현장 원본에는 쓰지 않았다.
- Serena·Graphify는 쓰지 않았고(지시), 서브에이전트도 부르지 않았다. 현장 테스트 전체·`make testp`·`make verify`는 돌리지 않았다(지시).

## §0 검증 실행 결과

| 검증 | 결과 |
|---|---|
| `make verify-web` | [실측] exit 0 · 112초. 픽스처 16파일 실패 0이다(`fixtures_debt` 80 · `fixtures_subst` 29 · `fixtures_refactor_audit` 55 포함). self-test는 claude·codex 모두 «점검 절 62 · 어구 32 · 극성 표본 16 · red 0»이다. `scripts`·`assets` `diff -rq` 0 · references `cmp` 5종 · REQUEST_GUIDE `cmp` · 요청 가이드 계약 PASS |
| `claude plugin validate dddjango-web --strict` | [실측] ✔ Validation passed(셸 초기화 경고 1줄 `_dotsync_agent_should_manage_launch` — 환경 잡음) |
| byte 미러(verify-web 밖) | [실측] 렌즈 문서 `discipline-cleancode/references/final.md` · `implementation-javascript/references/final.md` · `undecidable-web.md` 모두 Claude=Codex. `SKILL.md` 4종은 기존 frontmatter 차이 |
| Coordinator 의미 미러 | [실측] 6b 추가 조각은 Claude 46 · Codex 45개다. `${CLAUDE_PLUGIN_ROOT}`·입구 표기·질문 도구를 정규화한 뒤 차이는 다음뿐이다: `요청 원문:` 1행(설계 §1-2 기록 차이) · 판별 입력 «요청 첫 줄» · 본인 직접 괄호 문구 · `spawn_agent`+역할 스킬 · «네이티브 셸로» · «트래커 라인» · «`dddjango-web` 스킬» |
| 역할 SKILL 4 의미 미러 | [실측] coder-web 추가 문장은 에이전트와 글자 그대로 같다. 나머지 셋은 Codex 표기 차이(spawn · 네이티브 검색 도구 · 경로 사상 1구)뿐이다 |
| 적용 한정 어구 | [실측] Claude `scope_phrases()` = Codex = `phrase-classification.md` §2-1 = 32개. 두 Coordinator의 적용 범위 규범 문단은 글자 그대로 같다 |
| 문면 치환자 규칙(계획 §1) | [실측] 새 줄의 `$ARGUMENTS`는 `commands/dddjango-web.md:15` 1곳뿐이고 `$[0-9]`·`$feature`·`$api_url`은 새 줄에 0이다 |
| 현장 사본 리팩토링 스캔 | [실측] `--debt-scan --refactor`와 기본 스캔이 모두 키 3(WN8 이미지)이다 · 2.4초 · WS5 추가 0 |
| 현장 사본 `plan` | [실측] `web/static/images` 참조 치환 줄 5(`login.html:18·23·25` · `special_button.html:12·14`) · `web/consultation` 경계 교차 소비자 `home.html:13` · `conversation.css` 영역 전속 · `wonbo.png` 비영역 참조 — W6-T0·T5 기록을 현 HEAD에서 재현했다. `plan --against`(consultation)는 76.6초 · «같음» exit 0이다(기계가 T0b와 병행 부하 중) |
| 실험 e1~e6 | §2 각 항목에 인용한다 |
| `make verify` | 돌리지 않았다(지시 — core 봉인 드리프트 red는 봉인 write 전 예상 red) |

## §1 설계·계획 커버리지

| 계획 항목 | 구현 위치 | 판정 |
|---|---|---|
| §0 기준선 | `impl-log.md` §0 | ✓ |
| §1 입구(disable 제거 · `요청 원문:` · `refactor.md` · Codex 스킬·yaml) | `commands/dddjango-web.md:1-15`(frontmatter `disable-model-invocation` 없음 · `:15`) · `commands/refactor.md:1-10` · `codex-…/dddjango-web-refactor/SKILL.md` · `agents/openai.yaml`(`allow_implicit_invocation: false`) | ✓ description 문구는 설계 §1-1과 글자 그대로 같다 |
| 2-1 스키마 `mode` · `test_baseline` · 갱신 시점 · 디자인 플래그 | `:62` · `:74` · `:87` (Codex `:115`·`:127`) | ✓ |
| 2-2 사분류 · 판별 입력 둘 · 표지 손상 · 단조성 | `:121` · `:123` · `:130` (Codex `:143`·`:145`) | ✓ |
| 2-3 `<대상>` 표기 · R2·R3 축소 지시 불복 | `:132` | ✓ |
| 2-4 묶음 grep pathspec · web/ 아래 한정 · 비테스트 적중 제외 | `:154` (Codex `:176`) | ✓ pathspec은 Coordinator 안에서 2회 같은 문자열로 나오고 self-test가 대조한다 |
| 2-5 ⓐ′ 대가 «(의미 점검 포함)» | `:155` | ✓ |
| 2-6 `:193` 테스트 치환 파일 단위 판정 제외 | `:197` | ✓ |
| 2-7 ④′ 기준선 · ⑤ add 목록 | `:204` (Codex `:227`) | ✓ |
| 2-8 끝 green ①~⑤ · ⑤ 실행 규칙 · 재확인 | `:215` · `:216` · `:217` (Codex `:238-240`) | ✓ 백그라운드 실행 · `stopping after` · 통과 0 · 시간 제한 끊김 · 재기준선 모두 있다 |
| 2-9 `배선 적용:` → `--except` | `:218` | ✓ `--except` 값 검증은 → **M2** |
| 2-10 감사 반영·백스톱 반송 재확인 · G2 직전 ④ | `:222` · `:223` | ✓ |
| 2-11 G2 배너 두 행 | `:224` | ✓ |
| 2-12 Phase 3 재개봉 재확인 | `:228` | ✓ |
| 2-13 기록물 목록 | `:8` · `:272` | ✓ |
| 2-14 결정 출처 «`요청 원문:` 줄만으로는 본인 직접 아님» | `:156` (Codex 대응) | ✓ |
| §3 끝 절 1 머리 문단(흐름 · 바꾸는 곳 · 슬라이스 도출 임계 미사용) | `:280-282` | ✓ |
| §3-2~4 R0 · R0′(초기화 8필드 · 디자인 플래그 6) · G0 정지 재개(`--against`) | `:284` · `:286` · `:288` | ✓ R0′ 폴더 재사용과 `residual/` 이월이 충돌한다 → **B1** |
| §3-5 범위(네 판정 이름 · 이중 범위 · 키 소속 1~4) | 끝 절에 없다(도구 `refactor_audit.py:581-663`와 `plan.md`에만 있다) | △ 기록되지 않은 편차 → m8 |
| §3-6 줄 편집 (가)(나)(다) | `:298` | ✓ 참조 치환 줄 위 의미 항목의 편집 종류가 없다 → **M4** |
| §3-7 G1 스캔 단위 확인 리팩토링 판 | `:300` | ✓ |
| §3-8~11 R1 · R2 · R2′·R3 · 별도 요청 넷 | `:290` · `:292` · `:294` | ✓ |
| §3-12 적용 범위 규범(⑴⑵ · 끝 문장 · 32어구 · `:191` 관계 · F1 1문장) | `:296` | ✓ |
| §3-13~17 G0 · 배선 · Phase 1~2 · G2 | `:302` · `:304` · `:306` · `:308` | ✓ |
| §4 `check_structure.run_skeleton` | `src/check_structure.py:175-177` | ✓ |
| §4 `debt.py` `--refactor` · WP1 조건부 · `mode` · M 행 · `residual_m_sets` | `src/debt.py:36-40·50-54·108-135·143-192·296-337·376-391` | ✓ D24~D28 |
| §4 `parse_spec_pairs` · `tail_of`·`module_of` · `reference_lines` · `is_test_path` | `src/debt.py:416-506` | ✓ 경로 인용 문제는 → m4 |
| §4 `--subst-check`(편차 1: `src/subst.py`) | `src/subst.py:129-319` | ✓ S1~S13. `--except` 누수는 → **M2** |
| §4 `backstop.py` 인자·배타·헤더·`_USAGE` | `backstop.py:9-22·47-51·177-236` | ✓ D27a~g |
| §5 도구 공통(구조 판별 · `요약:`) | `refactor_audit.py:347-360` | ✓ J1·J2 |
| §5 `plan` · `--against` · `--names` · `--out` 거부 | `:581-863` (`:801-802` · `:789-796`) | ✓ A·B·C·D |
| §5 `check` | `:983-1025` | ✓ 짧은 행 탈락은 → **M3** |
| §5 `check-verdict`(다섯 출구 · 기계 근거 · 대리 축소 · `--final`) | `:1108-1466` | ✓ `--final`은 → **M1**, 근거 문서 범위는 → m2, 오탐 겹침은 → m3 |
| §5 `residual`(필수 조건 · 결정적 바닥 · 묶음 · `--finalize`) | `:1519-1642` | ✓ 이월은 → **B1**, pending exit은 → m1 |
| §5 `--self-test` | `:1647-1685` | ✓ 어구는 편차 5(Coordinator에서 읽음) → m7 |
| §6 에이전트 4 · 역할 SKILL 4 | `design-review-web.md:17·21·29-41·75` · `discipline-reviewer-web.md:32·34-46·63·82` · `design-architect-web.md:32·56·63-80·103` · `coder-web.md:34·39·58·76` | ✓ «모두» 1행 위치는 → m8 |
| §7 전수 분류 | `phrase-classification.md` | ✓ F4 처분의 사실 오류는 → m6 |
| §8 REQUEST_GUIDE §6·§7 · README · AGENTS · plugin.json 2 · houserules §7 · 6a 정정 메모 | `REQUEST_GUIDE.md:205-226·244-247` · `README.md:110·319` · `AGENTS.md:24-27` · `plugin.json` 2 · `final.md:199-200·208` · `web-g0-debt/behavior-tests.md` 정정 메모 | ✓ |
| §9 Makefile | `Makefile:98-100` (`set -euo pipefail` 블록 안 · `--platform` 없음) | ✓ |
| §10 픽스처 | `fixtures_debt.sh:439-545`(D24~D29) · `fixtures_subst.sh`(S1~S13) · `fixtures_refactor_audit.sh`(A~J) | ✓ 공백은 → m12 |
| §11 행동 시험 | `behavior-tests.md` — T1·T2·T0·T5·T13·T14·T9 완료 | △ T0b 진행 중 · T3·T10·T11·T12·C 남음(§3) |

**impl-log §2 편차 판정**

| # | 판정 |
|---|---|
| 1 `src/subst.py` 분리 | 타당. 바뀌는 이유가 다르고, 공통 함수는 `debt.py` 한 곳에 있다 |
| 2 경로 맞바꿈 red | 타당. fail-closed이고 S5b가 고정한다. 설계 «교환 쌍 green»은 `이름:` 교환(S5a)으로 성립한다 |
| 3 `--untracked -I` | 타당(범위를 넓히는 쪽). 다만 `-z`·`core.quotePath` 없이 경로를 읽는다 → m4 |
| 4 리팩토링 스캔 WS5 «신규 …» 문구 | 수용. 키·판정에 영향이 없다. G0 표에 기존 영역이 «신규 영역»으로 보이는 혼동 여지만 남는다 |
| 5 어구 목록을 실행 때 Coordinator에서 읽음 | 타당(산문 정본 한 곳 · 비면 exit 1). 드리프트 자리가 «Claude 문면 ↔ Codex 문면»으로 옮겨 갔다 → m7 |
| 6 `\|` 이스케이프 | 타당. 에이전트 문면(`design-review-web.md:37` 류)과 파서(`refactor_audit.py:868-877`)가 맞는다 |
| 7 REQUEST_GUIDE §7 대리 표지 | 타당. `dddjango/REQUEST_GUIDE.md:202-205`에 같은 문장이 실재함을 확인했다 |
| 8 F1~F9 처분 | 대체로 반영됐다. F1은 `:296` 끝 문장, F2는 `design-review-web.md:17·75`, F3은 `refactor_audit.py:103-115·125`, F5는 `:118-122`, F7은 `:282·302`에 있다. **F4 «같은 효과»는 사실이 아니다** → m6. F6·F8·F9는 §3에서 판정한다 |

## §2 지적

### blocker

**B1. 재사용 폴더의 새 점검에서 `residual`이 앞 실행의 해소를 M 번호로 이어받아 미해소 항목을 닫는다 — fail-open** [실측]

- **위치**: `dddjango-web/scripts/refactor_audit.py:1509-1516`(`_carried`) · `:1557-1560`(이월 판정이 결정적 바닥보다 먼저 돈다) · Codex byte 사본.
- **발동 경로**:
  - Coordinator `:286` R0′는 «끝난 실행 뒤의 새 점검은 그 폴더를 다시 쓰고»라고 정한다. 이때 `debt-g0.json`·build-state만 새로 하고 `residual/`은 남는다.
  - 새 audit의 `M<n>`은 다시 M1부터 매겨진다.
  - `_carried`는 `residual/` 아래에서 가장 최근 `result.json`의 `solved`를 **M 번호 키로** 읽는다.
  - 앞 실행 M1의 감시 파일 지문이 그대로면(앞 실행이 고친 파일을 이번 슬라이스 0이 건드리지 않으면 — 보통의 경우) 새 M1은 «해소 유지»가 된다. 이 판정은 결정적 잔존(파일 무변)보다도, 리뷰어 확인보다도 먼저 나온다.
- **실측** e1(`exp/e1_carried.sh`):
  - 실행 1: M1 = `home_view.py:1`. 고치고 `--finalize`로 해소했다.
  - 실행 2(같은 폴더 새 점검): M1 = `home_view2.py:1` — 무변(미해소) 항목이다.
  - 결과: `요약: residual M_m=0(결정적 잔존 0) · 해소 유지 1 · 리뷰어 확인 대상 0` · **exit 0**.
  - 대조(앞 `residual/`을 치움): `M_m=1(결정적 잔존 1)` · exit 2.
- **결과**: G2 배너의 `M_m`이 0이 되어 G0 ⓐ 의미 항목이 정리되지 않은 채 끝남으로 간다.
- **고침**:
  - `result.json`에 `audit`(`의미 audit` 시각)과 `git_snapshot`을 적는다.
  - `_carried`는 현재 `residual_m_sets`의 audit·build-state `git_snapshot`과 같은 판만 잇는다. 도구 한 곳에서 고치는 쪽을 권한다. R0′ 문면에 `residual/` 치우기를 더하는 방법도 있지만 모델 규율에 기댄다.
  - 회귀 픽스처 1건(재사용 폴더 새 점검 → 이월 금지 · 결정적 잔존 exit 2)을 둔다.
  - dddjango `refactor_audit.py:1276-1284·1316-1318`도 같은 모양이다[추정 — 범위 밖 · dddjango R0′도 같은 폴더의 새 실행이다]. 후속 과제로 적는다.

### major

**M1. `check-verdict --final`의 확정 표가 `verdict.md`에 남지 않아 G2 `residual`과 «잇기»가 다른 목록을 본다** [실측]

- **위치**: `refactor_audit.py:1347-1390`(`_finalize_verdicts` — 메모리 목록만 바꾼다) · `:1436-1438` · `:1449-1458`(확정 표는 `verdict-log.md`에만 쓴다) · `:1531`·`:1549-1550`(`residual`은 `verdict.md`를 읽는다).
- **시나리오**: architect가 통과 행 하나의 판정을 두 번 빠뜨린다. 그러면 `--final`이 새 번호 `M2`를 채택으로 매기고, G0이 M2를 ⓐ로 승인한다. 이어 G2에서 `residual`이 멈춘다.
  - 실측 e2: `실행 불능: ToolError: ⓐ 항목 M2 이 verdict.md 에 없다` · exit 1.
  - G2는 판정 불가로 끝낼 수 없다.
- **딸린 결과**:
  - (가) M 번호가 중복되면 `{v.mid: v}`가 뒤 행으로 덮는다. `--final`이 새 번호로 옮긴 행이 G0의 원래 번호로 확인된다[추정].
  - (나) Coordinator `:286` «잇기 — 그 audit 의 `verdict.md` 를 그대로 쓴다»도 G0에 보인 목록과 다른 목록을 쓴다. `--final`이 채택으로 돌린 제외·병합 행이 `verdict.md`에는 여전히 제외·병합으로 남는다.
- **고침**:
  - exit 0 판마다(`--final` 포함) 확정 표를 audit 폴더의 한 파일에 쓴다 — `verdict.md` 덮기, 또는 `verdict-final.md`.
  - `residual`·잇기·G0 목록이 그 파일을 읽는다.
  - 회귀 픽스처 1건(`--final` 새 번호 → residual 풀림)을 둔다.

**M2. `--subst-check --except`에 폴더·글롭을 주면 테스트 단언 변경과 비테스트 편집이 대조에서 빠진다(조건부 fail-open)** [실측]

- **위치**: `dddjango-web/scripts/src/subst.py:266-275` · Codex byte 사본.
  - 값 검사는 «`web`·`web/…`·`/…`·`.dddjango-web…`·테스트 파일 이름»만 거른다.
  - 값은 기본(글롭) 매직의 `:(exclude)<값>` pathspec이 되어 본 대조와 미커밋 가드 모두에서 빠진다.
- **실측** e3. 슬라이스 0에서 settings 배선 + `config/tests/test_cfg.py` 단언 변경 + `config/other.py` 신설을 했다.
  - `--except config/settings.py`(정상 사용): 어긋남 3 · exit 2.
  - `--except config`: 테스트 단언 변경과 `config/other.py`가 사라진다(다른 폴더 테스트 1건만 red).
  - `--except '*'` · `--except '*.py'`: `web/ 밖 변경 파일 0` · **exit 0**.
- **평가**: 설계 §7-2 «테스트 파일이면 exit 1»의 뜻은 «테스트는 결코 빼지 않는다»인데, 폴더·글롭으로 새어 나간다.
  - 발동은 Coordinator가 `배선 적용:` 행(`:218`)에 파일이 아닌 값을 적을 때뿐이다(6a 기능 요청의 Phase 2 배선 반송 경로). 그래서 조건부로 둔다.
- **고침**:
  - 값마다 기준·대상 트리에 실재하는 **파일**인지 확인한다(`git cat-file -e <대상>:<경로>` 류). 아니면 exit 1.
  - pathspec은 `:(exclude,literal)<경로>`로 쓴다.
  - 픽스처 S10e(폴더) · S10f(글롭) → exit 1을 둔다.

**M3. 리뷰어 표의 짧은 행을 조용히 버린다 — 설계 «무언 삭제 금지» 위반** [실측]

- **위치**: `refactor_audit.py:956-958`(`_load_rows` — 칸이 6개 미만이고 첫 칸이 숫자가 아니면 `continue`).
- **시나리오**: 리뷰어가 판형을 줄여 `| R4 | 규칙 | web/…:2 | 요지 |`처럼 낸다.
  - 이 행은 «인용 불일치»에도 «불편»에도 오르지 않고 사라진다.
  - 모든 행이 그러면 `check 행 0`이다. 이어 «의미 채택 0 → (C 없으면) G0 정지 “정리 대상 없음”»까지 간다.
  - 실측 e6: 5행 중 비숫자 첫 칸의 4칸·3칸 행 2개가 탈락했고 `check 행 3 · 통과 3`이 나왔다.
- **근거**: 설계 §4-3 R2′ «남는 행은 «인용 불일치» 목록(무언 삭제 금지)». 리뷰어는 모델이라 판형 이탈이 실하네스에서 나올 수 있는 결함이다.
- **고침**:
  - `web/…:\d+` 모양 위치 토큰이 있는 표 행은 칸 수와 무관하게 행으로 받는다. 8칸이 아니면 «인용 불일치(칸 부족)»로 올린다(숫자 첫 칸 행에 이미 하는 처리와 같다).
  - 보조 표(위치 토큰 없음)만 건너뛴다.
  - 픽스처 F3을 둔다.

**M4. 참조 치환 줄·(나) 줄 위의 의미 항목을 범위 안으로 받으면서, 그 줄의 편집 종류는 «참조 치환뿐»이라 문면이 서로 막는다** [실측(T0 기록) · 추정(DR 판정)]

- **위치**:
  - `refactor_audit.py:908-910`(`Plan.in_scope` — 설계 §4-3 ②대로 줄 편집·참조 치환·(나) 줄 위 항목을 범위 안으로 받는다).
  - Coordinator `:298` «(나) … 편집은 참조 치환뿐이다» · (다)는 «WI·WP 발견의 키»만.
  - `:300` ② 대조 목록.
  - `agents/discipline-reviewer-web.md:82` 9번 «(나) 줄은 옛 참조 → 새 참조 치환뿐인가».
  - Codex 대응.
- **시나리오**(T0 실하네스에서 이미 나왔다):
  - M4 = `web/design_system/component/button/special_button.html:12` 주석 단서 삭제다. 이 줄은 참조 치환 줄이자 `gold-blossom.png` 경로 쌍의 (나) 줄이다.
  - Coordinator는 G1 ②에서 문면에 없는 범주 «참조 치환 줄 위의 G0 승인 ⓐ M4 내용 교정»을 지어 통과시켰다(`sds-W6-T0/…/refactor-scope.md` «G1 스캔 단위 확인 21:28»).
  - Phase 2 5번 감사가 DR 9번 문면대로 보면 같은 편집이 «(나) 치환뿐» 위반이다. 설계상 채택된 항목이 반송·재상정으로 갈 수 있다.
- **고침**(설계 §4-3 ②가 그 줄 위 항목을 이미 범위 안으로 둔 데서 답이 나온다 — 사용자 질문 불요):
  - 끝 절 «범위와 줄 편집»에 한 줄을 더한다: «(라) (가)·(나)·(다)·참조 치환 줄 위의 G0 승인 `M<n>` ⓐ 항목 — 그 항목의 교정만(줄 단위)».
  - `:300` ② 목록과 DR 9번에 같은 구를 더하고 Codex에 미러한다.

### minor

- **m1. `residual` 첫 호출이 결정적 잔존이 있어도 exit 0** [실측]
  - 위치: `refactor_audit.py:1588-1591`.
  - 리뷰어 확인 대상이 있으면 `결정적 잔존 1 · … · M_m 미정` 요약과 함께 exit 0이다(e6 추가 실행).
  - `--finalize`가 floor를 더하므로 문면대로면 새지 않는다. 하지만 exit만 보는 호출자에게는 «M_m 0»으로 읽힌다(dddjango 판도 같다).
  - 고침: floor>0이면 exit 2로 둔다. 또는 G2 문단(`:308`)에 «`M_m 미정` 요약의 exit 0 은 판정이 아니다 — `--finalize` 결과만 쓴다» 1구.
- **m2. 제외·사용자 판단의 근거 문서가 규범 문서로 한정되지 않음** [실측]
  - 위치: `refactor_audit.py:967-980`(플러그인 루트 아래 아무 파일) · `:1108-1134`.
  - e6에서 Coordinator R2 문단의 절차 문장 «다발을 반복하는 것은 위반이 아니다»(`commands/dddjango-web.md §리팩토링 모드`)를 근거로 한 제외가 red 0으로 통과했다.
  - REQUEST_GUIDE와 `scripts/*.py` 주석도 `#` 제목으로 색인된다.
  - 고침: 제외·반대 방향 인용의 문서 키를 `LENS_SECTIONS` 문서 집합(∪ `CAN_DOCS`)으로 한정한다. dddjango가 rulepack 규범만 받는 것의 대응이다.
- **m3. 오탐 근거가 위반 인용과 같은 문구여도 통과** [실측]
  - 위치: `refactor_audit.py:1137-1154`.
  - 위반 인용 «기준은 dddart 검증 판형의 현지화다»를 그대로 오탐 근거로 적은 판정이 red 0이었다.
  - 고침(F8의 최소 보강): 오탐 인용 구간이 위반 인용 구간과 겹치면 red로 둔다. 같은 문장의 다른 요건절은 계속 받는다.
- **m4. git 출력 경로 인용(비 ASCII)으로 web/ 경로가 «web/ 밖»으로 분류됨** [실측(합성) · 현장 web/ 비 ASCII 경로 0]
  - 위치: `src/debt.py:483-497`(`reference_lines` — `-z`·`core.quotePath=false` 없음) · `refactor_audit.py:1471-1482`(`_changed_since`·`_renamed_since`).
  - e5: `web/home/home/section/카드.html`이 `"web/home/…/\354\271\264\353\223\234.html":1`로 나와 «web/ 밖 참조 줄»에 올랐다. 그 파일만 참조하는 `orphan.png`는 home 판정표에서 빠졌다(영역 전속 누락). residual에서는 바뀐 파일이 «무변»으로 읽힌다(fail-closed 방향).
  - 고침: git 호출에 `-c core.quotePath=false`를 붙이거나 `-z`로 읽는다.
- **m5. `RENAME_CHECKS`가 WN6 전체를 담음**
  - 위치: `refactor_audit.py:132-134`.
  - 주석과 Coordinator `:154`는 «WN6 «대응 미완»은 생성이라 제외»인데 코드는 WN6 키 전부를 개명 대상으로 본다.
  - 그래서 «대응 미완» VM 파일의 참조 줄이 참조 치환 줄·편집 줄 키로 과잉 편입된다(과잉 질문·과잉 허용 방향).
  - 고침: findings의 `message`가 `대응 미완`인 WN6 행은 대상에서 뺀다.
- **m6. 극성 술어 — F4 처분 «같은 효과»는 사실이 아니다** [실측(합성) · 현 렌즈 코퍼스 적중 0]
  - 공백을 전부 지운 본문에 술어를 걸어 낱말 경계를 넘는 적중이 난다. 예: «예외 다른 경로는 금지다»→`예외다`, «허용 이다음»→`허용이다`가 유효 긍정으로 잡힌다.
  - 부정형 목록(`:126`)에 `무방하지않`이 없어 «무방하지 않다»가 유효로 잡힌다.
  - 고침:
    - 술어는 공백 한 칸 접은 문장에 공백 허용 정규식(`예외\s?(?:다|이다)(?![가-힣])` 류)으로 건다.
    - `NEGATIONS`에 `무방하지않`을 더한다.
    - 극성 표본 2개를 추가한다.
- **m7. self-test가 Claude·Codex 적용 한정 어구 동일성을 보지 않음**
  - 편차 5로 드리프트 자리가 «상수 ↔ 문면»에서 «Claude 문면 ↔ Codex 문면»으로 옮겨 갔다. self-test는 플랫폼마다 존재와 맨 낱말만 본다(`:1662-1669`).
  - 지금은 32=32이고 문단도 같다[실측].
  - 고침: verify-web에 두 플랫폼 `norm_paragraph()` 본문 대조 1행을 둔다.
- **m8. 문면 커버리지 편차 3건 — impl-log §2에 기록되지 않음**
  - (가) 계획 §3-5가 싣기로 한 «네 판정 이름 · 이중 범위 · 키 소속 1~4(폴더·빈 경로 키)»가 끝 절에 없다(`plan.md`에만 있다).
  - (나) 계획 §6 «모두» 1행이 `coder-web.md:34`·`design-architect-web.md:32`에서는 «(리팩토링 모드면)» 조건 불릿 안에 있다(효과는 같다).
  - (다) Codex Coordinator R0·표지 없는 잇기 문장의 «`dddjango-web` 스킬 으로»(조사).
  - 고침: 편차로 기록하거나 끝 절에 1구를 더한다.
- **m9. ④의 사각 — web/ 아래 테스트 파일** [현장 0]
  - 위치: `src/subst.py:274`(pathspec이 web 전체를 뺀다).
  - 브라운필드 프로젝트가 web/ 아래에 테스트를 두면, 슬라이스 0이 그 단언을 고쳐 ⑤를 맞춰도 ④·⑤가 모두 green이다.
  - 고침: web/ 아래 `is_test_path` 파일도 대조에 넣는다. 또는 DR 9번에 «web/ 아래 테스트의 판정·단언 변경 금지» 1구를 둔다.
- **m10. 컨테이너 단위 표기가 셸 글롭으로 펼쳐짐** [실측]
  - `refactor_audit.py plan web/*.py …`를 따옴표 없이 넘기면 셸이 `web/__init__.py web/urls.py`로 펼친다. 결과는 `unrecognized arguments` · 실행 불능이다(e6 · zsh·bash 모두).
  - 고침: Coordinator R0·R2(`:284`·`:292`)에 «컨테이너 단위는 따옴표로 감싼다» 1구(Codex 같게)를 둔다.
- **m11. `plan --names`가 부모 패키지 import·상대 import 소비자를 놓침** [추정 — 코드 읽기]
  - 위치: `refactor_audit.py:835-844`. 옛 모듈 점 경로 문자열로만 importer를 고른다.
  - `from web.a.b import mod as m` → `m.name` 모양이나 `from .mod import name` 모양은 (나)에서 빠진다. 그러면 G1 ②에서 architect 반송이나 «경계 교차»로 떨어진다(fail-closed · 현장 모양은 T5에서 문제없음).
  - 고침: 부모 점 경로 + `import <끝 성분>` 적중 파일도 importers에 넣는다. 또는 한계로 기록한다.
- **m12. 픽스처 공백**
  - 소유자 전이(static → static 사슬).
  - `check-verdict` ④ 구간 겹침 red.
  - residual의 재승인 되살림과 `의미 ⓐ 키:` 값 형식 어긋남 exit 1.
  - 위 B1·M1·M2·M3의 회귀 사례. 계획이 적은 «이진 같은 byte green»은 diff에 오르지 않아 자명하다.

## §3 행동 시험 관찰 판정

| 행 | 판정 | 원 기록 대조 |
|---|---|---|
| W6-T1 | 합격 타당 | 최종 문면이 «`요청 원문:` 줄 … ` · ` 빠짐» 정지다. 폴더 전후 목록이 같고 모델 호출은 Bash 1회(입구 파일 grep) · $0.94 |
| W6-T2a~d | 합격 타당 | 네 기록 모두 Skill args가 표지 원문 그대로다. 정지 사유는 대상 없음·2개·단위 안쪽·기능 혼입이고 폴더 전후 목록이 같다 |
| W6-T0 | 합격 타당(단서 3) | ① G0 질문은 평문이다 — 비대화 `-p`라 질문 도구 폴백 문면(`:155`)대로다. ② R2 파견을 `run_in_background: true`로 내고 턴이 끝났다가 알림 3회로 이어졌다. 성립했지만 리뷰어 표 파일 쓰기가 알림 순서에 기댄다. ③ M4가 참조 치환 줄 위 내용 교정이고, G1 ②에서 문면 밖 범주로 통과했다(21:28 기록 — T0b 진행분) → **M4**. R1 `python` exit 127 → `.venv/bin/python`은 6a 관찰의 반복이다(6b 무관) |
| W6-T5 | 합격 타당 | 현장 HEAD `49b9b2182` 사본에서 consultation·images 판정을 재현했다(§0). `--names` 기록(`t5/web-ec`·`web-intake/plan-names.md`)은 (나) 12줄 / 0줄로 행과 같다 |
| W6-T13 | 합격 타당(범위 한정) | `t13/*.out`과 대조했다: A·C ⑤ red(`FAILED …employee_gate…` · `ERROR <모듈>` 2 · 단독 재현) · B·D 새 0 · E ④ exit 2(`:72`) · C-s1O exit 1 + `stopping after` · U1c exit 130 · U2c `1 error`·통과 0. **fail-fast가 새 실패를 가리는 사례는 재현되지 않았다**(행에 적힌 대로) — 그 조항은 문면 규칙만 있고 실측이 없다. 판정 불가 두 모양도 출력만 확인했고 Coordinator의 분류 행동은 T0b 몫이다 |
| W6-T14 | 합격 타당 | `t14/run.log`와 일치한다. 옛 상수를 import하는 «기존 테스트»(`test_zz_me_link.py`)는 합성이다 — 행에 «합성 테스트»로 적는 것이 정확하다 |
| W6-T9 | 합격 타당 | Q2x에서 ③ exit 1 · ⑤ 13 통과 · ④만 exit 2(`:110`)로 원 기록과 같다. G0 충돌 질문은 T11 몫(행에 적힘) |
| 미완 | 판정 없음 | T0b(진행 중) · T3 · T10 · T11 · T12 · W6-C. 계획 §11·§12 순서상 커밋 전 필수다 |

- **T0b 진행분 관찰**(판정 아님 · 원 기록 `bt/W6-T0b3.jsonl` 읽기만):
  - (i) 수정 전 렌더 보존을 위해 Coordinator가 저장소 밖 `/tmp/claude-501/g2h/test_g2_capture.py`(live_server pytest 하네스)를 만들어 돌렸다. 수정 모드 «구현 첫 편집 전에 수정 전 구현 근거를 보존»(`:243`)의 수단이 문면에 없어 생긴 즉흥이다. «실행 장치 신설 금지» 원칙에 걸리는지는 T0b 판정에서 본다.
  - (ii) M4의 DR 9번 충돌이 드러날 자리다.
  - (iii) 현장 `.pytest_cache`는 `check-ignore`로는 «무시 아님»이지만 pytest가 넣는 내부 `.gitignore`(`*`) 때문에 status에 뜨지 않는다. ④ 미커밋 가드에는 걸리지 않을 것으로 본다[추정].
- **F6(WP1·WP2 legacy 쌍을 겨누는 의미 항목의 이중 질문)**: 수용.
  - fail-closed 경로(채택 → G0 ⓐ → Phase 1 동작 불변 불가 → 재상정)로 두 번 묻는 비용만 있다.
  - 현장 사본 리팩토링 스캔이 기본 스캔과 같은 3키라 발생이 0이다[실측]. 장치를 더하지 않는다.
- **F8(생성 금지 조항의 «신규 한정» 오탐 해석)**: 부분 수용.
  - 해석 자체는 기계 관문 밖이 맞다(목록에 싣지 않은 판단 유지).
  - 다만 오탐 출구가 위반 인용과 같은 문구를 «요건»으로 받는다[실측] → m3의 겹침 red 1개로 가장 싼 우회를 닫는다.
- **F9(dddjango 닫힌 목록의 같은 공백)**: 수용(범위 밖).
  - dddjango 후속 과제로 기록한다. B1의 `_carried` 이월도 dddjango 판에 같은 모양이라[추정] 같은 후속에 싣는다.

## §4 리뷰 전후 git status

- 리뷰 시작 때 `git status --porcelain` 사본(scratch `review-R/status-before.txt` · 45행)과 리뷰 중간 사본(`status-mid.txt`)은 같다(`diff` 0).
- 대상 변경의 `git diff --stat`은 리뷰 중 변하지 않았다(27 files · +1006 · −120). verify-web·픽스처·실험은 저장소 파일을 바꾸지 않았다.
- [실측] 이 파일을 쓴 뒤의 기본 `git status --porcelain`(`status-after.txt`)도 리뷰 전과 같다(`diff` 0).
  - `-uall -- workspace/eval/web-refactor-entry` 목록은 16행에서 17행으로 늘었고, 늘어난 행은 `?? workspace/eval/web-refactor-entry/review-R-impl.md` 하나다. 폴더가 이미 미추적이라 기본 목록에는 보이지 않는다.
  - 대상 변경 `git diff --stat`은 여전히 27 files · +1006 · −120이다.
